# Part A. The argument the talk makes

## A.1 The one sentence the talk answers

The talk is built around a question, stated on slide 2 and answered on slide
16.

> When a generator is given industrial text, can a gate in the code decide
> whether the retrieved evidence actually contains the answer, and what is
> that gate worth once it has been measured properly?

There are two halves to it, and the second is the harder one. The first half
is a design question, and the deck answers it in the first three minutes: yes,
a gate can be built, and it sits in the path where it cannot be bypassed. The
second half is what the rest of the talk is about, and the word doing the work
in it is "properly". A framework is not worth what a benchmark says about it
if the benchmark can be read without the framework.

## A.2 The seven movements

| Movement | Slides | What it has to establish | The sentence that does it |
|---|---|---|---|
| The problem | 1, 2 | that a wrong answer costs more than a non-answer, so a gate is worth building | "here a refusal costs a supervisor five minutes, and a confidently fabricated tolerance costs a scrapped batch" |
| The framework | 3 to 6 | that the gate is in the path and cannot be bypassed | "the generator is injected into the framework and called at exactly one line, after the gate has accepted" |
| The method | 7, 8 | what was measured, on what, and with which tests | "every comparison is paired, because the arms answer the same questions" |
| The measurements | 9 to 13 | what the retrieval and the gate actually do | "the gate is precise where it refuses" |
| The three findings that qualify the verdict | 14 to 20 | what the verdict rests on, and where it stops | "the most useful thing this produced was not the framework" |
| The limitations | 21, 22 | what was measured and what was not | "L1: one generator" |
| The next steps | 23, 24 | what would change what the work can claim | "a framework's contribution is only as good as the instruments that measured it" |

The order is not arbitrary and it is not the order of the report. The
problem comes first because the committee decides whether the question matters
before it decides whether the answer is right. The framework comes next
because it is the design question, and it is quick. The method comes third
because it is what makes the later numbers legible. The measurements come
fourth, and they are the longest movement because there are six figures and
fifteen tables in them.

## A.3 Where the argument turns

The argument turns on slide 14, and it is the most important slide in the talk.

Everything before it is provisional. The benchmark's unanswerable half could
be separated from the question text alone: a classifier that saw only the
question, with no retrieval, no evidence and no corpus, told answerable from
unanswerable at ROC AUC {{UNANS_BEFORE_AUC}} against a permutation null of
{{UNANS_BEFORE_NULL}}. So the headline refusal rate of
{{UNANS_BEFORE_REFUSED_PCT}} was measuring the benchmark rather than the
framework.

After slide 14 the numbers are on a benchmark that can be trusted, and they
are much smaller: {{UNANS_HARD_REFUSED_PCT}} on the hard stratum, where the
corpus discusses the subject but does not state the answer, against
{{UNANS_OOD_REFUSED_PCT}} on the out-of-domain stratum, where the question
comes from outside the corpus entirely.

That is why slide 14 takes 35 seconds, the second longest in the talk. A talk
that reports the repaired rate without the artefact it replaced invites the
question "how do you know the benchmark was not rigged in the other
direction", and the only answer to that question is the artefact itself.

## A.4 The slide the talk is built around

Slide 16. It is the only slide where a gate's refusal is measured against a
generator that cannot refuse on its own.

Under the cautious prompt the generator declines most unanswerable questions
by itself, the gate's refusals are largely redundant, and the arms could not
have been told apart. That setup would have produced a null result that meant
nothing. The two prompt conditions exist so that slide 16 is possible, and
that reason is given on slide 15, before the reader reaches the verdict.

## A.5 The four things the talk does not claim

| The claim the talk refuses | The sentence that would overstate it | Where the boundary is |
|---|---|---|
| That the framework beats plain BM25 on recall | "the pipeline retrieves better than BM25" | the dense leg is significantly worse than BM25 on the focus corpus, and fusion only stops that being a loss. The retrieval claim carries its corpus. |
| That the gate lowers the answer rate on unanswerable questions | "confidence gating reduces hallucination" | the claim is about where the refusals land, not how many there are. The random control answers the unanswerable class at {{GEN_A_RANDOM_UNANS_ANSWER_RATE}} against the gate's {{GEN_A_FITTED_UNANS_ANSWER_RATE}}, and still spends eleven refusals on answerable questions against the gate's two. |
| That the contradiction mechanism works | "the gate detects contradictions" | its precision against reader labels is {{CONTRA_PRECISION_PCT}} on {{CONTRA_PRECISION_N}} alarms, and the corpus does not contain the phenomenon it detects. |
| That a fitted threshold transfers | "the gate is calibrated" | a calibrated threshold fitted on one half of a corpus over-refuses on the other half. The transferred arm answers {{GEN_A_XFER_ANS_ANSWERED}} of the answerable questions against the fitted gate's {{GEN_A_FITTED_ANS_ANSWERED}}. |

Each of these is a sentence a reader could write down and quote back. They are
the four ways this work can be misreported, and the script is worded to make
each of them hard to misreport.

## A.6 Why the argument ends on the instruments

The closing note on slide 23 is the conclusion of the argument, not an
afterthought. The most useful thing this work produced was not the framework.
It was finding that two of its own instruments were reporting numbers a
careful reader could not trust, and changing the headline rather than
explaining it away. A framework's contribution is only as good as the
instruments that measured it.

The next-steps list is ordered the same way. Repeating the comparison on a
generator that returns text is first, because it would change what the work
can claim. Publishing the corrected benchmark and the shortcut audit is last,
because that part outlives the report.
