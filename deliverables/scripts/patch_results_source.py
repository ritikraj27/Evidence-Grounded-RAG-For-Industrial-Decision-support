#!/usr/bin/env python3
"""Point every generator at the shared results-source module.

The generators each had their own loader that read `impl/results/`. The
headline numbers now come from the focus-domain run, with the multi-category
run as a fallback, and the transfer experiment comes only from the
multi-category run. Rather than change six copies of the same loader, they
all delegate to one module that says which directory each result comes from.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "deliverables" / "scripts"

IMPORT = (
    "sys.path.insert(0, str(Path(__file__).resolve().parent))\n"
    "from results_source import load as _src_load, load_transfer as _src_load_transfer\n"
)

LOADER = '''def {name}({sig}):
    """Load a result file, preferring the focus-domain run.

    The headline numbers come from the focus domain; the multi-category run
    is the fallback and the source of the transfer study. See
    `results_source.py` for why.
    """
    return _src_load({arg}, required)
'''

TRANSFER_LOADER = '''def load_transfer(name, required=()):
    """Load a result from the multi-category run only.

    The cross-category transfer experiment is defined on a multi-category
    corpus, so it is never taken from the focus-domain run.
    """
    return _src_load_transfer(name, required)
'''

#: file -> (loader function name, signature, first argument name)
LOADERS = {
    "make_results_md.py": ("load", "name, required=()", "name"),
    "make_paper_results.py": ("load", "name, required=()", "name"),
    "make_tex_results.py": ("load", "name, required=()", "name"),
    "make_tex_prose.py": ("load", "name, required=()", "name"),
    "make_pptx.py": ("_load", "name: str, required: tuple = ()", "name"),
    "make_docx.py": ("_load", "name, required=()", "name"),
}

#: files whose exp4 result must come from the multi-category run
TRANSFER_USERS = ["make_results_md.py", "make_paper_results.py", "make_pptx.py",
                  "make_docx.py"]


def main() -> int:
    failures = []
    for fname, (lname, sig, arg) in LOADERS.items():
        p = SCRIPTS / fname
        if not p.exists():
            failures.append(f"{fname}: not found")
            continue
        s = p.read_text(encoding="utf-8")

        if "from results_source import" not in s:
            # Insert the import right after the ROOT definition.
            m = re.search(r"^ROOT = .*$", s, re.M)
            if not m:
                failures.append(f"{fname}: no ROOT definition")
                continue
            s = s[:m.end()] + "\n" + IMPORT + s[m.end():]

        # Replace the loader body.
        pattern = re.compile(
            r"^def " + re.escape(lname) + r"\(.*?(?=\n(?:def |exp\d|OUT\b|# ---|\w+ = _load))",
            re.S | re.M)
        new_loader = LOADER.format(name=lname, sig=sig, arg=arg)
        s2, n = pattern.subn(new_loader, s, count=1)
        if n != 1:
            failures.append(f"{fname}: loader {lname} not matched")
            continue
        s = s2

        if fname in TRANSFER_USERS and "load_transfer(" not in s:
            m = re.search(r"^exp4 = _?load\(", s, re.M)
            if not m:
                failures.append(f"{fname}: exp4 assignment not found")
            else:
                s = s[:m.start()] + s[m.start():].replace(
                    "exp4 = load(", "exp4 = load_transfer(", 1).replace(
                    "exp4 = _load(", "exp4 = load_transfer(", 1)

        p.write_text(s, encoding="utf-8")
        print(f"  {fname}: loader now delegates to results_source")

    if failures:
        print("!! FAILURES:")
        for f in failures:
            print(f"   {f}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
