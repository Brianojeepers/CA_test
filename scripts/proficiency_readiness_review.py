#!/usr/bin/env python3
"""Print privacy-safe proficiency readiness evidence by competency."""

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


def format_rate(value: float | None) -> str:
    if value is None:
        return "pending"
    return f"{value:.1%}"


def report_summary(evidence: list[dict[str, Any]]) -> None:
    print_section("Readiness Summary")
    by_level = Counter(item["readiness_level"] for item in evidence)
    by_confidence = Counter(item["evidence_confidence"] for item in evidence)
    print(f"- evidence_records={len(evidence)}")
    print(
        "- readiness="
        + ", ".join(
            f"{level}:{by_level[level]}"
            for level in ("ready", "emerging", "not_ready", "pending", "insufficient_sample")
        )
    )
    print("- confidence=" + ", ".join(f"{level}:{by_confidence[level]}" for level in ("low", "medium", "high")))


def report_by_competency(
    evidence_by_competency: dict[str, list[dict[str, Any]]],
    competencies_by_id: dict[str, dict[str, Any]],
) -> None:
    print_section("Competency Readiness")
    for competency_id in sorted(evidence_by_competency):
        competency = competencies_by_id[competency_id]
        print(
            f"- {competency_id} {competency['role_archetype']} | "
            f"{competency['competency_cluster']} | target={competency['target_proficiency']}"
        )
        for item in sorted(evidence_by_competency[competency_id], key=lambda value: value["evidence_id"]):
            count = item["meets_threshold_count"]
            threshold = "pending" if count is None else f"{count}/{item['sample_size']}"
            print(
                f"  - {item['evidence_id']} {item['cohort_id']} [{item['readiness_level']}, "
                f"{item['evidence_confidence']}] type={item['evidence_type']}"
            )
            print(
                f"    threshold={threshold} | readiness_rate={format_rate(item['readiness_rate'])} | "
                f"suppressed={item['suppression_applied']}"
            )
            print(f"    evidence={item['evidence_summary']}")
            print(f"    next_action={item['next_action']}")


def report_attention_items(evidence: list[dict[str, Any]]) -> None:
    print_section("Attention Items")
    items = [
        item
        for item in evidence
        if item["readiness_level"] in {"pending", "insufficient_sample", "not_ready"}
        or item["suppression_applied"]
    ]
    if not items:
        print("- none")
        return
    for item in sorted(items, key=lambda value: (value["readiness_level"], value["evidence_id"])):
        print(
            f"- {item['evidence_id']} {item['competency_id']} | "
            f"level={item['readiness_level']} | action={item['next_action']}"
        )


def report_coverage(
    competencies: list[dict[str, Any]],
    evidence_by_competency: dict[str, list[dict[str, Any]]],
) -> None:
    print_section("Evidence Coverage")
    for competency in competencies:
        linked = evidence_by_competency.get(competency["competency_id"], [])
        if linked:
            ids = ", ".join(item["evidence_id"] for item in linked)
            print(f"- {competency['competency_id']} {competency['status']} -> {ids}")
            continue
        action = "acceptable: monitor competency can wait for stronger market pull"
        if competency["status"] == "active":
            action = "gap: active competency needs aggregated learner evidence"
        print(f"- {competency['competency_id']} {competency['status']} -> none | {action}")


def main() -> None:
    validate_or_exit()
    evidence = load_json("learner_evidence_summary.json")
    competencies = load_json("role_competencies.json")

    competencies_by_id = {competency["competency_id"]: competency for competency in competencies}
    evidence_by_competency: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in evidence:
        evidence_by_competency[item["competency_id"]].append(item)

    print("Decision Spine Proficiency Readiness Review")
    print(f"Generated: {TODAY.isoformat()}")
    print("Reference: docs/learner_evidence_model.md")
    report_summary(evidence)
    report_by_competency(evidence_by_competency, competencies_by_id)
    report_attention_items(evidence)
    report_coverage(competencies, evidence_by_competency)


if __name__ == "__main__":
    main()
