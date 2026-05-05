# Stakeholder Journey Map

This map describes how each stakeholder should move from evidence surface to
safe action in the current MVP. It uses the trust posture from
`docs/trust_registry.md` to separate useful planning work from deferred
decision-grade claims.

This is a horizontal MVP slice. It does not introduce database schemas,
warehouse models, scheduled ingestion, or downstream system writes.

## Journey Modes

| Mode | Meaning |
| --- | --- |
| Workflow design only | Evidence surfaces are useful for planning, but at least one required source is privacy blocked. |
| Planning ready | The surfaces expose blockers, owner requests, or intake posture without making evidence claims. |
| Controlled manual review | Sources can be manually sampled, but ownership or definitions still need confirmation. |
| Pilot candidate | Sources are green for a controlled pilot, but current MVP data remains synthetic. |
| Unmapped | A required surface lacks source-contract coverage. |

## Stakeholder Journeys

| Stakeholder | Current mode | Can do now | Must defer |
| --- | --- | --- | --- |
| Signal Intelligence Council | Workflow design only | Run the meeting around exceptions, blockers, and directional decision posture. | Treating placement, retention, or learner-readiness evidence as production proof. |
| Learning | Workflow design only | Plan curriculum responses and identify immature evidence. | Claiming a curriculum change improved placement. |
| Assessment Ops | Workflow design only | Identify readiness risks, privacy blockers, and assessment evidence requirements. | Storing learner-derived real extracts or moving high-stakes thresholds from synthetic evidence. |
| Matching and CSM | Workflow design only | Flag likely positioning opportunities and outcome gaps. | Updating client-facing placement claims. |
| Solutions and Sales | Workflow design only | Prepare non-overstated narratives with known limits. | Citing raw client demand, account-level evidence, or unapproved outcome claims. |
| Data and Analytics | Planning ready | Coordinate source-owner clarification, ingestion-envelope gaps, privacy blockers, and pilot fields. | Creating database schemas or warehouse models. |
| Delivery | Workflow design only | Review release timing risk and cohort-calendar gaps. | Automating delivery schedules or assuming real cohort timing confidence. |
| Market Intelligence and Research | Workflow design only | Stress-test role demand, horizon, and weak-signal assumptions with missing-field labels. | Publishing scores, model weights, or hard recommendations. |
| Source Owners | Planning ready | Respond to field requests, clarify grain and freshness, and identify privacy constraints. | Sending real extracts before privacy, storage, sample rules, and ingestion envelope are approved. |
| Executive stakeholders | Workflow design only | Review the operating narrative, known limits, and accountability. | Making performance claims or scale decisions from synthetic evidence. |

## Escalation Rules

- Red source blockers go to the named privacy owner.
- Unresolved decision ownership goes to the council chair.
- Learner-evidence blockers go to Assessment Ops and Talent Data Privacy.
- Cohort outcome blockers go to Matching Operations and Talent Data Privacy.
- Commercial-source ambiguity goes to Research and Commercial Operations.
- Cohort-calendar gaps go to Delivery leadership.

## Evidence Needed To Progress

- Privacy-cleared cohort outcomes.
- Approved aggregate learner evidence and suppression rules.
- Confirmed decision-register ownership.
- Owner-confirmed field definitions, sample availability, privacy decisions, and freshness SLAs.
- Confirmed cohort calendar and release-window data.
- Calibrated demand, horizon, and weak-signal scoring examples.

## Policy Link

Stakeholder journeys describe what each user can safely do. Decision policy
checks translate those journeys into operating outcomes: act now, revise,
monitor, wait, escalate, or archive.

Source ingestion checks define the canonical envelope and source freshness
posture that Data, Analytics, and Source Owners need before any live ingestion
or schema work begins.

Run:

```bash
python3 scripts/source_ingestion_review.py
python3 scripts/decision_policy_review.py
```

## Command

```bash
python3 scripts/stakeholder_journey_review.py
```
