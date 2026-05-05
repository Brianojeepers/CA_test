"""File-backed review workflow for monthly council operating outcomes."""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any

from decision_spine.services.review_snapshots import action_key


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
REVIEW_OUTCOME_FILE = DATA_DIR / "review_workflow_outcomes.json"
REVIEW_EVENT_FILE = DATA_DIR / "review_workflow_events.json"

REVIEW_OUTCOMES = {
    "accepted": "Accepted",
    "needs_follow_up": "Needs follow-up",
    "blocked": "Blocked",
    "deferred": "Deferred",
}
UNREVIEWED_OUTCOME = "unreviewed"
OUTCOME_LABELS = {UNREVIEWED_OUTCOME: "Unreviewed", **REVIEW_OUTCOMES}

AGENDA_STEPS: tuple[dict[str, str], ...] = (
    {
        "step_id": "trust_posture",
        "label": "Trust posture",
        "purpose": "Confirm what the current stakeholder surfaces can and cannot be trusted to say.",
    },
    {
        "step_id": "source_blockers",
        "label": "Source blockers",
        "purpose": "Assign follow-up for red or amber source contracts before real-data work.",
    },
    {
        "step_id": "decision_policy",
        "label": "Decision policy",
        "purpose": "Confirm the safe operating outcome for each active decision.",
    },
    {
        "step_id": "reasoning_stress",
        "label": "Reasoning stress",
        "purpose": "Check that unsafe claims still downgrade before schema or stakeholder commitments.",
    },
    {
        "step_id": "action_queue",
        "label": "Action queue",
        "purpose": "Record council outcomes for current action items.",
    },
)


class InvalidReviewOutcome(ValueError):
    """Raised when a review outcome is unsupported."""


class UnknownReviewItem(ValueError):
    """Raised when a workflow update references a non-current review item."""


def save_json_records(records: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(f"{path.suffix}.tmp")
    with temp_path.open("w", encoding="utf-8") as file:
        json.dump(records, file, indent=2)
        file.write("\n")
    temp_path.replace(path)


def load_review_outcome_records(path: Path | None = None) -> list[dict[str, Any]]:
    path = path or REVIEW_OUTCOME_FILE
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, list):
        raise ValueError(f"{path}: expected top-level JSON list")
    return data


def load_review_event_records(path: Path | None = None) -> list[dict[str, Any]]:
    path = path or REVIEW_EVENT_FILE
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, list):
        raise ValueError(f"{path}: expected top-level JSON list")
    return data


def save_review_outcome_records(records: list[dict[str, Any]], path: Path | None = None) -> None:
    save_json_records(records, path or REVIEW_OUTCOME_FILE)


def save_review_event_records(records: list[dict[str, Any]], path: Path | None = None) -> None:
    save_json_records(records, path or REVIEW_EVENT_FILE)


def review_key(step_id: str, item_id: str) -> str:
    return f"{step_id}:{item_id}"


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def slug(*parts: str, max_length: int = 80) -> str:
    raw = "-".join(part for part in parts if part)
    cleaned = re.sub(r"[^A-Za-z0-9_-]+", "-", raw).strip("-").lower()
    cleaned = re.sub(r"-{2,}", "-", cleaned) or "item"
    if len(cleaned) <= max_length:
        return cleaned
    digest = hashlib.sha1(raw.encode("utf-8")).hexdigest()[:10]
    return f"{cleaned[: max_length - 11].rstrip('-')}-{digest}"


def outcome_records_by_key(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {review_key(str(record.get("step_id", "")), str(record.get("item_id", ""))): record for record in records}


def sorted_review_events(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        events,
        key=lambda event: (str(event.get("event_date", "")), str(event.get("event_id", ""))),
        reverse=True,
    )


def review_events_by_key(events: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    by_key: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for event in sorted_review_events(events):
        by_key[review_key(str(event.get("step_id", "")), str(event.get("item_id", "")))].append(event)
    return dict(by_key)


def next_review_event_id(events: list[dict[str, Any]], event_date: str) -> str:
    prefix = f"RWE-{event_date.replace('-', '')}-"
    suffixes: list[int] = []
    for event in events:
        event_id = str(event.get("event_id", ""))
        if not event_id.startswith(prefix):
            continue
        try:
            suffixes.append(int(event_id.removeprefix(prefix)))
        except ValueError:
            continue
    return f"{prefix}{(max(suffixes) + 1) if suffixes else 1:03d}"


def attach_review_outcome(
    item: dict[str, Any],
    outcome_by_key: dict[str, dict[str, Any]],
    events_by_key: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    key = review_key(item["step_id"], item["item_id"])
    record = outcome_by_key.get(key, {})
    outcome = str(record.get("outcome", UNREVIEWED_OUTCOME))
    recent_events = events_by_key.get(key, [])[:3]
    return {
        **item,
        "review_outcome": outcome,
        "review_outcome_label": OUTCOME_LABELS.get(outcome, outcome),
        "review_notes": record.get("notes", ""),
        "review_updated_date": record.get("updated_date"),
        "last_event": recent_events[0] if recent_events else None,
        "recent_events": recent_events,
    }


def policy_severity(policy_outcome: str) -> str:
    return {
        "act_now": "green",
        "revise": "amber",
        "monitor": "neutral",
        "wait": "amber",
        "escalate": "red",
        "archive": "neutral",
    }.get(policy_outcome, "neutral")


def recommended_outcome_for_policy(policy_outcome: str) -> str:
    return {
        "act_now": "accepted",
        "revise": "needs_follow_up",
        "monitor": "deferred",
        "wait": "needs_follow_up",
        "escalate": "blocked",
        "archive": "accepted",
    }.get(policy_outcome, "needs_follow_up")


def source_action_items(trust_registry: dict[str, Any]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for action in trust_registry["priority_trust_actions"]:
        severity = action["severity"]
        items.append(
            {
                "step_id": "source_blockers",
                "item_id": slug(action["contract_id"]),
                "title": f"{action['contract_id']} {action['data_domain']}",
                "summary": action["next_action"],
                "owner": action["owner"],
                "severity": severity,
                "source_ref": action["contract_id"],
                "review_prompt": "Assign source-owner, privacy-owner, or council follow-up.",
                "recommended_outcome": "blocked" if severity == "red" else "needs_follow_up",
            }
        )
    return items


def trust_posture_items(trust_registry: dict[str, Any]) -> list[dict[str, Any]]:
    summary = trust_registry["summary"]
    privacy_blocked = summary["privacy_blocked_surface_count"]
    planning_ready = summary["planning_ready_surface_count"]
    severity = "red" if privacy_blocked else "amber"
    return [
        {
            "step_id": "trust_posture",
            "item_id": "stakeholder-surface-trust",
            "title": "Confirm stakeholder surface trust posture",
            "summary": (
                f"{privacy_blocked} privacy-blocked surface(s), {planning_ready} planning-ready control surface(s), "
                f"{summary['decision_grade_surface_count']} decision-grade surface(s)."
            ),
            "owner": "Signal Intelligence Council",
            "severity": severity,
            "source_ref": "trust_registry",
            "review_prompt": "Confirm language stays internal, directional, and bounded by source posture.",
            "recommended_outcome": "needs_follow_up" if privacy_blocked else "accepted",
        }
    ]


def decision_policy_items(policy_review: dict[str, Any]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for row in policy_review["policy_rows"]:
        items.append(
            {
                "step_id": "decision_policy",
                "item_id": slug(row["decision_id"]),
                "title": f"{row['decision_id']} {row['policy_label']}",
                "summary": row["rationale"],
                "owner": row["owner"],
                "severity": policy_severity(row["policy_outcome"]),
                "source_ref": row["decision_id"],
                "review_prompt": row["allowed_action"],
                "recommended_outcome": recommended_outcome_for_policy(row["policy_outcome"]),
                "policy_outcome": row["policy_outcome"],
                "next_review_trigger": row["next_review_trigger"],
            }
        )
    return items


def reasoning_stress_items(stress_review: dict[str, Any]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for scenario in stress_review["scenarios"]:
        passed = scenario["result"] == "pass"
        items.append(
            {
                "step_id": "reasoning_stress",
                "item_id": slug(scenario["scenario_id"]),
                "title": f"{scenario['scenario_id']} {scenario['title']}",
                "summary": scenario["safe_response"],
                "owner": "Signal Intelligence Council",
                "severity": "green" if passed else "red",
                "source_ref": scenario["scenario_id"],
                "review_prompt": scenario["unsafe_claim"],
                "recommended_outcome": "accepted" if passed else "blocked",
                "required_downgrade": scenario["required_downgrade"],
            }
        )
    return items


def action_queue_items(packet: dict[str, Any]) -> list[dict[str, Any]]:
    decision_owners = {
        row["decision_id"]: row["owner"]
        for row in packet.get("decision_impact", {}).get("rows", [])
    }
    items: list[dict[str, Any]] = []
    for action in packet.get("actions", []):
        stable_action_key = action_key(action)
        decision_id = action.get("decision_id", "")
        severity = action.get("severity", "amber")
        items.append(
            {
                "step_id": "action_queue",
                "item_id": slug(stable_action_key),
                "title": action["text"],
                "summary": action["text"],
                "owner": decision_owners.get(decision_id, "Signal Intelligence Council"),
                "severity": severity,
                "source_ref": decision_id or action.get("signal_id") or action.get("release_id") or action.get("kind", ""),
                "review_prompt": "Confirm the owner, follow-up trigger, and whether the action remains in scope.",
                "recommended_outcome": "blocked" if severity == "red" else "needs_follow_up",
            }
        )
    return items


def workflow_items(
    packet: dict[str, Any],
    trust_registry: dict[str, Any],
    policy_review: dict[str, Any],
    stress_review: dict[str, Any],
) -> list[dict[str, Any]]:
    return [
        *trust_posture_items(trust_registry),
        *source_action_items(trust_registry),
        *decision_policy_items(policy_review),
        *reasoning_stress_items(stress_review),
        *action_queue_items(packet),
    ]


def step_summary(step: dict[str, str], items: list[dict[str, Any]]) -> dict[str, Any]:
    counts = Counter(item["review_outcome"] for item in items)
    severity_counts = Counter(item["severity"] for item in items)
    return {
        **step,
        "item_count": len(items),
        "unreviewed_count": counts[UNREVIEWED_OUTCOME],
        "accepted_count": counts["accepted"],
        "needs_follow_up_count": counts["needs_follow_up"],
        "blocked_count": counts["blocked"],
        "deferred_count": counts["deferred"],
        "red_count": severity_counts["red"],
        "amber_count": severity_counts["amber"],
        "green_count": severity_counts["green"],
        "items": items,
    }


def build_review_workflow(
    *,
    packet: dict[str, Any] | None = None,
    trust_registry: dict[str, Any] | None = None,
    source_review: dict[str, Any] | None = None,
    policy_review: dict[str, Any] | None = None,
    stress_review: dict[str, Any] | None = None,
    outcome_records: list[dict[str, Any]] | None = None,
    event_records: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    if packet is None:
        from decision_spine.services.monthly_packet import build_monthly_packet

        packet = build_monthly_packet()
    from decision_spine.services.decision_policy import build_decision_policy_review
    from decision_spine.services.reasoning_stress import build_reasoning_stress_review
    from decision_spine.services.source_ingestion import build_source_ingestion_review
    from decision_spine.services.trust_registry import build_trust_registry

    trust_registry = trust_registry or build_trust_registry()
    source_review = source_review or build_source_ingestion_review()
    policy_review = policy_review or build_decision_policy_review(packet=packet)
    stress_review = stress_review or build_reasoning_stress_review(
        source_review=source_review,
        trust_registry=trust_registry,
        policy_review=policy_review,
    )
    outcome_records = outcome_records if outcome_records is not None else load_review_outcome_records()
    event_records = event_records if event_records is not None else load_review_event_records()
    outcome_by_key = outcome_records_by_key(outcome_records)
    events_by_key = review_events_by_key(event_records)
    items = [
        attach_review_outcome(item, outcome_by_key, events_by_key)
        for item in workflow_items(packet, trust_registry, policy_review, stress_review)
    ]
    items_by_step = defaultdict(list)
    for item in items:
        items_by_step[item["step_id"]].append(item)
    steps = [step_summary(step, items_by_step[step["step_id"]]) for step in AGENDA_STEPS]
    outcome_counts = Counter(item["review_outcome"] for item in items)
    severity_counts = Counter(item["severity"] for item in items)
    return {
        "generated_date": packet["generated_date"],
        "purpose": (
            "Run the monthly review as an operating workflow: confirm trust posture, assign source blockers, "
            "approve decision policy outcomes, verify stress-test downgrades, and record action follow-up."
        ),
        "summary": {
            "step_count": len(steps),
            "item_count": len(items),
            "unreviewed_count": outcome_counts[UNREVIEWED_OUTCOME],
            "accepted_count": outcome_counts["accepted"],
            "needs_follow_up_count": outcome_counts["needs_follow_up"],
            "blocked_count": outcome_counts["blocked"],
            "deferred_count": outcome_counts["deferred"],
            "red_count": severity_counts["red"],
            "amber_count": severity_counts["amber"],
            "green_count": severity_counts["green"],
            "local_register": display_path(REVIEW_OUTCOME_FILE),
        },
        "allowed_outcomes": [{"outcome": key, "label": label} for key, label in REVIEW_OUTCOMES.items()],
        "steps": steps,
        "recent_events": sorted_review_events(event_records)[:8],
    }


def current_review_item_by_key(outcome_records: list[dict[str, Any]] | None = None) -> dict[str, dict[str, Any]]:
    workflow = build_review_workflow(outcome_records=outcome_records)
    return {
        review_key(item["step_id"], item["item_id"]): item
        for step in workflow["steps"]
        for item in step["items"]
    }


def update_review_item_outcome(
    step_id: str,
    item_id: str,
    outcome: str,
    notes: str | None = None,
    *,
    path: Path | None = None,
    event_path: Path | None = None,
    updated_date: date | None = None,
) -> dict[str, Any]:
    outcome = outcome.strip()
    if outcome not in REVIEW_OUTCOMES:
        raise InvalidReviewOutcome(f"Unsupported review outcome: {outcome}")
    notes = notes.strip() if notes is not None else None

    records = load_review_outcome_records(path)
    by_key = outcome_records_by_key(records)
    key = review_key(step_id, item_id)
    current_items = current_review_item_by_key(records)
    item = current_items.get(key)
    if item is None:
        raise UnknownReviewItem(f"Unknown current review item: {key}")

    today = (updated_date or date.today()).isoformat()
    events = load_review_event_records(event_path)
    current_record = by_key.get(key)
    previous_outcome = str(current_record.get("outcome", UNREVIEWED_OUTCOME)) if current_record else UNREVIEWED_OUTCOME
    previous_notes = str(current_record.get("notes", "")) if current_record else ""
    next_notes = notes if notes is not None else previous_notes or item["review_prompt"]
    if current_record is None:
        current_record = {
            "step_id": step_id,
            "item_id": item_id,
            "title": item["title"],
            "owner": item["owner"],
            "outcome": outcome,
            "notes": next_notes,
            "updated_date": today,
        }
        records.append(current_record)
    else:
        current_record["title"] = item["title"]
        current_record["owner"] = item["owner"]
        current_record["outcome"] = outcome
        if notes is not None:
            current_record["notes"] = next_notes
        current_record["updated_date"] = today

    if previous_outcome != outcome or previous_notes != next_notes:
        events.append(
            {
                "event_id": next_review_event_id(events, today),
                "step_id": step_id,
                "item_id": item_id,
                "title": item["title"],
                "previous_outcome": previous_outcome,
                "next_outcome": outcome,
                "notes": next_notes,
                "event_date": today,
            }
        )

    save_review_outcome_records(records, path)
    save_review_event_records(events, event_path)
    return current_record


def review_workflow_summary_from_register(
    outcome_records: list[dict[str, Any]] | None = None,
    event_records: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    outcome_records = outcome_records if outcome_records is not None else load_review_outcome_records()
    event_records = event_records if event_records is not None else load_review_event_records()
    counts = Counter(record.get("outcome", UNREVIEWED_OUTCOME) for record in outcome_records)
    return {
        "recorded_outcome_count": len(outcome_records),
        "accepted_count": counts["accepted"],
        "needs_follow_up_count": counts["needs_follow_up"],
        "blocked_count": counts["blocked"],
        "deferred_count": counts["deferred"],
        "event_count": len(event_records),
        "local_register": display_path(REVIEW_OUTCOME_FILE),
    }


def render_review_workflow_text(workflow: dict[str, Any]) -> str:
    summary = workflow["summary"]
    lines = [
        "Review Workflow",
        "===============",
        "",
        f"Generated: {workflow['generated_date']}",
        "",
        workflow["purpose"],
        "",
        "Summary",
        "-------",
        (
            f"- steps={summary['step_count']} items={summary['item_count']} "
            f"unreviewed={summary['unreviewed_count']} accepted={summary['accepted_count']} "
            f"needs_follow_up={summary['needs_follow_up_count']} blocked={summary['blocked_count']} "
            f"deferred={summary['deferred_count']}"
        ),
        f"- local_register={summary['local_register']}",
        "",
        "Agenda",
        "------",
    ]
    for step in workflow["steps"]:
        lines.append(
            f"- {step['label']}: items={step['item_count']} unreviewed={step['unreviewed_count']} "
            f"blocked={step['blocked_count']} follow_up={step['needs_follow_up_count']}"
        )
        for item in step["items"][:6]:
            lines.append(
                f"  - [{item['review_outcome']}; {item['severity']}] {item['title']} "
                f"owner={item['owner']} recommended={item['recommended_outcome']}"
            )
    if workflow["recent_events"]:
        lines.extend(["", "Recent Events", "-------------"])
        for event in workflow["recent_events"]:
            lines.append(
                f"- {event['event_date']} {event['item_id']}: "
                f"{event['previous_outcome']} -> {event['next_outcome']} ({event['notes']})"
            )
    return "\n".join(lines).rstrip() + "\n"
