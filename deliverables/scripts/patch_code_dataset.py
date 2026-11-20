#!/usr/bin/env python3
"""Update the code walkthrough for the dataset, the focus domain and the
invariant tests.

The tree in Part D is the reader's map of the repository, and it has to be
right: the corpus is now 46 documents, the focus corpus and the dataset
export are new, and the invariant test suite is a third test file.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "deliverables" / "templates" / "Deliverable_1_PartD_Code.md"

EDITS = [
    (
        "│   ├── build_corpus.py   Fetches and cleans the public corpus\n"
        "│   └── build_benchmark.py Generates the silver-standard benchmark",
        "│   ├── build_corpus.py   Fetches and cleans the public corpus\n"
        "│   ├── build_benchmark.py Generates the silver-standard benchmark\n"
        "│   ├── build_index.py   Builds and caches the retrieval index\n"
        "│   ├── make_focus_corpus.py  Materialises the focus-domain subset\n"
        "│   └── export_dataset.py Exports the corpus with its provenance",
    ),
    (
        "│   └── run_transfer.py   Experiment 4 — cross-category transfer",
        "│   ├── run_transfer.py   Experiment 4 — cross-category transfer\n"
        "│   ├── run_pool_size.py  Experiment 5 — the rerank candidate pool\n"
        "│   └── run_focus_case.py Experiment 6 — the focus-domain case study",
    ),
    (
        "│   ├── corpus/           41 public industrial documents, 6 categories\n"
        "│   └── benchmark/        {{N_QUERIES}} silver queries ({{N_ANSWERABLE}} answerable, {{N_UNANSWERABLE}} unanswerable)",
        "│   ├── corpus/           {{N_DOCUMENTS}} public industrial documents, {{N_CATEGORIES_WORD}} categories\n"
        "│   ├── corpus_focus/     The focus domain alone: {{N_FOCUS_DOCUMENTS}} documents\n"
        "│   ├── benchmark/        {{N_QUERIES}} silver queries ({{N_ANSWERABLE}} answerable, {{N_UNANSWERABLE}} unanswerable)\n"
        "│   └── benchmark_focus/  {{N_FOCUS_QUERIES}} queries on the focus domain",
    ),
    (
        "**The tests.** `impl/tests/` pins down the two places where an inverted\n"
        "condition silently produces plausible-looking but wrong numbers: the rank-fusion\n"
        "properties and the quota's victim selection.",
        "**The tests.** `impl/tests/` pins down the places where an inverted condition or\n"
        "a misdirected filter silently produces plausible-looking but wrong numbers: the\n"
        "rank-fusion properties, the quota's victim selection, and a third file of\n"
        "**invariant tests** that assert what the mechanism predicts — that the category\n"
        "pre-filter restricts *both* retrieval legs, that the reranker only permutes its\n"
        "own pool, that the quota never introduces a chunk from outside its pool, that\n"
        "no document spans two categories, that the calibration is monotone, and that\n"
        "the built index holds no duplicated chunk id. Each of those corresponds to a\n"
        "defect that was actually found and fixed during this work, so the tests are\n"
        "regression tests rather than decoration.",
    ),
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
    print("  updated the code walkthrough")
    return 0


if __name__ == "__main__":
    sys.exit(main())
