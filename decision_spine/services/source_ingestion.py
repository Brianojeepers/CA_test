"""Review source-ingestion contracts before building live ingestion."""

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


INGESTION_ENVELOPE_FIELDS: tuple[dict[str, str], ...] = (
    {
        "field": "source_id",
        "purpose": "Stable source contract, system, or extract identifier.",
    },
    {
        "field": "source_owner",
        "purpose": "Named operating owner accountable for source meaning and availability.",
    },
    {
        "field": "privacy_owner",
        "purpose": "Named approver for privacy posture, aggregation, suppression, and allowed use.",
    },
    {
        "field": "source_type",
        "purpose": "Contract type such as market, decision, release, outcome, ontology, evidence, or prediction.",
    },
    {
        "field": "raw_grain",
        "purpose": "Smallest approved real-world unit represented by the source extract.",
    },
    {
        "field": "observed_date",
        "purpose": "Date the underlying event, signal, decision, release, or outcome happened.",
    },
    {
        "field": "logged_date",
        "purpose": "Date the source record or extract was captured for review.",
    },
    {
        "field": "freshness_sla",
        "purpose": "Expected refresh obligation before the source can support a stakeholder claim.",
    },
    {
        "field": "privacy_posture",
        "purpose": "Allowed privacy treatment and explicit exclusions for real source material.",
    },
    {
        "field": "allowed_use",
        "purpose": "Current allowed use: planning only, manual sample only, or controlled pilot candidate.",
    },
    {
        "field": "confidence_basis",
        "purpose": "Why the record should or should not raise stakeholder confidence.",
    },
    {
        "field": "canonical_target",
        "purpose": "Decision Spine concept the source would normalize into when approved.",
    },
    {
        "field": "normalization_notes",
        "purpose": "Terms, grains, labels, and joins that must be standardized before ingestion.",
    },
    {
        "field": "blocked_until",
        "purpose": "Condition that must clear before production ingestion or schema work begins.",
    },
)


CANONICAL_TARGET_BY_DOMAIN = {
    "market_signals": "market_signal",
    "decision_log": "decision_record",
    "release_log": "release_record",
    "cohort_outcomes": "cohort_outcome_aggregate",
    "competency_ontology": "competency_target",
    "learner_evidence": "learner_evidence_aggregate",
    "prediction_register": "prediction_record",
}


NORMALIZATION_FOCUS_BY_DOMAIN = {
    "market_signals": [
        "role archetype",
        "geography",
        "client segment",
        "horizon window",
        "score components",
    ],
    "decision_log": [
        "decision status",
        "decision type",
        "owner",
        "partner functions",
        "alternatives considered",
    ],
    "release_log": [
        "release status",
        "change scope",
        "programme",
        "artifact",
        "cohort link",
    ],
    "cohort_outcomes": [
        "cohort aggregate grain",
        "baseline period",
        "placement metric",
        "retention metric",
        "suppression label",
    ],
    "competency_ontology": [
        "role archetype",
        "competency cluster",
        "target proficiency",
        "market priority",
        "pedagogy links",
    ],
    "learner_evidence": [
        "aggregate evidence grain",
        "sample size",
        "readiness level",
        "suppression applied",
        "evidence confidence",
    ],
    "prediction_register": [
        "horizon window",
        "confidence",
        "confirming criterion",
        "contradicting criterion",
        "outcome scoring",
    ],
}


INGESTION_STATUS_BY_READINESS = {
    "red": "blocked",
    "amber": "manual_contracting",
    "green": "pilot_candidate",
}


ALLOWED_USE_BY_STATUS = {
    "blocked": "planning_only",
    "manual_contracting": "manual_sample_only",
    "pilot_candidate": "controlled_pilot_candidate",
}


CONFIDENCE_BASIS_BY_STATUS = {
    "blocked": "Source can shape workflow design but cannot support real-data claims.",
    "manual_contracting": "Source may support controlled manual examples after owner and definition checks.",
    "pilot_candidate": "Source is the first candidate for a privacy-reviewed pilot extract.",
}


def load_source_contracts(path: Path = SOURCE_CONTRACTS_FILE) -> list[dict[str, Any]]:
    """Load source contracts from the local source register."""
    with path.open(encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, list):
        raise ValueError(f"{path}: expected top-level JSON list")
    return data


def standardization_risk(contract: dict[str, Any]) -> str:
    """Classify how hard the source will be to normalize safely."""
    domain = str(contract["data_domain"])
    readiness = str(contract["readiness"])
    if readiness == "red" or domain in {"cohort_outcomes", "learner_evidence"}:
        return "high"
    if domain in {"market_signals", "competency_ontology"}:
        return "medium"
    if len(contract.get("feeds_files", [])) > 1:
        return "medium"
    if readiness == "amber":
        return "medium"
    return "low"


def blocked_until(contract: dict[str, Any], ingestion_status: str) -> str:
    blockers = contract.get("blockers", [])
    if blockers:
        return "; ".join(str(blocker) for blocker in blockers)
    if ingestion_status == "pilot_candidate":
        return "A controlled pilot extract is approved and reviewed."
    return "Owner, privacy, and freshness obligations are confirmed."


def build_source_record(contract: dict[str, Any]) -> dict[str, Any]:
    readiness = str(contract["readiness"])
    ingestion_status = INGESTION_STATUS_BY_READINESS[readiness]
    domain = str(contract["data_domain"])
    normalization_focus = NORMALIZATION_FOCUS_BY_DOMAIN.get(domain, ["source-specific terms"])
    return {
        "source_id": contract["contract_id"],
        "contract_id": contract["contract_id"],
        "source_type": domain,
        "data_domain": domain,
        "candidate_source": contract["candidate_source"],
        "source_owner": contract["source_owner"],
        "privacy_owner": contract["privacy_owner"],
        "source_files": list(contract.get("feeds_files", [])),
        "raw_grain": contract["minimum_grain"],
        "freshness_sla": contract["freshness_sla"],
        "privacy_posture": contract["privacy_posture"],
        "readiness": readiness,
        "pilot_status": contract["pilot_status"],
        "ingestion_status": ingestion_status,
        "allowed_use": ALLOWED_USE_BY_STATUS[ingestion_status],
        "standardization_risk": standardization_risk(contract),
        "confidence_basis": CONFIDENCE_BASIS_BY_STATUS[ingestion_status],
        "canonical_target": CANONICAL_TARGET_BY_DOMAIN.get(domain, domain),
        "normalization_focus": normalization_focus,
        "normalization_notes": ", ".join(normalization_focus),
        "next_ingestion_action": contract["next_action"],
        "blocked_until": blocked_until(contract, ingestion_status),
        "production_ingestion_ready": False,
    }


def build_source_ingestion_review(contracts: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Return the source ingestion posture without creating schemas or connectors."""
    contracts = contracts if contracts is not None else load_source_contracts()
    sources = [build_source_record(contract) for contract in contracts]
    status_counts = Counter(source["ingestion_status"] for source in sources)
    risk_counts = Counter(source["standardization_risk"] for source in sources)
    return {
        "generated_date": TODAY.isoformat(),
        "purpose": (
            "Define how source data should be described before ingestion, then rate each current "
            "source contract for freshness, allowed use, standardization risk, and live-ingestion readiness."
        ),
        "summary": {
            "source_count": len(sources),
            "blocked_count": status_counts["blocked"],
            "manual_contracting_count": status_counts["manual_contracting"],
            "pilot_candidate_count": status_counts["pilot_candidate"],
            "high_standardization_risk_count": risk_counts["high"],
            "medium_standardization_risk_count": risk_counts["medium"],
            "low_standardization_risk_count": risk_counts["low"],
            "envelope_field_count": len(INGESTION_ENVELOPE_FIELDS),
            "production_ingestion_ready_count": sum(1 for source in sources if source["production_ingestion_ready"]),
            "database_schema_work": "deferred",
        },
        "guardrails": [
            "Define the ingestion envelope before source connectors or database schemas.",
            "Keep raw source context separate from canonical Decision Spine targets.",
            "Normalize only after source ownership, freshness, privacy posture, and allowed use are explicit.",
            "Red sources remain planning-only; amber sources remain manual-sample-only.",
            "Do not build scheduled ingestion, landing tables, or warehouse models from this review alone.",
        ],
        "envelope_fields": [dict(field) for field in INGESTION_ENVELOPE_FIELDS],
        "sources": sources,
    }


def render_source_ingestion_review_text(review: dict[str, Any]) -> str:
    summary = review["summary"]
    lines = [
        "Source Ingestion Contract Review",
        "================================",
        "",
        f"Generated: {review['generated_date']}",
        "",
        review["purpose"],
        "",
        "Summary",
        "-------",
        (
            f"- sources={summary['source_count']} blocked={summary['blocked_count']} "
            f"manual_contracting={summary['manual_contracting_count']} pilot_candidate={summary['pilot_candidate_count']}"
        ),
        (
            f"- standardization_risk high={summary['high_standardization_risk_count']} "
            f"medium={summary['medium_standardization_risk_count']} low={summary['low_standardization_risk_count']}"
        ),
        f"- envelope_fields={summary['envelope_field_count']}",
        f"- production_ingestion_ready={summary['production_ingestion_ready_count']}",
        f"- database_schema_work={summary['database_schema_work']}",
        "",
        "Guardrails",
        "----------",
    ]
    lines.extend(f"- {guardrail}" for guardrail in review["guardrails"])
    lines.extend(["", "Canonical Envelope", "------------------"])
    for field in review["envelope_fields"]:
        lines.append(f"- {field['field']}: {field['purpose']}")
    lines.extend(["", "Source Posture", "--------------"])
    for source in review["sources"]:
        files = ", ".join(source["source_files"])
        focus = ", ".join(source["normalization_focus"])
        lines.extend(
            [
                f"- [{source['ingestion_status']}] {source['contract_id']} {source['data_domain']}",
                f"  owner: {source['source_owner']} | privacy: {source['privacy_owner']}",
                f"  files: {files}",
                f"  target: {source['canonical_target']} | allowed_use: {source['allowed_use']}",
                f"  freshness: {source['freshness_sla']}",
                f"  risk: {source['standardization_risk']} | focus: {focus}",
                f"  confidence: {source['confidence_basis']}",
                f"  blocked_until: {source['blocked_until']}",
                f"  next: {source['next_ingestion_action']}",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"
