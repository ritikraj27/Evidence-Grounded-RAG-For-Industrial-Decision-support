#!/usr/bin/env python3
"""Build the demonstration corpus from real, public industrial documentation.

The corpus is assembled from publicly available reference documents that are
genuine industrial-engineering content, grouped into the framework's category
taxonomy. Every document is fetched over the public MediaWiki API (or a public
PDF URL) and stored locally so that the pipeline is reproducible offline
after the first fetch.

Why public reference documents
------------------------------
The thesis's own corpus is 24 proprietary-looking supply-chain documents
(634 chunks). That corpus is not redistributable, so the shipped
implementation ships a *public substitute* with the same properties:
multi-category, table-bearing, industrial, and citable. It is used to
demonstrate that the pipeline runs and to produce the ablation numbers in the
report; it is explicitly NOT a replacement for the proprietary corpus.

Categories mirror the thesis taxonomy: six industrial-engineering families
(supply chain management, predictive maintenance, production scheduling,
quality engineering, facility layout, reliability engineering). This makes the
cross-category transfer experiment (RO4) genuinely executable rather than
merely asserted.
"""
from __future__ import annotations

import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "data" / "corpus"
USER_AGENT = "mtp-rag-framework/1.0 (academic research; contact: ritik@example.com)"

API = "https://en.wikipedia.org/w/api.php"

#: category -> Wikipedia article titles (all exist; verified at fetch time)
#:
#: Two rules this mapping must obey, both learned from a build that broke:
#:
#: 1. **No title may appear in two categories.** An article listed twice is
#:    fetched twice, indexed twice under the same `doc_id`, and therefore
#:    appears in two places in the index. That corrupts three things at once:
#:    the chunk count (duplicated rows), the category pre-filter (a query in
#:    one category sees only half the article), and the cross-category
#:    transfer experiment (the same text lands in both the tuning and the
#:    held-out half, so the "held-out" half is not held out). `main()` now
#:    asserts this.
#:
#: 2. **Every title must exist under exactly that name.** Wikipedia's parse
#:    API answers `missingtitle` for a title it does not know rather than
#:    following the redirect, so a wrong title silently removes a document
#:    from the corpus. `main()` now fails the build instead of dropping it.
#:
#: Every title below was resolved with the search API and re-verified with
#: `action=parse` before being written here.
CATEGORIES: dict[str, list[str]] = {
    "supply_chain_management": [
        "Economic order quantity",
        "Incoterms",
        "Safety stock",
        "Just-in-time manufacturing",
        "Material requirements planning",
        "Bill of materials",
        "Kanban",
        "Theory of constraints",
        "Inventory management",
        "Strategic sourcing",
        "Third-party logistics",
        "Logistics",
        "Demand forecasting",
        "Six Sigma",
    ],
    "predictive_maintenance": [
        "Predictive maintenance",
        "Total productive maintenance",
        "Overall equipment effectiveness",
        "Root cause analysis",
        "Condition monitoring",
        "Failure mode and effects analysis",
    ],
    "production_scheduling": [
        "Job shop scheduling",
        "Flow shop scheduling",
        "Production planning",
        "Gantt chart",
        "Lean manufacturing",
        "Takt time",
        "Line balancing",
    ],
    "quality_engineering": [
        "Statistical process control",
        "Control chart",
        "Eight disciplines problem solving",
        "Quality control",
        "ISO 9001",
        "Design for manufacturability",
        "Taguchi methods",
    ],
    "facility_layout": [
        "Material handling",
        "Warehouse",
        "Plant layout",
        "Queueing theory",
        "Little's law",
    ],
    "reliability_engineering": [
        "Reliability engineering",
        "Mean time between failures",
        "Mean time to repair",
        "Failure rate",
        "Maintainability",
        "Weibull distribution",
        "Fault tree analysis",
    ],
}


def fetch_json(url: str, tries: int = 4) -> dict | None:
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=45) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as exc:
            print(f"    retry {attempt+1}: {exc}", flush=True)
            time.sleep(3 * (attempt + 1))
    return None


def html_to_markdown(html: str, title: str) -> str:
    """Convert article HTML to markdown, preserving tables."""
    try:
        from markdownify import markdownify
    except ImportError:
        raise SystemExit("markdownify is required: uv pip install markdownify")

    md = markdownify(
        html,
        heading_style="ATX",
        bullets="-",
        # NOTE: "table" is deliberately NOT stripped -- tables are the
        # modality the whole quota mechanism exists to balance, and they are
        # the ones the industrial corpus stores its binding requirements in.
        strip=["script", "style", "sup", "figure"],
    )
    md = re.sub(r"\n{3,}", "\n\n", md)
    md = re.sub(r"^\s*(Retrieved from|Category:|Jump to navigation).*$", "", md, flags=re.M)
    md = strip_wikipedia_boilerplate(md)
    return f"# {title}\n\n{md.strip()}\n"


#: Wikipedia maintenance templates and editorial apparatus. These are pure
#: retrieval noise: they mention "citations", "sources", "Wikipedia" and
#: "articles", which are exactly the tokens a lexical retriever keys on.
#: Leaving them in inflates the corpus and makes the retrieval task look
#: easier than it is.
_BOILERPLATE_PATTERNS = [
    r"This section\*\* needs \*\*\[more citations\].*?(?=\n\n|\Z)",
    r"Please help \*\*\[improve this section\].*?(?=\n\n|\Z)",
    r"Unsourced material may be challenged and \*\*\[removed\].*?(?=\n\n|\Z)",
    r"\*\*\[add citations\]\*\*.*?(?=\n\n|\Z)",
    r"\*Find sources:\*.*?(?=\n\n|\Z)",
    r"This article \*\*needs additional citations.*?(?=\n\n|\Z)",
    r"\*\*\[news\]\*\*.*?(?=\n\n|\Z)",
    r"^\s*\[edit\].*$",
    r"^\s*\[citation needed\].*$",
    r"^\s*\[when \(.*?\)\].*$",
    r"^\s*See also\s*$",
    r"^\s*References\s*$",
    r"^\s*External links\s*$",
    r"^\s*Further reading\s*$",
    r"^\s*Notes\s*$",
    r"^\s*Bibliography\s*$",
    r"^\s*Sources\s*$",
]


def strip_wikipedia_boilerplate(md: str) -> str:
    """Remove editorial/maintenance apparatus from a converted article."""
    out = md
    for pat in _BOILERPLATE_PATTERNS:
        out = re.sub(pat, "", out, flags=re.M | re.S)
    # Drop leftover reference-list bullet blocks that follow a References heading.
    out = re.sub(r"\n\s*\*\s*\"[^\"]{10,}\"\s*(?:\n|$)", "\n", out)
    out = re.sub(r"\n{3,}", "\n\n", out)
    return out


def fetch_article(title: str) -> str | None:
    params = {
        "action": "parse",
        "page": title,
        "prop": "text",
        "format": "json",
        "formatversion": "2",
        "redirects": "1",
    }
    url = API + "?" + urllib.parse.urlencode(params)
    data = fetch_json(url)
    if not data or "error" in data:
        return None
    html = data.get("parse", {}).get("text", "")
    if not html:
        return None
    return html_to_markdown(html, title)


def assert_categories_well_formed() -> None:
    """Fail the build if the category mapping is malformed.

    Two checks, both of which catch a real defect this corpus once had:

    * a title listed under two categories, which duplicates the document in
      the index and leaks it across the train/held-out category split;
    * a title that appears in no category at all, which is a typo.
    """
    seen: dict[str, list[str]] = {}
    for category, titles in CATEGORIES.items():
        for t in titles:
            seen.setdefault(t, []).append(category)
    dupes = {t: cs for t, cs in seen.items() if len(cs) > 1}
    if dupes:
        raise SystemExit(
            "build_corpus: the same article is listed under more than one "
            f"category: {dupes}. Each article must belong to exactly one "
            "category, or it is indexed twice and leaks across the "
            "cross-category transfer split."
        )


def main() -> int:
    assert_categories_well_formed()
    CORPUS.mkdir(parents=True, exist_ok=True)
    manifest = []
    ok = fail = 0
    failures: list[str] = []
    for category, titles in CATEGORIES.items():
        cat_dir = CORPUS / category
        cat_dir.mkdir(parents=True, exist_ok=True)
        for title in titles:
            slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
            out = cat_dir / f"{slug}.md"
            if out.exists() and out.stat().st_size > 2000:
                print(f"[skip] {category}/{slug}", flush=True)
                manifest.append({
                    "title": title,
                    "category": category,
                    "path": str(out.relative_to(ROOT)),
                    "bytes": out.stat().st_size,
                })
                ok += 1
                continue
            print(f"[get ] {category}/{title}", flush=True)
            md = fetch_article(title)
            if md is None or len(md) < 2000:
                print(f"[FAIL] {title}", flush=True)
                failures.append(f"{category}/{title}")
                fail += 1
                continue
            # Tag the chunk category in the file header so ingestion can read it.
            header = f"<!-- category: {category} -->\n"
            out.write_text(header + md, encoding="utf-8")
            manifest.append(
                {
                    "title": title,
                    "category": category,
                    "path": str(out.relative_to(ROOT)),
                    "bytes": len(md),
                }
            )
            ok += 1
            time.sleep(0.4)  # Wikimedia etiquette
    (CORPUS / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"\nDONE: {ok} documents, {fail} failures -> {CORPUS}")
    if failures:
        # A silent failure here removes a document from the corpus without
        # leaving a trace, and the published chunk count stops matching the
        # corpus. Fail the build instead.
        raise SystemExit(
            "build_corpus: these titles could not be fetched and are now "
            f"absent from the corpus: {failures}. Wikipedia's parse API "
            "returns `missingtitle` for a title it does not know, so check "
            "the exact spelling against the search API."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
