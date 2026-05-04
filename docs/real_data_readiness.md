# Real Data Readiness

## Purpose

The Decision Spine MVP currently uses hand-created seed data. Real data should be introduced only after the team agrees the source systems, privacy rules, ownership, and minimum pilot extract.

The goal is not to ingest everything. The goal is to run a small, safe pilot that proves the workflow can operate on real evidence without exposing sensitive client, talent, or commercial data unnecessarily.

## Current Position

| Area | Status |
| --- | --- |
| Product workflow | Safe to test with synthetic seed data. |
| KPI logic | Safe to test with synthetic seed data. |
| Real source mapping | Draft source contracts defined in `data/source_contracts.json`. |
| Privacy and sensitivity review | Required before real extracts. |
| Production integration | Out of scope for the current MVP. |

## Candidate Source Systems

| Data Domain | Candidate Sources | Notes |
| --- | --- | --- |
| Market signals | Job market research, client RFP notes, sales notes, external reports, engineering trend research. | Prefer summarized evidence over raw confidential notes in v1. |
| Decisions | Council decision log, assessment governance notes, curriculum review records. | Needs explicit owner and decision date. |
| Releases | Curriculum version log, assessment rubric changes, credential requirement changes, LMS release notes. | Needs a consistent definition of "released." |
| Cohort outcomes | Matching records, placement tracking, CSM records, talent operations data. | Must be anonymized and aggregated for MVP use. |
| Predictions | Horizon review notes, research memos, council prediction register. | Must include confirming and contradicting criteria before scoring. |

## Minimum Viable Real Extract

Use the smallest extract that can exercise the full loop:

- 5-10 real market or client signals.
- 3-5 real decisions linked to those signals.
- 2-4 real releases linked to those decisions.
- 2-4 anonymized cohort outcome rows where aggregation is safe.
- 3-5 horizon predictions with scoring criteria.

This is enough to test traceability and KPI behavior without creating a broad data-governance burden.

## Required Protections

- Remove client names unless explicitly approved.
- Remove individual talent names, emails, IDs, and profile URLs.
- Aggregate outcomes at cohort or programme level.
- Suppress or label cohorts below the minimum standalone threshold.
- Replace commercially sensitive notes with short evidence summaries.
- Store only the fields needed by the current MVP schema.
- Mark every row with a data confidence value.

## Fields Needed By MVP

| File | Required Real-Data Inputs |
| --- | --- |
| `signals.json` | Signal ID, dates, theme, type, archetype, horizon, geography, client segment, score components, status, confidence, summary. |
| `decisions.json` | Decision ID, linked signal IDs, signed date, type, status, owner, partner functions, summary, rationale, alternatives, complexity. |
| `releases.json` | Release ID, decision ID, release date or pending status, change type, scope, programme, artifact, cohort ID, traceability flag, linked signal IDs. |
| `cohort_outcomes.json` | Cohort ID, programme, archetype, credential tier, dates, placement counts/rates, retention counts/rates, client satisfaction if safe, exposure, baseline, confidence. |
| `predictions.json` | Prediction ID, issued date, scoring date, linked signal IDs, claim, horizon, confidence, confirming criterion, contradicting criterion, outcome, score, notes. |

## Sign-Off Before Import

| Approval | Why It Matters |
| --- | --- |
| Data owner | Confirms source fields are allowed for MVP use. |
| Client/commercial owner | Confirms client demand evidence can be summarized safely. |
| Talent/data privacy owner | Confirms outcome data is anonymized and aggregated enough. |
| Council owner | Confirms the extract supports real operating decisions. |

## Source Contracts

Before importing real data, review `docs/source_data_contracts.md` and run:

```bash
python3 scripts/source_contract_review.py
```

The current contract register keeps real source readiness separate from seed-data
validity. A source can have useful candidate fields and still be blocked by
privacy, aggregation, ownership, or freshness rules.

## Pilot Extract Templates

Pilot extract templates live in:

```text
data/pilot_extract_templates/
```

Local pilot extracts should live in ignored `data/pilot_extracts/`.

Before any pilot extract is reviewed for import, run:

```bash
python3 scripts/validate_pilot_extract.py data/pilot_extracts
```

See `docs/pilot_extract_process.md` for the full dry-run process.

## Pilot Rules

- Keep synthetic seed data available for tests and demos.
- Store real pilot data separately until approved for broader use.
- Run `python3 scripts/validate_data.py` before any report.
- Treat warnings as review items, not noise.
- Do not use real pilot metrics for performance judgment until definitions and source quality are stable.

## Open Questions

- Which system should own the canonical decision log?
- Who approves use of client RFP or sales-note evidence?
- What aggregation threshold is acceptable for cohort outcomes beyond the current `n < 25` rule?
- Should real pilot files live in this repo, a private data store, or an ignored local folder?
- What fields need hashing, suppression, or manual summarization before import?
