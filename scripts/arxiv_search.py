#!/usr/bin/env python3
"""Search arXiv via its server-rendered HTML search (no API rate limit).

Usage:
  python3 scripts/arxiv_search.py "query string" [--max 25] [--json out.json]
  python3 scripts/arxiv_search.py --ids 2103.08541,2401.00396   # exact ids
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time

CACHE = "/tmp/ax_cache"


def curl(url: str, key: str, tries: int = 5) -> str:
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, key + ".html")
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return open(path, encoding="utf-8", errors="replace").read()
    delay = 6.0
    out = ""
    for attempt in range(tries):
        r = subprocess.run(
            ["curl", "-sSL", "--max-time", "90", url,
             "-A", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
             "-w", "\n__CODE__%{http_code}"],
            capture_output=True, text=True, check=False,
        )
        body = r.stdout
        code = ""
        m = re.search(r"__CODE__(\d+)\s*$", body)
        if m:
            code = m.group(1)
            body = body[: m.start()]
        if code == "200" and len(body) > 2000:
            out = body
            break
        # 429/503 -> back off; also rotate to a plain (unquoted) query as fallback
        time.sleep(delay)
        delay = min(delay * 2, 60)
    if out:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(out)
    return out


def parse(html: str) -> list[dict]:
    items = []
    # each result: <li class="arxiv-result"> ... <a href="https://arxiv.org/abs/XXXX"> ... title ...
    for block in re.split(r'<li class="arxiv-result">', html)[1:]:
        aid = re.search(r'arxiv\.org/abs/([\d.]+v?\d*)', block)
        title = re.search(r'<p class="title is-5 mathjax">(.*?)</p>', block, re.S)
        auth = re.search(r'<p class="authors">(.*?)</p>', block, re.S)
        ab = re.search(r'<span class="abstract-full[^"]*">(.*?)</span>', block, re.S)
        dat = re.search(r'<p class="is-size-7">(.*?)</p>', block, re.S)
        prim = re.search(r'<span class="tag is-small is-link tooltip is-tooltip-top"[^>]*>([^<]*)</span>', block)
        cm = re.search(r'<span class="has-text-grey-dark mathjax">(.*?)</span>', block, re.S)

        def clean(s):
            return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s or "")).strip()

        items.append({
            "id": aid.group(1) if aid else None,
            "title": clean(title.group(1)) if title else None,
            "authors": clean(auth.group(1)) if auth else None,
            "abstract": clean(ab.group(1)) if ab else None,
            "date": clean(dat.group(1)) if dat else None,
            "primary": clean(prim.group(1)) if prim else None,
            "comment": clean(cm.group(1)) if cm else None,
        })
    return items


def search(q: str, size: int = 25) -> list[dict]:
    import urllib.parse
    url = ("https://arxiv.org/search/?searchtype=all&query="
           + urllib.parse.quote(q) + f"&size={size}")
    key = "s_" + re.sub(r"[^A-Za-z0-9]+", "_", q)[:80] + f"_{size}"
    return parse(curl(url, key))


def by_id(aid: str) -> dict:
    url = f"https://arxiv.org/abs/{aid}"
    html = curl(url, "abs_" + aid)
    t = re.search(r'<h1 class="title mathjax">(.*?)</h1>', html, re.S)
    a = re.search(r'<div class="authors">(.*?)</div>', html, re.S)
    ab = re.search(r'<blockquote class="abstract mathjax">(.*?)</blockquote>', html, re.S)
    cm = re.search(r'<td class="tablecell comments mathjax">(.*?)</td>', html, re.S)
    jr = re.search(r'<td class="tablecell jref">(.*?)</td>', html, re.S)
    subj = re.search(r'<td class="tablecell subjects">(.*?)</td>', html, re.S)

    def clean(s):
        return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s or "")).strip()

    doi = re.search(r'<a[^>]*href="https://doi.org/([^"]+)"[^>]*>', html)
    return {
        "id": aid,
        "title": clean(t.group(1)) if t else None,
        "authors": clean(a.group(1)) if a else None,
        "abstract": clean(ab.group(1)) if ab else None,
        "comment": clean(cm.group(1)) if cm else None,
        "jref": clean(jr.group(1)) if jr else None,
        "subjects": clean(subj.group(1)) if subj else None,
        "doi": doi.group(1) if doi else None,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query", nargs="?")
    ap.add_argument("--ids", help="comma-separated exact arXiv ids")
    ap.add_argument("--max", type=int, default=25)
    ap.add_argument("--full", action="store_true", help="include abstract")
    ap.add_argument("--json", help="write results to this json file")
    args = ap.parse_args()

    results = []
    if args.ids:
        for aid in [i.strip() for i in args.ids.split(",") if i.strip()]:
            results.append(by_id(aid))
    elif args.query:
        results = search(args.query, args.max)
    else:
        ap.error("need query or --ids")

    for r in results:
        print(f"\n### {r.get('id')}  [{r.get('primary') or r.get('subjects','')[:40]}]")
        print(f"  {r.get('title')}")
        print(f"  {r.get('authors')}")
        if r.get('date'):
            print(f"  date: {r['date'][:60]}")
        if r.get('jref'):
            print(f"  jref: {r['jref'][:80]}")
        if r.get('comment'):
            print(f"  note: {r['comment'][:90]}")
        if r.get('doi'):
            print(f"  doi:  {r['doi']}")
        if args.full and r.get('abstract'):
            print(f"  ABS: {r['abstract'][:1100]}")

    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(results, fh, indent=1, ensure_ascii=False)
        print(f"\n[written] {args.json} ({len(results)} records)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
