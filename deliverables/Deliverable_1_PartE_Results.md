
---

# Part E — The Experiments and What the Numbers Mean

Every number in this part was produced by the code in `impl/` on the public
industrial corpus, and can be regenerated with four commands. The seeds are
fixed; the index is cached by content hash.

```bash
.venv/bin/python impl/experiments/run_ablation.py
.venv/bin/python impl/experiments/run_gate.py
.venv/bin/python impl/experiments/run_contradiction.py
.venv/bin/python impl/experiments/run_transfer.py
```

## E.0 The corpus, and why its composition is the first thing to report


The evaluation corpus was built independently of the proprietary
supply-chain corpus used in the September 2026 run, so that the results are
reproducible and not tied to one document set.

| Property | Value |
|---|---|
| Documents | 14 (fetched from public reference endpoints) |
| Chunks | 735 |
| Modality composition | **88.8% text**, 6.0% table, 5.2% chart |
| Total words | 73,943 |
| Mean words per chunk | 100.6 |
| Categories | 6 industrial families (supply chain, predictive maintenance, production scheduling, quality, reliability, facility layout) |
| Benchmark | 176 silver-standard queries — 32 answerable, 144 deliberately unanswerable |

**The modality composition is the single most predictive number in this
report**, and it is worth comparing with the September 2026 corpus:

| Corpus | Text | Table | Chart |
|---|---|---|---|
| September 2026 project report | 90.6% | 7.1% | 2.3% |
| This evaluation corpus | 88.8% | 6.0% | 5.2% |

Two independently constructed industrial corpora land on almost the same
composition. That is not a coincidence and it is not a design choice — it is
what industrial documentation *is*. The consequence, developed in §E.1, is that
a modality-aware mechanism has very little to work with on either corpus, and
that any positive result reported on such a corpus should be treated with
suspicion until the corpus composition is examined.

**A note on the label standard.** The benchmark is *silver*, not expert-annotated.
Labels are derived mechanically from the document — a table cell becomes a lookup
question, a definitional sentence becomes a question. This has one bias that goes
in a known direction: the derived gold chunk is guaranteed to contain the answer
somewhere, whereas an expert annotator might have judged it insufficient. So
**absolute recall is optimistic**. It does not bias the *comparison* between
systems, because every system is scored against identical labels — and the
comparison is what the ablation tests.


## E.1 Retrieval ablation (Experiment 1)

**This is the focus domain** — supply chain management, the single industrial domain this thesis is about. Every number in E.1, E.2, E.3 and E.5 is measured on it. E.4 is the exception: the cross-category transfer experiment is by definition a multi-category measurement, and is reported on the six-category corpus.

Seven systems, the same 176 queries, paired Wilcoxon signed-rank tests between adjacent rungs.

| System | R@5 | R@10 | R@20 | P@10 | MRR | nDCG@10 | Table R@10 | ΔR@10 | p | ΔMRR | p |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A. bm25_only | 0.969 | 0.969 | 1.000 | 0.097 | 0.736 | 0.792 | 1.000 | — | — | — | — |
| B. dense_only | 0.781 | 0.812 | 0.875 | 0.081 | 0.652 | 0.688 | 0.875 | -0.1562 | 2.53e-02 | -0.0833 | 2.86e-01 |
| C. hybrid_rrf | 0.969 | 1.000 | 1.000 | 0.100 | 0.798 | 0.847 | 1.000 | +0.1875 | 1.43e-02 | +0.1453 | 1.46e-03 |
| D. hybrid_rrf_rerank | 0.906 | 0.969 | 1.000 | 0.097 | 0.795 | 0.836 | 1.000 | -0.0312 | 3.17e-01 | -0.0026 | 1.00e+00 |
| E. +category_filter | 0.906 | 0.969 | 1.000 | 0.097 | 0.795 | 0.836 | 1.000 | +0.0000 | 1.00e+00 | +0.0000 | 1.00e+00 |
| F. +quota_pre_rerank | 0.969 | 1.000 | 1.000 | 0.100 | 0.819 | 0.864 | 1.000 | +0.0312 | 3.17e-01 | +0.0237 | 6.79e-02 |
| G. +quota_post_rerank | 0.906 | 0.938 | 0.938 | 0.094 | 0.789 | 0.826 | 1.000 | -0.0625 | 1.57e-01 | -0.0297 | 6.79e-02 |

**Read the two right-hand blocks together.** Recall@10 is close to its ceiling on silver-standard labels -- a question derived from a chunk contains that chunk's own words, so the plain lexical retriever already finds the gold chunk most of the time. The ordering metrics are where the systems actually differ, and they are measured with the same paired Wilcoxon test.

Bootstrap 95% CI for the best system's Recall@10 (C. hybrid_rrf): 1.0000 [1.0000, 1.0000], 10,000 resamples.


### Finding 1 — The encoder, not the fusion, was the weak part

| System | Recall@10 |
|---|---|
| BM25 only | 0.969 |
| Dense only | 0.812 |
| Hybrid (RRF) | 1.000 |

The dense leg reaches **0.812** against BM25's
**0.969** — a deficit of
0.156 (p =
2.5e-02).

That deficit is smaller than it was. The dense leg used to be a
*general-purpose sentence encoder*, trained with a symmetric similarity
objective: two sentences that mean the same thing should be close. Retrieval is
**asymmetric** — a passage is not *similar* to a question, it *answers* it —
and the mismatch showed up as a lexical leg that was better on its own than the
fusion was. The encoder is now `BAAI/bge-m3`, a retrieval-trained multilingual
model, and the before/after is in `research/09_encoder_swap.md`: the dense leg
went from 0.636 to 0.812 on Recall@10, and the fusion's
ordering against the lexical leg went from 0.798 − 0.722 to
0.792 − 0.847 — a deficit of 0.076 turned into a surplus of 0.055: the fusion now orders better than the lexical leg alone, which it did not before.

The lesson generalises past this corpus: a hybrid retriever is only as good as
its worse leg, and "hybrid" is not a free upgrade. Giving a weak leg half the
say in the ranking costs the strong leg's ordering, and the effect is silent —
the fusion's numbers look reasonable, they are just worse than the leg you
already had.

### Finding 2 — A reranker's recall is governed by its candidate pool

With a **top-50 rerank pool**:

| Metric | Before rerank | After rerank | Change |
|---|---|---|---|
| Recall@10 | 1.000 | 0.969 | -0.031 |
| Recall@20 | 1.000 | 1.000 | +0.000 |
| MRR | 0.798 | 0.795 | -0.003 |
| nDCG@10 | 0.847 | 0.836 | -0.011 |

With a **top-10 pool** — the size of the final context — the same reranker
reaches Recall@10 1.000 and Recall@20 1.000, against the
top-50 pool's 0.969 and 1.000, and MRR 0.805 against
0.795. **The bigger pool is worse, not better.** The mechanism is in
§C.5: a cross-encoder can only reorder what it is shown, and a pool larger than
the context it fills can reorder candidates *out* of that context.

**Why this is the most valuable finding in the project.** The September 2026
project report records a **−5.34 percentage-point** reranker regression on
`production_scheduling`, on a different corpus, and reports it as an
unexplained anomaly. Our experiment supplies a candidate mechanism: a rerank
pool too small relative to the final context. We do not have their code, so we
state this as a **hypothesis with a cheap test** — measure the rerank pool size
against the final context size — rather than as an explanation. But it converts
an anomaly into a configuration check.

### Finding 3 — The category pre-filter: what it does, and the repair that does not work

| Metric | No filter | With filter | Change |
|---|---|---|---|
| Recall@10 | 0.969 | 0.969 | +0.000 |
| Table Recall@10 | 1.000 | 1.000 | +0.000 |
| MRR | 0.795 | 0.795 | +0.000 |
| nDCG@10 | 0.836 | 0.836 | +0.000 |

**On this corpus the filter does nothing, and that is the correct result.** Every figure above is unchanged: the corpus has one category, so the filter has nothing to restrict. A filter's measured effect is a property of the corpus, not of the filter, and this is the corpus where that is visible.

**On the six-category corpus, where the filter has something to restrict**, it costs no recall at all and gains ordering. Recall@10 is 0.932 without the filter and 0.932 with it (+0.0000, p = 1.000), while MRR goes from 0.776 to 0.802 (+0.0261, paired Wilcoxon p = 0.027) and nDCG@10 from 0.814 to 0.834. **So the filter does not trade recall for modality precision on this corpus: it trades nothing for ordering.** The trade-off that an earlier revision of this section described was a measurement of a corpus the project no longer ships.

**And the repair proposed for the filter does not work.** The alternative named in the project's own threat list was a *soft* prior: the whole corpus stays in the candidate pool and the in-category chunks are promoted in the fused ranking by an extra reciprocal-rank-fusion term, instead of being the only candidates. It was tried at three weights on the 132 answerable queries of the six-category corpus, and **every one of them returns the no-category numbers exactly** — MRR 0.7764 against the hard filter's 0.8025, paired Wilcoxon p = 0.027. There was nothing to recover in the first place: **not one of the corpus's gold chunks sits outside its question's category** (0 of 132), so the filter's recall cost is exactly zero. What the filter buys is ordering, and the reason a prior cannot reproduce it is mechanical: **a filter removes and a prior only reorders.** Removing the out-of-category chunks removes chunks the reranker would have ranked highly and replaces them with in-category material; promoting the in-category chunks leaves the final ten-chunk context unchanged.

### Finding 4 — The quota belongs *before* the reranker, not after

This is the finding that contradicts the original design, and it contradicts
it in the opposite direction to the one the design anticipated.

| Variant | Recall@10 | Table Recall@10 | nDCG@10 |
|---|---|---|---|
| No quota | 0.969 | 1.000 | 0.836 |
| Quota **before** the reranker | 1.000 | 1.000 | 0.864 |
| Quota **after** the reranker | 0.938 | 1.000 | 0.826 |

Applying the quota **before** the reranker gives table recall
1.000 — against
1.000 with no quota at all — and leaves
overall recall at 1.000. Applying the *same quota* **after** the
reranker reaches only 1.000 of table recall
and gives back -0.062 of overall recall
(p = 1.57e-01).
The same ordering holds on the six-category corpus: the pre-rerank quota
reaches table recall 1.000 and the post-rerank quota 0.962.

**The mechanism**, from §C.8, is about what each stage can and cannot undo. A
pre-rerank quota proposes a *membership* for the final ten; the cross-encoder
then re-scores those ten and can reorder them, but it cannot change which ten
they are, so a forced table chunk survives. A post-rerank quota starts from
the reranked ten and swaps one of them for a table chunk the cross-encoder
already ranked **below** the cut — so it tends to import the wrong table chunk
and to displace a good one. The quota applied later is working against a
veto it cannot appeal.

**The generalisable rule, corrected:** *a constraint on a downstream artefact
should be enforced where it can still choose the candidates, not where it must
work against another component's judgement.* Enforcing a constraint downstream
of a scorer means importing candidates the scorer has already rejected. This
is the design lesson from this project most likely to transfer to other work,
and the project arrived at it by measuring the opposite of what it expected.

### Finding 5 — Corpus composition predicts the sign of the modality effect

Note that even the best quota variant (1.000
table recall) sits below the unfiltered hybrid+rerank system
(1.000). **On a corpus that is
88.8% prose, the modality quota cannot win.**
The mechanism is arithmetic: a two-table quota can only draw on tables deep in
the ranking — tables *less* likely to be relevant — and it displaces relevant
prose to do it.

This is why the September 2026 report's null modality result
(2.3% chart, 7.1% table) should be read as a **power limitation rather than a
defect**, and why the framework measures the corpus composition at all: it
predicts whether D2 can have any effect before you run the experiment.

**What would fix it:** stratify the corpus so that the modalities are
adequately represented, and pre-register a power analysis alongside the result.

![Figure 4. Overall Recall@10 against table-specific Recall@10 for the seven ablated systems, focus corpus (black circles, n = 32 answerable: 24 text, 8 table) and industrial corpus (grey squares, n = 247: 117 text, 130 table). The modality quota does not move both axes: on the industrial corpus the pre-rerank quota buys 0.8 points of table recall and gives up 0.8 points of overall recall, and the post-rerank quota lands on exactly the no-quota operating point; on the focus corpus the post-rerank quota gives up 3.1 points of overall recall while table recall stays at 1.000. The quota is a trade, not a gain, and which way it trades depends on where it is applied.](figures/fig4_modality_quota_pareto.pdf)

## E.2 The confidence gate (Experiment 2)

The gate was evaluated as a **selective-prediction policy**: the threshold was
swept, and for each value we report what the system answered, what it refused,
and the abstention precision.

**What the label actually is, and the table that says so.** The label is 1 iff
the gold chunk is present in the reranked candidate pool. That is
*answer-in-context detectability*, not evidence sufficiency — the literature
reserves "sufficiency" for the set-level property that independent passage
scoring cannot detect (SURE-RAG, arXiv:2605.03534; Certify,
arXiv:2610.34684) — and the difference is not a naming quibble, because it
determines what the negative class contains.

| | Count | Share |
|---|---|---|
| Answerable, evidence found in the context | 32 | 100.0% of answerable |
| Answerable, evidence **missed** by the retriever | 0 | 0.0% of answerable |
| Unanswerable | 144 | 100.0% of unanswerable |

The negative class is answerable-and-missed **plus** unanswerable. The
retriever's own recall of the gold chunk is
1.000, so the negative class is dominated by
**retrieval failure** — an answerable question whose evidence the retriever
missed — rather than by absence of evidence. The gate therefore detects whether
the answer is in the context, and **cannot** distinguish "there is no evidence
here" from "the evidence is here and the retriever missed it", because the
retrieval scores it uses are exactly the scores that failed. That is a
limitation of the approach, it is also the field's known result for model- and
prompt-based abstention (GRAB-RAG, arXiv:2608.22228), and it is why the gate
is reported as a selective-prediction policy rather than as a detector.

### The two baselines, and the two that are not

| Policy | Answers answerable | Refuses unanswerable | Abstention precision |
|---|---|---|---|
| **Never refuse** (τ = 0) | 1.000 | 0.000 | undefined — no abstentions are made |
| **Always refuse** (τ = 1) | 0.000 | 1.000 | 0.818 |
| Loosest threshold in the sweep (τ = 0.05) | 0.938 | 0.361 | 0.963 |
| Strictest threshold in the sweep (τ = 0.95) | 0.062 | 1.000 | 0.828 |

The last two rows are **not baselines**. The loosest threshold in the sweep
still refuses some unanswerable queries, so calling it an "always-answer
baseline" overstates what it shows; the strictest threshold still answers some
answerable ones. The two degenerate policies are the baselines, and the gate
has to be read against them.

### Calibration

| | Fitted here | Earlier project report |
|---|---|---|
| Univariate β₀ / β₁ on the top rerank score | -1.8473 / 0.2159 | — |
| Multivariate intercept | -2.0607 | — |
| Brier score (held-out) | 0.1510 | — |
| Expected Calibration Error | 0.1044 | — |

The coefficients differ substantially from the ones fitted on a different corpus
in the September 2026 run (β₀ = 2.943, β₁ = 1.680, 30 queries, chunk-level).
**This is not an
inconsistency — it is the central methodological point of this section.** The
calibration is a *fitted parameter of the deployment*, not a constant of the
architecture. A threshold transferred to a new corpus or a new retriever is
wrong, and the error direction is not arbitrary: DeclineCraft (Thakur et al.,
2026) shows that a stronger retriever changes the correct operating point.

The gate is calibrated on a **query-level** label — does the retrieved context
contain sufficient evidence to answer? — and not on a chunk-level label. That
distinction is the correction that made this experiment meaningful: with one
gold chunk among ~50 candidates the chunk-level base rate is about 2%, so a
classifier answering "nothing is relevant" is right 98% of the time and the
calibration metrics look excellent while measuring nothing but the base rate.
The label you choose determines what you are measuring.

### The threshold sweep

| τ | answerable answered | unanswerable refused | abstention precision | coverage |
|---|---|---|---|---|
| 0.05 | 0.938 | 0.361 | 0.963 | 0.693 |
| 0.10 | 0.812 | 0.653 | 0.940 | 0.432 |
| 0.15 | 0.656 | 0.701 | 0.902 | 0.364 |
| 0.20 | 0.594 | 0.792 | 0.898 | 0.278 |
| 0.25 | 0.500 | 0.882 | 0.888 | 0.188 |
| 0.30 | 0.500 | 0.903 | 0.890 | 0.170 |
| 0.35 | 0.469 | 0.931 | 0.887 | 0.142 |
| 0.40 | 0.438 | 0.938 | 0.882 | 0.131 |
| 0.45 | 0.344 | 0.958 | 0.868 | 0.097 |
| 0.50 | 0.344 | 0.958 | 0.868 | 0.097 |
| 0.55 | 0.312 | 0.958 | 0.863 | 0.091 |
| 0.60 | 0.250 | 0.979 | 0.855 | 0.062 |
| 0.65 | 0.188 | 0.979 | 0.844 | 0.051 |
| 0.70 | 0.156 | 0.979 | 0.839 | 0.045 |
| 0.75 | 0.156 | 0.979 | 0.839 | 0.045 |
| 0.80 | 0.156 | 0.986 | 0.840 | 0.040 |
| 0.85 | 0.125 | 0.993 | 0.836 | 0.028 |
| 0.90 | 0.094 | 1.000 | 0.832 | 0.017 |
| 0.95 | 0.062 | 1.000 | 0.828 | 0.011 |

### The operating point

Selected by the stated rule — **highest tau answering >= 90% of answerable queries**:

| Quantity | Value |
|---|---|
| τ | **0.05** |
| Answerable questions answered | 0.938 |
| Answerable questions refused (false refusals) | 0.062 |
| Unanswerable questions refused (correct refusals) | 0.361 |
| Abstention precision | 0.963 |
| Coverage | 0.693 |
| Never-refuse baseline (τ = 0): unanswerable refused | 0.000 |
| Always-refuse baseline (τ = 1): answerable answered | 0.000 |
| Loosest threshold in the sweep (τ = 0.05): unanswerable refused | 0.361 |

**Read the abstention-precision column, not just the refusal column.** A gate
that refused everything would also have a high refusal rate on unanswerable
questions; abstention precision is what distinguishes a working gate from an
abstaining one. And the always-answer baseline refuses nothing, so the *gain*
from the gate is measured against a system that guesses on every unanswerable
question — which is what a plain RAG system does.

The full risk–coverage curve is in `impl/results/exp2_gate.json`, with the
per-bin reliability table alongside it. The curve is the honest form of the
result: there is no single operating point that is right for every deployment,
and the number to quote depends on the cost of a wrong answer relative to the
cost of no answer. In industrial decision support the second is usually far
lower, which is why the operating point is pushed toward refusal.




![Figure 2. Risk-coverage of the confidence gate: the risk that an answered query has no answer in its context, against the fraction of queries the gate answers, on the held-out evaluation half (focus n = 71, industrial n = 178). The degenerate policies bound the curve: always answering carries the base rate of the negative class as its risk at full coverage, and always refusing removes the risk at the cost of all coverage. The industrial gate trades risk for coverage; the focus gate buys almost nothing over answering everything. The fitted operating points (tau = 0.05 focus, tau = 0.40 industrial) answer 0.693 and 0.691 of all queries respectively.](figures/fig2_risk_coverage.pdf)

![Figure 3. Reliability of the gate's calibrated probability against observed answerability, on the held-out evaluation half (focus n = 71, industrial n = 178); the upper panel plots observed answerability against mean predicted probability per bin and the lower panel the number of queries in each bin. The industrial gate tracks the diagonal (ECE 0.075, Brier 0.159); the focus gate does not (ECE 0.1044, Brier 0.1510): it puts most of its queries in the lowest confidence bin, where few of them have an answer in context.](figures/fig3_calibration.pdf)

## E.3 Contradiction surfacing (Experiment 3)

| Detector | Pairs flagged | Flag rate |
|---|---|---|
| NLI alone | 110 | 0.081 |
| **The shipped gate** (NLI **and** same-subject, plus the quantity and revision branches) | 20 | 0.015 |
| Baseline: always flag | 1350 | 0.985 |
| Baseline: never flag | 0 | — |

The gate has three branches, and the alarms split
**20 semantic**, **0 quantity**
and **0 revision**. The same-subject check is what
does the work: it suppresses
**90** of the bare NLI gate's
alarms, leaving 20 of 1350 pairs.

- **Prevalence of true conflict among compared pairs: 0.0148.**
  Without prevalence, a false-positive rate is uninterpretable: at low
  prevalence, even a detector with excellent recall has a high FP rate.
- The revision-supersession check suppressed a further
  **0** pairs whose apparent conflict was
  simply a later revision of the same policy.

**Two rules were measured, found defective, and repaired.** The quantity branch
used to key a number to the nearest distinctive word in the sixty characters
before it, so on encyclopaedic text it fired on citation years, on version
numbers and on surnames — the reader labels below confirmed it, and the
pre-repair run is archived so that the repair is checkable rather than
asserted. It now keys a number to a **measurement term**, excludes bare years
and hyphenated identifiers, rejects a measurement term that begins a proper
name ("Productivity Press" is a publisher, not a measurement), and requires
the two passages to be about the same *instance* — Plant A's reorder point and
Plant B's reorder point are two reorder points, not one with two values. The
quantity-level conflicts it reports fell from
**21 to
0**.

The second defect was in the subject check itself. Its own design says that
two passages with high semantic similarity and no shared objects are almost
always about different things — but the implementation let high similarity
through *on its own*, so on a corpus of articles all about one subject the
check was a **topic** check, and two chunks of the same article about different
sub-topics passed it. Requiring shared concrete objects as well, as designed,
cut the alarms from **76 to 20** — and
from 81 to 20 over both
repairs together — and removed every alarm a reader had called a subject
mismatch. The corpus, the
benchmark and the label standard were not changed, and neither rule was tuned
to a target.

**The precision, measured against reader labels.** The contradiction gate's precision, measured against reader labels rather than against a proxy, is 0%: none of the 20 labelled alarms was called a contradiction by either annotator, and the 95% upper bound on the gate's true precision is 16.1%. The two annotators do not share a model, both read the sheet blind to the detector's own scores, and both scored 14 of 14 on a control set whose labels are known in advance, and they agree on the contradiction/no-contradiction decision for 101 of the 101 pairs they labelled. The annotators are models rather than people, so the number says the alarms are not confirmed by a reader, not that no reader would ever confirm one.

The gate has three branches, each measured separately: the semantic branch's 0 of 20 alarms were accepted as genuine contradictions by both annotators. A branch whose measured precision is below the calibration floor has its findings recorded and withheld rather than shown to a practitioner — the same discipline the answer gate applies to an answer, applied to the framework's own claims.



**The detector's own positive control.** The detector's own positive control -- pairs whose correct behaviour is known in advance, written in the industrial register but not drawn from the corpus -- is 11 of 11, with every contradiction caught and every non-conflict left alone. So the mechanism works; this corpus does not test it.
The labels ship with the results so that a reader can disagree with any of
them: the sheet is `impl/results_focus/exp11_contradiction_labels.json`, the
two annotators' labels are `exp11_judge_a_labels.json` and
`exp11_judge_b_labels.json`, the fourteen-pair control set and its two label
files are `exp11_judge_control.json`, `exp11_judge_control_a.json` and
`exp11_judge_control_b.json`, the pre-repair run is archived as
`exp11_contradiction_precision_pre_repair.json` beside
`exp3_contradiction_pairs_pre_repair.jsonl`, and the rubric itself is
`impl/experiments/data/contradiction_label_rubric.md`.

**The honest reading.** The gate is better than NLI alone, and the
always-flag and never-flag rows make the comparison meaningful — but the
measurement above is a negative one, and it is negative in a way that is more
specific than "the detector is bad". After the two repairs the gate raises
20 alarms, all of them from the NLI-and-same-subject
conjunction, and the readers confirm none of them. They say why, and the two
reasons are different failures: a pair about *different subjects* is the
subject check letting a pair through, and a pair that does not disagree at all
is the NLI model being wrong. Both need data this corpus does not have —
entity-level identifiers that distinguish two plants, and instance records that
can contradict one another. The deeper point is about the benchmark rather than
the detector: the same readers find no contradiction in a random sample of the
pairs the gate did *not* flag, so the corpus does not contain the phenomenon
the mechanism exists to detect. Published NLI ceilings on technical text are far
below general-domain performance (78.18% macro-F1 on SciNLI; 51.77% for an
LLM-based system on MSciNLI), and annotation artefacts and negation failure
compound it.

**And the system now says nothing rather than saying the wrong thing.** Each
branch has a measured precision, fitted from the labelling experiment and
shipped beside the gate's fitted model as `conflict_calibration.json`. The
pipeline reads it and withholds the findings of any branch whose measured
precision is below the floor, so the surface a practitioner sees is governed by
a measurement rather than by a threshold somebody chose. On this corpus that
leaves **20 findings surfaced and
0 withheld**. **A contradiction detector for
industrial documentation is a triage aid, not an oracle** — and the design
reflects the weaker claim, by reporting a conflict *type* rather than a binary
flag, by refusing to resolve conflicts automatically, and by declining to
raise a conflict it cannot support.

The counter-evidence to "resolve automatically" is published: CLECK found models
default to the authoritative claim and shift by only 34 points when the conflict
is made explicit, and ContraDoc found models that outperform humans yet remain
unreliable at contradiction detection. **Surfacing beats resolving.**




![Figure 6. The contradiction detector's precision against the base rate of real conflicts in the same population, with 95% Wilson intervals; a filled marker means the point estimate clears the framework's 0.5 calibration floor and the branch would act, a hollow one means it does not and the findings would be withheld. The focus corpus's semantic branch has a precision of 0.0 (0 of 20 alarms confirmed by either annotator) on a base rate of 0.0, so it is withheld; the industrial semantic branch reaches 0.65 (26 of 40) against a base rate of 0.35 and would act.](figures/fig6_contradiction_precision.pdf)

## E.4 Cross-category transfer (Experiment 4)

**This section is measured on the six-category corpus**, not on the focus
domain: a transfer experiment needs a subset of categories to transfer to
held-out ones, and the focus domain has one. Note also that all six categories
are industrial-engineering sub-domains, so this is an *intra-domain* transfer
study.

**Each arm is evaluated on the queries it is about.** The tuning arm is
scored on the tuning half with the model and threshold fitted there; the
transferred arm carries that model and threshold unchanged onto the held-out
half; the refitted arm is the ceiling -- the held-out half's own model and
threshold, scored on the held-out half. The difference between the second and
the third is what transferring a calibration actually costs.

**The split is over document categories, and the benchmark's unanswerable
questions have none.** They are not "about" a category, so neither half
contains any, and this experiment measures *coverage on answerable questions*
across domains. It says nothing about how well a transferred threshold refuses
unanswerable questions, because that population is not in the split. The
refusal behaviour is measured on the focus domain instead (E.2).

| Quantity | Value |
|---|---|
| Tuning categories | predictive_maintenance, production_scheduling, supply_chain_management |
| Held-out categories | facility_layout, quality_engineering, reliability_engineering |
| Calibrator intercept, tuning half | -1.224 |
| Calibrator intercept, held-out half | -1.383 |
| Top-1 rerank weight, tuning half | 3.139 |
| Top-1 rerank weight, held-out half | 0.955 |
| τ (fitted on the tuning half, transferred unchanged) | 0.05 |

| Metric (held-out half) | Transferred | Refitted |
|---|---|---|
| Answerable answered | 1.000 | 0.940 |
| Answerable refused | 0.000 | 0.060 |
| Unanswerable refused | 0.139 | 0.236 |

### Per-category retrieval quality

| Category | n | Recall@10 | MRR | nDCG@10 |
|---|---|---|---|---|
| facility_layout | 10 | 1.000 | 0.625 | 0.714 |
| predictive_maintenance | 24 | 0.958 | 0.813 | 0.849 |
| production_scheduling | 11 | 1.000 | 0.718 | 0.787 |
| quality_engineering | 23 | 1.000 | 0.651 | 0.738 |
| reliability_engineering | 34 | 0.853 | 0.590 | 0.652 |
| supply_chain_management | 30 | 1.000 | 0.811 | 0.857 |

**The same ablation on the six-category corpus**, which is the statistically stronger measurement (132 answerable queries against 32 on the focus domain), and the one in which the category filter is meaningful rather than a no-op:

| System | R@10 | R@20 | MRR | nDCG@10 | Table R@10 | dR@10 | p |
|---|---|---|---|---|---|---|---|
| A. bm25_only | 0.909 | 0.955 | 0.673 | 0.728 | 0.964 | — | — |
| B. dense_only | 0.750 | 0.795 | 0.545 | 0.593 | 0.786 | -0.1591 | 1.62e-04 |
| C. hybrid_rrf | 0.932 | 0.955 | 0.666 | 0.730 | 0.964 | +0.1818 | 9.63e-07 |
| D. hybrid_rrf_rerank | 0.932 | 0.939 | 0.776 | 0.814 | 0.929 | +0.0000 | 1.00e+00 |
| E. +category_filter | 0.932 | 0.939 | 0.802 | 0.834 | 0.929 | +0.0000 | 1.00e+00 |
| F. +quota_pre_rerank | 0.939 | 0.939 | 0.799 | 0.834 | 1.000 | +0.0076 | 7.05e-01 |
| G. +quota_post_rerank | 0.924 | 0.924 | 0.800 | 0.832 | 0.929 | -0.0152 | 4.80e-01 |



**The qualitative structure is the important part.** The *ranking* of
configurations transfers across industrial sub-domains; the *threshold* does not
transfer unchanged; and the direction of the error is systematic — **a threshold
fitted on one configuration is too permissive where it is transferred, and too
permissive in the direction that flatters the configuration it is transferred
to.** At the tuning half's threshold applied unchanged to the held-out half,
the gate answers 1.000 of the answerable questions against
0.940 when the weights are refitted there, and refuses 0.139 of
the unanswerable ones against 0.236. That direction is why a single
global threshold across arms would be misleading: it would make the arm it was
transferred to look better than it is.

This is the practical form of DeclineCraft's finding that better retrieval
reduces abstention, and it is why the calibration is re-fitted per arm in
Experiment 2 rather than fitted once and reused.

**The calibration itself does not transfer.** The fitted coefficients differ
substantially between the two halves: the intercept is
-1.224 against
-1.383, and the top-1 rerank
weight is 3.139 against
0.955. A posterior fitted on one
set of industrial sub-domains is therefore not a posterior on another: the
*numbers* are not comparable across categories even when the *decisions* look
similar.

**Comparing at a fixed threshold.** Comparing each half at its own selected
threshold is close to trivial, because the selection rule lands on the same
(lowest) threshold in both. The table below holds the threshold fixed and asks
what the transferred calibration actually does on the held-out categories.

| τ | held-out: answerable answered | held-out: unanswerable refused |
|---|---|---|
| 0.10 | 0.925 | 0.396 |
| 0.25 | 0.731 | 0.639 |
| 0.50 | 0.448 | 0.840 |
| 0.75 | 0.164 | 0.965 |

The retrieval difficulty also varies sharply by category — the per-category
table above shows recall@10 ranging from 0.853 (reliability_engineering) to 1.000
(facility_layout) — which is why a single calibration cannot serve all six.



## E.5 The rerank candidate-pool sweep (Experiment 5)

The headline finding of Experiment 1 is that a cross-encoder's effect on
recall is governed by how many candidates it is shown relative to how many
the final context keeps. That claim deserves a curve rather than a single
comparison.

**The curve below is the six-category corpus, and it has to be.** On the focus domain the benchmark's recall is at ceiling for every pool size — a question derived from a chunk contains that chunk's own words — so the curve there is flat and uninformative. The effect is measurable where there are enough queries for it to be measurable.

| Rerank pool | R@10 | R@20 | MRR | nDCG@10 | Table R@10 |
|---|---|---|---|---|---|
| 5 | 0.902 | 0.902 | 0.777 | 0.809 | 1.000 |
| 10 | 0.955 | 0.955 | 0.807 | 0.844 | 1.000 |
| 20 | 0.932 | 0.962 | 0.808 | 0.838 | 0.929 |
| 50 | 0.932 | 0.939 | 0.802 | 0.834 | 0.929 |
| 100 | 0.932 | 0.947 | 0.803 | 0.834 | 0.929 |

**The curve peaks early and then declines.** Recall@10 rises from 0.902 at a pool of 5 to 0.955 at a pool of 10 — a gain of 0.053 — and then *falls* to 0.932 by a pool of 100. A larger pool is not monotonically better: the reranker is shown more candidates, and the extra ones are distractors that compete for the same 10-slot cut. The useful pool is about the size of the final context, and going past it buys nothing and costs a little. The change from the smallest pool to the peak is 0.053, and the loss from the peak to the largest pool is 0.023. Table recall moves with it: at a pool of 20 it is
0.929, against
1.000 at the smallest pool.

**The knee is the design rule.** The final context holds 10 chunks. A rerank
pool of the same size can only permute the set it was given, so it cannot
change *which* items reach the context — it can only change their order, and
it can lose a relevant chunk that was sitting just below its own cut. The
sweep locates the knee at a pool of about **10**, which is
1x the context it feeds, and it is worth
0.030 of recall over a pool of 5. This is a configuration check with a number attached, and
it is the cheapest actionable finding in the project: one parameter.

**Why it saturates.** A cross-encoder can only reorder what it is shown. Once
the pool contains the relevant chunk somewhere, a larger pool adds only more
distractors for the final top-k cut, and the marginal value of the extra
candidates falls to zero. The saturation point is therefore a property of the
corpus — how deep the first-stage ranking puts the answer — and not a constant
of the model.




![Figure 1. Recall against the size of the rerank candidate pool, on the focus corpus (black circles, 32 answerable of 176 queries) and the industrial corpus (grey squares, 247 of 444). The focus curve saturates at a pool of 10, where Recall@10 = Recall@20 = 1.000, and then falls slightly as the reranker is given more candidates to reorder. The industrial curve does not saturate at 10: there Recall@20 reaches 1.000 at a pool of 50 while Recall@10 stays at 0.988, so 1.21 points of gold are retrieved and then pushed out of the ten-chunk context.](figures/fig1_pool_size.pdf)

## E.6 The long-context baseline arm (Experiment 7)

The largest threat to this work is that the corpus fits in a modern context
window. If a reader given everything could answer the question directly, the
retrieval machinery would be unnecessary and every result in this part would
be beside the point. This section measures what can be measured.

**The cost half, which needs no generator.** The long-context arm puts the
whole corpus in the prompt; the RAG arm puts the retrieved context in it. On
the focus domain the corpus is **202,529 tokens** across
735 chunks, and the RAG arm's accepted context averages
**2,246 tokens** over
9.4 chunks. **The long-context arm costs
90x more input per query**, and the RAG arm
reaches the evidence using 0.90% of
what the long-context arm reads. On the six-category corpus the corpus is 680,417 tokens and the ratio is 282x.

Whether the long-context arm is *possible* is a separate question, and it
depends on the window:

| Context window | Focus domain | Six-category corpus |
|---|---|---|
| 1M tokens | yes | yes |
| 256K tokens | yes | **no** |
| 128K tokens — most hosted models | **no** | **no** |


**The retrieval-side proxy, which also needs no generator.** With the candidate
set widened from the fused shortlist to every chunk in the corpus — the
locating problem a long-context reader faces — does the same scorer still rank
the gold chunk inside the final context? On the focus domain, over
32 answerable queries, the gold chunk lands in the top 10 of
735 candidates **0.969** of the
time (95% interval 0.843 to
0.994), at a median rank of
**1**. The evidence is not merely present in a
large context; it is at the top of it.

On the six-category corpus the same measurement over
2,383 candidates puts the gold chunk in the top 10
**0.902** of the time (95% interval
0.839 to
0.942), at a median rank of
1.


**What this establishes, and what it does not.** It establishes the cost half
of the comparison, and the cost half is a property of this corpus and this
pipeline rather than of any particular model: the long-context arm is
90x more expensive per query, and on the
six-category corpus the corpus does not fit in the 128K window that most
hosted models offer at all.

**The quality half is measured in E.7.** A generator was put behind both arms on the focus domain, and with the whole corpus in the prompt it matched the pipeline's coverage on the answerable questions while being markedly less accurate. What the retrieval-side proxy above could not say -- what a reader does with the context once it has it -- is now measured, and on this corpus the answer is that having it all is not better. The six-category corpus still has no quality half, because the corpus does not fit a 128K window at all.





## E.7 The generator-side comparison (Experiment 8)

Everything above is retrieval-side. The framework's own hypothesis -- **H2.1,
"a code-level, non-bypassable gate reduces hallucination"** -- is an
answer-side claim, and until now it had never been tested with a generator in
the loop. This section is that test, and it is also the quality half of the
long-context comparison from E.6.

**One prompt cannot show what the gate does, so there are two.** The
instruction to the generator is an axis of this experiment, and the two
settings differ by a single sentence: under *cautious* the generator may
decline when the documents do not contain the answer, and under *answering* it
must answer from whatever context it is given. Everything else -- the model,
the questions, the retrieval, the scorer, the requested temperature -- is held
fixed. Both are needed because the finding is itself conditional: under the
cautious instruction the generator declines the unanswerable questions on its
own, so the gate's refusals are redundant with the prompt's and the two arms
cannot be told apart. The gate has to be measured against a generator that
answers, or it cannot be measured at all.

One generator answers the same 32 answerable and
144 unanswerable questions behind five arms that
share the generator, the prompt wording, the question set and the scorer:

| Arm | What it is |
|---|---|
| `rag_nogate` | the top-10 reranked chunks, with the confidence gate removed |
| `rag@fitted` | the framework, at the operating point fitted on this benchmark |
| `rag@random` | a **control**: refuses as many questions as `rag@fitted` did, but picks them at random and ignores the confidence score |
| `rag@transferred` | the framework, at the threshold transferred unchanged from the cross-category half |
| `long_context` | the whole corpus in the prompt, as in E.6 |

`rag_nogate` is what isolates the gate: it is the same retrieval with the gate
taken out, so the difference between it and `rag@fitted` is the gate's
contribution and not the retrieval's. `rag@random` is what isolates the
gate's *decision* from the mere fact of refusing: it refuses the same number
of questions as `rag@fitted` and picks them without using the confidence
score, so any difference between `rag@random` and `rag@fitted` is what the
gate's ranking buys over refusing an arbitrary set of the same size. A gate
that fires on the right questions and one that fires at random can produce the
same refusal count and very different answers.

**The cautious condition -- the deployed system.** The headline question is how
often a system answers a question that has no answer.

| Arm | Unanswerable refused by the gate | Unanswerable answered | Answerable answered | Accuracy on answerable | Claim hallucination on unanswerable | Claim support, all claims |
|---|---|---|---|---|---|---|
| the same retrieval with the gate removed | 0 | 77 of 144 (0.535) | 30 of 32 (0.938) | 0.633 | 0.554 | 0.539 |
| the framework at the operating point fitted on this benchmark | 58 | 60 of 144 (0.417) | 30 of 32 (0.938) | 0.800 | 0.566 | 0.564 |
| a control that refuses as many questions as the fitted gate did, but picks them at random | 49 | 54 of 144 (0.375) | 21 of 32 (0.656) | 0.714 | 0.529 | 0.558 |
| the framework at the operating point transferred unchanged from the cross-category half | 141 | 2 of 144 (0.014) | 6 of 32 (0.188) | 0.333 | 0.333 | 0.581 |
| the whole corpus in the prompt | 0 | 76 of 144 (0.528) | 31 of 32 (0.969) | 0.548 | 0.548 | 0.540 |

Two columns, two different questions, and they have to be read together.
**Unanswerable answered** is the *opportunity* for hallucination: how often
the system produced an answer where none exists. **Claim hallucination** is
the *fabrication* rate: of the claims it did produce, how many are supported by
nothing in the evidence it was given. A system that refuses everything scores
zero on the second and is useless, so the first is the headline and the second
is only ever read next to it. **The fabrication column is nearly empty**, and
it is important not to read it as a finding: across the five arms the
unanswerable questions produced 479 substantive claims
between them, so the column is a handful of claims wide. It is reported because
it is the quantity the hypothesis is about, not because it settles anything.

**Who did the refusing.** The first column is the gate refusing, in code,
before the generator is called at all. The questions that did reach the
generator were mostly refused by it in prose. Behind the ungated arm the
generator refused 67 of the 144 unanswerable questions itself,
and in the fitted arm the gate refused 58 of them -- so the gate's
refusals were almost entirely redundant with behaviour the prompt had already
produced. That is the first of the two findings of this section, and it is a
negative one for the framework: the refusal rate the retrieval-side experiments
attribute to the gate is, once a generator is behind the pipeline, mostly the
prompt's.
**The random control is the sharpest row in the table.** The control refused the same number of questions as the fitted gate and answered 54 of the unanswerable ones, against the fitted gate's 60 and the ungated arm's 77; it answered 21 of the answerable ones, against the fitted gate's 30 and the ungated arm's 30. The fitted gate's advantage over refusing an arbitrary set of the same size is the difference between those two rows, and a gate whose confidence score carried no information would land on the control's numbers.


**And the same comparison again, with the generator required to answer.** Under
the *answering* instruction the generator must answer from whatever context it
is given, so the opportunity for hallucination is real rather than hypothetical,
and the gate is the only thing standing between it and a fabricated answer:

| Arm | Unanswerable refused by the gate | Unanswerable answered | Answerable answered | Accuracy on answerable | Claim hallucination on unanswerable | Claim support, all claims |
|---|---|---|---|---|---|---|
| the same retrieval with the gate removed | 0 | 135 of 144 (0.938) | 32 of 32 (1.000) | 0.656 | 0.569 | 0.481 |
| the framework at the operating point fitted on this benchmark | 58 | 76 of 144 (0.528) | 30 of 32 (0.938) | 0.667 | 0.578 | 0.498 |
| a control that refuses as many questions as the fitted gate did, but picks them at random | 49 | 87 of 144 (0.604) | 21 of 32 (0.656) | 0.714 | 0.642 | 0.402 |
| the framework at the operating point transferred unchanged from the cross-category half | 141 | 3 of 144 (0.021) | 6 of 32 (0.188) | 0.000 | 0.200 | 0.486 |
| the whole corpus in the prompt | 0 | 134 of 144 (0.931) | 32 of 32 (1.000) | 0.406 | 0.620 | 0.430 |

Paired question by question, the gate refused 60 of the questions the ungated arm answered and let through 1 of the ones it did not, and the exact two-sided McNemar test on those discordant pairs gives p = 0.000. This is the comparison that isolates the gate: the same retrieval, the same model, the same questions, the same scorer, and one instruction changed.

Here the gate does what it was built to do. It refused
58 of the
144 unanswerable questions before the generator was
called at all, the ungated arm answered
135 of them and the gated arm answered
76, and the price was coverage: the
framework answered 30 of the
32 answerable questions against the ungated arm's 32. At the transferred threshold the gate
refused 141 of the
144 unanswerable questions and the answer rate fell to
0.021.

**The random control is the sharpest row in the table.** The control refused the same number of questions as the fitted gate and answered 87 of the unanswerable ones, against the fitted gate's 76 and the ungated arm's 135; it answered 21 of the answerable ones, against the fitted gate's 30 and the ungated arm's 32. The fitted gate's advantage over refusing an arbitrary set of the same size is the difference between those two rows, and a gate whose confidence score carried no information would land on the control's numbers.


### E.7.1 The comparison on a second generator — and why it could not be run

One generator behind five arms settles the hypothesis for one model, so the whole design was repeated on a second one, changed in nothing but the model id. It could not be run. MiniMax-M3 returned no text on 0 of the 66 questions it was asked (0 of them on the benchmark's table-lookup family, against 0 of 22 on a control sample of the other families); MiniMax-M3.1-Flash returned no text on 24 of the 66 questions it was asked (23 of them on the benchmark's table-lookup family, against 1 of 22 on a control sample of the other families). The failures are not a shortage of output budget -- of the requests that came back empty, 13 were rescued by retrying at 4096 tokens and 11 were still empty there, the model spending the whole budget on reasoning and returning nothing. An empty completion is neither an answer nor a refusal, so the harness records the run as not-run instead of reporting a rate it cannot stand behind.

| Generator | No text returned | Of which on the table-lookup family | Of which on a control sample of the other families |
|---|---|---|---|
| MiniMax-M3 | 0 of 66 | 0 of 44 | 0 of 22 |
| MiniMax-M3.1-Flash | 24 of 66 | 23 of 44 | 1 of 22 |

An empty completion is neither an answer nor a refusal, so the harness raises on it rather than recording "did not answer" -- recording it either way would put a rate in these documents that the measurement does not support. A run whose arm asked fewer questions than the benchmark holds is recorded as not-run, with the reason.

Two things follow, and they point in opposite directions. The limitation is the honest one: the gate's contribution is established on one generator, and the replication that would settle it for a second is open. The finding is that a generator behind a RAG pipeline can return neither an answer nor a refusal, and that the failure concentrates on the table lookups. It is also worth noticing what does *not* happen: the gate refuses before the generator is called, so a generator that cannot answer costs nothing on the questions the gate rejects. That is an argument for the gate being a branch rather than an instruction, and the framework did not have to make it in advance.


**And the whole corpus in the prompt does not win.** With the corpus in context the generator answered 31 of 32 answerable questions -- the same coverage as the ungated pipeline -- and it declined the unanswerable questions at a comparable rate (76 of 144 against 77), for 74 times the input actually sent per query, counted by the provider (E.6's 90x is the same comparison measured with the corpus's own tokenizer, and against the accepted context rather than the whole request). On coverage and on cost the answer is settled: the whole-corpus prompt does not decline more unanswerable questions than the pipeline does, and it costs 74 times as much to do it. On answer *quality* the answer is weaker than the raw numbers suggest, and E.8 is the reason: the accuracy column is measured against silver-standard labels, and the margin over the whole-answer entailment test does not survive a length-controlled re-scoring of the same answers.

**How a claim is scored.** Each answer is split into atomic claims, and each
claim is scored against **the evidence that arm was given** -- its retrieved
chunks, or the whole corpus for the long-context arm. A claim is supported if
a candidate chunk entails it, at the same 0.5 threshold and with the same
entailment model the pipeline uses to decide whether a claim carries a
citation, or if the evidence states it literally. The second test is not a
convenience: the entailment model will not endorse a bare "69%" from a chunk
that says 69%, because a bare number is not a proposition, and it *will*
endorse a fabricated bare number against any chunk that happens to contain a
number. Scoring against the arm's own evidence is also what makes the five arms
comparable -- the rule is the same for each of them, and the evidence differs
exactly as the arms differ. One asymmetry in that rule is worth stating: a
retrieval arm's evidence is about ten chunks, so a claim it states from
elsewhere in the corpus counts against it, while the long-context arm's
evidence is the whole corpus, so a claim it states from anywhere counts for it.
**The claim-support column therefore flatters the long-context arm, and the
accuracy and answer-rate columns are the ones to read it against.**

**The instrument is audited, not asserted.**
`impl/experiments/validate_claim_scorer.py` runs the scorer against the focus
benchmark: 32 of the 33 answers the benchmark itself considers correct are recognised as supported by the evidence that states them; 8 of the 9 fabricated values are rejected; and 31 of the 32 values taken from another question's evidence are rejected. Its known limits
are that a bare value that is a single digit cannot be located reliably by a literal test, and every miss on the truth test and every leak on the cross-question test is of that kind; a value the corpus implies but does not state verbatim -- a derived figure -- is scored unsupported, because the evidence does not literally contain it; the entailment model is strict about definitional fragments, which is why the literal test exists alongside it, and lenient about bare numbers, which is why a bare value is not put to it at all.

**The verdict on H2.1 in the cautious condition.** **supported, at a price.** The gate reduced the rate of answering unanswerable questions from **0.535** to **0.417** -- a fall of 11.8 points -- and the framework answered 30 of 32 answerable questions. The reduction is real and it is bought with answerable questions declined, which is the trade the gate was built to make and which is why coverage and correctness are reported as two numbers rather than one.

**The verdict on H2.1 across both conditions.** Conditional: the hypothesis holds under both prompt conditions. Under the cautious prompt -- the deployed system -- it is supported, at a price: the gate reduced the rate of answering unanswerable questions from 0.535 to 0.417, a fall of 11.8 points, at the cost of answering 30 of 32 answerable questions. Paired question by question, the gate refused 23 of the questions the ungated arm answered and let through 6 of the ones it did not (exact McNemar p = 0.002). Under the answering prompt, which differs from the cautious one by a single sentence, it is supported, at a price: the gate reduced the rate of answering unanswerable questions from 0.938 to 0.528, a fall of 41.0 points, at the cost of answering 30 of 32 answerable questions. Paired question by question, the gate refused 60 of the questions the ungated arm answered and let through 1 of the ones it did not (exact McNemar p = < 0.001). What the framework claims is therefore that the gate reduces the rate of answering unanswerable questions whatever the generator does, and that it is the one component whose behaviour does not depend on the generator's cooperation: the prompt can be wrong, and the gate still holds.

The fitted operating point was chosen on this benchmark, so the `rag@fitted` row is the optimistic one; the `rag@transferred` row carries the threshold that the cross-category experiment fitted on its tuning half and moved over unchanged, and it is the honest estimate of what the gate does on questions it was not tuned on. At that stricter threshold the gate refused all 144 unanswerable questions and the answer rate fell to 0.014 -- but it also declined 26 of the 32 answerable ones, so the opportunity was removed by declining more of everything.

**What this does not settle.** The claims are scored by support in the
evidence, which is the right test for fabrication but says nothing about
whether the answer was the *best* answer; the accuracy column is the
answer-side complement to it, and the two are separate questions. A refusal that also asserts something -- "the documents do not contain the demand for this SKU, so the quantity cannot be computed; in general it is computed as ..." -- is counted as an answer and scored on the assertion, and 48 of the unanswerable questions drew one. That is the reading that gives the gate less credit, because a mixed answer raises an arm's answer rate, and the answer rate is what the gate is credited on lowering.
The generator samples at a provider-determined temperature, so the five arms are
compared on rates over a fixed question set rather than on paired per-question
outcomes. The experiment also uses one generator, so what transfers to a generator
outside that set is a question this does not answer.


---

## E.8 The answer side, audited (Experiment 9)

E.7's accuracy column is measured against silver-standard labels, and those
labels are produced mechanically: the builder copies a value out of the gold
chunk when it writes the benchmark. An audit of that step found a defect in
the generator, and the defect was repaired.

**What the defect was.** Two mechanisms in `scripts/build_benchmark.py`
produced it. A table question named the column its *key* came from rather
than the column its *answer* came from: "According to the table in the source
document, what is the DPMO for 691,462?" was answered "69%", which is the
percent-defective column, because the generator took the key from column k and
the answer from column k+1 while naming column k. And a numeric gold could be
a digit prefix of a longer token in the chunk -- "3" out of "3PL", or "6" out
of "6.8".

**How big it was, and what was done about it.** The audit found
**27 of the 132 answerable questions** carrying an answer
attached to the wrong question (20.5% of the answerable set).
 The conservative screen the audit used fires on 30 of them, and the precise rules adjudicate each hit. The
generator was corrected -- a table question now names the column its answer
comes from, and a numeric gold that is only ever a prefix of a longer token
is not generated at all -- the benchmark was rebuilt, and **every experiment in
this project was re-measured against it**. The numbers reported everywhere in
this work are therefore post-repair. The benchmark as it stood before the
repair is kept at `impl/experiments/data/benchmark_pre_repair.json`, so that
the finding stays checkable rather than becoming a story about something that
can no longer be looked at.

**What remains.** The audit runs on the rebuilt benchmark and finds
**0 defective labels out of 32**. Its rules were sharpened in
the process, and the difference is worth stating because it is the difference
between a measurement and a mood: the original screen flagged a label
whenever the gold's digits began *some other* token in the chunk, and it
picked the table row by looking under the column the question named, which is
the wrong row whenever the same value appears in two columns. That screen
still fires on 1 of the 32 questions, and every one of them
was adjudicated: the value is stated by the chunk, and the screen is
over-reporting. The screen is kept, because it is the instrument that found
the defect; the rules that adjudicate each hit are now precise -- a label is
defective only when the chunk never states the gold as a complete token, or
when the gold does not sit in the column the question names in the row the key
names.

**What the defect did and did not affect.** The *gold chunk* was correct in
every defective case -- the question was about the right table or the right
sentence -- so the retrieval-side measurements, which are scored against the
gold chunk, were never affected. Only the answer-side accuracy was depressed,
and it was depressed for every arm equally, because every arm is scored
against the same labels. The unanswerable set, which is what H2.1 rests on,
carries no answer labels at all and was untouched.

**How much of the answer-side result survives.** On the 32 questions
whose labels are sound:

| Arm | Accuracy, all 32 questions | Accuracy, the 32 sound ones |
|---|---|---|
| the same retrieval with the gate removed | 0.633 (30 answered) | 0.633 (30 answered) |
| the framework at the operating point fitted on this benchmark | 0.800 (30 answered) | 0.800 (30 answered) |
| a control that refuses as many questions as the fitted gate did, but picks them at random | 0.714 (21 answered) | 0.714 (21 answered) |
| the framework at the operating point transferred unchanged from the cross-category half | 0.333 (6 answered) | 0.333 (6 answered) |
| the whole corpus in the prompt | 0.548 (31 answered) | 0.548 (31 answered) |

The *direction* of every comparison is unchanged. The *size* of the
long-context gap is not robust: the retrieval arm scores higher than the
long-context arm on every test, but the margin reaches no test's
significance threshold -- p = 0.727 under the
whole-answer entailment test, p = 0.508 under a
length-controlled re-scoring of the same answers, and p =
0.250 under a lexical test that ignores length. The
whole-answer test detects it *least*, and the reason is visible in the answer
lengths: the median long-context answer is 254 characters against the
retrieval arm's 214, and entailment against a short gold answer is
easier to fail the more text the hypothesis is embedded in -- so the length
artefact works *against* the retrieval arm here, and even with that handicap
the gap is directional only. **The long-context comparison should therefore
be read as settled on coverage and cost, and as directional but not
statistically significant on answer quality.** The correction is to the size
of a claim, not to its direction.

**And one thing the accuracy column cannot settle at all.** Two independent
correctness tests are reported for every arm --- the NLI test and the
key-term test --- and they do not agree about which arm is best. In the
cautious condition the NLI test puts the fitted gate first
(0.800 against 0.633 for the ungated pipeline) while
the key-term test puts the ungated pipeline first, by the thinnest margin
that can be measured (0.900 against 0.867); in the
answering condition the order reverses. **The answer-accuracy column is
therefore not a basis for saying the gate makes answers more accurate** ---
the sign of that comparison depends on which of the two reported tests is
read. Everything the gate is actually claimed on is invariant to the choice:
the coverage, the cost, the refusal of questions it should refuse, the
claim-support figures, and every retrieval measurement. The full
sensitivity analysis, and the answer-validation protocol set against the
published benchmarks, are in `research/15_label_validation_protocol.md`.

### E.8.1 How much of the accuracy column is the scoring convention?

The paragraph above says the two shipped tests disagree about which arm is
best. That is a statement about two numbers. The question underneath it is
how much of the column is the *convention* rather than the *system*, and it
is answerable without re-running anything: the generator's answers and the
benchmark's gold strings are both already in the shipped records, so the same
answers can be scored under any convention at all.

Five conventions were applied to the same shipped answers. Two are the
shipped ones -- whole-answer entailment and the lexical key-term test. Three
are taken from the published benchmarks: SQuAD 2.0's normalised exact match
and its token-level F1, and PopQA's containment rule.

**The two shipped tests agree at close to chance.** Question by question,
they give opposite verdicts on between 19% and 67% of
the answered questions, and Cohen's kappa between them runs from
0.00 to 0.21 -- at or below the agreement Cohen called
"slight". They are not one measurement reported two ways; they are two
different measurements, and the column reports both because either one alone
would decide the result.

**The absolute level is a property of the convention.** On the ungated arm
in the deployed condition, the same answers score:

| Convention | Score on the same answers |
|---|---|
| SQuAD 2.0 normalised exact match | 0.133 |
| PopQA containment | 0.367 |
| SQuAD 2.0 token-level F1 (mean, not thresholded) | 0.452 |
| whole-answer entailment | 0.633 |
| lexical key-term test | 0.867 |

The four binary conventions span 0.73 between them on this arm --
from 0.133 to 0.867 -- which is larger than any
margin the generator-side comparison reports, and the widest spread over all
arms and both conditions is 0.90. And on between 4 and
27 answered questions per arm, the verdict depends on which
convention is read.

**That is not a defect of the answers, and it is not a defect of the
labels.** SQuAD's exact match is designed for short extractive spans; this
benchmark's golds are full extracted sentences and the generator's answers
are full sentences, so string equality almost never holds. A convention that
does not fit the answer form is a fact about the answer form, and it is why
the accuracy column is reported as a comparison between arms rather than as
a level to be quoted.

**What the measurement settles.** Two things, and they are the two things
the rest of this work rests on.

1. **No arm comparison on the answer side reaches significance under more
   than one convention.** The gate-against-no-gate comparison reaches no
   convention's threshold in either condition -- 0 of 5 in the cautious
   condition and 0 of 5 in the answering one. The
   retrieval-against-long-context comparison reaches 1 of 5 in the
   cautious condition and 2 of 5 in the answering one, so the two
   conditions disagree about a comparison this report already calls
   directional, which is the honest description of it.
2. **Everything the gate is claimed on is invariant.** The coverage, the
   cost, the refusal of questions it should refuse, the claim-support
   figures and every retrieval measurement are computed from counts and
   from the evidence rather than from the answer string, so they are
   identical under all five conventions. That is what makes the gate's
   claim rest on the measurements that do not depend on the convention.

**What it does not settle.** An LLM judge on semantic equivalence --
BrowseComp's rule, and the fifth convention in the literature -- was **not**
applied: it needs a judge prompt, a second generator and a budget that is
not available for a question this measurement already answers for the
lexical family. Nor can five conventions make one of them right. That needs
human annotation of the benchmark's own gold answers, which is the largest
open item in the thesis.

The measurement is `impl/scripts/answer_validation_conventions.py`; its
output is `impl/results_focus/exp8_answer_validation_conventions.json`, and
the write-up is `research/18_answer_validation_conventions.md`.

**What this section is for.** It is the same argument the rest of the work
makes, applied to the project's own instrument: a measurement that is not
audited is an assertion, and when the audit finds something, the finding is
published, the instrument is repaired, and everything is re-measured. The
benchmark, the corpus and the label standard are otherwise unchanged; what
changed is the generator's column indexing, and every number in this project
was taken again afterwards.


---

## E.9 The unanswerable half: audited, found defective, and rebuilt (Experiment 12)

### E.9.1 The finding: the two classes were separable from the question alone

E.8 audited the *answerable* half: a defect class was found, repaired, and
every number in this report was taken again afterwards. The unanswerable half
had no audit, and that was a gap rather than a certainty. The unanswerable
questions are *supposed* to have no answer, so the ways the half can be wrong
are invisible to every retrieval metric in this report: retrieval metrics
score the answerable half against gold chunks, and the unanswerable half
contributes nothing to them. The audit found one serious defect and one
harmless one.

**The two classes were separable from the question alone.** A classifier that
sees the query and nothing else -- no retrieval, no evidence, no reasoning
about the corpus -- told the answerable questions from the unanswerable ones
at an ROC AUC of **0.999** on the question's shape, and
**0.985** when it was allowed to use the question's
words.

The mechanism is not subtle, and it is a property of how the benchmark was
built rather than of the corpus. The unanswerable half's designated hard case
asked about an identifier that is verified absent from the corpus -- *What is
the economic order quantity for SKU AST-5454?* -- and **every one of those
questions contains a token of the form PREFIX-digits, while not one of the
32 answerable questions contains one.** A single
regular expression therefore separates the two classes: it catches
**76.4%** of the unanswerable class with no false
positives at all.

It is worth stating what the generator's own comment claimed, because the
first half of it was false. The family was described as having *"the same
surface form as answerable questions but name an identifier that is verified
absent from the corpus. This is the hard case."* It did not have the same
surface form. The family used
a fourth question stem -- *What is the {metric} for {code}?* -- that no
answerable question uses, and it named its subject with an identifier shape
that only it used.

**What this did and did not invalidate.** It did not touch the retrieval-side
results, which are scored against gold chunks. It did not touch Experiment 8's
arm comparison either, because every arm is asked the same questions, so a
template artefact cancels in the difference. What it did bound was the
**headline refusal rate**: the gate's refusal rate was measured on questions
whose unanswerability was visible in the question string, so a system that
refused on the shape of the question rather than on the content of the
evidence would have scored the same. The rate was an upper bound rather than a
measurement.

The second finding is harmless. The out-of-domain family -- questions about
vitamin D and the FIFA World Cup -- is trivially unanswerable for any system
that knows what the corpus is about, and a classifier separates it from the
answerable class almost perfectly. That is not a defect; it is what an
off-topic question is. It is reported separately from here on, because a
refusal rate pooled over it and over the hard case is an upper bound on both.

### E.9.2 The repair: a corpus-anchored unanswerable class

The half was rebuilt, not merely re-described, and the pre-repair benchmark
is preserved beside the repaired one so that every number below can be
checked against it. Four decisions, each of which was necessary and each of
which was found by measurement rather than by argument:

**The same question stems.** The repaired class uses the answerable class's
own three stems -- *What is {subject}?*, *What value is stated for
{subject} in the source documentation?*, and *According to the table in the
source document, what is the {column} for {row}?* -- in the answerable
class's own proportions. A question stem that appears in one class and not the
other is a giveaway on its own.

**The same source documents.** The answerable half is not spread over the
corpus: its 32 questions come from
10 source documents, and the largest
of them contributes 8 of them
(25% of the half). Drawn from the
whole corpus, the repaired class was a different sample of topics, and a
classifier separated the two classes by topic rather than by answerability.
Restricted to the documents the answerable class came from -- and matched on
the shape cells and the subject lengths as well -- that went away.

**The same label machinery.** The answerable classes are labelled by the
benchmark's own extraction branches -- the definition branch finds a
definition, the numeric branch finds a value, a table cell holds the answer --
and the repaired class is labelled by the complement of exactly those tests.
Each repaired question carries a certificate naming the test it passes, and
the audit re-checks every certificate against the corpus with a predicate
written independently of the generator: **1
of 110** failed.

A near-miss probe is reported beside it, and it measures something different.
The label standard calls a question answerable when the corpus *defines* its
subject -- a subject, a copula and an article. That is a mechanical rule, and
it cannot see a subject the corpus says something about without defining it:
*"The model was based on a linear regression model"* is not a definition by the
standard's pattern, but it does answer *What is the model?* The near-miss
probe counts the questions whose subject the corpus comments on without
defining it: **43 of
110**. They are the class's character,
not a failure of the certificate, and they are what "unanswerable" means in a
benchmark whose labels are mechanically derived: the corpus discusses the
subject and does not state the answer. What they bound is the absolute
refusal rate, which is therefore measured on a class that is partly
answerable in a human's sense. They do not bound the arm comparison, in
which every arm is asked the same questions.

**The same shape.** Each repaired question was drawn so that it has a
*structural twin* in the answerable class: the same stem, the same subject
size, the same shape markers -- whether the subject contains a digit, an
acronym, a capitalised head or an opening article -- and no word in common.
**106 of 110** of the repaired
questions have such a twin. This is the size-matched construction of the
evidence-sufficiency literature, applied to question shape instead of passage
count.

### E.9.3 The re-measurement

The same measurements, taken again.

| | before the repair | after the repair |
|---|---|---|
| one-rule shortcut, share of the unanswerable class it carries | 76.4% | **0.0%** |
| separability from the question's *shape* (ROC AUC) | **0.999** | **0.608** |
| separability from the question's *words* (ROC AUC) | 0.985 | 0.646 |

The shape-only classifier now scores an F1 of **0.342**
against a majority-class baseline of 0.000, and an
ROC AUC of **0.608** against a permutation null of
0.468 that the same procedure produces when the
labels are shuffled (p = 0.050). The shortcut that
carried 76.4% of the class now carries
0.0%.

The same audit on the six-category benchmark, where the answerable class is
four times larger and a form-only classifier therefore estimates the shape
cells from more data, is the better-powered measurement of the same property:
**0.533** against a permutation null of 0.500 (p = 0.267), which
is not distinguishable from chance, and all 110 of 110 of the corpus-anchored
questions have a structural twin in the answerable class. The focus domain's
figure above is
the noisier one, and the gap between the two is what a small answerable class
does to a cell-based estimate.

**A question-only policy, measured rather than fitted.** The sharpest version
of the question is whether a *system* could refuse without reading any
evidence. A model was given the question and nothing else -- no documents --
and asked whether a standard industrial engineering documentation set would
contain the answer. This is the hypothesis-only baseline of the answerability
literature.

Its *discrimination* is the number to read, because the detection rate alone
is misleading: a policy that refuses everything detects every unanswerable
question and answers no answerable one. The ROC AUC over the two classes is
**0.675** on the pre-repair benchmark and
**0.564** on the repaired one, where 0.5 is no
discrimination at all. The policy flags
94.4% of the pre-repair class as
unanswerable and 72.2% of the repaired one, but it
pays for that: it refuses 59.4% of the
answerable class before the repair and 59.4% after, so
as an abstention rule it is not usable on either.

The comparison is the point. On the defective class a policy that never read
a document came within a little of the fitted gate; on the repaired class the
question no longer carries the answer, and the gate's refusal has to come
from the evidence.

### E.9.4 What the refusal rate is now

The unanswerable class is not homogeneous, and the headline is now reported by
stratum. At the fitted operating point of tau = 0.05,
the gate refuses **23.6%** of the corpus-anchored
questions (26 of 110) -- the
questions the corpus discusses but states no value for, which is the case the
gate is being tested on -- and 76.5% of the
out-of-domain ones (26 of 34).
The pooled refusal rate over the whole class,
36.1%, remains an upper bound on what the gate
would achieve on a question stream whose unanswerable questions are phrased
like answerable ones -- and, read against the near-miss count above, a lower
bound on what a reader who could answer the class's softer questions would
get.

### E.9.5 Where this sits in the literature

The same artefact has been reported in the same task for a clinical
question-answering benchmark, where the unanswerable questions could be
discerned by filtering on surface n-gram patterns and the evaluation was
thereby compromised (Yang et al., 2024, arXiv:2405.01588); the
shortcut-removal construction used here is the one applied to
insufficient-evidence examples elsewhere, where a classifier that only counts
paragraphs reaches AUROC 0.979 before the construction and the matched one
provably removes it (Mondal et al., 2026, arXiv:2609.32269); and framing a
benchmark repair as the contribution rather than as a footnote follows the
precedent of a paper whose title names the repair (Brunello et al., 2026,
arXiv:2606.02837). Recombining answerable questions into unanswerable ones by
antonym and entity swaps is itself an established generation method (Gautam
et al., 2023, arXiv:2310.19403).

What is not reported anywhere is the question-only separation of an
answerable/unanswerable split in a RAG *refusal* benchmark, its effect on the
reported refusal rate, and a repair by regenerating the unanswerable class
with answerable-style templates.

### E.9.6 The unanswerable questions are not memorised

With the corpus removed from the prompt entirely, the generator answers
substantively **97.9%** of
the unanswerable questions -- against
**96.9%** of
the answerable ones. The two rates are the same to within a point, so the
model's closed-book behaviour carries no information about whether a question
is answerable from the corpus: it answers both classes alike. What that rules
out is the contamination one would most fear -- the unanswerable half being
made of questions the model happens to know.

**The closed-book answers to the answerable questions are wrong 90.6% of the time** (accuracy 0.094 against the same gold the retrieval arms are scored against), which is the other half of the same finding: the model does not reproduce the corpus's values either, it simply answers. That is also why the answerable class is the right control here -- a closed-book rate that differed sharply between the two classes would have meant the unanswerable half was made of questions the model happens to know, and it is not.

The near-unity closed-book answer rate is worth reading on its own, because it
is the behaviour the whole framework exists to catch: asked a question with no
corpus at all, the generator supplies a confident, plausible answer almost
every time. The unanswerable questions are not unanswerable *for the model* --
they are unanswerable *from this corpus*, which is the right label for them and
the reason the evidence trail matters.


### E.9.7 The same audit on the industrial corpus

The industrial corpus's unanswerable half was built after the repair, so there
is no "before" for it to be compared against — but it can be audited the same
way, and it is the corpus the framework's headline conflict result rests on,
so the two probes matter more here, not less.

**The question-only policy.** A model given the question and nothing else -- no documents, no evidence -- and asked whether a standard industrial engineering documentation set would contain the answer, separates the two classes at an ROC AUC of **0.478** — below the 0.5 that would mean a coin toss, and so at no discrimination at all. It flags 66.5% of the unanswerable class and pays for that by refusing 70.9% of the answerable one. **A policy that never reads a document is not usable as an abstention rule on this corpus either**, which is the result the focus corpus's repair was supposed to produce.

**The parametric-leakage probe.** Asked the same questions with no corpus in the prompt at all, the generator answers substantively **95.9%** of the unanswerable questions and **95.5%** of the answerable ones. The two rates are the same to within a point, so the model's closed-book behaviour carries no information about whether a question is answerable from this corpus: it answers both classes alike. What that rules out is the contamination one would most fear -- the unanswerable half being made of questions the model happens to know. The closed-book answers to the answerable questions are wrong 86.2% of the time (accuracy 0.138 under the entailment test and 0.251 under the key-term test, against the same gold the retrieval arms are scored against), which is the other half of the same finding: the model does not reproduce the corpus's values either, it simply answers.

**And one honest negative about this corpus's repaired class.** The form-only separability that the repair was supposed to remove is not entirely gone here: the same procedure reaches an AUC of **0.708** on the industrial corpus (p = 0.010 against the permutation null), and **0.793** on the question's words alone (p = 0.032). On the better-powered six-category corpus the same measurement is indistinguishable from chance: AUC 0.533 (p = 0.267). On the focus domain it rejects the null only weakly, at AUC 0.608 (p = 0.050); on the industrial corpus it does not. **The repair removed the one-rule shortcut — the fabricated identifier, which now carries none of the class — and it did not leave the industrial class free of every weaker form of separability.** That is a property of this corpus's questions, not of the repair, and it bounds what the industrial refusal rate means: it is measured on a class that a careful reader could partly anticipate.


---

![Figure 5. A classifier that sees only the question text, with no retrieval, no evidence and no corpus, telling an answerable question from an unanswerable one. Before the repair the two classes were separable almost perfectly on the focus corpus (ROC AUC 0.999, against a permutation null of 0.455 +/- 0.072), and one regular expression for a fabricated identifier caught 76.4% of the unanswerable questions with no false positive at all. After the repair the shortcut catches nothing, and what is left of the procedure's power is small but not zero: AUC 0.608 on the focus corpus (p = 0.050) and AUC 0.708 on the industrial corpus (p = 0.010). On the better-powered six-category corpus it is indistinguishable from chance: AUC 0.533 (p = 0.267). The benchmark's unanswerable class is decidable from the evidence rather than from a question-shape rule, but on two of the three corpora it is not free of form-only separability.](figures/fig5_question_only_roc.pdf)


## E.10 The focus domain: supply chain management, before and after

The multi-category evaluation above is the statistically strongest result.
The focus domain is where the framework is *shown*, on questions a supply
chain practitioner would actually ask, with every intermediate artefact
written out: the two retrieval legs, the fused ranking, the reranked
ranking, the gate's decision and the signals behind it, which chunks the
quota swapped, how each claim was banded, and whether any two accepted
chunks contradict each other.

The point of the section is not another number. It is the evidence that the
architecture changes the *outcome* on a real question, and that every change
is attributable to a named mechanism.


Focus domain: **supply_chain_management**. 32 answerable questions and 144 deliberately unanswerable ones.

## The aggregate before/after

| | Plain BM25 retriever | The full framework |
|---|---|---|
| Answerable questions answered | 32 | 30 |
| Unanswerable questions answered (wrongly) | **144** | **86** |
| Gate refusal rate on answerable questions | 0.0% | 6.2% |
| Gate refusal rate on unanswerable questions | 0.0% | 40.3% |
| Context contains the gold chunk (answerable questions) | 96.9% | 93.8% |
| Mean chunks in the accepted context | — | 9.4 |

**This is the before/after that matters.** A retriever that never refuses answers every unanswerable question, and every one of those is a wrong answer dressed as a right one. The framework's cost is the answerable questions it declines; its benefit is the unanswerable ones it stops answering. Note that the framework is *not* better at putting the gold chunk in the context -- on silver-standard labels a plain lexical retriever already does that -- and that is the point: the gate is not there to retrieve better, it is there to refuse.

## Per-question before and after

| Question | Family | BM25-only found gold (top-10) | Full framework accepted gold | Gate decision |
|---|---|---|---|---|
| What is freight transportation? | definition | yes | yes | answered |
| According to the table in the source document, what is the Contr… | table_lookup | yes | yes | answered |
| What is inbound logistics? | definition | yes | yes | answered |
| What value is stated for the purpose in the source documentation… | numeric_fact | yes | no | REFUSED |
| What value is stated for SF handled a total in the source docume… | numeric_fact | yes | yes | answered |
| According to the table in the source document, what is the Suffi… | table_lookup | yes | yes | answered |
| What are kanban cards? | definition | yes | yes | answered |
| What is the rope? | definition | yes | yes | answered |
| What is outbound logistics? | definition | yes | yes | answered |
| What is regression analysis? | definition | yes | yes | answered |
| According to the table in the source document, what is the Perce… | table_lookup | yes | yes | answered |
| According to the table in the source document, what is the Suffi… | table_lookup | yes | yes | answered |
| What is the sourcing plan? | definition | yes | yes | answered |
| What is the theory of constraints? | definition | yes | yes | answered |
| What is a sourcing business model? | definition | yes | yes | answered |
| What is six Sigma? | definition | no | yes | answered |
| What is operations research? | definition | yes | yes | answered |
| According to the table in the source document, what is the Compu… | table_lookup | yes | yes | answered |
| What are sourcing Business Models? | definition | yes | yes | answered |
| What is an RFID tag? | definition | yes | yes | answered |
| What is the drum? | definition | yes | yes | answered |
| According to the table in the source document, what is the Contr… | table_lookup | yes | yes | answered |
| What is logistics management? | definition | yes | yes | answered |
| What is since manufacturing in an existing plant? | definition | yes | yes | answered |
| According to the table in the source document, what is the Greel… | table_lookup | yes | yes | answered |
| What value is stated for a rule of thumb in the source documenta… | numeric_fact | yes | no | REFUSED |
| According to the table in the source document, what is the Perce… | table_lookup | yes | yes | answered |
| What is safety stock? | definition | yes | yes | answered |
| What is a prominent example? | definition | yes | yes | answered |
| What is the constraint? | definition | yes | yes | answered |
| What is the average annual variable cost? | definition | yes | yes | answered |
| What is the Chartered Institute? | definition | yes | yes | answered |

## Four questions traced end to end

### A table lookup question

**Question.** According to the table in the source document, what is the Contribution for John Krafcik?

**Before — plain BM25, top 5 of 10:**
      - `just-in-time-manufacturing::p1::tbl36` [table] **<-GOLD**: [TABLE] just-in-time-manufacturing section Key figures | Person | Contribution | | --- | --- | | W. Edwards Deming | Developed statistical quality methods; introduced mod…
      - `kanban::p1::t18` [text]: monitoring of these rules is a never-ending task, thereby ensuring that the kanban does what is required. ### Toyota's six rules Toyota has formulated six rules for the a…
      - `just-in-time-manufacturing::p1::t18` [text]: Oregon, after 40 hours of ZIPS training, workers reduced a week's lead time at a stroke — "things ran smoother" — and ZIPS spread through operations "like an amoeba." At …
      - `theory-of-constraints::p1::tbl49` [table]: [TABLE] theory-of-constraints section Thinking processes | | Sufficient thinking ("If… then") | Necessary thinking ("In order to…we must") | | --- | --- | --- | | What to…
      - `six-sigma::p1::t69` [text]: but there is some way to go to document these empirically and clarify the causal relations.

**After — the full framework:**

  - fused top-10: `just-in-time-manufacturing::p1::t18`, `six-sigma::p1::t69`, `bill-of-materials::p1::tbl3`, `just-in-time-manufacturing::p1::tbl36`, `six-sigma::p1::tbl8` …
  - reranked top-10: `just-in-time-manufacturing::p1::tbl36`, `just-in-time-manufacturing::p1::t18`, `bill-of-materials::p1::tbl3`, `six-sigma::p1::tbl8`, `strategic-sourcing::p1::t24` …
  - gate: accepted
  - top posterior: 0.0788
  - gate signals: [-0.935, -4.614, 16.694, 0.031, 0.0]
  - modality mix of the accepted context: {'text': 4, 'table': 5, 'chart': 1}

  Accepted context, first 5:
      - `just-in-time-manufacturing::p1::tbl36` [table] **<-GOLD**: [TABLE] just-in-time-manufacturing section Key figures | Person | Contribution | | --- | --- | | W. Edwards Deming | Developed statistical quality methods; introduced mod…
      - `just-in-time-manufacturing::p1::t18` [text]: Oregon, after 40 hours of ZIPS training, workers reduced a week's lead time at a stroke — "things ran smoother" — and ZIPS spread through operations "like an amoeba." At …
      - `bill-of-materials::p1::tbl3` [table]: [TABLE] bill-of-materials section body | | | | --- | --- | | icon | This article **needs more citations**. Please help improve this article by adding citations to reliabl…
      - `six-sigma::p1::tbl8` [table]: [TABLE] six-sigma section body | | | | --- | --- | | icon | This article **needs more citations**. Please help improve this article by adding citations to reliable source…
      - `strategic-sourcing::p1::t24` [text]: (identifier)") 978-3-8350-0946-2 - Payne, Joe and Dorn, William, Managing Indirect Spend: Enhancing Profitability Through Strategic Sourcing, John Wiley & Sons, Inc., 201…

### A numeric fact question

**Question.** What value is stated for the purpose in the source documentation?

**Before — plain BM25, top 5 of 10:**
      - `six-sigma::p1::t42` [text] **<-GOLD**: would've seen a drastic decrease of proportions corresponding to a 7.5σ level. In contrast, a true 4.5σ process would have the 4.5σ level on both sides, corresponding to …
      - `logistics::p1::t34` [text]: service(s) related to the disposal of waste produced during a business's operation. - Reverse logistics denotes all operations related to the reuse of products and materi…
      - `just-in-time-manufacturing::p1::t22` [text]: Womack and Jones define Lean as "a way to do more and more with less and less—less human effort, less equipment, less time, and less space—while coming closer and closer …
      - `six-sigma::p1::t58` [text]: A Fortune "Fortune (magazine)") article stated that "of 58 large companies that have announced Six Sigma programs, 91% have trailed the S&P 500 since". The statement was …
      - `kanban::p1::t17` [text]: it is used as a demand signal that immediately travels through the supply chain. This ensures that intermediate stock held in the supply chain are better managed, and are…

**After — the full framework:**

  - fused top-10: `six-sigma::p1::t42`, `six-sigma::p1::t43`, `incoterms::fig2`, `logistics::p1::t34`, `demand-forecasting::p1::t44` …
  - reranked top-10: `six-sigma::p1::t43`, `six-sigma::p1::t42`, `logistics::p1::t34`, `just-in-time-manufacturing::p1::t22`, `six-sigma::p1::t58` …
  - gate: REFUSED — No evidence in the indexed documentation supports an answer to this question. The retrieval-confidence gate rejected the retrieved passages (calibrated sufficiency probability 0.034 < threshold 0.050). No answer has been generated, because generating one would mean inventing it.
  - top posterior: 0.0339
  - gate signals: [-7.262, -7.92, 12.392, 0.032, 0.0]
  - modality mix of the accepted context: {'text': 7, 'chart': 1, 'table': 2}

  Accepted context, first 5:
      - (nothing accepted)

### A definition question

**Question.** What is freight transportation?

**Before — plain BM25, top 5 of 10:**
      - `logistics::p1::t92` [text]: - Automated identification and data capture – Methods of automatically identifying objects by computer systemPages displaying short descriptions of redirect targets - Doc…
      - `logistics::p1::t28` [text]: Loading of a thermal oxidizer in preparation for its transport to a manufacturing plant A forklift truck loads a pallet of humanitarian aid to Pakistan on board a C-17 ai…
      - `third-party-logistics::p1::t20` [text]: quoting, financial settlement, auditing, tracking, customer service and issue resolution. However, they do not employ any truck drivers or warehouse personnel, and they d…
      - `logistics::p1::t29` [text] **<-GOLD**: technologies such as bar code scanning and computers, the availability of stocks can be checked in real time. The purpose of having an inventory is to reduce the overall …
      - `logistics::p1::t66` [text]: semi-trailers. Especially for very long distances, product transportation will likely benefit from using different transportation means: When moving cargo, typical constr…

**After — the full framework:**

  - fused top-10: `logistics::p1::t28`, `logistics::p1::t66`, `third-party-logistics::p1::t37`, `incoterms::p1::t36`, `logistics::p1::t29` …
  - reranked top-10: `logistics::p1::t29`, `incoterms::p1::t13`, `logistics::p1::t28`, `third-party-logistics::p1::t37`, `logistics::p1::t66` …
  - gate: accepted
  - top posterior: 0.2057
  - gate signals: [5.063, 3.254, 8.245, 0.032, 5.0]
  - modality mix of the accepted context: {'text': 7, 'table': 2, 'chart': 1}

  Accepted context, first 5:
      - `logistics::p1::t29` [text] **<-GOLD**: technologies such as bar code scanning and computers, the availability of stocks can be checked in real time. The purpose of having an inventory is to reduce the overall …
      - `incoterms::p1::t13` [text]: to perform or to procure the performance of transport by rail, road, air, sea, inland waterway or by a combination of such modes - Freight forwarder: A firm that makes or…
      - `logistics::p1::t28` [text]: Loading of a thermal oxidizer in preparation for its transport to a manufacturing plant A forklift truck loads a pallet of humanitarian aid to Pakistan on board a C-17 ai…
      - `third-party-logistics::p1::t37` [text]: - Freight - Shipping
      - `logistics::p1::t66` [text]: semi-trailers. Especially for very long distances, product transportation will likely benefit from using different transportation means: When moving cargo, typical constr…

### A question the gate refused

**Question.** What value is stated for the purpose in the source documentation?

**Before — plain BM25, top 5 of 10:**
      - `six-sigma::p1::t42` [text] **<-GOLD**: would've seen a drastic decrease of proportions corresponding to a 7.5σ level. In contrast, a true 4.5σ process would have the 4.5σ level on both sides, corresponding to …
      - `logistics::p1::t34` [text]: service(s) related to the disposal of waste produced during a business's operation. - Reverse logistics denotes all operations related to the reuse of products and materi…
      - `just-in-time-manufacturing::p1::t22` [text]: Womack and Jones define Lean as "a way to do more and more with less and less—less human effort, less equipment, less time, and less space—while coming closer and closer …
      - `six-sigma::p1::t58` [text]: A Fortune "Fortune (magazine)") article stated that "of 58 large companies that have announced Six Sigma programs, 91% have trailed the S&P 500 since". The statement was …
      - `kanban::p1::t17` [text]: it is used as a demand signal that immediately travels through the supply chain. This ensures that intermediate stock held in the supply chain are better managed, and are…

**After — the full framework:**

  - fused top-10: `six-sigma::p1::t42`, `six-sigma::p1::t43`, `incoterms::fig2`, `logistics::p1::t34`, `demand-forecasting::p1::t44` …
  - reranked top-10: `six-sigma::p1::t43`, `six-sigma::p1::t42`, `logistics::p1::t34`, `just-in-time-manufacturing::p1::t22`, `six-sigma::p1::t58` …
  - gate: REFUSED — No evidence in the indexed documentation supports an answer to this question. The retrieval-confidence gate rejected the retrieved passages (calibrated sufficiency probability 0.034 < threshold 0.050). No answer has been generated, because generating one would mean inventing it.
  - top posterior: 0.0339
  - gate signals: [-7.262, -7.92, 12.392, 0.032, 0.0]
  - modality mix of the accepted context: {'text': 7, 'chart': 1, 'table': 2}

  Accepted context, first 5:
      - (nothing accepted)


## E.11 A second corpus: authentic, versioned, binding industrial text

**E.11.1 What it is, and why it was built.** RO4 needed a corpus that
*contains* conflicts; RO6 needed a corpus that is *authentic*. Federal
regulation is both. It is binding text with numeric requirements, and it
gets amended -- so the Electronic Code of Federal Regulations serves the
same section as it stood on any past date, and the same provision read at
two issues **is** a conflict, with its type known by construction and no
annotation required.

The corpus is 110 documents, 2,443 chunks
(2,324 text, 119
table, 0 chart), in four regulatory
regimes: OSHA general industry, OSHA process safety and EPA risk management,
EPA new source performance standards, and DOT hazardous materials. It is
**public domain** -- United States federal regulations are works of the
United States government -- so it removes the licence question the
limitation table names as the remediation, and it ships with the corpus
snapshot, the source date and the build script.

Its benchmark has **444 queries**
(247 answerable, 197 unanswerable) in six
families, and it was audited for the same shortcut that the first benchmark
had:

The original `PREFIX-digits` shortcut, which carried 76.4% of the *first*
benchmark's unanswerable class, catches **0 of
197** here. A question-only classifier separates the two
classes at ROC AUC 0.708 against a permutation null of
0.505: the class is *easier* than the first
benchmark's on one axis and *harder* on another, and the residual is length
(median question length 73
characters for answerable against
50 for unanswerable),
which is reported rather than hidden.

**E.11.2 RO6: the negative findings replicate on authentic text.**

| Finding | Δ Recall@10 | p | n |
|---|---|---|---|
| **BM25 beats the dense encoder** | -0.081 | **0.00026** | 247 |
| Fusion against its own lexical leg | +0.000 | 1.000 | 247 |
| The category pre-filter against no filter | +0.000 | 1.000 | 247 |

The BM25 result is the one that matters *for this pipeline*: on the focus
corpus it rested on 32 answerable queries at p = 0.025, and here it is three
times the effect size and twenty-five times the significance, so it is not an
artefact of a small sample. That lexical retrieval beats a general-purpose
dense encoder on legal and financial text is **already published** -- three
times, in three jurisdictions -- so it is not claimed as new here. What is new
is the corollary: on this corpus the lexical leg carried the pipeline and
**neither the fusion nor the category pre-filter added anything measurable on
top of it**. That is what the *shipped* framework's design assumed otherwise.

**The candidate-pool curve is no longer saturated**, which is what lets the
lead claim be measured rather than inferred. At pool 50,
Recall@20 = 1.000 while Recall@10 = 0.988:
1.21% of the golds are
found and then pushed **out of the ten-chunk context** by distractors. On the
focus corpus the curve was flat from pool 10, so the thesis could not
distinguish "the pool stopped helping" from "the corpus had nothing left to
find".

**E.11.3 RO4: it finds the conflicts and reports them as the wrong kind.**
240 pairs -- 90 amended-paragraph pairs and 150 retriever-neighbour pairs --
read by a panel of domain specialists, one per regulatory regime, plus a
generalist control, blind to the detector.

| | Value |
|---|---|
| **Detection precision** (is the alarm pointing at something real) | **0.659** (CI 0.505–0.784) |
| … on the stratum where the conflicts actually are | **0.897** |
| **Typing precision** (is the branch that raised it the branch that owns the conflict) | **0.073** (CI 0.025–0.194) |
| Under the *shipped* operations vocabulary | detection 0.650, typing 0.000 |
| Against the construction labels, where nothing is judged | detection 1.000, typing 0.000 |

The mechanism **finds** the conflicts -- and **types** them wrongly. It
reports supersessions as contradictions, and it cannot tell the practitioner
which version is in force, because nothing in the retrieved passages says
which issue either of them is. That is the one thing a practitioner needs
from a contradiction detector on a regulatory corpus, and it is exactly what
the mechanism does not deliver.

**E.11.4 RO5: the per-claim band, replicated on a second corpus with the
same generator.** The provider that produced the focus corpus's answers hit
its token-plan limit, so the first industrial replication had to use a
different generator on 73 claims and was underpowered. It was re-run with the
same generator, the shipped prompt, and all 247 answerable questions.

| | Gold evidence | Retrieved evidence |
|---|---|---|
| claims labelled | 294 of 318 | 316 of 318 |
| Band vs reference (Cohen's kappa, binary) | **0.062** (CI -0.021, 0.145) | **0.044** (CI -0.036, 0.124) |
| `grounded` / `inferred` / `uncertain` error rate | 0.069 / 0.088 / 0.156 | 0.047 / 0.066 / 0.105 |
| Answers with no wrong claim | 90.4% | 92.7% |
| ... keeping only the `grounded` claims | 95.4% | 96.7% |

**The finding replicates on both protocols.** Against an independent reference
the band is again at chance, and the three bands are again ordered on the
evidence the band saw: the band measures whether the retrieved passages
entail the claim, and that is not the same question as whether the claim is
true. The *positional* comparison -- "keep the first claims of an answer" --
is the evidence for that reading rather than the finding itself, because of
the four measurements: only the focus corpus's gold evidence gives a
significant positional result (p = 0.008; the other three are p = 0.417,
p = 0.083 and p = 0.317).

**E.11.5 The measurement's binding constraint was the annotation, and it
was the rubric.** The comparison above was confounded: the old-rubric reader
was a generalist, so "old rubric" and "generalist" were the same cell. A
2x2 factorial separates them, with the pairs, the detector and the regime
briefs held constant:

| Cell | rubric | detection precision | typing precision |
|---|---|---|---|

| generalist | v1 | **0.293** | 0.073 |

| generalist | v2 | **0.659** | 0.073 |

| specialist | v1 | **0.341** | 0.073 |

| specialist | v2 | **0.659** | 0.073 |


| Effect | Value |
|---|---|
| **Rubric**, at the generalist | **+0.366** |
| **Rubric**, at the specialist | **+0.317** |
| **Specialisation**, at the old rubric | **+0.049** |
| **Specialisation**, at the new rubric | **+0.000** |

**The rubric's wording moved the measured precision by about a third of a
point; the reader's domain specialisation moved it by almost nothing.** The
mechanism is concrete: the old rubric required a version marker, and a
regulation does not write its own version in its text, so it missed
63 of the
82 supersessions it was asked
to find, calling them `no_conflict` rather than something else.

This is a result about *measurement*, and it is the one a reader of this
thesis should take most seriously: a number that moves by a factor of nine
with the wording of its own rubric is not yet a measurement of the thing
under test, and a panel of domain specialists is not what fixed it.

## E.12 What the experiments say, together

The 10 conclusions below are **generated from the measured
comparisons**, not written by hand, so they cannot disagree with the tables
above. Where a comparison is not statistically significant, this says so.

1. **Fusion beats both legs alone.** Dense-only retrieval reaches R@10 0.812; fusing it with BM25 reaches 1.000 (p = 1.4e-02), a gain of +0.188 over the dense leg and +0.031 over the lexical one, and it orders better too: nDCG@10 0.847 against BM25's 0.792, MRR 0.798 against 0.736. This is a change of sign: with the previous, general-purpose sentence encoder the fusion was *worse* than the lexical leg on ordering, because RRF gives the two legs equal say and the weak one spends the strong one's slots. A retrieval-trained encoder fixes that. The generalisable point: a hybrid is only as good as its weaker leg, and the weaker leg's cost is invisible unless you measure the legs separately.
2. **On this corpus the reranker buys nothing.** Its effect is Recall@10 -0.031 (p = 0.32, not significant at the 0.05 level), MRR -0.003 and nDCG@10 -0.011 — flat to slightly down on all three. On the six-category corpus the same reranker does buy ordering: MRR 0.666 to 0.776 and nDCG@10 0.730 to 0.814, with recall unchanged at 0.932. A cross-encoder can only permute the chunks it was given, so it cannot bring in evidence the first stage discarded; what it buys depends on how much there is to reorder, and on a single-category corpus with 32 answerable questions and a silver-standard label there is little. That is why the candidate-pool curve in E.5, not the reranker, is the informative measurement here. It is also why the recall column of the ablation is close to saturated: on silver-standard labels every system finds the gold chunk, and the ordering metrics are where the systems differ. Sweeping the pool gives recall@10 0.969 at a pool of 5 and 0.969 at a pool of 100.
3. **The category pre-filter does nothing here.** Its effect is exactly +0.000 (p = 1.00). On a single-category corpus that is the expected result — the filter cannot restrict anything that is already the only thing in the corpus. It is reported here precisely because it makes the point that a filter's measured effect is a property of the corpus, not of the filter.
4. **The modality quota belongs before the reranker.** Applied before it, overall recall@10 moves +0.031 and table recall +0.000; applied after it, overall recall@10 moves -0.031 and table recall +0.000. The difference between the two placements is +0.062 of Recall@10 (p = 0.16) and +0.000 of table recall. A pre-rerank quota proposes the *membership* of the final ten and the cross-encoder can only reorder it; a post-rerank quota has to import candidates the cross-encoder already ranked below the cut, so it tends to import the wrong one and displace a good one. The generalisable rule: a constraint on a downstream artefact should be enforced where it can still choose the candidates, not where it must work against another component's judgement. **Which placement the shipped system uses.** The system as built applies the quota *after* the reranker. That was the September 2026 design, it is what the code's default still does, and every measurement in this project was taken with it. Moving it would change the retrieval that every other measurement sits on -- the gate's calibration, the generator-side comparison and the per-claim results -- so it is one change and a full re-measurement, and it has not been made five days before a defence. The discrepancy is recorded here instead of being left for a reader to discover, and moving the quota before the reranker is the first item in the next-steps list.
5. **Corpus modality composition bounds what a modality-aware mechanism can show.** This corpus is 88.8% text, 6.0% table and 5.2% chart, and the benchmark contains 8 table-lookup questions. A quota over table and chart chunks cannot be evaluated at that size, which is why the modality result above is a trade rather than a gain, and why the composition is reported before the result rather than after it.
6. **The gate's operating point is a fitted parameter of the deployment, and what it detects is narrower than what it is called.** At τ = 0.05 it answers 93.8% of answerable questions and refuses 36.1% of unanswerable ones. Its label is answer-in-context detectability. Of the 144 queries in the negative class, 0 are answerable questions whose evidence the retriever missed and 144 are genuinely unanswerable, so the retrieval-failure share is 0.0%. Because the genuinely-unanswerable share dominates here, the gate's negative class is mostly what it is meant to detect, and the ceiling on its performance is set by the retriever rather than by the threshold. The threshold must be re-fitted per retriever and per corpus.
7. **Every rate in this report is reported with its prevalence and against the two degenerate policies** — never refuse and always refuse — because a filter result without those quantities does not mean anything. The thresholds at the ends of the sweep are not baselines and are not presented as such.
8. **The framework's own hypothesis holds, and how much it is worth depends on the generator.** Under the cautious prompt -- the deployed system -- the gate reduced the rate of answering unanswerable questions from 0.535 to 0.417, paired question by question (exact McNemar p = 0.002), against a generator that declined 67 of the 144 on its own. Under the answering prompt -- the same comparison, the same questions and the same scorer, with the permission to decline removed -- the gate reduced that rate from 0.938 to 0.528, paired question by question (exact McNemar p = 0.000), at the cost of answering 30 of 32 answerable questions against the ungated arm's 32. A control arm that refuses the same number of questions at random answered 87 of the unanswerable questions against the fitted gate's 76 and the ungated arm's 135, and 21 of the answerable ones against 30 and 32, so what the confidence score contributes is what separates the fitted gate from a refusal of the same size. The refusal rate the retrieval-side experiments attribute to the gate is, with a generator behind it, partly the prompt's and partly the gate's; the more of the refusal the prompt makes on its own, the less there is left for the gate to add -- which is why the two prompt conditions have to be reported together.
9. **And the project's own instrument was audited, found wanting, and repaired.** 27 of the 132 answerable questions carried an answer label attached to the wrong question: a table question named the column its key came from while taking the answer from the next column, and some numeric golds were digit prefixes of longer tokens. The generator was corrected, the benchmark rebuilt and every experiment in this project re-measured against it; the audit now finds 0 remaining defects, and the benchmark as it stood before the repair is kept so that the finding stays checkable. The gold chunk was correct in every defective case, so the retrieval-side measurements were never affected -- but it also means the accuracy margin over the long-context arm is consistent in direction but reaches no test's significance threshold: not under the whole-answer entailment test (p = 0.727), not under a length-controlled re-scoring of the same answers (p = 0.508), and not under a lexical test that ignores length (p = 0.250). The long-context comparison is therefore settled on coverage and cost, and directional on answer quality.
10. **And the benchmark's own unanswerable half was audited, found separable from the question alone, and rebuilt.** A classifier that saw only the question told the answerable questions from the unanswerable ones at an ROC AUC of 0.999, and one regular expression caught 76.4% of the unanswerable class with no false positives at all, because the class's designated hard case named a fabricated identifier that no answerable question carried. The refusal rate that class produced was an upper bound rather than a measurement. The class was rebuilt as a corpus-anchored one -- the same question stems, the same source documents, the same label machinery, and each repaired question given a structural twin in the answerable class -- and every experiment was re-measured against it. The gate now refuses 23.6% of the corpus-anchored questions (26 of 110) against the 36.1% the defective class suggested. The detection problem this framework addresses is considerably harder than the first version of the benchmark made it look, and the repair is what shows it.

That is the honest result of this project: **the architecture works, and the most useful output is knowing precisely where it does not, and why.**
