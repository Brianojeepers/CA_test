import unittest

from decision_spine.services.monthly_packet import build_monthly_packet
from decision_spine.services.stakeholder_packets import (
    STAKEHOLDER_VIEWS,
    build_all_stakeholder_packets,
    build_stakeholder_packet,
    render_stakeholder_packet_markdown,
)


class StakeholderPacketTests(unittest.TestCase):
    def test_builds_one_brief_for_each_stakeholder_view(self) -> None:
        packet = build_monthly_packet()
        briefs = build_all_stakeholder_packets(packet)

        self.assertEqual(len(briefs), len(STAKEHOLDER_VIEWS))
        self.assertEqual({brief["view_id"] for brief in briefs}, {view["id"] for view in STAKEHOLDER_VIEWS})

    def test_learning_packet_is_scoped_to_learning_decisions(self) -> None:
        brief = build_stakeholder_packet(build_monthly_packet(), "learning")

        self.assertEqual(brief["view_id"], "learning")
        self.assertGreaterEqual(brief["scope_count"], 1)
        self.assertTrue(
            all(
                decision["owner"] == "Learning" or "curriculum" in decision["summary"].lower()
                for decision in brief["key_decisions"]
            )
        )

    def test_markdown_render_is_nontechnical_and_decision_oriented(self) -> None:
        brief = build_stakeholder_packet(build_monthly_packet(), "council")
        markdown = render_stakeholder_packet_markdown(brief)

        self.assertIn("# Council Review Brief", markdown)
        self.assertIn("## Key Decisions", markdown)
        self.assertIn("## Action Items", markdown)
        self.assertIn("## What Changed", markdown)
        self.assertIn("Next trigger", markdown)


if __name__ == "__main__":
    unittest.main()
