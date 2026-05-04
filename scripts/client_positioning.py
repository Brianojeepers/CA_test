#!/usr/bin/env python3
"""Print Sales and Solutions positioning evidence from Decision Spine data."""

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


def fmt_pct(value: float | None) -> str:
    return "n/a" if value is None else f"{value * 100:.1f}%"


def release_summary(releases: list[dict[str, Any]]) -> str:
    if not releases:
        return "released_artifacts=none"
    released = [release for release in releases if release["release_status"] == "released"]
    if not released:
        return "released_artifacts=none yet"
    return "released_artifacts=" + "; ".join(
        f"{release['programme']} {release['artifact']}" for release in released
    )


def outcome_summary(releases: list[dict[str, Any]], cohorts_by_id: dict[str, dict[str, Any]]) -> str:
    parts = []
    for release in releases:
        cohort = cohorts_by_id.get(release["cohort_id"])
        if cohort is None:
            parts.append(f"{release['cohort_id']}: future cohort / no outcomes yet")
            continue
        notes = []
        if cohort["eligible_for_placement"] < 25:
            notes.append("small-n")
        if cohort["placement_rate"] is None:
            notes.append("placement pending")
        if cohort["retention_90d_rate"] is None:
            notes.append("retention pending")
        note = f" ({', '.join(notes)})" if notes else ""
        parts.append(
            f"{cohort['cohort_id']}{note}: placement={fmt_pct(cohort['placement_rate'])}, "
            f"retention={fmt_pct(cohort['retention_90d_rate'])}, confidence={cohort['data_confidence']}"
        )
    if not parts:
        return "outcomes=none"
    return "outcomes=" + "; ".join(parts)


def caveats_for(
    signals: list[dict[str, Any]], releases: list[dict[str, Any]], cohorts_by_id: dict[str, dict[str, Any]]
) -> list[str]:
    caveats = ["seed data is synthetic; do not use as real performance proof"]
    if any(signal["confidence"] == "low" or signal["status"] != "green" for signal in signals):
        caveats.append("market evidence is not fully validated")
    if not any(release["release_status"] == "released" for release in releases):
        caveats.append("no released artifact yet")
    for release in releases:
        cohort = cohorts_by_id.get(release["cohort_id"])
        if cohort is None:
            caveats.append("future cohort has no outcome data yet")
            continue
        if cohort["eligible_for_placement"] < 25:
            caveats.append("small-n cohort; directional only")
        if cohort["placement_rate"] is None or cohort["retention_90d_rate"] is None:
            caveats.append("placement or retention outcomes pending")
    return sorted(set(caveats))


def positioning_claim(signal: dict[str, Any], releases: list[dict[str, Any]]) -> str:
    if signal["status"] != "green":
        return "Do not position as a proven premium capability yet; monitor the signal."
    if not any(release["release_status"] == "released" for release in releases):
        return (
            f"Andela is preparing {signal['role_archetype']} capability around "
            f"{signal['signal_theme']}, with release evidence still pending."
        )
    return (
        f"Andela can position {signal['role_archetype']} talent around "
        f"{signal['signal_theme']} with market-traceable learning or credential evidence."
    )


def report_positioning(
    signals: list[dict[str, Any]],
    releases_by_signal: dict[str, list[dict[str, Any]]],
    cohorts_by_id: dict[str, dict[str, Any]],
) -> None:
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for signal in signals:
        grouped[(signal["role_archetype"], signal["client_segment"], signal["geography"])].append(signal)

    for (archetype, segment, geography), group_signals in sorted(grouped.items()):
        print_section(f"{archetype} | {segment} | {geography}")
        for signal in sorted(group_signals, key=lambda item: item["signal_strength_score"], reverse=True):
            releases = releases_by_signal.get(signal["signal_id"], [])
            print(
                f"- signal={signal['signal_id']} {signal['signal_theme']} "
                f"[{signal['status']} {signal['signal_strength_score']}, {signal['confidence']}]"
            )
            print(f"  claim={positioning_claim(signal, releases)}")
            print(f"  evidence={signal['summary']}")
            print(f"  {release_summary(releases)}")
            print(f"  {outcome_summary(releases, cohorts_by_id)}")
            print("  caveats=" + "; ".join(caveats_for([signal], releases, cohorts_by_id)))
            print("  drill_down=python3 scripts/signal_review.py")


def main() -> None:
    validate_or_exit()
    signals = load_json("signals.json")
    releases = load_json("releases.json")
    cohorts = load_json("cohort_outcomes.json")

    releases_by_signal: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for release in releases:
        for signal_id in release["linked_signal_ids"]:
            releases_by_signal[signal_id].append(release)

    cohorts_by_id = {cohort["cohort_id"]: cohort for cohort in cohorts}

    print("Decision Spine Client Positioning")
    print(f"Generated: {TODAY.isoformat()}")
    print("Commercial fields unavailable in v1: CRM opportunity detail, account detail, approved client references.")
    print("Use this as positioning input, not external proof.")
    report_positioning(signals, releases_by_signal, cohorts_by_id)


if __name__ == "__main__":
    main()
