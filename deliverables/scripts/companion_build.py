#!/usr/bin/env python3
"""Build a companion document for a deck.

A deck that carries every measured figure, every table and every formula is
legible to the audience and opaque to the person presenting it. This builds
the document that makes it legible: the vocabulary, the formulas with every
symbol named, the slides and the figures one at a time, and the protocol
behind the numbers.

The source is markdown, in parts. The parts are concatenated, the measured
values are substituted into them, the picture markers are replaced by the
pictures, and the result is rendered to PDF with the project's own chain:
markdown to pandoc to LaTeX to tectonic.

Two markers in the markdown are replaced by pictures. `<!-- slide:N -->`
becomes the picture of slide N of the deck, drawn by
`render_pptx_preview.py`, and `<!-- figure:NAME -->` becomes the measured
figure of that name. The pictures are laid into the work directory, because
the compiler is run there and resolves a relative path against its own
working directory.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DELIV = ROOT / "deliverables"
FIGDIR = DELIV / "figures"
MAKE_PDF = Path(__file__).resolve().parent / "make_pdf.py"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pdf_doc import (FIGURE_WIDTH, SLIDE_WIDTH, picture_block,  # noqa: E402
                      render_slides, widen_pipe_tables)
import substitute_tokens as _st  # noqa: E402

#: The markers in the markdown that a picture replaces. Both are matched
#: against a single line and against the whole document, so they carry the
#: multiline flag.
SLIDE_MARKER = re.compile(r"^<!--\s*slide:(\d+)\s*-->\s*$", re.M)
FIGURE_MARKER = re.compile(r"^<!--\s*figure:([A-Za-z0-9_\-]+)\s*-->\s*$", re.M)


@dataclass
class Companion:
    """What a companion document is built from."""
    deck: Path
    parts_dir: Path
    part_files: list[str]
    out_md: Path
    out_pdf: Path
    title: str
    subtitle: str
    shorttitle: str
    author: str
    date: str
    label: str = "companion"
    #: The page geometry, as the template's conditional takes it. A document
    #: whose content is a full-width picture of a slide needs the wider page;
    #: a document of prose does not.
    metadata: str = "widepage=true"


def read_parts(spec: Companion) -> str:
    """The companion's text, in the order the parts are read."""
    parts = []
    for name in spec.part_files:
        p = spec.parts_dir / name
        if not p.exists():
            raise SystemExit(f"  x {name} not found")
        parts.append(p.read_text(encoding="utf-8").strip())
    return "\n\n".join(parts) + "\n"


def substitute(text: str) -> str:
    """Replace {{TOKEN}} with the measured value, and fail on anything left.

    A corpus size or a query count is a measurement, and a measurement that
    is written out by hand is one that can go stale. The parts carry the
    token; the value comes from the archived result files.
    """
    values = _st.values()
    missing = sorted({m for m in re.findall(r"\{\{([A-Z0-9_]+)\}\}", text)
                      if m not in values})
    if missing:
        raise SystemExit(f"[companion] no measured value for: {missing}")
    return re.sub(r"\{\{([A-Z0-9_]+)\}\}",
                  lambda m: str(values[m.group(1)]), text)


def metadata(spec: Companion) -> str:
    """The YAML the template's title block reads."""
    def quoted(value: str) -> str:
        return '"' + value.replace('"', "'") + '"'

    return "\n".join([
        "---",
        f"title: {quoted(spec.title)}",
        f"subtitle: {quoted(spec.subtitle)}",
        f"author: {quoted(spec.author)}",
        f"date: {quoted(spec.date)}",
        f"shorttitle: {quoted(spec.shorttitle)}",
        "---",
        "",
    ])


def place_pictures(text: str, slides: dict[int, str], figures: set[str]) -> str:
    """Replace the picture markers with the pictures themselves.

    A marker for a slide or a figure that is not there is a mistake in the
    source, and it is reported rather than quietly dropped.
    """
    out: list[str] = []
    missing: list[str] = []
    for line in text.split("\n"):
        m = SLIDE_MARKER.match(line)
        if m:
            n = int(m.group(1))
            name = slides.get(n)
            if not name:
                missing.append(f"slide {n}")
                continue
            out.extend(picture_block(f"slides/{name}", SLIDE_WIDTH))
            continue

        m = FIGURE_MARKER.match(line)
        if m:
            name = m.group(1)
            if name not in figures:
                missing.append(f"figure {name}")
                continue
            out.extend(picture_block(f"figures/{name}.png", FIGURE_WIDTH))
            continue
        out.append(line)

    if missing:
        raise SystemExit("  x the source asks for pictures that are not "
                         "there: " + ", ".join(missing))
    return "\n".join(out)


def build(spec: Companion) -> int:
    """Build the companion's markdown and PDF."""
    for path in (spec.deck, FIGDIR):
        if not path.exists():
            print(f"  x {path.name} not found")
            return 1

    text = substitute(read_parts(spec))

    with tempfile.TemporaryDirectory(prefix="mtp-companion-") as tmp:
        work = Path(tmp)
        # The slide pictures are only drawn when the source asks for one. A
        # document about the script does not need them, and drawing twenty-four
        # of them is a minute of work for pictures nothing points at.
        slides: dict[int, str] = {}
        if SLIDE_MARKER.search(text):
            slides = render_slides(spec.deck, work / "slides")
            if not slides:
                print("  x the deck produced no slide pictures")
                return 1

        # The measured figures are copied in, so the compiler can find them
        # by the name the markdown uses.
        figdest = work / "figures"
        figdest.mkdir(parents=True, exist_ok=True)
        figures = set()
        for line in text.split("\n"):
            m = FIGURE_MARKER.match(line)
            if not m:
                continue
            name = m.group(1)
            src = FIGDIR / f"{name}.png"
            if not src.exists():
                continue
            shutil.copy2(src, figdest / f"{name}.png")
            figures.add(name)

        body = place_pictures(text, slides, figures)

        md = work / "companion.md"
        md.write_text(metadata(spec) + widen_pipe_tables(body), encoding="utf-8")

        # The compiler runs in the directory of the file it is given, so the
        # PDF is built inside the work directory, where the pictures are.
        args = [sys.executable, str(MAKE_PDF), str(md),
                str(work / spec.out_pdf.name), "--toc"]
        if spec.metadata:
            args += ["--metadata", spec.metadata]
        r = subprocess.run(args, capture_output=True, text=True, cwd=str(ROOT))
        for line in (r.stdout or "").splitlines():
            print("  " + line)
        if r.returncode != 0:
            for line in (r.stderr or "").splitlines()[-10:]:
                print("    " + line)
            return r.returncode

        (work / spec.out_pdf.name).replace(spec.out_pdf)

    spec.out_md.write_text(metadata(spec) + text, encoding="utf-8")
    if "{{" in spec.out_md.read_text(encoding="utf-8"):
        print("  x the shipped markdown still carries a token")
        return 1
    if not spec.out_pdf.exists():
        print(f"  x {spec.out_pdf.name} was not produced")
        return 1
    print(f"  [{spec.label}] {spec.out_pdf.name} "
          f"({spec.out_pdf.stat().st_size:,} bytes)")
    return 0
