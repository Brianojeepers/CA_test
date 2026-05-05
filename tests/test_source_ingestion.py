import unittest

from decision_spine.services.source_ingestion import (
    build_source_ingestion_review,
    render_source_ingestion_review_text,
)


class SourceIngestionTests(unittest.TestCase):
    def test_review_summarizes_current_ingestion_posture(self) -> None:
        review = build_source_ingestion_review()
        summary = review["summary"]

        self.assertEqual(summary["source_count"], 7)
        self.assertEqual(summary["blocked_count"], 2)
        self.assertEqual(summary["manual_contracting_count"], 4)
        self.assertEqual(summary["pilot_candidate_count"], 1)
        self.assertEqual(summary["production_ingestion_ready_count"], 0)
        self.assertEqual(summary["database_schema_work"], "deferred")

    def test_envelope_defines_core_ingestion_context(self) -> None:
        review = build_source_ingestion_review()
        fields = {field["field"] for field in review["envelope_fields"]}

        self.assertIn("source_id", fields)
        self.assertIn("observed_date", fields)
        self.assertIn("logged_date", fields)
        self.assertIn("freshness_sla", fields)
        self.assertIn("privacy_posture", fields)
        self.assertIn("canonical_target", fields)
        self.assertIn("blocked_until", fields)

    def test_red_sources_are_blocked_for_planning_only(self) -> None:
        review = build_source_ingestion_review()
        sources = {source["contract_id"]: source for source in review["sources"]}

        for contract_id in ("SRC-2026-004", "SRC-2026-007"):
            self.assertEqual(sources[contract_id]["ingestion_status"], "blocked")
            self.assertEqual(sources[contract_id]["allowed_use"], "planning_only")
            self.assertEqual(sources[contract_id]["standardization_risk"], "high")
            self.assertFalse(sources[contract_id]["production_ingestion_ready"])

    def test_green_prediction_register_is_controlled_pilot_candidate(self) -> None:
        review = build_source_ingestion_review()
        sources = {source["contract_id"]: source for source in review["sources"]}
        prediction_register = sources["SRC-2026-005"]

        self.assertEqual(prediction_register["ingestion_status"], "pilot_candidate")
        self.assertEqual(prediction_register["allowed_use"], "controlled_pilot_candidate")
        self.assertEqual(prediction_register["standardization_risk"], "low")

    def test_text_review_is_shareable(self) -> None:
        text = render_source_ingestion_review_text(build_source_ingestion_review())

        self.assertIn("Source Ingestion Contract Review", text)
        self.assertIn("production_ingestion_ready=0", text)
        self.assertIn("database_schema_work=deferred", text)
        self.assertIn("[blocked] SRC-2026-004 cohort_outcomes", text)
        self.assertNotIn("{", text)


if __name__ == "__main__":
    unittest.main()
