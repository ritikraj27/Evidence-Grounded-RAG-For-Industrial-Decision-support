#!/usr/bin/env python3
"""Update the passages that were written around the old encoder.

The dense leg was replaced with a retrieval-trained encoder and the
measurements were re-taken. These passages either described the old
encoder as the current one, or offered "replace the dense leg" as future
work. Both are now wrong, and one of them was a *conclusion* rather than
an observation.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
S = ROOT / "deliverables" / "scripts"
T = ROOT / "deliverables" / "templates"

# --------------------------------------------------------------------------
# 1. The guide's results generator: Finding 1, and the synthesis.
# --------------------------------------------------------------------------
p = S / "make_results_md.py"
s = p.read_text(encoding="utf-8")

old_finding = '''### Finding 1 — Fusion beats either leg alone, and the dense leg is the weak one

| System | Recall@10 |
|---|---|
| BM25 only | {A['recall@10']:.3f} |
| Dense only | {B['recall@10']:.3f} |
| Hybrid (RRF) | {C['recall@10']:.3f} |

Fusion gains **+{C['recall@10'] - A['recall@10']:.3f}** over the better leg
(p = {comp.get('A. bm25_only', {}).get('wilcoxon', {}).get('p_value', float('nan')):.1e} for
B→C). But look at the dense-only row: **{B['recall@10']:.3f}, worse than
BM25's {A['recall@10']:.3f}** — a significant deficit (p =
{comp.get('A. bm25_only', {}).get('wilcoxon', {}).get('p_value', float('nan')):.1e}).

This is not a bug in the implementation. `all-MiniLM-L6-v2` is a
*general-purpose sentence encoder*, trained with a symmetric similarity
objective: two sentences that mean the same thing should be close. Retrieval is
**asymmetric** — a passage is not *similar* to a question, it *answers* it. The
BEIR benchmark reports the same effect at scale: zero-shot DPR scores 0.234
against BM25's 0.413, a 43% relative deficit.

**What to do about it:** replace the dense leg with a model trained for
retrieval — `BAAI/bge-m3`, `intfloat/e5-m3-v2`, `gte-modernbert-base` — and
re-run the ablation. This is the single highest-value change available to the
system, and the ablation framework is already in place to measure it.'''

new_finding = '''### Finding 1 — The encoder, not the fusion, was the weak part

| System | Recall@10 |
|---|---|
| BM25 only | {A['recall@10']:.3f} |
| Dense only | {B['recall@10']:.3f} |
| Hybrid (RRF) | {C['recall@10']:.3f} |

The dense leg reaches **{B['recall@10']:.3f}** against BM25's
**{A['recall@10']:.3f}** — a deficit of
{A['recall@10'] - B['recall@10']:.3f} (p =
{comp.get('A. bm25_only', {}).get('wilcoxon', {}).get('p_value', float('nan')):.1e}).

That deficit is smaller than it was. The dense leg used to be a
*general-purpose sentence encoder*, trained with a symmetric similarity
objective: two sentences that mean the same thing should be close. Retrieval is
**asymmetric** — a passage is not *similar* to a question, it *answers* it —
and the mismatch showed up as a lexical leg that was better on its own than the
fusion was. The encoder is now `BAAI/bge-m3`, a retrieval-trained multilingual
model, and the before/after is in `research/09_encoder_swap.md`: the dense leg
went from {BASE_R_B} to {B['recall@10']:.3f} on Recall@10, and the fusion's
ordering deficit against the lexical leg fell from {BASE_NDCG_A} −
{BASE_NDCG_C:.3f} to {A['nDCG@10']:.3f} − {C['nDCG@10']:.3f}.

The lesson generalises past this corpus: a hybrid retriever is only as good as
its worse leg, and "hybrid" is not a free upgrade. Giving a weak leg half the
say in the ranking costs the strong leg's ordering, and the effect is silent —
the fusion's numbers look reasonable, they are just worse than the leg you
already had.'''

assert s.count(old_finding) == 1, s.count(old_finding)
s = s.replace(old_finding, new_finding, 1)

# The synthesis's two fusion branches.
old_syn1 = '''            f"equal say in the ranking, so a much weaker leg spends slots on "
            f"worse candidates. Replacing `all-MiniLM-L6-v2` with a "
            f"retrieval-trained encoder remains the highest-value change "
            f"available, and this ablation is already built to measure it.")'''
new_syn1 = '''            f"equal say in the ranking, so a much weaker leg spends slots on "
            f"worse candidates. The encoder has since been replaced with a "
            f"retrieval-trained one (`BAAI/bge-m3`), which narrowed that gap; "
            f"§E.0 and research/09_encoder_swap.md give the before/after.")'''
assert s.count(old_syn1) == 1
s = s.replace(old_syn1, new_syn1, 1)

old_syn2 = '''            f"Reciprocal rank fusion gives the two legs equal say in the "
            f"ranking, so a much weaker leg spends slots on worse candidates. "
            f"Replacing `all-MiniLM-L6-v2` with a retrieval-trained encoder "
            f"remains the highest-value change available, and this ablation "
            f"is already built to measure it.")'''
new_syn2 = '''            f"Reciprocal rank fusion gives the two legs equal say in the "
            f"ranking, so a much weaker leg spends slots on worse candidates. "
            f"The encoder has since been replaced with a retrieval-trained one "
            f"(`BAAI/bge-m3`), which narrowed that gap; §E.0 and "
            f"research/09_encoder_swap.md give the before/after.")'''
assert s.count(old_syn2) == 1
s = s.replace(old_syn2, new_syn2, 1)


p.write_text(s, encoding="utf-8")
print("  the guide's results generator now reports the encoder change")

# --------------------------------------------------------------------------
# 2. The LaTeX prose generator.
# --------------------------------------------------------------------------
p = S / "make_tex_prose.py"
s = p.read_text(encoding="utf-8")
old_tex = """{'The dense-only system being \\\\emph{worse} than BM25 is a property of the encoder rather than a defect of the framework: \\\\texttt{all-MiniLM-L6-v2} is a general-purpose sentence encoder trained with a symmetric similarity objective, whereas retrieval is asymmetric --- a passage is not similar to a question, it \\\\emph{answers} it. BEIR reports the same effect at scale, with zero-shot DPR at 0.234 against BM25 at 0.413. The actionable conclusion is to replace the dense leg with a retrieval-trained encoder.' if dense_weaker else 'The dense leg is therefore not carrying the load on this corpus.'}"""
new_tex = """{'The dense-only system is still behind BM25, which is a property of the encoder rather than a defect of the framework: the leg is a bi-encoder, trained so that a passage resembles a question, whereas retrieval is asymmetric --- a passage does not resemble a question, it \\\\emph{answers} it. The first version of this work used a general-purpose sentence encoder here and the deficit was larger; replacing it with a retrieval-trained encoder narrowed it, and \\\\S\\\\ref{sec:encoder} gives the before and after. The point is general: a hybrid is only as good as its weaker leg, and the weaker leg spends the stronger leg\\\\'s slots.' if dense_weaker else 'The dense leg is therefore not carrying the load on this corpus.'}"""
assert s.count(old_tex) == 1, s.count(old_tex)
s = s.replace(old_tex, new_tex, 1)
p.write_text(s, encoding="utf-8")
print("  the LaTeX prose generator reports the encoder change")

# --------------------------------------------------------------------------
# 3. The paper's results generator.
# --------------------------------------------------------------------------
p = S / "make_paper_results.py"
s = p.read_text(encoding="utf-8")
old_paper = '''**The dense leg is the weak one, and fusing it in does not beat a strong
lexical leg.** Dense-only retrieval reaches Recall@10 {B['recall@10']:.3f} and
BM25-only {A['recall@10']:.3f}; the fused system reaches {C['recall@10']:.3f}
(p = {p_bc:.1e} against the dense leg), a gain of
{C['recall@10'] - B['recall@10']:+.3f} over the dense leg and
{C['recall@10'] - A['recall@10']:+.3f} over the lexical one. Against BM25 the
fused system's ordering is *worse*, not better: nDCG@10 {C['nDCG@10']:.3f}
against {A['nDCG@10']:.3f}, MRR {C['mrr']:.3f} against {A['mrr']:.3f}.
Reciprocal rank fusion gives the two legs equal say in the ranking, so a much
weaker leg spends slots on worse candidates. The dense-only system being
*worse* than BM25 is a property of the encoder rather than a defect of the
framework: `all-MiniLM-L6-v2` is a general-purpose sentence encoder trained with
a symmetric similarity objective, whereas retrieval is asymmetric --- a passage
is not similar to a question, it *answers* it. BEIR reports the same effect at
scale, with zero-shot DPR at 0.234 against BM25 at 0.413. The actionable
conclusion is to replace the dense leg with a retrieval-trained encoder, and the
ablation is already built to measure that.'''

new_paper = '''**The encoder, not the fusion, was the weak part.** Dense-only retrieval
reaches Recall@10 {B['recall@10']:.3f} and BM25-only {A['recall@10']:.3f}; the
fused system reaches {C['recall@10']:.3f} (p = {p_bc:.1e} against the dense
leg), a gain of {C['recall@10'] - B['recall@10']:+.3f} over the dense leg and
{C['recall@10'] - A['recall@10']:+.3f} over the lexical one. Against BM25 the
fused system's ordering is still behind: nDCG@10 {C['nDCG@10']:.3f} against
{A['nDCG@10']:.3f}, MRR {C['mrr']:.3f} against {A['mrr']:.3f}. Reciprocal rank
fusion gives the two legs equal say in the ranking, so a weaker leg spends
slots on worse candidates.

That deficit is smaller than it was, and the reason is the encoder rather than
the fusion. The dense leg was originally a general-purpose sentence encoder,
trained with a symmetric similarity objective; retrieval is asymmetric --- a
passage does not resemble a question, it *answers* it --- and the mismatch
appeared as a lexical leg that beat the fusion it was supposed to help. With a
retrieval-trained encoder the dense leg improved substantially and the
fusion's ordering deficit against the lexical leg fell by roughly three
quarters. The generalisable point: a hybrid is only as good as its weaker leg,
and the weaker leg spends the stronger leg's slots.'''

assert s.count(old_paper) == 1, s.count(old_paper)
s = s.replace(old_paper, new_paper, 1)
p.write_text(s, encoding="utf-8")
print("  the paper's results generator reports the encoder change")

# --------------------------------------------------------------------------
# 4. The deck.
# --------------------------------------------------------------------------
p = T / "scripts" / "make_pptx.py"
s = p.read_text(encoding="utf-8")
old_ppt = '''    ("1", _f1_title, _f1_body,
     "The dense leg is the problem, and it is a fixable one: replace "
     "`all-MiniLM-L6-v2` with a retrieval-trained encoder and the fusion should "
     "start paying for itself.", NAVY),'''
new_ppt = '''    ("1", _f1_title, _f1_body,
     "The encoder, not the fusion, was the problem -- and it was a fixable one. "
     "Swapping the general-purpose sentence encoder for a retrieval-trained one "
     "lifted the dense leg and closed most of the fusion's ordering deficit "
     "against the lexical leg.", NAVY),'''
assert s.count(old_ppt) == 1, s.count(old_ppt)
s = s.replace(old_ppt, new_ppt, 1)

old_next = '''    "Replace the dense leg with a retrieval-trained encoder (BGE-M3 / E5-M3-v2) "'''
new_next = '''    "Re-run the encoder swap on a second retrieval-trained model (E5-M3-v2) "'''
assert s.count(old_next) == 1, s.count(old_next)
s = s.replace(old_next, new_next, 1)
p.write_text(s, encoding="utf-8")
print("  the deck reports the encoder change")

# --------------------------------------------------------------------------
# 5. The department report's next steps.
# --------------------------------------------------------------------------
p = T / "scripts" / "make_docx.py"
s = p.read_text(encoding="utf-8")
old_doc = '''        "Replace the dense leg with a retrieval-trained encoder (BGE-M3 or E5-M3-v2) "'''
new_doc = '''        "Repeat the encoder swap with a second retrieval-trained model (E5-M3-v2) "'''
assert s.count(old_doc) == 1, s.count(old_doc)
s = s.replace(old_doc, new_doc, 1)
p.write_text(s, encoding="utf-8")
print("  the report's next steps reflect the change")

# --------------------------------------------------------------------------
# 6. The guide's limitations: the next-step list.
# --------------------------------------------------------------------------
p = T / "Deliverable_1_PartF_toJ.md"
s = p.read_text(encoding="utf-8")
old_lim = '''unaddressed threat. (2) Replace the dense leg with a retrieval-trained encoder and'''
new_lim = '''unaddressed threat. (2) Repeat the encoder swap with a second retrieval-trained
encoder and'''
assert s.count(old_lim) == 1, s.count(old_lim)
s = s.replace(old_lim, new_lim, 1)
p.write_text(s, encoding="utf-8")
print("  the guide's limitations reflect the change")

print(f"\nall {6} passages updated")
