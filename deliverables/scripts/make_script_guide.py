#!/usr/bin/env python3
"""Build the explanation of the speaker script.

The deck is what the audience sees and the script is what is said. This builds
the third document: why the script is written the way it is, what each slide
argues, the numbers that have to be said exactly, and the questions to expect.
It is a document of prose, so it carries no pictures and uses the ordinary page
geometry.

Its source is markdown, in parts, under `deliverables/templates/script_guide/`.
The parts are concatenated, the measured values are substituted into them, and
the result is rendered to PDF with the project's own chain: markdown to pandoc
to LaTeX to tectonic. The build is the shared one, so this document and the
two companions cannot drift apart in how they are laid out.

Usage:
    python3 deliverables/scripts/make_script_guide.py
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
    parts_dir=DELIV / "templates" / "script_guide",
    part_files=[
        "Part0_Front.md",
        "PartA_The_Argument.md",
        "PartB_Delivering.md",
        "PartC_Slide_by_Slide.md",
        "PartD_Claims_and_Questions.md",
    ],
    out_md=DELIV / "MTP_Defence_Script_Guide.md",
    out_pdf=DELIV / "MTP_Defence_Script_Guide.pdf",
    title="The Script, Explained",
    subtitle="How the ten-minute defence script is built, what each slide "
             "argues, and how to deliver it",
    shorttitle="The script, explained",
    author="Ritik Raj (25IM60R12), Department of Industrial and Systems "
           "Engineering, IIT Kharagpur",
    date="",
    label="script guide",
    metadata="",
)

if __name__ == "__main__":
    raise SystemExit(build(SPEC))
