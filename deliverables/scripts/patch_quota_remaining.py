#!/usr/bin/env python3
"""Correct the remaining quota-placement prose in the papers, the report and
the deck.

The quota belongs before the cross-encoder now. These passages still say it
binds downstream, and one of them reports the old direction as a finding.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
S = ROOT / "deliverables" / "scripts"
T = ROOT / "deliverables" / "templates"

# --------------------------------------------------------------------------
# 1. The paper's results section.
# --------------------------------------------------------------------------
p = S / "make_paper_results.py"
s = p.read_text(encoding="utf-8")
old = """**The quota's effect depends on where it is applied.** Applied before the
reranker it cost {abs(F['recall@10'] - E['recall@10']):.3f} of Recall@10
({E['recall@10']:.3f} to {F['recall@10']:.3f}, p = {p_ef:.2e}) and drove table
recall to {F['modality_recall'].get('table', 0):.3f} — a net loss on both counts,
because the reranker undoes the quota and the quota has already removed good
text chunks from the candidate pool before the cross-encoder saw them. Applied
after the reranker it costs {abs(G['recall@10'] - E['recall@10']):.3f} instead
and is {G['recall@10'] - F['recall@10']:+.3f} better than the pre-rerank variant
(p = {p_fg:.2e}), at {G['modality_recall'].get('table', 0):.3f} table recall. The
generalisable lesson is that a quota on a downstream artefact must be enforced
downstream of the component that could undo it."""
new = """**The quota belongs before the cross-encoder, and this inverts the rule the
framework was designed on.** Applied before the reranker it moves Recall@10 by
{F['recall@10'] - E['recall@10']:+.3f} ({E['recall@10']:.3f} to
{F['recall@10']:.3f}, p = {p_ef:.2e}) and reaches table recall
{F['modality_recall'].get('table', 0):.3f}. Applied after the reranker it moves
recall by {G['recall@10'] - E['recall@10']:+.3f} and reaches only
{G['modality_recall'].get('table', 0):.3f} of table recall — so the
post-rerank placement is {G['recall@10'] - F['recall@10']:+.3f} of Recall@10
worse than the pre-rerank one (p = {p_fg:.2e}).

The mechanism is about what each stage can undo. A pre-rerank quota proposes a
*membership* for the final ten; the cross-encoder re-scores those ten and can
reorder them, but it cannot change which ten they are, so a forced table chunk
survives. A post-rerank quota starts from the reranked ten and swaps one of
them for a table chunk the cross-encoder already ranked below the cut, so it
tends to import the wrong table chunk and displace a good one. The corrected
generalisable lesson is that a constraint on a downstream artefact should be
enforced where it can still choose the candidates, not where it must work
against another component's judgement."""
assert s.count(old) == 1, s.count(old)
s = s.replace(old, new, 1)
p.write_text(s, encoding="utf-8")
print("  the paper's quota paragraph corrected")

# --------------------------------------------------------------------------
# 2. The department report's finding bullet.
# --------------------------------------------------------------------------
p = T / "scripts" / "make_docx.py"
s = p.read_text(encoding="utf-8")
old2 = '''               "The modality quota binds only downstream of the component that could "
               f"undo it. Applied before the reranker it costs "
               f"{abs(exp1['comparisons'][4]['delta']):.3f} Recall@10; applied after "
               f"it, the same quota recovers "
               f"{exp1['comparisons'][5]['delta']:.3f} "
               f"(p = {exp1['comparisons'][5]['wilcoxon']['p_value']:.1e}).")'''
new2 = '''               "The modality quota belongs BEFORE the cross-encoder, which "
               "inverts the rule the framework was designed on. Applied before "
               f"the reranker it moves Recall@10 by "
               f"{exp1['systems']['F. +quota_pre_rerank']['recall@10'] - exp1['systems']['E. +category_filter']['recall@10']:+.3f} "
               f"and reaches table recall "
               f"{exp1['systems']['F. +quota_pre_rerank']['modality_recall'].get('table', 0):.3f}; "
               f"applied after it, Recall@10 moves "
               f"{exp1['systems']['G. +quota_post_rerank']['recall@10'] - exp1['systems']['E. +category_filter']['recall@10']:+.3f} "
               f"and table recall falls to "
               f"{exp1['systems']['G. +quota_post_rerank']['modality_recall'].get('table', 0):.3f} "
               f"(p = {exp1['comparisons'][5]['wilcoxon']['p_value']:.1e}). A quota "
               "applied later has to import candidates the cross-encoder has "
               "already ranked below the cut.")'''
assert s.count(old2) == 1, s.count(old2)
s = s.replace(old2, new2, 1)
p.write_text(s, encoding="utf-8")
print("  the report's quota bullet corrected")

# --------------------------------------------------------------------------
# 3. The deck's finding 3 and its notes.
# --------------------------------------------------------------------------
p = T / "scripts" / "make_pptx.py"
s = p.read_text(encoding="utf-8")
old3 = '''    _f3_title = "A quota binds only downstream of the component that could undo it"'''
new3 = '''    _f3_title = "The quota belongs BEFORE the cross-encoder"'''
assert s.count(old3) == 1, s.count(old3)
s = s.replace(old3, new3, 1)

old4 = '''    else:
        _f3_body = (f"The quota lifts table recall by {_tbl_gain:+.3f}. Applied "
                    f"before the reranker it costs {_ef_cost:.3f} of overall recall; "
                    f"applied after it, {_eg_cost:.3f}.")'''
new4 = '''    else:
        _f3_body = (f"The quota lifts table recall by {_tbl_gain:+.3f}. Applied "
                    f"before the reranker it moves overall recall by "
                    f"{_ef_cost:+.3f}; applied after it, {_eg_cost:+.3f}.")'''
if old4 in s:
    s = s.replace(old4, new4, 1)
p.write_text(s, encoding="utf-8")
print("  the deck's quota finding corrected")

# --------------------------------------------------------------------------
# 4. The guide's viva question and limitations.
# --------------------------------------------------------------------------
p = T / "Deliverable_1_PartF_toJ.md"
s = p.read_text(encoding="utf-8")
old5 = """the finding that **the quota's position decides what it costs**: applied before
the reranker it is dominated by the same reranker that later reorders it, and
applied after it the same mechanism is affordable. The general rule is that a
constraint on a downstream artefact must be enforced downstream of the component
that could undo it."""
new5 = """the finding that **the quota's position decides what it costs** — and that
the answer is the opposite of what the framework was designed on. Applied
*before* the cross-encoder the quota reaches table recall {{TBL_F}} and moves
overall recall by {{QUOTA_PRE_DELTA}}; applied *after* it, table recall falls to
{{TBL_G}} and recall by {{QUOTA_POST_DELTA}}. The general rule, corrected: a
constraint on a downstream artefact should be enforced where it can still
choose the candidates, not where it must work against another component's
judgement."""
if old5 in s:
    s = s.replace(old5, new5, 1)
    print("  the guide's viva question corrected")
else:
    print("  !! the guide's viva question anchor not found")
p.write_text(s, encoding="utf-8")
