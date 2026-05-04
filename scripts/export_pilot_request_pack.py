#!/usr/bin/env python3
"""Export an owner-ready v0.2 pilot data request pack."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "outputs"
OUTPUT_PATH = OUTPUT_DIR / "pilot_request_pack.md"
sys.path.insert(0, str(ROOT))

from decision_spine.services.pilot_request_pack import build_pilot_request_pack, render_pilot_request_pack_markdown


def main() -> int:
    OUTPUT_DIR.mkdir(exist_ok=True)
    OUTPUT_PATH.write_text(render_pilot_request_pack_markdown(build_pilot_request_pack()), encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
