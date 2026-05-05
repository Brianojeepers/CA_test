"""Cross-layer reasoning stress tests for the Decision Spine MVP."""

from __future__ import annotations

from collections import Counter
from typing import Any

from decision_spine.services.architecture_readiness import build_architecture_readiness_review
from decision_spine.services.decision_policy import build_decision_policy_review
from decision_spine.services.source_ingestion import build_source_ingestion_review
from decision_spine.services.stakeholder_journey import build_stakeholder_journey_map
from decision_spine.services.trust_registry import build_trust_registry


STRESS_SCENARIOS: tuple[dict[str, str], ...] = (
    {
        "scenario_id": "RS-001",
        "title": "Strong market signal with blocked learner and outcome evidence",
        "claim_pressure": "Act on a strong role-demand signal and imply placement or readiness impact.",
        "layers_tested": "signal_ingestion, intelligence, observability_trust, stakeholder_experience",
        "primary_surface": "v02_intelligence_preview",
        "required_downgrade": "monitor",
        "unsafe_claim": "This signal proves learners are ready or that placement outcomes improved.",
        "safe_response": "Keep the signal in directional review until learner evidence and cohort outcomes clear privacy gates.",
    },
    {
        "scenario_id": "RS-002",
        "title": "Approved decision with blocked or incomplete release path",
        "claim_pressure": "Treat an approved decision as implemented operating change.",
        "layers_tested": "decision, activation, governance_cadence",
        "primary_decision": "DEC-2026-004",
        "required_downgrade": "revise",
        "unsafe_claim": "The decision is working because approval exists.",
        "safe_response": "Revise the release path and hold impact claims until implementation evidence exists.",
    },
    {
        "scenario_id": "RS-003",
        "title": "Green prediction register with amber market source",
        "claim_pressure": "Use a pilot-ready prediction register to publish a hard horizon recommendation.",
        "layers_tested": "signal_ingestion, intelligence, governance_cadence",
        "primary_source": "SRC-2026-005",
        "required_downgrade": "controlled_pilot_only",
        "unsafe_claim": "Prediction readiness makes the underlying market demand source production-ready.",
        "safe_response": "Run controlled prediction review while keeping market-signal ingestion manual-contracting only.",
    },
    {
        "scenario_id": "RS-004",
        "title": "External stakeholder asks for a client-facing proof claim",
        "claim_pressure": "Turn dashboard or brief language into external sales proof.",
        "layers_tested": "stakeholder_experience, observability_trust, activation",
        "primary_journey": "solutions_sales",
        "required_downgrade": "internal_directional_only",
        "unsafe_claim": "Client-facing claims can cite raw demand or unapproved outcome evidence.",
        "safe_response": "Use approved directional language only and escalate commercial-source ambiguity.",
    },
    {
        "scenario_id": "RS-005",
        "title": "Dashboard action tries to bypass decision policy",
        "claim_pressure": "Promote a selected decision directly to action from an insight card.",
        "layers_tested": "stakeholder_experience, decision, governance_cadence",
        "primary_decision": "DEC-2026-005",
        "required_downgrade": "escalate",
        "unsafe_claim": "A visible dashboard action can override negative evidence or suppressed samples.",
        "safe_response": "Route visible risk to an owner-level escalation and block amplification.",
    },
)


def _source_by_id(source_review: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {source["contract_id"]: source for source in source_review["sources"]}


def _journey_by_id(journey_map: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {journey["stakeholder_id"]: journey for journey in journey_map["journeys"]}


def _policy_by_decision(policy_review: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {row["decision_id"]: row for row in policy_review["policy_rows"]}


def evaluate_scenario(
    scenario: dict[str, str],
    *,
    source_review: dict[str, Any],
    trust_registry: dict[str, Any],
    journey_map: dict[str, Any],
    policy_review: dict[str, Any],
) -> dict[str, Any]:
    sources = _source_by_id(source_review)
    journeys = _journey_by_id(journey_map)
    policies = _policy_by_decision(policy_review)
    surfaces = {surface["surface_id"]: surface for surface in trust_registry["surfaces"]}
    scenario_id = scenario["scenario_id"]

    if scenario_id == "RS-001":
        passed = (
            surfaces["v02_intelligence_preview"]["trust_status"] == "privacy_blocked"
            and sources["SRC-2026-004"]["allowed_use"] == "planning_only"
            and sources["SRC-2026-007"]["allowed_use"] == "planning_only"
        )
        evidence = [
            "v0.2 intelligence preview is privacy-blocked",
            "cohort outcomes are planning-only",
            "learner evidence is planning-only",
        ]
    elif scenario_id == "RS-002":
        passed = policies["DEC-2026-004"]["policy_outcome"] == "revise"
        evidence = [
            "DEC-2026-004 policy outcome is revise",
            policies["DEC-2026-004"]["escalation_trigger"],
        ]
    elif scenario_id == "RS-003":
        passed = (
            sources["SRC-2026-005"]["ingestion_status"] == "pilot_candidate"
            and sources["SRC-2026-001"]["ingestion_status"] == "manual_contracting"
        )
        evidence = [
            "prediction register is pilot-candidate",
            "market signals remain manual-contracting",
        ]
    elif scenario_id == "RS-004":
        passed = (
            journeys["solutions_sales"]["current_mode"] == "workflow_design_only"
            and "privacy_blocked" in journeys["solutions_sales"]["trust_statuses"]
        )
        evidence = [
            "Solutions and Sales journey is workflow-design-only",
            "journey inherits privacy-blocked evidence surfaces",
        ]
    elif scenario_id == "RS-005":
        passed = policies["DEC-2026-005"]["policy_outcome"] == "escalate"
        evidence = [
            "DEC-2026-005 policy outcome is escalate",
            policies["DEC-2026-005"]["escalation_trigger"],
        ]
    else:
        raise ValueError(f"Unknown scenario_id: {scenario_id}")

    return {
        **scenario,
        "result": "pass" if passed else "fail",
        "unsafe_claim_blocked": passed,
        "evidence": evidence,
    }


def build_reasoning_stress_review(
    *,
    architecture_review: dict[str, Any] | None = None,
    source_review: dict[str, Any] | None = None,
    trust_registry: dict[str, Any] | None = None,
    journey_map: dict[str, Any] | None = None,
    policy_review: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return cross-layer stress scenarios and downgrade outcomes."""
    architecture_review = architecture_review or build_architecture_readiness_review()
    source_review = source_review or build_source_ingestion_review()
    trust_registry = trust_registry or build_trust_registry()
    journey_map = journey_map or build_stakeholder_journey_map(trust_registry)
    policy_review = policy_review or build_decision_policy_review(journey_map=journey_map)

    scenarios = [
        evaluate_scenario(
            scenario,
            source_review=source_review,
            trust_registry=trust_registry,
            journey_map=journey_map,
            policy_review=policy_review,
        )
        for scenario in STRESS_SCENARIOS
    ]
    result_counts = Counter(scenario["result"] for scenario in scenarios)
    return {
        "generated_date": source_review["generated_date"],
        "purpose": (
            "Stress-test cross-layer reasoning before database schemas by forcing the MVP to "
            "downgrade unsafe claims when evidence, trust, ingestion, policy, or stakeholder posture conflicts."
        ),
        "summary": {
            "scenario_count": len(scenarios),
            "pass_count": result_counts["pass"],
            "fail_count": result_counts["fail"],
            "unsafe_claims_blocked_count": sum(1 for scenario in scenarios if scenario["unsafe_claim_blocked"]),
            "architecture_posture": architecture_review["summary"]["recommended_posture"],
            "database_schema_work": architecture_review["summary"]["database_schema_work"],
        },
        "guardrails": [
            "A strong signal cannot override red learner or outcome source blockers.",
            "Approval is not implementation proof; release and evidence posture still govern action.",
            "A green source in one domain cannot make another source production-ready.",
            "External-facing claims require stronger trust posture than internal planning work.",
            "Dashboard actions must obey decision policy outcomes.",
        ],
        "scenarios": scenarios,
        "next_horizontal_slices": [
            "Controlled pilot extract rehearsal once source blockers clear",
            "Dashboard placement for decision policy and stress-test downgrades",
            "Schema decisions only after stress scenarios keep passing with pilot evidence",
        ],
    }


def render_reasoning_stress_text(review: dict[str, Any]) -> str:
    summary = review["summary"]
    lines = [
        "Reasoning Stress Test Review",
        "============================",
        "",
        f"Generated: {review['generated_date']}",
        "",
        review["purpose"],
        "",
        "Summary",
        "-------",
        (
            f"- scenarios={summary['scenario_count']} pass={summary['pass_count']} "
            f"fail={summary['fail_count']} unsafe_claims_blocked={summary['unsafe_claims_blocked_count']}"
        ),
        f"- architecture_posture={summary['architecture_posture']}",
        f"- database_schema_work={summary['database_schema_work']}",
        "",
        "Guardrails",
        "----------",
    ]
    lines.extend(f"- {guardrail}" for guardrail in review["guardrails"])
    lines.extend(["", "Scenarios", "---------"])
    for scenario in review["scenarios"]:
        evidence = "; ".join(scenario["evidence"])
        lines.extend(
            [
                f"- [{scenario['result']}] {scenario['scenario_id']} {scenario['title']}",
                f"  pressure: {scenario['claim_pressure']}",
                f"  layers: {scenario['layers_tested']}",
                f"  unsafe: {scenario['unsafe_claim']}",
                f"  downgrade: {scenario['required_downgrade']}",
                f"  safe: {scenario['safe_response']}",
                f"  evidence: {evidence}",
            ]
        )
    lines.extend(["", "Next Horizontal Slices", "----------------------"])
    lines.extend(f"- {item}" for item in review["next_horizontal_slices"])
    return "\n".join(lines).rstrip() + "\n"
