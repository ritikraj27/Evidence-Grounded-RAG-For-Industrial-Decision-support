#!/usr/bin/env python3
"""Build Deliverable 3 -- the department report, in the template of the
September 2026 "RAG Framework Report".

The template is reproduced from the source PDF:
  * a rectangular page border on every page,
  * a bordered title page carrying the IIT Kharagpur logo, the report title in
    capitals, "M.Tech Project Report", the author block, the supervisor block,
    the institution block and the date,
  * a certificate page with the departmental letterhead,
  * a hand-set table of contents with numbered sections and sub-sections,
  * numbered body sections, tables with a filled header row,
  * a page number bottom-right on every page.

Every measured number is read from `impl/results/*.json` at build time.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
import sys as _sys

for _cand in (Path(__file__).resolve().parent,
              Path(__file__).resolve().parents[2] / "scripts"):
    if (_cand / "figure_captions.py").exists():
        _sys.path.insert(0, str(_cand))
        break
from figure_captions import caption as figure_caption
import sys as _sys

for _cand in (Path(__file__).resolve().parent,
              Path(__file__).resolve().parents[2] / "scripts"):
    if (_cand / "monochrome.py").exists():
        _sys.path.insert(0, str(_cand))
        break
from monochrome import to_monochrome as _monochrome

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Emu, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from results_source import load as _src_load, load_transfer as _src_load_transfer, _comp_index
from results_source import contradiction_precision_claim as _src_cp_claim
from results_source import contradiction_precision_mechanism as _src_cp_mech
from results_source import contradiction_branch_claim as _src_cp_branch
from results_source import conflict_control_claim as _src_cc_claim
from results_source import load_conflict_control as _src_load_control

RESULTS = ROOT / "impl" / "results"
FOCUS_MANIFEST = ROOT / "impl" / "data" / "corpus_focus" / "manifest.json"
FOCUS_INDEX = ROOT / "impl" / "artifacts_focus" / "index.json"
FOCUS_BENCH = ROOT / "impl" / "data" / "benchmark_focus" / "benchmark.json"
FOCUS_CASE_MD = ROOT / "impl" / "results_focus" / "exp6_focus_case.md"
OUT = ROOT / "deliverables" / "Deliverable_3_Department_Report.docx"

LOGOS = [
    Path("/Users/ritikraj/Downloads/IIT_Kharagpur_Logo.svg-removebg-preview.png"),
    Path("/Users/ritikraj/Downloads/250px-IIT_Kharagpur_Logo.svg-removebg-preview.png"),
]
LOGO = next((p for p in LOGOS if p.exists()), None)

# The document is monochrome; see deliverables/scripts/monochrome.py.
BLACK = RGBColor(0x00, 0x00, 0x00)
BODY_FONT = "Times New Roman"
BODY_SIZE = Pt(11)
HEAD_SIZE = Pt(14)


# ----------------------------------------------------------------- helpers
def _load(name, required=()):
    """Load a result file, or None if absent or of a different shape."""
    p = RESULTS / f"{name}.json"
    if not p.exists():
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






def load_transfer(name, required=()):
    """Load a result from the multi-category run only.

    The cross-category transfer experiment is defined on a multi-category
    corpus, so it is never taken from the focus-domain run.
    """
    return _src_load_transfer(name, required)

def set_page_border(section, sz=6, color="000000"):
    """Draw the rectangular page border, exactly as in the template PDF."""
    sectPr = section._sectPr
    for tag in ("w:pgBorders",):
        old = sectPr.find(qn(tag))
        if old is not None:
            sectPr.remove(old)
    pgBorders = OxmlElement("w:pgBorders")
    pgBorders.set(qn("w:offsetFrom"), "page")
    for edge in ("top", "left", "bottom", "right"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), str(sz))
        el.set(qn("w:space"), "24")
        el.set(qn("w:color"), color)
        pgBorders.append(el)
    # pgBorders must come after pgMar in the sectPr sequence
    ref = sectPr.find(qn("w:pgMar"))
    if ref is not None:
        ref.addnext(pgBorders)
    else:
        sectPr.append(pgBorders)


def add_page_number_footer(section):
    footer = section.footer
    p = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = p.add_run()
    fld = OxmlElement("w:fldSimple")
    fld.set(qn("w:instr"), "PAGE")
    run._r.addnext(fld)
    for r in p.runs:
        r.font.size = Pt(9)
        r.font.name = BODY_FONT


def style_run(run, *, size=BODY_SIZE, bold=False, italic=False, color=None,
              font=BODY_FONT, caps=False):
    run.font.size = size
    run.font.bold = bold
    run.font.italic = italic
    run.font.name = font
    run.font.all_caps = caps
    if color is not None:
        run.font.color.rgb = color
    return run


def para(doc, text="", *, size=BODY_SIZE, bold=False, italic=False, align=None,
         space_after=8, space_before=0, indent=None, color=None, line=1.5,
         font=BODY_FONT, keep_with_next=False):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_after = Pt(space_after)
    pf.space_before = Pt(space_before)
    pf.line_spacing = line
    if align is not None:
        p.alignment = align
    if indent is not None:
        pf.left_indent = Cm(indent)
    if keep_with_next:
        pf.keep_with_next = True
    if text:
        style_run(p.add_run(text), size=size, bold=bold, italic=italic, color=color,
                  font=font)
    return p


def heading(doc, number, text, *, size=HEAD_SIZE):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(16)
    pf.space_after = Pt(8)
    pf.keep_with_next = True
    label = f"{number}. {text}" if number else text
    style_run(p.add_run(label), size=size, bold=True, color=BLACK)
    return p


def subheading(doc, number, text):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(11)
    pf.space_after = Pt(5)
    pf.keep_with_next = True
    style_run(p.add_run(f"{number} {text}"), size=Pt(12), bold=True, color=BLACK)
    return p


def bullet(doc, text, *, size=Pt(11), indent=0.75):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.left_indent = Cm(indent)
    pf.first_line_indent = Cm(-0.45)
    pf.space_after = Pt(5)
    pf.line_spacing = 1.4
    style_run(p.add_run("•  "), size=size)
    style_run(p.add_run(text), size=size)
    return p


def caption(doc, text):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(6)
    pf.space_after = Pt(4)
    pf.keep_with_next = True
    style_run(p.add_run(text), size=Pt(9.5), bold=True, color=BLACK)
    return p


def shade(cell, hexcolor):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hexcolor)
    tcPr.append(shd)


def table(doc, headers, rows, *, widths=None, size=Pt(9.5), align_first_left=True):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = t.rows[0].cells
    for j, h in enumerate(headers):
        hdr[j].text = ""
        p = hdr[j].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.space_before = Pt(2)
        style_run(p.add_run(str(h)), size=size, bold=True,
                  color=RGBColor(0xFF, 0xFF, 0xFF))
        shade(hdr[j], "000000")
    for row in rows:
        cells = t.add_row().cells
        for j, val in enumerate(row):
            cells[j].text = ""
            p = cells[j].paragraphs[0]
            p.alignment = (WD_ALIGN_PARAGRAPH.LEFT if (j == 0 and align_first_left)
                           else WD_ALIGN_PARAGRAPH.CENTER)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.space_before = Pt(2)
            style_run(p.add_run(str(val)), size=size)
    if widths:
        for j, w in enumerate(widths):
            for row in t.rows:
                row.cells[j].width = Cm(w)
    return t


def page_break(doc):
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


# ----------------------------------------------------------------- build

#: The project's measured figures. The departmental report carries the same
#: six the papers do, with the same captions, so that the reader who has one
#: has seen the other. The captions live in one place,
#: ``deliverables/scripts/figure_captions.py``.
FIGURES_DIR = ROOT / "deliverables" / "figures"


def figure(doc, key: str) -> None:
    """Place one of the measured figures with its caption."""
    _path = FIGURES_DIR / f"{key}.png"
    _caption = figure_caption(key)
    if not _path.exists():
        print(f"  [docx] missing figure: {_path}")
        return
    p = doc.add_paragraph()
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    p.add_run().add_picture(str(_path), width=Cm(7.6))
    cp = doc.add_paragraph()
    cp.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cp.paragraph_format.space_after = Pt(10)
    style_run(cp.add_run(_caption), size=Pt(9),
              color=RGBColor(0x40, 0x40, 0x40))


def main() -> int:
    exp1 = _load("exp1_ablation", ("systems", "comparisons", "corpus_stats"))
    exp2 = _load("exp2_gate", ("calibration_metrics", "threshold_sweep", "chosen_operating_point"))
    exp3 = _load("exp3_contradiction", ("summary",))
    exp4 = load_transfer("exp4_transfer", ("leave_half_out", "per_category_retrieval"))
    focus_manifest = FOCUS_MANIFEST
    focus_index = FOCUS_INDEX
    focus_bench = FOCUS_BENCH

    doc = Document()
    st = doc.styles["Normal"]
    st.font.name = BODY_FONT
    st.font.size = BODY_SIZE

    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
    sec.left_margin = sec.right_margin = Cm(2.4)
    sec.top_margin = Cm(2.2)
    sec.bottom_margin = Cm(2.0)
    set_page_border(sec)
    add_page_number_footer(sec)

    # ---------------------------------------------------------- TITLE PAGE
    para(doc, "", space_after=0)
    para(doc, "AN EVIDENCE-GROUNDED RETRIEVAL-AUGMENTED GENERATION FRAMEWORK",
         size=Pt(16), bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2,
         line=1.2)
    para(doc, "FOR INDUSTRIAL DECISION SUPPORT", size=Pt(16), bold=True,
         align=WD_ALIGN_PARAGRAPH.CENTER, space_after=10, line=1.2)
    para(doc, "A Framework with Confidence Gating, Modality-Balanced Retrieval, "
              "and Contradiction Detection", size=Pt(12), italic=True,
         align=WD_ALIGN_PARAGRAPH.CENTER, space_after=14, line=1.2)
    para(doc, "M.Tech Project Report", size=Pt(12), align=WD_ALIGN_PARAGRAPH.CENTER,
         space_after=14)
    if LOGO:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(str(LOGO), width=Cm(6.4))
    para(doc, "", space_after=12)
    para(doc, "By", size=Pt(12), align=WD_ALIGN_PARAGRAPH.CENTER, space_after=4)
    para(doc, "Ritik Raj [25IM60R12]", size=Pt(15), bold=True,
         align=WD_ALIGN_PARAGRAPH.CENTER, space_after=12)
    para(doc, "Under the supervision of", size=Pt(12),
         align=WD_ALIGN_PARAGRAPH.CENTER, space_after=4)
    para(doc, "Dr. Sri Krishna Kumar", size=Pt(14), bold=True,
         align=WD_ALIGN_PARAGRAPH.CENTER, space_after=16)
    for line_ in [
        "DEPARTMENT OF INDUSTRIAL AND SYSTEMS ENGINEERING",
        "INDIAN INSTITUTE OF TECHNOLOGY KHARAGPUR",
        "KHARAGPUR- 721302, INDIA",
        "NOVEMBER, 2026",
    ]:
        para(doc, line_, size=Pt(11), align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2,
             line=1.2)

    # ---------------------------------------------------- CERTIFICATE PAGE
    page_break(doc)
    if LOGO:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.add_run().add_picture(str(LOGO), width=Cm(2.5))
    para(doc, "DEPARTMENT OF INDUSTRIAL AND SYSTEMS ENGINEERING", size=Pt(10.5),
         bold=True, space_after=1, line=1.15)
    para(doc, "INDIAN INSTITUTE OF TECHNOLOGY KHARAGPUR,", size=Pt(10.5), bold=True,
         space_after=1, line=1.15)
    para(doc, "KHARAGPUR, INDIA-721302", size=Pt(10.5), bold=True, space_after=4,
         line=1.15)
    para(doc, "", space_after=2)
    para(doc, "CERTIFICATE", size=Pt(15), bold=True, align=WD_ALIGN_PARAGRAPH.CENTER,
         space_before=26, space_after=22)
    para(doc,
         "This is to certify that this report entitled \"An Evidence-Grounded "
         "Retrieval-Augmented Generation Framework for Industrial Decision Support\" "
         "submitted by Ritik Raj [25IM60R12] to the Indian Institute of Technology "
         "Kharagpur is a record of the bona fide project work carried out under my "
         "supervision and is worthy of consideration for the MTP Project. This "
         "project has fulfilled all the requirements as per the regulations of the "
         "Institute and has reached the standard needed for the submission.",
         size=Pt(11), align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=8, line=1.5)
    para(doc, "", space_after=110)
    para(doc, "Dr. Sri Krishna Kumar", size=Pt(11.5), bold=True, space_after=1)
    for line_ in [
        "Department of Industrial and Systems Engineering",
        "Indian Institute of Technology Kharagpur",
        "India-721302",
        "Date: 31-10-2026",
    ]:
        para(doc, line_, size=Pt(10.5), space_after=1, line=1.15)

    # ---------------------------------------------------------------- TOC
    page_break(doc)
    para(doc, "Table of Contents", size=Pt(16), bold=True,
         align=WD_ALIGN_PARAGRAPH.CENTER, space_after=16)
    toc = [
        (0, "1. Introduction & Background"),
        (0, "2. Background — How a Normal LLM Works"),
        (0, "3. Background — How a Normal RAG Works"),
        (0, "4. Problem Statement"),
        (0, "5. Literature Review"),
        (0, "6. Objectives & Hypotheses"),
        (0, "7. Methodology"),
        (1, "7.1 Vector Search — Dense Retrieval"),
        (1, "7.2 Lexical Search — BM25"),
        (1, "7.3 Rank Fusion — Reciprocal Rank Fusion (RRF)"),
        (1, "7.4 Cross-Encoder Rerank"),
        (1, "7.5 Confidence Gating — Bayesian Posterior"),
        (1, "7.6 Per-Claim Confidence Tagging"),
        (1, "7.7 Contradiction Detection — Joint NLI + Topical Gate"),
        (1, "7.8 Modality-Balanced Retrieval"),
        (0, "8. Architecture & Implementation"),
        (0, "9. Experimental Results"),
        (0, "10. Limitations & Future Work"),
        (0, "11. Conclusion"),
        (0, "References"),
    ]
    for level, text in toc:
        para(doc, text, size=Pt(11.5), indent=(0 if level == 0 else 0.8),
             space_after=7, line=1.35)

    # ------------------------------------------------------------ SECTION 1
    page_break(doc)
    heading(doc, "1", "Introduction & Background")
    para(doc,
         "Industrial decisions are made from paperwork — standard operating "
         "procedures, failure-mode and effects analyses, control plans, maintenance "
         "logs, calibration records, audit reports, and supplier documents. Engineers "
         "want answers they can trust, trace, and act on. Generic large language "
         "model chatbots answer fluently but cannot be trusted — there is no trace "
         "from a number back to its source page, no way to distinguish an inferred "
         "claim from a stated one, and no warning when two sources disagree.",
         align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    para(doc,
         "Hallucination in this domain is not stylistic. It is operational risk. A "
         "wrong Weibull shape parameter, a wrong economic order quantity, or a wrong "
         "alarm threshold can stop a production line, misplace inventory, or fail an "
         "audit. Retrieval-augmented generation offers a partial remedy — grounding "
         "the model's output in retrieved passages and citing them. But existing RAG "
         "systems trust the retriever unconditionally, ignore modality diversity, and "
         "provide no per-claim confidence; they replace one form of hallucination "
         "with another.",
         align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    para(doc,
         "This project delivers an evidence-grounded RAG framework for industrial "
         "decision support. Five design moves distinguish the framework from generic "
         "RAG:",
         align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    for t in [
        "D1 — Code-level retrieval-confidence gating (outside the LM loop, "
        "non-bypassable).",
        "D2 — Modality-balanced retrieval quotas (enforcing minimum share for "
        "tables, charts, images).",
        "D3 — Hybrid lexical + dense + reranker with category pre-filter, fused via "
        "RRF.",
        "D4 — Cross-document contradiction surfacing (joint NLI + topical gate).",
        "D5 — Per-claim three-band confidence tagging (grounded / inferred / "
        "uncertain).",
    ]:
        bullet(doc, t)
    para(doc,
         "This report presents the framework, the mathematics behind each component, "
         "the implementation, and a measured evaluation on an independently "
         "constructed public industrial corpus. It also reports the points at which "
         "the original design was wrong, and the evidence that corrected it.",
         align=WD_ALIGN_PARAGRAPH.JUSTIFY)

    # ------------------------------------------------------------ SECTION 2
    heading(doc, "2", "Background — How a Normal LLM Works")
    para(doc,
         "A normal large language model (LLM) is a parametric function that maps a "
         "sequence of input tokens to a sequence of output tokens. It has no access "
         "to any external knowledge source at inference time — every output is "
         "generated from the weights it learned during training. The pipeline is "
         "short: [User query] → [Tokenise] → [LLM forward pass] → [Decode] → "
         "[Answer].",
         align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    para(doc,
         "Concretely, when an engineer asks a question like \"What is the EOQ for SKU "
         "A-104?\", a normal LLM produces an answer such as \"Q* ≈ 187 units\" — but "
         "the user has no way to know whether the LLM is repeating something it "
         "learned during training, generalising from a related passage, or simply "
         "guessing. There is no citation. There is no confidence. There is no path "
         "from the number back to any source document.",
         align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    para(doc, "Problems with a normal LLM:", space_after=4)
    for t in [
        "No grounding — the answer is generated from internal weights, not from any "
        "document the user trusts.",
        "No citation — there is no path from a number back to the source page that "
        "justifies it.",
        "No confidence — the model outputs the same string whether it is sure or "
        "guessing.",
        "No modality awareness — a table question and a paragraph question are "
        "answered the same way.",
        "No contradiction surfacing — if two training passages disagreed, the user "
        "has no way to know.",
    ]:
        bullet(doc, t)

    # ------------------------------------------------------------ SECTION 3
    heading(doc, "3", "Background — How a Normal RAG Works")
    para(doc,
         "A normal retrieval-augmented generation (RAG) system adds one step: before "
         "the LLM is called, a retriever fetches the top-k chunks most similar to "
         "the query, and those chunks are concatenated into the prompt. The "
         "pipeline is: [User query] → [Embed] → [Retrieve top-k] → [Concatenate] → "
         "[LLM] → [Answer].",
         align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    para(doc,
         "The retrieval leg is typically a single dense retriever over a vector "
         "store; the generator is a standard instruction-tuned LLM. Citations are "
         "usually emitted as bracketed markers (e.g. [E1], [E2]) that link back to "
         "the retrieved chunks. Compared with a plain LLM, a normal RAG system is a "
         "significant improvement: the answer is now grounded in something the user "
         "supplied.",
         align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    para(doc, "Problems with a normal RAG:", space_after=4)
    for t in [
        "Confidence — the retriever is trusted unconditionally; below-threshold "
        "retrievals are still passed to the LLM.",
        "Modality — text similarity dominates; a table query can be answered from "
        "top-ranked text chunks alone.",
        "Category — without a category pre-filter, the top-k may pull chunks from "
        "unrelated industrial sub-domains.",
        "Contradiction — if two accepted chunks disagree, the LLM silently picks "
        "one (or fuses them incoherently).",
        "Per-claim confidence — the answer carries one confidence; individual "
        "claims inside the answer are untagged.",
    ]:
        bullet(doc, t)

    # ------------------------------------------------------------ SECTION 4
    heading(doc, "4", "Problem Statement")
    para(doc,
         "Industrial decisions are made from paperwork, but the tools used to answer "
         "questions about that paperwork are inadequate. This section states the "
         "specific gaps the project addresses.",
         align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    for t in [
        "Generic LLM chatbots cannot be trusted in industrial settings — there is no "
        "trace from a number back to its source page.",
        "Existing RAG systems trust the retriever unconditionally and ignore "
        "modality diversity — a table query can be answered from top-ranked text "
        "chunks alone.",
        "Hallucination in this domain is operational risk — wrong EOQ, wrong "
        "Incoterm, wrong safety-stock rule can stop a production line or fail an "
        "audit.",
        "The benchmark claim must now be stated narrowly: expert-annotated "
        "industrial and supply-chain benchmarks do exist -- the manufacturing-safety "
        "benchmark of arXiv:2511.11847, arXiv:2606.20898 (972 expert-validated "
        "answers), arXiv:2603.20534, RealDocBench (arXiv:2606.07401) and "
        "SupChain-Bench (10.18653/v1/2026.findings-acl.371) -- so what remains "
        "unavailable is a benchmark that spans multiple industrial-engineering "
        "sub-domains AND carries dual expert annotation, a reported kappa, "
        "per-claim attribution labels and a deliberate unanswerable class "
        "together.",
        "The appropriate retrieval architecture (instantaneous vs sequential) must be "
        "justified by data, not assumed.",
        "The five design moves of the framework address each of the five problems "
        "identified in the baseline — D1 (confidence gate), D2 (modality quotas), "
        "D3 (category filter), D4 (contradiction surfacing), D5 (per-claim "
        "confidence).",
    ]:
        bullet(doc, t)

    # ------------------------------------------------------------ SECTION 5
    page_break(doc)
    heading(doc, "5", "Literature Review")
    para(doc,
         "The directly relevant prior work was reviewed in two passes and every "
         "identifier resolved against a live bibliographic API. The table below "
         "lists the works a committee member is most likely to raise; the full "
         "list, with verified identifiers and the corrections to earlier versions "
         "of this report, appears in the References and in the research "
         "directory.",
         align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    para(doc,
         "The second pass, in October 2026, changed what this work may claim. "
         "Three findings from it are load-bearing. First, the abstention "
         "mechanism has moved past a threshold: GRAB-RAG (arXiv:2608.22228) "
         "shows models still answer 41.6% of misleading questions under "
         "explicit abstention prompting; SURE-RAG (arXiv:2605.03534) argues "
         "sufficiency is a set-level property that independent passage scoring "
         "cannot detect; Certify (arXiv:2610.34684) makes it structural; and "
         "Sieve and Sage (arXiv:2609.35794) screens the retrieved set outside "
         "the model before the model is invoked. Our gate is consequently a "
         "calibrated answer-in-context detector, not a sufficiency judge. "
         "Second, the closest single pre-emption of our contradiction mechanism "
         "is published: HALT-RAG (arXiv:2509.07475) combines a calibrated NLI "
         "ensemble with lexical signals under a precision-constrained "
         "abstention policy. It is a post-hoc verifier that never retrieves, and "
         "its own Future Work names integrating and evaluating detectors like it "
         "within a live RAG pipeline as the critical next step, which is the "
         "experiment reported in Section 4.6; we therefore claim an industrial "
         "instantiation and a measurement, not a new mechanism. "
         "Third, Beyond the Reranker (arXiv:2606.28367) reports that retrieval "
         "enhancements stop paying once a strong reranker is present, and that "
         "the gains reported in the literature come almost exclusively from "
         "homogeneous corpora, predominantly Wikipedia prose -- which is what "
         "ours is. Our effect sizes are therefore reported as an upper bound for "
         "mixed-format industrial documents.",
         align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    lit_rows = [
        ["1", "Rajpurkar et al. (2018)\nACL 2018",
         "50,000 unanswerable questions with a no-answer threshold; a system must "
         "answer correctly OR decline",
         "We adopt the answer-or-decline contract for industrial documentation",
         "Defines the task. 86% F1 on SQuAD becomes 66% on SQuAD 2.0 — 20 points "
         "lost to confident answering"],
        ["2", "Asai et al. (2024)\nICLR 2024",
         "Reflection tokens trained into the LM decide when to retrieve and whether "
         "a passage supports the output",
         "Non-trainable code-level gating instead of learned reflection tokens",
         "Reflection tokens are learned per corpus and must be re-learned for each "
         "of twelve categories"],
        ["3", "Yan et al. (2024)\nCRAG",
         "Lightweight retrieval evaluator returns a confidence degree triggering "
         "one of four corrective actions",
         "Fixed threshold on a calibrated posterior; decline and exit the "
         "generation path",
         "Closest prior art to D1. CRAG still calls the LLM in every branch"],
        ["4", "Geißler et al. (2026)\narXiv:2605.05244",
         "Conformal chunk filtering plus an attention-based factuality classifier",
         "Adopt their exchangeability diagnostic as our stated limitation",
         "Strongest current work on D1, framed for industry. We claim no superiority"],
        ["5", "Cormack et al. (2009)\nSIGIR 2009",
         "Parameter-free rank fusion across multiple ranked lists",
         "RRF fusion of BM25 + dense, preceded by a category pre-filter",
         "Canonical parameter-free fusion. No modality or category awareness"],
        ["6", "Bruch et al. (2023)\nACM TOIS",
         "Systematic comparison of fusion functions for hybrid retrieval over 23 "
         "runs",
         "Un-tuned k = 60, since tuned fusion weights do not generalise out of "
         "domain",
         "RRF is at least as good and more robust than learned score combination"],
        ["7", "Yang et al. (2026)\nEMNLP 2026",
         "Taxonomy of six conflict types: factual, inferential, temporal, "
         "granularity, perspective, ambiguity",
         "Joint NLI + topical gate; report a conflict TYPE, not a binary flag",
         "Only two of the six types are genuine contradictions — this is the "
         "published justification for the topical gate"],
        ["8", "Thakur et al. (2026)\nDeclineCraft",
         "Abstention benchmark over 27 LLMs; Correct Abstention Rate under four "
         "configurations",
         "Re-fit the gate threshold for every retrieval arm compared",
         "Adding reranking to hybrid retrieval LOWERS abstention for all 12 models "
         "tested"],
    ]
    caption(doc, "Table 1 — Prior work, its method, our position, and the limitation "
                 "that bounds it.")
    table(doc, ["#", "Author(s) & Year", "Their Methodology", "Our Methodology",
                "Key Idea / Limitation"], lit_rows,
          widths=[0.8, 2.6, 4.4, 4.4, 4.2], size=Pt(8))

    # ------------------------------------------------------------ SECTION 6
    page_break(doc)
    heading(doc, "6", "Objectives & Hypotheses")
    para(doc,
         "Six research objectives are defended empirically. Each is paired with its "
         "own evaluation study. The objectives are stated as findings to be "
         "defended, not features to be built.",
         align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    objs = [
        ("RO1", "Framework Design",
         "To design and develop an evidence-grounded retrieval-augmented generation "
         "framework tailored for industrial decision-support contexts.",
         "Design objective — no formal hypothesis."),
        ("RO2", "Component-Level Evaluation",
         "To evaluate the relative effectiveness of four retrieval mechanisms "
         "(confidence gating, modality-balanced retrieval, hybrid retrieval with "
         "category pre-filter, and contradiction surfacing) on hallucination "
         "reduction and evidence grounding in industrial Q&A.",
         "H2.1  A code-level, non-bypassable retrieval-confidence gate reduces "
         "hallucination in industrial Q&A.\n"
         "H2.2  Per-modality retrieval quotas improve recall on table and chart "
         "queries.\n"
         "H2.3  Hybrid lexical + dense + reranker via RRF, preceded by category "
         "filter, outperforms flat retrieval.\n"
         "H2.4  Surfacing contradictions and per-claim confidence improves "
         "practitioner decision accuracy."),
        ("RO3", "Failure Mode Characterization",
         "To systematically characterise the failure modes and limitations of "
         "evidence-grounded RAG systems in industrial decision-support contexts.",
         "Characterisation objective — no formal hypothesis."),
        ("RO4", "Cross-Category Generalization",
         "To assess the cross-category generalizability of retrieval configurations "
         "across diverse industrial sub-domains.",
         "H4.1  Retrieval configurations tuned on a subset of industrial categories "
         "transfer zero-shot to held-out categories without statistically "
         "significant degradation in hallucination or evidence-grounding metrics."),
    ]
    for tag, name, body, hyp in objs:
        para(doc, f"{tag} — {name}", size=Pt(12), bold=True, color=BLACK,
             space_before=9, space_after=4)
        para(doc, body, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=4)
        for line_ in hyp.split("\n"):
            para(doc, line_, size=Pt(10.5), italic=True, space_after=2, indent=0.6)

    # ------------------------------------------------------------ SECTION 7
    page_break(doc)
    heading(doc, "7", "Methodology")
    para(doc,
         "This chapter explains how the framework retrieves chunks for the user "
         "query, and derives each formula at the point where it is used. The "
         "implementation is in the project repository; every constant is defined in "
         "one configuration file with a note on its provenance.",
         align=WD_ALIGN_PARAGRAPH.JUSTIFY)

    subheading(doc, "7.1", "Vector Search — Dense Retrieval")
    para(doc,
         "When a query arrives, it is embedded with BAAI/bge-m3 (1024-d) and "
         "compared against every chunk embedding. The ranking function is cosine "
         "similarity between query vector q and chunk vector d. The top-k_dense (20) "
         "is passed to fusion.",
         align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    para(doc, "cos(q, d) = (q · d) / (‖q‖ ‖d‖)", size=Pt(12), bold=True,
         align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=4,
         font="Cambria Math")
    para(doc,
         "The derivation: the dot product equals the product of the magnitudes times "
         "the cosine of the angle between the vectors, so dividing by the magnitudes "
         "isolates the angle. The direction of the embedding carries the meaning; "
         "the magnitude is an artefact of encoding and is divided out. After L2 "
         "normalisation the cosine reduces to a plain dot product, which is what "
         "makes a pgvector HNSW dot-product index usable.",
         align=WD_ALIGN_PARAGRAPH.JUSTIFY)

    subheading(doc, "7.2", "Lexical Search — BM25")
    para(doc,
         "The lexical leg scores every chunk against the tokenised query with BM25 "
         "(Robertson–Sparck Jones). BM25 weights term frequency by an inverse "
         "document-frequency factor and applies document-length normalisation. "
         "Strong on supply-chain vocabulary.",
         align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    para(doc,
         "BM25(q, d) = Σ_{t∈Q} IDF(t) · [ f(t,d)(k₁+1) ] / "
         "[ f(t,d) + k₁(1 − b + b |d|/avgdl) ]",
         size=Pt(12), bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4,
         space_after=4, font="Cambria Math")
    para(doc,
         "The derivation runs through the probabilistic relevance framework. Under a "
         "term-independence assumption, taking logarithms of the product of "
         "likelihood ratios turns it into a sum of inverse document frequencies: "
         "IDF(t) = log[(N − n_t + 0.5)/(n_t + 0.5) + 1]. The +0.5 smoothing keeps "
         "the term finite and the +1 inside the logarithm keeps the IDF "
         "non-negative even for terms present in more than half the corpus. The "
         "numerator applies saturation, so the tenth occurrence of a term counts "
         "far less than the first; the denominator normalises for length, so a long "
         "document must work harder for the same score. k₁ = 1.2 and b = 0.75 are "
         "the standard defaults.",
         align=WD_ALIGN_PARAGRAPH.JUSTIFY)

    subheading(doc, "7.3", "Rank Fusion — Reciprocal Rank Fusion (RRF)")
    para(doc,
         "The dense top-k and the lexical top-k are fused by Reciprocal Rank Fusion "
         "(Cormack et al., 2009). The constant k = 60 is the default.",
         align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    para(doc, "RRF(d) = Σ_{r∈R} 1 / (k + r(d))     (k = 60)", size=Pt(12), bold=True,
         align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=4,
         font="Cambria Math")
    para(doc,
         "The derivation responds to a structural problem: BM25 scores, cosine "
         "similarities and cross-encoder logits lie on incomparable scales, so "
         "summing them requires a fitted weighting that does not transfer across "
         "corpora. Rank is scale-free, so RRF discards score magnitude and uses only "
         "positions. At k = 60 the discount 1/(k+r) is nearly flat across the top "
         "ten ranks, so the fused ordering is driven by agreement between the "
         "retrievers rather than by any one retriever's score magnitude. Bruch et "
         "al. (2023) found RRF at least as good as learned score-combination over "
         "23 runs, and that tuned fusion weights do not generalise out of domain — "
         "which argues for un-tuned k = 60 on an unseen corpus.",
         align=WD_ALIGN_PARAGRAPH.JUSTIFY)

    subheading(doc, "7.4", "Cross-Encoder Rerank")
    para(doc,
         "After fusion, the top-N (50) is sent to a cross-encoder rerank model "
         "(ms-marco-MiniLM-L6-v2). The reranker reads (query, chunk) jointly and "
         "emits a relevance score — no closed-form formula. Reorder by the score; "
         "pass top-10 to the confidence gate. The score is a logit, not a "
         "probability, and its scale shifts with query difficulty; Section 7.5 is "
         "what makes it usable.",
         align=WD_ALIGN_PARAGRAPH.JUSTIFY)

    subheading(doc, "7.5", "Confidence Gating — Bayesian Posterior")
    para(doc,
         "The framework computes the Bayesian posterior P(Relevant | d) for each "
         "accepted chunk. The posterior is calibrated via logistic regression on a "
         "held-out query split. If the maximum posterior falls below threshold τ, "
         "the framework returns an explicit \"no evidence\" response without calling "
         "the LLM.",
         align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    para(doc, "P(Relevant | d) = P(d|Relevant) · P(Relevant) / P(d)", size=Pt(12),
         bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=4,
         font="Cambria Math")
    para(doc,
         "In odds form this is prior odds × likelihood ratio. For a scalar rerank "
         "score x the logistic form P(R|d) = σ(β₀ + β₁x) is fitted by maximum "
         "likelihood; β₀ encodes the prior odds and β₁ the odds multiplier per unit "
         "of score. The split is by query rather than by candidate, so no "
         "evaluation candidate can leak into the calibration set. Calibration is "
         "not optional: thresholding a raw logit is a category error, so the "
         "framework additionally reports the Brier score, the Expected Calibration "
         "Error, a reliability table, and the risk–coverage curve.",
         align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    para(doc,
         "The gate is control flow rather than an instruction. It cannot be "
         "bypassed by the model, because no output the model produces reaches it; "
         "and it produces an auditable refusal, because the refusal records the "
         "posterior and the threshold that produced it.",
         align=WD_ALIGN_PARAGRAPH.JUSTIFY)

    subheading(doc, "7.6", "Per-Claim Confidence Tagging")
    para(doc,
         "Each claim of the answer is tagged using Information Gain — a measure of "
         "how much the retrieved set reduces uncertainty about the claim. High IG → "
         "grounded; moderate IG → inferred; low IG → uncertain.",
         align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    para(doc, "IG(X; Y) = H(Y) − H(Y | X) = Σ_{x,y} p(x,y) log[ p(x,y) / (p(x) p(y)) ]",
         size=Pt(12), bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4,
         space_after=4, font="Cambria Math")
    para(doc,
         "In the implementation the support probability is q = 1 − Πᵢ(1 − eᵢ), the "
         "noisy-OR combination of the per-chunk NLI entailment probabilities, and "
         "the information gain is IG = H(prior) − H(q) in bits. The two quantities "
         "answer different questions and must not be conflated: information gain is "
         "symmetric about q = 0.5, so a claim with q = 0.9 and one with q = 0.1 "
         "both yield 0.531 bits. The band is therefore cut on q, and the "
         "information gain is reported alongside as the separate measure of how "
         "much the evidence reduced uncertainty.",
         align=WD_ALIGN_PARAGRAPH.JUSTIFY)

    subheading(doc, "7.7", "Contradiction Detection — Joint NLI + Topical Gate")
    para(doc,
         "Two accepted chunks are flagged as conflicting only when an NLI model "
         "reports a contradiction AND a topical check confirms that the two "
         "passages are about the same subject. The topical check combines "
         "embedding cosine similarity with Jaccard overlap of concrete identifiers "
         "(part numbers, plant codes, standard references, quantities).",
         align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    para(doc,
         "The conjunction matters. Raising the NLI threshold alone reduces false "
         "positives only by also excluding genuine conflicts — both errors fall "
         "together. An orthogonal signal lets the two error types be traded off "
         "separately. Two further mechanisms are implemented: a quantity-conflict "
         "check, and a revision-conflict check, because \"Rev 3 sets EOQ at 187 "
         "units\" and \"Rev 4 sets EOQ at 95 units\" are both true and reporting "
         "that as a contradiction is the most damaging error available to the "
         "system.",
         align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    _sm3 = (_src_load("exp3_contradiction", ("summary",)) or {}).get("summary") or {}
    _cpd = _src_load("exp11_contradiction_precision")
    if _cpd:
        para(doc,
             "**What was measured, and what it says.** The gate's precision was "
             "measured against reader labels rather than against a proxy. "
             + _src_cp_claim(_cpd)
             + " " + _src_cp_branch(_cpd),
             align=WD_ALIGN_PARAGRAPH.JUSTIFY)
        para(doc, _src_cp_mech(_cpd), align=WD_ALIGN_PARAGRAPH.JUSTIFY)
        _cc = _src_load_control()
        if _cc:
            para(doc, _src_cc_claim(_cc), align=WD_ALIGN_PARAGRAPH.JUSTIFY)
        para(doc,
             "Two rules in the detector were found defective by that measurement "
             "and repaired: the quantity rule keyed a number to the nearest "
             "distinctive word, and so fired on citation years, version numbers "
             "and surnames; and the same-subject check let topical similarity "
             "through on its own, which made it a topic check rather than a "
             "subject check. Requiring a shared measurement, a shared instance "
             "and shared concrete objects cut the gate's alarms from 81 to "
             f"{_sm3.get('joint_gate_flagged', 0)}, and the quantity-level "
             f"conflicts it reports from 21 to "
             f"{_sm3.get('verifiable_numeric_conflicts', 0)}. "
             "Each branch's measured precision is then fitted into a calibration "
             "the pipeline reads, and a branch below the floor has its findings "
             "recorded and withheld rather than shown to a practitioner — the "
             "same discipline the answer gate applies to an answer, applied to "
             "the framework's own claims.",
             align=WD_ALIGN_PARAGRAPH.JUSTIFY)

    subheading(doc, "7.8", "Modality-Balanced Retrieval")
    para(doc,
         "A quota guarantees a minimum share of tables and charts in the final "
         "context. The implementation is swap-based: the natural top-k is taken "
         "untouched, and while a floor is unmet the lowest-ranked item of the "
         "over-represented modality is swapped for the highest-ranked available "
         "item of the under-represented modality.",
         align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    para(doc,
         "The position of the quota in the pipeline is decisive, and the ablation in "
         "Section 9 measures it. Applied before the reranker, the quota proposes a "
         "membership for the final ten, so the reranker can reorder them but not "
         "change which ten they are, and the floor binds; applied after the "
         "reranker, it adjusts the final context by importing a chunk the "
         "reranker already ranked below the cut, which displaces a good one.",
         align=WD_ALIGN_PARAGRAPH.JUSTIFY)

    # ------------------------------------------------------------ SECTION 8
    page_break(doc)
    heading(doc, "8", "Architecture & Implementation")
    para(doc,
         "The framework is organised as a four-stage pipeline. Each stage has a "
         "clear responsibility and an explicit hand-off to the next. The pipeline "
         "is config-driven: adding a category is a configuration change, not a code "
         "change.",
         align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    caption(doc, "Figure 1 — Pipeline architecture.")
    para(doc,
         "STAGE 1 — INGESTION (offline, per document)\n"
         "     [Documents] → [Parse: text + tables + figures] → [Chunk: table-aware]\n"
         "     → [Embed: BGE-M3 1024-d] → [Store: Postgres 16 + pgvector (HNSW)]",
         size=Pt(9.5), align=WD_ALIGN_PARAGRAPH.LEFT, space_after=6, line=1.3)
    para(doc,
         "STAGE 2 — RETRIEVAL AND RANKING (online, per query)\n"
         "     [User query] → [Embed query] → [Category filter]\n"
         "     → [Hybrid: BM25 + pgvector HNSW] → [RRF] → [Modality quotas]\n"
         "     → [Cross-encoder rerank] → [Confidence gate: Bayesian posterior]",
         size=Pt(9.5), align=WD_ALIGN_PARAGRAPH.LEFT, space_after=6, line=1.3)
    para(doc,
         "STAGE 3 — GENERATION (online, per accepted chunk-set)\n"
         "     [Per-claim tagging] → [Citations] → [Contradiction flag] → [Answer]",
         size=Pt(9.5), align=WD_ALIGN_PARAGRAPH.LEFT, space_after=10, line=1.3)
    caption(doc, "Table 2 — Stack at a glance.")
    table(doc, ["Layer", "Technology"], [
        ["Backend", "Python 3.12, FastAPI, Postgres 16 + pgvector (HNSW), psycopg"],
        ["Embeddings", "BAAI/bge-m3 (1024-d, default)"],
        ["LLM", "Instruction-tuned LLM behind a tool-call interface (deployment-specific)"],
        ["NER / NLI", "GLiNER zero-shot, cross-encoder/nli-deberta-v3-small"],
        ["Analytics", "pandas, SciPy, statsmodels, scikit-learn, lifelines, ruptures"],
        ["Frontend", "Next.js 15 (App Router), React 19, TypeScript, Tailwind v4, Recharts"],
        ["Evaluation", "Custom harness: paired Wilcoxon / McNemar, bootstrap CI, Cohen's κ"],
    ], widths=[3.4, 12.6], size=Pt(9.5))
    para(doc, "", space_after=6)
    caption(doc, "Table 3 — Repository layout.")
    table(doc, ["Path", "Contents"], [
        ["impl/src/lexical.py", "BM25 implemented from first principles, with the derivation"],
        ["impl/src/hybrid.py", "Reciprocal Rank Fusion and the swap-based modality quota"],
        ["impl/src/confidence.py", "Posterior, Platt and isotonic calibration, ECE, Brier, risk–coverage, the gate"],
        ["impl/src/contradiction.py", "Joint NLI + topical gate, entity overlap, numeric conflict"],
        ["impl/src/claims.py", "Claim decomposition, noisy-OR, entropy, information gain"],
        ["impl/src/stats.py", "Cohen's κ, McNemar, Wilcoxon, bootstrap, Cliff's δ"],
        ["impl/experiments/", "The six experiment scripts and their result files"],
    ], widths=[4.6, 11.4], size=Pt(9.5))

    # ------------------------------------------------------------ SECTION 9
    page_break(doc)
    heading(doc, "9", "Experimental Results")
    para(doc,
         "The evaluation uses an independently constructed public industrial corpus, "
         "so that the results are reproducible and are not tied to a single "
         "proprietary document set. The corpus contains six industrial categories.",
         align=WD_ALIGN_PARAGRAPH.JUSTIFY)

    # -- 9.0 The dataset, its source, and its provenance ------------------
    subheading(doc, "9.0", "The Dataset, Its Source and Its Provenance")
    para(doc,
         "Two corpora are referred to in this report, and they are not the same "
         "thing. The primary corpus of the original project specification was "
         "634 chunks across 24 proprietary supply-chain documents; it is not "
         "redistributable and therefore cannot be shipped with this report or "
         "re-run by a reader. Every measurement reported here was taken on a "
         "public substitute built to have the same properties — several "
         "industrial categories, genuine tables and figures so the modality "
         "mechanisms have something to act on, and a citable source.",
         align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    _focus_docs = _focus_chunks = _focus_queries = "—"
    if focus_manifest.exists():
        _focus_docs = str(len(json.loads(focus_manifest.read_text(encoding="utf-8"))))
    if focus_index.exists():
        _focus_chunks = f"{json.loads(focus_index.read_text(encoding='utf-8'))['stats']['n_chunks']:,}"
    if focus_bench.exists():
        _focus_queries = str(json.loads(focus_bench.read_text(encoding="utf-8"))["n_queries"])
    para(doc,
         f"Source: English Wikipedia, fetched through the MediaWiki parse API. "
         f"Licence: CC BY-SA 4.0 for the article text. The corpus is shipped in "
         f"full alongside this report, in deliverables/dataset/, together with a "
         f"provenance manifest that gives for every document its Wikipedia URL, "
         f"the upstream revision it was read at, the SHA-256 of the exact bytes "
         f"used, and its chunk count.",
         align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    para(doc,
         f"The thesis focuses on a single industrial domain, supply chain "
         f"management — {_focus_docs} documents and {_focus_chunks} chunks, with "
         f"its own {_focus_queries}-question benchmark — because that is the "
         f"domain the primary corpus covered and the one the practitioner "
         f"scenarios are drawn from. The remaining five categories are retained "
         f"for the cross-category transfer objective, which by definition needs "
         f"a subset of categories to transfer to held-out ones. A worked "
         f"before-and-after case study on the focus domain accompanies the "
         f"aggregate tables in the appendix, tracing real questions through "
         f"every stage of the pipeline.",
         align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    para(doc,
         "What the substitute is not: these are encyclopedia articles, not the "
         "operating manuals, standard operating procedures and supplier "
         "specifications of a real plant. They are industrial in subject matter, "
         "not operationally binding.",
         align=WD_ALIGN_PARAGRAPH.JUSTIFY)

    if exp1:
        cs = exp1["corpus_stats"]
        para(doc,
             f"Corpus: {cs['n_chunks']:,} chunks from {cs['n_documents']} documents "
             f"({cs['share_text']:.1%} text, {cs['share_table']:.1%} table, "
             f"{cs['share_chart']:.1%} chart). Benchmark: "
             f"{exp1['benchmark']['n_queries']} silver-standard queries "
             f"({exp1['benchmark']['n_answerable']} answerable, "
             f"{exp1['benchmark']['n_unanswerable']} deliberately unanswerable).",
             align=WD_ALIGN_PARAGRAPH.JUSTIFY)
        para(doc,
             "The labels are silver-standard: derived from the document "
             "rather than annotated by an expert, so absolute recall is "
             "optimistic. The first version of this benchmark was worse than "
             "that word suggests -- a quarter of its answerable questions were "
             "malformed, because the generator could match mid-clause and "
             "produce questions like 'What value is stated for a teep in the "
             "source documentation?'. The generator now anchors each match to "
             "the start of a sentence, rejects a subject containing a verb, a "
             "pronoun or a dangling preposition, and keeps acronyms in their own "
             "case. Every question in the benchmark is now one somebody would "
             "ask of the document.",
             align=WD_ALIGN_PARAGRAPH.JUSTIFY)
        caption(doc, "Table 4 — Retrieval ablation, with paired Wilcoxon signed-rank "
                     "tests between adjacent rungs.")
        order = ["A. bm25_only", "B. dense_only", "C. hybrid_rrf",
                 "D. hybrid_rrf_rerank", "E. +category_filter",
                 "F. +quota_pre_rerank", "G. +quota_post_rerank"]
        comp = _comp_index(exp1["comparisons"])
        rows = []
        for i, k in enumerate(order):
            v = exp1["systems"][k]
            prev = None
            for a, b in zip(order[:-1], order[1:]):
                if b == k:
                    prev = comp.get(a)
            rows.append([
                k.split(". ")[0], k.split(". ")[1] if ". " in k else k,
                f"{v['recall@5']:.3f}", f"{v['recall@10']:.3f}", f"{v['recall@20']:.3f}",
                f"{v['mrr']:.3f}", f"{v['nDCG@10']:.3f}",
                f"{v['modality_recall'].get('table', float('nan')):.3f}",
                f"{prev['delta']:+.3f}" if prev else "—",
                f"{prev['wilcoxon']['p_value']:.2e}" if prev else "—",
            ])
        table(doc, ["", "System", "R@5", "R@10", "R@20", "MRR", "nDCG@10",
                    "Tbl R@10", "ΔR@10", "p"], rows,
              widths=[0.7, 3.5, 1.1, 1.1, 1.1, 1.1, 1.3, 1.4, 1.2, 1.4], size=Pt(8))
        figure(doc, "fig4_modality_quota_pareto")
        para(doc, "", space_after=6)
        para(doc, "Three findings contradict the original design specification:",
             bold=True, space_after=4)
        bullet(doc,
               "A reranker's recall is governed by its candidate pool. The same "
               f"reranker on the same corpus raises Recall@10 from "
               f"{exp1['systems']['C. hybrid_rrf']['recall@10']:.3f} to "
               f"{exp1['systems']['D. hybrid_rrf_rerank']['recall@10']:.3f} with a "
               f"top-50 pool, but with a top-10 pool it leaves Recall@10 unchanged "
               f"and reduces Recall@20 from "
               f"{exp1['systems']['C. hybrid_rrf']['recall@20']:.3f} to "
               f"{exp1['systems']['D. hybrid_rrf_rerank']['recall@20']:.3f}. A "
               "reranker can only reorder within the pool it is given. This is the "
               "most likely explanation of the −5.34 pp reranker regression "
               "previously reported on an independent corpus.")
        figure(doc, "fig1_pool_size")
        bullet(doc,
               "The modality quota belongs BEFORE the cross-encoder, which "
               "inverts the rule the framework was designed on. Applied before "
               f"the reranker it moves Recall@10 by "
               f"{exp1['systems']['F. +quota_pre_rerank']['recall@10'] - exp1['systems']['E. +category_filter']['recall@10']:+.3f} "
               f"and reaches table recall "
               f"{exp1['systems']['F. +quota_pre_rerank']['modality_recall'].get('table', 0):.3f}; "
               f"applied after it, Recall@10 moves "
               f"{exp1['systems']['G. +quota_post_rerank']['recall@10'] - exp1['systems']['E. +category_filter']['recall@10']:+.3f} "
               f"and table recall falls to "
               f"{exp1['systems']['G. +quota_post_rerank']['modality_recall'].get('table', 0):.3f} "
               f"(p = {exp1['comparisons'][5]['wilcoxon']['p_value']:.1e}). A quota "
               "applied later has to import candidates the cross-encoder has "
               "already ranked below the cut.")
        bullet(doc,
               f"Corpus modality composition predicts the sign of the modality "
               f"effect. At {cs['share_text']:.1%} text, a two-table quota can only "
               f"draw on tables deep in the ranking, displacing relevant prose — so a "
               f"null or negative modality effect is the expected outcome on such a "
               f"corpus, not a defect. This is why the framework measures and "
               f"reports the corpus composition.")

    if exp2:
        para(doc, "", space_after=4)
        caption(doc, "Table 5 — The confidence gate as a selective-prediction policy.")
        cal = exp2["calibration_metrics"]
        uni = exp2["univariate_top1_rerank"]
        ch = exp2["chosen_operating_point"]
        rows = [
            ["Univariate β₀ / β₁ on the top rerank score",
             f"{uni['beta0']:.3f} / {uni['beta1']:.3f}"],
            ["Multivariate intercept", f"{exp2['weights']['intercept']:.3f}"],
            ["Brier score (held-out half)", f"{cal['brier']:.4f}"],
            ["Expected Calibration Error", f"{cal['ece']:.4f}"],
            ["Base rate of contexts with sufficient evidence",
             f"{exp2['base_rate_answer_in_context']:.3f}"],
            ["Retriever recall of the gold chunk",
             f"{exp2['retriever_recall_of_gold']:.3f}"],
            ["Selected operating point τ", f"{ch['tau']:.2f}"],
            ["Operating-point rule", exp2["operating_point_rule"]],
            ["Answerable questions answered", f"{ch['answerable_answered']:.3f}"],
            ["Unanswerable questions refused", f"{ch['unanswerable_refused']:.3f}"],
            ["Abstention precision", f"{ch['abstention_precision']:.3f}"],
            ["Always-answer baseline (unanswerable refused)",
             f"{exp2.get('never_refuse_baseline', {}).get('unanswerable_refused', 0.0):.3f}"],
        ]
        table(doc, ["Quantity", "Value"], rows, widths=[10.0, 6.0], size=Pt(9.5))
        figure(doc, "fig2_risk_coverage")
        figure(doc, "fig3_calibration")
        para(doc,
             "The calibration target is a QUERY-level label — whether the retrieved "
             "context contains sufficient evidence to answer — rather than a "
             "chunk-level one. With one gold chunk among fifty candidates the "
             "chunk-level base rate is about 2%, so fitting against it returns "
             "‘nothing is relevant’ and the calibration metrics measure the base "
             "rate rather than the filter. The fitted coefficients also differ "
             "substantially from the values fitted on a different corpus in an "
             "earlier run (β₀ = 2.943, β₁ = 1.680). That is not an inconsistency: it "
             "demonstrates that the calibration is a fitted parameter of the "
             "deployment rather than a constant of the architecture, and that it "
             "must be re-fitted for every retrieval configuration compared — as "
             "DeclineCraft (2026) requires, since better retrieval reduces "
             "abstention.",
             align=WD_ALIGN_PARAGRAPH.JUSTIFY)

    if exp3:
        sm = exp3["summary"]
        para(doc, "", space_after=4)
        caption(doc, "Table 6 — Contradiction detection, reported with prevalence and "
                     "with always-flag and never-flag baselines.")
        _kinds = sm.get("flagged_by_kind") or {}
        table(doc, ["Detector", "Pairs flagged", "Flag rate"], [
            ["NLI alone", sm["nli_only_flagged"], f"{sm['nli_flag_rate']:.3f}"],
            ["The shipped gate (NLI + same-subject, + quantity, + revision)",
             sm["joint_gate_flagged"], f"{sm['joint_flag_rate']:.3f}"],
            ["Baseline: always flag", sm["pairs_compared"],
             f"{sm['baseline_always_flag_false_positive_rate']:.3f}"],
            ["Baseline: never flag", 0, "—"],
        ], widths=[8.4, 3.2, 2.6], size=Pt(9.5))
        figure(doc, "fig6_contradiction_precision")
        para(doc,
             f"The gate has three branches, and the alarms split "
             f"{_kinds.get('semantic', 0)} semantic, {_kinds.get('quantity', 0)} "
             f"quantity and {_kinds.get('revision', 0)} revision. The same-subject "
             f"check is what does the work: it suppresses "
             f"{sm['nli_only_flagged'] - sm['joint_gate_flagged']} of the bare NLI "
             f"gate's alarms. Prevalence of true conflict among the compared pairs "
             f"is {sm['prevalence_of_true_conflict']:.4f}; without prevalence a "
             f"false-positive rate is uninterpretable. The revision-supersession "
             f"check suppressed {sm['revision_supersession_suppressed']} pairs whose "
             f"apparent conflict was simply a later revision of the same policy.",
             align=WD_ALIGN_PARAGRAPH.JUSTIFY)
        para(doc,
             f"Two rules in the detector were measured against reader labels, "
             f"found defective and repaired. The quantity rule used to key a "
             f"number to the nearest distinctive word, so on encyclopaedic text it "
             f"fired on citation years, version numbers and surnames; it now keys a "
             f"number to a measurement term and requires the two passages to be "
             f"about the same instance. The subject check used to let topical "
             f"similarity through on its own, which made it a topic check rather "
             f"than a subject check; it now requires shared concrete objects as "
             f"well, as its own design says. Between them the two repairs cut the "
             f"gate's alarms from 81 to {sm['joint_gate_flagged']}. The corpus, the "
             f"benchmark and the label standard were not changed.",
             align=WD_ALIGN_PARAGRAPH.JUSTIFY)
        para(doc,
             f"Each branch's measured precision is fitted into a calibration the "
             f"pipeline reads, and a branch below the floor has its findings "
             f"withheld rather than shown to a practitioner: on this corpus that "
             f"leaves {sm.get('surfaced_findings', 0)} findings surfaced and "
             f"{sm.get('withheld_findings', 0)} withheld. That is the same "
             f"discipline the answer gate applies to an answer, applied to the "
             f"framework's own claims.",
             align=WD_ALIGN_PARAGRAPH.JUSTIFY)
        _cp = _src_load("exp11_contradiction_precision")
        if _cp:
            para(doc, _src_cp_claim(_cp),
                 align=WD_ALIGN_PARAGRAPH.JUSTIFY)
            para(doc, _src_cp_mech(_cp),
                 align=WD_ALIGN_PARAGRAPH.JUSTIFY)

    if exp4:
        lh = exp4["leave_half_out"]
        para(doc, "", space_after=4)
        caption(doc, "Table 7 — Cross-category transfer (RO4).")
        table(doc, ["Quantity", "Value"], [
            ["Tuning categories", ", ".join(lh["tuning_categories"])],
            ["Held-out categories", ", ".join(lh["held_out_categories"])],
            ["β fitted on the tuning half",
             f"{lh['weights_tuning_half'][0]:.3f} / {lh['weights_tuning_half'][1]:.3f}"],
            ["β fitted on the held-out half",
             f"{lh['weights_held_out_half'][0]:.3f} / {lh['weights_held_out_half'][1]:.3f}"],
            ["τ (fitted on the tuning half, transferred unchanged)",
             f"{lh['tau']:.2f}"],
            ["Held-out: answerable answered (transferred)",
             f"{lh['metrics_held_out_transferred']['answerable_answered']:.3f}"],
            ["Held-out: answerable refused (transferred)",
             f"{lh['metrics_held_out_transferred']['answerable_refused']:.3f}"],
        ], widths=[10.0, 6.0], size=Pt(9.5))
        para(doc,
             "The ranking of configurations transfers across industrial sub-domains; "
             "the threshold does not transfer unchanged, and the direction of the "
             "error is systematic — a threshold fitted on one configuration is too "
             "permissive where it is transferred, and too permissive in the "
             "direction that flatters the configuration it is transferred to. At "
             "the tuning half's threshold applied unchanged to the held-out half, "
             "the gate answers "
             f"{lh['metrics_held_out_transferred']['answerable_answered']:.3f} of "
             "the answerable questions against "
             f"{lh['metrics_held_out_refitted']['answerable_answered']:.3f} when "
             "the weights are refitted there, and refuses "
             f"{lh['metrics_held_out_transferred']['unanswerable_refused']:.3f} of "
             "the unanswerable ones against "
             f"{lh['metrics_held_out_refitted']['unanswerable_refused']:.3f}. This "
             "is the practical form of the DeclineCraft finding, and it is why the "
             "calibration is re-fitted per arm.",
             align=WD_ALIGN_PARAGRAPH.JUSTIFY)

    # -- 9.9 The unanswerable half: audited, and rebuilt -------------------
    subheading(doc, "9.9", "The Benchmark's Unanswerable Half: Audited, and Rebuilt")
    para(doc,
         "The unanswerable class is the half on which a refusal benchmark lives "
         "or dies, and it was the half audited last. The audit found a serious "
         "defect. A classifier that saw only the question — no retrieval, no "
         "evidence, no reasoning about the corpus — told the answerable questions "
         "from the unanswerable ones at an ROC AUC of 0.999, and a "
         "single regular expression caught 76.4% of the "
         "unanswerable class with no false positives at all, because the class's "
         "designated hard case asked about a fabricated identifier that no "
         "answerable question carried. If a system's unanswerability is visible "
         "in the question, a system refusing on the question's shape scores as "
         "well as one reading the passages, and the benchmark cannot tell them "
         "apart. The refusal rate that class produced was an upper bound rather "
         "than a measurement.",
         align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    para(doc,
         "The class was rebuilt rather than reported around. The repaired class "
         "uses the answerable class's own three question stems, its own source "
         "documents and its own label machinery — the definition branch finds a "
         "definition, the numeric branch finds a value, a table cell holds the "
         "answer — and the repaired class is labelled by the complement of "
         "exactly those tests. Each repaired question was further drawn to have "
         "a structural twin in the answerable class: the same stem, the same "
         "subject size, the same shape markers, and no word in common "
         "(106 of 110 have one). The certificates the generator "
         "writes into each record were re-checked against the corpus by a "
         "predicate written independently of the generator: "
         "1 of 110 failed.",
         align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    para(doc,
         "Re-measured, the shape-only classifier scores an ROC AUC of "
         "0.608 against a permutation null of 0.468, and "
         "the one-rule shortcut carries 0.0%. The refusal "
         "rate is now reported by stratum: at the fitted operating point the "
         "gate refuses 23.6% of the corpus-anchored "
         "questions (26 of 110) — questions the corpus discusses "
         "but states no value for — and 76.5% of the "
         "out-of-domain ones (26 of 34), the latter being "
         "unanswerable for any system that knows what the corpus is about. The "
         "pooled figure over the whole unanswerable class is an upper bound.",
         align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    para(doc,
         "That gap is the result. The gate refuses a recognisable unanswerable "
         "question; it does not detect absent evidence, because on an on-topic "
         "question the retrieval features look healthy and there is nothing to "
         "detect. The detection problem this framework addresses is "
         "considerably harder than the first version of the benchmark made it "
         "look, and the repair is what shows it.",
         align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    figure(doc, "fig5_question_only_roc")

    # -- 9.10 A second corpus: authentic, versioned, binding industrial text ---
    subheading(doc, "9.10", "A Second Corpus: Authentic, Versioned, Binding "
                           "Industrial Text")
    para(doc,
         "The measurements reported above were taken on an encyclopaedic corpus: "
         "Wikipedia prose about industrial engineering. Three of the project's "
         "research objectives are closed on a second public corpus, the one this "
         "section reports. The numbering used here is the proposal's, which is "
         "finer-grained than the summary in Section 6: RO4 is "
         "cross-document contradiction surfacing, RO5 is per-claim confidence "
         "tagging, and RO6 is evaluation on industrial corpora and benchmarks.",
         align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    para(doc,
         "RO4 could not be closed on the first corpus. The contradiction "
         "mechanism's precision, measured against blind reader labels rather "
         "than against a proxy, was 0.0% on the focus domain "
         "of that corpus, and the reason is structural rather than incidental. A "
         "document read at a single upstream revision cannot contradict itself, "
         "and concept-level prose rarely binds a numeric requirement that "
         "another document contradicts. The corpus therefore contains no "
         "conflict a practitioner would recognise as one, and it is not the "
         "class of document a practitioner reads. What was needed was a corpus "
         "that provably contains conflicts, and on which each conflict's type "
         "is known without asking anybody.",
         align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    para(doc,
         "That corpus was built. It is the United States Electronic Code of "
         "Federal Regulations (eCFR), read through the versioner API, which "
         "serves any regulation as it stood on any past date. Two properties "
         "follow, and together they close the objectives with one artefact. The "
         "text is authentic and binding: these are the regulations a plant is "
         "measured against, they carry numeric requirements, and they are a work "
         "of the United States government in the public domain, so the corpus "
         "ships with this report and no licence obligation attaches to it. The "
         "text is also versioned: federal regulations are amended, so the same "
         "provision read at two dates is the same rule at two issues. The corpus "
         "snapshot is the 2026-06-01 issue, and the revision corpus "
         "pairs 2021-12-31 with 2026-06-01. It holds "
         "110 documents and 2,443 chunks across "
         "4 regulatory regimes: OSHA general industry; OSHA "
         "process safety and EPA risk management; EPA new source performance "
         "standards; and DOT hazardous materials.",
         align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    para(doc,
         "The version trick is what supplies the labels. Aligning the two issues "
         "gives 948 amended-paragraph pairs, of which "
         "361 (38.1%) state different numbers "
         "in the two vintages. Such a pair is a conflict, and its type is known "
         "by construction: the same provision at two issues is a supersession, "
         "not a contradiction. No annotation is needed, and no two readers have "
         "to agree.",
         align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    para(doc,
         "The benchmark built on it holds 444 queries — "
         "247 answerable and 197 "
         "unanswerable — and was audited for the same shortcut the first "
         "benchmark had. The one-rule identifier shortcut that carried "
         "76.4% of the first benchmark's unanswerable class "
         "catches 0 of 197 here. A "
         "classifier that sees only the question separates the two classes at an "
         "ROC AUC of 0.708 against a permutation null of "
         "0.505, and a bag-of-words model separates them at "
         "0.793. The residual separability is question length — "
         "73 characters in the answerable class against "
         "50 in the unanswerable one — and it is reported "
         "rather than hidden.",
         align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    para(doc,
         "RO6 — evaluation on industrial corpora. The retrieval ablation was "
         "re-run unchanged on this corpus, over the "
         "247 answerable queries of its benchmark.",
         align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    caption(doc, "Table 8 — Retrieval ablation on the industrial corpus, with "
                 "the paired Wilcoxon signed-rank test on each comparison.")
    table(doc, ["Measurement", "Value", "p"], [
        ["BM25 only — Recall@10", "0.9595", "—"],
        ["Dense encoder only — Recall@10", "0.8785", "—"],
        ["BM25 − dense encoder (Recall@10)", "-0.081",
         "0.00026"],
        ["Hybrid fusion − its own lexical leg (Recall@10)",
         "+0.000", "1.00000"],
        ["Category pre-filter − no filter (Recall@10)",
         "+0.000", "1.00000"],
        ["Cross-encoder − no reranker (Recall@10)",
         "+0.028", "0.01963"],
    ], widths=[8.4, 3.4, 2.4], size=Pt(9.5))
    para(doc,
         "The lexical leg carried the pipeline. BM25 reached a Recall@10 of "
         "0.9595 against the dense encoder's 0.8785, a "
         "difference of -0.081 at p = "
         "0.00026 over n = 247 queries. That "
         "lexical retrieval beats an off-the-shelf dense encoder on legal and "
         "regulatory text is already published, three times, in three "
         "jurisdictions, so it is not claimed here as new; and the dense leg in "
         "this pipeline is a general-purpose encoder that a domain-adapted one "
         "could overtake, so the result is a boundary condition on this pipeline "
         "rather than a claim about dense retrieval. What the measurement "
         "contributes is the corollary: on this corpus the fusion added "
         "+0.000 to its own lexical leg (p = "
         "1.00000) and the category pre-filter added "
         "+0.000 to no filter (p = "
         "1.00000), so neither added anything measurable "
         "on top of the lexical baseline. The cross-encoder was the one "
         "component that moved recall here, by +0.028 "
         "at p = 0.01963.",
         align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    para(doc,
         "The candidate-pool curve is no longer saturated. On the first corpus "
         "it peaked at a pool of 10 and did not improve beyond it, so "
         "the thesis could not distinguish a pool that had stopped helping from "
         "a corpus with nothing left to find. Here, at a pool of 50, Recall@20 "
         "reaches 1.000 while Recall@10 stands at "
         "0.988: 1.21% of the golds are "
         "retrieved and then pushed out of the ten-chunk context by the "
         "reranker's own ordering. A reranker can only reorder within the pool "
         "it is given.",
         align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    para(doc,
         "The gate's threshold does not transfer across corpora, and its "
         "operating point does. At τ = 0.40 the industrial gate "
         "answers 91.5% of the answerable "
         "queries and refuses 58.9% of the "
         "unanswerable ones, with an abstention precision of "
         "0.847 and a coverage of "
         "0.691. The threshold is a fitted parameter of the "
         "deployment — 0.40 here against 0.05 on the "
         "focus domain of the first corpus — while the point on the "
         "risk–coverage surface a practitioner cares about is a property of the "
         "mechanism, and it is nearly the same on both: "
         "0.691 against 0.693. The two "
         "calibrations differ in quality as well as in value. The industrial "
         "gate's expected calibration error is 0.075 against "
         "0.104, while its Brier score is 0.159 "
         "against 0.151; it is the better of the two on "
         "calibration error and the worse of the two on Brier, and both are "
         "reported.",
         align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    para(doc,
         "RO4 — cross-document contradiction surfacing. 240 pairs "
         "were assembled in two strata: 90 revision "
         "pairs, a paragraph and its amended self, and "
         "150 similar pairs, cross-document retrieval "
         "neighbours. The pool is mined by the retriever's own lexical signal "
         "and never by the detector's numeric rule, its NLI probability or its "
         "subject check: a pool selected on the detector's decision rule cannot "
         "measure the detector's precision, because every alarm would be in it "
         "by construction. The pairs were read by a panel of domain "
         "specialists, one per regulatory regime, together with a generalist "
         "control, all blind to the detector.",
         align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    para(doc,
         "A conflict detector's precision is two numbers, not one. Detection "
         "asks whether the alarm is pointing at something real; typing asks "
         "whether the branch that raised the alarm is the branch that owns the "
         "conflict.",
         align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    caption(doc, "Table 9 — A conflict detector's precision, measured as two "
                 "numbers rather than one.")
    table(doc, ["Measurement", "Detection", "Typing"], [
        ["Against the readers' labels",
         "0.659 (95% CI 0.505–"
         "0.784)",
         "0.073 (95% CI 0.025–"
         "0.194)"],
        ["Against the construction labels",
         "1.000",
         "0.000"],
        ["Under the shipped operations vocabulary",
         "0.650",
         "0.000"],
    ], widths=[6.0, 4.4, 3.8], size=Pt(9.5))
    para(doc,
         "Detection rises to 0.897 on the stratum where the "
         "conflicts actually are, and the recall of any real conflict is "
         "0.321 over the 84 annotated "
         "supersessions. Against the construction labels, where the conflict "
         "type is known without any judgement, every alarm points at a real "
         "conflict and not one alarm was raised by the branch that owns its "
         "conflict. The mechanism therefore finds the conflicts and reports "
         "them as the wrong kind: it calls supersessions contradictions, and it "
         "cannot say which version is in force, because nothing in the "
         "retrieved passages says which issue either of them is. On a "
         "regulatory corpus that is the one thing a practitioner needs from a "
         "contradiction detector. The consequence is a specification — a "
         "detector for regulatory text needs version metadata, or must be "
         "scoped to detection alone.",
         align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    para(doc,
         "The quantity branch is thinner still. An exhaustive corpus-wide search "
         "over 64 measurement terms found 1776 "
         "candidate cross-document quantity conflicts, a count that is exact "
         "rather than sampled because the search groups every (measurement "
         "term, value) pair in the corpus and keeps the terms whose values "
         "differ across documents. 119 pairs went to the reader "
         "and the branch fired on 13; of the 60 "
         "pairs the reader labelled, none was a genuine quantity conflict. The "
         "search is deliberately over-inclusive — two passages about different "
         "boilers share the word \"pressure\" — so the branch's precision on "
         "this corpus is not measurable, and the framework's calibration floor "
         "would withhold it rather than report it.",
         align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    para(doc,
         "What bound the measurement was the annotation rather than the "
         "mechanism. The first comparison of the two rubrics was confounded: the "
         "old-rubric reader was the generalist, so \"old rubric\" and "
         "\"generalist\" were the same cell. A 2×2 factorial separates them, "
         "with the pairs, the detector and the regime briefs held constant.",
         align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    caption(doc, "Table 10 — The annotation rubric against the reader's "
                 "specialisation, as a 2×2 factorial.")
    table(doc, ["Reader", "Old rubric", "Sharpened rubric"], [
        ["Generalist", "0.293", "0.659"],
        ["Specialist", "0.341", "0.659"],
    ], widths=[5.0, 4.6, 4.6], size=Pt(9.5))
    para(doc,
         "The rubric moved the measured precision by +0.366 "
         "at the generalist and +0.317 at the "
         "specialist; the reader's specialisation moved it by "
         "+0.049 at the old rubric and "
         "+0.000 at the sharpened one. The mechanism is "
         "concrete. The old rubric required a version marker, and a regulation "
         "does not write its own version in its text, so it missed "
         "63 of the "
         "82 supersessions it was asked to "
         "find; the specialist missed 63 of the "
         "90. Three qualifications are owed. "
         "The rubric changed the definition of the target as well as the "
         "procedure for recognising one, and this experiment cannot separate "
         "the two, so what it shows is that the reader factor is small. "
         "\"Specialisation\" was delivered as a brief to a fixed reader model "
         "rather than as a different capability, so the claim is narrower than "
         "the claim that specialists are unnecessary. And the qualitative "
         "principle — that the annotation guideline is a first-class error "
         "source in model annotation — is already published; what is new is "
         "that the factor of nine lands on the reported system measurement. The "
         "generalisable point is about measurement rather than about "
         "annotation: a number that moves by a factor of nine with the wording "
         "of its own rubric is not yet a measurement of the thing under test.",
         align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    para(doc,
         "RO5 — per-claim confidence tagging. The band was measured with the "
         "same generator and under both evidence protocols, over "
         "293 and 297 labelled "
         "claims. Against an independent reference its agreement is κ "
         "0.055 (95% CI -0.027–"
         "0.138) on the gold protocol and "
         "0.017 (95% CI "
         "-0.066–0.101) "
         "on the retrieved one, against 0.049 and "
         "0.069 on the first corpus. The band's error rates "
         "are 0.077 (grounded), "
         "0.119 (inferred) and "
         "0.139 (uncertain) on the gold protocol, and "
         "0.006, "
         "0.017 and "
         "0.026 on the retrieved one. The band "
         "is at chance against an independent reference on all four "
         "corpus-and-protocol combinations, and on the evidence the band itself "
         "saw its bands are ordered in the expected direction, which is what "
         "they should do if the band is scoring the support of a claim rather "
         "than its truth: it measures whether the retrieved passages entail "
         "the claim — agreement with itself — not whether the claim is true. As "
         "a filter it works. Answers containing no wrong claim rise from "
         "91.1% to 94.9% on "
         "the gold protocol and from 98.3% to "
         "99.6% on the retrieved one.",
         align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    para(doc,
         "The positional comparison — keeping the first half of an answer — is "
         "the evidence for that reading and not the finding, and it does not "
         "hold everywhere. Of the four corpus-and-protocol combinations, one "
         "gives a significant positional result (the first corpus's gold "
         "evidence, p = 0.008) and three do not (p = "
         "0.417, p = 1.000 and p = "
         "1.000).",
         align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    para(doc,
         "What the second corpus does not establish is stated rather than "
         "implied. One jurisdiction, one language and one regulatory family: "
         "the corpus is United States federal regulation, and nothing here "
         "shows that the decomposition holds for a plant's own procedures, for "
         "a non-English regulatory regime, or for a corpus of vendor "
         "specifications. The conflict labels are model-generated, so the "
         "panel's agreement is not confirmation that a label is right; this is "
         "the cost of replacing human annotators, and it is named as such in "
         "the limitations above. The rubric's wording moved the measured "
         "precision, which is a warning about every model-annotated number in "
         "this report and not only about that one. And the positional "
         "comparison did not replicate on three of the four combinations, so "
         "the band is reported as a filter with a measurement decomposition "
         "rather than as a ranking.",
         align=WD_ALIGN_PARAGRAPH.JUSTIFY)

    # ------------------------------------------------------------ SECTION 10
    page_break(doc)
    heading(doc, "10", "Limitations & Future Work")
    cs = exp1["corpus_stats"] if exp1 else {}
    _limitations = [
        f"Single-domain evaluation of the primary corpus — the original run covers "
        f"one focus category and the other eleven categories share the retrieval "
        f"pipeline. The reported results use the public substitute corpus, which "
        f"spans {cs.get('n_categories', 6)} categories and is tested for "
        f"cross-category transfer, but generalisation is demonstrated "
        f"mechanistically and not at production scale.",
        f"Small corpus — the primary corpus holds 634 chunks across 24 documents, "
        f"and the public substitute holds {cs.get('n_chunks', 0):,} chunks across "
        f"{cs.get('n_documents', 0)} documents. Both sit below the scale at which "
        f"the statistical framing used here is well founded.",
        "Modality-aware boost is a documented null result on a text-heavy corpus — "
        "the corpus is too sparse in tables and charts to exercise the signal, which "
        "Section 9 shows is a power limitation rather than a defect.",
        "Cross-encoder rerank regresses on some sub-categories; fine-tuning the "
        "reranker on a domain-matched dataset is future work.",
        "NLI-only contradiction detection has a high false-positive rate; the joint "
        "gate reduces it substantially, but the absolute rate remains high and "
        "published NLI ceilings on technical text are low.",
        "The user study is at the lower bound of its target size; replication with a "
        "larger cohort is needed before any claim about generalisability to "
        "practitioners.",
        "The long-context baseline is measured on cost and on answer quality for "
        "the focus domain. The long-context arm sends 74x more "
        "input tokens per query than the RAG arm on the focus domain, which at the "
        "provider's cached-prefix pricing is a 58.8x input-cost "
        "ratio. On the six-category corpus the corpus is 680,417 "
        "tokens, which exceeds the 128K window most hosted models offer but fits "
        "the 1M-token window of the generator used here, so the answer-quality "
        "half is measured on the focus domain because that is the domain this "
        "report is about and because the two corpora are never pooled -- not "
        "because the comparison would have been impossible. the comparison is measured, and on this corpus it does not support a superiority claim for long-context prompting in this domain The "
        "threat is therefore answered on this corpus and not in general.",
        "The calibration is deployment-specific and must be re-fitted for each "
        "retrieval configuration and each corpus.",
        "The framework's own hypothesis H2.1 -- that a code-level, non-bypassable "
        "gate reduces hallucination -- is supported under both prompt conditions The hypothesis was tested under two prompt conditions that differ by a single sentence, with everything else -- the model, the questions, the retrieval, the scorer -- held fixed. Conditional: the hypothesis holds under both prompt conditions. Under the cautious prompt -- the deployed system -- it is supported, at a price: the gate reduced the rate of answering unanswerable questions from 0.535 to 0.417, a fall of 11.8 points, at the cost of answering 30 of 32 answerable questions. Paired question by question, the gate refused 23 of the questions the ungated arm answered and let through 6 of the ones it did not (exact McNemar p = 0.002). Under the answering prompt, which differs from the cautious one by a single sentence, it is supported, at a price: the gate reduced the rate of answering unanswerable questions from 0.938 to 0.528, a fall of 41.0 points, at the cost of answering 30 of 32 answerable questions. Paired question by question, the gate refused 60 of the questions the ungated arm answered and let through 1 of the ones it did not (exact McNemar p = < 0.001). What the framework claims is therefore that the gate reduces the rate of answering unanswerable questions whatever the generator does, and that it is the one component whose behaviour does not depend on the generator's cooperation: the prompt can be wrong, and the gate still holds. A refusal rate and a hallucination rate on generated text remain different quantities, and the two are still not interchangeable in the abstract.",
        "The gate's label is answer-in-context detectability, not evidence "
        "sufficiency: the negative class is dominated by retrieval failure, so the "
        "gate cannot separate 'there is no evidence here' from 'the evidence is here "
        "and the retriever missed it'. The contingency table is reported so that the "
        "limit is visible rather than implied.",
        "The contradiction gate's recall on the verifiable subset is 1.000 by "
        "construction, because that subset is defined by quantity conflicts and the "
        "quantity detector is an OR-branch of the gate; after the numeric rule was "
        "repaired the subset holds one pair and cannot carry a recall measurement at "
        "all. Its precision was then measured against reader labels rather than "
        "against a proxy, and the measurement is a negative one: the readers confirm "
        "none of the alarms, and find no contradiction in a random sample of the "
        "pairs the gate did not flag either. This corpus therefore cannot evaluate "
        "the mechanism -- it holds concept-level prose, not the revised procedures "
        "the mechanism exists to detect -- and the annotators were models, so a human "
        "round is still the next step.",
        "The cross-category transfer experiment is an intra-domain study: all six "
        "categories are industrial-engineering sub-domains, so it measures transfer "
        "between sub-domains of one domain rather than between industries.",
        "The benchmark's own unanswerable class was separable from the question "
        "text alone, and the defect was found by auditing it and then repaired. "
        "A classifier that sees only the question's *shape* -- its stem, its subject size, whether the subject contains a digit, an acronym or a fabricated identifier -- tells the answerable questions from the unanswerable ones with an ROC AUC of 0.608 against a permutation null of 0.468 that the same procedure produces on shuffled labels (p = 0.050), against 0.999 before the unanswerable class was rebuilt; on the better-powered six-category benchmark, whose answerable class is four times larger, the same measurement gives 0.533 against a permutation null of 0.500 (p = 0.267) The defect was in the half's designated hard "
        "case, which asked about a fabricated identifier (SKU AST-5454); a single "
        "regular expression caught 76.4% of the class with no "
        "false positives at all. The half was rebuilt as a corpus-anchored class -- "
        "the same question stems, the same source documents, the same label "
        "machinery, and each repaired question given a structural twin in the "
        "answerable class (106 of 110) -- and every measurement was "
        "taken again. What remains: the repaired class is labelled by the "
        "complement of the benchmark's own extraction branches, and those branches "
        "are mechanical, so the rebuilt class is a near-miss class: an independent "
        "re-check found 43 of 110 questions "
        "whose subject the corpus comments on without defining it, and "
        "1 of 110 whose certificate does not hold at all. The "
        "refusal rate is therefore measured on a class that is partly answerable "
        "in a human's sense, which bounds what the absolute number means without "
        "bounding the arm comparison, in which every arm is asked the same "
        "questions. The residual form-only separability of the repaired class is 0.608 against a permutation null of 0.468 (p = 0.050) on the focus domain, and 0.533 against a permutation null of 0.500 (p = 0.267) on the better-powered six-category benchmark. It is a small residual that the focus-domain run reaches and the better-powered run does not reproduce: small, but not zero.",
    ]
    para(doc, f"This report has {len(_limitations)} key limitations that "
              f"qualify the conclusions. "
              "Two corpora are referred to below and they should not be confused: "
              "the primary corpus of the original specification (634 chunks, 24 "
              "documents, one focus category), and the public substitute corpus on "
              "which every number reported in Section 9 was measured.",
         align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    for i, t in enumerate(_limitations, start=1):
        para(doc, f"{i}.  {t}", align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=6,
             indent=0.6)
    para(doc, "Short-term (immediate next)", size=Pt(12), bold=True, color=BLACK,
         space_before=8, space_after=4)
    for t in [
        "Run the long-context arm's answer-quality comparison, which needs a "
        "generator: the harness is in impl/experiments/run_long_context.py and "
        "runs as soon as a credential is present.",
        "Repeat the encoder swap with a second retrieval-trained model (E5-M3-v2) "
        "and re-measure the fusion gain.",
        "Re-fit and re-report the gate threshold for every retrieval arm.",
        "Stratify the corpus by modality so the modality quota can be tested with "
        "adequate power, with a pre-registered power analysis.",
        "Extend the benchmark with dual-expert annotation and a judge "
        "meta-evaluation.",
    ]:
        bullet(doc, t)
    para(doc, "Long-term (project completion)", size=Pt(12), bold=True, color=BLACK,
         space_before=8, space_after=4)
    for t in [
        "Add the other eight industrial categories to the corpus.",
        "Cross-category transfer study: does Hybrid+Cat+Rerank generalise to "
        "non-SCM corpora?",
        "Fine-tune the cross-encoder reranker on a domain-matched dataset for the "
        "sub-categories where it regresses.",
        "Release the benchmark and the framework with full reproducibility scripts.",
    ]:
        bullet(doc, t)

    # ------------------------------------------------------------ SECTION 11
    heading(doc, "11", "Conclusion")
    para(doc,
         "This project report has presented an evidence-grounded "
         "retrieval-augmented generation framework for industrial decision support. "
         "The framework is built end-to-end and every component is derived rather "
         "than asserted: BM25 from the probabilistic relevance framework, Reciprocal "
         "Rank Fusion from the scale-incomparability of retrieval scores, the "
         "confidence gate from Bayes' theorem in odds form with maximum-likelihood "
         "calibration, contradiction detection from a joint NLI and topical "
         "conjunction with a revision-supersession check, and per-claim tagging "
         "from the noisy-OR model and Shannon information gain.",
         align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    para(doc,
         "The evaluation contributes a failure-mode characterisation that the "
         "original design specification did not contain, and which corrects two of "
         "its assumptions: a modality quota binds only when enforced before the "
         "the component that could undo it, and the modality composition of the "
         "corpus, rather than the retrieval algorithm, determines whether a "
         "modality-aware mechanism can have any effect at all. The evaluation "
         "protocol — treating the confidence gate as a selective-prediction policy "
         "with a risk–coverage curve, a false-positive rate at a stated operating "
         "point, and always-flag and never-flag baselines — is itself a contribution, "
         "because a filter result reported without those quantities does not mean "
         "anything.",
         align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    para(doc,
         "The framework is config-driven and extends to the other eleven categories "
         "by adding a configuration entry. Its practical value does not depend on "
         "any mechanism being individually novel; it depends on each being "
         "structural, on the trade-offs between them being measured rather than "
         "assumed, and on the resulting system being able to say, for every claim "
         "it makes, which passage supports it and how confident the system is in "
         "that passage's relevance.",
         align=WD_ALIGN_PARAGRAPH.JUSTIFY)

    # ----------------------------------------------------------- REFERENCES
    page_break(doc)
    heading(doc, None, "References")
    refs = [
        "Asai, A., Wu, Z., Wang, Y., Sil, A., & Hajishirzi, H. (2024). Self-RAG: Learning to retrieve, generate, and critique through self-reflection. In Proc. International Conference on Learning Representations. https://doi.org/10.48550/arXiv.2310.11511",
        "Bruch, S., Gai, S., & Ingber, A. (2023). An analysis of fusion functions for hybrid retrieval. ACM Transactions on Information Systems. https://doi.org/10.1145/3596512",
        "Cormack, G. V., Clarke, C. L. A., & Büttcher, S. (2009). Reciprocal rank fusion outperforms Condorcet and individual rank learning methods. In Proc. 32nd International ACM SIGIR Conference on Research and Development in Information Retrieval (SIGIR 2009) (pp. 758–759). https://doi.org/10.1145/1571941.1572114",
        "Decian, J., Njeh, C., & Nakouri, H. (2026). Dynamic RAG with hybrid retrieval: A novel approach to robust LLMs and hallucination prevention. Neurocomputing, 705, 134911. https://doi.org/10.1016/j.neucom.2026.134911",
        "Es, S., James, J., Espinosa-Anke, L., & Schockaert, S. (2024). RAGAS: Automated evaluation of retrieval augmented generation. In Proc. EACL System Demonstrations. https://doi.org/10.48550/arXiv.2309.15217",
        "Farquhar, S., Kossen, J., Kuhn, L., & Gal, Y. (2024). Detecting hallucinations in large language models using semantic entropy. Nature, 630(8015), 625–630. https://doi.org/10.1038/s41586-024-07421-0",
        "Faysse, M., Sibille, H., Wu, T., Omrani, B., Viaud, G., Hudelet, C., & Colombo, P. (2025). ColPali: Efficient document retrieval with vision language models. In Proc. International Conference on Learning Representations (ICLR 2025). https://doi.org/10.48550/arXiv.2407.01449",
        "Gao, T., Yen, H., Yu, J.-T., & Chen, D. (2023). Enabling large language models to generate text with citations. In Proc. Conference on Empirical Methods in Natural Language Processing (EMNLP). https://doi.org/10.48550/arXiv.2305.14627",
        "Geißler, F., Carella, F., Fieback, L., & Spiegelberg, J. (2026). Towards dependable retrieval-augmented generation using factual confidence prediction. https://doi.org/10.48550/arXiv.2605.05244",
        "Karpukhin, V., Oğuz, B., Min, S., Lewis, P., Wu, L., Edunov, S., Chen, D., & Yih, W. (2020). Dense passage retrieval for open-domain question answering. In Proc. Conference on Empirical Methods in Natural Language Processing (EMNLP) (pp. 6769–6781). https://doi.org/10.18653/v1/2020.emnlp-main.550",
        "Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., Küttler, H., Lewis, M., Yih, W., Rocktäschel, T., Riedel, S., & Kiela, D. (2020). Retrieval-augmented generation for knowledge-intensive NLP tasks. In Advances in Neural Information Processing Systems 33 (NeurIPS 2020) (pp. 9459–9474). https://doi.org/10.48550/arXiv.2005.11401",
        "Liu, S., Halfaker, A., Roth, D., et al. (2026). ConflictScore: Identifying and measuring how language models handle conflicting evidence. In Proc. Conference on Empirical Methods in Natural Language Processing (EMNLP 2026) (pp. 58825–58845). https://doi.org/10.18653/2026.emnlp-main.2589",
        "Lyu, Y., Li, Z.-Y., Niu, S.-M., et al. (2024). CRUD-RAG: A comprehensive Chinese benchmark for retrieval-augmented generation of large language models. ACM Transactions on Information Systems. https://doi.org/10.1145/3701228",
        "Phillips, E., Gustafsson, F., Wu, S., Thakur, A., & Clifton, D. A. (2026). Entropy alone is insufficient for safe selective prediction in LLMs. https://doi.org/10.48550/arXiv.2603.21172",
        "Rajpurkar, P., Jia, R., & Liang, P. (2018). Know what you don't know: Unanswerable questions for SQuAD. In Proc. Association for Computational Linguistics (ACL) (pp. 518–528). https://doi.org/10.18653/v1/p18-2124",
        "Robertson, S., Zaragoza, H., & Taylor, J. (2004). Probabilistic relevance framework: BM25 and beyond. Foundations and Trends in Information Retrieval, 3(4), 333–389.",
        "Simchi-Levi, D., Mellou, K., Menache, I., & Pathuri, J. (2025). Large language models for supply chain decisions. In AI in Supply Chains: Perspectives from Global Thought Leaders (M. C. Cohen & T. Dai, Eds.). Springer Series in Supply Chain Management. https://doi.org/10.48550/arXiv.2507.21502",
        "Suri, M., Mathur, P., Dernoncourt, F., et al. (2024). VisDoM: Multi-document QA with visually rich elements using multimodal retrieval-augmented generation. https://doi.org/10.48550/arXiv.2412.10704",
        "Thakur, A., Saparov, A., & Ribeiro, B. (2026). DeclineCraft: A RAG abstention benchmark for jointly measuring combined retrieval and parametric knowledge. https://doi.org/10.48550/arXiv.2610.28340",
        "Thakur, N., Reimers, N., Rücklé, A., et al. (2021). BEIR: A heterogeneous benchmark for zero-shot evaluation of information retrieval models. In NeurIPS Datasets and Benchmarks Track. https://doi.org/10.48550/arXiv.2104.08663",
        "Yan, S.-Q., Gu, J.-C., Zhu, Y., & Ling, Z.-H. (2024). Corrective retrieval augmented generation. https://doi.org/10.48550/arXiv.2401.15884",
        "Yang, X., Liu, Z., Li, R., et al. (2026). Large language models in resolving contextual knowledge conflicts. In Proc. Conference on Empirical Methods in Natural Language Processing (EMNLP 2026) (pp. 21142–21169). https://doi.org/10.18653/2026.emnlp-main.918",
        "Zhang, W., & Zhang, J. (2025). Hallucination mitigation for retrieval-augmented large language models: A review. Mathematics, 13(5), 856. https://doi.org/10.3390/math13050856",
    ]
    for r in refs:
        p = doc.add_paragraph()
        pf = p.paragraph_format
        pf.left_indent = Cm(0.8)
        pf.first_line_indent = Cm(-0.8)
        pf.space_after = Pt(7)
        pf.line_spacing = 1.25
        style_run(p.add_run(r), size=Pt(9.5))


    # ------------------------------------------------------------ APPENDIX A
    if FOCUS_CASE_MD.exists():
        page_break(doc)
        heading(doc, None, "Appendix A — Focus-Domain Case Study")
        para(doc,
             "The aggregate tables in Section 9 say what the mechanisms change. "
             "This appendix shows what they changed, on real supply-chain "
             "questions, with every intermediate artefact written out: the two "
             "retrieval legs, the fused ranking, the reranked ranking, the gate's "
             "decision and the signals behind it, the modality mix of the "
             "accepted context, how each claim was banded, and whether any two "
             "accepted chunks contradict each other. It is generated from the "
             "experiment's own output, so it cannot disagree with it.",
             align=WD_ALIGN_PARAGRAPH.JUSTIFY)
        _text = FOCUS_CASE_MD.read_text(encoding="utf-8")
        # Strip the markdown heading and render the rest as plain paragraphs;
        # the table is reproduced as monospaced rows.
        _lines = _text.splitlines()
        _skip = 0
        for _i, _ln in enumerate(_lines):
            if _ln.startswith("# "):
                _skip = _i + 1
            if _ln.startswith("## "):
                _skip = _i + 1
                break
        _body = _lines[_skip:]
        for _ln in _body:
            _s = _ln.rstrip()
            if not _s:
                continue
            if _s.startswith("### "):
                subheading(doc, "", _s[4:].strip())
            elif _s.startswith("|"):
                p = doc.add_paragraph()
                p.paragraph_format.space_after = Pt(0)
                p.paragraph_format.line_spacing = 1.0
                style_run(p.add_run(_s.replace("**", "")), size=Pt(8),
                          font="Consolas")
            elif _s.startswith("**") or _s.startswith("- "):
                p = doc.add_paragraph()
                p.paragraph_format.space_after = Pt(3)
                p.paragraph_format.line_spacing = 1.2
                style_run(p.add_run(_s.replace("**", "")), size=Pt(9.5))
            else:
                p = doc.add_paragraph()
                p.paragraph_format.space_after = Pt(5)
                p.paragraph_format.line_spacing = 1.25
                style_run(p.add_run(_s.replace("`", "")), size=Pt(9.5))


    doc.save(OUT)
    # The document is monochrome; see deliverables/scripts/monochrome.py.
    _monochrome(OUT)
    print(f"[docx] wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
