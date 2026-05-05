#!/usr/bin/env python3
"""Review horizontal readiness across the target intelligence architecture."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from decision_spine.services.architecture_readiness import (
    build_architecture_readiness_review,
    render_architecture_readiness_text,
)


def main() -> int:
    print(render_architecture_readiness_text(build_architecture_readiness_review()), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
