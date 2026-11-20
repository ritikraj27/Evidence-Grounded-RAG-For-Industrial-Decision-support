#!/usr/bin/env python3
"""Resolve paper titles via the DBLP API (authoritative for CS/NLP).

Usage: python3 scripts/dblp_resolve.py @terms.txt
Prints: title | year | venue | DOI | type | url
"""

from __future__ import annotations

import json
import sys
import time
import urllib.parse
import urllib.request

BASE = "https://dblp.org/search/publ/api"
UA = "claude-code-mtp-dblp/1.0"


def query(term, tries=3):
    params = {"q": term, "format": "json", "h": 5}
    url = f"{BASE}?{urllib.parse.urlencode(params)}"
    delay = 1.0
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=45) as r:
                data = json.load(r)
            hits = data.get("result", {}).get("hits", {}).get("hit", [])
            return [h["info"] for h in hits]
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
            hits = query(t)
        except Exception as e:  # noqa: BLE001
            print(f"ERROR     {t[:60]}  ({e})")
            continue
        if not hits:
            print(f"NO-HIT    {t[:70]}")
            continue
        for i, h in enumerate(hits[:3]):
            au = h.get("authors", {}).get("author", [])
            au = [au] if isinstance(au, dict) else au
            names = ", ".join(a["text"] for a in au[:3])
            print(f"{'TOP ' if i==0 else 'alt '}     {h.get('title','')[:78]}")
            print(
                f"          {h.get('year')} | {h.get('venue','')[:40]} | {h.get('type','')} | cites={h.get('citations',0)}"
            )
            print(f"          doi={h.get('doi','-')}  authors={names[:60]}")
        time.sleep(0.7)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
