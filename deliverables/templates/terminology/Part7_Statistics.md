# Part 7. The statistics

### Paired test

**Plain.** A test that compares two systems on the same questions, rather
than on two separate piles of questions.

**Technical.** A significance test in which the observations are differences
within units rather than measurements of two independent groups, which
removes between-unit variance from the comparison.

**Here.** Every comparison in this work is paired, because the arms answer
exactly the same questions. An unpaired test would treat the arms as
independent and throw the pairing away.

### Exact test

**Plain.** A test that works out the answer by counting every possible
arrangement, rather than by approximating.

**Technical.** A test in which the p value is computed by enumerating the
permutations of the data that are at least as extreme as the observed one,
under the null hypothesis. It makes no distributional approximation, which
matters when the counts are small.

**Here.** The McNemar test used for the generation experiment is exact, and
the counts are small enough for that to be a real difference rather than a
formality.

### McNemar's test

**Plain.** The test for two systems that answer the same questions, which
looks only at the questions where the two systems disagreed.

**Technical.** A test for the difference between two paired proportions in
which the discordant pairs alone carry information. The statistic is the
number of discordant pairs in one direction minus those in the other, and
the exact version conditions on their total.

**Here.** It is the generation-side test, and the table on slide 17 gives
the discordant counts directly: for the fitted gate against the ungated arm
on the unanswerable class, b = 60 and c = 1.

### Discordant pair

**Plain.** A question that one system answered and the other refused, or
that one refused and the other answered.

**Technical.** An observation in which two paired measurements differ in
outcome. The two cells in which both measurements agree carry no information
about the direction of the difference.

**Here.** The table reports b and c for every arm pair, so that the effect
is visible and not only the test result.

### The counts b and c

**Plain.** b is the number of questions the first system answered and the
second refused; c is the number the first refused and the second answered.

**Technical.** The two discordant cells of a two-by-two table, conventionally
ordered so that b counts the cells favouring the second condition and c
those favouring the first.

**Here.** For the fitted gate against the ungated arm, b = 60 and c = 1 on
the unanswerable class, at p {{GEN_PAIRED_FITTED_UNANS_P}}.

### Wilcoxon signed-rank test

**Plain.** A test that compares two systems on the same questions and takes
into account how big the differences are as well as how often they go each
way.

**Technical.** A non-parametric test for the difference between two paired
samples, in which the differences are ranked by absolute magnitude and the
test is on the signed rank sum. It assumes symmetry of the difference
distribution and does not assume normality of the values.

**Here.** It is the retrieval-side test, applied to every comparison of the
seven configurations, and the p values for the two headline comparisons are
0.025 and 0.014.

### Effect size

**Plain.** How big the difference is, as opposed to whether it is unlikely to
be chance.

**Technical.** A quantity expressing the magnitude of an effect in the units
of the measurement, as opposed to the evidence against the null hypothesis.
A p value answers "is it probably zero?"; an effect size answers "how big
is it?"

**Here.** Both are reported. Slide 12 gives Cohen's d and Cliff's delta
beside the p value, because a paired difference of 0.156 on 32 queries needs
both.

### Cohen's d_z

**Plain.** The difference between the two systems, expressed in units of the
spread of the differences themselves.

**Technical.** The standardised mean difference for paired samples, the mean
of the differences divided by their standard deviation. d_z = 1 means the
average difference is one standard deviation of the differences.

**Here.** It is {{ABL_DZ_AB}} for BM25 against the dense leg and
{{ABL_DZ_BC}} for fusion against the dense leg.

### Cliff's delta

**Plain.** How often one system beats the other, head to head, on every
pair of questions.

**Technical.** A non-parametric effect size equal to the proportion of
discordant pairs in one direction minus the proportion in the other, taking
all pairwise comparisons. It is bounded between minus one and one, and
absolute values below about 0.147 are conventionally called small.

**Here.** It is {{ABL_CD_AB}} for BM25 against the dense leg, which is a small
effect, and that is why the sentence about the dense leg says "significantly
worse" rather than "much worse".

### Null result

**Plain.** The comparison found nothing, and that is a finding rather than a
failure.

**Technical.** a failure to reject the null hypothesis. It is evidence that
the effect, if any, is smaller than the design could detect, and it is not
evidence that the effect is exactly zero.

**Here.** Four results are nulls: the quota placement on three corpora, the
fusion-over-BM25 comparison, the reranker on the focus corpus, and the
contradiction gate. Each is reported as no difference established here.

### No difference established here

**Plain.** The wording used instead of "no difference".

**Technical.** The standard reading of a null result at a given sample size:
the confidence interval for the effect includes zero, and the study was not
powered to exclude effects smaller than its resolution. It is a statement
about what this study could show, not about the world.

**Here.** It is how limitation L5 is worded on slide 23, and it is the phrase
to use if a panel presses on any of the four nulls.

### p value

**Plain.** How surprising the result would be if there were nothing going on.

**Technical.** The probability, under the null hypothesis, of observing a
statistic at least as extreme as the one obtained. It is not the probability
that the null is true and it is not the probability that the result is
correct.

**Here.** The headline p values are {{GEN_PAIRED_FITTED_UNANS_P}} under the
answering prompt and {{GEN_PAIRED_CAUTIOUS_UNANS_P}} under the cautious one.

### Significance

**Plain.** Unlikely enough to be worth believing.

**Technical.** A result is conventionally called significant when its p value
falls below a pre-set threshold, usually 0.05. The threshold is a convention
about evidence, not about truth.

**Here.** The comparisons that carry the claims are the ones the protocol
named in advance: one per class per arm pair.

### Power

**Plain.** How likely the study is to find a difference if there is one.

**Technical.** The probability of rejecting the null hypothesis when a
specified alternative is true, which depends on the sample size, the effect
size and the threshold.

**Here.** It is the reason the nulls are read as nulls. The quota-placement
and fusion-over-BM25 comparisons are nulls at this sample size, and item 5 of
the future-work list is a pre-registered power analysis for exactly this
reason.

### Multiple comparisons

**Plain.** Looking at a lot of things and finding that one of them looks
significant by chance.

**Technical.** The inflation of the family-wise error rate when several
hypotheses are tested against the same data, and the corrections or
pre-specified primary endpoints used to control it.

**Here.** The exploratory comparisons are reported as configuration findings
and nulls rather than as claims, so no correction is applied to them either.

### Wilson interval

**Plain.** A sensible range for a proportion, which behaves properly when the
proportion is near zero or one.

**Technical.** A score interval for a binomial proportion computed from the
Wilson score statistic, which stays inside the unit interval and is well
behaved at extreme proportions where the normal approximation is not.

**Here.** Proportions in this work carry Wilson intervals, and it is the
Wilson interval that gives the contradiction gate's 95 percent upper bound of
{{CONTRA_PRECISION_CI_HI}} on a precision of {{CONTRA_PRECISION_PCT}}.

### Bootstrap

**Plain.** Working out the uncertainty by resampling the data with
replacement, many times.

**Technical.** A resampling method that approximates the sampling
distribution of a statistic by drawing many resamples with replacement and
recomputing the statistic on each, with the spread of the results giving the
uncertainty.

**Here.** The bootstrap widths are reported next to the point estimates, as
the protocol note on slide 11 says.

### Proportion and rate

**Plain.** The share of something, and the same thing expressed per unit.

**Technical.** A proportion is a count divided by a denominator; a rate is a
count divided by an exposure. The two are not interchangeable, and a rate
without its denominator is not a measurement.

**Here.** Both are used and both are labelled: the rate of answering
unanswerable questions is a proportion over the class, and the abstention
precision is a proportion over the refusals.

### Refusal precision

**Plain.** Of the times the system refused, how often the answer really was
not there.

**Technical.** The proportion of abstentions that are correct, which is the
precision of the abstaining decision and the quantity that the risk-coverage
curve reports at each coverage.

**Here.** {{FOCUS_GATE_ABST_PRECISION}} at the fitted operating point. It is
the number that the random-escalation control exists to isolate, and slide 18
is built on the difference between it and the control's.
