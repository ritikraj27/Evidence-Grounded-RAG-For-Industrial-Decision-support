#!/usr/bin/env python3
"""Regenerate the ablation tables in the two LaTeX papers from the measured JSON.

The tables are located by their header row rather than by line number, so the
substitution survives edits elsewhere in the file.
"""
from __future__ import annotations

import json
import sys
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from results_source import load as _src_load, load_transfer as _src_load_transfer, _comp_index

RESULTS = ROOT / "impl" / "results"

ORDER = [
    ("A. bm25_only", "A. BM25 only"),
    ("B. dense_only", "B. Dense only"),
    ("C. hybrid_rrf", "C. Hybrid (RRF)"),
    ("D. hybrid_rrf_rerank", "D. \\quad$+$ rerank"),
    ("E. +category_filter", "E. \\quad$+$ category filter"),
    ("F. +quota_pre_rerank", "F. \\quad$+$ quota (pre-rerank)"),
    ("G. +quota_post_rerank", "G. \\quad$+$ quota (post-rerank)"),
]

SHORT = {
    "A. bm25_only": "A. BM25 only",
    "B. dense_only": "B. Dense only",
    "C. hybrid_rrf": "C. Hybrid (RRF)",
    "D. hybrid_rrf_rerank": "D. + cross-encoder rerank",
    "E. +category_filter": "E. + category filter",
    "F. +quota_pre_rerank": "F. + quota (pre-rerank)",
    "G. +quota_post_rerank": "G. + quota (post-rerank)",
}

ARROWS = ["A", "B", "C", "D", "E", "F"]








def fmt(x, nd=3):
    """Format a number the way the tables do: 0.555 -> .555, leading zero dropped."""
    s = f"{x:.{nd}f}"
    return s[1:] if s.startswith("0.") else s


def _sci(p: float) -> str:
    """Render a p-value as LaTeX scientific notation: 2.5e-08 -> 2.5\\!\\times\\!10^{-8}."""
    mant, exp = f"{p:.1e}".split("e")
    sign = "-" if exp.startswith("-") else ""
    digits = exp.lstrip("+-").lstrip("0") or "0"
    return rf"{mant}\!\times\!10^{{{sign}{digits}}}"


def build_rows(exp1) -> tuple[list[str], list[str]]:
    systems = exp1["systems"]
    comp = _comp_index(exp1["comparisons"])
    main_rows = []
    for key, label in ORDER:
        v = systems[key]
        main_rows.append(
            f"{label} & {fmt(v['recall@5'])} & {fmt(v['recall@10'])} & "
            f"{fmt(v['recall@20'])} & {fmt(v['mrr'])} & {fmt(v['nDCG@10'])} & "
            f"{fmt(v['modality_recall'].get('table', float('nan')))} \\\\"
        )
    delta_rows = []
    for a, b in zip(ORDER[:-1], ORDER[1:]):
        c = comp.get(a[0])
        if not c:
            delta_rows.append(f"{a[0][0]}$\\to${b[0][0]} & --- & --- \\\\")
            continue
        d = c["delta"]
        p = c["wilcoxon"]["p_value"]
        ptex = _sci(p)
        delta_rows.append(
            f"{a[0][0]}$\\to${b[0][0]} & ${d:+.3f}$ & ${ptex}$ \\\\"
        )
    return main_rows, delta_rows


def substitute(path: Path, main_rows: list[str], delta_rows: list[str]) -> bool:
    s = path.read_text(encoding="utf-8")
    changed = False

    # The main results table: the tabular whose header contains "Tbl R@10".
    for m in list(re.finditer(r"\\begin\{tabular\}\{[^}]*\}(.*?)\\end\{tabular\}",
                              s, re.S)):
        body = m.group(1)
        if "Tbl R@10" not in body:
            continue
        new_body = re.sub(
            r"(\\midrule\s*\n)(.*?)(\\bottomrule)",
            lambda mm: mm.group(1) + "\n".join(main_rows) + "\n" + mm.group(3),
            body,
            count=1,
            flags=re.S,
        )
        s = s[: m.start(1)] + new_body + s[m.end(1):]
        changed = True
        break

    # The paired-test table: the tabular whose header mentions the p-value.
    for m in list(re.finditer(r"\\begin\{tabular\}\{[^}]*\}(.*?)\\end\{tabular\}",
                              s, re.S)):
        body = m.group(1)
        if "Rung" not in body:
            continue
        new_body = re.sub(
            r"(\\midrule\s*\n)(.*?)(\\bottomrule)",
            lambda mm: mm.group(1) + "\n".join(delta_rows) + "\n" + mm.group(3),
            body,
            count=1,
            flags=re.S,
        )
        s = s[: m.start(1)] + new_body + s[m.end(1):]
        changed = True
        break

    if changed:
        path.write_text(s, encoding="utf-8")
    return changed


def main() -> int:
    exp1 = _src_load("exp1_ablation", ("systems", "comparisons", "corpus_stats"))
    if exp1 is None:
        print("[tex] exp1 not available; leaving the LaTeX tables as they are")
        return 1
    p = RESULTS / "exp1_ablation.json"
    if not p.exists():
        print("[tex] exp1 not available; leaving the LaTeX tables as they are")
        return 0
    main_rows, delta_rows = build_rows(exp1)
    for name in ["Deliverable_2b_IEEE_Conference_Paper.tex",
                 "Deliverable_2c_Journal_Style_Paper.tex"]:
        path = ROOT / "deliverables" / name
        ok = substitute(path, main_rows, delta_rows)
        print(f"[tex] {name}: {'tables updated' if ok else 'NO TABLE FOUND'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
