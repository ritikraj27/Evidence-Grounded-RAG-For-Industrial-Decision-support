#!/usr/bin/env python3
"""Resolve paper titles to verified metadata via the Crossref REST API.

Usage: python3 scripts/crossref_resolve.py @terms.txt
Each line: a search phrase (title fragment works best).
Prints top matches with DOI, container-title (venue), year, type.
"""

from __future__ import annotations

import json
import sys
import time
import urllib.parse
import urllib.request

BASE = "https://api.crossref.org/works"
UA = "claude-code-mtp-crossref/1.0 (mailto:mtp@iitkgp.ac.in)"


def query(term, tries=3):
    params = {
        "query.bibliographic": term,
        "rows": 4,
        "select": "DOI,title,container-title,issued,type,author,is-referenced-by-count",
        "mailto": "mtp@iitkgp.ac.in",
    }
    url = f"{BASE}?{urllib.parse.urlencode(params)}"
    delay = 1.5
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=45) as r:
                return json.load(r)["message"]["items"]
        except Exception:
            if attempt < tries - 1:
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
            items = query(t)
        except Exception as e:  # noqa: BLE001
            print(f"ERROR     {t[:60]}  ({e})")
            continue
        if not items:
            print(f"NO-HIT    {t[:70]}")
            continue
        for i, it in enumerate(items[:3]):
            title = (it.get("title") or ["?"])[0]
            venue = (it.get("container-title") or ["-"])[0]
            yr = (it.get("issued", {}).get("date-parts") or [[None]])[0][0]
            auth = it.get("author") or []
            first = f"{auth[0].get('family','?')}" if auth else "?"
            print(f"{'TOP ' if i==0 else 'alt '}     {title[:76]}")
            print(f"          {yr} | {venue[:52]} | cites={it.get('is-referenced-by-count',0)} | first-author={first}")
            print(f"          doi={it.get('DOI','-')}")
        time.sleep(0.8)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
