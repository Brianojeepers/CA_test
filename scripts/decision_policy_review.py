#!/usr/bin/env python3
"""Review safe operating policy for current decisions."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from decision_spine.services.decision_policy import build_decision_policy_review, render_decision_policy_text


def main() -> int:
    print(render_decision_policy_text(build_decision_policy_review()), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
