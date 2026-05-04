# Source Data Contracts

## Purpose

Source data contracts define the minimum evidence each real extract must provide
before it can feed the Decision Spine MVP.

They are deliberately narrower than a production data model. The goal is to
protect privacy, keep ownership clear, and make the first real pilot extract
boringly testable.

## Contract Rules

- Every real source must have a source owner and privacy owner.
- Every extract must declare which MVP file it feeds.
- Every row must be at the safest useful grain.
- Client, talent, and commercial details should be summarized unless explicit
  approval is given.
- A source can be useful before it is automated, but it cannot be trusted before
  ownership, freshness, and suppression rules are clear.

## Current Contract Register

The working register lives in `data/source_contracts.json`.

| Domain | Feeds | Readiness Meaning |
| --- | --- | --- |
| Market signals | `signals.json`, `predictions.json` | Source evidence can be summarized, but scoring needs calibration. |
| Decision log | `decisions.json` | Council ownership and status definitions must be confirmed. |
| Release log | `releases.json`, `pedagogy_map.json` | Release definitions must be consistent across curriculum and assessment. |
| Competency ontology | `role_competencies.json` | Role and capability definitions must be owner-approved before they drive gap scoring. |
| Learner evidence | `learner_evidence_summary.json` | Aggregated evidence can support readiness claims only after privacy and suppression rules are clear. |
| Cohort outcomes | `cohort_outcomes.json` | Privacy review and aggregation thresholds are blocking. |
| Prediction register | `predictions.json` | Ready for small manual pilot once council predictions are written. |

## Readiness Levels

| Level | Meaning | Import Rule |
| --- | --- | --- |
| Green | Owner, field shape, privacy posture, and pilot use are clear. | Can be used in a controlled pilot extract. |
| Amber | Useful candidate source, but ownership or definitions need confirmation. | Can be mocked or manually sampled; do not treat as trusted yet. |
| Red | Privacy, aggregation, or storage rules are unresolved. | Do not import real data until blockers are cleared. |

## Minimum Source Contract Fields

Each contract should specify:

- `contract_id`
- `data_domain`
- `candidate_source`
- `source_owner`
- `privacy_owner`
- `feeds_files`
- `minimum_grain`
- `required_fields`
- `privacy_posture`
- `freshness_sla`
- `pilot_status`
- `readiness`
- `blockers`
- `next_action`

## Operating Use

Run the contract review before planning a real-data pilot:

```bash
python3 scripts/source_contract_review.py
```

The review should answer:

- Which sources are ready enough to pilot?
- Which sources are blocked by privacy or ownership?
- Which MVP files have at least one candidate source?
- What concrete action is needed next for each source?

This should be read alongside `docs/real_data_readiness.md`. The readiness doc
sets the guardrails; the contract register turns those guardrails into source-by-
source obligations.
