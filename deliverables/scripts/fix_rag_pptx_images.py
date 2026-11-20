#!/usr/bin/env python3
"""Repair the image relationships in RAG_PPT.pptx so the deck opens on Windows.

The deck on the Desktop was built by python-pptx and then re-saved by
PowerPoint for Mac. Thirty-five of its thirty-six pictures carry a picture
frame with no usable link: twenty-one of them are the IIT Kharagpur emblem,
which was written as an empty `<a:blip/>` with no `r:embed` at all, and the
rest either point at a relationship whose target is the literal string
"NULL" or at a media part that is not in the package. macOS PowerPoint
tolerates this; Windows PowerPoint shows a broken-image placeholder instead,
so the emblem and the figures never appear.

The fix is to put the real bytes back. `deliverables/final_mtp.pptx` is the
same deck with the same slides and the same picture geometry, and every one
of its images is linked correctly, so its media parts are the source of truth
for what each picture frame should contain.

What this does, per slide, in picture order:
  * a picture whose link already resolves is left untouched;
  * a picture whose link is broken takes the bytes of the matching picture in
    the reference deck, which is added to `ppt/media/`, given a fresh
    relationship on the slide, and named in the picture's `<a:blip>`.

Usage:
    python3 deliverables/scripts/fix_rag_pptx_images.py SOURCE.pptx OUT.pptx
"""
from __future__ import annotations

import hashlib
import re
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REFERENCE = ROOT / "deliverables" / "final_mtp.pptx"

#: The picture elements on a slide, in the order they appear in the XML.
PICT_RE = re.compile(r"<p:pic>.*?</p:pic>", re.S)
BLIP_RE = re.compile(r"<a:blip(?:\s[^>]*)?/>")
EMBED_RE = re.compile(r'r:embed="([^"]*)"')
DESCR_RE = re.compile(r'descr="([^"]*)"')
EXT_RE = re.compile(r'<a:ext cx="(\d+)" cy="(\d+)"')
REL_RE = re.compile(
    r'<Relationship Id="([^"]+)" Type="([^"]+)" Target="([^"]*)"\s*/>'
)
NS_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


def read_rels(zf: zipfile.ZipFile, slide: int) -> dict:
    """The slide's relationships, as {rId: (type, target)}."""
    name = "ppt/slides/_rels/slide%d.xml.rels" % slide
    if name not in zf.namelist():
        return {}
    out = {}
    for m in REL_RE.finditer(zf.read(name).decode("utf-8")):
        out[m.group(1)] = (m.group(2), m.group(3))
    return out


def picture_frames(xml: str) -> list:
    """The picture frames on a slide, as a list of {descr, ext, blip}."""
    frames = []
    for m in PICT_RE.finditer(xml):
        block = m.group(0)
        descr = DESCR_RE.search(block)
        ext = EXT_RE.search(block)
        blip = BLIP_RE.search(block)
        frames.append({
            "descr": descr.group(1) if descr else "",
            "ext": (ext.group(1), ext.group(2)) if ext else None,
            "blip": blip.group(0) if blip else None,
        })
    return frames


def media_of(zf: zipfile.ZipFile, slide: int, frame: dict):
    """The bytes a picture frame points at, or None when its link is broken."""
    if not frame["blip"]:
        return None
    embed = EMBED_RE.search(frame["blip"])
    if not embed:
        return None
    rels = read_rels(zf, slide)
    entry = rels.get(embed.group(1))
    if not entry:
        return None
    target = entry[1]
    if not target or target.upper() == "NULL":
        return None
    part = "ppt/" + target.replace("../", "")
    if part not in zf.namelist():
        return None
    return zf.read(part)


def next_rid(rels: dict) -> str:
    used = {int(m.group(1)) for m in (re.match(r"rId(\d+)$", r) for r in rels) if m}
    n = 1
    while n in used:
        n += 1
    return "rId%d" % n


def repair(source: Path, output: Path, reference: Path) -> dict:
    src = zipfile.ZipFile(source)
    ref = zipfile.ZipFile(reference)

    slides = sorted(
        (n for n in src.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", n)),
        key=lambda n: int(re.search(r"(\d+)", n.split("/")[-1]).group(1)),
    )

    # Media added to the repaired package, keyed by the hash of its bytes so
    # that a repeated image is stored once.
    media = {}
    media_order = []
    for n in sorted(src.namelist()):
        if n.startswith("ppt/media/"):
            data = src.read(n)
            h = hashlib.md5(data).hexdigest()
            media[h] = ("ppt/media/" + Path(n).name, data)
            media_order.append(h)

    stats = {"linked": 0, "repaired": 0}
    parts = {}

    for name in slides:
        slide = int(re.search(r"(\d+)", name.split("/")[-1]).group(1))
        xml = src.read(name).decode("utf-8")
        rels = read_rels(src, slide)

        ref_name = "ppt/slides/slide%d.xml" % slide
        ref_frames = picture_frames(ref.read(ref_name).decode("utf-8")) \
            if ref_name in ref.namelist() else []

        blocks = list(PICT_RE.finditer(xml))
        out_xml = xml
        # Work back to front so the offsets of the earlier frames stay valid.
        for index in range(len(blocks) - 1, -1, -1):
            m = blocks[index]
            frame = picture_frames(m.group(0))
            frame = frame[0] if frame else {}
            if media_of(src, slide, frame):
                stats["linked"] += 1
                continue
            if index >= len(ref_frames):
                continue
            want = media_of(ref, slide, ref_frames[index])
            if not want:
                continue
            h = hashlib.md5(want).hexdigest()
            if h not in media:
                number = len(media_order) + 1
                part = "ppt/media/image%d.png" % number
                media[h] = (part, want)
                media_order.append(h)
            part = media[h][0]
            rid = next_rid(rels)
            rels[rid] = (NS_REL + "/image", "../" + part.replace("ppt/", ""))

            old_blip = frame["blip"] or "<a:blip/>"
            new_blip = '<a:blip r:embed="%s"/>' % rid
            start = m.start()
            abs_start = start + m.group(0).find(old_blip)
            out_xml = (out_xml[:abs_start] + new_blip
                       + out_xml[abs_start + len(old_blip):])
            stats["repaired"] += 1

        # Rewrite the slide's relationships: keep the layout and the links
        # that resolve, drop the ones that point nowhere, add the new ones.
        rel_name = "ppt/slides/_rels/slide%d.xml.rels" % slide
        lines = [
            '<Relationship Id="%s" Type="%s" Target="%s"/>' % (rid, typ, target)
            for rid, (typ, target) in sorted(rels.items(), key=lambda kv: kv[0])
            if not (typ.endswith("/image") and (not target or target.upper() == "NULL"))
        ]
        parts[rel_name] = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            + "".join(lines) + "</Relationships>"
        ).encode("utf-8")
        parts[name] = out_xml.encode("utf-8")

    # Write the repaired package: every part of the original, with the fixed
    # slides and relationships swapped in and the media added.
    written = set()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as out:
        for item in src.infolist():
            if item.filename in written:
                continue
            if item.filename.startswith("ppt/media/"):
                # Every media part is written below, from the `media` map.
                continue
            written.add(item.filename)
            if item.filename in parts:
                out.writestr(item.filename, parts[item.filename])
            else:
                out.writestr(item.filename, src.read(item.filename))
        for name, data in parts.items():
            if name not in written:
                written.add(name)
                out.writestr(name, data)
        for h in media_order:
            part, data = media[h]
            if part not in written:
                written.add(part)
                out.writestr(part, data)

    src.close()
    ref.close()
    return stats


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    source = Path(sys.argv[1]).resolve()
    output = Path(sys.argv[2]).resolve()
    if not source.exists():
        print("no such file: %s" % source)
        return 1
    if not REFERENCE.exists():
        print("reference deck missing: %s" % REFERENCE)
        return 1
    stats = repair(source, output, REFERENCE)
    print("already linked: %d" % stats["linked"])
    print("repaired:       %d" % stats["repaired"])
    print("written:        %s" % output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
