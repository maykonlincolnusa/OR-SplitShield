import unittest

from or_splitshield import detect_structuring, project_info


class ProjectSmokeTest(unittest.TestCase):
    def test_project_metadata(self) -> None:
        self.assertEqual(project_info()["status"], "starter")

    def test_detects_explainable_structuring(self) -> None:
        rows = [
            {"id": "1", "source_account_id": "a", "amount": "4000", "occurred_at": "2026-01-01T10:00:00+00:00"},
            {"id": "2", "source_account_id": "a", "amount": "3500", "occurred_at": "2026-01-01T10:10:00+00:00"},
            {"id": "3", "source_account_id": "a", "amount": "3000", "occurred_at": "2026-01-01T10:20:00+00:00"},
        ]
        alerts = detect_structuring(rows)
        self.assertEqual(alerts[0]["transaction_ids"], ["1", "2", "3"])



if __name__ == "__main__":
    unittest.main()

