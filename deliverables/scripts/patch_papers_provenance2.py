#!/usr/bin/env python3
"""Insert the corpus-provenance paragraph into the two LaTeX papers.

The anchors differ between the papers: the IEEE paper opens its evaluation
protocol with a `\\paragraph{Benchmark.}`, the journal paper with a
`\\subsection{Benchmark and label standard}`.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = ROOT / "deliverables" / "templates"

PROVENANCE = (
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
    "ones.\n\n"
)

TARGETS = [
    ("Deliverable_2b_IEEE_Conference_Paper.tex",
     "\\paragraph{Benchmark.} We evaluate on a \\emph{silver-standard} benchmark"),
    ("Deliverable_2c_Journal_Style_Paper.tex",
     "\\subsection{Benchmark and label standard}\n"),
]


def main() -> int:
    failures = []
    total = 0
    for rel, anchor in TARGETS:
        p = TEMPLATES / rel
        if not p.exists():
            failures.append(f"{rel}: not found")
            continue
        s = p.read_text(encoding="utf-8")
        if "The corpus and its provenance" in s:
            print(f"  {rel}: already present")
            continue
        if s.count(anchor) != 1:
            failures.append(f"{rel}: anchor count {s.count(anchor)}")
            continue
        s = s.replace(anchor, anchor + "\n" + PROVENANCE, 1)
        p.write_text(s, encoding="utf-8")
        total += 1
        print(f"  patched {rel}")
    print(f"\n{total} replacements applied")
    if failures:
        for f in failures:
            print(f"!! {f}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
