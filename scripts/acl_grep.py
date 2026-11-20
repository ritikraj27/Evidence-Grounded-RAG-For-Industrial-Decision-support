#!/usr/bin/env python3
"""Grep cached ACL Anthology volume pages for title fragments.

Usage: python3 scripts/acl_grep.py "vitamin" "docnli" ...
Scans every /tmp/acl_cache/vol_*.html and prints matching paper IDs + titles.
"""

from __future__ import annotations

import glob
import os
import re
import sys

PAT = re.compile(r"href=/?(\d{4}\.[a-z0-9\-]+\.\d+)/?>(.*?)</a>", re.S)


def main(argv):
    needles = [a.lower() for a in argv]
    if not needles:
        print("no needles")
        return 2
    files = sorted(glob.glob("/tmp/acl_cache/vol_*.html"))
    if not files:
        print("no cached volumes")
        return 2
    seen = set()
    for f in files:
        html = open(f, encoding="utf-8", errors="replace").read()
        vol = os.path.basename(f)[4:-5]
        for pid, raw in PAT.findall(html):
            t = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", raw)).strip()
            if not (4 <= len(t) <= 240):
                continue
            low = t.lower()
            if any(n in low for n in needles):
                key = (pid, t)
                if key in seen:
                    continue
                seen.add(key)
                print(f"{pid:34s} | {vol:22s} | {t}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
