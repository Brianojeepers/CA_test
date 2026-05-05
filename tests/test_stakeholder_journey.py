import unittest

from decision_spine.services.stakeholder_journey import (
    build_stakeholder_journey_map,
    render_stakeholder_journey_text,
)


class StakeholderJourneyTests(unittest.TestCase):
    def test_map_covers_core_stakeholder_journeys(self) -> None:
        journey_map = build_stakeholder_journey_map()
        journeys = {journey["stakeholder_id"]: journey for journey in journey_map["journeys"]}

        self.assertEqual(journey_map["summary"]["journey_count"], 10)
        self.assertIn("council", journeys)
        self.assertIn("learning", journeys)
        self.assertIn("assessment_ops", journeys)
        self.assertIn("matching_csm", journeys)
        self.assertIn("solutions_sales", journeys)
        self.assertIn("data_analytics", journeys)
        self.assertIn("delivery", journeys)
        self.assertIn("source_owners", journeys)

    def test_privacy_blocked_surfaces_keep_council_in_workflow_design_mode(self) -> None:
        journey_map = build_stakeholder_journey_map()
        journeys = {journey["stakeholder_id"]: journey for journey in journey_map["journeys"]}

        council = journeys["council"]
        self.assertEqual(council["current_mode"], "workflow_design_only")
        self.assertIn("privacy_blocked", council["trust_statuses"])
        self.assertIn("Monthly council packet", [surface["label"] for surface in council["surfaces"]])

    def test_source_owner_journey_is_planning_ready(self) -> None:
        journey_map = build_stakeholder_journey_map()
        journeys = {journey["stakeholder_id"]: journey for journey in journey_map["journeys"]}

        source_owners = journeys["source_owners"]
        self.assertEqual(source_owners["current_mode"], "planning_ready")
        self.assertEqual(source_owners["trust_statuses"], ["planning_ready"])
        self.assertIn("field definitions", source_owners["evidence_needed"])

    def test_every_journey_has_action_defer_escalation_and_evidence_need(self) -> None:
        journey_map = build_stakeholder_journey_map()

        for journey in journey_map["journeys"]:
            self.assertTrue(journey["primary_question"].strip())
            self.assertTrue(journey["can_do_now"].strip())
            self.assertTrue(journey["must_defer"].strip())
            self.assertTrue(journey["escalation_path"].strip())
            self.assertTrue(journey["evidence_needed"].strip())
            self.assertGreaterEqual(len(journey["surfaces"]), 3)

    def test_text_map_is_shareable(self) -> None:
        text = render_stakeholder_journey_text(build_stakeholder_journey_map())

        self.assertIn("Stakeholder Journey Map", text)
        self.assertIn("[workflow_design_only] Signal Intelligence Council", text)
        self.assertIn("[planning_ready] Source Owners", text)
        self.assertNotIn("{", text)


if __name__ == "__main__":
    unittest.main()
