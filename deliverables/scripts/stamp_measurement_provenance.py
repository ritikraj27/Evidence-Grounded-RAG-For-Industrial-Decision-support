#!/usr/bin/env python3
"""Stamp a measurement with the retrieval configuration it was taken under.

The measurement scripts write this field themselves, so a fresh run is
self-describing. This tool exists for the files that were *not* re-measured
-- the ones restored from the pre-change archive -- so that the build can
tell them apart from the current ones instead of having to be told.

Usage:
    python3 deliverables/scripts/stamp_measurement_provenance.py \\
        --placement post_rerank impl/results_focus/exp8_generation_answering.json
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--placement", required=True,
                    choices=["pre_rerank", "post_rerank"],
                    help="the placement the measurement was taken under")
    ap.add_argument("paths", nargs="+")
    args = ap.parse_args()

    for raw in args.paths:
        p = pathlib.Path(raw)
        if not p.is_absolute():
            p = ROOT / raw
        if not p.exists():
            print(f"  missing, skipped: {p}")
            continue
        try:
            doc = json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"  unreadable, skipped: {p} ({e})")
            continue
        if not isinstance(doc, dict):
            print(f"  not a JSON object, skipped: {p}")
            continue
        before = doc.get("retrieval_placement")
        doc["retrieval_placement"] = args.placement
        # The same shape the measurement scripts write, so a stamped file is
        # comparable with a freshly measured one.
        p.write_text(json.dumps(doc, indent=2, default=float), encoding="utf-8")
        print(f"  stamped {p.relative_to(ROOT) if p.is_relative_to(ROOT) else p}"
              f"  ({before!r} -> {args.placement!r})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
