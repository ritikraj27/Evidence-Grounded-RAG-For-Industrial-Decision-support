"""Neural components: dense embedding, cross-encoder reranking, NLI scoring.

All three are thin, well-documented wrappers so that the *math* lives in
readable form and the *model* is swappable.
"""
from __future__ import annotations

import hashlib
import json
import os
from functools import lru_cache
from pathlib import Path

import numpy as np

from .config import ARTIFACT_DIR

CACHE_DIR = ARTIFACT_DIR / "model_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------------------------------
# Dense embeddings
# --------------------------------------------------------------------------
#
# What an embedding is
# --------------------
# A bi-encoder maps a text to a fixed-length vector in R^d such that texts
# that mean similar things land near each other. The model is a Transformer
# whose final hidden state is pooled (mean or CLS) and optionally projected.
#
# The retrieval score is cosine similarity:
#
#     cos(q, d) = (q . d) / (||q|| ||d||)
#
# Written out, cos(q,d) = sum_i q_i d_i / (sqrt(sum_i q_i^2) sqrt(sum_i d_i^2)).
# This is the cosine of the angle between the two vectors: 1 means identical
# direction, 0 means orthogonal, -1 means opposite. Because it divides out
# the vector norms, a long document does not score higher simply for having a
# larger norm, which matters when embeddings are compared across documents
# of very different lengths.
#
# Note that "cosine similarity" and "dot product" are identical when the
# vectors are L2-normalised, which is why the code below normalises once and
# then uses a plain matrix product -- that is the standard trick for making
# ANN search over a large collection fast (a dot-product index is
# HNSW-friendly; a non-normalised cosine index is not).
#
# The 384-dimension figure for all-MiniLM-L6-v2 is simply the model's output
# width; it has no mathematical meaning beyond that.


@lru_cache(maxsize=4)
def _get_embedder(model_name: str):
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(model_name, device="cpu")


def embed_texts(
    texts: list[str],
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    batch_size: int = 64,
    normalize: bool = True,
    query_prefix: str = "",
    is_query: bool = False,
    dim: int = 384,
    max_seq_length: int | None = None,
) -> np.ndarray:
    """Embed a list of texts into an (n, d) float32 matrix.

    Results are cached on disk by content hash so repeated experiment runs do
    not re-encode the same corpus. `dim` is the model's output width; it is a
    parameter because the encoder is configurable and the empty-input shape
    has to match it.
    """
    if not texts:
        return np.zeros((0, dim), dtype=np.float32)

    key_parts = [model_name, normalize, query_prefix, is_query, texts]
    if max_seq_length is not None:
        key_parts.append(max_seq_length)
    key = hashlib.sha256(
        json.dumps(key_parts).encode()
    ).hexdigest()[:32]
    cache_file = CACHE_DIR / f"emb_{key}.npy"
    if cache_file.exists():
        return np.load(cache_file)

    model = _get_embedder(model_name)
    payload = [query_prefix + t for t in texts] if is_query and query_prefix else list(texts)
    previous = getattr(model, "max_seq_length", None)
    if max_seq_length is not None:
        model.max_seq_length = max_seq_length
    try:
        vecs = model.encode(
            payload,
            batch_size=batch_size,
            convert_to_numpy=True,
            normalize_embeddings=normalize,
            show_progress_bar=False,
        ).astype(np.float32)
    finally:
        if max_seq_length is not None and previous is not None:
            model.max_seq_length = previous
    np.save(cache_file, vecs)
    return vecs


def cosine_similarity_matrix(queries: np.ndarray, docs: np.ndarray) -> np.ndarray:
    """(n_queries, n_docs) cosine similarity matrix.

    With L2-normalised inputs this equals the raw dot product; the explicit
    renormalisation keeps the function correct even if a caller passes
    un-normalised vectors. A 1-D query vector is promoted to a single-row
    matrix so the caller never has to care about the rank of its input.
    """
    queries = np.atleast_2d(np.asarray(queries, dtype=np.float64))
    docs = np.atleast_2d(np.asarray(docs, dtype=np.float64))
    q = queries / (np.linalg.norm(queries, axis=1, keepdims=True) + 1e-12)
    d = docs / (np.linalg.norm(docs, axis=1, keepdims=True) + 1e-12)
    return q @ d.T


def dense_top_k(
    query_vec: np.ndarray,
    doc_vecs: np.ndarray,
    doc_ids: list[str],
    k: int,
) -> list[tuple[str, float]]:
    """Rank documents by cosine similarity and return the top k."""
    if not doc_ids:
        return []
    sims = cosine_similarity_matrix(query_vec, doc_vecs)[0]
    k = min(k, len(doc_ids))
    if k < len(sims):
        # argpartition places the k-th smallest value of -sims at position k,
        # so the first k positions hold the k largest similarities. The
        # argsort then puts them in descending order.
        idx = np.argpartition(-sims, k)[:k]
    else:
        idx = np.arange(len(sims))
    idx = idx[np.argsort(-sims[idx])]
    return [(doc_ids[i], float(sims[i])) for i in idx]


# --------------------------------------------------------------------------
# Cross-encoder reranking
# --------------------------------------------------------------------------
#
# Bi-encoder vs cross-encoder
# ---------------------------
# A bi-encoder (the dense retriever above) encodes the query and the document
# INDEPENDENTLY, then compares the two vectors. That is what makes pre-computing
# every document embedding possible -- and therefore what makes approximate
# nearest-neighbour search over millions of chunks feasible. The price is that
# the two texts never see each other: the model cannot represent "this
# passage answers *that* question", only "this passage is about something
# like this question".
#
# A cross-encoder concatenates query and document and runs the Transformer
# over the pair:
#
#     score(q, d) = w^T * Transformer([CLS] q [SEP] d [SEP])[CLS]
#
# so every token of the document can attend to every token of the query. It
# is strictly more expressive. The price is cost: you must run one forward
# pass per (query, document) pair, so it cannot be applied to a corpus of
# millions -- only to the shortlist the bi-encoder produced.
#
# This is why the pipeline is: bi-encoder (cheap, exhaustive) -> fusion
# (combine two shortlists) -> cross-encoder (expensive, precise) -> gate.


@lru_cache(maxsize=4)
def _get_cross_encoder(model_name: str):
    from sentence_transformers import CrossEncoder

    return CrossEncoder(model_name, device="cpu")


def rerank(
    query: str,
    pairs: list[tuple[str, str]],
    model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
) -> list[tuple[str, float]]:
    """Score (query, document) pairs and return them sorted best-first.

    The score is a raw logit from the MS MARCO ranking head. It is NOT a
    probability and its scale is not comparable across queries -- which is
    exactly why the confidence gate must calibrate it before thresholding.
    """
    if not pairs:
        return []
    model = _get_cross_encoder(model_name)
    scores = model.predict([(query, doc) for _, doc in pairs], show_progress_bar=False)
    scored = [(cid, float(s)) for (cid, _), s in zip(pairs, scores)]
    scored.sort(key=lambda t: -t[1])
    return scored


# --------------------------------------------------------------------------
# Natural Language Inference
# --------------------------------------------------------------------------
#
# NLI in three labels
# -------------------
# An NLI model reads a *premise* and a *hypothesis* and returns a distribution
# over:
#
#   entailment   -- the premise makes the hypothesis true
#   neutral      -- the premise neither proves nor disproves the hypothesis
#   contradiction -- the premise makes the hypothesis false
#
# For contradiction detection, the two retrieved passages play the roles of
# two competing premises. The pair is contradictory when one passage asserts
# something that the other denies.
#
# DeBERTa-v3 NLI models (Lewis et al., 2020; He et al., 2021) are trained on
# MNLI plus auxiliary NLI corpora. Note the ordering convention: the model
# expects (premise, hypothesis) in that order for a cross-encoder NLI head.


@lru_cache(maxsize=4)
def _get_nli(model_name: str):
    from sentence_transformers import CrossEncoder

    return CrossEncoder(model_name, device="cpu")


def nli_probs(
    pairs: list[tuple[str, str]],
    model_name: str = "cross-encoder/nli-deberta-v3-small",
) -> list[dict[str, float]]:
    """Return P(entailment), P(neutral), P(contradiction) for each pair.

    The cross-encoder/nli-* checkpoints emit a 3-way logit vector; a softmax
    over those logits gives the three probabilities.
    """
    if not pairs:
        return []
    import torch

    model = _get_nli(model_name)
    logits = model.predict([(p, h) for p, h in pairs], show_progress_bar=False)
    logits = np.atleast_2d(np.asarray(logits, dtype=np.float64))
    if logits.shape[1] == 2:  # binary model: [contradiction, entailment]
        probs = 1.0 / (1.0 + np.exp(-logits))
        return [
            {"entailment": float(p[1]), "neutral": 0.0, "contradiction": float(p[0])}
            for p in probs
        ]
    e = np.exp(logits - logits.max(axis=1, keepdims=True))
    probs = e / e.sum(axis=1, keepdims=True)
    # Label order for the deberta-v3 MNLI checkpoints is
    # [contradiction, entailment, neutral].
    return [
        {
            "contradiction": float(p[0]),
            "entailment": float(p[1]),
            "neutral": float(p[2]),
        }
        for p in probs
    ]


def nli_softmax_torch(model_name: str, pairs: list[tuple[str, str]]) -> np.ndarray:
    """Raw softmax probabilities from the NLI model, in the checkpoint's own
    label order [contradiction, entailment, neutral]. Kept separate so the
    label-order convention is visible in one place."""
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    tok = AutoTokenizer.from_pretrained(model_name)
    mdl = AutoModelForSequenceClassification.from_pretrained(model_name)
    mdl.eval()
    outs = []
    with torch.no_grad():
        for i in range(0, len(pairs), 16):
            batch = pairs[i : i + 16]
            enc = tok(
                [b[0] for b in batch],
                [b[1] for b in batch],
                truncation=True,
                max_length=256,
                padding=True,
                return_tensors="pt",
            )
            logits = mdl(**enc).logits
            outs.append(torch.softmax(logits, dim=-1).numpy())
    return np.concatenate(outs, axis=0) if outs else np.zeros((0, 3))
