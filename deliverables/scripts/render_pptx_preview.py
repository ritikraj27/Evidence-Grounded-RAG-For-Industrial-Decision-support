#!/usr/bin/env python3
"""Render a PPTX to PNG pages, for looking at a deck without PowerPoint.

Neither LibreOffice nor a scripted PowerPoint save is available on this
machine, so this reads the built .pptx with python-pptx and draws it with
matplotlib: shapes as filled rectangles, tables cell by cell, pictures from
their file, and text laid out with the run's own size, weight and colour.

The text metrics are an approximation, not PowerPoint's, so this is a check on
geometry and balance rather than on exact line breaks. It will show a title
running off the edge, a panel with text spilling out of it, a table wider than
the slide, or a slide that is visually empty at the bottom.

Usage:
    python3 deliverables/scripts/render_pptx_preview.py DECK.pptx OUTDIR
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.enum.text import PP_ALIGN

EMU_IN = 914400.0


def _rgb(color, default=(0, 0, 0)):
    try:
        c = color.rgb
        return (c[0] / 255.0, c[1] / 255.0, c[2] / 255.0)
    except Exception:
        return default


def _runs(para):
    out = []
    for r in para.runs:
        size = r.font.size.pt if r.font.size else 18.0
        out.append({
            "text": r.text,
            "size": size,
            "bold": bool(r.font.bold),
            "italic": bool(r.font.italic),
            "color": _rgb(r.font.color),
        })
    return out


#: Mean advance width of mixed-case text, in em. Only used as a fallback.
CHAR_W = 0.52


class Measurer:
    """Measures real glyph widths, so a word is never drawn over its neighbour.

    An estimate of the advance width is not good enough: bold text is wider
    than the estimate, so the next word lands on top of the previous one and
    the space between them disappears. Measuring the actual string avoids that.
    """

    def __init__(self, fig):
        from matplotlib.font_manager import FontProperties
        self._fp = FontProperties
        self._renderer = fig.canvas.get_renderer()
        self._dpi = fig.dpi
        # The face the deck is actually set in. A preview in a different face
        # shows line breaks that will not happen in PowerPoint.
        from matplotlib import font_manager
        available = {f.name for f in font_manager.fontManager.ttflist}
        self.family = ("Times New Roman" if "Times New Roman" in available
                       else "DejaVu Sans")

    def width_in(self, text, size, bold, italic):
        fp = self._fp(family=self.family, size=size,
                      weight="bold" if bold else "normal",
                      style="italic" if italic else "normal")
        try:
            w, _h, _d = self._renderer.get_text_width_height_descent(text, fp, False)
            return w / self._dpi
        except Exception:
            return len(text) * size * CHAR_W / 72.0

    def seg_width(self, seg):
        return self.width_in(seg["text"], seg["size"], seg["bold"], seg["italic"])

    def space_in(self, size, bold=False, italic=False):
        return self.width_in(" ", size, bold, italic)


def _wrap(runs, width_in, measure):
    """Greedy word wrap over styled runs.

    Each line is a list of segments: a word and the style it was written in.
    Words are separated by a measured space, so the gap is always visible.
    """
    limit = width_in
    lines = [[]]
    used = 0.0
    for run in runs:
        for ci, chunk in enumerate(run["text"].split("\n")):
            if ci:
                lines.append([])
                used = 0.0
            for word in chunk.split(" "):
                if not word:
                    continue
                seg = {**run, "text": word}
                w = measure.seg_width(seg)
                sp = measure.space_in(run["size"], run["bold"], run["italic"])
                add = w if used == 0.0 else w + sp
                if used + add > limit and used > 0.0:
                    lines.append([seg])
                    used = w
                else:
                    lines[-1].append(seg)
                    used += add
    return lines


def draw_textframe(ax, tf, x, y, w, h, measure):
    """Draw a text frame's paragraphs, top-anchored."""
    ml = (tf.margin_left or 0) / EMU_IN
    mr = (tf.margin_right or 0) / EMU_IN
    mt = (tf.margin_top or 0) / EMU_IN
    usable = max(w - ml - mr, 0.4)
    cursor = y + mt
    for para in tf.paragraphs:
        runs = _runs(para)
        if not runs:
            cursor += 0.18
            continue
        size = max(r["size"] for r in runs)
        spacing = para.line_spacing if isinstance(para.line_spacing, float) else 1.0
        lines = _wrap(runs, usable, measure)
        lh = size * spacing * 1.2 / 72.0
        after = (para.space_after.pt / 72.0) if para.space_after else 0.0
        for line in lines:
            if cursor > y + h + 0.6:
                break
            lw = sum(measure.seg_width(r) for r in line)
            if len(line) > 1:
                lw += sum(measure.space_in(r["size"], r["bold"], r["italic"])
                          for r in line[:-1])
            if para.alignment == PP_ALIGN.CENTER:
                lx = x + ml + (usable - lw) / 2.0
            elif para.alignment == PP_ALIGN.RIGHT:
                lx = x + ml + usable - lw
            else:
                lx = x + ml
            for k, r in enumerate(line):
                ax.text(lx, cursor + lh * 0.72, r["text"],
                        fontsize=r["size"] * 0.99,
                        color=r["color"],
                        fontweight="bold" if r["bold"] else "normal",
                        style="italic" if r["italic"] else "normal",
                        family=measure.family,
                        va="baseline", ha="left")
                lx += measure.seg_width(r)
                if k < len(line) - 1:
                    lx += measure.space_in(r["size"], r["bold"], r["italic"])
            cursor += lh
        cursor += after


def draw_table(ax, shape, x, y, measure):
    t = shape.table
    col_x = [x]
    for c in t.columns:
        col_x.append(col_x[-1] + c.width / EMU_IN)
    row_y = [y]
    for r in t.rows:
        row_y.append(row_y[-1] + r.height / EMU_IN)
    for i, row in enumerate(t.rows):
        for j, cell in enumerate(row.cells):
            cw = col_x[j + 1] - col_x[j]
            ch = row_y[i + 1] - row_y[i]
            try:
                fill = _rgb(cell.fill.fore_color, (1, 1, 1))
            except Exception:
                fill = (1, 1, 1)
            ax.add_patch(Rectangle((col_x[j], row_y[i]), cw, ch,
                                   facecolor=fill, edgecolor=(0.78, 0.78, 0.78),
                                   linewidth=0.5))
            draw_textframe(ax, cell.text_frame, col_x[j], row_y[i], cw, ch, measure)


def render(pptx_path: Path, outdir: Path, only=None):
    prs = Presentation(str(pptx_path))
    W = prs.slide_width / EMU_IN
    H = prs.slide_height / EMU_IN
    outdir.mkdir(parents=True, exist_ok=True)
    paths = []
    for i, slide in enumerate(prs.slides, start=1):
        if only and i not in only:
            continue
        fig = plt.figure(figsize=(W, H), dpi=100)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_xlim(0, W)
        ax.set_ylim(H, 0)
        ax.axis("off")
        ax.add_patch(Rectangle((0, 0), W, H, facecolor="white",
                               edgecolor="none"))
        measure = Measurer(fig)
        for shape in slide.shapes:
            x = shape.left / EMU_IN
            y = shape.top / EMU_IN
            w = shape.width / EMU_IN
            h = shape.height / EMU_IN
            if shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
                try:
                    img = matplotlib.image.imread(
                        shape.image.blob and __import__("io").BytesIO(
                            shape.image.blob))
                    ax.imshow(img, extent=(x, x + w, y + h, y),
                              aspect="auto", zorder=5)
                except Exception:
                    ax.add_patch(Rectangle((x, y), w, h, facecolor=(0.9, 0.9, 0.9),
                                           edgecolor=(0.6, 0.6, 0.6), zorder=4))
                continue
            if shape.has_table:
                draw_table(ax, shape, x, y, measure)
                continue
            if shape.shape_type == MSO_SHAPE_TYPE.AUTO_SHAPE:
                try:
                    fill = _rgb(shape.fill.fore_color, (1, 1, 1))
                except Exception:
                    fill = (1, 1, 1)
                ax.add_patch(Rectangle((x, y), w, h, facecolor=fill,
                                       edgecolor="none", zorder=2))
            if shape.has_text_frame and shape.text_frame.text.strip():
                draw_textframe(ax, shape.text_frame, x, y, w, h, measure)
        path = outdir / f"slide_{i:02d}.png"
        fig.savefig(path, dpi=100)
        plt.close(fig)
        paths.append(path)
    return paths


if __name__ == "__main__":
    src = Path(sys.argv[1])
    dst = Path(sys.argv[2])
    only = None
    if len(sys.argv) > 3:
        only = {int(a) for a in sys.argv[3].split(",")}
    for p in render(src, dst, only):
        print(p)
