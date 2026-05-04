#!/usr/bin/env python3
"""Export a shareable monthly Decision Spine packet as Markdown."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "outputs"
OUTPUT_PATH = OUTPUT_DIR / "monthly_packet.md"
sys.path.insert(0, str(ROOT))

from decision_spine.services.monthly_packet import build_monthly_packet, render_monthly_packet_markdown


def main() -> int:
    OUTPUT_DIR.mkdir(exist_ok=True)
    packet = render_monthly_packet_markdown(build_monthly_packet())
    OUTPUT_PATH.write_text(packet, encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
