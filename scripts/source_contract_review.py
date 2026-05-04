#!/usr/bin/env python3
"""Print source-data contract readiness for the Decision Spine MVP."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
TODAY = date.today()


def load_json(filename: str) -> list[dict[str, Any]]:
    with (DATA_DIR / filename).open(encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, list):
        raise ValueError(f"{filename}: expected top-level JSON list")
    return data


def print_section(title: str) -> None:
    print(f"\n{title}")
    print("-" * len(title))


def readiness_sort_key(contract: dict[str, Any]) -> tuple[int, str]:
    order = {"red": 0, "amber": 1, "green": 2}
    return (order.get(contract["readiness"], 9), contract["contract_id"])


def validate_contracts(contracts: list[dict[str, Any]]) -> list[str]:
    required = {
        "contract_id",
        "data_domain",
        "candidate_source",
        "source_owner",
        "privacy_owner",
        "feeds_files",
        "minimum_grain",
        "required_fields",
        "privacy_posture",
        "freshness_sla",
        "pilot_status",
        "readiness",
        "blockers",
        "next_action",
    }
    errors: list[str] = []
    seen: set[str] = set()
    for contract in contracts:
        contract_id = str(contract.get("contract_id", "<unknown>"))
        missing = sorted(required - set(contract))
        for field_name in missing:
            errors.append(f"{contract_id}: missing {field_name}")
        if contract_id in seen:
            errors.append(f"{contract_id}: duplicate contract_id")
        seen.add(contract_id)
        if contract.get("readiness") not in {"green", "amber", "red"}:
            errors.append(f"{contract_id}: readiness must be green, amber, or red")
        for field_name in ("feeds_files", "required_fields", "blockers"):
            if field_name in contract and not isinstance(contract[field_name], list):
                errors.append(f"{contract_id}: {field_name} must be a list")
    return errors


def report_readiness(contracts: list[dict[str, Any]]) -> None:
    print_section("Readiness Summary")
    counts = Counter(contract["readiness"] for contract in contracts)
    print(f"- green={counts['green']} amber={counts['amber']} red={counts['red']}")
    print("- red sources must not be imported as real data")
    print("- amber sources can be sampled manually but should not be treated as trusted")


def report_contracts(contracts: list[dict[str, Any]]) -> None:
    print_section("Source Contracts")
    for contract in sorted(contracts, key=readiness_sort_key):
        feeds = ", ".join(contract["feeds_files"])
        fields = ", ".join(contract["required_fields"])
        print(
            f"- {contract['contract_id']} {contract['data_domain']} "
            f"[{contract['readiness']}, {contract['pilot_status']}]"
        )
        print(f"  owner={contract['source_owner']} | privacy={contract['privacy_owner']}")
        print(f"  feeds={feeds}")
        print(f"  grain={contract['minimum_grain']}")
        print(f"  freshness={contract['freshness_sla']}")
        print(f"  required_fields={fields}")
        if contract["blockers"]:
            print("  blockers=" + "; ".join(contract["blockers"]))
        else:
            print("  blockers=none")
        print(f"  next_action={contract['next_action']}")


def report_file_coverage(contracts: list[dict[str, Any]]) -> None:
    print_section("MVP File Coverage")
    by_file: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for contract in contracts:
        for filename in contract["feeds_files"]:
            by_file[filename].append(contract)

    expected = [
        "signals.json",
        "decisions.json",
        "releases.json",
        "cohort_outcomes.json",
        "predictions.json",
        "pedagogy_map.json",
        "role_competencies.json",
    ]
    for filename in expected:
        linked = by_file.get(filename, [])
        if not linked:
            print(f"- {filename}: no source contract")
            continue
        readiness = Counter(contract["readiness"] for contract in linked)
        owners = ", ".join(sorted({contract["source_owner"] for contract in linked}))
        print(
            f"- {filename}: contracts={len(linked)} "
            f"green={readiness['green']} amber={readiness['amber']} red={readiness['red']} "
            f"owners={owners}"
        )


def report_pilot_gate(contracts: list[dict[str, Any]]) -> None:
    print_section("Pilot Gate")
    red = [contract for contract in contracts if contract["readiness"] == "red"]
    if red:
        print("- not ready for full real-data pilot")
        for contract in red:
            print(f"- clear {contract['contract_id']} {contract['data_domain']}: {contract['next_action']}")
        return
    amber = [contract for contract in contracts if contract["readiness"] == "amber"]
    if amber:
        print("- ready only for controlled manual sampling")
        for contract in amber:
            print(f"- confirm {contract['contract_id']} {contract['data_domain']}: {contract['next_action']}")
        return
    print("- ready for a small privacy-reviewed pilot extract")


def main() -> None:
    contracts = load_json("source_contracts.json")
    errors = validate_contracts(contracts)
    if errors:
        print("Source contract validation failed:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print("Decision Spine Source Contract Review")
    print(f"Generated: {TODAY.isoformat()}")
    print("Reference: docs/source_data_contracts.md")
    report_readiness(contracts)
    report_contracts(contracts)
    report_file_coverage(contracts)
    report_pilot_gate(contracts)


if __name__ == "__main__":
    main()
