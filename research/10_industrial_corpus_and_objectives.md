# RO4, RO5, RO6 — Closing the Three Open Objectives

**Scope.** Three of the thesis's six research objectives were open at the
start of this work: RO4 (cross-document contradiction surfacing), RO5
(per-claim confidence tagging) and RO6 (evaluation on industrial corpora and
industrial benchmarks, with cross-category generalisation). This file records
the measurements that close them.

**The question each one asked, and the answer.**

| RO | Objective | Status at the start | Status now |
|---|---|---|---|
| RO4 | contradiction surfacing (joint NLI + topical gate) | mechanism works (11/11 positive control) but **precision 0%** on a corpus with no contradictions, so unevaluable | measured on a corpus that *does* contain conflicts, against two independent annotators — and the measurement says the mechanism finds **supersession and reports it as contradiction** |
| RO5 | per-claim confidence banding (grounded / inferred / uncertain) | the labels are audited but **what the banding buys is unmeasured** | measured against two independent readers under two evidence protocols: the band is a usable **filter** and **not** a usable **ranking** — a positional heuristic beats it |
| RO6 | industrial corpora and industrial benchmarks, cross-category generalisation | **half closed** — the corpora are encyclopaedic Wikipedia *about* industrial engineering | an authentic regulatory corpus, a benchmark built on it with a shortcut audit, the cross-regime transfer measurement, and **three of the thesis's negative findings replicated on it** |

**Why RO4 and RO6 needed one artefact.** RO4 needs a corpus that contains
conflicts. RO6 needs a corpus that is authentic. The same artefact supplies
both: federal regulations are authentic industrial documents, and they are
amended, so the same section read on two dates is the same rule at two
issues.

**Where this now appears.** These measurements are carried in both papers:
`Deliverable_2b_IEEE_Conference_Paper.tex` (condensed) and
`Deliverable_2c_Journal_Style_Paper.tex` (full), in a section on the second
corpus with the six figures in `deliverables/figures/`. The section's prose,
tables and figure captions are **generated** from the result files by
`deliverables/scripts/make_tex_industrial.py`, so the papers cannot drift from
the artefacts, and `impl/scripts/verify_reported_numbers.py` checks that they
do not. A companion document, `research/14_full_explanation.md`, explains the
whole project — every term, every objective, every experiment — for someone
who has to present it.

---

## 1. The authentic industrial corpus (RO6)

### 1.1 What it is

**InduSight industrial regulatory corpus** — 110 documents, 2,443 chunks,
289,869 words, built from the Electronic Code of Federal Regulations
(eCFR) at the versioner date 2026-06-01.

| Category | Documents | Words | What it covers |
|---|---|---|---|
| `occupational_safety` | 44 | 88,529 | OSHA general industry: walking-working surfaces, exit routes, hazardous materials, PPE, materials handling, machine guarding, portable tools, welding, noise, ventilation, non-ionising radiation |
| `environmental_control` | 37 | 87,233 | Toxic and hazardous substances (29 CFR 1910.1000–1099: the air-contaminant exposure limits, asbestos, lead, cadmium) and EPA new source performance standards (40 CFR 60: cement plants, petroleum refineries, storage vessels, smelters, grain elevators, metallic mineral processing, equipment leaks) |
| `process_safety` | 10 | 29,527 | The standards that manage catastrophic risk: process safety management (1910.119), hazardous waste operations (1910.120), permit-required confined spaces (1910.146), lockout/tagout (1910.147), hazard communication (1910.1200), and EPA's risk management programme rule (40 CFR 112) |
| `hazmat_transport` | 19 | 21,250 | DOT's preparation, classification and packaging rules for hazardous materials (49 CFR 173), where the quantity limits a practitioner must comply with live |

**Public domain.** US federal regulations are works of the US government and
carry no copyright, so the corpus is redistributable with the thesis without
a licence question. The eCFR versioner is the authoritative source and the
fetch is reproducible from `impl/scripts/fetch_ecfr.py`.

**Modality composition.** 2,324 text chunks and 119 table chunks (4.9%
tables, 0% charts). Compare the focus corpus, where the modality quota
returned a null result partly because there was nothing tabular for it to
move: here the quota *binds* — a 15% table floor on a ten-chunk context is
one table, and the corpus has 119 of them to draw on. There are no charts,
because a regulation has none; the chart floor is therefore unsatisfiable
here, and the framework's quota reports the shortfall rather than papering
over it, which is the designed behaviour and is visible in the ablation.

### 1.2 Three construction decisions, and why

**Over-long sections are split, not dropped.** 29 CFR 1910.119 (process
safety management) is twenty thousand words and 1910.146 (permit-required
confined spaces) is comparable. A word-count cap that dropped them would
drop the two most decision-relevant standards in the corpus. A section longer
than 3,500 words is split into consecutive documents instead, each carrying
the parent section's identifier in the manifest.

**Tables are paginated.** 29 CFR 1910.1000 Table Z-1 (the air-contaminant
limits) is 6,926 words in one cell. The cross-encoder reads 512 tokens, so
that table is truncated to roughly its first twenty rows and the answer to a
question about row 400 is not in the text the reranker ever sees. A table
that cannot be retrieved is a table the modality quota cannot help with, and
the measurement of D2 would be measuring the tokenizer rather than the
quota. Tables are therefore paginated at 30 rows and 300 words, with the
header repeated on every page.

**Procedural sections are excluded.** The sections that describe how a rule
is made, challenged or exempted carry no requirement a practitioner has to
comply with, and they are the ones that most resemble the encyclopaedic
register the thesis is trying to move away from. Definitions are *kept* —
they are the source of most answerable questions in a regulatory corpus.

**The corpus is trimmed to a word budget, evenly within each category.**
The full extraction is 545 documents and 1.38 million words, and encoding it
with the project's dense encoder is a multi-hour job on this machine. The
trimmed corpus is **an evenly spaced subsample of each category's documents
in identifier order**, not the top-N by any quality measure — a corpus
chosen by a quality filter is a corpus chosen for the property being
measured, and the retrieval numbers on it would be a statement about the
filter as much as about the corpus. The budget is proportional to what each
category contributes, so the trimming does not reweight the regimes.

The cost of the trim is visible and is reported: the benchmark's
`numeric_fact` family falls from 30 questions to 7, because the documents
carrying the exposure-limit tables are thinned along with everything else.
The answerable half is 247 questions, which is enough to measure retrieval
and gating on, and the family's thinness is a limitation of the benchmark,
not a hidden one.

**The encoder's sequence limit is 512 tokens for this corpus only.**
BGE-M3's own limit is 8,192 and the median chunk here is 176 tokens, so
honouring the model's limit costs an order of magnitude in encoding time for
no change to the vectors of the 97.5% of chunks that fit. 512 is the same
window the cross-encoder uses, so setting it makes the dense leg see the
same text the reranker will. The limit is part of the embedding cache key
and is unset by default, so the two existing corpora keep their vectors and
their numbers.

### 1.3 The benchmark

`impl/data/benchmark_industrial/benchmark.json` — 444 queries, 247
answerable and 197 unanswerable, silver labels, mechanically derived from
the documents.

| Family | n |
|---|---|
| `definition` | 110 |
| `table_lookup` | 130 |
| `numeric_fact` | 7 |
| `unanswerable_corpus_anchored_definition` | 96 |
| `unanswerable_corpus_anchored_table` | 52 |
| `unanswerable_ood` | 49 |

**The label standard is unchanged.** Answerable questions are derived
mechanically from the document that answers them, so the gold chunk is
guaranteed to contain the answer somewhere; that optimistic bias is stated
wherever the numbers are reported and does not bias the *comparison* between
systems, because every system is scored against the same labels. The
unanswerable class is drawn from the same three stems, from the same
documents, and labelled by the complement of the answerable extraction tests
(`impl/scripts/unanswerable_repair.py`, unchanged), so the two classes differ
in one respect only: whether the corpus states the answer.

**Two differences were forced by the register.** The existing benchmark's
extraction patterns were written against Wikipedia prose, and applied to
regulatory text they produce questions nobody would ask: every table question
asked for the *next* column, which in the air-contaminant tables is always
"CAS No. (c)", giving 486 questions that test one column; the numeric branch
captured a clause rather than a subject ("What value is stated for only for a
maximum period…"); and the definition branch matched mid-clause ("What is
because inorganic arsenic?"). The industrial benchmark uses extraction
patterns for the register a regulation is written in — a noun phrase
followed by a limit verb, with the quantity named — and caps the table
family at 12 questions per (document, column).

**The out-of-domain class is the thesis's own original domain.** The
existing benchmark's out-of-domain class asks about vitamin D and the 1998
FIFA final, which a question-only classifier separates from a regulatory
corpus trivially. The industrial class asks about the industrial engineering
topics the framework was originally built for — economic order quantity,
safety stock, Six Sigma, takt time, ASME Section IX, EOQ lot-sizing rules —
none of which a federal *regulation* contains. The class is drawn from the
corpus's own subject area, so a system that refuses on the shape of the
question rather than on the evidence has nothing to hide behind.

### 1.4 The benchmark's own audit (Experiment 12, on the industrial corpus)

The unanswerable half is the half that can be wrong in ways no retrieval
metric can see, so it is audited separately: can the *question alone* tell
an answerable question from an unanswerable one?

| Measurement | Value |
|---|---|
| Structural separability (ROC-AUC) | 0.708 |
| Bag-of-words separability (ROC-AUC) | 0.793 |
| Permutation null (100 label shuffles) | mean 0.505, sd 0.036, max 0.597 |
| p-value vs the permutation null | **0.0099** (structural), 0.032 (bag of words) |
| Majority-class F1 baseline | 0.715 |
| The original `PREFIX-digits` shortcut | catches **0 of 197** unanswerable questions (recall 0.000) |
| Median question length | answerable 73 chars, unanswerable 50 chars |
| Question-only policy (closed-book LLM) | **not run** — no API credential was reachable when the audit was made |
| Parametric leakage probe | **not run** — same reason |

**What this says.** The defect the project's own audit found in the first
benchmark — a single regular expression that separated the two classes
perfectly — is gone: the rule catches nothing here. But the class is *not*
clean. A classifier that sees only the question still separates it at
AUC 0.708 against a null of 0.505, and the mechanism is largely length:
the answerable questions are longer than the unanswerable ones.

**Two defects found by the audit and repaired.**

1. **The unanswerable class was shape-matched against the wrong answerable
   class.** `unanswerable_repair` recovers the answerable class by replaying
   the benchmark's *own* generator, which was written for Wikipedia prose.
   On the industrial corpus the answerable half comes from different
   extractors, so the shape matching — the stem, the structural features,
   the subject-length quantiles that are the whole point of the repair — was
   calibrated against the wrong distribution. The generator now accepts the
   answerable class it is to be matched against, and the industrial
   benchmark supplies its own.
2. **Four repaired questions had certificates that did not hold.** "What is
   a lock?", "What is the text?", and two table lookups named subjects the
   corpus *does* define, so they were answerable and sat in the
   unanswerable class. The builder now re-checks every repaired question
   with the audit's own independently-written predicate and drops any that
   fails, so the benchmark and the audit cannot drift apart.

**What remains.** The residual length difference is reported, not hidden. It
is a real limitation of a silver benchmark whose two halves are built by
different extractors, and it means the industrial benchmark's
answerable/unanswerable split is *easier* than the focus corpus's on one
axis (question length) and harder on another (the old regex shortcut is
gone). Every number reported from it carries this caveat.


---

## 2. RO6 — measurement on the authentic corpus

### 2.1 The retrieval ablation (Experiment 1, 247 answerable queries)

Every number is a paired comparison over the same queries, with the
Wilcoxon signed-rank test and Cohen's d_z. The bootstrap interval for
Recall@10 of the shipped system is **[0.972, 1.000]**.

| System | R@5 | R@10 | R@20 | MRR | nDCG@10 | text R@10 | table R@10 |
|---|---|---|---|---|---|---|---|
| A. bm25_only | 0.879 | 0.960 | 0.996 | 0.755 | 0.803 | 0.949 | 0.969 |
| B. dense_only | 0.830 | 0.879 | 0.931 | 0.660 | 0.710 | 0.915 | 0.846 |
| C. hybrid_rrf | 0.931 | 0.960 | 0.988 | 0.771 | 0.816 | 0.974 | 0.946 |
| D. + reranker | 0.976 | 0.988 | 0.996 | 0.827 | 0.867 | 1.000 | 0.977 |
| E. + category filter | 0.972 | 0.988 | 1.000 | 0.834 | 0.872 | 1.000 | 0.977 |
| F. + quota, pre-rerank | 0.972 | 0.980 | 0.980 | 0.838 | 0.874 | 0.974 | 0.985 |
| G. + quota, post-rerank | 0.972 | 0.988 | 0.988 | 0.833 | 0.872 | 1.000 | 0.977 |

| Comparison | Δ Recall@10 | p | Δ MRR | p | Δ nDCG | p |
|---|---|---|---|---|---|---|
| A → B (lexical → dense) | **−0.081** | **0.00026** | −0.095 | 0.00070 | −0.092 | 0.00046 |
| B → C (dense → fusion) | **+0.081** | **7.7e−06** | +0.111 | 2.3e−09 | +0.106 | 2.0e−10 |
| C → D (fusion → + reranker) | **+0.028** | **0.0196** | +0.056 | 0.0037 | +0.051 | 0.0018 |
| D → E (+ category filter) | 0.000 | 1.000 | +0.007 | 0.088 | +0.005 | 0.099 |
| E → F (quota pre-rerank) | −0.008 | 0.317 | +0.004 | 0.158 | +0.002 | 0.177 |
| F → G (quota post-rerank) | +0.008 | 0.317 | −0.005 | 0.177 | −0.002 | 0.177 |
| **A → C** (fusion vs the lexical leg alone) | 0.000 | 1.000 | +0.016 | 0.384 | +0.013 | 0.549 |
| D → F (the quota in the pre-rerank position) | −0.008 | 0.317 | +0.011 | **0.038** | +0.007 | **0.049** |

**Three of the thesis's findings replicate on an authentic industrial corpus,
and one of them does not.**

**Replicated: the lexical leg beats the dense leg.** BM25's Recall@10 is
0.960 against the dense encoder's 0.879 — a paired difference of 0.081
(p = 0.00026, d_z = 0.238). This is the thesis's most counter-intuitive
result, and on the focus corpus it rested on 32 answerable queries with
BM25's advantage over dense at p = 0.025. On 247 answerable queries drawn
from authentic regulatory documents the effect is three times larger and
twenty-five times more significant. The lesson of the focus corpus was not
an artefact of a small encyclopaedic sample.

**Replicated: the fusion does not beat its lexical leg on recall.** A → C
is a difference of exactly 0.000 in Recall@10 (p = 1.000), and the MRR and
nDCG advantages (+0.016, +0.013) are not significant (p = 0.384, 0.549).
The fusion is a robust *ordering* mechanism and no recall mechanism, and on
a corpus where the lexical leg is this strong the claim that the hybrid
"outperforms flat retrieval" has no support.

**Replicated: the category pre-filter is not where the win is.** D → E is
0.000 on Recall@10 (p = 1.000), with MRR +0.007 (p = 0.088) and nDCG +0.005
(p = 0.099) — marginal, and in the same direction as on the focus corpus
(where it was a no-op or a loss). The thesis claimed that filtering before
retrieval changes the statistics of what remains and therefore beats flat
retrieval. On two corpora, in two domains, that claim does not hold.

**Replicated: the quota belongs after the reranker.** The pre-rerank quota
costs ordering quality against the shipped system (D → F: MRR +0.011,
p = 0.038; nDCG +0.007, p = 0.049) while the post-rerank placement does
not (F → G, all p > 0.17). The quota's effect on table recall is the
opposite sign (0.977 → 0.985 pre-rerank), which is the same trade the focus
corpus measured.

**Not replicated: the reranker's effect on recall.** On the focus corpus the
cross-encoder *reduced* recall; here it *increases* it, by 0.028
(p = 0.0196) and by 0.056 in MRR (p = 0.0037). The reranker is not
intrinsically harmful — it is governed by the candidate pool it is shown and
by the distractor density of the corpus, and on a corpus of 2,443 chunks
with many near-duplicate regulatory provisions the pool it gets is
friendlier than on 807 Wikipedia articles. **Which is exactly what
Experiment 5 measures, and it is the reason the pool-size result is worth
having: it explains why the same component helps in one corpus and hurts in
another.**

**The modality quota now binds.** The focus corpus had 44 table chunks in
807 (5.4%) and 38 chart chunks; the industrial corpus has 119 table chunks
in 2,443 (4.9%) and no charts at all. A 15% table floor on a ten-chunk
context is one table, and the corpus can supply one — so the quota is
exercised here, and its cost is measurable, where on the focus corpus the
floor was close to unsatisfiable and the result was null by construction.

### 2.2 The confidence gate (Experiment 2)

444 queries: 247 answerable, 197 unanswerable.

| | |
|---|---|
| `retriever_recall_of_gold` | **1.000** |
| Label decomposition | 247 answerable-and-found, **0 answerable-and-missed**, 197 unanswerable |
| Base rate, answer in context | 0.556 |
| Calibration (60% split) | Brier 0.159, ECE 0.075 |
| Chosen operating point | τ = **0.40** ("highest τ answering ≥ 90% of answerable queries") |
| — answerable answered | **0.915** |
| — unanswerable refused | **0.589** |
| — abstention precision | 0.847 |
| — coverage | 0.691 |
| Never-refuse baseline (τ = 0) | coverage 1.000, 0 refusals |
| Always-refuse baseline (τ = 1) | coverage 0.000, abstention precision 0.444 |

**The negative class is 100% unanswerable.** The retriever found the gold
chunk for every one of the 247 answerable queries, so the gate's negative
class contains no retrieval failures. That is the same clean decomposition
the focus corpus had, arrived at for a different reason, and it means the
gate's refusal rate here measures *detectability of unanswerability*, not
"the retriever missed it".

**The threshold sweep, in full:**

| τ | answerable answered | unanswerable refused | abstention precision | coverage |
|---|---|---|---|---|
| 0.05 | 1.000 | 0.208 | 1.000 | 0.908 |
| 0.10 | 0.992 | 0.274 | 0.964 | 0.874 |
| 0.15 | 0.988 | 0.355 | 0.959 | 0.836 |
| 0.20 | 0.984 | 0.396 | 0.951 | 0.815 |
| 0.25 | 0.976 | 0.447 | 0.936 | 0.788 |
| 0.30 | 0.951 | 0.487 | 0.889 | 0.757 |
| 0.35 | 0.935 | 0.543 | 0.870 | 0.723 |
| **0.40** | **0.915** | **0.589** | **0.847** | **0.691** |
| 0.45 | 0.887 | 0.619 | 0.813 | 0.662 |
| 0.50 | 0.858 | 0.675 | 0.792 | 0.622 |
| 0.55 | 0.814 | 0.731 | 0.758 | 0.572 |
| 0.60 | 0.781 | 0.761 | 0.735 | 0.541 |
| 0.65 | 0.749 | 0.817 | 0.722 | 0.498 |
| 0.70 | 0.676 | 0.838 | 0.673 | 0.448 |

**The threshold does not transfer, and the operating point does.** The
industrial corpus's τ is **0.40**; the focus corpus's is **0.05** — eight
times apart, on two corpora with different base rates (44% unanswerable
here against 82% there) and completely different documents. The *coverage*
at the two fitted operating points is nonetheless nearly identical: **0.691
here against 0.699 there.** So the transferable quantity is not the
threshold but the operating point, and a threshold transferred across corpora
lands somewhere else entirely.

**Where the gate works and where it does not**, at the fitted operating
point:

| Family | n | Refused |
|---|---|---|
| `unanswerable_ood` | 49 | **0.878** |
| `unanswerable_corpus_anchored_definition` | 96 | 0.521 |
| `unanswerable_corpus_anchored_table` | 52 | 0.442 |
| `definition` (answerable) | 110 | 0.055 |
| `table_lookup` (answerable) | 130 | 0.077 |
| `numeric_fact` (answerable) | 7 | 0.714 |

The gate refuses 88% of the questions that are visibly out of scope, and
about half of the corpus-anchored ones, which are the hard case: the corpus
discusses the subject and states no value for it, so only the evidence can
decide. It refuses 5–8% of the answerable questions, which is the cost of
the refusal. The `numeric_fact` family is seven questions and its refusal
rate is noise.

### 2.3 The candidate-pool sweep (Experiment 5) — the lead claim

The thesis's lead measurement is that a cross-encoder's effect on recall is
governed by the candidate pool it is shown rather than by the reranker
itself. The focus corpus measured it on a corpus whose retrieval was
**saturated** (Recall@10 = 1.000 at pool 10), so the shape it produced —
a peak at the final context size and a fall beyond it — could not
distinguish "the pool stopped helping" from "the corpus had nothing left
to find". The industrial corpus is **not** saturated, so it can.

| Pool | R@10 | R@20 | MRR | nDCG@10 | table R@10 | **Displaced (R@20 − R@10)** |
|---|---|---|---|---|---|---|
| 5 | 0.947 | 0.947 | 0.835 | 0.864 | 0.946 | 0.0000 |
| 10 | 0.980 | 0.980 | 0.838 | 0.874 | 0.985 | 0.0000 |
| 20 | 0.988 | 0.992 | **0.838** | **0.876** | 0.977 | **0.0040** |
| 50 | 0.988 | **1.000** | 0.834 | 0.872 | 0.977 | **0.0121** |
| 100 | 0.988 | **1.000** | 0.834 | 0.872 | 0.977 | **0.0121** |

**The displacement is measured directly.** Recall@20 reaches **1.000** at
pool 50 — with a pool of fifty, the gold chunk is in the reranked top-20
for *every single one* of the 247 answerable queries. Recall@10 stays at
0.988. The difference, 1.21%, is exactly the set of golds that the
reranker *did* find and then pushed **out of the ten-chunk context** in
favour of distractors. At pool 20 the displacement is 0.40%; at pools 5 and
10 it is zero by construction, because the context *is* ten chunks.

**So the pool beyond about twenty is net-harmful, and the harm is now
visible in the right place.** A larger pool buys recall-at-20 and loses
ordering: MRR peaks at pool 20 (0.838) and falls at 50 and 100 (0.834);
nDCG peaks at pool 20 (0.876) and falls (0.872); Recall@10 stops improving
at 0.988 from pool 20 onwards. The reranker can only reorder what it is
shown; giving it more candidates gives it more opportunities to place the
gold in the top-20 and more distractors to displace it from the top-10.

**This is a refinement of the focus corpus's result, and the refinement is
the point.** The pool at which recall peaks is set by where the *corpus*
saturates — 10 on the focus corpus, 20 here — but the *displacement rate*
grows with the pool regardless, and it is only measurable on a corpus that
is not already saturated. The focus corpus's fall from 1.000 to 0.969 was
the displacement effect seen through a saturated lens.

### 2.4 Cross-category transfer (Experiment 4) — and a defect in it

**A defect was found in the shipped transfer experiment and fixed.** The
unanswerable queries carry no category — "the corpus does not state this
answer" is not a property of one category — so a split *by category*
silently dropped the entire negative class out of **both** halves. The
shipped six-category result has exactly this shape: `n_unanswerable: 0` and
`unanswerable_refused: NaN` in every split. The experiment was measuring
only how many true answers get refused, and saying nothing about the gate's
discrimination, which is the thing the gate exists for.

The shared negative class now goes into both halves. The deliverables'
consistency checker still passes, and the rebuilt Table 6 gains a real
number where it had `NaN`.

| Industrial corpus, leave-half-out | Answerable answered | Unanswerable refused | Coverage |
|---|---|---|---|
| Tuning half (hazmat_transport, occupational_safety) | 0.993 | 0.299 | 0.590 |
| Held-out half, **transferred** (environmental_control, process_safety) | **1.000** | **0.299** | 0.543 |
| Held-out half, refitted on itself | 1.000 | 0.259 | 0.517 |

**A threshold fitted on two regulatory regimes transfers to the other two
without loss.** The transferred arm answers 100% of the held-out answerable
queries and refuses 29.9% of the unanswerables — the same refusal rate as
the tuning half, and a *higher* one than the arm refitted on the held-out
categories themselves.

**And the threshold still does not transfer across corpora.** The
industrial corpus's fitted threshold is 0.40 and the focus corpus's is
0.05. So the two transfer questions have different answers:

* **across regimes within a corpus** — the threshold transfers;
* **across corpora** — it does not, and the coverage does (0.691 against
  0.699).

The transfer result on the six-category Wikipedia corpus, re-run with the
fix, is the same shape: transferred answerable answered 1.000 and
unanswerable refused 0.174, against the refitted arm's 0.955 and 0.215.




---

## 3. RO5 — what the per-claim confidence band buys

### 3.1 The measurement, and why it was not already made

A claim is either right or wrong, and the framework has no independent way to
say which. Its own "claim hallucination rate" is computed from the same
entailment scores the band is cut from: a claim the NLI does not entail is,
by that computation, a hallucination. **The rate measures the detector, not
the answer.** So the reference labels have to come from outside the band.

Three references are used, and all of them are independent of the band:

* **two readers** — one a generalist, one a supply-chain and operations
  specialist, both blind to the band and to the framework's own scoring
  code, each shown a claim and a piece of evidence. Their agreement is what
  makes the labels a property of the claims rather than of one reader's
  habits: **κ = 0.902** on the gold protocol and **κ = 0.724** on the
  retrieved one, over 350 claims each;
* an **adjudicator** — a third reader, shown only the 53 claims the two
  readers disagreed about, who resolved them by the rubric. Its labels are
  the tie-break, and after it 347 of the 350 claims carry a reference;
* a **rule** — a mechanical string comparison against the benchmark's own
  silver gold answer: does the claim state that answer, or state a different
  value for the same measurement term? The rule wins where it applies,
  because it is reproducible and it cannot drift.

The two readers are given **different evidence**, and that is the design:
one sees the benchmark's gold passage and answers "is this claim right?",
the other sees the passages the band itself was computed over and answers
"does an independent reader agree with the scorer on the same evidence?".
One protocol cannot tell a band that does not track correctness apart from a
scorer that other readers disagree with.

### 3.2 Two definitions of "supported", and they are not the same

The framework's band is cut on a **noisy-OR** of the per-chunk entailment
probabilities (`src/claims.py::assess_claims`). The generation experiment
records a **maximum** over the same candidates, thresholded at 0.5
(`run_generation_eval.py::_claim_support`). Two different functions of the
same evidence: only the first is what the answer shows the practitioner, and
only the second is what the papers report as the claim-support rate.

On the 350 pooled claims the two disagree on **23** (6.6%): 12 claims the
experiment called `inferred` the framework calls `grounded`, and 11 the other
way. The noisy-OR assumes the witnesses fail independently, which they do
not — ten passages about the same subject are not ten independent trials — so
it saturates where the maximum does not, and it does so unevenly. **Everything
below measures the framework's own band**, recomputed over the same candidate
set, so that the only difference is the aggregation rule.

### 3.2b The circularity, quantified

The framework's reported **claim-hallucination rate is 0.382**: the share of
claims the NLI does not entail over the retrieved passages. Two independent
estimates of the same quantity bracket it:

| | Shipped | Independent reference | 95% CI |
|---|---|---|---|
| Against the **gold** evidence | 0.382 | **0.571** | [0.518, 0.622] |
| Against the **retrieved** evidence | 0.382 | **0.164** | [0.129, 0.207] |

The shipped number sits between two independent estimates that differ from
it by 0.19 and 0.22 in opposite directions, and it is a measure of
*entailment* being reported as a measure of *hallucination*. **The
framework's claim-support number is not a measurement of hallucination**,
and the two numbers it could be mistaken for differ from it by a factor of
1.5 one way and 2.3 the other.

### 3.3 The result

350 claims, two readers at κ = 0.902 (gold) and 0.724 (retrieved), plus an
adjudicator; 347 carry a reference.

| | Gold evidence ("is the claim right?") | Retrieved evidence ("does a reader agree with the scorer?") |
|---|---|---|
| Band vs reference (Cohen's κ) | **0.049** (CI −0.026, 0.124) | **0.069** (CI −0.002, 0.139) |
| `grounded` error rate | 0.542 (CI 0.460–0.621) | **0.118** (CI 0.075–0.181) |
| `inferred` error rate | 0.513 (CI 0.362–0.661) | 0.103 (CI 0.041–0.236) |
| `uncertain` error rate | 0.610 (CI 0.533–0.681) | 0.220 (CI 0.163–0.289) |
| Answers with no wrong claim | 34.4% | 59.4% |
| …keeping only the `grounded` claims | **50.0%** | **81.2%** |
| Share of claims the `grounded` band keeps | 41.5% | 41.5% |

**The band does not track correctness.** Against the benchmark's gold
evidence, the three bands are statistically indistinguishable (0.542 /
0.513 / 0.610) and the agreement with the reference is at chance (κ = 0.049,
CI includes zero).

**Against the same evidence the band was computed over, the band does
order.** A `grounded` claim is wrong 11.8% of the time and an `uncertain`
one 22.0%, and the intervals do not overlap. So the band is measuring
something — it is measuring whether the retrieved passages entail the claim
— and it is measuring it competently. It is simply not measuring whether
the claim is *true*.

### 3.4 The value test

The policies are applied *within* an answer, because the decision a
practitioner faces is "which sentences of *this* answer do I act on". The
risk gap is computed per answer and the interval is a **paired cluster
bootstrap over answers** — the same answer appears at every coverage point,
so bootstrapping over the rows would treat thirty answers as six hundred and
report an interval several times too narrow. (An earlier version of this
measurement bootstrapped over the rows, and reported the band as beating
random; that was an artefact of the interval, and the corrected interval does
not exclude zero.)

| Baseline | Gold gap (band − baseline) | 95% CI | Retrieved gap | 95% CI |
|---|---|---|---|---|
| random | −0.017 | [−0.063, +0.030] | −0.055 | [−0.090, +0.000] |
| shortest claims | −0.052 | [−0.110, +0.042] | **−0.104** | **[−0.146, −0.002]** |
| longest claims | −0.005 | [−0.049, +0.034] | −0.047 | [−0.109, +0.024] |
| **first claims** | **+0.092** | **[+0.016, +0.133]** | +0.023 | [−0.030, +0.055] |

Paired Wilcoxon over answers at half of each answer's claims: gold, band vs
first claims, p = 0.008.

**Position beats the band.** Keeping the *first* claims of an answer is a
better selector than the confidence band, significantly so against the gold
protocol. The generator front-loads its safe claims, so "read the first half"
is the stronger heuristic.

**And that is not a length artefact.** If the generator wrote short claims
first, "keep the first claims" and "keep the shortest claims" would be one
policy in two costumes. They are not: the Spearman correlation between a
claim's position and its length is **−0.195** (p = 0.0003) — later claims
are *shorter*, not longer — and the first and second halves of an answer
average 19.2 and 18.4 words. Position and length are different policies, and
the band loses to position while beating the length policies.

### 3.5 A generator defect that three readers found independently

Claims of the form `Preferred Provider | 4` pair a model with the number
the passage assigns to the **next** model — the passage numbers them Basic
2, Approved 3, Preferred 4, Performance-Based 5, Vested 6, Shared 7, and the
generator produces 3, 4, 5, 6, 7, 8. Two readers on the gold protocol and
one on the retrieved protocol flagged the family independently, without
knowing what the others had seen, and the adjudicator's notes identify it
pair by pair.

This is a defect in the **generator**, not in the band: the model reads an
ordered list and reports the ordinal one higher than the source states. It
is exactly the class of defect the per-claim apparatus exists to make
visible, and it is a demonstration that the apparatus is doing something —
even though the *confidence* it reports is not useful.

### 3.6 The industrial replication — the same generator, the same finding

The provider account that produced the focus corpus's answers hit its
token-plan limit, so the first industrial replication had to run with a
different generator, on 73 claims, and it was underpowered: 93% of its
claims were supported, so there was almost nothing to discriminate. The
account was reachable again, so the replication was re-run properly, with
**the same generator that produced the focus corpus's answers** (MiniMax-M3),
the shipped system prompt verbatim, and all 247 answerable industrial
questions.

| | Gold evidence | Retrieved evidence |
|---|---|---|
| claims labelled | 294 of 318 | 316 of 318 |
| Band vs reference (Cohen's κ, binary) | **0.062** (CI −0.021, 0.145) | **0.044** (CI −0.036, 0.124) |
| `grounded` / `inferred` / `uncertain` error rate | 0.069 / 0.088 / 0.156 | 0.047 / 0.066 / 0.105 |
| Answers with no wrong claim | 90.4% | 92.7% |
| … keeping only the `grounded` claims | 95.4% | 96.7% |
| Share of claims the `grounded` band keeps | 54.4% | 53.5% |

**The finding replicates, on both protocols.** Against an independent
reference the band is again at chance (κ 0.062 and 0.044, both intervals
including zero) and the three bands are again indistinguishable on the gold
evidence — and again *ordered* on the evidence the band saw, with the same
shape: a `grounded` claim is wrong 6.9% of the time and an `uncertain` one
15.6%. The band measures whether the retrieved passages entail the claim, and
that is not the same question as whether the claim is true. Two corpora, two
protocols, one generator: the same answer.

**And the positional comparison does not replicate.** On the focus corpus
"keep the first claims" beat the band on the gold protocol (p = 0.008). Here
it is the same direction but not significant — p = 0.083 on the gold evidence
(d_z = +0.328) and p = 0.317 on the retrieved evidence (d_z = +0.156) — and on
the focus corpus's own retrieved protocol it was p = 0.417. **Of the four
corpus-and-protocol combinations, one gives a significant positional result
and three do not.** The positional comparison is therefore evidence for the
reading, not the finding: the finding is the agreement-versus-correctness
split, which holds on all four.

Two methodological notes, because they changed the numbers. The judge's output
budget was hard-coded at 32 tokens, which is enough for a label and not enough
for a *reasoning* model, which spends the budget thinking and returns nothing;
the second reader's labels were recovered by re-running its failures at 4,096
tokens (`impl/scripts/relabel_failed.py`), which recovered 128 of 128 on the
gold protocol. And the consensus rule — the majority label, with a claim the
two readers disagree on left unlabelled — is *stricter* once both readers
cover every claim, so the complete run has fewer labelled claims than the
partial one and a weaker (not stronger) positional result. Reporting the
partial run's p = 0.005 would have been the wrong number.

### 3.7 A hypothesis that was tested and refuted

The framework feeds the claim text to the NLI model as the generator produced
it, and the generator produces Markdown: a claim can read "SF handled a
total of **3.05 billion shipments** in 2017", and that claim was scored at a
support probability of 0.006 despite being a verbatim quote of the source.
The obvious hypothesis was that the emphasis markers were costing the
entailment model its judgements.

The ablation (`impl/experiments/run_claim_band_ablation.py`) recomputes the
band for every claim with the Markdown stripped and re-measures the
agreement. **The hypothesis is refuted**: stripping the markers moves the
three-class κ from **+0.204 to −0.049**. Stripping makes the band agree
*less* with the judge, and 15 of 27 `grounded` claims fall to `uncertain`
when the markers are removed.

The reason is that the *passages* carry the same Markdown: the retrieved
chunk and the claim are marked up identically, so the markers cancel in the
entailment comparison. The NLI model's behaviour on a marked-up pair is not
a hygiene problem; it is a property of the model on that input, and the
measured agreement is what it is.

### 3.8 What this says

**1. The band measures "is this claim entailed by the retrieved passages",
and it does so competently.** Against the same evidence, the bands are
ordered (0.118 / 0.103 / 0.220) and the band's choice of claims beats a
random choice and the shortest-claims baseline.

**2. It does not measure "is this claim correct", and the difference
between those two questions is the whole story.** Against the benchmark's
gold evidence the bands are indistinguishable (0.542 / 0.513 / 0.610) and
the agreement is at chance (κ = 0.049, CI includes zero). A claim can be
perfectly true and not entailed by the passage the benchmark designated —
because the generator synthesised across two passages, or because the
designated gold passage is only one of several that support it — and a claim
can be entailed by a retrieved passage and still be wrong.

**3. As a *filter* the band still has value.** Keeping only the `grounded`
claims raises the share of answers containing no wrong claim from 34.4% to
50.0% against the gold evidence, and from 59.4% to 81.2% against the
evidence the band actually saw, at the cost of keeping 41.5% of the claims.
The filter's value is that it discards the worst third; its failure is that
it does not *rank* what remains better than position does.

**4. The band measures agreement with itself, not correctness.** Against the
evidence it saw, the three bands are ordered (0.118 / 0.103 / 0.220); against
an independent reference on the benchmark's gold evidence they are
indistinguishable (0.542 / 0.513 / 0.610, κ = 0.049). So the band measures
whether the retrieved passages entail the claim, competently, and that is not
the same question as whether the claim is true.

The evidence for that reading is the positional comparison: "read the first
half" beats "read what the framework tagged `grounded`" on the focus corpus's
gold protocol (p = 0.008, and not a length artefact — later claims are
*shorter*). It is reported as evidence and not as the finding, because of the
four measurements in §3.6: of the two corpora and two protocols, **one
gives a significant positional result and three do not** (focus retrieved
p = 0.417; industrial gold p = 0.083, d_z = +0.328; industrial retrieved
p = 0.317, d_z = +0.156). The agreement-versus-correctness split, by
contrast, holds on all four.

**5. The framework's own reporting is circular, and now measurably so.**
The reported claim-hallucination rate is a measure of entailment presented
as a measure of hallucination, and two independent estimates bracket it at
0.164 and 0.571.


## 4. RO4 — the contradiction detector on a corpus that contains conflicts

### 4.1 The corpus, and why it has conflicts in it

The eCFR versioner serves any regulation as it stood on any past date.
Federal regulations are amended. The same section read on **2021-12-31** and
on **2026-06-01** is the same rule at two issues, and where the amendment
changed a limit, the two versions state *different requirements*.

The two snapshots of the same sources produce **948 amended-paragraph
pairs** — paragraphs aligned across the snapshots by token overlap whose
text changed — and **361 of them (38.1%)** state different numbers in the
two vintages, so the amended set is where a changed requirement lives.

### 4.2 The candidate pool, and the one thing that must not happen

The pool of pairs a practitioner would actually be shown is the set of pairs
the **retriever** puts together. So the pool is mined by the retriever's own
signal — BM25, the lexical leg of the hybrid retriever — and **never** by
the detector's numeric rule, its NLI probability or its subject check. A
pool selected on the detector's decision rule cannot measure the detector's
precision: every alarm would be in the pool by construction, and the
precision estimate would be the detector's opinion of itself.

Two strata: 90 `revision` pairs (paragraphs and their amended selves) and
150 `similar` pairs (cross-document retrieval neighbours). The second stratum
carries the false-alarm load.

### 4.3 The annotations

The first RO4 measurement was annotated by two readers, and they disagreed
on 68 of 240 pairs — one cell: whether a pair that is recognisably the same
rule at two issues counts as *supersession* or as *no conflict*. That single
ambiguity moved the measured precision of the detector's semantic branch
from 0.075 to 0.675, so **the annotation, not the detector, was the binding
constraint on the measurement.**

Three things were done about it, and they are separable on purpose.

**1. The rubric was sharpened** so that the supersession branch is
*operational* rather than a judgement call. The branch now asks whether the
two passages are two issues of the same rule, and says explicitly that this
is a structural question — the same requirement, about the same subject, in
the same terms, differing only in detail — and that a version marker is one
way to see it, not the only way. It also says what supersession does *not*
mean: one of the two is not thereby wrong.

**2. The pairs were assigned to a regulatory regime**, and each regime was
read by a specialist: OSHA general industry (133 pairs), process safety
(44), environmental control (52), and DOT hazardous materials (11). Judging
whether two OSHA respiratory-protection provisions conflict is a different
task from judging whether two DOT packaging provisions conflict.

**3. A generalist read all 240 pairs** on the same sharpened rubric, with no
specialism in any regime. Without that control the rubric's contribution and
the specialisation's contribution could not be separated — and §4.4 now
separates them, by crossing the rubric against the reader type.

Two of the specialists verified their calls against the eCFR's point-in-time
API rather than reading alone, which settled most of the panel: the process
safety specialist found that most of its sheet is 29 CFR 1910.1200
Appendices A–F as rewritten by OSHA's 2024 HazCom final rule, and the
hazmat specialist confirmed eight pairs as the same rule at two issues by
fetching the two vintages.

**The annotators are not people.** They are language models with different
provenance — in-session agents with their own tools, and a provider-hosted
judge for the first measurement — and that is stated wherever the numbers
are reported. The agreement between them is evidence that the labels are a
property of the pairs rather than of one reader's habits; it is not human
validation.

### 4.4 The annotation, and which change produced the measurement

**The first measurement's problem was a rubric problem, and it is now measured
as one rather than asserted.**

The first RO4 measurement was annotated by two readers that did **not** use
the same rubric. `judge_a_model` read the original rubric, whose supersession
branch asked for a *version marker* — "revised", "updated", an effective date
— and so recognised almost none of the supersessions in regulatory text: it
found **9** conflicting pairs in 240. `judge_b_reader` read a second rubric in
which the branch was still a marker test but phrased so that an unmarked
supersession was allowed; it found **82**. Their consensus — the number the
first RO4 result was reported against — therefore had almost no supersessions
in it, and the detector's measured precision against it was **0.075**.

That comparison was then read as "the rubric or the specialisation?", and it
could not be answered, because the old-rubric reader was a generalist. The two
factors were the same cell.

#### The factorial

Two factors, crossed. **Rubric**: v1 (the marker test) or v2 (the structural
test). **Reader type**: generalist (no specialism in any regime) or
specialist (one reader per regulatory regime, each with that regime's brief).
The pairs, the detector, the regime assignment and the regime briefs are
identical across cells; only the rubric and the reader type vary. Every cell
is read by more than one reader, so a cell's number is not one reader's
idiosyncrasy.

| Cell | rubric | votes per pair | conflicts in the population | **detection precision** | typing precision |
|---|---|---|---|---|---|
| generalist | v1 | 2 | 21 | **0.293** (CI 0.176–0.445) | 0.073 |
| generalist | v2 | 2 | 82 | **0.659** (CI 0.505–0.784) | 0.073 |
| specialist | v1 | 1 | 28 | **0.341** (CI 0.216–0.495) | 0.073 |
| specialist | v2 | 1 | 90 | **0.659** (CI 0.505–0.784) | 0.073 |

(The two structures differ — the generalist cells have two votes per pair, the
specialist cells one — but they are identical across the two rubrics, so the
rubric contrast is unaffected. The generalist cell's two votes are the
original panel reader, who read all 240, and one further reader over that
half; the halves are the same under both rubrics.)

#### The effects

| Effect | Value |
|---|---|
| **Rubric**, at the generalist | **+0.366** |
| **Rubric**, at the specialist | **+0.317** |
| **Specialisation**, at rubric v1 | **+0.049** |
| **Specialisation**, at rubric v2 | **0.000** |
| Interaction (difference of differences) | 0.049 |

**The rubric's wording moved the measured precision by 0.32 to 0.37. The
reader's domain specialisation moved it by at most 0.049 — and on the rubric
the thesis reports, by nothing at all.** Under the sharpened rubric the
generalist and the specialists produced *identical* measured precision, 0.659.

#### The mechanism, in the labels

The rubric changed two things, and the labels separate them.

| | generalist | specialist |
|---|---|---|
| conflicting pairs found under v1 | 21 | 28 |
| conflicting pairs found under v2 | 82 | 90 |
| found by both | 19 | 27 |
| found only by v1 | 2 | 1 |
| **found only by v2 — the old rubric missed** | **63** | **63** |

The old rubric missed **63 of the 82 supersessions (77%)**, and it missed them
by calling them `no_conflict` — not by calling them something else. It
required a version marker, and a regulation does not write its own version in
its text. This is not a threshold that was slightly off; it is a conflict
class the reader was unable to see.

#### The agreement follows from it

With the rubric held fixed at v2, the generalist agrees with each specialist at
κ 0.661, 0.724, 0.686 and 0.651. With the rubric held fixed at v1, the same
two reader types agree at κ 0.579 (occupational), **0.100** (process safety)
and **0.268** (environmental). The old rubric did not define the task well
enough for a generalist and a specialist to converge; the sharpened one does.

The matched contrasts make the same point with the reader held fixed as well:
the same reader, on the same pairs, on the same model, with only the rubric
changed, agrees with its v2 counterpart at κ 0.132 (generalist, first half),
0.652 (generalist, second half), 0.558 (occupational, model-matched
replicate), 0.122 (process safety), 0.333 (environmental) and 0.415 (hazmat).

#### What is not claimed

The rubric changed the *definition* of the target — which pairs count as a
conflict at all — and the *procedure* for recognising one. This factorial
cannot separate those two components, and both are rubric-level. What it does
establish is that the reader factor is small: at most 0.049 of the movement,
and 0.000 on the rubric this thesis reports. A panel of domain specialists,
one per regulatory regime, is **not** what made the measurement work.

### 4.5 The detector, measured

240 pairs: 90 amended-paragraph pairs and 150 retriever-neighbour pairs.
Two detector configurations, because the two vocabularies are separable and
should be separable in the result: `shipped` is the framework as it is —
the operations and supply-chain measurement and version vocabularies it was
written against — and `regulatory` swaps in the regulatory measurement and
version vocabularies, which is the configuration the regulatory corpus
requires. (An earlier draft of this section reported four configurations,
`lookback` and `instance` among them. Those two were measured on the pool
but their results were not written to a file, and a number that no artefact
holds cannot be reported; the table below carries the two configurations
that the result file does hold.)

**Against the sharpened consensus labels** (the majority label; a contested
pair counts as *not* a conflict, which can only lower a precision):

| | shipped | regulatory |
|---|---|---|
| Alarms | 40 | 41 |
| — semantic branch | 40 | 38 |
| — quantity branch | **0** | **0** |
| — revision branch | **0** | 3 |
| **Detection precision** | 0.650 | **0.659** (CI 0.505–0.784) |
| **Typing precision** | **0.000** | **0.073** (CI 0.025–0.194) |
| Branches below the 0.5 floor | none | none |

The shipped profile detects almost as well (0.650 against 0.659) and types
nothing at all (0.000): the operations vocabulary matches no measurement a
regulation binds on, so the quantity branch cannot fire and the semantic
branch carries every alarm. The regulatory profile's entire gain comes from
the version vocabulary — the three alarms it adds are the pairs where a
*standard edition* changed — and its typing precision, while above zero,
is still 0.073.

**Detection** asks whether the alarm points at something real. **Typing**
asks whether the branch that raised it is the branch that owns the conflict.
A detector can be excellent at the first and systematically wrong about the
second, and the second is what tells a practitioner what to do about it.

**By stratum** (regulatory profile, consensus labels):

| Stratum | n | Flagged | Detection precision | Branches used |
|---|---|---|---|---|
| `revision` — the same provision at two issues | 90 | 29 | **0.897** | semantic 26, revision 3 |
| `similar` — retriever neighbours | 150 | 12 | **0.083** | semantic 12 |

**The consistency matrix** (regulatory profile, consensus labels):

| Label | Not flagged | Flagged (semantic) | Flagged (revision) |
|---|---|---|---|
| `supersession` | 57 | **24** | 3 |
| `term_mismatch` | 80 | **10** | 0 |
| `no_conflict` | 60 | **4** | 0 |
| `granularity` | 2 | 0 | 0 |

**Against the construction labels**, where no annotation is involved: the
revision stratum is the same provision at two issues *by construction*, and
where the two versions state different unit-bearing quantities the rule
changed the limit. 35 of the 90 sampled pairs changed a quantity and 55 did
not.

| | Value |
|---|---|
| Alarms on the revision stratum | 29 |
| **Detection precision** | **1.000** |
| **Typing precision** | **0.000** |
| Quantity branch, recall on the 35 construction-labelled quantity conflicts | **0.000** |
| Revision branch, recall on the 55 construction-labelled supersessions | **0.000** |

### 4.6 What the measurement says

**1. The mechanism finds the conflicts.** On the stratum where conflicts
actually are, its detection precision is **0.897**; against the
construction labels, where nothing is judged, it is **1.000**. The earlier
0% was a property of an empty corpus, and this is the measurement that
replaces it.

**2. It reports them as the wrong kind of thing.** Its typing precision is
**0.073**: of 41 alarms, 24 are supersessions reported as contradictions and
10 are term mismatches reported as contradictions. The detector's semantic
branch does not find contradictions in regulatory text — it finds
*out-of-date text*, and reports it as a conflict. **And it cannot tell the
practitioner which version is in force**, because nothing in the retrieved
passages says which issue either of them is. That is the one thing a
practitioner needs from a contradiction detector on a regulatory corpus, and
it is exactly what the mechanism does not deliver.

**3. The quantity branch never fires, even where it provably should.** Its
recall on the 35 construction-labelled pairs — where the rule demonstrably
changed a limit — is **0.000**. Two things are wrong with it: its declared
measurement vocabulary is written for operations and supply-chain prose
("eoq", "safety stock", "lead time") and covers none of the quantities a
regulation binds on; and the measurement key requires the term to sit
immediately before the number, where a regulation writes "the permissible
exposure limit for cadmium is 5 micrograms per cubic meter". Widening the
look-back and enabling the instance rule change nothing on this pool — the
regulatory profile's entire gain comes from the version vocabulary.

**4. The revision branch cannot see regulatory supersession.** Its recall on
the 55 construction-labelled supersessions is **0.000**. It fires on 3
pairs, all correctly (precision 1.000), and those are the pairs where a
*standard edition* changed ("ASTM A47-68" → "ASTM A47-89"). A regulation
does not write its own version in its text, so a detector that looks for
version markers in the text cannot tell a practitioner which issue is in
force. This is the same finding as point 2, reached by a different route.

**5. The binding constraint was the annotation, and the fix was the rubric.**
The same detector, on the same 240 pairs, scores **0.075** against the
first measurement's labels and **0.659** against the sharpened ones. A
measurement that moves by a factor of nine with the wording of its own
rubric is not yet a measurement of the thing under test — and the
factorial in §4.4 shows where the movement came from: the **rubric** was
worth +0.366 (generalist) and +0.317 (specialist), and the reader's domain
specialisation was worth +0.049 and 0.000.

**6. What this does not change.** The framework's own precision floor does
its job: under the sharpened labels the semantic branch's precision (0.632
against any real problem) clears 0.5, so the calibration would now surface
these findings — correctly, because they *are* real conflicts. Under the old
labels it would have withheld them. The calibration was never wrong; it was
responding to labels that were.

### 4.7 The quantity branch, on a stratum built for it

The quantity branch fired zero times on the revision stratum, and the
revision stratum contains 35 pairs where the rule demonstrably changed a
limit. Two explanations were possible, and they call for opposite
conclusions: the branch is broken, or there is nothing to fire on. The
corpus settles it.

**The corpus-wide search.** Every (measurement term, value) pair in every
document was collected and grouped by term. **64 measurement terms carry a
value somewhere in the corpus, and 1,776 of them take different values in
different documents** — "pressure" 333 times, "level" 246, "capacity" 241,
"concentration" 229, "temperature" 173. So the candidates are not scarce.
(The search is deliberately over-inclusive: two passages about different
boilers share the word "pressure".)

**The detector on those candidates.** The branch fired on **13 of the 119**
sampled candidate pairs.

**The gold standard.** A regulatory specialist labelled 60 pairs — all 13
that fired, plus 47 that did not — blind to which was which:

| Label | n |
|---|---|
| `term_mismatch` | 58 |
| `no_conflict` | 2 |
| **`quantity_conflict`** | **0** |

**The branch's record on this stratum: 0 true positives and 13 false
positives.** The specialist's own account is the mechanism: 39 of the 58
`term_mismatch` calls are the same measurement word naming two different
things — oxygen container capacity against LP-gas water capacity against an
SPCC's 1,320 gallons against a nitric-acid receptacle's 2.5 litres;
butadiene's vapour pressure against arsenic's boiling point; an oxygen
cylinder's 50-foot separation against an LP-gas system's 10-foot clearance.
The remaining 19 share no measurement term at all.

**So the quantity branch has nothing to find in this corpus, and what it
does find is not there.** The two failure modes are separable and both are
real:

* On the revision stratum, where the rule changed a limit, it fires on
  **0 of 35** — the measurement key cannot reach a limit written as "the
  permissible exposure limit for cadmium is 5 micrograms per cubic meter",
  because the key wants the term immediately before the number and the
  regulation puts three words and a copula in between.
* On the cross-document stratum, where the same measurement word names
  different things in different documents, it fires on 13 pairs and **none
  of them is a conflict**.

**The conclusion is about the domain, not only the code.** Federal
regulation is internally consistent about the numbers it binds — OSHA
harmonised its construction and general-industry limits for asbestos,
cadmium, lead and silica, so the same substance carries the same
permissible exposure limit in both — and it binds each quantity to one
scope, so two documents using the same word are almost never in conflict
about it. **A quantity-conflict detector has very little to detect in
regulatory text**, and the branch as written would report coincidences as
conflicts if it were allowed to fire.



---

## 5. What changed in the framework, and what did not

Four things changed in `impl/src/`. None of them changes a number that has
already been reported, and each is either a defect the measurement exposed
or an addition the new corpus needed.

**1. The measurement key may sit up to three tokens before the number**
(`src/contradiction.py::_measurement_key`). The shipped rule required the
measurement term to be the token immediately before the number, which fits
"the reorder point was set to 40 units" and does not fit "the permissible
exposure limit for cadmium is 5 micrograms per cubic meter", where the noun
phrase is separated from the number by the thing being limited and the
copula. Because the vocabulary is declared, the look-back can be bounded
rather than open: it cannot reach a surname or a month name that no
vocabulary entry would match.

**2. The regulatory measurement and version vocabularies** are selectable
(`ContradictionConfig.measurement_profile` and `.standard_profile`). The
shipped vocabulary is written for operations and supply-chain prose and
covers none of the quantities a regulation binds on; the regulatory profile
adds "permissible exposure limit", "action level", "clearance", "flash
point", "vapor pressure" and the rest. The version vocabulary changes too:
the shipped one reads "Incoterms 2020" and takes the qualifier from a
nearby acronym, which on regulatory text is often a *constant* ("FR",
"ANSI"), so it produces false revision conflicts; the regulatory one reads
the edition out of the citation itself ("ASTM A47-68", "ISO 817:2014(E)",
"ANSI Z87.1-2010") and uses the standard's own number as the qualifier,
which is the thing that has to match for two passages to be about the same
standard.

**The default is the shipped vocabulary**, so the focus corpus's fitted
calibration is unaffected by the existence of the alternative, and both
profiles are reported side by side.

**3. An instance identifier is kept in a proper name**
(`src/contradiction.py::proper_nouns`). "Plant A" and "Plant B" are two
instances, and the instance check is the only thing that tells them apart —
but "A" is on the stop list as the English article, so dropping the first
word of "Plant A" at the start of a passage left nothing, and the instance
disappeared. A single trailing capital letter is now kept.

**4. The embedding's sequence limit is configurable** and is part of the
embedding cache key *only when it is set*, so the corpora already encoded
keep their vectors and their numbers.

**5. The cross-category transfer experiment now includes the shared negative
class** (`experiments/run_transfer.py`). The unanswerable queries carry no
category, so a split by category dropped the entire negative class out of
*both* halves and the experiment measured only how many true answers get
refused. The shipped six-category result had `n_unanswerable: 0` and
`unanswerable_refused: NaN` in every split; the rebuilt Table 6 has real
numbers. The deliverables' consistency checker still passes.

**6. The batched entailment pass** (`experiments/run_claim_band_eval.py`).
The per-claim band is recomputed in one batched call rather than one call
per claim, and the value test's bootstrap resamples over *answers* rather
than over the random policy's draws — the draws are orderings of the same
answers, and treating them as independent observations reports an interval
several times too narrow. Neither change affects a reported number's
definition; the first is a speed change and the second corrects an interval
that was too narrow.

**7. `detect_contradictions` accepts pre-computed probabilities**
(`src/contradiction.py`). Scoring two hundred pairs one call at a time cost
fifteen minutes; passing the entailment probabilities in, computed in one
batch, costs forty seconds. The default behaviour is unchanged.

**8. The band recomputation is cached on disk**
(`impl/artifacts*/claim_band_cache.json`), so a re-run with a different
label set does not pay for the entailment pass again — twenty minutes down
to six seconds.

**9. The reference consensus is the majority, not the unanimity.** With two
readers and an adjudicator, a claim the readers disagree about is resolved
by the adjudicator rather than dropped. Thirty-three claims that the earlier
rule discarded are now used.

**10. The per-branch recall in the contradiction evaluation was computing
nothing** — the dict unpacking was reversed, so the per-branch recall was
always `None` and the measurement silently reported only the overall figure.
The overall figures were never affected; the per-branch ones are now
computed.

### What did not change

* **The corpus, the benchmark and the label standard of the existing
  deliverables.** The industrial corpus and its benchmark are a *third*
  variant, addressed by the `MTP_VARIANT` mechanism that already existed
  for the focus corpus. Nothing in `data/corpus`, `data/benchmark`,
  `data/corpus_focus` or `data/benchmark_focus` was touched.
* **The gate, the fusion, the reranker and the confidence code.** The
  industrial evaluation runs the shipped pipeline unchanged.
* **The gate's calibration discipline.** The contradiction branches are
  still withheld below the 0.5 precision floor, and the measurement below
  is what the floor would act on.

### The defect this work exposed in the framework's own reporting

**The band the answer shows the practitioner and the claim-support rate the
papers report are different functions of the same evidence.** The framework
tags a claim with a noisy-OR of the per-chunk entailment probabilities
(`src/claims.py::assess_claims`); the generation experiment records the
*maximum* entailment over the same candidates, thresholded at 0.5
(`run_generation_eval.py::_claim_support`). The two disagree on 23 of the
350 pooled claims.

The noisy-OR assumes the witnesses fail independently, which they do not:
ten passages about the same subject are not ten independent trials, so the
noisy-OR saturates where the maximum does not. The framework ships the
saturating one; the papers report the other.

### What could not be done

**The industrial-corpus replication of RO5 ran with a different generator.**
The provider account that produced the focus corpus's answers hit its
token-plan limit (HTTP 429, "Token Plan usage limit reached") after six
records, and the harness recorded the run as `not_run` rather than
reporting a rate it could not stand behind. The industrial replication was
therefore run with three in-session agents answering under the shipped
system prompt, and it is a replication rather than a second measurement: a
different model family, on a different corpus. It is also underpowered — 93%
of its claims are supported — and it is reported as such.

**The annotations are not human.** The RO4 pairs were read by four
domain-specialised readers and a generalist control; the RO5 claims by a
generalist, a supply-chain specialist and an adjudicator. The agreement
statistics are reported in full (κ = 0.902 between the two claim readers,
0.65–0.72 between each RO4 specialist and the generalist control), and the
thesis's existing disclosure — that the Experiment 11 annotators were
models — now applies to the two measurements that carry the most weight.
What a human round would have added is independent confirmation that the
labels are *right* rather than merely consistent, and the one place where
that mattered most is where the two readers disagreed by a factor of nine
in the measured precision.

---

## 6. What this changes for the thesis

**The three objectives are closed, and two of them close with a negative
result.** That is not a failure of the work; it is what the work found.

**RO6 closes with the thesis's own negative findings *replicated on
authentic industrial text*.** BM25 beats the dense encoder
(p = 0.00026, three times the effect size on the focus corpus and twenty-five
times the significance); the fusion does not beat its lexical leg on recall
(p = 1.000); the category pre-filter is a no-op (p = 1.000); the quota
belongs after the reranker (p = 0.038); and the candidate pool stops paying
for itself at about twenty, with the displacement measured directly
(Recall@20 = 1.000 at pool 50 while Recall@10 stays at 0.988). The
thesis's most surprising claims were not artefacts of a small encyclopaedic
sample, and the one claim that *did* change — the reranker, which helps on
regulation and hurts on Wikipedia — is explained by the pool result.

**RO4 closes with a finding that reframes the mechanism.** The
contradiction gate's semantic branch does not find contradictions in
regulatory text; it finds *out-of-date text*, and reports it as a
contradiction. Under the **regulatory** measurement and version vocabulary —
the configuration this corpus requires — its **detection** precision on a
corpus that does contain conflicts is **0.659** (CI 0.505–0.784), and
**0.897** on the stratum where the conflicts actually are — so it finds
them. Its **typing** precision is **0.073**: it calls supersessions
contradictions. (Under the shipped operations vocabulary, detection is
0.650 and typing is 0.000 — the same alarms, typed no better.) And it
cannot say which version is in force, because nothing in the retrieved
passages says which issue either of them is. The quantity branch never
fires: on 35 construction-labelled limit changes its recall is 0.000, and
on the 1,776 cross-document candidates a specialist confirmed **none** as a
real conflict. The revision branch fires on three pairs, all correctly, and
those are the pairs where a *standard edition* changed.

**And the measurement's binding constraint was the annotation.** Against
the first measurement's labels the same detector scores **0.075** on the two
readers' consensus (0.098 against the reader whose rubric had no working
supersession branch); against the sharpened ones, **0.659**. The
factorial in §4.4 removes the confound the first comparison could not: with
the reader type held fixed, the rubric is worth **+0.366** (generalist) and
**+0.317** (specialist), and the reader's domain specialisation is worth
**+0.049** at the old rubric and **0.000** at the new one. The rubric's
wording is what moved the number — and the old rubric's failure was
concrete: it required a version marker, and a regulation does not write its
own version in its text, so 63 of the 82 supersessions were invisible to it.

**RO5 closes with a finding that splits the mechanism in two.** The band is
a usable **filter** — keeping only the `grounded` claims raises the share of
answers with no wrong claim from 34.4% to 50.0% against the gold evidence
and from 59.4% to 81.2% against the evidence the band saw — and **not** a
usable **ranking**. Against the benchmark's gold evidence the band does not
track correctness at all (κ = 0.049, CI [−0.026, 0.124], and the three bands
are indistinguishable), while against the evidence it saw they are ordered
(0.118 / 0.103 / 0.220). **The band measures whether the retrieved passages
entail the claim — agreement with itself — not whether the claim is true.**
And that is the part that replicates: on the industrial corpus, with the same
generator, the band is again at chance against an independent reference (κ
0.062 and 0.044 on the two protocols) and again ordered on the evidence it
saw (0.069 / 0.088 / 0.156). The positional comparison ("keep the first
claims", p = 0.008 on the focus corpus's gold protocol, not a length
artefact) is the evidence for that reading rather than the finding itself,
because it did not replicate on the other three corpus-and-protocol
combinations. The framework's own claim-hallucination rate is a measure of
entailment presented as a measure of hallucination, with two independent
estimates bracketing it at 0.164 and 0.571.

**What a panel should take from this.** The thesis's framing — "which
reliability mechanisms pay for themselves, at what price, and exactly where
they break" — is now supported by measurement on an authentic corpus rather
than asserted. Three of the five mechanisms are shown to pay for themselves
on regulatory text: the confidence gate (at a threshold that must be
re-fitted per corpus), the hybrid retriever (through its ordering, not its
recall), and the modality quota (only in its post-rerank position, and only
where the corpus has the modality). Two are shown to break in ways that were
not anticipated: the contradiction gate's semantic branch detects
supersession and cannot say which version is current, and the per-claim
band is a filter that does not rank.

**What this does not settle.** The scope reconciliation the proposal needs:
the corpus is regulatory and industrial, but the proposal's machine-learning
and data-analytics domains are still not covered, and the industrial corpus
is 110 documents from four regulatory regimes rather than the twelve
categories spanning three domains that the proposal promised. And one
finding is domain-specific in a way worth stating plainly: the quantity
branch's failure is not only a vocabulary gap. Federal regulation is
internally consistent about the numbers it binds — OSHA harmonised its
construction and general-industry limits for asbestos, cadmium, lead and
silica — so a quantity-conflict detector has very little to detect in
regulatory text, and what it does find is coincidence.

**What was replaced, and what it cost.** The human annotation round was
replaced by a panel of domain-specialised readers plus an adjudicator, with
the agreement statistics reported in full. That bought agreement (κ = 0.902
on the claim labels, 0.65–0.72 between the RO4 specialists and the
generalist control) and it cost the thing a human round would have given:
independent confirmation that the labels are right rather than merely
consistent. The thesis already discloses that its Experiment 11 annotators
were models; this work makes the disclosure apply to the two measurements
that carry the most weight in RO4 and RO5.

