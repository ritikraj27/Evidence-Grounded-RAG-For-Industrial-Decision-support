---
title: "An Evidence-Grounded Retrieval-Augmented Generation Framework for Industrial Decision Support"
subtitle: "Technical Documentation — Architecture, Implementation and Measurement Protocol"
author: "Ritik Raj (25IM60R12) — Department of Industrial and Systems Engineering — IIT Kharagpur — Supervisor: Dr. Sri Krishna Kumar"
date: "11 November 2026"
shorttitle: "MTP Technical Documentation"
---

# 0. What this document is, and how to read it

This is the **deep document**. The status report says *what was built and what
it measures*; this one says *how each piece works, why it was built that way,
what evidence supports each design decision, and how to reproduce every
number*.

It is written so that a reader who has never seen the codebase can follow it
end to end and then answer a panel's questions about any part of it. Where a
decision was contested, the losing alternative and the measurement that
settled it are both recorded, because "why is it like this?" is the question
that distinguishes a system from a configuration.

**Reading order for a defence.** If you have twenty minutes, read §1 (the
problem), §3 (the architecture), §6.4 (what the gate actually does) and §9
(the experiments). If you have an hour, read all of it. If you have a
question about a specific number, Appendix B says which result file it came
from.

**Three conventions used throughout.**

1. **Every number is a measurement.** The figures in this document are
   substituted at build time from the experiment result files. A number that
   is not bound to a measurement is a number nobody re-checked, and this
   project does not ship those.
2. **A design decision is stated with the evidence that made it.** Where a
   choice was reversed, the reversal and its measurement are named.
3. **A negative result is reported as a negative result.** Several findings
   in this work are nulls, and they are the most informative part of it.

---

# 1. The problem, precisely

## 1.1 The industrial setting

Industrial engineering practice runs on documents. A maintenance engineer
deciding when to replace a conveyor drive reads a failure-mode and effects
analysis; a production planner reads a standard operating procedure; a
quality engineer reads a control plan; a procurement specialist reads a
supplier specification. Each organisation holds hundreds of such documents,
and the *answering* of a question about them is a human skill built on
knowing which document holds the answer.

Retrieval-augmented generation (RAG) is the obvious candidate for the
retrieval half of that job: retrieve the relevant passages, put them in the
prompt, let a language model compose the answer. It has been demonstrated
widely, on dialogue, on clinical text, on scientific claims and on
social-media fact-checking.

## 1.2 The failure that matters

RAG inherits the generator's ability to produce fluent, confident, and
entirely unsupported text. In a chat product that is a quality problem. In a
plant it is a safety and cost problem: a fabricated safety-stock rule, a
fabricated acceptance criterion or a fabricated duty cycle all look exactly
like correct ones, and they propagate into a plan.

The mechanisms that address this in the literature fall into two families:

* **post-hoc verification** — generate first, then check the output against
  the evidence and retract it if unsupported. HALT-RAG (arXiv:2509.07475) is
  the clearest instance: a dual-NLI ensemble plus lexical features through a
  calibrated meta-classifier, reporting detector-level F1 on HaluEval. It
  never runs a generator and makes no end-to-end RAG claim.
* **pre-generation gating** — decide *before* the model is called whether the
  retrieved evidence supports an answer at all, and refuse if it does not.
  This is the family this project belongs to.

The gap is not the mechanism. It is the **measurement**: what a gate in the
pre-generation family costs in coverage, what it buys in refusal, and how it
behaves when the evidence is not where the question says it is — measured on
industrial engineering text, at the level of the individual answer claim.

## 1.3 The three design questions

Everything in this project is downstream of three questions.

| Question | Answer | Where |
|---|---|---|
| Can the gate be bypassed? | No — it is a control-flow fact, not an instruction | §4.8 |
| What is the gate's label, precisely? | *Answer-in-context detectability*, not evidence sufficiency | §4.8.3 |
| What does the gate cost, and what does it buy? | Measured on two prompt conditions, against a random-escalation control | §7.7 |

The second question is the one that most often goes wrong. The literature
reserves *sufficiency* for a **set-level** property (SURE-RAG arXiv:2605.03534;
Certify arXiv:2610.34684); the positive class here is a **query-level**
property — "is the gold chunk in the reranked candidate pool". Calling it
"sufficiency" would have been claiming prior art this thesis does not have.

---

# 2. System overview

## 2.1 Module map

```
impl/src/
  config.py         every hyperparameter, with a provenance note per value
  ingestion.py      parse -> chunk -> tag modality + category -> Chunk
  lexical.py        BM25Index: Robertson/Sparck-Jones IDF, k1, b
  models.py         embed_texts, dense_top_k, rerank  (the model wrappers)
  hybrid.py         reciprocal_rank_fusion, apply_modality_quota
  confidence.py     the gate: features, Platt scaling, apply_gate
  query_form.py     the four-rule query-form validator
  claims.py         split_into_claims, assess_claims, band_for, render_answer
  contradiction.py  detect_contradictions, contradiction_summary
  evaluate.py       evaluate_retrieval, aggregate_generation
  pipeline.py       Framework: retrieve(), answer(); the Index dataclass
  stats.py          bootstrap intervals and the comparison statistics
```

`14` modules, 4,823 lines. `config.py` is the
single source of truth: no magic numbers in the pipeline, and every value
carries a note saying where it came from.

## 2.2 The data flow

```
  corpus documents
        |
        v
  [ingestion.py]  parse -> chunk -> tag(modality, category) -> Chunk records
        |
        v
  [build_index]   BM25Index.build(chunk_text)      -> lexical leg
                  embed_texts(chunk texts, BGE-M3)   -> dense leg  (735 x 1024)
        |
        v
  Index  (chunks, bm25, embeddings, chunk_ids, chunk_text, modality_of, category_of)
        |
        |  query
        v
  [Framework.answer]
        |
        +-- [query_form.py] assess_query_form      --> refuse? -> "form"
        |
        +-- [Framework.retrieve]
        |      category pre-filter (BOTH legs)
        |      BM25 leg          (top 20)
        |      dense leg         (top 20)
        |      RRF fusion        (k = 60)
        |      modality quota    (swap-based, floor on tables/charts)
        |      cross-encoder     (top 50 scored -> top 10 delivered)
        |      [confidence.py]   5 features -> calibrated posterior vs tau
        |                                          --> reject? -> "evidence"
        |
        +-- [generator]  ONLY on acceptance, ONLY with the accepted passages
        |
        +-- [claims.py]          per-claim confidence bands + citations
        +-- [contradiction.py]  NLI + same-subject + numeric contradiction
        |
        v
  AnswerResult(query, answer, accepted, trace, claim_assessments,
               contradictions, contradiction_summary, refusal)
```

`RetrievalTrace` records **everything** that happened for one query: the
dense and lexical candidate lists, the fused ranking, the reranked list, the
accepted chunks, the posterior, the gate's five features, the modality
counts and the quota note. It is the audit trail, and every experiment reads
from it rather than re-deriving anything.

## 2.3 The variant mechanism

`MTP_VARIANT` moves the corpus, the benchmark, the index and the results
directory together:

```python
def _variant(base: str) -> Path:
    variant = os.environ.get("MTP_VARIANT", "").strip()
    if not variant:
        return ROOT / base
    stem = Path(base).name
    parent = Path(base).parent.name
    return ROOT / parent / f"{stem}_{variant}"
```

So `MTP_VARIANT=focus` points `data/corpus` at `data/corpus_focus`,
`data/benchmark` at `data/benchmark_focus`, `artifacts` at `artifacts_focus`
and `results` at `results_focus`. **The same code runs both evaluations with
not one conditional.** The mechanism matters because it makes it impossible
for a variant to overwrite a measured run: the paths move together, and the
experiment scripts read the variant from the configuration rather than
taking a path argument.

| Variant | Corpus | Benchmark | Used for |
|---|---|---|---|
| unset | six categories (2,383 chunks) | 276 queries | the cross-category transfer study |
| `focus` | supply chain management (735 chunks) | 176 queries | every headline measurement |
| `demo` | the sandbox copy | the demo benchmark | trying the system by hand |

---

# 3. Stage 1 — ingestion and indexing

## 3.1 Chunking

`ingestion.py` parses each document into chunks and records, for each chunk:
its id (`doc::page::chunk`), its document, its text, its **modality**
(`text` / `table` / `chart`), its page, its section, its caption and its
**category**.

The focus corpus has 735 chunks over 14
documents, 88.8% text, 6.0% tables and 5.2%
charts. The six-category corpus has 2,383 chunks over 46
documents and 6 categories, at 88.8% text.

> **A defect this design caught.** An article was indexed twice under two
> category names, which split a document across two categories and leaked it
> into **both** halves of the cross-category transfer split — so the
> "held-out" half contained material the "tuning" half had been fitted on.
> The invariant test `test_real_corpus_has_no_duplicates` now asserts both
> that chunk ids are unique and that no document spans two categories.

## 3.2 The index

`build_index` produces an `Index` holding the chunk records, a BM25 index
built over the chunk texts, the embedding matrix, and the lookup dictionaries
the online path needs. It is saved as `index.json` plus `index.npy` and can
be reloaded without recomputing anything.

---

# 4. Stage 2 — retrieval

The order of these stages is the design. Each one is there because a
measurement said it had to be there.

## 4.1 The query-form validator (`query_form.py`)

A request that is not a question cannot produce an answer, so it is refused
**before** retrieval — before the cross-encoder, before the model, at no
retrieval cost. Four rules:

| Rule | Condition |
|---|---|
| `empty` | the query is empty |
| `no_words` | the query contains no alphabetic character |
| `no_content` | every word is a function word or a deictic |
| `incomplete` | the query ends on a word that cannot end an English question |

**It is a separate component from the gate**, and the distinction is
load-bearing. The gate answers "is there evidence here?"; the form check
answers "is this even a question?". They answer different questions and
neither substitutes for the other: the form check cannot tell whether the
corpus contains the answer, and the gate cannot tell whether the question was
ever a question.

The check is **lexical** and **fails open** — it is a filter, not a
classifier. On the focus domain it refuses 25 of 25 hand-authored
malformed queries, and 0 of 35 hand-authored well-formed ones — a **zero**
false-rejection rate on the well-formed population.

On the harder population — the question stems the benchmark generator emits
and then rejects, harvested from the corpus and labelled by hand, which is
the only malformed text not written by the author of the rule — it refuses 6 of 16
(37.5%), and 0 of 13 well-formed ones.

Against the benchmark itself it refuses 3 of 176 queries (1.7%). Those refusals are
worth being precise about: they are **generator artefacts that read as
malformed** — "What is among them?", "According to the table in the source
document, what is the Sufficient thinking ("If… then") for What to change
to??" — questions the generator emitted and then discarded. The check
refuses them because they genuinely are not well-formed; the benchmark
counts them as queries, which is the artefact.

The check costs 2.6 microseconds per query, and it runs
before retrieval, so a request it refuses costs no embedding pass, no
cross-encoder pass and no model call.

> **The counterfactual that decided the design.** The benchmark builder's own
> `_subject_is_usable` rule looks like a form check but is a rule about
> *question generation*. Reused as a runtime check it would have refused
> 13 of 13
> well-formed questions — a **100% false-rejection rate**. Most of the
> questions that generator rejects are perfectly good questions. A filter
> written for one purpose does not fit another, and the only way to know is
> to measure the false-rejection rate against a hand-labelled population
> before shipping it.

## 4.2 The category pre-filter

Applied **before** retrieval, to **both** legs.

Filtering after retrieval means the retriever paid to score documents that
were about to be discarded, and — worse — the discarded documents still
influenced the fusion. Filtering before retrieval means the candidate pool
contains only in-category material, so the dense model's top-k and the
reranker's ranking are computed on the correct sub-corpus.

BM25's IDF statistics are **not**: BM25 scores the whole corpus and the
filter is applied to the candidate list afterwards. That distinction is not
cosmetic — it is why a *soft prior* cannot reproduce the filter's benefit.
A prior promotes the in-category chunks in the fused ranking but leaves the
pool whole, and the chunks it moves are ones the reranker would not have
promoted; a filter *removes* the out-of-category chunks the reranker would
have ranked highly. Measured: `research/20_soft_prior.md`.

> **The defect that made it look like a measured effect of zero.** The filter
> was originally applied to the dense leg only. Because BM25 dominates the
> fusion, an unfiltered lexical list floods the fused ranking with
> out-of-category documents and the filter's effect disappears entirely. The
> ablation reported a difference of exactly 0.000 and it looked like a
> finding. It was a bug. `test_category_filter_applies_to_both_legs` now
> asserts it. This is the same failure mode as applying a pgvector metadata
> filter to only one of two indexes.

On the focus domain the filter is a **no-op**, and that is the correct
result: the corpus has one category. Its value appears on the six-category
corpus, where it changes **no recall at all** — not one of that corpus's gold
chunks sits outside its question's category — and gains **ordering**: MRR 0.8025 against 0.7764 with no category handling at all, a
paired difference of 0.0261 (Wilcoxon
p = 0.0272). The repair proposed for it — a soft prior instead of
a hard filter — does not work, and the reason is the one above.

## 4.3 The lexical leg — BM25 (`lexical.py`)

Okapi BM25 with the Robertson IDF variant:

```
score(q, d) = SUM_{t in q} IDF(t) * f(t,d) * (k1 + 1)
                         ----------------------------------------
                         f(t,d) + k1 * (1 - b + b * |d| / avgdl)

IDF(t) = ln( 1 + (N - df(t) + 0.5) / (df(t) + 0.5) )
```

`k1 = 1.2`, `b = 0.75` — the standard defaults recommended by Robertson et
al. and used by Lucene since 8.x. The `+1` inside the logarithm keeps the IDF
non-negative even for terms appearing in more than half the documents,
which matters here because the corpus is large and repetitive.

The leg contributes its top 20 to the fusion.

## 4.4 The dense leg — BGE-M3 (`models.py`, `config.py`)

The encoder is `BAAI/bge-m3`, 1024 dimensions, CLS pooling, L2
normalised so that inner product is cosine similarity. It replaced a
general-purpose sentence encoder (`all-MiniLM-L6-v2`), and the replacement was
the single highest-value change in the project.

> **Why the swap mattered.** Retrieval is *asymmetric*: a passage is not
> similar to a question, it answers it. A general-purpose sentence encoder is
> trained with a symmetric similarity objective, and on this corpus
> dense-only retrieval was significantly **worse** than plain BM25. The
> archived baseline is kept in `research/baseline_minilm/` and exposed through
> the `BASE_F_*` / `BASE_MC_*` tokens, so both sides of the comparison are
> bound to measured values rather than to recollection.

`query_prefix` is **empty**, and deliberately so. BGE-v1.5 and the small
instruction-tuned encoders (E5, GTE) expect a query instruction such as
"Represent this sentence for searching relevant passages: ". BGE-M3 does not:
its model card states that the model "no longer requires adding instructions
to the queries", because the asymmetry is handled in training rather than in
the prompt. The setting is kept configurable because the next encoder may
well want one.

## 4.5 Reciprocal Rank Fusion (`hybrid.py`)

```
RRF(d) = SUM over rankings r of  1 / (k + rank_r(d)),    k = 60
```

`k = 60` is Cormack, Clarke & Buettcher (SIGIR 2009), who report it is not
sensitive for `k > 10`. RRF is used rather than score interpolation because
BM25 scores, cosine similarities and cross-encoder logits are on incomparable
scales — summing them requires a normalisation that is itself a choice, and
RRF makes no such choice.

Each leg contributes its top 20. The fused ranking is
then truncated to the rerank pool.

## 4.6 The modality quota (`hybrid.py`)

The quota is a **floor** on the share of the final context occupied by
tables and by charts: `min_table_share = 0.15`, `min_chart_share = 0.05`,
`quota_depth = 10`. A floor, not a ceiling: in industrial corpora the binding
requirement usually sits in a table (EOQ, Incoterms, safety stock, acceptance
criteria), while the top-k dense ranking is dominated by prose because text
chunks are the majority of the corpus and are also the most self-similar.

The algorithm is **swap-based**, and that distinction is the whole design:

* *Rebuild-based* (the first implementation): start from scratch, walk the
  ranking, skip anything that would breach a floor. This silently **removes**
  good high-ranked items and replaces them with lower-ranked ones. Measured
  effect: table recall fell from 0.865 to 0.649 — the quota made retrieval
  worse and looked like a finding about modality balancing.
* *Swap-based* (the current implementation): take the natural top-k ranking
  untouched, then, while a floor is unmet, swap the **lowest-ranked** item of
  the over-represented modality for the **highest-ranked available** item of
  the under-represented one. The context degrades by the smallest possible
  amount and the ranking of everything kept is preserved.

When the corpus does not contain enough of a modality to satisfy the floor,
the shortfall is **reported rather than papered over**. In a corpus that is 88.8% prose there may be no chart chunk worth including at all, and
a system that pretends otherwise is worse than one that says so.

### Where the quota sits, and why it moved

The quota can sit at two points in the pipeline, and the choice matters more
than the threshold:

* **pre-rerank** — the quota proposes a **membership** for the final ten. The
  reranker then re-scores those ten and can reorder them but cannot change
  *which* ten they are, so the forced table chunk survives and the floor
  binds.
* **post-rerank** — the reranker ranks first and chooses the final ten itself,
  and the quota then adjusts the **final** context, typically by importing a
  table chunk the reranker already ranked below the cut.

The measurement settled it: the pre-rerank variant reaches table recall 1.000 with text recall intact, while the post-rerank variant costs
-0.062 in R@10 (p = 1.6 × 10⁻¹). **The quota belongs before the
cross-encoder.** The September 2026 design had it after; that was wrong, and
the ablation is what showed it. **The system now applies the quota
before the cross-encoder**.

The implementation supports both and the ablation measures both, because a
design that only supports the position that works is a design that cannot be
used to discover that the other position does not.

## 4.7 The cross-encoder reranker (`models.py`)

`cross-encoder/ms-marco-MiniLM-L6-v2` scores the fused top 50 against the query; the best 10 are
delivered.

Two things follow from this that are worth stating plainly:

1. **A reranker can only permute what it is shown.** A pool the size of the
   final context cannot improve recall; it can only lose the relevant chunk
   that was sitting just below the cut. The candidate-pool sweep measures
   this: recall@10 peaks at a pool of 10 (0.955) and
   falls to 0.932 at a pool of fifty, because a larger pool costs the
   reranker work and buys nothing.
2. **On this corpus the reranker does not help.** -0.031 in R@10, p =    3.2 × 10⁻¹ — not significant, and the sign is negative. It is kept anyway,
   for two reasons: the gate is calibrated on the reranker's score, and the
   September 2026 report recorded that on the production-scheduling
   sub-category this model *regressed* retrieval by 5.34 points relative to
   RRF alone — which is precisely why the gate downstream is not optional.

## 4.8 The confidence gate (`confidence.py`)

This is the component the thesis is about, so it gets the most detail.

### 4.8.1 The decision

For one query, the gate computes five features of the retrieved set, maps
them through a calibrated logistic model to a posterior
`P(the gold chunk is in the candidate pool)`, and compares that posterior
with an operating point `tau`.

| Feature | What it measures |
|---|---|
| `top1_rerank` | the cross-encoder's score on the best chunk |
| `mean_top3_rerank` | the mean cross-encoder score over the best three |
| `top1_bm25` | the best BM25 score for the query |
| `max_rrf` | the top fused RRF score |
| `n_candidates_above_bar` | how many candidates scored above zero |

The features are standardised by the mean and standard deviation of the
calibration split, then combined by logistic weights that were fitted by
`run_gate.py` on a held-out query split. The fitted artefact — the
standardisation, the weights **and the threshold** — is written to
`artifacts/gate_model.json` and loaded by the framework.

The threshold and the calibration are two halves of one fitted artefact.
Mixing a fitted posterior with a *different* threshold silently changes the
operating point the calibration was measured at, so the framework uses the
threshold stored in the fitted model rather than the configuration default.

### 4.8.2 The gate is a control-flow fact

The generator is **injected** into the framework:

```python
fw = Framework(index, generator=my_model)
result = fw.answer("...")
```

and `answer()` calls it at exactly one line, after the gate has accepted. On
a refusal, the claim assessment and the contradiction detection are skipped
too — so a refused query costs **no model call at all**, and the model is not
merely instructed to be careful.

> "The model was told to be careful" is an instruction, and a model can
> ignore it. "The model was never called" is a fact about the program.
> Before the generator was injected, the harness was trusted to check
> `trace.gate_rejected` before calling the model — a convention, and
> conventions are exactly what a control-flow fact is meant to replace.
> `impl/tests/test_invariants.py::test_the_generator_is_reached_only_through_the_gate`
> asserts it, and `impl/scripts/verify_gate_path.py` demonstrates it against
> the real focus index by instrumenting the call itself.

### 4.8.3 The label, and what the gate is *not*

The positive class is **"the gold chunk is present in the reranked candidate
pool"**. The negative class is therefore dominated by *retrieval failure* — an
answerable query whose evidence the retriever missed — not by absence of
evidence. The gate detects **answer-in-context detectability**; it does not
detect evidence sufficiency, and the deliverables never call it that.

On the focus domain the decomposition is unusually clean: 32 answerable-and-found, 0
answerable-and-missed, 144 unanswerable. The retriever
finds the gold chunk for every answerable question, so the negative class is
almost entirely genuine unanswerability.

### 4.8.4 Calibration and the operating point

| Quantity | Value |
|---|---|
| Brier score | 0.1510 |
| Expected calibration error | 0.1044 |
| Operating point τ | 0.05 |
| Selection rule | the highest τ still answering ≥ 90% of answerable queries |

The threshold sweep is reported in full, together with two degenerate
baselines — never refuse (τ = 0) and always refuse (τ = 1) — because the
endpoints of a sweep are not baselines: the loosest threshold in the sweep
still refuses some unanswerable questions.

### 4.8.5 Refusal, by stratum

The unanswerable class is **not homogeneous**, and pooling it hides the
finding.

| Stratum | n | Refused | Rate |
|---|---|---|---|
| Corpus-anchored (the hard case) | 110 | 26 of 110 | **23.6%** |
| Out-of-domain (trivially unanswerable) | 34 | 26 of 34 | 76.5% |

The out-of-domain family is unanswerable for *any* system that knows what the
corpus is about, so refusing it says almost nothing. The corpus-anchored
family is the real test: the corpus discusses the subject and states no value
for it, so only the retrieved evidence can decide. The gate refuses 23.6% of those.

**The gap between the two strata is the finding.** The gate is good at
*recognising* a recognisable unanswerable question; it is not good at
detecting *absent evidence*, and those are different problems. Reporting the
pooled figure alone would have flattered the system by roughly a factor of
one and a half.

---

# 5. Stage 3 — generation

## 5.1 Per-claim confidence tagging (`claims.py`)

An answer is split into propositions, and each proposition is scored against
the evidence the arm was actually shown. A proposition is supported if a
chunk entails it **or** the evidence states it literally; a **bare value**
(a number with no proposition around it) is scored by the literal test alone,
because the entailment model cannot adjudicate a number that is not a
proposition.

The bands are cut on the probability that the retrieved set entails the claim:

| Band | Condition |
|---|---|
| `grounded` | q ≥ 0.80 |
| `inferred` | q ≥ 0.45 |
| `uncertain` | otherwise |

The information gain of a claim is `1 - H(q)`: a fully supported claim
carries one bit of information, an unsupported one carries none. This is what
makes the per-claim tagging an audit trail rather than a decoration — a reader
can see *which* sentence in the answer is supported and which is not.

## 5.2 Contradiction surfacing (`contradiction.py`)

Two branches must agree before a contradiction is reported:

* **(a) an NLI model** says the two chunks conflict, at probability ≥
  0.70; and
* **(b) a same-subject check** says the two chunks are about the same
  subject — embedding cosine similarity ≥ 0.55 **and**
  Jaccard overlap of shared concrete objects ≥ 0.10.

Branch (b) is what suppresses the false positives a bare NLI gate produces
when two passages discuss different sub-topics, and **both** of its signals
are required. The implementation used to let high similarity through on its
own, which is not what the design says; on a corpus of articles all about one
subject that made the check a *topic* check, and the reader labels found it
to be the source of most of the alarms.

Two further branches are OR-ed in. A **quantity branch** fires when two
passages attach different values to the same measured quantity *of the same
instance* — Plant A's reorder point and Plant B's reorder point are two
reorder points, not one with two values. A **revision branch** fires when two
passages qualify the same term with different versions of the same named
standard; it is exact rather than statistical, so its correctness is a fact
about the text rather than a judgement about it.

The measured effect, on 1,350 pairs:

| Detector | Flagged | Flag rate |
|---|---|---|
| NLI alone | 110 | 0.081 |
| **The shipped gate** | 20 | 0.015 |

The alarms split 20 semantic, 0 quantity and 0 revision.

**Three cautions that must travel with these numbers.**

1. The "corroborated" column is **not a precision**. It is branch
   *agreement*: it decomposes the alarms between the gate's branches and
   cannot credit an alarm that only one of them raised. The precision has
   since been measured against reader labels rather than against a proxy:
   The contradiction gate's precision, measured against reader labels rather than against a proxy, is 0%: none of the 20 labelled alarms was called a contradiction by either annotator, and the 95% upper bound on the gate's true precision is 16.1%. The two annotators do not share a model, both read the sheet blind to the detector's own scores, and both scored 14 of 14 on a control set whose labels are known in advance, and they agree on the contradiction/no-contradiction decision for 101 of the 101 pairs they labelled. The annotators are models rather than people, so the number says the alarms are not confirmed by a reader, not that no reader would ever confirm one.
   
2. The detector's rules were **changed** after that measurement, and the
   changes are part of the result rather than patches to it. The quantity
   branch used to key a number to the nearest distinctive word, and the
   reader labels showed it firing on citation years, version numbers and
   surnames; the subject check used to let topical similarity through on its
   own. The quantity branch now keys a number to a measurement term and
   requires the same instance; the subject check now requires shared concrete
   objects as well as similarity. The quantity-level conflicts fell from    21 to 0 and the gate's alarms from    81 to 20. The corpus, the benchmark and the label standard
   were not changed.
3. **Surfacing is gated on measurement.** Each branch has a measured
   precision, fitted by Experiment 11 and shipped beside the gate's fitted
   model as `conflict_calibration.json`. A branch below the floor has its
   findings recorded and withheld rather than shown. The gate has three branches, each measured separately: the semantic branch's 0 of 20 alarms were accepted as genuine contradictions by both annotators. A branch whose measured precision is below the calibration floor has its findings recorded and withheld rather than shown to a practitioner — the same discipline the answer gate applies to an answer, applied to the framework's own claims.
   The detector's own positive control -- pairs whose correct behaviour is known in advance, written in the industrial register but not drawn from the corpus -- is 11 of 11, with every contradiction caught and every non-conflict left alone. So the mechanism works; this corpus does not test it.

The prevalence of genuine conflict in the compared pairs is 0.0148, and without it a false-positive rate is
uninterpretable — at low prevalence, a detector with good recall still has a
high false-positive rate. Here the prevalence is the deeper problem: the
readers found no contradiction at all in the corpus, flagged or not.

---

# 6. The measurement harness

## 6.1 The corpus and its provenance

The primary corpus — 2,383 chunks over 24 proprietary supply-chain
documents — cannot be redistributed, so every measurement runs on a public
substitute and the substitute ships with its provenance: per-document source
URL, upstream revision id, SHA-256 and chunk count, under CC BY-SA 4.0, in
`deliverables/dataset/`.

The corpus is **industrial-engineering encyclopaedic text**, and it is
described that way everywhere. It is not practitioner documentation, and no
claim in this work depends on it being so. The published RAG literature's
industrial papers all use authentic regulatory or manual documents; claiming
"industrial decision support" from encyclopaedic articles is the objection a
reviewer raises first, and the way to meet it is to say "industrial-engineering
encyclopaedic text" and keep the claims narrow.

## 6.2 The benchmark

Silver-standard: each question carries a gold chunk id and an answerable or
unanswerable label.

| | Focus domain | Six-category corpus |
|---|---|---|
| Queries | 176 | 276 |
| Answerable | 32 | 132 |
| Unanswerable | 144 | 144 |
| Label standard | silver | silver |

The **unanswerable half is corpus-anchored**: the corpus discusses the subject
and states no value for it. That is the hard case, and it is the one the gate
is being tested on.

![Figure 4. Overall Recall@10 against table-specific Recall@10 for the seven ablated systems, focus corpus (black circles, n = 32 answerable: 24 text, 8 table) and industrial corpus (grey squares, n = 247: 117 text, 130 table). The modality quota does not move both axes: on the industrial corpus the pre-rerank quota buys 0.8 points of table recall and gives up 0.8 points of overall recall, and the post-rerank quota lands on exactly the no-quota operating point; on the focus corpus the post-rerank quota gives up 3.1 points of overall recall while table recall stays at 1.000. The quota is a trade, not a gain, and which way it trades depends on where it is applied.](figures/fig4_modality_quota_pareto.pdf)

## 6.3 The claim scorer, and why its error rates are published

The scorer is the instrument that produces the hallucination numbers, so it
is audited by `impl/experiments/validate_claim_scorer.py` and the audit's
error rates travel with the numbers:

| Test | Result |
|---|---|
| The benchmark's own correct answers recognised as supported | 32 of the 33 answers the benchmark itself considers correct are recognised as supported by the evidence that states them |
| Fabricated values rejected | 8 of the 9 fabricated values are rejected |
| Values from other questions rejected | 31 of the 32 values taken from a different quantity are rejected |

Every miss and every leak in that audit is a single-digit value.

> **The scorer was rebuilt once, and the first version was wrong.** The
> original rule — a claim is supported if some chunk entails it at 0.5 —
> silently failed on this benchmark's answer style: `split_into_claims`
> needs three words, so a bare answer like `"69%"` produced *no* claims and
> was recorded as "did not answer", understating every arm's answer rate.
> And the entailment model treats a bare number as an easy entailment — it
> endorsed a fabricated `"37.412%"` at 0.72 against a chunk that never
> mentions the quantity. Entailment alone cannot tell a fabricated value from
> a real one.

> **When the measurement is the contribution, publish the instrument's error
> rates — never assert that a scorer works.**

![Figure 2. Risk-coverage of the confidence gate: the risk that an answered query has no answer in its context, against the fraction of queries the gate answers, on the held-out evaluation half (focus n = 71, industrial n = 178). The degenerate policies bound the curve: always answering carries the base rate of the negative class as its risk at full coverage, and always refusing removes the risk at the cost of all coverage. The industrial gate trades risk for coverage; the focus gate buys almost nothing over answering everything. The fitted operating points (tau = 0.05 focus, tau = 0.40 industrial) answer 0.693 and 0.691 of all queries respectively.](figures/fig2_risk_coverage.pdf)
![Figure 3. Reliability of the gate's calibrated probability against observed answerability, on the held-out evaluation half (focus n = 71, industrial n = 178); the upper panel plots observed answerability against mean predicted probability per bin and the lower panel the number of queries in each bin. The industrial gate tracks the diagonal (ECE 0.075, Brier 0.159); the focus gate does not (ECE 0.1044, Brier 0.1510): it puts most of its queries in the lowest confidence bin, where few of them have an answer in context.](figures/fig3_calibration.pdf)

## 6.4 The two audits, and the repairs

### Audit 1 — the answer labels (Experiment 9)

`audit_answer_side.py` applies *precise* rules: a label is defective only
when the chunk never states the gold as a complete token, or when the gold
does not sit in the named column of the named row. It found
**27 of
132** answerable questions carrying an answer
attached to the wrong question.

The cause was a **generator bug**, not an annotation problem, and the lesson
generalises: when an audit finds a benchmark defect, look for the generator
bug before reaching for an annotation round. Two one-line fixes — the table
generator took its answer from the *next* column while naming the key's own
column, and the numeric regex captured an ordinal as a bare digit ("the 4th
category" → gold "4") — removed every defect. The audit now finds 0 out of 32.

The gold *chunk* was correct in every case, so the retrieval-side
measurements were never affected; only the answer-side accuracy was
depressed, equally for every arm. The benchmark was rebuilt and **every
experiment in the project was re-measured** against it.

### Audit 2 — the unanswerable class (Experiment 12)

The unanswerable half turned out to be **separable from the question text
alone**. A classifier seeing only the query told answerable from
unanswerable at ROC-AUC 0.999, because one family of
unanswerable questions named a fabricated identifier (`SKU AST-5454`) whose
*shape* no answerable question carried — a single regular expression caught
100% of that family with zero false positives. The generator's own comment
claimed the family had "the same surface form as answerable questions"; it
did not.

The consequence was that the headline refusal rate was an **upper bound, not
a measurement**.

The half was **rebuilt, not reported around**. `unanswerable_repair.py`
generates a corpus-anchored class with the same three question stems as the
answerable half, the same source documents, and the same label machinery;
and it gives each repaired question a **structural twin** in the answerable
class — same stem, same subject size, same shape markers, matched
subject-length distribution, no word in common.

| | Before the repair | After |
|---|---|---|
| Question-only separability (ROC-AUC) | 0.999 | 0.608 |
| Bag-of-words separability (ROC-AUC) | 0.985 | 0.646 |
| Gate's refusal rate on the hard class | 91.7% | 23.6% |

**The honest headline changed, and that is the point.** Nobody has published a
question-only separation of an answerable/unanswerable split in a RAG refusal
benchmark; that gap is now the claim. The pre-repair benchmark is preserved
beside the repaired one, and `rerun_pre_repair_gate.sh` regenerates the
pre-repair gate result, so the before/after rests on a generated measurement
rather than on a transcribed number.

Two measurement lessons came out of it:

* read the **ingested chunk text**, not the raw markdown — the ingestion
  expands wiki links, so phrases exist in the chunks and not in the files;
* report a question-only policy's *discrimination* (ROC-AUC), not its raw
  detection rate, because it also flags a large share of the answerable class
  and its apparent detection is mostly explained by the stem.

![Figure 6. The contradiction detector's precision against the base rate of real conflicts in the same population, with 95% Wilson intervals; a filled marker means the point estimate clears the framework's 0.5 calibration floor and the branch would act, a hollow one means it does not and the findings would be withheld. The focus corpus's semantic branch has a precision of 0.0 (0 of 20 alarms confirmed by either annotator) on a base rate of 0.0, so it is withheld; the industrial semantic branch reaches 0.65 (26 of 40) against a base rate of 0.35 and would act.](figures/fig6_contradiction_precision.pdf)

## 6.5 The second corpus: the Electronic Code of Federal Regulations

The first corpus is encyclopaedic (§6.1), and two of this project's
objectives cannot be closed on it: it contains no conflict a practitioner
would recognise as one — a document read at a single upstream revision
cannot contradict itself — and it is not the class of document a practitioner
reads. The second corpus closes both with one artefact.

### The fetcher

`impl/scripts/fetch_ecfr.py` reads the United States *Electronic Code of
Federal Regulations* through the versioner API at
`https://www.ecfr.gov/api/versioner/v1`, and caches the raw XML under
`impl/data/_ecfr_raw/`. The leading underscore keeps the cache out of the
corpus, because the ingester skips underscore-prefixed directories.

The versioner serves any regulation as it stood on any past date. That
single property is what makes the corpus both authentic and versioned: the
text is the regulation a plant is measured against, not a document *about*
one, and the same provision can be read at two dates. Four parts are
fetched:

| Part | Regime |
|---|---|
| 29 CFR 1910 | OSHA general industry |
| 40 CFR 60 | EPA new source performance standards |
| 40 CFR 112 | EPA risk management programmes |
| 49 CFR 173 | DOT hazardous materials |

Three things about the fetcher are worth recording, because each was found
by running it rather than by reading the API's documentation. The versioner
refuses a request that does not advertise a compressed response, so the
`Accept-Encoding` header is mandatory rather than an optimisation; it
returns 502 and 503 often enough on the larger parts that the retry has to
be patient, and there is no smaller request to fall back on; and a
per-section request is refused for identifiers that resolve only through
their part, so the fetch is part-level and the split into sections happens
locally.

The XML-to-markdown conversion is where the corpus's register is decided.
The citation apparatus — `FTREF`, `AUTH`, `SOURCE`, `CITA` and the rest — is
dropped rather than rendered, because §5.2 records that the earlier
measurement found the source of every false numeric conflict: a citation
like "Dettmer H., 1998" was read as a quantity. Tables are converted to
markdown, and a merged cell is rendered as a single column with the others
left empty, because an irregular markdown table confuses both the model and
the tokenizer. The corpus holds **110 documents** and
**2,443 chunks** in **4 regulatory regimes**.

The corpus is public domain — a work of the United States government — so
the licence question the limitations table names does not arise for it, and
it ships with the thesis: `impl/data/corpus_industrial/` holds the corpus
and its manifest, and `impl/data/benchmark_industrial/benchmark.json` holds
the benchmark.

### The benchmark and its audit

`impl/scripts/build_industrial_benchmark.py` writes **444
queries** — **247 answerable** and
**197 unanswerable** — at the same silver label standard
as the first benchmark: mechanically derived from the document that answers
them, with the unanswerable class drawn from the same stems and the same
documents.

The same audit as §6.4's Audit 2 was run on it, by
`impl/experiments/audit_unanswerable_class.py`, and the numbers are better
in one respect and worse in another.

| Measurement | Value |
|---|---|
| The one-rule identifier shortcut | 0 of 197 unanswerable questions caught |
| Question-only classification, ROC AUC | 0.708 against a permutation null of 0.505 |
| Bag-of-words separability, ROC AUC | 0.793 |
| Median question length, answerable / unanswerable | 73 / 50 characters |

**The shortcut is gone; the residual is not.** The single regular expression
that carried 76.4% of the first benchmark's unanswerable
class catches none of this one, because the industrial benchmark's
unanswerable questions name real subjects the corpus discusses and states no
value for. But the two classes remain weakly separable from the question
text alone, and the residual tracks question length: the answerable
questions are the longer ones.

That residual is stated rather than hidden, and it bounds what this
benchmark can be used for. The identifier shortcut that made §6.4's
pre-repair headline an *upper bound* is gone, so the refusal rate measured
here is no longer inflated by that artefact. But the classes remain weakly
separable from the question's shape, so a policy that read only the shape
could still score a non-trivial refusal rate without looking at any
evidence. The benchmark therefore certifies that the unanswerable class is
not shortcut-separated; it does not certify that a refusal was
evidence-driven — and the second corpus is used here for what it does
establish cleanly, a corpus that contains conflicts.

### The revision corpus

The same sources, read at **2021-12-31** and
**2026-06-01**.
`impl/experiments/build_revision_candidates.py` aligns paragraphs across
the two snapshots by token-set overlap — the minimum overlap for a block to
count as the same paragraph across vintages is a fixed threshold in the
script — and keeps the aligned pairs whose text changed:
**948 amended-paragraph pairs**, of which
**361 (38.1%)** state different numbers in
the two vintages.

That count is not recoverable from the evaluation's own output, because the
evaluation scores a mined subset of it, and it used to live in the builder's
console output — exactly the kind of number that later drifts without anyone
noticing. `impl/experiments/summarise_revision_corpus.py` recomputes it
from the cached XML, using the builder's own alignment and numeric-change
functions, and writes it to
`impl/results_industrial/exp21_revision_corpus_stats.json`, so the papers
and the write-ups bind it to a token like every other measurement.

### The mining rule, and why it is the rule that matters

The candidate pairs the detector is scored on are two strata:
**90 revision pairs** (a paragraph and its
amended self) and **150 similar pairs**
(cross-document retrieval neighbours, which carry the false-alarm load).

The pool is mined by the **retriever's** own lexical signal and never by the
detector's numeric rule, its NLI probability or its subject check. This is
the single most consequential methodological decision in the second corpus,
and it has one reason: **a pool selected on the detector's decision rule
cannot measure the detector's precision, because every alarm would be in
the pool by construction.** The precision estimate would be the detector's
opinion of itself.

### The construction labels

`impl/experiments/annotate_construction_labels.py` labels the revision
stratum **without any annotation at all**. The same provision at two issues
is a *supersession*; where the two versions state different unit-bearing
quantities, it is a *quantity conflict*. Their type is known by
construction, so they need no reader and no agreement statistic.

The selection criterion is deliberately weaker than the detector's. It asks
whether a unit-bearing number differs, and nothing about whether that number
is governed by a declared measurement term, and nothing about the subject
and instance checks, which the detector requires. A detector that fails on
this stratum has failed on a real ambiguity, not on a tautology. A number
without a unit is not a quantity — in a regulation the bare numbers are
paragraph markers — so the unit is required.

### The reader panel

`impl/experiments/build_annotator_panels.py` writes one sheet per
regulatory regime, plus a generalist control on the same rubric.
`impl/experiments/run_revision_eval.py` scores the detector against the
panel's labels.

The generalist control is not a nicety: without it the rubric's
contribution and the specialisation's contribution cannot be separated,
because a panel could be agreeing with the reference for either reason.
The panel is **blind**: the sheet carries the rubric, the two passages and
the pair id, and never the detector's NLI probability, its similarity, its
numeric-conflict list or the stratum the pair came from.

### The rubric factorial

`impl/experiments/build_rubric_factorial.py` and
`impl/experiments/run_rubric_factorial.py`.

The first comparison of the two rubrics was **confounded**, because the
old-rubric reader was the generalist — so "old rubric" and "generalist" were
the same cell, and the decisive cell, specialist readers on the old rubric,
was never measured. The factorial separates them. The v1 rubric and its
instructions are taken **verbatim from the original judge input**, so the
v1 arm is the rubric as it actually was and not a reconstruction; the pairs,
the detector, the regime assignment and the regime briefs are identical
across cells; and a model-matched cell has the same reader model read both
rubrics, which removes the second confound the panel's earlier session had
left open.

Cells: generalist 0.293 → 0.659, specialist 0.341 → 0.659, in detection precision.
Effects: rubric +0.366 and
+0.317, specialisation +0.049 and
+0.000.

The mechanism is concrete. The old rubric required a version marker, and a
regulation does not write its own version in its text, so it missed
**63** of the
**82** supersessions it was asked to find,
and called them no-conflicts.

### The API generator harness

`impl/scripts/prepare_generator_sheet.py` builds the sheet — the question
and the retrieved passages, in the shipped format and under the shipped
prompt — and `impl/scripts/run_generator_api.py` calls the generator. The
key is read from `~/.mtp_llm_key` through the shell wrapper, so it never
appears on a command line, in a process listing or in a transcript.

`impl/scripts/relabel_failed.py` re-runs a judge's failed claims at a
larger output budget, and merges the result into its label file; the claims
the judge already labelled are untouched, so the merge cannot change a label
the judge did make. The re-run is necessary because a reasoning model can
spend its whole output budget thinking and return no text — which is neither
a label nor a refusal, and is recorded as its own status rather than
counted. That is also why `label_claim_bands_model.py` reads its output
budget from configuration rather than hard-coding it.

### The figures

`impl/scripts/make_figures.py` builds six figures from the result JSONs
into `deliverables/figures/`, as a vector PDF for LaTeX and as a PNG for
review. Every figure is read from a result file; where the result file
carries an interval it is plotted as an interval, and where it carries
none, none is drawn. Each figure is one column wide, and the width guard
**fails the build** rather than warns: a figure that overflows the column is
invisible in the PNG until the PDF is placed, and a check that reports and
continues is a check that does not check.

### The verification script

`impl/scripts/verify_reported_numbers.py` re-derives every quoted number
from the result files and checks that the shipped documents carry them. It
exists because the write-ups drifted from the artefacts once, and because
the one artefact the thesis's audit discipline rests on used to live in
`/tmp`, where a reboot would have destroyed it.

---

# 7. The experiments

Each experiment is a script under `impl/experiments/` that writes a JSON
result file and a markdown summary. `34` experiment scripts in
total. They are run by `impl/scripts/rerun_focus.sh` and `rerun_all.sh`.

| # | Experiment | What it measures | Result file |
|---|---|---|---|
| 1 | `run_ablation.py` | the seven-rung retrieval ablation, paired Wilcoxon between rungs | `exp1_ablation.json` |
| 2 | `run_gate.py` | the gate's calibration, threshold sweep and refusal by family | `exp2_gate.json` |
| 3 | `run_contradiction.py` | the contradiction detector's behaviour | `exp3_contradiction.json` |
| 4 | `run_transfer.py` | cross-category transfer of the calibration | `exp4_transfer.json` |
| 5 | `run_pool_size.py` | the rerank candidate-pool sweep | `exp5_pool_size.json` |
| 6 | `run_focus_case.py` | the focus-domain before/after case study, question by question | `exp6_focus_case.json` |
| 7 | `run_long_context.py` | the long-context baseline arm | `exp7_long_context.json` |
| 8 | `run_generation_eval.py` | the generator-side comparison | `exp8_generation.json` |
| 8b | `validate_claim_scorer.py` | the audit of the claim scorer | `exp8_scorer_validation.json` |
| 9 | `audit_answer_side.py` | the audit of the answer labels | `exp9_label_audit.json` |
| 10 | `run_form_validator.py` | the form validator's error rates | `exp10_form_validator.json` |
| 11 | `run_form_probe.py` | what the gate does with *malformed* stems | `exp9_form_probe.json` |
| 12 | `audit_unanswerable_class.py` | the audit of the unanswerable class | `exp12_unanswerable_class_audit.json` |
| 13 | `label_contradiction_pairs.py` + `label_contradiction_pairs_model.py` | the contradiction gate's precision, against reader labels | `exp11_contradiction_precision.json` |

## 7.1–7.2 Ablation and gate

Reported in the status report, §5.1 and §5.2. The ablation's seven rungs are
BM25 only, dense only, hybrid RRF, hybrid + rerank, + category filter, +
quota pre-rerank, + quota post-rerank.

## 7.3 Contradiction

Reported in §5.2 of the status report and §5.2 above.

## 7.4 Cross-category transfer

Three arms, each evaluated on the queries it is about:

| Metric (held-out half) | Transferred | Refitted (ceiling) |
|---|---|---|
| Answerable answered | 1.000 | 0.940 |
| Coverage | 0.412 | 0.460 |
| Top-1 accuracy given accepted | 0.940 | 0.952 |

Tuning half: predictive_maintenance, production_scheduling, supply_chain_management. Held-out half:
facility_layout, quality_engineering, reliability_engineering. τ fitted on the tuning half and transferred
unchanged: 0.05.

**The scope is narrower than "transfer" usually means, and it must be stated.**
The split is over *document categories*, and the benchmark's unanswerable
questions carry no category — they are not "about" a category — so neither
half contains any. This experiment therefore measures **coverage on the
answerable questions across domains**. It says nothing about how well a
transferred threshold refuses unanswerable questions, because that population
is not in the split. The refusal behaviour is measured on the focus domain
instead.

What transfers is the **ordering**, not the operating point: top-1 accuracy
given acceptance moves from 0.952 (refitted) to 0.940 (transferred), while coverage falls from 0.460 to 0.412. The practical
finding: **re-fit τ per corpus; do not expect to re-use it.**

> **A defect found in this experiment by inspection, and repaired.** All three
> arms were originally evaluated over *every* query in the corpus rather than
> over their own halves, and the "transferred" arm scored the held-out
> queries with the model fitted on the held-out half. The denominators
> proved it: all three arms reported `n_answerable = 132`, the whole
> benchmark, where a half is 66. Nothing was transferred; the labels were
> wrong. A second instance sat in the fixed-τ comparison, where the
> "refitted" column was computed by the same call as the "transferred" one.
> Both are fixed, and the numbers in the table above are post-repair.

![Figure 1. Recall against the size of the rerank candidate pool, on the focus corpus (black circles, 32 answerable of 176 queries) and the industrial corpus (grey squares, 247 of 444). The focus curve saturates at a pool of 10, where Recall@10 = Recall@20 = 1.000, and then falls slightly as the reranker is given more candidates to reorder. The industrial curve does not saturate at 10: there Recall@20 reaches 1.000 at a pool of 50 while Recall@10 stays at 0.988, so 1.21 points of gold are retrieved and then pushed out of the ten-chunk context.](figures/fig1_pool_size.pdf)

## 7.5 The before/after case study (Experiment 6)

An ablation table says what each mechanism does to a metric. Experiment 6
answers the question a practitioner actually asks: *what does the whole
framework do to my questions, compared with a plain retriever that never
refuses?* Two arms on the same 176 focus-domain questions.

| | Plain BM25 retriever | The full framework |
|---|---|---|
| Unanswerable questions **answered** (all wrongly) | **144 of 144** | **86 of 144** |
| Answerable questions answered | 32 of 32 | 30 of 32 |
| Gate refusal rate on answerable questions | 0.0% | 0.062 |
| Gate refusal rate on unanswerable questions | 0.0% | 0.403 |
| Context contains the gold chunk | 0.969 | 0.938 |
| Mean chunks in the accepted context | — | 9.4 |

The last row is the one that keeps the claim honest. On silver-standard
labels a plain lexical retriever already puts the gold chunk in the top ten
more often than the full framework does
(0.969 against 0.938): **the
framework is not better at retrieving, and it is not trying to be.** The gate
is there to refuse, and the price of refusing is paid in coverage — which is
the trade the whole thesis is about.

The experiment also records, for every question, the complete pipeline state
twice — before (the plain lexical retriever) and after (every stage) — so any
single question can be traced end to end: the two retrieval legs, the fused
ranking, the reranked ranking, what the gate decided and on which signals,
which chunks the quota swapped, how each claim was banded, and whether any
two accepted chunks contradict each other.

## 7.6 The candidate-pool sweep

| Rerank pool | R@10 | R@20 | MRR | nDCG@10 | Table R@10 |
|---|---|---|---|---|---|
| 5 | 0.902 | 0.902 | — | — | — |
| 10 | 0.955 | 0.955 | — | — | — |
| 20 | 0.932 | 0.962 | — | — | — |
| 50 | 0.932 | 0.939 | — | — | — |
| 100 | 0.932 | 0.947 | — | — | — |

Recall@10 peaks at a pool of 10 and then declines: a larger pool
costs the reranker work and buys nothing, because a reranker can only
permute what it is shown. The peak-minus-last difference is
+0.023.

## 7.7 The long-context baseline

The strongest threat to the work. Two corpora, two halves of the comparison.

**The cost half** needs no generator:

| | Focus domain | Six-category corpus |
|---|---|---|
| Whole corpus as a prompt | 202,529 tokens | 680,417 tokens |
| RAG arm's accepted context | 2,246 tokens | 2,399 tokens |
| Ratio | 90× | 282× |
| Fits a 128K window | **no** | **no** |

**The retrieval-side proxy**: with the candidate set widened to every chunk
in the corpus, the gold chunk still lands in the scorer's top 10 for 0.969 of focus-domain queries (95% interval 0.843-0.994) at a
median rank of 1.  The same proxy on the six-category corpus puts the gold chunk in the top 10 for 0.902 of the queries (0.839-0.942), at a median rank of 1.

**The answer-quality half** is measured with a generator, and
measured on cost on both corpora and on quality on the focus domain. The answer-quality half of the comparison was measured on the focus domain. With the whole corpus in the prompt the generator answered 31 of 32 answerable questions, the same coverage as the pipeline, and it declined the unanswerable questions at a comparable rate (76 of 144 against 77 of 144), for 74 times the input actually sent per query. On coverage and on cost the result is settled: the whole-corpus prompt declines no more unanswerable questions than the pipeline does and costs 74 times as much to do it. On answer quality the margin is directional but not statistically significant once the answers are scored without the length confound.

## 7.8 The generator-side comparison

The experiment that tests the framework's own hypothesis, and the one that had
to be rebuilt twice.

**The design.** One generator behind five arms that share the model, the
prompt wording, the question set and the scorer. Any difference between them
is attributable to the context and the gate and to nothing else.

**Under the cautious prompt** — the generator is permitted to decline.

| Arm | Unanswerable answered | Answerable answered | Answerable accuracy |
|---|---|---|---|
| `rag_nogate` — the same retrieval, gate removed | 0.535 (77 of 144) | 30 of 32 | 0.633 |
| `rag@fitted` — the framework at its fitted operating point | 0.417 (60 of 144) | 30 of 32 | 0.800 |
| `rag@random` — refuses the same number, picked at random | 0.375 (54 of 144) | 21 of 32 | 0.714 |
| `rag@transferred` — the threshold transferred from the cross-category half | 0.014 (2 of 144) | 6 of 32 | 0.333 |
| `long_context` — the whole corpus in the prompt | 0.528 (76 of 144) | 31 of 32 | 0.548 |

**Under the answering prompt** — the generator is *required* to answer, so it
cannot decline on its own and hand the gate the credit. This is the
condition in which the gate's own contribution is measurable, and it is the
decisive one.

| Arm | Unanswerable answered | Answerable answered | Answerable accuracy |
|---|---|---|---|
| `rag_nogate` — the same retrieval, gate removed | 0.938 (135 of 144) | 32 of 32 | 0.656 |
| `rag@fitted` — the framework at its fitted operating point | 0.528 (76 of 144) | 30 of 32 | 0.667 |
| `rag@random` — refuses the same number, picked at random | 0.604 (87 of 144) | 21 of 32 | 0.714 |
| `rag@transferred` — the threshold transferred from the cross-category half | 0.021 (3 of 144) | 6 of 32 | 0.000 |
| `long_context` — the whole corpus in the prompt | 0.931 (134 of 144) | 32 of 32 | 0.406 |

**The paired, question-by-question test** — the discordant pairs, with the
exact two-sided McNemar test on them:

| Arm | Question set | b | c | p |
|---|---|---|---|---|
| `rag@fitted` | unanswerable | 60 | 1 | < 0.001 |
| `rag@fitted` | answerable | 2 | 0 | 0.500 |
| `rag@random` | unanswerable | 50 | 2 | < 0.001 |
| `rag@random` | answerable | 11 | 0 | 0.001 |

`b` is the number of questions the ungated arm answered and the gated arm
refused; `c` is the reverse.

**The replication on a second generator could not be run.** One generator
behind five arms settles the hypothesis for one model, so the whole design was
repeated on a second one, changed in nothing but the model id. Experiment 13 measured why, on the benchmark's own
questions: MiniMax-M3 returned no text on 0 of the 66 questions it was asked (0 of them on the benchmark's table-lookup family, against 0 of 22 on a control sample of the other families); MiniMax-M3.1-Flash returned no text on 24 of the 66 questions it was asked (23 of them on the benchmark's table-lookup family, against 1 of 22 on a control sample of the other families). The failures are not a shortage of output budget -- of the requests that came back empty, 13 were rescued by retrying at 4096 tokens and 11 were still empty there, the model spending the whole budget on reasoning and returning nothing. An empty completion is neither an answer nor a refusal, so the harness records the run as not-run instead of reporting a rate it cannot stand behind.

| Generator | No text returned | Of which on the table-lookup family | Of which on a control sample of the other families |
|---|---|---|---|
| MiniMax-M3 | 0 of 66 | 0 of 44 | 0 of 22 |
| MiniMax-M3.1-Flash | 24 of 66 | 23 of 44 | 1 of 22 |

Three consequences, and they are worth separating.

1. **The gate's contribution is established on one generator.** The
   replication that would settle it for a second is open, and its obstacle is
   now specific rather than vague: a generator that returns text on the
   benchmark's table questions.
2. **An empty completion is a third outcome, and it is not an answer.** The
   harness raises on it rather than recording "did not answer", because
   recording it either way would put a rate in the deliverables that the
   measurement does not support. A run whose arm asked fewer questions than
   the benchmark holds is recorded as not-run, with the reason.
3. **The gate is upstream of the failure.** It refuses before the generator is
   called, so a generator that cannot answer costs nothing on the questions
   the gate rejects.

There is a reproducibility statement here as well, and it is this project's
own: the shipped run was made with MiniMax-M3 in November, and the row above
is the same model id, on the same corpus, with the same prompt, measured now — 0 of 66 of its requests came back with no text. The shipped
measurement is therefore still reproducible against the provider's route; what
is not reproducible is a *second* generator, and the reason is a property of
that model rather than of the measurement. That is why the per-question
records ship with the results rather than only the summaries.

**This is where the two arms come apart.** On the unanswerable questions the
gate and the random control both refuse substantially, and both reductions
are significant. On the **answerable** questions the gate's refusals cost it
almost nothing (2 of the questions the ungated arm
answered, p = 0.500), while the random control's
refusals cost it significantly (11 of them, p = 0.001). The confidence score is what makes the
difference, and the question it answers is *where the refusals land*.

**Three design decisions, and why each was necessary.**

1. **The prompt is an axis, not a constant.** The first version ran under one
   prompt and produced a null — and the null was an artefact of the design.
   Under the cautious prompt the generator declined the unanswerable questions
   on its own, so the gate's refusals were redundant and the arms could not be
   told apart. The harness now runs the same experiment under two conditions
   differing by **one sentence** — the permission to decline — with the model,
   the questions, the retrieval and the scorer identical.
   two of the two conditions has been run, and the
   hypothesis holds under each.

2. **A random-escalation control arm.** It refuses the same *number* of
   questions as the fitted gate but picks them at random, ignoring the
   confidence score. The difference between it and the fitted gate is exactly
   what the *confidence score* buys over refusing an arbitrary set of the same
   size. This is the control arXiv:2610.20634 prescribes, and that paper's
   own result is that the random control **matches** the confidence-gated
   cascade.

   The measured difference is worth stating precisely, because the obvious
   phrasing of it is wrong. The random set is drawn from *every* question, so
   the control spends part of its refusal budget on answerable questions.
   Under the answering prompt it answered 21 of 32
   answerable questions against the fitted gate's    30 of 32, and it answered    87 of 144 of the unanswerable ones against the
   gate's 76 of 144. So the control's raw answer rate
   on the unanswerable class is *lower* than the gate's — it refuses more of
   them, by luck. The confidence score does not buy a lower answer rate on
   unanswerable questions; the random arm has that too. What it buys is
   **where the refusals land**, which shows up as coverage on the answerable
   questions and is established by the paired test on that set. That is the
   quantity the control exists to isolate.

3. **A paired, question-by-question test.** The McNemar exact test on the
   discordant pairs, not a comparison of two independent rates.

**The verdict.** The gate's contribution is measured under both prompt conditions, and it holds in both. Under the cautious prompt -- the deployed system -- the hypothesis is supported, at a price: the gate reduced the rate of answering unanswerable questions from 0.535 to 0.417, a fall of 11.8 points, at the cost of answering 30 of 32 answerable questions. Paired question by question, the gate refused 23 of the questions the ungated arm answered and let through 6 of the ones it did not (exact McNemar p = 0.002). Under the answering prompt, which differs from the cautious one by a single sentence and by nothing else, the hypothesis is supported, at a price: the gate reduced the rate of answering unanswerable questions from 0.938 to 0.528, a fall of 41.0 points, at the cost of answering 30 of 32 answerable questions. Paired question by question, the gate refused 60 of the questions the ungated arm answered and let through 1 of the ones it did not (exact McNemar p = < 0.001). What the framework claims is therefore not that the gate reduces hallucination whatever the generator does, but that it is the one component whose behaviour does not depend on the generator's cooperation: the prompt can be wrong, and the gate still holds.

**The gate's cost and benefit, counted from the records.** The summary
blocks report an accuracy over the questions an arm *answered*, which a gate
raises by declining the hardest questions — a selection effect that must not
be read as a quality gain. Counting from the per-question records instead
gives the trade directly, under the answering prompt:

| Arm | Questions answered | Correct (entailment) | Correct (key term) | Confidently wrong |
|---|---|---|---|---|
| `rag_nogate` — gate removed | 167 | 21 | 29 | 135 |
| `rag@fitted` — the framework | 106 | 20 | 27 | 76 |
| `rag@random` — same count, at random | 108 | 15 | 20 | 87 |
| `long_context` — the whole corpus | 166 | 13 | 24 | 134 |

The gate costs 1 correct answers on the
entailment test (2 on the key-term
test) and removes 59 confidently-wrong
answers. The two correctness tests disagree about the size of the cost, which
is why both are reported.

Three readings of this table, and they are the ones a panel will offer:

1. **The gate is not an accuracy mechanism.** It costs one or four correct
   answers out of 21 and buys the
   removal of 59 wrong ones. Its value is in
   the second column, not the first.
2. **The per-answer accuracy advantage is a selection effect.** The gate
   declines the hardest questions, so the questions it does answer are
   easier. Under the cautious prompt the gate even ends up *ahead* on the
   entailment test (24 against    19) while removing    17 wrong answers — which is exactly why the
   cautious condition alone would have been a misleading headline.
3. **Refusing is not the gate's contribution; refusing the right questions
   is.** The random control refuses about as much and gets    15 correct answers against the gate's    20, and leaves    87 wrong answers against the
   gate's 76.

Whether the trade is worth making is a domain judgement, not a statistical
one, and the framework's contribution is that it is now measured at a stated
operating point under two prompt conditions rather than asserted.

**The two columns that answer different questions.** `answer_rate` is how
often the arm answers at all when the answer does not exist — the *opportunity*
for hallucination. `claim_hallucination_rate` is of the claims it did produce,
how many are supported by nothing in the evidence it was given —
*fabrication*. A system that refuses everything scores zero on the second and
is useless, so the first is the headline. And the fabrication column has
almost no denominator: across the arms the unanswerable questions produced
only a handful of substantive claims, so that column is four or five claims
wide and must not be read as a finding.

## 7.9 The audits and the probes (Experiments 8b, 9, 10, 11, 12)

Reported in §6.4 above and in the status report §9.

The **form probe** (`run_form_probe.py`) is worth naming here because it
answers a question a panel always asks: *does the gate reject bad questions?*
It harvests the real rejected stems by re-running the generator's extraction
and pushes them through the pipeline. The gate **accepted** the majority of
them — 76.7% on the focus domain, at a mean posterior of 0.323 against τ = 0.05, against a refusal rate of 23.6% on genuinely unanswerable questions.

So: **the gate is good at "is there evidence here?" and no use at "is this
even a question?"** The form validator is the component that does the latter,
and it must never be credited with the former.

### The contradiction precision, measured against reader labels (Experiment 11)

`impl/experiments/label_contradiction_pairs.py` samples the pairs the gate
flagged plus a simple random sample of the pairs it did not, writes a
labelling sheet with the rubric attached
(`impl/experiments/data/contradiction_label_rubric.md`), and scores a filled
sheet into a precision and a recall estimate with 95% intervals.

Two annotators labelled the sheet. They are **models, not people**, and they
do not share a model family: `label_contradiction_pairs_model.py` calls the
provider the generation experiment already uses, through
`impl/scripts/run_contradiction_labeling.sh` (which reads the key from
`~/.mtp_llm_key`, so it never appears on a command line); the second
annotator is a separate instruction-tuned model reading the same rubric.
Both were **blind**: the sheet they read carried the rubric and the two
passages and nothing else, so neither could anchor on the detector's NLI
probability, its topical similarity, its numeric-conflict list or the
stratum the pair came from. Each was checked on a 14-pair control set whose correct labels are known
in advance, and each scored 14 of 14.

The contradiction gate's precision, measured against reader labels rather than against a proxy, is 0%: none of the 20 labelled alarms was called a contradiction by either annotator, and the 95% upper bound on the gate's true precision is 16.1%. The two annotators do not share a model, both read the sheet blind to the detector's own scores, and both scored 14 of 14 on a control set whose labels are known in advance, and they agree on the contradiction/no-contradiction decision for 101 of the 101 pairs they labelled. The annotators are models rather than people, so the number says the alarms are not confirmed by a reader, not that no reader would ever confirm one.

The gate has three branches, each measured separately: the semantic branch's 0 of 20 alarms were accepted as genuine contradictions by both annotators. A branch whose measured precision is below the calibration floor has its findings recorded and withheld rather than shown to a practitioner — the same discipline the answer gate applies to an answer, applied to the framework's own claims.



### The detector's own positive control (Experiment 11b)

A measurement of zero on a corpus with no positives cannot distinguish "the
detector is broken" from "there is nothing to detect". Experiment 11b is
what distinguishes them. `impl/experiments/contradiction_control.py` runs
the **shipped** detector — the real encoder, the real NLI model, the real
thresholds — over a set of pairs whose correct behaviour is known in
advance: five contradictions, two revision conflicts, two compatible pairs
and two pairs about different subjects. The pairs are written in the
industrial register but are not drawn from the corpus.

The detector's own positive control -- pairs whose correct behaviour is known in advance, written in the industrial register but not drawn from the corpus -- is 11 of 11, with every contradiction caught and every non-conflict left alone. So the mechanism works; this corpus does not test it.

The result is 11 of 11. So the
mechanism works, and this corpus does not test it.

### What the calibration does

The measured precision of each branch is fitted by the labelling experiment
and written to `conflict_calibration.json` beside the gate's fitted model.
The pipeline reads it and withholds the findings of any branch whose measured
precision is below the floor. On this corpus that leaves
**20 findings surfaced and 0 withheld**:
the system is silent about conflicts here, and it is silent because the
measurement says it should be.

Three consequences for how the rest of this document is read. The corroboration
shares in §5.2 are a decomposition of the alarms between the gate's branches
and not evidence that the alarms are right. The "verifiable subset" whose
recall the experiment reports as 1.000 **by construction** is not verifiable:
the annotators do not read its members as contradictions, so the number is a
property of the subset's definition rather than of the detector. And the
mechanism itself cannot be evaluated on this corpus, because the corpus does
not contain contradictions — the same readers find none in a random sample of 80 pairs the gate did not flag. The label
distribution inside the alarms says where the failures are: 1 to 4 of the 20 alarms are pairs
about *different subjects* that branch (b) should have suppressed, and 16 to 19 are pairs that do not disagree at all, which is
the NLI model being wrong. Both are fixable with instance-level data, and
this corpus has none.

![Figure 5. A classifier that sees only the question text, with no retrieval, no evidence and no corpus, telling an answerable question from an unanswerable one. Before the repair the two classes were separable almost perfectly on the focus corpus (ROC AUC 0.999, against a permutation null of 0.455 +/- 0.072), and one regular expression for a fabricated identifier caught 76.4% of the unanswerable questions with no false positive at all. After the repair the shortcut catches nothing, and what is left of the procedure's power is small but not zero: AUC 0.608 on the focus corpus (p = 0.050) and AUC 0.708 on the industrial corpus (p = 0.010). On the better-powered six-category corpus it is indistinguishable from chance: AUC 0.533 (p = 0.267). The benchmark's unanswerable class is decidable from the evidence rather than from a question-shape rule, but on two of the three corpora it is not free of form-only separability.](figures/fig5_question_only_roc.pdf)

## 7.10 The contradiction detector on a corpus that contains conflicts

The precision reported in §5.2 and §7.9 was measured on a corpus with no
positives, so it measured the corpus rather than the mechanism. The
industrial corpus contains conflicts, and the evaluation is the same
detector, the same configuration and the same mining rule, over
**240** pairs.

**The two strata.** 90 revision pairs and
150 similar pairs (§6.5). **The panel.** One
reader per regulatory regime, plus a generalist control, blind to the
detector. **The two profiles.** The detector's measurement and version
vocabularies were declared for operations and supply-chain prose; a
regulatory corpus binds on "permissible exposure limit" and cites
"ASTM A47-68". The `shipped` profile is the one in production, and the
`regulatory` profile is the extension the industrial measurement motivates.
Both are reported, because the interesting number is the difference between
them.

A conflict detector's precision is **two** numbers, not one.

| Profile | Detection | Typing |
|---|---|---|
| `regulatory` | 0.659 (95% CI 0.505–0.784) | 0.073 (95% CI 0.025–0.194) |
| `shipped` | 0.650 | 0.000 |

*Detection* asks whether the alarm is pointing at something real. *Typing*
asks whether the branch that raised the alarm is the branch that owns the
conflict. The two are far apart, and the gap is the finding: the mechanism
**finds** the conflicts and **reports them as the wrong kind**. It calls
supersessions contradictions, and it cannot say which version is in force —
because nothing in the retrieved passages says which issue either of them
is.

Against the **construction labels** (§6.5), whose conflict type is known
without any judgement, the separation is starker still: detection is
**1.000** and typing is
**0.000**. Every alarm the detector raises on the
revision stratum points at a real conflict, and not one of them was raised by
the branch that owns it.

The detector raised **41** alarms on the 240 pairs, and it recovers 0.321 of the
conflicts the panel labelled. Over the labelled set the panel's verdicts
were 84 supersessions, 90 term mismatches and 64 no-conflicts.

> **What this does not repair.** The typing figure is a null that the corpus
> can explain on its own. The retrieval context is two passages and nothing
> else; a passage of a regulation does not carry the date of the issue it
> came from, so no branch can attribute a conflict to the version that
> superseded it. The detector's job — say *these two passages disagree* — is
> one it can do; the job of saying *this one is the version in force* is one
> the retrieved evidence does not contain. That is a limitation of the
> evidence, not a defect of the branch, and it is why the branch is reported
> as withheld rather than as wrong.

## 7.11 The rubric × specialisation factorial

The measurement's binding constraint was the annotation rather than the
detector, and the first attempt to show that was **confounded**: the
old-rubric reader was the generalist, so "old rubric" and "generalist" were
the same cell, and the decisive cell — specialist readers on the old rubric
— was never measured. §6.5 describes the design; the numbers are:

| Reader | Rubric | Detection precision |
|---|---|---|
| Generalist | v1 (the original) | 0.293 |
| Generalist | v2 (sharpened) | 0.659 |
| Specialist | v1 (the original) | 0.341 |
| Specialist | v2 (sharpened) | 0.659 |

| Effect | Δ detection precision |
|---|---|
| Rubric, at the generalist cell | +0.366 |
| Rubric, at the specialist cell | +0.317 |
| Specialisation, at the old rubric | +0.049 |
| Specialisation, at the sharpened rubric | +0.000 |

**The rubric's wording moved the measured precision; the reader's
specialisation did not.** The rubric's effect is several times larger than
the specialisation's at both levels of the reader factor, and the
specialisation effect is zero at the sharpened rubric.

The mechanism is concrete. The old rubric required a version marker, and a
regulation does not write its own version in its text, so the generalist on
the old rubric missed 63 of the 82 supersessions the sharpened rubric
found, calling them no-conflicts; the specialist on the old rubric missed 63 of 90.

Three qualifications are owed to this result.

1. The rubric changed the **definition** of the target as well as the
   procedure for recognising one, and this experiment cannot separate the
   two. What it shows is that the reader factor is small.
2. "Specialisation" here was delivered as a brief to a fixed reader model,
   not as a different capability. The claim is that a brief plus a sharpened
   rubric buys nothing over the rubric alone — narrower than "specialists
   are not needed".
3. The qualitative principle is already published: the annotation guideline
   is a first-class error source in model annotation. What is new is that
   the effect lands on the **reported system measurement** rather than only
   on the labels.

> **The generalisable lesson is about measurement, not about annotation.** A
> number that moves this far with the wording of its own rubric is not yet a
> measurement of the thing under test.

## 7.12 The quantity stratum

`impl/experiments/run_quantity_stratum.py`.

The quantity branch fires when two passages attach different values to the
same measured quantity. On the 240-pair revision corpus it did
not fire at all, on a stratum that contained limit changes where the rule
demonstrably changed a number. Two explanations are possible and they call
for opposite conclusions: the branch is broken, or there is nothing for it
to fire on.

The corpus is searched directly. Every (measurement term, value) pair in
every document is grouped by term, and a term whose values differ **across
documents** is a candidate conflict — over **64** measurement
terms, giving **1776 candidates**. The search is
**exhaustive over the corpus rather than sampled**, so the count is exact
rather than an estimate, and it is the answer to "how many are there?" that
a sampled evaluation cannot give.

**119** of those pairs went to the reader, and the branch
fired on **13**. Of the **60** labelled
pairs, **none** was a genuine quantity conflict.

The search is deliberately over-inclusive: two passages about different
boilers share the word "pressure". So the count is an upper bound on the
conflicts that exist, and the reader's job is to separate them — which is
why the judge's verdict, and not the search's tally, is the number that
matters.

The branch's precision on this corpus is therefore not measurable, and the
framework's calibration floor would withhold it rather than report it. That
is the correct outcome for a measurement that cannot be made, and it is
recorded as such rather than as a branch that failed.

## 7.13 The industrial replication of the claim band

The per-claim band was measured on the focus corpus; this is the same
measurement on the second corpus, with the **same generator** that produced
the focus corpus's answers, under the shipped prompt and the shipped
scorer, and with two evidence protocols on each corpus:

* **gold evidence** — the benchmark's own gold passage. Is the claim *right*?
* **retrieved evidence** — the passages the retriever actually returned.
  Does a reader agree with the scorer?

| Protocol | Labelled claims | κ against an independent reference | Band error rate, grounded / inferred / uncertain |
|---|---|---|---|
| Gold evidence | 293 | 0.055 (CI -0.027–0.138) | 0.077 / 0.119 / 0.139 |
| Retrieved evidence | 297 | 0.017 (CI -0.066–0.101) | 0.006 / 0.017 / 0.026 |

**The agreement-versus-correctness split.** Against the gold evidence the
band is at chance — κ 0.055 — and the three bands are
indistinguishable in their error rate. Against the evidence the band itself
saw, the bands are ordered: 0.006 for
`grounded`, 0.017 for `inferred`, 0.026 for `uncertain`. The band measures
whether the retrieved passages entail the claim — **agreement with itself**
— not whether the claim is true. The focus corpus says the same thing, at
κ 0.049 on its gold evidence and 0.069 on its
retrieved evidence, so the reading replicates on a second corpus and a
second generator.

As a filter the band works. Keeping only the `grounded` claims raises the
share of answers containing no wrong claim from 91.1%
to 94.9% on the gold protocol, and from 98.3% to 99.6%
on the retrieved one.

The positional comparison — keeping the first half of an answer rather than
what the band tagged `grounded` — is the *evidence* for that reading, not
the finding itself, and it does not hold on this corpus: p = 1.000 on the gold protocol and p = 1.000 on the retrieved one.

> **A methodological point that belongs here, because it went the wrong way.**
> The first industrial replication used a **different** generator, on a
> subset, and was underpowered: the claims that generator produced were
> nearly all supported, so the comparison had almost no power to
> discriminate. It was re-run with the same generator that produced the
> focus corpus's answers, and the re-run produced **weaker** numbers — and
> the weaker numbers are the ones reported. A replication that produced a
> more flattering result because it changed the instrument is not a
> replication.

---

# 8. Reproduction

## 8.1 Everything, from scratch

```bash
cd impl
bash scripts/rerun_focus.sh      # the focus domain: every headline number
bash scripts/rerun_all.sh        # the six-category corpus
```

Both scripts set `MTP_VARIANT` themselves, export it, and use `set -o
pipefail` so a failed experiment cannot report success through the
`tee | grep` pipeline.

## 8.2 The generator-side comparison

```bash
# the key lives outside the repository, mode 600, and is read from a file
# so it never appears in a shell history or a process listing
install -m 600 /dev/stdin ~/.mtp_llm_key <<< 'sk-...'

cd impl
bash scripts/run_generation_eval.sh                      # the cautious condition
bash scripts/run_generation_eval.sh --condition answering # the answering condition
```

The run costs money and takes hours: the long-context arm sends the whole 202,529-token corpus on every query. The harness records a cost
block in dollars (env-overridable price table, recorded in the payload) and a
cache hit-rate block.

**A cost ratio is not a token ratio.** Under prompt caching most of the
long-context arm's tokens are cache *reads* at a fifth of the base rate, so
the dollar ratio is much smaller than the token ratio. The long-context arm sends 74x more input tokens per query than the pipeline, which at the provider's cached-prefix pricing, with the corpus prefix served as a cache read on 33.0% of the long-context arm's input tokens is a 58.8x input-cost ratio rather than 74x: the token ratio and the cost ratio are different numbers, and only the second one is a cost.
The harness's token accounting adds `input + cache_read + cache_creation`,
because the provider reports the cached prefix separately and counting only
`input` under-counts the cost by two orders of magnitude.

## 8.3 One query, by hand

```bash
MTP_VARIANT=focus .venv/bin/python impl/scripts/ask.py \
    "what is the economic order quantity?"
```

## 8.4 Rebuild the deliverables

```bash
.venv/bin/python deliverables/scripts/build_all.py
```

The build restores the pristine templates, substitutes the measured values,
regenerates the results sections, rebuilds the DOCX, PPTX and PDF, exports
the dataset, and runs every check.

## 8.5 The seeding story

The seed is 20261118 and the bootstrap uses 10,000 resamples. The
generator's own `temperature` is **ignored** by the provider (always 1), so
its answers are sampled rather than greedy — which is why the reproducibility
claim is narrowed rather than absolute.

## 8.6 The second corpus, end to end

```bash
cd /Users/ritikraj/Documents/MTP
PY=.venv/bin/python

# 1. the fetch. The eCFR versioner is the only network call in the second
#    corpus, and the raw XML is cached under impl/data/_ecfr_raw/ and reused
#    by every later step, so the corpus is built from the cache, not the API.
$PY impl/scripts/fetch_ecfr.py fetch --title 29 --part 1910 --date 2026-06-01
$PY impl/scripts/fetch_ecfr.py fetch --title 40 --part 60  --date 2026-06-01
$PY impl/scripts/fetch_ecfr.py fetch --title 40 --part 112 --date 2026-06-01
$PY impl/scripts/fetch_ecfr.py fetch --title 49 --part 173 --date 2026-06-01

# 2. the corpus and its benchmark
$PY impl/scripts/build_industrial_corpus.py --out impl/data/corpus_industrial
MTP_VARIANT=industrial $PY impl/scripts/build_industrial_benchmark.py

# 3. the candidate pool, and the construction labels. The builder writes
#    two files: the judge sheet, and the un-clipped pairs the sheet is a
#    sample of.
MTP_VARIANT=industrial $PY impl/experiments/build_revision_candidates.py \
    --out       impl/results_industrial/exp14_judge_input.json \
    --pairs-out impl/results_industrial/exp14_pairs.json
$PY impl/experiments/annotate_construction_labels.py \
    --pairs impl/results_industrial/exp14_pairs.json \
    --out   impl/results_industrial/exp14_pairs_annotated.json
$PY impl/experiments/summarise_revision_corpus.py

# 4. the reader panel, and the detector scored against it. The annotated
#    pairs are the ones the scoring reads: they carry the construction
#    labels alongside the passages.
$PY impl/experiments/build_annotator_panels.py \
    --pairs  impl/results_industrial/exp14_pairs.json \
    --outdir impl/results_industrial/panels
$PY impl/experiments/run_revision_eval.py \
    --pairs  impl/results_industrial/exp14_pairs_annotated.json \
    --labels impl/results_industrial/exp14_judge_a_labels.json,\
impl/results_industrial/exp14_judge_b_labels.json \
    --out    impl/results_industrial/exp14_revision_eval.json

# 5. the rubric x specialisation factorial
$PY impl/experiments/build_rubric_factorial.py \
    --judge-input impl/results_industrial/exp14_judge_input.json \
    --panels      impl/results_industrial/panels \
    --outdir      impl/results_industrial/panels/factorial
$PY impl/experiments/run_rubric_factorial.py \
    --pairs         impl/results_industrial/exp14_pairs_annotated.json \
    --factorial-dir impl/results_industrial/panels/factorial \
    --industrial    impl/results_industrial \
    --out           impl/results_industrial/exp21_rubric_factorial.json

# 6. the quantity stratum
MTP_VARIANT=industrial $PY impl/experiments/run_quantity_stratum.py \
    --out impl/results_industrial/exp20_quantity_stratum.json
```

## 8.7 The claim-band replication, the figures and the generators

```bash
# 7. the claim-band replication. The sheet carries the question and the
#    retrieved passages under the shipped prompt; the answers come from the
#    same generator that produced the focus corpus's answers.
$PY impl/scripts/prepare_generator_sheet.py sheet \
    --out impl/results_industrial/exp21_generator_sheet.json --n 247
bash impl/scripts/run_generator_api.sh \
    --sheet impl/results_industrial/exp21_generator_sheet.json \
    --out   impl/results_industrial/exp21_generator_answers.json
$PY impl/scripts/prepare_generator_sheet.py score \
    --sheet   impl/results_industrial/exp21_generator_sheet.json \
    --answers impl/results_industrial/exp21_generator_answers.json \
    --out     impl/results_industrial/exp21_claims.json

# the two blind judge sheets -- the same claims, two questions
$PY impl/scripts/prepare_generator_sheet.py judge-sheets \
    --claims impl/results_industrial/exp21_claims.json \
    --bench  impl/data/benchmark_industrial/benchmark.json \
    --outdir impl/results_industrial --prefix exp21

# the judges, and the re-run of the claims a judge ran out of budget on.
# The wrapper reads the key from ~/.mtp_llm_key, so it never appears on a
# command line; the second judge is the same model reached as a different
# annotator.
bash impl/scripts/run_claim_labeling.sh \
    --input ../results_industrial/exp21_judge_input_gold.json \
    --out   ../results_industrial/exp21_judge_a_model_labels_gold.json
MTP_JUDGE_NAME=judge_b_model bash impl/scripts/run_claim_labeling.sh \
    --input ../results_industrial/exp21_judge_input_gold.json \
    --out   ../results_industrial/exp21_judge_b_model_labels_gold.json
$PY impl/scripts/relabel_failed.py \
    --input  impl/results_industrial/exp21_judge_input_gold.json \
    --labels impl/results_industrial/exp21_judge_a_model_labels_gold.json \
    --out    impl/results_industrial/exp21_judge_a_model_labels_gold.json

# the band, on the gold evidence and on the retrieved evidence
$PY impl/experiments/run_claim_band_eval.py eval \
    --generation impl/results_industrial/exp21_generator_answers.json \
    --bench      impl/data/benchmark_industrial/benchmark.json \
    --labels     impl/results_industrial/exp21_judge_a_model_labels_gold.json,\
impl/results_industrial/exp21_judge_b_model_labels_gold.json \
    --claims     impl/results_industrial/exp21_claims.json \
    --out        impl/results_industrial/exp21_claim_band_eval_gold.json

# 8. the figures, from the result JSONs
$PY impl/scripts/make_figures.py

# 9. re-derive every quoted number from the result files and check that the
#    shipped documents carry it
$PY impl/scripts/verify_reported_numbers.py
```

Two document generators write the second corpus into the deliverables, and
neither types a number by hand:

```bash
# the second-corpus section of both LaTeX papers, generated from the result
# files between the two markers in each paper
$PY deliverables/scripts/make_tex_industrial.py

# the saved office files, made monochrome -- a document whose meaning
# depends on a colour fails on a mono printer
$PY deliverables/scripts/monochrome.py \
    deliverables/Deliverable_3_Department_Report.docx \
    deliverables/Deliverable_4_Presentation_18Nov.pptx
```

`make_tex_industrial.py` writes prose rather than templates, because the
interpretive sentences in that section — whether fusion beat its lexical
leg, whether the band replicated, whether the rubric or the reader moved the
number — are exactly the kind that go stale: each is a fact about the run,
and a hand-written sentence asserts one answer regardless.

---

# 9. The test suite

```bash
.venv/bin/python -m pytest impl/tests -q      # 32 tests
```

`4` test files: `test_hybrid.py`, `test_confidence_and_claims.py`,
`test_query_form.py`, `test_invariants.py`.

The invariant tests assert the **mechanism's predictions**, on a synthetic
index with the models stubbed out, so they run in milliseconds and cannot be
fooled by a model's behaviour. The predictions asserted include:

| Prediction | Test |
|---|---|
| The category filter restricts **both** legs | `test_category_filter_applies_to_both_legs` |
| The reranker only permutes its pool | `test_the_reranker_only_permutes_its_pool` |
| The quota stays inside its pool | `test_the_quota_stays_inside_its_pool` |
| Platt scaling is monotone | `test_platt_scaling_is_monotone` |
| The generator is reached only through the gate | `test_the_generator_is_reached_only_through_the_gate` |
| A malformed query never reaches the generator | `test_a_malformed_query_never_reaches_the_generator` |
| The real index has unique chunk ids and single-category documents | `test_real_corpus_has_no_duplicates` |

**Three real defects were found this way, and none of them was visible in the
output:** the single-leg category filter, the quota that evicted modalities
already at their floor, and the article indexed under two category names.

> **A fourth defect was found by the test suite failing for an unrelated
> reason.** `test_a_malformed_query_never_reaches_the_generator` asserted
> that turning the form check off lets the query through. It stopped passing
> when a real calibrated gate model appeared in the default artefacts
> directory: the test inherited the ambient gate model, the stub query was
> gate-refused, and the generator was never reached for a reason that had
> nothing to do with the form check. The test now pins the gate model the
> same way its sibling does. **The framework was correct; the test was
> coupled to the environment.** A test that passes or fails depending on
> what happens to be on disk is not a test.

---

# 10. Known limitations and open threads

1. **Scale.** The primary corpus is 634 chunks over 24 documents; the public
   encyclopaedic corpus measured on is 2,383 chunks over    46 documents, and the regulatory corpus is    110 documents and 2,443 chunks. Claims are
   framed as demonstration and mechanism, not generalisation.
2. **One jurisdiction, one language, one regulatory family.** The
   encyclopaedic corpus is reference material about industrial engineering; the
   regulatory corpus is authentic, binding and versioned. But it is United
   States federal regulation, in one language, from one regulator family, and
   it is still not a plant's own procedures. See §6.1 and §6.5.
3. **The transfer experiment's scope.** Coverage across categories only; see
   §7.4.
4. **The conflict labels are model-generated.** On the regulatory corpus the
   detector's precision is 0.659 against the readers' labels
   and 1.000 against the construction labels,
   and its typing precision is 0.073 and    0.000: the mechanism finds the conflicts and
   reports them as the wrong kind. But the readers were models, so the labels
   are not independently confirmed, and the rubric factorial showed that the
   wording of the labelling instructions moved the measured precision by
   +0.366 at the generalist and
   +0.317 at the specialist. A human round, against a
   rubric fixed in advance, is still the next step. See §7.10 and §7.11.
5. **The generator-side comparison used one model.** Both prompt conditions
   were run on MiniMax-M3, and the hypothesis holds under each, but a
   claim about a gate wants a second model to hold on.
6. **The six-category long-context proxy did not complete** — the run was
   interrupted — so no six-category proxy figure is quoted. The cost half for
   that corpus is complete and is reported.
7. **The benchmark's unanswerable class is now corpus-anchored but not
   adversarial.** It is decidable from the evidence by construction, which
   makes it a fair test of the gate and a weak test of a benchmark. The repair
   holds on both corpora — the shortcut audit was repeated on the regulatory
   corpus, where the one-rule identifier shortcut catches    0 of 197 — but a hand-check
   against the corpus is still open.
8. **Calibration is deployment-specific.** See §7.4.

## 10.1 Open threads, in priority order

The same list the status report and the defence deck carry.

1. **Repeat the generator-side comparison on a generator that returns text on the table questions.** One generator behind five arms settles the hypothesis once; one generator settles it for one model. The replication was attempted on MiniMax-M3.1-Flash and could not be run: it returned no text on 24 of the 66 questions it was asked, of which 23 of the 44 were the benchmark's table lookups -- it spends its whole output budget thinking and comes back empty. Raising the budget fourfold rescued 13 of those, and 11 were still empty at that budget, so this is not a shortage of output room. The obstacle is now specific rather than vague: it wants a generator that can parse a table, or one whose reasoning budget is bounded. Both prompt conditions have been run on MiniMax-M3, and the result is that the gate's contribution does not depend on the generator's willingness to decline -- which is a claim about the *gate*, so it wants a second generator to hold.
2. **Compare the gate against a token-level faithfulness monitor.** The gate is currently measured against a prompt-level control and against the always-flag and never-flag baselines, but not against another *detector* of the same kind of thing. A SYNCHECK-style token-level monitor would put the two on one axis: both score the retrieved evidence, and the question becomes which is the better filter at a stated operating point, on one risk-coverage curve with both on it. The thesis's claim is about the gate as a branch rather than an instruction, and that claim does not need the comparison -- but the comparison is what a practitioner deciding whether to adopt the gate would ask for, and it is one implementation away.
3. **Settle the positional comparison's magnitude and power.** The direction is not uniform: keeping the first claims of an answer carries a higher risk than keeping the band's `grounded` claims in three of the four corpus-and-protocol combinations. What varies is the magnitude -- +0.0923 against +0.0231 on the focus corpus and +0.0152 against +0.0000 on the industrial one, all at matched coverage -- and only the largest of them clears significance (focus gold, p = 0.008). Why the gap is four times larger on the focus corpus's gold protocol than on its retrieved protocol is not established, and a larger sample of annotated claims would settle it. The band is reported as a filter and not as a ranking in the meantime, which the direction that replicates already supports.
4. **Run the answer-quality half of the long-context comparison on the six-category corpus.** The retrieval-side proxy is complete there (680,417 tokens over the corpus), the corpus fits the 1M-token window used here, and the cost half is already measured on both corpora. What is missing is the quality half on the larger corpus, and it is one run away.
5. **Add a second, stronger reranker to the candidate-pool sweep.** The pool result -- recall rising to a peak at a pool of ten and then declining -- is measured with one cross-encoder, so the reranker and the pool size are confounded: a stronger reranker might not decline at all. The sweep is cheap to repeat and the reranker is local, so a 2x2 over the shipped cross-encoder and a stronger one, at pool sizes 10, 50 and 100, plus a no-rerank arm, would separate them. Until it is run, the claim is about *this* reranker.
6. **Test specialisation with genuinely different reader models.** The 2x2 factorial over the annotation rubric and the reader's specialisation holds the reader model constant, so 'specialist' there is a brief given to one model, and the result -- that the rubric's wording and not the specialisation moved the measured precision -- is a statement about briefs. The panel's four regime specialists are differently briefed too. Running the same two roles on a second, genuinely different checkpoint would tell the panel whether specialisation is a capability at all, or only a way of writing a rubric.
7. **Confirm the conflict labels with human annotators, against a rubric whose wording is now known to move the measurement.** The pairs were read by a panel of domain specialists and a generalist control, blind to the detector, and the panel's agreement is reported in full. But the labels are model-generated, so agreement between readers is not confirmation that a label is right; and a 2x2 factorial over the annotation rubric and the reader's specialisation has shown that the wording of the rubric moved the measured precision by a factor of nine (+0.366 at the generalist and +0.317 at the specialist, against +0.049 and +0.000 for the specialisation). So the human round has to fix the rubric before it is run rather than after, and the pairs and the rubric ship with the thesis for that round.
8. **Extend the corpus from federal regulation to a plant's own revised procedures.** The second corpus supplies the conflicts the first one could not: 110 United States federal regulatory documents read at two past dates, giving 948 amended-paragraph pairs of which 361 state different numbers, with the conflict type known by construction and so no annotation needed to know the right answer. What it does not supply is a plant's own documents, where the same procedure at two revisions would be the same kind of conflict but with no public versioner to align them.
9. **Re-fit the conflict calibration on a plant's documents.** The calibration is fitted per corpus, exactly as the answer gate's threshold is. The regulatory profile is fitted and shipped, and it says that on this corpus a conflict is surfaced when the branch that raised it clears 0.5. A plant's documents would need their own fit, and the factorial's result -- that the rubric's wording moved the measured precision by a factor of nine -- means the fit has to be checked against the rubric that will actually be used.
10. **Extend the industrial corpus beyond one jurisdiction and one language.** The corpus is United States federal regulation, in one language, from one regulator family. Nothing in this thesis shows that the decomposition of a conflict detector's precision into detection and typing holds for another jurisdiction's regulatory language, for a plant's own procedures, or for vendor specifications.
11. **Stratify the corpus by modality** so the modality-quota objective can be tested with adequate power, with a pre-registered power analysis rather than a post-hoc one.
12. **Hand-check the repaired unanswerable class against the corpus, on both corpora.** The repair is no longer a single-corpus result: the shortcut audit has been repeated on the industrial corpus, where the one-rule identifier shortcut catches 0 of 197 and the question-only classifier separates the two classes at 0.708 against a permutation null of 0.505. What is still open is the part no audit can do: a person reading the repaired class against the corpus.

---

# Appendix A — a quick reference to the mechanisms

| Mechanism | Module | One line |
|---|---|---|
| Query-form validator | `query_form.py` | four lexical rules; refuses a non-question before retrieval costs anything |
| Category pre-filter | `pipeline.py` | restricts **both** legs before retrieval, so the statistics are computed on the right sub-corpus |
| BM25 | `lexical.py` | Robertson IDF, `k1=1.2`, `b=0.75` |
| Dense retrieval | `models.py` | `BAAI/bge-m3`, 1024-d, no query instruction |
| RRF | `hybrid.py` | `k=60`, no score normalisation needed |
| Modality quota | `hybrid.py` | swap-based floor; **before** the reranker |
| Cross-encoder | `models.py` | MS-MARCO MiniLM-L6-v2 over the top 50, delivering 10 |
| Confidence gate | `confidence.py` | five features → calibrated posterior vs τ; the model is not called on a refusal |
| Claim tagging | `claims.py` | per-claim entailment against the evidence actually shown |
| Contradiction | `contradiction.py` | NLI **and** same-subject, plus a numeric-conflict branch |

# Appendix B — where each number comes from

| Result file | Holds |
|---|---|
| `impl/results_focus/exp1_ablation.json` | the seven-rung ablation and the paired Wilcoxon tests |
| `impl/results_focus/exp2_gate.json` | calibration, the threshold sweep, refusal by question family |
| `impl/results_focus/exp3_contradiction.json` | the contradiction experiment |
| `impl/results_focus/exp5_pool_size.json` | the candidate-pool sweep |
| `impl/results_focus/exp7_long_context.json` | the long-context cost half and the retrieval-side proxy |
| `impl/results_focus/exp8_generation.json` | the generator-side comparison (cautious condition) |
| `impl/results_focus/exp8_generation_answering.json` | the generator-side comparison (answering condition) |
| `impl/results_focus/exp8_scorer_validation.json` | the audit of the claim scorer |
| `impl/results_focus/exp9_label_audit.json` | the audit of the answer labels |
| `impl/results_focus/exp12_unanswerable_class_audit.json` | the audit of the unanswerable class |
| `impl/results/exp1_ablation.json` | the six-category ablation |
| `impl/results/exp4_transfer.json` | the cross-category transfer experiment |
| `research/baseline_minilm/` | the archived pre-encoder-swap measurements, so the before/after stays checkable |
| `research/00_citation_audit.md` | every citation, resolved against arXiv |

# Appendix C — the guard rails

The build is not a convenience; it is part of the method. `check_consistency.py`
fails the build on:

* a token left unsubstituted — the prose would ship it literally;
* a template that hard-codes a measurement which has been superseded — the
  tripwire compares the templates against the archived pre-swap run, so a
  hand-written number that no longer describes any run is caught;
* an arXiv identifier that is not in the citation audit;
* a corpus size or document count that disagrees between documents;
* a duplicated chunk id, or a document spanning two categories;
* a malformed benchmark question;
* a generator-side run that disagrees with the benchmark it is filed next to;
* a missing deliverable.

And `check_latex.py` fails on a LaTeX error, an undefined citation or
reference, or an overfull line over 30pt — because a brace-balance check
proves a `.tex` file is *well formed*, not that it *compiles*.
