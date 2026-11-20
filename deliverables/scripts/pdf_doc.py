#!/usr/bin/env python3
"""Shared pieces for the two PDF builders.

The speaker script and the deck companion are both markdown first, and both
print a picture of a slide above the words for that slide. The pieces that
do that live here, so the two documents cannot drift apart in how they are
laid out.

The picture of a slide is drawn from the built `.pptx` by
`render_pptx_preview.py`, which reads the shapes and draws them with
matplotlib. It is an approximation of PowerPoint's layout rather than
PowerPoint's layout, so a word may sit slightly differently in the picture
than it will on the screen.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render_pptx_preview import render as _render_deck  # noqa: E402

#: The slide picture, as a fraction of the text width.
SLIDE_WIDTH = 0.88

#: The measured figure, as a fraction of the text width.
FIGURE_WIDTH = 0.82


def split_row(line: str) -> list[str]:
    """Split a pipe-table row into its cells.

    A pipe inside a cell is escaped, and a split on every pipe would cut
    that cell in two.
    """
    cells: list[str] = []
    cur: list[str] = []
    i = 0
    while i < len(line):
        ch = line[i]
        if ch == "\\" and i + 1 < len(line):
            cur.append(line[i:i + 2])
            i += 2
            continue
        if ch == "|":
            cells.append("".join(cur))
            cur = []
            i += 1
            continue
        cur.append(ch)
        i += 1
    cells.append("".join(cur))
    if cells and not cells[0].strip():
        cells = cells[1:]
    if cells and not cells[-1].strip():
        cells = cells[:-1]
    return [c.strip() for c in cells]


def plain_cell(cell: str) -> str:
    """The width of a cell's text, without the markup around it."""
    text = cell.replace("**", "").replace("`", "").replace("$", "")
    return " ".join(text.split())


def align_cell(cell: str, width: int) -> str:
    """A separator cell of the given width, keeping the alignment."""
    left, right = cell.startswith(":"), cell.endswith(":")
    if left and right:
        return ":" + "-" * max(width - 2, 1) + ":"
    if left:
        return ":" + "-" * max(width - 1, 1)
    if right:
        return "-" * max(width - 1, 1) + ":"
    return "-" * width


#: The characters a line of the table holds, used to turn a column's floor
#: into a share of the table's width. The count is deliberately on the low
#: side: a column that is a little too wide wraps, and a column that is a
#: little too narrow hyphenates a word in the middle.
CHARS_PER_LINE = 85


def _floor_share(cells: list[str]) -> float:
    """The share of the width a column must have to avoid breaking a word.

    A column narrower than its longest word hyphenates it. A column wider
    than its longest cell is wasted space, so the floor is capped by the
    content itself.
    """
    longest_word = 0
    longest_cell = 0
    for cell in cells:
        text = plain_cell(cell)
        longest_cell = max(longest_cell, len(text))
        for word in text.split():
            longest_word = max(longest_word, len(word))
    want = min(longest_cell, max(longest_word + 2, 20))
    return want / CHARS_PER_LINE


def widen_pipe_tables(text: str) -> str:
    """Give each column of a pipe table the width its content needs.

    Pandoc takes the widths of a pipe table's columns from the header
    separator row, and a uniform separator row gives columns close to equal
    widths. A table whose first column holds a number and whose second
    holds a sentence then prints that sentence wrapped over four lines. The
    separator is rewritten here so that each column gets a share of the
    width in proportion to the widest cell it holds.
    """
    lines = text.split("\n")
    out: list[str] = []
    i = 0
    while i < len(lines):
        if not lines[i].lstrip().startswith("|"):
            out.append(lines[i])
            i += 1
            continue
        block: list[str] = []
        while i < len(lines) and lines[i].lstrip().startswith("|"):
            block.append(lines[i])
            i += 1
        out.extend(widen_table(block))
    return "\n".join(out)


def widen_table(block: list[str]) -> list[str]:
    """Rewrite one pipe table's separator row."""
    if len(block) < 2:
        return block
    sep = split_row(block[1])
    if not sep or not all(re.fullmatch(r":?-+:?", c) for c in sep):
        return block

    n = len(sep)
    rows = [split_row(r) for r in (block[0], *block[2:])]
    weights: list[int] = []
    floors: list[float] = []
    for c in range(n):
        cells = [r[c] for r in rows if c < len(r)]
        widest = max((len(plain_cell(x)) for x in cells), default=0)
        weights.append(max(widest, 3))
        floors.append(_floor_share(cells))

    total = sum(weights)
    shares = [w / total for w in weights]

    # A column squeezed below its floor hyphenates the longest word in it,
    # which is the one table defect a reader notices without being able to
    # say why. So the columns that are short are widened to their floor, and
    # the space comes from the columns with the most to spare.
    for _ in range(n):
        need = [max(0.0, floors[i] - shares[i]) for i in range(n)]
        spare = [max(0.0, shares[i] - floors[i]) for i in range(n)]
        want_sum, spare_sum = sum(need), sum(spare)
        if want_sum <= 0 or spare_sum <= 0:
            break
        take = min(want_sum, spare_sum)
        for i in range(n):
            if need[i] > 0:
                shares[i] += take * need[i] / want_sum
            if spare[i] > 0:
                shares[i] -= take * spare[i] / spare_sum

    scale = sum(shares)
    dashes = [max(3, round(shares[i] / scale * 100)) for i in range(n)]
    # Pandoc takes the proportions from the separator row, so the row has to
    # add up to the width of the table.
    drift = 100 - sum(dashes)
    widest_col = max(range(n), key=lambda i: dashes[i])
    dashes[widest_col] = max(3, dashes[widest_col] + drift)

    new_sep = "|" + "|".join(align_cell(s, d) for s, d in zip(sep, dashes)) + "|"
    return [block[0], new_sep] + block[2:]


def raw_latex(latex: str) -> list[str]:
    """A block of raw LaTeX, passed through to the compiler untouched."""
    return ["```{=latex}", latex, "```", ""]


def picture_block(path: str, width: float) -> list[str]:
    """A picture in a thin frame, so a slide reads as a slide."""
    return raw_latex(
        "\\begin{center}\n"
        "\\setlength{\\fboxsep}{0pt}%\n"
        "\\setlength{\\fboxrule}{0.4pt}%\n"
        f"\\fbox{{\\includegraphics[width={width}\\linewidth]{{{path}}}}}\n"
        "\\end{center}")


def page_break() -> list[str]:
    return raw_latex("\\clearpage")


def render_slides(deck: Path, outdir: Path) -> dict[int, str]:
    """Draw every slide of the deck, and return the picture of each by number."""
    paths = _render_deck(deck, outdir)
    return {i + 1: p.name for i, p in enumerate(paths)}
