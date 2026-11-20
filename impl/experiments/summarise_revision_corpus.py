#!/usr/bin/env python3
"""Summarise the two-snapshot revision corpus as a permanent artefact.

The candidate pairs the RO4 evaluation uses are 90 mined paragraphs and
150 retrieval neighbours, so the size of the corpus they were mined from --
948 amended-paragraph pairs across the two snapshots, of which 361 state
different numbers in the two vintages -- is not recoverable from any file
the papers can read. It was printed by the builder's console output, which
is exactly the kind of number that later drifts without anyone noticing.

This script recomputes it from the cached eCFR XML, using the builder's own
alignment and numeric-change functions, and writes it to a result file so
the papers and the write-ups can bind it to a token like every other
measurement.

    python3 impl/experiments/summarise_revision_corpus.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "impl" / "experiments"))

from build_revision_candidates import (  # noqa: E402
    POST_DATE,
    PRE_DATE,
    load_snapshot,
    numbers_changed,
    revision_pairs,
)

OUT = ROOT / "impl" / "results_industrial" / "exp21_revision_corpus_stats.json"


def main() -> int:
    pre = load_snapshot(PRE_DATE)
    post = load_snapshot(POST_DATE)
    rev = revision_pairs(pre, post)
    n_numeric = sum(1 for p in rev
                    if numbers_changed(p["passage_a"], p["passage_b"]))
    doc = {
        "schema": "mtp.revision-corpus-stats/1",
        "pre_date": PRE_DATE,
        "post_date": POST_DATE,
        "n_sections_pre": len(pre),
        "n_sections_post": len(post),
        "n_amended_paragraph_pairs": len(rev),
        "n_pairs_stating_different_numbers": n_numeric,
        "share_stating_different_numbers": n_numeric / max(len(rev), 1),
        "note": (
            "Paragraphs are aligned across the two snapshots by token-set "
            "overlap and kept when the aligned text differs; the numeric "
            "count uses the builder's own numbers_changed test. The "
            "candidate pairs the RO4 evaluation scores are mined from this "
            "corpus by the retriever's signal and are a subset of it."
        ),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    print(f"[revision-corpus] {len(rev)} amended-paragraph pairs, "
          f"{n_numeric} stating different numbers "
          f"({n_numeric / max(len(rev), 1):.1%}) -> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
