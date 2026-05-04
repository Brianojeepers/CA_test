# Decision Spine MVP User Stories

## What Makes A Story Useful Here

A useful Decision Spine story must help someone make or audit a real operating decision. Stories that only say "show a dashboard" are too weak. Each story below names:

- The user and decision moment.
- The data needed from the current MVP files.
- The behavior that makes the story complete.
- The outcome that should be possible once the story is done.

The MVP loop is:

```text
signals -> decisions -> releases -> cohort outcomes -> prediction learning
```

## Story Map

| Priority | Story | User | Decision Enabled |
| --- | --- | --- | --- |
| P0 | 1. Decide Whether A Signal Needs Action | Signal Intelligence Council member | Act, monitor, reject, or defer a market signal. |
| P0 | 2. Find Validated Signals With No Decision | Council chair | Assign an owner before validated evidence stalls. |
| P0 | 3. Trace A Release Back To Evidence | Executive stakeholder | Trust that a change is market-backed. |
| P0 | 4. Identify Approved Decisions That Are Not Released | Learning lead | Remove blockers from curriculum, credential, or assessment work. |
| P1 | 5. Produce The Monthly Council Review Packet | Council chair | Run a meeting around exceptions and actions. |
| P1 | 6. Learn Whether A Released Change Improved Placement | Matching lead | Keep, adjust, or investigate a released change. |
| P1 | 7. Learn Whether Placements Are Sustaining At 90 Days | CSM lead | Investigate retention risk after a change. |
| P1 | 8. Score Horizon Predictions | Research lead | Recalibrate market judgment and signal weighting. |
| P2 | 9. Publish A Decision Changelog | Executive stakeholder | Communicate what changed and why. |
| P2 | 10. Maintain Clean Seed Data | Contributor | Update the MVP dataset without breaking reports. |

## Story 1: Decide Whether A Signal Needs Action

As a Signal Intelligence Council member, I want a signal review view that shows evidence strength, context, and recommended next step so that I can decide whether to act, monitor, reject, or defer.

Business value:

- Prevents noisy market claims from becoming curriculum changes.
- Helps high-confidence signals move into governance quickly.
- Makes "no source, no change" operational.

Data needed:

- `data/signals.json`
- K1 thresholds from `docs/kpi_dictionary.md`

Acceptance criteria:

- The view lists each signal's `signal_id`, theme, type, role archetype, horizon window, geography, client segment, confidence, summary, score, and status.
- Green signals are presented as "ready for council decision."
- Amber signals are presented as "monitor or gather evidence."
- Red signals are presented as "do not act unless clustered or escalated."
- The user can see the score components that explain the final signal strength score.
- The story is done when a council member can justify the next step for every signal without opening raw JSON.

Useful test cases:

- `SIG-2026-001` appears as high-priority because it is green, commercially pulled, and tied to enterprise demand.
- `SIG-2026-003` appears as monitor because it is amber and has weak commercial pull.
- `SIG-2026-006` appears as do-not-act because it is red and low confidence.

## Story 2: Find Validated Signals With No Decision

As a council chair, I want to see green signals that have no linked decision so that validated evidence does not disappear into discussion.

Business value:

- Protects the signal-to-decision operating promise.
- Creates a weekly queue for ownership and follow-up.
- Reduces time from evidence validation to action.

Data needed:

- `data/signals.json`
- `data/decisions.json`
- K2 thresholds from `docs/kpi_dictionary.md`

Acceptance criteria:

- Every green signal is matched to decisions through `signal_ids`.
- A green signal with no linked decision is flagged as red and labeled "no decision logged."
- A linked signal shows the first decision signed after `green_threshold_date`.
- The report shows elapsed calendar days from `green_threshold_date` to `decision_signed_date`.
- The status uses K2 thresholds: green `<= 21 days`, amber `22-45 days`, red `> 45 days`.
- The story is done when the chair can identify which validated signals need an owner before the next council meeting.

Useful test cases:

- `SIG-2026-004` links to `DEC-2026-004` and is amber because the decision took 43 days.
- If a new green signal is added without a decision, it appears as red in this story's output.

## Story 3: Trace A Release Back To Evidence

As an executive stakeholder, I want each released change to trace back to the signal evidence that justified it so that I can trust that programme changes are market-backed.

Business value:

- Makes the evidence chain auditable.
- Prevents unsupported curriculum, assessment, or credential changes.
- Supports commercial narratives about why Andela's AI talent standards are changing.

Data needed:

- `data/signals.json`
- `data/decisions.json`
- `data/releases.json`

Acceptance criteria:

- Each release shows its `release_id`, artifact, programme, change type, release status, decision, and linked signal themes.
- A release is traceable only when its `decision_id` exists and at least one linked signal can be resolved.
- If `releases.linked_signal_ids` disagrees with the decision's `signal_ids`, the release is flagged for governance review.
- Releases with `market_traceable: false` or missing evidence are separated from compliant releases.
- The story is done when a reviewer can answer "what changed, who decided it, and what evidence supported it?" for every release.

Useful test cases:

- `REL-2026-001` traces to `DEC-2026-001` and `SIG-2026-001`.
- `REL-2026-003` is traceable but not released yet.

## Story 4: Identify Approved Decisions That Are Not Released

As a Learning lead, I want a release accountability queue so that approved curriculum, credential, and assessment decisions do not remain in progress without follow-up.

Business value:

- Converts governance decisions into operational delivery.
- Highlights release bottlenecks before they become stale.
- Gives Learning and Assessment Ops a shared queue.

Data needed:

- `data/decisions.json`
- `data/releases.json`
- K3 thresholds from `docs/kpi_dictionary.md`

Acceptance criteria:

- Approved decisions with linked releases show release status, artifact, programme, complexity tier, elapsed days, and owner.
- Released items calculate `release_date - decision_signed_date`.
- Unreleased items show `pending` and keep their decision owner visible.
- Status follows K3 thresholds by complexity tier.
- Pending releases are grouped separately from completed releases.
- The story is done when the Learning lead can name which approved decision needs a delivery unblock this week.

Useful test cases:

- `REL-2026-003` appears as pending because it has no `release_date`.
- `REL-2026-002` appears as amber because its high-complexity release took 61 days.

## Story 5: Produce The Monthly Council Review Packet

As a council chair, I want one monthly review packet that separates healthy metrics from exceptions so that the meeting focuses on decisions, owners, and follow-up.

Business value:

- Turns the KPI report into an operating ritual.
- Keeps red and pending items from being buried in aggregate metrics.
- Connects metric status to the red KPI protocol.

Data needed:

- All files in `data/`
- `docs/kpi_dictionary.md`
- `docs/red_kpi_protocol.md`

Acceptance criteria:

- The packet includes K1 through K7 status.
- Red, amber, and pending items are grouped before green items.
- Each exception includes the relevant owner when available.
- Each exception includes the expected next action from the KPI dictionary or red KPI protocol.
- The packet includes a "decisions needed this month" section.
- The story is done when the chair can run the monthly meeting from the packet without manually inspecting the seed data.

Useful test cases:

- The packet surfaces `REL-2026-003` as pending.
- The packet surfaces `SIG-2026-004 -> DEC-2026-004` as an amber signal-to-decision item.
- The packet shows pending prediction `PRED-2026-001` with its scoring date.

## Story 6: Learn Whether A Released Change Improved Placement

As a Matching lead, I want to compare post-change placement rates against comparable pre-change cohorts so that I can decide whether a released change appears to improve placement conversion.

Business value:

- Connects learning and credential changes to placement outcomes.
- Helps Matching distinguish useful change from noise.
- Creates a feedback loop from market evidence to commercial outcome.

Data needed:

- `data/releases.json`
- `data/cohort_outcomes.json`
- K5 thresholds from `docs/kpi_dictionary.md`

Acceptance criteria:

- Post-change cohorts are matched to pre-change cohorts with the same `baseline_group`.
- Placement rate delta is calculated as `post_change_rate - average_pre_change_rate`.
- Delta is displayed in percentage points.
- Cohorts with `eligible_for_placement < 25` are labeled small-n and treated as directional.
- Missing placement outcomes are marked pending.
- The story is done when Matching can decide whether to keep monitoring, investigate, or amplify a released change.

Useful test cases:

- `COH-2026-03-BUILDER` shows a positive placement delta against the AI Builder baseline.
- `COH-2026-04-SCALER` is pending because placement data is not available.
- `COH-2026-04-PROTOTYPER` is pending and small-n.

## Story 7: Learn Whether Placements Are Sustaining At 90 Days

As a CSM lead, I want to compare 90-day retention after a change against the prior baseline so that I can identify whether talent placements are sustaining.

Business value:

- Prevents placement rate from becoming the only success measure.
- Connects client satisfaction and retention back into programme design.
- Identifies when credential thresholds or matching guidance may need adjustment.

Data needed:

- `data/releases.json`
- `data/cohort_outcomes.json`
- K6 thresholds from `docs/kpi_dictionary.md`

Acceptance criteria:

- Retention is calculated only for cohorts with `retention_90d_rate`.
- Pending 90-day outcomes are excluded from the delta calculation.
- Retention delta is calculated against matching pre-change baseline groups.
- Red retention deltas include a review prompt for client feedback, termination reasons, and credential thresholds.
- The story is done when CSM can tell whether a post-change cohort is ready for retention review or still waiting for data.

Useful test cases:

- `COH-2026-03-BUILDER` is pending for retention because 90-day data is not available.
- Pre-change Builder cohorts are available as the retention baseline once post-change data arrives.

## Story 8: Score Horizon Predictions

As a Research lead, I want prediction scoring to separate confirmed, contradicted, inconclusive, and pending claims so that the council can improve future market judgment.

Business value:

- Makes horizon calls falsifiable.
- Reduces retrospective storytelling.
- Improves signal weighting and prediction quality over time.

Data needed:

- `data/predictions.json`
- `data/signals.json`
- K7 thresholds from `docs/kpi_dictionary.md`

Acceptance criteria:

- Predictions are scored only when `scoring_date` has passed.
- Only confirmed and contradicted predictions count in the accuracy denominator.
- Pending predictions show their scoring date and linked signal themes.
- Predictions missing confirming or contradicting criteria are flagged as invalid for future scoring.
- Accuracy uses K7 thresholds: green `>= 60%`, amber `40-59%`, red `< 40%`.
- The story is done when Research can run a prediction post-mortem without rewriting the criteria after the fact.

Useful test cases:

- `PRED-2025-001` counts as confirmed.
- `PRED-2025-002` counts as contradicted.
- `PRED-2026-001` is pending until 2026-09-18.

## Story 9: Publish A Decision Changelog

As an executive stakeholder, I want a concise changelog of released and pending changes so that I can see how the intelligence engine is shaping curriculum, credentialing, assessment, and positioning.

Business value:

- Makes the operating system visible outside the council.
- Helps commercial and delivery teams explain what changed.
- Creates a lightweight audit trail for stakeholders.

Data needed:

- `data/signals.json`
- `data/decisions.json`
- `data/releases.json`

Acceptance criteria:

- The changelog lists released items first, then pending items.
- Each item includes artifact, programme, change type, release date or pending status, decision summary, owner, and linked signal themes.
- The changelog excludes watch decisions unless they explain why no change was made.
- Each item includes a short "why this matters" line from signal summary or decision rationale.
- The story is done when stakeholders can understand the latest operating changes in under five minutes.

Useful test cases:

- `DEC-2026-003` appears only as a monitored signal, not as a released change.
- `REL-2026-004` appears as a released Prototyper curriculum change tied to multimodal product prototyping.

## Story 10: Maintain Clean Seed Data

As a contributor, I want data validation rules for the seed files so that adding new examples does not break reporting or traceability.

Business value:

- Keeps the MVP credible as more examples are added.
- Reduces silent data errors.
- Makes the repo easier for other contributors to extend.

Data needed:

- All files in `data/`
- `data/README.md`

Acceptance criteria:

- Required fields are documented for signals, decisions, releases, outcomes, and predictions.
- Join keys are validated: signal IDs, decision IDs, release cohort IDs, and prediction signal IDs.
- Date fields are validated as `YYYY-MM-DD` or `null` where allowed.
- Enum-like fields are checked for known values such as `green`, `amber`, `red`, `released`, `in_progress`, `confirmed`, `contradicted`, and `pending`.
- The local KPI report fails clearly if a required field or join key is missing.
- The story is done when a contributor can add a new signal, decision, release, cohort, or prediction and know whether the dataset is still coherent.

Useful test cases:

- A release with an unknown `decision_id` fails validation.
- A decision with a missing `signal_ids` entry fails validation.
- A prediction with no confirming criterion is flagged as invalid for scoring.

## Near-Term Sprint Slice

The smallest useful next sprint is:

1. Story 2: Find Validated Signals With No Decision.
2. Story 4: Identify Approved Decisions That Are Not Released.
3. Story 5: Produce The Monthly Council Review Packet.
4. Story 10: Maintain Clean Seed Data.

This slice strengthens the operating loop before adding richer dashboard presentation.
