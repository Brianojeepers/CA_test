"""Review source-owner responses to v0.2 pilot data requests."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from decision_spine.services.pilot_request_pack import build_pilot_request_pack, field_label
from decision_spine.services.schema_gap import DATA_DIR, action_key


PILOT_RESPONSE_FILE = DATA_DIR / "pilot_request_responses.json"
INTAKE_STATUSES = ("accepted", "needs_clarification", "privacy_blocked", "not_ready")
STATUS_LABELS = {
    "accepted": "Accepted for pilot schema design",
    "needs_clarification": "Needs clarification",
    "privacy_blocked": "Privacy blocked",
    "not_ready": "Not ready",
}
STATUS_TONES = {
    "accepted": "green",
    "needs_clarification": "amber",
    "privacy_blocked": "red",
    "not_ready": "neutral",
}
APPROVED_PRIVACY_DECISIONS = {"not_required", "summary_approved", "aggregate_approved"}


def load_pilot_response_records(path: Path | None = None) -> list[dict[str, Any]]:
    path = path or PILOT_RESPONSE_FILE
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, list):
        raise ValueError(f"{path}: expected top-level JSON list")
    return data


def responses_by_key(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    by_key: dict[str, dict[str, Any]] = {}
    for record in records:
        by_key[action_key(str(record.get("capability", "")), str(record.get("field", "")))] = record
    return by_key


def missing_response_detail(response: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    for field in ("source_contract_id", "proposed_grain", "freshness_sla", "notes"):
        value = response.get(field)
        if not isinstance(value, str) or not value.strip():
            missing.append(field)
    if not isinstance(response.get("sample_available"), bool):
        missing.append("sample_available")
    return missing


def classify_intake(request: dict[str, Any], response: dict[str, Any] | None) -> tuple[str, str, str]:
    if response is None:
        return (
            "not_ready",
            "No source-owner intake response has been recorded for this field.",
            "Request a response before using this field in schema design.",
        )

    response_status = str(response.get("response_status", "not_ready"))
    privacy_decision = str(response.get("privacy_decision", "pending"))
    missing_details = missing_response_detail(response)

    if privacy_decision == "blocked" or response_status == "privacy_blocked":
        return (
            "privacy_blocked",
            "The recorded privacy decision blocks pilot use.",
            "Resolve privacy review before schema or ingestion work.",
        )
    if request["blocked"] and privacy_decision not in APPROVED_PRIVACY_DECISIONS:
        return (
            "privacy_blocked",
            "This field needs privacy approval before it can be used.",
            "Resolve suppression and privacy approval before schema or ingestion work.",
        )
    if response_status == "needs_clarification" or missing_details:
        detail = f" Missing: {', '.join(missing_details)}." if missing_details else ""
        return (
            "needs_clarification",
            f"The owner response needs more definition before schema design.{detail}",
            "Clarify field definition, grain, freshness, or owner commitment.",
        )
    if response_status == "not_ready" or response.get("sample_available") is not True:
        return (
            "not_ready",
            "The owner cannot provide a usable pilot sample yet.",
            "Keep this field out of schema design until a sample can be reviewed.",
        )
    if response_status == "accepted" and privacy_decision in APPROVED_PRIVACY_DECISIONS:
        return (
            "accepted",
            "The owner response supplies grain, freshness, privacy posture, and sample availability.",
            "Candidate field for schema design once extract shape is reviewed.",
        )
    return (
        "needs_clarification",
        "The owner response does not yet meet the pilot intake gate.",
        "Clarify status, privacy decision, and sample availability.",
    )


def build_intake_items(
    request_pack: dict[str, Any],
    responses: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for request in request_pack["requests"]:
        key = action_key(request["capability"], request["field"])
        response = responses.get(key)
        intake_status, rationale, next_step = classify_intake(request, response)
        items.append(
            {
                "owner": request["owner"],
                "capability": request["capability"],
                "capability_label": request["capability_label"],
                "field": request["field"],
                "privacy_sensitivity": request["privacy_sensitivity"],
                "request_priority": request["request_priority"],
                "request_label": request["request_label"],
                "response": response,
                "response_recorded": response is not None,
                "intake_status": intake_status,
                "intake_label": STATUS_LABELS[intake_status],
                "tone": STATUS_TONES[intake_status],
                "rationale": rationale,
                "next_step": next_step,
            }
        )

    status_order = {"privacy_blocked": 0, "needs_clarification": 1, "not_ready": 2, "accepted": 3}
    return sorted(
        items,
        key=lambda item: (
            status_order.get(item["intake_status"], 9),
            item["owner"],
            item["capability_label"],
            item["field"],
        ),
    )


def build_capability_groups(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_capability: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in items:
        by_capability[item["capability"]].append(item)

    groups: list[dict[str, Any]] = []
    for capability, capability_items in sorted(by_capability.items()):
        counts = Counter(item["intake_status"] for item in capability_items)
        total = len(capability_items)
        if counts["privacy_blocked"]:
            readiness = "privacy_blocked"
        elif counts["accepted"] == total:
            readiness = "pilot_ready"
        elif counts["accepted"]:
            readiness = "partial"
        elif counts["needs_clarification"]:
            readiness = "needs_clarification"
        else:
            readiness = "not_ready"
        groups.append(
            {
                "capability": capability,
                "capability_label": capability_items[0]["capability_label"],
                "readiness": readiness,
                "readiness_label": {
                    "pilot_ready": "Pilot-ready",
                    "partial": "Partially ready",
                    "needs_clarification": "Needs clarification",
                    "privacy_blocked": "Privacy blocked",
                    "not_ready": "Not ready",
                }[readiness],
                "tone": {
                    "pilot_ready": "green",
                    "partial": "amber",
                    "needs_clarification": "amber",
                    "privacy_blocked": "red",
                    "not_ready": "neutral",
                }[readiness],
                "field_count": total,
                "accepted_count": counts["accepted"],
                "needs_clarification_count": counts["needs_clarification"],
                "privacy_blocked_count": counts["privacy_blocked"],
                "not_ready_count": counts["not_ready"],
                "items": sorted(capability_items, key=lambda item: item["field"]),
            }
        )

    readiness_order = {"privacy_blocked": 0, "partial": 1, "needs_clarification": 2, "not_ready": 3, "pilot_ready": 4}
    return sorted(groups, key=lambda group: (readiness_order[group["readiness"]], group["capability_label"]))


def build_owner_groups(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_owner: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in items:
        by_owner[item["owner"]].append(item)

    groups: list[dict[str, Any]] = []
    for owner, owner_items in sorted(by_owner.items()):
        counts = Counter(item["intake_status"] for item in owner_items)
        groups.append(
            {
                "owner": owner,
                "field_count": len(owner_items),
                "accepted_count": counts["accepted"],
                "needs_clarification_count": counts["needs_clarification"],
                "privacy_blocked_count": counts["privacy_blocked"],
                "not_ready_count": counts["not_ready"],
                "items": owner_items,
            }
        )
    return groups


def build_pilot_intake_review(
    request_pack: dict[str, Any] | None = None,
    response_records: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    request_pack = request_pack or build_pilot_request_pack()
    response_records = response_records if response_records is not None else load_pilot_response_records()
    items = build_intake_items(request_pack, responses_by_key(response_records))
    counts = Counter(item["intake_status"] for item in items)
    capability_groups = build_capability_groups(items)
    return {
        "summary": {
            "field_count": len(items),
            "response_count": sum(1 for item in items if item["response_recorded"]),
            "accepted_count": counts["accepted"],
            "needs_clarification_count": counts["needs_clarification"],
            "privacy_blocked_count": counts["privacy_blocked"],
            "not_ready_count": counts["not_ready"],
            "capability_count": len(capability_groups),
            "pilot_ready_capability_count": sum(1 for group in capability_groups if group["readiness"] == "pilot_ready"),
        },
        "purpose": "Check whether source-owner responses are usable enough to inform v0.2 pilot schema design.",
        "guardrails": [
            "Accepted intake means a field can enter schema design, not live ingestion.",
            "Privacy-blocked fields stay out of schemas until suppression and storage rules are approved.",
            "Partial capability readiness should drive targeted clarification, not broad database work.",
        ],
        "capability_groups": capability_groups,
        "owner_groups": build_owner_groups(items),
        "items": items,
    }


def render_pilot_intake_review_text(review: dict[str, Any]) -> str:
    summary = review["summary"]
    lines = [
        "Pilot Intake Review",
        "===================",
        "",
        review["purpose"],
        "",
        "Summary",
        "-------",
        f"- fields={summary['field_count']} responses={summary['response_count']} capabilities={summary['capability_count']}",
        f"- accepted={summary['accepted_count']} needs_clarification={summary['needs_clarification_count']} privacy_blocked={summary['privacy_blocked_count']} not_ready={summary['not_ready_count']}",
        f"- pilot_ready_capabilities={summary['pilot_ready_capability_count']}",
        "",
        "Guardrails",
        "----------",
    ]
    lines.extend(f"- {guardrail}" for guardrail in review["guardrails"])
    lines.extend(["", "Capability Readiness", "--------------------"])
    for group in review["capability_groups"]:
        lines.append(
            f"- [{group['readiness']}] {group['capability_label']}: "
            f"{group['accepted_count']}/{group['field_count']} accepted; "
            f"clarify={group['needs_clarification_count']} privacy={group['privacy_blocked_count']} not_ready={group['not_ready_count']}"
        )
    lines.extend(["", "Field Intake Actions", "--------------------"])
    for item in review["items"]:
        response = item.get("response") or {}
        lines.extend(
            [
                f"- [{item['intake_status']}] {item['owner']}: {field_label(item['field'])} ({item['capability_label']})",
                f"  reason: {item['rationale']}",
                f"  next: {item['next_step']}",
                f"  grain: {response.get('proposed_grain', 'not recorded')}",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"
