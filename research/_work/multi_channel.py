#!/usr/bin/env python3
"""Multi-channel bibliographic verification for the MTP literature review.

OpenAlex's shared free budget and the Semantic Scholar anonymous pool are both
exhausted from this network, so verification runs over three channels that do
respond: the arXiv Atom API, the Crossref REST API and the DBLP publication
API. Every hit is normalised to a common record so a candidate citation can be
confirmed from whichever channel happens to index it.
"""
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

ARXIV = "https://export.arxiv.org/api/query"
CROSSREF = "https://api.crossref.org/works"
DBLP = "https://dblp.org/search/publ/api"
UA = "mtp-literature-review/1.0 (mailto:mtp-review@example.org)"
_ATOM = "{http://www.w3.org/2005/Atom}"
TIMEOUT = 45


def _get(url, tries=4, base_wait=8.0):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    wait = base_wait
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                return r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < tries - 1:
                print(f"    {e.code} -> wait {wait:.0f}s", file=sys.stderr)
                time.sleep(wait)
                wait *= 2
                continue
            raise
    raise RuntimeError("exhausted retries")


def arxiv(query, n=10):
    params = urllib.parse.urlencode({
        "search_query": query, "start": 0, "max_results": n,
        "sortBy": "relevance", "sortOrder": "descending",
    })
    root = ET.fromstring(_get(f"{ARXIV}?{params}"))
    out = []
    for e in root.findall(f"{_ATOM}entry"):
        def t(tag):
            el = e.find(tag)
            return " ".join(el.text.split()) if el is not None and el.text else ""
        aid = t(f"{_ATOM}id")
        m = re.search(r"abs/([^v]+)", aid)
        out.append({
            "channel": "arxiv",
            "arxiv_id": m.group(1) if m else aid,
            "title": t(f"{_ATOM}title"),
            "authors": [a.find(f"{_ATOM}name").text for a in e.findall(f"{_ATOM}author")
                        if a.find(f"{_ATOM}name") is not None],
            "abstract": t(f"{_ATOM}summary"),
            "published": t(f"{_ATOM}published")[:10],
            "updated": t(f"{_ATOM}updated")[:10],
            "comment": t(f"{_ATOM}comment"),
            "journal_ref": t(f"{_ATOM}journal_ref"),
            "doi": t(f"{_ATOM}doi"),
            "url": f"https://arxiv.org/abs/{m.group(1) if m else aid}",
        })
    return out


def crossref(query, n=8):
    params = urllib.parse.urlencode({
        "query.bibliographic": query, "rows": n,
        "select": "DOI,title,author,issued,container-title,type,abstract,URL,is-referenced-by-count",
        "mailto": "mtp-review@example.org",
    })
    data = json.loads(_get(f"{CROSSREF}?{params}"))
    out = []
    for it in data.get("message", {}).get("items", []):
        issued = (it.get("issued") or {}).get("date-parts") or [[None]]
        out.append({
            "channel": "crossref",
            "doi": it.get("DOI", ""),
            "title": " ".join((it.get("title") or [""])[0].split()),
            "authors": [f"{a.get('given','')} {a.get('family','')}".strip()
                        for a in (it.get("author") or [])],
            "year": issued[0][0] if issued and issued[0] else None,
            "venue": (it.get("container-title") or [""])[0],
            "type": it.get("type"),
            "abstract": (it.get("abstract") or "")[:2500],
            "cited_by": it.get("is-referenced-by-count"),
            "url": it.get("URL", ""),
        })
    return out


def dblp(query, n=8):
    params = urllib.parse.urlencode({
        "q": query, "format": "json", "h": n,
    })
    data = json.loads(_get(f"{DBLP}?{params}"))
    hits = ((data.get("result") or {}).get("hits") or {}).get("hit") or []
    out = []
    for h in hits:
        i = h.get("info") or {}
        if isinstance(i, list):
            i = i[0]
        authors = i.get("authors", {})
        if isinstance(authors, dict):
            authors = authors.get("author", [])
        if isinstance(authors, dict):
            authors = [authors]
        names = []
        for a in authors or []:
            if isinstance(a, dict):
                names.append(a.get("text", ""))
            else:
                names.append(str(a))
        out.append({
            "channel": "dblp",
            "title": " ".join((i.get("title") or "").split()),
            "authors": names,
            "year": i.get("year"),
            "venue": i.get("venue"),
            "doi": i.get("doi", ""),
            "url": i.get("ee", ""),
            "type": i.get("type"),
        })
    return out


def main():
    queries = json.load(open(sys.argv[1]))
    out = {}
    for label, spec in queries.items():
        rec = {"queries": spec if isinstance(spec, dict) else {"q": spec}}
        for chan, fn in (("arxiv", arxiv), ("crossref", crossref), ("dblp", dblp)):
            q = rec["queries"].get(chan) or rec["queries"].get("q")
            if not q:
                continue
            try:
                rec[chan] = fn(q)
                print(f"OK   {label}/{chan}: {len(rec[chan])}", file=sys.stderr)
            except Exception as e:
                rec[chan] = []
                rec.setdefault("errors", {})[chan] = str(e)
                print(f"FAIL {label}/{chan}: {e}", file=sys.stderr)
            time.sleep(4.0)
        out[label] = rec
    json.dump(out, open(sys.argv[2], "w"), indent=1)
    print("WROTE", sys.argv[2], file=sys.stderr)


if __name__ == "__main__":
    main()
