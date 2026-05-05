import unittest

from decision_spine.services.governance_cadence import (
    build_governance_cadence_review,
    render_governance_cadence_text,
)


class GovernanceCadenceTests(unittest.TestCase):
    def test_review_defines_weekly_monthly_and_quarterly_cadence(self) -> None:
        review = build_governance_cadence_review()
        summary = review["summary"]

        self.assertEqual(summary["cadence_count"], 3)
        self.assertEqual(summary["weekly_count"], 1)
        self.assertEqual(summary["monthly_count"], 1)
        self.assertEqual(summary["quarterly_count"], 1)
        self.assertEqual(summary["ready_for_manual_trial_count"], 2)
        self.assertEqual(summary["defined_not_trialed_count"], 1)
        self.assertEqual(summary["automated_scheduling"], "deferred")
        self.assertEqual(summary["production_jobs"], "deferred")

    def test_every_cadence_has_operating_contract(self) -> None:
        review = build_governance_cadence_review()

        for cadence in review["cadences"]:
            self.assertTrue(cadence["entry_criteria"])
            self.assertTrue(cadence["exit_criteria"])
            self.assertTrue(cadence["required_artifacts"])
            self.assertTrue(cadence["decision_rights"])
            self.assertTrue(cadence["escalation_triggers"])
            self.assertTrue(cadence["deferred_work"])

    def test_weekly_review_cannot_start_scheduled_ingestion(self) -> None:
        review = build_governance_cadence_review()
        cadences = {cadence["cadence_id"]: cadence for cadence in review["cadences"]}
        weekly = cadences["weekly_signal_refresh"]

        self.assertEqual(weekly["cadence"], "weekly")
        self.assertIn("Scheduled ingestion", weekly["deferred_work"])
        self.assertIn("scripts/source_ingestion_review.py", weekly["required_artifacts"])

    def test_monthly_review_uses_policy_and_stress_artifacts(self) -> None:
        review = build_governance_cadence_review()
        cadences = {cadence["cadence_id"]: cadence for cadence in review["cadences"]}
        monthly = cadences["monthly_council_review"]

        self.assertIn("scripts/decision_policy_review.py", monthly["required_artifacts"])
        self.assertIn("scripts/reasoning_stress_review.py", monthly["required_artifacts"])
        self.assertIn("Automated approvals", monthly["deferred_work"])

    def test_quarterly_recalibration_defers_schema_and_model_work(self) -> None:
        review = build_governance_cadence_review()
        cadences = {cadence["cadence_id"]: cadence for cadence in review["cadences"]}
        quarterly = cadences["quarterly_recalibration"]

        self.assertEqual(quarterly["manual_readiness"], "defined_not_trialed")
        self.assertIn("Final ontology schema", quarterly["deferred_work"])
        self.assertIn("Model training or scoring weights", quarterly["deferred_work"])

    def test_text_review_is_shareable(self) -> None:
        text = render_governance_cadence_text(build_governance_cadence_review())

        self.assertIn("Governance Cadence Review", text)
        self.assertIn("automated_scheduling=deferred", text)
        self.assertIn("[ready_for_manual_trial] Monthly council decision review", text)
        self.assertNotIn("{", text)


if __name__ == "__main__":
    unittest.main()
