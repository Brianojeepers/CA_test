# Source Ingestion Contract

This document defines the horizontal ingestion posture for the MVP before live
connectors, scheduled pipelines, database schemas, landing tables, or warehouse
models are built.

The goal is to make source ingestion thinkable without prematurely committing
to implementation depth. Every source should be described through the same
canonical envelope before it is normalized into the Decision Spine.

## Current Position

- The MVP uses synthetic seed data.
- Source contracts live in `data/source_contracts.json`.
- Live ingestion remains deferred.
- Red sources are planning-only.
- Amber sources are manual-sample-only.
- Green sources are controlled pilot candidates, not production-ready sources.

## Canonical Ingestion Envelope

| Field | Purpose |
| --- | --- |
| `source_id` | Stable source contract, system, or extract identifier. |
| `source_owner` | Named operating owner accountable for source meaning and availability. |
| `privacy_owner` | Named approver for privacy posture, aggregation, suppression, and allowed use. |
| `source_type` | Contract type such as market, decision, release, outcome, ontology, evidence, or prediction. |
| `raw_grain` | Smallest approved real-world unit represented by the source extract. |
| `observed_date` | Date the underlying event, signal, decision, release, or outcome happened. |
| `logged_date` | Date the source record or extract was captured for review. |
| `freshness_sla` | Expected refresh obligation before the source can support a stakeholder claim. |
| `privacy_posture` | Allowed privacy treatment and explicit exclusions for real source material. |
| `allowed_use` | Current allowed use: planning only, manual sample only, or controlled pilot candidate. |
| `confidence_basis` | Why the record should or should not raise stakeholder confidence. |
| `canonical_target` | Decision Spine concept the source would normalize into when approved. |
| `normalization_notes` | Terms, grains, labels, and joins that must be standardized before ingestion. |
| `blocked_until` | Condition that must clear before production ingestion or schema work begins. |

## Current Source Posture

| Source | Domain | Status | Allowed use | Standardization risk |
| --- | --- | --- | --- | --- |
| `SRC-2026-001` | `market_signals` | Manual contracting | Manual sample only | Medium |
| `SRC-2026-002` | `decision_log` | Manual contracting | Manual sample only | Medium |
| `SRC-2026-003` | `release_log` | Manual contracting | Manual sample only | Medium |
| `SRC-2026-004` | `cohort_outcomes` | Blocked | Planning only | High |
| `SRC-2026-006` | `competency_ontology` | Manual contracting | Manual sample only | Medium |
| `SRC-2026-007` | `learner_evidence` | Blocked | Planning only | High |
| `SRC-2026-005` | `prediction_register` | Pilot candidate | Controlled pilot candidate | Low |

No source is production-ingestion-ready.

## Standardization Risks

Market signals need consistent role archetype, geography, client segment,
horizon, and score-component language before they can support role-demand
reasoning.

Decision and release records need consistent status, type, ownership, artifact,
and cohort-link language before they can support reliable cycle-time and impact
views.

Cohort outcomes and learner evidence are the highest-risk sources because they
touch privacy, aggregation, suppression, sample-size, readiness, and outcome
claims.

Competency ontology records need stable role anchors, competency clusters,
target proficiency language, and pedagogy links before gap scoring should be
treated as authoritative.

Prediction records are the lowest-risk pilot candidate because they are already
time-bound, council-owned, and scored through explicit criteria.

## Guardrails

- Define the ingestion envelope before source connectors or database schemas.
- Keep raw source context separate from canonical Decision Spine targets.
- Normalize only after source ownership, freshness, privacy posture, and allowed
  use are explicit.
- Red sources remain planning-only; amber sources remain manual-sample-only.
- Do not build scheduled ingestion, landing tables, or warehouse models from
  this review alone.

## Command

Run:

```bash
python3 scripts/source_ingestion_review.py
```
