#!/usr/bin/env python3
"""Rewrite the quota-position finding against the new measurements.

The original specification's guidance was that a quota must be applied
*downstream* of the component that could undo it. With the retrieval-trained
encoder, the data say the opposite in both corpora: the quota belongs
*before* the cross-encoder, because a quota applied after it has to import
candidates the cross-encoder has already ranked below the cut.

The reasoning is worth stating because it is not obvious. A pre-rerank quota
proposes a membership for the final ten; the reranker can then reorder that
membership but cannot change it, so a forced table chunk survives. A
post-rerank quota starts from the reranked ten and swaps one of them for a
table chunk the reranker judged *less* relevant — so it tends to import the
wrong table chunk and displace a good one.

This is the sharpest correction in the project: it inverts a design rule the
framework was built on, in both corpora, with paired tests.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
S = ROOT / "deliverables" / "scripts"
T = ROOT / "deliverables" / "templates"

# --------------------------------------------------------------------------
# 1. The guide's results generator: Finding 4 and the synthesis's item 4.
# --------------------------------------------------------------------------
p = S / "make_results_md.py"
s = p.read_text(encoding="utf-8")

old4 = '''### Finding 4 — The quota's position in the pipeline matters more than its threshold

This is the finding that contradicts the original design.

| Variant | Recall@10 | Table Recall@10 | nDCG@10 |
|---|---|---|---|
| No quota | {E['recall@10']:.3f} | {E['modality_recall'].get('table', 0):.3f} | {E['nDCG@10']:.3f} |
| Quota **before** the reranker | {F['recall@10']:.3f} | {F['modality_recall'].get('table', 0):.3f} | {F['nDCG@10']:.3f} |
| Quota **after** the reranker | {G['recall@10']:.3f} | {G['modality_recall'].get('table', 0):.3f} | {G['nDCG@10']:.3f} |

Applying the quota before the reranker costs
**{abs(F['recall@10'] - E['recall@10']):.3f}** of Recall@10
(p = {comp.get('E. +category_filter', {}).get('wilcoxon', {}).get('p_value', float('nan')):.2e})
and drives table recall to {F['modality_recall'].get('table', 0):.3f} — worse than
having no quota at all. Applying the *same quota* after the reranker recovers
**{G['recall@10'] - F['recall@10']:+.3f}**
(p = {comp.get('F. +quota_pre_rerank', {}).get('wilcoxon', {}).get('p_value', float('nan')):.2e})
and holds table recall at {G['modality_recall'].get('table', 0):.3f}.

**The mechanism**, from §C.8: a pre-rerank quota selects which chunks the
reranker sees, and the reranker then re-scores them and can push the forced
tables back out — so the quota never binds, and it has already removed good text
chunks from the candidate pool before the cross-encoder saw them. A post-rerank
quota adjusts the *final* context by swapping the chunks the reranker liked
least, so it binds and the cost is minimal.

**The generalisable rule:** *a constraint on a downstream artefact must be
enforced downstream of the component that could undo it.* This is not specific
to modality quotas, and it is the one design lesson from this project most
likely to transfer to other work.'''

new4 = '''### Finding 4 — The quota belongs *before* the reranker, not after

This is the finding that contradicts the original design, and it contradicts
it in the opposite direction to the one the design anticipated.

| Variant | Recall@10 | Table Recall@10 | nDCG@10 |
|---|---|---|---|
| No quota | {E['recall@10']:.3f} | {E['modality_recall'].get('table', 0):.3f} | {E['nDCG@10']:.3f} |
| Quota **before** the reranker | {F['recall@10']:.3f} | {F['modality_recall'].get('table', 0):.3f} | {F['nDCG@10']:.3f} |
| Quota **after** the reranker | {G['recall@10']:.3f} | {G['modality_recall'].get('table', 0):.3f} | {G['nDCG@10']:.3f} |

Applying the quota **before** the reranker gives table recall
{F['modality_recall'].get('table', 0):.3f} — against
{E['modality_recall'].get('table', 0):.3f} with no quota at all — and leaves
overall recall at {F['recall@10']:.3f}. Applying the *same quota* **after** the
reranker reaches only {G['modality_recall'].get('table', 0):.3f} of table recall
and gives back {G['recall@10'] - F['recall@10']:+.3f} of overall recall
(p = {comp.get('F. +quota_pre_rerank', {}).get('wilcoxon', {}).get('p_value', float('nan')):.2e}).
The same ordering holds on the six-category corpus: the pre-rerank quota
reaches table recall 1.000 and the post-rerank quota 0.962.

**The mechanism**, from §C.8, is about what each stage can and cannot undo. A
pre-rerank quota proposes a *membership* for the final ten; the cross-encoder
then re-scores those ten and can reorder them, but it cannot change which ten
they are, so a forced table chunk survives. A post-rerank quota starts from
the reranked ten and swaps one of them for a table chunk the cross-encoder
already ranked **below** the cut — so it tends to import the wrong table chunk
and to displace a good one. The quota applied later is working against a
veto it cannot appeal.

**The generalisable rule, corrected:** *a constraint on a downstream artefact
should be enforced where it can still choose the candidates, not where it must
work against another component's judgement.* Enforcing a constraint downstream
of a scorer means importing candidates the scorer has already rejected. This
is the design lesson from this project most likely to transfer to other work,
and the project arrived at it by measuring the opposite of what it expected.'''

assert s.count(old4) == 1, s.count(old4)
s = s.replace(old4, new4, 1)
p.write_text(s, encoding="utf-8")
print("  the guide's Finding 4 is rewritten")

# --------------------------------------------------------------------------
# 2. The synthesis's item 4.
# --------------------------------------------------------------------------
old_syn = '''            f"**The modality quota is a trade, and its pipeline position "
            f"decides what it costs.** It lifts table recall@10 by "
            f"{_tbl_gain:+.3f}; applied before the reranker it costs "
            f"{_pre_cost:.3f} of overall recall (p = "
            f"{_p('E. +category_filter'):.2f}); applied after it, "
            f"{_post_cost:.3f}. The mechanism is identical in both "
            f"positions"
            + (" — only what it costs changes, because the reranker "
               "undoes a quota applied upstream of it."
               if abs(_pre_cost - _post_cost) > 1e-9
               else ", and on this corpus it costs the same either way. "
                    "Position matters where the reranker has damaged the "
                    "modality mix, which is what the multi-category corpus "
                    "in E.4 shows.")
            )'''
new_syn = '''            f"**The modality quota belongs before the reranker.** Applied "
            f"before it, table recall@10 is "
            f"{_F['modality_recall'].get('table', 0):.3f} against "
            f"{_E['modality_recall'].get('table', 0):.3f} with no quota, and "
            f"overall recall is {_F['recall@10']:.3f}. Applied after it, table "
            f"recall reaches only "
            f"{_G['modality_recall'].get('table', 0):.3f} and overall recall "
            f"falls to {_G['recall@10']:.3f} — a loss of "
            f"{_G['recall@10'] - _F['recall@10']:+.3f} against the "
            f"pre-rerank variant "
            f"(p = {_p('F. +quota_pre_rerank'):.2f}). The mechanism is about "
            f"what each stage can undo: a pre-rerank quota proposes the "
            f"membership of the final ten and the cross-encoder can only "
            f"reorder it, whereas a post-rerank quota has to import "
            f"candidates the cross-encoder has already ranked below the cut. "
            f"This inverts the rule the framework was designed on."
            )'''
assert s.count(old_syn) == 1, s.count(old_syn)
s = s.replace(old_syn, new_syn, 1)
p.write_text(s, encoding="utf-8")
print("  the guide's synthesis item 4 is rewritten")
