#!/usr/bin/env python3
"""Check a defence deck.

The house rules for this deliverable are the same as for the report deck, and
they are mechanical, so they are checked against the built file rather than
against the source:

  * the deck has enough slides to hold every figure, table and formula, and no
    more than a ten-minute talk can carry,
  * no text frame overflows the shape it sits in,
  * nothing on a slide carries a colour that is not a grey,
  * no dash other than a plain hyphen survives,
  * none of the stock phrases of the genre is present,
  * no narration about the project's own process leaks in,
  * no unsubstituted token reaches the page.

Usage:
    .venv/bin/python deliverables/scripts/check_defence_deck.py
    .venv/bin/python deliverables/scripts/check_defence_deck.py \
        --deck deliverables/final_mtp.pptx --slides 50:90
"""
from __future__ import annotations

import math
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
PPTX = ROOT / "deliverables" / "MTP_Defence_Deck.pptx"

from check_human_tone import (DASHES, PHRASES, PROCESS_NARRATION,  # noqa: E402
                              sentences)
from monochrome import ACCENT  # noqa: E402

#: The talk is ten minutes. The deck holds every figure and table in the
#: report, and each one takes about half a minute to speak.
MIN_SLIDES = 20
MAX_SLIDES = 26

#: Mean advance width of mixed-case text, in em, and the safety factor on it.
#: The same estimate the report's own overflow check uses.
MEAN_ADVANCE = 0.50
SAFETY = 1.10
LINE_FACTOR = 1.22


def frame_height_in(shape) -> float:
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


def non_grey_colours(path: Path) -> list[str]:
    bad = []
    with zipfile.ZipFile(path) as z:
        for name in z.namelist():
            if not name.endswith(".xml"):
                continue
            xml = z.read(name).decode("utf-8", "ignore")
            for m in re.finditer(r'srgbClr val="([0-9A-Fa-f]{6})"', xml):
                h = m.group(1)
                if not (h[0:2] == h[2:4] == h[4:6]) and h.upper() != ACCENT:
                    bad.append(f"{name}: srgbClr {h}")
            for m in re.finditer(r'<w:color[^>]*w:val="([0-9A-Fa-f]{6})"', xml):
                h = m.group(1)
                if not (h[0:2] == h[2:4] == h[4:6]) and h.upper() != ACCENT:
                    bad.append(f"{name}: w:color {h}")
    return bad


def deck_text(path: Path = PPTX) -> str:
    from pptx import Presentation
    prs = Presentation(str(path))
    out = []
    for slide in prs.slides:
        for shape in slide.shapes:
            if shape.has_text_frame:
                out.append(shape.text_frame.text)
    return "\n".join(out)


def table_text(path: Path = PPTX) -> str:
    """The table cells, which the shape walk above does not reach."""
    from pptx import Presentation
    prs = Presentation(str(path))
    out = []
    for slide in prs.slides:
        for shape in slide.shapes:
            if shape.has_table:
                for row in shape.table.rows:
                    for cell in row.cells:
                        out.append(cell.text)
    return "\n".join(out)


def missing_glyphs(text: str) -> set[str]:
    """Characters the deck's own face does not have.

    A missing glyph is not a crash, it is a blank square in the middle of a
    number, and it only shows up when the deck is opened somewhere. The p
    values arrived here that way: the superscript minus is not in Times New
    Roman, so "9.3 x 10^-4" lost its sign.
    """
    try:
        from fontTools.ttLib import TTFont
    except ImportError:
        return set()
    path = Path("/System/Library/Fonts/Supplemental/Times New Roman.ttf")
    if not path.exists():
        return set()
    try:
        font = TTFont(str(path), lazy=True)
        cmap = set(font.getBestCmap().keys())
    except Exception:
        return set()
    return {ch for ch in set(text)
            if ord(ch) > 127 and ord(ch) not in cmap}


def check(deck: Path, min_slides: int, max_slides: int,
          notes_required: bool = True) -> int:
    """Check one deck against the house rules."""
    problems: list[str] = []

    if not deck.exists():
        print(f"  x missing deliverable: {deck.name}")
        return 1

    from pptx import Presentation
    prs = Presentation(str(deck))
    n_slides = len(prs.slides._sldIdLst)
    print(f"=== {deck.name} ===")
    print(f"  slides: {n_slides}")
    if n_slides < min_slides:
        problems.append(f"the deck has {n_slides} slides, the floor is "
                        f"{min_slides}")
    if n_slides > max_slides:
        problems.append(f"the deck has {n_slides} slides, which is more than "
                        f"it should carry ({max_slides})")

    # Every slide carries notes, because a deck that is spoken needs them.
    missing_notes = [i for i, s in enumerate(prs.slides, start=1)
                     if not s.has_notes_slide
                     or not s.notes_slide.notes_text_frame.text.strip()]
    print(f"  slides without speaker notes: {len(missing_notes)}")
    if missing_notes and notes_required:
        problems.append(f"these slides carry no speaker notes: "
                        f"{missing_notes}")

    # ---- overflow
    overflow = 0
    for i, slide in enumerate(prs.slides, start=1):
        for shape in slide.shapes:
            if not shape.has_text_frame or not shape.text_frame.text.strip():
                continue
            box_h = shape.height / 914400.0
            need_h = frame_height_in(shape)
            if need_h > box_h * 1.08 and need_h - box_h > 0.08:
                overflow += 1
                problems.append(
                    f"slide {i}: text needs about {need_h:.2f}in in a "
                    f"{box_h:.2f}in box: "
                    f"{shape.text_frame.text[:56].strip()!r}")
    print(f"  possible text overflows: {overflow}")

    # ---- dashes, stock phrases, process narration
    text = deck_text(deck)
    for label, ch in DASHES.items():
        n = text.count(ch)
        print(f"  {label}: {n}")
        if n:
            problems.append(f"the deck contains {n} {label}(s)")
    hits = []
    for pattern, label in PHRASES:
        for m in re.finditer(pattern, text, re.I):
            hits.append(label)
    print(f"  stock phrases: {len(hits)}")
    if hits:
        problems.append(f"the deck uses {len(hits)} stock phrase(s): "
                        f"{sorted(set(hits))}")

    flat = re.sub(r"\s+", " ", text)
    for label, pattern in PROCESS_NARRATION.items():
        n = len(re.findall(pattern, flat, re.I))
        if n:
            print(f"  {label}: {n}")
            problems.append(f"the deck carries {n} piece(s) of {label}")

    sents = sentences(text)
    long_ones = [s for s in sents if len(s.split()) > 55]
    print(f"  sentences over 55 words: {len(long_ones)} of {len(sents)}")
    if long_ones and len(long_ones) > len(sents) * 0.06:
        problems.append(f"the deck has {len(long_ones)} sentences over 55 words")

    # Two sentences in a row opening the same way reads as machine written.
    from check_human_tone import DELIBERATE
    runs = 0
    for block in text.split("\n"):
        block = block.strip()
        if len(block) < 12:
            continue
        block_sents = [x.strip() for x in
                       re.split(r"(?<=[.!?])\s+", block) if x.strip()]
        for a_, b_ in zip(block_sents, block_sents[1:]):
            if not (a_.startswith("The ") and b_.startswith("The ")):
                continue
            if a_.startswith("**") or a_ in DELIBERATE:
                continue
            runs += 1
    print(f"  paragraphs with two sentences opening the same way: {runs}")
    if runs > 3:
        problems.append(f"the deck has {runs} places where two sentences in a row "
                        f"open the same way")

    # ---- the table cells, which the shape walk does not reach
    tt = table_text(deck)
    for label, ch in DASHES.items():
        if ch in tt:
            problems.append(f"a table cell contains a {label}")
    for pattern, label in PHRASES:
        if re.search(pattern, tt, re.I):
            problems.append(f"a table cell uses the stock phrase {label}")

    # ---- unsubstituted tokens and stray braces
    for m in re.finditer(r"\{[A-Z][A-Z0-9_]{2,}\}", text + "\n" + tt):
        problems.append(f"the deck prints a literal token: {m.group(0)}")

    # ---- colour
    bad = non_grey_colours(deck)
    print(f"  non-grey colours: {len(bad)}")
    for b in bad[:5]:
        problems.append(f"the deck carries a colour that is not a grey: {b}")

    # ---- glyphs the deck's face does not have
    gone = missing_glyphs(text + "\n" + tt)
    print(f"  characters missing from Times New Roman: {len(gone)}")
    for ch in sorted(gone):
        problems.append(f"the deck prints U+{ord(ch):04X} {ch!r}, which Times "
                        f"New Roman does not have")

    print()
    if problems:
        print(f"  {len(problems)} problem(s):")
        for p in problems:
            print(f"    x {p}")
        return 1
    print("  all checks passed")
    return 0


def main() -> int:
    """Check the ten-minute deck, or another deck named on the command line."""
    import argparse

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--deck", default=str(PPTX),
                    help="the .pptx to check")
    ap.add_argument("--slides", default=f"{MIN_SLIDES}:{MAX_SLIDES}",
                    help="the acceptable slide count, as MIN:MAX")
    ap.add_argument("--no-notes", action="store_true",
                    help="the deck carries no speaker notes, and does not "
                         "have to")
    args = ap.parse_args()
    lo, _, hi = args.slides.partition(":")
    return check(Path(args.deck), int(lo), int(hi),
                 notes_required=not args.no_notes)


if __name__ == "__main__":
    raise SystemExit(main())
