import unittest

from decision_spine.services.schema_gap import build_schema_gap_report, load_v02_requirements


class SchemaGapTests(unittest.TestCase):
    def test_report_includes_source_readiness_and_file_gaps(self) -> None:
        report = build_schema_gap_report()

        self.assertEqual(report["summary"]["red_sources"], 2)
        files = {item["file"]: item for item in report["file_reports"]}
        self.assertIn("predictions.json", files)
        self.assertIn("cohort_outcomes.json", files)

    def test_alias_coverage_keeps_contract_name_differences_explicit(self) -> None:
        report = build_schema_gap_report()
        files = {item["file"]: item for item in report["file_reports"]}
        predictions_aliases = files["predictions.json"]["contract_alias_covered_in_seed"]
        cohort_aliases = files["cohort_outcomes.json"]["contract_alias_covered_in_seed"]

        self.assertIn({"field": "prediction_statement", "covered_by": ["claim"]}, predictions_aliases)
        self.assertIn({"field": "baseline_period", "covered_by": ["baseline_group"]}, cohort_aliases)

    def test_v02_requirements_show_expansion_gaps(self) -> None:
        report = build_schema_gap_report()
        requirements = {item["capability"]: item for item in report["v02_requirements"]}

        self.assertIn("demand_growth_rate", requirements["role_anchor_demand_index"]["missing_fields"])
        self.assertIn(
            "proficiency_gap_score",
            requirements["competency_gap_index_learner_side"]["missing_fields"],
        )
        self.assertEqual(requirements["role_anchor_demand_index"]["owner"], "Signal Intelligence Council")
        self.assertEqual(
            requirements["curriculum_impact_simulator"]["decision_unlocked"],
            "Estimate cost and expected placement or extension impact for proposed curriculum changes.",
        )

    def test_minimum_viable_pilot_fields_include_future_intelligence_inputs(self) -> None:
        report = build_schema_gap_report()
        signal_fields = report["minimum_viable_pilot_fields"]["signals.json"]

        self.assertIn("demand_volume", signal_fields)
        self.assertIn("signal_strength_score", signal_fields)

    def test_v02_requirements_are_loaded_from_data_contract(self) -> None:
        requirements = load_v02_requirements()
        role_demand = next(item for item in requirements if item["capability"] == "role_anchor_demand_index")

        self.assertIn("demand_growth_rate", role_demand["required_fields"])
        self.assertTrue(all("source_owner" in field for field in role_demand["field_details"]))

    def test_missing_v02_fields_generate_actions(self) -> None:
        report = build_schema_gap_report()

        self.assertEqual(report["summary"]["field_action_count"], 18)
        self.assertEqual(len(report["field_actions"]), 18)
        self.assertEqual(report["summary"]["blocked_field_actions"], 2)

    def test_privacy_sensitive_learner_actions_are_blocked(self) -> None:
        report = build_schema_gap_report()
        actions = {item["field"]: item for item in report["field_actions"]}

        self.assertEqual(actions["demonstrated_proficiency"]["severity"], "red")
        self.assertTrue(actions["demonstrated_proficiency"]["blocked"])
        self.assertEqual(actions["proficiency_gap_score"]["severity"], "red")
        self.assertTrue(actions["proficiency_gap_score"]["blocked"])

    def test_commercial_summary_actions_route_to_market_intelligence(self) -> None:
        report = build_schema_gap_report()
        actions = {item["field"]: item for item in report["field_actions"]}

        self.assertEqual(actions["demand_volume"]["source_owner"], "Market Intelligence")
        self.assertEqual(actions["demand_volume"]["severity"], "amber")

    def test_field_actions_are_grouped_by_owner(self) -> None:
        report = build_schema_gap_report()
        owner_groups = {item["owner"]: item for item in report["field_actions_by_owner"]}

        self.assertIn("Market Intelligence", owner_groups)
        self.assertEqual(owner_groups["Market Intelligence"]["action_count"], 6)
        self.assertEqual(owner_groups["Market Intelligence"]["amber"], 6)
        self.assertEqual(owner_groups["Market Intelligence"]["blocked"], 0)
        self.assertEqual(report["summary"]["field_action_owner_count"], len(owner_groups))


if __name__ == "__main__":
    unittest.main()
