# Learner Evidence Model

## Purpose

Learner evidence links competency targets to privacy-safe proof of readiness. It
does not store individual learner records. It stores aggregated cohort or
programme evidence that can be used to decide whether a competency is ready to
credential, position, or improve.

The working register lives in `data/learner_evidence_summary.json`.

## Design Rules

- Use aggregated cohort or programme-level evidence only.
- Do not include learner names, email addresses, IDs, raw submissions, or client
  assignment details.
- Separate proficiency evidence from placement outcomes. Placement can validate
  market relevance, but it does not prove the learner demonstrated the
  competency.
- Mark small cohorts as suppressed or roll them into larger aggregates.
- Pending evidence should be explicit; null rates are valid when the evidence
  window has not closed.

## Required Fields

| Field | Meaning |
| --- | --- |
| `evidence_id` | Stable local identifier. |
| `competency_id` | Competency being evidenced. |
| `cohort_id` | Cohort aggregate the evidence describes. |
| `programme` | Programme name. |
| `role_archetype` | Builder, Scaler, Prototyper, or another mapped archetype. |
| `evidence_type` | `assessment_artifact`, `credential_review`, `simulation_result`, `portfolio_review`, or `placement_signal`. |
| `evidence_window` | Month or period covered by the evidence. |
| `sample_size` | Number of learners or artifacts in the aggregate. |
| `meets_threshold_count` | Count meeting the competency threshold, or null if pending/suppressed. |
| `readiness_rate` | Threshold count divided by sample size, or null if pending/suppressed. |
| `readiness_level` | `ready`, `emerging`, `not_ready`, `pending`, or `insufficient_sample`. |
| `evidence_confidence` | `low`, `medium`, or `high`. |
| `privacy_posture` | `aggregated` or `suppressed`. |
| `suppression_applied` | Whether reporting has been suppressed or rolled up. |
| `evidence_summary` | Short interpretation of what the evidence shows. |
| `next_action` | Concrete follow-up. |

## Readiness Interpretation

| Level | Meaning |
| --- | --- |
| `ready` | Evidence supports positioning or credentialing the competency. |
| `emerging` | Evidence is promising but needs rubric, sample, or outcome follow-up. |
| `not_ready` | Evidence shows the cohort is below the competency threshold. |
| `pending` | Evidence window has not closed or scoring is incomplete. |
| `insufficient_sample` | Sample is too small for standalone readiness claims. |

## Review Command

Run:

```bash
python3 scripts/proficiency_readiness_review.py
```

The review shows readiness by competency, flags pending and suppressed evidence,
and identifies active competencies without learner evidence.
