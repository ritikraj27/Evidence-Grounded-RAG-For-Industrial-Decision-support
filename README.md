# MTP-2 — An Evidence-Grounded RAG Framework for Industrial Decision Support

**Ritik Raj [25IM60R12]** · Supervisor: Dr. Sri Krishna Kumar
Department of Industrial and Systems Engineering, IIT Kharagpur

---

## Quick start

```bash
git clone git@github.com:ritikraj27/mtp-evidence-grounded-rag.git
cd mtp-evidence-grounded-rag

# Python environment (Python 3.12 was used)
python3.12 -m venv .venv
.venv/bin/pip install -r requirements.txt

# Optional: the three third-party skill suites used for writing and literature work
bash scripts/setup_external.sh
```

Then follow [Running it](#running-it) below. The commands there use `.venv/bin/python`
and are run from the repository root.

### API keys and secrets

No key is stored in this repository. The code reads credentials from the environment
only:

- `MTP_LLM_API_KEY` (or `ANTHROPIC_API_KEY`) for the generation experiment and
  `impl/scripts/ask.py`. The shell wrappers also read `~/.mtp_llm_key`, which lives in
  your home folder, outside the repository.
- `SEMANTIC_SCHOLAR_API_KEY`, `OPENALEX_API_KEY`, `EXA_API_KEY`, `DEEPXIV_TOKEN` for the
  optional literature tools in `tools/`.

Copy `.env.example` to `.env` and fill it in if you want a local file. `.env` is
git-ignored, as are `*.key`, `*.pem` and `.mcp.json`.

### What is deliberately not in the repository

| Left out | Why | How to get it back |
|---|---|---|
| `impl/artifacts*/` (embedding indexes, model caches, about 110 MB) | Fully reproducible | `impl/scripts/build_index.py` after step 2 of Running it |
| `.venv/`, `.snapshot_preswap/`, logs, caches | Local only | `pip install -r requirements.txt` |
| `academic-research-skills/`, `andrej-karpathy-skills/`, `claude-code-paper-writing/` and the symlinks into them | Third-party repositories with their own licences | `bash scripts/setup_external.sh` |
| `.mcp.json` | Holds an absolute path to a local virtualenv | Re-register Scrapling with `scrapling mcp` |

---

## What is in this repository

This repository contains two things: a **working, runnable implementation** of the
framework with a measured evaluation, and the **four deliverables** built from it.

The implementation exists so that nothing in the deliverables is asserted. Every
formula is derived from first principles in the code as well as in the prose, every
hyperparameter has a documented provenance, and every number in the report is
produced by a script that can be re-run.

---

## The four deliverables

| # | Deliverable | File(s) | What it is |
|---|---|---|---|
| **1** | **The Complete Guide** | `deliverables/Deliverable_1_Complete_Guide.md` (+ `.docx`) | The teaching-grade document. Ten parts: the five-minute version; every term defined; every formula derived from first principles with the reasoning and a worked example; the code walked through file by file; the experiments and what the numbers mean; the literature and exactly where this work stands in it; anticipated viva questions with defensible answers; the limitations; how the report and the paper differ; a one-page glossary. |
| **2** | **The polished paper, in three formats** | `Deliverable_2a_Technical_Report.md` / `.docx`<br>`Deliverable_2b_IEEE_Conference_Paper.tex`<br>`Deliverable_2c_Journal_Style_Paper.tex` | The same paper in three submission formats: single-column technical report, IEEE two-column conference paper, and an Elsevier/Scopus-style journal paper with a structured abstract and highlights. The `.tex` files compile with `pdflatex` and need only the standard `IEEEtran` / `elsarticle` classes, and they include the six figures in `deliverables/figures/` by relative path — so that directory has to travel with them. Both papers carry the second corpus: 110 United States federal regulations read at two past dates, with the retrieval ablation replicated on it, the conflict detector's precision measured as two numbers rather than one, and the annotation rubric separated from the reader's specialisation by a 2x2 factorial. |
| **3** | **The department report** | `deliverables/Deliverable_3_Department_Report.docx` | The report for departmental submission, built in the exact template of the September 2026 "RAG Framework Report": bordered title page with the IIT Kharagpur logo, certificate page, hand-set table of contents, numbered sections, tables with filled header rows, page numbers bottom-right. |
| **4** | **The presentation** | `deliverables/Deliverable_4_Presentation_18Nov.pptx` | 23 slides for a 15–20 minute MTP review, in the IIT ISE house style, with **speaker notes on every slide**. Every number on every slide is read from the results JSON at build time, so the deck cannot drift from the measurements. |

| **5** | **The project report, written fresh** | `deliverables/MTP_Report.docx` (+ `.pdf` reading copy) | A section-wise report written from scratch: abstract, literature review, system design with every formula in LaTeX, methodology, results, discussion, limitations, conclusion and future work, and a reference list in APA. Every formula is a real Word equation compiled from LaTeX, not a picture. 32 pages: the title page and the certificate page in the department's template, then the six measured figures in their own sections. Built by `deliverables/scripts/make_thesis_report.py` from `deliverables/templates/MTP_Report.md`. |
| **6** | **The report deck, written fresh** | `deliverables/MTP_Report_Presentation.pptx` | 38 slides for the review, with speaker notes on every one. Same measured values as the report, so the two cannot disagree. Built by `deliverables/scripts/make_thesis_deck.py`. |

Supporting material:

| File | What it is |
|---|---|
| `research/00_citation_audit.md` | The full citation audit: every reference in the proposal and the September report resolved against a live API, with the three corrections that must be applied. |
| `research/01_confidence_gating.md` … `07_frontier_2026.md` | Seven literature surveys, each verified against live bibliographic APIs. |
| `research/10_industrial_corpus_and_objectives.md` | The second corpus — 110 United States federal regulations read at two past dates — with every measurement on it, and the closing of the three open research objectives. |
| `research/11_supervisor_briefing_2026-11-11.md` | The briefing to present: the results, the novelty position, and the decisions that are the supervisor's to make. |
| `research/12_scope_reconciliation.md` | What was descoped relative to the proposal, and the three options for closing the gap. |
| `research/13_novelty_and_positioning.md` | The novelty check: five findings against the published literature, every identifier resolved live. |
| `research/14_full_explanation.md` | The whole thesis explained in one document — every term defined, every objective, every experiment, and the questions a panel will ask. |
| `research/15_label_validation_protocol.md` | The answer-validation protocol, set against the six published benchmarks it was built to match, with the sensitivity analysis of which reported numbers depend on which test. |
| `research/16_open_items_register.md` | Every limitation and every gap in one list — twelve limitations, six decisions, twenty-two measurements — each with an owner and what closing it would take. |
| `research/17_historical_figures.md` | The numbers in the prose that no artefact backs: measurements of implementations the project has since replaced, one figure quoted from another paper, and the one figure that was wrong. |
| `research/18_answer_validation_conventions.md` | Five scoring conventions applied to the same shipped answers, and what the measurement settles about the answer-accuracy column. |
| `research/19_gate_per_retriever.md` | The gate fitted separately on three retrievers: the per-retriever thresholds, the frontier as a curve, and the measured cost of a transferred threshold. |
| `research/20_soft_prior.md` | The soft prior against the hard category pre-filter — the repair the project's own threat list promised, measured, and the reason it does not work. |
| `research/21_industrial_probes.md` | The two probes the industrial corpus's unanswerable half had never had: the question-only policy and the parametric-leakage probe, run at last. |
| `deliverables/figures/` | The six figures, as PDF and PNG. They are included by the two papers, so that directory travels with them. |
| `deliverables/MTP_Plain_Language_Guide.pdf` | The same ground in ordinary words: the whole thesis as one all-in-one guide, for a reader who has never seen the project. 26 pages, with a table of contents and all six figures. |
| `deliverables/MTP_Full_Explanation.pdf` | The whole thesis explained, in one document: every term defined, every objective, every experiment, and the questions a panel will ask. 22 pages, with a table of contents. |
| `deliverables/MTP_Status_Report.pdf`, `deliverables/MTP_Technical_Documentation.pdf` | The other two prose reports as PDFs. |

All of the deliverables are **monochrome**. They are printed, photocopied and
projected, and none of those is guaranteed to reproduce a hue, so nothing
depends on a colour: the hierarchy is carried by weight and by darkness
instead. `deliverables/scripts/monochrome.py` rewrites an office file's theme
and its literal colours to greys, and the build's consistency check reads every
colour out of the shipped `.docx` and `.pptx` files and fails if one of them
is not a grey.
| `impl/` | The implementation, the corpus builder, the benchmark generator and the experiment scripts. |
| `deliverables/dataset/` | The evaluation corpus itself, with its provenance: every document with its Wikipedia URL, the upstream revision it was read at, the SHA-256 of the bytes used, and its chunk count, plus the licence and the benchmark. |

---

## Running it

```bash
# Run from the repository root.

# 1. Dependencies (see Quick start; the same list is in requirements.txt)
.venv/bin/pip install -r requirements.txt

# 2. Models (once) — embedding, cross-encoder reranker, NLI
.venv/bin/python impl/src/fetch_models.py

# 3. Corpus — 46 public industrial documents, 6 categories
.venv/bin/python impl/scripts/build_corpus.py

# 4. Focus domain — supply chain management on its own
.venv/bin/python impl/scripts/make_focus_corpus.py

# 5. Benchmark — 276 silver-standard queries (132 answerable, 144 unanswerable)
.venv/bin/python impl/scripts/build_benchmark.py

# 6. Unit and invariant tests (seconds)
.venv/bin/python impl/tests/test_hybrid.py
.venv/bin/python impl/tests/test_confidence_and_claims.py
.venv/bin/python impl/tests/test_query_form.py
.venv/bin/python impl/tests/test_invariants.py

# 7. Experiments
.venv/bin/python impl/experiments/run_ablation.py        # ~25 min, CPU
.venv/bin/python impl/experiments/run_gate.py            # ~12 min
.venv/bin/python impl/experiments/run_contradiction.py   # ~15 min
.venv/bin/python impl/experiments/run_transfer.py        # ~12 min

# 8. The contradiction labelling (Experiment 11) -- the gate's precision
#    measured against reader labels rather than against a proxy, and the
#    calibration that decides which of the gate's findings are surfaced.
cd impl
MTP_VARIANT=focus ../.venv/bin/python experiments/label_contradiction_pairs.py --sample
MTP_VARIANT=focus ../.venv/bin/python experiments/label_contradiction_pairs.py \
    --judge-input results_focus/exp11_judge_input.json
../.venv/bin/python experiments/make_contradiction_control.py \
    --out results_focus/exp11_judge_control.json
../.venv/bin/python experiments/make_contradiction_control.py --blind \
    --out results_focus/exp11_judge_control_input_b.json

# Annotator A: the model the generation experiment already uses. The key is
# read from ~/.mtp_llm_key by the wrapper, so it never appears on a command
# line, in a process listing or in a transcript.
bash scripts/run_contradiction_labeling.sh \
    --input results_focus/exp11_judge_input.json \
    --out   results_focus/exp11_judge_a_labels.json
bash scripts/run_contradiction_labeling.sh \
    --input results_focus/exp11_judge_control.json \
    --out   results_focus/exp11_judge_control_a.json

# Annotator B: a different model family, reading the same rubric blind. Any
# second model will do; what matters is that it does not share a family with
# A and that it never sees the detector's scores. The --no-stratum sheet is
# the same rubric and the same passages with the stratum removed, so its
# blindness is structural rather than a promise.
MTP_VARIANT=focus ../.venv/bin/python experiments/label_contradiction_pairs.py \
    --judge-input results_focus/exp11_judge_input_b.json --no-stratum

# Score both annotators, check them on the control set, and fit the
# calibration the pipeline reads to decide what is surfaced.
MTP_VARIANT=focus ../.venv/bin/python experiments/label_contradiction_pairs.py --score \
    --judge results_focus/exp11_judge_a_labels.json \
    --judge results_focus/exp11_judge_b_labels.json \
    --control        results_focus/exp11_judge_control.json \
    --control-labels results_focus/exp11_judge_control_a.json \
    --control-labels results_focus/exp11_judge_control_b.json \
    --calibration    artifacts_focus/conflict_calibration.json

# The detector's own positive control (Experiment 11b): pairs whose correct
# behaviour is known in advance, so that a measurement of zero on a corpus
# with no positives can be read as "the corpus cannot exercise the
# mechanism" rather than "the mechanism does not work".
MTP_VARIANT=focus ../.venv/bin/python experiments/contradiction_control.py

# Which generators can answer this benchmark's own questions (Experiment 13):
# one request per question per generator, at the output budget the shipped
# run used, with a retry at a larger budget where a request comes back empty.
# It reads the key from ~/.mtp_llm_key itself, so the key never appears on a
# command line, in a process listing or in a transcript.
MTP_VARIANT=focus ../.venv/bin/python experiments/run_generator_completion.py

# The generator-side comparison itself, and its replication on a second
# generator (Experiment 8). The replication is the one that cannot be run:
# the second generator returns no text on the benchmark's table questions.
bash scripts/run_generation_eval.sh --condition cautious
bash scripts/run_generation_eval.sh --condition answering
MTP_LLM_MODEL=MiniMax-M3.1-Flash bash scripts/run_generation_eval.sh \
    --condition answering --tag flash

# 9. Rebuild every deliverable from the measured results
cd ..
.venv/bin/python deliverables/scripts/build_all.py
```

Total: about an hour on CPU for the retrieval experiments, plus the labelling
round (one API call per pair, so a few minutes per annotator).
Everything on the retrieval side is seeded; the generator-side comparison is not, because the provider's sampling temperature is fixed rather than seed-controlled; the index and embeddings are
cached by content hash; the results are written to `impl/results/` as JSON
(full detail) and markdown (the tables that appear in the report).

---

## Trying it yourself

There is no server. The framework is a library (`impl/src/pipeline.py`) and
every measurement is a batch script that writes JSON — which is the right
shape for a thesis, and an awkward shape for poking at by hand.
`impl/scripts/ask.py` is the driver that fills the gap: it runs the real
online path and prints what each stage decided.

```bash
cd /Users/ritikraj/Documents/MTP

# one question
MTP_VARIANT=focus .venv/bin/python impl/scripts/ask.py \
  "what is the economic order quantity?"

# an interactive session
MTP_VARIANT=focus .venv/bin/python impl/scripts/ask.py \
  --category supply_chain_management
```

It prints the two retrieval legs, the fusion, the modality quota, the
reranked top ten, the gate's posterior against its threshold together with the
five signals it was calibrated on, and then the answer. On a question the
corpus cannot answer, the gate refuses and the language model is never
reached — that refusal is the thing to watch for, and it is why the refusal
message is printed in full.

### Swapping in your own documents

The corpus is plain files on disk, one directory per category:

```
impl/data/corpus/<category>/<document>.md
```

A `.md` or `.txt` file is chunked on its `##` headings, and markdown pipe
tables become table chunks in their own right. The category comes from a
`<!-- category: X -->` comment at the top of the file, or from the directory
name. `.pdf` files work as well.

`MTP_VARIANT` is the switch. It moves every path at once — corpus, benchmark,
index, results — so a variant runs on its own data without touching either
measured corpus:

```bash
# a sandbox of your own
mkdir -p impl/data/corpus_mine/my_category
cp my-document.md impl/data/corpus_mine/my_category/

MTP_VARIANT=mine .venv/bin/python impl/scripts/build_index.py
MTP_VARIANT=mine .venv/bin/python impl/scripts/build_benchmark.py
MTP_VARIANT=mine .venv/bin/python impl/experiments/run_gate.py
MTP_VARIANT=mine .venv/bin/python impl/scripts/ask.py "your question here"
```

`impl/data/corpus_demo/` is exactly such a sandbox, with a couple of small
documents already in it, so those commands work before you have added
anything of your own.

Two things about a new variant. The models are cached per variant, so point
the cache at one that already exists instead of downloading them again:

```bash
mkdir -p impl/artifacts_mine
ln -sfn ../artifacts_focus/model_cache impl/artifacts_mine/model_cache
```

And the gate has to be refitted on the new benchmark, which `run_gate.py`
does: a threshold calibrated on one corpus is not a threshold on another.
Until it is refitted the framework runs on its un-calibrated fallback and
says so on startup.

### The tests

```bash
.venv/bin/python impl/tests/test_hybrid.py
.venv/bin/python impl/tests/test_confidence_and_claims.py
.venv/bin/python impl/tests/test_query_form.py
.venv/bin/python impl/tests/test_invariants.py
```

The invariant tests are the ones worth reading: they assert the properties the
design claims — that the category pre-filter restricts both retrieval legs,
that the reranker only permutes the pool it is given, that the generator
is reachable only through the gate, and that a malformed query never reaches
it either.

---

## The implementation

```
impl/src/
├── config.py         Every hyperparameter, with provenance
├── ingestion.py      PDF/markdown → modality-tagged chunks
├── lexical.py        BM25, implemented from scratch
├── models.py         Embeddings, cross-encoder, NLI
├── hybrid.py         Reciprocal Rank Fusion + the swap-based modality quota
├── confidence.py     The posterior, Platt/isotonic calibration, ECE, Brier,
│                     risk–coverage, and the gate itself
├── query_form.py     The runtime form check: is this a question at all?
├── contradiction.py  Joint NLI + topical gate, entity overlap, numeric conflict
├── claims.py         Claim decomposition, noisy-OR, entropy, information gain
├── evaluate.py       Recall@k, nDCG@k, MRR, per-modality recall, faithfulness
├── stats.py          Cohen's κ, McNemar, Wilcoxon, bootstrap, Cliff's δ
└── pipeline.py       The orchestration
```

The components that are *not* in the upstream literature are implemented here
rather than taken from a library, because the thesis has to defend them: BM25
(so the scoring function and its edge cases can be argued), RRF (so the fusion
rationale can be derived), the calibration (so the threshold is a probability and
not a score), and the per-claim aggregation (so the information-gain figure is
the one the paper claims).

---

## The findings

These are the substantive results. Most of them are negative, which is the
point: the contribution is a measurement of which reliability mechanisms pay
for themselves in industrial text, and what they cost. Every number below is
substituted from `impl/results/` at build time.

**1. The encoder, not the fusion, was the weak part.** The dense leg was
originally a general-purpose sentence encoder, trained with a *symmetric*
similarity objective; retrieval is asymmetric, because a passage does not
resemble a question, it answers it. The mismatch was measurable on the
six-category corpus: dense-only retrieval reached Recall@10 0.652
against plain BM25's 0.917, and the *fusion's* ordering was worse
than the lexical leg's — nDCG@10 0.666 against 0.735 — because the fusion was spending the lexical leg's slots on
the dense leg's worse candidates. Replacing it with a retrieval-trained encoder
(BAAI/bge-m3) moved the dense leg to 0.750 and cut that ordering deficit
from 0.735 − 0.666 to 0.728 − 0.730. The fusion is now level with plain BM25 rather
than behind it, though the difference is not significant on recall
(+0.023, p = 3.2 × 10⁻¹): **fusion stopped being a loss; it did not
become a win.** The generalisable point: a hybrid is only as good as its
weaker leg, and the weaker leg spends the stronger leg's slots — so what a
hybrid retriever buys is bought by the *encoder*, not by the fusion. The
before/after is in `research/09_encoder_swap.md`.

**2. A reranker's recall is governed by the size of its candidate pool — and
more is not always better.** Sweeping the pool size gives a curve that rises
and then falls: Recall@10 goes from 0.902 at a pool of 5 to 0.955 at a
pool of 10 — the size of the final context — and then back down to 0.932 at a pool of 100. The peak is at 10, worth
+0.053 over the smallest pool, and a pool past it does not merely fail
to help: it costs, because the extra candidates are distractors competing for
the same ten slots. A cross-encoder can only reorder what it is shown, so a
pool the size of the context cannot reach evidence the first stage discarded.
This is a candidate explanation for the −5.34 pp reranker regression reported
in the September 2026 project report on a different corpus, and it converts
that anomaly into a cheap configuration check: one parameter.

**3. The reranker buys ordering, not recall.** On the six-category corpus its
effect on Recall@10 is +0.000 (p = 1.0 × 10⁰) — indistinguishable
from zero — while its effect on MRR is +0.111 (p = 9.3 × 10⁻⁴)
and on nDCG@10 +0.085 (p = 1.8 × 10⁻³). On a
silver-standard benchmark Recall@10 is close to its ceiling for every system —
a question derived from a chunk contains that chunk's own words — so the
ordering metrics are where the systems differ and where the paired tests have
anything to measure. On the focus domain, with 32 answerable questions, even
the ordering difference falls below significance; the effect is a property of
the corpus size as much as of the mechanism.

**4. The modality quota only pays where the corpus leaves something for it to
buy.** On the focus domain table recall is already 1.000 without it, so the
quota only moves overall recall: +0.031 applied before the
reranker and -0.031 applied after it. On the six-category corpus,
where the reranker takes table recall from 0.929 to 0.929, the
quota applied before the reranker restores it to 1.000 and applied after
it to 0.929. Which placement is cheaper depends on the retriever, not
on the quota's own logic — a more useful answer than the one it replaced.
And the corpus composition bounds all of it: this corpus is 88.8% text,
the September 2026 corpus was 90.6% text, and two independently constructed
industrial corpora land on the same composition because that is what
industrial documentation is.

**5. The long-context baseline is measured on cost and on answer quality; on this corpus it does not win on coverage or cost, and it does not win significantly on quality either.**
On the focus domain the whole corpus is 202,529 tokens against the
RAG arm's 2,246 accepted context — The long-context arm sends 74x more input tokens per query than the pipeline, which at the provider's cached-prefix pricing, with the corpus prefix served as a cache read on 33.0% of the long-context arm's input tokens is a 58.8x input-cost ratio rather than 74x: the token ratio and the cost ratio are different numbers, and only the second one is a cost. The RAG arm
reaches the same
evidence using 0.90% of what it reads. On the six-category
corpus the corpus is 680,417 tokens, 282x the
RAG arm's context. That corpus exceeds the 128K window that most hosted
models offer, but it fits the 1M-token window of the generator used here, so
the answer-quality half is measured on the focus domain because that is the
domain this thesis is about and because the two corpora are never pooled -- not
because the comparison would have been impossible, and running it there is
now the obvious next measurement. A retrieval-side proxy shows
the evidence stays locatable at the top of the whole-corpus ranking
(0.969 in the top 10 of 735 candidates, median
rank 1), so the long-context arm's advantage would have
to come from the reader rather than from the retrieval. The answer-quality half of the comparison was measured on the focus domain. With the whole corpus in the prompt the generator answered 31 of 32 answerable questions, the same coverage as the pipeline, and it declined the unanswerable questions at a comparable rate (76 of 144 against 77 of 144), for 74 times the input actually sent per query. On coverage and on cost the result is settled: the whole-corpus prompt declines no more unanswerable questions than the pipeline does and costs 74 times as much to do it. On answer quality the margin is directional but not statistically significant once the answers are scored without the length confound.

**6. The framework's own hypothesis about hallucination was tested under two prompt conditions, and it is supported under both prompt conditions.** The framework's hypothesis H2.1 is that a
code-level, non-bypassable gate reduces hallucination. The generator-side
comparison that would test it — one generator behind five arms, under two
prompt instructions differing by a single sentence, asking how often each arm
answers a question that has no answer — was run with MiniMax-M3 under two prompt conditions. One of the five
arms is a **random-escalation control** that refuses the same number of
questions as the fitted gate and picks them at random, which is what separates
"the gate refused" from "the gate refused the right ones". The replication on a
second generator could not be run, and the reason is measured rather than
guessed: MiniMax-M3 returned no text on 0 of the 66 questions it was asked (0 of them on the benchmark's table-lookup family, against 0 of 22 on a control sample of the other families); MiniMax-M3.1-Flash returned no text on 24 of the 66 questions it was asked (23 of them on the benchmark's table-lookup family, against 1 of 22 on a control sample of the other families). The failures are not a shortage of output budget -- of the requests that came back empty, 13 were rescued by retrying at 4096 tokens and 11 were still empty there, the model spending the whole budget on reasoning and returning nothing. An empty completion is neither an answer nor a refusal, so the harness records the run as not-run instead of reporting a rate it cannot stand behind.
Conditional: the hypothesis holds under both prompt conditions. Under the cautious prompt -- the deployed system -- it is supported, at a price: the gate reduced the rate of answering unanswerable questions from 0.535 to 0.417, a fall of 11.8 points, at the cost of answering 30 of 32 answerable questions. Paired question by question, the gate refused 23 of the questions the ungated arm answered and let through 6 of the ones it did not (exact McNemar p = 0.002). Under the answering prompt, which differs from the cautious one by a single sentence, it is supported, at a price: the gate reduced the rate of answering unanswerable questions from 0.938 to 0.528, a fall of 41.0 points, at the cost of answering 30 of 32 answerable questions. Paired question by question, the gate refused 60 of the questions the ungated arm answered and let through 1 of the ones it did not (exact McNemar p = < 0.001). What the framework claims is therefore that the gate reduces the rate of answering unanswerable questions whatever the generator does, and that it is the one component whose behaviour does not depend on the generator's cooperation: the prompt can be wrong, and the gate still holds. The retrieval-side refusal rate, which is what the
retrieval experiments could measure, is 23.6% of the
corpus-anchored unanswerable questions (26 of 110) and 76.5% of the out-of-domain ones (26 of 34)
at the operating point the gate was fitted at (τ = 0.05),
with a generator behind the pipeline that refusal rate turns out to be largely redundant wherever the generator is permitted to decline, because the generator declines those questions on its own. The pooled figure over the whole unanswerable
class is 36.1%, and that pooled figure is an upper
bound.

**The upper bound was earned, then replaced by a measurement.** The first
audit of the unanswerable half found it separable from the question text
alone: a classifier that saw only the question's shape told the answerable
questions from the unanswerable ones at an ROC AUC of 0.999, and
one regular expression — a fabricated `PREFIX-digits` identifier — carried the
hard family whole, 76.4% of the class, with no false
positives at all. The
half was rebuilt as a **corpus-anchored** class: the same question stems, the
same source documents, the same label machinery, and each repaired question
given a structural twin in the answerable class (106 of 110 of them
have one). Re-measured, the shape-only classifier scores 0.608
against a permutation null of 0.468, and the one-rule shortcut
carries 0.0%. A **question-only policy** — a model given
the question and no documents, asked whether the corpus could answer it —
discriminates the two classes at a ROC AUC of 0.675
before the repair and 0.564 after, where 0.5 is no
discrimination at all. §E.9 has the
audit, the repair and the numbers.

**And one result that constrains the gate.** The retriever's own recall of the
gold chunk is 100.0%: the evidence is missed for 0.0% of answerable questions. The gate's ceiling is therefore
set by the retriever, not by its threshold — the right diagnostic for a gate
that still answers questions it should have refused is to fix the retrieval,
not to tighten the gate.

---

## A fourth thing the implementation caught

The first version of the confidence gate calibrated at the **chunk** level: for
every (query, candidate) pair it asked "is this candidate the gold chunk?" and
fitted a logistic map from the reranker score to that label.

With about fifty candidates per query and one gold chunk, the base rate of
positives is roughly 2%. A classifier that answers "nothing is relevant" is
therefore right 98% of the time, and maximum-likelihood fitting duly returned a
large **negative** intercept (β₀ = −2.88) and a nearly flat slope (β₁ = 0.27).
The Brier score was 0.011 and the ECE 0.004 — which looked excellent, because
they were measuring the base rate rather than the filter. The operating point it
implied refused 46% of the answerable questions.

The gate does not decide "is this candidate the gold chunk". It decides "does
this retrieved context contain the answer at all". Recalibrating at the
**query** level removes the degenerate solution, because the base rate there
is around a third rather than 2%.

The same lesson turned up a second time, in a place nobody expected. The
benchmark's **unanswerable** half — the half a refusal benchmark lives or
dies on — was separable from the question text alone: one regular expression
caught 76.4% of it, because its hard case named a
fabricated identifier that no answerable question ever named. So the gate's
headline refusal rate was an upper bound rather than a measurement. The half
was rebuilt as a *corpus-anchored* class and every number was taken again;
the refusal rate on the hard stratum is now 23.6%, not
the number the defective class produced. The audit is
`impl/experiments/audit_unanswerable_class.py` and §E.9 has it.

The general lesson is the one the 2026 literature draws when it warns that
query-time filters can measure benchmark construction rather than filtering:
**the label you choose determines what you are measuring.** A beautiful
calibration number is not evidence that the thing is calibrated, and a
headline refusal rate measured on a defective class is not evidence that the
gate refuses well. The corrected design is described in
`impl/src/confidence.py` and in Part C.7 of the guide.

---

## The dataset, and the focus domain

Two corpora are in play, and they are not the same thing.

**The primary corpus** of the September 2026 specification was 634 chunks across 24
proprietary supply-chain documents. It is not redistributable, so it cannot ship
with this work or be re-run by a reader.

**The public substitute** is what every number here was measured on:
46 industrial-engineering articles from English Wikipedia
(2,383 chunks, 6 categories), fetched through the
MediaWiki API, licensed CC BY-SA 4.0. It ships in full in
`deliverables/dataset/`, with a manifest giving for every document its Wikipedia
URL, the upstream revision it was read at, the SHA-256 of the exact bytes used,
and its chunk count.

**The focus domain** is supply chain management — 14
documents, 735 chunks, 176 questions. It is the
domain the primary corpus covered and the one the practitioner scenarios come
from, so the thesis is focused there rather than spread thin; the other five
categories exist for the cross-category transfer experiment, which by
definition needs a subset of categories to transfer to held-out ones.

```bash
.venv/bin/python impl/scripts/export_dataset.py   # rebuild deliverables/dataset/
```

---

## Honesty notes

Three things in this work are worth stating plainly, because a reader who finds
them on their own will trust the rest less:

- **The evaluation corpus is a public substitute, not the proprietary corpus.**
  The 634-chunk supply-chain corpus of the September 2026 report is not
  redistributable. The implementation ships a public, multi-category industrial
  corpus with the same properties so that the pipeline runs and the ablation
  numbers are reproducible. The two are never pooled, and the results are
  reported as replication on an independent corpus. The substitute ships in
  full, in `deliverables/dataset/`, with the source and a per-document hash.
- **The benchmark's answer labels were defective, and the defect was found by
  auditing them and then repaired.** An audit of the label generator found
  that 27 of the 132
  answerable questions carried an answer label attached to the wrong question
  (20.5%): a table question that names the column
  its key came from rather than the column its answer came from, and a numeric
  gold that is a digit prefix of a longer token in the chunk. The gold *chunk*
  was correct in every case, so the retrieval-side measurements were never
  affected and only the answer-side accuracy was depressed, equally for every
  arm. The generator was corrected, the benchmark rebuilt, and every
  experiment in this project re-measured against it; the audit now finds   0 remaining defects out of 32, and
  the benchmark as it stood before the repair is kept so that the finding
  stays checkable. The numbers reported everywhere else are the post-repair
  ones.
- **The benchmark's unanswerable half was separable from the question text
  alone — and was rebuilt.** A classifier that sees only the question's *shape* -- its stem, its subject size, whether the subject contains a digit, an acronym or a fabricated identifier -- tells the answerable questions from the unanswerable ones with an ROC AUC of 0.608 against a permutation null of 0.468 that the same procedure produces on shuffled labels (p = 0.050), against 0.999 before the unanswerable class was rebuilt; on the better-powered six-category benchmark, whose answerable class is four times larger, the same measurement gives 0.533 against a permutation null of 0.500 (p = 0.267) The defect was in the
  half's designated hard case, which asked about a fabricated identifier
  (`SKU AST-5454`); every one of those questions carried an identifier shape
  that no answerable question carried, so one regular expression separated
  the classes perfectly. The consequence was a bound on the headline refusal
  rate rather than a contradiction of it: the retrieval-side results were
  unaffected, and the arm comparison was unaffected because every arm is
  asked the same questions. The half was then rebuilt as a corpus-anchored
  class — the same question stems, the same source documents, the same label
  machinery, and each repaired question given a structural twin in the
  answerable class — and every measurement was taken again. The one-rule
  shortcut now carries 0.0% of the class instead of   76.4%, the label certificates re-check with   1 of 110 failures, and the benchmark as it stood before the
  repair is kept so that the finding stays checkable. §E.9 has the audit,
  the repair and the numbers.
- **The benchmark is silver-standard, not expert-annotated.** Labels are
  derived mechanically from the documents. This inflates *absolute* recall
  (the derived gold chunk is guaranteed to contain the answer somewhere). It
  does not bias the *comparison* between systems, which is what the ablation
  tests. The benchmark holds 276 queries: 132 answerable and   144 deliberately unanswerable, split between out-of-domain topics
  and *near-misses* — questions
  of exactly the same surface form that name an identifier verified absent from
  the corpus, such as "What is the economic order quantity for SKU A-4711?".
  The near-miss class is the hard case for a confidence gate: a lexical
  retriever will happily return the passage about SKU A-104.
- **The gate's label is answer-in-context detectability, not evidence
  sufficiency.** The positive class is "the gold chunk is in the reranked
  candidate pool"; the negative class holds answerable questions whose evidence
  the retriever missed alongside the genuinely unanswerable ones. The gate's
  features are retrieval scores, so its ceiling is set by the retriever rather
  than by its threshold. The contingency table is reported rather than a base
  rate alone, and the operating point is re-fitted per corpus.
- **The framework's own hypothesis about hallucination was tested under two prompt conditions, and the answer is supported under both prompt conditions.** H2.1 -- that a code-level, non-bypassable gate reduces hallucination -- is supported under both, and what the framework claims is that the gate reduces the rate of answering unanswerable questions whatever the generator does: it is the one component whose behaviour does not depend on the generator's cooperation. What it does not claim is that a refusal rate is a hallucination rate -- the two are different quantities and neither is presented as the other. The claim is also established for one generator: the replication on a second generator could not be run, because MiniMax-M3.1-Flash returned no text on 24 of the 66 questions it was asked -- 23 of them on the benchmark's table-lookup family, against 1 of 22 on a control sample of the other families -- and 13 were rescued by a larger output budget. An empty completion is neither an answer nor a refusal, so the harness records the run as not-run instead of quoting a rate it cannot stand behind.
- **The architectural contribution is incremental.** Every one of the five
  mechanisms has published prior art, and the deliverables position each against
  it explicitly rather than claiming priority. What the work adds is a
  failure-mode characterisation and an evaluation protocol. The claims that are
  *not* supported — superiority over conformal abstention, priority on gating or
  on hybrid retrieval, the absence of a public industrial benchmark, any
  superiority over long-context prompting — are listed explicitly in the guide
  (Part H) and in the paper.

---

*All arXiv identifiers and DOIs in this repository were resolved against live
bibliographic APIs (arXiv, Semantic Scholar, Crossref, the ACL Anthology) on
31 October 2026. Where an earlier version of the project's documents carried a
DOI that resolves to a different paper, the correct identifier is used here and
the discrepancy is recorded in `research/00_citation_audit.md`.*
