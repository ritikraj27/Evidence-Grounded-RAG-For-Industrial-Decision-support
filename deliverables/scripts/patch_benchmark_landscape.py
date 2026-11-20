#!/usr/bin/env python3
"""Narrow the benchmark claim against the 2026 landscape, and add it to the guide.

The residual claim — that no public benchmark spans multiple
industrial-engineering sub-domains with dual expert annotation, a reported κ,
per-claim attribution labels and an unanswerable class — was defensible
against the 2025 landscape. It is not defensible against the 2026 one, which
contains expert-annotated industrial and supply-chain benchmarks. The claim is
restated to exactly what survives, and the landscape is written down so that a
panel member can see what was compared against.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
T = ROOT / "deliverables" / "templates"

REPORT_OLD = """        "No public benchmark spans multiple industrial-engineering sub-domains "
        "with dual expert annotation, reported κ, per-claim attribution labels and "
        "an unanswerable class.","""

REPORT_NEW = """        "The benchmark claim must now be stated narrowly: expert-annotated "
        "industrial and supply-chain benchmarks do exist -- the manufacturing-safety "
        "benchmark of arXiv:2511.11847, arXiv:2606.20898 (972 expert-validated "
        "answers), arXiv:2603.20534, RealDocBench (arXiv:2606.07401) and "
        "SupChain-Bench (10.18653/v1/2026.findings-acl.371) -- so what remains "
        "unavailable is a benchmark that spans multiple industrial-engineering "
        "sub-domains AND carries dual expert annotation, a reported kappa, "
        "per-claim attribution labels and a deliberate unanswerable class "
        "together.","""

PPTX_OLD = """         "And I have corrected the 'no public benchmark exists' claim to something "
         "much narrower, because the broad version is simply false.\\n\\n" """

PPTX_NEW = """         "And I have corrected the 'no public benchmark exists' claim to something "
         "much narrower, because the broad version is simply false. Expert-annotated "
         "industrial and supply-chain benchmarks exist -- the manufacturing-safety "
         "benchmark of arXiv 2511.11847, 972 expert-validated answers in "
         "arXiv 2606.20898, and SupChain-Bench at Findings of ACL 2026. What is "
         "still unavailable is a benchmark that has all four of the properties I "
         "need at once.\\n\\n" """

F8 = """
## F.8 The benchmark landscape, and what our benchmark is not

A panel member will ask what our benchmark should have been compared against.
The 2026 landscape has expert-annotated industrial and supply-chain benchmarks,
so the honest answer names them.

| Benchmark | Size | Domain | Annotation | Identifier |
|---|---|---|---|---|
| Manufacturing-safety chatbot benchmark | Expert-validated QA over 3 machines; 24 RAG configurations, full-factorial; top 2 reviewed by 10 industry experts and academics | Machine / occupational safety | Expert validation | arXiv:2511.11847 |
| Token Tax of Epistemic Accuracy | 972 answers, 3 machines, 2 SLMs, 3 grounding architectures | Manufacturing safety | Expert-validated | arXiv:2606.20898 |
| Industrial-scale RAG for requirements engineering | 669 requirements across 4 MBN standards + 49 supplier qualifications | Automotive requirements engineering | Authentic industrial documents; expert quality assessment | arXiv:2603.20534 |
| RealDocBench | 1,356 field-level QA over 581 documents incl. supply-chain logistics | Regulated real-world documents | Typed gold dictionaries; human-verified layout annotation | arXiv:2606.07401 |
| SupChain-Bench | — | Supply chain management | Peer-reviewed benchmark | 10.18653/v1/2026.findings-acl.371 |
| IndusSpec-QA | 3 industrial standard documents | Industrial standards | Ground truth from the standards | 10.18653/2026.emnlp-main.1456 |
| LakeQuest | 9,846 QA pairs, 3 domains | Enterprise/scientific data lakes | Human-validated, with modality-aware evidence pointers | arXiv:2607.12310 |
| T²-RAGBench | 23,088 triples | Real-world text-and-table | Expert-validated at 91.3% context-independence | EACL 2026, arXiv:2506.12071 |
| WIKICOLLIDE / CLAIRE | "the first benchmark of real Wikipedia inconsistencies"; ≥3.3% of English Wikipedia facts contradict another fact | Wikipedia | Human annotation + editor study | arXiv:2509.23233 |
| ExpertQA | 2,177 questions from 484 participants | Long-tail expert domains | Expert-curated questions, expert-evaluated responses, per-claim attributions | 10.18653/v1/2024.naacl-long.167 |

**What our benchmark is not.** Ours is silver-standard: labels derived
mechanically from the document. That is cheap, perfectly reproducible, and
slightly optimistic about absolute recall. It is not expert-annotated, and the
NeurIPS 2026 Evaluations and Datasets Track paper on the labelling problem in
hallucination-detection benchmarks (arXiv:2610.08026) shows, with 900
human-labelled pairs, that automated labelers systematically conflate reference
faithfulness with factual correctness — a direct constraint on what a
silver standard can be used to claim.

**The defensible claim, in full.** *No public benchmark we could find provides
all four of the properties this evaluation needs together: coverage of multiple
industrial-engineering sub-domains, dual expert annotation with a reported κ,
per-claim attribution labels, and a deliberate class of unanswerable questions.
Each property exists in isolation, and several of them — expert annotation,
supply-chain coverage, an unanswerable class — now exist in public benchmarks
that we did not use.* That is the sentence to say. The broader version is
false, and a panel member with the literature in front of them will know it.

**Two corrections to our own earlier notes, found during this check.**
ExpertQA is not arXiv:2402.15049 — that identifier resolves to an astronomy
poster; its canonical identifier is the NAACL 2024 DOI
10.18653/v1/2024.naacl-long.167, and its *published* title is "ExpertQA:
Expert-Curated Questions and Attributed Answers", not the preprint title.
T²-RAGBench's title changed between versions: the arXiv preprint is "T2-RAGBench:
Text-and-Table Benchmark for Evaluating Retrieval-Augmented Generation" and the
EACL 2026 version of record is "T2-RAGBench: Text-and-Table Aware
Retrieval-Augmented Generation".
"""


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
    total = 0
    total += apply(T / "scripts" / "make_docx.py", [(REPORT_OLD, REPORT_NEW)])
    total += apply(T / "scripts" / "make_pptx.py", [(PPTX_OLD, PPTX_NEW)])
    p = T / "Deliverable_1_PartF_toJ.md"
    s = p.read_text(encoding="utf-8")
    anchor = "\n# Part G — Anticipated viva questions"
    if anchor in s and "## F.8 The benchmark landscape" not in s:
        s = s.replace(anchor, F8 + anchor, 1)
        p.write_text(s, encoding="utf-8")
        total += 1
        print("  added F.8")
    print(f"\n{total} replacements applied")
    return 0


if __name__ == "__main__":
    sys.exit(main())
