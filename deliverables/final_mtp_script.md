# Speaker script: The Final Defence Deck

**Ten minutes, slide by slide, with every figure, table and formula explained.**

Ritik Raj (25IM60R12), Department of Industrial and Systems Engineering, IIT Kharagpur, under the supervision of Dr. Sri Krishna Kumar

# How to use this

This is the speaker script for the final defence deck, `final_mtp.pptx`. It
is the words to say, slide by slide, and it is meant to be read beside the
deck rather than instead of it. The deck is what the panel sees; this is what
you say.

**How the document is laid out.** The timing plan comes first, and it gives
the seconds each slide is allowed and the clock time it should begin at. Then
one section per slide, in the order the slides run. Each section carries the
words to say, what is on the slide and where to point, and why the slide is
there at all.

**If a word is used that you have not had to think about,** the terminology
guide, `MTP_Terminology.pdf`, gives every keyword of the work twice: once in
ordinary words and once in the technical words, with the number that belongs
to it. It is the layer between this script and the report.

**In the PDF form the slide is printed above its section**, so you can read
the words against the thing you are pointing at. One slide to a page, and the
page a slide is on can be found by counting.

**Total: 9 minutes 47 seconds.** The spoken words come to about nine and a
half minutes. The rest is the pause while you point at a table and the click
between slides. If you find yourself running behind, the section at the end
names the slides to cut.

**The order of the talk is the problem, the framework, the method, the
measurements, the findings that qualify the verdict, the limitations, and the
next steps.**

# Timing plan

| # | Slide | Seconds | Clock |
|---|---|---|---|
| 1 | Title | 15 | 0:15 |
| 2 | A wrong answer and a non-answer do not cost the same | 27 | 0:42 |
| 3 | Four objectives, six contributions | 19 | 1:01 |
| 4 | The literature, in eight threads | 18 | 1:19 |
| 5 | The gap, and what this work adds | 24 | 1:43 |
| 6 | The framework is a five-stage pipeline | 25 | 2:08 |
| 7 | The confidence gate, and its three formulas | 25 | 2:33 |
| 8 | The retrieval stack, and its three formulas | 23 | 2:56 |
| 9 | The corpora and the benchmark | 19 | 3:15 |
| 10 | The benchmark, and the audit that checks it | 35 | 3:50 |
| 11 | The metrics and the protocol | 16 | 4:06 |
| 12 | Retrieval: seven configurations over the same 32 queries | 31 | 4:37 |
| 13 | The quota has no universally better placement | 20 | 4:57 |
| 14 | More candidates are not monotonically better | 24 | 5:21 |
| 15 | The operating point, and the frontier behind it | 22 | 5:43 |
| 16 | The gate on the unanswerable class | 26 | 6:09 |
| 17 | The framework's own hypothesis, under two conditions | 31 | 6:40 |
| 18 | What the confidence score actually buys | 34 | 7:14 |
| 19 | Long context against the pipeline | 31 | 7:45 |
| 20 | The contradiction gate: a precision of zero | 21 | 8:06 |
| 21 | The findings, all fourteen | 19 | 8:25 |
| 22 | What the measurements support, and what they do not | 24 | 8:49 |
| 23 | The limitations | 18 | 9:07 |
| 24 | The conclusion, and the future work | 23 | 9:30 |
| 25 | The references | 7 | 9:37 |
| 26 | Thank you | 10 | 9:47 |

The total is 9:47, which is the spoken words at 140 words a minute plus the pause between slides. The per-slide seconds are the spoken words, and the clock column is where you should be when that slide comes up.

# The script

## 1. Title (15 seconds, clock 0:15)

**Say**

Good morning. I am Ritik Raj, 25IM60R12, from the Department of Industrial and Systems Engineering, under the supervision of Dr. Sri Krishna Kumar. My work is an evidence-grounded retrieval-augmented generation framework for industrial decision support.

**On the slide.**

- The title, and the subtitle, which names the four things the talk will cover.
- Your name, roll number, department and supervisor.
- Nothing else. Let the slide sit.

**Why this slide matters.** It names the four things the talk will cover, so the room knows the shape of the next ten minutes before the argument starts.

## 2. A wrong answer and a non-answer do not cost the same (27 seconds, clock 0:42)

**Say**

A retrieval-augmented generator reads a corpus and answers a question. In industry that corpus is not a wiki but a controlled set of signed-off documents, and the questions are operational. A refusal costs a supervisor five minutes; a fabricated tolerance costs a scrapped batch. So the question is not whether this works, but whether the deciding component can be measured at all.

**On the slide.**

- The left column, which gives the industrial corpus and the cost of the two outcomes.
- The card on the right, which bounds the claims: one generator, an encyclopaedic corpus, one corpus for long context.
- The takeaway band at the bottom, which is the research question in one sentence.

**Why this slide matters.** It starts from the industry rather than from the method, because a refusal that costs a supervisor five minutes and a fabricated tolerance that costs a scrapped batch is a cost the room already understands. The card on the right is what keeps the claims honest: one generator, an encyclopaedic corpus, one corpus for long context.

**If you are asked "what is the industry?"** Supply-chain procedures, equipment manuals, calibration records and regulatory text. The questions are whether a tolerance is acceptable, which step of a procedure applies, and what a specification requires.

## 3. Four objectives, six contributions (19 seconds, clock 1:01)

**Say**

Four objectives and six contributions, each one something that had to be built and then measured. The third decides the design of the experiment. If the generator may decline on its own, the gate's contribution cannot be separated from the generator's willingness to answer.

**On the slide.**

- The two tables. Read the objectives, not the contributions.
- The takeaway band, which says why the third objective decides the design of the experiment.

**Why this slide matters.** The third objective is the one that shapes the experiment, so the slide says why before the panel reads the tables. If the generator may decline on its own, the gate's contribution and the generator's willingness to answer are the same number.

## 4. The literature, in eight threads (18 seconds, clock 1:19)

**Say**

The literature, in eight threads. Two things to take from it. The abstention mechanism and the retrieval stack are prior art; the measurement is not. And the selection effect means a null under a cautious prompt must never be reported as gating failing.

**On the slide.**

- The fourth column, what is taken from each thread. That column is the point of the table.
- The third column, the representative work, if a thread is asked about.

**Why this slide matters.** The table is not a review for its own sake. It is there to say two things: that the mechanisms are prior art, and that a null under a cautious prompt has to be described in a particular way. Both of those are needed later, when a null is reported.

## 5. The gap, and what this work adds (24 seconds, clock 1:43)

**Say**

So here is the gap. The literature already gives the abstention mechanism, the retrieval stack and the benchmark desiderata. What it does not settle is what a confidence score buys once the generator may not decline, whether the shortcuts that inflate refusal rates carry over, and where the frontier sits for a gate on industrial text.

**On the slide.**

- The middle card, which is the gap: three questions the review does not settle.
- The right card, which is what this work adds.
- The takeaway band, which says the architecture is not the contribution.

**Why this slide matters.** The contribution is stated as a measurement and not as an architecture, because the architecture really is prior art, and saying so is the position that survives a question. The middle card is the gap, and it is the gap the review leaves, not the gap the work fills.

## 6. The framework is a five-stage pipeline (25 seconds, clock 2:08)

**Say**

The framework is a five-stage pipeline. Stage 0 validates the query form, stage 1 does hybrid retrieval, stage 2 reranks and applies the quota to give a final context of ten chunks, stage 3 is the gate and it may refuse, stage 4 generates and tags each claim. The gate is in code, so it cannot be bypassed.

**On the slide.**

- The diagram, the five stages left to right.
- The last column of the table, which marks the two stages that may refuse: the form validator and the gate.
- The input and output columns, which are read rather than said.

**Why this slide matters.** Non-bypassability is a property of the code rather than a claim about it, and the table says which two stages may refuse. The generator is called at one place, after the gate has accepted, so a refused query costs no model call at all.

## 7. The confidence gate, and its three formulas (25 seconds, clock 2:33)

**Say**

This is the mechanism the talk is about. The gate asks a query-level question: does the retrieved context contain evidence the question can be answered from? Five statistics of the candidate pool go into a Platt scaling, which gives a probability, and a threshold decides. Every feature describes the pool, not a chunk, which removes the degenerate chunk-level solution.

**On the slide.**

- The middle formula, which is the gate: the feature vector, the probability, the threshold.
- The symbol table on the right, which names every symbol.
- The note beneath it, which says where the numbers came from.

**Why this slide matters.** The feature vector is described as five statistics of the pool rather than of a chunk, because that is what makes the gate query-level. A chunk-level score admits the degenerate solution, which is high whenever the question looks familiar whether or not the answer is there.

**If you are asked "why five features, why not one?"** The five are the top reranker score, the mean reranker score, the top BM25 score, the best fused score, and the number of chunks above the reranker's own relevance bar. They are fitted together by maximum likelihood on 60 percent of the queries, and the calibration split's mean and deviation standardise them.

## 8. The retrieval stack, and its three formulas (23 seconds, clock 2:56)

**Say**

The retrieval stack is all from the literature. A lexical BM25 leg and a dense leg, fused by reciprocal rank fusion, then a cross-encoder reranker, with a floor on the share of tables and charts. The quota is a floor, not a ceiling, and it is relaxed when the pool cannot supply it.

**On the slide.**

- The three formulas: BM25, the rank fusion, the quota.
- The symbol table on the right.
- The note beneath it, which says the quota is a floor and not a ceiling.

**Why this slide matters.** Every mechanism on this slide is named and credited, so that nothing later can be read as a claim of novelty. The quota is described as a floor rather than a ceiling, because slide 13 shows that where it is applied is a configuration value.

## 9. The corpora and the benchmark (19 seconds, clock 3:15)

**Say**

Four corpora, and each has one job. The focus corpus carries the ablation, the gate and the generation experiment; the six-category corpus the cross-category transfer, and the industrial corpus the pool curve. Their numbers are never mixed, and every document ships with a hash.

**On the slide.**

- The corpus table, and the first column, which gives each corpus one job.
- The bullets under it, which say the focus corpus carries 32 answerable and 144 unanswerable questions.
- The card on the right, which says the corpus ships with its provenance.

**Why this slide matters.** Four corpora with one job each, and the rule that their numbers are never mixed, because every number in the rest of the talk is quoted with the corpus it came from. A number without its corpus is the easiest thing in this work to misreport.

## 10. The benchmark, and the audit that checks it (35 seconds, clock 3:50)

**Say**

The benchmark is generated from the corpus with the same three stems for both halves, so a difference between them is a difference in the evidence, not the phrasing. The unanswerable class is corpus-anchored: every question has a structural twin in the answerable class. And it is audited. A classifier seeing only the question text reaches an ROC AUC of 0.564 on the focus corpus and 0.533 on the six-category one. That is what a class with no shortcut should look like.

**On the slide.**

- The audit table on the right, and the two ROC AUC rows.
- The two rows that carry the certificates and the shortcut detection.
- The takeaway band, which says what the audit is for.

**Why this slide matters.** The audit is the hard half of the work, and the question-only classifier is the number that answers the obvious objection. The slide says what the audit is for, so the reader knows it is not there to make the numbers look good.

**If you are asked "what was the shortcut?"** The defective class put a fabricated identifier in the hard case, and an identifier filter found every one of them. It is described in the report, and the shortcut audit ships with the benchmark.

## 11. The metrics and the protocol (16 seconds, clock 4:06)

**Say**

Three retrieval measures, two generation rates, and one paired test. Every comparison is paired, because the arms answer the same questions, and every test is per class, because a gate can improve one class and damage the other.

**On the slide.**

- The three formulas on the left.
- The symbol table on the right, which names every symbol, so the formulas do not have to be read.
- The protocol note, which carries the two rules the whole results section rests on.

**Why this slide matters.** Two rules carry the whole results section, and they are stated as rules rather than defended, because they are properties of the design. Every comparison is paired because the arms answer the same questions, and every test is per class because a gate can improve one class and damage the other at the same time.

## 12. Retrieval: seven configurations over the same 32 queries (31 seconds, clock 4:37)

**Say**

Seven configurations over the same 32 queries. The dense leg is significantly worse than the lexical leg: Recall@10 falls from 0.969 to 0.812, a paired difference of 0.156 in favour of BM25, with Cohen's d of 0.42, at p = 0.025. That is why the encoder was replaced. Fusion recovers the loss, reaching 1.000, but the claim is narrow: it stopped being a loss and did not become a win over BM25.

**On the slide.**

- Rows A, B and C: BM25 alone, the dense leg alone, and the fusion.
- The prose on the right, which carries the effect sizes beside the p values.
- The takeaway band, which is the reranker's result with its corpus attached.

**Why this slide matters.** The number first and the meaning after it, and the effect size beside the p value, because a paired difference of 0.156 on 32 queries needs both. The claim is deliberately narrow: fusion stopped being a loss and did not become a win over BM25.

**Do not say** that fusion beat BM25. It did not, significantly. Say "it stopped being a loss."

## 13. The quota has no universally better placement (20 seconds, clock 4:57)

**Say**

The quota has no universally better placement. The direction reverses between corpora: before the reranker is better on the focus corpus, after it is better on the industrial one. None of the three differences is significant. The placement is a configuration value rather than a rule.

**On the slide.**

- The three p values in the last column, which are all larger than 0.15.
- The two recall columns, where the direction reverses between corpora.
- The figure, which shows the two corpora together.

**Why this slide matters.** It is a null, and it is reported as one, with the direction reversal visible in the two recall columns. The slide is here because a configuration value with a corpus attached is more useful to the next person than a rule that does not hold.

## 14. More candidates are not monotonically better (24 seconds, clock 5:21)

**Say**

More candidates are not monotonically better. On the focus corpus the curve peaks at a pool of ten and falls back to 0.969 at twenty, fifty and a hundred. The gold chunk is still being found, and then the reranker pushes it out of the ten-chunk context: a larger pool costs ordering without adding the answer.

**On the slide.**

- The figure, with the two corpora's curves on it.
- The note beneath the prose, which is the industrial exception and says why it is the exception.
- The prose on the right, which gives the numbers behind the curve.

**Why this slide matters.** The focus curve and the industrial curve fail in different directions, so the note says which is which. On the focus corpus the gold chunk is found and then pushed out by the reranker; on the industrial corpus it is still arriving at a pool of fifty.

## 15. The operating point, and the frontier behind it (22 seconds, clock 5:43)

**Say**

The operating point is not chosen by hand. The threshold is the highest one that still answers 90 percent of the answerable questions. The whole frontier is shown because a single threshold hides the shape behind it. At the fitted point the coverage is 0.693 and the abstention precision is 0.963.

**On the slide.**

- The tau column, and the two columns beside it: what the gate answers and what it refuses.
- The figure on the right, which is the whole frontier rather than one point on it.
- The takeaway band, which carries the coverage and the abstention precision.

**Why this slide matters.** The threshold comes from a rule stated in advance, and the whole curve is shown because a single threshold hides the shape behind it. A reader who wants a different operating point can read it off the first column.

## 16. The gate on the unanswerable class (26 seconds, clock 6:09)

**Say**

What the gate does with the unanswerable class. It refuses 23.6 percent of the hard stratum, and 26 of the 34 out-of-domain questions. The question-only classifier reaches an ROC AUC of 0.608, so a little shape is left. The finding is the gap: the gate detects a recognisable unanswerable question, and is much weaker when the topic is on-topic but unanswered.

**On the slide.**

- The table on the right, and the two strata: the hard stratum and the out-of-domain stratum.
- The ROC curve on the left, where the dashed line is chance.
- The note beneath, which is the finding: the gap between the two strata.

**Why this slide matters.** The gap between the two strata is the finding, and the ROC AUC of 0.608 is given so the panel can see how much shape is left. The gate detects a recognisable unanswerable question and is much weaker when the topic is on-topic but unanswered.

## 17. The framework's own hypothesis, under two conditions (31 seconds, clock 6:40)

**Say**

This is the framework's own hypothesis, under two conditions. Under a prompt that requires an answer, the gate reduces the rate of answering unanswerable questions from 0.938 to 0.528, at p below 0.001. Under a prompt that permits a decline, it reduces the rate from 0.535 to 0.417, at p = 0.002. The verdict is supported under both. Notice the transferred arm: 6 of 32 answerable answered, against 32 of 32 ungated.

**On the slide.**

- The fitted row and the no-gate row. Read those two and let the table carry the rest.
- The transferred row, which is the one to notice and the one to prepare for.
- The bullets under the table, which carry the two conditions.

**Why this slide matters.** Both prompt conditions are on one table, because the point is that the verdict does not depend on which prompt is used. The transferred row is called out because it is the one that over-refuses badly, and it is the row a panel is most likely to pull on.

**Do not read the table row by row.** Read the fitted row and the no-gate row, and let the table carry the rest.

## 18. What the confidence score actually buys (34 seconds, clock 7:14)

**Say**

And this is the finding most likely to be reported wrongly, so it gets a slide of its own. The score does not buy a lower answer rate on unanswerable questions. The random control reaches 0.604, worse than the fitted gate's 0.528, and far below the ungated arm's 0.938. What the score buys is where the refusals land: the gate refuses 2 answerable questions, the random control 11. The gate removes 59 wrong answers and costs 1 correct one.

**On the slide.**

- The three numbers across the top: the two refusals and the abstention precision.
- The note on the right, which carries the paired tests and the trade.
- The band at the bottom, which is the sentence to avoid.

**Why this slide matters.** This is the finding most likely to be misreported, so the slide states the misleading sentence and then destroys it with the control. The score does not lower the answer rate; it places the refusals, and the two refusals against eleven is the whole claim.

**Do not say** "the gate answers fewer unanswerable questions." It is true and it is misleading, because the random control answers fewer still. That sentence is on the slide as the sentence to avoid.

## 19. Long context against the pipeline (31 seconds, clock 7:45)

**Say**

Long context against the pipeline. The focus corpus is 202,529 tokens against an accepted context of 2,246: 74 times the tokens, but 58.8 times the cost, because a third of the requests are cache reads. The generator answered 32 of 32 answerable questions, at a per-answer accuracy of 0.406 against 0.667 for the gated pipeline. A token ratio is the size of the prompt; a cost ratio is what the prompt costs.

**On the slide.**

- The two ratios at the top, and the cache-read share that explains why they differ.
- The retrieval-side proxy table, which is what the pipeline does instead.
- The takeaway band, which is the sentence that stops an argument about money being made from a prompt size.

**Why this slide matters.** The two ratios are the point, and the sentence about the token ratio is the one that stops an argument about money being made from a prompt-size number. Most of the long-context arm's tokens are cache reads, so the cost ratio is much smaller than the token ratio.

**If you are asked "does long context win?"** No superiority claim is made. It matched the ungated coverage, lost on per-answer accuracy, and cost more. The tail is where corpus size bites.

## 20. The contradiction gate: a precision of zero (21 seconds, clock 8:06)

**Say**

The contradiction gate. Twenty labelled alarms, none confirmed. The precision against reader labels is zero, with a 95 percent upper bound of 16.1 percent. This is reported as unconfirmed with a stated bound: the mechanism is unproven rather than disproven, because this corpus does not hold the phenomenon it detects.

**On the slide.**

- The rows that carry the zero and the upper bound.
- The figure on the right, with its Wilson intervals.
- The takeaway band, which says unconfirmed rather than disproven, and says why.

**Why this slide matters.** Reported as unconfirmed with a bound rather than as a defect, and the reason is on the slide: this corpus does not hold the phenomenon the detector detects. The annotators agreed on all 101 decisions, so the labelling is not what is wrong.

## 21. The findings, all fourteen (19 seconds, clock 8:25)

**Say**

All fourteen findings, every one of them a measured result. The ones that contradict the framework sit in the same list as the ones that support it. That is deliberate: move the negatives elsewhere and this table would read as a list of successes.

**On the slide.**

- The table. Do not read the fourteen rows.
- F10, the contradiction gate's null, which sits in the middle of the list.
- F8 and F12, which are the two findings a panel is most likely to pull on.

**Why this slide matters.** Every finding is measured, and the negative ones are in the same list, and the slide says so, because a table with the negatives removed reads as a list of successes. This is the slide to leave up during the questions.

**Do not read the fourteen rows.** Say that they are all there, say that the negative ones are in the same list, and move on.

## 22. What the measurements support, and what they do not (24 seconds, clock 8:49)

**Say**

Three things the measurements support. The gate works, but not in the way it is usually described: it works by placing its refusals, not by answering fewer questions than a control. Its cost is coverage, not quality. And the benchmark was the harder half: repairing the shortcut moved the headline from 91.7 to 23.6 percent.

**On the slide.**

- The left card, the three things the measurements support.
- The right card, the three negative results.
- The takeaway band, which says why they are reported.

**Why this slide matters.** Three supported claims and three negative results are given the same weight on one slide, and the negative ones are named as results rather than as caveats. The gate's cost is coverage, not quality, and the benchmark was the harder half of the problem.

## 23. The limitations (18 seconds, clock 9:07)

**Say**

Eight limitations. The first is the largest gap: one generator, because the replication on a second model could not be run. Then the corpus, the long-context half, the model-based annotation, statistical power, and the fact that a refusal is not an answer.

**On the slide.**

- The first two rows of the table. The first is the largest gap in the work.
- The third column, which says what each limitation restricts.
- Do not read all eight.

**Why this slide matters.** The first row is the largest gap in the work and it is said first rather than last, because a limitation the panel finds is worth more than one volunteered late. The replication could not be run, so the hypothesis is supported for the generator tested and not in general.

**Do not read all eight.** Say the first one and point at the table.

## 24. The conclusion, and the future work (23 seconds, clock 9:30)

**Say**

The hypothesis is supported under both prompt conditions. Three findings qualify it: the score buys refusal precision, the benchmark's own shortcut was worth more than the system, and one mechanism did not survive measurement. The contribution is a cost-coverage-reliability frontier for a gate on industrial text, at the level of the answer claim.

**On the slide.**

- The three paragraphs on the left: the verdict, the three qualifying findings, and the contribution.
- The future work table on the right, which is in the order the steps would change what can be claimed.
- The closing point, which is the sentence to land.

**Why this slide matters.** The conclusion names the three qualifying findings rather than only the verdict, and the nine steps are ordered by what they would change. The closing point is the sentence to land, and it is the honest one: the most useful thing here was the instruments that turned out not to be trusted.

## 25. The references (7 seconds, clock 9:37)

**Say**

These are the eight works the work stands on. Every mechanism here is already in the literature.

**On the slide.**

- The eight entries. Do not read them aloud.
- Leave the slide up long enough to be photographed.

**Why this slide matters.** Not read aloud. The point of the slide is that every mechanism is already in the literature, and the slide is left up long enough to be photographed when a panel asks where the gate comes from.

## 26. Thank you (10 seconds, clock 9:47)

**Say**

That is the work. Every figure comes from an archived result file, and the report holds the full text and the benchmark. Thank you.

**On the slide.**

- Nothing. Leave it up for the questions.

**Why this slide matters.** It is left up for the questions, and the line under the rule says where the full text is. The last thing said aloud is that every figure came from an archived result file, which is true.

# If you are running long

Cut in this order. Each cut is a slide the argument survives without, and the
numbers on it are all on other slides.

1. **Slide 8**, the retrieval formulas. Say one sentence: the stack is BM25
   plus dense, fused by RRF, reranked, with a quota. Saves 23 seconds.
2. **Slide 11**, the metrics. Say one sentence: paired tests, per class.
   Saves 16 seconds.
3. **Slide 13**, the quota placement. It is a null, and it is in the findings
   table as F3. Saves 20 seconds.
4. **Slide 4**, the literature table. Say the two sentences on slide 4 and
   move straight to slide 5. Saves 18 seconds.
5. **Slide 20**, the contradiction gate. It is in the findings table as F10
   and in the negative results on slide 22. Saves 21 seconds.
6. **Slide 23**, the limitations, if the chair is being impatient. Say the
   first limitation only: one generator. Saves 18 seconds.

Cutting all six brings the talk to about eight minutes, which is the right
place to be if the chair has said anything about time.

# If you are running short

Do not add material. Re-run slides 12, 17 and 18 and let the numbers land
twice: say the finding, then read the two or three numbers that carry it.
Those three slides are the result, and a panel that has heard them once will
remember them better if they have heard them twice.
