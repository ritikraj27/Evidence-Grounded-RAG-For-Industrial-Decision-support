#!/usr/bin/env python3
"""Add the limitations the direction check surfaced.

Three of them are new limitations of the work itself, not of the corpus:

  * the gate's label is answer-in-context detectability, not evidence
    sufficiency, and the negative class is dominated by retrieval failure;
  * the contradiction gate's recall on the verifiable subset is 1.0 *by
    construction*, because the subset is defined by numeric conflicts and the
    numeric detector is an OR-branch of the gate, so no human labels exist to
    defend it;
  * the cross-category transfer study is an *intra*-domain study, because all
    six categories are industrial-engineering sub-domains.

L1 is corrected: the six-category corpus is now run, not merely planned.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
T = ROOT / "deliverables" / "templates"

L1_OLD = """| **L1** | Single-domain evaluation in the September 2026 run (Supply Chain Management only); the other 11 categories share the pipeline but were not run | Generalisation across categories is **demonstrated mechanistically**, not empirically, in the primary corpus | The transfer experiment in Part E, plus a second full category run |"""

L1_NEW = """| **L1** | The evaluation is single-domain by design — supply chain management is the focus — with the other five industrial-engineering categories retained for the cross-category transfer experiment | Generalisation beyond supply chain is **demonstrated mechanistically** and by that transfer experiment, not empirically at production scale | A licensed, multi-domain industrial corpus with the same provenance discipline |"""

L13_OLD = """| **L10** | Calibration is fitted per retriever, not universally | A threshold transferred to a new retriever is wrong — and DeclineCraft shows it is wrong in the direction that flatters the weaker system | Re-fit per arm, and report the per-arm threshold |"""

L13_NEW = """| **L10** | Calibration is fitted per retriever, not universally | A threshold transferred to a new retriever is wrong — and DeclineCraft shows it is wrong in the direction that flatters the weaker system | Re-fit per arm, and report the per-arm threshold |
| **L11** | The gate's label is **answer-in-context detectability**, not evidence sufficiency: the positive class is "the gold chunk is in the reranked candidate pool", and the negative class is dominated by *retrieval failure* rather than by absence of evidence | The gate cannot distinguish "there is no evidence here" from "the evidence is here and the retriever missed it", because the retrieval scores it uses are exactly the scores that failed. The literature reserves "sufficiency" for the set-level property (SURE-RAG, Certify) | A label that separates absent evidence from missed evidence — e.g. an answerability annotation on the context, independent of the retrieval scores |
| **L12** | The contradiction gate's recall on the *verifiable* subset is 1.000 **by construction**: the subset is defined by the presence of a numeric conflict and the numeric detector is an OR-branch of the gate | That number is not evidence. The informative quantity is how many verifiable conflicts the NLI-and-same-subject conjunction catches with the numeric branch removed, which the experiment now reports; but neither quantity can be defended without human labels | Hand-label a stratified sample of flagged and unflagged pairs against a rubric that separates contradiction from granularity difference, temporal supersession and term mismatch; report precision and recall with intervals |
| **L13** | The cross-category transfer experiment is an **intra-domain** study: all six categories are industrial-engineering sub-domains, so it tests transfer between sub-domains of one domain, not between domains | The proposal's wording ("across diverse industrial sub-domains") should be read as intra-domain transfer; no claim is made about transfer to a different industry | A corpus spanning genuinely different industries, with the same protocol |"""

REPORT_OLD = """        "The calibration is deployment-specific and must be re-fitted for each "
        "retrieval configuration and each corpus.",
    ], start=1):"""

REPORT_NEW = """        "The calibration is deployment-specific and must be re-fitted for each "
        "retrieval configuration and each corpus.",
        "The gate's label is answer-in-context detectability, not evidence "
        "sufficiency: the negative class is dominated by retrieval failure, so the "
        "gate cannot separate 'there is no evidence here' from 'the evidence is here "
        "and the retriever missed it'. The contingency table is reported so that the "
        "limit is visible rather than implied.",
        "The contradiction gate's recall on the verifiable subset is 1.000 by "
        "construction, because that subset is defined by numeric conflicts and the "
        "numeric detector is an OR-branch of the gate. The experiment reports what "
        "the NLI-and-same-subject conjunction catches without the numeric branch; "
        "defending either number requires human labels, which we do not have.",
        "The cross-category transfer experiment is an intra-domain study: all six "
        "categories are industrial-engineering sub-domains, so it measures transfer "
        "between sub-domains of one domain rather than between industries.",
    ], start=1):"""


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
    total += apply(T / "Deliverable_1_PartF_toJ.md",
                   [(L1_OLD, L1_NEW), (L13_OLD, L13_NEW)])
    total += apply(T / "scripts" / "make_docx.py", [(REPORT_OLD, REPORT_NEW)])
    print(f"\n{total} replacements applied")
    return 0


if __name__ == "__main__":
    sys.exit(main())
