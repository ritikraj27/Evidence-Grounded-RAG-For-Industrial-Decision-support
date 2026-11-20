# Part 5. The gate, and the statistics of deciding

### Confidence

**Plain.** How sure the system is that it can answer.

**Technical.** A score attached to a prediction, intended to be comparable
with a probability. Confidence is only meaningful relative to a calibration
procedure; an uncalibrated confidence score is a number.

**Here.** The gate's confidence is a calibrated probability of the answer
being present in the retrieved context, not a measure of how fluent the
answer would be.

### Calibration

**Plain.** Making sure that when the system says it is 80 percent sure, it is
right about eight times out of ten.

**Technical.** The property of a predictor that its output probabilities
match the observed frequencies of the outcomes, measured by a calibration
error such as the expected calibration error or the Brier score.

**Here.** The gate's calibration error is {{GATE_ECE}}, and it is reported
rather than improved by refitting, because a calibration error that is not
reported cannot be checked.

### Platt scaling

**Plain.** Turning a set of numbers into a probability, by fitting a simple
sigmoid to them.

**Technical.** A method for converting the scores of a classifier into
probabilities, by fitting a logistic regression on the scores, optionally with
a scaling factor, and regularising its slope so that it behaves sensibly on
an unbalanced problem.

**Here.** The gate is Platt scaling on a five-dimensional feature vector,
fitted by maximum likelihood on 60 percent of the queries. It is one
parameter family on purpose: it can be calibrated and audited.

### Feature vector

**Plain.** The list of numbers the gate looks at.

**Technical.** The vector of query-level statistics handed to the classifier.
Its dimensionality and its individual content determine what the model can
and cannot detect.

**Here.** Five statistics of the candidate pool: the top reranker score, the
mean reranker score, the top BM25 score, the best fused score, and the number
of chunks above the reranker's own relevance bar.

### Query-level gate

**Plain.** A gate that judges the whole search at once, rather than judging
each passage.

**Technical.** A gate whose decision is a function of aggregate statistics of
the retrieved set rather than of any individual retrieved unit. It cannot
localise the answer, but it is not gameable by the presence of one
confidently wrong passage.

**Here.** Every feature describes the pool rather than a chunk, and that is
what removes the degenerate chunk-level solution, where the score is high
whenever the question looks familiar whether or not the answer is there.

### Threshold

**Plain.** The line the score has to cross before the system answers.

**Technical.** The decision boundary of a binary classifier, expressed on the
score scale. Its value is a choice, and saying where it came from is part of
the result.

**Here.** The threshold is {{FOCUS_GATE_TAU}}, chosen by a rule stated in
advance: the highest that still answers at least 90 percent of the answerable
questions.

### Operating point

**Plain.** The particular threshold the system ships with, together with what
it costs and what it buys.

**Technical.** A specific choice on the risk-coverage curve, fixing the
trade-off between the risk of answering without evidence and the loss of
coverage from refusing.

**Here.** At the fitted point the coverage is {{FOCUS_GATE_COVERAGE}} and the
abstention precision is {{FOCUS_GATE_ABST_PRECISION}}.

### Coverage

**Plain.** The share of questions the system answers rather than refusing.

**Technical.** The proportion of the query set on which the selective
predictor emits a prediction, as opposed to abstaining. Coverage and risk
together determine the shape of the risk-coverage curve.

**Here.** The fitted point covers {{FOCUS_GATE_COVERAGE}} of the queries.

### Abstention

**Plain.** Saying "I do not have the evidence" instead of answering.

**Technical.** The withholding of a prediction by a selective predictor,
where the decision is governed by a calibrated confidence threshold. In the
conformal literature abstention carries a guarantee: with the threshold set
at a stated level, the probability that an emitted prediction is wrong is
bounded.

**Here.** The gate abstains without a model call, so a refusal costs a
fraction of an answer.

### Abstention precision

**Plain.** Of the times the system refused, how often it was right to refuse.

**Technical.** The proportion of abstentions that are correct, that is, the
cases in which the withheld answer would indeed have been wrong.

**Here.** It is {{FOCUS_GATE_ABST_PRECISION}} at the fitted operating point, and
it is the precision claim that the whole slide 18 rests on.

### Selective prediction

**Plain.** The system decides when to answer and when to keep quiet, and the
decision is measured rather than assumed.

**Technical.** A framework in which a model abstains on the inputs it cannot
answer, and the quality of that decision is measured on the risk-coverage
curve, with always-answer and never-answer baselines.

**Here.** The gate is evaluated as a selective-prediction policy with
risk-coverage, with the always-answer and never-answer baselines, and with
the random-escalation control as the third.

### Conformal prediction

**Plain.** A way of setting the decision line so that the promise about being
right has a stated guarantee attached to it.

**Technical.** A framework for distribution-free uncertainty quantification
that produces prediction sets or abstentions whose coverage guarantee holds
under exchangeability, without assumptions about the data distribution.

**Here.** The shape of the mechanism is taken from the conformal literature,
and the deck says so on slide 4. What is measured here is whether the
mechanism works on this corpus, which the literature does not answer.

### Risk-coverage curve

**Plain.** The picture of what you trade when you answer less: as the system
refuses more, the risk of being wrong goes down, and the curve shows the
price of each setting.

**Technical.** The curve of risk against coverage for a selective predictor,
where risk is the conditional error rate of the emitted predictions and
coverage is the fraction of inputs on which a prediction is emitted. A
steeper curve dominates a flatter one.

**Here.** Figure 3 on slide 15 is the whole curve, and the slide shows it
because a single threshold hides the shape behind it.

### Expected calibration error

**Plain.** On average, how far the system's stated confidence is from how
often it is actually right.

**Technical.** A weighted average, over confidence bins, of the absolute
difference between the mean confidence in a bin and the empirical frequency
of correct outcomes in that bin.

**Here.** The gate's expected calibration error is {{GATE_ECE}}.

### Brier score

**Plain.** A single number for how bad the probabilities are, counting both
over-confidence and over-caution.

**Technical.** The mean squared difference between a predicted probability
and the observed outcome, which decomposes into calibration and refinement
components.

**Here.** Not on the slides; it is in the report's derivation of the
calibration measurement, and it is the instrument to quote if the expected
calibration error is questioned as bin-dependent.

### Posterior

**Plain.** The probability after you have taken the evidence into account.

**Technical.** The probability distribution over an unknown quantity updated
by the likelihood of the observed data, as opposed to the prior distribution
before the data.

**Here.** The gate's output is a posterior over one event: that the answer is
present in the retrieved context.

### Fitted threshold and transferred threshold

**Plain.** The threshold the system was tuned with, and the same threshold
applied somewhere else.

**Technical.** A threshold selected on the data the model was fitted on, and
the same value applied to a different corpus or a different distribution. A
transferred threshold is only valid if the score distributions are
comparable.

**Here.** The transferred threshold does not transfer: the transferred arm
answered {{GEN_A_XFER_ANS_ANSWERED}} answerable questions against
{{GEN_A_NOGATE_ANS_ANSWERED}} for the ungated arm. That is finding F12, and it
is why the threshold is a configuration value rather than a property of the
method.
