"""Run a standalone JSON demonstration or process a local request."""
from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from pathlib import Path

from .demo import DEMO
from .runner import run


def main(argv=None):
    parser = argparse.ArgumentParser(description=__package__ + " independent prototype")
    inputs = parser.add_mutually_exclusive_group(required=True)
    inputs.add_argument("--demo", action="store_true")
    inputs.add_argument("--input", type=Path, help="JSON request file")
    parser.add_argument("--format", choices=("json", "csv"), default="json")
    args = parser.parse_args(argv)
    try:
        if args.demo:
            payload = DEMO
        else:
            with args.input.open("rb") as stream:
                content = stream.read(2_000_001)
            if len(content) > 2_000_000:
                raise ValueError("request exceeds the 2 MB limit")
            payload = json.loads(content)
        result = run(payload)
        if args.format == "csv":
            if __package__ != "or_aml_simulator":
                raise ValueError("CSV export is supported only by OR AML Simulator")
            buffer = io.StringIO()
            rows = result["transactions"]
            writer = csv.DictWriter(buffer, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
            sys.stdout.write(buffer.getvalue())
        else:
            print(json.dumps({"module": __package__, "schema_version": "2.0", "result": result},
                             indent=2, sort_keys=True, allow_nan=False))
    except (ValueError, TypeError, KeyError, OSError, RecursionError):
        print("Invalid request or unreadable input; check the documented input contract.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
