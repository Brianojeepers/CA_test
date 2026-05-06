#!/usr/bin/env python3
"""Review stakeholder communication gates from council outcomes."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from decision_spine.services.stakeholder_gates import (  # noqa: E402
    build_stakeholder_gate_review,
    render_stakeholder_gate_text,
)


def main() -> None:
    print(render_stakeholder_gate_text(build_stakeholder_gate_review()), end="")


if __name__ == "__main__":
    main()
