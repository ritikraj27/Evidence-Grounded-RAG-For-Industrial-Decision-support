# 16 — The quota placement moved, and what that changed

**Written 16 November 2026**, for the 18 November 2026 defence.

## What changed

The shipped system applied the modality quota **after** the cross-encoder.
The ablation measured the **before** the cross-encoder placement and found it
better on the focus domain. The thesis said the rule had been inverted; the
code was still doing the pre-inversion thing, and every measurement in the
project had been taken with it.

The default was moved on 16 November 2026, and everything that depends on the
retrieval was re-measured with it, apart from three measurements whose
labels come from a panel of reader agents under a written protocol and could
not be reproduced. The limitation names them, and the disclosure is derived
from the provenance stamps in the result files rather than written by hand.

## Where the placement now lives

It is a configuration value, not a literal in a function signature:

```
impl/src/config.py     ModalityQuotaConfig.position = "pre_rerank"
impl/src/pipeline.py   Framework.retrieve(quota_position=None) resolves it
                        from the configuration, and rejects a value that is
                        neither "pre_rerank" nor "post_rerank"
```

Three things in the deliverables read that value rather than asserting it:

| Where | What it controls |
|---|---|
| `results_source.shipped_quota_position()` | whether the quota's next-step item exists at all |
| `substitute_tokens.QUOTA_PLACEMENT_LIMITATION_ROW` | the limitation row: the discrepancy text, or the note about the change |
| `substitute_tokens.SHIPPED_QUOTA_PLACEMENT` | "before the cross-encoder" or "after the cross-encoder", wherever the prose names it |

So flipping the default back restores all three automatically, and no
document can end up describing a configuration the code does not have.

## A guard, because the original defect was invisible

The defect survived every check that existed: the numbers were internally
consistent and the prose was true as written. `check_consistency.py` now
compares the shipped placement with the ablation's own F-versus-G
measurement and fails the build when the shipped placement is the one the
ablation ranks worse **on the focus domain** — the corpus the thesis is
about, and the one the deliverables quote. It reports the other corpora's
numbers alongside, because the industrial corpus's preference for the other
placement is a disclosed finding rather than a reason to ship the worse
default.

It was tested by temporarily flipping the configuration back: it fires with
the numbers and the remedy, and it is silent when the configuration is
right.

The first version of the guard fired only when the shipped placement was
worse on *every* corpus. That was wrong, and it was wrong in the direction
that matters: the industrial corpus prefers the post-rerank placement, so a
revert to `post_rerank` would have slipped through the guard even though it
gives up 6.3 points of Recall@10 on the thesis's own corpus. Firing on the
primary corpus catches it.

## The finding that changes the framing: the ranking is corpus-dependent

This is the part worth reading, and it was visible only in the archived
measurements. The numbers below are the ablation's own F-versus-G
comparison — system F applies the quota before the cross-encoder, system G
after it — on each corpus that measures it.

| Corpus | Pre-rerank Recall@10 | Post-rerank Recall@10 | Difference | Which is better | Paired Wilcoxon p |
|---|---|---|---|---|---|
| Focus domain (supply chain articles, n = 32) | **1.000** | 0.938 | +0.063 | **pre** | 0.157 |
| Six-category Wikipedia (n = 132) | 0.939 | 0.924 | +0.015 | **pre** | 0.480 |
| Industrial corpus (eCFR regulatory text, n = 247) | 0.980 | 0.988 | −0.008 | **post** | 0.317 |

No difference is statistically significant at the 0.05 level, on any corpus.
So the honest summary is:

> **The placement's effect is small on every corpus, and its direction is not
> uniform.** The rule the thesis states — "the quota belongs before the
> cross-encoder" — is supported on the focus domain and on the six-category
> corpus, and not settled on the industrial one, which prefers the opposite
> placement by 0.8 points.

The shipped default is the focus domain's preference, because that is the
domain the thesis is about and because it is the largest of the three
differences (6.3 points, against 1.5 and −0.8). The limitation (L20) says
exactly this, rather than the earlier claim that the ablation inverts the
rule, which was true of one corpus and not the other.

## What was re-measured

| Corpus | What |
|---|---|
| Six-category Wikipedia | ablation, gate, contradiction, transfer, pool sweep, long-context arm, the unanswerable-class audit |
| Focus domain (supply chain) | the same, plus **both** generator-side prompt conditions, the claim scorer's validation, the answer-side audit and the case study |
| Industrial corpus (eCFR) | the retrieval-side suite: ablation, gate, pool sweep, transfer |

### What was not, and why

Two results were **not** re-measured, and the limitation names them. A third
was carried over deliberately, and a fourth was checked rather than assumed:

| Result | Why |
|---|---|
| the focus corpus's per-claim band evaluations (`exp17`, `exp18`) | their labels come from a panel of reader agents under a written protocol; no script in the repository reproduces that panel |
| the industrial corpus's claim-band replication (`exp19`) | the same, on the industrial corpus |
| the long-context generator arm | placement-independent by construction — it does not retrieve — so its archived records are still the right ones, and re-running it would have reproduced them at a cost of 36 million tokens |
| the contradiction labels (`exp11`) | *checked*, not assumed: all 101 labelled pairs are present in the re-run with the same passages, and a build check now keeps it that way |

The first two are the ones that matter for honesty. They are not a script
that was not run; they are a *measurement instrument* that was not
reproduced. Running `run_claim_labeling.sh` today would produce labels from
`MiniMax-M3`, not from the reader panel, and the number would not be
comparable with the archived one. Disclosing them is the honest option, and
the disclosure is derived from the provenance stamps in the result files
rather than written by hand, so it cannot go stale.

### The focus suite does not re-run everything the deliverables quote

`rerun_focus.sh` covers the retrieval experiments and the generator arms, but
four results the deliverables quote are produced by scripts the suite does
not call: the query-form validator (`exp10`), the gate under each retriever
(`exp2b`), the generator-completion check (`exp13`) and the repaired
unanswerable class's audit (`exp12`). Each was re-run on the new placement,
and each of the four scripts now stamps the placement it ran under, so the
build can tell which measurements sit on the shipped configuration without
being told.

### The provenance list was incomplete, and the disclosure was wrong because of it

The disclosure is derived, not written by hand — but it is derived from
**the list** of results that sit on the retrieval, and the list was
incomplete. It covered the focus corpus and the industrial corpus and
nothing else, while the deliverables quote nine results from the
multi-category corpus too. Tracing every file the token build actually
reads found them:

| Multi-category result | Re-measured on the new placement? |
|---|---|
| the ablation (`exp1`) | yes — it was re-run and reproduced exactly |
| the contradiction detection (`exp3`) | yes, by the suite |
| the cross-category transfer (`exp4`) | yes, by the suite |
| the rerank pool sweep (`exp5`) | yes, by the suite |
| the long-context cost half (`exp7`) | yes, by the suite |
| the repaired unanswerable class audit (`exp12`) | yes, by the suite |
| the query-form probe (`exp9`) | **no** — never re-run |
| the query-form validator (`exp10`) | **no** — never re-run |
| the soft-prior result (`exp22`) | **no** — never re-run |

The last three are not in the suite script, so they were still measured
under the earlier placement. The first six were re-measured, but their
scripts did not write a stamp yet, so they would have been read as
unstamped — and an unstamped file is read as the earlier placement.

The net effect was that the derived disclosure would have said *every
measurement that depends on the retrieval was re-taken with it*, while
three of the nine had not been. The mechanism was working exactly as
designed and the answer was wrong, because **the completeness of the
mechanism is a property of the list, not of the mechanism**. A derived
claim is only as good as the set it is derived over.

So: the three were re-run (all three are CPU-only and take minutes), the
other six were stamped, and all nine were added to the list. The seven
scripts that produce them now stamp the placement themselves, so the next
re-measurement records it rather than needing to be told afterwards.

Two of them needed a word of care. The **ablation** was re-run at 06:41,
before the configuration's default changed at 06:47 — and it does not
matter, because the ablation measures the placement as a *variable*: it
runs the framework once with the quota before the reranker and once with it
after, passing the placement explicitly. Its file is therefore valid under
either default, which is exactly why it reproduced to the digit. The
**long-context cost half** is a measurement of the corpus-in-the-prompt
cost, with a retrieval-side proxy beside it; the proxy was re-run with
everything else.

### Which results actually depend on the placement

Completing the list also meant deciding it, and three results that had been
in it do not belong, and three that were missing do:

| Result | Depends on the placement? | How that was established |
|---|---|---|
| the contradiction detector (`exp3`) and the precision and control that sit on it (`exp11`, `exp11b`) | **No** | it retrieves with `apply_quota=False` — the quota is never applied, so the detector sees the same pairs under either placement |
| the unanswerable-class audit (`exp12`) | **No** | it never retrieves; its halves are the question-only policy and the class's own separability |
| the scorer validation (`exp8`) | **No** | it scores synthetic truths, fabrications and foreign passages |
| the focus corpus's ablation, long-context cost half and answer-side label audit | **Yes** | the first measures the placement, the second has a retrieval-side proxy, the third re-scores the generator's answers |
| the industrial corpus's ablation, gate and pool sweep | **Yes** | all three retrieve |
| the industrial corpus's retrieved-evidence claim-band evaluation (`exp21`) | **Yes** | the claims come from a generator sheet whose evidence was retrieved, so the claims, the judges' labels and the band all move with the placement |

The contradiction detector is the one worth dwelling on, because it looks
like it should depend and does not. Its re-run reproduced the archived
result field for field — the same 1,350 pairs compared, the same 20 alarms,
the same rates to sixteen digits — and the only field that moved was
`surfaced_findings`, which went from 0 to 20 because the calibration file
that decides whether an alarm is shown to the practitioner now exists. That
is a change in the *instrument*, not in the placement.

### The industrial claim-band evaluation, and how the chain was verified

`exp21_claim_band_eval_retrieved.json` feeds six quoted numbers into the
deliverables, so it could not simply be left on the earlier placement. Its
chain is six steps — the sheet (where the retrieval happens), the
generator's answers, the claims, the two judge sheets, four labelling runs
(two judges on two evidence modes) and two evaluations — and the archived
files were kept so a failed run could be undone.

The chain was verified before it was run, at no cost: re-scoring the
*archived* claims and labels reproduced the archived evaluation field for
field, with the single difference that the payload now carries a placement
stamp. That test settled the one flag the reconstruction could have got
wrong — the archived evaluation recomputes the framework's band over the
recorded candidates rather than using the generation run's own support
value, and the two give different band distributions (160 grounded claims
against 94). A reconstruction that had guessed the other flag would have
produced a *different measurement* rather than a re-measurement, and the
comparison is what caught it.

### A small qualification the industrial re-measurement turned up

The generator answered the industrial sheet's 247 questions with three
coming back **empty** — no text, no refusal. The archived run on the same
corpus had none. The claims therefore fall from 318 to 315, which is the
whole of the difference.

This contradicts nothing the deliverables say. The completion check
(Experiment 13) reports MiniMax-M3 at "0 of 66 of its requests came back
with no text", and that sentence is scoped to the focus corpus and its
66-question sample. But the industrial number qualifies it usefully:
**the shipped generator is not incapable of returning nothing, it is simply
rare** — three times in 247 on the industrial corpus, against none in 66 on
the focus corpus, and twenty-four times in 66 for the second generator. The
finding the deliverables make is that an empty completion is a third outcome
the harness has to handle; the industrial run shows the harness handling one
for the shipped model too, on a corpus the focus-domain measurement does not
cover.

### A path in a background chain is a thing to verify, not to trust

The chain's commands were written `../results_industrial/...`, because the
project's scripts are habitually run from `impl/` with paths relative to it.
But `..` from `impl/` resolves to the *project root*, not to `impl/`, so
every artefact went to `/Users/ritikraj/Documents/MTP/results_industrial/`
— a directory the project does not otherwise have. The chain was
self-consistent, so it would have run to completion, printed "wrote …", and
left the real `impl/results_industrial/` untouched and stale.

What caught it was checking the log against the file: the log said the
answers had been written, and the file's modification time said they had
not. The two expensive steps were correct and were moved into place, so the
chain resumed from step 3, and the archived originals survive in two
independent places.

### The second annotator changed, and the reason is measured

The industrial claim-band evaluation rests on two annotators: MiniMax-M3
(`judge_a_model`) and MiniMax-M2.7 (`judge_b_model`). On the re-measurement,
**MiniMax-M2.7 failed on 132 of the 315 claims** — "no parsable label
returned" — where the archived run had none.

The cause is not the rubric, the claims or the evidence. It is the labelling
budget. The labeller asks for 32 tokens; MiniMax-M2.7 spends 142–209 of them
on reasoning and returns no text at all, so `stop_reason` is `max_tokens`
and the parser finds no label. The same claims are labelled without
difficulty by MiniMax-M3, which does not reason before answering. Raising
the budget to 256 makes MiniMax-M2.7 label all three of the failed claims
tested, so the instrument works — it just needs room to think.

The second annotator was changed to **MiniMax-M3.1-Flash** instead. Two
things follow from that and both are worth stating plainly:

* The failure is a property of the model-and-budget combination, not of the
  placement. The archived run succeeded because those claims drew less
  reasoning; the new claims draw more, and the budget did not move.
* **MiniMax-M3 would have been the wrong choice**, even though it is the
  obvious one. It is already the first annotator, it answers without
  reasoning, and at temperature 0 the two annotators would return the same
  label for every claim — so the agreement between them would be 1 by
  construction and would measure nothing. The agreement statistic needs the
  two annotators to be different models.

MiniMax-M3.1-Flash reasons before answering, so it needs a budget that holds
its reasoning; at 4096 it labelled every claim tried. It is the project's
established second model — the one Experiment 13 measures the shipped
generator against — and the run is faster than MiniMax-M2.7 at a workable
budget, because the two modes were run in parallel.

**What this costs.** The archived industrial evaluation's inter-annotator
agreement was between MiniMax-M3 and MiniMax-M2.7; the new one is between
MiniMax-M3 and MiniMax-M3.1-Flash. The two kappa figures are therefore not
comparable with each other, and the change is a change of instrument, not a
re-measurement of the same instrument. The band evaluation's own numbers —
the band distribution, the positional comparison, the risk gaps — rest on
the claims and the reference labels, not on which model produced the second
annotator's labels, and those are the ones the deliverables quote most.

### The re-measurement broke a claim, and the claim is now derived

The industrial retrieved-evidence gap came back as **+0.0000** against the
archived +0.0315. That is not a rounding artefact: the paired test over the
answers that contain a wrong claim found no discordant pair at all, so the
risk gap is exactly zero and the effect size is exactly 0. The other three
gaps are unchanged or still positive (+0.0923 focus gold, +0.0231 focus
retrieved, +0.0152 industrial gold).

So the deliverables' sentence — "the direction replicates even where the
significance does not: the risk ... is higher in all four" — was **no longer
true**, and the build had substituted the +0.0000 into the very paragraph
that called the direction uniform. The build's checks did not catch it: they
check that the numbers in the prose are the numbers in the files, and they
were. What was wrong was the claim the numbers no longer support.

The fix is the same discipline as the rest of this work: **the direction is
now derived from the four gaps rather than asserted.** `substitute_tokens.py`
computes how many of the four are strictly positive, how many tie and how
many reverse, and renders the sentence from that. The prose now reads "the
direction replicates in three of the four and ties in one ... is higher in
three of the four (+0.0923, +0.0231, +0.0152 and +0.0000 at matched
coverage)". The next-steps item follows the same token, and so do the
thesis report and the plain-language guide's register entry.

**Two things this changed that are worth knowing about.**

* **The next-steps item's wording came from the data, not from me.** "Settle
  the positional comparison's magnitude and power. The direction is uniform.
  The magnitude is not." became "The direction is not uniform. The
  magnitude is not." The short form had never been format-mapped, so the
  moment it carried a placeholder the build shipped it literally — and the
  build's own token check caught that. Both the short and the long forms
  are mapped now.
* **The claim that survived is the one the numbers still support.** Only one
  of the four clears significance (focus gold, p = 0.008), and that is
  unchanged. What the re-measurement did is turn the *direction* claim from
  universal to "three of the four, with an exact tie in the fourth" — which
  is a weaker claim than the thesis used to make, and is now made because
  the measurement says so rather than because the prose said so.


### The contradiction labels still apply, and that is now checked

The contradiction experiment was re-run, so the blind labels on its flagged
pairs and their controls are carried over from the earlier run. Carrying
labels over is only legitimate if the pairs are the same pairs, and it
turned out that they are: the flagged set is the same 20 pairs, the
passages are byte-identical, and all 101 labelled pairs — the 20 alarms and
the 81 unflagged controls — are present in the re-run with the same text.

That was not assumed. `check_consistency.py` now reads the pairs the run
actually produced and confirms that every labelled pair is still there with
the same passages, and fails the build if one is not. The check was tested
by perturbing a single passage: it fires and names the pair.

The labels themselves are model-produced (`judge_a_model` on `MiniMax-M3`,
`judge_b_frontier` on `claude-opus-5-5`, both with their raw responses
recorded), so unlike the claim-band labels they are a scripted measurement
that could be re-run. They did not need to be: the pairs they describe did
not change.

### The ablation reproduced exactly, and that is the useful part

Re-running the ablation on both Wikipedia corpora reproduced **every rung of
every system, to the digit** — the same recalls, the same MRRs, the same
nDCG, the same benchmark counts, the same corpus statistics. That is not a
null result; it is the reason the re-measurement is trustworthy.

The ablation measures the two placements *as a variable*, so the shipped
default does not enter it, and it had to come out the same. That it did
means the two corpora's benchmarks were regenerated identically, the seeds
matched, and the numbers the limitation rests on are the same numbers as
before the move. So the comparison is like-for-like, and the corpus-
dependence below is a property of the measurement rather than an artefact of
the change.

What did move is everything that runs through the *shipped* retrieval. On
the focus domain the gate's chosen operating point did not move at all — the
same threshold, the same 93.75% of answerable queries answered, the same
abstention precision to within 0.1 points — while the calibration did, in
both directions: ECE 0.114 → 0.104 (better) and Brier 0.144 → 0.151
(slightly worse). One query in the corpus-anchored table class flipped from
answered to refused. That is the size of the change the placement makes to
the shipped system's behaviour.

## The eCFR corpus's own generator-side experiments

**The eCFR corpus carries two generator-side experiments of its own, and only
one of them depends on the placement.** The distinction was established by
reading what each one actually consumes:

| Experiment | What it consumes | Depends on the placement? |
|---|---|---|
| `exp21` — the annotation-rubric factorial | `exp14_pairs_annotated.json`, 240 pairs a regulatory specialist labelled, plus fixed reader labels | **No.** Its own design records what is held constant: "the 240 pairs, the detector and its configuration, the regime assignment, the regime briefs, the reader model". `run_revision_eval.py` takes `--pairs` and `--labels` as inputs and never retrieves. |
| `exp19` — the per-claim band against generator answers | a generator sheet built by `prepare_generator_sheet.py`, which calls `_retrieve` → `Framework.retrieve` with no quota position, so it resolves the configuration's placement | **Yes.** The sheet's evidence differs, so the claims differ, so the band evaluation differs. |

So the earlier note that "both" eCFR experiments would have to be re-run was
wrong on one of the two, and the "about three hours of paid API calls" figure
with it. `exp21` needs nothing; it is a factorial over fixed annotated pairs.

`exp19` would need re-measuring, and it must follow the industrial suite,
because the `Framework` loads `artifacts_industrial/gate_model.json` and the
generator arm reads the fitted threshold from it — the suite refits that model
on the new placement. Its chain is scripted end to end: the sheet (60 items),
60 generator calls, the claims, the two judge sheets, the specialist labels,
and the band evaluation.

**The last step is the one that cannot be reproduced, and for the same reason
as the focus corpus's.** The archived labels record `"model": "none
(reader)"` and carry no `raw_responses`, and the string `none (reader)`
appears nowhere in the source tree — so the labelling was done by reader
agents under a written protocol, and no script in the repository reproduces
it. Re-labelling with today's script would record `MiniMax-M3` where the
archive records the reader, and the new number would not be comparable with
the archived one, which is the opposite of what a re-measurement is for.

So `exp19` is disclosed rather than re-run, and the limitation says so by
name.

## The generator-side comparison, and what it took to re-measure it

The focus corpus's generator-side comparison is five arms over one question
set. Four of them retrieve — `rag_nogate`, `rag@fitted`, `rag@random`,
`rag@transferred` — so the quota placement decides which passages the
generator was shown, and they have to be re-measured. The fifth does not:

> `run_arm` gives the `long_context` arm `context = corpus` and
> `evidence_ids = list(index.chunk_ids)`, and `build_long_context` renders the
> corpus by walking `index.chunk_ids`. It never touches the retriever, the
> reranker or the quota. **Its prompt is byte-identical under either
> placement.**

So the long-context arm is placement-independent by construction, and its
archived records are still the right ones. Re-running it would have spent
36 million tokens reproducing them — and it is what exhausted the provider's
token plan the first time the suite was run, because the corpus prefix is
re-sent with every one of the 176 requests.

That made the re-measurement affordable. `MTP_GEN_ARMS` narrows the arm list
and `--tag` writes to a separate file, so the four retrieving arms were
re-run to `exp8_generation_rerun.json` and promoted by
`deliverables/scripts/promote_generator_arms.py`, which carries the
long-context arm over from the archive and records the provenance of both.
The promotion refuses a partial re-measurement: if the file does not hold
exactly the four retrieving arms, it refuses to promote it.

### What the re-measurement found

The cautious condition was re-measured on the new placement and the numbers
moved. They moved because the *prompt* moved: the placement changes which
ten passages the generator is shown, and on the focus corpus it changes them
for almost every query.

| Arm | Unanswerable answered, before → after | Prompts that changed |
|---|---|---|
| `rag_nogate` (no gate) | 0.549 → 0.535 | 174 of 175 |
| `rag@fitted` (the gate) | 0.451 → **0.417** | 74 of 175 |
| `rag@random` (control) | 0.396 → 0.375 | 82 of 175 |
| `rag@transferred` | 0.042 → 0.014 | 13 of 175 |
| `long_context` | unchanged, by construction | 0 of 176 |

"Prompts that changed" counts the queries whose prompt was sent with a
different length under the two placements, pairing the two result files by
query. It is not the same as "the retrieval changed": the gated arms refuse
some questions outright, so fewer of their prompts are ever sent.

That is the effect the ablation predicted, showing up in the deployed
system's behaviour rather than only in a retrieval metric: with the quota
before the cross-encoder, the fitted gate **answers fewer of the
unanswerable questions** — 0.417 of them against 0.451 — and the paired
test against the ungated arm strengthens, p = 0.0023 against p = 0.0094.
The count behind that number is the clearest statement of it: the gate
refused **23** of the unanswerable questions that the ungated arm answered,
against **20** before the move.

The ungated arm also answers fewer of the *answerable* questions
(0.969 → 0.938). That is the other side of the same change: the placement
decides which ten passages the generator is shown, and the generator is
shown a different ten.

### The answering condition moved the other way, and that is the point

The comparison is reported under both prompt conditions, and the
answering condition — the one that tells the generator to answer rather than
to decline — was re-measured too. It moved differently:

| Arm | Unanswerable answered, before → after | Prompts that changed |
|---|---|---|
| `rag_nogate` (no gate) | 0.889 → **0.938** | 174 of 175 |
| `rag@fitted` (the gate) | 0.597 → **0.528** | 119 of 175 |
| `rag@random` (control) | 0.660 → 0.604 | 95 of 175 |
| `rag@transferred` | 0.042 → 0.021 | 15 of 175 |
| `long_context` | unchanged, by construction | 0 of 176 |

The ungated arm got *worse* — it answers more of the unanswerable
questions — while every gated arm got *better*, answering fewer. The
gate's paired margin over the ungated arm therefore widened, from 47
refusals to 60, and the test strengthened from p = 1.3 × 10⁻⁹ to
p = 5.4 × 10⁻¹⁷.

That asymmetry is the honest shape of the result, and it needs the caveat
that goes with it: under the answering condition, part of the gate's
improvement is that the arm it is measured against got worse, not only that
the gate got better. Under the **cautious** condition — the shipped one —
both moved the same way: the ungated arm answered fewer of the unanswerable
questions (0.549 → 0.535) and the gated arm answered fewer still (0.451 →
0.417), so the gate's improvement there is on its own footing rather than
against a deteriorating baseline. The same holds for the random control,
which is the point of having one: its refusal rate is fixed by
construction, so the change in the fitted arm cannot be an artefact of the
question set moving.

The paired refusal counts, both conditions:

| Arm vs. `rag_nogate` | Cautious, before → after | Answering, before → after |
|---|---|---|
| `rag@fitted` | 20 → **23** (p = 0.0094 → 0.0023) | 47 → **60** (p = 1.3e-09 → 5.4e-17) |
| `rag@random` | 30 → 30 (p = 0.00047 → 0.00019) | 37 → **50** (p = 1.0e-07 → 6.1e-13) |
| `rag@transferred` | 73 → **75** (p = 2.1e-22 → 5.3e-23) | 122 → **132** (p = 3.8e-37 → 3.7e-40) |

### One question is not the same question in the two runs

The archived results and the re-measurement do not share their entire
question set. The benchmark was rewritten during this work cycle — the
unanswerable class was repaired and the file was regenerated at 06:16 on
16 November — and one question was replaced:

- archived: `What are information in traditional bar codes?`
- current: `What is annual updating of data and formulae?`

The two runs therefore pair over **175** questions, not 176. The replaced
question is unanswerable under both versions, and the comparison above was
recomputed over the 175 shared questions alone: the rates agree with the
176-question figures to three decimal places (for instance the fitted
gate's 0.4476 → 0.4126 against 0.4514 → 0.4167), so the conclusion does not
rest on the swapped question. The `long_context` arm, which was carried
over from the archive rather than re-run, is the one place where the
difference is visible: its 176 questions are the archived set, because
those are the questions it was measured on.

### The rebuilt benchmark also moved the questions, and the pairing had to follow

The same rebuild **reordered** the benchmark. The archived and the current
question sets differ by one question, but their *orders* differ in 23 of the
176 positions — the benchmark is regenerated rather than edited in place.

That mattered because the paired test paired the arms **by position**. The
assumption behind it was explicit in the code:

> Every arm is run over the same questions in the same order and every
> question yields exactly one record, so the records pair by position.

That assumption held for the four arms that were re-measured together, and
it still holds for them. It did not hold for the `long_context` arm, which
is carried over from the archive and therefore carries the *archived*
order. Position-pairing it against the re-measured `rag_nogate` compared 23
questions against the wrong counterparts. The counts looked plausible —
144 pairs rather than the 143 the shared questions actually support — and
nothing else in the build would have noticed.

The pairing is now by **query**, and the count of unpaired questions is
recorded in the payload so that a mismatch is visible rather than silent.
The corrected long-context blocks are 143 pairs (17/16 discordant under the
cautious condition, 7/6 under the answering condition). The four
re-measured arms are unaffected — 14 of the 16 paired blocks are identical
before and after the change, which is the check that the fix is a fix and
not a rewrite.

`deliverables/scripts/check_consistency.py` now recomputes every paired
block by query and compares it with what the file reports, so this class of
error fails the build rather than reaching a table. The deliverables quote
the *rates* for the long-context arm and the *paired* blocks for
`rag@fitted` and `rag@random`, so no number the deliverables carry changes:
the wrong blocks were the long-context ones, and the two blocks the
deliverables do quote were verified correct.

Two smaller defects turned up in the same pass and were fixed at the
source, because both were the same mistake in different clothes — using a
name before the import that binds it:

- `run_gate_per_retriever.py` imported `src.config` before `common`, and
  `common` is what puts `impl/` on the path, so the import failed outright.
- `run_gate.py` used `CONFIG` above a function-local `from src.config
  import ...`, which makes the name local to the whole function and so
  raises `UnboundLocalError` at the point of use.

Both were caught by the suite rather than by inspection, and both are now
gone.



Every result that is computed over retrieved passages now records the
placement it was measured on. `run_generation_eval.py` and
`run_claim_band_eval.py` write `retrieval_placement` into the file they
produce, and `deliverables/scripts/stamp_measurement_provenance.py` stamps
the files that were restored from the archive with the placement they were
taken under.

`substitute_tokens.py` reads those stamps and derives, rather than asserts,
which generator-side results sit on the shipped configuration. The L20 row
names the ones that do not. So the limitation cannot claim that the
generator-side comparison was re-taken when it was not — the claim is
re-derived from the files on every build.

### The claim-band labels are a reader panel, not a script

The focus corpus's per-claim band evaluations (`exp17`, `exp18`) and the
industrial replication (`exp19`) are built on labels from a **panel of
reader agents** under a written protocol: a generalist reader, a
domain-specialist reader, an adjudicator over the contested claims, and a
second reader on the other protocol. Their label files record
`"model": "none (reader)"` and carry no `raw_responses`, and the string
`none (reader)` appears nowhere in the source tree — so the labelling was
done by reader agents, and no script in the repository reproduces it.

That is a different kind of thing from a re-runnable experiment. Running
`run_claim_labeling.sh` today would produce labels from
`MiniMax-M3`, not from the reader panel, and the resulting number would not
be comparable with the archived one: the measurement instrument would have
changed, not just the retrieval. **Those three measurements are therefore
disclosed rather than re-run**, and the limitation says so by name. The
pre-change results are archived in `.snapshot_preswap/` at the project root,
and

```
python3 deliverables/scripts/revert_quota_placement.py
```

puts the whole change back in one command — the measurements *and* the
shipped configuration together, because restoring only the measurements would
leave the code shipping one placement while the results describe the other,
and no check would notice.

## Why it was not simply left alone

Two reasons, and the second is the important one.

The first is that the disagreement between the shipped configuration and the
thesis's own recommendation was a genuine discovery: the ablation had been
measuring the two placements all along, and the code had been using the worse
one. Leaving that in place two days before the defence meant hoping no
committee member read the pipeline.

The second is that "the shipped configuration is not the one the thesis
recommends" was a limitation (L20) rather than a fact, and a limitation of
that kind is a standing invitation to a reviewer to go looking. Making the
placement a configuration value and putting a guard on it turns a disclosure
into an invariant.

The cost of doing it now, two days out, was that a full re-measurement of
three corpora plus two paid generator-side experiments had to fit into the
time. That is a cost the *timing* note in the task recognised, and it is why
the snapshot was taken before anything else.
