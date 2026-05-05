"""Decision policy checks for safe action under current evidence posture."""

from __future__ import annotations

from collections import Counter
from typing import Any

from decision_spine.data_access import load_json
from decision_spine.services.monthly_packet import build_monthly_packet
from decision_spine.services.stakeholder_journey import build_stakeholder_journey_map


POLICY_OUTCOMES: tuple[dict[str, str], ...] = (
    {
        "outcome": "act_now",
        "label": "Act now",
        "required_trust_posture": "Pilot-candidate or decision-grade evidence posture with no unresolved privacy blocker for the approving journey.",
        "evidence_conditions": "Released implementation, positive learner or outcome evidence, mature evidence window, and no suppressed or red source dependency.",
        "who_can_decide": "Signal Intelligence Council with the accountable functional owner.",
        "allowed_action": "Amplify, scale, or convert the change into the next operating plan.",
        "must_defer": "Do not automate downstream writes or claim causality without stronger longitudinal evidence.",
        "escalation_trigger": "Any red source contract, suppressed evidence, or negative outcome delta moves the policy out of act-now.",
    },
    {
        "outcome": "revise",
        "label": "Revise",
        "required_trust_posture": "Any posture, provided the revision is framed as implementation correction rather than evidence proof.",
        "evidence_conditions": "Pending implementation, blocked release, rubric quality concern, or evidence quality gap.",
        "who_can_decide": "Accountable functional owner with council visibility.",
        "allowed_action": "Revise scope, release plan, rubric, sample strategy, or evidence requirement.",
        "must_defer": "Do not present the decision as working until revised evidence is reviewed.",
        "escalation_trigger": "Revision cannot be completed without source-owner, privacy, or delivery-lead action.",
    },
    {
        "outcome": "monitor",
        "label": "Monitor",
        "required_trust_posture": "Workflow-design-only, planning-ready, or manual-review posture is acceptable if limits are visible.",
        "evidence_conditions": "Directional evidence exists, but outcome maturity, confidence, or source posture is not strong enough for action.",
        "who_can_decide": "Council chair, Research, or the functional owner named on the decision.",
        "allowed_action": "Keep on review calendar, gather evidence, and preserve known limits.",
        "must_defer": "Do not scale, archive, or make stakeholder claims from directional evidence alone.",
        "escalation_trigger": "Monitoring exceeds review window, signal strengthens, or a blocker becomes red.",
    },
    {
        "outcome": "wait",
        "label": "Wait",
        "required_trust_posture": "Any posture where the evidence window, release window, or source intake is not yet mature.",
        "evidence_conditions": "Evidence is pending, outcomes are not available, or source-owner intake is not accepted.",
        "who_can_decide": "Functional owner with council review date recorded.",
        "allowed_action": "Hold decision claims and define the next review trigger.",
        "must_defer": "Do not change thresholds, publish claims, or deepen schema work while the gate is immature.",
        "escalation_trigger": "The wait state passes its review trigger without new evidence or owner response.",
    },
    {
        "outcome": "escalate",
        "label": "Escalate",
        "required_trust_posture": "Any posture with red source blockers, suppressed evidence, negative outcome direction, or unresolved ownership.",
        "evidence_conditions": "Risk is visible and cannot be resolved by passive monitoring.",
        "who_can_decide": "Council chair routes to privacy owner, source owner, delivery lead, or functional owner.",
        "allowed_action": "Create a named blocker, assign owner, and require a follow-up decision.",
        "must_defer": "Do not keep recycling the decision in review without owner-level intervention.",
        "escalation_trigger": "Privacy block, insufficient sample, negative outcome direction, missing release, or stale ownership.",
    },
    {
        "outcome": "archive",
        "label": "Archive",
        "required_trust_posture": "Evidence remains weak, rejected, stale, or superseded after review.",
        "evidence_conditions": "Signal is rejected or repeatedly weak; no owner accepts action; or a later decision supersedes the claim.",
        "who_can_decide": "Signal Intelligence Council.",
        "allowed_action": "Retire the claim, record rationale, and remove it from active operating queues.",
        "must_defer": "Do not silently delete evidence; preserve audit trail and rationale.",
        "escalation_trigger": "Archive is disputed by an owner or tied to an active release.",
    },
)


OWNER_TO_JOURNEY = {
    "Signal Intelligence Council": "council",
    "Assessment Ops": "assessment_ops",
    "Learning": "learning",
    "Research": "market_intelligence",
}


POLICY_LABELS = {item["outcome"]: item["label"] for item in POLICY_OUTCOMES}


def policy_catalog() -> list[dict[str, str]]:
    return [dict(item) for item in POLICY_OUTCOMES]


def stakeholder_journey_for(owner: str, journey_map: dict[str, Any]) -> dict[str, Any]:
    journey_id = OWNER_TO_JOURNEY.get(owner, "council")
    journeys = {journey["stakeholder_id"]: journey for journey in journey_map["journeys"]}
    return journeys[journey_id]


def policy_for_impact_row(row: dict[str, Any], journey: dict[str, Any]) -> tuple[str, str]:
    status = row["status"]
    priority = row["recommendation"]["priority"]
    if status == "needs_attention":
        return (
            "escalate",
            "Decision has evidence or outcome risk that requires owner-level intervention.",
        )
    if status == "too_early" and priority == "high":
        return (
            "revise",
            "Implementation is blocked or incomplete, so the safe action is to revise the release path.",
        )
    if status == "too_early":
        return (
            "wait",
            "Evidence or outcome windows have not matured enough for an operating claim.",
        )
    if status == "positive_signal":
        if journey["current_mode"] in {"pilot_candidate"}:
            return (
                "act_now",
                "Positive evidence and source posture are strong enough for controlled amplification.",
            )
        return (
            "monitor",
            "Evidence is positive, but the stakeholder journey is not yet trusted enough for act-now claims.",
        )
    if status == "evidence_emerging":
        return (
            "monitor",
            "Evidence is promising but not mature enough to scale or claim impact.",
        )
    return (
        "wait",
        "Traceability exists, but relevant learner or cohort evidence is missing.",
    )


def build_policy_row(row: dict[str, Any], journey_map: dict[str, Any]) -> dict[str, Any]:
    journey = stakeholder_journey_for(row["owner"], journey_map)
    policy, rationale = policy_for_impact_row(row, journey)
    return {
        "decision_id": row["decision_id"],
        "source": "decision_impact",
        "owner": row["owner"],
        "stakeholder_journey": journey["label"],
        "journey_mode": journey["current_mode"],
        "impact_status": row["status"],
        "policy_outcome": policy,
        "policy_label": POLICY_LABELS[policy],
        "rationale": rationale,
        "allowed_action": allowed_action_for(policy),
        "must_defer": deferred_action_for(policy, journey["current_mode"]),
        "escalation_trigger": escalation_trigger_for(policy, row),
        "next_review_trigger": row["recommendation"]["next_review_trigger"],
        "recommendation": row["recommendation"]["recommended_action"],
    }


def build_monitor_policy_row(decision: dict[str, Any], journey_map: dict[str, Any]) -> dict[str, Any]:
    journey = stakeholder_journey_for(str(decision["owner"]), journey_map)
    return {
        "decision_id": decision["decision_id"],
        "source": "watch_decision",
        "owner": decision["owner"],
        "stakeholder_journey": journey["label"],
        "journey_mode": journey["current_mode"],
        "impact_status": "not_impact_scored",
        "policy_outcome": "monitor",
        "policy_label": POLICY_LABELS["monitor"],
        "rationale": "Decision is explicitly in watch/monitor posture and has no implementation claim.",
        "allowed_action": allowed_action_for("monitor"),
        "must_defer": "Do not create curriculum, credential, or assessment requirements until the signal strengthens.",
        "escalation_trigger": "Signal becomes green, commercial pull increases, or the council decides the watch state is stale.",
        "next_review_trigger": "Next signal review or horizon refresh.",
        "recommendation": "Continue signal monitoring before creating a release.",
    }


def allowed_action_for(policy: str) -> str:
    catalog = {item["outcome"]: item for item in POLICY_OUTCOMES}
    return catalog[policy]["allowed_action"]


def deferred_action_for(policy: str, journey_mode: str) -> str:
    catalog = {item["outcome"]: item for item in POLICY_OUTCOMES}
    if journey_mode == "workflow_design_only" and policy in {"monitor", "wait", "revise"}:
        return "Keep action internal and directional; do not make performance or stakeholder-facing proof claims."
    return catalog[policy]["must_defer"]


def escalation_trigger_for(policy: str, row: dict[str, Any]) -> str:
    if policy == "revise":
        releases = ", ".join(release["release_id"] for release in row.get("release_refs", []) if release["status"] != "released")
        if releases:
            return f"Release remains incomplete: {releases}."
    if policy == "escalate":
        return row["recommendation"]["blocker_or_risk"]
    catalog = {item["outcome"]: item for item in POLICY_OUTCOMES}
    return catalog[policy]["escalation_trigger"]


def build_decision_policy_review(
    packet: dict[str, Any] | None = None,
    journey_map: dict[str, Any] | None = None,
    decisions: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    packet = packet or build_monthly_packet()
    journey_map = journey_map or build_stakeholder_journey_map()
    decisions = decisions if decisions is not None else load_json("decisions.json")
    policy_rows = [
        build_policy_row(row, journey_map)
        for row in packet["decision_impact"]["rows"]
    ]
    policy_rows.extend(
        build_monitor_policy_row(decision, journey_map)
        for decision in decisions
        if decision["decision_status"] in {"watch", "deferred"} or decision["decision_type"] == "monitor"
    )
    outcome_counts = Counter(row["policy_outcome"] for row in policy_rows)
    return {
        "generated_date": packet["generated_date"],
        "purpose": (
            "Convert current evidence, trust, impact, and stakeholder-journey posture into explicit "
            "operating decisions: act now, revise, monitor, wait, escalate, or archive."
        ),
        "summary": {
            "decision_count": len(policy_rows),
            "act_now_count": outcome_counts["act_now"],
            "revise_count": outcome_counts["revise"],
            "monitor_count": outcome_counts["monitor"],
            "wait_count": outcome_counts["wait"],
            "escalate_count": outcome_counts["escalate"],
            "archive_count": outcome_counts["archive"],
        },
        "guardrails": [
            "Policy outcomes are operating guidance, not automated approvals.",
            "Workflow-design-only journeys can monitor, wait, revise, or escalate, but cannot support performance claims.",
            "Act-now requires positive evidence plus source posture strong enough for controlled amplification.",
            "Escalate when risk is visible and passive monitoring would hide ownership.",
            "Archive must preserve the rationale and audit trail.",
        ],
        "policy_catalog": policy_catalog(),
        "policy_rows": sorted(policy_rows, key=lambda row: (policy_sort_order(row["policy_outcome"]), row["decision_id"])),
    }


def policy_sort_order(policy: str) -> int:
    return {
        "escalate": 0,
        "revise": 1,
        "wait": 2,
        "monitor": 3,
        "act_now": 4,
        "archive": 5,
    }.get(policy, 9)


def render_decision_policy_text(review: dict[str, Any]) -> str:
    summary = review["summary"]
    lines = [
        "Decision Policy Review",
        "======================",
        "",
        f"Generated: {review['generated_date']}",
        "",
        review["purpose"],
        "",
        "Summary",
        "-------",
        (
            f"- decisions={summary['decision_count']} act_now={summary['act_now_count']} "
            f"revise={summary['revise_count']} monitor={summary['monitor_count']} "
            f"wait={summary['wait_count']} escalate={summary['escalate_count']} archive={summary['archive_count']}"
        ),
        "",
        "Guardrails",
        "----------",
    ]
    lines.extend(f"- {guardrail}" for guardrail in review["guardrails"])
    lines.extend(["", "Policy Catalog", "--------------"])
    for item in review["policy_catalog"]:
        lines.extend(
            [
                f"- [{item['outcome']}] {item['label']}",
                f"  trust: {item['required_trust_posture']}",
                f"  evidence: {item['evidence_conditions']}",
                f"  decides: {item['who_can_decide']}",
                f"  allowed: {item['allowed_action']}",
                f"  defer: {item['must_defer']}",
                f"  escalate: {item['escalation_trigger']}",
            ]
        )
    lines.extend(["", "Current Decision Policies", "-------------------------"])
    for row in review["policy_rows"]:
        lines.extend(
            [
                f"- [{row['policy_outcome']}] {row['decision_id']} ({row['owner']}, {row['journey_mode']})",
                f"  impact: {row['impact_status']} | journey: {row['stakeholder_journey']}",
                f"  reason: {row['rationale']}",
                f"  allowed: {row['allowed_action']}",
                f"  defer: {row['must_defer']}",
                f"  trigger: {row['next_review_trigger']}",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"
