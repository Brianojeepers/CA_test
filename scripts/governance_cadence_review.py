#!/usr/bin/env python3
"""Print manual governance cadence before automation."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from decision_spine.services.governance_cadence import (  # noqa: E402
    build_governance_cadence_review,
    render_governance_cadence_text,
)


def main() -> None:
    print(render_governance_cadence_text(build_governance_cadence_review()), end="")


if __name__ == "__main__":
    main()
