# Part 8. The machinery and the experiment

### Pipeline

**Plain.** The fixed order in which the work is done.

**Technical.** A sequence of processing stages in which each stage consumes
the output of the previous one. A pipeline is a control-flow decision: the
only way to reach a later stage is through the earlier ones.

**Here.** Five stages, and stage 3 is the gate. It is a pipeline in the
strong sense, not a set of components that can be rearranged.

### Stage

**Plain.** One step of the pipeline.

**Technical.** A unit of processing in a pipeline with a defined input, a
defined output and a defined place in the control flow.

**Here.** Stage 0 validates the query form and stage 3 is the confidence
gate. Those two are the stages that may refuse, and the table on slide 6
marks them.

### Arm

**Plain.** One version of the system being compared against the others.

**Technical.** A configuration of the system under test, differing from the
others in one controlled respect, and evaluated on the same questions.

**Here.** Five arms on slide 17: the ungated arm, the fitted gate, the random
control, the transferred threshold and the long-context arm.

### Ablation

**Plain.** Taking the system apart a piece at a time to see what each piece
was doing.

**Technical.** A controlled comparison in which one component is added or
removed at a time while everything else is held fixed, so that the effect of
that component is isolated.

**Here.** The seven retrieval configurations on slide 12 are an ablation, in
the order the components were added.

### Baseline

**Plain.** The thing you are compared against.

**Technical.** A reference configuration providing the reference point for a
comparison, either the simplest working configuration or the state of the
art against which a method is claimed to improve.

**Here.** The baseline is BM25 alone: Recall@10 {{R_A}}, the strongest of the
seven configurations on the focus corpus, and the reason the retrieval claim
is narrow.

### Control

**Plain.** A comparison built to make sure the effect you found came from the
thing you changed and not from something else.

**Technical.** A configuration that differs from the treatment in a way known
not to carry the mechanism under test, so that a difference between them
isolates the mechanism.

**Here.** The random-escalation control refuses at random with the same
frequency. It answers unanswerable questions at {{GEN_A_RANDOM_UNANS_ANSWER_RATE}}
against the fitted gate's {{GEN_A_FITTED_UNANS_ANSWER_RATE}}, and it refuses
{{GEN_PAIRED_RANDOM_ANS_B}} answerable questions against the gate's
{{GEN_PAIRED_FITTED_ANS_B}}. That comparison is the whole result.

### Evaluation arm

**Plain.** The version of the system whose numbers you report.

**Technical.** The configuration whose performance is the measurement of
interest, as opposed to configurations used as comparators.

**Here.** The fitted arm, at the threshold the stated rule selects.

### Non-bypassable

**Plain.** The system cannot answer without going through the check.

**Technical.** A property of the control flow in which the guarded component
is on every path to the output, so that no configuration of the inputs can
reach the output without passing the guard.

**Here.** The generator is called at exactly one line, after the gate has
accepted, so a refused query costs no model call at all. The only two paths
that skip the gate are the comparison arms, and both are reported as
separate results.

### Held-out half

**Plain.** The half of the questions kept back and not looked at while the
system was being built.

**Technical.** The evaluation partition, excluded from model fitting and from
threshold selection, used once at the end.

**Here.** The gate is fitted on 60 percent of the queries, and the threshold
sweep reported on slide 15 is on the remaining 40 percent.

### Calibration split

**Plain.** The part of the data used to turn the system's score into an
honest probability.

**Technical.** The partition on which the calibration mapping is estimated,
kept separate from the evaluation partition so that the calibration error
reported is out of sample.

**Here.** The calibration split's mean and deviation standardise the feature
vector, which is why the table on slide 7 names them.

### Seed

**Plain.** The number that makes a run repeatable.

**Technical.** The initial value of the random number generator, fixing the
random draws so that a run can be reproduced exactly.

**Here.** Every archived result file records the seed it was run with, which
is one of the things that makes the results checkable rather than merely
reported.

### Archived result file

**Plain.** The saved output of a run, kept so that anyone can check the
numbers later.

**Technical.** The persisted JSON of an experiment, holding the configuration,
the seed, the per-query records and the computed statistics, sufficient to
recompute every number reported without re-running the experiment.

**Here.** Every figure in the deck comes from one of these. That is the
sentence to say if a panel asks whether the numbers can be checked.

### Reproducibility

**Plain.** Being able to get the same numbers again.

**Technical.** The property that a result can be regenerated from a stated
configuration, code and seed, and that the regenerated result agrees with the
archived one.

**Here.** The build regenerates every deliverable from the archived result
files, and the checkers read the numbers back off the built artefacts, so a
drift between a report and a slide stops the build rather than reaching a
PDF.

### Instrument

**Plain.** The thing that does the measuring. It can be wrong.

**Technical.** Any device, procedure or model whose output is treated as a
measurement. The methodological point is that an instrument has to be audited
before its readings are trusted, exactly as a gauge has to be calibrated
before it is read.

**Here.** The two instruments that failed were the benchmark's own labelling
procedure and the contradiction annotation, and finding that out is what
changed the headline from {{UNANS_BEFORE_REFUSED_PCT}} to
{{UNANS_HARD_REFUSED_PCT}}.

### Claim annotation

**Plain.** Marking every sentence of the answer with what supports it.

**Technical.** The process of extracting the claims of a generated answer and
assigning each a support status, a confidence band and a citation.

**Here.** The per-claim band and the claim scorer's error profile are the
fifth mechanism and finding F13, which says that most unattributed error
comes from the evidence given rather than from the logic:
{{RO5_RETRIEVED_GROUNDED_ERROR}} against {{RO5_GOLD_GROUNDED_ERROR}}.

### Empty completion

**Plain.** The model returned nothing at all.

**Technical.** A generation that terminates without producing any text,
which is distinct from a refusal: a refusal is a decision, and an empty
completion is the absence of one.

**Here.** The second generator returned an empty completion on
{{GENCOMP_FAILING_EMPTY_N}} of the {{GENCOMP_FAILING_EMPTY_TOTAL}} questions,
which is why the replication could not be run. It is finding F14, and it is
the reason an empty completion is counted as a third outcome rather than
folded into refusal.
