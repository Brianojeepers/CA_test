#!/usr/bin/env python3
"""Print the current council review workflow and recorded outcomes."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from decision_spine.services.review_workflow import build_review_workflow, render_review_workflow_text


def main() -> int:
    print(render_review_workflow_text(build_review_workflow()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
