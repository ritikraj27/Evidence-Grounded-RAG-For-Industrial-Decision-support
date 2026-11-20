#!/usr/bin/env python3
"""Finish wiring the generators to the shared results source.

Three things the first patch did not cover:

* `make_tex_results.py` reads the ablation JSON directly instead of through
  a loader function;
* `make_docx.py` assigns exp4 inside `main()`, so the assignment is indented;
* the deck and report builders exist in two places -- the working copy and
  the pristine template that `build_all.py` restores from -- and both need
  the change, or the build silently reverts it.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "deliverables" / "scripts"
TEMPLATES = ROOT / "deliverables" / "templates" / "scripts"

IMPORT = (
    "sys.path.insert(0, str(Path(__file__).resolve().parent))\n"
    "from results_source import load as _src_load, load_transfer as _src_load_transfer\n"
)

TRANSFER_LOADER = '''def load_transfer(name, required=()):
    """Load a result from the multi-category run only.

    The cross-category transfer experiment is defined on a multi-category
    corpus, so it is never taken from the focus-domain run.
    """
    return _src_load_transfer(name, required)
'''


def add_import(s: str) -> str:
    if "from results_source import" in s:
        return s
    m = re.search(r"^ROOT = .*$", s, re.M)
    if not m:
        return s
    return s[:m.end()] + "\n" + IMPORT + s[m.end():]


def patch_tex_results(s: str) -> str:
    if "from results_source import" not in s:
        s = add_import(s)
    s = s.replace(
        '    p = RESULTS / "exp1_ablation.json"',
        '    exp1 = _src_load("exp1_ablation", ("systems", "comparisons", "corpus_stats"))\n'
        '    if exp1 is None:\n'
        '        print("[tex] exp1 not available; leaving the LaTeX tables as they are")\n'
        '        return 1\n'
        '    p = RESULTS / "exp1_ablation.json"', 1)
    # The direct json.loads becomes redundant.
    s = re.sub(r"\n *exp1 = json\.loads\(p\.read_text\(encoding=\"utf-8\"\)\)", "", s, count=1)
    return s


def patch_docx(s: str) -> str:
    if "from results_source import" not in s:
        s = add_import(s)
    if "def load_transfer(" not in s:
        m = re.search(r"^def _load\(.*?(?=\n(?:def |exp\d|# ---))", s, re.S | re.M)
        if m:
            s = s[:m.end()] + "\n\n" + TRANSFER_LOADER + s[m.end():]
    s = re.sub(r"exp4 = _load\(", "exp4 = load_transfer(", s, count=1)
    return s


def patch_pptx(s: str) -> str:
    if "from results_source import" not in s:
        s = add_import(s)
    s = re.sub(r"exp4 = _load\(", "exp4 = load_transfer(", s, count=1)
    return s


def main() -> int:
    jobs = [
        (SCRIPTS / "make_tex_results.py", patch_tex_results),
        (SCRIPTS / "make_docx.py", patch_docx),
        (TEMPLATES / "make_docx.py", patch_docx),
        (TEMPLATES / "make_pptx.py", patch_pptx),
    ]
    failures = []
    for path, fn in jobs:
        if not path.exists():
            failures.append(f"{path}: not found")
            continue
        s = path.read_text(encoding="utf-8")
        new = fn(s)
        if new != s:
            path.write_text(new, encoding="utf-8")
            print(f"  patched {path.relative_to(ROOT)}")
    if failures:
        for f in failures:
            print(f"!! {f}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
