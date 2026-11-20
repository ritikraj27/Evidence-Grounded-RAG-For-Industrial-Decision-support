#!/usr/bin/env python3
"""Check every DOI listed in a markdown file against doi.org.

Usage: python3 scripts/check_dois.py research/04_contradiction.md
Prints OK / FAIL per DOI, and prints a corrected form when the ACL Anthology
record declares a different (working) DOI for the same anthology id.
"""

from __future__ import annotations

import re
import subprocess
import sys

DOI_RE = re.compile(r"10\.\d{4,9}/[^\s`)\],;]+")


def resolves(doi: str) -> bool:
    """Does doi.org hold a registration for this DOI?

    Asked for the metadata, not for the landing page. Following the redirect
    to the publisher and reading the status there answers a different
    question: ACM and MDPI answer an automated client with a non-200, so
    that method reported four correct DOIs as broken. Content negotiation
    returns the registered title and authors as JSON, and the registration
    is what is being checked.
    """
    r = subprocess.run(
        ["curl", "-sSL", "--max-time", "30",
         "-H", "Accept: application/vnd.citationstyles.csl+json",
         "-w", "\n%{http_code}", f"https://doi.org/{doi}"],
        capture_output=True, text=True, check=False,
    )
    body, _, status = r.stdout.rpartition("\n")
    if status.strip() != "200":
        return False
    # A registry that has nothing for this DOI answers 200 with an empty
    # record rather than a 404, so the body has to be checked too.
    return '"title"' in body or '"DOI"' in body


def anthology_doi(pid: str) -> str | None:
    r = subprocess.run(
        ["curl", "-sSL", "--max-time", "30", f"https://aclanthology.org/{pid}.bib"],
        capture_output=True, text=True, check=False,
    )
    m = re.search(r'doi\s*=\s*"(.*?)"', r.stdout)
    return m.group(1) if m else None


def main():
    path = sys.argv[1]
    text = open(path, encoding="utf-8").read()
    dois = []
    for d in DOI_RE.findall(text):
        d = d.rstrip(".")
        if d not in dois:
            dois.append(d)
    bad = []
    for d in dois:
        ok = resolves(d)
        print(f"{'OK  ' if ok else 'FAIL'} {d}")
        if not ok:
            bad.append(d)
    print(f"\n{len(dois) - len(bad)}/{len(dois)} resolve")
    for d in bad:
        pid = d.split("/")[-1]
        alt = anthology_doi(pid)
        print(f"  FIX {d} -> {alt}  (resolves={resolves(alt) if alt else 'n/a'})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
