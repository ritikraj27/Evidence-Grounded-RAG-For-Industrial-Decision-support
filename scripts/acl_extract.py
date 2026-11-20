#!/usr/bin/env python3
"""Extract full records (title, authors, abstract, DOI, venue) from cached
ACL Anthology volume pages.

Usage:
  python3 scripts/acl_extract.py --ids 2025.acl-long.1476,2026.emnlp-main.1033
  python3 scripts/acl_extract.py --grep "conflict" [--limit 40]
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re

TITLE_PAT = re.compile(r"href=/?(\d{4}\.[a-z0-9\-]+\.\d+)/?>(.*?)</a>", re.S)
ABS_PAT = re.compile(
    r'id="abstract-([\d\-]+)"[^>]*>(.*?)</div>', re.S
)


def clean(s: str) -> str:
    s = re.sub(r"<[^>]+>", " ", s)
    s = s.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    s = s.replace("&quot;", '"').replace("&#39;", "'").replace("&nbsp;", " ")
    return re.sub(r"\s+", " ", s).strip()


def load_volume(path: str) -> dict:
    html = open(path, encoding="utf-8", errors="replace").read()
    vol = os.path.basename(path)[4:-5]
    abstracts = {}
    for aid, body in ABS_PAT.findall(html):
        abstracts[aid.replace("--", "-").replace("-", "-")] = clean(body)
    # abstract ids look like "abstract-2025--acl-long--1476"
    abstracts = {}
    for m in re.finditer(
        r'id="?abstract-(\d{4})--([a-z0-9\-]+)--(\d+)"?[^>]*>(.*?)</div>', html, re.S
    ):
        abstracts[f"{m.group(1)}.{m.group(2)}.{m.group(3)}"] = clean(m.group(4))

    recs = {}
    for pid, raw in TITLE_PAT.findall(html):
        title = clean(raw)
        if not (4 <= len(title) <= 240):
            continue
        if pid in recs:
            continue
        recs[pid] = {"id": pid, "title": title, "venue": vol}
    for pid, r in recs.items():
        r["abstract"] = abstracts.get(pid, "")
    return recs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", help="comma-separated anthology ids")
    ap.add_argument("--grep", help="case-insensitive title substring")
    ap.add_argument("--limit", type=int, default=60)
    ap.add_argument("--json", help="write to json")
    ap.add_argument("--abstracts", action="store_true")
    args = ap.parse_args()

    allr = {}
    for f in sorted(glob.glob("/tmp/acl_cache/vol_*.html")):
        allr.update(load_volume(f))

    out = []
    if args.ids:
        want = {i.strip() for i in args.ids.split(",") if i.strip()}
        out = [allr[i] for i in want if i in allr]
    elif args.grep:
        g = args.grep.lower()
        out = [r for r in allr.values() if g in r["title"].lower()][: args.limit]
    else:
        ap.error("need --ids or --grep")

    for r in sorted(out, key=lambda x: x["id"]):
        print(f"\n### {r['id']}  [{r['venue']}]")
        print(f"  {r['title']}")
        if args.abstracts and r.get("abstract"):
            print(f"  ABS: {r['abstract'][:1000]}")
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(out, fh, indent=1, ensure_ascii=False)
        print(f"\n[written] {args.json} ({len(out)} records)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
