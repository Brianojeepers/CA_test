#!/usr/bin/env python3
"""Export a shareable monthly Decision Spine packet as Markdown."""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path
from statistics import mean
from typing import Any

from decision_impact_review import deltas_for_cohort, impact_status
from validate_data import validate_all


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "outputs"
OUTPUT_PATH = OUTPUT_DIR / "monthly_packet.md"
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


def days_between(start: str | None, end: str | None) -> int | None:
    start_date = parse_date(start)
    end_date = parse_date(end)
    if start_date is None or end_date is None:
        return None
    return (end_date - start_date).days


def fmt_pct(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.1%}"


def fmt_days(value: int | None) -> str:
    return "n/a" if value is None else f"{value}d"


def signal_to_decision_status(days: int | None) -> str:
    if days is None:
        return "red"
    if days <= 21:
        return "green"
    if days <= 45:
        return "amber"
    return "red"


def decision_to_release_status(days: int | None, complexity: str) -> str:
    if days is None:
        return "pending"
    thresholds = {
        "low": (14, 30),
        "medium": (30, 60),
        "high": (60, 90),
    }
    green_days, red_days = thresholds.get(complexity, thresholds["medium"])
    if days <= green_days:
        return "green"
    if days > red_days:
        return "red"
    return "amber"


def validation_or_exit() -> list[str]:
    validation = validate_all()
    if validation.errors:
        print("Data validation failed:", file=sys.stderr)
        for error in validation.errors:
            print(f"- {error}", file=sys.stderr)
        raise SystemExit(1)
    return validation.warnings


def build_decision_impact_rows(
    decisions: list[dict[str, Any]],
    releases: list[dict[str, Any]],
    competencies: list[dict[str, Any]],
    evidence: list[dict[str, Any]],
    cohorts: list[dict[str, Any]],
) -> list[tuple[str, str, str, str]]:
    releases_by_decision: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for release in releases:
        releases_by_decision[release["decision_id"]].append(release)

    competencies_by_decision: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for competency in competencies:
        for decision_id in competency["linked_decision_ids"]:
            competencies_by_decision[decision_id].append(competency)

    evidence_by_competency: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in evidence:
        evidence_by_competency[item["competency_id"]].append(item)

    cohorts_by_id = {cohort["cohort_id"]: cohort for cohort in cohorts}
    baselines_by_group: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for cohort in cohorts:
        if cohort["change_exposure"] == "pre_change":
            baselines_by_group[cohort["baseline_group"]].append(cohort)

    rows: list[tuple[str, str, str, str]] = []
    for decision in decisions:
        if decision["decision_status"] != "approved":
            continue
        linked_releases = releases_by_decision.get(decision["decision_id"], [])
        linked_competencies = competencies_by_decision.get(decision["decision_id"], [])
        linked_evidence = [
            item
            for competency in linked_competencies
            for item in evidence_by_competency.get(competency["competency_id"], [])
        ]
        linked_cohorts = [
            cohorts_by_id[release["cohort_id"]]
            for release in linked_releases
            if release["cohort_id"] in cohorts_by_id
        ]
        placement_deltas: list[float] = []
        retention_deltas: list[float] = []
        for cohort in linked_cohorts:
            placement_delta, retention_delta = deltas_for_cohort(cohort, baselines_by_group)
            if placement_delta is not None:
                placement_deltas.append(placement_delta)
            if retention_delta is not None:
                retention_deltas.append(retention_delta)
        status = impact_status(
            linked_releases,
            linked_evidence,
            linked_cohorts,
            placement_deltas,
            retention_deltas,
        )
        release_text = ", ".join(f"{release['release_id']}:{release['release_status']}" for release in linked_releases)
        rows.append((decision["decision_id"], status, decision["owner"], release_text or "none"))
    return rows


def build_action_items(
    signals: list[dict[str, Any]],
    decisions: list[dict[str, Any]],
    releases: list[dict[str, Any]],
) -> list[str]:
    decisions_by_signal: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for decision in decisions:
        for signal_id in decision["signal_ids"]:
            decisions_by_signal[signal_id].append(decision)

    items: list[str] = []
    for signal in signals:
        linked_decisions = decisions_by_signal.get(signal["signal_id"], [])
        if signal["status"] == "green" and not linked_decisions:
            items.append(f"Assign decision owner for `{signal['signal_id']}` {signal['signal_theme']}.")
        elif signal["status"] == "green" and linked_decisions:
            first_decision = min(linked_decisions, key=lambda item: item["decision_signed_date"])
            elapsed = days_between(signal["green_threshold_date"], first_decision["decision_signed_date"])
            status = signal_to_decision_status(elapsed)
            if status in {"amber", "red"}:
                items.append(
                    f"Review `{signal['signal_id']} -> {first_decision['decision_id']}` "
                    f"({status}, {fmt_days(elapsed)}, owner={first_decision['owner']})."
                )

    releases_by_decision: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for release in releases:
        releases_by_decision[release["decision_id"]].append(release)

    for decision in decisions:
        if decision["decision_status"] != "approved":
            continue
        linked_releases = releases_by_decision.get(decision["decision_id"], [])
        if not linked_releases:
            items.append(f"Create release record for `{decision['decision_id']}` owner={decision['owner']}.")
        for release in linked_releases:
            elapsed = days_between(decision["decision_signed_date"], release["release_date"])
            status = decision_to_release_status(elapsed, decision["complexity_tier"])
            if status in {"pending", "red"}:
                items.append(
                    f"Unblock `{decision['decision_id']} -> {release['release_id']}` "
                    f"({status}, owner={decision['owner']}, artifact={release['artifact']})."
                )
    return items


def render_packet() -> str:
    warnings = validation_or_exit()
    signals = load_json("signals.json")
    decisions = load_json("decisions.json")
    releases = load_json("releases.json")
    cohorts = load_json("cohort_outcomes.json")
    predictions = load_json("predictions.json")
    competencies = load_json("role_competencies.json")
    evidence = load_json("learner_evidence_summary.json")

    signal_counts = Counter(signal["status"] for signal in signals)
    signal_avg = mean(signal["signal_strength_score"] for signal in signals)
    scored_predictions = [
        prediction
        for prediction in predictions
        if parse_date(prediction["scoring_date"]) <= TODAY
        and prediction["outcome"] in {"confirmed", "contradicted"}
    ]
    prediction_accuracy = None
    if scored_predictions:
        prediction_accuracy = sum(item["accuracy_score"] for item in scored_predictions) / len(scored_predictions)
    pending_outcome_count = sum(
        1
        for cohort in cohorts
        if cohort["change_exposure"] == "post_change"
        and (cohort["placement_rate"] is None or cohort["retention_90d_rate"] is None)
    )
    impact_rows = build_decision_impact_rows(decisions, releases, competencies, evidence, cohorts)
    impact_counts = Counter(row[1] for row in impact_rows)
    action_items = build_action_items(signals, decisions, releases)

    lines = [
        "# Decision Spine Monthly Packet",
        "",
        f"Generated: {TODAY.isoformat()}",
        "",
        "## Data Trust",
        "",
        f"- Validation: passed with {len(warnings)} warning(s).",
    ]
    for warning in warnings:
        lines.append(f"- Warning: `{warning}`")

    lines.extend(
        [
            "",
            "## KPI Posture",
            "",
            f"- K1 signal strength: avg={signal_avg:.1f}; green={signal_counts['green']}; "
            f"amber={signal_counts['amber']}; red={signal_counts['red']}.",
            f"- K7 prediction accuracy: {fmt_pct(prediction_accuracy)} ({len(scored_predictions)} scored).",
            f"- Outcome data pending for {pending_outcome_count} post-change cohort(s).",
            "",
            "## Decision Impact",
            "",
            f"- positive_signal={impact_counts['positive_signal']}",
            f"- evidence_emerging={impact_counts['evidence_emerging']}",
            f"- too_early={impact_counts['too_early']}",
            f"- needs_attention={impact_counts['needs_attention']}",
            f"- no_outcome_data={impact_counts['no_outcome_data']}",
            "",
            "| Decision | Status | Owner | Releases |",
            "| --- | --- | --- | --- |",
        ]
    )
    for decision_id, status, owner, release_text in impact_rows:
        lines.append(f"| `{decision_id}` | `{status}` | {owner} | {release_text} |")

    lines.extend(["", "## Decisions Needing Action", ""])
    if action_items:
        for item in action_items:
            lines.append(f"- {item}")
    else:
        lines.append("- None.")

    lines.extend(
        [
            "",
            "## Stakeholder Drill-Downs",
            "",
            "- Council: `python3 scripts/council_review.py`",
            "- Decision impact: `python3 scripts/decision_impact_review.py`",
            "- Matching and CSM outcomes: `python3 scripts/outcome_review.py`",
            "- Credential requirements: `python3 scripts/credential_requirements.py`",
            "- Learning outcomes: `python3 scripts/learning_outcomes.py`",
            "- Client positioning: `python3 scripts/client_positioning.py`",
            "- Training offers: `python3 scripts/training_offer_inputs.py`",
            "- Talent profile signals: `python3 scripts/talent_profile_signals.py`",
            "- Delivery windows: `python3 scripts/delivery_window_review.py`",
            "- Source contracts: `python3 scripts/source_contract_review.py`",
            "",
            "## Current Known Limits",
            "",
            "- Seed data is synthetic.",
            "- Real learner and outcome extracts remain blocked by source-contract privacy rules.",
            "- Actual cohort calendar detail is unavailable in v1.",
            "- Placement and readiness evidence are directional until sample sizes and retention windows mature.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    OUTPUT_DIR.mkdir(exist_ok=True)
    packet = render_packet()
    OUTPUT_PATH.write_text(packet, encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
