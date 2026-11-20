
# Part D — The code, walked through

Every file, what it does, and why it is the way it is. Paths are relative to the
project root.

```
impl/
├── src/
│   ├── config.py         Every hyperparameter, with provenance
│   ├── ingestion.py      PDF/markdown → modality-tagged chunks
│   ├── lexical.py        BM25, implemented from scratch
│   ├── models.py         Embeddings, cross-encoder, NLI
│   ├── hybrid.py         RRF + the modality quota
│   ├── confidence.py     The posterior, the calibration, the query-level gate
│   ├── query_form.py     The runtime form check: is this a question at all?
│   ├── contradiction.py  NLI + topical + revision checks
│   ├── claims.py         Per-claim tagging, noisy-OR, information gain
│   ├── evaluate.py       Retrieval and generation metrics
│   ├── stats.py          κ, McNemar, Wilcoxon, bootstrap, Cliff's δ
│   ├── pipeline.py       The orchestration
│   └── fetch_models.py   Pre-downloads the three models
├── scripts/
│   ├── build_corpus.py   Fetches and cleans the public corpus
│   ├── build_benchmark.py Generates the silver-standard benchmark
│   ├── unanswerable_repair.py  Builds the corpus-anchored unanswerable class
│   ├── build_index.py   Builds and caches the retrieval index
│   ├── make_focus_corpus.py  Materialises the focus-domain subset
│   └── export_dataset.py Exports the corpus with its provenance
├── experiments/
│   ├── common.py         Shared loading + the cross-encoder score cache
│   ├── run_ablation.py   Experiment 1 — retrieval ablation
│   ├── run_gate.py       Experiment 2 — calibration and operating point
│   ├── run_contradiction.py  Experiment 3 — NLI vs the joint gate
│   ├── run_transfer.py   Experiment 4 — cross-category transfer
│   ├── run_pool_size.py  Experiment 5 — the rerank candidate pool
│   ├── run_long_context.py Experiment 7 — the long-context baseline arm
│   ├── run_form_probe.py Experiment 9 — what the gate does with malformed queries
│   ├── run_form_validator.py Experiment 10 — the runtime form check
│   ├── audit_answer_side.py Experiment 9 — the answer-label audit
│   ├── audit_unanswerable_class.py Experiment 12 — the unanswerable-class audit
│   └── run_focus_case.py Experiment 8 — the focus-domain case study
├── data/
│   ├── corpus/           46 public industrial documents, six categories
│   ├── corpus_focus/     The focus domain alone: 14 documents
│   ├── benchmark/        276 silver queries (132 answerable, 144 unanswerable)
│   └── benchmark_focus/  176 queries on the focus domain
├── artifacts/            Cached index, embeddings, gate model, score cache
└── results/              Measured outputs (JSON + markdown tables)
```

**The tests.** `impl/tests/` pins down the places where an inverted condition or
a misdirected filter silently produces plausible-looking but wrong numbers: the
rank-fusion properties, the quota's victim selection, and a third file of
**invariant tests** that assert what the mechanism predicts — that the category
pre-filter restricts *both* retrieval legs, that the reranker only permutes its
own pool, that the quota never introduces a chunk from outside its pool, that
no document spans two categories, that the calibration is monotone, that the
generator is reachable only through the gate, and that a malformed query never
reaches it either. Each of those corresponds to a
defect that was actually found and fixed during this work, so the tests are
regression tests rather than decoration. The quota test is a direct
regression test — *the quota must never evict a modality that is already at its
floor* — and it exists because the original implementation had that condition
inverted, which made the quota evict the very modality it was protecting. The
gate tests cover the refusal message, the accept set, the noisy-OR, the entropy
symmetry that the thesis flags as a trap, and Platt recovery of a known
coefficient vector.

**Three artefacts, and why each exists.**

`artifacts/index.npy` + `index.json` — the embedded corpus. Cached by content
hash so a re-run does not re-encode 2,383 chunks.

`artifacts/gate_model.json` — **the fitted gate.** It holds the feature mean
and standard deviation from the calibration split and the logistic weights. The
framework loads it at construction; if it is absent, the framework prints a
loud warning and falls back to the un-calibrated chunk-level posterior, because
a silently un-calibrated gate is worse than no gate at all. This file is the
difference between "the gate is calibrated" and "the gate is a threshold".

`artifacts/rerank_scores.json` — the cross-encoder scores for every
(query, candidate-pool) pair. The cross-encoder pass is by far the most
expensive step and five of the six experiments need it; caching it turns
three passes into one and makes the suite re-runnable in minutes.

## D.1 `config.py` — one place for every hyperparameter

Every number the system uses lives here with a note on where it came from. There
are no magic numbers in the pipeline. A reviewer asking "where did 0.15 come from?"
gets an answer with a citation; a reviewer asking "why is this in the code rather
than the config?" gets a faster answer.

The `GateConfig` defaults (β₀ = 2.943, β₁ = 1.680) are the coefficients fitted in
the September 2026 project report on a 30-query calibration set. **They are
placeholders that `run_gate.py` overwrites with values fitted on the current
corpus.** This is deliberate and is discussed in §C.6: the calibration is a fitted
parameter of the deployment, not a constant of the architecture.

## D.2 `lexical.py` — BM25 from scratch

Why not `rank_bm25` or `sklearn`? Because the thesis has to defend the exact
scoring function, its parameters, and its edge cases, and a black box cannot be
defended. The full derivation is in §C.2; the file's docstring carries the same
derivation so that a reader opening the file gets it in context.

Two details worth knowing:

- **Stopwords are removed but stemming is not.** Aggressive stemming breaks
  industrial tokens — "EOQ", "MOQ", "SKU", "FMEA" have no useful stems, and
  stemmers routinely mangle them. Removing a small stop list is safe; Porter
  stemming on industrial vocabulary is not.
- **`explain()` returns the per-term breakdown.** This is what you show a
  practitioner who asks "why did this document come back?" — term, IDF, term
  frequency, document length, and the term's contribution to the final score. It
  is the qualitative evidence for the paper's BM25 analysis.

## D.3 `ingestion.py` — the stage everything else depends on

**Modality classification.** PyMuPDF exposes a page as blocks with bounding boxes,
plus a table detector. Every block is classified:

| Condition | Modality |
|---|---|
| Overlaps a detected table region | `table` |
| Less than 55% alphabetic characters | `chart` (figure label or chart annotation) |
| Otherwise | `text` |

**Table serialisation.** `table_to_markdown()` renders a detected table as
markdown, forward-filling horizontally merged cells so the result stays
rectangular — irregular markdown confuses both the LLM and the tokenizer.

**Text chunking.** 120-word windows with 30-word overlap. The overlap prevents a
sentence straddling a boundary from being lost. A trailing fragment shorter than
12 words is merged into the previous chunk rather than emitted as its own unit.

**Why the table chunk is never split.** A table is the atomic unit of a
specification. Splitting it produces fragments that mean nothing.

**Markdown figures.** In the markdown corpus, an image's alt text *is* its caption
— the same text a human reads to understand the chart. Treating it as a `chart`
chunk is what an OCR-free pipeline does, and it is what gives the modality quota
something to balance against.

**`corpus_statistics()`.** Reports the modality composition. This is not a
diagnostic afterthought: it *predicts* whether the modality-quota mechanism can
have any effect. On a corpus that is 91% prose, the expected result of D2 is a
null. It also reports the number of distinct categories and the number of
duplicated chunk ids, which is how the corpus defect described in §D.10 was
caught.

**`_strip_wiki_chrome()`.** Removes the navigation chrome that Wikipedia's
HTML carries into the converted markdown: the "edit" and "edit source" links
that head every section, the citation superscripts, the emphasis markers, the
links' URLs, and the images with no alt text. Left in, that chrome occupied
about **30% of the corpus text** and appeared verbatim in the retrieved
evidence — the case study in Part E would have shown a reader a passage
beginning `[[edit](/w/index.php?title=Little%27s_law&veaction=edit…)`. After
the strip it occupies under 3%. This is the unglamorous work that decides
whether the corpus is a corpus of industrial text or a corpus of Wikipedia
interface, and it is not visible in any result table: the numbers move by a
fraction of a point, but the evidence a reader is shown becomes legible.

## D.4 `models.py` — the three neural components

**`embed_texts`** encodes and caches to disk by content hash, so repeated
experiment runs do not re-encode the corpus.

**`cosine_similarity_matrix`** normalises explicitly and accepts either a 1-D or
2-D query array. (This function had a real bug during development: a 1-D query
promoted with `query_vec[None, :]` produced a 3-D array and a silently wrong
similarity matrix. The lesson worth keeping: *always assert the shape of a
similarity matrix in a test.*)

**`rerank`** returns raw cross-encoder logits. It deliberately does **not**
convert them to probabilities — that conversion is the confidence gate's job, and
doing it here would hide exactly the thing the thesis is about.

**`nli_probs`** returns the three-way distribution. The label order for the
DeBERTa-v3 MNLI checkpoints is `[contradiction, entailment, neutral]`, and that
convention is written in one place rather than scattered across call sites.

## D.5 `hybrid.py` — RRF and the quota

`reciprocal_rank_fusion` is nine lines. `apply_modality_quota` is the swap-based
algorithm described in §C.8, and it carries a comment explaining why the
rebuild-based alternative was wrong and what it cost.

## D.6 `confidence.py` — the heart of D1

Contains: `sigmoid` (numerically stable), `posterior_from_score`, `fit_platt`
(Newton's method on the log-loss, with the gradient and Hessian written out),
`fit_isotonic` (PAVA), `apply_isotonic`, `brier_score`,
`expected_calibration_error`, `reliability_table`, `selective_risk_curve`, and
`apply_gate`.

`apply_gate` returns a `GateDecision` with the accepted chunks and, on rejection,
the user-facing refusal text including the actual posterior and threshold. That
text is what makes the refusal auditable.

### `query_form.py` — the check that runs *before* the gate

The gate decides whether the *evidence* supports an answer. It never asks
whether the query was a question at all, and Experiment 9 measures what that
costs: at the fitted operating point, on the six-category corpus, the gate accepted 23
of the 30 malformed stems the benchmark's generator produced
(76.7%). Those are different questions, so they are different
components, and the form check runs first — before retrieval, so a request it
refuses costs no embedding pass, no cross-encoder pass and no model call.

`assess_query_form` applies four rules and returns a `FormAssessment` naming
the one that fired: `empty` (nothing but whitespace), `no_words` (no
alphabetic character at all), `no_content` (every word is a function word or a
deictic — "what is this?"), and `incomplete` (the query ends on a word that
cannot end a question — "what are units that?"). The last two rules need two
word lists, and both are conservative on purpose.

Two decisions in that file are worth stating, because both were made against a
measurement rather than by taste:

- **The benchmark's own filter is not reused.** `build_benchmark.py` has
  `_subject_is_usable`, which already rejects malformed question subjects, and
  reusing it is the obvious shortcut. It is a rule about *question generation*:
  it rejects "FMEA" for being one word, "root-cause analysis" for the hyphen
  and "pick and pack warehousing" for ending in "-ing". On the same
  hand-labelled stems it would have refused 13
  of 13 well-formed questions
  (100.0%). Experiment 10 measures that counterfactual
  rather than asserting it.
- **The check fails open.** It has no dictionary and no language model, so a
  keyboard mash is invisible to it; the test fixture records two such cases as
  expected misses. A rule that guessed would risk refusing valid questions,
  which is the failure the whole design is about avoiding.

## D.7 `contradiction.py` — D4

`detect_contradictions` compares every pair of accepted chunks, running the NLI
model once for all pairs (batched), and applying the topical and numeric checks.
`entity_jaccard` and `numeric_conflicts` are pure Python with no model calls.

`contradiction_summary` reports the NLI-only count alongside the joint-gate count,
so the false positives the topical gate suppresses are visible.

## D.8 `claims.py` — D5

`split_into_claims`, `noisy_or`, `binary_entropy`, `information_gain`, `band_for`,
`assess_claims`, `render_answer`. The docstrings carry the derivations from §C.9.

## D.9 `evaluate.py` and `stats.py` — the measurement layer

`evaluate.py` computes recall@k, precision@k, MRR, nDCG@k, and per-modality recall,
and aggregates generation metrics into faithfulness, hallucination rate, citation
precision and citation recall.

**A subtlety worth stating**: queries with an empty relevance set (the
unanswerable ones) are **excluded** from recall and nDCG aggregates rather than
averaged in as zero. A zero would make the system look as if it failed to retrieve
the answer when there is no answer to retrieve. Their behaviour is measured by the
gate's rejection rate instead, which is where it belongs.

`stats.py` contains Cohen's κ with its standard error, McNemar's exact test,
Wilcoxon signed-rank with Cohen's d_z, the paired t-test (kept for cases where
normality is defensible), the percentile bootstrap, Cliff's δ with a significance
approximation, and the Wilcoxon rank-biserial correlation.

## D.10 `pipeline.py` — the orchestration

`Index` holds the chunks, the BM25 index, the embedding matrix and the metadata
maps, and serialises to disk. `Framework.retrieve()` implements Stage 2 and
`Framework.answer()` implements Stage 3.

**Eight implementation bugs found and fixed during development are worth
recording**, because each is a trap that a reviewer might reasonably suspect is
still present — and because in four cases the bug first presented as a
*substantive negative result*:

1. **The category filter was applied to only one leg.** The filter restricted the
   dense candidate pool but not the BM25 leg. Because BM25 dominates the fusion
   (recall 0.969 vs dense 0.812), the filter's effect was almost entirely
   washed out — the measured difference between "with filter" and "without filter"
   was exactly zero. The lesson: a filter that touches one of two retrievers is
   not a filter, and this is the same failure mode as a pgvector metadata filter
   applied to only one index.

2. **The category was stored in the wrong place.** `category_of` was read from
   `chunk.meta`, but the category lived in a dedicated field. Every chunk silently
   defaulted to `"general"`, and the filter again did nothing. The symptom was
   identical to a working-but-useless filter, which is why it took a direct
   inspection of the loaded index to find.

3. **The quota was drawn from the whole corpus.** Pulling a table from fused rank
   800 into a 10-chunk context is not a quota, it is noise. The quota now draws
   from the bounded top-N candidate pool.

4. **The quota's victim-selection condition was inverted.** It evicted the
   modalities that were *at* their floor and spared the ones with a surplus. The
   symptom was that the quota made table recall *worse* — 0.906 collapsing to
   0.469 — which read as a substantive negative result about modality balancing
   rather than a one-character logic error. **This is the most instructive of the
   five**, and §C.8 gives it the treatment it deserves.

5. **The gate was calibrated at the wrong level.** It asked "is this candidate the
   gold chunk?" rather than "does this context contain enough evidence to answer?".
   With one gold chunk among fifty candidates the base rate is about 2%, so
   maximum-likelihood fitting returned β₀ = −2.88 and β₁ = 0.27, the Brier score
   was 0.011 and the ECE 0.004 — *excellent-looking numbers that measured the
   base rate* — and the implied operating point refused 46% of the answerable
   questions. Recalibrating at the query level gave Brier 0.1510 and
   ECE 0.1044, which are **worse-looking and honest**, and an operating
   point that actually works.

6. **The corpus held two articles twice.** Two articles had been listed under
   two category names each, so they were fetched twice and indexed twice: the
   index reported one chunk row for every copy, but held fewer distinct chunk
   ids than rows. The
   effect was not cosmetic. A document split across two categories is
   half-visible to the category pre-filter, and — because the two copies shared
   a chunk id — the *same* document landed in both halves of the
   cross-category transfer split, so the "held-out" half was not held out.
   The corpus builder now refuses to list one article under two categories, and
   the index reports its duplicate count.

7. **A recall metric that could not fail.** The reranked list was truncated to
   the final-context size before evaluation, so `Recall@20` was computed over a
   ten-item list and was therefore *identical* to `Recall@10` in every table —
   a column that looked like evidence and was an artefact of a slice. The
   pipeline now keeps the full reranked ranking so Recall@20 is a measurement.

8. **A recall figure that was true by construction.** The contradiction
   experiment reported the joint gate's recall on the "verifiable conflicts" as
   1.000. That subset is *defined* by the presence of a numeric conflict, and
   the numeric detector is an OR-branch of the gate, so the gate caught every
   member of the subset by definition. The experiment now reports the
   NLI-and-same-subject conjunction alone — which is the part that distinguishes
   the mechanism — and the deliverables say plainly that the 1.000 is not
   evidence.

**None of these eight is exotic.** They are the ordinary failure modes of a
filter-plus-fusion pipeline, and they are exactly the kind of thing that makes a
reported improvement vanish — or, worse, that makes a reported *regression*
appear to be a finding about the world rather than a bug in the code. The
lesson to state in the report is not "our system works" but "**our system works,
and here is how we established that each of its components is actually doing
something — including by checking whether the negative results were real**."

The generalisable form of the lesson: **a result that contradicts the mechanism
you believe is a bug report until proven otherwise.** Four of the eight bugs above
first appeared as findings, and all four would have been reported as
discoveries."

## D.11 Running it yourself

```bash
cd /Users/ritikraj/Documents/MTP

# 1. Models (once)
.venv/bin/python impl/src/fetch_models.py

# 2. Corpus (public documents; ~3 min)
.venv/bin/python impl/scripts/build_corpus.py

# 3. Benchmark
.venv/bin/python impl/scripts/build_benchmark.py

# 4. Index (embeds the corpus; ~1 min)
.venv/bin/python -c "
import sys; sys.path.insert(0,'impl')
from src.pipeline import build_index
from src.config import CORPUS_DIR
from pathlib import Path
build_index(CORPUS_DIR).save(Path('impl/artifacts/index'))"

# 5. Experiments
.venv/bin/python impl/experiments/run_ablation.py
.venv/bin/python impl/experiments/run_gate.py
.venv/bin/python impl/experiments/run_contradiction.py
.venv/bin/python impl/experiments/run_transfer.py

# The audits: the benchmark's own answer labels, and its unanswerable half
.venv/bin/python impl/experiments/audit_answer_side.py
.venv/bin/python impl/experiments/audit_unanswerable_class.py
```

Results land in `impl/results/` as JSON (full detail) and markdown (the tables
that appear in the report).

**Runtime.** The whole suite runs on CPU in roughly 25–35 minutes. The dominant
cost is cross-encoder reranking: 276 queries × 50 candidate pairs × 4 systems.

---
