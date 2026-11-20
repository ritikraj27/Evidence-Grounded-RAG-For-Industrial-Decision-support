#!/usr/bin/env python3
"""Fetch an authentic industrial corpus from the eCFR, and split it into sections.

Why the eCFR
-------------
The thesis's corpora are Wikipedia articles *about* industrial engineering.
They are encyclopaedic prose: uniform register, no binding requirement, no
revision history, no numeric tolerance that an engineer has to comply with.
That is the corpus artefact threat T10 in `research/08_direction_check.md`, and
it is the reason the cross-category generalisation claim (RO6) is only half
closed. This module fetches the alternative: authentic regulatory documents
that an industrial engineer actually consults, in which the load-bearing text
is a numeric limit, an acceptance criterion, or a requirement that changes
when the rule is amended.

The Electronic Code of Federal Regulations is the right source for four
reasons that bear directly on the research:

1. **It is authentic.** These are the regulations themselves, not documents
   *about* regulations. A 29 CFR 1910.119 requirement is what a plant has to
   comply with.
2. **It is public domain.** US government work carries no copyright, so the
   corpus can be redistributed with the thesis without a licence question.
3. **It is tabular.** 29 CFR 1910 alone carries 274 ruling-line tables --
   PEL tables, exposure-limit tables, footnote tables. This matters for RO2:
   the modality quota is a design move about tables, and a corpus with no
   tables cannot test it. The focus corpus's quota result was null partly
   because there was nothing for the quota to move.
4. **It has a version history.** The eCFR versioner serves any part as it
   stood on any past date, and the text carries the Federal Register
   amendment that produced it. That is what makes RO4 -- contradiction
   detection -- measurable on a real corpus rather than on a synthetic one.

The versioner serves a whole part in one request, and splits it into
sections locally. A per-section request is refused for some sections (the
versioner answers "No matching content found" for identifiers that resolve
only through their part), so the part-level fetch is the reliable form.

Usage
-----
    fetch_ecfr.py fetch --title 29 --part 1910 --date 2026-06-01
    fetch_ecfr.py build --title 29 --part 1910 --date 2026-06-01 \
        --category occupational_safety --out impl/data/corpus_industrial

`fetch` caches the raw XML under `data/_ecfr_raw/` (the leading underscore
keeps it out of the corpus, because `ingest_corpus` skips underscore
directories). `build` converts the cached XML into one markdown file per
section, under the category directory.
"""
from __future__ import annotations

import argparse
import gzip
import json
import re
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "_ecfr_raw"

#: The versioner's base URL. Its API is documented at
#: https://www.ecfr.gov/developers/documentation/api/v1 .
BASE = "https://www.ecfr.gov/api/versioner/v1"

#: Titles, for the corpus manifest.
TITLE_NAMES = {
    10: "Code of Federal Regulations, Title 10 -- Energy",
    29: "Code of Federal Regulations, Title 29 -- Labor",
    40: "Code of Federal Regulations, Title 40 -- Protection of the Environment",
    49: "Code of Federal Regulations, Title 49 -- Transportation",
}


# --------------------------------------------------------------------------
# fetching
# --------------------------------------------------------------------------
def _request(url: str, tries: int = 8) -> bytes:
    """GET a URL, with retries and gzip handling.

    The versioner refuses requests that do not advertise a compressed
    response ("This endpoint requires response compression"), so the
    Accept-Encoding header is mandatory rather than an optimisation.

    It also returns 502 and 503 fairly often on the larger parts. Those are
    transient, and the retry has to be patient enough to ride them out: a
    part-level fetch is the only reliable form (the versioner answers "No
    matching content found" for a per-section request on identifiers that
    resolve only through their part), so there is no smaller request to fall
    back to.
    """
    req = urllib.request.Request(
        url,
        headers={
            "Accept-Encoding": "gzip, deflate",
            "User-Agent": "MTP-research/1.0 (academic corpus fetch)",
        },
    )
    last = None
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                payload = resp.read()
                if resp.headers.get("Content-Encoding") == "gzip":
                    payload = gzip.decompress(payload)
                return payload
        except urllib.error.HTTPError as exc:
            last = exc
            # 404 is a definitive answer: this identifier does not resolve.
            if exc.code == 404:
                raise
            time.sleep(min(5 * (attempt + 1), 45))
        except Exception as exc:  # pragma: no cover - network flakiness
            last = exc
            time.sleep(min(5 * (attempt + 1), 45))
    raise RuntimeError(f"GET failed after {tries} tries: {url} ({last})")


def fetch_part_xml(title: int, part: str, date: str, refresh: bool = False,
                   subpart: str | None = None) -> Path:
    """Fetch one part as it stood on `date`, and cache the raw XML."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    suffix = f"_sp{subpart}" if subpart else ""
    stem = f"t{title}_p{part}{suffix}_{date}"
    path = RAW_DIR / f"{stem}.xml"
    if path.exists() and path.stat().st_size > 1000 and not refresh:
        return path
    url = f"{BASE}/full/{date}/title-{title}.xml?part={part}"
    if subpart:
        url += f"&subpart={subpart}"
    print(f"[ecfr] GET {url}", flush=True)
    payload = _request(url)
    path.write_bytes(payload)
    print(f"[ecfr] cached {path.name} ({len(payload):,} bytes)", flush=True)
    return path


def fetch_structure(title: int, date: str) -> dict:
    """The title's section structure as it stood on `date`."""
    url = f"{BASE}/structure/{date}/title-{title}.json"
    print(f"[ecfr] GET {url}", flush=True)
    return json.loads(_request(url))


# --------------------------------------------------------------------------
# XML -> markdown
# --------------------------------------------------------------------------
#: Elements whose text is furniture rather than content. Dropping them keeps
#: the retrieved evidence free of the citation apparatus that the earlier
#: measurement found to be the source of every false numeric conflict
#: ("Dettmer H., 1998" was read as a quantity).
_DROP = {"FTREF", "PSPACE", "AUTH", "SOURCE", "CITA", "LDRFIG", "LDRWK",
         "EFFDNOT", "RESERVED", "MARGIN", "HD"}

#: Inline elements that carry formatting only.
_INLINE = {"I", "E", "SU", "SUB", "EMPH", "HIGHLIGHT"}


def _inline_text(el: ET.Element) -> str:
    """The text of an element, with inline markup flattened.

    `<E T="01">` is emphasis and `<SU>` is a superscript; both are rendered as
    plain text, because the retriever compares words and the markup only adds
    tokens that match nothing.
    """
    parts: list[str] = []
    if el.text:
        parts.append(el.text)
    for child in el:
        if child.tag in _DROP:
            continue
        parts.append(_inline_text(child))
        if child.tail:
            parts.append(child.tail)
    return "".join(parts)


def _clean(text: str) -> str:
    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _table_to_markdown(tbl: ET.Element) -> str:
    """A ruling-line table as a markdown table.

    A merged cell (``colspan``) is rendered as a single column and the other
    columns of that row are left empty, which keeps the markdown rectangular.
    An irregular markdown table confuses both the LLM and the tokenizer.
    """
    rows: list[list[str]] = []
    header: list[str] = []
    for tr in tbl.findall(".//TR"):
        cells: list[str] = []
        is_head = False
        for cell in tr:
            if cell.tag not in ("TD", "TH"):
                continue
            if cell.tag == "TH":
                is_head = True
            span = int(cell.get("colspan", "1") or "1")
            value = _clean(_inline_text(cell))
            cells.append(value)
            for _ in range(span - 1):
                cells.append("")
        if not cells:
            continue
        if is_head and not header:
            header = cells
        else:
            rows.append(cells)
    if not header:
        if not rows:
            return ""
        header = rows.pop(0)
    width = max([len(header)] + [len(r) for r in rows])
    header = header + [""] * (width - len(header))
    out = ["| " + " | ".join(h.replace("|", "/") for h in header) + " |",
           "|" + "|".join(["---"] * width) + "|"]
    for r in rows:
        r = r + [""] * (width - len(r))
        out.append("| " + " | ".join(c.replace("|", "/") for c in r) + " |")
    return "\n".join(out)


def _caption_of(tbl: ET.Element) -> str:
    cap = tbl.find("CAPTION")
    if cap is None:
        return ""
    return _clean(_inline_text(cap))


def _blocks(el: ET.Element) -> list[str]:
    """The markdown blocks of an element's children, in document order."""
    out: list[str] = []
    for child in el:
        tag = child.tag
        if tag in _DROP:
            continue
        if tag == "P":
            text = _clean(_inline_text(child))
            if text:
                out.append(text)
        elif tag in ("FP", "FP-2", "FP-3"):
            text = _clean(_inline_text(child))
            if text:
                out.append(text)
        elif tag == "NOTE":
            body = _blocks(child)
            if body:
                out.append("> " + body[0])
                out.extend(body[1:])
        elif tag == "EXTRACT":
            body = _blocks(child)
            out.extend("> " + b for b in body)
        elif tag == "TABLE":
            md = _table_to_markdown(child)
            if md:
                caption = _caption_of(child)
                # The caption and the table stay in one block, so a caller
                # that paginates a long table can repeat the caption with
                # every page.
                out.append((caption + "\n" + md) if caption else md)
        elif tag in ("HD1", "HD2", "HD3", "HD4", "HED"):
            text = _clean(_inline_text(child))
            if text:
                out.append("#### " + text)
        elif tag == "FTNT":
            body = _blocks(child)
            if body:
                out.append("> " + body[0])
        elif tag in ("DIV", "DIV1", "DIV2", "DIV3", "DIV4", "DIV5", "DIV6",
                     "DIV7", "DIV8", "DIV9"):
            out.extend(_blocks(child))
    return out


def split_sections(xml_path: Path) -> list[dict]:
    """Split a cached part XML into its sections.

    Each section carries the subpart it sits in, so a caller can assign
    categories from the document structure without a second request to the
    structure endpoint.
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()
    sections: list[dict] = []

    def walk(node: ET.Element, subpart: str) -> None:
        tag = node.tag
        if tag == "DIV6":
            # The subpart node may be the root of a subpart-level fetch, so
            # the node's own tag is what carries the subpart identifier.
            subpart = node.get("N") or subpart
        elif tag == "DIV8":
            ident = node.get("N") or ""
            head_el = node.find("HEAD")
            head = _clean(_inline_text(head_el)) if head_el is not None else ""
            body = _blocks(node)
            if body:
                sections.append({"identifier": ident, "head": head,
                                 "body": body, "subpart": subpart})
            return
        for child in node:
            walk(child, subpart)

    walk(root, "")
    return sections


def section_markdown(section: dict, category: str) -> str:
    """One section as a markdown document the ingester can chunk."""
    head = section["head"] or f"§ {section['identifier']}"
    lines = [f"<!-- category: {category} -->", "", f"## {head}", ""]
    lines.extend(section["body"])
    lines.append("")
    return "\n".join(lines)


# --------------------------------------------------------------------------
# building
# --------------------------------------------------------------------------
def build(title: int, part: str, date: str, category: str, out: Path,
          min_words: int = 120, max_words: int = 6000) -> dict:
    """Convert a cached part into one markdown file per section.

    Sections outside the word-count band are skipped. A section shorter than
    `min_words` cannot support a question with a real answer in it; a section
    longer than `max_words` is usually a schedule of forms or a long
    appendix, and would make one document dominate the corpus.
    """
    path = fetch_part_xml(title, part, date)
    sections = split_sections(path)
    out.mkdir(parents=True, exist_ok=True)
    kept: list[dict] = []
    for sec in sections:
        md = section_markdown(sec, category)
        words = len(md.split())
        if not (min_words <= words <= max_words):
            continue
        fname = f"{sec['identifier']}.md"
        (out / fname).write_text(md, encoding="utf-8")
        kept.append({"identifier": sec["identifier"], "head": sec["head"],
                     "words": words, "file": fname,
                     "tables": sum(1 for b in sec["body"] if b.startswith("|"))})
    manifest = {
        "title": title,
        "title_name": TITLE_NAMES.get(title, f"Title {title}"),
        "part": part,
        "date": date,
        "category": category,
        "source_url": f"https://www.ecfr.gov/current/title-{title}/part-{part}",
        "n_sections": len(kept),
        "total_words": sum(k["words"] for k in kept),
        "sections": kept,
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2),
                                       encoding="utf-8")
    print(f"[ecfr] {title} CFR {part} @ {date}: {len(kept)} sections, "
          f"{manifest['total_words']:,} words -> {out}", flush=True)
    return manifest


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    f = sub.add_parser("fetch", help="cache a part's raw XML")
    f.add_argument("--title", type=int, required=True)
    f.add_argument("--part", required=True)
    f.add_argument("--date", required=True)
    f.add_argument("--subpart", default=None)
    f.add_argument("--refresh", action="store_true")

    b = sub.add_parser("build", help="convert a cached part into markdown")
    b.add_argument("--title", type=int, required=True)
    b.add_argument("--part", required=True)
    b.add_argument("--date", required=True)
    b.add_argument("--category", required=True)
    b.add_argument("--out", required=True)
    b.add_argument("--min-words", type=int, default=120)
    b.add_argument("--max-words", type=int, default=6000)

    args = ap.parse_args()
    if args.cmd == "fetch":
        p = fetch_part_xml(args.title, args.part, args.date, refresh=args.refresh,
                           subpart=args.subpart)
        print(p)
        return 0

    build(args.title, args.part, args.date, args.category, Path(args.out),
          min_words=args.min_words, max_words=args.max_words)
    return 0


if __name__ == "__main__":
    sys.exit(main())
