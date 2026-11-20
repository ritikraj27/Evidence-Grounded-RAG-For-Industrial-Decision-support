#!/usr/bin/env python3
"""Rewrite the findings around the encoder change.

The dense leg was replaced with a retrieval-trained encoder. That changed
what the measurements say, and the prose has to say what they say:

  * **The fusion stopped being a net loss; it did not become a win.** With a
    general-purpose sentence encoder the fused system's ordering was *worse*
    than plain BM25's, because RRF gave a much weaker leg equal say in the
    ranking. With `bge-m3` the two are level, and the difference is not
    significant either way. The claim "hybrid retrieval beats flat retrieval"
    is not made — it is prior art anyway (BEIR).
  * **The reranker still buys ordering and not recall.** Unchanged in
    direction, now with a significant ordering p-value on the
    multi-category corpus.
  * **The modality quota's position effect did not survive the encoder
    change.** Before it, the post-rerank placement was the affordable one;
    after it, the two placements are indistinguishable on recall in the
    multi-category corpus and the earlier placement is better in the focus
    domain. The position effect was an artefact of the weaker dense leg, and
    that is the honest report.

Every number is a token, so none of this can drift from the measurements.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
T = ROOT / "deliverables" / "templates"

# --------------------------------------------------------------------------
# The README's findings section.
# --------------------------------------------------------------------------
README_OLD = """## The three findings

These are the substantive results, and two of them contradict the framework's
original specification. They are reproduced here from `impl/results/`.

**1. A reranker's recall is governed by its candidate pool.** Sweeping the pool
size gives a monotone, saturating curve: Recall@10 rises from {{POOL5}} at a pool of
5 to {{POOL100}} at a pool of 100, with most of the gain arriving by a pool of about
20 — twice the 10-chunk final context. A cross-encoder can only reorder what it
is shown, so a pool the size of the final context cannot improve recall at all.
This is a candidate explanation for the −5.34 pp reranker regression reported
in the September 2026 project report on a different corpus, and it converts
that anomaly into a cheap configuration check: one parameter, worth +0.333 of
recall.

**2. A quota binds only downstream of the component that could undo it.** The
modality quota delivers its modality benefit in either position — table
recall@10 rises from 1.000 to 1.000 — but what it *costs* is entirely a
function of its pipeline position. Before the reranker it costs 3.0 points of
Recall@10 (p = 3.2 × 10⁻¹) and -0.004 of nDCG@10, because the reranker
undoes the quota and the quota has already removed good text chunks from the
candidate pool. After the reranker it costs 3.0 points of Recall@10 and 0.010
of nDCG@10. The mechanism is the same; only its position changed what it cost.

**3. Corpus modality composition bounds how large a modality effect can be.**
This corpus is 88.8% text; the September 2026 corpus was 90.6% text. Two
independently constructed industrial corpora land on the same composition,
because that is what industrial documentation is. The effect is therefore
small and weakly positive in both, and the corpus composition is measured and
reported precisely so that this is predictable rather than surprising.

**And one result that constrains the gate.** The retriever's own recall of the
gold chunk is 100.0%: for roughly 29% of answerable questions the relevant
passage never reaches the candidate pool at all. The gate's ceiling is
therefore set by the retriever, not by its threshold — the right diagnostic
for a gate that still answers those questions is to fix the retrieval, not to
tighten the gate."""

README_NEW = """## The findings

These are the substantive results. Most of them are negative, which is the
point: the contribution is a measurement of which reliability mechanisms pay
for themselves in industrial text, and what they cost. Every number below is
substituted from `impl/results/` at build time.

**1. The encoder, not the fusion, decided whether hybrid retrieval paid.**
With a general-purpose sentence encoder the dense leg reached Recall@10
{{BASE_MC_R_B}} against plain BM25's {{BASE_MC_R_A}}, and the *fused* system's
ordering was worse than the lexical leg's — nDCG@10 {{BASE_MC_NDCG_C}} against
{{BASE_MC_NDCG_A}} on the multi-category corpus. The fusion was paying for the
dense leg's slots and getting nothing back, because reciprocal rank fusion
gives the two legs equal say in the ranking. Swapping in a retrieval-trained
encoder ({{EMBED_MODEL}}) changed the numbers and not the method: the dense leg
reaches {{R_B}} and the fusion {{R_C}} against BM25's {{R_A}}, with the ordering
gap closed to {{MC_NDCG_C}} against {{MC_NDCG_A}} on the multi-category corpus.
The difference between the fused system and plain BM25 is not significant on
recall ({{DELTA_AC}}, p = {{P_AC}}). **Fusion did not become a win; it stopped
being a loss.** "Hybrid retrieval beats flat retrieval" is prior art (BEIR)
and is not claimed here.

**2. The reranker buys ordering, not recall.** Its effect on Recall@10 is
{{DELTA_CD}} (p = {{P_CD}}); its effect on MRR is {{DELTA_CD_MRR}}
(p = {{P_CD_MRR}}) and on nDCG@10 {{DELTA_CD_NDCG}} (p = {{P_CD_NDCG}}). A
cross-encoder can only reorder what it was shown, so it cannot bring in
evidence the first stage discarded. That is also why the candidate pool
matters more than the reranker: recall@20 rises from {{POOL5_R20}} at a pool
of 5 to {{POOL100_R20}} at a pool of 100 and then saturates, while recall@10
peaks at a pool of {{POOL_PEAK}} and drifts back, because a bigger pool gives
the reranker more material to promote and some of what it promotes is a
distractor. **The pool buys recall at depth and spends precision at the cut.**

**3. The modality quota's position effect was an artefact of the weaker dense
leg.** Before the encoder change, applying the quota after the reranker was
measurably the cheaper placement. After it, the two placements are
indistinguishable on recall in the multi-category corpus, and in the focus
domain the *earlier* placement is the better one. The quota still does what
it is for — it lifts table recall@10 from {{MC_TBL_E}} to {{MC_TBL_F}} on the
multi-category corpus — but which placement is cheaper now depends on the
retriever rather than on the quota's own logic. That is a more useful result
than the one it replaced, and it is the one the measurements support.

**4. Corpus modality composition bounds how large a modality effect can be.**
This corpus is {{SHARE_TEXT}} text; the September 2026 corpus was 90.6% text.
Two independently constructed industrial corpora land on the same composition,
because that is what industrial documentation is. The modality result is
therefore small, and the composition is reported before the result rather than
after it, so that the smallness is predictable rather than surprising.

**And one result that constrains the gate.** The retriever's own recall of the
gold chunk is {{GOLD_RECALL_PCT}}, so the gate's ceiling is set by the retriever
rather than by its threshold — and the right diagnostic for a gate that still
answers questions it should have refused is to fix the retrieval, not to
tighten the gate."""

# --------------------------------------------------------------------------
# The guide's A.4 bullets.
# --------------------------------------------------------------------------
A4_OLD = """- **Hybrid fusion beats either leg alone.** Recall@10: BM25 {{R_A}}, dense {{R_B}},
  hybrid {{R_C}} (paired Wilcoxon, p = {{P_BC}}).
- **The encoder, not the fusion, was the weak part.** With a general-purpose
  sentence encoder the dense leg was *worse than BM25* on this corpus, and the
  fusion's ordering was worse than BM25's too — the fusion was paying for the
  dense leg's slots and getting nothing back. Replacing it with a
  retrieval-trained encoder ({{EMBED_MODEL}}) is what the framework's own
  ablation said to do, and §C.3 reports what that changed.
- **A reranker's recall is governed by the size of its candidate pool.** Sweeping
  the pool size gives a monotone, saturating curve: recall@10 rises from {{POOL5}} at
  a pool of 5 to {{POOL100}} at a pool of 100, with most of the gain arriving by a pool
  of about 20 — twice the 10-chunk final context. A pool the size of the context
  cannot improve recall at all, because it can only permute the chunks it was
  given. This is the most likely explanation of the −5.34 pp reranker regression
  reported in the September 2026 project report on a different corpus, and it is
  the cheapest actionable finding in the project: one parameter, worth {{DELTA_BC}} of
  recall.
- **The modality quota delivers its table-recall gain, and its pipeline position
  decides what you pay for it.** The quota lifts table recall@10 from {{TBL_E}} to
  {{TBL_G}}. Applied *before* the reranker it costs {{QUOTA_PRE_COST_PP}} points of
  overall recall@10 (p = {{P_EF}}); applied *after* it costs
  {{QUOTA_POST_COST_PP}} points. See §C.8 and Part E."""

A4_NEW = """- **The encoder, not the fusion, decided whether hybrid retrieval paid.**
  With a general-purpose sentence encoder the dense leg reached Recall@10
  {{BASE_MC_R_B}} against plain BM25's {{BASE_MC_R_A}}, and the *fused* system's
  ordering was worse than the lexical leg's too — the fusion was paying for the
  dense leg's slots and getting nothing back. With a retrieval-trained encoder
  ({{EMBED_MODEL}}) the dense leg reaches {{R_B}} and the fusion {{R_C}} against
  BM25's {{R_A}}, and the two are level rather than the fusion behind. The
  difference is not significant on recall ({{DELTA_AC}}, p = {{P_AC}}): fusion
  stopped being a loss; it did not become a win. §C.3 reports this in full.
- **The reranker buys ordering, not recall.** Recall@10 {{DELTA_CD}}
  (p = {{P_CD}}), MRR {{DELTA_CD_MRR}} (p = {{P_CD_MRR}}) and nDCG@10
  {{DELTA_CD_NDCG}} (p = {{P_CD_NDCG}}). A cross-encoder can only permute the
  chunks it was given.
- **The candidate pool buys recall at depth and spends precision at the cut.**
  Recall@20 rises from {{POOL5_R20}} at a pool of 5 to {{POOL100_R20}} at a pool
  of 100 and then saturates, while recall@10 peaks at a pool of {{POOL_PEAK}}
  and drifts back: more material to promote, some of it a distractor. This is
  the most likely explanation of the −5.34 pp reranker regression reported in
  the September 2026 project report on a different corpus, and it is the
  cheapest actionable finding in the project — one parameter.
- **The modality quota delivers its table-recall gain, and which placement is
  cheaper now depends on the retriever.** The quota lifts table recall@10 from
  {{MC_TBL_E}} to {{MC_TBL_F}} on the multi-category corpus. Applied before the
  reranker it changes overall recall@10 by {{QUOTA_PRE_COST_PP}} points
  (p = {{P_EF}}); applied after it, by {{QUOTA_POST_COST_PP}} points
  (p = {{P_FG}}). Before the encoder change the later placement was the
  affordable one; after it the two are level. See §C.8 and Part E."""


def apply(path: Path, edits):
    if not path.exists():
        print(f"!! missing {path}")
        return 0
    s = path.read_text(encoding="utf-8")
    n = 0
    for old, new in edits:
        c = s.count(old)
        if c != 1:
            print(f"!! {path.name}: count={c} -> {old[:70]!r}")
            continue
        s = s.replace(old, new, 1)
        n += 1
    path.write_text(s, encoding="utf-8")
    return n


def main() -> int:
    total = 0
    total += apply(ROOT / "README.md", [(README_OLD, README_NEW)])
    total += apply(T / "Deliverable_1_Part1_Content.md", [(A4_OLD, A4_NEW)])
    print(f"\n{total} replacements applied")
    return 0


if __name__ == "__main__":
    sys.exit(main())
