#!/usr/bin/env python3
"""Fetch a web page with Scrapling and extract text, markdown, or JSON.

Two fetch modes:

  * default   -- HTTP via Scrapling's ``Fetcher`` (curl_cffi TLS fingerprint
                 impersonation). Fast, and enough for most documentation and
                 paper pages.
  * --browser -- stealth Chromium via ``StealthyFetcher`` (patchright /
                 Playwright). Use for JavaScript-rendered pages and sites
                 behind bot protection (e.g. Espacenet).

The script re-executes itself into the project virtualenv when ``scrapling``
is not importable under the current interpreter, so a skill can simply call
``python3 tools/web_fetch.py ...`` and have it work.

Exit codes:
  0  success
  1  fetch failed (network error, timeout, browser launch failure)
  2  command-line usage error (argparse)
  3  page fetched but the server answered with an HTTP error status (>= 400)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

# --------------------------------------------------------------------------
# Interpreter self-location
# --------------------------------------------------------------------------

#: Repository root = parent of the ``tools/`` directory holding this file.
REPO_ROOT = Path(__file__).resolve().parent.parent


def _venv_python() -> Path:
    """Path of the project virtualenv interpreter, honouring an override."""
    override = os.environ.get("WEB_FETCH_PYTHON")
    if override:
        return Path(override).expanduser()
    if os.name == "nt":  # pragma: no cover - Windows layout
        return REPO_ROOT / ".venv" / "Scripts" / "python.exe"
    return REPO_ROOT / ".venv" / "bin" / "python3"


def _install_hint() -> str:
    return (
        "Install it with:\n"
        '  uv pip install --python .venv/bin/python "scrapling[all]" && .venv/bin/scrapling install\n'
        "Or point WEB_FETCH_PYTHON at an interpreter that already has scrapling."
    )


def ensure_scrapling() -> None:
    """Re-exec into the project virtualenv if ``scrapling`` is missing here.

    Exits with a clear message (no traceback) when no suitable interpreter
    can be found.
    """
    try:
        import scrapling  # noqa: F401
    except ImportError:
        pass
    else:
        return

    if os.environ.get("_WEB_FETCH_REEXEC"):
        sys.stderr.write(
            "web_fetch.py: scrapling is not importable in the re-executed "
            f"interpreter ({sys.executable}).\n{_install_hint()}\n"
        )
        raise SystemExit(1)

    python = _venv_python()
    if not python.exists():
        sys.stderr.write(
            "web_fetch.py: scrapling is not importable under "
            f"{sys.executable!r} and no usable virtualenv interpreter was "
            f"found at {python}.\n{_install_hint()}\n"
        )
        raise SystemExit(1)

    os.environ["_WEB_FETCH_REEXEC"] = "1"
    script = str(Path(__file__).resolve())
    try:
        os.execv(str(python), [str(python), script, *sys.argv[1:]])
    except OSError as exc:  # pragma: no cover - exec failure
        sys.stderr.write(f"web_fetch.py: could not re-exec into {python}: {exc}\n")
        raise SystemExit(1) from exc


ensure_scrapling()


# --------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------

#: HTTP fetchers take seconds; browser fetchers take milliseconds.
DEFAULT_HTTP_TIMEOUT = 30
DEFAULT_BROWSER_TIMEOUT = 60


# --------------------------------------------------------------------------
# Fetching
# --------------------------------------------------------------------------


def fetch_http(url: str, timeout: float, user_agent: str | None):
    """Fetch ``url`` over HTTP with Scrapling's TLS-fingerprint impersonation."""
    from scrapling.fetchers import Fetcher

    kwargs: dict = {"timeout": timeout}
    if user_agent:
        kwargs["headers"] = {"User-Agent": user_agent}
    return Fetcher.get(url, **kwargs)


def fetch_browser(url: str, timeout: float, user_agent: str | None, solve_cloudflare: bool = False):
    """Fetch ``url`` with the stealth Chromium browser.

    ``timeout`` is in seconds here; Playwright expects milliseconds.
    """
    from scrapling.fetchers import StealthyFetcher

    kwargs: dict = {
        "timeout": int(timeout * 1000),  # seconds -> milliseconds
        "network_idle": True,
        "load_dom": True,
        "headless": True,
    }
    if user_agent:
        kwargs["useragent"] = user_agent
    if solve_cloudflare:
        # Scrapling's own challenge handling: detect the Cloudflare
        # interstitial, wait for it to clear, and tick a Turnstile box if one
        # appears. No bypass is implemented here.
        kwargs["solve_cloudflare"] = True
    return StealthyFetcher.fetch(url, **kwargs)


# --------------------------------------------------------------------------
# Extraction
# --------------------------------------------------------------------------


def _element_text(element) -> str:
    """Readable text of one matched element, collapsed onto a single line."""
    return " ".join(str(element.get_all_text(separator=" ", strip=True)).split())


def extract_title(response) -> str:
    """Best-effort document title."""
    try:
        titles = response.css("title::text")
    except Exception:
        titles = []
    for title in titles:
        text = str(title).strip()
        if text:
            return text
    try:
        heads = response.css("head title")
    except Exception:
        heads = []
    for head in heads:
        text = _element_text(head).strip()
        if text:
            return text
    return ""


def extract_content(response, css_selector: str | None, as_markdown: bool) -> str:
    """Extract the requested content from a response."""
    if css_selector:
        if as_markdown:
            return response.markdown(css_selector=css_selector)
        elements = response.css(css_selector)
        return "\n\n".join(_element_text(el) for el in elements)
    if as_markdown:
        return response.markdown()
    return str(response.get_all_text(separator="\n", strip=True))


def extract_matches(response, css_selector: str) -> list[dict]:
    """Structured data for each element matched by ``css_selector``."""
    matches = []
    for element in response.css(css_selector):
        try:
            html = str(element.html_content)
        except Exception:
            html = ""
        matches.append({"text": _element_text(element), "html": html})
    return matches


# --------------------------------------------------------------------------
# Output
# --------------------------------------------------------------------------


def _write(path: str, payload: str) -> None:
    target = Path(path).expanduser()
    if target.parent and not target.parent.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
    if not payload.endswith("\n"):
        payload += "\n"
    target.write_text(payload, encoding="utf-8")


def _emit(payload: str, output: str | None) -> None:
    """Write ``payload`` to stdout, or to ``output`` when given."""
    if output:
        _write(output, payload)
        sys.stderr.write(f"web_fetch.py: wrote {len(payload)} characters to {output}\n")
    else:
        sys.stdout.write(payload)
        if not payload.endswith("\n"):
            sys.stdout.write("\n")


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

EPILOG = """\
examples:
  # plain text of a page
  python3 tools/web_fetch.py https://example.com

  # extract every quote (CSS selector)
  python3 tools/web_fetch.py https://quotes.toscrape.com/ --css-selector '.quote'

  # JavaScript-rendered page -> stealth browser
  python3 tools/web_fetch.py https://quotes.toscrape.com/js/ --browser

  # HTML -> markdown, saved to a file
  python3 tools/web_fetch.py https://example.com --markdown --output page.md

  # structured result for programmatic use
  python3 tools/web_fetch.py https://example.com --json --css-selector 'h1'
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="web_fetch.py",
        description=(
            "Fetch a web page with Scrapling and print extracted content.\n\n"
            "Default mode is a plain HTTP request with TLS-fingerprint "
            "impersonation; --browser drives a stealth Chromium instead, which "
            "is needed for JavaScript-rendered and bot-protected pages."
        ),
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("url_positional", nargs="?", metavar="URL", help="URL to fetch")
    parser.add_argument("--url", dest="url_option", metavar="URL", help="URL to fetch (alternative to the positional argument)")
    parser.add_argument(
        "--browser",
        action="store_true",
        help="Fetch with the stealth Chromium browser instead of plain HTTP",
    )
    parser.add_argument(
        "--css-selector",
        metavar="SEL",
        help="Extract only the elements matching this CSS selector",
    )
    parser.add_argument(
        "--markdown",
        action="store_true",
        help="Convert the HTML to Markdown instead of plain text",
    )
    parser.add_argument(
        "--text",
        action="store_true",
        help="Extract plain text (the default output format)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit a JSON object with status, url, title and the extracted content",
    )
    parser.add_argument("--output", metavar="FILE", help="Write the result to FILE instead of stdout")
    parser.add_argument(
        "--timeout",
        type=float,
        metavar="SECONDS",
        help="Timeout in seconds (default: 30 for HTTP, 60 for the browser)",
    )
    parser.add_argument(
        "--user-agent",
        metavar="UA",
        help="Override the User-Agent header (default: Scrapling's built-in browser impersonation)",
    )
    parser.add_argument("--save-html", metavar="FILE", help="Also save the raw HTML of the page to FILE")
    parser.add_argument(
        "--solve-cloudflare",
        action="store_true",
        help="Browser mode only: wait out a Cloudflare/Turnstile challenge (Scrapling's built-in handling)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    url = args.url_option or args.url_positional
    if not url:
        parser.error("a URL is required (positional argument or --url)")
    if args.url_option and args.url_positional:
        parser.error("give the URL either positionally or with --url, not both")
    if not url.lower().startswith(("http://", "https://")):
        url = "https://" + url

    as_markdown = args.markdown
    if args.text and args.markdown:
        parser.error("--text and --markdown are mutually exclusive")
    if args.solve_cloudflare and not args.browser:
        parser.error("--solve-cloudflare only applies to --browser")
    timeout = args.timeout
    if timeout is None:
        timeout = DEFAULT_BROWSER_TIMEOUT if args.browser else DEFAULT_HTTP_TIMEOUT
    if timeout <= 0:
        parser.error("--timeout must be a positive number of seconds")

    mode = "browser" if args.browser else "http"
    try:
        if args.browser:
            response = fetch_browser(url, timeout, args.user_agent, args.solve_cloudflare)
        else:
            response = fetch_http(url, timeout, args.user_agent)
    except Exception as exc:
        message = str(exc).strip() or exc.__class__.__name__
        sys.stderr.write(f"web_fetch.py: {mode} fetch failed for {url}: {message}\n")
        return 1

    status = getattr(response, "status", None)

    if args.save_html:
        try:
            _write(args.save_html, str(response.html_content))
        except OSError as exc:
            sys.stderr.write(f"web_fetch.py: could not save HTML to {args.save_html}: {exc}\n")
            return 1

    try:
        content = extract_content(response, args.css_selector, as_markdown)
    except Exception as exc:
        message = str(exc).strip() or exc.__class__.__name__
        sys.stderr.write(f"web_fetch.py: extraction failed for {url}: {message}\n")
        return 1

    if args.css_selector:
        try:
            count = len(response.css(args.css_selector))
        except Exception:
            count = 0
        if count == 0:
            sys.stderr.write(
                f"web_fetch.py: CSS selector {args.css_selector!r} matched no elements on {url}\n"
            )

    if args.json:
        payload_obj = {
            "url": url,
            "final_url": str(getattr(response, "url", url) or url),
            "status": status,
            "title": extract_title(response),
            "mode": mode,
            "format": "markdown" if as_markdown else "text",
            "content": content,
        }
        if args.css_selector:
            payload_obj["matches"] = extract_matches(response, args.css_selector)
        payload = json.dumps(payload_obj, ensure_ascii=False, indent=2)
    else:
        payload = content

    try:
        _emit(payload, args.output)
    except BrokenPipeError:
        # e.g. `web_fetch.py URL | head`: exit quietly rather than reporting a
        # write failure.
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        return 0
    except OSError as exc:
        sys.stderr.write(f"web_fetch.py: could not write output: {exc}\n")
        return 1

    if status is not None and status >= 400:
        sys.stderr.write(f"web_fetch.py: server returned HTTP {status} for {url}\n")
        return 3

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:  # pragma: no cover - downstream closed the pipe
        # e.g. `web_fetch.py URL | head`: exit quietly instead of dumping a
        # "BrokenPipeError ignored" traceback and a confusing exit status.
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        raise SystemExit(0)
    except KeyboardInterrupt:  # pragma: no cover
        sys.stderr.write("web_fetch.py: interrupted\n")
        raise SystemExit(1)
