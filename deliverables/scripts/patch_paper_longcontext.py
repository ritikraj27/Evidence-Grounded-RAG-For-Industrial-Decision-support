#!/usr/bin/env python3
"""Update the papers, the report and the deck for the long-context arm.

The long-context baseline was the largest unresolved threat. The cost half of
it is now measured, and the quality half was not run because no generator was
reachable. Every statement that said "not yet run" or "must be run" is
replaced by one that says what was measured, what was not, and what remains
open.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
T = ROOT / "deliverables" / "templates"

# --------------------------------------------------------------------------
# The technical report.
# --------------------------------------------------------------------------
PAPER_OLD = """It does not yet beat long context. The most serious threat to this work is that a 2026 study of document-grounded generation in manufacturing safety reports long-context systems ahead of semantic RAG, and another reports near-perfect performance by placing an entire 26k-token knowledge base in the prompt. On a 634-chunk corpus that baseline is feasible. We do not claim it is worse, and the corresponding experiment is the first item on our list."""

PAPER_NEW = """It does not yet beat long context, and we measure the part of that we can. The most serious threat to this work is that a 2026 study of document-grounded generation in manufacturing safety reports long-context systems ahead of semantic RAG, and another reports near-perfect performance by placing an entire 26k-token knowledge base in the prompt. Our evaluation corpus fits in a modern context window, so the baseline is feasible and we treat it as a threat rather than a formality. Experiment 7 measures the cost half: on the focus domain the corpus is {{LC_CORPUS_TOKENS}} tokens and the RAG arm's accepted context averages {{LC_RAG_TOKENS}} tokens, so the long-context arm costs {{LC_RATIO}}x more input per query; on the six-category corpus the corpus is {{MC_LC_CORPUS_TOKENS}} tokens, which does not fit in the 128K window most hosted models offer at all. A retrieval-side proxy shows the evidence stays locatable at the top of the whole-corpus ranking ({{LC_PROXY_TOP10}} in the top 10 of {{LC_PROXY_SET_SIZE}}). The quality half was **not** measured, because no generator was reachable when the experiment ran; we therefore make no claim about long-context answer quality in either direction, and the harness is in place to run it as soon as one is."""

PAPER_LIM_OLD = """7. **Long context not yet compared.** No superiority claim over long-context prompting is made."""

PAPER_LIM_NEW = """7. **Long context compared on cost, not on quality.** The long-context arm costs {{LC_RATIO}}x more input per query than the RAG arm on the focus domain ({{MC_LC_RATIO}}x on the six-category corpus), and on the six-category corpus the corpus exceeds the 128K window most hosted models offer. The answer-quality comparison was not run, because no generator was reachable; no superiority claim over long-context prompting is made in either direction."""

# --------------------------------------------------------------------------
# The department report.
# --------------------------------------------------------------------------
REPORT_OLD = """        "The long-context baseline has not been run on either corpus, so no "
        "superiority claim over long-context prompting is made. This is the largest "
        "unresolved threat to the framing.","""

REPORT_NEW = """        "The long-context baseline is measured on cost but not on quality. The "
        "long-context arm costs {{LC_RATIO}}x more input per query than the RAG "
        "arm on the focus domain, and on the six-category corpus the corpus is "
        "{{MC_LC_CORPUS_TOKENS}} tokens, which does not fit the 128K window most "
        "hosted models offer. The answer-quality comparison was not run, because no "
        "generator was reachable when the experiment ran, so no superiority claim "
        "over long-context prompting is made in either direction. This remains "
        "the largest unresolved threat to the framing.","""

REPORT_FUTURE_OLD = """        "Run the long-context baseline on the same corpus and the same questions.","""
REPORT_FUTURE_NEW = """        "Run the long-context arm's answer-quality comparison, which needs a "
        "generator: the harness is in impl/experiments/run_long_context.py and "
        "runs as soon as a credential is present.","""

# --------------------------------------------------------------------------
# The deck.
# --------------------------------------------------------------------------
PPTX_OLD = """    "Any superiority claim over long-context prompting — that baseline has not been "
    "run on our corpus.","""

PPTX_NEW = """    "Any superiority claim over long-context prompting — we measured the cost "
    "half of that baseline, not the answer quality, so we claim neither way.","""

PPTX_NEXT_OLD = """    "Run the long-context baseline on our own corpus — the biggest unaddressed "
    "threat.","""

PPTX_NEXT_NEW = """    "Run the long-context arm's answer-quality comparison — the cost half is "
    "measured, the quality half needs a generator.","""

PPTX_NOTES_OLD = """         "The biggest honest gap is long context. On a 634-chunk corpus you can put "
         "the whole thing in the prompt, and 2026 work reports long-context beating "
         "semantic RAG in manufacturing safety. That experiment has not been run on "
         "my corpus, and it is first on my list.")"""

PPTX_NOTES_NEW = """         "The biggest honest gap is long context. My corpus does fit in a modern "
         "context window, and 2026 work reports long-context beating semantic RAG "
         "in manufacturing safety. I measured the cost half of that comparison: "
         "the whole corpus is {{LC_CORPUS_TOKENS}} tokens against the RAG arm's "
         "{{LC_RAG_TOKENS}}, so the long-context arm is {{LC_RATIO}} times more "
         "expensive per query. I did not measure the answer-quality half, because "
         "I had no generator available when I ran it, and I am not going to "
         "estimate it. It is first on my list.")"""

# --------------------------------------------------------------------------
# The guide: the Part F threat, the viva answer, and the limitation row.
# --------------------------------------------------------------------------
GUIDE_T1_OLD = """**T1 — Long context beats RAG in this exact domain.** A 2026 study of document-grounded generation in *manufacturing safety* reports long-context systems ahead of semantic RAG. The corpus is small enough that this baseline is feasible, and it is the most serious threat to the framing. It must be run before submission, and if long context wins, the claim has to be narrowed to the *confidence* mechanisms rather than the retrieval."""

GUIDE_T1_NEW = """**T1 — Long context beats RAG in this exact domain.** A 2026 study of document-grounded generation in *manufacturing safety* reports long-context systems ahead of semantic RAG. The corpus is small enough that this baseline is feasible, and it is the most serious threat to the framing. **Part E.7 measures the cost half**: the long-context arm costs {{LC_RATIO}}x more input per query on the focus domain, and on the six-category corpus the corpus does not fit the 128K window most hosted models offer at all. The answer-quality half was **not** measured — no generator was reachable when the experiment ran — so if long context wins on quality the claim still has to be narrowed to the *confidence* mechanisms rather than the retrieval, and we do not know yet."""

GUIDE_Q_OLD = """corpus it is feasible, and 2026 work reports long-context systems beating semantic
RAG in manufacturing safety at 26× the token cost. We do not claim long context is
worse; we claim that the mechanisms a long-context prompt does not have — refusal,
per-claim confidence bands, category routing — are properties our system has and a long-context
prompt does not, and that the corresponding long-context baseline must be run before any superiority
claim is made."""

GUIDE_Q_NEW = """corpus it is feasible, and 2026 work reports long-context systems beating semantic
RAG in manufacturing safety at 26× the token cost. We do not claim long context is
worse. **We measured the cost half of it**: on the focus domain the corpus is
{{LC_CORPUS_TOKENS}} tokens against the RAG arm's {{LC_RAG_TOKENS}}, so the
long-context arm costs {{LC_RATIO}}x more per query, and on the six-category
corpus the corpus does not fit a 128K window at all. A retrieval-side proxy shows
the evidence stays at the top of the whole-corpus ranking ({{LC_PROXY_TOP10}} in
the top 10 of {{LC_PROXY_SET_SIZE}}), so the long-context arm's advantage would
have to come from the reader, not from the retrieval. **We did not measure the
answer-quality half**, because no generator was reachable when the experiment
ran, and we will not estimate it. So we claim neither way: the mechanisms a
long-context prompt does not have — refusal, per-claim confidence bands,
category routing — are properties our system has, and the honest position on
the retrieval comparison is that it is open."""

GUIDE_L9_OLD = """| **L9** | Long-context baseline not yet run | **No superiority claim over long context can be made** | Run it on the same corpus with the same questions |"""

GUIDE_L9_NEW = """| **L9** | Long-context baseline measured on cost, not on quality | The long-context arm costs {{LC_RATIO}}x more input per query, and the six-category corpus exceeds a 128K window; but no generator was reachable, so the answer-quality comparison was not run and **no superiority claim over long context can be made in either direction** | Run the quality half of the comparison (`impl/experiments/run_long_context.py`, needs a credential) |"""


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
    total += apply(T / "Deliverable_2a_Technical_Report.md",
                   [(PAPER_OLD, PAPER_NEW), (PAPER_LIM_OLD, PAPER_LIM_NEW)])
    total += apply(T / "scripts" / "make_docx.py",
                   [(REPORT_OLD, REPORT_NEW),
                    (REPORT_FUTURE_OLD, REPORT_FUTURE_NEW)])
    total += apply(T / "scripts" / "make_pptx.py",
                   [(PPTX_OLD, PPTX_NEW), (PPTX_NEXT_OLD, PPTX_NEXT_NEW),
                    (PPTX_NOTES_OLD, PPTX_NOTES_NEW)])
    total += apply(T / "Deliverable_1_PartF_toJ.md",
                   [(GUIDE_T1_OLD, GUIDE_T1_NEW), (GUIDE_Q_OLD, GUIDE_Q_NEW),
                    (GUIDE_L9_OLD, GUIDE_L9_NEW)])
    print(f"\n{total} replacements applied")
    return 0


if __name__ == "__main__":
    sys.exit(main())
