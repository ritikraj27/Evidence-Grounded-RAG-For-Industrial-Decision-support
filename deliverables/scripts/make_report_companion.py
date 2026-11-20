#!/usr/bin/env python3
"""Build the companion to the 38-slide report deck.

The report deck walks the report from end to end and carries every measured
figure, every table and every formula. This is the document that makes it
legible to the person presenting it: the vocabulary, the formulas with every
symbol named, the slides and the figures one at a time, and the protocol
behind the numbers.

Usage:
    python3 deliverables/scripts/make_report_companion.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DELIV = ROOT / "deliverables"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from companion_build import Companion, build  # noqa: E402

SPEC = Companion(
    deck=DELIV / "MTP_Report_Presentation.pptx",
    parts_dir=DELIV / "templates" / "companion_report",
    part_files=[
        "Part0_Front.md",
        "PartA_Terms.md",
        "PartB_Formulas.md",
        "PartC_Slides_and_Figures.md",
        "PartD_Technicalities.md",
    ],
    out_md=DELIV / "MTP_Report_Deck_Companion.md",
    out_pdf=DELIV / "MTP_Report_Deck_Companion.pdf",
    title="The Report Deck, Explained",
    subtitle="Every formula, every term and every measurement behind the "
             "38-slide report deck",
    shorttitle="The report deck, explained",
    author="Ritik Raj (25IM60R12), Department of Industrial and Systems "
           "Engineering, IIT Kharagpur",
    date="",
    label="companion",
)

if __name__ == "__main__":
    raise SystemExit(build(SPEC))
