"""Reciprocal Rank Fusion, and the modality-quota allocation that sits on top.

The derivation of RRF
---------------------
Suppose we have two ranked lists, R1 (from a dense retriever) and R2 (from a
lexical retriever). We want one ranking. The obvious thing is to add the
*scores*: score(d) = s1(d) + s2(d). This fails for a structural reason. The
two retrievers produce scores on incomparable scales: BM25 scores are
unbounded sums of IDF-weighted counts, cosine similarities live in [-1, 1],
and cross-encoder logits are unbounded and arbitrarily shifted. There is no
principled way to add them, and any weighting you pick is fitted to one
corpus and breaks on the next.

Cormack, Clarke and Buettcher (2009) observed that the *rank* is the one
quantity every retriever agrees on, and that rank is scale-free. So: ignore
the scores, use only the positions.

For a document d, let r_i(d) be its 1-based rank in list i (and r_i(d) = the
list length + 1, i.e. "not present", when it is absent). Define

    RRF(d) = Σ_{i} 1 / (k + r_i(d))

Two properties fall out immediately.

**Parameter-free in the weights.** Every list contributes equally, in the
sense that there is no per-retriever weight to tune. The only constant, k, is
not a weighting: it controls the *shape* of the rank discount, and Cormack
et al. report it is insensitive for k > 10. The de-facto default, k = 60, is
used here.

**Why k damps the top.** The discount 1/(k + r) is roughly 1/k for r << k.
At k = 60, a rank-1 document contributes 1/61 = 0.0164 and a rank-10
document contributes 1/70 = 0.0143. They differ by only 13%. What actually
decides the fused order is *agreement*: a document ranked 1 by both retrievers
accumulates 2 * 0.0164 = 0.0328, roughly double a document ranked 1 by one
retriever and absent from the other. That is the whole point of fusion -- a
document that two independent retrievers both like beats a document that one
retriever loves.

The cost is that RRF discards score magnitude entirely. A reranker that is
wildly confident about its top hit gets no more credit than a reranker that
is barely sure. This is why the framework applies the reranker *after* fusion
rather than folding its scores into it.

**RRF vs CombSUM.** CombSUM (Fox & Shaw, 1994) sums normalised scores with
learned weights. Bruch et al. (2023) compared them across 23 runs and found
RRF at least as good and far more robust, because CombSUM's weights are
sensitive to the score distribution and RRF has nothing to tune. The
trade-off is that CombSUM can exploit score *margins* -- if the top document
scores 0.99 and the rest score 0.2, CombSUM knows that; RRF does not.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .config import FusionConfig, ModalityQuotaConfig


def reciprocal_rank_fusion(
    ranked_lists: list[list[str]],
    k: int = 60,
    doc_ids: list[str] | None = None,
) -> dict[str, float]:
    """Fuse several ranked id lists into one score per document.

    Parameters
    ----------
    ranked_lists:
        One ranked list of document ids per retriever, best first.
    k:
        The RRF constant. Default 60 (Cormack et al. 2009).
    doc_ids:
        Optional universe of ids. If given, documents absent from every list
        still receive a score of 0.0 so the output keys are stable.

    Returns
    -------
    dict mapping document id -> fused RRF score (higher is better).
    """
    scores: dict[str, float] = {}
    for ranked in ranked_lists:
        for rank, doc_id in enumerate(ranked, start=1):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank)
    if doc_ids is not None:
        for doc_id in doc_ids:
            scores.setdefault(doc_id, 0.0)
    return scores


def rrf_explain(
    ranked_lists: list[list[str]],
    k: int = 60,
) -> dict[str, list[tuple[str, int, float]]]:
    """Per-retriever contribution breakdown for each document.

    Used to show *why* a chunk was retrieved: "it was rank 3 for BM25 and
    rank 5 for dense, giving 0.0159 + 0.0154 = 0.0313".
    """
    out: dict[str, list[tuple[str, int, float]]] = {}
    for i, ranked in enumerate(ranked_lists):
        for rank, doc_id in enumerate(ranked, start=1):
            out.setdefault(doc_id, []).append((f"retriever_{i}", rank, 1.0 / (k + rank)))
    return out


@dataclass
class QuotaResult:
    """Outcome of modality-balanced selection."""

    selected: list[str]
    #: modality label -> number of chunks selected
    counts: dict[str, int]
    #: modality label -> number that were available
    available: dict[str, int]
    #: True when every quota was satisfiable from the candidate pool.
    quotas_met: bool
    #: Human-readable note on any quota that could not be met.
    note: str = ""


def apply_modality_quota(
    candidate_ranked: list[str],
    modality_of: dict[str, str],
    config: ModalityQuotaConfig,
    target: int = 10,
) -> QuotaResult:
    """Select a final context honouring per-modality minimum shares.

    The rule is a *floor* on the share of the context occupied by tables and
    by charts. The algorithm is **swap-based**, not **rebuild-based**, and the
    distinction matters:

        Rebuild-based: start from scratch, walking the ranking and skipping
        anything that would breach a floor. This silently *removes* good
        high-ranked items and replaces them with lower-ranked ones, so the
        quota can make retrieval worse -- which is exactly what the first
        implementation did (table recall fell from 0.865 to 0.649).

        Swap-based (this implementation): take the natural top-`target`
        ranking untouched. Then, while a floor is unmet, swap the
        *lowest-ranked* item of the over-represented modality for the
        *highest-ranked* available item of the under-represented modality.
        The context degrades by the smallest possible amount, and the
        ranking of everything that is kept is preserved.

    When the corpus does not contain enough of a modality to satisfy the
    floor, the shortfall is reported rather than papered over. That case is
    common: in a corpus that is 91% prose, there may be no chart chunk worth
    including at all, and a system that pretends otherwise is worse than one
    that says so.
    """
    counts: dict[str, int] = {}
    available: dict[str, int] = {}
    for cid in candidate_ranked:
        m = modality_of.get(cid, "text")
        available[m] = available.get(m, 0) + 1

    min_table = int(np.ceil(config.min_table_share * target))
    min_chart = int(np.ceil(config.min_chart_share * target))

    # Step 1 -- the natural top-target ranking, untouched.
    selected = list(candidate_ranked[:target])
    for cid in selected:
        m = modality_of.get(cid, "text")
        counts[m] = counts.get(m, 0) + 1

    floors = {"table": min_table, "chart": min_chart}

    # Step 2 -- swap until every floor is met or the pool is exhausted.
    for modality, floor in floors.items():
        while counts.get(modality, 0) < floor:
            # Best candidate of this modality outside the current selection.
            donor = None
            for cid in candidate_ranked:
                if cid in selected:
                    continue
                if modality_of.get(cid, "text") == modality:
                    donor = cid
                    break
            if donor is None:
                break  # pool exhausted; the shortfall is reported below

            # Worst-ranked item whose modality is not itself short of its
            # floor. "Text" is the usual donor, but any over-represented
            # modality can give up a slot.
            victim = None
            victim_rank = -1
            for rank, cid in enumerate(selected):
                m = modality_of.get(cid, "text")
                # A modality that is AT its floor cannot spare a slot: taking
                # one would break the floor it is already satisfying. Only a
                # modality with a surplus is eligible to be evicted.
                if counts.get(m, 1) <= floors.get(m, 0):
                    continue
                if m == modality:
                    continue
                if rank > victim_rank:
                    victim_rank = rank
                    victim = cid
            if victim is None:
                break

            selected[victim_rank] = donor
            vm = modality_of.get(victim, "text")
            counts[vm] = counts.get(vm, 1) - 1
            counts[modality] = counts.get(modality, 0) + 1

    # Preserve the fused rank order of the surviving items.
    order = {cid: i for i, cid in enumerate(candidate_ranked)}
    selected.sort(key=lambda cid: order.get(cid, 10**9))

    notes: list[str] = []
    quotas_met = True
    for modality, floor in floors.items():
        got = counts.get(modality, 0)
        if got < floor:
            quotas_met = False
            notes.append(
                f"{modality} floor not met: need {floor}, got {got} "
                f"(only {available.get(modality, 0)} {modality} chunks in the corpus)"
            )

    return QuotaResult(
        selected=selected,
        counts=counts,
        available=available,
        quotas_met=quotas_met,
        note="; ".join(notes),
    )
