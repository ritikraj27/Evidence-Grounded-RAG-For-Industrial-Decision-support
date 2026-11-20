#!/usr/bin/env python3
"""Experiment 2b -- the gate fitted per retriever, and the frontier as a curve.

Limitation **L10** says the gate's calibration is fitted per retriever rather
than universally, and that a threshold transferred to a new retriever is wrong
-- and wrong in the direction that flatters the weaker system. The thesis
reports **one** operating point, for **one** retriever, and the limitation
names what would close it: *re-fit per arm, and report the per-arm
threshold*.

This experiment does that, and it adds the second half of what L10 asks for:
the **frontier as a curve** rather than as a point. A single operating point
hides the trade-off; the sweep and the risk--coverage curve show it.

Three retrievers are compared. Each produces the *same kind* of input to the
gate -- a cross-encoder score over a candidate pool -- so the gate's
calibrator has the same shape in all three cases, and what differs is the
retriever that produced the scores:

    hybrid_rrf_rerank   the shipped configuration: dense + BM25 fused by RRF
    bm25_only_rerank    the lexical leg alone, reranked
    dense_only_rerank   the dense leg alone, reranked

For each retriever the experiment reports:

  * the calibrator fitted on its own features, on its own calibration split;
  * the threshold it fits, under the same operating-point rule the shipped
    gate uses;
  * the **whole sweep** -- every threshold's answer rate, refusal rate,
    abstention precision and coverage -- so the frontier is a curve;
  * the risk--coverage curve on the held-out half;
  * what the **shipped** retriever's threshold costs when it is transferred
    here unchanged, against the threshold fitted here, which is the quantity
    L10 warns about.

Nothing is re-run from the generator side and no API is used: retrieval and
reranking are local.

Usage:
    python impl/experiments/run_gate_per_retriever.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import (  # noqa: E402
    load_benchmark,
    load_index,
    rerank_cached,
    save_score_cache,
    write_result,
)
from src.config import CONFIG  # noqa: E402
from src.confidence import (  # noqa: E402
    brier_score,
    expected_calibration_error,
    fit_platt,
    selective_risk_curve,
)
from src.hybrid import reciprocal_rank_fusion  # noqa: E402
from src.pipeline import Framework  # noqa: E402

SEED = 20261118

FEATURE_NAMES = ["top1_rerank", "mean_top3_rerank", "top1_bm25", "max_rrf",
                 "n_candidates_above_bar"]

#: The retrievers compared. The shipped one is first, and its fitted
#: threshold is the one transferred to the others.
RETRIEVERS = {
    "hybrid_rrf_rerank": {"use_dense": True, "use_lexical": True,
                          "label": "dense + BM25 fused by RRF, reranked "
                                   "(the shipped configuration)"},
    "bm25_only_rerank": {"use_dense": False, "use_lexical": True,
                         "label": "the lexical leg alone, reranked"},
    "dense_only_rerank": {"use_dense": True, "use_lexical": False,
                          "label": "the dense leg alone, reranked"},
}

#: The operating-point rule, unchanged from the shipped gate.
OPERATING_POINT_RULE = "highest tau answering >= 90% of answerable queries"


def collect_features(fw: Framework, bench: dict, spec: dict) -> list[dict]:
    """The per-query feature vector and label for one retriever.

    The five feature slots are the shipped gate's five, computed from this
    retriever's own output. `max_rrf` is constant for a single-leg
    retriever -- the fusion of one list is 1/(k+rank), so its maximum does
    not vary by query -- and it therefore carries no information there. It
    is kept rather than dropped so that the feature vector has the same
    shape in all three retrievers and the calibrators stay comparable.
    """
    out = []
    for q in bench["queries"]:
        gold = set(q["gold"])
        trace = fw.retrieve(
            q["query"],
            category=q["category"] if q["category"] != "unanswerable" else None,
            apply_quota=False,
            apply_rerank=False,
            use_dense=spec["use_dense"],
            use_lexical=spec["use_lexical"],
        )
        pool = trace.fused[: fw.config.rerank.top_n]
        scored = rerank_cached(fw, q["query"], pool)
        ids = [cid for cid, _ in scored]

        dense = trace.dense[: fw.config.fusion.dense_top_k]
        lex = trace.lexical[: fw.config.fusion.lexical_top_k]
        fused_scores = reciprocal_rank_fusion([dense, lex], k=fw.config.fusion.rrf_k)

        top = scored[0][1] if scored else -10.0
        top3 = [s for _, s in scored[:3]]
        bm25 = fw.index.bm25.score(q["query"])
        bm25_max = float(bm25.max()) if bm25.size else 0.0
        max_rrf = float(max(fused_scores.values())) if fused_scores else 0.0
        n_above = sum(1 for _, s in scored if s > 0.0)

        out.append({
            "query": q["query"],
            "family": q["family"],
            "category": q["category"],
            "features": [top, float(np.mean(top3)), bm25_max, max_rrf,
                         float(n_above)],
            "label": 1 if gold and (gold & set(ids)) else 0,
            "gold_found": bool(gold & set(ids)),
            "has_gold": bool(gold),
        })
    save_score_cache()
    return out


def fit_calibrator(cases: list[dict], rng) -> dict:
    """The shipped calibrator, on this retriever's features.

    Identical to `run_gate.fit_query_calibrator`: a 60/40 split by query,
    standardisation on the calibration half only, and a multivariate
    logistic fit by IRLS with a ridge term.
    """
    idx = rng.permutation(len(cases))
    n_cal = int(len(cases) * 0.6)
    cal_idx, ev_idx = idx[:n_cal], idx[n_cal:]

    X = np.array([c["features"] for c in cases], dtype=np.float64)
    y = np.array([c["label"] for c in cases], dtype=np.float64)

    mu = X[cal_idx].mean(axis=0)
    sd = X[cal_idx].std(axis=0)
    sd[sd == 0] = 1.0
    Xs = (X - mu) / sd

    beta0, beta1 = fit_platt(X[cal_idx, 0], y[cal_idx])

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

    return {"mu": mu, "sd": sd, "weights": w,
            "univariate_beta0": beta0, "univariate_beta1": beta1,
            "cal_idx": cal_idx, "ev_idx": ev_idx}


def score(cases: list[dict], model: dict) -> np.ndarray:
    X = np.array([c["features"] for c in cases], dtype=np.float64)
    Xs = (X - model["mu"]) / model["sd"]
    Z = np.hstack([np.ones((len(Xs), 1)), Xs])
    return 1.0 / (1.0 + np.exp(-(Z @ model["weights"])))


def sweep_thresholds(cases: list[dict], post: np.ndarray) -> list[dict]:
    """Every threshold's operating point -- the frontier, not a point."""
    thresholds = [round(x, 3) for x in np.arange(0.05, 0.96, 0.05)]
    ans_mask = np.array([c["has_gold"] for c in cases])
    n_ans, n_un = int(ans_mask.sum()), int((~ans_mask).sum())
    out = []
    for tau in thresholds:
        refused = post < tau
        answered = ~refused
        tp = int(np.sum(answered & ans_mask))
        fn = int(np.sum(refused & ans_mask))
        fp = int(np.sum(answered & ~ans_mask))
        tn = int(np.sum(refused & ~ans_mask))
        out.append({
            "tau": tau,
            "answerable_answered": tp / n_ans if n_ans else float("nan"),
            "answerable_refused": fn / n_ans if n_ans else float("nan"),
            "unanswerable_refused": tn / n_un if n_un else float("nan"),
            "unanswerable_answered": fp / n_un if n_un else float("nan"),
            "abstention_precision": tn / (tn + fn) if (tn + fn) else float("nan"),
            "coverage": float(answered.mean()),
        })
    return out


def choose_operating_point(sweep: list[dict]) -> tuple[dict, str]:
    """The shipped operating-point rule."""
    feasible = [s for s in sweep if s["answerable_answered"] >= 0.90]
    if feasible:
        return max(feasible, key=lambda s: s["unanswerable_refused"]), \
            OPERATING_POINT_RULE
    best = max(s["answerable_answered"] for s in sweep)
    chosen = max((s for s in sweep if s["answerable_answered"] == best),
                 key=lambda s: s["unanswerable_refused"])
    return chosen, ("no tau in the sweep answered >= 90% of answerable "
                    "queries; the tau with the highest answerable-answer rate "
                    "was taken")


def at_tau(sweep: list[dict], tau: float) -> dict:
    """The operating point a given threshold produces.

    The sweep is on a 0.05 grid, so a transferred threshold that is not on
    the grid is interpolated onto it rather than silently rounded.
    """
    taus = [s["tau"] for s in sweep]
    if tau in taus:
        return dict(next(s for s in sweep if s["tau"] == tau))
    lo = max((t for t in taus if t <= tau), default=taus[0])
    hi = min((t for t in taus if t >= tau), default=taus[-1])
    a = next(s for s in sweep if s["tau"] == lo)
    b = next(s for s in sweep if s["tau"] == hi)
    if hi == lo:
        return dict(a)
    w = (tau - lo) / (hi - lo)
    out = {"tau": tau}
    for k in a:
        if k == "tau":
            continue
        out[k] = a[k] + w * (b[k] - a[k])
    return out


def main() -> int:
    print("[exp2b] loading ...", flush=True)
    index = load_index()
    bench = load_benchmark()
    fw = Framework(index)
    print(f"[exp2b] benchmark: {bench['n_queries']} queries, "
          f"{bench.get('n_answerable', '?')} answerable, "
          f"{bench.get('n_unanswerable', '?')} unanswerable", flush=True)

    payload: dict = {
        "seed": SEED,
        "design": "the gate fitted separately on each retriever; the frontier "
                  "reported as a curve",
        "feature_names": FEATURE_NAMES,
        "operating_point_rule": OPERATING_POINT_RULE,
        "n_queries": len(bench["queries"]),
        "retrievers": {},
    }

    fitted_tau: dict[str, float] = {}
    posteriors: dict[str, np.ndarray] = {}
    sweeps: dict[str, list[dict]] = {}

    for name, spec in RETRIEVERS.items():
        print(f"[exp2b] {name}: collecting features ...", flush=True)
        cases = collect_features(fw, bench, spec)
        n_pos = sum(c["label"] for c in cases)
        print(f"[exp2b] {name}: evidence found for {n_pos}/{len(cases)} queries "
              f"({n_pos / len(cases):.3f})", flush=True)

        rng = np.random.default_rng(SEED)
        model = fit_calibrator(cases, rng)
        post = score(cases, model)
        posteriors[name] = post

        y = np.array([c["label"] for c in cases], dtype=np.float64)
        ev = model["ev_idx"]
        metrics = {
            "brier": brier_score(post[ev], y[ev]),
            "ece": expected_calibration_error(post[ev], y[ev], n_bins=10),
        }

        sweep = sweep_thresholds(cases, post)
        sweeps[name] = sweep
        chosen, rule = choose_operating_point(sweep)
        fitted_tau[name] = chosen["tau"]

        rc = selective_risk_curve(post[ev], y[ev])
        curve = [{"coverage": round(c, 4), "accuracy": round(a, 4),
                  "risk": round(r, 4)} for c, a, r in rc]

        payload["retrievers"][name] = {
            "label": spec["label"],
            "n_evidence_found": n_pos,
            "base_rate": n_pos / len(cases),
            "weights": [float(w) for w in model["weights"]],
            "univariate_beta0": float(model["univariate_beta0"]),
            "univariate_beta1": float(model["univariate_beta1"]),
            "calibration_metrics": {k: float(v) for k, v in metrics.items()},
            "fitted_tau": float(chosen["tau"]),
            "operating_point_rule": rule,
            "operating_point": {k: (float(v) if isinstance(v, (int, float))
                                     else v)
                                for k, v in chosen.items()},
            "threshold_sweep": sweep,
            "risk_coverage": curve,
            "gold_found_for_answerable": sum(1 for c in cases
                                             if c["has_gold"]
                                             and c["gold_found"]),
            "n_answerable": sum(1 for c in cases if c["has_gold"]),
        }
        print(f"[exp2b] {name}: fitted tau={chosen['tau']}, answers "
              f"{chosen['answerable_answered']:.3f} of answerable, refuses "
              f"{chosen['unanswerable_refused']:.3f} of unanswerable, "
              f"Brier {metrics['brier']:.4f}, ECE {metrics['ece']:.4f}",
              flush=True)

    # ---- the transfer, which is the quantity L10 warns about ---------
    shipped = "hybrid_rrf_rerank"
    transfer = {}
    for name in RETRIEVERS:
        if name == shipped:
            continue
        tau = fitted_tau[shipped]
        transferred = at_tau(sweeps[name], tau)
        refitted = at_tau(sweeps[name], fitted_tau[name])
        transfer[name] = {
            "transferred_tau": float(tau),
            "transferred_operating_point": {
                k: (float(v) if isinstance(v, (int, float)) else v)
                for k, v in transferred.items()},
            "refitted_tau": float(fitted_tau[name]),
            "refitted_operating_point": {
                k: (float(v) if isinstance(v, (int, float)) else v)
                for k, v in refitted.items()},
            "cost_of_transfer": {
                "answerable_answered": (refitted["answerable_answered"]
                                         - transferred["answerable_answered"]),
                "unanswerable_refused": (refitted["unanswerable_refused"]
                                         - transferred["unanswerable_refused"]),
                "coverage": refitted["coverage"] - transferred["coverage"],
            },
        }
        print(f"[exp2b] transfer {shipped} -> {name}: tau {tau} gives "
              f"answerable_answered "
              f"{transferred['answerable_answered']:.3f} / "
              f"unanswerable_refused "
              f"{transferred['unanswerable_refused']:.3f}; refitting to tau "
              f"{fitted_tau[name]} gives "
              f"{refitted['answerable_answered']:.3f} / "
              f"{refitted['unanswerable_refused']:.3f}", flush=True)
    payload["transfer"] = {
        "shipped_retriever": shipped,
        "note": ("a threshold fitted on the shipped retriever, applied "
                 "unchanged to another retriever's calibrated posterior"),
        "per_retriever": transfer,
    }

    payload["fitted_tau_by_retriever"] = {
        k: float(v) for k, v in fitted_tau.items()}
    payload["fitted_tau_spread"] = float(max(fitted_tau.values())
                                         - min(fitted_tau.values()))

    payload["retrieval_placement"] = CONFIG.modality.position
    write_result("exp2b_gate_per_retriever", payload)
    return 0


if __name__ == "__main__":
    sys.exit(main())
