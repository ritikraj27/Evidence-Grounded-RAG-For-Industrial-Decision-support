#!/usr/bin/env python3
"""arXiv Atom API tool for the `arxiv` and `research-lit` skills.

Documented interface (see `.claude/skills/arxiv/SKILL.md` and
`.claude/skills/research-lit/SKILL.md`):

    python3 tools/arxiv_fetch.py search "QUERY" --max 10
    python3 tools/arxiv_fetch.py search "id:1706.03762" --max 1
    python3 tools/arxiv_fetch.py download 1706.03762 --dir papers/

Single-paper lookup by id (the `paper` subcommand, also reachable by
passing a bare id as the first argument):

    python3 tools/arxiv_fetch.py paper 1706.03762
    python3 tools/arxiv_fetch.py 1706.03762

Flag-style compatibility interface (see `.claude/skills/arxiv-database/SKILL.md`,
which documents the same Atom API under the name `scripts/arxiv_search.py`):

    python3 tools/arxiv_fetch.py --keywords "a" "b" --max-results 20 \
        --category cs.LG --output results.json

Output is JSON on stdout: a list of paper objects for `search`, a single
paper object (metadata plus `pdf_url`/`abs_url`) for `paper`, a
`{query, result_count, results}` envelope in flag mode, and a per-file
report for `download`.

Requires only the Python standard library. arXiv's Terms of Use ask for no
more than one request every three seconds, so calls are paced accordingly.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

API_URL = "https://export.arxiv.org/api/query"
PDF_URL = "https://arxiv.org/pdf/{arxiv_id}"
ABS_URL = "https://arxiv.org/abs/{arxiv_id}"

USER_AGENT = os.environ.get(
    "ARXIV_USER_AGENT",
    "claude-code-paper-writing-skills/1.0 (arxiv_fetch.py)",
)

# arXiv API Terms of Use: no more than one request every three seconds.
MIN_INTERVAL = 3.0
TIMEOUT = 30

_ATOM = "{http://www.w3.org/2005/Atom}"
_ARXIV = "{http://arxiv.org/schemas/atom}"
_OPENSEARCH = "{http://a9.com/-/spec/opensearch/1.1/}"

# Fields a query may already carry. Anything else is treated as free text.
_FIELD_PREFIXES = ("all:", "ti:", "au:", "abs:", "cat:", "co:", "jr:", "id:", "rn:")

_last_request = 0.0

# Wall-clock stamp of the last arXiv request made by *any* process, so the
# three-second limit also holds across separate invocations of this script
# (the skills call it repeatedly from one bash block).
_THROTTLE_FILE = os.path.join(tempfile.gettempdir(), "arxiv_fetch_last_request")


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _die(message: str, code: int = 1) -> "None":
    """Print an actionable error to stderr and exit non-zero."""
    print("ERROR: {}".format(message), file=sys.stderr)
    raise SystemExit(code)


def _throttle() -> None:
    """Sleep so that consecutive arXiv calls are >= MIN_INTERVAL apart."""
    global _last_request
    wait = MIN_INTERVAL - (time.monotonic() - _last_request)
    try:
        with open(_THROTTLE_FILE, "r") as handle:
            other = float(handle.read().strip() or 0.0)
    except (OSError, ValueError):
        other = 0.0
    wait = max(wait, MIN_INTERVAL - (time.time() - other))
    if wait > 0:
        time.sleep(wait)
    _last_request = time.monotonic()
    try:
        with open(_THROTTLE_FILE, "w") as handle:
            handle.write(str(time.time()))
    except OSError:
        pass


def _http_get(url: str, timeout: int = TIMEOUT) -> bytes:
    """GET a URL with the polite User-Agent, retrying on 429/5xx."""
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    last_error = None
    for attempt in range(3):
        _throttle()
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.read()
        except urllib.error.HTTPError as exc:
            last_error = exc
            if exc.code == 429:
                time.sleep(MIN_INTERVAL * (attempt + 1))
                continue
            if 500 <= exc.code < 600:
                time.sleep(2.0 * (attempt + 1))
                continue
            _die("arXiv API returned HTTP {}: {}".format(exc.code, exc.reason))
        except urllib.error.URLError as exc:
            last_error = exc
            time.sleep(2.0 * (attempt + 1))
    _die("arXiv API unreachable: {}".format(last_error))


def _strip_version(arxiv_id: str) -> str:
    """Drop a trailing version suffix (v1, v2 ...) from an arXiv id."""
    return re.sub(r"v\d+$", "", arxiv_id)


def _normalise_id(raw: str) -> str:
    """Accept a bare id, an abs/pdf URL, or an old-style `cs/0601001` id."""
    raw = raw.strip()
    if not raw:
        return raw
    if "arxiv.org" in raw:
        raw = raw.split("/abs/")[-1].split("/pdf/")[-1]
        raw = raw.split(".pdf")[0]
    return _strip_version(raw)


_NEW_ID_RE = re.compile(r"^\d{4}\.\d{4,5}(v\d+)?$")
_OLD_ID_RE = re.compile(r"^[a-zA-Z][a-zA-Z\-]*(\.[A-Za-z]{2})?/\d{7}(v\d+)?$")


def _looks_like_arxiv_id(value: str) -> bool:
    """True for a bare arXiv id or an arxiv.org abs/pdf URL."""
    value = value.strip()
    if not value or value.startswith("-"):
        return False
    if "arxiv.org" in value:
        return True
    return bool(_NEW_ID_RE.match(value) or _OLD_ID_RE.match(value))


def _text(node) -> str:
    """Collapse whitespace in an Atom text node."""
    if node is None or node.text is None:
        return ""
    return " ".join(node.text.split())


def _entry_to_dict(entry) -> dict:
    """Project an Atom <entry> into the paper dict the skills consume."""
    raw_id = _text(entry.find(_ATOM + "id"))
    arxiv_id = _normalise_id(raw_id)

    title = _text(entry.find(_ATOM + "title"))
    abstract = _text(entry.find(_ATOM + "summary"))
    authors = [
        _text(a.find(_ATOM + "name")) for a in entry.findall(_ATOM + "author")
    ]
    categories = [c.get("term", "") for c in entry.findall(_ATOM + "category")]

    published = _text(entry.find(_ATOM + "published"))
    updated = _text(entry.find(_ATOM + "updated"))

    pdf_url = ""
    for link in entry.findall(_ATOM + "link"):
        href = link.get("href", "")
        if link.get("title") == "pdf" or link.get("rel") == "related":
            pdf_url = href
            break
    if not pdf_url:
        pdf_url = PDF_URL.format(arxiv_id=arxiv_id)

    primary = entry.find(_ATOM + "primary_category")
    primary_category = primary.get("term", "") if primary is not None else (
        categories[0] if categories else ""
    )

    return {
        "id": arxiv_id,
        "arxiv_id": arxiv_id,
        "title": title,
        "authors": authors,
        "abstract": abstract,
        "published": published[:10] if published else "",
        "published_iso": published,
        "updated": updated[:10] if updated else "",
        "updated_iso": updated,
        "categories": categories,
        "primary_category": primary_category,
        "doi": _text(entry.find(_ARXIV + "doi")),
        "comment": _text(entry.find(_ARXIV + "comment")),
        "journal_ref": _text(entry.find(_ARXIV + "journal_ref")),
        "pdf_url": pdf_url,
        "abs_url": ABS_URL.format(arxiv_id=arxiv_id),
    }


def _parse_feed(body: bytes) -> tuple:
    """Parse an Atom feed into (total_results, [paper dicts])."""
    try:
        root = ET.fromstring(body)
    except ET.ParseError as exc:
        _die("could not parse the arXiv Atom response: {}".format(exc))
    total = _text(root.find(_OPENSEARCH + "totalResults"))
    try:
        total = int(total)
    except (TypeError, ValueError):
        total = 0
    papers = [_entry_to_dict(e) for e in root.findall(_ATOM + "entry")]
    return total, papers


def _build_query(
    keywords,
    author=None,
    category=None,
    search_field="all",
) -> str:
    """Build an arXiv `search_query` string from the flag-style interface."""
    terms = []
    for keyword in keywords:
        keyword = keyword.strip()
        if not keyword:
            continue
        if any(keyword.lower().startswith(p) for p in _FIELD_PREFIXES):
            terms.append(keyword)
        else:
            terms.append('{}:"{}"'.format(search_field, keyword))
    if author:
        terms.append('au:"{}"'.format(author.strip()))
    if category:
        terms.append("cat:{}".format(category.strip()))
    if not terms:
        _die("no search terms given")
    return " AND ".join(terms)


def _search(
    search_query=None,
    ids=None,
    max_results=10,
    sort_by="relevance",
    sort_order="descending",
) -> dict:
    """Run one arXiv query. Returns {query, total, papers}."""
    params = {
        "start": 0,
        "max_results": max_results,
        "sortBy": sort_by,
        "sortOrder": sort_order,
    }
    if ids:
        params["id_list"] = ",".join(_normalise_id(i) for i in ids)
        query_label = "id_list=" + params["id_list"]
    else:
        params["search_query"] = search_query
        query_label = search_query

    url = API_URL + "?" + urllib.parse.urlencode(params)
    total, papers = _parse_feed(_http_get(url))
    return {"query": query_label, "total": total, "papers": papers}


def _paper(arxiv_id: str) -> dict:
    """Fetch one paper by id. Returns the paper dict, or {} when not found."""
    result = _search(ids=[arxiv_id], max_results=1)
    papers = result["papers"]
    if not papers:
        _die("arXiv has no paper with id {!r}".format(arxiv_id))
    return papers[0]


def _download(arxiv_ids, directory, min_kb=10) -> list:
    """Download one or more PDFs into `directory`; never overwrite."""
    try:
        os.makedirs(directory, exist_ok=True)
    except OSError as exc:
        _die("could not create download directory {}: {}".format(directory, exc))

    results = []
    for index, raw_id in enumerate(arxiv_ids):
        if index:
            time.sleep(1.0)  # arXiv skill: 1s between consecutive downloads
        arxiv_id = _normalise_id(raw_id)
        target = os.path.join(directory, "{}.pdf".format(arxiv_id.replace("/", "_")))

        if os.path.exists(target):
            results.append(
                {
                    "id": arxiv_id,
                    "status": "exists",
                    "path": target,
                    "size_bytes": os.path.getsize(target),
                    "message": "Already exists: {}".format(target),
                }
            )
            print("Already exists: {}".format(target), file=sys.stderr)
            continue

        url = PDF_URL.format(arxiv_id=arxiv_id)
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                payload = response.read()
        except (urllib.error.URLError, urllib.error.HTTPError) as exc:
            _die("failed to download {}: {}".format(url, exc))

        with open(target, "wb") as handle:
            handle.write(payload)
        size = os.path.getsize(target)

        if size < min_kb * 1024:
            os.remove(target)
            message = "Downloaded file for {} is only {} KB (< {} KB) - deleted".format(
                arxiv_id, size // 1024, min_kb
            )
            results.append(
                {"id": arxiv_id, "status": "too_small", "path": target, "message": message}
            )
            print("WARNING: " + message, file=sys.stderr)
            continue

        message = "Downloaded: {} ({} KB)".format(target, size // 1024)
        results.append(
            {
                "id": arxiv_id,
                "status": "downloaded",
                "path": target,
                "size_bytes": size,
                "message": message,
            }
        )
        print(message, file=sys.stderr)
    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _add_search_options(parser) -> None:
    parser.add_argument("--max", "--max-results", dest="max_results", type=int, default=10,
                        help="Maximum number of results (default: 10)")
    parser.add_argument("--category", help="arXiv category filter, e.g. cs.LG")
    parser.add_argument("--search-field", default="all",
                        choices=["all", "ti", "au", "abs", "cat"],
                        help="Field the free-text query is searched in (default: all)")
    parser.add_argument("--sort-by", default="relevance",
                        choices=["relevance", "lastUpdatedDate", "submittedDate"],
                        help="arXiv sort key (default: relevance)")
    parser.add_argument("--sort-order", default="descending",
                        choices=["ascending", "descending"],
                        help="arXiv sort direction (default: descending)")
    parser.add_argument("--output", "-o", help="Write the JSON to this file instead of stdout")


def _flag_mode_parser() -> argparse.ArgumentParser:
    """Parser for the `arxiv-database` flag-style interface."""
    parser = argparse.ArgumentParser(
        prog="arxiv_fetch.py",
        description="Search arXiv (flag-style interface). "
                    "Prints a {query, result_count, results} JSON envelope.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Example:\n"
               "  python3 tools/arxiv_fetch.py --keywords \"sparse autoencoders\" "
               "--max-results 20 --output results.json",
    )
    parser.add_argument("--keywords", nargs="+", help="Keywords to search for")
    parser.add_argument("--author", help="Author name filter (au:)")
    parser.add_argument("--ids", nargs="+", help="arXiv ids to look up (ids or URLs)")
    _add_search_options(parser)
    parser.add_argument("--download-pdf", metavar="DIR",
                        help="Download the resolved ids into DIR and exit")
    return parser


def _search_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="arxiv_fetch.py search",
        description="Search arXiv and print a JSON list of papers.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Example:\n"
               "  python3 tools/arxiv_fetch.py search \"attention mechanism\" --max 10\n"
               "  python3 tools/arxiv_fetch.py search \"id:1706.03762\" --max 1",
    )
    parser.add_argument("query", help="Free-text query or an arXiv field query (id:, ti:, au:, cat:, ...)")
    _add_search_options(parser)
    return parser


def _paper_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="arxiv_fetch.py paper",
        description="Fetch one arXiv paper by id (metadata + PDF URL).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Example:\n"
               "  python3 tools/arxiv_fetch.py paper 1706.03762",
    )
    parser.add_argument("arxiv_id", help="arXiv id (1706.03762), abs/pdf URL, or cs/0601001")
    parser.add_argument("--output", "-o", help="Write the JSON to this file instead of stdout")
    return parser


def _download_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="arxiv_fetch.py download",
        description="Download arXiv PDFs into a directory.",
    )
    parser.add_argument("arxiv_id", nargs="+", help="arXiv id(s) to download")
    parser.add_argument("--dir", default="papers", help="Target directory (default: papers)")
    parser.add_argument("--output", "-o", help="Write the JSON report to this file")
    return parser


def _result_count(payload) -> int:
    """Number of papers in a payload (list, or an envelope with `results`)."""
    if isinstance(payload, list):
        return len(payload)
    if isinstance(payload, dict) and isinstance(payload.get("results"), list):
        return len(payload["results"])
    return 1


def _emit(payload, output_path) -> None:
    text = json.dumps(payload, indent=2, ensure_ascii=False)
    if output_path:
        with open(output_path, "w", encoding="utf-8") as handle:
            handle.write(text)
        print("Wrote {} result(s) -> {}".format(
            _result_count(payload), output_path), file=sys.stderr)
    else:
        print(text)


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)

    if argv and argv[0] == "search":
        args = _search_parser().parse_args(argv[1:])
        result = _search(
            search_query=args.query,
            max_results=args.max_results,
            sort_by=args.sort_by,
            sort_order=args.sort_order,
        )
        _emit(result["papers"], args.output)
        return 0

    if argv and argv[0] == "download":
        args = _download_parser().parse_args(argv[1:])
        _emit(_download(args.arxiv_id, args.dir), args.output)
        return 0

    if argv and argv[0] == "paper":
        args = _paper_parser().parse_args(argv[1:])
        _emit(_paper(args.arxiv_id), args.output)
        return 0

    if argv and _looks_like_arxiv_id(argv[0]):
        args = _paper_parser().parse_args(argv)
        _emit(_paper(args.arxiv_id), args.output)
        return 0

    args = _flag_mode_parser().parse_args(argv)

    if args.download_pdf:
        if not args.ids:
            _die("--download-pdf needs --ids to say what to download")
        _emit(_download(args.ids, args.download_pdf), None)
        return 0

    if args.ids:
        result = _search(ids=args.ids, max_results=args.max_results)
    elif args.keywords:
        result = _search(
            search_query=_build_query(
                args.keywords,
                author=args.author,
                category=args.category,
                search_field=args.search_field,
            ),
            max_results=args.max_results,
            sort_by=args.sort_by,
            sort_order=args.sort_order,
        )
    else:
        _flag_mode_parser().print_usage(sys.stderr)
        _die("give --keywords, --ids or --author to search arXiv")

    payload = {
        "query": result["query"],
        "result_count": len(result["papers"]),
        "total_results": result["total"],
        "results": result["papers"],
    }
    _emit(payload, args.output)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001 - a clean message beats a traceback
        print("ERROR: {}: {}".format(type(exc).__name__, exc), file=sys.stderr)
        raise SystemExit(1)
