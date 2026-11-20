#!/usr/bin/env python3
"""The theme and the layout primitives for the final MTP deck.

This is a deck of its own, not a copy of the ten-minute one. Its idea is
restraint: one column, one accent, a lot of white, and a single sentence under
every title saying what the slide establishes. The institute's purple is the
only colour, and it appears in six places: the tick beside the section label,
the hero number on a slide, the rule under a table's header, the figure number
in a caption, the numeral on a section divider, and the word that opens a
takeaway.

The primitives live here so the seventy slides cannot drift apart in the way
they are laid out. Every measurement is in inches and floats, because that is
how a layout is reasoned about; the conversion to EMU happens at the call.
"""
from __future__ import annotations

import io
import tempfile
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from PIL import Image  # noqa: E402
from pptx import Presentation  # noqa: E402
from pptx.dml.color import RGBColor  # noqa: E402
from pptx.enum.shapes import MSO_SHAPE  # noqa: E402
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN  # noqa: E402
from pptx.oxml.ns import qn  # noqa: E402
from pptx.util import Emu, Inches, Pt  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
LOGO = ROOT / "deliverables" / "assets" / "iitkgp_emblem.png"
FIGDIR = ROOT / "deliverables" / "figures"

# ------------------------------------------------------------------ palette
#: The ink. Not pure black: a hair of warmth survives a projector better than
#: 0,0,0 does.
INK = RGBColor(0x11, 0x11, 0x11)
INK_SOFT = RGBColor(0x3C, 0x3C, 0x42)
GREY = RGBColor(0x6E, 0x6E, 0x76)
GREY_LIGHT = RGBColor(0x9A, 0x9A, 0xA2)
RULE = RGBColor(0xE4, 0xE4, 0xE8)
RULE_SOFT = RGBColor(0xF0, 0xF0, 0xF3)
SURFACE = RGBColor(0xF7, 0xF7, 0xF9)
ZEBRA = RGBColor(0xFB, 0xFB, 0xFC)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

#: The institute's purple, the colour of the emblem. It is the deck's only
#: accent.
ACCENT = RGBColor(0x29, 0x19, 0x72)
ACCENT_TINT = RGBColor(0xF2, 0xF0, 0xF8)
ACCENT_LINE = RGBColor(0xC9, 0xC2, 0xE4)

#: The deck is set in the same face as the report it defends.
TIMES = "Times New Roman"

# -------------------------------------------------------------------- grid
SW, SH = 13.333, 7.5
ML, MR = 0.72, 0.72
CW = SW - ML - MR

EYEBROW_Y = 0.44
TITLE_Y = 0.70
KICKER_Y = 1.19
RULE_Y = 1.63
BODY_TOP = 1.92
BODY_BOT = 6.52
TAKE_Y = 5.84
FOOT_RULE_Y = 6.80
FOOT_Y = 6.90

#: The table style that draws nothing, so the deck can draw its own.
NO_STYLE_NO_GRID = "{2D5ABB26-0587-4C30-8999-92F81FD0307C}"


def _spc(run, hundredths: int) -> None:
    """Track the letters of a run, in hundredths of a point.

    A small amount of tracking on a short uppercase line is what separates a
    label from a heading. Without it the two read at the same weight.
    """
    run.font._rPr.set("spc", str(hundredths))


class Deck:
    """A deck and the vocabulary of its slides."""

    def __init__(self, footer: str):
        self.prs = Presentation()
        self.prs.slide_width = Inches(SW)
        self.prs.slide_height = Inches(SH)
        self.blank = self.prs.slide_layouts[6]
        self.footer_text = footer
        self.n = 0
        self.part = ""

    # ------------------------------------------------------------ plumbing
    def save(self, path: Path) -> None:
        self.prs.save(str(path))

    def notes(self, slide, text: str) -> None:
        slide.notes_slide.notes_text_frame.text = text

    def logo(self, slide, x: float, y: float, h: float) -> float:
        """The institute's emblem, at a height, keeping its aspect ratio."""
        if not LOGO.exists():
            return 0.0
        with Image.open(LOGO) as im:
            aspect = im.size[0] / im.size[1]
        w = h * aspect
        slide.shapes.add_picture(str(LOGO), Inches(x), Inches(y),
                                 width=Inches(w), height=Inches(h))
        return w

    # --------------------------------------------------------------- shapes
    def rect(self, slide, x, y, w, h, fill, *, line=None, line_w=0.75):
        sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y),
                                    Inches(w), Inches(h))
        if fill is None:
            sh.fill.background()
        else:
            sh.fill.solid()
            sh.fill.fore_color.rgb = fill
        if line is None:
            sh.line.fill.background()
        else:
            sh.line.color.rgb = line
            sh.line.width = Pt(line_w)
        sh.shadow.inherit = False
        return sh

    def rule(self, slide, x, y, w, color=RULE, weight=0.75):
        """A hairline, drawn as a filled rectangle so it has no end caps."""
        return self.rect(slide, x, y, w, weight / 72.0, color)

    def text(self, slide, x, y, w, h, *, align=PP_ALIGN.LEFT, anchor=None):
        tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = Emu(0)
        tf.margin_top = tf.margin_bottom = Emu(0)
        tf.paragraphs[0].alignment = align
        if anchor is not None:
            tf.vertical_anchor = anchor
        return tf

    def para(self, tf, text, *, size=15, bold=False, italic=False, color=INK,
             space_after=7, first=False, align=PP_ALIGN.LEFT, line=1.16,
             track=None, font=TIMES):
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        p.alignment = align
        p.space_after = Pt(space_after)
        p.line_spacing = line
        r = p.add_run()
        r.text = text
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.italic = italic
        r.font.color.rgb = color
        r.font.name = font
        if track:
            _spc(r, track)
        return p

    def rich(self, tf, chunks, *, size=15, space_after=7, first=False,
             align=PP_ALIGN.LEFT, line=1.16):
        """chunks = [(text, bold, color) | (text, bold, color, italic)]"""
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        p.alignment = align
        p.space_after = Pt(space_after)
        p.line_spacing = line
        for chunk in chunks:
            text, bold, color = chunk[0], chunk[1], chunk[2]
            italic = chunk[3] if len(chunk) > 3 else False
            r = p.add_run()
            r.text = text
            r.font.size = Pt(size)
            r.font.bold = bold
            r.font.italic = italic
            r.font.color.rgb = color
            r.font.name = TIMES
        return p

    # -------------------------------------------------------------- slides
    def slide(self, title, kicker=None, *, eyebrow=None, chrome=True):
        """A content slide: label, title, one line saying what it establishes."""
        self.n += 1
        s = self.prs.slides.add_slide(self.blank)
        if not chrome:
            return s
        label = eyebrow if eyebrow is not None else self.part
        if label:
            self.rect(s, ML, EYEBROW_Y + 0.035, 0.075, 0.075, ACCENT)
            tf = self.text(s, ML + 0.18, EYEBROW_Y, 9.4, 0.22)
            self.para(tf, label.upper(), size=11, bold=True, color=ACCENT,
                      first=True, space_after=0, track=70)
        # A title is one line. The size is worked out from the length so
        # that a long title shrinks instead of wrapping into the kicker.
        size = 26 if len(title) <= 54 else max(18, int(1425 / len(title)))
        tf = self.text(s, ML, TITLE_Y, CW - 1.0, 0.56)
        self.para(tf, title, size=size, bold=True, color=INK, first=True,
                  space_after=0, line=1.04)
        if kicker:
            tf = self.text(s, ML, KICKER_Y, CW - 1.1, 0.38)
            self.para(tf, kicker, size=13.5, italic=True, color=GREY,
                      first=True, space_after=0, line=1.14)
        self.rule(s, ML, RULE_Y, CW)
        self.rule(s, ML, FOOT_RULE_Y, CW)
        tf = self.text(s, ML, FOOT_Y, 10.4, 0.24)
        self.para(tf, self.footer_text, size=9, color=GREY_LIGHT, first=True,
                  space_after=0)
        tf = self.text(s, SW - MR - 0.7, FOOT_Y - 0.01, 0.7, 0.24,
                        align=PP_ALIGN.RIGHT)
        self.para(tf, str(self.n), size=10, color=INK_SOFT, first=True,
                  space_after=0, align=PP_ALIGN.RIGHT)
        self.logo(s, SW - MR - 0.62, 0.40, 0.56)
        return s

    def section_slide(self, number, title, blurb, items, notes_text=None):
        """A divider: a numeral, a title, and what the section holds."""
        self.n += 1
        s = self.prs.slides.add_slide(self.blank)
        tf = self.text(s, SW - 5.30, 1.55, 4.60, 2.40, align=PP_ALIGN.RIGHT)
        self.para(tf, f"{number:02d}", size=150, bold=True,
                  color=RGBColor(0xEC, 0xEC, 0xF0), first=True, space_after=0,
                  align=PP_ALIGN.RIGHT, line=0.92)
        tf = self.text(s, ML, 2.34, 3.0, 0.24)
        self.para(tf, f"SECTION {number:02d}", size=11.5, bold=True, color=ACCENT,
                  first=True, space_after=0, track=80)
        tf = self.text(s, ML, 2.62, 7.0, 1.10)
        self.para(tf, title, size=30 if len(title) > 30 else 36, bold=True,
                  color=INK, first=True, space_after=0, line=1.04)
        self.rect(s, ML, 3.74, 1.30, 0.028, ACCENT)
        tf = self.text(s, ML, 3.98, 6.9, 0.70)
        self.para(tf, blurb, size=15, color=GREY, first=True, space_after=0,
                  line=1.24)
        # A long list runs in two columns, because a divider is not the place
        # for a column of text that reaches the floor.
        if len(items) > 6:
            half = (len(items) + 1) // 2
            columns = [(ML, items[:half]), (ML + 3.55, items[half:])]
        else:
            columns = [(ML, items)]
        for cx, column in columns:
            tf = self.text(s, cx, 4.76, 3.40, 1.76)
            for i, item in enumerate(column):
                self.rich(tf, [("·   ", False, ACCENT), (item, False, INK_SOFT)],
                          size=12.5, space_after=4, first=(i == 0), line=1.18)
        self.rule(s, ML, FOOT_RULE_Y, CW)
        tf = self.text(s, ML, FOOT_Y, 10.4, 0.24)
        self.para(tf, self.footer_text, size=9, color=GREY_LIGHT, first=True,
                  space_after=0)
        tf = self.text(s, SW - MR - 0.7, FOOT_Y - 0.01, 0.7, 0.24,
                        align=PP_ALIGN.RIGHT)
        self.para(tf, str(self.n), size=10, color=INK_SOFT, first=True,
                  space_after=0, align=PP_ALIGN.RIGHT)
        self.logo(s, SW - MR - 0.62, 0.40, 0.56)
        if notes_text:
            self.notes(s, notes_text)
        return s

    def title_slide(self, title, subtitle, image, credits):
        """The opening slide: the title, the picture, and then the credits.

        The credits are a list of (chunks, size) pairs, where a chunk is a
        (text, colour, bold) triple. The presenter, the roll number and the
        supervisor sit under the picture, in the order a title page reads.
        """
        self.n += 1
        s = self.prs.slides.add_slide(self.blank)
        self.logo(s, SW - MR - 0.74, 0.30, 0.62)
        tf = self.text(s, 0.70, 0.92, SW - 1.40, 1.66, align=PP_ALIGN.CENTER)
        self.para(tf, title, size=34, bold=True, color=INK, first=True,
                  space_after=0, align=PP_ALIGN.CENTER, line=1.06)
        tf = self.text(s, 1.50, 2.60, SW - 3.00, 0.40, align=PP_ALIGN.CENTER)
        self.para(tf, subtitle, size=15.5, italic=True, color=GREY, first=True,
                  space_after=0, align=PP_ALIGN.CENTER, line=1.2)
        self.rect(s, (SW - 1.50) / 2, 3.06, 1.50, 0.028, ACCENT)
        if image is not None:
            s.shapes.add_picture(str(image), Inches((SW - 9.20) / 2),
                                 Inches(3.26), width=Inches(9.20))
        y = 6.08
        for chunks, size in credits:
            tf = self.text(s, 1.4, y, SW - 2.8, 0.28, align=PP_ALIGN.CENTER)
            self.rich(tf, chunks, size=size, space_after=0, first=True,
                      align=PP_ALIGN.CENTER, line=1.16)
            y += 0.26
        self.rect(s, 0, SH - 0.075, SW, 0.075, ACCENT)
        return s

    def closing_slide(self, heading, lines, foot):
        self.n += 1
        s = self.prs.slides.add_slide(self.blank)
        self.rect(s, 0, 0, SW, 0.075, ACCENT)
        self.logo(s, SW - MR - 0.74, 0.34, 0.64)
        tf = self.text(s, 1.4, 2.42, SW - 2.8, 0.80, align=PP_ALIGN.CENTER)
        self.para(tf, heading, size=38, bold=True, color=INK, first=True,
                  space_after=0, align=PP_ALIGN.CENTER)
        tf = self.text(s, 1.8, 3.34, SW - 3.6, 0.34, align=PP_ALIGN.CENTER)
        self.para(tf, lines[0], size=16, italic=True, color=GREY, first=True,
                  space_after=0, align=PP_ALIGN.CENTER)
        tf = self.text(s, 2.2, 3.96, SW - 4.4, 1.30, align=PP_ALIGN.CENTER)
        for i, line in enumerate(lines[1:]):
            self.para(tf, line, size=14, color=INK_SOFT, first=(i == 0),
                      space_after=5, align=PP_ALIGN.CENTER, line=1.2)
        self.rect(s, (SW - 1.50) / 2, 5.44, 1.50, 0.028, ACCENT)
        tf = self.text(s, 2.0, 5.66, SW - 4.0, 0.60, align=PP_ALIGN.CENTER)
        self.para(tf, foot, size=13.5, color=GREY, first=True, space_after=0,
                  align=PP_ALIGN.CENTER, line=1.2)
        return s

    # ---------------------------------------------------------- components
    def bullets(self, slide, x, y, w, items, *, size=15, gap=9, h=None):
        """A list. The marker is a small accent dot, not a dash."""
        tf = self.text(slide, x, y, w, h if h else (BODY_BOT - y))
        for i, item in enumerate(items):
            if isinstance(item, tuple):
                head, rest = item
                self.rich(tf, [("·   ", False, ACCENT), (head, True, INK),
                               (rest, False, INK_SOFT)],
                          size=size, space_after=gap, first=(i == 0), line=1.2)
            else:
                self.rich(tf, [("·   ", False, ACCENT), (item, False, INK_SOFT)],
                          size=size, space_after=gap, first=(i == 0), line=1.2)
        return tf

    def prose(self, slide, x, y, w, h, paragraphs, *, size=15, gap=9):
        tf = self.text(slide, x, y, w, h)
        for i, item in enumerate(paragraphs):
            if isinstance(item, tuple):
                head, rest = item
                self.rich(tf, [(head, True, INK), (rest, False, INK_SOFT)],
                          size=size, space_after=gap, first=(i == 0), line=1.24)
            else:
                self.para(tf, item, size=size, color=INK_SOFT, space_after=gap,
                          first=(i == 0), line=1.24)
        return tf

    def card(self, slide, x, y, w, h, heading, body, *, size=18, bsize=14,
             fill=SURFACE, edge=None):
        """A quiet card: a tinted panel with a heading and a list of lines."""
        self.rect(slide, x, y, w, h, fill, line=edge)
        tf = self.text(slide, x + 0.24, y + 0.17, w - 0.48, h - 0.30)
        self.para(tf, heading, size=size, bold=True, color=INK, first=True,
                  space_after=8, line=1.08)
        for item in body:
            if isinstance(item, tuple):
                head, rest = item
                self.rich(tf, [(head, True, INK), (rest, False, INK_SOFT)],
                          size=bsize, space_after=7, line=1.2)
            else:
                self.para(tf, item, size=bsize, color=INK_SOFT, space_after=7,
                          line=1.2)
        return tf

    def kpi(self, slide, x, y, w, value, label, *, vsize=36, lsize=12.5,
            rule_color=ACCENT):
        self.rule(slide, x, y, w, rule_color, 1.5)
        tf = self.text(slide, x, y + 0.16, w, 0.62)
        self.para(tf, value, size=vsize, bold=True, color=ACCENT, first=True,
                  space_after=0, line=1.0)
        tf = self.text(slide, x, y + 0.16 + vsize / 72.0 * 1.06, w, 0.80)
        self.para(tf, label, size=lsize, color=INK_SOFT, first=True, space_after=0,
                  line=1.18)

    def takeaway(self, slide, label, text, *, y=TAKE_Y, h=0.86, x=ML, w=CW,
                 stacked=False):
        """The one line a reader should leave the slide with.

        Across the page the label sits beside the sentence. In a column it
        sits above it, because a column is too narrow to carry both.
        """
        self.rect(slide, x, y, w, h, SURFACE)
        self.rect(slide, x, y, 0.035, h, ACCENT)
        if stacked:
            tf = self.text(slide, x + 0.26, y + 0.10, w - 0.52, 0.20)
            self.para(tf, label.upper(), size=10.5, bold=True, color=ACCENT,
                      first=True, space_after=0, track=60, line=1.1)
            tf = self.text(slide, x + 0.26, y + 0.34, w - 0.52, h - 0.44)
            self.para(tf, text, size=13.5, color=INK, first=True, space_after=0,
                      line=1.16)
            return
        tf = self.text(slide, x + 0.28, y + 0.10, 1.85, h - 0.20)
        self.para(tf, label.upper(), size=10.5, bold=True, color=ACCENT, first=True,
                  space_after=0, track=60, line=1.1)
        tf = self.text(slide, x + 2.22, y + 0.11, w - 2.50, h - 0.22)
        self.para(tf, text, size=13.5, color=INK, first=True, space_after=0,
                  line=1.18)

    def block(self, slide, x, y, w, h, heading, body, *, size=12.5,
              bsize=13):
        """A labelled note: a rule, a small heading, and the prose under it.

        This carries more text than a card of the same height, because the
        text runs to the edge of the column instead of sitting inside a
        panel. The formula slides use it for the three notes that say where
        a formula came from, why its value is what it is, and what the
        caveat is.
        """
        self.rule(slide, x, y, w, RULE, 0.75)
        tf = self.text(slide, x, y + 0.10, w, h - 0.10)
        self.para(tf, heading.upper(), size=size, bold=True, color=ACCENT,
                  first=True, space_after=5, track=60, line=1.1)
        self.para(tf, body, size=bsize, color=INK_SOFT, space_after=0,
                  line=1.18)

    def table(self, slide, x, y, w, headers, rows, *, col_widths=None,
              size=12.5, head_size=12.5, row_h=0.34, head_h=0.36, zebra=True,
              bold_first=False):
        """A table with no grid: a rule under the header, and a quiet zebra."""
        n_rows = len(rows) + 1
        shape = slide.shapes.add_table(n_rows, len(headers), Inches(x), Inches(y),
                                       Inches(w), Inches(head_h + row_h * len(rows)))
        tbl = shape.table
        _no_table_style(tbl)
        if col_widths:
            total = sum(col_widths)
            for i, cw in enumerate(col_widths):
                tbl.columns[i].width = Emu(int(Inches(w) * cw / total))
        tbl.rows[0].height = Inches(head_h)
        for i in range(1, n_rows):
            tbl.rows[i].height = Inches(row_h)

        for j, htxt in enumerate(headers):
            cell = tbl.cell(0, j)
            cell.fill.background()
            cell.margin_left = cell.margin_right = Inches(0.06)
            cell.margin_top = cell.margin_bottom = Inches(0.02)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = cell.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT
            r = p.add_run()
            r.text = htxt
            r.font.size = Pt(head_size)
            r.font.bold = True
            r.font.color.rgb = INK
            r.font.name = TIMES

        for i, row in enumerate(rows, start=1):
            for j, val in enumerate(row):
                cell = tbl.cell(i, j)
                cell.fill.solid()
                cell.fill.fore_color.rgb = ZEBRA if (zebra and i % 2 == 0) else WHITE
                cell.margin_left = cell.margin_right = Inches(0.06)
                cell.margin_top = cell.margin_bottom = Inches(0.02)
                cell.vertical_anchor = MSO_ANCHOR.MIDDLE
                p = cell.text_frame.paragraphs[0]
                r = p.add_run()
                text = str(val)
                strong = text.startswith("**")
                r.text = text.replace("**", "")
                r.font.size = Pt(size)
                r.font.bold = strong or (bold_first and j == 0)
                r.font.color.rgb = INK if (strong or (bold_first and j == 0)) else INK_SOFT
                r.font.name = TIMES

        self.rule(slide, x, y + head_h, w, ACCENT, 1.25)
        self._check_widths(headers, rows, col_widths, w, size, row_h, head_h)
        return shape

    def _check_widths(self, headers, rows, col_widths, w, size, row_h,
                      head_h) -> None:
        """Report a cell that would wrap past the height its row allows.

        PowerPoint grows a row to fit its text, so a cell that wraps past its
        row pushes the rows below it down, and the table stops being the
        shape it was drawn as. The estimate is the same one the overflow
        checker uses.
        """
        if not col_widths:
            return
        total = sum(col_widths)
        line_in = size * 1.22 / 72.0
        for j, head in enumerate(headers):
            cells = [(head, head_h)] + [(r[j], row_h) for r in rows if j < len(r)]
            for cell, height in cells:
                text = str(cell).replace("**", "")
                width_pt = w * col_widths[j] / total * 72.0 - 8.6
                per_line = max(int(width_pt / (0.50 * size * 1.10)), 8)
                lines = max(1, -(-len(text) // per_line))
                if lines * line_in > height - 0.04:
                    print(f"  ! slide {self.n}: a table cell needs {lines} "
                          f"lines in a {height:.2f}in row: {text[:56]!r}")

    def figure(self, slide, key, x, y, w, *, frame=True):
        """A measured figure, at a width, keeping its aspect ratio."""
        path = FIGDIR / f"{key}.png"
        if not path.exists():
            return 0.0
        with Image.open(path) as im:
            aspect = im.size[0] / im.size[1]
        h = w / aspect
        if frame:
            self.rect(slide, x - 0.10, y - 0.10, w + 0.20, h + 0.20, None,
                      line=RULE, line_w=0.75)
        slide.shapes.add_picture(str(path), Inches(x), Inches(y), width=Inches(w))
        return h

    def caption(self, slide, x, y, w, number, text, *, size=12, h=0.92):
        """A figure caption, with its number in the accent."""
        tf = self.text(slide, x, y, w, h)
        self.rich(tf, [(f"Figure {number}.  ", True, ACCENT), (text, False, GREY)],
                  size=size, space_after=0, first=True, line=1.18)
        return tf

    # -------------------------------------------------------------- maths
    def formula(self, latex, *, fontsize=26):
        """Render a formula to a black-on-transparent PNG and return the path.

        The maths is written for matplotlib's renderer, which is a subset of
        LaTeX, so upright words are written with `\\mathrm{}` rather than
        `\\text{}`. The face is STIX, which is the Times of the maths world.
        """
        with matplotlib.rc_context({
                "mathtext.fontset": "stix",
                "font.family": "serif",
                "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
        }):
            tmp = Path(tempfile.mkdtemp(prefix="mtp-formula-"))
            path = tmp / "f.png"
            fig = plt.figure(figsize=(0.01, 0.01))
            fig.text(0, 0, "$" + latex + "$", fontsize=fontsize,
                     color="black")
            fig.savefig(path, dpi=300, bbox_inches="tight", pad_inches=0.04,
                        transparent=True)
            plt.close(fig)
        return path

    def put_formula(self, slide, latex, x, y, w, *, fontsize=26, max_h=None,
                    centre_w=None):
        """Place a formula, scaled to fit the width and an optional height.

        The band a formula sits in is a fixed height, and a long formula
        would otherwise run past it, so the image is scaled by whichever of
        the two limits binds first. When a band width is given the image is
        centred inside it.
        """
        path = self.formula(latex, fontsize=fontsize)
        with Image.open(path) as im:
            aspect = im.size[0] / im.size[1]
        h = w / aspect
        if max_h is not None and h > max_h:
            h = max_h
            w = h * aspect
        if centre_w is not None:
            x = x + (centre_w - w) / 2
        slide.shapes.add_picture(str(path), Inches(x), Inches(y),
                                 width=Inches(w), height=Inches(h))
        return h, w


def _no_table_style(tbl) -> None:
    """Take the table off PowerPoint's default blue style.

    The deck draws its own rules, so the built-in banding and borders have to
    go, or they show through the fills.
    """
    tbl.first_row = False
    tbl.horz_banding = False
    tblPr = tbl._tbl.tblPr
    for el in tblPr.findall(qn("a:tableStyleId")):
        tblPr.remove(el)
    el = tblPr.makeelement(qn("a:tableStyleId"), {})
    el.text = NO_STYLE_NO_GRID
    tblPr.append(el)


def png_size(path: Path):
    with Image.open(path) as im:
        return im.size


def image_bytes(path: Path) -> bytes:
    return Path(path).read_bytes()


def open_image(path: Path):
    return io.BytesIO(Path(path).read_bytes())
