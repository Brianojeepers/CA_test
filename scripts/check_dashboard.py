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
    "Workspace",
    "Stakeholder workspace",
    "Stakeholder lens",
    "Stakeholder insights",
    "Stakeholder mode",
    "Review-gated communication",
    "Share-ready language",
    "Architecture navigation",
    "Horizontal MVP surface",
    "Next horizontal slices",
    "Review workflow",
    "Council operating review",
    "Recent review outcomes",
    "v0.2 intelligence",
    "Directional preview",
    "Pilot data requests",
    "Owner-ready request pack",
    "Pilot intake readiness",
    "Schema design gate",
    "Since last snapshot",
    "v0.2 readiness",
    "Intelligence capability readiness",
    "Owner workbench",
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
            "render/architectureSurface.js",
            "render/changelog.js",
            "render/detail.js",
            "render/drilldowns.js",
            "render/filters.js",
            "render/focusStrip.js",
            "render/impact.js",
            "render/insights.js",
            "render/meetingNotes.js",
            "render/pilotIntake.js",
            "render/pilotRequests.js",
            "render/recommendation.js",
            "render/reviewDiff.js",
            "render/reviewWorkflow.js",
            "render/schemaGap.js",
            "render/stakeholderBrief.js",
            "render/stakeholderGates.js",
            "render/summary.js",
            "render/table.js",
            "render/v02Intelligence.js",
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

    try:
        schema_gap = fetch_json(f"{API_BASE_URL}/schema-gap", origin=DASHBOARD_BASE_URL.rstrip("/"))
    except RuntimeError as exc:
        errors.append(str(exc))
        return

    requirements = schema_gap.get("v02_requirements", [])
    if not requirements:
        errors.append("schema gap endpoint returned no v0.2 requirements")
    if schema_gap.get("summary", {}).get("v02_gap_count") is None:
        errors.append("schema gap endpoint returned no v0.2 gap count")
    if len(schema_gap.get("field_actions", [])) != schema_gap.get("summary", {}).get("field_action_count"):
        errors.append("schema gap endpoint field action count does not match summary")
    if not schema_gap.get("field_actions_by_owner"):
        errors.append("schema gap endpoint returned no owner workbench groups")

    try:
        v02_intelligence = fetch_json(f"{API_BASE_URL}/v02-intelligence", origin=DASHBOARD_BASE_URL.rstrip("/"))
    except RuntimeError as exc:
        errors.append(str(exc))
        return

    if v02_intelligence.get("summary", {}).get("hard_recommendations_enabled") is not False:
        errors.append("v0.2 intelligence preview must keep hard recommendations disabled")
    if len(v02_intelligence.get("sections", [])) != 4:
        errors.append("v0.2 intelligence endpoint did not return four preview sections")
    if not v02_intelligence.get("guardrails"):
        errors.append("v0.2 intelligence endpoint returned no guardrails")

    try:
        pilot_pack = fetch_json(f"{API_BASE_URL}/pilot-request-pack", origin=DASHBOARD_BASE_URL.rstrip("/"))
    except RuntimeError as exc:
        errors.append(str(exc))
        return

    if pilot_pack.get("summary", {}).get("request_count") != 18:
        errors.append("pilot request pack endpoint did not return 18 field requests")
    if pilot_pack.get("summary", {}).get("privacy_review_count") != 2:
        errors.append("pilot request pack endpoint did not return two privacy-review requests")
    if not pilot_pack.get("owner_groups"):
        errors.append("pilot request pack endpoint returned no owner groups")

    try:
        pilot_intake = fetch_json(f"{API_BASE_URL}/pilot-intake-review", origin=DASHBOARD_BASE_URL.rstrip("/"))
    except RuntimeError as exc:
        errors.append(str(exc))
        return

    if pilot_intake.get("summary", {}).get("field_count") != 18:
        errors.append("pilot intake endpoint did not review 18 field requests")
    if pilot_intake.get("summary", {}).get("accepted_count") != 5:
        errors.append("pilot intake endpoint did not return five accepted fields")
    if pilot_intake.get("summary", {}).get("privacy_blocked_count") != 2:
        errors.append("pilot intake endpoint did not return two privacy-blocked fields")
    if not pilot_intake.get("capability_groups"):
        errors.append("pilot intake endpoint returned no capability groups")

    try:
        architecture = fetch_json(f"{API_BASE_URL}/architecture-readiness", origin=DASHBOARD_BASE_URL.rstrip("/"))
    except RuntimeError as exc:
        errors.append(str(exc))
        return

    if architecture.get("summary", {}).get("database_schema_work") != "deferred":
        errors.append("architecture readiness endpoint must keep database schema work deferred")
    if architecture.get("summary", {}).get("layer_count") != len(architecture.get("layers", [])):
        errors.append("architecture readiness endpoint layer count does not match layers")
    if not architecture.get("next_horizontal_slices"):
        errors.append("architecture readiness endpoint returned no next horizontal slices")

    try:
        trust_registry = fetch_json(f"{API_BASE_URL}/trust-registry", origin=DASHBOARD_BASE_URL.rstrip("/"))
    except RuntimeError as exc:
        errors.append(str(exc))
        return

    if trust_registry.get("summary", {}).get("surface_count") != len(trust_registry.get("surfaces", [])):
        errors.append("trust registry endpoint surface count does not match surfaces")
    if trust_registry.get("summary", {}).get("decision_grade_surface_count") != 0:
        errors.append("trust registry endpoint should not mark synthetic surfaces decision-grade")

    try:
        source_ingestion = fetch_json(f"{API_BASE_URL}/source-ingestion", origin=DASHBOARD_BASE_URL.rstrip("/"))
    except RuntimeError as exc:
        errors.append(str(exc))
        return

    if source_ingestion.get("summary", {}).get("production_ingestion_ready_count") != 0:
        errors.append("source ingestion endpoint must not mark production ingestion ready")
    if not source_ingestion.get("envelope_fields"):
        errors.append("source ingestion endpoint returned no ingestion envelope fields")

    try:
        normalization = fetch_json(f"{API_BASE_URL}/normalization-crosswalk", origin=DASHBOARD_BASE_URL.rstrip("/"))
    except RuntimeError as exc:
        errors.append(str(exc))
        return

    if normalization.get("summary", {}).get("ontology_schema_work") != "deferred":
        errors.append("normalization crosswalk endpoint must keep ontology schema work deferred")
    if normalization.get("summary", {}).get("competency_count") != len(normalization.get("rows", [])):
        errors.append("normalization crosswalk endpoint row count does not match summary")

    try:
        governance = fetch_json(f"{API_BASE_URL}/governance-cadence", origin=DASHBOARD_BASE_URL.rstrip("/"))
    except RuntimeError as exc:
        errors.append(str(exc))
        return

    if governance.get("summary", {}).get("automated_scheduling") != "deferred":
        errors.append("governance cadence endpoint must keep automated scheduling deferred")
    if governance.get("summary", {}).get("cadence_count") != len(governance.get("cadences", [])):
        errors.append("governance cadence endpoint cadence count does not match cadences")

    try:
        decision_policy = fetch_json(f"{API_BASE_URL}/decision-policy", origin=DASHBOARD_BASE_URL.rstrip("/"))
    except RuntimeError as exc:
        errors.append(str(exc))
        return

    if decision_policy.get("summary", {}).get("decision_count") != len(decision_policy.get("policy_rows", [])):
        errors.append("decision policy endpoint row count does not match summary")
    if not decision_policy.get("policy_catalog"):
        errors.append("decision policy endpoint returned no policy catalog")

    try:
        reasoning_stress = fetch_json(f"{API_BASE_URL}/reasoning-stress", origin=DASHBOARD_BASE_URL.rstrip("/"))
    except RuntimeError as exc:
        errors.append(str(exc))
        return

    if reasoning_stress.get("summary", {}).get("database_schema_work") != "deferred":
        errors.append("reasoning stress endpoint must keep database schema work deferred")
    if reasoning_stress.get("summary", {}).get("scenario_count") != len(reasoning_stress.get("scenarios", [])):
        errors.append("reasoning stress endpoint scenario count does not match scenarios")

    try:
        review_workflow = fetch_json(f"{API_BASE_URL}/review-workflow", origin=DASHBOARD_BASE_URL.rstrip("/"))
    except RuntimeError as exc:
        errors.append(str(exc))
        return

    if review_workflow.get("summary", {}).get("step_count") != len(review_workflow.get("steps", [])):
        errors.append("review workflow endpoint step count does not match steps")
    item_count = sum(len(step.get("items", [])) for step in review_workflow.get("steps", []))
    if review_workflow.get("summary", {}).get("item_count") != item_count:
        errors.append("review workflow endpoint item count does not match step items")
    if not review_workflow.get("allowed_outcomes"):
        errors.append("review workflow endpoint returned no allowed outcomes")

    try:
        stakeholder_gates = fetch_json(f"{API_BASE_URL}/stakeholder-gates", origin=DASHBOARD_BASE_URL.rstrip("/"))
    except RuntimeError as exc:
        errors.append(str(exc))
        return

    if stakeholder_gates.get("summary", {}).get("item_count") is None:
        errors.append("stakeholder gates endpoint returned no item count")
    if not stakeholder_gates.get("stakeholder_views"):
        errors.append("stakeholder gates endpoint returned no stakeholder views")
    if not stakeholder_gates.get("gate_catalog"):
        errors.append("stakeholder gates endpoint returned no gate catalog")

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
