#!/usr/bin/env python3
"""Print the directional v0.2 intelligence preview."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from decision_spine.services.v02_intelligence import build_v02_intelligence_preview, render_v02_intelligence_preview_text


def main() -> int:
    print(render_v02_intelligence_preview_text(build_v02_intelligence_preview()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
