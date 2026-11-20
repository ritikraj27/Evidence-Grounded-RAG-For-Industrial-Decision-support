#!/usr/bin/env python3
"""Make the presentation's narrative numbers read from the experiment JSON.

The ablation table on slide 12 was already built from `exp1`, but the
paragraph underneath it and the speaker notes quoted the same measurements
as literal text. When the corpus changed, the table updated and the prose
did not -- a deck whose caption contradicts its own table.

This patch rewrites those passages so every number in them comes from the
measured JSON at build time.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "deliverables" / "templates" / "scripts" / "make_pptx.py"

HELPER = '''
def _spoken_p(p: float) -> str:
    """Render a p-value the way it is said aloud, e.g. '3.5 times 10 to the minus 8'."""
    if p <= 0:
        return "smaller than one times ten to the minus three hundred"
    from math import floor, log10
    e = int(floor(log10(p)))
    m = p / (10 ** e)
    return f"{m:.1f} times 10 to the minus {abs(e)}"

'''

OLD_NARRATIVE = '''    rich(tf, [("Read the last two columns together: ", True, NAVY),
              ("D → E is a real loss of overall recall (−0.067) that buys modality "
               "precision (table recall 0.892 → 0.919); E → F is a catastrophe "
               "(−0.134) because the quota was applied in the wrong place; and "
               "F → G recovers +0.088 by moving the quota downstream. ", False, INK),
              ("The quota's position matters more than its threshold.",
               True, ACCENT)], size=14, first=True, space_after=0)'''

NEW_NARRATIVE = '''    def _tbl(k):
        return systems[k]["modality_recall"].get("table", float("nan"))

    rich(tf, [("Read the last two columns together: ", True, NAVY),
              (f"D → E is a real loss of overall recall "
               f"({comp['D. hybrid_rrf_rerank']['delta']:+.3f}) that buys modality "
               f"precision (table recall {_tbl('D. hybrid_rrf_rerank'):.3f} → "
               f"{_tbl('E. +category_filter'):.3f}); E → F is a catastrophe "
               f"({comp['E. +category_filter']['delta']:+.3f}) because the quota was "
               f"applied in the wrong place; and F → G recovers "
               f"{comp['F. +quota_pre_rerank']['delta']:+.3f} by moving the quota "
               f"downstream. ", False, INK),
              ("The quota's position matters more than its threshold.",
               True, ACCENT)], size=14, first=True, space_after=0)'''

OLD_NOTES_12 = '''notes(s, "This is the core experimental table. Seven systems, the same {{N_QUERIES}} queries, "
         "paired Wilcoxon tests between adjacent rungs.\\n\\n"
         "Read it top to bottom. Fusion works: BM25 alone 0.599, dense alone 0.471, "
         "fused 0.643, p = 2.5 times 10 to the minus 8. Reranking on a top-50 pool "
         "takes it to 0.731.\\n\\n"
         "Then the three findings, which are the actual contribution. D to E: the "
         "category filter costs overall recall and buys modality precision — a real "
         "trade-off. E to F: applying the modality quota BEFORE the reranker costs "
         "13.4 points. F to G: the SAME quota applied AFTER the reranker recovers 8.8 "
         "points. The quota's position in the pipeline matters more than its "
         "threshold value.\\n\\n"
         "I will unpack that in the next slide.")'''

NEW_NOTES_12 = '''notes(s, "This is the core experimental table. Seven systems, the same {{N_QUERIES}} queries, "
         "paired Wilcoxon tests between adjacent rungs.\\n\\n"
         f"Read it top to bottom. Fusion works: BM25 alone "
         f"{systems['A. bm25_only']['recall@10']:.3f}, dense alone "
         f"{systems['B. dense_only']['recall@10']:.3f}, fused "
         f"{systems['C. hybrid_rrf']['recall@10']:.3f}, p = "
         f"{_spoken_p(comp['C. hybrid_rrf']['wilcoxon']['p_value'])}. Reranking on a "
         f"top-50 pool takes it to "
         f"{systems['D. hybrid_rrf_rerank']['recall@10']:.3f}.\\n\\n"
         "Then the three findings, which are the actual contribution. D to E: the "
         "category filter costs overall recall and buys modality precision — a real "
         "trade-off. E to F: applying the modality quota BEFORE the reranker costs "
         f"{-comp['E. +category_filter']['delta'] * 100:.1f} points. F to G: the SAME "
         f"quota applied AFTER the reranker recovers "
         f"{comp['F. +quota_pre_rerank']['delta'] * 100:.1f} "
         "points. The quota's position in the pipeline matters more than its "
         "threshold value.\\n\\n"
         "I will unpack that in the next slide.")'''

OLD_NOTES_13 = '''         "pool recall goes up 8.4 points. With a top-10 pool recall cannot improve "'''

NEW_NOTES_13 = '''         f"pool recall goes up "
         f"{(systems['D. hybrid_rrf_rerank']['recall@10'] - systems['C. hybrid_rrf']['recall@10']) * 100:.1f} "
         "points. With a top-10 pool recall cannot improve "'''

OLD_NOTES_13B = '''         "modality result is a POWER question, not an algorithm question. On a corpus "
         "that is 91% prose, you cannot show a modality effect, and anyone who reports "'''

NEW_NOTES_13B = '''         "modality result is a POWER question, not an algorithm question. On a corpus "
         f"that is {_cs['share_text']:.0%} prose, you cannot show a modality effect, "
         "and anyone who reports "'''

PATCHES = [
    (OLD_NARRATIVE, NEW_NARRATIVE),
    (OLD_NOTES_12, NEW_NOTES_12),
    (OLD_NOTES_13, NEW_NOTES_13),
    (OLD_NOTES_13B, NEW_NOTES_13B),
]


def main() -> int:
    if not TARGET.exists():
        print(f"!! not found: {TARGET}")
        return 1
    text = original = TARGET.read_text(encoding="utf-8")
    failures = []
    for old, new in PATCHES:
        n = text.count(old)
        if n != 1:
            failures.append(f"count={n} -> {old[:70]!r}")
            continue
        text = text.replace(old, new)
    # Insert the helper just before the first slide that uses it.
    anchor = "# ================================================================ SLIDE 12"
    if anchor in text and "_spoken_p" not in original:
        text = text.replace(anchor, HELPER.lstrip("\n") + anchor, 1)
    elif "_spoken_p" in original and HELPER.strip() not in original:
        pass
    if text != original:
        TARGET.write_text(text, encoding="utf-8")
        print(f"  patched {TARGET.name}")
    if failures:
        print("!! FAILURES:")
        for f in failures:
            print(f"   {f}")
        return 1
    print("  narrative numbers now read from the experiment JSON")
    return 0


if __name__ == "__main__":
    sys.exit(main())
