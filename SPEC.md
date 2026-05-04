# Decision Spine MVP Specification

MVP spec version: `0.2.0`

## 1. Purpose

The Decision Spine MVP is a local, file-based operating system for translating
market evidence into academy decisions, releases, competency targets, learner
evidence reviews, outcome reviews, prediction learning, and the first data
readiness map for a broader intelligence engine.

It exists to prove the operating loop and identify the exact schema gaps before
introducing live ingestion, learner-level data, production dashboards, deployed
APIs, scheduled workflows, or real source-system imports.

## 2. Scope

In scope:

- Synthetic seed data in `data/`.
- Read-only review scripts in `scripts/`.
- Markdown operating documentation in `docs/`.
- Regression tests in `tests/`.
- Markdown packet export to `outputs/monthly_packet.md`.
- Reusable Python service functions under `decision_spine/` for future API and UI use.
- FastAPI boundary under `app/api/` for structured JSON access to service-layer data.
- Static first-pass dashboard prototype under `web/` for stakeholder workflow discovery.
- Pilot extract templates and dry-run validation.
- Schema gap review across seed data, pilot templates, source contracts, and v0.2 intelligence requirements.
- Full coverage of the 17 original user stories in `docs/user_stories.md`.

Out of scope:

- Real Andela operating data.
- Learner-level records.
- CRM/account-level commercial data.
- Live job-market ingestion.
- Production dashboard UI beyond the local static prototype.
- API/service deployment.
- Automated writes to downstream systems.
- Database schema migration or warehouse models.
- Role-demand, competency-gap, horizon-radar, or simulator outputs based on real data.

## 3. Core Operating Loop

The MVP loop is:

```text
signals -> decisions -> releases -> competencies -> learner evidence -> outcomes -> prediction learning
```

Every market-backed curriculum, credential, assessment, positioning, or profile
claim must remain traceable to source signals and decision records.

## 4. Data Contracts

Primary seed files:

| File | Contract |
| --- | --- |
| `data/signals.json` | Market, client, and learner signals. |
| `data/decisions.json` | Council or owner decisions linked to signals. |
| `data/releases.json` | Curriculum, credential, assessment, and positioning changes linked to decisions. |
| `data/cohort_outcomes.json` | Aggregated cohort outcomes for placement and retention review. |
| `data/predictions.json` | Falsifiable horizon predictions and scoring records. |
| `data/role_competencies.json` | Role-archetype competency targets linked to signals, decisions, releases, and pedagogy. |
| `data/learner_evidence_summary.json` | Aggregated learner evidence by competency and cohort. |
| `data/pedagogy_map.json` | Bloom/Dreyfus/performance framing for selected decisions and releases. |
| `data/source_contracts.json` | Real-data source readiness, ownership, freshness, and privacy contracts. |
| `data/v02_intelligence_requirements.json` | Versioned field requirements for expanded role-demand, competency-gap, horizon, and impact reasoning. |

Detailed field-level contribution rules live in `data/README.md`.

Pilot extract templates live in `data/pilot_extract_templates/`. Local real-data
pilot extracts should live in ignored `data/pilot_extracts/`.

Real-data readiness and source obligations live in:

- `docs/real_data_readiness.md`
- `docs/pilot_extract_process.md`
- `docs/source_data_contracts.md`
- `docs/v02_pilot_schema.md`
- `data/source_contracts.json`
- `data/v02_intelligence_requirements.json`

## 5. Validation Rules

`scripts/validate_data.py` is the authoritative MVP validator.

It must:

- validate required fields,
- validate date formats,
- validate enum-like status fields,
- validate numeric ranges,
- validate cross-file join keys,
- fail unknown released cohort IDs,
- warn, not fail, when pending releases reference future cohorts,
- identify active competencies without evidence,
- identify green signals without competency mapping,
- validate optional structured files when present.

Current expected warning:

```text
releases.json:REL-2026-003:cohort_id: future cohort / no outcomes yet: 'COH-2026-06-SCALER'
```

## 6. Command Surface

Quality gate:

```bash
python3 scripts/run_checks.py
```

Core operating scripts:

| Script | Requirement |
| --- | --- |
| `scripts/report_kpis.py` | Print K1-K7 KPI posture from seed data. |
| `scripts/council_review.py` | Print council decision, release, traceability, and prediction queues. |
| `scripts/signal_review.py` | Classify signals as act, tracked, monitor, or do not act. |
| `scripts/monthly_packet.py` | Print concise monthly packet with drill-down commands. |
| `scripts/export_monthly_packet.py` | Write `outputs/monthly_packet.md`. |
| `scripts/export_stakeholder_packets.py` | Write concise stakeholder briefs under `outputs/stakeholder_packets/`. |
| `scripts/save_review_snapshot.py` | Save the current structured packet under `outputs/review_snapshots/` for future review diffing. |
| `scripts/decision_impact_review.py` | Classify approved decisions by impact maturity. |
| `scripts/source_contract_review.py` | Gate real-data imports by source readiness and privacy posture. |
| `scripts/validate_pilot_extract.py` | Dry-run pilot extract shape and privacy-risk checks. |
| `scripts/schema_gap_review.py` | Compare current seed schema, pilot templates, source contracts, and v0.2 intelligence requirements. |

Reusable service layer:

| Service | Requirement |
| --- | --- |
| `decision_spine.services.monthly_packet.build_monthly_packet` | Return structured monthly-packet data for CLI, Markdown export, API, and future frontend consumption. |
| `decision_spine.services.monthly_packet.render_monthly_packet_markdown` | Render the structured monthly packet to `outputs/monthly_packet.md` without duplicating calculation logic. |
| `decision_spine.services.review_snapshots.build_review_diff` | Compare current packet state to a saved review snapshot. |
| `decision_spine.services.review_snapshots.save_review_snapshot` | Persist the current packet as an ignored JSON review snapshot. |
| `decision_spine.services.stakeholder_packets.build_stakeholder_packet` | Return a concise stakeholder-specific brief from the same monthly-packet data. |
| `decision_spine.services.stakeholder_packets.render_stakeholder_packet_markdown` | Render stakeholder briefs for Markdown export without recalculating packet data. |
| `decision_spine.services.schema_gap.build_schema_gap_report` | Return structured schema coverage and v0.2 field-gap data. |
| `decision_spine.services.schema_gap.render_schema_gap_report_text` | Render schema gap review output for CLI use. |

API surface:

| Endpoint | Requirement |
| --- | --- |
| `GET /api/health` | Return API health as `{ "status": "ok" }`. |
| `GET /api/monthly-packet` | Return the structured monthly packet from `build_monthly_packet()`. |
| `GET /api/schema-gap` | Return seed, pilot-template, source-contract, and v0.2 intelligence field readiness. |
| `GET /api/decisions/{decision_id}` | Return a joined traceability detail across signals, releases, competencies, evidence, outcomes, predictions, and pedagogy. |

Frontend prototype:

| Surface | Requirement |
| --- | --- |
| `web/index.html` | Render the monthly-packet API as a stakeholder dashboard with summary metrics, actions, review snapshot diffs, decision impact, changelog review, copyable briefs, drill-downs, and known limits. |
| `web/app.js` | Coordinate dashboard state, filtering, decision selection, and council meeting controls. |
| `web/api.js` | Fetch `GET /api/monthly-packet` and `GET /api/decisions/{decision_id}`. |
| `web/stakeholders.js` | Define stakeholder-specific dashboard lenses and row/action filtering. |
| `web/render/*.js` | Render stakeholder insight cards, trust/source badges, selected-decision recommendations, review snapshot diffs, changelog filters, summary metrics, filters, action queues, decision detail, drill-downs, warnings, meeting notes, and impact tables. |
| `scripts/check_frontend.py` | Validate dashboard DOM contracts, module wiring, API references, and JavaScript syntax. |
| `scripts/check_dashboard.py` | Smoke-test the live local dashboard/API contract when both local servers are running. |

Stakeholder scripts:

| Script | Stakeholder |
| --- | --- |
| `scripts/credential_requirements.py` | Assessment Ops. |
| `scripts/learning_outcomes.py` | Developer Learning. |
| `scripts/outcome_review.py` | Matching and CSM. |
| `scripts/client_positioning.py` | Solutions and Sales. |
| `scripts/training_offer_inputs.py` | Training as a Service. |
| `scripts/talent_profile_signals.py` | Talent Experience. |
| `scripts/delivery_window_review.py` | Delivery. |
| `scripts/decision_changelog.py` | Executive stakeholders. |
| `scripts/competency_gap_review.py` | Learning, Assessment Ops, Matching, and Solutions. |
| `scripts/proficiency_readiness_review.py` | Assessment Ops and Data/Analytics. |
| `scripts/pedagogy_review.py` | Learning and Assessment design. |

## 7. Reasoning Gates

Decision impact:

- `positive_signal` requires released implementation, non-suppressed positive readiness evidence, positive outcome direction, and no pending placement or retention outcome.
- `evidence_emerging` means readiness or outcome evidence is promising but incomplete.
- `too_early` means release or evidence windows are not mature.
- `needs_attention` covers insufficient sample, not-ready evidence, or negative outcome direction.
- `no_outcome_data` means traceability exists but evidence is missing.

Training offer inputs:

- `ready_for_offer_design` requires a green signal, released internal artifact, and non-suppressed ready or emerging learner evidence.
- Released artifacts with pending/suppressed evidence must remain `validated_but_readiness_pending`.

Talent profile signals:

- `active_profile_guidance` requires a green signal, released artifact, and non-suppressed ready or emerging learner evidence.
- Released artifacts with pending/suppressed evidence must remain `released_but_evidence_pending`.

Delivery windows:

- Pending release with unknown cohort is `future_cohort`.
- Released item after cohort start but before credential issue is `in_cohort_timing_review`.
- Released item after credential issue is `late_for_credential_window`.
- Released item with unknown cohort is a data quality issue.

## 8. Outputs

Generated outputs go under `outputs/`.

Tracked:

- `outputs/.gitkeep`

Ignored:

- `outputs/monthly_packet.md`
- any other generated output files under `outputs/`

Generate the monthly packet with:

```bash
python3 scripts/export_monthly_packet.py
```

## 9. Acceptance Criteria

The MVP is in a valid local state when:

- `python3 scripts/run_checks.py` passes.
- `scripts/validate_data.py` has no errors.
- Only known intentional validation warnings remain.
- The original 17 user stories have script or documentation coverage.
- Real-data import remains blocked unless source contracts are green or explicitly pilot-approved.
- Pilot extracts pass `scripts/validate_pilot_extract.py` before review.
- Schema gap review makes source-template, seed-contract, and v0.2 intelligence field gaps explicit before broader product expansion.
- Generated outputs are ignored by git.
- Monthly packet data is available as structured Python dictionaries before rendering to Markdown or UI.
- The API exposes health and monthly-packet endpoints backed by the same Python service layer as the CLI.
- Decision detail is available through the API as a joined traceability object.
- Schema gap readiness is available through the API for frontend v0.2 planning views.
- The first frontend prototype renders the monthly packet without exposing raw JSON to stakeholders.
- The dashboard supports an action-focused council meeting mode with copyable meeting notes.
- The dashboard supports stakeholder-specific views without duplicating the underlying packet data.
- The dashboard shows clickable role-specific insight cards with trust/source badges before the audit table.
- The dashboard translates each selected decision into a stakeholder action: keep/amplify, update/monitor, wait, or corrective review.
- The dashboard shows a filtered "what changed and why" changelog backed by structured monthly-packet data.
- The dashboard shows what changed since the latest saved review snapshot when one exists.
- The dashboard shows v0.2 intelligence readiness by capability, missing field count, owner, and privacy posture.
- The dashboard can copy a concise Markdown brief for the active stakeholder lens.
- Stakeholder-specific Markdown briefs can be exported without duplicating dashboard logic.
- Frontend module wiring passes `python3 scripts/check_frontend.py`.
- With the local API and static server running, `python3 scripts/check_dashboard.py` passes.

## 10. Tests

Regression tests live in `tests/`.

They currently cover:

- validation warning behavior for future cohorts,
- decision impact maturity gates,
- stakeholder readiness gates,
- delivery-window timing classifications,
- schema gap coverage, alias handling, and v0.2 expansion requirements.

Run:

```bash
python3 -m unittest discover -s tests
```

## 11. Known Limitations

- All seed data is synthetic.
- Outcome and learner evidence samples are intentionally immature.
- Placement, retention, and readiness evidence are directional, not causal proof.
- Source contracts currently block real learner and outcome extracts pending privacy review.
- Actual cohort calendar data is unavailable.
- Client/account-level commercial evidence is unavailable.
- Training offers and talent profile signals are recommendation inputs only; they do not write to downstream systems.
- v0.2 intelligence requirements are field-readiness requirements, not implemented forecasting or simulation models.

## 12. Future Work

Next stages should focus on:

- privacy-reviewed pilot extracts,
- v0.2 pilot schema decisions for role-anchor demand, competency gaps, horizon radar, and curriculum impact simulation,
- cohort calendar data,
- stronger learner evidence thresholds,
- dashboard interaction depth and stakeholder-specific views,
- scheduled ingestion and source freshness monitoring.
