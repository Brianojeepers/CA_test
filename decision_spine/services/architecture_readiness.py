"""Map current MVP coverage across the target intelligence architecture."""

from __future__ import annotations

from collections import Counter
from typing import Any


ARCHITECTURE_LAYERS: tuple[dict[str, Any], ...] = (
    {
        "layer": "signal_ingestion",
        "label": "Signal ingestion layer",
        "target_state": "Bring market, client, learner, outcome, compensation, and tooling signals into a governed refresh loop.",
        "current_coverage": "Synthetic signals, source contracts, ingestion-envelope review, pilot templates, and owner request packs exist; live pulls are intentionally absent.",
        "current_assets": [
            "data/signals.json",
            "data/source_contracts.json",
            "data/pilot_extract_templates/",
            "scripts/source_contract_review.py",
            "scripts/source_ingestion_review.py",
            "scripts/export_pilot_request_pack.py",
            "scripts/pilot_intake_review.py",
            "docs/source_ingestion_contract.md",
        ],
        "readiness": "partial",
        "stakeholder_value": "Source owners can see exactly what evidence is being requested before any production ingestion work begins.",
        "horizontal_next_step": "Rehearse controlled pilot extracts once source blockers clear.",
        "defer_vertical_work": "Do not build scheduled ingestion, warehouse landing tables, or source-specific pipelines yet.",
    },
    {
        "layer": "normalization",
        "label": "Normalization layer",
        "target_state": "Standardize roles, competencies, skills, horizons, confidence, privacy posture, and source provenance.",
        "current_coverage": "Role competencies, pedagogy framing, source contracts, v0.2 field requirements, and a crosswalk review provide early normalization anchors.",
        "current_assets": [
            "data/role_competencies.json",
            "data/pedagogy_map.json",
            "data/v02_intelligence_requirements.json",
            "scripts/competency_gap_review.py",
            "scripts/normalization_crosswalk_review.py",
            "scripts/pedagogy_review.py",
            "scripts/schema_gap_review.py",
            "docs/normalization_crosswalk.md",
        ],
        "readiness": "partial",
        "stakeholder_value": "Learning, Assessment Ops, and Data can discuss the same roles and competencies without assuming a final ontology.",
        "horizontal_next_step": "Use crosswalk gaps to shape controlled pilot extracts before ontology/schema work.",
        "defer_vertical_work": "Do not lock a canonical ontology table or warehouse semantic model until source terms and stakeholder language stabilize.",
    },
    {
        "layer": "intelligence",
        "label": "Intelligence layer",
        "target_state": "Score role demand, competency gaps, horizon maturity, and curriculum impact with explicit confidence and guardrails.",
        "current_coverage": "Directional v0.2 previews and schema gaps exist; hard recommendations remain disabled by design.",
        "current_assets": [
            "scripts/v02_intelligence_preview.py",
            "scripts/reasoning_stress_review.py",
            "scripts/schema_gap_review.py",
            "data/v02_intelligence_requirements.json",
            "docs/v02_pilot_schema.md",
            "docs/reasoning_stress_tests.md",
        ],
        "readiness": "partial",
        "stakeholder_value": "Stakeholders can inspect what the engine would reason about without mistaking synthetic data for production truth.",
        "horizontal_next_step": "Use stress-test failures to define the narrowest pilot extract rehearsal.",
        "defer_vertical_work": "Do not train models, tune weights, or publish scoring contracts before pilot evidence and confidence rules are accepted.",
    },
    {
        "layer": "decision",
        "label": "Decision layer",
        "target_state": "Convert evidence into governed curriculum, credential, assessment, positioning, and profile decisions.",
        "current_coverage": "Decision logs, council queues, changelogs, impact reviews, and decision-detail joins are already working locally.",
        "current_assets": [
            "data/decisions.json",
            "scripts/council_review.py",
            "scripts/decision_impact_review.py",
            "scripts/decision_policy_review.py",
            "scripts/reasoning_stress_review.py",
            "scripts/decision_changelog.py",
            "docs/decision_policy.md",
            "docs/reasoning_stress_tests.md",
            "app/api/main.py",
        ],
        "readiness": "covered",
        "stakeholder_value": "The council can trace why a decision exists, what changed, and whether evidence is emerging.",
        "horizontal_next_step": "Place policy and stress-test downgrades into the dashboard once the review language stabilizes.",
        "defer_vertical_work": "Do not automate approvals or downstream writes until decision rights and exception rules are tested in council review.",
    },
    {
        "layer": "activation",
        "label": "Activation layer",
        "target_state": "Translate decisions into curriculum maps, assessments, matcher playbooks, talent profiles, and stakeholder briefs.",
        "current_coverage": "Stakeholder packet exports, dashboard lenses, journey mapping, credential actions, learner evidence reviews, and talent/profile scripts exist.",
        "current_assets": [
            "scripts/export_stakeholder_packets.py",
            "scripts/stakeholder_journey_review.py",
            "scripts/credential_requirements.py",
            "scripts/learning_outcomes.py",
            "scripts/talent_profile_signals.py",
            "scripts/training_offer_inputs.py",
            "docs/stakeholder_journey_map.md",
            "web/",
        ],
        "readiness": "partial",
        "stakeholder_value": "Different teams can consume the same decision spine through their own work lens.",
        "horizontal_next_step": "Rehearse controlled pilot extracts once source blockers clear.",
        "defer_vertical_work": "Do not integrate with LMS, CRM, ATS, or delivery tools until stakeholder workflows are stable.",
    },
    {
        "layer": "governance_cadence",
        "label": "Governance cadence layer",
        "target_state": "Run weekly refresh, monthly council review, quarterly recalibration, and documented source-quality governance.",
        "current_coverage": "Council charter, monthly packet, review snapshots, data rules, and validation-first checks are in place.",
        "current_assets": [
            "docs/signal_intelligence_council.md",
            "scripts/monthly_packet.py",
            "scripts/save_review_snapshot.py",
            "scripts/run_checks.py",
            "data/README.md",
        ],
        "readiness": "partial",
        "stakeholder_value": "The MVP has an operating rhythm, not just isolated analytics outputs.",
        "horizontal_next_step": "Define agenda templates for weekly, monthly, and quarterly reviews with explicit entry and exit criteria.",
        "defer_vertical_work": "Do not schedule automated production jobs until the human cadence proves which reviews actually matter.",
    },
    {
        "layer": "observability_trust",
        "label": "Observability and trust layer",
        "target_state": "Track validation, freshness, provenance, privacy, confidence, warnings, and generated-output integrity.",
        "current_coverage": "Validation, unit tests, frontend checks, dashboard smoke tests, privacy gates, known warnings, source ingestion posture, and surface-level trust posture are documented.",
        "current_assets": [
            "scripts/validate_data.py",
            "scripts/check_frontend.py",
            "scripts/check_dashboard.py",
            "scripts/run_checks.py",
            "scripts/trust_registry_review.py",
            "scripts/source_ingestion_review.py",
            "scripts/reasoning_stress_review.py",
            "docs/real_data_readiness.md",
            "docs/source_data_contracts.md",
            "docs/trust_registry.md",
            "docs/source_ingestion_contract.md",
            "docs/reasoning_stress_tests.md",
        ],
        "readiness": "partial",
        "stakeholder_value": "Stakeholders can see what is trustworthy, directional, blocked, or intentionally synthetic.",
        "horizontal_next_step": "Expose stress-test downgrades as stakeholder-visible trust signals.",
        "defer_vertical_work": "Do not add production observability tooling before the MVP defines the trust signals users need to see.",
    },
    {
        "layer": "stakeholder_experience",
        "label": "Stakeholder experience layer",
        "target_state": "Provide intuitive, drillable, role-specific views that make evidence, actions, and limits easy to inspect.",
        "current_coverage": "The static dashboard, Markdown packets, trust registry, and journey map provide the first stakeholder-facing surfaces, but workflow depth is still narrow.",
        "current_assets": [
            "web/index.html",
            "web/render/",
            "scripts/export_monthly_packet.py",
            "scripts/export_stakeholder_packets.py",
            "scripts/stakeholder_journey_review.py",
            "outputs/",
        ],
        "readiness": "partial",
        "stakeholder_value": "The MVP is moving from technical packet output toward usable decision support.",
        "horizontal_next_step": "Broaden the dashboard from monthly packet review into architecture-wide navigation: signals, trust, decisions, activation, and learning.",
        "defer_vertical_work": "Do not optimize one dashboard module deeply until the full stakeholder journey is represented at a useful level.",
    },
)


READINESS_LABELS = {
    "covered": "Covered for local MVP",
    "partial": "Partially covered",
    "thin": "Thin early coverage",
    "missing": "Missing",
}


def build_architecture_readiness_review() -> dict[str, Any]:
    """Return horizontal architecture coverage without proposing database work."""
    layers = [dict(layer) for layer in ARCHITECTURE_LAYERS]
    counts = Counter(layer["readiness"] for layer in layers)
    return {
        "purpose": (
            "Rate the current MVP horizontally across the target intelligence architecture "
            "before going deeper into database schemas or production infrastructure."
        ),
        "summary": {
            "layer_count": len(layers),
            "covered_count": counts["covered"],
            "partial_count": counts["partial"],
            "thin_count": counts["thin"],
            "missing_count": counts["missing"],
            "database_schema_work": "deferred",
            "recommended_posture": "expand horizontally before going vertically",
        },
        "rating": {
            "score": 9,
            "out_of": 10,
            "rationale": (
                "The MVP is strong as a decision spine, but it is still too narrow to represent "
                "the full intelligence engine. Broadening layer coverage now is the right move."
            ),
        },
        "guardrails": [
            "Keep real-data, database, and warehouse work deferred until horizontal coverage is coherent.",
            "Prefer read-only reviews and stakeholder workflow surfaces over persistence commitments.",
            "Each new slice should clarify source, trust, decision, activation, or governance behavior across the architecture.",
            "Directional intelligence outputs must keep explicit limits until pilot data passes privacy, ownership, and freshness gates.",
        ],
        "layers": layers,
        "next_horizontal_slices": [
            "Controlled pilot extract rehearsal once source blockers clear",
            "Dashboard placement for decision policy and stress-test downgrades",
            "Governance cadence templates with weekly, monthly, and quarterly entry and exit criteria",
        ],
    }


def render_architecture_readiness_text(review: dict[str, Any]) -> str:
    summary = review["summary"]
    rating = review["rating"]
    lines = [
        "Architecture Readiness Review",
        "=============================",
        "",
        review["purpose"],
        "",
        "Rating",
        "------",
        f"- horizontal_strategy_rating={rating['score']}/{rating['out_of']}",
        f"- rationale: {rating['rationale']}",
        "",
        "Summary",
        "-------",
        (
            f"- layers={summary['layer_count']} covered={summary['covered_count']} "
            f"partial={summary['partial_count']} thin={summary['thin_count']} missing={summary['missing_count']}"
        ),
        f"- database_schema_work={summary['database_schema_work']}",
        f"- recommended_posture={summary['recommended_posture']}",
        "",
        "Guardrails",
        "----------",
    ]
    lines.extend(f"- {guardrail}" for guardrail in review["guardrails"])
    lines.extend(["", "Layer Readiness", "---------------"])
    for layer in review["layers"]:
        lines.extend(
            [
                f"- [{layer['readiness']}] {layer['label']}: {READINESS_LABELS[layer['readiness']]}",
                f"  target: {layer['target_state']}",
                f"  current: {layer['current_coverage']}",
                f"  value: {layer['stakeholder_value']}",
                f"  next: {layer['horizontal_next_step']}",
                f"  defer: {layer['defer_vertical_work']}",
            ]
        )
    lines.extend(["", "Next Horizontal Slices", "----------------------"])
    lines.extend(f"- {item}" for item in review["next_horizontal_slices"])
    return "\n".join(lines).rstrip() + "\n"
