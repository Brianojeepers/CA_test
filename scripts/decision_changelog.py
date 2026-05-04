#!/usr/bin/env python3
"""Print stakeholder-facing Decision Spine change history."""

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


def signal_themes(signals: list[dict[str, Any]]) -> str:
    return "; ".join(f"{signal['signal_id']} {signal['signal_theme']}" for signal in signals)


def why_it_matters(decision: dict[str, Any], signals: list[dict[str, Any]]) -> str:
    if decision.get("rationale"):
        return decision["rationale"]
    return " ".join(signal["summary"] for signal in signals)


def print_release_item(
    release: dict[str, Any],
    decision: dict[str, Any],
    signals: list[dict[str, Any]],
) -> None:
    release_date = release["release_date"] or "pending"
    print(
        f"- {release['release_id']} {release['release_status']} | "
        f"{release['programme']} | {release['artifact']} ({release_date})"
    )
    print(
        f"  decision={decision['decision_id']} type={decision['decision_type']} "
        f"owner={decision['owner']}"
    )
    print(f"  change={decision['decision_summary']}")
    print(f"  evidence={signal_themes(signals)}")
    print(f"  why={why_it_matters(decision, signals)}")
    print("  drill_down=python3 scripts/council_review.py")


def report_released(
    releases: list[dict[str, Any]],
    decisions_by_id: dict[str, dict[str, Any]],
    signals_by_id: dict[str, dict[str, Any]],
) -> None:
    print_section("Released Changes")
    released = [release for release in releases if release["release_status"] == "released"]
    if not released:
        print("- none")
        return
    for release in sorted(released, key=lambda item: item["release_date"] or ""):
        decision = decisions_by_id[release["decision_id"]]
        signals = [signals_by_id[signal_id] for signal_id in release["linked_signal_ids"]]
        print_release_item(release, decision, signals)


def report_pending(
    releases: list[dict[str, Any]],
    decisions_by_id: dict[str, dict[str, Any]],
    signals_by_id: dict[str, dict[str, Any]],
) -> None:
    print_section("Pending Changes")
    pending = [release for release in releases if release["release_status"] != "released"]
    if not pending:
        print("- none")
        return
    for release in pending:
        decision = decisions_by_id[release["decision_id"]]
        signals = [signals_by_id[signal_id] for signal_id in release["linked_signal_ids"]]
        print_release_item(release, decision, signals)


def report_monitor_decisions(
    decisions: list[dict[str, Any]],
    signals_by_id: dict[str, dict[str, Any]],
) -> None:
    print_section("Monitor / No Change Decisions")
    monitor = [
        decision
        for decision in decisions
        if decision["decision_type"] == "monitor" or decision["decision_status"] in {"watch", "rejected", "deferred"}
    ]
    if not monitor:
        print("- none")
        return
    for decision in monitor:
        signals = [signals_by_id[signal_id] for signal_id in decision["signal_ids"]]
        print(
            f"- {decision['decision_id']} {decision['decision_status']} | "
            f"owner={decision['owner']}"
        )
        print(f"  decision={decision['decision_summary']}")
        print(f"  evidence={signal_themes(signals)}")
        print(f"  why={why_it_matters(decision, signals)}")
        print("  drill_down=python3 scripts/signal_review.py")


def report_decisions_without_releases(
    decisions: list[dict[str, Any]],
    releases_by_decision: dict[str, list[dict[str, Any]]],
    signals_by_id: dict[str, dict[str, Any]],
) -> None:
    print_section("Approved Decisions Without Release Record")
    items = [
        decision
        for decision in decisions
        if decision["decision_status"] == "approved"
        and not releases_by_decision.get(decision["decision_id"])
    ]
    if not items:
        print("- none")
        return
    for decision in items:
        signals = [signals_by_id[signal_id] for signal_id in decision["signal_ids"]]
        print(f"- {decision['decision_id']} owner={decision['owner']}")
        print(f"  change={decision['decision_summary']}")
        print(f"  evidence={signal_themes(signals)}")
        print("  next_step=create release record")


def main() -> None:
    validate_or_exit()
    signals = load_json("signals.json")
    decisions = load_json("decisions.json")
    releases = load_json("releases.json")

    signals_by_id = {signal["signal_id"]: signal for signal in signals}
    decisions_by_id = {decision["decision_id"]: decision for decision in decisions}
    releases_by_decision: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for release in releases:
        releases_by_decision[release["decision_id"]].append(release)

    print("Decision Spine Changelog")
    print(f"Generated: {TODAY.isoformat()}")
    print("Drill-down packet: python3 scripts/monthly_packet.py")
    report_released(releases, decisions_by_id, signals_by_id)
    report_pending(releases, decisions_by_id, signals_by_id)
    report_monitor_decisions(decisions, signals_by_id)
    report_decisions_without_releases(decisions, releases_by_decision, signals_by_id)


if __name__ == "__main__":
    main()
