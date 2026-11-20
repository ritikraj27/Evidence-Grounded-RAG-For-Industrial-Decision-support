#!/usr/bin/env python3
"""Batch-verify a list of arXiv IDs against the arXiv API in ONE request (id_list).

Usage: python3 scripts/verify_arxiv_ids.py 1809.05053 1910.14599 ...
Output: one line per requested ID -> RESOLVED title (year) | NOT FOUND
Also accepts a file with one ID per line via @path.
"""

from __future__ import annotations

import sys
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

API = "https://export.arxiv.org/api/query"
UA = "claude-code-mtp-verify/1.0"
_ATOM = "{http://www.w3.org/2005/Atom}"
_ARX = "{http://arxiv.org/schemas/atom}"


def resolve(ids):
    q = urllib.parse.urlencode(
        {"id_list": ",".join(ids), "max_results": len(ids)}
    )
    req = urllib.request.Request(
        f"{API}?{q}", headers={"User-Agent": UA}
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return ET.fromstring(r.read())


def main(argv):
    ids = []
    for a in argv:
        if a.startswith("@"):
            with open(a[1:], encoding="utf-8") as fh:
                ids.extend(l.strip() for l in fh if l.strip() and not l.startswith("#"))
        else:
            ids.append(a.strip())
    ids = [i for i in ids if i]
    if not ids:
        print("no ids")
        return 2

    root = resolve(ids)
    found = {}
    for e in root.findall(f"{_ATOM}entry"):
        aid = e.findtext(f"{_ATOM}id", "")
        m = aid.rsplit("/", 1)[-1]
        base = m.split("v")[0]
        title = " ".join((e.findtext(f"{_ATOM}title", "") or "").split())
        pub = e.findtext(f"{_ATOM}published", "")[:10]
        doi = e.findtext(f"{_ARX}doi", "") or ""
        jref = e.findtext(f"{_ARX}journal_ref", "") or ""
        found[base] = (title, pub, doi, jref)

    for i in ids:
        base = i.split("v")[0]
        if base in found:
            t, p, d, j = found[base]
            print(f"RESOLVED  {i:14s} {p[:4]}  {t}\n            doi={d or '-'}  jref={j or '-'}")
        else:
            print(f"NOT-FOUND {i}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
