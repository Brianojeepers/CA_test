import unittest

from decision_spine.services.review_workflow import build_review_workflow
from decision_spine.services.stakeholder_gates import (
    build_stakeholder_gate_review,
    render_stakeholder_gate_text,
)


def outcome_record_for(item: dict[str, str], outcome: str) -> dict[str, str]:
    return {
        "step_id": item["step_id"],
        "item_id": item["item_id"],
        "title": item["title"],
        "owner": item["owner"],
        "outcome": outcome,
        "notes": "Recorded during test review.",
        "updated_date": "2026-05-05",
    }


class StakeholderGateTests(unittest.TestCase):
    def test_unreviewed_workflow_keeps_stakeholder_language_internal(self) -> None:
        workflow = build_review_workflow(outcome_records=[], event_records=[])
        gate_review = build_stakeholder_gate_review(workflow=workflow)

        self.assertEqual(gate_review["summary"]["item_count"], 19)
        self.assertEqual(gate_review["summary"]["share_ready_count"], 0)
        self.assertEqual(gate_review["summary"]["unreviewed_count"], 19)
        self.assertEqual(gate_review["summary"]["share_ready_view_count"], 0)
        self.assertFalse(gate_review["share_ready_language"])

    def test_accepted_review_item_becomes_share_ready_for_relevant_views(self) -> None:
        workflow = build_review_workflow(outcome_records=[], event_records=[])
        trust_item = workflow["steps"][0]["items"][0]
        reviewed_workflow = build_review_workflow(
            outcome_records=[outcome_record_for(trust_item, "accepted")],
            event_records=[],
        )

        gate_review = build_stakeholder_gate_review(workflow=reviewed_workflow)

        self.assertEqual(gate_review["summary"]["share_ready_count"], 1)
        self.assertEqual(len(gate_review["share_ready_language"]), 1)
        self.assertIn("Share only bounded language", gate_review["share_ready_language"][0]["communication_instruction"])
        council_gate = next(view for view in gate_review["stakeholder_views"] if view["view_id"] == "council")
        self.assertEqual(council_gate["share_ready_count"], 1)

    def test_blocked_review_item_is_suppressed(self) -> None:
        workflow = build_review_workflow(outcome_records=[], event_records=[])
        source_step = next(step for step in workflow["steps"] if step["step_id"] == "source_blockers")
        red_source_item = next(item for item in source_step["items"] if item["severity"] == "red")
        reviewed_workflow = build_review_workflow(
            outcome_records=[outcome_record_for(red_source_item, "blocked")],
            event_records=[],
        )

        gate_review = build_stakeholder_gate_review(workflow=reviewed_workflow)

        self.assertEqual(gate_review["summary"]["suppressed_count"], 1)
        self.assertIn("Suppress from stakeholder claims", gate_review["blocked_or_follow_up"][0]["communication_instruction"])

    def test_text_review_names_share_readiness(self) -> None:
        text = render_stakeholder_gate_text(build_stakeholder_gate_review(workflow=build_review_workflow()))

        self.assertIn("Stakeholder Gate Review", text)
        self.assertIn("Share-Ready Language", text)
        self.assertIn("Internal Or Suppressed", text)


if __name__ == "__main__":
    unittest.main()
