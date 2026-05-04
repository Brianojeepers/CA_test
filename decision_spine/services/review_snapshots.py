"""Persist and compare monthly review snapshots."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SNAPSHOT_DIR = ROOT / "outputs" / "review_snapshots"
SNAPSHOT_SCHEMA_VERSION = 1


def packet_for_snapshot(packet: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in packet.items() if key != "review_diff"}


def action_key(action: dict[str, Any]) -> str:
    return "|".join(
        [
            action.get("kind", ""),
            action.get("decision_id", ""),
            action.get("signal_id", ""),
            action.get("release_id", ""),
            action.get("text", ""),
        ]
    )


def changelog_key(item: dict[str, Any]) -> str:
    return "|".join([item.get("category", ""), item.get("item_id", ""), item.get("decision_id", "")])


def latest_snapshot_path(snapshot_dir: Path = DEFAULT_SNAPSHOT_DIR) -> Path | None:
    paths = sorted(snapshot_dir.glob("*.json"))
    return paths[-1] if paths else None


def load_snapshot(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def latest_snapshot(snapshot_dir: Path = DEFAULT_SNAPSHOT_DIR) -> dict[str, Any] | None:
    path = latest_snapshot_path(snapshot_dir)
    return load_snapshot(path) if path else None


def save_review_snapshot(
    packet: dict[str, Any],
    snapshot_dir: Path = DEFAULT_SNAPSHOT_DIR,
    *,
    snapshot_id: str | None = None,
) -> Path:
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    saved_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    stable_id = snapshot_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    envelope = {
        "schema_version": SNAPSHOT_SCHEMA_VERSION,
        "snapshot_id": stable_id,
        "saved_at": saved_at,
        "generated_date": packet.get("generated_date"),
        "packet": packet_for_snapshot(packet),
    }
    output_path = snapshot_dir / f"{stable_id}.json"
    output_path.write_text(json.dumps(envelope, indent=2, sort_keys=True), encoding="utf-8")
    return output_path


def add_item(items: list[dict[str, Any]], kind: str, severity: str, text: str, **extra: Any) -> None:
    items.append({"kind": kind, "severity": severity, "text": text, **extra})


def decision_rows(packet: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {row["decision_id"]: row for row in packet.get("decision_impact", {}).get("rows", [])}


def build_review_diff(
    current_packet: dict[str, Any],
    previous_packet: dict[str, Any] | None,
    *,
    previous_snapshot: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if previous_packet is None:
        return {
            "snapshot_status": "no_snapshot",
            "summary": "No saved review snapshot yet. Save one after this review to enable month-over-month diffing.",
            "previous_snapshot": None,
            "counts": {
                "new_decisions": 0,
                "removed_decisions": 0,
                "status_changes": 0,
                "recommendation_changes": 0,
                "new_actions": 0,
                "removed_actions": 0,
                "new_changelog_items": 0,
            },
            "items": [],
        }

    current_rows = decision_rows(current_packet)
    previous_rows = decision_rows(previous_packet)
    items: list[dict[str, Any]] = []

    for decision_id in sorted(current_rows.keys() - previous_rows.keys()):
        row = current_rows[decision_id]
        add_item(
            items,
            "new_decision",
            "green",
            f"New decision in packet: {decision_id} ({row['status']}, owner={row['owner']}).",
            decision_id=decision_id,
        )
    for decision_id in sorted(previous_rows.keys() - current_rows.keys()):
        add_item(
            items,
            "removed_decision",
            "amber",
            f"Decision no longer appears in packet: {decision_id}.",
            decision_id=decision_id,
        )
    for decision_id in sorted(current_rows.keys() & previous_rows.keys()):
        current = current_rows[decision_id]
        previous = previous_rows[decision_id]
        if current["status"] != previous["status"]:
            add_item(
                items,
                "status_change",
                "amber" if current["status"] != "needs_attention" else "red",
                f"{decision_id} status changed from {previous['status']} to {current['status']}.",
                decision_id=decision_id,
                previous_value=previous["status"],
                current_value=current["status"],
            )
        current_recommendation = current["recommendation"]
        previous_recommendation = previous["recommendation"]
        if (
            current_recommendation["recommended_action"] != previous_recommendation["recommended_action"]
            or current_recommendation["blocker_or_risk"] != previous_recommendation["blocker_or_risk"]
        ):
            add_item(
                items,
                "recommendation_change",
                "amber",
                f"{decision_id} recommendation changed.",
                decision_id=decision_id,
                previous_value=previous_recommendation["recommended_action"],
                current_value=current_recommendation["recommended_action"],
            )

    current_actions = {action_key(action): action for action in current_packet.get("actions", [])}
    previous_actions = {action_key(action): action for action in previous_packet.get("actions", [])}
    for key in sorted(current_actions.keys() - previous_actions.keys()):
        action = current_actions[key]
        add_item(
            items,
            "new_action",
            action.get("severity", "amber"),
            f"New action: {action['text']}",
            decision_id=action.get("decision_id"),
        )
    for key in sorted(previous_actions.keys() - current_actions.keys()):
        action = previous_actions[key]
        add_item(
            items,
            "removed_action",
            "neutral",
            f"Action cleared: {action['text']}",
            decision_id=action.get("decision_id"),
        )

    current_changelog = {
        changelog_key(item): item for item in current_packet.get("decision_changelog", {}).get("items", [])
    }
    previous_changelog = {
        changelog_key(item): item for item in previous_packet.get("decision_changelog", {}).get("items", [])
    }
    for key in sorted(current_changelog.keys() - previous_changelog.keys()):
        item = current_changelog[key]
        add_item(
            items,
            "new_changelog_item",
            item.get("severity", "neutral"),
            f"New changelog item: {item['title']}",
            decision_id=item.get("decision_id"),
        )

    counts = {
        "new_decisions": sum(item["kind"] == "new_decision" for item in items),
        "removed_decisions": sum(item["kind"] == "removed_decision" for item in items),
        "status_changes": sum(item["kind"] == "status_change" for item in items),
        "recommendation_changes": sum(item["kind"] == "recommendation_change" for item in items),
        "new_actions": sum(item["kind"] == "new_action" for item in items),
        "removed_actions": sum(item["kind"] == "removed_action" for item in items),
        "new_changelog_items": sum(item["kind"] == "new_changelog_item" for item in items),
    }
    changed_count = sum(counts.values())
    summary = (
        f"{changed_count} change(s) since the latest saved review snapshot."
        if changed_count
        else "No material changes since the latest saved review snapshot."
    )
    previous_meta = None
    if previous_snapshot:
        previous_meta = {
            "snapshot_id": previous_snapshot.get("snapshot_id"),
            "saved_at": previous_snapshot.get("saved_at"),
            "generated_date": previous_snapshot.get("generated_date"),
        }
    return {
        "snapshot_status": "compared",
        "summary": summary,
        "previous_snapshot": previous_meta,
        "counts": counts,
        "items": items,
    }


def review_diff_from_latest(
    current_packet: dict[str, Any],
    snapshot_dir: Path = DEFAULT_SNAPSHOT_DIR,
) -> dict[str, Any]:
    snapshot = latest_snapshot(snapshot_dir)
    previous_packet = snapshot.get("packet") if snapshot else None
    return build_review_diff(current_packet, previous_packet, previous_snapshot=snapshot)
