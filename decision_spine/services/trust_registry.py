"""Summarize source coverage and trust posture by stakeholder surface."""

from __future__ import annotations

import json
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
SOURCE_CONTRACTS_FILE = DATA_DIR / "source_contracts.json"
TODAY = date.today()


TRUST_SURFACES: tuple[dict[str, Any], ...] = (
    {
        "surface_id": "monthly_packet",
        "label": "Monthly council packet",
        "surface_type": "evidence_surface",
        "stakeholders": ["Signal Intelligence Council", "Executive stakeholders"],
        "source_files": [
            "signals.json",
            "decisions.json",
            "releases.json",
            "cohort_outcomes.json",
            "predictions.json",
            "role_competencies.json",
            "learner_evidence_summary.json",
        ],
        "control_files": ["outputs/monthly_packet.md"],
        "decision_use": "Monthly action review, decision impact posture, KPI posture, and known limits.",
        "known_limit": "Uses synthetic seed data and inherits privacy blockers from learner evidence and cohort outcomes.",
    },
    {
        "surface_id": "stakeholder_briefs",
        "label": "Stakeholder Markdown briefs",
        "surface_type": "evidence_surface",
        "stakeholders": ["Learning", "Assessment Ops", "Matching", "Solutions", "Sales", "Delivery"],
        "source_files": [
            "signals.json",
            "decisions.json",
            "releases.json",
            "cohort_outcomes.json",
            "role_competencies.json",
            "learner_evidence_summary.json",
        ],
        "control_files": ["outputs/stakeholder_packets/"],
        "decision_use": "Translate shared evidence into stakeholder-specific action briefings.",
        "known_limit": "Briefs should not be treated as operational truth until source contracts clear real-data gates.",
    },
    {
        "surface_id": "dashboard_prototype",
        "label": "Local stakeholder dashboard",
        "surface_type": "evidence_surface",
        "stakeholders": ["Council", "Learning", "Assessment Ops", "Matching", "Solutions", "Sales", "Delivery"],
        "source_files": [
            "signals.json",
            "decisions.json",
            "releases.json",
            "cohort_outcomes.json",
            "predictions.json",
            "role_competencies.json",
            "learner_evidence_summary.json",
        ],
        "control_files": ["web/", "app/api/main.py"],
        "decision_use": "Interactive workflow discovery across insights, trust badges, decisions, packets, and v0.2 readiness.",
        "known_limit": "The dashboard is a local prototype; it should disclose confidence and source coverage before claims.",
    },
    {
        "surface_id": "decision_impact_review",
        "label": "Decision impact review",
        "surface_type": "evidence_surface",
        "stakeholders": ["Signal Intelligence Council", "Executive stakeholders", "Data and Analytics"],
        "source_files": [
            "decisions.json",
            "releases.json",
            "cohort_outcomes.json",
            "role_competencies.json",
            "learner_evidence_summary.json",
        ],
        "control_files": ["scripts/decision_impact_review.py"],
        "decision_use": "Classify whether approved decisions are too early, promising, positive, or need attention.",
        "known_limit": "Impact status is directional until outcome and learner evidence sources clear privacy and aggregation rules.",
    },
    {
        "surface_id": "v02_intelligence_preview",
        "label": "v0.2 intelligence preview",
        "surface_type": "evidence_surface",
        "stakeholders": ["Signal Intelligence Council", "Market Intelligence", "Learning", "Matching"],
        "source_files": [
            "signals.json",
            "predictions.json",
            "releases.json",
            "role_competencies.json",
            "learner_evidence_summary.json",
        ],
        "control_files": ["data/v02_intelligence_requirements.json", "scripts/v02_intelligence_preview.py"],
        "decision_use": "Preview role demand, competency gaps, horizon radar, and curriculum impact with hard recommendations disabled.",
        "known_limit": "Expanded intelligence remains directional until real pilot fields pass ownership, privacy, and freshness gates.",
    },
    {
        "surface_id": "schema_gap_workbench",
        "label": "Schema gap workbench",
        "surface_type": "control_surface",
        "stakeholders": ["Data and Analytics", "Source owners", "Signal Intelligence Council"],
        "source_files": [],
        "control_files": [
            "data/source_contracts.json",
            "data/v02_intelligence_requirements.json",
            "data/pilot_extract_templates/",
            "scripts/schema_gap_review.py",
        ],
        "uses_contract_register": True,
        "decision_use": "Expose missing fields, source-owner gaps, and privacy blockers before schema work.",
        "known_limit": "This is a planning control, not proof that the underlying real sources are ready.",
    },
    {
        "surface_id": "pilot_request_pack",
        "label": "Pilot request pack",
        "surface_type": "control_surface",
        "stakeholders": ["Source owners", "Data and Analytics", "Signal Intelligence Council"],
        "source_files": [],
        "control_files": ["outputs/pilot_request_pack.md", "scripts/export_pilot_request_pack.py"],
        "uses_contract_register": True,
        "decision_use": "Turn missing v0.2 fields into owner-ready pilot requests.",
        "known_limit": "Requests are not source-owner approval and should not trigger schema or ingestion work by themselves.",
    },
    {
        "surface_id": "pilot_intake_review",
        "label": "Pilot intake review",
        "surface_type": "control_surface",
        "stakeholders": ["Source owners", "Data and Analytics", "Signal Intelligence Council"],
        "source_files": [],
        "control_files": ["data/pilot_request_responses.json", "scripts/pilot_intake_review.py"],
        "uses_contract_register": True,
        "decision_use": "Classify owner responses as accepted, unclear, privacy blocked, or not ready before schema design.",
        "known_limit": "Current intake records are synthetic planning records, not real source-owner approvals.",
    },
    {
        "surface_id": "source_ingestion_review",
        "label": "Source ingestion review",
        "surface_type": "control_surface",
        "stakeholders": ["Source owners", "Data and Analytics", "Signal Intelligence Council"],
        "source_files": [],
        "control_files": ["data/source_contracts.json", "scripts/source_ingestion_review.py"],
        "uses_contract_register": True,
        "decision_use": "Define the canonical ingestion envelope and rate source freshness, allowed use, and standardization risk.",
        "known_limit": "This is not approval for live ingestion, source connectors, landing tables, or database schemas.",
    },
)


TRUST_STATUS_LABELS = {
    "privacy_blocked": "Privacy blocked",
    "manual_sampling_only": "Manual sampling only",
    "pilot_candidate": "Pilot candidate",
    "planning_ready": "Planning control ready",
    "unmapped": "Unmapped",
}


def load_source_contracts(path: Path = SOURCE_CONTRACTS_FILE) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, list):
        raise ValueError(f"{path}: expected top-level JSON list")
    return data


def contracts_by_file(contracts: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    by_file: dict[str, list[dict[str, Any]]] = {}
    for contract in contracts:
        for filename in contract.get("feeds_files", []):
            by_file.setdefault(str(filename), []).append(contract)
    return by_file


def unique_contracts(contracts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for contract in contracts:
        contract_id = str(contract.get("contract_id", ""))
        if contract_id in seen:
            continue
        seen.add(contract_id)
        unique.append(contract)
    return sorted(unique, key=lambda contract: str(contract["contract_id"]))


def classify_trust_status(surface: dict[str, Any], counts: Counter[str], uncovered_source_files: list[str]) -> tuple[str, str, str]:
    if uncovered_source_files:
        return (
            "unmapped",
            "low",
            "At least one source file has no source contract, so coverage is not inspectable.",
        )
    if surface["surface_type"] == "control_surface":
        return (
            "planning_ready",
            "medium",
            "This surface exposes planning gaps and blockers; it does not make evidence claims.",
        )
    if counts["red"]:
        return (
            "privacy_blocked",
            "low",
            "One or more supporting sources are privacy-blocked for real-data use.",
        )
    if counts["amber"]:
        return (
            "manual_sampling_only",
            "low",
            "Supporting sources can be manually sampled, but ownership or definitions still need confirmation.",
        )
    if counts["green"]:
        return (
            "pilot_candidate",
            "medium",
            "Supporting sources are green for a controlled pilot extract, but the MVP still uses synthetic seed data.",
        )
    return ("unmapped", "low", "No supporting source contracts are linked.")


def data_state_for(status: str) -> str:
    return {
        "privacy_blocked": "synthetic_seed_with_real_data_blockers",
        "manual_sampling_only": "synthetic_seed_with_manual_sampling_gate",
        "pilot_candidate": "synthetic_seed_with_pilot_candidate_sources",
        "planning_ready": "synthetic_planning_control",
        "unmapped": "unmapped",
    }[status]


def build_surface_records(surfaces: tuple[dict[str, Any], ...], contracts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_file = contracts_by_file(contracts)
    records: list[dict[str, Any]] = []
    for surface in surfaces:
        linked: list[dict[str, Any]] = []
        uncovered_source_files: list[str] = []
        for filename in surface["source_files"]:
            file_contracts = by_file.get(filename, [])
            if file_contracts:
                linked.extend(file_contracts)
            else:
                uncovered_source_files.append(filename)

        if surface.get("uses_contract_register"):
            linked.extend(contracts)

        linked_contracts = unique_contracts(linked)
        counts = Counter(str(contract["readiness"]) for contract in linked_contracts)
        status, stakeholder_confidence, rationale = classify_trust_status(surface, counts, uncovered_source_files)
        red_contracts = [contract for contract in linked_contracts if contract["readiness"] == "red"]
        amber_contracts = [contract for contract in linked_contracts if contract["readiness"] == "amber"]
        records.append(
            {
                "surface_id": surface["surface_id"],
                "label": surface["label"],
                "surface_type": surface["surface_type"],
                "stakeholders": surface["stakeholders"],
                "source_files": surface["source_files"],
                "control_files": surface["control_files"],
                "source_contract_ids": [contract["contract_id"] for contract in linked_contracts],
                "source_readiness_counts": {
                    "green": counts["green"],
                    "amber": counts["amber"],
                    "red": counts["red"],
                },
                "uncovered_source_files": uncovered_source_files,
                "trust_status": status,
                "trust_label": TRUST_STATUS_LABELS[status],
                "stakeholder_confidence": stakeholder_confidence,
                "data_state": data_state_for(status),
                "decision_grade": False,
                "rationale": rationale,
                "decision_use": surface["decision_use"],
                "known_limit": surface["known_limit"],
                "blocked_contracts": [
                    {
                        "contract_id": contract["contract_id"],
                        "data_domain": contract["data_domain"],
                        "next_action": contract["next_action"],
                    }
                    for contract in red_contracts
                ],
                "manual_sampling_contracts": [
                    {
                        "contract_id": contract["contract_id"],
                        "data_domain": contract["data_domain"],
                        "next_action": contract["next_action"],
                    }
                    for contract in amber_contracts
                ],
                "next_trust_action": next_trust_action(status, red_contracts, amber_contracts, uncovered_source_files),
            }
        )
    status_order = {"privacy_blocked": 0, "manual_sampling_only": 1, "unmapped": 2, "planning_ready": 3, "pilot_candidate": 4}
    return sorted(records, key=lambda record: (status_order[record["trust_status"]], record["label"]))


def next_trust_action(
    status: str,
    red_contracts: list[dict[str, Any]],
    amber_contracts: list[dict[str, Any]],
    uncovered_source_files: list[str],
) -> str:
    if status == "unmapped":
        return f"Create source contracts for: {', '.join(uncovered_source_files)}."
    if status == "privacy_blocked":
        domains = ", ".join(contract["data_domain"] for contract in red_contracts)
        return f"Clear privacy and aggregation blockers for: {domains}."
    if status == "manual_sampling_only":
        domains = ", ".join(contract["data_domain"] for contract in amber_contracts)
        return f"Confirm ownership, field definitions, and freshness for: {domains}."
    if status == "planning_ready":
        return "Use this control to expose blockers; keep schema, ingestion, and database work deferred."
    return "Run a controlled pilot extract before raising stakeholder confidence."


def build_priority_trust_actions(contracts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    for contract in sorted(contracts, key=lambda item: ({"red": 0, "amber": 1, "green": 2}[item["readiness"]], item["contract_id"])):
        if contract["readiness"] == "green":
            continue
        actions.append(
            {
                "severity": contract["readiness"],
                "contract_id": contract["contract_id"],
                "data_domain": contract["data_domain"],
                "owner": contract["source_owner"],
                "privacy_owner": contract["privacy_owner"],
                "next_action": contract["next_action"],
            }
        )
    return actions


def build_trust_registry(
    contracts: list[dict[str, Any]] | None = None,
    surfaces: tuple[dict[str, Any], ...] = TRUST_SURFACES,
) -> dict[str, Any]:
    contracts = contracts if contracts is not None else load_source_contracts()
    source_counts = Counter(str(contract["readiness"]) for contract in contracts)
    surface_records = build_surface_records(surfaces, contracts)
    surface_counts = Counter(record["trust_status"] for record in surface_records)
    return {
        "generated_date": TODAY.isoformat(),
        "purpose": (
            "Show what each stakeholder-facing surface can be trusted to say, "
            "which source contracts support it, and what must clear before claims become decision-grade."
        ),
        "summary": {
            "source_contract_count": len(contracts),
            "green_source_count": source_counts["green"],
            "amber_source_count": source_counts["amber"],
            "red_source_count": source_counts["red"],
            "surface_count": len(surface_records),
            "privacy_blocked_surface_count": surface_counts["privacy_blocked"],
            "manual_sampling_surface_count": surface_counts["manual_sampling_only"],
            "planning_ready_surface_count": surface_counts["planning_ready"],
            "pilot_candidate_surface_count": surface_counts["pilot_candidate"],
            "decision_grade_surface_count": sum(1 for record in surface_records if record["decision_grade"]),
        },
        "guardrails": [
            "Synthetic seed data can support workflow design, not production claims.",
            "Red source contracts block real-data use for any surface that depends on them.",
            "Amber source contracts require manual sampling and owner confirmation before trust increases.",
            "Control surfaces can expose blockers without making the underlying evidence decision-grade.",
            "No database, warehouse, or scheduled-ingestion work should start from this registry alone.",
        ],
        "surfaces": surface_records,
        "priority_trust_actions": build_priority_trust_actions(contracts),
    }


def render_trust_registry_text(registry: dict[str, Any]) -> str:
    summary = registry["summary"]
    lines = [
        "Trust and Source Coverage Registry",
        "==================================",
        "",
        f"Generated: {registry['generated_date']}",
        "",
        registry["purpose"],
        "",
        "Summary",
        "-------",
        (
            f"- source_contracts={summary['source_contract_count']} "
            f"green={summary['green_source_count']} amber={summary['amber_source_count']} red={summary['red_source_count']}"
        ),
        (
            f"- surfaces={summary['surface_count']} privacy_blocked={summary['privacy_blocked_surface_count']} "
            f"manual_sampling={summary['manual_sampling_surface_count']} planning_ready={summary['planning_ready_surface_count']} "
            f"pilot_candidate={summary['pilot_candidate_surface_count']}"
        ),
        f"- decision_grade_surfaces={summary['decision_grade_surface_count']}",
        "",
        "Guardrails",
        "----------",
    ]
    lines.extend(f"- {guardrail}" for guardrail in registry["guardrails"])
    lines.extend(["", "Surface Trust", "-------------"])
    for surface in registry["surfaces"]:
        counts = surface["source_readiness_counts"]
        contracts = ", ".join(surface["source_contract_ids"]) or "none"
        lines.extend(
            [
                f"- [{surface['trust_status']}] {surface['label']}",
                f"  confidence: {surface['stakeholder_confidence']} | data_state: {surface['data_state']}",
                f"  source_contracts: {contracts}",
                f"  source_readiness: green={counts['green']} amber={counts['amber']} red={counts['red']}",
                f"  use: {surface['decision_use']}",
                f"  limit: {surface['known_limit']}",
                f"  next: {surface['next_trust_action']}",
            ]
        )
    lines.extend(["", "Priority Trust Actions", "----------------------"])
    for action in registry["priority_trust_actions"]:
        lines.append(
            f"- [{action['severity']}] {action['contract_id']} {action['data_domain']}: "
            f"owner={action['owner']} privacy={action['privacy_owner']} next={action['next_action']}"
        )
    return "\n".join(lines).rstrip() + "\n"
