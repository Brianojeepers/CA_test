#!/usr/bin/env python3
"""Print a concise monthly Decision Spine council packet with drill-down paths."""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
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


def fmt_days(value: int | None) -> str:
    return "n/a" if value is None else f"{value}d"


def fmt_pct(value: float | None) -> str:
    return "n/a" if value is None else f"{value * 100:.1f}%"


def print_section(title: str, drill_down: str) -> None:
    print(f"\n{title}")
    print("-" * len(title))
    print(f"Drill-down: {drill_down}")


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


def validate_or_exit() -> list[str]:
    validation = validate_all()
    if validation.errors:
        print("Data validation failed:", file=sys.stderr)
        for error in validation.errors:
            print(f"- {error}", file=sys.stderr)
        raise SystemExit(1)
    return validation.warnings


def signal_bucket(signal: dict[str, Any], decisions: list[dict[str, Any]]) -> str:
    if signal["status"] == "green" and not decisions:
        return "act_now"
    if signal["status"] == "green":
        return "act_tracked"
    if signal["status"] == "amber":
        return "monitor"
    return "do_not_act"


def summarize_validation(warnings: list[str]) -> None:
    print_section("Data Trust", "python3 scripts/validate_data.py")
    if warnings:
        print(f"- passed with {len(warnings)} warning(s)")
        for warning in warnings[:3]:
            print(f"- warning: {warning}")
    else:
        print("- passed with no warnings")


def summarize_kpis(
    signals: list[dict[str, Any]],
    decisions: list[dict[str, Any]],
    releases: list[dict[str, Any]],
    cohorts: list[dict[str, Any]],
    predictions: list[dict[str, Any]],
) -> None:
    print_section("KPI Posture", "python3 scripts/report_kpis.py")
    signal_avg = mean(signal["signal_strength_score"] for signal in signals)
    signal_counts = Counter(signal["status"] for signal in signals)
    print(
        f"- K1 signal strength: avg={signal_avg:.1f} "
        f"green={signal_counts['green']} amber={signal_counts['amber']} red={signal_counts['red']}"
    )

    decisions_by_signal: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for decision in decisions:
        for signal_id in decision["signal_ids"]:
            decisions_by_signal[signal_id].append(decision)
    k2_counts: Counter[str] = Counter()
    for signal in signals:
        if signal["status"] != "green":
            continue
        linked_decisions = decisions_by_signal.get(signal["signal_id"], [])
        if not linked_decisions:
            k2_counts["red"] += 1
            continue
        first_decision = min(linked_decisions, key=lambda item: item["decision_signed_date"])
        elapsed = days_between(signal["green_threshold_date"], first_decision["decision_signed_date"])
        k2_counts[signal_to_decision_status(elapsed)] += 1
    print(f"- K2 signal-to-decision: {dict(k2_counts)}")

    decisions_by_id = {decision["decision_id"]: decision for decision in decisions}
    k3_counts: Counter[str] = Counter()
    for release in releases:
        decision = decisions_by_id[release["decision_id"]]
        elapsed = days_between(decision["decision_signed_date"], release["release_date"])
        k3_counts[decision_to_release_status(elapsed, decision["complexity_tier"])] += 1
    print(f"- K3 decision-to-release: {dict(k3_counts)}")

    scored = [
        prediction
        for prediction in predictions
        if parse_date(prediction["scoring_date"]) <= TODAY
        and prediction["outcome"] in {"confirmed", "contradicted"}
    ]
    accuracy = None
    if scored:
        accuracy = sum(item["accuracy_score"] for item in scored) / len(scored)
    print(f"- K7 prediction accuracy: {fmt_pct(accuracy)} ({len(scored)} scored)")

    post_change_pending = sum(
        1
        for cohort in cohorts
        if cohort["change_exposure"] == "post_change"
        and (cohort["placement_rate"] is None or cohort["retention_90d_rate"] is None)
    )
    print(f"- Outcome data pending for {post_change_pending} post-change cohort(s)")


def summarize_signals(signals: list[dict[str, Any]], decisions: list[dict[str, Any]]) -> None:
    print_section("Signal Posture", "python3 scripts/signal_review.py")
    decisions_by_signal: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for decision in decisions:
        for signal_id in decision["signal_ids"]:
            decisions_by_signal[signal_id].append(decision)

    counts: Counter[str] = Counter()
    for signal in signals:
        counts[signal_bucket(signal, decisions_by_signal.get(signal["signal_id"], []))] += 1

    print(
        f"- act_now={counts['act_now']} act_tracked={counts['act_tracked']} "
        f"monitor={counts['monitor']} do_not_act={counts['do_not_act']}"
    )
    top = max(signals, key=lambda item: item["signal_strength_score"])
    print(f"- strongest signal: {top['signal_id']} {top['signal_theme']} ({top['signal_strength_score']})")


def summarize_decisions_needed(
    signals: list[dict[str, Any]],
    decisions: list[dict[str, Any]],
    releases: list[dict[str, Any]],
) -> None:
    print_section("Decisions Needed This Month", "python3 scripts/council_review.py")
    decisions_by_signal: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for decision in decisions:
        for signal_id in decision["signal_ids"]:
            decisions_by_signal[signal_id].append(decision)

    items: list[str] = []
    for signal in signals:
        linked_decisions = decisions_by_signal.get(signal["signal_id"], [])
        if signal["status"] == "green" and not linked_decisions:
            items.append(f"- assign decision owner for {signal['signal_id']} {signal['signal_theme']}")
        elif signal["status"] == "green" and linked_decisions:
            first_decision = min(linked_decisions, key=lambda item: item["decision_signed_date"])
            elapsed = days_between(signal["green_threshold_date"], first_decision["decision_signed_date"])
            status = signal_to_decision_status(elapsed)
            if status in {"amber", "red"}:
                items.append(
                    f"- review {signal['signal_id']} -> {first_decision['decision_id']} "
                    f"({status}, {fmt_days(elapsed)}, owner={first_decision['owner']})"
                )

    releases_by_decision: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for release in releases:
        releases_by_decision[release["decision_id"]].append(release)

    for decision in decisions:
        if decision["decision_status"] != "approved":
            continue
        linked_releases = releases_by_decision.get(decision["decision_id"], [])
        if not linked_releases:
            items.append(f"- create release record for {decision['decision_id']} owner={decision['owner']}")
        for release in linked_releases:
            elapsed = days_between(decision["decision_signed_date"], release["release_date"])
            status = decision_to_release_status(elapsed, decision["complexity_tier"])
            if status in {"pending", "red"}:
                items.append(
                    f"- unblock {decision['decision_id']} -> {release['release_id']} "
                    f"({status}, owner={decision['owner']}, artifact={release['artifact']})"
                )

    if items:
        for item in items[:6]:
            print(item)
    else:
        print("- none")


def summarize_credential_and_learning(
    decisions: list[dict[str, Any]], releases: list[dict[str, Any]]
) -> None:
    print_section("Credential And Learning Work", "python3 scripts/credential_requirements.py && python3 scripts/learning_outcomes.py")
    releases_by_decision: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for release in releases:
        releases_by_decision[release["decision_id"]].append(release)

    credential_actions = [item for item in decisions if item["decision_type"] in {"credential", "assessment"}]
    curriculum_actions = [item for item in decisions if item["decision_type"] == "curriculum"]
    monitor_actions = [item for item in decisions if item["decision_type"] == "monitor" or item["decision_status"] == "watch"]
    pending_requirement = sum(
        1
        for decision in credential_actions
        if not releases_by_decision.get(decision["decision_id"])
        or any(release["release_status"] != "released" for release in releases_by_decision[decision["decision_id"]])
    )
    print(f"- credential/assessment actions: {len(credential_actions)} ({pending_requirement} pending)")
    print(f"- curriculum actions: {len(curriculum_actions)}")
    print(f"- monitor/do-not-add decisions: {len(monitor_actions)}")


def summarize_predictions(predictions: list[dict[str, Any]]) -> None:
    print_section("Prediction Follow-Ups", "python3 scripts/council_review.py")
    pending = [item for item in predictions if item["outcome"] == "pending"]
    overdue = [
        item
        for item in pending
        if parse_date(item["scoring_date"]) and parse_date(item["scoring_date"]) <= TODAY
    ]
    print(f"- pending={len(pending)} overdue={len(overdue)}")
    for prediction in sorted(pending, key=lambda item: item["scoring_date"])[:3]:
        print(f"- next: {prediction['prediction_id']} score on {prediction['scoring_date']}")


def main() -> None:
    warnings = validate_or_exit()
    signals = load_json("signals.json")
    decisions = load_json("decisions.json")
    releases = load_json("releases.json")
    cohorts = load_json("cohort_outcomes.json")
    predictions = load_json("predictions.json")

    print("Decision Spine Monthly Packet")
    print(f"Generated: {TODAY.isoformat()}")
    summarize_validation(warnings)
    summarize_kpis(signals, decisions, releases, cohorts, predictions)
    summarize_signals(signals, decisions)
    summarize_decisions_needed(signals, decisions, releases)
    summarize_credential_and_learning(decisions, releases)
    summarize_predictions(predictions)


if __name__ == "__main__":
    main()
