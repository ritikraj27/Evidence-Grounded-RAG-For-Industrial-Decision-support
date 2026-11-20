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
from a command line — and the code is
{{N_SOURCE_MODULES}} modules and {{N_SOURCE_LINES}} lines under `impl/src/`,
with {{N_EXPERIMENTS}} experiment scripts and {{N_TESTS}} tests.

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
| Chunks | {{N_FOCUS_CHUNKS}} | {{N_CHUNKS}} |
| Documents | {{N_FOCUS_DOCUMENTS}} | {{N_DOCUMENTS}} |
| Categories | 1 | {{N_CATEGORIES}} |
| Tokens | {{LC_CORPUS_TOKENS}} | {{MC_LC_CORPUS_TOKENS}} |
| Modality mix | {{SHARE_TEXT}} text, {{SHARE_TABLE}} tables, {{SHARE_CHART}} charts | — |
| Benchmark queries | {{N_FOCUS_QUERIES}} ({{N_FOCUS_ANSWERABLE}} answerable, {{N_FOCUS_UNANSWERABLE}} unanswerable) | {{MC_N_QUERIES}} ({{MC_N_ANSWERABLE}} answerable, {{MC_N_UNANSWERABLE}} unanswerable) |
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
adjacent rungs. Focus domain, {{N_FOCUS_QUERIES}} queries.

| System | R@5 | R@10 | R@20 | MRR | nDCG@10 | Table R@10 |
|---|---|---|---|---|---|---|
| A. BM25 only | {{R_A}} | {{R_A}} | {{R20_A}} | {{MRR_A}} | {{NDCG_A}} | {{TBL_A}} |
| B. Dense only | {{R_B}} | {{R_B}} | {{R20_B}} | {{MRR_B}} | {{NDCG_B}} | {{TBL_B}} |
| C. Hybrid (RRF) | {{R_C}} | {{R_C}} | {{R20_C}} | {{MRR_C}} | {{NDCG_C}} | {{TBL_C}} |
| D. + cross-encoder rerank | {{R_D}} | {{R_D}} | {{R20_D}} | {{MRR_D}} | {{NDCG_D}} | {{TBL_D}} |
| E. + category filter | {{R_E}} | {{R_E}} | {{R20_E}} | {{MRR_E}} | {{NDCG_E}} | {{TBL_E}} |
| F. + quota (pre-rerank) | {{R_F}} | {{R_F}} | {{R20_F}} | {{MRR_F}} | {{NDCG_F}} | {{TBL_F}} |
| G. + quota (post-rerank) | {{R_G}} | {{R_G}} | {{R20_G}} | {{MRR_G}} | {{NDCG_G}} | {{TBL_G}} |

| Comparison | ΔR@10 | p (Wilcoxon) |
|---|---|---|
| A → B (BM25 → dense) | {{DELTA_AB}} | {{P_AB}} |
| B → C (dense → hybrid) | {{DELTA_BC}} | {{P_BC}} |
| C → D (+ rerank) | {{DELTA_CD}} | {{P_CD}} |
| D → E (+ category filter) | {{DELTA_DE}} | {{P_DE}} |
| E → F (+ quota, pre-rerank) | {{DELTA_EF}} | {{P_EF}} |
| F → G (quota moved post-rerank) | {{DELTA_FG}} | {{P_FG}} |

**What the ablation actually shows.**

* **Fusion works, and it is the only retrieval change that is significant.**
  Dense-only retrieval is *worse than plain BM25* ({{DELTA_AB}} in R@10, p =
  {{P_AB}}). Fusing the two recovers it and then some ({{DELTA_BC}}, p =
  {{P_BC}}). This is the argument for hybrid retrieval stated as a
  measurement rather than as a received wisdom.
* **The reranker does not help.** {{DELTA_CD}} in R@10, p = {{P_CD}} — not
  significant, and the sign is negative. It is kept anyway, because the gate
  is calibrated on the reranker's score and because the cross-encoder is what
  makes the *candidate pool* large enough to need gating.
* **The category filter is a no-op on the focus domain**, and that is the
  correct result: the corpus has one category. Its value shows up on the
  six-category corpus and in the mechanism tests.
* **The modality quota belongs *before* the cross-encoder.** Applied after
  the reranker ({{DELTA_FG}}, p = {{P_FG}}) it costs recall; applied before it,
  it restores table recall to {{TBL_F}} at no measurable cost to text recall.
  A quota that runs before the reranker fixes the membership of the final
  ten, so the cross-encoder can reorder it but not change it, and the forced
  table chunk survives; a quota that runs after has to import a chunk the
  cross-encoder already ranked below the cut, which displaces a good one.
  **The system now applies it {{SHIPPED_QUOTA_PLACEMENT}}.** It was built
  with the later placement and kept it until 16 November 2026, because every
  measurement had been taken with it; on that date it was moved and
  everything that depends on it was measured again. The direction is
  corpus-dependent: the earlier placement is also the better one on the
  six-category corpus, and the later one is marginally better on the
  industrial corpus, by less than the noise.
* **The candidate-pool curve peaks and then declines.** Recall@10 is highest
  at a pool of ten ({{POOL_PEAK_R10}}) and falls to {{POOL50}} at a pool of
  fifty. A larger pool costs the reranker work and buys nothing — the
  reranker can only permute what it is shown.

![{{FIG4_CAPTION}}](figures/fig4_modality_quota_pareto.pdf)
![{{FIG1_CAPTION}}](figures/fig1_pool_size.pdf)

## 5.2 The confidence gate

The gate's label is **answer-in-context detectability**, not evidence
sufficiency. The positive class is "the gold chunk is present in the reranked
candidate pool". The literature reserves *sufficiency* for the set-level
property, so the name is deliberately not borrowed.

Calibration: Brier {{GATE_BRIER}}, ECE {{GATE_ECE}}. Operating point:
τ = {{TAU}}, chosen by a stated rule (the highest τ still answering ≥ 90% of
answerable queries).

| | Value |
|---|---|
| Answerable questions answered | {{ANSWERABLE_ANSWERED_PCT}} |
| Unanswerable questions refused (pooled) | {{UNANSWERABLE_REFUSED_PCT}} |
| Abstention precision | {{ABSTENTION_PRECISION}} |
| **Corpus-anchored unanswerable class refused** | **{{UNANS_HARD_REFUSED_PCT}}** ({{UNANS_HARD_REFUSED_N}}) |
| Out-of-domain unanswerable class refused | {{UNANS_OOD_REFUSED_PCT}} ({{UNANS_OOD_REFUSED_N}}) |

**The pooled number is an upper bound, and the gap between the two strata is
the finding.** The out-of-domain family is unanswerable for any system that
knows what the corpus is about, so refusing it says almost nothing. The
corpus-anchored family is the real test: the corpus discusses the subject and
states no value for it, so only the retrieved evidence can decide. The gate
refuses **{{UNANS_HARD_REFUSED_PCT}}** of those. It is good at *recognising* an
unanswerable question; it is not good at detecting *absent evidence*, and
those are different problems. Reporting only the pooled figure would have
flattered the system by a factor of about one and a half.

![{{FIG2_CAPTION}}](figures/fig2_risk_coverage.pdf)
![{{FIG3_CAPTION}}](figures/fig3_calibration.pdf)

## 5.3 Contradiction surfacing

{{CONTRA_PAIRS}} chunk pairs compared over the accepted contexts.

| Detector | Pairs flagged | Flag rate |
|---|---|---|
| NLI alone | {{CONTRA_NLI_FLAGGED}} | {{CONTRA_NLI_FLAG_RATE}} |
| **and** the same-subject check (the shipped gate) | {{CONTRA_JOINT_FLAGGED}} | {{CONTRA_JOINT_FLAG_RATE}} |

The same-subject check is what does the work: it suppresses
{{CONTRA_NLI_FLAGGED}} minus {{CONTRA_JOINT_FLAGGED}} of the bare NLI gate's
alarms, leaving {{CONTRA_JOINT_FLAGGED}} of
{{CONTRA_PAIRS}} pairs. The gate has three branches — a semantic one
(NLI and same-subject), a quantity one (the same measured quantity with two
values) and a revision one (the same term at two versions of the same
standard) — and on this corpus the alarms split
{{CONTRA_BRANCH_SEMANTIC}} semantic,
{{CONTRA_BRANCH_QUANTITY}} quantity,
{{CONTRA_BRANCH_REVISION}} revision.

The precision has been measured against reader labels rather than against a
proxy: {{CONTRA_PRECISION_CLAIM}}

{{CONTRA_BRANCH_CLAIM}}

{{CONTRA_PRECISION_MECHANISM}}

{{CONTRA_CONTROL_CLAIM}}

**What this means for the shipped system.** The calibration is fitted from the
measurement and the pipeline reads it: a branch whose measured precision is
below the floor has its findings recorded and withheld rather than shown to a
practitioner. On this corpus that leaves **{{CONTRA_SURFACED}} findings
surfaced and {{CONTRA_WITHHELD}} withheld**. The system no longer raises
{{CONTRA_JOINT_FLAGGED}} false warnings about a corpus that contains no
contradictions; it is silent here, and it is silent because the measurement
says it should be.

That silence is a statement about the benchmark and not a claim that the
mechanism is useless. {{CONTRA_CONTROL_CLAIM}} The gate is the mechanism that
stops a practitioner applying a superseded policy, and evaluating it needs a
corpus of revised procedures rather than articles about concepts.

![{{FIG6_CAPTION}}](figures/fig6_contradiction_precision.pdf)

## 5.4 Cross-category transfer (O4)

Measured on the six-category corpus, because a transfer experiment needs a
subset of categories to transfer to held-out ones.

| Metric (held-out half) | Transferred | Refitted (ceiling) |
|---|---|---|
| Answerable answered | {{TRANSFER_XFER_ANSWERABLE_ANSWERED}} | {{TRANSFER_REFIIT_ANSWERABLE_ANSWERED}} |
| Answerable refused | — | — |
| Coverage | {{TRANSFER_XFER_COVERAGE}} | {{TRANSFER_REFIIT_COVERAGE}} |
| Top-1 accuracy given accepted | {{TRANSFER_XFER_TOP1_ACC}} | {{TRANSFER_REFIIT_TOP1_ACC}} |

Tuning half: {{TRANSFER_TUNING_CATS}}. Held-out half:
{{TRANSFER_HELDOUT_CATS}}. τ fitted on the tuning half and transferred
unchanged: {{TRANSFER_TAU}}.

**The scope is narrower than "transfer" usually means, and it has to be
stated.** The split is over *document categories*, and the benchmark's
unanswerable questions carry no category, so neither half contains any. This
experiment therefore measures **coverage on answerable questions across
domains**; it says nothing about how well a transferred threshold refuses
unanswerable questions. What transfers, quantitatively, is the *ordering*:
top-1 accuracy given acceptance moves only from {{TRANSFER_REFIIT_TOP1_ACC}}
to {{TRANSFER_XFER_TOP1_ACC}}, while coverage falls from
{{TRANSFER_REFIIT_COVERAGE}} to {{TRANSFER_XFER_COVERAGE}}. The calibration's
*ranking* travels; its *operating point* does not. That is the practical
finding: re-fit τ per corpus, do not expect to re-use it.

## 5.5 The long-context baseline — the strongest threat to the work

The threat: the corpus fits in a modern context window, so a reader given
everything could answer directly and the retrieval machinery would be
unnecessary.

| | Focus domain | Six-category corpus |
|---|---|---|
| Whole corpus as a prompt | {{LC_CORPUS_TOKENS}} tokens | {{MC_LC_CORPUS_TOKENS}} tokens |
| RAG arm's accepted context | {{LC_RAG_TOKENS}} tokens ({{LC_RAG_CHUNKS}} chunks) | {{MC_LC_RAG_TOKENS}} tokens |
| **Cost ratio** | **{{LC_RATIO}}×** | **{{MC_LC_RATIO}}×** |
| Fits a 128K window | {{LC_FITS_128K}} | {{MC_LC_FITS_128K}} |

{{GEN_LC_COST_CLAIM}}

The retrieval-side proxy says the evidence is not lost in a big context: with
the candidate set widened to every chunk in the corpus, the gold chunk still
lands in the scorer's top 10 for {{LC_PROXY_TOP10}} of focus-domain queries
(95% interval {{LC_PROXY_CI}}) at a median rank of {{LC_PROXY_MEDIAN_RANK}}.
{{MC_LC_PROXY_CLAUSE}}

**The honest position:** the long-context arm wins on coverage and loses on
cost, and the answer-quality comparison is directional rather than
significant. {{GEN_LC_FINDING}}

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
| The same retrieval, **gate removed** | {{GEN_NOGATE_UNANS_ANSWER_RATE}} ({{GEN_NOGATE_UNANS_ANSWERED}}) | {{GEN_NOGATE_ANS_ANSWERED}} | {{GEN_NOGATE_ANS_ACCURACY}} |
| The framework at its fitted operating point | {{GEN_FITTED_UNANS_ANSWER_RATE}} ({{GEN_FITTED_UNANS_ANSWERED}}) | {{GEN_FITTED_ANS_ANSWERED}} | {{GEN_FITTED_ANS_ACCURACY}} |
| **Random-escalation control** (refuses as many, picks at random) | {{GEN_RANDOM_UNANS_ANSWER_RATE}} ({{GEN_RANDOM_UNANS_ANSWERED}}) | {{GEN_RANDOM_ANS_ANSWERED}} | {{GEN_RANDOM_ANS_ACCURACY}} |
| The framework at the threshold transferred from the cross-category half | {{GEN_XFER_UNANS_ANSWER_RATE}} ({{GEN_XFER_UNANS_ANSWERED}}) | {{GEN_XFER_ANS_ANSWERED}} | {{GEN_XFER_ANS_ACCURACY}} |
| The whole corpus in the prompt | {{GEN_LONGCTX_UNANS_ANSWER_RATE}} ({{GEN_LONGCTX_UNANS_ANSWERED}}) | {{GEN_LONGCTX_ANS_ANSWERED}} | {{GEN_LONGCTX_ANS_ACCURACY}} |

**Under the answering prompt** — the generator is *required* to answer, so it
cannot decline on its own and give the gate the credit. This is the
condition in which the gate's own contribution is measurable, and it is the
decisive one.

| Arm | Unanswerable answered | Answerable answered | Answerable accuracy |
|---|---|---|---|
| The same retrieval, **gate removed** | {{GEN_A_NOGATE_UNANS_ANSWER_RATE}} ({{GEN_A_NOGATE_UNANS_ANSWERED}}) | {{GEN_A_NOGATE_ANS_ANSWERED}} | {{GEN_A_NOGATE_ANS_ACCURACY}} |
| The framework at its fitted operating point | {{GEN_A_FITTED_UNANS_ANSWER_RATE}} ({{GEN_A_FITTED_UNANS_ANSWERED}}) | {{GEN_A_FITTED_ANS_ANSWERED}} | {{GEN_A_FITTED_ANS_ACCURACY}} |
| **Random-escalation control** | {{GEN_A_RANDOM_UNANS_ANSWER_RATE}} ({{GEN_A_RANDOM_UNANS_ANSWERED}}) | {{GEN_A_RANDOM_ANS_ANSWERED}} | {{GEN_A_RANDOM_ANS_ACCURACY}} |
| The framework at the threshold transferred from the cross-category half | {{GEN_A_XFER_UNANS_ANSWER_RATE}} ({{GEN_A_XFER_UNANS_ANSWERED}}) | {{GEN_A_XFER_ANS_ANSWERED}} | {{GEN_A_XFER_ANS_ACCURACY}} |
| The whole corpus in the prompt | {{GEN_A_LONGCTX_UNANS_ANSWER_RATE}} ({{GEN_A_LONGCTX_UNANS_ANSWERED}}) | {{GEN_A_LONGCTX_ANS_ANSWERED}} | {{GEN_A_LONGCTX_ANS_ACCURACY}} |

**Read the two tables together and the separation is complete.** Under the
answering prompt the gate cuts the rate of answering unanswerable questions
from {{GEN_A_NOGATE_UNANS_ANSWER_RATE}} to
{{GEN_A_FITTED_UNANS_ANSWER_RATE}} while still answering
{{GEN_A_FITTED_ANS_ANSWERED}} of the answerable ones. The random control
also refuses a lot — but it answers only {{GEN_A_RANDOM_ANS_ANSWERED}} of
the answerable questions, so its refusals are landing on the wrong ones.
Paired question by question, {{GEN_GATE_EFFECT}}

The **random-escalation control** is the arm that makes this a measurement
rather than an anecdote. It refuses the same *number* of questions as the
fitted gate — but picks them at random, ignoring the confidence score
entirely. Under the answering prompt, the fitted gate answered
{{GEN_A_FITTED_ANS_ANSWERED}} answerable questions against the control's
{{GEN_A_RANDOM_ANS_ANSWERED}}, and answered
{{GEN_A_FITTED_UNANS_ANSWERED}} of the unanswerable ones against the
control's {{GEN_A_RANDOM_UNANS_ANSWERED}}.

That is the finding, and it is easy to state wrongly. The control refuses the
same *total* number of questions, but the gate concentrates them where they
belong: on the unanswerable questions. So the confidence score does not buy a
lower answer rate on unanswerable questions — the random arm has that too,
and by luck. What it buys is **where the refusals land**, which shows up as
coverage on the answerable questions.

The paired test on the answerable questions is where the two come apart. The
gate refused {{GEN_PAIRED_FITTED_ANS_B}} of the questions the ungated arm
answered and let through {{GEN_PAIRED_FITTED_ANS_C}} (exact McNemar p =
{{GEN_PAIRED_FITTED_ANS_P}}); the random control refused
{{GEN_PAIRED_RANDOM_ANS_B}} and let through {{GEN_PAIRED_RANDOM_ANS_C}}
(p = {{GEN_PAIRED_RANDOM_ANS_P}}). The gate's refusals cost it essentially no
coverage; the control's cost it significantly. **That is what the confidence
score buys over refusing an arbitrary set of the same size.**

**The verdict:** {{GEN_GATE_OVERALL}}

### 5.6.1 The replication on a second generator — and what it turned into

The whole design was repeated on a second generator, changed in nothing but
the model id, and **the run did not complete**. The harness recorded it as
not-run rather than quoting a rate it could not stand behind. Experiment 13 measured
why, on the benchmark's own questions: {{GENCOMP_CLAIM}}

| Generator | No text returned | Of which on the table-lookup family | Of which on a control sample of the other families |
|---|---|---|---|
| {{GENCOMP_MODEL_1}} | {{GENCOMP_1_EMPTY}} | {{GENCOMP_1_EMPTY_TABLE}} | {{GENCOMP_1_EMPTY_CONTROL}} |
| {{GENCOMP_MODEL_2}} | {{GENCOMP_2_EMPTY}} | {{GENCOMP_2_EMPTY_TABLE}} | {{GENCOMP_2_EMPTY_CONTROL}} |

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
shipped run was made with {{GEN_MODEL}} in November, and the row above is the
same model id, on the same corpus, with the same prompt, measured now:
{{GENCOMP_1_EMPTY}} of its requests came back with no text. So the shipped
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
published rather than asserted: {{GEN_SCORER_TRUTH}}; {{GEN_SCORER_FAB}}; and
{{GEN_SCORER_FOREIGN}}.

## 5.7 The before/after, in one table

An ablation table says what each mechanism does to a metric. It does not say
what the whole framework does to a practitioner's questions. Experiment 6
answers that, on the same {{CASE_N_QUERIES}} focus-domain questions, comparing
the plain lexical retriever — which never refuses — against the full
framework.

| | Plain BM25 retriever | The full framework |
|---|---|---|
| Unanswerable questions **answered** (all wrongly) | **{{CASE_BM25_UNANS_ANSWERED}} of {{CASE_N_UNANSWERABLE}}** | **{{CASE_FW_UNANS_ANSWERED}} of {{CASE_N_UNANSWERABLE}}** |
| Answerable questions answered | {{CASE_BM25_ANS_ANSWERED}} of {{CASE_N_ANSWERABLE}} | {{CASE_FW_ANS_ANSWERED}} of {{CASE_N_ANSWERABLE}} |
| Gate refusal rate on unanswerable questions | 0.0% | {{CASE_GATE_REF_UNANSWERABLE}} |
| Context contains the gold chunk | {{CASE_BM25_GOLD_TOP10}} | {{CASE_FW_GOLD_ACCEPTED}} |
| Mean chunks in the accepted context | — | {{CASE_MEAN_CHUNKS}} |

**This is the before/after that matters.** A retriever that never refuses
answers every unanswerable question, and every one of those is a wrong answer
dressed as a right one. The framework's cost is the answerable questions it
declines; its benefit is the unanswerable ones it stops answering.

Note also the fourth row: on silver-standard labels a plain lexical retriever
already puts the gold chunk in the top ten more often ({{CASE_BM25_GOLD_TOP10}}
against {{CASE_FW_GOLD_ACCEPTED}}) — **the framework is not better at
retrieving, and it is not trying to be.** The gate is there to refuse.

## 5.8 The second corpus — authentic, versioned, binding industrial text

Two of the objectives could not be closed on the corpus of §4. That corpus is
encyclopaedic prose about industrial engineering, and it is the wrong instrument
for a contradiction mechanism in two ways at once. It contains no conflict a
practitioner would recognise as one — a document read at a single upstream
revision cannot contradict itself, and concept-level prose rarely binds a
numeric requirement that another document contradicts — so RO4's first
measurement was unevaluable: the contradiction mechanism's measured precision
was {{CONTRA_PRECISION_PCT}} on a corpus that contains no conflicts, which says
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

The corpus holds {{IND_N_DOCUMENTS}} documents and {{IND_N_CHUNKS}} chunks
({{IND_N_TEXT_CHUNKS}} text, {{IND_N_TABLE_CHUNKS}} table) in
{{IND_N_REGIMES}} regulatory regimes: OSHA general industry; OSHA process
safety and EPA risk management; EPA new source performance standards; and DOT
hazardous materials. The snapshot is the {{IND_REV_POST_DATE}} issue.

### 5.8.1 The version trick, and why it supplies labels

Federal regulations are amended, so the same section read at two dates is the
same rule at two issues. The corpus is read twice — at {{IND_REV_PRE_DATE}} and
at {{IND_REV_POST_DATE}} — and aligning the two snapshots gives
{{IND_REV_PAIRS}} amended-paragraph pairs, of which {{IND_REV_NUMERIC}}
({{IND_REV_NUMERIC_PCT}}) state different numbers in the two vintages.

Such a pair **is** a conflict, and its type is known by construction: the same
provision at two issues is a supersession, not a contradiction. No annotation is
needed to know the right answer, which is what makes this corpus a measuring
instrument rather than a pile of text.

### 5.8.2 The benchmark, and the shortcut audit it needed

{{IND_N_QUERIES}} queries: {{IND_N_ANSWERABLE}} answerable,
{{IND_N_UNANSWERABLE}} unanswerable. The audit repeated the first benchmark's
test. The one-rule identifier shortcut that carried {{UNANS_SHORTCUT_BEFORE}} of
the first benchmark's unanswerable class catches {{IND_SHORTCUT_CAUGHT}} of
{{IND_N_UNANSWERABLE}} here. A question-only classifier separates the two
classes at ROC AUC {{IND_AUDIT_STRUCTURAL}} against a permutation null of
{{IND_AUDIT_NULL_MEAN}} — above the null, not at it — and the bag-of-words
separability is {{IND_AUDIT_BOW}}.

The residual separability is question **length**: median
{{IND_LEN_ANSWERABLE}} characters for the answerable class against
{{IND_LEN_UNANSWERABLE}} for the unanswerable one. That is reported here rather
than hidden, because it is the same kind of residual the first benchmark had,
and §9 is the story of finding that one and repairing it.

### 5.8.3 RO6 — the negative findings replicate

**"BM25 beats an off-the-shelf dense encoder on regulatory text" is already
published — three times over, in three jurisdictions (arXiv:2506.12895,
arXiv:2604.01733, arXiv:2412.07462) — so it is not claimed here as new, and it
is not in the abstract.** What the measurement contributes is the *corollary*.

| Finding | Number |
|---|---|
| BM25 Recall@10 | {{IND_BM25_R10}} |
| Dense-encoder Recall@10 | {{IND_DENSE_R10}} |
| BM25 − dense | {{IND_BM25_VS_DENSE_DELTA}}, p {{IND_BM25_VS_DENSE_P}}, n {{IND_BM25_VS_DENSE_N}} |
| Fusion against its own lexical leg | {{IND_FUSION_VS_LEXICAL_DELTA}}, p {{IND_FUSION_VS_LEXICAL_P}} |
| Category pre-filter against no filter | {{IND_FILTER_VS_NO_FILTER_DELTA}}, p {{IND_FILTER_VS_NO_FILTER_P}} |
| Cross-encoder against no reranker | {{IND_RERANK_VS_NO_RERANK_DELTA}}, p {{IND_RERANK_VS_NO_RERANK_P}} |

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
reaches {{IND_POOL_R20_AT_50}} while Recall@10 stands at {{IND_POOL_R10_AT_50}}:
{{IND_POOL_DISPLACEMENT_PCT}} of the golds are retrieved and then pushed *out of
the ten-chunk context* by the reranker's own ordering.

### 5.8.5 The gate's operating point transfers; its threshold does not

At τ = {{IND_GATE_TAU}} the industrial gate answers
{{IND_GATE_ANSWERABLE_ANSWERED_PCT}} of the answerable queries and refuses
{{IND_GATE_UNANSWERABLE_REFUSED_PCT}} of the unanswerable ones, with an
abstention precision of {{IND_GATE_ABST_PRECISION}} and a coverage of
{{IND_GATE_COVERAGE}}.

The threshold does not transfer — {{IND_GATE_TAU}} here against
{{FOCUS_GATE_TAU}} on the focus corpus — and the operating point does:
{{IND_GATE_COVERAGE}} against {{FOCUS_GATE_COVERAGE}}. That is the calibration
result of §5.4 restated on a second corpus: τ is a fitted parameter of the
deployment and must be re-fitted, while the point on the risk–coverage surface
a practitioner cares about is a property of the mechanism.

The two calibrations differ in quality as well as in value, and both metrics
are reported: ECE {{IND_GATE_ECE}} against {{FOCUS_GATE_ECE}}, Brier
{{IND_GATE_BRIER}} against {{FOCUS_GATE_BRIER}}. The industrial gate is the
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

{{IND_RO4_PAIRS}} pairs were assembled in two strata: {{IND_RO4_REVISION_STRATUM_N}}
*revision* pairs (a paragraph and its amended self) and
{{IND_RO4_SIMILAR_STRATUM_N}} *similar* pairs (cross-document retrieval
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
| The readers' labels | {{IND_RO4_DETECTION}} (95% CI {{IND_RO4_DETECTION_CI_LO}}–{{IND_RO4_DETECTION_CI_HI}}) | {{IND_RO4_TYPING}} (95% CI {{IND_RO4_TYPING_CI_LO}}–{{IND_RO4_TYPING_CI_HI}}) |
| **The construction labels** | {{IND_RO4_CONSTRUCTION_DETECTION}} | {{IND_RO4_CONSTRUCTION_TYPING}} |
| The shipped operations vocabulary | {{IND_RO4_SHIPPED_DETECTION}} | {{IND_RO4_SHIPPED_TYPING}} |

Against the readers' labels the detector's detection precision is
{{IND_RO4_DETECTION}}, and {{IND_RO4_REV_STRATUM}} on the stratum where the
conflicts actually are. Recall of any real conflict is {{IND_RO4_RECALL_ANY}}
over the {{IND_RO4_N_SUPERSESSION}} annotated supersessions.

**The quantity branch is the thinnest result in the whole study.** An
exhaustive corpus-wide search over {{IND_QTY_TERMS}} measurement terms found
{{IND_QTY_CANDIDATES}} candidate cross-document quantity conflicts — exact
rather than sampled, because the search groups every (measurement term, value)
pair in the corpus and keeps the terms whose values differ across documents.
{{IND_QTY_SCORED}} pairs were put to the reader and the branch fired on
{{IND_QTY_FIRED}}; of the {{IND_QTY_JUDGED}} pairs the reader labelled, **none**
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
| Generalist | {{IND_FACT_G_V1_DET}} | {{IND_FACT_G_V2_DET}} |
| Specialist | {{IND_FACT_S_V1_DET}} | {{IND_FACT_S_V2_DET}} |

Effects: rubric {{IND_FACT_RUBRIC_GENERALIST}} at the generalist and
{{IND_FACT_RUBRIC_SPECIALIST}} at the specialist; specialisation
{{IND_FACT_SPEC_AT_V1}} at the old rubric and {{IND_FACT_SPEC_AT_V2}} at the
sharpened one. The mechanism is concrete. The old rubric required a version
marker, and a regulation does not write its own version in its text, so it
missed {{IND_FACT_GENERALIST_MISSED}} of the {{IND_FACT_GENERALIST_V2_CONFLICTS}}
supersessions it was asked to find ({{IND_FACT_GENERALIST_MISSED_SHARE}} of
them); the specialist missed {{IND_FACT_SPECIALIST_MISSED}} of
{{IND_FACT_SPECIALIST_V2_CONFLICTS}} ({{IND_FACT_SPECIALIST_MISSED_SHARE}} of
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
   detector's precision splits into on this corpus are {{IND_RO4_DETECTION}} and
   {{IND_RO4_TYPING}}, and the rubric's wording is what put them that far
   apart.

The lesson is about measurement rather than about annotation: a number that
moves by a factor of nine with the wording of its own rubric is not yet a
measurement of the thing under test.

### 5.8.8 RO5 — the band replicates

The third mechanism was measured on both corpora, with the same generator and
two evidence protocols on each: the benchmark's own gold evidence (is the
claim right?) and the evidence the retriever actually returned (does an
independent reader agree with the scorer?). On this corpus
{{IND_RO5_GOLD_N_CLAIMS}} and {{IND_RO5_RETRIEVED_N_CLAIMS}} claims were
labelled under the two protocols.

| Corpus and protocol | κ (band vs reference) | Band error (grounded / inferred / uncertain) | Answers with no wrong claim |
|---|---|---|---|
| Focus, gold | {{RO5_GOLD_KAPPA}} | {{RO5_GOLD_GROUNDED_ERROR}} / {{RO5_GOLD_INFERRED_ERROR}} / {{RO5_GOLD_UNCERTAIN_ERROR}} | {{RO5_GOLD_CLEAN_PCT}} → {{RO5_GOLD_GROUNDED_ONLY_PCT}} |
| Focus, retrieved | {{RO5_RETRIEVED_KAPPA}} | {{RO5_RETRIEVED_GROUNDED_ERROR}} / {{RO5_RETRIEVED_INFERRED_ERROR}} / {{RO5_RETRIEVED_UNCERTAIN_ERROR}} | {{RO5_RETRIEVED_CLEAN_PCT}} → {{RO5_RETRIEVED_GROUNDED_ONLY_PCT}} |
| Industrial, gold | {{IND_RO5_GOLD_KAPPA}} | {{IND_RO5_GOLD_GROUNDED_ERROR}} / {{IND_RO5_GOLD_INFERRED_ERROR}} / {{IND_RO5_GOLD_UNCERTAIN_ERROR}} | {{IND_RO5_GOLD_CLEAN_PCT}} → {{IND_RO5_GOLD_GROUNDED_ONLY_PCT}} |
| Industrial, retrieved | {{IND_RO5_RETRIEVED_KAPPA}} | {{IND_RO5_RETRIEVED_GROUNDED_ERROR}} / {{IND_RO5_RETRIEVED_INFERRED_ERROR}} / {{IND_RO5_RETRIEVED_UNCERTAIN_ERROR}} | {{IND_RO5_RETRIEVED_CLEAN_PCT}} → {{IND_RO5_RETRIEVED_GROUNDED_ONLY_PCT}} |

The industrial κ carries a 95% interval of
{{IND_RO5_GOLD_KAPPA_CI_LO}}–{{IND_RO5_GOLD_KAPPA_CI_HI}} on the gold protocol
and {{IND_RO5_RETRIEVED_KAPPA_CI_LO}}–{{IND_RO5_RETRIEVED_KAPPA_CI_HI}} on the
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
combinations, one gives a significant positional result (focus gold, p
{{RO5_GOLD_POSITION_P}}) and three do not ({{RO5_RETRIEVED_POSITION_P}},
{{IND_RO5_GOLD_POSITION_P}} and {{IND_RO5_RETRIEVED_POSITION_P}}). **{{RO5_POSITIONAL_DIRECTION_CLAUSE}},
even where the significance does not**: the risk of
keeping the first claims of an answer rather than the band's `grounded`
claims is higher in {{RO5_POSITIONAL_DIRECTION_PHRASE}} ({{RO5_GOLD_BAND_MINUS_FIRST}},
{{RO5_RETRIEVED_BAND_MINUS_FIRST}},
{{IND_RO5_GOLD_BAND_MINUS_FIRST}} and
{{IND_RO5_RETRIEVED_BAND_MINUS_FIRST}} at matched coverage), and only the
largest of the four clears significance. The band is therefore reported as a
filter and not as a ranking, and the reason is the direction rather than the
power.

# 6. So — does it reduce hallucination in an industrial RAG model?

**The precise answer, which is not the one a panel expects:**

> The framework **declines to answer where there is no answer**, which removes
> the *opportunity* for a fabricated answer. Measured against a generator
> that is required to answer, the gate cuts the rate of answering
> unanswerable questions from {{GEN_A_NOGATE_UNANS_ANSWER_RATE}} to
> {{GEN_A_FITTED_UNANS_ANSWER_RATE}} — a fall of 29.2 points, significant at
> exact McNemar p = {{GEN_PAIRED_FITTED_UNANS_P}} — and it does so while
> still answering {{GEN_A_FITTED_ANS_ANSWERED}} of the answerable questions.
> The hypothesis holds under **both** prompt conditions, so the gate's value
> does not depend on the generator's cooperation.

Three distinctions carry the weight, and conflating any two of them would be
the easiest way to get this project wrong in a defence:

1. **A refusal rate is not a hallucination rate.** The first is a property of
   the retrieval-side pipeline; the second is a property of generated text.
   The pipeline's refusal rate on unanswerable questions is
   {{UNANS_HARD_REFUSED_PCT}} (corpus-anchored class) — it is not, and cannot
   be, quoted as a hallucination rate.
2. **Answering an unanswerable question is not the same as fabricating.** The
   fabrication column has almost no denominator: across the arms, the
   unanswerable questions produced only a handful of substantive claims. The
   headline metric is therefore the **rate of answering** an unanswerable
   question, and the accuracy column is the solid one — read as a comparison
   between arms rather than as a level, because the scoring convention moves
   the level by up to {{AVC_SPREAD_MAX}} while it leaves the comparison where
   it was.
3. **What the gate buys is *where the refusals land*, not how many.** The
   random-escalation control refuses the same number of questions and
   refuses just as many of the unanswerable ones — but it wastes
   {{GEN_PAIRED_RANDOM_ANS_B}} of its refusals on answerable questions where
   the gate wastes {{GEN_PAIRED_FITTED_ANS_B}}. The gate's contribution is a
   **precision** claim about refusals, and the paired test on the answerable
   questions (p = {{GEN_PAIRED_RANDOM_ANS_P}} for the control against
   {{GEN_PAIRED_FITTED_ANS_P}} for the gate) is where it is established.

## 6.1 So — with the gate, or without it?

This is the question that follows "is it working?", and the honest answer is
that **it depends on what "better" means**, because the gate trades one
quantity for another. The trade is measured here rather than asserted.

Under the answering prompt — where every answer the generator gives is one
it would not otherwise have declined — the four arms come out like this.
The counts are over all {{N_FOCUS_QUERIES}} questions:

| Arm | Questions answered | Correct (entailment) | Correct (key term) | **Confidently wrong** |
|---|---|---|---|---|
| The same retrieval, **gate removed** | {{TRADE_ANSWERING_NOGATE_ANSWERED}} | {{TRADE_ANSWERING_NOGATE_CORRECT_NLI}} | {{TRADE_ANSWERING_NOGATE_CORRECT_KEYTERM}} | **{{TRADE_ANSWERING_NOGATE_WRONG_ANSWERED}}** |
| **The framework (gate on)** | {{TRADE_ANSWERING_FITTED_ANSWERED}} | {{TRADE_ANSWERING_FITTED_CORRECT_NLI}} | {{TRADE_ANSWERING_FITTED_CORRECT_KEYTERM}} | **{{TRADE_ANSWERING_FITTED_WRONG_ANSWERED}}** |
| Random-escalation control | {{TRADE_ANSWERING_RANDOM_ANSWERED}} | {{TRADE_ANSWERING_RANDOM_CORRECT_NLI}} | {{TRADE_ANSWERING_RANDOM_CORRECT_KEYTERM}} | {{TRADE_ANSWERING_RANDOM_WRONG_ANSWERED}} |
| The whole corpus in the prompt | {{TRADE_ANSWERING_LONGCTX_ANSWERED}} | {{TRADE_ANSWERING_LONGCTX_CORRECT_NLI}} | {{TRADE_ANSWERING_LONGCTX_CORRECT_KEYTERM}} | {{TRADE_ANSWERING_LONGCTX_WRONG_ANSWERED}} |

**"Confidently wrong"** is the count that matters: questions the corpus
cannot answer, where the system nevertheless produced an answer. Every one of
them is a wrong answer presented with the same confidence as a right one.

**Read the table this way:**

* **Without the gate**, the system answers
  {{TRADE_ANSWERING_NOGATE_WRONG_ANSWERED}} of the
  {{N_FOCUS_UNANSWERABLE}} unanswerable questions — every one wrongly — and
  gets {{TRADE_ANSWERING_NOGATE_CORRECT_NLI}} answers right.
* **With the gate**, it answers {{TRADE_ANSWERING_FITTED_WRONG_ANSWERED}} of
  them wrongly and gets {{TRADE_ANSWERING_FITTED_CORRECT_NLI}} right.

**So the gate gives up {{TRADE_ANSWERING_CORRECT_COST_NLI}} correct answers
and removes {{TRADE_ANSWERING_WRONG_REMOVED}} confidently-wrong ones.** On the
entailment test that is a trade of
{{TRADE_ANSWERING_CORRECT_COST_NLI}} right answers for
{{TRADE_ANSWERING_WRONG_REMOVED}} wrong ones; on the key-term test it is
{{TRADE_ANSWERING_CORRECT_COST_KEYTERM}} for
{{TRADE_ANSWERING_WRONG_REMOVED}}. The two tests disagree about the size of
the cost, which is why both are reported.

**Two things that must not be misread.**

1. **The gate is not there to make answers more accurate.** It barely affects
   that — the cost is {{TRADE_ANSWERING_CORRECT_COST_NLI}} or
   {{TRADE_ANSWERING_CORRECT_COST_KEYTERM}} answers out of
   {{TRADE_ANSWERING_NOGATE_CORRECT_NLI}}. It is there to stop the
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
({{TRADE_ANSWERING_RANDOM_ANSWERED}} questions answered against
{{TRADE_ANSWERING_FITTED_ANSWERED}}) yet gets only
{{TRADE_ANSWERING_RANDOM_CORRECT_NLI}} answers right against the gate's
{{TRADE_ANSWERING_FITTED_CORRECT_NLI}} — so *refusing* is not what the gate
does; **refusing the right questions** is. And the strongest competing
approach, putting the whole corpus in the prompt, is worse on both counts at
once: {{TRADE_ANSWERING_LONGCTX_CORRECT_NLI}} correct answers and
{{TRADE_ANSWERING_LONGCTX_WRONG_ANSWERED}} confidently-wrong ones.

Under the cautious prompt the same trade is smaller, because the generator
has already declined much of what the gate would have refused: the gate
removes {{TRADE_CAUTIOUS_WRONG_REMOVED}} confidently-wrong answers there, and
on the entailment test it ends up *ahead* on correct answers as well — which
is the selection effect again, and is why the cautious condition alone would
have been a misleading headline.

# 7. Is it working? — an honest scorecard

| Component | Working? | Evidence | Caveat |
|---|---|---|---|
| Hybrid retrieval (BM25 + dense, RRF) | **Yes** | {{DELTA_BC}} R@10, p = {{P_BC}} | Fusion beats BM25 significantly; it does **not** significantly beat the lexical leg alone, and the deliverables say so |
| Cross-encoder reranking | **No** | {{DELTA_CD}} R@10, p = {{P_CD}} | Not significant, sign negative. Kept because the gate is calibrated on its score |
| Category pre-filter | **Yes** | invariant test; six-category ablation | No-op on a single-category corpus, by construction |
| Modality quota | **Yes, {{SHIPPED_QUOTA_PLACEMENT}}** | table recall {{TBL_C}} → {{TBL_F}} at no text-recall cost | Placing it after the reranker costs recall ({{DELTA_FG}}) on the focus domain; the industrial corpus prefers the other placement, by a margin that is not significant |
| Confidence gate — calibration | **Yes** | Brier {{GATE_BRIER}}, ECE {{GATE_ECE}} | Operating point is deployment-specific; thresholds must be re-fitted |
| Confidence gate — refusal on the hard class | **Partly** | {{UNANS_HARD_REFUSED_PCT}} of the corpus-anchored class | Detects *recognisable* unanswerability, not absent evidence |
| Confidence gate — its cost/benefit trade | **Measured** | removes {{TRADE_ANSWERING_WRONG_REMOVED}} confidently-wrong answers for {{TRADE_ANSWERING_CORRECT_COST_NLI}} correct ones (§6.1) | Not a quality gain — it is an explicit trade, and the direction is a domain judgement |
| Query-form validator | **Yes, in its own lane** | refused {{FORMVAL_FIX_MAL_REJECTED}} of {{FORMVAL_FIX_MAL_N}} hand-authored malformed queries and {{FORMVAL_FIX_VAL_REJECTED}} of {{FORMVAL_FIX_VAL_N}} well-formed ones; {{FORMVAL_BENCH_REJECTED}} of {{FORMVAL_BENCH_N}} benchmark queries | Lexical; deliberately fails open; the benchmark refusals are generator artefacts that read as malformed, not real questions |
| Contradiction surfacing | **Mechanism built and repaired; not evaluable on this corpus** | The gate's alarms fell from 81 to {{CONTRA_JOINT_FLAGGED}} after two measured repairs; its measured precision against reader labels is {{CONTRA_PRECISION_PCT}}; its own positive control is {{CONTRA_CONTROL_CORRECT}} of {{CONTRA_CONTROL_N}}; and the fitted calibration leaves {{CONTRA_SURFACED}} findings surfaced here | The corpus holds concept-level prose, not instance records, so it contains no contradictions for the mechanism to find — the same readers find {{CONTRA_UNFLAGGED_CONTRADICTIONS}} in {{CONTRA_UNFLAGGED_SAMPLE}} random unflagged pairs. The annotators were models. **The second corpus, in §5.8, is the corpus that can evaluate it** |
| Conflict detection and typing — the second corpus | **Detection yes, typing no** | detection {{IND_RO4_DETECTION}} against the readers' labels ({{IND_RO4_REV_STRATUM}} on the stratum where the conflicts are), typing {{IND_RO4_TYPING}}; against the construction labels, detection {{IND_RO4_CONSTRUCTION_DETECTION}} and typing {{IND_RO4_CONSTRUCTION_TYPING}} | The mechanism finds the conflicts and reports them as the wrong kind. A detector for regulatory text needs version metadata, or must be scoped to detection alone |
| The annotation rubric — the second corpus | **The binding constraint** | rubric {{IND_FACT_RUBRIC_GENERALIST}} at the generalist and {{IND_FACT_RUBRIC_SPECIALIST}} at the specialist, against {{IND_FACT_SPEC_AT_V1}} and {{IND_FACT_SPEC_AT_V2}} for specialisation | A 2×2 factorial: the reader factor is small and the rubric's wording is not, and the experiment cannot separate the rubric's definition of the target from its procedure for recognising one |
| Per-claim band — the second corpus | **Yes, as a filter** | κ {{IND_RO5_GOLD_KAPPA}} (gold) and {{IND_RO5_RETRIEVED_KAPPA}} (retrieved), against {{RO5_GOLD_KAPPA}} and {{RO5_RETRIEVED_KAPPA}} on the focus corpus; clean answers {{IND_RO5_GOLD_CLEAN_PCT}} → {{IND_RO5_GOLD_GROUNDED_ONLY_PCT}} and {{IND_RO5_RETRIEVED_CLEAN_PCT}} → {{IND_RO5_RETRIEVED_GROUNDED_ONLY_PCT}} | At chance against an independent reference on all four corpus-and-protocol combinations — the band measures agreement with itself, not truth |
| Retrieval — the second corpus (RO6) | **The negative findings replicate** | BM25 {{IND_BM25_R10}} against dense {{IND_DENSE_R10}} (Δ {{IND_BM25_VS_DENSE_DELTA}}, p {{IND_BM25_VS_DENSE_P}}); fusion {{IND_FUSION_VS_LEXICAL_DELTA}} (p {{IND_FUSION_VS_LEXICAL_P}}); pre-filter {{IND_FILTER_VS_NO_FILTER_DELTA}} (p {{IND_FILTER_VS_NO_FILTER_P}}) | Already published in three jurisdictions, so it is not claimed as new; what is new is the corollary — the fusion and the pre-filter add nothing on top of the lexical leg. The dense leg is a general-purpose 2022 encoder, so this bounds this pipeline and not dense retrieval as a class |
| The candidate pool — the second corpus | **No longer saturated** | at a pool of 50, Recall@20 {{IND_POOL_R20_AT_50}} against Recall@10 {{IND_POOL_R10_AT_50}}: {{IND_POOL_DISPLACEMENT_PCT}} of the golds are displaced out of the ten-chunk context | On the focus corpus the curve saturated at a pool of ten, so the thesis could not tell "the pool stopped helping" from "the corpus had nothing left to find" |
| The gate — the second corpus | **Yes** | τ {{IND_GATE_TAU}}, coverage {{IND_GATE_COVERAGE}} against {{FOCUS_GATE_COVERAGE}}; ECE {{IND_GATE_ECE}} against {{FOCUS_GATE_ECE}}, Brier {{IND_GATE_BRIER}} against {{FOCUS_GATE_BRIER}} | The threshold does not transfer ({{IND_GATE_TAU}} against {{FOCUS_GATE_TAU}}) and the operating point does; the pooled refusal rate is an upper bound, as in §5.2 |
| Claim scoring | **Yes, as an instrument** | audited: {{GEN_SCORER_TRUTH}}; {{GEN_SCORER_FAB}} | Every miss and every leak is a single-digit value |
| Cross-category transfer | **Partly** | ranking transfers ({{TRANSFER_XFER_TOP1_ACC}} vs {{TRANSFER_REFIIT_TOP1_ACC}} top-1 accuracy) | The *operating point* does not transfer; re-fit τ per corpus |
| Long-context comparison | **Yes, on cost** | {{LC_RATIO}}× input tokens, {{GEN_LC_COST_RATIO}}× input cost | Answer-quality margin is directional, not significant |
| Hypothesis H2.1 ("the gate reduces hallucination") | **Yes** | {{GEN_H2_1_SHORT}} | Holds under both prompt conditions; the claim is about answer *opportunities*, and the fabrication rate on generated text is measured separately |
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
.venv/bin/python -m pytest impl/tests -q          # {{N_TESTS}} tests
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
digit. {{AUDIT_PRE_REPAIR_DEFECTIVE_N}} of
{{AUDIT_PRE_REPAIR_ANSWERABLE_N}} answerable questions carried an answer
attached to the wrong question. The gold *chunk* was right in every case, so
the retrieval-side measurements were unaffected — but the answer-side accuracy
was depressed, equally for every arm. The generator was corrected, the
benchmark rebuilt, and every experiment in the project re-measured against it.
The audit now finds {{AUDIT_DEFECTIVE_N}} defective labels out of
{{AUDIT_ANSWERABLE_N}}.

**Defect 2 — the unanswerable class (Experiment 12).** The unanswerable half
was separable from the question text alone: a classifier seeing only the query
told answerable from unanswerable at ROC-AUC {{UNANS_BEFORE_AUC}}, because one
family of unanswerable questions named a fabricated identifier whose *shape*
no answerable question carried. The consequence was that the headline refusal
rate was an **upper bound, not a measurement**.

The half was rebuilt, not reported around. The repaired class is
corpus-anchored — the corpus discusses the subject and states no value for it —
and each repaired question was given a structural twin in the answerable class.
Separability fell from {{UNANS_BEFORE_AUC}} to {{UNANS_SEP_AUC}}, and the gate's
refusal rate on the hard class fell from {{UNANS_BEFORE_REFUSED_PCT}} to
{{UNANS_HARD_REFUSED_PCT}}. **The honest headline changed, and that is the
point.** The gate is good at recognising a *recognisable* unanswerable
question; detecting absent evidence is a harder problem than the first
benchmark made it look.

The pre-repair benchmark is preserved beside the repaired one so the finding
stays checkable, and the pre-repair gate result is regenerated by a script
rather than transcribed.

![{{FIG5_CAPTION}}](figures/fig5_question_only_roc.pdf)

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
   encyclopaedic corpus measured on is {{N_CHUNKS}} chunks over
   {{N_DOCUMENTS}} documents, and the regulatory corpus is
   {{IND_N_DOCUMENTS}} documents and {{IND_N_CHUNKS}} chunks. All are below
   the scale at which the statistical framing is well founded. The claims are
   framed as demonstration and mechanism, not generalisation.
2. **The first corpus is encyclopaedic, not procedural.** Industrial-engineering
   text from Wikipedia, not operating manuals or supplier specifications. It
   ships with per-document provenance, but a practitioner would not find their
   documents in it. The second corpus is authentic and binding — but it is
   *regulation*, and the only kind of industrial text this thesis measures
   against is what a regulator publishes.
3. **Single-domain by design, and the proposal's scope narrowed.**
   Supply chain management is the focus; the other {{N_CATEGORIES_WORD}}
   categories exist for the transfer experiment, which is an *intra-domain*
   study. The proposal described a **{{SCOPE_N_CATEGORIES_PROMISED}}-category**
   benchmark across industrial engineering, machine learning and data
   analytics; this thesis builds **{{SCOPE_N_CATEGORIES_BUILT}}** of the nine
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

{{NEXT_STEPS_LIST}}

# Appendix A — where things live

| Path | What it is |
|---|---|
| `impl/src/` | the framework: ingestion, lexical, dense, fusion, quota, rerank, gate, claims, contradiction, form check, pipeline |
| `impl/experiments/` | {{N_EXPERIMENTS}} experiment scripts, one per result file |
| `impl/tests/` | {{N_TEST_FILES}} test files, {{N_TESTS}} tests |
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

Seed for every stochastic component: {{SEED}}. Bootstrap resamples for the
confidence intervals: {{N_BOOTSTRAP}}.

## The one-paragraph version

> We built a retrieval-augmented generation framework for industrial
> engineering documentation whose answers pass through a **calibrated,
> non-bypassable confidence gate**: the language model is never called on a
> question the retrieved evidence does not support. We built the measurement
> to evaluate it — a silver-standard benchmark with an answerable and an
> unanswerable half, a scorer that is itself audited — and we audited our own
> instrument and repaired two defects in it. On the supply-chain focus domain
> ({{N_FOCUS_CHUNKS}} chunks, {{N_FOCUS_QUERIES}} queries), hybrid lexical and
> dense retrieval with reciprocal-rank fusion is the one retrieval change
> that is significant ({{DELTA_BC}} R@10, p = {{P_BC}}); the gate refuses
> {{UNANS_HARD_REFUSED_PCT}} of the corpus-anchored unanswerable class while
> still answering {{ANSWERABLE_ANSWERED_PCT}} of the answerable ones; and
> against a generator that answers rather than declining, the gate reduces
> the rate of answering unanswerable questions at the cost of coverage —
> **conditionally on the generator's own behaviour, which is the honest form
> of the claim**. Every component has published prior art, so the
> contribution is the measurement. The clearest new result is on a second
> corpus — {{IND_N_DOCUMENTS}} United States federal regulations read at two
> past dates, where the same provision at two issues *is* a conflict whose
> type is known by construction: there, a conflict detector's precision
> splits into **detection** ({{IND_RO4_DETECTION}}) and **typing**
> ({{IND_RO4_TYPING}}), so the mechanism finds the conflicts and reports them
> as the wrong kind. The measurement's own binding constraint was the
> annotation: a rubric factorial shows the wording of the labelling
> instructions, not the reader's specialisation, moved that number
> ({{IND_FACT_RUBRIC_GENERALIST}} against {{IND_FACT_SPEC_AT_V1}}). One
> result we do **not** claim is that lexical retrieval beats dense retrieval
> on regulatory text — that is already published, three times over.
