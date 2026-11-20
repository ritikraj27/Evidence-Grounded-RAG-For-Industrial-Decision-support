#!/usr/bin/env python3
"""Build the complete MTP deck, every table and formula.

This deck is the whole of the work in one place: the objective, the literature
review in tables, the references, the framework with every formula and every
symbol named, the methodology with the benchmark's three repairs, the results
with every measured figure, and the conclusion, the limitations and the future
work.

It is built from the same measured-value table as every other deliverable, so
it cannot disagree with the report or with the papers. Where a number has no
token, the archived result file is read directly.

Its theme is its own: one column, one accent, a lot of white, and a sentence
under every title saying what the slide establishes.

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
from monochrome import ACCENT as ACCENT_HEX, to_monochrome as _monochrome  # noqa: E402
from final_mtp_theme import (ACCENT, CW, INK, INK_SOFT, ML, GREY, GREY_LIGHT,  # noqa: E402
                             RULE, SURFACE, WHITE, Deck)
from pptx.util import Inches  # noqa: E402

OUT = ROOT / "deliverables" / "final_mtp_reference.pptx"
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


def focus_sweep() -> list[dict]:
    """The gate's threshold sweep, read from the archived focus run."""
    path = FOCUS_RESULTS / "exp2_gate.json"
    if not path.exists():
        return []
    doc = json.loads(path.read_text(encoding="utf-8"))
    return doc.get("threshold_sweep", [])


# ------------------------------------------------------------------ content
FOOTER = ("MTP  |  An Evidence-Grounded RAG Framework for Industrial "
          "Decision Support  |  Ritik Raj 25IM60R12  |  IIT Kharagpur, ISE")

TITLE_TEXT = ("An Evidence-Grounded Retrieval-Augmented Generation Framework "
              "for Industrial Decision Support")
SUBTITLE = ("Architecture, evaluation protocol, failure modes, and what the "
            "measurements show")

deck = Deck(FOOTER)


# ------------------------------------------------------------------- slides
def slide_title():
    image = ROOT / "deliverables" / "assets" / "mtp_intent.png"
    credits = [
        ([("Presented by   ", True, ACCENT), ("Ritik Raj", True, INK),
          ("      Roll No. 25IM60R12", False, INK_SOFT)], 13.5),
        ([("Under the supervision of   ", False, GREY),
          ("Dr. Sri Krishna Kumar", False, INK_SOFT)], 12),
        ([("Department of Industrial and Systems Engineering, "
           "IIT Kharagpur", False, GREY)], 11),
    ]
    s = deck.title_slide(TITLE_TEXT, SUBTITLE, image, credits)
    deck.notes(s, "The picture is the framework: five stages, and two places "
                  "where the answer is a refusal. Everything that follows is "
                  "either a stage of that pipeline or a measurement of it.")


def slide_contents():
    deck.part = "contents"
    s = deck.slide("How this deck is organised",
                   "Six sections. The third and the fifth carry the work; the "
                   "rest carries the argument around it.")
    rows = [
        ["01", "Objective", "The question, four research objectives, the "
         "contributions, and the scope of the claims", "4 to 7"],
        ["02", "Literature review", "Eight threads in two tables, what the "
         "review leaves open, and the references", "9 to 13"],
        ["03", "Framework", "The five stages, the four mechanisms inside them, "
         "and every formula with its symbols named", "15 to 26"],
        ["04", "Methodology", "The corpora, the benchmark and its three "
         "repairs, the metrics, the protocol, the arms", "28 to 41"],
        ["05", "Results", "Retrieval, the gate, the benchmark audit, the "
         "generator, long context, contradiction", "43 to 66"],
        ["06", "Conclusion", "What the measurements establish, the "
         "limitations, the future work", "68 to 74"],
    ]
    deck.table(s, ML, 2.06, CW, ["", "Section", "What it holds", "Slides"],
               rows, col_widths=[0.05, 0.16, 0.62, 0.10], size=12.5,
               head_size=11, row_h=0.50, head_h=0.36, bold_first=True)
    deck.takeaway(s, "How to read it",
                  "Every slide ends with the one sentence it establishes. The "
                  "slides that carry a formula also carry where the formula "
                  "came from and why its value is the value it is.")
    deck.notes(s, "Say where the deck goes in one breath, then move. The "
                  "formulas are in section three, the findings in section "
                  "five, and everything else supports one or the other.")


def section(number, title, blurb, items, note=""):
    deck.section_slide(number, title, blurb, items, notes_text=note)


# ------------------------------------------------------------------ 1
def part_objective():
    deck.part = "objective"
    section(1, "Objective",
            "The question this work asks, the four objectives it runs on, and "
            "the boundaries that keep the claims inside what the measurements "
            "can carry.",
            ["The problem in one slide",
             "The four research objectives",
             "The contributions",
             "The scope of the claims"],
            "The question the work asks, and the boundaries that keep the claims inside what the measurements can carry.")

    s = deck.slide("A wrong answer and a non-answer do not cost the same",
                   "This is the asymmetry the whole framework is built "
                   "around.")
    deck.prose(s, ML, 2.02, 6.55, 3.30, [
        ("A retrieval-augmented generator reads a corpus and answers a "
         "question. In industry the corpus is not a wiki. It is a controlled "
         "set of documents somebody signed off on, and the questions are "
         "operational decisions: whether a part's tolerance is acceptable, "
         "which step of a procedure applies, what a specification requires."),
        ("Such a corpus gives the system one property that dialogue and "
         "open-domain benchmarks never test. A refusal costs a supervisor "
         "five minutes. A confidently fabricated tolerance costs a scrapped "
         "batch."),
    ])
    deck.card(s, 7.62, 2.02, 5.01, 3.30, "The question this work asks", [
        ("Not whether retrieval-augmented generation works. ", "It already "
         "does, in the sense that it returns text."),
        ("Whether the component that decides to answer can be measured at "
         "all", ", and what that decision is worth once it has been measured "
         "properly."),
    ], size=17, bsize=13)
    deck.takeaway(s, "The question",
                  "Can a gate in the code decide whether the retrieved "
                  "industrial evidence actually contains the answer?")
    deck.notes(s, "The cost asymmetry is the reason the work exists. A "
                  "refusal is cheap and a fabrication is not, so the decision "
                  "to answer is worth measuring on its own.")

    s = deck.slide("The four research objectives",
                   "Each one is a thing that had to be built and then "
                   "measured, not a claim to be argued.")
    rows = [
        ["**RO1**", "Build an evidence-grounded framework for industrial "
         "decision support", "Generation is gated in code. The generator is "
         "called at exactly one point in the pipeline, and only when the gate "
         "has accepted."],
        ["**RO2**", "Make the retrieval stage modality-balanced and "
         "category-aware", "Fuse a lexical and a dense leg, rerank with a "
         "cross-encoder, and hold a quota over text, table and chart chunks."],
        ["**RO3**", "Test the framework's own hypothesis about hallucination",
         "The claim that a non-bypassable gate reduces hallucination has to "
         "be tested against a generator that is required to answer, not only "
         "one allowed to decline."],
        ["**RO4**", "Characterise the failure modes", "The framework has to "
         "report the failures that contradict it with the same care as the "
         "successes, and publish the error rates of its own instruments."],
    ]
    deck.table(s, ML, 2.02, CW, ["", "Objective", "What it demands"],
               rows, col_widths=[0.07, 0.31, 0.62], size=12,
               head_size=10.5, row_h=0.72, head_h=0.34, bold_first=True)
    deck.takeaway(s, "RO3 decides the design",
                  "If the generator is allowed to decline, the gate's "
                  "contribution cannot be separated from the generator's "
                  "willingness to answer. So one arm of the experiment makes "
                  "an answer compulsory.")
    deck.notes(s, "RO3 is the one that shapes the experiment rather than the "
                  "code. A cautious generator refuses most unanswerable "
                  "questions by itself, which would have produced a null that "
                  "meant nothing.")

    s = deck.slide("The contributions",
                   "A framework, and the measurement of it. The second half of "
                   "the list is where the care went.")
    rows = [
        ["1", "The framework", "Five stages: hybrid retrieval under a "
         "category pre-filter, a modality quota, a calibrated gate, "
         "contradiction surfacing, per-claim evidence tags."],
        ["2", "A repaired refusal benchmark, with a published shortcut audit",
         "The unanswerable class was separable from the question text alone at "
         "ROC AUC " + t("UNANS_BEFORE_AUC") + ". Rebuilt, the refusal rate is "
         + t("UNANS_HARD_REFUSED_PCT") + " against the "
         + t("UNANS_BEFORE_REFUSED_PCT") + " the defective class produced."],
        ["3", "A two-condition test of the framework's own hypothesis",
         "The prompt condition is an experimental axis rather than a fixed "
         "setting, and the verdict is supported under both."],
        ["4", "A random-escalation control",
         "It refuses the same number of questions at random, which isolates "
         "what the confidence score buys: refusal precision, not a lower "
         "answer rate."],
        ["5", "A reader-label measurement of the contradiction gate",
         "Precision came out at " + t("CONTRA_PRECISION_PCT") + ", and the "
         "audit exposed two real defects in the detector."],
        ["6", "A published error profile for the claim scorer",
         "The claim scorer is the instrument the hallucination metric is "
         "computed from, so its own error rate is reported."],
    ]
    deck.table(s, ML, 2.02, CW, ["", "Contribution", "What it is"],
               rows, col_widths=[0.04, 0.30, 0.66], size=11,
               head_size=10.5, row_h=0.56, head_h=0.32, bold_first=True)
    deck.takeaway(s, "What to stress",
                  "Contribution two is the one that changed a headline "
                  "number. A refusal rate that falls by a factor of four when "
                  "the benchmark is repaired is a fact about the benchmark.")
    deck.notes(s, "Do not rush this slide. The six contributions are what the "
                  "committee will ask about one by one.")

    s = deck.slide("The scope of the claims",
                   "Three boundaries. Every one of them narrows what the "
                   "measurements can be read as saying.")
    deck.card(s, ML, 2.02, 3.87, 3.42, "An encyclopaedic corpus", [
        ("An industrial-engineering encyclopaedic corpus, not "
         "practitioner documentation. ", "The primary corpus is proprietary "
         "supply-chain text and cannot be redistributed, so every measurement "
         "runs on a public substitute that ships with its provenance. The "
         "Claims are narrowed to match."),
    ], size=15, bsize=12)
    deck.card(s, 4.77, 2.02, 3.87, 3.42, "One generator", [
        ("The generator-side comparison ran on one generator. ", "A "
         "replication on a second one could not be run, because that model "
         "returned no text on " + t("GENCOMP_FAILING_EMPTY_N") + " of "
         + t("GENCOMP_FAILING_EMPTY_TOTAL") + " questions. One generator "
         "settles the hypothesis for that generator, not in general."),
    ], size=15, bsize=12)
    deck.card(s, 8.82, 2.02, 3.79, 3.42, "One corpus for long context", [
        ("Only the focus corpus carries the long-context comparison's quality "
         "half. ", "The cross-category corpus does not fit a 128K-token "
         "context window, so on that corpus the comparison is settled on cost "
         "and coverage alone."),
    ], size=15, bsize=12)
    deck.takeaway(s, "The rule",
                  "A number from one corpus is never quoted beside a number "
                  "from another as though they were the same measurement.")
    deck.notes(s, "Saying the scope out loud is what stops the third question "
                  "from being a correction.")


# ------------------------------------------------------------------ 2
def part_literature():
    deck.part = "literature review"
    section(2, "Literature review",
            "Eight threads, the work that stands behind each, what this work "
            "takes from it, and what it leaves open.",
            ["Evaluation is the hard part",
             "Confidence, calibration and abstention",
             "Sufficiency and the risk-coverage frontier",
             "The selection effect",
             "Fusion and reranking",
             "Contradiction detection",
             "Evaluation practice for abstention",
             "Industrial and enterprise retrieval"],
            "Eight threads, the work behind each, and the gap they leave.")

    s = deck.slide("Eight threads, and what each one gives",
                   "Part one: how RAG is evaluated, how a system knows what it "
                   "knows, and how the two 2026 results constrain a null.")
    rows = [
        ["1. RAG and how it is evaluated",
         "A dense retriever and a reader, measured by citation precision and "
         "recall and by atomic decomposition. Both are necessary and both "
         "miss the decision to answer at all.",
         "Lewis et al. (2020); Karpukhin et al. (2020)",
         "The reader and retriever split, and the warning that a system which "
         "answers everything scores perfectly on claim precision."],
        ["2. Confidence, calibration and abstention",
         "Abstention as conformal prediction with a coverage guarantee. A "
         "confidence score needs a calibration step and a measurement of its "
         "own error, not a threshold picked by hand.",
         "Yadkori et al. (2024)",
         "The shape of the mechanism: calibrate first, then measure the "
         "calibration, and report it even when it is unflattering."],
        ["3. Sufficiency and the risk-coverage frontier",
         "Answer accuracy is conditional on the context being sufficient, not "
         "merely present. The operating point is a pair of coverage and risk.",
         "Joren et al. (2024)",
         "The risk-coverage formulation, measured here at the level of the "
         "individual answer claim rather than the answer."],
        ["4. The selection effect, and recognition-refusal misalignment",
         "A gate forwards a slice on which the downstream component is no "
         "better than the baseline, which erases the advantage. A model can "
         "recognise an impossible question and fail to route that "
         "recognition to an abstention.",
         "Tikhomirov and Savchenko (2026)",
         "The rule that a null under a cautious prompt is reported as the "
         "prompt having realised the gate's function, never as confidence "
         "gating failing."],
    ]
    deck.table(s, ML, 2.02, CW, ["Thread", "What it established",
                                  "Representative work", "What is taken from it"],
               rows, col_widths=[0.15, 0.29, 0.16, 0.40], size=10,
               head_size=9.5, row_h=1.05, head_h=0.32, bold_first=True)
    deck.notes(s, "The fourth row is the one that shapes how the results are "
                  "reported. Read it slowly.")

    s = deck.slide("Eight threads, and what each one gives",
                   "Part two: the retrieval stack, contradiction detection, how "
                   "a refusal benchmark is built, and what industry has "
                   "measured.")
    rows = [
        ["5. Hybrid retrieval, fusion and reranking",
         "Okapi BM25 and a dense leg joined by reciprocal rank fusion. A later "
         "analysis settled which fusion functions actually work.",
         "Cormack et al. (2009); Karpukhin et al. (2020)",
         "The fusion function and its constant, and the counter-evidence that "
         "retrieval gains often stop once a strong reranker is present."],
        ["6. Contradiction detection in retrieved evidence",
         "The literature on knowledge conflict is large. It also shows that "
         "rerankers have to be optimised for semantic conflict rather than "
         "for topical similarity.",
         "Several 2024 to 2026 studies",
         "Two lessons applied directly: a detector judged against a ground "
         "truth defined by its own threshold measures agreement, and the "
         "phenomenon has to exist in the corpus for a high recall to mean "
         "anything."],
        ["7. Evaluation practice for abstention",
         "Unanswerable questions must be plausible. An n-gram filter that "
         "identifies the questions a knowledge base cannot answer invalidates "
         "an evaluation of unanswerability detection.",
         "Rajpurkar et al. (2018)",
         "The desiderata this work adopts, and the reason the shortcut found "
         "in its own benchmark was treated as a defect rather than a result."],
        ["8. Industrial and enterprise retrieval",
         "Industrial RAG has been built far more often than it has been "
         "measured at the level of the answer claim, and the deployed corpora "
         "are regulatory and procedural.",
         "Industrial frameworks for manufacturing and regulated deployment",
         "A measurement on encyclopaedic industrial-engineering text, and the "
         "admission that it is a different corpus regime from the deployed "
         "ones."],
    ]
    deck.table(s, ML, 2.02, CW, ["Thread", "What it established",
                                  "Representative work", "What is taken from it"],
               rows, col_widths=[0.15, 0.29, 0.16, 0.40], size=10,
               head_size=9.5, row_h=1.05, head_h=0.32, bold_first=True)
    deck.notes(s, "Row six is the thread this work is most careful about, "
                  "because its own measurement came out at zero.")

    s = deck.slide("What the review leaves open",
                   "Three things are not settled by the literature, and two of "
                   "them are what this work is about.")
    deck.card(s, ML, 2.02, 3.87, 3.30, "The measurement", [
        ("The abstention mechanism is established prior art. ", "Goswami and "
         "Kurra (2025) are the closest. The end-to-end measurement of it, "
         "with a control arm, on industrial text, is not."),
    ], size=15, bsize=12.5)
    deck.card(s, 4.77, 2.02, 3.87, 3.30, "The benchmark", [
        ("Shortcuts that inflate refusal rates are known. ", "On the "
         "evidence of this literature they have not been reported for a "
         "retrieval-augmented refusal benchmark."),
    ], size=15, bsize=12.5)
    deck.card(s, 8.82, 2.02, 3.79, 3.30, "The value of the score", [
        ("What a confidence score buys, once the generator is not allowed to "
         "decline on its own, ", "is still an open question. That is the "
         "question the random-escalation control was built to answer."),
    ], size=15, bsize=12.5)
    deck.takeaway(s, "The contribution",
                  "No new mechanism here. Measuring it, on "
                  "industrial text, against a control that ignores the score, "
                  "is.")
    deck.notes(s, "This slide is where the committee decides whether the work "
                  "is a contribution or an engineering exercise. Say plainly "
                  "that the mechanism is prior art.")

    for _half in (0, 1):
        s = deck.slide("References",
                       "The eight works the work stands on, and "
                       "where each one is used."
                       if _half == 0 else
                       "The remaining four, with where each one is used.")
        _y = 2.02
        for _citation, _use in IEEE_REFS[_half * 4:_half * 4 + 4]:
            tf = deck.text(s, ML, _y, CW, 1.16)
            deck.para(tf, _citation, size=12.5, color=INK_SOFT, space_after=4,
                      first=True, line=1.18)
            deck.rich(tf, [("Used here:  ", True, ACCENT), (_use, False, GREY)],
                      size=12, space_after=0, line=1.16)
            _y += 1.16
        deck.notes(s, "Every mechanism here is prior art. The contribution is "
                      "the industrial measurement, not the architecture.")

def part_framework():
    deck.part = "framework"
    section(3, "Framework",
            "The five stages, the four mechanisms inside them, and every "
            "formula with its symbols named and its origin stated.",
            ["The pipeline", "Corpus and chunking", "Okapi BM25",
             "Reciprocal rank fusion", "The modality quota",
             "The gate's feature vector", "The calibrated posterior",
             "The decision rule", "The contradiction gate",
             "The query-form validator", "Per-claim assessment"],
            "The five stages and every formula with its symbols named.")


def part_framework_slides():
    s = deck.slide("The framework is a five-stage pipeline",
                   "A request enters at stage 0 and leaves at stage 4 as a "
                   "refusal or as a set of per-claim annotations.")
    s.shapes.add_picture(str(_diagram.build()), Inches((13.333 - 9.60) / 2),
                         Inches(2.00), width=Inches(9.60))
    rows = [
        ["0", "Query-form validation", "the raw query string",
         "a query or a refusal", "yes"],
        ["1", "Hybrid retrieval", "the query",
         "a candidate pool of chunks", "no"],
        ["2", "Rerank and quota", "the candidate pool",
         "a final context of " + t("RERANK_TOP_K_FINAL") + " chunks", "no"],
        ["3", "Confidence gate", "the final context", "accept or refuse", "yes"],
        ["4", "Generation and claim assessment", "the accepted context",
         "an annotated answer", "no"],
    ]
    deck.table(s, ML, 4.52, CW, ["", "Stage", "Input", "Output", "May refuse"],
               rows, col_widths=[0.04, 0.30, 0.22, 0.30, 0.14], size=11,
               head_size=10, row_h=0.30, head_h=0.30, bold_first=True)
    deck.notes(s, "Two properties are in the code rather than in a convention. "
                  "The generator is injected and called at exactly one line, "
                  "after the gate accepts. And the form validator is a "
                  "separate component, because it runs before retrieval and "
                  "the two must not be merged.")

    s = deck.slide("Corpus and chunking",
                   "Documents become chunks, and every chunk carries the "
                   "things a measurement needs to count.")
    deck.kpi(s, ML, 2.06, 3.40, t("SHARE_TEXT"),
             "of the focus corpus is text")
    deck.kpi(s, 4.62, 2.06, 3.40, t("MEAN_WORDS") + " words",
             "is the mean chunk length")
    deck.kpi(s, 8.52, 2.06, 3.40, t("DUP_CHUNK_IDS"),
             "duplicate chunk identifiers")
    deck.bullets(s, ML, 3.62, 6.55, [
        ("Each chunk records its modality: ", "text, table or chart. The "
         "remainder of the focus corpus is " + t("SHARE_TABLE") + " tables and "
         + t("SHARE_CHART") + " charts."),
        ("Every chunk carries its source document, its category and its "
         "modality. ", "The chunk identifier is unique across the corpus, "
         "because a duplicated chunk identifier quietly inflates every recall "
         "measurement that counts chunks."),
        ("The public corpus ships with its provenance: ", "the upstream "
         "identifier, a SHA-256 of the content, the chunk count and the "
         "licence."),
    ], size=13, gap=10)
    deck.card(s, 7.62, 3.62, 5.01, 2.00, "Why the corpus is public", [
        ("A corpus that cannot be redistributed is the reason the study runs "
         "on a public substitute. ", "A corpus that cannot be traced is the "
         "reason that substitute ships with its provenance attached."),
    ], size=15, bsize=12.5)
    deck.takeaway(s, "The chunk count",
                  "The unique identifier is not housekeeping. It is the "
                  "difference between a recall number and a number that counts "
                  "the same chunk twice.")
    deck.notes(s, "The duplicate-identifier check is worth one sentence "
                  "because it is the sort of thing that silently inflates a "
                  "recall figure.")

    formula_slide(
        title="Okapi BM25, the lexical leg",
        kicker="The one textbook component in the pipeline, and the one that "
               "carried the retrieval on the focus corpus.",
        latex=r"\mathrm{BM25}(q,d)=\sum_{t\in q}\mathrm{IDF}(t)\cdot"
              r"\frac{f_{t,d}(k_1+1)}{f_{t,d}+k_1\left(1-b+b"
              r"\frac{|d|}{\mathrm{avgdl}}\right)}",
        width=6.30, fontsize=21,
        symbols=[
            ["q", "the query, which is the user's text"],
            ["d", "one candidate chunk"],
            ["t", "each query word in turn"],
            ["IDF(t)", "how rare the word is, on a log scale"],
            ["f(t,d)", "how many times the word occurs in the chunk"],
            ["|d|", "the length of the chunk, in words"],
            ["avgdl", "the average chunk length of the corpus"],
            ["k1", "how quickly the frequency factor saturates: "
                   + t("BM25_K1")],
            ["b", "how strongly long chunks are penalised: 0.75"],
        ],
        source=("Okapi BM25, with the Robertson-Sparck-Jones IDF variant and a "
                "plus one offset. The offset is why a word that appears in "
                "every document scores exactly zero instead of a negative "
                "number."),
        value=("The two knobs have standard settings. b = 0 would ignore "
               "chunk length entirely and count only word overlap. b = 1 "
               "would require a chunk to be as dense as the average one. "
               "k1 = " + t("BM25_K1") + " is the standard saturation setting "
               "and was used here."),
        caveat=("The lexical leg was measurably stronger than the dense leg "
                "on the focus corpus, which is why the fusion recovers a loss "
                "rather than adding a second strong leg."),
        notes=("Name the formula, say what it is for, and move. The two knobs "
               "are the only part an examiner is likely to ask about."),
    )

    formula_slide(
        title="Reciprocal rank fusion joins the two legs",
        kicker="Why ranks are added rather than scores: BM25 scores and "
               "cosine similarities are on different scales, and ranks are not.",
        latex=r"S_{\mathrm{RRF}}(d)=\sum_{r\in\mathcal{R}}"
              r"\frac{1}{k_{\mathrm{RRF}}+\mathrm{rank}_r(d)},\qquad "
              r"k_{\mathrm{RRF}}=60",
        width=5.40, fontsize=21,
        symbols=[
            ["S_RRF(d)", "the fused score of the chunk; higher is better"],
            ["R", "the two ranked lists being fused"],
            ["rank_r(d)", "where the chunk sits in list r; 1 is the best"],
            ["k_RRF", "the smoothing constant, set to " + t("RRF_K")],
            ["d", "any candidate chunk"],
        ],
        source=("Cormack et al. (2009), the function that joins a lexical and "
                "a dense leg. A chunk absent from a list contributes nothing "
                "at all."),
        value=("Why 60. The constant stops the top result from dominating. At "
               "rank 1 the contribution is 1/61, at rank 10 it is 1/70, so a "
               "chunk that appears twice at moderate rank can beat one that "
               "appears once at the top. Agreement between two methods is "
               "evidence."),
        caveat=("Fusion does not create information. On the focus corpus the "
                "dense leg was measurably worse than the lexical one, so "
                "fusion recovered the loss without becoming a significant win "
                "over the lexical leg on its own."),
        notes=("The honest framing is that fusion stopped being a loss. It did "
               "not become a significant win over BM25 alone, and saying "
               "otherwise would be overclaiming."),
    )

    formula_slide(
        title="The modality quota is a floor, not a ceiling",
        kicker="It says at least this many tables and charts. Nothing in it "
               "limits text, which is the most common misreading of a quota.",
        latex=r"q_m=\min\left(n_m,\left\lceil \alpha_m\,|\mathcal{C}|"
              r"\right\rceil\right),\qquad \alpha_{\mathrm{table}}=0.15,\ "
              r"\alpha_{\mathrm{chart}}=0.05",
        width=5.60, fontsize=19,
        symbols=[
            ["q_m", "the quota for modality m, a number of chunks"],
            ["n_m", "how many of that modality the pool holds"],
            ["alpha_m", "the share the context should give that modality"],
            ["|C|", "the size of the candidate pool, "
                    + t("RERANK_TOP_N") + " chunks"],
            ["m", "a modality: text, table or chart"],
        ],
        source=("A quota mechanism of the framework. The shares are "
                + t("QUOTA_MIN_TABLE_SHARE") + " for tables and "
                + t("QUOTA_MIN_CHART_SHARE") + " for charts, and the depth it "
                "draws to is " + t("QUOTA_DEPTH") + " chunks per modality."),
        value=("Why the minimum is in the formula. When the pool cannot supply "
               "the floor, the floor is relaxed rather than invented. A quota "
               "that quietly became a ceiling on a thin pool would be a "
               "different mechanism under the same name, and it would be "
               "measuring the pool rather than the quota."),
        caveat=("Where the quota is applied is a configuration value rather "
                "than a rule, and the measurement that shows why is three "
                "corpora and three non-significant differences."),
        notes=("Say the word floor out loud. A quota read as a ceiling is the "
               "single most common mistake in this piece of machinery."),
    )

    formula_slide(
        title="The gate's feature vector",
        kicker="Five query-level statistics of the retrieved pool. Every one "
               "describes the pool rather than any single chunk, and that is "
               "deliberate.",
        latex=r"\phi(q)=\left[s^{(1)}_{\mathrm{rerank}},\ "
              r"\bar{s}^{(3)}_{\mathrm{rerank}},\ s^{(1)}_{\mathrm{bm25}},\ "
              r"\max_d S_{\mathrm{RRF}}(d),\ |\{d\in\mathcal{C}: "
              r"s_{\mathrm{rerank}}(d)>\beta\}|\right]",
        width=6.30, fontsize=15,
        symbols=[
            ["phi(q)", "the feature vector of the query: five numbers"],
            ["s_rerank(1)", "the cross-encoder's top score in the pool"],
            ["s_rerank(1..3) mean", "the mean of the top three scores"],
            ["s_bm25(1)", "the best lexical score in the pool"],
            ["max S_RRF(d)", "the best fused score"],
            ["beta", "the reranker's own relevance bar"],
        ],
        source=("A feature set for the calibrated gate. The vector is "
                "standardised with the calibration split's own mean and "
                "standard deviation before it is used."),
        value=("Why the level matters, and it is the point of the slide. There "
               "is one gold chunk among roughly fifty candidates, so a "
               "chunk-level classifier is right 98 percent of the time by "
               "answering that nothing is relevant. Maximum-likelihood fitting "
               "dutifully returns a large negative intercept: a degenerate "
               "solution that looks like a fitted model and behaves like a "
               "constant."),
        caveat=("Each feature is a summary of the pool, so the gate cannot "
                "tell a pool holding one strong answer from a pool holding "
                "four mediocre ones. The alternatives need more labelled data "
                "than there was."),
        notes=("This is the slide that shows the query-level design was a "
               "choice, not an accident. The degenerate chunk-level solution "
               "is the reason."),
    )

    formula_slide(
        title="The calibrated posterior",
        kicker="Platt scaling on top of the feature vector: the output is a "
               "probability, and the probability is fitted on held-out data.",
        latex=r"p_{\mathrm{conf}}(q)=\sigma\left(\beta_0+"
              r"\boldsymbol{\beta}_1^{\mathsf{T}}"
              r"\frac{\phi(q)-\boldsymbol{\mu}}{\boldsymbol{\sigma}}"
              r"\right),\qquad \sigma(z)=\frac{1}{1+e^{-z}}",
        width=5.90, fontsize=19,
        symbols=[
            ["p_conf(q)", "the probability that the answer is in the context"],
            ["sigma(z)", "the logistic function, mapping any number to [0,1]"],
            ["beta_0", "the intercept, fitted"],
            ["beta_1", "one weight per feature, fitted"],
            ["mu", "the calibration split's mean of each feature"],
            ["sigma", "the calibration split's standard deviation"],
        ],
        source=("Platt's method: take an existing score, fit a logistic model "
                "on top of it so that the output is a probability, and fit it "
                "by maximum likelihood on a held-out split. The weights are "
                "fitted on 60 percent of the queries and the calibration "
                "numbers are measured on the other 40."),
        value=("Why standardise. Without it a feature measured on a larger "
               "scale would dominate the weighted sum purely because of its "
               "units, and the fit would have to work harder to undo that."),
        caveat=("The expected calibration error of " + t("GATE_ECE") + " is "
                "reported rather than improved by refitting. It is the "
                "calibration of one fitted artefact on one fixed split."),
        notes=("The examiner's likely question is why Platt scaling and not "
               "something fancier. The answer is the amount of labelled data "
               "there was, and the fact that the calibration is measured."),
    )

    formula_slide(
        title="The decision rule, and the threshold",
        kicker="A threshold on the posterior. Below it the framework refuses, "
               "and the generator is never called.",
        latex=r"\mathrm{accept}(q)=\mathbf{1}\left[p_{\mathrm{conf}}(q)"
              r"\geq\tau\right]",
        width=4.40, fontsize=22,
        symbols=[
            ["accept(q)", "whether the query reaches the generator: 1 or 0"],
            ["p_conf(q)", "the calibrated probability"],
            ["tau", "the threshold, which is the operating point"],
            ["1[...]", "the indicator function: 1 if the condition holds"],
        ],
        source=("The fitted operating point on the focus domain is tau = "
                + t("FOCUS_GATE_TAU") + ". A second operating point, tau = "
                + t("GEN_TRANSFERRED_TAU") + ", fitted on one half of the "
                "cross-category corpus and applied unchanged to the other "
                "half, is used as the transfer arm."),
        value=("Why the threshold is " + t("FOCUS_GATE_TAU") + ". It was "
               "chosen by a stated rule rather than by taste: the highest "
               "threshold that still answers at least 90 percent of the "
               "answerable queries. The sweep is shown in full later, because "
               "a single threshold hides the shape of the frontier behind it."),
        caveat=("A threshold is a policy, not a property of the model. It "
                "belongs to a deployment, and a deployment team would have to "
                "calibrate it on its own corpus."),
        notes=("The threshold is the number an examiner will probe hardest, "
               "so give the rule and not just the value."),
    )

    formula_slide(
        title="The contradiction gate",
        kicker="A pair of chunks is flagged only when two independent "
               "branches agree. Requiring both is what cut the alarms from "
               + t("CONTRA_ALARMS_BEFORE") + " to " + t("CONTRA_ALARMS_AFTER")
               + ".",
        latex=r"\mathrm{contradiction}(c_1,c_2)=\mathbf{1}\left["
              r"\mathrm{NLI}(c_1,c_2)=\mathrm{contradiction}\right]"
              r"\wedge\mathbf{1}\left[\mathrm{shared}\ \mathrm{measurement}"
              r"\ \wedge\ \mathrm{shared}\ \mathrm{instance}\right]",
        width=6.10, fontsize=13,
        symbols=[
            ["c1, c2", "two retrieved chunks, any pair from the context"],
            ["NLI(c1,c2)", "a natural language inference model's judgement"],
            ["shared measurement", "the two discuss the same measured "
                                    "quantity"],
            ["shared instance", "of the same instance, the narrower test"],
        ],
        source=("A natural language inference branch, "
                + t("CONTRA_NLI_THRESHOLD") + " on the entailment threshold of "
                "a published cross-encoder. The second branch is the "
                "framework's own rule."),
        value=("Why both branches. A quantity branch on its own fired on "
               "citation years, and a topical subject check on its own was a "
               "topic check rather than a contradiction check. The narrow test "
               "is the one that stops the detector crying wolf."),
        caveat=("A precision of " + t("CONTRA_PRECISION_PCT") + " against reader labels. "
                "The mechanism is reported as "
                "unproven rather than disproven, and the reason is that this "
                "corpus does not hold the phenomenon it detects."),
        notes=("Do not let this slide end in a triumph. The measurement is a "
               "null and it is reported as one."),
    )

    s = deck.slide("The runtime query-form validator",
                   "A separate component, before retrieval, that catches a "
                   "degenerate request and refuses it cheaply.")
    deck.prose(s, ML, 2.02, 6.55, 3.40, [
        ("Four rules fire: ", "empty, no_words, no_content (every word is a "
         "function word or a deictic), and incomplete (the string ends on a "
         "word that cannot end a question). The check is deliberately "
         "lexical, and it deliberately fails open."),
        ("It exists to catch an empty or degenerate request, not to adjudicate "
         "English. ", "It runs before retrieval, so a request it refuses costs "
         "neither retrieval nor a model call, at "
         + t("FORMVAL_COST_US") + " microseconds per query."),
        ("The component was added because the benchmark builder contained a "
         "rule with a similar name, ", "which turned out to be a rule about "
         "question generation rather than about form. Reusing it at runtime "
         "was measured rather than assumed."),
    ])
    deck.card(s, 7.62, 2.02, 5.01, 1.62, "Measured on the benchmark", [
        (t("FORMVAL_BENCH_REJECTED") + " of " + t("FORMVAL_BENCH_N") +
         " queries refused (" + t("FORMVAL_BENCH_RATE") + "). ",
         "All of them are generator artefacts that read as malformed rather "
         "than real questions."),
    ], size=15, bsize=12.5)
    deck.card(s, 7.62, 3.84, 5.01, 2.00, "The counterfactual", [
        ("Reusing the benchmark builder's own subject rule as a runtime check "
         "would have refused ", t("FORMVAL_COUNTERFACTUAL_REJECTED") + " of "
         + t("FORMVAL_COUNTERFACTUAL_N") + " hand-labelled well-formed "
         "questions, a " + t("FORMVAL_COUNTERFACTUAL_RATE") +
         " false-rejection rate. That rule is about question generation, not "
         "about form."),
    ], size=15, bsize=12.5)
    deck.takeaway(s, "The lesson",
                  "The false-rejection rate of a reused filter has to be "
                  "measured against a hand-labelled population before such a "
                  "filter ships.")
    deck.notes(s, "This is a small slide with a large lesson in it, and the "
                  "lesson generalises beyond this framework.")

    s = deck.slide("Per-claim assessment",
                   "When the gate accepts, each claim in the answer is scored "
                   "against the evidence the arm was shown, and nothing else.")
    deck.prose(s, ML, 2.02, 6.55, 3.30, [
        ("A claim counts as supported ", "when a chunk entails it at threshold "
         "0.5 or when the evidence states it literally. A bare value is scored "
         "by the literal test alone, because an entailment model cannot "
         "adjudicate a number that is not a proposition."),
        ("The literal test requires every content word and every number to "
         "appear, word-boundary matched, in the same chunk. ", "That design "
         "has a consequence the naive rule missed: the gold chunk is never "
         "force-added to the evidence set, so nothing outside the evidence can "
         "support a claim."),
    ])
    deck.kpi(s, 7.62, 2.06, 2.40, "0.80", "a claim is called grounded at or "
             "above this score")
    deck.kpi(s, 10.22, 2.06, 2.41, "0.45", "a claim is called inferred at or "
             "above this score")
    deck.bullets(s, 7.62, 3.72, 5.01, [
        ("Anything below both is uncertain, ", "and is reported as uncertain "
         "rather than dropped."),
        ("The instrument is audited too: ", t("GEN_SCORER_TRUTH") + ", and "
         + t("GEN_SCORER_FAB") + ". A metric whose instrument is the "
         "contribution has to be audited rather than asserted."),
    ], size=12.5, gap=9)
    deck.takeaway(s, "Why this is a framework",
                  "The framework does not claim to produce a correct answer. "
                  "It declines where the evidence does not support one, and it "
                  "tags the claims it does make.")
    deck.notes(s, "Two thresholds, two meanings. The claim scorer carries a "
                  "published error profile, which is what makes the "
                  "hallucination metric quotable.")

    s = deck.slide("What the framework does not do",
                   "Five statements it never makes, and the sentence that "
                   "would overstate each one.")
    rows = [
        ["That it beats BM25 on recall", "The fusion recovered the dense "
         "leg's loss and stopped being a loss. It was not a significant win "
         "over the lexical leg on its own."],
        ["That it lowers the answer rate on unanswerable questions",
         "A random control refuses as many, and more, by luck. What the score "
         "buys is where the refusals land."],
        ["That the contradiction mechanism works", "Its precision against "
         "reader labels was " + t("CONTRA_PRECISION_PCT") + ", with a 95 "
         "percent upper bound of " + t("CONTRA_PRECISION_CI_HI") + ". It is "
         "unproven, not disproven."],
        ["That a fitted threshold transfers", "A threshold transferred "
         "unchanged across corpora over-refused badly: "
         + t("GEN_A_XFER_ANS_ANSWERED") + " against "
         + t("GEN_A_NOGATE_ANS_ANSWERED") + " answerable questions answered."],
        ["That a refusal is an answer", "The gate reduces the opportunity for "
         "a hallucination by declining. It does not make the answers it does "
         "give more correct."],
    ]
    deck.table(s, ML, 2.02, CW, ["The claim the framework refuses to make",
                                  "What the measurement actually supports"],
               rows, col_widths=[0.34, 0.66], size=12, head_size=10.5,
               row_h=0.62, head_h=0.32, bold_first=True)
    deck.takeaway(s, "Why this slide exists",
                  "Every one of these five sentences is true of the "
                  "measurements, and every one of them would be misleading in "
                  "a sentence. This slide is the answer before it is asked.")
    deck.notes(s, "Read the left column only if there is time. The point is "
                  "that the framework's own limits are on the record.")


# ------------------------------------------------------------------ 4
def part_methodology():
    deck.part = "methodology"
    section(4, "Methodology",
            "The corpora, the benchmark and the three repairs it needed, the "
            "metrics, the statistical protocol, and the five arms of the "
            "generation experiment.",
            ["The corpora", "How the benchmark was built",
             "Repair one: the answer labels",
             "Repair two: the unanswerable class",
             "Repair three: the form check", "The metrics",
             "The statistical protocol", "The five arms",
             "The two prompt conditions", "Reproducibility"],
            "The corpora, the benchmark, the metrics, the protocol and the arms.")

    s = deck.slide("The corpora, and what each one is for",
                   "Four corpora, four roles. Their numbers are never mixed, "
                   "because each was collected for a different experiment.")
    rows = [
        ["Supply-chain focus", "The ablation, the gate, the generation "
         "experiment", t("SCOPE_SCM_CHUNKS"), t("SCOPE_SCM_DOCS"),
         t("CASE_N_QUERIES"), t("CASE_N_ANSWERABLE") + " / " +
         t("CASE_N_UNANSWERABLE")],
        ["Six-category industrial", "Cross-category transfer, and the cost "
         "half of the long-context comparison", t("N_CHUNKS"),
         t("N_DOCUMENTS"), t("MC_N_QUERIES"), t("MC_N_ANSWERABLE") + " / " +
         t("MC_N_UNANSWERABLE")],
        ["Industrial", "The candidate-pool curve and the quota trade",
         t("IND_N_CHUNKS"), t("IND_N_DOCUMENTS"), t("IND_N_QUERIES"),
         t("IND_N_ANSWERABLE") + " / " + t("IND_N_UNANSWERABLE")],
        ["Federal regulatory", "The contradiction detector's phenomenon",
         t("SCOPE_RE_CHUNKS"), t("SCOPE_RE_DOCS"), "none", "none"],
    ]
    deck.table(s, ML, 2.02, CW, ["Corpus", "Role", "Chunks", "Documents",
                                  "Queries", "Answerable / Unanswerable"],
               rows, col_widths=[0.17, 0.32, 0.11, 0.12, 0.10, 0.18],
               size=11.5, head_size=10, row_h=0.66, head_h=0.46,
               bold_first=True)
    deck.bullets(s, ML, 4.86, CW, [
        ("The regulatory corpus carries no queries, ", "because it is not a "
         "benchmark corpus. It is in the study because its documents contain "
         "the instance-level measurements the contradiction detector looks "
         "for, and therefore no retrieval measurement is made on it."),
    ], size=12.5, gap=6)
    deck.takeaway(s, "The rule",
                  "Ablation and gate measurements sit on the focus corpus, the "
                  "transfer study on the six-category corpus, and the "
                  "contradiction study on the regulatory one.")
    deck.notes(s, "Point out the regulatory corpus has no queries. It is the "
                  "corpus the contradiction mechanism was built for, and "
                  "nothing was measured on it.")

    s = deck.slide("How the benchmark was built",
                   "Questions are generated from the corpus, against chunks "
                   "that state their answer and against documents that do not.")
    deck.prose(s, ML, 2.02, 6.55, 3.70, [
        ("The answerable class is generated against chunks that state the "
         "answer, ", "so that every answerable question has a gold chunk and "
         "a gold answer. Unanswerable questions are generated against "
         "documents that do not, so the question looks like it should be "
         "answerable and is not."),
        ("Both classes use the same three question stems, ", "the same source "
         "documents and the same label machinery. A class that is generated "
         "differently from the other one is a class that can be told apart by "
         "how it was written."),
        ("The gold chunk was always correct throughout, ", "so the "
         "retrieval-side measurements were never affected by the label defect "
         "described on the next slide. Only the answer side was depressed, and "
         "equally for every arm."),
    ])
    deck.card(s, 7.62, 2.02, 5.01, 1.62, "The three question families", [
        ("Definition, numeric fact and table lookup. ", "The family a "
         "question belongs to is part of its record, so a refusal rate can be "
         "read per family and not only in aggregate."),
    ], size=15, bsize=12.5)
    deck.card(s, 7.62, 3.84, 5.01, 2.00, "What a gold chunk is", [
        ("The chunk the benchmark says holds the answer. ", "Recall counts "
         "whether that chunk was retrieved. It was audited separately from "
         "the answer label, which is why one defect could be repaired without "
         "disturbing the other."),
    ], size=15, bsize=12.5)
    deck.takeaway(s, "The design",
                  "Both halves are generated the same way, so a difference "
                  "between them is a difference in the evidence and not in the "
                  "phrasing.")
    deck.notes(s, "This slide exists to make the next three slides make "
                  "sense. The benchmark is software, and its bugs are "
                  "invisible in its outputs.")

    s = deck.slide("Repair one: the answer labels",
                   "An audit of the benchmark's own answer labels found that "
                   "the labels were wrong on a third of the answerable "
                   "questions.")
    deck.kpi(s, ML, 2.06, 3.40, "30 of 32",
             "answerable questions carried an answer label attached to the "
             "wrong question")
    deck.kpi(s, 4.62, 2.06, 3.40, "1 of 32", "the defect rate after the "
             "repair")
    deck.kpi(s, 8.52, 2.06, 3.40, "0", "gold chunks were ever wrong")
    deck.bullets(s, ML, 3.62, 6.55, [
        ("Two defects caused it. ", "The table generator took its answer from "
         "the next column while naming the key's own column in the question, "
         "and the numeric regular expression captured an ordinal as a bare "
         "digit."),
        ("Both are one-line fixes, ", "and the defect rate afterwards is "
         "1 of 32."),
        ("The gold chunk was always correct, ", "so only the answer-side "
         "accuracy was depressed, and equally for every arm. The retrieval "
         "measurements stand."),
    ], size=13, gap=10)
    deck.card(s, 7.62, 3.62, 5.01, 2.30, "Why an audit at all", [
        ("A benchmark is a piece of software, ", "and its bugs do not show up "
         "in its outputs. The audit instrument is kept rather than deleted, "
         "because it is the instrument that found the defect, and the "
         "pre-repair benchmark sits beside the repaired one so that every "
         "before-and-after claim can be regenerated."),
    ], size=15, bsize=12.5)
    deck.takeaway(s, "The effect",
                  "Only the answer side moved, and it moved for every arm "
                  "equally, so the comparisons the benchmark supports were "
                  "never at stake.")
    deck.notes(s, "This is the repair that matters least for the headline and "
                  "matters most for the method.")

    s = deck.slide("Repair two: the unanswerable class",
                   "The class was separable from the question text alone, so "
                   "the headline refusal rate was an upper bound on the "
                   "benchmark rather than a measurement of the framework.")
    rows = [
        ["Separability from the question's shape",
         t("UNANS_BEFORE_AUC"), t("UNANS_SEP_AUC")],
        ["Question-only policy discrimination",
         t("UNANS_POLICY_BEFORE_AUC"), t("UNANS_POLICY_AUC")],
        ["Identifier-shortcut detection", t("UNANS_SHORTCUT_BEFORE"),
         t("UNANS_SHORTCUT_AFTER")],
        ["Gate refusal rate on the class", t("UNANS_BEFORE_REFUSED_PCT"),
         t("UNANS_HARD_REFUSED_PCT")],
    ]
    deck.table(s, ML, 2.02, 6.55, ["Quantity", "Before the repair",
                                   "After the repair"],
               rows, col_widths=[0.58, 0.21, 0.21], size=11.5,
               head_size=10, row_h=0.42, head_h=0.44, bold_first=True)
    deck.prose(s, 7.62, 2.02, 5.01, 3.40, [
        ("One family caused it. ", "The class's designated hard case named "
         "a fabricated identifier that no answerable question carried, and "
         "one regular expression caught that family completely."),
        ("The class was rebuilt rather than reported around. ", "Its "
         "replacement is corpus-anchored: the same three stems, the same "
         "source documents, the same label machinery."),
        ("Every repaired question is given a structural twin in the answerable "
         "class: ", "same stem, same subject size, same shape markers, and "
         "no word in common. The repair was validated rather than assumed, "
         "with " + t("UNANS_MATCH_RATE") + " certificates."),
    ], size=12.5, gap=9)
    deck.takeaway(s, "The point",
                  "The before-and-after gap is not a better system. It is a "
                  "better benchmark, and it took a repair to see it.")
    deck.notes(s, "The single most important slide in the deck. The "
                  "separator's structural twins are what make the repair "
                  "credible.")

    s = deck.slide("Repair three: the form check and the shortcut audit",
                   "The third repair is smaller, and the audit behind it is "
                   "the instrument that found the other two.")
    deck.bullets(s, ML, 2.02, 6.55, [
        ("The runtime form validator was measured against the "
         + t("FORMVAL_BENCH_N") + " benchmark queries and refused "
         + t("FORMVAL_BENCH_REJECTED") + " of them ("
         + t("FORMVAL_BENCH_RATE") + "). ", "All of them are generator "
         "artefacts that read as malformed rather than real questions."),
        ("On the hand-written sets it refused ", t("FORMVAL_FIX_MAL_REJECTED")
         + " of " + t("FORMVAL_FIX_MAL_TOTAL") + " malformed queries and "
         + t("FORMVAL_FIX_VAL_REJECTED") + " of " + t("FORMVAL_FIX_VAL_N")
         + " well-formed ones, at a cost of " + t("FORMVAL_COST_US") +
         " microseconds per query."),
        ("The two keyboard mashes in the malformed set are expected misses. ",
         "The check has no dictionary and no language model, so it misses a "
         "string that is not a word at all."),
    ], size=13, gap=11)
    deck.card(s, 7.62, 2.02, 5.01, 2.30, "The shortcut audit", [
        ("The question-only classifier is the audit instrument. ", "Before the "
         "repair it separated the two classes at ROC AUC "
         + t("UNANS_BEFORE_AUC") + ", against a permutation null of "
         + t("UNANS_BEFORE_NULL") + ". After the repair it is at "
         + t("UNANS_SEP_AUC") + " on the focus corpus and "
         + t("UNANS_MC_SEP_AUC") + " on the better-powered six-category one."),
    ], size=15, bsize=12.5)
    deck.card(s, 7.62, 4.42, 5.01, 1.40, "What is kept", [
        ("The instrument and the pre-repair benchmark, ", "so that every "
         "before-and-after claim can be regenerated rather than taken on "
         "trust."),
    ], size=15, bsize=12)
    deck.takeaway(s, "The generalisable lesson",
                  "Audit the benchmark's own shortcuts before trusting the "
                  "headline, and keep the instrument that did it.")
    deck.notes(s, "The shortcut audit is the reusable contribution. Publish "
                  "the benchmark and the audit so other work can check its "
                  "own benchmarks against the same instrument.")

    formula_slide(
        title="The retrieval metrics",
        kicker="Three measures, because they fail in different ways, and an "
               "ablation needs all three to say anything.",
        latex=r"\mathrm{Recall}@k=\frac{|R_k\cap G|}{|G|},\qquad "
              r"\mathrm{MRR}=\frac{1}{|Q|}\sum_{q\in Q}\frac{1}"
              r"{\mathrm{rank}_q},\qquad \mathrm{nDCG}@k="
              r"\frac{\mathrm{DCG}@k}{\mathrm{IDCG}@k}",
        width=6.30, fontsize=17,
        symbols=[
            ["R_k", "the top k results of the ranked list"],
            ["G", "the gold chunks, the ones holding the answer"],
            ["k", "how deep to look: " + t("RERANK_TOP_K_FINAL") + ", and also "
                  "20"],
            ["rank_q", "the rank of the gold chunk for query q"],
            ["Q", "the benchmark's queries"],
            ["IDCG@k", "the discounted gain of the best possible ordering"],
        ],
        source=("The three measures the retrieval side reports throughout. "
                "DCG is defined on the next slide."),
        value=("Why three. A system can find every answer and bury it, in "
               "which case recall ties and MRR loses. A system can find fewer "
               "answers and rank them better. Reporting recall alone would "
               "have made the reranker look worthless, and reporting MRR "
               "alone would have hidden that a configuration lost answers."),
        caveat=("Recall@10 on a benchmark whose gold chunk is in the pool is "
                "measured on the pool, not on the corpus. That is why the "
                "retriever's own recall of the gold is reported separately."),
        notes=("The ablation table later uses all three. Say why they are "
               "not redundant."),
    )

    formula_slide(
        title="Discounted cumulative gain",
        kicker="The third retrieval measure, weighted by position and "
               "normalised so that two systems can be compared.",
        latex=r"\mathrm{DCG}@k=\sum_{i=1}^{k}\frac{\mathrm{rel}_i}"
              r"{\log_2(i+1)}",
        width=4.30, fontsize=22,
        symbols=[
            ["rel_i", "how relevant the i-th result is, a weight"],
            ["i", "the position in the ranked list; 1 is the best"],
            ["log2(i+1)", "the discount: 1 at the top, growing slowly"],
            ["k", "how deep to look: " + t("RERANK_TOP_K_FINAL")],
        ],
        source=("A discounted gain, with a logarithmic discount. "
                "The relevance weight here is binary: the chunk is the gold one "
                "or it is not."),
        value=("Why a logarithm rather than a straight division. A linear "
               "discount would make position 1 worth as much as positions 2 "
               "to 10 combined. The logarithmic form says that moving from "
               "second to first is worth about the same as moving from eighth "
               "to ninth."),
        caveat=("Because the relevance is binary, DCG here is close to a "
                "position-weighted recall, and it is reported alongside MRR "
                "rather than instead of it."),
        notes=("Short slide. The binary relevance caveat is the honest part "
               "and worth saying."),
    )

    formula_slide(
        title="The answer rate and the refusal precision",
        kicker="Two different measurements over two different denominators, "
               "and the second one is the claim.",
        latex=r"r_{\mathrm{ans}}(U)=\frac{|\{q\in U:\mathrm{answered}(q)\}|}"
              r"{|U|},\qquad \mathrm{Prec}_{\mathrm{ref}}=\frac{"
              r"|\mathrm{refused}\cap U|}{|\mathrm{refused}|}",
        width=5.80, fontsize=18,
        symbols=[
            ["U", "a class of queries: answerable or unanswerable"],
            ["r_ans(U)", "the share of that class the system answered"],
            ["refused", "the set of queries the gate refused"],
            ["Prec_ref", "of the refusals, the share right to refuse"],
        ],
        source=("The two generation-side rates. Every comparison in the "
                "generation experiment is reported per class, never pooled."),
        value=("Why the second one is the claim. A practitioner wants to know "
               "whether the system is right when it says it does not know. "
               "That is the refusal precision, and it is "
               + t("FOCUS_GATE_ABST_PRECISION") + " at the fitted operating "
               "point."),
        caveat=("A system that refused everything would have a perfect "
                "refusal precision and be useless, which is why coverage is "
                "reported next to it. A gate can improve the unanswerable "
                "class and damage the answerable class at the same time."),
        notes=("This is the slide that separates the correct headline from "
               "the tempting one."),
    )

    formula_slide(
        title="The ROC AUC of a question-only policy",
        kicker="How the benchmark audit is scored: a classifier that sees only "
               "the question text, with no retrieval and no corpus.",
        latex=r"\mathrm{AUC}=P\left(s(x^{+})>s(x^{-})\right)",
        width=3.90, fontsize=24,
        symbols=[
            ["x+", "an answerable question"],
            ["x-", "an unanswerable question"],
            ["s(x)", "the score the policy gives the question"],
            ["AUC", "that a random unanswerable question scores lower"],
        ],
        source=("The discrimination measure used for the shortcut audit, and "
                "for the question-only policy that the audit compares against. "
                "A permutation null is reported beside it."),
        value=("Why not the raw detection rate. A question-only policy keys "
               "on the stem it was written for, so its raw detection rate is "
               "mostly explained by that stem. Discrimination is the part "
               "that is not."),
        caveat=("An AUC near 0.5 means the class is not decidable from the "
                "question's shape, which is what a real benchmark should look "
                "like."),
        notes=("The examiner may ask what the null is. It is a permutation "
               "null, and it is reported with its spread."),
    )

    formula_slide(
        title="The exact McNemar test",
        kicker="The test used for every comparison between two generation "
               "arms, and the reason the counts are on the slide rather than "
               "only the p-value.",
        latex=r"p=2\sum_{k=0}^{\min(b,c)}\binom{n}{k}\left(\frac{1}{2}"
              r"\right)^{n}",
        width=4.10, fontsize=24,
        symbols=[
            ["b", "questions the baseline answered and the arm refused"],
            ["c", "questions the baseline refused and the arm answered"],
            ["n", "b + c, the number of disagreements"],
            ["C(n,k)", "the number of ways to choose k of n"],
            ["p", "the probability of a split this lopsided"],
        ],
        source=("The exact McNemar test, applied to the paired arms. It "
                "computes the probability directly instead of approximating it "
                "with a normal curve, which matters at these counts."),
        value=("Why the disagreements are the whole test. The questions where "
               "both systems agreed tell the test nothing, because they cannot "
               "distinguish the arms. Only the b + c where they differ can."),
        caveat=("A p-value of 0.001 says the disagreement is not a coin flip. "
                "It does not say how large the effect is, and it does not say "
                "the effect transfers to another corpus or another generator."),
        notes=("The headline counts are b = " + t("GEN_PAIRED_FITTED_UNANS_B")
               + " and c = " + t("GEN_PAIRED_FITTED_UNANS_C") + " for the gate, "
               "and b = " + t("GEN_PAIRED_RANDOM_ANS_B") + " for the control. "
               "That difference is the finding."),
    )

    s = deck.slide("The statistical protocol",
                   "Three decisions in the protocol do real work, and each of "
                   "them changes what a number means.")
    deck.card(s, ML, 2.02, 3.87, 3.40, "Every comparison is paired", [
        ("The arms answer the same questions, ", "so an unpaired test throws "
         "away most of the available signal. Retrieval comparisons are "
         "paired over the same queries and tested with the Wilcoxon "
         "signed-rank test, with Cliff's delta and Cohen's d_z as effect "
         "sizes."),
    ], size=15, bsize=12.5)
    deck.card(s, 4.77, 2.02, 3.87, 3.40, "The test is applied per class", [
        ("A gate's effect on the unanswerable class and its effect on the "
         "answerable class are separate tests with separate hypotheses, ",
         "because a gate can improve the first and damage the second. One "
         "number for both would hide the trade."),
    ], size=15, bsize=12.5)
    deck.card(s, 8.82, 2.02, 3.79, 3.40, "Proportions carry intervals", [
        ("Wilson score intervals, not a bare proportion. ", "The bootstrap "
         "intervals are reported next to the point estimates so a reader can "
         "see the width of the evidence, which is what separates a null of "
         "this corpus at this size from a difference that was not found."),
    ], size=15, bsize=12.5)
    deck.takeaway(s, "The effect size",
                  "The counts b and c are on the slide beside the p-value, "
                  "because the counts are the effect and the p-value is only "
                  "the evidence against chance.")
    deck.notes(s, "The per-class decision is the one that matters most, and "
                  "it is what makes the refusal precision claim possible.")

    s = deck.slide("The five arms of the generation experiment",
                   "One generator behind five arms, each differing only in "
                   "what it removes. The fourth is the control that makes the "
                   "others readable.")
    rows = [
        ["rag_nogate", "the gate, keeping retrieval", "the baseline the "
         "others are measured against"],
        ["rag@fitted", "nothing: the framework at its fitted operating point",
         "the framework as it ships"],
        ["rag@random", "the confidence score, keeping the refusal budget",
         "the control: it refuses the same number of questions, chosen at "
         "random"],
        ["rag@transferred", "the fitted operating point, since the threshold "
         "is transferred unchanged", "the arm that shows a threshold does not "
         "travel"],
        ["long_context", "retrieval: the whole corpus goes into the prompt",
         "the comparison against long-context prompting"],
    ]
    deck.table(s, ML, 2.02, CW, ["Arm", "What it removes", "What it is for"],
               rows, col_widths=[0.16, 0.40, 0.44], size=12, head_size=10.5,
               row_h=0.56, head_h=0.32, bold_first=True)
    deck.takeaway(s, "Why the control matters",
                  "The gap between the fitted gate and the random control is "
                  "what the confidence score buys over refusing an arbitrary "
                  "set of the same size. Without that arm the other four rows "
                  "cannot be told apart.")
    deck.notes(s, "The random arm is the one to explain. It is what turns a "
                  "refusal rate into a claim about where refusals land.")

    s = deck.slide("The two prompt conditions",
                   "The prompt condition is an experimental axis, not a fixed "
                   "setting, and the two conditions differ by a single "
                   "sentence.")
    deck.prose(s, ML, 2.02, 6.55, 3.30, [
        ("Under one condition the generator may decline; under the other it "
         "must answer. ", "Model, questions, retrieval, scorer and "
         "temperature stay identical either way, and the two conditions are "
         "written to separate files and read back independently."),
        ("The two-condition design is not there for style. ", "Under the "
         "cautious prompt alone, the generator refused most of the "
         "unanswerable questions on its own. The gate's refusals were largely "
         "redundant, and the arms could not be told apart. That setup would "
         "have produced a null result that meant nothing."),
    ])
    deck.card(s, 7.62, 2.02, 5.01, 1.62, "The generator", [
        ("One generator, " + t("GEN_MODEL") + ", and " +
         t("GEN_CONDITIONS_RUN") + " prompt conditions. ",
         "One generator behind five arms settles the hypothesis once."),
    ], size=15, bsize=12.5)
    deck.card(s, 7.62, 3.84, 5.01, 2.00, "The replication that could not "
             "run", [
        ("A second generator returned no text on " +
         t("GENCOMP_FAILING_EMPTY_N") + " of "
         + t("GENCOMP_FAILING_EMPTY_TOTAL") + " questions. ",
         "Raising the output budget fourfold rescued "
         + t("GENCOMP_FAILING_RESCUED") + " and left "
         + t("GENCOMP_FAILING_STILL_EMPTY") + " still empty. The run is "
         "recorded as not run, with the reason, because a rate quoted from a "
         "run that did not happen is indistinguishable from a rate that did."),
    ], size=15, bsize=12.5)
    deck.takeaway(s, "The design decision",
                  "The answering condition exists so that the gate's "
                  "contribution cannot be confused with the generator's own "
                  "willingness to answer.")
    deck.notes(s, "Say why the cautious condition alone would have been "
                  "misleading. That is a design point, not a defensive one.")

    s = deck.slide("Reproducibility",
                   "What is deterministic, what is not, and what the claim "
                   "therefore covers.")
    deck.card(s, ML, 2.02, 6.55, 1.90, "The retrieval side", [
        ("Deterministic given the seed, ", "which is fixed at "
         + t("SEED") + " in the configuration. The mechanism's predictions "
         "are asserted directly: the category filter restricts both legs, the "
         "reranker only permutes its own pool, the quota stays inside its "
         "pool, and Platt scaling is monotone."),
    ], size=15, bsize=12.5)
    deck.card(s, ML, 4.12, 6.55, 1.90, "The generator side", [
        ("Not seed-controlled, ", "because the provider's sampling "
         "temperature is fixed rather than seed-controlled. Its "
         "reproducibility claim is therefore narrower: rates over a fixed "
         "question set, rather than identical answers."),
    ], size=15, bsize=12.5)
    deck.card(s, 7.62, 2.02, 5.01, 4.00, "What the assertions found", [
        ("Three real defects, none of them visible in the output. ",
         "The invariants are what caught them, and they are checked against "
         "the built artefact rather than against a description of it."),
        ("Behind this sits ", t("N_SOURCE_MODULES") +
         " source modules and " + t("N_TESTS") + " tests across "
         + t("N_TEST_FILES") + " test files, and " + t("N_EXPERIMENTS") +
         " recorded experiments."),
    ], size=15, bsize=12.5)
    deck.takeaway(s, "The honest claim",
                  "Rates over a fixed question set on the generator side, and "
                  "identical results on the retrieval side.")
    deck.notes(s, "Do not oversell the reproducibility. The narrower claim is "
                  "the one that is true.")


# ------------------------------------------------------------------ 5
def part_results():
    deck.part = "results"
    section(5, "Results",
            "Retrieval, the confidence gate, the benchmark audit, the "
            "generator, long context, and the contradiction mechanism. Every "
            "number comes from an archived result file.",
            ["The seven systems", "What the ablation changed",
             "The quota has no best placement", "The candidate-pool curve",
             "Calibration", "The operating-point sweep",
             "The risk-coverage frontier", "The benchmark audit",
             "The generator, under two conditions", "Long context",
             "The contradiction gate", "Attribution and transfer"],
            "Every number here comes from an archived result file.")

    s = deck.slide("Seven configurations over the same 32 answerable queries",
                   "The focus corpus, with a paired Wilcoxon signed-rank test "
                   "on every comparison.")
    rows = [
        ["A. bm25_only", t("R_A"), t("MRR_A"), t("NDCG_A"), t("TBL_A")],
        ["B. dense_only", t("R_B"), t("MRR_B"), t("NDCG_B"), t("TBL_B")],
        ["C. hybrid_rrf", t("R_C"), t("MRR_C"), t("NDCG_C"), t("TBL_C")],
        ["D. +rerank", t("R_D"), t("MRR_D"), t("NDCG_D"), t("TBL_D")],
        ["E. +category_filter", t("R_E"), t("MRR_E"), t("NDCG_E"), t("TBL_E")],
        ["F. +quota_pre_rerank", t("R_F"), t("MRR_F"), t("NDCG_F"), t("TBL_F")],
        ["G. +quota_post_rerank", t("R_G"), t("MRR_G"), t("NDCG_G"), t("TBL_G")],
    ]
    deck.table(s, ML, 2.02, CW, ["System", "Recall@10", "MRR", "nDCG@10",
                                  "Table recall"],
               rows, col_widths=[0.34, 0.17, 0.17, 0.17, 0.15], size=12,
               head_size=10.5, row_h=0.32, head_h=0.34, bold_first=True)
    deck.bullets(s, ML, 4.72, CW, [
        ("The dense leg is significantly worse than the lexical leg here. ",
         "Recall@10 falls from " + t("R_A") + " to " + t("R_B") + ", a paired "
         "difference of " + pnum(t("P_AB")) + " at p = " + pnum(t("P_AB")) + ". That "
         "finding is why the encoder was replaced."),
        ("Fusion recovers the loss and beats both legs. ", "Recall@10 reaches "
         + t("R_C") + " against " + t("R_B") + " for the dense leg alone, at p "
         "= " + pnum(t("P_BC")) + ". The claim is deliberately narrow: fusion "
         "stopped being a loss. It did not become a significant win over "
         "plain BM25 on its own."),
    ], size=12.5, gap=8)
    deck.notes(s, "Read the table's shape before the numbers. The order is "
                  "the ablation order, and each row adds one thing.")

    s = deck.slide("Three findings from the ablation, and one changed the "
                   "design",
                   "The reranker's value depends on the corpus, so the "
                   "sentence about it is never used without its corpus "
                   "attached.")
    deck.kpi(s, ML, 2.06, 3.40, t("RERANK_MRR_PP") + " pp",
             "the reranker moves MRR on the focus corpus")
    deck.kpi(s, 4.62, 2.06, 3.40, t("MC_MRR_RERANK_PP") + " pp",
             "the reranker moves MRR on the six-category corpus")
    deck.kpi(s, 8.52, 2.06, 3.40, t("MC_DELTA_CD_NDCG").replace("+", ""),
             "the nDCG it adds there")
    deck.bullets(s, ML, 3.72, 6.55, [
        ("On the focus corpus ", "the reranker moves MRR by "
         + t("RERANK_MRR_PP") + " points and nDCG by " + t("RERANK_NDCG_PP")
         + " points. Both are negative and neither is significant."),
        ("On the cross-category corpus ", "it moves MRR by "
         + t("MC_MRR_RERANK_PP") + " points at p = "
         + pnum(t("MC_P_CD_MRR")) + ", and nDCG by "
         + t("MC_DELTA_CD_NDCG") + " points at p = "
         + pnum(t("MC_P_CD_NDCG")) + ". The gain survives the transfer."),
        ("So the sentence ", "the reranker buys ordering, not recall is true "
         "on one corpus and false on the other. It is reported with its "
         "corpus attached everywhere it appears."),
    ], size=12.5, gap=10)
    deck.card(s, 7.62, 3.72, 5.01, 2.30, "What the archived baseline bought", [
        ("The previous general-purpose sentence encoder is archived, ", "and "
         "its numbers are kept as measured values rather than recalled, so "
         "both sides of the encoder comparison rest on measurements."),
        ("Keeping the baseline means ", "the comparison can be checked rather "
         "than taken on trust."),
    ], size=15, bsize=12)
    deck.takeaway(s, "The rule",
                  "A component that helps on one corpus and not on another is "
                  "not a component that helps.")
    deck.notes(s, "This is the finding that changed a design decision, so it "
                  "deserves its own slide rather than a footnote.")

    s = deck.slide("The modality quota has no universally better placement",
                   "The direction reverses between corpora, and none of the "
                   "three differences is statistically significant.")
    rows = [
        ["Supply-chain focus", t("QUOTA_PRE_FOCUS_R10"),
         t("QUOTA_POST_FOCUS_R10"), t("QUOTA_PLACE_FOCUS_P")],
        ["Six-category industrial", t("QUOTA_PRE_SIXCAT_R10"),
         t("QUOTA_POST_SIXCAT_R10"), t("QUOTA_PLACE_SIXCAT_P")],
        ["Industrial", t("QUOTA_PRE_IND_R10"), t("QUOTA_POST_IND_R10"),
         t("QUOTA_PLACE_IND_P")],
    ]
    deck.figure(s, "fig4_modality_quota_pareto", ML, 2.02, 3.90)
    deck.caption(s, 4.95, 2.02, 7.66, 1,
                 "Overall Recall@10 against table-specific Recall@10 for the "
                 "seven ablated systems, on the focus corpus (black circles) "
                 "and the industrial corpus (grey squares). The quota is a "
                 "trade, not a gain, and which way it trades depends on where "
                 "it is applied.")
    deck.table(s, 4.95, 3.24, 7.66, ["Corpus", "Quota before the reranker",
                                     "Quota after it", "p"],
               rows, col_widths=[0.37, 0.26, 0.22, 0.15], size=11.5,
               head_size=9.5, row_h=0.40, head_h=0.46, bold_first=True)
    deck.takeaway(s, "The conclusion",
                  "The placement is a configuration value rather than a rule, "
                  "and the ranking is reported with its corpus attached.",
                  x=4.95, w=7.66, y=5.48, h=1.04, stacked=True)
    deck.notes(s, "The figure is the two axes trading against each other. "
                  "Point at the industrial squares, where the pre-rerank "
                  "quota buys table recall and gives up overall recall.")

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
        ("On the focus corpus ", "Recall@10 peaks at " + t("POOL_PEAK") +
         " with a pool of ten and falls back to " + t("POOL20") + " at twenty, "
         "fifty and a hundred."),
        ("What is happening is visible in the recall at twenty, ", "which "
         "keeps rising as the pool grows: the gold chunk is still being found, "
         "and then the reranker pushes it out of the ten-chunk context. A "
         "larger pool costs ordering without adding the answer."),
    ], size=12.5, gap=9)
    deck.block(s, 4.95, 5.06, 7.66, 1.46, "The industrial corpus is the "
               "exception, and the exception is the point",
               "There the gold chunk is still arriving at twenty and fifty, so "
               "Recall@20 reaches " + t("IND_POOL_R20_AT_50") + " at a pool of "
               "fifty while Recall@10 stays at " + t("IND_POOL_R10_AT_50") +
               ". Some 1.21 points of gold are retrieved and then pushed out "
               "of the ten-chunk context.")
    deck.notes(s, "The mechanism is the same on both corpora: the gold is "
                  "found and then pushed out. The pool size at which that "
                  "starts differs.")

    s = deck.slide("The gate's calibration",
                   "The gate is a query-level model, fitted by Platt scaling "
                   "on a 60 percent calibration split of "
                   + t("CASE_N_QUERIES") + " queries.")
    rows = [
        ["Expected calibration error", t("GATE_ECE")],
        ["Brier score", t("GATE_BRIER")],
        ["Base rate of answer-in-context", "0.182"],
        ["Retriever recall of the gold chunk", t("GOLD_RECALL_PCT")],
    ]
    deck.figure(s, "fig3_calibration", ML, 2.02, 3.90)
    deck.caption(s, 4.95, 2.02, 7.66, 3,
                 "Reliability of the gate's calibrated probability against "
                 "observed answerability, on the held-out evaluation half. "
                 "The industrial gate tracks the diagonal; the focus gate does "
                 "not.")
    deck.table(s, 4.95, 3.02, 7.66, ["Metric", "Value"], rows,
               col_widths=[0.70, 0.30], size=12, head_size=10.5, row_h=0.36,
               head_h=0.34, bold_first=True)
    deck.prose(s, 4.95, 5.06, 7.66, 1.46, [
        ("An expected calibration error of " + t("GATE_ECE") +
         " is not excellent. ", "It is reported rather than improved by "
         "refitting. The gate is fitted once, on a fixed split, and the "
         "calibration numbers describe that fitted artefact."),
        ("Most of its queries land in the lowest confidence "
         "bin, ", "where few of them have an answer in context. That is what "
         "the number is made of."),
    ], size=12, gap=8)
    deck.notes(s, "Do not defend the calibration number. Report it and say "
                  "what it is made of, which is the shape of the "
                  "reliability diagram.")

    s = deck.slide("The operating-point sweep",
                   "The threshold is chosen by a stated rule, and the whole "
                   "frontier is shown because a single threshold hides the "
                   "shape behind it.")
    rows = []
    for r in focus_sweep():
        tau = r["tau"]
        if tau not in (0.05, 0.10, 0.15, 0.20, 0.30, 0.50, 0.90):
            continue
        rows.append([f"{tau:.2f}", f"{r['answerable_answered']:.3f}",
                     f"{r['unanswerable_refused']:.3f}",
                     f"{r['abstention_precision']:.3f}",
                     f"{r['coverage']:.3f}"])
    deck.table(s, ML, 2.02, 7.30, ["tau", "Answerable answered",
                                   "Unanswerable refused",
                                   "Abstention precision", "Coverage"],
               rows, col_widths=[0.12, 0.22, 0.22, 0.24, 0.20], size=11.5,
               head_size=9.5, row_h=0.32, head_h=0.48, bold_first=True)
    deck.prose(s, 8.40, 2.02, 4.20, 3.40, [
        ("The rule: ", "the highest tau that still answers at least 90 percent "
         "of the answerable queries. That gives " + t("FOCUS_GATE_TAU") + "."),
        ("The gate is precise where it refuses. ", "At the fitted operating "
         "point the abstention precision is " + t("FOCUS_GATE_ABST_PRECISION")
         + ", so almost every refusal lands on a question that should have "
         "been refused."),
        ("The frontier is real. ", "Every extra refusal is paid for in "
         "coverage, and the price climbs steeply past tau = 0.15."),
    ], size=12, gap=9)
    deck.takeaway(s, "The trade",
                  "At the fitted point the coverage is "
                  + t("FOCUS_GATE_COVERAGE") + " and the abstention precision "
                  "is " + t("FOCUS_GATE_ABST_PRECISION") + ". Both are "
                  "defensible, and they are not the same product.")
    deck.notes(s, "Read the first row and the last row, and the direction of "
                  "the two middle columns. The shape is what matters.")

    s = deck.slide("Why the threshold is " + t("FOCUS_GATE_TAU"),
                   "Every threshold in the framework has a stated rule behind "
                   "it, and this is the one an examiner will ask about.")
    deck.card(s, ML, 2.02, 3.87, 3.40, "The rule", [
        ("The highest threshold that still answers at least 90 percent of the "
         "answerable queries. ", "It is a rule, not a preference, and it is "
         "written down in the configuration before the sweep is run."),
        ("Why 90 percent. ", "The deployment framing is that a refusal costs "
         "a supervisor a few minutes, so most of the questions that can be "
         "answered should be answered."),
    ], size=15, bsize=12)
    deck.card(s, 4.77, 2.02, 3.87, 3.40, "What it buys", [
        ("At " + t("FOCUS_GATE_TAU") + ": ",
         "coverage of " + t("FOCUS_GATE_COVERAGE") + ", abstention precision of "
         + t("FOCUS_GATE_ABST_PRECISION") + ", and "
         + t("FOCUS_GATE_ANSWERABLE_ANSWERED_PCT") + " of answerable "
         "questions answered."),
    ], size=15, bsize=12)
    deck.card(s, 8.82, 2.02, 3.79, 3.40, "What it costs", [
        ("The price is coverage, and it climbs steeply. ",
         "At tau = 0.15 the coverage has fallen to 0.364, and at tau = 0.50 "
         "it is 0.097."),
        ("A threshold is a policy, not a property of the model. ",
         "A deployment team would have to calibrate it on its own corpus."),
    ], size=15, bsize=12)
    deck.takeaway(s, "The honest answer",
                  "The threshold was chosen by a rule that was written down "
                  "first, and the whole frontier is published so that a "
                  "reader can pick a different point on it.")
    deck.notes(s, "If the threshold is questioned, the answer is the rule, "
                  "and then the frontier. Both are on the table.")

    s = deck.slide("The risk-coverage frontier",
                   "The risk that an answered query has no answer in its "
                   "context, against the fraction of queries the gate answers.")
    deck.figure(s, "fig2_risk_coverage", ML, 2.02, 3.90)
    deck.caption(s, 4.95, 2.02, 7.66, 4,
                 "Risk-coverage of the confidence gate on the held-out "
                 "evaluation half. The degenerate policies bound the curve: "
                 "always answering carries the base rate of the negative "
                 "class, and always refusing removes the risk at the cost of "
                 "all coverage.")
    deck.prose(s, 4.95, 3.02, 7.66, 2.10, [
        ("The fitted operating points ", "are tau = "
         + t("FOCUS_GATE_TAU") + " on the focus corpus and tau = "
         + t("IND_GATE_TAU") + " on the industrial one, answering "
         + t("FOCUS_GATE_COVERAGE") + " and " + t("IND_GATE_COVERAGE") +
         " of all queries respectively."),
        ("On the industrial corpus the gate trades risk for coverage. ", "On the focus corpus it "
         "buys almost nothing over answering everything, and the reliability "
         "diagram on the previous slide shows why."),
    ], size=12.5, gap=9)
    deck.block(s, 4.95, 5.06, 7.66, 1.46, "What the frontier is for",
               "The operating point of the framework is the pair of coverage "
               "and risk it selects. This is the measurement of that frontier "
               "at the level of the individual answer claim, on a corpus "
               "regime that is not the procedural one every earlier "
               "deployment uses.")
    deck.notes(s, "The framing sentence is the contribution. The frontier "
                  "itself is a known idea; measuring it here, on this text, "
                  "at claim level, is the work.")

    s = deck.slide("The gate is an evidence gate, not a form gate",
                   "A distinction that decides which component is credited "
                   "with which job.")
    deck.bullets(s, ML, 2.02, 6.55, [
        ("The gate was probed ", "by pushing the real rejected stems from the "
         "generator's extraction through the pipeline. On the cross-category "
         "corpus it accepted " + t("FORM_PROBE_ACCEPTED") + " of "
         + t("FORM_PROBE_N") + " (" + t("FORM_PROBE_RATE") + ") at a mean "
         "posterior of " + t("FORM_PROBE_MEAN_POSTERIOR") + "."),
        ("So the gate is good at ", "asking whether there is evidence here, "
         "and of no use at asking whether this is even a question."),
        ("It is never credited with the second job. ", "That is what the "
         "runtime query-form validator is for, and the two components are kept "
         "apart on purpose."),
    ], size=13, gap=11)
    deck.card(s, 7.62, 2.02, 5.01, 1.70, "The validator's own numbers", [
        ("It refused " + t("FORMVAL_MC_STEM_MAL_REJECTED") + " of "
         + t("FORMVAL_MC_STEM_MAL_N") + " malformed stems on the "
         "cross-category corpus (" + t("FORMVAL_MC_STEM_MAL_RATE") + ") and "
         + t("FORMVAL_MC_STEM_GOOD_REJECTED") + " of "
         + t("FORMVAL_MC_STEM_GOOD_N") + " well-formed ones."),
    ], size=15, bsize=12)
    deck.card(s, 7.62, 3.92, 5.01, 2.00, "The counterfactual, again", [
        ("Reusing the benchmark builder's own subject rule would have refused ",
         t("FORMVAL_MC_COUNTERFACTUAL_REJECTED") + " of "
         + t("FORMVAL_MC_COUNTERFACTUAL_N") + " hand-labelled well-formed "
         "questions on that corpus, a 100 percent false-rejection rate."),
    ], size=15, bsize=12)
    deck.takeaway(s, "The distinction",
                  "Is there evidence here, and is this even a question, are "
                  "two questions with two different instruments.")
    deck.notes(s, "This slide exists so that the form validator is not "
                  "presented as part of the gate, and the gate is not "
                  "presented as a form checker.")

    s = deck.slide("The unanswerable class, before and after the repair",
                   "The headline refusal rate fell by a factor of nearly "
                   "four, and the number that replaced it is the one a "
                   "deployment would meet.")
    rows = [
        ["Separability from the question's shape",
         t("UNANS_BEFORE_AUC"), t("UNANS_SEP_AUC")],
        ["Question-only policy discrimination",
         t("UNANS_POLICY_BEFORE_AUC"), t("UNANS_POLICY_AUC")],
        ["Identifier-shortcut detection", t("UNANS_SHORTCUT_BEFORE"),
         t("UNANS_SHORTCUT_AFTER")],
        ["Gate refusal rate on the class", t("UNANS_BEFORE_REFUSED_PCT"),
         t("UNANS_HARD_REFUSED_PCT")],
    ]
    deck.table(s, ML, 2.02, 6.40, ["Quantity", "Before the repair",
                                   "After the repair"],
               rows, col_widths=[0.58, 0.21, 0.21], size=11.5,
               head_size=10, row_h=0.42, head_h=0.44, bold_first=True)
    deck.prose(s, 7.42, 2.02, 5.20, 3.50, [
        ("Before the repair ", "the headline refusal rate was "
         + t("UNANS_BEFORE_REFUSED_PCT") + ", and it was an upper bound rather "
         "than a measurement, because the class carried the answer in its own "
         "surface form."),
        ("After the repair ", "the gate refuses "
         + t("UNANS_HARD_REFUSED_PCT") + " of the corpus-anchored hard "
         "stratum, and " + t("UNANS_OOD_REFUSED_N") + " of the out-of-domain "
         "stratum."),
        ("The gap between the two strata is the finding. ", "What the gate "
         "detects is a recognisable unanswerable question, one drawn from "
         "outside the corpus or one whose subject is plainly absent. It is "
         "much weaker on the on-topic-but-unanswered case, where the corpus "
         "discusses the subject but does not state the answer."),
    ], size=12.5, gap=9)
    deck.takeaway(s, "The finding",
                  "A system with a " + t("UNANS_HARD_REFUSED_PCT") + " refusal "
                  "rate on the hard stratum is a different instrument from one "
                  "with a " + t("UNANS_BEFORE_REFUSED_PCT") + " rate on an easy "
                  "one, and the first number is the one a deployment meets.")
    deck.notes(s, "The out-of-domain stratum is the second half of the "
                  "finding and it is easy to leave out.")

    s = deck.slide("The shortcut audit",
                   "A classifier that sees only the question text, with no "
                   "retrieval, no evidence and no corpus.")
    deck.figure(s, "fig5_question_only_roc", ML, 2.02, 3.90)
    deck.caption(s, 4.95, 2.02, 7.66, 5,
                 "A question-only classifier telling an answerable question "
                 "from an unanswerable one, before and after the repair, with "
                 "a permutation null.")
    deck.prose(s, 4.95, 2.94, 7.66, 2.10, [
        ("Before the repair ", "the two classes were separable almost "
         "perfectly on the focus corpus, at ROC AUC " + t("UNANS_BEFORE_AUC")
         + " against a permutation null of " + t("UNANS_BEFORE_NULL") +
         ". One regular expression for a fabricated identifier caught "
         + t("UNANS_SHORTCUT_BEFORE") + " of the unanswerable questions with "
         "no false positive at all."),
        ("After the repair ", "the shortcut catches " +
         t("UNANS_SHORTCUT_AFTER") + ", and what is left of the procedure's "
         "power is small but not zero: AUC " + t("UNANS_SEP_AUC") + " on the "
         "focus corpus and " + t("IND_AUD_SEP_AUC") + " on the industrial "
         "one."),
    ], size=12.5, gap=9)
    deck.block(s, 4.95, 5.06, 7.66, 1.46, "The honest reading",
               "The unanswerable class is decidable from the evidence rather "
               "than from a question-shape rule, but on two of the three "
               "corpora it is not entirely free of form-only separability. "
               "That is stated rather than smoothed over.")
    deck.notes(s, "The last card is the part a careful reader wants. Say it "
                  "before it is asked for.")

    s = deck.slide("The framework's own hypothesis, under the answering "
                   "condition",
                   "The generator is required to answer, so the gate's "
                   "contribution is not mixed up with its willingness to "
                   "answer.")
    rows = [
        ["rag_nogate", t("GEN_A_NOGATE_UNANS_ANSWER_RATE"),
         t("GEN_A_NOGATE_ANS_ANSWERED"), "none", "none"],
        ["rag@fitted", t("GEN_A_FITTED_UNANS_ANSWER_RATE"),
         t("GEN_A_FITTED_ANS_ANSWERED"),
         "b = " + t("GEN_PAIRED_FITTED_UNANS_B") + ", c = " +
         t("GEN_PAIRED_FITTED_UNANS_C") + ", p = " +
         t("GEN_PAIRED_FITTED_UNANS_P"),
         "b = " + t("GEN_PAIRED_FITTED_ANS_B") + ", p = " +
         t("GEN_PAIRED_FITTED_ANS_P")],
        ["rag@random", t("GEN_A_RANDOM_UNANS_ANSWER_RATE"),
         t("GEN_A_RANDOM_ANS_ANSWERED"), "none",
         "b = " + t("GEN_PAIRED_RANDOM_ANS_B") + ", p = " +
         t("GEN_PAIRED_RANDOM_ANS_P")],
        ["rag@transferred", t("GEN_A_XFER_UNANS_ANSWER_RATE"),
         t("GEN_A_XFER_ANS_ANSWERED"), "none", "none"],
        ["long_context", t("GEN_A_LONGCTX_UNANS_ANSWER_RATE"),
         t("GEN_A_LONGCTX_ANS_ANSWERED"), "p = 1.00", "p = 1.00"],
    ]
    deck.table(s, ML, 2.02, CW, ["Arm", "Unanswerable answered",
                                  "Answerable answered",
                                  "McNemar, unanswerable",
                                  "McNemar, answerable"],
               rows, col_widths=[0.18, 0.18, 0.18, 0.25, 0.21], size=11,
               head_size=9.5, row_h=0.42, head_h=0.46, bold_first=True)
    deck.bullets(s, ML, 4.66, CW, [
        ("The gate reduces the rate of answering unanswerable questions from ",
         t("GEN_A_NOGATE_UNANS_ANSWER_RATE") + " to "
         + t("GEN_A_FITTED_UNANS_ANSWER_RATE") + ", a fall of 41.0 points, and "
         "the paired test is significant. The verdict is supported in the "
         "direction claimed."),
        ("The transferred arm over-refuses badly, ", "answering only "
         + t("GEN_A_XFER_ANS_ANSWERED") + " against "
         + t("GEN_A_NOGATE_ANS_ANSWERED") + " for the ungated arm."),
    ], size=12.5, gap=8)
    deck.notes(s, "Do not read the table row by row. Read the fitted row and "
                  "the no-gate row, and let the table carry the rest.")

    s = deck.slide("Under the cautious condition, the verdict still holds",
                   "And it holds for a different reason, which is why the "
                   "second condition is not a formality.")
    deck.kpi(s, ML, 2.06, 3.40, "0.417",
             "the rate of answering unanswerable questions under a prompt "
             "that permits a decline, down from 0.535")
    deck.kpi(s, 4.62, 2.06, 3.40, t("GEN_A_FITTED_ANS_ANSWERED"),
             "answerable questions answered by the gated arm")
    deck.kpi(s, 8.52, 2.06, 3.40, "p = 0.002",
             "the paired exact McNemar test on the unanswerable class")
    deck.bullets(s, ML, 3.72, 6.55, [
        ("The fall is smaller than under the answering condition, ", "because "
         "the generator was already refusing most of the unanswerable "
         "questions on its own."),
        ("The gate's refusals were largely redundant there, ", "and the arms "
         "could not be told apart. That setup would have produced a null "
         "result that meant nothing."),
        ("So the cautious condition is not the primary result. ", "It is the "
         "condition that shows the primary result is not an artefact of the "
         "prompt."),
    ], size=12.5, gap=10)
    deck.card(s, 7.62, 3.72, 5.01, 2.30, "The rule this imposes", [
        ("A cautious-condition null has to be reported as ", "the prompt had "
         "already realised the gate's function on that slice, and never as "
         "confidence gating does not work. That is a rule about how a null "
         "may be described, and it comes from the literature this work "
         "cites."),
    ], size=15, bsize=12)
    deck.takeaway(s, "The verdict",
                  "Supported under both prompt conditions, and for a "
                  "different reason in each.")
    deck.notes(s, "The second condition is a check on the first. Say that "
                  "plainly.")

    s = deck.slide("What the confidence score actually buys",
                   "This is the finding most likely to be reported wrongly, so "
                   "it gets its own slide.")
    deck.prose(s, ML, 2.02, 6.55, 3.30, [
        ("It does not buy a lower answer rate on unanswerable questions. ",
         "A random control achieves " + t("GEN_A_RANDOM_UNANS_ANSWER_RATE")
         + ", which is worse than the fitted gate's "
         + t("GEN_A_FITTED_UNANS_ANSWER_RATE") + ", yet still far below the "
         "ungated arm's " + t("GEN_A_NOGATE_UNANS_ANSWER_RATE") + "."),
        ("It gets there by refusing an arbitrary set of the same size, ", "and "
         "some of those are answerable questions. Refusing questions at random "
         "is already a large improvement over never refusing, because most "
         "questions in a benchmark are unanswerable."),
        ("What the confidence score buys is where the refusals land. ",
         "The fitted gate refuses " + t("GEN_PAIRED_FITTED_ANS_B") +
         " answerable questions where the random control refuses "
         + t("GEN_PAIRED_RANDOM_ANS_B") + "."),
    ])
    deck.card(s, 7.62, 2.02, 5.01, 1.70, "The evidence", [
        ("A paired test on the answerable class gives p = "
         + t("GEN_PAIRED_FITTED_ANS_P") + " for the gate and p = "
         + t("GEN_PAIRED_RANDOM_ANS_P") + " for the control. ",
         "Concentrating refusals on the unanswerable class is a precision "
         "claim, and the test on the answerable questions is where it is "
         "established."),
    ], size=15, bsize=12)
    deck.card(s, 7.62, 3.92, 5.01, 2.00, "The sentence to avoid", [
        ("A report that said the gate answers fewer unanswerable questions ",
         "would have been true and misleading, because the random control "
         "answers fewer still."),
    ], size=15, bsize=12)
    deck.takeaway(s, "The finding",
                  "The confidence score buys refusal precision, not a lower "
                  "answer rate, and the paired test on the answerable class "
                  "is where that is established.")
    deck.notes(s, "If only one results slide is remembered, it should be this "
                  "one.")

    s = deck.slide("The trade, counted from the records",
                   "Under the answering condition, the gate removes "
                   + t("TRADE_ANSWERING_WRONG_REMOVED") + " wrong answers and "
                   "costs " + t("TRADE_ANSWERING_CORRECT_COST_NLI") +
                   " correct answer under the entailment test.")
    rows = [
        ["rag_nogate", t("TRADE_ANSWERING_NOGATE_ANSWERED"),
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
         t("TRADE_ANSWERING_LONGCTX_CORRECT_KEYTERM")],
    ]
    deck.table(s, ML, 2.02, CW, ["Arm", "Answered", "Of which wrong",
                                  "Correct (entailment)",
                                  "Correct (key term)"],
               rows, col_widths=[0.20, 0.16, 0.18, 0.24, 0.22], size=12,
               head_size=10, row_h=0.38, head_h=0.46, bold_first=True)
    deck.bullets(s, ML, 4.42, CW, [
        ("Under the cautious condition the trade looks different. ",
         "The gate removes " + t("TRADE_CAUTIOUS_WRONG_REMOVED") +
         " wrong answers and, under the entailment test, ends up ahead on "
         "the correct count."),
        ("That is not a quality gain. It is a selection effect. ",
         "A gate declines the hardest questions, so the ones it does answer "
         "are easier, and its per-answer accuracy cannot be compared with "
         "that of an arm that answered everything."),
    ], size=12.5, gap=8)
    deck.takeaway(s, "The caveat",
                  "Whether this trade is worth making is a domain judgement, "
                  "and these measurements do not settle it. What they settle "
                  "is what the gate removed and what it cost.")
    deck.notes(s, "The selection effect is the trap here. The correct "
                  "count going up is not the gate answering better.")

    s = deck.slide("Long context against the pipeline, on cost",
                   "The focus corpus is " + t("LC_CORPUS_TOKENS") +
                   " tokens against the pipeline's accepted context of "
                   + t("LC_RAG_TOKENS") + " tokens.")
    deck.kpi(s, ML, 2.10, 3.40, t("GEN_LC_TOKEN_RATIO") + "x",
             "the input tokens per query, whole corpus against accepted "
             "context")
    deck.kpi(s, 4.62, 2.10, 3.40, t("GEN_LC_COST_RATIO") + "x",
             "the input cost per query, at the provider's cached-prefix "
             "pricing")
    deck.kpi(s, 8.52, 2.10, 3.40, t("GEN_LC_CACHE_HIT"),
             "of requests served as a cache read")
    deck.bullets(s, ML, 3.86, 6.55, [
        ("The cost correction matters. ", "Read the token ratio naively and "
         "the cost penalty looks two orders of magnitude larger than the one "
         "measured, because most of the long-context arm's tokens are cache "
         "reads at a fifth of the base rate."),
        ("A token ratio must never carry an argument about money. ",
         "The cost ratio is derived from the token ratio and the cache share, "
         "so the two always have to travel together."),
    ], size=13, gap=11)
    deck.card(s, 7.62, 3.86, 5.01, 2.16, "The cross-category half", [
        ("The cross-category corpus is ", t("MC_LC_CORPUS_TOKENS") +
         " tokens, " + t("MC_LC_CORPUS_VS_128K") + " times the 128K-token "
         "limit, so it does not fit a 128K context window and the quality "
         "half of that comparison could not be run there. On that corpus the "
         "comparison is settled on cost and coverage alone."),
    ], size=15, bsize=12)
    deck.takeaway(s, "The reading",
                  "A token ratio is the size of the prompt. A cost ratio is "
                  "is what the prompt costs. Only the second one belongs in "
                  "an argument about money.")
    deck.notes(s, "The two ratios are different measurements of different "
                  "things, and the cost one is the one that matters.")

    s = deck.slide("Long context, on coverage and quality",
                   "No superiority claim is made over long-context prompting "
                   "on this corpus, because the measurement does not support "
                   "one.")
    deck.bullets(s, ML, 2.02, 6.55, [
        ("With the whole corpus in the prompt, ", "the generator answered "
         + t("GEN_A_LONGCTX_ANS_ANSWERED") + " answerable questions, the same "
         "coverage as the ungated pipeline, and declined the unanswerable "
         "questions at a comparable rate."),
        ("Its per-answer accuracy was ", t("GEN_A_LONGCTX_ANS_ACCURACY") +
         " against " + t("GEN_A_FITTED_ANS_ACCURACY") + " for the gated arm, "
         "and the accuracy margin is not significant under a length-controlled "
         "re-scoring of the same answers."),
        ("The retrieval-side proxy ", "was measured on both corpora by "
         "widening the candidate set to every chunk. The gold chunk lands in "
         "the top ten for " + t("LC_PROXY_TOP10") + " of the focus queries "
         "and " + t("MC_LC_PROXY_TOP10") + " of the cross-category ones, at a "
         "median rank of " + t("LC_PROXY_MEDIAN_RANK") + "."),
    ], size=12.5, gap=11)
    deck.card(s, 7.62, 2.02, 5.01, 2.30, "What that proxy means", [
        ("The evidence is not lost in a large context; the tail is where "
         "corpus size bites. ", "A retriever that finds the gold chunk at "
         "median rank 1 in a pool of " + t("LC_CORPUS_CHUNKS") +
         " chunks has no use for the other " + t("LC_CORPUS_CHUNKS") + "."),
    ], size=15, bsize=12)
    deck.card(s, 7.62, 4.52, 5.01, 1.30, "The claim", [
        ("No superiority claim is made. ", "On this corpus the whole-corpus prompt wins on "
         "neither coverage nor cost."),
    ], size=15, bsize=12)
    deck.takeaway(s, "The interpretation",
                  "The long-context arm is not a strawman and not a "
                  "winner. It is the alternative a reader would ask about, "
                  "measured on both sides.")
    deck.notes(s, "Say that no superiority claim is made. It is the easiest "
                  "place to overclaim in this whole deck.")

    s = deck.slide("The contradiction gate: a precision of zero",
                   "Measured against reader labels rather than against the "
                   "detector's own threshold, and reported as a null.")
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
    deck.figure(s, "fig6_contradiction_precision", ML, 2.02, 3.90)
    deck.caption(s, 4.95, 2.02, 7.66, 6,
                 "The contradiction detector's precision against the base rate "
                 "of real conflicts, with 95 percent Wilson intervals. A "
                 "filled marker clears the framework's calibration floor and "
                 "the branch would act.")
    deck.table(s, 4.95, 2.94, 7.66, ["Quantity", "Value"], rows,
               col_widths=[0.72, 0.28], size=11.5, head_size=10, row_h=0.32,
               head_h=0.32, bold_first=True)
    deck.block(s, 4.95, 5.06, 7.66, 1.46, "The wording",
               "Not one of the raised alarms was confirmed. The annotators do "
               "not share a model, both read the sheet blind to the "
               "detector's scores, and both were 14 of 14 correct on a "
               "control set whose labels were known in advance. The result "
               "is reported as unconfirmed with a stated upper bound, not as "
               "a defect to be explained away.")
    deck.notes(s, "Do not soften this and do not overexplain it. It is a null "
                  "with a stated bound, and the caveat about model-based "
                  "annotators goes with it.")

    s = deck.slide("The corpus does not hold the phenomenon",
                   "Which is why the mechanism is unproven rather than "
                   "disproved, and why the two detector defects are not the "
                   "reason for the null.")
    deck.card(s, ML, 2.02, 6.10, 2.30, "What the readers found in the rest", [
        ("The readers found " + t("CONTRA_UNFLAGGED_CONTRADICTIONS") +
         " contradictions in a random sample of " +
         t("CONTRA_UNFLAGGED_SAMPLE") + " pairs the gate did not flag. ",
         "That is a statement about the corpus rather than about the "
         "detector."),
    ], size=15, bsize=12.5)
    deck.card(s, ML, 4.42, 6.10, 1.40, "What that means", [
        ("This corpus holds concept-level prose, not instance records, ",
         "so it does not contain the phenomenon the mechanism detects."),
    ], size=15, bsize=12)
    deck.prose(s, 7.20, 2.02, 5.40, 3.40, [
        ("The audit exposed two real defects, and both were repaired. ",
         "One keyed numbers to the nearest distinctive word, so it fired on "
         "citation years. The other let topical similarity through on its "
         "own, which made it a topic check rather than a contradiction check."),
        ("Requiring a shared measurement and a shared instance cut the "
         "alarms from ", t("CONTRA_ALARMS_BEFORE") + " to "
         + t("CONTRA_ALARMS_AFTER") + "."),
        ("Those two defects were not the reason the remaining alarms were "
         "unconfirmed. ", "The reason is the corpus. Both facts are reported, "
         "because the second is easy to mistake for the first."),
    ], size=12.5, gap=9)
    deck.takeaway(s, "The wording",
                  "A high recall in a corpus with nothing to find is a "
                  "statement about the corpus. A precision of zero against "
                  "reader labels is a statement about the detector.")
    deck.notes(s, "This slide separates two things that get confused: a "
                  "detector that is wrong, and a corpus that does not "
                  "contain the phenomenon.")

    s = deck.slide("Attribution and answer position",
                   "The same answers, scored against two different evidence "
                   "sets, and the gap between the two columns is large.")
    rows = [
        ["Grounded claims, error rate", t("RO5_RETRIEVED_GROUNDED_ERROR"),
         t("RO5_GOLD_GROUNDED_ERROR")],
        ["Inferred claims, error rate", t("RO5_RETRIEVED_INFERRED_ERROR"),
         t("RO5_GOLD_INFERRED_ERROR")],
        ["Uncertain claims, error rate", t("RO5_RETRIEVED_UNCERTAIN_ERROR"),
         t("RO5_GOLD_UNCERTAIN_ERROR")],
        ["Reference hallucination rate",
         t("RO5_RETRIEVED_REFERENCE_HALLUCINATION"),
         t("RO5_GOLD_REFERENCE_HALLUCINATION")],
        ["Answer-position effect, p", t("RO5_RETRIEVED_POSITION_P"),
         t("RO5_GOLD_POSITION_P")],
    ]
    deck.table(s, ML, 2.02, 7.10, ["Error measure", "Over the retrieved "
                                   "evidence", "Over the gold evidence"],
               rows, col_widths=[0.44, 0.28, 0.28], size=11.5,
               head_size=10, row_h=0.38, head_h=0.46, bold_first=True)
    deck.prose(s, 8.10, 2.02, 4.50, 3.40, [
        ("Most of the error the framework's own attribution cannot explain ",
         "is explained by the evidence it was given, not by the attribution "
         "logic. A grounded-claim error rate of "
         + t("RO5_RETRIEVED_GROUNDED_ERROR") + " over the evidence the arm was "
         "shown becomes " + t("RO5_GOLD_GROUNDED_ERROR") + " over the gold "
         "chunk."),
        ("Keeping the first claims of an answer ", "carries a higher risk "
         "than keeping the band of claims the scorer calls grounded: "
         + t("RO5_GOLD_BAND_MINUS_FIRST") + " on the focus domain and "
         + t("RO5_RETRIEVED_BAND_MINUS_FIRST") + " on the retrieved "
         "evidence."),
        ("The direction replicates in three of the four measurements and ties "
         "in one. ", "Its magnitude does not, so the claim is stated with the "
         "magnitude rather than as a rule."),
    ], size=12, gap=9)
    deck.takeaway(s, "The implication",
                  "Most unattributed error comes from the evidence given, "
                  "which is a retrieval problem rather than an attribution "
                  "problem.")
    deck.notes(s, "The two columns are the same answers scored against "
                  "different evidence. That is the whole argument.")

    s = deck.slide("Cross-category transfer",
                   "The reranker's gain survives the transfer. A fitted "
                   "threshold does not.")
    rows = [
        ["A to C, BM25 to fusion", t("MC_DELTA_AC"), t("MC_DELTA_AC_MRR"),
         "none", pnum(t("MC_P_AC"))],
        ["C to D, fusion to rerank", t("MC_DELTA_CD"), t("MC_DELTA_CD_MRR"),
         t("MC_DELTA_CD_NDCG"), pnum(t("MC_P_CD_MRR"))],
    ]
    deck.table(s, ML, 2.02, CW, ["Comparison", "Delta Recall@10", "Delta MRR",
                                  "Delta nDCG", "p (MRR)"],
               rows, col_widths=[0.30, 0.18, 0.16, 0.16, 0.20], size=12,
               head_size=10, row_h=0.40, head_h=0.46, bold_first=True)
    deck.bullets(s, ML, 3.30, 6.55, [
        ("The fusion's recall advantage over BM25 does not survive, ", "while "
         "the reranker's gain does: " + t("MC_DELTA_CD_MRR") + " points of MRR "
         "at p = " + pnum(t("MC_P_CD_MRR")) + "."),
        ("A threshold transferred unchanged across corpora over-refuses "
         "badly: ", t("GEN_A_XFER_ANS_ANSWERED") + " against "
         + t("GEN_A_NOGATE_ANS_ANSWERED") + " answerable questions answered, "
         "and " + t("GEN_A_XFER_UNANS_ANSWER_RATE") + " of the unanswerable "
         "class answered."),
    ], size=12.5, gap=10)
    deck.card(s, 7.62, 3.30, 5.01, 2.10, "What the transfer study can and "
             "cannot measure", [
        ("It measures coverage on answerable questions across categories only. ",
         "The benchmark's unanswerable questions carry no category, so neither "
         "half contains any, and refusal behaviour across domains is not "
         "measurable under a category split. That is stated rather than "
         "claimed."),
    ], size=15, bsize=12)
    deck.takeaway(s, "The finding",
                  "A calibrated threshold does not transfer across corpora, "
                  "and has to be refitted per corpus.")
    deck.notes(s, "The transferred arm is the evidence for the last line of "
                  "the takeaway. It is also the arm a deployment team would "
                  "most want to avoid.")

    s = deck.slide("An empty completion is a third outcome",
                   "The replication could not be run, and the reason was "
                   "measured rather than guessed.")
    rows = [
        ["MiniMax-M3", "0 of 66", "0 of 44", "0 of 22", "0", "0"],
        [t("GENCOMP_FAILING_MODEL"),
         t("GENCOMP_FAILING_EMPTY_N") + " of "
         + t("GENCOMP_FAILING_EMPTY_TOTAL"),
         t("GENCOMP_FAILING_EMPTY_TABLE_N") + " of "
         + t("GENCOMP_FAILING_EMPTY_TABLE_TOTAL"), "1 of 22",
         t("GENCOMP_FAILING_RESCUED"),
         t("GENCOMP_FAILING_STILL_EMPTY")],
    ]
    deck.table(s, ML, 2.02, CW, ["Generator", "No text returned",
                                  "On the table-lookup family",
                                  "On a control sample",
                                  "Rescued by a 4x budget", "Still empty"],
               rows, col_widths=[0.22, 0.16, 0.20, 0.16, 0.14, 0.12], size=11,
               head_size=9, row_h=0.50, head_h=0.56, bold_first=True)
    deck.bullets(s, ML, 3.66, 6.55, [
        ("Raising the output budget fourfold rescued "
         + t("GENCOMP_FAILING_RESCUED") + " and left "
         + t("GENCOMP_FAILING_STILL_EMPTY") + " still empty. ",
         "So this is not a shortage of output room. The model spends its "
         "budget thinking and returns nothing."),
        ("The run is recorded as not run, with the reason. ",
         "A rate quoted from a run that did not happen is indistinguishable "
         "from a rate that did."),
    ], size=12.5, gap=10)
    deck.card(s, 7.62, 3.66, 5.01, 2.16, "A practical argument for the gate", [
        ("A generator that declines on its own costs a model call. ",
         "A generator that returns nothing costs a model call and produces "
         "nothing. On the questions the gate rejects, the framework spends "
         "nothing at all."),
    ], size=15, bsize=12.5)
    deck.takeaway(s, "The methodological consequence",
                  "An empty completion is neither an answer nor a refusal. A "
                  "run like that is recorded as not run, with the reason.")
    deck.notes(s, "This is the reason the replication is a limitation rather "
                  "than a gap in the work.")

    s = deck.slide("The fourteen measured findings",
                   "Part one: retrieval, the gate, and the benchmark.")
    rows = [
        ["F1", "The dense leg is significantly worse than BM25 on the focus "
         "corpus, and fusion recovers it",
         t("R_A") + " vs " + t("R_B") + " vs " + t("R_C")],
        ["F2", "The reranker's value depends on the corpus",
         t("RERANK_MRR_PP") + " pp on focus vs " + t("MC_MRR_RERANK_PP") +
         " pp on six-category"],
        ["F3", "The quota placement has no universally better answer, and none "
         "of the three differences is significant",
         "p = " + t("QUOTA_PLACE_FOCUS_P") + ", " + t("QUOTA_PLACE_SIXCAT_P") +
         ", " + t("QUOTA_PLACE_IND_P")],
        ["F4", "The candidate-pool curve peaks and then declines",
         "pool of " + t("POOL_PEAK") + " on focus, " + t("POOL10") +
         " against " + t("POOL50") + " on industrial"],
        ["F5", "The gate is precise where it refuses",
         "abstention precision " + t("FOCUS_GATE_ABST_PRECISION")],
        ["F6", "The gate detects a recognisable unanswerable question, not an "
         "absent answer",
         t("UNANS_HARD_REFUSED_PCT") + " on the hard stratum vs " +
         t("UNANS_OOD_REFUSED_N") + " out of domain"],
        ["F7", "The framework's hypothesis is supported under both prompt "
         "conditions",
         "McNemar p " + t("GEN_PAIRED_FITTED_UNANS_P") + " (answering) and " +
         t("GEN_PAIRED_CAUTIOUS_UNANS_P") + " (cautious)"],
    ]
    deck.table(s, ML, 2.02, CW, ["", "Finding", "Evidence"], rows,
               col_widths=[0.05, 0.52, 0.43], size=11, head_size=10,
               row_h=0.46, head_h=0.32, bold_first=True)
    deck.notes(s, "Seven findings. Do not read them all aloud; point at the "
                  "ones the committee has reached.")

    s = deck.slide("The fourteen measured findings",
                   "Part two: the score, the contradiction gate, long context, "
                   "and the two instruments.")
    rows = [
        ["F8", "The confidence score buys refusal precision, not a lower "
         "answer rate",
         "b = " + t("GEN_PAIRED_FITTED_ANS_B") + " vs b = " +
         t("GEN_PAIRED_RANDOM_ANS_B") + " answerable refused"],
        ["F9", "The gate is an evidence gate, not a form gate",
         t("FORM_PROBE_RATE") + " of malformed stems accepted"],
        ["F10", "The contradiction gate's precision against reader labels is "
         + t("CONTRA_PRECISION_PCT"),
         t("CONTRA_PRECISION_N") + " alarms, upper bound " +
         t("CONTRA_PRECISION_CI_HI")],
        ["F11", "Long context costs " + t("GEN_LC_TOKEN_RATIO") + " times the "
         "tokens and " + t("GEN_LC_COST_RATIO") + " times the input cost",
         t("LC_CORPUS_TOKENS") + " vs " + t("LC_RAG_TOKENS") + " tokens"],
        ["F12", "A calibrated threshold does not transfer across corpora",
         t("GEN_A_XFER_ANS_ANSWERED") + " against " +
         t("GEN_A_NOGATE_ANS_ANSWERED") + " answerable answered"],
        ["F13", "Most unattributed error comes from the evidence given, not "
         "from the attribution logic",
         t("RO5_RETRIEVED_GROUNDED_ERROR") + " vs " +
         t("RO5_GOLD_GROUNDED_ERROR")],
        ["F14", "An empty completion is a third outcome, not a refusal",
         t("GENCOMP_FAILING_EMPTY_N") + " of " +
         t("GENCOMP_FAILING_EMPTY_TOTAL") + " questions"],
    ]
    deck.table(s, ML, 2.02, CW, ["", "Finding", "Evidence"], rows,
               col_widths=[0.05, 0.52, 0.43], size=11, head_size=10,
               row_h=0.46, head_h=0.32, bold_first=True)
    deck.takeaway(s, "How to read them",
                  "Two of the fourteen are about the instruments rather than "
                  "the system, and they are the ones that changed a headline "
                  "number.")
    deck.notes(s, "F2, F10 and F13 are the ones that would have been "
                  "reported wrongly.")


# ------------------------------------------------------------------ 6
def part_conclusion():
    deck.part = "conclusion"
    section(6, "Conclusion, limitations and future work",
            "What the measurements establish, what they do not, what would "
            "change the claims, and what comes next.",
            ["What the measurements establish", "The negative results",
             "Threats to validity", "What this changes for practice",
             "The limitations", "The conclusion", "The future work"],
            "What the measurements establish, and what they do not.")

    s = deck.slide("What the measurements establish",
                   "Three things, and the middle one is the one that is easy "
                   "to state wrongly.")
    deck.card(s, ML, 2.02, 3.87, 3.40, "The gate works, but not in the way it "
             "is usually described", [
        ("It does not work by answering fewer unanswerable questions than a "
         "control. ", "A random control refuses as many, and more, by luck, "
         "because most of a benchmark is unanswerable."),
        ("It works by placing its refusals. ", "It concentrates them on the "
         "class that should be refused and spends almost none on the class "
         "that should not. That is a precision claim, established by a paired "
         "test on the answerable class."),
    ], size=14.5, bsize=12)
    deck.card(s, 4.77, 2.02, 3.87, 3.40, "The cost of the gate is coverage, "
             "not quality", [
        ("Counting from the records, ", "the gate removes "
         + t("TRADE_ANSWERING_WRONG_REMOVED") + " wrong answers under the "
         "answering condition and costs "
         + t("TRADE_ANSWERING_CORRECT_COST_NLI") + " correct answer under "
         "the entailment test."),
        ("Its per-answer accuracy cannot be compared with "
         "that of an ungated arm, ", "because the gated arm's answers are a "
         "selected and easier subset."),
    ], size=14.5, bsize=12)
    deck.card(s, 8.82, 2.02, 3.79, 3.40, "The benchmark was the harder half "
             "of the problem", [
        ("A refusal benchmark whose unanswerable half is separable from the "
         "question text ", "reports the benchmark's shortcut, not the "
         "system's capability."),
        ("Finding that, rebuilding the class, and reporting the fall from ",
         t("UNANS_BEFORE_REFUSED_PCT") + " to " + t("UNANS_HARD_REFUSED_PCT")
         + " is a contribution in its own right."),
    ], size=14.5, bsize=12)
    deck.takeaway(s, "The contribution",
                  "A cost-coverage-reliability frontier for a confidence gate "
                  "on industrial text, measured at the level of the individual "
                  "answer claim.")
    deck.notes(s, "The middle card is the one to slow down on. The cost of "
                  "the gate is coverage, and saying so protects the "
                  "strongest result.")

    s = deck.slide("The negative results, and what they mean",
                   "Three results that would each be easy to misreport, and "
                   "each of them reported here as what it is.")
    deck.card(s, ML, 2.02, 3.87, 3.40, "The contradiction gate's precision is "
             + t("CONTRA_PRECISION_PCT"), [
        ("It is tempting to report the recall, ", "the fact that the gate "
         "flagged " + t("CONTRA_ALARMS_AFTER") + " candidate pairs, as "
         "evidence that it works. That would report a rate against a ground "
         "truth defined by the detector's own threshold, which measures "
         "agreement rather than precision."),
        ("The right conclusion is that this corpus does not contain the "
         "phenomenon the mechanism detects, ", "so the mechanism is unproven "
         "rather than disproven."),
    ], size=14.5, bsize=12)
    deck.card(s, 4.77, 2.02, 3.87, 3.40, "The reranker does not help on the "
             "focus corpus", [
        ("A component that helps on one corpus and not on another is not a "
         "component that helps. ", "It is reported with its corpus "
         "attached, and the sentence is never used without it."),
    ], size=14.5, bsize=12)
    deck.card(s, 8.82, 2.02, 3.79, 3.40, "The gate does not reject malformed "
             "questions", [
        ("It is good at asking whether there is evidence here, ", "and of no "
         "use at asking whether this is even a question."),
        ("A separate runtime form validator exists because that question "
         "needs a different instrument. ", "The gate is never credited with "
         "the validator's work."),
    ], size=14.5, bsize=12)
    deck.takeaway(s, "Why these are reported",
                  "A negative result that is stated plainly is worth more to "
                  "the next person than a positive one that was "
                  "overstated.")
    deck.notes(s, "Do not rush these. A committee that reads a report with "
                  "its negative results still present trusts the rest of it.")

    s = deck.slide("Threats to validity",
                   "Five, and each of them is a reason a reader might not "
                   "accept a result at face value.")
    rows = [
        ["The generator", "One generator behind five arms settles the "
         "hypothesis for one model. A single-model null could not have "
         "supported a general claim, and a single-model positive result does "
         "not either."],
        ["The corpus", "Every measurement runs on industrial-engineering "
         "encyclopaedic text, not procedural documentation. The prior "
         "industrial work uses authentic regulatory and manual documents, and "
         "a reviewer is right to note that the two are not the same thing."],
        ["The answer labels", "The benchmark's answer-side accuracy was "
         "depressed by a defect until it was found and repaired. The gold "
         "chunk was always correct, so the retrieval-side measurements were "
         "never affected."],
        ["The annotators", "Precision was measured against two model-based "
         "annotators rather than people. They do not share a model, both read "
         "the sheet blind, and both scored 14 of 14 on a control set."],
        ["Statistical power", "Several of the results reported as nulls are "
         "nulls of this corpus at this size. The bootstrap intervals are "
         "reported next to the point estimates so a reader can see the "
         "width."],
    ]
    deck.table(s, ML, 2.02, CW, ["Threat", "What it means for the claims"],
               rows, col_widths=[0.17, 0.83], size=11.5, head_size=10.5,
               row_h=0.66, head_h=0.32, bold_first=True)
    deck.takeaway(s, "The honest summary",
                  "The strongest claims are the ones that survive the "
                  "narrowest reading of the corpus, the single generator and "
                  "the sample size.")
    deck.notes(s, "The last row is the one a statistical examiner will probe. "
                  "The answer is that the interval widths are published.")

    s = deck.slide("What this changes for practice",
                   "Four things for somebody who has to decide whether to "
                   "deploy a gate.")
    deck.bullets(s, ML, 2.02, CW, [
        ("Calibrate the gate and measure it. ", "Do not pick a threshold by "
         "hand. The sweep is a frontier rather than a cliff, and the "
         "operating point has to be chosen against a stated cost of coverage."),
        ("Evaluate the gate against a random-refusal control. ", "Without "
         "one, an implementation that refuses on a coin flip and one that "
         "refuses on a calibrated confidence score look identical on the "
         "metric that is easiest to report."),
        ("Audit the benchmark's own shortcuts before trusting the headline. ",
         "The difference between " + t("UNANS_BEFORE_REFUSED_PCT") + " and "
         + t("UNANS_HARD_REFUSED_PCT") + " is not a better system. It is a "
         "better benchmark, and it took a repair to see it."),
        ("Put the gate upstream of generation. ", "A generator that declines "
         "on its own costs a model call. A generator that returns nothing "
         "costs a model call and produces nothing. On the questions the gate "
         "rejects, the framework spends nothing."),
    ], size=13.5, gap=15)
    deck.takeaway(s, "The second one",
                  "The random-refusal control is the cheapest and the most "
                  "missing experiment in this area of work.")
    deck.notes(s, "These four sentences are the practical output. The second "
                  "is the one to underline.")

    s = deck.slide("The limitations",
                   "Eight, and the first is the largest gap in the work.")
    rows = [
        ["L1", "One generator", "The replication on a second generator could "
         "not be run, because that model returned no text on "
         + t("GENCOMP_FAILING_EMPTY_N") + " of "
         + t("GENCOMP_FAILING_EMPTY_TOTAL") + " questions. The hypothesis is "
         "supported for the generator tested, not in general."],
        ["L2", "An encyclopaedic corpus, not a procedural one",
         "The public corpus does not contain the instance records, "
         "specification tables or calibration logs a production deployment "
         "would query."],
        ["L3", "The long-context quality half was measured on one corpus",
         "The cross-category corpus is " + t("MC_LC_CORPUS_TOKENS") +
         " tokens, " + t("MC_LC_CORPUS_VS_128K") + " times the 128K window, so "
         "the whole-corpus arm could not be run there."],
        ["L4", "The annotation behind the contradiction precision is "
         "model-based", "Two annotators that do not share a model, blind to "
         "the detector's scores, and correct on a control set, but not human "
         "readers."],
        ["L5", "Statistical power", "The quota-placement comparison and the "
         "fusion-over-BM25 comparison are nulls at this sample size on these "
         "corpora, and are read as no difference established here."],
        ["L6", "The scope of the generator's own abstention",
         "The measured effect is on the rate of answering unanswerable "
         "questions. On generated text the hallucination rate is a different "
         "quantity, computed by a different instrument."],
        ["L7", "A refusal is not an answer", "The gate reduces the "
         "opportunity for a hallucinated answer by declining. It does not "
         "make the answers it does give more correct."],
        ["L8", "English and one jurisdiction", "The corpora are English, and "
         "the industrial corpus is United States federal regulation. Nothing "
         "here shows the decomposition holds elsewhere."],
    ]
    deck.table(s, ML, 2.02, CW, ["", "Limitation", "What it restricts"],
               rows, col_widths=[0.04, 0.27, 0.69], size=10.5, head_size=10,
               row_h=0.44, head_h=0.30, bold_first=True)
    deck.notes(s, "L1 is the largest gap. Say so before it is pointed at.")

    s = deck.slide("The conclusion",
                   "What the work establishes, and the three qualifications "
                   "that are the most useful part of it.")
    deck.prose(s, ML, 2.02, 6.55, 1.70, [
        ("The framework's own hypothesis, that a code-level and "
         "non-bypassable gate lowers the rate of answering unanswerable "
         "questions, is supported under both prompt conditions. ", "Under a "
         "prompt that requires an answer, the fitted gate reduces the rate "
         "from " + t("GEN_A_NOGATE_UNANS_ANSWER_RATE") + " to "
         + t("GEN_A_FITTED_UNANS_ANSWER_RATE") + ", with a paired exact "
         "McNemar test at p = " + t("GEN_PAIRED_FITTED_UNANS_P") + "."),
    ], size=13, gap=8)
    rows = [
        ["1", "The confidence score buys refusal precision, not a lower "
         "answer rate", "The gate spends " + t("GEN_PAIRED_FITTED_ANS_B") +
         " refusals on answerable questions; the control spends " +
         t("GEN_PAIRED_RANDOM_ANS_B") + "."],
        ["2", "The benchmark's shortcut was worth more than the system",
         "The headline " + t("UNANS_BEFORE_REFUSED_PCT") + " was an upper "
         "bound on a benchmark artefact. After the repair the rate is " +
         t("UNANS_HARD_REFUSED_PCT") + "."],
        ["3", "One mechanism did not survive measurement",
         "The contradiction gate's precision against reader labels is " +
         t("CONTRA_PRECISION_PCT") + ", with a 95 percent upper bound of " +
         t("CONTRA_PRECISION_CI_HI") + ". It is reported as unproven."],
    ]
    deck.table(s, ML, 3.92, CW, ["", "The three qualifications",
                                  "The evidence"],
               rows, col_widths=[0.04, 0.38, 0.58], size=11.5,
               head_size=10, row_h=0.74, head_h=0.30, bold_first=True)
    deck.takeaway(s, "The closing point",
                  "The most useful thing here was finding that two of its "
                  "own instruments were reporting numbers a careful reader "
                  "could not trust, and changing the headline rather than "
                  "explaining it away.")
    deck.notes(s, "The closing point is the one to land. A framework's "
                  "contribution is only as good as the instruments that "
                  "measured it.")

    s = deck.slide("The future work",
                   "Listed in the order in which they would change what the "
                   "claims can say.")
    rows = [
        ["1", "Repeat the generator-side comparison on a generator that "
         "returns text on the table questions",
         "One generator settles the hypothesis once. The replication was "
         "attempted and could not be run."],
        ["2", "Compare the gate against a token-level faithfulness monitor",
         "The gate is measured against a prompt-level control and against the "
         "always-flag and never-flag baselines, but not against another "
         "detector of the same kind."],
        ["3", "Settle the magnitude and the power of the positional "
         "comparison", "The direction replicates in three of four "
         "measurements and ties in one. The magnitude does not."],
        ["4", "Extend the industrial corpus beyond one jurisdiction and one "
         "language", "Nothing here shows the decomposition of a detector's "
         "precision holds elsewhere."],
        ["5", "Stratify the corpus by modality",
         "So that the modality-quota objective can be tested with adequate "
         "power, under a pre-registered power analysis."],
        ["6", "Hand-check the repaired unanswerable class against the corpus, "
         "on both corpora", "The repair was validated structurally and "
         "automatically, not by hand on both corpora."],
        ["7", "Run the long-context quality arm on a corpus that fits the "
         "context window", "So that corpus's comparison is settled on "
         "quality and not only on cost."],
        ["8", "Replace the model-based contradiction annotators with human "
         "readers", "Which would strengthen the " +
         t("CONTRA_PRECISION_PCT") + " finding in either direction."],
        ["9", "Publish the corrected benchmark and the shortcut audit as a "
         "separate artefact", "So that other work on refusal can check its "
         "own benchmarks against the same instrument."],
    ]
    deck.table(s, ML, 2.02, CW, ["", "Next step", "Why it is on the list"],
               rows, col_widths=[0.04, 0.40, 0.56], size=10.5, head_size=10,
               row_h=0.44, head_h=0.30, bold_first=True)
    deck.notes(s, "Step nine is the one that outlives this defence. The "
                  "instrument is more reusable than the framework.")

    s = deck.closing_slide("Thank you", [
        "Questions",
        "An Evidence-Grounded Retrieval-Augmented Generation Framework for "
        "Industrial Decision Support",
        "Ritik Raj  |  25IM60R12  |  Department of Industrial and Systems "
        "Engineering, IIT Kharagpur",
        "Under the supervision of Dr. Sri Krishna Kumar",
    ], "Every figure in this deck comes from an archived result file, and "
       "the full text, the appendix and the benchmark are in the report.")
    deck.notes(s, "Leave this up during the questions. The pipeline picture "
                  "is a useful thing to point at when the examiner asks "
                  "where a component sits.")


# ------------------------------------------------------------- the formula
def formula_slide(*, title, kicker, latex, width, fontsize, symbols,
                  source, value, caveat, notes):
    """A slide carrying one formula: its symbols, its origin, its value.

    The layout is fixed. The formula sits in a band on the right, the symbols
    are tabled on the left, and the three prose blocks say where the formula
    came from, why its value is the value it is, and what the caveat is.
    """
    s = deck.slide(title, kicker)
    deck.rect(s, ML, 2.02, 6.10, 1.30, SURFACE)
    deck.put_formula(s, latex, ML + 0.25, 2.24, width - 0.50, max_h=0.86,
                     fontsize=fontsize, centre_w=5.60)
    deck.table(s, ML, 3.52, 6.10, ["Symbol", "What it is"], symbols,
               col_widths=[0.30, 0.70], size=10.5, head_size=10, row_h=0.28,
               head_h=0.30, bold_first=True)
    deck.block(s, 7.10, 2.02, 5.52, 1.46, "Where it comes from", source,
               size=11.5, bsize=11)
    deck.block(s, 7.10, 3.54, 5.52, 1.46, "Why this value", value,
               size=11.5, bsize=11)
    deck.block(s, 7.10, 5.06, 5.52, 1.46, "The caveat", caveat,
               size=11.5, bsize=11)
    deck.notes(s, notes)


# ------------------------------------------------------------------- build
def main() -> int:
    slide_title()
    slide_contents()
    part_objective()
    part_literature()
    part_framework()
    part_framework_slides()
    part_methodology()
    part_results()
    part_conclusion()
    deck.save(OUT)
    _monochrome(OUT, keep=(ACCENT_HEX,))
    print(f"[final mtp reference] wrote {OUT.name} "
          f"({len(deck.prs.slides._sldIdLst)} slides)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
