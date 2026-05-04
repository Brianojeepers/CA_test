import unittest

from decision_spine.services.pilot_request_pack import build_pilot_request_pack, render_pilot_request_pack_markdown


class PilotRequestPackTests(unittest.TestCase):
    def test_pack_represents_all_current_v02_field_requests(self) -> None:
        pack = build_pilot_request_pack()

        self.assertEqual(pack["summary"]["request_count"], 18)
        self.assertGreaterEqual(pack["summary"]["owner_count"], 1)
        self.assertEqual(sum(group["request_count"] for group in pack["owner_groups"]), 18)

    def test_learner_fields_are_privacy_review_requests(self) -> None:
        pack = build_pilot_request_pack()
        requests = {item["field"]: item for item in pack["requests"]}

        self.assertTrue(requests["demonstrated_proficiency"]["blocked"])
        self.assertEqual(requests["demonstrated_proficiency"]["request_priority"], "privacy_review")
        self.assertTrue(requests["proficiency_gap_score"]["blocked"])
        self.assertEqual(requests["proficiency_gap_score"]["request_priority"], "privacy_review")

    def test_each_request_has_owner_purpose_status_and_capability(self) -> None:
        pack = build_pilot_request_pack()

        for request in pack["requests"]:
            self.assertTrue(request["owner"])
            self.assertTrue(request["purpose"])
            self.assertTrue(request["status"])
            self.assertTrue(request["capability_label"])

    def test_markdown_is_owner_ready(self) -> None:
        markdown = render_pilot_request_pack_markdown(build_pilot_request_pack())

        self.assertIn("# v0.2 Pilot Data Request Pack", markdown)
        self.assertIn("## Market Intelligence", markdown)
        self.assertIn("Privacy review required", markdown)
        self.assertNotIn("{", markdown)


if __name__ == "__main__":
    unittest.main()
