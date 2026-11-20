#!/usr/bin/env python3
"""The last quota-placement corrections: the LaTeX prose generator, the
papers' abstracts and contributions, the report's conclusion, and the deck.

Every one of these still says the quota binds downstream. The measurements
say the opposite, in both corpora.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
S = ROOT / "deliverables" / "scripts"
T = ROOT / "deliverables" / "templates"

# --------------------------------------------------------------------------
# 1. The LaTeX prose generator: the quota clause and the lesson.
# --------------------------------------------------------------------------
p = S / "make_tex_prose.py"
s = p.read_text(encoding="utf-8")
old = '''    quota_clause = (
        f"Applied before the reranker it cost {pre_cost_pp:.1f} points of "
        f"Recall@10 ({E['recall@10']:.3f} to {F['recall@10']:.3f}, "
        f"$p={sci(p_of('E. +category_filter'))}$) and table recall to {tbl_f:.3f} "
        f"--- a net loss on both counts, because the reranker undoes the quota and "
        f"the quota has already removed good text chunks before the cross-encoder "
        f"saw them. Applied after the reranker it costs {post_cost_pp:.1f} points "
        f"instead, and is {post_vs_pre_pp:.1f} points better than the pre-rerank "
        f"variant ($p={sci(p_of('F. +quota_pre_rerank'))}$) at {tbl_g * 100:.1f}\\\\% "
        f"table recall."
    )'''
new = '''    quota_clause = (
        f"Applied before the reranker it moves Recall@10 by "
        f"{F['recall@10'] - E['recall@10']:+.3f} ({E['recall@10']:.3f} to "
        f"{F['recall@10']:.3f}, $p={sci(p_of('E. +category_filter'))}$) and "
        f"reaches table recall {tbl_f:.3f}. Applied after the reranker it moves "
        f"recall by {G['recall@10'] - E['recall@10']:+.3f} and reaches only "
        f"{tbl_g * 100:.1f}\\\\% table recall --- so the post-rerank placement "
        f"is {post_vs_pre_pp:.1f} points worse on Recall@10 than the "
        f"pre-rerank one ($p={sci(p_of('F. +quota_pre_rerank'))}$). The "
        f"mechanism is about what each stage can undo: a pre-rerank quota "
        f"proposes the membership of the final ten and the cross-encoder can "
        f"only reorder it, whereas a post-rerank quota must import candidates "
        f"the cross-encoder already ranked below the cut."
    )'''
assert s.count(old) == 1, s.count(old)
s = s.replace(old, new, 1)

old2 = '''The generalisable lesson is that \\\\emph{{a quota on a downstream artefact must be
enforced downstream of the component that could undo it}}.'''
new2 = '''The generalisable lesson, corrected, is that \\\\emph{{a constraint on a
downstream artefact should be enforced where it can still choose the
candidates, not where it must work against another component's judgement}}.'''
assert s.count(old2) == 1, s.count(old2)
s = s.replace(old2, new2, 1)
p.write_text(s, encoding="utf-8")
print("  the LaTeX prose generator corrected")

# --------------------------------------------------------------------------
# 2. The papers' abstracts and contributions.
# --------------------------------------------------------------------------
EDITS = [
    ("Deliverable_2c_Journal_Style_Paper.tex", [
        ("""\\item A modality quota shown to bind only when enforced downstream of the
component that could undo it.""",
         """\\item A modality quota shown to belong \\emph{before} the cross-encoder
rather than after it, which inverts the rule the framework was designed
on."""),
    ]),
    ("Deliverable_2b_IEEE_Conference_Paper.tex", [
        ("""retrieval legs is a no-op, and a modality quota binds only when applied""",
         """retrieval legs is a no-op, and a modality quota binds only when applied"""),
    ]),
]

for rel, edits in EDITS:
    p = T / rel
    s = p.read_text(encoding="utf-8")
    for old_t, new_t in edits:
        c = s.count(old_t)
        if c != 1:
            print(f"!! {rel}: count={c}")
            continue
        s = s.replace(old_t, new_t, 1)
    p.write_text(s, encoding="utf-8")
print("  the papers' contribution lists corrected")

# --------------------------------------------------------------------------
# 3. The report's conclusion.
# --------------------------------------------------------------------------
p = T / "scripts" / "make_docx.py"
s = p.read_text(encoding="utf-8")
old3 = '''         "its assumptions: a modality quota binds only when enforced downstream of "'''
new3 = '''         "its assumptions: a modality quota binds only when enforced before the "'''
if old3 in s:
    s = s.replace(old3, new3, 1)
    print("  the report's conclusion corrected")
else:
    print("  !! the report's conclusion anchor not found")
p.write_text(s, encoding="utf-8")

# --------------------------------------------------------------------------
# 4. The deck: the slide-12 narrative and the next-steps list.
# --------------------------------------------------------------------------
p = T / "scripts" / "make_pptx.py"
s = p.read_text(encoding="utf-8")
old4 = '''         "be enforced downstream of whatever could undo it.\\n\\n"'''
new4 = '''         "be enforced where it can still choose the candidates.\\n\\n"'''
if old4 in s:
    s = s.replace(old4, new4, 1)
    print("  the deck's slide-12 narrative corrected")
else:
    print("  !! the deck's slide-12 anchor not found")
old5 = '''     "quota binds only downstream of the component that could undo it; the modality "'''
new5 = '''     "quota binds only before the cross-encoder, which inverts the rule the "
     "framework was designed on; the modality "'''
if old5 in s:
    s = s.replace(old5, new5, 1)
    print("  the deck's next-steps corrected")
else:
    print("  !! the deck's next-steps anchor not found")
p.write_text(s, encoding="utf-8")
