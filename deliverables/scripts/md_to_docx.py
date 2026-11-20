#!/usr/bin/env python3
"""Convert a markdown document to a formatted DOCX.

Handles the subset of markdown used by the deliverables: ATX headings,
paragraphs, pipe tables, fenced code blocks, bullet and numbered lists, block
quotes, horizontal rules, and inline **bold** / *italic* / `code`.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
import sys

# The monochrome helper lives beside the shipped builders. The template
# copy of the deck generator sits one directory higher, so both places are
# offered to the import.
for _cand in (Path(__file__).resolve().parent,
              Path(__file__).resolve().parents[2] / "scripts"):
    if (_cand / "monochrome.py").exists():
        sys.path.insert(0, str(_cand))
        break
from monochrome import to_monochrome as _monochrome

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

BLACK = RGBColor(0x00, 0x00, 0x00)
BODY = "Times New Roman"
MONO = "Consolas"


def set_borders(doc):
    sec = doc.sections[0]
    sectPr = sec._sectPr
    pgBorders = OxmlElement("w:pgBorders")
    pgBorders.set(qn("w:offsetFrom"), "page")
    for edge in ("top", "left", "bottom", "right"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "6")
        el.set(qn("w:space"), "24")
        el.set(qn("w:color"), "000000")
        pgBorders.append(el)
    ref = sectPr.find(qn("w:pgMar"))
    (ref.addnext(pgBorders) if ref is not None else sectPr.append(pgBorders))


def add_page_footer(section):
    p = section.footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = p.add_run()
    fld = OxmlElement("w:fldSimple")
    fld.set(qn("w:instr"), "PAGE")
    run._r.addnext(fld)
    for r in p.runs:
        r.font.size = Pt(9)
        r.font.name = BODY


INLINE = re.compile(r"(\*\*.+?\*\*|\*[^*]+?\*|`[^`]+?`)")


def add_inline(paragraph, text, *, size, base_bold=False, base_italic=False,
                color=None, font=BODY):
    for chunk in INLINE.split(text):
        if not chunk:
            continue
        bold, italic, mono = base_bold, base_italic, False
        if chunk.startswith("**") and chunk.endswith("**") and len(chunk) > 4:
            chunk, bold = chunk[2:-2], True
        elif chunk.startswith("*") and chunk.endswith("*") and len(chunk) > 2:
            chunk, italic = chunk[1:-1], True
        elif chunk.startswith("`") and chunk.endswith("`") and len(chunk) > 2:
            chunk, mono = chunk[1:-1], True
        r = paragraph.add_run(chunk)
        r.font.size = size
        r.font.bold = bold
        r.font.italic = italic
        r.font.name = MONO if mono else font
        if color is not None:
            r.font.color.rgb = color


def shade(cell, hexcolor):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hexcolor)
    tcPr.append(shd)


def split_row(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def convert(md_path: Path, out_path: Path, *, base_font=BODY, base_size=Pt(10.5),
            code_size=Pt(8.5), table_size=Pt(8.5)):
    text = md_path.read_text(encoding="utf-8")
    lines = text.split("\n")

    doc = Document()
    st = doc.styles["Normal"]
    st.font.name = base_font
    st.font.size = base_size
    sec = doc.sections[0]
    sec.left_margin = sec.right_margin = Cm(2.2)
    sec.top_margin = Cm(2.0)
    sec.bottom_margin = Cm(2.0)
    set_borders(doc)
    add_page_footer(sec)

    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        # fenced code
        if stripped.startswith("```"):
            lang = stripped[3:].strip()
            i += 1
            buf = []
            while i < n and not lines[i].strip().startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1
            p = doc.add_paragraph()
            pf = p.paragraph_format
            pf.left_indent = Cm(0.4)
            pf.space_before = Pt(4)
            pf.space_after = Pt(8)
            pf.line_spacing = 1.05
            r = p.add_run("\n".join(buf))
            r.font.name = MONO
            r.font.size = code_size
            continue

        # horizontal rule
        if stripped in ("---", "***", "___"):
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(8)
            pPr = p._p.get_or_add_pPr()
            pbdr = OxmlElement("w:pBdr")
            bot = OxmlElement("w:bottom")
            bot.set(qn("w:val"), "single")
            bot.set(qn("w:sz"), "6")
            bot.set(qn("w:color"), "BFBFBF")
            pbdr.append(bot)
            pPr.append(pbdr)
            i += 1
            continue

        # heading
        m = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if m:
            level = len(m.group(1))
            content = m.group(2).strip()
            sizes = {1: Pt(17), 2: Pt(14), 3: Pt(12), 4: Pt(11), 5: Pt(10.5),
                     6: Pt(10.5)}
            p = doc.add_paragraph()
            pf = p.paragraph_format
            pf.space_before = Pt(14 if level <= 2 else 10)
            pf.space_after = Pt(6)
            pf.keep_with_next = True
            add_inline(p, content, size=sizes.get(level, Pt(10.5)),
                       base_bold=True, color=BLACK)
            i += 1
            continue

        # table
        if stripped.startswith("|") and i + 1 < n and re.match(
                r"^\|[\s:\-|]+\|$", lines[i + 1].strip()):
            header = split_row(stripped)
            i += 2
            body_rows = []
            while i < n and lines[i].strip().startswith("|"):
                body_rows.append(split_row(lines[i].strip()))
                i += 1
            t = doc.add_table(rows=1, cols=len(header))
            t.style = "Table Grid"
            hdr = t.rows[0].cells
            for j, h in enumerate(header):
                hdr[j].text = ""
                p = hdr[j].paragraphs[0]
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.space_after = Pt(1)
                add_inline(p, h, size=table_size, base_bold=True,
                           color=RGBColor(0xFF, 0xFF, 0xFF))
                shade(hdr[j], "000000")
            for row in body_rows:
                cells = t.add_row().cells
                for j in range(len(header)):
                    val = row[j] if j < len(row) else ""
                    cells[j].text = ""
                    p = cells[j].paragraphs[0]
                    p.paragraph_format.space_after = Pt(1)
                    add_inline(p, val, size=table_size)
            doc.add_paragraph().paragraph_format.space_after = Pt(4)
            continue

        # image: ![caption](path)
        #
        # The figures are written as PDF so that the LaTeX path embeds them
        # as vectors. Word cannot embed a PDF, so the PNG sibling is used
        # instead; it is the same figure at the same size.
        m = re.match(r"^!\[(.*?)\]\(([^)]+)\)\s*$", stripped)
        if m:
            _alt, _src = m.group(1), m.group(2)
            _path = (Path(md_path).parent / _src)
            if _path.suffix.lower() == ".pdf":
                _png = _path.with_suffix(".png")
                if _png.exists():
                    _path = _png
            if _path.exists():
                p = doc.add_paragraph()
                p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.space_before = Pt(6)
                p.paragraph_format.space_after = Pt(2)
                p.add_run().add_picture(str(_path), width=Cm(8.0))
                if _alt:
                    cp = doc.add_paragraph()
                    cp.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    cp.paragraph_format.space_after = Pt(10)
                    add_inline(cp, _alt, size=Pt(9),
                               color=RGBColor(0x40, 0x40, 0x40))
            else:
                print(f"  [docx] missing figure: {_path}")
            i += 1
            continue

        # block quote
        if stripped.startswith(">"):
            content = stripped.lstrip(">").strip()
            p = doc.add_paragraph()
            pf = p.paragraph_format
            pf.left_indent = Cm(0.8)
            pf.space_after = Pt(6)
            pf.line_spacing = 1.3
            pPr = p._p.get_or_add_pPr()
            pbdr = OxmlElement("w:pBdr")
            left = OxmlElement("w:left")
            left.set(qn("w:val"), "single")
            left.set(qn("w:sz"), "18")
            left.set(qn("w:space"), "8")
            left.set(qn("w:color"), "6E6E6E")
            pbdr.append(left)
            pPr.append(pbdr)
            add_inline(p, content, size=Pt(10.5), color=RGBColor(0x40, 0x40, 0x40))
            i += 1
            continue

        # bullet list
        m = re.match(r"^(\s*)[-*+]\s+(.*)$", line)
        if m:
            indent = len(m.group(1)) // 2
            p = doc.add_paragraph()
            pf = p.paragraph_format
            pf.left_indent = Cm(0.7 + 0.6 * indent)
            pf.first_line_indent = Cm(-0.4)
            pf.space_after = Pt(4)
            pf.line_spacing = 1.35
            add_inline(p, "•  " + m.group(2).strip(), size=base_size)
            i += 1
            continue

        # numbered list
        m = re.match(r"^(\s*)(\d+)\.\s+(.*)$", line)
        if m:
            indent = len(m.group(1)) // 3
            p = doc.add_paragraph()
            pf = p.paragraph_format
            pf.left_indent = Cm(0.8 + 0.6 * indent)
            pf.first_line_indent = Cm(-0.6)
            pf.space_after = Pt(4)
            pf.line_spacing = 1.35
            add_inline(p, f"{m.group(2)}.  {m.group(3).strip()}", size=base_size)
            i += 1
            continue

        # paragraph (accumulate soft-wrapped lines)
        buf = [stripped]
        i += 1
        while i < n and lines[i].strip() and not re.match(
                r"^\s*(#{1,6}\s|[-*+]\s|\d+\.\s|\||>|```|---)", lines[i]):
            buf.append(lines[i].strip())
            i += 1
        joined = " ".join(buf)
        p = doc.add_paragraph()
        pf = p.paragraph_format
        pf.space_after = Pt(7)
        pf.line_spacing = 1.4
        pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        add_inline(p, joined, size=base_size)

    doc.save(out_path)
    # The document is monochrome: the theme it inherits from the
    # python-docx template carries the Office accent colours, and the
    # built-in heading styles reference them.
    _monochrome(out_path)
    print(f"[md2docx] {md_path.name} -> {out_path.name}")


if __name__ == "__main__":
    src = Path(sys.argv[1])
    dst = Path(sys.argv[2])
    convert(src, dst)
