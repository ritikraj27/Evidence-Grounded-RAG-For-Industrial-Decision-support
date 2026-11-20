# Speaker script: MTP Defence Deck

**Ten minutes, slide by slide, with every figure, table and formula explained.**
Ritik Raj (25IM60R12), Department of Industrial and Systems Engineering, IIT
Kharagpur. 18 November 2026.

# How to use this

The deck is `deliverables/MTP_Defence_Deck.pptx`. It carries all six measured
figures, all fifteen tables from the report and every formula the report uses.
The body is black on white with a single accent, the institute's own purple, so
it survives a projector with a bad gamma and a mono printer.

Every slide in the deck has speaker notes attached. This document is the longer
version: what to say, how to point at each element, and what the elements mean.

In the PDF form, the slide is printed above each block, so you can read the
words against the thing you are pointing at. One slide to a page.

**Total: 10 minutes 00 seconds.** The spoken words come to about nine and a
half minutes. The rest is the pause while you point at a table and the click
between slides. If you find yourself running behind, the section at the end
names the slides to compress.

The order of the talk is: the problem, the framework, the method, the
measurements, the three findings that qualify the verdict, the limitations,
the next steps.

---

# Timing plan

| # | Slide | Seconds | Clock |
|---|---|---|---|
| 1 | Title | 20 | 0:20 |
| 2 | A wrong answer costs more than no answer | 30 | 0:50 |
| 3 | The framework: five stages | 36 | 1:26 |
| 4 | Retrieval: two legs, one fusion, one quota | 28 | 1:54 |
| 5 | The confidence gate | 28 | 2:22 |
| 6 | The contradiction gate, and the form validator | 23 | 2:45 |
| 7 | Three corpora, and a benchmark that had to be repaired | 25 | 3:10 |
| 8 | Metrics, tests, and the rule that every comparison is paired | 20 | 3:30 |
| 9 | Retrieval: seven configurations on the focus corpus | 28 | 3:58 |
| 10 | The modality quota is a trade, not a gain | 15 | 4:13 |
| 11 | More candidates are not monotonically better | 15 | 4:28 |
| 12 | The gate is calibrated, and it is not excellent | 22 | 4:50 |
| 13 | The operating point, and the frontier it sits on | 28 | 5:18 |
| 14 | The benchmark answered itself | 35 | 5:53 |
| 15 | One generator, five arms, two prompt conditions | 28 | 6:21 |
| 16 | The verdict under the answering condition | 38 | 6:59 |
| 17 | What the confidence score buys, and what it costs | 38 | 7:37 |
| 18 | Long context against the pipeline | 22 | 7:59 |
| 19 | The contradiction gate: a precision of zero | 28 | 8:27 |
| 20 | Most unattributed error comes from the evidence, not the scorer | 20 | 8:47 |
| 21 | What the measurements establish | 20 | 9:07 |
| 22 | Limitations | 28 | 9:35 |
| 23 | What comes next, and a closing note | 23 | 9:58 |
| 24 | Thank you | 2 | 10:00 |

---

# The script

## 1. Title (20 seconds, clock 0:20)

**Say**

> Good morning. My work is an evidence-grounded retrieval-augmented generation
> framework for industrial decision support. Architecture, evaluation protocol,
> failure modes, and what the measurements actually show.
>
> I will give you one question and its answer, and I will show you the numbers
> behind both.

**On the slide.** The title, the subtitle, your name and roll number, the
department, the supervisor and the date. Say your name clearly and move on.
Do not read the title aloud word for word.

---

## 2. A wrong answer costs more than no answer (30 seconds, clock 0:50)

**Say**

> Let me start with why this is worth doing. In industry the corpus is not a
> wiki. It is a controlled set of documents somebody signed off on, and the
> questions are operational. Is this tolerance acceptable, which procedure step
> applies, what does the specification require.
>
> Here a refusal costs a supervisor five minutes, and a confidently fabricated
> tolerance costs a scrapped batch. So the question I set out to answer is
> narrow. When a generator is given industrial text, can a gate in the code
> decide whether the retrieved evidence actually contains the answer, and what
> is that gate worth once it has been measured properly?

**On the slide.** Three bullets on the left. The panel on the right holds the
research question. Point at the panel when you ask the question, because that
is the sentence the rest of the talk answers.

**Why this slide matters.** The asymmetry between a wrong answer and a
non-answer is the reason a gate is worth building. Everything after this slide
is about measuring that gate honestly rather than assuming it works.

---

## 3. The framework: five stages (36 seconds, clock 1:26)

**Say**

> The framework is five stages. Stage 0 validates the form of the query and can
> refuse before any retrieval happens. Stage 1 is hybrid retrieval. Stage 2
> reranks and applies a modality quota. Stage 3 is the confidence gate, which
> is the mechanism this talk is about. Stage 4 generates and scores every claim
> against the evidence it was shown.
>
> Two things about this arrangement are properties of the code. The generator
> is injected into the framework and called at exactly one line, after the gate
> has accepted, so a refused query costs no model call at all. And the form
> validator is a separate component from the gate, because they answer
> different questions.

**On the slide.**

- **The pipeline diagram**, five boxes left to right. The two purple boxes are
  the stages that can refuse, stages 0 and 3. The grey boxes cannot. Say
  "two stages can refuse" and point at the two purple ones.
- **The table** under the diagram gives each stage its input, its output and
  whether it may refuse. Read nothing from it. It is there so that a question
  about the pipeline can be answered by pointing rather than by talking.
- **The purple band** at the bottom is the non-bypassability claim. Non-bypassability
  is a property of the code here, not a convention the caller is trusted to
  follow. The only two paths that skip the gate are the comparison arms
  `rag_nogate` and `long_context`, and both are reported as separate results.

---

## 4. Retrieval: two legs, one fusion, one quota (28 seconds, clock 1:54)

**Say**

> Retrieval is a lexical leg and a dense leg, fused by reciprocal rank fusion,
> with a floor on the share of non-text chunks in the final context.
>
> Three things are asserted rather than assumed. The category filter restricts
> both legs before fusion, the reranker only permutes its pool, and the quota
> never leaves its pool.
>
> One measurement changed the design. The first dense encoder was measurably
> worse than plain BM25 on this corpus, so the fusion was carrying a leg that
> lost information. It was replaced with bge-m3.

**On the slide. The three formulas.**

- **Top left, BM25.** The standard Okapi scoring function. For each term in
  the query it multiplies the term's inverse document frequency by a saturated
  frequency factor, where the saturation depends on the ratio of the document
  length to the average document length, with `k1 = 1.2` and `b = 0.75`. Say
  "standard Okapi BM25" and move on. If somebody asks about the IDF, it is the
  Robertson-Sparck-Jones variant with a plus one offset, so a term that appears
  in every document scores zero rather than a negative number.
- **Top right, RRF.** Reciprocal rank fusion. A chunk's score is the sum over
  the ranked lists it appears in of one divided by 60 plus its rank in that
  list. A chunk missing from a list contributes nothing. `k_RRF = 60`. The
  point of fusion this way is that it needs no score calibration between the
  two legs, only their ranks.
- **Left, under BM25, the quota.** The final context must hold at least
  `q_m` chunks of modality `m`, where `q_m` is the smaller of the number of
  candidates of that modality and a ceiling of the modality's share times the
  pool size. With a table share of 0.15 and a chart share of 0.05. It is a
  **floor**, not a ceiling on text. When the pool cannot supply the floor, the
  floor is relaxed rather than invented.
- **The panel, top right.** The three invariants, asserted directly. Each one
  is a property of the code that is checked, not a convention.
- **The purple band at the bottom.** Why the dense leg changed. This is the
  point to make if anyone asks why the encoder is what it is.

---

## 5. The confidence gate (28 seconds, clock 2:22)

**Say**

> The gate is a calibrated posterior over the whole retrieved pool. Five
> query-level features go into a logistic model fitted by maximum likelihood,
> and the decision is a threshold on the posterior.
>
> The query level is a deliberate choice. With one gold chunk among about fifty
> candidates, a chunk-level classifier is right 98 percent of the time by
> answering "nothing is relevant", and the fit duly returns a large negative
> intercept. That looks like a fitted model and behaves like a constant.
> Calibrating at the query level removes it.

**On the slide. The three formulas.**

- **Top left, the feature vector `phi(q)`.** Five numbers about the whole
  retrieved pool, not about any one chunk: the top reranker score, the mean of
  the top three reranker scores, the top BM25 score, the largest fused RRF
  score, and the number of candidates above the reranker's relevance bar.
- **Top right, the posterior.** Platt's form. The standardised feature vector
  goes through a logistic function, so the output is a probability. The
  weights are fitted by maximum likelihood on a 60 percent calibration split.
- **Below the feature vector, the decision rule.** Accept when the posterior
  is at or above tau. The fitted operating point on the focus domain is
  `tau = 0.05`.
- **The panel.** Why the query level rather than the chunk level. This is the
  answer if somebody asks why the gate is not just a similarity threshold.

**One more thing to know.** The positive class is **answer-in-context
detectability**, defined operationally as the gold chunk being present in the
reranked candidate pool. The literature reserves "sufficiency" for a set-level
property, so calling this "sufficiency" would claim prior work that is not
here.

---

## 6. The contradiction gate, and the form validator (23 seconds, clock 2:45)

**Say**

> Two components refuse, for different reasons. The contradiction gate needs
> two independent branches to agree before it raises an alarm. A quantity branch
> on its own fired on citation years, and a topical subject check on its own
> was a topic check rather than a contradiction check. Requiring both cut the
> alarms from 81 to 20.
>
> The form validator runs before retrieval. The gate accepted 76.7 percent of
> the malformed stems that were pushed through it, so it is an evidence gate and
> not a form gate, and it is never credited with the validator's work.

**On the slide.**

- **The formula across the top.** A pair of chunks is flagged when branch one
  and branch two both fire. Branch one is a natural language inference model at
  threshold 0.70. Branch two requires that the two chunks talk about the same
  measured quantity of the same instance, not merely about the same topic.
- **The panel on the left.** Why the conjunction. The quantity branch alone
  keyed numbers to the nearest distinctive word and fired on citation years.
  The topical subject check alone was a topic check. Requiring both cut the
  alarms from 81 to 20, and 20 is a number a reader can check.
- **The panel on the right.** The form validator. It refused 25 of 25
  hand-authored malformed queries and 0 of 35 well-formed ones, at 2.6
  microseconds per query. The counterfactual is the memorable part: reusing the
  benchmark builder's question-generation rule as a runtime check would have
  refused 100 percent of hand-labelled well-formed questions. A filter written
  for one purpose does not fit another, and its false rejection rate has to be
  measured before it ships.

---

## 7. Three corpora, and a benchmark that had to be repaired (25 seconds, clock 3:10)

**Say**

> Three corpora, and their roles do not overlap. The supply chain focus corpus
> carries 735 chunks from 14 documents and is where the ablation, the gate and
> the generation experiments run. The six category industrial corpus carries
> 2383 chunks from 46 documents and is where the transfer study and the long
> context cost run. The federal regulatory corpus is where the contradiction
> detector's phenomenon lives.
>
> The benchmark needed three repairs. Thirty of the answerable questions carried
> an answer label attached to the wrong question. The unanswerable half was
> separable from the question text alone, so the headline refusal rate measured
> the benchmark rather than the framework. And the runtime validator refused
> three of 176 queries, all generator artefacts.
>
> The audit instrument was kept, because it is the instrument that found the
> defects.

**On the slide.**

- **The table** gives the role, chunk count, document count and query count for
  each corpus. The two question sets are never mixed, because they are used for
  different experiments.
- **The three panels** are the three repairs. Repair 1 is the answer-label
  defect, and the important detail is that the gold *chunk* was always right,
  so the retrieval-side numbers were never affected. Only the answer-side
  accuracy was depressed, and equally for every arm. Repair 2 is the
  unanswerable class, which comes back on slide 14. Repair 3 is the form check.
- **Be honest about the substitute corpus.** The primary corpus of proprietary
  supply-chain documents cannot be redistributed, so every measurement runs on
  a public substitute that ships with its provenance. Each document carries the
  upstream identifier, a SHA-256, the chunk count and the licence.

---

## 8. Metrics, tests, and the rule that every comparison is paired (20 seconds, clock 3:30)

**Say**

> Every comparison is paired, because the arms answer the same questions.
> Retrieval comparisons use the Wilcoxon signed rank test. Generation
> comparisons use the exact McNemar test, and the test is applied per class,
> because a gate can improve the unanswerable class and damage the answerable
> class. One number for both would hide the trade.

**On the slide. The three formulas.**

- **Top, the retrieval metrics.** Recall at a cutoff is the share of the gold
  set that lands in the top `k`. MRR is the mean of one over the rank of the
  gold chunk. nDCG at `k` is the discounted cumulative gain over the ideal
  ranking, and the DCG itself, in the formula at the right, discounts by
  `log2(i+1)` so that a hit in position one counts for more than a hit in
  position ten.
- **Bottom left, the two generation rates.** The answer rate on the
  unanswerable class is the share of that class the arm answered. The refusal
  precision is the share of refusals that land on the unanswerable class. The
  second one is the number this whole talk ends up defending.
- **The bullets.** The Wilcoxon test carries Cliff's delta and Cohen's `dz` as
  effect sizes. For McNemar, `b` counts the questions the baseline answered and
  the arm refused, and `c` counts the other way round. The exact two-sided
  p-value is the formula on slide 15. Proportions carry Wilson score intervals.
- **The last bullet.** One generator, five arms, one of which refuses the same
  number of questions at random. Without that arm, refusing on a coin flip and
  refusing on a calibrated score look identical on the easiest metric to report.

---

## 9. Retrieval: seven configurations on the focus corpus (28 seconds, clock 3:58)

**Say**

> Seven configurations over the same 32 answerable queries, with a paired
> Wilcoxon signed rank test on every comparison.
>
> The dense leg is significantly worse than BM25, 0.969 against 0.812, a paired
> difference of -0.156 at p of 0.025. That is why the encoder changed. Fusion
> recovers the loss and reaches 1.000, a paired improvement of +0.188 at p of
> 0.014, and it improves the ordering too, MRR from 0.652 to 0.798.
>
> The claim for fusion is narrow. It stopped being a loss. It did not become a
> significant win over plain BM25 on its own.
>
> The table on the right is the transfer study on the six category corpus. The
> reranker's gain survives the change of corpus, +11.1 points of MRR at p of
> 0.00093. The fusion's recall advantage over BM25 does not.

**On the slide.**

- **The main table.** Seven rows, A to G, each one adding a mechanism to the
  one above it. The last column is table-specific Recall@10, and it is the only
  place the dense leg loses table recall too, at 0.875.
- **The transfer table.** Two comparisons, A to C and C to D. The row that
  matters is C to D: fusion to rerank, +0.111 MRR, +0.085 nDCG, p of 0.00093
  and 0.0018. The reranker helps on this corpus and slightly hurts on the focus
  corpus, where it moves MRR by -0.3 points and nDCG by -1.1 points, neither
  significant. That is why the sentence "the reranker buys ordering, not
  recall" is always said with its corpus attached.

---

## 10. The modality quota is a trade, not a gain (15 seconds, clock 4:13)

**Say**

> The modality quota is a trade, not a gain. On the industrial corpus the
> pre-rerank quota buys 0.8 points of table recall and gives up 0.8 points of
> overall recall, and the post-rerank quota lands on exactly the no-quota
> operating point. On the focus corpus the post-rerank quota gives up 3.1
> points of overall recall while table recall stays at 1.000.
>
> None of the three differences is statistically significant. So the placement is
> a configuration value, and the ranking is reported with its corpus attached.

**On the slide.**

- **The figure.** Overall Recall@10 on the horizontal axis against
  table-specific Recall@10 on the vertical axis. Black circles are the focus
  corpus, grey squares the industrial corpus. Each letter is one ablated
  system, and the arrows show what the modality quota does. A good system is up
  and to the right. The arrows point left or down, never both ways up.
- **The table.** The three corpora and the two placements, with the p-value of
  each difference. All three p-values are above 0.05.
- **The thing to say out loud.** A claim that the quota belongs before the
  cross-encoder would not hold on every corpus.

---

## 11. More candidates are not monotonically better (15 seconds, clock 4:28)

**Say**

> The candidate pool curve peaks and then declines. On the focus corpus
> Recall@10 peaks at a pool of ten and falls back to 0.969 at twenty, fifty and
> a hundred.
>
> What is happening is visible in the recall at twenty, which keeps rising as
> the pool grows. The gold chunk is still being found, and then the reranker
> pushes it out of the ten-chunk context. A larger pool costs ordering without
> adding the answer.

**On the slide.**

- **The top panel** of the figure plots Recall@10 and Recall@20 against the
  pool size. The dashed line is Recall@20 on the focus corpus, and it stays at
  1.000 while the solid line, Recall@10, drops away. That gap is the whole
  story.
- **The bottom panel** plots the number of gold chunks retrieved at ten but
  displaced from the context, which is zero up to a pool of ten and then jumps
  to three on the focus corpus.
- **The table** gives the five pool sizes with Recall@10, Recall@20 and MRR.
  MRR falls from 0.807 at a pool of five to 0.795 at a hundred, so the extra
  candidates really do cost ordering.
- **The exception.** On the industrial corpus the gold chunk is still arriving at
  fifty, so Recall@20 reaches 1.000 at a pool of fifty while Recall@10 stays at
  0.988. Some 1.21 percent of gold is retrieved and then pushed out.

---

## 12. The gate is calibrated, and it is not excellent (22 seconds, clock 4:50)

**Say**

> The gate is calibrated on the held-out evaluation half, and it is not
> excellent. The expected calibration error is 0.1044 and the Brier score is
> 0.1510. The industrial gate tracks the diagonal, at an ECE of 0.075. The focus
> gate does not, and it puts most of its queries in the lowest confidence bin,
> where few of them have an answer in context.
>
> The number is reported rather than improved by refitting, because it describes
> one fitted artefact on one fixed split.

**On the slide. The two formulas.**

- **ECE, top right.** The expected calibration error is a weighted sum over
  equal-width probability bins of the gap between the observed accuracy in the
  bin and the mean predicted probability in that bin. Zero is perfect
  calibration. The weighting is the share of queries in the bin.
- **Brier, below it.** The mean squared difference between the predicted
  probability and the observed label, over all the queries. Lower is better.
  The Brier score is the one to quote when somebody wants a single number.

**The table** gives both metrics for the focus gate, plus the base rate of
answer-in-context, which is 0.182, and the retriever's own recall of the gold
chunk, which is 1.000. The base rate matters: the gate is trying to predict a
rare positive.

**The figure.** The upper panel plots observed answerability against mean
predicted probability per bin, with the diagonal as perfect calibration. The
lower panel is the number of queries in each bin, and that is what shows the
focus gate's problem. It is not badly spread, it is badly placed.

---

## 13. The operating point, and the frontier it sits on (28 seconds, clock 5:18)

**Say**

> The threshold is chosen by a stated rule: the highest tau that still answers
> at least 90 percent of the answerable queries, which gives 0.05.
>
> Two readings of this table matter. The gate is precise where it refuses. At
> the fitted operating point the abstention precision is 0.963, so almost every
> refusal lands on a question that should have been refused. And the frontier
> is real. Every extra refusal is paid for in coverage, and the price climbs
> steeply past tau of 0.15. At 0.05 the coverage is 0.693; by 0.30 it is 0.170.

**On the slide.**

- **The table** is the full sweep, seven thresholds. Read the columns this
  way: `tau` is the threshold, the next two columns are what happens to the two
  classes, the fourth is the abstention precision, and the last is the fraction
  of all queries the gate answers. Moving down the table, coverage falls from
  0.693 to 0.017 and the unanswerable refusal rate rises from 0.361 to 1.000.
- **The figure** is the same trade in the risk-coverage form. The horizontal
  axis is coverage, the fraction of queries answered. The vertical axis is the
  risk, which is the chance that an answered query has no answer in its
  context. Two degenerate policies bound the curve: always answering, which is
  the horizontal line at the base rate of the negative class, and always
  refusing, which is the vertical line at zero risk and zero coverage. The
  black curve is the focus gate and the grey one the industrial gate. The
  fitted operating points answer 0.693 and 0.691 of all queries.
- **The honest note.** The focus gate buys very little over answering
  everything. That is visible on the curve and it is stated in the report.

---

## 14. The benchmark answered itself (35 seconds, clock 5:53)

**Say**

> This is the finding that took the most work, and it changes the headline.
>
> The unanswerable half of the benchmark was separable from the question text
> alone. A classifier seeing only the query, with no retrieval, no evidence and
> no corpus, told answerable from unanswerable at ROC AUC 0.999. One regular
> expression caught 76 percent of the unanswerable class with no false positive
> at all, because that class named a fabricated identifier that no answerable
> question carried.
>
> So the headline refusal rate of 91.7 percent was an upper bound on a benchmark
> artefact, not a measurement of the framework. The class was rebuilt with
> corpus-anchored definitions and a structural twin for every repaired question,
> same stem, same subject size, matched subject-length distribution, no word in
> common.
>
> The true rate is 23.6 percent.

**On the slide.**

- **The figure** is the ROC curve of the question-only classifier. The solid
  black curve in the top left corner is the focus corpus before the repair,
  with AUC 0.999 against a permutation null of 0.455. The star on the left
  axis marks the regular expression: it catches 76.4 percent of the
  unanswerable questions with zero false positives. The dashed black curve is
  after the repair, at AUC 0.608.
- **The table** is the before and after, and its first two rows are two
  different classifiers, both of which see only the question. The shape
  separability row is the one the figure plots: 0.999 against 0.608. The
  question-only policy row is a rule-based detector: 0.675 against 0.564.
  Then the shortcut detection, 76.4 percent against 0.0 percent, and the gate
  refusal rate, 91.7 percent against 23.6 percent.
- **The two strata.** After the repair the gate refuses 26 of 110 of the
  corpus-anchored hard stratum and 26 of 34 of the out-of-domain stratum. That
  gap is the finding. What the gate detects is a **recognisable** unanswerable
  question, one drawn from outside the corpus or one whose subject is plainly
  absent. It is much weaker on the on-topic-but-unanswered case, where the
  corpus discusses the subject but does not state the answer.
- **Why a 24 percent rate matters more than a 92 percent rate.** A 24 percent
  rate on the hard stratum is a different instrument from a 92 percent rate on
  an easy one, and the first number is the one a deployment would meet.

---

## 15. One generator, five arms, two prompt conditions (28 seconds, clock 6:21)

**Say**

> One generator, five arms, each differing only in what it removes. The two
> prompt conditions differ by a single sentence: under one the generator may
> decline, and under the other it must answer. Model, questions, retrieval,
> scorer and temperature stay identical either way.
>
> The table at the bottom is why the replication on a second generator could
> not be run. That model returned no text on 24 of 66 questions, 23 of them on
> the benchmark's table-lookup family. Raising the output budget fourfold
> rescued 13 and left 11 still empty. The model spends its budget thinking and
> returns nothing.
>
> An empty completion is neither an answer nor a refusal. A run like that is
> recorded as not run, with the reason, because a rate quoted from a run that
> did not happen is indistinguishable from a rate that did.

**On the slide.**

- **The arms table, top left.** Read the `rag@random` row carefully: it removes
  the confidence score and keeps the refusal budget, so refusals are drawn at
  random. That is the control that makes the other rows readable.
- **The formula, top right.** The exact two-sided McNemar p-value, where `b` and
  `c` are the discordant counts and `n` is their sum. It is exact because the
  binomial sum is computed, not approximated.
- **The table at the bottom.** Two generators, and how many questions each one
  returned no text on. MiniMax-M3 returned text every time. MiniMax-M3.1-Flash
  did not, and four times the budget did not fix it.
- **Why the two conditions matter.** Under the cautious prompt alone the
  generator refused most unanswerable questions by itself, the gate's refusals
  were largely redundant, and the arms could not have been told apart. That
  setup would have produced a null result that meant nothing.

---

## 16. The verdict under the answering condition (38 seconds, clock 6:59)

**Say**

> This is the slide the talk is built around. Under the prompt that requires an
> answer, the generator cannot decline on its own, so the gate cannot be
> redundant.
>
> The ungated arm answers 135 of 144 unanswerable questions. The fitted gate
> answers 76, and the paired exact McNemar test gives p below 0.001 on the
> unanswerable class, with `b` of 60 and `c` of 1. The cost is on the same row.
> It answers 30 of 32 answerable questions where the ungated arm answers 32 of
> 32.
>
> Under the cautious prompt the rate falls from 0.535 to 0.417 for the same two
> answerable questions, and the paired test is significant there as well.
>
> So the verdict is supported under both prompt conditions.

**On the slide.**

- **The table.** Read it as five rows, one per arm, and four columns. The
  second column is the unanswerable class: how many of the 144 the arm
  answered. The third column is the answerable class: how many of the 32 it
  answered. The last two columns are the paired McNemar test, applied
  separately to each class. `none` means that arm is the baseline for that
  comparison, so there is nothing to test it against.
- **The `b` and `c` values.** On the unanswerable class the fitted gate has
  `b = 60`, meaning 60 questions the baseline answered and the gate refused,
  and `c = 1`, one question the baseline refused and the gate answered. On the
  answerable class `b = 2` and `c = 0`. That second pair is the whole story,
  and it comes on the next slide.
- **The purple band.** The verdict, and the cautious-condition numbers. The
  two-condition design is stated here because it is what stops a cautious null
  from being read as "confidence gating does not work".
- **The last row.** The transferred arm answers only 3 of 144 unanswerable
  questions and only 6 of 32 answerable ones. The threshold was fitted on one
  half of the cross-category corpus and applied unchanged to the other half,
  and it over-refuses badly. This is the clearest evidence that a calibrated
  threshold does not transfer.

---

## 17. What the confidence score buys, and what it costs (38 seconds, clock 7:37)

**Say**

> Now the finding most likely to be reported wrongly.
>
> The confidence score does not buy a lower answer rate on unanswerable
> questions. The random control reaches 0.604, which is worse than the fitted
> gate's 0.528 and far below the ungated arm's 0.938. It gets there by
> refusing an arbitrary set of the same size, and some of those refusals are
> answerable questions. Refusing at random is already a large improvement over
> never refusing, because most questions in a benchmark are unanswerable.
>
> What the score buys is where the refusals land. The gate spends two refusals
> on answerable questions. The random control spends eleven. That is a precision
> claim about refusals, and the paired test on the answerable class is where it
> is established, p of 0.500 for the gate against p of 0.001 for the control.
>
> The cost side is in the table. The gate removes 59 wrong answers and costs one
> correct answer under the entailment test. Do not read the accuracy columns as
> a quality gain. The gated arm answers an easier subset, because a gate
> declines the hardest questions. That is the selection effect, and it is why
> per-answer accuracy cannot be compared across arms with different coverage.

**On the slide.**

- **The table** counts from the records. Four arms. Answered, of which wrong,
  correct under the entailment test, correct under the key term test. The
  ungated arm answers 167, of which 135 are wrong. The fitted gate answers 106,
  of which 76 are wrong.
- **The two big numbers.** `2` and `11`. These are the answerable questions
  each arm refused. The gate's paired test on the answerable class gives p of
  0.500, so its two refusals are indistinguishable from chance in the good
  direction. The control's eleven refusals give p of 0.001, so the control is
  significantly damaging the answerable class.
- **The sentence to have ready.** A report that said "the gate answers fewer
  unanswerable questions" would be true and it would be misleading. The claim
  is about precision, and the random control is what makes the difference
  visible.

---

## 18. Long context against the pipeline (22 seconds, clock 7:59)

**Say**

> Long context was measured on cost and on coverage, and it does not win. 74
> times the tokens per query, and 58.8 times the input cost once the cached
> prefix pricing is applied, because 33 percent of the long context tokens are
> cache reads at a fifth of the base rate. The token ratio on its own is off by
> an order of magnitude, so a token ratio must never carry an argument about
> money.
>
> On coverage the whole-corpus prompt answered 32 of 32 answerable questions,
> the same as the ungated pipeline. On the retrieval side the evidence is not
> lost in a big context. The gold chunk lands in the top ten for 0.969 of the
> focus queries and 0.902 of the cross-category queries, at a median rank of
> one.

**On the slide.**

- **The three panels.** The token ratio, the input cost ratio, and the share of
  long-context tokens that are cache reads. The third number is the one that
  reconciles the first two.
- **The bullets, left.** Cost, coverage and quality. The accuracy numbers are
  0.406 for the whole-corpus arm against 0.667 for the gated arm, and the
  margin is not significant under a length-controlled re-scoring of the same
  answers. No superiority claim is made over long-context prompting.
- **The panel, right.** The retrieval-side proxy. It is the cheap half of the
  comparison and the part that generalises: a retriever that finds the answer
  at median rank 1 has no use for the other 735 chunks.
- **The limit to state.** The cross-category corpus is 680,417 tokens, 5.2
  times the 128K window, so the quality half of that comparison could not be run
  there and it is settled on coverage and cost alone.

---

## 19. The contradiction gate: a precision of zero (28 seconds, clock 8:27)

**Say**

> The contradiction gate's precision against reader labels is zero. Twenty
> labelled alarms, none confirmed.
>
> The annotators do not share a model, both read the sheet blind to the
> detector's scores, and both were 14 of 14 on a control set with known labels.
> They still confirmed nothing, and they agree with each other on 101 of 101
> pairs.
>
> The readers also found no contradictions in a random sample of 80 pairs the
> gate did not flag. So this corpus holds concept-level prose rather than
> instance records, and it does not contain the phenomenon the mechanism
> detects. A detector that finds nothing in a corpus that has nothing to find
> is not a failing detector. The mechanism is unproven rather than disproven,
> and it is reported as a null with a 16.1 percent upper bound.

**On the slide.**

- **The figure.** Each row is a stratum. The horizontal axis is the precision
  of the detector's alarms, with the interval bars. A filled marker means the
  point estimate clears the framework's 0.5 calibration floor and the branch
  would act. A hollow marker means it does not, and the findings would be
  withheld. The top row, focus corpus semantic branch, is hollow, at a
  precision of 0.0 on a base rate of 0.0. The industrial semantic branch
  reaches 0.65 against a base rate of 0.35, and is filled, so it would act.
  The industrial quantity stratum is hollow and its precision was never
  established: the branch fired
  on 13 of 119 scored pairs, but its precision was never measured.
- **The table.** The six numbers that make the null result checkable, including
  the annotators' own agreement and the upper bound.
- **What to say about the two detector defects.** Both were real and both were
  fixed. One keyed numbers to the nearest distinctive word and fired on
  citation years. The other let topical similarity through on its own. They
  were not the reason the remaining alarms went unconfirmed.

---

## 20. Most unattributed error comes from the evidence, not the scorer (20 seconds, clock 8:47)

**Say**

> The same answers, scored against two evidence sets. The grounded claim error
> rate is 0.118 over the evidence the arm was shown, and 0.542 over the gold
> chunk. Most of what the framework's own attribution cannot explain comes from
> the evidence it was given, which is a retrieval problem rather than a scoring
> problem.
>
> The answer position effect holds in three of the four measurements and ties in
> the fourth, so it is stated with its magnitude rather than as a rule.

**On the slide.**

- **The table.** Five error measures, each against the retrieved evidence and
  then against the gold evidence. The gap between the columns is large and it
  runs the same way every time. Because the gold chunk was always right, this
  is a clean comparison.
- **The panel.** How a claim is scored. Supported means a chunk entails it at
  threshold 0.5 or the evidence states it literally. Two thresholds separate
  the classes: 0.80 for a claim to be called grounded, 0.45 for it to be called
  inferred, and anything below is uncertain. A bare value is scored by the
  literal test alone, because the entailment model cannot adjudicate a number
  that is not a proposition.
- **The one detail worth pointing at.** The gold chunk is never force-added to
  the evidence set, so nothing outside the evidence can support a claim. That
  is what makes the two columns comparable.

---

## 21. What the measurements establish (20 seconds, clock 9:07)

**Say**

> Fourteen findings, each with the number that carries it. Every row is a
> measurement against an archived result file.
>
> Three qualify the verdict. F8, the confidence score buys refusal precision
> rather than a lower answer rate. F10, the contradiction gate's precision
> against reader labels is zero. F12, a calibrated threshold does not transfer
> across corpora. Those three are worth reading twice. The rest are in the
> report.

**On the slide.** The table. Leave it up while you talk through the three
qualifying findings. It is the slide an examiner will photograph, so it should
be on screen while you say the sentence about the three.

---

## 22. Limitations (28 seconds, clock 9:35)

**Say**

> Eight limitations. Two of them matter most, and I will name them first.
>
> L1: one generator. The hypothesis is supported for the generator tested, not
> in general. That is the largest gap in this work. L2: an encyclopaedic
> corpus, not procedural documentation, and the contradiction detector's
> phenomenon is measurably absent from it.
>
> The rest are statistical power, with several nulls being nulls of this corpus
> at this size; model-based rather than human annotation; the fact that the
> hallucination rate on generated text is a different quantity from the
> refusal rate; the fact that a refusal is not an answer; and English in one
> jurisdiction.

**On the slide.** The eight tagged lines. Do not rush this slide. L1 and L2 are
the two that get raised in the questions, and they are better raised here than
waiting to be found in a question.

---

## 23. What comes next, and a closing note (23 seconds, clock 9:58)

**Say**

> Six next steps, in the order that would change what this work can claim.
> Repeating the comparison on a generator that returns text is first. Publishing
> the corrected benchmark and the shortcut audit is last, because that part
> outlives the report.
>
> The closing note is this. The most useful thing this produced was not the
> framework. It was finding that two of its own instruments were reporting
> numbers a careful reader could not trust, and changing the headline rather
> than explaining it away. A framework's contribution is only as good as the
> instruments that measured it.

**On the slide.** The six numbered steps, each with the reason it is on the
list. The purple band at the bottom is the closing note. End on the instruments,
not on the architecture. The contribution is the measurement.

---

## 24. Thank you (2 seconds, clock 10:00)

**Say**

> Thank you. I am happy to take questions.

---

# If you are running behind

The two slides that can be compressed without losing an argument are slide 10
(the modality quota) and slide 11 (the candidate pool). Both are retrieval
results whose place in the argument is carried by the findings table on slide
21. Compressing both saves 30 seconds.

Slide 20 (attribution) can be reduced to one sentence, since F13 carries it.
That saves 20 seconds.

Slide 23's next-steps list can be pointed at rather than read, if you have
already made the closing point. That saves 20 seconds.

**Do not compress** slides 2, 14, 16 and 17. Those four carry the problem, the
benchmark repair, the verdict and the finding most likely to be reported
wrongly. They are the talk.

---

# Questions to expect

**"Why is the refusal rate only 23.6 percent? That sounds low for a gate."**

Because the class it is measured on is the hard stratum, where the corpus
discusses the subject but does not state the answer. On the out-of-domain
stratum, where the question comes from outside the corpus entirely, the gate
refuses 26 of 34. Before the benchmark repair the rate was 91.7 percent, and
that number was measuring a shortcut in the benchmark rather than the system.
A gate that detects a recognisable unanswerable question is worth having. A
gate that detects an absent answer is what the report does not claim.

**"Is the improvement just the gate refusing more questions?"**

That is the question the random control exists to answer. The random control
refuses the same number of questions at random, and it lands in a similar place
on the unanswerable class, at 0.604 against the gate's 0.528. The difference
shows up on the answerable class, where the gate spends 2 refusals and the
control spends 11. So the claim is about precision, and it is a precision claim
about refusals.

**"What is the cost of the gate?"**

Coverage. Every extra refusal is paid for in coverage, and the price climbs
steeply past tau of 0.15. At the fitted operating point the gate answers 30 of
32 answerable questions where the ungated arm answers 32 of 32, and it removes
59 wrong answers for the cost of one correct answer under the entailment test.
Whether that trade is worth making is a domain judgement, and these
measurements do not settle it.

**"The contradiction gate did not work. Why keep it?"**

Because the corpus does not contain the phenomenon it detects. The readers found
no contradictions in a random sample of 80 pairs the gate did not flag either,
so this is a statement about the corpus and not about the detector. It is
reported as unproven with a 16.1 percent upper bound rather than dropped, and
the two detector defects the audit exposed were real and were fixed.

**"How do you know the framework is better than just BM25?"**

On the focus corpus it is not, on recall. The dense leg is significantly worse
than BM25, fusion recovers it to 1.000, and the reranker moves MRR by -0.3
points, which is not significant. On the six-category corpus the reranker
moves MRR by 11.1 points at p of 0.00093. So the retrieval side of the claim
carries its corpus, and the contribution of the framework is the gate and the
measurement of it rather than the retrieval.

**"Why is the answer position effect not a finding?"**

Because the direction replicates in three of the four corpus-and-protocol
measurements and ties in the fourth, and the magnitude does not replicate. It is
stated with its magnitude rather than as a rule.

**"Can the framework be deployed?"**

Not on this corpus as it stands. The scope is narrowed to match what was
measured: industrial-engineering encyclopaedic text rather than practitioner
documentation, one generator rather than one model class, English and one
jurisdiction. The cost-coverage-reliability frontier is the deliverable, and a
deployment team would have to calibrate the threshold on its own corpus and
audit its own benchmark for the same shortcut before it trusted any number.

**"How was the benchmark shortcut found?"**

By auditing it, and by keeping the instrument. A classifier was trained on the
question text alone, with no retrieval and no corpus, and it separated the two
classes at ROC AUC 0.999. The pre-repair benchmark sits beside the repaired one
so that every before-and-after claim can be regenerated, and the shortcut audit
is the first of the six next steps to be published separately.

---

# One page to keep in front of you

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
