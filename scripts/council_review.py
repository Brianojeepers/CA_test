#!/usr/bin/env python3
"""Print an action-focused Decision Spine council review."""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path
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


def fmt_days(value: int | None) -> str:
    return "n/a" if value is None else f"{value}d"


def print_section(title: str) -> None:
    print(f"\n{title}")
    print("-" * len(title))


def signal_to_decision_status(days: int | None) -> str:
    if days is None:
        return "red"
    if days <= 21:
        return "green"
    if days <= 45:
        return "amber"
    return "red"


def decision_to_release_status(days: int | None, complexity: str) -> str:
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


def validate_or_exit() -> None:
    validation = validate_all()
    if validation.errors:
        print("Data validation failed:", file=sys.stderr)
        for error in validation.errors:
            print(f"- {error}", file=sys.stderr)
        raise SystemExit(1)
    for warning in validation.warnings:
        print(f"Data validation warning: {warning}", file=sys.stderr)


def report_decisions_needed(
    signals: list[dict[str, Any]], decisions: list[dict[str, Any]]
) -> None:
    print_section("Decisions Needed")
    decisions_by_signal: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for decision in decisions:
        for signal_id in decision["signal_ids"]:
            decisions_by_signal[signal_id].append(decision)

    action_items: list[str] = []
    watch_items: list[str] = []

    for signal in sorted(signals, key=lambda item: item["signal_strength_score"], reverse=True):
        linked_decisions = decisions_by_signal.get(signal["signal_id"], [])
        if signal["status"] == "green" and not linked_decisions:
            action_items.append(
                f"- red {signal['signal_id']}: no decision logged | "
                f"owner=Signal Intelligence Council | action=assign decision owner"
            )
            continue

        if signal["status"] == "green" and linked_decisions:
            first_decision = min(linked_decisions, key=lambda item: item["decision_signed_date"])
            elapsed_days = days_between(
                signal["green_threshold_date"], first_decision["decision_signed_date"]
            )
            status = signal_to_decision_status(elapsed_days)
            if status in {"amber", "red"}:
                action_items.append(
                    f"- {status} {signal['signal_id']} -> {first_decision['decision_id']}: "
                    f"{fmt_days(elapsed_days)} | owner={first_decision['owner']} | "
                    "action=review stalled decision path"
                )

        if signal["status"] == "amber":
            watch_items.append(
                f"- monitor {signal['signal_id']}: {signal['signal_theme']} | "
                f"confidence={signal['confidence']} | action=gather evidence"
            )

    if action_items:
        for item in action_items:
            print(item)
    else:
        print("- none")

    if watch_items:
        print("\nWatchlist")
        for item in watch_items:
            print(item)


def report_release_queue(decisions: list[dict[str, Any]], releases: list[dict[str, Any]]) -> None:
    print_section("Release Accountability")
    releases_by_decision: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for release in releases:
        releases_by_decision[release["decision_id"]].append(release)

    items: list[str] = []
    for decision in decisions:
        if decision["decision_status"] != "approved":
            continue

        linked_releases = releases_by_decision.get(decision["decision_id"], [])
        if not linked_releases:
            items.append(
                f"- red {decision['decision_id']}: no release logged | "
                f"owner={decision['owner']} | action=create release record"
            )
            continue

        for release in linked_releases:
            elapsed_days = days_between(decision["decision_signed_date"], release["release_date"])
            status = decision_to_release_status(elapsed_days, decision["complexity_tier"])
            if status in {"pending", "amber", "red"}:
                target = release["release_date"] or "not released"
                items.append(
                    f"- {status} {decision['decision_id']} -> {release['release_id']}: "
                    f"{fmt_days(elapsed_days)} ({decision['complexity_tier']}, {target}) | "
                    f"owner={decision['owner']} | artifact={release['artifact']}"
                )

    if items:
        for item in items:
            print(item)
    else:
        print("- none")


def report_traceability(decisions: list[dict[str, Any]], releases: list[dict[str, Any]]) -> None:
    print_section("Traceability Checks")
    decisions_by_id = {decision["decision_id"]: decision for decision in decisions}
    items: list[str] = []

    for release in releases:
        decision = decisions_by_id.get(release["decision_id"])
        if decision is None:
            items.append(f"- red {release['release_id']}: missing decision")
            continue

        decision_signals = set(decision["signal_ids"])
        release_signals = set(release["linked_signal_ids"])
        if not release["market_traceable"]:
            items.append(f"- red {release['release_id']}: market_traceable=false")
        if release_signals != decision_signals:
            items.append(
                f"- amber {release['release_id']}: release signals "
                f"{sorted(release_signals)} differ from decision signals {sorted(decision_signals)}"
            )

    if items:
        for item in items:
            print(item)
    else:
        print("- all releases trace to their decision evidence")


def report_prediction_followups(predictions: list[dict[str, Any]]) -> None:
    print_section("Prediction Follow-Ups")
    pending = []
    review = []
    for prediction in predictions:
        scoring_date = parse_date(prediction["scoring_date"])
        if prediction["outcome"] == "pending" and scoring_date and scoring_date <= TODAY:
            review.append(
                f"- red {prediction['prediction_id']}: scoring date passed "
                f"({prediction['scoring_date']}) | action=score prediction"
            )
        elif prediction["outcome"] == "pending":
            pending.append(
                f"- pending {prediction['prediction_id']}: score on {prediction['scoring_date']} | "
                f"claim={prediction['claim']}"
            )

    if review:
        for item in review:
            print(item)
    if pending:
        for item in pending:
            print(item)
    if not review and not pending:
        print("- none")


def main() -> None:
    validate_or_exit()
    signals = load_json("signals.json")
    decisions = load_json("decisions.json")
    releases = load_json("releases.json")
    predictions = load_json("predictions.json")

    print("Decision Spine Council Review")
    print(f"Generated: {TODAY.isoformat()}")
    report_decisions_needed(signals, decisions)
    report_release_queue(decisions, releases)
    report_traceability(decisions, releases)
    report_prediction_followups(predictions)


if __name__ == "__main__":
    main()
