#!/usr/bin/env python3
"""Print placement and retention outcome review for Matching and CSM."""

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


def status_for_delta(delta: float | None, green: float, red: float) -> str:
    if delta is None:
        return "pending"
    if delta >= green:
        return "green"
    if delta <= red:
        return "red"
    return "amber"


def action_for_outcome(
    placement_status: str,
    retention_status: str,
    small_n: bool,
    placement_pending: bool,
    retention_pending: bool,
) -> str:
    if placement_pending or retention_pending:
        return "wait for maturity"
    if small_n:
        return "monitor directionally; roll into aggregate"
    if placement_status == "red" or retention_status == "red":
        return "investigate funnel, client feedback, and credential thresholds"
    if placement_status == "green" and retention_status in {"green", "amber"}:
        return "amplify and keep monitoring retention"
    return "monitor"


def deltas_for_cohort(
    cohort: dict[str, Any], baseline: list[dict[str, Any]]
) -> tuple[float | None, float | None]:
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

    return placement_delta, retention_delta


def release_summary(releases: list[dict[str, Any]]) -> str:
    if not releases:
        return "release=none"
    return "; ".join(
        f"{release['release_id']} {release['artifact']} ({release['release_status']})"
        for release in releases
    )


def report_post_change_outcomes(
    cohorts: list[dict[str, Any]], releases_by_cohort: dict[str, list[dict[str, Any]]]
) -> None:
    print_section("Post-Change Cohort Outcomes")
    baselines_by_group: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for cohort in cohorts:
        if cohort["change_exposure"] == "pre_change":
            baselines_by_group[cohort["baseline_group"]].append(cohort)

    post_change = [cohort for cohort in cohorts if cohort["change_exposure"] == "post_change"]
    if not post_change:
        print("- none")
        return

    for cohort in post_change:
        baseline = baselines_by_group.get(cohort["baseline_group"], [])
        placement_delta, retention_delta = deltas_for_cohort(cohort, baseline)
        placement_status = status_for_delta(placement_delta, green=0.05, red=-0.05)
        retention_status = status_for_delta(retention_delta, green=0.03, red=-0.03)
        small_n = cohort["eligible_for_placement"] < 25
        placement_pending = cohort["placement_rate"] is None
        retention_pending = cohort["retention_90d_rate"] is None
        action = action_for_outcome(
            placement_status,
            retention_status,
            small_n,
            placement_pending,
            retention_pending,
        )

        notes = []
        if small_n:
            notes.append("small-n")
        if placement_pending:
            notes.append("placement pending")
        if retention_pending:
            notes.append("retention pending")
        note = f" [{', '.join(notes)}]" if notes else ""

        print(f"- {cohort['cohort_id']}{note} | {cohort['programme']} | confidence={cohort['data_confidence']}")
        print(f"  {release_summary(releases_by_cohort.get(cohort['cohort_id'], []))}")
        print(
            f"  placement={placement_status} {fmt_pct(cohort['placement_rate'])} "
            f"delta={fmt_pp(placement_delta)}"
        )
        print(
            f"  retention={retention_status} {fmt_pct(cohort['retention_90d_rate'])} "
            f"delta={fmt_pp(retention_delta)}"
        )
        print(f"  action={action}")


def report_baseline_coverage(cohorts: list[dict[str, Any]]) -> None:
    print_section("Baseline Coverage")
    baselines_by_group: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for cohort in cohorts:
        if cohort["change_exposure"] == "pre_change":
            baselines_by_group[cohort["baseline_group"]].append(cohort)

    for baseline_group, baseline in sorted(baselines_by_group.items()):
        placement_values = [item["placement_rate"] for item in baseline if item["placement_rate"] is not None]
        retention_values = [item["retention_90d_rate"] for item in baseline if item["retention_90d_rate"] is not None]
        print(
            f"- {baseline_group}: cohorts={len(baseline)} "
            f"placement_baseline={fmt_pct(mean(placement_values) if placement_values else None)} "
            f"retention_baseline={fmt_pct(mean(retention_values) if retention_values else None)}"
        )


def main() -> None:
    validate_or_exit()
    cohorts = load_json("cohort_outcomes.json")
    releases = load_json("releases.json")

    releases_by_cohort: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for release in releases:
        releases_by_cohort[release["cohort_id"]].append(release)

    print("Decision Spine Outcome Review")
    print(f"Generated: {TODAY.isoformat()}")
    print("Drill-down KPI report: python3 scripts/report_kpis.py")
    report_post_change_outcomes(cohorts, releases_by_cohort)
    report_baseline_coverage(cohorts)


if __name__ == "__main__":
    main()
