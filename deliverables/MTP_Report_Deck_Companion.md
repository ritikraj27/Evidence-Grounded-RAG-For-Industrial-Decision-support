---
title: "The Report Deck, Explained"
subtitle: "Every formula, every term and every measurement behind the 38-slide report deck"
author: "Ritik Raj (25IM60R12), Department of Industrial and Systems Engineering, IIT Kharagpur"
date: ""
shorttitle: "The report deck, explained"
---
# How to use this companion

This document explains the 38-slide report deck, slide by slide. It is
written to be read beside the deck, not instead of it: the deck is what the
audience sees, and this is what makes the deck legible to you.

**What is in it.** Four parts. Part A is the vocabulary, every term the deck
uses in plain words with the slide it appears on. Part B is the formulas:
the four written on the slides, and the set of quantities the deck's tables
rest on, each with every symbol named and the caveat that comes with it.
Part C is the slides and the six measured figures, in order. Part D is the
protocol behind the numbers: the splits, the benchmark and its repairs, the
five arms, the statistics, the objectives, the prior art, and the boundary
of what is claimed.

**How to use it before you present.** Read Part A once, quickly, so that no
word on a slide is unfamiliar. Then read Part B for slides 7, 8, 9 and 20,
which carry the formulas, and skim the rest. Part C is the slide-by-slide
version of what the speaker notes say, with the measurement behind each
slide added. Part D is the one to read on the morning of the presentation if
a question goes somewhere the deck does not reach.

**The pictures.** Each slide is printed above its explanation, and each
measured figure is printed where it is explained. The slide pictures are
drawn from the deck file itself, so they show the shape of the slide exactly
as it is, with one caveat: they are drawn by this project's own renderer
rather than screenshotted from PowerPoint, so a word may sit a fraction
differently in the picture than it will on the screen. The layout, the
tables, the figures and the numbers are the same.

**What this document does not do.** It does not replace the report. The
report carries the derivations, the citations, the full literature review,
the appendix-free text and the numbers behind every row of the findings
table. Where this document says a number, that number is the one on the
slide; where the report says more, this document says where to look.

**A note on the two decks.** This deck is the section-wise report deck: it
walks the report from end to end and reads as a document. The shorter
ten-minute deck is the one sized to a spoken slot. They say the same things
about the same measurements, and this companion explains the one it is
attached to. Where a slide here has no counterpart in the shorter deck, it
is because this deck carries the report's argument in full: the objectives,
the prior art, the per-claim assessment, and the slide that separates what
was measured from what was not.

# Part A. The terms

Every term the deck uses, in plain words, with the slide it appears on. The
deck can be read in twenty minutes and the terms can be looked up here.
Nothing in this part is a claim; it is the vocabulary.

## A.1 The machinery

RAG (retrieval-augmented generation)
:   A generator that is given text to answer from, instead of answering from
    what it memorised. **Slide 2.** The phrase that matters is "in front of".
    A gate that sits after generation is a filter on output; a gate that sits
    before it is a decision about whether to spend a model call at all.

Corpus
:   The set of documents the system is allowed to read. **Slides 2, 10.** The
    corpus in this work is a public substitute for the department's
    proprietary supply chain corpus, and the report says so wherever it
    matters.

Chunk
:   A piece of a document, of a size a retriever can return and a generator
    can read. **Slide 10.**

Retrieval
:   Finding the chunks that might contain the answer. **Slide 7.** The
    framework uses two retrieval methods at once, which is what "hybrid"
    means.

Lexical retrieval, and BM25
:   Retrieval by word overlap. BM25 is the standard scoring function for it:
    a term's inverse document frequency, times a saturated frequency factor.
    **Slide 7.** The full formula is in Part B of the ten-minute companion;
    here it is enough to know that a rare word in the query counts for more
    than a common one, and that a chunk does not win by being long.

Dense retrieval
:   Retrieval by meaning. Each chunk and each query is turned into a vector of
    numbers, and the chunks whose vectors point in the same direction as the
    query's are returned. **Slide 7.** It reads well and, on this corpus, it
    was measurably worse than BM25. That is why the encoder was replaced.

Embedding
:   The vector a chunk or a query is turned into. The encoder used here is
    BAAI/bge-m3, which produces 1024-dimensional vectors that are L2
    normalised, so their length is fixed and only their direction carries
    information. **Slide 7.**

Dense leg, lexical leg
:   The two halves of hybrid retrieval: the BM25 half and the embedding
    half. **Slide 7.** "Leg" is used because the two are run in parallel and
    then joined.

Fusion
:   Joining the two ranked lists into one list. **Slide 7.** The method used
    is reciprocal rank fusion, which needs no score calibration between the
    two legs, only their ranks.

RRF (reciprocal rank fusion)
:   A fusion rule: a chunk's fused score is the sum, over the lists it
    appears in, of one divided by a constant plus its rank in that list. A
    chunk missing from a list contributes nothing. **Slide 7.** The formula
    is in Part B.

Reranker, cross-encoder
:   A model that reads the query and a chunk together and scores how well
    they answer each other. It is more accurate than a bi-encoder, which
    scores them separately, and much slower, so it runs on the shortlist
    rather than the whole corpus. **Slides 6, 15.**

Modality quota
:   A floor on how many chunks of a non-text kind (a table, a chart) must be
    in the final context. **Slides 6, 18, 19.** A floor, not a ceiling: it
    puts a lower bound on tables and charts and no upper bound on text.

Floor, and relaxation
:   The quota is a minimum, and when the candidate pool cannot supply it the
    minimum is relaxed rather than invented. **Slide 6.** A floor that
    silently becomes a ceiling is a different mechanism wearing the same
    name.

Category pre-filter
:   A check that removes chunks from categories the question cannot be about,
    applied to both legs before fusion. **Slides 6, 7.** One of three
    invariants: things that are asserted in the code rather than assumed.

Invariant
:   A property the code asserts about itself, which a test can check. **Slide
    7.** Three are asserted here, and three real defects were found by
    asserting them, none of which was visible in the output.

Confidence gate
:   The component that decides whether the retrieved evidence actually
    contains the answer, before the generator is called. **Slides 6, 8.** It
    is the mechanism the report is about.

Posterior
:   The gate's calibrated estimate that the answer is in the context. It is a
    probability, not a score, and the distinction is what makes a threshold
    on it meaningful. **Slide 8.**

Feature vector
:   The five numbers the gate reads about the whole retrieved pool. **Slide
    8.** The gate is query level: the features describe the query's pool as a
    whole, not any one chunk.

Platt scaling
:   Fitting a logistic model on top of an existing score so that its output
    is a probability. **Slide 8.** The weights are fitted by maximum
    likelihood on a calibration split.

Maximum likelihood
:   The standard way of fitting a model: choose the parameters that make the
    observed data most probable under the model. **Slide 8.**

Calibration split
:   The part of the data the gate's weights are fitted on. **Slide 8.** Here
    60 percent of the queries. The other 40 percent is the evaluation half,
    and the calibration numbers are reported on the evaluation half, not on
    the split they were fitted on.

Standardisation
:   Subtracting the mean and dividing by the standard deviation of each
    feature, so that no feature dominates the logistic model purely by being
    measured on a larger scale. **Slide 8.**

Threshold, and operating point
:   The cut-off on the posterior, and the particular cut-off the gate is run
    at. **Slides 8, 20.** The operating point here is tau = 0.05, and it was
    chosen by a stated rule rather than by taste.

Abstention, refusal
:   The gate declining to answer, so the generator is never called. **Slide
    6.** "Abstention" and "refusal" are the same thing here.

Answer-in-context detectability
:   The positive class of the gate: the answer is in the context. It is
    defined operationally as the gold chunk being present in the reranked
    candidate pool. **Slide 8.** The report does not call this "sufficiency",
    because the literature reserves that word for a set-level property that
    is not what is being measured.

Gold chunk
:   The chunk the benchmark says contains the answer. **Slides 8, 32.** It is
    the target of retrieval and the reference for everything else.

Contradiction gate
:   A second component that refuses, this time when two retrieved chunks
    contradict each other. **Slide 9.** It needs two independent branches to
    agree before it alarms.

NLI (natural language inference)
:   A model that is given two statements and judges whether they contradict.
    **Slide 9.** This one is used at a threshold of 0.70.

Shared instance
:   The requirement that two chunks talk about the same thing: the same
    substance, the same part, the same regulation. **Slide 9.** It is the
    detail that stops the detector from being a topic detector.

Form validator
:   A runtime check that a query is shaped like a question before anything
    else happens. **Slides 6, 31.** It refused 25 of 25 hand-authored
    malformed queries and 0 of 35 well-formed ones, at 2.6 microseconds per
    query.

Malformed stem
:   A query that is not shaped like a question, such as a bare fragment.
    **Slide 31.** The form validator's job.

Counterfactual
:   What would have happened under a different choice that was available and
    was not taken. **Slide 31.** The memorable one: the benchmark builder's
    own question-generation rule, used as a runtime check, would have refused
    100.0 percent of hand-labelled well-formed questions.

False rejection rate
:   The share of good inputs a filter wrongly turns away. **Slide 31.** It is
    the number that decides whether a filter is safe to ship.

Claim
:   One assertion in a generated answer. **Slides 6, 32.** Every claim is
    scored against the evidence it was shown.

Per-claim evidence tag
:   The chunk that supports a claim, attached to that claim. **Slide 5.** It
    is the mechanism that turns an answer into something a reader can check.

Entailment
:   A statement being supported by the evidence, as judged by an NLI model.
    **Slides 25, 32.** A claim counts as supported when a chunk entails it at
    a threshold of 0.5, or when the evidence states it literally.

Grounded, inferred, uncertain claim
:   Three bands a claim is put in by its confidence score. **Slide 32.** 0.80
    separates a grounded claim from 0.45 for an inferred one, and anything
    below is uncertain.

Non-bypassability
:   The property that the generator cannot be reached without passing the
    gate. **Slide 6.** Here it is a property of the code, not a convention
    the caller is trusted to follow: the generator is injected into the
    framework and called at exactly one line.

Comparison arm
:   A version of the system run without part of it, so that the part can be
    measured. **Slides 6, 22.** The arms are named in Part D.

## A.2 The measurements

Recall@k
:   The share of the queries for which the right chunk appears in the top k
    results. **Slides 15, 17.** It says whether the answer was found, and
    nothing about where it was placed.

MRR (mean reciprocal rank)
:   The average, over the queries, of one divided by the rank of the right
    chunk. **Slides 15, 16, 17.** It says how high up the answer was, so a
    system that finds the answer but buries it loses on MRR and ties on
    recall.

nDCG (normalised discounted cumulative gain)
:   A ranking measure that rewards the right chunk being high, and
    normalises against the best possible ordering. **Slide 15.** It is the
    third retrieval number here because it is the one that notices a
    reordering that recall cannot.

DCG (discounted cumulative gain)
:   The sum of each result's relevance divided by the log of its position, so
    that a relevant result further down counts for less. **Slide 15.** The
    logarithm is the discount.

IDCG
:   The DCG of the best possible ordering of the same results. **Slide 15.**
    nDCG is DCG divided by this, which is what makes it comparable across
    queries with different numbers of relevant results.

Inverse document frequency (IDF)
:   How rare a term is across the corpus, on a logarithmic scale. **Slide 7.**
    A term in every document carries no information and scores zero rather
    than a negative number.

Base rate
:   The share of the data in the positive class before anything is predicted.
    **Slide 8.** The gate's positive class has a base rate of 0.182, so a
    model that always answered "no" would be right 81.8 percent of the time.

Calibration
:   Whether a stated probability matches the observed frequency of the
    outcome. **Slides 20, 21.** A model can rank well and be badly
    calibrated.

ECE (expected calibration error)
:   The average, over the probability bins, of the gap between the mean
    predicted probability in the bin and the observed frequency in that bin,
    weighted by how many queries are in it. **Slides 20, 21.** Zero is
    perfect calibration.

Brier score
:   The mean squared difference between a stated probability and the outcome.
    **Slide 20.** Lower is better, and it punishes confident mistakes harder
    than vague ones.

Reliability diagram
:   A plot of observed frequency against predicted probability, with the
    diagonal as the target. **Slide 21.** A model that tracks the diagonal
    is calibrated.

Held-out evaluation half
:   The part of the data that was not used to fit anything. **Slide 21.**
    Every calibration number in the deck is measured there.

Abstention precision
:   Of the queries the gate refused, the share that genuinely had no answer.
    **Slides 20, 24.** This is the number a practitioner needs, and it is
    the one the report's central claim rests on.

Coverage
:   The share of queries the system answers rather than refuses. **Slide
    20.** Every extra refusal is paid for in coverage.

Risk-coverage curve
:   The trade between how many queries are answered and how often an answered
    query has no answer in its context. **Slide 21.** The threshold sweep in
    the deck is the same curve in table form.

Frontier
:   The set of points a system can reach, and the boundary of it. **Slide
    21.** The report shows the whole frontier rather than one point on it.

ROC AUC
:   The area under the curve of true positive rate against false positive
    rate, over every possible threshold. **Slides 12, 14, 36.** 0.5 is a
    coin flip, 1.0 is perfect separation.

Shortcut
:   A feature that predicts the label without the thing the benchmark is
    supposed to test. **Slides 12, 14.** Here a single regular expression
    separated the two classes, which is why the headline refusal rate was
    reporting the benchmark rather than the framework.

Stratum
:   A subpopulation the results are broken down into. **Slides 13, 34.** Two
    strata matter: the hard stratum, where the corpus discusses the subject
    but does not state the answer, and the out-of-domain stratum, where the
    question comes from outside the corpus entirely.

Out-of-domain
:   A question about something the corpus does not cover at all. **Slide
    13.** It is the easier half of the unanswerable class, and the gate does
    better on it.

Structural twin
:   A question built to look like the other class in every respect except the
    one that matters. **Slide 11.** Every repaired unanswerable question was
    given a twin in the answerable class, so a shortcut that keys on shape
    cannot separate them.

Corpus-anchored
:   A class defined by what the corpus contains rather than by how a question
    is written. **Slide 11.** It is the repair that made the unanswerable
    class hard.

Precision of a detector
:   Of the times a detector fires, the share of times it is right. **Slides
    28, 29.** A detector that fires rarely has a wide interval on its
    precision, and 0 out of 20 alarms is a null with an upper bound of 16.1
    percent, not a statement that the detector can never be right.

95 percent upper bound
:   The largest value the true quantity could plausibly be, at 95 percent
    confidence, given what was observed. **Slides 28, 29.** It is how a null
    is reported without pretending to know more than the data allows.

Wilson score interval
:   The interval used for a proportion when the count is small. **Slide 29.**
    It stays sensible at 0 out of 20, where the naive interval does not.

Base rate of real conflicts
:   How often two retrieved chunks of this corpus actually contradict each
    other. **Slide 29.** A detector's precision means nothing without it.

Paired test
:   A test that compares two systems on the same items, so that the item's
    own difficulty cancels out. **Slide 15.** Every comparison in the deck is
    paired, because the arms answer the same questions.

Wilcoxon signed-rank test
:   The paired test used for the retrieval comparisons. **Slide 15.** It uses
    the rank of the differences rather than their size, so one wild
    difference cannot dominate.

McNemar test
:   The paired test for two outcomes, used for the generation comparisons.
    **Slides 23, 25.** It counts the questions where the two systems
    disagreed, and only those.

b and c
:   In McNemar's table, b is the number of questions the baseline answered
    and the arm refused, and c is the number where the baseline refused and
    the arm answered. **Slide 23.** Only b and c matter, and the test asks
    whether the disagreement is lopsided.

p-value
:   The probability of seeing a result at least this extreme if the null
    hypothesis were true. **Slide 15.** It is not the probability that the
    null hypothesis is true.

Null result
:   A result that establishes no difference. **Slides 18, 28.** The report
    reads a null as no difference established here, and reports nulls with
    their interval widths rather than dropping them.

Effect size
:   How large a difference is, as opposed to whether it is distinguishable
    from zero. **Slide 15.** A difference can be significant and trivial.

Random control
:   An arm that refuses the same number of questions as the gate, but picks
    them at random. **Slides 22, 24.** Without it, refusing on a coin flip
    and refusing on a calibrated score look identical.

Selection effect
:   Comparing two systems on the subset each of them answered, which is not
    the same set of questions. **Slide 25.** It is why per-answer accuracy
    cannot be compared across arms with different coverage.

Per-answer accuracy
:   The share of the answers that were right, among the questions that were
    answered at all. **Slide 25.** It is a coverage-dependent quantity, and
    the gated arm's answers are easier by construction.

Length-controlled re-scoring
:   Scoring the same answers again with the length taken out of the
    comparison. **Slide 26.** It is how the quality half of the long-context
    comparison is made fair.

Cached pricing
:   A provider's lower rate for input tokens already seen in an earlier
    request. **Slide 26.** 33.0 percent of the long-context arm's tokens were
    cache reads, which is why the money ratio and the token ratio differ so
    much.

## A.3 The experimental vocabulary

Prompt condition
:   The instruction the generator is given. **Slides 22, 23.** Two are used,
    differing by a single sentence: under one the generator may decline,
    under the other it must answer.

Empty completion
:   The generator returning no text at all. **Slide 30.** It is neither an
    answer nor a refusal, and it is recorded as a third outcome.

Arm
:   One version of the pipeline in a comparison. **Slide 22.** Five of them,
    listed in Part D.

Fit, transfer, and the fitted operating point
:   Fitting the gate's threshold on one half of one corpus and applying it
    unchanged to another. **Slide 33.** It is the transfer arm, and it is how
    the report shows a calibrated threshold does not travel.

Concept-level prose, instance records
:   The two kinds of text a contradiction detector needs. **Slide 28.** An
    instance record states a value for a particular thing; concept-level prose
    discusses a topic. Only the first contains the phenomenon.

Research objective (RO)
:   One of the four things the project set out to do. **Slide 4.** RO1 build
    the framework, RO2 make retrieval modality-balanced and category-aware,
    RO3 test the framework's own hypothesis about hallucination, RO4
    characterise the failure modes.

Prior art
:   The published work the framework draws on. **Slide 5.** Every mechanism in
    this framework is published; the contribution is putting them together
    into one industrial system and measuring the whole thing end to end.

# Part B. The formulas

Four formulas are written on the slides of this deck: the fusion rule, the
posterior, the decision rule and the contradiction gate. They are given
first. The rest of this part is the set of quantities the deck's tables rest
on, which it names but does not write out: the retrieval metrics, the
calibration measures, the refusal rates and the three tests.

Two conventions worth stating once. An indicator function $\mathbf{1}[\cdot]$
is 1 when the condition inside the brackets is true and 0 when it is false.
$\mathbb{E}[\cdot]$ means the average of a quantity over a set.

## B.1 Reciprocal rank fusion

*Slide 7. Written on the slide.*

$$
S_{RRF}(d)=\sum_{r\in\mathcal{R}}\frac{1}{k_{RRF}+\mathrm{rank}_r(d)},
\qquad k_{RRF}=60
$$

| Symbol | What it is | Value or form here |
|---|---|---|
| $S_{RRF}(d)$ | the fused score of chunk $d$ | higher is better |
| $\mathcal{R}$ | the ranked lists being fused | the BM25 list and the dense list |
| $\mathrm{rank}_r(d)$ | where $d$ sits in list $r$ | 1 for the best |
| $k_{RRF}$ | the smoothing constant | 60 |
| $d$ | a chunk | any candidate |

**In plain words.** For every list a chunk appears in, take one divided by
its rank in that list plus 60, and add these up. A chunk that two lists both
rank highly beats a chunk that one list ranks first and the other does not
mention. A chunk missing from a list contributes nothing at all.

**Why this and not adding the scores.** Because BM25 scores and cosine
similarities are on different scales. Comparing them directly would require
calibrating one against the other, which is fragile. Ranks need no
calibration: only the ordering matters, and the ordering is the thing each
leg is actually good at.

**Why 60.** The constant stops the top result from dominating. At rank 1 the
contribution is $1/61$; at rank 10 it is $1/70$. The ratio between them is
small, so a chunk that appears twice at moderate rank can beat a chunk that
appears once at the top. That is the behaviour wanted: agreement between two
retrieval methods is evidence.

**The caveat.** Fusion does not create information. On this corpus the dense
leg was measurably worse than BM25, and fusing a strong leg with a weak one
recovers the loss but does not turn it into a win over the strong leg alone.
Slide 15 says this in those words.

## B.2 The calibrated posterior

*Slide 8. Written on the slide.*

$$
p_{conf}(q)=\sigma\left(\beta_0+\beta_1^{T}
\frac{\phi(q)-\mu}{\sigma}\right),
\qquad \sigma(z)=\frac{1}{1+e^{-z}}
$$

| Symbol | What it is | Value or form here |
|---|---|---|
| $p_{conf}(q)$ | the gate's probability that the answer is in the context | a number in $[0,1]$ |
| $\sigma(z)$ | the logistic function | squashes any real number into $[0,1]$ |
| $\beta_0$ | the intercept | fitted |
| $\beta_1$ | the weight on each feature | fitted, one per feature |
| $\mu$ | the mean of each feature | the calibration split's means |
| $\sigma$ | the standard deviation of each feature | the calibration split's standard deviations |
| $\beta_1^{T}$ | the transpose, so the vectors multiply | a dot product |
| $\phi(q)$ | the feature vector | five numbers |

**In plain words.** Standardise the five features, weight them and add them
to a constant, and squash the result through the logistic function. What
comes out is a probability: the chance that the answer is in the retrieved
context.

**The five features.** The top reranker score, the mean of the reranker's top
three scores, the top BM25 score, the largest fused RRF score, and the number
of candidates above the reranker's own relevance bar.

**Platt scaling.** This is Platt's method: take an existing score, fit a
logistic model on top of it so that the output is a probability, and fit it by
maximum likelihood on a held-out split. The weights are fitted on 60 percent
of the queries; the calibration numbers in the deck are measured on the
other 40 percent.

**Why standardisation.** Without it, a feature measured on a larger scale
would dominate the weighted sum purely because of its units, and the fit
would have to work harder to undo that.

**The caveat, and it is a real one.** An ECE of 0.1044 is reported rather
than improved by refitting. It is the calibration of one fitted artefact on
one fixed split. The industrial gate tracks the diagonal at ECE 0.075; the
focus gate does not, and it puts most of its queries in the lowest confidence
bin.

## B.3 The decision rule

*Slide 8. Written on the slide.*

$$
\mathrm{accept}(q)=\mathbf{1}\left[p_{conf}(q)\geq\tau\right]
$$

| Symbol | What it is | Value or form here |
|---|---|---|
| $\mathrm{accept}(q)$ | whether the query is passed to the generator | 1 or 0 |
| $p_{conf}(q)$ | the calibrated probability | from B.2 |
| $\tau$ | the threshold, the operating point | 0.05 |
| $\mathbf{1}[\cdot]$ | the indicator function | 1 if true, 0 if false |

**In plain words.** If the probability is at least the threshold, answer.
Otherwise refuse, and do not call the generator at all.

**Why the threshold is 0.05.** It was chosen by a stated rule, not by taste:
the highest threshold that still answers at least 90 percent of the answerable
queries. Slide 20 shows the whole sweep, because a single threshold hides
the shape of the frontier behind it.

**The cost.** Every extra refusal is paid for in coverage, and the price
climbs steeply past $\tau = 0.15$. At $\tau = 0.05$ the coverage is 0.693 and
the abstention precision is 0.963. At $\tau = 0.50$ the coverage is 0.097 and
the abstention precision is 0.868. Both are defensible; they are not the same
product.

**The caveat.** A threshold is a policy, not a property of the model. It
belongs to a deployment, and a deployment team would have to calibrate it on
its own corpus.

## B.4 The contradiction gate

*Slide 9. Written on the slide.*

$$
\mathrm{contradiction}(c_1,c_2)=\mathbf{1}\left[\mathrm{NLI}(c_1,c_2)=\mathrm{contradiction}\right]
\wedge\mathbf{1}\left[\mathrm{shared\ measurement}\wedge\mathrm{shared\ instance}\right]
$$

| Symbol | What it is | Value or form here |
|---|---|---|
| $c_1, c_2$ | two retrieved chunks | any pair from the context |
| $\mathrm{NLI}(c_1,c_2)$ | a natural language inference model's judgement | a label: entailment, neutral, or contradiction |
| $\mathrm{shared\ measurement}$ | the two chunks discuss the same measured quantity | the same limit, the same tolerance |
| $\mathrm{shared\ instance}$ | ...of the same instance | the same substance, the same part |
| $\wedge$ | logical and | both must hold |
| $\mathbf{1}[\cdot]$ | the indicator function | 1 if the whole conjunction holds, 0 otherwise |

**In plain words.** A pair of chunks is flagged as a contradiction only when
two independent tests agree: an NLI model says they contradict, *and* they
are talking about the same measured quantity of the same instance.

**Why both branches.** A quantity branch on its own fired on citation years,
and a topical subject check on its own was a topic check rather than a
contradiction check. Requiring both cut the alarms from 81 to 20. Twenty is a
number a reader can check; eighty-one is a number a reader has to take on
trust.

**The cost.** At most 60 candidate pairs are examined per query, which is
what makes the precision study on slide 29 possible at all: twenty alarms is
a manageable number for a reader to check.

**The caveat, and it is the sharpest in the deck.** The precision of this
detector against reader labels is 0.0 percent. Slides 28 and 29 report it
as a null with a 95 percent upper bound of 16.1 percent, not as a defect to
be explained away. The mechanism is unproven rather than disproven, and the
reason is in Part D.

## B.5 The retrieval metrics

*Slide 15. Used in the table, not written on the slide.*

$$
\mathrm{Recall}@k=\frac{\lvert R_k\cap G\rvert}{\lvert G\rvert},
\qquad
\mathrm{MRR}=\frac{1}{\lvert Q\rvert}\sum_{q\in Q}\frac{1}{\mathrm{rank}_q},
\qquad
\mathrm{nDCG}@k=\frac{\mathrm{DCG}@k}{\mathrm{IDCG}@k}
$$

| Symbol | What it is | Value or form here |
|---|---|---|
| $R_k$ | the top $k$ results | the first $k$ of the ranked list |
| $G$ | the gold chunks | the chunk the benchmark says holds the answer |
| $k$ | how deep to look | 10, and also 20 |
| $\mathrm{rank}_q$ | the rank of the gold chunk for query $q$ | 1 if it was first |
| $Q$ | the queries | the benchmark's queries |
| $\mathrm{DCG}@k$ | the discounted gain of the top $k$ | from B.6 |
| $\mathrm{IDCG}@k$ | the discounted gain of the best possible ordering | the ceiling |

**In plain words.** Recall asks whether the answer was found at all. MRR
asks how high up it was. nDCG asks the same as MRR but weighted by relevance
and normalised, so that two systems can be compared on queries with different
numbers of relevant results.

**Why three.** They fail in different ways, and the ablation needs all three
to say anything. A system can find every answer and bury it (recall ties, MRR
loses). A system can find fewer answers but rank them better. Reporting only
recall would have made the reranker look worthless, and only MRR would have
hidden that a configuration lost answers.

**The caveat.** Recall@10 on a benchmark whose gold chunk is in the pool is
measured on the pool, not on the corpus. That is why the deck also reports
the retriever's recall of the gold separately, and why the long-context
comparison is settled on cost and coverage.

## B.6 Discounted cumulative gain

*Slide 15. Used in the table, not written on the slide.*

$$
\mathrm{DCG}@k=\sum_{i=1}^{k}\frac{\mathrm{rel}_i}{\log_2(i+1)}
$$

| Symbol | What it is | Value or form here |
|---|---|---|
| $\mathrm{rel}_i$ | how relevant the $i$-th result is | a relevance weight |
| $i$ | the position in the ranked list | 1 is the best |
| $\log_2(i+1)$ | the discount | 1 at the top, growing slowly |
| $k$ | how deep to look | 10 |

**In plain words.** Add up the relevance of each result, discounted by the
logarithm of its position. The logarithm is what makes the discount gentle:
the difference between first and second place is worth much more than the
difference between ninth and tenth, but not so much that it swamps everything
else.

**Why a logarithm rather than a straight division.** A linear discount would
make position 1 worth as much as positions 2 through 10 combined. The
logarithmic form says that moving from second to first is worth about the
same as moving from eighth to ninth, which matches how much a reader actually
loses by not seeing the best result first.

**The caveat.** DCG depends on relevance judgements, and this project's
relevance is binary: the chunk is the gold one or it is not. That makes DCG
close to a position-weighted recall, and it is reported alongside MRR rather
than instead of it.

## B.7 The answer rate and the abstention precision

*Slide 20. Used in the table, not written on the slide.*

$$
r_{ans}(U)=\frac{\lvert\left\{q\in U:\mathrm{answered}(q)\right\}\rvert}{\lvert U\rvert},
\qquad
\mathrm{Prec}_{ref}=\frac{\lvert\mathrm{refused}\cap U\rvert}{\lvert\mathrm{refused}\rvert}
$$

| Symbol | What it is | Value or form here |
|---|---|---|
| $U$ | a class of queries | the unanswerable class, or the answerable class |
| $r_{ans}(U)$ | the share of that class the system answered | a rate |
| $\mathrm{answered}(q)$ | whether query $q$ was answered | 1 or 0 |
| $\mathrm{refused}$ | the set of queries the gate refused | a set |
| $\mathrm{Prec}_{ref}$ | of the refusals, the share that were right to refuse | a rate |

**In plain words.** The first asks: of the questions that had no answer, how
many did the system answer anyway? The second asks: of the questions it
refused, how many genuinely had no answer?

**They are not the same measurement, and the deck is careful about which one
it is quoting.** $r_{ans}$ is measured over a class and has that class in the
denominator. $\mathrm{Prec}_{ref}$ is measured over the refusals and has the
refusals in the denominator, so it says nothing about how much was refused.
A system that refused everything would have a perfect abstention precision
and be useless, which is why the sweep on slide 20 reports coverage next to
it.

**Why the second one is the claim.** A practitioner wants to know: when this
system says it does not know, is it right? That is exactly
$\mathrm{Prec}_{ref}$, and it is 0.963 at the fitted operating point.

**The caveat.** The two are reported separately per class, never pooled. A
gate can improve the unanswerable class and damage the answerable class at
the same time, and one number for both would hide the trade.

## B.8 Expected calibration error

*Slide 20. Used in the table, not written on the slide.*

$$
\mathrm{ECE}=\sum_{b=1}^{B}\frac{\lvert B_b\rvert}{N}\left\lvert\mathrm{acc}(B_b)-\bar{p}(B_b)\right\rvert
$$

| Symbol | What it is | Value or form here |
|---|---|---|
| $B_b$ | the queries in confidence bin $b$ | a bin |
| $B$ | the number of bins | the bins used |
| $\lvert B_b\rvert$ | how many queries are in bin $b$ | a count |
| $N$ | the total number of queries | 71 on the focus half, 178 on the industrial half |
| $\mathrm{acc}(B_b)$ | the observed answerable rate in bin $b$ | the truth |
| $\bar{p}(B_b)$ | the mean predicted probability in bin $b$ | what the model said |
| $\lvert\cdot\rvert$ | absolute value | so that over- and under-confidence both count |

**In plain words.** Split the queries into bins by how confident the gate
was. In each bin, compare the average confidence with the observed rate of
the answers actually being there. Weight each bin by how many queries are in
it, and add up the gaps. Zero is perfect calibration.

**Why the weighting matters.** Without the weight, a bin with one query
counts as much as a bin with a hundred. The weighting says the ECE is the
average error over queries, which is the thing a reader wants.

**What it cannot tell you.** A single number hides the shape. The focus
gate's ECE of 0.1044 comes mostly from the fact that it puts most of its
queries in the lowest confidence bin. The reliability diagram on slide 21 is
where that is visible, and the deck shows both.

## B.9 The Brier score

*Slide 20. Used in the table, not written on the slide.*

$$
\mathrm{Brier}=\frac{1}{N}\sum_{i=1}^{N}(p_i-y_i)^2
$$

| Symbol | What it is | Value or form here |
|---|---|---|
| $p_i$ | the predicted probability for query $i$ | in $[0,1]$ |
| $y_i$ | the outcome for query $i$ | 1 if the answer was in the context, 0 if not |
| $N$ | the number of queries | the evaluation half |
| $(\cdot)^2$ | squaring | so that errors count in both directions |

**In plain words.** The average squared gap between what the gate said and
what was true. Lower is better.

**Why square the error.** A large mistake must count more than a small one,
or the score would reward a model that is confidently wrong. Squaring also
makes the loss smooth, so a fitted model can be optimised on it directly.

**How it differs from the ECE.** The ECE is about bins: it asks whether the
average confidence in a group matches its observed rate, and it is blind to
whether the predictions inside a bin are ordered. The Brier score is about
each query: it asks how close each stated probability is to the truth. A
model can have a good ECE and a poor Brier score, because a confident and
wrong prediction inside a well-calibrated bin still costs a full point of
squared error.

**The value.** 0.1510. With a base rate of 0.182, a model that always
answered "no" would score 0.182. The gate's 0.1510 is better than that
trivial model and not dramatically so. That is the honest size of the gain,
and the report gives the trivial model's number rather than only its own.

## B.10 The exact McNemar test

*Slide 23. Used in the table, not written on the slide.*

$$
p=2\sum_{k=0}^{\min(b,c)}\binom{n}{k}\left(\frac{1}{2}\right)^{n}
$$

| Symbol | What it is | Value or form here |
|---|---|---|
| $b$ | questions the baseline answered and the arm refused | the disagreements that help |
| $c$ | questions the baseline refused and the arm answered | the disagreements that hurt |
| $n$ | $b + c$, the number of disagreements | the only rows that matter |
| $\binom{n}{k}$ | the number of ways to choose $k$ of $n$ | a binomial coefficient |
| $k$ | the running index of the sum | 0 to $\min(b,c)$ |
| $p$ | the p-value | the probability of a split this lopsided, by chance |

**In plain words.** Only the questions where the two systems disagreed can
carry evidence. Under the null hypothesis that the two systems are
indifferent, each of those $n$ disagreements is a coin flip, so the number
of them landing on one side is a binomial count. The formula computes the
probability of a split at least as lopsided as the observed one, and doubles
it because a split that lopsided could have gone the other way.

**Why the disagreements are the whole test.** The 176 queries
where both systems agreed tell the test nothing: they cannot distinguish the
arms. Only
the $b + c$ where they differ can, and that is why the counts $b$ and $c$ are
on the slide rather than a bare p-value.

**Why it is exact.** The formula computes the probability directly instead of
approximating it with a normal curve. At these counts, where $n$ is small,
the approximation is poor and the exact test is the right one.

**The two headline counts.** The gate against the ungated arm on the
unanswerable class gives $b = 60$, $c = 1$, $p < 0.001$. The random control
against the ungated arm gives $b = 11$ with $p = 0.001$. The difference
between those two is the whole finding: the gate's refusals land on the
right questions and the random control's do not.

## B.11 The ROC curve and its permutation null

*Slides 12 and 14. Used in the table and the figure.*

The ROC curve plots the true positive rate against the false positive rate
over every possible threshold, and the ROC AUC is the area under it. A coin
flip gives 0.5; perfect separation gives 1.0.

**The permutation null.** To ask whether a classifier is doing something, the
labels are shuffled and the classifier is re-run many times. The AUC of a
classifier that has learned nothing is then whatever the shuffled procedure
produces by chance. Here the focus corpus's permutation null has a mean of
0.455 and a standard deviation of 0.072, with a maximum of 0.628 over the
permutations. A measured AUC is only interesting against that null, not
against 0.5.

**The headline.** The question-only classifier scored 0.999 against a null
of 0.455 plus or minus 0.072. That is not a classifier, it is a leak: the
answer was written into the question.

**The caveat.** After the repair the same procedure scores 0.608 on the
focus corpus and 0.708 on the industrial one, and on the better-powered
six-category corpus it is indistinguishable from chance at 0.533. The
repaired benchmark is decidable from the evidence rather than from a
question-shape rule, but on two of the three corpora it is not entirely free
of form-only separability. That is reported rather than rounded away.

## B.12 The Wilson score interval

*Slide 29. Used in the figure.*

For a proportion $\hat{p}=x/n$ observed $x$ times in $n$ trials, the Wilson
interval is

$$
\frac{2x + z^2 \;\pm\; z\sqrt{z^2 + 4x(n-x)}}{2(n + z^2)}
$$

where $z$ is the normal quantile for the chosen confidence level, 1.96 for
95 percent.

**In plain words.** The interval that behaves sensibly when the count is
small.

**Why it is used.** At 0 successes out of 20, the naive interval
("plus or minus 1.96 times the standard error of a proportion that is
zero") collapses to a single point and claims a precision it does not have.
The Wilson interval stays wide and honest, which is what makes the
contradiction result reportable as a range rather than as a bare zero.

**The caveat.** The upper bound of 16.1 percent on the contradiction
detector's precision is a Wilson upper bound. It says the true precision is
probably below 16.1 percent. It does not say it is zero.

# Part C. The slides

Every slide, in order, with what is on it, the measurement behind it, and the
caveat that belongs with it. The six measured figures are explained at the
end.

## C.1 Slide 1. Title

<!-- slide:1 -->

The title, the subtitle, your name and roll number, the department, the
supervisor and the date. The subtitle names the four things the talk covers:
architecture, evaluation protocol, failure modes, and what the measurements
actually show. The third is the unusual one, and it is the one to emphasise:
the report does not claim a new architecture, it claims a measured
characterisation of one.

## C.2 Slide 2. A wrong answer costs more than no answer

<!-- slide:2 -->

**On the slide.** Three bullets on the left, and the research question in a
panel on the right.

**The argument.** The corpus is not a wiki. It is a controlled set of
documents somebody signed off on, and the questions are operational decisions:
is this tolerance acceptable, which procedure step applies, what does the
specification require. A refusal costs a supervisor five minutes. A
confidently fabricated tolerance costs a scrapped batch.

**The question being asked.** When a retrieval-augmented generator is given
industrial text, can a gate in the code decide whether the retrieved evidence
actually contains the answer? And what is that gate worth, once it has been
measured properly?

**The caveat, which is the point of the second half of the question.** "Once
it has been measured properly" is doing real work. Slide 3 says what that
turns out to have cost.

## C.3 Slide 3. Two things that make this hard to measure

<!-- slide:3 -->

**On the slide.** Two panels, numbered 1 and 2.

**1. Gates get evaluated by intent, not by measurement.** Someone picks a
threshold. The system refuses some questions. A refusal rate gets reported.
The question a practitioner needs is different: given a refusal budget, how
many refusals land on the questions that should have been refused?

**2. The benchmark can carry its own answer.** A benchmark whose unanswerable
half is easy to separate from the answerable half measures the benchmark,
not the system. This project found exactly that defect in its own benchmark.
Repairing it moved the headline refusal rate by a factor of nearly four.

**Why this slide exists.** Both of these are things that only show up when
you go looking for the measurement behind a headline number. Neither is
visible in the output of the system.

**Terms.** *Abstention precision*, *shortcut* -- Part A.

## C.4 Slide 4. Four research objectives

<!-- slide:4 -->

**On the slide.** Four numbered objectives.

**RO1.** Build an evidence-grounded RAG framework for industrial decision
support. Generation is gated in code. The generator is called at one point in
the pipeline, and only when the gate accepts.

**RO2.** Make retrieval modality-balanced and category-aware. Fuse a lexical
and a dense leg, rerank with a cross-encoder, and hold a quota over text,
table and chart chunks.

**RO3.** Test the framework's own hypothesis about hallucination. Against a
generator that is required to answer, not only one allowed to decline. Only
the first case removes the generator's own credit.

**RO4.** Characterise the failure modes. Report the failures that contradict
the framework with the same care as the successes, and publish the error
rates of the measuring instruments.

**RO3 is the objective that gets pressed on.** The hypothesis is the
framework's own, and the design makes it falsifiable.

## C.5 Slide 5. The contribution is the framework, and the measurement of it

<!-- slide:5 -->

**On the slide.** Five bullets on the left, and a panel on the right headed
"What is new".

**The five components.** Hybrid retrieval: a lexical leg and a dense leg
(Karpukhin et al. 2020) fused by reciprocal-rank fusion (Cormack et al.
2009). Modality balance: a quota across text, tables and charts. A gate that
cannot be bypassed: generation is called at exactly one point, after a
calibrated posterior clears the threshold (Yadkori et al. 2024). Contradiction
surfacing: two independent branches that have to agree. Per-claim evidence
tags: every claim in the answer carries the chunk that supports it.

**What is new.** Every mechanism the framework draws on is published. What is
new is that they are put together into one industrial system, and that the
whole thing is then measured end to end on industrial text, at the level of
the individual answer claim, with the benchmark's own defects audited and
repaired.

**The closest prior art.** HALT-RAG (Goswami and Kurra 2025) is a post-hoc
output verifier. It never runs a generator. Its own future work names the
step this report performs.

**Why the framing matters.** The room should hear that the architecture is a
contribution in its own right, and that the measurement of it is the second
half of the contribution rather than the whole of it. A candidate who claims
the architecture is new will be asked which component is new, and every
answer is "none of them".

## C.6 Slide 6. The framework: five stages

<!-- slide:6 -->

**On the slide.** Five boxes, left to right, with a chevron between each.
Two of them are purple and three are grey. A panel below them carries the
non-bypassability claim.

**The five stages.** Stage 0 query-form validation, which costs no retrieval
and no model call. Stage 1 hybrid retrieval, BM25 plus bge-m3 fused by RRF.
Stage 2 rerank and quota, a cross-encoder and a modality floor. Stage 3 the
confidence gate, which is the mechanism the report is about. Stage 4
generation and claim assessment, every claim scored against the evidence
shown.

**The two purple boxes are stages 0 and 3.** Say "two stages can refuse" and
point at them. The grey ones cannot.

**The panel below.** The generator is not handed to `answer()` by the caller.
It is injected into the framework, and the framework calls it at exactly one
line, after the gate has accepted. On a refusal the claim assessment and the
contradiction detection are skipped too, so a refused query costs no model
call at all. The only paths that skip the gate are the two comparison arms,
`rag_nogate` and `long_context`. Both are named for what they remove and
reported as separate results.

**Terms.** *Non-bypassability*, *form validator*, *claim*, *modality quota* --
Part A.

## C.7 Slide 7. Hybrid retrieval

<!-- slide:7 -->

**On the slide.** The fusion formula (B.1), four bullets, and a panel on the
right headed "Why the dense leg changed".

**The configuration.** The lexical leg is Okapi BM25. The dense leg is
BAAI/bge-m3, 1024 dimensions, L2 normalised. Fusion is reciprocal rank fusion
over the top 20 of each leg. The category pre-filter restricts both legs
before fusion.

**The panel.** The first dense leg was a general-purpose sentence encoder,
and it was measurably worse than plain BM25 on this corpus. A fusion that
included it was carrying a leg that lost information. The encoder was
replaced with BAAI/bge-m3. It is archived and its numbers are kept as
tokens, so both sides of the comparison rest on measured values rather than
recollection.

**The invariants.** The category filter, the reranker and the quota are all
enforced as invariants, and each one is asserted directly.

**Why it matters.** The encoder swap is a good example of measuring the
components rather than assuming them. Two findings changed sign when it was
done.

## C.8 Slide 8. The confidence gate

<!-- slide:8 -->

**On the slide.** Two formulas (B.2, B.3), three bullets, and a panel headed
"Why the query level, not the chunk level".

**What it is.** A calibrated posterior over the whole retrieved pool. Five
query-level features go into a logistic model fitted by maximum likelihood on
a 60 percent calibration split, and the decision is a threshold on the
posterior. The fitted operating point on the focus domain is $\tau = 0.05$.

**The five features.** The top reranker score, the mean of the top three,
the top BM25 score, the maximum fused score, and the candidates above the
reranker's bar.

**The panel is the answer to "why is this not just a similarity threshold".**
With one gold chunk among about fifty candidates, a chunk-level classifier
is right 98 percent of the time by answering "nothing is relevant".
Maximum-likelihood fitting duly returns a large negative intercept. That is a
degenerate solution: it looks like a fitted model and behaves like a
constant. Calibrating at the query level removes it.

## C.9 Slide 9. The contradiction gate

<!-- slide:9 -->

**On the slide.** The conjunction formula (B.4), four bullets, and a panel
on the right headed "Why the conjunction".

**The two branches.** Branch 1 is a natural-language-inference model at
threshold 0.70. Branch 2 requires that the two chunks talk about the same
measured quantity of the same instance. At most 60 candidate pairs are
examined per query.

**The panel.** A quantity branch on its own fired on citation years. A
subject check based on topical similarity on its own was a topic check, not a
contradiction check. Requiring both cut the alarms from 81 to 20. Twenty
alarms is a manageable number for a reader to check, which is why the
precision study was possible at all.

**The forward reference.** The branch-2 check is what keeps this from being a
topic detector. What happens to the alarms it raises comes later, and the
answer is not what this framework wanted.

## C.10 Slide 10. The corpora

<!-- slide:10 -->

**On the slide.** A table of three corpora with their roles, chunk counts,
document counts and query counts, and two panels.

**The corpora and their roles, which do not overlap.** The supply-chain
focus corpus carries 735 chunks from 14
documents and is where the ablation, the gate and the generation experiments
run. The six-category industrial corpus carries 2383 chunks
from 46 documents and is where transfer and the long-context
cost are measured. The federal regulatory corpus carries 465
chunks from 7 documents and exists because it is the corpus
where the contradiction detector's phenomenon could be looked for.

**The question split.** The focus corpus carries 32
answerable and 144 unanswerable questions. The
cross-category corpus carries 132 and
144. The two never mix.

**Why a public substitute.** The primary corpus of 24 proprietary
supply-chain documents cannot be redistributed, so every measurement runs on
a public substitute. Each document ships with its upstream identifier, a
SHA-256, the chunk count and the licence.

**The limit, stated up front.** The corpus is encyclopaedic text, not
practitioner documentation, and the claims are narrowed to match.

## C.11 Slide 11. The benchmark had to be repaired twice

<!-- slide:11 -->

**On the slide.** Two repair panels and a third headed "Why it counts".

**Repair 1, the answer-label defect.** 30 of the answerable questions
carried an answer label attached to the wrong question. Two defects in the
label generation caused it. After the repair the defect rate is 1 of 32. The
gold chunk was always right, so the retrieval-side numbers were never
affected.

**Repair 2, the unanswerable class.** The unanswerable half was separable
from the question text alone. One regular expression caught 100 percent of
the hard family with zero false positives. The class was rebuilt with
corpus-anchored definitions and a structural twin for every repaired
question. The pre-repair benchmark is archived, so the before-and-after claim
stays checkable.

**Why it counts.** The instrument that found the defect was kept, not
deleted. A benchmark is a piece of software. Its bugs are invisible in its
outputs.

**Why this slide is worth the time.** If the room only remembers one thing
about methodology, this is it. The benchmark was audited and the headline
changed rather than explained away.

## C.12 Slide 12. The shortcut

<!-- slide:12 -->

**On the slide.** Three big numbers.

**The numbers.** ROC AUC 0.999 for a question-only classifier before the
repair. A gate refusal rate of 91.7 percent on the defective class. 76.4
percent caught by a single identifier regular expression.

**What happened.** The hard family named a fabricated identifier. No
answerable question carried an identifier of that shape, so one regular
expression caught the whole family. The hard family was recognisable from
the question text alone, and a classifier on the query alone told the two
classes apart.

**The consequence.** The refusal rate measured the benchmark, not the
framework. This is the finding that took the most work, and it is the one
that changes the headline. Say it slowly.

## C.13 Slide 13. After the repair

<!-- slide:13 -->

**On the slide.** Three big numbers, and a panel headed "The gap between the
two strata is the finding".

**The numbers.** A question-only policy ROC AUC of 0.564 after the repair. 0.0
percent caught by the same identifier regular expression. A gate refusal of
23.6 percent on the corpus-anchored hard stratum.

**The panel.** The gate refuses 26 of 34 of the out-of-domain
stratum, and only 23.6 percent of the hard stratum, where the corpus
discusses the subject but does not state the answer. So the gate detects a
*recognisable* unanswerable question. It does not detect an absent answer. A
24 percent rate on the hard stratum is a different instrument from a 92
percent rate on an easy one, and the first number is the one a deployment
would meet.

**The likely question, and where the answer is.** The examiner will likely
ask whether the gate is worth anything if it only catches the easy cases. The
answer is on the next slides: the gate's precision where it refuses is 0.963,
and the random control is what makes that visible.

## C.14 Slide 14. A classifier that reads the answer off the question

<!-- slide:14 -->

**On the slide.** The ROC figure (Figure 5), and three bullets.

**The bullets.** Before the repair, the two classes were separable almost
perfectly on the focus corpus: ROC AUC 0.999 against a permutation null of
0.455. One regular expression did it: a fabricated identifier caught 76
percent of the unanswerable questions with no false positive at all. After
the repair, the shortcut catches nothing and what is left of the procedure's
power is small but not zero.

**What the figure is.** It is the audit, and it is the reason the headline
refusal rate had to be rebuilt. Four curves: chance, the focus corpus before
the repair, the focus corpus after it, and the industrial corpus after it.

**Terms.** *ROC AUC*, *shortcut*, *permutation null* -- Part A and B.11.

## C.15 Slide 15. Retrieval results on the focus corpus

<!-- slide:15 -->

**On the slide.** A table of seven ablated systems with three metrics each,
and three bullets.

**The seven configurations.** A is BM25 only. B is dense only. C is the
fusion. D adds the reranker. E adds the category filter. F adds the quota
before the reranker. G adds the quota after it. Each row is the previous
row plus one thing, so a difference between two rows is the cost of that one
thing.

**What the numbers say.** The dense leg is significantly worse than BM25:
0.969 to 0.812, $p = 0.025$. This is why the encoder changed. Fusion
recovers the loss and beats both legs: 1.000 against 0.812, $p = 0.014$.

**The claim for fusion is narrow.** It stopped being a loss. It did not
become a significant win over plain BM25 on its own.

**Why seven rows.** A fusion carrying a leg that lost information is worse
than no fusion, and only a row-by-row ablation shows which leg that was.

## C.16 Slide 16. The reranker's value depends on the corpus

<!-- slide:16 -->

**On the slide.** Two big numbers and a quotation panel.

**The numbers.** An MRR change from the reranker of -0.3 percentage points
on the focus corpus, not significant. 11.1 percentage points on the
six-category corpus, $p = 9.3\times10^{-4}$.

**The quotation.** "The reranker buys ordering, not recall." True on the
six-category corpus, false on the focus corpus. So it is reported with its
corpus attached wherever it appears. A component that helps on one corpus and
not on another is not a component that helps.

**Why this slide exists.** A claim without the corpus attached, and the
numbers in the same paragraph, contradict each other. That contradiction is
in the report's own earlier draft of this material, and the slide is the
correction.

## C.17 Slide 17. The candidate pool curve peaks and then declines

<!-- slide:17 -->

**On the slide.** The pool-size figure (Figure 1), a table of five pool
sizes with three metrics each, and two bullets.

**The table.** A pool of 5 gives Recall@10 of 0.969, a pool of 10 gives
1.000, and pools of 20, 50 and 100 give 0.969. MRR falls as the pool grows:
0.807, 0.805, 0.797, 0.795, 0.795.

**The bullets.** Recall@10 peaks at a pool of ten. Beyond that the gold chunk
is still found at twenty, and then the reranker pushes it out of the
ten-chunk context. The industrial corpus is the exception: there the gold
chunk is still arriving at fifty, so Recall@20 reaches 1.000 while Recall@10
stays at 0.988.

**The point.** A larger pool costs ordering without adding the answer, and
which way it fails depends on the corpus.

## C.18 Slide 18. The quota placement has no universally better answer

<!-- slide:18 -->

**On the slide.** A table of three corpora with the quota before and after
the reranker and a p-value, and a panel below.

**The table.** On the focus corpus the quota before the reranker gives 1.000
and after it 0.938, with $p = 0.157$. On the six-category industrial corpus
0.939 against 0.924, $p = 0.480$. On the federal regulatory corpus 0.988
against 0.980, $p = 0.317$.

**The panel.** The position is read from the configuration rather than
asserted in prose, because the ranking differs by corpus and a fixed rule
would not hold on all of them.

**How to say it.** A placement that has to be read from the configuration is
a placement the evidence does not settle. Say so rather than asserting one.

## C.19 Slide 19. The modality quota is a trade, not a gain

<!-- slide:19 -->

**On the slide.** The quota figure (Figure 4) and three bullets.

**The bullets.** On the industrial corpus, the pre-rerank quota buys 0.8
points of table recall and gives up 0.8 points of overall recall, and the
post-rerank quota lands on exactly the no-quota operating point. On the
focus corpus, the post-rerank quota gives up 3.1 points of overall recall
while table recall stays at 1.000. So the placement is a configuration value.
Which way it trades depends on where it is applied, and the claim is never
made without its corpus.

**This is the picture behind the placement question.** The quota moves one
axis and gives up the other.

## C.20 Slide 20. Calibration and the operating-point sweep

<!-- slide:20 -->

**On the slide.** The threshold sweep in full (seven rows) and four bullets.

**The rule.** The highest $\tau$ that still answers at least 90 percent of
the answerable queries. That gives $\tau = 0.05$.

**The sweep.** At 0.05: 0.938 of the answerable answered, 0.361 of the
unanswerable refused, abstention precision 0.963, coverage 0.693. At 0.10:
coverage falls to 0.432. At 0.15: 0.364. At 0.20: 0.278. At 0.30: 0.170.
At 0.50: 0.097. At 0.90: 0.017.

**The four bullets.** The gate is precise where it refuses: abstention
precision 0.963. The frontier is real: every extra refusal is paid for in
coverage, and the price climbs steeply past $\tau = 0.15$. Calibration:
ECE 0.1044, Brier 0.1510.

**What a practitioner takes from this slide.** The abstention precision
column. 0.963 says: when this system says it does not know, it is right 96
percent of the time on this corpus at this operating point.

## C.21 Slide 21. Calibration and the risk-coverage frontier

<!-- slide:21 -->

**On the slide.** Two figures side by side: the reliability diagram
(Figure 3) on the left, the risk-coverage curve (Figure 2) on the right.

**The caption.** Figure 3 is the reliability of the calibrated probability
against observed answerability. Figure 2 is the risk that an answered query
has no answer in its context, against the fraction of queries the gate
answers.

**What they show.** The industrial gate tracks the diagonal on the
reliability diagram; the focus gate does not. On the risk-coverage curve the
focus gate buys very little over answering everything.

**Both are measured on the held-out evaluation half**, not on the split the
gate was fitted on.

## C.22 Slide 22. One generator, five arms, two prompt conditions

<!-- slide:22 -->

**On the slide.** A table of the five arms and what each removes, and a
panel headed "Why the random arm matters".

**The five arms.**

| Arm | What it removes |
|---|---|
| `rag_nogate` | the gate, keeping retrieval |
| `rag@fitted` | nothing; the framework at its fitted operating point |
| `rag@random` | the confidence score, keeping the refusal budget |
| `rag@transferred` | the fitted operating point; the threshold moved across corpora |
| `long_context` | retrieval; the whole corpus in the prompt |

**The panel.** `rag@random` refuses the same number of questions as the
fitted gate but picks them at random, ignoring the confidence score. Without
it, an implementation that refuses on a coin flip and one that refuses on a
calibrated score look identical on the easiest metric to report.

**The two prompt conditions differ by one sentence.** Everything else is
identical: model, questions, retrieval, scorer, temperature.

**Why the slide title says "Experiment 8".** The deck numbers its
experiments, and this is the eighth. The numbering is in the report, where
every experiment is written out with its own hypothesis.

## C.23 Slide 23. The answering condition

<!-- slide:23 -->

**On the slide.** A table of five arms against four columns, and the
verdict.

**The table.** Under the answering condition the generator cannot decline on
its own, so the gate cannot be redundant.

| Arm | Unanswerable answered | Answerable answered | Paired McNemar, unanswerable |
|---|---|---|---|
| `rag_nogate` | 135 of 144 (0.938) | 32 of 32 | none |
| `rag@fitted` | 76 of 144 (0.528) | 30 of 32 | b = 60, c = 1, p < 0.001 |
| `rag@random` | 87 of 144 (0.604) | 21 of 32 | none |
| `rag@transferred` | 3 of 144 (0.021) | 6 of 32 | none |
| `long_context` | 134 of 144 (0.931) | 32 of 32 | p = 1.00 |

**The verdict: supported under both prompt conditions.** Under the cautious
prompt the rate falls from 0.535 to 0.417, at the cost of the same two
answerable questions. The paired test is significant under both conditions.

**This is the slide the whole report is built around.** The paired test on
the unanswerable class is the headline, and the cost in coverage is stated
on the same slide.

## C.24 Slide 24. What the confidence score actually buys

<!-- slide:24 -->

**On the slide.** A paragraph, two callouts, and a closing statement.

**It does not buy a lower answer rate on unanswerable questions.** The random
control reaches 0.604, which is worse than the fitted gate's 0.528 and far
below the ungated arm's 0.938. It gets there by refusing an arbitrary set of
the same size, and some of those are answerable questions. Refusing at random
is already a big improvement over never refusing, because most questions in
a benchmark are unanswerable.

**The two callouts.** 2 answerable questions refused by the gate,
$p = 0.500$. 11 answerable questions refused by the random control,
$p = 0.001$.

**What the score buys is where the refusals land.** The gate concentrates
them on the unanswerable class. The control does not. This is a precision
claim about refusals, and the paired test on the answerable questions is
where it is established.

**The warning.** If a report said "the gate answers fewer unanswerable
questions", it would be true and it would be misleading.

## C.25 Slide 25. The trade, counted from the records

<!-- slide:25 -->

**On the slide.** A table of four arms against four count columns, and two
paragraphs.

**The table.**

| Arm | Answered | Of which wrong | Correct (entailment) | Correct (key term) |
|---|---|---|---|---|
| `rag_nogate` | 167 | 135 | 21 | 29 |
| `rag@fitted` | 106 | 76 | 20 | 27 |
| `rag@random` | 108 | 87 | 15 | 20 |
| `long_context` | 166 | 134 | 13 | 24 |

**The trade.** The gate removes 59 wrong answers and costs 1 correct answer
under the entailment test. Under the cautious prompt the gate even ends up
ahead on the correct count.

**And that is not a quality gain.** It is a selection effect: a gate declines
the hardest questions, so the ones it does answer are easier, and its
per-answer accuracy cannot be compared with an arm that answered everything.
Tikhomirov and Savchenko (2026) name the phenomenon. It is also why the
cautious condition alone would have been a misleading headline.

## C.26 Slide 26. Long context against the pipeline

<!-- slide:26 -->

**On the slide.** Three big numbers, three bullets, and a panel.

**The three numbers.** 74 times the input tokens per query. 58.8 times the
input cost per query, at the provider's cached pricing. 33.0 percent of the
long-context tokens are cache reads.

**The bullets.** Coverage: the whole-corpus prompt answered
32 of 32 answerable questions, the same as the ungated
pipeline. Quality: accuracy 0.406 against 0.667 for the gated arm, not
significant under a length-controlled re-scoring.

**The panel: the token ratio is not a cost.** Read the token ratio naively
and the cost penalty looks two orders of magnitude larger than the one
actually measured. Most of the long-context arm's tokens are cache reads at a
fifth of the base rate. A token ratio must never carry an argument about
money.

## C.27 Slide 27. The evidence is not lost in a big context

<!-- slide:27 -->

**On the slide.** Two big numbers and two bullets.

**The numbers.** 0.969 of focus queries put the gold chunk in the top 10 when
the candidate set is every chunk. 0.902 of cross-category queries, same
measurement.

**The bullets.** Median rank of the gold chunk: 1. A retriever that finds the
answer at median rank 1 does not need the rest of the corpus in the prompt.
The cross-category corpus does not fit a 128K window: 680,417
tokens, 5.2 times the limit, so the quality half of that
comparison could not be run there and it is settled on coverage and cost
alone.

**Why this slide is separate.** This is the cheap half of the long-context
comparison, and it is the part that generalises.

## C.28 Slide 28. The contradiction gate: a precision of zero

<!-- slide:28 -->

**On the slide.** Three big numbers and a panel.

**The numbers.** 0.0 percent precision against reader labels, from 20
labelled alarms. A 95 percent upper bound of 16.1 percent on the true
precision. Annotator agreement of 101 out of 101 on the contradiction
decision.

**The panel.** None of the raised alarms was confirmed. Two annotators that
do not share a model, both blind to the detector's scores, and both 14 of 14
correct on a control set with known labels. They still confirmed nothing.
The readers also found 0 contradictions in a random sample of 80 pairs the
gate did not flag. This corpus holds concept-level prose, not instance
records, so it does not contain the phenomenon the mechanism detects. The
mechanism is unproven, not disproven.

**How to report it.** This is the negative result. Report it as a null with
an upper bound, not as a defect. The two detector defects the audit exposed
were real and were fixed, but they were not the reason the alarms went
unconfirmed.

## C.29 Slide 29. The contradiction detector against the base rate

<!-- slide:29 -->

**On the slide.** The precision figure (Figure 6) and three bullets.

**The bullets.** The focus corpus's semantic branch has a precision of 0.0.
Not one of the 20 alarms was confirmed by either annotator, and the 95 percent
upper bound is 16.1 percent. The branch would not act. The industrial
semantic branch reaches 0.65 against a base rate of 0.35, so there it would
act. The industrial quantity stratum is not measurable from these data: the
branch fired on 13 of 119 scored pairs, but its precision was never
measured.

**How to read the figure.** A filled marker means the branch would act; a
hollow one means the findings would be withheld. On the focus corpus it is
hollow.

**The base rate is the point.** A detector's precision means nothing without
the rate at which the thing it detects actually occurs. If the corpus
contains no real conflicts, every alarm is a false alarm and the precision
is zero by construction.

## C.30 Slide 30. An empty completion is a third outcome

<!-- slide:30 -->

**On the slide.** A table of two generators, three bullets, and a panel
headed "The rule this forces".

**The table.** MiniMax-M3 returned no text on 0 of 66 questions and 0 of 44
on the table-lookup family. MiniMax-M3.1-Flash returned no text on 24 of 66
questions and 23 of 44 on the table-lookup family; raising the output budget
fourfold rescued 13 and left 11 still empty.

**The bullets.** Raising the budget fourfold did not fix it: 13 rescued, 11
still empty. The model spends its budget thinking and returns nothing. So
the replication could not be run, and the hypothesis is supported for one
generator rather than in general.

**The rule this forces.** A run like that is recorded as not run, with the
reason, rather than as a run with empty arms. A rate quoted from a run that
did not happen is indistinguishable from a rate that did.

**The argument for the gate's position.** A generator that cannot answer
costs nothing on the questions the gate rejects, which is an argument for the
gate sitting upstream of generation.

## C.31 Slide 31. The gate is an evidence gate, not a form gate

<!-- slide:31 -->

**On the slide.** Three big numbers and three bullets.

**The numbers.** 76.7 percent of malformed stems were accepted by the gate.
25 of 25 hand-authored malformed queries refused by the form validator. 0 of
35 hand-authored well-formed queries wrongly refused.

**The bullets.** The gate is good at "is there evidence here?" and no use at
"is this even a question?". It is never credited with the validator's work.
The counterfactual is worth recording: reusing the benchmark builder's
question-generation rule as a runtime check would have refused 100.0 percent
of hand-labelled well-formed questions. The lesson: a filter written for one
purpose does not fit another, and the false-rejection rate has to be
measured before it ships.

**The memorable part.** The counterfactual. A rule that looked as if it did
the job would have refused every well-formed question in the set.

## C.32 Slide 32. Most unattributed error comes from the evidence

<!-- slide:32 -->

**On the slide.** A table of five error measures against two evidence sets,
and a paragraph.

**The table.** Over the retrieved evidence against over the gold evidence:
grounded claims 0.118 against 0.542; inferred claims 0.103 against 0.513;
uncertain claims 0.220 against 0.610; reference hallucination 0.164 against
0.571; answer-position effect $p = 0.417$ against $p = 0.008$.

**What it means.** The grounded-claim error rate is 0.118 over the evidence
the arm was shown, and 0.542 over the gold chunk. Most of the error the
framework's own attribution cannot explain is explained by the evidence it
was given. That is a retrieval problem, not a scoring problem.

**Why the comparison is clean.** The gold chunk was always right, so this is
the same answers scored against two evidence sets, with nothing else
changing.

## C.33 Slide 33. Cross-category transfer

<!-- slide:33 -->

**On the slide.** A table of two comparisons across four columns, and three
paragraphs.

**The table.**

| Comparison | Delta Recall@10 | Delta MRR | Delta nDCG | p (MRR) |
|---|---|---|---|---|
| A to C, BM25 to fusion | +0.023 | -0.007 | none | 0.76 |
| C to D, fusion to rerank | +0.000 | +0.111 | +0.085 | 0.00093 |

**A calibrated threshold does not transfer.** `rag@transferred` answers only
6 of 32 answerable questions. The threshold was fitted on
one half of the cross-category corpus and applied unchanged to the other
half, and it over-refuses badly. The threshold has to be refitted per corpus.
This is the clearest evidence in the report that a calibrated number is only
valid for the thing it was calibrated on.

**The limit worth stating.** The transfer study measures coverage on
answerable questions across categories only. The benchmark's unanswerable
questions carry no category, so refusal behaviour across domains is not
measurable under a category split.

**Why this slide is the most practically useful one in the deck.** For anyone
who wants to deploy this: calibrate per corpus.

## C.34 Slide 34. What was measured, and what was not

<!-- slide:34 -->

**On the slide.** Two columns, "Measured" and "Not measured".

**Measured.** Retrieval on 32 answerable queries, seven configurations, paired
tests. The gate's calibration and its full threshold sweep,
176 queries. The gate's behaviour on unanswerable questions
under two prompt conditions, one generator, five arms, paired McNemar. The
contradiction gate's precision against reader labels, with the annotators' own
agreement. The claim scorer's error profile, audited on the benchmark's own
answers. The long-context arm's cost, coverage and retrieval-side proxy on
both corpora.

**Not measured.** The generator-side comparison on a second generator: the
model returned no text on 24 of 66 questions. The long-context answer quality
on the cross-category corpus: it does not fit a 128K window. The
hallucination rate on generated text as such: what is measured is the rate of
answering unanswerable questions, which is a different quantity. Refusal
behaviour across domains: the category split carries no unanswerable
questions. The contradiction gate's precision against human readers: the
annotators are models.

**Read the right-hand column out loud.** A committee values a candidate who
knows what they did not measure. A one-sided list is the thing this report
argues against.

## C.35 Slide 35. Limitations

<!-- slide:35 -->

**On the slide.** Eight limitations, L1 to L8.

**L1.** One generator. The hypothesis is supported for the generator tested,
not in general. This is the largest gap.
**L2.** An encyclopaedic corpus, not procedural documentation. The
contradiction detector's phenomenon is measurably absent from it.
**L3.** The long-context quality half was measured on one corpus only.
**L4.** The annotation behind the contradiction precision is model-based, not
human.
**L5.** Statistical power. Several nulls are nulls of this corpus at this
size, and they are reported with their interval widths.
**L6.** The hallucination rate on generated text is a different quantity from
the refusal rate, and the two are never substituted for one another.
**L7.** A refusal is not an answer. Per-answer accuracy cannot be compared
across arms with different coverage.
**L8.** English, and one jurisdiction. Nothing here shows the findings hold
for another language or another regulator.

**Do not rush this slide.** L1 and L2 are the two that get raised, and they
were already flagged in the text rather than waiting to be found in the
questions.

## C.36 Slide 36. Conclusion

<!-- slide:36 -->

**On the slide.** A statement of the verdict and four bullets.

**The verdict.** The framework's own hypothesis is supported under both prompt
conditions. Under a prompt that requires an answer, the fitted gate cuts the
rate from 0.938 to 0.528, at a cost of 30 of 32
answerable questions answered where the ungated arm answers
32 of 32.

**The four bullets.**

1. The confidence score buys refusal precision, not a lower answer rate. It
   spends 2 refusals on answerable questions where the random control spends
   11.
2. The benchmark's shortcut was worth more than the system. A question-only
   classifier separated the classes at ROC AUC 0.999, so the headline 91.7
   percent was an artefact. The true rate is 23.6 percent.
3. The gate detects a recognisable unanswerable question, not an absent
   answer. 23.6 percent on the hard stratum against 26 of 34 out of domain.
4. One mechanism did not survive measurement. The contradiction gate's
   precision is 0.0 percent, upper bound 16.1 percent, and it is reported as
   unproven rather than dropped.

**End on the findings, not on the architecture.** The contribution is the
measurement.

## C.37 Slide 37. Future work

<!-- slide:37 -->

**On the slide.** Nine numbered next steps.

**The list.** 1. Repeat the generator-side comparison on a generator that
returns text on the table questions; one generator settles the hypothesis for
one model. 2. Compare the gate against a token-level faithfulness monitor;
the gate is currently measured against a prompt-level control only. 3. Settle
the magnitude and the power of the positional comparison; the direction holds
in three of the four measurements, and not in the magnitude. 4. Extend the
industrial corpus beyond one jurisdiction and one language. 5. Stratify the
corpus by modality, under a pre-registered power analysis. 6. Hand-check the
repaired unanswerable class against the corpus, on both corpora. 7. Run the
long-context quality arm on a corpus that fits the context window. 8.
Replace the model-based contradiction annotators with human readers. 9.
Publish the corrected benchmark and the shortcut audit as a separate
artefact, so other work can check its own benchmarks against the same
instrument.

**Point at item 1 and item 9.** The replication is the gap that matters for
the claim, and the published benchmark is the contribution that outlives the
report.

## C.38 Slide 38. Thank you

<!-- slide:38 -->

Say thank you and stop. The benchmark repair and the shortcut audit are
published separately.

---

# Part C2. The six figures

Each figure is one measurement, plotted. A figure is the easiest thing on a
deck to misread, so each is given with what is plotted, how to read it, and
what it does not show.

## Figure 1. Recall against the candidate pool size

*Slide 17.*

<!-- figure:fig1_pool_size -->

**What is plotted.** Recall against the size of the reranker's candidate
pool, for the focus corpus in black and the industrial corpus in grey. Two
series per corpus, at Recall@10 and Recall@20.

**How to read it.** Move along the horizontal axis, which is the pool size
in chunks: 5, 10, 20, 50, 100. Move up the vertical axis, which is recall.

**What it shows.** The focus curve saturates at a pool of ten and then falls
back, while its Recall@20 keeps rising. So the gold chunk is still being
found and the reranker is pushing it out of the ten-chunk context. The
industrial curve behaves differently: its Recall@20 reaches 1.000 at a pool
of fifty while Recall@10 stays at 0.988.

**What it does not show.** It is two corpora, not the population of corpora.
The pool size of 50 used in the system is a configuration value informed by
this curve, not a result.

## Figure 2. The risk-coverage curve of the gate

*Slide 21.*

<!-- figure:fig2_risk_coverage -->

**What is plotted.** The risk-coverage curve of the confidence gate: the
fraction of queries the gate answers on the horizontal axis, and the risk,
which is the share of answered queries that had no answer in their context,
on the vertical axis.

**How to read it.** Each point is a threshold. Moving right means the gate
answers more; moving down means the answers are safer. The operating point
sits at coverage 0.693.

**What it shows.** That the trade is real and steep. The curve is the shape
of the frontier, and the sweep table on slide 20 is the same curve
discretised. Always answering is the top-right end; always refusing is the
bottom-left end.

**What it does not show.** Whether any particular point is the right point.
That is a deployment decision about what a refusal costs, and the report
gives the curve so the reader can make it.

## Figure 3. The reliability of the gate's probability

*Slide 21.*

<!-- figure:fig3_calibration -->

**What is plotted.** Two panels. The upper one plots observed answerability
against mean predicted probability, bin by bin, against the diagonal. The
lower one plots the number of queries in each bin.

**How to read it.** A perfectly calibrated gate puts every point on the
diagonal. Points above it are under-confident, points below are
over-confident. The lower panel matters as much as the upper one: a model
whose points are near the diagonal but which has almost all its queries in
one bin is calibrated by an accident of where the queries fell.

**What it shows.** The industrial gate tracks the diagonal at ECE 0.075. The
focus gate does not, and it puts most of its queries in the lowest
confidence bin. The upper panel alone would show a mismatch; the lower panel
shows why.

**What it does not show.** Any improvement. The numbers are reported as they
came out of the fit, on the held-out half (focus $n = 71$, industrial
$n = 178$).

## Figure 4. The modality quota's trade

*Slide 19.*

<!-- figure:fig4_modality_quota_pareto -->

**What is plotted.** Overall Recall@10 against table-specific Recall@10, for
the seven ablated systems, with the quota applied at three different points.

**How to read it.** Each point is a configuration. Moving up is better table
recall; moving right is better overall recall. The no-quota point is the
reference.

**What it shows.** That the quota moves one axis and gives up the other. On
the industrial corpus the pre-rerank quota buys 0.8 points of table recall
and gives up 0.8 points of overall recall, and the post-rerank quota lands on
exactly the no-quota operating point.

**What it does not show.** A winner. None of the three differences across
the three corpora is significant, so the placement is reported as a
configuration value.

## Figure 5. The question-only classifier

*Slide 14.*

<!-- figure:fig5_question_only_roc -->

**What is plotted.** The ROC curve of a classifier that is given only the
question text: no retrieval, no corpus, no evidence. The pre-repair curve
and the post-repair curve.

**How to read it.** The diagonal is a coin flip. The area under the curve is
the ROC AUC, and 0.5 is chance.

**What it shows.** Before the repair, the classifier separated the two
classes at ROC AUC 0.999 against a permutation null of 0.455 plus or minus
0.072. It was reading the answer off the question, so the benchmark's
headline refusal rate was measuring the benchmark. After the repair the same
classifier is at 0.608 on the focus corpus and 0.708 on the industrial one,
and the one-rule shortcut catches nothing.

**What it does not show.** That the repaired benchmark is easy. It shows that
the *question text* no longer carries the answer. The retrieval side of the
benchmark was never affected, because the gold chunk was always right.

## Figure 6. The contradiction detector's precision

*Slide 29.*

<!-- figure:fig6_contradiction_precision -->

**What is plotted.** The detector's precision against the base rate of real
conflicts, with 95 percent Wilson intervals.

**How to read it.** The interval is the honest part. With 20 alarms and 0
confirmed, the point estimate is zero, but the interval runs up to 16.1
percent, and the report quotes the upper bound rather than the point. A
filled marker means the branch would act; a hollow one means the findings
would be withheld.

**What it shows.** That no alarm was confirmed by readers who were blind to
the detector's scores, who agreed with each other on 101 of 101 decisions,
and who were 14 of 14 correct on a control set with known labels. On the
focus corpus the branch would not act; on the industrial corpus its
precision reaches 0.65 against a base rate of 0.35, so there it would.

**What it does not show.** That the detector can never be right. A null with
an upper bound is not a refutation, and the corpus is the reason: the
readers found no contradictions in a random sample of 80 unflagged pairs
either, so this corpus does not contain the phenomenon the mechanism
detects.

# Part D. The technicalities

The things that are true of every experiment at once, rather than of one
slide. This is the part to read on the morning of the presentation if a
question goes somewhere the deck does not reach.

## D.1 The shape of every experiment

Every measurement in this project has the same four properties, and they are
what make the numbers comparable across slides.

1. **A stated denominator.** Every rate says what it is a rate of. The
   refusal rate is a rate over the unanswerable class. The abstention
   precision is a rate over the refusals. These are different quantities and
   the deck never quotes one in place of the other.
2. **A paired comparison.** Two systems are compared on the same queries or
   the same questions, so that the difficulty of the item cancels out.
3. **One test per class.** The effect on the unanswerable class and the
   effect on the answerable class are separate tests with separate
   hypotheses, because a gate can improve the first and damage the second.
4. **A random control where the alternative is "refusing is good".** The
   random arm refuses the same number of questions as the gate and picks them
   at random. Without it, refusing on a coin flip and refusing on a
   calibrated score look identical, and the deck would be unfalsifiable.

## D.2 The splits

There are three of them, and they do different jobs.

**The calibration split.** 60 percent of the queries. The gate's weights and
its threshold are fitted here and nowhere else.

**The evaluation half.** The other 40 percent. Every calibration number in
the deck is measured here: the ECE of 0.1044, the Brier score of 0.1510,
the reliability diagram with $n = 71$ on the focus half and $n = 178$ on the
industrial half. Reporting a calibration number on the split it was fitted
on would be measuring how well the model remembers its own training data.

**The cross-category split.** For the transfer study, the six-category
corpus is split by category and the threshold fitted on one half is applied
unchanged to the other half. That is what the `rag@transferred` arm does,
and it is what makes the transfer failure a measurement rather than an
assertion.

**Why the base rate matters so much.** The gate's positive class has a base
rate of 0.182 on the focus corpus. That is, 18.2 percent of the queries
have their answer in the retrieved context. A model that always answered
"no" would be right 81.8 percent of the time. This is why a chunk-level
version of the gate failed (Part B.2 of the ten-minute companion), and it is
also why the Brier score of 0.1510 has to be read against the trivial
model's 0.182.

## D.3 The benchmark, and its repairs

The benchmark was audited before it was used, and the audit found defects.
Two of them changed the headline. The account is here in full, because "the
framework was measured on a benchmark that had to be repaired" is a claim
that needs its evidence.

**Repair 1: the answer labels.** 30 of the answerable questions carried an
answer label attached to the wrong question. Two defects in the label
generation caused it. After the repair, the defect rate is 1 of 32. The gold
chunk was always right, so the retrieval side of the benchmark was never
affected, and no retrieval result in the deck had to be recomputed.

**Repair 2: the unanswerable class.** This is the one that changed the
headline. The unanswerable half of the benchmark was separable from the
question text alone: a classifier given only the question told answerable
from unanswerable at ROC AUC 0.999, and one regular expression caught 76.4
percent of the unanswerable class with no false positives, because the class's
hard case asked about a fabricated identifier (`SKU AST-5454`) and no
answerable question ever named one.

The consequence was not that the framework was good. It was that the
headline refusal rate of 91.7 percent was an upper bound rather than a
measurement: the benchmark was easy to separate, so refusing was easy, and
the rate was reporting the benchmark rather than the framework.

The repair rebuilt the class as a **corpus-anchored** one: the same question
stems, the same source documents, the same label machinery, and every
repaired question given a **structural twin** in the answerable class. A
question that looked like the unanswerable class in every respect except that
its subject was present in the corpus. A shortcut that keys on shape cannot
separate a structural twin from its original, so the shortcut had to go.

After the repair, the shape-separability classifier scores 0.608 on the focus
corpus against a permutation null of 0.455 plus or minus 0.072, the
question-only policy scores 0.564 where 0.5 is no discrimination, and the
one-rule shortcut carries 0.0 percent. The benchmark as it stood before the
repair is kept beside the repaired one, so every before-and-after claim can
be regenerated rather than asserted.

**Repair 3: the form check.** The runtime validator refused 3 of
176 benchmark queries. All three were generator artefacts
that read as malformed rather than real questions. This is the one repair
that goes the other way: the validator was too eager on this benchmark, and
the benchmark was right.

**The audit instrument was kept rather than deleted**, because it is the
instrument that found the defects. It is one of the nine next steps to be
published separately, so that other work on RAG refusal can check its own
benchmarks against the same instrument.

**Two classifiers, two rows.** The shape-separability classifier reads the
question's shape. The question-only policy is a rule-based detector. They are
different classifiers, so the before-and-after table has a row for each, and
the figure plots the separability one. A single row that paired one
classifier's before-value with the other's after-value would describe two
classifiers at once.

## D.4 The five arms

Every arm is the full framework with exactly one thing changed.

| Arm | What it removes | What it is for |
|---|---|---|
| `rag_nogate` | the gate, keeping retrieval | the baseline: what happens if nothing refuses |
| `rag@fitted` | nothing | the framework at its fitted operating point |
| `rag@random` | the confidence score, keeping the refusal budget | the control: is it the score or the refusing? |
| `rag@transferred` | the fitted operating point; the threshold is moved across corpora | does a calibrated threshold travel? |
| `long_context` | retrieval; the whole corpus goes in the prompt | is the machinery necessary at all? |

Two of these deserve comment.

**`rag@random` is the arm that makes the central finding possible.** It
refuses the same number of questions as the gate, chosen at random. It
reaches 0.604 on the unanswerable class, against the gate's 0.528, and the
ungated arm's 0.938. On its own that looks like the gate is worse than
random. But on the answerable class the gate spends 2 refusals and the random
control spends 11, and that difference is the finding: the score decides
*where* the refusals land.

**`long_context` is the arm that makes the machinery's necessity arguable.**
It answers 32 of 32 answerable questions, the same as
the ungated pipeline, and it costs 74 times the tokens and 58.8 times the
money. The report does not claim the retrieval machinery is cheaper in
absolute terms; it claims the cost ratio, and it claims the cost because the
corpus does not fit in a context window for one of the two corpora.

## D.5 The two prompt conditions

The generator's instruction is an experimental axis here, not a fixed
setting. The two conditions differ by a single sentence: under one the
generator may decline, and under the other it must answer. Model,
questions, retrieval, scorer and temperature are identical either way.

**Why two conditions were needed.** Under the cautious prompt alone, the
generator refused most unanswerable questions by itself. The gate's refusals
were then largely redundant, and the arms could not have been told apart. The
answering condition is the one in which the gate can be seen doing work that
nothing else was doing.

**The verdict is claimed under both.** Under the cautious prompt the rate
falls from 0.535 to 0.417, at the cost of the same two answerable questions,
and the paired test is significant under both conditions.

**The third outcome.** MiniMax-M3.1-Flash returned no text on 24 of 66
questions. Raising the output budget fourfold rescued 13 and left 11 empty.
An empty completion is neither an answer nor a refusal, so that run is
recorded as not run, with the reason. A rate quoted from a run that did not
happen is indistinguishable from a rate that did.

## D.6 The statistics

**Which test for which comparison.** Retrieval comparisons use the Wilcoxon
signed-rank test on paired differences, because the differences are not
normally distributed and the test uses their ranks rather than their sizes.
Generation comparisons use the exact McNemar test, because the outcome is
binary and only the disagreements carry information. Effect sizes are
reported alongside: Cliff's delta and Cohen's $d_z$ for the retrieval
comparisons, and the raw counts $b$ and $c$ for the generation ones.

**What a null means here.** A null is read as no difference established
here, and it is reported with its interval width rather than dropped. Three
of the deck's results are nulls, and each is reported with what would be
needed to move it: the quota placement (three corpora, three p-values of
0.157, 0.480 and 0.317), the contradiction detector (0 out of 20, upper
bound 16.1 percent), and the answer position effect (three of four
measurements in the same direction, the fourth tied).

**Why the answer position effect is not a finding.** The direction replicates
in three of the four corpus-and-protocol measurements and ties in the fourth.
The magnitude does not replicate. A finding is a rule that holds, and a
direction that holds in three measurements out of four with a magnitude that
does not hold is stated with its magnitude, not as a rule.

**Why Wilson intervals.** For a proportion with a small count, the naive
interval is badly behaved at 0 and at 1. The Wilson interval stays sensible,
which is what makes the 0-out-of-20 result reportable as an interval rather
than as a bare zero.

**The base rate of real conflicts.** A detector's precision means nothing
without the base rate of the thing it detects. If the corpus contains no
real conflicts, then every alarm is a false alarm, and the detector's
precision is zero by construction. That is what slides 28 and 29 establish,
and it is why the finding is a statement about the corpus as much as about
the detector.

## D.7 The objectives, and where each one is answered

The deck's slide 4 states four objectives. Each has a slide that answers it,
and it is worth knowing which.

| Objective | Answered on |
|---|---|
| RO1, build an evidence-grounded framework | Slides 6, 7, 8, 9, and the whole deck |
| RO2, modality-balanced and category-aware retrieval | Slides 7, 15, 18, 19 |
| RO3, test the framework's own hypothesis | Slides 22, 23, 24, 25 |
| RO4, characterise the failure modes | Slides 11, 12, 13, 28, 29, 30, 32, 34, 35 |

**RO4 is the objective that distinguishes this project.** A framework report
that only reported what worked would be a smaller claim. What is here is a
failure-mode characterisation with the error rates of the measuring
instruments published alongside it: the benchmark's own defect (slides 11 to
13), the contradiction detector's null (28 and 29), the second generator's
empty completions (30), and the attribution gap that turns out to be a
retrieval problem rather than a scoring one (32).

## D.8 The prior art, and what is new

Every mechanism in the framework is published. The deck names five of them
with their citations: hybrid retrieval and reciprocal-rank fusion
(Karpukhin et al. 2020; Cormack et al. 2009), selective prediction through a
calibrated gate (Yadkori et al. 2024), and the rest of the components that
the report's literature review covers.

**The closest prior art is HALT-RAG (Goswami and Kurra 2025),** and the
distinction is worth having ready. HALT-RAG is a post-hoc output verifier:
it reads what the generator produced and checks it afterwards. It never runs
a generator, and it never decides not to call one. The step this report
performs is deciding whether to generate at all, in code, before the model is
invoked. HALT-RAG's own future work names that step.

**So what is new.** The assembly into one industrial system; the evaluation
at the level of the individual answer claim rather than the answer; and the
audit and repair of the benchmark the measurement rests on. A committee that
wants to know which component is new will find that none of them is, and a
candidate who says so before being asked is making a stronger claim than one
who claims otherwise.

## D.9 What is claimed, and what is not

**Claimed.** That a code-level gate, placed before the generator, can refuse
queries the retrieved evidence cannot answer, and that at its fitted
operating point on the focus corpus it refuses with a precision of 0.963.
That the refusals concentrate on the class that should be refused, which the
random control establishes. That the hypothesis holds under both prompt
conditions for the generator tested.

**Not claimed.** That the gate reduces hallucination on generated text; the
hallucination rate and the refusal rate are different quantities and are
never substituted for one another. That the score lowers the answer rate on
unanswerable questions; the random control reaches 0.604 against the gate's
0.528. That a per-answer accuracy comparison between arms is meaningful when
the arms have different coverage. That the framework is better than BM25 on
recall on the focus corpus, where it is not. That the contradiction detector
does not work, which is a different claim from saying its precision was not
established. That a calibrated threshold transfers across corpora, which it
demonstrably does not. That any of this holds for a generator other than the
one tested.

## D.10 Reproducibility and provenance

**Every number is a measurement against an archived result file.** The
figures are regenerated from the result files, and the build fails if a
figure is older than the results it draws. The caption of a figure and the
number it carries are checked against each other, because a caption that
disagrees with its own figure is worse than no caption.

**The corpus ships with its provenance.** For every document the manifest
gives the source URL, the upstream revision it was read at, the SHA-256 of
the exact bytes used, and its chunk count. The licence for the article text
is stated. The primary corpus of proprietary supply chain documents cannot be
redistributed, so it cannot be shipped or re-run by a reader, and the report
says so wherever the substitute matters.

**The audit instruments are kept.** The benchmark as it stood before the
repair sits beside the repaired one. The earlier encoder's numbers are kept
as tokens, so both sides of the comparison that changed the architecture rest
on measured values rather than recollection.

**What this buys the reader.** Any claim in the deck can be checked against
an archived result rather than taken on trust. That is the standard the
project holds itself to, and the reason three of the deck's findings are
about the project's own instruments rather than about the framework.

---

## D.11 One page of numbers to have in mind

| If you are asked about | Say this number |
|---|---|
| The gate's precision where it refuses | 0.963 abstention precision at tau of 0.05 |
| What the score buys | 2 refusals on answerable against 11 for the random control |
| The benchmark's own shortcut | ROC AUC 0.999, one regular expression at 76.4 percent |
| The honest refusal rate | 23.6 percent, 26 of 110 on the hard stratum |
| The contradiction gate | 0.0 percent precision, 20 alarms, upper bound 16.1 percent |
| Long context cost | 74x the tokens, 58.8x the money |
| The generator limitation | no text on 24 of 66 questions |
| The reranker | -0.3 points on focus, +11.1 points on six-category |
| The gate's calibration | ECE 0.1044, Brier 0.1510, base rate 0.182 |
| The threshold's cost | coverage 0.693 at tau of 0.05, 0.432 at tau of 0.10 |
