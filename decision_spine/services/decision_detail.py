"""Decision traceability service for stakeholder drill-downs."""

from __future__ import annotations

from typing import Any

from decision_spine.data_access import load_json
from scripts.validate_data import validate_all


def validation_warnings_or_raise() -> list[str]:
    validation = validate_all()
    if validation.errors:
        joined = "\n".join(f"- {error}" for error in validation.errors)
        raise ValueError(f"Data validation failed:\n{joined}")
    return validation.warnings


def build_decision_detail(decision_id: str) -> dict[str, Any] | None:
    warnings = validation_warnings_or_raise()
    decisions = load_json("decisions.json")
    signals = load_json("signals.json")
    releases = load_json("releases.json")
    competencies = load_json("role_competencies.json")
    evidence = load_json("learner_evidence_summary.json")
    cohorts = load_json("cohort_outcomes.json")
    predictions = load_json("predictions.json")
    pedagogy = load_json("pedagogy_map.json")

    decision = next((item for item in decisions if item["decision_id"] == decision_id), None)
    if decision is None:
        return None

    signal_ids = set(decision["signal_ids"])
    linked_signals = [item for item in signals if item["signal_id"] in signal_ids]
    linked_releases = [item for item in releases if item["decision_id"] == decision_id]
    release_ids = {item["release_id"] for item in linked_releases}
    cohort_ids = {item["cohort_id"] for item in linked_releases}

    linked_competencies = [
        item for item in competencies if decision_id in item["linked_decision_ids"]
    ]
    competency_ids = {item["competency_id"] for item in linked_competencies}

    linked_evidence = [item for item in evidence if item["competency_id"] in competency_ids]
    linked_cohorts = [item for item in cohorts if item["cohort_id"] in cohort_ids]
    linked_predictions = [
        item for item in predictions if signal_ids.intersection(item["linked_signal_ids"])
    ]
    linked_pedagogy = [
        item
        for item in pedagogy
        if item["decision_id"] == decision_id
        or item["release_id"] in release_ids
        or any(signal_id in signal_ids for signal_id in item["signal_ids"])
    ]

    return {
        "data_trust": {
            "validation_status": "passed",
            "warning_count": len(warnings),
            "warnings": warnings,
        },
        "decision": decision,
        "signals": linked_signals,
        "releases": linked_releases,
        "competencies": linked_competencies,
        "learner_evidence": linked_evidence,
        "cohort_outcomes": linked_cohorts,
        "predictions": linked_predictions,
        "pedagogy": linked_pedagogy,
        "traceability": {
            "signal_count": len(linked_signals),
            "release_count": len(linked_releases),
            "competency_count": len(linked_competencies),
            "evidence_count": len(linked_evidence),
            "cohort_count": len(linked_cohorts),
            "prediction_count": len(linked_predictions),
            "pedagogy_count": len(linked_pedagogy),
        },
    }
