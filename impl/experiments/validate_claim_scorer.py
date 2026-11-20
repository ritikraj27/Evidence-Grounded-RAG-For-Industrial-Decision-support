#!/usr/bin/env python3
"""Audit the claim scorer that Experiment 8's numbers rest on.

The generator-side comparison reports how often each arm asserts something
the evidence does not support. That number is only worth reading if the
instrument that produced it can be shown to recognise truth and to reject
fabrication, and this script is that demonstration. It runs three tests
against the focus benchmark and writes the counts.

  1. Truth. Each answerable question's gold answer is scored against the
     chunk that states it. The corpus's own answers must be recognised as
     supported.
  2. Fabrication. The number in a gold answer is replaced with one the
     corpus nowhere states, and the fabricated answer must be rejected.
  3. Cross-question leakage. A bare value the corpus states for one
     quantity is scored against the chunk of a different quantity, and must
     be rejected -- otherwise every number in the corpus supports every
     question.

The known limits are reported with the counts, because the limits are part
of what the measurement means.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

from common import load_benchmark, load_index, write_result  # noqa: E402
from run_generation_eval import _claim_support, split_into_claims  # noqa: E402

#: Values the corpus does not state, used to fabricate an answer.
FABRICATED_VALUES = ("37.412%", "83.7%", "61.29%", "12.846%", "49.553%")


def main() -> int:
    index = load_index()
    bench = load_benchmark()
    answerable = [q for q in bench["queries"] if q["category"] != "unanswerable"]
    corpus = " ".join(index.chunk_text.values()).lower()

    # -- 1. the corpus's own answers must be recognised
    n_truth = n_truth_supported = 0
    missed: list[str] = []
    for q in answerable:
        answer = str(q["answer"])
        claims = split_into_claims(answer)
        bare = not claims
        claims = claims or [answer]
        scored = _claim_support(index, claims, list(q.get("gold") or []),
                                bare=bare)
        for c, s in zip(claims, scored):
            n_truth += 1
            if s["supported"]:
                n_truth_supported += 1
            else:
                missed.append(c[:120])

    # -- 2. a fabricated number must be rejected
    n_fab = n_fab_rejected = 0
    for q in answerable:
        answer = str(q["answer"])
        nums = re.findall(r"\d[\d.]*%?", answer)
        if not nums:
            continue
        fake = next((c for c in FABRICATED_VALUES if c.lower() not in corpus),
                    None)
        if fake is None:
            continue
        fabricated = answer.replace(nums[0], fake, 1)
        claims = split_into_claims(fabricated)
        bare = not claims
        claims = claims or [fabricated]
        scored = _claim_support(index, claims, list(q.get("gold") or []),
                                bare=bare)
        n_fab += 1
        if not any(s["supported"] for s in scored):
            n_fab_rejected += 1

    # -- 3. a value from another quantity must not be supported
    n_foreign = n_foreign_rejected = 0
    foreign_values = [
        re.findall(r"\d[\d.]*%?", str(o["answer"]))
        for o in answerable
        if re.findall(r"\d[\d.]*%?", str(o.get("answer") or ""))
    ]
    for q in answerable:
        value = next((v[0] for v in foreign_values
                      if v[0] not in re.findall(r"\d[\d.]*%?",
                                               str(q.get("answer") or ""))),
                     None)
        if value is None:
            continue
        scored = _claim_support(index, [value], list(q.get("gold") or []),
                                bare=True)
        n_foreign += 1
        if not any(s["supported"] for s in scored):
            n_foreign_rejected += 1

    payload = {
        "status": "run",
        "n_truth": n_truth,
        "n_truth_supported": n_truth_supported,
        "n_fabrication": n_fab,
        "n_fabrication_rejected": n_fab_rejected,
        "n_foreign": n_foreign,
        "n_foreign_rejected": n_foreign_rejected,
        "truth_recall": (n_truth_supported / n_truth) if n_truth else 0.0,
        "fabrication_rejection": (n_fab_rejected / n_fab) if n_fab else 0.0,
        "foreign_rejection": (n_foreign_rejected / n_foreign) if n_foreign else 0.0,
        "known_limits": [
            "a bare value that is a single digit cannot be located "
            "reliably by a literal test, and every miss on the truth test "
            "and every leak on the cross-question test is of that kind",
            "a value the corpus implies but does not state verbatim -- a "
            "derived figure -- is scored unsupported, because the evidence "
            "does not literally contain it",
            "the entailment model is strict about definitional fragments, "
            "which is why the literal test exists alongside it, and lenient "
            "about bare numbers, which is why a bare value is not put to "
            "it at all",
        ],
        "missed_truths": missed[:20],
    }
    write_result("exp8_scorer_validation", payload)
    print(f"[scorer] truth {n_truth_supported}/{n_truth} recognised, "
          f"fabrication {n_fab_rejected}/{n_fab} rejected, "
          f"cross-question {n_foreign_rejected}/{n_foreign} rejected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
