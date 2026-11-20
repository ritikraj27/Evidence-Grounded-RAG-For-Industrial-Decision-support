#!/usr/bin/env python3
"""Estimate text overflow in the generated presentation.

A slide deck fails in the eyes, not in the file format: a paragraph that runs
past the bottom of its box is invisible in the XML and obvious on the screen.
There is no PowerPoint here to render and check, so this approximates the
rendered height of every text frame and compares it with the shape it sits in.

The character-width estimate is deliberately conservative. For Calibri and
Cambria at a given point size, the mean advance width of mixed-case English
text is close to 0.48 em; the estimate uses that, adds a 10% safety margin,
and counts line breaks explicitly. It will not catch every overflow, but it
catches the gross ones — which are the ones that make a slide look broken.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from pptx import Presentation
from pptx.util import Emu

ROOT = Path(__file__).resolve().parents[2]
PPTX = ROOT / "deliverables" / "Deliverable_4_Presentation_18Nov.pptx"

#: Mean advance width of mixed-case text, in em.
MEAN_ADVANCE = 0.50
SAFETY = 1.10
LINE_FACTOR = 1.22


def frame_height_in(shape) -> float:
    """Estimated rendered height of a text frame, in inches."""
    tf = shape.text_frame
    width_pt = shape.width / 12700.0
    height_pt = shape.height / 12700.0
    if width_pt <= 0:
        return 0.0
    total = 0.0
    for para in tf.paragraphs:
        text = "".join(r.text for r in para.runs)
        sizes = [r.font.size.pt for r in para.runs if r.font.size]
        size = max(sizes) if sizes else 18.0
        if not text.strip():
            total += size * LINE_FACTOR
            continue
        usable = width_pt - (tf.margin_left + tf.margin_right) / 12700.0
        char_w = MEAN_ADVANCE * size * SAFETY
        per_line = max(int(usable / char_w), 8)
        lines = max(1, math.ceil(len(text) / per_line))
        space_after = para.space_after.pt if para.space_after else 0
        total += lines * size * LINE_FACTOR + space_after
    return total / 72.0


def main() -> int:
    if not PPTX.exists():
        print(f"  ✗ {PPTX.name} not found")
        return 1
    prs = Presentation(str(PPTX))
    problems = []
    for i, slide in enumerate(prs.slides, start=1):
        for shape in slide.shapes:
            if not shape.has_text_frame or not shape.text_frame.text.strip():
                continue
            box_h = shape.height / 914400.0
            need_h = frame_height_in(shape)
            if need_h > box_h * 1.30 and need_h - box_h > 0.12:
                problems.append(
                    f"slide {i}: text needs ~{need_h:.2f}in in a {box_h:.2f}in "
                    f"box — '{shape.text_frame.text[:58].strip()}'"
                )
    print(f"=== slide layout check ({len(prs.slides.__iter__.__self__._sldIdLst)} slides) ===")
    if problems:
        print(f"  {len(problems)} possible overflow(s):")
        for p in problems:
            print(f"    ! {p}")
        return 1
    print("  no overflow detected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
