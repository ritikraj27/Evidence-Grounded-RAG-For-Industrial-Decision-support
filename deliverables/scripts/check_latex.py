#!/usr/bin/env python3
"""Compile the two LaTeX papers and fail the build if they do not build.

The papers are the only deliverables that are *not* written in a language the
build can check. A brace-balance check proves the file is well-formed LaTeX;
it does not prove the file compiles, and it cannot see a package that was
never loaded, an environment a class does not define, or a token value that
carries a character the document cannot hold.

That gap was real. Three defects sat in the papers undetected, because no
LaTeX engine had ever run on them:

  * `\\texttt{{EMBED_MODEL}}` -- the token's braces and the command's braces
    are the same character, so the substitution left `\\texttt` without its
    opening brace and the compile died with "Undefined control sequence".
  * `\\url` used in the bibliography of the IEEE paper, which never loaded the
    `url` package.
  * `\\begin{keywords}` in the journal paper, which `elsarticle` calls
    `keyword`, and a `highlights` environment it already defines.

A fourth was not a LaTeX error but a layout one: the gate equation and the
seven-column ablation table each overran a single IEEE column by more than a
centimetre.

The engine is `tectonic`, which fetches its packages on demand and needs no
TeX Live installation. If it is not present the check is skipped with a note
rather than failing: a machine without LaTeX should still be able to build the
other three deliverables.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DELIV = ROOT / "deliverables"

#: The papers, and the engine each prefers. The first engine found is used
#: for both, so a machine with only one of them still checks both papers.
PAPERS = (
    "Deliverable_2b_IEEE_Conference_Paper.tex",
    "Deliverable_2c_Journal_Style_Paper.tex",
)

#: An overfull box wider than this is a layout defect a camera-ready check
#: would flag. Below it, LaTeX's own line-breaking has simply found a
#: slightly tight spot, which is normal.
OVERFULL_LIMIT_PT = 30.0

#: The page budget for the conference paper, references included: for IEEE
#: venues the references count toward it. The paper was 12 pages for
#: most of this project's life, was cut to 9, then to 10, and is now 13. The
#: first raise added the nineteen papers of the 2026 literature that bear
#: directly on the claims -- including the four that change what the paper may
#: say -- and grew the reference list by 29 entries. The second raise added a
#: second corpus: 110 United States federal regulatory documents read at two
#: past dates, with the ablation replicated on them, the conflict detector's
#: precision measured as two numbers rather than one, a 2x2 factorial over the
#: annotation rubric, two figures, three tables and fifteen more references.
#: The alternative was to cut the paper's clearest new result, or the
#: positioning paragraphs that say which of its findings are already
#: published, both of which a quality audit had already said to protect. The
#: budget is recorded here so the change is visible rather than silent, and
#: it is a decision the supervisor can reverse.
#: The journal version has no limit and is not checked.
PAGE_LIMIT = {
    "Deliverable_2b_IEEE_Conference_Paper.tex": 13,
}


def _find_engine() -> str | None:
    for name in ("tectonic", "pdflatex", "lualatex", "xelatex"):
        path = shutil.which(name)
        if path:
            return path
    return None


def _compile(engine: str, source: Path, workdir: Path) -> tuple[bool, str, str]:
    """Compile one paper. Returns (ok, log, engine output)."""
    target = workdir / source.name
    target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    if engine.endswith("tectonic"):
        cmd = [engine, "-X", "compile", target.name, "--outfmt", "pdf",
               "--keep-logs", "--synctex"]
    else:
        cmd = [engine, "-interaction=nonstopmode", "-halt-on-error",
               target.name]
    try:
        proc = subprocess.run(cmd, cwd=workdir, capture_output=True,
                              text=True, timeout=900)
    except subprocess.TimeoutExpired:
        return False, "", "the compile timed out"
    log_path = workdir / (target.stem + ".log")
    log = log_path.read_text(encoding="utf-8", errors="replace") \
        if log_path.exists() else ""
    return proc.returncode == 0, log, (proc.stdout or "") + (proc.stderr or "")


#: The page counts the pre-submission guide quotes, and the pattern each is
#: written in. The numbers drift: the guide said nine and eighteen pages for
#: a long time after the papers had grown, and nobody noticed because the
#: guide is read by hand rather than compiled.
_STATED_PAGES = [
    ("Deliverable_2b_IEEE_Conference_Paper.tex",
     r"the IEEE conference paper is \*\*(\d+)\s+pages?\*\*"),
    ("Deliverable_2c_Journal_Style_Paper.tex",
     r"the journal paper is \*\*(\d+)\s+pages?\*\*"),
]


def _check_stated_page_counts(measured: dict[str, int]) -> list[str]:
    """The page counts the guide states must be the ones that compile."""
    found: list[str] = []
    guide = DELIV / "READ_ME_FIRST.md"
    if not guide.exists():
        return found
    text = guide.read_text(encoding="utf-8")
    for name, pattern in _STATED_PAGES:
        m = re.search(pattern, text)
        if not m:
            continue
        stated = int(m.group(1))
        actual = measured.get(name)
        if actual is None:
            continue
        if stated != actual:
            found.append(
                f"READ_ME_FIRST.md states that "
                f"{name.split('_', 2)[-1].split('.')[0]} is {stated} pages, "
                f"but it compiles to {actual}")
    return found


def main() -> int:
    engine = _find_engine()
    if not engine:
        print("  · LaTeX check: skipped (no tectonic, pdflatex, lualatex or "
              "xelatex on this machine)")
        return 0

    problems: list[str] = []
    notes: list[str] = []
    _measured: dict[str, int] = {}
    with tempfile.TemporaryDirectory(prefix="mtp-latex-") as tmp:
        workdir = Path(tmp)
        # The papers include figures by relative path, and the compile runs
        # in a temporary directory, so the figure directory has to travel
        # with the source. A missing figure is a compile error, not a
        # warning, and this is where it is caught.
        figdir = DELIV / "figures"
        if figdir.exists():
            shutil.copytree(figdir, workdir / "figures")
        for name in PAPERS:
            src = DELIV / name
            if not src.exists():
                problems.append(f"{name}: the file does not exist")
                continue
            text = src.read_text(encoding="utf-8")
            left = re.findall(r"\{\{[A-Z0-9_]+\}\}", text)
            if left:
                problems.append(
                    f"{name}: unsubstituted tokens {sorted(set(left))} -- the "
                    "paper would ship them literally")
                continue
            ok, log, out = _compile(engine, src, workdir)
            if not ok:
                err = re.findall(r"^error:.*$|^! .*$", out, re.M)
                problems.append(f"{name}: the paper does not compile -- "
                                + ("; ".join(err[:3]) or "see the log"))
                continue
            pages = re.findall(r"Output written on .*?\((\d+) pages", log)
            overfull = [float(x) for x in
                        re.findall(r"Overfull \\hbox \((\d+\.\d+)pt too wide", log)]
            undef_cite = re.findall(r"Citation `([^']+)' .*undefined", log)
            undef_ref = re.findall(r"Reference `([^']+)' .*undefined", log)
            if undef_cite:
                problems.append(f"{name}: undefined citations {sorted(set(undef_cite))}")
            if undef_ref:
                problems.append(f"{name}: undefined references {sorted(set(undef_ref))}")
            bad = [o for o in overfull if o > OVERFULL_LIMIT_PT]
            if bad:
                problems.append(
                    f"{name}: {len(bad)} overfull line(s) wider than "
                    f"{OVERFULL_LIMIT_PT:.0f}pt -- the largest is "
                    f"{max(bad):.1f}pt over the margin")
            limit = PAGE_LIMIT.get(name)
            n_pages = int(pages[0]) if pages else None
            if limit and n_pages and n_pages > limit:
                problems.append(
                    f"{name}: compiles to {n_pages} pages, over the "
                    f"{limit}-page budget (references count toward it for "
                    f"IEEE)")
            notes.append(
                f"{name}: compiles, {pages[0] if pages else '?'} pages"
                + (f" (budget {limit})" if limit else "")
                + f", {len(overfull)} overfull line(s)"
                + (f" (largest {max(overfull):.1f}pt)" if overfull else ""))
            if pages:
                _measured[name] = int(pages[0])

        problems.extend(_check_stated_page_counts(_measured))

    for n in notes:
        print(f"  · {n}")
    for p in problems:
        print(f"  ✗ {p}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
