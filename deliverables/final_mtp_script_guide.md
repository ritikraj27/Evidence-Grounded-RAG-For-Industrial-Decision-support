---
title: "The Script, Explained"
subtitle: "How the ten-minute defence script is built, what each slide argues, and how to answer the panel"
author: "Ritik Raj (25IM60R12), Department of Industrial and Systems Engineering, IIT Kharagpur"
date: ""
shorttitle: "The script, explained"
---
# How to use this

This document explains the speaker script for the final defence deck,
`final_mtp.pptx`. It is written to be read beside the script, not instead of
it. The script is what you say. This is what tells you why it says it that
way, and what to do with the ten minutes you have.

**What is in it.** Four parts. Part A is the argument the talk makes: the
seven movements, what each one has to establish, where the argument turns,
and the five things the talk deliberately does not claim. Part B is the
mechanics of delivering it: where the clock goes, what to cut when you are
running late, where to point, and what to do when something goes wrong. Part C
is the script slide by slide, with the claim each slide makes, the claim it
refuses to make, and the trap on it. Part D is the numbers that have to be
said exactly, the mistakes the talk is built to avoid, and the questions to
expect with what each answer rests on.

**The documents, and which one to reach for.**

| Document | What it holds | When to read it |
|---|---|---|
| The deck, `final_mtp.pptx` | what the audience sees | the morning of |
| The script, `final_mtp_script.pdf` | what to say, slide by slide, with the slide printed above the words | rehearsing |
| This document | why the script is written the way it is, and how to deliver it | the day before, and on the morning |
| The complete reference, `final_mtp_reference.pptx` | every table and every formula at full size, seventy-five slides | when a question goes where the script does not reach |
| The terminology guide, `MTP_Terminology.pdf` | every keyword, in plain language and in technical language, with the number that belongs to it | when a word is used that you have not had to think about |

**What this document does not do.** It does not replace the report, and it
does not carry the derivations, which are in the report. Where a number
appears here, it is the number on the slide, and the report carries the
measurement behind it. It is the document that tells you what to do with the
ten minutes you have, which is the one thing none of the others can do.

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
0.938 to 0.528,
and the paired test is significant. The obvious summary is that confidence
gating reduces the number of unanswerable questions the system answers.

Slide 18 exists to destroy that sentence, because it is true and misleading.
The random-escalation control reaches 0.604, which
is worse than the fitted gate's 0.528, and still
far below the ungated arm's 0.938. Refusing at
random is already a large improvement over never refusing, because most
questions in a benchmark are unanswerable. What the score buys is where the
refusals land: the fitted gate refuses 2 answerable
questions, the random control refuses 11, and counting
from the records the gate removes
59 wrong answers at a cost of
1 correct answer.

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
| That the gate lowers the answer rate on unanswerable questions | "confidence gating reduces hallucination" | the claim is about where the refusals land, not how many there are. The random control answers 0.604 against the gate's 0.528, and refuses 11 answerable questions against the gate's 2 |
| That the contradiction mechanism works | "the gate detects contradictions" | its precision against reader labels is 0.0% on 20 alarms, and the corpus does not contain the phenomenon it detects |
| That a fitted threshold transfers | "the gate is calibrated" | the transferred arm answered 6 of 32 answerable questions against the fitted gate's 32 of 32 |
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

# Part B. Delivering it

## B.1 The clock

Ten minutes exactly, and the spoken words come to about nine and a half. The
rest is the pause while you point at a table and the click between slides.
The timing table in the script gives the seconds for each slide and the clock
time at each one. It is a plan, not a wish.

Three checks during the talk, each at a slide where the clock is a round
number:

| After this slide | The clock should read | If you are past it |
|---|---|---|
| 11, the metrics and the protocol | 3:56 | cut slide 13 now, and slide 20 with it |
| 15, the operating point | 5:43 | cut slide 20, and point at the next-steps list on slide 24 rather than reading it |
| 19, long context | 7:45 | point at the next-steps list on slide 24 rather than reading it |

The last check is the one that saves you. Slide 21 and slide 22 are nineteen
and twenty-four seconds, and they are the two you should not cut, so by the
time you reach slide 19 you need to know whether the list on slide 24 is
going to be read or pointed at.

## B.2 What to cut, in what order

| Slide | Seconds | What it saves | Why it can go |
|---|---|---|---|
| 8, the retrieval formulas | 23 | 23 s | the stack is BM25, a dense leg, rank fusion, a reranker and a quota, and the numbers that matter are on slide 12 |
| 11, the metrics | 16 | 16 s | paired tests and per class, which slide 17 applies |
| 13, the quota placement | 20 | 20 s | it is a null, and it is finding F3 on slide 21 |
| 4, the literature table | 18 | 18 s | the two sentences on the slide carry the point, and slide 5 says what the review does not settle |
| 20, the contradiction gate | 21 | 21 s | it is finding F10 on slide 21 and the first negative result on slide 22 |
| 23, the limitations | 18 | 18 s | say the first limitation only, and let the table carry the other seven |

Cutting all six takes a little under two minutes off, which brings the talk
to about eight minutes.

**Do not compress slides 2, 12, 17 and 18.** Those four carry the problem,
the benchmark repair, the verdict and the finding most likely to be reported
wrongly. Slide 18 is on that list for a reason worth knowing in advance: "the
gate answers fewer unanswerable questions" is true and it is misleading,
because the random control answers even fewer. A talk that drops slide 18
leaves the audience with a claim the control contradicts.

## B.3 Pointing

One point per slide, and the script says where it is on every slide that has
one. The rule that makes it work is to say the number first and then point at
the row that carries it. Reading a number off a table while pointing at it is
what makes a talk slow down, and it makes the number harder to hear.

The pause after the point is three seconds. It is the silence where the
audience reads the number, and it is the only silence you should take.
Taking it deliberately is what keeps the pace up later.

Never read a table aloud. On the slides that carry a table, the table is there
so that a question can be answered by pointing rather than by talking.

## B.4 Voice

The numbers are said more slowly than the prose. In a talk, numbers are
usually the fastest thing, and here the numbers are the content, because the
audience is writing them down.

Three sentences not to rush:

- the sentence on slide 12 that gives the paired difference of 0.156;
- the sentence on slide 17 that gives the two prompt conditions;
- the sentence on slide 18 that says what the score buys.

Each of them is followed by a pause.

## B.5 If something goes wrong

**A slide on the screen is wrong.** Do not stop to fix it. Say the next line
of the script and move on. Every number the talk needs is in the script, so
the talk does not depend on the screen being right.

**The projector is unreadable.** The talk can be delivered from the script and
this document alone. Say that the tables are in the report, and read the
numbers rather than pointing.

**You are asked to stop early.** Give the verdict, the three qualifying
findings, and the closing note. That is slides 17, 18 and 24, and it is the
shape of the talk in miniature.

**You are asked to go back.** The slide most likely to be asked for is 10,
because it is where the benchmark's own shortcut was found and repaired. The
two numbers for it are 0.564 and 0.533: a
classifier that saw only the question text, with no retrieval, no evidence
and no corpus, told the two classes apart at an ROC AUC of
0.564 on the focus corpus and 0.533 on the
six-category one. Before the repair the same class produced a refusal rate of
91.7%.

## B.6 The room

Stand where you can see the screen and the audience is not behind you. Wait
for the slide to change before you speak. The audience reads first and hears
second, and a sentence that starts before the slide lands is a sentence about
the previous slide.

The deck is generated from the project, so the file is on every machine. The
institute's emblem is on every slide, and the only colour in the deck is the
institute's own purple, which is the colour the emblem is printed in. Nothing
on a slide needs a colour to be understood, so a photocopied handout of the
deck is still readable.

# Part C. The script, slide by slide

What each slide argues, why the script is worded the way it is, the claim it makes, the claim it refuses to make, and the trap on it. The wording of the script is the authoritative part; this part explains it.

## C.1 Title (15 seconds, clock 0:15)

**What it argues.** Nothing yet. It is the handshake and the promise: one question and its answer, and the numbers behind both.

**Why it is worded this way.** It names the four things the talk will cover, so the room knows the shape of the next ten minutes before the argument starts.

**The claim it makes.** None.

**The claim it refuses to make.** None. The instruction is not to read the title aloud word for word.

**The trap.** Spending the first fifteen seconds on yourself. Say your name clearly and move on.

## C.2 A wrong answer and a non-answer do not cost the same (27 seconds, clock 0:42)

**What it argues.** The asymmetry between a wrong answer and a non-answer is the reason a gate is worth building.

**Why it is worded this way.** It starts from the industry rather than from the method, because a refusal that costs a supervisor five minutes and a fabricated tolerance that costs a scrapped batch is a cost the room already understands. The card on the right is what keeps the claims honest: one generator, an encyclopaedic corpus, one corpus for long context.

**The claim it makes.** The research question, in the words the rest of the talk answers.

**The claim it refuses to make.** That this is a gap in the literature. The gap is not what earns the ten minutes; the measurement is.

**The trap.** Pointing at the takeaway band when you ask the question. That sentence is what the rest of the talk is for, and if the room has not heard it clearly, slides 3 to 24 lose their subject.

## C.3 Four objectives, six contributions (19 seconds, clock 1:01)

**What it argues.** The map of the work, and the reason the generator must be forced to answer.

**Why it is worded this way.** The third objective is the one that shapes the experiment, so the slide says why before the panel reads the tables. If the generator may decline on its own, the gate's contribution and the generator's willingness to answer are the same number.

**The claim it makes.** That the third objective shapes the experiment, because a gate's contribution cannot be separated from a generator's willingness to answer.

**The claim it refuses to make.** That six contributions are six novel mechanisms. Five of them are measurements and one is a repaired benchmark.

**The trap.** Reading the six contributions aloud. They are on the slide for the reader; the spoken part is RO3.

## C.4 The literature, in eight threads (18 seconds, clock 1:19)

**What it argues.** Two things are taken from the literature: the mechanism is prior art, and a null under a cautious prompt has to be described in a particular way.

**Why it is worded this way.** The table is not a review for its own sake. It is there to say two things: that the mechanisms are prior art, and that a null under a cautious prompt has to be described in a particular way. Both of those are needed later, when a null is reported.

**The claim it makes.** That the abstention mechanism and the retrieval stack are prior art, and that the measurement is not.

**The claim it refuses to make.** That the literature has never measured a gate on industrial text. It has not, and the next slide says so.

**The trap.** Reading eight threads. Say the two sentences and move on.

## C.5 The gap, and what this work adds (24 seconds, clock 1:43)

**What it argues.** The contribution is a measurement, not an architecture.

**Why it is worded this way.** The contribution is stated as a measurement and not as an architecture, because the architecture really is prior art, and saying so is the position that survives a question. The middle card is the gap, and it is the gap the review leaves, not the gap the work fills.

**The claim it makes.** The three questions the review does not settle, and the three things this work adds to answer them.

**The claim it refuses to make.** That the framework is new. It is assembled from prior art, and the slide says so.

**The trap.** Pointing at the right-hand card too early. The middle card is the gap, and the right-hand card is the answer to it.

## C.6 The framework is a five-stage pipeline (25 seconds, clock 2:08)

**What it argues.** The gate is in the path and cannot be bypassed.

**Why it is worded this way.** Non-bypassability is a property of the code rather than a claim about it, and the table says which two stages may refuse. The generator is called at one place, after the gate has accepted, so a refused query costs no model call at all.

**The claim it makes.** Non-bypassability. The gate is code, and the generator is called at one place, after the gate has accepted.

**The claim it refuses to make.** That the gate is a component somebody can switch off. It is in the path.

**The trap.** Reading the input and output columns. The table is there to be pointed at.

## C.7 The confidence gate, and its three formulas (25 seconds, clock 2:33)

**What it argues.** The gate is a calibrated query-level posterior over the retrieved pool.

**Why it is worded this way.** The feature vector is described as five statistics of the pool rather than of a chunk, because that is what makes the gate query-level. A chunk-level score admits the degenerate solution, which is high whenever the question looks familiar whether or not the answer is there.

**The claim it makes.** That every feature describes the pool rather than a chunk, which is what removes the degenerate chunk-level solution.

**The claim it refuses to make.** That the gate understands the question. It cannot; it only sees statistics of the pool.

**The trap.** Saying five features without saying what they are. The panel will ask, and the answer is the top reranker score, the mean reranker score, the top BM25 score, the best fused score, and the count above the reranker's own bar.

## C.8 The retrieval stack, and its three formulas (23 seconds, clock 2:56)

**What it argues.** The retrieval stack is assembled from prior art, and the quota is a floor rather than a ceiling.

**Why it is worded this way.** Every mechanism on this slide is named and credited, so that nothing later can be read as a claim of novelty. The quota is described as a floor rather than a ceiling, because slide 13 shows that where it is applied is a configuration value.

**The claim it makes.** That every mechanism in the stack is from the literature.

**The claim it refuses to make.** That the quota placement is a rule. Slide 13 shows that it is a configuration value.

**The trap.** Saying the quota improves retrieval. It does not; the three corpora disagree about it.

## C.9 The corpora and the benchmark (19 seconds, clock 3:15)

**What it argues.** The roles of the four corpora do not overlap, and every number in the talk is quoted with its corpus.

**Why it is worded this way.** Four corpora with one job each, and the rule that their numbers are never mixed, because every number in the rest of the talk is quoted with the corpus it came from. A number without its corpus is the easiest thing in this work to misreport.

**The claim it makes.** That the focus corpus carries 32 answerable and 144 unanswerable questions, and that the corpora's numbers are never mixed.

**The claim it refuses to make.** That the primary corpus is the one measured on. It is proprietary supply-chain text that cannot be redistributed, so every measurement runs on a public substitute.

**The trap.** Being asked about the substitute before anybody asks. Say that the primary corpus is proprietary supply-chain text that cannot be redistributed, and that the substitute ships with its provenance.

## C.10 The benchmark, and the audit that checks it (35 seconds, clock 3:50)

**What it argues.** The unanswerable half of the benchmark was rebuilt, and the audit is the evidence that the rebuild worked.

**Why it is worded this way.** The audit is the hard half of the work, and the question-only classifier is the number that answers the obvious objection. The slide says what the audit is for, so the reader knows it is not there to make the numbers look good.

**The claim it makes.** That a classifier seeing only the question text cannot tell the classes apart: ROC AUC 0.564 on the focus corpus and 0.533 on the six-category one.

**The claim it refuses to make.** That the class is now unattackable. It is audited, and the audit is what it is.

**The trap.** Saying the class is perfect. The certificate count and the two AUCs are the honest numbers, and both are on the slide.

## C.11 The metrics and the protocol (16 seconds, clock 4:06)

**What it argues.** Every comparison is paired, and every test is applied per class.

**Why it is worded this way.** Two rules carry the whole results section, and they are stated as rules rather than defended, because they are properties of the design. Every comparison is paired because the arms answer the same questions, and every test is per class because a gate can improve one class and damage the other at the same time.

**The claim it makes.** Paired testing for the retrieval side, the exact McNemar test for the generation side, and effect sizes for the headline comparisons.

**The claim it refuses to make.** That a single pooled figure describes the system. It does not.

**The trap.** Reading the formulas. The symbol table names every one of them.

## C.12 Retrieval: seven configurations over the same 32 queries (31 seconds, clock 4:37)

**What it argues.** The dense leg loses, fusion recovers the loss, and the reranker's value depends on the corpus.

**Why it is worded this way.** The number first and the meaning after it, and the effect size beside the p value, because a paired difference of 0.156 on 32 queries needs both. The claim is deliberately narrow: fusion stopped being a loss and did not become a win over BM25.

**The claim it makes.** That the dense leg is significantly worse than BM25 here, at 0.812 against 0.969 with a paired difference of 0.156, and that fusion stopped being a loss.

**The claim it refuses to make.** That fusion beat BM25. It did not, significantly.

**The trap.** Saying fusion improved retrieval. Say that it recovered the loss the dense leg caused.

## C.13 The quota has no universally better placement (20 seconds, clock 4:57)

**What it argues.** The quota placement is a configuration value rather than a rule.

**Why it is worded this way.** It is a null, and it is reported as one, with the direction reversal visible in the two recall columns. The slide is here because a configuration value with a corpus attached is more useful to the next person than a rule that does not hold.

**The claim it makes.** That the direction reverses between corpora and that none of the three differences is significant.

**The claim it refuses to make.** That the quota placement is settled. It is not, and the slide says so.

**The trap.** Reading the p values as evidence that there is no difference. They are evidence of no difference established here, at this sample size.

## C.14 More candidates are not monotonically better (24 seconds, clock 5:21)

**What it argues.** The candidate-pool curve peaks and then declines, and which way it fails depends on the corpus.

**Why it is worded this way.** The focus curve and the industrial curve fail in different directions, so the note says which is which. On the focus corpus the gold chunk is found and then pushed out by the reranker; on the industrial corpus it is still arriving at a pool of fifty.

**The claim it makes.** That the focus curve peaks at a pool of ten and falls to 0.969, while the industrial curve is still arriving at a pool of fifty.

**The claim it refuses to make.** That a larger pool is always better, or always worse. It depends on whether the gold chunk is still arriving.

**The trap.** Giving the mechanism for the industrial curve. The displacement is the reason: the gold is retrieved and then pushed out of the ten-chunk context.

## C.15 The operating point, and the frontier behind it (22 seconds, clock 5:43)

**What it argues.** The operating point comes from a rule stated in advance, and the whole frontier is shown.

**Why it is worded this way.** The threshold comes from a rule stated in advance, and the whole curve is shown because a single threshold hides the shape behind it. A reader who wants a different operating point can read it off the first column.

**The claim it makes.** That at the fitted point the coverage is 0.693 and the abstention precision is 0.963.

**The claim it refuses to make.** That the fitted threshold is the only defensible one. It is the one the stated rule picks.

**The trap.** Quoting only the fitted point. The table is there so the panel can read a different threshold off it.

## C.16 The gate on the unanswerable class (26 seconds, clock 6:09)

**What it argues.** The gate detects a recognisable unanswerable question and is much weaker on the on-topic-but-unanswered case.

**Why it is worded this way.** The gap between the two strata is the finding, and the ROC AUC of 0.608 is given so the panel can see how much shape is left. The gate detects a recognisable unanswerable question and is much weaker when the topic is on-topic but unanswered.

**The claim it makes.** That it refuses 23.6 percent of the hard stratum and 26 of the 34 out-of-domain questions, and that the question-only classifier reaches an ROC AUC of 0.608.

**The claim it refuses to make.** That the gate understands the evidence. It reads statistics of the pool.

**The trap.** Saying the gate solves the unanswerable class. The gap between the two strata is the finding, and the gap is not small.

## C.17 The framework's own hypothesis, under two conditions (31 seconds, clock 6:40)

**What it argues.** The framework's own hypothesis holds under both prompt conditions, and the threshold does not transfer.

**Why it is worded this way.** Both prompt conditions are on one table, because the point is that the verdict does not depend on which prompt is used. The transferred row is called out because it is the one that over-refuses badly, and it is the row a panel is most likely to pull on.

**The claim it makes.** That the gate reduces the rate of answering unanswerable questions from 0.938 to 0.528 under the answering prompt and from 0.535 to 0.417 under the cautious one, and that both tests are significant.

**The claim it refuses to make.** That the gate generalises across corpora. The transferred arm answered 6 of 32 answerable questions.

**The trap.** Reading the table row by row. Read the fitted row and the no-gate row, and let the table carry the rest.

## C.18 What the confidence score actually buys (34 seconds, clock 7:14)

**What it argues.** The score buys refusal precision, not a lower answer rate.

**Why it is worded this way.** This is the finding most likely to be misreported, so the slide states the misleading sentence and then destroys it with the control. The score does not lower the answer rate; it places the refusals, and the two refusals against eleven is the whole claim.

**The claim it makes.** That the gate refuses 2 answerable questions where the random control refuses 11, and that the gate removes 59 wrong answers at a cost of 1 correct answer.

**The claim it refuses to make.** That the gate answers fewer unanswerable questions than a control would. It does not, and that sentence is the misleading one.

**The trap.** Saying the gate answers fewer unanswerable questions. It is true and it is misleading, because the random control answers fewer still.

## C.19 Long context against the pipeline (31 seconds, clock 7:45)

**What it argues.** A token ratio is not a cost ratio, and the long-context arm loses on accuracy while costing more.

**Why it is worded this way.** The two ratios are the point, and the sentence about the token ratio is the one that stops an argument about money being made from a prompt-size number. Most of the long-context arm's tokens are cache reads, so the cost ratio is much smaller than the token ratio.

**The claim it makes.** That the focus corpus is 202,529 tokens against an accepted context of 2,246, which is 74 times the tokens and 58.8 times the cost.

**The claim it refuses to make.** That long context wins. It matched the coverage and lost the accuracy.

**The trap.** Quoting the token ratio alone. Most of those tokens are cache reads at a fifth of the base rate.

## C.20 The contradiction gate: a precision of zero (21 seconds, clock 8:06)

**What it argues.** The contradiction detector's precision is zero against reader labels, and the corpus does not hold the phenomenon.

**Why it is worded this way.** Reported as unconfirmed with a bound rather than as a defect, and the reason is on the slide: this corpus does not hold the phenomenon the detector detects. The annotators agreed on all 101 decisions, so the labelling is not what is wrong.

**The claim it makes.** That twenty alarms were raised and none was confirmed, with a 95 percent upper bound of 16.1 percent on the true precision.

**The claim it refuses to make.** That the mechanism does not work. It is unproven, not disproven.

**The trap.** Reporting the detector's recall instead. Recall against a ground truth defined by the detector's own threshold measures agreement with itself.

## C.21 The findings, all fourteen (19 seconds, clock 8:25)

**What it argues.** Fourteen measured findings, with the negative ones in the same list.

**Why it is worded this way.** Every finding is measured, and the negative ones are in the same list, and the slide says so, because a table with the negatives removed reads as a list of successes. This is the slide to leave up during the questions.

**The claim it makes.** That every finding is a measured result, and that the ones contradicting the framework are reported in the same voice.

**The claim it refuses to make.** That the list is fourteen successes. Five of them are nulls or negative results.

**The trap.** Reading the fourteen rows. Say that they are all there, and that the negatives are in the same list.

## C.22 What the measurements support, and what they do not (24 seconds, clock 8:49)

**What it argues.** Three things the measurements support and three they do not, in the same voice.

**Why it is worded this way.** Three supported claims and three negative results are given the same weight on one slide, and the negative ones are named as results rather than as caveats. The gate's cost is coverage, not quality, and the benchmark was the harder half of the problem.

**The claim it makes.** That the gate works by placing its refusals, that its cost is coverage rather than quality, and that the benchmark was the harder half of the problem.

**The claim it refuses to make.** That the negative results are caveats. They are results.

**The trap.** Skipping the negative card. It is the half of the slide a panel trusts.

## C.23 The limitations (18 seconds, clock 9:07)

**What it argues.** Eight limitations, led by the largest gap in the work.

**Why it is worded this way.** The first row is the largest gap in the work and it is said first rather than last, because a limitation the panel finds is worth more than one volunteered late. The replication could not be run, so the hypothesis is supported for the generator tested and not in general.

**The claim it makes.** That the hypothesis is supported for the generator tested and not in general, because the replication could not be run.

**The claim it refuses to make.** That the work is ready for deployment. The corpus holds no instance records, specification tables or calibration logs.

**The trap.** Reading all eight. Say the first and point at the table.

## C.24 The conclusion, and the future work (23 seconds, clock 9:30)

**What it argues.** What the work establishes, and the nine steps that would change what it can claim.

**Why it is worded this way.** The conclusion names the three qualifying findings rather than only the verdict, and the nine steps are ordered by what they would change. The closing point is the sentence to land, and it is the honest one: the most useful thing here was the instruments that turned out not to be trusted.

**The claim it makes.** A cost-coverage-reliability frontier for a gate on industrial text, at the level of the individual answer claim.

**The claim it refuses to make.** That the verdict stands without its three qualifiers. It is named with them.

**The trap.** Reading the nine steps aloud. Point at the table, and answer with item 1 if the chair asks what you would do next.

## C.25 The references (7 seconds, clock 9:37)

**What it argues.** Every mechanism in the framework is already in the literature.

**Why it is worded this way.** Not read aloud. The point of the slide is that every mechanism is already in the literature, and the slide is left up long enough to be photographed when a panel asks where the gate comes from.

**The claim it makes.** Nothing. The slide is the evidence for the claim made on slide 5.

**The claim it refuses to make.** None.

**The trap.** Reading eight references aloud. Leave the slide up long enough to be photographed.

## C.26 Thank you (10 seconds, clock 9:47)

**What it argues.** That the work is finished, and where to find it.

**Why it is worded this way.** It is left up for the questions, and the line under the rule says where the full text is. The last thing said aloud is that every figure came from an archived result file, which is true.

**The claim it makes.** That every figure in the deck comes from an archived result file.

**The claim it refuses to make.** None.

**The trap.** Talking over the questions. Leave the slide up and stop.

# Part D. The numbers, the traps and the questions

## D.1 The numbers to say exactly

These are the load-bearing numbers. If one of them is misremembered, the
claim it carries does not hold, and the numbers are the part the audience
writes down.

| Number | What it is | Where it comes from |
|---|---|---|
| 0.969 and 0.812 | Recall@10 for BM25 alone and for the dense leg alone | the focus ablation, 32 queries, paired |
| 0.025 and 0.014 | the p values for BM25 against dense, and for fusion against dense | the same archived comparison |
| 1.000 | Recall@10 for fusion by reciprocal rank fusion | the focus ablation |
| -0.3 pp and 11.1 pp | what the reranker moves MRR on the focus and the six-category corpora | two separate corpora, two separate runs |
| 0.157, 0.480 and 0.317 | the p values for the quota placement on three corpora | three corpora, each from its own ablation |
| 0.05 | the gate's threshold | the rule: the highest that still answers 90 percent of the answerable questions |
| 0.693 and 0.963 | coverage and abstention precision at that threshold | the threshold sweep |
| 0.1044 | the calibration error of the confidence score | reported, not improved by refitting |
| 0.564 and 0.533 | the question-only classifier's ROC AUC on the focus and six-category corpora | the benchmark audit |
| 23.6% | the gate's refusal rate on the repaired hard stratum | the repaired unanswerable class |
| 91.7% | the refusal rate the defective class suggested | the shortcut audit, reported as the upper bound it was |
| 0.938 to 0.528 | the rate of answering unanswerable questions, ungated then gated, under the answering prompt | the generation experiment, paired McNemar |
| 0.535 to 0.417 | the same, under the cautious prompt | the second condition, p = 0.002 |
| 2 against 11 | answerable questions refused by the fitted gate and by the random control | the precision claim, and the only place the score shows up |
| 59 and 1 | wrong answers removed and correct answers lost, counted from the records | the trade at the operating point |
| 74 and 58.8 | the token ratio and the cost ratio against long context | the long-context run, with cached-prefix pricing |
| 0.406 against 0.667 | per-answer accuracy for long context and for the gated pipeline | the same run |
| 0.0% and 16.1% | the contradiction detector's precision and its 95 percent upper bound | against reader labels, not the detector's own threshold |
| 101 of 101 | the annotator agreement on the contradiction decisions | two annotators that do not share a model |
| 24 of 66 | the questions on which the second generator returned no text | the reason the replication could not be run |

## D.2 The mistakes the talk is built to avoid

Each of these is true, and each misleads. They are the traps from Part C,
collected in one place.

**"The gate answers fewer unanswerable questions."** True. Misleading, because
the random control answers fewer still, at 0.604
against the fitted gate's 0.528. The gate's
contribution is precision of refusal, not a lower answer rate.

**"Fusion improves retrieval."** The dense leg is significantly worse than
BM25 here, and fusion recovers it to 1.000, but fusion is not a significant
win over BM25 on its own. Say "fusion stopped being a loss".

**"The reranker improves ranking."** It does on the six-category corpus, by
11.1 points of MRR. On the focus corpus it moves MRR by
-0.3 points. The sentence is never used without its corpus
attached.

**"The gate rejects malformed questions."** It does not. It accepts
76.7% of malformed stems. It is an evidence gate, not a form
gate, and a separate validator does the form check.

**"The contradiction detector does not work."** Unproven, not disproven. The
precision is 0.0% against reader labels with a 95 percent
upper bound of 16.1%, on a corpus that may simply not
contain the phenomenon.

**"The gate reduces hallucinations."** The measurement is on the rate of
answering unanswerable questions. On generated text, the hallucination rate
is a different quantity computed by a different instrument. This is the
limitation on slide 23, and it is the most likely overreach in a summary of
the work.

**"A refusal is a safe answer."** A refusal is not an answer. The gate
reduces the opportunity for a fabricated answer by declining. It does not make
the answers it does give more correct.

**"The system is safe for industrial deployment."** Nothing here supports
that. The corpus is encyclopaedic, not procedural. It holds no instance
records, specification tables or calibration logs of the kind a deployment
would query.

## D.3 The questions to expect

### About the contribution

**"Is your framework new, or is it assembled from existing work?"**
It is assembled from existing work, deliberately. BM25, dense retrieval,
reciprocal rank fusion, the cross-encoder reranker and conformal abstention
are all prior art, and the deck says so on slides 4 and 5. What is new is the
measurement: the gate is measured end to end against a random-escalation
control, the benchmark is audited before it is trusted, and the frontier is
reported at the level of the individual answer claim.

**"What is your single strongest claim?"**
That the gate places its refusals. The fitted gate refuses
2 answerable questions where the random control
refuses 11, and it removes
59 wrong answers at a cost of
1 correct answer. That is a precision
claim, and it is the one the paired test supports.

**"If the mechanism is prior art, why is this a master's project rather than
an engineering report?"**
Because the engineering report would have been a sentence with no number
attached. The work is in finding that two of the project's own instruments
reported numbers a careful reader could not trust, rebuilding the benchmark
class that was causing it, and changing the headline from
91.7% to 23.6%. And in
establishing what the confidence score does and does not buy, which is a
question the prior work did not answer.

### About the method

**"Why a query-level gate rather than a chunk-level one?"**
Because a chunk-level gate admits the degenerate solution: pick the single
chunk the reader is most confident about, and the confidence is high whenever
the question looks familiar, whether or not the answer is there. Every
feature in the feature vector describes the candidate pool rather than any
chunk, so the score cannot be gamed that way.

**"Why Platt scaling rather than a deeper classifier?"**
Because the question is whether the score is calibrated, and a
one-parameter family fitted by maximum likelihood on 60 percent of the
queries can be calibrated and audited. The calibration error is
0.1044, reported rather than improved by refitting, which is the point:
a number that is not reported cannot be checked.

**"Why 90 percent as the threshold rule?"**
It is a stated rule, chosen before looking at the outcome: the highest
threshold that still answers at least 90 percent of the answerable questions.
The point of stating the rule is that the operating point is not chosen to
flatter the result, and the whole frontier is shown so that the panel can see
what the other thresholds would have given.

**"What is the modality quota, and why does it exist?"**
A floor on the share of the final context given to tables and charts relative
to text, so that a text-heavy pool cannot starve a modality that carries the
answer. It is a floor, not a ceiling, and when the pool cannot supply it the
floor is relaxed rather than invented. Where it is applied turned out not to
matter, which is slide 13 and finding F3.

**"How was the gate calibrated without leaking the test data?"**
The logistic model is fitted by maximum likelihood on 60 percent of the
queries. The remaining 40 percent is the held-out evaluation half, and the
threshold sweep reported on slide 15 is on that half.

### About the running of the system

**"How long does a query take, and how long is each stage?"**
Measured directly, on the real index with the real models, over the
176 focus-corpus queries. The retrieval path is
124 milliseconds on average, 158 at the
median and 166 at the 95th percentile. The cross-encoder
rerank is 122 of those milliseconds, which is almost all of the
framework's own work; the query embedding is 0.8, the dense leg
0.7, the lexical leg 0.1, and the rank fusion, the
modality quota and the gate together come to under a millisecond.

**"And when the gate refuses to answer?"**
A refusal is not a faster answer. The gate's decision is taken at the end of
the retrieval path, so a refused query costs the same 0.12
seconds of retrieval and then stops: the model is never called and no answer
is generated. On the focus benchmark the gate refused 60 of
the 176 queries, and the latency run reproduces the archived
run's refusals exactly, which is the check that the timing was measured on the
same system as the results.

**"And when it does answer?"**
The generation dominates, and it is not the framework's cost. From the
archived arm totals, the model call together with the offline claim-scoring
pass costs between 4.2 and 13.6
seconds per answered query, depending on the arm and the prompt condition. The
framework's own share is 0.12 seconds: under three percent of an
answered query, and the whole of a refused one. The long-context arm, which
sends the whole corpus in the prompt and does no retrieval at all, costs
8.4 to 10.2 seconds per
query.

### About the statistics

**"Why paired tests?"**
Because the arms answer exactly the same questions, so each query is its own
control. An unpaired test would treat the arms as independent samples and
throw away the pairing.

**"Why McNemar rather than a chi-squared test on the same counts?"**
McNemar is the exact paired test for two proportions on the same units, and
it is exact here rather than asymptotic. The counts are small enough for the
exact version to matter.

**"What do b and c mean in your table?"**
b is the number of questions the first arm answered and the second refused; c
is the number the first refused and the second answered. The other two cells,
both answered and both refused, carry no information about the direction of
the difference. For the fitted gate against the ungated arm, b = 60 and c = 1
on the unanswerable class.

**"Is the effect size meaningful, or only the p value?"**
Both are reported. The dense leg against BM25 has a paired difference of
0.156 in Recall@10, Cohen's d of 0.42 and Cliff's delta of
0.16. Cliff's delta of 0.16 is a small effect, which is why
the sentence about fusion is narrow and the sentence about the dense leg is
not: the dense leg is reliably worse, and it is not much worse.

**"You have several null results. Is this underpowered?"**
Yes, and that is stated as a limitation. The quota-placement and
fusion-over-BM25 comparisons are nulls at this sample size and are read as
"no difference established here", never as evidence of no difference.

**"What is the effect size for the headline result?"**
The headline is a proportion change from 0.938
to 0.528 on the unanswerable class, with a
paired exact McNemar test at p < 0.001, and it
replicates under the second prompt condition at p =
0.002 with a smaller effect. The precision claim on
the answerable class has b = 2 against b =
11.

**"Is there a multiple-comparisons correction?"**
The comparisons that carry the claims are the ones stated in advance by the
protocol: one per class per arm pair. The exploratory ones, the quota
placement across three corpora and the pool sweep, are reported as nulls and
as configuration findings rather than as claims, so no correction is applied
to them either.

### About the benchmark

**"How do you know your unanswerable class is not just a different kind of
question?"**
That is what the audit is for. Every unanswerable question is given a
structural twin in the answerable class: the same stem, the same subject
size, the same shape markers, and no word in common.
106 of 110 structural certificates pass. And the check that matters
is the question-only classifier, which sees the question text and nothing
else. Its ROC AUC is 0.564 on the focus corpus and
0.533 on the six-category one. If the class were identifiable
from its shape, those numbers would be high.

**"What was the shortcut you found?"**
The defective unanswerable class put a fabricated identifier in the hard case,
so a filter that looked only at identifiers found every hard question. It is
reported in the shortcut audit, which ships with the benchmark, and the
defective class's refusal rate of 91.7% is reported as
the upper bound it was rather than as a result.

**"Why does the closed-book accuracy appear in the audit?"**
Because a class that a model without retrieval can recognise as unanswerable
is measuring something else. The closed-book unanswerable rate is
0.094, and the audit table carries it so that the reader
can see the class was not obvious from the question alone.

**"You call the corpus encyclopaedic. Does that undermine the industrial
claim?"**
It narrows the claim, and the deck says so on slide 2 and slide 23. The
primary corpus is proprietary supply-chain text that cannot be redistributed,
so every measurement runs on a public substitute that ships with its
provenance. The claim is narrowed to match. No claim is made that depends on
the procedural documents the substitute does not contain.

### About the negative results

**"Your contradiction gate has zero precision. Why is it in the framework?"**
Because it was measured, and because a framework with a component that
silently does nothing is worse than one that reports it. The precision is
0.0% against reader labels, with a 95 percent upper bound
of 16.1%, and the annotators agreed on all
101 decisions, so the labelling is not the problem.
The mechanism is unproven rather than disproven: this corpus does not hold
the phenomenon the detector detects.

**"Why not report the contradiction detector's recall instead?"**
Because recall against a ground truth defined by the detector's own threshold
measures agreement with itself, not precision. That is the mistake the
contradiction thread in the literature review is there to prevent.

**"The reranker makes things slightly worse on your focus corpus. Why keep
it?"**
Because on the six-category corpus it moves MRR by 11.1
points, and the system has to run on more than one corpus. The honest summary
is that a component that helps on one corpus and not on another is not a
component that helps, and the sentence about the reranker is never used
without its corpus attached.

**"Your transferred threshold over-refuses. Isn't that just a failure?"**
It is a failure, and it is finding F12. A calibrated threshold does not
transfer across corpora: the transferred arm answered
6 of 32 answerable questions against
32 of 32 for the ungated arm. That is the reason the
threshold is a configuration value rather than a property of the method, and
it is the first item on the future-work list to settle.

### About the scope

**"Why only one generator?"**
Because the replication could not be run. The second model returned no text
on 24 of the 66
questions, so there was nothing to compare. That is the first limitation on
slide 23 and the first item on the future-work list.

**"How general is the result?"**
It is established for the generator tested, on these corpora, in English and
one jurisdiction. The measurements show the gate's contribution to the rate of
answering unanswerable questions; they do not show the gate's contribution to
the hallucination rate on generated text, which is a different quantity with a
different instrument.

**"Why is the unanswerable class larger than the answerable class?"**
Because most questions in a corpus are not answered by it, and a benchmark
that answered everything would measure recall rather than refusal. That is
also why the random control looks good on the answer rate: refusing at random
is already a large improvement over never refusing, which is exactly why the
random control was needed.

**"How would this deploy?"**
It would not, on this corpus. A deployment queries instance records,
specification tables and calibration logs, which an encyclopaedic corpus does
not contain. The work gives the measurement instrument and the benchmark; the
corpus regime is the thing to change, and item 4 on the future-work list is
the change.

**"What would you do next, and in what order?"**
In this order. One, repeat the generator comparison on a generator that
returns text. Two, compare the gate against a token-level faithfulness
monitor. Three, settle the magnitude and the power of the positional
comparison. Four, extend the corpus. Five, stratify by modality under a
pre-registered power analysis. Six, hand-check the repaired class on both
corpora. Seven, run the long-context quality arm on a corpus that fits the
window. Eight, replace the model-based annotators with human readers. Nine,
publish the corrected benchmark and the shortcut audit as a separate artefact.

### About the writing of the deck

**"Why is the architecture on slide 6 but not in the contribution?"**
Because the architecture is prior art and saying so is the honest position.
The contribution is the measurement, and slide 5 says exactly that in one
line: the architecture is not the contribution, the measurement of it is.

**"Why does the deck report negative results with the same prominence as
positive ones?"**
Because a negative result stated plainly is worth more to the next person
than a positive one that was overstated, and because moving the negatives to
a separate slide would make the findings table read as a list of successes.

## D.4 When you do not know

Some questions will go past what the deck carries. The complete reference
deck and the report are there for that. The rule is:

1. Say what you do know, precisely, in one sentence.
2. Say where the answer is: "that is in the report, in the section on the
   benchmark audit" or "that is in the reference deck".
3. Say plainly that it is not something you measured, if it is not.

Never guess a number. A panel member who is told "I would have to check" has
learned something about the work. A panel member who is told a wrong number
has learned that the other numbers cannot be trusted either.

If a question attacks something the work does not claim, that is the easiest
answer there is: "that is not a claim this work makes". The limitations on
slide 23 are there to be quoted.
