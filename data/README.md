# Sample Data

This folder contains seed data for the Decision Spine MVP.

The sample data is intentionally small and hand-readable. It is not production data, and it should not be treated as an accurate representation of Andela systems or outcomes.

## Files

| File | Purpose |
| --- | --- |
| `signals.json` | Market, client, and learner signals that may trigger decisions. |
| `decisions.json` | Documented decisions linked to one or more signals. |
| `releases.json` | Curriculum, credential, assessment, or positioning changes linked to decisions. |
| `cohort_outcomes.json` | Cohort-level placement and retention metrics for pre/post comparisons. |
| `predictions.json` | Horizon predictions with six-month scoring fields. |

## Join Keys

| Key | Used In |
| --- | --- |
| `signal_id` | `signals.json`, `decisions.json`, `predictions.json` |
| `decision_id` | `decisions.json`, `releases.json` |
| `cohort_id` | `releases.json`, `cohort_outcomes.json` |
| `prediction_id` | `predictions.json` |

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

