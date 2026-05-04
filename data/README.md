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
| `role_competencies.json` | Role-archetype competency targets linked to signals, decisions, releases, and pedagogy. |
| `learner_evidence_summary.json` | Aggregated proficiency evidence by competency and cohort. |
| `pedagogy_map.json` | Optional pedagogical framing for selected learning, credential, and assessment changes. |
| `source_contracts.json` | Source-owner, privacy, field, freshness, and readiness contracts for real-data pilot extracts. |

The operating role accountable for turning this evidence into action is defined in
`docs/signal_intelligence_council.md`.

## Join Keys

| Key | Used In |
| --- | --- |
| `signal_id` | `signals.json`, `decisions.json`, `predictions.json` |
| `decision_id` | `decisions.json`, `releases.json` |
| `cohort_id` | `releases.json`, `cohort_outcomes.json` |
| `prediction_id` | `predictions.json` |
| `competency_id` | `role_competencies.json` |
| `evidence_id` | `learner_evidence_summary.json` |
| `pedagogy_id` | `pedagogy_map.json` |
| `contract_id` | `source_contracts.json` |

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

Run the Developer Learning outcome view:

```bash
python3 scripts/learning_outcomes.py
```

The learning outcomes view shows curriculum changes, linked market evidence,
release status, cohort exposure, outcome readiness, and monitor decisions that
should not become learning modules yet.

Run the concise monthly council packet:

```bash
python3 scripts/monthly_packet.py
```

The monthly packet summarizes data trust, KPI posture, signal posture, decisions
needed, credential and learning work, and prediction follow-ups. Each section
includes a drill-down command for granular review.

Run the stakeholder-facing decision changelog:

```bash
python3 scripts/decision_changelog.py
```

The decision changelog lists released changes, pending changes, monitor/no-change
decisions, and any approved decisions missing a release record.

Run the Matching and CSM outcome review:

```bash
python3 scripts/outcome_review.py
```

The outcome review shows post-change cohorts, linked releases, placement and
retention deltas, small-n and pending-data flags, confidence, and suggested
actions.

Run the Sales and Solutions positioning view:

```bash
python3 scripts/client_positioning.py
```

The positioning view groups market evidence by role archetype, client segment,
and geography, then shows relevant artifacts, outcomes, caveats, and suggested
positioning claims.

Run the Training as a Service offer input view:

```bash
python3 scripts/training_offer_inputs.py
```

The training offer input view summarizes capability areas, validated evidence,
internal artifacts, regulated-client relevance, and future data needed before
client-facing training products are designed.

Run the Talent Experience profile signal view:

```bash
python3 scripts/talent_profile_signals.py
```

The talent profile signal view translates released, market-backed capabilities
into profile guidance inputs and excludes monitored or unsupported tags.

Run the Delivery cohort window review:

```bash
python3 scripts/delivery_window_review.py
```

The delivery window review maps approved releases to target cohort IDs, release
status, and available cohort timing context. Actual cohort calendar detail is
unavailable in v1.

Run the pedagogical framing review:

```bash
python3 scripts/pedagogy_review.py
```

The pedagogy review shows optional Bloom/Dreyfus/performance-evidence framing for
selected decisions and releases. See `docs/pedagogical_framing.md` for the design
rules behind this map.

Run the role competency gap review:

```bash
python3 scripts/competency_gap_review.py
```

The competency gap review groups role-archetype capability targets by market
priority, linked signals, releases, pedagogy, and gap hypothesis. See
`docs/competency_ontology.md` for the ontology rules.

Run the proficiency readiness review:

```bash
python3 scripts/proficiency_readiness_review.py
```

The proficiency readiness review shows aggregated learner evidence by competency
and cohort, including pending evidence, insufficient samples, suppression flags,
and next actions. See `docs/learner_evidence_model.md` for the privacy-safe
evidence model.

Run the decision impact review:

```bash
python3 scripts/decision_impact_review.py
```

The decision impact review classifies approved decisions as too early, emerging,
positive, needing attention, or missing outcome data by joining implementation,
competency, learner evidence, outcome, and prediction records. See
`docs/decision_impact_model.md` for interpretation rules.

Run the real-data source contract review:

```bash
python3 scripts/source_contract_review.py
```

The source contract review shows which future source extracts are ready, blocked,
or usable only for controlled manual sampling. See `docs/source_data_contracts.md`
and `docs/real_data_readiness.md` before importing real data.
