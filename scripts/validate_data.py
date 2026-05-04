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

    validate_dates(result, "signals.json", signals, "signal_id", {"logged_date", "source_date", "green_threshold_date"})
    validate_dates(result, "decisions.json", decisions, "decision_id", {"decision_signed_date"})
    validate_dates(result, "releases.json", releases, "release_id", {"release_date"})
    validate_dates(result, "cohort_outcomes.json", cohorts, "cohort_id", {"cohort_start_date", "credential_issued_date"})
    validate_dates(result, "predictions.json", predictions, "prediction_id", {"issued_date", "scoring_date"})

    validate_enum(result, "signals.json", signals, "signal_id", "status", {"green", "amber", "red"})
    validate_enum(result, "signals.json", signals, "signal_id", "confidence", {"low", "medium", "high"})
    validate_enum(result, "decisions.json", decisions, "decision_id", "decision_status", {"approved", "watch", "rejected", "deferred"})
    validate_enum(result, "decisions.json", decisions, "decision_id", "complexity_tier", {"low", "medium", "high"})
    validate_enum(result, "releases.json", releases, "release_id", "release_status", {"released", "in_progress", "scheduled"})
    validate_enum(result, "cohort_outcomes.json", cohorts, "cohort_id", "change_exposure", {"pre_change", "post_change"})
    validate_enum(result, "cohort_outcomes.json", cohorts, "cohort_id", "data_confidence", {"low", "medium", "high"})
    validate_enum(result, "predictions.json", predictions, "prediction_id", "outcome", {"confirmed", "contradicted", "inconclusive", "pending"})

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

    framed_decisions = {item.get("decision_id") for item in pedagogy}
    for decision in decisions:
        if decision["decision_type"] in {"curriculum", "credential", "assessment"} and decision["decision_id"] not in framed_decisions:
            result.warning(
                "pedagogy_map.json",
                decision["decision_id"],
                "decision_id",
                "learning or credential decision has no pedagogy mapping yet",
            )

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
