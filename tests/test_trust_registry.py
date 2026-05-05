import unittest

from decision_spine.services.trust_registry import build_trust_registry, render_trust_registry_text


class TrustRegistryTests(unittest.TestCase):
    def test_registry_summarizes_current_source_contract_posture(self) -> None:
        registry = build_trust_registry()
        summary = registry["summary"]

        self.assertEqual(summary["source_contract_count"], 7)
        self.assertEqual(summary["green_source_count"], 1)
        self.assertEqual(summary["amber_source_count"], 4)
        self.assertEqual(summary["red_source_count"], 2)
        self.assertEqual(summary["decision_grade_surface_count"], 0)

    def test_evidence_surfaces_inherit_privacy_blockers(self) -> None:
        registry = build_trust_registry()
        surfaces = {surface["surface_id"]: surface for surface in registry["surfaces"]}

        self.assertEqual(surfaces["monthly_packet"]["trust_status"], "privacy_blocked")
        self.assertEqual(surfaces["monthly_packet"]["stakeholder_confidence"], "low")
        self.assertIn("SRC-2026-004", surfaces["monthly_packet"]["source_contract_ids"])
        self.assertIn("SRC-2026-007", surfaces["monthly_packet"]["source_contract_ids"])

    def test_control_surfaces_are_planning_ready_not_decision_grade(self) -> None:
        registry = build_trust_registry()
        surfaces = {surface["surface_id"]: surface for surface in registry["surfaces"]}

        self.assertEqual(surfaces["schema_gap_workbench"]["trust_status"], "planning_ready")
        self.assertFalse(surfaces["schema_gap_workbench"]["decision_grade"])
        self.assertIn("schema", surfaces["schema_gap_workbench"]["next_trust_action"])

    def test_priority_actions_include_red_privacy_contracts_first(self) -> None:
        registry = build_trust_registry()
        actions = registry["priority_trust_actions"]

        self.assertEqual(actions[0]["severity"], "red")
        self.assertEqual(actions[1]["severity"], "red")
        self.assertEqual({actions[0]["contract_id"], actions[1]["contract_id"]}, {"SRC-2026-004", "SRC-2026-007"})

    def test_text_registry_is_shareable(self) -> None:
        text = render_trust_registry_text(build_trust_registry())

        self.assertIn("Trust and Source Coverage Registry", text)
        self.assertIn("decision_grade_surfaces=0", text)
        self.assertIn("[privacy_blocked] Monthly council packet", text)
        self.assertNotIn("{", text)


if __name__ == "__main__":
    unittest.main()
