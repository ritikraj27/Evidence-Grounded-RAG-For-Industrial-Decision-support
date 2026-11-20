# Part D. The technicalities

The things that are true of every experiment at once, rather than of one
slide. This is the part to read on the morning of the presentation if a
question goes somewhere the deck does not reach.

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
the deck is measured here: the ECE of 0.1044, the Brier score of 0.1510,
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
version of the gate failed (Part B.2 of the ten-minute companion), and it is
also why the Brier score of 0.1510 has to be read against the trivial
model's 0.182.

## D.3 The benchmark, and its repairs

The benchmark was audited before it was used, and the audit found defects.
Two of them changed the headline. The account is here in full, because "the
framework was measured on a benchmark that had to be repaired" is a claim
that needs its evidence.

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

After the repair, the shape-separability classifier scores 0.608 on the focus
corpus against a permutation null of 0.455 plus or minus 0.072, the
question-only policy scores 0.564 where 0.5 is no discrimination, and the
one-rule shortcut carries 0.0 percent. The benchmark as it stood before the
repair is kept beside the repaired one, so every before-and-after claim can
be regenerated rather than asserted.

**Repair 3: the form check.** The runtime validator refused 3 of
{{CASE_N_QUERIES}} benchmark queries. All three were generator artefacts
that read as malformed rather than real questions. This is the one repair
that goes the other way: the validator was too eager on this benchmark, and
the benchmark was right.

**The audit instrument was kept rather than deleted**, because it is the
instrument that found the defects. It is one of the nine next steps to be
published separately, so that other work on RAG refusal can check its own
benchmarks against the same instrument.

**Two classifiers, two rows.** The shape-separability classifier reads the
question's shape. The question-only policy is a rule-based detector. They are
different classifiers, so the before-and-after table has a row for each, and
the figure plots the separability one. A single row that paired one
classifier's before-value with the other's after-value would describe two
classifiers at once.

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
It answers {{GEN_A_LONGCTX_ANS_ANSWERED}} answerable questions, the same as
the ungated pipeline, and it costs 74 times the tokens and 58.8 times the
money. The report does not claim the retrieval machinery is cheaper in
absolute terms; it claims the cost ratio, and it claims the cost because the
corpus does not fit in a context window for one of the two corpora.

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
happen is indistinguishable from a rate that did.

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
precision is zero by construction. That is what slides 28 and 29 establish,
and it is why the finding is a statement about the corpus as much as about
the detector.

## D.7 The objectives, and where each one is answered

The deck's slide 4 states four objectives. Each has a slide that answers it,
and it is worth knowing which.

| Objective | Answered on |
|---|---|
| RO1, build an evidence-grounded framework | Slides 6, 7, 8, 9, and the whole deck |
| RO2, modality-balanced and category-aware retrieval | Slides 7, 15, 18, 19 |
| RO3, test the framework's own hypothesis | Slides 22, 23, 24, 25 |
| RO4, characterise the failure modes | Slides 11, 12, 13, 28, 29, 30, 32, 34, 35 |

**RO4 is the objective that distinguishes this project.** A framework report
that only reported what worked would be a smaller claim. What is here is a
failure-mode characterisation with the error rates of the measuring
instruments published alongside it: the benchmark's own defect (slides 11 to
13), the contradiction detector's null (28 and 29), the second generator's
empty completions (30), and the attribution gap that turns out to be a
retrieval problem rather than a scoring one (32).

## D.8 The prior art, and what is new

Every mechanism in the framework is published. The deck names five of them
with their citations: hybrid retrieval and reciprocal-rank fusion
(Karpukhin et al. 2020; Cormack et al. 2009), selective prediction through a
calibrated gate (Yadkori et al. 2024), and the rest of the components that
the report's literature review covers.

**The closest prior art is HALT-RAG (Goswami and Kurra 2025),** and the
distinction is worth having ready. HALT-RAG is a post-hoc output verifier:
it reads what the generator produced and checks it afterwards. It never runs
a generator, and it never decides not to call one. The step this report
performs is deciding whether to generate at all, in code, before the model is
invoked. HALT-RAG's own future work names that step.

**So what is new.** The assembly into one industrial system; the evaluation
at the level of the individual answer claim rather than the answer; and the
audit and repair of the benchmark the measurement rests on. A committee that
wants to know which component is new will find that none of them is, and a
candidate who says so before being asked is making a stronger claim than one
who claims otherwise.

## D.9 What is claimed, and what is not

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

## D.10 Reproducibility and provenance

**Every number is a measurement against an archived result file.** The
figures are regenerated from the result files, and the build fails if a
figure is older than the results it draws. The caption of a figure and the
number it carries are checked against each other, because a caption that
disagrees with its own figure is worse than no caption.

**The corpus ships with its provenance.** For every document the manifest
gives the source URL, the upstream revision it was read at, the SHA-256 of
the exact bytes used, and its chunk count. The licence for the article text
is stated. The primary corpus of proprietary supply chain documents cannot be
redistributed, so it cannot be shipped or re-run by a reader, and the report
says so wherever the substitute matters.

**The audit instruments are kept.** The benchmark as it stood before the
repair sits beside the repaired one. The earlier encoder's numbers are kept
as tokens, so both sides of the comparison that changed the architecture rest
on measured values rather than recollection.

**What this buys the reader.** Any claim in the deck can be checked against
an archived result rather than taken on trust. That is the standard the
project holds itself to, and the reason three of the deck's findings are
about the project's own instruments rather than about the framework.

---

## D.11 One page of numbers to have in mind

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
| The gate's calibration | ECE 0.1044, Brier 0.1510, base rate 0.182 |
| The threshold's cost | coverage 0.693 at tau of 0.05, 0.432 at tau of 0.10 |
