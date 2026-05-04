"""Directional v0.2 intelligence preview.

This layer previews the future role-demand, competency-gap, horizon, and
curriculum-impact surfaces without claiming production forecasting or causal
simulation from synthetic seed data.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from statistics import mean
from typing import Any

from decision_spine.data_access import load_json
from decision_spine.services.schema_gap import build_schema_gap_report


GUARDRAILS = [
    "Directional preview only: synthetic seed data cannot support hard role-demand, competency-gap, horizon, or impact claims.",
    "No v0.2 intelligence output should become a recommendation until missing fields have named owners and approved source posture.",
    "Learner-derived evidence remains blocked when privacy or suppression gates are unresolved.",
    "Curriculum-impact estimates remain hypotheses until cost, learner-time, placement, and extension fields exist.",
]


SECTION_META = {
    "role_anchor_demand_index": {
        "label": "Role Anchor Demand Index",
        "question": "Which role anchors look worth prioritizing once demand-volume and conversion fields exist?",
    },
    "competency_gap_index": {
        "label": "Competency Gap Index",
        "question": "Which competencies look like teach-now, monitor, or deprecate candidates once market and learner gap fields exist?",
    },
    "horizon_radar": {
        "label": "Horizon Radar",
        "question": "Which weak or scored signals need horizon review before they become curriculum claims?",
    },
    "curriculum_impact_simulator": {
        "label": "Curriculum Impact Simulator",
        "question": "Which curriculum changes can be reviewed directionally before cost and impact assumptions exist?",
    },
}


def pct(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.0%}"


def avg(values: list[float]) -> float | None:
    return round(mean(values), 1) if values else None


def action_key(capability: str, field: str) -> str:
    return f"{capability}:{field}"


def requirement_map(schema_gap: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item["capability"]: item for item in schema_gap["v02_requirements"]}


def actions_for_capabilities(schema_gap: dict[str, Any], capabilities: set[str]) -> list[dict[str, Any]]:
    return [action for action in schema_gap["field_actions"] if action["capability"] in capabilities]


def missing_for_capabilities(schema_gap: dict[str, Any], capabilities: set[str]) -> list[dict[str, Any]]:
    requirements = requirement_map(schema_gap)
    missing: list[dict[str, Any]] = []
    for capability in sorted(capabilities):
        requirement = requirements[capability]
        for field in requirement["missing_field_details"]:
            missing.append(
                {
                    "capability": capability,
                    "capability_label": requirement["label"],
                    "field": field["field"],
                    "source_owner": field.get("source_owner", requirement.get("owner", "")),
                    "privacy_sensitivity": field.get("privacy_sensitivity", requirement.get("privacy_sensitivity", "")),
                    "purpose": field.get("purpose", "Field required by the v0.2 contract."),
                }
            )
    return missing


def readiness_for(missing_fields: list[dict[str, Any]], actions: list[dict[str, Any]]) -> dict[str, str]:
    if any(action["blocked"] for action in actions):
        return {
            "status": "blocked",
            "tone": "red",
            "label": "Blocked",
            "reason": "At least one required field is blocked by privacy or suppression review.",
        }
    if missing_fields:
        return {
            "status": "field_gaps",
            "tone": "amber",
            "label": "Field gaps",
            "reason": "Required v0.2 fields are not yet covered by seed data, pilot templates, or source contracts.",
        }
    return {
        "status": "pilot_ready",
        "tone": "green",
        "label": "Pilot ready",
        "reason": "The current field contract is covered enough for a governed pilot review.",
    }


def next_actions(actions: list[dict[str, Any]], limit: int = 4) -> list[dict[str, str]]:
    return [
        {
            "owner": action["source_owner"],
            "field": action["field"],
            "status": action["action_status"],
            "severity": action["severity"],
            "text": action["action_text"],
        }
        for action in actions[:limit]
    ]


def make_section(
    section_id: str,
    schema_gap: dict[str, Any],
    capabilities: set[str],
    evidence: list[dict[str, Any]],
    findings: list[dict[str, str]],
    do_not_claim: str,
) -> dict[str, Any]:
    missing_fields = missing_for_capabilities(schema_gap, capabilities)
    actions = actions_for_capabilities(schema_gap, capabilities)
    readiness = readiness_for(missing_fields, actions)
    return {
        "id": section_id,
        "label": SECTION_META[section_id]["label"],
        "question": SECTION_META[section_id]["question"],
        "readiness": readiness,
        "recommendation_strength": "directional_only",
        "hard_recommendations_enabled": False,
        "evidence": evidence,
        "directional_findings": findings,
        "missing_fields": missing_fields,
        "missing_field_count": len(missing_fields),
        "next_actions": next_actions(actions),
        "do_not_claim": do_not_claim,
    }


def build_role_anchor_section(schema_gap: dict[str, Any], signals: list[dict[str, Any]]) -> dict[str, Any]:
    by_role: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for signal in signals:
        by_role[signal["role_archetype"]].append(signal)

    findings: list[dict[str, str]] = []
    for role, role_signals in sorted(by_role.items()):
        scores = [float(signal["signal_strength_score"]) for signal in role_signals]
        green_count = sum(1 for signal in role_signals if signal["status"] == "green")
        horizons = ", ".join(sorted(set(signal["horizon_window"] for signal in role_signals)))
        findings.append(
            {
                "title": role,
                "metric": f"{avg(scores)} avg signal strength",
                "detail": f"{green_count}/{len(role_signals)} green signal(s); horizon(s): {horizons}.",
                "tone": "amber" if green_count else "red",
            }
        )

    return make_section(
        "role_anchor_demand_index",
        schema_gap,
        {"role_anchor_demand_index"},
        [
            {"label": "Signals", "value": str(len(signals))},
            {"label": "Role anchors", "value": str(len(by_role))},
            {"label": "Green signals", "value": str(sum(1 for signal in signals if signal["status"] == "green"))},
        ],
        sorted(findings, key=lambda item: item["metric"], reverse=True),
        "Do not rank role anchors as RDI until demand volume, growth, hiring velocity, compensation pressure, durability, and placement alignment fields exist.",
    )


def build_competency_gap_section(
    schema_gap: dict[str, Any],
    competencies: list[dict[str, Any]],
    evidence_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    evidence_by_competency: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for evidence in evidence_rows:
        evidence_by_competency[evidence["competency_id"]].append(evidence)

    findings: list[dict[str, str]] = []
    for competency in competencies:
        linked_evidence = evidence_by_competency.get(competency["competency_id"], [])
        readiness_levels = sorted(set(item["readiness_level"] for item in linked_evidence)) or ["no_evidence"]
        suppressed = any(item.get("suppression_applied") for item in linked_evidence)
        if competency["market_priority"] == "monitor" or competency["status"] == "monitor":
            posture = "monitor"
            tone = "neutral"
        elif suppressed:
            posture = "privacy blocked"
            tone = "red"
        elif "pending" in readiness_levels or "no_evidence" in readiness_levels:
            posture = "teach-now candidate, evidence pending"
            tone = "amber"
        else:
            posture = "evidence emerging"
            tone = "amber"
        findings.append(
            {
                "title": competency["competency_cluster"],
                "metric": posture,
                "detail": f"{competency['role_archetype']} / {competency['market_priority']}; readiness: {', '.join(readiness_levels)}.",
                "tone": tone,
            }
        )

    return make_section(
        "competency_gap_index",
        schema_gap,
        {"competency_gap_index_market_side", "competency_gap_index_learner_side"},
        [
            {"label": "Competencies", "value": str(len(competencies))},
            {"label": "Evidence rows", "value": str(len(evidence_rows))},
            {"label": "Suppressed evidence rows", "value": str(sum(1 for item in evidence_rows if item.get("suppression_applied")))},
        ],
        findings,
        "Do not calculate CGI until market-required proficiency, demonstrated proficiency, and proficiency gap fields are defined and privacy-approved.",
    )


def build_horizon_section(schema_gap: dict[str, Any], predictions: list[dict[str, Any]]) -> dict[str, Any]:
    outcome_counts = Counter(prediction["outcome"] for prediction in predictions)
    findings = [
        {
            "title": prediction["prediction_id"],
            "metric": prediction["outcome"],
            "detail": prediction["claim"],
            "tone": "green" if prediction["outcome"] == "confirmed" else "amber" if prediction["outcome"] == "pending" else "red",
        }
        for prediction in predictions
    ]

    return make_section(
        "horizon_radar",
        schema_gap,
        {"horizon_radar"},
        [
            {"label": "Predictions", "value": str(len(predictions))},
            {"label": "Confirmed", "value": str(outcome_counts["confirmed"])},
            {"label": "Pending review", "value": str(outcome_counts["pending"])},
        ],
        findings,
        "Do not claim horizon maturity until maturity stage, weak-signal theme, and review due date fields exist.",
    )


def build_curriculum_impact_section(schema_gap: dict[str, Any], releases: list[dict[str, Any]]) -> dict[str, Any]:
    status_counts = Counter(release["release_status"] for release in releases)
    findings = [
        {
            "title": release["artifact"],
            "metric": release["release_status"],
            "detail": f"{release['programme']} / {release['change_scope']} / cohort {release['cohort_id']}.",
            "tone": "green" if release["release_status"] == "released" else "amber",
        }
        for release in releases
    ]

    return make_section(
        "curriculum_impact_simulator",
        schema_gap,
        {"curriculum_impact_simulator"},
        [
            {"label": "Releases", "value": str(len(releases))},
            {"label": "Released", "value": str(status_counts["released"])},
            {"label": "In progress", "value": str(status_counts["in_progress"])},
        ],
        findings,
        "Do not simulate impact until learner time, capacity cost, placement lift, and extension lift assumptions exist.",
    )


def build_v02_intelligence_preview() -> dict[str, Any]:
    schema_gap = build_schema_gap_report()
    signals = load_json("signals.json")
    competencies = load_json("role_competencies.json")
    learner_evidence = load_json("learner_evidence_summary.json")
    predictions = load_json("predictions.json")
    releases = load_json("releases.json")

    sections = [
        build_role_anchor_section(schema_gap, signals),
        build_competency_gap_section(schema_gap, competencies, learner_evidence),
        build_horizon_section(schema_gap, predictions),
        build_curriculum_impact_section(schema_gap, releases),
    ]
    missing_field_count = sum(section["missing_field_count"] for section in sections)
    blocked_sections = sum(1 for section in sections if section["readiness"]["status"] == "blocked")

    return {
        "summary": {
            "preview_status": "directional_only",
            "hard_recommendations_enabled": False,
            "section_count": len(sections),
            "missing_field_count": missing_field_count,
            "blocked_section_count": blocked_sections,
        },
        "guardrails": GUARDRAILS,
        "sections": sections,
    }


def render_v02_intelligence_preview_text(preview: dict[str, Any]) -> str:
    summary = preview["summary"]
    lines = [
        "Decision Spine v0.2 Intelligence Preview",
        "========================================",
        "",
        "Summary",
        "-------",
        f"- status={summary['preview_status']} hard_recommendations={summary['hard_recommendations_enabled']}",
        f"- sections={summary['section_count']} missing_fields={summary['missing_field_count']} blocked_sections={summary['blocked_section_count']}",
        "",
        "Guardrails",
        "----------",
    ]
    lines.extend(f"- {guardrail}" for guardrail in preview["guardrails"])
    for section in preview["sections"]:
        lines.extend(
            [
                "",
                section["label"],
                "-" * len(section["label"]),
                f"- readiness={section['readiness']['status']} missing_fields={section['missing_field_count']}",
                f"- question: {section['question']}",
                f"- do not claim: {section['do_not_claim']}",
                "- evidence: "
                + ", ".join(f"{item['label']}={item['value']}" for item in section["evidence"]),
            ]
        )
        lines.append("- directional findings:")
        for finding in section["directional_findings"][:5]:
            lines.append(f"  - {finding['title']}: {finding['metric']} - {finding['detail']}")
        lines.append("- next actions:")
        if not section["next_actions"]:
            lines.append("  - none")
        for action in section["next_actions"]:
            lines.append(f"  - {action['owner']}: {action['field']} ({action['status']})")
    return "\n".join(lines)
