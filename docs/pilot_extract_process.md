# Pilot Extract Process

## Purpose

Pilot extracts let source owners test real-data shape before anything is merged
into the Decision Spine seed data.

The process is intentionally dry-run only. It checks field shape and obvious
privacy risks, then reports whether source contracts currently allow import.

## Directory Rules

Tracked templates live in:

```text
data/pilot_extract_templates/
```

Local pilot extracts should live in:

```text
data/pilot_extracts/
```

`data/pilot_extracts/` is ignored by git except `.gitkeep`. Do not commit real
pilot data.

## Templates

Current templates:

- `signals_template.json`
- `decisions_template.json`
- `releases_template.json`
- `cohort_outcomes_template.json`
- `learner_evidence_template.json`
- `predictions_template.json`

Each template is a top-level JSON list containing example aggregate or summarized
records.

## Dry-Run Validation

Validate templates:

```bash
python3 scripts/validate_pilot_extract.py data/pilot_extract_templates
```

Validate a local pilot extract directory:

```bash
python3 scripts/validate_pilot_extract.py data/pilot_extracts
```

The validator checks:

- known pilot file names,
- top-level JSON lists,
- required fields from `data/source_contracts.json`,
- simple privacy-risk field names and text patterns,
- source contract readiness.

## Import Gate

A passing dry-run does not mean data can be imported.

Real import remains blocked when the source contract is red. Amber contracts can
support controlled manual sampling only. Green contracts can support a
privacy-reviewed pilot extract.

Before import:

1. Confirm source owner.
2. Confirm privacy owner.
3. Confirm suppression rules.
4. Remove direct client, talent, and account identifiers.
5. Run dry-run validation.
6. Run `python3 scripts/source_contract_review.py`.
7. Get explicit council approval for the pilot extract.
