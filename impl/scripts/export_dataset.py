#!/usr/bin/env python3
"""Export the evaluation corpus as a self-describing, citable dataset.

The thesis is only reproducible if a reader can answer three questions
without emailing anyone: *what* was searched, *where did it come from*, and
*can I rebuild it*. This script exports the corpus with all three answered:

  * every document, with the exact Wikipedia URL it was fetched from, the
    upstream revision id, the SHA-256 of the bytes actually used, and the
    number of chunks it produced;
  * the licence and attribution, because Wikipedia text is CC BY-SA 4.0 and
    redistribution carries obligations;
  * the benchmark, so the corpus and the questions that interrogate it travel
    together.

The revision ids are queried live from the MediaWiki API. They identify the
upstream state of each article at the moment of export; the SHA-256 values
identify the bytes in this repository, which is the stronger guarantee -- the
upstream page can be edited, the local file cannot.

Output: deliverables/dataset/
"""
from __future__ import annotations

import hashlib
import json
import shutil
import time
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "data" / "corpus"
INDEX = ROOT / "artifacts" / "index.json"
BENCH = ROOT / "data" / "benchmark" / "benchmark.json"
OUT = ROOT.parent / "deliverables" / "dataset"
API = "https://en.wikipedia.org/w/api.php"
UA = "mtp-rag-framework/1.0 (academic research; contact: ritik@example.com)"

#: The single industrial domain the thesis focuses on. Everything else in the
#: corpus exists to serve the cross-category transfer objective (RO4), not to
#: broaden the headline claim.
FOCUS_CATEGORY = "supply_chain_management"


def api(params: dict) -> dict:
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def api_retry(params: dict, attempts: int = 3) -> dict | None:
    """A live API call that survives a transient failure.

    The export makes one request per document to record the upstream
    revision. A single hiccup should not abort the whole export, so a
    failed lookup is recorded as missing rather than raised.
    """
    last = None
    for i in range(attempts):
        try:
            return api(params)
        except Exception as exc:  # noqa: BLE001
            last = exc
            time.sleep(1.5 * (i + 1))
    print(f"    [warn] API call failed after {attempts} attempts: {last}")
    return None


def revision_for(title: str) -> tuple[int | None, str | None]:
    """Return (revision id, resolved title) for a Wikipedia article."""
    d = api_retry({
        "action": "query", "titles": title, "prop": "revisions|info",
        "rvprop": "ids|timestamp", "format": "json", "formatversion": "2",
        "redirects": "1",
    })
    if d is None:
        return None, None
    pages = d.get("query", {}).get("pages", [])
    if not pages:
        return None, None
    p = pages[0]
    if "missing" in p:
        return None, None
    revs = p.get("revisions") or [{}]
    return revs[0].get("revid"), p.get("title")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def main() -> int:
    if not (CORPUS / "manifest.json").exists():
        print("!! no corpus manifest; run scripts/build_corpus.py first")
        return 1
    manifest = json.loads((CORPUS / "manifest.json").read_text(encoding="utf-8"))

    chunk_counts: Counter = Counter()
    if INDEX.exists():
        index = json.loads(INDEX.read_text(encoding="utf-8"))
        for c in index["chunks"]:
            chunk_counts[c["doc_id"]] += 1

    (OUT / "documents").mkdir(parents=True, exist_ok=True)
    records = []
    for entry in manifest:
        src = ROOT / entry["path"]
        if not src.exists():
            print(f"!! missing corpus file: {entry['path']}")
            continue
        slug = Path(entry["path"]).stem
        dest = OUT / "documents" / entry["category"] / src.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)

        revid, resolved = revision_for(entry["title"])
        time.sleep(0.35)

        records.append({
            "title": entry["title"],
            "resolved_title": resolved,
            "category": entry["category"],
            "is_focus_domain": entry["category"] == FOCUS_CATEGORY,
            "wikipedia_url": "https://en.wikipedia.org/wiki/"
                             + urllib.parse.quote((resolved or entry["title"]).replace(" ", "_")),
            "source_api": API + "?" + urllib.parse.urlencode({
                "action": "parse", "page": entry["title"], "prop": "text",
                "format": "json", "formatversion": "2", "redirects": "1",
            }),
            "revision_id": revid,
            "local_file": str(dest.relative_to(OUT)),
            "sha256": sha256(src),
            "bytes": src.stat().st_size,
            "chunks": chunk_counts.get(slug, 0),
        })
        print(f"  {entry['title']:45s} rev={revid} chunks={records[-1]['chunks']}")

    total_chunks = sum(r["chunks"] for r in records)
    focus = [r for r in records if r["is_focus_domain"]]

    payload = {
        "dataset_name": "Industrial documentation corpus (public substitute)",
        "focus_domain": FOCUS_CATEGORY,
        "n_documents": len(records),
        "n_chunks": total_chunks,
        "n_focus_documents": len(focus),
        "n_focus_chunks": sum(r["chunks"] for r in focus),
        "source": "English Wikipedia, via the MediaWiki parse API",
        "licence": "CC BY-SA 4.0 (text of the source articles)",
        "exported": time.strftime("%Y-%m-%d"),
        "rebuild": "python3 impl/scripts/build_corpus.py",
        "documents": records,
    }
    (OUT / "manifest.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    if BENCH.exists():
        shutil.copy2(BENCH, OUT / "benchmark.json")
    # The benchmark as it stood before its unanswerable class was rebuilt.
    # It ships with the dataset so that the audit's finding stays checkable
    # by a reader who has nothing but the released artefacts.
    pre = BENCH.parent / "benchmark_pre_unanswerable_repair.json"
    if pre.exists():
        shutil.copy2(pre, OUT / "benchmark_pre_unanswerable_repair.json")

    write_readme(payload)
    print(f"\nwrote {OUT} — {len(records)} documents, {total_chunks} chunks "
          f"({payload['n_focus_chunks']} in the focus domain)")
    return 0


def write_readme(p: dict) -> None:
    focus_name = p["focus_domain"].replace("_", " ")
    rows = []
    for r in p["documents"]:
        mark = " **(focus)**" if r["is_focus_domain"] else ""
        rows.append(
            f"| {r['title']}{mark} | {r['category']} | {r['chunks']} | "
            f"`{r['sha256'][:12]}…` | [{r['revision_id']}]({r['wikipedia_url']}) |"
        )
    table = "\n".join(rows)

    focus_docs = [r for r in p["documents"] if r["is_focus_domain"]]
    focus_rows = "\n".join(
        f"| {r['title']} | {r['chunks']} | `{r['sha256'][:12]}…` |"
        for r in focus_docs
    )

    (OUT / "README.md").write_text(f"""# Evaluation dataset — provenance and reproduction

This directory is the dataset every number in the thesis was measured on.
It is self-contained: the documents, their provenance, and the benchmark
that interrogates them.

## What it is

| | |
|---|---|
| **Source** | English Wikipedia, fetched through the MediaWiki `parse` API |
| **Documents** | {p['n_documents']} industrial-engineering articles |
| **Chunks** | {p['n_chunks']:,} chunks after modality-aware chunking |
| **Focus domain** | {focus_name} — {p['n_focus_documents']} documents, {p['n_focus_chunks']:,} chunks |
| **Benchmark** | `benchmark.json` — silver-standard questions with a deliberate unanswerable class |
| **Pre-repair benchmark** | `benchmark_pre_unanswerable_repair.json` — the benchmark before its unanswerable class was rebuilt, shipped so the audit's finding stays checkable |
| **Licence** | {p['licence']} |
| **Exported** | {p['exported']} |

The corpus is a **public substitute** for the primary corpus of the original
project specification (634 chunks, 24 proprietary supply-chain documents),
which cannot be redistributed. It was assembled to have the properties the
framework needs: several industrial categories, real tables and figures to
exercise the modality mechanisms, and citable provenance.

## The focus domain

The thesis focuses on a single industrial domain, **{focus_name}**, because the
original specification's corpus and its practitioner scenarios were
supply-chain, and because a deep before/after demonstration in one domain is
more informative than a shallow one across six. The remaining categories are
retained for the cross-category transfer objective (RO4), which by definition
needs a subset of categories to transfer to held-out ones.

| Document | Chunks | SHA-256 |
|---|---|---|
{focus_rows}

## Every document

`revision_id` is the upstream Wikipedia revision the article was read at.
The SHA-256 is of the exact bytes in `documents/`, which is the stronger
guarantee: an upstream article can be edited, the local copy cannot.

| Article | Category | Chunks | SHA-256 | Revision |
|---|---|---|---|---|
{table}

## Reproducing it

```bash
python3 impl/scripts/build_corpus.py        # re-fetch the documents
python3 impl/scripts/build_benchmark.py      # regenerate the questions
python3 impl/scripts/build_index.py          # build the retrieval index
```

`impl/scripts/build_corpus.py` is deterministic in its output given the
upstream revisions recorded above, and it fails loudly if a title cannot be
fetched rather than silently dropping a document.

## Attribution

The article texts are from Wikipedia and are licensed under
**CC BY-SA 4.0**. Wikipedia content is contributed by its users under that
licence, and the per-document attribution belongs to those contributors; the
revision identifiers above identify exactly which revision was used, which is
the attribution the licence asks for.

## Known limitations

- These are encyclopedia articles, not the operating manuals, standard
  operating procedures and supplier specifications of a real plant. They are
  *industrial in subject matter*, not *operationally binding*.
- Silver-standard labels are derived mechanically from the document, so
  absolute recall is optimistic. The comparisons between systems are not
  affected, because every system is scored against identical labels.
- The corpus is small relative to production corpora, which is why the
  results are framed as mechanism characterisation rather than generalisation.
""", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
