#!/usr/bin/env python3
"""Promote the re-measured generator arms into the canonical result file.

**Why the merge is legitimate.** The five arms of the generator-side
comparison are not equally dependent on the quota placement. Four of them
retrieve -- `rag_nogate`, `rag@fitted`, `rag@random`, `rag@transferred` -- so
the placement decides which passages the generator was shown, and they have
to be re-measured. The fifth, `long_context`, does not retrieve: its prompt
is the entire corpus, rendered by `build_long_context`, which walks
`index.chunk_ids` and never touches the retriever, the reranker or the
quota. Its prompt is byte-identical under either placement, so its archived
records are still the right ones and re-running it would spend 36 million
tokens to reproduce them.

So the re-measurement runs the four retrieving arms, and the long-context
arm is carried over from the archive with its provenance recorded.

Usage:
    python3 deliverables/scripts/promote_generator_arms.py --tag rerun
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
IMPL = ROOT / "impl"
RESULTS = IMPL / "results_focus"
ARCHIVE = ROOT / ".snapshot_preswap/results_focus"

RETRIEVING_ARMS = ("rag_nogate", "rag@fitted", "rag@random", "rag@transferred")
PLACEMENT_INDEPENDENT_ARM = "long_context"

sys.path.insert(0, str(IMPL))
sys.path.insert(0, str(IMPL / "experiments"))
os.environ.setdefault("MTP_VARIANT", "focus")


def shipped_placement() -> str:
    from src.config import CONFIG

    return CONFIG.modality.position


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tag", required=True,
                    help="the tag the re-measurement was run under")
    ap.add_argument("--condition", default="cautious")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    base = ("exp8_generation" if args.condition == "cautious"
            else f"exp8_generation_{args.condition}")
    fresh_path = RESULTS / f"{base}_{args.tag}.json"
    archive_path = ARCHIVE / f"{base}.json"

    if not fresh_path.exists():
        print(f"no re-measured file at {fresh_path}")
        return 2

    fresh = json.loads(fresh_path.read_text(encoding="utf-8"))
    if fresh.get("status") != "run":
        print(f"the re-measured file is not a completed run "
              f"(status={fresh.get('status')!r}); nothing to promote")
        return 2

    archived = json.loads(archive_path.read_text(encoding="utf-8"))
    old_records = archived.get("records") or {}
    if PLACEMENT_INDEPENDENT_ARM not in old_records:
        print(f"the archived file has no {PLACEMENT_INDEPENDENT_ARM!r} arm to "
              f"carry over")
        return 2

    got = set((fresh.get("records") or {}))
    if got != set(RETRIEVING_ARMS):
        print(f"the re-measured file holds {sorted(got)}, not the four "
              f"retrieving arms {sorted(RETRIEVING_ARMS)}; refusing to "
              f"promote a partial re-measurement")
        return 2

    merged = dict(fresh)
    records = dict(fresh["records"])
    records[PLACEMENT_INDEPENDENT_ARM] = old_records[PLACEMENT_INDEPENDENT_ARM]
    merged["records"] = records

    arms = dict(fresh.get("arms") or {})
    old_arm = (archived.get("arms") or {}).get(PLACEMENT_INDEPENDENT_ARM)
    if old_arm:
        arms[PLACEMENT_INDEPENDENT_ARM] = old_arm
    merged["arms"] = arms

    merged["retrieval_placement"] = shipped_placement()
    merged["arm_provenance"] = {
        PLACEMENT_INDEPENDENT_ARM: (
            "carried over from the pre-change archive: the arm sends the "
            "whole corpus and does not retrieve, so the quota placement "
            "cannot affect its prompt"),
        **{a: "re-measured under the shipped placement" for a in RETRIEVING_ARMS},
    }

    if args.dry_run:
        print("dry run -- would promote:")
        print("  from:", fresh_path)
        print("  to:  ", RESULTS / f"{base}.json")
        print("  arms:", sorted(records))
        print("  placement stamp:", merged["retrieval_placement"])
        return 0

    target = RESULTS / f"{base}.json"
    shutil.copy2(target, ARCHIVE / f"{base}.superseded_by_{args.tag}.json")
    target.write_text(json.dumps(merged, indent=2), encoding="utf-8")
    print(f"promoted {fresh_path} -> {target}")
    print(f"  arms: {sorted(records)}")
    print(f"  placement stamp: {merged['retrieval_placement']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
