import unittest

from decision_spine.services.monthly_packet import build_monthly_packet, render_monthly_packet_markdown


class MonthlyPacketServiceTests(unittest.TestCase):
    def test_monthly_packet_returns_frontend_ready_sections(self) -> None:
        packet = build_monthly_packet()

        self.assertEqual(packet["data_trust"]["validation_status"], "passed")
        self.assertIn("kpi_posture", packet)
        self.assertIn("decision_impact", packet)
        self.assertIn("actions", packet)
        self.assertIn("stakeholder_drilldowns", packet)
        self.assertIn("known_limits", packet)

    def test_markdown_renderer_uses_structured_packet(self) -> None:
        markdown = render_monthly_packet_markdown(build_monthly_packet())

        self.assertIn("# Decision Spine Monthly Packet", markdown)
        self.assertIn("## Decision Impact", markdown)
        self.assertIn("## Stakeholder Drill-Downs", markdown)


if __name__ == "__main__":
    unittest.main()
