#!/usr/bin/env python3
"""Resolve the identifiers the direction check surfaced, and record them.

Every arXiv id and DOI that will appear in a deliverable must be resolved
against a live bibliographic API before it is written down. This script
resolves the batch, prints what it found, and appends the verified entries to
`research/00_citation_audit.md` — which is the file the consistency checker
requires every identifier in a deliverable to appear in.
"""
from __future__ import annotations

import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "research" / "00_citation_audit.md"
UA = "mtp-rag-framework/1.0 (academic research; contact: ritik@example.com)"

ARXIV_IDS = [
    "2509.07475",   # HALT-RAG
    "2608.22228",   # GRAB-RAG
    "2605.03534",   # SURE-RAG
    "2610.34684",   # Certify
    "2609.35794",   # Sieve and Sage
    "2610.01218",   # AGO AI Quality Gate
    "2607.05438",   # Modality Relevance is not Modality Utility
    "2609.35782",   # Financial Evidence Crowding
    "2606.28367",   # Beyond the Reranker
    "2504.13128",   # FreshStack
    "2506.12071",   # T2-RAGBench
    "2607.25959",   # Kontrast
    "2509.23233",   # WIKICOLLIDE / CLAIRE
    "2609.07075",   # Hierarchical Consistency Framework
    "2610.08026",   # The Labeling Problem in Hallucination Detection Benchmarks
    "2605.27157",   # Detecting Is Not Resolving
    "2603.21172",   # Entropy Alone is Insufficient
    "2511.11847",   # Manufacturing-safety chatbot benchmark
    "2606.20898",   # Token Tax of Epistemic Accuracy
    "2603.20534",   # Industrial-scale RAG for requirements engineering
    "2606.07401",   # RealDocBench
]

DOIS = [
    "10.18653/v1/2026.findings-acl.371",   # SupChain-Bench
    "10.18653/v1/2024.naacl-long.167",      # ExpertQA
    "10.18653/2026.emnlp-main.1456",       # IndusSpec-QA
]


def fetch(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.loads(r.read().decode("utf-8"))


def resolve_arxiv(aid: str) -> dict | None:
    url = ("https://export.arxiv.org/api/query?id_list=" + aid)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=40) as r:
        text = r.read().decode("utf-8")
    m = re.search(r"<entry>(.*?)</entry>", text, re.S)
    if not m:
        return None
    e = m.group(1)
    title = re.search(r"<title>(.*?)</title>", e, re.S)
    published = re.search(r"<published>(.*?)</published>", e)
    comment = re.search(r"<arxiv:comment[^>]*>(.*?)</arxiv:comment>", e, re.S)
    authors = re.findall(r"<name>(.*?)</name>", e)
    return {
        "id": aid,
        "title": " ".join(title.group(1).split()) if title else "",
        "published": published.group(1)[:10] if published else "",
        "comment": " ".join(comment.group(1).split()) if comment else "",
        "authors": [a.strip() for a in authors],
    }


def resolve_doi(doi: str) -> dict | None:
    url = ("https://api.crossref.org/works/" + urllib.parse.quote(doi, safe=""))
    try:
        d = fetch(url)["message"]
    except Exception:
        return None
    return {
        "doi": doi,
        "title": (d.get("title") or [""])[0],
        "container": (d.get("container-title") or [""])[0],
        "page": d.get("page", ""),
        "year": (d.get("issued", {}).get("date-parts") or [[""]])[0][0],
    }


def main() -> int:
    lines = []
    bad = []

    print("=== arXiv ===")
    for aid in ARXIV_IDS:
        try:
            r = resolve_arxiv(aid)
        except Exception as e:  # noqa: BLE001
            print(f"  {aid}  REQUEST-FAIL {e}")
            bad.append(aid)
            continue
        if not r or not r["title"]:
            print(f"  {aid}  NOT FOUND")
            bad.append(aid)
            continue
        print(f"  {aid}  {r['title'][:72]}")
        print(f"           {r['published']}  {r['comment'][:60]}")
        lines.append(
            f"| arXiv:{aid} | {r['title']} | {r['published']} | "
            f"{r['comment'] or '—'} | {', '.join(r['authors'][:4])} |"
        )
        time.sleep(0.4)

    print("\n=== Crossref ===")
    for doi in DOIS:
        r = resolve_doi(doi)
        if not r:
            print(f"  {doi}  NOT RESOLVED")
            bad.append(doi)
            continue
        print(f"  {doi}  {r['title'][:66]}")
        print(f"           {r['container']} {r['year']} p.{r['page']}")
        lines.append(
            f"| {doi} | {r['title']} | {r['container']} {r['year']}, p.{r['page']} | "
            f"— | — |"
        )
        time.sleep(0.3)

    if bad:
        print(f"\n!! unresolved: {bad}")
        return 1

    header = (
        "\n---\n\n## Additions from the direction check (31 October 2026)\n\n"
        "Every identifier below was resolved live on 31 October 2026 against the\n"
        "arXiv API (title, date, and the venue comment in the arXiv metadata) and\n"
        "the Crossref REST API (title, container, pages). The first column is the\n"
        "identifier as it appears in the deliverables.\n\n"
        "| Identifier | Title | Venue / date | Note | Authors |\n"
        "|---|---|---|---|---|\n"
    )
    AUDIT.write_text(AUDIT.read_text(encoding="utf-8") + header + "\n".join(lines) + "\n",
                    encoding="utf-8")
    print(f"\nappended {len(lines)} verified entries to {AUDIT.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
