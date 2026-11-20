#!/usr/bin/env python3
"""Experiment 2 -- the confidence gate: calibration, operating point, abstention.

THE DESIGN POINT (and the bug this rewrite fixes)
-------------------------------------------------
An earlier version of this script calibrated at the *candidate* level: for every
(query, candidate) pair it labelled the pair positive iff the candidate was the
gold chunk, and fitted a logistic map from the reranker score to that label.

That is the wrong question, and it produced a confidently wrong result. With
about fifty candidates per query and one gold chunk, the base rate of positives
is roughly 2%. A classifier that answers "nothing is relevant" is therefore right
98% of the time, and maximum-likelihood fitting duly returned a large negative
intercept (beta0 = -2.88) and a nearly flat slope (beta1 = 0.27). The Brier
score and ECE looked excellent -- because they were measuring the base rate --
and the resulting operating point refused 46% of the answerable questions.

The gate does not decide "is THIS candidate the gold chunk". It decides **"does
this retrieved context contain sufficient evidence to answer the question at
all"**. So the calibration must be at the level of the *query*:

    feature vector  ->  P(the retrieved context is sufficient to answer)

The label is 1 when the context contains a gold chunk (the answerable case, and
also the case where retrieval succeeded), and 0 when it does not -- which covers
both a genuinely unanswerable question and an answerable question whose evidence
the retriever missed. In both of those cases the correct behaviour is to refuse.

This is the same distinction SQuAD 2.0 makes and the same one that TPQA
generalises, and getting it right is the difference between a gate that works
and a gate that looks calibrated because it is measuring the wrong thing.

Features used (all computed from the retrieved set, before generation):
  f1  the top cross-encoder rerank score
  f2  the mean of the top-3 rerank scores
  f3  the top-1 BM25 score
  f4  the maximum Reciprocal Rank Fusion score
  f5  the number of candidates that cleared a low relevance bar
"""
from __future__ import annotations

import json
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
from src.confidence import (  # noqa: E402
    brier_score,
    expected_calibration_error,
    fit_platt,
    posterior_from_score,
    reliability_table,
    selective_risk_curve,
)
from src.pipeline import Framework  # noqa: E402

SEED = 20261118
FEATURE_NAMES = ["top1_rerank", "mean_top3_rerank", "top1_bm25", "max_rrf",
                 "n_candidates_above_bar"]


def collect_query_features(fw: Framework, bench: dict) -> list[dict]:
    """For every query, compute the retrieved set and its feature vector."""
    from common import rerank_cached, save_score_cache

    out = []
    for q in bench["queries"]:
        gold = set(q["gold"])
        trace = fw.retrieve(
            q["query"],
            category=q["category"] if q["category"] != "unanswerable" else None,
            apply_quota=False,
            apply_rerank=False,
        )
        pool = trace.fused[: fw.config.rerank.top_n]
        scored = rerank_cached(fw, q["query"], pool)

        rrf_scores = trace.fused  # ordered; rebuild the score map
        rrf_map = {}
        # Recompute RRF scores for the pool so the feature is comparable.
        from src.hybrid import reciprocal_rank_fusion

        dense = trace.dense[: fw.config.fusion.dense_top_k]
        lex = trace.lexical[: fw.config.fusion.lexical_top_k]
        fused_scores = reciprocal_rank_fusion([dense, lex], k=fw.config.fusion.rrf_k)

        top_rerank = scored[0][1] if scored else -10.0
        top3 = [s for _, s in scored[:3]]
        bm25_top = fw.index.bm25.score(q["query"])
        bm25_max = float(bm25_top.max()) if bm25_top.size else 0.0
        max_rrf = float(max(fused_scores.values())) if fused_scores else 0.0
        n_above = sum(1 for _, s in scored if s > 0.0)

        label = 1 if gold and (gold & set(cid for cid, _ in scored)) else 0
        out.append(
            {
                "query": q["query"],
                "family": q["family"],
                "category": q["category"],
                "features": [top_rerank, float(np.mean(top3)), bm25_max, max_rrf,
                             float(n_above)],
                "label": label,
                "gold_found": bool(gold & set(cid for cid, _ in scored)),
                "has_gold": bool(gold),
            }
        )
    save_score_cache()
    return out


def fit_query_calibrator(cases, rng, frac=0.6):
    """Fit a logistic calibrator on QUERY-level features.

    The split is by query, so no query appears in both halves.
    """
    idx = rng.permutation(len(cases))
    n_cal = int(len(cases) * frac)
    cal_idx, ev_idx = idx[:n_cal], idx[n_cal:]

    X = np.array([c["features"] for c in cases], dtype=np.float64)
    y = np.array([c["label"] for c in cases], dtype=np.float64)

    # Standardise on the calibration half only.
    mu = X[cal_idx].mean(axis=0)
    sd = X[cal_idx].std(axis=0)
    sd[sd == 0] = 1.0
    Xs = (X - mu) / sd

    # Fit by logistic regression on the standardised features (Newton/IRLS).
    from src.confidence import fit_platt

    # Fit a per-feature univariate map first for interpretability, then a
    # multivariate logistic model for the operating point.
    beta0, beta1 = fit_platt(X[cal_idx, 0], y[cal_idx])
    coefs = np.zeros(X.shape[1])
    coefs[0] = beta1
    intercept = beta0

    # Multivariate IRLS on the calibration half.
    Z = np.hstack([np.ones((len(cal_idx), 1)), Xs[cal_idx]])
    w = np.zeros(Z.shape[1])
    for _ in range(100):
        z = Z @ w
        p = 1.0 / (1.0 + np.exp(-z))
        W = p * (1 - p) + 1e-9
        g = Z.T @ (p - y[cal_idx])
        H = Z.T @ (Z * W[:, None]) + 1e-6 * np.eye(Z.shape[1])
        try:
            step = np.linalg.solve(H, g)
        except np.linalg.LinAlgError:
            break
        w = w - step
        if np.max(np.abs(step)) < 1e-9:
            break

    return {
        "mu": mu,
        "sd": sd,
        "weights": w,
        "univariate_beta0": beta0,
        "univariate_beta1": beta1,
        "cal_idx": cal_idx,
        "ev_idx": ev_idx,
    }


def score(cases, model):
    X = np.array([c["features"] for c in cases], dtype=np.float64)
    Xs = (X - model["mu"]) / model["sd"]
    Z = np.hstack([np.ones((len(Xs), 1)), Xs])
    return 1.0 / (1.0 + np.exp(-(Z @ model["weights"])))


def _refusal_by_family(cases: list[dict], post: np.ndarray,
                       tau: float) -> dict:
    """The refusal rate at the operating point, split by question family.

    The unanswerable class is not homogeneous. The out-of-domain family
    asks about vitamin D and the FIFA World Cup and is unanswerable for
    any system that knows what the corpus is about; the corpus-anchored
    family asks about subjects the corpus discusses and is the case the
    gate is actually being tested on. A refusal rate pooled over both is
    an upper bound on what the gate achieves on a question stream whose
    unanswerable questions are on-topic, so the strata are reported
    separately and the pooled number is reported beside them.
    """
    out: dict[str, dict] = {}
    families = sorted({c["family"] for c in cases})
    for fam in families:
        idx = [i for i, c in enumerate(cases) if c["family"] == fam]
        refused = [i for i in idx if post[i] < tau]
        out[fam] = {
            "n": len(idx),
            "refused": len(refused),
            "refused_rate": (len(refused) / len(idx)) if idx else None,
            "answered": len(idx) - len(refused),
            "answerable": sum(1 for i in idx if cases[i]["has_gold"]),
        }
    return {
        "tau": tau,
        "by_family": out,
        "note": (
            "the refusal rate at the fitted operating point, per question "
            "family. The corpus-anchored families are the hard case: the "
            "corpus discusses the subject and states no value for it, so "
            "only the retrieved evidence can decide. The out-of-domain "
            "family is trivially unanswerable and is reported separately; a "
            "pooled rate over both is an upper bound."),
    }


def main() -> int:
    print("[exp2] loading ...", flush=True)
    index = load_index()
    bench = load_benchmark()
    fw = Framework(index)
    print(f"[exp2] benchmark: {bench['n_queries']} queries, "
          f"{bench.get('n_answerable', '?')} answerable, "
          f"{bench.get('n_unanswerable', '?')} unanswerable", flush=True)

    print("[exp2] reranking candidate pools ...", flush=True)
    cases = collect_query_features(fw, bench)
    n_pos = sum(c["label"] for c in cases)
    print(f"[exp2] contexts containing sufficient evidence: {n_pos}/{len(cases)} "
          f"({n_pos / len(cases):.3f})", flush=True)
    print(f"[exp2] gold found by the retriever for answerable queries: "
          f"{sum(1 for c in cases if c['gold_found'])}/"
          f"{sum(1 for c in cases if c['has_gold'])}", flush=True)

    rng = np.random.default_rng(SEED)
    model = fit_query_calibrator(cases, rng)
    ev = model["ev_idx"]
    cal = model["cal_idx"]

    post_all = score(cases, model)
    y_all = np.array([c["label"] for c in cases], dtype=np.float64)
    y_ev = y_all[ev]
    p_ev = post_all[ev]

    metrics = {
        "brier": brier_score(p_ev, y_ev),
        "ece": expected_calibration_error(p_ev, y_ev, n_bins=10),
        "brier_calibration_half": brier_score(post_all[cal], y_all[cal]),
        "brier_evaluation_half": brier_score(p_ev, y_ev),
    }
    print(f"[exp2] Brier {metrics['brier']:.4f} | ECE {metrics['ece']:.4f}",
          flush=True)
    print(f"[exp2] weights: intercept={model['weights'][0]:.4f} " +
          ", ".join(f"{n}={model['weights'][i+1]:+.4f}"
                    for i, n in enumerate(FEATURE_NAMES)), flush=True)

    # ---- operating point sweep ----------------------------------------
    thresholds = [round(x, 3) for x in np.arange(0.05, 0.96, 0.05)]
    sweep = []
    for tau in thresholds:
        refused = post_all < tau
        answered = ~refused
        ans_mask = np.array([c["has_gold"] for c in cases])
        tp = int(np.sum(answered & ans_mask))          # answerable & answered
        fn = int(np.sum(refused & ans_mask))            # answerable & refused
        fp = int(np.sum(answered & ~ans_mask))          # unanswerable & answered
        tn = int(np.sum(refused & ~ans_mask))           # unanswerable & refused
        n_ans, n_un = tp + fn, fp + tn
        sweep.append({
            "tau": tau,
            "answerable_answered": tp / n_ans if n_ans else float("nan"),
            "answerable_refused": fn / n_ans if n_ans else float("nan"),
            "unanswerable_refused": tn / n_un if n_un else float("nan"),
            "unanswerable_answered": fp / n_un if n_un else float("nan"),
            "abstention_precision": tn / (tn + fn) if (tn + fn) else float("nan"),
            "coverage": answered.mean(),
        })

    feasible = [s for s in sweep if s["answerable_answered"] >= 0.90]
    if feasible:
        chosen = max(feasible, key=lambda s: s["unanswerable_refused"])
        rule = "highest tau answering >= 90% of answerable queries"
    else:
        best_cov = max(s["answerable_answered"] for s in sweep)
        chosen = max((s for s in sweep if s["answerable_answered"] == best_cov),
                     key=lambda s: s["unanswerable_refused"])
        rule = ("no tau in the sweep answered >= 90% of answerable queries; "
                "the tau with the highest answerable-answer rate was taken")
    print(f"[exp2] operating point: tau={chosen['tau']} "
          f"answers {chosen['answerable_answered']:.3f} of answerable, "
          f"refuses {chosen['unanswerable_refused']:.3f} of unanswerable "
          f"(rule: {rule})", flush=True)

    # The endpoints of the sweep are NOT baselines: the loosest threshold in
    # the sweep still refuses some unanswerable queries, and the strictest
    # still answers some answerable ones. The true baselines are the two
    # degenerate policies, tau = 0 (never refuse) and tau = 1 (always
    # refuse), and they have to be computed rather than read off the
    # sweep.
    ans_mask = np.array([c["has_gold"] for c in cases])
    n_ans, n_un = int(ans_mask.sum()), int((~ans_mask).sum())
    never_refuse = {
        "tau": 0.0,
        "answerable_answered": 1.0,
        "answerable_refused": 0.0,
        "unanswerable_refused": 0.0,
        "unanswerable_answered": 1.0,
        # Undefined, not zero: no abstentions are made, so there is no
        # precision to report.
        "abstention_precision": None,
        "coverage": 1.0,
    }
    always_refuse = {
        "tau": 1.0,
        "answerable_answered": 0.0,
        "answerable_refused": 1.0,
        "unanswerable_refused": 1.0,
        "unanswerable_answered": 0.0,
        "abstention_precision": (n_un / (n_un + n_ans)) if (n_un + n_ans) else None,
        "coverage": 0.0,
    }
    loosest = sweep[0]
    strictest = sweep[-1]
    print(f"[exp2] never-refuse baseline (tau=0) refuses 0.000 of unanswerable; "
          f"always-refuse (tau=1) answers 0.000 of answerable. The loosest "
          f"threshold in the sweep (tau={loosest['tau']:.2f}) still refuses "
          f"{loosest['unanswerable_refused']:.3f} of unanswerable, which is why "
          f"it is a sweep endpoint and not a baseline.", flush=True)

    payload = {
        "seed": SEED,
        "design": "query-level answer-in-context calibration (not candidate-level)",
        "refusal_by_family": _refusal_by_family(cases, post_all, chosen["tau"]),
        "feature_names": FEATURE_NAMES,
        "n_queries": len(cases),
        "n_contexts_with_answer_in_context": int(n_pos),
        "base_rate_answer_in_context": float(y_all.mean()),
        "label_definition": (
            "The positive class is 1 iff the gold chunk is present in the "
            "reranked candidate pool. The negative class is therefore "
            "dominated by RETRIEVAL FAILURE -- an answerable query whose "
            "evidence the retriever missed -- not by absence of evidence. "
            "The gate detects answer-in-context detectability; it does not "
            "detect evidence sufficiency."),
        "label_decomposition": {
            "answerable_and_found": int(sum(
                1 for c in cases if c["has_gold"] and c["gold_found"])),
            "answerable_and_missed": int(sum(
                1 for c in cases if c["has_gold"] and not c["gold_found"])),
            "unanswerable": int(sum(1 for c in cases if not c["has_gold"])),
            "note": (
                "The negative class is (answerable_and_missed + unanswerable). "
                "Report the share of it that is retrieval failure: that "
                "fraction is the limit on what the gate can be said to "
                "detect."),
        },
        "retriever_recall_of_gold": float(
            sum(1 for c in cases if c["gold_found"]) /
            max(sum(1 for c in cases if c["has_gold"]), 1)),
        "calibration_split": "60% of queries by index",
        "weights": {
            "intercept": float(model["weights"][0]),
            **{n: float(model["weights"][i + 1])
               for i, n in enumerate(FEATURE_NAMES)},
        },
        "univariate_top1_rerank": {
            "beta0": float(model["univariate_beta0"]),
            "beta1": float(model["univariate_beta1"]),
        },
        "calibration_metrics": metrics,
        "reliability_table": reliability_table(p_ev, y_ev, n_bins=10),
        "risk_coverage": [
            {"coverage": c, "accuracy": a, "risk": r}
            for c, a, r in selective_risk_curve(p_ev, y_ev)[:: max(1, len(p_ev) // 25)]
        ],
        "threshold_sweep": sweep,
        "chosen_operating_point": chosen,
        "operating_point_rule": rule,
        "never_refuse_baseline": never_refuse,
        "always_refuse_baseline": always_refuse,
        "loosest_threshold_in_sweep": loosest,
        "strictest_threshold_in_sweep": strictest,
        "baseline_note": (
            "The sweep endpoints are not baselines: the loosest threshold in "
            "the sweep still refuses some unanswerable queries. The true "
            "baselines are the degenerate policies tau=0 (never refuse) and "
            "tau=1 (always refuse)."),
    }
    # Write the fitted gate model so the framework itself uses the calibrated
    # query-level posterior rather than the un-calibrated chunk-level fallback.
    from src.config import ARTIFACT_DIR, CONFIG

    payload["retrieval_placement"] = CONFIG.modality.position

    write_result("exp2_gate", payload)

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    model_path = ARTIFACT_DIR / "gate_model.json"
    model_path.write_text(
        json.dumps(
            {
                "mu": model["mu"].tolist(),
                "sd": model["sd"].tolist(),
                "weights": model["weights"].tolist(),
                "feature_names": FEATURE_NAMES,
                "tau": chosen["tau"],
                "fitted_on": {
                    "n_queries": len(cases),
                    "seed": SEED,
                    "base_rate": float(y_all.mean()),
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"[exp2] wrote {model_path}", flush=True)

    rows = [
        [f"{s['tau']:.2f}", f"{s['answerable_answered']:.3f}",
         f"{s['unanswerable_refused']:.3f}", f"{s['abstention_precision']:.3f}",
         f"{s['coverage']:.3f}"]
        for s in sweep
    ]
    table = markdown_table(
        ["tau", "answerable answered", "unanswerable refused",
         "abstention precision", "coverage"], rows
    )
    (RESULTS_DIR / "exp2_gate.md").write_text(
        "# Experiment 2 -- Confidence gate\n\n"
        f"Query-level sufficiency calibration. Base rate of contexts containing "
        f"sufficient evidence: {y_all.mean():.3f}.\n\n"
        f"Brier {metrics['brier']:.4f} | ECE {metrics['ece']:.4f}\n\n"
        f"Chosen operating point: tau={chosen['tau']} (rule: {rule})\n\n"
        + table + "\n", encoding="utf-8"
    )
    print(f"[exp2] wrote {RESULTS_DIR / 'exp2_gate.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
