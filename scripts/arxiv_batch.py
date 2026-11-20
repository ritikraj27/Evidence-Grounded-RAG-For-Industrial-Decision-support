#!/usr/bin/env python3
"""Run a batch of arXiv HTML searches and write a compact JSON index.

Usage: python3 scripts/arxiv_batch.py @queries.txt out.json
Each line of queries.txt is one arXiv search query.
"""

from __future__ import annotations

import json
import sys
import time

sys.path.insert(0, "/Users/ritikraj/Documents/MTP/scripts")
from arxiv_search import search  # noqa: E402


def main():
    qf, out = sys.argv[1].lstrip("@"), sys.argv[2]
    with open(qf, encoding="utf-8") as fh:
        queries = [l.strip() for l in fh if l.strip() and not l.startswith("#")]
    allr = {}
    for q in queries:
        try:
            items = search(q, 20)
        except Exception as e:  # noqa: BLE001
            print(f"ERR {q}: {e}", file=sys.stderr)
            items = []
        allr[q] = [
            {
                "id": i.get("id"),
                "title": i.get("title"),
                "date": (i.get("date") or "")[:40],
                "primary": (i.get("primary") or "")[:60],
                "comment": (i.get("comment") or "")[:90],
                "abstract": (i.get("abstract") or "")[:900],
            }
            for i in items
        ]
        print(f"{len(items):3d}  {q}", file=sys.stderr)
        time.sleep(7.0)
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(allr, fh, indent=1, ensure_ascii=False)
    print(f"[written] {out}")


if __name__ == "__main__":
    raise SystemExit(main())
