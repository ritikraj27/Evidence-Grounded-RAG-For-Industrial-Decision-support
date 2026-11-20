#!/usr/bin/env python3
"""Build the explanation of the final deck's speaker script.

The deck is what the panel sees and the script is what is said. This builds
the third document: why the script is worded the way it is, what each slide
argues, the numbers that have to be said exactly, and the questions to
expect. It is a document of prose, so it carries no pictures and uses the
ordinary page geometry.

Part C, the slide-by-slide part, is generated from the same per-slide data
that writes the script, so the two documents cannot disagree about what a
slide argues or what the trap on it is. The other three parts are written
out, in the templates directory, and the measured values are substituted into
them from the archived result files.

Usage:
    python3 deliverables/scripts/make_final_mtp_script_guide.py
"""
from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DELIV = ROOT / "deliverables"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from companion_build import Companion, build  # noqa: E402
from make_final_mtp_script import (ARGUES, CLAIM, REFUSES, SAYS,  # noqa: E402
                                   TRAP, WPM, WHY)

TEMPLATES = DELIV / "templates" / "final_script_guide"

PARTS = ["Part0_Front.md", "PartA_The_Argument.md", "PartB_Delivering.md",
         "PartC_Slide_by_Slide.md", "PartD_Numbers_Traps_Questions.md"]


def mmss(seconds: int) -> str:
    return f"{seconds // 60}:{seconds % 60:02d}"


def part_c() -> str:
    """The slide-by-slide part, written from the shared per-slide data.

    The clock column is the same clock the script's timing plan carries, so
    the two documents point at the same moment.
    """
    out = ["# Part C. The script, slide by slide", ""]
    out.append("What each slide argues, why the script is worded the way it "
               "is, the claim it makes, the claim it refuses to make, and the "
               "trap on it. The wording of the script is the authoritative "
               "part; this part explains it.")
    out.append("")
    cum = 0
    for n, title, say in SAYS:
        secs = max(5, round(len(say.split()) / WPM * 60))
        cum += secs
        out.append(f"## C.{n} {title} ({secs} seconds, clock {mmss(cum)})")
        out.append("")
        out.append(f"**What it argues.** {ARGUES[n]}")
        out.append("")
        out.append(f"**Why it is worded this way.** {WHY[n]}")
        out.append("")
        out.append(f"**The claim it makes.** {CLAIM[n]}")
        out.append("")
        out.append(f"**The claim it refuses to make.** {REFUSES[n]}")
        out.append("")
        out.append(f"**The trap.** {TRAP[n]}")
        out.append("")
    return "\n".join(out)


def main() -> int:
    if not TEMPLATES.exists():
        print(f"  x {TEMPLATES} not found")
        return 1

    # The generated part is written beside the written ones, in a temporary
    # directory, so the templates stay the source of what is written by hand.
    with tempfile.TemporaryDirectory(prefix="mtp-final-guide-") as tmp:
        parts_dir = Path(tmp)
        for name in PARTS:
            if name == "PartC_Slide_by_Slide.md":
                (parts_dir / name).write_text(part_c(), encoding="utf-8")
            else:
                src = TEMPLATES / name
                if not src.exists():
                    print(f"  x {name} not found")
                    return 1
                shutil.copy2(src, parts_dir / name)

        spec = Companion(
            deck=DELIV / "final_mtp.pptx",
            parts_dir=parts_dir,
            part_files=PARTS,
            out_md=DELIV / "final_mtp_script_guide.md",
            out_pdf=DELIV / "final_mtp_script_guide.pdf",
            title="The Script, Explained",
            subtitle="How the ten-minute defence script is built, what each "
                     "slide argues, and how to answer the panel",
            shorttitle="The script, explained",
            author="Ritik Raj (25IM60R12), Department of Industrial and "
                   "Systems Engineering, IIT Kharagpur",
            date="",
            label="final script guide",
            metadata="",
        )
        return build(spec)


if __name__ == "__main__":
    raise SystemExit(main())
