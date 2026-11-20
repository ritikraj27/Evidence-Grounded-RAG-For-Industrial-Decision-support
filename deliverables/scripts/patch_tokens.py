#!/usr/bin/env python3
"""Replace every hard-coded corpus/benchmark number in the templates with a token.

The token machinery (`substitute_tokens.py`) already existed but nothing used
it: the numbers were written out by hand in the prose. That is how the guide
came to claim "41 documents" while the report claimed "39", and how a stale
"371 silver queries" survived in the code guide after the benchmark changed
twice.

This patch replaces those literals with `{{TOKEN}}` placeholders, so the
prose is regenerated from the measured artefacts on every build and cannot
drift again. Every replacement is asserted, so a silently-missed literal
fails the patch rather than surviving unnoticed.

Run from the repository root.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = ROOT / "deliverables" / "templates"

#: (relative path, [(old, new), ...])
PATCHES: list[tuple[str, list[tuple[str, str]]]] = [
    ("Deliverable_1_Part1_Content.md", [
        ("(41 documents, 2,570 chunks,\nsix industrial categories) and a "
         "366-query silver-standard benchmark",
         "({{N_DOCUMENTS}} documents, {{N_CHUNKS}} chunks,\n"
         "{{N_CATEGORIES_WORD}} industrial categories) and a "
         "{{N_QUERIES}}-query silver-standard benchmark"),
        ("Here: 2,570 chunks\nfrom 39 documents.",
         "Here: {{N_CHUNKS}} chunks\nfrom {{N_DOCUMENTS}} documents."),
        ("Ours are ~115 words, tagged with",
         "Ours are ~{{MEAN_WORDS}} words, tagged with"),
        ("system A better than system B on the same 366 queries",
         "system A better than system B on the same {{N_QUERIES}} queries"),
        ("Our 366-query benchmark is silver",
         "Our {{N_QUERIES}}-query benchmark is silver"),
        ("With N = 366 queries, a paired test",
         "With N = {{N_QUERIES}} queries, a paired test"),
        ("With a corpus that is 90.7% prose, a null is the **expected** outcome,",
         "With a corpus that is {{SHARE_TEXT}} prose, a null is the **expected** "
         "outcome,"),
        ("corpus was 2.3% chart and 7.1% table; our corpus is 3.9% chart and 5.4% table.",
         "corpus was 2.3% chart and 7.1% table; our corpus is {{SHARE_CHART}} chart "
         "and {{SHARE_TABLE}} table."),
    ]),
    ("Deliverable_1_PartD_Code.md", [
        ("hash so a re-run does not re-encode 2,570 chunks.",
         "hash so a re-run does not re-encode {{N_CHUNKS}} chunks."),
        ("│   └── benchmark/        371 silver queries (227 answerable, 144 unanswerable)",
         "│   └── benchmark/        {{N_QUERIES}} silver queries "
         "({{N_ANSWERABLE}} answerable, {{N_UNANSWERABLE}} unanswerable)"),
        ("cost is cross-encoder reranking: 366 queries × 50 candidate pairs × 4 systems.",
         "cost is cross-encoder reranking: {{N_QUERIES}} queries × 50 candidate "
         "pairs × 4 systems."),
    ]),
    ("Deliverable_1_PartF_toJ.md", [
        ("On a corpus that is 90.7% prose, a two-table quota can only pull tables from deep",
         "On a corpus that is {{SHARE_TEXT}} prose, a two-table quota can only pull "
         "tables from deep"),
        ("(2.3% chart, 7.1% table in the primary corpus; 3.9%/5.4% in ours)",
         "(2.3% chart, 7.1% table in the primary corpus; "
         "{{SHARE_CHART}}/{{SHARE_TABLE}} in ours)"),
    ]),
    ("Deliverable_2a_Technical_Report.md", [
        ("public industrial corpus of 2,570 chunks across six categories and a "
         "366-query silver-standard benchmark",
         "public industrial corpus of {{N_CHUNKS}} chunks across "
         "{{N_CATEGORIES_WORD}} categories and a {{N_QUERIES}}-query "
         "silver-standard benchmark"),
        ("39 documents and 2,570 chunks across six industrial",
         "{{N_DOCUMENTS}} documents and {{N_CHUNKS}} chunks across "
         "{{N_CATEGORIES_WORD}} industrial"),
        ("categories, with a modality composition of 90.7% text,",
         "categories, with a modality composition of {{SHARE_TEXT}} text,"),
        ("5.4% table and 3.9% chart — closely matching",
         "{{SHARE_TABLE}} table and {{SHARE_CHART}} chart — closely matching"),
        ("366 silver-standard queries, of which 144 are",
         "{{N_QUERIES}} silver-standard queries, of which {{N_UNANSWERABLE}} are"),
        ("Seven systems were compared on the same 366 queries.",
         "Seven systems were compared on the same {{N_QUERIES}} queries."),
        ("90.7% text, a two-table quota can only draw on tables deep in",
         "{{SHARE_TEXT}} text, a two-table quota can only draw on tables deep in"),
    ]),
    ("Deliverable_2b_IEEE_Conference_Paper.tex", [
        ("public industrial corpus of 2,570 chunks across six\ncategories and a "
         "366-query silver-standard benchmark",
         "public industrial corpus of {{N_CHUNKS_TEX}} chunks across "
         "{{N_CATEGORIES_WORD}}\ncategories and a {{N_QUERIES}}-query "
         "silver-standard benchmark"),
        ("Seven systems were compared on the same 366 queries over a 2{,}570-chunk,\n"
         "39-document, six-category corpus.",
         "Seven systems were compared on the same {{N_QUERIES}} queries over a "
         "{{N_CHUNKS_TEX}}-chunk,\n{{N_DOCUMENTS}}-document, "
         "{{N_CATEGORIES_WORD}}-category corpus."),
        ("\\caption{Retrieval ablation on 366 silver-standard queries over a "
         "2{,}570-chunk\npublic industrial corpus.",
         "\\caption{Retrieval ablation on {{N_QUERIES}} silver-standard queries "
         "over a {{N_CHUNKS_TEX}}-chunk\npublic industrial corpus."),
        ("\\paragraph{The corpus composition predicts the outcome.} The corpus is 90.7\\%",
         "\\paragraph{The corpus composition predicts the outcome.} The corpus is "
         "{{SHARE_TEXT_TEX}}"),
    ]),
    ("Deliverable_2c_Journal_Style_Paper.tex", [
        ("public industrial corpus of 2{,}570\nchunks spanning six categories, with a "
         "366-query silver-standard benchmark",
         "public industrial corpus of {{N_CHUNKS_TEX}}\nchunks spanning "
         "{{N_CATEGORIES_WORD}} categories, with a {{N_QUERIES}}-query "
         "silver-standard benchmark"),
        ("Seven systems were compared on the same 366 queries over a 2{,}570-chunk,\n"
         "39-document, six-category corpus (90.7\\% text, 5.4\\% table, 3.9\\% chart).",
         "Seven systems were compared on the same {{N_QUERIES}} queries over a "
         "{{N_CHUNKS_TEX}}-chunk,\n{{N_DOCUMENTS}}-document, "
         "{{N_CATEGORIES_WORD}}-category corpus ({{SHARE_TEXT_TEX}} text, "
         "{{SHARE_TABLE_TEX}} table, {{SHARE_CHART_TEX}} chart)."),
        ("\\caption{Retrieval ablation on 366 silver-standard queries.",
         "\\caption{Retrieval ablation on {{N_QUERIES}} silver-standard queries."),
        ("modality composition of the corpus --- 90.7\\% text in the evaluation corpus ---",
         "modality composition of the corpus --- {{SHARE_TEXT_TEX}} text in the "
         "evaluation corpus ---"),
        ("\\paragraph{The corpus composition predicts the outcome.} With 90.7\\% text, a",
         "\\paragraph{The corpus composition predicts the outcome.} With "
         "{{SHARE_TEXT_TEX}} text, a"),
    ]),
    ("scripts/make_pptx.py", [
        ('"366 silver-standard queries over a 2,570-chunk, 39-document public industrial "',
         '"{{N_QUERIES}} silver-standard queries over a {{N_CHUNKS}}-chunk, '
         '{{N_DOCUMENTS}}-document public industrial "'),
        ('"corpus spanning six categories (supply chain, predictive maintenance, "',
         '"corpus spanning {{N_CATEGORIES_WORD}} categories (supply chain, '
         'predictive maintenance, "'),
        ('notes(s, "This is the core experimental table. Seven systems, the same 366 queries, "',
         'notes(s, "This is the core experimental table. Seven systems, the same '
         '{{N_QUERIES}} queries, "'),
    ]),
]


def main() -> int:
    failures: list[str] = []
    total = 0
    for rel, edits in PATCHES:
        path = TEMPLATES / rel
        if not path.exists():
            failures.append(f"{rel}: file not found")
            continue
        text = original = path.read_text(encoding="utf-8")
        for old, new in edits:
            n = text.count(old)
            if n == 0:
                failures.append(f"{rel}: NOT FOUND -> {old[:70]!r}")
                continue
            if n > 1:
                failures.append(f"{rel}: AMBIGUOUS ({n}x) -> {old[:70]!r}")
                continue
            text = text.replace(old, new)
            total += 1
        if text != original:
            path.write_text(text, encoding="utf-8")
            print(f"  patched {rel}")
    print(f"\n{total} replacements applied")
    if failures:
        print("\n!! FAILURES:")
        for f in failures:
            print(f"   {f}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
