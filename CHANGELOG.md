# Changelog

## 0.1.1 - 2026-05-04

Added:

- Pilot extract templates for signals, decisions, releases, cohort outcomes,
  learner evidence, and predictions.
- Dry-run pilot extract validator via `scripts/validate_pilot_extract.py`.
- Ignored local pilot extract directory at `data/pilot_extracts/`.
- Pilot-template validation in `scripts/run_checks.py`.

## 0.1.0 - 2026-05-04

Baseline local MVP contract.

Implemented:

- Full coverage of the 17 original user stories in `docs/user_stories.md`.
- Synthetic seed data for signals, decisions, releases, outcomes, predictions,
  competencies, learner evidence, pedagogy, and source contracts.
- Validation-first data quality gate via `scripts/validate_data.py`.
- Full local check runner via `scripts/run_checks.py`.
- Council, KPI, signal, changelog, outcome, decision impact, and stakeholder
  review scripts.
- Training offer, talent profile, and delivery-window stakeholder views.
- Reasoning gates for decision impact, training offer readiness, profile
  guidance, and delivery timing.
- Regression tests for validation warnings and reasoning gates.
- Markdown monthly packet export via `scripts/export_monthly_packet.py`.
- Executable MVP specification in `SPEC.md`.

Known limitations:

- All data is synthetic.
- Real learner and cohort outcome extracts remain blocked by privacy/source
  contract requirements.
- Actual cohort calendar detail is unavailable.
- Placement, retention, and learner evidence are directional until sample sizes
  and evidence windows mature.
- Outputs are local CLI/Markdown artifacts, not a dashboard or service.
