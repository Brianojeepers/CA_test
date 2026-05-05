#!/usr/bin/env python3
"""Review stakeholder journeys from evidence surface to safe action."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from decision_spine.services.stakeholder_journey import (
    build_stakeholder_journey_map,
    render_stakeholder_journey_text,
)


def main() -> int:
    print(render_stakeholder_journey_text(build_stakeholder_journey_map()), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
