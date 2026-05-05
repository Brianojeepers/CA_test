#!/usr/bin/env python3
"""Review source coverage and trust posture by stakeholder surface."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from decision_spine.services.trust_registry import build_trust_registry, render_trust_registry_text


def main() -> int:
    print(render_trust_registry_text(build_trust_registry()), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
