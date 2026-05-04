#!/usr/bin/env python3
"""Print learning outcome actions from Decision Spine data."""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from datetime import date
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
    return "n/a" if value is None else f"{value * 100:.1f}%"


def fmt_pp(value: float | None) -> str:
    return "n/a" if value is None else f"{value * 100:+.1f}pp"


def signal_summary(signals: list[dict[str, Any]]) -> str:
    return "; ".join(
        f"{signal['signal_id']} {signal['signal_theme']} "
        f"[{signal['status']} {signal['signal_strength_score']}, {signal['confidence']}]"
        for signal in signals
    )


def outcome_summary(cohort: dict[str, Any] | None, cohorts: list[dict[str, Any]]) -> str:
    if cohort is None:
        return "outcome=future cohort / no outcomes yet"

    baseline = [
        item
        for item in cohorts
        if item["baseline_group"] == cohort["baseline_group"]
        and item["change_exposure"] == "pre_change"
    ]
    placement_baseline = [
        item["placement_rate"] for item in baseline if item["placement_rate"] is not None
    ]
    retention_baseline = [
        item["retention_90d_rate"] for item in baseline if item["retention_90d_rate"] is not None
    ]

    placement_delta = None
    if cohort["placement_rate"] is not None and placement_baseline:
        placement_delta = cohort["placement_rate"] - mean(placement_baseline)

    retention_delta = None
    if cohort["retention_90d_rate"] is not None and retention_baseline:
        retention_delta = cohort["retention_90d_rate"] - mean(retention_baseline)

    notes = []
    if cohort["eligible_for_placement"] < 25:
        notes.append("small-n")
    if cohort["placement_rate"] is None:
        notes.append("placement pending")
    if cohort["retention_90d_rate"] is None:
        notes.append("retention pending")
    note = f" ({', '.join(notes)})" if notes else ""

    return (
        f"outcome={cohort['cohort_id']}{note}: "
        f"placement {fmt_pct(cohort['placement_rate'])} delta {fmt_pp(placement_delta)}; "
        f"retention {fmt_pct(cohort['retention_90d_rate'])} delta {fmt_pp(retention_delta)}"
    )


def report_learning_changes(
    decisions: list[dict[str, Any]],
    signals_by_id: dict[str, dict[str, Any]],
    releases_by_decision: dict[str, list[dict[str, Any]]],
    cohorts_by_id: dict[str, dict[str, Any]],
    cohorts: list[dict[str, Any]],
) -> None:
    print_section("Learning Outcome Changes")
    curriculum_decisions = [
        decision for decision in decisions if decision["decision_type"] == "curriculum"
    ]
    if not curriculum_decisions:
        print("- none")
        return

    for decision in curriculum_decisions:
        linked_signals = [signals_by_id[signal_id] for signal_id in decision["signal_ids"]]
        releases = releases_by_decision.get(decision["decision_id"], [])
        release_state = "pending" if not releases or any(item["release_status"] != "released" for item in releases) else "released"
        print(
            f"- {decision['decision_id']} [{release_state}] owner={decision['owner']} "
            f"complexity={decision['complexity_tier']}"
        )
        print(f"  change={decision['decision_summary']}")
        print(f"  evidence={signal_summary(linked_signals)}")
        print(f"  rationale={decision['rationale']}")
        if not releases:
            print("  release=none")
            print("  next_step=create release record")
            continue

        for release in releases:
            release_date = release["release_date"] or "not released"
            cohort = cohorts_by_id.get(release["cohort_id"])
            print(
                f"  release={release['release_id']} {release['release_status']} "
                f"{release['programme']} | {release['artifact']} ({release_date})"
            )
            print(f"  {outcome_summary(cohort, cohorts)}")

        if release_state == "pending":
            print("  next_step=finish or schedule learning release")
        else:
            print("  next_step=review outcome evidence as cohorts mature")


def report_monitor_items(
    decisions: list[dict[str, Any]], signals_by_id: dict[str, dict[str, Any]]
) -> None:
    print_section("Do Not Add Yet")
    monitor_decisions = [
        decision
        for decision in decisions
        if decision["decision_type"] == "monitor" or decision["decision_status"] == "watch"
    ]
    if not monitor_decisions:
        print("- none")
        return

    for decision in monitor_decisions:
        linked_signals = [signals_by_id[signal_id] for signal_id in decision["signal_ids"]]
        print(
            f"- {decision['decision_id']} [{decision['decision_status']}] "
            f"owner={decision['owner']} | action=monitor, do not add module yet"
        )
        print(f"  signal={signal_summary(linked_signals)}")
        print(f"  rationale={decision['rationale']}")


def report_non_curriculum_decisions(decisions: list[dict[str, Any]]) -> None:
    print_section("Non-Curriculum Decisions")
    items = [
        decision
        for decision in decisions
        if decision["decision_type"] not in {"curriculum", "monitor"}
    ]
    if not items:
        print("- none")
        return
    for decision in items:
        print(
            f"- {decision['decision_id']} type={decision['decision_type']} "
            f"owner={decision['owner']} | route=Assessment Ops or council review"
        )


def main() -> None:
    validate_or_exit()
    signals = load_json("signals.json")
    decisions = load_json("decisions.json")
    releases = load_json("releases.json")
    cohorts = load_json("cohort_outcomes.json")

    signals_by_id = {signal["signal_id"]: signal for signal in signals}
    cohorts_by_id = {cohort["cohort_id"]: cohort for cohort in cohorts}
    releases_by_decision: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for release in releases:
        releases_by_decision[release["decision_id"]].append(release)

    print("Decision Spine Learning Outcomes")
    print(f"Generated: {TODAY.isoformat()}")
    report_learning_changes(decisions, signals_by_id, releases_by_decision, cohorts_by_id, cohorts)
    report_monitor_items(decisions, signals_by_id)
    report_non_curriculum_decisions(decisions)


if __name__ == "__main__":
    main()
