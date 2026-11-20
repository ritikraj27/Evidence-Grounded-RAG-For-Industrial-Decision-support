#!/usr/bin/env python3
"""paper_finder - find published conference papers by topic, venue and year.

Backs the "Search Tools" section of the `deep-research-lit` skill (Phase 1
"Frontier" and Phase 2 "Survey"), which references a `paper_finder.py` that
was never published upstream.

Two backends, tried in this order:

  1. OpenReview REST API  - used when credentials are available
     (OPENREVIEW_EMAIL / OPENREVIEW_PASSWORD, or --email/--password).
     Returns full records: title, abstract, authors, venue, pdf link.

  2. Stealth browser (Scrapling) - used when the API refuses the request.
     openreview.net now answers unauthenticated API calls with
     403 ChallengeRequiredError, so the rendered venue page is read instead.
     This backend yields title + forum id + venue/year; it does NOT yield
     abstracts or author lists.

Records are written as JSONL, one paper per line, in the shape the
`deep-research-lit` skill's `scripts/paper_db.py` consumes.

Usage:
  paper_finder.py --list-venues
  paper_finder.py --mode scrape --config config.yaml
  paper_finder.py --mode download --jsonl results.jsonl --output-dir pdfs/
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, Iterable, List, Optional, Tuple

USER_AGENT = (
    "paper_finder/1.0 (academic literature search; contact: local user)"
)

# venue key -> OpenReview group id prefix
VENUES: Dict[str, str] = {
    "iclr": "ICLR.cc",
    "neurips": "NeurIPS.cc",
    "icml": "ICML.cc",
    "cvpr": "CVPR.cc",
    "iccv": "ICCV.cc",
}

API_V2 = "https://api2.openreview.net"
GROUP_URL = "https://openreview.net/group?id={group}&tab={tab}"
PDF_URL = "https://openreview.net/pdf?id={paper_id}"

# The venue page renders one tab at a time; posters hold the bulk of a
# conference, so poster + spotlight + oral are all collected.
ACCEPT_TABS = ("accept-poster", "accept-spotlight", "accept-oral")

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENV_PYTHON = os.path.join(PROJECT_ROOT, ".venv", "bin", "python")


# --------------------------------------------------------------------------- #
# scoring
# --------------------------------------------------------------------------- #
STOPWORDS = {
    "a", "an", "the", "of", "for", "and", "or", "to", "in", "on", "with",
    "via", "using", "towards", "toward", "by", "from", "at", "is", "are",
    "that", "this", "it", "as", "be", "we", "our",
}


def tokenize(text: str) -> List[str]:
    text = (text or "").lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return [t for t in text.split() if t and t not in STOPWORDS]


def score_record(record: Dict[str, Any], query_tokens: List[str]) -> float:
    """Weighted keyword overlap: title matches count more than abstract ones."""
    if not query_tokens:
        return 1.0
    title_tokens = set(tokenize(record.get("title", "")))
    abstract_tokens = set(tokenize(record.get("abstract", "")))
    score = 0.0
    for token in query_tokens:
        if token in title_tokens:
            score += 3.0
        elif token in abstract_tokens:
            score += 1.0
        elif len(token) > 4 and any(token in t for t in title_tokens):
            score += 1.5
    return score


# --------------------------------------------------------------------------- #
# bibtex
# --------------------------------------------------------------------------- #
def make_bibtex(record: Dict[str, Any]) -> str:
    def clean(value: str) -> str:
        return re.sub(r"[{}\\]", "", value or "").strip()

    first_author = "anonymous"
    authors = record.get("authors") or ""
    if isinstance(authors, list):
        authors = ", ".join(authors)
    if authors:
        first_author = authors.split(",")[0].split()[-1] if authors.split() else "anonymous"
    key = re.sub(r"[^A-Za-z0-9]", "", f"{first_author}{record.get('year', '')}{record.get('title', '')[:24]}")
    fields = [
        ("title", clean(record.get("title", ""))),
        ("author", clean(authors)),
        ("booktitle", clean(record.get("venue", ""))),
        ("year", str(record.get("year", ""))),
    ]
    if record.get("link"):
        fields.append(("url", record["link"]))
    body = ",\n".join(f"  {k} = {{{v}}}" for k, v in fields if v)
    return f"@{record.get('entry_type', 'inproceedings')}{{{key.lower()},\n{body}\n}}"


# --------------------------------------------------------------------------- #
# backend 1 - OpenReview REST API
# --------------------------------------------------------------------------- #
def api_get(url: str, email: Optional[str], password: Optional[str],
            retries: int = 3) -> Optional[Dict[str, Any]]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT,
                                                   "Accept": "application/json"})
    if email:
        token = urllib.request.HTTPPasswordMgr()
        # basic auth is what the openreview SDK does with credentials
        import base64
        raw = f"{email}:{password or ''}".encode()
        request.add_header("Authorization", "Basic " + base64.b64encode(raw).decode())

    for attempt in range(retries):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code in (401, 403):
                return None          # challenged or unauthenticated -> browser backend
            if attempt < retries - 1:
                time.sleep(2 * (attempt + 1))
                continue
            raise
        except (urllib.error.URLError, TimeoutError):
            if attempt < retries - 1:
                time.sleep(2 * (attempt + 1))
                continue
            raise
    return None


def fetch_accepted_api(venue_key: str, year: int, email: Optional[str],
                       password: Optional[str]) -> List[Dict[str, Any]]:
    prefix = VENUES[venue_key]
    invitation = f"{prefix}/{year}/Conference/-/Submission"
    records: List[Dict[str, Any]] = []
    offset, limit = 0, 1000

    while True:
        url = f"{API_V2}/notes?invitation={urllib.parse.quote(invitation)}&limit={limit}&offset={offset}"
        payload = api_get(url, email, password)
        if payload is None:
            return []
        notes = payload.get("notes") or []
        if not notes:
            break
        for note in notes:
            record = note_to_record(note, venue_key, year)
            if record:
                records.append(record)
        if len(notes) < limit:
            break
        offset += limit
        time.sleep(1)
    return records


def note_to_record(note: Dict[str, Any], venue_key: str, year: int) -> Optional[Dict[str, Any]]:
    content = note.get("content") or {}

    def value(key: str) -> Any:
        raw = content.get(key)
        if isinstance(raw, dict):
            return raw.get("value")
        return raw

    title = value("title")
    if not isinstance(title, str) or not title.strip():
        return None
    if re.fullmatch(r"Null\S+", title):
        return None

    venue_raw = value("venue")
    venue = venue_raw if isinstance(venue_raw, str) and venue_raw else f"{VENUES[venue_key]} {year}"

    # accepted only: the venue string of a rejected/withdrawn submission says so
    lowered = venue.lower()
    if any(word in lowered for word in ("submitted", "withdrawn", "rejected", "desk reject")):
        return None

    authors = value("authors") or []
    if isinstance(authors, str):
        authors = [authors]

    pdf = value("pdf") or ""
    if pdf and not pdf.startswith("http"):
        pdf = "https://openreview.net/" + pdf.lstrip("/")

    abstract = value("abstract") or ""
    if not isinstance(abstract, str):
        abstract = str(abstract)

    return {
        "title": title.strip(),
        "authors": authors,
        "abstract": abstract,
        "venue": venue,
        "year": year,
        "paperId": note.get("id") or value("paperhash") or "",
        "link": f"https://openreview.net/forum?id={note.get('id')}" if note.get("id") else "",
        "pdf": pdf,
        "arxiv_id": value("arxiv_id") or "",
        "entry_type": "inproceedings",
        "source": "openreview-api",
    }


# --------------------------------------------------------------------------- #
# backend 2 - stealth browser
# --------------------------------------------------------------------------- #
def browser_records(venue_key: str, year: int) -> List[Dict[str, Any]]:
    """Read the rendered venue page with a stealth browser.

    openreview.net answers unauthenticated API calls with
    403 ChallengeRequiredError, so the accepted-paper tables are read from the
    rendered page instead. One browser session is reused across tabs so the
    challenge cookie carries over; each tab is switched with a page_action
    click on the tab link.
    """
    try:
        from scrapling.fetchers import StealthySession
    except ImportError:
        raise SystemExit(
            "The browser backend needs Scrapling. Run this script with the project\n"
            f"virtualenv interpreter:  {VENV_PYTHON} {os.path.basename(__file__)} ...\n"
            "or install it:  uv pip install --python .venv/bin/python scrapling"
        )

    group = f"{VENUES[venue_key]}/{year}/Conference"
    seen: Dict[str, Dict[str, Any]] = {}

    def click_tab(page, tab: str) -> None:
        try:
            page.locator(f'a[href*="tab-{tab}"]').first.click(timeout=20000)
            page.wait_for_timeout(4000)
        except Exception:                            # noqa: BLE001 - tab may be absent
            pass

    with StealthySession(headless=True) as session:
        for tab in ACCEPT_TABS:
            url = GROUP_URL.format(group=group, tab=tab)
            try:
                page = session.fetch(
                    url,
                    headless=True,
                    timeout=90000,
                    network_idle=True,
                    wait_selector='a[href*="/forum?id="]',
                    page_action=lambda p, t=tab: click_tab(p, t),
                )
            except Exception as exc:                 # noqa: BLE001 - report and continue
                print(f"  ! tab {tab}: {type(exc).__name__}: {exc}", file=sys.stderr)
                continue

            found = 0
            for anchor in page.css('a[href*="/forum?id="]'):
                href = anchor.attrib.get("href", "")
                match = re.search(r"/forum\?id=([A-Za-z0-9_-]+)", href)
                title = (anchor.text or "").strip()
                if not match or not title:
                    continue
                paper_id = match.group(1)
                if paper_id in seen:
                    continue
                seen[paper_id] = {
                    "title": title,
                    "authors": [],
                    "abstract": "",
                    "venue": f"{VENUES[venue_key]} {year}",
                    "year": year,
                    "paperId": paper_id,
                    "link": f"https://openreview.net/forum?id={paper_id}",
                    "pdf": PDF_URL.format(paper_id=paper_id),
                    "arxiv_id": "",
                    "entry_type": "inproceedings",
                    "source": "openreview-browser",
                }
                found += 1
            print(f"     tab {tab}: +{found} new papers", file=sys.stderr)
    return list(seen.values())


# --------------------------------------------------------------------------- #
# config
# --------------------------------------------------------------------------- #
def load_config(path: str) -> Dict[str, Any]:
    try:
        import yaml
    except ImportError:
        raise SystemExit("PyYAML is required to read a config file: pip install pyyaml")
    with open(path, "r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle) or {}
    if not isinstance(config, dict):
        raise SystemExit(f"{path}: expected a YAML mapping at the top level")
    return config


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
    return slug[:60] or "search"


# --------------------------------------------------------------------------- #
# modes
# --------------------------------------------------------------------------- #
def cmd_list_venues(args: argparse.Namespace) -> int:
    print("Supported venues (key -> OpenReview group):")
    for key, prefix in sorted(VENUES.items()):
        print(f"  {key:<10} {prefix}/<year>/Conference")
    print()
    print("Years: any conference year OpenReview hosts (2020 onwards is reliable).")
    print("Credentials: set OPENREVIEW_EMAIL and OPENREVIEW_PASSWORD to use the API")
    print("backend (full abstracts + authors). Without them the stealth browser")
    print("backend is used, which returns titles only.")
    return 0


def cmd_scrape(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    searches = config.get("searches") or []
    if not searches:
        raise SystemExit(f"{args.config}: no 'searches' entries found")

    output_cfg = config.get("output") or {}
    root_template = output_cfg.get("root") or "paper-finder-output/{slug}"
    overwrite = bool(output_cfg.get("overwrite", True))

    email = args.email or os.environ.get("OPENREVIEW_EMAIL")
    password = args.password or os.environ.get("OPENREVIEW_PASSWORD")
    total_written = 0

    for search in searches:
        if not isinstance(search, dict):
            continue
        query = search.get("query") or ""
        num_results = int(search.get("num_results") or 50)
        venue_map = search.get("venues") or {}
        slug = slugify(query)
        root = root_template.replace("{slug}", slug).replace("{query}", slug)
        os.makedirs(root, exist_ok=True)

        query_tokens = tokenize(query)
        for venue_key, years in sorted(venue_map.items()):
            venue_key = venue_key.lower()
            if venue_key not in VENUES:
                print(f"  ! unknown venue '{venue_key}' (skipped)", file=sys.stderr)
                continue
            for year in years or []:
                year = int(year)
                print(f"  -> {venue_key} {year}: querying {query!r}", file=sys.stderr)

                records = fetch_accepted_api(venue_key, year, email, password) if email else []
                backend = "openreview-api"
                if not records:
                    records = browser_records(venue_key, year)
                    backend = "openreview-browser"
                if not records:
                    print(f"     no records returned for {venue_key} {year}", file=sys.stderr)
                    continue

                scored = [(score_record(r, query_tokens), r) for r in records]
                scored = [(s, r) for s, r in scored if s > 0]
                scored.sort(key=lambda pair: pair[0], reverse=True)
                chosen = [r for _, r in scored[:num_results]]

                for (score, _record), record in zip(scored[:num_results], chosen):
                    record["score"] = round(score, 2)
                    record["bibtex"] = make_bibtex(record)
                    record["keywords"] = query_tokens

                filename = os.path.join(root, f"papers_{venue_key}{year}_{slug}.jsonl")
                if os.path.exists(filename) and not overwrite:
                    print(f"     exists, skipped: {filename}", file=sys.stderr)
                    continue
                with open(filename, "w", encoding="utf-8") as handle:
                    for record in chosen:
                        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
                total_written += len(chosen)
                print(f"     {len(chosen):>4} papers via {backend} -> {filename}",
                      file=sys.stderr)
    print(json.dumps({"papers_written": total_written}, ensure_ascii=False))
    return 0


def cmd_download(args: argparse.Namespace) -> int:
    if not os.path.exists(args.jsonl):
        raise SystemExit(f"{args.jsonl}: not found")
    os.makedirs(args.output_dir, exist_ok=True)
    downloaded, skipped = 0, 0
    with open(args.jsonl, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            url = record.get("pdf") or record.get("link")
            if not url:
                skipped += 1
                continue
            if args.max_downloads and downloaded >= args.max_downloads:
                break
            name = re.sub(r"[^A-Za-z0-9._-]+", "_", record.get("title", "paper"))[:120]
            target = os.path.join(args.output_dir, f"{name}.pdf")
            try:
                request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
                with urllib.request.urlopen(request, timeout=120) as response:
                    data = response.read()
                if not data.startswith(b"%PDF"):
                    print(f"  ! not a PDF, skipped: {url}", file=sys.stderr)
                    skipped += 1
                    continue
                with open(target, "wb") as handle:
                    handle.write(data)
                downloaded += 1
            except Exception as exc:                 # noqa: BLE001 - report and continue
                print(f"  ! {url}: {type(exc).__name__}: {exc}", file=sys.stderr)
                skipped += 1
    print(json.dumps({"downloaded": downloaded, "skipped": skipped}, ensure_ascii=False))
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Find published conference papers by topic, venue and year.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--mode", choices=("scrape", "download"), default="scrape",
                        help="scrape: search venues per a config file. "
                             "download: fetch PDFs for records in a JSONL file.")
    parser.add_argument("--config", help="YAML config with 'searches:' and 'output:'")
    parser.add_argument("--jsonl", help="JSONL file of records (for --mode download)")
    parser.add_argument("--output-dir", default="paper-finder-pdfs",
                        help="where downloaded PDFs go (default: paper-finder-pdfs)")
    parser.add_argument("--max-downloads", type=int, default=0,
                        help="stop after N downloads (0 = no limit)")
    parser.add_argument("--list-venues", action="store_true",
                        help="print the supported venues and exit")
    parser.add_argument("--email", help="OpenReview email (or OPENREVIEW_EMAIL)")
    parser.add_argument("--password", help="OpenReview password (or OPENREVIEW_PASSWORD)")
    args = parser.parse_args(argv)

    if args.list_venues:
        return cmd_list_venues(args)
    if args.mode == "download":
        if not args.jsonl:
            parser.error("--mode download needs --jsonl")
        return cmd_download(args)
    if not args.config:
        parser.error("--mode scrape needs --config")
    return cmd_scrape(args)


if __name__ == "__main__":
    sys.exit(main())
