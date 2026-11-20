"""Retrieval and generation quality metrics, with the formulas written out.

Retrieval metrics
-----------------
Given a ranked list of retrieved chunk ids R = [r_1, ..., r_k] and the set of
relevant chunk ids for that query, Rel:

**Recall@k** = |R_k ∩ Rel| / |Rel|. "Of the passages that should have been
found, what fraction did we find in the top k?" This is the metric that
matters for a decision-support system: a missed safety-stock table is a
failure regardless of what else was retrieved.

**Precision@k** = |R_k ∩ Rel| / k. "Of what we retrieved, how much was
relevant?" Useful for diagnosing over-retrieval, but it is not the metric to
optimise when the generator can ignore irrelevant context.

**MRR (Mean Reciprocal Rank)** = (1/|Q|) Σ_q 1/rank_q of the first relevant
document. Sensitive to whether the right answer is *first*, which matches
the fact that LLMs attend most strongly to early context ("lost in the
middle", Liu et al., TACL 2024).

**nDCG@k** = DCG@k / IDCG@k, where

    DCG@k = Σ_{i=1..k} (2^rel_i - 1) / log2(i + 1)

with rel_i the graded relevance of the i-th retrieved item (0 if not
relevant, 1 if relevant, up to 3 for a "critical" passage such as the table
carrying a binding requirement). The exponential gain 2^rel - 1 makes the
difference between relevance 0 and 1 worth more than between 1 and 2, which
is the standard "graded relevance" preference. IDCG@k is DCG@k computed on
the ideal ordering (all relevant items first, in descending grade), so nDCG is
normalised to [0, 1] and comparable across queries with different numbers of
relevant documents.

**Modality recall** = the same Recall@k restricted to relevant chunks of a
given modality. This is how the modality-quota claim (D2) is tested: if
text dominates the corpus, a system with no quota will have poor *table*
recall even when its overall recall looks healthy.

Generation metrics
------------------
**Faithfulness** (RAGAS-style): the fraction of claims in the answer that are
entailed by the retrieved context. Operationally: decompose the answer into
atomic claims, run an NLI entailment model on (context, claim) pairs, and
count a claim as supported if max over context chunks of P(entail) exceeds a
threshold.

**Citation precision** (ALCE-style): the fraction of citations attached to
claims that actually support the claim they are attached to.

**Citation recall** (ALCE-style): the fraction of claims that *could* be
cited (i.e. are supported by some retrieved passage) that actually carry a
citation.

The distinction matters: a system that cites nothing has perfect citation
precision and zero citation recall. Both are reported.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


def recall_at_k(retrieved: list[str], relevant: set[str], k: int) -> float:
    if not relevant:
        return float("nan")
    return len(set(retrieved[:k]) & relevant) / len(relevant)


def precision_at_k(retrieved: list[str], relevant: set[str], k: int) -> float:
    if k <= 0:
        return 0.0
    return len(set(retrieved[:k]) & relevant) / k


def reciprocal_rank(retrieved: list[str], relevant: set[str]) -> float:
    for i, doc_id in enumerate(retrieved, start=1):
        if doc_id in relevant:
            return 1.0 / i
    return 0.0


def dcg_at_k(grades: list[float], k: int) -> float:
    import math

    return sum(
        (2.0 ** g - 1.0) / math.log2(i + 1)
        for i, g in enumerate(grades[:k], start=1)
    )


def ndcg_at_k(retrieved: list[str], relevant: set[str], grades: dict[str, float], k: int) -> float:
    actual = [grades.get(d, 0.0) for d in retrieved]
    ideal_grades = sorted(grades.values(), reverse=True)
    idcg = dcg_at_k(ideal_grades, k)
    if idcg == 0:
        return float("nan")
    return dcg_at_k(actual, k) / idcg


@dataclass
class RetrievalEval:
    """Aggregate retrieval metrics over a benchmark."""

    n_queries: int = 0
    recall_at_5: float = 0.0
    recall_at_10: float = 0.0
    recall_at_20: float = 0.0
    precision_at_10: float = 0.0
    mrr: float = 0.0
    ndcg_at_10: float = 0.0
    #: Per-modality recall, e.g. {"table": 0.41, "chart": 0.12}
    modality_recall: dict[str, float] = field(default_factory=dict)
    #: Mean number of chunks returned before gating
    mean_candidates: float = 0.0
    #: Mean number of chunks that survived the confidence gate
    mean_accepted: float = 0.0
    #: Fraction of queries the gate rejected
    rejection_rate: float = 0.0

    def to_dict(self) -> dict:
        return {
            "n_queries": self.n_queries,
            "recall@5": self.recall_at_5,
            "recall@10": self.recall_at_10,
            "recall@20": self.recall_at_20,
            "precision@10": self.precision_at_10,
            "mrr": self.mrr,
            "nDCG@10": self.ndcg_at_10,
            "modality_recall": self.modality_recall,
            "mean_candidates": self.mean_candidates,
            "mean_accepted": self.mean_accepted,
            "rejection_rate": self.rejection_rate,
        }

    def __str__(self) -> str:
        return (
            f"R@{5}={self.recall_at_5:.3f} R@{10}={self.recall_at_10:.3f} "
            f"R@{20}={self.recall_at_20:.3f} P@10={self.precision_at_10:.3f} "
            f"MRR={self.mrr:.3f} nDCG@10={self.ndcg_at_10:.3f} "
            f"reject={self.rejection_rate:.3f}"
        )


def evaluate_retrieval(
    runs: list[list[str]],
    relevances: list[set[str]],
    grades: list[dict[str, float]] | None = None,
    modality_of: dict[str, str] | None = None,
    modality_relevance: list[dict[str, set[str]]] | None = None,
    gate_stats: list[tuple[int, int]] | None = None,
) -> RetrievalEval:
    """Compute aggregate retrieval metrics over all queries."""
    if not runs:
        return RetrievalEval()
    grades = grades or [{} for _ in runs]
    n = len(runs)
    r5 = r10 = r20 = p10 = mrr = ndcg = 0.0
    counts = 0
    for i, run in enumerate(runs):
        rel = relevances[i]
        # Unanswerable queries have an empty relevance set, so recall and
        # nDCG are undefined for them. They are excluded from these
        # aggregates rather than averaged in as zero -- a zero would make the
        # system look as if it failed to retrieve the answer, when in fact
        # there is no answer to retrieve. Their behaviour is measured by the
        # gate's rejection rate instead.
        if not rel:
            continue
        r5 += recall_at_k(run, rel, 5)
        r10 += recall_at_k(run, rel, 10)
        r20 += recall_at_k(run, rel, 20)
        p10 += precision_at_k(run, rel, 10)
        mrr += reciprocal_rank(run, rel)
        nd = ndcg_at_k(run, rel, grades[i], 10)
        ndcg += 0.0 if nd != nd else nd
        counts += 1

    mod_recall: dict[str, float] = {}
    if modality_relevance and modality_of:
        acc: dict[str, list[float]] = {}
        for i, run in enumerate(runs):
            for m, rel_m in modality_relevance[i].items():
                if not rel_m:
                    continue
                acc.setdefault(m, []).append(recall_at_k(run, rel_m, 10))
        mod_recall = {m: sum(v) / len(v) for m, v in acc.items()}

    mean_cand = mean_acc = 0.0
    rejection = 0.0
    if gate_stats:
        cands = [c for c, _ in gate_stats]
        accs = [a for _, a in gate_stats]
        mean_cand = sum(cands) / len(cands)
        mean_acc = sum(accs) / len(accs)
        rejection = sum(1 for a in accs if a == 0) / len(accs)

    denom = counts or 1
    return RetrievalEval(
        n_queries=n,
        recall_at_5=r5 / denom,
        recall_at_10=r10 / denom,
        recall_at_20=r20 / denom,
        precision_at_10=p10 / denom,
        mrr=mrr / denom,
        ndcg_at_10=ndcg / denom,
        modality_recall=mod_recall,
        mean_candidates=mean_cand,
        mean_accepted=mean_acc,
        rejection_rate=rejection,
    )


@dataclass
class GenerationEval:
    """Aggregate generation-quality metrics over the benchmark."""

    n_answers: int = 0
    #: Fraction of claims entailed by the retrieved context (higher is better).
    faithfulness: float = 0.0
    #: 1 - faithfulness. The headline hallucination rate.
    hallucination_rate: float = 0.0
    #: Fraction of claims carrying a citation that actually supports them.
    citation_precision: float = 0.0
    #: Fraction of supportable claims that carry a citation.
    citation_recall: float = 0.0
    #: Share of claims in each confidence band.
    band_counts: dict[str, int] = field(default_factory=dict)
    #: Mean information gain of a claim, in bits.
    mean_information_gain: float = 0.0

    def to_dict(self) -> dict:
        total = sum(self.band_counts.values()) or 1
        return {
            "n_answers": self.n_answers,
            "faithfulness": self.faithfulness,
            "hallucination_rate": self.hallucination_rate,
            "citation_precision": self.citation_precision,
            "citation_recall": self.citation_recall,
            "band_shares": {k: v / total for k, v in self.band_counts.items()},
            "band_counts": self.band_counts,
            "mean_information_gain_bits": self.mean_information_gain,
        }

    def __str__(self) -> str:
        return (
            f"faithfulness={self.faithfulness:.3f} "
            f"halluc={self.hallucination_rate:.3f} "
            f"citeP={self.citation_precision:.3f} citeR={self.citation_recall:.3f}"
        )


def aggregate_generation(per_answer: list[dict]) -> GenerationEval:
    """Aggregate per-answer generation metrics.

    Each per-answer dict carries: n_claims, n_supported, n_cited, n_cited_and_supported,
    n_supportable, band_counts (dict), and information gains (list of floats).
    """
    if not per_answer:
        return GenerationEval()
    tot_claims = tot_sup = tot_cited = tot_cited_ok = tot_supportable = 0
    bands: dict[str, int] = {}
    gains: list[float] = []
    for a in per_answer:
        tot_claims += a["n_claims"]
        tot_sup += a["n_supported"]
        tot_cited += a["n_cited"]
        tot_cited_ok += a["n_cited_and_supported"]
        tot_supportable += a["n_supportable"]
        for k, v in a.get("band_counts", {}).items():
            bands[k] = bands.get(k, 0) + v
        gains.extend(a.get("information_gains", []))
    return GenerationEval(
        n_answers=len(per_answer),
        faithfulness=tot_sup / tot_claims if tot_claims else 0.0,
        hallucination_rate=1.0 - (tot_sup / tot_claims if tot_claims else 0.0),
        citation_precision=tot_cited_ok / tot_cited if tot_cited else 0.0,
        citation_recall=tot_cited_ok / tot_supportable if tot_supportable else 0.0,
        band_counts=bands,
        mean_information_gain=float(np.mean(gains)) if gains else 0.0,
    )
