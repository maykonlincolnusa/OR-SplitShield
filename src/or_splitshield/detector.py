"""Currency-isolated rolling-window structuring indicators."""
from __future__ import annotations

from collections import defaultdict
from datetime import timedelta
from decimal import Decimal
from hashlib import sha256

from .validation import instant, integer, money, transactions

RULE_VERSION = "2.0"


def detect_structuring(transactions_input, threshold="10000", min_count=3, window_minutes=60):
    limit = money(threshold, "threshold")
    integer(min_count, "min_count", 2)
    integer(window_minutes, "window_minutes", 1, 10080)
    grouped = defaultdict(list)
    for row in transactions(transactions_input):
        if Decimal(row["amount"]) < limit:
            grouped[(row["source_account_id"], row["currency"])].append(row)
    alerts = []
    for (account, unit), rows in sorted(grouped.items()):
        left = 0
        total = Decimal("0")
        for right, row in enumerate(rows):
            total += Decimal(row["amount"])
            while instant(row["occurred_at"]) - instant(rows[left]["occurred_at"]) > timedelta(minutes=window_minutes):
                total -= Decimal(rows[left]["amount"])
                left += 1
            if right - left + 1 >= min_count and total >= limit:
                selected = rows[left:right + 1]
                ids = [item["id"] for item in selected]
                identity = sha256(repr((account, unit, ids, threshold, min_count, window_minutes)).encode()).hexdigest()[:20]
                alerts.append({
                    "id": "split-" + identity, "account_id": account, "currency": unit,
                    "rule": "STRUCTURING_WINDOW", "rule_version": RULE_VERSION,
                    "transaction_ids": ids, "total": format(total, "f"),
                    "window_start": selected[0]["occurred_at"],
                    "window_end": selected[-1]["occurred_at"],
                    "explanation": f"{len(ids)} sub-threshold transfers reach {threshold} {unit} within {window_minutes} minutes.",
                })
                # Emit disjoint evidence sets; subsequent activity can create another alert.
                left = right + 1
                total = Decimal("0")
    return alerts

