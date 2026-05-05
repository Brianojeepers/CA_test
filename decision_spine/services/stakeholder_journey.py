"""Map stakeholder journeys across evidence, trust, decisions, and activation."""

from __future__ import annotations

from collections import Counter
from typing import Any

from decision_spine.services.trust_registry import build_trust_registry


JOURNEY_DEFINITIONS: tuple[dict[str, Any], ...] = (
    {
        "stakeholder_id": "council",
        "label": "Signal Intelligence Council",
        "primary_question": "Which signals, decisions, and follow-ups need attention this review cycle?",
        "decision_moment": "Monthly council review and exception handling.",
        "surface_ids": ["monthly_packet", "dashboard_prototype", "decision_impact_review"],
        "can_do_now": "Run the meeting around exceptions, blockers, and directional decision posture.",
        "must_defer": "Do not treat placement, retention, or learner-readiness evidence as production proof.",
        "escalation_path": "Escalate red source blockers to the named privacy owner and unresolved decision ownership to the council chair.",
        "evidence_needed": "Privacy-cleared cohort outcomes, aggregate learner evidence, and confirmed decision-register ownership.",
    },
    {
        "stakeholder_id": "learning",
        "label": "Learning",
        "primary_question": "Which curriculum changes are worth planning, revising, or holding?",
        "decision_moment": "Curriculum planning and release follow-up.",
        "surface_ids": ["stakeholder_briefs", "dashboard_prototype", "decision_impact_review", "v02_intelligence_preview"],
        "can_do_now": "Plan curriculum responses to validated signals and identify where evidence is still immature.",
        "must_defer": "Do not claim a curriculum change improved placement until outcome evidence clears privacy and maturity gates.",
        "escalation_path": "Escalate learner-evidence blockers to Assessment Ops and Talent Data Privacy; escalate release ambiguity to Academy Operations.",
        "evidence_needed": "Released-change evidence, pedagogy links, aggregate readiness evidence, and post-change outcome maturity.",
    },
    {
        "stakeholder_id": "assessment_ops",
        "label": "Assessment Ops",
        "primary_question": "Which credential or assessment changes need stronger proof before standards move?",
        "decision_moment": "Assessment threshold review and credential integrity checks.",
        "surface_ids": ["stakeholder_briefs", "decision_impact_review", "v02_intelligence_preview", "pilot_intake_review"],
        "can_do_now": "Identify readiness risks, privacy blockers, and assessment evidence requirements for planned changes.",
        "must_defer": "Do not store learner-derived real extracts or update high-stakes thresholds from synthetic evidence.",
        "escalation_path": "Escalate suppression and learner-evidence approvals to Talent Data Privacy.",
        "evidence_needed": "Approved aggregate suppression rules, rubric threshold normalization, and pilot-safe proficiency evidence.",
    },
    {
        "stakeholder_id": "matching_csm",
        "label": "Matching and CSM",
        "primary_question": "Which changes can inform matching narratives, and which still need outcome proof?",
        "decision_moment": "Placement narrative review and post-placement follow-up.",
        "surface_ids": ["stakeholder_briefs", "monthly_packet", "decision_impact_review"],
        "can_do_now": "Use directional evidence to flag likely positioning opportunities and outcome gaps.",
        "must_defer": "Do not update client-facing placement claims until cohort outcome data clears privacy review.",
        "escalation_path": "Escalate cohort outcome blockers to Matching Operations and Talent Data Privacy.",
        "evidence_needed": "Privacy-cleared placement, retention, extension, and client satisfaction aggregates.",
    },
    {
        "stakeholder_id": "solutions_sales",
        "label": "Solutions and Sales",
        "primary_question": "Which market-backed capabilities can support client conversations safely?",
        "decision_moment": "Client positioning and offer narrative preparation.",
        "surface_ids": ["stakeholder_briefs", "dashboard_prototype", "monthly_packet"],
        "can_do_now": "Use approved directional language and known limits to prepare non-overstated narratives.",
        "must_defer": "Do not cite raw client demand, account-level commercial evidence, or unapproved outcome claims.",
        "escalation_path": "Escalate commercial-source ambiguity to Research and Commercial Operations.",
        "evidence_needed": "Approved market-signal summaries, safe commercial aggregation, and outcome evidence fit for external use.",
    },
    {
        "stakeholder_id": "data_analytics",
        "label": "Data and Analytics",
        "primary_question": "Where is evidence trustworthy enough, and where are source contracts still blocking progress?",
        "decision_moment": "Source-quality review and field-readiness planning.",
        "surface_ids": ["schema_gap_workbench", "pilot_request_pack", "pilot_intake_review"],
        "can_do_now": "Coordinate source-owner clarification, privacy blockers, and minimum viable pilot fields.",
        "must_defer": "Do not create database schemas or warehouse models until horizontal trust and field ownership are coherent.",
        "escalation_path": "Escalate red source contracts to privacy owners and unresolved field ownership to the council chair.",
        "evidence_needed": "Accepted source-owner intake, privacy-cleared sample rows, and agreed freshness obligations.",
    },
    {
        "stakeholder_id": "delivery",
        "label": "Delivery",
        "primary_question": "Which approved changes can be sequenced without disrupting active cohorts?",
        "decision_moment": "Cohort delivery planning and release timing review.",
        "surface_ids": ["stakeholder_briefs", "dashboard_prototype", "decision_impact_review"],
        "can_do_now": "Review release timing risk and flag where cohort-calendar confidence is missing.",
        "must_defer": "Do not automate delivery schedules or assume real cohort timing confidence from seed data.",
        "escalation_path": "Escalate release-state ambiguity to Academy Operations and cohort-calendar gaps to Delivery leadership.",
        "evidence_needed": "Confirmed cohort calendar data, release windows, and delivery capacity estimates.",
    },
    {
        "stakeholder_id": "market_intelligence",
        "label": "Market Intelligence and Research",
        "primary_question": "Which demand, horizon, and weak-signal claims are ready for controlled review?",
        "decision_moment": "Signal refresh, horizon scoring, and v0.2 intelligence planning.",
        "surface_ids": ["v02_intelligence_preview", "schema_gap_workbench", "pilot_request_pack"],
        "can_do_now": "Stress-test role demand, horizon, and weak-signal assumptions with explicit missing-field labels.",
        "must_defer": "Do not publish scores, model weights, or hard recommendations until pilot evidence is approved.",
        "escalation_path": "Escalate source-owner gaps to Research and council-owned maturity definitions to the council chair.",
        "evidence_needed": "Approved demand summaries, horizon maturity definitions, and calibrated scoring examples.",
    },
    {
        "stakeholder_id": "source_owners",
        "label": "Source Owners",
        "primary_question": "What do I need to clarify before my source can support the pilot?",
        "decision_moment": "Source-owner response and pilot extract readiness review.",
        "surface_ids": ["pilot_request_pack", "pilot_intake_review", "schema_gap_workbench"],
        "can_do_now": "Respond to field requests, clarify grain and freshness, and identify privacy constraints.",
        "must_defer": "Do not send real extracts until privacy posture, storage, and sample rules are approved.",
        "escalation_path": "Escalate privacy uncertainty to the named privacy owner and unresolved field need to Data and Analytics.",
        "evidence_needed": "Owner-confirmed field definitions, sample availability, privacy decision, and freshness SLA.",
    },
    {
        "stakeholder_id": "executive",
        "label": "Executive stakeholders",
        "primary_question": "What changed, why did it change, and how confident should we be?",
        "decision_moment": "Executive review, strategic narrative, and investment prioritization.",
        "surface_ids": ["monthly_packet", "stakeholder_briefs", "decision_impact_review"],
        "can_do_now": "Review the operating narrative, known limits, and decision accountability without overstating evidence.",
        "must_defer": "Do not make performance claims or scale decisions from low-confidence synthetic evidence.",
        "escalation_path": "Escalate unresolved operating risk to the council chair and red source blockers to privacy owners.",
        "evidence_needed": "Decision-grade source posture, mature outcome windows, and confirmed signal-to-release traceability.",
    },
)


MODE_LABELS = {
    "workflow_design_only": "Workflow design only",
    "planning_ready": "Planning ready",
    "controlled_manual_review": "Controlled manual review",
    "pilot_candidate": "Pilot candidate",
    "unmapped": "Unmapped",
}


def journey_mode(surface_statuses: list[str]) -> str:
    if not surface_statuses or "unmapped" in surface_statuses:
        return "unmapped"
    if "privacy_blocked" in surface_statuses:
        return "workflow_design_only"
    if "manual_sampling_only" in surface_statuses:
        return "controlled_manual_review"
    if all(status == "planning_ready" for status in surface_statuses):
        return "planning_ready"
    return "pilot_candidate"


def build_stakeholder_journey_map(trust_registry: dict[str, Any] | None = None) -> dict[str, Any]:
    trust_registry = trust_registry or build_trust_registry()
    surfaces_by_id = {surface["surface_id"]: surface for surface in trust_registry["surfaces"]}
    journeys: list[dict[str, Any]] = []

    for definition in JOURNEY_DEFINITIONS:
        surface_records = [surfaces_by_id[surface_id] for surface_id in definition["surface_ids"]]
        statuses = [surface["trust_status"] for surface in surface_records]
        mode = journey_mode(statuses)
        journeys.append(
            {
                "stakeholder_id": definition["stakeholder_id"],
                "label": definition["label"],
                "primary_question": definition["primary_question"],
                "decision_moment": definition["decision_moment"],
                "current_mode": mode,
                "mode_label": MODE_LABELS[mode],
                "surfaces": [
                    {
                        "surface_id": surface["surface_id"],
                        "label": surface["label"],
                        "trust_status": surface["trust_status"],
                        "stakeholder_confidence": surface["stakeholder_confidence"],
                    }
                    for surface in surface_records
                ],
                "trust_statuses": sorted(set(statuses)),
                "can_do_now": definition["can_do_now"],
                "must_defer": definition["must_defer"],
                "escalation_path": definition["escalation_path"],
                "evidence_needed": definition["evidence_needed"],
            }
        )

    counts = Counter(journey["current_mode"] for journey in journeys)
    return {
        "generated_date": trust_registry["generated_date"],
        "purpose": (
            "Show how each stakeholder should move from evidence surfaces to action, "
            "using the current trust posture to separate safe next steps from deferred claims."
        ),
        "summary": {
            "journey_count": len(journeys),
            "workflow_design_only_count": counts["workflow_design_only"],
            "planning_ready_count": counts["planning_ready"],
            "controlled_manual_review_count": counts["controlled_manual_review"],
            "pilot_candidate_count": counts["pilot_candidate"],
            "unmapped_count": counts["unmapped"],
        },
        "guardrails": [
            "A stakeholder journey can be useful even when evidence surfaces are not decision-grade.",
            "Privacy-blocked journeys should produce planning actions, not performance claims.",
            "Planning-ready journeys can clarify ownership, grain, and next evidence needs before schema work.",
            "Escalation paths should identify the operating owner who can remove the blocker.",
        ],
        "journeys": journeys,
        "next_horizontal_slices": [
            "Decision policy checks for wait, revise, escalate, or archive",
            "Cross-layer reasoning stress tests before schema commitments",
            "Source freshness and owner-obligation review",
        ],
    }


def render_stakeholder_journey_text(journey_map: dict[str, Any]) -> str:
    summary = journey_map["summary"]
    lines = [
        "Stakeholder Journey Map",
        "=======================",
        "",
        f"Generated: {journey_map['generated_date']}",
        "",
        journey_map["purpose"],
        "",
        "Summary",
        "-------",
        (
            f"- journeys={summary['journey_count']} workflow_design_only={summary['workflow_design_only_count']} "
            f"planning_ready={summary['planning_ready_count']} controlled_manual_review={summary['controlled_manual_review_count']} "
            f"pilot_candidate={summary['pilot_candidate_count']} unmapped={summary['unmapped_count']}"
        ),
        "",
        "Guardrails",
        "----------",
    ]
    lines.extend(f"- {guardrail}" for guardrail in journey_map["guardrails"])
    lines.extend(["", "Journeys", "--------"])

    for journey in journey_map["journeys"]:
        surfaces = ", ".join(
            f"{surface['label']} [{surface['trust_status']}]"
            for surface in journey["surfaces"]
        )
        lines.extend(
            [
                f"- [{journey['current_mode']}] {journey['label']}",
                f"  question: {journey['primary_question']}",
                f"  decision_moment: {journey['decision_moment']}",
                f"  surfaces: {surfaces}",
                f"  can_do_now: {journey['can_do_now']}",
                f"  defer: {journey['must_defer']}",
                f"  escalate: {journey['escalation_path']}",
                f"  evidence_needed: {journey['evidence_needed']}",
            ]
        )

    lines.extend(["", "Next Horizontal Slices", "----------------------"])
    lines.extend(f"- {item}" for item in journey_map["next_horizontal_slices"])
    return "\n".join(lines).rstrip() + "\n"
