#!/usr/bin/env python3
"""Run the project validation, tests, and compile checks."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PYCACHE_PREFIX = "/private/tmp/ca_test_pycache"


def run_step(label: str, command: list[str], *, env: dict[str, str] | None = None) -> int:
    print(f"\n{label}")
    print("-" * len(label))
    print(" ".join(command))
    completed = subprocess.run(command, cwd=ROOT, env=env, check=False)
    return completed.returncode


def main() -> int:
    python = sys.executable
    steps = [
        ("Validate data", [python, "scripts/validate_data.py"], None),
        ("Validate pilot templates", [python, "scripts/validate_pilot_extract.py", "data/pilot_extract_templates"], None),
        ("Run tests", [python, "-m", "unittest", "discover", "-s", "tests"], None),
        (
            "Compile scripts and tests",
            [
                python,
                "-m",
                "py_compile",
                *sorted(map(str, ROOT.glob("decision_spine/**/*.py"))),
                *sorted(map(str, ROOT.glob("scripts/*.py"))),
                *sorted(map(str, ROOT.glob("tests/*.py"))),
            ],
            {**os.environ, "PYTHONPYCACHEPREFIX": PYCACHE_PREFIX},
        ),
    ]

    for label, command, env in steps:
        returncode = run_step(label, command, env=env)
        if returncode:
            print(f"\nCheck failed: {label}", file=sys.stderr)
            return returncode

    print("\nAll checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
