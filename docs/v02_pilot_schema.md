# v0.2 Pilot Schema

## Purpose

The v0.2 pilot schema defines the minimum field contract for expanding Decision
Spine from a decision dashboard into an intelligence engine. It covers role
demand, competency gaps, horizon radar, and curriculum impact simulation.

The executable contract lives in `data/v02_intelligence_requirements.json`.
`scripts/schema_gap_review.py` reads that file and reports which fields are
covered by current seed data, pilot templates, and source contracts.

## Product Boundary

v0.2 is still a pilot. It should not claim production forecasting, causal impact,
or learner-level analytics.

It should answer:

- Which role anchors are most worth prioritizing?
- Which competencies appear under-taught or over-taught?
- Which weak signals deserve horizon review?
- Which curriculum changes have plausible cost and placement impact?

It should not yet:

- ingest live job-market feeds,
- store learner-level records,
- expose client/account-level data,
- automate curriculum changes,
- produce high-confidence forecasts from synthetic data.

## Capability Contracts

| Capability | Current File | Decision It Unlocks |
| --- | --- | --- |
| Role Anchor Demand Index | `signals.json` | Rank role anchors by demand strength, durability, and placement relevance. |
| Competency Gap Index - market side | `role_competencies.json` | Decide teach-now, monitor, or deprecate treatment for role competencies. |
| Competency Gap Index - learner side | `learner_evidence_summary.json` | Compare market-required proficiency with aggregated learner evidence. |
| Horizon Radar | `predictions.json` | Track weak, accelerating, baseline, and commoditizing signals by horizon. |
| Curriculum Impact Simulator | `releases.json` | Estimate cost and expected placement or extension impact for proposed changes. |

## Current Missing Fields

As of the current seed schema, `scripts/schema_gap_review.py` reports 18 v0.2
field gaps:

| Capability | Missing Fields |
| --- | --- |
| Role Anchor Demand Index | `compensation_pressure`, `demand_growth_rate`, `demand_volume`, `hiring_velocity`, `placement_conversion_alignment`, `strategic_durability_score` |
| Competency Gap Index - market side | `deprecation_signal`, `market_required_proficiency`, `tool_decay_risk` |
| Competency Gap Index - learner side | `demonstrated_proficiency`, `proficiency_gap_score` |
| Horizon Radar | `maturity_stage`, `review_due_date`, `weak_signal_theme` |
| Curriculum Impact Simulator | `estimated_learner_time_delta`, `expected_extension_lift`, `expected_placement_lift`, `instructional_capacity_cost` |

## Pilot Data Rules

- Treat all role-demand values as summarized evidence, not raw client or account
  records.
- Keep learner evidence aggregated at cohort or competency level.
- Suppress or block learner-derived evidence when privacy posture is not clear.
- Mark every v0.2 field with a source owner before it is used in recommendations.
- Keep synthetic seed data separate from any approved real pilot extract.
- Use the schema gap review before requesting new fields from source owners.

## Review Command

```bash
python3 scripts/schema_gap_review.py
```

The review should be clean enough to show stakeholders:

- what the current MVP can already support,
- what v0.2 needs next,
- which fields are blocked by privacy or ownership,
- which pilot fields are worth requesting first.
