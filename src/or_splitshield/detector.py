"""Small, explainable detector for transaction structuring."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta
from decimal import Decimal


def detect_structuring(
    transactions: list[dict[str, object]],
    threshold: str = "10000",
    min_count: int = 3,
    window_minutes: int = 60,
) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    limit = Decimal(threshold)
    for transaction in transactions:
        if Decimal(str(transaction["amount"])) < limit:
            grouped[str(transaction["source_account_id"])].append(transaction)

    alerts: list[dict[str, object]] = []
    window = timedelta(minutes=window_minutes)
    for account_id, rows in grouped.items():
        ordered = sorted(rows, key=lambda row: str(row["occurred_at"]))
        for start in range(len(ordered)):
            first_time = datetime.fromisoformat(str(ordered[start]["occurred_at"]))
            selected = []
            for row in ordered[start:]:
                if datetime.fromisoformat(str(row["occurred_at"])) - first_time <= window:
                    selected.append(row)
            total = sum((Decimal(str(row["amount"])) for row in selected), Decimal("0"))
            if len(selected) >= min_count and total >= limit:
                alerts.append(
                    {
                        "account_id": account_id,
                        "rule": "STRUCTURING_WINDOW",
                        "transaction_ids": [str(row["id"]) for row in selected],
                        "total": str(total),
                    }
                )
                break
    return alerts

