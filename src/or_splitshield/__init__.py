"""Public API for OR SplitShield."""

from .detector import detect_structuring

__version__ = "0.2.0"


def project_info() -> dict[str, str]:
    return {
        "name": "OR SplitShield",
        "focus": "Explainable transaction-structuring detection",
        "status": "reference-prototype",
    }


__all__ = ["detect_structuring", "project_info"]

