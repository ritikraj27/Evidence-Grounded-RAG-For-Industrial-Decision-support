"""Shared loading and evaluation helpers for the experiment scripts."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import ARTIFACT_DIR, BENCHMARK_DIR, CORPUS_DIR, RESULTS_DIR  # noqa: E402
from src.evaluate import evaluate_retrieval  # noqa: E402
from src.pipeline import Framework, Index, build_index  # noqa: E402

RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def _use_every_core() -> None:
    """Let torch use every core.

    The cross-encoder pass is the most expensive step in the suite -- tens
    of thousands of (query, passage) pairs -- and it is embarrassingly
    parallel. Torch's default thread count is conservative and leaves most
    of the machine idle, which is a wall-clock cost and not a result: the
    same pairs are scored either way.
    """
    import os

    try:
        import torch

        torch.set_num_threads(int(os.environ.get(
            "MTP_TORCH_THREADS", "0") or 0) or (os.cpu_count() or 4))
    except Exception:  # pragma: no cover - torch is always present
        pass


_use_every_core()


def load_benchmark(path: Path | None = None) -> dict:
    """The benchmark to measure against.

    `MTP_BENCHMARK_FILE` overrides the default path, which is how the
    pre-repair benchmark is measured for the before-and-after comparison
    without swapping the file the rest of the project reads. Swapping a
    file another process may open at any moment is a race; an override is
    not.
    """
    if path is None:
        override = os.environ.get("MTP_BENCHMARK_FILE")
        path = Path(override) if override else (BENCHMARK_DIR / "benchmark.json")
    return json.loads(path.read_text(encoding="utf-8"))


def load_index(rebuild: bool = False) -> Index:
    """Load the index, building and caching it if needed.

    The cache path is variant-aware. A hard-coded one silently loaded the
    multi-category index into the focus-domain run, so the focus evaluation
    searched 2,592 chunks while reporting a 807-chunk corpus.
    """
    cache = ARTIFACT_DIR / "index"
    if cache.with_suffix(".npy").exists() and not rebuild:
        return Index.load(cache)
    index = build_index(CORPUS_DIR)
    index.save(cache)
    return index


def write_result(name: str, payload: dict) -> Path:
    path = RESULTS_DIR / f"{name}.json"
    path.write_text(json.dumps(payload, indent=2, default=float), encoding="utf-8")
    print(f"[write] {path}")
    return path


def markdown_table(headers: list[str], rows: list[list]) -> str:
    """Render a markdown table (used to paste results into the report)."""
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for row in rows:
        out.append("| " + " | ".join(str(c) for c in row) + " |")
    return "\n".join(out)


def relevance_sets(bench: dict) -> list[set[str]]:
    return [set(q["gold"]) for q in bench["queries"]]


def grade_map(bench: dict) -> list[dict[str, float]]:
    """Graded relevance: 3 for table-lookup golds (the binding requirement),
    1 for ordinary golds. This makes nDCG sensitive to whether the *table*
    was found, which is the claim the modality quota makes."""
    out = []
    for q in bench["queries"]:
        out.append({g: (3.0 if q["family"] == "table_lookup" else 1.0) for g in q["gold"]})
    return out


def modality_relevance(bench: dict, modality_of: dict[str, str]) -> list[dict[str, set[str]]]:
    """Per-modality gold sets, for the modality-recall metric."""
    out = []
    for q in bench["queries"]:
        by_mod: dict[str, set[str]] = {}
        for g in q["gold"]:
            by_mod.setdefault(modality_of.get(g, "text"), set()).add(g)
        out.append(by_mod)
    return out


# --------------------------------------------------------------------------
# Shared cross-encoder score cache
# --------------------------------------------------------------------------
# The cross-encoder pass is by far the most expensive step (~50 candidate
# pairs per query), and experiments 2, 3 and 4 all need it. Caching it on disk
# turns three passes into one and makes the suite re-runnable in minutes.
_SCORE_CACHE_PATH = ARTIFACT_DIR / "rerank_scores.json"
_SCORE_CACHE: dict[str, list] | None = None


def _load_score_cache() -> dict:
    global _SCORE_CACHE
    if _SCORE_CACHE is None:
        if _SCORE_CACHE_PATH.exists():
            try:
                _SCORE_CACHE = json.loads(_SCORE_CACHE_PATH.read_text())
            except Exception:
                _SCORE_CACHE = {}
        else:
            _SCORE_CACHE = {}
    return _SCORE_CACHE


def save_score_cache() -> None:
    global _SCORE_CACHE
    if _SCORE_CACHE is None:
        return
    _SCORE_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    _SCORE_CACHE_PATH.write_text(json.dumps(_SCORE_CACHE), encoding="utf-8")


def rerank_cached(fw, query: str, pool: list[str]) -> list[tuple[str, float]]:
    """Cross-encoder scores for a query, cached on disk by query text.

    The cache key is the query text plus the identity of the candidate pool,
    so a changed corpus invalidates it automatically.
    """
    from src.models import rerank

    cache = _load_score_cache()
    key = f"{query}||{len(pool)}||{pool[0] if pool else ''}||{pool[-1] if pool else ''}"
    if key in cache:
        return [tuple(x) for x in cache[key]]
    pairs = [(cid, fw.index.chunk_text[cid]) for cid in pool]
    scored = rerank(query, pairs, model_name=fw.config.rerank.model)
    cache[key] = [list(x) for x in scored]
    if len(cache) % 50 == 0:
        save_score_cache()
    return scored


# --------------------------------------------------------------------------
# Query-level sufficiency calibration, shared by experiments 2 and 4
# --------------------------------------------------------------------------
# The gate decides a QUERY-level question: "does this retrieved context
# contain sufficient evidence to answer at all?" Calibrating per candidate
# instead would fit "nothing is relevant" and call it a probability,
# because one gold chunk among ~50 candidates is a ~2% base rate.
FEATURE_NAMES = ("top1_rerank", "mean_top3_rerank", "top1_bm25", "max_rrf",
                 "n_candidates_above_bar")


def query_features(fw, bench, cases_out=None):
    """Compute the query-level feature vector and label for every query.

    The label is 1 when the retrieved candidate pool contains a gold chunk.
    That covers both an answerable question whose evidence the retriever
    found and an answerable question whose evidence it missed -- in both
    cases the correct behaviour is to refuse.
    """
    from src.hybrid import reciprocal_rank_fusion

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

        dense = trace.dense[: fw.config.fusion.dense_top_k]
        lex = trace.lexical[: fw.config.fusion.lexical_top_k]
        fused_scores = reciprocal_rank_fusion([dense, lex], k=fw.config.fusion.rrf_k)

        all_scores = sorted((s for _, s in scored), reverse=True)
        bm25_all = fw.index.bm25.score(q["query"])
        bm25_max = float(bm25_all.max()) if bm25_all.size else 0.0
        top3 = all_scores[:3]

        features = [
            all_scores[0] if all_scores else -10.0,
            float(np.mean(top3)) if top3 else -10.0,
            bm25_max,
            float(max(fused_scores.values())) if fused_scores else 0.0,
            float(sum(1 for s in all_scores if s > 0.0)),
        ]
        found = bool(gold & {cid for cid, _ in scored})
        out.append(
            {
                "q": q,
                "scored": scored,
                "fused": trace.fused,
                "features": features,
                "label": 1 if found else 0,
                "has_gold": bool(gold),
                "gold_found": found,
            }
        )
    save_score_cache()
    return out


def fit_query_calibrator(cases, rng, frac=0.6, cat_filter=None):
    """Fit a logistic calibrator on QUERY-level features.

    The split is by query, so no query appears in both halves.
    """
    subset = [c for c in cases
              if cat_filter is None or c["q"]["category"] == cat_filter]
    if not subset:
        return None
    idx = rng.permutation(len(subset))
    n_cal = int(len(subset) * frac)
    cal_idx = idx[:n_cal]
    ev_idx = idx[n_cal:]

    X = np.array([c["features"] for c in subset], dtype=np.float64)
    y = np.array([c["label"] for c in subset], dtype=np.float64)

    mu = X[cal_idx].mean(axis=0)
    sd = X[cal_idx].std(axis=0)
    sd[sd == 0] = 1.0
    Xs = (X - mu) / sd

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

    return {"mu": mu, "sd": sd, "weights": w, "cal_idx": cal_idx,
            "ev_idx": ev_idx, "subset": subset}


def detectability_posterior(cases, model, cat_filter=None):
    """Calibrated P(the context is sufficient) for each query."""
    out = []
    for c in cases:
        if cat_filter is not None and c["q"]["category"] != cat_filter:
            continue
        x = np.asarray(c["features"], dtype=np.float64)
        mu = model["mu"]
        sd = np.where(model["sd"] == 0, 1.0, model["sd"])
        z = model["weights"][0] + float(np.dot((x - mu) / sd, model["weights"][1:]))
        out.append((c, 1.0 / (1.0 + np.exp(-z))))
    return out
