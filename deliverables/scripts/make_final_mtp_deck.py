#!/usr/bin/env python3
"""Build the final MTP presentation: a ten-minute defence deck.

Twenty-five slides, one idea each, sized for the slot the defence actually
has. Every figure, table and formula the talk depends on is here, and every
number comes from the archived result files through the measured-value table,
so the deck cannot disagree with the report or with the papers.

Its theme is its own: one column, one accent, a lot of white, and a sentence
under every title saying what the slide establishes. The institute's emblem
is in the top right corner of every slide.

The complete deck, with every table and every formula at full size, is built
by `make_final_mtp_reference.py` and is the document to open when a question
goes deeper than a slide.

Usage:
    .venv/bin/python deliverables/scripts/make_final_mtp_deck.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

import final_mtp_diagram as _diagram  # noqa: E402
from final_mtp_refs import IEEE_REFS  # noqa: E402
import substitute_tokens as _st  # noqa: E402
from final_mtp_theme import (ACCENT, CW, GREY, GREY_LIGHT, INK, INK_SOFT,  # noqa: E402
                             ML, RULE, SURFACE, WHITE, Deck)
from monochrome import ACCENT as ACCENT_HEX, to_monochrome as _monochrome  # noqa: E402
from pptx.util import Inches  # noqa: E402

OUT = ROOT / "deliverables" / "final_mtp.pptx"
FOCUS_RESULTS = ROOT / "impl" / "results_focus"

V = _st.values()


def t(name: str, default: str = "") -> str:
    return str(V.get(name, default))


#: The superscript digits, so that a p value written as "10^-4" can be read
#: back out of a token.
_SUPERSCRIPT = {"⁰": 0, "¹": 1, "²": 2, "³": 3, "⁴": 4,
                "⁵": 5, "⁶": 6, "⁷": 7, "⁸": 8, "⁹": 9}


def pnum(token: str) -> str:
    """A p value in a form that survives a projector.

    The token carries a superscript minus, and Times New Roman has no glyph
    for it, so "2.5 x 10^-2" would arrive on the slide with a missing
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


def pv(token: str) -> str:
    """A p value written for a sentence: 'p < 0.001' or 'p = 0.002'.

    A token that is already an inequality carries its own sign, so putting
    an equals sign in front of it reads as 'p = < 0.001'.
    """
    token = token.strip()
    if token.startswith("<"):
        return "p " + token
    return "p = " + token


def focus_sweep() -> list[dict]:
    """The gate's threshold sweep, read from the archived focus run."""
    path = FOCUS_RESULTS / "exp2_gate.json"
    if not path.exists():
        return []
    doc = json.loads(path.read_text(encoding="utf-8"))
    return doc.get("threshold_sweep", [])


FOOTER = ("MTP  |  An Evidence-Grounded RAG Framework for Industrial "
          "Decision Support  |  Ritik Raj 25IM60R12  |  IIT Kharagpur, ISE")

TITLE_TEXT = ("An Evidence-Grounded Retrieval-Augmented Generation Framework "
              "for Industrial Decision Support")
SUBTITLE = ("Architecture, evaluation protocol, failure modes, and what the "
            "measurements show")

deck = Deck(FOOTER)


# ------------------------------------------------------------------- front
def slide_title():
    image = ROOT / "deliverables" / "assets" / "mtp_intent.png"
    credits = [
        ([("Presented by   ", True, ACCENT), ("Ritik Raj", True, INK),
          ("      Roll No. 25IM60R12", False, INK_SOFT)], 15),
        ([("Under the supervision of   ", False, GREY),
          ("Dr. Sri Krishna Kumar", False, INK_SOFT)], 13.5),
        ([("Department of Industrial and Systems Engineering, "
           "IIT Kharagpur", False, GREY)], 12.5),
    ]
    s = deck.title_slide(TITLE_TEXT, SUBTITLE, image, credits)
    

# ---------------------------------------------------------------- objective
def slide_problem():
    deck.part = "objective"
    s = deck.slide("A wrong answer and a non-answer do not cost the same",
                   "This asymmetry is the reason the whole framework exists.")
    deck.prose(s, ML, 2.02, 6.55, 3.62, [
        ("A retrieval-augmented generator reads a corpus and answers a "
         "question. In industry the corpus is not a wiki. It is a controlled "
         "set of documents somebody signed off on, and the questions are "
         "operational decisions: whether a part's tolerance is acceptable, "
         "which step of a procedure applies, what a specification requires."),
        ("A refusal costs a supervisor five minutes. A confidently fabricated "
         "tolerance costs a scrapped batch. ", "So the question is not whether "
         "retrieval-augmented generation works. It is whether the component "
         "that decides to answer can be measured at all, and what that "
         "decision is worth once it has been measured properly."),
    ])
    deck.card(s, 7.62, 2.02, 5.01, 3.62, "The scope of the claims", [
        ("An encyclopaedic corpus, not a procedural one. ", "A primary "
         "corpus is proprietary supply-chain text and cannot be "
         "redistributed, so every measurement runs on a public substitute "
         "that ships with its provenance."),
        ("One generator. ", "A replication on a second model could not be "
         "run, because that model returned no text on "
         + t("GENCOMP_FAILING_EMPTY_N") + " of "
         + t("GENCOMP_FAILING_EMPTY_TOTAL") + " questions."),
        ("One corpus for long context. ", "The cross-category corpus does not "
         "fit a 128K-token window, so there the comparison is settled on "
         "cost and coverage alone."),
    ], size=16, bsize=13)
    deck.takeaway(s, "The question",
                  "Can a gate in the code decide whether the retrieved "
                  "industrial evidence actually contains the answer?")
    

def slide_objectives():
    deck.part = "objective"
    s = deck.slide("Four objectives, six contributions",
                   "Each objective is something that had to be built and "
                   "then measured.")
    deck.table(s, ML, 2.02, 5.90, ["", "Research objective"], [
        ["RO1", "Build an evidence-grounded framework, with generation gated "
         "in code"],
        ["RO2", "Make retrieval modality-balanced and category-aware"],
        ["RO3", "Test the framework's own hypothesis against a generator "
         "required to answer"],
        ["RO4", "Characterise the failure modes, including the ones that "
         "contradict the framework"],
    ], col_widths=[0.13, 0.87], size=12.5, head_size=12.5, row_h=0.62,
        head_h=0.36, bold_first=True)
    deck.table(s, 6.86, 2.02, 5.75, ["", "Contribution"], [
        ["1", "The framework, with a gate that cannot be bypassed"],
        ["2", "A repaired refusal benchmark, with its shortcut audit "
         "published alongside it"],
        ["3", "A two-condition test of the framework's own hypothesis"],
        ["4", "A random-escalation control, which isolates what the "
         "confidence score buys"],
        ["5", "A reader-label measurement of the contradiction gate"],
        ["6", "An error profile for the claim scorer, published with the "
         "benchmark"],
    ], col_widths=[0.08, 0.92], size=12.5, head_size=12.5, row_h=0.50,
        head_h=0.36, bold_first=True)
    deck.takeaway(s, "RO3 decides the design",
                  "If the generator is allowed to decline, the gate's "
                  "contribution cannot be separated from the generator's "
                  "willingness to answer. So one arm of the experiment makes "
                  "an answer compulsory.")
    

# -------------------------------------------------------------- literature
def slide_literature():
    deck.part = "literature"
    s = deck.slide("The literature, in eight threads",
                   "What each thread shows, and what is taken from it.")
    rows = [
        ["RAG and its evaluation",
         "A dense retriever and a reader, judged by citation precision and "
         "recall.",
         "Lewis et al. (2020); Karpukhin et al. (2020)",
         "Both miss the decision to answer at all."],
        ["Confidence and abstention",
         "Abstention as conformal prediction, with a coverage guarantee.",
         "Yadkori et al. (2024)",
         "Calibrate the score first, then measure the calibration."],
        ["Sufficiency and risk-coverage",
         "Accuracy is conditional on the context being sufficient, not "
         "present.",
         "Joren et al. (2024)",
         "The operating point is a pair of coverage and risk."],
        ["The selection effect",
         "A gate forwards a slice on which the downstream component is no "
         "better.",
         "Tikhomirov and Savchenko (2026)",
         "A null under a cautious prompt is never read as gating failing."],
        ["Fusion and reranking",
         "BM25 and a dense leg joined by reciprocal rank fusion.",
         "Cormack et al. (2009)",
         "The fusion function, and the counter-evidence about rerankers."],
        ["Contradiction detection",
         "Rerankers must be optimised for semantic conflict, not topical "
         "similarity.",
         "Several 2024 to 2026 studies",
         "A detector judged against its own threshold measures agreement."],
        ["Evaluation of abstention",
         "An unanswerable question must be plausible, or nothing is "
         "measured.",
         "Rajpurkar et al. (2018)",
         "The reason the shortcut found here was treated as a defect."],
        ["Industrial retrieval",
         "Industrial RAG is built far more often than it is measured.",
         "Industrial and regulated deployments",
         "A measurement on encyclopaedic industrial text."],
    ]
    deck.table(s, ML, 2.02, CW, ["Thread", "What it shows",
                                  "Representative work", "What is taken from it"],
               rows, col_widths=[0.15, 0.30, 0.19, 0.36], size=12,
               head_size=12, row_h=0.52, head_h=0.36, bold_first=True)
    

def slide_references():
    deck.part = "references"
    s = deck.slide("The references",
                   "The eight works the work stands on. Every mechanism "
                   "here is already in the literature.")
    tf = deck.text(s, ML, 2.02, CW, 4.60)
    for i, (citation, _use) in enumerate(IEEE_REFS):
        deck.para(tf, citation, size=12, color=INK_SOFT, space_after=8,
                  first=(i == 0), line=1.16)
    

def slide_gap():
    deck.part = "literature"
    s = deck.slide("The gap, and what this work adds",
                   "The mechanism is prior art. What the review does not "
                   "settle is the measurement of it.")
    deck.card(s, ML, 2.02, 3.87, 3.68, "What the literature already provides", [
        ("The abstention mechanism. ", "Conformal abstention with a coverage "
         "guarantee (Yadkori et al., 2024)."),
        ("The retrieval stack. ", "BM25, dense retrieval, rank fusion and a "
         "reranker, all from the literature."),
        ("The benchmark desiderata. ", "An unanswerable question must be "
         "plausible (Rajpurkar et al., 2018)."),
    ], size=16, bsize=13)
    deck.card(s, 4.77, 2.02, 3.87, 3.68, "What the review does not settle", [
        ("What a confidence score buys ", "once the generator is not allowed "
         "to decline."),
        ("Whether the shortcuts that inflate refusal rates ", "carry over to "
         "a retrieval-augmented benchmark."),
        ("Where the cost-coverage-reliability frontier sits ", "for a gate on "
         "industrial text."),
    ], size=16, bsize=13)
    deck.card(s, 8.82, 2.02, 3.79, 3.68, "What this work adds", [
        ("A five-stage framework whose gate cannot be bypassed, ", "measured "
         "end to end against a random-escalation control."),
        ("A repaired refusal benchmark, ", "with its shortcut audit "
         "published alongside it."),
        ("A frontier at claim level, ", "on encyclopaedic industrial text, "
         "with negative results reported in the same voice."),
    ], size=16, bsize=13)
    deck.takeaway(s, "The contribution",
                  "The architecture is not the contribution. The measurement "
                  "of it, on industrial text, against a control that ignores "
                  "the score, is.")
    

# --------------------------------------------------------------- framework
def slide_framework():
    deck.part = "framework"
    s = deck.slide("The framework is a five-stage pipeline",
                   "A request enters at stage 0 and leaves at stage 4 as a "
                   "refusal or as a set of per-claim annotations.")
    s.shapes.add_picture(str(_diagram.build()), Inches((13.333 - 9.60) / 2),
                         Inches(2.00), width=Inches(9.60))
    rows = [
        ["0", "Query-form validation", "the raw query string",
         "a query or a refusal", "yes"],
        ["1", "Hybrid retrieval", "the query", "a candidate pool",
         "no"],
        ["2", "Rerank and quota", "the candidate pool",
         "a final context of " + t("RERANK_TOP_K_FINAL") + " chunks", "no"],
        ["3", "Confidence gate", "the final context", "accept or refuse", "yes"],
        ["4", "Generation and claim assessment", "the accepted context",
         "an annotated answer", "no"],
    ]
    deck.table(s, ML, 4.48, CW, ["", "Stage", "Input", "Output", "May refuse"],
               rows, col_widths=[0.04, 0.30, 0.22, 0.30, 0.14], size=12.5,
               head_size=12.5, row_h=0.34, head_h=0.36, bold_first=True)
    

def slide_gate():
    deck.part = "framework"
    s = deck.slide("The confidence gate, and its three formulas",
                   "The mechanism the talk is about: does the context "
                   "contain evidence the question can be answered from?")
    bands = [
        (r"\phi(q)=\left[s^{(1)}_{\mathrm{rerank}},\ "
         r"\bar{s}^{(3)}_{\mathrm{rerank}},\ s^{(1)}_{\mathrm{bm25}},\ "
         r"\max_d S_{\mathrm{RRF}}(d),\ |\{d\in\mathcal{C}: "
         r"s_{\mathrm{rerank}}(d)>\beta\}|\right]", 13),
        (r"p_{\mathrm{conf}}(q)=\sigma\left(\beta_0+"
         r"\boldsymbol{\beta}_1^{\mathsf{T}}"
         r"\frac{\phi(q)-\boldsymbol{\mu}}{\boldsymbol{\sigma}}"
         r"\right),\qquad \sigma(z)=\frac{1}{1+e^{-z}}", 17),
        (r"\mathrm{accept}(q)=\mathbf{1}\left[p_{\mathrm{conf}}(q)"
         r"\geq\tau\right]", 20),
    ]
    y = 2.02
    for latex, fs in bands:
        deck.rect(s, ML, y, 6.10, 1.16, SURFACE)
        deck.put_formula(s, latex, ML + 0.25, y + 0.20, 5.60, max_h=0.76,
                         fontsize=fs, centre_w=5.60)
        y += 1.26
    deck.table(s, 7.10, 2.02, 5.52, ["Symbol", "What it is"], [
        ["phi(q)", "five statistics of the pool"],
        ["s_rerank", "the cross-encoder's score for a chunk"],
        ["beta", "the reranker's own relevance bar"],
        ["p_conf(q)", "the probability the answer is there"],
        ["beta_0, beta_1", "the fitted intercept and weights"],
        ["mu, sigma", "the calibration split's spread"],
        ["sigma(z)", "the logistic function, into [0,1]"],
        ["tau", "the operating point (" + t("FOCUS_GATE_TAU") + ")"],
        ["1[...]", "1 if the condition holds, 0 otherwise"],
    ], col_widths=[0.32, 0.68], size=12.5, head_size=12.5, row_h=0.30,
        head_h=0.34, bold_first=True)
    deck.block(s, 7.10, 5.16, 5.52, 1.46, "Where these come from",
               "Platt scaling on a feature vector, fitted by maximum "
               "likelihood on 60 percent of the queries. The threshold "
               "follows a stated rule: the highest that still answers 90 "
               "percent of the answerable questions. Every feature describes "
               "the pool, not a chunk.")
    

def slide_retrieval():
    deck.part = "framework"
    s = deck.slide("The retrieval stack, and its three formulas",
                   "A lexical leg and a dense leg, fused by rank, then "
                   "reranked, with a floor on tables and charts.")
    bands = [
        (r"\mathrm{BM25}(q,d)=\sum_{t\in q}\mathrm{IDF}(t)\cdot"
         r"\frac{f_{t,d}(k_1+1)}{f_{t,d}+k_1\left(1-b+b"
         r"\frac{|d|}{\mathrm{avgdl}}\right)}", 14),
        (r"S_{\mathrm{RRF}}(d)=\sum_{r\in\mathcal{R}}"
         r"\frac{1}{k_{\mathrm{RRF}}+\mathrm{rank}_r(d)},\qquad "
         r"k_{\mathrm{RRF}}=60", 17),
        (r"q_m=\min\left(n_m,\left\lceil \alpha_m\,|\mathcal{C}|"
         r"\right\rceil\right),\qquad \alpha_{\mathrm{table}}=0.15,\ "
         r"\alpha_{\mathrm{chart}}=0.05", 16),
    ]
    y = 2.02
    for latex, fs in bands:
        deck.rect(s, ML, y, 6.10, 1.16, SURFACE)
        deck.put_formula(s, latex, ML + 0.25, y + 0.20, 5.60, max_h=0.76,
                         fontsize=fs, centre_w=5.60)
        y += 1.26
    deck.table(s, 7.10, 2.02, 5.52, ["Symbol", "What it is"], [
        ["BM25(q,d)", "the lexical score of chunk d"],
        ["IDF(t)", "how rare the word is, on a log scale"],
        ["f(t,d)", "how often the word occurs in the chunk"],
        ["k1, b: " + t("BM25_K1") + ", 0.75", "the saturation and length knobs"],
        ["S_RRF(d)", "the fused score of the chunk"],
        ["rank_r(d)", "where the chunk sits in list r"],
        ["k_RRF", "the smoothing constant, set to " + t("RRF_K")],
        ["q_m", "the quota for modality m"],
        ["alpha_m", "the share the context should give it"],
    ], col_widths=[0.32, 0.68], size=12.5, head_size=12.5, row_h=0.30,
        head_h=0.34, bold_first=True)
    deck.block(s, 7.10, 5.16, 5.52, 1.46, "Where these come from",
               "Okapi BM25 with the Robertson-Sparck-Jones IDF, and reciprocal "
               "rank fusion from Cormack et al. The quota is a floor, not a "
               "ceiling: when the pool cannot supply it the floor is relaxed "
               "rather than invented.")
    

# -------------------------------------------------------------- methodology
def slide_dataset():
    deck.part = "methodology"
    s = deck.slide("The corpora and the benchmark",
                   "Questions are generated against chunks that state their "
                   "answer, and against documents that do not.")
    rows = [
        ["Supply-chain focus", "The ablation, the gate, the generation "
         "experiment", t("SCOPE_SCM_CHUNKS"), t("SCOPE_SCM_DOCS"),
         t("CASE_N_QUERIES")],
        ["Six-category industrial", "Cross-category transfer, and the cost "
         "half of the long-context comparison", t("N_CHUNKS"),
         t("N_DOCUMENTS"), t("MC_N_QUERIES")],
        ["Industrial", "The candidate-pool curve and the quota trade",
         t("IND_N_CHUNKS"), t("IND_N_DOCUMENTS"), t("IND_N_QUERIES")],
        ["Federal regulatory", "The contradiction detector's phenomenon",
         t("SCOPE_RE_CHUNKS"), t("SCOPE_RE_DOCS"), "none"],
    ]
    deck.table(s, ML, 2.02, CW, ["Corpus", "Role", "Chunks", "Documents",
                                  "Queries"],
               rows, col_widths=[0.20, 0.44, 0.12, 0.13, 0.11], size=12.5,
               head_size=12.5, row_h=0.58, head_h=0.36, bold_first=True)
    deck.bullets(s, ML, 4.78, 6.55, [
        ("The focus corpus carries ", t("CASE_N_ANSWERABLE") + " answerable "
         "and " + t("CASE_N_UNANSWERABLE") + " unanswerable questions; the "
         "cross-category corpus carries " + t("MC_N_ANSWERABLE") + " and "
         + t("MC_N_UNANSWERABLE") + ". Their numbers are never mixed."),
        ("Every chunk carries its modality, ", "its category and its source "
         "document, and the chunk identifier is unique across the corpus."),
    ], size=13.5, gap=9, h=1.94)
    deck.card(s, 7.62, 4.78, 5.01, 1.80, "The public corpus ships with its "
             "provenance", [
        ("Each document carries the upstream identifier, ", "a SHA-256 of the "
         "content, the chunk count and the licence, so the corpus can be "
         "traced."),
    ], size=16, bsize=13)
    

def slide_benchmark():
    deck.part = "methodology"
    s = deck.slide("The benchmark, and the audit that checks it",
                   "Both classes use the same three stems, so a difference "
                   "between them is a difference in the evidence.")
    deck.prose(s, ML, 2.02, 6.55, 3.60, [
        ("Answerable questions are generated against chunks that state their "
         "answer, ", "so each has a gold chunk and a gold answer. "
         "Unanswerable questions are generated against documents that do not, "
         "so the question looks answerable and is not."),
        ("The unanswerable class is corpus-anchored. ", "Every question has a "
         "structural twin in the answerable class: same stem, same subject "
         "size, same shape markers, and no word in common."),
        ("Both classes use the same three stems, ", "the same source "
         "documents and the same label machinery, and every question carries "
         "its family, so a rate can be read per family."),
    ])
    deck.table(s, 7.62, 2.02, 5.01, ["The audit", "Reading"], [
        ["Structural certificates passed", t("UNANS_MATCH_RATE")],
        ["Identifier-shortcut detection", t("UNANS_SHORTCUT_AFTER")],
        ["Question-only policy, focus", "ROC AUC " + t("UNANS_POLICY_AUC")],
        ["Policy, six-category corpus",
         "ROC AUC " + t("UNANS_MC_SEP_AUC")],
        ["Closed-book unanswerable rate", t("UNANS_CLOSED_BOOK_ACC")],
        ["Refusal rate, hard stratum", t("UNANS_HARD_REFUSED_PCT")],
    ], col_widths=[0.62, 0.38], size=12.5, head_size=12.5, row_h=0.46,
        head_h=0.36, bold_first=True)
    deck.takeaway(s, "What the audit is for",
                  "A benchmark whose unanswerable half can be told apart by "
                  "the shape of the question reports its own shortcut rather "
                  "than the system's capability. These are the readings that "
                  "say the class does not.")
    

def slide_metrics():
    deck.part = "methodology"
    s = deck.slide("The metrics and the protocol",
                   "Three retrieval measures, two generation rates, and one "
                   "paired test, applied per class.")
    deck.rect(s, ML, 2.02, 6.10, 1.16, SURFACE)
    deck.put_formula(
        s, r"\mathrm{Recall}@k=\frac{|R_k\cap G|}{|G|},\qquad "
           r"\mathrm{MRR}=\frac{1}{|Q|}\sum_{q\in Q}\frac{1}"
           r"{\mathrm{rank}_q},\qquad \mathrm{nDCG}@k="
           r"\frac{\mathrm{DCG}@k}{\mathrm{IDCG}@k}",
        ML + 0.25, 2.22, 5.60, max_h=0.76, fontsize=13, centre_w=5.60)
    deck.rect(s, ML, 3.28, 6.10, 1.16, SURFACE)
    deck.put_formula(
        s, r"r_{\mathrm{ans}}(U)=\frac{|\{q\in U:\mathrm{answered}(q)\}|}"
           r"{|U|},\qquad \mathrm{Prec}_{\mathrm{ref}}=\frac{"
           r"|\mathrm{refused}\cap U|}{|\mathrm{refused}|}",
        ML + 0.25, 3.48, 5.60, max_h=0.76, fontsize=16, centre_w=5.60)
    deck.rect(s, ML, 4.54, 6.10, 1.16, SURFACE)
    deck.put_formula(
        s, r"p=2\sum_{k=0}^{\min(b,c)}\binom{n}{k}\left(\frac{1}{2}"
           r"\right)^{n}",
        ML + 0.25, 4.74, 5.60, max_h=0.76, fontsize=21, centre_w=5.60)
    deck.table(s, 7.10, 2.02, 5.52, ["Symbol", "What it is"], [
        ["R_k, G", "the top k results, and the gold chunks"],
        ["rank_q", "the rank of the gold chunk"],
        ["DCG@k", "the position-weighted gain"],
        ["U", "a class of queries"],
        ["r_ans(U)", "the share of that class answered"],
        ["refused", "the set of queries the gate refused"],
        ["Prec_ref", "the share of refusals that were right"],
        ["b, c, n", "the discordant counts and their sum"],
    ], col_widths=[0.32, 0.68], size=12.5, head_size=12.5, row_h=0.30,
        head_h=0.34, bold_first=True)
    deck.block(s, 7.10, 4.98, 5.52, 1.58, "The protocol",
               "Every comparison is paired, because the arms answer the same "
               "questions. Every test is applied per class, because a gate can "
               "improve the unanswerable class and damage the answerable one "
               "at the same time.")
    

# ----------------------------------------------------------------- results
def slide_retrieval_results():
    deck.part = "results / retrieval"
    s = deck.slide("Retrieval: seven configurations over the same 32 queries",
                   "The lexical leg alone, the dense leg alone, then each "
                   "component added in turn. Paired tests throughout.")
    rows = [
        ["A. BM25 alone", t("R_A"), t("MRR_A"),
         t("NDCG_A"), t("TBL_A")],
        ["B. Dense alone", t("R_B"), t("MRR_B"), t("NDCG_B"),
         t("TBL_B")],
        ["C. Fusion by RRF", t("R_C"), t("MRR_C"), t("NDCG_C"),
         t("TBL_C")],
        ["D. + cross-encoder", t("R_D"), t("MRR_D"), t("NDCG_D"),
         t("TBL_D")],
        ["E. + category pre-filter", t("R_E"), t("MRR_E"), t("NDCG_E"),
         t("TBL_E")],
        ["F. + quota, pre-rerank", t("R_F"), t("MRR_F"),
         t("NDCG_F"), t("TBL_F")],
        ["G. + quota, post-rerank", t("R_G"), t("MRR_G"),
         t("NDCG_G"), t("TBL_G")],
    ]
    deck.table(s, ML, 2.02, 7.20, ["System", "Recall@10", "MRR", "nDCG@10",
                                    "Table R@10"],
               rows, col_widths=[0.38, 0.155, 0.155, 0.155, 0.155], size=12.5,
               head_size=12.5, row_h=0.34, head_h=0.36, bold_first=True)
    deck.prose(s, 8.40, 2.02, 4.20, 3.68, [
        ("The dense leg is significantly worse than the lexical leg here. ",
         "Recall@10 falls from " + t("R_A") + " to " + t("R_B") + ", a paired "
         "difference of 0.156 in favour of the lexical leg (Cohen's d_z = "
         + t("ABL_DZ_AB") + ", Cliff's delta = " + t("ABL_CD_AB") + "), at "
         "p = " + pnum(t("P_AB")) + ". That is why the encoder was replaced."),
        ("Fusion recovers the loss. ", "Recall@10 reaches " + t("R_C") +
         " against " + t("R_B") + " for the dense leg alone (Cohen's d_z = "
         + t("ABL_DZ_BC") + "), at p = " + pnum(t("P_BC")) + ". The claim is "
         "narrow: fusion stopped being a loss, and did not become a "
         "significant win over plain BM25."),
    ], size=13.5, gap=10)
    deck.takeaway(s, "The reranker",
                  "It moves MRR by " + t("RERANK_MRR_PP") + " points on the "
                  "focus corpus and by " + t("MC_MRR_RERANK_PP") + " points on "
                  "the cross-category one. A component that helps on one "
                  "corpus and not on another is not a component that helps.")
    

def slide_quota():
    deck.part = "results / retrieval"
    s = deck.slide("The quota has no universally better placement",
                   "The direction reverses between corpora, and none of the "
                   "three differences is significant.")
    rows = [
        ["Supply-chain focus", t("QUOTA_PRE_FOCUS_R10"),
         t("QUOTA_POST_FOCUS_R10"), t("QUOTA_PLACE_FOCUS_P")],
        ["Six-category industrial", t("QUOTA_PRE_SIXCAT_R10"),
         t("QUOTA_POST_SIXCAT_R10"), t("QUOTA_PLACE_SIXCAT_P")],
        ["Industrial", t("QUOTA_PRE_IND_R10"), t("QUOTA_POST_IND_R10"),
         t("QUOTA_PLACE_IND_P")],
    ]
    deck.table(s, ML, 2.02, 7.20, ["Corpus", "Quota before the reranker",
                                    "Quota after it", "p"],
               rows, col_widths=[0.37, 0.26, 0.22, 0.15], size=12.5,
               head_size=12, row_h=0.44, head_h=0.50, bold_first=True)
    deck.figure(s, "fig4_modality_quota_pareto", 8.60, 2.02, 3.90)
    deck.caption(s, 8.50, 5.40, 4.10, 1,
                 "Overall Recall@10 against table-specific Recall@10 for the "
                 "seven ablated systems, on the focus corpus (black circles) "
                 "and the industrial corpus (grey squares).")
    deck.takeaway(s, "What follows",
                  "The placement is a configuration value rather than a rule, "
                  "and the ranking is reported with its corpus attached.",
                  x=ML, w=7.20, y=4.00, h=1.10, stacked=True)
    

def slide_pool():
    deck.part = "results / retrieval"
    s = deck.slide("More candidates are not monotonically better",
                   "The pool curve peaks and then declines, and which way it "
                   "fails depends on the corpus.")
    deck.figure(s, "fig1_pool_size", ML, 2.02, 3.90)
    deck.caption(s, 4.95, 2.02, 7.66, 2,
                 "Recall against the size of the rerank candidate pool, on the "
                 "focus corpus and the industrial corpus. The focus curve "
                 "saturates at a pool of ten and then falls slightly as the "
                 "reranker is given more candidates to reorder.")
    deck.prose(s, 4.95, 3.00, 7.66, 2.00, [
        ("On the focus corpus ", "Recall@10 peaks with a pool of ten and "
         "falls back to " + t("FOCUS_POOL_R10_AT_20") + " at twenty, "
         "fifty and a hundred."),
        ("What the recall at twenty shows ", "is that the gold chunk is still "
         "being found, and then the reranker pushes it out of the ten-chunk "
         "context. A larger pool costs ordering without adding the answer."),
    ], size=13.5, gap=9)
    deck.block(s, 4.95, 5.06, 7.66, 1.46, "The industrial corpus is the "
               "exception, and the exception is the point",
               "There the gold chunk is still arriving at twenty and fifty, so "
               "Recall@20 reaches " + t("IND_POOL_R20_AT_50") + " at a pool of "
               "fifty while Recall@10 stays at " + t("IND_POOL_R10_AT_50") +
               ". Some 1.21 points of gold are retrieved and then pushed out "
               "of the ten-chunk context.")
    

def slide_frontier():
    deck.part = "results / the gate"
    s = deck.slide("The operating point, and the frontier behind it",
                   "The threshold follows a stated rule, and the whole "
                   "frontier is shown, not one point on it.")
    rows = []
    for r in focus_sweep():
        tau = r["tau"]
        if tau not in (0.05, 0.10, 0.15, 0.20, 0.30, 0.50, 0.90):
            continue
        rows.append([f"{tau:.2f}", f"{r['answerable_answered']:.3f}",
                     f"{r['unanswerable_refused']:.3f}",
                     f"{r['abstention_precision']:.3f}",
                     f"{r['coverage']:.3f}"])
    deck.table(s, ML, 2.02, 7.20, ["tau", "Answerable answered",
                                   "Unanswerable refused",
                                   "Abstention precision", "Coverage"],
               rows, col_widths=[0.12, 0.22, 0.22, 0.24, 0.20], size=12.5,
               head_size=12, row_h=0.34, head_h=0.52, bold_first=True)
    deck.figure(s, "fig2_risk_coverage", 8.60, 2.02, 3.90)
    deck.caption(s, 8.50, 5.78, 4.10, 3,
                 "Risk-coverage of the gate: the risk that an answered query "
                 "has no answer in its context, against the fraction of "
                 "queries the gate answers.")
    deck.takeaway(s, "The trade",
                  "At the fitted point the coverage is "
                  + t("FOCUS_GATE_COVERAGE") + " and the abstention precision "
                  "is " + t("FOCUS_GATE_ABST_PRECISION") + ". The calibration "
                  "error is " + t("GATE_ECE") + ", reported rather than "
                  "improved by refitting.",
                  x=ML, w=7.20, y=5.00, h=1.10, stacked=True)
    

def slide_audit():
    deck.part = "results / the gate"
    s = deck.slide("The gate on the unanswerable class",
                   "The class the gate refuses, and the question-only classifier "
                   "that audits it.")
    deck.figure(s, "fig5_question_only_roc", ML, 2.02, 3.90)
    deck.caption(s, 4.95, 2.02, 7.66, 4,
                 "A classifier that sees only the question text, with no "
                 "retrieval, no evidence and no corpus. Its discrimination is "
                 "the audit of the benchmark, and the dashed line is chance.")
    rows = [
        ["Gate refusal rate on the hard stratum",
         t("UNANS_HARD_REFUSED_PCT") + " of " + t("UNANS_HARD_N")],
        ["Gate refusals on the out-of-domain stratum",
         t("UNANS_OOD_REFUSED_N")],
        ["Abstention precision at the fitted operating point",
         t("FOCUS_GATE_ABST_PRECISION")],
        ["Separability from the question's shape (ROC AUC)",
         t("UNANS_SEP_AUC")],
    ]
    deck.table(s, 4.95, 2.98, 7.66, ["What the gate does with the class",
                                     "Reading"],
               rows, col_widths=[0.70, 0.30], size=12.5, head_size=12.5,
               row_h=0.46, head_h=0.44, bold_first=True)
    deck.block(s, 4.95, 5.34, 7.66, 1.30, "The finding",
               "What the gate detects is a recognisable unanswerable "
               "question, one drawn from outside the corpus or one whose "
               "subject is plainly absent. It is much weaker on the "
               "on-topic-but-unanswered case, where the corpus discusses the "
               "subject but does not state the answer. The gap between the "
               "two strata is the finding.")
    

def slide_verdict():
    deck.part = "results / the generator"
    s = deck.slide("The framework's own hypothesis, under two conditions",
                   "The generator must answer in one condition and may "
                   "decline in the other. Nothing else changes.")
    rows = [
        ["rag_nogate", t("GEN_A_NOGATE_UNANS_ANSWERED") + " ("
         + t("GEN_A_NOGATE_UNANS_ANSWER_RATE") + ")",
         t("GEN_A_NOGATE_ANS_ANSWERED") + " ("
         + t("GEN_A_NOGATE_ANS_ANSWERED_RATE") + ")",
         t("GEN_A_NOGATE_UNANS_MCNEMAR"), t("GEN_A_NOGATE_ANS_MCNEMAR")],
        ["rag@fitted", t("GEN_A_FITTED_UNANS_ANSWERED") + " ("
         + t("GEN_A_FITTED_UNANS_ANSWER_RATE") + ")",
         t("GEN_A_FITTED_ANS_ANSWERED") + " ("
         + t("GEN_A_FITTED_ANS_ANSWERED_RATE") + ")",
         t("GEN_A_FITTED_UNANS_MCNEMAR"), t("GEN_A_FITTED_ANS_MCNEMAR")],
        ["rag@random", t("GEN_A_RANDOM_UNANS_ANSWERED") + " ("
         + t("GEN_A_RANDOM_UNANS_ANSWER_RATE") + ")",
         t("GEN_A_RANDOM_ANS_ANSWERED") + " ("
         + t("GEN_A_RANDOM_ANS_ANSWERED_RATE") + ")",
         t("GEN_A_RANDOM_UNANS_MCNEMAR"), t("GEN_A_RANDOM_ANS_MCNEMAR")],
        ["rag@transferred", t("GEN_A_XFER_UNANS_ANSWERED") + " ("
         + t("GEN_A_XFER_UNANS_ANSWER_RATE") + ")",
         t("GEN_A_XFER_ANS_ANSWERED") + " ("
         + t("GEN_A_XFER_ANS_ANSWERED_RATE") + ")",
         t("GEN_A_XFER_UNANS_MCNEMAR"), t("GEN_A_XFER_ANS_MCNEMAR")],
        ["long_context", t("GEN_A_LONGCTX_UNANS_ANSWERED") + " ("
         + t("GEN_A_LONGCTX_UNANS_ANSWER_RATE") + ")",
         t("GEN_A_LONGCTX_ANS_ANSWERED") + " ("
         + t("GEN_A_LONGCTX_ANS_ANSWERED_RATE") + ")",
         t("GEN_A_LONGCTX_UNANS_MCNEMAR"),
         t("GEN_A_LONGCTX_ANS_MCNEMAR")],
    ]
    deck.table(s, ML, 2.02, CW, ["Arm", "Unanswerable answered",
                                  "Answerable answered",
                                  "McNemar, unanswerable",
                                  "McNemar, answerable"],
               rows, col_widths=[0.18, 0.18, 0.18, 0.25, 0.21], size=12.5,
               head_size=12.5, row_h=0.46, head_h=0.44, bold_first=True)
    deck.bullets(s, ML, 4.90, CW, [
        ("Under a prompt that requires an answer, ", "the gate reduces the "
         "rate from " + t("GEN_A_NOGATE_UNANS_ANSWER_RATE") + " to "
         + t("GEN_A_FITTED_UNANS_ANSWER_RATE") + " at "
         + pv(t("GEN_PAIRED_FITTED_UNANS_P")) + ". Under a prompt that permits "
         "a decline, it reduces the rate from 0.535 to 0.417 at "
         + pv(t("GEN_PAIRED_CAUTIOUS_UNANS_P")) + ". The verdict is supported "
         "under both."),
        ("The transferred arm over-refuses badly, ", "answering only "
         + t("GEN_A_XFER_ANS_ANSWERED") + " against "
         + t("GEN_A_NOGATE_ANS_ANSWERED") + " for the ungated arm."),
    ], size=13.5, gap=8, h=1.62)
    

def slide_score_buys():
    deck.part = "results / the generator"
    s = deck.slide("What the confidence score actually buys",
                   "This is the finding most likely to be reported wrongly, so "
                   "it gets a slide of its own.")
    deck.kpi(s, ML, 2.10, 3.40, t("GEN_PAIRED_FITTED_ANS_B"),
             "answerable questions refused by the fitted gate")
    deck.kpi(s, 4.62, 2.10, 3.40, t("GEN_PAIRED_RANDOM_ANS_B"),
             "answerable questions refused by the random control")
    deck.kpi(s, 8.52, 2.10, 3.40, t("FOCUS_GATE_ABST_PRECISION"),
             "abstention precision at the fitted operating point")
    deck.prose(s, ML, 3.70, 6.55, 2.00, [
        ("It does not buy a lower answer rate on unanswerable questions. ",
         "A random control reaches " + t("GEN_A_RANDOM_UNANS_ANSWER_RATE") +
         ", worse than the fitted gate's "
         + t("GEN_A_FITTED_UNANS_ANSWER_RATE") + ", yet far below the "
         "ungated arm's " + t("GEN_A_NOGATE_UNANS_ANSWER_RATE") + "."),
        ("Refusing questions at random is already a large improvement over "
         "never refusing, ", "because most questions in a benchmark are "
         "unanswerable. What the score buys is where the refusals land."),
    ], size=13.5, gap=9)
    deck.block(s, 7.62, 3.70, 5.01, 2.00, "The evidence, and the trade",
               "A paired test on the answerable class gives "
               + pv(t("GEN_PAIRED_FITTED_ANS_P")) + " for the gate and "
               + pv(t("GEN_PAIRED_RANDOM_ANS_P")) + " for the control. "
               "Concentrating refusals on the unanswerable class is a "
               "precision claim, and that test is where it is established. "
               "Counting from the records, the gate removes "
               + t("TRADE_ANSWERING_WRONG_REMOVED") + " wrong answers and "
               "costs " + t("TRADE_ANSWERING_CORRECT_COST_NLI") + " correct "
               "answer under the entailment test.")
    deck.takeaway(s, "The sentence to avoid",
                  "A report that said the gate answers fewer unanswerable "
                  "questions would have been true and misleading, because the "
                  "random control answers fewer still.")
    

def slide_long_context():
    deck.part = "results / long context"
    s = deck.slide("Long context against the pipeline",
                   "The focus corpus is " + t("LC_CORPUS_TOKENS") +
                   " tokens against the pipeline's accepted context of "
                   + t("LC_RAG_TOKENS") + " tokens.")
    deck.kpi(s, ML, 2.10, 3.40, t("GEN_LC_TOKEN_RATIO") + "x",
             "the input tokens per query")
    deck.kpi(s, 4.62, 2.10, 3.40, t("GEN_LC_COST_RATIO") + "x",
             "the input cost per query, at cached-prefix pricing")
    deck.kpi(s, 8.52, 2.10, 3.40, t("GEN_LC_CACHE_HIT"),
             "of requests served as a cache read")
    deck.bullets(s, ML, 3.66, 6.55, [
        ("The cost correction matters. ", "Most of the long-context tokens "
         "are cache reads at a fifth of the base rate, so a token ratio "
         "overstates the cost penalty."),
        ("With the whole corpus in the prompt, ", "the generator answered "
         + t("GEN_A_LONGCTX_ANS_ANSWERED") + " answerable questions at a "
         "per-answer accuracy of " + t("GEN_A_LONGCTX_ANS_ACCURACY") +
         " against " + t("GEN_A_FITTED_ANS_ACCURACY") + " for the gated "
         "pipeline."),
        ("The evidence is not lost in a large context; ", "the tail is where "
         "corpus size bites."),
    ], size=13.5, gap=8, h=2.14)
    deck.table(s, 7.62, 3.70, 5.01, ["The retrieval-side proxy", "Reading"], [
        ["Top ten, focus queries", t("LC_PROXY_TOP10")],
        ["Top ten, six-category queries",
         t("MC_LC_PROXY_TOP10")],
        ["Median rank of the gold chunk", t("LC_PROXY_MEDIAN_RANK")],
        ["Cross-category corpus against 128K",
         t("MC_LC_CORPUS_VS_128K") + " times"],
    ], col_widths=[0.70, 0.30], size=12.5, head_size=12.5, row_h=0.44,
        head_h=0.36, bold_first=True)
    deck.takeaway(s, "What follows",
                  "A token ratio is the size of the prompt. A cost ratio is "
                  "what the prompt costs. Only the second one belongs in "
                  "an argument about money.")
    

def slide_contradiction():
    deck.part = "results / contradiction"
    s = deck.slide("The contradiction gate: a precision of zero",
                   "Measured against reader labels, not the detector's own "
                   "threshold, and reported as a null.")
    rows = [
        ["Labelled alarms", t("CONTRA_PRECISION_N")],
        ["Confirmed as contradictions", "0"],
        ["Precision against reader labels", t("CONTRA_PRECISION_PCT")],
        ["95 percent upper bound on the true precision",
         t("CONTRA_PRECISION_CI_HI")],
        ["Annotator agreement on the decision",
         t("CONTRA_PRECISION_AGREE_N") + " of " + t("CONTRA_PRECISION_AGREE_N")],
        ["Annotator disagreement", t("CONTRA_PRECISION_DISAGREE_N")],
    ]
    deck.table(s, ML, 2.02, 6.55, ["Quantity", "Value"], rows,
               col_widths=[0.70, 0.30], size=12.5, head_size=12.5, row_h=0.36,
               head_h=0.36, bold_first=True)
    deck.figure(s, "fig6_contradiction_precision", 7.60, 2.02, 3.90)
    deck.caption(s, 7.50, 6.00, 5.10, 5,
                 "The contradiction detector's precision against the base rate "
                 "of real conflicts, with 95 percent Wilson intervals.")
    deck.takeaway(s, "The finding",
                  "Reported as unconfirmed with a stated upper bound, not as a "
                  "defect to be explained away. The mechanism is unproven "
                  "rather than disproven: this corpus does not hold the "
                  "phenomenon it detects.",
                  x=ML, w=6.55, y=4.66, h=1.30, stacked=True)
    

def slide_findings():
    deck.part = "results / the findings"
    s = deck.slide("The findings, all fourteen",
                   "Every one is a measured result, and the ones that "
                   "contradict the framework sit in the same list.")
    rows = [
        ["F1", "The dense leg is worse than BM25 here, and fusion recovers it",
         t("R_A") + " vs " + t("R_B") + " vs " + t("R_C")],
        ["F2", "The reranker's value depends on the corpus",
         t("RERANK_MRR_PP") + " pp on focus vs " + t("MC_MRR_RERANK_PP") +
         " pp on six-category"],
        ["F3", "The quota placement has no universally better answer",
         "p = " + t("QUOTA_PLACE_FOCUS_P") + ", " + t("QUOTA_PLACE_SIXCAT_P") +
         ", " + t("QUOTA_PLACE_IND_P")],
        ["F4", "The candidate-pool curve peaks and then declines",
         "focus " + t("FOCUS_POOL_PEAK_R10") + " at ten, " +
         t("FOCUS_POOL_R10_AT_50") + " at fifty"],
        ["F5", "The gate is precise where it refuses",
         "abstention precision " + t("FOCUS_GATE_ABST_PRECISION")],
        ["F6", "The gate detects a recognisable question, not an absent "
         "answer", t("UNANS_HARD_REFUSED_PCT") + " on hard stratum vs "
         + t("UNANS_OOD_REFUSED_N") + " out of domain"],
        ["F7", "The framework's hypothesis holds under both prompt conditions",
         "McNemar p " + t("GEN_PAIRED_FITTED_UNANS_P") + " answering, " +
         t("GEN_PAIRED_CAUTIOUS_UNANS_P") + " cautious"],
        ["F8", "The confidence score buys refusal precision, not a lower "
         "answer rate", "b = " + t("GEN_PAIRED_FITTED_ANS_B") + " against b = "
         + t("GEN_PAIRED_RANDOM_ANS_B") + " answerable refused"],
        ["F9", "The gate is an evidence gate, not a form gate",
         t("FORM_PROBE_RATE") + " of malformed stems accepted"],
        ["F10", "The contradiction gate's precision against reader labels is "
         + t("CONTRA_PRECISION_PCT"), t("CONTRA_PRECISION_N") +
         " alarms, upper bound " + t("CONTRA_PRECISION_CI_HI")],
        ["F11", "Long context costs " + t("GEN_LC_TOKEN_RATIO") + " times the "
         "tokens and " + t("GEN_LC_COST_RATIO") + " times the input cost",
         t("LC_CORPUS_TOKENS") + " against " + t("LC_RAG_TOKENS") + " tokens"],
        ["F12", "A calibrated threshold does not transfer across corpora",
         t("GEN_A_XFER_ANS_ANSWERED") + " against " +
         t("GEN_A_NOGATE_ANS_ANSWERED") + " answerable answered"],
        ["F13", "Most unattributed error comes from the evidence given, not "
         "the logic", t("RO5_RETRIEVED_GROUNDED_ERROR") +
         " against " + t("RO5_GOLD_GROUNDED_ERROR")],
        ["F14", "An empty completion is a third outcome, not a refusal",
         t("GENCOMP_FAILING_EMPTY_N") + " of " +
         t("GENCOMP_FAILING_EMPTY_TOTAL") + " questions"],
    ]
    deck.table(s, ML, 2.02, CW, ["", "Finding", "Evidence"], rows,
               col_widths=[0.045, 0.555, 0.40], size=12, head_size=12,
               row_h=0.31, head_h=0.32, bold_first=True)


# ---------------------------------------------------------------- reading
def slide_reading():
    deck.part = "conclusion"
    s = deck.slide("What the measurements support, and what they do not",
                   "Three things the measurements support, and three "
                   "negative results that are easy to misreport.")
    deck.card(s, ML, 2.02, 5.85, 3.62, "Supported", [
        ("The gate works, but not in the way it is usually described. ",
         "It does not work by answering fewer unanswerable questions than a "
         "control. It works by placing its refusals, concentrating them on "
         "the class that should be refused."),
        ("The cost of the gate is coverage, not quality. ",
         "It removes " + t("TRADE_ANSWERING_WRONG_REMOVED") + " wrong answers "
         "and costs " + t("TRADE_ANSWERING_CORRECT_COST_NLI") + " correct "
         "answer under the entailment test."),
        ("The benchmark was the harder half of the problem. ",
         "Finding the shortcut, rebuilding the class and reporting the fall "
         "from " + t("UNANS_BEFORE_REFUSED_PCT") + " to "
         + t("UNANS_HARD_REFUSED_PCT") + " is a contribution in its own "
         "right."),
    ], size=16, bsize=13)
    deck.card(s, 6.76, 2.02, 5.85, 3.62, "Negative results", [
        ("The contradiction gate's precision is " +
         t("CONTRA_PRECISION_PCT") + ". ",
         "Reporting the recall instead would be reporting a rate against a "
         "ground truth defined by the detector's own threshold, which "
         "measures agreement rather than precision."),
        ("The reranker does not help on the focus corpus. ",
         "A component that helps on one corpus and not on another is not a "
         "component that helps, so the sentence is never used without its "
         "corpus."),
        ("The gate does not reject malformed questions. ",
         "It is good at asking whether there is evidence here, and of no use "
         "at asking whether this is even a question. A separate validator "
         "does that job."),
    ], size=16, bsize=13)
    deck.takeaway(s, "Why these are reported",
                  "A negative result stated plainly is worth more to the next "
                  "person than a positive one that was overstated.")
    

def slide_limitations():
    deck.part = "conclusion"
    s = deck.slide("The limitations",
                   "Eight, and the first is the largest gap in the work.")
    rows = [
        ["L1", "One generator", "The replication on a second model could not "
         "be run, so the hypothesis is supported for the generator tested and "
         "not in general."],
        ["L2", "An encyclopaedic corpus, not a procedural one", "It holds no "
         "instance records, specification tables or calibration logs of the "
         "kind a deployment would query."],
        ["L3", "The long-context quality half was measured on one corpus",
         "The cross-category corpus does not fit a 128K-token window, so the "
         "whole-corpus arm could not be run there."],
        ["L4", "The contradiction annotation is model-based", "Two "
         "annotators that do not share a model, blind to the detector's "
         "scores, and correct on a control set, but not human readers."],
        ["L5", "Statistical power", "The quota-placement and "
         "fusion-over-BM25 comparisons are nulls at this sample size, and are "
         "read as no difference established here."],
        ["L6", "The scope of the generator's own abstention", "The measured "
         "effect is on the rate of answering unanswerable questions. On "
         "generated text the hallucination rate is a different quantity."],
        ["L7", "A refusal is not an answer", "The gate reduces the "
         "opportunity for a hallucinated answer by declining. It does not "
         "make the answers it does give more correct."],
        ["L8", "English and one jurisdiction", "Nothing here shows that the "
         "decomposition of a detector's precision holds for another "
         "language or another jurisdiction."],
    ]
    deck.table(s, ML, 2.02, CW, ["", "Limitation", "What it restricts"], rows,
               col_widths=[0.04, 0.30, 0.66], size=12, head_size=12.5,
               row_h=0.54, head_h=0.34, bold_first=True)
    

def slide_conclusion():
    deck.part = "conclusion"
    s = deck.slide("The conclusion, and the future work",
                   "What the work establishes, and the nine steps that would "
                   "change what it can claim, in that order.")
    deck.prose(s, ML, 2.02, 5.90, 3.40, [
        ("The framework's own hypothesis is supported under both prompt "
         "conditions. ", "Under a prompt that requires an answer, the fitted "
         "gate reduces the rate from " + t("GEN_A_NOGATE_UNANS_ANSWER_RATE") +
         " to " + t("GEN_A_FITTED_UNANS_ANSWER_RATE") + " at "
         + pv(t("GEN_PAIRED_FITTED_UNANS_P")) + "."),
        ("Three findings qualify that verdict. ", "The score buys refusal "
         "precision, the benchmark's shortcut was worth more than the system, "
         "and one mechanism did not survive measurement."),
        ("The contribution is ", "a cost-coverage-reliability frontier for a "
         "confidence gate on industrial text, at the level of the individual "
         "answer claim, with the benchmark repairs and instrument audits."),
    ], size=13.5, gap=10)
    deck.table(s, 6.86, 2.02, 5.75, ["", "Future work"], [
        ["1", "Repeat the generator-side comparison on a generator that "
         "returns text on the table questions"],
        ["2", "Compare the gate against a token-level faithfulness monitor"],
        ["3", "Settle the magnitude and the power of the positional "
         "comparison"],
        ["4", "Extend the industrial corpus beyond one jurisdiction and one "
         "language"],
        ["5", "Stratify the corpus by modality, under a pre-registered power "
         "analysis"],
        ["6", "Hand-check the repaired unanswerable class against the corpus, "
         "on both corpora"],
        ["7", "Run the long-context quality arm on a corpus that fits the "
         "context window"],
        ["8", "Replace the model-based contradiction annotators with human "
         "readers"],
        ["9", "Publish the corrected benchmark and the shortcut audit as a "
         "separate artefact"],
    ], col_widths=[0.07, 0.93], size=12, head_size=12.5, row_h=0.46,
        head_h=0.34, bold_first=True)
    deck.takeaway(s, "The closing point",
                  "The most useful thing here was finding that two of its own "
                  "instruments reported numbers a careful reader could not "
                  "trust, and changing the headline.",
                  x=ML, w=5.90, y=5.50, h=1.10, stacked=True)
    

def slide_thanks():
    s = deck.closing_slide("Thank you", [
        "Questions",
        "An Evidence-Grounded Retrieval-Augmented Generation Framework for "
        "Industrial Decision Support",
        "Ritik Raj  |  25IM60R12  |  Department of Industrial and Systems "
        "Engineering, IIT Kharagpur",
        "Under the supervision of Dr. Sri Krishna Kumar",
    ], "Every figure in this deck comes from an archived result file, and the "
       "full text, the appendix and the benchmark are in the report.")
    

# ------------------------------------------------------------------- build
def main() -> int:
    slide_title()
    slide_problem()
    slide_objectives()
    slide_literature()
    slide_gap()
    slide_framework()
    slide_gate()
    slide_retrieval()
    slide_dataset()
    slide_benchmark()
    slide_metrics()
    slide_retrieval_results()
    slide_quota()
    slide_pool()
    slide_frontier()
    slide_audit()
    slide_verdict()
    slide_score_buys()
    slide_long_context()
    slide_contradiction()
    slide_findings()
    slide_reading()
    slide_limitations()
    slide_conclusion()
    slide_references()
    slide_thanks()
    deck.save(OUT)
    _monochrome(OUT, keep=(ACCENT_HEX,))
    print(f"[final mtp deck] wrote {OUT.name} "
          f"({len(deck.prs.slides._sldIdLst)} slides)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
