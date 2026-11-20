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

**Why the disagreements are the whole test.** The {{CASE_N_QUERIES}} queries
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
