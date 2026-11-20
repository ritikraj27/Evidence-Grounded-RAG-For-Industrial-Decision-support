#!/usr/bin/env python3
"""Resolve every arXiv identifier that appears in a deliverable template.

An identifier in a bibliography is a promise that the reader can follow. The
project's citation audit already covers the identifiers it knows about, but a
template can grow a new citation that the audit never saw, and a wrong
identifier is worse than a missing one: it looks verified.

For each identifier this script fetches the arXiv abstract page, reads the
title, and prints the identifier beside the title the deliverable claims for
it, so that the two can be compared. It writes the result to
`research/01_citation_resolution.md`.

Usage:

    python impl/scripts/verify_all_citations.py
"""
from __future__ import annotations

import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = ROOT / "deliverables" / "templates"
OUT = ROOT / "research" / "01_citation_resolution.md"

UA = "mtp-rag-framework/1.0 (academic research; thesis citation check)"

TITLE_RE = re.compile(r'<h1 class="title[^"]*">(.*?)</h1>', re.S)
DATE_RE = re.compile(r'"citation_date"\s+content="([^"]+)"')
#: An identifier appears in a template in two forms: as "arXiv:2401.12345" in
#: the prose, and as "\url{https://arxiv.org/abs/2401.12345}" in a LaTeX
#: bibliography. The second form was not matched, so the bibliography entries
#: were never resolved -- and an unresolved identifier is an unverified one.
ID_RE = re.compile(r"(?:arXiv:|arxiv\.org/abs/)(\d{4}\.\d{4,5})")


def _claims() -> dict[str, list[str]]:
    """Every identifier in the templates, with the text that names it."""
    out: dict[str, list[str]] = {}
    for p in sorted(TEMPLATES.rglob("*")):
        if p.suffix not in (".md", ".tex", ".py") or not p.is_file():
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except Exception:
            continue
        for m in ID_RE.finditer(text):
            aid = m.group(1)
            # The claim is the nearest name before the identifier: the text
            # between the previous sentence break and the identifier.
            start = max(text.rfind(".", 0, m.start()), text.rfind("\n", 0, m.start()))
            frag = text[start + 1:m.start()].strip()
            frag = re.sub(r"[\s()\[\]`*,;:]+", " ", frag).strip()
            out.setdefault(aid, [])
            if frag and frag not in out[aid]:
                out[aid].append(frag)
    return out


def _fetch(aid: str) -> tuple[str, str]:
    url = f"https://arxiv.org/abs/{aid}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=45) as r:
        html = r.read().decode("utf-8", "replace")
    m = TITLE_RE.search(html)
    title = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", m.group(1))).strip() \
        if m else "NO TITLE FOUND"
    # arXiv writes the descriptor as "Title:" inside the heading; the actual
    # title is what follows it.
    title = re.sub(r"^Title:\s*", "", title).strip()
    d = DATE_RE.search(html)
    return title, (d.group(1) if d else "?")


def main() -> int:
    claims = _claims()
    lines = [
        "# Citation resolution — every arXiv identifier in the deliverable "
        "templates",
        "",
        "Each identifier was resolved against arxiv.org and the title the "
        "record carries is printed beside the name the deliverable claims "
        "for it. A row where the two disagree is a wrong identifier.",
        "",
        "| arXiv | claimed as | resolved title | submitted |",
        "|---|---|---|---|",
    ]
    problems = []
    for n, aid in enumerate(sorted(claims), 1):
        try:
            title, date = _fetch(aid)
        except urllib.error.HTTPError as e:
            title, date = f"HTTP {e.code}", "?"
        except Exception as e:  # noqa: BLE001
            title, date = f"UNREACHABLE ({type(e).__name__})", "?"
        claimed = "; ".join(claims[aid])[:120] or "—"
        lines.append(f"| {aid} | {claimed} | {title} | {date} |")
        if title.startswith(("NO TITLE", "HTTP", "UNREACHABLE")):
            problems.append(f"{aid}: {title}")
        print(f"[{n}/{len(claims)}] {aid}: {title[:90]}", flush=True)
        time.sleep(1.2)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nwrote {OUT}")
    if problems:
        print(f"!! identifiers that did not resolve: {problems}")
        return 1
    print("every identifier resolved")
    return 0


if __name__ == "__main__":
    sys.exit(main())
