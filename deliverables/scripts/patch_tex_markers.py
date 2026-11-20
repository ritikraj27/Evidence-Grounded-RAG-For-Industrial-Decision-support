#!/usr/bin/env python3
"""Wrap the numeric Results paragraphs of the LaTeX templates in markers.

The paragraphs between these markers are regenerated from the measured JSON
by `make_tex_prose.py`. Everything outside them — the framing, the
literature, the discussion — stays hand-written, because it is analysis
rather than measurement.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = ROOT / "deliverables" / "templates"

BEGIN = "% BEGIN RESULTS-NUMERIC"
END = "% END RESULTS-NUMERIC"

#: (file, first paragraph to replace, text that ends the block)
TARGETS = [
    ("Deliverable_2b_IEEE_Conference_Paper.tex",
     r"\\paragraph\{Hybrid fusion beats either leg alone",
     r"\\subsection\{The confidence gate, contradiction surfacing and transfer\}"),
    ("Deliverable_2c_Journal_Style_Paper.tex",
     r"\\paragraph\{Fusion beats either leg alone",
     r"\\subsection\{Confidence gate, contradiction surfacing and cross-category transfer\}"),
]


def main() -> int:
    failures = []
    for name, start_pat, end_pat in TARGETS:
        p = TEMPLATES / name
        if not p.exists():
            failures.append(f"{name}: not found")
            continue
        s = p.read_text(encoding="utf-8")
        if BEGIN in s:
            print(f"  {name}: markers already present")
            continue
        m_start = re.search(start_pat, s)
        m_end = re.search(end_pat, s)
        if not m_start:
            failures.append(f"{name}: start anchor not found")
            continue
        if not m_end or m_end.start() <= m_start.start():
            failures.append(f"{name}: end anchor not found or misplaced")
            continue
        block = s[m_start.start():m_end.start()]
        new = (s[:m_start.start()]
               + BEGIN + "\n\n" + block.rstrip() + "\n\n" + END + "\n\n"
               + s[m_end.start():])
        p.write_text(new, encoding="utf-8")
        print(f"  {name}: wrapped {len(block):,} characters of results prose")
    if failures:
        print("!! FAILURES:")
        for f in failures:
            print(f"   {f}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
