#!/usr/bin/env python3
"""Semantic Scholar Graph API tool for the `semantic-scholar` and
`research-lit` skills.

Documented interface (see `.claude/skills/semantic-scholar/SKILL.md` and
`.claude/skills/research-lit/SKILL.md`):

    python3 tools/semantic_scholar_fetch.py search "QUERY" --max 10 \
        --fields-of-study "Computer Science,Engineering" \
        --publication-types JournalArticle,Conference

    python3 tools/semantic_scholar_fetch.py search-bulk "QUERY" --max 100 \
        --sort citationCount:desc --fields-of-study "Computer Science" --year "2020-"

    python3 tools/semantic_scholar_fetch.py paper "PAPER_ID"

PAPER_ID may be a DOI (`10.1109/TSP.2021.3071210`), an arXiv id
(`ARXIV:2006.10685`), a corpus id (`CorpusId:219792180`) or a 40-character
Semantic Scholar paper id.

Output is the raw Semantic Scholar JSON on stdout, so consumers can read
`externalIds.ArXiv`, `tldr.text`, `publicationVenue.type` and
`openAccessPdf.url` exactly as the skill documents them.

Requires only the Python standard library. Set `SEMANTIC_SCHOLAR_API_KEY`
(or `S2_API_KEY`) for a higher rate limit; the unauthenticated pool is
throttled to roughly one request per second.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BASE_URL = "https://api.semanticscholar.org/graph/v1"
USER_AGENT = os.environ.get(
    "SEMANTIC_SCHOLAR_USER_AGENT",
    "claude-code-paper-writing-skills/1.0 (semantic_scholar_fetch.py)",
)
TIMEOUT = 30

# Rich field set: `publicationVenue` and `openAccessPdf` are required by the
# skill's presentation step, `tldr` supplies the one-line summary.
FIELDS = (
    "paperId,title,abstract,authors,year,citationCount,influentialCitationCount,"
    "venue,publicationVenue,publicationTypes,fieldsOfStudy,tldr,externalIds,"
    "openAccessPdf,url,publicationDate"
)
# Reduced field set for endpoints that reject `tldr`.
FLAT_FIELDS = (
    "paperId,title,abstract,authors,year,citationCount,influentialCitationCount,"
    "venue,publicationTypes,fieldsOfStudy,externalIds,openAccessPdf,url,publicationDate"
)

API_KEY = os.environ.get("SEMANTIC_SCHOLAR_API_KEY") or os.environ.get("S2_API_KEY") or ""
RETRY_WAIT = float(os.environ.get("S2_RETRY_WAIT", "30"))
MAX_RETRIES = int(os.environ.get("S2_MAX_RETRIES", "3"))

_HEADERS = {"User-Agent": USER_AGENT, "Accept": "application/json"}
if API_KEY:
    _HEADERS["x-api-key"] = API_KEY

_MIN_INTERVAL = 0.2 if API_KEY else 1.2
_last_request = 0.0


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


class _RequestFailed(Exception):
    """Internal: the request failed and the caller may want to retry differently."""


def _die(message: str, code: int = 1) -> "None":
    print("ERROR: {}".format(message), file=sys.stderr)
    raise SystemExit(code)


def _throttle() -> None:
    global _last_request
    wait = _MIN_INTERVAL - (time.monotonic() - _last_request)
    if wait > 0:
        time.sleep(wait)
    _last_request = time.monotonic()


def _request(method: str, path: str, params=None, body=None):
    """Call the S2 API with pacing and 429/5xx retries."""
    url = BASE_URL + path
    if params:
        url += "?" + urllib.parse.urlencode(params, doseq=True)

    data = None
    headers = dict(_HEADERS)
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"

    last_error = None
    for attempt in range(MAX_RETRIES):
        _throttle()
        request = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
                payload = response.read()
            return json.loads(payload.decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = ""
            try:
                detail = exc.read().decode("utf-8", "replace")[:300]
            except Exception:  # noqa: BLE001 - body may already be consumed
                detail = ""
            last_error = "HTTP {} {}".format(exc.code, detail or exc.reason)
            if exc.code == 429:
                wait = RETRY_WAIT * (attempt + 1)
                print(
                    "Rate limited by Semantic Scholar; waiting {}s "
                    "(attempt {}/{}).".format(wait, attempt + 1, MAX_RETRIES),
                    file=sys.stderr,
                )
                time.sleep(wait)
                continue
            if 500 <= exc.code < 600:
                time.sleep(2.0 * (attempt + 1))
                continue
            raise _RequestFailed("Semantic Scholar API error: " + last_error)
        except urllib.error.URLError as exc:
            last_error = str(exc.reason)
            time.sleep(2.0 * (attempt + 1))
        except ValueError as exc:
            raise _RequestFailed(
                "could not decode the Semantic Scholar response: {}".format(exc))
    raise _RequestFailed("Semantic Scholar API unreachable: {}".format(last_error))


def _split_multi(value):
    """`"Computer Science,Engineering"` -> `["Computer Science", "Engineering"]`."""
    if not value:
        return []
    return [part.strip() for part in value.split(",") if part.strip()]


def _search_params(args) -> dict:
    params = {
        "query": args.query,
        "limit": args.max_results,
        "fields": args.fields,
    }
    fields_of_study = _split_multi(args.fields_of_study)
    if fields_of_study:
        params["fieldsOfStudy"] = fields_of_study
    publication_types = _split_multi(args.publication_types)
    if publication_types:
        params["publicationTypes"] = publication_types
    if args.min_citations is not None:
        params["minCitationCount"] = args.min_citations
    if args.year:
        params["year"] = args.year
    if args.venue:
        params["venue"] = args.venue
    return params


def _search(args) -> list:
    """Relevance-ranked `/paper/search`."""
    params = _search_params(args)
    try:
        data = _request("GET", "/paper/search", params=params)
    except _RequestFailed:
        # A rejected field (e.g. an unknown field-of-study) should not sink
        # the search: retry once with the reduced field set.
        params["fields"] = FLAT_FIELDS
        data = _request("GET", "/paper/search", params=params)
    return data.get("data", [])


def _search_bulk(args) -> list:
    """`/paper/search/bulk` - sorted, up to 1000 results per page."""
    body = {
        "query": args.query,
        "fields": args.fields,
        "sort": args.sort,
    }
    token = getattr(args, "token", None)
    if token:
        body["token"] = token

    fields_of_study = _split_multi(args.fields_of_study)
    if fields_of_study:
        body["fieldsOfStudy"] = fields_of_study
    publication_types = _split_multi(args.publication_types)
    if publication_types:
        body["publicationTypes"] = publication_types
    if args.min_citations is not None:
        body["minCitationCount"] = args.min_citations
    if args.year:
        body["year"] = args.year
    if args.venue:
        body["venue"] = args.venue

    try:
        data = _request("POST", "/paper/search/bulk", body=body)
    except _RequestFailed:
        body["fields"] = FLAT_FIELDS
        data = _request("POST", "/paper/search/bulk", body=body)
    return data.get("data", [])


def _paper(paper_id: str) -> dict:
    """`/paper/{id}` for a DOI / arXiv / CorpusId / S2 paper id."""
    paper_id = paper_id.strip()
    if not paper_id:
        _die("a paper id is required")
    quoted = urllib.parse.quote(paper_id, safe="")
    try:
        return _request("GET", "/paper/{}".format(quoted), params={"fields": FIELDS})
    except _RequestFailed:
        return _request("GET", "/paper/{}".format(quoted), params={"fields": FLAT_FIELDS})


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _add_filter_options(parser) -> None:
    parser.add_argument("--max", dest="max_results", type=int, default=10,
                        help="Maximum number of results (default: 10)")
    parser.add_argument("--fields-of-study",
                        help='Comma-separated fields, e.g. "Computer Science,Engineering"')
    parser.add_argument("--publication-types",
                        help="Comma-separated types, e.g. JournalArticle,Conference")
    parser.add_argument("--min-citations", type=int, help="Only papers with at least N citations")
    parser.add_argument("--year", help='Publication year filter, e.g. "2022-" or "2020-2024"')
    parser.add_argument("--venue", help="Exact venue name (partial matches do not work)")
    parser.add_argument("--output", "-o", help="Write the JSON to this file instead of stdout")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="semantic_scholar_fetch.py",
        description="Search Semantic Scholar for published venue papers.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Examples:\n"
               "  python3 tools/semantic_scholar_fetch.py search \"transformer\" --max 10 \\\n"
               "      --fields-of-study \"Computer Science,Engineering\" \\\n"
               "      --publication-types JournalArticle,Conference\n"
               "  python3 tools/semantic_scholar_fetch.py search-bulk \"transformer\" \\\n"
               "      --sort citationCount:desc --year \"2020-\"\n"
               "  python3 tools/semantic_scholar_fetch.py paper \"10.1109/TSP.2021.3071210\"",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_search = sub.add_parser("search", help="Relevance-ranked paper search")
    p_search.add_argument("query", help="Search query")
    p_search.add_argument("--fields", default=FIELDS, help=argparse.SUPPRESS)
    p_search.add_argument("--sort", default=None,
                          help="Sort key; when given the bulk endpoint is used")
    _add_filter_options(p_search)

    p_bulk = sub.add_parser("search-bulk", help="Sorted bulk paper search")
    p_bulk.add_argument("query", help="Search query")
    p_bulk.add_argument("--sort", default="citationCount:desc",
                        help="Sort key, e.g. citationCount:desc (default: citationCount:desc)")
    p_bulk.add_argument("--token", help="Pagination token from a previous bulk response")
    p_bulk.add_argument("--fields", default=FIELDS, help=argparse.SUPPRESS)
    _add_filter_options(p_bulk)

    p_paper = sub.add_parser("paper", help="Fetch one paper by DOI / arXiv / CorpusId / S2 id")
    p_paper.add_argument("paper_id", help="e.g. 10.1109/TSP.2021.3071210 or ARXIV:2006.10685")
    p_paper.add_argument("--output", "-o", help="Write the JSON to this file instead of stdout")

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
    args = _build_parser().parse_args(argv)

    if args.command == "search":
        if args.sort:
            # The skill maps `- sort: citations` onto the bulk endpoint.
            args.sort = args.sort
            result = _search_bulk(args)
        else:
            result = _search(args)
    elif args.command == "search-bulk":
        result = _search_bulk(args)
    else:
        result = _paper(args.paper_id)

    _emit(result, getattr(args, "output", None))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
    except SystemExit:
        raise
    except _RequestFailed as exc:
        print("ERROR: {}".format(exc), file=sys.stderr)
        raise SystemExit(1)
    except Exception as exc:  # noqa: BLE001 - a clean message beats a traceback
        print("ERROR: {}: {}".format(type(exc).__name__, exc), file=sys.stderr)
        raise SystemExit(1)
