#!/usr/bin/env python3
"""Print decision-level impact status across releases, readiness, and outcomes."""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from statistics import mean
from typing import Any

try:
    from validate_data import validate_all
except ModuleNotFoundError:
    from scripts.validate_data import validate_all


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
TODAY = date.today()


def load_json(filename: str) -> list[dict[str, Any]]:
    with (DATA_DIR / filename).open(encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, list):
        raise ValueError(f"{filename}: expected top-level JSON list")
    return data


def print_section(title: str) -> None:
    print(f"\n{title}")
    print("-" * len(title))


def validate_or_exit() -> None:
    validation = validate_all()
    if validation.errors:
        print("Data validation failed:", file=sys.stderr)
        for error in validation.errors:
            print(f"- {error}", file=sys.stderr)
        raise SystemExit(1)
    for warning in validation.warnings:
        print(f"Data validation warning: {warning}", file=sys.stderr)


def fmt_pct(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.1%}"


def fmt_pp(value: float | None) -> str:
    return "n/a" if value is None else f"{value:+.1%}"


def deltas_for_cohort(
    cohort: dict[str, Any],
    baselines_by_group: dict[str, list[dict[str, Any]]],
) -> tuple[float | None, float | None]:
    baseline = baselines_by_group.get(cohort["baseline_group"], [])
    placement_baseline = [item["placement_rate"] for item in baseline if item["placement_rate"] is not None]
    retention_baseline = [item["retention_90d_rate"] for item in baseline if item["retention_90d_rate"] is not None]

    placement_delta = None
    if cohort["placement_rate"] is not None and placement_baseline:
        placement_delta = cohort["placement_rate"] - mean(placement_baseline)

    retention_delta = None
    if cohort["retention_90d_rate"] is not None and retention_baseline:
        retention_delta = cohort["retention_90d_rate"] - mean(retention_baseline)

    return placement_delta, retention_delta


def impact_status(
    releases: list[dict[str, Any]],
    evidence: list[dict[str, Any]],
    cohorts: list[dict[str, Any]],
    placement_deltas: list[float],
    retention_deltas: list[float],
) -> str:
    if not releases:
        return "no_outcome_data"
    if any(release["release_status"] != "released" for release in releases):
        return "too_early"
    if not evidence and not cohorts:
        return "no_outcome_data"

    readiness_levels = {item["readiness_level"] for item in evidence}
    if "not_ready" in readiness_levels:
        return "needs_attention"
    if "insufficient_sample" in readiness_levels:
        return "needs_attention"
    if placement_deltas and min(placement_deltas) <= -0.05:
        return "needs_attention"
    if retention_deltas and min(retention_deltas) <= -0.03:
        return "needs_attention"

    has_positive_readiness = any(item["readiness_level"] in {"ready", "emerging"} for item in evidence)
    has_positive_outcome = any(delta >= 0.05 for delta in placement_deltas) or any(delta >= 0.03 for delta in retention_deltas)
    has_pending = any(item["readiness_level"] == "pending" for item in evidence)
    has_pending_outcome = any(cohort["placement_rate"] is None or cohort["retention_90d_rate"] is None for cohort in cohorts)

    if has_positive_readiness and has_positive_outcome and not has_pending_outcome:
        return "positive_signal"
    if has_positive_readiness:
        return "evidence_emerging"
    if has_pending or has_pending_outcome:
        return "too_early"
    return "no_outcome_data"


def action_for_status(status: str) -> str:
    actions = {
        "too_early": "keep on review calendar until evidence window closes",
        "evidence_emerging": "tighten evidence quality and wait for placement/retention maturity",
        "positive_signal": "consider amplifying while continuing retention monitoring",
        "needs_attention": "review rubric, release quality, sample size, and outcome signals",
        "no_outcome_data": "add learner evidence or cohort outcome linkage",
    }
    return actions[status]


def report_summary(statuses: list[str]) -> None:
    print_section("Impact Summary")
    counts = Counter(statuses)
    for status in ("positive_signal", "evidence_emerging", "too_early", "needs_attention", "no_outcome_data"):
        print(f"- {status}={counts[status]}")


def report_decisions(
    decisions: list[dict[str, Any]],
    releases_by_decision: dict[str, list[dict[str, Any]]],
    competencies_by_decision: dict[str, list[dict[str, Any]]],
    evidence_by_competency: dict[str, list[dict[str, Any]]],
    cohorts_by_id: dict[str, dict[str, Any]],
    baselines_by_group: dict[str, list[dict[str, Any]]],
    predictions_by_signal: dict[str, list[dict[str, Any]]],
) -> list[str]:
    print_section("Decision Impact")
    statuses: list[str] = []
    approved = [decision for decision in decisions if decision["decision_status"] == "approved"]
    for decision in approved:
        releases = releases_by_decision.get(decision["decision_id"], [])
        competencies = competencies_by_decision.get(decision["decision_id"], [])
        evidence = [
            item
            for competency in competencies
            for item in evidence_by_competency.get(competency["competency_id"], [])
        ]
        cohorts = [
            cohorts_by_id[release["cohort_id"]]
            for release in releases
            if release["cohort_id"] in cohorts_by_id
        ]
        placement_deltas: list[float] = []
        retention_deltas: list[float] = []
        cohort_deltas: dict[str, tuple[float | None, float | None]] = {}
        for cohort in cohorts:
            placement_delta, retention_delta = deltas_for_cohort(cohort, baselines_by_group)
            cohort_deltas[cohort["cohort_id"]] = (placement_delta, retention_delta)
            if placement_delta is not None:
                placement_deltas.append(placement_delta)
            if retention_delta is not None:
                retention_deltas.append(retention_delta)

        status = impact_status(releases, evidence, cohorts, placement_deltas, retention_deltas)
        statuses.append(status)
        release_text = ", ".join(
            f"{release['release_id']}:{release['release_status']}" for release in releases
        ) or "none"
        competency_text = ", ".join(item["competency_id"] for item in competencies) or "none"
        evidence_text = ", ".join(
            f"{item['evidence_id']}:{item['readiness_level']}" for item in evidence
        ) or "none"
        prediction_text = ", ".join(
            prediction["prediction_id"]
            for signal_id in decision["signal_ids"]
            for prediction in predictions_by_signal.get(signal_id, [])
        ) or "none"

        print(f"- {decision['decision_id']} [{status}] {decision['decision_summary']}")
        print(f"  owner={decision['owner']} | type={decision['decision_type']} | action={action_for_status(status)}")
        print(f"  releases={release_text}")
        print(f"  competencies={competency_text}")
        print(f"  learner_evidence={evidence_text}")
        if cohorts:
            for cohort in cohorts:
                placement_delta, retention_delta = cohort_deltas[cohort["cohort_id"]]
                print(
                    f"  cohort={cohort['cohort_id']} placement={fmt_pct(cohort['placement_rate'])} "
                    f"delta={fmt_pp(placement_delta)} retention={fmt_pct(cohort['retention_90d_rate'])} "
                    f"delta={fmt_pp(retention_delta)} confidence={cohort['data_confidence']}"
                )
        else:
            print("  cohort=none")
        print(f"  linked_predictions={prediction_text}")
    return statuses


def report_exclusions(decisions: list[dict[str, Any]]) -> None:
    print_section("Not Impact-Scored")
    excluded = [decision for decision in decisions if decision["decision_status"] != "approved"]
    if not excluded:
        print("- none")
        return
    for decision in excluded:
        print(
            f"- {decision['decision_id']} {decision['decision_status']} | "
            f"type={decision['decision_type']} | reason=not an approved implementation decision"
        )


def main() -> None:
    validate_or_exit()
    decisions = load_json("decisions.json")
    releases = load_json("releases.json")
    competencies = load_json("role_competencies.json")
    evidence = load_json("learner_evidence_summary.json")
    cohorts = load_json("cohort_outcomes.json")
    predictions = load_json("predictions.json")

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

    predictions_by_signal: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for prediction in predictions:
        for signal_id in prediction["linked_signal_ids"]:
            predictions_by_signal[signal_id].append(prediction)

    print("Decision Spine Decision Impact Review")
    print(f"Generated: {TODAY.isoformat()}")
    print("Reference: docs/decision_impact_model.md")
    statuses = report_decisions(
        decisions,
        releases_by_decision,
        competencies_by_decision,
        evidence_by_competency,
        cohorts_by_id,
        baselines_by_group,
        predictions_by_signal,
    )
    report_summary(statuses)
    report_exclusions(decisions)


if __name__ == "__main__":
    main()
