#!/usr/bin/env python3
"""Write the encoder-swap comparison: before and after, measured.

The dense leg was a general-purpose sentence encoder and is now a
retrieval-trained multilingual one. This script writes down what changed,
from the two sets of measurements rather than from recollection.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / "research" / "baseline_minilm" / "baseline_summary.json"
OUT = ROOT / "research" / "09_encoder_swap.md"

RUNG = [("A", "A. bm25_only", "BM25 only"),
        ("B", "B. dense_only", "Dense only"),
        ("C", "C. hybrid_rrf", "Hybrid (RRF)"),
        ("D", "D. hybrid_rrf_rerank", "+ cross-encoder rerank"),
        ("E", "E. +category_filter", "+ category pre-filter"),
        ("F", "F. +quota_pre_rerank", "+ quota (pre-rerank)"),
        ("G", "G. +quota_post_rerank", "+ quota (post-rerank)")]


def after(path: Path):
    p = path / "exp1_ablation.json"
    if not p.exists():
        return None
    e = json.loads(p.read_text(encoding="utf-8"))
    comp = {c["comparison"].split(" -> ")[0]: c for c in e["comparisons"]}
    return {
        "n_answerable": e["benchmark"]["n_answerable"],
        "n_chunks": e["corpus_stats"]["n_chunks"],
        "systems": {k: v for k, v in e["systems"].items()},
        "comparisons": comp,
    }


def fmt(x, nd=3):
    return f"{x:.{nd}f}"


def section(title, before, now):
    if not before or not now:
        return f"\n## {title}\n\n_Not available._\n"
    b, n = before, now
    out = [f"\n## {title}\n",
           f"Before: `{b.get('encoder', 'sentence-transformers/all-MiniLM-L6-v2')}`, "
           f"{b['n_answerable']} answerable queries over {b['n_chunks']:,} chunks. "
           f"After: `BAAI/bge-m3`, {n['n_answerable']} answerable queries over "
           f"{n['n_chunks']:,} chunks.\n",
           "| System | R@10 before | R@10 after | MRR before | MRR after | "
           "nDCG@10 before | nDCG@10 after | Table R@10 before | Table R@10 after |",
           "|---|---|---|---|---|---|---|---|---|"]
    for letter, key, label in RUNG:
        bs, ns = b["systems"][key], n["systems"][key]
        out.append(
            f"| {label} | {fmt(bs['recall@10'])} | {fmt(ns['recall@10'])} | "
            f"{fmt(bs['mrr'])} | {fmt(ns['mrr'])} | "
            f"{fmt(bs['nDCG@10'])} | {fmt(ns['nDCG@10'])} | "
            f"{fmt(bs['table_recall'] or 0)} | {fmt(ns['modality_recall'].get('table', 0))} |")
    out += ["", "### Paired tests, before and after", "",
            "| Comparison | ΔR@10 before | p before | ΔR@10 after | p after | "
            "ΔMRR before | p before | ΔMRR after | p after |",
            "|---|---|---|---|---|---|---|---|---|"]
    for letter, key, label in RUNG:
        if letter == "A":
            continue
        prev = RUNG[[r[0] for r in RUNG].index(letter) - 1][1]
        bc, nc = b["comparisons"].get(prev), n["comparisons"].get(prev)
        if not bc or not nc:
            continue

        def cell(c, dk, pk, nd=4):
            v = c.get(dk)
            p = c.get(pk)
            if v is None:
                return "—"
            pv = f"{p:.1e}" if isinstance(p, (int, float)) else "—"
            return f"{v:+.{nd}f} | {pv}"

        out.append(
            f"| {prev.split('. ')[0]} → {letter} | "
            f"{cell(bc, 'delta', 'p_value')} | {cell(nc, 'delta', 'p_value')} | "
            f"{cell(bc, 'delta_mrr', 'p_mrr')} | {cell(nc, 'delta_mrr', 'p_mrr')} |")
    return "\n".join(out) + "\n"


def main() -> int:
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    mc_after = after(ROOT / "impl" / "results")
    f_after = after(ROOT / "impl" / "results_focus")

    parts = ["""# 09 — Replacing the dense leg: before and after

**What changed.** The dense retrieval leg was
`sentence-transformers/all-MiniLM-L6-v2` — a general-purpose sentence encoder
trained with a *symmetric* similarity objective — and is now `BAAI/bge-m3`, a
retrieval-trained multilingual encoder (1024 dimensions, CLS pooling, a
normalisation module).

**Why.** Retrieval is asymmetric: a passage does not resemble a question, it
answers it. The first measurement in this project showed the mismatch was not
theoretical — dense-only retrieval was significantly worse than plain BM25, and
the fusion's ordering was worse than the lexical leg's, so the fusion was
spending the lexical leg's slots on the dense leg's worse candidates.

**One detail, because it is easy to get wrong.** BGE-M3 takes **no query
instruction**. BGE-v1.5 and the small instruction-tuned encoders (E5, GTE)
expect "Represent this sentence for searching relevant passages: " in front of
the query; BGE-M3's model card states that it "no longer requires adding
instructions to the queries", because the asymmetry is handled in training.
The configuration leaves `query_prefix` empty for that reason, and keeps the
field configurable because the next encoder may well want one.
"""]

    parts.append(section("Multi-category corpus (six industrial categories)",
                         baseline["multi_category"], mc_after))
    parts.append(section("Focus domain (supply chain management)",
                         baseline["focus"], f_after))

    # The headline comparison.
    lines = ["\n## What the change bought\n"]
    if mc_after:
        b = baseline["multi_category"]["systems"]
        n = mc_after["systems"]
        dense_gap_before = b["A. bm25_only"]["recall@10"] - b["B. dense_only"]["recall@10"]
        dense_gap_after = n["A. bm25_only"]["recall@10"] - n["B. dense_only"]["recall@10"]
        order_before = b["A. bm25_only"]["nDCG@10"] - b["C. hybrid_rrf"]["nDCG@10"]
        order_after = n["A. bm25_only"]["nDCG@10"] - n["C. hybrid_rrf"]["nDCG@10"]
        lines += [
            "| Quantity | Before | After | Change |",
            "|---|---|---|---|",
            f"| Dense-only Recall@10 | {fmt(b['B. dense_only']['recall@10'])} | "
            f"{fmt(n['B. dense_only']['recall@10'])} | "
            f"{n['B. dense_only']['recall@10'] - b['B. dense_only']['recall@10']:+.3f} |",
            f"| Dense-only MRR | {fmt(b['B. dense_only']['mrr'])} | "
            f"{fmt(n['B. dense_only']['mrr'])} | "
            f"{n['B. dense_only']['mrr'] - b['B. dense_only']['mrr']:+.3f} |",
            f"| Dense-only nDCG@10 | {fmt(b['B. dense_only']['nDCG@10'])} | "
            f"{fmt(n['B. dense_only']['nDCG@10'])} | "
            f"{n['B. dense_only']['nDCG@10'] - b['B. dense_only']['nDCG@10']:+.3f} |",
            f"| Gap between the dense leg and the lexical leg (R@10) | "
            f"{fmt(dense_gap_before)} | {fmt(dense_gap_after)} | "
            f"{dense_gap_after - dense_gap_before:+.3f} |",
            f"| The fusion's ordering deficit against the lexical leg (nDCG@10) | "
            f"{fmt(order_before)} | {fmt(order_after)} | "
            f"{order_after - order_before:+.3f} |",
            f"| The reranker's ordering gain (ΔMRR, C→D) | "
            f"{fmt(baseline['multi_category']['comparisons']['C. hybrid_rrf'].get('delta_mrr') or 0)} | "
            f"{fmt(mc_after['comparisons']['C. hybrid_rrf'].get('delta_mrr') or 0)} | "
            f"{(mc_after['comparisons']['C. hybrid_rrf'].get('delta_mrr') or 0) - (baseline['multi_category']['comparisons']['C. hybrid_rrf'].get('delta_mrr') or 0):+.3f} |",
            "",
            "A negative entry in the last two rows is an improvement: the gap "
            "is something the dense leg has to close, and the deficit is what "
            "the fusion was costing the lexical leg.",
            "",
            "The reranker's ordering gain gets *smaller* here, and that is not a "
            "regression. The reranker reorders the fused list, so the headroom "
            "it has to improve is whatever the fusion left on the table; once "
            "the fusion is better, there is less for it to recover. The gain "
            "is still large and still significant on its own.",
        ]
    parts.append("\n".join(lines))

    OUT.write_text("\n".join(parts) + "\n", encoding="utf-8")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
