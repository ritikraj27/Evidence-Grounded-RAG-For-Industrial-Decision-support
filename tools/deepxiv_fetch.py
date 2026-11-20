#!/usr/bin/env python3
"""DeepXiv adapter for the `deepxiv` and `research-lit` skills.

Documented interface (see `.claude/skills/deepxiv/SKILL.md` and
`.claude/skills/research-lit/SKILL.md`):

    python3 tools/deepxiv_fetch.py --help
    python3 tools/deepxiv_fetch.py search "QUERY" --max 10
    python3 tools/deepxiv_fetch.py paper-brief ARXIV_ID
    python3 tools/deepxiv_fetch.py paper-head ARXIV_ID
    python3 tools/deepxiv_fetch.py paper-section ARXIV_ID "Experiments"
    python3 tools/deepxiv_fetch.py trending --days 7 --max 10
    python3 tools/deepxiv_fetch.py wsearch "QUERY"
    python3 tools/deepxiv_fetch.py sc "SEMANTIC_SCHOLAR_ID"

Two backends are tried in this order:

1. the `deepxiv-sdk` Python package (`pip install deepxiv-sdk`)
2. the `deepxiv` command-line tool on PATH

If neither is installed the tool exits non-zero with the install
instructions instead of raising an ImportError traceback, so the skill can
skip this source and continue with the remaining ones.

Reads the optional `DEEPXIV_TOKEN` env var; without it the SDK registers a
free token on first use. JSON goes to stdout; `--output FILE` writes it to
a file instead.
"""

from __future__ import annotations

import argparse
import inspect
import json
import os
import shutil
import subprocess
import sys

DEEPXIV_TOKEN = os.environ.get("DEEPXIV_TOKEN", "")
CLI_TIMEOUT = 120

try:
    from deepxiv_sdk import Reader

    try:
        from deepxiv_sdk.reader import (
            APIError,
            AuthenticationError,
            NotFoundError,
            RateLimitError,
        )
    except ImportError:  # pragma: no cover - older SDK layouts
        class APIError(Exception):
            pass

        class AuthenticationError(Exception):
            pass

        class NotFoundError(Exception):
            pass

        class RateLimitError(Exception):
            pass

    HAS_DEEPXIV = True
except ImportError:
    HAS_DEEPXIV = False
    Reader = None

    class APIError(Exception):
        pass

    class AuthenticationError(Exception):
        pass

    class NotFoundError(Exception):
        pass

    class RateLimitError(Exception):
        pass


_reader = None


# ---------------------------------------------------------------------------
# backends
# ---------------------------------------------------------------------------


def _die(message: str, code: int = 1) -> "None":
    """Print an actionable error to stderr and exit non-zero."""
    print("ERROR: {}".format(message), file=sys.stderr)
    raise SystemExit(code)


def _sdk_reader():
    """Return a memoised `deepxiv_sdk.Reader` instance."""
    global _reader
    if _reader is None:
        kwargs = {}
        if DEEPXIV_TOKEN:
            kwargs["token"] = DEEPXIV_TOKEN
        _reader = Reader(**kwargs)
    return _reader


def _sdk_call(method_name: str, **kwargs):
    """Call an SDK method, passing only the keyword arguments it accepts.

    Returns ``None`` when the installed SDK has no such method, so the
    caller can fall back to the command-line tool.
    """
    reader = _sdk_reader()
    method = getattr(reader, method_name, None)
    if method is None:
        return None
    try:
        accepted = inspect.signature(method).parameters
    except (TypeError, ValueError):  # pragma: no cover - builtins/C callables
        accepted = {}
    if accepted:
        kwargs = {k: v for k, v in kwargs.items() if k in accepted}
    return method(**kwargs)


def _cli_run(args) -> object:
    """Run the `deepxiv` CLI and return its JSON output."""
    exe = shutil.which("deepxiv")
    if not exe:
        return None
    try:
        proc = subprocess.run(
            [exe] + list(args),
            capture_output=True,
            text=True,
            timeout=CLI_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        _die("the `deepxiv` CLI timed out after {}s".format(CLI_TIMEOUT))
    except OSError as exc:
        _die("could not run the `deepxiv` CLI: {}".format(exc))
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "").strip()
        _die("`deepxiv {}` failed (exit {}): {}".format(
            " ".join(args), proc.returncode, detail or "no output"))
    try:
        return json.loads(proc.stdout)
    except ValueError:
        return {"raw": proc.stdout}


def _no_backend() -> "None":
    """Exit with the install instructions when neither backend exists."""
    _die(
        "DeepXiv is not available: neither the `deepxiv-sdk` package nor the "
        "`deepxiv` CLI is installed.\n"
        "  Install the SDK:  pip install deepxiv-sdk\n"
        "  Or the CLI:      pip install deepxiv\n"
        "DeepXiv is optional - skip this source and continue with the others."
    )


# ---------------------------------------------------------------------------
# normalisation (same field names as the upstream tools/fetch_deepxiv.py)
# ---------------------------------------------------------------------------


def _authors_of(raw):
    """Normalise the several author shapes the API returns to a list of names."""
    if not raw:
        return []
    if isinstance(raw[0], dict):
        return [a.get("name", "") for a in raw]
    return list(raw)


def _normalise_search(data) -> list:
    """Normalise a search payload to the upstream paper dict shape."""
    results = data.get("results", []) if isinstance(data, dict) else data
    papers = []
    for r in results or []:
        papers.append(
            {
                "arxiv_id": r.get("arxiv_id", ""),
                "title": r.get("title", ""),
                "abstract": r.get("abstract", ""),
                "authors": _authors_of(r.get("authors", [])),
                "categories": r.get("categories", []),
                "year": r.get("year"),
                "citation_count": r.get("citation", 0),
                "relevance_score": r.get("score", 0.0),
                "published": r.get("publish_at", ""),
            }
        )
    return papers


def _normalise_brief(data: dict, arxiv_id: str) -> dict:
    return {
        "arxiv_id": data.get("arxiv_id", arxiv_id),
        "title": data.get("title", ""),
        "tldr": data.get("tldr", ""),
        "keywords": data.get("keywords", []),
        "citations": data.get("citations", 0),
        "published": data.get("publish_at", ""),
        "src_url": data.get("src_url", ""),
        "github_url": data.get("github_url", None),
    }


def _normalise_head(data: dict, arxiv_id: str) -> dict:
    sections_raw = data.get("sections", {})
    sections = []
    if isinstance(sections_raw, dict):
        for name, info in sections_raw.items():
            if isinstance(info, dict):
                sections.append(
                    {
                        "name": name,
                        "tldr": info.get("tldr", ""),
                        "token_count": info.get("token_count", 0),
                    }
                )
            else:
                sections.append({"name": name, "tldr": "", "token_count": 0})
    elif isinstance(sections_raw, list):
        for item in sections_raw:
            if isinstance(item, dict):
                sections.append(
                    {
                        "name": item.get("name", ""),
                        "tldr": item.get("tldr", ""),
                        "token_count": item.get("token_count", 0),
                    }
                )
    return {
        "arxiv_id": data.get("arxiv_id", arxiv_id),
        "title": data.get("title", ""),
        "abstract": data.get("abstract", ""),
        "authors": _authors_of(data.get("authors", [])),
        "categories": data.get("categories", []),
        "published": data.get("publish_at", ""),
        "token_count": data.get("token_count", 0),
        "sections": sections,
    }


def _normalise_trending(data) -> list:
    papers = data.get("papers", []) if isinstance(data, dict) else data
    out = []
    for p in papers or []:
        out.append(
            {
                "arxiv_id": p.get("arxiv_id", ""),
                "title": p.get("title", ""),
                "rank": p.get("rank", 0),
                "social_impact": p.get("stats", {}),
                "categories": p.get("categories", []),
            }
        )
    return out


# ---------------------------------------------------------------------------
# commands
# ---------------------------------------------------------------------------


def cmd_search(args) -> list:
    if HAS_DEEPXIV:
        data = _sdk_call(
            "search",
            query=args.query,
            size=args.max_results,
            search_mode=args.mode,
            categories=args.categories,
            min_citation=args.min_citation,
            date_from=args.date_from,
            date_to=args.date_to,
        )
        if data is not None:
            return _normalise_search(data)
    cli = _cli_run(
        ["search", args.query, "--limit", str(args.max_results), "--format", "json"]
    )
    if cli is None:
        _no_backend()
    return _normalise_search(cli)


def cmd_paper_brief(args) -> dict:
    if HAS_DEEPXIV:
        data = _sdk_call("brief", arxiv_id=args.arxiv_id)
        if data is not None:
            return _normalise_brief(data, args.arxiv_id)
    cli = _cli_run(["paper", args.arxiv_id, "--brief", "--format", "json"])
    if cli is None:
        _no_backend()
    return _normalise_brief(cli, args.arxiv_id)


def cmd_paper_head(args) -> dict:
    if HAS_DEEPXIV:
        data = _sdk_call("head", arxiv_id=args.arxiv_id)
        if data is not None:
            return _normalise_head(data, args.arxiv_id)
    cli = _cli_run(["paper", args.arxiv_id, "--head", "--format", "json"])
    if cli is None:
        _no_backend()
    return _normalise_head(cli, args.arxiv_id)


def cmd_paper_section(args) -> dict:
    if HAS_DEEPXIV:
        content = _sdk_call(
            "section", arxiv_id=args.arxiv_id, section_name=args.section_name
        )
        if content is not None:
            return {
                "arxiv_id": args.arxiv_id,
                "section_name": args.section_name,
                "content": content if isinstance(content, str) else str(content),
            }
    cli = _cli_run(
        ["paper", args.arxiv_id, "--section", args.section_name, "--format", "json"]
    )
    if cli is None:
        _no_backend()
    if isinstance(cli, dict) and "content" in cli:
        return {
            "arxiv_id": args.arxiv_id,
            "section_name": args.section_name,
            "content": cli.get("content", ""),
        }
    return {
        "arxiv_id": args.arxiv_id,
        "section_name": args.section_name,
        "content": cli if isinstance(cli, str) else json.dumps(cli, ensure_ascii=False),
    }


def cmd_paper_raw(args) -> dict:
    if HAS_DEEPXIV:
        content = _sdk_call("raw", arxiv_id=args.arxiv_id)
        if content is not None:
            return {
                "arxiv_id": args.arxiv_id,
                "content": content if isinstance(content, str) else str(content),
            }
    cli = _cli_run(["paper", args.arxiv_id, "--raw", "--format", "json"])
    if cli is None:
        _no_backend()
    return {
        "arxiv_id": args.arxiv_id,
        "content": cli if isinstance(cli, str) else json.dumps(cli, ensure_ascii=False),
    }


def cmd_paper_social(args) -> dict:
    if HAS_DEEPXIV:
        data = _sdk_call("social_impact", arxiv_id=args.arxiv_id)
        if data is not None:
            if data is None:
                return _empty_social(args.arxiv_id)
            return {
                "arxiv_id": data.get("arxiv_id", args.arxiv_id),
                "tweets": data.get("total_tweets", 0),
                "views": data.get("total_views", 0),
                "likes": data.get("total_likes", 0),
                "replies": data.get("total_replies", 0),
                "first_seen": data.get("first_seen_date", ""),
                "last_seen": data.get("last_seen_date", ""),
            }
    cli = _cli_run(["paper", args.arxiv_id, "--social", "--format", "json"])
    if cli is None:
        _no_backend()
    if isinstance(cli, dict):
        return {
            "arxiv_id": cli.get("arxiv_id", args.arxiv_id),
            "tweets": cli.get("total_tweets", cli.get("tweets", 0)),
            "views": cli.get("total_views", cli.get("views", 0)),
            "likes": cli.get("total_likes", cli.get("likes", 0)),
            "replies": cli.get("total_replies", cli.get("replies", 0)),
            "first_seen": cli.get("first_seen_date", ""),
            "last_seen": cli.get("last_seen_date", ""),
        }
    return _empty_social(args.arxiv_id)


def _empty_social(arxiv_id: str) -> dict:
    return {
        "arxiv_id": arxiv_id,
        "tweets": 0,
        "views": 0,
        "likes": 0,
        "replies": 0,
        "first_seen": "",
        "last_seen": "",
    }


def cmd_trending(args) -> list:
    if HAS_DEEPXIV:
        data = _sdk_call("trending", days=args.days, limit=args.max_results)
        if data is not None:
            return _normalise_trending(data)
    cli = _cli_run(
        ["trending", "--days", str(args.days), "--limit", str(args.max_results),
         "--output", "json"]
    )
    if cli is None:
        _no_backend()
    return _normalise_trending(cli)


def cmd_wsearch(args) -> object:
    if HAS_DEEPXIV:
        data = _sdk_call("wsearch", query=args.query, size=args.max_results)
        if data is not None:
            return data
    cli = _cli_run(["wsearch", args.query, "--output", "json"])
    if cli is None:
        _no_backend()
    return cli


def cmd_sc(args) -> object:
    if HAS_DEEPXIV:
        data = _sdk_call("sc", paper_id=args.semantic_scholar_id)
        if data is not None:
            return data
    cli = _cli_run(["sc", args.semantic_scholar_id, "--output", "json"])
    if cli is None:
        _no_backend()
    return cli


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _add_common(parser) -> None:
    parser.add_argument("--output", "-o", help="Write the JSON to this file instead of stdout")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="deepxiv_fetch.py",
        description="DeepXiv: semantic search + progressive paper reading.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Examples:\n"
               "  python3 tools/deepxiv_fetch.py search \"low rank adaptation\" --max 10\n"
               "  python3 tools/deepxiv_fetch.py paper-brief 2106.09685\n"
               "  python3 tools/deepxiv_fetch.py paper-head 2106.09685\n"
               "  python3 tools/deepxiv_fetch.py paper-section 2106.09685 \"Experiments\"\n"
               "  python3 tools/deepxiv_fetch.py trending --days 7 --max 10\n"
               "  python3 tools/deepxiv_fetch.py wsearch \"RAG pipelines\"\n"
               "  python3 tools/deepxiv_fetch.py sc \"649def34f8be52c8b66281af98ae884c09aef38b\"",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_search = sub.add_parser("search", help="Hybrid search for papers")
    p_search.add_argument("query", help="Search query")
    p_search.add_argument("--max", "--limit", dest="max_results", type=int, default=10,
                           help="Maximum number of results (default: 10)")
    p_search.add_argument("--mode", choices=["hybrid", "bm25", "vector"], default="hybrid",
                          help="Search mode (default: hybrid)")
    p_search.add_argument("--categories", nargs="+", help="arXiv category filter")
    p_search.add_argument("--min-citation", type=int, help="Minimum citation count")
    p_search.add_argument("--date-from", help="From date (YYYY-MM-DD)")
    p_search.add_argument("--date-to", help="To date (YYYY-MM-DD)")
    _add_common(p_search)

    p_brief = sub.add_parser("paper-brief", help="Quick paper summary (TLDR)")
    p_brief.add_argument("arxiv_id", help="arXiv ID, e.g. 2106.09685")
    _add_common(p_brief)

    p_head = sub.add_parser("paper-head", help="Paper metadata + section map")
    p_head.add_argument("arxiv_id", help="arXiv ID")
    _add_common(p_head)

    p_section = sub.add_parser("paper-section", help="Read one named section")
    p_section.add_argument("arxiv_id", help="arXiv ID")
    p_section.add_argument("section_name", help="Section name (case-insensitive)")
    _add_common(p_section)

    p_raw = sub.add_parser("paper-raw", help="Full paper text in markdown")
    p_raw.add_argument("arxiv_id", help="arXiv ID")
    _add_common(p_raw)

    p_social = sub.add_parser("paper-social", help="Social impact metrics")
    p_social.add_argument("arxiv_id", help="arXiv ID")
    _add_common(p_social)

    p_trending = sub.add_parser("trending", help="Trending papers")
    p_trending.add_argument("--days", type=int, choices=[7, 14, 30], default=7,
                            help="Lookback window (default: 7)")
    p_trending.add_argument("--max", "--limit", dest="max_results", type=int, default=10,
                            help="Maximum number of results (default: 10)")
    _add_common(p_trending)

    p_wsearch = sub.add_parser("wsearch", help="DeepXiv web search")
    p_wsearch.add_argument("query", help="Web search query")
    p_wsearch.add_argument("--max", "--limit", dest="max_results", type=int, default=10,
                           help="Maximum number of results (default: 10)")
    _add_common(p_wsearch)

    p_sc = sub.add_parser("sc", help="Semantic Scholar metadata by id")
    p_sc.add_argument("semantic_scholar_id", help="Semantic Scholar paper id")
    _add_common(p_sc)

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

    handlers = {
        "search": cmd_search,
        "paper-brief": cmd_paper_brief,
        "paper-head": cmd_paper_head,
        "paper-section": cmd_paper_section,
        "paper-raw": cmd_paper_raw,
        "paper-social": cmd_paper_social,
        "trending": cmd_trending,
        "wsearch": cmd_wsearch,
        "sc": cmd_sc,
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
    except (APIError, AuthenticationError, RateLimitError, NotFoundError) as exc:
        print("ERROR: DeepXiv API error: {}".format(exc), file=sys.stderr)
        raise SystemExit(1)
    except ConnectionError as exc:
        print("ERROR: connection error: {}".format(exc), file=sys.stderr)
        raise SystemExit(1)
    except Exception as exc:  # noqa: BLE001 - a clean message beats a traceback
        print("ERROR: {}: {}".format(type(exc).__name__, exc), file=sys.stderr)
        raise SystemExit(1)
