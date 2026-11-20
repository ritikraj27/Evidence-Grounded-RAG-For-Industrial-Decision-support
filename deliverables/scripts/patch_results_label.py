#!/usr/bin/env python3
"""Put the label's contingency table and the true baselines in the results.

The gate section of the guide currently reports a base rate and calls the
threshold-sweep endpoints "baselines". Both are wrong: the endpoints are not
baselines, and a base rate alone does not say how much of the negative class
is retrieval failure. This patch reports the three-way decomposition and the
two degenerate policies.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "deliverables" / "scripts" / "make_results_md.py"

OLD = """The gate was evaluated as a **selective-prediction policy**: the threshold was
swept, and for each value we report what the system answered, what it refused,
and the abstention precision. The base rate of contexts containing sufficient
evidence is {exp2['base_rate_answer_in_context']:.3f}, and the retriever's
own recall of the gold chunk is {exp2['retriever_recall_of_gold']:.3f}."""

NEW = """The gate was evaluated as a **selective-prediction policy**: the threshold was
swept, and for each value we report what the system answered, what it refused,
and the abstention precision.

**What the label actually is, and the table that says so.** The label is 1 iff
the gold chunk is present in the reranked candidate pool. That is
*answer-in-context detectability*, not evidence sufficiency — the literature
reserves "sufficiency" for the set-level property that independent passage
scoring cannot detect (SURE-RAG, arXiv:2605.03534; Certify,
arXiv:2610.34684) — and the difference is not a naming quibble, because it
determines what the negative class contains.

| | Count | Share |
|---|---|---|
| Answerable, evidence found in the context | {dec['answerable_and_found']} | {dec['answerable_and_found'] / max(n_ans, 1):.1%} of answerable |
| Answerable, evidence **missed** by the retriever | {dec['answerable_and_missed']} | {dec['answerable_and_missed'] / max(n_ans, 1):.1%} of answerable |
| Unanswerable | {dec['unanswerable']} | {dec['unanswerable'] / max(n_un, 1):.1%} of unanswerable |

The negative class is answerable-and-missed **plus** unanswerable. The
retriever's own recall of the gold chunk is
{exp2['retriever_recall_of_gold']:.3f}, so the negative class is dominated by
**retrieval failure** — an answerable question whose evidence the retriever
missed — rather than by absence of evidence. The gate therefore detects whether
the answer is in the context, and **cannot** distinguish "there is no evidence
here" from "the evidence is here and the retriever missed it", because the
retrieval scores it uses are exactly the scores that failed. That is a
limitation of the approach, it is also the field's known result for model- and
prompt-based abstention (GRAB-RAG, arXiv:2608.22228), and it is why the gate
is reported as a selective-prediction policy rather than as a detector."""

OLD_BASELINES = """### Calibration"""

NEW_BASELINES = """### The two baselines, and the two that are not

| Policy | Answers answerable | Refuses unanswerable | Abstention precision |
|---|---|---|---|
| **Never refuse** (τ = 0) | 1.000 | 0.000 | undefined — no abstentions are made |
| **Always refuse** (τ = 1) | 0.000 | 1.000 | {n_un / max(n_un + n_ans, 1):.3f} |
| Loosest threshold in the sweep (τ = {loose['tau']:.2f}) | {loose['answerable_answered']:.3f} | {loose['unanswerable_refused']:.3f} | {loose['abstention_precision']:.3f} |
| Strictest threshold in the sweep (τ = {strict['tau']:.2f}) | {strict['answerable_answered']:.3f} | {strict['unanswerable_refused']:.3f} | {strict['abstention_precision']:.3f} |

The last two rows are **not baselines**. The loosest threshold in the sweep
still refuses some unanswerable queries, so calling it an "always-answer
baseline" overstates what it shows; the strictest threshold still answers some
answerable ones. The two degenerate policies are the baselines, and the gate
has to be read against them.

### Calibration"""


def main() -> int:
    s = TARGET.read_text(encoding="utf-8")
    failures = []
    if OLD not in s:
        failures.append("the gate paragraph was not found")
    else:
        s = s.replace(OLD, NEW, 1)
    if OLD_BASELINES not in s:
        failures.append("the calibration heading was not found")
    else:
        s = s.replace(OLD_BASELINES, NEW_BASELINES, 1)
    # The values the new text interpolates.
    anchor = """    uni = exp2["univariate_top1_rerank"]"""
    if anchor not in s:
        failures.append("the univariate anchor was not found")
    else:
        s = s.replace(anchor, anchor + """
    dec = exp2.get("label_decomposition", {})
    n_ans = int(dec.get("answerable_and_found", 0)) + int(dec.get("answerable_and_missed", 0))
    n_un = int(dec.get("unanswerable", 0))
    loose = exp2.get("loosest_threshold_in_sweep") or exp2["threshold_sweep"][0]
    strict = exp2.get("strictest_threshold_in_sweep") or exp2["threshold_sweep"][-1]""", 1)
    if failures:
        for f in failures:
            print(f"!! {f}")
        return 1
    TARGET.write_text(s, encoding="utf-8")
    print("  the results generator now reports the label decomposition and the true baselines")
    return 0


if __name__ == "__main__":
    sys.exit(main())
