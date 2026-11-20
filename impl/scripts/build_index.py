#!/usr/bin/env python3
"""Build the retrieval index and cache it to disk.

Separate from the experiments so the corpus and the index can be built (and
rebuilt) without running an experiment, and so the README's reproduction
steps are commands that actually exist.

Two environment variables tune the *cost* of the build, not its results:

``MTP_TORCH_THREADS``
    The encoder is the most expensive step in the suite and is
    embarrassingly parallel. Torch defaults to a conservative thread count
    that leaves most of the machine idle.

``MTP_MAX_SEQ_LENGTH``
    The tokenised length the encoder is allowed to see. BGE-M3's own limit
    is 8,192 tokens; the median chunk in these corpora is 176. Setting 512
    -- the same window the cross-encoder uses -- leaves the vectors of the
    97.5% of chunks that fit unchanged and makes the encoding roughly
    fifty times faster. The limit is part of the embedding cache key, and
    it is unset by default, so the corpora already encoded keep their
    vectors and their numbers.
"""
from __future__ import annotations

import dataclasses
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import ARTIFACT_DIR, CONFIG, CORPUS_DIR  # noqa: E402
from src.pipeline import build_index  # noqa: E402


def main() -> int:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    threads = int(os.environ.get("MTP_TORCH_THREADS", "0") or 0)
    if threads <= 0:
        threads = os.cpu_count() or 4
    try:
        import torch

        torch.set_num_threads(threads)
        print(f"[index] torch threads: {threads}")
    except Exception as exc:  # pragma: no cover - torch is always present
        print(f"[index] could not set the thread count: {exc}")

    config = CONFIG
    limit = os.environ.get("MTP_MAX_SEQ_LENGTH", "").strip()
    if limit:
        config = dataclasses.replace(
            CONFIG,
            embedding=dataclasses.replace(
                CONFIG.embedding, max_seq_length=int(limit)))
        print(f"[index] encoder sequence limit: {limit} tokens")

    print(f"[index] corpus: {CORPUS_DIR}")
    index = build_index(CORPUS_DIR, config)
    cache = ARTIFACT_DIR / "index"
    index.save(cache)
    stats = index.stats if hasattr(index, "stats") else {}
    print(f"[index] wrote {cache}.json and {cache}.npy")
    if stats:
        print(f"[index] {stats}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
