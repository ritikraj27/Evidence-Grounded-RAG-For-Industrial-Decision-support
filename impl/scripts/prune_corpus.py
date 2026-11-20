#!/usr/bin/env python3
"""Remove corpus files that the current CATEGORIES mapping no longer lists.

The corpus directory is a cache: `build_corpus.py` skips a file that already
exists. That is what makes the build cheap, but it also means a file left
behind by an earlier mapping survives forever -- and an earlier mapping is
exactly how this corpus ended up holding two copies of two articles.

This script reconciles the directory with the mapping: files whose slug is
not in the mapping are moved aside into `data/corpus/_retired/` rather than
deleted, so nothing is destroyed and the build can be inspected.
"""
from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_corpus import CATEGORIES, CORPUS, ROOT  # noqa: E402


def main() -> int:
    expected = {
        (cat, re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-") + ".md")
        for cat, titles in CATEGORIES.items()
        for title in titles
    }
    retired_dir = CORPUS / "_retired"
    moved = []
    for path in sorted(CORPUS.glob("*/*.md")):
        rel = path.relative_to(CORPUS)
        cat, name = rel.parts[0], rel.name
        if (cat, name) in expected:
            continue
        retired_dir.mkdir(parents=True, exist_ok=True)
        dest = retired_dir / f"{cat}__{name}"
        shutil.move(str(path), str(dest))
        moved.append(f"{cat}/{name}")

    print(f"expected files : {len(expected)}")
    on_disk = len(list(CORPUS.glob("*/*.md")))
    print(f"files on disk  : {on_disk}")
    if moved:
        print(f"retired ({len(moved)}):")
        for m in moved:
            print(f"   {m}")
    else:
        print("retired: none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
