#!/usr/bin/env python3
"""Batch OpenAlex metadata collection for the MTP literature review.

OpenAlex is fully open and far less restrictive than the arXiv Atom API, so it
carries the bulk of the verification load. Results are written to a single JSON
file for offline filtering.
"""
import json
import sys
import time
import urllib.parse
import urllib.request

BASE_URL = "https://api.openalex.org/works"
UA = "mtp-literature-review/1.0 (mailto:mtp-review@example.org)"
TIMEOUT = 45


def search(q, max_results=10, year="", extra=None):
    params = {
        "search": q,
        "per-page": max_results,
        "mailto": "mtp-review@example.org",
    }
    if year:
        params["filter"] = f"from_publication_date:{year}-01-01" if year.endswith("-") else year
    if extra:
        params.update(extra)
    url = f"{BASE_URL}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def compact(w):
    loc = w.get("primary_location") or {}
    src = (loc.get("source") or {}).get("display_name") or ""
    ids = w.get("ids") or {}
    authors = [
        a.get("author", {}).get("display_name")
        for a in (w.get("authorships") or [])
    ]
    return {
        "openalex_id": w.get("id", "").split("/")[-1],
        "title": w.get("title") or w.get("display_name"),
        "year": w.get("publication_year"),
        "date": w.get("publication_date"),
        "doi": (w.get("doi") or "").replace("https://doi.org/", ""),
        "arxiv_id": (ids.get("openalex", "") and "") or "",
        "type": w.get("type"),
        "venue": src,
        "authors": [a for a in authors if a],
        "cited_by_count": w.get("cited_by_count"),
        "is_oa": (w.get("open_access") or {}).get("is_oa"),
        "abstract_inverted_index": w.get("abstract_inverted_index"),
    }


def rebuild_abstract(inv):
    if not inv:
        return ""
    positions = {}
    for word, idxs in inv.items():
        for i in idxs:
            positions[i] = word
    return " ".join(positions[i] for i in sorted(positions))


def main():
    queries = json.load(open(sys.argv[1]))
    out = {}
    for label, spec in queries.items():
        q = spec["query"] if isinstance(spec, dict) else spec
        year = spec.get("year", "") if isinstance(spec, dict) else ""
        try:
            data = search(q, max_results=10, year=year)
            rows = []
            for w in data.get("results", []):
                c = compact(w)
                c["abstract"] = rebuild_abstract(w.get("abstract_inverted_index"))
                c.pop("abstract_inverted_index", None)
                rows.append(c)
            out[label] = {"query": q, "results": rows}
            print(f"OK   {label}: {len(rows)}", file=sys.stderr)
        except Exception as e:
            out[label] = {"query": q, "error": str(e), "results": []}
            print(f"FAIL {label}: {e}", file=sys.stderr)
        time.sleep(1.2)
    json.dump(out, open(sys.argv[2], "w"), indent=1)
    print("WROTE", sys.argv[2], file=sys.stderr)


if __name__ == "__main__":
    main()
