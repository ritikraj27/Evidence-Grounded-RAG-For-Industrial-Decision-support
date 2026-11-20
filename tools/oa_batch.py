#!/usr/bin/env python3
"""Batch-verify a list of paper titles/DOIs against OpenAlex.

Usage: python3 tools/oa_batch.py queries.txt
Each line of the file: "<query string>" or "doi:<10.xxxx/yyy>"
Prints compact verification lines.
"""
import json
import sys
import time
import urllib.parse
import urllib.request

MAIL = "ritikraj@example.com"


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": f"oa-batch/1.0 (mailto:{MAIL})"})
    with urllib.request.urlopen(req, timeout=45) as r:
        return json.load(r)


def fmt(w):
    loc = w.get("primary_location") or {}
    src = (loc.get("source") or {}).get("display_name") or "?"
    b = w.get("biblio") or {}
    pages = f"{b.get('first_page')}-{b.get('last_page')}" if b.get("first_page") else ""
    doi = (w.get("doi") or "").replace("https://doi.org/", "")
    auth = w.get("authorships") or []
    first = auth[0]["author"]["display_name"] if auth else "?"
    n = len(auth)
    return (
        f"{first} ({n} auth) | {w.get('publication_year')} | {src} | {pages} | "
        f"DOI {doi} | cites {w.get('cited_by_count')} | {w.get('title')}"
    )


def main():
    lines = [l.strip() for l in open(sys.argv[1]) if l.strip() and not l.startswith("#")]
    for q in lines:
        print(f"### {q}")
        try:
            if q.startswith("doi:"):
                url = f"https://api.openalex.org/works/doi:{urllib.parse.quote(q[4:])}?mailto={MAIL}"
                w = get(url)
                print("  OK  " + fmt(w))
            else:
                url = (
                    "https://api.openalex.org/works?search="
                    + urllib.parse.quote(q)
                    + f"&per_page=2&mailto={MAIL}"
                )
                d = get(url)
                for w in d.get("results", []):
                    print("  ->  " + fmt(w))
        except Exception as e:
            print(f"  FAIL: {type(e).__name__}: {e}")
        time.sleep(0.35)
        print()


if __name__ == "__main__":
    main()
