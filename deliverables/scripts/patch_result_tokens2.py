#!/usr/bin/env python3
"""Bind the last three measured literals in the guide.

§C.5 quotes the reranking result, §C.5's lesson quotes the MRR change, and
§C.8 quotes the symptom of the rebuild-based quota. All three are
measurements and all three were literals.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "deliverables" / "templates" / "Deliverable_1_Part1_Content.md"

EDITS = [
    ("improved recall@10 from 0.644 to 0.730 (p = 1.3 × 10⁻³), MRR from 0.373 to 0.531\n"
     "and nDCG@10 from 0.431 to 0.580.",
     "improved recall@10 from {{R_C}} to {{R_RERANK}} (p = {{P_CD}}), MRR from\n"
     "{{MRR_C}} to {{MRR_RERANK}} and nDCG@10 from {{NDCG_C}} to {{NDCG_RERANK}}."),
    ("ordering benefit is real and large (MRR 0.368 → 0.528), and ordering is what",
     "ordering benefit is real and large (MRR {{MRR_C}} → {{MRR_RERANK}}), and ordering is what"),
    ("Our first implementation did this, and table recall fell from\n"
     "0.865 to 0.649 — the quota made the system actively worse.",
     "Our first implementation did this, and table recall fell from\n"
     "{{TBL_E}} to {{TBL_F}} — the quota made the system actively worse."),
]


def main() -> int:
    s = TARGET.read_text(encoding="utf-8")
    failures = []
    for old, new in EDITS:
        n = s.count(old)
        if n != 1:
            failures.append(f"count={n} -> {old[:60]!r}")
            continue
        s = s.replace(old, new, 1)
    if failures:
        for f in failures:
            print(f"!! {f}")
        return 1
    TARGET.write_text(s, encoding="utf-8")
    print("  bound the last three measured literals in the guide")
    return 0


if __name__ == "__main__":
    sys.exit(main())
