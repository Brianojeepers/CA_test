# Decision Spine Risk Register v1.0

## Purpose

This register documents how the Decision Spine dashboard can mislead teams, create false confidence, or fail to drive action.

The governing assumption is:

```text
This dashboard is guilty until proven decision-useful.
```

## Top Risks

| ID | Failure Mode | Category | Early Warning Signal | Mitigation | Owner |
| --- | --- | --- | --- | --- | --- |
| R1 | KPI definitions drift by function. | Governance | The same KPI is reported differently in different meetings. | Version-controlled KPI dictionary with monthly sign-off. | Signal Intelligence Council |
| R2 | Signal scoring becomes subjective storytelling. | Design | Different reviewers produce materially different scores for the same signal. | Use a scoring rubric and run biweekly calibration on sample signals. | Research |
| R3 | Outcome KPIs over-attribute impact to learning changes. | Analytics | Positive placement or retention deltas appear without exposure verification. | Require exposure flags and confounder notes in outcome readouts. | Matching + CSM |
| R4 | Decision log is incomplete. | Data | High volume of missing timestamps, owners, or linked signals. | Make decision register fields mandatory; use a no-ID, no-report rule. | Signal Intelligence Council |
| R5 | Small sample noise drives false action. | Analytics | Large cohort-to-cohort movement with low `n`. | Suppress standalone deltas below `n = 25`; use three-cohort rolling baseline. | Matching |
| R6 | Teams game the metric. | Incentive | KPI improves without corresponding operational evidence. | Maintain audit trails and run random monthly audit of five records. | Signal Intelligence Council |
| R7 | Red KPIs create no action. | Adoption | Same KPI remains red across cycles with no logged owner task. | Enforce red KPI protocol with seven-day escalation. | KPI Owners |
| R8 | Prediction accuracy becomes unfalsifiable. | Design | `Inconclusive` outcomes dominate prediction scoring. | Require confirming and contradicting criteria when predictions are issued. | Research |
| R9 | External demand cycles are mistaken for internal success or failure. | Analytics | Outcome swings align with broad market shifts rather than programme changes. | Add market context notes to every monthly outcome readout. | Signal Intelligence Council |
| R10 | Dashboard becomes reporting theater. | Adoption | Meetings discuss charts but no decisions change. | Track decisions influenced and retire metrics that do not affect action. | Signal Intelligence Council |

## Cross-Cutting Safeguards

- Every KPI readout must include a data confidence label: high, medium, or low.
- Outcome KPIs must include at least one confounder note.
- Prediction records must be falsifiable before they can enter accuracy scoring.
- Red metrics must create a case, not a discussion item.
- Metric ownership and threshold changes must be logged.

## Kill Criteria

Retire or redesign a KPI if any of the following conditions hold for two consecutive operating cycles:

- The KPI triggers no decisions or actions.
- The KPI cannot be calculated without repeated manual reinterpretation.
- Stakeholders cannot agree on the definition after governance review.
- Data confidence remains low and no credible path to medium confidence exists.
- The KPI incentivizes behavior that weakens credential integrity or placement quality.

## Keep Criteria

Keep and mature a KPI if it meets at least two of the following conditions:

- It triggers useful action within a quarter.
- It exposes a meaningful bottleneck in the signal-to-action workflow.
- It helps disconfirm or refine an existing market assumption.
- It is cited in a curriculum, credential, commercial, or matching decision.
- It becomes more reliable as source systems improve.
