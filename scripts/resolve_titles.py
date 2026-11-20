#!/usr/bin/env python3
"""Resolve paper titles to verified metadata via OpenAlex (free-text search + polite pool).

Usage: python3 scripts/resolve_titles.py @titles.txt
Each line: one search phrase (keep it SHORT and distinctive).
Output per hit: resolved title | year | venue | DOI | cited_by_count
"""

from __future__ import annotations

import json
import sys
import time
import urllib.parse
import urllib.request

BASE = "https://api.openalex.org/works"
UA = "claude-code-mtp-resolve/1.0 (mailto:mtp@iitkgp.ac.in)"


def search(term, tries=4):
    params = {
        "search": term,
        "per-page": 5,
        "mailto": "mtp@iitkgp.ac.in",
        "select": "id,title,publication_year,doi,primary_location,ids,cited_by_count,type",
    }
    url = f"{BASE}?{urllib.parse.urlencode(params)}"
    delay = 2.0
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=45) as r:
                return json.load(r).get("results", [])
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < tries - 1:
                time.sleep(delay)
                delay *= 2
                continue
            raise
    return []


def main(argv):
    terms = []
    for a in argv:
        if a.startswith("@"):
            with open(a[1:], encoding="utf-8") as fh:
                terms.extend(l.strip() for l in fh if l.strip() and not l.startswith("#"))
        else:
            terms.append(a.strip())
    for t in terms:
        try:
            res = search(t)
        except Exception as e:  # noqa: BLE001
            print(f"ERROR     {t[:60]}  ({e})")
            continue
        if not res:
            print(f"NO-HIT    {t[:70]}")
            continue
        for i, w in enumerate(res[:3]):
            loc = w.get("primary_location") or {}
            src = (loc.get("source") or {}).get("display_name") or "-"
            doi = (w.get("doi") or "").replace("https://doi.org/", "")
            tag = "TOP " if i == 0 else "alt "
            print(f"{tag}      {(w.get('title') or '')[:76]}")
            print(
                f"          {w.get('publication_year')} | {w.get('type')} | cites={w.get('cited_by_count')} | {src[:44]}"
            )
            print(f"          doi={doi or '-'}")
        time.sleep(1.5)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
