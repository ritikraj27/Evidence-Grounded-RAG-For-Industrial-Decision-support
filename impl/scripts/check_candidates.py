#!/usr/bin/env python3
"""Check which candidate Wikipedia titles resolve and how long the article is."""
from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request

API = "https://en.wikipedia.org/w/api.php"
UA = "mtp-rag-framework/1.0 (academic research; contact: ritik@example.com)"

CANDIDATES = [
    "Kanban",
    "Kanban (signal)",
    "Strategic sourcing",
    "Eight disciplines problem solving",
    "Material handling",
    "Warehouse",
    "Redundancy (engineering)",
    "Maintainability",
    "Availability (engineering)",
    "Reliability theory",
    "Six Sigma",
    "Production planning",
]


def main() -> int:
    for t in CANDIDATES:
        url = API + "?" + urllib.parse.urlencode({
            "action": "parse", "page": t, "prop": "text",
            "format": "json", "formatversion": "2", "redirects": "1",
        })
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                d = json.loads(r.read().decode("utf-8"))
        except Exception as e:  # noqa: BLE001
            print(f"  {t!r:45s} REQUEST-FAIL {e}")
            continue
        if "error" in d:
            print(f"  {t!r:45s} {d['error'].get('code')}")
        else:
            txt = d.get("parse", {}).get("text", "")
            print(f"  {t!r:45s} OK  html_len={len(txt):>7d}")
        time.sleep(0.35)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
