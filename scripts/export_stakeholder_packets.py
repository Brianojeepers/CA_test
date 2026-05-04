#!/usr/bin/env python3
"""Export stakeholder-specific Decision Spine briefs as Markdown."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "outputs" / "stakeholder_packets"
sys.path.insert(0, str(ROOT))

from decision_spine.services.monthly_packet import build_monthly_packet
from decision_spine.services.stakeholder_packets import (
    build_all_stakeholder_packets,
    render_stakeholder_packet_markdown,
)


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    packet = build_monthly_packet()
    for brief in build_all_stakeholder_packets(packet):
        output_path = OUTPUT_DIR / f"{brief['view_id']}.md"
        output_path.write_text(render_stakeholder_packet_markdown(brief), encoding="utf-8")
        print(f"Wrote {output_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
