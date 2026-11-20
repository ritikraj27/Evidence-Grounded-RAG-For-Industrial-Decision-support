#!/usr/bin/env python3
"""Bind the guide's quoted results to tokens, and add the dataset section.

The guide's A.4 summary, C.3, C.8, the code commentary and the viva
questions quoted measurements as literal text. Those literals are the
numbers a reader checks against the tables, so they have to be the same
numbers. This patch replaces them with tokens and inserts a new A.5 that
states exactly what the dataset is and where it came from.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = ROOT / "deliverables" / "templates"

A5 = """## A.5 The dataset, and where it came from

| | |
|---|---|
| **What** | {{N_DOCUMENTS}} public industrial-engineering articles, {{N_CHUNKS}} chunks, {{N_CATEGORIES_WORD}} categories |
| **Source** | English Wikipedia, fetched through the MediaWiki `parse` API |
| **Focus domain** | supply chain management — {{N_FOCUS_DOCUMENTS}} documents, {{N_FOCUS_CHUNKS}} chunks |
| **Benchmark** | {{N_QUERIES}} silver-standard questions ({{N_ANSWERABLE}} answerable, {{N_UNANSWERABLE}} deliberately unanswerable) |
| **Licence** | CC BY-SA 4.0 for the article text |
| **Shipped with** | `deliverables/dataset/` — the documents, the provenance manifest, the benchmark |
| **Rebuild** | `python3 impl/scripts/build_corpus.py` |

Two corpora are in play here, and they should not be confused.

**The primary corpus** of the original project specification was 634 chunks
across 24 proprietary supply-chain documents. It cannot be redistributed, so
it cannot be shipped with this work or re-run by a reader.

**The public substitute** is what every number in this guide was measured on.
It was assembled to have the properties the framework needs — several
industrial categories, real tables and figures so the modality mechanisms have
something to bite on, and a citable source — and it ships in full with its
provenance. Every document in `deliverables/dataset/manifest.json` carries its
Wikipedia URL, the upstream revision it was read at, the SHA-256 of the exact
bytes used, and its chunk count.

**The focus domain** is supply chain management: {{N_FOCUS_DOCUMENTS}}
documents and {{N_FOCUS_CHUNKS}} chunks, with its own {{N_FOCUS_QUERIES}}-question
benchmark ({{N_FOCUS_ANSWERABLE}} answerable, {{N_FOCUS_UNANSWERABLE}}
deliberately unanswerable). It is the single industrial domain this thesis is
about — the one the primary corpus covered and the one the practitioner
scenarios are drawn from — and Part E traces real questions from it end to
end. The other five categories are retained for the cross-category transfer
objective, which by definition needs a subset of categories to transfer to
held-out ones.

**What the substitute is not.** These are encyclopedia articles, not the
operating manuals, standard operating procedures and supplier specifications of
a real plant. They are industrial in subject matter, not operationally binding.
The silver-standard labels are derived mechanically from the document, so
absolute recall is optimistic — the comparisons between systems are not
affected, because every system is scored against identical labels.

"""

PATCHES: list[tuple[str, list[tuple[str, str]]]] = [
    ("Deliverable_1_Part1_Content.md", [
        # --- A.4: the five-minute summary --------------------------------
        ("- **Hybrid fusion beats either leg alone.** Recall@10: BM25 0.599, dense 0.477,\n"
         "  hybrid 0.644 (paired Wilcoxon, p = 3.5 × 10⁻⁸).",
         "- **Hybrid fusion beats either leg alone.** Recall@10: BM25 {{R_A}}, dense {{R_B}},\n"
         "  hybrid {{R_C}} (paired Wilcoxon, p = {{P_BC}})."),
        ("  the pool size gives a monotone, saturating curve: recall@10 rises from 0.491 at\n"
         "  a pool of 5 to 0.658 at a pool of 100, with most of the gain arriving by a pool",
         "  the pool size gives a monotone, saturating curve: recall@10 rises from {{POOL5}} at\n"
         "  a pool of 5 to {{POOL100}} at a pool of 100, with most of the gain arriving by a pool"),
        ("  cheapest actionable finding in the project: one parameter, worth 0.167 of\n  recall.",
         "  cheapest actionable finding in the project: one parameter, worth {{DELTA_BC}} of\n  recall."),
        ("- **The modality quota delivers its table-recall gain, and its pipeline position\n"
         "  decides what you pay for it.** The quota lifts table recall@10 from 0.906 to\n"
         "  0.969. Applied *before* the reranker it costs 8.6 points of overall recall@10\n"
         "  (p = 4 × 10⁻⁴); applied *after* it costs 0.4 points. See §C.8 and Part E.",
         "- **The modality quota delivers its table-recall gain, and its pipeline position\n"
         "  decides what you pay for it.** The quota lifts table recall@10 from {{TBL_E}} to\n"
         "  {{TBL_G}}. Applied *before* the reranker it costs {{QUOTA_PRE_COST_PP}} points of\n"
         "  overall recall@10 (p = {{P_EF}}); applied *after* it costs\n"
         "  {{QUOTA_POST_COST_PP}} points. See §C.8 and Part E."),
        ("  finds the gold chunk for 70.7% of answerable questions, so a perfect gate could",
         "  finds the gold chunk for {{GOLD_RECALL_PCT}} of answerable questions, so a perfect gate could"),
        # --- C.3: the dense leg -------------------------------------------
        ("**What happened.** On our corpus, dense-only retrieval (Recall@10 = 0.471) was\n"
         "**worse** than BM25-only (0.599).",
         "**What happened.** On our corpus, dense-only retrieval (Recall@10 = {{R_B}}) was\n"
         "**worse** than BM25-only ({{R_A}})."),
        # --- C.8: the quota -----------------------------------------------
        ("modality benefit in both positions — table recall@10 rises from 0.906 to 0.969 —\n"
         "but the price is very different. Before the reranker it costs 8.6 points of\n"
         "overall recall@10 (p = 4 × 10⁻⁴) and 4.5 points of nDCG@10; after the reranker\n"
         "it costs 0.4 points of recall@10 and 0.002 of nDCG@10.",
         "modality benefit in both positions — table recall@10 rises from {{TBL_E}} to\n"
         "{{TBL_G}} — but the price is very different. Before the reranker it costs\n"
         "{{QUOTA_PRE_COST_PP}} points of overall recall@10 (p = {{P_EF}}) and\n"
         "{{NDCG_QUOTA_PRE_COST}} of nDCG@10; after the reranker it costs\n"
         "{{QUOTA_POST_COST_PP}} points of recall@10 and {{NDCG_QUOTA_POST_COST}} of\n"
         "nDCG@10."),
    ]),
    ("Deliverable_1_PartD_Code.md", [
        ("   (recall 0.599 vs dense 0.477), the filter's effect was almost entirely",
         "   (recall {{R_A}} vs dense {{R_B}}), the filter's effect was almost entirely"),
    ]),
    ("Deliverable_1_PartF_toJ.md", [
        ("context. With a top-10 pool it cannot bring in a relevant chunk sitting at fused\n"
         "rank 34, and it can only lose the one sitting at rank 12: recall@20 fell\n"
         "0.731 → 0.643. With a top-50 pool the same reranker raises recall@10 from 0.643\n"
         "to 0.731 (p = 1.2 × 10⁻³) and MRR from 0.368 to 0.528.",
         "context. With a top-10 pool it cannot bring in a relevant chunk sitting at fused\n"
         "rank 34, and it can only lose the one sitting at rank 12: recall@20 fell\n"
         "{{R20_D}} → {{R20_C}}. With a top-50 pool the same reranker raises recall@10 from\n"
         "{{R_C}} to {{R_RERANK}} (p = {{P_CD}}) and MRR from {{MRR_C}} to {{MRR_D}}."),
    ]),
]


def main() -> int:
    failures = []
    total = 0
    for rel, edits in PATCHES:
        p = TEMPLATES / rel
        if not p.exists():
            failures.append(f"{rel}: not found")
            continue
        s = original = p.read_text(encoding="utf-8")
        for old, new in edits:
            n = s.count(old)
            if n == 0:
                failures.append(f"{rel}: NOT FOUND -> {old[:60]!r}")
                continue
            if n > 1:
                failures.append(f"{rel}: AMBIGUOUS ({n}x) -> {old[:60]!r}")
                continue
            s = s.replace(old, new)
            total += 1
        if s != original:
            p.write_text(s, encoding="utf-8")
            print(f"  patched {rel}")

    # --- A.5: the dataset section ---------------------------------------
    p1 = TEMPLATES / "Deliverable_1_Part1_Content.md"
    s = p1.read_text(encoding="utf-8")
    if "## A.5 The dataset" not in s:
        anchor = "\n---\n\n# Part B — Every term, defined"
        if anchor not in s:
            failures.append("A.5: anchor for the dataset section not found")
        else:
            s = s.replace(anchor, "\n" + A5 + anchor, 1)
            p1.write_text(s, encoding="utf-8")
            print(f"  added the dataset section (A.5) to {p1.name}")
            total += 1

    print(f"\n{total} replacements applied")
    if failures:
        print("!! FAILURES:")
        for f in failures:
            print(f"   {f}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
