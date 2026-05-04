# Decision Spine MVP

This repository contains a local MVP for a market-intelligence-to-academy-decision
loop. It is intentionally small, file-based, and auditable.

The core loop is:

```text
signals -> decisions -> releases -> competencies -> learner evidence -> outcomes -> prediction learning
```

The goal is to test the operating model before introducing live ingestion,
learner-level data, production dashboards, or production services.

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

Check the static dashboard wiring and JavaScript syntax:

```bash
python3 scripts/check_frontend.py
```

Smoke-test the local dashboard/API contract after starting both servers:

```bash
python3 scripts/check_dashboard.py
```

Run the full local check suite:

```bash
python3 scripts/run_checks.py
```

Install API dependencies before running the FastAPI boundary:

```bash
python3 -m pip install -r requirements.txt
```

Validate pilot extract templates:

```bash
python3 scripts/validate_pilot_extract.py data/pilot_extract_templates
```

Run the core operating packet:

```bash
python3 scripts/monthly_packet.py
```

Export a shareable Markdown packet:

```bash
python3 scripts/export_monthly_packet.py
```

The generated file is written to `outputs/monthly_packet.md`. Generated files in
`outputs/` are ignored by git except `outputs/.gitkeep`.

Both monthly packet commands use
`decision_spine.services.monthly_packet.build_monthly_packet()`, which returns
structured data for future API and frontend consumption before rendering text or
Markdown.

Run the decision impact synthesis:

```bash
python3 scripts/decision_impact_review.py
```

Run the local API:

```bash
python3 -m uvicorn app.api.main:app --reload
```

The first API endpoints are:

- `GET /api/health`
- `GET /api/monthly-packet`
- `GET /api/decisions/{decision_id}`

Run the first stakeholder dashboard prototype:

```bash
python3 -m http.server 3000 --directory web
```

Open `http://127.0.0.1:3000`. The page consumes
`http://127.0.0.1:8000/api/monthly-packet`.
Use action mode and the council notes panel during monthly review.
The dashboard shell lives in `web/index.html`, API access in `web/api.js`, and
rendering modules under `web/render/`.
With both servers running, `python3 scripts/check_dashboard.py` verifies the
served dashboard assets and API contract.

## Before Committing

Run:

```bash
python3 scripts/run_checks.py
```

This includes seed-data validation, pilot-template dry-run validation, regression
tests, frontend contract checks, and compile checks.

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
| `scripts/export_monthly_packet.py` | Writes `outputs/monthly_packet.md` for sharing. |
| `scripts/decision_impact_review.py` | Decision-level impact status across releases, evidence, and outcomes. |
| `scripts/competency_gap_review.py` | Role competency coverage and gap hypotheses. |
| `scripts/proficiency_readiness_review.py` | Aggregated learner evidence by competency and cohort. |
| `scripts/source_contract_review.py` | Real-data source readiness and privacy gate. |
| `scripts/validate_pilot_extract.py` | Dry-run validator for pilot extract templates or ignored local extracts. |
| `scripts/check_frontend.py` | Static dashboard contract and JavaScript syntax check. |
| `scripts/check_dashboard.py` | Live local dashboard/API smoke check. |

More stakeholder-specific scripts are documented in `data/README.md`.

## Data Rules

The seed data is synthetic. Do not treat it as real Andela operating data.

Real data should enter only through a controlled, privacy-reviewed pilot extract.
See:

- `docs/real_data_readiness.md`
- `docs/pilot_extract_process.md`
- `docs/source_data_contracts.md`
- `data/source_contracts.json`

Current real-data blockers include learner evidence suppression rules and cohort
outcome privacy review.
