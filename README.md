# OR SplitShield

Explainable rolling-window indicators for transaction structuring or smurfing hypotheses.

## Why it matters

Repeated sub-threshold transfers can be missed when each payment is reviewed separately. This project groups activity by source account and currency, applies a bounded rolling window, and returns the exact evidence behind every alert.

## Current capabilities

- Configurable threshold, minimum count, and time window.
- Exact decimal arithmetic and strict rejection of floating-point money.
- Currency isolation and stable evidence-linked alert IDs.
- Deterministic processing and disjoint evidence sets.
- Human-readable explanations and versioned rules.
- Entity-level aggregation across explicitly mapped accounts, excluding internal transfers.
- CLI, optional authenticated API, Docker image, and CI.

## Run

```sh
python -m pip install -e '.[dev,api]'
python -m or_splitshield --demo
pytest -q && ruff check src tests
```

API: set `OR_API_KEY` to at least 16 characters, run `uvicorn or_splitshield.api:create_app --factory`, then POST `examples/request.json` to `/v1/analyze`.

## Limitations and roadmap

Set `action` to `linked` and supply reviewed account-to-entity mappings for linked-account analysis. Thresholds are demonstration settings, not regulatory advice. The prototype has no customer segmentation, channel logic, event-time streaming, threshold governance, or false-positive measurement. Next steps are policy packs, cohort-specific thresholds, late-event handling, counterparty and channel dimensions, and feedback capture.
