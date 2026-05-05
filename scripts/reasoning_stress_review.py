#!/usr/bin/env python3
"""Print cross-layer reasoning stress tests."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from decision_spine.services.reasoning_stress import (  # noqa: E402
    build_reasoning_stress_review,
    render_reasoning_stress_text,
)


def main() -> None:
    print(render_reasoning_stress_text(build_reasoning_stress_review()), end="")


if __name__ == "__main__":
    main()
