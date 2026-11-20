---
title: "The Ten-Minute Deck, Explained"
subtitle: "Every formula, every term and every measurement behind the ten-minute defence deck"
author: "Ritik Raj (25IM60R12), Department of Industrial and Systems Engineering, IIT Kharagpur"
date: ""
shorttitle: "The deck, explained"
---
# How to use this companion

This document explains the ten-minute deck, slide by slide. It is written to
be read beside the deck, not instead of it: the deck is what the audience
sees, and this is what makes the deck legible to you.

**What is in it.** Four parts. Part A is the vocabulary, every term the deck
uses in plain words with the slide it appears on. Part B is the thirteen
formulas, each typeset with every symbol named, a reading in ordinary words,
the job it does here, and the caveat that comes with it. Part C is the
slides and the six figures, in order. Part D is the protocol behind the
numbers: the splits, the benchmark and its repairs, the five arms, the
statistics, and the boundary of what is claimed.

**How to use it before you present.** Read Part A once, quickly, so that no
word on a slide is unfamiliar. Then read Part B for slides 4, 5, 6, 8, 12
and 15, which are the ones carrying the formulas, and skim the rest. Part C
is the slide-by-slide version of what the speaker script already says, with
the measurement behind each slide added. Part D is the one to read on the
morning of the presentation if a question goes somewhere the script does not
reach.

**The pictures.** Each slide is printed above its explanation, and each
measured figure is printed where it is explained. The slide pictures are
drawn from the deck file itself, so they show the shape of the slide exactly
as it is, with one caveat: they are drawn by this project's own renderer
rather than screenshotted from PowerPoint, so a word may sit a fraction
differently in the picture than it will on the screen. The layout, the
tables, the figures and the numbers are the same.

**What this document does not do.** It does not replace the report. The
report carries the derivations, the citations, the appendix-free full text
and the numbers behind every row of the findings table. Where this document
says a number, that number is the one on the slide; where the report says
more, this document says where to look.

# Part A. The terms

Every term the deck uses, in plain words, with the slide it appears on. The
deck can be read in ten minutes and the terms can be looked up here. Nothing
in this part is a claim; it is the vocabulary.

## A.1 The machinery

RAG (retrieval-augmented generation)
:   A generator that is given text to answer from, instead of answering from
    what it memorised. The framework in this report is RAG with a gate in
    front of the generator: the retrieved text is checked before the
    generator is allowed to see it. **Slide 2.** The phrase that matters is
    "in front of". A gate that sits after generation is a filter on output; a
    gate that sits before it is a decision about whether to spend a model
    call at all.

Corpus
:   The set of documents the system is allowed to read. **Slide 2.** The
    corpus in this work is a public substitute for the department's
    proprietary supply chain corpus, and the report says so wherever it
    matters.

Chunk
:   A piece of a document, of a size a retriever can return and a generator
    can read. The focus corpus carries 735 chunks from
    14 documents. **Slides
    7, 11.**

Retrieval
:   Finding the chunks that might contain the answer. **Slide 4.** The
    framework uses two retrieval methods at once, which is what "hybrid" means.

Lexical retrieval, and BM25
:   Retrieval by word overlap. BM25 is the standard scoring function for it:
    a term's inverse document frequency, times a saturated frequency factor.
    **Slide 4.** The full formula is in Part B.

Dense retrieval
:   Retrieval by meaning. Each chunk and each query is turned into a vector of
    numbers, and the chunks whose vectors point in the same direction as the
    query's are returned. **Slide 4.** It reads well and, on this corpus, it
    was measurably worse than BM25. That is why the encoder was replaced.

Embedding
:   The vector a chunk or a query is turned into. The encoder used here is
    BAAI/bge-m3, which produces 1024-dimensional vectors that are L2
    normalised, so their length is fixed and only their direction carries
    information. **Slide 4.**

Dense leg, lexical leg
:   The two halves of hybrid retrieval: the BM25 half and the embedding
    half. **Slide 4.** "Leg" is used because the two are run in parallel and
    then joined.

Fusion
:   Joining the two ranked lists into one list. **Slide 4.** The method used
    is reciprocal rank fusion, which needs no score calibration between the
    two legs, only their ranks.

RRF (reciprocal rank fusion)
:   A fusion rule: a chunk's fused score is the sum, over the lists it
    appears in, of one divided by a constant plus its rank in that list. A
    chunk missing from a list contributes nothing. **Slide 4.** The formula is
    in Part B.

Candidate pool
:   The list of chunks the reranker gets to choose from. **Slides 4, 11.**
    The pool here is 50 chunks, built from the top 20 of each leg. The report
    shows what happens when the pool is made larger.

Reranker, cross-encoder
:   A model that reads the query and a chunk together and scores how well
    they answer each other. It is more accurate than a bi-encoder, which
    scores them separately, and much slower, so it runs on the shortlist
    rather than the whole corpus. **Slides 4, 9.**

Modality quota
:   A floor on how many chunks of a non-text kind (a table, a chart) must be
    in the final context. **Slides 4, 10.** A floor, not a ceiling: it puts
    a lower bound on tables and charts and no upper bound on text.

Floor, and relaxation
:   The quota is a minimum, and when the candidate pool cannot supply it the
    minimum is relaxed rather than invented. **Slide 4.** A floor that
    silently becomes a ceiling is a different mechanism wearing the same
    name.

Category pre-filter
:   A check that removes chunks from categories the question cannot be about,
    applied to both legs before fusion. **Slide 4.** One of three invariants:
    things that are asserted in the code rather than assumed.

Invariant
:   A property the code asserts about itself, which a test can check. **Slide
    4.** Three are asserted here, and three real defects were found by
    asserting them, none of which was visible in the output.

Confidence gate
:   The component that decides whether the retrieved evidence actually
    contains the answer, before the generator is called. **Slides 3, 5.** It
    is the mechanism this report is about.

Posterior
:   The gate's calibrated estimate that the answer is in the context. It is a
    probability, not a score, and the distinction is what makes a threshold
    on it meaningful. **Slide 5.**

Feature vector
:   The five numbers the gate reads about the whole retrieved pool. **Slide
    5.** The gate is query level: the features describe the query's pool as a
    whole, not any one chunk.

Platt scaling
:   Fitting a logistic model on top of an existing score so that its output
    is a probability. **Slide 5.** The weights are fitted by maximum
    likelihood on a calibration split.

Maximum likelihood
:   The standard way of fitting a model: choose the parameters that make the
    observed data most probable under the model. **Slide 5.**

Calibration split
:   The part of the data the gate's weights are fitted on. **Slide 5.** Here
    60 percent of the queries. The other 40 percent is the evaluation half,
    and the calibration numbers are reported on the evaluation half, not on
    the split they were fitted on.

Standardisation
:   Subtracting the mean and dividing by the standard deviation of each
    feature, so that no feature dominates the logistic model purely by being
    measured on a larger scale. **Slide 5.** It appears in the posterior
    formula.

Threshold, and operating point
:   The cut-off on the posterior, and the particular cut-off the gate is run
    at. **Slides 5, 13.** The operating point here is tau = 0.05, and it was
    chosen by a stated rule rather than by taste.

Abstention, refusal
:   The gate declining to answer, so the generator is never called. **Slide
    3.** "Abstention" and "refusal" are the same thing here.

Answer-in-context detectability
:   The positive class of the gate: the answer is in the context. It is
    defined operationally as the gold chunk being present in the reranked
    candidate pool. **Slide 5.** The report does not call this "sufficiency",
    because the literature reserves that word for a set-level property that
    is not what is being measured.

Gold chunk
:   The chunk the benchmark says contains the answer. **Slides 5, 14.** It is
    the target of retrieval and the reference for everything else.

Contradiction gate
:   A second component that refuses, this time when two retrieved chunks
    contradict each other. **Slide 6.** It needs two independent branches to
    agree before it alarms.

NLI (natural language inference)
:   A model that is given two statements and judges whether they contradict.
    **Slide 6.** This one is used at a threshold of 0.70.

Form validator
:   A runtime check that a query is shaped like a question before anything
    else happens. **Slide 6.** It refused 25 of 25 hand-authored malformed
    queries and 0 of 35 well-formed ones, at 2.6 microseconds per query.

Malformed stem
:   A query that is not shaped like a question, such as a bare fragment. **Slide
    6.** The form validator's job.

Counterfactual
:   What would have happened under a different choice that was available and
    was not taken. **Slide 6.** The memorable one: the benchmark builder's own
    question-generation rule, used as a runtime check, would have refused
    100.0 percent of hand-labelled well-formed questions.

False rejection rate
:   The share of good inputs a filter wrongly turns away. **Slide 6.** It is
    the number that decides whether a filter is safe to ship.

Claim
:   One assertion in a generated answer. **Slide 20.** Every claim is scored
    against the evidence it was shown.

Entailment
:   A statement being supported by the evidence, as judged by an NLI model.
    **Slides 17, 20.** A claim counts as supported when a chunk entails it at
    a threshold of 0.5, or when the evidence states it literally.

Grounded, inferred, uncertain claim
:   Three bands a claim is put in by its confidence score. **Slide 20.** 0.80
    separates a grounded claim from 0.45 for an inferred one, and anything
    below is uncertain.

Non-bypassability
:   The property that the generator cannot be reached without passing the
    gate. **Slide 3.** Here it is a property of the code, not a convention
    the caller is trusted to follow: the generator is injected into the
    framework and called at exactly one line.

Comparison arm
:   A version of the system run without part of it, so that the part can be
    measured. **Slides 3, 15.** The arms are named in Part D.

## A.2 The measurements

Recall@k
:   The share of the queries for which the right chunk appears in the top k
    results. **Slides 8, 9.** It says whether the answer was found, and
    nothing about where it was placed.

MRR (mean reciprocal rank)
:   The average, over the queries, of one divided by the rank of the right
    chunk. **Slides 8, 9.** It says how high up the answer was, so a system
    that finds the answer but buries it loses on MRR and ties on recall.

nDCG (normalised discounted cumulative gain)
:   A ranking measure that rewards the right chunk being high, and
    normalises against the best possible ordering. **Slides 8, 9.** It is
    the third retrieval number here because it is the one that notices a
    reordering that recall cannot.

DCG (discounted cumulative gain)
:   The sum of each result's relevance divided by the log of its position, so
    that a relevant result further down counts for less. **Slide 8.** The
    logarithm is the discount.

IDCG
:   The DCG of the best possible ordering of the same results. **Slide 8.**
    nDCG is DCG divided by this, which is what makes it comparable across
    queries with different numbers of relevant results.

Inverse document frequency (IDF)
:   How rare a term is across the corpus, on a logarithmic scale. **Slide 4.**
    A term in every document carries no information and scores zero rather
    than a negative number.

Base rate
:   The share of the data in the positive class before anything is predicted.
    **Slide 12.** The gate's positive class has a base rate of 0.182, so a
    model that always answered "no" would be right 81.8 percent of the time.
    This is why the chunk-level version of the gate failed.

Calibration
:   Whether a stated probability matches the observed frequency of the
    outcome. **Slide 12.** A model can rank well and be badly calibrated.

ECE (expected calibration error)
:   The average, over the probability bins, of the gap between the mean
    predicted probability in the bin and the observed frequency in that bin,
    weighted by how many queries are in it. **Slide 12.** Zero is perfect
    calibration.

Brier score
:   The mean squared difference between a stated probability and the outcome.
    **Slide 12.** Lower is better, and it punishes confident mistakes harder
    than vague ones.

Reliability diagram
:   A plot of observed frequency against predicted probability, with the
    diagonal as the target. **Slide 12.** A model that tracks the diagonal
    is calibrated.

Held-out evaluation half
:   The part of the data that was not used to fit anything. **Slide 12.** Every
    calibration number in the report is measured there.

Abstention precision
:   Of the queries the gate refused, the share that genuinely had no answer.
    **Slides 13, 21.** This is the number a practitioner needs, and it is
    the one the report's central claim rests on.

Coverage
:   The share of queries the system answers rather than refuses. **Slide 13.**
    Every extra refusal is paid for in coverage.

Risk-coverage curve
:   The trade between how many queries are answered and how often an answered
    query has no answer in its context. **Slide 13.** The threshold sweep in
    the report is the same curve in table form.

Frontier
:   The set of points a system can reach, and the boundary of it. **Slide
    13.** The report shows the whole frontier rather than one point on it.

ROC AUC
:   The area under the curve of true positive rate against false positive
    rate, over every possible threshold. **Slide 14.** 0.5 is a coin flip, 1.0
    is perfect separation.

Shortcut
:   A feature that predicts the label without the thing the benchmark is
    supposed to test. **Slide 14.** Here a single regular expression
    separated the two classes, which is why the headline refusal rate was
    reporting the benchmark rather than the framework.

Stratum
:   A subpopulation the results are broken down into. **Slide 14.** Two
    strata matter: the hard stratum, where the corpus discusses the subject
    but does not state the answer, and the out-of-domain stratum, where the
    question comes from outside the corpus entirely.

Out-of-domain
:   A question about something the corpus does not cover at all. **Slide 14.**
    It is the easier half of the unanswerable class, and the gate does better
    on it.

Structural twin
:   A question built to look like the other class in every respect except the
    one that matters. **Slide 14.** Every repaired unanswerable question was
    given a twin in the answerable class, so a shortcut that keys on shape
    cannot separate them.

Precision of a detector
:   Of the times a detector fires, the share of times it is right. **Slide
    19.** A detector that fires rarely has a wide interval on its precision,
    and 0 out of 20 alarms is a null with an upper bound of 16.1 percent, not
    a statement that the detector can never be right.

95 percent upper bound
:   The largest value the true quantity could plausibly be, at 95 percent
    confidence, given what was observed. **Slide 19.** It is how a null is
    reported without pretending to know more than the data allows.

Wilson score interval
:   The interval used for a proportion when the count is small. **Slides 8,
    19.** It stays sensible at 0 out of 20, where the naive interval does
    not.

Paired test
:   A test that compares two systems on the same items, so that the item's
    own difficulty cancels out. **Slide 8.** Every comparison here is paired,
    because the arms answer the same questions.

Wilcoxon signed-rank test
:   The paired test used for the retrieval comparisons. **Slide 8.** It uses
    the rank of the differences rather than their size, so one wild
    difference cannot dominate.

Cliff's delta
:   An effect size that says how often one system beats another, as a number
    between minus one and one. **Slide 8.** It does not assume the size of
    the differences are normal.

Cohen's dz
:   An effect size measured in standard deviations of the paired difference.
    **Slide 8.** It does assume the differences are roughly symmetric.

McNemar test
:   The paired test for two outcomes, used for the generation comparisons.
    **Slides 8, 16.** It counts the questions where the two systems
    disagreed, and only those.

b and c
:   In McNemar's table, b is the number of questions the baseline answered
    and the arm refused, and c is the number where the baseline refused and
    the arm answered. **Slide 8.** Only b and c matter, and the test asks
    whether the disagreement is lopsided.

Exact test
:   A test that computes the probability of what was observed under the null
    hypothesis directly, rather than approximating it with a formula. **Slide
    15.** The McNemar p-value here is exact, which matters at these counts.

p-value
:   The probability of seeing a result at least this extreme if the null
    hypothesis were true. **Slide 8.** It is not the probability that the null
    hypothesis is true.

Null result
:   A result that establishes no difference. **Slides 10, 19.** The report
    reads a null as no difference established here, and reports nulls with
    their interval widths rather than dropping them.

Effect size
:   How large a difference is, as opposed to whether it is distinguishable
    from zero. **Slide 8.** A difference can be significant and trivial.

Random control
:   An arm that refuses the same number of questions as the gate, but picks
    them at random. **Slides 8, 15, 17.** Without it, refusing on a coin
    flip and refusing on a calibrated score look identical.

Selection effect
:   Comparing two systems on the subset each of them answered, which is not
    the same set of questions. **Slide 17.** It is why per-answer accuracy
    cannot be compared across arms with different coverage.

Per-answer accuracy
:   The share of the answers that were right, among the questions that were
    answered at all. **Slide 17.** It is a coverage-dependent quantity, and
    the gated arm's answers are easier by construction.

Length-controlled re-scoring
:   Scoring the same answers again with the length taken out of the
    comparison. **Slide 18.** It is how the quality half of the long-context
    comparison is made fair.

Cached pricing
:   A provider's lower rate for input tokens already seen in an earlier
    request. **Slide 18.** 33.0 percent of the long-context arm's tokens were
    cache reads, which is why the money ratio and the token ratio differ so
    much.

## A.3 The experimental vocabulary

Prompt condition
:   The instruction the generator is given. **Slides 15, 16.** Two are used,
    differing by a single sentence: under one the generator may decline,
    under the other it must answer.

Empty completion
:   The generator returning no text at all. **Slide 15.** It is neither an
    answer nor a refusal, and it is recorded as a third outcome.

Cautious condition, answering condition
:   The two prompt conditions. **Slide 16.** The verdict is claimed under
    both.

Arm
:   One version of the pipeline in a comparison. **Slide 15.** Five of them,
    listed in Part D.

Fit, transfer, and the fitted operating point
:   Fitting the gate's threshold on one half of one corpus and applying it
    unchanged to another. **Slide 16.** It is the transfer arm, and it is how
    the report shows a calibrated threshold does not travel.

Reproducibility, provenance
:   Keeping the inputs, the seeds and the results, so a number can be
    regenerated. **Slide 7.** Every row of the findings table is a
    measurement against an archived result file.

# Part B. The formulas

Thirteen formulas appear on the deck. Each is given here as it is on the
slide, with every symbol named, a reading in ordinary words, the job it does
in this project, and the caveat that comes with it.

Two conventions worth stating once. An indicator function $\mathbf{1}[\cdot]$
is 1 when the condition inside the brackets is true and 0 when it is false.
$\mathbb{E}[\cdot]$ means the average of a quantity over a set.

## B.1 Okapi BM25

*Slide 4, top left.*

$$
\mathrm{BM25}(q,d)=\sum_{t\in q}\mathrm{IDF}(t)\cdot
\frac{f_{t,d}(k_1+1)}{f_{t,d}+k_1\left(1-b+b\frac{|d|}{\mathrm{avgdl}}\right)}
$$

| Symbol | What it is | Value or form here |
|---|---|---|
| $q$ | the query | the user's text |
| $d$ | a document, here a chunk | one candidate chunk |
| $t$ | a term in the query | each query word in turn |
| $\mathrm{IDF}(t)$ | inverse document frequency of $t$ | how rare $t$ is in the corpus, on a log scale |
| $f_{t,d}$ | how many times $t$ occurs in $d$ | a count |
| $\vert d\vert$ | the length of $d$ | in tokens |
| $\mathrm{avgdl}$ | the average chunk length in the corpus | a constant of the corpus |
| $k_1$ | how quickly the frequency factor saturates | 1.2 |
| $b$ | how strongly long chunks are penalised | 0.75 |

**In plain words.** For each word of the query, multiply how rare that word
is by how much of it this chunk contains, with a correction that stops a word
repeating in one chunk from counting forever and stops a long chunk from
winning just by being long. Add up over the query's words.

**The two knobs.** $b = 0$ means chunk length is ignored and only word
overlap counts. $b = 1$ means a chunk has to be about as dense as the average
one to score well. $k_1$ controls the saturation: at $k_1 = 0$ the frequency
factor is simply 1 and a word appearing once counts as much as a word
appearing fifty times; $k_1 = 1.2$ is the standard setting and was used here.

**What it is used for here.** It is the lexical leg of retrieval, and it is
the only part of the pipeline that is a textbook component. The report says so
plainly: every component of this framework has published prior art, and the
contribution is not the architecture.

**The caveat.** The IDF here is the Robertson-Sparck-Jones variant with a plus
one offset, so a term appearing in every document scores exactly zero rather
than a negative number. If somebody asks why a term that appears everywhere
contributes nothing rather than something harmful, that is the reason.

## B.2 Reciprocal rank fusion

*Slide 4, top right.*

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
The deck says this in those words.

## B.3 The modality quota

*Slide 4, left, under BM25.*

$$
q_m=\min\left(n_m,\left\lceil \alpha_m \lvert\mathcal{C}\rvert\right\rceil\right),
\qquad \alpha_{table}=0.15,\quad \alpha_{chart}=0.05
$$

| Symbol | What it is | Value or form here |
|---|---|---|
| $q_m$ | the quota for modality $m$ | a number of chunks |
| $n_m$ | how many chunks of modality $m$ the pool can supply | a count |
| $\alpha_m$ | the share of the context that modality $m$ should get | 0.15 for tables, 0.05 for charts |
| $\lvert\mathcal{C}\rvert$ | the size of the candidate pool | 50 |
| $m$ | a modality | text, table, or chart |

**In plain words.** Work out the share of the pool that tables or charts
should occupy, round it up to a whole number of chunks, and then take the
smaller of that number and how many such chunks actually exist. The result
is the number of table or chart chunks that must be in the final context.

**It is a floor, not a ceiling.** Nothing in this formula limits text. The
quota says "at least this many tables", and text takes whatever is left.
This is the single most common misreading of a quota, and the deck names it
out loud.

**Why the minimum is there.** If the pool cannot supply the floor, the floor
is relaxed rather than invented. A quota that quietly became a ceiling when
the pool was thin would be a different mechanism under the same name, and it
would be measuring the pool rather than the quota.

**The caveat.** The placement of the quota, before or after the reranker, is
not settled by measurement. Slide 10 shows three corpora and three
non-significant differences, so the report states the placement as a
configuration value and reports the ranking with its corpus attached.

## B.4 The gate's feature vector

*Slide 5, top left.*

$$
\phi(q)=\left[s^{(1)}_{rerank},\;\bar{s}^{(3)}_{rerank},\;s^{(1)}_{bm25},\;
\max_d S_{RRF}(d),\;\left\lvert\left\{d\in\mathcal{C}: s_{rerank}(d)>\beta\right\}\right\rvert\right]
$$

| Symbol | What it is | Value or form here |
|---|---|---|
| $\phi(q)$ | the feature vector of query $q$ | five numbers |
| $s^{(1)}_{rerank}$ | the reranker's top score | the best cross-encoder score in the pool |
| $\bar{s}^{(3)}_{rerank}$ | the mean of the reranker's top three scores | an average |
| $s^{(1)}_{bm25}$ | the top BM25 score | the best lexical score in the pool |
| $\max_d S_{RRF}(d)$ | the best fused score | the top of the fused list |
| $s_{rerank}(d)$ | the reranker's score for chunk $d$ | a score |
| $\beta$ | the reranker's relevance bar | a threshold on that score |
| $\lvert\{\cdot\}\rvert$ | the size of a set | a count |

**In plain words.** Five numbers describing the query's retrieved pool as a
whole: how well the best chunk scores, how well the best three score on
average, how well the best lexical match scores, how well the best fused
match scores, and how many chunks clear the reranker's own relevance bar.

**The level matters, and it is the point of the slide.** Every feature
describes the pool, not any single chunk. There is one gold chunk among
about fifty candidates, so a chunk-level classifier is right 98 percent of the
time by answering "nothing is relevant here". Maximum likelihood fitting
dutifully returns a large negative intercept: a degenerate solution that
looks like a fitted model and behaves like a constant. Calibrating at the
query level removes it.

**The caveat.** The features are summaries of the pool, so the gate cannot
tell a pool containing one strong answer from a pool containing four
mediocre ones. That is a deliberate simplification: the alternatives need
more labelled data than this project had.

## B.5 The calibrated posterior

*Slide 5, top right.*

$$
p_{conf}(q)=\sigma\left(\beta_0+\boldsymbol{\beta}_1^{T}
\frac{\phi(q)-\boldsymbol{\mu}}{\boldsymbol{\sigma}}\right),
\qquad \sigma(z)=\frac{1}{1+e^{-z}}
$$

| Symbol | What it is | Value or form here |
|---|---|---|
| $p_{conf}(q)$ | the gate's probability that the answer is in the context | a number in $[0,1]$ |
| $\sigma(z)$ | the logistic function | squashes any real number into $[0,1]$ |
| $\beta_0$ | the intercept | fitted |
| $\boldsymbol{\beta}_1$ | the weight on each feature | fitted, one per feature |
| $\boldsymbol{\mu}$ | the mean of each feature | the calibration split's means |
| $\boldsymbol{\sigma}$ | the standard deviation of each feature | the calibration split's standard deviations |
| $\boldsymbol{\beta}_1^{T}$ | the transpose, so the vectors multiply | a dot product |
| $\phi(q)$ | the feature vector | five numbers |

**In plain words.** Standardise the five features, weight them and add them
to a constant, and squash the result through the logistic function. What
comes out is a probability: the chance that the answer is in the retrieved
context.

**Platt scaling.** This is Platt's method: take an existing score, fit a
logistic model on top of it so that the output is a probability, and fit it by
maximum likelihood on a held-out split. The weights are fitted on 60 percent
of the queries; the calibration numbers in the report are measured on the
other 40 percent.

**Why standardisation.** Without it, a feature measured on a larger scale
would dominate the weighted sum purely because of its units, and the fit
would have to work harder to undo that.

**The caveat, and it is a real one.** An ECE of 0.1044 is reported rather
than improved by refitting. It is the calibration of one fitted artefact on
one fixed split. The industrial gate tracks the diagonal at ECE 0.075; the
focus gate does not, and it puts most of its queries in the lowest confidence
bin.

## B.6 The decision rule

*Slide 5, below the feature vector.*

$$
\mathrm{accept}(q)=\mathbf{1}\left[p_{conf}(q)\ge\tau\right]
$$

| Symbol | What it is | Value or form here |
|---|---|---|
| $\mathrm{accept}(q)$ | whether the query is passed to the generator | 1 or 0 |
| $p_{conf}(q)$ | the calibrated probability | from B.5 |
| $\tau$ | the threshold, the operating point | 0.05 |
| $\mathbf{1}[\cdot]$ | the indicator function | 1 if true, 0 if false |

**In plain words.** If the probability is at least the threshold, answer.
Otherwise refuse, and do not call the generator at all.

**Why the threshold is 0.05.** It was chosen by a stated rule, not by taste:
the highest threshold that still answers at least 90 percent of the answerable
queries. Slide 13 shows the whole sweep, because a single threshold hides
the shape of the frontier behind it.

**The cost.** Every extra refusal is paid for in coverage, and the price
climbs steeply past $\tau = 0.15$. At $\tau = 0.05$ the coverage is 0.693 and
the abstention precision is 0.963. At $\tau = 0.50$ the coverage is 0.097 and
the abstention precision is 0.868. Both are defensible; they are not the same
product.

**The caveat.** A threshold is a policy, not a property of the model. It
belongs to a deployment, and a deployment team would have to calibrate it on
its own corpus.

## B.7 The contradiction gate

*Slide 6, across the top.*

$$
\mathrm{contradiction}(c_1,c_2)=\mathbf{1}\left[\mathrm{NLI}(c_1,c_2)=\mathrm{contradiction}\right]
\wedge\mathbf{1}\left[\mathrm{shared\ measurement}\wedge\mathrm{shared\ instance}\right]
$$

| Symbol | What it is | Value or form here |
|---|---|---|
| $c_1, c_2$ | two retrieved chunks | any pair from the context |
| $\mathrm{NLI}(c_1,c_2)$ | a natural language inference model's judgement | a label: entailment, neutral, or contradiction |
| $\mathrm{shared\ measurement}$ | the two chunks discuss the same measured quantity | the same limit, the same tolerance, the same threshold |
| $\mathrm{shared\ instance}$ | ...of the same instance | the same substance, the same part, the same regulation |
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

**The distinguishing detail.** "Same measured quantity" is not "same topic".
Two chunks that both discuss occupational exposure limits are on the same
topic. Two chunks that both state a limit for the *same substance* are
discussing the same measured quantity. The second is much the narrower test,
and it is the one that stops the detector from crying wolf.

**The caveat, and it is the sharpest in the deck.** The precision of this
detector against reader labels is 0.0 percent. Slide 19 reports it as a null
with a 95 percent upper bound of 16.1 percent, not as a defect to be
explained away. The mechanism is unproven rather than disproven, and the
reason is in Part D.

## B.8 The retrieval metrics

*Slide 8, across the top.*

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
| $\mathrm{DCG}@k$ | the discounted gain of the top $k$ | from B.10 |
| $\mathrm{IDCG}@k$ | the discounted gain of the best possible ordering | the ceiling |

**In plain words.** Recall asks whether the answer was found at all. MRR
asks how high up it was. nDCG asks the same as MRR but weighted by
relevance and normalised, so that two systems can be compared on queries
with different numbers of relevant results.

**Why three.** They fail in different ways, and the ablation needs all three
to say anything. A system can find every answer and bury it (recall ties, MRR
loses). A system can find fewer answers but rank them better. Reporting only
recall would have made the reranker look worthless, and only MRR would have
hidden that a configuration lost answers.

**The caveat.** Recall@10 on a benchmark whose gold chunk is in the pool is
measured on the pool, not on the corpus. That is why the report also reports
the retriever's recall of the gold separately, and why the long-context
comparison is settled on cost and coverage.

## B.9 The answer rate and the abstention precision

*Slide 8, second row, left.*

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
and be useless, which is why the sweep on slide 13 reports coverage next to
it.

**Why the second one is the claim.** A practitioner wants to know: when this
system says it does not know, is it right? That is exactly
$\mathrm{Prec}_{ref}$, and it is 0.963 at the fitted operating point.

**The caveat.** The two are reported separately per class, never pooled. A
gate can improve the unanswerable class and damage the answerable class at
the same time, and one number for both would hide the trade.

## B.10 Discounted cumulative gain

*Slide 8, second row, right.*

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

## B.11 Expected calibration error

*Slide 12, top right.*

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

**In plain words.**Split the queries into bins by how confident the gate was.
In each bin, compare the average confidence with the observed rate of the
answers actually being there. Weight each bin by how many queries are in it,
and add up the gaps. Zero is perfect calibration.

**Why the weighting matters.** Without the weight, a bin with one query
counts as much as a bin with a hundred. The weighting says the ECE is the
average error over queries, which is the thing a reader wants.

**What it cannot tell you.** A single number hides the shape. The focus
gate's ECE of 0.1044 comes mostly from the fact that it puts most of its
queries in the lowest confidence bin. The reliability diagram on slide 12 is
where that is visible, and the report shows both.

**The caveat.** The value is 0.1044, and the deck says it out loud and does
not defend it. The industrial gate is at 0.075 and tracks the diagonal; the
focus gate does not.

## B.12 The Brier score

*Slide 12, below the ECE.*

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
answered "no" would score $(1-0)^2$ on the negative class and $(0-1)^2$ on
the positive class, giving a Brier score of about 0.182. The gate's 0.1510 is
better than that trivial model and not dramatically so. That is the honest
size of the gain, and the report gives the trivial model's number rather than
only its own.

## B.13 The exact McNemar test

*Slide 15, top right.*

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
where both
systems agreed tell the test nothing: they cannot distinguish the arms. Only
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

**The caveat.** A p-value of 0.001 says the disagreement is not a coin flip.
It does not say how large the effect is, and it does not say the effect
transfers to another corpus or another generator. The counts $b$ and $c$ are
the effect size, and they are on the slide for that reason.

# Part C. The slides and the figures

Every slide, in order, with what is on it, the measurement behind it, and the
caveat that belongs with it. The six figures are explained at the end.

## C.1 Slide 1. Title

<!-- slide:1 -->

The title, the subtitle, your name and roll number, the department, the
supervisor and the date. The subtitle names the four things the talk
covers: architecture, evaluation protocol, failure modes, and what the
measurements actually show. The third of those is the unusual one, and it is
the one to emphasise: the report does not claim a new architecture, it claims
a measured characterisation of one.

## C.2 Slide 2. A wrong answer costs more than no answer

<!-- slide:2 -->

**On the slide.** Three bullets on the left. The panel on the right holds
the research question.

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
it has been measured properly" is doing real work. Three of the fourteen
findings are about this project's own instruments reporting numbers a careful
reader could not trust, and the headline refusal rate was one of them. A
framework's contribution is only as good as the instruments that measured it.

## C.3 Slide 3. The framework: five stages

<!-- slide:3 -->

**On the slide.** A pipeline diagram of five boxes, left to right. Two of
them are purple and three are grey. A table under the diagram gives each
stage its input, its output and whether it may refuse. A purple band at the
bottom carries the non-bypassability claim.

**The five stages.** Stage 0 validates the form of the query and can refuse
before any retrieval happens. Stage 1 is hybrid retrieval. Stage 2 reranks
and applies a modality quota. Stage 3 is the confidence gate, which is the
mechanism the talk is about. Stage 4 generates and scores every claim against
the evidence it was shown.

**The two purple boxes are stages 0 and 3.** Say "two stages can refuse" and
point at them. The grey ones cannot.

**Read nothing from the table.** It is there so that a question about the
pipeline can be answered by pointing rather than by talking.

**The purple band.** The generator is injected into the framework and called
at exactly one line, after the gate has accepted, so a refused query costs no
model call at all. Non-bypassability is a property of the code here, not a
convention the caller is trusted to follow. The only two paths that skip the
gate are the comparison arms `rag_nogate` and `long_context`, and both are
reported as separate results.

**Terms.** *Pipeline stage*, *form validator*, *confidence gate*, *claim
assessment*, *non-bypassability* -- Part A.

## C.4 Slide 4. Retrieval: two legs, one fusion, one quota

<!-- slide:4 -->

**On the slide.** Three formulas (B.1, B.2, B.3), a panel of three
invariants on the right, five bullets, and a band at the bottom explaining
why the dense leg changed.

**The configuration.** The lexical leg is Okapi BM25 with $k_1 = 1.2$ and
$b = 0.75$. The dense leg is BAAI/bge-m3, 1024 dimensions, L2 normalised.
Fusion takes the top 20 of each leg into a pool of 50. The quota is a floor
on the non-text share, relaxed when the pool cannot supply it.

**The three invariants, asserted rather than assumed.** The category
pre-filter restricts both legs before fusion. The reranker only permutes its
own pool. The quota never leaves its pool. Each one is asserted directly in
the code, and three real defects were found that way, none of them visible
in the output.

**The band at the bottom is the point to make.** The first dense encoder was
measurably worse than plain BM25 on this corpus, so the fusion had been
carrying a leg that lost information. It was replaced with BAAI/bge-m3. The
archive keeps the earlier encoder's numbers, so both sides of that comparison
rest on measured values rather than on a claim.

**Terms.** *Hybrid retrieval*, *BM25*, *dense leg*, *embedding*, *RRF*,
*modality quota*, *candidate pool*, *invariant* -- Part A.

## C.5 Slide 5. The confidence gate

<!-- slide:5 -->

**On the slide.** Three formulas (B.4, B.5, B.6), a bullet list of the five
features and the fitting procedure, and a panel on the right answering why
the gate works at the query level.

**What it is.** A calibrated posterior over the whole retrieved pool. Five
query-level features go into a logistic model fitted by maximum likelihood,
and the decision is a threshold on the posterior. The fitted operating point
on the focus domain is $\tau = 0.05$.

**The panel is the answer to "why is this not just a similarity threshold".**
With one gold chunk among about fifty candidates, a chunk-level classifier
is right 98 percent of the time by answering "nothing is relevant". Maximum
likelihood fitting duly returns a large negative intercept: a degenerate
solution that looks like a fitted model and behaves like a constant.
Calibrating at the query level removes it.

**One more thing to know, and it is a naming matter.** The positive class is
answer-in-context detectability, defined operationally as the gold chunk
being present in the reranked candidate pool. The literature reserves
"sufficiency" for a set-level property, so calling this "sufficiency" would
claim prior work that is not here.

**Terms.** *Posterior*, *feature vector*, *Platt scaling*, *maximum
likelihood*, *calibration split*, *threshold*, *answer-in-context
detectability*, *gold chunk* -- Part A.

## C.6 Slide 6. The contradiction gate, and the form validator

<!-- slide:6 -->

**On the slide.** One formula across the top (B.7), and two panels: the
contradiction gate on the left, the form validator on the right.

**Two components that refuse, for two different reasons.** The contradiction
gate needs two independent branches to agree. Branch one is a natural
language inference model at threshold 0.70. Branch two requires that the two
chunks talk about the same measured quantity of the same instance. A
quantity branch on its own fired on citation years, and a topical subject
check on its own was a topic check rather than a contradiction check.
Requiring both cut the alarms from 81 to 20.

**The form validator runs before retrieval.** The gate accepted 76.7 percent
of the malformed stems that were pushed through it, so it is an evidence gate
and not a form gate, and it is never credited with the validator's work. The
validator itself refused 25 of 25 hand-authored malformed queries and 0 of
35 well-formed ones, at 2.6 microseconds per query.

**The counterfactual is the memorable part.** Reusing the benchmark builder's
question-generation rule as a runtime check would have refused 100.0 percent
of hand-labelled well-formed questions. A filter written for one purpose does
not fit another, and its false rejection rate has to be measured before it
ships.

**Terms.** *NLI*, *form validator*, *malformed stem*, *counterfactual*,
*false rejection rate* -- Part A.

## C.7 Slide 7. Three corpora, and a benchmark that had to be repaired

<!-- slide:7 -->

**On the slide.** A table of the three corpora, and three panels describing
the three repairs.

**The corpora and their roles, which do not overlap.** The supply chain
focus corpus carries 735 chunks from 14
documents and is where the ablation, the gate and the generation experiments
run. The six-category industrial corpus carries 2383 chunks
from 46 documents and is where transfer and the long-context
cost are measured. The federal regulatory corpus carries 465
chunks from 7 documents and exists because it is the corpus
where the contradiction detector's phenomenon could be looked for.

**Repair 1: the answer labels.** 30 of the answerable questions carried an
answer label attached to the wrong question. Two defects in the label
generation caused it. After the repair the defect rate is 1 of 32. The gold
chunk was always right, so the retrieval side was never affected.

**Repair 2: the unanswerable class.** The unanswerable half was separable
from the question text alone, so the headline refusal rate was measuring the
benchmark rather than the framework. The class was rebuilt with corpus-anchored
definitions, and every repaired question was given a structural twin in the
answerable class.

**Repair 3: the form check.** The runtime validator refused 3 of
176 benchmark queries, all of them generator artefacts that
read as malformed rather than real questions. The audit instrument was kept
rather than deleted, because it is the instrument that found the defects.

**Be honest about the substitute.** The primary corpus of proprietary supply
chain documents cannot be redistributed, so it cannot be shipped or re-run by
a reader. Everything measured was measured on a public substitute. The
focus corpus carries 32 answerable and
144 unanswerable questions; the cross-category corpus
carries 132 and 144. The two never mix,
because they are used for different experiments.

**Terms.** *Corpus*, *chunk*, *gold chunk*, *structural twin*, *shortcut* --
Part A.

## C.8 Slide 8. Metrics, tests, and the rule that every comparison is paired

<!-- slide:8 -->

**On the slide.** Three formulas (B.8, B.9, B.10) and five bullets.

**The rule that does the work.** Every comparison is paired, because the arms
answer the same questions, and the paired test is applied per class, because
one number for both would hide the trade. A gate can improve the unanswerable
class and damage the answerable class at the same time, and a single pooled
number cannot show that.

**Which test for what.** Retrieval comparisons are paired over the same
queries and tested with the Wilcoxon signed-rank test, with Cliff's delta
and Cohen's $d_z$ as effect sizes. Generation comparisons are paired over
the same questions and tested with the exact McNemar test (B.13), where $b$
counts the questions the baseline answered and the arm refused and $c$ counts
the other way round.

**Proportions carry Wilson score intervals**, and a null is read as no
difference established here.

**The random arm.** One generator, five arms, one of which refuses the same
number of questions at random. Without that arm, refusing on a coin flip and
refusing on a calibrated score look identical. This is the single most
important control in the deck and it returns on slide 17.

**Terms.** *Paired test*, *Wilcoxon signed-rank test*, *Cliff's delta*,
*Cohen's dz*, *McNemar test*, *b and c*, *Wilson score interval*, *null
result*, *effect size*, *random control* -- Part A.

## C.9 Slide 9. Retrieval: seven configurations on the focus corpus

<!-- slide:9 -->

**On the slide.** A table of seven ablated systems with four metrics each, and
a second table of two paired comparisons.

**The seven configurations.** A is BM25 only. B is dense only. C is the
fusion. D adds the reranker. E adds the category filter. F adds the quota
before the reranker. G adds the quota after it. Each row is the previous
row plus one thing, so a difference between two rows is the cost of that one
thing.

**What the numbers say.** The dense leg is significantly worse than BM25:
0.969 to 0.812, a paired difference of -0.156 at $p = 0.025$. That is why
the encoder was replaced. Fusion recovers the loss: 1.000 against 0.812, a
paired improvement of +0.188 at $p = 0.014$, and it improves the ordering as
well.

**The claim for fusion is narrow.** It stopped being a loss. It did not
become a significant win over plain BM25 on its own: A to C is -0.007 at
$p = 0.76$. The reranker is the other story: C to D is +0.111 at
$p = 0.00093$.

**Cross-category transfer.** The reranker's gain survives the change of
corpus, while the fusion's recall advantage over BM25 does not. That is why
the reranker sentence always travels with its corpus: -0.3 points on the
focus corpus against +11.1 points on the six-category corpus.

**Terms.** *Ablation*, *Recall@k*, *MRR*, *nDCG*, *paired test* -- Part A.

## C.10 Slide 10. The modality quota is a trade, not a gain

<!-- slide:10 -->

**On the slide.** A scatter plot, a table of the quota placement on three
corpora, and three bullets.

**The table.** On the focus corpus the quota before the reranker gives 1.000
and after it 0.938, with $p = 0.157$. On the six-category industrial corpus
0.939 against 0.924, $p = 0.480$. On the federal regulatory corpus 0.988
against 0.980, $p = 0.317$.

**What it says.** On the industrial corpus the pre-rerank quota buys 0.8
points of table recall and gives up 0.8 points of overall recall, and the
post-rerank quota lands on exactly the no-quota operating point. On the
focus corpus the post-rerank quota gives up 3.1 points of overall recall
while table recall stays at 1.000. None of the three differences is
significant.

**So the placement is a configuration value**, and the ranking is reported
with its corpus attached. A claim that the quota belonged before the cross
encoder would not hold on every corpus.

**Terms.** *Modality quota*, *null result*, *significance* -- Part A.

## C.11 Slide 11. More candidates are not monotonically better

<!-- slide:11 -->

**On the slide.** A plot of recall against pool size, a table of five pool
sizes with three metrics each, and three bullets.

**The table.** A pool of 5 gives Recall@10 of 0.969, a pool of 10 gives
1.000, and pools of 20, 50 and 100 give 0.969. MRR falls as the pool grows:
0.807, 0.805, 0.797, 0.795, 0.795.

**What is happening is visible at twenty.** Recall@20 keeps rising as the
pool grows, so the gold chunk is still being found, and then the reranker
pushes it out of the ten-chunk context. The answer is still in the pool and
the reranker is choosing differently.

**The industrial corpus is the exception.** There Recall@20 reaches 1.000 at
a pool of fifty while Recall@10 stays at 0.988, so 1.21 percent of the gold
is retrieved and then pushed out.

**The general lesson.** A larger pool costs ordering without adding the
answer, and which way it fails depends on the corpus. The focus curve
saturates at ten. The industrial curve does not, and that is the exception
that makes the point.

**Terms.** *Candidate pool*, *reranker*, *Recall@k*, *MRR* -- Part A.

## C.12 Slide 12. The gate is calibrated, and it is not excellent

<!-- slide:12 -->

**On the slide.** The reliability diagram (Figure 3), a table of four
calibration numbers, the ECE and Brier formulas (B.11, B.12), and three
bullets.

**The numbers.** Expected calibration error 0.1044. Brier score 0.1510. Base
rate of answer in context 0.182. Retriever recall of gold 1.000.

**What the numbers mean.** The gate is fitted on a 60 percent calibration
split of 176 queries, and its positive class has a base rate
of 0.182. The
industrial gate tracks the diagonal at ECE 0.075. The focus gate does not,
and it puts most of its queries in the lowest confidence bin.

**Say the ECE out loud and do not defend it.** An ECE of 0.1044 is reported
rather than improved by refitting. It is the calibration of one fitted
artefact on one fixed split, and it is reported because a reader would
otherwise have to assume it is better than it is.

**The retriever's recall of gold is 1.000.** That number is doing quiet work
throughout the deck: when the gate refuses, it is not because the retriever
failed to find the answer, and the comparison on slide 20 is clean because
the gold chunk was always available.

**Terms.** *Calibration*, *ECE*, *Brier score*, *base rate*, *reliability
diagram*, *held-out evaluation half* -- Part A.

## C.13 Slide 13. The operating point, and the frontier it sits on

<!-- slide:13 -->

**On the slide.** The threshold sweep in full (seven rows), the risk-coverage
figure (Figure 2), and three bullets.

**The rule.** The highest $\tau$ that still answers at least 90 percent of
the answerable queries, which gives $\tau = 0.05$.

**The sweep.** At 0.05: 0.938 of the answerable answered, 0.361 of the
unanswerable refused, abstention precision 0.963, coverage 0.693. At 0.10:
coverage falls to 0.432. At 0.15: 0.364. At 0.20: 0.278. At 0.30: 0.170.
At 0.50: 0.097. At 0.90: 0.017.

**The gate is precise where it refuses.** At the fitted operating point the
abstention precision is 0.963, so almost every refusal lands on a question
that should have been refused.

**The frontier is real.** Every extra refusal is paid for in coverage, and
the price climbs steeply past $\tau = 0.15$. The sweep is shown in full
because a single threshold hides the shape of the frontier behind it.

**What a practitioner takes from this slide.** The abstention precision
column. 0.963 is the number that says: when this system says it does not
know, it is right 96 percent of the time on this corpus at this operating
point.

**Terms.** *Operating point*, *abstention precision*, *coverage*,
*risk-coverage curve*, *frontier* -- Part A.

## C.14 Slide 14. The benchmark answered itself

<!-- slide:14 -->

**On the slide.** The ROC curve of the question-only classifier (Figure 5), a
before-and-after table, and three bullets.

**The table.** Two different classifiers read only the question text, so
the table has a row for each. The shape-separability row, which is the one
the figure plots, is 0.999 before the repair and 0.608 after it. The
question-only policy row, a rule-based detector, is 0.675 before and 0.564
after. The identifier shortcut caught 76.4 percent of the unanswerable class
before and 0.0 percent after. The gate's refusal rate on the class was 91.7
percent before and 23.6 percent after.

**What happened.** The hard family named a fabricated identifier, and no
answerable question carried an identifier of that shape, so one regular
expression caught the whole family. The headline refusal rate was therefore
an upper bound rather than a measurement, and the rate that was measured was
measuring the benchmark rather than the framework.

**The gap between the two strata is the finding.** After the repair the gate
refuses 26 of 110 of the corpus-anchored hard stratum and
26 of 34 of the
out-of-domain stratum. What the gate detects is a *recognisable*
unanswerable question, one drawn from outside the corpus or one whose subject
is plainly absent. It is much weaker on the on-topic but unanswered case.

**Say it slowly.** This is the slide that changes the headline, and it changes
it downward, from 91.7 percent to 23.6 percent. The number that survives is
the one that can be defended.

**Terms.** *ROC AUC*, *shortcut*, *stratum*, *out-of-domain*, *structural
twin* -- Part A.

## C.15 Slide 15. One generator, five arms, two prompt conditions

<!-- slide:15 -->

**On the slide.** The five arms and what each removes, the McNemar formula
(B.13), a panel on the two prompt conditions, a table of two generators, and
two bullets.

**The five arms.**

| Arm | What it removes |
|---|---|
| `rag_nogate` | the gate, keeping retrieval |
| `rag@fitted` | nothing; the framework at its fitted operating point |
| `rag@random` | the confidence score, keeping the refusal budget |
| `rag@transferred` | the fitted operating point; the threshold moved across corpora |
| `long_context` | retrieval; the whole corpus in the prompt |

**The two prompt conditions differ by a single sentence.** Under one the
generator may decline, and under the other it must answer. Model, questions,
retrieval, scorer and temperature stay identical either way. The prompt
condition is an experimental axis, not a fixed setting.

**The replication that could not be run.** MiniMax-M3.1-Flash returned no
text on 24 of 66 questions, and raising the output budget fourfold rescued
13 and left 11 empty. An empty completion is neither an answer nor a refusal,
so a run like that is recorded as not run, with the reason, because a rate
quoted from a run that did not happen is indistinguishable from a rate that
did.

**Terms.** *Arm*, *prompt condition*, *empty completion*, *exact test* --
Part A.

## C.16 Slide 16. The verdict under the answering condition

<!-- slide:16 -->

**On the slide.** A table of five arms against four columns, and the verdict.

**The table.** Under the answering condition the generator cannot decline on
its own, so the gate cannot be redundant.

| Arm | Unanswerable answered | Answerable answered |
|---|---|---|
| `rag_nogate` | 135 of 144 (0.938) | 32 of 32 |
| `rag@fitted` | 76 of 144 (0.528) | 30 of 32 |
| `rag@random` | 87 of 144 (0.604) | 21 of 32 |
| `rag@transferred` | 3 of 144 (0.021) | 6 of 32 |
| `long_context` | 134 of 144 (0.931) | 32 of 32 |

The paired McNemar test on the unanswerable class gives $b = 60$, $c = 1$,
$p < 0.001$ for the fitted gate. On the answerable class it gives $b = 2$,
$c = 0$, $p = 0.500$: two answerable questions lost, and that is not
distinguishable from chance. The random control against the ungated arm
gives $b = 11$ with $p = 0.001$ on the answerable class.

**The verdict: supported under both prompt conditions.** Under the cautious
prompt the rate falls from 0.535 to 0.417, at the cost of the same two
answerable questions.

**Why the two-condition design matters.** Under the cautious prompt alone the
generator refused most unanswerable questions on its own, the gate's
refusals were largely redundant, and the arms could not have been told
apart. The answering condition is the one that can separate them.

**The transferred arm over-refuses badly.** It answers
6 of 32 answerable
questions, because the threshold was fitted on one half of the cross-category
corpus and applied unchanged to the other half. Do not linger on this slide;
it comes back at the end.

**Terms.** *Arm*, *paired test*, *McNemar test*, *fit and transfer* -- Part A.

## C.17 Slide 17. What the confidence score buys, and what it costs

<!-- slide:17 -->

**On the slide.** A table of four arms against four count columns, two
callouts, and the bullet that carries the finding.

**The table.** `rag_nogate` answered 167, of which 135 were wrong, with 21
correct under the entailment test and 29 under the key-term test.
`rag@fitted` answered 106, of which 76 were wrong, with 20 and 27 correct.
`rag@random` answered 108, of which 87 were wrong, with 15 and 20 correct.
`long_context` answered 166, of which 134 were wrong, with 13 and 24
correct.

**It does not buy a lower answer rate on unanswerable questions.** The
random control reaches 0.604, worse than the fitted gate's 0.528 and far
below the ungated arm's 0.938, because most questions in a benchmark are
unanswerable and refusing at random is already a large improvement over never
refusing.

**What the score buys is where the refusals land.** The gate removes 59
wrong answers and costs 1 correct answer under the entailment test, and its
refusals concentrate on the class that should be refused. That is a precision
claim.

**The two callouts.** 2 answerable questions refused by the gate, $p = 0.500$.
11 answerable questions refused by the random control, $p = 0.001$.

**The warning to give.** The per-answer accuracy numbers must not be read as
a quality win. The gated arm answers an easier subset, which is the
selection effect. If a report said the gate answers fewer unanswerable
questions, it would be true and it would be misleading.

**Terms.** *Selection effect*, *per-answer accuracy*, *entailment*,
*precision claim* -- Part A.

## C.18 Slide 18. Long context against the pipeline

<!-- slide:18 -->

**On the slide.** Three big numbers at the top, three bullets on the left, a
panel on the right, and a figure.

**The three numbers.** 74 times the input tokens per query. 58.8 times the
input cost per query, at the provider's cached pricing. 33.0 percent of the
long-context tokens are cache reads.

**Cost.** The focus corpus is 202,529 tokens against the pipeline's accepted
context of 2,246 tokens.

**Coverage.** The whole-corpus prompt answered
32 of 32 answerable
questions, the same as the ungated pipeline.

**Quality.** Accuracy 0.406 against 0.667 for the gated arm, and the margin
is not significant under a length-controlled re-scoring of the same answers.

**The retrieval-side proxy.** With the candidate set widened to every chunk,
the gold chunk lands in the top 10 for 0.969 of the focus queries and 0.902
of the cross-category queries, at a median rank of 1. The evidence is not
lost in a large context; the tail is where corpus size bites, and a retriever
that finds the answer at median rank 1 has no use for the other
735 chunks.

**The point about the two ratios.** The token ratio on its own is off by an
order of magnitude against the money, because most of the long-context arm's
tokens are cache reads at a fifth of the base rate. A token ratio must never
carry an argument about money.

**The limit of the comparison.** The cross-category corpus is 680,417
tokens, 5.2 times the 128K window, so the quality half of that comparison
could not be run there, and it is settled on coverage and cost alone.

**Terms.** *Long context*, *cached pricing*, *cache read*, *length-controlled
re-scoring*, *median rank* -- Part A.

## C.19 Slide 19. The contradiction gate: a precision of zero

<!-- slide:19 -->

**On the slide.** The precision figure (Figure 6), a table of six quantities,
and two bullets.

**The table.** 20 labelled alarms. 0 confirmed as contradictions. Precision
against reader labels 0.0 percent. 95 percent upper bound on the true
precision 16.1 percent. Annotator agreement on the decision 101 of 101.
Annotator disagreement 0.

**What happened.** None of the raised alarms was confirmed. Two annotators
that do not share a model, both blind to the detector's scores and both 14
of 14 correct on a control set with known labels, still confirmed nothing.

**And the other half.** The readers also found no contradictions in a random
sample of 80 pairs the gate did not flag. So this corpus holds concept-level
prose rather than instance records, and it does not contain the phenomenon
the mechanism detects.

**How to report it.** As a null with a stated upper bound, not as a defect to
be explained away. The two detector defects the audit exposed were real and
were fixed, and they were not the reason the alarms went unconfirmed. The
mechanism is unproven rather than disproven.

**Terms.** *Precision*, *95 percent upper bound*, *Wilson score interval*,
*annotator agreement* -- Part A.

## C.20 Slide 20. Most unattributed error comes from the evidence

<!-- slide:20 -->

**On the slide.** A table of five error measures against two evidence sets,
a panel on how a claim is scored, and a statement of what it means.

**The table.** Over the retrieved evidence against over the gold evidence:
grounded claims 0.118 against 0.542; inferred claims 0.103 against 0.513;
uncertain claims 0.220 against 0.610; reference hallucination 0.164 against
0.571; answer position effect $p = 0.417$ against $p = 0.008$.

**How a claim is scored.** A claim counts as supported when a chunk entails
it at threshold 0.5, or when the evidence states it literally. 0.80 separates
a grounded claim from 0.45 for an inferred one; anything below is uncertain.
The gold chunk is never force-added, so nothing outside the evidence can
support a claim.

**What it means.** The grounded-claim error rate is 0.118 over the evidence
the arm was shown and 0.542 over the gold chunk, so most of what the
framework's own attribution cannot explain comes from the evidence it was
given. The gold chunk was always right, so this is a clean comparison: the
same answers, two evidence sets, and the gap between the columns is large.

**The answer position effect is not a finding.** The direction replicates in
three of the four corpus-and-protocol measurements and ties in the fourth,
and the magnitude does not replicate. It is stated with its magnitude rather
than as a rule.

**Terms.** *Claim*, *entailment*, *grounded, inferred, uncertain claim*,
*answer position effect* -- Part A.

## C.21 Slide 21. What the measurements establish

<!-- slide:21 -->

**On the slide.** Fourteen findings, each with the number that carries it.

**The findings.** F1 the dense leg is worse than BM25 on focus and fusion
recovers it. F2 the reranker's value depends on the corpus. F3 quota
placement has no universally better answer. F4 the candidate pool curve peaks
and then declines. F5 the gate is precise where it refuses. F6 the gate finds
a recognisable unanswerable question. F7 the hypothesis holds under both
prompt conditions. F8 the score buys refusal precision, not a lower answer
rate. F9 the gate is an evidence gate, not a form gate. F10 the contradiction
gate's precision against readers is zero. F11 long context costs 74 times the
tokens and 58.8 times the money. F12 a calibrated threshold does not transfer
across corpora. F13 most unattributed error comes from the evidence. F14 an
empty completion is a third outcome.

**Every row is a measurement against an archived result file.** The three
that qualify the verdict are F8, F10 and F12, and they are the three worth
reading twice.

**Leave this slide up while you talk through those three.** F8 is the finding
most likely to be reported wrongly, and the one to be ready for. F10 is a
null with an upper bound. F12 is the transfer failure.

**Terms.** *Findings table*, *archived result file* -- Part A.

## C.22 Slide 22. Limitations

<!-- slide:22 -->

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
were flagged in the text rather than waiting to be found in the questions.
Volunteering your own weaknesses before being asked is what makes the rest of
the work credible.

## C.23 Slide 23. What comes next

<!-- slide:23 -->

**On the slide.** Six numbered next steps, and a closing note.

**The six.** 1. Repeat the generator-side comparison on a generator that
returns text on the table questions; one generator settles the hypothesis for
one model. 2. Compare the gate against a token-level faithfulness monitor;
the gate is currently measured against a prompt-level control only. 3. Settle
the magnitude and the power of the positional comparison; the direction holds
in three of the four measurements, and not in the magnitude. 4. Hand-check
the repaired unanswerable class against the corpus, on both corpora. 5.
Replace the model-based contradiction annotators with human readers, which
would strengthen the 0.0 percent finding in either direction. 6. Publish the
corrected benchmark and the shortcut audit as a separate artefact, so other
work on RAG refusal can check its own benchmarks against the same instrument.

**The closing note.** The most useful thing this produced was not the
framework. It was finding that two of its own instruments were reporting
numbers a careful reader could not trust, and changing the headline rather
than explaining it away. A framework's contribution is only as good as the
instruments that measured it.

**End on the instruments, not on the architecture.** Point at item 1 and item
6. The replication is the gap that matters for the claim, and the published
benchmark is the part that outlives the report.

## C.24 Slide 24. Thank you

<!-- slide:24 -->

Say thank you and stop. The report has the full text, the eight works that
were actually used, and the numbers behind every row of the findings table.

---

# Part C2. The six figures

Each figure is one measurement, plotted. A figure is the easiest thing on a
deck to misread, so each is given with what is plotted, how to read it, and
what it does not show.

## Figure 1. Recall against the candidate pool size

*Slide 11.*

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

*Slide 13.*

<!-- figure:fig2_risk_coverage -->

**What is plotted.** The risk-coverage curve of the confidence gate: the
fraction of queries the gate answers on the horizontal axis, and the risk,
which is the share of answered queries that had no answer in their context,
on the vertical axis.

**How to read it.** Each point is a threshold. Moving right means the gate
answers more; moving down means the answers are safer. The operating point
sits at coverage 0.693 with a risk equal to the ungated arm's answer rate on
the unanswerable class.

**What it shows.** That the trade is real and steep. The curve is the shape
of the frontier, and the sweep table on the same slide is the same curve
discretised. Always answering is the top-right end; always refusing is the
bottom-left end.

**What it does not show.** Whether any particular point is the right point.
That is a deployment decision about what a refusal costs, and the report
gives the curve so the reader can make it.

## Figure 3. The reliability of the gate's probability

*Slide 12.*

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

*Slide 10.*

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

*Slide 19.*

<!-- figure:fig6_contradiction_precision -->

**What is plotted.** The detector's precision against the base rate of real
conflicts, with 95 percent Wilson intervals.

**How to read it.** The interval is the honest part. With 20 alarms and 0
confirmed, the point estimate is zero, but the interval runs up to 16.1
percent, and the report quotes the upper bound rather than the point.

**What it shows.** That no alarm was confirmed by readers who were blind to
the detector's scores, who agreed with each other on 101 of 101 decisions,
and who were 14 of 14 correct on a control set with known labels.

**What it does not show.** That the detector can never be right. A null with
an upper bound is not a refutation, and the corpus is the reason: the
readers found no contradictions in a random sample of 80 unflagged pairs
either, so this corpus does not contain the phenomenon the mechanism
detects.

# Part D. The technicalities

The things that are true of every experiment at once, rather than of one
slide. This is the part that has to be understood to answer a question that
does not fit on a slide.

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
the report is measured here: the ECE of 0.1044, the Brier score of 0.1510,
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
version of the gate failed (Part B.4), and it is also why the Brier score of
0.1510 has to be read against the trivial model's 0.182.

## D.3 The benchmark, and its three repairs

The benchmark was audited before it was used, and the audit found three
defects. Two of them changed the headline. The account is here in full,
because "the framework was measured on a benchmark that had to be repaired"
is a claim that needs its evidence.

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

After the repair, the shape-separability classifier scores 0.608 on the
focus corpus against a permutation null of 0.455 plus or minus 0.072, the
question-only policy scores 0.564 where 0.5 is no discrimination, and the
one-rule shortcut carries 0.0 percent. The benchmark as it stood before the
repair is kept beside the repaired one, so every before-and-after claim can
be regenerated rather than asserted.

**Repair 3: the form check.** The runtime validator refused 3 of 176
benchmark queries. All three were generator artefacts that read as malformed
rather than real questions. This is the one repair that goes the other way:
the validator was too eager on this benchmark, and the benchmark was right.

**The audit instrument was kept rather than deleted**, because it is the
instrument that found the defects. It is the first of the six next steps to
be published separately, so that other work on RAG refusal can check its own
benchmarks against the same instrument.

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
the ungated pipeline,
and it costs 74 times the tokens and 58.8 times the money. The report does
not claim the retrieval machinery is cheaper in absolute terms; it claims
the cost ratio, and it claims the cost because the corpus does not fit in a
context window for one of the two corpora.

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
happen is indistinguishable from a rate that did, and that is a distinction
worth keeping in a project where the whole claim rests on measurement.

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
precision is zero by construction. That is what slide 19 establishes, and it
is why the finding is a statement about the corpus as much as about the
detector.

## D.7 What is claimed, and what is not

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

**The three qualifying findings.** F8, F10 and F12 are the ones that
qualify the verdict, and they are the three worth reading twice: the score
buys refusal precision and not a lower answer rate; the contradiction
detector's precision against readers is zero, with an upper bound of 16.1
percent; and a calibrated threshold does not transfer across corpora.

## D.8 Reproducibility and provenance

**Every number is a measurement against an archived result file.** The
findings table on slide 21 is a list of measurements, not a list of
conclusions, and each row can be regenerated.

**The corpus ships with its provenance.** For every document the manifest
gives the source URL, the upstream revision it was read at, the SHA-256 of
the exact bytes used, and its chunk count. The licence for the article text
is stated. The primary corpus of proprietary supply chain documents cannot be
redistributed, so it cannot be shipped or re-run by a reader, and the report
says so wherever the substitute matters.

**The audit instruments are kept.** The benchmark as it stood before the
repair sits beside the repaired one. The figures are regenerated from the
result files, and the build fails if a figure is older than the results it
draws. The caption of a figure and the number it carries are checked against
each other, because a caption that disagrees with its own figure is worse
than no caption.

**What this buys the reader.** Any claim in the deck can be checked against
an archived result rather than taken on trust. That is the standard the
project holds itself to, and the reason three of the deck's findings are
about the project's own instruments rather than about the framework.

---

## D.9 One page of numbers to have in mind

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
