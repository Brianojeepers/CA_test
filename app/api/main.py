"""FastAPI boundary for Decision Spine services."""

from __future__ import annotations

from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from decision_spine.services.architecture_readiness import build_architecture_readiness_review
from decision_spine.services.decision_detail import build_decision_detail
from decision_spine.services.decision_policy import build_decision_policy_review
from decision_spine.services.governance_cadence import build_governance_cadence_review
from decision_spine.services.monthly_packet import build_monthly_packet
from decision_spine.services.normalization_crosswalk import build_normalization_crosswalk
from decision_spine.services.pilot_intake_review import build_pilot_intake_review
from decision_spine.services.pilot_request_pack import build_pilot_request_pack
from decision_spine.services.reasoning_stress import build_reasoning_stress_review
from decision_spine.services.schema_gap import (
    InvalidFieldActionStatus,
    UnknownFieldAction,
    build_schema_gap_report,
    update_field_action_status,
)
from decision_spine.services.source_ingestion import build_source_ingestion_review
from decision_spine.services.trust_registry import build_trust_registry
from decision_spine.services.v02_intelligence import build_v02_intelligence_preview


class FieldActionStatusUpdate(BaseModel):
    status: str
    notes: Optional[str] = None


app = FastAPI(
    title="Decision Spine API",
    version="0.1.0",
    description="JSON API for the local Decision Spine MVP.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "PATCH"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/monthly-packet")
def monthly_packet() -> dict[str, Any]:
    try:
        return build_monthly_packet()
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/schema-gap")
def schema_gap() -> dict[str, Any]:
    try:
        return build_schema_gap_report()
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/v02-intelligence")
def v02_intelligence() -> dict[str, Any]:
    try:
        return build_v02_intelligence_preview()
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/pilot-request-pack")
def pilot_request_pack() -> dict[str, Any]:
    try:
        return build_pilot_request_pack()
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/pilot-intake-review")
def pilot_intake_review() -> dict[str, Any]:
    try:
        return build_pilot_intake_review()
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/architecture-readiness")
def architecture_readiness() -> dict[str, Any]:
    try:
        return build_architecture_readiness_review()
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/trust-registry")
def trust_registry() -> dict[str, Any]:
    try:
        return build_trust_registry()
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/source-ingestion")
def source_ingestion() -> dict[str, Any]:
    try:
        return build_source_ingestion_review()
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/normalization-crosswalk")
def normalization_crosswalk() -> dict[str, Any]:
    try:
        return build_normalization_crosswalk()
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/governance-cadence")
def governance_cadence() -> dict[str, Any]:
    try:
        return build_governance_cadence_review()
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/decision-policy")
def decision_policy() -> dict[str, Any]:
    try:
        return build_decision_policy_review()
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/reasoning-stress")
def reasoning_stress() -> dict[str, Any]:
    try:
        return build_reasoning_stress_review()
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.patch("/api/schema-gap/actions/{capability}/{field}")
def update_schema_gap_action(capability: str, field: str, update: FieldActionStatusUpdate) -> dict[str, Any]:
    try:
        update_field_action_status(capability, field, update.status, update.notes)
        return build_schema_gap_report()
    except InvalidFieldActionStatus as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except UnknownFieldAction as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/decisions/{decision_id}")
def decision_detail(decision_id: str) -> dict[str, Any]:
    try:
        detail = build_decision_detail(decision_id)
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    if detail is None:
        raise HTTPException(status_code=404, detail=f"Unknown decision_id: {decision_id}")
    return detail
