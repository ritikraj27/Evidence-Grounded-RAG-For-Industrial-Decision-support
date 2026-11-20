#!/usr/bin/env python3
"""Add the dataset provenance and focus domain to the deck's protocol slide.

A panel member asking "where did the data come from?" should get an answer
from the slide itself: the source, the licence, and the fact that the
corpus ships with the report with a per-document URL, revision id and
hash. The focus domain is named at the same time, because it is the domain
the thesis is about.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "deliverables" / "templates" / "scripts" / "make_pptx.py"

OLD = '''    "The 300-query expert-annotated SupplyChainQA v7 (κ ≥ 0.7 on four categorical "
    "fields) is reported separately. The two are never pooled.",
]:'''

NEW = '''    "The 300-query expert-annotated SupplyChainQA v7 (κ ≥ 0.7 on four categorical "
    "fields) is reported separately. The two are never pooled.",
    "SOURCE: English Wikipedia via the MediaWiki API. Licence CC BY-SA 4.0. The "
    "corpus ships IN FULL with the report — every document with its URL, the "
    "revision it was read at, and the SHA-256 of the bytes used.",
    "FOCUS DOMAIN: supply chain management — {{N_FOCUS_DOCUMENTS}} documents, "
    "{{N_FOCUS_CHUNKS}} chunks, {{N_FOCUS_QUERIES}} questions, traced end to end "
    "in the case study.",
]:'''

OLD_N = '''"reported with every p-value — at n = 239 the difference between “unlikely” and "'''
NEW_N = '''"reported with every p-value — at n = {{N_ANSWERABLE}} the difference between “unlikely” and "'''


def main() -> int:
    s = TARGET.read_text(encoding="utf-8")
    failures = []
    if OLD in s:
        s = s.replace(OLD, NEW, 1)
        print("  added the source, licence and focus domain to the protocol slide")
    else:
        failures.append("protocol bullet anchor not found")
    if OLD_N in s:
        s = s.replace(OLD_N, NEW_N, 1)
        print("  bound the sample size to the benchmark")
    else:
        failures.append("sample-size anchor not found")
    if failures:
        for f in failures:
            print(f"!! {f}")
        return 1
    TARGET.write_text(s, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
