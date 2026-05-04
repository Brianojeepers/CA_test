#!/usr/bin/env python3
"""Validate the static dashboard wiring without requiring a browser."""

from __future__ import annotations

import shutil
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WEB_DIR = ROOT / "web"

REQUIRED_IDS = {
    "generated-date",
    "refresh-button",
    "status-banner",
    "stakeholder-views",
    "view-title",
    "view-description",
    "view-primary-question",
    "view-focus-list",
    "view-scope-count",
    "view-action-count",
    "stakeholder-insights",
    "data-trust",
    "data-warning",
    "signal-average",
    "signal-mix",
    "prediction-accuracy",
    "prediction-scored",
    "action-count",
    "action-caption",
    "impact-filter",
    "decision-heading",
    "decision-question",
    "decision-search",
    "owner-filter",
    "action-mode-button",
    "copy-meeting-notes",
    "impact-bars",
    "decision-table",
    "action-heading",
    "action-list",
    "decision-detail",
    "warning-list",
    "meeting-notes",
    "drilldowns",
    "known-limits",
}

REQUIRED_FILES = [
    "index.html",
    "styles.css",
    "app.js",
    "api.js",
    "format.js",
    "stakeholders.js",
    "render/actions.js",
    "render/detail.js",
    "render/drilldowns.js",
    "render/filters.js",
    "render/impact.js",
    "render/insights.js",
    "render/meetingNotes.js",
    "render/summary.js",
    "render/table.js",
    "render/views.js",
    "render/warnings.js",
]


class DashboardHtmlParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.module_scripts: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {name: value for name, value in attrs}
        element_id = attr_map.get("id")
        if element_id:
            self.ids.add(element_id)
        if tag == "script" and attr_map.get("type") == "module":
            src = attr_map.get("src")
            if src:
                self.module_scripts.add(src)


def check_required_files(errors: list[str]) -> None:
    for relative_path in REQUIRED_FILES:
        path = WEB_DIR / relative_path
        if not path.exists():
            errors.append(f"missing frontend file: web/{relative_path}")


def check_html_contract(errors: list[str]) -> None:
    parser = DashboardHtmlParser()
    parser.feed((WEB_DIR / "index.html").read_text(encoding="utf-8"))

    missing_ids = sorted(REQUIRED_IDS - parser.ids)
    for element_id in missing_ids:
        errors.append(f"missing dashboard element id: {element_id}")

    if "./app.js" not in parser.module_scripts:
        errors.append("web/index.html must load ./app.js as a module script")


def check_api_contract(errors: list[str]) -> None:
    api_js = (WEB_DIR / "api.js").read_text(encoding="utf-8")
    for endpoint in ("/monthly-packet", "/decisions/"):
        if endpoint not in api_js:
            errors.append(f"web/api.js is missing API endpoint reference: {endpoint}")


def check_insight_trust_contract(errors: list[str]) -> None:
    insights_js = (WEB_DIR / "render" / "insights.js").read_text(encoding="utf-8")
    styles_css = (WEB_DIR / "styles.css").read_text(encoding="utf-8")

    for token in ("sourceCoverageForRows", "confidenceForRows", "maturityForRows", "trust-badges"):
        if token not in insights_js:
            errors.append(f"web/render/insights.js is missing insight trust token: {token}")

    for token in (".trust-badges", ".trust-badge"):
        if token not in styles_css:
            errors.append(f"web/styles.css is missing insight trust style: {token}")


def check_js_syntax(errors: list[str]) -> None:
    node = shutil.which("node")
    if not node:
        errors.append("Node.js is required for frontend syntax validation")
        return

    js_files = [WEB_DIR / "app.js", WEB_DIR / "api.js", WEB_DIR / "format.js", *sorted((WEB_DIR / "render").glob("*.js"))]
    failed_files: list[str] = []
    for js_file in js_files:
        completed = subprocess.run([node, "--check", str(js_file)], cwd=ROOT, check=False)
        if completed.returncode:
            failed_files.append(f"web/{js_file.relative_to(WEB_DIR)}")

    for failed_file in failed_files:
        errors.append(f"frontend JavaScript syntax validation failed: {failed_file}")


def main() -> int:
    errors: list[str] = []
    check_required_files(errors)
    if not errors:
        check_html_contract(errors)
        check_api_contract(errors)
        check_insight_trust_contract(errors)
        check_js_syntax(errors)

    if errors:
        print("Frontend check failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("Frontend check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
