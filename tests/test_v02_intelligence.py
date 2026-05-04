import unittest

from decision_spine.services.v02_intelligence import build_v02_intelligence_preview


class V02IntelligencePreviewTests(unittest.TestCase):
    def test_preview_returns_four_directional_sections(self) -> None:
        preview = build_v02_intelligence_preview()

        self.assertEqual(preview["summary"]["section_count"], 4)
        self.assertFalse(preview["summary"]["hard_recommendations_enabled"])
        self.assertEqual(preview["summary"]["preview_status"], "directional_only")
        self.assertEqual({section["recommendation_strength"] for section in preview["sections"]}, {"directional_only"})

    def test_role_anchor_preview_stays_blocked_by_missing_rdi_fields(self) -> None:
        preview = build_v02_intelligence_preview()
        sections = {section["id"]: section for section in preview["sections"]}
        role_anchor = sections["role_anchor_demand_index"]
        missing = {field["field"] for field in role_anchor["missing_fields"]}

        self.assertEqual(role_anchor["readiness"]["status"], "field_gaps")
        self.assertIn("demand_volume", missing)
        self.assertIn("placement_conversion_alignment", missing)
        self.assertFalse(role_anchor["hard_recommendations_enabled"])

    def test_competency_gap_preview_preserves_learner_privacy_blocker(self) -> None:
        preview = build_v02_intelligence_preview()
        sections = {section["id"]: section for section in preview["sections"]}
        competency_gap = sections["competency_gap_index"]

        self.assertEqual(competency_gap["readiness"]["status"], "blocked")
        self.assertGreaterEqual(len(competency_gap["next_actions"]), 1)
        self.assertIn("privacy", competency_gap["readiness"]["reason"])
        self.assertIn("demonstrated proficiency", competency_gap["do_not_claim"].replace("_", " "))

    def test_horizon_and_impact_sections_show_current_evidence_but_no_hard_claims(self) -> None:
        preview = build_v02_intelligence_preview()
        sections = {section["id"]: section for section in preview["sections"]}

        self.assertGreaterEqual(len(sections["horizon_radar"]["directional_findings"]), 1)
        self.assertGreaterEqual(len(sections["curriculum_impact_simulator"]["directional_findings"]), 1)
        self.assertFalse(sections["horizon_radar"]["hard_recommendations_enabled"])
        self.assertFalse(sections["curriculum_impact_simulator"]["hard_recommendations_enabled"])


if __name__ == "__main__":
    unittest.main()
