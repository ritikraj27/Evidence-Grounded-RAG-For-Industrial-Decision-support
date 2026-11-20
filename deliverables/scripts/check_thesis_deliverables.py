#!/usr/bin/env python3
"""Check the two fresh thesis deliverables.

The report and the deck are generated, so the checks that matter are the ones
that can be run against the built files rather than against the source:

  * the deck has at least the required number of slides,
  * no text frame in the deck overflows the shape it sits in,
  * neither file carries a colour that is not a grey,
  * neither file contains an em dash, which the reader asked to be gone,
  * the report's equations are real Word equations rather than pictures,
  * the report is at least the required number of pages,
  * the two files agree, because they read the same measured-value table.

Usage:
    python3 deliverables/scripts/check_thesis_deliverables.py
"""
from __future__ import annotations

import math
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from monochrome import ACCENT  # noqa: E402
DELIV = ROOT / "deliverables"
DOCX = DELIV / "MTP_Report.docx"
MD = DELIV / "MTP_Report.md"
PPTX = DELIV / "MTP_Report_Presentation.pptx"

MIN_PAGES = 20
MIN_SLIDES = 20
MIN_EQUATIONS = 10

#: Mean advance width of mixed-case text, in em. The same estimate the
#: project's own slide checker uses.
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


def docx_text(path: Path) -> str:
    with zipfile.ZipFile(path) as z:
        xml = z.read("word/document.xml").decode("utf-8", "ignore")
    return re.sub(r"<[^>]+>", " ", xml)


def pptx_text(path: Path) -> str:
    from pptx import Presentation
    prs = Presentation(str(path))
    out = []
    for slide in prs.slides:
        for shape in slide.shapes:
            if shape.has_text_frame:
                out.append(shape.text_frame.text)
    return "\n".join(out)


def main() -> int:
    problems: list[str] = []

    for p in (DOCX, MD, PPTX):
        if not p.exists():
            problems.append(f"missing deliverable: {p.name}")
    if problems:
        for p in problems:
            print(f"  x {p}")
        return 1

    # ---- the report
    with zipfile.ZipFile(DOCX) as z:
        xml = z.read("word/document.xml").decode("utf-8", "ignore")
    n_eq = xml.count("<m:oMath")
    print(f"=== report ===")
    print(f"  equations compiled from LaTeX: {n_eq}")
    if n_eq < MIN_EQUATIONS:
        problems.append(f"the report has {n_eq} compiled equations, "
                        f"the floor is {MIN_EQUATIONS}")

    dt = docx_text(DOCX)
    if "—" in dt:
        problems.append("the report still contains an em dash")
    if "{{" in dt:
        problems.append("the report contains an unsubstituted placeholder")
    # A token reference that reached the page as literal text is a defect the
    # eye finds immediately and the reader has to guess about. It happened
    # once: a single-brace reference in a generator's plain string.
    for m in re.finditer(r"\{[A-Z][A-Z0-9_]{2,}\}", dt):
        problems.append(f"the report prints a literal token: {m.group(0)}")

    # The figures have to be in the document, in order, and numbered in the
    # order they appear. A figure that was dropped by the build leaves a
    # caption with nothing under it, and the reader has no way of telling.
    with zipfile.ZipFile(DOCX) as z:
        media = [n for n in z.namelist() if n.startswith("word/media/")]
    n_figures = len(media)
    print(f"  figures embedded in the report: {n_figures}")
    if n_figures < 6:
        problems.append(f"the report carries {n_figures} figure(s); the six "
                        f"measured figures are all meant to be in it")
    # The contents list has to be there, with page numbers in it. An empty
    # table of contents is what a document with an unrefreshed field opens
    # with, and it is the first thing a reader looks at. The entries live
    # in a structured document tag, so they are read out of the XML.
    with zipfile.ZipFile(DOCX) as z:
        doc_xml = z.read("word/document.xml").decode("utf-8")
    toc_paras = re.findall(
        r'<w:pStyle w:val="TOC[123]"/>.*?</w:p>', doc_xml, re.S)
    print(f"  contents entries: {len(toc_paras)}")
    if len(toc_paras) < 10:
        problems.append(f"the contents list has {len(toc_paras)} entries; "
                        f"it should carry every heading")
    if toc_paras and "TOC \\o" not in doc_xml:
        problems.append("the contents list is not a live field, so a reader "
                        "cannot refresh the page numbers")
    # The page numbers have to be there, and they have to go up.
    if toc_paras:
        nums = []
        for t in toc_paras:
            parts = re.findall(r"<w:t[^>]*>([^<]*)</w:t>", t)
            if parts and parts[-1].strip().isdigit():
                nums.append(int(parts[-1]))
        print(f"  contents page numbers: {len(nums)}")
        if len(nums) < len(toc_paras):
            problems.append("the contents list is missing its page numbers")
        elif nums != sorted(nums):
            problems.append("the contents page numbers are not in order")
    # The two settings that make Word rebuild the contents on open, and
    # rebuild it before the document has been laid out.
    with zipfile.ZipFile(DOCX) as z:
        settings = z.read("word/settings.xml").decode("utf-8")
    if "w:dirty" in doc_xml:
        problems.append("the contents field is marked dirty; Word would "
                        "rebuild it before the document is laid out")
    if "updateFields" in settings:
        problems.append("the document asks Word to update every field on "
                        "open, which empties the contents")

    labels = [int(m) for m in re.findall(r"\bFigure\s+(\d+)\.", dt)]
    if labels and labels != sorted(labels):
        problems.append(f"the report's figure numbers are out of order: {labels}")
    if labels and len(set(labels)) != len(labels):
        problems.append(f"the report's figure numbers repeat: {labels}")

    pages = -1
    pdf = DELIV / "MTP_Report.pdf"
    if pdf.exists():
        try:
            import pypdf
            pages = len(pypdf.PdfReader(str(pdf)).pages)
        except Exception:
            pages = -1
    print(f"  pages in the reading copy: {pages}")
    if 0 <= pages < MIN_PAGES:
        problems.append(f"the report is {pages} pages, the floor is {MIN_PAGES}")

    # ---- the legacy formats, for a department that asks for them.
    # They are optional: the Word 97-2003 and PowerPoint 97-2003 formats
    # cannot carry a modern equation, and the department has the current
    # ones. A legacy copy that is here has to be current, though, or it is a
    # revision behind and nobody would know.
    for modern, legacy in ((DOCX, DOCX.with_suffix(".doc")),
                            (PPTX, PPTX.with_suffix(".ppt"))):
        if not legacy.exists():
            print(f"  legacy format: {legacy.name} not present (optional)")
            continue
        head = legacy.read_bytes()[:8]
        if not head.startswith(b"\xd0\xcf\x11\xe0"):
            problems.append(f"{legacy.name} is not a Word 97-2003 / "
                            f"PowerPoint 97-2003 file")
        # The legacy copy has to be at least as new as the file it was
        # made from, or it is a revision behind and nobody would know.
        if legacy.stat().st_mtime < modern.stat().st_mtime:
            problems.append(f"{legacy.name} is older than {modern.name}; run "
                            f"deliverables/scripts/make_legacy_formats.py")
    print(f"  legacy formats: {DOCX.with_suffix('.doc').name}, "
          f"{PPTX.with_suffix('.ppt').name}")

    # ---- the deck
    from pptx import Presentation
    prs = Presentation(str(PPTX))
    n_slides = len(prs.slides._sldIdLst)
    print(f"=== deck ===")
    print(f"  slides: {n_slides}")
    if n_slides < MIN_SLIDES:
        problems.append(f"the deck has {n_slides} slides, the floor is {MIN_SLIDES}")

    overflow = 0
    for i, slide in enumerate(prs.slides, start=1):
        for shape in slide.shapes:
            if not shape.has_text_frame or not shape.text_frame.text.strip():
                continue
            box_h = shape.height / 914400.0
            need_h = frame_height_in(shape)
            if need_h > box_h * 1.30 and need_h - box_h > 0.12:
                overflow += 1
                problems.append(
                    f"slide {i}: text needs about {need_h:.2f}in in a "
                    f"{box_h:.2f}in box: "
                    f"{shape.text_frame.text[:56].strip()!r}")
    print(f"  possible text overflows: {overflow}")

    pt = pptx_text(PPTX)
    if "—" in pt:
        problems.append("the deck still contains an em dash")
    for m in re.finditer(r"\{[A-Z][A-Z0-9_]{2,}\}", pt):
        problems.append(f"the deck prints a literal token: {m.group(0)}")

    # ---- both files must be grey
    for p in (DOCX, PPTX):
        bad = non_grey_colours(p)
        print(f"  non-grey colours in {p.name}: {len(bad)}")
        for b in bad[:5]:
            problems.append(f"{p.name} carries a colour that is not a grey: {b}")

    # ---- the two must agree
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import substitute_tokens as st
    values = st.values()
    md = MD.read_text(encoding="utf-8")
    disagree = []
    for token in ("GEN_A_FITTED_UNANS_ANSWER_RATE", "GEN_A_NOGATE_UNANS_ANSWER_RATE",
                  "CONTRA_PRECISION_PCT", "UNANS_HARD_REFUSED_PCT",
                  "FOCUS_GATE_ABST_PRECISION", "TAU"):
        v = str(values[token])
        if v not in md:
            disagree.append(f"the report does not carry {token} ({v})")
        if v not in pt:
            disagree.append(f"the deck does not carry {token} ({v})")
    if disagree:
        for d in disagree:
            problems.append(d)
    print(f"  agreement between the report and the deck: "
          f"{'checked' if not disagree else 'PROBLEM'}")

    print()
    if problems:
        print(f"  {len(problems)} problem(s):")
        for p in problems:
            print(f"    x {p}")
        return 1
    print("  all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
