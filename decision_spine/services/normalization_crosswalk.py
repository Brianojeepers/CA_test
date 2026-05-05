"""Normalize role, competency, pedagogy, decision, release, evidence, and outcome links."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from decision_spine.data_access import load_json


CROSSWALK_STATE_LABELS = {
    "aligned_for_planning": "Aligned for planning",
    "evidence_pending": "Evidence pending",
    "implementation_pending": "Implementation pending",
    "suppressed_evidence": "Suppressed evidence",
    "monitor_only": "Monitor only",
    "needs_mapping": "Needs mapping",
}


def index_by_id(items: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    return {str(item[key]): item for item in items}


def evidence_by_competency(evidence_rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in evidence_rows:
        grouped[str(row["competency_id"])].append(row)
    return grouped


def outcomes_by_cohort(outcomes: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(outcome["cohort_id"]): outcome for outcome in outcomes}


def linked_records(ids: list[str], lookup: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    return [lookup[item_id] for item_id in ids if item_id in lookup]


def crosswalk_state(
    competency: dict[str, Any],
    releases: list[dict[str, Any]],
    pedagogies: list[dict[str, Any]],
    evidence_rows: list[dict[str, Any]],
) -> str:
    if competency["status"] == "monitor" or competency["market_priority"] == "monitor":
        return "monitor_only"
    if any(row.get("suppression_applied") for row in evidence_rows):
        return "suppressed_evidence"
    if releases and any(release["release_status"] != "released" for release in releases):
        return "implementation_pending"
    if evidence_rows and any(row["readiness_level"] == "pending" for row in evidence_rows):
        return "evidence_pending"
    if releases and pedagogies and evidence_rows:
        return "aligned_for_planning"
    return "needs_mapping"


def ambiguity_flags(
    competency: dict[str, Any],
    releases: list[dict[str, Any]],
    pedagogies: list[dict[str, Any]],
    evidence_rows: list[dict[str, Any]],
    outcome_rows: list[dict[str, Any]],
) -> list[str]:
    flags: list[str] = []
    if competency["status"] != "monitor" and not releases:
        flags.append("missing_release")
    if competency["status"] != "monitor" and not pedagogies:
        flags.append("missing_pedagogy")
    if competency["status"] != "monitor" and not evidence_rows:
        flags.append("missing_evidence")
    if releases and any(release["release_status"] != "released" for release in releases):
        flags.append("release_not_released")
    if evidence_rows and any(row["readiness_level"] == "pending" for row in evidence_rows):
        flags.append("evidence_pending")
    if evidence_rows and any(row.get("suppression_applied") for row in evidence_rows):
        flags.append("evidence_suppressed")
    if evidence_rows and not outcome_rows:
        flags.append("missing_outcome")
    if competency["market_priority"] == "monitor" or competency["status"] == "monitor":
        flags.append("monitor_not_standalone")
    return flags


def build_crosswalk_row(
    competency: dict[str, Any],
    *,
    signals_by_id: dict[str, dict[str, Any]],
    decisions_by_id: dict[str, dict[str, Any]],
    releases_by_id: dict[str, dict[str, Any]],
    pedagogies_by_id: dict[str, dict[str, Any]],
    evidence_lookup: dict[str, list[dict[str, Any]]],
    outcome_lookup: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    signals = linked_records(competency["linked_signal_ids"], signals_by_id)
    decisions = linked_records(competency["linked_decision_ids"], decisions_by_id)
    releases = linked_records(competency["linked_release_ids"], releases_by_id)
    pedagogies = linked_records(competency["pedagogy_ids"], pedagogies_by_id)
    evidence_rows = evidence_lookup.get(competency["competency_id"], [])
    outcome_rows = [
        outcome_lookup[row["cohort_id"]]
        for row in evidence_rows
        if row["cohort_id"] in outcome_lookup
    ]
    state = crosswalk_state(competency, releases, pedagogies, evidence_rows)
    flags = ambiguity_flags(competency, releases, pedagogies, evidence_rows, outcome_rows)
    return {
        "competency_id": competency["competency_id"],
        "role_archetype": competency["role_archetype"],
        "competency_cluster": competency["competency_cluster"],
        "capability": competency["capability"],
        "target_proficiency": competency["target_proficiency"],
        "market_priority": competency["market_priority"],
        "horizon_window": competency["horizon_window"],
        "owner": competency["owner"],
        "status": competency["status"],
        "crosswalk_state": state,
        "state_label": CROSSWALK_STATE_LABELS[state],
        "ambiguity_flags": flags,
        "signal_ids": [signal["signal_id"] for signal in signals],
        "decision_ids": [decision["decision_id"] for decision in decisions],
        "release_ids": [release["release_id"] for release in releases],
        "pedagogy_ids": [pedagogy["pedagogy_id"] for pedagogy in pedagogies],
        "evidence_ids": [row["evidence_id"] for row in evidence_rows],
        "outcome_cohort_ids": [row["cohort_id"] for row in outcome_rows],
        "release_statuses": sorted({release["release_status"] for release in releases}),
        "readiness_levels": sorted({row["readiness_level"] for row in evidence_rows}),
        "suppression_applied": any(row.get("suppression_applied") for row in evidence_rows),
        "outcome_confidence": sorted({row["data_confidence"] for row in outcome_rows}),
        "normalization_focus": normalization_focus_for(state, flags),
    }


def normalization_focus_for(state: str, flags: list[str]) -> str:
    if state == "aligned_for_planning":
        return "Keep role, capability, pedagogy, evidence, and outcome language aligned during pilot extract design."
    if "release_not_released" in flags:
        return "Confirm release status and cohort linkage before treating the capability as implemented."
    if "evidence_pending" in flags:
        return "Wait for scored learner evidence before using this capability in gap or readiness claims."
    if "evidence_suppressed" in flags:
        return "Resolve suppression or roll-up rules before making role-readiness claims."
    if "monitor_not_standalone" in flags:
        return "Keep this capability embedded in broader workflow quality language until signal pull strengthens."
    return "Clarify missing links before designing ontology or warehouse fields."


def build_role_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["role_archetype"]].append(row)
    summaries: list[dict[str, Any]] = []
    for role, role_rows in grouped.items():
        states = Counter(row["crosswalk_state"] for row in role_rows)
        summaries.append(
            {
                "role_archetype": role,
                "competency_count": len(role_rows),
                "clusters": sorted({row["competency_cluster"] for row in role_rows}),
                "states": dict(sorted(states.items())),
                "owners": sorted({row["owner"] for row in role_rows}),
            }
        )
    return sorted(summaries, key=lambda item: item["role_archetype"])


def build_normalization_crosswalk(
    *,
    competencies: list[dict[str, Any]] | None = None,
    signals: list[dict[str, Any]] | None = None,
    decisions: list[dict[str, Any]] | None = None,
    releases: list[dict[str, Any]] | None = None,
    pedagogies: list[dict[str, Any]] | None = None,
    evidence_rows: list[dict[str, Any]] | None = None,
    outcomes: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    competencies = competencies if competencies is not None else load_json("role_competencies.json")
    signals = signals if signals is not None else load_json("signals.json")
    decisions = decisions if decisions is not None else load_json("decisions.json")
    releases = releases if releases is not None else load_json("releases.json")
    pedagogies = pedagogies if pedagogies is not None else load_json("pedagogy_map.json")
    evidence_rows = evidence_rows if evidence_rows is not None else load_json("learner_evidence_summary.json")
    outcomes = outcomes if outcomes is not None else load_json("cohort_outcomes.json")

    signals_by_id = index_by_id(signals, "signal_id")
    decisions_by_id = index_by_id(decisions, "decision_id")
    releases_by_id = index_by_id(releases, "release_id")
    pedagogies_by_id = index_by_id(pedagogies, "pedagogy_id")
    evidence_lookup = evidence_by_competency(evidence_rows)
    outcome_lookup = outcomes_by_cohort(outcomes)

    rows = [
        build_crosswalk_row(
            competency,
            signals_by_id=signals_by_id,
            decisions_by_id=decisions_by_id,
            releases_by_id=releases_by_id,
            pedagogies_by_id=pedagogies_by_id,
            evidence_lookup=evidence_lookup,
            outcome_lookup=outcome_lookup,
        )
        for competency in competencies
    ]
    state_counts = Counter(row["crosswalk_state"] for row in rows)
    role_summaries = build_role_summary(rows)
    return {
        "purpose": (
            "Show whether role, competency, pedagogy, decision, release, learner-evidence, and outcome "
            "language is coherent enough for pilot planning before ontology or schema commitments."
        ),
        "summary": {
            "role_count": len(role_summaries),
            "competency_count": len(rows),
            "aligned_for_planning_count": state_counts["aligned_for_planning"],
            "evidence_pending_count": state_counts["evidence_pending"],
            "implementation_pending_count": state_counts["implementation_pending"],
            "suppressed_evidence_count": state_counts["suppressed_evidence"],
            "monitor_only_count": state_counts["monitor_only"],
            "needs_mapping_count": state_counts["needs_mapping"],
            "ontology_schema_work": "deferred",
        },
        "guardrails": [
            "This crosswalk clarifies language and joins; it is not a canonical ontology schema.",
            "Monitor-only competencies should stay out of standalone credentials until signal pull strengthens.",
            "Suppressed or pending evidence cannot support readiness claims.",
            "Implementation-pending releases cannot be treated as proof of activation.",
            "Use crosswalk gaps to shape pilot extracts before designing tables.",
        ],
        "role_summaries": role_summaries,
        "rows": sorted(rows, key=lambda row: (row["role_archetype"], row["competency_id"])),
    }


def render_normalization_crosswalk_text(crosswalk: dict[str, Any]) -> str:
    summary = crosswalk["summary"]
    lines = [
        "Normalization Crosswalk Review",
        "==============================",
        "",
        crosswalk["purpose"],
        "",
        "Summary",
        "-------",
        (
            f"- roles={summary['role_count']} competencies={summary['competency_count']} "
            f"aligned_for_planning={summary['aligned_for_planning_count']} "
            f"evidence_pending={summary['evidence_pending_count']} "
            f"implementation_pending={summary['implementation_pending_count']} "
            f"suppressed_evidence={summary['suppressed_evidence_count']} "
            f"monitor_only={summary['monitor_only_count']} needs_mapping={summary['needs_mapping_count']}"
        ),
        f"- ontology_schema_work={summary['ontology_schema_work']}",
        "",
        "Guardrails",
        "----------",
    ]
    lines.extend(f"- {guardrail}" for guardrail in crosswalk["guardrails"])
    lines.extend(["", "Role Summary", "------------"])
    for role in crosswalk["role_summaries"]:
        states = ", ".join(f"{state}:{count}" for state, count in role["states"].items())
        clusters = ", ".join(role["clusters"])
        owners = ", ".join(role["owners"])
        lines.extend(
            [
                f"- {role['role_archetype']}: competencies={role['competency_count']} states={states}",
                f"  clusters: {clusters}",
                f"  owners: {owners}",
            ]
        )
    lines.extend(["", "Crosswalk Rows", "--------------"])
    for row in crosswalk["rows"]:
        flags = ", ".join(row["ambiguity_flags"]) or "none"
        releases = ", ".join(row["release_ids"]) or "none"
        pedagogies = ", ".join(row["pedagogy_ids"]) or "none"
        evidence = ", ".join(row["evidence_ids"]) or "none"
        outcomes = ", ".join(row["outcome_cohort_ids"]) or "none"
        lines.extend(
            [
                f"- [{row['crosswalk_state']}] {row['competency_id']} {row['role_archetype']} / {row['competency_cluster']}",
                f"  capability: {row['capability']}",
                f"  proficiency: {row['target_proficiency']} | priority: {row['market_priority']} | status: {row['status']}",
                f"  signals: {', '.join(row['signal_ids'])} | decisions: {', '.join(row['decision_ids'])}",
                f"  releases: {releases} | pedagogy: {pedagogies} | evidence: {evidence} | outcomes: {outcomes}",
                f"  flags: {flags}",
                f"  focus: {row['normalization_focus']}",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"
