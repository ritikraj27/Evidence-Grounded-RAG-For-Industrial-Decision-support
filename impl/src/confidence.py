"""Retrieval-confidence gating: the Bayesian posterior, and its calibration.

Why a gate at all
-----------------
The failure this defends against is specific: the retriever returns nothing
relevant, the generator is still called, and it produces a fluent, plausible,
*wrong* answer. In an industrial setting the wrong answer can be a wrong
economic order quantity or a wrong safety-stock rule. The framework's answer
is to make the "there is no evidence" path structural rather than advisory --
a module in the pipeline that the generator cannot talk its way past.

The derivation
--------------
Let R be the event "this chunk is relevant to the user's question" and let d
be the evidence we have about it (the reranker's score, the chunk's rank, its
lexical overlap, ...). We want P(R | d).

Bayes' theorem gives the posterior in terms of the likelihood ratio:

    P(R | d) = [ P(d | R) * P(R) ] / P(d)
             = P(R) * [ P(d | R) / P(d | ¬R) ] / P(d | ¬R)

Dividing numerator and denominator by P(d | ¬R):

    P(R | d) = [ P(R) / P(d | ¬R) ] * [ P(d | R) / P(d | ¬R) ]

The first bracket is the prior odds; the second is the likelihood ratio (the
"Bayes factor"). This decomposition matters because it tells us what we are
actually estimating: the prior P(R) comes from the base rate of relevance in
the corpus, and the likelihood ratio comes from how surprising the observed
evidence is.

For a scalar evidence feature x (here: the cross-encoder reranker score),
the most tractable model is a logistic (logit) model on the log-odds scale.
Under it,

    log [ P(R|d) / P(¬R|d) ] = β0 + β1 * x

so

    P(R | d) = sigmoid(β0 + β1 * x) = 1 / (1 + exp(-(β0 + β1 x)))

This is Platt scaling's form, and it is exactly what the Sept 2026 report used
(β0 = 2.943, β1 = 1.680 on a 30-query calibration set). Note the mapping:
β0 encodes the prior odds (at x = 0 the odds are exp(2.943) ≈ 19:1 in favour
of relevance) and β1 encodes how much one unit of reranker score moves the
odds (exp(1.680) ≈ 5.4x per point).

**Why the score must be calibrated before it can be thresholded.** A raw
cross-encoder score is a logit. It is not a probability and it is not even on
a common scale across queries: a score of 3.0 might mean "certainly relevant"
for one query and "borderline" for another, because the reranker's output
distribution shifts with query difficulty and with the number of candidates.
Thresholding an uncalibrated score is therefore a category error. We must map
scores to probabilities first, using held-out data, and then threshold the
*probability*.

Two calibration routes are provided:
  * Platt scaling -- fit (β0, β1) by maximum likelihood on held-out labels.
    Two parameters, so low variance; the shape of the map is fixed to a
    logistic, which is a real assumption.
  * Isotonic regression -- fit a free-form monotone map. More flexible, lower
    bias, higher variance; needs more calibration data than a sigmoid.

Calibration quality is measured with:
  * **Brier score** = mean squared error between predicted probability and the
    binary label. Lower is better. Decomposes into calibration error and
    refinement error.
  * **Expected Calibration Error (ECE)** = Σ_b (n_b/N) * |acc_b - conf_b|,
    the sample-size-weighted gap between confidence and accuracy within each
    equal-width probability bin. This is the number a reviewer will ask for.
  * **Reliability diagram** -- accuracy vs confidence per bin, with the
    diagonal as the perfect-calibration reference.
  * **Selective risk / risk-coverage** -- if the gate abstains on the
    lowest-confidence fraction f, what is the error rate on what remains?
    This is the operational question the gate exists to answer, and it is the
    right way to pick tau: choose the point where the curve has flattened.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


def sigmoid(z: np.ndarray | float) -> np.ndarray | float:
    """Numerically stable logistic function."""
    z = np.asarray(z, dtype=np.float64)
    out = np.empty_like(z)
    pos = z >= 0
    out[pos] = 1.0 / (1.0 + np.exp(-z[pos]))
    ez = np.exp(z[~pos])
    out[~pos] = ez / (1.0 + ez)
    return out if out.ndim else float(out)


def posterior_from_score(score: np.ndarray | float, beta0: float, beta1: float):
    """Calibrated P(relevant | score) under a fitted logistic model."""
    return sigmoid(beta0 + beta1 * np.asarray(score, dtype=np.float64))


def fit_platt(scores: np.ndarray, labels: np.ndarray, max_iter: int = 200) -> tuple[float, float]:
    """Maximum-likelihood fit of the logistic calibration map.

    Uses Newton's method on the log-loss. The log-loss for a logistic model is

        L(β) = - [ Σ y_i log σ(β0 + β1 x_i)
                   + Σ (1 - y_i) log(1 - σ(β0 + β1 x_i)) ]

    which is convex in (β0, β1), so Newton's method converges reliably. The
    gradient is the usual score function

        ∂L/∂β0 = Σ (σ(z_i) - y_i)
        ∂L/β1 = Σ (σ(z_i) - y_i) * x_i

    and the Hessian is

        ∂²L/∂β0² = Σ p_i (1 - p_i)
        ∂²L/∂β0∂β1 = Σ p_i (1 - p_i) x_i
        ∂²L/∂β1² = Σ p_i (1 - p_i) x_i²

    with p_i = σ(z_i). A small ridge term (lambda) is added to the Hessian for
    numerical stability when the score has (near-)zero variance, which would
    otherwise make the design matrix singular.
    """
    x = np.asarray(scores, dtype=np.float64)
    y = np.asarray(labels, dtype=np.float64)
    if x.size == 0:
        return 0.0, 0.0
    if x.size == 1 or np.allclose(x, x[0]):
        # Degenerate: no slope information. Fall back to the base rate.
        base = float(np.clip(y.mean(), 1e-6, 1 - 1e-6))
        return float(np.log(base / (1 - base))), 0.0

    # Centre the feature for conditioning; this does not change the model.
    x_mean = x.mean()
    x_std = x.std() or 1.0
    xs = (x - x_mean) / x_std

    beta = np.zeros(2)  # [intercept, slope] in the centred parameterisation
    ridge = 1e-6
    for _ in range(max_iter):
        z = beta[0] + beta[1] * xs
        p = sigmoid(z)
        g = np.array([np.sum(p - y), np.sum((p - y) * xs)])
        w = p * (1 - p)
        h = np.array(
            [
                [np.sum(w) + ridge, np.sum(w * xs)],
                [np.sum(w * xs), np.sum(w * xs * xs) + ridge],
            ]
        )
        try:
            step = np.linalg.solve(h, g)
        except np.linalg.LinAlgError:
            break
        beta = beta - step
        if np.max(np.abs(step)) < 1e-10:
            break

    # Undo the centring: β0_orig = β0_centred - β1_centred * x_mean / x_std
    b1 = beta[1] / x_std
    b0 = beta[0] - b1 * x_mean
    return float(b0), float(b1)


def fit_isotonic(scores: np.ndarray, labels: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Fit a free-form monotone (isotonic) calibration map via PAVA.

    Pool Adjacent Violators Algorithm: repeatedly find the longest adjacent
    pair of blocks whose fitted values decrease, and merge them. This is the
    standard exact algorithm for the least-squares isotonic regression
    problem, O(n) with a union-find implementation.
    """
    x = np.asarray(scores, dtype=np.float64)
    y = np.asarray(labels, dtype=np.float64)
    order = np.argsort(x, kind="mergesort")
    xs, ys = x[order], y[order]

    values = list(ys.astype(np.float64))
    weights = [1.0] * len(ys)
    blocks: list[list] = []  # [start, end, value, weight]
    i = 0
    while i < len(values):
        start = i
        val = values[i]
        wt = weights[i]
        i += 1
        while blocks and blocks[-1][2] > val:
            b_start, b_end, b_val, b_w = blocks.pop()
            start = b_start
            val = (b_val * b_w + val * wt) / (b_w + wt)
            wt = b_w + wt
        blocks.append([start, i - 1, val, wt])

    fitted = np.empty(len(ys), dtype=np.float64)
    for b_start, b_end, b_val, _ in blocks:
        fitted[b_start : b_end + 1] = b_val
    inv = np.empty_like(order)
    inv[order] = np.arange(len(order))
    return x[order], fitted[inv]


def apply_isotonic(x_new: np.ndarray, x_fit: np.ndarray, y_fit: np.ndarray) -> np.ndarray:
    """Apply a fitted isotonic map to new scores (piecewise-constant, with
    linear interpolation between knots)."""
    x_new = np.asarray(x_new, dtype=np.float64)
    return np.interp(x_new, x_fit, y_fit, left=y_fit[0], right=y_fit[-1])


def brier_score(probs: np.ndarray, labels: np.ndarray) -> float:
    """Mean squared error between predicted probability and binary outcome."""
    p = np.asarray(probs, dtype=np.float64)
    y = np.asarray(labels, dtype=np.float64)
    if p.size == 0:
        return float("nan")
    return float(np.mean((p - y) ** 2))


def expected_calibration_error(
    probs: np.ndarray, labels: np.ndarray, n_bins: int = 10
) -> float:
    """Sample-weighted mean gap between confidence and empirical accuracy."""
    p = np.asarray(probs, dtype=np.float64)
    y = np.asarray(labels, dtype=np.float64)
    if p.size == 0:
        return float("nan")
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    ece = 0.0
    for lo, hi in zip(edges[:-1], edges[1:]):
        # np.histogram-style binning; the last bin is closed on the right.
        if hi >= 1.0:
            mask = (p >= lo) & (p <= hi)
        else:
            mask = (p >= lo) & (p < hi)
        if not mask.any():
            continue
        conf = float(p[mask].mean())
        acc = float(y[mask].mean())
        ece += (mask.sum() / p.size) * abs(acc - conf)
    return float(ece)


def reliability_table(
    probs: np.ndarray, labels: np.ndarray, n_bins: int = 10
) -> list[dict]:
    """Per-bin (confidence, accuracy, count) for the reliability diagram."""
    p = np.asarray(probs, dtype=np.float64)
    y = np.asarray(labels, dtype=np.float64)
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    rows = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        if hi >= 1.0:
            mask = (p >= lo) & (p <= hi)
        else:
            mask = (p >= lo) & (p < hi)
        if not mask.any():
            rows.append({"bin_lo": float(lo), "bin_hi": float(hi), "count": 0,
                         "confidence": None, "accuracy": None})
            continue
        rows.append(
            {
                "bin_lo": float(lo),
                "bin_hi": float(hi),
                "count": int(mask.sum()),
                "confidence": float(p[mask].mean()),
                "accuracy": float(y[mask].mean()),
            }
        )
    return rows


def selective_risk_curve(
    probs: np.ndarray, labels: np.ndarray
) -> list[tuple[float, float, float]]:
    """Risk-coverage curve.

    For each coverage level f (the fraction of queries the system chooses to
    answer), sort by confidence descending, keep the top f fraction, and
    record the error rate among them and the accuracy.

    Returns a list of (coverage, accuracy, error_rate) sorted by coverage.
    """
    p = np.asarray(probs, dtype=np.float64)
    y = np.asarray(labels, dtype=np.float64)
    if p.size == 0:
        return []
    order = np.argsort(-p)
    ys = y[order]
    n = len(ys)
    correct = np.cumsum(ys)
    out = []
    for k in range(1, n + 1):
        acc = correct[k - 1] / k
        out.append((k / n, float(acc), float(1.0 - acc)))
    return out


@dataclass
class GateDecision:
    """The gate's verdict for one query."""

    accept: bool
    best_posterior: float
    threshold: float
    #: chunk ids that survived the gate
    accepted_chunks: list[str]
    #: The user-facing refusal, when the gate rejects.
    message: str = ""


NO_EVIDENCE_MESSAGE = (
    "No evidence in the indexed documentation supports an answer to this "
    "question. The retrieval-confidence gate rejected the retrieved passages "
    "(calibrated sufficiency probability "
    "{posterior:.3f} < threshold {tau:.3f}). No answer has been generated, "
    "because generating one would mean inventing it."
)


#: The five query-level signals the gate is calibrated on. Each is computed
#: from the retrieved set before any generation happens.
SUFFICIENCY_FEATURES = (
    "top1_rerank",
    "mean_top3_rerank",
    "top1_bm25",
    "max_rrf",
    "n_candidates_above_bar",
)


def detectability_features(
    top1_rerank: float,
    mean_top3_rerank: float,
    top1_bm25: float,
    max_rrf: float,
    n_candidates_above_bar: float,
) -> list[float]:
    """Build the query-level feature vector the gate is calibrated on.

    The gate decides a *query-level* question -- "does this retrieved context
    contain sufficient evidence to answer at all?" -- not a chunk-level one
    ("is this chunk the gold one?"). The distinction matters: with one gold
    chunk among ~50 candidates, a chunk-level classifier is right 98% of the
    time by answering "nothing is relevant", and maximum-likelihood fitting
    duly returns a large negative intercept. Calibrating at the query level
    removes that degenerate solution.
    """
    return [
        float(top1_rerank),
        float(mean_top3_rerank),
        float(top1_bm25),
        float(max_rrf),
        float(n_candidates_above_bar),
    ]


def detectability_posterior(features, model: dict) -> float:
    """Calibrated P(the retrieved context is sufficient to answer).

    `model` is the fitted artefact written by `run_gate.py`: the feature mean
    and standard deviation (from the calibration split) and the logistic
    weights.
    """
    x = np.asarray(features, dtype=np.float64)
    mu = np.asarray(model["mu"], dtype=np.float64)
    sd = np.asarray(model["sd"], dtype=np.float64)
    sd = np.where(sd == 0, 1.0, sd)
    z = float(np.asarray(model["weights"], dtype=np.float64)[0]) + float(
        np.dot((x - mu) / sd, np.asarray(model["weights"], dtype=np.float64)[1:])
    )
    return float(sigmoid(z))


def apply_gate(
    chunk_ids: list[str],
    posterior: np.ndarray,
    tau: float = 0.5,
) -> GateDecision:
    """Apply the confidence gate to a reranked chunk set.

    The gate is *non-bypassable by construction*: this function returns the
    set of chunks that may reach the generator, and the generator is only
    called if that set is non-empty. There is no flag that lets the LLM
    override it, and there is no prompt instruction asking the LLM to decide
    whether the evidence is good enough -- that decision is made here, in
    code, on a calibrated probability, before any generation happens.

    A chunk is accepted when its calibrated posterior is at or above tau.
    """
    posterior = np.asarray(posterior, dtype=np.float64)
    if posterior.size == 0:
        return GateDecision(
            accept=False,
            best_posterior=0.0,
            threshold=tau,
            accepted_chunks=[],
            message=NO_EVIDENCE_MESSAGE.format(posterior=0.0, tau=tau),
        )
    mask = posterior >= tau
    accepted = [cid for cid, keep in zip(chunk_ids, mask) if keep]
    best = float(posterior.max())
    if not accepted:
        return GateDecision(
            accept=False,
            best_posterior=best,
            threshold=tau,
            accepted_chunks=[],
            message=NO_EVIDENCE_MESSAGE.format(posterior=best, tau=tau),
        )
    return GateDecision(
        accept=True, best_posterior=best, threshold=tau, accepted_chunks=accepted
    )
