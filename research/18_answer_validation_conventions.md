# 18 — How much of the answer-accuracy column is the scoring convention?

**Written:** 12 November 2026, six days before the defence.
**Closes:** gap **G18** (a third validation convention) and gap **G19** (the
paired disagreement count between the two shipped tests), from
`research/16_open_items_register.md` §D.
**Artefact:** `impl/scripts/answer_validation_conventions.py` →
`impl/results_focus/exp8_answer_validation_conventions.json`.
**Read alongside:** `research/15_label_validation_protocol.md`, which states
the protocol and sets it against the published benchmarks; this note measures
what that protocol could not measure.

---

## 1. What was asked, and what was already known

`research/15` §5 items 3 and 4 recorded two open items on the answer side.

**G18 — a third convention.** The thesis reports two correctness tests and
audits three variants of them. No convention *from the literature* had been
applied to the shipped answers. Note 15 was explicit that this was feasible
and cheap: `_answer_is_correct` is a single function, the generator's answers
and the benchmark's gold strings are both present in the result files, and
`audit_answer_side.py:244-295` already demonstrates the pattern by re-scoring
the *same* answers three ways and reporting McNemar tests.

**G19 — the paired disagreement count.** The project reports both columns and
the arm-level spreads, but never the question-by-question count of the
questions on which the two tests give opposite verdicts. Note 15 called it
"derivable from the shipped records without re-running anything".

Both are now measured. Nothing was re-run: the generator's answers are in
`impl/results_focus/exp8_generation.json` and
`impl/results_focus/exp8_generation_answering.json`, and the gold strings are
in `impl/data/benchmark_focus/benchmark.json`.

## 2. The conventions

Five, applied to the same answers.

| # | Convention | Source | How it is computed here |
|---|---|---|---|
| 1 | **Whole-answer entailment** (`nli`) | this project | The shipped `correct_nli` flag: the answer is the premise and the gold the hypothesis of a DeBERTa NLI model, scored at a 0.5 entailment threshold. |
| 2 | **Lexical key-term** (`keyterm`) | this project | The shipped `correct_keyterm` flag: at least half of the gold's content tokens (up to six) appear somewhere in the answer. |
| 3 | **SQuAD 2.0 normalised exact match** (`squad_nem`) | `arXiv:1806.03822`, `evaluate-v2.0.py` | Lowercase, strip all punctuation, drop the articles `a|an|the`, collapse whitespace; then string equality. |
| 4 | **SQuAD 2.0 token-level F1** (`squad_f1`) | `arXiv:1806.03822` Table 4; `arXiv:1705.03551` §6.1 | Token overlap over the same normalised strings, as a harmonic mean of precision and recall. SQuAD reports F1 as a continuous score; it is also thresholded at 0.5 here so that it can be put on the same footing as the other four in the paired tests. |
| 5 | **PopQA containment** (`popqa_containment`) | `arXiv:2212.10511` §3.1 | "Any substring of the prediction is an exact match of any of the gold answers" — the gold, case-insensitively, is inside the answer. |

**The one convention in the literature that was not applied** is an LLM judge
on semantic equivalence, BrowseComp's rule (`arXiv:2504.12516` §2.3). It
needs a judge prompt, a second generator and a budget, and it does not answer
the question this measurement answers for the lexical family. It is recorded
as not done rather than as done-and-failed.

**What was not changed.** The corpus, the benchmark and the label standard are
untouched. Nothing was re-labelled. This is a re-scoring of answers that were
already produced, not a new experiment.

## 3. The result

### 3.1 The two shipped tests agree at close to chance

This is G19, and it is the headline. Question by question, over the answered
answerable questions:

| Condition | Arm | n | both correct | NLI only | key-term only | neither | disagreement | Cohen's κ |
|---|---|---|---|---|---|---|---|---|
| cautious | retrieval, gate removed | 31 | 17 | 2 | 11 | 1 | 41.9% | −0.012 |
| cautious | framework, gate fitted | 30 | 20 | 2 | 7 | 1 | 30.0% | 0.020 |
| cautious | control refusing at random | 22 | 11 | 2 | 7 | 2 | 40.9% | 0.032 |
| cautious | framework, threshold transferred | 11 | 3 | 1 | 5 | 2 | 54.5% | 0.011 |
| cautious | whole corpus in the prompt | 31 | 15 | 2 | 9 | 5 | 35.5% | 0.103 |
| answering | retrieval, gate removed | 32 | 22 | 1 | 6 | 3 | 21.9% | 0.158 |
| answering | framework, gate fitted | 30 | 18 | 1 | 9 | 2 | 33.3% | 0.070 |
| answering | control refusing at random | 22 | 12 | 2 | 6 | 2 | 36.4% | 0.052 |
| answering | framework, threshold transferred | 11 | 2 | 1 | 7 | 1 | 72.7% | −0.053 |
| answering | whole corpus in the prompt | 32 | 11 | 2 | 13 | 6 | 46.9% | 0.056 |

Across every arm and both conditions the disagreement rate runs from **21.9%
to 72.7%**, and Cohen's κ runs from **−0.05 to 0.16**. Cohen's own scale puts
0.00–0.20 at "slight" agreement and below 0.00 at worse than chance. Two of
the ten cells are below zero.

**The asymmetry is the mechanism.** The key-term test marks 5 to 13 questions
correct that the entailment test marks wrong, and marks only 1 or 2 correct
that the entailment test also marks correct. The key-term test is a
containment test with a low bar; the entailment test is a semantic test
against a 0.5 threshold with a premise that may be much longer than its
hypothesis. The two are not two readings of one measurement. They are two
different measurements, which is why the thesis reports both: either one
alone would have decided the result.

**This is a stronger and less comfortable statement than the one the thesis
was carrying.** Note 15 §4.2 said the convention "determines the absolute
level" of the accuracy figures and whether the gate looks better or worse
than no gate. The measurement says the two columns are close to
statistically independent, so "the level" was never the right handle: it is
not that the same quantity is measured at two offsets.

### 3.2 The absolute level, under all five conventions

**Cautious condition** (the deployed system — the generator is permitted to
decline):

| Arm | answered | NLI | key-term | SQuAD NEM | SQuAD F1 (mean) | PopQA |
|---|---|---|---|---|---|---|
| retrieval, gate removed | 31 | 0.613 | 0.903 | 0.097 | 0.420 | 0.323 |
| framework, gate fitted | 30 | 0.733 | 0.900 | 0.167 | 0.447 | 0.433 |
| control refusing at random | 22 | 0.591 | 0.818 | 0.136 | 0.390 | 0.227 |
| framework, threshold transferred | 11 | 0.364 | 0.727 | 0.000 | 0.156 | 0.091 |
| whole corpus in the prompt | 31 | 0.548 | 0.774 | 0.161 | 0.335 | 0.290 |

**Answering condition** (the generator must answer everything):

| Arm | answered | NLI | key-term | SQuAD NEM | SQuAD F1 (mean) | PopQA |
|---|---|---|---|---|---|---|
| retrieval, gate removed | 32 | 0.719 | 0.875 | 0.094 | 0.364 | 0.312 |
| framework, gate fitted | 30 | 0.633 | 0.900 | 0.067 | 0.385 | 0.233 |
| control refusing at random | 22 | 0.636 | 0.818 | 0.000 | 0.324 | 0.273 |
| framework, threshold transferred | 11 | 0.273 | 0.818 | 0.000 | 0.133 | 0.091 |
| whole corpus in the prompt | 32 | 0.406 | 0.750 | 0.062 | 0.271 | 0.219 |

The four binary conventions span **0.81** on the ungated arm's answers in the
cautious condition (0.097 to 0.903), and the widest spread over all ten
arm-and-condition cells is **0.83** (the fitted gate in the answering
condition, 0.067 to 0.900) — larger than any margin the generator-side
comparison reports.

**How many questions does the convention actually decide?** Counting the
answered questions that every convention calls correct, and those that no
convention calls correct:

| Condition | Arm | n | all five correct | no convention correct | **verdict depends on the convention** |
|---|---|---|---|---|---|
| cautious | retrieval, gate removed | 31 | 2 | 1 | **28** |
| cautious | framework, gate fitted | 30 | 5 | 1 | 24 |
| cautious | control refusing at random | 22 | 3 | 2 | 17 |
| cautious | framework, threshold transferred | 11 | 0 | 2 | 9 |
| cautious | whole corpus in the prompt | 31 | 5 | 5 | 21 |
| answering | retrieval, gate removed | 32 | 3 | 3 | **26** |
| answering | framework, gate fitted | 30 | 2 | 2 | 26 |
| answering | control refusing at random | 22 | 0 | 2 | 20 |
| answering | framework, threshold transferred | 11 | 0 | 1 | 10 |
| answering | whole corpus in the prompt | 32 | 2 | 6 | 24 |

On the ungated arm in the deployed condition, **two of 31** answers are
correct under all five conventions and **one of 31** is wrong under all five.
The verdict on the other **28** depends on the convention. That is the
honest size of the answer-accuracy column.

### 3.3 Which arm is best, and does the reversal survive?

The thesis's claim was that the two shipped tests disagree about which arm
is best, and that the order reverses between the two prompt conditions.
The measurement says the reversal is **not** an artefact of the two shipped
tests — it survives three further conventions.

| Condition | NLI | key-term | SQuAD NEM | SQuAD F1 | PopQA | Best arm |
|---|---|---|---|---|---|---|
| cautious | fitted | **ungated** | fitted | fitted | fitted | **fitted, under 4 of 5** |
| answering | **ungated** | fitted | **ungated** | fitted | **ungated** | **ungated, under 3 of 5** |

So the sign of the gate-against-no-gate comparison on the answer side is a
property of the **condition**, not of the convention: with the generator
permitted to decline — the deployed system — the fitted gate is ahead under
four conventions out of five; with the generator forced to answer, the
ungated pipeline is ahead under three out of five. Note 15 §4.2 described
this reversal as a property of the scoring convention. It is not. It is a
property of the system, and it is now measured as one.

### 3.4 What reaches significance

Every paired comparison, under every convention. The binary conventions use
the exact two-sided McNemar on the discordant pairs; token-level F1 uses a
paired bootstrap (10,000 resamples over pairs, fixed seed) and is called
significant when its 95% interval excludes zero.

| Condition | Comparison | NLI | key-term | SQuAD NEM | SQuAD F1 | PopQA | **significant under** |
|---|---|---|---|---|---|---|---|
| cautious | fitted gate vs gate removed | 0.219 | 1.000 | 0.625 | — | 0.125 | **0 of 5** |
| cautious | gate removed vs whole corpus | 1.000 | 0.250 | 0.625 | — | 1.000 | **0 of 5** |
| answering | fitted gate vs gate removed | 0.453 | 1.000 | 1.000 | — | 0.500 | **0 of 5** |
| answering | gate removed vs whole corpus | 0.002 | 0.219 | 1.000 | — | 0.375 | **2 of 5** |

("—" means the bootstrap interval includes zero; the p-value columns are the
McNemar exact p-values for the four binary conventions.)

**Two things follow, and they are the two the thesis actually rests on.**

1. **No arm comparison on the answer side reaches significance under more
   than one convention.** The gate-against-no-gate comparison reaches *no*
   convention's threshold in either condition. The retrieval-against-
   long-context comparison reaches two of five in the answering condition and
   none in the cautious one — so the two conditions disagree about a
   comparison the report already calls *directional rather than significant*.
   The thesis's existing wording was therefore right, and is now measured
   rather than asserted.
2. **Everything the gate is claimed on is invariant.** The coverage, the
   cost, the refusal of the questions that should be refused, the
   claim-support figures and every retrieval measurement are computed from
   counts and from the evidence, not from the answer string. None of them can
   be moved by the choice of scoring convention. Before this measurement that
   was an argument; it is now a check.

## 4. What this does not settle

* **It does not make any convention right.** Five conventions measured is not
  one convention validated. Which one is right is a question about the
  benchmark's gold answers, and that needs human annotation — **G16**, the
  largest open item in the thesis.
* **It does not measure the aliasing rate** on this corpus's gold answers.
  That follows from G16 (**G17**).
* **It does not cover the industrial corpus.** The generator-side evaluation
  on the industrial corpus was never run (**G20**), so there are no
  industrial answers to re-score. The finding is a finding about the focus
  corpus.
* **It does not apply an LLM judge** on semantic equivalence, for the
  reasons in §2.
* **It does not measure a containment test's false-positive rate**, which
  note 15 §3.1 recorded as a gap in the literature as well as here. What it
  shows is that the corpus's own key-term test — which is a containment test
  with no token-boundary check — is the most lenient of the five and agrees
  with the most rigorous of them on 11 of 31 questions.

## 5. What changed in the deliverables

| Where | What |
|---|---|
| `deliverables/Deliverable_1_PartE_Results.md` §E.8.1 (generated by `deliverables/scripts/make_results_md.py`) | The new subsection: the five conventions, the disagreement and κ, the five levels, the consensus counts, and what the measurement settles. |
| `deliverables/templates/Deliverable_1_PartF_toJ.md`, limitation **L18** | Rewritten. It also had a **missing table cell** — the row had four columns where the header has five — so its "consequence for the claims" was silently absent from the rendered table. |
| `deliverables/templates/MTP_Plain_Language_Guide.md` §10.2 item 11 | Moved to §10.3 "What is *not* open", with the measured result. |
| `deliverables/templates/MTP_Plain_Language_Guide.md`, Part 11 | A new panel question: *"Your answer-accuracy numbers depend on how you score the answer. Isn't that fragile?"* |
| `deliverables/scripts/results_source.py` | `load_answer_validation_conventions`, `answer_validation_conventions_summary`, `answer_validation_conventions_claim` — the numbers are read out of the measurement, not typed. |
| `deliverables/scripts/substitute_tokens.py` | The `AVC_*` tokens. |
| `research/16_open_items_register.md` | G18 and G19 moved to §H, "What is closed". |

## 6. How to re-derive any of it

```bash
python impl/scripts/answer_validation_conventions.py
```

writes `impl/results_focus/exp8_answer_validation_conventions.json`, from
which `results_source.answer_validation_conventions_summary` reads the
headline numbers and the build substitutes them into the prose.
