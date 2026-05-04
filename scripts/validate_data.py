#!/usr/bin/env python3
"""Validate Decision Spine seed JSON data."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
TODAY = date.today()


@dataclass
class ValidationResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def error(self, filename: str, record_id: str, field_name: str, reason: str) -> None:
        self.errors.append(f"{filename}:{record_id}:{field_name}: {reason}")

    def warning(self, filename: str, record_id: str, field_name: str, reason: str) -> None:
        self.warnings.append(f"{filename}:{record_id}:{field_name}: {reason}")

    @property
    def ok(self) -> bool:
        return not self.errors


def load_json(filename: str) -> list[dict[str, Any]]:
    with (DATA_DIR / filename).open(encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, list):
        raise ValueError(f"{filename}: expected top-level JSON list")
    return data


def load_optional_json(filename: str) -> list[dict[str, Any]]:
    path = DATA_DIR / filename
    if not path.exists():
        return []
    return load_json(filename)


def load_optional_json_document(filename: str) -> dict[str, Any]:
    path = DATA_DIR / filename
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise ValueError(f"{filename}: expected top-level JSON object")
    return data


def parse_date(value: Any) -> date | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("expected YYYY-MM-DD string or null")
    return datetime.strptime(value, "%Y-%m-%d").date()


def record_id(record: dict[str, Any], *candidates: str) -> str:
    for candidate in candidates:
        value = record.get(candidate)
        if value:
            return str(value)
    return "<unknown>"


def require_fields(
    result: ValidationResult,
    filename: str,
    records: list[dict[str, Any]],
    fields: set[str],
    id_field: str,
) -> None:
    for record in records:
        rid = record_id(record, id_field)
        for field_name in sorted(fields):
            if field_name not in record:
                result.error(filename, rid, field_name, "required field is missing")


def require_unique_ids(
    result: ValidationResult,
    filename: str,
    records: list[dict[str, Any]],
    id_field: str,
) -> None:
    seen: set[str] = set()
    for record in records:
        rid = record.get(id_field)
        if not isinstance(rid, str) or not rid:
            result.error(filename, record_id(record, id_field), id_field, "must be a non-empty string")
            continue
        if rid in seen:
            result.error(filename, rid, id_field, "duplicate ID")
        seen.add(rid)


def validate_dates(
    result: ValidationResult,
    filename: str,
    records: list[dict[str, Any]],
    id_field: str,
    date_fields: set[str],
) -> None:
    for record in records:
        rid = record_id(record, id_field)
        for field_name in sorted(date_fields):
            if field_name not in record:
                continue
            try:
                parse_date(record[field_name])
            except ValueError as exc:
                result.error(filename, rid, field_name, str(exc))


def validate_enum(
    result: ValidationResult,
    filename: str,
    records: list[dict[str, Any]],
    id_field: str,
    field_name: str,
    allowed: set[str],
) -> None:
    for record in records:
        value = record.get(field_name)
        if value not in allowed:
            result.error(
                filename,
                record_id(record, id_field),
                field_name,
                f"expected one of {sorted(allowed)}, got {value!r}",
            )


def validate_number(
    result: ValidationResult,
    filename: str,
    records: list[dict[str, Any]],
    id_field: str,
    field_name: str,
    *,
    nullable: bool = False,
    minimum: float | None = None,
    maximum: float | None = None,
) -> None:
    for record in records:
        value = record.get(field_name)
        rid = record_id(record, id_field)
        if value is None and nullable:
            continue
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            result.error(filename, rid, field_name, f"expected number, got {value!r}")
            continue
        if minimum is not None and value < minimum:
            result.error(filename, rid, field_name, f"expected >= {minimum}, got {value}")
        if maximum is not None and value > maximum:
            result.error(filename, rid, field_name, f"expected <= {maximum}, got {value}")


def validate_list_of_ids(
    result: ValidationResult,
    filename: str,
    record: dict[str, Any],
    id_field: str,
    field_name: str,
    allowed_ids: set[str],
) -> None:
    rid = record_id(record, id_field)
    values = record.get(field_name)
    if not isinstance(values, list) or not values:
        result.error(filename, rid, field_name, "must be a non-empty list")
        return
    for value in values:
        if value not in allowed_ids:
            result.error(filename, rid, field_name, f"unknown ID {value!r}")


def validate_all() -> ValidationResult:
    result = ValidationResult()
    try:
        signals = load_json("signals.json")
        decisions = load_json("decisions.json")
        releases = load_json("releases.json")
        cohorts = load_json("cohort_outcomes.json")
        predictions = load_json("predictions.json")
        pedagogy = load_optional_json("pedagogy_map.json")
        source_contracts = load_optional_json("source_contracts.json")
        role_competencies = load_optional_json("role_competencies.json")
        learner_evidence = load_optional_json("learner_evidence_summary.json")
        v02_requirements = load_optional_json_document("v02_intelligence_requirements.json")
        v02_action_statuses = load_optional_json("v02_field_action_status.json")
        v02_action_events = load_optional_json("v02_field_action_events.json")
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        result.errors.append(str(exc))
        return result

    require_unique_ids(result, "signals.json", signals, "signal_id")
    require_unique_ids(result, "decisions.json", decisions, "decision_id")
    require_unique_ids(result, "releases.json", releases, "release_id")
    require_unique_ids(result, "cohort_outcomes.json", cohorts, "cohort_id")
    require_unique_ids(result, "predictions.json", predictions, "prediction_id")
    if pedagogy:
        require_unique_ids(result, "pedagogy_map.json", pedagogy, "pedagogy_id")
    if source_contracts:
        require_unique_ids(result, "source_contracts.json", source_contracts, "contract_id")
    if role_competencies:
        require_unique_ids(result, "role_competencies.json", role_competencies, "competency_id")
    if learner_evidence:
        require_unique_ids(result, "learner_evidence_summary.json", learner_evidence, "evidence_id")

    require_fields(
        result,
        "signals.json",
        signals,
        {
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
        },
        "signal_id",
    )
    require_fields(
        result,
        "decisions.json",
        decisions,
        {
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
        },
        "decision_id",
    )
    require_fields(
        result,
        "releases.json",
        releases,
        {
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
        },
        "release_id",
    )
    require_fields(
        result,
        "cohort_outcomes.json",
        cohorts,
        {
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
        },
        "cohort_id",
    )
    require_fields(
        result,
        "predictions.json",
        predictions,
        {
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
        },
        "prediction_id",
    )
    if pedagogy:
        require_fields(
            result,
            "pedagogy_map.json",
            pedagogy,
            {
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
            },
            "pedagogy_id",
        )
    if source_contracts:
        require_fields(
            result,
            "source_contracts.json",
            source_contracts,
            {
                "contract_id",
                "data_domain",
                "candidate_source",
                "source_owner",
                "privacy_owner",
                "feeds_files",
                "minimum_grain",
                "required_fields",
                "privacy_posture",
                "freshness_sla",
                "pilot_status",
                "readiness",
                "blockers",
                "next_action",
            },
            "contract_id",
        )
    if role_competencies:
        require_fields(
            result,
            "role_competencies.json",
            role_competencies,
            {
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
            },
            "competency_id",
        )
    if learner_evidence:
        require_fields(
            result,
            "learner_evidence_summary.json",
            learner_evidence,
            {
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
            },
            "evidence_id",
        )
    if v02_action_statuses:
        require_fields(
            result,
            "v02_field_action_status.json",
            v02_action_statuses,
            {
                "capability",
                "field",
                "owner",
                "status",
                "notes",
                "updated_date",
            },
            "field",
        )
    if v02_action_events:
        require_unique_ids(result, "v02_field_action_events.json", v02_action_events, "event_id")
        require_fields(
            result,
            "v02_field_action_events.json",
            v02_action_events,
            {
                "event_id",
                "capability",
                "field",
                "previous_status",
                "next_status",
                "notes",
                "event_date",
            },
            "event_id",
        )

    validate_dates(result, "signals.json", signals, "signal_id", {"logged_date", "source_date", "green_threshold_date"})
    validate_dates(result, "decisions.json", decisions, "decision_id", {"decision_signed_date"})
    validate_dates(result, "releases.json", releases, "release_id", {"release_date"})
    validate_dates(result, "cohort_outcomes.json", cohorts, "cohort_id", {"cohort_start_date", "credential_issued_date"})
    validate_dates(result, "predictions.json", predictions, "prediction_id", {"issued_date", "scoring_date"})
    if v02_action_statuses:
        validate_dates(result, "v02_field_action_status.json", v02_action_statuses, "field", {"updated_date"})
    if v02_action_events:
        validate_dates(result, "v02_field_action_events.json", v02_action_events, "event_id", {"event_date"})

    validate_enum(result, "signals.json", signals, "signal_id", "status", {"green", "amber", "red"})
    validate_enum(result, "signals.json", signals, "signal_id", "confidence", {"low", "medium", "high"})
    validate_enum(result, "decisions.json", decisions, "decision_id", "decision_status", {"approved", "watch", "rejected", "deferred"})
    validate_enum(result, "decisions.json", decisions, "decision_id", "complexity_tier", {"low", "medium", "high"})
    validate_enum(result, "releases.json", releases, "release_id", "release_status", {"released", "in_progress", "scheduled"})
    validate_enum(result, "cohort_outcomes.json", cohorts, "cohort_id", "change_exposure", {"pre_change", "post_change"})
    validate_enum(result, "cohort_outcomes.json", cohorts, "cohort_id", "data_confidence", {"low", "medium", "high"})
    validate_enum(result, "predictions.json", predictions, "prediction_id", "outcome", {"confirmed", "contradicted", "inconclusive", "pending"})
    for status in v02_action_statuses:
        validate_enum(
            result,
            "v02_field_action_status.json",
            [status],
            "field",
            "status",
            {"open", "in_review", "approved", "blocked", "deferred"},
        )
    for event in v02_action_events:
        validate_enum(
            result,
            "v02_field_action_events.json",
            [event],
            "event_id",
            "previous_status",
            {"open", "in_review", "approved", "blocked", "deferred"},
        )
        validate_enum(
            result,
            "v02_field_action_events.json",
            [event],
            "event_id",
            "next_status",
            {"open", "in_review", "approved", "blocked", "deferred"},
        )

    for score_field in (
        "source_diversity_score",
        "recency_score",
        "corroboration_score",
        "commercial_pull_score",
        "signal_strength_score",
    ):
        validate_number(result, "signals.json", signals, "signal_id", score_field, minimum=0, maximum=100)

    for rate_field in ("placement_rate", "retention_90d_rate", "client_csat_avg"):
        maximum = 5 if rate_field == "client_csat_avg" else 1
        validate_number(
            result,
            "cohort_outcomes.json",
            cohorts,
            "cohort_id",
            rate_field,
            nullable=True,
            minimum=0,
            maximum=maximum,
        )

    for count_field in (
        "eligible_for_placement",
        "placed_within_60_days",
        "placements_started",
        "active_and_satisfactory_at_day_90",
    ):
        validate_number(
            result,
            "cohort_outcomes.json",
            cohorts,
            "cohort_id",
            count_field,
            nullable=True,
            minimum=0,
        )

    validate_number(result, "predictions.json", predictions, "prediction_id", "accuracy_score", nullable=True, minimum=0, maximum=1)

    signal_ids = {signal.get("signal_id") for signal in signals}
    decision_ids = {decision.get("decision_id") for decision in decisions}
    release_ids = {release.get("release_id") for release in releases}
    cohort_ids = {cohort.get("cohort_id") for cohort in cohorts}
    competency_ids = {competency.get("competency_id") for competency in role_competencies}

    for decision in decisions:
        validate_list_of_ids(result, "decisions.json", decision, "decision_id", "signal_ids", signal_ids)

    for release in releases:
        rid = record_id(release, "release_id")
        decision_id = release.get("decision_id")
        if decision_id not in decision_ids:
            result.error("releases.json", rid, "decision_id", f"unknown ID {decision_id!r}")
        validate_list_of_ids(result, "releases.json", release, "release_id", "linked_signal_ids", signal_ids)

        cohort_id = release.get("cohort_id")
        if cohort_id not in cohort_ids:
            if release.get("release_status") == "released":
                result.error("releases.json", rid, "cohort_id", f"unknown released cohort {cohort_id!r}")
            else:
                result.warning("releases.json", rid, "cohort_id", f"future cohort / no outcomes yet: {cohort_id!r}")

    for prediction in predictions:
        validate_list_of_ids(result, "predictions.json", prediction, "prediction_id", "linked_signal_ids", signal_ids)

    for item in pedagogy:
        pid = record_id(item, "pedagogy_id")
        if item.get("decision_id") not in decision_ids:
            result.error("pedagogy_map.json", pid, "decision_id", f"unknown ID {item.get('decision_id')!r}")
        if item.get("release_id") not in release_ids:
            result.error("pedagogy_map.json", pid, "release_id", f"unknown ID {item.get('release_id')!r}")
        validate_list_of_ids(result, "pedagogy_map.json", item, "pedagogy_id", "signal_ids", signal_ids)
        practice_path = item.get("practice_path")
        if not isinstance(practice_path, list) or not practice_path:
            result.error("pedagogy_map.json", pid, "practice_path", "must be a non-empty list")
        for field_name in (
            "capability",
            "bloom_target",
            "dreyfus_target",
            "performance_context",
            "assessment_evidence",
            "credential_threshold",
            "outcome_hypothesis",
        ):
            if field_name in item and (not isinstance(item[field_name], str) or not item[field_name].strip()):
                result.error("pedagogy_map.json", pid, field_name, "must be a non-empty string")

    pedagogy_ids = {item.get("pedagogy_id") for item in pedagogy}
    for item in role_competencies:
        cid = record_id(item, "competency_id")
        validate_enum(
            result,
            "role_competencies.json",
            [item],
            "competency_id",
            "market_priority",
            {"core", "emerging", "monitor"},
        )
        validate_enum(
            result,
            "role_competencies.json",
            [item],
            "competency_id",
            "status",
            {"active", "monitor", "deprecated"},
        )
        for field_name, allowed_ids in (
            ("linked_signal_ids", signal_ids),
            ("linked_decision_ids", decision_ids),
        ):
            validate_list_of_ids(result, "role_competencies.json", item, "competency_id", field_name, allowed_ids)
        for field_name, allowed_ids in (
            ("linked_release_ids", release_ids),
            ("pedagogy_ids", pedagogy_ids),
        ):
            values = item.get(field_name)
            if not isinstance(values, list):
                result.error("role_competencies.json", cid, field_name, "must be a list")
                continue
            for value in values:
                if value not in allowed_ids:
                    result.error("role_competencies.json", cid, field_name, f"unknown ID {value!r}")
        for field_name in (
            "role_archetype",
            "competency_cluster",
            "capability",
            "target_proficiency",
            "horizon_window",
            "assessment_signal",
            "gap_hypothesis",
            "owner",
        ):
            if field_name in item and (not isinstance(item[field_name], str) or not item[field_name].strip()):
                result.error("role_competencies.json", cid, field_name, "must be a non-empty string")
        if item.get("status") == "active" and item.get("market_priority") == "monitor":
            result.warning(
                "role_competencies.json",
                cid,
                "market_priority",
                "active competency is marked monitor priority",
            )
        if item.get("market_priority") in {"core", "emerging"} and not item.get("linked_release_ids"):
            result.warning(
                "role_competencies.json",
                cid,
                "linked_release_ids",
                "core or emerging competency has no release yet",
            )

    framed_decisions = {item.get("decision_id") for item in pedagogy}
    for decision in decisions:
        if decision["decision_type"] in {"curriculum", "credential", "assessment"} and decision["decision_id"] not in framed_decisions:
            result.warning(
                "pedagogy_map.json",
                decision["decision_id"],
                "decision_id",
                "learning or credential decision has no pedagogy mapping yet",
            )

    competency_signals: set[str] = set()
    for item in role_competencies:
        linked_signal_ids = item.get("linked_signal_ids")
        if isinstance(linked_signal_ids, list):
            competency_signals.update(linked_signal_ids)
    for signal in signals:
        if signal["status"] == "green" and signal["signal_id"] not in competency_signals:
            result.warning(
                "role_competencies.json",
                signal["signal_id"],
                "linked_signal_ids",
                "green signal has no competency mapping yet",
            )

    for item in learner_evidence:
        eid = record_id(item, "evidence_id")
        if item.get("competency_id") not in competency_ids:
            result.error(
                "learner_evidence_summary.json",
                eid,
                "competency_id",
                f"unknown ID {item.get('competency_id')!r}",
            )
        if item.get("cohort_id") not in cohort_ids:
            result.error(
                "learner_evidence_summary.json",
                eid,
                "cohort_id",
                f"unknown ID {item.get('cohort_id')!r}",
            )
        validate_enum(
            result,
            "learner_evidence_summary.json",
            [item],
            "evidence_id",
            "evidence_type",
            {"assessment_artifact", "credential_review", "simulation_result", "portfolio_review", "placement_signal"},
        )
        validate_enum(
            result,
            "learner_evidence_summary.json",
            [item],
            "evidence_id",
            "readiness_level",
            {"ready", "emerging", "not_ready", "pending", "insufficient_sample"},
        )
        validate_enum(
            result,
            "learner_evidence_summary.json",
            [item],
            "evidence_id",
            "evidence_confidence",
            {"low", "medium", "high"},
        )
        validate_enum(
            result,
            "learner_evidence_summary.json",
            [item],
            "evidence_id",
            "privacy_posture",
            {"aggregated", "suppressed"},
        )
        validate_number(
            result,
            "learner_evidence_summary.json",
            [item],
            "evidence_id",
            "sample_size",
            minimum=0,
        )
        validate_number(
            result,
            "learner_evidence_summary.json",
            [item],
            "evidence_id",
            "meets_threshold_count",
            nullable=True,
            minimum=0,
        )
        validate_number(
            result,
            "learner_evidence_summary.json",
            [item],
            "evidence_id",
            "readiness_rate",
            nullable=True,
            minimum=0,
            maximum=1,
        )
        if not isinstance(item.get("suppression_applied"), bool):
            result.error("learner_evidence_summary.json", eid, "suppression_applied", "must be a boolean")
        sample_size = item.get("sample_size")
        threshold_count = item.get("meets_threshold_count")
        readiness_rate = item.get("readiness_rate")
        if isinstance(sample_size, (int, float)) and isinstance(threshold_count, (int, float)):
            if threshold_count > sample_size:
                result.error(
                    "learner_evidence_summary.json",
                    eid,
                    "meets_threshold_count",
                    "cannot exceed sample_size",
                )
            expected_rate = round(threshold_count / sample_size, 3) if sample_size else None
            if readiness_rate is not None and expected_rate is not None and abs(readiness_rate - expected_rate) > 0.001:
                result.warning(
                    "learner_evidence_summary.json",
                    eid,
                    "readiness_rate",
                    f"does not match meets_threshold_count/sample_size ({expected_rate})",
                )
        if item.get("readiness_level") in {"pending", "insufficient_sample"} and readiness_rate is not None:
            result.warning(
                "learner_evidence_summary.json",
                eid,
                "readiness_rate",
                "pending or insufficient-sample evidence should usually have null readiness_rate",
            )
        if item.get("readiness_level") == "insufficient_sample" and not item.get("suppression_applied"):
            result.warning(
                "learner_evidence_summary.json",
                eid,
                "suppression_applied",
                "insufficient sample should be suppressed or rolled up",
            )
        for field_name in (
            "programme",
            "role_archetype",
            "evidence_window",
            "evidence_summary",
            "next_action",
        ):
            if field_name in item and (not isinstance(item[field_name], str) or not item[field_name].strip()):
                result.error("learner_evidence_summary.json", eid, field_name, "must be a non-empty string")

    evidence_competencies = {item.get("competency_id") for item in learner_evidence}
    for competency in role_competencies:
        if competency["status"] == "active" and competency["competency_id"] not in evidence_competencies:
            result.warning(
                "learner_evidence_summary.json",
                competency["competency_id"],
                "competency_id",
                "active competency has no learner evidence yet",
            )

    if v02_requirements or v02_action_statuses or v02_action_events:
        requirements = v02_requirements.get("requirements")
        known_v02_fields: set[tuple[str, str]] = set()
        if v02_requirements and not isinstance(requirements, list):
            result.error("v02_intelligence_requirements.json", "<root>", "requirements", "must be a list")
        elif isinstance(requirements, list):
            for requirement in requirements:
                if not isinstance(requirement, dict):
                    result.error("v02_intelligence_requirements.json", "<unknown>", "requirements", "each item must be an object")
                    continue
                capability = requirement.get("capability")
                fields = requirement.get("required_fields")
                if not isinstance(capability, str) or not capability.strip():
                    result.error("v02_intelligence_requirements.json", "<unknown>", "capability", "must be a non-empty string")
                    continue
                if not isinstance(fields, list) or not fields:
                    result.error("v02_intelligence_requirements.json", capability, "required_fields", "must be a non-empty list")
                    continue
                for field_item in fields:
                    field_name = field_item.get("field") if isinstance(field_item, dict) else field_item
                    if not isinstance(field_name, str) or not field_name.strip():
                        result.error(
                            "v02_intelligence_requirements.json",
                            capability,
                            "required_fields",
                            "field must be a non-empty string",
                        )
                        continue
                    known_v02_fields.add((capability, field_name))

        seen_status_keys: set[tuple[Any, Any]] = set()
        for status in v02_action_statuses:
            capability = status.get("capability")
            field_name = status.get("field")
            sid = f"{capability}:{field_name}"
            if (capability, field_name) in seen_status_keys:
                result.error("v02_field_action_status.json", sid, "field", "duplicate capability/field status")
            seen_status_keys.add((capability, field_name))
            if known_v02_fields and (capability, field_name) not in known_v02_fields:
                result.error("v02_field_action_status.json", sid, "field", "status references unknown v0.2 field")
            for field_name_key in ("capability", "field", "owner", "notes"):
                if field_name_key in status and (
                    not isinstance(status[field_name_key], str) or not status[field_name_key].strip()
                ):
                    result.error("v02_field_action_status.json", sid, field_name_key, "must be a non-empty string")
        for event in v02_action_events:
            capability = event.get("capability")
            field_name = event.get("field")
            event_id = record_id(event, "event_id")
            if known_v02_fields and (capability, field_name) not in known_v02_fields:
                result.error("v02_field_action_events.json", event_id, "field", "event references unknown v0.2 field")
            for field_name_key in ("event_id", "capability", "field", "previous_status", "next_status", "notes"):
                if field_name_key in event and (
                    not isinstance(event[field_name_key], str) or not event[field_name_key].strip()
                ):
                    result.error("v02_field_action_events.json", event_id, field_name_key, "must be a non-empty string")

    expected_files = {
        "signals.json",
        "decisions.json",
        "releases.json",
        "cohort_outcomes.json",
        "predictions.json",
        "pedagogy_map.json",
        "role_competencies.json",
        "learner_evidence_summary.json",
    }
    for contract in source_contracts:
        cid = record_id(contract, "contract_id")
        if contract.get("readiness") not in {"green", "amber", "red"}:
            result.error(
                "source_contracts.json",
                cid,
                "readiness",
                "expected one of ['amber', 'green', 'red']",
            )
        for field_name in ("feeds_files", "required_fields", "blockers"):
            value = contract.get(field_name)
            if not isinstance(value, list):
                result.error("source_contracts.json", cid, field_name, "must be a list")
        feeds_files = contract.get("feeds_files")
        if isinstance(feeds_files, list):
            for filename in feeds_files:
                if filename not in expected_files:
                    result.warning(
                        "source_contracts.json",
                        cid,
                        "feeds_files",
                        f"file is not part of current MVP schema: {filename!r}",
                    )
        for field_name in (
            "data_domain",
            "candidate_source",
            "source_owner",
            "privacy_owner",
            "minimum_grain",
            "privacy_posture",
            "freshness_sla",
            "pilot_status",
            "next_action",
        ):
            if field_name in contract and (
                not isinstance(contract[field_name], str) or not contract[field_name].strip()
            ):
                result.error("source_contracts.json", cid, field_name, "must be a non-empty string")

    for prediction in predictions:
        rid = record_id(prediction, "prediction_id")
        try:
            scoring_date = parse_date(prediction.get("scoring_date"))
        except ValueError:
            continue
        outcome = prediction.get("outcome")
        if scoring_date and scoring_date <= TODAY and outcome == "pending":
            result.warning("predictions.json", rid, "outcome", "past scoring date is still pending")
        if outcome in {"confirmed", "contradicted"} and prediction.get("accuracy_score") is None:
            result.error("predictions.json", rid, "accuracy_score", "scored prediction requires accuracy_score")
        if outcome == "pending" and prediction.get("accuracy_score") is not None:
            result.error("predictions.json", rid, "accuracy_score", "pending prediction must have null accuracy_score")
        if not prediction.get("confirming_criterion"):
            result.error("predictions.json", rid, "confirming_criterion", "required for falsifiable prediction")
        if not prediction.get("contradicting_criterion"):
            result.error("predictions.json", rid, "contradicting_criterion", "required for falsifiable prediction")

    return result


def print_result(result: ValidationResult) -> None:
    if result.errors:
        print("Validation errors:")
        for error in result.errors:
            print(f"- {error}")
    if result.warnings:
        print("Validation warnings:")
        for warning in result.warnings:
            print(f"- {warning}")
    if result.ok:
        print(f"Validation passed ({len(result.warnings)} warning(s)).")


def main() -> int:
    result = validate_all()
    print_result(result)
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
