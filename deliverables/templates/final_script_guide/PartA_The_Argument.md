# Part A. The argument the talk makes

## A.1 The one sentence the talk answers

The talk is built around a question, and the question is on slide 2 and
answered on slide 17.

> When a generator is given industrial text, can a gate in the code decide
> whether the retrieved evidence actually contains the answer, and what is
> that gate worth once it has been measured properly?

There are two halves to it, and the second half is the harder one. The first
half is a design question, and the deck answers it in the first three minutes:
yes, a gate can be built, and it sits in the path where it cannot be
bypassed. The second half is what the rest of the talk is about. A framework
is not worth much on its own. A framework is worth something when somebody
has measured it, with a control, on a benchmark that was audited before it was
trusted.

## A.2 The seven movements

| Movement | Slides | What it has to establish | The sentence that does it |
|---|---|---|---|
| The problem | 2, 3 | that a wrong answer and a non-answer do not cost the same | "a refusal costs a supervisor five minutes, and a fabricated tolerance costs a scrapped batch" |
| The prior art | 4, 5 | what is already known, and what is not | "the abstention mechanism and the retrieval stack are prior art; the measurement is not" |
| The framework | 6, 7, 8 | that the gate is in the path and cannot be bypassed | "the gate is in code, so it cannot be bypassed" |
| The method | 9, 10, 11 | what was measured, on what, and with which tests | "every comparison is paired, and every test is applied per class" |
| The measurements | 12, 13, 14, 15, 16 | what the retrieval, the gate and the benchmark audit show | "the gate is precise where it refuses" |
| The findings that qualify the verdict | 17, 18, 19, 20, 21 | what the verdict rests on, and where it stops | "the score buys refusal precision, not a lower answer rate" |
| The reading and the limits | 22, 23, 24, 25, 26 | what is established, what is not, and what would change it | "a negative result stated plainly is worth more to the next person than a positive one that was overstated" |

The order is not arbitrary and it is not the order of the report. The problem
comes first because the committee decides whether the question matters before
it decides whether the answer is right. The framework comes next because it
is the design question, and it is quick. The method comes third because it is
what makes the later numbers legible. The measurements come fourth, and they
are the longest movement because six slides carry the tables. The findings
that qualify the verdict come fifth, because that is the turn in the
argument, and the reading and the limits come last.

## A.3 Where the argument turns

The argument turns on slide 18, and it turns against the work's own first
reading.

Everything before slide 18 could be read as a straightforward success. The
gate cut the rate of answering unanswerable questions from
{{GEN_A_NOGATE_UNANS_ANSWER_RATE}} to {{GEN_A_FITTED_UNANS_ANSWER_RATE}},
and the paired test is significant. The obvious summary is that confidence
gating reduces the number of unanswerable questions the system answers.

Slide 18 exists to destroy that sentence, because it is true and misleading.
The random-escalation control reaches {{GEN_A_RANDOM_UNANS_ANSWER_RATE}}, which
is worse than the fitted gate's {{GEN_A_FITTED_UNANS_ANSWER_RATE}}, and still
far below the ungated arm's {{GEN_A_NOGATE_UNANS_ANSWER_RATE}}. Refusing at
random is already a large improvement over never refusing, because most
questions in a benchmark are unanswerable. What the score buys is where the
refusals land: the fitted gate refuses {{GEN_PAIRED_FITTED_ANS_B}} answerable
questions, the random control refuses {{GEN_PAIRED_RANDOM_ANS_B}}, and counting
from the records the gate removes
{{TRADE_ANSWERING_WRONG_REMOVED}} wrong answers at a cost of
{{TRADE_ANSWERING_CORRECT_COST_NLI}} correct answer.

That is why slide 18 gets a slide of its own. A talk that reported the
headline rate and stopped there would be misreported, and the misreport is
the kind a panel finds.

## A.4 The slide the talk is built around

Slide 17. It is the only slide where a gate's refusal is measured against a
generator that cannot decline on its own, which is what makes the comparison
a comparison.

Under a prompt that permits a decline, the generator refuses most
unanswerable questions by itself, the gate's refusals are largely redundant
there, and the arms cannot be told apart. That setup would have produced a
null result that meant nothing. The two prompt conditions exist so that the
primary result is not an artefact of the prompt, and the reason is given on
slide 17 before the reader reaches the verdict.

## A.5 The five things the talk does not claim

| The claim the talk refuses | The sentence that would overstate it | Where the boundary is |
|---|---|---|
| That the framework beats plain BM25 on recall | "the pipeline retrieves better than BM25" | the dense leg is significantly worse than BM25 on the focus corpus, and fusion only stops that being a loss. The retrieval claim carries its corpus |
| That the gate lowers the answer rate on unanswerable questions | "confidence gating reduces hallucination" | the claim is about where the refusals land, not how many there are. The random control answers {{GEN_A_RANDOM_UNANS_ANSWER_RATE}} against the gate's {{GEN_A_FITTED_UNANS_ANSWER_RATE}}, and refuses {{GEN_PAIRED_RANDOM_ANS_B}} answerable questions against the gate's {{GEN_PAIRED_FITTED_ANS_B}} |
| That the contradiction mechanism works | "the gate detects contradictions" | its precision against reader labels is {{CONTRA_PRECISION_PCT}} on {{CONTRA_PRECISION_N}} alarms, and the corpus does not contain the phenomenon it detects |
| That a fitted threshold transfers | "the gate is calibrated" | the transferred arm answered {{GEN_A_XFER_ANS_ANSWERED}} answerable questions against the fitted gate's {{GEN_A_NOGATE_ANS_ANSWERED}} |
| That the system is ready for industrial use | "the framework is deployable" | the corpus is encyclopaedic industrial text and holds no instance records, specification tables or calibration logs |

Each of these is a sentence a reader could write down and quote back. They are
the five ways this work can be misreported, and the script is worded to make
each of them hard to misreport.

## A.6 Why the argument ends on the instruments

The closing note on slide 24 is the conclusion of the argument, not an
afterthought. The most useful thing this work produced was not the framework.
It was finding that two of its own instruments were reporting numbers a
careful reader could not trust, and changing the headline rather than
explaining it away. A framework's contribution is only as good as the
instruments that measured it.

The next-steps list is ordered the same way. Repeating the generator-side
comparison on a generator that returns text is first, because it would change
what the work can claim. Publishing the corrected benchmark and the shortcut
audit is last, because that part outlives the report.
