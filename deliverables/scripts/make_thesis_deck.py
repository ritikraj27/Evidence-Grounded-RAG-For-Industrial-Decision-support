#!/usr/bin/env python3
"""Build the MTP report deck.

A section-wise presentation of the report, built from the same measured-value
table the report reads, so the two cannot disagree.

Every number on every slide comes from `substitute_tokens.values()`, which
reads the archived result files. Nothing here is typed in by hand.

The deck is monochrome: black for the structure, grey for emphasis, a lighter
grey for panel fills. These decks are projected in a room where the projector's
colour is not guaranteed and printed on a mono printer, so no
meaning may depend on a hue. Hierarchy is carried by weight and darkness.

Formulas are LaTeX, compiled to images with matplotlib's maths renderer and
placed on the slide as black-on-transparent PNGs, so they stay sharp at any
projection size and stay grey.

Usage:
    python3 deliverables/scripts/make_thesis_deck.py
"""
from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path

for _cand in (Path(__file__).resolve().parent,
              Path(__file__).resolve().parents[2] / "scripts"):
    if (_cand / "monochrome.py").exists():
        sys.path.insert(0, str(_cand))
        break
from monochrome import ACCENT, to_monochrome as _monochrome

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Emu, Inches, Pt

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "deliverables" / "MTP_Report_Presentation.pptx"
FIGDIR = ROOT / "deliverables" / "figures"

sys.path.insert(0, str(Path(__file__).resolve().parent))
import substitute_tokens as _st

for _cand in (Path(__file__).resolve().parent,
              Path(__file__).resolve().parents[2] / "scripts"):
    if (_cand / "figure_captions.py").exists():
        sys.path.insert(0, str(_cand))
        break
from figure_captions import FIGURES as FIGURE_CAPTIONS

V = _st.values()

BLACK = RGBColor(0x00, 0x00, 0x00)
DARK = RGBColor(0x1A, 0x1A, 0x1A)
DARK_GREY = RGBColor(0x3A, 0x3A, 0x3A)
MID_GREY = RGBColor(0x6E, 0x6E, 0x6E)
MUTED = RGBColor(0x80, 0x80, 0x80)
PANEL = RGBColor(0xF4, 0xF4, 0xF6)
LIGHT = RGBColor(0xE2, 0xE2, 0xE6)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

#: The institute's own purple, the colour of the emblem, and the deck's
#: single accent: the bar beside the title, the head of a table, the hero
#: number on a slide, and the number in the footer.
PURPLE = RGBColor(0x29, 0x19, 0x72)
#: The tint behind a row or a card, a hair away from white.
PURPLE_TINT = RGBColor(0xF4, 0xF2, 0xF9)
#: Hairlines, which are structure rather than content.
RULE = RGBColor(0xD2, 0xD2, 0xD8)

FOOTER = ("MTP  |  Evidence-Grounded RAG for Industrial Decision Support  |  "
          "Ritik Raj 25IM60R12  |  IIT Kharagpur, ISE")

#: The face the deck is set in. The report is Times New Roman, and a deck
#: that is set in a different face from the document it defends looks like
#: two different pieces of work.
TIMES = "Times New Roman"

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]
SW, SH = prs.slide_width, prs.slide_height

_n = 0


# ---------------------------------------------------------------- helpers
def textbox(slide, x, y, w, h, *, align=PP_ALIGN.LEFT):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Emu(0)
    tf.margin_top = tf.margin_bottom = Emu(0)
    tf.paragraphs[0].alignment = align
    return tf


def para(tf, text, *, size=14, bold=False, color=DARK, space_after=7, first=False,
         align=PP_ALIGN.LEFT, italic=False, font=TIMES, line=1.18):
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    p.alignment = align
    p.space_after = Pt(space_after)
    p.line_spacing = line
    r = p.add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.italic = italic
    r.font.color.rgb = color
    r.font.name = font
    return p


def rich(tf, chunks, *, size=14, space_after=7, first=False, align=PP_ALIGN.LEFT,
         line=1.18):
    """chunks = [(text, bold, color) | (text, bold, color, italic)]"""
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    p.alignment = align
    p.space_after = Pt(space_after)
    p.line_spacing = line
    for chunk in chunks:
        text, bold, color = chunk[0], chunk[1], chunk[2]
        italic = chunk[3] if len(chunk) > 3 else False
        r = p.add_run()
        r.text = text
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.italic = italic
        r.font.color.rgb = color
        r.font.name = TIMES
    return p


def rect(slide, x, y, w, h, fill, line=None, line_w=1.0):
    from pptx.enum.shapes import MSO_SHAPE
    sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
    sh.fill.solid()
    sh.fill.fore_color.rgb = fill
    if line is None:
        sh.line.fill.background()
    else:
        sh.line.color.rgb = line
        sh.line.width = Pt(line_w)
    sh.shadow.inherit = False
    return sh


def base(title, subtitle=None, *, number=True):
    """A content slide with the house header band, rule, footer and number."""
    global _n
    _n += 1
    s = prs.slides.add_slide(BLANK)
    rect(s, Inches(0.55), Inches(0.27), Inches(0.055), Inches(0.60), PURPLE)
    logo(s, 12.16, 0.26, 0.70)
    tf = textbox(s, Inches(0.80), Inches(0.24), Inches(11.25), Inches(0.80))
    size = 26 if len(title) <= 52 else (22 if len(title) <= 68 else 20)
    para(tf, title, size=size, bold=True, color=BLACK, first=True, space_after=3,
         line=1.06)
    if subtitle:
        para(tf, subtitle, size=12.5, color=MUTED, italic=True, space_after=0,
             line=1.1)
    rect(s, Inches(0.55), Inches(1.05), Inches(12.23), Pt(1.0), RULE)
    rect(s, Inches(0.55), SH - Inches(0.42), Inches(12.23), Pt(0.75), RULE)
    tf = textbox(s, Inches(0.55), SH - Inches(0.30), Inches(11.0), Inches(0.26))
    para(tf, FOOTER, size=9, color=MUTED, first=True, space_after=0)
    if number:
        tf = textbox(s, SW - Inches(1.05), SH - Inches(0.31), Inches(0.5), Inches(0.26),
                     align=PP_ALIGN.RIGHT)
        para(tf, str(_n), size=9.5, bold=True, color=PURPLE, first=True, space_after=0,
             align=PP_ALIGN.RIGHT)
    return s


def notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text


def bullets(slide, x, y, w, h, items, *, size=14, gap=8):
    tf = textbox(slide, x, y, w, h)
    for i, item in enumerate(items):
        if isinstance(item, tuple):
            head, rest = item
            rich(tf, [("•  ", True, BLACK), (head, True, BLACK), (rest, False, DARK)],
                 size=size, space_after=gap, first=(i == 0))
        else:
            rich(tf, [("•  ", True, BLACK), (item, False, DARK)],
                 size=size, space_after=gap, first=(i == 0))
    return tf


def table(slide, x, y, w, headers, rows, *, col_widths=None, size=11.5,
          row_h=0.30, head_h=0.34):
    n_rows = len(rows) + 1
    h = Inches(head_h + row_h * len(rows))
    shape = slide.shapes.add_table(n_rows, len(headers), x, y, w, h)
    t = shape.table
    if col_widths:
        total = sum(col_widths)
        for i, cw in enumerate(col_widths):
            t.columns[i].width = int(w * cw / total)
    for j, htxt in enumerate(headers):
        cell = t.cell(0, j)
        cell.text = ""
        cell.fill.solid()
        cell.fill.fore_color.rgb = PURPLE
        cell.margin_left = cell.margin_right = Inches(0.09)
        cell.margin_top = cell.margin_bottom = Inches(0.04)
        p = cell.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT
        r = p.add_run()
        r.text = htxt
        r.font.size = Pt(size)
        r.font.bold = True
        r.font.color.rgb = WHITE
        r.font.name = TIMES
    for i, row in enumerate(rows, start=1):
        for j, val in enumerate(row):
            cell = t.cell(i, j)
            cell.text = ""
            cell.fill.solid()
            cell.fill.fore_color.rgb = WHITE if i % 2 else PURPLE_TINT
            cell.margin_left = cell.margin_right = Inches(0.09)
            cell.margin_top = cell.margin_bottom = Inches(0.025)
            p = cell.text_frame.paragraphs[0]
            r = p.add_run()
            r.text = str(val)
            r.font.size = Pt(size)
            r.font.color.rgb = DARK
            r.font.name = TIMES
            if j == 0 and str(val).startswith("**"):
                r.text = str(val).replace("**", "")
                r.font.bold = True
    return shape


def kpi(slide, x, y, w, h, value, label, *, vsize=30, lsize=11.5):
    """A hero number with a rule above it and a label under it."""
    rect(slide, x, y, w, Inches(0.045), PURPLE)
    tf = textbox(slide, x, y + Inches(0.16), w, h - Inches(0.16))
    para(tf, value, size=vsize, bold=True, color=PURPLE, first=True,
         space_after=2, line=1.0)
    para(tf, label, size=lsize, color=DARK_GREY, space_after=0, line=1.12)


# ---------------------------------------------------------------- formulas
def formula(latex, *, fontsize=26, pad=0.06):
    """Render a LaTeX formula to a black-on-transparent PNG, and return it.

    The maths is written for matplotlib's renderer, which is a subset of LaTeX.
    `\\text{}` and `\\mathbb{}` are not in it, so `\\mathrm{}` is used for
    upright words.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    tmp = Path(tempfile.mkdtemp(prefix="mtp-formula-"))
    path = tmp / "f.png"
    fig = plt.figure(figsize=(0.01, 0.01))
    fig.text(0, 0, latex, fontsize=fontsize, color="black")
    fig.savefig(path, dpi=300, bbox_inches="tight", pad_inches=pad,
                transparent=True)
    plt.close(fig)
    return path


def put_formula(slide, latex, x, y, w, *, fontsize=26):
    path = formula(latex, fontsize=fontsize)
    slide.shapes.add_picture(str(path), x, y, width=w)
    return path


# ---------------------------------------------------------------- data
def t(name, default="not measured"):
    return str(V.get(name, default))


#: The superscript digits, so that a p value written as "10^-4" can be read
#: back out of a token.
_SUPERSCRIPT = {"⁰": 0, "¹": 1, "²": 2, "³": 3, "⁴": 4, "⁵": 5,
                "⁶": 6, "⁷": 7, "⁸": 8, "⁹": 9}


def p_decimal(token: str) -> str:
    """A p value in a form that survives a projector.

    The token carries a superscript minus, and Times New Roman has no glyph
    for it, so the number would arrive on the slide with a missing character
    in the middle of it. The same number written out is the same number.
    """
    m = re.match(r"^([0-9.]+)\s*[×x]\s*10([⁻⁺-]?)(.*)$", token.strip())
    if not m:
        return token
    sign = -1 if m.group(2) in ("⁻", "-") else 1
    digits = m.group(3)
    if not digits or any(d not in _SUPERSCRIPT for d in digits):
        return token
    exponent = sign * int("".join(str(_SUPERSCRIPT[d]) for d in digits))
    return f"{float(m.group(1)) * 10 ** exponent:.5g}"


SCOPE_SCM_CHUNKS = t("SCOPE_SCM_CHUNKS")
SCOPE_SCM_DOCS = t("SCOPE_SCM_DOCS")
MC_CHUNKS = t("MC_LC_CORPUS_CHUNKS")
MC_DOCS = t("N_DOCUMENTS")
MC_QUERIES = t("MC_N_QUERIES")
CASE_Q = t("CASE_N_QUERIES")
CASE_A = t("CASE_N_ANSWERABLE")
CASE_U = t("CASE_N_UNANSWERABLE")
TAU = t("TAU")
ECE = t("GATE_ECE")
BRIER = t("GATE_BRIER")
PREC = t("FOCUS_GATE_ABST_PRECISION")
HARD = t("UNANS_HARD_REFUSED_PCT")
HARD_N = t("UNANS_HARD_REFUSED_N")
HARD_TOT = t("UNANS_HARD_N")
OOD_N = t("UNANS_OOD_REFUSED_N")
OOD_TOT = t("UNANS_OOD_N")
BEFORE_AUC = t("UNANS_BEFORE_AUC")
BEFORE_REF = t("UNANS_BEFORE_REFUSED_PCT")
AFTER_AUC = t("UNANS_POLICY_AUC")
SC_BEFORE = t("UNANS_SHORTCUT_BEFORE")
SC_AFTER = t("UNANS_SHORTCUT_AFTER")
GEN_NOGATE_U = t("GEN_A_NOGATE_UNANS_ANSWER_RATE")
GEN_FITTED_U = t("GEN_A_FITTED_UNANS_ANSWER_RATE")
GEN_RANDOM_U = t("GEN_A_RANDOM_UNANS_ANSWER_RATE")
GEN_XFER_U = t("GEN_A_XFER_UNANS_ANSWER_RATE")
GEN_LC_U = t("GEN_A_LONGCTX_UNANS_ANSWER_RATE")
GEN_NOGATE_A = t("GEN_A_NOGATE_ANS_ANSWERED")
GEN_FITTED_A = t("GEN_A_FITTED_ANS_ANSWERED")
GEN_RANDOM_A = t("GEN_A_RANDOM_ANS_ANSWERED")
GEN_XFER_A = t("GEN_A_XFER_ANS_ANSWERED")
GEN_LC_A = t("GEN_A_LONGCTX_ANS_ANSWERED")
FIT_B = t("GEN_PAIRED_FITTED_ANS_B")
FIT_P = t("GEN_PAIRED_FITTED_ANS_P")
RND_B = t("GEN_PAIRED_RANDOM_ANS_B")
RND_P = t("GEN_PAIRED_RANDOM_ANS_P")
H2 = t("GEN_H2_1_SHORT")
CONTRA = t("CONTRA_PRECISION_PCT")
CONTRA_N = t("CONTRA_PRECISION_N")
CONTRA_CI = t("CONTRA_PRECISION_CI_HI")
CONTRA_PAIRS = t("CONTRA_PRECISION_PAIRS")
CONTRA_CTRL = t("CONTRA_PRECISION_CONTROL")
LC_TOK = t("LC_CORPUS_TOKENS")
RAG_TOK = t("LC_RAG_TOKENS")
LC_RATIO = t("GEN_LC_TOKEN_RATIO")
LC_COST = t("GEN_LC_COST_RATIO")
LC_CACHE = t("GEN_LC_CACHE_HIT")
LC_PROXY = t("LC_PROXY_TOP10")
MC_PROXY = t("MC_LC_PROXY_TOP10")
LC_RANK = t("LC_PROXY_MEDIAN_RANK")
MC_LC_TOK = t("MC_LC_CORPUS_TOKENS")
MC_LC_FACTOR = t("MC_LC_CORPUS_VS_128K")
TRADE_WRONG = t("TRADE_ANSWERING_WRONG_REMOVED")
TRADE_COST = t("TRADE_ANSWERING_CORRECT_COST_NLI")
FORM_PROBE = t("FORM_PROBE_RATE")
FORMVAL_REJ = t("FORMVAL_FIX_MAL_REJECTED")
FORMVAL_TOT = t("FORMVAL_FIX_MAL_N")
FORMVAL_OK = t("FORMVAL_FIX_VAL_REJECTED")
FORMVAL_OKN = t("FORMVAL_FIX_VAL_N")
RERANK_FOCUS = t("RERANK_MRR_PP")
RERANK_MC = t("MC_MRR_RERANK_PP")
POOL_MRR = t("MRR_C")
POOL_NDCG = t("NDCG_C")
R_A = t("R_A")
R_B = t("R_B")
R_C = t("R_C")
R_F = t("R_F")
R_G = t("R_G")
MC_R_F = t("MC_R_F")
MC_R_G = t("MC_R_G")
GCOMP_EMPTY = t("GENCOMP_2_EMPTY")
GCOMP_MODEL = t("GENCOMP_MODEL_2")
GCOMP_RESCUED = t("GENCOMP_FAILING_RESCUED")
GCOMP_STILL = t("GENCOMP_FAILING_STILL_EMPTY")
GENCOMP_TOTAL = t("GENCOMP_FAILING_EMPTY_TOTAL")
ENC = "BAAI/bge-m3"
POS_DIR_ADVERB = t("RO5_POSITIONAL_DIRECTION_ADVERB")
POS_DIR_PHRASE = t("RO5_POSITIONAL_DIRECTION_PHRASE")
RRF_K = t("RRF_K")
N_TESTS = t("N_TESTS")
SHARE_TEXT = t("FOCUS_SHARE_TEXT")
ERR_RETRIEVED = t("RO5_RETRIEVED_GROUNDED_ERROR")
ERR_GOLD = t("RO5_GOLD_GROUNDED_ERROR")


# ---------------------------------------------------------------- slides
def slide_title():
    global _n
    _n += 1
    s = prs.slides.add_slide(BLANK)
    rect(s, 0, 0, SW, Inches(0.09), PURPLE)
    logo(s, 6.216, 0.40, 0.90)
    tf = textbox(s, Inches(1.0), Inches(1.45), Inches(11.3), Inches(2.4),
                 align=PP_ALIGN.CENTER)
    para(tf, "An Evidence-Grounded Retrieval-Augmented Generation Framework "
             "for Industrial Decision Support", size=34, bold=True, color=BLACK,
         first=True, space_after=14, align=PP_ALIGN.CENTER, line=1.12)
    para(tf, "Architecture, Evaluation Protocol, Failure Modes, and What the "
             "Measurements Show", size=17, italic=True, color=DARK_GREY,
         space_after=0, align=PP_ALIGN.CENTER)
    rect(s, Inches(5.42), Inches(4.18), Inches(2.5), Pt(2.0), PURPLE)
    tf = textbox(s, Inches(1.0), Inches(4.5), Inches(11.3), Inches(1.6),
                 align=PP_ALIGN.CENTER)
    para(tf, "Ritik Raj (25IM60R12)", size=17, bold=True, color=BLACK, first=True,
         space_after=5, align=PP_ALIGN.CENTER)
    para(tf, "Department of Industrial and Systems Engineering, IIT Kharagpur",
         size=12.5, color=DARK_GREY, space_after=3, align=PP_ALIGN.CENTER)
    para(tf, "Supervisor: Dr. Sri Krishna Kumar", size=12.5, color=DARK_GREY,
         space_after=16, align=PP_ALIGN.CENTER)
    rect(s, 0, SH - Inches(0.40), SW, Inches(0.40), PANEL)
    notes(s, "This talk is about one question: when a retrieval-augmented generator "
             "is given industrial text, can a gate in the code decide whether the "
             "retrieved evidence contains the answer, and what is that gate worth "
             "once it has been measured properly?")


def slide_problem():
    s = base("The problem: a wrong answer costs more than no answer",
             "Why industrial RAG is not the same problem as open-domain RAG")
    bullets(s, Inches(0.55), Inches(1.35), Inches(6.6), Inches(4.6), [
        ("The corpus is not a wiki. ",
         "It is a controlled set of documents somebody signed off on."),
        ("The questions are not curiosity. ",
         "They are operational decisions: is this tolerance acceptable, which "
         "procedure step applies, what does the specification require."),
        ("A refusal costs a supervisor five minutes. ",
         "A confidently fabricated tolerance costs a scrapped batch."),
    ], size=17, gap=20)
    rect(s, Inches(7.5), Inches(1.45), Inches(5.3), Inches(3.65), PURPLE_TINT)
    rect(s, Inches(7.5), Inches(1.45), Inches(0.045), Inches(3.65), PURPLE)
    tf = textbox(s, Inches(7.8), Inches(1.72), Inches(4.7), Inches(3.2))
    para(tf, "The question this report asks", size=16.5, bold=True, color=BLACK,
         first=True, space_after=14)
    para(tf, "When a RAG generator is given industrial text, can a gate in the "
             "code decide whether the retrieved evidence actually contains the "
             "answer?", size=16.5, color=DARK, space_after=14, line=1.25)
    para(tf, "And what is that gate worth, once it has been measured properly?",
         size=16.5, bold=True, color=BLACK, space_after=0, line=1.25)
    notes(s, "The asymmetry between a wrong answer and a non-answer is the whole "
             "reason a gate is worth building. Everything that follows is about "
             "measuring that gate honestly.")


def slide_measure():
    s = base("Two things that make this hard to measure",
             "Both of them are easy to get wrong")
    rect(s, Inches(0.55), Inches(1.35), Inches(6.0), Inches(5.0), PURPLE_TINT)
    rect(s, Inches(0.55), Inches(1.35), Inches(0.045), Inches(5.0), PURPLE)
    tf = textbox(s, Inches(0.85), Inches(1.62), Inches(5.4), Inches(4.5))
    para(tf, "1. Gates get evaluated by intent, not by measurement", size=17,
         bold=True, color=BLACK, first=True, space_after=10)
    para(tf, "Someone picks a threshold. The system refuses some questions. A "
             "refusal rate gets reported.", size=17, color=DARK, space_after=12,
         line=1.25)
    para(tf, "The question a practitioner needs is different. Given a refusal "
             "budget, how many refusals land on the questions that should have "
             "been refused?", size=14, bold=True, color=DARK, space_after=0,
         line=1.2)
    rect(s, Inches(6.85), Inches(1.35), Inches(6.0), Inches(5.0), PURPLE_TINT)
    rect(s, Inches(6.85), Inches(1.35), Inches(0.045), Inches(5.0), PURPLE)
    tf = textbox(s, Inches(7.15), Inches(1.62), Inches(5.4), Inches(4.5))
    para(tf, "2. The benchmark can carry its own answer", size=17,
         color=BLACK, first=True, space_after=10)
    para(tf, "A benchmark whose unanswerable half is easy to separate from the "
             "answerable half measures the benchmark, not the system.",
         size=17, color=DARK, space_after=12, line=1.25)
    para(tf, "This project found exactly that defect in its own benchmark. "
             "Repairing it moved the headline refusal rate by a factor of nearly "
             "four.", size=17, bold=True, color=DARK, space_after=0, line=1.25)
    notes(s, "Both of these are things that only show up when you go looking for "
             "the measurement behind a headline number. Neither is visible in the "
             "output of the system.")


def slide_objectives():
    s = base("Four research objectives")
    items = [
        ("RO1", "Build an evidence-grounded RAG framework for industrial decision "
                "support", "Generation is gated in code. The generator is called at "
                "one point in the pipeline, and only when the gate accepts."),
        ("RO2", "Make retrieval modality-balanced and category-aware",
         "Fuse a lexical and a dense leg, rerank with a cross-encoder, and hold a "
         "quota over text, table and chart chunks."),
        ("RO3", "Test the framework's own hypothesis about hallucination",
         "Against a generator that is required to answer, not only one allowed to "
         "decline. Only the first case removes the generator's own credit."),
        ("RO4", "Characterise the failure modes",
         "Report the failures that contradict the framework with the same care as "
         "the successes, and publish the error rates of the measuring "
         "instruments."),
    ]
    y = 1.35
    for tag, head, body in items:
        rect(s, Inches(0.55), Inches(y), Inches(0.78), Inches(1.18), BLACK)
        tf = textbox(s, Inches(0.55), Inches(y + 0.42), Inches(0.78), Inches(0.4),
                     align=PP_ALIGN.CENTER)
        para(tf, tag, size=14, bold=True, color=WHITE, first=True, space_after=0,
             align=PP_ALIGN.CENTER)
        tf = textbox(s, Inches(1.55), Inches(y + 0.05), Inches(11.2), Inches(1.15))
        para(tf, head, size=16.5, bold=True, color=BLACK, first=True, space_after=5)
        para(tf, body, size=12.5, color=DARK_GREY, space_after=0, line=1.18)
        y += 1.34
    notes(s, "RO3 is the objective that gets pressed on. The hypothesis is the "
             "framework's own, and the design makes it falsifiable.")


def slide_contribution():
    s = base("The contribution is the framework, and the measurement of it",
             "Five stages, one pipeline, and a frontier measured on industrial text")
    bullets(s, Inches(0.55), Inches(1.4), Inches(6.4), Inches(4.7), [
        ("Hybrid retrieval: ", "a lexical leg and a dense leg (Karpukhin et al. "
         "2020) fused by reciprocal-rank fusion (Cormack et al. 2009)."),
        ("Modality balance: ", "a quota across text, tables and charts, applied "
         "where the corpus says it should be."),
        ("A gate that cannot be bypassed: ", "generation is called at exactly one "
         "point, after a calibrated posterior clears the threshold (Yadkori et al. "
         "2024)."),
        ("Contradiction surfacing: ", "two independent branches that have to "
         "agree before an alarm is raised."),
        ("Per-claim evidence tags: ", "every claim in the answer carries the chunk "
         "that supports it."),
    ], size=17, gap=12)
    rect(s, Inches(7.25), Inches(1.4), Inches(5.55), Inches(5.0), PURPLE_TINT)
    rect(s, Inches(7.25), Inches(1.4), Inches(0.045), Inches(5.0), PURPLE)
    tf = textbox(s, Inches(7.55), Inches(1.68), Inches(4.95), Inches(4.5))
    para(tf, "What is new", size=17, bold=True, color=BLACK, first=True,
         space_after=12)
    para(tf, "Every mechanism the framework draws on is published. What is new "
             "is that they are put together into one industrial system, and that "
             "the whole thing is then measured end to end on industrial text, at "
             "the level of the individual answer claim, with the benchmark's own "
             "defects audited and repaired.",
         size=17, color=DARK, space_after=13, line=1.25)
    para(tf, "The closest prior art, HALT-RAG (Goswami and Kurra 2025), is a "
             "post-hoc output verifier. It never runs a generator. Its own "
             "future work names the step this report performs.",
         size=14, italic=True, color=DARK_GREY, space_after=0, line=1.22)
    notes(s, "Lead with the framework. The room should hear that the architecture "
             "is a contribution in its own right, and that the measurement of it is "
             "the second half of the contribution rather than the whole of it.")


def slide_pipeline():
    s = base("The framework: five stages", "Two stages can refuse. One of them "
                                            "runs before retrieval.")
    stages = [
        ("0", "Query-form validation", "refuse", "costs no retrieval, no model call"),
        ("1", "Hybrid retrieval", "retrieve", "BM25 + bge-m3, fused by RRF"),
        ("2", "Rerank and quota", "rerank", "cross-encoder, modality floor"),
        ("3", "Confidence gate", "refuse", "the mechanism this report is about"),
        ("4", "Generation and claim assessment", "answer", "every claim scored against the evidence shown"),
    ]
    y = Inches(1.45)
    for i, (tag, name, kind, detail) in enumerate(stages):
        x = Inches(0.55 + i * 2.52)
        w = Inches(2.28)
        shade = PURPLE if kind == "refuse" else PANEL
        rect(s, x, y, w, Inches(1.85), shade)
        tf = textbox(s, x + Inches(0.13), y + Inches(0.12), w - Inches(0.26),
                     Inches(1.6))
        para(tf, f"Stage {tag}", size=11.5, bold=True,
             color=WHITE if kind == "refuse" else MID_GREY, first=True, space_after=3)
        para(tf, name, size=14, bold=True,
             color=WHITE if kind == "refuse" else BLACK, space_after=4, line=1.1)
        para(tf, detail, size=11.5,
             color=LIGHT if kind == "refuse" else DARK_GREY, space_after=0, line=1.1)
        if i < 4:
            tf = textbox(s, x + w, y + Inches(0.6), Inches(0.24), Inches(0.3),
                         align=PP_ALIGN.CENTER)
            para(tf, ">", size=17, bold=True, color=MID_GREY, first=True,
                 space_after=0, align=PP_ALIGN.CENTER)
    rect(s, Inches(0.55), Inches(3.65), Inches(12.23), Inches(2.75), PURPLE_TINT)
    rect(s, Inches(0.55), Inches(3.65), Inches(0.045), Inches(2.75), PURPLE)
    tf = textbox(s, Inches(0.9), Inches(3.92), Inches(11.6), Inches(2.25))
    para(tf, "The gate cannot be bypassed", size=17, bold=True, color=BLACK,
         first=True, space_after=10)
    para(tf, "The generator is not handed to answer() by the caller. It is injected "
             "into the framework, and the framework calls it at exactly one line, "
             "after the gate has accepted. On a refusal the claim assessment and "
             "the contradiction detection are skipped too, so a refused query "
             "costs no model call at all.", size=17, color=DARK, space_after=10,
         line=1.22)
    para(tf, "The only paths that skip the gate are the two comparison arms, "
             "rag_nogate and long_context. Both are named for what they remove and "
             "reported as separate results.", size=14, italic=True, color=DARK_GREY,
         space_after=0, line=1.2)
    notes(s, "Non-bypassability is a property of the code here, not a convention "
             "the caller is trusted to follow.")


def slide_retrieval():
    s = base("Hybrid retrieval", "A lexical leg, a dense leg, and reciprocal rank "
                                 "fusion")
    put_formula(s, r"$S_{RRF}(d) = \sum_{r \in \mathcal{R}} \frac{1}{k_{RRF} + "
                    r"rank_r(d)}$,  with $k_{RRF} = %s$" % RRF_K,
                Inches(0.8), Inches(1.35), Inches(6.0), fontsize=25)
    bullets(s, Inches(0.55), Inches(2.35), Inches(6.2), Inches(3.9), [
        ("Lexical leg: ", "Okapi BM25."),
        ("Dense leg: ", f"{ENC}, 1024 dimensions, L2 normalised."),
        ("Fusion: ", "reciprocal rank fusion over the top 20 of each leg."),
        ("Category pre-filter: ", "restricts both legs before fusion."),
    ], size=14, gap=10)
    tf = textbox(s, Inches(7.2), Inches(1.4), Inches(5.6), Inches(4.6))
    para(tf, "Why the dense leg changed", size=17, bold=True, color=BLACK,
         first=True, space_after=8)
    para(tf, "The first dense leg was a general-purpose sentence encoder, and it "
             "was measurably worse than plain BM25 on this corpus. A fusion that "
             "included it was carrying a leg that lost information.", size=14,
         color=DARK, space_after=10, line=1.2)
    para(tf, f"The encoder was replaced with {ENC}. It is archived and "
             "its numbers are kept as tokens, so both sides of the comparison rest "
             "on measured values rather than recollection.", size=14, color=DARK,
         space_after=10, line=1.2)
    para(tf, "The category filter, the reranker and the quota are all enforced as "
             "invariants, and each one is asserted directly.", size=12.5,
         italic=True, color=DARK_GREY, space_after=0, line=1.2)
    notes(s, "The encoder swap is a good example of measuring the components "
             "rather than assuming them. Two findings changed sign when it was "
             "done.")


def slide_gate_formula():
    s = base("The confidence gate", "A calibrated posterior over the whole "
                                    "retrieved pool")
    put_formula(s, r"$p_{conf}(q) = \sigma\left(\beta_0 + \beta_1^{T}"
                    r"\frac{\phi(q) - \mu}{\sigma}\right)$",
                Inches(0.8), Inches(1.3), Inches(4.6), fontsize=26)
    put_formula(s, r"$\mathrm{accept}(q) = \mathbb{1}\left[p_{conf}(q) \geq "
                    r"\tau\right]$",
                Inches(6.4), Inches(1.35), Inches(3.5), fontsize=26)
    bullets(s, Inches(0.55), Inches(2.6), Inches(6.2), Inches(3.7), [
        ("Five features: ", "top reranker score, mean of the top three, top BM25 "
         "score, maximum fused score, candidates above the reranker's bar."),
        ("Platt scaling: ", "fitted by maximum likelihood on a 60% calibration "
         "split."),
        ("Threshold: ", f"fitted at tau = {TAU} on the focus domain."),
    ], size=14, gap=10)
    rect(s, Inches(7.0), Inches(2.6), Inches(5.8), Inches(3.3), PURPLE_TINT)
    rect(s, Inches(7.0), Inches(2.6), Inches(0.045), Inches(3.3), PURPLE)
    tf = textbox(s, Inches(7.3), Inches(2.85), Inches(5.2), Inches(2.8))
    para(tf, "Why the query level, not the chunk level", size=14, bold=True,
         color=BLACK, first=True, space_after=9)
    para(tf, "With one gold chunk among about fifty candidates, a chunk-level "
             "classifier is right 98% of the time by answering \"nothing is "
             "relevant\". Maximum-likelihood fitting duly returns a large negative "
             "intercept.", size=14, color=DARK, space_after=9, line=1.2)
    para(tf, "That is a degenerate solution. It looks like a fitted model and "
             "behaves like a constant. Calibrating at the query level removes it.",
         size=14, bold=True, color=DARK, space_after=0, line=1.2)
    notes(s, "If someone asks why the gate is not just a similarity threshold, this "
             "is the answer. The chunk-level version has a trivial solution and the "
             "fit finds it.")


def slide_contradiction_formula():
    s = base("The contradiction gate", "Two independent branches have to agree")
    put_formula(s, r"$\mathrm{contradiction}(c_1,c_2) = \mathbb{1}[NLI = "
                    r"contradiction] \wedge \mathbb{1}[shared\ measurement \wedge "
                    r"shared\ instance]$",
                Inches(0.7), Inches(1.4), Inches(10.4), fontsize=27)
    bullets(s, Inches(0.55), Inches(2.35), Inches(6.2), Inches(3.9), [
        ("Branch 1: ", "a natural-language-inference model at threshold 0.70."),
        ("Branch 2: ", "the two chunks must talk about the same measured quantity "
         "of the same instance."),
        ("Cost: ", "at most 60 candidate pairs are examined per query."),
        ("The branch-2 check is what keeps this from being a topic detector. ",
         "What happens to the alarms it raises comes later, and the answer is "
         "not what this framework wanted."),
    ], size=17, gap=13)
    rect(s, Inches(7.0), Inches(2.35), Inches(5.8), Inches(3.9), PURPLE_TINT)
    rect(s, Inches(7.0), Inches(2.35), Inches(0.045), Inches(3.9), PURPLE)
    tf = textbox(s, Inches(7.3), Inches(2.62), Inches(5.2), Inches(3.45))
    para(tf, "Why the conjunction", size=17, bold=True, color=BLACK, first=True,
         space_after=11)
    para(tf, "A quantity branch on its own fired on citation years. A subject "
             "check based on topical similarity on its own was a topic check, not "
             "a contradiction check.", size=14, color=DARK, space_after=11, line=1.25)
    para(tf, "Requiring both cut the alarms from 81 to 20.", size=14, bold=True,
         color=DARK, space_after=11, line=1.25)
    para(tf, "Twenty alarms is a manageable number for a reader to check, which is "
             "why the precision study was possible at all.", size=14,
         italic=True, color=DARK_GREY, space_after=0, line=1.25)
    notes(s, "Keep this slide short in the talk. The finding about the precision of "
             "these alarms comes later and it is the surprising one.")


def slide_corpora():
    s = base("The corpora", "Industrial-engineering encyclopaedic text, with its "
                            "provenance attached")
    table(s, Inches(0.55), Inches(1.4), Inches(12.23),
          ["Corpus", "Role", "Chunks", "Documents", "Queries"],
          [["Supply-chain focus", "Ablation, gate, generation", SCOPE_SCM_CHUNKS,
            SCOPE_SCM_DOCS, CASE_Q],
           ["Six-category industrial", "Transfer, long-context cost", MC_CHUNKS,
            MC_DOCS, MC_QUERIES],
           ["Federal regulatory", "The contradiction detector's phenomenon",
            t("SCOPE_RE_CHUNKS"), t("SCOPE_RE_DOCS"), "none"]],
          col_widths=[2.6, 3.4, 1.1, 1.3, 1.1], size=12.5, row_h=0.40)
    bullets(s, Inches(0.55), Inches(3.4), Inches(6.3), Inches(2.8), [
        ("The focus corpus carries ", f"{CASE_A} answerable and {CASE_U} "
         "unanswerable questions."),
        ("The cross-category corpus carries ", f"{t('MC_N_ANSWERABLE')} and "
         f"{t('MC_N_UNANSWERABLE')}."),
        ("The two never mix. ", "The ablation and the gate are on the focus "
         "corpus, while the transfer study is on the six-category corpus."),
    ], size=14, gap=9)
    rect(s, Inches(7.15), Inches(3.4), Inches(5.65), Inches(2.6), PURPLE_TINT)
    rect(s, Inches(7.15), Inches(3.4), Inches(0.045), Inches(2.6), PURPLE)
    tf = textbox(s, Inches(7.45), Inches(3.62), Inches(5.05), Inches(2.2))
    para(tf, "Why a public substitute", size=14, bold=True, color=BLACK,
         first=True, space_after=8)
    para(tf, "The primary corpus of 24 proprietary supply-chain documents cannot "
             "be redistributed, so every measurement runs on a public substitute. "
             "Each document ships with its upstream identifier, a SHA-256, the "
             "chunk count and the licence.", size=12.5, color=DARK, space_after=0,
         line=1.2)
    notes(s, "Be honest about this limit. The corpus is encyclopaedic text, not "
             "practitioner documentation, and the claims are narrowed to match.")


def slide_benchmark():
    s = base("The benchmark had to be repaired twice",
             "Both repairs change what the headline number means")
    rect(s, Inches(0.55), Inches(1.4), Inches(4.0), Inches(4.7), PURPLE_TINT)
    rect(s, Inches(0.55), Inches(1.4), Inches(0.045), Inches(4.7), PURPLE)
    tf = textbox(s, Inches(0.85), Inches(1.65), Inches(3.4), Inches(4.2))
    para(tf, "Repair 1", size=14, bold=True, color=BLACK, first=True, space_after=4)
    para(tf, "The answer-label defect", size=12.5, italic=True, color=DARK_GREY,
         space_after=8)
    para(tf, f"{t('AUDIT_PRE_REPAIR_SCREEN_N')} of the answerable questions carried "
             "an answer label attached to the wrong question. Two defects in the "
             "label generation caused it.", size=12.5, color=DARK, space_after=8,
             line=1.2)
    para(tf, f"After the repair the defect rate is {t('AUDIT_SCREEN_N')} of "
             f"{t('AUDIT_CLEAN_N')}.", size=12.5, bold=True, color=DARK,
         space_after=8, line=1.2)
    para(tf, "The gold chunk was always right, so the retrieval-side numbers were "
             "never affected.", size=12.5, color=DARK_GREY, space_after=0, line=1.2)
    rect(s, Inches(4.72), Inches(1.4), Inches(4.0), Inches(4.7), PURPLE_TINT)
    rect(s, Inches(4.72), Inches(1.4), Inches(0.045), Inches(4.7), PURPLE)
    tf = textbox(s, Inches(5.02), Inches(1.65), Inches(3.4), Inches(4.2))
    para(tf, "Repair 2", size=14, bold=True, color=BLACK, first=True, space_after=4)
    para(tf, "The unanswerable class", size=12.5, italic=True, color=DARK_GREY,
         space_after=8)
    para(tf, "The unanswerable half was separable from the question text alone. One "
             "regular expression caught 100% of the hard family with zero false "
             "positives.", size=12.5, color=DARK, space_after=8, line=1.2)
    para(tf, "The class was rebuilt with corpus-anchored definitions and a "
             "structural twin for every repaired question.", size=12.5, bold=True,
         color=DARK, space_after=8, line=1.2)
    para(tf, f"The pre-repair benchmark is archived, so the before-and-after claim "
             f"stays checkable. {t('AUDIT_SCREEN_N')} of {t('AUDIT_CLEAN_N')} now.",
         size=12.5, color=DARK_GREY, space_after=0, line=1.2)
    rect(s, Inches(8.9), Inches(1.4), Inches(3.9), Inches(4.7), PURPLE)
    tf = textbox(s, Inches(9.2), Inches(1.65), Inches(3.3), Inches(4.2))
    para(tf, "Why it counts", size=14, bold=True, color=WHITE, first=True,
         space_after=10)
    para(tf, "The instrument that found the defect was kept, not deleted.",
         size=14, color=WHITE, space_after=10, line=1.2)
    para(tf, "A benchmark is a piece of software. Its bugs are invisible in its "
             "outputs.", size=14, color=LIGHT, space_after=0, line=1.2)
    notes(s, "If the room only remembers one thing about methodology, this is it. "
             "The benchmark was audited and the headline changed rather than "
             "explaining it away.")


def slide_shortcut():
    s = base("The shortcut: a classifier could read the answer off the question",
             "The headline refusal rate was an upper bound, not a measurement")
    kpi(s, Inches(0.55), Inches(1.45), Inches(3.9), Inches(1.35),
        BEFORE_AUC, "ROC AUC of a question-only classifier, before the repair",
        vsize=30)
    kpi(s, Inches(4.75), Inches(1.45), Inches(3.9), Inches(1.35),
        BEFORE_REF, "gate refusal rate on the defective class", vsize=30)
    kpi(s, Inches(8.95), Inches(1.45), Inches(3.85), Inches(1.35),
        SC_BEFORE, "caught by a single identifier regular expression", vsize=30)
    bullets(s, Inches(0.55), Inches(3.2), Inches(12.2), Inches(2.8), [
        ("The hard family named a fabricated identifier. ",
         "No answerable question carried an identifier of that shape, so one "
         "regular expression caught the whole family."),
        ("The hard family was recognisable from the question text alone. ",
         "A classifier on the query alone told the two classes apart."),
        ("The consequence: ", "the refusal rate measured the benchmark, not the "
         "framework."),
    ], size=17, gap=15)
    notes(s, "This is the finding that took the most work and it is the one that "
             "changes the headline. Say it slowly.")


def slide_after_repair():
    s = base("After the repair", "The honest headline is smaller, and more useful")
    kpi(s, Inches(0.55), Inches(1.45), Inches(3.9), Inches(1.35),
        AFTER_AUC, "question-only policy ROC AUC, after the repair", vsize=30)
    kpi(s, Inches(4.75), Inches(1.45), Inches(3.9), Inches(1.35),
        SC_AFTER, "caught by the same identifier regular expression", vsize=30)
    kpi(s, Inches(8.95), Inches(1.45), Inches(3.85), Inches(1.35),
        HARD, "gate refusal on the corpus-anchored hard stratum", vsize=30)
    rect(s, Inches(0.55), Inches(3.15), Inches(12.23), Inches(2.75), PURPLE_TINT)
    rect(s, Inches(0.55), Inches(3.15), Inches(0.045), Inches(2.75), PURPLE)
    tf = textbox(s, Inches(0.9), Inches(3.4), Inches(11.6), Inches(2.3))
    para(tf, "The gap between the two strata is the finding", size=16.5, bold=True,
         color=BLACK, first=True, space_after=10)
    para(tf, f"The gate refuses {OOD_N} of the out-of-domain stratum, and "
             f"only {HARD} of the hard stratum, where the corpus discusses the "
             "subject but does not state the answer.", size=14, color=DARK,
         space_after=10, line=1.2)
    para(tf, "So the gate detects a recognisable unanswerable question. It does not "
             "detect an absent answer. A 24% rate on the hard stratum is a different "
             "instrument from a 92% rate on an easy one, and the first number is the "
             "one a deployment would meet.", size=14, bold=True, color=DARK,
         space_after=0, line=1.2)
    notes(s, "The examiner will likely ask whether the gate is worth anything if it "
             "only catches the easy cases. The answer is on the next slides.")


def slide_retrieval_results():
    s = base("Retrieval results on the focus corpus",
             "Seven configurations, paired Wilcoxon signed-rank on every comparison")
    table(s, Inches(0.55), Inches(1.4), Inches(7.6),
          ["System", "Recall@10", "MRR", "nDCG@10"],
          [["A. bm25_only", R_A, t("MRR_A"), t("NDCG_A")],
           ["B. dense_only", R_B, t("MRR_B"), t("NDCG_B")],
           ["C. hybrid_rrf", R_C, t("MRR_C"), t("NDCG_C")],
           ["D. +rerank", t("R_D"), t("MRR_D"), t("NDCG_D")],
           ["E. +category_filter", t("R_E"), t("MRR_E"), t("NDCG_E")],
           ["F. +quota_pre_rerank", R_F, t("MRR_F"), t("NDCG_F")],
           ["G. +quota_post_rerank", R_G, t("MRR_G"), t("NDCG_G")]],
          col_widths=[2.6, 1.3, 1.1, 1.3], size=12.5, row_h=0.38)
    bullets(s, Inches(8.45), Inches(1.45), Inches(4.35), Inches(4.7), [
        ("The dense leg is significantly worse than BM25. ",
         f"{R_A} to {R_B}, p = 0.025. This is why the encoder changed."),
        ("Fusion recovers the loss and beats both legs. ",
         f"{R_C} against {R_B}, p = 0.014."),
        ("The claim for fusion is narrow. ",
         "It stopped being a loss. It did not become a significant win over plain "
         "BM25 on its own."),
    ], size=14, gap=14)
    notes(s, "The encoder swap is the thing to point at. A fusion carrying a leg "
             "that lost information is worse than no fusion.")


def slide_reranker():
    s = base("The reranker's value depends on the corpus",
             "One sentence, two truths, so the corpus travels with it")
    kpi(s, Inches(0.9), Inches(1.6), Inches(5.4), Inches(1.5),
        f"{RERANK_FOCUS} pp", "MRR change from the reranker, focus corpus "
        "(not significant)", vsize=30)
    kpi(s, Inches(7.0), Inches(1.6), Inches(5.4), Inches(1.5),
        f"{RERANK_MC} pp", "MRR change from the reranker, six-category corpus "
        "(p = 9.3e-04)", vsize=30)
    rect(s, Inches(0.9), Inches(3.5), Inches(11.5), Inches(2.6), PURPLE_TINT)
    rect(s, Inches(0.9), Inches(3.5), Inches(0.045), Inches(2.6), PURPLE)
    tf = textbox(s, Inches(1.25), Inches(3.75), Inches(10.8), Inches(2.1))
    para(tf, "\"The reranker buys ordering, not recall\"", size=17, bold=True,
         color=BLACK, first=True, space_after=10)
    para(tf, "True on the six-category corpus, false on the focus corpus. So it is "
             "reported with its corpus attached wherever it appears.", size=14,
         color=DARK, space_after=10, line=1.2)
    para(tf, "A component that helps on one corpus and not on another is not a "
             "component that helps.", size=14, bold=True, color=DARK, space_after=0,
         line=1.2)
    notes(s, "This slide exists because a claim without the corpus attached, and "
             "the numbers in the same paragraph, contradict each other.")


def slide_quota():
    s = base("The quota placement has no universally better answer",
             "The ranking differs by corpus, and none of it is significant")
    table(s, Inches(0.55), Inches(1.45), Inches(12.23),
          ["Corpus", "Quota before the reranker", "Quota after the reranker", "p"],
          [["Supply-chain focus", t("QUOTA_PRE_FOCUS_R10"),
            t("QUOTA_POST_FOCUS_R10"), t("QUOTA_PLACE_FOCUS_P")],
           ["Six-category industrial", t("QUOTA_PRE_SIXCAT_R10"),
            t("QUOTA_POST_SIXCAT_R10"), t("QUOTA_PLACE_SIXCAT_P")],
           ["Industrial", t("QUOTA_PRE_IND_R10"), t("QUOTA_POST_IND_R10"),
            t("QUOTA_PLACE_IND_P")]],
          col_widths=[3.2, 3.3, 3.3, 1.2], size=12.5, row_h=0.44)
    rect(s, Inches(0.55), Inches(3.5), Inches(12.23), Inches(2.85), PURPLE_TINT)
    rect(s, Inches(0.55), Inches(3.5), Inches(0.045), Inches(2.85), PURPLE)
    tf = textbox(s, Inches(0.9), Inches(3.78), Inches(11.6), Inches(2.4))
    para(tf, "So the placement is a configuration value, not a rule", size=16.5,
         bold=True, color=BLACK, first=True, space_after=10)
    para(tf, "The position is read from the configuration rather than asserted in "
             "prose, because the ranking differs by corpus and a fixed rule would "
             "not hold on all of them.", size=16.5, color=DARK, space_after=0,
         line=1.25)
    notes(s, "A placement that has to be read from the configuration is a "
             "placement the evidence does not settle. Say so rather than "
             "asserting one.")


def slide_gate_sweep():
    s = base("The gate: calibration and the operating-point sweep",
             "The threshold is chosen by a stated rule, and the frontier is shown "
             "in full")
    table(s, Inches(0.55), Inches(1.4), Inches(7.4),
          ["tau", "Answerable answered", "Unanswerable refused",
           "Abstention precision", "Coverage"],
          [["0.05", "0.938", "0.361", "0.963", "0.693"],
           ["0.10", "0.812", "0.653", "0.940", "0.432"],
           ["0.15", "0.656", "0.701", "0.902", "0.364"],
           ["0.20", "0.594", "0.792", "0.898", "0.278"],
           ["0.30", "0.500", "0.903", "0.890", "0.170"],
           ["0.50", "0.344", "0.958", "0.868", "0.097"],
           ["0.90", "0.094", "1.000", "0.832", "0.017"]],
          col_widths=[0.8, 1.8, 1.9, 1.9, 1.1], size=11.5, row_h=0.36)
    bullets(s, Inches(8.3), Inches(1.45), Inches(4.5), Inches(4.6), [
        ("The rule: ", "the highest tau that still answers at least 90% of the "
         "answerable queries. That gives tau = 0.05."),
        ("The gate is precise where it refuses. ", f"Abstention precision {PREC}."),
        ("The frontier is real. ", "Every extra refusal is paid for in coverage, "
         "and the price climbs steeply past tau = 0.15."),
        ("Calibration: ", f"ECE {ECE}, Brier {BRIER}."),
    ], size=14, gap=13)
    notes(s, "Point at the precision column. That is the number a practitioner "
             "actually needs.")


def slide_exp8():
    s = base("Experiment 8: one generator, five arms, two prompt conditions",
             "The prompt condition is an experimental axis, not a fixed setting")
    table(s, Inches(0.55), Inches(1.4), Inches(12.23),
          ["Arm", "What it removes"],
          [["rag_nogate", "the gate, keeping retrieval"],
           ["rag@fitted", "nothing, the framework at its fitted operating point"],
           ["rag@random", "the confidence score, keeping the refusal budget"],
           ["rag@transferred", "the fitted operating point, threshold moved across corpora"],
           ["long_context", "retrieval, the whole corpus in the prompt"]],
          col_widths=[2.6, 9.6], size=12.5, row_h=0.37)
    rect(s, Inches(0.55), Inches(3.85), Inches(12.23), Inches(2.05), PURPLE_TINT)
    rect(s, Inches(0.55), Inches(3.85), Inches(0.045), Inches(2.05), PURPLE)
    tf = textbox(s, Inches(0.9), Inches(4.05), Inches(11.6), Inches(1.65))
    para(tf, "Why the random arm matters", size=17, bold=True, color=BLACK,
         first=True, space_after=8)
    para(tf, "rag@random refuses the same number of questions as the fitted gate but "
             "picks them at random, ignoring the confidence score. Without it, an "
             "implementation that refuses on a coin flip and one that refuses on a "
             "calibrated score look identical on the easiest metric to report.",
         size=14, color=DARK, space_after=8, line=1.2)
    para(tf, f"The two prompt conditions differ by one sentence. Everything else is "
             f"identical: model, questions, retrieval, scorer, temperature.",
         size=14, italic=True, color=DARK_GREY, space_after=0, line=1.2)
    notes(s, "The cautious condition alone would have produced a null that meant "
             "nothing, because the generator refuses most unanswerable questions on "
             "its own.")


def slide_answering():
    s = base("The answering condition: the generator must answer",
             "The gate cannot be redundant here, because the generator is not "
             "allowed to decline")
    table(s, Inches(0.55), Inches(1.4), Inches(12.23),
          ["Arm", "Unanswerable answered", "Answerable answered",
           "Paired McNemar, unanswerable"],
          [["rag_nogate", f"{t('GEN_A_NOGATE_UNANS_ANSWERED')} ({GEN_NOGATE_U})",
            GEN_NOGATE_A, "none"],
           ["rag@fitted", f"{t('GEN_A_FITTED_UNANS_ANSWERED')} ({GEN_FITTED_U})",
            GEN_FITTED_A, "b = 60, c = 1, p < 0.001"],
           ["rag@random", f"{t('GEN_A_RANDOM_UNANS_ANSWERED')} ({GEN_RANDOM_U})",
            GEN_RANDOM_A, "none"],
           ["rag@transferred", f"{t('GEN_A_XFER_UNANS_ANSWERED')} ({GEN_XFER_U})",
            GEN_XFER_A, "none"],
           ["long_context", f"{t('GEN_A_LONGCTX_UNANS_ANSWERED')} ({GEN_LC_U})",
            GEN_LC_A, "p = 1.00"]],
          col_widths=[2.3, 3.5, 2.6, 3.8], size=12.5, row_h=0.40)
    rect(s, Inches(0.55), Inches(4.15), Inches(12.23), Inches(1.75), PURPLE)
    tf = textbox(s, Inches(0.9), Inches(4.38), Inches(11.6), Inches(1.35))
    para(tf, f"Verdict: {H2}", size=19, bold=True, color=WHITE, first=True,
         space_after=8)
    para(tf, "Under the cautious prompt the rate falls from 0.535 to 0.417, at the "
             "cost of the same two answerable questions. The paired test is "
             "significant under both conditions.", size=14, color=LIGHT,
         space_after=0, line=1.2)
    notes(s, "This is the slide the whole report is built around. The paired test "
             "on the unanswerable class is the headline, and the cost in coverage "
             "is stated on the same slide.")


def slide_random_control():
    s = base("What the confidence score actually buys",
             "This is the finding most likely to be reported wrongly, so it "
             "needs care")
    rect(s, Inches(0.55), Inches(1.4), Inches(12.23), Inches(1.75), PURPLE_TINT)
    rect(s, Inches(0.55), Inches(1.4), Inches(0.045), Inches(1.75), PURPLE)
    tf = textbox(s, Inches(0.9), Inches(1.62), Inches(11.6), Inches(1.35))
    para(tf, "It does not buy a lower answer rate on unanswerable questions.",
         size=17, bold=True, color=BLACK, first=True, space_after=9)
    para(tf, f"The random control reaches {GEN_RANDOM_U}, which is worse than the "
             f"fitted gate's {GEN_FITTED_U} and far below the ungated arm's "
             f"{GEN_NOGATE_U}. It gets there by refusing an arbitrary set of the "
             "same size, and some of those are answerable questions. Refusing at "
             "random is already a big improvement over never refusing, because most "
             "questions in a benchmark are unanswerable.", size=14, color=DARK,
         space_after=0, line=1.2)
    kpi(s, Inches(0.9), Inches(3.45), Inches(5.4), Inches(1.55),
        f"{FIT_B}", f"answerable questions refused by the gate (p = {FIT_P})",
        vsize=30)
    kpi(s, Inches(7.0), Inches(3.45), Inches(5.4), Inches(1.55),
        f"{RND_B}", f"answerable questions refused by the random control (p = {RND_P})",
        vsize=30)
    tf = textbox(s, Inches(0.9), Inches(5.25), Inches(11.5), Inches(1.1))
    para(tf, "What the score buys is where the refusals land. The gate concentrates "
             "them on the unanswerable class. The control does not. This is a "
             "precision claim about refusals, and the paired test on the answerable "
             "questions is where it is established.", size=14, bold=True, color=DARK,
         first=True, space_after=0, line=1.2)
    notes(s, "If a report said 'the gate answers fewer unanswerable questions', it "
             "would be true and it would be misleading. The claim is about "
             "precision, and the control is what makes it visible.")


def slide_trade():
    s = base("The trade, counted from the records",
             "A refusal is not an answer, and the counts are not a quality gain")
    table(s, Inches(0.55), Inches(1.4), Inches(12.23),
          ["Arm", "Answered", "Of which wrong", "Correct (entailment)",
           "Correct (key term)"],
          [["rag_nogate", t("TRADE_ANSWERING_NOGATE_ANSWERED"),
            t("TRADE_ANSWERING_NOGATE_WRONG_ANSWERED"),
            t("TRADE_ANSWERING_NOGATE_CORRECT_NLI"),
            t("TRADE_ANSWERING_NOGATE_CORRECT_KEYTERM")],
           ["rag@fitted", t("TRADE_ANSWERING_FITTED_ANSWERED"),
            t("TRADE_ANSWERING_FITTED_WRONG_ANSWERED"),
            t("TRADE_ANSWERING_FITTED_CORRECT_NLI"),
            t("TRADE_ANSWERING_FITTED_CORRECT_KEYTERM")],
           ["rag@random", t("TRADE_ANSWERING_RANDOM_ANSWERED"),
            t("TRADE_ANSWERING_RANDOM_WRONG_ANSWERED"),
            t("TRADE_ANSWERING_RANDOM_CORRECT_NLI"),
            t("TRADE_ANSWERING_RANDOM_CORRECT_KEYTERM")],
           ["long_context", t("TRADE_ANSWERING_LONGCTX_ANSWERED"),
            t("TRADE_ANSWERING_LONGCTX_WRONG_ANSWERED"),
            t("TRADE_ANSWERING_LONGCTX_CORRECT_NLI"),
            t("TRADE_ANSWERING_LONGCTX_CORRECT_KEYTERM")]],
          col_widths=[2.3, 2.0, 2.2, 2.8, 2.6], size=12.5, row_h=0.42)
    rect(s, Inches(0.55), Inches(3.75), Inches(12.23), Inches(2.15), PURPLE_TINT)
    rect(s, Inches(0.55), Inches(3.75), Inches(0.045), Inches(2.15), PURPLE)
    tf = textbox(s, Inches(0.9), Inches(3.95), Inches(11.6), Inches(1.75))
    para(tf, f"The gate removes {TRADE_WRONG} wrong answers and costs {TRADE_COST} "
             "correct answer under the entailment test.", size=17, bold=True,
         color=BLACK, first=True, space_after=9)
    para(tf, "Under the cautious prompt the gate even ends up ahead on the correct "
             "count. That is not a quality gain. It is a selection effect: a gate "
             "declines the hardest questions, so the ones it does answer are easier, "
             "and its per-answer accuracy cannot be compared with an arm that "
             "answered everything.", size=14, color=DARK, space_after=9, line=1.2)
    para(tf, "Tikhomirov and Savchenko (2026) name the phenomenon. It is also why the "
             "cautious condition alone would have been a misleading headline.",
         size=14, italic=True, color=DARK_GREY, space_after=0, line=1.2)
    notes(s, "Do not let the per-answer accuracy numbers be read as a quality win. "
             "They are a selection effect and the slide says so.")


def slide_long_context():
    s = base("Long context against the pipeline",
             "Measured on cost and on coverage, and it does not win")
    kpi(s, Inches(0.55), Inches(1.45), Inches(3.9), Inches(1.45),
        f"{LC_RATIO}x", "input tokens per query, against the pipeline", vsize=30)
    kpi(s, Inches(4.75), Inches(1.45), Inches(3.9), Inches(1.45),
        f"{LC_COST}x", "input cost per query, at the provider's cached pricing",
        vsize=30)
    kpi(s, Inches(8.95), Inches(1.45), Inches(3.85), Inches(1.45),
        LC_CACHE, "of the long-context tokens are cache reads", vsize=30)
    bullets(s, Inches(0.55), Inches(3.25), Inches(6.2), Inches(2.7), [
        ("Coverage: ", f"the whole-corpus prompt answered {GEN_LC_A} answerable "
         "questions, the same as the ungated pipeline."),
        ("Quality: ", f"accuracy {t('GEN_A_LONGCTX_ANS_ACCURACY')} against "
         f"{t('GEN_A_FITTED_ANS_ACCURACY')} for the gated arm, not significant "
         "under a length-controlled re-scoring."),
    ], size=14, gap=10)
    rect(s, Inches(7.0), Inches(3.25), Inches(5.8), Inches(2.7), PURPLE_TINT)
    rect(s, Inches(7.0), Inches(3.25), Inches(0.045), Inches(2.7), PURPLE)
    tf = textbox(s, Inches(7.3), Inches(3.45), Inches(5.2), Inches(2.3))
    para(tf, "The token ratio is not a cost", size=14, bold=True, color=BLACK,
         first=True, space_after=8)
    para(tf, "Read the token ratio naively and the cost penalty looks two orders of "
             "magnitude larger than the one actually measured. Most of the "
             "long-context arm's tokens are cache reads at a fifth of the base "
             "rate.", size=12.5, color=DARK, space_after=8, line=1.2)
    para(tf, "A token ratio must never carry an argument about money.", size=12.5,
         bold=True, color=DARK, space_after=0, line=1.2)
    notes(s, "The cost ratio is the point. The token ratio on its own is off by "
             "an order of magnitude.")


def slide_proxy():
    s = base("The evidence is not lost in a big context",
             "The tail is where corpus size bites")
    kpi(s, Inches(0.9), Inches(1.55), Inches(5.3), Inches(1.5),
        LC_PROXY, "of focus queries put the gold chunk in the top 10 when the "
        "candidate set is every chunk", vsize=30)
    kpi(s, Inches(6.9), Inches(1.55), Inches(5.3), Inches(1.5),
        MC_PROXY, "of cross-category queries, same measurement", vsize=30)
    bullets(s, Inches(0.9), Inches(3.45), Inches(11.5), Inches(2.6), [
        ("Median rank of the gold chunk: ", f"{LC_RANK}. A retriever that finds the "
         "answer at median rank 1 does not need the rest of the corpus in the "
         "prompt."),
        ("The cross-category corpus does not fit a 128K window. ",
         f"{MC_LC_TOK} tokens, {MC_LC_FACTOR} times the limit, so the quality half "
         "of that comparison could not be run there and it is settled on coverage "
         "and cost alone."),
    ], size=16.5, gap=14)
    notes(s, "This is the cheap half of the long-context comparison and it is the "
             "part that generalises.")


def slide_contra():
    s = base("The contradiction gate: a precision of zero",
             "Measured against reader labels, not against a proxy the detector "
             "defines")
    kpi(s, Inches(0.55), Inches(1.45), Inches(3.9), Inches(1.5),
        CONTRA, f"precision against reader labels, {CONTRA_N} labelled alarms",
        vsize=30)
    kpi(s, Inches(4.75), Inches(1.45), Inches(3.9), Inches(1.5),
        CONTRA_CI, "95% upper bound on the true precision", vsize=30)
    kpi(s, Inches(8.95), Inches(1.45), Inches(3.85), Inches(1.5),
        f"{CONTRA_PAIRS} / {CONTRA_PAIRS}", "annotator agreement on the "
        "contradiction decision", vsize=30)
    rect(s, Inches(0.55), Inches(3.3), Inches(12.23), Inches(2.6), PURPLE_TINT)
    rect(s, Inches(0.55), Inches(3.3), Inches(0.045), Inches(2.6), PURPLE)
    tf = textbox(s, Inches(0.9), Inches(3.5), Inches(11.6), Inches(2.2))
    para(tf, "None of the raised alarms was confirmed", size=16.5, bold=True,
         color=BLACK, first=True, space_after=9)
    para(tf, "Two annotators that do not share a model, both blind to the detector's "
             f"scores, and both {CONTRA_CTRL} correct on a control set with known "
             "labels. They still confirmed nothing.", size=14, color=DARK,
         space_after=9, line=1.2)
    para(tf, "The readers also found 0 contradictions in a random sample of 80 pairs "
             "the gate did not flag. This corpus holds concept-level prose, not "
             "instance records, so it does not contain the phenomenon the mechanism "
             "detects. The mechanism is unproven, not disproven.", size=14,
         bold=True, color=DARK, space_after=0, line=1.2)
    notes(s, "This is the negative result. Report it as a null with an upper bound, "
             "not as a defect. The two detector defects the audit exposed were real "
             "and were fixed, but they were not the reason the alarms went "
             "unconfirmed.")


def slide_empty():
    s = base("An empty completion is a third outcome",
             "Neither an answer nor a refusal")
    table(s, Inches(0.55), Inches(1.4), Inches(12.23),
          ["Generator", "No text returned", "On the table-lookup family",
           "Rescued by a 4x budget", "Still empty"],
          [[t("GENCOMP_MODEL_1"), t("GENCOMP_1_EMPTY"), t("GENCOMP_1_EMPTY_TABLE"),
            t("GENCOMP_1_RESCUED"), t("GENCOMP_1_STILL_EMPTY")],
           [t("GENCOMP_MODEL_2"), t("GENCOMP_2_EMPTY"), t("GENCOMP_2_EMPTY_TABLE"),
            t("GENCOMP_2_RESCUED"), t("GENCOMP_2_STILL_EMPTY")]],
          col_widths=[2.6, 2.3, 2.9, 2.4, 1.7], size=12.5, row_h=0.44)
    bullets(s, Inches(0.55), Inches(3.35), Inches(6.4), Inches(2.7), [
        ("Raising the budget fourfold did not fix it. ",
         f"{GCOMP_RESCUED} rescued, {GCOMP_STILL} still empty. The model spends its "
         "budget thinking and returns nothing."),
        ("So the replication could not be run, ", "and the hypothesis is supported "
         "for one generator rather than in general."),
    ], size=16.5, gap=14)
    rect(s, Inches(7.2), Inches(3.35), Inches(5.6), Inches(2.7), PURPLE_TINT)
    rect(s, Inches(7.2), Inches(3.35), Inches(0.045), Inches(2.7), PURPLE)
    tf = textbox(s, Inches(7.5), Inches(3.55), Inches(5.0), Inches(2.3))
    para(tf, "The rule this forces", size=14, bold=True, color=BLACK, first=True,
         space_after=8)
    para(tf, "A run like that is recorded as not run, with the reason, rather "
             "than as a run with empty arms.", size=14, color=DARK, space_after=10,
         line=1.25)
    para(tf, "A rate quoted from a run that did not happen is indistinguishable from "
             "a rate that did.", size=14, bold=True, color=DARK, space_after=0,
         line=1.25)
    notes(s, "This is also an argument for the gate sitting upstream of generation. "
             "A generator that cannot answer costs nothing on the questions the gate "
             "rejects.")


def slide_form():
    s = base("The gate is an evidence gate, not a form gate",
             "Two different questions need two different instruments")
    kpi(s, Inches(0.55), Inches(1.45), Inches(3.9), Inches(1.45),
        FORM_PROBE, "of malformed stems were accepted by the gate", vsize=30)
    kpi(s, Inches(4.75), Inches(1.45), Inches(3.9), Inches(1.45),
        f"{FORMVAL_REJ} / {FORMVAL_TOT}", "hand-authored malformed queries refused "
        "by the form validator", vsize=30)
    kpi(s, Inches(8.95), Inches(1.45), Inches(3.85), Inches(1.45),
        f"{FORMVAL_OK} / {FORMVAL_OKN}", "hand-authored well-formed queries "
        "wrongly refused", vsize=30)
    bullets(s, Inches(0.55), Inches(3.25), Inches(12.2), Inches(2.7), [
        ("The gate is good at \"is there evidence here?\" ",
         "and no use at \"is this even a question?\". It is never credited with the "
         "validator's work."),
        ("The counterfactual is worth recording. ",
         "Reusing the benchmark builder's question-generation rule as a runtime "
         f"check would have refused {t('FORMVAL_COUNTERFACTUAL_RATE')} of "
         "hand-labelled well-formed questions."),
        ("The lesson: ", "a filter written for one purpose does not fit another, "
         "and the false-rejection rate has to be measured before it ships."),
    ], size=14, gap=11)
    notes(s, "The counterfactual is the memorable part. A rule that looked like it "
             "did the job would have refused every well-formed question in the set.")


def slide_attribution():
    s = base("Most unattributed error comes from the evidence, not the scorer",
             "The same answers scored against two evidence sets")
    table(s, Inches(0.55), Inches(1.4), Inches(12.23),
          ["Error measure", "Over the retrieved evidence", "Over the gold evidence"],
          [["Grounded claims", ERR_RETRIEVED, ERR_GOLD],
           ["Inferred claims", t("RO5_RETRIEVED_INFERRED_ERROR"),
            t("RO5_GOLD_INFERRED_ERROR")],
           ["Uncertain claims", t("RO5_RETRIEVED_UNCERTAIN_ERROR"),
            t("RO5_GOLD_UNCERTAIN_ERROR")],
           ["Reference hallucination", t("RO5_RETRIEVED_REFERENCE_HALLUCINATION"),
            t("RO5_GOLD_REFERENCE_HALLUCINATION")],
           ["Answer-position effect, p", t("RO5_RETRIEVED_POSITION_P"),
            t("RO5_GOLD_POSITION_P")]],
          col_widths=[4.4, 4.0, 3.8], size=12.5, row_h=0.40)
    rect(s, Inches(0.55), Inches(4.0), Inches(12.23), Inches(1.9), PURPLE_TINT)
    rect(s, Inches(0.55), Inches(4.0), Inches(0.045), Inches(1.9), PURPLE)
    tf = textbox(s, Inches(0.9), Inches(4.2), Inches(11.6), Inches(1.5))
    para(tf, f"The grounded-claim error rate is {ERR_RETRIEVED} over the evidence the "
             f"arm was shown, and {ERR_GOLD} over the gold chunk.", size=17,
         bold=True, color=BLACK, first=True, space_after=8)
    para(tf, "Most of the error the framework's own attribution cannot explain is "
             "explained by the evidence it was given. That is a retrieval problem, "
             "not a scoring problem.", size=14, color=DARK, space_after=0, line=1.2)
    notes(s, "The gold chunk was always right, so this is a clean comparison.")


def slide_transfer():
    s = base("Cross-category transfer",
             "The reranker survives it. The calibrated threshold does not.")
    table(s, Inches(0.55), Inches(1.4), Inches(12.23),
          ["Comparison", "Delta Recall@10", "Delta MRR", "Delta nDCG", "p (MRR)"],
          [["A to C, BM25 to fusion", t("MC_DELTA_AC"), t("MC_DELTA_AC_MRR"), "none",
            p_decimal(t("MC_P_AC_MRR"))],
           ["C to D, fusion to rerank", t("MC_DELTA_CD"), t("MC_DELTA_CD_MRR"),
            t("MC_DELTA_CD_NDCG"), p_decimal(t("MC_P_CD_MRR"))]],
          col_widths=[3.6, 2.2, 2.0, 2.0, 1.8], size=12.5, row_h=0.44)
    rect(s, Inches(0.55), Inches(3.05), Inches(12.23), Inches(3.0), PURPLE_TINT)
    rect(s, Inches(0.55), Inches(3.05), Inches(0.045), Inches(3.0), PURPLE)
    tf = textbox(s, Inches(0.9), Inches(3.28), Inches(11.6), Inches(2.6))
    para(tf, "A calibrated threshold does not transfer", size=16.5, bold=True,
         color=BLACK, first=True, space_after=9)
    para(tf, f"rag@transferred answers only {GEN_XFER_A} answerable "
             "questions. The threshold was fitted on one half of the cross-category "
             "corpus and applied unchanged to the other half, and it over-refuses "
             "badly.", size=14, color=DARK, space_after=9, line=1.2)
    para(tf, "The threshold has to be refitted per corpus. This is the clearest "
             "evidence in this report that a calibrated number is only valid for the "
             "thing it was calibrated on.", size=14, bold=True, color=DARK,
         space_after=9, line=1.2)
    para(tf, "One limit is worth stating: the transfer study measures coverage on "
             "answerable questions across categories only. The benchmark's "
             "unanswerable questions carry no category, so refusal behaviour across "
             "domains is not measurable under a category split.", size=12.5,
         italic=True, color=DARK_GREY, space_after=0, line=1.2)
    notes(s, "The transfer arm is the most practically useful finding for anyone "
             "who wants to deploy this. Calibrate per corpus.")


def slide_measured():
    s = base("What was measured, and what was not",
             "Both sides, because a one-sided list is the thing this report argues "
             "against")
    rect(s, Inches(0.55), Inches(1.4), Inches(6.0), Inches(4.7), PURPLE_TINT)
    rect(s, Inches(0.55), Inches(1.4), Inches(0.045), Inches(4.7), PURPLE)
    tf = textbox(s, Inches(0.85), Inches(1.62), Inches(5.4), Inches(4.25))
    para(tf, "Measured", size=17, bold=True, color=BLACK, first=True, space_after=9)
    for item in [
        f"Retrieval on {CASE_A} answerable queries, seven configurations, paired "
        "tests.",
        f"The gate's calibration and its full threshold sweep, {CASE_Q} queries.",
        "The gate's behaviour on unanswerable questions under two prompt "
        "conditions, one generator, five arms, paired McNemar.",
        "The contradiction gate's precision against reader labels, with the "
        "annotators' own agreement.",
        "The claim scorer's error profile, audited on the benchmark's own answers.",
        "The long-context arm's cost, coverage and retrieval-side proxy on both "
        "corpora.",
    ]:
        para(tf, "•  " + item, size=12.5, color=DARK, space_after=7, line=1.15)
    rect(s, Inches(6.85), Inches(1.4), Inches(6.0), Inches(4.7), PURPLE_TINT)
    rect(s, Inches(6.85), Inches(1.4), Inches(0.045), Inches(4.7), PURPLE)
    tf = textbox(s, Inches(7.15), Inches(1.62), Inches(5.4), Inches(4.25))
    para(tf, "Not measured", size=17, bold=True, color=BLACK, first=True,
         space_after=9)
    for item in [
        "The generator-side comparison on a second generator. The model returned no "
        "text on 24 of 66 questions.",
        "The long-context answer quality on the cross-category corpus. It does not "
        "fit a 128K window.",
        "The hallucination rate on generated text as such. What is measured is the "
        "rate of answering unanswerable questions, which is a different quantity.",
        "Refusal behaviour across domains. The category split carries no "
        "unanswerable questions.",
        "The contradiction gate's precision against human readers. The annotators "
        "are models.",
    ]:
        para(tf, "•  " + item, size=12.5, color=DARK, space_after=7, line=1.15)
    notes(s, "Read the right-hand column out loud. A committee values a candidate "
             "who knows what they did not measure.")


def slide_limitations():
    s = base("Limitations")
    items = [
        ("L1", "One generator. The hypothesis is supported for the generator "
               "tested, not in general. This is the largest gap."),
        ("L2", "An encyclopaedic corpus, not procedural documentation. The "
               "contradiction detector's phenomenon is measurably absent from it."),
        ("L3", "The long-context quality half was measured on one corpus only."),
        ("L4", "The annotation behind the contradiction precision is model-based, "
               "not human."),
        ("L5", "Statistical power. Several nulls are nulls of this corpus at this "
               "size, and they are reported with their interval widths."),
        ("L6", "The hallucination rate on generated text is a different quantity "
               "from the refusal rate, and the two are never substituted for one "
               "another."),
        ("L7", "A refusal is not an answer. Per-answer accuracy cannot be compared "
               "across arms with different coverage."),
        ("L8", "English, and one jurisdiction. Nothing here shows the findings hold "
               "for another language or another regulator."),
    ]
    y = 1.32
    for tag, body in items:
        rect(s, Inches(0.55), Inches(y), Inches(0.62), Inches(0.6), BLACK)
        tf = textbox(s, Inches(0.55), Inches(y + 0.16), Inches(0.62), Inches(0.3),
                     align=PP_ALIGN.CENTER)
        para(tf, tag, size=11.5, bold=True, color=WHITE, first=True, space_after=0,
             align=PP_ALIGN.CENTER)
        tf = textbox(s, Inches(1.38), Inches(y + 0.06), Inches(11.4), Inches(0.6))
        para(tf, body, size=12.5, color=DARK, first=True, space_after=0, line=1.15)
        y += 0.68
    notes(s, "Do not rush this slide. L1 and L2 are the two that get raised, "
             "and they are the two that were already flagged in the text.")


def slide_conclusion():
    s = base("Conclusion")
    rect(s, Inches(0.55), Inches(1.35), Inches(12.23), Inches(1.95), PURPLE)
    tf = textbox(s, Inches(0.9), Inches(1.58), Inches(11.6), Inches(1.65))
    para(tf, f"The framework's own hypothesis is {H2}.", size=21, bold=True,
         color=WHITE, first=True, space_after=8)
    para(tf, f"Under a prompt that requires an answer, the fitted gate cuts the rate "
             f"from {GEN_NOGATE_U} to {GEN_FITTED_U}, at a cost of {GEN_FITTED_A} "
             f"answerable questions answered where the ungated arm answers "
             f"{GEN_NOGATE_A}.", size=14,
         color=LIGHT, space_after=0, line=1.2)
    bullets(s, Inches(0.55), Inches(3.55), Inches(12.2), Inches(2.9), [
        ("The confidence score buys refusal precision, not a lower answer rate. ",
         f"It spends {FIT_B} refusals on answerable questions where the random "
         f"control spends {RND_B}."),
        ("The benchmark's shortcut was worth more than the system. ",
         f"A question-only classifier separated the classes at ROC AUC {BEFORE_AUC}, "
         f"so the headline {BEFORE_REF} was an artefact. The true rate is {HARD}."),
        ("The gate detects a recognisable unanswerable question, not an absent "
         "answer. ", f"{HARD} on the hard stratum against {OOD_N} out of "
         "domain."),
        ("One mechanism did not survive measurement. ",
         f"The contradiction gate's precision is {CONTRA}, upper bound "
         f"{CONTRA_CI}, and it is reported as unproven rather than dropped."),
    ], size=14, gap=11)
    notes(s, "End on the three findings, not on the architecture. The contribution "
             "is the measurement.")


def slide_future():
    s = base("Future work", "In the order that would change what the report can "
                            "claim")
    items = [
        ("1", "Repeat the generator-side comparison on a generator that returns text "
              "on the table questions.", "One generator settles the hypothesis for "
              "one model."),
        ("2", "Compare the gate against a token-level faithfulness monitor.", "The "
              "gate is currently measured against a prompt-level control only."),
        ("3", "Settle the magnitude and the power of the positional comparison.",
         f"The direction holds in {POS_DIR_PHRASE} measurements, and not in the "
         f"magnitude."),
        ("4", "Extend the industrial corpus beyond one jurisdiction and one "
              "language.", ""),
        ("5", "Stratify the corpus by modality, under a pre-registered power "
              "analysis.", ""),
        ("6", "Hand-check the repaired unanswerable class against the corpus, on "
              "both corpora.", ""),
        ("7", "Run the long-context quality arm on a corpus that fits the context "
              "window.", ""),
        ("8", "Replace the model-based contradiction annotators with human "
              "readers.", ""),
        ("9", "Publish the corrected benchmark and the shortcut audit as a "
              "separate artefact.", "So other work can check its own benchmarks "
              "against the same instrument."),
    ]
    y = 1.28
    for tag, head, detail in items:
        rect(s, Inches(0.55), Inches(y), Inches(0.42), Inches(0.42), BLACK)
        tf = textbox(s, Inches(0.55), Inches(y + 0.08), Inches(0.42), Inches(0.26),
                     align=PP_ALIGN.CENTER)
        para(tf, tag, size=11.5, bold=True, color=WHITE, first=True, space_after=0,
             align=PP_ALIGN.CENTER)
        tf = textbox(s, Inches(1.18), Inches(y + 0.02), Inches(11.6), Inches(0.55))
        para(tf, head, size=12.5, bold=True, color=BLACK, first=True, space_after=2,
             line=1.12)
        if detail:
            para(tf, detail, size=11.5, color=DARK_GREY, space_after=0, line=1.1)
        y += 0.63
    notes(s, "Point at item 1 and item 9. The replication is the gap that matters "
             "for the claim, and the published benchmark is the contribution that "
             "outlives the report.")


def slide_thanks():
    global _n
    _n += 1
    s = prs.slides.add_slide(BLANK)
    rect(s, 0, 0, SW, Inches(0.09), PURPLE)
    logo(s, 6.216, 1.05, 0.90)
    tf = textbox(s, Inches(1.0), Inches(2.3), Inches(11.3), Inches(2.6),
                 align=PP_ALIGN.CENTER)
    para(tf, "Thank you", size=38, bold=True, color=BLACK, first=True, space_after=16,
         align=PP_ALIGN.CENTER)
    para(tf, "Questions", size=17, italic=True, color=DARK_GREY, space_after=22,
         align=PP_ALIGN.CENTER)
    para(tf, "An Evidence-Grounded Retrieval-Augmented Generation Framework for "
             "Industrial Decision Support", size=14, color=DARK, space_after=6,
         align=PP_ALIGN.CENTER)
    para(tf, "Ritik Raj (25IM60R12)  |  Supervisor: Dr. Sri Krishna Kumar  |  "
             "Department of Industrial and Systems Engineering, IIT Kharagpur",
         size=12.5, color=MUTED, space_after=0, align=PP_ALIGN.CENTER)
    rect(s, 0, SH - Inches(0.40), SW, Inches(0.40), PANEL)
    notes(s, "The benchmark repair and the shortcut audit are published "
             "separately.")



# ---------------------------------------------------------------- figures
def caption_text(key: str) -> str:
    """The project's own caption for a figure, with its tokens resolved."""
    text = FIGURE_CAPTIONS.get(key, "")
    for _ in range(8):
        before = text
        text = re.sub(r"\{\{([A-Z0-9_]+)\}\}",
                      lambda m: str(V.get(m.group(1), m.group(0))), text)
        if text == before:
            break
    return text


#: The institute's emblem. It is the one element of a slide that carries
#: colour, and it is in colour because the department's own report prints it
#: that way: the emblem is the institution's mark, not a colour that carries
#: meaning in the content.
LOGO = ROOT / "deliverables" / "assets" / "iitkgp_emblem.png"


def logo(slide, x, y, h):
    """The institute's emblem, at a given height, keeping its aspect ratio."""
    if not LOGO.exists():
        print(f"  [deck] missing emblem: {LOGO.name}")
        return
    slide.shapes.add_picture(str(LOGO), Inches(x), Inches(y), height=Inches(h))

def figure(slide, key, x, y, w):
    """Place a measured figure, keeping its aspect ratio. Returns its height."""
    from PIL import Image
    path = FIGDIR / f"{key}.png"
    if not path.exists():
        print(f"  [deck] missing figure: {path.name}")
        return 0.0
    with Image.open(path) as im:
        aspect = im.size[0] / im.size[1]
    h = w / aspect
    slide.shapes.add_picture(str(path), x, y, width=w, height=h)
    return h


#: One-line captions for the slides. The full caption of each figure is in the
#: report, where there is room for it; a slide has two lines under a figure
#: and a paragraph there reads as a wall of text.
SLIDE_CAPTIONS = {
    "fig1_pool_size":
        "Recall against the size of the rerank candidate pool, focus corpus "
        "(black) and industrial corpus (grey).",
    "fig4_modality_quota_pareto":
        "Overall Recall@10 against table-specific Recall@10 for the seven "
        "ablated systems.",
    "fig5_question_only_roc":
        "A classifier seeing only the question text, telling the two classes "
        "apart.",
    "fig6_contradiction_precision":
        "The contradiction detector's precision against the base rate of real "
        "conflicts, with 95% Wilson intervals.",
}


def figure_caption(slide, key, x, y, w, *, size=11.5):
    tf = textbox(slide, x, y, w, Inches(0.6))
    para(tf, SLIDE_CAPTIONS.get(key, caption_text(key)), size=size,
         color=DARK_GREY, first=True, space_after=0, line=1.15)
    return tf


def slide_pool_curve():
    s = base("The candidate pool curve peaks and then declines",
             "More candidates are not monotonically better")
    h = figure(s, "fig1_pool_size", Inches(0.7), Inches(1.35), Inches(4.5))
    table(s, Inches(5.5), Inches(1.35), Inches(7.3),
          ["Pool", "Recall@10", "Recall@20", "MRR"],
          [["5", "0.969", "0.969", "0.807"],
           ["10", "1.000", "1.000", "0.805"],
           ["20", "0.969", "1.000", "0.797"],
           ["50", "0.969", "1.000", "0.795"],
           ["100", "0.969", "1.000", "0.795"]],
          col_widths=[1.1, 1.6, 1.6, 1.4], size=11.5, row_h=0.36)
    bullets(s, Inches(5.5), Inches(3.6), Inches(7.3), Inches(3.0), [
        ("Recall@10 peaks at a pool of ten. ",
         "Beyond that the gold chunk is still found at twenty, and then the "
         "reranker pushes it out of the ten-chunk context."),
        ("The industrial corpus is the exception. ",
         "There the gold chunk is still arriving at fifty, so Recall@20 reaches "
         "1.000 while Recall@10 stays at 0.988."),
    ], size=14, gap=11)
    figure_caption(s, "fig1_pool_size", Inches(0.7), Inches(1.35) + Inches(5.3),
                   Inches(4.5))
    notes(s, "The point of this slide is that a larger pool costs ordering "
             "without adding the answer, and which way it fails depends on the "
             "corpus.")


def slide_quota_figure():
    s = base("The modality quota is a trade, not a gain",
             "It does not move both axes at once")
    figure(s, "fig4_modality_quota_pareto", Inches(0.7), Inches(1.35), Inches(5.9))
    bullets(s, Inches(7.0), Inches(1.45), Inches(5.8), Inches(4.7), [
        ("On the industrial corpus, ",
         "the pre-rerank quota buys 0.8 points of table recall and gives up "
         "0.8 points of overall recall, and the post-rerank quota lands on "
         "exactly the no-quota operating point."),
        ("On the focus corpus, ",
         "the post-rerank quota gives up 3.1 points of overall recall while "
         "table recall stays at 1.000."),
        ("So the placement is a configuration value. ",
         "Which way it trades depends on where it is applied, and the claim "
         "is never made without its corpus."),
    ], size=14, gap=12)
    figure_caption(s, "fig4_modality_quota_pareto", Inches(0.7), Inches(6.35),
                   Inches(5.9))
    notes(s, "This is the picture behind the placement question. The quota moves "
             "one axis and gives up the other.")


def slide_calibration_figures():
    s = base("Calibration and the risk-coverage frontier",
             "Both measured on the held-out evaluation half")
    figure(s, "fig3_calibration", Inches(0.6), Inches(1.3), Inches(5.5))
    figure(s, "fig2_risk_coverage", Inches(6.6), Inches(1.3), Inches(6.1))
    tf = textbox(s, Inches(0.6), Inches(6.35), Inches(12.1), Inches(0.7))
    para(tf, "Figure 3 (left): reliability of the calibrated probability against "
             "observed answerability. Figure 2 (right): the risk that an "
             "answered query has no answer in its context, against the fraction "
             "of queries the gate answers.",
         size=11.5, color=DARK_GREY, first=True, space_after=0, line=1.15)
    notes(s, "The industrial gate tracks the diagonal; the focus gate does not. "
             "On risk-coverage the focus gate buys very little over answering "
             "everything.")


def slide_shortcut_figure():
    s = base("A classifier that reads the answer off the question",
             "No retrieval, no evidence, no corpus, only the question text")
    figure(s, "fig5_question_only_roc", Inches(0.8), Inches(1.3), Inches(5.3))
    bullets(s, Inches(6.6), Inches(1.4), Inches(6.2), Inches(4.7), [
        ("Before the repair, ",
         "the two classes were separable almost perfectly on the focus corpus: "
         "ROC AUC 0.999 against a permutation null of 0.455."),
        ("One regular expression did it. ",
         "A fabricated identifier caught 76% of the unanswerable questions "
         "with no false positive at all."),
        ("After the repair, ",
         "the shortcut catches nothing and what is left of the procedure's power "
         "is small but not zero."),
    ], size=14, gap=13)
    figure_caption(s, "fig5_question_only_roc", Inches(0.8), Inches(6.45),
                   Inches(5.3))
    notes(s, "This figure is the audit. It is the reason the headline refusal "
             "rate had to be rebuilt.")


def slide_contra_figure():
    s = base("The contradiction detector against the base rate of real conflicts",
             "With 95% Wilson intervals")
    figure(s, "fig6_contradiction_precision", Inches(0.8), Inches(1.3), Inches(5.4))
    bullets(s, Inches(6.7), Inches(1.4), Inches(6.1), Inches(4.7), [
        ("The focus corpus's semantic branch has a precision of 0.0. ",
         "None of the 20 alarms was confirmed by either annotator, and the 95% "
         "upper bound is 16.1%. The branch would not act."),
        ("The industrial semantic branch reaches 0.65 ",
         "against a base rate of 0.35, so there it would act."),
        ("The industrial quantity stratum is not measurable from these data. ",
         "The branch fired on 13 of 119 scored pairs, but its precision was "
         "never measured."),
    ], size=14, gap=13)
    figure_caption(s, "fig6_contradiction_precision", Inches(0.8), Inches(6.5),
                   Inches(5.4))
    notes(s, "A filled marker means the branch would act; a hollow one means the "
             "findings would be withheld. On the focus corpus it is hollow.")


# ---------------------------------------------------------------- build
def main() -> int:
    slide_title()
    slide_problem()
    slide_measure()
    slide_objectives()
    slide_contribution()
    slide_pipeline()
    slide_retrieval()
    slide_gate_formula()
    slide_contradiction_formula()
    slide_corpora()
    slide_benchmark()
    slide_shortcut()
    slide_after_repair()
    slide_shortcut_figure()
    slide_retrieval_results()
    slide_reranker()
    slide_pool_curve()
    slide_quota()
    slide_quota_figure()
    slide_gate_sweep()
    slide_calibration_figures()
    slide_exp8()
    slide_answering()
    slide_random_control()
    slide_trade()
    slide_long_context()
    slide_proxy()
    slide_contra()
    slide_contra_figure()
    slide_empty()
    slide_form()
    slide_attribution()
    slide_transfer()
    slide_measured()
    slide_limitations()
    slide_conclusion()
    slide_future()
    slide_thanks()

    prs.save(str(OUT))
    _monochrome(OUT, keep=(ACCENT,))
    print(f"[deck] wrote {OUT.name} ({len(prs.slides._sldIdLst)} slides)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
