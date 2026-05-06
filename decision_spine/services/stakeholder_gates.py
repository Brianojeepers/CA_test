"""Review-gated stakeholder communication mode."""

from __future__ import annotations

from collections import Counter
from typing import Any

from decision_spine.services.review_workflow import UNREVIEWED_OUTCOME, build_review_workflow
from decision_spine.services.stakeholder_packets import STAKEHOLDER_VIEWS


GATE_CATALOG = {
    "share_ready": {
        "label": "Share-ready",
        "meaning": "Council has accepted bounded language for this item.",
    },
    "needs_follow_up": {
        "label": "Needs follow-up",
        "meaning": "Use only as an owner follow-up prompt until review closes.",
    },
    "suppressed": {
        "label": "Suppressed",
        "meaning": "Keep out of stakeholder claims until the blocker clears.",
    },
    "internal_only": {
        "label": "Internal only",
        "meaning": "Keep in operating review; do not include in share-ready summaries.",
    },
    "unreviewed": {
        "label": "Unreviewed",
        "meaning": "No council outcome has been recorded yet.",
    },
}

OUTCOME_TO_GATE_STATE = {
    "accepted": "share_ready",
    "needs_follow_up": "needs_follow_up",
    "blocked": "suppressed",
    "deferred": "internal_only",
    UNREVIEWED_OUTCOME: "unreviewed",
}

ALL_STAKEHOLDER_VIEW_IDS = [view["id"] for view in STAKEHOLDER_VIEWS]

OWNER_VIEW_MAP = {
    "Academy Operations": ["learning", "matching"],
    "Assessment Ops": ["assessment"],
    "Council Chair": ["council"],
    "Data and Analytics": ["data"],
    "Delivery": ["learning", "matching"],
    "Learning": ["learning"],
    "Learning Architecture": ["learning"],
    "Learning Design": ["learning"],
    "Market Intelligence": ["solutions"],
    "Matching Operations": ["matching"],
    "Research": ["solutions"],
    "Signal Intelligence Council": ["council"],
}

STEP_VIEW_MAP = {
    "trust_posture": ALL_STAKEHOLDER_VIEW_IDS,
    "reasoning_stress": ALL_STAKEHOLDER_VIEW_IDS,
    "source_blockers": ["council", "data"],
    "decision_policy": ["council"],
    "action_queue": ["council"],
}

GATE_SORT_ORDER = {
    "suppressed": 0,
    "needs_follow_up": 1,
    "unreviewed": 2,
    "internal_only": 3,
    "share_ready": 4,
}


def stakeholder_views_for_item(item: dict[str, Any]) -> list[str]:
    view_ids = set(STEP_VIEW_MAP.get(item["step_id"], ["council"]))
    view_ids.update(OWNER_VIEW_MAP.get(item.get("owner", ""), []))
    if item.get("severity") == "red":
        view_ids.add("data")
    return [view_id for view_id in ALL_STAKEHOLDER_VIEW_IDS if view_id in view_ids]


def gate_state_for_outcome(outcome: str) -> str:
    return OUTCOME_TO_GATE_STATE.get(outcome, "unreviewed")


def gate_instruction(item: dict[str, Any], gate_state: str) -> str:
    if gate_state == "share_ready":
        return f"Share only bounded language: {item['summary']}"
    if gate_state == "needs_follow_up":
        return f"Use as a follow-up prompt for {item['owner']}: {item['review_prompt']}"
    if gate_state == "suppressed":
        return f"Suppress from stakeholder claims until this blocker clears: {item['summary']}"
    if gate_state == "internal_only":
        return f"Keep internal unless the council reopens it: {item['summary']}"
    return f"Keep internal until a council outcome is recorded: {item['title']}"


def gate_item_from_review_item(item: dict[str, Any]) -> dict[str, Any]:
    gate_state = gate_state_for_outcome(item["review_outcome"])
    return {
        "step_id": item["step_id"],
        "item_id": item["item_id"],
        "title": item["title"],
        "summary": item["summary"],
        "owner": item["owner"],
        "severity": item["severity"],
        "source_ref": item.get("source_ref", ""),
        "review_outcome": item["review_outcome"],
        "review_outcome_label": item["review_outcome_label"],
        "gate_state": gate_state,
        "gate_label": GATE_CATALOG[gate_state]["label"],
        "stakeholder_view_ids": stakeholder_views_for_item(item),
        "communication_instruction": gate_instruction(item, gate_state),
    }


def sort_gate_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        items,
        key=lambda item: (
            GATE_SORT_ORDER.get(item["gate_state"], 9),
            item["severity"] != "red",
            item["owner"],
            item["title"],
        ),
    )


def view_mode_from_counts(counts: Counter[str]) -> str:
    if counts["suppressed"]:
        return "suppressed"
    if counts["needs_follow_up"]:
        return "needs_follow_up"
    if counts["unreviewed"]:
        return "unreviewed"
    if counts["internal_only"]:
        return "internal_only"
    return "share_ready"


def build_view_gate(view: dict[str, Any], items: list[dict[str, Any]]) -> dict[str, Any]:
    view_items = [item for item in items if view["id"] in item["stakeholder_view_ids"]]
    counts = Counter(item["gate_state"] for item in view_items)
    mode = view_mode_from_counts(counts)
    return {
        "view_id": view["id"],
        "label": view["label"],
        "mode": mode,
        "mode_label": GATE_CATALOG[mode]["label"],
        "item_count": len(view_items),
        "share_ready_count": counts["share_ready"],
        "needs_follow_up_count": counts["needs_follow_up"],
        "suppressed_count": counts["suppressed"],
        "internal_only_count": counts["internal_only"],
        "unreviewed_count": counts["unreviewed"],
        "share_ready_items": [item for item in view_items if item["gate_state"] == "share_ready"][:5],
        "follow_up_items": [
            item for item in view_items if item["gate_state"] in {"needs_follow_up", "suppressed"}
        ][:5],
        "internal_items": [
            item for item in view_items if item["gate_state"] in {"internal_only", "unreviewed"}
        ][:5],
    }


def flatten_review_items(workflow: dict[str, Any]) -> list[dict[str, Any]]:
    return [item for step in workflow["steps"] for item in step["items"]]


def build_stakeholder_gate_review(
    *,
    packet: dict[str, Any] | None = None,
    workflow: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if workflow is None:
        workflow = build_review_workflow(packet=packet)
    items = sort_gate_items([gate_item_from_review_item(item) for item in flatten_review_items(workflow)])
    counts = Counter(item["gate_state"] for item in items)
    view_gates = [build_view_gate(view, items) for view in STAKEHOLDER_VIEWS]
    return {
        "generated_date": workflow["generated_date"],
        "purpose": (
            "Convert council review outcomes into stakeholder communication permissions: "
            "share-ready, follow-up, suppressed, internal-only, or unreviewed."
        ),
        "guardrails": [
            "Accepted means share bounded language, not production-grade proof.",
            "Blocked review items are suppressed from stakeholder claims.",
            "Deferred and unreviewed items stay internal until council records a new outcome.",
            "Needs-follow-up items can appear only as owner actions, not as evidence claims.",
        ],
        "summary": {
            "item_count": len(items),
            "share_ready_count": counts["share_ready"],
            "needs_follow_up_count": counts["needs_follow_up"],
            "suppressed_count": counts["suppressed"],
            "internal_only_count": counts["internal_only"],
            "unreviewed_count": counts["unreviewed"],
            "stakeholder_view_count": len(view_gates),
            "share_ready_view_count": sum(1 for view in view_gates if view["mode"] == "share_ready"),
        },
        "gate_catalog": [{"state": state, **definition} for state, definition in GATE_CATALOG.items()],
        "items": items,
        "stakeholder_views": view_gates,
        "share_ready_language": [item for item in items if item["gate_state"] == "share_ready"][:8],
        "blocked_or_follow_up": [
            item for item in items if item["gate_state"] in {"suppressed", "needs_follow_up"}
        ][:8],
        "internal_only_language": [
            item for item in items if item["gate_state"] in {"internal_only", "unreviewed"}
        ][:8],
    }


def stakeholder_gate_summary_from_review(gate_review: dict[str, Any] | None = None) -> dict[str, Any]:
    gate_review = gate_review or build_stakeholder_gate_review()
    summary = gate_review["summary"]
    return {
        "share_ready_count": summary["share_ready_count"],
        "needs_follow_up_count": summary["needs_follow_up_count"],
        "suppressed_count": summary["suppressed_count"],
        "internal_only_count": summary["internal_only_count"],
        "unreviewed_count": summary["unreviewed_count"],
        "stakeholder_view_count": summary["stakeholder_view_count"],
        "share_ready_view_count": summary["share_ready_view_count"],
    }


def render_stakeholder_gate_text(gate_review: dict[str, Any]) -> str:
    summary = gate_review["summary"]
    lines = [
        "Stakeholder Gate Review",
        "=======================",
        "",
        f"Generated: {gate_review['generated_date']}",
        "",
        gate_review["purpose"],
        "",
        "Summary",
        "-------",
        (
            f"- items={summary['item_count']} share_ready={summary['share_ready_count']} "
            f"follow_up={summary['needs_follow_up_count']} suppressed={summary['suppressed_count']} "
            f"internal={summary['internal_only_count']} unreviewed={summary['unreviewed_count']}"
        ),
        f"- share_ready_views={summary['share_ready_view_count']}/{summary['stakeholder_view_count']}",
        "",
        "Guardrails",
        "----------",
    ]
    lines.extend(f"- {guardrail}" for guardrail in gate_review["guardrails"])

    lines.extend(["", "Stakeholder Modes", "-----------------"])
    for view in gate_review["stakeholder_views"]:
        lines.append(
            f"- [{view['mode']}] {view['label']}: share={view['share_ready_count']} "
            f"follow_up={view['needs_follow_up_count']} suppressed={view['suppressed_count']} "
            f"internal={view['internal_only_count']} unreviewed={view['unreviewed_count']}"
        )
        for item in [*view["follow_up_items"], *view["share_ready_items"]][:3]:
            lines.append(f"  - {item['gate_label']}: {item['title']} ({item['owner']})")

    lines.extend(["", "Share-Ready Language", "--------------------"])
    if gate_review["share_ready_language"]:
        lines.extend(f"- {item['communication_instruction']}" for item in gate_review["share_ready_language"])
    else:
        lines.append("- No share-ready language has been accepted by council yet.")

    lines.extend(["", "Internal Or Suppressed", "----------------------"])
    for item in [*gate_review["blocked_or_follow_up"], *gate_review["internal_only_language"]][:8]:
        lines.append(f"- [{item['gate_state']}] {item['communication_instruction']}")
    lines.append("")
    return "\n".join(lines)
