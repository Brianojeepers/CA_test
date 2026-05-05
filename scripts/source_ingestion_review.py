#!/usr/bin/env python3
"""Print source ingestion envelope and freshness readiness."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from decision_spine.services.source_ingestion import (  # noqa: E402
    build_source_ingestion_review,
    render_source_ingestion_review_text,
)


def main() -> None:
    print(render_source_ingestion_review_text(build_source_ingestion_review()), end="")


if __name__ == "__main__":
    main()
