# 21 — The two never-run probes, on the industrial corpus

**Written:** 12 November 2026, six days before the defence.
**Closes:** gaps **G21** and **G22** from `research/16_open_items_register.md` §E.
**Artefact:** `impl/experiments/audit_unanswerable_class.py` run with
`MTP_VARIANT=industrial` → `impl/results_industrial/exp12_unanswerable_class_audit.json`.

---

## 1. Why these two were open

`impl/results_industrial/exp12_unanswerable_class_audit.json` carried

```json
"question_only_policy": {"status": "not_run",
                          "note": "no API credential reachable from this machine"},
"parametric_leakage":   {"status": "not_run", ...}
```

The focus corpus's audit had run both probes; the industrial corpus's had
not, because no credential was reachable from the machine at the time. Both
gaps therefore said the same thing — *the probes were never run* — and the
register recorded them as gaps rather than as failures, which is what they
were.

## 2. What the probes are

**The question-only policy** (`G21`). A model is given the question and
**nothing else** — no documents, no evidence — and asked whether a standard
industrial engineering documentation set would contain the answer. This is the
hypothesis-only baseline of the answerability literature, and it is the
measurement that matters for the benchmark's validity: a fitted classifier
can memorise a sample, but a model that has never seen the benchmark can only
use what the question carries. If the policy can tell the two classes apart,
then a system that refused on the question's *shape* would score as well as
one that read the passages, and the benchmark could not tell them apart.

**The parametric-leakage probe** (`G22`). The generator is asked the same
questions with **no corpus in the prompt at all**. A high rate on the
unanswerable class means the "unanswerable" label is not corpus-specific:
either the parameters contain the answer, or the generator is guessing — which
is the behaviour the gate exists to prevent. The answerable class is the
control, and the closed-book answers to it are scored against the same gold
the retrieval arms are scored against, so that a high answer *rate* with a low
*accuracy* (truthiness) can be told apart from genuine memorisation.

## 3. The result

### 3.1 The question-only policy is worse than chance on this corpus

A model given the question and nothing else separates the two classes at an
ROC AUC of **0.478** — that is, at *no* discrimination at all, and below the
0.5 that would mean a coin toss. It flags 66.5% of the unanswerable class as
unanswerable, and it pays for that by refusing **70.9%** of the answerable
class: 175 of the 247 answerable questions are called unanswerable when they
are not. Its abstention precision is 0.428 and its F1 is 0.521.

That is the strongest version of the result the focus corpus's repair was
meant to produce, and it is worth reading beside the other two corpora:

| Corpus | Question-only policy's AUC | Detects | Costs |
|---|---|---|---|
| focus domain | 0.576 | 71.5% | 56.3% |
| six-category | 0.588 | 72.2% | 54.5% |
| **industrial** | **0.478** | 66.5% | **70.9%** |

**On the industrial corpus the question carries no information about whether
the corpus can answer it.** A system that refused on the question's shape
would refuse most of the answerable questions and still be unable to find the
unanswerable ones, and the benchmark can tell such a system apart from one
that reads the evidence. That is the property the benchmark needs, and it is
the reason the class was rebuilt in the first place.

### 3.2 The parametric-leakage probe: truthiness, not memorisation

Asked the same questions with no corpus in the prompt at all, the generator
answers substantively **95.9%** of the unanswerable questions — 100.0% of the
corpus-anchored definition family, 92.3% of the corpus-anchored table family
and 91.8% of the out-of-domain family — and **95.5%** of the answerable ones.
The two rates are the same to within a point, so the model's closed-book
behaviour carries no information about whether a question is answerable from
this corpus: it answers both classes alike.

And the closed-book answers to the answerable questions are right only
**0.138** of the time under the entailment test and **0.251** under the
key-term test, against the same gold the retrieval arms are scored against. A
high answer rate with a low accuracy is **truthiness, not memorisation**: the
model does not reproduce the corpus's values either, it simply answers.

This matters because it rules out the contamination one would most fear —
the unanswerable half being made of questions the model happens to know. It is
not: the closed-book answers are confidently wrong about both classes, at
almost exactly the same rate.

### 3.3 The same picture as the other two corpora

| Corpus | Closed-book answer rate, unanswerable | answerable | Closed-book accuracy on the answerable class (NLI / key-term) |
|---|---|---|---|
| focus domain | 0.965 | 0.906 | 0.094 / 0.188 |
| six-category | 0.979 | 0.932 | 0.061 / 0.220 |
| **industrial** | **0.959** | **0.955** | **0.138 / 0.251** |

Three corpora, three constructions, the same finding: the generator answers
almost everything with no corpus in the prompt, and is mostly wrong when it
does. The gate's job is not to stop the model from answering — it cannot — but
to refuse to let an answer through without evidence attached to it, and the
refusal has to come from the evidence rather than from the question's shape.
On the industrial corpus it demonstrably does.

## 4. What this does and does not settle

* It does **not** make the industrial unanswerable class free of form-only
  separability. The separate structural measurement puts that at AUC 0.708
  (p = 0.010) on this corpus, against 0.556 (p = 0.149) on the better-powered
  six-category corpus. That residual is stated in the deliverables rather
  than glossed.
* It does **not** measure memorisation of the corpus's content by the model.
  The closed-book answers to the answerable questions are scored against the
  gold, and they are mostly wrong — which says the model does not reproduce
  the corpus's values, not that it never could.
* It does **not** change the focus corpus's measurements, which were already
  run and are unchanged.

## 5. How it was run, and what was fixed to run it

The first attempt **failed**, and the failure was worth fixing:

* the provider answered **429 Too Many Requests** after 744 requests, and the
  probe's retry policy waited 8, 16 and 24 seconds — the wrong length of wait
  for a rate limit;
* the probe then **crashed** rather than returning what it had collected,
  because `impl/experiments/audit_unanswerable_class.py`'s `_leakage` function
  carried a copy of the *question-only policy's* error branch, naming four
  variables (`precision`, `recall`, `f1`, `fp`) that `_leakage` never
  defines. The bug fires only when the probe hits a provider error, which is
  why it had never been seen.

Both are fixed in the shipped script:

* **a disk cache of the API responses**, keyed by the system prompt and the
  question, at `impl/artifacts<variant>/exp12_llm_cache.json`. A run
  interrupted by a rate limit no longer throws away the answers it already
  has, and a re-run is free. The key includes the system prompt, so the
  question-only policy and the closed-book probe cannot collide.
* **a rate-limit-aware backoff**: a 429 waits 60, 120 and 180 seconds rather
  than 8, 16 and 24, and the inter-request pause is configurable.

The corrected error branch returns the partial result with the shortfall
stated, which is the honest thing to do: a provider timeout is not a fact
about the policy being measured.

## 6. How to re-derive any of it

```bash
MTP_VARIANT=industrial bash impl/scripts/run_unanswerable_audit.sh
```

writes `impl/results_industrial/exp12_unanswerable_class_audit.json`, from
which `results_source.unanswerable_audit_summary` reads the numbers and the
build substitutes them into the prose.
