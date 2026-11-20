#!/usr/bin/env python3
"""Experiment 1 -- retrieval ablation.

Systems compared
----------------
    A. bm25_only                 lexical leg alone
    B. dense_only                dense leg alone
    C. hybrid_rrf                BM25 + dense fused with RRF
    D. hybrid_rrf_rerank         C + cross-encoder reranking
    E. hybrid_rrf_rerank_cat     D + category pre-filter
    F. hybrid_rrf_rerank_cat_q   E + modality quota
    G. no_gate                   F without the confidence gate (control)
    H. full                      F with the confidence gate (the system)

The point of the ladder is that each rung isolates one design move, so the
contribution of each can be read off directly rather than inferred from a
two-system comparison. C vs A/B tests fusion; D vs C tests reranking; E vs D
tests the category filter; F vs E tests the modality quota; H vs G tests the
gate.

Every system is scored against the SAME silver labels, and paired statistical
tests are run between adjacent rungs so that the reported differences are not
just noise on 243 queries.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import (  # noqa: E402
    RESULTS_DIR,
    ROOT,
    grade_map,
    load_benchmark,
    load_index,
    markdown_table,
    modality_relevance,
    relevance_sets,
    write_result,
)
from src.evaluate import evaluate_retrieval  # noqa: E402
from src.config import CONFIG  # noqa: E402
from src.stats import (  # noqa: E402
    bootstrap_ci,
    cliffs_delta,
    mcnemar_test,
    wilcoxon_signed_rank,
)

SEED = 20261118


def _mrr_at(ranked: list[str], gold: set[str]) -> float:
    """Reciprocal rank of the first relevant chunk, 0 if none is present."""
    for i, cid in enumerate(ranked, start=1):
        if cid in gold:
            return 1.0 / i
    return 0.0


def _ndcg_at(ranked: list[str], gold: set[str], k: int = 10) -> float:
    """Normalised discounted cumulative gain over the first k results."""
    dcg = sum((1.0 / np.log2(i + 1))
               for i, cid in enumerate(ranked[:k], start=1) if cid in gold)
    ideal = sum((1.0 / np.log2(i + 1)) for i in range(1, min(len(gold), k) + 1))
    return dcg / ideal if ideal else 0.0


def run_system(fw, bench, name, *, use_dense, use_lexical, apply_quota, apply_rerank, use_category, quota_position="post_rerank", answerable_only=False):
    runs, relevances, grades = [], [], []
    mod_rel = []
    per_query_recall = []
    per_query_mrr = []
    per_query_ndcg = []
    queries = ([q for q in bench["queries"] if q["gold"]]
               if answerable_only else bench["queries"])
    for q in queries:
        gold = set(q["gold"])
        # The category pre-filter is only meaningful for answerable queries;
        # an unanswerable query is supposed to be unfiltered, and filtering it
        # to "unanswerable" would make retrieval trivially correct.
        # An unanswerable query has no gold chunk, and filtering it to the
        # category "unanswerable" would match nothing and silently fall back
        # to the whole corpus.
        category = q["category"] if (use_category and q["gold"]) else None
        trace = fw.retrieve(
            q["query"],
            category=category,
            apply_quota=apply_quota,
            apply_rerank=apply_rerank,
            use_dense=use_dense,
            use_lexical=use_lexical,
            quota_position=quota_position,
        )
        if not apply_rerank:
            ranked = trace.fused
        elif apply_quota and quota_position == "post_rerank":
            # The post-rerank quota produces a *context*, not a ranking: it
            # selects the ten chunks the generator will see. Recall@20 is
            # therefore not defined for it, and equals Recall@10 by
            # construction. For every other system the ranking is the
            # system's output, so the full reranked list is evaluated and
            # Recall@20 is a real measurement rather than an artefact of
            # the final-context truncation.
            ranked = trace.reranked or trace.fused
        else:
            ranked = trace.reranked_full or trace.reranked or trace.fused
        runs.append(ranked)
        relevances.append(gold)
        grades.append({g: (3.0 if q["family"] == "table_lookup" else 1.0) for g in gold})
        mod_rel.append(
            {m: {g for g in gold if fw.index.modality_of.get(g, "text") == m} for m in ("text", "table")}
        )
        # Only answerable queries enter the paired per-query statistics.
        # A query with no gold chunk contributes 0.0 to every system
        # identically, which inflates the sample size without adding
        # information and dilutes the paired differences. The behaviour on
        # unanswerable queries is measured by the gate's rejection rate in
        # Experiment 2, which is where it belongs.
        if gold:
            per_query_recall.append(len(set(ranked[:10]) & gold) / len(gold))
            # The ordering metrics are collected per query as well, because
            # Recall@10 saturates on silver-standard labels: a question
            # derived from a chunk contains that chunk's own words, so every
            # system finds the gold chunk and the paired recall test has
            # almost nothing to discriminate. The reranker's effect shows up
            # in the ordering, and it needs a paired test of its own.
            per_query_mrr.append(_mrr_at(ranked, gold))
            per_query_ndcg.append(_ndcg_at(ranked, gold))
    return {
        "name": name,
        "eval": evaluate_retrieval(runs, relevances, grades, fw.index.modality_of, mod_rel),
        "runs": runs,
        "per_query_recall": per_query_recall,
        "per_query_mrr": per_query_mrr,
        "per_query_ndcg": per_query_ndcg,
    }


def main() -> int:
    print("[exp1] loading index ...", flush=True)
    index = load_index()
    print(f"[exp1] corpus: {index.stats}", flush=True)
    bench = load_benchmark()
    print(f"[exp1] benchmark: {bench['n_queries']} queries "
          f"({bench['n_answerable']} answerable, {bench['n_unanswerable']} unanswerable)", flush=True)

    from src.pipeline import Framework

    fw = Framework(index)

    systems = [
        ("A. bm25_only", dict(use_dense=False, use_lexical=True, apply_quota=False, apply_rerank=False, use_category=False)),
        ("B. dense_only", dict(use_dense=True, use_lexical=False, apply_quota=False, apply_rerank=False, use_category=False)),
        ("C. hybrid_rrf", dict(use_dense=True, use_lexical=True, apply_quota=False, apply_rerank=False, use_category=False)),
        ("D. hybrid_rrf_rerank", dict(use_dense=True, use_lexical=True, apply_quota=False, apply_rerank=True, use_category=False)),
        ("E. +category_filter", dict(use_dense=True, use_lexical=True, apply_quota=False, apply_rerank=True, use_category=True)),
        ("F. +quota_pre_rerank", dict(use_dense=True, use_lexical=True, apply_quota=True, apply_rerank=True, use_category=True, quota_position="pre_rerank")),
        ("G. +quota_post_rerank", dict(use_dense=True, use_lexical=True, apply_quota=True, apply_rerank=True, use_category=True, quota_position="post_rerank")),
    ]

    results = {}
    # The unanswerable queries have no gold chunk. `evaluate_retrieval`
    # excludes them from every aggregate and `run_system` excludes them from
    # the paired per-query statistics, so dropping them here changes no
    # reported number -- but each one still costs a cross-encoder pass over
    # its candidate pool. The flag is opt-in so that the shipped behaviour
    # is unchanged.
    answerable_only = "--answerable-only" in sys.argv
    for name, kwargs in systems:
        print(f"[exp1] running {name} ...", flush=True)
        results[name] = run_system(fw, bench, name, answerable_only=answerable_only,
                                   **kwargs)

    # --- paired statistical tests between adjacent rungs ---
    print("[exp1] statistical tests ...", flush=True)
    comparisons = []
    names = [n for n, _ in systems]
    for a, b in zip(names[:-1], names[1:]):
        ra = results[a]["per_query_recall"]
        rb = results[b]["per_query_recall"]
        w = wilcoxon_signed_rank(ra, rb)
        d = cliffs_delta(np.array(ra), np.array(rb))
        entry = {
            "comparison": f"{a} -> {b}",
            "mean_recall_a": float(np.mean(ra)),
            "mean_recall_b": float(np.mean(rb)),
            "delta": float(np.mean(rb) - np.mean(ra)),
            "wilcoxon": w.to_dict(),
            "cliffs_delta": d,
        }
        # The same paired test on the two ordering metrics.
        for key, label in (("per_query_mrr", "mrr"), ("per_query_ndcg", "ndcg")):
            ma, mb = results[a][key], results[b][key]
            if len(ma) == len(mb) and len(ma) > 1:
                mw = wilcoxon_signed_rank(ma, mb)
                entry[f"wilcoxon_{label}"] = mw.to_dict()
                entry[f"delta_{label}"] = float(np.mean(mb) - np.mean(ma))
        comparisons.append(entry)
        print(f"       {a} -> {b}: dR@10={np.mean(rb)-np.mean(ra):+.4f} "
              f"p={w.p_value:.4g} d_z={w.effect_size:+.3f} | "
              f"dMRR={entry.get('delta_mrr', float('nan')):+.4f} "
              f"p={entry.get('wilcoxon_mrr', {}).get('p_value', float('nan')):.4g}")

    # The adjacent-rung tests cannot answer the question the narrative now
    # turns on: does fusing the dense leg in beat the lexical leg alone? That
    # is a non-adjacent comparison, so it is run explicitly.
    for a, b in (("A. bm25_only", "C. hybrid_rrf"),
                 ("D. hybrid_rrf_rerank", "F. +quota_pre_rerank")):
        ra = results[a]["per_query_recall"]
        rb = results[b]["per_query_recall"]
        if len(ra) != len(rb) or len(ra) < 2:
            continue
        w = wilcoxon_signed_rank(ra, rb)
        entry = {
            "comparison": f"{a} -> {b}",
            "non_adjacent": True,
            "mean_recall_a": float(np.mean(ra)),
            "mean_recall_b": float(np.mean(rb)),
            "delta": float(np.mean(rb) - np.mean(ra)),
            "wilcoxon": w.to_dict(),
            "cliffs_delta": cliffs_delta(np.array(ra), np.array(rb)),
        }
        for key, label in (("per_query_mrr", "mrr"), ("per_query_ndcg", "ndcg")):
            ma, mb = results[a][key], results[b][key]
            if len(ma) == len(mb) and len(ma) > 1:
                entry[f"wilcoxon_{label}"] = wilcoxon_signed_rank(ma, mb).to_dict()
                entry[f"delta_{label}"] = float(np.mean(mb) - np.mean(ma))
        comparisons.append(entry)
        print(f"       {a} -> {b} [non-adjacent]: dR@10="
              f"{entry['delta']:+.4f} p={w.p_value:.4g}")

    # A paired test of the fusion against the *lexical* leg. The adjacent-rung
    # comparisons above test the fusion against the dense leg, but the claim
    # that fusion is worth having rests on whether it beats the leg it is
    # fused with, so that comparison needs a test of its own.
    _ra = results["A. bm25_only"]["per_query_recall"]
    _rc = results["C. hybrid_rrf"]["per_query_recall"]
    _ac_w = wilcoxon_signed_rank(_ra, _rc)
    comparisons.append(
        {
            "comparison": "A. bm25_only -> C. hybrid_rrf",
            "mean_recall_a": float(np.mean(_ra)),
            "mean_recall_b": float(np.mean(_rc)),
            "delta": float(np.mean(_rc) - np.mean(_ra)),
            "wilcoxon": _ac_w.to_dict(),
            "cliffs_delta": cliffs_delta(np.array(_ra), np.array(_rc)),
            "note": "non-adjacent rungs: the fusion against the lexical leg",
        }
    )
    for _label, _key in (("mrr", "per_query_mrr"), ("ndcg", "per_query_ndcg")):
        _ma = results["A. bm25_only"][_key]
        _mc = results["C. hybrid_rrf"][_key]
        if len(_ma) == len(_mc) and len(_ma) > 1:
            _mw = wilcoxon_signed_rank(_ma, _mc)
            comparisons[-1][f"wilcoxon_{_label}"] = _mw.to_dict()
            comparisons[-1][f"delta_{_label}"] = float(np.mean(_mc) - np.mean(_ma))
    print(f"       A. bm25_only -> C. hybrid_rrf: dR@10="
          f"{np.mean(_rc) - np.mean(_ra):+.4f} p={_ac_w.p_value:.4g}")

    # --- bootstrap CI on the best system (highest Recall@10) ---
    best = max(names, key=lambda n: results[n]["eval"].recall_at_10)
    point, lo, hi = bootstrap_ci(
        np.array(results[best]["per_query_recall"]), n_bootstrap=10_000, seed=SEED
    )

    payload = {
        "seed": SEED,
        "corpus_stats": index.stats,
        "benchmark": {
            "n_queries": bench["n_queries"],
            "n_answerable": bench["n_answerable"],
            "n_unanswerable": bench["n_unanswerable"],
            "label_standard": bench["label_standard"],
        },
        "systems": {n: results[n]["eval"].to_dict() for n in names},
        "comparisons": comparisons,
        "bootstrap_recall10": {"system": best, "point": point, "lo": lo, "hi": hi},
    }
    payload["retrieval_placement"] = CONFIG.modality.position
    write_result("exp1_ablation", payload)

    # --- console table ---
    rows = []
    for n in names:
        e = results[n]["eval"]
        rows.append([
            n,
            f"{e.recall_at_5:.3f}",
            f"{e.recall_at_10:.3f}",
            f"{e.recall_at_20:.3f}",
            f"{e.precision_at_10:.3f}",
            f"{e.mrr:.3f}",
            f"{e.ndcg_at_10:.3f}",
            f"{e.modality_recall.get('table', float('nan')):.3f}",
        ])
    table = markdown_table(
        ["System", "R@5", "R@10", "R@20", "P@10", "MRR", "nDCG@10", "Table R@10"], rows
    )
    print("\n" + table)
    (RESULTS_DIR / "exp1_ablation.md").write_text(
        "# Experiment 1 -- Retrieval ablation\n\n" + table + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
