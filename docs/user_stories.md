# Decision Spine MVP User Stories

## What Makes A Story Useful Here

A useful Decision Spine story must help someone make or audit a real operating decision. Stories that only say "show a dashboard" are too weak.

Each story uses the standard format:

```text
As a [user], I want [capability], so I can [outcome].
```

Each story also names:

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
| P1 | 3. Trace A Release Back To Evidence | Executive stakeholder | Trust that a change is market-backed. |
| P0 | 4. Identify Approved Decisions That Are Not Released | Learning lead | Remove blockers from curriculum, credential, or assessment work. |
| P1 | 5. Produce The Monthly Council Review Packet | Council chair | Run a meeting around exceptions and actions. |
| P1 | 6. Learn Whether A Released Change Improved Placement | Matching lead | Keep, adjust, or investigate a released change. |
| P1 | 7. Learn Whether Placements Are Sustaining At 90 Days | CSM lead | Investigate retention risk after a change. |
| P1 | 8. Score Horizon Predictions | Research lead | Recalibrate market judgment and signal weighting. |
| P2 | 9. Publish A Decision Changelog | Executive stakeholder | Communicate what changed and why. |
| P2 | 10. Document Seed Data Contribution Rules | Contributor | Update the MVP dataset without breaking reports. |
| P2 | 11. Package Market Evidence For Client Positioning | Solutions and Sales lead | Explain why Andela talent is aligned to current AI demand. |
| P1 | 12. Translate Signals Into Credential Requirements | Assessment Ops lead | Update evidence thresholds without weakening credential integrity. |
| P1 | 13. Translate Signals Into Learning Outcomes | Developer Learning lead | Adjust programme design based on validated market demand. |
| P2 | 14. Reuse Intelligence In Training Offers | Training as a Service lead | Shape client training products from market-backed capability gaps. |
| P2 | 15. Surface Credential Signals In Talent Profiles | Talent Experience lead | Help talent show market-relevant capability clearly. |
| P0 | 16. Validate Decision Spine Data Quality | Data/Analytics lead | Trust KPI outputs before they influence decisions. |
| P1 | 17. Align Releases To Cohort Delivery Windows | Delivery lead | Schedule approved changes without disrupting active cohorts. |

## Stakeholder Coverage

| Stakeholder From Council Charter | Covered By |
| --- | --- |
| Signal Intelligence Council | Stories 1, 2, 5 |
| Solutions and Sales | Stories 3, 9, 11 |
| Training as a Service | Story 14 |
| Matching | Stories 6, 11 |
| CSM | Story 7 |
| Research and Innovation | Stories 1, 8 |
| Assessment Ops | Stories 4, 12 |
| Developer Learning | Stories 4, 13 |
| Talent Experience | Story 15 |
| Executive stakeholder | Stories 3, 9 |
| Contributor | Story 10 |
| Data/Analytics | Story 16 |
| Delivery | Story 17 |

Blueprint council-function coverage:

| Blueprint Function | Covered By |
| --- | --- |
| Academy | Stories 12, 13 |
| Matching | Stories 6, 11 |
| Data | Stories 10, 16 |
| Delivery | Stories 4, 17 |
| Client Success | Story 7 |

## Stress Test Results

The stakeholder coverage is now complete against `docs/signal_intelligence_council.md`, but not every story is equally ready for MVP implementation.

| Test | Result | Backlog Response |
| --- | --- | --- |
| Stakeholder coverage | Pass | Every charter stakeholder has at least one explicit story. |
| Standard story format | Pass | Every story uses `As a [user], I want [capability], so I can [outcome].` |
| Decision usefulness | Pass with one priority change | Every story names the operating decision it enables; traceability moved from P0 to P1 because validation and operating queues come first. |
| Current seed data support | Mixed | Stories 1-10, 12-13, and 16 are directly supported. Stories 11, 14, 15, and 17 are partially supported until commercial, training, talent-profile, and cohort calendar data exists. |
| Acceptance-test clarity | Mostly pass | Stories include concrete seed-data test cases; future-data-dependent stories must label missing data rather than imply precision. |
| Traceability | Pass | Stories require signal -> decision -> release links where claims depend on evidence. |
| Responsibility separation | Pass after adjustment | Contributor documentation and automated validation are separate stories. |
| Priority realism | Pass after adjustment | Future-data-dependent commercial packaging is P2; automated data validation is P0 because every other story depends on it. |
| Temporal joins | Pass after adjustment | Future release cohorts may not yet exist in outcome data; this is a warning state, not always a failure. |

MVP guardrails:

- Story 16 must be implemented before stories that turn KPI output into operating decisions.
- If a story asks for data not present in `data/`, the output must label that field as unavailable rather than infer it.
- Placement and retention evidence can support commercial, training, or talent-facing stories only when linked cohort data exists.
- Client-segment and geography views are signal-derived in v1; they are not full CRM segmentation.
- Talent-profile and training-offer stories should produce recommendation inputs in v1, not write to downstream systems.
- Cohort delivery-window stories can use `cohort_id` in v1, but actual scheduling confidence requires cohort calendar data.
- A release `cohort_id` can point to a future cohort that is not yet present in `cohort_outcomes.json`; validation should label this as "future cohort / no outcomes yet" when the release is pending.

## Implementation Triage

| Tier | Stories | Reason |
| --- | --- | --- |
| Build first | 16, 2, 4 | Validates the data, then exposes the two most important operating queues. |
| Build next | 1, 5, 12, 13 | Enables council review, credential translation, and learning translation once the queues are trustworthy. |
| Build after outcome maturity | 6, 7, 8, 17 | Useful now, but stronger as placement, retention, prediction, and cohort-calendar data matures. |
| Build as stakeholder outputs | 3, 9, 11, 14, 15 | Important for communication and adoption, but should not precede the operating loop. |
| Keep as contributor support | 10 | Helps maintain the dataset, but automation in Story 16 is the enforcement mechanism. |

## Story 1: Decide Whether A Signal Needs Action

As a Signal Intelligence Council member, I want a signal review view that shows evidence strength, context, and recommended next step, so I can decide whether to act, monitor, reject, or defer.

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

As a council chair, I want to see green signals that have no linked decision, so I can assign an owner before validated evidence disappears into discussion.

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

As an executive stakeholder, I want each released change to trace back to the signal evidence that justified it, so I can trust that programme changes are market-backed.

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

As a Learning lead, I want a release accountability queue, so I can keep approved curriculum, credential, and assessment decisions from remaining in progress without follow-up.

Business value:

- Converts governance decisions into operational delivery.
- Highlights release bottlenecks before they become stale.
- Gives Learning and Assessment Ops a shared queue.

Data needed:

- `data/decisions.json`
- `data/releases.json`
- K3 thresholds from `docs/kpi_dictionary.md`

Acceptance criteria:

- Approved decisions with no release record are flagged as "no release logged."
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

As a council chair, I want one monthly review packet that separates healthy metrics from exceptions, so I can focus the meeting on decisions, owners, and follow-up.

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

As a Matching lead, I want to compare post-change placement rates against comparable pre-change cohorts, so I can decide whether a released change appears to improve placement conversion.

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

As a CSM lead, I want to compare 90-day retention after a change against the prior baseline, so I can identify whether talent placements are sustaining.

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

As a Research lead, I want prediction scoring to separate confirmed, contradicted, inconclusive, and pending claims, so I can improve future market judgment with the council.

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

As an executive stakeholder, I want a concise changelog of released and pending changes, so I can see how the intelligence engine is shaping curriculum, credentialing, assessment, and positioning.

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

## Story 10: Document Seed Data Contribution Rules

As a contributor, I want clear seed data contribution rules, so I can add new examples without breaking reporting or traceability.

Business value:

- Keeps the MVP credible as more examples are added.
- Reduces avoidable data entry errors before validation runs.
- Makes the repo easier for other contributors to extend.

Data needed:

- All files in `data/`
- `data/README.md`

Acceptance criteria:

- Required fields are documented for signals, decisions, releases, outcomes, and predictions.
- Join-key expectations are documented for signal IDs, decision IDs, release cohort IDs, and prediction signal IDs, including future cohort exceptions.
- Date conventions are documented as `YYYY-MM-DD` or `null` where allowed.
- Known values are documented for fields such as `green`, `amber`, `red`, `released`, `in_progress`, `confirmed`, `contradicted`, and `pending`.
- The documentation points contributors to the automated validation from Story 16.
- The story is done when a contributor can add a new signal, decision, release, cohort, or prediction and know what validation will check.

Useful test cases:

- A contributor can identify which fields are required before adding a new release.
- A contributor can tell which IDs must join across files.
- A contributor can tell whether a missing date should be `null` or omitted.

## Story 11: Package Market Evidence For Client Positioning

As a Solutions and Sales lead, I want market signals, released changes, and placement outcomes packaged by role archetype and client segment, so I can explain why Andela talent is aligned to current AI demand.

Business value:

- Turns council evidence into commercial positioning.
- Helps Sales avoid generic AI claims.
- Supports premium authorization with traceable proof.

Data needed:

- `data/signals.json`
- `data/decisions.json`
- `data/releases.json`
- `data/cohort_outcomes.json`

Acceptance criteria:

- The view groups evidence by role archetype, programme, geography, and client segment.
- Each positioning claim links to at least one signal and one relevant release when available.
- Placement and retention outcomes are shown as supporting evidence only when data is available.
- Low-confidence, pending, or small-n evidence is clearly labeled.
- Missing commercial fields, such as CRM opportunity detail or client account data, are labeled unavailable in v1.
- The story is done when Sales can answer "why this talent profile now?" with traceable evidence.

Useful test cases:

- Enterprise SaaS positioning for Builders includes `SIG-2026-001` and `REL-2026-001`.
- Financial services Scaler positioning includes `SIG-2026-002` and `REL-2026-002`.
- Prototyper multimodal positioning flags `COH-2026-04-PROTOTYPER` as pending and small-n.

## Story 12: Translate Signals Into Credential Requirements

As an Assessment Ops lead, I want validated market signals translated into credential requirements and evidence thresholds, so I can update assessments without weakening credential integrity.

Business value:

- Keeps credentials tied to demonstrated capability.
- Makes market-informed assessment changes auditable.
- Reduces the risk of adding vague or aspirational credential tags.

Data needed:

- `data/signals.json`
- `data/decisions.json`
- `data/releases.json`

Acceptance criteria:

- Credential and assessment decisions are separated from curriculum-only decisions.
- Each credential or assessment requirement links to the signal that justified it.
- Each requirement includes decision rationale, complexity tier, owner, release status, and artifact.
- Watch or rejected signals are visible as non-requirements, with rationale.
- The story is done when Assessment Ops can tell which evidence thresholds need creation, revision, or monitoring.

Useful test cases:

- `DEC-2026-002` appears as a credential requirement tied to integration architecture.
- `DEC-2026-004` appears as an assessment update for AI security and privacy checks.
- `DEC-2026-003` appears as monitor, not as a new credential requirement.

## Story 13: Translate Signals Into Learning Outcomes

As a Developer Learning lead, I want validated signals and approved decisions translated into learning outcome changes, so I can adjust programme design based on market demand.

Business value:

- Converts evidence into teachable programme changes.
- Helps Learning prioritize what to add, monitor, or deprecate.
- Keeps curriculum decisions connected to expected placement impact.

Data needed:

- `data/signals.json`
- `data/decisions.json`
- `data/releases.json`
- `data/cohort_outcomes.json`

Acceptance criteria:

- Curriculum decisions are separated from credential, assessment, monitor, and positioning decisions.
- Each learning change shows signal theme, decision summary, programme, artifact, release status, and linked cohort.
- Pending outcomes are labeled separately from available placement or retention results.
- Monitor decisions are visible as "do not add yet" inputs.
- The story is done when Developer Learning can decide which learning outcomes to add, revise, monitor, or leave unchanged.

Useful test cases:

- `DEC-2026-001` appears as an AI Builder learning outcome change.
- `DEC-2026-005` appears as an AI Prototyper learning outcome change.
- `DEC-2026-003` explains why prompt library maintenance is monitored rather than added as a module.

## Story 14: Reuse Intelligence In Training Offers

As a Training as a Service lead, I want market evidence, credential frameworks, and programme quality signals summarized by capability area, so I can shape client training offers around validated capability gaps.

Business value:

- Reuses internal intelligence in external training products.
- Helps client training offers stay grounded in current demand.
- Creates a bridge between Andela's talent engine and client upskilling needs.

Data needed:

- `data/signals.json`
- `data/decisions.json`
- `data/releases.json`
- `docs/signal_intelligence_council.md`

Acceptance criteria:

- Capability areas are summarized with signal strength, horizon window, role archetype, and relevant programme changes.
- Training offer inputs distinguish validated capabilities from monitored or low-confidence signals.
- Each recommendation includes the source signals and internal release artifacts that support it.
- Regulated-client needs are distinguishable from general market demand.
- Gaps that require external training product, pricing, or client diagnostic data are labeled as future-data-dependent.
- The story is done when Training as a Service can identify which capability gaps are ready for client-facing training design.

Useful test cases:

- Agent evaluation and observability appears as a validated Builder capability area.
- AI security and privacy controls appear as a regulated-client Scaler capability area.
- Prompt library maintenance appears as monitor, not a standalone training offer.

## Story 15: Surface Credential Signals In Talent Profiles

As a Talent Experience lead, I want credential and horizon intelligence translated into talent-facing profile signals, so I can help talent show market-relevant capability clearly.

Business value:

- Helps talent understand which capabilities matter in the market.
- Improves profile quality for Matching and client conversations.
- Avoids profile tags that are not backed by demonstrated evidence.

Data needed:

- `data/signals.json`
- `data/decisions.json`
- `data/releases.json`

Acceptance criteria:

- Talent-facing profile signals map to validated signals and released credential or curriculum artifacts.
- Each profile signal includes the role archetype and capability area it supports.
- Pending releases are not presented as active profile signals.
- Low-confidence or monitored signals are excluded from active profile tags but may appear as future guidance.
- The v1 output creates profile guidance only; it does not assume integration with a talent profile system.
- The story is done when Talent Experience can update profile guidance without inventing unsupported AI capability labels.

Useful test cases:

- Builder profiles can reference evaluation engineering only after `REL-2026-001`.
- Scaler profiles can reference integration architecture evidence after `REL-2026-002`.
- Multimodal prototyping can be suggested for Prototyper profile guidance after `REL-2026-004`.

## Story 16: Validate Decision Spine Data Quality

As a Data/Analytics lead, I want automated validation of Decision Spine seed data, so I can trust KPI outputs before they influence council decisions.

Business value:

- Protects every downstream KPI and story from silent data errors.
- Gives contributors fast feedback when sample data changes.
- Makes the MVP credible enough for operating review.

Data needed:

- All files in `data/`
- `docs/kpi_dictionary.md`

Acceptance criteria:

- Required fields are checked for signals, decisions, releases, cohort outcomes, and predictions.
- Join keys are checked across signal, decision, release, cohort, and prediction records.
- Pending releases may reference future cohort IDs that do not yet exist in `cohort_outcomes.json`; these are warnings, not failures.
- KPI-critical dates are validated as `YYYY-MM-DD` or allowed `null`.
- Status-like fields are checked against known values.
- Validation failures name the file, record ID, field, and reason.
- The story is done when `scripts/report_kpis.py` cannot silently produce misleading output from broken joins or malformed dates.

Useful test cases:

- A release linked to an unknown decision fails validation.
- A decision linked to an unknown signal fails validation.
- A pending release linked to a future cohort absent from outcomes is labeled "future cohort / no outcomes yet."
- A prediction with a past scoring date and pending outcome is flagged for review.

## Story 17: Align Releases To Cohort Delivery Windows

As a Delivery lead, I want approved releases mapped to cohort IDs and release status, so I can schedule changes without disrupting active cohorts.

Business value:

- Prevents approved changes from missing the relevant cohort window.
- Helps Delivery, Learning, and Assessment Ops coordinate timing.
- Separates true delivery delay from intentional cohort scheduling.

Data needed:

- `data/decisions.json`
- `data/releases.json`
- `data/cohort_outcomes.json`

Acceptance criteria:

- Each release shows programme, artifact, release status, release date, and linked `cohort_id`.
- Released items with unknown cohort IDs are flagged as data quality issues.
- Pending items with target cohort IDs absent from outcomes are labeled "future cohort / no outcomes yet."
- Pending releases show the target cohort even when `release_date` is unavailable.
- The output labels actual cohort calendar detail as unavailable in v1.
- The story is done when Delivery can identify which approved changes need timing coordination before the next cohort starts.

Useful test cases:

- `REL-2026-003` maps to `COH-2026-06-SCALER` and appears pending.
- `REL-2026-001` maps to `COH-2026-03-BUILDER` and appears released.
- A released item with a missing or unknown `cohort_id` fails the delivery-window check.

## Near-Term Sprint Slice

The smallest useful next sprint is:

1. Story 16: Validate Decision Spine Data Quality.
2. Story 2: Find Validated Signals With No Decision.
3. Story 4: Identify Approved Decisions That Are Not Released.
4. Story 1: Decide Whether A Signal Needs Action.
5. Story 12: Translate Signals Into Credential Requirements.
6. Story 5: Produce The Monthly Council Review Packet.

This slice strengthens the operating loop before adding richer dashboard presentation.
