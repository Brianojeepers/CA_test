#!/usr/bin/env python3
"""Print seed, pilot-template, and v0.2 intelligence schema gaps."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from decision_spine.services.schema_gap import build_schema_gap_report, render_schema_gap_report_text


def main() -> None:
    print(render_schema_gap_report_text(build_schema_gap_report()))


if __name__ == "__main__":
    main()
