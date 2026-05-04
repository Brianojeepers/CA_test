"""Structured monthly packet service for CLI export and future UI/API use."""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date, datetime
from statistics import mean
from typing import Any

from decision_spine.data_access import load_json
from scripts.decision_impact_review import deltas_for_cohort, impact_status
from scripts.validate_data import validate_all


TODAY = date.today()


STAKEHOLDER_DRILLDOWNS = [
    {"label": "Council", "command": "python3 scripts/council_review.py"},
    {"label": "Decision impact", "command": "python3 scripts/decision_impact_review.py"},
    {"label": "Matching and CSM outcomes", "command": "python3 scripts/outcome_review.py"},
    {"label": "Credential requirements", "command": "python3 scripts/credential_requirements.py"},
    {"label": "Learning outcomes", "command": "python3 scripts/learning_outcomes.py"},
    {"label": "Client positioning", "command": "python3 scripts/client_positioning.py"},
    {"label": "Training offers", "command": "python3 scripts/training_offer_inputs.py"},
    {"label": "Talent profile signals", "command": "python3 scripts/talent_profile_signals.py"},
    {"label": "Delivery windows", "command": "python3 scripts/delivery_window_review.py"},
    {"label": "Source contracts", "command": "python3 scripts/source_contract_review.py"},
]


KNOWN_LIMITS = [
    "Seed data is synthetic.",
    "Real learner and outcome extracts remain blocked by source-contract privacy rules.",
    "Actual cohort calendar detail is unavailable in v1.",
    "Placement and readiness evidence are directional until sample sizes and retention windows mature.",
]


def parse_date(value: str | None) -> date | None:
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


def days_between(start: str | None, end: str | None) -> int | None:
    start_date = parse_date(start)
    end_date = parse_date(end)
    if start_date is None or end_date is None:
        return None
    return (end_date - start_date).days


def fmt_pct(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.1%}"


def fmt_days(value: int | None) -> str:
    return "n/a" if value is None else f"{value}d"


def signal_to_decision_status(days: int | None) -> str:
    if days is None:
        return "red"
    if days <= 21:
        return "green"
    if days <= 45:
        return "amber"
    return "red"


def decision_to_release_status(days: int | None, complexity: str) -> str:
    if days is None:
        return "pending"
    thresholds = {
        "low": (14, 30),
        "medium": (30, 60),
        "high": (60, 90),
    }
    green_days, red_days = thresholds.get(complexity, thresholds["medium"])
    if days <= green_days:
        return "green"
    if days > red_days:
        return "red"
    return "amber"


def validation_warnings_or_raise() -> list[str]:
    validation = validate_all()
    if validation.errors:
        joined = "\n".join(f"- {error}" for error in validation.errors)
        raise ValueError(f"Data validation failed:\n{joined}")
    return validation.warnings


def recommendation_for_status(
    status: str,
    releases: list[dict[str, Any]],
    evidence: list[dict[str, Any]],
    cohorts: list[dict[str, Any]],
) -> dict[str, str]:
    if status == "positive_signal":
        return {
            "priority": "low",
            "recommended_action": "Consider amplifying the change while continuing retention monitoring.",
            "evidence_basis": "Released implementation has positive learner or cohort evidence.",
            "blocker_or_risk": "No immediate blocker; avoid overstating causality.",
            "next_review_trigger": "Next placement or retention refresh.",
        }
    if status == "evidence_emerging":
        return {
            "priority": "medium",
            "recommended_action": "Keep the decision on the review calendar and tighten evidence quality.",
            "evidence_basis": "Learner evidence is promising, but outcome maturity or confidence is incomplete.",
            "blocker_or_risk": "Placement, retention, or confidence is not mature enough for a stronger claim.",
            "next_review_trigger": "Placement window, retention window, or next learner-evidence aggregate closes.",
        }
    if status == "too_early":
        pending_releases = [item for item in releases if item["release_status"] != "released"]
        if pending_releases:
            release_names = ", ".join(item["release_id"] for item in pending_releases)
            return {
                "priority": "high",
                "recommended_action": "Unblock implementation before judging impact.",
                "evidence_basis": "At least one linked release is not complete.",
                "blocker_or_risk": f"Pending release: {release_names}.",
                "next_review_trigger": "Release status changes to released or pilot evidence becomes available.",
            }
        return {
            "priority": "medium",
            "recommended_action": "Wait for evidence and outcome windows before escalating the decision.",
            "evidence_basis": "Implementation exists, but learner or outcome evidence is still pending.",
            "blocker_or_risk": "Evidence window has not matured.",
            "next_review_trigger": "Learner evidence, placement, or retention data becomes available.",
        }
    if status == "needs_attention":
        suppressed = any(item.get("suppression_applied") for item in evidence)
        low_sample = any(item.get("readiness_level") == "insufficient_sample" for item in evidence)
        pending_outcomes = any(item["placement_rate"] is None or item["retention_90d_rate"] is None for item in cohorts)
        risk_parts = []
        if suppressed:
            risk_parts.append("suppressed evidence")
        if low_sample:
            risk_parts.append("insufficient sample")
        if pending_outcomes:
            risk_parts.append("pending outcomes")
        risk_text = ", ".join(risk_parts) if risk_parts else "readiness or outcome risk"
        return {
            "priority": "high",
            "recommended_action": "Review release quality, rubric thresholds, sample size, and outcome signals.",
            "evidence_basis": "Evidence or outcomes indicate risk rather than a confident positive signal.",
            "blocker_or_risk": risk_text,
            "next_review_trigger": "Corrective action is logged or the next non-suppressed evidence aggregate is available.",
        }
    return {
        "priority": "medium",
        "recommended_action": "Add learner evidence or cohort outcome linkage before making an impact claim.",
        "evidence_basis": "Decision has traceability, but no relevant learner or cohort evidence is linked.",
        "blocker_or_risk": "Missing outcome evidence.",
        "next_review_trigger": "Evidence or cohort outcome record is linked.",
    }


def build_decision_impact_rows(
    decisions: list[dict[str, Any]],
    releases: list[dict[str, Any]],
    competencies: list[dict[str, Any]],
    evidence: list[dict[str, Any]],
    cohorts: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    releases_by_decision: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for release in releases:
        releases_by_decision[release["decision_id"]].append(release)

    competencies_by_decision: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for competency in competencies:
        for decision_id in competency["linked_decision_ids"]:
            competencies_by_decision[decision_id].append(competency)

    evidence_by_competency: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in evidence:
        evidence_by_competency[item["competency_id"]].append(item)

    cohorts_by_id = {cohort["cohort_id"]: cohort for cohort in cohorts}
    baselines_by_group: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for cohort in cohorts:
        if cohort["change_exposure"] == "pre_change":
            baselines_by_group[cohort["baseline_group"]].append(cohort)

    rows: list[dict[str, Any]] = []
    for decision in decisions:
        if decision["decision_status"] != "approved":
            continue
        linked_releases = releases_by_decision.get(decision["decision_id"], [])
        linked_competencies = competencies_by_decision.get(decision["decision_id"], [])
        linked_evidence = [
            item
            for competency in linked_competencies
            for item in evidence_by_competency.get(competency["competency_id"], [])
        ]
        linked_cohorts = [
            cohorts_by_id[release["cohort_id"]]
            for release in linked_releases
            if release["cohort_id"] in cohorts_by_id
        ]
        placement_deltas: list[float] = []
        retention_deltas: list[float] = []
        for cohort in linked_cohorts:
            placement_delta, retention_delta = deltas_for_cohort(cohort, baselines_by_group)
            if placement_delta is not None:
                placement_deltas.append(placement_delta)
            if retention_delta is not None:
                retention_deltas.append(retention_delta)
        status = impact_status(
            linked_releases,
            linked_evidence,
            linked_cohorts,
            placement_deltas,
            retention_deltas,
        )
        rows.append(
            {
                "decision_id": decision["decision_id"],
                "status": status,
                "owner": decision["owner"],
                "partner_functions": decision["partner_functions"],
                "summary": decision["decision_summary"],
                "decision_type": decision["decision_type"],
                "signal_ids": decision["signal_ids"],
                "release_refs": [
                    {"release_id": release["release_id"], "status": release["release_status"]}
                    for release in linked_releases
                ],
                "competency_ids": [competency["competency_id"] for competency in linked_competencies],
                "evidence_ids": [item["evidence_id"] for item in linked_evidence],
                "recommendation": recommendation_for_status(
                    status,
                    linked_releases,
                    linked_evidence,
                    linked_cohorts,
                ),
            }
        )
    return rows


def build_action_items(
    signals: list[dict[str, Any]],
    decisions: list[dict[str, Any]],
    releases: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    decisions_by_signal: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for decision in decisions:
        for signal_id in decision["signal_ids"]:
            decisions_by_signal[signal_id].append(decision)

    items: list[dict[str, Any]] = []
    for signal in signals:
        linked_decisions = decisions_by_signal.get(signal["signal_id"], [])
        if signal["status"] == "green" and not linked_decisions:
            items.append(
                {
                    "kind": "decision_owner",
                    "severity": "red",
                    "text": f"Assign decision owner for {signal['signal_id']} {signal['signal_theme']}.",
                    "signal_id": signal["signal_id"],
                }
            )
        elif signal["status"] == "green" and linked_decisions:
            first_decision = min(linked_decisions, key=lambda item: item["decision_signed_date"])
            elapsed = days_between(signal["green_threshold_date"], first_decision["decision_signed_date"])
            status = signal_to_decision_status(elapsed)
            if status in {"amber", "red"}:
                items.append(
                    {
                        "kind": "decision_latency",
                        "severity": status,
                        "text": (
                            f"Review {signal['signal_id']} -> {first_decision['decision_id']} "
                            f"({status}, {fmt_days(elapsed)}, owner={first_decision['owner']})."
                        ),
                        "signal_id": signal["signal_id"],
                        "decision_id": first_decision["decision_id"],
                        "elapsed_days": elapsed,
                    }
                )

    releases_by_decision: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for release in releases:
        releases_by_decision[release["decision_id"]].append(release)

    for decision in decisions:
        if decision["decision_status"] != "approved":
            continue
        linked_releases = releases_by_decision.get(decision["decision_id"], [])
        if not linked_releases:
            items.append(
                {
                    "kind": "missing_release",
                    "severity": "red",
                    "text": f"Create release record for {decision['decision_id']} owner={decision['owner']}.",
                    "decision_id": decision["decision_id"],
                }
            )
        for release in linked_releases:
            elapsed = days_between(decision["decision_signed_date"], release["release_date"])
            status = decision_to_release_status(elapsed, decision["complexity_tier"])
            if status in {"pending", "red"}:
                items.append(
                    {
                        "kind": "release_blocker",
                        "severity": status,
                        "text": (
                            f"Unblock {decision['decision_id']} -> {release['release_id']} "
                            f"({status}, owner={decision['owner']}, artifact={release['artifact']})."
                        ),
                        "decision_id": decision["decision_id"],
                        "release_id": release["release_id"],
                        "elapsed_days": elapsed,
                    }
                )
    return items


def build_monthly_packet() -> dict[str, Any]:
    warnings = validation_warnings_or_raise()
    signals = load_json("signals.json")
    decisions = load_json("decisions.json")
    releases = load_json("releases.json")
    cohorts = load_json("cohort_outcomes.json")
    predictions = load_json("predictions.json")
    competencies = load_json("role_competencies.json")
    evidence = load_json("learner_evidence_summary.json")

    signal_counts = Counter(signal["status"] for signal in signals)
    signal_avg = mean(signal["signal_strength_score"] for signal in signals)
    scored_predictions = [
        prediction
        for prediction in predictions
        if parse_date(prediction["scoring_date"]) <= TODAY
        and prediction["outcome"] in {"confirmed", "contradicted"}
    ]
    prediction_accuracy = None
    if scored_predictions:
        prediction_accuracy = sum(item["accuracy_score"] for item in scored_predictions) / len(scored_predictions)
    pending_outcome_count = sum(
        1
        for cohort in cohorts
        if cohort["change_exposure"] == "post_change"
        and (cohort["placement_rate"] is None or cohort["retention_90d_rate"] is None)
    )
    impact_rows = build_decision_impact_rows(decisions, releases, competencies, evidence, cohorts)
    impact_counts = Counter(row["status"] for row in impact_rows)
    action_items = build_action_items(signals, decisions, releases)

    return {
        "generated_date": TODAY.isoformat(),
        "data_trust": {
            "validation_status": "passed",
            "warning_count": len(warnings),
            "warnings": warnings,
        },
        "kpi_posture": {
            "signal_strength": {
                "average": signal_avg,
                "green": signal_counts["green"],
                "amber": signal_counts["amber"],
                "red": signal_counts["red"],
            },
            "prediction_accuracy": {
                "value": prediction_accuracy,
                "scored_count": len(scored_predictions),
            },
            "pending_post_change_outcomes": pending_outcome_count,
        },
        "decision_impact": {
            "counts": {
                status: impact_counts[status]
                for status in (
                    "positive_signal",
                    "evidence_emerging",
                    "too_early",
                    "needs_attention",
                    "no_outcome_data",
                )
            },
            "rows": impact_rows,
        },
        "actions": action_items,
        "stakeholder_drilldowns": STAKEHOLDER_DRILLDOWNS,
        "known_limits": KNOWN_LIMITS,
    }


def render_monthly_packet_markdown(packet: dict[str, Any]) -> str:
    signal_strength = packet["kpi_posture"]["signal_strength"]
    prediction_accuracy = packet["kpi_posture"]["prediction_accuracy"]
    impact_counts = packet["decision_impact"]["counts"]
    lines = [
        "# Decision Spine Monthly Packet",
        "",
        f"Generated: {packet['generated_date']}",
        "",
        "## Data Trust",
        "",
        f"- Validation: passed with {packet['data_trust']['warning_count']} warning(s).",
    ]
    for warning in packet["data_trust"]["warnings"]:
        lines.append(f"- Warning: `{warning}`")

    lines.extend(
        [
            "",
            "## KPI Posture",
            "",
            f"- K1 signal strength: avg={signal_strength['average']:.1f}; "
            f"green={signal_strength['green']}; amber={signal_strength['amber']}; red={signal_strength['red']}.",
            f"- K7 prediction accuracy: {fmt_pct(prediction_accuracy['value'])} "
            f"({prediction_accuracy['scored_count']} scored).",
            f"- Outcome data pending for {packet['kpi_posture']['pending_post_change_outcomes']} "
            "post-change cohort(s).",
            "",
            "## Decision Impact",
            "",
            f"- positive_signal={impact_counts['positive_signal']}",
            f"- evidence_emerging={impact_counts['evidence_emerging']}",
            f"- too_early={impact_counts['too_early']}",
            f"- needs_attention={impact_counts['needs_attention']}",
            f"- no_outcome_data={impact_counts['no_outcome_data']}",
            "",
            "| Decision | Status | Owner | Releases |",
            "| --- | --- | --- | --- |",
        ]
    )
    for row in packet["decision_impact"]["rows"]:
        release_text = ", ".join(
            f"{release['release_id']}:{release['status']}" for release in row["release_refs"]
        ) or "none"
        lines.append(f"| `{row['decision_id']}` | `{row['status']}` | {row['owner']} | {release_text} |")

    lines.extend(["", "## Decisions Needing Action", ""])
    if packet["actions"]:
        for item in packet["actions"]:
            lines.append(f"- {item['text']}")
    else:
        lines.append("- None.")

    lines.extend(["", "## Stakeholder Drill-Downs", ""])
    for item in packet["stakeholder_drilldowns"]:
        lines.append(f"- {item['label']}: `{item['command']}`")

    lines.extend(["", "## Current Known Limits", ""])
    for limit in packet["known_limits"]:
        lines.append(f"- {limit}")
    lines.append("")
    return "\n".join(lines)


def render_monthly_packet_text(packet: dict[str, Any]) -> str:
    signal_strength = packet["kpi_posture"]["signal_strength"]
    prediction_accuracy = packet["kpi_posture"]["prediction_accuracy"]
    impact_counts = packet["decision_impact"]["counts"]
    lines = [
        "Decision Spine Monthly Packet",
        f"Generated: {packet['generated_date']}",
        "",
        "Data Trust",
        "----------",
        f"- passed with {packet['data_trust']['warning_count']} warning(s)",
    ]
    for warning in packet["data_trust"]["warnings"][:3]:
        lines.append(f"- warning: {warning}")
    lines.extend(
        [
            "",
            "KPI Posture",
            "-----------",
            f"- K1 signal strength: avg={signal_strength['average']:.1f} "
            f"green={signal_strength['green']} amber={signal_strength['amber']} red={signal_strength['red']}",
            f"- K7 prediction accuracy: {fmt_pct(prediction_accuracy['value'])} "
            f"({prediction_accuracy['scored_count']} scored)",
            f"- Outcome data pending for {packet['kpi_posture']['pending_post_change_outcomes']} "
            "post-change cohort(s)",
            "",
            "Decision Impact",
            "---------------",
            f"- positive_signal={impact_counts['positive_signal']}",
            f"- evidence_emerging={impact_counts['evidence_emerging']}",
            f"- too_early={impact_counts['too_early']}",
            f"- needs_attention={impact_counts['needs_attention']}",
            f"- no_outcome_data={impact_counts['no_outcome_data']}",
            "",
            "Decisions Needing Action",
            "------------------------",
        ]
    )
    if packet["actions"]:
        for item in packet["actions"][:6]:
            lines.append(f"- {item['text']}")
    else:
        lines.append("- none")
    return "\n".join(lines)
