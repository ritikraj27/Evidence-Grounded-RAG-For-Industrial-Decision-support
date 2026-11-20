#!/usr/bin/env python3
"""Experiment 22 -- the soft prior, and what the hard pre-filter costs.

Threat **T1** in `research/08_direction_check.md` §4.0 said the category
pre-filter cost 7.7 Recall@10 points on the corpus the project then had, and
that the hypothesis had to be re-stated as a negative result *and the fix
tested*: "replace the hard filter with a soft prior (e.g. a category-boosted
RRF term) and report whether it recovers the [lost] points while keeping the
cross-category benefit. If it does not, the negative result stands and
should be the claim."

The hypothesis was re-stated and the cost was measured. **The repair was
never tried.** This experiment tries it.

Five configurations are compared on the same queries, with the same corpus,
the same generator-free retrieval stack and the same scorer:

    no_category        neither the hard filter nor a prior -- the control
    hard_filter       the shipped configuration: the category pre-filter
    soft_prior_w0.25  the whole corpus stays in the pool and the in-category
    soft_prior_w0.5   chunks are promoted in the fused ranking by an extra
    soft_prior_w1.0   reciprocal-rank-fusion term of that weight

The soft prior differs from the hard filter in one way that matters and is
the whole of the proposal: under the hard filter a chunk outside the
category **cannot be retrieved at all**, and under the prior it can -- it is
only demoted. So the prior can recover a recall the filter destroys, if the
filter ever destroys one.

Two things are reported for each configuration: the metrics, and the paired
tests against the shipped configuration. The unanswerable questions are
excluded, because the pre-filter is only meaningful for a query with a gold
chunk: an unanswerable query has no gold, and filtering it would be
meaningless. They contribute nothing to a paired test, since every
configuration scores them identically.

Usage:
    python impl/experiments/run_soft_prior.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import (  # noqa: E402
    load_benchmark,
    load_index,
    markdown_table,
    write_result,
)
from src.evaluate import evaluate_retrieval  # noqa: E402
from src.config import CONFIG  # noqa: E402
from src.pipeline import Framework  # noqa: E402
from src.stats import cliffs_delta, wilcoxon_signed_rank  # noqa: E402

SEED = 20261118

#: The configurations compared. `category_prior` is the weight of the extra
#: RRF term; 0.0 with `use_filter` is the control, and the shipped
#: configuration is the hard filter.
CONFIGS = [
    ("no_category", False, 0.0,
     "neither the hard filter nor a prior (control)"),
    ("hard_filter", True, 0.0,
     "the shipped configuration: the category pre-filter"),
    ("soft_prior_w0.25", False, 0.25,
     "soft prior, weight 0.25 of an extra RRF term"),
    ("soft_prior_w0.5", False, 0.5,
     "soft prior, weight 0.5 of an extra RRF term"),
    ("soft_prior_w1.0", False, 1.0,
     "soft prior, weight 1.0 -- exactly one extra RRF list"),
]


def _mrr_at(ranked: list[str], gold: set[str]) -> float:
    for i, cid in enumerate(ranked, start=1):
        if cid in gold:
            return 1.0 / i
    return 0.0


def _ndcg_at(ranked: list[str], gold: set[str], k: int = 10) -> float:
    dcg = sum((1.0 / np.log2(i + 1))
              for i, cid in enumerate(ranked[:k], start=1) if cid in gold)
    ideal = sum((1.0 / np.log2(i + 1))
                for i in range(1, min(len(gold), k) + 1))
    return dcg / ideal if ideal else 0.0


def run_config(fw, bench, name, use_filter, prior, queries):
    """One configuration over the answerable queries."""
    runs, relevances, grades, mod_rel = [], [], [], []
    per_query_recall, per_query_mrr, per_query_ndcg = [], [], []
    n_out_of_category_gold = 0
    for q in queries:
        gold = set(q["gold"])
        category = q["category"] if use_filter or prior > 0 else None
        trace = fw.retrieve(
            q["query"],
            category=category,
            apply_quota=False,
            apply_rerank=True,
            use_dense=True,
            use_lexical=True,
            category_prior=prior,
        )
        ranked = trace.reranked_full or trace.reranked or trace.fused
        runs.append(ranked)
        relevances.append(gold)
        grades.append({g: (3.0 if q["family"] == "table_lookup" else 1.0)
                       for g in gold})
        mod_rel.append({m: {g for g in gold
                            if fw.index.modality_of.get(g, "text") == m}
                        for m in ("text", "table")})
        per_query_recall.append(len(set(ranked[:10]) & gold) / len(gold))
        per_query_mrr.append(_mrr_at(ranked, gold))
        per_query_ndcg.append(_ndcg_at(ranked, gold))
        # Does the gold chunk sit outside the question's own category? If it
        # does, the hard filter cannot retrieve it and the soft prior can.
        if any(fw.index.category_of.get(g) != q["category"] for g in gold):
            n_out_of_category_gold += 1
    return {
        "name": name,
        "eval": evaluate_retrieval(runs, relevances, grades,
                                   fw.index.modality_of, mod_rel),
        "per_query_recall": per_query_recall,
        "per_query_mrr": per_query_mrr,
        "per_query_ndcg": per_query_ndcg,
        "n_out_of_category_gold": n_out_of_category_gold,
    }


def main() -> int:
    print("[exp22] loading ...", flush=True)
    index = load_index()
    bench = load_benchmark()
    fw = Framework(index)
    queries = [q for q in bench["queries"] if q["gold"]]
    print(f"[exp22] {len(queries)} answerable queries over "
          f"{index.stats.get('n_chunks', '?')} chunks, "
          f"{index.stats.get('n_categories', '?')} categories", flush=True)

    results = {}
    for name, use_filter, prior, label in CONFIGS:
        print(f"[exp22] {name} ...", flush=True)
        results[name] = run_config(fw, bench, name, use_filter, prior, queries)
        r = results[name]["eval"]
        print(f"[exp22] {name}: R@10={r.recall_at_10:.4f} "
              f"R@20={r.recall_at_20:.4f} MRR={r.mrr:.4f} "
              f"nDCG@10={r.ndcg_at_10:.4f}", flush=True)

    # --- the paired tests ---------------------------------------------
    comparisons = []
    for name, _uf, _p, _l in CONFIGS:
        if name == "hard_filter":
            continue
        a = results["hard_filter"]
        b = results[name]
        ra, rb = a["per_query_recall"], b["per_query_recall"]
        w = wilcoxon_signed_rank(ra, rb)
        entry = {
            "comparison": f"hard_filter -> {name}",
            "mean_recall_a": float(np.mean(ra)),
            "mean_recall_b": float(np.mean(rb)),
            "delta": float(np.mean(rb) - np.mean(ra)),
            "wilcoxon": w.to_dict(),
            "cliffs_delta": cliffs_delta(np.array(ra), np.array(rb)),
        }
        for key, label2 in (("per_query_mrr", "mrr"),
                            ("per_query_ndcg", "ndcg")):
            ma, mb = a[key], b[key]
            if len(ma) == len(mb) and len(ma) > 1:
                entry[f"wilcoxon_{label2}"] = wilcoxon_signed_rank(ma, mb).to_dict()
                entry[f"delta_{label2}"] = float(np.mean(mb) - np.mean(ma))
        comparisons.append(entry)
        print(f"[exp22] hard_filter -> {name}: dR@10={entry['delta']:+.4f} "
              f"p={w.p_value:.4g} d_z={w.effect_size:+.3f} | "
              f"dMRR={entry.get('delta_mrr', float('nan')):+.4f} "
              f"p={entry.get('wilcoxon_mrr', {}).get('p_value', float('nan')):.4g}",
              flush=True)

    payload = {
        "seed": SEED,
        "question": ("does a soft prior recover the recall the hard "
                     "category pre-filter costs, while keeping the ordering "
                     "benefit the filter gives?"),
        "n_queries": len(queries),
        "n_out_of_category_gold": results["hard_filter"][
            "n_out_of_category_gold"],
        "note": ("the answerable questions only: an unanswerable question has "
                 "no gold chunk, so the pre-filter has nothing to act on and "
                 "every configuration scores it identically"),
        "systems": {},
        "comparisons": comparisons,
    }
    for name, use_filter, prior, label in CONFIGS:
        r = results[name]
        payload["systems"][name] = {
            "label": label,
            "hard_filter": use_filter,
            "category_prior": prior,
            "eval": {k: (float(v) if isinstance(v, (int, float)) else v)
                     for k, v in r["eval"].to_dict().items()
                     if not isinstance(v, (dict, list))},
            "modality_recall": r["eval"].modality_recall,
            "n_out_of_category_gold": r["n_out_of_category_gold"],
        }
        for key, k in (("per_query_recall", "per_query_recall"),
                       ("per_query_mrr", "per_query_mrr"),
                       ("per_query_ndcg", "per_query_ndcg")):
            payload["systems"][name][k] = [float(x) for x in r[key]]

    payload["retrieval_placement"] = CONFIG.modality.position
    write_result("exp22_soft_prior", payload)

    rows = []
    for name, _uf, _p, label in CONFIGS:
        e = payload["systems"][name]["eval"]
        rows.append([label, f"{e.get('recall@10', 0):.4f}",
                     f"{e.get('recall@20', 0):.4f}",
                     f"{e.get('mrr', 0):.4f}",
                     f"{e.get('nDCG@10', 0):.4f}"])
    print("\n[exp22] " + markdown_table(
        ["configuration", "R@10", "R@20", "MRR", "nDCG@10"], rows), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
