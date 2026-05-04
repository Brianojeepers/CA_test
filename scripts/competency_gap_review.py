#!/usr/bin/env python3
"""Print role competency coverage and early gap hypotheses."""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any

from validate_data import validate_all


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


def report_summary(competencies: list[dict[str, Any]]) -> None:
    print_section("Competency Summary")
    by_role = Counter(item["role_archetype"] for item in competencies)
    by_priority = Counter(item["market_priority"] for item in competencies)
    by_status = Counter(item["status"] for item in competencies)
    print(f"- competencies={len(competencies)}")
    print("- roles=" + ", ".join(f"{role}:{count}" for role, count in sorted(by_role.items())))
    print(
        "- priority="
        + ", ".join(f"{priority}:{by_priority[priority]}" for priority in ("core", "emerging", "monitor"))
    )
    print("- status=" + ", ".join(f"{status}:{count}" for status, count in sorted(by_status.items())))


def report_by_role(
    competencies_by_role: dict[str, list[dict[str, Any]]],
    signals_by_id: dict[str, dict[str, Any]],
) -> None:
    print_section("Role Competency Map")
    for role in sorted(competencies_by_role):
        print(f"- {role}")
        for item in sorted(competencies_by_role[role], key=lambda value: value["competency_id"]):
            signal_text = "; ".join(
                f"{signal_id} {signals_by_id[signal_id]['signal_theme']}" for signal_id in item["linked_signal_ids"]
            )
            release_text = ", ".join(item["linked_release_ids"]) or "none"
            pedagogy_text = ", ".join(item["pedagogy_ids"]) or "none"
            print(
                f"  - {item['competency_id']} [{item['market_priority']}, {item['status']}] "
                f"{item['competency_cluster']}"
            )
            print(f"    capability={item['capability']}")
            print(f"    proficiency={item['target_proficiency']} | horizon={item['horizon_window']}")
            print(f"    signals={signal_text}")
            print(f"    releases={release_text} | pedagogy={pedagogy_text}")
            print(f"    evidence={item['assessment_signal']}")
            print(f"    gap={item['gap_hypothesis']}")


def report_active_gaps(competencies: list[dict[str, Any]]) -> None:
    print_section("Active Gap Hypotheses")
    items = [
        item
        for item in competencies
        if item["status"] == "active" and item["market_priority"] in {"core", "emerging"}
    ]
    if not items:
        print("- none")
        return
    for item in sorted(items, key=lambda value: (value["role_archetype"], value["competency_id"])):
        print(
            f"- {item['competency_id']} {item['role_archetype']} | "
            f"owner={item['owner']} | hypothesis={item['gap_hypothesis']}"
        )


def report_monitor_items(competencies: list[dict[str, Any]]) -> None:
    print_section("Monitor Competencies")
    items = [item for item in competencies if item["market_priority"] == "monitor" or item["status"] == "monitor"]
    if not items:
        print("- none")
        return
    for item in sorted(items, key=lambda value: value["competency_id"]):
        print(
            f"- {item['competency_id']} {item['role_archetype']} | "
            f"signals={', '.join(item['linked_signal_ids'])} | action=keep out of standalone credential until pull improves"
        )


def report_signal_coverage(
    signals: list[dict[str, Any]],
    competencies_by_signal: dict[str, list[dict[str, Any]]],
) -> None:
    print_section("Signal Coverage")
    for signal in signals:
        linked = competencies_by_signal.get(signal["signal_id"], [])
        if linked:
            ids = ", ".join(item["competency_id"] for item in linked)
            print(f"- {signal['signal_id']} {signal['status']} -> {ids}")
            continue
        action = "acceptable: weak/red signal has no competency target"
        if signal["status"] == "green":
            action = "gap: green signal needs competency target"
        print(f"- {signal['signal_id']} {signal['status']} -> none | {action}")


def main() -> None:
    validate_or_exit()
    competencies = load_json("role_competencies.json")
    signals = load_json("signals.json")

    signals_by_id = {signal["signal_id"]: signal for signal in signals}
    competencies_by_role: dict[str, list[dict[str, Any]]] = defaultdict(list)
    competencies_by_signal: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for item in competencies:
        competencies_by_role[item["role_archetype"]].append(item)
        for signal_id in item["linked_signal_ids"]:
            competencies_by_signal[signal_id].append(item)

    print("Decision Spine Competency Gap Review")
    print(f"Generated: {TODAY.isoformat()}")
    print("Reference: docs/competency_ontology.md")
    report_summary(competencies)
    report_by_role(competencies_by_role, signals_by_id)
    report_active_gaps(competencies)
    report_monitor_items(competencies)
    report_signal_coverage(signals, competencies_by_signal)


if __name__ == "__main__":
    main()
