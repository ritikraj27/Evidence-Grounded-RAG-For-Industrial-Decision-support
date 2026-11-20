#!/usr/bin/env python3
"""Add the dataset provenance and the focus domain to the three papers.

A paper that says "a public industrial corpus" without saying where it came
from invites the question it cannot answer. Each paper now states the
source, the licence, the relationship to the primary (proprietary) corpus,
and the fact that the corpus ships with the paper with per-document
provenance.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = ROOT / "deliverables" / "templates"

PARA_MD = """
**The corpus, and where it came from.** Every measurement in this paper was
taken on an independently constructed public corpus of {{N_DOCUMENTS}}
industrial-engineering articles ({{N_CHUNKS}} chunks, {{N_CATEGORIES_WORD}}
categories), assembled from English Wikipedia through the MediaWiki API and
licensed CC BY-SA 4.0. It is a substitute for the primary corpus of the
original specification --- {{'634 chunks across 24 proprietary supply-chain documents'}}
--- which cannot be redistributed and therefore cannot be shipped with this
paper or re-run by a reader. The substitute ships in full alongside it:
`deliverables/dataset/` holds the documents and a manifest giving, for each
one, its Wikipedia URL, the upstream revision it was read at, the SHA-256 of
the bytes used, and its chunk count.

The thesis focuses on a **single industrial domain, supply chain management**
({{N_FOCUS_DOCUMENTS}} documents, {{N_FOCUS_CHUNKS}} chunks,
{{N_FOCUS_QUERIES}} questions), because that is the domain the primary corpus
covered and the one the practitioner scenarios are drawn from. The remaining
categories are retained for the cross-category transfer objective, which by
definition needs a subset of categories to transfer to held-out ones. Section
5 traces real questions from the focus domain end to end: what the plain
lexical retriever returned, what the full framework returned instead, what the
gate decided and on which signals, and how every claim in the answer was
banded.
"""

PATCHES = [
    ("Deliverable_2a_Technical_Report.md", [
        ("Crucially, the benchmark contains a family of **deliberately unanswerable questions**",
         PARA_MD.strip() + "\n\nCrucially, the benchmark contains a family of **deliberately unanswerable questions**"),
        ("and the difference is material at n = 239.",
         "and the difference is material at n = {{N_ANSWERABLE}}."),
        ("our substantive contribution is a failure-mode characterisation, obtained on an "
         "independently constructed public industrial corpus of {{N_CHUNKS}} chunks across "
         "{{N_CATEGORIES_WORD}} categories and a {{N_QUERIES}}-query silver-standard benchmark "
         "containing deliberately unanswerable questions.",
         "our substantive contribution is a failure-mode characterisation, obtained on an "
         "independently constructed public industrial corpus of {{N_CHUNKS}} chunks across "
         "{{N_CATEGORIES_WORD}} categories and a {{N_QUERIES}}-query silver-standard benchmark "
         "containing deliberately unanswerable questions, with supply chain management as the "
         "single industrial domain the work focuses on."),
    ]),
    ("Deliverable_2b_IEEE_Conference_Paper.tex", [
        ("\\subsection{The benchmark, and what it is not}",
         "\\subsection{The benchmark, and what it is not}\n\n"
         "\\paragraph{The corpus and its provenance.} Every measurement reported here was "
         "taken on an independently constructed public corpus of {{N_DOCUMENTS}} "
         "industrial-engineering articles ({{N_CHUNKS_TEX}} chunks, "
         "{{N_CATEGORIES_WORD}} categories), assembled from English Wikipedia through the "
         "MediaWiki API and licensed CC BY-SA 4.0. It substitutes for the primary corpus of "
         "the original specification --- 634 chunks across 24 proprietary supply-chain "
         "documents --- which cannot be redistributed and so cannot be shipped with this "
         "paper or re-run by a reader. The substitute ships in full alongside it, with a "
         "manifest giving, for every document, its Wikipedia URL, the upstream revision it "
         "was read at, the SHA-256 of the bytes used, and its chunk count. The work focuses "
         "on a single industrial domain, supply chain management "
         "({{N_FOCUS_DOCUMENTS}} documents, {{N_FOCUS_CHUNKS_TEX}} chunks, "
         "{{N_FOCUS_QUERIES}} questions); the remaining categories serve the cross-category "
         "transfer objective, which needs a subset of categories to transfer to held-out "
         "ones."),
        ("categories and a {{N_QUERIES}}-query silver-standard benchmark containing deliberately\n"
         "unanswerable questions.",
         "categories and a {{N_QUERIES}}-query silver-standard benchmark containing deliberately\n"
         "unanswerable questions, with supply chain management as the single industrial\n"
         "domain the work focuses on."),
    ]),
    ("Deliverable_2c_Journal_Style_Paper.tex", [
        ("\\subsection{The benchmark, and what it is not}",
         "\\subsection{The benchmark, and what it is not}\n\n"
         "\\paragraph{The corpus and its provenance.} Every measurement reported here was "
         "taken on an independently constructed public corpus of {{N_DOCUMENTS}} "
         "industrial-engineering articles ({{N_CHUNKS_TEX}} chunks, "
         "{{N_CATEGORIES_WORD}} categories), assembled from English Wikipedia through the "
         "MediaWiki API and licensed CC BY-SA 4.0. It substitutes for the primary corpus of "
         "the original specification --- 634 chunks across 24 proprietary supply-chain "
         "documents --- which cannot be redistributed and so cannot be shipped with this "
         "paper or re-run by a reader. The substitute ships in full alongside it, with a "
         "manifest giving, for every document, its Wikipedia URL, the upstream revision it "
         "was read at, the SHA-256 of the bytes used, and its chunk count. The work focuses "
         "on a single industrial domain, supply chain management "
         "({{N_FOCUS_DOCUMENTS}} documents, {{N_FOCUS_CHUNKS_TEX}} chunks, "
         "{{N_FOCUS_QUERIES}} questions); the remaining categories serve the cross-category "
         "transfer objective, which needs a subset of categories to transfer to held-out "
         "ones."),
        ("chunks spanning {{N_CATEGORIES_WORD}} categories, with a {{N_QUERIES}}-query silver-standard benchmark\n"
         "that includes a deliberate unanswerable class.",
         "chunks spanning {{N_CATEGORIES_WORD}} categories, with a {{N_QUERIES}}-query silver-standard benchmark\n"
         "that includes a deliberate unanswerable class, with supply chain management as the\n"
         "single industrial domain the work focuses on."),
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
    print(f"\n{total} replacements applied")
    if failures:
        print("!! FAILURES:")
        for f in failures:
            print(f"   {f}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
