import json
import unittest
from contextlib import contextmanager
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterator

from fastapi.testclient import TestClient

from app.api.main import app
from decision_spine.services import schema_gap as schema_gap_service


class ApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    @contextmanager
    def temporary_status_register(self) -> Iterator[Path]:
        original_path = schema_gap_service.FIELD_ACTION_STATUS_FILE
        with TemporaryDirectory() as temp_dir:
            status_path = Path(temp_dir) / "v02_field_action_status.json"
            status_path.write_text(original_path.read_text(encoding="utf-8"), encoding="utf-8")
            schema_gap_service.FIELD_ACTION_STATUS_FILE = status_path
            try:
                yield status_path
            finally:
                schema_gap_service.FIELD_ACTION_STATUS_FILE = original_path

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

    def test_schema_gap_action_status_update_persists_and_refreshes_report(self) -> None:
        with self.temporary_status_register() as status_path:
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
            actions = {item["field"]: item for item in payload["field_actions"]}
            self.assertEqual(actions["demand_volume"]["action_status"], "in_review")
            self.assertEqual(
                actions["demand_volume"]["status_notes"],
                "Market source owner is confirming the pilot extract.",
            )

            records = json.loads(status_path.read_text(encoding="utf-8"))
            updated = next(item for item in records if item["field"] == "demand_volume")
            self.assertEqual(updated["status"], "in_review")
            self.assertEqual(updated["updated_date"], date.today().isoformat())

    def test_schema_gap_action_status_update_rejects_invalid_status(self) -> None:
        with self.temporary_status_register():
            response = self.client.patch(
                "/api/schema-gap/actions/role_anchor_demand_index/demand_volume",
                json={"status": "done", "notes": "Not a supported status."},
            )

        self.assertEqual(response.status_code, 400)

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
