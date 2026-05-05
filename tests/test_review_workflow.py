import json
import unittest
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory

from decision_spine.services.review_workflow import (
    InvalidReviewOutcome,
    UnknownReviewItem,
    build_review_workflow,
    update_review_item_outcome,
)


class ReviewWorkflowTests(unittest.TestCase):
    def test_build_review_workflow_returns_agenda_items(self) -> None:
        workflow = build_review_workflow(outcome_records=[], event_records=[])

        self.assertEqual(workflow["summary"]["step_count"], 5)
        self.assertEqual(workflow["summary"]["item_count"], 19)
        self.assertEqual(workflow["summary"]["unreviewed_count"], 19)
        self.assertEqual([step["step_id"] for step in workflow["steps"]][0], "trust_posture")
        self.assertIn("allowed_outcomes", workflow)

    def test_update_review_item_outcome_persists_record_and_event(self) -> None:
        workflow = build_review_workflow(outcome_records=[], event_records=[])
        item = workflow["steps"][0]["items"][0]
        with TemporaryDirectory() as temp_dir:
            status_path = Path(temp_dir) / "review_workflow_outcomes.json"
            event_path = Path(temp_dir) / "review_workflow_events.json"
            status_path.write_text("[]", encoding="utf-8")
            event_path.write_text("[]", encoding="utf-8")

            record = update_review_item_outcome(
                item["step_id"],
                item["item_id"],
                "accepted",
                "Council accepted the current bounded trust language.",
                path=status_path,
                event_path=event_path,
                updated_date=date(2026, 5, 5),
            )

            self.assertEqual(record["outcome"], "accepted")
            records = json.loads(status_path.read_text(encoding="utf-8"))
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0]["step_id"], item["step_id"])
            self.assertEqual(records[0]["item_id"], item["item_id"])
            self.assertEqual(records[0]["updated_date"], "2026-05-05")
            events = json.loads(event_path.read_text(encoding="utf-8"))
            self.assertEqual(len(events), 1)
            self.assertEqual(events[0]["previous_outcome"], "unreviewed")
            self.assertEqual(events[0]["next_outcome"], "accepted")

            refreshed = build_review_workflow(outcome_records=records, event_records=events)
            refreshed_item = refreshed["steps"][0]["items"][0]
            self.assertEqual(refreshed_item["review_outcome"], "accepted")
            self.assertEqual(refreshed["summary"]["accepted_count"], 1)

    def test_update_review_item_outcome_rejects_invalid_outcome(self) -> None:
        workflow = build_review_workflow(outcome_records=[], event_records=[])
        item = workflow["steps"][0]["items"][0]
        with TemporaryDirectory() as temp_dir:
            status_path = Path(temp_dir) / "review_workflow_outcomes.json"
            event_path = Path(temp_dir) / "review_workflow_events.json"
            status_path.write_text("[]", encoding="utf-8")
            event_path.write_text("[]", encoding="utf-8")

            with self.assertRaises(InvalidReviewOutcome):
                update_review_item_outcome(
                    item["step_id"],
                    item["item_id"],
                    "done",
                    path=status_path,
                    event_path=event_path,
                )

    def test_update_review_item_outcome_rejects_unknown_item(self) -> None:
        with TemporaryDirectory() as temp_dir:
            status_path = Path(temp_dir) / "review_workflow_outcomes.json"
            event_path = Path(temp_dir) / "review_workflow_events.json"
            status_path.write_text("[]", encoding="utf-8")
            event_path.write_text("[]", encoding="utf-8")

            with self.assertRaises(UnknownReviewItem):
                update_review_item_outcome(
                    "trust_posture",
                    "not-current",
                    "accepted",
                    path=status_path,
                    event_path=event_path,
                )


if __name__ == "__main__":
    unittest.main()
