#!/usr/bin/env python3
"""Print talent-facing profile signal guidance from Decision Spine evidence."""

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


def active_release(releases: list[dict[str, Any]]) -> bool:
    return any(release["release_status"] == "released" for release in releases)


def has_profile_ready_evidence(
    competencies: list[dict[str, Any]], evidence_by_competency: dict[str, list[dict[str, Any]]]
) -> bool:
    return any(
        evidence["readiness_level"] in {"ready", "emerging"} and not evidence["suppression_applied"]
        for competency in competencies
        for evidence in evidence_by_competency.get(competency["competency_id"], [])
    )


def profile_status(
    signal: dict[str, Any],
    releases: list[dict[str, Any]],
    competencies: list[dict[str, Any]],
    evidence_by_competency: dict[str, list[dict[str, Any]]],
) -> str:
    if signal["status"] == "green" and active_release(releases) and has_profile_ready_evidence(
        competencies, evidence_by_competency
    ):
        return "active_profile_guidance"
    if signal["status"] == "green" and active_release(releases):
        return "released_but_evidence_pending"
    if signal["status"] == "green":
        return "future_guidance"
    if signal["status"] == "amber":
        return "monitor_only"
    return "exclude"


def profile_line(signal: dict[str, Any], competencies: list[dict[str, Any]]) -> str:
    if competencies:
        capability = competencies[0]["capability"]
    else:
        capability = signal["signal_theme"]
    return f"Show evidence of {capability}"


def release_text(releases: list[dict[str, Any]]) -> str:
    released = [release for release in releases if release["release_status"] == "released"]
    if not released:
        return "released_artifacts=none"
    return "released_artifacts=" + "; ".join(
        f"{release['release_id']} {release['programme']} {release['artifact']}" for release in released
    )


def report_profile_guidance(
    signals: list[dict[str, Any]],
    releases_by_signal: dict[str, list[dict[str, Any]]],
    competencies_by_signal: dict[str, list[dict[str, Any]]],
    evidence_by_competency: dict[str, list[dict[str, Any]]],
) -> None:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for signal in signals:
        grouped[signal["role_archetype"]].append(signal)

    for archetype in sorted(grouped):
        print_section(f"{archetype} Profile Guidance")
        for signal in sorted(grouped[archetype], key=lambda item: item["signal_strength_score"], reverse=True):
            releases = releases_by_signal.get(signal["signal_id"], [])
            competencies = competencies_by_signal.get(signal["signal_id"], [])
            status = profile_status(signal, releases, competencies, evidence_by_competency)
            evidence_ids = [
                evidence["evidence_id"]
                for competency in competencies
                for evidence in evidence_by_competency.get(competency["competency_id"], [])
            ]
            print(f"- {signal['signal_id']} [{status}] {signal['signal_theme']}")
            print(f"  guidance={profile_line(signal, competencies)}")
            print(f"  role_archetype={signal['role_archetype']} | capability_area={signal['signal_theme']}")
            print(f"  {release_text(releases)}")
            print(f"  learner_evidence={', '.join(evidence_ids) if evidence_ids else 'none'}")
            if status == "active_profile_guidance":
                print("  action=use as profile guidance input; do not claim unreviewed individual proficiency")
            elif status == "released_but_evidence_pending":
                print("  action=hold active tag until aggregated readiness evidence is stronger")
            elif status == "future_guidance":
                print("  action=hold until release is active")
            elif status == "monitor_only":
                print("  action=exclude from active tags; use only as future guidance")
            else:
                print("  action=exclude from profile guidance")


def main() -> None:
    validate_or_exit()
    signals = load_json("signals.json")
    releases = load_json("releases.json")
    competencies = load_json("role_competencies.json")
    evidence = load_json("learner_evidence_summary.json")

    releases_by_signal: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for release in releases:
        for signal_id in release["linked_signal_ids"]:
            releases_by_signal[signal_id].append(release)

    competencies_by_signal: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for competency in competencies:
        for signal_id in competency["linked_signal_ids"]:
            competencies_by_signal[signal_id].append(competency)

    evidence_by_competency: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in evidence:
        evidence_by_competency[item["competency_id"]].append(item)

    print("Decision Spine Talent Profile Signals")
    print(f"Generated: {TODAY.isoformat()}")
    print("V1 limitation: outputs profile guidance only; it does not write to a talent profile system.")
    report_profile_guidance(signals, releases_by_signal, competencies_by_signal, evidence_by_competency)


if __name__ == "__main__":
    main()
