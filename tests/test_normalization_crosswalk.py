import unittest

from decision_spine.services.normalization_crosswalk import (
    build_normalization_crosswalk,
    render_normalization_crosswalk_text,
)


class NormalizationCrosswalkTests(unittest.TestCase):
    def test_crosswalk_summarizes_current_normalization_states(self) -> None:
        crosswalk = build_normalization_crosswalk()
        summary = crosswalk["summary"]

        self.assertEqual(summary["role_count"], 3)
        self.assertEqual(summary["competency_count"], 5)
        self.assertEqual(summary["aligned_for_planning_count"], 1)
        self.assertEqual(summary["evidence_pending_count"], 1)
        self.assertEqual(summary["implementation_pending_count"], 1)
        self.assertEqual(summary["suppressed_evidence_count"], 1)
        self.assertEqual(summary["monitor_only_count"], 1)
        self.assertEqual(summary["needs_mapping_count"], 0)
        self.assertEqual(summary["ontology_schema_work"], "deferred")

    def test_crosswalk_maps_competency_to_decision_release_pedagogy_evidence_and_outcome(self) -> None:
        crosswalk = build_normalization_crosswalk()
        rows = {row["competency_id"]: row for row in crosswalk["rows"]}
        builder = rows["COMP-2026-001"]

        self.assertEqual(builder["crosswalk_state"], "aligned_for_planning")
        self.assertEqual(builder["signal_ids"], ["SIG-2026-001"])
        self.assertEqual(builder["decision_ids"], ["DEC-2026-001"])
        self.assertEqual(builder["release_ids"], ["REL-2026-001"])
        self.assertEqual(builder["pedagogy_ids"], ["PED-2026-001"])
        self.assertEqual(builder["evidence_ids"], ["EVID-2026-001"])
        self.assertEqual(builder["outcome_cohort_ids"], ["COH-2026-03-BUILDER"])

    def test_crosswalk_flags_pending_suppressed_and_monitor_only_items(self) -> None:
        crosswalk = build_normalization_crosswalk()
        rows = {row["competency_id"]: row for row in crosswalk["rows"]}

        self.assertEqual(rows["COMP-2026-002"]["crosswalk_state"], "evidence_pending")
        self.assertIn("evidence_pending", rows["COMP-2026-002"]["ambiguity_flags"])
        self.assertEqual(rows["COMP-2026-003"]["crosswalk_state"], "implementation_pending")
        self.assertIn("release_not_released", rows["COMP-2026-003"]["ambiguity_flags"])
        self.assertEqual(rows["COMP-2026-004"]["crosswalk_state"], "suppressed_evidence")
        self.assertIn("evidence_suppressed", rows["COMP-2026-004"]["ambiguity_flags"])
        self.assertEqual(rows["COMP-2026-005"]["crosswalk_state"], "monitor_only")
        self.assertIn("monitor_not_standalone", rows["COMP-2026-005"]["ambiguity_flags"])

    def test_role_summary_keeps_role_cluster_owner_context(self) -> None:
        crosswalk = build_normalization_crosswalk()
        roles = {role["role_archetype"]: role for role in crosswalk["role_summaries"]}

        self.assertEqual(roles["Builder"]["competency_count"], 1)
        self.assertEqual(roles["Scaler"]["competency_count"], 2)
        self.assertEqual(roles["Prototyper"]["competency_count"], 2)
        self.assertIn("Assessment Ops", roles["Scaler"]["owners"])
        self.assertIn("workflow_asset_quality", roles["Prototyper"]["clusters"])

    def test_text_crosswalk_is_shareable(self) -> None:
        text = render_normalization_crosswalk_text(build_normalization_crosswalk())

        self.assertIn("Normalization Crosswalk Review", text)
        self.assertIn("ontology_schema_work=deferred", text)
        self.assertIn("[suppressed_evidence] COMP-2026-004", text)
        self.assertNotIn("{", text)


if __name__ == "__main__":
    unittest.main()
