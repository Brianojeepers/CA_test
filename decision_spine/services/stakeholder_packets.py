"""Stakeholder-specific packet builders backed by monthly packet data."""

from __future__ import annotations

from collections import Counter
from typing import Any


STAKEHOLDER_VIEWS = [
    {
        "id": "council",
        "label": "Council",
        "title": "Council Review Brief",
        "primary_question": "Which decisions need action, patience, or amplification this month?",
        "focus": ["Action queue", "Decision impact", "Traceability"],
    },
    {
        "id": "learning",
        "label": "Learning",
        "title": "Learning Brief",
        "primary_question": "Which learning changes need evidence, iteration, or stronger implementation quality?",
        "focus": ["Curriculum releases", "Readiness evidence", "Pedagogy links"],
        "decision_types": ["curriculum"],
        "owners": ["Learning"],
    },
    {
        "id": "assessment",
        "label": "Assessment Ops",
        "title": "Assessment Ops Brief",
        "primary_question": "Which assessment decisions need implementation or readiness evidence before confidence increases?",
        "focus": ["Credential thresholds", "Assessment releases", "Readiness risk"],
        "decision_types": ["credential", "assessment"],
        "owners": ["Assessment Ops"],
    },
    {
        "id": "matching",
        "label": "Matching / CSM",
        "title": "Matching and CSM Brief",
        "primary_question": "Which decisions are ready to influence matching narratives, and which need more outcome evidence?",
        "focus": ["Placement evidence", "Client-facing risk", "Outcome maturity"],
        "partner_functions": ["Matching", "CSM"],
    },
    {
        "id": "solutions",
        "label": "Solutions / Sales",
        "title": "Solutions and Sales Brief",
        "primary_question": "Which signals can support client conversations without overstating evidence?",
        "focus": ["Market signal", "Positioning readiness", "Commercial risk"],
        "partner_functions": ["Solutions"],
    },
    {
        "id": "data",
        "label": "Data / Analytics",
        "title": "Data and Analytics Brief",
        "primary_question": "Where is the evidence strong enough to trust, and where is the data still limiting judgment?",
        "focus": ["Data trust", "Evidence maturity", "Measurement gaps"],
        "statuses": ["evidence_emerging", "too_early", "needs_attention", "no_outcome_data"],
    },
]


def stakeholder_view(view_id: str) -> dict[str, Any]:
    for view in STAKEHOLDER_VIEWS:
        if view["id"] == view_id:
            return view
    raise ValueError(f"Unknown stakeholder view: {view_id}")


def intersects(values: list[str], candidates: list[str] | None) -> bool:
    return any(value in (candidates or []) for value in values)


def row_matches_view(row: dict[str, Any], view: dict[str, Any]) -> bool:
    if view["id"] == "council":
        return True
    return (
        intersects([row["owner"]], view.get("owners"))
        or intersects([row["decision_type"]], view.get("decision_types"))
        or intersects(row.get("partner_functions", []), view.get("partner_functions"))
        or intersects([row["status"]], view.get("statuses"))
    )


def rows_for_view(packet: dict[str, Any], view: dict[str, Any]) -> list[dict[str, Any]]:
    return [row for row in packet["decision_impact"]["rows"] if row_matches_view(row, view)]


def actions_for_view(packet: dict[str, Any], rows: list[dict[str, Any]], view: dict[str, Any]) -> list[dict[str, Any]]:
    visible_decision_ids = {row["decision_id"] for row in rows}
    if view["id"] in {"council", "data"}:
        actions = list(packet["actions"])
    else:
        actions = [
            action
            for action in packet["actions"]
            if not action.get("decision_id") or action.get("decision_id") in visible_decision_ids
        ]
    action_decision_ids = {action["decision_id"] for action in actions if action.get("decision_id")}
    recommendation_actions = [
        {
            "kind": "recommendation",
            "severity": "red" if row["status"] == "needs_attention" else "amber",
            "text": f"{view['label']}: {row['decision_id']} - {row['recommendation']['recommended_action']}",
            "decision_id": row["decision_id"],
        }
        for row in rows
        if row["decision_id"] not in action_decision_ids
        and (row["status"] == "needs_attention" or row["recommendation"]["priority"] == "high")
    ]
    return [*actions, *recommendation_actions]


def recommendation_label(row: dict[str, Any]) -> str:
    labels = {
        "positive_signal": "Keep / amplify",
        "evidence_emerging": "Update / monitor",
        "too_early": "Wait",
        "needs_attention": "Update",
        "no_outcome_data": "Wait",
    }
    if row["status"] == "needs_attention" and "suppressed evidence" in row["recommendation"]["blocker_or_risk"]:
        return "Update / consider deprecation"
    return labels.get(row["status"], "Review")


def sort_rows_for_brief(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    priority_order = {"high": 0, "medium": 1, "low": 2}
    status_order = {
        "needs_attention": 0,
        "too_early": 1,
        "evidence_emerging": 2,
        "no_outcome_data": 3,
        "positive_signal": 4,
    }
    return sorted(
        rows,
        key=lambda row: (
            priority_order.get(row["recommendation"]["priority"], 9),
            status_order.get(row["status"], 9),
            row["decision_id"],
        ),
    )


def changelog_for_view(packet: dict[str, Any], rows: list[dict[str, Any]], view: dict[str, Any]) -> list[dict[str, Any]]:
    if view["id"] in {"council", "data"}:
        return packet["decision_changelog"]["items"]
    visible_decision_ids = {row["decision_id"] for row in rows}
    return [
        item
        for item in packet["decision_changelog"]["items"]
        if item["decision_id"] in visible_decision_ids
    ]


def build_stakeholder_packet(packet: dict[str, Any], view_id: str) -> dict[str, Any]:
    from decision_spine.services.stakeholder_gates import build_stakeholder_gate_review

    view = stakeholder_view(view_id)
    rows = rows_for_view(packet, view)
    actions = actions_for_view(packet, rows, view)
    sorted_rows = sort_rows_for_brief(rows)
    status_counts = Counter(row["status"] for row in rows)
    gate_review = build_stakeholder_gate_review(packet=packet)
    view_gate = next(item for item in gate_review["stakeholder_views"] if item["view_id"] == view["id"])
    key_decisions = [
        {
            "decision_id": row["decision_id"],
            "status": row["status"],
            "owner": row["owner"],
            "summary": row["summary"],
            "recommended_action": recommendation_label(row),
            "evidence_basis": row["recommendation"]["evidence_basis"],
            "risk": row["recommendation"]["blocker_or_risk"],
            "next_review_trigger": row["recommendation"]["next_review_trigger"],
        }
        for row in sorted_rows[:5]
    ]
    return {
        "generated_date": packet["generated_date"],
        "view_id": view["id"],
        "label": view["label"],
        "title": view["title"],
        "primary_question": view["primary_question"],
        "focus": view["focus"],
        "scope_count": len(rows),
        "action_count": len(actions),
        "status_counts": dict(status_counts),
        "key_decisions": key_decisions,
        "actions": actions[:6],
        "changelog_items": changelog_for_view(packet, rows, view)[:6],
        "data_trust": packet["data_trust"],
        "stakeholder_gate": view_gate,
        "known_limits": packet["known_limits"][:2],
    }


def build_all_stakeholder_packets(packet: dict[str, Any]) -> list[dict[str, Any]]:
    return [build_stakeholder_packet(packet, view["id"]) for view in STAKEHOLDER_VIEWS]


def render_stakeholder_packet_markdown(brief: dict[str, Any]) -> str:
    lines = [
        f"# {brief['title']}",
        "",
        f"Generated: {brief['generated_date']}",
        "",
        f"Primary question: {brief['primary_question']}",
        "",
        "## At A Glance",
        "",
        f"- Scope: {brief['scope_count']} decision(s).",
        f"- Actions: {brief['action_count']} item(s).",
        f"- Data trust: passed with {brief['data_trust']['warning_count']} warning(s).",
        f"- Review gate: {brief['stakeholder_gate']['mode_label']} "
        f"({brief['stakeholder_gate']['share_ready_count']} share-ready item(s)).",
        f"- Focus: {', '.join(brief['focus'])}.",
        "",
        "## Key Decisions",
        "",
    ]
    if brief["key_decisions"]:
        for decision in brief["key_decisions"]:
            lines.extend(
                [
                    f"- `{decision['decision_id']}` {decision['recommended_action']} ({decision['status']}, owner: {decision['owner']})",
                    f"  - Decision: {decision['summary']}",
                    f"  - Evidence: {decision['evidence_basis']}",
                    f"  - Risk: {decision['risk']}",
                    f"  - Next trigger: {decision['next_review_trigger']}",
                ]
            )
    else:
        lines.append("- No decisions in scope.")

    lines.extend(["", "## Action Items", ""])
    if brief["actions"]:
        lines.extend(f"- {action['text']}" for action in brief["actions"])
    else:
        lines.append("- No action items for this stakeholder lens.")

    gate = brief["stakeholder_gate"]
    lines.extend(["", "## Review Gate", ""])
    lines.append(
        f"- Mode: {gate['mode_label']} "
        f"(follow-up={gate['needs_follow_up_count']}, suppressed={gate['suppressed_count']}, "
        f"internal={gate['internal_only_count']}, unreviewed={gate['unreviewed_count']})."
    )
    if gate["share_ready_items"]:
        lines.append("- Share-ready language:")
        lines.extend(f"  - {item['communication_instruction']}" for item in gate["share_ready_items"][:3])
    else:
        lines.append("- Share-ready language: none accepted by council yet.")
    if gate["follow_up_items"]:
        lines.append("- Follow-up or suppressed items:")
        lines.extend(f"  - {item['communication_instruction']}" for item in gate["follow_up_items"][:3])

    lines.extend(["", "## What Changed", ""])
    if brief["changelog_items"]:
        for item in brief["changelog_items"]:
            lines.extend(
                [
                    f"- `{item['category']}` {item['title']} ({item['status']}, owner: {item['owner']})",
                    f"  - Why: {item['why_it_matters']}",
                    f"  - Next: {item['next_step']}",
                ]
            )
    else:
        lines.append("- No changelog items for this stakeholder lens.")

    lines.extend(["", "## Limits", ""])
    lines.extend(f"- {limit}" for limit in brief["known_limits"])
    lines.append("")
    return "\n".join(lines)
