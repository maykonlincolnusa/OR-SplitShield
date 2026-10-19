"""Validated boundary used by the CLI and HTTP adapter."""
from .detector import detect_structuring
from .linked import detect_linked_structuring


def run(payload):
    if not isinstance(payload, dict) or set(payload) - set(["transactions","options","accounts","action"]):
        raise ValueError("request must be an object containing only documented fields")
    if payload.get("action") == "linked":
        return detect_linked_structuring(payload.get("transactions"), payload.get("accounts"),
                                        **payload.get("options", {}))
    if payload.get("action", "account") != "account" or "accounts" in payload:
        raise ValueError("unknown action or unexpected account mappings")
    return detect_structuring(payload.get('transactions'), **payload.get('options', {}))
