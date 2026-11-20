#!/usr/bin/env python3
"""Experiment 5 -- the rerank candidate-pool sweep.

The headline finding of Experiment 1 is that a cross-encoder's effect on recall
is governed by how many candidates it is shown relative to how many the final
context keeps. That claim deserves a curve rather than a single comparison,
because "a top-50 pool helps and a top-10 pool does not" is an anecdote unless
the intermediate points are measured too.

For each pool size we report the same retrieval metrics as Experiment 1. The
interesting shape is the recall curve: it should rise with pool size and then
flatten, because a reranker cannot recover a chunk it was never shown, and
because a larger pool also means more distractors for the final top-k cut.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import (  # noqa: E402
    RESULTS_DIR,
    load_benchmark,
    load_index,
    markdown_table,
    write_result,
)
from src.evaluate import evaluate_retrieval  # noqa: E402
from src.config import CONFIG  # noqa: E402
from src.pipeline import Framework  # noqa: E402

SEED = 20261118
POOL_SIZES = [5, 10, 20, 50, 100]


def main() -> int:
    index = load_index()
    bench = load_benchmark()
    fw = Framework(index)

    # The unanswerable queries have empty gold sets, so they contribute
    # nothing to recall, MRR or nDCG -- but each one still costs a
    # cross-encoder pass over its candidate pool. On a corpus where the
    # unanswerable class is the larger half, skipping them is a large
    # saving and changes no number. It is opt-in so that the shipped
    # behaviour is unchanged.
    answerable_only = "--answerable-only" in sys.argv
    queries = [q for q in bench["queries"] if q["gold"]] if answerable_only \
        else bench["queries"]
    print(f"[exp5] {len(queries)} queries "
          f"({'answerable only' if answerable_only else 'all'})", flush=True)

    results = []
    for size in POOL_SIZES:
        print(f"[exp5] rerank pool = {size} ...", flush=True)
        runs, rels, grades, mod_rels = [], [], [], []
        for q in queries:
            gold = set(q["gold"])
            trace = fw.retrieve(
                q["query"],
                category=q["category"] if q["category"] != "unanswerable" else None,
                apply_quota=False,
                apply_rerank=True,
                rerank_pool=size,
            )
            # The full reranked ranking, so Recall@20 is a real measurement
            # rather than an artefact of the ten-chunk final context.
            ranked = trace.reranked_full or trace.reranked or trace.fused
            runs.append(ranked)
            rels.append(gold)
            grades.append({g: (3.0 if q["family"] == "table_lookup" else 1.0)
                           for g in gold})
            mod_rels.append({m: {g for g in gold
                                 if fw.index.modality_of.get(g, "text") == m}
                              for m in ("text", "table")})
        ev = evaluate_retrieval(runs, rels, grades, fw.index.modality_of, mod_rels)
        row = {"pool_size": size, **ev.to_dict()}
        results.append(row)
        print(f"[exp5]   pool={size}: R@10={ev.recall_at_10:.3f} "
              f"R@20={ev.recall_at_20:.3f} MRR={ev.mrr:.3f} "
              f"nDCG@10={ev.ndcg_at_10:.3f}", flush=True)

    write_result("exp5_pool_size", {"seed": SEED, "pool_sizes": POOL_SIZES,
                                     "results": results,
                                     "retrieval_placement": CONFIG.modality.position})

    rows = [[f"{r['pool_size']}", f"{r['recall@10']:.3f}", f"{r['recall@20']:.3f}",
             f"{r['mrr']:.3f}", f"{r['nDCG@10']:.3f}",
             f"{r['modality_recall'].get('table', float('nan')):.3f}"]
            for r in results]
    table = markdown_table(
        ["Rerank pool", "R@10", "R@20", "MRR", "nDCG@10", "Tbl R@10"], rows)
    (RESULTS_DIR / "exp5_pool_size.md").write_text(
        "# Experiment 5 -- Rerank candidate-pool sweep\n\n" + table + "\n",
        encoding="utf-8")
    print(f"[exp5] wrote {RESULTS_DIR / 'exp5_pool_size.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
