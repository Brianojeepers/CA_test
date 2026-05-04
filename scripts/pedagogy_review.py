#!/usr/bin/env python3
"""Print pedagogical framing coverage for Decision Spine changes."""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path
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


def report_framed_changes(
    pedagogy: list[dict[str, Any]],
    decisions_by_id: dict[str, dict[str, Any]],
    releases_by_id: dict[str, dict[str, Any]],
    signals_by_id: dict[str, dict[str, Any]],
) -> None:
    print_section("Framed Changes")
    if not pedagogy:
        print("- none")
        return
    for item in pedagogy:
        decision = decisions_by_id[item["decision_id"]]
        release = releases_by_id[item["release_id"]]
        signals = [signals_by_id[signal_id] for signal_id in item["signal_ids"]]
        signal_text = "; ".join(f"{signal['signal_id']} {signal['signal_theme']}" for signal in signals)
        print(
            f"- {item['pedagogy_id']} -> {decision['decision_id']} "
            f"({decision['decision_type']}) | {release['artifact']}"
        )
        print(f"  capability={item['capability']}")
        print(f"  bloom={item['bloom_target']} | dreyfus={item['dreyfus_target']}")
        print(f"  context={item['performance_context']}")
        print(f"  evidence={item['assessment_evidence']}")
        print(f"  threshold={item['credential_threshold']}")
        print(f"  outcome_hypothesis={item['outcome_hypothesis']}")
        print(f"  signals={signal_text}")


def report_missing_framing(
    decisions: list[dict[str, Any]], pedagogy_by_decision: dict[str, list[dict[str, Any]]]
) -> None:
    print_section("Missing Or Deferred Framing")
    items = [
        decision
        for decision in decisions
        if decision["decision_type"] in {"curriculum", "credential", "assessment"}
        and not pedagogy_by_decision.get(decision["decision_id"])
    ]
    if not items:
        print("- none")
        return
    for decision in items:
        print(
            f"- {decision['decision_id']} {decision['decision_type']} | "
            f"owner={decision['owner']} | action=add pedagogy_map entry when labels are agreed"
        )


def report_monitor_items(decisions: list[dict[str, Any]]) -> None:
    print_section("Monitor Items Not Framed As Requirements")
    items = [decision for decision in decisions if decision["decision_type"] == "monitor"]
    if not items:
        print("- none")
        return
    for decision in items:
        print(
            f"- {decision['decision_id']} watch | owner={decision['owner']} | "
            "reason=not a standalone learning or credential requirement yet"
        )


def main() -> None:
    validate_or_exit()
    pedagogy = load_json("pedagogy_map.json")
    decisions = load_json("decisions.json")
    releases = load_json("releases.json")
    signals = load_json("signals.json")

    decisions_by_id = {decision["decision_id"]: decision for decision in decisions}
    releases_by_id = {release["release_id"]: release for release in releases}
    signals_by_id = {signal["signal_id"]: signal for signal in signals}
    pedagogy_by_decision: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in pedagogy:
        pedagogy_by_decision[item["decision_id"]].append(item)

    print("Decision Spine Pedagogy Review")
    print(f"Generated: {TODAY.isoformat()}")
    print("Reference: docs/pedagogical_framing.md")
    report_framed_changes(pedagogy, decisions_by_id, releases_by_id, signals_by_id)
    report_missing_framing(decisions, pedagogy_by_decision)
    report_monitor_items(decisions)


if __name__ == "__main__":
    main()
