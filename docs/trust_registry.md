# Trust and Source Coverage Registry

The trust registry explains what each stakeholder-facing surface can safely say
today, which source contracts support it, and what has to clear before the
surface becomes decision-grade.

This is still a horizontal MVP slice. It does not introduce a database schema,
warehouse model, production observability stack, or scheduled ingestion.

## Trust States

| State | Meaning | Stakeholder handling |
| --- | --- | --- |
| Privacy blocked | At least one supporting source is red in `data/source_contracts.json`. | Use for workflow design only; do not treat as real evidence. |
| Manual sampling only | Supporting sources are amber and need owner, field, freshness, or definition confirmation. | Use for controlled review and source-owner clarification. |
| Pilot candidate | Supporting sources are green, but current MVP data is still synthetic. | Run a controlled pilot extract before increasing confidence. |
| Planning control ready | The surface exposes gaps, blockers, or requests rather than making evidence claims. | Use to plan work; do not treat it as evidence proof. |
| Unmapped | A source file has no source contract. | Create a source contract before relying on the surface. |

## Current Surface Coverage

| Surface | Trust posture | Why |
| --- | --- | --- |
| Monthly council packet | Privacy blocked | Depends on cohort outcome and learner evidence sources that still require privacy review. |
| Stakeholder Markdown briefs | Privacy blocked | Reuses the same synthetic decision spine evidence as the monthly packet. |
| Local stakeholder dashboard | Privacy blocked | Displays stakeholder-facing evidence before real-data gates have cleared. |
| Decision impact review | Privacy blocked | Impact maturity depends on cohort outcomes and learner evidence. |
| v0.2 intelligence preview | Privacy blocked | Competency-gap reasoning still depends on learner evidence privacy approval. |
| Schema gap workbench | Planning control ready | Its job is to expose missing fields and source blockers before schema work. |
| Pilot request pack | Planning control ready | It requests owner input; it is not source approval. |
| Pilot intake review | Planning control ready | It classifies intake responses, but current responses are synthetic planning records. |

## Current Source Contract Posture

- Green: 1 source contract.
- Amber: 4 source contracts.
- Red: 2 source contracts.
- Decision-grade stakeholder surfaces: 0.

The two red contracts are:

- `SRC-2026-004` cohort outcomes.
- `SRC-2026-007` learner evidence.

Those two sources block real-data use for any surface that relies on placement,
retention, readiness, or proficiency evidence.

## Operating Rules

- Synthetic seed data can support workflow design, not production claims.
- Red source contracts block real-data use for dependent surfaces.
- Amber source contracts require manual sampling and owner confirmation before
  stakeholder confidence increases.
- Planning controls can expose blockers without making the underlying evidence
  decision-grade.
- Do not begin database, warehouse, or scheduled-ingestion work from this
  registry alone.

## Command

```bash
python3 scripts/trust_registry_review.py
```
