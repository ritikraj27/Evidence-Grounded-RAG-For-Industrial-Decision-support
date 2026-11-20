---
title: "The Script, Explained"
subtitle: "How the ten-minute defence script is built, what each slide argues, and how to deliver it"
author: "Ritik Raj (25IM60R12), Department of Industrial and Systems Engineering, IIT Kharagpur"
date: ""
shorttitle: "The script, explained"
---
# How to use this

This document explains the speaker script for the ten-minute defence deck. It
is written to be read beside the script, not instead of it. The script is what
you say. This is what tells you why it says it that way, and what to do with
the ten minutes you have.

**What is in it.** Four parts. Part A is the argument the talk makes: the
seven movements, what each one has to establish, where the argument turns, and
the four things the talk deliberately does not claim. Part B is the mechanics
of delivering it: where the clock goes, what to cut when you are running late,
where to point, and what to do when something goes wrong. Part C is the script
slide by slide, with the claim each slide makes, the claim it refuses to make,
and the trap on it. Part D is the numbers that have to be said exactly, the
five mistakes the talk is built to avoid, and the questions to expect with
what each answer rests on.

**The four documents, and which one to reach for.**

| Document | What it holds | When to read it |
|---|---|---|
| The deck, `MTP_Defence_Deck.pptx` | what the audience sees | the morning of |
| The script, `MTP_Defence_Deck_Script.pdf` | what to say, slide by slide, with the slide printed above the words | rehearsing |
| This document | why the script is written the way it is, and how to deliver it | the day before, and on the morning |
| The companion, `MTP_Defence_Deck_Companion.pdf` | every term, every formula and every measurement behind the deck | when a question goes where the script does not reach |

**What this document does not do.** It does not replace the report, and it does
not carry the derivations, which are in the report. Where a number appears
here, it is the number on the slide, and the companion carries the measurement
behind it. It is the document that tells you what to do with the ten minutes
you have, which is the one thing none of the others can do.

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
unanswerable at ROC AUC 0.999 against a permutation null of
0.455. So the headline refusal rate of
91.7% was measuring the benchmark rather than the
framework.

After slide 14 the numbers are on a benchmark that can be trusted, and they
are much smaller: 23.6% on the hard stratum, where the
corpus discusses the subject but does not state the answer, against
76.5% on the out-of-domain stratum, where the question
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
| That the gate lowers the answer rate on unanswerable questions | "confidence gating reduces hallucination" | the claim is about where the refusals land, not how many there are. The random control answers the unanswerable class at 0.604 against the gate's 0.528, and still spends eleven refusals on answerable questions against the gate's two. |
| That the contradiction mechanism works | "the gate detects contradictions" | its precision against reader labels is 0.0% on 20 alarms, and the corpus does not contain the phenomenon it detects. |
| That a fitted threshold transfers | "the gate is calibrated" | a calibrated threshold fitted on one half of a corpus over-refuses on the other half. The transferred arm answers 6 of 32 of the answerable questions against the fitted gate's 30 of 32. |

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

# Part B. Delivering it

## B.1 The clock

Ten minutes exactly. The spoken words come to about nine and a half, and the
rest is the pause while you point at a table and the click between slides. The
timing table in the script gives the seconds for each slide and the clock
time at each one. It is a plan, not a wish.

Three checks during the talk, each at a slide where the clock is a round
number:

| After this slide | The clock should read | If you are past it |
|---|---|---|
| 6, the contradiction gate and the form validator | 2:45 | cut slide 11 now, and slide 10 with it |
| 13, the operating point | 5:18 | cut slides 20 and 23 |
| 19, the contradiction gate's precision | 8:27 | point at the next-steps list on slide 23 rather than reading it |

The last check is the one that saves you. Slide 21 and slide 22 are twenty and
twenty-eight seconds, and they are the two you should not cut, so by the time
you reach slide 19 you need to know whether the list on slide 23 is going to
be read or pointed at.

## B.2 What to cut, in what order

| Slide | Seconds | What it saves | Why it can go |
|---|---|---|---|
| 10, the modality quota | 15 | 15 s | it is a retrieval result whose place in the argument is carried by the findings table on slide 21 |
| 11, the candidate pool | 15 | 15 s | the same |
| 20, the attribution | 20 | 20 s | finding F13 on slide 21 carries it |
| 23, the next steps | 23 | 20 s | the list can be pointed at once the closing point has been made |
| | | **70 s** | |

**Do not compress slides 2, 14, 16 and 17.** Those four carry the problem, the
benchmark repair, the verdict, and the finding most likely to be reported
wrongly. They are the talk.

Slide 17 is on that list for a reason worth knowing in advance. "The gate
answers fewer unanswerable questions" is true and it is misleading, because
the random control answers even fewer. The finding is about precision. A talk
that drops slide 17 and keeps slide 16 leaves the audience with a claim that
the random control also satisfies.

## B.3 Pointing

One point per slide, and the script says where it is on every slide that has
one. The rule that makes it work is to say the number first and then point at
the row that carries it. Reading a number off a table while pointing at it is
what makes a talk slow down, and it makes the number harder to hear.

The pause after the point is three seconds. It is the silence where the
audience reads the number, and it is the only silence you should take. Taking
it deliberately is what keeps the pace up later.

Never read a table aloud. On the slides that carry a table, the table is
there so that a question can be answered by pointing rather than by talking.
Slide 3 says this in the script: "read nothing from it".

## B.4 Voice

The numbers are said more slowly than the prose. In a talk, numbers are
usually the fastest thing in it, and here the numbers are the content, because
the audience is writing them down.

Three sentences not to rush:

- the research question on slide 2, because it is the sentence the rest of
  the talk answers;
- the benchmark artefact on slide 14, because it is the turn in the argument;
- the verdict on slide 16, because it is the sentence the whole talk was
  built to reach.

Each is followed by a pause. If you are running out of time, the place to
save is not these.

## B.5 If something goes wrong

**A slide on the screen is wrong.** Do not stop to fix it. Say the next line
of the script and move on. Every number the talk needs is in the script, so
the talk does not depend on the screen being right.

**The projector is unreadable.** The talk can be delivered from the script and
this document alone. Say that the tables are in the report, and read the
numbers rather than pointing.

**You are asked to stop early.** Give the verdict, the three qualifying
findings, and the closing note. That is slides 16, 21 and 23, and it is the
shape of the talk in miniature.

**You are asked to go back.** The slide most likely to be asked for is 14,
because it is the one that changes what the other numbers mean. The one
number for it is 0.999: a classifier that saw only the question
text told answerable from unanswerable at that ROC AUC, before the repair.

## B.6 The room

Stand where you can see the screen and the audience is not behind you. Wait
for the slide to change before you speak. The audience reads first and hears
second, and a sentence that starts before the slide lands is a sentence about
the previous slide.

The deck is generated from the project, so it is the same file on every
machine. The institute's emblem is on every slide, and the only colour in the
deck is the institute's own purple, which is the colour the emblem is
printed in. Nothing on a slide needs a colour to be understood, so a
photocopied handout of the deck is still readable.

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
0.05 on the focus domain.

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
Requiring both cut the alarms from 81 to
20.

**The claim it makes.** The form validator refused
25 of 25 hand-authored malformed
queries and 0 of 35 well-formed
ones, at 2.6 microseconds per query.

**The claim it refuses to make.** That the gate did the validator's work. The
gate accepted 76.7 percent of the malformed stems pushed through it, so it is
an evidence gate and not a form gate.

**The trap.** The memorable part is the counterfactual: reusing the benchmark
builder's question-generation rule as a runtime check would have refused
100.0% of the hand-labelled well-formed questions. A
filter written for one purpose does not fit another, and its false rejection
rate has to be measured before it ships.

## C.7 Three corpora, and a benchmark that had to be repaired (25 seconds, clock 3:10)

**What it argues.** The roles of the three corpora do not overlap, and the
benchmark needed three repairs.

**Why it is worded this way.** The audit instrument is kept and named, because
it is the instrument that found the defects. A reader who suspects the
benchmark was written to flatter the system is answered by the fact that the
tool that caught it is still there.

**The claim it makes.** The focus corpus carries 735 chunks
from 14 documents and is where the ablation, the gate and the
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
at p of 1.4 × 10⁻², and it improves the ordering too, MRR from 0.652 to
0.798.

**The claim it refuses to make.** That the reranker buys ordering. It does
that on the six-category corpus, where it moves MRR by 11.1 points at p of
0.00093, and it does not do it on the focus corpus, where it moves MRR by
-0.3 points and nDCG by -1.1, neither significant.

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
3.1 points of overall recall while table recall stays at
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
0.969 at twenty, fifty and a hundred.

**The claim it refuses to make.** That more context is better.

**The trap.** The industrial corpus behaves differently. There the gold chunk
is still arriving at fifty, so Recall@20 reaches 1.000 at a pool of fifty
while Recall@10 stays at 0.988. The sentence always carries its corpus.

## C.12 The gate is calibrated, and it is not excellent (22 seconds, clock 4:50)

**What it argues.** The gate is calibrated on the held-out evaluation half,
and the calibration is not excellent.

**Why it is worded this way.** The number is reported rather than improved by
refitting, because it describes one fitted artefact on one fixed split. The
industrial gate tracks the diagonal at an ECE of 0.075; the focus
gate does not, and it puts most of its queries in the lowest confidence bin,
where few of them have an answer in context.

**The claim it makes.** Expected calibration error 0.1044 and a Brier
score of 0.1510.

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
0.05.

**The claim it makes.** At the fitted operating point the abstention precision
is 0.963, and the coverage is 0.693.

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
repair the shape separability was 0.999; after it is
0.608. The true refusal rate is 23.6%.

**The claim it refuses to make.** The old rate of 91.7%.

**The trap.** The table's first two rows are two different classifiers, both
of which see only the question. The shape separability row is the one the
figure plots, 0.999 against 0.608. The question-only
policy row is a separate rule-based detector, 0.675
against 0.564. Reading them as one row's before and after
contradicts the figure on the same slide.

## C.15 One generator, five arms, two prompt conditions (28 seconds, clock 6:21)

**What it argues.** The design of the experiment, and why the replication on a
second generator could not be run.

**Why it is worded this way.** An empty completion is neither an answer nor a
refusal. That model returned no text on 24 of 66 of its
questions, 23 of 44 of them on the benchmark's
table-lookup family, and raising the output budget fourfold rescued 13 and
left 11 still empty. A run like that is recorded
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
arm answers 135 of 144 unanswerable questions and the
fitted gate answers 76 of 144, with the paired exact
McNemar test significant on the unanswerable class at b of 60 and c of 1. On
the answerable class the gate answers 30 of 32 where the
ungated arm answers 32 of 32.

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
0.604 against the gate's
0.528 and the ungated arm's
0.938.

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

**The claim it makes.** 74 times the tokens per query and
58.8 times the input cost, with the cache read share at
33.0%. On coverage the whole-corpus prompt answered
32 of 32 answerable questions, the same as the ungated
pipeline.

**The claim it refuses to make.** A superiority claim over long-context
prompting. The accuracy margin, 0.406 against
0.667, is not significant under a length-controlled
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
readers were 14 of 14 on a control set with known labels,
and they agree with each other on 101 pairs.

**The claim it makes.** The precision against reader labels is
0.0% on 20 labelled alarms, reported
as a null with a 16.1% upper bound.

**The claim it refuses to make.** That the detector is broken. The readers
also found no contradictions in a random sample of
80 pairs the gate did not flag. A detector that finds
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
0.118 over the retrieved evidence and
0.542 over the gold chunk.

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

# Part D. The numbers, the traps and the questions

## D.1 The numbers to say exactly

Ten numbers, and what happens if one of them is wrong.

| Number | What it is | Slide | If you get it wrong |
|---|---|---|---|
| 23.6% | the gate's refusal rate on the hard stratum, after the repair | 14 | this is the headline, and the one a reader will check against the report |
| 26 of 110 and 26 of 34 | the two strata the rate is made of | 14 | the rate without the strata is a rate on nothing in particular |
| 0.999 against 0.608 | the shortcut's separability, before and after the repair | 14 | these two are the proof that the benchmark had to be repaired |
| 0.963 | abstention precision at the fitted operating point | 13 | this is the number the precision claim rests on |
| 0.05 | the fitted threshold on the focus domain | 5, 13 | every number on slide 13 is conditional on it |
| two against eleven | refusals spent on answerable questions, the gate against the random control | 17 | this pair is the difference between a gate and a coin flip |
| 0.528 against 0.604 against 0.938 | answer rates on the unanswerable class: gate, control, ungated | 17 | the control is worse than the gate here, and that is the point |
| 0.0% on 20 alarms | the contradiction gate's precision against reader labels | 19 | this is a measured zero, and saying it is unmeasured is a mistake |
| 74 and 58.8 | the long-context arm's token and cost penalty | 18 | the two are different numbers, and only the second is a cost |
| 0.1044 and 0.1510 | the focus gate's calibration | 12 | these are reported, not improved, and the slide says so |

## D.2 The five mistakes the talk is built to avoid

**Saying the gate lowers the answer rate on unanswerable questions.** It does
not. The random control answers that class at
0.604 against the gate's
0.528. The claim is about where refusals land,
and the control is what makes it visible.

**Pairing the two classifiers in the slide 14 table.** The shape separability
row is the one the figure plots, 0.999 against
0.608. The question-only policy row is a separate rule-based
detector, 0.675 against 0.564. Reading one
row's before-value against the other row's after-value produces a sentence
that is true of neither.

**Reading the accuracy columns on slide 17 as a quality gain.** The gated arm
answers an easier subset, because a gate declines the hardest questions. That
is a selection effect, and it is why per-answer accuracy cannot be compared
across arms with different coverage.

**Calling the contradiction gate's precision unmeasured.** It was measured, by
two independent annotators who read the sheet blind to the detector's scores,
and it is zero. Reporting it as unproven rather than as a null is the
mistake; it is a measured null with a 16.1% upper bound.

**Claiming that a calibrated threshold transfers.** It does not. The
transferred arm, fitted on one half of the cross-category corpus and applied
unchanged to the other half, answers 6 of 32 of the
answerable questions against the fitted gate's
30 of 32, and 3 of 144 of the
unanswerable ones.

## D.3 The questions to expect

**"Why is the refusal rate only 23.6%? That sounds low for
a gate."**
:   The answer rests on the class the rate is measured on, and on the repair.
    The rate is on the hard stratum, where the corpus discusses the subject
    but does not state the answer. On the out-of-domain stratum, where the
    question comes from outside the corpus entirely, the gate refuses
    26 of 34. Before the repair the rate was
    91.7%, and that number was measuring a shortcut in
    the benchmark rather than the system.
    *Follow-up:* "so is the gate useless?" No. A gate that detects a
    recognisable unanswerable question is worth having. A gate that detects an
    absent answer is what the report does not claim.

**"Is the improvement just the gate refusing more questions?"**
:   That is the question the random control exists to answer, and the answer
    is that the control refuses the same number of questions at random. The
    difference shows up on the answerable class, where the gate spends two
    refusals and the control spends eleven.
    *Follow-up:* "so what is the claim?" That it is a precision claim about
    refusals.

**"What is the cost of the gate?"**
:   Coverage. Every extra refusal is paid for in coverage, and the price
    climbs steeply past tau of 0.15. At the fitted operating point the gate
    answers 30 of 32 where the ungated arm answers
    32 of 32, and it removes 59 wrong answers for the
    cost of one correct answer under the entailment test.
    *Follow-up:* "is that trade worth it?" Whether it is worth making is a
    domain judgement, and these measurements do not settle it. Say that.

**"The contradiction gate did not work. Why keep it?"**
:   Because the corpus does not contain the phenomenon it detects. The readers
    found no contradictions in a random sample of 80
    pairs the gate did not flag either, so this is a statement about the
    corpus and not about the detector.
    *Follow-up:* "then delete it?" It is reported as a null rather than
    dropped, because the two defects the audit exposed were real and were
    fixed, and the corpus the framework would meet may contain the
    phenomenon.

**"How do you know the framework is better than just BM25?"**
:   On the focus corpus it is not, on recall. The dense leg is significantly
    worse than BM25, fusion recovers it to 1.000, and the reranker moves MRR
    by -0.3 points, which is not significant. On the six-category
    corpus the reranker moves MRR by 11.1 points at p of 0.00093.
    *Follow-up:* "then what is the contribution?" The gate, and the measurement
    of it, rather than the retrieval.

**"Why is the answer position effect not a finding?"**
:   Because the direction replicates in three of the four corpus-and-protocol
    measurements and ties in the fourth, and the magnitude does not replicate.
    It is stated with its magnitude rather than as a rule.
    *Follow-up:* "is it in the report?" Yes, with all four measurements, so
    the reader can see which one ties.

**"Can the framework be deployed?"**
:   Not on this corpus as it stands. The scope is narrowed to match what was
    measured: industrial-engineering encyclopaedic text rather than
    practitioner documentation, one generator rather than one model class,
    English and one jurisdiction.
    *Follow-up:* "what would it take?" The cost-coverage-reliability frontier
    is the deliverable, and a deployment team would have to calibrate the
    threshold on its own corpus and audit its own benchmark for the same
    shortcut before it trusted any number.

**"How was the benchmark shortcut found?"**
:   By auditing it, and by keeping the instrument. A classifier was trained on
    the question text alone, with no retrieval and no corpus, and it separated
    the two classes at ROC AUC 0.999.
    *Follow-up:* "how do I know you did not just fix the benchmark until it
    said what you wanted?" The pre-repair benchmark sits beside the repaired
    one, so every before-and-after claim can be regenerated, and the shortcut
    audit is the first of the six next steps to be published separately.

## D.4 When you do not know

Say what is known, say what is not, and say where it would be measured. "I do
not have that number in front of me; it is in the report in the section on
the long-context comparison, and the first item on the next-steps list is the
measurement that would settle it."

Do not estimate, and do not put "roughly" in front of a number. The one thing
a committee cannot check for itself is whether you made it up, and a hedge in
front of a number is the only place where that shows.
