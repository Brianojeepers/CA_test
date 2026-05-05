"""Manual governance cadence definitions for the Decision Spine MVP."""

from __future__ import annotations

from collections import Counter
from datetime import date
from typing import Any


TODAY = date.today()


CADENCE_REVIEWS: tuple[dict[str, Any], ...] = (
    {
        "cadence_id": "weekly_signal_refresh",
        "cadence": "weekly",
        "label": "Weekly signal and source-quality refresh",
        "owner": "Market Intelligence and Research",
        "participants": ["Research", "Data and Analytics", "Source Owners", "Council Chair"],
        "purpose": "Review new or changed signals, source blockers, freshness posture, and urgent evidence-quality risks.",
        "entry_criteria": [
            "Seed data validation has no errors.",
            "Source ingestion and trust registry reviews are current.",
            "New or changed signals have source, confidence, and horizon context.",
            "Open source-owner and privacy blockers are visible.",
        ],
        "required_artifacts": [
            "scripts/validate_data.py",
            "scripts/signal_review.py",
            "scripts/source_ingestion_review.py",
            "scripts/trust_registry_review.py",
            "scripts/schema_gap_review.py",
        ],
        "exit_criteria": [
            "Signals are classified as act, track, monitor, or exclude.",
            "Freshness or ownership blockers have named owners.",
            "Urgent source-quality issues are escalated to the council chair or privacy owner.",
            "No scheduled ingestion or database work is started from this review alone.",
        ],
        "decision_rights": [
            "Classify signal posture.",
            "Request source-owner clarification.",
            "Escalate red privacy or ownership blockers.",
            "Recommend council agenda items for monthly review.",
        ],
        "escalation_triggers": [
            "Red source contract blocks a stakeholder-facing surface.",
            "A green signal lacks a competency, decision, or source-quality path.",
            "A source owner cannot confirm grain, freshness, or allowed use.",
        ],
        "deferred_work": [
            "Scheduled ingestion",
            "Warehouse landing tables",
            "Automated source pulls",
            "Production freshness monitoring",
        ],
        "manual_readiness": "ready_for_manual_trial",
    },
    {
        "cadence_id": "monthly_council_review",
        "cadence": "monthly",
        "label": "Monthly council decision review",
        "owner": "Signal Intelligence Council Chair",
        "participants": ["Council", "Learning", "Assessment Ops", "Matching and CSM", "Solutions and Sales", "Data and Analytics"],
        "purpose": "Convert evidence, policy, stakeholder journeys, and reasoning stress tests into safe operating decisions.",
        "entry_criteria": [
            "Monthly packet is generated from current seed data.",
            "Decision policy and reasoning stress reviews pass.",
            "Normalization crosswalk exposes pending, suppressed, and monitor-only competencies.",
            "Trust and source blockers are visible before any stakeholder claim.",
        ],
        "required_artifacts": [
            "scripts/monthly_packet.py",
            "scripts/decision_policy_review.py",
            "scripts/reasoning_stress_review.py",
            "scripts/normalization_crosswalk_review.py",
            "scripts/save_review_snapshot.py",
        ],
        "exit_criteria": [
            "Each active decision has an operating policy outcome.",
            "Approved actions identify owner, next trigger, and known limits.",
            "Review snapshot is saved after council decisions are recorded.",
            "Stakeholder-facing claims remain bounded by trust posture.",
        ],
        "decision_rights": [
            "Approve, revise, monitor, wait, escalate, or archive decisions.",
            "Assign release and evidence owners.",
            "Set next review triggers.",
            "Authorize internal stakeholder language within known limits.",
        ],
        "escalation_triggers": [
            "Decision stays in wait or monitor state past its review trigger.",
            "Suppressed evidence is being used as stakeholder proof.",
            "Dashboard or packet language conflicts with decision policy.",
        ],
        "deferred_work": [
            "Automated approvals",
            "Downstream LMS, CRM, ATS, or delivery-tool writes",
            "External proof claims",
            "Schema changes based only on council discussion",
        ],
        "manual_readiness": "ready_for_manual_trial",
    },
    {
        "cadence_id": "quarterly_recalibration",
        "cadence": "quarterly",
        "label": "Quarterly role, competency, and horizon recalibration",
        "owner": "Signal Intelligence Council",
        "participants": ["Council", "Research", "Learning", "Assessment Ops", "Matching and CSM", "Delivery", "Data and Analytics"],
        "purpose": "Review role anchors, competency clusters, horizon predictions, outcome evidence, and structural programme changes.",
        "entry_criteria": [
            "At least one monthly council cycle has completed with saved snapshots.",
            "Prediction scoring and horizon review notes are available.",
            "Normalization crosswalk identifies stable and unstable role/competency links.",
            "Outcome and learner evidence limitations are explicitly named.",
        ],
        "required_artifacts": [
            "scripts/report_kpis.py",
            "scripts/normalization_crosswalk_review.py",
            "scripts/proficiency_readiness_review.py",
            "scripts/outcome_review.py",
            "scripts/reasoning_stress_review.py",
        ],
        "exit_criteria": [
            "Role or competency changes are classified as keep, revise, monitor, or deprecate.",
            "Prediction learning is recorded for horizon claims that matured.",
            "Pilot extract priorities are updated without committing to production schemas.",
            "Quarterly structural changes have named owners and evidence requirements.",
        ],
        "decision_rights": [
            "Recommend role-anchor and competency adjustments.",
            "Prioritize pilot extracts for the next operating cycle.",
            "Deprecate monitor-only capabilities from standalone credential consideration.",
            "Set quarterly evidence and prediction-learning priorities.",
        ],
        "escalation_triggers": [
            "A capability remains monitor-only across multiple cycles but appears in stakeholder claims.",
            "Prediction accuracy review contradicts current horizon posture.",
            "Outcome evidence remains blocked after repeated monthly escalations.",
        ],
        "deferred_work": [
            "Final ontology schema",
            "Warehouse semantic model",
            "Model training or scoring weights",
            "Automated quarterly recalibration jobs",
        ],
        "manual_readiness": "defined_not_trialed",
    },
)


READINESS_LABELS = {
    "ready_for_manual_trial": "Ready for manual trial",
    "defined_not_trialed": "Defined but not trialed",
}


def build_governance_cadence_review() -> dict[str, Any]:
    """Return manual governance cadence definitions before automation."""
    cadences = [dict(item) for item in CADENCE_REVIEWS]
    cadence_counts = Counter(item["cadence"] for item in cadences)
    readiness_counts = Counter(item["manual_readiness"] for item in cadences)
    return {
        "generated_date": TODAY.isoformat(),
        "purpose": (
            "Define the weekly, monthly, and quarterly human operating cadence before scheduled "
            "jobs, production automation, or downstream writes are introduced."
        ),
        "summary": {
            "cadence_count": len(cadences),
            "weekly_count": cadence_counts["weekly"],
            "monthly_count": cadence_counts["monthly"],
            "quarterly_count": cadence_counts["quarterly"],
            "ready_for_manual_trial_count": readiness_counts["ready_for_manual_trial"],
            "defined_not_trialed_count": readiness_counts["defined_not_trialed"],
            "automated_scheduling": "deferred",
            "production_jobs": "deferred",
        },
        "guardrails": [
            "Human review cadence must prove which decisions matter before scheduling jobs.",
            "Weekly review can classify and escalate signals, but cannot approve curriculum or credential changes.",
            "Monthly council review can decide operating posture, but cannot automate downstream writes.",
            "Quarterly recalibration can recommend structural changes, but final ontology/schema work stays deferred.",
            "Every cadence needs entry criteria, exit criteria, artifacts, decision rights, and escalation triggers.",
        ],
        "cadences": cadences,
    }


def render_governance_cadence_text(review: dict[str, Any]) -> str:
    summary = review["summary"]
    lines = [
        "Governance Cadence Review",
        "=========================",
        "",
        f"Generated: {review['generated_date']}",
        "",
        review["purpose"],
        "",
        "Summary",
        "-------",
        (
            f"- cadences={summary['cadence_count']} weekly={summary['weekly_count']} "
            f"monthly={summary['monthly_count']} quarterly={summary['quarterly_count']}"
        ),
        (
            f"- ready_for_manual_trial={summary['ready_for_manual_trial_count']} "
            f"defined_not_trialed={summary['defined_not_trialed_count']}"
        ),
        f"- automated_scheduling={summary['automated_scheduling']}",
        f"- production_jobs={summary['production_jobs']}",
        "",
        "Guardrails",
        "----------",
    ]
    lines.extend(f"- {guardrail}" for guardrail in review["guardrails"])
    lines.extend(["", "Cadences", "--------"])
    for cadence in review["cadences"]:
        lines.extend(
            [
                f"- [{cadence['manual_readiness']}] {cadence['label']} ({cadence['cadence']})",
                f"  owner: {cadence['owner']}",
                f"  participants: {', '.join(cadence['participants'])}",
                f"  purpose: {cadence['purpose']}",
                f"  entry: {'; '.join(cadence['entry_criteria'])}",
                f"  artifacts: {', '.join(cadence['required_artifacts'])}",
                f"  exit: {'; '.join(cadence['exit_criteria'])}",
                f"  rights: {'; '.join(cadence['decision_rights'])}",
                f"  escalate: {'; '.join(cadence['escalation_triggers'])}",
                f"  defer: {'; '.join(cadence['deferred_work'])}",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"
