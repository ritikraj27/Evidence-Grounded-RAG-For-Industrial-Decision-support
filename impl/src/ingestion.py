"""Document ingestion and modality-aware chunking (design move D2's prerequisite).

Why modality matters at ingestion time
---------------------------------------
A PDF is a *visual* object: a page is a layout of text blocks, ruled tables,
and figures that only become a table once you understand where the ruling
lines are. A naive text extractor throws that structure away and hands the
retriever a flat wall of prose, in which a table's rows have been flattened
into unreadable text and a chart's numbers have been lost entirely.

In an industrial corpus this is fatal, because the *binding* requirements
live in tables: an EOQ, a safety-stock rule, an acceptance tolerance, a
Incoterms matrix. If ingestion destroys the table, no amount of retrieval
cleverness downstream can recover it.

So ingestion runs in two stages.

**Stage 1 -- structural parsing.** PyMuPDF exposes the page as a tree of
blocks with bounding boxes, plus a table detector that finds ruled regions
and, critically, the *cells* within them. We classify every block:

    text   -- prose paragraph
    table  -- overlaps a detected table region
    chart  -- an image or vector drawing region (figure/plot)

**Stage 2 -- modality-specific serialisation.** Each modality is serialised
into a form the *text* encoder can actually compare against a question:

    text   -> the prose, lightly normalised
    table  -> a markdown rendering: header row, then one row per line, with a
              leading caption naming the document, page and table, because a
              bare "| sku | qty |" table is nearly indistinguishable from
              every other table in the corpus
    chart  -> the figure's caption and any text drawn on it, plus a
              "FIGURE" marker. If the PDF stores the figure only as pixels,
              the surrounding caption text is still retrieved, which is why
              caption-first is the right fallback when no vision model is
              available.

Chunking rules
--------------
* Text chunks target ~120 words with ~30 words of overlap. The overlap
  prevents a sentence that straddles a boundary from being lost; the target
  is short enough that a 10-chunk context still covers real content and long
  enough that each chunk is a coherent unit.
* Table chunks are never split. A table is the atomic unit of a specification.
* Every chunk carries metadata: document id, page, modality, section, and the
  table/figure caption. The metadata is what makes the category pre-filter
  and the modality quota possible.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path

from .config import CORPUS_DIR

#: Target chunk size in words, and the overlap between consecutive chunks.
CHUNK_WORDS = 120
CHUNK_OVERLAP_WORDS = 30

_WS_RE = re.compile(r"[ \t]+")
_MULTI_NL_RE = re.compile(r"\n{3,}")


@dataclass
class Chunk:
    """One retrievable unit of evidence."""

    chunk_id: str
    doc_id: str
    text: str
    modality: str  # "text" | "table" | "chart"
    page: int
    section: str = ""
    caption: str = ""
    #: The industrial category this chunk belongs to. Populated from the
    #: corpus manifest or the `<!-- category: X -->` file header.
    category: str = "general"
    meta: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "chunk_id": self.chunk_id,
            "doc_id": self.doc_id,
            "text": self.text,
            "modality": self.modality,
            "page": self.page,
            "section": self.section,
            "caption": self.caption,
            "category": self.category,
            "meta": self.meta,
        }


def _normalise(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = _WS_RE.sub(" ", text)
    text = _MULTI_NL_RE.sub("\n\n", text)
    return text.strip()


#: Wikipedia's "edit" and "edit source" links are navigation chrome, not
#: content: they head every section of every article and say nothing about
#: the subject. Left in, they occupy about 30% of the corpus text and
#: appear verbatim in the retrieved evidence, which is what a reader of the
#: case study sees first.
_WIKI_EDIT_PAIR_RE = re.compile(
    r"\[\[edit\]\([^)]*\)\s*\|\s*\[edit source\]\([^)]*\)\]", re.IGNORECASE)
_WIKI_EDIT_RE = re.compile(r"\[\[edit\]\([^)]*\)\]", re.IGNORECASE)
#: A markdown link, rendered as its anchor text -- which is what a human
#: reads. Leaving the URL in puts `(/wiki/Standard_cost_accounting
#: "Standard cost accounting")` in the middle of the evidence.
_MD_LINK_RE = re.compile(r"\[([^\]\n]{1,150})\]\([^)\n]{0,400}\)")
#: A bare wiki link, rendered as its text.
_WIKILINK_RE = re.compile(r"\[\[([^\]\n]{1,150})\]\]")
#: A citation marker: the markdown converter turns Wikipedia's reference
#: superscripts into "7(#cite_note-little-graves-7)".
_CITE_REF_RE = re.compile(r"\d*\(#cite[^)]*\)")
#: Emphasis, rendered as the emphasised text.
_EMPHASIS_RE = re.compile(r"(?<![\w*])\*([^*\n]{1,120})\*(?![\w*])")
#: A stray double space left by a removed marker.
_DOUBLE_SPACE_RE = re.compile(r"[ \t]{2,}")
#: An image with no alt text: an infobox or navigation icon that carries no
#: information a reader could use.
_EMPTY_IMG_RE = re.compile(r"!\[\]\([^)]*\)")


def _strip_wiki_chrome(text: str) -> str:
    """Remove Wikipedia's navigation chrome and render links as text."""
    text = _WIKI_EDIT_PAIR_RE.sub("", text)
    text = _WIKI_EDIT_RE.sub("", text)
    text = _WIKILINK_RE.sub(r"\1", text)
    text = _MD_LINK_RE.sub(r"\1", text)
    text = _EMPHASIS_RE.sub(r"\1", text)
    text = _CITE_REF_RE.sub("", text)
    text = _EMPTY_IMG_RE.sub("", text)
    text = _DOUBLE_SPACE_RE.sub(" ", text)
    return text


def chunk_text_block(text: str, doc_id: str, page: int, section: str, start_index: int) -> list[Chunk]:
    """Split a prose block into overlapping word-window chunks."""
    words = _normalise(_strip_wiki_chrome(text)).split()
    if not words:
        return []
    chunks: list[Chunk] = []
    step = max(CHUNK_WORDS - CHUNK_OVERLAP_WORDS, 1)
    i = 0
    idx = start_index
    while i < len(words):
        window = words[i : i + CHUNK_WORDS]
        if len(window) < 12 and chunks:
            # Merge a short tail into the previous chunk rather than emitting
            # a fragment that would be retrieved as its own unit.
            prev = chunks[-1]
            prev.text = prev.text + " " + " ".join(window)
            break
        body = " ".join(window)
        cid = f"{doc_id}::p{page}::t{idx}"
        chunks.append(
            Chunk(
                chunk_id=cid,
                doc_id=doc_id,
                text=body,
                modality="text",
                page=page,
                section=section,
                meta={"word_count": len(window), "start_word": i},
            )
        )
        idx += 1
        i += step
    return chunks


def table_to_markdown(table) -> str:
    """Serialise a PyMuPDF table object into markdown.

    ``table.extract()`` returns a list of rows of cell strings, with None for
    empty cells. We forward-fill merged cells (a merged header spans several
    columns) so the markdown stays rectangular -- an irregular markdown table
    confuses both the LLM and the tokenizer.
    """
    try:
        rows = table.extract()
    except Exception:
        return ""
    if not rows:
        return ""
    width = max(len(r) for r in rows)
    rows = [list(r) + [""] * (width - len(r)) for r in rows]
    # Forward-fill horizontally merged cells.
    filled: list[list[str]] = []
    for row in rows:
        carry = ""
        new_row = []
        for cell in row:
            cell = (cell or "").strip()
            if not cell:
                cell = carry
            else:
                carry = cell
            new_row.append(cell)
        filled.append(new_row)
    out = ["| " + " | ".join(filled[0]) + " |", "|" + "|".join(["---"] * width) + "|"]
    for row in filled[1:]:
        out.append("| " + " | ".join(row) + " |")
    return "\n".join(out)


def ingest_pdf(path: Path, doc_id: str | None = None) -> list[Chunk]:
    """Parse a PDF into modality-tagged chunks.

    PyMuPDF's ``find_tables`` uses the ruling lines (or, failing that, the
    text alignment) to find table regions. Every block whose bounding box
    overlaps a table region is classified as table content; everything else
    that is mostly prose stays text.
    """
    import pymupdf

    doc_id = doc_id or hashlib.sha256(path.name.encode()).hexdigest()[:10]
    category = path.parent.name if path.parent.name not in ("corpus", "") else "general"
    chunks: list[Chunk] = []
    index = 0

    with pymupdf.open(path) as doc:
        for pno, page in enumerate(doc, start=1):
            try:
                found = page.find_tables()
                table_bboxes = [t.bbox for t in found.tables]
            except Exception:
                found = []
                table_bboxes = []

            table_regions = []
            for t in found.tables:
                md = table_to_markdown(t)
                if not md:
                    continue
                table_regions.append((t.bbox, md))

            def in_table(bbox) -> bool:
                for tb, _ in table_regions:
                    if not (bbox[2] < tb[0] or bbox[0] > tb[2] or bbox[3] < tb[1] or bbox[1] > tb[3]):
                        return True
                return False

            # Tables first, so their cells are not also emitted as text.
            for (tb, md) in table_regions:
                caption = f"[TABLE] {doc_id} page {pno}"
                body = f"{caption}\n{md}"
                chunks.append(
                    Chunk(
                        chunk_id=f"{doc_id}::p{pno}::tbl{index}",
                        doc_id=doc_id,
                        text=body,
                        modality="table",
                        page=pno,
                        section="table",
                        caption=caption,
                        meta={"n_rows": md.count("\n") - 1},
                    )
                )
                index += 1

            for block in page.get_text("blocks"):
                x0, y0, x1, y1, text = block[0], block[1], block[2], block[3], block[4]
                if not text or not text.strip():
                    continue
                if in_table((x0, y0, x1, y1)):
                    continue
                # A block that is mostly non-alphabetic is a figure label or a
                # chart annotation, not prose.
                alpha = sum(ch.isalpha() for ch in text)
                if alpha / max(len(text), 1) < 0.55:
                    caption = f"[FIGURE] {doc_id} page {pno}"
                    chunks.append(
                        Chunk(
                            chunk_id=f"{doc_id}::p{pno}::fig{index}",
                            doc_id=doc_id,
                            text=f"{caption}\n{_normalise(text)}",
                            modality="chart",
                            page=pno,
                            section="figure",
                            caption=caption,
                            meta={},
                        )
                    )
                    index += 1
                    continue
                for ch in chunk_text_block(text, doc_id, pno, "body", index):
                    chunks.append(ch)
                    index += 1
    for ch in chunks:
        ch.category = category
    return chunks


def ingest_markdown(path: Path, doc_id: str | None = None) -> list[Chunk]:
    """Ingest a markdown or text file, honouring `## ` headings as sections
    and markdown pipe-tables as table chunks.

    A `<!-- category: X -->` header comment in the file sets the industrial
    category for every chunk produced from it.
    """
    doc_id = doc_id or path.stem
    raw = path.read_text(encoding="utf-8", errors="ignore")

    category = "general"
    m = re.match(r"\s*<!--\s*category:\s*([a-z0-9_\- ]+)\s*-->", raw, re.IGNORECASE)
    if m:
        category = m.group(1).strip().replace(" ", "_")
        raw = raw[m.end() :]
    # The category may also come from the parent directory name.
    if category == "general" and path.parent.name not in ("corpus",):
        category = path.parent.name

    lines = raw.splitlines()

    sections: list[tuple[str, list[str]]] = []
    current_title = "body"
    current: list[str] = []
    for line in lines:
        if line.strip().startswith("## "):
            if current:
                sections.append((current_title, current))
            current_title = line.strip()[3:].strip()
            current = []
        else:
            current.append(line)
    if current:
        sections.append((current_title, current))

    chunks: list[Chunk] = []
    index = 0

    # Figures. A markdown image carries its alt text, which in a technical
    # article is the figure's caption -- the same text a human reads to
    # understand what the chart shows. Treating it as a distinct `chart`
    # chunk is what an OCR-free pipeline does, and it is what gives the
    # modality quota something to balance against.
    for m in re.finditer(r"!\[[^\]]*\]\(([^)]*)\)", raw):
        alt = m.group(0)
        url = m.group(1)
        if url.startswith("http") and "upload.wikimedia.org" not in url:
            continue
        caption = f"[FIGURE] {doc_id} :: {alt}"
        chunks.append(
            Chunk(
                chunk_id=f"{doc_id}::fig{index}",
                doc_id=doc_id,
                text=f"{caption}\n{alt}",
                modality="chart",
                page=1,
                section="figure",
                caption=caption,
                meta={"source": "markdown_image"},
            )
        )
        index += 1

    for title, sec_lines in sections:
        buf: list[str] = []
        in_table = False
        table_buf: list[str] = []
        for line in sec_lines:
            is_table_row = line.strip().startswith("|")
            if is_table_row and not in_table:
                if buf:
                    for ch in chunk_text_block("\n".join(buf), doc_id, 1, title, index):
                        chunks.append(ch)
                        index += 1
                    buf = []
                in_table = True
                table_buf = []
            if in_table:
                table_buf.append(line)
                if not line.strip().startswith("|"):
                    in_table = False
                    md = _strip_wiki_chrome("\n".join(table_buf)).strip()
                    if md:
                        caption = f"[TABLE] {doc_id} section {title}"
                        chunks.append(
                            Chunk(
                                chunk_id=f"{doc_id}::p1::tbl{index}",
                                doc_id=doc_id,
                                text=f"{caption}\n{md}",
                                modality="table",
                                page=1,
                                section=title,
                                caption=caption,
                                meta={},
                            )
                        )
                        index += 1
                continue
            buf.append(line)
        if buf:
            for ch in chunk_text_block("\n".join(buf), doc_id, 1, title, index):
                chunks.append(ch)
                index += 1
        if in_table and table_buf:
            md = _strip_wiki_chrome("\n".join(table_buf)).strip()
            if md:
                caption = f"[TABLE] {doc_id} section {title}"
                chunks.append(
                    Chunk(
                        chunk_id=f"{doc_id}::p1::tbl{index}",
                        doc_id=doc_id,
                        text=f"{caption}\n{md}",
                        modality="table",
                        page=1,
                        section=title,
                        caption=caption,
                        meta={},
                    )
                )
                index += 1
    for ch in chunks:
        ch.category = category
    return chunks


def ingest_corpus(corpus_dir: Path = CORPUS_DIR) -> list[Chunk]:
    """Ingest every supported file under `corpus_dir`, recursively.

    Directories whose name begins with an underscore are skipped. They are
    where retired documents are parked, and ingesting them would silently
    add their chunks to the corpus -- which is how a corpus of 46 documents
    once indexed 48.
    """
    chunks: list[Chunk] = []
    if not corpus_dir.exists():
        return chunks
    for path in sorted(corpus_dir.rglob("*")):
        if not path.is_file() or path.name.startswith("."):
            continue
        if any(part.startswith("_") for part in path.relative_to(corpus_dir).parts[:-1]):
            continue
        suffix = path.suffix.lower()
        try:
            if suffix == ".pdf":
                chunks.extend(ingest_pdf(path))
            elif suffix in (".md", ".txt"):
                chunks.extend(ingest_markdown(path))
        except Exception as exc:  # pragma: no cover - defensive
            print(f"[ingest] FAILED {path.name}: {exc}")
    return chunks


def corpus_statistics(chunks: list[Chunk]) -> dict:
    """Modality composition of the corpus.

    The Sept 2026 report recorded 2.3% chart and 7.1% table content for the
    634-chunk supply-chain corpus. This statistic is what made the
    modality-quota experiment return a null result: there simply were not
    enough table or chart chunks for a quota to move the needle. It is worth
    reporting for any corpus, because it predicts whether design move D2 can
    possibly have an effect.
    """
    from collections import Counter

    counts = Counter(c.modality for c in chunks)
    total = len(chunks) or 1
    words = sum(len(c.text.split()) for c in chunks)
    ids = Counter(c.chunk_id for c in chunks)
    return {
        "n_chunks": len(chunks),
        "n_documents": len({c.doc_id for c in chunks}),
        "n_categories": len({c.category for c in chunks}),
        # A chunk id is doc-scoped, so a repeated id means the same document
        # was ingested twice. That silently inflates the chunk count, splits
        # a document across two categories so the category pre-filter sees
        # only half of it, and leaks the document into both halves of the
        # cross-category transfer split. It must be zero.
        "duplicate_chunk_ids": sum(v - 1 for v in ids.values() if v > 1),
        "by_modality": dict(counts),
        "share_text": counts.get("text", 0) / total,
        "share_table": counts.get("table", 0) / total,
        "share_chart": counts.get("chart", 0) / total,
        "total_words": words,
        "mean_words_per_chunk": words / total,
    }
