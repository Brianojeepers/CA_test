# Sample Data

This folder contains seed data for the Decision Spine MVP.

The sample data is intentionally small and hand-readable. It is not production data, and it should not be treated as an accurate representation of Andela systems or outcomes.

Real data should be introduced only through a controlled, privacy-reviewed pilot extract.
See `docs/real_data_readiness.md` before replacing or supplementing these seed files
with real source data.

## Files

| File | Purpose |
| --- | --- |
| `signals.json` | Market, client, and learner signals that may trigger decisions. |
| `decisions.json` | Documented decisions linked to one or more signals. |
| `releases.json` | Curriculum, credential, assessment, or positioning changes linked to decisions. |
| `cohort_outcomes.json` | Cohort-level placement and retention metrics for pre/post comparisons. |
| `predictions.json` | Horizon predictions with six-month scoring fields. |

The operating role accountable for turning this evidence into action is defined in
`docs/signal_intelligence_council.md`.

## Join Keys

| Key | Used In |
| --- | --- |
| `signal_id` | `signals.json`, `decisions.json`, `predictions.json` |
| `decision_id` | `decisions.json`, `releases.json` |
| `cohort_id` | `releases.json`, `cohort_outcomes.json` |
| `prediction_id` | `predictions.json` |

Pending releases may reference future cohort IDs that are not present in
`cohort_outcomes.json` yet. The validator treats those as warnings, not failures.
Released items with unknown cohort IDs are data quality failures.

## Intended MVP Flow

```text
signals -> decisions -> releases -> cohort outcomes -> prediction learning
```

These files are enough to build a first local dashboard or script that calculates:

- Signal Strength Score.
- Signal-to-Decision Time.
- Decision-to-Release Time.
- Curriculum/Credential Changes per Quarter.
- Placement Rate Delta.
- 90-Day Retention Delta.
- Prediction Accuracy at 6 Months.

## Local KPI Report

Validate the seed data from the repository root:

```bash
python3 scripts/validate_data.py
```

Run the first MVP report:

```bash
python3 scripts/report_kpis.py
```

The report reads these seed files and prints the current Decision Spine KPI status,
including threshold colors, pending releases, outcome deltas, and prediction scoring.
It runs validation first and stops if the seed data has errors.

Run the action-focused council review:

```bash
python3 scripts/council_review.py
```

The council review surfaces decision queues, release accountability, traceability
checks, and prediction follow-ups for monthly operating review.

Run the signal-to-action review:

```bash
python3 scripts/signal_review.py
```

The signal review groups evidence into act now, act tracked, monitor, and do not
act buckets with linked decisions, releases, implications, and next steps.

Run the Assessment Ops credential and assessment view:

```bash
python3 scripts/credential_requirements.py
```

The credential requirements view shows credential and assessment actions, linked
signal evidence, release status, and monitor decisions that should not become
requirements yet.
