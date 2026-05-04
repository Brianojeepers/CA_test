"""FastAPI boundary for Decision Spine services."""

from __future__ import annotations

from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from decision_spine.services.decision_detail import build_decision_detail
from decision_spine.services.monthly_packet import build_monthly_packet
from decision_spine.services.schema_gap import (
    InvalidFieldActionStatus,
    UnknownFieldAction,
    build_schema_gap_report,
    update_field_action_status,
)
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
