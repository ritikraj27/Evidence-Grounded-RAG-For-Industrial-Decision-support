#!/usr/bin/env python3
"""DBLP bibliographic lookup — no auth, no aggressive rate limits.

Usage: python3 tools/dblp.py "query string" [limit]
"""
import json
import sys
import time
import urllib.parse
import urllib.request


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "dblp-helper/1.0"})
    with urllib.request.urlopen(req, timeout=45) as r:
        return json.load(r)


def main():
    q = sys.argv[1]
    lim = sys.argv[2] if len(sys.argv) > 2 else "4"
    url = (
        "https://dblp.org/search/publ/api?q="
        + urllib.parse.quote(q)
        + f"&format=json&h={lim}"
    )
    d = get(url)
    hits = d.get("result", {}).get("hits", {})
    total = hits.get("@total", "0")
    print(f"QUERY: {q}  -> {total} hits\n")
    for h in hits.get("hit", []):
        i = h.get("info", {})
        au = i.get("authors", {}).get("author", [])
        if isinstance(au, dict):
            au = [au]
        names = [a.get("text") if isinstance(a, dict) else a for a in au]
        print(f"  TITLE : {i.get('title')}")
        print(f"  AUTH  : {', '.join(str(n) for n in names[:8])}")
        print(f"  YEAR  : {i.get('year')} | VENUE: {i.get('venue')} | TYPE: {i.get('type')}")
        print(f"  PAGES : {i.get('pages')} | VOL: {i.get('volume')}")
        doi = i.get("doi")
        if doi:
            print(f"  DOI   : {doi}")
        ee = i.get("ee")
        if isinstance(ee, str):
            print(f"  EE    : {ee}")
        elif isinstance(ee, list) and ee:
            print(f"  EE    : {ee[0]}")
        print()


if __name__ == "__main__":
    main()
