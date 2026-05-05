#!/usr/bin/env python3
"""Print role, competency, evidence, and outcome normalization crosswalk."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from decision_spine.services.normalization_crosswalk import (  # noqa: E402
    build_normalization_crosswalk,
    render_normalization_crosswalk_text,
)


def main() -> None:
    print(render_normalization_crosswalk_text(build_normalization_crosswalk()), end="")


if __name__ == "__main__":
    main()
