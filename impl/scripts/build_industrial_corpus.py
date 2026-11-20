#!/usr/bin/env python3
"""Assemble the authentic industrial corpus (RO6) from the eCFR.

The thesis's existing corpora are Wikipedia articles *about* industrial
engineering. This builds the alternative the direction check asked for: a
corpus of authentic regulatory documents, in which the load-bearing text is a
numeric limit, an acceptance criterion, or a requirement that changes when the
rule is amended.

Four categories, each a different regulatory regime rather than a different
Wikipedia article:

``occupational_safety``
    OSHA general-industry standards: walking-working surfaces, exit routes,
    hazardous materials, personal protective equipment, materials handling,
    machinery and machine guarding, hand and portable powered tools, welding.

``process_safety``
    The regimes that manage *catastrophic* risk: OSHA's process safety
    management standard together with its permit-required confined spaces and
    lockout/tagout rules (29 CFR 1910 subpart G), and EPA's risk management
    programme rule (40 CFR 112).

``environmental_control``
    New source performance standards (40 CFR 60) with their emission-limit
    tables -- cement plants, petroleum refineries, storage vessels, smelters,
    grain elevators, metallic mineral processing -- and OSHA's general
    environmental controls (1910 subpart J).

``hazmat_transport``
    DOT's preparation, classification and packaging rules for hazardous
    materials (49 CFR 173), which is where the *quantity* limits a
    practitioner has to comply with live.

The categories matter for RO6 in one specific way: a threshold fitted on one
regulatory regime and applied to another is the cross-category transfer
question, and the regimes differ in register, in required specificity, and in
how much of the binding content is tabular.

Everything here is public domain: US federal regulations are works of the US
government and carry no copyright.

Two corpus-construction decisions worth stating, because both are visible in
the corpus statistics:

* **Over-long sections are split, not dropped.** 29 CFR 1910.119 (process
  safety management) is twenty thousand words, and 1910.146 (permit-required
  confined spaces) is comparable. A word-count cap that dropped them would
  drop the two most decision-relevant standards in the corpus, so a section
  longer than the cap is split into consecutive documents instead. Each
  carries the parent section's identifier, so the manifest can recover the
  grouping.
* **Procedural sections are excluded.** The sections that describe how a rule
  is made, challenged or exempted carry no requirement a practitioner has to
  comply with, and they are the ones that most resemble the encyclopaedic
  register the thesis is trying to move away from. The exclusion list and the
  reason for each entry are in `EXCLUDE`.

Usage:
    build_industrial_corpus.py --out impl/data/corpus_industrial
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from fetch_ecfr import (  # noqa: E402
    fetch_part_xml,
    split_sections,
    section_markdown,
)

DATE = "2026-06-01"

#: (title, part, subparts). The subpart list is empty for a whole-part fetch.
#: A source is fetched at subpart granularity when the subpart list is given
#: and the part is large, because the versioner returns 502 and 503 fairly
#: often on the larger parts and a smaller request is a smaller thing to
#: fail.
SOURCES = [
    # OSHA general industry, fetched whole. Its subparts do not line up with
    # the regimes: the confined-spaces and lockout/tagout rules sit in
    # subpart J ("General Environmental Controls"), the hazard communication
    # rule sits in subpart Z, and the versioner's XML nests the subpart Z
    # sections without a subpart tag at all. The CFR *numbering* groups by
    # subject, so the category is assigned by identifier range instead.
    (29, "1910", set()),
    # EPA's risk management programme rule: the process-safety regime on the
    # environmental side.
    (40, "112", set()),
    # New source performance standards: the industrial process regimes.
    (40, "60", {"A", "D", "F", "J", "L", "M", "DD", "LL", "OOO", "VV"}),
    # DOT hazardous materials: classification, packaging, and the quantity
    # limits.
    (49, "173", {"B", "C", "E", "F"}),
]

#: 29 CFR 1910 by identifier range. The CFR numbering is organised by
#: subject, and this is where the four regimes separate:
#:
#: * 1910.1000-1099 -- toxic and hazardous substances: the air-contaminant
#:   exposure limits, the asbestos, lead and cadmium standards, the
#:   respiratory-protection appendices. Environmental exposure control.
#: * 1910.1200-1201 -- hazard communication: the standard every workplace
#:   uses to classify and communicate chemical hazards.
#: * 1910.119-120 and 1910.146-147 -- process safety management, hazardous
#:   waste operations, permit-required confined spaces and lockout/tagout.
#:   The standards that manage catastrophic risk.
#:
#: Everything else in part 1910 is routine occupational safety.
RANGE_1910 = [
    (1000, 1099, "environmental_control"),
    (1200, 1299, "process_safety"),
    (119, 120, "process_safety"),
    (146, 147, "process_safety"),
]

#: Categories for the parts fetched whole.
PART_CATEGORY = {
    ("40", "112"): "process_safety",
    ("40", "60"): "environmental_control",
    ("49", "173"): "hazmat_transport",
}

#: A section shorter than this cannot carry a question with a real answer in
#: it.
MIN_WORDS = 150

#: A section longer than this is split into consecutive documents.
MAX_WORDS = 3500

#: Sections excluded whatever their subpart, with the reason. Only genuinely
#: procedural sections are here: tables of contents, effective-date notices
#: and the reporting apparatus. Definitions are *kept* -- they are the source
#: of most answerable questions in a regulatory corpus.
EXCLUDE = {
    "1910.33": "table of contents; no requirement attached",
    "1910.122": "table of contents; no requirement attached",
    "1910.98": "effective dates; procedural",
    "1910.1201": "table of contents; no requirement attached",
    "40.60.7": "procedural; records and reports",
    "40.60.8": "procedural; reporting",
    "40.60.9": "procedural",
    "40.60.24": "procedural; notifications",
    "40.60.30": "procedural; petitions for review",
    "40.60.31": "procedural",
}


#: A table with more rows than this is paginated, with the header repeated.
#:
#: The reason is mechanical. The cross-encoder reads 512 tokens, so a
#: 6,900-word table is truncated to roughly its first twenty rows and the
#: answer to a question about row 400 is not in the text the reranker ever
#: sees. A table that cannot be retrieved is a table the modality quota
#: cannot help with, and the framework's own measurement of D2 would be
#: measuring the tokenizer rather than the quota.
#:
#: The word cap matters as much as the row cap: the cross-encoder's window
#: is 512 tokens, which is roughly 380 English words, so a page has to fit
#: in that whatever its rows look like.
MAX_TABLE_ROWS = 30
MAX_TABLE_WORDS = 300


def _split_table_block(block: str) -> list[str]:
    """Paginate one table block, repeating the header on every page."""
    lines = block.splitlines()
    if len(lines) < 3:
        return [block]
    # The caption, when there is one, is the first line. It is not a table
    # row, so it has to be set aside before the table is recognised.
    caption = ""
    start = 0
    if not lines[0].lstrip().startswith("|"):
        caption = lines[0]
        start = 1
    if len(lines) - start < 3:
        return [block]
    header = lines[start:start + 2]
    rows = lines[start + 2:]
    if not header[0].lstrip().startswith("|"):
        return [block]
    if len(rows) <= MAX_TABLE_ROWS:
        return [block]
    pages: list[list[str]] = []
    current: list[str] = []
    current_words = 0
    for row in rows:
        words = len(row.split())
        if current and (len(current) >= MAX_TABLE_ROWS
                        or current_words + words > MAX_TABLE_WORDS):
            pages.append(current)
            current, current_words = [], 0
        current.append(row)
        current_words += words
    if current:
        pages.append(current)
    out: list[str] = []
    for i, page in enumerate(pages):
        body = "\n".join(header + page)
        if caption:
            label = caption if i == 0 else f"{caption} (continued)"
            body = f"{label}\n{body}"
        out.append(body)
    return out


def _split_blocks(blocks: list[str], max_words: int) -> list[list[str]]:
    """Split a section's blocks into consecutive groups of at most
    `max_words` words.

    A single block longer than the cap stays whole: cutting a paragraph in
    half would separate a requirement from the condition it qualifies under,
    which is worse for retrieval than a long document.
    """
    expanded: list[str] = []
    for block in blocks:
        expanded.extend(_split_table_block(block))
    groups: list[list[str]] = []
    current: list[str] = []
    current_words = 0
    for block in expanded:
        words = len(block.split())
        if current and current_words + words > max_words:
            groups.append(current)
            current, current_words = [], 0
        current.append(block)
        current_words += words
    if current:
        groups.append(current)
    return groups


def _section_documents(section: dict, category: str) -> list[dict]:
    """One section as one or more corpus documents."""
    groups = _split_blocks(section["body"], MAX_WORDS)
    out: list[dict] = []
    for i, group in enumerate(groups):
        # Blocks are separated by a blank line. The ingester ends a table
        # chunk at the first line that is not a table row, so a blank line
        # between blocks is what keeps one document's table from running into
        # the next one's caption.
        md = "\n".join([
            f"<!-- category: {category} -->", "",
            f"## {section['head']}", "",
            "\n\n".join(group), "",
        ])
        words = len(md.split())
        if words < MIN_WORDS:
            continue
        suffix = "" if len(groups) == 1 else f"_part{i + 1}"
        out.append({
            "identifier": section["identifier"] + suffix,
            "parent": section["identifier"],
            "head": section["head"],
            "category": category,
            "subpart": section.get("subpart", ""),
            "words": words,
            "n_table_blocks": sum(1 for b in group if b.startswith("|")),
            "markdown": md,
        })
    return out


def _numeric_tail(identifier: str) -> int | None:
    """The number in a CFR identifier: "1910.1200" -> 1200."""
    tail = identifier.rsplit(".", 1)[-1]
    digits = "".join(ch for ch in tail if ch.isdigit())
    return int(digits) if digits else None


def _category_for(title: int, part: str, section: dict) -> str | None:
    """The category a section belongs to, or None when it is out of scope."""
    ident = section["identifier"]
    if (str(title), part) == ("29", "1910"):
        number = _numeric_tail(ident)
        if number is not None:
            for low, high, category in RANGE_1910:
                if low <= number <= high:
                    return category
        return "occupational_safety"
    return PART_CATEGORY.get((str(title), part))


def _select(documents: list[dict], budget_words: int | None
            ) -> list[dict]:
    """Trim the corpus to a word budget, evenly within each category.

    The selection is an **evenly spaced** subsample of each category's
    documents in identifier order, not the top-N by any quality measure. That
    matters: a corpus chosen by a quality filter is a corpus chosen for the
    property being measured, and the retrieval numbers on it would be a
    statement about the filter as much as about the corpus.

    The budget is per category and proportional to what each category
    contributes, so trimming does not silently reweight the regimes.
    """
    if not budget_words:
        return documents
    by_category: dict[str, list[dict]] = {}
    for d in documents:
        by_category.setdefault(d["category"], []).append(d)
    total = sum(d["words"] for d in documents) or 1
    kept: list[dict] = []
    for category, docs in sorted(by_category.items()):
        budget = int(budget_words * sum(d["words"] for d in docs) / total)
        docs = sorted(docs, key=lambda d: d["identifier"])
        if sum(d["words"] for d in docs) <= budget:
            kept.extend(docs)
            continue
        # Evenly spaced: take every k-th document, which keeps the
        # identifier range and the subject mix of the category.
        running = 0
        step = 1
        while True:
            running = 0
            chosen = []
            for i, d in enumerate(docs):
                if i % step == 0:
                    chosen.append(d)
                    running += d["words"]
                if running > budget:
                    break
            if running <= budget or step > len(docs):
                kept.extend(chosen)
                break
            step += 1
    return kept


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", required=True)
    ap.add_argument("--date", default=DATE)
    ap.add_argument("--max-words", type=int, default=None,
                    help="trim the corpus to this many words, evenly within "
                         "each category")
    ap.add_argument("--dry-run", action="store_true",
                    help="report the corpus shape without writing it")
    args = ap.parse_args()
    out = Path(args.out)

    documents: list[dict] = []
    seen: set[str] = set()

    for title, part, subparts in SOURCES:
        if subparts:
            paths = [fetch_part_xml(title, part, args.date, subpart=sp)
                     for sp in sorted(subparts)]
        else:
            paths = [fetch_part_xml(title, part, args.date)]
        kept: dict[str, int] = {}
        for path in paths:
            for section in split_sections(path):
                ident = section["identifier"]
                if ident in seen or ident in EXCLUDE:
                    continue
                if subparts and section.get("subpart", "") not in subparts:
                    continue
                category = _category_for(title, part, section)
                if category is None:
                    continue
                docs = _section_documents(section, category)
                if not docs:
                    continue
                for d in docs:
                    documents.append(dict(d))
                    seen.add(ident)
                    kept[category] = kept.get(category, 0) + 1
        for category, n in sorted(kept.items()):
            print(f"[corpus] {title} CFR {part} -> {category}: {n} documents",
                  flush=True)

    if args.max_words:
        before = len(documents)
        documents = _select(documents, args.max_words)
        print(f"[corpus] trimmed {before} -> {len(documents)} documents "
              f"({sum(d['words'] for d in documents):,} words)", flush=True)

    for d in documents:
        if args.dry_run:
            continue
        target = out / d["category"]
        target.mkdir(parents=True, exist_ok=True)
        (target / f"{d['identifier']}.md").write_text(
            d["markdown"], encoding="utf-8")

    manifest = {
        "name": "InduSight industrial regulatory corpus",
        "date": args.date,
        "source": "Electronic Code of Federal Regulations (eCFR), "
                  "https://www.ecfr.gov",
        "licence": "public domain (US government work)",
        "n_documents": len(documents),
        "total_words": sum(d["words"] for d in documents),
        "by_category": {},
        "documents": sorted(
            ({k: v for k, v in d.items() if k != "markdown"} for d in documents),
            key=lambda d: d["identifier"]),
    }
    for d in documents:
        s = manifest["by_category"].setdefault(
            d["category"], {"n_documents": 0, "words": 0})
        s["n_documents"] += 1
        s["words"] += d["words"]
    if not args.dry_run:
        out.mkdir(parents=True, exist_ok=True)
        (out / "manifest.json").write_text(json.dumps(manifest, indent=2),
                                           encoding="utf-8")
    print(f"[corpus] {manifest['n_documents']} documents, "
          f"{manifest['total_words']:,} words -> {out}")
    for cat, s in sorted(manifest["by_category"].items()):
        print(f"    {cat:24s} {s['n_documents']:4d} docs  {s['words']:>9,} words")
    return 0


if __name__ == "__main__":
    sys.exit(main())
