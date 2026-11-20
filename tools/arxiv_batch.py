#!/usr/bin/env python3
"""Batch-verify arXiv IDs via the arXiv Atom API (id: lookups).

Usage: python3 tools/arxiv_batch.py ids.txt
Each line: an arXiv id, optionally with a version suffix (e.g. 2405.21044v1).
Prints: id | published | title | authors | journal_ref | doi
"""
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

API = "https://export.arxiv.org/api/query"
UA = "claude-code-paper-writing-skills/1.0 (arxiv_batch.py)"
A = "{http://www.w3.org/2005/Atom}"
AR = "{http://arxiv.org/schemas/atom}"
MIN_INTERVAL = 3.0


def fetch(ids):
    q = urllib.parse.urlencode(
        {"id_list": ",".join(ids), "max_results": len(ids)}
    )
    req = urllib.request.Request(f"{API}?{q}", headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def main():
    ids = [l.strip() for l in open(sys.argv[1]) if l.strip() and not l.startswith("#")]
    # arXiv allows id_list with many ids; chunk into groups of 25.
    for i in range(0, len(ids), 25):
        chunk = ids[i : i + 25]
        for attempt in range(3):
            try:
                raw = fetch(chunk)
                break
            except Exception as e:
                print(f"  retry {attempt+1}: {e}")
                time.sleep(5)
        else:
            continue
        root = ET.fromstring(raw)
        found = {}
        for e in root.findall(f"{A}entry"):
            eid = (e.findtext(f"{A}id") or "").rsplit("/", 1)[-1]
            base = eid.split("v")[0]
            title = " ".join((e.findtext(f"{A}title") or "").split())
            pub = (e.findtext(f"{A}published") or "")[:10]
            upd = (e.findtext(f"{A}updated") or "")[:10]
            jr = e.findtext(f"{AR}journal_ref") or ""
            doi = e.findtext(f"{AR}doi") or ""
            com = " ".join((e.findtext(f"{AR}comment") or "").split())[:120]
            authors = [
                " ".join((a.findtext(f"{A}name") or "").split())
                for a in e.findall(f"{A}author")
            ]
            found[base] = {
                "id": eid,
                "pub": pub,
                "upd": upd,
                "title": title,
                "journal": jr,
                "doi": doi,
                "comment": com,
                "authors": authors,
            }
        for want in chunk:
            base = want.split("v")[0]
            if base in found:
                f = found[base]
                print(f"OK   {base} | pub {f['pub']} (upd {f['upd']})")
                print(f"     {f['title']}")
                print(
                    f"     authors({len(f['authors'])}): "
                    + ", ".join(f["authors"][:5])
                    + (" et al." if len(f["authors"]) > 5 else "")
                )
                if f["journal"]:
                    print(f"     journal_ref: {f['journal']}")
                if f["doi"]:
                    print(f"     doi: {f['doi']}")
                if f["comment"]:
                    print(f"     comment: {f['comment']}")
                print()
            else:
                print(f"MISS {base}  <-- NOT FOUND in arXiv\n")
        time.sleep(MIN_INTERVAL)


if __name__ == "__main__":
    main()
