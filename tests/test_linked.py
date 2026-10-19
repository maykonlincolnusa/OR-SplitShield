from or_splitshield.linked import detect_linked_structuring


def row(identifier, source, target, amount, minute):
    return {"id": identifier, "source_account_id": source,
            "destination_account_id": target, "amount": amount, "currency": "BRL",
            "occurred_at": f"2026-01-01T10:{minute:02d}:00Z"}


def test_aggregates_multiple_accounts_owned_by_same_entity():
    accounts = [{"id": "a1", "entity_id": "e1"}, {"id": "a2", "entity_id": "e1"},
                {"id": "x", "entity_id": "external"}]
    rows = [row("1", "a1", "x", "4000", 0), row("2", "a2", "x", "3500", 5),
            row("3", "a1", "x", "3000", 10)]
    alert = detect_linked_structuring(rows, accounts)[0]
    assert alert["entity_id"] == "e1"
    assert alert["account_ids"] == ["a1", "a2"]


def test_does_not_count_internal_transfer():
    accounts = [{"id": "a1", "entity_id": "e1"}, {"id": "a2", "entity_id": "e1"}]
    assert detect_linked_structuring([row("1", "a1", "a2", "9000", 0)], accounts) == []
