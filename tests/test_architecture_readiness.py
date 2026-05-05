import unittest

from decision_spine.services.architecture_readiness import (
    build_architecture_readiness_review,
    render_architecture_readiness_text,
)


class ArchitectureReadinessTests(unittest.TestCase):
    def test_review_covers_target_architecture_layers(self) -> None:
        review = build_architecture_readiness_review()
        layers = {layer["layer"] for layer in review["layers"]}

        self.assertEqual(review["summary"]["layer_count"], 8)
        self.assertEqual(
            layers,
            {
                "signal_ingestion",
                "normalization",
                "intelligence",
                "decision",
                "activation",
                "governance_cadence",
                "observability_trust",
                "stakeholder_experience",
            },
        )

    def test_review_keeps_database_work_deferred(self) -> None:
        review = build_architecture_readiness_review()

        self.assertEqual(review["summary"]["database_schema_work"], "deferred")
        self.assertIn("horizontally", review["summary"]["recommended_posture"])
        self.assertGreaterEqual(review["rating"]["score"], 8)

    def test_every_layer_has_horizontal_next_step_and_deferred_vertical_work(self) -> None:
        review = build_architecture_readiness_review()

        for layer in review["layers"]:
            self.assertTrue(layer["horizontal_next_step"].strip())
            self.assertTrue(layer["defer_vertical_work"].strip())
            self.assertIn(layer["readiness"], {"covered", "partial", "thin", "missing"})

    def test_text_review_is_shareable(self) -> None:
        text = render_architecture_readiness_text(build_architecture_readiness_review())

        self.assertIn("Architecture Readiness Review", text)
        self.assertIn("database_schema_work=deferred", text)
        self.assertIn("Stakeholder experience layer", text)
        self.assertNotIn("{", text)


if __name__ == "__main__":
    unittest.main()
