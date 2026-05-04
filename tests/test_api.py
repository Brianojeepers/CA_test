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


if __name__ == "__main__":
    unittest.main()
