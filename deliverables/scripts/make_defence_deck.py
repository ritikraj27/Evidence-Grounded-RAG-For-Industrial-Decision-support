#!/usr/bin/env python3
"""Build the ten-minute defence deck.

A shorter, denser deck than `make_thesis_deck.py`. That one walks the report
section by section and runs to thirty-eight slides, which is a document to read
rather than a talk to give. This one is built to be spoken in ten minutes: it
holds every measured figure, every table and every formula from the report, and
it carries the speaker notes that go with them.

Two rules shape it.

Monochrome. Black for the structure, grey for emphasis, a light grey for panel
fills. The deck is projected in a room whose projector colour is not
guaranteed and printed on a mono printer, so no meaning may depend on a hue.
Hierarchy is carried by weight, size and darkness.

Every number comes from `substitute_tokens.values()`, which reads the archived
result files, so this deck cannot disagree with the report or with the other
deliverables.

Formulas are LaTeX, compiled to images with matplotlib's maths renderer and
placed on the slide as black-on-transparent PNGs, so they stay sharp at any
projection size and stay grey.

Usage:
    .venv/bin/python deliverables/scripts/make_defence_deck.py
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
OUT = ROOT / "deliverables" / "MTP_Defence_Deck.pptx"
FIGDIR = ROOT / "deliverables" / "figures"

sys.path.insert(0, str(Path(__file__).resolve().parent))
import substitute_tokens as _st

V = _st.values()

BLACK = RGBColor(0x00, 0x00, 0x00)
DARK = RGBColor(0x1A, 0x1A, 0x1A)
DARK_GREY = RGBColor(0x3A, 0x3A, 0x3A)
MID_GREY = RGBColor(0x6E, 0x6E, 0x6E)
MUTED = RGBColor(0x80, 0x80, 0x80)
PANEL = RGBColor(0xF4, 0xF4, 0xF6)
LIGHT = RGBColor(0xE2, 0xE2, 0xE6)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

#: The institute's own purple, the colour of the emblem. It is the deck's
#: single accent: the bar beside the title, the number in the footer, the
#: head of a table, the hero number on a slide, and the one band that
#: carries a verdict. Used this sparingly, it reads as a designed system;
#: used more widely it reads as decoration.
PURPLE = RGBColor(0x29, 0x19, 0x72)
#: The tint behind a card, a hair away from white.
PURPLE_TINT = RGBColor(0xF4, 0xF2, 0xF9)
#: Hairlines, which are structure rather than content.
RULE = RGBColor(0xD2, 0xD2, 0xD8)

FOOTER = ("MTP  |  Evidence-Grounded RAG for Industrial Decision Support  |  "
          "Ritik Raj 25IM60R12  |  IIT Kharagpur, ISE")

#: The deck is set in the same face as the report it defends.
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


def base(title, subtitle=None):
    """A content slide: accent bar, title, kicker, hairline, footer.

    The header used to be a full-width black band over a grey rule over a
    grey footer band, and every slide carried the same three horizontal
    stripes. It is now one accent bar, one hairline under the header and
    one hairline above the footer, so the type has room to breathe and the
    accent is the only thing on the slide that carries colour.
    """
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
    para(tf, value, size=vsize, bold=True, color=PURPLE, first=True, space_after=2,
         line=1.0)
    para(tf, label, size=lsize, color=DARK_GREY, space_after=0, line=1.12)


def band(slide, x, y, w, h, heading, body, *, size=17, bsize=12.5):
    """The one verdict of the slide, in the accent colour."""
    rect(slide, x, y, w, h, PURPLE)
    tf = textbox(slide, x + Inches(0.35), y + Inches(0.22), w - Inches(0.70),
                 h - Inches(0.40))
    para(tf, heading, size=size, bold=True, color=WHITE, first=True, space_after=7)
    para(tf, body, size=bsize, color=LIGHT, space_after=0, line=1.2)


def panel(slide, x, y, w, h, heading, body_items, *, size=17, bsize=12.5,
          hsize=None):
    """A tinted card with a purple edge, a heading and a list of paragraphs."""
    rect(slide, x, y, w, h, PURPLE_TINT)
    rect(slide, x, y, Inches(0.045), h, PURPLE)
    tf = textbox(slide, x + Inches(0.34), y + Inches(0.24), w - Inches(0.64),
                 h - Inches(0.44))
    para(tf, heading, size=hsize or size, bold=True, color=BLACK, first=True,
         space_after=9, line=1.1)
    for item in body_items:
        if isinstance(item, tuple):
            head, rest = item
            rich(tf, [(head, True, BLACK), (rest, False, DARK)], size=bsize,
                 space_after=8, line=1.2)
        else:
            para(tf, item, size=bsize, color=DARK, space_after=8, line=1.2)


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
    for it, so "9.3 x 10^-4" would arrive on the slide with a missing
    character in the middle of the number. The same number written out is the
    same number.
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
MC_A = t("MC_N_ANSWERABLE")
MC_U = t("MC_N_UNANSWERABLE")
TAU = t("TAU")
ECE = t("GATE_ECE")
BRIER = t("GATE_BRIER")
IND_ECE = t("IND_GATE_ECE")
PREC = t("FOCUS_GATE_ABST_PRECISION")
HARD = t("UNANS_HARD_REFUSED_PCT")
HARD_N = t("UNANS_HARD_REFUSED_N")
OOD_N = t("UNANS_OOD_REFUSED_N")
BEFORE_AUC = t("UNANS_BEFORE_AUC")
BEFORE_REF = t("UNANS_BEFORE_REFUSED_PCT")
#: Two different classifiers read only the question text, so their
#: before-and-after figures are two rows rather than one. The separability
#: row is the one the ROC figure on the same slide plots; the policy row is
#: a rule-based detector, and pairing its after-value with the
#: separability before-value would make one row describe two classifiers.
SEP_AFTER_AUC = t("UNANS_SEP_AUC")
POLICY_BEFORE_AUC = t("UNANS_POLICY_BEFORE_AUC")
POLICY_AFTER_AUC = t("UNANS_POLICY_AUC")
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
FORMVAL_CF = t("FORMVAL_COUNTERFACTUAL_RATE")
RERANK_FOCUS = t("RERANK_MRR_PP")
RERANK_MC = t("MC_MRR_RERANK_PP")
R_A = t("R_A")
R_B = t("R_B")
R_C = t("R_C")
R_D = t("R_D")
R_E = t("R_E")
R_F = t("R_F")
R_G = t("R_G")
MC_R_F = t("MC_R_F")
MC_R_G = t("MC_R_G")
POOL_PEAK = t("POOL_PEAK")
POOL_PEAK_R10 = t("POOL_PEAK_R10")
POOL10 = t("POOL10")
POOL100 = t("POOL100")
DISPLACEMENT = t("IND_POOL_DISPLACEMENT_PCT")
IND_R10_AT_50 = t("IND_POOL_R10_AT_50")
IND_R20_AT_50 = t("IND_POOL_R20_AT_50")
GCOMP_EMPTY = t("GENCOMP_2_EMPTY")
GCOMP_MODEL = t("GENCOMP_MODEL_2")
GCOMP_RESCUED = t("GENCOMP_FAILING_RESCUED")
GCOMP_STILL = t("GENCOMP_FAILING_STILL_EMPTY")
ENC = "BAAI/bge-m3"
RRF_K = t("RRF_K")
N_TESTS = t("N_TESTS")
SHARE_TEXT = t("FOCUS_SHARE_TEXT")
ERR_RETRIEVED = t("RO5_RETRIEVED_GROUNDED_ERROR")
ERR_GOLD = t("RO5_GOLD_GROUNDED_ERROR")
POS_DIR = t("RO5_POSITIONAL_DIRECTION_PHRASE")
AUDIT_PRE = t("AUDIT_PRE_REPAIR_SCREEN_N")
AUDIT_NOW = t("AUDIT_SCREEN_N")
AUDIT_CLEAN = t("AUDIT_CLEAN_N")
MC_DELTA_CD_MRR = t("MC_DELTA_CD_MRR")
MC_DELTA_CD_NDCG = t("MC_DELTA_CD_NDCG")
MC_P_CD_MRR = p_decimal(t("MC_P_CD_MRR"))
MC_P_CD_NDCG = p_decimal(t("MC_P_CD_NDCG"))
MC_DELTA_AC = t("MC_DELTA_AC")
MC_DELTA_AC_MRR = t("MC_DELTA_AC_MRR")
MC_P_AC_MRR = p_decimal(t("MC_P_AC_MRR"))
LC_ACC = t("GEN_A_LONGCTX_ANS_ACCURACY")
FIT_ACC = t("GEN_A_FITTED_ANS_ACCURACY")


# ---------------------------------------------------------------- figures
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


#: One-line captions. The full caption of each figure is in the report, where
#: there is room for it; a slide has two lines under a figure and a paragraph
#: there reads as a wall of text.
SLIDE_CAPTIONS = {
    "fig1_pool_size":
        "Recall against the size of the rerank candidate pool, focus corpus "
        "(black) and industrial corpus (grey).",
    "fig2_risk_coverage":
        "The risk that an answered query has no answer in its context, against "
        "the fraction of queries the gate answers.",
    "fig3_calibration":
        "Reliability of the calibrated probability against observed "
        "answerability, and the number of queries in each bin.",
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
    para(tf, SLIDE_CAPTIONS[key], size=size, color=DARK_GREY, first=True,
         space_after=0, line=1.15)
    return tf


# ---------------------------------------------------------------- slides
def slide_title():
    global _n
    _n += 1
    s = prs.slides.add_slide(BLANK)
    rect(s, 0, 0, SW, Inches(0.09), PURPLE)
    logo(s, 6.216, 0.40, 0.90)
    tf = textbox(s, Inches(1.0), Inches(1.50), Inches(11.3), Inches(2.4),
                 align=PP_ALIGN.CENTER)
    para(tf, "An Evidence-Grounded Retrieval-Augmented Generation Framework "
             "for Industrial Decision Support", size=34, bold=True, color=BLACK,
         first=True, space_after=14, align=PP_ALIGN.CENTER, line=1.10)
    para(tf, "Architecture, Evaluation Protocol, Failure Modes, and What the "
             "Measurements Show", size=17, italic=True, color=DARK_GREY,
         space_after=0, align=PP_ALIGN.CENTER)
    rect(s, Inches(5.42), Inches(4.18), Inches(2.5), Pt(2.0), PURPLE)
    tf = textbox(s, Inches(1.0), Inches(4.52), Inches(11.3), Inches(1.6),
                 align=PP_ALIGN.CENTER)
    para(tf, "Ritik Raj (25IM60R12)", size=17, bold=True, color=BLACK, first=True,
         space_after=5, align=PP_ALIGN.CENTER)
    para(tf, "Department of Industrial and Systems Engineering, IIT Kharagpur",
         size=12.5, color=DARK_GREY, space_after=3, align=PP_ALIGN.CENTER)
    para(tf, "Supervisor: Dr. Sri Krishna Kumar", size=12.5, color=DARK_GREY,
         space_after=16, align=PP_ALIGN.CENTER)
    notes(s, "Ten minutes. The question is narrow: when a retrieval-augmented "
             "generator is handed industrial text, can a gate in the code decide "
             "whether the retrieved evidence contains the answer, and what is "
             "that gate worth once it has been measured properly.")


def slide_problem():
    s = base("A wrong answer costs more than no answer",
             "Why industrial RAG is not the same problem as open-domain RAG")
    bullets(s, Inches(0.55), Inches(1.38), Inches(6.6), Inches(4.7), [
        ("The corpus is not a wiki. ",
         "It is a controlled set of documents somebody signed off on."),
        ("The questions are not curiosity. ",
         "They are operational decisions: is this tolerance acceptable, which "
         "procedure step applies, what does the specification require."),
        ("A refusal costs a supervisor five minutes. ",
         "A confidently fabricated tolerance costs a scrapped batch."),
    ], size=17, gap=20)
    rect(s, Inches(7.5), Inches(1.42), Inches(5.3), Inches(4.2), PANEL)
    tf = textbox(s, Inches(7.8), Inches(1.68), Inches(4.7), Inches(3.7))
    para(tf, "The question this report asks", size=17, bold=True, color=BLACK,
         first=True, space_after=13)
    para(tf, "When a RAG generator is given industrial text, can a gate in the "
             "code decide whether the retrieved evidence actually contains the "
             "answer?", size=17, color=DARK, space_after=13, line=1.24)
    para(tf, "And what is that gate worth, once it has been measured properly?",
         size=17, bold=True, color=BLACK, space_after=0, line=1.24)
    notes(s, "The asymmetry between a wrong answer and a non-answer is the whole "
             "reason a gate is worth building. Everything after this slide is "
             "about measuring that gate honestly.")


def slide_framework():
    s = base("The framework: five stages",
             "Two stages can refuse, and one of them runs before retrieval")
    stages = [
        ("0", "Query-form validation", "refuse", "costs no retrieval, no model call"),
        ("1", "Hybrid retrieval", "retrieve", "BM25 and bge-m3, fused by RRF"),
        ("2", "Rerank and quota", "rerank", "cross-encoder, modality floor"),
        ("3", "Confidence gate", "refuse", "the mechanism this report is about"),
        ("4", "Generation and claim assessment", "answer", "every claim scored against the evidence shown"),
    ]
    y = Inches(1.34)
    for i, (tag, name, kind, detail) in enumerate(stages):
        x = Inches(0.55 + i * 2.52)
        w = Inches(2.28)
        shade = PURPLE if kind == "refuse" else PANEL
        rect(s, x, y, w, Inches(1.62), shade)
        tf = textbox(s, x + Inches(0.13), y + Inches(0.10), w - Inches(0.26),
                     Inches(1.42))
        para(tf, f"Stage {tag}", size=11.5, bold=True,
             color=WHITE if kind == "refuse" else MID_GREY, first=True, space_after=3)
        para(tf, name, size=12.5, bold=True,
             color=WHITE if kind == "refuse" else BLACK, space_after=4, line=1.1)
        para(tf, detail, size=11.5,
             color=LIGHT if kind == "refuse" else DARK_GREY, space_after=0, line=1.1)
        if i < 4:
            tf = textbox(s, x + w, y + Inches(0.55), Inches(0.24), Inches(0.3),
                         align=PP_ALIGN.CENTER)
            para(tf, ">", size=17, bold=True, color=MID_GREY, first=True,
                 space_after=0, align=PP_ALIGN.CENTER)
    table(s, Inches(0.55), Inches(3.20), Inches(12.23),
          ["Stage", "Name", "Input", "Output", "May refuse?"],
          [["0", "Query-form validation", "raw query string",
            "query or refusal", "yes"],
           ["1", "Hybrid retrieval", "query", "candidate pool of chunks", "no"],
           ["2", "Rerank and quota", "candidate pool",
            "final context of 10 chunks", "no"],
           ["3", "Confidence gate", "final context", "accept or refuse", "yes"],
           ["4", "Generation and claim assessment", "accepted context",
            "annotated answer", "no"]],
          col_widths=[0.9, 3.3, 2.6, 3.6, 1.5], size=11.5, row_h=0.30)
    band(s, Inches(0.55), Inches(5.20), Inches(12.23), Inches(1.55),
         "The gate cannot be bypassed",
         "The generator is injected into the framework and called at exactly one "
         "line, after the gate has accepted. On a refusal the claim assessment and "
         "the contradiction detection are skipped too, so a refused query costs no "
         "model call at all. The only paths that skip the gate are the two "
         "comparison arms, rag_nogate and long_context.",
         size=17, bsize=12.5)
    notes(s, "Non-bypassability is a property of the code here, not a convention "
             "the caller is trusted to follow. Stage 0 runs before retrieval, so a "
             "malformed request costs nothing.")


def slide_retrieval_math():
    s = base("Retrieval: two legs, one fusion, one quota",
             "BM25, reciprocal rank fusion, and a floor on the non-text share")
    put_formula(s, r"$\mathrm{BM25}(q,d)=\sum_{t\in q}\mathrm{IDF}(t)\cdot"
                    r"\frac{f_{t,d}(k_1+1)}{f_{t,d}+k_1\left(1-b+b"
                    r"\frac{|d|}{\mathrm{avgdl}}\right)}$",
                Inches(0.55), Inches(1.36), Inches(5.9), fontsize=22)
    put_formula(s, r"$S_{RRF}(d)=\sum_{r\in\mathcal{R}}"
                    r"\frac{1}{k_{RRF}+\mathrm{rank}_r(d)},\;\; k_{RRF}=%s$" % RRF_K,
                Inches(6.9), Inches(1.40), Inches(5.9), fontsize=23)
    put_formula(s, r"$q_m=\min\left(n_m,\lceil \alpha_m\,|\mathcal{C}|\rceil\right),"
                    r"\;\; \alpha_{table}=0.15,\;\; \alpha_{chart}=0.05$",
                Inches(0.55), Inches(2.32), Inches(5.9), fontsize=23)
    bullets(s, Inches(0.55), Inches(3.00), Inches(5.9), Inches(2.45), [
        ("Lexical leg: ", "Okapi BM25 with k1 = 1.2 and b = 0.75."),
        ("Dense leg: ", f"{ENC}, 1024 dimensions, L2 normalised."),
        ("Fusion: ", "the top 20 of each leg, into a pool of 50."),
        ("Quota: ", "a floor on the non-text share, relaxed when the pool "
         "cannot supply it."),
        ("The archive keeps the earlier encoder's numbers, ",
         "so both sides of that comparison rest on measured values."),
    ], size=12.5, gap=7)
    panel(s, Inches(6.9), Inches(2.45), Inches(5.9), Inches(3.00),
          "Three invariants, asserted rather than assumed",
          ["A category pre-filter restricts both legs before fusion, the reranker "
           "only permutes its own pool, and the quota never leaves its pool.",
           "Each one is asserted directly, and three real defects were found that "
           "way, none of them visible in the output."],
          size=17, bsize=12.5)
    band(s, Inches(0.55), Inches(5.62), Inches(12.23), Inches(1.28),
         "Why the dense leg changed",
         "The earlier general purpose sentence encoder was measurably worse than "
         "plain BM25 on this corpus, so the fusion had been carrying a leg that "
         "lost information. It was replaced with BAAI/bge-m3.",
         size=17, bsize=12.5)
    notes(s, "Two things to point at. The quota is a floor on the non-text share, "
             "not a ceiling on text. And the encoder swap came out of a "
             "measurement, not a preference.")


def slide_gate_math():
    s = base("The confidence gate",
             "A calibrated posterior over the whole retrieved pool")
    put_formula(s, r"$\phi(q)=\left[s^{(1)}_{rerank},\; \bar{s}^{(3)}_{rerank},\; "
                    r"s^{(1)}_{bm25},\; \max_d S_{RRF}(d),\; \left|\{d\in"
                    r"\mathcal{C}: s_{rerank}(d)>\beta\}\right|\right]$",
                Inches(0.55), Inches(1.34), Inches(6.6), fontsize=20)
    put_formula(s, r"$p_{conf}(q)=\sigma\left(\beta_0+\boldsymbol{\beta}_1^{T}"
                    r"\frac{\phi(q)-\boldsymbol{\mu}}{\boldsymbol{\sigma}}\right),"
                    r"\quad \sigma(z)=\frac{1}{1+e^{-z}}$",
                Inches(7.45), Inches(1.40), Inches(5.4), fontsize=22)
    put_formula(s, r"$\mathrm{accept}(q)=\mathbb{1}\left[p_{conf}(q)\geq\tau"
                    r"\right]$",
                Inches(0.55), Inches(2.20), Inches(3.3), fontsize=24)
    bullets(s, Inches(4.3), Inches(2.18), Inches(8.5), Inches(2.0), [
        ("Five features: ", "top reranker score, mean of the top three, top BM25 "
         "score, maximum fused score, candidates above the reranker's bar."),
        ("Platt scaling: ", "weights fitted by maximum likelihood on a 60% "
         "calibration split of the queries."),
        ("Threshold: ", f"fitted at tau = {TAU} on the focus domain, chosen as the "
         "highest tau that still answers 90% of the answerable queries."),
    ], size=14, gap=7)
    panel(s, Inches(0.55), Inches(4.32), Inches(12.23), Inches(2.38),
          "Why the query level, not the chunk level",
          ["With one gold chunk among about fifty candidates, a chunk level "
           "classifier is right 98% of the time by answering nothing is "
           "relevant. Maximum likelihood fitting duly returns a large negative "
           "intercept, a degenerate solution that looks like a fitted model and "
           "behaves like a constant.",
           "Calibrating at the query level removes it. The gate's positive class "
           "is answer-in-context detectability, and it is defined operationally "
           "as the gold chunk being present in the reranked candidate pool."],
          size=17, bsize=12.5)
    notes(s, "If someone asks why the gate is not just a similarity threshold, "
             "this is the answer. The chunk level version has a trivial solution "
             "and the fit finds it.")


def slide_contradiction_and_form():
    s = base("The contradiction gate, and the form validator",
             "Two components that refuse, for two different reasons")
    put_formula(s, r"$\mathrm{contradiction}(c_1,c_2)=\mathbb{1}\left[\mathrm{NLI}"
                    r"(c_1,c_2)=\mathrm{contradiction}\right]\wedge\mathbb{1}"
                    r"\left[shared\ measurement\;\wedge\;shared\ instance\right]$",
                Inches(0.55), Inches(1.34), Inches(12.23), fontsize=24)
    panel(s, Inches(0.55), Inches(1.90), Inches(6.0), Inches(4.00),
          "The contradiction gate",
          [("Branch 1: ", "a natural language inference model at threshold 0.70."),
           ("Branch 2: ", "the two chunks must talk about the same measured "
            "quantity of the same instance."),
           ("Why both: ", "a quantity branch on its own fired on citation years, "
            "and a topical subject check on its own was a topic check rather than "
            "a contradiction check. Requiring both cut the alarms from 81 to 20."),
           ("What happens to those 20 alarms comes later on this deck.")],
          size=17, bsize=12.5)
    panel(s, Inches(6.78), Inches(1.90), Inches(6.0), Inches(4.00),
          "The form validator",
          [("An evidence gate, not a form gate. ", f"It accepted {FORM_PROBE} of "
            "the real malformed stems that were pushed through it, so it is never "
            "credited with the validator's work."),
           (f"The validator refused {FORMVAL_REJ} of {FORMVAL_TOT} hand authored "
            f"malformed queries and {FORMVAL_OK} of {FORMVAL_OKN} well formed "
            "ones, at 2.6 microseconds per query."),
           ("The counterfactual: ", f"reusing the benchmark builder's question "
            f"generation rule as a runtime check would have refused {FORMVAL_CF} "
            "of hand labelled well formed questions."),
           ("The lesson: ", "a filter written for one purpose does not fit "
            "another, and its false rejection rate has to be measured before it "
            "ships.")],
          size=17, bsize=12.5)
    notes(s, "The counterfactual is the memorable part. A rule that looked as if "
             "it did the job would have refused every well formed question in the "
             "set. This is also where the two refusal stages earn their keep, "
             "since they answer different questions.")


def slide_corpora():
    s = base("Three corpora, and a benchmark that had to be repaired",
             "Industrial engineering encyclopaedic text, with its provenance "
             "attached")
    table(s, Inches(0.55), Inches(1.34), Inches(12.23),
          ["Corpus", "Role", "Chunks", "Documents", "Queries"],
          [["Supply chain focus", "Ablation, gate, generation", SCOPE_SCM_CHUNKS,
            SCOPE_SCM_DOCS, CASE_Q],
           ["Six category industrial", "Transfer, long context cost", MC_CHUNKS,
            MC_DOCS, MC_QUERIES],
           ["Federal regulatory", "The contradiction detector's phenomenon",
            t("SCOPE_RE_CHUNKS"), t("SCOPE_RE_DOCS"), "none"]],
          col_widths=[2.6, 3.6, 1.1, 1.3, 1.1], size=11.5, row_h=0.36)
    panel(s, Inches(0.55), Inches(2.90), Inches(4.0), Inches(3.30),
          "Repair 1: the answer labels",
          [f"{AUDIT_PRE} of the answerable questions carried an answer label "
           "attached to the wrong question. Two defects in the label generation "
           "caused it.",
           f"After the repair the defect rate is {AUDIT_NOW} of {AUDIT_CLEAN}. The "
           "gold chunk was always right, so the retrieval side was never "
           "affected."],
          size=17, bsize=12.5)
    panel(s, Inches(4.72), Inches(2.90), Inches(4.0), Inches(3.30),
          "Repair 2: the unanswerable class",
          ["The unanswerable half was separable from the question text alone, so "
           "the headline refusal rate measured the benchmark rather than the "
           "framework.",
           "The class was rebuilt with corpus anchored definitions, and every "
           "repaired question was given a structural twin in the answerable "
           "class."],
          size=17, bsize=12.5)
    panel(s, Inches(8.89), Inches(2.90), Inches(3.89), Inches(3.30),
          "Repair 3: the form check",
          [f"The runtime validator refused 3 of {CASE_Q} benchmark queries, all "
           "of them generator artefacts that read as malformed rather than real "
           "questions.",
           "The audit instrument was kept rather than deleted, because it is the "
           "instrument that found the defects."],
          size=17, bsize=12.5)
    notes(s, "The focus corpus carries 32 answerable and 144 unanswerable "
             "questions. The cross category corpus carries 132 and 144. The two "
             "never mix, because they are used for different experiments. Be "
             "honest about the public substitute: the primary corpus of "
             "proprietary supply chain documents cannot be redistributed.")


def slide_metrics():
    s = base("Metrics, tests, and the rule that every comparison is paired",
             "Every rate has a stated denominator")
    put_formula(s, r"$\mathrm{Recall}@k=\frac{|R_k\cap G|}{|G|},\quad "
                    r"\mathrm{MRR}=\frac{1}{|Q|}\sum_{q\in Q}\frac{1}"
                    r"{\mathrm{rank}_q},\quad \mathrm{nDCG}@k=\frac"
                    r"{\mathrm{DCG}@k}{\mathrm{IDCG}@k}$",
                Inches(0.55), Inches(1.32), Inches(12.23), fontsize=22)
    put_formula(s, r"$r_{ans}(U)=\frac{|\{q\in U:\mathrm{answered}(q)\}|}{|U|},"
                    r"\quad \mathrm{Prec}_{ref}=\frac{|\mathrm{refused}\cap U|}"
                    r"{|\mathrm{refused}|}$",
                Inches(0.55), Inches(2.75), Inches(7.0), fontsize=22)
    put_formula(s, r"$\mathrm{DCG}@k=\sum_{i=1}^{k}\frac{\mathrm{rel}_i}"
                    r"{\log_2(i+1)}$",
                Inches(8.0), Inches(2.68), Inches(3.8), fontsize=22)
    bullets(s, Inches(0.55), Inches(4.15), Inches(12.2), Inches(2.75), [
        ("Retrieval comparisons: ", "paired over the same queries and tested with "
         "the Wilcoxon signed rank test, with Cliff's delta and Cohen's dz as "
         "effect sizes."),
        ("Generation comparisons: ", "paired over the same questions and tested "
         "with the exact McNemar test. b counts the questions the baseline "
         "answered and the arm refused, c counts the other way round."),
        ("One test per class. ", "A gate's effect on the unanswerable class and "
         "its effect on the answerable class are separate tests with separate "
         "hypotheses, because a gate can improve the first and damage the "
         "second."),
        ("Proportions carry Wilson score intervals, and a null is read as no "
         "difference established here."),
        ("One generator, five arms, one of which refuses the same number of "
         "questions at random. ", "Without that arm, refusing on a coin flip and "
         "refusing on a calibrated score look identical."),
    ], size=12.5, gap=9)
    notes(s, "Two protocol decisions do real work. Every comparison is paired, "
             "because the arms answer the same questions. And the paired test is "
             "applied per class, because one number for both would hide the "
             "trade.")


def slide_retrieval_results():
    s = base("Retrieval: seven configurations on the focus corpus",
             "Paired Wilcoxon signed rank test on every comparison")
    table(s, Inches(0.55), Inches(1.34), Inches(12.23),
          ["System", "Recall@10", "MRR", "nDCG@10", "Table recall"],
          [["A. bm25_only", R_A, t("MRR_A"), t("NDCG_A"), "1.000"],
           ["B. dense_only", R_B, t("MRR_B"), t("NDCG_B"), "0.875"],
           ["C. hybrid_rrf", R_C, t("MRR_C"), t("NDCG_C"), "1.000"],
           ["D. +rerank", R_D, t("MRR_D"), t("NDCG_D"), "1.000"],
           ["E. +category_filter", R_E, t("MRR_E"), t("NDCG_E"), "1.000"],
           ["F. +quota_pre_rerank", R_F, t("MRR_F"), t("NDCG_F"), "1.000"],
           ["G. +quota_post_rerank", R_G, t("MRR_G"), t("NDCG_G"), "1.000"]],
          col_widths=[3.2, 1.6, 1.4, 1.6, 1.7], size=11.5, row_h=0.33)
    bullets(s, Inches(0.55), Inches(4.05), Inches(6.1), Inches(2.50), [
        ("The dense leg is significantly worse than BM25. ",
         f"{R_A} to {R_B}, a paired difference of -0.156 at p = 0.025. That is why "
         "the encoder was replaced."),
        ("Fusion recovers the loss. ",
         f"{R_C} against {R_B}, a paired improvement of +0.188 at p = 0.014, and it "
         "improves the ordering as well."),
        ("The claim for fusion is narrow. ",
         "It stopped being a loss. It did not become a significant win over plain "
         "BM25 on its own."),
    ], size=12.5, gap=8)
    table(s, Inches(7.05), Inches(4.10), Inches(5.73),
          ["Comparison", "Delta MRR", "p (MRR)"],
          [["A to C, BM25 to fusion", MC_DELTA_AC_MRR, MC_P_AC_MRR],
           ["C to D, fusion to rerank", MC_DELTA_CD_MRR, MC_P_CD_MRR]],
          col_widths=[3.2, 1.4, 1.4], size=11.5, row_h=0.34)
    tf = textbox(s, Inches(7.05), Inches(5.20), Inches(5.73), Inches(1.0))
    para(tf, "Cross category transfer, six category corpus. The reranker's gain "
             "survives the change of corpus, while the fusion's recall advantage "
             "over BM25 does not.",
         size=11.5, color=DARK_GREY, first=True, space_after=0, line=1.18)
    notes(s, "The encoder swap is the thing to point at. A fusion carrying a leg "
             "that lost information is worse than no fusion at all. And the "
             "transfer table is the reason the reranker sentence always travels "
             "with its corpus: -0.3 points on the focus corpus against +11.1 "
             "points on the six category corpus.")


def slide_quota():
    s = base("The modality quota is a trade, not a gain",
             "It does not move both axes at once")
    figure(s, "fig4_modality_quota_pareto", Inches(0.7), Inches(1.32), Inches(5.5))
    table(s, Inches(6.55), Inches(1.34), Inches(6.23),
          ["Corpus", "Quota before the reranker", "Quota after the reranker", "p"],
          [["Supply chain focus", t("QUOTA_PRE_FOCUS_R10"),
            t("QUOTA_POST_FOCUS_R10"), t("QUOTA_PLACE_FOCUS_P")],
           ["Six category industrial", t("QUOTA_PRE_SIXCAT_R10"),
            t("QUOTA_POST_SIXCAT_R10"), t("QUOTA_PLACE_SIXCAT_P")],
           ["Industrial", t("QUOTA_PRE_IND_R10"), t("QUOTA_POST_IND_R10"),
            t("QUOTA_PLACE_IND_P")]],
          col_widths=[2.2, 2.1, 2.1, 0.9], size=11.5, row_h=0.42)
    bullets(s, Inches(6.55), Inches(3.30), Inches(6.23), Inches(2.3), [
        ("On the industrial corpus, ", "the pre rerank quota buys 0.8 points of "
         "table recall and gives up 0.8 points of overall recall, and the post "
         "rerank quota lands on exactly the no quota operating point."),
        ("On the focus corpus, ", "the post rerank quota gives up 3.1 points of "
         "overall recall while table recall stays at 1.000."),
        ("None of the three differences is significant. ", "So the placement is a "
         "configuration value, and the ranking is reported with its corpus "
         "attached."),
    ], size=12.5, gap=8)
    figure_caption(s, "fig4_modality_quota_pareto", Inches(0.7), Inches(6.10),
                   Inches(5.5))
    notes(s, "This is the picture behind the placement question. The quota moves "
             "one axis and gives up the other. A claim that the quota belonged "
             "before the cross encoder would not hold on every corpus.")


def slide_pool():
    s = base("More candidates are not monotonically better",
             "The candidate pool curve peaks and then declines")
    figure(s, "fig1_pool_size", Inches(0.7), Inches(1.32), Inches(4.1))
    table(s, Inches(5.15), Inches(1.34), Inches(7.63),
          ["Pool", "Recall@10", "Recall@20", "MRR"],
          [["5", "0.969", "0.969", "0.807"],
           ["10", "1.000", "1.000", "0.805"],
           ["20", "0.969", "1.000", "0.797"],
           ["50", "0.969", "1.000", "0.795"],
           ["100", "0.969", "1.000", "0.795"]],
          col_widths=[1.2, 1.8, 1.8, 1.5], size=11.5, row_h=0.36)
    bullets(s, Inches(5.15), Inches(3.72), Inches(7.63), Inches(2.1), [
        ("On the focus corpus ", f"Recall@10 peaks at {POOL_PEAK_R10} with a pool of "
         f"{POOL_PEAK} and falls back to 0.969 at twenty, fifty and a hundred."),
        ("What is happening is visible at twenty. ", "Recall@20 keeps rising as "
         "the pool grows, so the gold chunk is still being found and then the "
         "reranker pushes it out of the ten chunk context."),
        (f"The industrial corpus is the exception. ", f"There Recall@20 reaches "
         f"{IND_R20_AT_50} at a pool of fifty while Recall@10 stays at "
         f"{IND_R10_AT_50}, so {DISPLACEMENT} of gold is retrieved and then pushed "
         "out."),
    ], size=12.5, gap=8)
    figure_caption(s, "fig1_pool_size", Inches(0.7), Inches(6.10), Inches(4.1))
    notes(s, "A larger pool costs ordering without adding the answer, and which "
             "way it fails depends on the corpus. The focus curve saturates at "
             "ten. The industrial curve does not, and that is the exception that "
             "makes the point.")


def slide_calibration():
    s = base("The gate is calibrated, and it is not excellent",
             "Both measured on the held out evaluation half")
    figure(s, "fig3_calibration", Inches(0.65), Inches(1.32), Inches(4.5))
    table(s, Inches(5.55), Inches(1.34), Inches(3.3),
          ["Metric", "Value"],
          [["Expected calibration error", ECE],
           ["Brier score", BRIER],
           ["Base rate of answer in context", "0.182"],
           ["Retriever recall of gold", "1.000"]],
          col_widths=[2.3, 1.0], size=11.5, row_h=0.40)
    put_formula(s, r"$\mathrm{ECE}=\sum_{b=1}^{B}\frac{|B_b|}{N}"
                    r"\left|\mathrm{acc}(B_b)-\bar{p}(B_b)\right|$",
                Inches(9.15), Inches(1.40), Inches(3.6), fontsize=17)
    put_formula(s, r"$\mathrm{Brier}=\frac{1}{N}\sum_{i=1}^{N}(p_i-y_i)^2$",
                Inches(9.15), Inches(2.30), Inches(3.0), fontsize=17)
    bullets(s, Inches(5.55), Inches(3.50), Inches(7.2), Inches(1.6), [
        (f"The gate is fitted on a 60% calibration split of {CASE_Q} queries, and "
         f"its positive class has a base rate of 0.182.", ""),
        ("The industrial gate tracks the diagonal ", f"at ECE {IND_ECE}. The focus "
         "gate does not, and it puts most of its queries in the lowest confidence "
         "bin."),
        ("An ECE of " + ECE + " is reported rather than improved by refitting. ", ""),
    ], size=12.5, gap=8)
    tf = textbox(s, Inches(0.65), Inches(6.05), Inches(12.1), Inches(0.75))
    para(tf, "Figure 3. Reliability of the gate's calibrated probability against "
             "observed answerability on the held out evaluation half (focus n = "
             "71, industrial n = 178). The upper panel plots observed "
             "answerability against mean predicted probability per bin, and the "
             "lower panel the number of queries in each bin.",
         size=11.5, color=DARK_GREY, first=True, space_after=0, line=1.15)
    notes(s, "Say the ECE out loud and do not defend it. It is the calibration of "
             "one fitted artefact on one fixed split, and it is reported because "
             "a reader would otherwise have to assume it is better than it is.")


def slide_sweep():
    s = base("The operating point, and the frontier it sits on",
             "The threshold is chosen by a stated rule, and the sweep is shown in "
             "full")
    table(s, Inches(0.55), Inches(1.34), Inches(7.1),
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
    figure(s, "fig2_risk_coverage", Inches(8.05), Inches(1.32), Inches(4.7))
    bullets(s, Inches(0.55), Inches(4.35), Inches(7.1), Inches(1.8), [
        ("The rule: ", f"the highest tau that still answers at least 90% of the "
         f"answerable queries, which gives tau = {TAU}."),
        ("The gate is precise where it refuses. ", f"At the fitted operating point "
         f"the abstention precision is {PREC}, so almost every refusal lands on a "
         "question that should have been refused."),
        ("The frontier is real. ", "Every extra refusal is paid for in coverage, "
         "and the price climbs steeply past tau = 0.15."),
    ], size=12.5, gap=8)
    tf = textbox(s, Inches(8.05), Inches(5.75), Inches(4.7), Inches(0.9))
    para(tf, "Figure 4. Risk coverage of the confidence gate, the risk that an "
             "answered query has no answer in its context against the fraction of "
             "queries the gate answers.",
         size=11.5, color=DARK_GREY, first=True, space_after=0, line=1.15)
    notes(s, "Point at the abstention precision column. That is the number a "
             "practitioner actually needs. And the sweep is shown in full because "
             "a single threshold hides the shape of the frontier.")


def slide_shortcut():
    s = base("The benchmark answered itself",
             "A classifier could read the answer off the question text alone")
    figure(s, "fig5_question_only_roc", Inches(0.75), Inches(1.32), Inches(4.4))
    table(s, Inches(5.55), Inches(1.34), Inches(7.23),
          ["Quantity", "Before the repair", "After the repair"],
          [["Question-shape separability (ROC AUC)", BEFORE_AUC, SEP_AFTER_AUC],
           ["Question-only policy (ROC AUC)", POLICY_BEFORE_AUC, POLICY_AFTER_AUC],
           ["Identifier shortcut detection", SC_BEFORE, SC_AFTER],
           ["Gate refusal rate on the class", BEFORE_REF, HARD]],
          col_widths=[3.4, 1.8, 1.8], size=11.5, row_h=0.38)
    bullets(s, Inches(5.55), Inches(3.28), Inches(7.23), Inches(2.3), [
        ("The hard family named a fabricated identifier. ", "No answerable question "
         "carried an identifier of that shape, so one regular expression caught "
         "the whole family."),
        ("So the headline refusal rate was an upper bound rather than a "
         "measurement, ", "and the rate that was measured measured the benchmark "
         "rather than the framework."),
        (f"After the repair the gate refuses {HARD_N} of the corpus anchored hard "
         f"stratum and {OOD_N} of the out of domain stratum.", ""),
    ], size=12.5, gap=8)
    figure_caption(s, "fig5_question_only_roc", Inches(0.75), Inches(6.10),
                   Inches(4.4))
    notes(s, "The gap between the two strata is the finding. What the gate "
             "detects is a recognisable unanswerable question, one drawn from "
             "outside the corpus or one whose subject is plainly absent. It is "
             "much weaker on the on topic but unanswered case. Say it slowly, this "
             "is the slide that changes the headline.")


def slide_arms():
    s = base("One generator, five arms, two prompt conditions",
             "The prompt condition is an experimental axis, not a fixed setting")
    table(s, Inches(0.55), Inches(1.34), Inches(7.2),
          ["Arm", "What it removes"],
          [["rag_nogate", "the gate, keeping retrieval"],
           ["rag@fitted", "nothing, the framework at its fitted operating point"],
           ["rag@random", "the confidence score, keeping the refusal budget"],
           ["rag@transferred", "the fitted operating point, threshold moved across "
            "corpora"],
           ["long_context", "retrieval, the whole corpus in the prompt"]],
          col_widths=[2.4, 4.8], size=11.5, row_h=0.36)
    put_formula(s, r"$p=2\sum_{k=0}^{\min(b,c)}\binom{n}{k}\left(\frac{1}{2}"
                    r"\right)^{n}$",
                Inches(8.3), Inches(1.44), Inches(3.6), fontsize=21)
    tf = textbox(s, Inches(8.3), Inches(2.88), Inches(4.48), Inches(1.9))
    para(tf, "The two prompt conditions differ by a single sentence. Under one the "
             "generator may decline, and under the other it must answer. Model, "
             "questions, retrieval, scorer and temperature stay identical either "
             "way.",
         size=12.5, color=DARK, first=True, space_after=0, line=1.2)
    table(s, Inches(0.55), Inches(3.58), Inches(12.23),
          ["Generator", "No text returned", "On the table lookup family",
           "Rescued by a 4x budget", "Still empty"],
          [[t("GENCOMP_MODEL_1"), t("GENCOMP_1_EMPTY"), t("GENCOMP_1_EMPTY_TABLE"),
            t("GENCOMP_1_RESCUED"), t("GENCOMP_1_STILL_EMPTY")],
           [GCOMP_MODEL, GCOMP_EMPTY, t("GENCOMP_2_EMPTY_TABLE"),
            GCOMP_RESCUED, GCOMP_STILL]],
          col_widths=[2.6, 2.3, 2.9, 2.4, 1.7], size=11.5, row_h=0.40)
    bullets(s, Inches(0.55), Inches(5.02), Inches(12.2), Inches(1.6), [
        (f"The replication on a second generator could not be run. ", f"{GCOMP_MODEL} "
         f"returned no text on {GCOMP_EMPTY} questions, and raising the output "
         f"budget fourfold rescued {GCOMP_RESCUED} and left {GCOMP_STILL} empty."),
        ("An empty completion is neither an answer nor a refusal. ", "A run like "
         "that is recorded as not run, with the reason, because a rate quoted from "
         "a run that did not happen is indistinguishable from a rate that did."),
    ], size=12.5, gap=8)
    notes(s, "The empty completion table is the reason the hypothesis is claimed "
             "for one generator rather than in general. It is also an argument for "
             "the gate sitting upstream of generation, since a generator that "
             "cannot answer costs nothing on the questions the gate rejects.")


def slide_verdict():
    s = base("The verdict under the answering condition",
             "The generator cannot decline on its own here, so the gate cannot be "
             "redundant")
    table(s, Inches(0.55), Inches(1.34), Inches(12.23),
          ["Arm", "Unanswerable answered", "Answerable answered",
           "Paired McNemar, unanswerable", "Paired McNemar, answerable"],
          [["rag_nogate", f"{t('GEN_A_NOGATE_UNANS_ANSWERED')} ({GEN_NOGATE_U})",
            GEN_NOGATE_A, "none", "none"],
           ["rag@fitted", f"{t('GEN_A_FITTED_UNANS_ANSWERED')} ({GEN_FITTED_U})",
            GEN_FITTED_A, "b = 60, c = 1, p < 0.001", "b = 2, c = 0, p = 0.500"],
           ["rag@random", f"{t('GEN_A_RANDOM_UNANS_ANSWERED')} ({GEN_RANDOM_U})",
            GEN_RANDOM_A, "none", "b = 11, p = 0.001"],
           ["rag@transferred", f"{t('GEN_A_XFER_UNANS_ANSWERED')} ({GEN_XFER_U})",
            GEN_XFER_A, "none", "none"],
           ["long_context", f"{t('GEN_A_LONGCTX_UNANS_ANSWERED')} ({GEN_LC_U})",
            GEN_LC_A, "p = 1.00", "p = 1.00"]],
          col_widths=[2.2, 3.1, 2.4, 3.2, 2.7], size=11.5, row_h=0.40)
    band(s, Inches(0.55), Inches(3.92), Inches(12.23), Inches(1.72),
         f"Verdict: {H2}",
         "Under the cautious prompt the rate falls from 0.535 to 0.417, at the cost "
         "of the same two answerable questions. The paired test is significant "
         "under both conditions, and the two condition design matters: under the "
         "cautious prompt alone the generator refused most unanswerable questions "
         "on its own, the gate's refusals were largely redundant, and the arms "
         "could not have been told apart.",
         size=17, bsize=12.5)
    bullets(s, Inches(0.55), Inches(5.76), Inches(12.2), Inches(1.1), [
        ("The transferred arm over refuses badly. ", f"It answers {GEN_XFER_A} "
         "answerable questions, because the threshold was fitted on one half of "
         "the cross category corpus and applied unchanged to the other half."),
    ], size=12.5, gap=6)
    notes(s, "This is the slide the whole talk is built around. The paired test on "
             "the unanswerable class is the headline, and the cost in coverage is "
             "stated on the same slide. Do not linger on the transferred arm here, "
             "it comes back at the end.")


def slide_score_buys():
    s = base("What the confidence score buys, and what it costs",
             "This is the finding most likely to be reported wrongly")
    table(s, Inches(0.55), Inches(1.34), Inches(12.23),
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
          col_widths=[2.3, 2.0, 2.2, 2.8, 2.6], size=11.5, row_h=0.40)
    kpi(s, Inches(0.85), Inches(3.42), Inches(5.4), Inches(1.42),
        FIT_B, f"answerable questions refused by the gate (p = {FIT_P})", vsize=30)
    kpi(s, Inches(6.95), Inches(3.42), Inches(5.4), Inches(1.42),
        RND_B, f"answerable questions refused by the random control (p = {RND_P})",
        vsize=30)
    bullets(s, Inches(0.55), Inches(5.08), Inches(12.2), Inches(1.6), [
        ("It does not buy a lower answer rate on unanswerable questions. ",
         f"The random control reaches {GEN_RANDOM_U}, worse than the fitted gate's "
         f"{GEN_FITTED_U} and far below the ungated arm's {GEN_NOGATE_U}, because "
         "most questions in a benchmark are unanswerable and refusing at random "
         "is already a large improvement over never refusing."),
        (f"What the score buys is where the refusals land. ", f"The gate removes "
         f"{TRADE_WRONG} wrong answers and costs {TRADE_COST} correct answer under "
         "the entailment test, and its refusals concentrate on the class that "
         "should be refused. That is a precision claim."),
    ], size=12.5, gap=7)
    notes(s, "If a report said the gate answers fewer unanswerable questions, it "
             "would be true and it would be misleading. The claim is about "
             "precision, and the control is what makes it visible. Also do not let "
             "the per answer accuracy numbers be read as a quality win. The gated "
             "arm answers an easier subset, which is the selection effect.")


def slide_long_context():
    s = base("Long context against the pipeline",
             "Measured on cost and on coverage, and it does not win")
    kpi(s, Inches(0.55), Inches(1.40), Inches(3.9), Inches(1.40),
        f"{LC_RATIO}x", "input tokens per query, against the pipeline", vsize=30)
    kpi(s, Inches(4.75), Inches(1.40), Inches(3.9), Inches(1.40),
        f"{LC_COST}x", "input cost per query, at the provider's cached pricing",
        vsize=30)
    kpi(s, Inches(8.95), Inches(1.40), Inches(3.83), Inches(1.40),
        LC_CACHE, "of the long context tokens are cache reads", vsize=30)
    bullets(s, Inches(0.55), Inches(2.98), Inches(6.1), Inches(2.4), [
        ("Cost: ", f"the focus corpus is {LC_TOK} tokens against the pipeline's "
         f"accepted context of {RAG_TOK} tokens."),
        ("Coverage: ", f"the whole corpus prompt answered {GEN_LC_A} answerable "
         "questions, the same as the ungated pipeline."),
        ("Quality: ", f"accuracy {LC_ACC} against {FIT_ACC} for the gated arm, and "
         "the margin is not significant under a length controlled re scoring of "
         "the same answers."),
    ], size=12.5, gap=8)
    panel(s, Inches(6.95), Inches(2.98), Inches(5.83), Inches(3.80),
          "The retrieval side proxy",
          [f"With the candidate set widened to every chunk, the gold chunk lands "
           f"in the top 10 for {LC_PROXY} of the focus queries and {MC_PROXY} of "
           f"the cross category queries, at a median rank of {LC_RANK}.",
           f"The evidence is not lost in a large context; the tail is where corpus "
           f"size bites, and a retriever that finds the answer at median rank 1 "
           f"has no use for the other {SCOPE_SCM_CHUNKS} chunks.",
           f"The cross category corpus is {MC_LC_TOK} tokens, {MC_LC_FACTOR} times "
           "the 128K window, so the quality half of that comparison could not be "
           "run there and it is settled on coverage and cost alone."],
          size=17, bsize=12.5)
    notes(s, "The cost ratio is the point. The token ratio on its own is off by an "
             "order of magnitude, because most of the long context arm's tokens "
             "are cache reads at a fifth of the base rate. A token ratio must "
             "never carry an argument about money.")


def slide_contra_result():
    s = base("The contradiction gate: a precision of zero",
             "Measured against reader labels, not against a proxy the detector "
             "defines")
    figure(s, "fig6_contradiction_precision", Inches(0.75), Inches(1.32), Inches(4.5))
    table(s, Inches(5.65), Inches(1.34), Inches(7.13),
          ["Quantity", "Value"],
          [["Labelled alarms", CONTRA_N],
           ["Confirmed as contradictions", "0"],
           ["Precision against reader labels", CONTRA],
           ["95% upper bound on the true precision", CONTRA_CI],
           ["Annotator agreement on the decision",
            f"{CONTRA_PAIRS} of {CONTRA_PAIRS}"],
           ["Annotator disagreement", "0"]],
          col_widths=[4.6, 2.0], size=11.5, row_h=0.38)
    bullets(s, Inches(5.65), Inches(4.20), Inches(7.13), Inches(1.90), [
        ("None of the raised alarms was confirmed. ", f"Two annotators that do "
         f"not share a model, both blind to the detector's scores and both "
         f"{CONTRA_CTRL} correct on a control set with known labels, still "
         "confirmed nothing."),
        ("The readers also found no contradictions in a random sample of 80 pairs "
         "the gate did not flag, ", "so this corpus holds concept level prose "
         "rather than instance records and does not contain the phenomenon the "
         "mechanism detects."),
    ], size=12.5, gap=8)
    figure_caption(s, "fig6_contradiction_precision", Inches(0.75), Inches(6.10),
                   Inches(4.5))
    notes(s, "Report this as a null with a stated upper bound, not as a defect to "
             "be explained away. The two detector defects the audit exposed were "
             "real and were fixed, and they were not the reason the alarms went "
             "unconfirmed. The mechanism is unproven rather than disproven.")


def slide_attribution():
    s = base("Most unattributed error comes from the evidence, not the scorer",
             "The same answers scored against two evidence sets")
    table(s, Inches(0.55), Inches(1.34), Inches(7.5),
          ["Error measure", "Over the retrieved evidence", "Over the gold evidence"],
          [["Grounded claims, error rate", ERR_RETRIEVED, ERR_GOLD],
           ["Inferred claims, error rate", t("RO5_RETRIEVED_INFERRED_ERROR"),
            t("RO5_GOLD_INFERRED_ERROR")],
           ["Uncertain claims, error rate", t("RO5_RETRIEVED_UNCERTAIN_ERROR"),
            t("RO5_GOLD_UNCERTAIN_ERROR")],
           ["Reference hallucination rate",
            t("RO5_RETRIEVED_REFERENCE_HALLUCINATION"),
            t("RO5_GOLD_REFERENCE_HALLUCINATION")],
           ["Answer position effect, p", t("RO5_RETRIEVED_POSITION_P"),
            t("RO5_GOLD_POSITION_P")]],
          col_widths=[3.4, 2.2, 2.0], size=11.5, row_h=0.38)
    panel(s, Inches(8.35), Inches(1.34), Inches(4.43), Inches(3.05),
          "How a claim is scored",
          ["A claim counts as supported when a chunk entails it at threshold 0.5, "
           "or when the evidence states it literally.",
           "0.80 separates a grounded claim from 0.45 for an inferred one. "
           "Anything below is uncertain.",
           "The gold chunk is never force added, so nothing outside the evidence "
           "can support a claim."],
          size=17, bsize=12.5)
    band(s, Inches(0.55), Inches(4.50), Inches(12.23), Inches(1.45),
         "Most of the error is a retrieval problem",
         f"The grounded claim error rate is {ERR_RETRIEVED} over the evidence the "
         f"arm was shown and {ERR_GOLD} over the gold chunk, so most of what the "
         "framework's own attribution cannot explain comes from the evidence it "
         "was given. Meanwhile the answer position effect holds in three of the "
         "four measurements and ties in the fourth.",
         size=17, bsize=12.5)
    notes(s, "The gold chunk was always right, so this is a clean comparison. The "
             "same answers, two evidence sets, and the gap between the columns is "
             "large.")


def slide_findings():
    s = base("What the measurements establish",
             "Fourteen findings, each with the number that carries it")
    rows = [
        ["F1", "Dense leg worse than BM25 on focus, fusion recovers it",
         "0.969 vs 0.812 vs 1.000"],
        ["F2", "The reranker's value depends on the corpus",
         "-0.3 pp focus, 11.1 pp six category"],
        ["F3", "Quota placement has no universally better answer",
         "p = 0.157, 0.480, 0.317"],
        ["F4", "The candidate pool curve peaks and then declines",
         "pool of 10 on the focus corpus"],
        ["F5", "The gate is precise where it refuses",
         "abstention precision 0.963"],
        ["F6", "The gate finds a recognisable unanswerable question",
         "23.6% hard stratum, 26 of 34 out of domain"],
        ["F7", "The hypothesis holds under both prompt conditions",
         "McNemar p < 0.001 and p = 0.009"],
        ["F8", "The score buys refusal precision, not a lower answer rate",
         "b = 2 against b = 11"],
        ["F9", "The gate is an evidence gate, not a form gate",
         "76.7% of malformed stems accepted"],
        ["F10", "The contradiction gate's precision against readers is zero",
         "20 alarms, upper bound 16.1%"],
        ["F11", "Long context costs 74x the tokens and 58.8x the money",
         "202,529 against 2,246 tokens"],
        ["F12", "A calibrated threshold does not transfer across corpora",
         "6 of 32 answerable answered"],
        ["F13", "Most unattributed error comes from the evidence",
         "0.118 against 0.542"],
        ["F14", "An empty completion is a third outcome",
         "24 of 66 questions"],
    ]
    table(s, Inches(0.55), Inches(1.30), Inches(12.23),
          ["#", "Finding", "Evidence"], rows,
          col_widths=[0.6, 7.4, 4.3], size=11.5, row_h=0.31, head_h=0.30)
    tf = textbox(s, Inches(0.55), Inches(6.05), Inches(12.2), Inches(0.7))
    para(tf, "Every row is a measurement against an archived result file. The "
             "three that qualify the verdict are F8, F10 and F12, and they are the "
             "three worth reading twice.",
         size=11.5, color=DARK_GREY, first=True, space_after=0, line=1.18)
    notes(s, "Leave this slide up while you talk through the three qualifying "
             "findings. It is the slide an examiner will photograph.")


def slide_limitations():
    s = base("Limitations", "Eight, and two of them are the ones that matter")
    items = [
        ("L1", "One generator. The hypothesis is supported for the generator "
               "tested, not in general. This is the largest gap."),
        ("L2", "An encyclopaedic corpus, not procedural documentation. The "
               "contradiction detector's phenomenon is measurably absent from it."),
        ("L3", "The long context quality half was measured on one corpus only."),
        ("L4", "The annotation behind the contradiction precision is model based, "
               "not human."),
        ("L5", "Statistical power. Several nulls are nulls of this corpus at this "
               "size, and they are reported with their interval widths."),
        ("L6", "The hallucination rate on generated text is a different quantity "
               "from the refusal rate, and the two are never substituted for one "
               "another."),
        ("L7", "A refusal is not an answer. Per answer accuracy cannot be compared "
               "across arms with different coverage."),
        ("L8", "English, and one jurisdiction. Nothing here shows the findings "
               "hold for another language or another regulator."),
    ]
    y = 1.34
    for tag, body in items:
        rect(s, Inches(0.55), Inches(y), Inches(0.62), Inches(0.60), BLACK)
        tf = textbox(s, Inches(0.55), Inches(y + 0.16), Inches(0.62), Inches(0.30),
                     align=PP_ALIGN.CENTER)
        para(tf, tag, size=11.5, bold=True, color=WHITE, first=True, space_after=0,
             align=PP_ALIGN.CENTER)
        tf = textbox(s, Inches(1.38), Inches(y + 0.06), Inches(11.4), Inches(0.58))
        para(tf, body, size=12.5, color=DARK, first=True, space_after=0, line=1.15)
        y += 0.68
    notes(s, "Do not rush this slide. L1 and L2 are the two that get raised, and "
             "they were already flagged in the text rather than waiting to be "
             "found in the questions.")


def slide_next():
    s = base("What comes next, and a closing note",
             "The next steps are in the order that would change what the report can "
             "claim")
    items = [
        ("1", "Repeat the generator side comparison on a generator that returns "
              "text on the table questions.",
         "One generator settles the hypothesis for one model."),
        ("2", "Compare the gate against a token level faithfulness monitor.",
         "The gate is currently measured against a prompt level control only."),
        ("3", "Settle the magnitude and the power of the positional comparison.",
         "The direction holds in three of the four measurements, and not in the "
         "magnitude."),
        ("4", "Hand check the repaired unanswerable class against the corpus, on "
              "both corpora.", ""),
        ("5", "Replace the model based contradiction annotators with human "
              "readers.", "Which would strengthen the 0.0% finding in either "
              "direction."),
        ("6", "Publish the corrected benchmark and the shortcut audit as a "
              "separate artefact.",
         "So other work on RAG refusal can check its own benchmarks against the "
         "same instrument."),
    ]
    y = 1.28
    for tag, head, detail in items:
        rect(s, Inches(0.55), Inches(y), Inches(0.42), Inches(0.42), BLACK)
        tf = textbox(s, Inches(0.55), Inches(y + 0.08), Inches(0.42), Inches(0.26),
                     align=PP_ALIGN.CENTER)
        para(tf, tag, size=11.5, bold=True, color=WHITE, first=True, space_after=0,
             align=PP_ALIGN.CENTER)
        tf = textbox(s, Inches(1.18), Inches(y + 0.02), Inches(11.6), Inches(0.62))
        para(tf, head, size=12.5, bold=True, color=BLACK, first=True, space_after=2,
             line=1.12)
        if detail:
            para(tf, detail, size=11.5, color=DARK_GREY, space_after=0, line=1.1)
        y += 0.68
    band(s, Inches(0.55), Inches(5.44), Inches(12.23), Inches(1.46),
         "The most useful thing this produced was not the framework",
         "It was finding that two of its own instruments were reporting numbers a "
         "careful reader could not trust, and changing the headline rather than "
         "explaining it away. A framework's contribution is only as good as the "
         "instruments that measured it.",
         size=17, bsize=12.5)
    notes(s, "End on the instruments, not on the architecture. Point at item 1 and "
             "item 6. The replication is the gap that matters for the claim, and "
             "the published benchmark is the part that outlives the report.")


def slide_thanks():
    global _n
    _n += 1
    s = prs.slides.add_slide(BLANK)
    rect(s, 0, 0, SW, Inches(0.09), PURPLE)
    logo(s, 6.216, 1.05, 0.90)
    tf = textbox(s, Inches(1.0), Inches(2.25), Inches(11.3), Inches(2.6),
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
    rect(s, Inches(5.42), Inches(5.10), Inches(2.5), Pt(2.0), PURPLE)
    notes(s, "The report has the full appendix-free text, the eight works that "
             "were actually used, and the numbers behind every row of the findings "
             "table.")


# ---------------------------------------------------------------- build
def main() -> int:
    slide_title()
    slide_problem()
    slide_framework()
    slide_retrieval_math()
    slide_gate_math()
    slide_contradiction_and_form()
    slide_corpora()
    slide_metrics()
    slide_retrieval_results()
    slide_quota()
    slide_pool()
    slide_calibration()
    slide_sweep()
    slide_shortcut()
    slide_arms()
    slide_verdict()
    slide_score_buys()
    slide_long_context()
    slide_contra_result()
    slide_attribution()
    slide_findings()
    slide_limitations()
    slide_next()
    slide_thanks()

    prs.save(str(OUT))
    _monochrome(OUT, keep=(ACCENT,))
    print(f"[defence deck] wrote {OUT.name} "
          f"({len(prs.slides._sldIdLst)} slides)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
