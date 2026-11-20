# Part D. The numbers, the traps and the questions

## D.1 The numbers to say exactly

These are the load-bearing numbers. If one of them is misremembered, the
claim it carries does not hold, and the numbers are the part the audience
writes down.

| Number | What it is | Where it comes from |
|---|---|---|
| {{R_A}} and {{R_B}} | Recall@10 for BM25 alone and for the dense leg alone | the focus ablation, 32 queries, paired |
| 0.025 and 0.014 | the p values for BM25 against dense, and for fusion against dense | the same archived comparison |
| {{R_C}} | Recall@10 for fusion by reciprocal rank fusion | the focus ablation |
| {{RERANK_MRR_PP}} pp and {{MC_MRR_RERANK_PP}} pp | what the reranker moves MRR on the focus and the six-category corpora | two separate corpora, two separate runs |
| 0.157, 0.480 and 0.317 | the p values for the quota placement on three corpora | three corpora, each from its own ablation |
| {{FOCUS_GATE_TAU}} | the gate's threshold | the rule: the highest that still answers 90 percent of the answerable questions |
| {{FOCUS_GATE_COVERAGE}} and {{FOCUS_GATE_ABST_PRECISION}} | coverage and abstention precision at that threshold | the threshold sweep |
| {{GATE_ECE}} | the calibration error of the confidence score | reported, not improved by refitting |
| {{UNANS_POLICY_AUC}} and {{UNANS_MC_SEP_AUC}} | the question-only classifier's ROC AUC on the focus and six-category corpora | the benchmark audit |
| {{UNANS_HARD_REFUSED_PCT}} | the gate's refusal rate on the repaired hard stratum | the repaired unanswerable class |
| {{UNANS_BEFORE_REFUSED_PCT}} | the refusal rate the defective class suggested | the shortcut audit, reported as the upper bound it was |
| {{GEN_A_NOGATE_UNANS_ANSWER_RATE}} to {{GEN_A_FITTED_UNANS_ANSWER_RATE}} | the rate of answering unanswerable questions, ungated then gated, under the answering prompt | the generation experiment, paired McNemar |
| 0.535 to 0.417 | the same, under the cautious prompt | the second condition, p = {{GEN_PAIRED_CAUTIOUS_UNANS_P}} |
| {{GEN_PAIRED_FITTED_ANS_B}} against {{GEN_PAIRED_RANDOM_ANS_B}} | answerable questions refused by the fitted gate and by the random control | the precision claim, and the only place the score shows up |
| {{TRADE_ANSWERING_WRONG_REMOVED}} and {{TRADE_ANSWERING_CORRECT_COST_NLI}} | wrong answers removed and correct answers lost, counted from the records | the trade at the operating point |
| {{GEN_LC_TOKEN_RATIO}} and {{GEN_LC_COST_RATIO}} | the token ratio and the cost ratio against long context | the long-context run, with cached-prefix pricing |
| 0.406 against 0.667 | per-answer accuracy for long context and for the gated pipeline | the same run |
| {{CONTRA_PRECISION_PCT}} and {{CONTRA_PRECISION_CI_HI}} | the contradiction detector's precision and its 95 percent upper bound | against reader labels, not the detector's own threshold |
| {{CONTRA_PRECISION_AGREE_N}} of {{CONTRA_PRECISION_AGREE_N}} | the annotator agreement on the contradiction decisions | two annotators that do not share a model |
| {{GENCOMP_FAILING_EMPTY_N}} of {{GENCOMP_FAILING_EMPTY_TOTAL}} | the questions on which the second generator returned no text | the reason the replication could not be run |

## D.2 The mistakes the talk is built to avoid

Each of these is true, and each misleads. They are the traps from Part C,
collected in one place.

**"The gate answers fewer unanswerable questions."** True. Misleading, because
the random control answers fewer still, at {{GEN_A_RANDOM_UNANS_ANSWER_RATE}}
against the fitted gate's {{GEN_A_FITTED_UNANS_ANSWER_RATE}}. The gate's
contribution is precision of refusal, not a lower answer rate.

**"Fusion improves retrieval."** The dense leg is significantly worse than
BM25 here, and fusion recovers it to {{R_C}}, but fusion is not a significant
win over BM25 on its own. Say "fusion stopped being a loss".

**"The reranker improves ranking."** It does on the six-category corpus, by
{{MC_MRR_RERANK_PP}} points of MRR. On the focus corpus it moves MRR by
{{RERANK_MRR_PP}} points. The sentence is never used without its corpus
attached.

**"The gate rejects malformed questions."** It does not. It accepts
{{FORM_PROBE_RATE}} of malformed stems. It is an evidence gate, not a form
gate, and a separate validator does the form check.

**"The contradiction detector does not work."** Unproven, not disproven. The
precision is {{CONTRA_PRECISION_PCT}} against reader labels with a 95 percent
upper bound of {{CONTRA_PRECISION_CI_HI}}, on a corpus that may simply not
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
{{GEN_PAIRED_FITTED_ANS_B}} answerable questions where the random control
refuses {{GEN_PAIRED_RANDOM_ANS_B}}, and it removes
{{TRADE_ANSWERING_WRONG_REMOVED}} wrong answers at a cost of
{{TRADE_ANSWERING_CORRECT_COST_NLI}} correct answer. That is a precision
claim, and it is the one the paired test supports.

**"If the mechanism is prior art, why is this a master's project rather than
an engineering report?"**
Because the engineering report would have been a sentence with no number
attached. The work is in finding that two of the project's own instruments
reported numbers a careful reader could not trust, rebuilding the benchmark
class that was causing it, and changing the headline from
{{UNANS_BEFORE_REFUSED_PCT}} to {{UNANS_HARD_REFUSED_PCT}}. And in
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
{{GATE_ECE}}, reported rather than improved by refitting, which is the point:
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
{{LAT_N_QUERIES}} focus-corpus queries. The retrieval path is
{{LAT_TOTAL_MEAN_MS}} milliseconds on average, {{LAT_TOTAL_MEDIAN_MS}} at the
median and {{LAT_TOTAL_P95_MS}} at the 95th percentile. The cross-encoder
rerank is {{LAT_RERANK_MS}} of those milliseconds, which is almost all of the
framework's own work; the query embedding is {{LAT_EMBED_MS}}, the dense leg
{{LAT_DENSE_MS}}, the lexical leg {{LAT_BM25_MS}}, and the rank fusion, the
modality quota and the gate together come to under a millisecond.

**"And when the gate refuses to answer?"**
A refusal is not a faster answer. The gate's decision is taken at the end of
the retrieval path, so a refused query costs the same {{LAT_RETRIEVAL_S}}
seconds of retrieval and then stops: the model is never called and no answer
is generated. On the focus benchmark the gate refused {{LAT_GATE_REFUSED_N}} of
the {{LAT_N_QUERIES}} queries, and the latency run reproduces the archived
run's refusals exactly, which is the check that the timing was measured on the
same system as the results.

**"And when it does answer?"**
The generation dominates, and it is not the framework's cost. From the
archived arm totals, the model call together with the offline claim-scoring
pass costs between {{GEN_S_PER_ANSWER_MIN}} and {{GEN_S_PER_ANSWER_MAX}}
seconds per answered query, depending on the arm and the prompt condition. The
framework's own share is {{LAT_RETRIEVAL_S}} seconds: under three percent of an
answered query, and the whole of a refused one. The long-context arm, which
sends the whole corpus in the prompt and does no retrieval at all, costs
{{LAT_LONGCTX_S_PER_Q_CAUTIOUS}} to {{LAT_LONGCTX_S_PER_Q_ANSWERING}} seconds per
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
0.156 in Recall@10, Cohen's d of {{ABL_DZ_AB}} and Cliff's delta of
{{ABL_CD_AB}}. Cliff's delta of {{ABL_CD_AB}} is a small effect, which is why
the sentence about fusion is narrow and the sentence about the dense leg is
not: the dense leg is reliably worse, and it is not much worse.

**"You have several null results. Is this underpowered?"**
Yes, and that is stated as a limitation. The quota-placement and
fusion-over-BM25 comparisons are nulls at this sample size and are read as
"no difference established here", never as evidence of no difference.

**"What is the effect size for the headline result?"**
The headline is a proportion change from {{GEN_A_NOGATE_UNANS_ANSWER_RATE}}
to {{GEN_A_FITTED_UNANS_ANSWER_RATE}} on the unanswerable class, with a
paired exact McNemar test at p {{GEN_PAIRED_FITTED_UNANS_P}}, and it
replicates under the second prompt condition at p =
{{GEN_PAIRED_CAUTIOUS_UNANS_P}} with a smaller effect. The precision claim on
the answerable class has b = {{GEN_PAIRED_FITTED_ANS_B}} against b =
{{GEN_PAIRED_RANDOM_ANS_B}}.

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
{{UNANS_MATCH_RATE}} structural certificates pass. And the check that matters
is the question-only classifier, which sees the question text and nothing
else. Its ROC AUC is {{UNANS_POLICY_AUC}} on the focus corpus and
{{UNANS_MC_SEP_AUC}} on the six-category one. If the class were identifiable
from its shape, those numbers would be high.

**"What was the shortcut you found?"**
The defective unanswerable class put a fabricated identifier in the hard case,
so a filter that looked only at identifiers found every hard question. It is
reported in the shortcut audit, which ships with the benchmark, and the
defective class's refusal rate of {{UNANS_BEFORE_REFUSED_PCT}} is reported as
the upper bound it was rather than as a result.

**"Why does the closed-book accuracy appear in the audit?"**
Because a class that a model without retrieval can recognise as unanswerable
is measuring something else. The closed-book unanswerable rate is
{{UNANS_CLOSED_BOOK_ACC}}, and the audit table carries it so that the reader
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
{{CONTRA_PRECISION_PCT}} against reader labels, with a 95 percent upper bound
of {{CONTRA_PRECISION_CI_HI}}, and the annotators agreed on all
{{CONTRA_PRECISION_AGREE_N}} decisions, so the labelling is not the problem.
The mechanism is unproven rather than disproven: this corpus does not hold
the phenomenon the detector detects.

**"Why not report the contradiction detector's recall instead?"**
Because recall against a ground truth defined by the detector's own threshold
measures agreement with itself, not precision. That is the mistake the
contradiction thread in the literature review is there to prevent.

**"The reranker makes things slightly worse on your focus corpus. Why keep
it?"**
Because on the six-category corpus it moves MRR by {{MC_MRR_RERANK_PP}}
points, and the system has to run on more than one corpus. The honest summary
is that a component that helps on one corpus and not on another is not a
component that helps, and the sentence about the reranker is never used
without its corpus attached.

**"Your transferred threshold over-refuses. Isn't that just a failure?"**
It is a failure, and it is finding F12. A calibrated threshold does not
transfer across corpora: the transferred arm answered
{{GEN_A_XFER_ANS_ANSWERED}} answerable questions against
{{GEN_A_NOGATE_ANS_ANSWERED}} for the ungated arm. That is the reason the
threshold is a configuration value rather than a property of the method, and
it is the first item on the future-work list to settle.

### About the scope

**"Why only one generator?"**
Because the replication could not be run. The second model returned no text
on {{GENCOMP_FAILING_EMPTY_N}} of the {{GENCOMP_FAILING_EMPTY_TOTAL}}
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
