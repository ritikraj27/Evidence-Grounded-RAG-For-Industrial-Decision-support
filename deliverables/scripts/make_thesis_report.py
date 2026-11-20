#!/usr/bin/env python3
"""Build the MTP project report.

A section-wise report for the M.Tech project, built from a pristine template
and a measured-value table, and rendered to a Word document in which every
formula is a real Word equation compiled from LaTeX.

The pipeline is:

    template  ->  token substitution  ->  Markdown  ->  pandoc  ->  DOCX
                                                                   |
                                            page furniture, tables, TOC
                                                                   |
                                                              monochrome
                                                                   |
                                                      soffice  ->  PDF  ->  page count

Why pandoc rather than python-docx: pandoc compiles LaTeX math into Office
Math Markup, so an equation written as `\\frac{1}{N}` is a Word equation the
reader can click and edit, not a picture of one. python-docx has no LaTeX
support at all, so a hand-built writer would have had to ship the formulas as
images, which is exactly what "every formula in LaTeX format" rules out.

The document is monochrome. See deliverables/scripts/monochrome.py.

Usage:
    python3 deliverables/scripts/make_thesis_report.py
"""
from __future__ import annotations


import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

for _cand in (Path(__file__).resolve().parent,
              Path(__file__).resolve().parents[2] / "scripts"):
    if (_cand / "monochrome.py").exists():
        sys.path.insert(0, str(_cand))
        break
from monochrome import to_monochrome as _monochrome

sys.path.insert(0, str(Path(__file__).resolve().parent))
from docx_settings import set_compatibility_mode

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[2]
DELIV = ROOT / "deliverables"
TEMPLATE = DELIV / "templates" / "MTP_Report.md"
MARKDOWN = DELIV / "MTP_Report.md"
DOCX = DELIV / "MTP_Report.docx"
PDF = DELIV / "MTP_Report.pdf"

BODY_FONT = "Times New Roman"
MONO_FONT = "Consolas"
BODY_SIZE = Pt(12)
HEAD_SIZE = Pt(14)
BLACK = RGBColor(0x00, 0x00, 0x00)
DARK = RGBColor(0x26, 0x26, 0x26)
GREY = RGBColor(0x59, 0x59, 0x59)

#: The report must be at least this long. The requirement is a floor, not a
#: target: a chapter-wise report with this much measured material should not
#: be short, and if it is, something was dropped.
MIN_PAGES = 20


# ----------------------------------------------------------------- tokens
def substitute(text: str) -> str:
    """Replace {{TOKEN}} with the measured value, and fail on anything left."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import substitute_tokens as st

    values = st.values()

    def resolved(name: str) -> bool:
        # A figure's number is read off the token's own name, so it needs no
        # measured value of its own.
        return (name in values
                or bool(re.fullmatch(r"FIG\d+_NUMBER", name)))

    missing = sorted({m for m in re.findall(r"\{\{([A-Z0-9_]+)\}\}", text)
                      if not resolved(m)})
    if missing:
        raise SystemExit(f"[report] no measured value for: {missing}")

    def repl(m):
        name = m.group(1)
        if name not in values:
            num = re.fullmatch(r"FIG(\d+)_NUMBER", name)
            if not num:
                raise SystemExit(f"[report] no measured value for: {name}")
            return num.group(1)
        val = str(values[name])
        # A figure caption carries its own number, and the number comes from
        # the token's own name, so it cannot drift from the file it names.
        # The caption body is the rest of the text, and the label is put
        # back in front of it by the caller.
        if name.startswith("FIG") and name.endswith("_CAPTION"):
            return re.sub(r"^Figure\s+\d+\.\s*", "", val)
        if name.startswith("FIG") and name.endswith("_NUMBER"):
            m = re.match(r"FIG(\d+)_NUMBER", name)
            if m:
                return m.group(1)
        return val

    out = re.sub(r"\{\{([A-Z0-9_]+)\}\}", repl, text)
    out = re.sub(r"\*\*Figure\s+(\d+)\.\*\*",
                 lambda m: f"**Figure {m.group(1)}.**", out)
    # The figures are numbered in the order they appear in the report. The
    # figure script numbers them by the experiment that produced them, and
    # those two orders are not the same, so a caption that kept the script's
    # number would read "Figure 4" and then "Figure 1" on the next page.
    counter = [0]

    def renumber(m):
        counter[0] += 1
        return f"**Figure {counter[0]}.**"

    out = re.sub(r"\*\*Figure\s+\d+\.\*\*", renumber, out)
    leftover = re.findall(r"\{\{[^}]*\}\}", out)
    if leftover:
        raise SystemExit(f"[report] unsubstituted placeholders: {leftover[:5]}")
    return out


# ----------------------------------------------------------------- docx furniture
def _style(doc, name, *, size=None, bold=None, color=None, space_before=None,
           space_after=None, align=None, keep_next=None, italic=None):
    try:
        st = doc.styles[name]
    except KeyError:
        return
    f = st.font
    f.name = BODY_FONT
    if size is not None:
        f.size = size
    if bold is not None:
        f.bold = bold
    if italic is not None:
        f.italic = italic
    if color is not None:
        f.color.rgb = color
    pf = st.paragraph_format
    if space_before is not None:
        pf.space_before = space_before
    if space_after is not None:
        pf.space_after = space_after
    if align is not None:
        pf.alignment = align
    if keep_next is not None:
        pf.keep_with_next = keep_next


def build_reference_docx(dest: Path) -> None:
    """A styled pandoc reference document: Times New Roman, A4, greyscale."""
    raw = subprocess.run(["pandoc", "--print-default-data-file", "reference.docx"],
                         capture_output=True, check=True).stdout
    tmp = dest.with_suffix(".raw.docx")
    tmp.write_bytes(raw)

    doc = Document(str(tmp))
    for section in doc.sections:
        section.page_width = Cm(21.0)
        section.page_height = Cm(29.7)
        section.left_margin = section.right_margin = Cm(2.6)
        section.top_margin = Cm(2.4)
        section.bottom_margin = Cm(2.2)

    _style(doc, "Normal", size=BODY_SIZE, color=BLACK)
    _style(doc, "Body Text", size=BODY_SIZE, color=BLACK,
           align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=Pt(6))
    _style(doc, "First Paragraph", size=BODY_SIZE, color=BLACK,
           align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=Pt(6))
    _style(doc, "Compact", size=Pt(11), color=BLACK, space_after=Pt(4))
    _style(doc, "Title", size=Pt(16), bold=True, color=BLACK,
           align=WD_ALIGN_PARAGRAPH.CENTER, space_after=Pt(10))
    _style(doc, "Subtitle", size=Pt(14), bold=False, italic=True, color=DARK,
           align=WD_ALIGN_PARAGRAPH.CENTER, space_after=Pt(14))
    _style(doc, "Author", size=Pt(12), color=DARK,
           align=WD_ALIGN_PARAGRAPH.CENTER, space_after=Pt(4))
    _style(doc, "Date", size=Pt(12), color=GREY,
           align=WD_ALIGN_PARAGRAPH.CENTER, space_after=Pt(4))
    # The headings are set at 14 and the body at 12, which is the size the
    # department asked for. The chapter and the section under it are the same
    # size on purpose: what separates them is the numbering ("Chapter 5:" and
    # "5.1"), the page break, and the fact that only the chapter carries the
    # reader's eye in the contents list.
    _style(doc, "Heading 1", size=HEAD_SIZE, bold=True, color=BLACK,
           space_before=Pt(18), space_after=Pt(8), keep_next=True)
    _style(doc, "Heading 2", size=HEAD_SIZE, bold=True, color=DARK,
           space_before=Pt(13), space_after=Pt(6), keep_next=True)
    _style(doc, "Heading 3", size=BODY_SIZE, bold=True, color=DARK,
           space_before=Pt(10), space_after=Pt(5), keep_next=True)
    _style(doc, "Heading 4", size=Pt(11), bold=True, italic=True, color=GREY,
           space_before=Pt(9), space_after=Pt(4), keep_next=True)
    _style(doc, "Table Caption", size=Pt(11), bold=True, color=BLACK,
           space_before=Pt(10), space_after=Pt(3))
    _style(doc, "Image Caption", size=Pt(10.5), italic=True, color=GREY,
           align=WD_ALIGN_PARAGRAPH.CENTER, space_after=Pt(12))
    _style(doc, "Source Code", size=Pt(9), color=BLACK)
    _style(doc, "Block Text", size=Pt(11), italic=True, color=DARK,
           align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    _style(doc, "Abstract", size=BODY_SIZE, color=BLACK,
           align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=Pt(6))

    # The contents list. Word has built-in styles for these and will use
    # them when the field is refreshed; defining them here means the list
    # is right in the file as shipped, before anybody refreshes anything.
    for level, indent in ((1, 0.0), (2, 0.55), (3, 1.1)):
        st = doc.styles.add_style(f"TOC {level}", WD_STYLE_TYPE.PARAGRAPH)
        st.base_style = doc.styles["Normal"]
        st.font.name = BODY_FONT
        st.font.size = BODY_SIZE
        st.font.bold = (level == 1)
        pf = st.paragraph_format
        pf.left_indent = Cm(indent)
        pf.space_before = Pt(0)
        pf.space_after = Pt(3)

    # The document's default font, for any run that does not name one.
    doc.styles.element.find(qn("w:docDefaults")).find(qn("w:rPrDefault")).find(
        qn("w:rPr")).append(_rfonts(BODY_FONT))

    doc.save(str(dest))
    _name_toc_styles_built_in(dest)
    tmp.unlink(missing_ok=True)


def _name_toc_styles_built_in(path: Path) -> None:
    """Give the contents styles Word's own names.

    A style whose identifier is TOC1 but whose name is "TOC 1" is a
    different style from Word's built-in "toc 1", and Word's contents
    update hangs on the mismatch. The identifier has to stay TOC1, because
    that is what the field's paragraphs refer to.
    """
    import zipfile

    tmp = path.with_suffix(".styles.docx")
    with zipfile.ZipFile(path) as zin, \
            zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "word/styles.xml":
                xml = data.decode("utf-8")
                for n in (1, 2, 3):
                    xml = xml.replace(f'<w:name w:val="TOC {n}"/>',
                                      f'<w:name w:val="toc {n}"/>')
                data = xml.encode("utf-8")
            zout.writestr(item, data)
    tmp.replace(path)


def _rfonts(name: str) -> OxmlElement:
    el = OxmlElement("w:rFonts")
    for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        el.set(qn(attr), name)
    return el


def set_page_borders(doc) -> None:
    """A thin rectangular border on every page, as the department template has."""
    for section in doc.sections:
        sectPr = section._sectPr
        pgBorders = OxmlElement("w:pgBorders")
        pgBorders.set(qn("w:offsetFrom"), "page")
        for edge in ("top", "left", "bottom", "right"):
            el = OxmlElement(f"w:{edge}")
            el.set(qn("w:val"), "single")
            el.set(qn("w:sz"), "6")
            el.set(qn("w:space"), "20")
            el.set(qn("w:color"), "000000")
            pgBorders.append(el)
        ref = sectPr.find(qn("w:pgMar"))
        (ref.addnext(pgBorders) if ref is not None else sectPr.append(pgBorders))


def add_page_footer(doc) -> None:
    for section in doc.sections:
        # The title page carries no number, the way the reference has it.
        section.different_first_page_header_footer = True
        first = section.first_page_footer
        if not first.paragraphs:
            first.add_paragraph()
        p = section.footer.paragraphs[0]
        # Bottom right, the way the reference has it.
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        run = p.add_run()
        fld = OxmlElement("w:fldSimple")
        fld.set(qn("w:instr"), " PAGE ")
        run._r.addnext(fld)
        for r in p.runs:
            r.font.size = Pt(9)
            r.font.name = BODY_FONT
            r.font.color.rgb = GREY


def shade(cell, hexcolor: str) -> None:
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hexcolor)
    tcPr.append(shd)


def style_tables(doc) -> None:
    """A filled header row and hairline rules: legible in mono print."""
    for t in doc.tables:
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        if not t.rows:
            continue
        for j, cell in enumerate(t.rows[0].cells):
            shade(cell, "000000")
            for p in cell.paragraphs:
                p.paragraph_format.space_before = Pt(2)
                p.paragraph_format.space_after = Pt(2)
                for r in p.runs:
                    r.font.size = Pt(11)
                    r.font.bold = True
                    r.font.name = BODY_FONT
                    r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        for row in t.rows[1:]:
            for cell in row.cells:
                for p in cell.paragraphs:
                    p.paragraph_format.space_before = Pt(1)
                    p.paragraph_format.space_after = Pt(1)
                    for r in p.runs:
                        r.font.size = Pt(11)
                        r.font.name = BODY_FONT
                        r.font.color.rgb = BLACK


def chapter_page_breaks(doc) -> None:
    """Every chapter starts on a fresh page.

    The report is read in sections, and a chapter that starts halfway down a
    page reads as a continuation of the previous one. The abstract gets one
    too, so it starts after the contents list rather than running into it.
    """
    for p in doc.paragraphs:
        if p.style.name not in ("Heading 1", "heading 1"):
            continue
        p.paragraph_format.page_break_before = True
        p.paragraph_format.keep_with_next = True


def contents_page_break(doc) -> bool:
    """The contents list starts on the page after the title block.

    Pandoc writes the contents as a structured document tag, so the heading
    inside it is not among the document's paragraphs and has to be reached
    through the XML.
    """
    from docx.text.paragraph import Paragraph

    body = doc.element.body
    for sdt in body.findall(qn("w:sdt")):
        for p_el in sdt.iter(qn("w:p")):
            p = Paragraph(p_el, doc)
            name = (p.style.name or "").lower().replace(" ", "")
            if name.startswith("toc"):
                p.paragraph_format.page_break_before = True
                return True
    return False


def style_figure_captions(doc) -> None:
    """The caption under each figure: smaller, italic, centred.

    The caption is the sentence a reader reads to understand the picture
    without the picture, so it is set the way a caption is set rather than
    the way a paragraph is.
    """
    for p in doc.paragraphs:
        if not re.match(r"^Figure\s+\d+\.", p.text.strip()):
            continue
        pf = p.paragraph_format
        pf.alignment = WD_ALIGN_PARAGRAPH.CENTER
        pf.space_before = Pt(4)
        pf.space_after = Pt(14)
        pf.keep_with_next = False
        for r in p.runs:
            r.font.size = Pt(10.5)
            r.font.name = BODY_FONT
            r.font.color.rgb = GREY
            if r.text.startswith("Figure"):
                r.font.bold = True
                r.font.color.rgb = BLACK
            else:
                r.font.italic = True


def style_references(doc) -> None:
    """A hanging indent on the reference list, as APA requires."""
    in_refs = False
    for p in doc.paragraphs:
        text = p.text.strip()
        if not text:
            continue
        if text == "References":
            in_refs = True
            continue
        if in_refs:
            pf = p.paragraph_format
            pf.left_indent = Cm(1.0)
            pf.first_line_indent = Cm(-1.0)
            pf.space_after = Pt(7)
            pf.alignment = WD_ALIGN_PARAGRAPH.LEFT
            for r in p.runs:
                r.font.size = Pt(12)
                r.font.name = BODY_FONT
                r.font.color.rgb = BLACK


#: The Office Math namespace, which python-docx does not know about.
MATH_NS = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"


def _insert_ordered(parent, element, after: tuple[str, ...]) -> None:
    """Put `element` into `parent` before the first child that must follow it.

    WordprocessingML elements have a fixed order inside their parent, and a
    consumer ignores one that is out of place. `after` lists the tags that
    have to come after the element being inserted.
    """
    for child in parent:
        if child.tag in after:
            child.addprevious(element)
            return
    parent.append(element)


def clear_equation_borders(doc) -> int:
    """State, on the equation itself, that no rule may touch it.

    A display equation is a paragraph and an inline formula is a run, so
    whatever border a style hands them is drawn around them, and a formula
    then reads as a boxed label rather than as part of the line. The document
    defines no such border, but saying so explicitly costs nothing and leaves
    no room for one to arrive from a style, a template or a consumer that
    supplies its own: every paragraph holding a formula gets a border of
    "nil" on all four sides, and every run inside a formula gets a character
    border of "nil". Direct formatting beats a style, so nothing can inherit
    a rule past this.
    """
    nil_borders = ("w:top", "w:left", "w:bottom", "w:right")
    after_p = ("w:shd", "w:tabs", "w:suppressAutoHyphens", "w:kinsoku",
               "w:wordWrap", "w:overflowPunct", "w:topLinePunct",
               "w:autoSpaceDE", "w:autoSpaceDN", "w:bidi", "w:adjustRightInd",
               "w:snapToGrid", "w:spacing", "w:ind", "w:contextualSpacing",
               "w:mirrorIndents", "w:suppressOverlap", "w:jc", "w:textDirection",
               "w:textAlignment", "w:textboxTightWrap", "w:outlineLvl",
               "w:divId", "w:cnfStyle", "w:rPr", "w:sectPr", "w:pPrChange")
    after_r = ("w:shd", "w:fitText", "w:vertAlign", "w:rtl", "w:cs", "w:em",
               "w:lang", "w:eastAsianLayout", "w:specVanish", "w:oMath")

    touched = 0
    for p in doc.element.body.iter(qn("w:p")):
        if not (p.findall(f".//{MATH_NS}oMath")
                or p.findall(f".//{MATH_NS}oMathPara")):
            continue
        touched += 1

        pPr = p.find(qn("w:pPr"))
        if pPr is None:
            pPr = OxmlElement("w:pPr")
            p.insert(0, pPr)
        old = pPr.find(qn("w:pBdr"))
        if old is not None:
            pPr.remove(old)
        pBdr = OxmlElement("w:pBdr")
        for side in nil_borders:
            el = OxmlElement(side)
            el.set(qn("w:val"), "nil")
            el.set(qn("w:sz"), "0")
            el.set(qn("w:space"), "0")
            el.set(qn("w:color"), "auto")
            pBdr.append(el)
        _insert_ordered(pPr, pBdr, tuple(qn(t) for t in after_p))

        for mr in p.iter(f"{MATH_NS}r"):
            rPr = mr.find(qn("w:rPr"))
            if rPr is None:
                rPr = OxmlElement("w:rPr")
                math_rpr = mr.find(f"{MATH_NS}rPr")
                if math_rpr is not None:
                    math_rpr.addnext(rPr)
                else:
                    mr.insert(0, rPr)
            if rPr.find(qn("w:bdr")) is not None:
                continue
            bdr = OxmlElement("w:bdr")
            bdr.set(qn("w:val"), "nil")
            bdr.set(qn("w:sz"), "0")
            bdr.set(qn("w:space"), "0")
            bdr.set(qn("w:color"), "auto")
            _insert_ordered(rPr, bdr, tuple(qn(t) for t in after_r))
    return touched


def set_update_fields(path: Path) -> None:
    """Ask Word and LibreOffice to populate the table of contents on open."""
    import zipfile

    tmp = path.with_suffix(".fields.docx")
    with zipfile.ZipFile(path) as zin, \
            zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "word/settings.xml":
                xml = data.decode("utf-8")
                if "w:updateFields" not in xml:
                    xml = xml.replace(
                        "<w:settings ", "<w:settings ", 1)
                    # Insert immediately after the opening tag.
                    idx = xml.find(">", xml.find("<w:settings"))
                    xml = (xml[:idx + 1]
                           + '<w:updateFields w:val="true"/>'
                           + xml[idx + 1:])
                data = xml.encode("utf-8")
            zout.writestr(item, data)
    tmp.replace(path)



# ---------------------------------------------------------------- front matter
#: The institute's emblem, copied into the project so the build does not
#: depend on a file in the reader's downloads folder.
LOGO = ROOT / "deliverables" / "assets" / "iitkgp_emblem.png"

#: The report's own title, as it appears on the title page and in the
#: certificate's certification paragraph.
REPORT_TITLE = ("An Evidence-Grounded Retrieval-Augmented Generation Framework "
                "for Industrial Decision Support")


def drop_title_block(doc) -> int:
    """Remove the title block pandoc writes from the metadata.

    The title page is built by hand, to the department's template, and the
    two together would print the title twice.
    """
    dropped = 0
    for p in list(doc.paragraphs):
        if p.style.name in ("Title", "Subtitle", "Author", "Date"):
            p._p.getparent().remove(p._p)
            dropped += 1
    return dropped


def front_matter(doc) -> int:
    """The title page and the certificate page, in the department's template.

    The reference is the report the department circulated earlier. These two
    pages follow it: a bordered title page with the title in capitals, the
    emblem, the author and supervisor blocks and the institution block; then
    a certificate page with the departmental letterhead, the certification
    paragraph and the signature block.

    They are built at the end of the document and then moved to the front.
    python-docx can add a picture anywhere in a document but cannot insert a
    paragraph at the beginning of the body without hand-editing the XML, and
    moving an element that already exists is safe: the picture's relationship
    travels with it.
    """
    made: list = []

    def para(text="", *, size=12, bold=False, italic=False, align=None,
             space_after=0, space_before=0, line=1.0, indent=None):
        p = doc.add_paragraph()
        pf = p.paragraph_format
        pf.space_after = Pt(space_after)
        pf.space_before = Pt(space_before)
        pf.line_spacing = line
        if align is not None:
            p.alignment = align
        if indent is not None:
            pf.left_indent = Cm(indent)
        if text:
            r = p.add_run(text)
            r.font.name = BODY_FONT
            r.font.size = Pt(size)
            r.font.bold = bold
            r.font.italic = italic
            r.font.color.rgb = BLACK
        made.append(p._p)
        return p

    def picture(path: Path, width_cm: float, *, align=WD_ALIGN_PARAGRAPH.CENTER):
        p = doc.add_paragraph()
        p.alignment = align
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.space_before = Pt(0)
        p.add_run().add_picture(str(path), width=Cm(width_cm))
        made.append(p._p)
        return p

    def page_break():
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run()
        r.add_break(WD_BREAK.PAGE)
        made.append(p._p)
        return p

    C = WD_ALIGN_PARAGRAPH.CENTER
    J = WD_ALIGN_PARAGRAPH.JUSTIFY

    # ------------------------------------------------------------ TITLE PAGE
    para("AN EVIDENCE-GROUNDED", size=20, bold=True, align=C, line=1.15,
         space_before=24)
    para("RETRIEVAL-AUGMENTED GENERATION", size=18, bold=True, align=C, line=1.15,
         space_after=4)
    para("FRAMEWORK", size=18, bold=True, align=C, line=1.15, space_after=4)
    para("FOR INDUSTRIAL DECISION SUPPORT", size=16, bold=True, align=C, line=1.15,
         space_after=20)
    para("M.Tech Project Report", size=14, italic=True, align=C, space_after=30)
    if LOGO.exists():
        picture(LOGO, 5.66)
    para("", space_after=100)
    para("By", size=13, align=C, space_after=6)
    para("Ritik Raj [25IM60R12]", size=15, bold=True, align=C, space_after=14)
    para("Under the supervision of", size=13, align=C, space_after=6)
    para("Dr. Sri Krishna Kumar", size=14, bold=True, align=C, space_after=26)
    para("INDIAN INSTITUTE OF TECHNOLOGY KHARAGPUR)", size=12, bold=True,
         align=C, line=1.15, space_after=2)
    for line_ in ("DEPARTMENT OF INDUSTRIAL AND SYSTEMS ENGINEERING",
                  "INDIAN INSTITUTE OF TECHNOLOGY, KHARAGPUR"):
        para(line_, size=12, bold=True, align=C, line=1.15, space_after=2)
    para("KHARAGPUR- 721302, INDIA", size=12, align=C, line=1.15, space_after=10)
    para("NOVEMBER, 2026", size=12, bold=True, align=C, space_after=0)
    page_break()

    # ------------------------------------------------------ CERTIFICATE PAGE
    # The letterhead: the emblem on the left, the department's address on
    # the right, the way the reference sets it.
    table = doc.add_table(rows=1, cols=2)
    made.append(table._tbl)
    table.autofit = False
    # The table's properties have to be in the order the schema wants. Word
    # ignores a property that is out of place, and a table that keeps its
    # default style draws borders that the reference does not have.
    tblPr = table._tbl.tblPr
    for child in list(tblPr):
        tblPr.remove(child)
    el = OxmlElement("w:tblW")
    el.set(qn("w:w"), str(int(14.6 * 567)))
    el.set(qn("w:type"), "dxa")
    tblPr.append(el)
    el = OxmlElement("w:tblInd")
    el.set(qn("w:w"), str(int(-0.78 * 567)))
    el.set(qn("w:type"), "dxa")
    tblPr.append(el)
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        b_ = OxmlElement(f"w:{edge}")
        b_.set(qn("w:val"), "nil")
        borders.append(b_)
    tblPr.append(borders)
    el = OxmlElement("w:tblLayout")
    el.set(qn("w:type"), "fixed")
    tblPr.append(el)
    # The default table style draws a rule under the first row. The letterhead
    # wants one rule, in one place, so the conditional formatting is switched
    # off here and the rule is drawn deliberately further down.
    el = OxmlElement("w:tblLook")
    for k, v in (("w:val", "0000"), ("w:firstRow", "0"), ("w:lastRow", "0"),
                 ("w:firstColumn", "0"), ("w:lastColumn", "0"),
                 ("w:noHBand", "1"), ("w:noVBand", "1")):
        el.set(qn(k), v)
    tblPr.append(el)
    table.columns[0].width = Cm(2.4)
    table.columns[1].width = Cm(12.2)
    left, right = table.rows[0].cells
    for cell, width_cm in ((left, 2.4), (right, 12.2)):
        tcPr = cell._tc.get_or_add_tcPr()
        tcW = tcPr.find(qn("w:tcW"))
        if tcW is None:
            tcW = OxmlElement("w:tcW")
            tcPr.append(tcW)
        tcW.set(qn("w:w"), str(int(width_cm * 567)))
        tcW.set(qn("w:type"), "dxa")
        cell.margin_left = Cm(0)
        cell.margin_right = Cm(0)
        cell.margin_top = Cm(0)
        cell.margin_bottom = Cm(0)
    lp = left.paragraphs[0]
    lp.alignment = WD_ALIGN_PARAGRAPH.LEFT
    lp.paragraph_format.space_after = Pt(0)
    if LOGO.exists():
        lp.add_run().add_picture(str(LOGO), width=Cm(1.81))
    for i, line_ in enumerate(("DEPARTMENT OF INDUSTRIAL AND SYSTEMS ENGINEERING",
                                "INDIAN INSTITUTE OF TECHLOGY KHARAGPUR,",
                                "KHARAGPUR, INDIA-721302")):
        rp = right.paragraphs[0] if i == 0 else right.add_paragraph()
        rp.paragraph_format.space_after = Pt(2)
        rp.paragraph_format.line_spacing = 1.15
        rr = rp.add_run(line_)
        rr.font.name = BODY_FONT
        rr.font.size = Pt(11)
        rr.font.bold = True
        rr.font.color.rgb = BLACK

    # The rule under the letterhead.
    rule = doc.add_paragraph()
    rule.paragraph_format.space_before = Pt(14)
    rule.paragraph_format.space_after = Pt(0)
    pPr = rule._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    bot = OxmlElement("w:bottom")
    bot.set(qn("w:val"), "single")
    bot.set(qn("w:sz"), "6")
    bot.set(qn("w:space"), "1")
    bot.set(qn("w:color"), "000000")
    pBdr.append(bot)
    pPr.append(pBdr)
    made.append(rule._p)

    para("CERTIFICATE", size=18, bold=True, align=C, space_before=66,
         space_after=72)
    para(f"This is to certify that this report entitled {REPORT_TITLE} submitted "
         "by Ritik Raj [25IM60R12] to the Indian Institute of Technology Kharagpur "
         "is a record of the bona fide project work carried out under my "
         "supervision and is worthy of consideration for the MTP Project. This "
         "project has fulfilled all the requirements as per the regulations of "
         "the Institute and has reached the standard needed for the submission.",
         size=12, align=J, line=1.72, space_after=0)
    para("", space_after=150)
    para("Dr. Sri Krishna Kumar", size=10.6, bold=True, space_after=11)
    for line_ in ("Department of Industrial and Systems Engineering",
                  "Indian Institute of Technology Kharagpur",
                  "India-721302",
                  "Date: 18-11-2026"):
        para(line_, size=10.6, space_after=11, line=1.15)

    # ------------------------------------------------- move them to the front
    body = doc.element.body
    anchor = body[0]
    for el in made:
        body.remove(el)
    for el in made:
        anchor.addprevious(el)
    return len(made)

# ---------------------------------------------------------------- contents
#: The contents list is written into the document rather than left to Word.
#:
#: Pandoc writes the table-of-contents field with an empty result, so the
#: document opens with a blank box where the contents should be. Asking Word
#: to fill it in is not an option here: the field is refreshed before Word
#: has laid the document out, and the result is a page number of 1 on every
#: line.
#:
#: So the entries are written in as the field's cached result. The field is
#: kept, which means a reader who wants Word's own page numbers can select
#: the list and press F9, and Word computes them exactly. What is written
#: here is the structure, which is the part that cannot be wrong.
def _toc_sdt_content(entries) -> str:
    """The contents as the cached result of the table-of-contents field."""
    from xml.sax.saxutils import escape

    # The right tab stop, at the edge of the text column, with dot leaders.
    tab = '<w:tabs><w:tab w:val="right" w:leader="dot" w:pos="8957"/></w:tabs>'
    out = ['<w:p><w:pPr><w:pStyle w:val="TOCHeading"/><w:pageBreakBefore/></w:pPr>'
           '<w:r><w:t xml:space="preserve">Table of Contents</w:t></w:r></w:p>'
           '<w:p><w:pPr><w:spacing w:after="120"/>'
           '<w:rPr><w:i/><w:sz w:val="19"/><w:szCs w:val="19"/>'
           '<w:color w:val="595959"/></w:rPr></w:pPr>'
           '<w:r><w:rPr><w:i/><w:sz w:val="19"/><w:szCs w:val="19"/>'
           '<w:color w:val="595959"/></w:rPr><w:t xml:space="preserve">'
           'Every heading in the report, with the page it starts on.'
           '</w:t></w:r></w:p>']
    for i, (level, title) in enumerate(entries):
        runs = []
        if i == 0:
            runs.append('<w:r><w:fldChar w:fldCharType="begin"/></w:r>')
            runs.append('<w:r><w:instrText xml:space="preserve">TOC \\o "1-3" '
                        '\\h \\z \\u</w:instrText></w:r>')
            runs.append('<w:r><w:fldChar w:fldCharType="separate"/></w:r>')
        runs.append('<w:r><w:t xml:space="preserve">' + escape(title) + '</w:t></w:r>')
        runs.append("<w:r><w:tab/></w:r>")
        if i == len(entries) - 1:
            runs.append('<w:r><w:fldChar w:fldCharType="end"/></w:r>')
        out.append('<w:p><w:pPr><w:pStyle w:val="TOC' + str(level) + '"/>' + tab
                   + '</w:pPr>' + "".join(runs) + '</w:p>')
    return "".join(out)


def write_toc(docx: Path, entries) -> None:
    """Write the contents into the document.

    Two settings are removed while the document is written. `w:updateFields`
    tells Word to refresh every field when the document is opened, and
    `w:dirty` on the field asks for the same thing. Word does that before it
    has laid the document out, so a contents list refreshed that way comes
    out with a page number of 1 on every line. Removing both leaves the
    written list alone, and leaves the field ready for a reader to refresh by
    hand.
    """
    import zipfile

    tmp = docx.with_suffix(".toc.docx")
    with zipfile.ZipFile(docx) as zin, \
            zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "word/document.xml":
                xml = data.decode("utf-8")
                i = xml.find("<w:sdtContent>")
                j = xml.find("</w:sdtContent>")
                if i < 0 or j < 0:
                    raise SystemExit("[report] no table of contents found")
                xml = (xml[:i] + "<w:sdtContent>"
                       + _toc_sdt_content(entries)
                       + "</w:sdtContent>"
                       + xml[j + len("</w:sdtContent>"):])
                data = xml.encode("utf-8")
            elif item.filename == "word/settings.xml":
                xml = data.decode("utf-8")
                xml = re.sub(r"<w:updateFields[^/]*/>", "", xml)
                data = xml.encode("utf-8")
            zout.writestr(item, data)
    tmp.replace(docx)


def finalise_settings(docx: Path) -> None:
    """Stop Word refreshing the contents when the document is opened.

    `w:dirty` on the field asks for the same refresh, and the two settings
    together are what turn a correct contents list into a column of ones.
    """
    import zipfile

    tmp = docx.with_suffix(".fields.docx")
    with zipfile.ZipFile(docx) as zin, \
            zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "word/document.xml":
                data = data.decode("utf-8").replace(' w:dirty="true"', "") \
                    .encode("utf-8")
            elif item.filename == "word/settings.xml":
                xml = data.decode("utf-8")
                xml = re.sub(r"<w:updateFields[^/]*/>", "", xml)
                data = xml.encode("utf-8")
            zout.writestr(item, data)
    tmp.replace(docx)

    set_compatibility_mode(docx)


# ----------------------------------------------------------------- verification
def pdf_pages(markdown: Path) -> int:
    """The page count of the report's reading copy.

    The reading copy is rendered from the report's own Markdown through the
    project's pipeline -- pandoc to LaTeX, the project's greyscale template to
    lay it out, tectonic to compile it -- which is how the other PDFs in this
    project are made. Its geometry is A4 at 11pt with 2.4cm margins, within a
    few millimetres of the DOCX's own page setup, so its pagination is a
    faithful measure of the report's length. (LibreOffice is not installed on
    this machine and Word's AppleScript `save as` does not answer to
    automation, so neither can render the DOCX itself.)
    """
    script = Path(__file__).resolve().parent / "make_pdf.py"
    if not script.exists():
        return -1
    # The old PDF goes first. If the render fails, the absence of a new file is
    # the signal; a stale file would otherwise be counted as this build's
    # output, which is how a stale reading copy once hid a broken render.
    PDF.unlink(missing_ok=True)
    r = subprocess.run(
        [sys.executable, str(script), str(markdown), str(PDF), "--toc",
         "--strip-front-matter",
         # The same two typography choices the DOCX makes: Times for the text
         # and the maths, and the contents list on a page of its own after the
         # title block.
         "--variable=timesfont=true",
         "--variable=bodypt12=true",
         "--variable=toc-on-own-page=true",
         # The title page and the certificate page, in the department's
         # template, the same two pages the Word file carries.
         "--variable=frontmatter=true",
         "--variable=deptfurniture=true",
         "--metadata", "title=An Evidence-Grounded Retrieval-Augmented "
                       "Generation Framework for Industrial Decision Support",
         "--metadata", "subtitle=Architecture, Evaluation Protocol, "
                       "Failure-Mode Characterisation, and Measured Findings",
         "--metadata", "author=Ritik Raj (25IM60R12), Supervisor: "
                       "Dr. Sri Krishna Kumar, Department of Industrial and "
                       "Systems Engineering, IIT Kharagpur",
         ],
        capture_output=True, text=True)
    if not PDF.exists():
        print(f"  -- reading copy not rendered: "
              f"{(r.stdout or r.stderr or '').strip()[:300]}")
        return -1
    try:
        import pypdf
        return len(pypdf.PdfReader(str(PDF)).pages)
    except Exception:
        return -1


def count_equations(docx: Path) -> int:
    import zipfile
    with zipfile.ZipFile(docx) as z:
        xml = z.read("word/document.xml").decode("utf-8")
    return xml.count("<m:oMath")


def count_non_grey(docx: Path) -> int:
    """Every literal colour in the file, read back out of the saved document."""
    import zipfile
    bad = 0
    with zipfile.ZipFile(docx) as z:
        for name in z.namelist():
            if not name.endswith(".xml"):
                continue
            xml = z.read(name).decode("utf-8", "ignore")
            for m in re.finditer(r'srgbClr val="([0-9A-Fa-f]{6})"', xml):
                h = m.group(1)
                if not (h[0:2] == h[2:4] == h[4:6]):
                    bad += 1
            for m in re.finditer(r'<w:color[^>]*w:val="([0-9A-Fa-f]{6})"', xml):
                h = m.group(1)
                if not (h[0:2] == h[2:4] == h[4:6]):
                    bad += 1
    return bad


def check_citations(markdown: str) -> list[str]:
    """Every reference in the list must be cited in the text, and vice versa.

    APA requires both directions, and both are easy to break by editing one
    side of the document. A reference nobody cites is dead weight; a citation
    with no reference is a dangling name, which is what a reviewer notices
    first.
    """
    if "# References" not in markdown:
        return ["the report has no references section"]
    body, refs = markdown.split("# References", 1)
    entries = [p.strip() for p in refs.strip().split("\n\n") if p.strip()]
    problems: list[str] = []

    for e in entries:
        m = re.match(r"([A-Z][A-Za-zÀ-ɏ'’\-]+)", e)
        ym = re.search(r"\((\d{4})\)", e)
        if not m or not ym:
            problems.append(f"unparseable reference entry: {e[:60]!r}")
            continue
        s, y = m.group(1), ym.group(1)
        # APA has two shapes: "Surname (year)" / "Surname et al. (year)", and
        # the narrative form inside a bracket, "Surname et al., year".
        authors = (rf"(?:et\s+al\.|&\s*[A-Z][A-Za-z\-]+|and\s+[A-Z][A-Za-z\-]+)?")
        forms = [
            rf"\b{re.escape(s)}\s*{authors}\s*\(\s*{y}\s*\)",
            rf"\b{re.escape(s)}\s+{authors.strip('?')}\s*,\s*{y}\b",
        ]
        if not any(re.search(p, body) for p in forms):
            problems.append(f"reference not cited in the text: {s} ({y})")

    # The reverse direction: a year that appears in the text with a name but
    # has no entry in the list.
    listed = set()
    for e in entries:
        m = re.match(r"([A-Z][A-Za-zÀ-ɏ'’\-]+)", e)
        ym = re.search(r"\((\d{4})\)", e)
        if m and ym:
            listed.add((m.group(1), ym.group(1)))
    for m in re.finditer(
            r"\b([A-Z][A-Za-zÀ-ɏ'’\-]+)(?:\s+et al\.|\s+&\s+[A-Z][A-Za-z\-]+|"
            r"\s+and\s+[A-Z][A-Za-z\-]+)?\s*\((\d{4})\)", body):
        pair = (m.group(1), m.group(2))
        if pair not in listed and m.group(1) not in {"Chapter", "Table", "Figure"}:
            problems.append(f"cited in the text but not in the list: "
                            f"{pair[0]} ({pair[1]})")
    return problems


def main() -> int:
    if not TEMPLATE.exists():
        print(f"  x template missing: {TEMPLATE}")
        return 1
    if not shutil.which("pandoc"):
        print("  x pandoc not on PATH: the LaTeX equations need it")
        return 1

    text = TEMPLATE.read_text(encoding="utf-8")
    body = substitute(text)
    MARKDOWN.write_text(body, encoding="utf-8")
    n_tokens = len(re.findall(r"\{\{[A-Z0-9_]+\}\}", text))
    print(f"[report] substituted {n_tokens} measured values "
          f"-> {MARKDOWN.name} ({len(body):,} chars)")

    with tempfile.TemporaryDirectory(prefix="mtp-report-") as tmp:
        tmpdir = Path(tmp)
        ref = tmpdir / "reference.docx"
        build_reference_docx(ref)

        subprocess.run(
            ["pandoc", str(MARKDOWN),
             "-o", str(DOCX),
             "--reference-doc", str(ref),
             "--toc", "--toc-depth=3",
             "--from", "markdown+tex_math_dollars+pipe_tables",
             "--standalone",
             # The figures live beside the markdown, not in the directory
             # pandoc is run from.
             "--resource-path", str(DELIV),
             "--metadata", "lang=en-GB"],
            check=True, capture_output=True)

    doc = Document(str(DOCX))
    set_page_borders(doc)
    add_page_footer(doc)
    if not contents_page_break(doc):
        print("  x the contents list was not found in the document")
        return 1
    chapter_page_breaks(doc)
    style_tables(doc)
    style_figure_captions(doc)
    style_references(doc)
    n_bordered = clear_equation_borders(doc)
    drop_title_block(doc)
    n_front = front_matter(doc)
    headings = []
    for p in doc.paragraphs:
        lvl = {"Heading 1": 1, "Heading 2": 2, "Heading 3": 3}.get(p.style.name)
        if lvl and p.text.strip():
            headings.append((lvl, p.text.strip()))
    doc.save(str(DOCX))

    # The contents list, filled in with the page numbers Word computes for it.
    # Pandoc writes the field with an empty result, so the document opens
    # with a blank contents until somebody refreshes the field. Word can
    # compute the list but cannot save the file, so the list is computed
    # there and written in here.
    write_toc(DOCX, headings)
    finalise_settings(DOCX)
    print(f"         front matter: title page and certificate page "
          f"({n_front} blocks)")
    print(f"         equations stated border-free:             {n_bordered}")
    print(f"         contents list: {len(headings)} entries, written into the "
          f"document")
    _monochrome(DOCX)

    n_eq = count_equations(DOCX)
    n_colour = count_non_grey(DOCX)
    pages = pdf_pages(MARKDOWN)
    cite_problems = check_citations(body)

    print(f"[report] {DOCX.name}")
    print(f"         equations (OMML, compiled from LaTeX): {n_eq}")
    print(f"         non-grey colours in the file:          {n_colour}")
    print(f"         pages (reading copy, A4 12pt Times):   {pages}")
    if PDF.exists():
        print(f"         reading copy:                          {PDF.name}")

    ok = True
    if n_eq < 10:
        print("  x fewer than ten compiled equations: the LaTeX did not "
              "survive the conversion")
        ok = False
    if n_colour:
        print("  x the document carries a colour that is not a grey")
        ok = False
    if pages >= 0 and pages < MIN_PAGES:
        print(f"  x the report is {pages} pages; the floor is {MIN_PAGES}")
        ok = False
    if pages < 0:
        print("  -- page count not verified (no PDF engine)")
    for p in cite_problems:
        print(f"  x {p}")
        ok = False
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
