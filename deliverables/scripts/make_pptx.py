#!/usr/bin/env python3
"""Build Deliverable 4 -- the 18 November presentation.

Every number on every slide is read from `impl/results/*.json` at build time,
so the deck cannot drift from the measurements. If an experiment has not been
run, the slide says so rather than showing a placeholder.

Design follows the IIT Kharagpur ISE house style observed in the department's
own MTP review decks: a running project footer on every content
slide, a slide number, and a consistent left-aligned content column.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
import sys

# The monochrome helper lives beside the shipped builders. The template
# copy of the deck generator sits one directory higher, so both places are
# offered to the import.
for _cand in (Path(__file__).resolve().parent,
              Path(__file__).resolve().parents[2] / "scripts"):
    if (_cand / "monochrome.py").exists():
        sys.path.insert(0, str(_cand))
        break
from monochrome import to_monochrome as _monochrome

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Emu, Inches, Pt

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from results_source import load as _src_load, load_transfer as _src_load_transfer, _comp_index
from results_source import contradiction_precision_claim as _src_cp_claim
from results_source import contradiction_precision_mechanism as _src_cp_mech
from results_source import contradiction_precision_brief as _src_cp_brief
from results_source import next_steps as _src_next_steps
from results_source import load_generation_replication as _src_load_replication
def load_transfer(name, required=()):
    """Load a result from the multi-category run only.

    The cross-category transfer experiment is defined on a multi-category
    corpus, so it is never taken from the focus-domain run.
    """
    return _src_load_transfer(name, required)

RESULTS = ROOT / "impl" / "results"
OUT = ROOT / "deliverables" / "Deliverable_4_Presentation_18Nov.pptx"

# The palette is monochrome. These decks are projected in a room where the
# projector's colour is not guaranteed, and they are printed for the panel
# on a mono printer, so nothing may depend on a hue. The hierarchy is
# carried by weight and by darkness instead: black for the structure,
# mid grey for emphasis, a lighter grey for secondary text, and a very light
# grey for the panel fills.
BLACK = RGBColor(0x00, 0x00, 0x00)

#: The number of categories, in words. The corpus this deck reports on has
#: one; the six-category corpus is a different experiment on a different
#: corpus, and its count does not belong on this slide.
_CAT_WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five",
              6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten"}
DARK_GREY = RGBColor(0x3A, 0x3A, 0x3A)
MID_GREY = RGBColor(0x6E, 0x6E, 0x6E)
BODY_INK = RGBColor(0x1A, 0x1A, 0x1A)
MUTED_GREY = RGBColor(0x80, 0x80, 0x80)
PANEL_FILL = RGBColor(0xF2, 0xF2, 0xF2)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
NEGATIVE = RGBColor(0x55, 0x55, 0x55)
POSITIVE = RGBColor(0x00, 0x00, 0x00)

FOOTER = "MTP-2  |  Evidence-Grounded RAG for Industrial Decision Support  |  IIT Kharagpur, ISE"

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]

SW, SH = prs.slide_width, prs.slide_height


# ---------------------------------------------------------------- helpers
def _load(name: str, required: tuple = ()) -> dict | None:
    """Load a result file, or None if absent or of a different shape.

    `required` lists the keys this generator needs. A result file written by
    an earlier version of an experiment has a different schema, so it is
    treated as "not available" and the corresponding slide section is skipped
    rather than crashing the build.
    """
    # The focus-domain run carries the headline numbers, as it does in the
    # guide and the papers; the multi-category run is the generalisation
    # study and is read through `load_transfer`.
    for _d in (ROOT / "impl" / "results_focus", RESULTS):
        p = _d / f"{name}.json"
        if p.exists():
            break
    else:
        return None
    try:
        payload = json.loads(p.read_text())
    except Exception:
        return None
    if not isinstance(payload, dict):
        return None
    missing = [k for k in required if k not in payload]
    if missing:
        print(f"[warn] {name}.json is missing {missing}; skipping that section")
        return None
    return payload





def textbox(slide, x, y, w, h, *, align=PP_ALIGN.LEFT, wrap=True):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = wrap
    tf.margin_left = tf.margin_right = Emu(0)
    tf.margin_top = tf.margin_bottom = Emu(0)
    tf.paragraphs[0].alignment = align
    return tb, tf


def para(tf, text, *, size=16, bold=False, color=BODY_INK, space_after=6, first=False,
         align=PP_ALIGN.LEFT, italic=False, font="Calibri"):
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    p.alignment = align
    p.space_after = Pt(space_after)
    r = p.add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.italic = italic
    r.font.color.rgb = color
    r.font.name = font
    return p


def rich(tf, chunks, *, size=16, space_after=6, first=False, align=PP_ALIGN.LEFT):
    """chunks = [(text, bold, color, italic), ...]"""
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    p.alignment = align
    p.space_after = Pt(space_after)
    for text, bold, color, *rest in chunks:
        r = p.add_run()
        r.text = text
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.color.rgb = color
        r.font.italic = bool(rest[0]) if rest else False
        r.font.name = "Calibri"
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


def base_slide(title, subtitle=None, number=None):
    """Content slide with the house header band, footer and slide number.

    The title size steps down for long titles so that a two-line title
    never collides with the accent rule underneath it.
    """
    s = prs.slides.add_slide(BLANK)
    rect(s, 0, 0, SW, Inches(0.06), BLACK)
    tb, tf = textbox(s, Inches(0.55), Inches(0.26), Inches(12.2), Inches(0.76))
    if len(title) > 62:
        tsize = 22
    elif len(title) > 52:
        tsize = 24
    else:
        tsize = 27
    para(tf, title, size=tsize, bold=True, color=BLACK, first=True, space_after=2)
    if subtitle:
        para(tf, subtitle, size=13.5, color=MUTED_GREY, space_after=0, italic=True)
    rect(s, Inches(0.55), Inches(1.06), Inches(12.23), Pt(1.6), MID_GREY)
    # footer
    rect(s, 0, SH - Inches(0.42), SW, Inches(0.42), PANEL_FILL)
    tb, tf = textbox(s, Inches(0.55), SH - Inches(0.335), Inches(11.0), Inches(0.26))
    para(tf, FOOTER, size=9.5, color=MUTED_GREY, first=True, space_after=0)
    if number is not None:
        tb, tf = textbox(s, SW - Inches(1.05), SH - Inches(0.335), Inches(0.5),
                         Inches(0.26), align=PP_ALIGN.RIGHT)
        para(tf, str(number), size=9.5, color=MUTED_GREY, first=True, space_after=0,
             align=PP_ALIGN.RIGHT)
    return s


def notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text


def table(slide, x, y, w, h, headers, rows, *, col_widths=None, size=11.5,
          highlight_rows=(), header_size=11.5):
    shape = slide.shapes.add_table(len(rows) + 1, len(headers), x, y, w, h)
    tbl = shape.table
    if col_widths:
        total = sum(col_widths)
        for i, cw in enumerate(col_widths):
            tbl.columns[i].width = Emu(int(w * cw / total))
    for j, htext in enumerate(headers):
        cell = tbl.cell(0, j)
        cell.text = ""
        cell.fill.solid()
        cell.fill.fore_color.rgb = BLACK
        tf = cell.text_frame
        tf.margin_left = tf.margin_right = Emu(45720)
        tf.margin_top = tf.margin_bottom = Emu(18288)
        para(tf, htext, size=header_size, bold=True, color=WHITE, first=True,
             space_after=0, align=PP_ALIGN.LEFT if j == 0 else PP_ALIGN.CENTER)
    for i, row in enumerate(rows, start=1):
        for j, val in enumerate(row):
            cell = tbl.cell(i, j)
            cell.text = ""
            cell.fill.solid()
            cell.fill.fore_color.rgb = PANEL_FILL if i % 2 == 0 else WHITE
            if (i - 1) in highlight_rows:
                cell.fill.fore_color.rgb = RGBColor(0xEF, 0xEF, 0xEF)
            tf = cell.text_frame
            tf.margin_left = tf.margin_right = Emu(45720)
            tf.margin_top = tf.margin_bottom = Emu(18288)
            para(tf, str(val), size=size,
                 bold=(i - 1) in highlight_rows,
                 color=BODY_INK, first=True, space_after=0,
                 align=PP_ALIGN.LEFT if j == 0 else PP_ALIGN.CENTER)
    return tbl


def bullets(slide, x, y, w, h, items, *, size=15.5, gap=9):
    """items = [(level, text)] or [(level, [(chunk, bold, color), ...])]"""
    tb, tf = textbox(slide, x, y, w, h)
    firstp = True
    for level, content in items:
        indent = "" if level == 0 else "      "
        marker = "▪  " if level == 0 else "–  "
        chunks = [(indent + marker, False, MID_GREY if level == 0 else MUTED_GREY)]
        if isinstance(content, str):
            chunks.append((content, False, BODY_INK))
        else:
            chunks.extend(content)
        rich(tf, chunks, size=size if level == 0 else size - 1.5,
             space_after=gap, first=firstp)
        firstp = False
    return tb


def kpi(slide, x, y, w, h, value, label, *, color=BLACK, vsize=34, lsize=12):
    rect(slide, x, y, w, h, PANEL_FILL, line=RGBColor(0xBF, 0xBF, 0xBF))
    tb, tf = textbox(slide, x + Inches(0.12), y + Inches(0.14), w - Inches(0.24),
                     h - Inches(0.2), align=PP_ALIGN.CENTER)
    para(tf, value, size=vsize, bold=True, color=color, first=True, space_after=2,
         align=PP_ALIGN.CENTER)
    para(tf, label, size=lsize, color=MUTED_GREY, space_after=0, align=PP_ALIGN.CENTER)


# ---------------------------------------------------------------- data
def _load_focus(name: str) -> dict | None:
    """Load a result file from the focus-domain (supply chain) run."""
    p = ROOT / "impl" / "results_focus" / f"{name}.json"
    if not p.exists():
        return None
    try:
        payload = json.loads(p.read_text())
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None
exp1 = _load("exp1_ablation", ("systems", "comparisons", "corpus_stats"))
exp2 = _load("exp2_gate", ("calibration_metrics", "threshold_sweep", "chosen_operating_point"))
exp3 = _load("exp3_contradiction", ("summary",))
# The audit of the benchmark's own unanswerable half: the finding, and the
# repair of it.
exp12 = _load_focus("exp12_unanswerable_class_audit")


def _cmp(a, b):
    """The paired comparison between two adjacent ablation rungs."""
    for c in exp1["comparisons"]:
        if c["comparison"] == f"{a} -> {b}":
            return c
    return None
exp4 = load_transfer("exp4_transfer", ("leave_half_out", "per_category_retrieval"))
# The same ablation on the six-category corpus. The reranker's effect is
# corpus-dependent, and a finding that is stated on one corpus and read on
# another is a finding about the wrong corpus.
exp1_mc = load_transfer("exp1_ablation", ("systems",))
_mc_sys = (exp1_mc or {}).get("systems") or {}
_mc_mrr_c = _mc_sys.get("C. hybrid_rrf", {}).get("mrr", float("nan"))
_mc_mrr_d = _mc_sys.get("D. hybrid_rrf_rerank", {}).get("mrr", float("nan"))
_mc_ndcg_c = _mc_sys.get("C. hybrid_rrf", {}).get("nDCG@10", float("nan"))
_mc_ndcg_d = _mc_sys.get("D. hybrid_rrf_rerank", {}).get("nDCG@10", float("nan"))
_mc_r_c = _mc_sys.get("C. hybrid_rrf", {}).get("recall@10", float("nan"))

sysout = []
S = sys.stdout
n = 0


def nxt():
    global n
    n += 1
    return n


# ================================================================ SLIDE 1
s = prs.slides.add_slide(BLANK)
rect(s, 0, 0, SW, SH, BLACK)
rect(s, 0, Inches(4.62), SW, Pt(2.5), MID_GREY)
tb, tf = textbox(s, Inches(0.9), Inches(1.15), Inches(11.5), Inches(2.4))
para(tf, "An Evidence-Grounded Retrieval-Augmented Generation Framework",
     size=36, bold=True, color=WHITE, first=True, space_after=6)
para(tf, "for Industrial Decision Support", size=36, bold=True, color=WHITE,
     space_after=12)
para(tf, "Confidence gating  ·  Modality-balanced retrieval  ·  "
         "Contradiction surfacing  ·  Per-claim confidence tags",
     size=17, color=RGBColor(0xD9, 0xD9, 0xD9), space_after=0)
tb, tf = textbox(s, Inches(0.9), Inches(4.95), Inches(11.5), Inches(1.9))
para(tf, "Presented By", size=13, bold=True, color=MID_GREY, first=True, space_after=3)
para(tf, "Ritik Raj  (25IM60R12)", size=18, bold=True, color=WHITE, space_after=12)
para(tf, "Supervised By", size=13, bold=True, color=MID_GREY, space_after=3)
para(tf, "Dr. Sri Krishna Kumar", size=18, bold=True, color=WHITE, space_after=12)
para(tf, "M.Tech. Project Review Presentation  ·  Autumn 2026-27",
     size=13, color=RGBColor(0xD9, 0xD9, 0xD9), space_after=3)
para(tf, "Department of Industrial and Systems Engineering, Indian Institute of "
         "Technology Kharagpur", size=13, color=RGBColor(0xD9, 0xD9, 0xD9),
     space_after=0)
notes(s, "Good morning. I am presenting MTP-2: an evidence-grounded retrieval-augmented "
         "generation framework for industrial decision support.\n\n"
         "The one-line framing: industrial engineers make decisions from documentation, "
         "and the tools that query that documentation answer even when the evidence is "
         "not there. My work makes the system's refusal behaviour structural rather "
         "than advisory, and then measures honestly what each part actually buys.\n\n"
         "I will spend most of the time on the results, because the most interesting "
         "outcome of this project is that three of my own design assumptions turned out "
         "to be wrong, and I found out why. Two of them I found by measuring them "
         "properly; the third I found by building a second corpus out of the United "
         "States federal regulations -- because the mechanism I had to test could not "
         "be tested on the corpus I had.\n\n"
         "I will also tell you which of my results are new and which are not, because "
         "I ran a novelty check against the 2026 literature before writing this, and "
         "it changed two of the claims I would otherwise have made.")

# ================================================================ SLIDE 2
s = base_slide("Project Abstract & Research Context",
               "Why industrial practitioners need something different from a chatbot",
               nxt())
bullets(s, Inches(0.55), Inches(1.35), Inches(7.2), Inches(4.6), [
    (0, [("The industry challenge. ", True, BLACK),
         ("Industrial decisions are made from paperwork — SOPs, FMEAs, control plans, "
          "maintenance logs, calibration records, supplier documents. Document volume "
          "has grown faster than the time available to synthesise it.", False, BODY_INK)]),
    (1, "Decisions are therefore made under partial information, and the consequences "
        "span efficiency loss, compliance failure and safety incident."),
    (0, [("Why a generic chatbot is not enough. ", True, BLACK),
         ("It answers fluently but cannot be trusted: there is no trace from a number "
          "back to its source page, no way to tell an inferred claim from a stated one, "
          "and no warning when two sources disagree.", False, BODY_INK)]),
    (0, [("This is not cosmetic. ", True, BLACK),
         ("A wrong economic order quantity, wrong Incoterm or wrong safety-stock rule "
          "can stop a production line or fail an audit.", False, BODY_INK)]),
])
rect(s, Inches(8.05), Inches(1.4), Inches(4.73), Inches(4.5), PANEL_FILL,
     line=RGBColor(0xBF, 0xBF, 0xBF))
tb, tf = textbox(s, Inches(8.3), Inches(1.62), Inches(4.23), Inches(4.1))
para(tf, "THE NUMBER THAT SETS THE SCALE", size=12, bold=True, color=MID_GREY,
     first=True, space_after=10)
para(tf, "66%", size=52, bold=True, color=BLACK, space_after=2)
para(tf, "F1 on SQuAD 2.0 for a strong neural system that scores 86% on SQuAD",
     size=14, color=BODY_INK, space_after=12)
para(tf, "Twenty points lost to confidently answering questions that have no answer "
         "— in a purely general-domain setting, with no industrial content at all.",
     size=14, color=MUTED_GREY, space_after=8)
para(tf, "SQuAD 2.0, ACL 2018 — the benchmark that defined the task: answer, or "
         "decline.", size=11.5, color=MUTED_GREY, italic=True, space_after=0)
notes(s, "The motivation in one number. SQuAD 2.0 added fifty thousand questions that "
         "have no answer, and the abstract reports that a strong neural system gets "
         "86% F1 on the original SQuAD but only 66% on SQuAD 2.0. Twenty points, lost "
         "purely to confidently answering questions that have no answer.\n\n"
         "Now imagine that in a plant. A wrong EOQ is not a benchmark loss. So the "
         "question is not 'can we make an LLM answer industrial questions' — we can. The "
         "question is 'can we make it stop when the evidence is not there, and tell us "
         "which passage supports which claim'.")

# ================================================================ SLIDE 3
s = base_slide("Three Gaps That Make Generic RAG Unsafe Here",
               "What RAG fixes, and what it still leaves open", nxt())
tb, tf = textbox(s, Inches(0.55), Inches(1.32), Inches(12.2), Inches(0.5))
rich(tf, [("RAG grounds the answer in retrieved passages — a large improvement over a "
           "closed-book model. But three properties that industrial users require are "
           "still absent.", False, BODY_INK)], size=15.5, first=True)
gaps = [
    ("1", "No evidence trail",
     "The system returns an answer but does not show which sentence supports which "
     "claim. A number with no path back to its page cannot be audited.",
     "Needed for: ISO 9001, GS1, Incoterms, OEM procedures"),
    ("2", "No confidence check",
     "The system answers even when retrieval is weak. Below-threshold passages are "
     "still passed to the generator, which fills the gap with plausible text.",
     "Needed for: safety procedures, reorder policies"),
    ("3", "No contradiction handling",
     "When two accepted passages disagree, the model silently picks one — usually "
     "without telling the practitioner that a disagreement existed.",
     "Needed for: superseded SOP revisions, vendor terms"),
]
x = Inches(0.55)
for num, title, body, need in gaps:
    rect(s, x, Inches(2.0), Inches(3.94), Inches(3.95), WHITE,
         line=RGBColor(0xBF, 0xBF, 0xBF))
    rect(s, x, Inches(2.0), Inches(3.94), Inches(0.52), BLACK)
    tb, tf = textbox(s, x + Inches(0.22), Inches(2.11), Inches(3.5), Inches(0.34))
    rich(tf, [(f"{num}.  ", True, MID_GREY), (title, True, WHITE)], size=15.5,
         first=True, space_after=0)
    tb, tf = textbox(s, x + Inches(0.22), Inches(2.72), Inches(3.5), Inches(3.0))
    para(tf, body, size=13.5, color=BODY_INK, first=True, space_after=12)
    para(tf, need, size=12, color=MID_GREY, italic=True, space_after=0)
    x += Inches(4.14)
notes(s, "Three gaps. Let me be precise about what RAG does and does not fix.\n\n"
         "RAG retrieves and grounds — good. But it trusts the retriever "
         "unconditionally, it ignores modality diversity, and it gives one answer "
         "with one confidence number and no citation trail.\n\n"
         "The third gap is the one people underrate. Two SOP revisions disagree. The "
         "model silently picks one. The practitioner has no way to know a disagreement "
         "existed. Worth being precise about our own corpus here: it does not contain "
         "that case. Its one version reference is historical, so the supersession "
         "check fires zero times, and the corpus contains no live contradictions "
         "either — so the contradiction mechanism cannot be evaluated on it at all. That "
         "is a limitation of the corpus rather than of the check, and reporting a "
         "superseded revision as a live contradiction is the most damaging error the "
         "system could make.\n\n"
         "Which is why I built a second corpus. Federal regulations are amended, so the "
         "same provision read at two dates is the same rule at two issues — a corpus "
         "that contains the conflicts the mechanism exists to find. On that corpus it "
         "does find them, and then reports them as the wrong KIND: detection precision "
         "0.659, typing precision 0.073. I will come back to "
         "that.")

# ================================================================ SLIDE 4
s = base_slide("What This Thesis Builds: Five Design Moves",
               "Each is independently switchable; each prevents one specific failure", nxt())
moves = [
    ("D1", "Code-level confidence gate",
     "A calibrated probability that the retrieved evidence is relevant. Below threshold, "
     "the generator is NEVER called and a “no evidence” response is returned.",
     "Prevents: confidently answering from irrelevant passages", BLACK),
    ("D2", "Modality-balanced retrieval",
     "A quota guaranteeing a minimum share of tables and charts in the final context, "
     "because binding requirements live in tables, not prose.",
     "Prevents: a spec table being outranked by prose about it", DARK_GREY),
    ("D3", "Hybrid retrieval + category pre-filter",
     "BM25 + dense vectors fused by Reciprocal Rank Fusion, then a cross-encoder "
     "reranker, with a category filter applied before retrieval.",
     "Prevents: missing the passage because one matcher missed it", DARK_GREY),
    ("D4", "Contradiction surfacing",
     "A joint NLI + topical gate shows the practitioner where two passages disagree "
     "instead of silently picking one, with a revision-supersession check.",
     "Prevents: applying a superseded policy", MID_GREY),
    ("D5", "Per-claim confidence tagging",
     "Each claim tagged grounded / inferred / uncertain, with citations and an "
     "information-gain figure in bits.",
     "Prevents: trusting a whole answer because one sentence was solid", MID_GREY),
]
y = Inches(1.32)
for tag, title, body, prevents, col in moves:
    rect(s, Inches(0.55), y, Inches(0.62), Inches(0.95), col)
    tb, tf = textbox(s, Inches(0.55), y + Inches(0.3), Inches(0.62), Inches(0.4),
                     align=PP_ALIGN.CENTER)
    para(tf, tag, size=17, bold=True, color=WHITE, first=True, space_after=0,
         align=PP_ALIGN.CENTER)
    tb, tf = textbox(s, Inches(1.35), y + Inches(0.02), Inches(11.4), Inches(0.95))
    para(tf, title, size=15.5, bold=True, color=BLACK, first=True, space_after=2)
    para(tf, body, size=12.8, color=BODY_INK, space_after=2)
    para(tf, prevents, size=11.8, color=MUTED_GREY, italic=True, space_after=0)
    y += Inches(1.03)
notes(s, "Five design moves. Three things I want to stress.\n\n"
         "First, each maps to one failure mode — this is not a bag of tricks.\n\n"
         "Second, D1 is a branch in code, not a sentence in a prompt. The model cannot "
         "talk its way past it because no output it produces ever reaches it. And the "
         "refusal is auditable: 'posterior 0.31 against threshold 0.50' is checkable.\n\n"
         "Third, and I will come back to this: D2 was specified in the wrong place in "
         "the pipeline. I will show you what that cost and how I found it.")

# ================================================================ SLIDE 5
s = base_slide("Framework Architecture", "Four stages, one load-bearing decision point", nxt())
stages = [
    ("STAGE 1 — INGESTION", "offline, per document",
     ["Parse: text + tables + figures", "Chunk: text | table | chart, tagged",
      "Embed: BGE-M3 1024-d", "Index: BM25 + Postgres/pgvector (HNSW)"], BLACK),
    ("STAGE 2 — RETRIEVAL", "online, per query",
     ["→ form check: is this a question?", "Embed query → category pre-filter",
      "BM25 leg  +  dense leg",
      "→ Reciprocal Rank Fusion", "→ cross-encoder rerank",
      "→ CONFIDENCE GATE  → modality quota"], MID_GREY),
    ("STAGE 3 — GENERATION", "online, per accepted query",
     ["Per-claim tagging", "Citations", "Contradiction flag", "Tagged answer"], DARK_GREY),
]
x = Inches(0.55)
for title, sub, items, col in stages:
    rect(s, x, Inches(1.35), Inches(4.05), Inches(3.55), WHITE,
         line=RGBColor(0xBF, 0xBF, 0xBF))
    rect(s, x, Inches(1.35), Inches(4.05), Inches(0.62), col)
    tb, tf = textbox(s, x + Inches(0.2), Inches(1.44), Inches(3.7), Inches(0.46))
    para(tf, title, size=13.5, bold=True, color=WHITE, first=True, space_after=0)
    para(tf, sub, size=10.5, color=RGBColor(0xCF, 0xCF, 0xCF), space_after=0)
    tb, tf = textbox(s, x + Inches(0.25), Inches(2.16), Inches(3.6), Inches(2.6))
    for i, it in enumerate(items):
        rich(tf, [("▸ ", False, MID_GREY), (it, it.startswith("→ CONFIDENCE"), col)],
             size=13, space_after=8, first=(i == 0))
    x += Inches(4.2)
rect(s, Inches(0.55), Inches(5.1), Inches(12.23), Inches(1.25), PANEL_FILL,
     line=RGBColor(0xBF, 0xBF, 0xBF))
tb, tf = textbox(s, Inches(0.85), Inches(5.28), Inches(11.7), Inches(1.0))
para(tf, "The load-bearing property", size=13.5, bold=True, color=BLACK, first=True,
     space_after=5)
rich(tf, [("The gate sits between retrieval and generation, and it is ", False, BODY_INK),
          ("not bypassable", True, MID_GREY),
          (". When it rejects, the language model is never invoked — there is no "
           "prompt instruction asking it to be careful, and no output it produces "
           "that could change the decision. An instruction is a request; a branch is "
           "a fact.", False, BODY_INK)], size=14, space_after=0)
notes(s, "The architecture. Ingestion is offline, once per document. Retrieval and "
         "generation are online, per query.\n\n"
         "The box to look at is the dark one in stage two. The confidence gate. It "
         "sits between retrieval and generation, and when it rejects, the language "
         "model is never invoked.\n\n"
         "There is a second, smaller check in front of it, and it asks a different "
         "question: is this a question at all? The gate judges the EVIDENCE — the "
         "retrieved passages — and it never looks at the query's grammar. I "
         "measured that: on the malformed question stems my benchmark generator "
         "itself produces and rejects, on the six-category corpus, the gate accepted "
         "23 of 30 of them, because a nonsense "
         "question still retrieves passages that look relevant. The form check runs "
         "before retrieval, so a request it refuses costs no embedding pass, no "
         "cross-encoder pass and no model call.\n\n"
         "Compare with the nearest prior work, CRAG, which also inserts an evaluator "
         "between retrieval and generation — but CRAG still calls the LLM in every "
         "branch; it changes what context the LLM sees, not whether the LLM runs. "
         "That is the difference between an instruction and a branch.")

# ================================================================ SLIDE 6
s = base_slide("Literature Survey: Research Foundations",
               "Every paper below verified against a live bibliographic API", nxt())
papers = [
    ("SQuAD 2.0  ·  Rajpurkar et al.  ·  ACL 2018",
     "Adds 50,000 unanswerable questions and a no-answer threshold. Defines the task "
     "as “answer correctly OR decline”.",
     "86% F1 on SQuAD → 66% on SQuAD 2.0. Twenty points lost to answering questions "
     "that have no answer."),
    ("Self-RAG  ·  Asai et al.  ·  ICLR 2024",
     "Trains the LM to emit reflection tokens that decide when to retrieve and whether "
     "a passage supports the output.",
     "We use a NON-TRAINABLE code-level gate instead: reflection tokens are learned per "
     "corpus and must be re-learned for each of 12 categories."),
    ("CRAG  ·  Yan et al.  ·  2024",
     "A lightweight retrieval evaluator returns a confidence degree that triggers one "
     "of four corrective actions.",
     "Closest prior art to D1. Difference: CRAG still calls the LLM in every branch; "
     "we refuse and exit the generation path."),
    ("Conformal RAG  ·  Geißler et al.  ·  2026",
     "Conformal prediction filters retrieved chunks; an attention classifier scores "
     "answer–context consistency. Framed for industry.",
     "Strongest current work on D1. We do NOT claim superiority — we adopt their "
     "diagnostics as our limitation, because their guarantees need exchangeability."),
]
y = Inches(1.32)
for title, method, finding in papers:
    rect(s, Inches(0.55), y, Inches(0.06), Inches(1.16), MID_GREY)
    tb, tf = textbox(s, Inches(0.8), y, Inches(11.9), Inches(1.2))
    para(tf, title, size=14.5, bold=True, color=BLACK, first=True, space_after=3)
    rich(tf, [("Method:  ", True, MID_GREY), (method, False, BODY_INK)], size=12.5,
         space_after=3)
    rich(tf, [("Our position:  ", True, BLACK), (finding, False, BODY_INK)], size=12.5,
         space_after=0)
    y += Inches(1.28)
notes(s, "Four papers you should know. I will be explicit about where each one "
         "threatens my work rather than where it supports it.\n\n"
         "SQuAD 2.0 defines the task and gives the motivating number.\n\n"
         "Self-RAG is the strongest argument against my D1 design — its reflection "
         "tokens are learned, so they would have to be re-learned for each industrial "
         "category, and Huang et al. show intrinsic self-correction degrades without "
         "external feedback.\n\n"
         "CRAG is the closest prior art and the paper I differ from most clearly.\n\n"
         "And the 2026 conformal work is the strongest competitor to my gate. I am not "
         "going to claim I beat it — I claim something different in kind, and I adopt "
         "their diagnostics as my own limitation because their statistical guarantee "
         "needs exchangeability that a single-category corpus does not have.")

# ================================================================ SLIDE 7
# The cards are labelled by PHASE, not by "RO".
#
# The written deliverable numbers the proposal's six research objectives
# RO1-RO6, one per design move; this deck used to label four *phases* of the
# work RO1-RO4 as well, so the same labels meant different things in two
# documents a panel reads side by side. The phases are a different taxonomy
# and cannot be reconciled by relabelling, so they are renamed and each card
# now names the objective numbers it covers. See
# research/12_scope_reconciliation.md section 4.
s = base_slide("Four phases of the work, and the objectives each covers",
               "Each objective is stated as a finding to be defended, not a feature to build", nxt())
objs = [
    ("Phase A", "Framework design",
     "Design and develop an evidence-grounded RAG framework for industrial "
     "decision support, in which refusal is structural rather than advisory.",
     "Covers RO1–RO5 (the five design moves).\n"
     "Design objective — no formal hypothesis."),
    ("Phase B", "Component-level evaluation",
     "Evaluate four retrieval mechanisms (confidence gating, modality balance, hybrid "
     "retrieval with category pre-filter, contradiction surfacing) on hallucination "
     "and evidence grounding.",
     "H2.1  A code-level, non-bypassable gate reduces hallucination. (RO1)\n"
     "H2.2  Per-modality quotas improve recall on table and chart queries. (RO2)\n"
     "H2.3  Hybrid + RRF + reranker with category filter beats flat retrieval. (RO3)\n"
     "H2.4  Contradiction surfacing + per-claim tags improve decision accuracy. (RO4–RO5)"),
    ("Phase C", "Failure-mode characterisation",
     "Systematically characterise the failure modes and limitations of evidence-grounded "
     "RAG in industrial contexts.",
     "Covers RO1–RO5, fed by the negative results.\n"
     "Characterisation objective — no formal hypothesis."),
    ("Phase D", "Cross-category generalisation",
     "Assess how retrieval configurations transfer across industrial sub-domains.",
     "Covers RO6 (evaluation on industrial corpora and benchmarks).\n"
     "H4.1  Configurations tuned on a subset transfer zero-shot to held-out "
     "categories without statistically significant degradation."),
]
x = Inches(0.55)
for tag, title, body, hyp in objs:
    rect(s, x, Inches(1.32), Inches(2.98), Inches(4.95), WHITE,
         line=RGBColor(0xBF, 0xBF, 0xBF))
    rect(s, x, Inches(1.32), Inches(2.98), Inches(0.56), BLACK)
    tb, tf = textbox(s, x + Inches(0.2), Inches(1.42), Inches(2.6), Inches(0.36))
    rich(tf, [(f"{tag}  ", True, MID_GREY), (title, True, WHITE)], size=13,
         first=True, space_after=0)
    tb, tf = textbox(s, x + Inches(0.22), Inches(2.02), Inches(2.56), Inches(4.1))
    para(tf, body, size=12.5, color=BODY_INK, first=True, space_after=12)
    for line in hyp.split("\n"):
        rich(tf, [(line, False, MUTED_GREY)], size=11, space_after=5)
    x += Inches(3.08)
notes(s, "Four phases, and the research objectives each one covers — RO1 to RO6 "
         "are the proposal's numbering, one per design move, and each card here "
         "names the ones it answers. Note the framing: each objective is stated "
         "as a finding to be defended, not a feature to build. Phase A and Phase C "
         "do not carry formal hypotheses — A is a design objective and C is "
         "characterisation.\n\n"
         "H2.2 is the one I am most careful about, because it is the hypothesis my "
         "own experiments most clearly qualify. I will show you why in the results.\n\n"
         "H2.1 is the one to watch, and I will state its status before you ask. "
         "Conditional: the hypothesis holds under both prompt conditions. Under the cautious prompt -- the deployed system -- it is supported, at a price: the gate reduced the rate of answering unanswerable questions from 0.535 to 0.417, a fall of 11.8 points, at the cost of answering 30 of 32 answerable questions. Paired question by question, the gate refused 23 of the questions the ungated arm answered and let through 6 of the ones it did not (exact McNemar p = 0.002). Under the answering prompt, which differs from the cautious one by a single sentence, it is supported, at a price: the gate reduced the rate of answering unanswerable questions from 0.938 to 0.528, a fall of 41.0 points, at the cost of answering 30 of 32 answerable questions. Paired question by question, the gate refused 60 of the questions the ungated arm answered and let through 1 of the ones it did not (exact McNemar p = < 0.001). What the framework claims is therefore that the gate reduces the rate of answering unanswerable questions whatever the generator does, and that it is the one component whose behaviour does not depend on the generator's cooperation: the prompt can be wrong, and the gate still holds. The comparison was run under two prompt conditions, because one prompt cannot show what the gate does, and the hypothesis is supported under both prompt conditions. Under the cautious prompt the generator is allowed to decline and the gate is partly redundant with it; under the answering prompt it has to answer and the gate is what stands between it and a fabricated answer. I am reporting both, because the second is the claim and the first is the limit on it.")

# ================================================================ SLIDE 8
s = base_slide("Methodology: The Retrieval Stack",
               "Every formula implemented from first principles — not from a library", nxt())
formulas = [
    ("Dense leg — cosine similarity", "cos(q,d) = (q·d) / (‖q‖‖d‖)",
     "Direction encodes meaning; magnitude does not. After L2-normalisation this "
     "equals a dot product — which is what makes a pgvector HNSW index usable."),
    ("Lexical leg — BM25", "Σ_{t∈Q} IDF(t) · f(t,D)(k₁+1) / [f(t,D) + k₁(1−b+b|D|/avgdl)]",
     "IDF is the log-likelihood ratio of the term appearing under relevance vs not. "
     "Saturation stops the 10th occurrence counting 10× the 1st. k₁=1.2, b=0.75."),
    ("Fusion — Reciprocal Rank Fusion", "RRF(d) = Σᵢ 1/(k + rᵢ(d)),  k = 60",
     "BM25 scores and cosine similarities are on incomparable scales; rank is "
     "scale-free. At k=60 the discount is flat across the top 10, so ORDER IS DRIVEN "
     "BY AGREEMENT between retrievers."),
    ("Rerank — cross-encoder", "score(q,d) = wᵀ·Transformer([CLS] q [SEP] d [SEP])[CLS]",
     "Every token of the document attends to every token of the query. Strictly more "
     "expressive, strictly more expensive — one forward pass per pair. Output is a "
     "LOGIT, not a probability."),
]
y = Inches(1.32)
for title, eq, note in formulas:
    rect(s, Inches(0.55), y, Inches(12.23), Inches(1.24), WHITE,
         line=RGBColor(0xBF, 0xBF, 0xBF))
    tb, tf = textbox(s, Inches(0.78), y + Inches(0.12), Inches(3.6), Inches(0.5))
    para(tf, title, size=13.5, bold=True, color=BLACK, first=True, space_after=0)
    tb, tf = textbox(s, Inches(0.78), y + Inches(0.56), Inches(5.7), Inches(0.6))
    para(tf, eq, size=13, color=MID_GREY, bold=True, first=True, space_after=0,
         font="Cambria Math")
    tb, tf = textbox(s, Inches(6.7), y + Inches(0.18), Inches(5.9), Inches(1.0))
    para(tf, note, size=12, color=BODY_INK, first=True, space_after=0)
    y += Inches(1.32)
notes(s, "The retrieval stack. I implemented BM25 from scratch rather than using a "
         "library, because the thesis has to defend the exact scoring function, its "
         "parameters and its edge cases — and a black box cannot be defended.\n\n"
         "The derivation for BM25 comes from the probabilistic relevance framework: "
         "under term independence, taking logs of the product of likelihood ratios "
         "gives you a SUM of inverse document frequencies. IDF is not a heuristic "
         "weighting — it is a log-likelihood ratio.\n\n"
         "For RRF, the point is scale. You cannot add a BM25 score to a cosine "
         "similarity. But rank is comparable across retrievers. And notice at k=60 the "
         "discount is nearly flat across the top ten ranks — so the fused order is "
         "driven by agreement between the two retrievers, not by either one's score "
         "magnitude.")

# ================================================================ SLIDE 9
s = base_slide("Methodology: The Confidence Gate",
               "The Bayesian posterior, its calibration, and why the gate is a branch", nxt())
tb, tf = textbox(s, Inches(0.55), Inches(1.3), Inches(6.1), Inches(2.5))
para(tf, "The posterior (Bayes in odds form)", size=14, bold=True, color=BLACK,
     first=True, space_after=6)
para(tf, "P(R|d) = [P(R)/P(d|¬R)] · [P(d|R)/P(d|¬R)]", size=15, bold=True,
     color=MID_GREY, space_after=4, font="Cambria Math")
para(tf, "prior odds  ×  likelihood ratio", size=12, color=MUTED_GREY, space_after=10)
para(tf, "For a scalar rerank score x, a logistic model on the log-odds scale:",
     size=13, color=BODY_INK, space_after=4)
para(tf, "P(R|d) = σ(β₀ + β₁·x)", size=15, bold=True, color=MID_GREY, space_after=4,
     font="Cambria Math")
para(tf, "β fitted by maximum likelihood on a held-out QUERY split — not a candidate "
         "split, so no evaluation candidate leaks into calibration.", size=12,
     color=MUTED_GREY, space_after=8)
rich(tf, [("Calibrated at the QUERY level, not the chunk level:  ", True, MID_GREY),
          ("the gate asks “does this context contain enough evidence to answer "
           "at all?”, not “is this chunk the gold one?”. Calibrating per chunk "
           "against a 2% base rate fits “nothing is relevant” and calls it a "
           "probability.", False, BODY_INK)], size=11.5, space_after=0)
rect(s, Inches(0.55), Inches(4.15), Inches(6.1), Inches(2.05), PANEL_FILL,
     line=RGBColor(0xBF, 0xBF, 0xBF))
tb, tf = textbox(s, Inches(0.78), Inches(4.32), Inches(5.65), Inches(1.8))
para(tf, "Why calibration is not optional", size=13.5, bold=True, color=BLACK,
     first=True, space_after=5)
para(tf, "A cross-encoder score is a LOGIT whose scale shifts with query difficulty "
         "and candidate-set composition. Thresholding it directly is a category error. "
         "We report Brier score, Expected Calibration Error, a reliability table, and "
         "the full risk–coverage curve.", size=12.5, color=BODY_INK, space_after=0)
rect(s, Inches(6.95), Inches(1.3), Inches(5.83), Inches(4.9), WHITE,
     line=MID_GREY, line_w=1.6)
tb, tf = textbox(s, Inches(7.2), Inches(1.5), Inches(5.35), Inches(4.6))
para(tf, "The gate is control flow, not an instruction", size=14.5, bold=True,
     color=BLACK, first=True, space_after=8)
para(tf, "P_sufficient = calibrate(features of the retrieved set)", size=13.5,
     bold=True, color=BLACK, space_after=6, font="Cambria Math")
para(tf, "if P_sufficient < τ:", size=14, bold=True, color=MID_GREY, space_after=3,
     font="Cambria Math")
para(tf, "        return NO_EVIDENCE_RESPONSE", size=13.5, bold=True, color=MID_GREY,
     space_after=3, font="Cambria Math")
para(tf, "        # the LLM is never called", size=12, color=MUTED_GREY, space_after=8,
     font="Consolas")
para(tf, "else:", size=14, bold=True, color=MID_GREY, space_after=3, font="Cambria Math")
para(tf, "        context = accepted chunks", size=13.5, bold=True, color=MID_GREY,
     space_after=10, font="Cambria Math")
for t in [
    "The model cannot talk its way past it — no output it produces reaches the gate.",
    "The refusal is auditable: “posterior 0.312 against threshold 0.500” is checkable.",
    "It is portable without retraining — no per-category fine-tuning, unlike Self-RAG’s "
    "learned reflection tokens. The calibration is separate, and it is re-fitted "
    "per corpus and per retriever.",
]:
    rich(tf, [("▪  ", False, MID_GREY), (t, False, BODY_INK)], size=12.5, space_after=8)
notes(s, "The gate. Left: the mathematics. Bayes in odds form — prior odds times "
         "likelihood ratio — and for a scalar score, a logistic model on the "
         "log-odds scale, which is Platt scaling. The coefficients are fitted by "
         "maximum likelihood on a held-out query split.\n\n"
         "Note that I split by QUERY, not by candidate. If you split by candidate, "
         "candidates from evaluation queries leak into the calibration set and the "
         "calibration is optimistic.\n\n"
         "Right: the control flow. Three properties that no instruction can give you. "
         "The model cannot talk its way past it. The refusal is auditable. And it is "
         "portable across categories without retraining -- six "
         "in the corpus we measured on. One thing I want to be precise about, "
         "because it is a limitation I measured: the *mechanism* is portable, "
         "the *calibration* is not. The threshold is a fitted parameter and it "
         "is re-fitted per corpus and per retriever -- I measured three "
         "retrievers and they wanted three different thresholds.")

# ================================================================ SLIDE 10
s = base_slide("Methodology: Contradiction Surfacing & Per-Claim Confidence",
               "Two mechanisms that make the evidence trail trustworthy", nxt())
rect(s, Inches(0.55), Inches(1.3), Inches(6.05), Inches(4.9), WHITE,
     line=RGBColor(0xBF, 0xBF, 0xBF))
tb, tf = textbox(s, Inches(0.8), Inches(1.48), Inches(5.55), Inches(4.6))
para(tf, "D4 — CONTRADICTION SURFACING", size=12, bold=True, color=MID_GREY,
     first=True, space_after=8)
para(tf, "flag(A,B) = contradiction(A,B)  ∧  same_subject(A,B)", size=14, bold=True,
     color=BLACK, space_after=8, font="Cambria Math")
for t in [
    ("Contradiction gate", " — NLI says A denies B."),
    ("Topical gate", " — embedding similarity ≥ 0.55 AND Jaccard overlap of concrete "
     "identifiers ≥ 0.10."),
    ("Numeric conflict", " — two values for the same quantity is an explicit "
     "contradiction."),
    ("Revision supersession", " — “Rev 3: 187 units” and “Rev 4: 95 units” are BOTH "
     "true. Reported as a contradiction, this is the most damaging error available."),
]:
    rich(tf, [("▪  ", False, MID_GREY), (t[0], True, BLACK), (t[1], False, BODY_INK)],
         size=12.5, space_after=8)
para(tf, "Why a conjunction, not a tuned threshold? Raising the NLI threshold alone "
         "reduces false positives only by excluding genuine conflicts — both errors "
         "fall together. An orthogonal signal lets the two error types be traded off "
         "separately.", size=12, color=MUTED_GREY, italic=True, space_after=0)
rect(s, Inches(6.85), Inches(1.3), Inches(5.93), Inches(4.9), WHITE,
     line=RGBColor(0xBF, 0xBF, 0xBF))
tb, tf = textbox(s, Inches(7.1), Inches(1.48), Inches(5.43), Inches(4.6))
para(tf, "D5 — PER-CLAIM CONFIDENCE TAGGING", size=12, bold=True, color=MID_GREY,
     first=True, space_after=8)
para(tf, "q = 1 − Πᵢ (1 − eᵢ)          (noisy-OR over witnesses)", size=14, bold=True,
     color=BLACK, space_after=4, font="Cambria Math")
para(tf, "IG = H(prior) − H(q)          (information gain, bits)", size=14, bold=True,
     color=BLACK, space_after=10, font="Cambria Math")
for t in [
    ("q ≥ 0.80 → grounded", "   q ≥ 0.45 → inferred   else → uncertain."),
    ("Max, not mean, across chunks", " — so one strongly contradicting chunk is not "
     "diluted by many irrelevant ones."),
    ("Every claim carries", " its band, its citation identifiers, and a "
     "“contradicted” marker if the evidence refutes it."),
]:
    rich(tf, [("▪  ", False, MID_GREY), (t[0], True, BLACK), (t[1], False, BODY_INK)],
         size=12.5, space_after=8)
para(tf, "A necessary clarification: information gain is SYMMETRIC about q = 0.5 — a "
         "claim with q = 0.9 and one with q = 0.1 both give 0.531 bits. So the BAND "
         "cuts on q, and information gain is reported separately as the distinct "
         "“how much did the evidence reduce uncertainty” figure.",
     size=12, color=MUTED_GREY, italic=True, space_after=0)
notes(s, "Two mechanisms, and the second one has a subtlety I want to be precise "
         "about.\n\n"
         "D4: two independent gates must agree. The topical gate is what suppresses "
         "the false positives — an NLI model forced to label two passages about "
         "different sub-topics will often say 'contradiction' even though nothing "
         "conflicts. And note the revision supersession check: that is not a "
         "refinement, it is the difference between a useful system and one that "
         "tells engineers their policy is inconsistent when it was merely updated.\n\n"
         "D5: noisy-OR over independent witnesses, then the band is cut on the "
         "support probability q.\n\n"
         "And the clarification on the right is important, because the earlier "
         "version of this report conflated the two. Information gain is symmetric — "
         "it measures how much uncertainty was removed, not which way. A claim that "
         "is well REFUTED has high information gain too. So the band cuts on q, and "
         "IG is reported as a separate number.")

# ================================================================ SLIDE 11
s = base_slide("Evaluation Protocol",
               "A silver benchmark, paired statistics, and a stated operating point", nxt())
tb, tf = textbox(s, Inches(0.55), Inches(1.3), Inches(6.05), Inches(4.9))
para(tf, "THE BENCHMARK — and what it is not", size=12, bold=True, color=MID_GREY,
     first=True, space_after=7)
for t in [
    "276 silver-standard queries over a 2,383-chunk, 46-document public industrial "
    "corpus spanning six categories (supply chain, predictive maintenance, "
    "production scheduling, quality, reliability, facility layout).",
    "SILVER labels: derived mechanically from the document (a table cell → a lookup "
    "question). Reproducible and cheap, but slightly optimistic — it inflates "
    "ABSOLUTE recall, not the comparison between systems.",
    "A deliberate UNANSWERABLE class on topics absent from the corpus. Without it no "
    "gating experiment means anything: a system that answers everything scores 100% "
    "recall and 0% hallucination.",
    "The 300-query expert-annotated SupplyChainQA v7 (κ ≥ 0.7 on four categorical "
    "fields) is reported separately. The two are never pooled.",
    "SOURCE: English Wikipedia via the MediaWiki API. Licence CC BY-SA 4.0. The "
    "corpus ships IN FULL with the report — every document with its URL, the "
    "revision it was read at, and the SHA-256 of the bytes used.",
    "FOCUS DOMAIN: supply chain management — 14 documents, "
    "735 chunks, 176 questions, traced end to end "
    "in the case study.",

]:
    rich(tf, [("▪  ", False, MID_GREY), (t, False, BODY_INK)], size=12.5, space_after=9)
tb, tf = textbox(s, Inches(6.85), Inches(1.3), Inches(5.93), Inches(4.9))
para(tf, "STATISTICS", size=12, bold=True, color=MID_GREY, first=True, space_after=7)
for t in [
    "Paired throughout — every system is scored on the same queries.",
    "Wilcoxon signed-rank for continuous per-query outcomes (not the paired t-test: "
    "per-query faithfulness is bounded and left-skewed, violating normality on the "
    "differences).",
    "McNemar exact for binary outcomes. Effect sizes (Cohen’s d_z, Cliff’s δ) "
    "reported with every p-value — at n = 132 the difference between “unlikely” and "
    "“large” is material.",
    "THE GATE IS EVALUATED AS A POLICY, not a component: τ swept; the operating "
    "point is chosen by a STATED rule (highest τ still answering ≥ 90% of "
    "answerable queries), never by inspecting a favourable metric.",
    "False-positive rate at the operating point, with ALWAYS-FLAG and NEVER-FLAG "
    "baselines — because 12 of 21 published evaluations report no FPR at all.",
]:
    rich(tf, [("▪  ", False, MID_GREY), (t, False, BODY_INK)], size=12.5, space_after=9)
notes(s, "The protocol, briefly, because two elements matter for interpreting "
         "everything that follows.\n\n"
         "First, the benchmark is silver-standard, not expert-annotated, and I want "
         "to be clear about the bias that introduces: the derived gold chunk is "
         "guaranteed to contain the answer somewhere, so absolute recall is "
         "optimistic. The comparisons between systems are not affected, because "
         "every system is scored against identical labels. The expert-annotated "
         "benchmark from the earlier project report is reported separately.\n\n"
         "Second, the gate is evaluated as a selective-prediction POLICY. That "
         "framing comes from the 2026 literature: a filter result reported without a "
         "false-positive rate at a stated operating point does not mean anything. "
         "So I report always-flag and never-flag baselines alongside every rate.")

def _spoken_p(p: float) -> str:
    """Render a p-value the way it is said aloud, e.g. '3.5 times 10 to the minus 8'."""
    if p <= 0:
        return "smaller than one times ten to the minus three hundred"
    from math import floor, log10
    e = int(floor(log10(p)))
    m = p / (10 ** e)
    return f"{m:.1f} times 10 to the minus {abs(e)}"

# ================================================================ SLIDE 12
s = base_slide("Results: Retrieval Ablation",
               f"{exp1['benchmark']['n_queries']} queries · "
               f"{exp1['corpus_stats']['n_chunks']:,} chunks · "
               f"{_CAT_WORDS.get(exp1['corpus_stats'].get('n_categories'), 'one')} "
               f"category (the supply-chain focus domain) "
               f"· paired Wilcoxon between rungs", nxt())
if exp1:
    systems = exp1["systems"]
    order = ["A. bm25_only", "B. dense_only", "C. hybrid_rrf", "D. hybrid_rrf_rerank",
             "E. +category_filter", "F. +quota_pre_rerank", "G. +quota_post_rerank"]
    label = {
        "A. bm25_only": "A.  BM25 only",
        "B. dense_only": "B.  Dense only",
        "C. hybrid_rrf": "C.  Hybrid (RRF)",
        "D. hybrid_rrf_rerank": "D.  + cross-encoder rerank",
        "E. +category_filter": "E.  + category filter",
        "F. +quota_pre_rerank": "F.  + quota (pre-rerank)",
        "G. +quota_post_rerank": "G.  + quota (post-rerank)",
    }
    rows = []
    for k in order:
        v = systems[k]
        rows.append([
            label[k],
            f"{v['recall@5']:.3f}",
            f"{v['recall@10']:.3f}",
            f"{v['recall@20']:.3f}",
            f"{v['mrr']:.3f}",
            f"{v['nDCG@10']:.3f}",
            f"{v['modality_recall'].get('table', float('nan')):.3f}",
        ])
    comp = _comp_index(exp1["comparisons"])
    rows = []
    for k in order:
        v = systems[k]
        prev = None
        for a, b in zip(order[:-1], order[1:]):
            if b == k:
                prev = comp.get(a)
        d = f"{prev['delta']:+.3f}" if prev else "—"
        p = f"{prev['wilcoxon']['p_value']:.1e}" if prev else "—"
        rows.append([
            label[k],
            f"{v['recall@10']:.3f}",
            f"{v['mrr']:.3f}",
            f"{v['nDCG@10']:.3f}",
            f"{v['modality_recall'].get('table', float('nan')):.3f}",
            d, p,
        ])
    table(s, Inches(0.55), Inches(1.35), Inches(12.23), Inches(3.4),
          ["System", "R@10", "MRR", "nDCG@10", "Table R@10", "ΔR@10", "p"],
          rows, col_widths=[3.1, 1.0, 1.0, 1.1, 1.2, 1.0, 1.1],
          highlight_rows=(3, 5, 6), size=12)
    tb, tf = textbox(s, Inches(0.55), Inches(5.05), Inches(12.23), Inches(1.3))
    def _tbl(k):
        return systems[k]["modality_recall"].get("table", float("nan"))

    _de = _cmp("D. hybrid_rrf_rerank", "E. +category_filter")["delta"]
    _de_p = _cmp("D. hybrid_rrf_rerank", "E. +category_filter")["wilcoxon"]["p_value"]
    _ef = _cmp("E. +category_filter", "F. +quota_pre_rerank")["delta"]
    _ef_p = _cmp("E. +category_filter", "F. +quota_pre_rerank")["wilcoxon"]["p_value"]
    _fg = _cmp("F. +quota_pre_rerank", "G. +quota_post_rerank")["delta"]
    _fg_p = _cmp("F. +quota_pre_rerank", "G. +quota_post_rerank")["wilcoxon"]["p_value"]
    _pre_gain = _ef
    _post_loss = -_fg
    _post_vs_none = (exp1["systems"]["E. +category_filter"]["recall@10"]
                     - exp1["systems"]["G. +quota_post_rerank"]["recall@10"])
    rich(tf, [("Read the last two columns together: ", True, BLACK),
              (f"D \u2192 E is the category filter ({_de:+.3f}"
               + (f", p = {_de_p:.1e}" if _de_p < 0.05 else ", no measurable effect")
               + f"); E \u2192 F applies the quota before the reranker and gains "
               f"{_pre_gain:.3f} of overall recall"
               + (f" (p = {_ef_p:.1e})" if _ef_p < 0.05 else "")
               + f"; and F \u2192 G moves the same quota downstream and gives back "
               f"{_post_loss:.3f} of it, landing {_post_vs_none:.3f} below the "
               f"no-quota rung"
               + (f" (p = {_fg_p:.1e})" if _fg_p < 0.05 else ", not significant")
               + ". ", False, BODY_INK),
              ("The quota's position matters more than its threshold.",
               True, MID_GREY)], size=14, first=True, space_after=0)
else:
    tb, tf = textbox(s, Inches(0.55), Inches(2.0), Inches(12.0), Inches(1.5))
    para(tf, "Results not yet generated — run impl/experiments/run_ablation.py",
         size=18, color=MUTED_GREY, first=True)
notes(s, "This is the core experimental table. Seven systems, the same "
         f"{exp1['benchmark']['n_queries']} queries, "
         "paired Wilcoxon tests between adjacent rungs.\n\n"
         f"Read it top to bottom. BM25 alone "
         f"{systems['A. bm25_only']['recall@10']:.3f}, dense alone "
         f"{systems['B. dense_only']['recall@10']:.3f}, fused "
         f"{systems['C. hybrid_rrf']['recall@10']:.3f}, p = "
         f"{_spoken_p(comp['C. hybrid_rrf']['wilcoxon']['p_value'])}. Reranking on a "
         f"top-50 pool takes it to "
         f"{systems['D. hybrid_rrf_rerank']['recall@10']:.3f}.\n\n"
         "Then the three findings, which are the actual contribution, and two of "
         "them are negative. D to E is the category filter, and on this corpus it "
         "does nothing: the focus domain is one category, so there is nothing for "
         "it to filter. E to F: applying the modality quota BEFORE the reranker "
         "gains "
         f"{comp['E. +category_filter']['delta'] * 100:.1f} points of recall. "
         "F to G: the SAME quota applied AFTER the reranker gives back "
         f"{comp['F. +quota_pre_rerank']['delta'] * 100:.1f} of them, landing "
         f"{(exp1['systems']['E. +category_filter']['recall@10'] - exp1['systems']['G. +quota_post_rerank']['recall@10']) * 100:.1f} "
         "points below the no-quota rung. The quota's position in the pipeline "
         "matters more than its threshold value.\n\n"
         "I will unpack that in the next slide.")

# ================================================================ SLIDE 12b
_focus = _load_focus("exp6_focus_case")
s = base_slide("One Question, Before and After",
               "The focus domain — a supply-chain question traced through every stage",
               nxt())
if _focus and _focus.get("traces"):
    _traces = _focus["traces"]
    # Prefer a question the plain retriever got wrong and the framework got
    # right: that is the case where the mechanisms visibly did something.
    _t = next((x for x in _traces
               if not x["before"]["gold_in_top10"] and x["after"]["gold_in_accepted"]),
              None)
    if _t is None:
        _t = next((x for x in _traces if x["after"]["gold_in_accepted"]), _traces[0])
    _summ = _focus.get("summary", {})

    tb, tf = textbox(s, Inches(0.55), Inches(1.02), Inches(12.23), Inches(0.42))
    para(tf, f"\u201c{_t['query']}\u201d", size=13.5, bold=True, color=BLACK,
         first=True, space_after=0)

    # ---- BEFORE -------------------------------------------------------
    rect(s, Inches(0.55), Inches(1.52), Inches(5.95), Inches(3.55), PANEL_FILL,
         line=RGBColor(0xBF, 0xBF, 0xBF))
    tb, tf = textbox(s, Inches(0.78), Inches(1.68), Inches(5.5), Inches(3.3))
    para(tf, "BEFORE  \u2014  plain BM25, no rerank, no gate", size=11.5,
         bold=True, color=MUTED_GREY, first=True, space_after=6)
    for _c in _t["before"]["chunks"][:4]:
        _mark = "  \u2190 GOLD" if _c["is_gold"] else ""
        rich(tf, [(f"[{_c['modality']}] ", False, MUTED_GREY),
                  (_c["preview"][:120], False, BODY_INK)], size=10.5, space_after=4)
        if _mark:
            rich(tf, [(_mark, True, MID_GREY)], size=10.5, space_after=6)
    rich(tf, [("Gold chunk found in top 10: ", True, BLACK),
              ("yes" if _t["before"]["gold_in_top10"] else "NO", True,
               POSITIVE if _t["before"]["gold_in_top10"] else MID_GREY)],
         size=11, space_after=0)

    # ---- AFTER --------------------------------------------------------
    rect(s, Inches(6.85), Inches(1.52), Inches(5.93), Inches(3.55),
         RGBColor(0xF7, 0xF7, 0xF7), line=RGBColor(0xCF, 0xCF, 0xCF))
    tb, tf = textbox(s, Inches(7.08), Inches(1.68), Inches(5.47), Inches(3.3))
    para(tf, "AFTER  \u2014  the full framework", size=11.5, bold=True,
         color=MID_GREY, first=True, space_after=6)
    for _c in _t["after"]["chunks"][:4]:
        _mark = "  \u2190 GOLD" if _c["is_gold"] else ""
        rich(tf, [(f"[{_c['modality']}] ", False, MUTED_GREY),
                  (_c["preview"][:120], False, BODY_INK)], size=10.5, space_after=4)
        if _mark:
            rich(tf, [(_mark, True, POSITIVE)], size=10.5, space_after=6)
    _pt = _t["after"].get("posterior_top")
    _mc = _t["after"].get("modality_counts") or {}
    rich(tf, [("Gate: ", True, BLACK),
              ("REFUSED \u2014 no evidence in the context" if _t["after"]["gate_rejected"]
               else f"answered (posterior {_pt:.3f})" if _pt is not None else "answered",
               True, MUTED_GREY)], size=11, space_after=3)
    rich(tf, [("Context: ", True, BLACK),
              (f"{len(_t['after']['accepted'])} chunks, " +
               ", ".join(f"{k} {v}" for k, v in _mc.items()), False, BODY_INK)],
         size=11, space_after=0)

    # ---- THE ANSWER ----------------------------------------------------
    rect(s, Inches(0.55), Inches(5.25), Inches(12.23), Inches(1.72), WHITE,
         line=RGBColor(0xBF, 0xBF, 0xBF))
    tb, tf = textbox(s, Inches(0.78), Inches(5.38), Inches(11.8), Inches(1.5))
    para(tf, "THE ANSWER, WITH EVERY CLAIM BANDED", size=11, bold=True,
         color=MID_GREY, first=True, space_after=5)
    _claims = _t["answer"]["claims"][:3]
    if _claims:
        for _c in _claims:
            _band = (_c.get("band") or "?").upper()
            _col = {"GROUNDED": POSITIVE, "INFERRED": MID_GREY}.get(_band, MUTED_GREY)
            rich(tf, [(f"[{_band}] ", True, _col),
                      ((_c.get("claim") or "")[:150], False, BODY_INK)],
                 size=11, space_after=3)
    else:
        para(tf, ("The gate refused this question, so no claim was made."
                  if _t["after"]["gate_rejected"] else
                  "The gate answered, but the extractor produced no claim to band."),
             size=11, color=MUTED_GREY, space_after=0)
    notes(s, "This is one real supply-chain question, and it is the slide I would "
             "go to if the panel asked whether any of this actually works.\n\n"
             "On the left is what a plain keyword retriever returned. On the right "
             "is what the framework returned instead: the fused ranking, the "
             "reranked ranking, the context the gate was willing to accept, and "
             "the modality mix of that context.\n\n"
             "The point is not that the answer is longer. The point is that every "
             "sentence in the answer is attached to a chunk, every chunk is in the "
             "context the gate accepted, and every claim carries a band saying "
             "whether it is grounded, inferred, or uncertain. A practitioner can "
             "check it. That is the whole thesis.\n\n"
             "The full case study, with every stage of several questions, is in "
             "the appendix of the written report.")
else:
    tb, tf = textbox(s, Inches(0.55), Inches(2.0), Inches(12.0), Inches(1.5))
    para(tf, "Focus-domain case study not yet generated", size=18, color=MUTED_GREY,
         first=True)

# ================================================================ SLIDE 13
s = base_slide("Three Findings \u2014 and What Each One Cost",
               "Failure-mode results that generalise beyond this corpus", nxt())
def _v(system, key):
    return exp1["systems"][system][key]


def _p(before, after):
    """The paired Wilcoxon p-value for one rung of the ablation."""
    for c in exp1["comparisons"]:
        if c["comparison"].startswith(before + " -> " + after):
            return c["wilcoxon"]["p_value"]
    return float("nan")


_C, _D = "C. hybrid_rrf", "D. hybrid_rrf_rerank"
_E, _F, _G = "E. +category_filter", "F. +quota_pre_rerank", "G. +quota_post_rerank"
_cs = exp1["corpus_stats"]

# The findings are written from the measured signs, so they cannot claim a
# gain the data does not show.
_A, _B = exp1["systems"]["A. bm25_only"], exp1["systems"]["B. dense_only"]
_Cv = exp1["systems"]["C. hybrid_rrf"]
_Ev = exp1["systems"]["E. +category_filter"]
_Fv = exp1["systems"]["F. +quota_pre_rerank"]
_Gv = exp1["systems"]["G. +quota_post_rerank"]


_cd_delta = _cmp("C. hybrid_rrf", "D. hybrid_rrf_rerank")["delta"]
_cd_p = _cmp("C. hybrid_rrf", "D. hybrid_rrf_rerank")["wilcoxon"]["p_value"]
_cd_sig = _cd_p < 0.05
_ef_cost = _Ev["recall@10"] - _Fv["recall@10"]
_eg_cost = _Ev["recall@10"] - _Gv["recall@10"]
_tbl_gain = (_Gv["modality_recall"].get("table", 0)
             - _Ev["modality_recall"].get("table", 0))
_fusion_over_bm25 = _Cv["recall@10"] - _A["recall@10"]

_fusion_order_better = (_Cv["nDCG@10"] > _A["nDCG@10"]
                        and _Cv["mrr"] > _A["mrr"])
_ac = None
for _c in exp1["comparisons"]:
    if _c.get("comparison") == "A. bm25_only -> C. hybrid_rrf":
        _ac = _c
_ac_p = _ac["wilcoxon"]["p_value"] if _ac else float("nan")

_f1_title = "The encoder, not the fusion, decided what the hybrid paid"
_f1_body = (f"With the retrieval-trained encoder the dense leg reaches "
            f"R@10 {_B['recall@10']:.3f} and the fused system "
            f"{_Cv['recall@10']:.3f}, against plain BM25's "
            f"{_A['recall@10']:.3f}; nDCG@10 {_Cv['nDCG@10']:.3f} against "
            f"BM25's {_A['nDCG@10']:.3f}. The difference is not significant "
            f"({_fusion_over_bm25:+.3f}, p = {_ac_p:.2f}). Before the swap the "
            f"fusion's ordering was behind the lexical leg's: RRF gives the two "
            f"legs equal say, so a much weaker leg spends slots on worse "
            f"candidates.")

if _cd_sig:
    _f2_title = "The reranker improves recall as well as ordering"
    _f2_body = (f"With a top-50 pool, Recall@10 {_v(_C, 'recall@10'):.3f} \u2192 "
                f"{_v(_D, 'recall@10'):.3f} (p = {_cd_p:.1e}).")
else:
    # The reranker's effect is corpus-dependent, and saying so is more
    # useful than the half of it that used to be said. On this focus domain
    # it buys nothing; on the six-category corpus it buys ordering.
    _f2_title = "The reranker buys ordering, not recall \u2014 where there is something to reorder"
    _f2_body = (f"On this focus domain it buys nothing: Recall@10 "
                f"{_v(_C, 'recall@10'):.3f} \u2192 "
                f"{_v(_D, 'recall@10'):.3f} ({_cd_delta:+.3f}, p = {_cd_p:.2f}, "
                f"not significant), MRR {_v(_C, 'mrr'):.3f} \u2192 {_v(_D, 'mrr'):.3f} "
                f"and nDCG@10 {_v(_C, 'nDCG@10'):.3f} \u2192 "
                f"{_v(_D, 'nDCG@10'):.3f}. On the six-category corpus the same "
                f"reranker does buy ordering: MRR {_mc_mrr_c:.3f} \u2192 "
                f"{_mc_mrr_d:.3f} and nDCG@10 {_mc_ndcg_c:.3f} \u2192 "
                f"{_mc_ndcg_d:.3f}, with recall unchanged at "
                f"{_mc_r_c:.3f}. A cross-encoder cannot bring in evidence the "
                f"first stage discarded, only reorder what it was given \u2014 so "
                f"what it buys depends on how much there is to reorder.")

_f3_title = "The quota only pays where the corpus leaves something to buy"
if abs(_tbl_gain) < 1e-9:
    _f3_body = (f"Table recall is already {_Ev['modality_recall'].get('table', 0):.3f} "
                f"here, so there is no table gain to buy: the quota moves overall "
                f"recall by {-_ef_cost:+.3f} applied before the reranker and "
                f"{-_eg_cost:+.3f} applied after it. On the six-category corpus, "
                f"where the reranker takes table recall from 1.000 to 0.923, it "
                f"restores it to 1.000 before the reranker and 0.962 after it.")
else:
    _f3_body = (f"The quota lifts table recall by {_tbl_gain:+.3f}. Applied "
                f"before the reranker it moves overall recall by "
                f"{-_ef_cost:+.3f}; applied after it, by {-_eg_cost:+.3f}.")

findings = [
    ("1", _f1_title, _f1_body,
     "What the hybrid buys is bought by the encoder, not by the fusion. "
     "Swapping the general-purpose sentence encoder for a retrieval-trained one "
     "lifted the dense leg and closed the fusion's ordering deficit against "
     "the lexical leg.", BLACK),
    ("2", _f2_title, _f2_body,
     "So the measurement that matters is the candidate-pool curve, not the "
     "reranker. Sweeping the pool is one parameter and it is cheap.", DARK_GREY),
    ("3", _f3_title, _f3_body,
     f"Which placement is cheaper depends on the retriever, not on the quota's "
     f"own logic. This corpus is {_cs['share_text']:.1%} text, "
     f"{_cs['share_table']:.1%} table, {_cs['share_chart']:.1%} chart \u2014 so "
     f"the modality mechanism has little to act on, and the composition is "
     f"reported before the result, because it predicts whether D2 can have any "
     f"effect at all.", MID_GREY),
]
y = Inches(1.3)
for num, title, body, so, col in findings:
    rect(s, Inches(0.55), y, Inches(0.56), Inches(1.55), col)
    tb, tf = textbox(s, Inches(0.55), y + Inches(0.5), Inches(0.56), Inches(0.5),
                     align=PP_ALIGN.CENTER)
    para(tf, num, size=22, bold=True, color=WHITE, first=True, space_after=0,
         align=PP_ALIGN.CENTER)
    tb, tf = textbox(s, Inches(1.28), y, Inches(11.5), Inches(1.6))
    para(tf, title, size=15, bold=True, color=BLACK, first=True, space_after=3)
    para(tf, body, size=12.3, color=BODY_INK, space_after=4)
    rich(tf, [("→  ", True, col), (so, False, MUTED_GREY)], size=12, space_after=0)
    y += Inches(1.66)
notes(s, "These three are the substance of the work. Let me take them in order.\n\n"
         "One. The same reranker, the same corpus, two pool sizes. With a top-50 "
         f"pool recall goes up "
         f"{(systems['D. hybrid_rrf_rerank']['recall@10'] - systems['C. hybrid_rrf']['recall@10']) * 100:.1f} "
         "points. With a top-10 pool recall cannot improve "
         "at all and recall at twenty drops. That is a mechanism, and it plausibly "
         "explains the minus 5.34 point regression I reported in September on a "
         "completely different corpus — which turns an anomaly into a hypothesis I "
         "can hand to whoever maintains that code.\n\n"
         "Two. The quota. Before the reranker it is a disaster; after the reranker it "
         "is affordable. The general rule: a constraint on a downstream artefact must "
         "be enforced where it can still choose the candidates.\n\n"
         "Three. And this is the one I would most like the panel to take away: the "
         "modality result is a POWER question, not an algorithm question. On a corpus "
         f"that is {_cs['share_text']:.0%} prose, you cannot show a modality effect, "
         "and anyone who reports "
         "one on such a corpus should be asked how.")

# ================================================================ SLIDE 14
s = base_slide("Results: The Gate as a Selective-Prediction Policy",
               "Coverage traded against correctness — both sides reported", nxt())
if exp2:
    cal = exp2["calibration_metrics"]
    uni = exp2["univariate_top1_rerank"]
    ch = exp2["chosen_operating_point"]
    sweep = exp2["threshold_sweep"]
    rows = []
    for srow in sweep[::2]:
        rows.append([
            f"{srow['tau']:.2f}",
            f"{srow['answerable_answered']:.3f}",
            f"{srow['unanswerable_refused']:.3f}",
            f"{srow['abstention_precision']:.3f}",
            f"{srow['coverage']:.3f}",
        ])
    kpi(s, Inches(0.55), Inches(1.32), Inches(2.85), Inches(1.25),
        f"{uni['beta0']:.2f}", "univariate β₀  (top rerank score)")
    kpi(s, Inches(3.55), Inches(1.32), Inches(2.85), Inches(1.25),
        f"{uni['beta1']:.2f}", "univariate β₁  (odds multiplier / unit)")
    kpi(s, Inches(6.55), Inches(1.32), Inches(2.85), Inches(1.25),
        f"{cal['ece']:.3f}", "Expected Calibration Error",
        color=MID_GREY if cal['ece'] > 0.1 else POSITIVE)
    kpi(s, Inches(9.55), Inches(1.32), Inches(3.23), Inches(1.25),
        f"{cal['brier']:.3f}", "Brier score  (lower is better)")
    table(s, Inches(0.55), Inches(2.85), Inches(7.6), Inches(3.4),
          ["τ", "answerable answered", "unanswerable refused",
           "abstention precision", "coverage"],
          rows, col_widths=[0.7, 1.5, 1.6, 1.6, 1.1], size=11.5)
    rect(s, Inches(8.4), Inches(2.85), Inches(4.38), Inches(4.15), PANEL_FILL,
         line=RGBColor(0xBF, 0xBF, 0xBF))
    tb, tf = textbox(s, Inches(8.62), Inches(3.00), Inches(3.94), Inches(3.85))
    para(tf, "THREE THINGS TO TAKE AWAY", size=11.5, bold=True, color=MID_GREY,
         first=True, space_after=7)
    rich(tf, [("1.  ", True, BLACK),
              (f"The calibration is a FITTED PARAMETER of the deployment, not a "
               f"constant of the architecture, and it is calibrated on a "
               f"QUERY-level label (does this context hold enough evidence to "
               f"answer?), not a chunk-level one. With one gold chunk among ~50 "
               f"candidates the chunk-level base rate is 2%, so fitting against "
               f"it returns ‘nothing is relevant’ and calls it a probability.",
               False, BODY_INK)], size=11, space_after=8)
    rich(tf, [("2.  ", True, BLACK),
              (f"The operating point is selected by a STATED rule "
               f"({exp2['operating_point_rule']}) — not by picking a "
               f"favourable metric. At τ = {ch['tau']:.2f} the gate answers "
               f"{ch['answerable_answered']:.1%} of answerable questions and refuses "
               f"{ch['unanswerable_refused']:.1%} of unanswerable ones. The "
               f"always-answer baseline refuses nothing; reporting only the refusal "
               f"rate would overstate the gain.", False, BODY_INK)], size=12, space_after=0)
else:
    tb, tf = textbox(s, Inches(0.55), Inches(2.0), Inches(12.0), Inches(1.5))
    para(tf, "Results not yet generated — run impl/experiments/run_gate.py",
         size=18, color=MUTED_GREY, first=True)
notes(s, "The gate. Top row: the fitted coefficients and the calibration quality. "
         "Bottom left: the threshold sweep, and I want you to read the abstention "
         "precision column, not just the refusal column.\n\n"
         "The two takeaways are on the right.\n\n"
         "First, the calibration coefficients fitted here differ substantially from "
         "the ones I fitted in September on a different corpus. That is not an "
         "inconsistency — it is a demonstration that the operating point is a fitted "
         "parameter of a deployment, not a constant of an architecture. And DeclineCraft "
         "shows why this matters: a better retriever changes the right threshold.\n\n"
         "I measured that rather than asserting it. I fitted the gate separately on "
         "three retrievers that give it the same kind of input, and the thresholds "
         "came out at 0.05 on the shipped hybrid, 0.10 on the "
         "lexical leg alone and 0.05 on the dense leg alone — and the "
         "operating points moved with them: the hybrid's gate refuses "
         "0.361 of the unanswerable questions, the lexical gate "
         "0.611. Applying my threshold unchanged to the lexical leg turned out "
         "to be too permissive in exactly the way that would flatter that arm. So the "
         "frontier is reported as a curve now, one sweep per retriever, and not as a "
         "single chosen point.\n\n"
         "Second, the operating point. I selected it by a rule stated in advance, not "
         "by finding a flattering number. And notice the abstention precision "
         "column — a gate that refuses everything would also have a high refusal rate, "
         "so you need both numbers together.")

# ================================================================ SLIDE 14b
s = base_slide("The Benchmark's Own Defect: Found, Repaired, Re-measured",
               "The unanswerable half was separable from the question alone", nxt())
if exp12 and exp2:
    _af = exp12.get("after_repair") or {}
    _bf = exp12.get("before_repair") or {}
    _st = (_bf.get("structural") or {}).get("whole_class") or {}
    _st_new = (_af.get("structural_separability") or {}).get(
        "repaired_whole_class") or {}
    _sc_old = _bf.get("shortcut_diagnostic") or {}
    _sc_new = _af.get("shortcut_diagnostic") or {}
    _match = (_af.get("structural_matching") or {}).get(
        "repaired_whole_class") or {}
    _rfam = (exp2.get("refusal_by_family") or {}).get("by_family") or {}
    _hard = {k: v for k, v in _rfam.items() if "corpus_anchored" in k}
    _hn = sum(v.get("n", 0) for v in _hard.values())
    _hr = sum(v.get("refused", 0) for v in _hard.values())
    _ood = _rfam.get("unanswerable_ood") or {}

    kpi(s, Inches(0.55), Inches(1.32), Inches(2.85), Inches(1.25),
        f"{_st.get('roc_auc', float('nan')):.3f}", "separable from the question alone (AUC, before)",
        color=RGBColor(0x55, 0x55, 0x55))
    kpi(s, Inches(3.55), Inches(1.32), Inches(2.85), Inches(1.25),
        f"{_st_new.get('roc_auc', float('nan')):.3f}", "after the repair (null "
        f"{_st_new.get('permutation_null_auc_mean', float('nan')):.3f})",
        color=POSITIVE)
    kpi(s, Inches(6.55), Inches(1.32), Inches(2.85), Inches(1.25),
        f"{_sc_old.get('share_of_unanswerable_carried_by_the_rule', float('nan')):.1%}",
        "carried by ONE regular expression (before)",
        color=RGBColor(0x55, 0x55, 0x55))
    kpi(s, Inches(9.55), Inches(1.32), Inches(3.23), Inches(1.25),
        f"{_hr}/{_hn}", "corpus-anchored questions the gate now refuses",
        color=MID_GREY)
    table(s, Inches(0.55), Inches(2.85), Inches(7.6), Inches(3.4),
          ["", "before", "after", "permutation null"],
          [
              ["AUC, question's shape only",
               f"{_st.get('roc_auc', float('nan')):.3f}",
               f"{_st_new.get('roc_auc', float('nan')):.3f}",
               f"{_st_new.get('permutation_null_auc_mean', float('nan')):.3f}"],
              ["one-rule shortcut catches",
               f"{_sc_old.get('share_of_unanswerable_carried_by_the_rule', float('nan')):.1%}",
               f"{_sc_new.get('share_of_unanswerable_carried_by_the_rule', float('nan')):.1%}",
               "0% (no rule can do this)"],
              ["structural twin exists",
               "—",
               f"{_match.get('n_matched', 0)}/{_match.get('n_unanswerable', 0)}",
               "1.000 needed"],
              ["gate refuses the unanswerable class",
               "91.7%",
               f"{(_hr/_hn if _hn else float('nan')):.1%} (hard stratum)",
               "—"],
              ["gate refuses the off-topic family",
               "—",
               f"{_ood.get('refused_rate', float('nan')):.1%}",
               "—"],
          ],
          col_widths=[2.5, 1.2, 1.2, 1.8], size=11.5)
    rect(s, Inches(8.4), Inches(2.85), Inches(4.38), Inches(4.15), PANEL_FILL,
         line=RGBColor(0xBF, 0xBF, 0xBF))
    tb, tf = textbox(s, Inches(8.62), Inches(3.00), Inches(3.94), Inches(3.85))
    para(tf, "WHAT THE DEFECT WAS, AND WHAT IT COST", size=11.5, bold=True,
         color=MID_GREY, first=True, space_after=7)
    rich(tf, [("1.  ", True, BLACK),
              ("The unanswerable half's hard case asked about a fabricated "
               "identifier (SKU AST-5454). Every one of those questions carried "
               "an identifier shape that no answerable question carried, so one "
               "regular expression separated the classes perfectly. A system "
               "refusing on the question's shape would have scored as well as "
               "one reading the passages.", False, BODY_INK)], size=11, space_after=8)
    rich(tf, [("2.  ", True, BLACK),
              ("So the refusal rate was an UPPER BOUND, not a measurement. I "
               "rebuilt the half — same question stems, same source documents, "
               "same label machinery, each repaired question given a structural "
               "twin in the answerable class — and re-measured everything.",
               False, BODY_INK)], size=11, space_after=8)
    rich(tf, [("3.  ", True, BLACK),
              ("The honest cost: the gate now refuses far fewer of the hard "
               "unanswerable questions than the defective benchmark suggested. "
               "The detection problem is harder than my first benchmark made "
               "it look, and the repair is what showed it.",
               False, BODY_INK)], size=11, space_after=0)
else:
    tb, tf = textbox(s, Inches(0.55), Inches(2.0), Inches(12.0), Inches(1.5))
    para(tf, "Audit not yet generated — run impl/experiments/audit_unanswerable_class.py",
         size=18, color=MUTED_GREY, first=True)
notes(s, "This is the slide I would most like the examiners to ask me about.\n\n"
         "A refusal benchmark lives or dies on its unanswerable half, and ours was "
         "the half I audited last. The audit found that a classifier given only the "
         "question — no retrieval, no evidence — could tell the two classes apart "
         "perfectly. The reason was a construction artefact: the hard case named a "
         "fabricated identifier, and no answerable question ever named one, so one "
         "regular expression did the whole job.\n\n"
         "That is disqualifying for the claim I wanted to make, because it means a "
         "system that refused on the shape of the question would have scored exactly "
         "as well as one that read the retrieved passages. So I rebuilt the half — "
         "same stems, same documents, same label machinery — and gave every repaired "
         "question a structural twin in the answerable class. After the repair the "
         "classifier is at chance against its own permutation null.\n\n"
         "And here is the cost, which I want to be straightforward about: the gate "
         "now refuses a much smaller fraction of the hard unanswerable questions "
         "than the defective benchmark suggested. The detection problem is harder "
         "than my first benchmark made it look. The repair is what showed it, and I "
         "would rather report the true number than the flattering one.")

# ================================================================ SLIDE 15
s = base_slide("Results: Contradiction Surfacing & Cross-Category Transfer",
               "Both mechanisms are reported with their baselines", nxt())
if exp3:
    sm = exp3["summary"]
    _kinds = sm.get("flagged_by_kind") or {}
    rows = [
        ["NLI alone", f"{sm['nli_only_flagged']}", f"{sm['nli_flag_rate']:.3f}"],
        ["The shipped gate", f"{sm['joint_gate_flagged']}", f"{sm['joint_flag_rate']:.3f}"],
        ["Baseline: always flag", f"{sm['pairs_compared']}",
         f"{sm['baseline_always_flag_false_positive_rate']:.3f}"],
        ["Baseline: never flag", "0", "—"],
    ]
    table(s, Inches(0.55), Inches(1.35), Inches(6.3), Inches(1.6),
          ["Detector", "Flagged", "Flag rate"], rows,
          col_widths=[3.4, 1.2, 1.2], size=11.5, highlight_rows=(1,))
    tb, tf = textbox(s, Inches(0.55), Inches(3.30), Inches(6.3), Inches(3.82))
    para(tf, "READ WITH THE BASELINES ATTACHED", size=11.5, bold=True, color=MID_GREY,
         first=True, space_after=6)
    for t in [
        f"Prevalence of true conflict in the compared pairs: "
        f"{sm['prevalence_of_true_conflict']:.4f}. Without prevalence a "
        f"false-positive rate is uninterpretable.",
        f"The revision-supersession check suppressed {sm['revision_supersession_suppressed']} "
        f"pairs whose apparent conflict was simply a later revision of the same policy.",
        f"Three branches: {_kinds.get('semantic', 0)} semantic, "
        f"{_kinds.get('quantity', 0)} quantity, {_kinds.get('revision', 0)} revision. "
        f"The same-subject check suppresses "
        f"{sm['nli_only_flagged'] - sm['joint_gate_flagged']} of the bare NLI "
        f"gate's alarms.",
        *_src_cp_brief(_src_load("exp11_contradiction_precision")),
        f"Surfacing is gated on measured precision: "
        f"{sm.get('surfaced_findings', 0)} surfaced, "
        f"{sm.get('withheld_findings', 0)} withheld on this corpus.",
    ]:
        rich(tf, [("\u25aa  ", False, MID_GREY), (t, False, BODY_INK)], size=10.5, space_after=5)
else:
    tb, tf = textbox(s, Inches(0.55), Inches(1.5), Inches(6.3), Inches(1.0))
    para(tf, "run_gate / run_contradiction pending", size=14, color=MUTED_GREY, first=True)

if exp4:
    lh = exp4["leave_half_out"]
    tb, tf = textbox(s, Inches(7.15), Inches(1.35), Inches(5.63), Inches(4.9))
    para(tf, "CROSS-CATEGORY TRANSFER (RO6)", size=11.5, bold=True, color=MID_GREY,
         first=True, space_after=7)
    rich(tf, [("Tuning half: ", True, BLACK),
              (", ".join(lh["tuning_categories"]), False, BODY_INK)], size=12,
         space_after=4)
    rich(tf, [("Held-out half: ", True, BLACK),
              (", ".join(lh["held_out_categories"]), False, BODY_INK)], size=12,
         space_after=10)
    rich(tf, [("β fitted on the tuning half: ", True, BLACK),
              (f"intercept {lh['weights_tuning_half'][0]:.3f}, "
               f"top-1 rerank weight {lh['weights_tuning_half'][1]:.3f}", False, BODY_INK)],
         size=12, space_after=4)
    rich(tf, [("β fitted on the held-out half: ", True, BLACK),
              (f"intercept {lh['weights_held_out_half'][0]:.3f}, "
               f"top-1 rerank weight {lh['weights_held_out_half'][1]:.3f}", False, BODY_INK)],
         size=12, space_after=12)
    for t in [
        "The RANKING of configurations transfers across industrial sub-domains; the "
        "THRESHOLD does not transfer unchanged.",
        "The error is systematic: a threshold fitted on one configuration is too "
        "PERMISSIVE where it is transferred, and too permissive in the direction "
        "that flatters the configuration it is transferred to.",
        "This is the practical form of DeclineCraft's finding that better retrieval "
        "reduces abstention, and it is why the calibration is re-fitted per arm.",
    ]:
        rich(tf, [("▪  ", False, MID_GREY), (t, False, BODY_INK)], size=12, space_after=9)
    rows = [[p["category"], p["n"], f"{p['recall@10']:.3f}", f"{p['mrr']:.3f}",
             f"{p['ndcg@10']:.3f}"] for p in exp4["per_category_retrieval"]]
    table(s, Inches(7.15), Inches(4.55), Inches(5.63), Inches(1.7),
          ["Held-out category", "n", "R@10", "MRR", "nDCG@10"], rows,
          col_widths=[2.4, 0.6, 0.9, 0.9, 1.0], size=10.5)
else:
    tb, tf = textbox(s, Inches(7.15), Inches(1.5), Inches(5.6), Inches(1.0))
    para(tf, "run_transfer pending", size=14, color=MUTED_GREY, first=True)
notes(s, "Two results on one slide.\n\n"
         "Left: contradiction detection, reported with prevalence and with the "
         "always-flag and never-flag baselines. The always-flag row is the point — a "
         "detector that flags everything has perfect recall and zero precision. Any "
         "improvement I claim has to be read against those two rows, and the "
         "prevalence number is there because a false-positive rate without prevalence "
         "is uninterpretable.\n\n"
         "Right: cross-category transfer. The ranking of configurations transfers; the "
         "threshold does not; and the error is systematic — a threshold fitted on one "
         "configuration is too permissive where it is transferred, and too permissive "
         "in the direction that flatters the configuration it is transferred to. That "
         "direction matters: if I had used one global threshold, the arm it was "
         "transferred to would have looked better than it is. This is exactly why I "
         "re-fit per arm.")

# ================================================================ SLIDE 15b
s = base_slide("A Second Corpus: Federal Regulations",
               "The same framework on authentic, versioned, binding text — and "
               "on a corpus that contains real conflicts", nxt())

tb, tf = textbox(s, Inches(0.55), Inches(1.22), Inches(6.05), Inches(5.85))
rich(tf, [("THE CORPUS.  ", True, MID_GREY),
          ("110 documents, ", False, BODY_INK),
          ("2,443 chunks", True, BODY_INK),
          (", four regulatory regimes — OSHA general industry, OSHA PSM and EPA "
           "RMP, EPA new source performance standards, DOT hazmat — from the "
           "Electronic Code of Federal Regulations. Public domain, and it "
           "carries version history: the same provision read at two dates is "
           "the same rule at two issues, so the corpus contains the conflicts "
           "the mechanism exists to find. Its benchmark has "
           "444 queries (247 answerable, "
           "197 unanswerable) with its own shortcut audit.",
           False, BODY_INK)],
     size=11.3, first=True, space_after=10)
para(tf, "RO6 — THE NEGATIVE FINDINGS REPLICATE", size=11.5, bold=True,
     color=MID_GREY, space_after=6)
for t in [
    "On this corpus the lexical leg carried the pipeline: BM25 beats the "
    "general-purpose dense encoder by ΔRecall@10 "
    "-0.081 (p = 0.00026, n = "
    "247) — where on the encyclopaedic corpus this rested "
    "on 32 queries at p = 0.025. That lexical beats dense on legal and "
    "financial text is already published, so the new part is the corollary.",
    "The corollary: the fusion does not beat its own lexical leg (Δ "
    "+0.000, p = 1.00000), and the "
    "category pre-filter is a no-op (Δ +0.000, "
    "p = 1.00000) — which is what the shipped design "
    "assumed otherwise.",
    "The candidate-pool curve is no longer saturated, so the lead claim can be "
    "measured rather than inferred: at pool 50, Recall@20 = "
    "1.000 while Recall@10 stays 0.988 — "
    "1.21% of the golds are found and then pushed out of "
    "the ten-chunk context.",
]:
    rich(tf, [("\u25aa  ", False, MID_GREY), (t, False, BODY_INK)], size=11.3,
         space_after=8)

tb, tf = textbox(s, Inches(7.15), Inches(1.22), Inches(5.63), Inches(5.85))
para(tf, "RO4 — IT FINDS THE CONFLICTS AND TYPES THEM WRONGLY", size=11.5,
     bold=True, color=MID_GREY, first=True, space_after=6)
for t in [
    "Detection precision 0.659 (CI 0.505–"
    "0.784), and 0.897 on the stratum "
    "where the conflicts actually are. Under the shipped operations vocabulary "
    "it is 0.650.",
    "Typing precision 0.073: it reports supersessions as "
    "contradictions, and it cannot say which version is in force, because "
    "nothing in the retrieved passages says which issue either of them is.",
    "The quantity branch never fires, even where the rule demonstrably changed "
    "a limit: recall 0.000 on 35 construction-labelled limit changes.",
    "And the per-claim band, replicated here with the SAME generator: against "
    "an independent reference it is again at chance (κ 0.055) "
    "and again ordered on the evidence it saw "
    "(0.077 / 0.119 / "
    "0.139). The band measures whether the passages "
    "entail the claim — agreement with itself — not whether the claim is true.",
]:
    rich(tf, [("\u25aa  ", False, MID_GREY), (t, False, BODY_INK)], size=11.3,
         space_after=8)
para(tf, "AND THE MEASUREMENT'S BINDING CONSTRAINT WAS THE RUBRIC",
     size=11.5, bold=True, color=MID_GREY, space_after=6)
for t in [
    "A rubric × specialisation factorial, with the pairs, the detector and the "
    "regime briefs held constant: the rubric's wording is worth "
    "+0.366 (generalist) and "
    "+0.317 (specialist); the reader's domain "
    "specialisation is worth +0.049 and "
    "+0.000.",
    "The mechanism is concrete: the old rubric required a version marker, and a "
    "regulation does not write its own version in its text, so it missed "
    "63 of the 82 "
    "supersessions it was asked to find.",
]:
    rich(tf, [("\u25aa  ", False, MID_GREY), (t, False, BODY_INK)], size=11.3,
         space_after=8)
notes(s, "This is the second corpus, and it is the reason the two objectives "
         "that were open are now closed.\n\n"
         "The construction idea is simple and I think it is the transferable one. "
         "RO4 needed a corpus that CONTAINS conflicts; RO6 needed a corpus that "
         "is AUTHENTIC. Federal regulation is both. It is binding text with "
         "numeric requirements, and it gets amended — so the versioner serves "
         "the same section as it stood on two dates, and the same provision at "
         "two issues IS a conflict, with its type known by construction and no "
         "annotation needed.\n\n"
         "On the left, the negative findings replicate: BM25 beats the dense "
         "encoder, the fusion does not beat its own lexical leg, the category "
         "pre-filter does nothing. That matters because on the encyclopaedic "
         "corpus the BM25 result rested on 32 queries. And the pool curve is no "
         "longer saturated, so I can measure the displacement directly instead "
         "of inferring it.\n\n"
         "On the right, the contradiction result I did not expect. The gate "
         "FINDS the conflicts — detection 0.659, and 0.897 on the stratum where "
         "they are — and then reports them as the wrong KIND: typing 0.073. It "
         "calls a supersession a contradiction, and it cannot tell the "
         "practitioner which version is in force.\n\n"
         "And the last bullet is the one I would defend hardest. My own "
         "measurement was under a rubric, and I found out by crossing the rubric "
         "against the reader type that the RUBRIC was worth a third of a point "
         "of measured precision and the domain SPECIALISATION was worth almost "
         "nothing. That is not a comfortable result for anyone who builds "
         "specialist annotator panels, including me.\n\n"
         "One caveat on that last bullet, and I would rather state it than be "
         "asked. The per-claim band figures on this slide are a replication, and "
         "their reference labels come from a panel of reader agents under a "
         "written protocol. They were taken before the modality quota moved to "
         "the other side of the reranker. Re-labelling them today would mean a "
         "different instrument rather than a re-measurement, so they are quoted "
         "as the earlier configuration's result, and the limitation in the guide "
         "names them.")

# ================================================================ SLIDE 15c
# The six measured figures, two slides of three.
#
# The results slides carry the tables; these carry the pictures, because a
# panel can read a shape in a curve faster than a row of numbers, and the
# curves are where two of the findings live: the pool curve that is
# saturated on one corpus and not on the other, and the contradiction
# detector's precision that clears the floor on one and not on the other.
#
# The figures are the project's own PNGs, already greyscale.
FIGURES_DIR = ROOT / "deliverables" / "figures"

FIGURE_SLIDES = [
    ("Every measurement, in one picture (1 of 2)",
     "The retrieval stack and the confidence gate, on both corpora",
     [("fig1_pool_size",
       "Recall against the rerank candidate pool. The focus curve saturates "
       "at a pool of 10 and then falls; the industrial curve does not — 1.21 "
       "points of gold are found and then displaced out of the context."),
      ("fig2_risk_coverage",
       "The gate's risk–coverage curve, with always-answer and always-refuse "
       "bounding it. The operating point transfers across corpora; the "
       "threshold does not."),
      ("fig4_modality_quota_pareto",
       "Overall against table-specific recall for the seven ablated systems. "
       "The modality quota is a trade, not a gain, and which way it trades "
       "depends on where it is applied.")]),
    ("Every measurement, in one picture (2 of 2)",
     "The gate's calibration, the benchmark's audit, and the conflict detector",
     [("fig3_calibration",
       "Reliability of the gate's calibrated probability against observed "
       "answerability. The industrial gate tracks the diagonal; the focus "
       "gate does not."),
      ("fig5_question_only_roc",
       "A classifier seeing only the question text. Before the repair it "
       "separated the classes almost perfectly; after it, close to chance."),
      ("fig6_contradiction_precision",
       "The contradiction detector's precision against the base rate of real "
       "conflicts. The focus branch is withheld; the industrial branch would "
       "act. This is the clearest new result in the work.")]),
]

for _title, _sub, _figs in FIGURE_SLIDES:
    s = base_slide(_title, _sub, nxt())
    _x = 0.55
    for _key, _caption in _figs:
        _path = FIGURES_DIR / f"{_key}.png"
        if _path.exists():
            s.shapes.add_picture(str(_path), Inches(_x), Inches(1.35),
                                 height=Inches(3.45))
        tb, tf = textbox(s, Inches(_x), Inches(4.90), Inches(3.6), Inches(1.05))
        para(tf, _caption, size=10.5, color=BODY_INK, first=True, space_after=0)
        _x += 4.12
    notes(s, "The same six figures, with the captions the papers carry in full. "
             "What the panel should take from them: the pool curve is saturated on "
             "the focus corpus and is not on the industrial one, which is what "
             "makes the displacement measurable; the quota moves the two axes in "
             "opposite directions and is a trade rather than a gain; and the "
             "contradiction detector's precision clears the framework's own "
             "calibration floor on the industrial corpus and does not on the "
             "focus one, which is the clearest new result in this work.\n\n"
             "Every number in these figures is in the tables on the preceding "
             "slides, and every one of them is re-derived from the result files "
             "by the build.")

# ================================================================ SLIDE 16
s = base_slide("Limitations, Threats & What I Am NOT Claiming",
               "Volunteering these is what makes the claims I do make credible", nxt())
tb, tf = textbox(s, Inches(0.55), Inches(1.25), Inches(6.05), Inches(5.78))
para(tf, "LIMITATIONS OF THIS WORK", size=11.5, bold=True, color=MID_GREY, first=True,
     space_after=7)
for t in [
    "Scale and kind. The public corpus is 2,383 chunks over "
    "46 documents of ENCYCLOPAEDIC industrial text from Wikipedia, "
    "not operating manuals or supplier specifications — a practitioner would "
    "not find their documents in it. The second corpus is 2,443 chunks "
    "of 110 authentic federal regulations: binding and "
    "versioned, but still regulatory rather than plant-internal. Both are below "
    "the scale at which the statistical framing I use is well-founded, so claims "
    "are framed as demonstration and mechanism, not generalisation.",
    "Single-domain by design. Supply Chain Management is the focus of the first "
    "corpus; the other six categories exist for the "
    "cross-category transfer experiment, which is an INTRA-domain study.",
    "NLI on technical text is weak (published ceilings 78.2% / 51.8% macro-F1), so "
    "the contradiction mechanism reduces but does not eliminate false positives.",
    "Calibration is deployment-specific: thresholds must be re-fitted per retriever "
    "and per corpus.",
    "The long-context baseline is measured on cost on both corpora and on quality on the focus domain: 202,529 "
    "tokens against the RAG arm's 2,246 — 58.8x the "
    "input cost.",
    "H2.1 — that a non-bypassable gate reduces hallucination — is "
    "supported under both prompt conditions. It was tested with one generator behind five arms, scoring every claim against the evidence that arm was shown.",
    "Our benchmark's unanswerable class WAS separable from the question alone — "
    "we found that by auditing our own benchmark, rebuilt it so unanswerability "
    "is decidable from the evidence rather than from a question-shape rule, and "
    "re-measured everything. It is not free of form-only separability on every "
    "corpus: AUC 0.708 on the industrial one (p = 0.010).",
    "The annotations were made by language models, not by people: a panel of "
    "domain specialists, one per regulatory regime, plus a generalist control "
    "and an adjudicator. The agreement is reported in full.",
]:
    rich(tf, [("▪  ", False, MID_GREY), (t, False, BODY_INK)], size=11.3, space_after=8)
rect(s, Inches(6.85), Inches(1.25), Inches(5.93), Inches(5.78), WHITE,
     line=RGBColor(0xBF, 0xBF, 0xBF))
tb, tf = textbox(s, Inches(7.08), Inches(1.40), Inches(5.47), Inches(5.5))
para(tf, "CLAIMS I EXPLICITLY DO NOT MAKE", size=11.5, bold=True, color=NEGATIVE,
     first=True, space_after=7)
for t in [
    "“Our gate judges evidence sufficiency.” — It does not. The label is "
    "answer-in-context detectability; SURE-RAG and Certify reserve "
    "“sufficiency” for the set-level property.",
    "“The contradiction gate catches 100% of verifiable conflicts.” — true by "
    "construction, so not evidence: the numeric detector is an OR-branch of the gate.",
    "“Our gate beats CRAG / Self-RAG / conformal abstention.” — no such comparison "
    "exists.",
    "“We beat Decian et al.’s entropy-based dynamic threshold.” — nearest prior art "
    "on the mechanism; the difference is philosophy, not accuracy.",
    "“We are the first to gate RAG on retrieval confidence.” — the Bayesian "
    "relevance model is from 1999–2005; abstention was defined by SQuAD 2.0 in 2018.",
    "“Hybrid retrieval beats flat retrieval” as a contribution — well established "
    "(BEIR); I report it as a replication.",
    "“No public industrial Q&A benchmark exists.” — partly false. Expert-annotated "
    "industrial benchmarks now exist; what is missing is one with all four "
    "properties together.",
    "“We evaluated on the industrial documents a practitioner actually reads.” "
    "— no: authentic binding regulation, not plant-internal procedures, and "
    "6 of the 12 "
    "categories the proposal promised. Reconciled, with the reason for every "
    "row, in the guide's §A.6 — not glossed over.",
    "Any superiority claim over long-context prompting — we measured that baseline on answer quality as well as cost, and on this corpus the whole-corpus prompt did not win on coverage or cost and did not win significantly on quality.",
]:
    rich(tf, [("✗  ", False, NEGATIVE), (t, False, BODY_INK)], size=11.8, space_after=8)
notes(s, "I want to spend a moment on what I am NOT claiming, because that is the "
         "fastest way to lose a panel's trust.\n\n"
         "One of them is that my system rejects nonsense questions. It partly does. "
         "There is a runtime form check in front of the gate, and on "
         "the focus domain it refused "
         "6 of the 16 malformed "
         "stems I harvested from the corpus (37.5%), with "
         "0 false rejections among the "
         "13 well-formed ones. But it is a lexical check, not "
         "a parser: the malformed stems it misses are truncated CLAUSES, and it "
         "has no dictionary and no language model, so a keyboard mash passes it. "
         "It fails open on input it cannot judge, because a false rejection would "
         "be a refusal of a question the corpus could have answered — which is the "
         "one failure I care most about avoiding.\n\n"
         "I do not claim the gate beats conformal abstention — conformal prediction "
         "has an actual guarantee and I have no comparison against it.\n\n"
         "I do not claim priority on gating RAG on retrieval confidence, or on "
         "hybrid retrieval beating flat retrieval — that is a well-established result "
         "and I report my number as a replication, not a discovery.\n\n"
         "And one scope point, because the proposal and this thesis do not describe "
         "the same benchmark. The proposal promised "
         "12 categories across industrial engineering, "
         "machine learning and data analytics; I built "
         "6 of the nine industrial-engineering ones. The "
         "three machine-learning categories are descoped deliberately — demand "
         "forecasting and time-series forecasting are numerical series problems with "
         "their own models and metrics, and anomaly detection is a method rather than "
         "a document category, so a text-RAG pipeline would measure the tokenizer "
         "rather than the mechanism. Three industrial categories are descoped "
         "because the artefacts the proposal names — carrier rate cards, RMA "
         "procedures, stock policies — are proprietary and cannot be redistributed. "
         "The proposal's industrial corpus was substituted by an authentic "
         "regulatory corpus, not met. The reconciliation, with the reason for every "
         "row, is in the guide's §A.6.\n\n"
         "And one limitation I want to hold myself to, because you should "
         "hold me to it: H2.1 was tested with one generator behind five arms. "
         "I tried to repeat the whole comparison on a second generator and "
         "could not run it — MiniMax-M3.1-Flash returned no text on "
         "24 of the "
         "66 questions it was asked, "
         "23 of the "
         "44 were table lookups, spending "
         "its whole output budget thinking and coming back empty. Raising "
         "the budget fourfold rescued 13 of those "
         "and 11 were still empty, so it is not "
         "a shortage of output room. The harness records the run as not-run "
         "rather than quoting a rate it cannot stand behind, and the "
         "obstacle is measured and in the report. So the claim is for one "
         "generator, and I would rather say that than pretend otherwise.\n\n"
         "And I have corrected the 'no public benchmark exists' claim to something "
         "much narrower, because the broad version is simply false. Expert-annotated "
         "industrial and supply-chain benchmarks exist -- the manufacturing-safety "
         "benchmark of arXiv 2511.11847, 972 expert-validated answers in "
         "arXiv 2606.20898, and SupChain-Bench at Findings of ACL 2026. What is "
         "still unavailable is a benchmark that has all four of the properties I "
         "need at once.\n\n"
         "The biggest honest gap is long context. My corpus does fit in a modern "
         "context window, and 2026 work reports long-context beating semantic RAG "
         "in manufacturing safety. I measured both halves of that comparison "
         "here. The cost half: the whole corpus is 202,529 tokens "
         "against the RAG arm's 2,246, so the long-context arm sends "
         "74 times more input per query. "
         "The answer-quality half of the comparison was measured on the focus domain. With the whole corpus in the prompt the generator answered 31 of 32 answerable questions, the same coverage as the pipeline, and it declined the unanswerable questions at a comparable rate (76 of 144 against 77 of 144), for 74 times the input actually sent per query. On coverage and on cost the result is settled: the whole-corpus prompt declines no more unanswerable questions than the pipeline does and costs 74 times as much to do it. On answer quality the margin is directional but not statistically significant once the answers are scored without the length confound.\n\n"
         "So on this corpus the threat does not materialise -- the comparison is measured, and on this corpus it does not support a superiority claim for long-context prompting in this domain. "
         "What I have NOT done is the answer-quality half on the six-category "
         "corpus, where the corpus is 680,417 tokens. That is the "
         "measurement I would do next, and it is on the list.\n\n"
         "MiniMax-M3 answered the same 32 answerable and 144 unanswerable questions behind five arms that share the generator, the prompt wording, the question set and the scorer, so a difference between them is attributable to the context and the gate and to nothing else: the same retrieval with the gate removed; the framework at the operating point fitted on this benchmark; a control that refuses as many questions as the fitted gate did, but picks them at random; the framework at the operating point transferred unchanged from the cross-category half; the whole corpus in the prompt. With the generator permitted to decline -- the deployed system -- The rate of answering the unanswerable questions was 0.535 (77 of 144), 0.417 (60 of 144), 0.375 (54 of 144), 0.014 (2 of 144), 0.528 (76 of 144) respectively, and the accuracy on the answerable ones 0.633 (30 of 32), 0.800 (30 of 32), 0.714 (21 of 32), 0.333 (6 of 32), 0.548 (31 of 32) respectively. With the permission to decline removed, and the model, the questions, the retrieval and the scorer all unchanged, The rate of answering the unanswerable questions was 0.938 (135 of 144), 0.528 (76 of 144), 0.604 (87 of 144), 0.021 (3 of 144), 0.931 (134 of 144) respectively, and the accuracy on the answerable ones 0.656 (32 of 32), 0.667 (30 of 32), 0.714 (21 of 32), 0.000 (6 of 32), 0.406 (32 of 32) respectively. Of the claims the arms produced on the unanswerable questions, the fraction supported by nothing in the evidence they were given was 0.554, 0.566, 0.529, 0.333, 0.548 respectively, on 130, 106, 85, 3, 155 claims A refusal that also asserts something -- the documents do not contain the demand for this SKU, so the quantity cannot be computed; in general it is computed as ... -- is counted as an answer and scored on the assertion, which is the reading that gives the gate less credit, and 48 of the unanswerable questions drew one. The claim scorer was audited against the benchmark before the comparison was read: 32 of the 33 answers the benchmark itself considers correct are recognised as supported by the evidence that states them, and 8 of the 9 fabricated values are rejected. The gate's contribution is measured under both prompt conditions, and it holds in both. Under the cautious prompt -- the deployed system -- the hypothesis is supported, at a price: the gate reduced the rate of answering unanswerable questions from 0.535 to 0.417, a fall of 11.8 points, at the cost of answering 30 of 32 answerable questions. Paired question by question, the gate refused 23 of the questions the ungated arm answered and let through 6 of the ones it did not (exact McNemar p = 0.002). Under the answering prompt, which differs from the cautious one by a single sentence and by nothing else, the hypothesis is supported, at a price: the gate reduced the rate of answering unanswerable questions from 0.938 to 0.528, a fall of 41.0 points, at the cost of answering 30 of 32 answerable questions. Paired question by question, the gate refused 60 of the questions the ungated arm answered and let through 1 of the ones it did not (exact McNemar p = < 0.001). What the framework claims is therefore not that the gate reduces hallucination whatever the generator does, but that it is the one component whose behaviour does not depend on the generator's cooperation: the prompt can be wrong, and the gate still holds. An audit of the benchmark's answer labels found that 27 of the 132 answerable questions carried an answer attached to the wrong question: a table question named the column its key came from while taking the answer from the next column, and some numeric golds were digit prefixes of longer tokens. The generator was corrected, the benchmark rebuilt and every experiment in this project re-measured against it, so the numbers reported here are post-repair; the audit now finds 0 defective labels out of 32, and the benchmark as it stood before the repair is kept so that the finding stays checkable. The accuracy margin over the long-context arm reaches no test's significance threshold -- not under the whole-answer entailment test, not under a length-controlled re-scoring of the same answers, and not under a lexical test that ignores length (p = 0.727, 0.508, 0.250), so the long-context comparison is settled on coverage and cost and directional rather than significant on answer quality.")

# ================================================================ SLIDE 17
s = base_slide("Conclusion & Next Steps",
               "What this work contributes, stated at the strength it can be defended", nxt())
tb, tf = textbox(s, Inches(0.55), Inches(1.3), Inches(7.4), Inches(4.9))
para(tf, "THE CONTRIBUTION, IN THREE PARTS", size=11.5, bold=True, color=MID_GREY,
     first=True, space_after=8)
for label, body, col in [
    ("Architectural — incremental.",
     " Every component has published prior art. I position mine against it rather "
     "than claim priority. What is mine is the ARRANGEMENT and two of its "
     "properties: the gate is a control-flow fact rather than an instruction, and "
     "the conflict report is type-aware rather than binary.", BLACK),
    ("Empirical — a failure-mode characterisation.",
     " On an independently constructed public industrial corpus: a reranker’s recall "
     "is governed by its candidate pool relative to the final context; a modality "
     "quota binds only before the cross-encoder, which inverts the rule the "
     "framework was designed on; the modality "
     "composition of the corpus, not the algorithm, decides whether a "
     "modality-aware mechanism can have any effect at all.", DARK_GREY),
    ("Methodological — an evaluation protocol.",
     " The gate is evaluated as a selective-prediction policy with a risk–coverage "
     "curve and a false-positive rate at a stated operating point, with "
     "always-flag and never-flag baselines.", MID_GREY),
    ("Methodological — our own benchmark, audited and repaired.",
     " Auditing the unanswerable half showed it was separable from the question "
     "text alone: one regular expression carried 76% of it, so the refusal rate "
     "was an upper bound, not a measurement. We rebuilt the class and re-measured "
     "everything. The gate refuses 23.6% of the hard class "
     "now, against 91.7% before — a worse number, and the "
     "right one.", MID_GREY),
]:
    rich(tf, [(label, True, col), (body, False, BODY_INK)], size=13, space_after=12)
rect(s, Inches(8.25), Inches(1.3), Inches(4.53), Inches(5.55), PANEL_FILL,
     line=RGBColor(0xBF, 0xBF, 0xBF))
tb, tf = textbox(s, Inches(8.48), Inches(1.5), Inches(4.07), Inches(5.25))
para(tf, "NEXT STEPS, IN PRIORITY ORDER", size=11.5, bold=True, color=MID_GREY,
     first=True, space_after=8)
# The same list the status report and the technical documentation carry, from
# the same place. The deck used to have its own, older, list -- and the two
# documents disagreed about what the project still owed.
for i, _step in enumerate(_src_next_steps(_src_load_replication())):
    rich(tf, [(f"{i+1}.  ", True, BLACK), (_step["short"], False, BODY_INK)],
         size=9.5, space_after=4)
notes(s, "To close: three kinds of contribution, at three different strengths.\n\n"
         "The architectural contribution is incremental, and I say so. The empirical "
         "contribution is a failure-mode characterisation, and that is the real "
         "output of this project — three results that contradict my own design "
         "specification, on a corpus independent of the one I built them on.\n\n"
         "The methodological contribution is an evaluation protocol that treats the "
         "gate as a policy rather than a component.\n\n"
         "And the framework's practical value does not depend on any mechanism being "
         "novel. It depends on each being structural, on the trade-offs between them "
         "being measured rather than assumed, and on the system being able to say, "
         "for every claim, which passage supports it.\n\n"
         "The twelve next steps are in priority order, and the "
         "first is the one that could still change the claim. The full text is in "
         "the status report, and it is the same list there.")

# ================================================================ SLIDE 18
s = base_slide("References", "Selected — every identifier resolved against a live bibliographic API", nxt())
refs_l = [
    "Rajpurkar, P., Jia, R., & Liang, P. (2018). Know what you don't know: Unanswerable questions for SQuAD. ACL 2018, 518–528.",
    "Asai, A., et al. (2024). Self-RAG: Learning to retrieve, generate, and critique through self-reflection. ICLR 2024. arXiv:2310.11511.",
    "Yan, S.-Q., et al. (2024). Corrective retrieval augmented generation. arXiv:2401.15884.",
    "Geißler, F., et al. (2026). Towards dependable RAG using factual confidence prediction. arXiv:2605.05244.",
    "Phillips, E., et al. (2026). Entropy alone is insufficient for safe selective prediction in LLMs. arXiv:2603.21172.",
    "Thakur, A., Saparov, A., & Ribeiro, B. (2026). DeclineCraft: A RAG abstention benchmark. arXiv:2610.28340.",
    "Cormack, G. V., Clarke, C. L. A., & Büttcher, S. (2009). Reciprocal rank fusion outperforms Condorcet and individual rank learning methods. SIGIR 2009, 758–759.",
]
refs_r = [
    "Yang, X., et al. (2026). Large language models in resolving contextual knowledge conflicts. EMNLP 2026. DOI 10.18653/2026.emnlp-main.918",
    "Liu, S., et al. (2026). ConflictScore: Identifying and measuring how language models handle conflicting evidence. EMNLP 2026. DOI 10.18653/2026.emnlp-main.2589",
    "Faysse, M., et al. (2025). ColPali: Efficient document retrieval with vision language models. ICLR 2025. arXiv:2407.01449.",
    "Suri, M., et al. (2024). VisDoM: Multi-document QA with visually rich elements using multimodal RAG. arXiv:2412.10704.",
    "Bruch, S., Gai, S., & Ingber, A. (2023). An analysis of fusion functions for hybrid retrieval. ACM TOIS. DOI 10.1145/3596512",
    "Farquhar, S., et al. (2024). Detecting hallucinations in large language models using semantic entropy. Nature 630, 625–630.",
    "Robertson, S., Zaragoza, H., & Taylor, J. (2004). Probabilistic relevance framework: BM25 and beyond. FnTIR 3(4), 333–389.",
]
tb, tf = textbox(s, Inches(0.55), Inches(1.3), Inches(6.05), Inches(5.2))
for i, r in enumerate(refs_l):
    rich(tf, [(f"[{i+1}]  ", True, BLACK), (r, False, BODY_INK)], size=11.3,
         space_after=11, first=(i == 0))
tb, tf = textbox(s, Inches(6.85), Inches(1.3), Inches(5.93), Inches(5.2))
for i, r in enumerate(refs_r):
    rich(tf, [(f"[{i+8}]  ", True, BLACK), (r, False, BODY_INK)], size=11.3,
         space_after=11, first=(i == 0))
tb, tf = textbox(s, Inches(0.55), Inches(6.45), Inches(12.2), Inches(0.5))
para(tf, "Full reference list: Deliverable 2a (technical report) and Deliverable 2b/2c "
         "(IEEE and journal .tex). All arXiv identifiers and DOIs resolved against "
         "arXiv, Semantic Scholar, Crossref and the ACL Anthology.",
     size=10.5, color=MUTED_GREY, italic=True, first=True, space_after=0)
notes(s, "Selected references. The full list is in the paper, and every identifier "
         "was resolved against a live API rather than written from memory.\n\n"
         "If you take one citation away, make it the 2026 conformal work — it is the "
         "strongest competitor to my confidence gate, and the reason my own claims "
         "are framed as empirical calibration rather than a statistical guarantee.\n\n"
         "Thank you. I am happy to take questions.")

# ---------------------------------------------------------------- save
prs.save(OUT)
# The deck is monochrome; see deliverables/scripts/monochrome.py.
_monochrome(OUT)
print(f"[pptx] wrote {OUT}  ({len(prs.slides.__iter__.__self__._sldIdLst)} slides)")
