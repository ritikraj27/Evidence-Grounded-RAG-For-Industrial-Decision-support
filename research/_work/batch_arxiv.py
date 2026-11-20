#!/usr/bin/env python3
"""Batch arXiv metadata collection for the MTP literature review.

Runs a list of queries against the arXiv Atom API with a polite interval and
dumps every result to a single JSON file so the result set can be filtered
offline without re-hitting the network.
"""
import json
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

API_URL = "https://export.arxiv.org/api/query"
MIN_INTERVAL = 6.0
TIMEOUT = 40
_ATOM = "{http://www.w3.org/2005/Atom}"
_ARXIV = "{http://arxiv.org/schemas/atom}"
UA = "mtp-literature-review/1.0 (arxiv batch collector)"


def parse_feed(xml_text):
    root = ET.fromstring(xml_text)
    out = []
    for entry in root.findall(f"{_ATOM}entry"):
        def txt(tag):
            el = entry.find(tag)
            return el.text if el is not None else ""

        authors = [
            a.find(f"{_ATOM}name").text
            for a in entry.findall(f"{_ATOM}author")
            if a.find(f"{_ATOM}name") is not None
        ]
        aid = txt(f"{_ATOM}id")
        m = re.search(r"abs/([^v]+)v?(\d*)$", aid)
        arxiv_id = m.group(1) if m else aid
        cats = [c.get("term") for c in entry.findall(f"{_ATOM}category")]
        prim = entry.find(f"{_ATOM}primary_category")
        out.append({
            "arxiv_id": arxiv_id,
            "title": " ".join(txt(f"{_ATOM}title").split()),
            "authors": authors,
            "abstract": " ".join(txt(f"{_ATOM}summary").split()),
            "published": txt(f"{_ATOM}published")[:10],
            "updated": txt(f"{_ATOM}updated")[:10],
            "categories": cats,
            "primary_category": prim.get("term") if prim is not None else "",
            "comment": txt(f"{_ATOM}comment") if entry.find(f"{_ATOM}comment") is not None else "",
            "journal_ref": txt(f"{_ATOM}journal_ref") if entry.find(f"{_ATOM}journal_ref") is not None else "",
            "doi": txt(f"{_ATOM}doi") if entry.find(f"{_ATOM}doi") is not None else "",
            "abs_url": f"https://arxiv.org/abs/{arxiv_id}",
        })
    return out


def query(q, max_results=12):
    params = urllib.parse.urlencode({
        "search_query": q,
        "start": 0,
        "max_results": max_results,
        "sortBy": "relevance",
        "sortOrder": "descending",
    })
    req = urllib.request.Request(f"{API_URL}?{params}", headers={"User-Agent": UA})
    delay = 10.0
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                return parse_feed(r.read().decode("utf-8", "replace"))
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 4:
                print(f"  429 on '{q}', backing off {delay:.0f}s", file=sys.stderr)
                time.sleep(delay)
                delay *= 2
                continue
            raise
    raise RuntimeError("exhausted retries")


def main():
    queries = json.load(open(sys.argv[1]))
    collected = {}
    for label, q in queries.items():
        try:
            res = query(q, max_results=12)
            collected[label] = {"query": q, "results": res}
            print(f"OK   {label}: {len(res)}", file=sys.stderr)
        except Exception as e:
            collected[label] = {"query": q, "error": str(e), "results": []}
            print(f"FAIL {label}: {e}", file=sys.stderr)
        time.sleep(MIN_INTERVAL)
    json.dump(collected, open(sys.argv[2], "w"), indent=1)
    print("WROTE", sys.argv[2], file=sys.stderr)


if __name__ == "__main__":
    main()
