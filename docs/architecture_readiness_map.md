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
| Signal ingestion | Partial | Add a source freshness and owner-obligation view that spans planned signal domains. | Scheduled ingestion, warehouse landing tables, and source-specific pipelines. |
| Normalization | Thin | Create a crosswalk review for role anchors, competency clusters, evidence types, and decision references. | Canonical ontology tables and warehouse semantic models. |
| Intelligence | Partial | Extend reasoning stress tests across role demand, competency gaps, horizon radar, and curriculum impact assumptions. | Model training, weight tuning, and scoring contracts. |
| Decision | Covered for local MVP | Add decision-policy checks for wait, escalate, revise, or archive. | Automated approvals and downstream writes. |
| Activation | Partial | Map every stakeholder lens to expected actions, evidence thresholds, and escalation paths. | LMS, CRM, ATS, or delivery-tool integrations. |
| Governance cadence | Partial | Define weekly, monthly, and quarterly review templates with entry and exit criteria. | Automated production schedules. |
| Observability and trust | Partial | Add a trust registry for freshness, source coverage, privacy posture, and confidence by surface. | Production observability tooling. |
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

1. Architecture readiness map.
2. Trust and source coverage registry.
3. Stakeholder journey map across evidence, decision, activation, and follow-up.
4. Decision policy checks for wait, revise, escalate, or archive.
5. Cross-layer reasoning stress tests before schema commitments.
