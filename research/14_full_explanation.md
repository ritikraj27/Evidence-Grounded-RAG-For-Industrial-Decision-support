# 14 — The whole thesis, explained

**What this document is.** A single document that explains, in full, what was
built, what was measured, what was found, what was found *not* to hold, and
what every term in the project means. It is written to be read once before the
defence and then used as the reference during it. It assumes no prior
knowledge of the project, and it explains the vocabulary from scratch, because
a panel will ask about the vocabulary.

**How to use it.** §1 is the version for a stranger. §2 is the vocabulary —
scan it once so that no word in a question is unfamiliar. §3 is the six
objectives, one at a time, each with what was asked, how it was tested, what
was found and what a panel will push on. §4–§7 are the corpora, the method,
the experiments and the statistics, in the order a question would ask for them.
§8–§10 are the results, the novelty position and the limitations. §11 is the
questions a panel will ask and the answers. §12 is what remains open, and
§13 is where everything lives.

**Every number in this document is bound to a result file.** The script
`impl/scripts/verify_reported_numbers.py` re-derives them from the artefacts
and fails the build if any of them disagrees with what a document says. If a
number here is wrong, the build breaks.

---

## 1. The one-page version

**The problem.** Industrial practitioners make decisions from technical
documentation. They have to find the right passage, work out which version of
it applies, notice when two documents disagree, and know how much to trust
what the system tells them. Retrieval-augmented generation (RAG) — a language
model answering a question using passages retrieved from a document collection
— is the tool for the first of these and is usually trusted for all four.

**What was built.** A five-mechanism framework for industrial RAG, and a
measurement of whether the mechanisms do what they were designed to do. The
mechanisms are: a **confidence gate** that refuses to answer when the
retrieved evidence does not support an answer; a **modality quota** that
guarantees the final context contains tables and charts; **hybrid retrieval**
(lexical + dense, fused and reranked); a **contradiction gate** that surfaces
disagreements between passages instead of silently resolving them; and
**per-claim confidence banding**, which tags every sentence of the answer as
`grounded`, `inferred` or `uncertain` with a citation.

**The honest headline.** Four of the original design's properties turned out to
be wrong, and the thesis's value is that it says so with numbers:

1. **A reranker cannot improve recall if its candidate pool is the same size
   as the final context.** It can only reorder what it is given. The
   candidate-pool curve peaks and then declines, which explains a reranker
   regression of −5.34 percentage points previously reported on an
   independent corpus and turns an anomaly into a testable hypothesis.
2. **The modality quota belongs *after* the cross-encoder**, not before, which
   is the opposite of the rule the framework was designed on. A constraint on
   a downstream artefact should be enforced where it can still choose the
   candidates, not where it must work against another component's judgement.
3. **The corpus's modality composition decides whether a modality-aware
   mechanism can have any effect at all.** A corpus that is 88.8% prose has
   almost nothing for a table quota to select.
4. **The category pre-filter is a no-op** on the focus corpus, and on the
   second corpus it costs nothing and gains nothing.

**The clearest new result.** A conflict detector's precision, reported as one
number, conflates two different questions: *is the alarm pointing at something
real* (detection) and *is the branch that raised it the branch that owns the
conflict* (typing). Measured on a second corpus of United States federal
regulations read at two past dates — where the same provision at two issues
**is** a conflict with its type known by construction, so no annotation is
needed — the two numbers are **1.000 and 0.000** against the construction
labels, and **0.659 and 0.073** against a panel of readers' labels. The
mechanism *finds* the conflicts and *reports them as the wrong kind*. It calls
supersessions contradictions, and it cannot say which version of a superseded
provision is in force, because nothing in the retrieved passages carries the
version. That turns into a specification: a detector for regulatory text
needs version metadata, or must be scoped to detection alone.

**The second new result, and its caveat.** The per-claim confidence band
measures *agreement with itself*, not correctness. Against an independent
reference it is at chance (κ = 0.049, 0.069, 0.062, 0.044 on the four
corpus-and-protocol combinations), while its three bands are ordered on the
evidence the band itself saw. As a *filter* it works — keeping only the
`grounded` claims raises the share of answers containing no wrong claim from
34.4% to 50.0% on the focus corpus's gold protocol and from 90.4% to 95.4% on
the industrial corpus's. As a *ranking* it does not, and the positional
comparison that supports the reading replicated on only one of the four
combinations, so it is reported as evidence, not as the finding.

**The third, and the most humbling.** The measurement's binding constraint was
the *annotation*, not the mechanism. A 2×2 factorial over the annotation rubric
and the reader's domain specialisation, with everything else held constant,
shows the rubric's wording moved the measured precision by **+0.366** and
**+0.317** while the reader's specialisation moved it by **+0.049** and
**+0.000**. The mechanism is concrete: the old rubric required a version
marker, and a regulation does not write its own version in its text, so it
missed **63 of the 82** supersessions it was asked to find, calling them
`no_conflict`. A number that moves by a factor of nine with the wording of its
own rubric is not yet a measurement of the thing under test.

**What is claimed, and what is not.** Five findings were checked against the
published literature. One is a new measurement (the detection/typing
decomposition). One is a new measurement with a published mechanism around it
(the band). One is a sharper version of a published principle (rubric versus
specialisation). One is a known method pointed at a new purpose (point-in-time
regulatory corpora). And one — "BM25 beats a dense encoder on regulatory text" —
is **already published**, three times, in three jurisdictions, so it is not in
the abstract and is reported only as a boundary condition on this pipeline.

---

## 2. The vocabulary

Nothing here is assumed. A panel will use these words; this section says what
each one means *in this project*, because several have a specific meaning here.

### 2.1 The domain words

**Industrial documentation.** Technical documents that a working practitioner
uses to make decisions: operating procedures, control plans, specifications,
standard operating procedures, failure-mode analyses, supplier documents. The
thesis's own limitation table names "a licensed, multi-domain industrial
corpus" as the remediation its original corpus lacked, because the corpus it
had was encyclopaedic *about* industrial engineering rather than industrial
documentation itself.

**Corpus.** The collection of documents the system searches. A *chunk* is a
piece of one. The thesis has three corpora (§4).

**Benchmark.** A set of questions with known answers, used to score a system.
A *gold chunk* is the chunk that contains the answer to a question.

**Answerable / unanswerable.** A question is answerable if the corpus
contains its answer; unanswerable if it does not. The unanswerable half is
what makes a *refusal* benchmark possible: without it, a system that answers
everything scores 100% recall and 0% hallucination, and nothing can be
measured.

**Silver standard.** Labels *derived* from the document by a rule rather than
annotated by an expert. Cheap and perfectly reproducible; slightly optimistic,
because the derived gold chunk is guaranteed to contain the answer somewhere,
whereas an expert might judge it insufficient. It inflates *absolute* recall
but does not bias the *comparison* between systems, because every system is
scored against identical labels.

**SQuAD 2.0.** The published benchmark that established the abstention task
and its metric: a system must both answer answerable questions correctly and
decline unanswerable ones. It reported a strong neural system at 86% F1 on
SQuAD and 66% on SQuAD 2.0 — twenty points lost to confidently answering
questions that have no answer, in a purely general-domain setting.

### 2.2 The retrieval words

**Chunking.** Splitting a document into the units that are retrieved. Done
*modality-aware* here: text into 120-word windows with 30-word overlap;
tables are never split, because a table is the atomic unit of a specification;
and charts are their own modality.

**Modality.** Which kind of thing a chunk is: `text`, `table` or `chart`. The
framework's quota mechanism acts on the modality composition of the final
context.

**BM25.** A lexical ranking function: it scores a document by how many times
the query's terms appear in it, weighted by how rare those terms are across
the corpus (IDF), with the frequency contribution saturating and the length
normalised. Its strength is exact-term matching; its weakness is that it
cannot match a query to a passage that uses different words for the same
thing. It is implemented here from first principles so its parameters and edge
cases can be defended directly.

**Dense retrieval / embedding.** Turning a passage and a query into vectors so
that "meaning" rather than "wording" is what is compared. The score is the
cosine similarity — the dot product of the normalised vectors. The encoder
here is `BAAI/bge-m3`, a 1024-dimensional retrieval-trained multilingual
encoder.

**Dual-encoder vs cross-encoder.** A dual encoder (used for dense retrieval)
embeds the query and the document *separately*, so the comparison is a cheap
vector dot product, but the two vectors never see each other. A cross-encoder
reads the query and the document *jointly*, so every token of the document
attends to every token of the query: strictly more expressive and strictly
more expensive. It is applied to a shortlist rather than to the corpus.

**A logit, not a probability.** The cross-encoder's output is a raw score
whose scale shifts with query difficulty. Thresholding it directly is a
category error, which is why the framework *calibrates* it (§2.3).

**Reciprocal Rank Fusion (RRF).** Combining two ranked lists without comparing
their scores: `RRF(d) = Σ 1/(k + r_i(d))`, with `k = 60` and `r_i(d)` the
rank of document *d* in list *i*. The reason to use ranks rather than scores
is that BM25 scores, cosine similarities and cross-encoder logits are on
incomparable scales; summing them needs a fitted weighting that does not
transfer across corpora, whereas rank is scale-free.

**Candidate pool.** The number of candidates the reranker is given. This is
the thesis's central retrieval finding: a reranker can only reorder within the
pool it is given, so a pool the same size as the final context cannot improve
recall at all.

**Recall@k.** Of the questions whose gold chunk exists, the fraction for which
the gold chunk is in the top *k*. **MRR** (mean reciprocal rank) is the mean
of 1/rank of the first correct result. **nDCG@k** is a rank-sensitive
discounted gain. **Precision@k** is the fraction of the top *k* that are
relevant.

**Modality recall.** Recall restricted to one modality — "of the queries whose
gold chunk is a table, how often did the table come back?" This is how the
quota claim is tested.

### 2.3 The confidence words

**Bayes' theorem in odds form.** `P(R|d) = P(R)/P(d|¬R) × P(d|R)/P(d|¬R)`:
prior odds times likelihood ratio. The framework uses a logistic model on the
log-odds scale, `P(R|d) = σ(β₀ + β₁x)`, fitted by maximum likelihood. Because
the log-loss is convex in `(β₀, β₁)`, Newton's method converges reliably, and
the implementation carries the gradient and Hessian explicitly.

**Calibration.** Whether a predicted probability means what it says. Measured
by the **Brier score** (mean squared error of the probability) and the
**Expected Calibration Error** `ECE = Σ_b (n_b/N)|acc_b − conf_b|`: among all
the predictions in bin *b*, the gap between how confident the system was and
how often it was right. A reliability table shows it bin by bin.

**The gate.** A *code-level branch* that decides whether to answer. Its
decision is a calibrated probability compared against a threshold τ, and it is
**control flow, not an instruction**: when it rejects, the language model is
never invoked. Three properties follow that no instruction can give — the
model cannot talk its way past it, the refusal is reconstructible ("maximum
calibrated relevance probability 0.312 against threshold 0.500"), and it
portable without retraining.

**Answer-in-context detectability.** The quantity the gate actually predicts:
whether the retrieved context contains the answer at all. It is deliberately
*not* called *sufficiency*, because the published literature reserves
*sufficiency* for a set-level property — what closes the evidence gap once
relevance has been established — and using the word here would claim prior
art this thesis does not have.

**Abstention / refusal.** Saying "the corpus does not answer this". A
refusal benchmark measures how much refusing costs and how much it buys.

**Selective prediction.** Treating the decision to answer as a *policy* with a
stated operating point, rather than a single accuracy number.

**Risk–coverage curve.** For each threshold, the fraction of queries answered
(**coverage**) against the **risk**: of the queries answered at that
threshold, the fraction that had no answer in context. Two degenerate
policies bound the curve: always answering (risk = the base rate of the
negative class, coverage = 1) and always refusing (risk = 0, coverage = 0).

**Coverage.** The fraction of *all* queries the gate answers — answerable
plus unanswerable. **Abstention precision**: of the queries the gate refused,
the fraction that really were unanswerable.

### 2.4 The conflict words

**Entailment / NLI.** Natural language inference: does passage A entail
passage B? The framework uses a DeBERTa-v3 MNLI model, which outputs a
probability that the second passage is *entailed* by the first.

**Contradiction vs supersession.** This distinction is the spine of the
thesis's new result, so it is worth being exact.

- A **contradiction**: two passages cannot both be true at the same time.
  "The limit is 5 ppm" and "the limit is 25 ppm" — with the same substance,
  the same scenario, the same date.
- A **supersession**: two passages *can* both be true, because they describe
  the same rule at two different times. "Rev 3 sets the EOQ at 187 units" and
  "Rev 4 sets the EOQ at 95 units" are both true: Rev 4 replaced Rev 3.
  Reporting a supersession as a contradiction is the single most damaging
  error available to the system, because it tells the practitioner the policy
  is inconsistent when it was in fact updated.

**The revision-supersession check.** The branch that tells the two apart. In
this project it was found that the *rubric* the readers used to make that call
was the problem: the first version required a version marker in the text, and
a regulation does not write its own version in its text.

**Detection precision.** Of the detector's alarms, the fraction that point at a
real conflict of any type. **Typing precision.** Of the detector's alarms, the
fraction raised by the branch that *owns* the conflict. A detector can be
excellent at the first and systematically wrong at the second; that is exactly
what happened here.

**Term mismatch.** Two passages use the same word for different things. This
is the commonest false alarm in the industrial corpus and the reason the
quantity branch has so little to fire on: OSHA harmonised its construction
and general-industry limits for asbestos, cadmium, lead and silica, so the
same substance carries the same limit in both, and 58 of 60 cross-document
pairs a specialist reviewed turned out to be the same word used for different
things.

**Always-flag / never-flag baselines.** The two degenerate policies for a
conflict detector: flag every pair, or flag none. A precision of 0 is
meaningless without them, because the base rate of real conflicts sets the
floor.

### 2.5 The evidence words

**Atomic claim.** The smallest claim an answer makes, obtained by splitting
the answer by sentence and then at discourse markers.

**Entailment probability `e_i`.** For claim *i* and retrieved chunk *i*, the
probability that the chunk entails the claim.

**Noisy-OR.** Combining several fallible witnesses: `q = 1 − Π(1 − e_i)`.
Each chunk is an independent witness; the claim is supported if at least one
covers it. The framework takes the **maximum** across chunks rather than the
mean, so that one strongly contradicting chunk is not diluted by many
irrelevant ones.

**The three bands.** `grounded` if `q ≥ 0.80`, `inferred` if `q ≥ 0.45`,
otherwise `uncertain`.

**Information gain.** `IG = H(prior) − H(q)` in bits: how much the retrieved
set reduced uncertainty about the claim. It is *symmetric about q = 0.5*, so a
claim with `q = 0.9` and one with `q = 0.1` both yield 0.531 bits. That is
why the band cuts on `q` and information gain is reported separately — the two
answer different questions and must not be conflated.

**The circularity problem.** The band is computed from the evidence the
retriever returned. If it is then compared against a reference computed from
*the same* evidence, the band is being compared with itself, and high
agreement means nothing. This is why the thesis measures the band against an
**independent reference** — a separate judge reading the evidence this run
used, but deciding whether the claim is *true* rather than whether the
passages entail it.

### 2.6 The statistics words

**Wilcoxon signed-rank test.** A paired non-parametric test: it asks whether
the per-query differences are systematically one way. Preferred over the paired
*t*-test because per-query faithfulness is bounded and left-skewed with a mass
at 1.0, which violates the normality assumption on the paired differences.

**Cohen's `d_z`.** The standardised mean of the paired differences: how large
the effect is in standard-deviation units. A *p*-value answers "is it
unlikely"; an effect size answers "is it large". The difference is material at
`n = 239`.

**Bootstrap.** Resampling with replacement to get an interval. The bootstrap
unit here is the **answer**, not the claim, because claims within an answer are
not independent — this is a *cluster* bootstrap.

**Wilson interval.** The confidence interval for a proportion, computed
directly rather than from the normal approximation, so it behaves correctly at
the extremes and near 0 and 1.

**Cohen's κ.** Chance-corrected agreement between two raters: 1 is perfect
agreement, 0 is what two independent raters would achieve by chance, and
negative values mean worse than chance. It is the right statistic for a
categorical label set where the marginals are skewed — which is exactly the
case for "is this claim supported", where most claims are supported.

**Per-claim bootstrap over answers.** The RO5 measurement's unit of
resampling is the answer, because the claims inside one answer share an
evidence set and are not independent.

**Construction labels.** Labels known *by construction* rather than by
annotation: in the revision corpus, a paragraph and its amended self are
known to be a supersession or a quantity conflict without anybody reading
them. They are the only labels in this project that need no human judgement.

---

## 3. The six research objectives

### RO1 — Design

**Asked:** to specify a framework for industrial RAG that addresses the three
requirements industrial users bring and generic systems lack: an evidence
trail, a confidence check, and contradiction handling.

**Delivered:** five mechanisms, specified as equations and implemented as
code. The pipeline is

```
ingest -> index -> [form -> filter -> BM25 + dense -> RRF -> rerank
                                -> GATE -> quota] -> claims -> answer
```

**Status: closed.** Each mechanism has published prior art and is positioned
against it rather than claimed as priority. That is a deliberate position,
not a weakness: the thesis's contribution is the measurement.

### RO2 — Component-level evaluation

**Asked:** to evaluate each mechanism individually, not just the whole
system.

**Delivered:** a seven-rung ablation (A BM25 → B dense → C hybrid → D
+reranker → E +category filter → F +quota pre-rerank → G +quota post-rerank),
a threshold sweep for the gate with the calibration refitted per retrieval
configuration, and a risk–coverage curve.

**Status: closed, with four negative results.** The interesting output was
not which rungs won but which design assumptions failed (§1).

### RO3 — Failure-mode characterisation

**Asked:** to characterise how the framework fails, and to correct the design
where it does.

**Delivered:** the candidate-pool curve that explains the −5.34-point
reranker regression; the quota's inverted pipeline position; the corpus
composition's predictive role; the category pre-filter's no-op status; and the
benchmark defect described in RO2's audit below.

**Status: closed, and the hypothesis was rewritten.** RO3's original
hypothesis — that hybrid + RRF + category pre-filter beats flat retrieval — is
contradicted by the thesis's own numbers on **both** corpora (fusion Δ 0.000,
p = 1.000; pre-filter Δ 0.000, p = 1.000 on the industrial corpus). It is now
stated as a negative-result hypothesis. This is recorded as a change the
thesis made to itself, not a failure.

### RO4 — Cross-document contradiction surfacing

**Asked:** to surface disagreements between documents rather than silently
resolving them, and to measure whether the mechanism actually works.

**Status: closed, and the answer is "it finds them and mislabels them".**

The first measurement was unevaluable: the corpus had no conflicts in it, so
the mechanism's precision was 0% and that was uninformative. The corpus was
rebuilt — hence the second corpus. On it, 240 pairs (90 amendment pairs and
150 retrieval neighbours, mined by the retriever's own signal and never by the
detector's) were read by a panel of domain specialists plus a generalist
control, blind to the detector:

| | Value |
|---|---|
| Detection precision (is there something there) | **0.659** (CI 0.505–0.784) |
| … on the stratum where the conflicts actually are | **0.897** |
| Typing precision (is it typed correctly) | **0.073** (CI 0.025–0.194) |
| Under the *shipped* operations vocabulary | detection 0.650, typing 0.000 |
| Against the construction labels | detection **1.000**, typing **0.000** |
| Quantity branch recall on 35 limit changes | **0.000** |
| Quantity branch, 1,776 cross-document candidates | 0 of 13 alarms confirmed |

**What a panel will push on:** "your labels are model-generated, so the
precision is only as good as the labels." The answer is in the row that
needs no labels at all — against the construction labels, detection is 1.000
and typing is 0.000. The typing failure does not depend on any annotation.

### RO5 — Per-claim confidence banding

**Asked:** to attach a per-claim confidence signal a practitioner can act on,
and to measure *what it buys*.

**Status: closed. It buys a filter, not a ranking.**

350 claims on the focus corpus and 294–316 on the industrial corpus, read by
two readers (κ = 0.902 between them) plus an adjudicator, under two evidence
protocols:

| | Gold evidence ("is the claim right?") | Retrieved evidence ("does a reader agree with the scorer?") |
|---|---|---|
| Band vs independent reference (κ) | **0.049** (CI −0.026, 0.124) | 0.069 (CI −0.002, 0.139) |
| `grounded` / `inferred` / `uncertain` error | 0.542 / 0.513 / 0.610 | **0.118 / 0.103 / 0.220** |
| Answers with no wrong claim → keeping only `grounded` | 34.4% → **50.0%** | 59.4% → **81.2%** |

Replicated on the industrial corpus with the same generator: κ 0.062 and
0.044 (both intervals include zero), bands ordered 0.069 / 0.088 / 0.156 and
0.047 / 0.066 / 0.105.

**What a panel will push on:** "then the band is useless." The answer is that
it is at chance against *correctness* but ordered against *entailment*, and
as a filter it raises the clean-answer rate by 15.6 points (focus, gold) and
5.0 points (industrial, gold). The finding is the decomposition, and the
decomposition is what tells a practitioner what the band is for.

### RO6 — Industrial corpora, benchmarks, cross-category generalisation

**Asked:** to evaluate on industrial corpora and industrial benchmarks, and to
study generalisation across categories.

**Status: closed.** Three findings replicate on authentic regulatory text:

- BM25 beats the dense encoder: Δ R@10 −0.081, **p = 0.00026**, n = 247 —
  three times the effect size and twenty-five times the significance of the
  focus corpus's p = 0.025. **Already published**, so not claimed as new; the
  new part is the corollary that the fusion (Δ 0.000, p = 1.000) and the
  category pre-filter (Δ 0.000, p = 1.000) added nothing on top of it.
- The candidate-pool curve is no longer saturated: at a pool of 50,
  R@20 = 1.000 while R@10 = 0.988, so **1.21%** of the golds are retrieved and
  then pushed out of the ten-chunk context.
- The gate's **threshold does not transfer** (τ = 0.40 here against 0.05 on
  the focus corpus) but its **operating point does** (coverage 0.691 against
  0.699).

---

## 4. The corpora, the benchmarks and the benchmark audit

### 4.1 Three corpora

| | **Focus** | **Multi-category** | **Industrial (eCFR)** |
|---|---|---|---|
| What it is | English Wikipedia articles *about* industrial engineering | the same, six categories | US federal regulations |
| Documents | 46 | 46 | **110** |
| Chunks | 2,383 | 2,383 | **2,443** (2,324 text, 119 table) |
| Categories / regimes | 6 | 6 | **4** regulatory regimes |
| Focus domain | supply chain management: 14 docs, 735 chunks | — | — |
| Licence | CC BY-SA 4.0 | CC BY-SA 4.0 | **public domain** (US government work) |
| Benchmark | 176 queries (32 answerable, 144 unanswerable) | 276 (132 / 144) | **444 (247 / 197)** |

The focus corpus is where the pre-registered measurements live, so it carries
the headline numbers. The multi-category corpus exists because the
cross-category transfer study needs more than one category. The industrial
corpus is the one built to close RO4 and RO6.

**The industrial corpus's four regimes:** OSHA general industry (29 CFR
1910), EPA risk management programmes (40 CFR 112), EPA new source
performance standards (40 CFR 60), and DOT hazardous materials (49 CFR 173).

**Why it is the right artefact.** It is *authentic* (binding text with numeric
requirements — exposure limits, separation distances, capacities) and it is
*versioned*. The eCFR versioner API serves any regulation as it stood on any
past date, so the same section read on **2021-12-31** and **2026-06-01** is the
same rule at two issues. Aligning the two snapshots gives **948
amended-paragraph pairs**, of which **361 (38.1%)** state different numbers in
the two vintages. Such a pair *is* a conflict, and its type is known **by
construction** — no annotation required. One artefact therefore closes two
objectives at once, and supplies the labels that the Wikipedia corpus cannot
contain.

**The revision corpus's candidate pool.** 240 pairs: 90 `revision` pairs (a
paragraph and its amended self) and 150 `similar` pairs (cross-document
retrieval neighbours). The pool is mined by the **retriever's** own lexical
signal and **never** by the detector's numeric rule, its NLI probability or
its subject check. This matters: a pool selected on the detector's decision
rule cannot measure the detector's precision, because every alarm would be in
the pool by construction.

### 4.2 The benchmark defect, and its repair

This is a contribution, not a caveat, because the repair changes what the
headline number means.

**The defect.** The unanswerable class is the half on which a refusal
benchmark lives or dies. It was audited, and a classifier that saw **only the
question** — no retrieval, no evidence, no reasoning about the corpus —
told the answerable questions from the unanswerable ones at **ROC AUC 0.999**.
The mechanism was concrete: the class's designated hard case asked about a
fabricated identifier (`SKU AST-5454`), and every one of those questions
carried an identifier shape that no answerable question carried, so **one
regular expression separated the two classes perfectly, catching 76.4% of the
unanswerable class with no false positives at all**. If a system's
unanswerability is visible in the question, then a system refusing on the
question's *shape* scores as well as one reading the passages, and the
benchmark cannot tell them apart. On the defective class the gate refused
**91.7%** — an upper bound on the refusal rate, not a measurement of it.

**The repair.** The class was rebuilt as a *corpus-anchored* one: the same
question stems, the same source documents, the same label machinery, and each
repaired question given a **structural twin** in the answerable class — same
stem, same subject size, same shape markers, no word in common (106 of 110
have one). Every measurement was taken again.

**After the repair.** The shape-only classifier scores **0.605** against a
permutation null of 0.452; the one-rule shortcut carries **0.0%**; and on the
better-powered multi-category benchmark the same measurement gives **0.556**
against a null of **0.506** — indistinguishable from chance. At τ = 0.05 the
gate refuses **22.7%** of the corpus-anchored hard class and **76.5%** of the
out-of-domain class (the latter being unanswerable for any system that knows
what the corpus is about).

**The industrial corpus was audited the same way, and passed.** The
one-rule shortcut catches **0 of 197**; a question-only classifier separates
the classes at ROC AUC **0.708** against a permutation null of **0.505**; and
the bag-of-words separability is 0.793. The residual separability is question
*length* — median 73 characters for answerable against 50 for unanswerable —
which is reported rather than hidden.

**The benchmark's own certification.** The generator writes a certificate into
each record, and a predicate written independently of the generator re-checks
it: 0 failures.

### 4.3 A second defect: the per-claim rate and the shipped rate

The reported "claim hallucination rate" of 0.382 is a measure of *entailment*
presented as a measure of *hallucination*. Two independent estimates bracket
it: the shipped rate counts a claim as hallucinated when the NLI does not
entail it over the retrieved passages (0.382), while the reference rate counts
it when an independent judge reading the same evidence does not find the
claim supported (0.571 on the gold protocol, 0.164 on the retrieved one). The
two functions of the same evidence — a noisy-OR against a maximum — disagree
on 23 of 350 claims.

---

## 5. The framework, end to end

### 5.1 Ingestion (offline, once per document)

**Structural parsing.** A PDF is a visual object: a page is a layout of text
blocks, ruled tables and figures, and becomes a table only once the ruling
lines are understood. A naive text extractor destroys that structure, and in
an industrial corpus the binding requirements live in tables — an economic
order quantity, a safety-stock rule, an acceptance tolerance. Blocks with
bounding boxes are classified as `text`, `table` (overlapping a detected table
region) or `chart` (mostly non-alphabetic).

**Serialisation.** Tables become markdown with horizontally merged cells
forward-filled so the result stays rectangular, and are **never split** — a
table is the atomic unit of a specification. Text is chunked into 120-word
windows with 30-word overlap; a trailing fragment shorter than twelve words
is merged into its predecessor rather than emitted as its own unit.

**Metadata.** Every chunk carries document identifier, page, modality, section
and caption. The corpus's modality composition is measured and reported,
because it predicts whether modality-balancing can have any effect at all.

### 5.2 Retrieval (online, per query)

1. **Form check** — refuses an empty query, a query of only function words or
   deictics, and a query ending on a word that cannot end a question. It runs
   *before* retrieval, so a request it refuses costs no embedding pass, no
   cross-encoder pass and no model call.
2. **Category pre-filter** — restricts the candidate set to the query's
   category.
3. **BM25 leg** and **dense leg** run independently.
4. **RRF fusion**, k = 60.
5. **Cross-encoder rerank** of the fused shortlist, on a **top-50** pool.
6. **Confidence gate** — refuses or passes.
7. **Modality quota** — adjusts the final context.

### 5.3 The confidence gate

**The label, and why it is a query-level label.** The gate does not ask
whether *this candidate* is the gold chunk; it asks whether the retrieved
context contains the answer at all. This matters because with about fifty
candidates per query and one gold chunk, chunk-level positives have a base
rate of roughly 2%. A chunk-level classifier answering "nothing is relevant"
is right 98% of the time; maximum-likelihood fitting against that label
returns a large negative intercept and a nearly flat slope, and the
calibration metrics look excellent because they measure the base rate rather
than the filter. The label is therefore 1 when the context contains a gold
chunk — *found or missed*, because in both cases the correct behaviour is to
refuse.

**The five features**, all available before generation: the top cross-encoder
score, the mean of the top three scores, the best BM25 score, the best RRF
score, and the number of candidates clearing a low relevance bar.

**The split** is by *query*, not by candidate, so no candidate from an
evaluation query can leak into the calibration set.

**Why refuse rather than refine.** CRAG, the nearest prior art, responds to
low confidence by improving the evidence and continuing, and calls the LLM in
every branch. Refuse-and-decline is preferable under a specific condition: the
corpus is a fixed, closed set of controlled documents and the cost of a wrong
answer exceeds the cost of no answer. That is the industrial case, and stating
the condition precisely *is* the argument.

### 5.4 The modality quota

A floor on the share of the final context occupied by tables (0.15) and charts
(0.05), implemented as a **swap**: take the natural top-k untouched and, while
a floor is unmet, swap the lowest-ranked item of the over-represented modality
for the highest-ranked available item of the under-represented modality. A
rebuild-based implementation — walk the ranking, skip what would breach a
floor, backfill — silently removes good high-ranked items and measurably
degraded table recall during development.

**Why the position matters.** Applied before the reranker, the quota selects
which chunks the reranker sees; the reranker re-scores them and can push the
forced tables back out, so the quota does not bind and merely removes good
text chunks from the candidate pool. Applied after the reranker, it adjusts
the final context by swapping the chunks the reranker ranked lowest, so it
binds at minimal cost. **The framework was designed the other way round, and
the measurement inverted it.**

### 5.5 The contradiction gate

Two accepted chunks are flagged as conflicting only when two independent gates
agree:

```
flag(A, B) = contradiction(A, B) AND same_subject(A, B)
```

`contradiction` is the NLI probability from a DeBERTa-v3 MNLI model;
`same_subject` combines embedding cosine similarity (threshold 0.55) with
Jaccard overlap of concrete identifiers (threshold 0.10). The conjunction
matters because raising the NLI threshold alone reduces false positives only
by excluding genuine conflicts, whereas an orthogonal signal lets the two
error types be traded off separately.

Two further mechanisms matter in industrial documentation. A **numeric
conflict** — two passages attaching different values to the same quantity — is
an explicit contradiction regardless of the NLI model's confidence. A
**revision-supersession check** suppresses the flag when the two passages
carry different revision markers and sufficient entity overlap.

Following ContextConflict, a conflict *type* is reported rather than a binary
flag.

### 5.6 Per-claim confidence banding

Each answer is decomposed into atomic claims by sentence and then split at
discourse markers. For each claim the NLI model gives an entailment
probability `e_i` for every retrieved chunk, combined by noisy-OR across
chunks (using the maximum across chunks rather than the mean, so that one
strongly contradicting chunk is not diluted by many irrelevant ones). The band
is cut on `q`; information gain in bits is reported beside it; and every claim
carries its band, its citation identifiers and, where the evidence contradicts
it, a *contradicted* marker pointing at the contradicting passage.

### 5.7 Generation

The generator is called only if the gate passed. Its output is split into
claims, each tagged, and each claim cited. The two prompt conditions used in
the comparison — `cautious` and `answering` — differ by a single sentence, and
a refusal rate obtained under one prompt is not a property of the model.

---

## 6. The experiments, one at a time

Each entry gives the question, the design, the measurement, the result, and
what the result does *not* say.

### E1 — The retrieval ablation

**Q:** does each retrieval component earn its place?
**D:** seven rungs, the same queries, paired Wilcoxon between adjacent rungs,
calibration refitted per configuration.
**Focus result (n = 32 answerable over 735 chunks):**

| System | R@5 | R@10 | R@20 | MRR | nDCG@10 | Tbl R@10 |
|---|---|---|---|---|---|---|
| A. BM25 only | 0.969 | 0.969 | 1.000 | 0.736 | 0.792 | 1.000 |
| B. Dense only | 0.781 | 0.813 | 0.875 | 0.652 | 0.688 | 0.875 |
| C. Hybrid (RRF) | 0.969 | **1.000** | 1.000 | 0.798 | 0.847 | 1.000 |
| D. + cross-encoder | 0.906 | 0.969 | 1.000 | 0.795 | 0.836 | 1.000 |
| E. + category filter | 0.906 | 0.969 | 1.000 | 0.795 | 0.836 | 1.000 |
| F. + quota (pre-rerank) | 0.969 | **1.000** | 1.000 | 0.819 | 0.864 | 1.000 |
| G. + quota (post-rerank) | 0.906 | 0.938 | 0.938 | 0.789 | 0.826 | 1.000 |

**Reading it.** Fusion beats the dense leg by +0.188 (p = 0.014) but beats
its own lexical leg by only +0.031 (p = 0.317, not significant). The
cross-encoder *lowers* Recall@10 from 1.000 to 0.969 (p = 0.317) — because
the pool it was given was the same size as the final context. The category
filter is a no-op on a one-category corpus. The quota before the reranker
recovers what the reranker lost; the quota after it costs 6.25 points.
**Does not say:** that the reranker is useless — it moves MRR and nDCG, and on
the industrial corpus with a 50-candidate pool it *helps* (+0.028, p = 0.020).

### E2 — The candidate-pool sweep

**Q:** how big should the reranker's candidate pool be?
**D:** sweep the pool size; measure Recall@10 and Recall@20.
**Focus:** the curve saturates at pool 10, where R@10 = R@20 = 1.000, and then
falls slightly as the reranker is given more distractors to reorder. Because
it saturates, the focus corpus *cannot* distinguish "the pool stopped helping"
from "the corpus had nothing left to find".
**Industrial:** the curve is sharp. At pool 50, R@20 = 1.000 and R@10 = 0.988
— **1.21% of the golds are retrieved and then pushed out of the ten-chunk
context by the reranker's own ordering.**
**Does not say:** that a bigger pool is always better. The measured trade is
"enlarging the pool buys recall the context cannot hold".

### E3 — The gate as a selective-prediction policy

**Q:** what does refusing cost, and what does it buy?
**D:** sweep τ; for each value report the fraction of answerable questions
answered, the fraction of unanswerable questions refused, abstention precision
and coverage; report the whole risk–coverage curve; compare against
always-answer and always-refuse.
**Focus:** τ = 0.05, coverage 0.699, abstention precision 0.962, ECE 0.114,
Brier 0.144.
**Industrial:** τ = 0.40, coverage 0.691, abstention precision 0.847, ECE
0.075, Brier 0.159. At that operating point it answers **91.5%** of the
answerable queries and refuses **58.9%** of the unanswerable ones.
**The result that matters:** the threshold does not transfer; the operating
point does. **The calibration is a fitted parameter of the deployment, not a
constant of the architecture.**
**Does not say:** that the gate certifies its own confidence. The conformal
guarantees rest on an exchangeability assumption that a single-category
industrial corpus violates.

### E4 — The cross-category transfer study

**Q:** does the gate transfer across industrial sub-domains?
**D:** fit the coefficients and threshold on one half of the six categories,
apply unchanged to the held-out half, plus a leave-one-category-out variant.
**Result:** the *ranking* of configurations transfers; the *threshold* does
not, and the error is systematic — a threshold fitted on a weaker retrieval
configuration is too permissive when applied to a stronger one.
**Does not say:** that the corpora differ by category in the way the thesis's
own "cross-category" phrasing suggests. They are industrial sub-domains, so
this is an **intra-domain** transfer, and the thesis re-reads the original
claim that way rather than claiming cross-domain generalisation it did not
test.

### E5 — The benchmark audit (described in §4.2)

### E6 — The revision corpus and the conflict panel

**Q:** does the contradiction gate work on a corpus that contains conflicts?
**D:** 240 pairs mined by the retriever; read by four domain specialists (OSHA
general industry 133 pairs, process safety 44, environmental control 52, DOT
hazmat 11), a generalist control on all 240, and an adjudicator for disputed
claims; all blind to the detector. Two specialists verified their calls
against the eCFR's point-in-time API rather than reading alone.
**Labels:** 84 supersession, 90 term_mismatch, 64 no_conflict, 2 granularity.
**Result:** §3/RO4's table.
**Agreement:** κ = 0.303 between the generalist control and judge A; 0.65–0.72
between each specialist and the generalist control.
**Does not say:** that the labels are *correct* — only that the readers agree.

### E7 — The rubric × specialisation factorial

**Q:** the RO4 measurement moved when the rubric changed. Was that the rubric,
or the reader?
**D:** 2×2. The same 240 pairs, the same detector, the same regime briefs.
The v1 rubric and its instructions are taken **verbatim** from the original
judge input, so the v1 arm is the rubric as it actually was. Nine readers in
all, including a model-matched cell in which the *same* model read both
rubrics.

| Cell | rubric | detection | typing |
|---|---|---|---|
| generalist | v1 (marker test) | 0.293 | 0.073 |
| generalist | v2 (structural test) | **0.659** | 0.073 |
| specialist | v1 | 0.341 | 0.073 |
| specialist | v2 | **0.659** | 0.073 |

**Effects:** rubric +0.366 (generalist), +0.317 (specialist); specialisation
+0.049 (v1), +0.000 (v2).
**Mechanism:** the old rubric required a version marker; a regulation does not
write its own version in its text; so it missed **63 of the 82** supersessions
it was asked to find (76.8% of the new rubric's conflicts), calling them
`no_conflict`. The specialist missed 63 of 90 (70%).
**Three qualifications, all owed in the write-up:** (i) the rubric changed the
*definition* of the target as well as the procedure for recognising one, and
this experiment cannot separate the two — what it shows is that the reader
factor is small; (ii) "specialisation" was a brief to a fixed reader model,
not a different capability, so the claim is narrower than "specialists are not
needed"; (iii) the qualitative principle is published — the annotation
guideline is a first-class error source in model annotation — and what is new
is the factor of nine landing on the *reported system measurement*.

### E8 — The per-claim band (described in §3/RO5)

### E9 — The industrial replication of RO5

**Q:** does the band finding replicate on a second corpus?
**D:** the *same generator* that produced the focus corpus's answers, the
shipped prompt, all 247 answerable questions, both evidence protocols.
**Result:** κ 0.062 (gold) and 0.044 (retrieved), both intervals including
zero; bands ordered 0.069 / 0.088 / 0.156 and 0.047 / 0.066 / 0.105; clean
answers 90.4% → 95.4% and 92.7% → 96.7%.
**A methodological note worth knowing before you are asked:** the first
industrial replication used a different generator on 73 claims and was
underpowered; it was re-run properly. The re-run produced *fewer* labelled
claims (the majority consensus is stricter once both readers cover every
claim) and a **weaker** positional result. Reporting the partial run's
p = 0.005 would have been the wrong number.

### E10 — The positional comparison, and why it is evidence and not the finding

The comparison is: keep the first half of each answer, versus keep what the
band tagged `grounded`. On the focus corpus's gold protocol the positional
baseline wins (p = 0.008, d_z = +0.465), and it is not a length artefact —
later claims are *shorter* (Spearman ρ = −0.195, p = 0.0003). But across the
four corpus-and-protocol combinations the positional result is significant in
only **one**: focus gold p = 0.008, focus retrieved p = 0.417, industrial gold
p = 0.083, industrial retrieved p = 0.317.

So the finding is the **agreement-versus-correctness split**, which holds on
all four. The positional comparison is the evidence for that reading. This
distinction is stated explicitly everywhere the comparison appears.

### E11 — The quantity stratum

**Q:** the quantity branch found nothing. Is that because there was nothing to
find?
**D:** an exhaustive, corpus-wide search over 64 measurement terms, grouping
every (measurement term, value) pair in the corpus and keeping the terms whose
values differ across documents. The count is therefore **exact, not sampled**:
**1,776** candidate cross-document quantity conflicts. 119 pairs were put to
the reader; the branch fired on 13.
**Result:** the branch's recall against the 35 construction-labelled limit
changes is **0.000**, and the specialist read **all 13 pairs the branch fired
on, plus 47 it did not**, blind to which was which: 58 `term_mismatch`, 2
`no_conflict`, and **0 `quantity_conflict`**. So the branch's record on this
stratum is 0 true positives and 13 false positives. The search is deliberately
over-inclusive — two passages about different boilers share the word
"pressure" — and the specialist's own account is the mechanism: 39 of the 58
`term_mismatch` calls are the same measurement word naming two different
things.
**Does not say:** that the branch is worthless. It says the corpus contains no
cross-document quantity conflicts of the kind the branch detects, which is a
statement about OSHA's harmonisation, not about the mechanism.

### E12 — The long-context comparison

**Q:** does putting the whole corpus in the prompt beat retrieval?
**D:** the long-context arm reads the entire corpus — **202,529 tokens** on
the focus domain against the RAG arm's accepted context of **1,842** tokens on
average, so **109x** the input per query — priced in dollars, and run under
two prompt conditions differing by one sentence. A retrieval-side proxy shows
the evidence stays locatable even in the whole-corpus ranking: the gold chunk
is in the top 10 of the 735-chunk set for 0.969 of the queries (95% Wilson
0.843–0.994).
**Result:** with the whole corpus in the prompt the generator matched the
pipeline's coverage on the answerable questions but was markedly less
accurate, so on this corpus the whole-corpus prompt does not beat the
retrieval pipeline.
**Does not say:** that it never will. A 2026 study reports long-context
systems ahead of semantic RAG in manufacturing safety; the closest published
analogue favours retrieval (Agri-Query, a 165-page manual, where hybrid RAG
beats direct long context and naive insertion is significantly worse); and
*Length Is Cheap, Competition Is Not* predicts that a whole-corpus prompt
fails through competition among similar values, not through length.

---

## 7. The statistics, and how to talk about them

**Every comparison is paired** — the same queries run through both arms, so
the test is on the per-query differences, not on two independent samples.

| Situation | Test used | Why |
|---|---|---|
| Binary per-query outcome (answered/refused, correct/wrong) | McNemar's exact test | paired, exact, no normality assumption |
| Continuous per-query outcome (recall, faithfulness) | Wilcoxon signed-rank | bounded, left-skewed, mass at 1.0 |
| Proportion with an interval (precision, agreement rate) | Wilson interval | correct at extremes and near 0/1 |
| Agreement between two raters on a skewed categorical label | Cohen's κ | chance-corrected; marginals are skewed |
| Risk–coverage curves, band comparisons | paired cluster bootstrap over **answers** | claims within an answer share evidence and are not independent |

**Rules the thesis follows.** Every *p*-value is accompanied by an effect size
and, for the headline figures, an interval. A *p*-value answers "is it
unlikely"; an effect size answers "is it large"; the difference is material at
*n* = 239. Where a comparison is not significant, the write-up says so rather
than omitting it. Where a *p*-value is very small, it is printed in
scientific notation rather than as 0.000.

**The power discipline.** The positional comparison was re-run with the same
generator and all 247 queries precisely because the first industrial
replication was underpowered. The RO4 comparison was re-run as a factorial
precisely because the first one was confounded. Both re-runs produced
*weaker* headline numbers than the partial versions, and the weaker numbers
are what is reported.

---

## 8. The findings, and which of them are new

| Finding | Published? | What may be claimed | Evidence |
|---|---|---|---|
| **Detection/typing decomposition** | **No** — not published in this pairing | Two metrics instead of one; nine-fold apart; a branch with recall 0.000 where conflict provably exists; a specification | 240 pairs, 84 annotated conflicts, 41 alarms; CIs disjoint on both metrics; exhaustive quantity stratum |
| **Band measures agreement, not correctness** | The filter result is published; the decomposition is not | The band is ordered on the evidence it saw and indistinguishable on an independent reference | 350 + 294/316 claims, four combinations; split holds on all four |
| **Rubric vs specialisation** | The principle is published; the factor of nine is not | The specification of the task moved the measured precision of an unchanged detector by a factor of nine | Factorial, 240 pairs, model-matched cell, non-overlapping CIs |
| **Point-in-time regulatory corpora** | The *method* is published (NitiBench+, ICAIL 2026, TALD); the *purpose* is not | We applied a published corpus-construction method to conflict detection, and the detector that consumed it finds the conflicts and cannot type them | 110 docs / 2,443 chunks / 240 pairs / 35 construction-labelled limit changes / 1,776 quantity candidates |
| **BM25 beats dense on regulatory text** | **Already published**, three times, three jurisdictions | Only the pipeline corollary: the lexical leg carried the pipeline and the fusion and pre-filter added nothing on top of it | 247 queries, Δ −0.081, p = 0.00026; strong for this pipeline, weak as a claim about dense retrieval |

**The one-line version.** Of the five findings: one is a new measurement, one
is a new measurement with a published mechanism around it, one is a sharper
version of a published principle, one is a known method pointed at a new
purpose, and one is already known. **The thesis's spine is the
detection/typing decomposition.**

**A correction applied after the novelty assessment was written.** The
assessment originally judged the industrial replication's non-replication from
the first, underpowered run. After the re-run the numbers changed: one of four
combinations is significant, not zero of four. The verdict stands — the
*filter* result is published and the *ranking* result is the new part — and
the positional comparison is reported as evidence for the
agreement-versus-correctness reading rather than as the finding itself.

---

## 9. Three defects found in this project's own experiments

Reported because the audit discipline is the strongest thing about the work,
and because one of them changed a number already in the deliverables.

1. **The cross-category transfer experiment had no negative class.** The
   unanswerable queries carry no category, so splitting *by category* dropped
   them out of both halves. The shipped result had `n_unanswerable: 0` and
   `unanswerable_refused: NaN` in every split — the experiment was measuring
   only how many true answers get refused. Fixed: the shared negative class
   now goes into both halves. The deliverables were rebuilt and Table 6 now
   carries 0.174 and 0.215 where it had `NaN`.
2. **The per-claim band and the reported claim-support rate are different
   functions of the same evidence** — a noisy-OR against a maximum. They
   disagree on 23 of 350 claims, and the reported 0.382 is a measure of
   entailment presented as a measure of hallucination.
3. **Five numbers in the research write-up itself did not match the result
   files** — a benchmark count off by 25, two audit AUCs, the two reference
   hallucination rates, and two detector profiles that did not exist. All
   corrected. The verification script that found them now lives in the
   repository (`impl/scripts/verify_reported_numbers.py`), not in `/tmp`,
   where a reboot would have destroyed the one artefact the thesis's audit
   discipline rests on.

Also fixed: the per-branch recall in the contradiction evaluation had its
dictionary unpacking reversed and was silently always `None`.

---

## 10. The limitations, stated as the thesis states them

**Internal.** The silver labels are optimistic and mechanically tied to the
chunking, which could inflate the benefit of a retriever that shares the
chunking's biases. The rebuilt unanswerable class is a *near-miss class*:
106 of its questions have a structural twin, but an independent re-check found
questions whose subject the corpus comments on without defining it, so the
refusal rate is measured on a class that is partly answerable in a human's
sense. That bounds what the absolute number means without bounding the arm
comparison, in which every arm is asked the same questions.

**External.** The original corpus is public reference material rather than
proprietary industrial documentation. The second corpus narrows this — it is
authentic, binding and versioned — but it is one jurisdiction, one language,
one regulatory family, and it is regulation rather than a plant's own
procedures.

**Construct.** Retrieval and gating quality are measured, not end-to-end
decision quality; that requires a practitioner study, and the 16-participant
pilot supports a within-subject sign test but not a claim about
generalisation. The conflict mechanism's precision is measured against reader
labels rather than against a proxy. The per-claim band does not certify
correctness. The query-form check does not parse English: it is lexical, so
it misses stems whose malformation is grammatical, and it has no dictionary
or language model, so a keyboard mash passes it. It refuses 37.5% of the
hand-labelled malformed stems (6 of 16, with no false rejections among 13
well-formed stems) and fails open on what it cannot judge — the
conservative direction, since a false rejection would refuse a question the
corpus could have answered.

**Specific to the second corpus.** The labels on the conflict pairs are
model-generated, so the panel's agreement is reported in full but agreement
between readers is not confirmation that a label is right; independent
confirmation would require human annotators. The wording of the annotation
rubric moved the measured precision by a factor of nine, which is a warning
about every model-annotated number in the thesis and not only about that one.

**The scope.** The proposal promised twelve categories spanning industrial
engineering, machine learning and data analytics. The thesis has industrial
engineering (six sub-domains) and industrial regulation (four regimes). The
reconciliation is written up in `research/12_scope_reconciliation.md` with
three options for the supervisor; the recommendation is a scope-reconciliation
table stating plainly what was descoped and why.

---

## 11. The questions a panel will ask

**"What is the contribution?"**
Not the architecture — every component has published prior art, and the thesis
says so. The contribution is a **failure-mode characterisation** (four design
properties that turned out to be wrong, with the measurements), a **metric
contribution** (a conflict detector's precision decomposes into detection and
typing, and they are nine-fold apart), a **methodological contribution** (the
gate evaluated as a selective-prediction policy), and a **benchmark
contribution** (a defect found by auditing the thesis's own benchmark and then
repaired, plus a second corpus whose conflicts are labelled by construction).

**"Isn't 'BM25 beats dense' already known?"**
Yes — three times, in three jurisdictions, and it is deliberately *not* in the
abstract. What is new is the corollary: on this corpus the lexical leg carried
the pipeline and neither the fusion nor the category pre-filter added anything
measurable on top of it (Δ 0.000, p = 1.000 each). And the dense leg here is
a general-purpose 2022 encoder that a domain-adapted one could overtake, so
the result is a boundary condition on this pipeline, not a claim about dense
retrieval.

**"Your annotations are model-generated. Why should we believe them?"**
We should not, and the thesis does not ask us to. The detection/typing
decomposition does not depend on the annotations: against the *construction*
labels, whose conflict types are known without any judgement, detection is
1.000 and typing is 0.000. The model-annotation question is instead handled
by the factorial, which shows the rubric's wording moved the measured
precision by a factor of nine — so the honest statement is that the number
was not yet a measurement of the thing under test. Independent confirmation
would need human annotators, and that is named as the cost.

**"What does the contradiction detector actually do, then?"**
It finds real conflicts — detection precision 0.659 against readers' labels
and 0.897 on the stratum where the conflicts are — and reports them under the
wrong label. It calls supersessions contradictions and cannot say which
version of a superseded provision is in force, because nothing in the
retrieved passages carries the version. A detector for regulatory text
therefore needs version metadata, or must be scoped to detection alone.

**"Is the per-claim band useful?"**
As a filter, yes: keeping only the `grounded` claims raises the share of
answers with no wrong claim from 34.4% to 50.0% on the focus corpus's gold
protocol and from 90.4% to 95.4% on the industrial corpus's. As a ranking, no:
it is at chance against an independent reference on all four corpus-and-
protocol combinations. The useful statement is the decomposition: it measures
whether the retrieved passages entail the claim, not whether the claim is
true.

**"Why two corpora?"**
Because the first cannot support the claims. It is encyclopaedic prose about
industrial engineering: it contains no conflict a practitioner would
recognise as one, and it is not the class of document a practitioner reads.
The second is authentic, binding and versioned, and because regulations are
amended, the same provision read at two dates *is* a conflict with its type
known by construction — which is what made RO4 measurable at all.

**"Which of your results would survive if you had to pick one?"**
The detection/typing decomposition. It is a metric contribution, it is nine
fold apart, and it converts into a specification for anyone building a
conflict detector on regulatory text. It also survives the annotation
criticism, because its sharpest form uses no annotations.

**"What would you do next, with more time?"**
Run the factorial with genuinely different reader models rather than a brief
to a fixed one, since "specialisation" here was a brief rather than a
capability. Obtain human labels for a subsample of the conflict pairs, so the
agreement statistics can be separated from correctness. Carry the industrial
corpus and the six figures into the papers as a structural revision — which
is now done. And extend the corpora beyond one jurisdiction and one language.

**"Why did you rewrite your own hypothesis?"**
Because RO3's hypothesis — that hybrid + RRF + category pre-filter beats flat
retrieval — is contradicted by the thesis's own numbers on both corpora. The
project's rule is that an honest negative is worth more than a favourable
comparison, so the hypothesis was restated as a negative-result hypothesis
rather than the data being explained away.

**"What is the weakest part of the work?"**
The annotation. The rubric factorial showed that the wording of the labelling
instructions moved the headline number by a factor of nine, which means every
model-annotated measurement in the thesis carries that uncertainty. The
detection/typing decomposition survives it because it also has a
label-free form; the band measurement is the one that depends on the readers
most.

---

## 12. What remains open

Nothing below is a loose end. Each item is a measurement that has not been
made, a decision that is not the author's to make, or a limitation that has
been stated rather than concealed. They are listed in the order of how much
they would change the thesis's claims.

### 12.1 Two decisions that are the supervisor's

**The scope.** The proposal promised twelve categories spanning industrial
engineering, machine learning and data analytics. The thesis has industrial
engineering in six sub-domains and industrial regulation in four regimes. The
reconciliation is written up in `research/12_scope_reconciliation.md` with three
options: **(a)** a table stating plainly what was descoped and why, **(b)** an
extension into the machine-learning and data-analytics categories, which needs
a series corpus, series-appropriate metrics and a new benchmark, and would
measure a different system from the one this thesis builds, and **(c)** a
re-reading of the proposal's wording as "industrial sub-domains", which is a
change of wording in place of a change of scope. **The recommendation is (a)**,
and it is the only option that puts the discrepancy on the record before a
panel finds it.

**The conference paper's length.** It is 13 pages against a house budget of
10, raised with the reason recorded in `deliverables/scripts/check_latex.py`.
The paper gained a second corpus's worth of results, six figures, three tables
and fifteen references; the alternative was to cut the clearest new result or
the positioning paragraphs. A 13-page IEEE conference paper is not a
submittable conference paper, and whether that matters is a judgement about
what the paper is for.

### 12.2 The measurement gaps

**This list was written on 11 November 2026. Three of its items were closed
on 12 November, and they are marked below.** `research/16_open_items_register.md`
is the authoritative list; where the two differ, the register is current.

1. **Human confirmation of the conflict labels.** The readers were models.
   Their agreement is reported in full, but agreement between readers is not
   confirmation that a label is right. This is the cost of replacing human
   annotators, and the rubric factorial made it worse rather than better: the
   wording of the labelling instructions moved the measured precision by a
   factor of nine, so the human round has to fix the rubric before it is run,
   not after.
2. **One jurisdiction, one language, one regulatory family.** Nothing here
   shows that the detection/typing decomposition holds for another
   jurisdiction's regulatory language, for a plant's own procedures, or for
   vendor specifications.
3. **"Specialisation" was a brief, not a capability.** The factorial shows
   that a brief plus a sharpened rubric buys nothing over the rubric alone. A
   stronger version needs genuinely different reader models.
4. **The positional comparison did not replicate** on three of the four
   corpus-and-protocol combinations. The band is reported as a filter with a
   measurement decomposition, not as a ranking, and that is a weaker claim
   than the one the focus corpus alone would have supported.
5. **A plant's own revised procedures.** The eCFR corpus supplies the
   conflicts the Wikipedia corpus could not; it does not supply a plant's
   documents, where the same procedure at two revisions would be the same kind
   of conflict with no public versioner to align them.
6. **A second, stronger reranker** in the pool-size factorial. The pool-size
   result is measured; the reranker is not shown not to be the confound.
7. **A token-level faithfulness monitor** in the SYNCHECK style, so the gate
   is compared to a detector rather than only to a prompt.
8. **The long-context answer-quality half** on the six-category corpus. The
   cost half is measured on both corpora and the quality half on the focus
   domain.
9. **The generator-side comparison on a second provider family.** One
   provider behind five arms settles the hypothesis for one family.
10. **A meta-evaluation of the annotation instrument** against human labels,
    so that the model readers' agreement reads as a property of the pairs
    rather than of the models.
11. **The corpus stratified by modality**, with a pre-registered power
    analysis, so the quota objective can be tested with adequate power.
12. **A hand-check of the repaired unanswerable class** against the corpus.
    The audit is no longer a single-corpus result — it has been repeated on
    the industrial corpus — but the part no audit can do is a person reading
    the class against the corpus.

### 12.3 What is *not* open

For the avoidance of doubt, these were open at some point and are closed:

- The contradiction detector could not be evaluated, because the first corpus
  contained no conflicts. **Closed** — the second corpus does, and the
  detector's precision is measured.
- The conflict calibration was fitted on a corpus with no conflicts in it.
  **Closed** — the regulatory profile is fitted and shipped.
- The benchmark's unanswerable class was separable from the question text
  alone. **Closed** — the class was rebuilt and the audit repeated on a
  second corpus.
- The retrieval findings had never been measured on authentic industrial text.
  **Closed** — the negative findings replicate on the second corpus.
- The per-claim band had never been replicated. **Closed** — it replicates on
  the second corpus with the same generator.
- The first comparison of the two rubrics was confounded. **Closed** — the
  2×2 factorial separates them.
- **The answer-accuracy column was a report rather than a measurement** (a
  third convention had never been applied, and the two shipped tests were
  never compared question by question). **Closed 12 November 2026** — the same
  shipped answers were re-scored under five conventions, and the two shipped
  tests turn out to agree at close to chance: opposite verdicts on between
  22% and 73% of the answered questions, Cohen's κ from -0.05 to 0.16. No arm
  comparison on the answer side reaches significance under more than one
  convention, and everything the gate is claimed on is computed from counts
  and from the evidence rather than from the answer string.
  `research/18_answer_validation_conventions.md`.
- **The gate was reported at one retriever's operating point, with the
  frontier as a point.** **Closed 12 November 2026** — the gate was fitted
  separately on three retrievers and the thresholds differ (0.05, 0.10,
  0.05), the operating points move with them, and a transferred threshold is
  too permissive in the direction that flatters the arm it is transferred to.
  `research/19_gate_per_retriever.md`.
- **The soft-prior alternative to the hard category pre-filter** was never
  tried, although the project's own threat list had promised the repair by
  name. **Closed 12 November 2026** — it was tried, at three weights, and it
  does not work: every one of them returns the no-category numbers exactly.
  There was nothing to recover (not one gold chunk on the six-category corpus
  sits outside its question's category), and what the filter does buy is
  ordering, which a prior that only reorders cannot reproduce.
  `research/20_soft_prior.md`.

---

## 13. Where everything lives

**The four deliverables** (`deliverables/`)

| File | What it is |
|---|---|
| `Deliverable_1_Complete_Guide.md/.docx` | the full technical guide, with the results generated from the experiment JSON |
| `Deliverable_2a_Technical_Report.md/.docx` | the technical report |
| `Deliverable_2b_IEEE_Conference_Paper.tex` | the condensed conference version (13 pages) |
| `Deliverable_2c_Journal_Style_Paper.tex` | the journal-style version (30 pages) |
| `Deliverable_3_Department_Report.docx` | the department report |
| `Deliverable_4_Presentation_18Nov.pptx` | the defence deck (21 slides) |
| `figures/` | the six figures, as PDF and PNG |
| `MTP_Full_Explanation.pdf` | this document as a 22-page A4 PDF, monochrome, with a table of contents |
| `MTP_Status_Report.pdf`, `MTP_Technical_Documentation.pdf` | the other two prose reports as PDFs |

**Everything is monochrome.** The deliverables are printed, photocopied and
projected, and none of those is guaranteed to reproduce a hue, so nothing in
them depends on a colour; the hierarchy is carried by weight and by darkness
instead. The build reads every colour back out of the shipped `.docx` and
`.pptx` files and fails if one of them is not a grey.

**The research write-ups** (`research/`)

| File | What it is |
|---|---|
| `00_citation_audit.md` | every citation in the deliverables, resolved against a live registry |
| `03_hybrid_retrieval.md`, `04_contradiction.md` | the design decisions and their literature |
| `07_frontier_2026.md` | the 2026 state of the art, by design move |
| `08_direction_check.md` | the sceptical review that redirected the project |
| `09_encoder_swap.md` | why the dense leg was replaced |
| **`10_industrial_corpus_and_objectives.md`** | **the full write-up of the second corpus, with every number** |
| **`11_supervisor_briefing_2026-11-11.md`** | **the briefing to present** |
| **`12_scope_reconciliation.md`** | **what was descoped relative to the proposal, and the three options** |
| **`13_novelty_and_positioning.md`** | **the novelty check against the published literature** |
| `15_label_validation_protocol.md` | how a generated answer is scored as correct, and what the literature says about the alternatives |
| `14_full_explanation.md` | this document |

**The code**

| Path | What it is |
|---|---|
| `impl/src/` | the framework itself — retrieval, gate, quota, claims |
| `impl/experiments/` | every experiment script |
| `impl/scripts/` | corpus and benchmark builders, the figure script, the verification script |
| `impl/results_focus/`, `impl/results_industrial/` | every result file |
| `impl/data/corpus_industrial/`, `impl/data/benchmark_industrial/` | the second corpus and its benchmark |

**Reproducing anything.** `python3 deliverables/scripts/build_all.py` rebuilds
every deliverable from source and fails if any number, citation, layout or
page budget is wrong. `python3 impl/scripts/verify_reported_numbers.py`
independently re-derives every quoted number from the result files.

---

## 14. A one-page cheat sheet

If you remember nothing else, remember these six sentences.

1. The contribution is a **measurement**, not an architecture: four design
   properties turned out to be wrong, and the paper says so with numbers.
2. A conflict detector's precision is **two numbers**. Detection and typing
   are nine-fold apart, and the mechanism finds the conflicts and reports them
   as the wrong kind.
3. The **rubric**, not the reader's specialisation, moved the measured
   precision — by a factor of nine. A number that moves with its own rubric is
   not yet a measurement.
4. The per-claim band is a **filter, not a ranking**: it measures agreement
   with itself, not correctness.
5. **BM25 over dense is already published**; the new part is that the fusion
   and the pre-filter added nothing on top of it.
6. The **threshold does not transfer** across corpora; the **operating point
   does**. The calibration is a fitted parameter of the deployment.
