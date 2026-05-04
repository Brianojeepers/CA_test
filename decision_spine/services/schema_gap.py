"""Review current schema coverage against pilot and v0.2 intelligence needs."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
TEMPLATE_DIR = DATA_DIR / "pilot_extract_templates"


CURRENT_SCHEMA_FIELDS: dict[str, tuple[str, ...]] = {
    "signals.json": (
        "signal_id",
        "logged_date",
        "source_date",
        "green_threshold_date",
        "signal_theme",
        "signal_type",
        "role_archetype",
        "horizon_window",
        "geography",
        "client_segment",
        "source_classes",
        "source_diversity_score",
        "recency_score",
        "corroboration_score",
        "commercial_pull_score",
        "signal_strength_score",
        "status",
        "confidence",
        "summary",
    ),
    "decisions.json": (
        "decision_id",
        "signal_ids",
        "decision_signed_date",
        "decision_type",
        "decision_status",
        "owner",
        "partner_functions",
        "decision_summary",
        "rationale",
        "alternatives_considered",
        "complexity_tier",
    ),
    "releases.json": (
        "release_id",
        "decision_id",
        "release_date",
        "release_status",
        "change_type",
        "change_scope",
        "programme",
        "artifact",
        "cohort_id",
        "market_traceable",
        "linked_signal_ids",
    ),
    "cohort_outcomes.json": (
        "cohort_id",
        "programme",
        "archetype",
        "credential_tier",
        "cohort_start_date",
        "credential_issued_date",
        "eligible_for_placement",
        "placed_within_60_days",
        "placement_rate",
        "placements_started",
        "active_and_satisfactory_at_day_90",
        "retention_90d_rate",
        "client_csat_avg",
        "change_exposure",
        "baseline_group",
        "data_confidence",
    ),
    "predictions.json": (
        "prediction_id",
        "issued_date",
        "scoring_date",
        "linked_signal_ids",
        "claim",
        "horizon_class",
        "confidence_tag",
        "confirming_criterion",
        "contradicting_criterion",
        "outcome",
        "accuracy_score",
        "scoring_notes",
    ),
    "pedagogy_map.json": (
        "pedagogy_id",
        "decision_id",
        "release_id",
        "signal_ids",
        "capability",
        "bloom_target",
        "dreyfus_target",
        "performance_context",
        "practice_path",
        "assessment_evidence",
        "credential_threshold",
        "outcome_hypothesis",
    ),
    "role_competencies.json": (
        "competency_id",
        "role_archetype",
        "competency_cluster",
        "capability",
        "target_proficiency",
        "market_priority",
        "horizon_window",
        "linked_signal_ids",
        "linked_decision_ids",
        "linked_release_ids",
        "pedagogy_ids",
        "assessment_signal",
        "gap_hypothesis",
        "owner",
        "status",
    ),
    "learner_evidence_summary.json": (
        "evidence_id",
        "competency_id",
        "cohort_id",
        "programme",
        "role_archetype",
        "evidence_type",
        "evidence_window",
        "sample_size",
        "meets_threshold_count",
        "readiness_rate",
        "readiness_level",
        "evidence_confidence",
        "privacy_posture",
        "suppression_applied",
        "evidence_summary",
        "next_action",
    ),
}


PILOT_TEMPLATE_FILES = {
    "signals.json": "signals_template.json",
    "decisions.json": "decisions_template.json",
    "releases.json": "releases_template.json",
    "cohort_outcomes.json": "cohort_outcomes_template.json",
    "predictions.json": "predictions_template.json",
    "learner_evidence_summary.json": "learner_evidence_template.json",
}


CONTRACT_PRIMARY_FILES = {
    "market_signals": "signals.json",
    "decision_log": "decisions.json",
    "release_log": "releases.json",
    "cohort_outcomes": "cohort_outcomes.json",
    "competency_ontology": "role_competencies.json",
    "learner_evidence": "learner_evidence_summary.json",
    "prediction_register": "predictions.json",
}


FIELD_ALIASES: dict[str, dict[str, tuple[str, ...]]] = {
    "signals.json": {
        "score_components": (
            "source_diversity_score",
            "recency_score",
            "corroboration_score",
            "commercial_pull_score",
        ),
        "source_diversity_score": ("score_components",),
        "recency_score": ("score_components",),
        "corroboration_score": ("score_components",),
        "commercial_pull_score": ("score_components",),
        "signal_strength_score": ("score_components",),
    },
    "decisions.json": {
        "linked_signal_ids": ("signal_ids",),
        "signal_ids": ("linked_signal_ids",),
    },
    "cohort_outcomes.json": {
        "baseline_period": ("baseline_group",),
        "baseline_group": ("baseline_period",),
    },
    "predictions.json": {
        "prediction_statement": ("claim",),
        "claim": ("prediction_statement",),
        "horizon_window": ("horizon_class",),
        "horizon_class": ("horizon_window",),
        "confidence": ("confidence_tag",),
        "confidence_tag": ("confidence",),
        "learning_notes": ("scoring_notes",),
        "scoring_notes": ("learning_notes",),
    },
}


V02_INTELLIGENCE_REQUIREMENTS: tuple[dict[str, Any], ...] = (
    {
        "capability": "role_anchor_demand_index",
        "label": "Role Anchor Demand Index",
        "file": "signals.json",
        "required_fields": (
            "role_archetype",
            "geography",
            "horizon_window",
            "source_date",
            "source_classes",
            "confidence",
            "signal_strength_score",
            "demand_volume",
            "demand_growth_rate",
            "hiring_velocity",
            "compensation_pressure",
            "strategic_durability_score",
            "placement_conversion_alignment",
        ),
    },
    {
        "capability": "competency_gap_index_market_side",
        "label": "Competency Gap Index - market side",
        "file": "role_competencies.json",
        "required_fields": (
            "role_archetype",
            "competency_cluster",
            "capability",
            "target_proficiency",
            "market_priority",
            "horizon_window",
            "market_required_proficiency",
            "tool_decay_risk",
            "deprecation_signal",
        ),
    },
    {
        "capability": "competency_gap_index_learner_side",
        "label": "Competency Gap Index - learner side",
        "file": "learner_evidence_summary.json",
        "required_fields": (
            "competency_id",
            "cohort_id",
            "sample_size",
            "readiness_rate",
            "readiness_level",
            "demonstrated_proficiency",
            "proficiency_gap_score",
            "evidence_confidence",
            "privacy_posture",
        ),
    },
    {
        "capability": "horizon_radar",
        "label": "Horizon Radar",
        "file": "predictions.json",
        "required_fields": (
            "prediction_id",
            "issued_date",
            "horizon_window",
            "confidence",
            "outcome",
            "accuracy_score",
            "maturity_stage",
            "weak_signal_theme",
            "review_due_date",
        ),
    },
    {
        "capability": "curriculum_impact_simulator",
        "label": "Curriculum Impact Simulator",
        "file": "releases.json",
        "required_fields": (
            "decision_id",
            "release_date",
            "change_type",
            "change_scope",
            "programme",
            "cohort_id",
            "estimated_learner_time_delta",
            "instructional_capacity_cost",
            "expected_placement_lift",
            "expected_extension_lift",
        ),
    },
)


def load_json(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, list):
        raise ValueError(f"{path}: expected top-level JSON list")
    return data


def fields_in_records(records: list[dict[str, Any]]) -> set[str]:
    fields: set[str] = set()
    for record in records:
        fields.update(record)
    return fields


def load_fields(filename: str, *, template: bool = False) -> set[str]:
    if template:
        template_name = PILOT_TEMPLATE_FILES.get(filename)
        if not template_name:
            return set()
        path = TEMPLATE_DIR / template_name
    else:
        path = DATA_DIR / filename
    if not path.exists():
        return set()
    return fields_in_records(load_json(path))


def contract_primary_file(contract: dict[str, Any]) -> str:
    data_domain = str(contract.get("data_domain", ""))
    if data_domain in CONTRACT_PRIMARY_FILES:
        return CONTRACT_PRIMARY_FILES[data_domain]
    feeds_files = contract.get("feeds_files", [])
    return str(feeds_files[0]) if feeds_files else ""


def contracts_by_feed_file() -> dict[str, list[dict[str, Any]]]:
    by_file: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for contract in load_json(DATA_DIR / "source_contracts.json"):
        for filename in contract.get("feeds_files", []):
            by_file[str(filename)].append(contract)
    return dict(by_file)


def contracts_by_primary_file() -> dict[str, list[dict[str, Any]]]:
    by_file: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for contract in load_json(DATA_DIR / "source_contracts.json"):
        primary_file = contract_primary_file(contract)
        if primary_file:
            by_file[primary_file].append(contract)
    return dict(by_file)


def contract_fields(contracts: list[dict[str, Any]]) -> set[str]:
    fields: set[str] = set()
    for contract in contracts:
        fields.update(str(field) for field in contract.get("required_fields", []))
    return fields


def alias_hits(field: str, available_fields: set[str], filename: str) -> list[str]:
    return sorted(alias for alias in FIELD_ALIASES.get(filename, {}).get(field, ()) if alias in available_fields)


def is_field_covered(field: str, available_fields: set[str], filename: str) -> bool:
    return field in available_fields or bool(alias_hits(field, available_fields, filename))


def missing_fields(required_fields: set[str], available_fields: set[str], filename: str) -> list[str]:
    return sorted(field for field in required_fields if not is_field_covered(field, available_fields, filename))


def alias_covered_fields(required_fields: set[str], available_fields: set[str], filename: str) -> list[dict[str, Any]]:
    covered: list[dict[str, Any]] = []
    for field in sorted(required_fields):
        if field in available_fields:
            continue
        aliases = alias_hits(field, available_fields, filename)
        if aliases:
            covered.append({"field": field, "covered_by": aliases})
    return covered


def build_file_report(
    filename: str,
    linked_contracts: list[dict[str, Any]],
    field_contracts: list[dict[str, Any]],
) -> dict[str, Any]:
    seed_fields = load_fields(filename)
    template_fields = load_fields(filename, template=True)
    current_required = set(CURRENT_SCHEMA_FIELDS.get(filename, ()))
    source_required = contract_fields(field_contracts)

    return {
        "file": filename,
        "source_contract_ids": [contract["contract_id"] for contract in linked_contracts],
        "field_contract_ids": [contract["contract_id"] for contract in field_contracts],
        "seed_fields": sorted(seed_fields),
        "template_fields": sorted(template_fields),
        "current_required_fields": sorted(current_required),
        "contract_required_fields": sorted(source_required),
        "current_missing_from_seed": missing_fields(current_required, seed_fields, filename),
        "current_missing_from_template": missing_fields(current_required, template_fields, filename),
        "contract_missing_from_seed": missing_fields(source_required, seed_fields, filename),
        "contract_missing_from_template": missing_fields(source_required, template_fields, filename),
        "contract_alias_covered_in_seed": alias_covered_fields(source_required, seed_fields, filename),
        "template_alias_covered_for_current": alias_covered_fields(current_required, template_fields, filename),
        "contract_only_fields": sorted(field for field in source_required if field not in current_required),
    }


def build_v02_requirement_report() -> list[dict[str, Any]]:
    contracts = contracts_by_primary_file()
    reports: list[dict[str, Any]] = []
    for requirement in V02_INTELLIGENCE_REQUIREMENTS:
        filename = requirement["file"]
        seed_fields = load_fields(filename)
        template_fields = load_fields(filename, template=True)
        source_required = contract_fields(contracts.get(filename, []))
        available_fields = seed_fields | template_fields | source_required
        required = set(requirement["required_fields"])
        missing = missing_fields(required, available_fields, filename)
        reports.append(
            {
                "capability": requirement["capability"],
                "label": requirement["label"],
                "file": filename,
                "required_fields": sorted(required),
                "covered_fields": sorted(field for field in required if is_field_covered(field, available_fields, filename)),
                "missing_fields": missing,
                "coverage": round((len(required) - len(missing)) / len(required), 2),
            }
        )
    return reports


def build_minimum_viable_pilot_fields(file_reports: list[dict[str, Any]]) -> dict[str, list[str]]:
    v02_by_file: dict[str, set[str]] = defaultdict(set)
    for requirement in V02_INTELLIGENCE_REQUIREMENTS:
        v02_by_file[requirement["file"]].update(requirement["required_fields"])

    fields_by_file: dict[str, list[str]] = {}
    for report in file_reports:
        filename = report["file"]
        fields = (
            set(report["current_required_fields"])
            | set(report["contract_required_fields"])
            | v02_by_file.get(filename, set())
        )
        fields_by_file[filename] = sorted(fields)
    return fields_by_file


def build_source_readiness(contract_groups: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    contracts = {contract["contract_id"]: contract for group in contract_groups.values() for contract in group}
    readiness: list[dict[str, Any]] = []
    for contract in sorted(contracts.values(), key=lambda item: item["contract_id"]):
        readiness.append(
            {
                "contract_id": contract["contract_id"],
                "data_domain": contract["data_domain"],
                "readiness": contract["readiness"],
                "pilot_status": contract["pilot_status"],
                "feeds_files": contract["feeds_files"],
                "blocked": contract["readiness"] == "red",
                "manual_sampling_only": contract["readiness"] == "amber",
                "next_action": contract["next_action"],
            }
        )
    return readiness


def build_schema_gap_report() -> dict[str, Any]:
    feed_contract_groups = contracts_by_feed_file()
    field_contract_groups = contracts_by_primary_file()
    filenames = sorted(set(CURRENT_SCHEMA_FIELDS) | set(feed_contract_groups) | set(field_contract_groups))
    file_reports = [
        build_file_report(
            filename,
            feed_contract_groups.get(filename, []),
            field_contract_groups.get(filename, []),
        )
        for filename in filenames
    ]
    v02_reports = build_v02_requirement_report()
    source_readiness = build_source_readiness(feed_contract_groups)
    readiness_counts = Counter(item["readiness"] for item in source_readiness)

    return {
        "summary": {
            "seed_files": len([filename for filename in filenames if (DATA_DIR / filename).exists()]),
            "pilot_templates": len(PILOT_TEMPLATE_FILES),
            "source_contracts": len(source_readiness),
            "green_sources": readiness_counts["green"],
            "amber_sources": readiness_counts["amber"],
            "red_sources": readiness_counts["red"],
            "contract_seed_gap_count": sum(len(report["contract_missing_from_seed"]) for report in file_reports),
            "contract_template_gap_count": sum(len(report["contract_missing_from_template"]) for report in file_reports),
            "v02_gap_count": sum(len(report["missing_fields"]) for report in v02_reports),
        },
        "file_reports": file_reports,
        "source_readiness": source_readiness,
        "v02_requirements": v02_reports,
        "minimum_viable_pilot_fields": build_minimum_viable_pilot_fields(file_reports),
    }


def format_list(items: list[str], *, empty: str = "none") -> str:
    return ", ".join(items) if items else empty


def format_aliases(items: list[dict[str, Any]]) -> str:
    if not items:
        return "none"
    return "; ".join(f"{item['field']} via {', '.join(item['covered_by'])}" for item in items)


def render_schema_gap_report_text(report: dict[str, Any]) -> str:
    lines: list[str] = [
        "Decision Spine Schema Gap Review",
        "================================",
        "",
        "Readiness Summary",
        "-----------------",
    ]
    summary = report["summary"]
    lines.extend(
        [
            f"- seed_files={summary['seed_files']} pilot_templates={summary['pilot_templates']} source_contracts={summary['source_contracts']}",
            f"- green={summary['green_sources']} amber={summary['amber_sources']} red={summary['red_sources']}",
            f"- contract_seed_gaps={summary['contract_seed_gap_count']} contract_template_gaps={summary['contract_template_gap_count']} v0.2_gaps={summary['v02_gap_count']}",
        ]
    )

    lines.extend(["", "Current Schema Gaps", "-------------------"])
    for file_report in report["file_reports"]:
        if not file_report["contract_missing_from_seed"] and not file_report["contract_missing_from_template"]:
            continue
        lines.append(f"- {file_report['file']}")
        lines.append(f"  contract missing from seed: {format_list(file_report['contract_missing_from_seed'])}")
        lines.append(f"  contract missing from template: {format_list(file_report['contract_missing_from_template'])}")
        lines.append(f"  alias-covered in seed: {format_aliases(file_report['contract_alias_covered_in_seed'])}")

    lines.extend(["", "v0.2 Intelligence Gaps", "----------------------"])
    for requirement in report["v02_requirements"]:
        lines.append(
            f"- {requirement['label']} ({requirement['file']}): "
            f"coverage={requirement['coverage']:.0%}; missing={format_list(requirement['missing_fields'])}"
        )

    lines.extend(["", "Pilot Blockers", "--------------"])
    blocked = [item for item in report["source_readiness"] if item["blocked"]]
    if not blocked:
        lines.append("- none")
    for item in blocked:
        lines.append(f"- {item['contract_id']} {item['data_domain']}: {item['next_action']}")

    lines.extend(["", "Minimum Viable Pilot Fields", "---------------------------"])
    for filename, fields in report["minimum_viable_pilot_fields"].items():
        lines.append(f"- {filename}: {format_list(fields)}")

    return "\n".join(lines)
