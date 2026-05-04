#!/usr/bin/env python3
"""Print release-to-cohort delivery-window coordination view."""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from datetime import date, datetime
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


def parse_date(value: str | None) -> date | None:
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


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


def delivery_status(release: dict[str, Any], cohort: dict[str, Any] | None) -> str:
    if cohort is None:
        if release["release_status"] == "released":
            return "data_quality_issue"
        return "future_cohort"
    if release["release_status"] != "released":
        return "coordination_needed"
    release_date = parse_date(release["release_date"])
    cohort_start = parse_date(cohort["cohort_start_date"])
    credential_date = parse_date(cohort["credential_issued_date"])
    if release_date and credential_date and release_date > credential_date:
        return "late_for_credential_window"
    if release_date and cohort_start and release_date > cohort_start:
        return "in_cohort_timing_review"
    return "aligned"


def action_for(status: str) -> str:
    actions = {
        "aligned": "no delivery action required",
        "future_cohort": "confirm target cohort window when calendar data exists",
        "coordination_needed": "coordinate owner, target cohort, and release readiness",
        "in_cohort_timing_review": "confirm whether release landed before the relevant module or assessment week",
        "late_for_credential_window": "review whether change missed credential issuance window",
        "data_quality_issue": "fix released item with unknown cohort_id",
    }
    return actions[status]


def report_delivery_windows(
    releases: list[dict[str, Any]],
    decisions_by_id: dict[str, dict[str, Any]],
    cohorts_by_id: dict[str, dict[str, Any]],
) -> None:
    by_status: dict[str, list[str]] = defaultdict(list)
    for release in releases:
        decision = decisions_by_id[release["decision_id"]]
        cohort = cohorts_by_id.get(release["cohort_id"])
        status = delivery_status(release, cohort)
        cohort_text = "future cohort / no outcomes yet"
        if cohort:
            cohort_text = (
                f"start={cohort['cohort_start_date']} credential={cohort['credential_issued_date']} "
                f"confidence={cohort['data_confidence']}"
            )
        release_date = release["release_date"] or "not released"
        by_status[status].append(
            f"- {release['release_id']} [{status}] {release['programme']} | {release['artifact']}\n"
            f"  decision={decision['decision_id']} owner={decision['owner']} complexity={decision['complexity_tier']}\n"
            f"  release_status={release['release_status']} release_date={release_date} target_cohort={release['cohort_id']}\n"
            f"  cohort={cohort_text}\n"
            f"  action={action_for(status)}"
        )

    for status in (
        "coordination_needed",
        "future_cohort",
        "in_cohort_timing_review",
        "late_for_credential_window",
        "data_quality_issue",
        "aligned",
    ):
        print_section(status.replace("_", " ").title())
        items = by_status.get(status, [])
        if not items:
            print("- none")
            continue
        for item in items:
            print(item)


def main() -> None:
    validate_or_exit()
    decisions = load_json("decisions.json")
    releases = load_json("releases.json")
    cohorts = load_json("cohort_outcomes.json")

    decisions_by_id = {decision["decision_id"]: decision for decision in decisions}
    cohorts_by_id = {cohort["cohort_id"]: cohort for cohort in cohorts}

    print("Decision Spine Delivery Window Review")
    print(f"Generated: {TODAY.isoformat()}")
    print("V1 limitation: actual cohort calendar detail is unavailable; this uses release cohort IDs only.")
    report_delivery_windows(releases, decisions_by_id, cohorts_by_id)


if __name__ == "__main__":
    main()
