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
