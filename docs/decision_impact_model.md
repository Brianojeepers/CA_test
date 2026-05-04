# Decision Impact Model

## Purpose

Decision impact review asks whether an approved decision appears to be working.
It combines implementation status, competency readiness evidence, and cohort
outcomes into one operating view.

This is not causal proof. It is a structured review layer that tells the council
which decisions are too early, which show positive evidence, and which need
attention.

## Inputs

The review joins:

- `decisions.json`
- `releases.json`
- `role_competencies.json`
- `learner_evidence_summary.json`
- `cohort_outcomes.json`
- `predictions.json`

## Impact Statuses

| Status | Meaning |
| --- | --- |
| `too_early` | Release is not yet complete or evidence windows have not closed. |
| `evidence_emerging` | Learner evidence is promising, but outcome maturity or confidence is incomplete. |
| `positive_signal` | Learner evidence or cohort outcomes are directionally positive enough to amplify. |
| `needs_attention` | Readiness evidence, outcomes, or implementation state indicate risk. |
| `no_outcome_data` | Decision has implementation traceability but no relevant learner or cohort evidence yet. |

## Interpretation Rules

- Do not treat placement outcomes as proof of proficiency.
- Do not treat learner evidence as proof of market impact.
- A decision can be promising even before retention data matures.
- A released decision with suppressed or pending evidence should remain under
  review.
- Monitor decisions are excluded from impact scoring unless they become approved
  curriculum, credential, or assessment decisions.

## Review Command

Run:

```bash
python3 scripts/decision_impact_review.py
```

The review prints one impact classification per approved decision, plus evidence
and outcome details for follow-up.
