#!/usr/bin/env python3
"""Correct the candidate-pool claims.

With the retrieval-trained encoder the pool sweep no longer rises
monotonically: it peaks at a pool of about ten — the size of the final
context — and then *declines*, because the extra candidates are distractors
competing for the same ten slots. The old text said the curve was monotone
and saturating and that the useful regime was twenty to fifty. Both are now
wrong, and the new shape is a sharper finding: the pool should be about the
size of the context, not twenty times it.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
T = ROOT / "deliverables" / "templates"

EDITS = [
    ("Deliverable_1_Part1_Content.md", [
        ("""- **A reranker's recall is governed by the size of its candidate pool.** Sweeping
  the pool size gives a monotone, saturating curve: recall@10 rises from {{POOL5}} at
  a pool of 5 to {{POOL100}} at a pool of 100, with most of the gain arriving by a pool
  of about 20 — twice the 10-chunk final context. A pool the size of the context
  cannot improve recall at all, because it can only permute the chunks it was
  given. This is the most likely explanation of the −5.34 pp reranker regression
  reported in the September 2026 project report on a different corpus, and it is
  the cheapest actionable finding in the project: one parameter, worth {{DELTA_BC}} of
  recall.""",
         """- **A reranker's recall is governed by the size of its candidate pool.** Sweeping
  the pool size gives a curve that rises and then falls: recall@10 goes from
  {{POOL5}} at a pool of 5 to {{POOL10}} at a pool of 10 — the size of the
  final context — and then back down to {{POOL100}} at a pool of 100. The
  peak is at {{POOL_KNEE}}, and a pool past it does not merely fail to help:
  it costs, because the extra candidates are distractors competing for the
  same ten slots. A pool the size of the context cannot improve recall at all,
  since it can only permute the chunks it was given. This is the most likely
  explanation of the −5.34 pp reranker regression reported in the September 2026
  project report on a different corpus, and it is the cheapest actionable
  finding in the project: one parameter, worth {{POOL_GAIN}} of recall."""),
        ("""**Why the pool size decides it.** A cross-encoder can only reorder the candidates
it is given. It has no opinion about the 40 chunks that were never shown to it.
Give it a pool the size of the final context and the best it can do is permute
those ten — it cannot bring in the relevant chunk sitting at fused rank 34, and
it can only lose the relevant one sitting at rank 12. Give it a pool an order of
magnitude larger and it has room to promote chunks the first stage ranked below
the cut.""",
         """**Why the pool size decides it.** A cross-encoder can only reorder the candidates
it is given. It has no opinion about the 40 chunks that were never shown to it.
Give it a pool the size of the final context and the best it can do is permute
those ten — it cannot bring in the relevant chunk sitting at fused rank 34, and
it can only lose the relevant one sitting at rank 12. Give it a larger pool and
it has room to promote chunks the first stage ranked below the cut — but the
room is not free: every extra candidate is also a chance to promote a
distractor into the same ten slots. That is why the measured curve peaks
rather than saturates, and why the useful pool is about the size of the
context it feeds rather than an order of magnitude larger."""),
    ]),
    ("Deliverable_1_PartF_toJ.md", [
        ("the reranker's effect on recall is **pool-relative**: it needs a candidate pool an order of magnitude larger than the final context.",
         "the reranker's effect on recall is **pool-relative**: the measured curve peaks at a pool about the size of the final context, and a larger pool costs as well as gains."),
    ]),
]

total = 0
for rel, edits in EDITS:
    p = T / rel
    s = p.read_text(encoding="utf-8")
    for old, new in edits:
        c = s.count(old)
        if c != 1:
            print(f"!! {rel}: count={c} -> {old[:60]!r}")
            continue
        s = s.replace(old, new, 1)
        total += 1
    p.write_text(s, encoding="utf-8")
print(f"  {total} pool claims corrected")
