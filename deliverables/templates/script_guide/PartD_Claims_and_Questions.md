# Part D. The numbers, the traps and the questions

## D.1 The numbers to say exactly

Ten numbers, and what happens if one of them is wrong.

| Number | What it is | Slide | If you get it wrong |
|---|---|---|---|
| {{UNANS_HARD_REFUSED_PCT}} | the gate's refusal rate on the hard stratum, after the repair | 14 | this is the headline, and the one a reader will check against the report |
| {{UNANS_HARD_REFUSED_N}} and {{UNANS_OOD_REFUSED_N}} | the two strata the rate is made of | 14 | the rate without the strata is a rate on nothing in particular |
| {{UNANS_BEFORE_AUC}} against {{UNANS_SEP_AUC}} | the shortcut's separability, before and after the repair | 14 | these two are the proof that the benchmark had to be repaired |
| {{ABSTENTION_PRECISION}} | abstention precision at the fitted operating point | 13 | this is the number the precision claim rests on |
| {{FOCUS_GATE_TAU}} | the fitted threshold on the focus domain | 5, 13 | every number on slide 13 is conditional on it |
| two against eleven | refusals spent on answerable questions, the gate against the random control | 17 | this pair is the difference between a gate and a coin flip |
| {{GEN_A_FITTED_UNANS_ANSWER_RATE}} against {{GEN_A_RANDOM_UNANS_ANSWER_RATE}} against {{GEN_A_NOGATE_UNANS_ANSWER_RATE}} | answer rates on the unanswerable class: gate, control, ungated | 17 | the control is worse than the gate here, and that is the point |
| {{CONTRA_PRECISION_PCT}} on {{CONTRA_PRECISION_N}} alarms | the contradiction gate's precision against reader labels | 19 | this is a measured zero, and saying it is unmeasured is a mistake |
| {{GEN_LC_TOKEN_RATIO}} and {{GEN_LC_COST_RATIO}} | the long-context arm's token and cost penalty | 18 | the two are different numbers, and only the second is a cost |
| {{GATE_ECE}} and {{GATE_BRIER}} | the focus gate's calibration | 12 | these are reported, not improved, and the slide says so |

## D.2 The five mistakes the talk is built to avoid

**Saying the gate lowers the answer rate on unanswerable questions.** It does
not. The random control answers that class at
{{GEN_A_RANDOM_UNANS_ANSWER_RATE}} against the gate's
{{GEN_A_FITTED_UNANS_ANSWER_RATE}}. The claim is about where refusals land,
and the control is what makes it visible.

**Pairing the two classifiers in the slide 14 table.** The shape separability
row is the one the figure plots, {{UNANS_BEFORE_AUC}} against
{{UNANS_SEP_AUC}}. The question-only policy row is a separate rule-based
detector, {{UNANS_POLICY_BEFORE_AUC}} against {{UNANS_POLICY_AUC}}. Reading one
row's before-value against the other row's after-value produces a sentence
that is true of neither.

**Reading the accuracy columns on slide 17 as a quality gain.** The gated arm
answers an easier subset, because a gate declines the hardest questions. That
is a selection effect, and it is why per-answer accuracy cannot be compared
across arms with different coverage.

**Calling the contradiction gate's precision unmeasured.** It was measured, by
two independent annotators who read the sheet blind to the detector's scores,
and it is zero. Reporting it as unproven rather than as a null is the
mistake; it is a measured null with a {{CONTRA_PRECISION_CI_HI}} upper bound.

**Claiming that a calibrated threshold transfers.** It does not. The
transferred arm, fitted on one half of the cross-category corpus and applied
unchanged to the other half, answers {{GEN_A_XFER_ANS_ANSWERED}} of the
answerable questions against the fitted gate's
{{GEN_A_FITTED_ANS_ANSWERED}}, and {{GEN_A_XFER_UNANS_ANSWERED}} of the
unanswerable ones.

## D.3 The questions to expect

**"Why is the refusal rate only {{UNANS_HARD_REFUSED_PCT}}? That sounds low for
a gate."**
:   The answer rests on the class the rate is measured on, and on the repair.
    The rate is on the hard stratum, where the corpus discusses the subject
    but does not state the answer. On the out-of-domain stratum, where the
    question comes from outside the corpus entirely, the gate refuses
    {{UNANS_OOD_REFUSED_N}}. Before the repair the rate was
    {{UNANS_BEFORE_REFUSED_PCT}}, and that number was measuring a shortcut in
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
    answers {{GEN_A_FITTED_ANS_ANSWERED}} where the ungated arm answers
    {{GEN_A_NOGATE_ANS_ANSWERED}}, and it removes 59 wrong answers for the
    cost of one correct answer under the entailment test.
    *Follow-up:* "is that trade worth it?" Whether it is worth making is a
    domain judgement, and these measurements do not settle it. Say that.

**"The contradiction gate did not work. Why keep it?"**
:   Because the corpus does not contain the phenomenon it detects. The readers
    found no contradictions in a random sample of {{CONTRA_UNFLAGGED_SAMPLE}}
    pairs the gate did not flag either, so this is a statement about the
    corpus and not about the detector.
    *Follow-up:* "then delete it?" It is reported as a null rather than
    dropped, because the two defects the audit exposed were real and were
    fixed, and the corpus the framework would meet may contain the
    phenomenon.

**"How do you know the framework is better than just BM25?"**
:   On the focus corpus it is not, on recall. The dense leg is significantly
    worse than BM25, fusion recovers it to 1.000, and the reranker moves MRR
    by {{RERANK_MRR_PP}} points, which is not significant. On the six-category
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
    the two classes at ROC AUC {{UNANS_BEFORE_AUC}}.
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
