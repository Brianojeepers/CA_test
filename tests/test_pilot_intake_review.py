import unittest

from decision_spine.services.pilot_intake_review import build_pilot_intake_review, render_pilot_intake_review_text


class PilotIntakeReviewTests(unittest.TestCase):
    def test_review_classifies_current_owner_responses(self) -> None:
        review = build_pilot_intake_review()

        self.assertEqual(review["summary"]["field_count"], 18)
        self.assertEqual(review["summary"]["response_count"], 18)
        self.assertEqual(review["summary"]["accepted_count"], 5)
        self.assertEqual(review["summary"]["needs_clarification_count"], 6)
        self.assertEqual(review["summary"]["privacy_blocked_count"], 2)
        self.assertEqual(review["summary"]["not_ready_count"], 5)

    def test_capability_readiness_summarizes_schema_gate(self) -> None:
        review = build_pilot_intake_review()
        capabilities = {item["capability"]: item for item in review["capability_groups"]}

        self.assertEqual(capabilities["competency_gap_index_learner_side"]["readiness"], "privacy_blocked")
        self.assertEqual(capabilities["role_anchor_demand_index"]["readiness"], "partial")
        self.assertEqual(capabilities["curriculum_impact_simulator"]["readiness"], "not_ready")
        self.assertEqual(review["summary"]["pilot_ready_capability_count"], 0)

    def test_accepted_items_have_pilot_schema_design_next_step(self) -> None:
        review = build_pilot_intake_review()
        items = {item["field"]: item for item in review["items"]}

        self.assertEqual(items["demand_volume"]["intake_status"], "accepted")
        self.assertIn("schema design", items["demand_volume"]["next_step"])
        self.assertEqual(items["demonstrated_proficiency"]["intake_status"], "privacy_blocked")

    def test_text_review_is_shareable(self) -> None:
        text = render_pilot_intake_review_text(build_pilot_intake_review())

        self.assertIn("Pilot Intake Review", text)
        self.assertIn("Capability Readiness", text)
        self.assertIn("[privacy_blocked] Assessment Ops", text)
        self.assertNotIn("{", text)


if __name__ == "__main__":
    unittest.main()
