"""Owner-ready pilot data request pack for v0.2 field gaps."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from decision_spine.services.schema_gap import action_key, build_schema_gap_report


def request_priority(action: dict[str, Any]) -> str:
    if action["blocked"]:
        return "privacy_review"
    if action["action_status"] in {"in_review", "approved"}:
        return "already_moving"
    return "request_definition"


def request_label(priority: str) -> str:
    labels = {
        "privacy_review": "Privacy review required",
        "already_moving": "Already moving",
        "request_definition": "Request field definition",
    }
    return labels.get(priority, "Request field definition")


def build_request_items(schema_gap: dict[str, Any]) -> list[dict[str, Any]]:
    missing_details: dict[str, dict[str, Any]] = {}
    for requirement in schema_gap["v02_requirements"]:
        for field in requirement.get("missing_field_details", []):
            missing_details[action_key(requirement["capability"], field["field"])] = {
                "purpose": field.get("purpose", "Field required by the v0.2 contract."),
                "source_owner": field.get("source_owner", requirement.get("owner", "")),
                "privacy_sensitivity": field.get(
                    "privacy_sensitivity",
                    requirement.get("privacy_sensitivity", ""),
                ),
                "decision_unlocked": field.get(
                    "decision_unlocked",
                    requirement.get("decision_unlocked", ""),
                ),
            }

    requests: list[dict[str, Any]] = []
    for action in schema_gap["field_actions"]:
        key = action_key(action["capability"], action["field"])
        detail = missing_details.get(key, {})
        priority = request_priority(action)
        requests.append(
            {
                "owner": action["source_owner"],
                "capability": action["capability"],
                "capability_label": action["capability_label"],
                "field": action["field"],
                "purpose": detail.get("purpose", "Field required by the v0.2 contract."),
                "privacy_sensitivity": detail.get("privacy_sensitivity", action["privacy_sensitivity"]),
                "decision_unlocked": detail.get("decision_unlocked", action["decision_unlocked"]),
                "status": action["action_status"],
                "status_notes": action["status_notes"],
                "severity": action["severity"],
                "blocked": action["blocked"],
                "request_priority": priority,
                "request_label": request_label(priority),
                "request": action["action_text"],
            }
        )

    priority_order = {"privacy_review": 0, "request_definition": 1, "already_moving": 2}
    return sorted(
        requests,
        key=lambda request: (
            priority_order.get(request["request_priority"], 9),
            request["owner"],
            request["capability_label"],
            request["field"],
        ),
    )


def build_owner_groups(requests: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_owner: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for request in requests:
        by_owner[request["owner"]].append(request)

    owner_groups: list[dict[str, Any]] = []
    for owner, items in sorted(by_owner.items()):
        priorities = Counter(item["request_priority"] for item in items)
        statuses = Counter(item["status"] for item in items)
        owner_groups.append(
            {
                "owner": owner,
                "request_count": len(items),
                "privacy_review_count": priorities["privacy_review"],
                "definition_request_count": priorities["request_definition"],
                "already_moving_count": priorities["already_moving"],
                "status_counts": dict(statuses),
                "requests": items,
            }
        )
    return owner_groups


def build_pilot_request_pack(schema_gap: dict[str, Any] | None = None) -> dict[str, Any]:
    schema_gap = schema_gap or build_schema_gap_report()
    requests = build_request_items(schema_gap)
    priorities = Counter(item["request_priority"] for item in requests)
    owners = sorted({item["owner"] for item in requests})

    return {
        "summary": {
            "request_count": len(requests),
            "owner_count": len(owners),
            "privacy_review_count": priorities["privacy_review"],
            "definition_request_count": priorities["request_definition"],
            "already_moving_count": priorities["already_moving"],
        },
        "purpose": "Convert v0.2 field gaps into owner-ready pilot data requests before live ingestion or database migration.",
        "guardrails": [
            "Use summarized or aggregated data only unless privacy review explicitly approves more detail.",
            "Do not use requested fields in recommendations until source owner, privacy posture, and freshness are confirmed.",
            "Learner-derived and outcome-derived fields require extra suppression review before pilot use.",
        ],
        "owner_groups": build_owner_groups(requests),
        "requests": requests,
    }


def field_label(value: str) -> str:
    return value.replace("_", " ")


def render_pilot_request_pack_markdown(pack: dict[str, Any]) -> str:
    summary = pack["summary"]
    lines = [
        "# v0.2 Pilot Data Request Pack",
        "",
        pack["purpose"],
        "",
        "## Summary",
        "",
        f"- {summary['request_count']} field request(s) across {summary['owner_count']} owner(s).",
        f"- {summary['privacy_review_count']} privacy-review request(s).",
        f"- {summary['definition_request_count']} field-definition request(s).",
        "",
        "## Guardrails",
        "",
    ]
    lines.extend(f"- {guardrail}" for guardrail in pack["guardrails"])
    for group in pack["owner_groups"]:
        lines.extend(
            [
                "",
                f"## {group['owner']}",
                "",
                f"{group['request_count']} request(s); {group['privacy_review_count']} privacy-review item(s).",
                "",
            ]
        )
        for request in group["requests"]:
            lines.extend(
                [
                    f"### {field_label(request['field'])}",
                    "",
                    f"- Capability: {request['capability_label']}",
                    f"- Request type: {request['request_label']}",
                    f"- Current status: {field_label(request['status'])}",
                    f"- Privacy: {field_label(request['privacy_sensitivity'])}",
                    f"- Why needed: {request['purpose']}",
                    f"- Unlocks: {request['decision_unlocked']}",
                    f"- Next request: {request['request']}",
                    "",
                ]
            )
    return "\n".join(lines).rstrip() + "\n"
