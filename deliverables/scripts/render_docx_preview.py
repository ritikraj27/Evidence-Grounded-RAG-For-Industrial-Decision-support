#!/usr/bin/env python3
"""Render the front matter of a DOCX to PNG, so it can be looked at.

Word is the only thing that lays a .docx out for real, and it will not
render on this machine. This reads the document's own XML -- the paragraph
alignment, the spacing, the run sizes, the picture extents and the page
breaks -- and draws it with matplotlib, using the same text measurement the
slide renderer uses. The layout is therefore close to Word's and not
identical, which is enough to see whether a title page hangs together.

Usage:
    python3 deliverables/scripts/render_docx_preview.py FILE.docx OUTDIR [PAGES]
"""
from __future__ import annotations

import io
import sys
import zipfile
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render_pptx_preview import Measurer

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
EMU_PT = 12700.0
PT_CM = 2.54 / 72.0


def q(tag):
    return f"{{{W_NS}}}{tag}"


def parse_spacing(ppr):
    if ppr is None:
        return 0.0, 0.0, 1.0
    sp = ppr.find(q("spacing"))
    before = after = 0.0
    line = 1.0
    if sp is not None:
        before = float(sp.get(q("before"), 0)) / 20.0
        after = float(sp.get(q("after"), 0)) / 20.0
        ln = sp.get(q("line"))
        if ln:
            line = float(ln) / 240.0
    return before, after, line


def parse_alignment(ppr):
    if ppr is None:
        return "left"
    jc = ppr.find(q("jc"))
    return (jc.get(q("val")) if jc is not None else "left") or "left"


def parse_indent(ppr):
    if ppr is None:
        return 0.0
    ind = ppr.find(q("ind"))
    if ind is None:
        return 0.0
    return float(ind.get(q("left"), 0)) / 20.0


def _on(el) -> bool:
    """A property that is present but switched off is off."""
    if el is None:
        return False
    val = el.get(q("val"))
    return val is None or val not in ("0", "false", "off")


def runs_of(p):
    out = []
    for r in p.findall(q("r")):
        rpr = r.find(q("rPr"))
        size = 12.0
        bold = italic = False
        if rpr is not None:
            sz = rpr.find(q("sz"))
            if sz is not None:
                size = float(sz.get(q("val"))) / 2.0
            bold = _on(rpr.find(q("b")))
            italic = _on(rpr.find(q("i")))
        text = "".join(t.text or "" for t in r.findall(q("t")))
        if r.find(q("br")) is not None and r.find(q("t")) is None:
            out.append({"text": "\n", "size": size, "bold": bold, "italic": italic})
            continue
        if text:
            out.append({"text": text, "size": size, "bold": bold, "italic": italic})
    return out


def pictures_of(p, zf, rels):
    out = []
    for drawing in p.iter(q("drawing")):
        extent = drawing.find(f".//{{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}}extent")
        blip = drawing.find(f".//{{{A_NS}}}blip")
        if extent is None or blip is None:
            continue
        rid = blip.get(f"{{http://schemas.openxmlformats.org/officeDocument/2006/relationships}}embed")
        target = rels.get(rid)
        if not target:
            continue
        name = "word/" + target.lstrip("/").replace("word/", "", 1)
        try:
            data = zf.read(name)
        except KeyError:
            continue
        out.append({
            "data": data,
            "w": float(extent.get("cx")) / EMU_PT,
            "h": float(extent.get("cy")) / EMU_PT,
        })
    return out


def render(docx: Path, outdir: Path, pages: int = 4):
    import xml.etree.ElementTree as ET

    zf = zipfile.ZipFile(docx)
    root = ET.fromstring(zf.read("word/document.xml"))
    body = root.find(q("body"))
    rels = {}
    try:
        rxml = ET.fromstring(zf.read("word/_rels/document.xml.rels"))
        for rel in rxml:
            rels[rel.get("Id")] = rel.get("Target")
    except KeyError:
        pass

    # The page setup.
    sect = body.find(q("sectPr"))
    pg = sect.find(q("pgSz"))
    # The page size is in twips, like every other measurement in the format.
    pw = float(pg.get(q("w"))) / 20.0
    ph = float(pg.get(q("h"))) / 20.0
    mar = sect.find(q("pgMar"))
    ml = float(mar.get(q("left"))) / 20.0
    mr = float(mar.get(q("right"))) / 20.0
    mt = float(mar.get(q("top"))) / 20.0
    mb = float(mar.get(q("bottom"))) / 20.0

    outdir.mkdir(parents=True, exist_ok=True)
    written = []
    page = 0
    cursor = mt
    fig = None
    ax = None
    measure = None

    def new_page():
        nonlocal fig, ax, page, cursor, measure
        if fig is not None:
            fig.savefig(outdir / f"page{page:02d}.png", dpi=100)
            written.append(outdir / f"page{page:02d}.png")
        page += 1
        fig = plt.figure(figsize=(pw / 72.0, ph / 72.0), dpi=100)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_xlim(0, pw)
        ax.set_ylim(ph, 0)
        ax.axis("off")
        ax.add_patch(Rectangle((0, 0), pw, ph, facecolor="white",
                               edgecolor="none"))
        measure = Measurer(fig)
        cursor = mt

    def draw_para(el, x=None, width=None):
        nonlocal cursor
        ppr = el.find(q("pPr"))
        before, after, line = parse_spacing(ppr)
        cursor += before
        runs = runs_of(el)
        pics = pictures_of(el, zf, rels)
        if x is None:
            x = ml
        base_x = x
        avail = width if width is not None else (pw - ml - mr)
        align = parse_alignment(ppr)
        indent = parse_indent(ppr)

        if pics:
            pic = pics[0]
            x = base_x + (avail - pic["w"]) / 2 if align == "center" else base_x + indent
            img = plt.imread(io.BytesIO(pic["data"]))
            ax.imshow(img, extent=(x, x + pic["w"], cursor + pic["h"], cursor),
                      aspect="auto", zorder=3)
            cursor += pic["h"]
        elif runs:
            text = "".join(r["text"] for r in runs)
            size = max(r["size"] for r in runs)
            lh = size * line * 1.2
            for hard in text.split("\n"):
                words = hard.split(" ")
                lines = []
                current = []
                used = 0.0
                for w in words:
                    seg = {"text": w, "size": size, "bold": runs[0]["bold"],
                           "italic": runs[0]["italic"]}
                    wpt = measure.seg_width(seg) * 72.0
                    sp = measure.space_in(size) * 72.0
                    add = wpt + (sp if current else 0.0)
                    if current and used + add > avail - indent:
                        lines.append(current)
                        current = [seg]
                        used = wpt
                    else:
                        current.append(seg)
                        used += add
                if current:
                    lines.append(current)
                for ln in lines:
                    lw = sum(measure.seg_width(s) for s in ln) * 72.0 \
                        + measure.space_in(size) * 72.0 * (len(ln) - 1)
                    if align == "center":
                        x = base_x + (avail - lw) / 2
                    elif align == "right":
                        x = base_x + avail - lw
                    else:
                        x = base_x + indent
                    for seg in ln:
                        ax.text(x, cursor + lh * 0.78, seg["text"],
                                fontsize=seg["size"] * 0.99,
                                color="black",
                                fontweight="bold" if seg["bold"] else "normal",
                                style="italic" if seg["italic"] else "normal",
                                family=measure.family, va="baseline", ha="left")
                        x += (measure.seg_width(seg) + measure.space_in(size)) * 72.0
                    cursor += lh
        cursor += after

    for el in list(body):
        tag = el.tag.split("}")[1]
        if tag == "sectPr":
            continue
        if fig is None:
            new_page()
        if tag == "tbl":
            # The certificate's letterhead: the emblem beside the address.
            for tr in el.findall(q("tr")):
                x = ml
                # Every cell of a row starts at the top of the row, so the
                # emblem and the letterhead sit beside one another the way
                # Word puts them.
                row_top = cursor
                tallest = 0.0
                for tc in tr.findall(q("tc")):
                    tcw = tc.find(q("tcPr"))
                    cw = 100.0
                    if tcw is not None and tcw.find(q("tcW")) is not None:
                        cw = float(tcw.find(q("tcW")).get(q("w"))) / 20.0
                    cursor = row_top
                    for p in tc.findall(q("p")):
                        draw_para(p, x=x, width=cw)
                    tallest = max(tallest, cursor - row_top)
                    x += cw
                cursor = row_top + tallest
            continue
        if tag == "sdt":
            # The contents list is a structured document tag, so its
            # paragraphs are one level down.
            content = el.find(q("sdtContent"))
            if content is not None:
                for sub in list(content):
                    if sub.tag == q("p"):
                        draw_para(sub)
            continue
        if tag != "p":
            continue
        # A page break inside the paragraph starts a new page. Word records
        # where it broke the pages when it saved, so a document it has
        # saved can be paginated the way Word paginated it.
        breaks = [b for b in el.iter(q("br")) if b.get(q("type")) == "page"]
        if breaks:
            new_page()
        elif el.find(f".//{q('lastRenderedPageBreak')}") is not None:
            new_page()
        if page > pages:
            break
        draw_para(el)

    if fig is not None:
        fig.savefig(outdir / f"page{page:02d}.png", dpi=100)
        written.append(outdir / f"page{page:02d}.png")
    return written


if __name__ == "__main__":
    src = Path(sys.argv[1])
    dst = Path(sys.argv[2])
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    for p in render(src, dst, n):
        print(p)
