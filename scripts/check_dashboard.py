#!/usr/bin/env python3
"""Smoke-test the local dashboard/API contract.

This check expects the local services to be running:
- static dashboard: http://127.0.0.1:3000
- FastAPI API: http://127.0.0.1:8000
"""

from __future__ import annotations

import json
import sys
from html.parser import HTMLParser
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen


DASHBOARD_BASE_URL = "http://127.0.0.1:3000/"
API_BASE_URL = "http://127.0.0.1:8000/api"

EXPECTED_DASHBOARD_TEXT = [
    "Monthly Council Dashboard",
    "Copy brief",
    "Stakeholder lens",
    "Stakeholder insights",
    "Since last snapshot",
    "Decision impact",
    "Action queue",
    "Recommended action",
    "Selected decision",
    "What changed since last review",
    "Council notes",
]


class ScriptParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.module_scripts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {name: value for name, value in attrs}
        if tag == "script" and attr_map.get("type") == "module" and attr_map.get("src"):
            self.module_scripts.append(attr_map["src"] or "")


def fetch_text(url: str, *, origin: str | None = None) -> str:
    headers = {"User-Agent": "decision-spine-dashboard-check/1.0"}
    if origin:
        headers["Origin"] = origin
    request = Request(url, headers=headers)
    try:
        with urlopen(request, timeout=5) as response:
            return response.read().decode("utf-8")
    except HTTPError as exc:
        raise RuntimeError(f"{url} returned HTTP {exc.code}") from exc
    except URLError as exc:
        raise RuntimeError(f"{url} is not reachable: {exc.reason}") from exc
    except TimeoutError as exc:
        raise RuntimeError(f"{url} timed out") from exc


def fetch_json(url: str, *, origin: str | None = None) -> dict[str, Any]:
    try:
        return json.loads(fetch_text(url, origin=origin))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{url} did not return valid JSON") from exc


def check_dashboard_shell(errors: list[str]) -> list[str]:
    try:
        html = fetch_text(DASHBOARD_BASE_URL)
    except RuntimeError as exc:
        errors.append(str(exc))
        return []

    for expected_text in EXPECTED_DASHBOARD_TEXT:
        if expected_text not in html:
            errors.append(f"dashboard shell missing expected text: {expected_text}")

    parser = ScriptParser()
    parser.feed(html)
    if "./app.js" not in parser.module_scripts:
        errors.append("dashboard shell does not load ./app.js as a module")
    return parser.module_scripts


def check_static_modules(module_scripts: list[str], errors: list[str]) -> None:
    urls = [urljoin(DASHBOARD_BASE_URL, src) for src in module_scripts]
    urls.extend(
        urljoin(DASHBOARD_BASE_URL, path)
        for path in [
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
            "render/stakeholderBrief.js",
            "render/summary.js",
            "render/table.js",
            "render/views.js",
            "render/warnings.js",
            "styles.css",
        ]
    )

    for url in sorted(set(urls)):
        try:
            fetch_text(url)
        except RuntimeError as exc:
            errors.append(str(exc))


def check_api(errors: list[str]) -> None:
    try:
        health = fetch_json(f"{API_BASE_URL}/health", origin=DASHBOARD_BASE_URL.rstrip("/"))
    except RuntimeError as exc:
        errors.append(str(exc))
        return

    if health.get("status") != "ok":
        errors.append("API health endpoint did not return status=ok")

    try:
        packet = fetch_json(f"{API_BASE_URL}/monthly-packet", origin=DASHBOARD_BASE_URL.rstrip("/"))
    except RuntimeError as exc:
        errors.append(str(exc))
        return

    rows = packet.get("decision_impact", {}).get("rows", [])
    actions = packet.get("actions", [])
    changelog_items = packet.get("decision_changelog", {}).get("items", [])
    review_diff = packet.get("review_diff", {})
    if not rows:
        errors.append("monthly packet returned no decision impact rows")
        return
    if not actions:
        errors.append("monthly packet returned no action items")
    if not changelog_items:
        errors.append("monthly packet returned no decision changelog items")
    if not review_diff.get("snapshot_status"):
        errors.append("monthly packet returned no review diff status")

    first_decision_id = rows[0].get("decision_id")
    if not first_decision_id:
        errors.append("first decision impact row is missing decision_id")
        return

    try:
        detail = fetch_json(f"{API_BASE_URL}/decisions/{first_decision_id}", origin=DASHBOARD_BASE_URL.rstrip("/"))
    except RuntimeError as exc:
        errors.append(str(exc))
        return

    if detail.get("decision", {}).get("decision_id") != first_decision_id:
        errors.append(f"decision detail endpoint did not return requested decision: {first_decision_id}")
    if "traceability" not in detail:
        errors.append(f"decision detail endpoint returned no traceability block: {first_decision_id}")


def main() -> int:
    errors: list[str] = []
    module_scripts = check_dashboard_shell(errors)
    check_static_modules(module_scripts, errors)
    check_api(errors)

    if errors:
        print("Dashboard smoke check failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("Dashboard smoke check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
