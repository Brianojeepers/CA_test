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
    "copy-stakeholder-brief",
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
    "review-diff-summary",
    "review-diff-counts",
    "review-diff-list",
    "schema-gap-summary",
    "schema-gap-list",
    "schema-gap-blockers",
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
    "recommendation-panel",
    "decision-detail",
    "changelog-title",
    "changelog-basis",
    "changelog-filter",
    "changelog-list",
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
    "render/changelog.js",
    "render/detail.js",
    "render/drilldowns.js",
    "render/filters.js",
    "render/impact.js",
    "render/insights.js",
    "render/meetingNotes.js",
    "render/recommendation.js",
    "render/reviewDiff.js",
    "render/schemaGap.js",
    "render/stakeholderBrief.js",
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
    for endpoint in ("/monthly-packet", "/schema-gap", "/decisions/"):
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


def check_recommendation_contract(errors: list[str]) -> None:
    app_js = (WEB_DIR / "app.js").read_text(encoding="utf-8")
    recommendation_js = (WEB_DIR / "render" / "recommendation.js").read_text(encoding="utf-8")
    styles_css = (WEB_DIR / "styles.css").read_text(encoding="utf-8")

    for token in ("renderRecommendation",):
        if token not in app_js:
            errors.append(f"web/app.js is missing recommendation panel token: {token}")

    for token in ("recommendation-panel", "Keep / Amplify", "Update / Monitor", "Wait", "Update / Consider Deprecation"):
        if token not in recommendation_js:
            errors.append(f"web/render/recommendation.js is missing decision action token: {token}")

    for token in (".decision-recommendation", ".recommendation-verdict", ".recommendation-reasons"):
        if token not in styles_css:
            errors.append(f"web/styles.css is missing recommendation style: {token}")


def check_changelog_contract(errors: list[str]) -> None:
    app_js = (WEB_DIR / "app.js").read_text(encoding="utf-8")
    changelog_js = (WEB_DIR / "render" / "changelog.js").read_text(encoding="utf-8")
    styles_css = (WEB_DIR / "styles.css").read_text(encoding="utf-8")

    for token in ("renderChangelog", "activeChangelogCategory"):
        if token not in app_js:
            errors.append(f"web/app.js is missing changelog token: {token}")

    for token in ("data-changelog-category", "data-changelog-decision-id", "changelog-list"):
        if token not in changelog_js:
            errors.append(f"web/render/changelog.js is missing changelog token: {token}")

    for token in (".changelog-panel", ".changelog-list", ".changelog-item"):
        if token not in styles_css:
            errors.append(f"web/styles.css is missing changelog style: {token}")


def check_stakeholder_brief_contract(errors: list[str]) -> None:
    app_js = (WEB_DIR / "app.js").read_text(encoding="utf-8")
    brief_js = (WEB_DIR / "render" / "stakeholderBrief.js").read_text(encoding="utf-8")

    for token in ("copy-stakeholder-brief", "buildStakeholderBrief"):
        if token not in app_js:
            errors.append(f"web/app.js is missing stakeholder brief token: {token}")

    for token in ("Primary question", "Key Decisions", "Action Items", "What Changed"):
        if token not in brief_js:
            errors.append(f"web/render/stakeholderBrief.js is missing brief token: {token}")


def check_review_diff_contract(errors: list[str]) -> None:
    app_js = (WEB_DIR / "app.js").read_text(encoding="utf-8")
    review_diff_js = (WEB_DIR / "render" / "reviewDiff.js").read_text(encoding="utf-8")
    styles_css = (WEB_DIR / "styles.css").read_text(encoding="utf-8")

    for token in ("renderReviewDiff", "review_diff"):
        if token not in app_js:
            errors.append(f"web/app.js is missing review diff token: {token}")

    for token in ("review-diff-summary", "data-review-diff-decision-id", "save_review_snapshot.py"):
        if token not in review_diff_js:
            errors.append(f"web/render/reviewDiff.js is missing review diff token: {token}")

    for token in (".review-diff-panel", ".review-diff-list", ".review-diff-item"):
        if token not in styles_css:
            errors.append(f"web/styles.css is missing review diff style: {token}")


def check_schema_gap_contract(errors: list[str]) -> None:
    app_js = (WEB_DIR / "app.js").read_text(encoding="utf-8")
    schema_gap_js = (WEB_DIR / "render" / "schemaGap.js").read_text(encoding="utf-8")
    styles_css = (WEB_DIR / "styles.css").read_text(encoding="utf-8")

    for token in ("fetchSchemaGap", "renderSchemaGap", "schemaGap"):
        if token not in app_js:
            errors.append(f"web/app.js is missing schema gap token: {token}")

    for token in ("schema-gap-summary", "v02_requirements", "privacy_sensitivity", "decision_unlocked"):
        if token not in schema_gap_js:
            errors.append(f"web/render/schemaGap.js is missing schema gap token: {token}")

    for token in (".schema-gap-panel", ".schema-gap-list", ".schema-card", ".schema-blocker"):
        if token not in styles_css:
            errors.append(f"web/styles.css is missing schema gap style: {token}")


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
        check_recommendation_contract(errors)
        check_changelog_contract(errors)
        check_stakeholder_brief_contract(errors)
        check_review_diff_contract(errors)
        check_schema_gap_contract(errors)
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
