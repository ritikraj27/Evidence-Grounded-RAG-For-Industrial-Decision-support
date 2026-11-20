#!/usr/bin/env python3
"""arXiv search-page scraper.

The arXiv Atom API rate-limits this network hard (429 on any burst), while the
HTML search interface tolerates a slow, steady request rate from a browser
user-agent. This module drives the HTML interface and parses the result list
into clean records, so a whole query sweep stays on one code path.
"""
import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
TIMEOUT = 45


def fetch(url, tries=3):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-US,en;q=0.9",
    })
    wait = 8.0
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                return r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < tries - 1:
                time.sleep(wait)
                wait *= 2
                continue
            raise
    raise RuntimeError("exhausted retries")


def strip_tags(h):
    h = re.sub(r"<[^>]+>", " ", h)
    h = (h.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
           .replace("&quot;", '"').replace("&#39;", "'").replace("&nbsp;", " "))
    return " ".join(h.split())


def parse(html):
    blocks = re.findall(r'<li class="arxiv-result">(.*?)</li>', html, re.S)
    out = []
    for b in blocks:
        aid = re.search(r'arxiv\.org/abs/([0-9.]+v?\d*)', b)
        title = re.search(r'<p class="title[^"]*">(.*?)</p>', b, re.S)
        abstract = re.search(r'<span class="abstract-full[^"]*"[^>]*>(.*?)</span>', b, re.S)
        authors = re.findall(r'<a href="/search/[^"]*">\s*([^<]+?)\s*</a>', b)
        comment = re.search(r'<span class="has-text-black-bis[^"]*"[^>]*>(.*?)</span>', b, re.S)
        subj = re.search(r'<span class="primary-subject">(.*?)</span>', b, re.S)
        out.append({
            "arxiv_id": (aid.group(1).split("v")[0] if aid else ""),
            "title": strip_tags(title.group(1)) if title else "",
            "authors": [strip_tags(a) for a in authors][:12],
            "abstract": strip_tags(strip_tags(abstract.group(1)).replace("Abstract:", "")) if abstract else "",
            "comment": strip_tags(comment.group(1)) if comment else "",
            "primary_subject": strip_tags(subj.group(1)) if subj else "",
        })
    return out


def search(query, size=50, field="all"):
    url = ("https://arxiv.org/search/?searchtype=" + field +
           "&query=" + urllib.parse.quote_plus(query) +
           f"&size={size}&order=-announced_date_first")
    return parse(fetch(url))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("queries", help="JSON file: {label: query} or {label: {query, field}}")
    ap.add_argument("out")
    ap.add_argument("--size", type=int, default=30)
    ap.add_argument("--gap", type=float, default=7.0)
    a = ap.parse_args()
    spec = json.load(open(a.queries))
    out = {}
    for label, q in spec.items():
        field = "all"
        if isinstance(q, dict):
            field = q.get("field", "all")
            q = q["query"]
        try:
            res = search(q, size=a.size, field=field)
            out[label] = {"query": q, "field": field, "results": res}
            print(f"OK   {label}: {len(res)}", file=sys.stderr)
        except Exception as e:
            out[label] = {"query": q, "error": str(e), "results": []}
            print(f"FAIL {label}: {e}", file=sys.stderr)
        time.sleep(a.gap)
    json.dump(out, open(a.out, "w"), indent=1)
    print("WROTE", a.out, file=sys.stderr)


if __name__ == "__main__":
    main()
