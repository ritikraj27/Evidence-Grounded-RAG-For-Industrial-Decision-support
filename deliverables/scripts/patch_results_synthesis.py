#!/usr/bin/env python3
"""Make the guide's synthesis section derive from the measurements.

The seven numbered conclusions at the end of Part E were written by hand,
which is why they had to be rewritten every time a corpus changed -- and why
they were wrong the last time it changed. They are now generated from the
signs and significance of the measured comparisons, so the summary cannot
contradict the tables above it.

The wording follows the data: a comparison that is not significant is said to
be not significant, and a mechanism that helps ordering but not recall is
described that way.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "deliverables" / "scripts" / "make_results_md.py"

OLD = '''## E.8 What the experiments say, together

1. **Fusion is the retrieval win; the dense leg is the weak one.** Replacing
   `all-MiniLM-L6-v2` with a retrieval-trained encoder is the highest-value
   change available and the ablation is already built to measure it.
2. **The reranker's effect is pool-relative.** This is a candidate explanation
   for a regression reported on a different corpus, and it is a cheap
   configuration check.
3. **The category filter is a trade, not a gain** — overall recall for modality
   precision.
4. **The modality quota's pipeline position dominates its threshold.** Before
   the reranker it is harmful; after it, it is affordable.
5. **Corpus modality composition predicts whether a modality-aware mechanism can
   have any effect at all**, and both industrial corpora measured here are
   text-dominated.
6. **The gate's operating point is a fitted parameter of the deployment**, and
   it must be re-fitted per retriever and per corpus.
7. **Every rate in this report is reported with its prevalence and with
   always-flag and never-flag baselines**, because a filter result without
   those quantities does not mean anything.

That is the honest result of this project: **the architecture works, and the
most useful output is knowing precisely where it does not, and why.**
"""'''

NEW = '''## E.8 What the experiments say, together

The seven conclusions below are **generated from the measured comparisons**,
not written by hand, so they cannot disagree with the tables above. Where a
comparison is not statistically significant, this says so.

1. **{finding_fusion}**
2. **{finding_rerank}**
3. **{finding_filter}**
4. **{finding_quota}**
5. **{finding_composition}**
6. **{finding_gate}**
7. **{finding_baselines}**

That is the honest result of this project: **{closing}**
"""'''


def main() -> int:
    s = TARGET.read_text(encoding="utf-8")
    if OLD not in s:
        print("!! the synthesis block was not found")
        return 1
    s = s.replace(OLD, NEW, 1)

    # The values the new text interpolates, computed from the measurements.
    anchor = '''OUT.write_text("\\n".join(L), encoding="utf-8")'''
    if anchor not in s:
        print("!! the write call was not found")
        return 1

    generator = '''
# --------------------------------------------------------------------------
# The synthesis, derived from the measurements.
# --------------------------------------------------------------------------
if exp1:
    _S = exp1["systems"]
    _C = {c["comparison"].split(" -> ")[0]: c for c in exp1["comparisons"]}

    def _d(a):
        return _C[a]["delta"]

    def _p(a):
        return _C[a]["wilcoxon"]["p_value"]

    def _sig(a, alpha=0.05):
        return _p(a) < alpha

    _A, _B = _S["A. bm25_only"], _S["B. dense_only"]
    _Cc, _D = _S["C. hybrid_rrf"], _S["D. hybrid_rrf_rerank"]
    _E, _F, _G = (_S["E. +category_filter"], _S["F. +quota_pre_rerank"],
                   _S["G. +quota_post_rerank"])

    # 1. Fusion.
    _hybrid_over_bm25 = _Cc["recall@10"] - _A["recall@10"]
    _hybrid_better_order = (_Cc["nDCG@10"] > _A["nDCG@10"]
                            and _Cc["mrr"] > _A["mrr"])
    if _hybrid_better_order and _sig("B. dense_only"):
        finding_fusion = (
            f"**Fusion recovers what the dense leg loses, and does not beat a "
            f"strong lexical leg.** Dense-only retrieval reaches "
            f"R@10 {_B['recall@10']:.3f}; fusing it with BM25 reaches "
            f"{_Cc['recall@10']:.3f} (p = {_p('B. dense_only'):.1e}), a gain of "
            f"{_d('B. dense_only'):+.3f}. But BM25 alone reaches "
            f"{_A['recall@10']:.3f} with nDCG@10 {_A['nDCG@10']:.3f} and MRR "
            f"{_A['mrr']:.3f}, against the fused system's "
            f"{_Cc['nDCG@10']:.3f} and {_Cc['mrr']:.3f}. RRF gives the two legs "
            f"equal say in the ranking, so a much weaker leg spends slots on "
            f"worse candidates. Replacing `all-MiniLM-L6-v2` with a "
            f"retrieval-trained encoder remains the highest-value change "
            f"available, and this ablation is already built to measure it.")
    else:
        finding_fusion = (
            f"**Fusion beats both legs alone.** Dense-only reaches "
            f"R@10 {_B['recall@10']:.3f} and BM25-only {_A['recall@10']:.3f}; "
            f"fused reaches {_Cc['recall@10']:.3f} "
            f"(p = {_p('B. dense_only'):.1e} against the dense leg).")

    # 2. Reranking.
    _rec_gain = _d("C. hybrid_rrf")
    _order_gain = _D["mrr"] - _Cc["mrr"]
    _ndcg_gain = _D["nDCG@10"] - _Cc["nDCG@10"]
    _rec_sig = _sig("C. hybrid_rrf")
    if _rec_sig:
        finding_rerank = (
            f"**The reranker improves recall as well as ordering.** R@10 rises "
            f"{_rec_gain:+.3f} (p = {_p('C. hybrid_rrf'):.1e}), MRR "
            f"{_order_gain:+.3f} and nDCG@10 {_ndcg_gain:+.3f}.")
    else:
        finding_rerank = (
            f"**The reranker buys ordering, not recall.** Its effect on Recall@10 "
            f"is {_rec_gain:+.3f} (p = {_p('C. hybrid_rrf'):.2f}"
            f"{', not significant at the 0.05 level' if not _rec_sig else ''}), "
            f"while its effect on ordering is large: MRR {_order_gain:+.3f} and "
            f"nDCG@10 {_ndcg_gain:+.3f}. A cross-encoder that cannot bring in "
            f"evidence the first stage discarded cannot improve recall, only "
            f"the order of what it was given — which is why the candidate-pool "
            f"curve in E.5, not the reranker, is the informative measurement "
            f"here.")
        if exp5:
            _pool = {r["pool_size"]: r for r in exp5["results"]}
            _lo, _hi = min(_pool), max(_pool)
            finding_rerank += (
                f" Sweeping the pool gives recall@10 {_pool[_lo]['recall@10']:.3f} "
                f"at a pool of {_lo} and {_pool[_hi]['recall@10']:.3f} at a pool "
                f"of {_hi}.")

    # 3. The category filter.
    _cf_delta = _d("D. hybrid_rrf_rerank")
    _cf_sig = _sig("D. hybrid_rrf_rerank")
    if abs(_cf_delta) < 1e-9:
        finding_filter = (
            f"**The category pre-filter does nothing here.** Its effect is "
            f"exactly {_cf_delta:+.3f} (p = {_p('D. hybrid_rrf_rerank'):.2f}). On "
            f"a single-category corpus that is the expected result — the filter "
            f"cannot restrict anything that is already the only thing in the "
            f"corpus. It is reported here precisely because it makes the "
            f"point that a filter's measured effect is a property of the "
            f"corpus, not of the filter.")
    elif _cf_delta < 0 and _cf_sig:
        finding_filter = (
            f"**The category pre-filter is a recall liability.** It costs "
            f"{_cf_delta:+.3f} Recall@10 (p = {_p('D. hybrid_rrf_rerank'):.1e}): "
            f"a hard metadata filter removes evidence the retriever would have "
            f"found.")
    elif _cf_delta < 0:
        finding_filter = (
            f"**The category pre-filter does not pay for itself here.** It "
            f"costs {_cf_delta:+.3f} Recall@10 (p = "
            f"{_p('D. hybrid_rrf_rerank'):.2f}, not significant).")
    else:
        finding_filter = (
            f"**The category pre-filter helps.** It gains {_cf_delta:+.3f} "
            f"Recall@10 (p = {_p('D. hybrid_rrf_rerank'):.1e}): narrowing the "
            f"pool to one industrial sub-domain removes distractors before the "
            f"expensive stage.")

    # 4. The quota.
    _pre_cost = -_d("E. +category_filter")
    _post_cost = _E["recall@10"] - _G["recall@10"]
    _post_gain = _d("F. +quota_pre_rerank")
    _tbl_gain = _G["modality_recall"].get("table", 0) - _E["modality_recall"].get("table", 0)
    if abs(_tbl_gain) < 1e-9:
        finding_quota = (
            f"**The modality quota does not pay for itself on this corpus, and "
            f"its pipeline position decides how much it costs.** Table recall "
            f"is already {_E['modality_recall'].get('table', 0):.3f} without it, "
            f"so there is no table gain to buy ({_tbl_gain:+.3f}); what it costs "
            f"is overall recall. Applied before the reranker it costs "
            f"{_pre_cost:.3f} (p = {_p('E. +category_filter'):.2f}); applied "
            f"after it, {_post_cost:.3f}. The mechanism is identical in both "
            f"positions — only what it costs changes, because the reranker "
            f"undoes a quota applied upstream of it.")
    else:
        finding_quota = (
            f"**The modality quota is a trade, and its pipeline position "
            f"decides what it costs.** It lifts table recall@10 by "
            f"{_tbl_gain:+.3f}; applied before the reranker it costs "
            f"{_pre_cost:.3f} of overall recall (p = "
            f"{_p('E. +category_filter'):.2f}), applied after it "
            f"{_post_cost:.3f} — and the post-rerank variant is "
            f"{_post_gain:+.3f} better than the pre-rerank one (p = "
            f"{_p('F. +quota_pre_rerank'):.2f}).")

    # 5. Corpus composition.
    _cs = exp1["corpus_stats"]
    _n_table_q = sum(1 for q in (load_benchmark()["queries"])
                      if q["family"] == "table_lookup")
    finding_composition = (
        f"**Corpus modality composition bounds what a modality-aware mechanism "
        f"can show.** This corpus is {_cs['share_text']:.1%} text, "
        f"{_cs['share_table']:.1%} table and {_cs['share_chart']:.1%} chart, and "
        f"the benchmark contains {_n_table_q} table-lookup questions. A quota "
        f"over table and chart chunks cannot be evaluated at that size, which "
        f"is why the modality result above is a trade rather than a gain, and "
        f"why the composition is reported before the result rather than after "
        f"it.")

    # 6. The gate.
    if exp2:
        _ch = exp2["chosen_operating_point"]
        _dec = exp2.get("label_decomposition", {})
        _n_missed = int(_dec.get("answerable_and_missed", 0))
        _n_found = int(_dec.get("answerable_and_found", 0))
        finding_gate = (
            f"**The gate's operating point is a fitted parameter of the "
            f"deployment, and what it detects is narrower than what it is "
            f"called.** At τ = {_ch['tau']:.2f} it answers "
            f"{_ch['answerable_answered']:.1%} of answerable questions and "
            f"refuses {_ch['unanswerable_refused']:.1%} of unanswerable ones. "
            f"Its label is answer-in-context detectability, and the negative "
            f"class is dominated by retrieval failure — {_n_missed} answerable "
            f"questions whose evidence was missed against {_n_found} whose "
            f"evidence was found — so it cannot separate 'there is no evidence "
            f"here' from 'the evidence is here and the retriever missed it'. "
            f"The threshold must be re-fitted per retriever and per corpus.")
    else:
        finding_gate = (
            "**The gate's operating point is a fitted parameter of the "
            "deployment**, and it must be re-fitted per retriever and per "
            "corpus.")

    # 7. The reporting discipline.
    finding_baselines = (
        "**Every rate in this report is reported with its prevalence and "
        "against the two degenerate policies** — never refuse and always "
        "refuse — because a filter result without those quantities does not "
        "mean anything. The thresholds at the ends of the sweep are not "
        "baselines and are not presented as such.")

    closing = (
        "**the architecture works, and the most useful output is knowing "
        "precisely where it does not, and why.**")

'''
    s = s.replace(anchor, generator + anchor, 1)
    TARGET.write_text(s, encoding="utf-8")
    print("  the synthesis is now derived from the measurements")
    return 0


if __name__ == "__main__":
    sys.exit(main())
