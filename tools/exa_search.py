#!/usr/bin/env python3
"""Exa AI-powered web search for the `exa-search` and `research-lit` skills.

Documented interface (see `.claude/skills/exa-search/SKILL.md` and
`.claude/skills/research-lit/SKILL.md`):

    python3 tools/exa_search.py search "QUERY" --max 10 --content highlights
    python3 tools/exa_search.py search "QUERY" --max 10 \
        --category "research paper" --start-date 2025-01-01 \
        --content text --max-chars 8000
    python3 tools/exa_search.py find-similar "URL" --max 5 --content highlights
    python3 tools/exa_search.py get-contents "URL1" "URL2" --content text

The search runs against Exa's REST API (https://api.exa.ai) using the
`EXA_API_KEY` environment variable. When no key is set but the `exa-py`
SDK is installed, the SDK is used instead. With neither available the tool
exits non-zero with the install instructions - Exa is optional and the
skill skips this source when it is missing.

The raw Exa payload is printed as JSON on stdout, so callers can read
`title`, `url`, `author`, `publisher`, `publishedDate`, `score` and the
content fields (`highlights`, `text`, `summary`) directly.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

API_URL = "https://api.exa.ai"
SEARCH_URL = API_URL + "/search"
FIND_SIMILAR_URL = API_URL + "/findSimilar"
CONTENTS_URL = API_URL + "/contents"

USER_AGENT = os.environ.get(
    "EXA_USER_AGENT", "claude-code-paper-writing-skills/1.0 (exa_search.py)"
)
TIMEOUT = 60

MAX_RESULTS_DEFAULT = 10

# The categories the skill documents.
CATEGORIES = [
    "research paper",
    "news",
    "company",
    "personal site",
    "financial report",
    "people",
]
CONTENT_MODES = ["highlights", "text", "summary", "none"]
SEARCH_TYPES = ["auto", "neural", "fast", "instant"]

API_KEY = os.environ.get("EXA_API_KEY", "")


def _die(message: str, code: int = 1) -> "None":
    """Print an actionable error to stderr and exit non-zero."""
    print("ERROR: {}".format(message), file=sys.stderr)
    raise SystemExit(code)


def _has_sdk() -> bool:
    try:
        import exa_py  # noqa: F401
    except ImportError:
        return False
    return True


def _require_backend() -> None:
    """Exit with install instructions when neither the key nor the SDK exist."""
    if not API_KEY and not _has_sdk():
        _die(
            "Exa is not available: EXA_API_KEY is not set and the `exa-py` SDK "
            "is not installed.\n"
            "  Install the SDK:  pip install exa-py\n"
            "  Set the key:     export EXA_API_KEY=your-key-here\n"
            "  Get a key from:  https://exa.ai\n"
            "Exa is optional - skip this source and continue with the others."
        )


def _split_multi(value):
    """`"a,b"` -> `["a", "b"]`."""
    if not value:
        return []
    return [part.strip() for part in value.split(",") if part.strip()]


def _post_json(url: str, body: dict) -> dict:
    """POST JSON to Exa and return the decoded response."""
    payload = json.dumps(body).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": USER_AGENT,
    }
    if API_KEY:
        headers["x-api-key"] = API_KEY
    request = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = ""
        try:
            detail = exc.read().decode("utf-8", "replace")[:500]
        except Exception:  # noqa: BLE001 - the body may already be consumed
            detail = ""
        _die("Exa API error: HTTP {}{}".format(exc.code, " - " + detail if detail else ""))
    except urllib.error.URLError as exc:
        _die("Exa API unreachable: {}".format(exc.reason))
    except ValueError as exc:
        _die("could not decode the Exa response: {}".format(exc))


def _to_plain(value):
    """Turn SDK response objects into plain JSON-serialisable data."""
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, list):
        return [_to_plain(item) for item in value]
    if isinstance(value, dict):
        return {k: _to_plain(v) for k, v in value.items()}
    for attr in ("model_dump", "dict"):
        method = getattr(value, attr, None)
        if callable(method):
            try:
                return _to_plain(method())
            except TypeError:
                continue
    if hasattr(value, "__dict__"):
        return {
            k: _to_plain(v) for k, v in vars(value).items() if not k.startswith("_")
        }
    return str(value)


def _sdk_call(method_name: str, **kwargs):
    """Call the exa-py SDK; returns None when the SDK is unavailable."""
    try:
        from exa_py import Exa
    except ImportError:
        return None
    client = Exa(api_key=API_KEY) if API_KEY else Exa()
    method = getattr(client, method_name, None)
    if method is None:
        return None
    return _to_plain(method(**kwargs))


def _contents_block(mode: str, query: str, max_chars, summary_query):
    """Build the Exa `contents` object for the requested content mode."""
    if mode == "none":
        return None
    if mode == "highlights":
        return {"highlights": {"numSentences": 2, "highlightsPerUrl": 3}}
    if mode == "text":
        text = {}
        if max_chars:
            text["maxCharacters"] = max_chars
        return {"text": text}
    if mode == "summary":
        summary = {}
        if summary_query:
            summary["query"] = summary_query
        return {"summary": summary}
    return None


def cmd_search(args) -> dict:
    body = {"query": args.query, "numResults": args.max_results}
    if args.type:
        body["type"] = args.type
    if args.category:
        body["category"] = args.category
    include_domains = _split_multi(args.domains)
    if include_domains:
        body["includeDomains"] = include_domains
    exclude_domains = _split_multi(args.exclude_domains)
    if exclude_domains:
        body["excludeDomains"] = exclude_domains
    include_text = _split_multi(args.include_text)
    if include_text:
        body["includeText"] = include_text
    exclude_text = _split_multi(args.exclude_text)
    if exclude_text:
        body["excludeText"] = exclude_text
    if args.start_date:
        body["startPublishedDate"] = args.start_date
    if args.end_date:
        body["endPublishedDate"] = args.end_date
    if args.location:
        body["country"] = args.location
    contents = _contents_block(args.content, args.query, args.max_chars, args.summary_query)
    if contents:
        body["contents"] = contents

    if not API_KEY:
        sdk = _sdk_call("search_and_contents", **body)
        if sdk is not None:
            return sdk
        _die("EXA_API_KEY is not set and the `exa-py` SDK failed to run.")
    return _post_json(SEARCH_URL, body)


def cmd_find_similar(args) -> dict:
    body = {"url": args.url, "numResults": args.max_results}
    if args.type:
        body["type"] = args.type
    if args.category:
        body["category"] = args.category
    include_domains = _split_multi(args.domains)
    if include_domains:
        body["includeDomains"] = include_domains
    exclude_domains = _split_multi(args.exclude_domains)
    if exclude_domains:
        body["excludeDomains"] = exclude_domains
    if args.start_date:
        body["startPublishedDate"] = args.start_date
    if args.end_date:
        body["endPublishedDate"] = args.end_date
    if args.location:
        body["country"] = args.location
    contents = _contents_block(args.content, args.url, args.max_chars, args.summary_query)
    if contents:
        body["contents"] = contents

    if not API_KEY:
        sdk = _sdk_call("find_similar", **body)
        if sdk is not None:
            return sdk
        _die("EXA_API_KEY is not set and the `exa-py` SDK failed to run.")
    return _post_json(FIND_SIMILAR_URL, body)


def cmd_get_contents(args) -> dict:
    contents = _contents_block(args.content, args.urls[0], args.max_chars, args.summary_query)
    body = {"urls": list(args.urls)}
    if contents:
        body.update(contents)

    if not API_KEY:
        sdk_kwargs = {"urls": list(args.urls)}
        if args.content == "text":
            text = {}
            if args.max_chars:
                text["maxCharacters"] = args.max_chars
            sdk_kwargs["text"] = text
        elif args.content == "highlights":
            sdk_kwargs["highlights"] = {"numSentences": 2, "highlightsPerUrl": 3}
        elif args.content == "summary":
            sdk_kwargs["summary"] = (
                {"query": args.summary_query} if args.summary_query else {}
            )
        sdk = _sdk_call("get_contents", **sdk_kwargs)
        if sdk is not None:
            return sdk
        _die("EXA_API_KEY is not set and the `exa-py` SDK failed to run.")
    return _post_json(CONTENTS_URL, body)


def _add_common(parser) -> None:
    parser.add_argument("--output", "-o", help="Write the JSON to this file instead of stdout")


def _add_search_options(parser) -> None:
    parser.add_argument("--max", "--max-results", dest="max_results", type=int,
                        default=MAX_RESULTS_DEFAULT,
                        help="Maximum number of results (default: {})".format(MAX_RESULTS_DEFAULT))
    parser.add_argument("--category", choices=CATEGORIES,
                        help="Restrict results to one Exa category")
    parser.add_argument("--content", choices=CONTENT_MODES, default="highlights",
                        help="Content extraction mode (default: highlights)")
    parser.add_argument("--max-chars", type=int,
                        help="Maximum characters of extracted text (used by --content text)")
    parser.add_argument("--summary-query",
                        help="Question for --content summary (default: Exa's own summary)")
    parser.add_argument("--type", choices=SEARCH_TYPES, default="auto",
                        help="Exa search type (default: auto)")
    parser.add_argument("--domains", help="Comma-separated include domains")
    parser.add_argument("--exclude-domains", help="Comma-separated exclude domains")
    parser.add_argument("--include-text", help="Comma-separated phrases that must appear")
    parser.add_argument("--exclude-text", help="Comma-separated phrases to exclude")
    parser.add_argument("--start-date", help="Only results published after this ISO 8601 date")
    parser.add_argument("--end-date", help="Only results published before this ISO 8601 date")
    parser.add_argument("--location", help="Two-letter ISO country code, e.g. US")
    _add_common(parser)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="exa_search.py",
        description="Exa AI-powered web search with content extraction.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Examples:\n"
               "  python3 tools/exa_search.py search \"RAG pipelines\" --max 10 --content highlights\n"
               "  python3 tools/exa_search.py search \"transformer\" --max 10 \\\n"
               "      --category \"research paper\" --content text --max-chars 8000\n"
               "  python3 tools/exa_search.py find-similar \"https://arxiv.org/abs/2301.07041\" --max 5\n"
               "  python3 tools/exa_search.py get-contents \"https://example.com\" --content text",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_search = sub.add_parser("search", help="Search the web")
    p_search.add_argument("query", help="Search query")
    _add_search_options(p_search)

    p_sim = sub.add_parser("find-similar", help="Find pages similar to a URL")
    p_sim.add_argument("url", help="URL to find similar pages for")
    _add_search_options(p_sim)

    p_contents = sub.add_parser("get-contents", help="Fetch content for known URLs")
    p_contents.add_argument("urls", nargs="+", help="One or more URLs")
    p_contents.add_argument("--content", choices=CONTENT_MODES, default="text",
                            help="Content extraction mode (default: text)")
    p_contents.add_argument("--max-chars", type=int,
                            help="Maximum characters of extracted text")
    p_contents.add_argument("--summary-query",
                            help="Question for --content summary")
    _add_common(p_contents)

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
    _require_backend()

    handlers = {
        "search": cmd_search,
        "find-similar": cmd_find_similar,
        "get-contents": cmd_get_contents,
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
