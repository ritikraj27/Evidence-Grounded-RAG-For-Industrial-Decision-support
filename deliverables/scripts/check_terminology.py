#!/usr/bin/env python3
"""Check the terminology guide.

The guide is a document of words, and the only thing in it that can be wrong
in a way a reader would not catch is a number. So the check is: every
measurement in it must be a measurement on a slide, every term must carry
all three of its blocks, and nothing may be left unsubstituted.

Usage:
    python3 deliverables/scripts/check_terminology.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DELIV = ROOT / "deliverables"

DOC = DELIV / "MTP_Terminology.md"
DECK = DELIV / "final_mtp.pptx"

#: The numbers that are not measurements of this work and so do not appear on
#: a slide. Each one is a constant or an illustration, and the reason it is
#: here is the reason it is not a measurement.
ALLOWED = {
    "0.147": "the conventional small-effect threshold for Cliff's delta",
    "1024": "the width of the embedding vector, a property of the model",
    "24.95": "the illustrative tolerance example",
    "25.00": "the illustrative tolerance example",
    "25.05": "the illustrative tolerance example",
    "4.0": "the version of the Creative Commons licence the corpus ships under",
}

#: The three blocks every term carries.
BLOCKS = ("**Plain.**", "**Technical.**", "**Here.**")


def deck_text() -> str:
    """Every word on every slide, tables included."""
    from pptx import Presentation
    prs = Presentation(str(DECK))
    out = []
    for slide in prs.slides:
        for shape in slide.shapes:
            if shape.has_text_frame:
                out.append(shape.text_frame.text)
            if shape.has_table:
                for row in shape.table.rows:
                    for cell in row.cells:
                        out.append(cell.text)
    return "\n".join(out)


def measured_values() -> set[str]:
    """Every value the measured-value table holds."""
    import substitute_tokens as st
    out: set[str] = set()
    for value in st.values().values():
        out.add(str(value).strip())
        for part in re.findall(r"\d+(?:,\d{3})*(?:\.\d+)?", str(value)):
            out.add(part)
    return out


def main() -> int:
    problems: list[str] = []

    for path in (DOC, DECK):
        if not path.exists():
            print(f"  x missing: {path.name}")
            return 1

    text = DOC.read_text(encoding="utf-8")
    deck = deck_text()
    sourced = set(re.findall(r"\d+(?:,\d{3})*(?:\.\d+)?", deck))
    sourced |= measured_values()

    terms = re.findall(r"^### (.+)$", text, re.M)
    print("=== the terminology guide ===")
    print(f"  terms: {len(terms)}")
    if len(terms) < 100:
        problems.append(f"the guide carries {len(terms)} terms, which is too "
                        f"few to be a glossary of this work")
    dupes = {t for t in terms if terms.count(t) > 1}
    if dupes:
        problems.append(f"these terms appear twice: {sorted(dupes)}")

    # Every term carries all three blocks.
    entries = re.split(r"^### ", text, flags=re.M)[1:]
    for entry in entries:
        name = entry.split("\n", 1)[0].strip()
        for block in BLOCKS:
            if block not in entry:
                problems.append(f"'{name}' has no {block} block")

    # The numbers.
    nums = set(re.findall(r"(?<![\w.])\d+(?:,\d{3})*(?:\.\d+)?%?", text))
    missing = sorted(n for n in nums if n not in sourced and n not in ALLOWED)
    print(f"  numbers: {len(nums) - len(missing)} of {len(nums)} sourced "
          f"from a slide or a measured value")
    if missing:
        problems.append(f"the guide prints numbers that are neither on a "
                        f"slide nor a measured value: {missing}")
    for n in ALLOWED:
        if n not in text:
            problems.append(f"the allowed constant {n} is no longer used")

    # Nothing unsubstituted.
    left = re.findall(r"\{[A-Z][A-Z0-9_]{2,}\}", text)
    if left:
        problems.append(f"the guide still carries tokens: {sorted(set(left))[:6]}")

    # The house prose rules. A table row is not a sentence, so the tables
    # are taken out before the sentences are counted.
    for label, ch in (("em dash", "—"), ("en dash", "–")):
        if ch in text:
            problems.append(f"the guide contains a {label}")
    prose = "\n".join(ln for ln in text.splitlines()
                      if not ln.lstrip().startswith("|"))
    long_ones = [s for s in re.split(r"(?<=[.!?])\s+", prose)
                 if len(s.split()) > 55]
    if long_ones:
        problems.append(f"the guide has {len(long_ones)} sentences over 55 "
                        f"words: {long_ones[0][:70]}")

    print()
    if problems:
        print(f"  {len(problems)} problem(s):")
        for p in problems:
            print(f"    x {p}")
        return 1
    print("  all checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
