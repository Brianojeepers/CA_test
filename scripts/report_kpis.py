#!/usr/bin/env python3
"""Print a local Decision Spine KPI report from seed JSON data."""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path
from statistics import mean
from typing import Any

from validate_data import validate_all


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
TODAY = date.today()


def load_json(filename: str) -> list[dict[str, Any]]:
    with (DATA_DIR / filename).open(encoding="utf-8") as file:
        return json.load(file)


def parse_date(value: str | None) -> date | None:
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


def days_between(start: str | None, end: str | None) -> int | None:
    start_date = parse_date(start)
    end_date = parse_date(end)
    if start_date is None or end_date is None:
        return None
    return (end_date - start_date).days


def status_for_signal_to_decision(days: int | None) -> str:
    if days is None:
        return "red"
    if days <= 21:
        return "green"
    if days <= 45:
        return "amber"
    return "red"


def status_for_decision_to_release(days: int | None, complexity: str) -> str:
    if days is None:
        return "pending"

    thresholds = {
        "low": (14, 30),
        "medium": (30, 60),
        "high": (60, 90),
    }
    green_days, red_days = thresholds.get(complexity, thresholds["medium"])
    if days <= green_days:
        return "green"
    if days > red_days:
        return "red"
    return "amber"


def status_for_delta(delta: float | None, green: float, red: float) -> str:
    if delta is None:
        return "pending"
    if delta >= green:
        return "green"
    if delta <= red:
        return "red"
    return "amber"


def fmt_days(value: int | None) -> str:
    return "n/a" if value is None else f"{value}d"


def fmt_pct(value: float | None) -> str:
    return "n/a" if value is None else f"{value * 100:.1f}%"


def fmt_pp(value: float | None) -> str:
    return "n/a" if value is None else f"{value * 100:+.1f}pp"


def print_section(title: str) -> None:
    print(f"\n{title}")
    print("-" * len(title))


def report_signal_strength(signals: list[dict[str, Any]]) -> None:
    print_section("K1 Signal Strength")
    counts = defaultdict(int)
    for signal in signals:
        counts[signal["status"]] += 1

    average_score = mean(signal["signal_strength_score"] for signal in signals)
    print(f"Average score: {average_score:.1f}")
    print(
        "Status mix: "
        f"green={counts['green']} amber={counts['amber']} red={counts['red']}"
    )

    strongest = sorted(signals, key=lambda item: item["signal_strength_score"], reverse=True)
    for signal in strongest[:3]:
        print(
            f"- {signal['signal_id']} [{signal['status']} "
            f"{signal['signal_strength_score']}]: {signal['signal_theme']}"
        )


def report_signal_to_decision(
    signals: list[dict[str, Any]], decisions: list[dict[str, Any]]
) -> None:
    print_section("K2 Signal-To-Decision Time")
    decisions_by_signal: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for decision in decisions:
        for signal_id in decision["signal_ids"]:
            decisions_by_signal[signal_id].append(decision)

    green_signals = [signal for signal in signals if signal["status"] == "green"]
    for signal in green_signals:
        linked_decisions = decisions_by_signal.get(signal["signal_id"], [])
        if not linked_decisions:
            print(f"- red {signal['signal_id']}: no linked decision")
            continue

        first_decision = min(linked_decisions, key=lambda item: item["decision_signed_date"])
        elapsed_days = days_between(
            signal["green_threshold_date"], first_decision["decision_signed_date"]
        )
        status = status_for_signal_to_decision(elapsed_days)
        print(
            f"- {status} {signal['signal_id']} -> {first_decision['decision_id']}: "
            f"{fmt_days(elapsed_days)}"
        )


def report_decision_to_release(
    decisions: list[dict[str, Any]], releases: list[dict[str, Any]]
) -> None:
    print_section("K3 Decision-To-Release Time")
    decisions_by_id = {decision["decision_id"]: decision for decision in decisions}

    for release in releases:
        decision = decisions_by_id[release["decision_id"]]
        elapsed_days = days_between(decision["decision_signed_date"], release["release_date"])
        status = status_for_decision_to_release(elapsed_days, decision["complexity_tier"])
        target = release["release_date"] or "not released"
        print(
            f"- {status} {decision['decision_id']} -> {release['release_id']}: "
            f"{fmt_days(elapsed_days)} ({decision['complexity_tier']}, {target})"
        )


def report_changes_per_quarter(releases: list[dict[str, Any]]) -> None:
    print_section("K4 Changes Per Quarter")
    released = [release for release in releases if release["release_date"]]
    by_quarter: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for release in released:
        release_date = parse_date(release["release_date"])
        quarter = ((release_date.month - 1) // 3) + 1
        by_quarter[f"{release_date.year}-Q{quarter}"].append(release)

    for quarter in sorted(by_quarter):
        quarter_releases = by_quarter[quarter]
        traceable_count = sum(1 for item in quarter_releases if item["market_traceable"])
        if traceable_count == 0:
            status = "red"
        elif len(quarter_releases) >= 3:
            status = "green"
        else:
            status = "amber"

        print(
            f"- {status} {quarter}: {len(quarter_releases)} released, "
            f"{traceable_count} market-traceable"
        )


def report_outcome_deltas(cohorts: list[dict[str, Any]]) -> None:
    print_section("K5/K6 Outcome Deltas")
    pre_rates_by_baseline: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for cohort in cohorts:
        if cohort["change_exposure"] == "pre_change":
            pre_rates_by_baseline[cohort["baseline_group"]].append(cohort)

    for cohort in cohorts:
        if cohort["change_exposure"] != "post_change":
            continue

        baseline = pre_rates_by_baseline.get(cohort["baseline_group"], [])
        placement_baseline = [
            item["placement_rate"] for item in baseline if item["placement_rate"] is not None
        ]
        retention_baseline = [
            item["retention_90d_rate"]
            for item in baseline
            if item["retention_90d_rate"] is not None
        ]

        placement_delta = None
        if cohort["placement_rate"] is not None and placement_baseline:
            placement_delta = cohort["placement_rate"] - mean(placement_baseline)

        retention_delta = None
        if cohort["retention_90d_rate"] is not None and retention_baseline:
            retention_delta = cohort["retention_90d_rate"] - mean(retention_baseline)

        placement_status = status_for_delta(placement_delta, green=0.05, red=-0.05)
        retention_status = status_for_delta(retention_delta, green=0.03, red=-0.03)
        n_note = " small-n" if cohort["eligible_for_placement"] < 25 else ""

        print(
            f"- {cohort['cohort_id']}{n_note}: "
            f"placement {placement_status} {fmt_pp(placement_delta)} "
            f"({fmt_pct(cohort['placement_rate'])}); "
            f"retention {retention_status} {fmt_pp(retention_delta)} "
            f"({fmt_pct(cohort['retention_90d_rate'])})"
        )


def report_prediction_accuracy(predictions: list[dict[str, Any]]) -> None:
    print_section("K7 Prediction Accuracy")
    scored = [
        prediction
        for prediction in predictions
        if parse_date(prediction["scoring_date"]) <= TODAY
        and prediction["outcome"] in {"confirmed", "contradicted"}
    ]
    pending = [
        prediction
        for prediction in predictions
        if prediction["outcome"] == "pending" or parse_date(prediction["scoring_date"]) > TODAY
    ]

    accuracy = None
    if scored:
        accuracy = sum(item["accuracy_score"] for item in scored) / len(scored)

    status = status_for_delta(accuracy, green=0.60, red=0.40)
    print(f"Scored accuracy: {status} {fmt_pct(accuracy)} ({len(scored)} scored)")

    for prediction in pending:
        print(
            f"- pending {prediction['prediction_id']}: score on "
            f"{prediction['scoring_date']}"
        )


def main() -> None:
    validation = validate_all()
    if validation.errors:
        print("Data validation failed:", file=sys.stderr)
        for error in validation.errors:
            print(f"- {error}", file=sys.stderr)
        raise SystemExit(1)

    for warning in validation.warnings:
        print(f"Data validation warning: {warning}", file=sys.stderr)

    signals = load_json("signals.json")
    decisions = load_json("decisions.json")
    releases = load_json("releases.json")
    cohorts = load_json("cohort_outcomes.json")
    predictions = load_json("predictions.json")

    print("Decision Spine KPI Report")
    print(f"Generated: {TODAY.isoformat()}")
    report_signal_strength(signals)
    report_signal_to_decision(signals, decisions)
    report_decision_to_release(decisions, releases)
    report_changes_per_quarter(releases)
    report_outcome_deltas(cohorts)
    report_prediction_accuracy(predictions)


if __name__ == "__main__":
    main()
