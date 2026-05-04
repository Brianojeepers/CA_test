#!/usr/bin/env python3
"""Print credential and assessment requirement actions from Decision Spine data."""

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


def requirement_label(decision_type: str) -> str:
    if decision_type == "credential":
        return "credential evidence threshold"
    if decision_type == "assessment":
        return "assessment criterion"
    return "not a credential requirement"


def release_summary(releases: list[dict[str, Any]]) -> str:
    if not releases:
        return "release=none"
    parts = []
    for release in releases:
        release_date = release["release_date"] or "not released"
        parts.append(
            f"{release['release_id']} {release['release_status']} "
            f"{release['artifact']} ({release_date})"
        )
    return "release=" + "; ".join(parts)


def signal_summary(signals: list[dict[str, Any]]) -> str:
    return "; ".join(
        f"{signal['signal_id']} {signal['signal_theme']} "
        f"[{signal['status']} {signal['signal_strength_score']}, {signal['confidence']}]"
        for signal in signals
    )


def report_requirement_actions(
    decisions: list[dict[str, Any]],
    signals_by_id: dict[str, dict[str, Any]],
    releases_by_decision: dict[str, list[dict[str, Any]]],
) -> None:
    print_section("Credential And Assessment Actions")
    action_decisions = [
        decision
        for decision in decisions
        if decision["decision_type"] in {"credential", "assessment"}
    ]
    if not action_decisions:
        print("- none")
        return

    for decision in action_decisions:
        linked_signals = [signals_by_id[signal_id] for signal_id in decision["signal_ids"]]
        releases = releases_by_decision.get(decision["decision_id"], [])
        release_state = "pending" if not releases or any(item["release_status"] != "released" for item in releases) else "released"
        print(
            f"- {decision['decision_id']} [{release_state}] {requirement_label(decision['decision_type'])} | "
            f"owner={decision['owner']} | complexity={decision['complexity_tier']}"
        )
        print(f"  requirement={decision['decision_summary']}")
        print(f"  evidence={signal_summary(linked_signals)}")
        print(f"  rationale={decision['rationale']}")
        print(f"  {release_summary(releases)}")
        if release_state == "pending":
            print("  next_step=finish or schedule requirement release")
        else:
            print("  next_step=monitor placement and retention outcomes")


def report_non_requirements(
    decisions: list[dict[str, Any]], signals_by_id: dict[str, dict[str, Any]]
) -> None:
    print_section("Monitor Or Exclude From Requirements")
    monitor_decisions = [
        decision
        for decision in decisions
        if decision["decision_type"] == "monitor" or decision["decision_status"] in {"watch", "rejected", "deferred"}
    ]
    if not monitor_decisions:
        print("- none")
        return

    for decision in monitor_decisions:
        linked_signals = [signals_by_id[signal_id] for signal_id in decision["signal_ids"]]
        print(
            f"- {decision['decision_id']} [{decision['decision_status']}] "
            f"owner={decision['owner']} | action=do not create requirement yet"
        )
        print(f"  signal={signal_summary(linked_signals)}")
        print(f"  rationale={decision['rationale']}")


def report_unresolved_green_signals(
    signals: list[dict[str, Any]], decisions_by_signal: dict[str, list[dict[str, Any]]]
) -> None:
    print_section("Green Signals Without Requirement Decision")
    items = []
    for signal in signals:
        decisions = decisions_by_signal.get(signal["signal_id"], [])
        has_requirement_decision = any(
            decision["decision_type"] in {"credential", "assessment", "monitor"}
            for decision in decisions
        )
        if signal["status"] == "green" and not has_requirement_decision:
            items.append(
                f"- {signal['signal_id']} {signal['signal_theme']} | "
                f"archetype={signal['role_archetype']} | action=decide if credential evidence is needed"
            )
    if items:
        for item in items:
            print(item)
    else:
        print("- none")


def main() -> None:
    validate_or_exit()
    signals = load_json("signals.json")
    decisions = load_json("decisions.json")
    releases = load_json("releases.json")

    signals_by_id = {signal["signal_id"]: signal for signal in signals}
    releases_by_decision: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for release in releases:
        releases_by_decision[release["decision_id"]].append(release)

    decisions_by_signal: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for decision in decisions:
        for signal_id in decision["signal_ids"]:
            decisions_by_signal[signal_id].append(decision)

    print("Decision Spine Credential Requirements")
    print(f"Generated: {TODAY.isoformat()}")
    report_requirement_actions(decisions, signals_by_id, releases_by_decision)
    report_non_requirements(decisions, signals_by_id)
    report_unresolved_green_signals(signals, decisions_by_signal)


if __name__ == "__main__":
    main()
