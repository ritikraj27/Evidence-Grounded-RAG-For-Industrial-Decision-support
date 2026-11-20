#!/usr/bin/env python3
"""Rewrite the prose that was written around the old encoder.

Every number here is a token, so the text states whatever the new
measurements say — including the case where the change did not help, which
is the outcome the thesis's framing is built to accommodate.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
T = ROOT / "deliverables" / "templates"

C3_OLD = """## C.3 The dense leg and why it underperformed

**What happened.** On our corpus, dense-only retrieval (Recall@10 = {{R_B}}) was
**worse** than BM25-only ({{R_A}}).

**Why.** `all-MiniLM-L6-v2` is a *general-purpose sentence encoder*, not a
retriever trained for the query–passage matching task. It was trained to make
semantically similar sentences close together — a symmetric objective — whereas
retrieval is asymmetric: a query and a passage are similar in a *directional*
sense (the passage answers the query), not a symmetric one. BEIR's main results table
reports the same effect at scale: across its 18 datasets, zero-shot DPR scores
0.234 against BM25's 0.413, a 43% relative deficit.

**The actionable consequence.** This is the highest-value change available to this
system: replace the dense leg with a model trained for retrieval — `BAAI/bge-m3`,
`intfloat/e5-m3-v2`, or `gte-modernbert-base` — and re-measure. The framework does
not depend on the choice; the *ablation* is what tells you which leg is carrying
the load."""

C3_NEW = """## C.3 The dense leg, and the encoder that was wrong for it

**What the dense leg is.** A bi-encoder embeds the query and each passage
*independently* and compares the two vectors. That is what makes a document
index possible — but it is also where the difficulty lives: the encoder has to
guess, from each side alone, that a question and a passage are related.

**The first choice was wrong for the job.** The original encoder,
`{{BASE_MC_ENC}}`, is a *general-purpose sentence encoder* trained with a
symmetric similarity objective: it is trained to place two sentences that mean
the same thing near each other. Retrieval is asymmetric. A passage does not
*resemble* a question; it *answers* it. On this corpus the mismatch was
measurable rather than theoretical: dense-only retrieval reached Recall@10
{{BASE_MC_R_B}} against plain BM25's {{BASE_MC_R_A}} (paired Wilcoxon,
p = {{BASE_MC_P_AB}}), and the fused system's ordering was *worse* than the
lexical leg's — nDCG@10 {{BASE_MC_NDCG_C}} against {{BASE_MC_NDCG_A}}. The
fusion was paying for the dense leg's slots and getting nothing back. BEIR's
main results table reports the same effect at scale: across its 18 datasets,
zero-shot DPR scores 0.234 against BM25's 0.413, a 43% relative deficit.

**The change, and one detail that is easy to get wrong.** The encoder is now
`{{EMBED_MODEL}}`, a retrieval-trained multilingual model: {{EMBED_DIM}}
dimensions, CLS pooling, a normalisation module, and a long-document training
strategy that handles the query/passages asymmetry in training rather than in
the prompt. **BGE-M3 takes no query instruction.** The smaller
instruction-tuned encoders (E5, GTE, BGE-v1.5) want "Represent this sentence for
searching relevant passages: " in front of the query; BGE-M3's model card says
explicitly that it "no longer requires adding instructions to the queries".
The configuration therefore leaves `query_prefix` empty — and keeps the field
configurable, because the next encoder may well want one.

**What changed.** {{ENCODER_VERDICT}} Dense-only retrieval now reaches
Recall@10 {{R_B}} against BM25's {{R_A}}, and the fused system reaches
{{R_C}} with nDCG@10 {{NDCG_C}} against BM25's {{NDCG_A}}.

**The generalisable lesson.** A hybrid retriever is only as good as its worse
leg, and "hybrid" is not a free upgrade: giving a weak leg half the say in the
ranking costs the strong leg's ordering. If the dense leg is not
retrieval-trained, it should not be in the fusion at all — and the way to find
out is to measure the two legs separately, which is what the ablation does."""

A4_OLD = """- **The dense leg is the weak one.** A general-purpose sentence encoder
  (`all-MiniLM-L6-v2`) is *worse than BM25* on this corpus. This is a real, reported
  finding in the literature (DPR loses 43% to BM25 on BEIR) and it is the single most
  actionable thing to know about this stack."""

A4_NEW = """- **The encoder, not the fusion, was the weak part.** With a general-purpose
  sentence encoder the dense leg was *worse than BM25* on this corpus, and the
  fusion's ordering was worse than BM25's too — the fusion was paying for the
  dense leg's slots and getting nothing back. Replacing it with a
  retrieval-trained encoder ({{EMBED_MODEL}}) is what the framework's own
  ablation said to do, and §C.3 reports what that changed."""

Q5_OLD = """**Q5. Your dense retriever is worse than BM25. Why is that not fatal?**
Because it is a finding, not a defect. `all-MiniLM-L6-v2` is a general-purpose
sentence encoder, not a retrieval-trained model, and the retrieval objective is
asymmetric in a way the sentence-similarity objective is not. The BEIR benchmark
reports the same effect — DPR zero-shot at 0.234 versus BM25 at 0.413. The
framework is unaffected because fusion takes the *union* of the two shortlists;
the actionable conclusion is to replace the dense leg with a retrieval-trained
encoder and re-measure."""

Q5_NEW = """**Q5. Your dense retriever was worse than BM25. Why is that not fatal?**
Because it was a finding, not a defect — and because the framework is
instrumented well enough to act on it. `{{BASE_MC_ENC}}` is a general-purpose
sentence encoder, not a retrieval-trained model, and the retrieval objective is
asymmetric in a way the sentence-similarity objective is not. The BEIR benchmark
reports the same effect — DPR zero-shot at 0.234 versus BM25 at 0.413.

The part worth saying plainly: the first version of this thesis *measured*
that and then kept the weak encoder. The ablation exists to tell you which
leg is carrying the load, so the correct response was to replace it, not to
report around it. The dense leg is now `{{EMBED_MODEL}}`, and §C.3 reports
what that changed: {{ENCODER_VERDICT}} The general lesson is the one the
framework teaches: fusion takes the *union* of two shortlists, so a weak leg
does not fail loudly — it just spends the other leg's slots. Measure the legs
separately, and do not assume a hybrid is an upgrade."""


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
    total += apply(T / "Deliverable_1_Part1_Content.md",
                   [(C3_OLD, C3_NEW), (A4_OLD, A4_NEW)])
    total += apply(T / "Deliverable_1_PartF_toJ.md", [(Q5_OLD, Q5_NEW)])
    print(f"\n{total} replacements applied")
    return 0


if __name__ == "__main__":
    sys.exit(main())
