#!/usr/bin/env python3
"""Find ACL Anthology papers by title fragment and return verified metadata.

Downloads the static volume index pages (no JS, no rate limits), greps titles
across all needles in ONE pass per volume, then fetches the canonical .bib
record for each hit so metadata is exact (not fuzzy-matched).

Usage:
  python3 scripts/acl_find.py --volumes 2021.emnlp-main,2020.emnlp-main \
      "VitaminC" "ConTRoL" "DocNLI"
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys

BASE = "https://aclanthology.org"
CACHE = os.path.expanduser("/tmp/acl_cache")


def fetch(url: str, cache_key: str | None = None) -> str:
    path = os.path.join(CACHE, cache_key) if cache_key else None
    if path and os.path.exists(path) and os.path.getsize(path) > 0:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return fh.read()
    r = subprocess.run(
        ["curl", "-sSL", "--max-time", "120", "--retry", "2", url],
        capture_output=True, text=True, check=False,
    )
    out = r.stdout
    if path and out:
        os.makedirs(CACHE, exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(out)
    return out


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("needles", nargs="+")
    ap.add_argument("--volumes", required=True, help="comma-separated volume ids")
    ap.add_argument("--full", action="store_true", help="print full bib record")
    args = ap.parse_args()

    vols = [v.strip() for v in args.volumes.split(",") if v.strip()]
    needles = [(n, norm(n)) for n in args.needles]

    # Anchor content may contain <span class="acl-fixed-case"> around acronyms,
    # so capture up to </a> and strip markup afterwards.
    pat = re.compile(r"href=/?(\d{4}\.[a-z0-9\-]+\.\d+)/?>(.*?)</a>", re.S)
    found: dict[str, list[tuple[str, str]]] = {n: [] for n, _ in needles}

    for v in vols:
        html = fetch(f"{BASE}/volumes/{v}/", cache_key=f"vol_{v}.html")
        if not html or len(html) < 5000:
            print(f"  [skip] volume {v} unavailable", file=sys.stderr)
            continue
        entries = []
        for pid, raw in pat.findall(html):
            title = re.sub(r"<[^>]+>", "", raw)
            title = re.sub(r"\s+", " ", title).strip()
            if 4 <= len(title) <= 240:
                entries.append((pid, title))
        for n, nn in needles:
            for pid, title in entries:
                if nn and nn in norm(title):
                    if (pid, title) not in found[n]:
                        found[n].append((pid, title))
        print(f"  [vol] {v}: {len(entries)} entries scanned", file=sys.stderr)

    for n, _ in needles:
        print(f"\n######## {n}")
        if not found[n]:
            print("  NO HIT in the listed volumes")
            continue
        for pid, title in found[n]:
            b = fetch(f"{BASE}/{pid}.bib", cache_key=f"bib_{pid}.bib")
            g = lambda p: (re.search(p, b, re.S).group(1) if re.search(p, b, re.S) else "-")
            au = re.findall(r'author\s*=\s*"(.*?)"', b, re.S)
            names = ", ".join(a.split(" and ")[0] for a in au[:4])
            print(f"  ID      {pid}")
            print(f"  TITLE   {' '.join(g(r'title\s*=\s*"(.*?)"').split())}")
            print(f"  AUTHORS {names}")
            print(f"  YEAR    {g(r'year\s*=\s*"(.*?)"')}   VENUE {g(r'booktitle\s*=\s*"(.*?)"')}")
            print(f"  DOI     {g(r'doi\s*=\s*"(.*?)"')}")
            print(f"  URL     {g(r'url\s*=\s*"(.*?)"')}")
            if args.full:
                print("  ---- bib ----")
                print("  " + b.replace("\n", "\n  ")[:2000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
