import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from scripts.validate_data import validate_all


class ValidateDataTests(unittest.TestCase):
    def test_future_pending_release_cohort_is_warning_not_error(self) -> None:
        result = validate_all()

        self.assertTrue(result.ok)
        self.assertIn(
            "releases.json:REL-2026-003:cohort_id: future cohort / no outcomes yet: 'COH-2026-06-SCALER'",
            result.warnings,
        )


if __name__ == "__main__":
    unittest.main()
