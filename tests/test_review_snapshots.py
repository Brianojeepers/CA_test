import tempfile
import unittest
from pathlib import Path

from decision_spine.services.review_snapshots import (
    build_review_diff,
    latest_snapshot,
    save_review_snapshot,
)


def packet(status: str = "too_early", action_text: str = "Unblock decision.") -> dict:
    return {
        "generated_date": "2026-05-04",
        "decision_impact": {
            "rows": [
                {
                    "decision_id": "DEC-1",
                    "status": status,
                    "owner": "Assessment Ops",
                    "recommendation": {
                        "recommended_action": "Review evidence." if status == "needs_attention" else "Wait for evidence.",
                        "blocker_or_risk": "suppressed evidence" if status == "needs_attention" else "Evidence window.",
                    },
                }
            ]
        },
        "actions": [{"kind": "release_blocker", "decision_id": "DEC-1", "severity": "amber", "text": action_text}],
        "decision_changelog": {
            "items": [
                {
                    "category": "pending",
                    "item_id": "REL-1",
                    "decision_id": "DEC-1",
                    "severity": "amber",
                    "title": "Assessment release",
                }
            ]
        },
    }


class ReviewSnapshotTests(unittest.TestCase):
    def test_save_and_load_latest_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = save_review_snapshot(packet(), Path(temp_dir), snapshot_id="review-1")
            loaded = latest_snapshot(Path(temp_dir))

        self.assertEqual(output_path.name, "review-1.json")
        self.assertEqual(loaded["snapshot_id"], "review-1")
        self.assertEqual(loaded["packet"]["generated_date"], "2026-05-04")
        self.assertNotIn("review_diff", loaded["packet"])

    def test_no_snapshot_diff_is_explicit(self) -> None:
        diff = build_review_diff(packet(), None)

        self.assertEqual(diff["snapshot_status"], "no_snapshot")
        self.assertEqual(diff["items"], [])

    def test_detects_status_recommendation_and_action_changes(self) -> None:
        previous = packet(status="too_early", action_text="Unblock decision.")
        current = packet(status="needs_attention", action_text="Review suppressed evidence.")
        diff = build_review_diff(current, previous)

        self.assertEqual(diff["snapshot_status"], "compared")
        self.assertEqual(diff["counts"]["status_changes"], 1)
        self.assertEqual(diff["counts"]["recommendation_changes"], 1)
        self.assertEqual(diff["counts"]["new_actions"], 1)
        self.assertEqual(diff["counts"]["removed_actions"], 1)


if __name__ == "__main__":
    unittest.main()
