#!/usr/bin/env python3
"""Stop a paragraph being cut in two by a number at the start of a line.

A line that begins with a number and a full stop reads as a markdown
ordered-list item, and the DOCX writer takes it as one, so a paragraph can
be broken in half by a measured value that happened to land at the start of
a line. The templates wrap their prose at a fixed column, so whether that
happens depends on how long the value is, and the generated documents --
which are written after the substitution -- are not covered by the
substitution's own guard.

This runs at the end of the build, over every markdown deliverable, and
joins such a line to the line above it. Markdown soft-wraps and the DOCX
writer joins wrapped lines, so the rendered text is unchanged; what changes
is that the paragraph is whole again.

It also fails the build if a hazard survives, because a silently
half-rendered paragraph is worse than a broken build.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "deliverables" / "scripts"))

from results_source import pull_up_leading_numbers  # noqa: E402

TARGETS = [
    "deliverables/Deliverable_1_Complete_Guide.md",
    "deliverables/Deliverable_1_Part1_Content.md",
    "deliverables/Deliverable_1_PartD_Code.md",
    "deliverables/Deliverable_1_PartE_Results.md",
    "deliverables/Deliverable_1_PartF_toJ.md",
    "deliverables/Deliverable_2a_Technical_Report.md",
    "deliverables/MTP_Plain_Language_Guide.md",
    "deliverables/MTP_Status_Report.md",
    "deliverables/MTP_Technical_Documentation.md",
    "deliverables/READ_ME_FIRST.md",
]

#: A line that begins with a number and a full stop, and whose predecessor is
#: a paragraph line rather than a list item or a blank line.
_HAZARD = re.compile(r"^\s*\d+\.\s")


def _hazards(text: str) -> list[int]:
    """The line numbers of the hazards left in a document."""
    out: list[int] = []
    lines = text.split("\n")
    list_open = False
    list_indent = 0
    list_last = 0
    in_fence = False
    for i, line in enumerate(lines, 1):
        stripped = line.lstrip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if not line.strip():
            list_open = False
            continue
        if in_fence:
            continue
        m = _HAZARD.match(line)
        if not m:
            continue
        indent = len(line) - len(stripped)
        num = int(stripped.split(".", 1)[0])
        prev_blank = (i == 1) or (not lines[i - 2].strip())
        if list_open and indent == list_indent and num == list_last + 1:
            list_last = num
            continue
        if not list_open and prev_blank:
            list_open = True
            list_indent = indent
            list_last = num
            continue
        out.append(i)
    return out


def main() -> int:
    bad = 0
    for rel in TARGETS:
        p = ROOT / rel
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8")
        fixed = pull_up_leading_numbers(text)
        left = _hazards(fixed)
        if left:
            print(f"  !! {p.name}: {len(left)} paragraph(s) still broken by a "
                  f"number at the start of a line (lines {left[:6]})")
            bad += len(left)
            continue
        if fixed != text:
            p.write_text(fixed, encoding="utf-8")
            print(f"  joined the broken paragraphs in {p.name}")
    if bad:
        return 1
    print("  no paragraph is broken by a number at the start of a line")
    return 0


if __name__ == "__main__":
    sys.exit(main())
