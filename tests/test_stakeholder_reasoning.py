import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from scripts.delivery_window_review import delivery_status
from scripts.talent_profile_signals import profile_status
from scripts.training_offer_inputs import offer_readiness


class StakeholderReasoningTests(unittest.TestCase):
    def test_suppressed_evidence_blocks_active_profile_guidance(self) -> None:
        status = profile_status(
            {"status": "green"},
            [{"release_status": "released"}],
            [{"competency_id": "COMP-1"}],
            {
                "COMP-1": [
                    {"readiness_level": "emerging", "suppression_applied": True},
                ]
            },
        )

        self.assertEqual(status, "released_but_evidence_pending")

    def test_pending_readiness_blocks_training_offer_readiness(self) -> None:
        readiness = offer_readiness(
            {"status": "green"},
            [{"release_status": "released"}],
            [{"competency_id": "COMP-1"}],
            {
                "COMP-1": [
                    {"readiness_level": "pending", "suppression_applied": False},
                ]
            },
        )

        self.assertEqual(readiness, "validated_but_readiness_pending")

    def test_release_after_start_before_credential_needs_timing_review(self) -> None:
        status = delivery_status(
            {
                "release_status": "released",
                "release_date": "2026-04-23",
            },
            {
                "cohort_start_date": "2026-04-06",
                "credential_issued_date": "2026-05-22",
            },
        )

        self.assertEqual(status, "in_cohort_timing_review")

    def test_release_after_credential_is_late_for_credential_window(self) -> None:
        status = delivery_status(
            {
                "release_status": "released",
                "release_date": "2026-06-01",
            },
            {
                "cohort_start_date": "2026-04-06",
                "credential_issued_date": "2026-05-22",
            },
        )

        self.assertEqual(status, "late_for_credential_window")


if __name__ == "__main__":
    unittest.main()
