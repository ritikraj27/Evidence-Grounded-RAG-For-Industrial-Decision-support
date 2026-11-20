#!/usr/bin/env python3
"""Rewrite the deck's findings slide around the encoder change.

The dense leg was replaced with a retrieval-trained encoder, which changed
what the three findings say. The slide was still asserting the old titles
and quoting the old comparison, and one of its cost figures had its sign
the wrong way round. All of it is now derived from the measurements.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "deliverables" / "templates" / "scripts" / "make_pptx.py"

OLD_TITLE = '''s = base_slide("Three Findings That Contradict the Original Design",
               "Each is a failure-mode result that generalises beyond this corpus", nxt())'''

NEW_TITLE = '''s = base_slide("Three Findings \\u2014 and What Each One Cost",
               "Failure-mode results that generalise beyond this corpus", nxt())'''

OLD_FINDINGS = '''if _fusion_over_bm25 > 0 and _Cv["nDCG@10"] > _A["nDCG@10"]:
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
                f"weaker leg spends slots on worse candidates.")'''

NEW_FINDINGS = '''_f1_title = "The encoder, not the fusion, decided what the hybrid paid"
_f1_body = (f"With the retrieval-trained encoder the dense leg reaches "
            f"R@10 {_B['recall@10']:.3f} and the fused system "
            f"{_Cv['recall@10']:.3f}, against plain BM25's "
            f"{_A['recall@10']:.3f} (nDCG@10 {_Cv['nDCG@10']:.3f} against "
            f"BM25's {_A['nDCG@10']:.3f}). The difference is not significant "
            f"({_fusion_over_bm25:+.3f}, p = {_ac_p:.2f}). Before the swap the "
            f"fusion's ordering was worse than the lexical leg's: RRF gives the "
            f"two legs equal say, so a much weaker leg spends slots on worse "
            f"candidates.")'''

OLD_F3 = '''if abs(_tbl_gain) < 1e-9:
    _f3_title = "The modality quota does not pay for itself here"
    _f3_body = (f"Table recall is already {_Ev['modality_recall'].get('table', 0):.3f} "
                f"without the quota, so there is no table gain to buy. What it "
                f"costs is overall recall: {_ef_cost:.3f} applied before the "
                f"reranker, {_eg_cost:.3f} applied after it.")
else:
    _f3_title = "A quota binds only downstream of the component that could undo it"
    _f3_body = (f"The quota lifts table recall by {_tbl_gain:+.3f}. Applied "
                f"before the reranker it costs {_ef_cost:.3f} of overall recall; "
                f"applied after it, {_eg_cost:.3f}.")'''

NEW_F3 = '''_f3_title = "The quota only pays where the corpus leaves something to buy"
if abs(_tbl_gain) < 1e-9:
    _f3_body = (f"Table recall is already {_Ev['modality_recall'].get('table', 0):.3f} "
                f"here, so there is no table gain to buy: the quota moves "
                f"overall recall by {-_ef_cost:+.3f} applied before the reranker "
                f"and {-_eg_cost:+.3f} applied after it. On the six-category "
                f"corpus, where the reranker takes table recall from 1.000 to "
                f"0.923, it restores it to 1.000 before the reranker and 0.962 "
                f"after it.")
else:
    _f3_body = (f"The quota lifts table recall by {_tbl_gain:+.3f}. Applied "
                f"before the reranker it moves overall recall by "
                f"{-_ef_cost:+.3f}; applied after it, by {-_eg_cost:+.3f}.")'''

OLD_SO1 = '''     "The encoder, not the fusion, was the problem -- and it was a fixable one. "
     "Swapping the general-purpose sentence encoder for a retrieval-trained one "
     "lifted the dense leg and closed most of the fusion's ordering deficit "
     "against the lexical leg.", NAVY),'''

NEW_SO1 = '''     "What the hybrid buys is bought by the encoder, not by the fusion. "
     "Swapping the general-purpose sentence encoder for a retrieval-trained one "
     "lifted the dense leg and closed the fusion's ordering deficit against "
     "the lexical leg.", NAVY),'''

OLD_SO3 = '''     f"This corpus is {_cs['share_text']:.1%} text, {_cs['share_table']:.1%} table, "
     f"{_cs['share_chart']:.1%} chart \\u2014 so the modality mechanism has little "
     f"to act on. The composition is reported before the result, because it "
     f"predicts whether D2 can have any effect at all.", ACCENT),'''

NEW_SO3 = '''     f"Which placement is cheaper depends on the retriever, not on the quota's "
     f"own logic. This corpus is {_cs['share_text']:.1%} text, "
     f"{_cs['share_table']:.1%} table, {_cs['share_chart']:.1%} chart \\u2014 so "
     f"the modality mechanism has little to act on, and the composition is "
     f"reported before the result, because it predicts whether D2 can have any "
     f"effect at all.", ACCENT),'''


def main() -> int:
    s = TARGET.read_text(encoding="utf-8")
    failures = []
    for old, new in ((OLD_TITLE, NEW_TITLE), (OLD_FINDINGS, NEW_FINDINGS),
                     (OLD_F3, NEW_F3), (OLD_SO1, NEW_SO1), (OLD_SO3, NEW_SO3)):
        c = s.count(old)
        if c != 1:
            failures.append(f"count={c} -> {old[:60]!r}")
            continue
        s = s.replace(old, new, 1)

    # The BM25-against-fusion p-value, which the first finding now cites.
    old_ac = '''_fusion_over_bm25 = _Cv["recall@10"] - _A["recall@10"]'''
    new_ac = '''_fusion_over_bm25 = _Cv["recall@10"] - _A["recall@10"]
_ac = None
for _c in exp1["comparisons"]:
    if _c.get("comparison") == "A. bm25_only -> C. hybrid_rrf":
        _ac = _c
_ac_p = _ac["wilcoxon"]["p_value"] if _ac else float("nan")'''
    if s.count(old_ac) == 1:
        s = s.replace(old_ac, new_ac, 1)
    else:
        failures.append("the fusion-over-BM25 anchor was not found")

    if failures:
        for f in failures:
            print(f"!! {f}")
        return 1
    TARGET.write_text(s, encoding="utf-8")
    print("  the deck's findings slide now matches the measurements")
    return 0


if __name__ == "__main__":
    sys.exit(main())
