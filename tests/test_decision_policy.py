import unittest

from decision_spine.services.decision_policy import build_decision_policy_review, render_decision_policy_text


class DecisionPolicyTests(unittest.TestCase):
    def test_policy_catalog_defines_all_operating_outcomes(self) -> None:
        review = build_decision_policy_review()
        outcomes = {item["outcome"] for item in review["policy_catalog"]}

        self.assertEqual(outcomes, {"act_now", "revise", "monitor", "wait", "escalate", "archive"})
        for item in review["policy_catalog"]:
            self.assertTrue(item["required_trust_posture"])
            self.assertTrue(item["evidence_conditions"])
            self.assertTrue(item["who_can_decide"])

    def test_current_policy_counts_reflect_seed_decisions(self) -> None:
        review = build_decision_policy_review()
        summary = review["summary"]

        self.assertEqual(summary["decision_count"], 5)
        self.assertEqual(summary["act_now_count"], 0)
        self.assertEqual(summary["revise_count"], 1)
        self.assertEqual(summary["monitor_count"], 2)
        self.assertEqual(summary["wait_count"], 1)
        self.assertEqual(summary["escalate_count"], 1)
        self.assertEqual(summary["archive_count"], 0)

    def test_policy_rows_map_current_decisions_to_safe_actions(self) -> None:
        review = build_decision_policy_review()
        rows = {row["decision_id"]: row for row in review["policy_rows"]}

        self.assertEqual(rows["DEC-2026-001"]["policy_outcome"], "monitor")
        self.assertEqual(rows["DEC-2026-002"]["policy_outcome"], "wait")
        self.assertEqual(rows["DEC-2026-004"]["policy_outcome"], "revise")
        self.assertEqual(rows["DEC-2026-005"]["policy_outcome"], "escalate")
        self.assertEqual(rows["DEC-2026-003"]["policy_outcome"], "monitor")

    def test_policy_keeps_workflow_design_only_claims_deferred(self) -> None:
        review = build_decision_policy_review()
        rows = {row["decision_id"]: row for row in review["policy_rows"]}

        self.assertEqual(rows["DEC-2026-001"]["journey_mode"], "workflow_design_only")
        self.assertIn("do not make performance", rows["DEC-2026-001"]["must_defer"])

    def test_text_policy_review_is_shareable(self) -> None:
        text = render_decision_policy_text(build_decision_policy_review())

        self.assertIn("Decision Policy Review", text)
        self.assertIn("[escalate] DEC-2026-005", text)
        self.assertIn("[revise] DEC-2026-004", text)
        self.assertNotIn("{", text)


if __name__ == "__main__":
    unittest.main()
