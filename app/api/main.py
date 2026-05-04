"""FastAPI boundary for Decision Spine services."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from decision_spine.services.decision_detail import build_decision_detail
from decision_spine.services.monthly_packet import build_monthly_packet


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
    allow_methods=["GET"],
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


@app.get("/api/decisions/{decision_id}")
def decision_detail(decision_id: str) -> dict[str, Any]:
    try:
        detail = build_decision_detail(decision_id)
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    if detail is None:
        raise HTTPException(status_code=404, detail=f"Unknown decision_id: {decision_id}")
    return detail
