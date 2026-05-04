# Decision Spine KPI Dictionary v1.0

## Purpose

This dictionary defines the first seven KPIs for the AI Talent Strategy Decision Spine MVP.

The MVP workflow is:

```text
Signal -> Decision -> Release -> Outcome -> Learning
```

The goal is to make each KPI decision-useful, auditable, and clear enough for cross-functional teams to operate against without reinterpreting definitions in every meeting.

## Operating Rules

- No metric without a named decision owner.
- No red metric without an action, due date, and escalation path.
- Low-confidence KPI values are directional signals, not performance judgments.
- Threshold changes should not happen mid-quarter unless approved as a governance exception.
- Every curriculum or credential change counted in this system must be traceable to evidence.

## Global Definitions

| Term | Definition |
| --- | --- |
| Signal | A documented market, client, placement, or learner evidence point that may imply a curriculum, credential, or positioning response. |
| Green signal | A signal with strength score at or above the action threshold. |
| Decision | A documented accept, reject, monitor, or defer choice tied to one or more signals. |
| Release | The first point at which a curriculum, credential, assessment, or positioning change is live for the relevant audience. |
| Placement | Recommended v1 definition: talent placement start date, not contract signature or first invoice. |
| Market-traceable change | A released curriculum or credential change with at least one linked signal or prediction record. |
| Minimum cohort size | If `n < 25`, suppress standalone outcome delta and roll into a three-cohort aggregate. |

## KPI Summary

| ID | KPI | Primary Owner | Grain | Refresh | Red Trigger |
| --- | --- | --- | --- | --- | --- |
| K1 | Signal Strength Score | Research / AI Talent Strategy | Per signal | Weekly | Audit scoring consistency and evidence tags. |
| K2 | Signal-to-Decision Time | AI Talent Strategy | Per green signal | Weekly | Review stalled items and assign owner plus due date. |
| K3 | Decision-to-Release Time | Learning | Per decision | Weekly | Re-plan blocked release with dependency owner. |
| K4 | Curriculum/Credential Changes per Quarter | Learning + Assessment Ops | Quarterly | Monthly check, quarterly close | Run change-debt review and commit one market-traceable change. |
| K5 | Placement Rate Delta | Matching + CSM | Per cohort | Monthly | Run placement funnel diagnostic. |
| K6 | 90-Day Retention Delta | CSM + Talent Experience | Per placement, aggregated by cohort | Monthly lagged | Pull client feedback and review screening or credential thresholds. |
| K7 | Prediction Accuracy at 6 Months | Research / AI Talent Strategy | Per prediction | Monthly batch | Run prediction post-mortem and recalibrate signal weighting. |

## K1: Signal Strength Score

| Field | Definition |
| --- | --- |
| Business question | How strong is the evidence that a market shift requires a curriculum, credential, or positioning response? |
| Formula | Weighted score from 0 to 100: `SourceDiversity`, `Recency`, `Corroboration`, and `CommercialPull`, each weighted 25% in v1. |
| Component logic | `SourceDiversity`: distinct source classes capped at 5 and scaled 0-100. `Recency`: decay over 90 days. `Corroboration`: independent sightings capped at 10 and scaled 0-100. `CommercialPull`: named client demand scored 0 or 100. |
| Owner | Research / AI Talent Strategy. |
| Grain | Per signal, aggregated into a monthly signal register summary. |
| Dimensions | Signal type, source class, role archetype, geography, client segment, horizon window. |
| Sources | Manual signal register in v1; later job feeds, CRM notes, client feedback, win/loss notes, and vetting feedback. |
| Data quality risks | Subjective scoring, duplicate sources, hype-cycle inflation, logging date confused with source date. |
| Refresh cadence | Weekly intake, quarterly weight review. |
| Thresholds | Green: `>= 70`. Amber: `40-69`. Red: `< 40`. |
| Triggered action when red | No automatic action for a single red signal. If five or more red signals cluster in one signal type within 60 days, escalate to the monthly horizon review. |
| Exclusions | Unsourced claims, duplicate reposts, and signals without a source date. |
| Data confidence | Low in v1 because scoring is manual. |
| Caveat | This score is a ranking aid, not a probability. |

## K2: Signal-to-Decision Time

| Field | Definition |
| --- | --- |
| Business question | How long does it take to move from validated market signal to documented decision? |
| Formula | `DecisionSignedDate - SignalThresholdDate`, in calendar days. |
| Owner | AI Talent Strategy. |
| Grain | Per green signal. |
| Dimensions | Signal type, decision class, owner, function, horizon window. |
| Sources | Signal register and decision register. |
| Data quality risks | Missing dates, reconstructed historical decisions, deliberate watch items counted as stalled. |
| Refresh cadence | Weekly. |
| Thresholds | Green: `<= 21 days`. Amber: `22-45 days`. Red: `> 45 days`. |
| Triggered action when red | Review stalled item, assign named decision owner, and set due date within seven days. |
| Exclusions | Signals explicitly marked `watch`, `rejected`, or `duplicate`. |
| Data confidence | Medium once the decision register is active; low during backfill. |
| Caveat | Long incubation is acceptable only when intentionally logged as watch or defer. |

## K3: Decision-to-Release Time

| Field | Definition |
| --- | --- |
| Business question | How long does it take to operationalize a signed decision? |
| Formula | `ReleaseDate - DecisionSignedDate`, in calendar days. |
| Owner | Learning, with Assessment Ops consulted for credential and rubric changes. |
| Grain | Per decision. |
| Dimensions | Decision class, complexity tier, programme, release artifact type. |
| Sources | Decision register, curriculum version log, assessment rubric log, LMS release log, programme delivery board. |
| Data quality risks | Release definition varies by artifact type, dependency bottlenecks, cohort calendar constraints. |
| Refresh cadence | Weekly. |
| Thresholds | Low complexity: green `<= 14 days`, red `> 30 days`. Medium: green `<= 30 days`, red `> 60 days`. High: green `<= 60 days`, red `> 90 days`. |
| Triggered action when red | Re-plan blocked release, name dependency owner, and set revised release commitment. |
| Exclusions | Decisions intentionally scheduled for a future cohort window and marked `scheduled`. |
| Data confidence | Medium. |
| Caveat | A long release time may reflect legitimate cohort timing rather than delivery failure. |

## K4: Curriculum/Credential Changes per Quarter

| Field | Definition |
| --- | --- |
| Business question | Is the programme evolving often enough, and is at least one quarterly change traceable to market evidence? |
| Formula | `count(released_changes in quarter)` and `count(market_traceable_changes) / count(total_released_changes)`. |
| Owner | Learning + Assessment Ops. |
| Grain | Quarterly. |
| Dimensions | Change scope, programme, trigger source, credential tier, assessment artifact. |
| Sources | Decision register, curriculum versioning, assessment rubric repository. |
| Data quality risks | Cosmetic edits counted as meaningful changes, missing trigger-source tags, inconsistent versioning. |
| Refresh cadence | Monthly check, quarterly close. |
| Thresholds | Green: at least three total released changes and at least one market-traceable change. Amber: at least one market-traceable change but fewer than three total, or three total with zero market-traceable. Red: zero market-traceable changes. |
| Triggered action when red | Run change-debt review and identify the next market-traceable change before quarter close. |
| Exclusions | Typo fixes, copy polish, administrative edits, and delivery-only scheduling changes. |
| Data confidence | Medium if versioning is disciplined. |
| Caveat | Change volume is not success by itself; pair this KPI with placement and retention outcomes. |

## K5: Placement Rate Delta

| Field | Definition |
| --- | --- |
| Business question | Are programme or credential changes improving placement conversion? |
| Formula | `PostChangePlacementRate - PreChangePlacementRate`, where `PlacementRate = placed_within_window / eligible_for_placement`. Recommended window: 60 days from credential issuance. Baseline: prior three comparable cohorts. |
| Owner | Matching + CSM. |
| Grain | Per cohort, compared with rolling baseline. |
| Dimensions | Cohort, programme, archetype, credential tier, geography, seniority, client segment. |
| Sources | Credential issuance log, matching system, CSM placement records, CRM opportunity data. |
| Data quality risks | Placement definition disagreement, demand seasonality, client mix shifts, small sample sizes, exposure uncertainty. |
| Refresh cadence | Monthly. |
| Thresholds | Green: `>= +5 percentage points`. Amber: within `+/- 5 percentage points`. Red: `<= -5 percentage points`. |
| Triggered action when red | Run funnel diagnostic across vetting, matching, client selection, and start-date conversion. Verify the cohort was exposed to the relevant change. |
| Exclusions | Cohorts with `n < 25` as standalone views; unavailable talent; candidates outside defined placement eligibility window. |
| Data confidence | Medium if matching and placement systems reconcile. |
| Caveat | Placement is multi-causal. Treat this as directional unless confounders are controlled. |

## K6: 90-Day Retention Delta

| Field | Definition |
| --- | --- |
| Business question | Do post-change placements sustain performance and client satisfaction at 90 days? |
| Formula | `PostChangeRetentionRate - PreChangeRetentionRate`, where `RetentionRate = active_at_day_90_and_satisfactory / placements_started`. Recommended satisfaction threshold: client rating `>= 4/5`. |
| Owner | CSM + Talent Experience. |
| Grain | Per placement, aggregated by cohort. |
| Dimensions | Cohort, archetype, credential tier, client, geography, engagement type, seniority. |
| Sources | CSM platform, client check-in survey, matching system start dates, termination reason log. |
| Data quality risks | 90-day measurement lag, survey response bias, client project changes, termination reason ambiguity. |
| Refresh cadence | Monthly batch for placements crossing day 90. |
| Thresholds | Green: `>= +3 percentage points`. Amber: within `+/- 3 percentage points`. Red: `<= -3 percentage points`. |
| Triggered action when red | Pull qualitative client feedback, inspect termination reasons, and review credential threshold or pre-placement screening. |
| Exclusions | Placements not yet at day 90, client-side cancellations unrelated to talent performance, cohorts with `n < 25` as standalone views. |
| Data confidence | Medium to low until the 90-day check-in process is standardized. |
| Caveat | A retention dip can reflect client-side changes rather than talent quality. |

## K7: Prediction Accuracy at 6 Months

| Field | Definition |
| --- | --- |
| Business question | Are horizon predictions being validated by market movement six months later? |
| Formula | `confirmed_predictions / scored_predictions`, where scored predictions are those whose six-month scoring window has been reached. |
| Owner | Research / AI Talent Strategy. |
| Grain | Per prediction. |
| Dimensions | Signal type, horizon class, confidence tag, source mix, role archetype. |
| Sources | Prediction register, signal register, placement outcomes, external market evidence. |
| Data quality risks | Vague predictions, retrospective rationalization, overuse of inconclusive outcomes, small sample size. |
| Refresh cadence | Monthly batch. |
| Thresholds | Green: `>= 60% confirmed`. Amber: `40-59%`. Red: `< 40%`. |
| Triggered action when red | Run prediction post-mortem, tighten falsifiability rules, and recalibrate K1 weighting. |
| Exclusions | Predictions without predefined confirming and contradicting criteria; predictions whose six-month scoring date has not arrived. |
| Inconclusive handling | Exclude from the numerator and denominator, but monitor inconclusive rate as a data quality flag. If inconclusive rate exceeds 30%, review prediction-writing standards. |
| Data confidence | Low until at least two six-month scoring batches are complete. |
| Caveat | Treat the first year as calibration rather than performance judgment. |

