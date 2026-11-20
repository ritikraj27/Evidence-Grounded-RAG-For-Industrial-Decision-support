#!/usr/bin/env python3
"""Build the companion to the ten-minute deck.

The deck is spoken in ten minutes and carries every measured figure, every
table and every formula. This is the document that makes it legible to the
person presenting it: the vocabulary, the thirteen formulas with every symbol
named, the slides and the figures one at a time, and the protocol behind the
numbers.

Usage:
    python3 deliverables/scripts/make_companion.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DELIV = ROOT / "deliverables"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from companion_build import Companion, build  # noqa: E402

SPEC = Companion(
    deck=DELIV / "MTP_Defence_Deck.pptx",
    parts_dir=DELIV / "templates" / "companion",
    part_files=[
        "Part0_Front.md",
        "PartA_Terms.md",
        "PartB_Formulas.md",
        "PartC_Slides_and_Figures.md",
        "PartD_Technicalities.md",
    ],
    out_md=DELIV / "MTP_Defence_Deck_Companion.md",
    out_pdf=DELIV / "MTP_Defence_Deck_Companion.pdf",
    title="The Ten-Minute Deck, Explained",
    subtitle="Every formula, every term and every measurement behind the "
             "ten-minute defence deck",
    shorttitle="The deck, explained",
    author="Ritik Raj (25IM60R12), Department of Industrial and Systems "
           "Engineering, IIT Kharagpur",
    date="",
    label="companion",
)

if __name__ == "__main__":
    raise SystemExit(build(SPEC))
