import unittest

from fastapi.testclient import TestClient

from app.api.main import app


class ApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

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
        self.assertIn("v02_requirements", payload)
        self.assertEqual(payload["v02_requirements"][0]["capability"], "role_anchor_demand_index")

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
