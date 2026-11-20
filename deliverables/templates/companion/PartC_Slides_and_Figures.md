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
focus corpus carries {{SCOPE_SCM_CHUNKS}} chunks from {{SCOPE_SCM_DOCS}}
documents and is where the ablation, the gate and the generation experiments
run. The six-category industrial corpus carries {{MC_LC_CORPUS_CHUNKS}} chunks
from {{N_DOCUMENTS}} documents and is where transfer and the long-context
cost are measured. The federal regulatory corpus carries {{SCOPE_RE_CHUNKS}}
chunks from {{SCOPE_RE_DOCS}} documents and exists because it is the corpus
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
{{CASE_N_QUERIES}} benchmark queries, all of them generator artefacts that
read as malformed rather than real questions. The audit instrument was kept
rather than deleted, because it is the instrument that found the defects.

**Be honest about the substitute.** The primary corpus of proprietary supply
chain documents cannot be redistributed, so it cannot be shipped or re-run by
a reader. Everything measured was measured on a public substitute. The
focus corpus carries {{CASE_N_ANSWERABLE}} answerable and
{{CASE_N_UNANSWERABLE}} unanswerable questions; the cross-category corpus
carries {{MC_N_ANSWERABLE}} and {{MC_N_UNANSWERABLE}}. The two never mix,
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
split of {{CASE_N_QUERIES}} queries, and its positive class has a base rate
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
refuses {{UNANS_HARD_REFUSED_N}} of the corpus-anchored hard stratum and
{{UNANS_OOD_REFUSED_N}} of the
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
| `rag_nogate` | {{GEN_A_NOGATE_UNANS_ANSWERED}} ({{GEN_A_NOGATE_UNANS_ANSWER_RATE}}) | {{GEN_A_NOGATE_ANS_ANSWERED}} |
| `rag@fitted` | {{GEN_A_FITTED_UNANS_ANSWERED}} ({{GEN_A_FITTED_UNANS_ANSWER_RATE}}) | {{GEN_A_FITTED_ANS_ANSWERED}} |
| `rag@random` | {{GEN_A_RANDOM_UNANS_ANSWERED}} ({{GEN_A_RANDOM_UNANS_ANSWER_RATE}}) | {{GEN_A_RANDOM_ANS_ANSWERED}} |
| `rag@transferred` | {{GEN_A_XFER_UNANS_ANSWERED}} ({{GEN_A_XFER_UNANS_ANSWER_RATE}}) | {{GEN_A_XFER_ANS_ANSWERED}} |
| `long_context` | {{GEN_A_LONGCTX_UNANS_ANSWERED}} ({{GEN_A_LONGCTX_UNANS_ANSWER_RATE}}) | {{GEN_A_LONGCTX_ANS_ANSWERED}} |

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
{{GEN_A_XFER_ANS_ANSWERED}} answerable
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
{{GEN_A_LONGCTX_ANS_ANSWERED}} answerable
questions, the same as the ungated pipeline.

**Quality.** Accuracy 0.406 against 0.667 for the gated arm, and the margin
is not significant under a length-controlled re-scoring of the same answers.

**The retrieval-side proxy.** With the candidate set widened to every chunk,
the gold chunk lands in the top 10 for 0.969 of the focus queries and 0.902
of the cross-category queries, at a median rank of 1. The evidence is not
lost in a large context; the tail is where corpus size bites, and a retriever
that finds the answer at median rank 1 has no use for the other
{{SCOPE_SCM_CHUNKS}} chunks.

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
