#!/usr/bin/env python3
"""Experiment 23 -- how long a query takes, stage by stage.

Every other measurement in this project asks how good the answers are. This
one asks how long the system takes to produce them, which is the question a
panel member asks once the results have been read out: how long does a user
wait, and what does the wait consist of.

The retrieval path is measured directly, on the real index, with the real
models, by timing each stage inside the framework rather than by timing a
re-implementation of it. The stages are wrapped in place: the query
embedding, the dense leg, the lexical leg, the rank fusion, the modality
quota, the cross-encoder rerank, and the gate itself.

The generation stage cannot be measured here, because it calls a language
model over the network. It is derived instead from the archived arm totals:
the arm totals are the retrieval path plus the model calls, and the retrieval
path is what this experiment measures, so the difference is the generation.

A refusal is not a faster answer. The gate's decision is taken at the end of
the retrieval path, so a refused query costs exactly what an accepted one
costs up to that point; what a refusal saves is the generation, because the
model is never called. That is why the refusal path and the answer path are
reported separately.

Usage:
    MTP_VARIANT=focus .venv/bin/python impl/experiments/run_latency.py
"""
from __future__ import annotations

import json
import os
import statistics
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))

from common import load_benchmark, load_index, write_result  # noqa: E402
from src import config as config_mod  # noqa: E402
from src import pipeline as pipeline_mod  # noqa: E402
from src.pipeline import Framework  # noqa: E402

RESULT_NAME = "exp23_latency"

#: The stages that are timed, and the module attribute that performs each.
#: The wrapper is installed on the module the framework calls it from, so the
#: framework's own code path is what is measured.
STAGES = ("embed", "dense_top_k", "bm25", "fusion", "quota", "rerank", "gate")


def _stats(samples: list[float]) -> dict:
    """The distribution of a set of timings, in milliseconds."""
    if not samples:
        return {"n": 0}
    s = sorted(samples)
    return {
        "n": len(s),
        "mean_ms": round(statistics.fmean(s), 1),
        "median_ms": round(statistics.median(s), 1),
        "p90_ms": round(s[int(0.90 * (len(s) - 1))], 1),
        "p95_ms": round(s[int(0.95 * (len(s) - 1))], 1),
        "max_ms": round(s[-1], 1),
        "min_ms": round(s[0], 1),
    }


class _Timers:
    """Accumulate the time spent in each stage."""

    def __init__(self) -> None:
        self.acc: dict[str, float] = {k: 0.0 for k in STAGES}
        self.calls: dict[str, int] = {k: 0 for k in STAGES}

    def wrap(self, module, name: str, stage: str):
        """Wrap a module-level function so its time is attributed to a stage."""
        original = getattr(module, name)

        def timed(*args, **kwargs):
            t0 = time.perf_counter()
            try:
                return original(*args, **kwargs)
            finally:
                self.acc[stage] += (time.perf_counter() - t0) * 1000.0
                self.calls[stage] += 1

        setattr(module, name, timed)

    def restore(self, module, name: str, original) -> None:
        setattr(module, name, original)


def main() -> int:
    index = load_index()
    bench = load_benchmark()
    fw = Framework(index)
    cfg = config_mod.CONFIG

    print(f"[exp23] index: {len(index.chunk_ids)} chunks", flush=True)
    print(f"[exp23] embedding model {cfg.embedding.model}; reranker "
          f"{cfg.rerank.model}; rerank pool {cfg.rerank.top_n}; "
          f"final context {cfg.rerank.top_k_final}", flush=True)

    queries = list(bench["queries"])

    # The first call loads the embedding and cross-encoder models, which is
    # a startup cost and not a per-query cost. It is run on a query that is
    # not in the benchmark, so that no benchmark query is served from the
    # in-memory rerank cache and every one of them pays a live rerank.
    warm = fw.retrieve("a warm-up query that is not in the benchmark",
                       category=None)
    print(f"[exp23] warm-up done (gate rejected: {warm.gate_rejected})",
          flush=True)

    timers = _Timers()
    saved = []
    for name, stage in (("embed_texts", "embed"),
                        ("dense_top_k", "dense_top_k"),
                        ("reciprocal_rank_fusion", "fusion"),
                        ("apply_modality_quota", "quota"),
                        ("_rerank_cached", "rerank")):
        saved.append((pipeline_mod, name, getattr(pipeline_mod, name)))
        timers.wrap(pipeline_mod, name, stage)

    import src.confidence as confidence_mod
    import src.lexical as lexical_mod
    saved.append((confidence_mod, "detectability_features",
                  confidence_mod.detectability_features))
    saved.append((confidence_mod, "detectability_posterior",
                  confidence_mod.detectability_posterior))
    saved.append((confidence_mod, "apply_gate", confidence_mod.apply_gate))
    timers.wrap(confidence_mod, "detectability_features", "gate")
    timers.wrap(confidence_mod, "detectability_posterior", "gate")
    timers.wrap(confidence_mod, "apply_gate", "gate")

    _orig_bm25 = lexical_mod.BM25Index.score

    def _bm25_timed(self, query, *args, **kwargs):
        t0 = time.perf_counter()
        try:
            return _orig_bm25(self, query, *args, **kwargs)
        finally:
            timers.acc["bm25"] += (time.perf_counter() - t0) * 1000.0
            timers.calls["bm25"] += 1

    lexical_mod.BM25Index.score = _bm25_timed

    totals: list[float] = []
    refused_totals: list[float] = []
    accepted_totals: list[float] = []
    n_refused = 0
    per_query: list[dict] = []

    print(f"[exp23] timing {len(queries)} queries ...", flush=True)
    for i, q in enumerate(queries, 1):
        category = None if q["category"] == "unanswerable" else q["category"]
        before = dict(timers.acc)
        t0 = time.perf_counter()
        trace = fw.retrieve(q["query"], category=category)
        elapsed = (time.perf_counter() - t0) * 1000.0
        stage_ms = {k: timers.acc[k] - before[k] for k in STAGES}
        totals.append(elapsed)
        if trace.gate_rejected:
            refused_totals.append(elapsed)
            n_refused += 1
        else:
            accepted_totals.append(elapsed)
        per_query.append({
            "query_id": q.get("query_id") or q.get("id"),
            "category": q.get("category"),
            "gate_rejected": bool(trace.gate_rejected),
            "total_ms": round(elapsed, 1),
            "stage_ms": {k: round(v, 2) for k, v in stage_ms.items()},
        })
        if i % 40 == 0:
            print(f"    {i}/{len(queries)}", flush=True)

    for module, name, original in saved:
        setattr(module, name, original)
    lexical_mod.BM25Index.score = _orig_bm25

    payload = {
        "seed": cfg.get("seed", None) if isinstance(cfg, dict) else None,
        "measurement": (
            "Wall-clock of the retrieval path (query embedding, dense leg, "
            "lexical leg, rank fusion, modality quota, cross-encoder "
            "rerank, confidence gate) on the real index with the real "
            "models, measured on this machine. The generation stage is not "
            "measured here; it is derived from the archived arm totals."),
        "machine": {
            "cpu_count": os.cpu_count(),
            "platform": sys.platform,
            "python": sys.version.split()[0],
            "numpy": np.__version__,
        },
        "config": {
            "embedding_model": cfg.embedding.model,
            "rerank_model": cfg.rerank.model,
            "rerank_pool": cfg.rerank.top_n,
            "final_context_chunks": cfg.rerank.top_k_final,
        },
        "n_queries": len(queries),
        "n_chunks": len(index.chunk_ids),
        "total": _stats(totals),
        "stages": {
            k: _stats([q["stage_ms"][k] for q in per_query])
            for k in STAGES
        },
        "gate_refused": {**_stats(refused_totals), "n_refused": n_refused},
        "gate_accepted": _stats(accepted_totals),
        "per_query": per_query,
    }
    write_result(RESULT_NAME, payload)

    t = payload["total"]
    print(f"[exp23] total per query: mean {t['mean_ms']} ms, median "
          f"{t['median_ms']} ms, p95 {t['p95_ms']} ms, max {t['max_ms']} ms")
    for k in STAGES:
        st = payload["stages"][k]
        print(f"[exp23]   {k:14s} mean {st['mean_ms']:7.1f} ms  "
              f"median {st['median_ms']:7.1f} ms  calls {timers.calls[k]}")
    print(f"[exp23] gate refused {n_refused} of {len(queries)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
