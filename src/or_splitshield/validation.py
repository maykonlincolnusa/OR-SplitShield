"""Strict input contracts for small, standalone financial-crime experiments."""
from __future__ import annotations

import re
from datetime import datetime, timezone
from decimal import Decimal

MAX_ROWS = 10000


def text(value, field="identifier"):
    if not isinstance(value, str) or not value.strip() or len(value) > 200:
        raise ValueError(f"{field} must be a non-empty string of at most 200 characters")
    return value


def integer(value, field, minimum=1, maximum=10000):
    if type(value) is not int or not minimum <= value <= maximum:
        raise ValueError(f"{field} must be an integer between {minimum} and {maximum}")
    return value


def money(value, field="amount", allow_zero=False):
    # Decimal strings avoid binary float rounding; keep sums within Decimal precision.
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]{1,16}(\.[0-9]{1,8})?", value):
        raise ValueError(f"{field} must be a decimal string, up to 16 integer and 8 fractional digits")
    amount = Decimal(value)
    if amount < 0 or (not allow_zero and amount == 0):
        raise ValueError(f"{field} must be positive")
    return amount


def currency(value):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Z]{3}", value):
        raise ValueError("currency must contain three uppercase ASCII letters")
    return value


def instant(value):
    if not isinstance(value, str):
        raise ValueError("timestamp must be an ISO 8601 string")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("timestamp must be an ISO 8601 string") from exc
    if parsed.utcoffset() is None:
        raise ValueError("timestamp must include a timezone")
    return parsed.astimezone(timezone.utc)


def records(value, field="records"):
    if not isinstance(value, list) or len(value) > MAX_ROWS:
        raise ValueError(f"{field} must be a list of at most {MAX_ROWS} objects")
    if any(not isinstance(row, dict) for row in value):
        raise ValueError(f"{field} must contain objects")
    return value


def identifiers(value, field="identifiers"):
    if not isinstance(value, list) or len(value) > MAX_ROWS:
        raise ValueError(f"{field} must be a list")
    result = [text(item, field) for item in value]
    if len(set(result)) != len(result):
        raise ValueError(f"{field} must contain unique identifiers")
    return result


def unique_rows(rows, key="id"):
    records(rows)
    identifiers([row.get(key) for row in rows], key)
    return rows


def transactions(rows):
    result = []
    for row in unique_rows(rows):
        source = text(row.get("source_account_id"), "source_account_id")
        target = text(row.get("destination_account_id"), "destination_account_id")
        if source == target:
            raise ValueError("self transfers are not supported")
        result.append({
            **row,
            "amount": format(money(row.get("amount")), "f"),
            "currency": currency(row.get("currency")),
            "occurred_at": instant(row.get("occurred_at")).isoformat(),
        })
    return sorted(result, key=lambda row: (instant(row["occurred_at"]), row["id"]))
