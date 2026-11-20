#!/usr/bin/env python3
"""OpenAlex works/author lookup for the `research-lit` skill.

Documented interface (see `.claude/skills/research-lit/SKILL.md`):

    python3 tools/openalex_fetch.py search "QUERY" --max 10 \
        --year "2022-" --type article --sort relevance

    python3 tools/openalex_fetch.py work W2741809807
    python3 tools/openalex_fetch.py author A5023888391
    python3 tools/openalex_fetch.py authors "Yann LeCun"

The OpenAlex API is fully open - no key is required. Set
`OPENALEX_API_KEY` to use a premium key, and `OPENALEX_MAILTO` (or
`--mailto`) to join OpenAlex's polite pool.

The raw OpenAlex payload is printed as JSON on stdout (`meta` + `results`
for searches, a single object for `work`/`author`), so callers can read
`cited_by_count`, `authorships`, `grants`, `topics` and `primary_location`
directly.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE_URL = "https://api.openalex.org"
USER_AGENT = os.environ.get(
    "OPENALEX_USER_AGENT", "claude-code-paper-writing-skills/1.0 (openalex_fetch.py)"
)
TIMEOUT = 45

API_KEY = os.environ.get("OPENALEX_API_KEY", "")
MAILTO = os.environ.get("OPENALEX_MAILTO", "")

MAX_RESULTS_DEFAULT = 10

# Friendly sort names -> OpenAlex `sort` parameter values.
SORTS = {
    "relevance": "relevance_score:desc",
    "citations": "cited_by_count:desc",
    "date": "publication_date:desc",
    "newest": "publication_date:desc",
    "oldest": "publication_date:asc",
    "updated": "updated_date:desc",
}


def _die(message: str, code: int = 1) -> "None":
    """Print an actionable error to stderr and exit non-zero."""
    print("ERROR: {}".format(message), file=sys.stderr)
    raise SystemExit(code)


def _get_json(path: str, params=None) -> dict:
    """GET a path under the OpenAlex API and return the decoded JSON."""
    query = dict(params or {})
    if API_KEY:
        query["api_key"] = API_KEY
    if MAILTO:
        query["mailto"] = MAILTO
    url = BASE_URL + path
    if query:
        url += "?" + urllib.parse.urlencode(query)

    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT,
                                                   "Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = ""
        try:
            detail = exc.read().decode("utf-8", "replace")[:500]
        except Exception:  # noqa: BLE001 - the body may already be consumed
            detail = ""
        if exc.code == 403:
            _die("OpenAlex rejected the request (403). Check OPENALEX_API_KEY. "
                 + detail)
        if exc.code == 404:
            _die("OpenAlex has no record for {} (404). {}".format(path, detail))
        _die("OpenAlex API error: HTTP {}{}".format(
            exc.code, " - " + detail if detail else ""))
    except urllib.error.URLError as exc:
        _die("OpenAlex API unreachable: {}".format(exc.reason))
    except ValueError as exc:
        _die("could not decode the OpenAlex response: {}".format(exc))


def _year_filter(spec: str):
    """Turn `"2022-"` / `"2020-2024"` / `"2022"` into OpenAlex date filters."""
    spec = spec.strip()
    if not spec:
        return []
    if re.fullmatch(r"\d{4}", spec):
        return [
            "from_publication_date:{}-01-01".format(spec),
            "to_publication_date:{}-12-31".format(spec),
        ]
    match = re.fullmatch(r"(\d{4})\s*-\s*(\d{4})?", spec)
    if not match:
        _die("--year expects a year or a range, e.g. \"2022-\" or \"2020-2024\"")
    start, end = match.group(1), match.group(2)
    filters = ["from_publication_date:{}-01-01".format(start)]
    if end:
        filters.append("to_publication_date:{}-12-31".format(end))
    return filters


def _work_id(raw: str) -> str:
    """Normalise a work reference into an OpenAlex path segment."""
    raw = raw.strip()
    if not raw:
        _die("a work id is required")
    if "openalex.org" in raw:
        raw = raw.rstrip("/").split("/")[-1]
        raw = raw.split("?")[0]
    if raw.lower().startswith("doi:"):
        return "doi:" + raw[4:]
    if raw.startswith("http://doi.org/") or raw.startswith("https://doi.org/"):
        return "doi:" + raw.split("doi.org/", 1)[1]
    if raw.startswith("10."):
        return "doi:" + raw
    return raw


def _author_id(raw: str) -> str:
    """Normalise an author reference into an OpenAlex path segment."""
    raw = raw.strip()
    if not raw:
        _die("an author id is required")
    if "openalex.org" in raw:
        raw = raw.rstrip("/").split("/")[-1]
        raw = raw.split("?")[0]
    return raw


def cmd_search(args) -> dict:
    filters = []
    filters.extend(_year_filter(args.year))
    if args.type:
        filters.append("type:{}".format(args.type))
    if args.open_access:
        filters.append("is_oa:true")
    filters.extend(f for f in (args.filter or []) if f)

    params = {
        "search": args.query,
        "per-page": args.max_results,
        "page": 1,
    }
    if filters:
        params["filter"] = ",".join(filters)
    if args.sort:
        params["sort"] = SORTS.get(args.sort.lower(), args.sort)
    return _get_json("/works", params)


def cmd_work(args) -> dict:
    return _get_json("/works/" + urllib.parse.quote(_work_id(args.work_id), safe=":"))


def cmd_author(args) -> dict:
    return _get_json("/authors/" + urllib.parse.quote(_author_id(args.author_id), safe=""))


def cmd_authors(args) -> dict:
    params = {"search": args.query, "per-page": args.max_results, "page": 1}
    return _get_json("/authors", params)


def _add_common(parser) -> None:
    parser.add_argument("--output", "-o", help="Write the JSON to this file instead of stdout")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="openalex_fetch.py",
        description="Search OpenAlex works, or fetch one work / author by id.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Examples:\n"
               "  python3 tools/openalex_fetch.py search \"sparse autoencoder\" --max 10 \\\n"
               "      --year \"2022-\" --type article --sort relevance\n"
               "  python3 tools/openalex_fetch.py work W2741809807\n"
               "  python3 tools/openalex_fetch.py author A5023888391",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_search = sub.add_parser("search", help="Search works")
    p_search.add_argument("query", help="Search query")
    p_search.add_argument("--max", "--max-results", dest="max_results", type=int,
                          default=MAX_RESULTS_DEFAULT,
                          help="Maximum number of results (default: {})".format(
                              MAX_RESULTS_DEFAULT))
    p_search.add_argument("--year", help='Publication year filter, e.g. "2022-" or "2020-2024"')
    p_search.add_argument("--type", help="Work type filter, e.g. article, preprint, book")
    p_search.add_argument("--sort", help="Sort order: relevance, citations, date, oldest, "
                                         "newest, or a raw OpenAlex `field:dir` value")
    p_search.add_argument("--filter", action="append",
                          help="Extra raw OpenAlex filter (repeatable), e.g. "
                               "\"is_oa:true\" or \"institutions.id:I123\"")
    p_search.add_argument("--open-access", action="store_true",
                          help="Only open-access works")
    p_search.add_argument("--mailto", help="Email for the OpenAlex polite pool")
    _add_common(p_search)

    p_work = sub.add_parser("work", help="Fetch one work by id, DOI or OpenAlex URL")
    p_work.add_argument("work_id", help="e.g. W2741809807 or 10.1109/TSP.2021.3071210")
    p_work.add_argument("--mailto", help="Email for the OpenAlex polite pool")
    _add_common(p_work)

    p_author = sub.add_parser("author", help="Fetch one author by OpenAlex id")
    p_author.add_argument("author_id", help="e.g. A5023888391")
    p_author.add_argument("--mailto", help="Email for the OpenAlex polite pool")
    _add_common(p_author)

    p_authors = sub.add_parser("authors", help="Search authors by name")
    p_authors.add_argument("query", help="Author name")
    p_authors.add_argument("--max", "--max-results", dest="max_results", type=int,
                           default=MAX_RESULTS_DEFAULT,
                           help="Maximum number of results (default: {})".format(
                               MAX_RESULTS_DEFAULT))
    p_authors.add_argument("--mailto", help="Email for the OpenAlex polite pool")
    _add_common(p_authors)

    return parser


def _emit(payload, output_path) -> None:
    text = json.dumps(payload, indent=2, ensure_ascii=False)
    if output_path:
        with open(output_path, "w", encoding="utf-8") as handle:
            handle.write(text)
        print("Wrote results -> {}".format(output_path), file=sys.stderr)
    else:
        print(text)


def main(argv=None) -> int:
    global MAILTO
    args = _build_parser().parse_args(argv)
    if getattr(args, "mailto", None):
        MAILTO = args.mailto

    handlers = {
        "search": cmd_search,
        "work": cmd_work,
        "author": cmd_author,
        "authors": cmd_authors,
    }
    result = handlers[args.command](args)
    _emit(result, args.output)
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
