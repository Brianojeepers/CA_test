import json
import unittest
from contextlib import contextmanager
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterator

from fastapi.testclient import TestClient

from app.api.main import app
from decision_spine.services import review_workflow as review_workflow_service
from decision_spine.services import schema_gap as schema_gap_service


class ApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    @contextmanager
    def temporary_status_register(self) -> Iterator[tuple[Path, Path]]:
        original_status_path = schema_gap_service.FIELD_ACTION_STATUS_FILE
        original_event_path = schema_gap_service.FIELD_ACTION_EVENT_FILE
        with TemporaryDirectory() as temp_dir:
            status_path = Path(temp_dir) / "v02_field_action_status.json"
            event_path = Path(temp_dir) / "v02_field_action_events.json"
            status_path.write_text(original_status_path.read_text(encoding="utf-8"), encoding="utf-8")
            event_path.write_text(original_event_path.read_text(encoding="utf-8"), encoding="utf-8")
            schema_gap_service.FIELD_ACTION_STATUS_FILE = status_path
            schema_gap_service.FIELD_ACTION_EVENT_FILE = event_path
            try:
                yield status_path, event_path
            finally:
                schema_gap_service.FIELD_ACTION_STATUS_FILE = original_status_path
                schema_gap_service.FIELD_ACTION_EVENT_FILE = original_event_path

    @contextmanager
    def temporary_review_workflow_register(self) -> Iterator[tuple[Path, Path]]:
        original_outcome_path = review_workflow_service.REVIEW_OUTCOME_FILE
        original_event_path = review_workflow_service.REVIEW_EVENT_FILE
        with TemporaryDirectory() as temp_dir:
            outcome_path = Path(temp_dir) / "review_workflow_outcomes.json"
            event_path = Path(temp_dir) / "review_workflow_events.json"
            outcome_path.write_text("[]", encoding="utf-8")
            event_path.write_text("[]", encoding="utf-8")
            review_workflow_service.REVIEW_OUTCOME_FILE = outcome_path
            review_workflow_service.REVIEW_EVENT_FILE = event_path
            try:
                yield outcome_path, event_path
            finally:
                review_workflow_service.REVIEW_OUTCOME_FILE = original_outcome_path
                review_workflow_service.REVIEW_EVENT_FILE = original_event_path

    def test_health_endpoint(self) -> None:
        response = self.client.get("/api/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_monthly_packet_endpoint_returns_structured_packet(self) -> None:
        response = self.client.get("/api/monthly-packet")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["data_trust"]["validation_status"], "passed")
        self.assertIn("kpi_posture", payload)
        self.assertIn("decision_impact", payload)
        self.assertIn("actions", payload)

    def test_schema_gap_endpoint_returns_v02_readiness(self) -> None:
        response = self.client.get("/api/schema-gap")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["summary"]["v02_gap_count"], 18)
        self.assertEqual(payload["summary"]["field_action_count"], 18)
        self.assertEqual(payload["summary"]["blocked_field_actions"], 2)
        self.assertEqual(payload["summary"]["field_action_status_counts"]["open"], 18)
        self.assertIn("v02_requirements", payload)
        self.assertIn("field_actions", payload)
        self.assertIn("field_actions_by_owner", payload)
        self.assertEqual(payload["v02_requirements"][0]["capability"], "role_anchor_demand_index")

    def test_v02_intelligence_endpoint_returns_directional_preview(self) -> None:
        response = self.client.get("/api/v02-intelligence")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertFalse(payload["summary"]["hard_recommendations_enabled"])
        self.assertEqual(payload["summary"]["section_count"], 4)
        self.assertEqual(payload["sections"][0]["id"], "role_anchor_demand_index")
        self.assertIn("guardrails", payload)

    def test_pilot_request_pack_endpoint_returns_owner_ready_requests(self) -> None:
        response = self.client.get("/api/pilot-request-pack")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["summary"]["request_count"], 18)
        self.assertEqual(payload["summary"]["privacy_review_count"], 2)
        self.assertIn("owner_groups", payload)

    def test_pilot_intake_review_endpoint_returns_schema_gate(self) -> None:
        response = self.client.get("/api/pilot-intake-review")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["summary"]["field_count"], 18)
        self.assertEqual(payload["summary"]["accepted_count"], 5)
        self.assertEqual(payload["summary"]["privacy_blocked_count"], 2)
        self.assertIn("capability_groups", payload)

    def test_architecture_readiness_endpoint_returns_horizontal_review(self) -> None:
        response = self.client.get("/api/architecture-readiness")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["summary"]["database_schema_work"], "deferred")
        self.assertEqual(payload["summary"]["layer_count"], len(payload["layers"]))
        self.assertEqual(payload["rating"]["score"], 9)
        self.assertIn("next_horizontal_slices", payload)

    def test_trust_registry_endpoint_returns_surface_posture(self) -> None:
        response = self.client.get("/api/trust-registry")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["summary"]["source_contract_count"], 7)
        self.assertEqual(payload["summary"]["surface_count"], len(payload["surfaces"]))
        self.assertEqual(payload["summary"]["decision_grade_surface_count"], 0)
        self.assertIn("priority_trust_actions", payload)

    def test_source_ingestion_endpoint_returns_readiness_posture(self) -> None:
        response = self.client.get("/api/source-ingestion")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["summary"]["source_count"], 7)
        self.assertEqual(payload["summary"]["production_ingestion_ready_count"], 0)
        self.assertEqual(payload["summary"]["database_schema_work"], "deferred")
        self.assertIn("envelope_fields", payload)

    def test_normalization_crosswalk_endpoint_returns_mapping_posture(self) -> None:
        response = self.client.get("/api/normalization-crosswalk")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["summary"]["role_count"], 3)
        self.assertEqual(payload["summary"]["competency_count"], len(payload["rows"]))
        self.assertEqual(payload["summary"]["ontology_schema_work"], "deferred")
        self.assertIn("role_summaries", payload)

    def test_governance_cadence_endpoint_returns_manual_cadences(self) -> None:
        response = self.client.get("/api/governance-cadence")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["summary"]["cadence_count"], len(payload["cadences"]))
        self.assertEqual(payload["summary"]["ready_for_manual_trial_count"], 2)
        self.assertEqual(payload["summary"]["automated_scheduling"], "deferred")

    def test_decision_policy_endpoint_returns_operating_policy(self) -> None:
        response = self.client.get("/api/decision-policy")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["summary"]["decision_count"], len(payload["policy_rows"]))
        self.assertEqual(payload["summary"]["escalate_count"], 1)
        self.assertIn("policy_catalog", payload)

    def test_reasoning_stress_endpoint_returns_cross_layer_scenarios(self) -> None:
        response = self.client.get("/api/reasoning-stress")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["summary"]["scenario_count"], len(payload["scenarios"]))
        self.assertEqual(payload["summary"]["fail_count"], 0)
        self.assertEqual(payload["summary"]["database_schema_work"], "deferred")
        self.assertIn("next_horizontal_slices", payload)

    def test_review_workflow_endpoint_returns_operating_agenda(self) -> None:
        with self.temporary_review_workflow_register():
            response = self.client.get("/api/review-workflow")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["summary"]["step_count"], 5)
        self.assertEqual(payload["summary"]["item_count"], 19)
        self.assertEqual(payload["summary"]["unreviewed_count"], 19)
        self.assertIn("allowed_outcomes", payload)

    def test_stakeholder_gates_endpoint_returns_communication_modes(self) -> None:
        with self.temporary_review_workflow_register():
            response = self.client.get("/api/stakeholder-gates")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["summary"]["item_count"], 19)
        self.assertEqual(payload["summary"]["share_ready_count"], 0)
        self.assertEqual(payload["summary"]["unreviewed_count"], 19)
        self.assertIn("stakeholder_views", payload)
        self.assertIn("gate_catalog", payload)

    def test_review_workflow_outcome_update_persists_and_refreshes_workflow(self) -> None:
        with self.temporary_review_workflow_register() as (outcome_path, event_path):
            workflow = self.client.get("/api/review-workflow").json()
            item = workflow["steps"][0]["items"][0]

            response = self.client.patch(
                f"/api/review-workflow/items/{item['step_id']}/{item['item_id']}",
                json={
                    "outcome": "accepted",
                    "notes": "Council accepted the current bounded trust language.",
                },
            )

            self.assertEqual(response.status_code, 200)
            payload = response.json()
            self.assertEqual(payload["summary"]["accepted_count"], 1)
            self.assertEqual(payload["summary"]["unreviewed_count"], 18)
            records = json.loads(outcome_path.read_text(encoding="utf-8"))
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0]["outcome"], "accepted")
            events = json.loads(event_path.read_text(encoding="utf-8"))
            self.assertEqual(len(events), 1)
            self.assertEqual(events[0]["next_outcome"], "accepted")

    def test_review_workflow_outcome_update_rejects_invalid_outcome(self) -> None:
        with self.temporary_review_workflow_register():
            workflow = self.client.get("/api/review-workflow").json()
            item = workflow["steps"][0]["items"][0]
            response = self.client.patch(
                f"/api/review-workflow/items/{item['step_id']}/{item['item_id']}",
                json={"outcome": "done", "notes": "Not a supported outcome."},
            )

        self.assertEqual(response.status_code, 400)

    def test_review_workflow_outcome_update_rejects_unknown_item(self) -> None:
        with self.temporary_review_workflow_register():
            response = self.client.patch(
                "/api/review-workflow/items/trust_posture/not-current",
                json={"outcome": "accepted", "notes": "Cannot update an unknown item."},
            )

        self.assertEqual(response.status_code, 404)

    def test_schema_gap_action_status_update_persists_and_refreshes_report(self) -> None:
        with self.temporary_status_register() as (status_path, event_path):
            response = self.client.patch(
                "/api/schema-gap/actions/role_anchor_demand_index/demand_volume",
                json={
                    "status": "in_review",
                    "notes": "Market source owner is confirming the pilot extract.",
                },
            )

            self.assertEqual(response.status_code, 200)
            payload = response.json()
            self.assertEqual(payload["summary"]["field_action_status_counts"]["open"], 17)
            self.assertEqual(payload["summary"]["field_action_status_counts"]["in_review"], 1)
            self.assertEqual(payload["summary"]["field_action_event_count"], 1)
            actions = {item["field"]: item for item in payload["field_actions"]}
            self.assertEqual(actions["demand_volume"]["action_status"], "in_review")
            self.assertEqual(
                actions["demand_volume"]["status_notes"],
                "Market source owner is confirming the pilot extract.",
            )
            self.assertEqual(actions["demand_volume"]["last_event"]["next_status"], "in_review")
            self.assertEqual(payload["recent_field_action_events"][0]["field"], "demand_volume")

            records = json.loads(status_path.read_text(encoding="utf-8"))
            updated = next(item for item in records if item["field"] == "demand_volume")
            self.assertEqual(updated["status"], "in_review")
            self.assertEqual(updated["updated_date"], date.today().isoformat())
            events = json.loads(event_path.read_text(encoding="utf-8"))
            self.assertEqual(len(events), 1)
            self.assertEqual(events[0]["previous_status"], "open")
            self.assertEqual(events[0]["next_status"], "in_review")

    def test_schema_gap_action_status_update_rejects_invalid_status(self) -> None:
        with self.temporary_status_register() as (status_path, event_path):
            before_statuses = status_path.read_text(encoding="utf-8")
            before_events = event_path.read_text(encoding="utf-8")
            response = self.client.patch(
                "/api/schema-gap/actions/role_anchor_demand_index/demand_volume",
                json={"status": "done", "notes": "Not a supported status."},
            )

            self.assertEqual(response.status_code, 400)
            self.assertEqual(status_path.read_text(encoding="utf-8"), before_statuses)
            self.assertEqual(event_path.read_text(encoding="utf-8"), before_events)

    def test_schema_gap_action_status_update_rejects_unknown_action(self) -> None:
        with self.temporary_status_register():
            response = self.client.patch(
                "/api/schema-gap/actions/role_anchor_demand_index/not_a_field",
                json={"status": "open", "notes": "Cannot update an unknown action."},
            )

        self.assertEqual(response.status_code, 404)

    def test_decision_detail_endpoint_returns_traceability(self) -> None:
        response = self.client.get("/api/decisions/DEC-2026-001")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["decision"]["decision_id"], "DEC-2026-001")
        self.assertGreaterEqual(payload["traceability"]["signal_count"], 1)
        self.assertGreaterEqual(payload["traceability"]["release_count"], 1)
        self.assertGreaterEqual(payload["traceability"]["competency_count"], 1)

    def test_decision_detail_endpoint_returns_404_for_unknown_id(self) -> None:
        response = self.client.get("/api/decisions/DEC-DOES-NOT-EXIST")

        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
