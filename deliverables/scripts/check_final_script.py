#!/usr/bin/env python3
"""Check the final deck's script and its guide against the deck.

The script is a spoken document, and the only way it can fail silently is by
losing its text: a regular expression that rewrites a label can swallow the
paragraph after it, and the document still looks fine until someone opens it
and finds that the words to say are missing. This checks that the script
still carries one block per slide, that the seconds claimed for each slide
match the words actually written, that the guide's clock agrees with the
script's, and that every number in the spoken text is a number that appears
on a slide.

Usage:
    python3 deliverables/scripts/check_final_script.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DELIV = ROOT / "deliverables"

SCRIPT = DELIV / "final_mtp_script.md"
GUIDE = DELIV / "final_mtp_script_guide.md"
DECK = DELIV / "final_mtp.pptx"

#: How many slides the deck has, and therefore how many script blocks and how
#: many guide entries there must be.
SLIDES = 26

#: The words a minute the timings assume.
WPM = 140

#: A script section: the heading, and the three blocks that follow it.
SCRIPT_SECTION = re.compile(
    r"^## (\d+)\. (.+?) \((\d+) seconds, clock (\d+):(\d\d)\)\n"
    r"\n\*\*Say\*\*\n\n(.+?)\n\n\*\*On the slide\.\*\*\n\n(.+?)\n\n"
    r"\*\*Why this slide matters\.\*\* (.+?)(?=\n\n(?:##|\*\*)|\Z)",
    re.M | re.S)

#: A guide entry: the heading, and the five fields that follow it.
GUIDE_SECTION = re.compile(
    r"^## C\.(\d+) (.+?) \((\d+) seconds, clock (\d+):(\d\d)\)\n"
    r"\n\*\*What it argues\.\*\* (.+?)\n\n"
    r"\*\*Why it is worded this way\.\*\* (.+?)\n\n"
    r"\*\*The claim it makes\.\*\* (.+?)\n\n"
    r"\*\*The claim it refuses to make\.\*\* (.+?)\n\n"
    r"\*\*The trap\.\*\* (.+?)(?=\n\n##|\Z)",
    re.M | re.S)

#: The numbers a reader would want to check, which are the ones in the
#: spoken text and in the guide's prose. The timing columns are excluded,
#: because a clock reading is not a measurement.
TIMING = re.compile(r"\b\d+ seconds\b|\bclock \d+:\d\d\b|\b\d+:\d\d\b")


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
    """Every value the measured-value table holds.

    A number in a document is sourced if it is on a slide or if it is a
    measured value. The second case is the one the latency measurement needs:
    it is a reading from an archived result file rather than a figure the
    deck happens to carry, and it is exactly as checkable.
    """
    import substitute_tokens as st
    out: set[str] = set()
    for value in st.values().values():
        out.add(str(value).strip())
        for part in re.findall(r"\d+(?:,\d{3})*(?:\.\d+)?", str(value)):
            out.add(part)
    return out


def numbers_in(text: str) -> set[str]:
    """The numbers in a piece of prose, with the timings taken out."""
    clean = TIMING.sub(" ", text)
    return set(re.findall(r"(?<![\w.])\d+(?:,\d{3})*(?:\.\d+)?%?", clean))


def main() -> int:
    problems: list[str] = []

    for path in (SCRIPT, GUIDE, DECK):
        if not path.exists():
            print(f"  x missing: {path.name}")
            return 1

    script = SCRIPT.read_text(encoding="utf-8")
    guide = GUIDE.read_text(encoding="utf-8")
    deck = deck_text()
    sourced = set(re.findall(r"\d+(?:,\d{3})*(?:\.\d+)?", deck))
    sourced |= measured_values()

    # ---- the script
    print("=== the script ===")
    sections = SCRIPT_SECTION.findall(script)
    print(f"  sections: {len(sections)}")
    if len(sections) != SLIDES:
        problems.append(f"the script has {len(sections)} sections, and the "
                        f"deck has {SLIDES} slides")
    if not sections:
        problems.append("the script has no spoken text at all")

    cum = 0
    spoken = []
    for n, title, secs, cm, cs, say, on_slide, why in sections:
        words = len(say.split())
        implied = max(5, round(words / WPM * 60))
        cum += implied
        spoken.append(say)
        if int(secs) != implied:
            problems.append(f"slide {n} claims {secs} seconds for {words} "
                            f"words, which is {implied} at {WPM} a minute")
        if int(cm) * 60 + int(cs) != cum:
            problems.append(f"slide {n} claims clock {cm}:{cs}, which should "
                            f"be {cum // 60}:{cum % 60:02d}")
        if not on_slide.strip():
            problems.append(f"slide {n} has nothing under 'On the slide'")
        if not why.strip():
            problems.append(f"slide {n} has nothing under 'Why this slide "
                            f"matters'")
    total = sum(len(b.split()) for b in spoken)
    print(f"  spoken words: {total}")
    print(f"  total at {WPM} wpm: {cum // 60}:{cum % 60:02d}")
    if cum > 600:
        problems.append(f"the script runs to {cum}s, which is over the "
                        f"ten-minute slot")

    # ---- the guide
    print("=== the guide ===")
    entries = GUIDE_SECTION.findall(guide)
    print(f"  slide entries: {len(entries)}")
    if len(entries) != SLIDES:
        problems.append(f"the guide has {len(entries)} slide entries, not "
                        f"{SLIDES}")
    for (n, title, secs, cm, cs, argues, why, claim, refuses, trap) in entries:
        for label, text in (("What it argues", argues),
                            ("Why it is worded this way", why),
                            ("The claim it makes", claim),
                            ("The claim it refuses to make", refuses),
                            ("The trap", trap)):
            if not text.strip():
                problems.append(f"guide entry C.{n} has nothing under "
                                f"'{label}'")

    # The guide's clock must be the script's clock.
    script_clock = {(n, f"{cm}:{cs}") for n, _, _, cm, cs, _, _, _ in sections}
    guide_clock = {(n, f"{cm}:{cs}") for n, _, _, cm, cs, *_ in entries}
    if script_clock and guide_clock and script_clock != guide_clock:
        problems.append("the guide's clock does not agree with the script's")
    print(f"  clock agrees with the script: "
          f"{script_clock == guide_clock if script_clock and guide_clock else 'n/a'}")

    questions = len(re.findall(r'^\*\*"', guide, re.M))
    print(f"  panel questions answered: {questions}")
    if questions < 20:
        problems.append(f"the guide answers only {questions} panel questions")

    # ---- the numbers
    print("=== the numbers ===")
    for label, text in (("script", "\n".join(spoken)),
                        ("guide", guide)):
        nums = numbers_in(text)
        missing = sorted(n for n in nums if n not in sourced)
        print(f"  {label}: {len(nums) - len(missing)} of {len(nums)} numbers "
              f"are sourced from a slide or a measured value")
        if missing:
            problems.append(f"the {label} prints numbers that are neither on "
                            f"a slide nor a measured value: {missing[:8]}")

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
