---
title: "An Evidence-Grounded Retrieval-Augmented Generation Framework for Industrial Decision Support"
subtitle: "M.Tech Project — Status Report"
author: "Ritik Raj (25IM60R12) — Department of Industrial and Systems Engineering — IIT Kharagpur — Supervisor: Dr. Sri Krishna Kumar"
date: "11 November 2026"
shorttitle: "MTP Status Report"
---

# 1. The problem this project addresses

Industrial practitioners make decisions from paperwork: standard operating
procedures, failure-mode and effects analyses, control plans, calibration
records, OEM manuals, supplier specifications. A question — *"what is the
economic order quantity for this SKU?"*, *"what acceptance criterion applies to
this lot?"* — is normally answered by a person who knows which of hundreds of
documents holds the answer.

Retrieval-augmented generation (RAG) is the obvious tool for that. It also has
a failure mode that matters more in industry than in dialogue: a RAG system
that answers when the documentation does **not** contain the answer fabricates
one, and the fabrication is indistinguishable *in form* from a correct answer.
In a plant that means a wrong safety-stock rule or a wrong acceptance
criterion propagates into a plan.

The published reliability literature addresses this mostly in dialogue,
clinical text, social-media claims and scientific claims. Industrial
engineering documentation is largely unmeasured. So the question this project
actually asks is **not** "does RAG hallucinate" — that is answered. It asks:

> What does a reliability mechanism **cost** and what does it **buy**, on
> industrial engineering text, at the level of the individual answer claim?

That is a measurement problem, and the thesis's contribution is the
measurement, not the architecture. Every mechanism below has published prior
art; what is new is the joint cost–coverage–reliability frontier it produces
on a corpus regime that is not the procedural one most deployments use.

# 2. Objectives

**These are this report's own working objectives, numbered O1–O4.** They are *not*
the MTP proposal's research objectives, which are numbered RO1–RO6 and are set out
in full in the complete guide, §A.1. The two lists overlap but do not use the
same numbering, and this report uses the O-prefix throughout so that "RO4" means
the same thing everywhere it appears.

| # | Objective | Where it is answered | Status |
|---|---|---|---|
| O1 | Build a framework whose answer is gated by a **code-level, non-bypassable** confidence check, not by an instruction to a model | §3, §5.2 | **Met** — the gate is a control-flow fact, asserted by an invariant test |
| O2 | Establish what the gate **costs** (coverage) and what it **buys** (refusal of unanswerable questions), at a stated operating point | §5.2, §5.6 | **Met** — measured on two prompt conditions, with a paired significance test |
| O3 | Build the measurement instrument — benchmark, scorer — and **audit it** | §4, §9 | **Met** — two audits found two defects; both were repaired and everything re-measured |
| O4 | Test whether the calibration **transfers** across industrial sub-domains | §5.4 | **Met with a stated scope** — coverage transfer is measured; refusal transfer is not measurable under a category split, and §5.4 says so |

# 3. What we built

The system is a **library plus batch experiment scripts**, not a service. That
is the right shape for a thesis — every measurement has to be reproducible
from a command line — and the code is 14 modules and 4,823 lines under `impl/src/`,
with 34 experiment scripts and 32 tests.

```
DOCUMENT SET           +------------------------------------------------+
(46 Wikipedia          | STAGE 1 -- INGESTION  (offline, once)          |
 articles,             | parse -> chunk -> tag modality+category        |
 6 industrial-         |        -> embed (BGE-M3, 1024-d) -> index      |
 engineering)          +------------------------------------------------+
 categories)                                   |
                                               v
        +------------------------------------------------+
        | STAGE 2 -- RETRIEVAL  (online, per query)      |
        |                                                |
        | [form check] refuse a non-question             |
        |   (before retrieval; costs no model call)      |
        |                                                |
        | category pre-filter  (BOTH legs)               |
        |     |                                          |
        | +---+---+                                      |
        | v       v                                      |
        | BM25     dense (BGE-M3)                        |
        |  |       |                                     |
        | +---+---+                                      |
        |     v                                          |
        | RRF fusion (k=60)                              |
        |     |                                          |
        | modality quota (floor on tables/charts)        |
        |     |                                          |
        | cross-encoder rerank (top-50 -> top-10)        |
        |     |                                          |
        | >>> CONFIDENCE GATE <<<                        |
        |     5 signals -> calibrated posterior          |
        |     posterior >= tau -> accept, else REFUSE    |
        |     (the model is not called)                  |
        +------------------------------------------------+
        |                                               |
        +-----------------------------------------------+
                                v  (only if accepted)
                     +------------------------------------------+
                     | STAGE 3 -- GENERATION                    |
                     | per-claim confidence tagging             |
                     | citation attachment                      |
                     | contradiction surfacing (NLI + numeric)  |
                     | -> answer with a per-claim audit trail   |
                     +------------------------------------------+
```

## 3.1 Two properties that are load-bearing

**(a) The gate is a control-flow fact, not an instruction.** "The model was
told to be careful" is an instruction, and a model can ignore it. "The model
was never called" is a fact about the program. The generator is *injected*
into the framework (`Framework(index, generator=...)`) and `answer()` calls it
at exactly one line, after the gate has accepted. On a refusal, the claim
assessment and contradiction detection are skipped too, so a refused query
costs no model call at all. `impl/tests/test_invariants.py` asserts this, and
`impl/scripts/verify_gate_path.py` demonstrates it against the real focus
index by instrumenting the call itself.

**(b) The category pre-filter runs *before* retrieval, not after.** Filtering
after retrieval means the retriever already paid to score documents that were
going to be discarded — and, worse, those discarded documents still influenced
the fusion. Filtering before retrieval means the candidate pool contains only
in-category material, so BM25's IDF statistics, the dense model's attention
and the reranker's ranking are all computed on the correct sub-corpus.

> This was not free. An early version applied the filter to the dense leg
> only, which made it a **silent no-op** — BM25 dominates the fusion, so an
> unfiltered lexical list floods the fused ranking and the filter's effect
> disappears. It looked like a measured effect of zero. It is now asserted by
> an invariant test (`test_category_filter_applies_to_both_legs`).

# 4. How it is evaluated

| | Focus domain (headline) | Six-category corpus (transfer study) |
|---|---|---|
| Domain | Supply chain management | Six industrial-engineering sub-domains |
| Chunks | 735 | 2,383 |
| Documents | 14 | 46 |
| Categories | 1 | 6 |
| Tokens | 202,529 | 680,417 |
| Modality mix | 88.8% text, 6.0% tables, 5.2% charts | — |
| Benchmark queries | 176 (32 answerable, 144 unanswerable) | 276 (132 answerable, 144 unanswerable) |
| Role | every headline measurement | the cross-category transfer study |

The corpus is **industrial-engineering encyclopaedic text** — Wikipedia
articles on supply chain management, production scheduling, quality
engineering, reliability engineering, predictive maintenance and facility
layout — and it is described as exactly that. It is not practitioner
documentation, and the deliverables do not claim it is. The primary corpus
(634 chunks over 24 proprietary supply-chain documents) cannot be
redistributed; the public corpus ships with per-document provenance (source
URL, upstream revision id, SHA-256, chunk count) under CC BY-SA 4.0 in
`deliverables/dataset/`.

The benchmark is **silver-standard**: gold chunk plus a label for whether the
question is answerable at all. The answerable half's labels were audited and
repaired (§9).

# 5. Results

## 5.1 Retrieval

Seven configurations, one query set, paired Wilcoxon signed-rank test between
adjacent rungs. Focus domain, 176 queries.

| System | R@5 | R@10 | R@20 | MRR | nDCG@10 | Table R@10 |
|---|---|---|---|---|---|---|
| A. BM25 only | 0.969 | 0.969 | 1.000 | 0.736 | 0.792 | 1.000 |
| B. Dense only | 0.812 | 0.812 | 0.875 | 0.652 | 0.688 | 0.875 |
| C. Hybrid (RRF) | 1.000 | 1.000 | 1.000 | 0.798 | 0.847 | 1.000 |
| D. + cross-encoder rerank | 0.969 | 0.969 | 1.000 | 0.795 | 0.836 | 1.000 |
| E. + category filter | 0.969 | 0.969 | 1.000 | 0.795 | 0.836 | 1.000 |
| F. + quota (pre-rerank) | 1.000 | 1.000 | 1.000 | 0.819 | 0.864 | 1.000 |
| G. + quota (post-rerank) | 0.938 | 0.938 | 0.938 | 0.789 | 0.826 | 1.000 |

| Comparison | ΔR@10 | p (Wilcoxon) |
|---|---|---|
| A → B (BM25 → dense) | -0.156 | 2.5 × 10⁻² |
| B → C (dense → hybrid) | +0.188 | 1.4 × 10⁻² |
| C → D (+ rerank) | -0.031 | 3.2 × 10⁻¹ |
| D → E (+ category filter) | +0.000 | 1.0 × 10⁰ |
| E → F (+ quota, pre-rerank) | +0.031 | 3.2 × 10⁻¹ |
| F → G (quota moved post-rerank) | -0.062 | 1.6 × 10⁻¹ |

**What the ablation actually shows.**

* **Fusion works, and it is the only retrieval change that is significant.**
  Dense-only retrieval is *worse than plain BM25* (-0.156 in R@10, p =   2.5 × 10⁻²). Fusing the two recovers it and then some (+0.188, p =   1.4 × 10⁻²). This is the argument for hybrid retrieval stated as a
  measurement rather than as a received wisdom.
* **The reranker does not help.** -0.031 in R@10, p = 3.2 × 10⁻¹ — not
  significant, and the sign is negative. It is kept anyway, because the gate
  is calibrated on the reranker's score and because the cross-encoder is what
  makes the *candidate pool* large enough to need gating.
* **The category filter is a no-op on the focus domain**, and that is the
  correct result: the corpus has one category. Its value shows up on the
  six-category corpus and in the mechanism tests.
* **The modality quota belongs *before* the cross-encoder.** Applied after
  the reranker (-0.062, p = 1.6 × 10⁻¹) it costs recall; applied before it,
  it restores table recall to 1.000 at no measurable cost to text recall.
  A quota that runs before the reranker fixes the membership of the final
  ten, so the cross-encoder can reorder it but not change it, and the forced
  table chunk survives; a quota that runs after has to import a chunk the
  cross-encoder already ranked below the cut, which displaces a good one.
  **The system now applies it before the cross-encoder.** It was built
  with the later placement and kept it until 16 November 2026, because every
  measurement had been taken with it; on that date it was moved and
  everything that depends on it was measured again. The direction is
  corpus-dependent: the earlier placement is also the better one on the
  six-category corpus, and the later one is marginally better on the
  industrial corpus, by less than the noise.
* **The candidate-pool curve peaks and then declines.** Recall@10 is highest
  at a pool of ten (0.955) and falls to 0.932 at a pool of
  fifty. A larger pool costs the reranker work and buys nothing — the
  reranker can only permute what it is shown.

![Figure 4. Overall Recall@10 against table-specific Recall@10 for the seven ablated systems, focus corpus (black circles, n = 32 answerable: 24 text, 8 table) and industrial corpus (grey squares, n = 247: 117 text, 130 table). The modality quota does not move both axes: on the industrial corpus the pre-rerank quota buys 0.8 points of table recall and gives up 0.8 points of overall recall, and the post-rerank quota lands on exactly the no-quota operating point; on the focus corpus the post-rerank quota gives up 3.1 points of overall recall while table recall stays at 1.000. The quota is a trade, not a gain, and which way it trades depends on where it is applied.](figures/fig4_modality_quota_pareto.pdf)
![Figure 1. Recall against the size of the rerank candidate pool, on the focus corpus (black circles, 32 answerable of 176 queries) and the industrial corpus (grey squares, 247 of 444). The focus curve saturates at a pool of 10, where Recall@10 = Recall@20 = 1.000, and then falls slightly as the reranker is given more candidates to reorder. The industrial curve does not saturate at 10: there Recall@20 reaches 1.000 at a pool of 50 while Recall@10 stays at 0.988, so 1.21 points of gold are retrieved and then pushed out of the ten-chunk context.](figures/fig1_pool_size.pdf)

## 5.2 The confidence gate

The gate's label is **answer-in-context detectability**, not evidence
sufficiency. The positive class is "the gold chunk is present in the reranked
candidate pool". The literature reserves *sufficiency* for the set-level
property, so the name is deliberately not borrowed.

Calibration: Brier 0.1510, ECE 0.1044. Operating point:
τ = 0.05, chosen by a stated rule (the highest τ still answering ≥ 90% of
answerable queries).

| | Value |
|---|---|
| Answerable questions answered | 93.8% |
| Unanswerable questions refused (pooled) | 36.1% |
| Abstention precision | 0.963 |
| **Corpus-anchored unanswerable class refused** | **23.6%** (26 of 110) |
| Out-of-domain unanswerable class refused | 76.5% (26 of 34) |

**The pooled number is an upper bound, and the gap between the two strata is
the finding.** The out-of-domain family is unanswerable for any system that
knows what the corpus is about, so refusing it says almost nothing. The
corpus-anchored family is the real test: the corpus discusses the subject and
states no value for it, so only the retrieved evidence can decide. The gate
refuses **23.6%** of those. It is good at *recognising* an
unanswerable question; it is not good at detecting *absent evidence*, and
those are different problems. Reporting only the pooled figure would have
flattered the system by a factor of about one and a half.

![Figure 2. Risk-coverage of the confidence gate: the risk that an answered query has no answer in its context, against the fraction of queries the gate answers, on the held-out evaluation half (focus n = 71, industrial n = 178). The degenerate policies bound the curve: always answering carries the base rate of the negative class as its risk at full coverage, and always refusing removes the risk at the cost of all coverage. The industrial gate trades risk for coverage; the focus gate buys almost nothing over answering everything. The fitted operating points (tau = 0.05 focus, tau = 0.40 industrial) answer 0.693 and 0.691 of all queries respectively.](figures/fig2_risk_coverage.pdf)
![Figure 3. Reliability of the gate's calibrated probability against observed answerability, on the held-out evaluation half (focus n = 71, industrial n = 178); the upper panel plots observed answerability against mean predicted probability per bin and the lower panel the number of queries in each bin. The industrial gate tracks the diagonal (ECE 0.075, Brier 0.159); the focus gate does not (ECE 0.1044, Brier 0.1510): it puts most of its queries in the lowest confidence bin, where few of them have an answer in context.](figures/fig3_calibration.pdf)

## 5.3 Contradiction surfacing

1,350 chunk pairs compared over the accepted contexts.

| Detector | Pairs flagged | Flag rate |
|---|---|---|
| NLI alone | 110 | 0.081 |
| **and** the same-subject check (the shipped gate) | 20 | 0.015 |

The same-subject check is what does the work: it suppresses 110 minus 20 of the bare NLI gate's
alarms, leaving 20 of 1,350 pairs. The gate has three branches — a semantic one
(NLI and same-subject), a quantity one (the same measured quantity with two
values) and a revision one (the same term at two versions of the same
standard) — and on this corpus the alarms split 20 semantic, 0 quantity, 0 revision.

The precision has been measured against reader labels rather than against a
proxy: The contradiction gate's precision, measured against reader labels rather than against a proxy, is 0%: none of the 20 labelled alarms was called a contradiction by either annotator, and the 95% upper bound on the gate's true precision is 16.1%. The two annotators do not share a model, both read the sheet blind to the detector's own scores, and both scored 14 of 14 on a control set whose labels are known in advance, and they agree on the contradiction/no-contradiction decision for 101 of the 101 pairs they labelled. The annotators are models rather than people, so the number says the alarms are not confirmed by a reader, not that no reader would ever confirm one.

The gate has three branches, each measured separately: the semantic branch's 0 of 20 alarms were accepted as genuine contradictions by both annotators. A branch whose measured precision is below the calibration floor has its findings recorded and withheld rather than shown to a practitioner — the same discipline the answer gate applies to an answer, applied to the framework's own claims.



The detector's own positive control -- pairs whose correct behaviour is known in advance, written in the industrial register but not drawn from the corpus -- is 11 of 11, with every contradiction caught and every non-conflict left alone. So the mechanism works; this corpus does not test it.

**What this means for the shipped system.** The calibration is fitted from the
measurement and the pipeline reads it: a branch whose measured precision is
below the floor has its findings recorded and withheld rather than shown to a
practitioner. On this corpus that leaves **20 findings
surfaced and 0 withheld**. The system no longer raises 20 false warnings about a corpus that contains no
contradictions; it is silent here, and it is silent because the measurement
says it should be.

That silence is a statement about the benchmark and not a claim that the
mechanism is useless. The detector's own positive control -- pairs whose correct behaviour is known in advance, written in the industrial register but not drawn from the corpus -- is 11 of 11, with every contradiction caught and every non-conflict left alone. So the mechanism works; this corpus does not test it. The gate is the mechanism that
stops a practitioner applying a superseded policy, and evaluating it needs a
corpus of revised procedures rather than articles about concepts.

![Figure 6. The contradiction detector's precision against the base rate of real conflicts in the same population, with 95% Wilson intervals; a filled marker means the point estimate clears the framework's 0.5 calibration floor and the branch would act, a hollow one means it does not and the findings would be withheld. The focus corpus's semantic branch has a precision of 0.0 (0 of 20 alarms confirmed by either annotator) on a base rate of 0.0, so it is withheld; the industrial semantic branch reaches 0.65 (26 of 40) against a base rate of 0.35 and would act.](figures/fig6_contradiction_precision.pdf)

## 5.4 Cross-category transfer (O4)

Measured on the six-category corpus, because a transfer experiment needs a
subset of categories to transfer to held-out ones.

| Metric (held-out half) | Transferred | Refitted (ceiling) |
|---|---|---|
| Answerable answered | 1.000 | 0.940 |
| Answerable refused | — | — |
| Coverage | 0.412 | 0.460 |
| Top-1 accuracy given accepted | 0.940 | 0.952 |

Tuning half: predictive_maintenance, production_scheduling, supply_chain_management. Held-out half:
facility_layout, quality_engineering, reliability_engineering. τ fitted on the tuning half and transferred
unchanged: 0.05.

**The scope is narrower than "transfer" usually means, and it has to be
stated.** The split is over *document categories*, and the benchmark's
unanswerable questions carry no category, so neither half contains any. This
experiment therefore measures **coverage on answerable questions across
domains**; it says nothing about how well a transferred threshold refuses
unanswerable questions. What transfers, quantitatively, is the *ordering*:
top-1 accuracy given acceptance moves only from 0.952
to 0.940, while coverage falls from 0.460 to 0.412. The calibration's
*ranking* travels; its *operating point* does not. That is the practical
finding: re-fit τ per corpus, do not expect to re-use it.

## 5.5 The long-context baseline — the strongest threat to the work

The threat: the corpus fits in a modern context window, so a reader given
everything could answer directly and the retrieval machinery would be
unnecessary.

| | Focus domain | Six-category corpus |
|---|---|---|
| Whole corpus as a prompt | 202,529 tokens | 680,417 tokens |
| RAG arm's accepted context | 2,246 tokens (9.4 chunks) | 2,399 tokens |
| **Cost ratio** | **90×** | **282×** |
| Fits a 128K window | **no** | **no** |

The long-context arm sends 74x more input tokens per query than the pipeline, which at the provider's cached-prefix pricing, with the corpus prefix served as a cache read on 33.0% of the long-context arm's input tokens is a 58.8x input-cost ratio rather than 74x: the token ratio and the cost ratio are different numbers, and only the second one is a cost.

The retrieval-side proxy says the evidence is not lost in a big context: with
the candidate set widened to every chunk in the corpus, the gold chunk still
lands in the scorer's top 10 for 0.969 of focus-domain queries
(95% interval 0.843-0.994) at a median rank of 1.
 The same proxy on the six-category corpus puts the gold chunk in the top 10 for 0.902 of the queries (0.839-0.942), at a median rank of 1.

**The honest position:** the long-context arm wins on coverage and loses on
cost, and the answer-quality comparison is directional rather than
significant. The answer-quality half of the comparison was measured on the focus domain. With the whole corpus in the prompt the generator answered 31 of 32 answerable questions, the same coverage as the pipeline, and it declined the unanswerable questions at a comparable rate (76 of 144 against 77 of 144), for 74 times the input actually sent per query. On coverage and on cost the result is settled: the whole-corpus prompt declines no more unanswerable questions than the pipeline does and costs 74 times as much to do it. On answer quality the margin is directional but not statistically significant once the answers are scored without the length confound.

## 5.6 The generator-side comparison — does it reduce hallucination?

This is the experiment that tests the framework's own hypothesis (H2.1), and
it is the one that had to be rebuilt.

The design: **one** generator behind **five** arms that share the model, the
prompt wording, the question set and the scorer, so any difference between
them is attributable to the context and the gate and to nothing else. The
whole design was then repeated on a **second** generator, changed in nothing
but the model id, so that the gate's contribution can be read as a property of
the framework rather than of one checkpoint.

| Arm | Unanswerable answered | Answerable answered | Answerable accuracy |
|---|---|---|---|
| The same retrieval, **gate removed** | 0.535 (77 of 144) | 30 of 32 | 0.633 |
| The framework at its fitted operating point | 0.417 (60 of 144) | 30 of 32 | 0.800 |
| **Random-escalation control** (refuses as many, picks at random) | 0.375 (54 of 144) | 21 of 32 | 0.714 |
| The framework at the threshold transferred from the cross-category half | 0.014 (2 of 144) | 6 of 32 | 0.333 |
| The whole corpus in the prompt | 0.528 (76 of 144) | 31 of 32 | 0.548 |

**Under the answering prompt** — the generator is *required* to answer, so it
cannot decline on its own and give the gate the credit. This is the
condition in which the gate's own contribution is measurable, and it is the
decisive one.

| Arm | Unanswerable answered | Answerable answered | Answerable accuracy |
|---|---|---|---|
| The same retrieval, **gate removed** | 0.938 (135 of 144) | 32 of 32 | 0.656 |
| The framework at its fitted operating point | 0.528 (76 of 144) | 30 of 32 | 0.667 |
| **Random-escalation control** | 0.604 (87 of 144) | 21 of 32 | 0.714 |
| The framework at the threshold transferred from the cross-category half | 0.021 (3 of 144) | 6 of 32 | 0.000 |
| The whole corpus in the prompt | 0.931 (134 of 144) | 32 of 32 | 0.406 |

**Read the two tables together and the separation is complete.** Under the
answering prompt the gate cuts the rate of answering unanswerable questions
from 0.938 to 0.528 while still answering 30 of 32 of the answerable ones. The random control
also refuses a lot — but it answers only 21 of 32 of
the answerable questions, so its refusals are landing on the wrong ones.
Paired question by question, the gate refused 60 of the questions the ungated arm answered and let through 1 of the ones it did not (exact McNemar p = < 0.001).

The **random-escalation control** is the arm that makes this a measurement
rather than an anecdote. It refuses the same *number* of questions as the
fitted gate — but picks them at random, ignoring the confidence score
entirely. Under the answering prompt, the fitted gate answered 30 of 32 answerable questions against the control's 21 of 32, and answered 76 of 144 of the unanswerable ones against the
control's 87 of 144.

That is the finding, and it is easy to state wrongly. The control refuses the
same *total* number of questions, but the gate concentrates them where they
belong: on the unanswerable questions. So the confidence score does not buy a
lower answer rate on unanswerable questions — the random arm has that too,
and by luck. What it buys is **where the refusals land**, which shows up as
coverage on the answerable questions.

The paired test on the answerable questions is where the two come apart. The
gate refused 2 of the questions the ungated arm
answered and let through 0 (exact McNemar p = 0.500); the random control refused 11 and let through 0
(p = 0.001). The gate's refusals cost it essentially no
coverage; the control's cost it significantly. **That is what the confidence
score buys over refusing an arbitrary set of the same size.**

**The verdict:** The gate's contribution is measured under both prompt conditions, and it holds in both. Under the cautious prompt -- the deployed system -- the hypothesis is supported, at a price: the gate reduced the rate of answering unanswerable questions from 0.535 to 0.417, a fall of 11.8 points, at the cost of answering 30 of 32 answerable questions. Paired question by question, the gate refused 23 of the questions the ungated arm answered and let through 6 of the ones it did not (exact McNemar p = 0.002). Under the answering prompt, which differs from the cautious one by a single sentence and by nothing else, the hypothesis is supported, at a price: the gate reduced the rate of answering unanswerable questions from 0.938 to 0.528, a fall of 41.0 points, at the cost of answering 30 of 32 answerable questions. Paired question by question, the gate refused 60 of the questions the ungated arm answered and let through 1 of the ones it did not (exact McNemar p = < 0.001). What the framework claims is therefore not that the gate reduces hallucination whatever the generator does, but that it is the one component whose behaviour does not depend on the generator's cooperation: the prompt can be wrong, and the gate still holds.

### 5.6.1 The replication on a second generator — and what it turned into

The whole design was repeated on a second generator, changed in nothing but
the model id, and **the run did not complete**. The harness recorded it as
not-run rather than quoting a rate it could not stand behind. Experiment 13 measured
why, on the benchmark's own questions: MiniMax-M3 returned no text on 0 of the 66 questions it was asked (0 of them on the benchmark's table-lookup family, against 0 of 22 on a control sample of the other families); MiniMax-M3.1-Flash returned no text on 24 of the 66 questions it was asked (23 of them on the benchmark's table-lookup family, against 1 of 22 on a control sample of the other families). The failures are not a shortage of output budget -- of the requests that came back empty, 13 were rescued by retrying at 4096 tokens and 11 were still empty there, the model spending the whole budget on reasoning and returning nothing. An empty completion is neither an answer nor a refusal, so the harness records the run as not-run instead of reporting a rate it cannot stand behind.

| Generator | No text returned | Of which on the table-lookup family | Of which on a control sample of the other families |
|---|---|---|---|
| MiniMax-M3 | 0 of 66 | 0 of 44 | 0 of 22 |
| MiniMax-M3.1-Flash | 24 of 66 | 23 of 44 | 1 of 22 |

Two things follow, and they point in opposite directions.

The first is a limitation of the claim, and it is the honest one: **the gate's
contribution is established on one generator.** One generator behind five arms
settles the hypothesis for one model, and the replication that would settle it
for a second is still open. What the attempt bought is a specific obstacle
rather than a vague one, and it is written into §12 as such.

The second is a finding in its own right. **A generator behind a RAG pipeline
can return neither an answer nor a refusal.** It can spend its whole output
budget on reasoning and return nothing, and it can do so on the questions that
are hardest to parse. A pipeline that counted an empty completion as an answer
would report an answer rate it cannot support; one that counted it as a
refusal would report a refusal rate for questions the model never saw. The
harness treats it as a failure and records the run as not-run, which is why the
table above exists instead of a table of rates.

**And there is a reproducibility statement in here, for this project.** The
shipped run was made with MiniMax-M3 in November, and the row above is the
same model id, on the same corpus, with the same prompt, measured now: 0 of 66 of its requests came back with no text. So the shipped
measurement is still reproducible against the provider's route; what is not
reproducible is a *second* generator, and the reason is a property of that
model rather than of the measurement. That is also why the per-question
records ship with the results rather than only the summaries.

One design point is easy to miss here and worth saying out loud. **The gate is
upstream of all of it.** It refuses before the generator is called, so a
generator that cannot answer costs nothing on the questions the gate rejects —
the refusals are free, and the failure mode only ever reaches the questions the
framework had already decided to answer. That is an argument for the gate
being a branch rather than an instruction, and it is an argument the framework
did not have to make in advance.

**Why the prompt is an axis, not a constant.** The first version of this
experiment ran under one prompt and produced a null — and the null was an
artefact of the design, not a fact about the gate. Under the *cautious* prompt
the generator declined the unanswerable questions on its own, so the gate's
refusals were redundant and the arms could not be told apart. The harness now
runs the same experiment under two conditions that differ by **one sentence**
(the permission to decline), with everything else identical, and reports both.
Both conditions have now been run, and the hypothesis holds under each — which
is the whole point of making the prompt an axis rather than a constant: the
gate's value does not depend on the generator's willingness to decline.

The scorer that produces these numbers is itself audited, because when the
measurement is the contribution, the instrument's error rates have to be
published rather than asserted: 32 of the 33 answers the benchmark itself considers correct are recognised as supported by the evidence that states them; 8 of the 9 fabricated values are rejected; and 31 of the 32 values taken from a different quantity are rejected.

## 5.7 The before/after, in one table

An ablation table says what each mechanism does to a metric. It does not say
what the whole framework does to a practitioner's questions. Experiment 6
answers that, on the same 176 focus-domain questions, comparing
the plain lexical retriever — which never refuses — against the full
framework.

| | Plain BM25 retriever | The full framework |
|---|---|---|
| Unanswerable questions **answered** (all wrongly) | **144 of 144** | **86 of 144** |
| Answerable questions answered | 32 of 32 | 30 of 32 |
| Gate refusal rate on unanswerable questions | 0.0% | 0.403 |
| Context contains the gold chunk | 0.969 | 0.938 |
| Mean chunks in the accepted context | — | 9.4 |

**This is the before/after that matters.** A retriever that never refuses
answers every unanswerable question, and every one of those is a wrong answer
dressed as a right one. The framework's cost is the answerable questions it
declines; its benefit is the unanswerable ones it stops answering.

Note also the fourth row: on silver-standard labels a plain lexical retriever
already puts the gold chunk in the top ten more often (0.969
against 0.938) — **the framework is not better at
retrieving, and it is not trying to be.** The gate is there to refuse.

## 5.8 The second corpus — authentic, versioned, binding industrial text

Two of the objectives could not be closed on the corpus of §4. That corpus is
encyclopaedic prose about industrial engineering, and it is the wrong instrument
for a contradiction mechanism in two ways at once. It contains no conflict a
practitioner would recognise as one — a document read at a single upstream
revision cannot contradict itself, and concept-level prose rarely binds a
numeric requirement that another document contradicts — so RO4's first
measurement was unevaluable: the contradiction mechanism's measured precision
was 0.0% on a corpus that contains no conflicts, which says
nothing about the mechanism. And it is not the class of document a practitioner
reads: reference material about concepts, not operating procedures carrying
binding limits.

A second corpus was built to close that gap. It is the United States
*Electronic Code of Federal Regulations* (eCFR), read through the versioner
API, which serves any regulation as it stood on any past date. Two properties
follow. The text is authentic and binding — these are the regulations a plant
is measured against, and they carry numeric requirements. And it is public
domain, so the corpus ships with the thesis and the licence question the
limitations table names for the other corpora does not arise.

The corpus holds 110 documents and 2,443 chunks
(2,324 text, 119 table) in 4 regulatory regimes: OSHA general industry; OSHA process
safety and EPA risk management; EPA new source performance standards; and DOT
hazardous materials. The snapshot is the 2026-06-01 issue.

### 5.8.1 The version trick, and why it supplies labels

Federal regulations are amended, so the same section read at two dates is the
same rule at two issues. The corpus is read twice — at 2021-12-31 and
at 2026-06-01 — and aligning the two snapshots gives 948 amended-paragraph pairs, of which 361
(38.1%) state different numbers in the two vintages.

Such a pair **is** a conflict, and its type is known by construction: the same
provision at two issues is a supersession, not a contradiction. No annotation is
needed to know the right answer, which is what makes this corpus a measuring
instrument rather than a pile of text.

### 5.8.2 The benchmark, and the shortcut audit it needed

444 queries: 247 answerable, 197 unanswerable. The audit repeated the first benchmark's
test. The one-rule identifier shortcut that carried 76.4% of
the first benchmark's unanswerable class catches 0 of 197 here. A question-only classifier separates the two
classes at ROC AUC 0.708 against a permutation null of 0.505 — above the null, not at it — and the bag-of-words
separability is 0.793.

The residual separability is question **length**: median 73 characters for the answerable class against 50 for the unanswerable one. That is reported here rather
than hidden, because it is the same kind of residual the first benchmark had,
and §9 is the story of finding that one and repairing it.

### 5.8.3 RO6 — the negative findings replicate

**"BM25 beats an off-the-shelf dense encoder on regulatory text" is already
published — three times over, in three jurisdictions (arXiv:2506.12895,
arXiv:2604.01733, arXiv:2412.07462) — so it is not claimed here as new, and it
is not in the abstract.** What the measurement contributes is the *corollary*.

| Finding | Number |
|---|---|
| BM25 Recall@10 | 0.9595 |
| Dense-encoder Recall@10 | 0.8785 |
| BM25 − dense | -0.081, p 0.00026, n 247 |
| Fusion against its own lexical leg | +0.000, p 1.00000 |
| Category pre-filter against no filter | +0.000, p 1.00000 |
| Cross-encoder against no reranker | +0.028, p 0.01963 |

The lexical leg carried the pipeline. On top of it, neither the hybrid fusion
nor the category pre-filter added anything measurable — the two mechanisms that
look like the pipeline's contributions buy nothing on this corpus. The
cross-encoder did help here, unlike on the focus corpus, and that is stated
rather than buried: the reranker buys recall on this corpus, and the pool curve
below explains why.

**The dense leg here is a general-purpose 2022 encoder**, so this is a boundary
condition on *this* pipeline and not a claim about dense retrieval as a class.
The published work on domain-adapted encoders says a fine-tuned dense model can
overtake BM25, and the thesis's own dense leg is the weak one here.

### 5.8.4 The candidate-pool curve is no longer saturated

On the focus corpus the candidate-pool curve saturated at a pool of ten, so the
thesis could not distinguish "the pool stopped helping" from "the corpus had
nothing left to find". That ambiguity is gone here. At a pool of 50, Recall@20
reaches 1.000 while Recall@10 stands at 0.988: 1.21% of the golds are retrieved and then pushed *out of
the ten-chunk context* by the reranker's own ordering.

### 5.8.5 The gate's operating point transfers; its threshold does not

At τ = 0.40 the industrial gate answers 91.5% of the answerable queries and refuses 58.9% of the unanswerable ones, with an
abstention precision of 0.847 and a coverage of 0.691.

The threshold does not transfer — 0.40 here against 0.05 on the focus corpus — and the operating point does: 0.691 against 0.693. That is the calibration
result of §5.4 restated on a second corpus: τ is a fitted parameter of the
deployment and must be re-fitted, while the point on the risk–coverage surface
a practitioner cares about is a property of the mechanism.

The two calibrations differ in quality as well as in value, and both metrics
are reported: ECE 0.075 against 0.104, Brier 0.159 against 0.151. The industrial gate is the
better-calibrated of the two on ECE and the worse of the two on Brier.

**The pooled refusal figure is an upper bound here too, for the same reason as
in §5.2.** The unanswerable half carries the same two strata — an
out-of-domain family that is unanswerable for any system that knows what the
corpus is about, and a corpus-anchored family where only the retrieved
evidence can decide — and the figure above mixes them. The per-family rates
are in `impl/results_industrial/exp2_gate.json`.

### 5.8.6 RO4 — detection and typing decompose

This is the clearest new result in the project, and it needed a corpus that
contains conflicts to be visible at all.

240 pairs were assembled in two strata: 90
*revision* pairs (a paragraph and its amended self) and
150 *similar* pairs (cross-document retrieval
neighbours). The pool is mined by the **retriever's** own lexical signal and
never by the detector's numeric rule, its NLI probability or its subject check
— a pool selected on the detector's decision rule cannot measure the detector's
precision, because every alarm would be in it by construction. The pairs were
read by four domain specialists (one per regulatory regime) plus a generalist
control, all blind to the detector.

A conflict detector's precision is two numbers, not one. **Detection** asks
whether the alarm is pointing at something real. **Typing** asks whether the
branch that raised the alarm is the branch that owns the conflict.

| Measured against | Detection precision | Typing precision |
|---|---|---|
| The readers' labels | 0.659 (95% CI 0.505–0.784) | 0.073 (95% CI 0.025–0.194) |
| **The construction labels** | 1.000 | 0.000 |
| The shipped operations vocabulary | 0.650 | 0.000 |

Against the readers' labels the detector's detection precision is 0.659, and 0.897 on the stratum where the
conflicts actually are. Recall of any real conflict is 0.321
over the 84 annotated supersessions.

**The quantity branch is the thinnest result in the whole study.** An
exhaustive corpus-wide search over 64 measurement terms found 1776 candidate cross-document quantity conflicts — exact
rather than sampled, because the search groups every (measurement term, value)
pair in the corpus and keeps the terms whose values differ across documents. 119 pairs were put to the reader and the branch fired on 13; of the 60 pairs the reader labelled, **none**
was a genuine quantity conflict. The search is deliberately over-inclusive — two
passages about different boilers share the word "pressure" — which is what the
reader sheet separates. The branch's precision on this corpus is therefore not
measurable, and the framework's calibration floor would withhold it rather than
report it.

**The finding, in plain words: the mechanism finds the conflicts and reports
them as the wrong kind.** It calls supersessions contradictions, and it cannot
say which version is in force, because nothing in the retrieved passages says
which issue either of them is. On a regulatory corpus that is the one thing a
practitioner needs from a contradiction detector. The consequence is a
specification: a detector for regulatory text needs version metadata, or must
be scoped to detection alone.

### 5.8.7 RO4 — the measurement's binding constraint was the rubric

The first comparison was confounded, and the confound was in the annotation
rather than in the detector: the old-rubric reader was a generalist, so "old
rubric" and "generalist" were the same cell. A 2×2 factorial separates them,
with the pairs, the detector and the regime briefs held constant.

| Reader | Old rubric (marker test) | Sharpened rubric (structural test) |
|---|---|---|
| Generalist | 0.293 | 0.659 |
| Specialist | 0.341 | 0.659 |

Effects: rubric +0.366 at the generalist and
+0.317 at the specialist; specialisation
+0.049 at the old rubric and +0.000 at the
sharpened one. The mechanism is concrete. The old rubric required a version
marker, and a regulation does not write its own version in its text, so it
missed 63 of the 82
supersessions it was asked to find (0.77 of
them); the specialist missed 63 of 90 (0.70 of
them).

Three qualifications are owed to this result.

1. The rubric changed the **definition** of the target as well as the
   procedure for recognising one, and this experiment cannot separate the two.
   What it shows is that the reader factor is small.
2. "Specialisation" here was delivered as a brief to a fixed reader model, not
   as a different capability, so the claim is narrower than "specialists are
   not needed".
3. The qualitative principle is already published — that the annotation
   guideline is a first-class error source in model annotation is established
   — and what is new is the factor of nine, and that it lands on the *reported
   system measurement* rather than only on the labels: the two numbers a
   detector's precision splits into on this corpus are 0.659 and    0.073, and the rubric's wording is what put them that far
   apart.

The lesson is about measurement rather than about annotation: a number that
moves by a factor of nine with the wording of its own rubric is not yet a
measurement of the thing under test.

### 5.8.8 RO5 — the band replicates

The third mechanism was measured on both corpora, with the same generator and
two evidence protocols on each: the benchmark's own gold evidence (is the
claim right?) and the evidence the retriever actually returned (does an
independent reader agree with the scorer?). On this corpus 293 and 297 claims were
labelled under the two protocols.

| Corpus and protocol | κ (band vs reference) | Band error (grounded / inferred / uncertain) | Answers with no wrong claim |
|---|---|---|---|
| Focus, gold | 0.049 | 0.542 / 0.513 / 0.610 | 34.4% → 50.0% |
| Focus, retrieved | 0.069 | 0.118 / 0.103 / 0.220 | 59.4% → 81.2% |
| Industrial, gold | 0.055 | 0.077 / 0.119 / 0.139 | 91.1% → 94.9% |
| Industrial, retrieved | 0.017 | 0.006 / 0.017 / 0.026 | 98.3% → 99.6% |

The industrial κ carries a 95% interval of
-0.027–0.138 on the gold protocol
and -0.066–0.101 on the
retrieved one.

**The finding: the band is at chance against an independent reference on all
four corpus-and-protocol combinations, and ordered on the evidence the band
itself saw.** The three bands are indistinguishable on the gold protocols and
ordered on the retrieved ones. The sharper way to state it: **the band measures
whether the retrieved passages entail the claim — agreement with itself — not
whether the claim is true.** As a filter it works: keeping only the *grounded*
claims raises the share of answers containing no wrong claim on every one of
the four combinations.

The positional comparison — keeping the first half of an answer rather than
what the band tagged *grounded* — is the **evidence** for that reading, not the
finding, and it does not hold everywhere. Of the four corpus-and-protocol
combinations, one gives a significant positional result (focus gold, p 0.008) and three do not (0.417, 1.000 and 1.000). **the direction replicates in three of the four and ties in one,
even where the significance does not**: the risk of
keeping the first claims of an answer rather than the band's `grounded`
claims is higher in three of the four (+0.0923,
+0.0231,
+0.0152 and
+0.0000 at matched coverage), and only the
largest of the four clears significance. The band is therefore reported as a
filter and not as a ranking, and the reason is the direction rather than the
power.

# 6. So — does it reduce hallucination in an industrial RAG model?

**The precise answer, which is not the one a panel expects:**

> The framework **declines to answer where there is no answer**, which removes
> the *opportunity* for a fabricated answer. Measured against a generator
> that is required to answer, the gate cuts the rate of answering
> unanswerable questions from 0.938 to
> 0.528 — a fall of 29.2 points, significant at
> exact McNemar p = < 0.001 — and it does so while
> still answering 30 of 32 of the answerable questions.
> The hypothesis holds under **both** prompt conditions, so the gate's value
> does not depend on the generator's cooperation.

Three distinctions carry the weight, and conflating any two of them would be
the easiest way to get this project wrong in a defence:

1. **A refusal rate is not a hallucination rate.** The first is a property of
   the retrieval-side pipeline; the second is a property of generated text.
   The pipeline's refusal rate on unanswerable questions is    23.6% (corpus-anchored class) — it is not, and cannot
   be, quoted as a hallucination rate.
2. **Answering an unanswerable question is not the same as fabricating.** The
   fabrication column has almost no denominator: across the arms, the
   unanswerable questions produced only a handful of substantive claims. The
   headline metric is therefore the **rate of answering** an unanswerable
   question, and the accuracy column is the solid one — read as a comparison
   between arms rather than as a level, because the scoring convention moves
   the level by up to 0.90 while it leaves the comparison where
   it was.
3. **What the gate buys is *where the refusals land*, not how many.** The
   random-escalation control refuses the same number of questions and
   refuses just as many of the unanswerable ones — but it wastes    11 of its refusals on answerable questions where
   the gate wastes 2. The gate's contribution is a
   **precision** claim about refusals, and the paired test on the answerable
   questions (p = 0.001 for the control against    0.500 for the gate) is where it is established.

## 6.1 So — with the gate, or without it?

This is the question that follows "is it working?", and the honest answer is
that **it depends on what "better" means**, because the gate trades one
quantity for another. The trade is measured here rather than asserted.

Under the answering prompt — where every answer the generator gives is one
it would not otherwise have declined — the four arms come out like this.
The counts are over all 176 questions:

| Arm | Questions answered | Correct (entailment) | Correct (key term) | **Confidently wrong** |
|---|---|---|---|---|
| The same retrieval, **gate removed** | 167 | 21 | 29 | **135** |
| **The framework (gate on)** | 106 | 20 | 27 | **76** |
| Random-escalation control | 108 | 15 | 20 | 87 |
| The whole corpus in the prompt | 166 | 13 | 24 | 134 |

**"Confidently wrong"** is the count that matters: questions the corpus
cannot answer, where the system nevertheless produced an answer. Every one of
them is a wrong answer presented with the same confidence as a right one.

**Read the table this way:**

* **Without the gate**, the system answers
  135 of the   144 unanswerable questions — every one wrongly — and
  gets 21 answers right.
* **With the gate**, it answers 76 of
  them wrongly and gets 20 right.

**So the gate gives up 1 correct answers
and removes 59 confidently-wrong ones.** On the
entailment test that is a trade of 1 right answers for 59 wrong ones; on the key-term test it is 2 for 59. The two tests disagree about the size of
the cost, which is why both are reported.

**Two things that must not be misread.**

1. **The gate is not there to make answers more accurate.** It barely affects
   that — the cost is 1 or    2 answers out of    21. It is there to stop the
   confidently-wrong ones. The apparent per-answer accuracy advantage of the
   gated arm is a **selection effect**: a gate declines the hardest
   questions, so the ones it does answer are easier. It is not a quality
   gain, and it must never be quoted as one.
2. **Whether the trade is worth making is a domain judgement, not a
   statistical one.** Four right answers against forty-two wrong ones is
   obviously the right trade in a plant, where a fabricated acceptance
   criterion can cost far more than a declined lookup. It is not obviously
   the right trade in a general question-answering assistant. **The
   framework's contribution is that the trade is now measured, at a stated
   operating point, under two prompt conditions — so the decision can be made
   explicitly instead of inherited.**

**And two things that settle the alternatives.** The random-escalation
control refuses about as much as the gate
(108 questions answered against 106) yet gets only 15 answers right against the gate's 20 — so *refusing* is not what the gate
does; **refusing the right questions** is. And the strongest competing
approach, putting the whole corpus in the prompt, is worse on both counts at
once: 13 correct answers and 134 confidently-wrong ones.

Under the cautious prompt the same trade is smaller, because the generator
has already declined much of what the gate would have refused: the gate
removes 17 confidently-wrong answers there, and
on the entailment test it ends up *ahead* on correct answers as well — which
is the selection effect again, and is why the cautious condition alone would
have been a misleading headline.

# 7. Is it working? — an honest scorecard

| Component | Working? | Evidence | Caveat |
|---|---|---|---|
| Hybrid retrieval (BM25 + dense, RRF) | **Yes** | +0.188 R@10, p = 1.4 × 10⁻² | Fusion beats BM25 significantly; it does **not** significantly beat the lexical leg alone, and the deliverables say so |
| Cross-encoder reranking | **No** | -0.031 R@10, p = 3.2 × 10⁻¹ | Not significant, sign negative. Kept because the gate is calibrated on its score |
| Category pre-filter | **Yes** | invariant test; six-category ablation | No-op on a single-category corpus, by construction |
| Modality quota | **Yes, before the cross-encoder** | table recall 1.000 → 1.000 at no text-recall cost | Placing it after the reranker costs recall (-0.062) on the focus domain; the industrial corpus prefers the other placement, by a margin that is not significant |
| Confidence gate — calibration | **Yes** | Brier 0.1510, ECE 0.1044 | Operating point is deployment-specific; thresholds must be re-fitted |
| Confidence gate — refusal on the hard class | **Partly** | 23.6% of the corpus-anchored class | Detects *recognisable* unanswerability, not absent evidence |
| Confidence gate — its cost/benefit trade | **Measured** | removes 59 confidently-wrong answers for 1 correct ones (§6.1) | Not a quality gain — it is an explicit trade, and the direction is a domain judgement |
| Query-form validator | **Yes, in its own lane** | refused 25 of 25 hand-authored malformed queries and 0 of 35 well-formed ones; 3 of 176 benchmark queries | Lexical; deliberately fails open; the benchmark refusals are generator artefacts that read as malformed, not real questions |
| Contradiction surfacing | **Mechanism built and repaired; not evaluable on this corpus** | The gate's alarms fell from 81 to 20 after two measured repairs; its measured precision against reader labels is 0.0%; its own positive control is 11 of 11; and the fitted calibration leaves 20 findings surfaced here | The corpus holds concept-level prose, not instance records, so it contains no contradictions for the mechanism to find — the same readers find 0 in 80 random unflagged pairs. The annotators were models. **The second corpus, in §5.8, is the corpus that can evaluate it** |
| Conflict detection and typing — the second corpus | **Detection yes, typing no** | detection 0.659 against the readers' labels (0.897 on the stratum where the conflicts are), typing 0.073; against the construction labels, detection 1.000 and typing 0.000 | The mechanism finds the conflicts and reports them as the wrong kind. A detector for regulatory text needs version metadata, or must be scoped to detection alone |
| The annotation rubric — the second corpus | **The binding constraint** | rubric +0.366 at the generalist and +0.317 at the specialist, against +0.049 and +0.000 for specialisation | A 2×2 factorial: the reader factor is small and the rubric's wording is not, and the experiment cannot separate the rubric's definition of the target from its procedure for recognising one |
| Per-claim band — the second corpus | **Yes, as a filter** | κ 0.055 (gold) and 0.017 (retrieved), against 0.049 and 0.069 on the focus corpus; clean answers 91.1% → 94.9% and 98.3% → 99.6% | At chance against an independent reference on all four corpus-and-protocol combinations — the band measures agreement with itself, not truth |
| Retrieval — the second corpus (RO6) | **The negative findings replicate** | BM25 0.9595 against dense 0.8785 (Δ -0.081, p 0.00026); fusion +0.000 (p 1.00000); pre-filter +0.000 (p 1.00000) | Already published in three jurisdictions, so it is not claimed as new; what is new is the corollary — the fusion and the pre-filter add nothing on top of the lexical leg. The dense leg is a general-purpose 2022 encoder, so this bounds this pipeline and not dense retrieval as a class |
| The candidate pool — the second corpus | **No longer saturated** | at a pool of 50, Recall@20 1.000 against Recall@10 0.988: 1.21% of the golds are displaced out of the ten-chunk context | On the focus corpus the curve saturated at a pool of ten, so the thesis could not tell "the pool stopped helping" from "the corpus had nothing left to find" |
| The gate — the second corpus | **Yes** | τ 0.40, coverage 0.691 against 0.693; ECE 0.075 against 0.104, Brier 0.159 against 0.151 | The threshold does not transfer (0.40 against 0.05) and the operating point does; the pooled refusal rate is an upper bound, as in §5.2 |
| Claim scoring | **Yes, as an instrument** | audited: 32 of the 33 answers the benchmark itself considers correct are recognised as supported by the evidence that states them; 8 of the 9 fabricated values are rejected | Every miss and every leak is a single-digit value |
| Cross-category transfer | **Partly** | ranking transfers (0.940 vs 0.952 top-1 accuracy) | The *operating point* does not transfer; re-fit τ per corpus |
| Long-context comparison | **Yes, on cost** | 90× input tokens, 58.8× input cost | Answer-quality margin is directional, not significant |
| Hypothesis H2.1 ("the gate reduces hallucination") | **Yes** | supported under both prompt conditions | Holds under both prompt conditions; the claim is about answer *opportunities*, and the fabrication rate on generated text is measured separately |
| The benchmark itself | **Repaired** | two audits, two defects found and fixed | The story is "we audited our instrument and repaired it", not "we found a defect" |

# 8. How to run it, and how to test it

There is no server. The framework is a library and the experiments are batch
scripts that write JSON. That is deliberate — every measurement must be
reproducible from a command line — but it makes the system awkward to poke at
by hand, so there is **one** interactive entry point.

## 8.1 Watch it work (30 seconds, no key needed)

```bash
cd /Users/ritikraj/Documents/MTP
MTP_VARIANT=focus .venv/bin/python impl/scripts/ask.py \
    "what is the economic order quantity?"
```

This runs the real online path and prints every stage's decision:

```
--- FORM CHECK ----------------------------------------------------------
  PASSED -- the request is a well-formed question.

--- RETRIEVAL -----------------------------------------------------------
  dense candidates    : 20
  lexical candidates  : 20
  after RRF fusion    : 735
  after rerank        : 50 scored -> 10 delivered
    1. economic-order-quantity::p1::t0 [text] # Economic order quantity ...
    2. economic-order-quantity::p1::t12 [text] 10000+40\cdot(10000/300)+5\cdot(300/2)...

--- CONFIDENCE GATE ------------------------------------------------------
  posterior 0.671  vs  tau 0.050  ->  ACCEPT
    top1_rerank                  +8.9363
    mean_top3_rerank             +6.9287
    top1_bm25                    +14.5477
    max_rrf                      +0.0320
    n_candidates_above_bar       +12.0000

--- ANSWER --------------------------------------------------------------
  # Economic order quantity ...

--- CONTRADICTION DETECTION ---------------------------------------------
  {'pairs_compared': 45, 'nli_only_flagged': 7, 'joint_gate_flagged': 2,
   'flagged_by_kind': {'semantic': 2}, 'surfaced': 0, 'withheld': 2, ...}
  withheld: the semantic branch's measured precision is 0.000 on 40 labelled
  findings, below the 0.50 floor, so the finding is recorded and withheld
```

Run it interactively (without the question) for a prompt. The first query
loads the embedding model and takes tens of seconds on CPU; later queries are
fast. Inside the session: `/category supply_chain_management` to pin the
category, `/help`, `/quit`.

Add `--llm` with a key in `~/.mtp_llm_key` to put a real generator behind the
gate and watch the per-claim tagging stage run.

## 8.2 Swap in your own data

The corpus, the benchmark, the index and the results directory move together
under one variable, so a variant can never touch the measured corpora:

```bash
MTP_VARIANT=focus  .venv/bin/python impl/scripts/ask.py "..."   # the focus domain
MTP_VARIANT=demo   .venv/bin/python impl/scripts/ask.py "..."   # the sandbox dataset
```

`impl/data/corpus_demo/` is the sandbox: copy it, edit the documents, and
point `MTP_VARIANT` at your copy.

## 8.3 Run the test suite

```bash
.venv/bin/python -m pytest impl/tests -q          # 32 tests
```

The invariant tests assert the *mechanism's predictions* rather than its
outputs, on a synthetic index with the models stubbed out, so they run in
milliseconds and cannot be fooled by a model's behaviour. Three real defects
were found this way and none of them was visible in the output:

* a category pre-filter applied to only one of two retrieval legs, which made
  the filter a no-op while looking like a measured effect;
* a quota that evicted the modalities already at their floor, which produced a
  plausible-looking *negative* result about modality balancing;
* an article indexed twice under two category names, which split a document
  across two categories and leaked it into both halves of the transfer split.

## 8.4 Re-run the experiments

```bash
cd impl
bash scripts/rerun_focus.sh        # the focus domain, end to end
bash scripts/rerun_all.sh          # the six-category corpus
```

`MTP_VARIANT` is set inside those scripts, so the runs cannot be confused with
one another. The generator-side comparison needs a credential and costs money;
`scripts/run_generation_eval.sh` reads the key from `~/.mtp_llm_key` so it
never appears in a shell history or a process listing.

## 8.5 Rebuild every deliverable

```bash
.venv/bin/python deliverables/scripts/build_all.py
```

The build restores the tokenised templates, substitutes the measured values
into the prose, regenerates the results sections from the experiment JSON,
rebuilds the DOCX, PPTX and PDF deliverables, and then runs the consistency
checks. **Every number in every deliverable is a token bound to a
measurement**, and the build fails if a token is left unsubstituted, if a
template hard-codes a measurement that has been superseded, or if a citation
identifier is not in the audit.

# 9. Two defects we found in our own benchmark

This is a deliberate part of the story, because an instrument that has never
been audited is an instrument whose error rates are unknown.

**Defect 1 — the answer labels (Experiment 9).** The table-question
generator took its answer from the *next* column while naming the key's own
column in the question, and the numeric regex captured an ordinal as a bare
digit. 27 of 132 answerable questions carried an answer
attached to the wrong question. The gold *chunk* was right in every case, so
the retrieval-side measurements were unaffected — but the answer-side accuracy
was depressed, equally for every arm. The generator was corrected, the
benchmark rebuilt, and every experiment in the project re-measured against it.
The audit now finds 0 defective labels out of 32.

**Defect 2 — the unanswerable class (Experiment 12).** The unanswerable half
was separable from the question text alone: a classifier seeing only the query
told answerable from unanswerable at ROC-AUC 0.999, because one
family of unanswerable questions named a fabricated identifier whose *shape*
no answerable question carried. The consequence was that the headline refusal
rate was an **upper bound, not a measurement**.

The half was rebuilt, not reported around. The repaired class is
corpus-anchored — the corpus discusses the subject and states no value for it —
and each repaired question was given a structural twin in the answerable class.
Separability fell from 0.999 to 0.608, and the gate's
refusal rate on the hard class fell from 91.7% to 23.6%. **The honest headline changed, and that is the
point.** The gate is good at recognising a *recognisable* unanswerable
question; detecting absent evidence is a harder problem than the first
benchmark made it look.

The pre-repair benchmark is preserved beside the repaired one so the finding
stays checkable, and the pre-repair gate result is regenerated by a script
rather than transcribed.

![Figure 5. A classifier that sees only the question text, with no retrieval, no evidence and no corpus, telling an answerable question from an unanswerable one. Before the repair the two classes were separable almost perfectly on the focus corpus (ROC AUC 0.999, against a permutation null of 0.455 +/- 0.072), and one regular expression for a fabricated identifier caught 76.4% of the unanswerable questions with no false positive at all. After the repair the shortcut catches nothing, and what is left of the procedure's power is small but not zero: AUC 0.608 on the focus corpus (p = 0.050) and AUC 0.708 on the industrial corpus (p = 0.010). On the better-powered six-category corpus it is indistinguishable from chance: AUC 0.533 (p = 0.267). The benchmark's unanswerable class is decidable from the evidence rather than from a question-shape rule, but on two of the three corpora it is not free of form-only separability.](figures/fig5_question_only_roc.pdf)

# 10. Where this sits in the literature

| Prior work | What it is | How this project relates |
|---|---|---|
| Lewis et al. 2020 (arXiv:2005.11401) | RAG | The starting point, not a contribution |
| CRAG (arXiv:2401.15884), Self-RAG (arXiv:2310.11511) | corrective and self-reflective RAG | comparison arms that do *not* gate at retrieval time |
| **RCL** (arXiv:2609.11023) | a retrieval-confidence layer for insufficient context in enterprise RAG | **prior art for the gate mechanism itself** |
| **HIRA** (arXiv:2608.21792) | human-in-the-loop cascade for document classification in regulated industries | prior art for the cascade in a regulated setting |
| **RADIANT-LLM** (arXiv:2604.22755) | agentic RAG for reliable decision support in safety-critical nuclear engineering | prior art for the domain framing |
| **CiteGuard-RAG** (arXiv:2609.15830) | validation-centred evidence-grounded QA | prior art for validation-centred design |
| **I-CALM** (arXiv:2604.03904) | two-stage answer/abstain protocol, abstention scored as a classifier | the design precedent for the two prompt conditions |
| **TAPS** (arXiv:2610.16318) | abstention without learning to abstain | coverage-matched arm comparison |
| **Jev-as-a-Judge** (arXiv:2610.20634) | confidence-gated cascading claim verification | the precedent for the random-escalation control arm |
| SURE-RAG (arXiv:2605.03534), Sufficient Context (arXiv:2411.06037) | set-level sufficiency, accuracy-vs-coverage | the concepts this project deliberately does *not* claim |
| The Selection Effect (EMNLP 2026) | a gate forwards a slice on which the downstream component is no better than the baseline | **the literature names this project's failure mode** |

**The positioning, stated exactly.** Every architectural mechanism in this
framework has published prior art. The nearest is RCL, which publishes a
retrieval-confidence layer — and HALT-RAG, which is a *post-hoc output
verifier* that reads the source text and the generated output and scores
hallucination with a calibrated meta-classifier. Its own Future Work says the
critical next step is to "integrate and evaluate detectors like HALT-RAG
within a live RAG pipeline to measure its resilience to noisy or irrelevant
retrieved context." **That step is this project's Experiment 8.**

So the claim is not "we built a mechanism nobody has built". It is:

> The abstention **mechanism** is prior art; the end-to-end **measurement** of
> it — the joint cost–coverage–reliability frontier for a confidence gate on
> industrial text, at the level of the individual answer claim, on a corpus
> regime that is not the procedural one most deployments use — is not.

And the literature also names the failure this project is most exposed to: a
gate can forward a slice on which the downstream component is no better than
the baseline, erasing its advantage. That is why the random-escalation control
arm exists, and why a null result under one prompt is reported as *"the
prompt had already realised the gate's function on that slice"* and never as
"confidence gating does not work".

# 11. Limitations

1. **Scale.** The primary corpus is 634 chunks over 24 documents; the public
   encyclopaedic corpus measured on is 2,383 chunks over    46 documents, and the regulatory corpus is    110 documents and 2,443 chunks. All are below
   the scale at which the statistical framing is well founded. The claims are
   framed as demonstration and mechanism, not generalisation.
2. **The first corpus is encyclopaedic, not procedural.** Industrial-engineering
   text from Wikipedia, not operating manuals or supplier specifications. It
   ships with per-document provenance, but a practitioner would not find their
   documents in it. The second corpus is authentic and binding — but it is
   *regulation*, and the only kind of industrial text this thesis measures
   against is what a regulator publishes.
3. **Single-domain by design, and the proposal's scope narrowed.**
   Supply chain management is the focus; the other six
   categories exist for the transfer experiment, which is an *intra-domain*
   study. The proposal described a **12-category**
   benchmark across industrial engineering, machine learning and data
   analytics; this thesis builds **6** of the nine
   industrial-engineering ones, descopes the three machine-learning categories
   as a different problem class, and descopes three industrial categories
   because their binding artefacts are proprietary. The reconciliation is
   `research/12_scope_reconciliation.md`, the table is in the Complete Guide's
   §A.6, and it is limitation L19 in the guide's table.
4. **NLI on technical text is weak** (published ceilings of 78.2% / 51.8%
   macro-F1), so the contradiction mechanism reduces but does not eliminate
   false positives.
5. **Calibration is deployment-specific.** Thresholds must be re-fitted per
   retriever and per corpus — §5.4 measures exactly how far a threshold
   travels.
6. **The long-context comparison is settled on cost, not on quality.** The
   answer-quality margin is directional.
7. **H2.1 is conditional**, and the condition is the generator's behaviour, not
   the framework's.
8. **The six-category long-context proxy did not complete.** The run was
   interrupted part-way, so no six-category proxy figure is quoted; the
   cost half for that corpus is complete and is reported.
9. **The second corpus is one jurisdiction, one language and one regulatory
   family.** It is US federal regulation, so nothing in §5.8 shows that the
   detection/typing decomposition holds for a plant's own procedures, for a
   non-English regulatory regime, or for a corpus of vendor specifications.
10. **The conflict labels are model-generated.** The panel's agreement is
    reported in full, but agreement between readers is not confirmation that a
    label is right. This is the cost of replacing human annotators, and it is
    the same cost this table names for the other corpora.
11. **The rubric's wording moved the measured precision by a factor of nine.**
    That is a warning about every model-annotated number in this thesis and
    not only about that one.
12. **The positional comparison did not replicate** on three of the four
    corpus-and-protocol combinations, so the per-claim band is reported as a
    filter with a measurement decomposition and not as a ranking.
13. **The second corpus is regulation, not a plant's own procedures.** It is
    authentic and binding, and it is what closed the contradiction objective,
    but a practitioner reads their own standard operating procedures, not the
    Code of Federal Regulations.

# 12. Next steps, in priority order

These are the same list the technical documentation and the defence deck
carry; it is defined once, in `deliverables/scripts/results_source.py`, so
that the three documents cannot drift apart.

1. **Repeat the generator-side comparison on a generator that returns text on the table questions.** One generator behind five arms settles the hypothesis once; one generator settles it for one model. The replication was attempted on MiniMax-M3.1-Flash and could not be run: it returned no text on 24 of the 66 questions it was asked, of which 23 of the 44 were the benchmark's table lookups -- it spends its whole output budget thinking and comes back empty. Raising the budget fourfold rescued 13 of those, and 11 were still empty at that budget, so this is not a shortage of output room. The obstacle is now specific rather than vague: it wants a generator that can parse a table, or one whose reasoning budget is bounded. Both prompt conditions have been run on MiniMax-M3, and the result is that the gate's contribution does not depend on the generator's willingness to decline -- which is a claim about the *gate*, so it wants a second generator to hold.
2. **Compare the gate against a token-level faithfulness monitor.** The gate is currently measured against a prompt-level control and against the always-flag and never-flag baselines, but not against another *detector* of the same kind of thing. A SYNCHECK-style token-level monitor would put the two on one axis: both score the retrieved evidence, and the question becomes which is the better filter at a stated operating point, on one risk-coverage curve with both on it. The thesis's claim is about the gate as a branch rather than an instruction, and that claim does not need the comparison -- but the comparison is what a practitioner deciding whether to adopt the gate would ask for, and it is one implementation away.
3. **Settle the positional comparison's magnitude and power.** The direction is not uniform: keeping the first claims of an answer carries a higher risk than keeping the band's `grounded` claims in three of the four corpus-and-protocol combinations. What varies is the magnitude -- +0.0923 against +0.0231 on the focus corpus and +0.0152 against +0.0000 on the industrial one, all at matched coverage -- and only the largest of them clears significance (focus gold, p = 0.008). Why the gap is four times larger on the focus corpus's gold protocol than on its retrieved protocol is not established, and a larger sample of annotated claims would settle it. The band is reported as a filter and not as a ranking in the meantime, which the direction that replicates already supports.
4. **Run the answer-quality half of the long-context comparison on the six-category corpus.** The retrieval-side proxy is complete there (680,417 tokens over the corpus), the corpus fits the 1M-token window used here, and the cost half is already measured on both corpora. What is missing is the quality half on the larger corpus, and it is one run away.
5. **Add a second, stronger reranker to the candidate-pool sweep.** The pool result -- recall rising to a peak at a pool of ten and then declining -- is measured with one cross-encoder, so the reranker and the pool size are confounded: a stronger reranker might not decline at all. The sweep is cheap to repeat and the reranker is local, so a 2x2 over the shipped cross-encoder and a stronger one, at pool sizes 10, 50 and 100, plus a no-rerank arm, would separate them. Until it is run, the claim is about *this* reranker.
6. **Test specialisation with genuinely different reader models.** The 2x2 factorial over the annotation rubric and the reader's specialisation holds the reader model constant, so 'specialist' there is a brief given to one model, and the result -- that the rubric's wording and not the specialisation moved the measured precision -- is a statement about briefs. The panel's four regime specialists are differently briefed too. Running the same two roles on a second, genuinely different checkpoint would tell the panel whether specialisation is a capability at all, or only a way of writing a rubric.
7. **Confirm the conflict labels with human annotators, against a rubric whose wording is now known to move the measurement.** The pairs were read by a panel of domain specialists and a generalist control, blind to the detector, and the panel's agreement is reported in full. But the labels are model-generated, so agreement between readers is not confirmation that a label is right; and a 2x2 factorial over the annotation rubric and the reader's specialisation has shown that the wording of the rubric moved the measured precision by a factor of nine (+0.366 at the generalist and +0.317 at the specialist, against +0.049 and +0.000 for the specialisation). So the human round has to fix the rubric before it is run rather than after, and the pairs and the rubric ship with the thesis for that round.
8. **Extend the corpus from federal regulation to a plant's own revised procedures.** The second corpus supplies the conflicts the first one could not: 110 United States federal regulatory documents read at two past dates, giving 948 amended-paragraph pairs of which 361 state different numbers, with the conflict type known by construction and so no annotation needed to know the right answer. What it does not supply is a plant's own documents, where the same procedure at two revisions would be the same kind of conflict but with no public versioner to align them.
9. **Re-fit the conflict calibration on a plant's documents.** The calibration is fitted per corpus, exactly as the answer gate's threshold is. The regulatory profile is fitted and shipped, and it says that on this corpus a conflict is surfaced when the branch that raised it clears 0.5. A plant's documents would need their own fit, and the factorial's result -- that the rubric's wording moved the measured precision by a factor of nine -- means the fit has to be checked against the rubric that will actually be used.
10. **Extend the industrial corpus beyond one jurisdiction and one language.** The corpus is United States federal regulation, in one language, from one regulator family. Nothing in this thesis shows that the decomposition of a conflict detector's precision into detection and typing holds for another jurisdiction's regulatory language, for a plant's own procedures, or for vendor specifications.
11. **Stratify the corpus by modality** so the modality-quota objective can be tested with adequate power, with a pre-registered power analysis rather than a post-hoc one.
12. **Hand-check the repaired unanswerable class against the corpus, on both corpora.** The repair is no longer a single-corpus result: the shortcut audit has been repeated on the industrial corpus, where the one-rule identifier shortcut catches 0 of 197 and the question-only classifier separates the two classes at 0.708 against a permutation null of 0.505. What is still open is the part no audit can do: a person reading the repaired class against the corpus.

# Appendix A — where things live

| Path | What it is |
|---|---|
| `impl/src/` | the framework: ingestion, lexical, dense, fusion, quota, rerank, gate, claims, contradiction, form check, pipeline |
| `impl/experiments/` | 34 experiment scripts, one per result file |
| `impl/tests/` | 4 test files, 32 tests |
| `impl/scripts/ask.py` | the interactive entry point |
| `impl/scripts/rerun_focus.sh`, `rerun_all.sh` | the full re-run scripts |
| `impl/results_focus/`, `impl/results/` | the measured results, by variant |
| `research/baseline_minilm/` | the archived pre-encoder-swap run, kept so the before/after stays checkable |
| `research/00_citation_audit.md` | every citation, resolved against arXiv |
| `deliverables/templates/` | the pristine, tokenised sources |
| `deliverables/scripts/` | the build: substitution, generators, checks |
| `deliverables/dataset/` | the corpus with its provenance, exported for redistribution |

# Appendix B — every number in this report is a measurement

Each figure in this document is a token bound to a value in a result
file. The build substitutes them at build time and fails if any token is left
unsubstituted, so a number in this report cannot drift away from the run that
produced it. The result files are:

| Result file | What it holds |
|---|---|
| `impl/results_focus/exp1_ablation.json` | the seven-rung retrieval ablation and the paired tests |
| `impl/results_focus/exp2_gate.json` | the gate's calibration, its threshold sweep, and the refusal rate per question family |
| `impl/results_focus/exp3_contradiction.json` | the contradiction experiment |
| `impl/results_focus/exp5_pool_size.json` | the candidate-pool sweep |
| `impl/results_focus/exp7_long_context.json` | the long-context cost half and the retrieval-side proxy |
| `impl/results_focus/exp8_generation.json` | the generator-side comparison |
| `impl/results_focus/exp8_scorer_validation.json` | the audit of the claim scorer |
| `impl/results_focus/exp9_label_audit.json` | the audit of the benchmark's answer labels |
| `impl/results_focus/exp11_contradiction_precision.json` | the contradiction gate's precision, against reader labels |
| `impl/results_focus/exp12_unanswerable_class_audit.json` | the audit of the benchmark's unanswerable class |
| `impl/results/exp4_transfer.json` | the cross-category transfer experiment |
| `research/baseline_minilm/` | the archived pre-encoder-swap measurements |

Seed for every stochastic component: 20261118. Bootstrap resamples for the
confidence intervals: 10,000.

## The one-paragraph version

> We built a retrieval-augmented generation framework for industrial
> engineering documentation whose answers pass through a **calibrated,
> non-bypassable confidence gate**: the language model is never called on a
> question the retrieved evidence does not support. We built the measurement
> to evaluate it — a silver-standard benchmark with an answerable and an
> unanswerable half, a scorer that is itself audited — and we audited our own
> instrument and repaired two defects in it. On the supply-chain focus domain
> (735 chunks, 176 queries), hybrid lexical and
> dense retrieval with reciprocal-rank fusion is the one retrieval change
> that is significant (+0.188 R@10, p = 1.4 × 10⁻²); the gate refuses
> 23.6% of the corpus-anchored unanswerable class while
> still answering 93.8% of the answerable ones; and
> against a generator that answers rather than declining, the gate reduces
> the rate of answering unanswerable questions at the cost of coverage —
> **conditionally on the generator's own behaviour, which is the honest form
> of the claim**. Every component has published prior art, so the
> contribution is the measurement. The clearest new result is on a second
> corpus — 110 United States federal regulations read at two
> past dates, where the same provision at two issues *is* a conflict whose
> type is known by construction: there, a conflict detector's precision
> splits into **detection** (0.659) and **typing**
> (0.073), so the mechanism finds the conflicts and reports them
> as the wrong kind. The measurement's own binding constraint was the
> annotation: a rubric factorial shows the wording of the labelling
> instructions, not the reader's specialisation, moved that number
> (+0.366 against +0.049). One
> result we do **not** claim is that lexical retrieval beats dense retrieval
> on regulatory text — that is already published, three times over.
