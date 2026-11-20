---
title: "The Whole Thesis in Plain Language"
subtitle: "An all-in-one guide to an evidence-grounded retrieval-augmented generation framework for industrial decision support"
author: "Ritik Raj (25IM60R12) — Department of Industrial and Systems Engineering — IIT Kharagpur — Supervisor: Dr. Sri Krishna Kumar"
shorttitle: "Plain-Language Guide"
---

# How to read this guide

This document explains the whole project in ordinary words. It assumes you
have never seen it before. It assumes you do not know what a benchmark, a
recall, a reranker or a confidence gate is, and it explains all of them.

It is long on purpose. Every claim the thesis makes is here, with the number
behind it, in plain English, so that you can check any one of them without
opening a result file.

There are two other documents that cover the same ground. The **Complete
Guide** (`Deliverable_1_Complete_Guide`) is the technical reference: every
term, every formula, every line of code. The **Full Explanation**
(`MTP_Full_Explanation.pdf`) is the panel-facing version of this document, and
it uses the technical register on purpose. This one is the plain-language
version, and it is the one to read first.

**Every number in this document is bound to a result file.** The build
substitutes the measured values into this text at build time, so a number
here cannot drift away from the number the experiment produced. If a token
does not exist, the build stops.

**And every citation is on a list.** This document quotes no literature, so
that it can stay in plain English — but the work it describes is built on
published research, and every paper it leans on is recorded in
`research/00_citation_audit.md` with its identifier checked against a live
registry. The build refuses to ship a document containing a citation that is
not on that list, so "this was made up" is not a failure mode you have to
take on trust.

---

# Part 1 — The problem, in ordinary words

## 1.1 What a working engineer actually does

A working engineer sits down with a pile of paperwork: operating procedures,
control plans, specification sheets, supplier datasheets, standard operating
procedures, failure-mode analyses. A question arrives.

> "What is the maximum jacket temperature for the reactor?"
>
> "How much stock do we hold for part X?"
>
> "Which acceptance criterion applies to this lot?"

Answering it takes four separate skills, and no single search box does all
four:

1. **Finding the right passage.** The answer is in a few thousand passages.
   You need the right one.
2. **Working out which version applies.** Documents get revised. Revision 3
   and revision 4 both sit in the folder. Only one of them is in force today.
3. **Noticing when two documents disagree.** Sometimes two documents give
   different numbers for the same thing. Sometimes they give the same number
   for different things. Sometimes they are about the same rule at two
   different times, and there is no disagreement at all.
4. **Deciding how much to trust what you found.** Some passages answer the
   question. Others are on the same subject but do not answer it. You have to
tell them apart.

## 1.2 What a language model does with that pile

Retrieval-augmented generation (RAG) is the obvious tool for skill number 1.
The system searches the collection, hands the best passages to a language
model, and the model writes an answer. It is very good at this.

It is also usually trusted with all four skills. That is where it goes wrong,
and it goes wrong in a way that matters much more in industry than in a chat
window.

| What goes wrong | What it looks like to the engineer | The name for it |
|---|---|---|
| Answering when the paperwork cannot answer | A confident, specific, wrong number | Hallucination |
| Blending two versions of a rule | A limit that no document ever stated | Version confusion |
| Hiding a disagreement | A clean answer where the source documents contradict each other | Silent conflict resolution |
| Not saying which sentences are supported | Every sentence looks equally trustworthy | No claim-level provenance |

Each of these has published fixes, and each fix has been shown to work on the
benchmarks its authors used. The open question — and the question this thesis
answers — is whether they still work on real industrial text, and whether
anyone has measured the parts that are usually left unmeasured.

## 1.3 What this thesis did about it

The thesis builds a five-mechanism framework for industrial RAG. Then it does
the part that is usually skipped: it measures each mechanism on its own, on
two corpora, with an audited benchmark, and it reports the cases where the
mechanism did not do what it was designed to do.

That last part is the thesis's contribution. Four of the design's assumptions
turned out to be wrong, and the thesis says so, with numbers, in the abstract
and in the results.

The clearest new result is a **measurement** result: a conflict detector's
precision is not one number, it is two, and they are nine-fold apart. The
detector *finds* real conflicts and *reports them under the wrong label*. That
turns into a specification for anyone building a conflict detector on
regulatory text.

## 1.4 The three statements that hold the whole thing up

1. The contribution is stated in **four parts, at four different strengths**,
   and the strongest one is the measurement. The *architecture* is
   **incremental**: every mechanism in the framework has published prior art,
   and the thesis names that prior art rather than claiming priority over it.
   What is yours is the **arrangement** and two of its properties — the gate
   is a fact in the code rather than a sentence in the prompt, so the model
   cannot talk its way past it; and the conflict report is type-aware rather
   than binary.
2. A conflict detector's precision is **two numbers** — detection and typing —
   and they are nine-fold apart.
3. The **rubric**, not the reader's specialisation, moved the measured
   precision, by a factor of nine. A number that moves with the wording of
   its own labelling instructions is not yet a measurement of the thing under
   test.

---

# Part 2 — The words this guide uses

Every term below is used later in this document, so this section comes first.
Each definition is the plainest true one.

## 2.1 The collection and the test

**Corpus.** The collection of documents the system searches. Think of it as
the folder on the engineer's desk.

**Chunk.** A piece of a document. A document is too big to search as one
thing, so it is split into chunks of about 120 words. A table is never split:
a table is one atomic unit, because a specification's meaning lives in the
whole table.

**Benchmark.** A set of questions with known answers, used to score a system.
The system runs the questions, and the answers are compared with the known
ones.

**Gold chunk.** The chunk that contains the answer to a particular question.
"Six out of ten questions had their gold chunk in the top ten results" means
the search found what it was looking for, six times out of ten.

**Answerable and unanswerable.** An answerable question is one the corpus can
answer. An unanswerable question is one it cannot. The second kind is the
hard half, and it is the half that makes a refusal benchmark possible: if
every question had an answer, a system that answered everything would score
perfectly and nothing could be measured.

**Recall@k.** Of the questions whose answer exists somewhere, the fraction for
which the answer came back in the top *k* results. It is the standard way to
ask "did the search find it?"

**MRR and nDCG.** Two ways of also caring about *where* it came back. MRR
(mean reciprocal rank) rewards finding it first. nDCG rewards putting the
good results near the top. Neither is hard to read: higher is better.

**Token.** The unit a language model actually reads and writes. Models do not
see words or characters; they see tokens, which are usually word-pieces.
"Economic order quantity" might be five tokens; "reorder" might be one. This
is why a system's cost is counted in tokens rather than in words, and why the
size of a context — how much a model can hold at once — is measured in them
too.

**Annotation and annotator.** A label put on something by a reader, and the
reader who put it there. When the thesis says the conflict pairs were
"annotated", it means someone decided, for each pair, whether it was a
contradiction, a supersession or neither. The readers here were language
models rather than people, and that is a limitation and not a detail:
agreement between readers shows the instructions were followed consistently, not
that the label is right.

**Regime.** A family of rules from one regulator that share a vocabulary and a
scope. The industrial corpus has four — occupational safety, process safety,
environmental control, and hazardous-materials transport — and each was read
by a reader briefed on that regime alone.

## 2.2 The search machinery

**BM25.** A way of ranking documents by word overlap. It counts how often the
query's words appear, weights rare words higher than common ones, and stops
rewarding a document that repeats a word many times. Its strength is exact
terms: it finds the document that says "asbestos". Its weakness is that it
cannot match a query to a passage that uses *different* words for the same
thing.

**Dense retrieval, or embedding.** Turning a passage and a question into
vectors (lists of numbers) so that "meaning" rather than "wording" is what
gets compared. A passage saying "upper limit for airborne exposure" and a
question about "maximum concentration in air" can land close together. The
encoder here is `BAAI/bge-m3`, a 1024-dimensional
retrieval-trained multilingual encoder.

**Dual encoder and cross-encoder.** Two ways of comparing a question with a
passage.

- A *dual encoder* embeds them separately, then compares the two vectors with
  a dot product. It is cheap. But the question and the passage never see each
  other.
- A *cross-encoder* reads them together, so every word of the passage can
  attend to every word of the question. It is much more accurate and much
  more expensive. So it is used only on a shortlist, never on the whole
  corpus.

**Reranker.** The cross-encoder, used to put the shortlist in a better order.
It can only reorder what it is given. Remember that: it is the single most
important sentence in the retrieval part of this thesis.

**Candidate pool.** The number of candidates handed to the reranker. If the
pool is the same size as the final context, the reranker has nothing to
choose from and can only shuffle.

**Quota, floor and swap.** A quota is a rule about how many chunks of a given
*kind* must be in the final answer. Here the kinds are tables and charts, and
the rule is a **floor**: at least 2 of the 10 chunks must be tables, at least
1 of 10 must be a chart. A floor is enforced by a **swap** — leave the natural
top ten alone, and while the floor is unmet, swap out the lowest-ranked chunk
of the over-full kind for the best-ranked available chunk of the under-full
kind. Calling it a floor rather than a preference is what makes it a quota.

**Reciprocal Rank Fusion (RRF).** A way of combining two ranked lists without
comparing their scores. BM25 scores, cosine similarities and reranker logits
are on completely different scales, so adding them up needs a weighting that
does not travel. RRF instead adds `1/(60 + rank)` over the two lists, so only
the *ranks* matter. The 60 is a smoothing constant (`60`).

**Modality.** Which kind of thing a chunk is: text, a table, or a chart.

## 2.3 Deciding whether to answer

**Confidence gate.** A decision point in the code that either passes the
question on to the language model or refuses it. It is *code*, not an
instruction in the prompt. That matters: a model that is told "refuse if you
are unsure" can talk itself past the instruction, whereas a branch in the
code cannot be talked past. The model is never even called when the gate
refuses.

**Threshold (tau).** The number the gate compares against. A threshold of
0.05 refuses very little; 0.40 refuses a lot. Where the threshold should sit
is a decision about what a wrong answer costs.

**Coverage.** The fraction of all questions the gate chooses to answer.

**Abstention precision.** Of the questions the gate refused, the fraction that
really were unanswerable. If the gate refuses 100 questions and 90 of them
genuinely had no answer, its abstention precision is 0.90.

**Risk and coverage.** Risk is the fraction of the questions the gate *did*
answer that had no answer in the retrieved passages. A **risk-coverage curve**
plots risk against coverage for every threshold, and it is the honest way to
show a gate: no single threshold, the whole trade-off.

**Hallucination.** An answer the model produced that the evidence does not
support. The framework cannot stop a model from writing one — that is what
language models do — so it does something else: it refuses to let an answer
reach the practitioner unless the retrieved passages support it, and it labels
every claim so the reader can see which is which.

**Calibration.** Whether a stated probability means what it says. If the
system says "70% confident" about a hundred questions and 70 of them are
right, it is calibrated. Two numbers measure it: the **Brier score** (the
average squared error of the probability) and the **Expected Calibration
Error** (the average gap between stated confidence and observed accuracy).

## 2.4 Telling documents apart

**Entailment / NLI (natural language inference).** Whether passage A implies
passage B. The model used here says how likely it is that the second passage
is entailed by the first.

**Contradiction and supersession.** This distinction is the spine of the
thesis's new result, so it is worth being exact.

- A **contradiction**: two passages cannot both be true at the same time.
  "The limit is 5 ppm" and "The limit is 25 ppm", same substance, same
  scenario, same date.
- A **supersession**: two passages can both be true, because they describe the
  same rule at two different times. "Revision 3 sets the EOQ at 187 units" and
  "Revision 4 sets the EOQ at 95 units" are both true: revision 4 replaced
  revision 3.

Reporting a supersession as a contradiction is the worst thing this system can
do, because it tells the practitioner the policy is inconsistent when it was
in fact updated.

**Detection precision and typing precision.** Two different questions about
the same set of alarms.

- *Detection*: is the alarm pointing at something real?
- *Typing*: is it the right kind of conflict?

A detector can be excellent at the first and systematically wrong at the
second. That is exactly what happened here.

**Term mismatch.** Two passages use the same word for different things. This
is the commonest false alarm in industrial text, and it is why the
"same subject" check exists.

## 2.5 Marking up the answer

**Atomic claim.** The smallest claim an answer makes. An answer is split into
sentences, and each sentence is split again at words like "however" and
"therefore", so that each claim gets its own label.

**Entailment probability.** For one claim and one retrieved chunk, the
probability that the chunk entails the claim.

**Noisy-OR.** Combining several fallible witnesses. If chunk 1 supports the
claim with probability 0.7 and chunk 2 with 0.5, the claim's overall
support is `1 - (1-0.7)(1-0.5)` = 0.85. The framework takes the *best* chunk
rather than the average, so that one strongly contradicting chunk is not
diluted by many irrelevant ones.

**The three bands.** Every claim is tagged `grounded` (support at least 0.80),
`inferred` (at least 0.45) or `uncertain`. Think of it as a traffic light on
every sentence of the answer.

## 2.6 The statistics

**Wilcoxon signed-rank test.** A test for "is this difference consistently
one way?". The same questions are run through both systems being compared, so
the test is on the per-question differences. It is used instead of the paired
*t*-test because these measurements are bounded and bunched up at 1.0, which
breaks the normality assumption.

**A p-value.** Answers "is this difference unlikely to be chance?" It says
nothing about size.

**An effect size (Cohen's `d`).** Answers "is this difference large?" The
difference matters at `n = 239`.

**A confidence interval.** A range that the true value is probably inside.
A p-value and an interval say different things, and the thesis reports both.

**Cohen's kappa.** How well two raters agree, corrected for the agreement
two raters would get by luck. 1 is perfect agreement, 0 is chance, negative
is worse than chance.

**McNemar's test.** For right-or-wrong answers on the same questions: "did
system A get this right while system B got it wrong, and the other way
round?" It is the right test when the outcome is a yes or a no and both
systems were asked the same thing.

**Bootstrap.** Shuffling the data thousands of times and recomputing the
statistic each time, to see how much the answer moves. If it moves a lot the
measurement is not precise; if it hardly moves, it is. The thesis reports the
interval it produces beside the p-value, because the two say different things:
a p-value says "unlikely to be chance", an interval says "how big, and how
sure".

**A permutation null.** Asking what the measurement would read if the labels
carried no information at all, by shuffling them and recomputing. The
measurement is only meaningful against that: if a shuffled version of the
labels gives 0.50 and the real one gives 0.61, the 0.61 is doing something.

---

# Part 3 — What we built

## 3.1 The pipeline, end to end

```
ingest -> index -> [form check -> category filter -> BM25 + dense -> RRF
                   -> rerank -> GATE -> modality quota] -> claims -> answer
```

Read it left to right. A document is broken into chunks once, offline. Then,
for each question:

1. **Form check.** Refuses a question that is empty, or made only of filler
   words, or that ends in a way no question can end. It runs before anything
   expensive, so a question it refuses costs nothing.
2. **Category filter.** Throws away chunks from categories the question is not
   about.
3. **BM25 and dense retrieval** run independently, each producing a ranking.
4. **RRF** merges the two rankings into one. 4. **The reranker** reorders the top of that list.
5. **The confidence gate** decides whether to answer at all. 5. **The modality quota** adjusts the final context.
6. **The claim splitter and the band** tag the answer sentence by sentence.

Five of those steps are the framework's own mechanisms. Here is each one in
plain terms.

## 3.2 Mechanism 1 — the confidence gate (a bouncer at the door)

**What it is.** A branch in the code. Before the language model is called, a
small logistic model looks at five features of the retrieved material — the
top reranker score, the mean of the top three, the best BM25 score, the best
fusion score, and how many candidates cleared a low relevance bar — and
produces a calibrated probability that the retrieved passages contain the
answer. That probability is compared with a threshold. Above it, the
question goes through. Below it, the system answers "the corpus does not
answer this" and the language model is never invoked.

**Why it is code and not a prompt.** Three things follow that no instruction
can give. The model cannot talk its way past it. The refusal can be
reconstructed exactly ("maximum calibrated relevance probability 0.312
against threshold 0.500"). And it can be moved to a new corpus without
retraining anything.

**The label it predicts, and why it is a query-level label.** The gate does
not ask "is *this candidate* the right one". It asks "does the retrieved
context contain the answer at all". That choice matters more than it looks.
With around fifty candidates per question and one correct answer, a
chunk-level classifier is right about 98% of the time simply by saying "no",
and fitting it against that label produces a model that looks perfectly
calibrated while doing nothing. So the label is set at the query level: 1 when
the context contains the right chunk, whether it was found or missed, because
in both cases the right behaviour is to refuse.

**When to refuse rather than to try harder.** The closest published work
responds to low confidence by gathering more evidence and carrying on, and it
calls the language model in every branch. Refusing outright is better under
one specific condition: the corpus is a closed, controlled set of documents,
and a wrong answer costs more than no answer. That is the industrial case.
Stating the condition precisely *is* the argument.

## 3.3 Mechanism 2 — hybrid retrieval (ask two search engines, then a judge)

**What it is.** BM25 (matching words) and the dense encoder (matching
meaning) each rank the collection. RRF merges the rankings without comparing
their scores. A cross-encoder then reorders the top 50 of the merged list.

**Why two.** They fail differently. BM25 finds "asbestos" when the question
says "asbestos". The dense encoder finds a passage that says "upper limit for
airborne concentration" when the question says "maximum exposure limit". On
regulatory text, this thesis's own measurements show the lexical leg doing
the work and the dense leg adding nothing on top of it — but that is a
finding about *this* corpus and *this* encoder, and it is reported as a
boundary condition rather than a claim about dense retrieval.

## 3.4 Mechanism 3 — the modality quota (make sure the answer has the table in it)

**What it is.** A floor on how much of the final context must be tables
(0.15) and charts (0.05). It is implemented as a swap: leave the natural
top-k alone, and while a floor is unmet, swap out the lowest-ranked chunk of
the over-represented kind for the highest-ranked available chunk of the
under-represented kind.

**Why a swap and not a rebuild.** An earlier implementation walked the
ranking, skipped anything that would breach a floor, and backfilled. That
silently threw away good high-ranked passages and measurably hurt table
recall during development.

**Where it belongs.** This is the mechanism whose position in the pipeline
turned out to matter most. Applied *before* the reranker, it fixes the final
ten before the cross-encoder has a say; the reranker then re-scores those ten
and can reorder them but cannot change *which* ten they are, so the forced
table chunk survives. Applied *after* the reranker, it starts from the
reranked ten and has to swap one of them for a table chunk the cross-encoder
already ranked below the cut — so it tends to import the wrong table chunk and
displace a good one.

**The framework was designed the other way round, and the measurement
inverted it.** The system was built with the *later* placement and kept it
until 16 November 2026, because every measurement in the thesis had been
taken with it and changing it would mean re-running all of them. On that date
it was moved, and everything that depends on it was measured again. On the
focus corpus the later placement costs -0.031 of overall recall
against no quota at all, where the earlier placement gains
+0.031.

## 3.5 Mechanism 4 — the contradiction gate (a smoke alarm for documents)

**What it is.** Two accepted chunks are flagged as conflicting only when two
independent checks agree:

```
flag(A, B) = contradiction(A, B) AND same_subject(A, B)
```

`contradiction` is the entailment probability from the NLI model.
`same_subject` combines embedding similarity (threshold 0.55) with overlap
of concrete identifiers (threshold 0.10). The conjunction matters: raising
the NLI threshold alone only reduces false alarms by throwing away genuine
conflicts, whereas an orthogonal signal lets the two error types be traded
off separately.

Two further pieces matter in industrial text. A **numeric conflict** — two
passages attaching different values to the same quantity — is treated as an
explicit contradiction whatever the NLI model thinks. A
**revision-supersession check** suppresses the alarm when the two passages
carry different revision markers.

Rather than a bare yes/no flag, the mechanism reports a **conflict type**.

## 3.6 Mechanism 5 — per-claim confidence banding (a traffic light on every sentence)

**What it is.** The answer is split into atomic claims. For each claim, the
NLI model gives an entailment probability against every retrieved chunk, and
the chunk probabilities are combined by noisy-OR using the maximum rather
than the mean. The result is cut into `grounded` / `inferred` / `uncertain`,
and each claim carries its band and the identifiers of the passages that
support it. Where the evidence contradicts a claim, the claim is marked
*contradicted* and points at the passage that contradicts it.

**The circularity problem, and why it matters.** The band is computed from the
evidence the retriever returned. If you then check it against a reference
computed from *the same* evidence, the band is being compared with itself,
and high agreement means nothing at all. So the thesis measures the band
against an **independent reference**: a separate judge reading the same
evidence, but deciding whether the claim is *true* rather than whether the
passages entail it.

**Information gain, reported separately.** How much the retrieved set reduced
the uncertainty about the claim, in bits. It is symmetric around 0.5, so a
claim with support 0.9 and one with support 0.1 both yield 0.531 bits. That
is why the band cuts on the support value and the information gain is
reported next to it: the two answer different questions and must not be
conflated.

---

# Part 4 — How we tested it

## 4.1 Three corpora

| | **Focus corpus** | **Multi-category corpus** | **Industrial corpus** |
|---|---|---|---|
| What it is | Wikipedia articles *about* industrial engineering | the same, six categories | US federal regulations |
| Documents | 14 | 46 | 110 |
| Chunks | 735 | 2,383 | 2,443 (2,324 text, 119 table) |
| Categories or regimes | one | six | 4 regulatory regimes |
| Questions | 176 | 276 | 444 |
| Answerable / unanswerable | 32 / 144 | 132 / 144 | 247 / 197 |

The focus corpus is the one the pre-registered measurements live in, so it
carries the headline numbers. It is 88.8% prose (88.8% text, 6.0% table, 5.2% chart), and the numbers on it are
small, which is the point: they are the numbers a critic can check by hand.

The multi-category corpus exists because the transfer study needs more than
one category.

The industrial corpus is the one built to make the conflict objective
measurable at all. It is *authentic* (binding text with numeric requirements:
exposure limits, separation distances, capacities) and it is *versioned*.

**The industrial corpus's four regimes:** OSHA general industry (29 CFR
1910), EPA risk management programmes (40 CFR 112), EPA new source
performance standards (40 CFR 60), and DOT hazardous materials (49 CFR 173).

**Why it is the right artefact.** The US electronic Code of Federal
Regulations serves any regulation as it stood on any past date. The same
section read on **2021-12-31** and **2026-06-01** is the
same rule at two issues. Aligning the two snapshots gives
**361** amended-paragraph pairs, of which
**38.1%** state different numbers in the two vintages.

Such a pair *is* a conflict, and its type is known **by construction**:
nobody has to read it and decide. One artefact therefore does two jobs at
once — it gives the conflict mechanism something to find, and it gives the
measurement labels that need no human judgement.

## 4.2 A defect in the benchmark, and the repair

The unanswerable half of a benchmark is the half on which a refusal
benchmark lives or dies. This one was audited, and it failed.

**What the audit found.** A classifier that saw **only the question text** —
no retrieval, no evidence, no reasoning about the corpus — told the
answerable questions from the unanswerable ones at **ROC AUC 0.999**. The
mechanism was concrete: the class's designated hard case asked about a
fabricated identifier, and every one of those questions carried an identifier
shape that no answerable question carried, so **one regular expression
separated the two classes perfectly**, catching 76.4% of
the unanswerable class with no false positives at all.

If a system's unanswerability is visible in the question, then a system that
refuses on the *shape* of the question scores as well as one that reads the
passages, and the benchmark cannot tell the two apart. On the defective
class the gate refused 91.7% — an upper bound on the refusal rate, not a
measurement of it.

**The repair.** The class was rebuilt as a *corpus-anchored* one: the same
question stems, the same source documents, the same label machinery, and each
repaired question given a **structural twin** in the answerable class — same
stem, same subject size, same shape markers, no word in common
(43 of 110 of 110 have one).

**After the repair.** The shape-only classifier scores 0.608
against a permutation null of 0.468; the one-rule shortcut
carries **0.0%**. On the better-powered multi-category
benchmark the same measurement gives 0.533 against a null of 0.500, which is indistinguishable from chance. At the operating
threshold the gate refuses 23.6% of the corpus-anchored
hard class and 76.5% of the out-of-domain class (the
latter being unanswerable for any system that knows what the corpus is
about).

**The industrial corpus was audited the same way, and it passed.** The
one-rule shortcut catches 0 of 197.
The residual separability is question *length* — median 73 characters for answerable against 50 for unanswerable — which is reported rather than
hidden.

## 4.3 A second defect: two rates wearing the same name

The reported "claim hallucination rate" of 0.382 measures *entailment*, not
hallucination. Two independent estimates bracket it: the shipped rate counts a
claim as hallucinated when the NLI model does not entail it over the
retrieved passages, while the reference rate counts it when an independent
judge, reading the same evidence, does not find the claim supported. The two
are different functions of the same evidence, and they disagree on 23 of 350
claims.

## 4.4 The statistics, and how to talk about them

**Every comparison is paired.** The same questions go through both systems
being compared, so the test is on the per-question differences rather than on
two independent samples.

| The situation | The test used | Why |
|---|---|---|
| A yes/no per-question outcome (answered/refused, correct/wrong) | McNemar's exact test | paired, exact, no normality assumption |
| A continuous per-question outcome (recall, faithfulness) | Wilcoxon signed-rank | bounded, left-skewed, bunched up at 1.0 |
| A proportion with an interval (precision, agreement) | Wilson interval | behaves correctly at the extremes |
| Agreement between two raters on a skewed label set | Cohen's kappa | chance-corrected; the marginals are skewed |
| Risk-coverage curves, band comparisons | paired cluster bootstrap over **answers** | claims inside one answer share evidence and are not independent |

**The rules the thesis follows.** Every p-value is accompanied by an effect
size, and the headline figures also carry an interval. Where a comparison is
not significant, the write-up says so rather than leaving it out. Where a
p-value is very small it is printed in scientific notation rather than as
0.000.

**The power discipline.** Two comparisons in this project were re-run because
the first attempt was underpowered or confounded. Both re-runs produced
*weaker* headline numbers than the partial versions, and the weaker numbers
are what is reported.

---

# Part 5 — What we found

## 5.1 Retrieval: does each piece earn its place?

Seven systems were compared on the same questions. Each one adds one thing.

- **A** — BM25 alone
- **B** — the dense encoder alone
- **C** — hybrid (the two fused with RRF)
- **D** — plus the cross-encoder reranker
- **E** — plus the category filter
- **F** — plus the quota, applied before the reranker
- **G** — plus the quota, applied after the reranker

### Focus corpus (n = 32 answerable over 735 chunks)

| System | Recall@5 | Recall@10 | Recall@20 | MRR | nDCG@10 | Table recall@10 |
|---|---|---|---|---|---|---|
| A. BM25 only | 0.969 | 0.969 | 1.000 | 0.736 | 0.792 | 1.000 |
| B. Dense only | 0.781 | 0.812 | 0.875 | 0.652 | 0.688 | 0.875 |
| C. Hybrid (RRF) | 0.969 | **1.000** | 1.000 | 0.798 | 0.847 | 1.000 |
| D. + cross-encoder | 0.906 | 0.969 | 1.000 | 0.795 | 0.836 | 1.000 |
| E. + category filter | 0.906 | 0.969 | 1.000 | 0.795 | 0.836 | 1.000 |
| F. + quota (pre-rerank) | 0.969 | **1.000** | 1.000 | 0.819 | 0.864 | 1.000 |
| G. + quota (post-rerank) | 0.906 | 0.938 | 0.938 | 0.789 | 0.826 | 1.000 |

**Reading it.**

- Fusion beats the dense leg by +0.188 (p = 1.4 × 10⁻²) but beats its own
  lexical leg by only +0.031, which is not statistically significant.
- The cross-encoder **lowers** recall@10 from 1.000 to 0.969
  (-0.031, p = 3.2 × 10⁻¹). The reason is the subject of the next
  section: the fusion had already found the right chunk every time, so a
  pool of fifty gave the reranker room to pick a *different* ten — and it
  picked worse 3.1% of the time.
- The category filter changes nothing, and there is a reason for that which
  is in Part 6.
- The quota *before* the reranker recovers what the reranker lost, taking
  recall@10 from 0.969 to 1.000 against the no-quota baseline of 0.969.
  The quota *after* it lands at 0.938, which is 3.1
  points below that same baseline.

**What this does not say.** It does not say the reranker is useless. It moves
MRR and nDCG, and on the industrial corpus, with a 50-candidate pool, it
**helps**: +0.028 (p = 0.01963,
n = 247).

### The industrial corpus, where the reranker earns its place

| | Recall@10 |
|---|---|
| BM25 alone | 0.9595 |
| Dense alone | 0.8785 |
| Fused | 0.9595 |
| + reranker | 0.9879 |
| + quota (pre-rerank) | 0.9798 |

**BM25 beats the dense encoder** by -0.081
(p = 0.00026, n = 247) — three times the
effect size and twenty-five times the significance of the focus corpus's
result. **This is already published**, three times, in three jurisdictions, so
it is not in the abstract and is reported only as a boundary condition on this
pipeline. What is new is the corollary: the fusion
(+0.000, p = 1.00000) and the
category pre-filter (+0.000,
p = 1.00000) added nothing on top of it.

## 5.2 The candidate pool: how big should the reranker's shortlist be?

**The claim.** A reranker can only reorder what it is given. If the pool is
the same size as the final context, it cannot improve recall at all — it can
only shuffle. So there must be a point where enlarging the pool stops
paying.

**Focus corpus.** The curve saturates at a pool of 10, where
recall@10 = recall@20 = 1.000, and then falls slightly as the reranker is
handed more distractors to reorder. Because it saturates, the focus corpus
**cannot distinguish** "the pool stopped helping" from "the corpus had
nothing left to find". That is a limitation of the corpus, not a finding.

**Industrial corpus.** The curve is sharp. At a pool of 50,
recall@20 = 1.000 while recall@10 = 0.988 —
so **1.21%** of the correct answers are retrieved and
then pushed straight back out of the ten-chunk context by the reranker's own
ordering.

![Figure 1. Recall against the size of the rerank candidate pool, on the focus corpus (black circles, 32 answerable of 176 queries) and the industrial corpus (grey squares, 247 of 444). The focus curve saturates at a pool of 10, where Recall@10 = Recall@20 = 1.000, and then falls slightly as the reranker is given more candidates to reorder. The industrial curve does not saturate at 10: there Recall@20 reaches 1.000 at a pool of 50 while Recall@10 stays at 0.988, so 1.21 points of gold are retrieved and then pushed out of the ten-chunk context.](figures/fig1_pool_size.pdf)

**What this does not say.** It does not say a bigger pool is always better.
The measured trade is: enlarging the pool buys recall the context cannot
hold.

## 5.3 The gate: what does refusing cost, and what does it buy?

The gate was swept over every threshold, and for each one the whole
risk-coverage curve was recorded.

| | Focus corpus | Industrial corpus |
|---|---|---|
| Operating threshold (tau) | 0.05 | 0.40 |
| Coverage (fraction of all questions answered) | 0.693 | 0.691 |
| Abstention precision | 0.963 | 0.847 |
| Expected calibration error | 0.104 | 0.075 |
| Brier score | 0.151 | 0.159 |
| Answerable questions answered | 93.8% | 91.5% |
| Unanswerable questions refused | 36.1% | 58.9% |

![Figure 2. Risk-coverage of the confidence gate: the risk that an answered query has no answer in its context, against the fraction of queries the gate answers, on the held-out evaluation half (focus n = 71, industrial n = 178). The degenerate policies bound the curve: always answering carries the base rate of the negative class as its risk at full coverage, and always refusing removes the risk at the cost of all coverage. The industrial gate trades risk for coverage; the focus gate buys almost nothing over answering everything. The fitted operating points (tau = 0.05 focus, tau = 0.40 industrial) answer 0.693 and 0.691 of all queries respectively.](figures/fig2_risk_coverage.pdf)

![Figure 3. Reliability of the gate's calibrated probability against observed answerability, on the held-out evaluation half (focus n = 71, industrial n = 178); the upper panel plots observed answerability against mean predicted probability per bin and the lower panel the number of queries in each bin. The industrial gate tracks the diagonal (ECE 0.075, Brier 0.159); the focus gate does not (ECE 0.1044, Brier 0.1510): it puts most of its queries in the lowest confidence bin, where few of them have an answer in context.](figures/fig3_calibration.pdf)

**The result that matters.** The **threshold does not transfer** from one
corpus to the other (0.05 here, 0.40 there). The
**operating point does** (coverage 0.693 against
0.691). In other words: the calibration is a fitted parameter
of the deployment, not a constant of the architecture. You have to re-fit it
wherever you deploy.

**What this does not say.** It does not say the gate certifies its own
confidence. The published conformal guarantees rest on an exchangeability
assumption that a single-category industrial corpus violates.

## 5.4 The modality quota: a trade, not a gain

![Figure 4. Overall Recall@10 against table-specific Recall@10 for the seven ablated systems, focus corpus (black circles, n = 32 answerable: 24 text, 8 table) and industrial corpus (grey squares, n = 247: 117 text, 130 table). The modality quota does not move both axes: on the industrial corpus the pre-rerank quota buys 0.8 points of table recall and gives up 0.8 points of overall recall, and the post-rerank quota lands on exactly the no-quota operating point; on the focus corpus the post-rerank quota gives up 3.1 points of overall recall while table recall stays at 1.000. The quota is a trade, not a gain, and which way it trades depends on where it is applied.](figures/fig4_modality_quota_pareto.pdf)

The quota does not move both axes at once. On the industrial corpus, the
pre-rerank quota buys 0.8 points of table recall and gives up 0.8 points of
overall recall, and the post-rerank quota lands on exactly the no-quota
operating point. On the focus corpus the post-rerank quota gives up 3.1 points of overall recall against the no-quota
configuration, while table recall stays at 1.000. Which way it trades
depends on where it is applied, and **the system applies the quota
before the cross-encoder**.

**The deeper reason, and it is a finding.** The corpus's modality composition
decides whether a modality-aware mechanism can have any effect at all. The
focus corpus is 88.8% prose, 6.0% tables and 5.2% charts. There is very little for a table quota to select. A
mechanism can be correct and still have nothing to do.

## 5.5 Contradictions: the detector finds them and mislabels them

**The setup.** 240 pairs of passages (90 where a
paragraph was amended, 150 that were merely
retrieval neighbours) were read by four domain specialists plus a generalist
control, blind to the detector. The pairs were mined by the **retriever's**
own signal and never by the detector's rule — a pool selected on the
detector's decision would have contained every alarm by construction, and
could not have measured the detector's precision.

**The labels the readers agreed on:** 84
supersessions, 90 term mismatches, 64 with no conflict.

**The result.**

| | Value |
|---|---|
| Detection precision — is there something real there | **0.659** (95% CI 0.505–0.784) |
| … on the stratum where the conflicts actually are | **0.897** |
| Typing precision — is it the right kind of conflict | **0.073** (95% CI 0.025–0.194) |
| Against the labels that need no human judgement | detection **1.000**, typing **0.000** |
| Under the shipped operations vocabulary | detection 0.650, typing 0.000 |

![Figure 6. The contradiction detector's precision against the base rate of real conflicts in the same population, with 95% Wilson intervals; a filled marker means the point estimate clears the framework's 0.5 calibration floor and the branch would act, a hollow one means it does not and the findings would be withheld. The focus corpus's semantic branch has a precision of 0.0 (0 of 20 alarms confirmed by either annotator) on a base rate of 0.0, so it is withheld; the industrial semantic branch reaches 0.65 (26 of 40) against a base rate of 0.35 and would act.](figures/fig6_contradiction_precision.pdf)

**The two numbers are nine-fold apart, and the gap is the finding.** The
mechanism *finds* the conflicts and *reports them as the wrong kind*. It calls
supersessions contradictions, and it cannot say which version of a superseded
provision is in force, because nothing in the retrieved passages carries the
version.

**Why the second row matters.** The first row was measured against labels
that human readers produced, and a panel will rightly ask whether those
labels are right. The second row does not use them at all: in the revision
corpus, a paragraph and its amended self are known to be a supersession
without anyone reading them. Against those labels, detection is 1.000 and typing is 0.000. **The typing failure does not depend on any
annotation at all.**

**The quantity branch found nothing, and that is also a result.** An
exhaustive search over 64 measurement terms found 1776 candidate cross-document quantity conflicts — the
count is exact, not sampled. 119 pairs were put to a reader,
and the branch fired on 13. A specialist read all 13 pairs the branch fired on, plus 47 it did not, blind to
which was which: 58 term mismatches, 2 with no conflict, and **zero**
quantity conflicts. So on this stratum the branch's record is 0 true positives
and 13 false positives.

**What this does not say.** It does not say the branch is worthless. It says
the corpus contains no cross-document quantity conflicts of the kind the
branch detects, which is a statement about OSHA's harmonisation (it aligned
its construction and general-industry limits, so the same substance carries
the same limit in both), not about the mechanism.

**The specification that comes out of this.** A detector for regulatory text
needs version metadata, or must be scoped to detection alone.

## 5.6 The per-claim band: agreement with itself, not correctness

The band was measured against an independent reference — a separate judge
reading the same evidence, but deciding whether the claim is *true* rather
than whether the passages entail it.

| | Gold evidence ("is the claim right?") | Retrieved evidence ("does a reader agree with the scorer?") |
|---|---|---|
| Band against the independent reference (kappa) | **0.049** (CI -0.026 to 0.124) | 0.069 |
| Error in the `grounded` / `inferred` / `uncertain` band | 0.542 / 0.513 / 0.610 | 0.118 / 0.103 / 0.220 |
| Answers containing no wrong claim | 34.4% | 59.4% |
| … keeping only the `grounded` claims | **50.0%** | 81.2% |

**Replicated on the industrial corpus**, with the same generator:
kappa 0.055 (gold) and 0.017
(retrieved), both intervals including zero; bands ordered 0.077 / 0.119 / 0.139; clean answers 91.1% → 94.9%.

**What this means, plainly.** The band is **at chance against correctness**.
Against the evidence it saw, its three bands are correctly ordered. So:

- As a **filter**, it works. Keeping only the `grounded` claims raises the
  share of answers containing no wrong claim from 34.4% to   50.0% on the focus corpus, and from   91.1% to 94.9% on the
  industrial one.
- As a **ranking**, it does not. It cannot be used to say "the best claim in
  this answer is claim 7".

**The comparison that is evidence rather than finding.** The obvious rival is
positional: keep the first half of each answer. On the focus corpus's gold
protocol the positional baseline wins (p = 0.008,
d = +0.465), and it is not a length artefact — later claims
are actually shorter. But across the four corpus-and-protocol combinations,
the positional result is significant in only one. **What replicates is the
direction, not the significance**: keeping the first claims of an answer
carries a higher risk than keeping the band's `grounded` claims in **three of the four**
measurements (+0.0923,
+0.0231 on the focus corpus and
+0.0152,
+0.0000 on the industrial one, all at matched
coverage) — and only the largest of those four clears significance. So the
finding is the **agreement-versus-correctness split**, which holds on all
four. The positional comparison is the evidence for that reading, not the
finding itself.

## 5.7 What about just putting the whole corpus in the prompt?

A fair question, and the obvious alternative to retrieval.

**The design.** The long-context arm reads the entire corpus —
202,529 tokens — against the pipeline's accepted context of 2,246 tokens on average, so **90 times** the input per
question, priced in dollars, and run under two prompt conditions that differ
by a single sentence.

**The result.** With the whole corpus in the prompt the generator matched the
pipeline's coverage on the answerable questions but was markedly less
accurate. On coverage and on cost the result is settled: the whole-corpus
prompt declines no more unanswerable questions than the pipeline does, and
costs far more to do it. On answer quality the margin is directional but not
statistically significant once the answers are scored without the length
confound.

**A check that the evidence stayed findable.** A retrieval-side proxy shows
the gold chunk sits in the top 10 of the 735-chunk set for 0.969 of the queries (95% Wilson 0.843-0.994), with a median rank of 1. So the
failure is not that the evidence became unreachable.

**What this does not say.** It does not say long context never wins. A 2026
study reports long-context systems ahead of semantic RAG in manufacturing
safety; the closest published analogue favours retrieval (a 165-page manual,
where hybrid RAG beats direct long context); and the paper *"Length Is Cheap,
Competition Is Not"* predicts that a whole-corpus prompt fails through
competition among similar values, not through length.

## 5.8 The benchmark audit, as a picture

![Figure 5. A classifier that sees only the question text, with no retrieval, no evidence and no corpus, telling an answerable question from an unanswerable one. Before the repair the two classes were separable almost perfectly on the focus corpus (ROC AUC 0.999, against a permutation null of 0.455 +/- 0.072), and one regular expression for a fabricated identifier caught 76.4% of the unanswerable questions with no false positive at all. After the repair the shortcut catches nothing, and what is left of the procedure's power is small but not zero: AUC 0.608 on the focus corpus (p = 0.050) and AUC 0.708 on the industrial corpus (p = 0.010). On the better-powered six-category corpus it is indistinguishable from chance: AUC 0.533 (p = 0.267). The benchmark's unanswerable class is decidable from the evidence rather than from a question-shape rule, but on two of the three corpora it is not free of form-only separability.](figures/fig5_question_only_roc.pdf)

This is the audit of §4.2 as a graph. Before the repair, the two classes were
almost perfectly separable from the question text alone. After the repair,
the one-rule shortcut catches nothing and the procedure's residual power is
small but not zero: AUC 0.608 on the focus corpus (p = 0.050) and 0.708 on the industrial corpus (p = 0.010). On the better-powered six-category corpus it is
indistinguishable from chance: AUC 0.533 (p = 0.267).

---

# Part 6 — Four things we got wrong

These are the thesis's most useful results, and each one is a design
assumption that turned out to be false.

## 6.1 A reranker cannot improve recall if its pool is the same size as the context

**What we assumed.** That adding a cross-encoder to the pipeline would help.

**What happened.** On the focus corpus it *lowered* recall@10 from
1.000 to 0.969. That looked like an anomaly — a reranker making things
worse is a strange result to report.

**What it actually is.** Not an anomaly, and not a defect of the reranker.
The fusion had already found the right chunk every time on this corpus —
without the cross-encoder, recall@10 was 1.000 — so the only thing the
cross-encoder could do was pick a *different* ten out of the fifty it was
shown, and 3.1% of the time it picked worse. Give it a pool of exactly ten
and it would have had nothing to choose from: it could only shuffle. The
candidate-pool sweep (§5.2) measures both, and the industrial corpus shows
the other side of the trade: there the fusion is *not* already perfect, so
the extra candidates are worth having — with a pool of fifty the same
reranker **helps**, +0.028 — and every gold chunk
is inside the top twenty.

**Why it matters.** It is a lesson about experimental design, not about
rerankers: a component measured inside a degenerate configuration looks
useless, and the configuration, not the component, was the problem. And the
pool size is a genuine trade — a bigger pool lets the reranker recover chunks
the first stage missed, and lets it drop chunks the first stage found — so
where the first stage is already perfect, a bigger pool can only cost.

## 6.2 The modality quota belongs before the reranker, not after — on the corpora we measured

**What we assumed.** That the quota should be applied late, after the
reranker, so that it could swap out the chunks the reranker liked least and
degrade the context as little as possible.

**What happened.** Applied late, it starts from the reranked ten and has to
swap one of them for a table chunk the cross-encoder already ranked below the
cut — so it tends to import the wrong table chunk and displace a good one.
Applied early instead, it fixes the final ten before the cross-encoder has a
say; the cross-encoder can reorder those ten but cannot change which ten they
are, so the forced table chunk survives.

**And the direction is not the same on every corpus.** Applied early, the quota
is the better placement on the focus domain and on the six-category corpus.
On the industrial corpus the order reverses: applied late, it is the better
placement there, by a small margin. The difference is small everywhere and
never statistically significant, so the honest summary is not "the quota always
belongs before the cross-encoder" but "it belongs before it on the corpora this
thesis measures it on, and its direction depends on the corpus".

**Why it matters.** It is a general principle about constraint placement: a
constraint on a downstream artefact should be enforced where it can still
choose the candidates, not where it must work against another component's
judgement.

## 6.3 The corpus's composition decides whether a modality-aware mechanism can have any effect at all

**What we assumed.** That a table quota would improve table retrieval.

**What happened.** It depends entirely on what is in the corpus. A corpus that
is 88.8% prose has very little for a table quota to select. A
mechanism can be correct and still have nothing to do.

**Why it matters.** Before measuring a modality-aware mechanism, measure the
modality mix first.

## 6.4 The category pre-filter does nothing

**What we assumed.** That filtering candidates to the question's category
would cut down the search space and improve precision.

**What happened.** On the focus corpus it is a no-op, because the corpus *is*
one category. On the industrial corpus it costs nothing and gains nothing
(+0.000, p = 1.00000).

**Why it matters.** A component can be harmless and still be dead weight.
The thesis also notes the repair it never tried: a *soft prior* on the
category, rather than a hard filter, was proposed and never measured, so the
pre-filter's cost is known and its proposed replacement is not.

---

# Part 7 — Four defects we found in our own work

These are reported because the audit discipline is the strongest thing about
the project, and because one of them changed a number that was already in the
deliverables.

1. **The cross-category transfer experiment had no negative class.** The
   unanswerable questions carry no category, so splitting by category dropped
   them out of both halves. The shipped result had `n_unanswerable: 0` and
   `unanswerable_refused: NaN` in every split — the experiment was measuring
   only how many true answers get refused. Fixed: the shared negative class
   now goes into both halves, the deliverables were rebuilt, and the table
   carries real numbers where it had `NaN`.

2. **The per-claim band and the reported claim-support rate are different
   functions of the same evidence** — a noisy-OR against a maximum. They
   disagree on 23 of 350 claims, and the reported 0.382 is a measure of
   entailment presented as a measure of hallucination (§4.3).

3. **Five numbers in the research write-up itself did not match the result
   files** — a benchmark count off by 25, two audit AUCs, the two reference
   hallucination rates, and two detector profiles that did not exist. All
   corrected. The verification script that found them now lives in the
   repository, not in a temporary directory, where a reboot would have
   destroyed the one artefact the audit discipline rests on.

4. **The per-branch recall in the contradiction evaluation had its dictionary
   unpacked the wrong way round** and was silently always `None`.

---

# Part 8 — What is new, and what is already published

| Finding | Already published? | What may be claimed |
|---|---|---|
| **Detection and typing are two numbers** | **No** — not published in this pairing | Two metrics instead of one; nine-fold apart; a branch with recall 0.000 where conflict provably exists; a specification |
| **The band measures agreement, not correctness** | The filter result is published; the decomposition is not | The band is ordered on the evidence it saw, and indistinguishable on an independent reference |
| **Rubric versus specialisation** | The principle is published; the factor of nine is not | The specification of the task moved the measured precision of an unchanged detector by a factor of nine |
| **Point-in-time regulatory corpora** | The *method* is published; the *purpose* is not | A published corpus-construction method applied to conflict detection, and the detector that consumed it finds the conflicts and cannot type them |
| **BM25 beats a dense encoder on regulatory text** | **Already published**, three times, three jurisdictions | Only the pipeline corollary: the lexical leg carried the pipeline, and the fusion and the pre-filter added nothing on top of it |

**The one-line version.** Of the five findings: one is a new measurement, one
is a new measurement with a published mechanism around it, one is a sharper
version of a published principle, one is a known method pointed at a new
purpose, and one is already known. **The thesis's spine is the
detection/typing decomposition.**

**The rubric result, which is the humbling one.** A 2x2 experiment over the
labelling rubric and the reader's domain specialisation, with everything else
held constant, showed that the rubric's wording moved the measured precision
by **+0.366** and **+0.317**, while the reader's specialisation moved it by
**+0.049** and **+0.000**. The mechanism is concrete: the old rubric required
a version marker in the text, and a regulation does not write its own version
in its text, so it missed **63 of the 82** supersessions it was asked to find,
calling them `no_conflict`.

A number that moves by a factor of nine with the wording of its own rubric is
not yet a measurement of the thing under test. That is a warning about every
model-annotated number in the thesis, not only about that one.

**Three qualifications, all owed.** (i) The rubric changed the *definition*
of the target as well as the procedure for recognising one, and the
experiment cannot separate the two — what it shows is that the reader factor
is small. (ii) "Specialisation" here was a brief to a fixed reader model, not
a different capability, so the claim is narrower than "specialists are not
needed". (iii) The qualitative principle is published — the annotation
guideline is a first-class error source in model annotation — and what is new
is the factor of nine landing on the *reported system measurement*.

---

# Part 9 — What this work cannot claim

**Internal.** The silver labels are optimistic and mechanically tied to the
chunking, which could inflate the benefit of a retriever that shares the
chunking's biases. The rebuilt unanswerable class is a *near-miss class*: 43 of 110 of its questions have a structural twin, but an
independent re-check found questions whose subject the corpus comments on
without defining it, so the refusal rate is measured on a class that is
partly answerable in a human's sense. That bounds what the absolute number
means, without bounding the arm comparison, in which every arm is asked the
same questions.

**External.** The original corpus is public reference material rather than
proprietary industrial documentation. The second corpus narrows this — it is
authentic, binding and versioned — but it is one jurisdiction, one language,
one regulatory family, and it is regulation rather than a plant's own
procedures.

**Construct.** Retrieval and gating quality are measured, not end-to-end
decision quality; that would need a practitioner study, and the
16-participant pilot supports a within-subject sign test but not a claim
about generalisation. The conflict mechanism's precision is measured against
reader labels rather than against a proxy. The per-claim band does not
certify correctness. The query-form check does not parse English: it is
lexical, so it misses stems whose malformation is grammatical, and it has no
dictionary or language model, so a keyboard mash passes it. It refuses 37.5% of the hand-labelled malformed stems with no false
rejections among the well-formed ones, and it fails open on what it cannot
judge — the conservative direction, since a false rejection would refuse a
question the corpus could have answered.

**Specific to the second corpus.** The labels on the conflict pairs are
model-generated, so the panel's agreement is reported in full, but agreement
between readers is not confirmation that a label is right. The wording of the
annotation rubric moved the measured precision by a factor of nine, which is
a warning about every model-annotated number in the thesis.

**The scope.** The proposal promised twelve categories spanning industrial
engineering, machine learning and data analytics. The thesis has industrial
engineering (six sub-domains) and industrial regulation (four regimes). The
reconciliation is written up with three options for the supervisor, and the
recommendation is a scope-reconciliation table stating plainly what was
descoped and why.

---

# Part 10 — What is still open

Nothing below is a loose end. Each item is a measurement that has not been
made, a decision that is not the author's to make, or a limitation that has
been stated rather than concealed. They are listed in the order of how much
they would change the thesis's claims.

## 10.1 One decision that is the supervisor's

**The conference paper's length.** It is 13 pages against a house budget of
10, raised with the reason recorded. The paper gained a second corpus's worth
of results, six figures, three tables and fifteen references; the alternative
was to cut the clearest new result or the positioning paragraphs. A 13-page
IEEE conference paper is not a submittable conference paper, and whether that
matters is a judgement about what the paper is for.

## 10.2 The measurement gaps

1. **Human confirmation of the conflict labels.** The readers were models.
   Their agreement is reported in full, but agreement between readers is not
   confirmation that a label is right. The rubric factorial made this worse
   rather than better, so the human round has to fix the rubric before it is
   run, not after.
2. **One jurisdiction, one language, one regulatory family.** Nothing here
   shows that the detection/typing decomposition holds for another
   jurisdiction's regulatory language, for a plant's own procedures, or for
   vendor specifications.
3. **"Specialisation" was a brief, not a capability.** The factorial shows
   that a brief plus a sharpened rubric buys nothing over the rubric alone. A
   stronger version needs genuinely different reader models.
4. **A plant's own revised procedures.** The eCFR corpus supplies the
   conflicts the Wikipedia corpus could not; it does not supply a plant's
   documents, where the same procedure at two revisions would be the same kind
   of conflict with no public versioner to align them.
5. **A second, stronger reranker** in the pool-size factorial. The pool-size
   result is measured; the reranker is not shown not to be the confound.
6. **A token-level faithfulness monitor** in the SYNCHECK style, so the gate
   is compared to a detector rather than only to a prompt.
7. **The long-context answer-quality half** on the six-category corpus. The
   cost half is measured on both corpora and the quality half on the focus
   domain.
8. **The generator-side comparison on a second provider family.** One
   provider behind five arms settles the hypothesis for one family.
9. **A meta-evaluation of the annotation instrument** against human labels,
   so that the model readers' agreement reads as a property of the pairs
   rather than of the models.
10. **The corpus stratified by modality**, with a pre-registered power
    analysis, so the quota objective can be tested with adequate power.
11. **A hand-check of the repaired unanswerable class** against the corpus.
    The part no audit can do is a person reading the class against the
    corpus.

## 10.3 What is *not* open

For the avoidance of doubt, these were open at some point and are closed:

- The contradiction detector could not be evaluated, because the first corpus
  contained no conflicts. **Closed** — the second corpus does, and the
  detector's precision is measured.
- The conflict calibration was fitted on a corpus with no conflicts in it.
  **Closed** — the regulatory profile is fitted and shipped.
- The benchmark's unanswerable class was separable from the question text
  alone. **Closed** — the class was rebuilt and the audit repeated on a
  second corpus.
- The retrieval findings had never been measured on authentic industrial
  text. **Closed** — the negative findings replicate on the second corpus.
- The per-claim band had never been replicated. **Closed** — it replicates on
  the second corpus with the same generator.
- The first comparison of the two rubrics was confounded. **Closed** — the
  2x2 factorial separates them.
- **The answer-accuracy column was a report rather than a measurement,**
  because the two shipped tests disagree about which arm is best and no third
  convention had been applied. **Closed 12 November 2026** — the same shipped
  answers were re-scored under five conventions: the two shipped ones, plus
  SQuAD 2.0's normalised exact match and token-level F1 and PopQA's
  containment rule. The two shipped tests turn out to agree at close to
  chance — they give opposite verdicts on between 19% and   67% of the answered questions, with Cohen's κ from   0.00 to 0.21 — and the four binary conventions
  span up to 0.90 on one arm's answers. So the accuracy column is
  reported as a comparison between arms and never as a level. What that
  settles is that **no arm comparison on the answer side reaches significance
  under more than one convention**, and that everything the gate is claimed on
  — the coverage, the cost, the refusal, the claim-support figures and every
  retrieval measurement — is computed from counts and from the evidence rather
  than from the answer string, so it is identical under all five. See §E.8.1
  and `research/18_answer_validation_conventions.md`.
- **The gate's operating point was reported for one retriever only**, and the
  frontier as a point rather than a curve. **Closed 12 November 2026** — the
  gate was fitted separately on three retrievers, and the thresholds differ:   0.05 on the shipped hybrid, 0.10 on the lexical leg
  alone, 0.05 on the dense leg alone. The operating points move
  with them — the hybrid's gate refuses 0.361 of the
  unanswerable questions, the lexical gate 0.611, the dense gate   0.660 — and applying the shipped threshold unchanged to the
  lexical leg turns out to be **too permissive, and in the direction that
  flatters the arm it is transferred to**. Each retriever's full threshold
  sweep and risk–coverage curve is now reported, so the frontier is a curve.
  See `research/19_gate_per_retriever.md`.
- **The soft-prior alternative to the hard category pre-filter** was never
  tried. **Closed 12 November 2026** — it was tried, at three weights, and it
  does not work: every one of them returns the no-category numbers exactly
  (MRR 0.7764 against the hard filter's 0.8025, paired
  Wilcoxon p = 0.0272). There was nothing to recover in the first
  place — the filter's recall cost on the six-category corpus is exactly zero,
  because not one gold chunk sits outside its question's category — and what
  the filter does buy is ordering, which a prior that only reorders cannot
  reproduce. See `research/20_soft_prior.md`.
- **The positional comparison's non-replication** was listed as an open
  measurement gap. **Closed 12 November 2026, and revised on 16 November
  2026** — the direction was uniform then, and the register's wording had
  conflated it with the significance. After the re-measurement under the new
  quota placement, the direction replicates in three of the four and ties in one. What varies is the
  magnitude, and only the largest of the four clears significance. So the band
  is reported as a filter and not as a ranking because position beats it
  wherever the comparison has the power to show it, not because the
  comparison disagreed. The residual — the magnitude, and the power it needs — is the
  next-steps list's third item.
- **The proposal's scope was an open decision**, with three options and a
  recommendation. **Closed 12 November 2026** — option (a) was taken, and it
  is the one that puts the discrepancy on the record rather than leaving a
  panel to find it. The reconciliation table is in the Complete Guide's §A.6
  and in `research/12_scope_reconciliation.md`, and the thesis now carries it
  as limitation L19. The other two options are not rejected: the extension
  into the machine-learning categories is the honest next measurement and
  belongs in the next-steps list, where it already is.
- **The industrial corpus's unanswerable half was never put through the two
  probes** the focus corpus's was: the question-only policy and the
  parametric-leakage probe were both recorded as `not_run`, because no
  credential was reachable at the time. **Closed 12 November 2026** — both
  were run. The question-only policy separates the two classes at an AUC of   0.478 — no discrimination at all, worse than a coin toss —
  and it refuses 70.9% of the answerable class to do it, so
  it is not usable as an abstention rule. And asked with no corpus at all, the
  generator answers substantively 0.959 of the unanswerable
  questions against 0.955 of the answerable ones, with
  the closed-book answers to the answerable questions right only   0.138 of the time under the entailment test. The
  unanswerable class is therefore not made of questions the model happens to
  know. See `research/21_industrial_probes.md`.

---

# Part 11 — Questions a panel will ask

**"What is the contribution?"**
Not the architecture alone. The contribution is **four parts, at four
strengths**, and it is worth saying all four out loud, because a panel that
hears only the first will think you have nothing.

1. **Architectural — incremental, and treated as such.** Every component has
   published prior art, and the thesis says so. What is yours is the
   arrangement and two of its properties: the gate is a control-flow fact
   rather than an instruction, and the conflict report is type-aware rather
   than binary.
2. **Empirical — a failure-mode characterisation.** Four design properties
   that turned out to be wrong, with the measurements.
3. **Metric** — a conflict detector's precision decomposes into detection and
   typing, and they are nine-fold apart.
4. **Methodological** — the gate evaluated as a selective-prediction policy,
   and a benchmark contribution: a defect found by auditing the thesis's own
   benchmark and then repaired, plus a second corpus whose conflicts are
   labelled by construction.

The architecture is the weakest of the four, and it is placed last in the
paper on purpose. The *system's* value does not depend on any part of it being
new. It depends on each piece being structural, on the trade-offs between
them being measured rather than assumed, and on the system being able to say,
for every claim, which passage supports it.

**"Isn't 'BM25 beats dense' already known?"**
Yes — three times, in three jurisdictions, and it is deliberately not in the
abstract. What is new is the corollary: on this corpus the lexical leg
carried the pipeline and neither the fusion nor the category pre-filter added
anything measurable on top of it. And the dense leg here is a general-purpose
2022 encoder that a domain-adapted one could overtake, so the result is a
boundary condition on this pipeline, not a claim about dense retrieval.

**"Your annotations are model-generated. Why should we believe them?"**
We should not, and the thesis does not ask us to. The detection/typing
decomposition does not depend on the annotations: against the construction
labels, whose conflict types are known without any judgement, detection is 1.000 and typing is 0.000. The model-annotation question is handled by
the factorial, which shows the rubric's wording moved the measured precision
by a factor of nine — so the honest statement is that the number was not yet
a measurement of the thing under test. Independent confirmation would need
human annotators, and that is named as the cost.

**"Your answer-accuracy numbers depend on how you score the answer. Isn't that
fragile?"**
Yes, and it is measured rather than left to be discovered. The two tests the
thesis reports turn out to agree at close to chance: question by question
they give opposite verdicts on between 19% and 67% of the answered questions, with Cohen's κ between 0.00 and 0.21. Re-scored on the *same* answers under
five conventions — the two shipped ones, plus SQuAD 2.0's normalised exact
match and token-level F1 and PopQA's containment rule — the four binary ones
span up to 0.90 on one arm's answers. So the accuracy column is
reported as a comparison between arms and never as a level.

Two things follow, and they are the useful ones. First, **no arm comparison
on the answer side reaches significance under more than one convention** — the
gate-against-no-gate comparison reaches 0 of 5 conventions in the cautious condition and 0 of 5 in the answering one. The
gate's claim was never that it makes answers more accurate; it is that it
refuses what should be refused at a cost, and those numbers are computed from
counts and from the evidence, not from the answer string, so they are
identical under all five conventions. Second, what the measurement does *not*
settle is which convention is right — none of the five is right, and that
needs human annotation of the benchmark's own gold answers, which is named as
the largest open item in the thesis.

**"What does the contradiction detector actually do, then?"**
It finds real conflicts — detection precision 0.659 against
readers' labels, and 0.897 on the stratum where the
conflicts are — and reports them under the wrong label. It calls
supersessions contradictions and cannot say which version of a superseded
provision is in force, because nothing in the retrieved passages carries the
version. A detector for regulatory text therefore needs version metadata, or
must be scoped to detection alone.

**"Is the per-claim band useful?"**
As a filter, yes: keeping only the `grounded` claims raises the share of
answers with no wrong claim from 34.4% to 50.0% on the focus corpus, and from 91.1% to 94.9% on the
industrial one. As a ranking, no: it is at chance against an independent
reference on all four corpus-and-protocol combinations. The useful statement
is the decomposition: it measures whether the retrieved passages entail the
claim, not whether the claim is true.

**"Why two corpora?"**
Because the first cannot support the claims. It is encyclopaedic prose about
industrial engineering: it contains no conflict a practitioner would recognise
as one, and it is not the class of document a practitioner reads. The second
is authentic, binding and versioned, and because regulations are amended, the
same provision read at two dates *is* a conflict with its type known by
construction — which is what made the conflict objective measurable at all.

**"Which of your results would survive if you had to pick one?"**
The detection/typing decomposition. It is a metric contribution, it is
nine-fold apart, and it converts into a specification for anyone building a
conflict detector on regulatory text. It also survives the annotation
criticism, because its sharpest form uses no annotations.

**"What would you do next, with more time?"**
Run the factorial with genuinely different reader models rather than a brief
to a fixed one. Obtain human labels for a subsample of the conflict pairs, so
the agreement statistics can be separated from correctness. Extend the corpora
beyond one jurisdiction and one language.

**"Why did you rewrite your own hypothesis?"**
Because the hypothesis that hybrid retrieval plus the category pre-filter
beats flat retrieval is contradicted by the thesis's own numbers on both
corpora. The project's rule is that an honest negative is worth more than a
favourable comparison, so the hypothesis was restated as a negative-result
hypothesis rather than the data being explained away.

**"What is the weakest part of the work?"**
The annotation. The rubric factorial showed that the wording of the labelling
instructions moved the headline number by a factor of nine, which means every
model-annotated measurement in the thesis carries that uncertainty. The
detection/typing decomposition survives it because it also has a label-free
form; the band measurement is the one that depends on the readers most.

---

# Part 12 — The one-page cheat sheet

If you remember nothing else, remember these seven sentences.

1. The contribution is **four parts, at four strengths**, and the strongest is
   the measurement. The *architecture* is incremental — every mechanism has
   published prior art, and what is yours is the arrangement plus two of its
   properties. Then: four design properties turned out to be wrong, a conflict
   detector's precision is two numbers, and your own benchmark was audited,
   found defective, repaired, and re-measured.
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
6. The **threshold does not transfer** — not across corpora, and not across
   retrievers either: three retrievers wanted three thresholds. The
   **operating point does** transfer. The calibration is a fitted parameter of
   the deployment.
7. **Your own benchmark is the thing to audit first.** The unanswerable half
   of it was separable from the question text alone; it was rebuilt, and
   everything was measured again.

---

# Part 13 — Where everything lives, and how to rebuild it

**The deliverables** (`deliverables/`)

| File | What it is |
|---|---|
| `Deliverable_1_Complete_Guide.md/.docx/.pdf` | the full technical guide, with the results generated from the experiment JSON |
| `Deliverable_2a_Technical_Report.md/.docx/.pdf` | the technical report |
| `Deliverable_2b_IEEE_Conference_Paper.tex` | the condensed conference version |
| `Deliverable_2c_Journal_Style_Paper.tex` | the journal-style version |
| `Deliverable_3_Department_Report.docx/.pdf` | the department report |
| `Deliverable_4_Presentation_18Nov.pptx` | the defence deck |
| `MTP_Plain_Language_Guide.md/.docx/.pdf` | this document |
| `MTP_Full_Explanation.pdf` | the same ground in the technical register |
| `MTP_Status_Report.pdf`, `MTP_Technical_Documentation.pdf` | the two prose reports |
| `figures/` | the six figures, as PDF and PNG |

**Everything is monochrome.** The deliverables are printed, photocopied and
projected, and none of those is guaranteed to reproduce a hue, so nothing in
them depends on a colour; the hierarchy is carried by weight and darkness
instead. The build reads every colour back out of the shipped `.docx` and
`.pptx` files and every pixel out of the six figures, and fails if one of
them is not a grey.

**The research write-ups** (`research/`)

| File | What it is |
|---|---|
| `00_citation_audit.md` | every citation in the deliverables, resolved against a live registry |
| `03_hybrid_retrieval.md`, `04_contradiction.md` | the design decisions and their literature |
| `07_frontier_2026.md` | the 2026 state of the art, by design move |
| `08_direction_check.md` | the sceptical review that redirected the project |
| `09_encoder_swap.md` | why the dense leg was replaced |
| `10_industrial_corpus_and_objectives.md` | the full write-up of the second corpus, with every number |
| `11_supervisor_briefing_2026-11-11.md` | the briefing to present |
| `12_scope_reconciliation.md` | what was descoped relative to the proposal, and the three options |
| `13_novelty_and_positioning.md` | the novelty check against the published literature |
| `14_full_explanation.md` | the same ground in the technical register |
| `15_label_validation_protocol.md` | how a generated answer is scored as correct, and what the literature says about the alternatives |
| `16_open_items_register.md` | every limitation and every gap in one list, with an owner and what closing it would take |
| `17_historical_figures.md` | the numbers in the prose that no result file backs, and the one that was wrong |
| `18_answer_validation_conventions.md` | five scoring conventions applied to the same shipped answers: how much of the answer-accuracy column is the convention rather than the system |
| `19_gate_per_retriever.md` | the gate fitted on three retrievers, the frontier as a curve, and what a transferred threshold costs |
| `20_soft_prior.md` | the soft prior against the hard category pre-filter: the repair that was promised and does not work |

**The code**

| Path | What it is |
|---|---|
| `impl/src/` | the framework itself: retrieval, gate, quota, claims |
| `impl/experiments/` | every experiment script |
| `impl/scripts/` | corpus and benchmark builders, the figure script, the verification script |
| `impl/results_focus/`, `impl/results_industrial/` | every result file |
| `impl/data/corpus_industrial/`, `impl/data/benchmark_industrial/` | the second corpus and its benchmark |

**How big it is.** 14 source modules, 4,823
lines, 34 experiments, 26 runner scripts, 32 unit tests across 4 test files.

**Reproducing anything.** `python3 deliverables/scripts/build_all.py` rebuilds
every deliverable from source and fails if any number, citation, layout or
page budget is wrong. `python3 impl/scripts/verify_reported_numbers.py`
independently re-derives every quoted number from the result files.

**What is reproducible, and what is not.** the retrieval-side experiment scripts are deterministic given the seeds, while the generator-side comparison is not, because the generator's sampling temperature is provider-determined rather than seed-controlled; its five arms are therefore compared on rates over a fixed question set rather than on paired per-question outcomes
