import unittest

from decision_spine.services.monthly_packet import (
    build_decision_changelog,
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
        self.assertIn("decision_changelog", packet)
        self.assertIn("review_diff", packet)
        self.assertIn("stakeholder_drilldowns", packet)
        self.assertIn("known_limits", packet)
        self.assertIn("recommendation", packet["decision_impact"]["rows"][0])
        self.assertIn("signal_ids", packet["decision_impact"]["rows"][0])
        self.assertIn("partner_functions", packet["decision_impact"]["rows"][0])
        self.assertIn("categories", packet["decision_changelog"])
        self.assertIn("items", packet["decision_changelog"])
        self.assertIn("snapshot_status", packet["review_diff"])

    def test_markdown_renderer_uses_structured_packet(self) -> None:
        markdown = render_monthly_packet_markdown(build_monthly_packet())

        self.assertIn("# Decision Spine Monthly Packet", markdown)
        self.assertIn("## Decision Impact", markdown)
        self.assertIn("## What Changed And Why", markdown)
        self.assertIn("## Since Last Review Snapshot", markdown)
        self.assertIn("## Stakeholder Drill-Downs", markdown)

    def test_decision_changelog_groups_releases_and_no_change_decisions(self) -> None:
        changelog = build_decision_changelog(
            [{"signal_id": "SIG-1", "signal_theme": "Market signal", "summary": "Client demand."}],
            [
                {
                    "decision_id": "DEC-1",
                    "signal_ids": ["SIG-1"],
                    "decision_signed_date": "2026-04-01",
                    "decision_type": "curriculum",
                    "decision_status": "approved",
                    "owner": "Learning",
                    "decision_summary": "Add curriculum module.",
                    "rationale": "Demand is strong.",
                },
                {
                    "decision_id": "DEC-2",
                    "signal_ids": ["SIG-1"],
                    "decision_signed_date": "2026-04-03",
                    "decision_type": "monitor",
                    "decision_status": "watch",
                    "owner": "Research",
                    "decision_summary": "Monitor signal.",
                    "rationale": "Demand is weak.",
                },
                {
                    "decision_id": "DEC-3",
                    "signal_ids": ["SIG-1"],
                    "decision_signed_date": "2026-04-05",
                    "decision_type": "assessment",
                    "decision_status": "approved",
                    "owner": "Assessment Ops",
                    "decision_summary": "Add assessment criterion.",
                    "rationale": "Credential evidence is needed.",
                },
            ],
            [
                {
                    "release_id": "REL-1",
                    "decision_id": "DEC-1",
                    "release_date": "2026-04-12",
                    "release_status": "released",
                    "programme": "AI Builder",
                    "artifact": "Evaluation block",
                    "linked_signal_ids": ["SIG-1"],
                }
            ],
        )

        self.assertEqual(
            {item["category"] for item in changelog["items"]},
            {"released", "monitor", "missing_release"},
        )
        self.assertEqual(changelog["categories"][0]["id"], "all")

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
