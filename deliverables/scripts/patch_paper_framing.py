#!/usr/bin/env python3
"""Reframe the paper's contribution around what the evidence supports.

The direction check's verdict was that the thesis was aimed at the weakest
version of itself: it presented an architecture whose components are all
published, and the *measurements* — several of them negative — as a
secondary result. The measurements are the contribution. This patch:

  * rewrites the contribution statement to say so, and lists the prior art
    that pre-empts each architectural claim;
  * narrows the positioning table, which had claimed D4 had "no published
    equivalent";
  * adds the label correction (the gate detects answer-in-context, not
    evidence sufficiency) where the protocol is stated;
  * adds the corpus characterisation to the abstract, because the corpus is
    encyclopaedic industrial-engineering text rather than the operating
    documents a practitioner uses;
  * adds the threats the direction check identified.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
T = ROOT / "deliverables" / "templates"

# --------------------------------------------------------------------------
# 1. The technical report: the contribution statement.
# --------------------------------------------------------------------------
OLD_CONTRIB = """We propose a framework with five mechanisms and evaluate it. We state the contribution in three parts, because they differ in strength.

**Architectural — incremental.** The five mechanisms have published prior art. We position ours against that prior art explicitly (Section 2) rather than claiming priority. Our architectural contribution is a particular *arrangement* and, more substantively, two properties of that arrangement: the confidence gate is a control-flow fact rather than an instruction, and the conflict report is type-aware rather than binary.

**Empirical — a failure-mode characterisation.** Our substantive contribution is what the measurements show, including two results that contradict the framework's original specification: the pipeline position at which a modality quota actually binds, and the no-op behaviour of a filter applied to only one retrieval leg. We reproduce, on an independent corpus, the cross-encoder recall regression reported in an earlier project report on a different corpus.

**Methodological — an evaluation protocol.** We evaluate the confidence gate as a selective-prediction policy with a risk–coverage curve and a false-positive rate at a stated operating point, with always-flag and never-flag baselines. This follows recent findings that filter results reported without these quantities are uninterpretable (Section 2.4)."""

NEW_CONTRIB = """We measure which reliability mechanisms pay for themselves in industrial text, and report where they break. We state the contribution in three parts, and we state them in that order deliberately: the measurement is the contribution, not the architecture.

**Architectural — incremental, and treated as such.** Every one of the five mechanisms has published prior art, and by late 2026 the closest of them are close enough that the architecture cannot be the argument. A code-level, pre-generation gate with a calibrated, task-adapted decision policy is published (Sieve and Sage, EMNLP 2026 Findings; BITEM, NTCIR-19; HALT-RAG); set-level sufficiency verification and structural certificates are published (SURE-RAG; Certify); a calibrated NLI ensemble combined with lexical signals under a precision-constrained abstention policy is published (HALT-RAG); the argument that modality routing is performed at the wrong decision point is published in the modality-RAG literature (Modality Relevance is not Modality Utility); and the claim that retrieval enhancements stop paying once a strong reranker is present is published on heterogeneous corpora (Beyond the Reranker). We position ours against that prior art explicitly (Section 2) rather than claiming priority. The one architectural property we hold is that the gate is a control-flow fact rather than an instruction.

**Empirical — a failure-mode characterisation, mostly of negative results.** Our substantive contribution is what the measurements show, and several of them contradict the framework's original specification and one contradicts the direction the field has been moving. The modality quota is a trade and not a gain, and its pipeline position decides what it costs. The dense leg is not merely weaker than the lexical leg: on a corpus whose questions are derived from the documents themselves, fusing it in can cost recall. The confidence gate cannot separate "there is no evidence here" from "the evidence is here and the retriever missed it", because the retrieval scores it uses cannot; it is therefore an answer-in-context detector, and Section 4.4 reports the contingency table that says so rather than a base rate alone. And a reranker's effect on recall is governed by its candidate pool rather than by the reranker.

**Methodological — an evaluation protocol.** We evaluate the confidence gate as a selective-prediction policy with a risk–coverage curve, a false-positive rate at a stated operating point, and the two degenerate policies — never refuse and always refuse — as baselines, rather than the endpoints of the threshold sweep, which are not baselines. We report the label's contingency table rather than a base rate alone. We separate the components of a compound detector, so that a recall which is true by construction cannot be presented as a result. This follows recent findings that filter results reported without these quantities are uninterpretable (Section 2.4), and that automated labelers conflate reference faithfulness with factual correctness (Section 2.7)."""

# --------------------------------------------------------------------------
# 2. The positioning table: D4 is no longer "no published equivalent".
# --------------------------------------------------------------------------
OLD_POSITION = """| Contradiction surfacing | **No published equivalent** | Type-aware conflict report; the strongest surviving novelty. |"""

NEW_POSITION = """| Contradiction surfacing | HALT-RAG (arXiv:2509.07475); Kontrast (arXiv:2607.25959); Financial Evidence Crowding (arXiv:2609.35782); HCF (arXiv:2609.07075); WIKICOLLIDE (arXiv:2509.23233) | An industrial instantiation in which the numeric detector is independent of the NLI verifier and the supersession check is explicit. The conjunction is not published; each conjunct is. |"""

OLD_POSITION_HYBRID = """| Hybrid retrieval | Cormack et al. 2009; Bruch et al. 2023; BEIR | A replication and a clarification of what fusion and reranking each buy. Not priority. |"""

NEW_POSITION_HYBRID = """| Hybrid retrieval | Cormack et al. 2009; Bruch et al. 2023; BEIR; Beyond the Reranker (arXiv:2606.28367); T²-RAGBench (EACL 2026); FreshStack (NeurIPS 2025) | A replication and a clarification of what fusion and reranking each buy, plus the candidate-pool curve, which we find is unpublished. Not priority. |"""

# --------------------------------------------------------------------------
# 3. The label correction, in the evaluation protocol.
# --------------------------------------------------------------------------
OLD_LABEL = """Crucially, the benchmark contains a family of **deliberately unanswerable questions** on topics absent from the corpus. Without them, no confidence-gating experiment is meaningful: a system that answers everything scores 100% recall and 0% hallucination."""

NEW_LABEL = """Crucially, the benchmark contains a family of **deliberately unanswerable questions** on topics absent from the corpus. Without them, no confidence-gating experiment is meaningful: a system that answers everything scores 100% recall and 0% hallucination.

**What the gate's label actually is, stated exactly.** The gate is calibrated on a query-level label that is 1 iff the gold chunk is present in the reranked candidate pool. That is an *answer-in-context* label, not an evidence-sufficiency label: the literature reserves "sufficiency" for a set-level property, where scoring passages independently cannot detect it. The consequence is important and we state it rather than hide it. The negative class is dominated by **retrieval failure** — an answerable question whose evidence the retriever missed — and not by absence of evidence. The gate therefore detects whether the answer is in the context, and cannot distinguish "there is no evidence here" from "the evidence is here and the retriever missed it". Section 4.4 reports the full contingency table: the number of answerable questions whose evidence was found, the number whose evidence was missed, and the number of unanswerable questions. Every claim about the gate in this paper should be read against that decomposition."""

# --------------------------------------------------------------------------
# 4. The corpus characterisation, in the abstract.
# --------------------------------------------------------------------------
OLD_ABSTRACT_TAIL = """We also show that the modality composition of the corpus, rather than the retrieval algorithm, determines whether a modality-aware mechanism can have any effect at all — a null result that is the expected outcome on a text-heavy corpus and is, we argue, under-reported in the literature."""

NEW_ABSTRACT_TAIL = """We also show that the modality composition of the corpus, rather than the retrieval algorithm, determines whether a modality-aware mechanism can have any effect at all — a null result that is the expected outcome on a text-heavy corpus and is, we argue, under-reported in the literature. We are explicit about what our corpus is: industrial-engineering *encyclopaedic* text drawn from English Wikipedia under CC BY-SA 4.0, shipped in full with per-document provenance, and not the operating manuals, control plans and supplier specifications a practitioner actually uses. Claims that depend on such documents are not made."""


def apply(path: Path, edits):
    if not path.exists():
        print(f"!! missing {path}")
        return 0
    s = path.read_text(encoding="utf-8")
    n = 0
    for old, new in edits:
        c = s.count(old)
        if c != 1:
            print(f"!! {path.name}: count={c} -> {old[:64]!r}")
            continue
        s = s.replace(old, new, 1)
        n += 1
    path.write_text(s, encoding="utf-8")
    return n


def main() -> int:
    total = 0
    total += apply(T / "Deliverable_2a_Technical_Report.md", [
        (OLD_CONTRIB, NEW_CONTRIB),
        (OLD_POSITION, NEW_POSITION),
        (OLD_POSITION_HYBRID, NEW_POSITION_HYBRID),
        (OLD_LABEL, NEW_LABEL),
        (OLD_ABSTRACT_TAIL, NEW_ABSTRACT_TAIL),
    ])
    print(f"\n{total} replacements applied")
    return 0


if __name__ == "__main__":
    sys.exit(main())
