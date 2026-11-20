#!/usr/bin/env python3
"""Make the deck's three findings follow the measurements.

The findings slide asserted three things that the measurements no longer
support in the form stated: that fusion beats either leg, that the reranker
improves recall, and that the quota delivers a table-recall gain. Each of
those now depends on the corpus and the run, so each is written from the
measured signs instead of being asserted.

The slide's title also changes: "Three Findings That Contradict the Original
Design" becomes "Three Findings, Two of Them Negative", because on this corpus
the findings are mostly negative results, and the slide should say so.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "deliverables" / "templates" / "scripts" / "make_pptx.py"

OLD_TITLE = '''s = base_slide("Three Findings That Contradict the Original Design",
               "Each is a failure-mode result that generalises beyond this corpus", nxt())'''

NEW_TITLE = '''s = base_slide("Three Findings \\u2014 Two of Them Negative",
               "Each is a failure-mode result that generalises beyond this corpus", nxt())'''

OLD_FINDINGS = '''findings = [
    ("1", "A reranker's recall is governed by its candidate pool",
     f"Same reranker, same corpus. With a top-50 pool: Recall@10 "
     f"{_v(_C, 'recall@10'):.3f} \\u2192 {_v(_D, 'recall@10'):.3f} "
     f"(p = {_p(_C, _D):.1e}). With a top-10 pool \\u2014 the size of the final context \\u2014 "
     f"Recall@10 is unchanged and Recall@20 FALLS {_v(_C, 'recall@20'):.3f} \\u2192 "
     f"{_v(_D, 'recall@20'):.3f}. A reranker can only reorder within the pool it is "
     f"given; a small pool forces it to discard relevant tail items.",
     "This is the most likely explanation of the \\u22125.34 pp reranker regression "
     "previously reported on an independent corpus \\u2014 turning an unexplained anomaly "
     "into a testable configuration hypothesis.", NAVY),
    ("2", "A quota binds only downstream of the component that could undo it",
     f"The modality quota applied before the reranker: Recall@10 "
     f"{_v(_E, 'recall@10'):.3f} \\u2192 {_v(_F, 'recall@10'):.3f} "
     f"(p = {_p(_E, _F):.1e}), table recall \\u2192 "
     f"{_v(_F, 'modality_recall').get('table', float('nan')):.3f}. The reranker undoes "
     f"the quota, and the quota has already removed good text chunks before the "
     f"cross-encoder saw them. Applied after the reranker: "
     f"{_v(_G, 'recall@10'):.3f} Recall@10, "
     f"{_v(_G, 'modality_recall').get('table', float('nan')):.3f} table recall.",
     "Generalisable design rule: a constraint on a downstream artefact must be "
     "enforced downstream of the component that could undo it.", NAVY_LIGHT),
    ("3", "Corpus modality composition predicts the sign of the modality effect",
     f"This corpus is {_cs['share_text']:.1%} text, {_cs['share_table']:.1%} table, "
     f"{_cs['share_chart']:.1%} chart \\u2014 closely matching the 2.3% chart / 7.1% table "
     f"of the earlier project-report corpus. With so few non-text chunks, a "
     f"two-table quota can only draw on tables deep in the ranking, displacing "
     f"relevant prose.",
     "So a NULL or negative modality effect is the EXPECTED outcome on such a corpus, "
     "not a bug. This is why the framework measures and reports corpus composition \\u2014 "
     "it predicts whether D2 can have any effect at all.", ACCENT),
]'''

NEW_FINDINGS = '''# The findings are written from the measured signs, so they cannot claim a
# gain the data does not show.
_A, _B = exp1["systems"]["A. bm25_only"], exp1["systems"]["B. dense_only"]
_Cv = exp1["systems"]["C. hybrid_rrf"]
_Ev = exp1["systems"]["E. +category_filter"]
_Fv = exp1["systems"]["F. +quota_pre_rerank"]
_Gv = exp1["systems"]["G. +quota_post_rerank"]
_cd = exp1["comparisons"]
def _cmp(a, b):
    for c in _cd:
        if c["comparison"] == f"{a} -> {b}":
            return c
    return None
_cd_delta = _cmp("C. hybrid_rrf", "D. hybrid_rrf_rerank")["delta"]
_cd_p = _cmp("C. hybrid_rrf", "D. hybrid_rrf_rerank")["wilcoxon"]["p_value"]
_cd_sig = _cd_p < 0.05
_ef_cost = _Ev["recall@10"] - _Fv["recall@10"]
_eg_cost = _Ev["recall@10"] - _Gv["recall@10"]
_tbl_gain = (_Gv["modality_recall"].get("table", 0)
             - _Ev["modality_recall"].get("table", 0))
_fusion_over_bm25 = _Cv["recall@10"] - _A["recall@10"]

if _fusion_over_bm25 > 0 and _Cv["nDCG@10"] > _A["nDCG@10"]:
    _f1_title = "Fusion beats either leg alone"
    _f1_body = (f"Dense-only Recall@10 {_B['recall@10']:.3f}; fused "
                f"{_Cv['recall@10']:.3f}; BM25 alone {_A['recall@10']:.3f}, "
                f"nDCG@10 {_A['nDCG@10']:.3f} against the fused system's "
                f"{_Cv['nDCG@10']:.3f}.")
else:
    _f1_title = "Fusion recovers the dense leg \\u2014 and does not beat BM25"
    _f1_body = (f"Dense-only Recall@10 {_B['recall@10']:.3f}; fused with BM25 "
                f"{_Cv['recall@10']:.3f}; BM25 alone {_A['recall@10']:.3f}. "
                f"But the ordering is worse: nDCG@10 {_Cv['nDCG@10']:.3f} against "
                f"BM25's {_A['nDCG@10']:.3f}, MRR {_Cv['mrr']:.3f} against "
                f"{_A['mrr']:.3f}. RRF gives the two legs equal say, so a much "
                f"weaker leg spends slots on worse candidates.")

if _cd_sig:
    _f2_title = "The reranker improves recall as well as ordering"
    _f2_body = (f"With a top-50 pool, Recall@10 {_v(_C, 'recall@10'):.3f} \\u2192 "
                f"{_v(_D, 'recall@10'):.3f} (p = {_cd_p:.1e}).")
else:
    _f2_title = "The reranker buys ordering, not recall"
    _f2_body = (f"Recall@10 {_v(_C, 'recall@10'):.3f} \\u2192 "
                f"{_v(_D, 'recall@10'):.3f} ({_cd_delta:+.3f}, p = {_cd_p:.2f}, "
                f"not significant), while MRR rises {_v(_D, 'mrr') - _v(_C, 'mrr'):+.3f} "
                f"and nDCG@10 {_v(_D, 'nDCG@10') - _v(_C, 'nDCG@10'):+.3f}. A "
                f"cross-encoder cannot bring in evidence the first stage "
                f"discarded, only reorder what it was given.")

if abs(_tbl_gain) < 1e-9:
    _f3_title = "The modality quota does not pay for itself here"
    _f3_body = (f"Table recall is already {_Ev['modality_recall'].get('table', 0):.3f} "
                f"without the quota, so there is no table gain to buy. What it "
                f"costs is overall recall: {_ef_cost:.3f} applied before the "
                f"reranker, {_eg_cost:.3f} applied after it.")
else:
    _f3_title = "A quota binds only downstream of the component that could undo it"
    _f3_body = (f"The quota lifts table recall by {_tbl_gain:+.3f}. Applied "
                f"before the reranker it costs {_ef_cost:.3f} of overall recall; "
                f"applied after it, {_eg_cost:.3f}.")

findings = [
    ("1", _f1_title, _f1_body,
     "The dense leg is the problem, and it is a fixable one: replace "
     "`all-MiniLM-L6-v2` with a retrieval-trained encoder and the fusion should "
     "start paying for itself.", NAVY),
    ("2", _f2_title, _f2_body,
     "So the measurement that matters is the candidate-pool curve, not the "
     "reranker. Sweeping the pool is one parameter and it is cheap.", NAVY_LIGHT),
    ("3", _f3_title, _f3_body,
     f"This corpus is {_cs['share_text']:.1%} text, {_cs['share_table']:.1%} table, "
     f"{_cs['share_chart']:.1%} chart \\u2014 so the modality mechanism has little "
     f"to act on. The composition is reported before the result, because it "
     f"predicts whether D2 can have any effect at all.", ACCENT),
]'''


def main() -> int:
    s = TARGET.read_text(encoding="utf-8")
    failures = []
    for old, new in ((OLD_TITLE, NEW_TITLE), (OLD_FINDINGS, NEW_FINDINGS)):
        c = s.count(old)
        if c != 1:
            failures.append(f"count={c} -> {old[:60]!r}")
            continue
        s = s.replace(old, new, 1)
    if failures:
        for f in failures:
            print(f"!! {f}")
        return 1
    TARGET.write_text(s, encoding="utf-8")
    print("  the deck's findings are now written from the measurements")
    return 0


if __name__ == "__main__":
    sys.exit(main())
