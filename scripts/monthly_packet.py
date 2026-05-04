#!/usr/bin/env python3
"""Print a concise monthly Decision Spine council packet with drill-down paths."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from decision_spine.services.monthly_packet import build_monthly_packet, render_monthly_packet_text


def main() -> None:
    print(render_monthly_packet_text(build_monthly_packet()))


if __name__ == "__main__":
    main()
