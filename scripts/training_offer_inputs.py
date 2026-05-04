#!/usr/bin/env python3
"""Print Training as a Service offer inputs from Decision Spine evidence."""

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


def has_readiness_evidence(
    competencies: list[dict[str, Any]], evidence_by_competency: dict[str, list[dict[str, Any]]]
) -> bool:
    return any(
        evidence["readiness_level"] in {"ready", "emerging"} and not evidence["suppression_applied"]
        for competency in competencies
        for evidence in evidence_by_competency.get(competency["competency_id"], [])
    )


def offer_readiness(
    signal: dict[str, Any],
    releases: list[dict[str, Any]],
    competencies: list[dict[str, Any]],
    evidence_by_competency: dict[str, list[dict[str, Any]]],
) -> str:
    released = any(release["release_status"] == "released" for release in releases)
    if signal["status"] == "green" and released and has_readiness_evidence(competencies, evidence_by_competency):
        return "ready_for_offer_design"
    if signal["status"] == "green" and released:
        return "validated_but_readiness_pending"
    if signal["status"] == "green":
        return "validated_but_release_pending"
    if signal["status"] == "amber":
        return "monitor"
    return "exclude"


def recommendation_for(readiness: str, signal: dict[str, Any]) -> str:
    if readiness == "ready_for_offer_design":
        return f"Use as an input to client training design for {signal['role_archetype']} capability gaps."
    if readiness == "validated_but_release_pending":
        return "Track as a future offer candidate; internal artifact is not released yet."
    if readiness == "validated_but_readiness_pending":
        return "Hold for offer design until aggregated readiness evidence is stronger."
    if readiness == "monitor":
        return "Do not package as standalone training yet; keep as embedded or exploratory content."
    return "Exclude from training offer packaging until commercial pull improves."


def release_text(releases: list[dict[str, Any]]) -> str:
    if not releases:
        return "internal_artifacts=none"
    return "internal_artifacts=" + "; ".join(
        f"{release['release_id']} {release['programme']} {release['artifact']} [{release['release_status']}]"
        for release in releases
    )


def competency_text(competencies: list[dict[str, Any]]) -> str:
    if not competencies:
        return "competencies=none"
    return "competencies=" + "; ".join(
        f"{item['competency_id']} {item['competency_cluster']} [{item['market_priority']}]"
        for item in competencies
    )


def report_offer_inputs(
    signals: list[dict[str, Any]],
    releases_by_signal: dict[str, list[dict[str, Any]]],
    competencies_by_signal: dict[str, list[dict[str, Any]]],
    evidence_by_competency: dict[str, list[dict[str, Any]]],
) -> None:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for signal in signals:
        grouped[signal["role_archetype"]].append(signal)

    for archetype in sorted(grouped):
        print_section(f"{archetype} Training Inputs")
        for signal in sorted(grouped[archetype], key=lambda item: item["signal_strength_score"], reverse=True):
            releases = releases_by_signal.get(signal["signal_id"], [])
            competencies = competencies_by_signal.get(signal["signal_id"], [])
            readiness = offer_readiness(signal, releases, competencies, evidence_by_competency)
            regulated = "yes" if signal["client_segment"] in {"Financial services", "Healthcare"} else "no"
            print(
                f"- {signal['signal_id']} [{readiness}] {signal['signal_theme']} | "
                f"segment={signal['client_segment']} | regulated={regulated}"
            )
            print(
                f"  signal_strength={signal['signal_strength_score']} | "
                f"confidence={signal['confidence']} | horizon={signal['horizon_window']}"
            )
            print(f"  {competency_text(competencies)}")
            print(f"  {release_text(releases)}")
            print(f"  recommendation={recommendation_for(readiness, signal)}")
            print("  future_data_needed=training product scope, pricing, client diagnostic data, delivery capacity")


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

    print("Decision Spine Training Offer Inputs")
    print(f"Generated: {TODAY.isoformat()}")
    print("V1 limitation: produces training-offer inputs only; no product, pricing, or client diagnostic data.")
    report_offer_inputs(signals, releases_by_signal, competencies_by_signal, evidence_by_competency)


if __name__ == "__main__":
    main()
