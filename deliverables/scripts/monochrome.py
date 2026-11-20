#!/usr/bin/env python3
"""Make an OOXML file monochrome.

A Word or PowerPoint file carries two kinds of colour. The first is
explicit -- every fill, every font colour, written as a literal
``srgbClr`` or ``w:color`` value. The second is inherited: the file's
theme declares a colour scheme, and the built-in styles reference that
scheme by name, so a document that never writes a colour in hex can still
render in colour. That second kind is the one that survives a naive
palette edit, because python-docx and python-pptx copy their default
Office theme into the file they save.

This module rewrites both kinds: every literal colour that is not already
grey is converted to its luminance grey, and the theme's colour scheme is
replaced with a monochrome one. The conversion is by luminance, so the
relative lightness of the original palette survives -- a blue accent and a
red accent become two different greys rather than the same one.

Usage:
    python3 deliverables/scripts/monochrome.py FILE.docx [FILE.pptx ...]
"""
from __future__ import annotations

import re
import shutil
import sys
import zipfile
from pathlib import Path


def _luminance(hexv: str) -> str:
    """The ITU-R BT.601 luma of a hex colour, as a hex grey."""
    r, g, b = (int(hexv[i:i + 2], 16) for i in (0, 2, 4))
    y = round(0.299 * r + 0.587 * g + 0.114 * b)
    y = max(0, min(255, y))
    return f"{y:02X}{y:02X}{y:02X}"


#: The colours that survive the pass. The accent is the institute's own
#: purple, the colour of the emblem: it is the one hue in the deck, it marks
#: the title, the table heads, the hero number and the verdict band, and it
#: carries no meaning that a grey could not.
ACCENT = "291972"


def _keep_or_grey(hexv: str, keep: frozenset[str]) -> str:
    """The colour to write: unchanged for the accent, a grey for the rest."""
    if hexv.upper() in keep:
        return hexv
    return _luminance(hexv)


def _grey_hex(m: re.Match, keep: frozenset[str] = frozenset()) -> str:
    hexv = m.group(1)
    if hexv[0:2] == hexv[2:4] == hexv[4:6]:
        return m.group(0)          # already grey
    return m.group(0).replace(hexv, _keep_or_grey(hexv, keep))


#: The literal colours, matched only where they are colours. The Word
#: colour element is matched as a whole so that the ``w:val`` of, say, a
#: font size is never touched.
_LITERAL = [
    re.compile(r'srgbClr val="([0-9A-Fa-f]{6})"'),
    re.compile(r'(<w:color\b[^>]*?w:val=")([0-9A-Fa-f]{6})(")'),
    re.compile(r'(w:fill=")([0-9A-Fa-f]{6})(")'),
    re.compile(r'(<a:solidFill>\s*<a:srgbClr val=")([0-9A-Fa-f]{6})(")'),
]

#: The theme's colour scheme, replaced wholesale.
_CLR_SCHEME = re.compile(r"<a:clrScheme.*?</a:clrScheme>", re.S)

_MONO_SCHEME = (
    '<a:clrScheme name="Monochrome">'
    '<a:dk1><a:srgbClr val="000000"/></a:dk1>'
    '<a:lt1><a:srgbClr val="FFFFFF"/></a:lt1>'
    '<a:dk2><a:srgbClr val="3A3A3A"/></a:dk2>'
    '<a:lt2><a:srgbClr val="F2F2F2"/></a:lt2>'
    '<a:accent1><a:srgbClr val="6E6E6E"/></a:accent1>'
    '<a:accent2><a:srgbClr val="555555"/></a:accent2>'
    '<a:accent3><a:srgbClr val="808080"/></a:accent3>'
    '<a:accent4><a:srgbClr val="3A3A3A"/></a:accent4>'
    '<a:accent5><a:srgbClr val="999999"/></a:accent5>'
    '<a:accent6><a:srgbClr val="BFBFBF"/></a:accent6>'
    '<a:hlink><a:srgbClr val="000000"/></a:hlink>'
    '<a:folHlink><a:srgbClr val="000000"/></a:folHlink>'
    '</a:clrScheme>'
)


def _grey_part(name: str, data: bytes, keep: frozenset[str] = frozenset()) -> bytes:
    """Rewrite one entry of the package.

    Only the XML is rewritten. Every other entry --- the embedded images ---
    is copied byte for byte, because decoding a PNG as text and encoding it
    back replaces its high bytes with the replacement character, and the
    image in the title page of the departmental report was silently
    corrupted that way before this was fixed.
    """
    if not name.endswith(".xml"):
        return data
    text = data.decode("utf-8", "replace")
    text = _CLR_SCHEME.sub(_MONO_SCHEME, text)
    for pat in _LITERAL:
        if pat.groups == 3:
            text = pat.sub(lambda m: m.group(1) + _keep_or_grey(m.group(2), keep)
                           + m.group(3), text)
        else:
            text = pat.sub(lambda m: _grey_hex(m, keep), text)
    return text.encode("utf-8")


def to_monochrome(path: str | Path, keep=()) -> tuple[int, int]:
    """Rewrite the file in place. Returns (colours converted, theme slots).

    The colours named in `keep` are left as they are. The accent is the one
    hue a deck may carry, and it is the emblem's own colour.
    """
    p = Path(path)
    if not p.exists():
        return 0, 0
    keep = frozenset(h.upper() for h in keep)
    tmp = p.with_suffix(p.suffix + ".mono")
    n_colours = 0
    n_slots = 0
    with zipfile.ZipFile(p) as src, zipfile.ZipFile(
            tmp, "w", zipfile.ZIP_DEFLATED) as dst:
        for item in src.infolist():
            # The entry is read before it is written, because writestr
            # mutates the ZipInfo it is given -- and that ZipInfo belongs to
            # the archive being read, so reading it afterwards would seek to
            # the wrong place.
            original = src.read(item.filename)
            data = _grey_part(item.filename, original, keep)
            # Every entry that is not XML must come out byte for byte. An
            # embedded image decoded as text and encoded back loses its
            # high bytes, and the title-page logo of the departmental
            # report was corrupted exactly that way.
            if not item.filename.endswith(".xml") and data != original:
                raise RuntimeError(
                    f"the monochrome pass altered {item.filename}, which it "
                    f"must not touch")
            if data != original:
                n_colours += sum(1 for _ in re.finditer(
                    r'srgbClr val="[0-9A-Fa-f]{6}"',
                    data.decode("utf-8", "replace")))
                n_slots += 1
            dst.writestr(item, data)
    shutil.move(str(tmp), str(p))
    return n_colours, n_slots


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: monochrome.py FILE [FILE ...]")
        return 2
    for arg in sys.argv[1:]:
        n, s = to_monochrome(arg)
        print(f"  [monochrome] {Path(arg).name}: {s} part(s) rewritten")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
