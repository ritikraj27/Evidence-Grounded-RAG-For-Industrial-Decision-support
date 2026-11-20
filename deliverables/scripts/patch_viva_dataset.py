#!/usr/bin/env python3
"""Add the dataset question to the viva section and a limitation about it.

"Where did the data come from?" is the first question a panel asks, and it is
the one this work is most exposed on: the primary corpus is proprietary and
the measurements were taken on a public substitute. The answer belongs in
the viva section verbatim, with the limitation stated in Part H rather than
buried.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "deliverables" / "templates" / "Deliverable_1_PartF_toJ.md"

Q0 = """**Q0. Where did the data come from, and can I run it?**
The primary corpus of the original specification was 634 chunks across 24
proprietary supply-chain documents. It cannot be redistributed, so it cannot be
shipped with this work or re-run by a reader. Every measurement reported here
was taken on a **public substitute**: {{N_DOCUMENTS}} industrial-engineering
articles from English Wikipedia ({{N_CHUNKS}} chunks, {{N_CATEGORIES_WORD}}
categories), fetched through the MediaWiki API and licensed CC BY-SA 4.0. It was
assembled to have the properties the framework needs — several industrial
categories, genuine tables and figures so the modality mechanisms have
something to act on, and citable provenance.

It ships in full, in `deliverables/dataset/`. For every document the manifest
gives its Wikipedia URL, the upstream revision it was read at, the SHA-256 of
the exact bytes used, and its chunk count. The corpus builder fails loudly
rather than silently dropping a document, and the build checks that no document
is indexed twice or spans two categories.

The thesis focuses on a **single industrial domain, supply chain management**
({{N_FOCUS_DOCUMENTS}} documents, {{N_FOCUS_CHUNKS}} chunks,
{{N_FOCUS_QUERIES}} questions), because that is what the primary corpus
covered and where the practitioner scenarios come from. The other five
categories exist for the cross-category transfer experiment, which by
definition needs a subset of categories to transfer to held-out ones. Part E
traces real questions from the focus domain end to end.

The honest limitation: these are encyclopedia articles, not operating manuals,
standard operating procedures and supplier specifications. They are industrial
in subject matter, not operationally binding. The labels are silver-standard —
derived mechanically from the document rather than annotated by an expert — so
absolute recall is optimistic. The comparisons between systems are unaffected,
because every system is scored against identical labels.

"""

OLD_LIMIT = """| **L2** | Small corpus (634 chunks, 24 documents) | Results may not transfer to production-scale corpora | A larger, licensed industrial corpus |"""

NEW_LIMIT = """| **L2** | Small corpus (634 chunks, 24 documents) | Results may not transfer to production-scale corpora | A larger, licensed industrial corpus |
| **L2b** | The measurements were taken on a **public substitute** corpus, because the primary corpus is proprietary and cannot be redistributed | The corpus is industrial in subject matter but not operationally binding: encyclopedia articles, not the operating manuals and standard operating procedures of a real plant. The labels are silver-standard, so absolute recall is optimistic | A licensed, expert-annotated industrial corpus with the same provenance discipline; the pipeline is corpus-agnostic and re-runs unchanged |"""


def main() -> int:
    s = TARGET.read_text(encoding="utf-8")
    failures = []

    if "**Q0. Where did the data come from" not in s:
        anchor = "**Q1. What is the one-sentence contribution?**"
        if anchor not in s:
            failures.append("Q1 anchor not found")
        else:
            s = s.replace(anchor, Q0 + anchor, 1)
            print("  added Q0 to the viva section")

    if "| **L2b** |" not in s:
        if OLD_LIMIT not in s:
            failures.append("L2 anchor not found")
        else:
            s = s.replace(OLD_LIMIT, NEW_LIMIT, 1)
            print("  added limitation L2b about the substitute corpus")

    if failures:
        for f in failures:
            print(f"!! {f}")
        return 1
    TARGET.write_text(s, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
