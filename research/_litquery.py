#!/usr/bin/env python3
"""Robust multi-source literature query helper (arXiv / Crossref).

Usage:
  python3 research/_litquery.py arxiv "all:\"time series\" AND all:\"language model\"" [max]
  python3 research/_litquery.py crossref <issn> "<query>" [rows]
  python3 research/_litquery.py crossref-title "<title words>" [rows]
  python3 research/_litquery.py doi <doi>
"""
import json
import sys
import time
import urllib.parse
import urllib.request
import urllib.error

UA = "MTPLit/1.0 (mailto:ritikraj@example.com)"


def get(url, timeout=30, retries=5):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    delay = 4
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as exc:
            if exc.code in (429, 503) and attempt < retries - 1:
                time.sleep(delay)
                delay = min(delay * 2, 45)
                continue
            raise
        except urllib.error.URLError:
            if attempt < retries - 1:
                time.sleep(delay)
                delay = min(delay * 2, 45)
                continue
            raise
    raise RuntimeError("unreachable")


def arxiv(query, max_results=6):
    import xml.etree.ElementTree as ET

    url = (
        "https://export.arxiv.org/api/query?search_query="
        + urllib.parse.quote(query)
        + f"&max_results={max_results}&sortBy=relevance"
    )
    raw = get(url)
    A = "{http://www.w3.org/2005/Atom}"
    X = "{http://arxiv.org/schemas/atom}"
    root = ET.fromstring(raw)
    out = []
    for e in root.findall(A + "entry"):
        jr = e.find(X + "journal_ref")
        cm = e.find(X + "comment")
        out.append(
            {
                "id": e.find(A + "id").text.split("/abs/")[-1],
                "title": " ".join(e.find(A + "title").text.split()),
                "authors": [a.find(A + "name").text for a in e.findall(A + "author")][:6],
                "published": e.find(A + "published").text[:10],
                "journal_ref": jr.text if jr is not None else "",
                "comment": (cm.text or "") if cm is not None else "",
                "summary": " ".join(e.find(A + "summary").text.split()),
            }
        )
    return out


def crossref(issn, query, rows=12):
    url = (
        f"https://api.crossref.org/journals/{issn}/works"
        f"?filter=from-pub-date:2023-01-01&query.bibliographic="
        + urllib.parse.quote(query)
        + f"&rows={rows}&select=DOI,title,volume,page,issued,author,container-title"
    )
    try:
        raw = get(url)
    except Exception as exc:
        return {"error": str(exc)}
    try:
        data = json.loads(raw)
    except Exception:
        return {"error": "non-json: " + raw[:200]}
    items = []
    for it in data.get("message", {}).get("items", []):
        items.append(
            {
                "doi": it.get("DOI"),
                "title": (it.get("title") or ["?"])[0],
                "venue": (it.get("container-title") or ["?"])[0],
                "volume": it.get("volume"),
                "page": it.get("page"),
                "year": (it.get("issued", {}).get("date-parts") or [["?"]])[0][0],
                "authors": [
                    (a.get("given", "") + " " + a.get("family", "")).strip()
                    for a in it.get("author", [])[:4]
                ],
            }
        )
    return items


def arxiv_ids(ids, show_abstract=True):
    import xml.etree.ElementTree as ET

    url = (
        "https://export.arxiv.org/api/query?id_list="
        + urllib.parse.quote(",".join(ids))
        + "&max_results=40"
    )
    raw = get(url, timeout=45)
    A = "{http://www.w3.org/2005/Atom}"
    X = "{http://arxiv.org/schemas/atom}"
    root = ET.fromstring(raw)
    out = []
    for e in root.findall(A + "entry"):
        jr = e.find(X + "journal_ref")
        cm = e.find(X + "comment")
        out.append(
            {
                "id": e.find(A + "id").text.split("/abs/")[-1],
                "title": " ".join(e.find(A + "title").text.split()),
                "authors": [a.find(A + "name").text for a in e.findall(A + "author")][:8],
                "published": e.find(A + "published").text[:10],
                "journal_ref": jr.text if jr is not None else "",
                "comment": (cm.text or "") if cm is not None else "",
                "summary": " ".join(e.find(A + "summary").text.split()),
            }
        )
    return out


def crossref_title(title, rows=8):
    url = (
        "https://api.crossref.org/works?query.bibliographic="
        + urllib.parse.quote(title)
        + f"&rows={rows}&select=DOI,title,volume,page,issued,author,container-title"
    )
    raw = get(url)
    data = json.loads(raw)
    items = []
    for it in data.get("message", {}).get("items", []):
        items.append(
            {
                "doi": it.get("DOI"),
                "title": (it.get("title") or ["?"])[0],
                "venue": (it.get("container-title") or ["?"])[0],
                "volume": it.get("volume"),
                "page": it.get("page"),
                "year": (it.get("issued", {}).get("date-parts") or [["?"]])[0][0],
                "authors": [
                    (a.get("given", "") + " " + a.get("family", "")).strip()
                    for a in it.get("author", [])[:4]
                ],
            }
        )
    return items


def doi_lookup(doi):
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi)
    raw = get(url)
    m = json.loads(raw)["message"]
    return {
        "doi": m.get("DOI"),
        "title": (m.get("title") or ["?"])[0],
        "venue": (m.get("container-title") or ["?"])[0],
        "volume": m.get("volume"),
        "page": m.get("page"),
        "year": (m.get("issued", {}).get("date-parts") or [["?"]])[0][0],
        "authors": [
            (a.get("given", "") + " " + a.get("family", "")).strip()
            for a in m.get("author", [])[:8]
        ],
    }


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "arxiv":
        for p in arxiv(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 6):
            print(f"{p['id']} | {p['published']} | {p['title'][:100]}")
            print(f"    AUTH {p['authors'][:4]}")
            if p["journal_ref"]:
                print(f"    JOURNAL {p['journal_ref'][:80]}")
            print(f"    {p['summary'][:340]}")
            print()
    elif cmd == "crossref":
        res = crossref(sys.argv[2], sys.argv[3], int(sys.argv[4]) if len(sys.argv) > 4 else 12)
        if isinstance(res, dict):
            print("ERROR:", res)
        else:
            for it in res:
                print(f"{it['year']} | v{it['volume']} p{it['page']} | {it['title'][:88]}")
                print(f"    {it['venue'][:60]} | DOI {it['doi']} | {it['authors']}")
    elif cmd == "arxiv-ids":
        for p in arxiv_ids(sys.argv[2].split(",")):
            print(f"{p['id']} | {p['published']} | {p['title'][:110]}")
            print(f"    AUTH {p['authors'][:5]}")
            if p["journal_ref"]:
                print(f"    JOURNAL {p['journal_ref'][:90]}")
            if p["comment"]:
                print(f"    NOTE {p['comment'][:90]}")
            print(f"    {p['summary'][:1000]}")
            print()
    elif cmd == "crossref-title":
        for it in crossref_title(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 8):
            print(f"{it['year']} | {it['title'][:95]}")
            print(f"    {it['venue'][:55]} | v{it['volume']} p{it['page']} | DOI {it['doi']}")
            print(f"    {it['authors']}")
    elif cmd == "doi":
        try:
            print(json.dumps(doi_lookup(sys.argv[2]), indent=2, ensure_ascii=False))
        except Exception as exc:
            print("LOOKUP FAILED:", exc)
