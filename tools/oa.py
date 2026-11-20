#!/usr/bin/env python3
"""OpenAlex query helper for citation verification.

Usage:
    python3 tools/oa.py "query string" [per_page]
    python3 tools/oa.py --doi "10.1145/1571941.1572114"
"""
import json
import sys
import urllib.parse
import urllib.request

MAIL = "ritikraj@example.com"


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": f"oa-helper/1.0 (mailto:{MAIL})"})
    with urllib.request.urlopen(req, timeout=45) as r:
        return json.load(r)


def show(w):
    loc = w.get("primary_location") or {}
    src = (loc.get("source") or {}).get("display_name")
    b = w.get("biblio") or {}
    pages = f"{b.get('first_page')}-{b.get('last_page')}" if b.get("first_page") else ""
    vol = f"vol {b.get('volume')}" if b.get("volume") else ""
    doi = (w.get("doi") or "").replace("https://doi.org/", "")
    auth = [a["author"]["display_name"] for a in w.get("authorships", [])]
    aid = (w.get("ids") or {}).get("openalex")
    print(f"  TITLE : {w.get('title')}")
    print(f"  AUTH  : {', '.join(auth[:8])}{' et al.' if len(auth) > 8 else ''}")
    print(f"  YEAR  : {w.get('publication_year')} | VENUE: {src} | {vol} {pages}")
    print(f"  DOI   : {doi}")
    print(f"  CITES : {w.get('cited_by_count')} | OA_ID: {aid}")
    oa = w.get("open_access") or {}
    if oa.get("oa_url"):
        print(f"  OA_URL: {oa.get('oa_url')}")
    print()


def main():
    args = sys.argv[1:]
    if args and args[0] == "--doi":
        d = args[1]
        url = f"https://api.openalex.org/works/doi:{urllib.parse.quote(d)}?mailto={MAIL}"
        try:
            show(get(url))
        except Exception as e:
            print(f"  NOT FOUND for DOI {d}: {e}")
        return
    q = args[0]
    per = args[1] if len(args) > 1 else "5"
    url = (
        "https://api.openalex.org/works?search="
        + urllib.parse.quote(q)
        + f"&per_page={per}&mailto={MAIL}"
    )
    d = get(url)
    print(f"QUERY: {q}  -> {d.get('meta',{}).get('count')} results\n")
    for w in d.get("results", []):
        show(w)


if __name__ == "__main__":
    main()
