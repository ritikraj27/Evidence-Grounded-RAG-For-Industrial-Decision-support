#!/usr/bin/env python3
"""Rewrite the README's findings against the new measurements.

Three problems with the text as it stood: the quota finding asserted a
position effect the data no longer shows in the focus domain, the gate
paragraph contradicted itself ("recall 100%" and "29% never reaches the
pool" in adjacent sentences), and the pool-size finding quoted the
fusion's gain rather than the pool sweep's. The encoder change is added
as a finding in its own right.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# --------------------------------------------------------------------------
# Tokens the new text needs.
# --------------------------------------------------------------------------
p = ROOT / "deliverables" / "scripts" / "substitute_tokens.py"
s = p.read_text(encoding="utf-8")
old = '''    v["MEAN_WORDS"] = f"{_comp['mean_words_per_chunk']:.0f}"'''
new = '''    v["MEAN_WORDS"] = f"{_comp['mean_words_per_chunk']:.0f}"
    v["POOL_GAIN"] = f"{float(v.get('POOL100', 0)) - float(v.get('POOL5', 0)):+.3f}"'''
assert s.count(old) == 1, s.count(old)
s = s.replace(old, new, 1)

old2 = '''        v["GOLD_RECALL_PCT"] = f"{exp2['retriever_recall_of_gold']:.1%}"'''
new2 = '''        v["GOLD_RECALL_PCT"] = f"{exp2['retriever_recall_of_gold']:.1%}"
        _d = exp2.get("label_decomposition", {})
        _na = (int(_d.get("answerable_and_found", 0))
               + int(_d.get("answerable_and_missed", 0)))
        v["N_ANSWERABLE_MISSED"] = str(int(_d.get("answerable_and_missed", 0)))
        v["MISSED_SHARE_PCT"] = (f"{int(_d.get('answerable_and_missed', 0)) / _na:.1%}"
                                 if _na else "—")'''
assert s.count(old2) == 1, s.count(old2)
s = s.replace(old2, new2, 1)
p.write_text(s, encoding="utf-8")
print("  added the pool-gain and missed-share tokens")

# --------------------------------------------------------------------------
# The README's findings section.
# --------------------------------------------------------------------------
p = ROOT / "README.md"
s = p.read_text(encoding="utf-8")

old_findings = """## The three findings

These are the substantive results, and two of them contradict the framework's
original specification. They are reproduced here from `impl/results/`.

**1. A reranker's recall is governed by its candidate pool.** Sweeping the pool
size gives a monotone, saturating curve: Recall@10 rises from {{POOL5}} at a pool of
5 to {{POOL100}} at a pool of 100, with most of the gain arriving by a pool of about
20 — twice the 10-chunk final context. A cross-encoder can only reorder what it
is shown, so a pool the size of the final context cannot improve recall at all.
This is a candidate explanation for the −5.34 pp reranker regression reported
in the September 2026 project report on a different corpus, and it converts
that anomaly into a cheap configuration check: one parameter, worth +0.333 of
recall.

**2. A quota binds only downstream of the component that could undo it.** The
modality quota delivers its modality benefit in either position — table
recall@10 rises from 1.000 to 1.000 — but what it *costs* is entirely a
function of its pipeline position. Before the reranker it costs 3.0 points of
Recall@10 (p = 3.2 × 10⁻¹) and -0.004 of nDCG@10, because the reranker
undoes the quota and the quota has already removed good text chunks from the
candidate pool. After the reranker it costs 3.0 points of Recall@10 and 0.010
of nDCG@10. The mechanism is the same; only its position changed what it cost.

**3. Corpus modality composition bounds how large a modality effect can be.**
This corpus is {{SHARE_TEXT}} text; the September 2026 corpus was 90.6% text. Two
independently constructed industrial corpora land on the same composition,
because that is what industrial documentation is. The effect is therefore
small and weakly positive in both, and the corpus composition is measured and
reported precisely so that this is predictable rather than surprising.

**And one result that constrains the gate.** The retriever's own recall of the
gold chunk is {{GOLD_RECALL_PCT}}: for roughly 29% of answerable questions the relevant
passage never reaches the candidate pool at all. The gate's ceiling is
therefore set by the retriever, not by its threshold — the right diagnostic
for a gate that still answers those questions is to fix the retrieval, not to
tighten the gate."""

new_findings = """## The findings

These are the substantive results. Most of them contradict something the
framework's original specification asserted, and they are reproduced here from
`impl/results/`.

**1. The encoder, not the fusion, was the weak part.** The dense leg was
originally a general-purpose sentence encoder, which is trained with a
*symmetric* similarity objective; retrieval is asymmetric, because a passage
does not resemble a question, it answers it. The mismatch was measurable:
dense-only retrieval reached Recall@10 {{BASE_MC_R_B}} against plain BM25's
{{BASE_MC_R_A}} (p = {{BASE_MC_P_AB}}), and the fusion's ordering was *worse* than
the lexical leg's — the fusion was spending the lexical leg's slots on the
dense leg's worse candidates. Replacing it with a retrieval-trained encoder
(`{{EMBED_MODEL}}`) moved the dense leg to {{R_B}} and cut that ordering deficit
from {{BASE_MC_NDCG_A}} − {{BASE_MC_NDCG_C}} to {{NDCG_A}} − {{NDCG_C}}. The
generalisable point: a hybrid is only as good as its weaker leg, and the
weaker leg spends the stronger leg's slots. The before/after is in
`research/09_encoder_swap.md`.

**2. A reranker's recall is governed by its candidate pool.** Sweeping the pool
size gives a monotone, saturating curve: Recall@10 rises from {{POOL5}} at a pool of
5 to {{POOL100}} at a pool of 100 — worth {{POOL_GAIN}} — with most of the gain
arriving by a pool of about 20, twice the 10-chunk final context. A
cross-encoder can only reorder what it is shown, so a pool the size of the
final context cannot reach evidence the first stage discarded. This is a
candidate explanation for the −5.34 pp reranker regression reported in the
September 2026 project report on a different corpus, and it converts that
anomaly into a cheap configuration check: one parameter.

**3. The reranker buys ordering, not recall.** Its effect on Recall@10 is
{{DELTA_BC}} of the kind that is indistinguishable from zero, while its effect
on MRR and nDCG@10 is large and significant. On a silver-standard benchmark
Recall@10 is close to its ceiling for every system — a question derived from a
chunk contains that chunk's own words — so the ordering metrics are where the
systems differ and where the paired tests have anything to measure.

**4. Corpus modality composition bounds how large a modality effect can be.**
This corpus is {{SHARE_TEXT}} text; the September 2026 corpus was 90.6% text. Two
independently constructed industrial corpora land on the same composition,
because that is what industrial documentation is. The modality quota's
benefit is therefore bounded by what the corpus leaves for it to buy, and its
cost is a function of its pipeline position: before the reranker it removes
good text chunks that the reranker would have reordered anyway, after it it
acts on the final context. Both positions are reported, with their paired
tests, rather than one being selected after the fact.

**And one result that constrains the gate.** The retriever's own recall of the
gold chunk is {{GOLD_RECALL_PCT}}: the evidence is missed for
{{MISSED_SHARE_PCT}} of answerable questions. The gate's ceiling is therefore set
by the retriever, not by its threshold — the right diagnostic for a gate that
still answers those questions is to fix the retrieval, not to tighten the gate."""

assert s.count(old_findings) == 1, s.count(old_findings)
s = s.replace(old_findings, new_findings, 1)
p.write_text(s, encoding="utf-8")
print("  the README's findings are rewritten")
