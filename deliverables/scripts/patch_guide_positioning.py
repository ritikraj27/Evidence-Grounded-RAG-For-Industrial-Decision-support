#!/usr/bin/env python3
"""Correct the guide's positioning statement and add the 2026 frontier.

F.4 claimed that the type-aware conflict report had "no published
equivalent". The direction check found the closest single pre-emption:
HALT-RAG (arXiv:2509.07475), which combines a calibrated NLI ensemble with
lexical signals under a precision-constrained abstention policy — the union of
D1 and D4. The claim is narrowed, the empirical summary is updated to the
measurements, and F.7 states the three 2026 developments that force the
narrowing.

The guide's Part H gains the corresponding limitations, and Part G gains the
two viva questions these changes create.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
T = ROOT / "deliverables" / "templates"

F4_OLD = """Our contribution is different in kind: a **code-level,
non-bypassable** gate that produces an auditable refusal, is portable across
twelve industrial categories without retraining, and exposes per-claim
confidence bands — and, in the contradiction-surfacing component, a
**type-aware** conflict report for which no published equivalent exists.
Our headline empirical contribution is not the architecture but the
**failure-mode characterisation**: we show, on an independent corpus, that
reranking improves ordering while degrading recall, that a modality quota only
binds when applied after the reranker, and that the modality composition of the
corpus — not the algorithm — determines whether a modality-aware mechanism can
have any effect at all."""

F4_NEW = """Our contribution is different in kind: a **code-level,
non-bypassable** gate that produces an auditable refusal, and, in the
contradiction-surfacing component, a **type-aware** conflict report in which the
numeric detector is independent of the NLI verifier and the supersession check
is explicit. The conjunction itself is not published, but every conjunct is —
HALT-RAG (arXiv:2509.07475) publishes a calibrated NLI ensemble with lexical
signals under a precision-constrained abstention policy, which is functionally
the union of our D1 and D4, and Kontrast (arXiv:2607.25959) formalises the
temporal-change distinction we implement as a supersession check. **We do not
claim the contradiction gate is new.** We claim it is a carefully instantiated
one, and that we report what it costs rather than only what it catches.

Our headline empirical contribution is not the architecture but the
**failure-mode characterisation**, and it is mostly negative. We show, on an
independent corpus, that a modality quota is a **trade and not a gain**, and that
its pipeline position decides what it costs; that a reranker's effect on recall
is governed by its **candidate pool** rather than by the reranker; that the
modality composition of the corpus — not the algorithm — determines whether a
modality-aware mechanism can have any effect at all; and that the confidence
gate **cannot separate "there is no evidence here" from "the evidence is here
and the retriever missed it"**, because the retrieval scores it uses cannot.
That last one is a negative result about our own mechanism, and it is the one
we expect a committee to press on, so we state it before they do."""

F5_OLD = """- ❌ "SupplyChainQA is a public benchmark." It is our own unreleased construction;
  the report itself lists the Zenodo release as future work."""

F5_NEW = """- ❌ "SupplyChainQA is a public benchmark." It is our own unreleased construction;
  the report itself lists the Zenodo release as future work.
- ❌ "Our contradiction gate has no published equivalent." HALT-RAG
  (arXiv:2509.07475) is functionally the union of D1 and D4; Kontrast
  (arXiv:2607.25959) publishes the conflict taxonomy we implement. Narrow
  the claim to the *industrial instantiation with an NLI-independent numeric
  detector*.
- ❌ "Our gate judges evidence sufficiency." It does not. The label is
  answer-in-context detectability, and the literature reserves "sufficiency"
  for the set-level property (SURE-RAG, arXiv:2605.03534; Certify,
  arXiv:2610.34684). Say "the gate detects whether the answer is in the
  retrieved context".
- ❌ "Our gate catches unanswerable questions." Report the rate at a stated
  operating point against the *never-refuse* and *always-refuse* policies. The
  endpoints of a threshold sweep are not baselines.
- ❌ "Our results transfer to industrial practice." The corpus is
  industrial-engineering *encyclopaedic* text. Beyond the Reranker
  (arXiv:2606.28367) reports that retrieval-enhancement gains come almost
  exclusively from homogeneous corpora, predominantly Wikipedia prose, which
  ours is. State the upper bound rather than the generalisation.
- ❌ "Our contradiction gate recalls 100% of verifiable conflicts." That number
  is true by construction: the verifiable subset is *defined* by numeric
  conflicts and the numeric detector is an OR-branch of the gate. Report what
  the NLI-and-same-subject conjunction catches on its own."""

F7 = """
## F.7 What changed in 2026, and what it forces us to narrow

Three developments between the framework's specification and this writing bear
directly on our claims. This subsection exists so that nobody discovers them in
the room.

**The abstention mechanism has moved past a threshold.** GRAB-RAG
(arXiv:2608.22228) shows that under explicit abstention prompting, models still
answer 41.6% of *misleading* questions, with 63% of those answers echoing the
planted wrong entity; the paper's contribution is not that a threshold exists
but that a threshold is insufficient. SURE-RAG (arXiv:2605.03534) argues that
sufficiency is a *set-level* property that independent passage scoring cannot
detect, and Certify (arXiv:2610.34684) makes it structural, deriving a
Horn-closure certificate from a per-query requirement hypergraph. Sieve and
Sage (arXiv:2609.35794) screens the retrieved set in a lightweight module
*outside* the model before the model is invoked, with a two-state failure
decomposition — unanswerable versus distracted. AGO (arXiv:2610.01218)
quantifies regression risk probabilistically instead of thresholding.

**What this forces on us.** Our gate is a **calibrated answer-in-context
detector with a stated operating point**, not a sufficiency judge, and the
literature reserves "sufficiency" for the set-level property. Part E reports
the contingency table that makes the distinction concrete: how many answerable
questions had their evidence found, how many had it missed, and how many were
unanswerable. The negative class is dominated by *retrieval failure*, and a
reviewer who reads the code will see that in five minutes.

**The closest single pre-emption of our contradiction mechanism is published.**
HALT-RAG (arXiv:2509.07475) is task-adaptable: an ensemble of NLI models
combined with lexical signals, fed to a calibrated meta-classifier, deployed
under a precision-constrained abstention policy — functionally the union of D1
and D4. Kontrast (arXiv:2607.25959) separates direct conflicts from
information-granularity differences, temporal changes and incompleteness, which
is our supersession check formalised. WIKICOLLIDE (arXiv:2509.23233) reports
that at least 3.3% of English Wikipedia facts contradict another fact — which is
both a reason our corpus is a reasonable object of study and a benchmark we
should have used.

**What this forces on us.** Our remaining D4 claim is an *industrial
instantiation* in which the numeric detector is independent of the NLI verifier
and the supersession check is explicit, and that can only be defended against
human labels, which we do not have. We say so.

**Retrieval enhancements stop paying once a strong reranker is present.**
Beyond the Reranker (arXiv:2606.28367) evaluates eight enhancement methods on a
heterogeneous corpus with chunker-agnostic relevance labels and
collection-disjoint splits, and finds that only query expansion and one
calibrated method give reliable gains beyond a strong reranker. Its framing
sentence is aimed at work like ours: the reported gains "come almost entirely
from homogeneous corpora, predominantly Wikipedia prose." Ours is exactly such a
corpus. FreshStack (arXiv:2504.13128) independently reports rerankers that fail
to improve first-stage retrieval on two of five technical topics, and T²-RAGBench
(EACL 2026, arXiv:2506.12071) finds hybrid BM25 most effective on text-and-table
data.

**What this forces on us.** Our effect sizes should be read as an **upper
bound** on what the same mechanisms would deliver on mixed-format industrial
documents. It also means the candidate-pool curve (Experiment 5) is the part of
this work that is most likely to be new, and it is the part that was least
discussed until now.

Two further threats belong with these. The Labeling Problem in Hallucination
Detection Benchmarks (NeurIPS 2026 Evaluations and Datasets Track,
arXiv:2610.08026) shows, with 900 human-labelled pairs, that automated labelers
systematically conflate reference faithfulness with factual correctness — a
direct constraint on our silver-standard labels, and the reason the label
standard is stated in the abstract rather than buried. Entropy Alone is
Insufficient for Safe Selective Prediction in LLMs (arXiv:2603.21172) bears on
our information-gain component. And Detecting Is Not Resolving
(arXiv:2605.27157) reports across more than 50,000 turn-level evaluations that
models acknowledge contradictory evidence without constraining their
recommendations — the monitoring-control gap, and the reason we treat
contradiction *surfacing* as a reporting mechanism rather than a resolution
mechanism.

**The benchmark landscape has moved too.** Expert-annotated industrial and
supply-chain benchmarks now exist: the manufacturing-safety benchmark of
arXiv:2511.11847 (24 RAG configurations in a full-factorial design, top two
reviewed by ten industry experts and academics), arXiv:2606.20898 (972
expert-validated answers, comparing RAG against long-context prompting),
arXiv:2603.20534 (669 requirements across four MBN standards plus 49 supplier
qualifications, with expert quality assessment), RealDocBench
(arXiv:2606.07401, which includes supply-chain logistics), and SupChain-Bench
(10.18653/v1/2026.findings-acl.371, peer-reviewed at Findings of ACL 2026). Our
residual claim — that no public benchmark spans multiple industrial-engineering
sub-domains *with dual expert annotation, a reported κ, per-claim attribution
labels, and a deliberate unanswerable class* — has to be stated in exactly those
terms or not at all. Note also that all six of our categories are
industrial-engineering sub-domains, so our transfer experiment is an
**intra-domain** transfer study, and the proposal's wording should be read that
way.
"""

Q_VIVA_1 = """**Q3c. Your gate is calibrated on a label that is really "did the retriever
find the answer". Isn't that a retrieval-success detector, not a sufficiency
judge?**
Yes, and I now say so explicitly rather than defending the old name. The label
is 1 iff the gold chunk is in the reranked candidate pool. The literature
reserves "sufficiency" for a set-level property — that scoring passages
independently cannot detect sufficiency, which is the argument of SURE-RAG
(arXiv:2605.03534) and Certify (arXiv:2610.34684) — so calling my label
"sufficiency" reads as a claim of prior art I do not have. The honest name is
**answer-in-context detectability**.

The consequence is the important part, and it is a limitation rather than a
rhetorical point. The negative class is dominated by *retrieval failure*: an
answerable question whose evidence the retriever missed. Part E reports the
three-way decomposition — answerable-and-found, answerable-and-missed, and
unanswerable — so you can see exactly how much of the negative class is
retrieval failure. A gate built on these scores cannot distinguish "there is no
evidence here" from "the evidence is here and the retriever missed it", because
the scores it uses are exactly the scores that failed. That is a limitation of
the approach, it is the field's known result for prompt- and model-based
abstention too (GRAB-RAG, arXiv:2608.22228, finds models still answer 41.6% of
misleading questions), and it is why I present the gate as a selective-prediction
policy with a risk–coverage curve rather than as a detector.

**Q3d. What has changed in the literature since you designed this, and does it
change what you are claiming?**
Three things, and yes, they narrowed the claims. First, the abstention
mechanism has moved past a threshold: GRAB-RAG, SURE-RAG, Certify and Sieve and
Sage all argue that a threshold is insufficient, and I have stopped calling my
gate a sufficiency judge for the reason in Q3c. Second, HALT-RAG
(arXiv:2509.07475) is functionally the union of my D1 and D4 — a calibrated NLI
ensemble with lexical signals under a precision-constrained abstention policy —
so I no longer claim the contradiction gate is new; I claim it is a carefully
instantiated one whose numeric detector is independent of the NLI verifier.
Third, Beyond the Reranker (arXiv:2606.28367) reports that retrieval
enhancements stop paying once a strong reranker is present, and that the
reported gains come almost exclusively from homogeneous corpora, predominantly
Wikipedia prose. Mine is exactly such a corpus, so I report my effect sizes as
an upper bound for mixed-format industrial documents. What survives unchanged is
the measurement work: the candidate-pool curve, the quota's position-versus-cost
trade, and the three-way decomposition of the gate's own label.

"""

Q_ANCHOR = """**Q4. Why not conformal prediction? It has actual guarantees.**"""


def apply(path: Path, edits):
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
    p = T / "Deliverable_1_PartF_toJ.md"
    total = 0
    total += apply(p, [(F4_OLD, F4_NEW), (F5_OLD, F5_NEW),
                       (Q_ANCHOR, Q_VIVA_1 + Q_ANCHOR)])
    # F.7 goes at the end of the literature part, before Part G.
    s = p.read_text(encoding="utf-8")
    anchor = "\n# Part G — Anticipated viva questions"
    if anchor in s and "## F.7 What changed in 2026" not in s:
        s = s.replace(anchor, F7 + anchor, 1)
        p.write_text(s, encoding="utf-8")
        total += 1
        print("  added F.7")
    print(f"\n{total} replacements applied")
    return 0


if __name__ == "__main__":
    sys.exit(main())
