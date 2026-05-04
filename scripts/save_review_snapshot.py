#!/usr/bin/env python3
"""Save the current monthly packet as a review snapshot."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from decision_spine.services.monthly_packet import build_monthly_packet
from decision_spine.services.review_snapshots import save_review_snapshot


def main() -> int:
    output_path = save_review_snapshot(build_monthly_packet())
    print(f"Wrote {output_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
