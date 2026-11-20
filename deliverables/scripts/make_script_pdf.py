#!/usr/bin/env python3
"""Render the ten-minute deck's speaker script to a PDF.

The script is written as markdown and shipped as a Word document. This adds
the third form: a PDF that prints the slide above the words for that slide,
so the presenter can read what to say against the thing they are pointing
at. The diagram, the tables and the figures are on the slides, and a script
that describes them without showing them is half a script.

The pictures come from `render_pptx_preview.py`, which reads the built .pptx
and draws it with matplotlib. That is an approximation of PowerPoint's layout
rather than PowerPoint's layout, so a word may sit slightly differently here
than it will on the screen. The words are the authoritative part; the picture
is there to show the shape of the slide.

The document's own title block becomes the PDF's title block, so it is
printed once at the top and not again as the first paragraph. Every slide
section starts a page, so the page a slide is on can be found by counting.

Usage:
    python3 deliverables/scripts/make_script_pdf.py
    python3 deliverables/scripts/make_script_pdf.py \
        --script deliverables/final_mtp_script.md \
        --deck deliverables/final_mtp.pptx \
        --out deliverables/final_mtp_script.pdf
"""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DELIV = ROOT / "deliverables"
SCRIPT_MD = DELIV / "MTP_Defence_Deck_Script.md"
DECK = DELIV / "MTP_Defence_Deck.pptx"
OUT = DELIV / "MTP_Defence_Deck_Script.pdf"
MAKE_PDF = Path(__file__).resolve().parent / "make_pdf.py"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pdf_doc import (page_break, picture_block, render_slides,  # noqa: E402
                     widen_pipe_tables)

#: A slide section of the script. The number is the slide's number in the
#: deck, which is what the timing table and the closing card refer to.
SLIDE_HEADING = re.compile(r"^##\s+(\d+)\.\s")

#: The date at the end of the author block.
DATE_AT_END = re.compile(r"((?:\d{1,2}\s+)?[A-Z][a-z]+\s+\d{4})\s*$")


def split_document(text: str) -> tuple[str, str, str]:
    """Split the script into its title, its title block and its body.

    The script opens with a heading, then the one-line description of what
    the document is, then the author's details, and then the body. The first
    two go into the PDF's title block, so they are printed once at the top
    rather than twice.
    """
    lines = text.split("\n")
    heads = [i for i, line in enumerate(lines) if line.startswith("# ")]
    if len(heads) < 2:
        raise SystemExit("  x the script has no title block to separate")
    title = lines[heads[0]][2:].strip()
    front = "\n".join(lines[heads[0] + 1:heads[1]]).strip()
    body = "\n".join(lines[heads[1]:]).strip()
    return title, front, body


def front_to_metadata(title: str, front: str) -> str:
    """Turn the title block into the YAML the template's title block reads."""
    # The title block is a bold one-liner followed by the author's details,
    # and the markdown wraps the details over two lines. The first line is
    # the subtitle and the rest is the author.
    lines = [ln.strip() for ln in front.split("\n") if ln.strip()]
    subtitle = lines[0] if lines else ""
    if subtitle.startswith("**") and subtitle.endswith("**"):
        subtitle = subtitle[2:-2].strip()
    author = " ".join(lines[1:])

    date = ""
    m = DATE_AT_END.search(author)
    if m:
        date = m.group(1)
        author = author[:m.start()].strip().rstrip(".")

    def quoted(value: str) -> str:
        return '"' + value.replace('"', "'") + '"'

    out = [
        "---",
        f"title: {quoted(title)}",
        f"subtitle: {quoted(subtitle)}",
        f"author: {quoted(author)}",
    ]
    if date:
        out.append(f"date: {quoted(date)}")
    out.append('shorttitle: "Speaker script"')
    out.append("---")
    out.append("")
    return "\n".join(out)


def add_slide_pictures(body: str, slides: dict[int, str]) -> str:
    """Put each slide's picture at the head of that slide's script block.

    Every section but the first starts on a new page, so the page a slide is
    on can be found by counting rather than by looking.
    """
    out: list[str] = []
    seen_section = False
    for line in body.split("\n"):
        if line.startswith("# ") and not line.startswith("## "):
            if seen_section:
                out.extend(page_break())
            seen_section = True
            out.append(line)
            continue

        m = SLIDE_HEADING.match(line)
        if m:
            n = int(m.group(1))
            if n > 1:
                out.extend(page_break())
            out.append(line)
            out.append("")
            name = slides.get(n)
            if name:
                out.extend(picture_block(f"slides/{name}", 0.94))
            continue
        out.append(line)
    return "\n".join(out)


def main(script_md: Path = SCRIPT_MD, deck: Path = DECK,
         out: Path = OUT) -> int:
    for path in (script_md, deck):
        if not path.exists():
            print(f"  x {path.name} not found")
            return 1

    title, front, body = split_document(script_md.read_text(encoding="utf-8"))

    with tempfile.TemporaryDirectory(prefix="mtp-script-pdf-") as tmp:
        work = Path(tmp)
        slides = render_slides(deck, work / "slides")
        if not slides:
            print("  x the deck produced no slide pictures")
            return 1

        md = work / "script.md"
        md.write_text(front_to_metadata(title, front)
                      + widen_pipe_tables(add_slide_pictures(body, slides)),
                      encoding="utf-8")

        # The compiler is run in the directory of the file it is given, so
        # the PDF is built inside the work directory, where the slide
        # pictures are. It is moved to its place afterwards.
        r = subprocess.run(
            [sys.executable, str(MAKE_PDF), str(md), str(work / out.name),
             "--metadata", "widepage=true"],
            capture_output=True, text=True, cwd=str(ROOT))
        for line in (r.stdout or "").splitlines():
            print("  " + line)
        if r.returncode != 0:
            for line in (r.stderr or "").splitlines()[-8:]:
                print("    " + line)
            return r.returncode

        (work / out.name).replace(out)

    if not out.exists():
        print(f"  x {out.name} was not produced")
        return 1
    print(f"  [script] {out.name} ({out.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--script", default=str(SCRIPT_MD),
                    help="the script's markdown")
    ap.add_argument("--deck", default=str(DECK),
                    help="the deck whose slides are printed above the words")
    ap.add_argument("--out", default=str(OUT),
                    help="the PDF to write")
    args = ap.parse_args()
    raise SystemExit(main(Path(args.script), Path(args.deck), Path(args.out)))
