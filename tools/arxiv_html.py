#!/usr/bin/env python3
"""arXiv search via Scrapling (HTML endpoint — distinct from the rate-limited API).

Usage:
    .venv/bin/python tools/arxiv_html.py "query string" [size]
    .venv/bin/python tools/arxiv_html.py --abs 2405.21044     # fetch one abs page
"""
import re
import sys
import urllib.parse

from scrapling.fetchers import Fetcher

UA_DEFAULT = None


def clean(s):
    return " ".join((s or "").split())


def search(q, size=25):
    # arXiv's search endpoint rejects size values other than 25/50/100/200 (HTTP 400).
    page_size = 25 if size <= 25 else (50 if size <= 50 else 100)
    url = (
        "https://arxiv.org/search/?searchtype=all&query="
        + urllib.parse.quote(q)
        + f"&size={page_size}"
    )
    r = Fetcher.get(url, timeout=45, stealthy_headers=True)
    out = []
    for li in r.css("li.arxiv-result"):
        title = li.css("p.title")
        ids = li.css("p.list-title")
        authors = li.css("p.authors")
        date = li.css("p.is-size-7")
        aid = ""
        for a in li.css("p.list-title a"):
            m = re.search(r"arXiv:([\d.]+v?\d*)", clean(a.text))
            if m:
                aid = m.group(1)
                break
        t = ""
        if title:
            raw = title[0].html_content
            raw = re.sub(r"<[^>]+>", " ", raw)
            t = clean(raw)
            t = re.sub(r"^Title:\s*", "", t)
        au = clean(authors[0].text) if authors else ""
        au = re.sub(r"^Authors?:\s*", "", au)
        dt = clean(date[0].text) if date else ""
        dt = re.sub(r"^Submitted.*?;\s*", "", dt)
        out.append((aid, t, au[:170], dt[:60]))
    return out[:size]


def _txt(el):
    """Full text of an element including nested <a>/<span> (Scrapling's .text skips them)."""
    if el is None:
        return ""
    raw = el.html_content
    raw = re.sub(r"<[^>]+>", " ", raw)
    return clean(raw)


def abs_page(aid):
    url = f"https://arxiv.org/abs/{aid}"
    r = Fetcher.get(url, timeout=45, stealthy_headers=True)
    if r.status != 200:
        return None
    title = r.css("h1.title")
    auth = r.css("div.authors")
    jr = r.css("td.tablecell.jref")
    com = r.css("td.tablecell.comments")
    subj = r.css("td.tablecell.subjects")
    doi = r.css("td.tablecell.doi")
    b = r.css("blockquote.abstract")
    t = re.sub(r"^Title:\s*", "", _txt(title[0] if title else None))
    a = re.sub(r"^Authors?:\s*", "", _txt(auth[0] if auth else None))
    return {
        "id": aid,
        "title": t,
        "authors": a,
        "journal_ref": _txt(jr[0] if jr else None),
        "comments": _txt(com[0] if com else None),
        "subjects": _txt(subj[0] if subj else None),
        "doi": _txt(doi[0] if doi else None),
        "abstract": _txt(b[0] if b else None)[:900],
    }


def main():
    args = sys.argv[1:]
    if args and args[0] == "--abs":
        for aid in args[1:]:
            d = abs_page(aid)
            print("=" * 70)
            if not d:
                print(f"{aid}: NOT FOUND")
                continue
            print(f"ID      : {d['id']}")
            print(f"TITLE   : {d['title']}")
            print(f"AUTHORS : {d['authors'][:250]}")
            print(f"JOURNAL : {d['journal_ref']}")
            print(f"COMMENTS: {d['comments']}")
            print(f"SUBJECT : {d['subjects']}")
            print(f"DOI     : {d['doi']}")
            print(f"ABSTRACT: {d['abstract']}")
        return
    q = args[0]
    size = int(args[1]) if len(args) > 1 else 15
    res = search(q, size)
    print(f"QUERY: {q}  -> {len(res)} results\n")
    for aid, t, au, dt in res:
        print(f"[{aid}] {t}")
        print(f"    {au}")
        print(f"    {dt}\n")


if __name__ == "__main__":
    main()
