import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from scripts.decision_impact_review import impact_status


class DecisionImpactReviewTests(unittest.TestCase):
    def test_positive_readiness_and_placement_with_pending_retention_is_emerging(self) -> None:
        status = impact_status(
            releases=[{"release_status": "released"}],
            evidence=[{"readiness_level": "emerging"}],
            cohorts=[{"placement_rate": 0.694, "retention_90d_rate": None}],
            placement_deltas=[0.093],
            retention_deltas=[],
        )

        self.assertEqual(status, "evidence_emerging")

    def test_positive_signal_requires_no_pending_outcomes(self) -> None:
        status = impact_status(
            releases=[{"release_status": "released"}],
            evidence=[{"readiness_level": "ready"}],
            cohorts=[{"placement_rate": 0.7, "retention_90d_rate": 0.84}],
            placement_deltas=[0.08],
            retention_deltas=[0.04],
        )

        self.assertEqual(status, "positive_signal")

    def test_insufficient_sample_needs_attention(self) -> None:
        status = impact_status(
            releases=[{"release_status": "released"}],
            evidence=[{"readiness_level": "insufficient_sample"}],
            cohorts=[{"placement_rate": None, "retention_90d_rate": None}],
            placement_deltas=[],
            retention_deltas=[],
        )

        self.assertEqual(status, "needs_attention")


if __name__ == "__main__":
    unittest.main()
