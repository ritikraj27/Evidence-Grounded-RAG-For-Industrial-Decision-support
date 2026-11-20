#!/usr/bin/env python3
"""Build the terminology guide.

One document, every keyword the work uses, given twice: once in ordinary
words and once in the technical words, with the work's own number attached.
It is the layer between the plain-language guide, which tells the story, and
the technical companion, which derives the formulas.

The source is markdown, in parts, under `deliverables/templates/terminology/`.
The measured values are substituted into the parts from the archived result
files, so the numbers in the document are the numbers on the slides.

Usage:
    python3 deliverables/scripts/make_terminology.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DELIV = ROOT / "deliverables"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from companion_build import Companion, build  # noqa: E402

TEMPLATES = DELIV / "templates" / "terminology"

PARTS = [
    "Part0_Front.md",
    "Part1_Industrial.md",
    "Part2_Corpus.md",
    "Part3_Retrieval.md",
    "Part4_Generator.md",
    "Part5_Gate.md",
    "Part6_Benchmark.md",
    "Part7_Statistics.md",
    "Part8_Machinery.md",
    "Part9_Timing.md",
    "Part10_Cheat_Sheet.md",
]

SPEC = Companion(
    deck=DELIV / "final_mtp.pptx",
    parts_dir=TEMPLATES,
    part_files=PARTS,
    out_md=DELIV / "MTP_Terminology.md",
    out_pdf=DELIV / "MTP_Terminology.pdf",
    title="The Words of This Work",
    subtitle="Every keyword, in plain language and in technical language, "
             "with the number that belongs to it",
    shorttitle="The terminology guide",
    author="Ritik Raj (25IM60R12), Department of Industrial and Systems "
           "Engineering, IIT Kharagpur",
    date="",
    label="terminology",
    metadata="",
)

if __name__ == "__main__":
    raise SystemExit(build(SPEC))
