#!/usr/bin/env python3
"""Tokenise the root README and add the dataset and focus domain to it.

The README is the first thing a reader sees, and it quoted the corpus size,
the benchmark size and the headline results as literals — the same drift
surface the rest of the deliverables had. It is now a substitution target,
like everything else.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "README.md"

EDITS = [
    # --- running it -------------------------------------------------------
    ("# 3. Corpus — 41 public industrial documents, six categories\n"
     ".venv/bin/python impl/scripts/build_corpus.py\n"
     "\n"
     "# 4. Benchmark — 371 silver-standard queries (227 answerable, 144 unanswerable)\n"
     ".venv/bin/python impl/scripts/build_benchmark.py\n"
     "\n"
     "# 5. Unit tests (seconds)\n"
     ".venv/bin/python impl/tests/test_hybrid.py\n"
     ".venv/bin/python impl/tests/test_confidence_and_claims.py",
     "# 3. Corpus — {{N_DOCUMENTS}} public industrial documents, {{N_CATEGORIES_WORD}} categories\n"
     ".venv/bin/python impl/scripts/build_corpus.py\n"
     "\n"
     "# 4. Focus domain — supply chain management on its own\n"
     ".venv/bin/python impl/scripts/make_focus_corpus.py\n"
     "\n"
     "# 5. Benchmark — {{N_QUERIES}} silver-standard queries "
     "({{N_ANSWERABLE}} answerable, {{N_UNANSWERABLE}} unanswerable)\n"
     ".venv/bin/python impl/scripts/build_benchmark.py\n"
     "\n"
     "# 6. Unit and invariant tests (seconds)\n"
     ".venv/bin/python impl/tests/test_hybrid.py\n"
     ".venv/bin/python impl/tests/test_confidence_and_claims.py\n"
     ".venv/bin/python impl/tests/test_invariants.py"),
    ("# 6. Experiments\n", "# 7. Experiments\n"),
    ("# 7. Rebuild every deliverable from the measured results\n",
     "# 8. Rebuild every deliverable from the measured results\n"),
    # --- the findings -----------------------------------------------------
    ("size gives a monotone, saturating curve: Recall@10 rises from 0.491 at a pool of\n"
     "5 to 0.658 at a pool of 100, with most of the gain arriving by a pool of about",
     "size gives a monotone, saturating curve: Recall@10 rises from {{POOL5}} at a pool of\n"
     "5 to {{POOL100}} at a pool of 100, with most of the gain arriving by a pool of about"),
    ("that anomaly into a cheap configuration check: one parameter, worth 0.167 of\n"
     "recall.",
     "that anomaly into a cheap configuration check: one parameter, worth {{DELTA_BC}} of\n"
     "recall."),
    ("modality quota delivers its modality benefit in either position — table\n"
     "recall@10 rises from 0.906 to 0.969 — but what it *costs* is entirely a",
     "modality quota delivers its modality benefit in either position — table\n"
     "recall@10 rises from {{TBL_E}} to {{TBL_G}} — but what it *costs* is entirely a"),
    ("candidate pool. After the reranker it costs 0.4 points of Recall@10 and 0.002\n"
     "of nDCG@10. The mechanism is the same; only its position changed what it cost.",
     "candidate pool. After the reranker it costs {{QUOTA_POST_COST_PP}} points of "
     "Recall@10 and {{NDCG_QUOTA_POST_COST}}\nof nDCG@10. The mechanism is the same; only its "
     "position changed what it cost."),
    ("Before the reranker it costs 8.6 points of\n"
     "Recall@10 (p = 4 × 10⁻⁴) and 4.5 points of nDCG@10, because the reranker",
     "Before the reranker it costs {{QUOTA_PRE_COST_PP}} points of\n"
     "Recall@10 (p = {{P_EF}}) and {{NDCG_QUOTA_PRE_COST}} of nDCG@10, because the reranker"),
    ("**3. Corpus modality composition bounds how large a modality effect can be.**\n"
     "This corpus is 90.7% text; the September 2026 corpus was 90.6% text.",
     "**3. Corpus modality composition bounds how large a modality effect can be.**\n"
     "This corpus is {{SHARE_TEXT}} text; the September 2026 corpus was 90.6% text."),
    ("**And one result that constrains the gate.** The retriever's own recall of the\n"
     "gold chunk is 0.707: for roughly 29% of answerable questions the relevant",
     "**And one result that constrains the gate.** The retriever's own recall of the\n"
     "gold chunk is {{GOLD_RECALL_PCT}}: for roughly 29% of answerable questions the relevant"),
    # --- the deck ---------------------------------------------------------
    ("| **4** | **The presentation** | `deliverables/Deliverable_4_Presentation_18Nov.pptx` | 18 slides for a 15–20 minute MTP review,",
     "| **4** | **The presentation** | `deliverables/Deliverable_4_Presentation_18Nov.pptx` | 19 slides for a 15–20 minute MTP review,"),
    # --- the dataset ------------------------------------------------------
    ("| `impl/` | The implementation, the corpus builder, the benchmark generator and the four experiment scripts. |",
     "| `impl/` | The implementation, the corpus builder, the benchmark generator and the experiment scripts. |\n"
     "| `deliverables/dataset/` | The evaluation corpus itself, with its provenance: every document with its Wikipedia URL, the upstream revision it was read at, the SHA-256 of the bytes used, and its chunk count, plus the licence and the benchmark. |"),
    # --- the honesty notes ------------------------------------------------
    ("  corpus with the same properties so that the pipeline runs and the ablation\n"
     "  numbers are reproducible. The two are never pooled, and the results are\n"
     "  reported as replication on an independent corpus.",
     "  corpus with the same properties so that the pipeline runs and the ablation\n"
     "  numbers are reproducible. The two are never pooled, and the results are\n"
     "  reported as replication on an independent corpus. The substitute ships in\n"
     "  full, in `deliverables/dataset/`, with the source and a per-document hash."),
    ("  tests. The benchmark holds 371 queries: 227 answerable and 144 deliberately\n"
     "  unanswerable, split between out-of-domain topics and *near-misses*",
     "  tests. The benchmark holds {{N_QUERIES}} queries: {{N_ANSWERABLE}} answerable and\n"
     "  {{N_UNANSWERABLE}} deliberately unanswerable, split between out-of-domain topics\n"
     "  and *near-misses*"),
]

DATASET_SECTION = """
---

## The dataset, and the focus domain

Two corpora are in play, and they are not the same thing.

**The primary corpus** of the September 2026 specification was 634 chunks across 24
proprietary supply-chain documents. It is not redistributable, so it cannot ship
with this work or be re-run by a reader.

**The public substitute** is what every number here was measured on:
{{N_DOCUMENTS}} industrial-engineering articles from English Wikipedia
({{N_CHUNKS}} chunks, {{N_CATEGORIES_WORD}} categories), fetched through the
MediaWiki API, licensed CC BY-SA 4.0. It ships in full in
`deliverables/dataset/`, with a manifest giving for every document its Wikipedia
URL, the upstream revision it was read at, the SHA-256 of the exact bytes used,
and its chunk count.

**The focus domain** is supply chain management — {{N_FOCUS_DOCUMENTS}}
documents, {{N_FOCUS_CHUNKS}} chunks, {{N_FOCUS_QUERIES}} questions. It is the
domain the primary corpus covered and the one the practitioner scenarios come
from, so the thesis is focused there rather than spread thin; the other five
categories exist for the cross-category transfer experiment, which by
definition needs a subset of categories to transfer to held-out ones.

```bash
.venv/bin/python impl/scripts/export_dataset.py   # rebuild deliverables/dataset/
```

---
"""


def main() -> int:
    s = TARGET.read_text(encoding="utf-8")
    failures = []
    for old, new in EDITS:
        n = s.count(old)
        if n != 1:
            failures.append(f"count={n} -> {old[:60]!r}")
            continue
        s = s.replace(old, new, 1)
    if "## The dataset, and the focus domain" not in s:
        anchor = "\n---\n\n## Honesty notes"
        if anchor not in s:
            failures.append("honesty-notes anchor not found")
        else:
            s = s.replace(anchor, DATASET_SECTION + "\n## Honesty notes", 1)
    if failures:
        for f in failures:
            print(f"!! {f}")
        return 1
    TARGET.write_text(s, encoding="utf-8")
    print("  tokenised the root README and added the dataset section")
    return 0


if __name__ == "__main__":
    sys.exit(main())
