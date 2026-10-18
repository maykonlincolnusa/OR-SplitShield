"""Validated boundary used by the CLI and HTTP adapter."""
from .detector import detect_structuring


def run(payload):
    if not isinstance(payload, dict) or set(payload) - set(["transactions","options"]):
        raise ValueError("request must be an object containing only documented fields")
    return detect_structuring(payload.get('transactions'), **payload.get('options', {}))
