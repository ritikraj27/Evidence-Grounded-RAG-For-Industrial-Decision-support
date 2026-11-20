#!/usr/bin/env python3
"""Create the focus-domain corpus: supply chain management only.

The thesis focuses on one industrial domain. The full six-category corpus
stays in place, because the cross-category transfer objective (RO4/H4.1)
needs a subset of categories to transfer to held-out ones. This script
materialises the focus subset as a corpus of its own so the same pipeline,
with the same code and no conditionals, can be evaluated on it.

Setting `MTP_VARIANT=focus` points the framework at
`data/corpus_focus`, `data/benchmark_focus`, `artifacts_focus` and
`results_focus`.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

FOCUS = "supply_chain_management"
CORPUS = ROOT / "data" / "corpus"
FOCUS_DIR = ROOT / "data" / "corpus_focus"


def main() -> int:
    manifest = json.loads((CORPUS / "manifest.json").read_text(encoding="utf-8"))
    keep = [d for d in manifest if d["category"] == FOCUS]
    if not keep:
        print(f"!! no documents in category {FOCUS}")
        return 1

    if FOCUS_DIR.exists():
        shutil.rmtree(FOCUS_DIR)
    FOCUS_DIR.mkdir(parents=True, exist_ok=True)
    (FOCUS_DIR / FOCUS).mkdir(parents=True, exist_ok=True)

    out_manifest = []
    for d in keep:
        src = ROOT / d["path"]
        dest = FOCUS_DIR / FOCUS / src.name
        shutil.copy2(src, dest)
        out_manifest.append({
            "title": d["title"],
            "category": d["category"],
            "path": str(dest.relative_to(ROOT)),
            "bytes": d["bytes"],
        })

    (FOCUS_DIR / "manifest.json").write_text(
        json.dumps(out_manifest, indent=2), encoding="utf-8")
    total_bytes = sum(d["bytes"] for d in out_manifest)
    print(f"[focus] {len(out_manifest)} documents, {total_bytes:,} bytes "
          f"-> {FOCUS_DIR}")
    for d in out_manifest:
        print(f"    {d['title']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
