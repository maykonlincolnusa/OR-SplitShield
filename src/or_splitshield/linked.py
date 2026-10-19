"""Entity-level structuring from an explicit, user-reviewed ownership mapping."""
from collections import defaultdict
from datetime import timedelta
from decimal import Decimal
from hashlib import sha256

from .validation import instant, integer, money, text, transactions, unique_rows


def detect_linked_structuring(rows, accounts, threshold="10000", min_count=3,
                             window_minutes=60, min_accounts=2):
    limit = money(threshold, "threshold")
    integer(min_count, "min_count", 2)
    integer(min_accounts, "min_accounts", 1)
    integer(window_minutes, "window_minutes", 1, 10080)
    owners = {a["id"]: text(a.get("entity_id"), "entity_id") for a in unique_rows(accounts)}
    grouped = defaultdict(list)
    for row in transactions(rows):
        source, target = row["source_account_id"], row["destination_account_id"]
        if source not in owners or target not in owners:
            raise ValueError("all accounts require explicit ownership mappings")
        # Internal transfers would double-count the same economic movement.
        if owners[source] != owners[target] and Decimal(row["amount"]) < limit:
            grouped[(owners[source], row["currency"])].append(row)
    alerts = []
    for (entity, unit), events in sorted(grouped.items()):
        left, total = 0, Decimal(0)
        sources = defaultdict(int)
        for right, row in enumerate(events):
            total += Decimal(row["amount"])
            sources[row["source_account_id"]] += 1
            while instant(row["occurred_at"]) - instant(events[left]["occurred_at"]) > timedelta(minutes=window_minutes):
                old = events[left]
                total -= Decimal(old["amount"])
                sources[old["source_account_id"]] -= 1
                if not sources[old["source_account_id"]]:
                    del sources[old["source_account_id"]]
                left += 1
            if right - left + 1 >= min_count and total >= limit and len(sources) >= min_accounts:
                selected = events[left:right + 1]
                ids = [r["id"] for r in selected]
                identity = (entity, unit, ids, str(limit), min_count, window_minutes, min_accounts)
                alerts.append({"id": "linked-" + sha256(repr(identity).encode()).hexdigest()[:20],
                               "rule": "LINKED_ACCOUNT_STRUCTURING", "rule_version": "3.0",
                               "entity_id": entity, "account_ids": sorted(sources),
                               "currency": unit, "total": str(total), "transaction_ids": ids,
                               "window_start": selected[0]["occurred_at"],
                               "window_end": selected[-1]["occurred_at"]})
                left, total, sources = right + 1, Decimal(0), defaultdict(int)
    return alerts
