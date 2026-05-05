# Reasoning Stress Tests

This document defines cross-layer reasoning stress tests for the MVP before
database schemas, source-specific connectors, scheduled ingestion, or warehouse
models are introduced.

The purpose is to prove that the system downgrades unsafe claims when evidence,
trust posture, ingestion readiness, stakeholder journey, or decision policy
conflicts.

## Current Result

The current MVP passes 5 of 5 stress scenarios.

All tested unsafe claims are blocked or downgraded.

## Scenarios

| Scenario | Claim pressure | Required downgrade |
| --- | --- | --- |
| Strong market signal with blocked learner and outcome evidence | Act on a strong role-demand signal and imply placement or readiness impact. | Monitor |
| Approved decision with blocked or incomplete release path | Treat an approved decision as implemented operating change. | Revise |
| Green prediction register with amber market source | Use a pilot-ready prediction register to publish a hard horizon recommendation. | Controlled pilot only |
| External stakeholder asks for a client-facing proof claim | Turn dashboard or brief language into external sales proof. | Internal directional only |
| Dashboard action tries to bypass decision policy | Promote a selected decision directly to action from an insight card. | Escalate |

## Guardrails

- A strong signal cannot override red learner or outcome source blockers.
- Approval is not implementation proof; release and evidence posture still
  govern action.
- A green source in one domain cannot make another source production-ready.
- External-facing claims require stronger trust posture than internal planning
  work.
- Dashboard actions must obey decision policy outcomes.

## What This Prevents

The MVP should not imply that a market signal proves learner readiness.

The MVP should not treat a council approval as implementation or impact proof.

The MVP should not let a green prediction register upgrade amber market-signal
ingestion.

The MVP should not allow Solutions, Sales, or executive users to convert
directional evidence into client-facing proof claims.

The MVP should not let dashboard affordances bypass policy outcomes such as
monitor, wait, revise, or escalate.

## Command

Run:

```bash
python3 scripts/reasoning_stress_review.py
```
