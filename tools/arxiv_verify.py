#!/usr/bin/env python3
"""Batch-verify arXiv IDs by fetching each abs page (authoritative).

Usage: .venv/bin/python tools/arxiv_verify.py ids.txt
"""
import sys
import time

sys.path.insert(0, "tools")
from arxiv_html import abs_page  # noqa: E402

ids = [l.strip() for l in open(sys.argv[1]) if l.strip() and not l.startswith("#")]
for aid in ids:
    try:
        d = abs_page(aid)
    except Exception as e:
        d = None
        print(f"ERROR {aid}: {e}")
    print("=" * 72)
    if not d:
        print(f"{aid}:  *** NOT FOUND / NOT ON ARXIV ***")
        continue
    print(f"ID      : {d['id']}")
    print(f"TITLE   : {d['title']}")
    print(f"AUTHORS : {d['authors'][:260]}")
    if d["journal_ref"]:
        print(f"JOURNAL : {d['journal_ref']}")
    if d["comments"]:
        print(f"COMMENTS: {d['comments'][:200]}")
    if d["doi"]:
        print(f"DOI     : {d['doi']}")
    print(f"SUBJECT : {d['subjects'][:120]}")
    print(f"ABSTRACT: {d['abstract'][:700]}")
    time.sleep(1.0)
