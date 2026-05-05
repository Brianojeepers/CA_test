import unittest

from decision_spine.services.reasoning_stress import (
    build_reasoning_stress_review,
    render_reasoning_stress_text,
)


class ReasoningStressTests(unittest.TestCase):
    def test_review_blocks_all_current_unsafe_claims(self) -> None:
        review = build_reasoning_stress_review()
        summary = review["summary"]

        self.assertEqual(summary["scenario_count"], 5)
        self.assertEqual(summary["pass_count"], 5)
        self.assertEqual(summary["fail_count"], 0)
        self.assertEqual(summary["unsafe_claims_blocked_count"], 5)
        self.assertEqual(summary["database_schema_work"], "deferred")

    def test_strong_signal_cannot_override_red_evidence_sources(self) -> None:
        review = build_reasoning_stress_review()
        scenarios = {scenario["scenario_id"]: scenario for scenario in review["scenarios"]}
        scenario = scenarios["RS-001"]

        self.assertEqual(scenario["result"], "pass")
        self.assertEqual(scenario["required_downgrade"], "monitor")
        self.assertIn("cohort outcomes are planning-only", scenario["evidence"])
        self.assertIn("learner evidence is planning-only", scenario["evidence"])

    def test_approved_decision_with_blocked_release_is_revised(self) -> None:
        review = build_reasoning_stress_review()
        scenarios = {scenario["scenario_id"]: scenario for scenario in review["scenarios"]}

        self.assertEqual(scenarios["RS-002"]["result"], "pass")
        self.assertEqual(scenarios["RS-002"]["required_downgrade"], "revise")

    def test_green_prediction_source_does_not_upgrade_market_ingestion(self) -> None:
        review = build_reasoning_stress_review()
        scenarios = {scenario["scenario_id"]: scenario for scenario in review["scenarios"]}
        scenario = scenarios["RS-003"]

        self.assertEqual(scenario["result"], "pass")
        self.assertEqual(scenario["required_downgrade"], "controlled_pilot_only")
        self.assertIn("market signals remain manual-contracting", scenario["evidence"])

    def test_text_review_is_shareable(self) -> None:
        text = render_reasoning_stress_text(build_reasoning_stress_review())

        self.assertIn("Reasoning Stress Test Review", text)
        self.assertIn("unsafe_claims_blocked=5", text)
        self.assertIn("[pass] RS-005 Dashboard action tries to bypass decision policy", text)
        self.assertNotIn("{", text)


if __name__ == "__main__":
    unittest.main()
