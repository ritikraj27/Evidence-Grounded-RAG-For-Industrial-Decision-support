#!/usr/bin/env python3
"""Re-label the claims a judge failed to label, and merge.

**Why this exists.** A judge that is a reasoning model can spend its whole
output budget thinking and return no text. The annotator records that as an
unlabelled claim and moves on, which is right — an empty completion is
neither a label nor a refusal — but it leaves the claim without a reference,
and it leaves the reader-to-reader agreement computed over a smaller and
possibly non-random subset of the claims.

The fix is to give the same judge more room: re-run only the claims it
failed on, at a larger output budget, and merge the result into its label
file. The claims it already labelled are untouched, so the merge cannot
change a label the judge did make.

Usage:
    python scripts/relabel_failed.py \
        --input  ../results_industrial/exp21_judge_input_gold.json \
        --labels ../results_industrial/exp21_judge_b_model_labels_gold.json \
        --out    ../results_industrial/exp21_judge_b_model_labels_gold.json \
        --max-tokens 4096
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "scripts"))

os.environ.setdefault("MTP_VARIANT", "industrial")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", required=True, help="the judge sheet")
    ap.add_argument("--labels", required=True, help="the label file to complete")
    ap.add_argument("--out", required=True, help="where to write the merged file")
    ap.add_argument("--max-tokens", type=int, default=4096)
    args = ap.parse_args()

    from label_claim_bands_model import annotate, _config

    sheet = json.loads(Path(args.input).read_text(encoding="utf-8"))
    doc = json.loads(Path(args.labels).read_text(encoding="utf-8"))
    have = dict(doc.get("labels") or {})
    missing = [it for it in sheet["items"] if it["key"] not in have]
    print(f"[relabel] {len(have)} already labelled, {len(missing)} to retry")
    if not missing:
        print("[relabel] nothing to do")
        return 0

    cfg = _config()
    cfg["max_tokens"] = args.max_tokens

    out = annotate(missing, sheet["rubric"], cfg)
    added = 0
    for key, label in (out.get("labels") or {}).items():
        if key not in have:
            have[key] = label
            added += 1
    merged = dict(doc)
    merged["labels"] = have
    merged["unlabelled_keys"] = sorted(
        set(doc.get("unlabelled_keys") or []) - set(have))
    merged["relabelled"] = {
        "n_retried": len(missing),
        "n_recovered": added,
        "max_tokens": args.max_tokens,
    }
    Path(args.out).write_text(json.dumps(merged, indent=2), encoding="utf-8")
    print(f"[relabel] recovered {added} of {len(missing)}; "
          f"{len(have)} labelled in total -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
