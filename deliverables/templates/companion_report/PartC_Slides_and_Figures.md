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
focus corpus carries {{SCOPE_SCM_CHUNKS}} chunks from {{SCOPE_SCM_DOCS}}
documents and is where the ablation, the gate and the generation experiments
run. The six-category industrial corpus carries {{MC_LC_CORPUS_CHUNKS}} chunks
from {{N_DOCUMENTS}} documents and is where transfer and the long-context
cost are measured. The federal regulatory corpus carries {{SCOPE_RE_CHUNKS}}
chunks from {{SCOPE_RE_DOCS}} documents and exists because it is the corpus
where the contradiction detector's phenomenon could be looked for.

**The question split.** The focus corpus carries {{CASE_N_ANSWERABLE}}
answerable and {{CASE_N_UNANSWERABLE}} unanswerable questions. The
cross-category corpus carries {{MC_N_ANSWERABLE}} and
{{MC_N_UNANSWERABLE}}. The two never mix.

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

**The panel.** The gate refuses {{UNANS_OOD_REFUSED_N}} of the out-of-domain
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
| `rag_nogate` | {{GEN_A_NOGATE_UNANS_ANSWERED}} ({{GEN_A_NOGATE_UNANS_ANSWER_RATE}}) | {{GEN_A_NOGATE_ANS_ANSWERED}} | none |
| `rag@fitted` | {{GEN_A_FITTED_UNANS_ANSWERED}} ({{GEN_A_FITTED_UNANS_ANSWER_RATE}}) | {{GEN_A_FITTED_ANS_ANSWERED}} | b = 60, c = 1, p < 0.001 |
| `rag@random` | {{GEN_A_RANDOM_UNANS_ANSWERED}} ({{GEN_A_RANDOM_UNANS_ANSWER_RATE}}) | {{GEN_A_RANDOM_ANS_ANSWERED}} | none |
| `rag@transferred` | {{GEN_A_XFER_UNANS_ANSWERED}} ({{GEN_A_XFER_UNANS_ANSWER_RATE}}) | {{GEN_A_XFER_ANS_ANSWERED}} | none |
| `long_context` | {{GEN_A_LONGCTX_UNANS_ANSWERED}} ({{GEN_A_LONGCTX_UNANS_ANSWER_RATE}}) | {{GEN_A_LONGCTX_ANS_ANSWERED}} | p = 1.00 |

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
{{GEN_A_LONGCTX_ANS_ANSWERED}} answerable questions, the same as the ungated
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
The cross-category corpus does not fit a 128K window: {{MC_LC_CORPUS_TOKENS}}
tokens, {{MC_LC_CORPUS_VS_128K}} times the limit, so the quality half of that
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
{{GEN_A_XFER_ANS_ANSWERED}} answerable questions. The threshold was fitted on
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
{{CASE_N_QUERIES}} queries. The gate's behaviour on unanswerable questions
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
rate from 0.938 to 0.528, at a cost of {{GEN_A_FITTED_ANS_ANSWERED}}
answerable questions answered where the ungated arm answers
{{GEN_A_NOGATE_ANS_ANSWERED}}.

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
