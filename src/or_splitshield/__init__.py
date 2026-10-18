"""Starter package for OR SplitShield."""

from .detector import detect_structuring

__version__ = "0.1.0"


def project_info() -> dict[str, str]:
    return {
        "name": "OR SplitShield",
        "focus": "Explainable transaction-structuring detection",
        "status": "starter",
    }


__all__ = ["detect_structuring", "project_info"]

