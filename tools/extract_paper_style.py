#!/usr/bin/env python3
"""Extract an aggregate *structural* style profile from a reference paper.

Contract (from the skills that call it)::

    paper-write/SKILL.md:47-58, paper-plan/SKILL.md:45-58,
    paper-poster/SKILL.md:40-48, paper-slides/SKILL.md:41-48,
    paper-illustration/SKILL.md:82-86, grant-proposal/SKILL.md:53-57,
    paper-writing/SKILL.md:54-58::

        CACHE=$(python3 tools/extract_paper_style.py --source "<source>")
        case $? in
          0) ;;                          # use $CACHE/style_profile.md
          2) echo "warning: style-ref skipped (missing optional dep)" >&2 ;;
          3) echo "error: --style-ref source failed; aborting draft" >&2 ;;
          *) echo "error: helper failed unexpectedly; aborting draft" >&2 ;;
        esac

So:

* stdout carries **only** the cache directory path (nothing else), and the
  cache always contains ``style_profile.md`` (plus ``style_profile.json`` and
  the extracted ``source.txt``).
* exit ``0`` - success.
* exit ``2`` - a required optional dependency is missing (for example no PDF
  text extraction library). The caller is expected to *skip* the style ref.
* exit ``3`` - the ``--source`` could not be resolved, fetched or parsed. The
  caller is expected to *abort*.
* exit ``1`` - usage error / unexpected internal failure.

Accepted ``--source`` values (paper-write/SKILL.md:60,
paper-illustration/SKILL.md:95):

* a local TeX directory or ``.tex``/``.bib`` file,
* a local ``.pdf`` file,
* an arXiv id (``2501.12345`` or ``arxiv:2501.12345``),
* an ``http(s)`` URL.

Overleaf URLs and bare project ids are rejected - clone the project locally
first and pass the local path.

The profile is deliberately **aggregate**: section ordering, theorem density,
caption length, sentence cadence, math display ratio, citation style and
figure density. It never carries prose, claims or terminology from the source,
because the calling skills copy from it as *structural* guidance only.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.request

EXIT_OK = 0
EXIT_USAGE = 1
EXIT_MISSING_DEP = 2
EXIT_SOURCE_FAILED = 3

USER_AGENT = "extract_paper_style/1.0 (Claude Code skill helper)"
HTTP_TIMEOUT = 30


class SourceError(Exception):
    """The --source could not be resolved, fetched or parsed (exit 3)."""


class MissingDependency(Exception):
    """An optional third-party dependency is unavailable (exit 2)."""


# --------------------------------------------------------------------------
# LaTeX helpers
# --------------------------------------------------------------------------

SECTION_COMMANDS = (
    "chapter",
    "section",
    "subsection",
    "subsubsection",
    "paragraph",
    "subparagraph",
)

# LaTeX sectioning command -> coarse level used in the profile.
SECTION_LEVEL = {
    "chapter": "section",
    "section": "section",
    "subsection": "subsection",
    "subsubsection": "subsubsection",
    "paragraph": "paragraph",
    "subparagraph": "paragraph",
}

THEOREM_ENVS = (
    "theorem",
    "lemma",
    "proposition",
    "corollary",
    "conjecture",
    "definition",
    "remark",
    "observation",
    "claim",
    "example",
    "problem",
)

PROOF_ENVS = ("proof",)

FIGURE_ENVS = ("figure", "figure*", "subfigure", "wrapfigure")

TABLE_ENVS = ("table", "table*", "longtable")

CITE_COMMANDS = (
    "cite",
    "citep",
    "citet",
    "citeauthor",
    "citeyear",
    "citealp",
    "citealt",
    "parencite",
    "textcite",
    "autocite",
    "footcite",
    "supercite",
    "smartcite",
    "nocite",
)

MATH_ENVS = (
    "equation",
    "equation*",
    "align",
    "align*",
    "gather",
    "gather*",
    "eqnarray",
    "eqnarray*",
    "multline",
    "multline*",
    "displaymath",
    "flalign",
    "flalign*",
    "alignat",
    "alignat*",
    "split",
    "dmath",
    "dmath*",
)

NUMERIC_BIB_STYLES = (
    "plain",
    "abbrv",
    "unsrt",
    "unsrtnat",
    "ieeetran",
    "ieeetranfull",
    "ieeetranb",
    "elsarticle-num",
    "apsrev4-1",
    "apsrev4-2",
    "acm",
    "svjour3",
    "llncs",
)

AUTHOR_YEAR_BIB_STYLES = (
    "apalike",
    "authoryear",
    "plainnat",
    "abbrvnat",
    "alphabet",
    "alpha",
    "unsrtnat",
    "harvard",
    "chicago",
)


def strip_comments(text: str) -> str:
    """Remove unescaped ``%`` comments, honouring ``\\%``."""
    out = []
    for line in text.split("\n"):
        match = re.search(r"(?<!\\)%", line)
        if match:
            line = line[: match.start()]
        out.append(line)
    return "\n".join(out)


def remove_math(text: str) -> str:
    """Blank out inline and display math so prose statistics are not skewed."""
    text = re.sub(r"\\\[.*?\\\]", " ", text, flags=re.S)
    text = re.sub(r"\\\(.*?\\\)", " ", text, flags=re.S)
    text = re.sub(r"\$[^$]*\$", " ", text)
    env_alt = "|".join(re.escape(env) for env in MATH_ENVS)
    text = re.sub(
        r"\\begin\{(?:" + env_alt + r")\}.*?\\end\{(?:" + env_alt + r")\}",
        " ",
        text,
        flags=re.S,
    )
    return text


def extract_braced(text: str, start: int):
    """Return ``(content, index_after_closing_brace)`` for the brace at *start*."""
    depth = 0
    index = start
    length = len(text)
    while index < length:
        char = text[index]
        if char == "\\":
            index += 2
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start + 1 : index], index + 1
        index += 1
    return text[start + 1 :], length


def word_list(text: str):
    """Crude but stable word tokenizer for prose statistics."""
    text = re.sub(r"\\[a-zA-Z@]+\*?", " ", text)
    text = re.sub(r"[^A-Za-z0-9'\-]+", " ", text)
    return [word for word in text.split() if re.search(r"[A-Za-z]", word)]


def percentile(values, fraction):
    if not values:
        return 0
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = fraction * (len(ordered) - 1)
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def mean(values):
    if not values:
        return 0.0
    return float(sum(values)) / len(values)


def round_or_none(value, digits=2):
    if value is None:
        return None
    return round(float(value), digits)


# --------------------------------------------------------------------------
# TeX analysis
# --------------------------------------------------------------------------


def _drop_block(text: str, env_names) -> str:
    alt = "|".join(re.escape(name) for name in env_names)
    return re.sub(
        r"\\begin\{(?:" + alt + r")\}.*?\\end\{(?:" + alt + r")\}",
        " ",
        text,
        flags=re.S,
    )


def analyze_tex_files(paths):
    """Analyse one or more .tex files and return the metric dictionary."""
    metrics = {
        "kind": "tex",
        "files": [],
        "sections": [],
        "section_levels": {},
        "theorem_environments": {},
        "proof_environments": 0,
        "figure_count": 0,
        "subfigure_count": 0,
        "table_count": 0,
        "caption_lengths": [],
        "caption_count": 0,
        "citation_commands": 0,
        "citation_keys": 0,
        "citation_clusters": [],
        "inline_math": 0,
        "display_math": 0,
        "bibliography_style": None,
        "citation_command_kinds": {},
        "word_count": 0,
        "paragraph_lengths": [],
        "sentence_lengths": [],
    }

    for path in paths:
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as handle:
                raw = handle.read()
        except OSError as exc:
            raise SourceError("cannot read %s: %s" % (path, exc))
        metrics["files"].append(os.path.basename(path))
        text = strip_comments(raw)

        # --- structure -----------------------------------------------------
        # One combined scan so the section list keeps document order.
        section_pattern = re.compile(
            r"\\(" + "|".join(SECTION_COMMANDS) + r")\*?\s*\{"
        )
        for match in section_pattern.finditer(text):
            command = match.group(1)
            content, _ = extract_braced(text, match.end() - 1)
            title = " ".join(word_list(content))
            level = SECTION_LEVEL.get(command, "section")
            metrics["sections"].append({"level": level, "title": title})
            metrics["section_levels"][level] = metrics["section_levels"].get(level, 0) + 1

        for env in THEOREM_ENVS:
            count = len(re.findall(r"\\begin\{" + re.escape(env) + r"\*?\}", text))
            if count:
                metrics["theorem_environments"][env] = count
        for env in PROOF_ENVS:
            metrics["proof_environments"] += len(
                re.findall(r"\\begin\{" + re.escape(env) + r"\*?\}", text)
            )

        for env in FIGURE_ENVS:
            count = len(re.findall(r"\\begin\{" + re.escape(env) + r"\*?\}", text))
            if env == "subfigure":
                metrics["subfigure_count"] += count
            elif env == "wrapfigure":
                metrics["figure_count"] += count
            else:
                metrics["figure_count"] += count
        for env in TABLE_ENVS:
            count = len(re.findall(r"\\begin\{" + re.escape(env) + r"\*?\}", text))
            if env in ("table", "table*"):
                metrics["table_count"] += count

        # --- captions ------------------------------------------------------
        for match in re.finditer(r"\\caption\s*\{", text):
            content, _ = extract_braced(text, match.end() - 1)
            metrics["caption_count"] += 1
            metrics["caption_lengths"].append(len(word_list(content)))

        # --- citations -----------------------------------------------------
        for command in CITE_COMMANDS:
            pattern = re.compile(r"\\" + command + r"\s*(?:\[[^\]]*\])?\s*(?:\[[^\]]*\])?\s*\{")
            for match in pattern.finditer(text):
                metrics["citation_commands"] += 1
                metrics["citation_command_kinds"][command] = (
                    metrics["citation_command_kinds"].get(command, 0) + 1
                )
                content, _ = extract_braced(text, match.end() - 1)
                keys = [key.strip() for key in content.split(",") if key.strip()]
                metrics["citation_clusters"].append(len(keys))
                metrics["citation_keys"] += len(keys)

        bibstyle = re.search(r"\\bibliographystyle\s*\{([^}]*)\}", text)
        if bibstyle:
            metrics["bibliography_style"] = bibstyle.group(1).strip()
        elif re.search(r"\\usepackage(?:\[[^\]]*\])?\{[^}]*\bnatbib\b", text):
            metrics["bibliography_style"] = "natbib"

        # --- math ----------------------------------------------------------
        metrics["inline_math"] += len(re.findall(r"(?<!\\)\$[^$]*?(?<!\\)\$", text))
        metrics["display_math"] += len(re.findall(r"\\\[", text))
        for env in MATH_ENVS:
            metrics["display_math"] += len(
                re.findall(r"\\begin\{" + re.escape(env) + r"\}", text)
            )

        # --- prose ---------------------------------------------------------
        prose = remove_math(text)
        prose = re.sub(r"\\(?:sub)*section\*?\s*\{[^}]*\}", " ", prose)
        prose = re.sub(r"\\(?:label|includegraphics|bibliography|bibliographystyle)\s*\{[^}]*\}", " ", prose)
        prose = _drop_block(prose, ("figure", "figure*", "subfigure", "wrapfigure"))
        prose = _drop_block(prose, ("table", "table*", "longtable"))
        prose = _drop_block(prose, ("thebibliography",))
        prose = _drop_block(prose, ("algorithm", "algorithm*"))

        paragraphs = []
        for chunk in re.split(r"\n\s*\n", prose):
            if len(word_list(chunk)) >= 5:
                paragraphs.append(chunk)
        for chunk in paragraphs:
            metrics["paragraph_lengths"].append(len(word_list(chunk)))
            # Split on the raw text: tokenising first would destroy the
            # sentence boundaries.
            for sentence in split_sentences(chunk):
                count = len(word_list(sentence))
                if count:
                    metrics["sentence_lengths"].append(count)


    metrics["word_count"] = sum(metrics["paragraph_lengths"])
    metrics["citation_style"] = _tex_citation_style(metrics)
    return metrics


def _tex_citation_style(metrics):
    kinds = metrics.get("citation_command_kinds") or {}
    if kinds.get("citep") or kinds.get("citet") or kinds.get("parencite") or kinds.get("textcite"):
        return "author-year (natbib-style commands)"
    bibstyle = (metrics.get("bibliography_style") or "").lower()
    for style in AUTHOR_YEAR_BIB_STYLES:
        if style in bibstyle:
            return "author-year (bibliographystyle=%s)" % metrics.get("bibliography_style")
    for style in NUMERIC_BIB_STYLES:
        if style in bibstyle:
            return "numeric (bibliographystyle=%s)" % metrics.get("bibliography_style")
    return "numeric (plain \\cite commands)"


# --------------------------------------------------------------------------
# Plain-text / PDF analysis
# --------------------------------------------------------------------------

HEADING_NUMBERED = re.compile(r"^\s*((?:\d+|[IVXLC]+)(?:\.\d+)*)\.?\s+([A-Z][^\n]{2,70})\s*$")
HEADING_ALL_CAPS = re.compile(r"^\s*([A-Z][A-Z0-9 &/,\-]{3,70})\s*$")
CAPTION_LINE = re.compile(r"^\s*(figure|fig\.?|table|tab\.?)\s*(\d+)\s*[\.:]", re.IGNORECASE)
CITATION_NUMERIC = re.compile(r"\[\s*\d+(?:\s*[,;–-]\s*\d+)*\s*\]")
CITATION_AUTHOR_YEAR = re.compile(r"\b[A-Z][A-Za-z\-]+(?:\s+et\s+al\.)?\s*,?\s*\(?\d{4}[a-z]?\)?")
SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9(\[])")
CJK_SENTENCE_SPLIT = re.compile(r"(?<=[。！？])")
LINE_END = re.compile(r"[.!?。！？][\"')\]]?\s*$")


def split_sentences(text):
    """Split a block of prose into sentences (ASCII and CJK terminators)."""
    pieces = []
    for chunk in CJK_SENTENCE_SPLIT.split(text):
        pieces.extend(SENTENCE_SPLIT.split(chunk))
    return pieces


def flow_paragraphs(text, min_words=12):
    """Group lines into paragraphs for PDF/HTML text, where blank lines are rare."""
    chunks = []
    for block in re.split(r"\n\s*\n", text):
        current = []
        for line in block.split("\n"):
            if not line.strip():
                continue
            current.append(line.strip())
            if LINE_END.search(line.strip()):
                chunk = " ".join(current)
                if len(word_list(chunk)) >= min_words:
                    chunks.append(chunk)
                current = []
        if current:
            chunk = " ".join(current)
            if len(word_list(chunk)) >= min_words:
                chunks.append(chunk)
    return chunks


def _looks_like_heading(line):
    match = HEADING_NUMBERED.match(line)
    if match:
        title = match.group(2).strip()
        if len(title.split()) <= 14:
            return title
    stripped = line.strip()
    if HEADING_ALL_CAPS.match(stripped) and 1 < len(stripped.split()) <= 12:
        return stripped
    return None


def analyze_plain_text(pages, kind, source_label, backend=None):
    """Analyse extracted text (PDF or HTML-stripped text) heuristically."""
    metrics = {
        "kind": kind,
        "source_label": source_label,
        "pages": len(pages),
        "pdf_backend": backend,
        "sections": [],
        "section_levels": {},
        "theorem_environments": {},
        "proof_environments": None,
        "figure_count": 0,
        "subfigure_count": None,
        "table_count": 0,
        "caption_lengths": [],
        "caption_count": 0,
        "citation_commands": 0,
        "citation_keys": 0,
        "citation_clusters": [],
        "inline_math": None,
        "display_math": None,
        "bibliography_style": None,
        "citation_command_kinds": {},
        "word_count": 0,
        "paragraph_lengths": [],
        "sentence_lengths": [],
    }

    full = "\n".join(pages)
    lines = full.split("\n")

    seen_figures = set()
    seen_tables = set()

    for index, line in enumerate(lines):
        heading = _looks_like_heading(line)
        if heading:
            level = "section"
            if re.match(r"^\d+\.\d+", line.strip()):
                level = "subsection"
            metrics["sections"].append({"level": level, "title": heading})
            metrics["section_levels"][level] = metrics["section_levels"].get(level, 0) + 1

        caption = CAPTION_LINE.match(line)
        if caption:
            kindword = caption.group(1).lower().rstrip(".")
            number = caption.group(2)
            if kindword.startswith("fig"):
                seen_figures.add(number)
            else:
                seen_tables.add(number)
            metrics["caption_count"] += 1
            caption_words = len(word_list(line))
            # Captions often wrap; add the following lines until a blank one.
            cursor = index + 1
            while cursor < len(lines) and lines[cursor].strip() and caption_words < 60:
                caption_words += len(word_list(lines[cursor]))
                cursor += 1
            metrics["caption_lengths"].append(caption_words)

    metrics["figure_count"] = len(seen_figures)
    metrics["table_count"] = len(seen_tables)

    numeric_clusters = CITATION_NUMERIC.findall(full)
    metrics["citation_clusters"].extend(len(re.findall(r"\d+", cluster)) for cluster in numeric_clusters)
    metrics["citation_commands"] = len(numeric_clusters) + len(CITATION_AUTHOR_YEAR.findall(full))
    metrics["citation_keys"] = sum(metrics["citation_clusters"]) or metrics["citation_commands"]

    if numeric_clusters:
        metrics["citation_style"] = "numeric (bracketed)"
    elif CITATION_AUTHOR_YEAR.search(full):
        metrics["citation_style"] = "author-year (parenthetical)"
    else:
        metrics["citation_style"] = "undetermined"

    for chunk in flow_paragraphs(full, min_words=12):
        metrics["paragraph_lengths"].append(len(word_list(chunk)))
        for sentence in split_sentences(chunk):
            count = len(word_list(sentence))
            if count:
                metrics["sentence_lengths"].append(count)

    metrics["word_count"] = sum(metrics["paragraph_lengths"])
    return metrics


# --------------------------------------------------------------------------
# PDF / URL / arXiv resolution
# --------------------------------------------------------------------------


def pdf_pages_text(path):
    """Return ``(backend, page_texts)``; raises MissingDependency."""
    reader_cls = None
    backend = None
    try:
        from pypdf import PdfReader as reader_cls  # noqa: N813
        backend = "pypdf"
    except ImportError:
        try:
            from PyPDF2 import PdfReader as reader_cls  # noqa: N813
            backend = "PyPDF2"
        except ImportError:
            reader_cls = None
    if reader_cls is not None:
        reader = reader_cls(path)
        pages = []
        for page in reader.pages:
            try:
                pages.append(page.extract_text() or "")
            except Exception:  # noqa: BLE001 - a bad page must not kill the run
                pages.append("")
        return backend, pages
    try:
        from pdfminer.high_level import extract_text as pdfminer_extract
    except ImportError:
        raise MissingDependency(
            "no PDF text extraction library found; install one of "
            "pypdf, PyPDF2, pdfminer.six (pip install pypdf)"
        )
    return "pdfminer", [pdfminer_extract(path) or ""]


def http_get(url):
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=HTTP_TIMEOUT) as response:
            return response.read()
    except urllib.error.HTTPError as exc:
        raise SourceError("HTTP %s for %s" % (exc.code, url))
    except Exception as exc:  # noqa: BLE001 - network errors are source failures
        raise SourceError("cannot fetch %s: %s" % (url, exc))


def strip_html(text):
    text = re.sub(r"(?is)<(script|style).*?</\1>", " ", text)
    text = re.sub(r"(?s)<!--.*?-->", " ", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    text = (
        text.replace("&nbsp;", " ")
        .replace("&amp;", "&")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&quot;", '"')
        .replace("&#39;", "'")
    )
    return text


def detect_source_kind(source):
    lowered = source.strip()
    if lowered.startswith("http://") or lowered.startswith("https://"):
        if "overleaf.com" in lowered.lower():
            raise SourceError(
                "Overleaf URLs are rejected; clone the project locally "
                "(/overleaf-sync setup <id>) and pass the local clone path"
            )
        return "url"
    if lowered.lower().startswith("arxiv:"):
        return "arxiv"
    if re.match(r"^\d{4}\.\d{4,5}(v\d+)?$", lowered):
        return "arxiv"
    if re.match(r"^[a-z-]+(?:\.[A-Z]{2})?/\d{7}(v\d+)?$", lowered):
        return "arxiv"
    if os.path.exists(lowered):
        if os.path.isdir(lowered):
            return "texdir"
        extension = os.path.splitext(lowered)[1].lower()
        if extension == ".pdf":
            return "pdf"
        if extension in (".tex", ".ltx", ".latex", ".bib", ".txt", ".md"):
            return "tex" if extension != ".txt" else "text"
        return "text"
    if re.match(r"^[A-Za-z0-9_\-]{20,}$", lowered):
        raise SourceError(
            "'%s' looks like a project id, not a path or arXiv id; clone the "
            "project locally and pass the local path" % lowered
        )
    raise SourceError("cannot resolve source: %s" % source)


def collect_tex_files(directory):
    collected = []
    for root, dirs, files in os.walk(directory):
        dirs[:] = sorted(d for d in dirs if not d.startswith("."))
        for name in sorted(files):
            if name.lower().endswith((".tex", ".ltx", ".latex")):
                collected.append(os.path.join(root, name))
    if not collected:
        raise SourceError("no .tex files found under %s" % directory)
    return collected


def order_tex_files(paths):
    """Put the main file first so section ordering follows the document."""
    main_candidates = [p for p in paths if os.path.basename(p).lower() in ("main.tex", "paper.tex", "ms.tex")]
    if main_candidates:
        rest = [p for p in paths if p not in main_candidates]
        return main_candidates + rest
    for path in paths:
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as handle:
                if "\\documentclass" in handle.read(4096):
                    rest = [p for p in paths if p != path]
                    return [path] + rest
        except OSError:
            continue
    return paths


# --------------------------------------------------------------------------
# Profile rendering
# --------------------------------------------------------------------------


def summarise(metrics):
    """Derive the shared statistics from the raw counters."""
    words = metrics.get("word_count") or 0
    per_kw = 1000.0 / words if words else 0.0
    sections = metrics.get("sections") or []
    section_titles = [s.get("title", "") for s in sections if s.get("title")]
    section_count = len(section_titles)

    paragraph_lengths = metrics.get("paragraph_lengths") or []
    sentence_lengths = metrics.get("sentence_lengths") or []
    caption_lengths = metrics.get("caption_lengths") or []

    theorem_total = sum((metrics.get("theorem_environments") or {}).values())
    figure_count = metrics.get("figure_count") or 0
    table_count = metrics.get("table_count") or 0

    subsections = sum(
        1 for s in sections if s.get("level") in ("subsection", "subsubsection")
    )
    sections_at_top = sum(1 for s in sections if s.get("level") == "section")
    top_level_titles = [
        s.get("title", "") for s in sections if s.get("level") == "section" and s.get("title")
    ]

    figure_table_ratio = None
    if table_count:
        figure_table_ratio = round_or_none(figure_count / float(table_count))

    return {
        "word_count": words,
        "section_count": section_count,
        "top_level_section_count": sections_at_top,
        "section_titles": section_titles,
        "section_entries": [
            {"level": item.get("level", "section"), "title": item.get("title", "")}
            for item in sections
        ],
        "top_level_section_titles": top_level_titles,
        "subsections": subsections,
        "subsections_per_section": round_or_none(
            subsections / float(sections_at_top) if sections_at_top else 0.0
        ),
        "paragraph_count": len(paragraph_lengths),
        "paragraph_words_mean": round_or_none(mean(paragraph_lengths)),
        "paragraph_words_median": round_or_none(percentile(paragraph_lengths, 0.5)),
        "paragraph_words_p90": round_or_none(percentile(paragraph_lengths, 0.9)),
        "sentence_count": len(sentence_lengths),
        "sentence_words_mean": round_or_none(mean(sentence_lengths)),
        "sentence_words_median": round_or_none(percentile(sentence_lengths, 0.5)),
        "sentence_words_p90": round_or_none(percentile(sentence_lengths, 0.9)),
        "long_sentence_share": round_or_none(
            sum(1 for length in sentence_lengths if length > 35) / float(len(sentence_lengths))
            if sentence_lengths
            else 0.0
        ),
        "theorem_count": theorem_total,
        "theorem_per_1k_words": round_or_none(theorem_total * per_kw),
        "proof_count": metrics.get("proof_environments"),
        "figure_count": figure_count,
        "table_count": table_count,
        "figure_table_ratio": figure_table_ratio,
        "figures_per_section": round_or_none(
            figure_count / float(sections_at_top) if sections_at_top else 0.0
        ),
        "caption_count": metrics.get("caption_count") or 0,
        "caption_words_mean": round_or_none(mean(caption_lengths)),
        "caption_words_median": round_or_none(percentile(caption_lengths, 0.5)),
        "caption_words_p90": round_or_none(percentile(caption_lengths, 0.9)),
        "citation_count": metrics.get("citation_commands") or 0,
        "citation_keys": metrics.get("citation_keys") or 0,
        "citation_cluster_mean": round_or_none(
            mean(metrics.get("citation_clusters") or []) or None
        ),
        "citations_per_section": round_or_none(
            (metrics.get("citation_commands") or 0) / float(sections_at_top) if sections_at_top else 0.0
        ),
        "citation_style": metrics.get("citation_style"),
        "bibliography_style": metrics.get("bibliography_style"),
        "inline_math": metrics.get("inline_math"),
        "display_math": metrics.get("display_math"),
        "display_per_1k_words": round_or_none((metrics.get("display_math") or 0) * per_kw),
        "display_share_of_math": round_or_none(
            (metrics.get("display_math") or 0)
            / float((metrics.get("display_math") or 0) + (metrics.get("inline_math") or 0))
            if ((metrics.get("display_math") or 0) + (metrics.get("inline_math") or 0))
            else 0.0
        ),
        "source_kind": metrics.get("kind"),
        "pages": metrics.get("pages"),
        "pdf_backend": metrics.get("pdf_backend"),
        "files": metrics.get("files"),
    }


def _fmt(value, suffix=""):
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return ("%g" % value) + suffix
    return str(value) + suffix


def render_profile(summary):
    lines = []
    add = lines.append
    add("# Structural Style Profile")
    add("")
    add("> Aggregate structural measurements of the reference paper. Use them as")
    add("> *structural* guidance only (section count and ordering, theorem density,")
    add("> caption length, sentence cadence, math display ratio, citation style,")
    add("> figure density). Never copy prose, claims, examples or terminology from")
    add("> the source, and never forward this profile to a reviewer or auditor.")
    add("")
    add("- source kind: %s" % _fmt(summary.get("source_kind")))
    if summary.get("files"):
        add("- source files: %s" % ", ".join(summary["files"]))
    if summary.get("pages"):
        add("- pages: %s (text via %s)" % (_fmt(summary.get("pages")), _fmt(summary.get("pdf_backend"))))
    add("- word count (prose): %s" % _fmt(summary.get("word_count")))
    add("")

    add("## 1. Section structure")
    add("")
    add("- top-level sections: %s" % _fmt(summary.get("top_level_section_count")))
    add("- headings counted (incl. subsections): %s" % _fmt(summary.get("section_count")))
    add("- subsections: %s (mean %.2f per top-level section)" % (
        _fmt(summary.get("subsections")), summary.get("subsections_per_section") or 0.0))
    add("- section order:")
    entries = summary.get("section_entries") or []
    if entries:
        for position, entry in enumerate(entries[:60], start=1):
            level = entry.get("level", "section")
            indent = "  " if level == "section" else "    - "
            marker = "" if level == "section" else "(%s) " % level
            add("  %d. %s%s%s" % (position, indent, marker, entry.get("title", "")))
        if len(entries) > 60:
            add("  ... (%d more)" % (len(entries) - 60))
    else:
        add("  (no headings detected)")
    add("")

    add("## 2. Paragraph and sentence cadence")
    add("")
    add("- paragraphs: %s" % _fmt(summary.get("paragraph_count")))
    add("- paragraph length (words): mean %s / median %s / p90 %s" % (
        _fmt(summary.get("paragraph_words_mean")),
        _fmt(summary.get("paragraph_words_median")),
        _fmt(summary.get("paragraph_words_p90"))))
    add("- sentences: %s" % _fmt(summary.get("sentence_count")))
    add("- sentence length (words): mean %s / median %s / p90 %s" % (
        _fmt(summary.get("sentence_words_mean")),
        _fmt(summary.get("sentence_words_median")),
        _fmt(summary.get("sentence_words_p90"))))
    add("- long-sentence share (>35 words): %s" % _fmt(summary.get("long_sentence_share")))
    add("")

    add("## 3. Theorem environment density")
    add("")
    add("- theorem-like environments: %s" % _fmt(summary.get("theorem_count")))
    add("- per 1000 words: %s" % _fmt(summary.get("theorem_per_1k_words")))
    add("- proofs: %s" % _fmt(summary.get("proof_count")))
    add("")

    add("## 4. Math display ratio")
    add("")
    add("- display equations: %s" % _fmt(summary.get("display_math")))
    add("- inline math spans: %s" % _fmt(summary.get("inline_math")))
    add("- display equations per 1000 words: %s" % _fmt(summary.get("display_per_1k_words")))
    add("- display share of all math: %s" % _fmt(summary.get("display_share_of_math")))
    add("")

    add("## 5. Figure and table density")
    add("")
    add("- figures: %s" % _fmt(summary.get("figure_count")))
    add("- tables: %s" % _fmt(summary.get("table_count")))
    add("- figure-to-table ratio: %s" % _fmt(summary.get("figure_table_ratio")))
    add("- figures per section: %s" % _fmt(summary.get("figures_per_section")))
    add("- captions: %s" % _fmt(summary.get("caption_count")))
    add("- caption length (words): mean %s / median %s / p90 %s" % (
        _fmt(summary.get("caption_words_mean")),
        _fmt(summary.get("caption_words_median")),
        _fmt(summary.get("caption_words_p90"))))
    add("")

    add("## 6. Citation style")
    add("")
    add("- style: %s" % _fmt(summary.get("citation_style")))
    add("- bibliography style: %s" % _fmt(summary.get("bibliography_style")))
    add("- citation commands: %s (distinct keys: %s)" % (
        _fmt(summary.get("citation_count")), _fmt(summary.get("citation_keys"))))
    add("- mean keys per citation cluster: %s" % _fmt(summary.get("citation_cluster_mean")))
    add("- citations per section: %s" % _fmt(summary.get("citations_per_section")))
    add("")

    add("## 7. Guidance")
    add("")
    section_count = summary.get("top_level_section_count") or summary.get("section_count")
    if section_count:
        add("- Target roughly %s top-level section(s)." % section_count)
    top_titles = summary.get("top_level_section_titles") or summary.get("section_titles") or []
    if top_titles:
        add("- Prefer this ordering: %s" % " -> ".join(top_titles[:8]))
    if summary.get("theorem_per_1k_words") is not None:
        add("- Theorem density of the reference is %s per 1000 words; match it within an order of magnitude." % summary.get("theorem_per_1k_words"))
    if summary.get("caption_words_mean") is not None:
        add("- Caption length tendency: about %s words." % summary.get("caption_words_mean"))
    if summary.get("sentence_words_mean") is not None:
        add("- Sentence cadence: about %s words per sentence." % summary.get("sentence_words_mean"))
    if summary.get("figure_table_ratio") is not None:
        add("- Figure-to-table ratio: about %s." % summary.get("figure_table_ratio"))
    add("- Keep the venue template's mandated section order; this profile only refines secondary structure.")
    add("")
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def default_root():
    if os.environ.get("ARIS_ROOT"):
        return os.path.abspath(os.environ["ARIS_ROOT"])
    cwd = os.getcwd()
    if os.path.isdir(os.path.join(cwd, ".claude")) or os.path.isdir(os.path.join(cwd, ".aris")):
        return cwd
    return os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def build_parser():
    parser = argparse.ArgumentParser(
        prog="extract_paper_style.py",
        description=(
            "Extract an aggregate structural style profile from a reference paper "
            "(local TeX/PDF, arXiv id or http(s) URL) and print the cache directory "
            "holding style_profile.md on stdout."
        ),
        epilog=(
            "Exit codes: 0 success (stdout = cache dir), 2 missing optional "
            "dependency (caller should skip the style ref), 3 source failed "
            "(caller should abort)."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--source",
        required=True,
        metavar="SRC",
        help="local TeX dir/file, local PDF, arXiv id (2501.12345 or arxiv:2501.12345), or http(s) URL",
    )
    parser.add_argument(
        "--root",
        default=None,
        metavar="DIR",
        help="project root that owns .aris/ (default: $ARIS_ROOT, else the current directory)",
    )
    parser.add_argument(
        "--cache-dir",
        default=None,
        metavar="DIR",
        help="style cache base directory (default: <root>/.aris/style-cache)",
    )
    parser.add_argument(
        "--output",
        default=None,
        metavar="DIR",
        help="exact cache directory to use (overrides --cache-dir)",
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="rebuild the profile even when the cache already exists",
    )
    parser.add_argument(
        "--print-profile",
        action="store_true",
        help="print style_profile.md on stdout instead of the cache path",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="print the metrics JSON on stdout instead of the cache path",
    )
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    root = os.path.abspath(args.root) if args.root else default_root()
    if args.output:
        cache_dir = os.path.abspath(args.output)
    else:
        base = os.path.abspath(args.cache_dir) if args.cache_dir else os.path.join(root, ".aris", "style-cache")
        digest = hashlib.sha256(args.source.strip().encode("utf-8")).hexdigest()[:16]
        cache_dir = os.path.join(base, digest)

    profile_md = os.path.join(cache_dir, "style_profile.md")
    if os.path.isfile(profile_md) and not args.refresh:
        if args.print_profile:
            with open(profile_md, "r", encoding="utf-8") as handle:
                sys.stdout.write(handle.read())
        elif args.json:
            with open(os.path.join(cache_dir, "style_profile.json"), "r", encoding="utf-8") as handle:
                sys.stdout.write(handle.read())
        else:
            sys.stdout.write(cache_dir + "\n")
        return EXIT_OK

    source = args.source.strip()
    kind = detect_source_kind(source)

    metrics = None
    extracted_text = ""
    backend = None

    if kind == "texdir":
        paths = order_tex_files(collect_tex_files(source))
        metrics = analyze_tex_files(paths)
    elif kind == "tex":
        metrics = analyze_tex_files([source])
    elif kind == "pdf":
        backend, pages = pdf_pages_text(source)
        metrics = analyze_plain_text(pages, "pdf", os.path.basename(source), backend)
        extracted_text = "\n".join(pages)
    elif kind == "text":
        with open(source, "r", encoding="utf-8", errors="replace") as handle:
            raw = handle.read()
        extracted_text = raw
        metrics = analyze_plain_text([raw], "text", os.path.basename(source))
    elif kind == "arxiv":
        arxiv_id = source.lower()
        if arxiv_id.startswith("arxiv:"):
            arxiv_id = arxiv_id[len("arxiv:") :]
        os.makedirs(cache_dir, exist_ok=True)
        pdf_path = os.path.join(cache_dir, "source.pdf")
        url = "https://arxiv.org/pdf/%s" % arxiv_id
        payload = http_get(url)
        if not payload.startswith(b"%PDF"):
            raise SourceError("arxiv did not return a PDF for %s" % arxiv_id)
        with open(pdf_path, "wb") as handle:
            handle.write(payload)
        backend, pages = pdf_pages_text(pdf_path)
        metrics = analyze_plain_text(pages, "pdf", "arxiv:%s" % arxiv_id, backend)
        extracted_text = "\n".join(pages)
    elif kind == "url":
        payload = http_get(source)
        if payload.startswith(b"%PDF"):
            os.makedirs(cache_dir, exist_ok=True)
            pdf_path = os.path.join(cache_dir, "source.pdf")
            with open(pdf_path, "wb") as handle:
                handle.write(payload)
            backend, pages = pdf_pages_text(pdf_path)
            metrics = analyze_plain_text(pages, "pdf", source, backend)
            extracted_text = "\n".join(pages)
        else:
            raw = payload.decode("utf-8", errors="replace")
            if "<html" in raw[:2000].lower() or "<!doctype html" in raw[:2000].lower():
                raw = strip_html(raw)
            extracted_text = raw
            metrics = analyze_plain_text([raw], "text", source)
    else:  # pragma: no cover - detect_source_kind only returns the above
        raise SourceError("unsupported source kind: %s" % kind)

    summary = summarise(metrics)
    summary["source"] = source
    summary["generated_at"] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    summary["cache_dir"] = cache_dir

    os.makedirs(cache_dir, exist_ok=True)
    with open(profile_md, "w", encoding="utf-8") as handle:
        handle.write(render_profile(summary))
    with open(os.path.join(cache_dir, "style_profile.json"), "w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=False)
        handle.write("\n")
    if extracted_text:
        with open(os.path.join(cache_dir, "source.txt"), "w", encoding="utf-8") as handle:
            handle.write(extracted_text)

    if args.print_profile:
        with open(profile_md, "r", encoding="utf-8") as handle:
            sys.stdout.write(handle.read())
    elif args.json:
        with open(os.path.join(cache_dir, "style_profile.json"), "r", encoding="utf-8") as handle:
            sys.stdout.write(handle.read())
    else:
        sys.stdout.write(cache_dir + "\n")
    return EXIT_OK


if __name__ == "__main__":
    try:
        sys.exit(main())
    except MissingDependency as exc:
        sys.stderr.write("extract_paper_style.py: missing optional dependency: %s\n" % exc)
        sys.exit(EXIT_MISSING_DEP)
    except SourceError as exc:
        sys.stderr.write("extract_paper_style.py: source failed: %s\n" % exc)
        sys.exit(EXIT_SOURCE_FAILED)
    except KeyboardInterrupt:  # pragma: no cover
        sys.stderr.write("extract_paper_style.py: interrupted\n")
        sys.exit(EXIT_USAGE)
    except Exception as exc:  # noqa: BLE001 - unexpected failures must not look like success
        sys.stderr.write("extract_paper_style.py: unexpected failure: %s\n" % exc)
        sys.exit(EXIT_USAGE)
