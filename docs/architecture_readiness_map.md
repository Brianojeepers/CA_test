# Architecture Readiness Map

This map keeps the MVP expansion horizontal before database schemas, warehouse
models, scheduled ingestion, or source-specific pipelines.

The current product should broaden across the target intelligence architecture
before it goes deep into persistence. That means each slice should clarify how
signals, normalization, intelligence, decisions, activation, governance,
observability, and stakeholder experience fit together.

## Current Rating

Rating: 9/10 for pausing vertical schema work and expanding horizontally.

Rationale: the local MVP is strong as a decision spine, but it is still too
narrow to represent the full intelligence engine. Expanding layer coverage now
will make later schema and database decisions more defensible.

## Layer Map

| Layer | Current readiness | Horizontal next step | Vertical work deferred |
| --- | --- | --- | --- |
| Signal ingestion | Partial | Rehearse controlled pilot extracts once source blockers clear. | Scheduled ingestion, warehouse landing tables, and source-specific pipelines. |
| Normalization | Partial | Use crosswalk gaps to shape controlled pilot extracts before ontology/schema work. | Canonical ontology tables and warehouse semantic models. |
| Intelligence | Partial | Use stress-test failures to define the narrowest pilot extract rehearsal. | Model training, weight tuning, and scoring contracts. |
| Decision | Covered for local MVP | Place policy and stress-test downgrades into the dashboard once the review language stabilizes. | Automated approvals and downstream writes. |
| Activation | Partial | Rehearse controlled pilot extracts once source blockers clear. | LMS, CRM, ATS, or delivery-tool integrations. |
| Governance cadence | Partial | Trial the manual cadence and capture review outcomes before automation. | Automated production schedules. |
| Observability and trust | Partial | Expose stress-test downgrades as stakeholder-visible trust signals. | Production observability tooling. |
| Stakeholder experience | Partial | Broaden the dashboard into architecture-wide navigation: signals, trust, decisions, activation, and learning. | Deep optimization of any single dashboard module. |

## Guardrails

- Keep real-data, database, and warehouse work deferred until horizontal coverage
  is coherent.
- Prefer read-only reviews and stakeholder workflow surfaces over persistence
  commitments.
- Each new slice should clarify source, trust, decision, activation, or
  governance behavior across the architecture.
- Directional intelligence outputs must keep explicit limits until pilot data
  passes privacy, ownership, and freshness gates.

## Next Horizontal Slices

1. Controlled pilot extract rehearsal once source blockers clear.
2. Dashboard placement for decision policy and stress-test downgrades.
3. Manual governance cadence trial with saved review outcomes.
