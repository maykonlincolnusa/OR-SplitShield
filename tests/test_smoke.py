import unittest

from or_splitshield import detect_structuring, project_info


def tx(identifier, amount, currency="BRL", minute=0):
    return {"id": identifier, "source_account_id": "a", "destination_account_id": "b",
            "amount": amount, "currency": currency,
            "occurred_at": f"2026-01-01T10:{minute:02d}:00+00:00"}


class ProjectTest(unittest.TestCase):
    def test_detects_explainable_structuring(self):
        alerts = detect_structuring([tx("1", "4000"), tx("2", "3500", minute=10),
                                     tx("3", "3000", minute=20)])
        self.assertEqual(alerts[0]["transaction_ids"], ["1", "2", "3"])
        self.assertEqual(alerts[0]["currency"], "BRL")
        self.assertEqual(project_info()["status"], "reference-prototype")

    def test_does_not_mix_currencies(self):
        rows = [tx("1", "4000", "BRL"), tx("2", "3500", "USD", 10), tx("3", "3000", "BRL", 20)]
        self.assertEqual(detect_structuring(rows), [])

    def test_rejects_float_money(self):
        with self.assertRaises(ValueError):
            detect_structuring([tx("1", 4000.0), tx("2", "3500", minute=1), tx("3", "3000", minute=2)])


if __name__ == "__main__":
    unittest.main()
