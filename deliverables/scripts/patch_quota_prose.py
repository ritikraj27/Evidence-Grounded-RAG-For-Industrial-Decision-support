#!/usr/bin/env python3
"""Correct the prose that still asserts the old quota-placement rule.

The measurements now put the quota *before* the cross-encoder, in both
corpora, which inverts the rule the framework was designed on. Every
sentence that said "the quota binds only downstream" has to change, and
every one that reported the old direction has to report the new one.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
T = ROOT / "deliverables" / "templates"
S = ROOT / "deliverables" / "scripts"

EDITS = [
    ("Deliverable_1_Part1_Content.md", [
        # C.8 -- the measured consequence.
        ("""**The measured consequence is the difference between a mechanism that works
and one that is merely present.** The quota buys modality precision, and what
it costs depends on where it is applied. On the multi-category corpus the
reranker takes table recall@10 from {{MC_TBL_D}} to {{MC_TBL_E}}, and the quota
applied *after* it puts it back to {{MC_TBL_G}} — at a cost of
{{MC_QUOTA_POST_COST_PP}} points of overall recall@10. Applied *before* the
reranker the same quota reaches the same table recall and costs
{{MC_QUOTA_PRE_COST_PP}} points of recall@10. **The mechanism is the same;
only its position changed what it cost.**

And on the focus domain there is a second lesson. There, table recall is
already {{TBL_E}} before the quota is applied, so the quota has no table gain
left to buy and all it does is displace relevant prose. **A quota pays only
where the modality mix has left something to pay for** — which is a statement
about the corpus, and is why the corpus composition is reported before the
result rather than after it.""",
         """**The measured consequence inverts the rule the framework was designed
on.** The quota belongs **before** the cross-encoder, not after it. On the
focus domain, applying it before the reranker moves overall recall@10 by
{{QUOTA_PRE_DELTA}} and leaves table recall at {{TBL_F}}, while applying the
*same quota* after the reranker moves recall by {{QUOTA_POST_DELTA}} and drops
table recall to {{TBL_G}}. The same ordering holds on the six-category corpus:
the pre-rerank quota reaches table recall {{MC_TBL_F}} and the post-rerank
quota {{MC_TBL_G}}.

**Why, which is not obvious.** It is about what each stage can and cannot
undo. A pre-rerank quota proposes a *membership* for the final ten; the
cross-encoder then re-scores those ten and can reorder them, but it cannot
change which ten they are, so a forced table chunk survives. A post-rerank
quota starts from the reranked ten and swaps one of them for a table chunk the
cross-encoder already ranked **below** the cut — so it tends to import the
wrong table chunk and to displace a good one. The quota applied later is
working against a veto it cannot appeal.

**The generalisable rule, corrected:** *a constraint on a downstream artefact
should be enforced where it can still choose the candidates, not where it must
work against another component's judgement.* Enforcing a constraint downstream
of a scorer means importing candidates the scorer has already rejected. This
project arrived at the rule by measuring the opposite of what it expected,
which is the more convincing way to arrive at one."""),
        # A.4 -- the quota bullet.
        ("""- **The modality quota delivers its table-recall gain, and its pipeline position
  decides what you pay for it.** The quota lifts table recall@10 from {{TBL_E}} to
  {{TBL_G}}. Applied *before* the reranker it costs {{QUOTA_PRE_COST_PP}} points of
  overall recall@10 (p = {{P_EF}}); applied *after* it costs
  {{QUOTA_POST_COST_PP}} points. See §C.8 and Part E.""",
         """- **The modality quota belongs before the cross-encoder, not after it.** This
  inverts the rule the framework was designed on. Applied *before* the reranker
  it moves overall recall@10 by {{QUOTA_PRE_DELTA}} and holds table recall at
  {{TBL_F}}; applied *after* it moves recall by {{QUOTA_POST_DELTA}} and table
  recall falls to {{TBL_G}}. A quota applied later has to import candidates the
  cross-encoder already rejected. See §C.8 and Part E."""),
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
print(f"  {total} guide passages corrected")
