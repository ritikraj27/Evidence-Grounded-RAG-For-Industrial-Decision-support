# Part C. The script, slide by slide

What each slide argues, why the script is worded the way it is, the claim it
makes, the claim it refuses to make, and the trap on it. The wording of the
script is the authoritative part; this part explains it.

## C.1 Title (20 seconds, clock 0:20)

**What it argues.** Nothing yet. It is the handshake and the promise: one
question and its answer, and the numbers behind both.

**Why it is worded this way.** It names the four things the talk will cover,
so the room knows the shape of the next ten minutes.

**The claim it makes.** None.

**The claim it refuses to make.** None. The instruction is not to read the
title aloud word for word.

**The trap.** Spending the first twenty seconds on yourself. Say your name
clearly and move on.

## C.2 A wrong answer costs more than no answer (30 seconds, clock 0:50)

**What it argues.** The asymmetry between a wrong answer and a non-answer is
the reason a gate is worth building.

**Why it is worded this way.** It starts from the industry rather than from
the method, because a refusal that costs a supervisor five minutes and a
fabricated tolerance that costs a scrapped batch is a cost the room already
understands.

**The claim it makes.** The research question, in the words the rest of the
talk answers.

**The claim it refuses to make.** That this is a gap in the literature. The
gap is not what earns the ten minutes; the measurement is.

**The trap.** Point at the panel on the right when you ask the question. That
sentence is what the rest of the talk is for, and if the room has not heard it
clearly, slides 3 to 20 lose their subject.

## C.3 The framework: five stages (36 seconds, clock 1:26)

**What it argues.** The gate is in the path and cannot be bypassed.

**Why it is worded this way.** Two properties of the arrangement are asserted
rather than explained, because they are properties of the code and can be
pointed at: the generator is called at exactly one line, after the gate has
accepted, so a refused query costs no model call at all; and the form
validator is a separate component from the gate, because they answer
different questions.

**The claim it makes.** Non-bypassability. The only two paths that skip the
gate are the comparison arms, and both are reported as separate results.

**The claim it refuses to make.** That the gate is a component somebody can
switch off. It is in the path.

**The trap.** The two purple boxes on the pipeline are the stages that can
refuse. Say "two stages can refuse" and point at them, because the room will
otherwise read the boxes as five equal steps.

## C.4 Retrieval: two legs, one fusion, one quota (28 seconds, clock 1:54)

**What it argues.** Three invariants are asserted rather than assumed, and one
of them changed the design.

**Why it is worded this way.** The three formulas are named, not derived.
BM25 is standard Okapi, reciprocal rank fusion needs only ranks and no score
calibration between the two legs, and the quota is a floor on the share of
non-text chunks rather than a ceiling on text.

**The claim it makes.** Fusion stopped the dense leg being a loss. The first
dense encoder was measurably worse than plain BM25 on this corpus, so it was
replaced, and that is why the encoder is what it is.

**The claim it refuses to make.** That fusion beats BM25. It does not; it
recovers the loss.

**The trap.** Three formulas and a panel in twenty-eight seconds. Name them
and move on. The panel on the right is the one to point at if somebody asks
about the invariants.

## C.5 The confidence gate (28 seconds, clock 2:22)

**What it argues.** The gate is a calibrated posterior over the whole
retrieved pool, at the query level.

**Why it is worded this way.** The query level is explained with the
"98 percent by answering nothing is relevant" figure, because that is what a
reader thinks of first. With one gold chunk among about fifty candidates, a
chunk-level classifier is right almost all of the time by refusing, and the
fit duly returns a large negative intercept. That looks like a fitted model
and behaves like a constant.

**The claim it makes.** A calibrated posterior with a threshold at
{{FOCUS_GATE_TAU}} on the focus domain.

**The claim it refuses to make.** That the positive class is sufficiency. The
literature reserves that word for a set-level property, and this class is
answer-in-context detectability, defined operationally as the gold chunk
being present in the reranked candidate pool. Calling it sufficiency would
claim prior work that is not here.

**The trap.** This is the answer to "why is the gate not just a similarity
threshold", and the panel on the slide is that answer. It is worth knowing
before the question arrives.

## C.6 The contradiction gate, and the form validator (23 seconds, clock 2:45)

**What it argues.** Two components refuse, for different reasons.

**Why it is worded this way.** The conjunction is explained through its two
defects, because a claim about a detector needs to say what it detects. A
quantity branch on its own fired on citation years, and a topical subject
check on its own was a topic check rather than a contradiction check.
Requiring both cut the alarms from {{CONTRA_ALARMS_BEFORE}} to
{{CONTRA_ALARMS_AFTER}}.

**The claim it makes.** The form validator refused
{{FORMVAL_FIX_MAL_REJECTED}} of {{FORMVAL_FIX_MAL_N}} hand-authored malformed
queries and {{FORMVAL_FIX_VAL_REJECTED}} of {{FORMVAL_FIX_VAL_N}} well-formed
ones, at {{FORMVAL_COST_US}} microseconds per query.

**The claim it refuses to make.** That the gate did the validator's work. The
gate accepted 76.7 percent of the malformed stems pushed through it, so it is
an evidence gate and not a form gate.

**The trap.** The memorable part is the counterfactual: reusing the benchmark
builder's question-generation rule as a runtime check would have refused
{{FORMVAL_COUNTERFACTUAL_RATE}} of the hand-labelled well-formed questions. A
filter written for one purpose does not fit another, and its false rejection
rate has to be measured before it ships.

## C.7 Three corpora, and a benchmark that had to be repaired (25 seconds, clock 3:10)

**What it argues.** The roles of the three corpora do not overlap, and the
benchmark needed three repairs.

**Why it is worded this way.** The audit instrument is kept and named, because
it is the instrument that found the defects. A reader who suspects the
benchmark was written to flatter the system is answered by the fact that the
tool that caught it is still there.

**The claim it makes.** The focus corpus carries {{SCOPE_SCM_CHUNKS}} chunks
from {{SCOPE_SCM_DOCS}} documents and is where the ablation, the gate and the
generation experiments run.

**The claim it refuses to make.** That the retrieval-side numbers were
affected by the mislabelled answers. The gold chunk was always right, so only
the answer-side accuracy was depressed, and equally for every arm.

**The trap.** Be honest about the substitute corpus before anybody asks. The
primary corpus of proprietary supply-chain documents cannot be redistributed,
so every measurement runs on a public substitute that ships with its
provenance: each document carries the upstream identifier, a SHA-256, the
chunk count and the licence.

## C.8 Metrics, tests, and the rule that every comparison is paired (20 seconds, clock 3:30)

**What it argues.** Every comparison is paired, and the test is applied per
class.

**Why it is worded this way.** Because one number for both classes would hide
the trade. A gate can improve the unanswerable class and damage the
answerable class, and a single figure over the two classes would hide exactly
that.

**The claim it makes.** Wilcoxon for retrieval, the exact McNemar test for
generation, effect sizes with the Wilcoxon, Wilson intervals for proportions.

**The claim it refuses to make.** A single verdict number across the two
classes.

**The trap.** The random arm is on this slide, not on the verdict slide, and
it belongs here. It removes the confidence score and keeps the refusal
budget, so refusals are drawn at random. Without it, refusing on a coin flip
and refusing on a calibrated score look identical on the easiest metric to
report.

## C.9 Retrieval: seven configurations on the focus corpus (28 seconds, clock 3:58)

**What it argues.** The dense leg loses, fusion recovers the loss, and the
reranker helps on the other corpus and does not help on this one.

**Why it is worded this way.** The claim for fusion is deliberately narrow.
It stopped being a loss; it did not become a significant win over plain BM25
on its own.

**The claim it makes.** Fusion reaches 1.000, a paired improvement of +0.188
at p of {{P_BC}}, and it improves the ordering too, MRR from {{MRR_B}} to
{{MRR_C}}.

**The claim it refuses to make.** That the reranker buys ordering. It does
that on the six-category corpus, where it moves MRR by 11.1 points at p of
0.00093, and it does not do it on the focus corpus, where it moves MRR by
{{RERANK_MRR_PP}} points and nDCG by {{RERANK_NDCG_PP}}, neither significant.

**The trap.** The sentence "the reranker buys ordering, not recall" is always
said with its corpus attached. Said bare, it is false on the corpus this talk
is about.

## C.10 The modality quota is a trade, not a gain (15 seconds, clock 4:13)

**What it argues.** The quota is a trade, and the placement is a configuration
value.

**Why it is worded this way.** Because none of the three differences is
statistically significant, and saying so is the only honest way to report a
configuration that was chosen.

**The claim it makes.** On the focus corpus the post-rerank quota gives up
{{QUOTA_POST_COST_PP}} points of overall recall while table recall stays at
1.000.

**The claim it refuses to make.** That the quota belongs before the
cross-encoder. That claim would not hold on every corpus.

**The trap.** The shipped placement is not the one the ablation ranks first on
the focus domain, and that is what limitation L20 in the report exists for.
The figure shows the arrows pointing left or down, never both ways up.

## C.11 More candidates are not monotonically better (15 seconds, clock 4:28)

**What it argues.** A larger pool costs ordering without adding the answer.

**Why it is worded this way.** The gap between the two curves is the whole
story, so the figure is read as a pair. Recall at twenty keeps rising as the
pool grows while Recall@10 falls away, because the gold chunk is still being
found and then the reranker pushes it out of the ten-chunk context.

**The claim it makes.** Recall@10 peaks at a pool of ten and falls back to
{{R_A}} at twenty, fifty and a hundred.

**The claim it refuses to make.** That more context is better.

**The trap.** The industrial corpus behaves differently. There the gold chunk
is still arriving at fifty, so Recall@20 reaches 1.000 at a pool of fifty
while Recall@10 stays at 0.988. The sentence always carries its corpus.

## C.12 The gate is calibrated, and it is not excellent (22 seconds, clock 4:50)

**What it argues.** The gate is calibrated on the held-out evaluation half,
and the calibration is not excellent.

**Why it is worded this way.** The number is reported rather than improved by
refitting, because it describes one fitted artefact on one fixed split. The
industrial gate tracks the diagonal at an ECE of {{IND_GATE_ECE}}; the focus
gate does not, and it puts most of its queries in the lowest confidence bin,
where few of them have an answer in context.

**The claim it makes.** Expected calibration error {{GATE_ECE}} and a Brier
score of {{GATE_BRIER}}.

**The claim it refuses to make.** That the gate is good. The slide's own
title says the opposite, and the lower panel of the figure shows why: it is
not badly spread, it is badly placed.

**The trap.** "Calibrated" is heard as "excellent" unless the room is told
otherwise. The base rate of answer-in-context is 0.182, so the gate is
trying to predict a rare positive.

## C.13 The operating point, and the frontier it sits on (28 seconds, clock 5:18)

**What it argues.** The threshold follows a stated rule, the gate is precise
where it refuses, and every extra refusal is paid for in coverage.

**Why it is worded this way.** The rule is stated before the number, so the
number can be recomputed by anyone in the room: the highest tau that still
answers at least 90 percent of the answerable queries, which gives
{{FOCUS_GATE_TAU}}.

**The claim it makes.** At the fitted operating point the abstention precision
is {{ABSTENTION_PRECISION}}, and the coverage is {{FOCUS_GATE_COVERAGE}}.

**The claim it refuses to make.** That the gate buys much over answering
everything. On the focus corpus it buys very little, which is visible on the
curve and is stated in the report.

**The trap.** The curve carries two degenerate policies: always answering, as
the horizontal line at the base rate of the negative class, and always
refusing, as the vertical line at zero risk and zero coverage. A reader who
sees the curve and hears only the precision will think the talk oversold it.
That is why the honest note is spoken on this slide.

## C.14 The benchmark answered itself (35 seconds, clock 5:53)

**What it argues.** The unanswerable half of the benchmark was separable from
the question text alone, so the headline refusal rate was an artefact of the
benchmark and not a measurement of the framework.

**Why it is worded this way.** This is the finding that took the most work and
it changes the headline, so it gets the second longest time in the talk and
the most detail. The class was rebuilt with corpus-anchored definitions and a
structural twin for every repaired question: same stem, same subject size,
matched subject-length distribution, no word in common.

**The claim it makes.** The shortcut existed and it was removed. Before the
repair the shape separability was {{UNANS_BEFORE_AUC}}; after it is
{{UNANS_SEP_AUC}}. The true refusal rate is {{UNANS_HARD_REFUSED_PCT}}.

**The claim it refuses to make.** The old rate of {{UNANS_BEFORE_REFUSED_PCT}}.

**The trap.** The table's first two rows are two different classifiers, both
of which see only the question. The shape separability row is the one the
figure plots, {{UNANS_BEFORE_AUC}} against {{UNANS_SEP_AUC}}. The question-only
policy row is a separate rule-based detector, {{UNANS_POLICY_BEFORE_AUC}}
against {{UNANS_POLICY_AUC}}. Reading them as one row's before and after
contradicts the figure on the same slide.

## C.15 One generator, five arms, two prompt conditions (28 seconds, clock 6:21)

**What it argues.** The design of the experiment, and why the replication on a
second generator could not be run.

**Why it is worded this way.** An empty completion is neither an answer nor a
refusal. That model returned no text on {{GENCOMP_FAILING_EMPTY}} of its
questions, {{GENCOMP_FAILING_EMPTY_TABLE}} of them on the benchmark's
table-lookup family, and raising the output budget fourfold rescued 13 and
left {{GENCOMP_FAILING_STILL_EMPTY}} still empty. A run like that is recorded
as not run, with the reason, because a rate quoted from a run that did not
happen is indistinguishable from a rate that did.

**The claim it makes.** One generator, five arms that each differ only in
what they remove, and two prompt conditions that differ by a single sentence.

**The claim it refuses to make.** Any replication claim. There is no second
generator in the results, and the slide says so.

**The trap.** The two tables are easy to swap. The arms table is at the top
left and it is the experiment. The table at the bottom is about the second
generator, and it explains an absence rather than a result.

## C.16 The verdict under the answering condition (38 seconds, clock 6:59)

**What it argues.** The gate is supported under both prompt conditions.

**Why it is worded this way.** The cost is spoken in the same breath as the
benefit, so the trade cannot be separated from the headline afterwards.

**The claim it makes.** Under the prompt that requires an answer, the ungated
arm answers {{GEN_A_NOGATE_UNANS_ANSWERED}} unanswerable questions and the
fitted gate answers {{GEN_A_FITTED_UNANS_ANSWERED}}, with the paired exact
McNemar test significant on the unanswerable class at b of 60 and c of 1. On
the answerable class the gate answers {{GEN_A_FITTED_ANS_ANSWERED}} where the
ungated arm answers {{GEN_A_NOGATE_ANS_ANSWERED}}.

**The claim it refuses to make.** A net accuracy gain. The gate spends two
refusals on answerable questions to remove 59 wrong answers, and that is a
trade, not a win.

**The trap.** The b and c values are per class. On the unanswerable class they
are 60 and 1; on the answerable class they are 2 and 0, and that second pair
is the whole story. It comes on the next slide.

## C.17 What the confidence score buys, and what it costs (38 seconds, clock 7:37)

**What it argues.** The score buys precision, not a lower answer rate.

**Why it is worded this way.** The control is stated before the claim,
because the control is what makes the claim possible. Refusing at random is
already a large improvement over never refusing, since most questions in a
benchmark are unanswerable: the control reaches
{{GEN_A_RANDOM_UNANS_ANSWER_RATE}} against the gate's
{{GEN_A_FITTED_UNANS_ANSWER_RATE}} and the ungated arm's
{{GEN_A_NOGATE_UNANS_ANSWER_RATE}}.

**The claim it makes.** Where the refusals land. The gate spends two refusals
on answerable questions; the random control spends eleven.

**The claim it refuses to make.** A quality gain from the accuracy columns.
The gated arm answers an easier subset, because a gate declines the hardest
questions. That is the selection effect, and per-answer accuracy cannot be
compared across arms with different coverage.

**The trap.** This is the slide the script says is most likely to be reported
wrongly. A report that said "the gate answers fewer unanswerable questions"
would be true and it would be misleading.

## C.18 Long context against the pipeline (22 seconds, clock 7:59)

**What it argues.** Long context was measured on cost and on coverage, and it
does not win.

**Why it is worded this way.** The token ratio is corrected against the cost
ratio in the same sentence, because a token ratio must never carry an
argument about money. Most of the long-context arm's tokens are cache reads
at a fifth of the base rate, so the money penalty is smaller than the token
penalty by more than the two numbers suggest.

**The claim it makes.** {{GEN_LC_TOKEN_RATIO}} times the tokens per query and
{{GEN_LC_COST_RATIO}} times the input cost, with the cache read share at
{{GEN_LC_CACHE_HIT}}. On coverage the whole-corpus prompt answered
{{GEN_A_LONGCTX_ANS_ANSWERED}} answerable questions, the same as the ungated
pipeline.

**The claim it refuses to make.** A superiority claim over long-context
prompting. The accuracy margin, {{GEN_A_LONGCTX_ANS_ACCURACY}} against
{{GEN_A_FITTED_ANS_ACCURACY}}, is not significant under a length-controlled
re-scoring of the same answers.

**The trap.** The cross-category corpus does not fit a 128K window, so the
quality half of that comparison could not be run there and it is settled on
coverage and cost alone. Say so rather than letting the room assume it was
measured.

## C.19 The contradiction gate: a precision of zero (28 seconds, clock 8:27)

**What it argues.** The mechanism is unproven rather than disproven, because
the corpus does not contain the phenomenon it detects.

**Why it is worded this way.** The annotators' agreement and their control
result are given, so the null is checkable rather than merely asserted. Both
readers were {{CONTRA_PRECISION_CONTROL}} on a control set with known labels,
and they agree with each other on {{CONTRA_PRECISION_PAIRS}} pairs.

**The claim it makes.** The precision against reader labels is
{{CONTRA_PRECISION_PCT}} on {{CONTRA_PRECISION_N}} labelled alarms, reported
as a null with a {{CONTRA_PRECISION_CI_HI}} upper bound.

**The claim it refuses to make.** That the detector is broken. The readers
also found no contradictions in a random sample of
{{CONTRA_UNFLAGGED_SAMPLE}} pairs the gate did not flag. A detector that finds
nothing in a corpus that has nothing to find is not a failing detector.

**The trap.** The markers on the figure mean something. A filled marker means
the point estimate clears the framework's 0.5 calibration floor and the branch
would act; a hollow marker means it does not, and the findings would be
withheld. The focus semantic branch is hollow, at a precision of 0.0 on a base
rate of 0.0.

## C.20 Most unattributed error comes from the evidence, not the scorer (20 seconds, clock 8:47)

**What it argues.** The gap between the evidence the arm was shown and the
gold chunk is a retrieval problem rather than a scoring problem.

**Why it is worded this way.** The same answers are scored against two
evidence sets, so the comparison is clean. The gold chunk is never
force-added to the evidence set, so nothing outside the evidence can support a
claim, and that is what makes the two columns comparable.

**The claim it makes.** The grounded claim error rate is
{{RO5_RETRIEVED_GROUNDED_ERROR}} over the retrieved evidence and
{{RO5_GOLD_GROUNDED_ERROR}} over the gold chunk.

**The claim it refuses to make.** A rule about the answer position effect.
The direction replicates in three of the four corpus-and-protocol
measurements and ties in the fourth, so it is stated with its magnitude rather
than as a rule.

**The trap.** This is the slide to compress if you are running behind, and the
slide most likely to be misquoted as a finding. The claim is about where the
error comes from, not about where in the passage the answer sits.

## C.21 What the measurements establish (20 seconds, clock 9:07)

**What it argues.** Fourteen findings, each with the number that carries it,
and three of them that qualify the verdict.

**Why it is worded this way.** This is the slide an examiner will photograph,
so it stays on screen while the three qualifying findings are said. The rest
are pointed at.

**The claim it makes.** F8, the confidence score buys refusal precision
rather than a lower answer rate. F10, the contradiction gate's precision
against reader labels is zero. F12, a calibrated threshold does not transfer
across corpora.

**The claim it refuses to make.** That the other eleven need reading aloud.

**The trap.** Those three are worth reading twice. Every row is a measurement
against an archived result file, so if a number is challenged it can be
regenerated.

## C.22 Limitations (28 seconds, clock 9:35)

**What it argues.** Eight limitations, two of them named first.

**Why it is worded this way.** L1 and L2 come first because they are the ones
that change what the work can claim: one generator, and an encyclopaedic
corpus rather than procedural documentation, in which the contradiction
detector's phenomenon is measurably absent.

**The claim it makes.** The boundaries of the work: one generator, an
encyclopaedic corpus, statistical power at this corpus size, model-based
rather than human annotation, the fact that a hallucination rate on generated
text is a different quantity from a refusal rate, the fact that a refusal is
not an answer, and English in one jurisdiction.

**The claim it refuses to make.** That the nulls are evidence of absence.
Several of them are nulls of this corpus at this size.

**The trap.** Do not rush this slide. The two limitations that matter most are
better raised here than waiting to be found in a question.

## C.23 What comes next, and a closing note (23 seconds, clock 9:58)

**What it argues.** Six next steps, in the order that would change what this
work can claim, and the closing note.

**Why it is worded this way.** The closing note is the point of the talk, not
an afterthought, so it is spoken last and it is about the instruments rather
than the architecture.

**The claim it makes.** That the contribution is the measurement: finding that
two of the framework's own instruments were reporting numbers a careful reader
could not trust, and changing the headline rather than explaining it away.

**The claim it refuses to make.** That the architecture is the contribution.

**The trap.** End on the instruments, not on the architecture. If the closing
point has been made, point at the six steps instead of reading them.

## C.24 Thank you (2 seconds, clock 10:00)

**What it argues.** Nothing.

**Why it is worded this way.** Two seconds. The talk ends on slide 23.

**The claim it makes.** None.

**The claim it refuses to make.** A second summary. The closing note was the
ending, and a summary after it takes the ending back.

**The trap.** "So, to summarise, the framework..." is the most common way a
good ending is spoiled.
