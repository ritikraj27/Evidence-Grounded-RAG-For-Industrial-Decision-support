#!/usr/bin/env python3
"""Add the 2026 frontier to the related work.

The direction check found substantial 2026 work that the thesis does not
engage: a calibrated NLI-plus-lexical abstention framework (HALT-RAG), a
controlled study showing prompt-based abstention fails under misleading
context (GRAB-RAG), set-level sufficiency verification (SURE-RAG) and
structural certificates (Certify), the argument that modality routing is
performed at the wrong decision point, and a controlled evaluation showing
that retrieval enhancements stop paying once a strong reranker is present.

A paper that does not cite these reads as unaware of them. This patch adds
a subsection to the technical report and a paragraph to each LaTeX paper,
and states the narrowed claim each one forces.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
T = ROOT / "deliverables" / "templates"

# --------------------------------------------------------------------------
# The technical report: a new subsection 2.7.
# --------------------------------------------------------------------------
SECTION_27 = """
### 2.7 What changed in 2026, and what it forces us to narrow

Three developments between the framework's specification and this writing bear
directly on our claims, and we state them here rather than leaving a reader to
find them.

**The abstention mechanism has moved past a threshold.** GRAB-RAG
(arXiv:2608.22228) shows that under explicit abstention prompting models still
answer 41.6% of *misleading* questions, with 63% of those answers echoing the
planted wrong entity; the paper's contribution is not that a threshold exists but
that a threshold is insufficient. SURE-RAG (arXiv:2605.03534) argues that
sufficiency is a *set-level* property that independent passage scoring cannot
detect, and Certify (arXiv:2610.34684) makes it structural, deriving a
Horn-closure certificate from a per-query requirement hypergraph. Sieve and Sage
(arXiv:2609.35794) screens the retrieved set in a lightweight module *outside*
the model before the model is invoked, with a two-state failure decomposition
(unanswerable versus distracted); AGO (arXiv:2610.01218) quantifies
regression risk probabilistically. The consequence for us is narrow and we accept
it: our gate is a **calibrated answer-in-context detector with a stated
operating point**, not a sufficiency judge, and the literature reserves
"sufficiency" for the set-level property. Section 4.4 reports the contingency
table that makes the distinction concrete.

**The closest single pre-emption of our contradiction mechanism is published.**
HALT-RAG (arXiv:2509.07475) is a task-adaptable framework that combines an
ensemble of NLI models with lexical signals, feeds them to a calibrated
meta-classifier, and deploys it under a precision-constrained abstention
policy — functionally the union of our D1 and D4. Kontrast
(arXiv:2607.25959) separates direct conflicts from information-granularity
differences, temporal changes and incompleteness, which is our supersession
check formalised. WIKICOLLIDE (arXiv:2509.23233) reports that at least 3.3% of
English Wikipedia facts contradict another fact — which is both a reason our
corpus is a reasonable object of study and a benchmark we should have used.
Our remaining D4 claim is therefore an *industrial instantiation* in which the
numeric detector is independent of the NLI verifier and the supersession check
is explicit, and it can only be defended against human labels, which we do not
have and say so.

**Retrieval enhancements stop paying once a strong reranker is present.**
Beyond the Reranker (arXiv:2606.28367) evaluates eight enhancement methods on a
heterogeneous corpus and reports that only query expansion and one calibrated
method give reliable gains beyond a strong reranker; its framing sentence is
aimed at work like ours, noting that reported gains "come almost exclusively
from homogeneous corpora, predominantly Wikipedia prose." Ours is exactly such
a corpus, so the effect sizes we measure should be read as an upper bound on
what the same mechanisms would deliver on mixed-format industrial documents.
FreshStack (arXiv:2504.13128) independently reports rerankers that fail to
improve first-stage retrieval on two of five technical topics, and T²-RAGBench
(EACL 2026, arXiv:2506.12071) finds hybrid BM25 most effective on text-and-table
data. We therefore report the candidate-pool curve (Section 5) as our
contribution in this area and treat the pipeline itself as the instrument
rather than the result.

Two further threats belong with these. The Labeling Problem in Hallucination
Detection Benchmarks (NeurIPS 2026 Evaluations and Datasets Track,
arXiv:2610.08026) shows with 900 human-labelled pairs that automated labelers
systematically conflate reference faithfulness with factual correctness — a
direct constraint on our silver-standard labels. Entropy Alone is Insufficient
for Safe Selective Prediction in LLMs (arXiv:2603.21172) bears on our
information-gain component. And Detecting Is Not Resolving
(arXiv:2605.27157) reports across more than 50,000 turn-level evaluations that
models acknowledge contradictory evidence without constraining their
recommendations — the monitoring-control gap, which is why we treat
contradiction *surfacing* as a reporting mechanism rather than a resolution
mechanism.
"""

ANCHOR_26 = """We also correct the following bibliographic errors found in the project's own proposal and earlier report:"""

# --------------------------------------------------------------------------
# The IEEE paper: a paragraph in the related work.
# --------------------------------------------------------------------------
IEEE_PARAGRAPH = """
\\paragraph{What changed in 2026, and what it forces us to narrow.}
Three developments bear directly on our claims. First, the abstention mechanism
has moved past a threshold: GRAB-RAG (arXiv:2608.22228) shows models still
answer \\emph{41.6\\%} of misleading questions under explicit abstention
prompting, SURE-RAG (arXiv:2605.03534) argues sufficiency is a set-level
property that independent passage scoring cannot detect, Certify
(arXiv:2610.34684) makes it structural, and Sieve and Sage
(arXiv:2609.35794) screens the retrieved set outside the model before the
model is invoked. Our gate is consequently a calibrated \\emph{answer-in-context
detector}, not a sufficiency judge, and we report the contingency table that
makes the distinction concrete. Second, the closest single pre-emption of our
contradiction mechanism is published: HALT-RAG (arXiv:2509.07475) combines a
calibrated NLI ensemble with lexical signals under a precision-constrained
abstention policy, and Kontrast (arXiv:2607.25959) formalises the
temporal-change distinction we implement as a supersession check. Our remaining
D4 claim is an industrial instantiation with an NLI-independent numeric
detector, which can only be defended against human labels that we do not have.
Third, Beyond the Reranker (arXiv:2606.28367) reports that retrieval
enhancements stop paying once a strong reranker is present, and notes that
reported gains come almost exclusively from homogeneous corpora, predominantly
Wikipedia prose --- which ours is; our effect sizes should therefore be read as
an upper bound for mixed-format industrial documents. We report the
candidate-pool curve as our contribution in this area and treat the pipeline as
the instrument rather than the result.
"""

# --------------------------------------------------------------------------
# The journal paper: a paragraph in the related work.
# --------------------------------------------------------------------------
JOURNAL_PARAGRAPH = """
\\paragraph{What changed in 2026, and what it forces us to narrow.}
The abstention mechanism has moved past a threshold. GRAB-RAG
(arXiv:2608.22228) reports that models still answer 41.6\\% of misleading
questions under explicit abstention prompting; SURE-RAG (arXiv:2605.03534)
argues that sufficiency is a set-level property that independent passage
scoring cannot detect; Certify (arXiv:2610.34684) makes it structural; and
Sieve and Sage (arXiv:2609.35794) screens the retrieved set in a module outside
the model before the model is invoked. Our gate is consequently a calibrated
\\emph{answer-in-context detector} rather than a sufficiency judge, and we
report the contingency table that makes the distinction concrete. The closest
single pre-emption of our contradiction mechanism is published: HALT-RAG
(arXiv:2509.07475) combines a calibrated NLI ensemble with lexical signals
under a precision-constrained abstention policy, while Kontrast
(arXiv:2607.25959) formalises the temporal-change distinction we implement as
a supersession check; our remaining claim is an industrial instantiation with
an NLI-independent numeric detector, which only human labels could defend.
Finally, Beyond the Reranker (arXiv:2606.28367) reports that retrieval
enhancements stop paying once a strong reranker is present, and that reported
gains come almost exclusively from homogeneous corpora, predominantly Wikipedia
prose --- which ours is, so our effect sizes are an upper bound for mixed-format
industrial documents. The Labeling Problem in Hallucination Detection
Benchmarks (arXiv:2610.08026) further constrains our silver-standard labels,
showing that automated labelers conflate reference faithfulness with factual
correctness.
"""


def apply(path: Path, edits):
    if not path.exists():
        print(f"!! missing {path}")
        return 0
    s = path.read_text(encoding="utf-8")
    n = 0
    for old, new in edits:
        c = s.count(old)
        if c != 1:
            print(f"!! {path.name}: count={c} -> {old[:60]!r}")
            continue
        s = s.replace(old, new, 1)
        n += 1
    path.write_text(s, encoding="utf-8")
    return n


def main() -> int:
    total = 0
    total += apply(T / "Deliverable_2a_Technical_Report.md", [
        (ANCHOR_26, SECTION_27.strip() + "\n\n" + ANCHOR_26),
    ])
    total += apply(T / "Deliverable_2b_IEEE_Conference_Paper.tex", [
        ("\\subsection{Positioning summary}", IEEE_PARAGRAPH.strip()
         + "\n\n\\subsection{Positioning summary}"),
    ])
    total += apply(T / "Deliverable_2c_Journal_Style_Paper.tex", [
        ("\\subsection{Positioning summary}", JOURNAL_PARAGRAPH.strip()
         + "\n\n\\subsection{Positioning summary}"),
    ])
    print(f"\n{total} replacements applied")
    return 0


if __name__ == "__main__":
    sys.exit(main())
