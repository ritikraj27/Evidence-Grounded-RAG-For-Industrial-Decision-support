#!/usr/bin/env python3
"""Render a markdown deliverable to PDF.

The chain is markdown -> pandoc -> LaTeX -> tectonic. Pandoc does the
structural conversion and the LaTeX template does the typography; tectonic
compiles, and it is the same engine the two `.tex` papers are checked with,
so a document that renders here renders with the tool the project already
trusts.

Two of the tools can be missing, and neither failure is silently absorbed:

* **pandoc** does the conversion. Without it there is no route from markdown
  to LaTeX in this project.
* **tectonic** compiles. Without it there is no PDF.

When an engine is absent the script reports which one and exits with the
code the build treats as "skipped, with a note" rather than "failed", because
a missing optional tool is not a defect in the document. When the engine is
present and the document does not compile, that *is* a failure and the exit
code says so.

Usage:
    python deliverables/scripts/make_pdf.py SOURCE.md OUTPUT.pdf
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = ROOT / "deliverables" / "templates" / "report_template.tex"

#: Exit code for "the tool that would render this is not installed". The
#: build treats it as a skip, not as a failure.
EXIT_NO_ENGINE = 3


def _which(name: str) -> str | None:
    return shutil.which(name)


#: Superscript characters and their ASCII equivalents.
#:
#: A measurement written as "2.5 x 10^-2" in Unicode is not renderable in a
#: T1-encoded LaTeX document: the superscript minus and the superscript zero
#: are not in the encoding, and they come out as noise -- "2.5 ? 108" in the
#: finished PDF. The scientific notation is therefore converted into LaTeX
#: math before pandoc sees it, which renders it properly and reads the same.
_SUPERSCRIPT = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹⁻", "0123456789-")
_SCI_RE = re.compile(r"(\d+(?:\.\d+)?)\s*×\s*10([⁰¹²³⁴⁵⁶⁷⁸⁹⁻]+)")

#: Symbols the Latin Modern text font does not carry. The compiler reports
#: each of these as "Missing character", and the document prints a blank
#: where they should be -- a silent loss in a document whose whole point is
#: that its numbers are legible. They are written as maths instead.
#:
#: The T1 text encoding carries the dashes, the section sign and the middle
#: dot, so those are left alone. It does not carry the Greek letters or the
#: mathematical operators, and those are the ones this table lists: the
#: framework's notation is Greek (kappa, tau, beta, sigma, rho) and the
#: documents quote it directly. The multiplication sign is here too: the
#: compiler maps it to a mojibake glyph rather than to the character, so
#: "74x" was printed as "74" followed by an unrelated letter -- a wrong
#: number in a document whose whole point is that its numbers are legible.
#:
#: The conversion runs on the *generated LaTeX*, not on the markdown.
#: Writing "$...$" into the markdown and letting pandoc read it is not safe:
#: pandoc refuses to close a maths span whose closing delimiter is followed
#: immediately by a digit, and escapes the dollar signs instead, so "2 x 2"
#: became "2\$\\times\$2" -- an escaped dollar followed by a maths command
#: outside maths, which does not compile. Converting afterwards leaves the
#: delimiters under this script's control.
_SYMBOLS_TEX = {
    "\u2192": r"\(\rightarrow\)",
    "\u0394": r"\(\Delta\)",
    "\u03ba": r"\(\kappa\)",
    "\u03c4": r"\(\tau\)",
    "\u03b2": r"\(\beta\)",
    "\u03c3": r"\(\sigma\)",
    "\u03c1": r"\(\rho\)",
    "\u03a3": r"\(\sum\)",
    "\u03a0": r"\(\prod\)",
    "\u2265": r"\(\geq\)",
    "\u2295": r"\(\oplus\)",
    "\u2227": r"\(\wedge\)",
    "\u00d7": r"\(\times\)",
    # The Unicode minus sign is not in the T1 text encoding either: it
    # renders as a blank in the compiled PDF, which is a silent loss in a
    # document whose numbers are the point. A plain hyphen-minus is used
    # instead, which is how the rest of the project writes a negative.
    "\u2212": "-",
}

#: Greek letters written with a Unicode subscript digit. These are replaced
#: before the single-character table runs, so that "beta sub zero" becomes
#: one maths expression rather than two adjacent ones with a gap between.
_SUBSCRIPTED_TEX = {
    "\u03b2\u2080": r"\(\beta_0\)",
    "\u03b2\u2081": r"\(\beta_1\)",
    "\u03c3\u2080": r"\(\sigma_0\)",
    "\u03c3\u2081": r"\(\sigma_1\)",
}

#: Regions of the generated LaTeX whose contents are literal: a verbatim
#: block, a listing, or an inline code span. The symbols are not converted
#: inside them, because a maths expression inside a verbatim block is
#: printed literally rather than typeset.
_LITERAL_REGIONS = re.compile(
    r"(\\begin\{(?:verbatim|Verbatim|listing|lstlisting)\}.*?"
    r"\\end\{(?:verbatim|Verbatim|listing|lstlisting)\})"
    r"|(\\texttt\{(?:[^{}]|\{[^{}]*\})*\})",
    re.S)


def _convert_symbols(tex: str) -> str:
    """Rewrite the symbols the text font cannot carry, as LaTeX maths.

    The literal regions -- verbatim blocks, listings and inline code spans
    -- are copied across untouched; everything between them is converted.
    """
    out = []
    pos = 0
    for m in _LITERAL_REGIONS.finditer(tex):
        out.append(_convert_prose(tex[pos:m.start()]))
        out.append(m.group(0))
        pos = m.end()
    out.append(_convert_prose(tex[pos:]))
    return "".join(out)


def _convert_prose(text: str) -> str:
    """The symbol conversion, applied to one stretch of ordinary prose."""
    text = _SCI_RE.sub(
        lambda m: (r"\(" + m.group(1) + r" \times 10^{"
                   + m.group(2).translate(_SUPERSCRIPT) + r"}\))"),
        text)
    for sym, latex in _SUBSCRIPTED_TEX.items():
        text = text.replace(sym, latex)
    for sym, latex in _SYMBOLS_TEX.items():
        text = text.replace(sym, latex)
    return text


def _strip_front_matter(text: str) -> str:
    """Drop the document's own title block.

    The markdown deliverable opens with its title, its subtitle and its
    author line, followed by a horizontal rule. The PDF carries those in a
    title block drawn from the metadata instead, so the markdown's copy of
    them would appear twice.

    A YAML metadata block is the same thing with the rules in the opposite
    places: it opens with a rule and closes with one. Dropping only the first
    rule would leave the metadata itself in the document, printed as text.
    """
    lines = text.split("\n")
    rules = ("---", "***", "___")
    if lines and lines[0].strip() in rules:
        for j in range(1, len(lines)):
            if lines[j].strip() in rules:
                return "\n".join(lines[j + 1:])
        return text
    for i, line in enumerate(lines):
        if line.strip() in rules:
            return "\n".join(lines[i + 1:])
    return text


def _strip_first_heading(text: str) -> str:
    """Drop the document's own top-level heading.

    Used when the title is supplied as metadata instead: pandoc would then
    print the title block and the heading underneath it, which says the same
    thing twice.
    """
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if line.startswith("# "):
            del lines[i]
            break
    return "\n".join(lines)


#: Pandoc turns an image's alt text into the figure's caption, and the LaTeX
#: template numbers the figure itself. An alt text that begins with
#: "Figure 4." therefore produced "Figure 1: Figure 4. ..." in the finished
#: PDF -- a duplicate, and a wrong one whenever the document's own numbering
#: differs from the number the caption was written with. The number is the
#: template's to supply, so it is dropped from the alt text on this path.
#: The markdown keeps its own copy of the number, so the Word path, which
#: prints the alt text as it stands, still numbers its captions.
_FIG_NUMBER_PREFIX = re.compile(r"(!\[)\s*Figure\s+\d+\.\s*")


def _strip_figure_numbers(text: str) -> str:
    """Drop a figure number written into an image's alt text."""
    return _FIG_NUMBER_PREFIX.sub(r"\1", text)


def _fix_table_widths(tex: str) -> str:
    """Correct the width arithmetic of pandoc's longtables.

    Pandoc writes every column as
    ``p{(\\linewidth - 6\\tabcolsep) * \\real{fraction}}``. The ``6`` is two
    column separations per column for a *three*-column table. For a wider
    table the widths add up to more than the line, longtable redistributes
    them, and the columns come out visibly uneven.

    The number of separations is two per column, so it is recomputed per
    table. The column specification is matched by brace counting rather than
    by a regular expression, because it contains braces of its own.
    """
    marker = "\\begin{longtable}[]{"
    out: list[str] = []
    i = 0
    while True:
        j = tex.find(marker, i)
        if j < 0:
            out.append(tex[i:])
            break
        out.append(tex[i:j])
        k = j + len(marker)
        depth = 1
        while depth:
            ch = tex[k]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
            k += 1
        spec = tex[j + len(marker):k]
        n_cols = spec.count("\\real{")
        if n_cols > 3:
            spec = spec.replace("6\\tabcolsep", f"{2 * n_cols}\\tabcolsep")
        out.append(marker + spec)
        i = k
    return "".join(out)


def main() -> int:
    if len(sys.argv) < 3:
        print("usage: make_pdf.py SOURCE.md OUTPUT.pdf [pandoc options...]")
        return 2

    # Both paths are resolved to absolute ones. The compiler is run with
    # the output directory as its working directory, so a relative output
    # path would be looked for twice over -- deliverables/deliverables/...
    src = Path(sys.argv[1]).resolve()
    out = Path(sys.argv[2]).resolve()
    extra = list(sys.argv[3:])
    # A long reference document needs a title block and a table of contents,
    # and it needs the title not to be repeated as the first heading. Both
    # are handled here rather than by every caller, so that a caller who
    # forgets them gets the same document rather than a different one.
    strip_heading = "--strip-first-heading" in extra
    extra = [a for a in extra if a != "--strip-first-heading"]
    strip_front = "--strip-front-matter" in extra
    extra = [a for a in extra if a != "--strip-front-matter"]
    if not src.exists():
        print(f"  ✗ {src} not found")
        return 1

    pandoc = _which("pandoc")
    tectonic = _which("tectonic")
    if not pandoc or not tectonic:
        missing = " and ".join(
            n for n, p in (("pandoc", pandoc), ("tectonic", tectonic)) if not p)
        print(f"  -- no PDF engine ({missing} not on PATH); skipping "
              f"{out.name}")
        return EXIT_NO_ENGINE

    work = out.with_suffix(".pdf.tex")
    work.parent.mkdir(parents=True, exist_ok=True)

    # The Unicode scientific notation is converted on a temporary copy, so
    # the markdown deliverable itself keeps the readable form.
    md = out.with_suffix(".pdf.md")
    _text = src.read_text(encoding="utf-8")
    if strip_front:
        _text = _strip_front_matter(_text)
    if strip_heading:
        _text = _strip_first_heading(_text)
    _text = _strip_figure_numbers(_text)
    md.write_text(_text, encoding="utf-8")

    cmd = [
        pandoc, str(md),
        "--from", "markdown+pipe_tables+raw_tex+fenced_code_blocks",
        "--to", "latex",
        "--standalone",
        # No syntax highlighting. The reports' code blocks are shell
        # commands and ASCII diagrams, and highlighting them buys nothing
        # while pulling in a large macro block that has to survive being
        # pasted into a template -- it did not, and the document did not
        # compile.
        "--no-highlight",
        "--template", str(TEMPLATE),
        "--output", str(work),
        # Keep the build self-contained: no network at compile time for
        # images that were not shipped with the document.
        "--resource-path", str(src.parent),
    ]
    cmd.extend(extra)
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  ✗ pandoc failed on {src.name}")
        for line in ((r.stdout or "") + (r.stderr or "")).splitlines()[-12:]:
            print("    " + line)
        return 1
    print(f"  [pdf] {src.name} -> {work.name}")

    # The column widths are corrected before compiling; see the function.
    tex = work.read_text(encoding="utf-8")
    fixed = _fix_table_widths(tex)
    if fixed != tex:
        print("  [pdf] corrected the longtable column widths")
    # The symbols the text font cannot carry are converted here rather than
    # in the markdown, so that the maths delimiters are this script's to
    # choose. See _convert_symbols.
    converted = _convert_symbols(fixed)
    if converted != fixed:
        print("  [pdf] rewrote the symbols the text font cannot carry")
    fixed = converted
    work.write_text(fixed, encoding="utf-8")

    # tectonic writes the PDF next to the .tex it is given.
    r = subprocess.run([tectonic, "-X", "compile", str(work)],
                       capture_output=True, text=True,
                       cwd=str(work.parent))
    produced = work.with_suffix(".pdf")
    if r.returncode != 0 or not produced.exists():
        print(f"  ✗ tectonic did not compile {work.name}")
        for line in ((r.stdout or "") + (r.stderr or "")).splitlines()[-15:]:
            print("    " + line)
        return 1

    if out.exists():
        out.unlink()
    produced.replace(out)
    work.unlink(missing_ok=True)
    md.unlink(missing_ok=True)
    # tectonic leaves its log beside the source. It is a build artefact, not
    # a deliverable, and it was ending up in the shipped folder.
    for _side in (work.with_suffix(".log"), work.with_suffix(".xdv")):
        _side.unlink(missing_ok=True)
    print(f"  [pdf] wrote {out.name} ({out.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
