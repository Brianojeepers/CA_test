#!/usr/bin/env python3
"""Dry-run validation for pilot extract templates or local pilot extracts."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DEFAULT_EXTRACT_DIR = DATA_DIR / "pilot_extract_templates"

FILE_TO_DOMAIN = {
    "signals_template.json": "market_signals",
    "signals.json": "market_signals",
    "decisions_template.json": "decision_log",
    "decisions.json": "decision_log",
    "releases_template.json": "release_log",
    "releases.json": "release_log",
    "cohort_outcomes_template.json": "cohort_outcomes",
    "cohort_outcomes.json": "cohort_outcomes",
    "learner_evidence_template.json": "learner_evidence",
    "learner_evidence_summary.json": "learner_evidence",
    "predictions_template.json": "prediction_register",
    "predictions.json": "prediction_register",
}

SENSITIVE_FIELD_PATTERNS = (
    "email",
    "name",
    "talent_id",
    "candidate_id",
    "profile_url",
    "client_name",
    "account_name",
    "raw_text",
    "transcript",
)
SENSITIVE_VALUE_RE = re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|https?://", re.IGNORECASE)


def load_json_file(path: Path) -> Any:
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def load_contracts() -> dict[str, dict[str, Any]]:
    contracts = load_json_file(DATA_DIR / "source_contracts.json")
    return {contract["data_domain"]: contract for contract in contracts}


def iter_values(value: Any) -> list[Any]:
    if isinstance(value, dict):
        items: list[Any] = []
        for nested in value.values():
            items.extend(iter_values(nested))
        return items
    if isinstance(value, list):
        items = []
        for nested in value:
            items.extend(iter_values(nested))
        return items
    return [value]


def validate_file(path: Path, contracts_by_domain: dict[str, dict[str, Any]]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    domain = FILE_TO_DOMAIN.get(path.name)
    if domain is None:
        warnings.append(f"{path.name}: ignored unknown pilot extract file")
        return errors, warnings

    contract = contracts_by_domain.get(domain)
    if contract is None:
        errors.append(f"{path.name}: no source contract for domain {domain!r}")
        return errors, warnings

    try:
        data = load_json_file(path)
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{path.name}: cannot read JSON: {exc}")
        return errors, warnings

    if not isinstance(data, list):
        errors.append(f"{path.name}: expected top-level JSON list")
        return errors, warnings
    if not data:
        warnings.append(f"{path.name}: file has no records")

    required_fields = set(contract["required_fields"])
    for index, record in enumerate(data, start=1):
        if not isinstance(record, dict):
            errors.append(f"{path.name}: record {index}: expected object")
            continue
        missing = sorted(required_fields - set(record))
        for field_name in missing:
            errors.append(f"{path.name}: record {index}: missing required field {field_name!r}")
        for field_name in record:
            lowered = field_name.lower()
            if any(pattern in lowered for pattern in SENSITIVE_FIELD_PATTERNS):
                errors.append(f"{path.name}: record {index}: sensitive field name {field_name!r}")
        for value in iter_values(record):
            if isinstance(value, str) and SENSITIVE_VALUE_RE.search(value):
                errors.append(f"{path.name}: record {index}: sensitive value pattern in text")

    readiness = contract["readiness"]
    if readiness == "red":
        warnings.append(f"{path.name}: source contract {contract['contract_id']} is red; real import is blocked")
    elif readiness == "amber":
        warnings.append(
            f"{path.name}: source contract {contract['contract_id']} is amber; manual sampling only"
        )
    else:
        warnings.append(f"{path.name}: source contract {contract['contract_id']} is green")

    return errors, warnings


def main(argv: list[str]) -> int:
    extract_dir = Path(argv[1]) if len(argv) > 1 else DEFAULT_EXTRACT_DIR
    if not extract_dir.is_absolute():
        extract_dir = ROOT / extract_dir
    if not extract_dir.exists():
        print(f"Pilot extract path does not exist: {extract_dir}", file=sys.stderr)
        return 1
    if not extract_dir.is_dir():
        print(f"Pilot extract path is not a directory: {extract_dir}", file=sys.stderr)
        return 1

    contracts_by_domain = load_contracts()
    json_files = sorted(path for path in extract_dir.iterdir() if path.suffix == ".json")
    if not json_files:
        print(f"No JSON files found in {extract_dir}")
        return 1

    all_errors: list[str] = []
    all_warnings: list[str] = []
    for path in json_files:
        errors, warnings = validate_file(path, contracts_by_domain)
        all_errors.extend(errors)
        all_warnings.extend(warnings)

    print("Pilot Extract Dry-Run Validation")
    print(f"Path: {extract_dir.relative_to(ROOT)}")
    for warning in all_warnings:
        print(f"- warning: {warning}")
    for error in all_errors:
        print(f"- error: {error}")

    if all_errors:
        print(f"Validation failed ({len(all_errors)} error(s), {len(all_warnings)} warning(s)).")
        return 1
    print(f"Validation passed ({len(all_warnings)} warning(s)).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
