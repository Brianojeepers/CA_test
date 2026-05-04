# Decision Spine MVP

This repository contains a local MVP for a market-intelligence-to-academy-decision
loop. It is intentionally small, file-based, and auditable.

The core loop is:

```text
signals -> decisions -> releases -> competencies -> learner evidence -> outcomes -> prediction learning
```

The goal is to test the operating model before introducing live ingestion,
learner-level data, dashboards, or production services.

## Current Scope

- Seed JSON data in `data/`.
- Read-only review scripts in `scripts/`.
- Operating docs and model notes in `docs/`.
- Regression tests in `tests/`.
- Strategy context in `strategy_blueprint.md`.

The original 17 user stories in `docs/user_stories.md` now have concrete script
or documentation coverage.

## Main Commands

Validate all seed data:

```bash
python3 scripts/validate_data.py
```

Run regression tests:

```bash
python3 -m unittest discover -s tests
```

Compile scripts and tests:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/ca_test_pycache python3 -m py_compile scripts/*.py tests/*.py
```

Run the core operating packet:

```bash
python3 scripts/monthly_packet.py
```

Run the decision impact synthesis:

```bash
python3 scripts/decision_impact_review.py
```

## Before Committing

Run:

```bash
python3 scripts/validate_data.py
python3 -m unittest discover -s tests
PYTHONPYCACHEPREFIX=/private/tmp/ca_test_pycache python3 -m py_compile scripts/*.py tests/*.py
```

Expected current validation warning:

```text
releases.json:REL-2026-003:cohort_id: future cohort / no outcomes yet: 'COH-2026-06-SCALER'
```

That warning is intentional. Pending releases may reference future cohorts before
outcome data exists.

## Useful Review Scripts

| Script | Purpose |
| --- | --- |
| `scripts/report_kpis.py` | K1-K7 KPI report. |
| `scripts/council_review.py` | Council decision, release, traceability, and prediction queues. |
| `scripts/signal_review.py` | Signal triage: act, monitor, or exclude. |
| `scripts/monthly_packet.py` | Concise council packet with drill-down commands. |
| `scripts/decision_impact_review.py` | Decision-level impact status across releases, evidence, and outcomes. |
| `scripts/competency_gap_review.py` | Role competency coverage and gap hypotheses. |
| `scripts/proficiency_readiness_review.py` | Aggregated learner evidence by competency and cohort. |
| `scripts/source_contract_review.py` | Real-data source readiness and privacy gate. |

More stakeholder-specific scripts are documented in `data/README.md`.

## Data Rules

The seed data is synthetic. Do not treat it as real Andela operating data.

Real data should enter only through a controlled, privacy-reviewed pilot extract.
See:

- `docs/real_data_readiness.md`
- `docs/source_data_contracts.md`
- `data/source_contracts.json`

Current real-data blockers include learner evidence suppression rules and cohort
outcome privacy review.
