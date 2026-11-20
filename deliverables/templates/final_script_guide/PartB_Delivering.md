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
two numbers for it are {{UNANS_POLICY_AUC}} and {{UNANS_MC_SEP_AUC}}: a
classifier that saw only the question text, with no retrieval, no evidence
and no corpus, told the two classes apart at an ROC AUC of
{{UNANS_POLICY_AUC}} on the focus corpus and {{UNANS_MC_SEP_AUC}} on the
six-category one. Before the repair the same class produced a refusal rate of
{{UNANS_BEFORE_REFUSED_PCT}}.

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
