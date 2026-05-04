import unittest

from decision_spine.services.monthly_packet import (
    build_monthly_packet,
    recommendation_for_status,
    render_monthly_packet_markdown,
)


class MonthlyPacketServiceTests(unittest.TestCase):
    def test_monthly_packet_returns_frontend_ready_sections(self) -> None:
        packet = build_monthly_packet()

        self.assertEqual(packet["data_trust"]["validation_status"], "passed")
        self.assertIn("kpi_posture", packet)
        self.assertIn("decision_impact", packet)
        self.assertIn("actions", packet)
        self.assertIn("stakeholder_drilldowns", packet)
        self.assertIn("known_limits", packet)
        self.assertIn("recommendation", packet["decision_impact"]["rows"][0])
        self.assertIn("signal_ids", packet["decision_impact"]["rows"][0])

    def test_markdown_renderer_uses_structured_packet(self) -> None:
        markdown = render_monthly_packet_markdown(build_monthly_packet())

        self.assertIn("# Decision Spine Monthly Packet", markdown)
        self.assertIn("## Decision Impact", markdown)
        self.assertIn("## Stakeholder Drill-Downs", markdown)

    def test_pending_release_recommendation_prioritizes_unblocking(self) -> None:
        recommendation = recommendation_for_status(
            "too_early",
            [{"release_id": "REL-1", "release_status": "in_progress"}],
            [],
            [],
        )

        self.assertEqual(recommendation["priority"], "high")
        self.assertIn("Unblock implementation", recommendation["recommended_action"])

    def test_suppressed_evidence_recommendation_names_risk(self) -> None:
        recommendation = recommendation_for_status(
            "needs_attention",
            [{"release_id": "REL-1", "release_status": "released"}],
            [{"readiness_level": "ready", "suppression_applied": True}],
            [{"placement_rate": None, "retention_90d_rate": None}],
        )

        self.assertEqual(recommendation["priority"], "high")
        self.assertIn("suppressed evidence", recommendation["blocker_or_risk"])


if __name__ == "__main__":
    unittest.main()
