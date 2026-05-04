#!/usr/bin/env python3
"""Print a signal-to-action review for the Decision Spine MVP."""

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


def action_for_signal(signal: dict[str, Any], decisions: list[dict[str, Any]]) -> str:
    if signal["status"] == "green" and not decisions:
        return "act now"
    if signal["status"] == "green":
        return "act tracked"
    if signal["status"] == "amber":
        return "monitor"
    return "do not act"


def next_step_for_signal(signal: dict[str, Any], decisions: list[dict[str, Any]]) -> str:
    if signal["status"] == "green" and not decisions:
        return "assign council decision owner"
    if signal["status"] == "amber":
        return "gather stronger evidence before changing curriculum or credentialing"
    if signal["status"] == "red":
        return "do not create new requirement unless signal cluster escalates"

    open_releases = []
    for decision in decisions:
        releases = decision.get("_releases", [])
        if decision["decision_status"] == "approved" and not releases:
            open_releases.append("create release record")
        for release in releases:
            if release["release_status"] != "released":
                open_releases.append(f"finish {release['artifact']}")

    if open_releases:
        return "; ".join(open_releases)
    return "review outcome evidence as cohorts mature"


def implication_for_decision_type(decision_type: str) -> str:
    if decision_type == "curriculum":
        return "learning outcome change"
    if decision_type == "credential":
        return "credential evidence threshold"
    if decision_type == "assessment":
        return "assessment or simulation criterion"
    if decision_type == "monitor":
        return "no requirement yet"
    return "governance review"


def report_signal(signal: dict[str, Any], decisions: list[dict[str, Any]]) -> None:
    action = action_for_signal(signal, decisions)
    next_step = next_step_for_signal(signal, decisions)
    print(
        f"- {signal['signal_id']} [{action}] {signal['signal_theme']} "
        f"({signal['role_archetype']}, {signal['horizon_window']})"
    )
    print(
        f"  score={signal['signal_strength_score']} status={signal['status']} "
        f"confidence={signal['confidence']} segment={signal['client_segment']} geography={signal['geography']}"
    )
    print(f"  evidence={signal['summary']}")
    print(f"  next_step={next_step}")

    if not decisions:
        print("  decision=none")
        return

    for decision in decisions:
        implication = implication_for_decision_type(decision["decision_type"])
        print(
            f"  decision={decision['decision_id']} {decision['decision_status']} "
            f"type={decision['decision_type']} implication={implication} owner={decision['owner']}"
        )
        print(f"  rationale={decision['rationale']}")
        releases = decision.get("_releases", [])
        if not releases:
            print("  release=none")
        for release in releases:
            release_date = release["release_date"] or "not released"
            print(
                f"  release={release['release_id']} {release['release_status']} "
                f"{release['artifact']} ({release_date})"
            )


def main() -> None:
    validate_or_exit()
    signals = load_json("signals.json")
    decisions = load_json("decisions.json")
    releases = load_json("releases.json")

    decisions_by_signal: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for decision in decisions:
        for signal_id in decision["signal_ids"]:
            decisions_by_signal[signal_id].append(decision)

    releases_by_decision: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for release in releases:
        releases_by_decision[release["decision_id"]].append(release)

    for decision in decisions:
        decision["_releases"] = releases_by_decision.get(decision["decision_id"], [])

    print("Decision Spine Signal Review")
    print(f"Generated: {TODAY.isoformat()}")

    buckets = [
        ("Act Now", lambda signal: action_for_signal(signal, decisions_by_signal.get(signal["signal_id"], [])) == "act now"),
        ("Act Tracked", lambda signal: action_for_signal(signal, decisions_by_signal.get(signal["signal_id"], [])) == "act tracked"),
        ("Monitor", lambda signal: action_for_signal(signal, decisions_by_signal.get(signal["signal_id"], [])) == "monitor"),
        ("Do Not Act", lambda signal: action_for_signal(signal, decisions_by_signal.get(signal["signal_id"], [])) == "do not act"),
    ]

    sorted_signals = sorted(signals, key=lambda item: item["signal_strength_score"], reverse=True)
    for title, predicate in buckets:
        print_section(title)
        bucket_signals = [signal for signal in sorted_signals if predicate(signal)]
        if not bucket_signals:
            print("- none")
            continue
        for signal in bucket_signals:
            report_signal(signal, decisions_by_signal.get(signal["signal_id"], []))


if __name__ == "__main__":
    main()
