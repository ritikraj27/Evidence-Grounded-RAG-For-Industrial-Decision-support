#!/usr/bin/env python3
"""Resolve the canonical Wikipedia title for each query string.

The corpus builder listed a few article titles that do not exist under those
exact names ("Facility layout", "8D problem solving", ...). Wikipedia's parse
API returns `missingtitle` for them rather than following the redirect, so
those documents were silently dropped from the corpus. This script resolves
each to its real title via the search API, so the builder can fetch them.
"""
from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request

API = "https://en.wikipedia.org/w/api.php"
UA = "mtp-rag-framework/1.0 (academic research; contact: ritik@example.com)"

QUERIES = [
    "Kanban signalling manufacturing",
    "Supplier development",
    "8D problem solving",
    "Facility layout",
    "Warehouse layout",
    "Bathroom analogy reliability",
]


def api(params: dict) -> dict:
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def main() -> int:
    for q in QUERIES:
        d = api({
            "action": "query", "list": "search", "srsearch": q,
            "srlimit": 4, "format": "json", "formatversion": "2",
        })
        hits = d.get("query", {}).get("search", [])
        print(f"\n=== {q!r}")
        for h in hits:
            print(f"    {h['title']!r}")
        time.sleep(0.4)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
