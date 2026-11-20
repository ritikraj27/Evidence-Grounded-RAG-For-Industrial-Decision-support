# An Evidence-Grounded RAG Framework for Industrial Decision Support
## The Complete Guide — every term, every formula, every line of code, and every number

**Ritik Raj [25IM60R12]** · Supervisor: Dr. Sri Krishna Kumar
Department of Industrial and Systems Engineering, Indian Institute of Technology Kharagpur

---

# How to use this document

You are about to defend this work. This document is written so
that you can go into that room knowing not just *what* the system does but *why each
piece is the way it is*, what the evidence supports, and where the evidence runs out.

It has ten parts:

| Part | What it gives you | Read it when |
|---|---|---|
| **A** | The five-minute version — the whole system on one page, the dataset it was measured on, and the objectives it answers | You need to explain it to a stranger |
| **B** | Every term defined, from "token" to "kappa" | Any word in a viva is unfamiliar |
| **C** | Every formula derived from first principles, with the reasoning | A committee member asks "where does that come from?" |
| **D** | The code, walked through file by file | You need to change something or answer "how is it implemented?" |
| **E** | The experiments and what the numbers actually mean | You are asked about results |
| **F** | The literature, by sub-literature, and exactly where this work stands in it | You are asked "what is new?" |
| **G** | Anticipated viva questions with defensible answers | The night before |
| **H** | Limitations, threats, and the honest boundary of the claims | You are being probed for overclaiming |
| **I** | The report and the paper, and how they differ | You are asked to distinguish them |
| **J** | A one-page glossary you can revise from the night before | You have twenty minutes left |

**A note on honesty.** Every number in this document was measured by code in this
repository, or is quoted from a paper whose DOI/arXiv identifier was resolved against a
live bibliographic API. Where a number is *not* yet measured, this document says so
rather than estimating. Section H lists the specific claims that are **not** supported
by the current evidence — knowing those is what makes the supported claims credible.

---

# Part A — The five-minute version

## A.1 The problem, the objectives, and the questions this thesis answers

An engineer on a plant floor needs to answer a question from documentation: *what is
the economic order quantity for SKU A-104 under the current policy?* A large language
model (LLM) will answer — fluently, in the right register, with plausible numbers. It
might also be **completely wrong**, because the number came from the model's internal
weights rather than from any document. In an industrial setting that is not a cosmetic
problem. A wrong economic order quantity costs inventory; a wrong safety-stock rule
costs stock-outs; a wrong Incoterm costs a legal argument. Retrieval-augmented
generation (RAG) fixes half the problem by fetching relevant passages and putting them
in the prompt. The other half — the reason you are here — is that **RAG answers anyway
when the retrieved passages do not contain the answer**, and it does not tell you which
passage supports which claim.

### The problem, stated as four problems

**P1 — The system answers when it has nothing to answer from.**
A retrieval-augmented generator produces fluent, specific, plausible output whether or
not the retrieved passages contain the answer. In an industrial setting the failure is
not a wrong *style*; it is a wrong *number*, delivered silently.

**P2 — A refusal is only useful if it can be audited.**
Abstention in most deployed systems is a sentence in a prompt, or a probability compared
against a threshold somebody chose. The reader cannot then say *why* the system declined,
and a reviewer cannot reproduce the operating point.

**P3 — A retrieved context is heterogeneous, and the heterogeneity is not random.**
The passage carrying the binding requirement — a table row, an axis label — competes for
the same ten slots as the prose written about it, and can lose.

**P4 — Two retrieved passages can disagree, and the generator will pick one silently.**
When two revisions of the same procedure are retrieved, whichever the prompt ordering
favours wins, and the practitioner is not told that a choice was made.

### The research objectives

These are the MTP proposal's objectives, in its numbering. The literature evidence base
for each is the corresponding file under `research/`, and every citation in those files
was resolved against a live bibliographic API rather than written from memory.

| # | Objective, as stated in the proposal | Design move | Evidence base |
|---|---|---|---|
| **RO1** | A code-level, non-bypassable retrieval-confidence gate that returns an explicit "no evidence" response when retrieval confidence falls below a threshold, instead of calling the LLM | **D1** | `research/01_confidence_gating.md` |
| **RO2** | Per-modality retrieval quotas that enforce a minimum share of tables, charts and images in the retrieved context, so that text chunks do not crowd out tabular evidence in industrial corpora | **D2** | `research/02_modality_balanced.md` |
| **RO3** | Hybrid lexical + dense + reranker via RRF, preceded by a category filter, outperforms flat retrieval | **D3** | `research/03_hybrid_retrieval.md` |
| **RO4** | Cross-document contradiction surfacing — a joint NLI and topical gate | **D4** | `research/04_contradiction.md` |
| **RO5** | Per-claim confidence tagging: each claim labelled *grounded*, *inferred* or *uncertain*, carrying a citation back to its source chunk | **D5** | `research/05_attribution_eval.md` |
| **RO6** | Evaluation on industrial corpora and industrial benchmarks, with cross-category generalisation | — | `research/06_industrial.md` |

**The proposal's twelve-category promise, and what was descoped and why, are
reconciled in §A.6** and in `research/12_scope_reconciliation.md`. Six of the
nine industrial-engineering categories were built, the three machine-learning
categories were descoped as a different problem class, and three industrial
categories were descoped because their binding artefacts are proprietary and
not redistributable.

### Where each objective is answered, and what the answer turned out to be

| Objective | Experiments | Headline result | Read at |
|---|---|---|---|
| **RO1** | 2 (the gate), 8 (the generator-side comparison) | The gate is a control-flow fact, not an instruction: the generator is reached only through it, and an invariant test asserts that. What the gate costs (coverage) and what it buys (refusal of unanswerable questions) are measured at a stated operating point, and the trade is reported as a risk–coverage curve rather than a single number. | §C.7, §E.2, §E.7 |
| **RO2** | 1 (the retrieval ablation) | The quota only pays where the corpus leaves something for it to buy, and *where it is placed relative to the reranker* decides more than the quota's own logic. | §C.8, §E.1 |
| **RO3** | 1 (the ablation), 5 (the candidate-pool sweep) | **Not supported.** The hypothesis — that hybrid lexical + dense + reranker preceded by a category filter beats flat retrieval — is contradicted by this thesis's own numbers on both corpora: the fusion does not beat its lexical leg (Δ Recall@10 0.000, p = 1.000 on the industrial corpus) and the category pre-filter is a no-op on recall (Δ 0.000, p = 1.000), while the *lexical* leg beats the general-purpose dense encoder (Δ −0.081, p = 0.00026). The reranker's recall is governed by the size of its candidate pool — the knee is at 10, worth +0.053 of recall — and on the industrial corpus the pool curve is unsaturated, so the displacement is measured (1.21% of golds found and then pushed out of the ten-chunk context) rather than inferred. **The repair proposed for the filter has now been measured, and it does not work.** A soft prior — the in-category chunks promoted in the fusion by an extra reciprocal-rank-fusion term instead of being the only candidates — was tried at three weights on the 132 answerable queries of the six-category corpus, and every one of them returns the no-category numbers exactly: MRR 0.7764 against the hard filter's 0.8025, paired Wilcoxon p = 0.0272. There is nothing for it to recover, because the filter's recall cost on this corpus is exactly zero — not one of its gold chunks sits outside its question's category. What the filter does buy is ordering: MRR 0.8025 against 0.7764 with no category handling, a paired difference of 0.0261 (p = 0.0272). And it buys it by *removing* the out-of-category chunks from the candidate pool rather than by promoting the in-category ones, which is why a prior that only reorders cannot reproduce it | §C.3, §E.1, §E.5, §E.11 |
| **RO4** | 3 (the detector), 11 (the reader labelling), 11b (the detector's own control), 14 (the detector on an authentic industrial corpus) | **The first corpus cannot evaluate it; the second one shows it finding the conflicts and mislabelling them.** Two defects the measurement found were repaired, and the gate's alarms fell from 81 to 20; its precision against blind reader labels is 0.0% of 20 alarms, the same readers find 0 contradictions in 80 random unflagged pairs, and the detector's own positive control is 11 of 11 — so that corpus holds concept-level prose, not the revised procedures the mechanism exists to detect. **A second corpus closes it.** Built from the United States federal regulations, it contains the conflicts the mechanism exists to find: the same provision read at two vintages. There the mechanism **detects** them — precision 0.659 (CI 0.505–0.784), 0.897 on the stratum where the conflicts are — and **types** them wrongly (0.073): it reports supersessions as contradictions and cannot say which version is in force. A 2×2 factorial then shows the measurement's binding constraint was the **rubric**, not the reader's specialisation (+0.366 against +0.049). | §C.10, §E.3, §E.11, §E.12 |
| **RO5** | 9 (the answer-side audit), 12 (the unanswerable-class audit), 15–18 (the per-claim band against an independent reference) | Per-claim tagging is in the shipped pipeline, and its labels are audited rather than asserted. The *benchmark* turned out to be the defective part: the unanswerable class was separable from the question text alone, and it was rebuilt and everything re-measured. **And the band itself was then measured** against two independent readers and an adjudicator (κ = 0.902): it is a usable **filter** — keeping only the `grounded` claims raises the share of answers containing no wrong claim from 34.4% to 50.0% against the gold evidence — and **not** a usable **ranking**, because keeping the first claims of an answer beats it — in three of the four corpus-and-protocol measurements, though only one of them clears significance — and that is not a length artefact. Against the benchmark's gold evidence the band does not track correctness at all (κ = 0.049). **On the industrial corpus the band does not replicate** — the two readers agree at κ = -0.056 (CI -0.176–0.065) over 73 claims, on answers from a different generator, and that interval spans zero on a sample too small to say whether the band replicates or not. | §C.9, §E.8, §E.9, §E.11 |
| **RO6** | 4 (cross-category transfer), 7 and 8 (the long-context baseline), 1, 2 and 5 on the industrial corpus | Coverage transfers across the industrial sub-domains and the *threshold* does not: a threshold fitted on one configuration is too permissive where it is transferred, and too permissive in the direction that flatters the configuration it is transferred to. The long-context baseline is a cost question, and the cost is measured in dollars rather than only in tokens. **The objective is now closed on a second, authentic corpus**: 110 federal regulatory documents (2,443 chunks, four regimes, public domain) with a 444-query benchmark, on which three of the thesis's negative findings replicate — BM25 beats the dense encoder (Δ Recall@10 -0.081, p = 0.00026, n = 247), the fusion does not beat its lexical leg (p = 1.00000) and the category pre-filter is a no-op (p = 1.00000) — and the candidate-pool curve is no longer saturated, so the displacement is measured rather than inferred. | §E.4, §E.6, §E.7, §E.11 |

## A.2 What this system does

Five mechanisms, each independently switchable, each with a specific failure it prevents:

| # | Mechanism | The failure it prevents |
|---|---|---|
| **D1** | **Code-level confidence gate.** A calibrated probability that the answer is *present in the retrieved context* — that is, answer-in-context **detectability**, which is not the same as evidence sufficiency (§C.7). Below a threshold, the generator is **never called** and a "no evidence" response is returned. | Confidently answering from irrelevant passages |
| **D2** | **Modality-balanced retrieval.** A quota guaranteeing a minimum share of tables and charts in the final context. | A table carrying the binding requirement being outranked by prose about it |
| **D3** | **Hybrid retrieval with category pre-filter.** BM25 + dense vectors fused by Reciprocal Rank Fusion, then a cross-encoder reranker. | Missing the passage because the retriever only understands one way of matching |
| **D4** | **Contradiction surfacing.** A joint NLI + topical gate that shows the practitioner where two passages disagree, instead of silently picking one. | Applying a superseded policy because the generator chose the wrong source |
| **D5** | **Per-claim confidence tagging.** Each claim tagged *grounded*, *inferred*, or *uncertain*, with citations and an information-gain figure. | A practitioner trusting a whole answer because one sentence in it was solid |

## A.3 The pipeline

```
STAGE 1 — INGESTION (offline, once per document)
    PDF / markdown  →  parse  →  chunk (text | table | chart)  →  tag category
                                                        ↓
                                   embed (BAAI/bge-m3, 1024-d)  +  BM25 inverted index
                                                        ↓
                                   Postgres 16 + pgvector (HNSW)  [production]

STAGE 2 — RETRIEVAL (online, per query)
    query → embed → category pre-filter → BM25 leg  ┐
                     → dense leg                   ┴→ RRF → cross-encoder rerank
                                                       → CONFIDENCE GATE
                                                       → modality quota

STAGE 3 — GENERATION (online, per accepted query)
    per-claim tagging → citations → contradiction flag → tagged answer
```

**The single most important property:** the gate sits *between* retrieval and
generation and is **not bypassable**. It is not a sentence in the prompt telling the
model to be careful. It is a branch in the code. When it rejects, the language model
is never invoked. That distinction — an instruction versus a control-flow fact — is
the difference between a design that can be audited and a design that can only be
hoped for.

## A.4 What was measured

On a real, public, multi-category industrial corpus (46 documents, 2,383 chunks,
six industrial categories) and a 276-query silver-standard benchmark including
deliberately unanswerable questions:

- **The encoder, not the fusion, decided whether hybrid retrieval paid.** With
  a general-purpose sentence encoder the dense leg reached Recall@10   0.636 against plain BM25's 0.970, and the *fused* system's
  ordering was worse than the lexical leg's — nDCG@10 0.722 against   0.798. The fusion was paying for the dense leg's slots and
  getting nothing back. With a retrieval-trained encoder (BAAI/bge-m3) the
  dense leg reaches 0.812 and the fusion 1.000 against BM25's 0.969 — ahead
  on recall by +0.031, though not significantly (p = 3.2e-01), and ahead on
  ordering too (nDCG@10 0.847 against 0.792). On the six-category
  corpus the fusion is ahead on recall by +0.023 (p = 3.2 × 10⁻¹) and
  still behind on ordering (0.730 against 0.728). **Fusion
  stopped being a loss; whether it is a win depends on the corpus, and on
  neither corpus is the difference significant.** §C.3 reports this in full,
  with both corpora's numbers.
- **A reranker's recall is governed by the size of its candidate pool.** Sweeping
  the pool size gives a curve that rises and then falls: recall@10 goes from   0.902 at a pool of 5 to 0.955 at a pool of 10 — the size of the
  final context — and then back down to 0.932 at a pool of 100. The
  peak is at 10, and a pool past it does not merely fail to help:
  it costs, because the extra candidates are distractors competing for the
  same ten slots. A pool the size of the context cannot improve recall at all,
  since it can only permute the chunks it was given. This is the most likely
  explanation of the −5.34 pp reranker regression reported in the September 2026
  project report on a different corpus, and it is the cheapest actionable
  finding in the project: one parameter, worth +0.053 of recall.
- **The modality quota only pays where the corpus leaves something for it to
  buy.** On the focus domain table recall is already 1.000 without it, so the
  quota only moves overall recall: +0.031 applied before the
  reranker and -0.031 applied after it. On the six-category
  corpus, where the reranker takes table recall from 0.964 to   0.929, the quota applied before the reranker restores it to   1.000 and applied after it to 0.929. Which placement is cheaper
  depends on the retriever, not on the quota's own logic — which is a more
  useful answer than the one it replaced. See §C.8 and Part E.
- **The long-context baseline is a cost question, and the cost is measured in
  dollars rather than only in tokens.**
  The whole corpus is 202,529 tokens; the RAG arm's accepted
  context averages 2,246. The long-context arm sends 74x more input tokens per query than the pipeline, which at the provider's cached-prefix pricing, with the corpus prefix served as a cache read on 33.0% of the long-context arm's input tokens is a 58.8x input-cost ratio rather than 74x: the token ratio and the cost ratio are different numbers, and only the second one is a cost. The RAG arm
  reaches the same evidence using 0.90% of what it reads. The
  six-category corpus exceeds the 128K window most hosted models offer but
  fits the 1M-token window of the generator used here, so the answer-quality
  half is measured on the focus domain because that is the domain this thesis
  is about and because the two corpora are never pooled -- not because the
  comparison would have been impossible. The answer-quality half of the comparison was measured on the focus domain. With the whole corpus in the prompt the generator answered 31 of 32 answerable questions, the same coverage as the pipeline, and it declined the unanswerable questions at a comparable rate (76 of 144 against 77 of 144), for 74 times the input actually sent per query. On coverage and on cost the result is settled: the whole-corpus prompt declines no more unanswerable questions than the pipeline does and costs 74 times as much to do it. On answer quality the margin is directional but not statistically significant once the answers are scored without the length confound. See §E.6.
- **The gate trades coverage for correctness**, and the trade is measurable and
  reportable as a risk–coverage curve rather than a single number. The binding
  constraint is not the threshold but the retriever: on this corpus the retriever
  finds the gold chunk for 100.0% of answerable questions, so a perfect gate could
  not usefully answer more than that.
- **On a second corpus, the negative findings replicate and the conflict
  detector's precision splits in two.** The second corpus is   110 United States federal regulations (2,443 chunks,   4 regimes) read through the eCFR versioner at two past dates, so
  the same provision at two issues *is* a conflict whose type is known by
  construction. There the lexical leg again carried the pipeline
  (-0.081 R@10 against dense, p = 0.00026) while
  neither the fusion (+0.000, p = 1.00000)
  nor the category pre-filter (+0.000,
  p = 1.00000) added anything measurable on top of it; the
  candidate-pool curve stopped being saturated, so   1.21% of the retrieved golds are displaced out of the
  context; and the gate's operating point transfers across corpora
  (coverage 0.691 against 0.693) while its threshold
  does not (0.40 against 0.05). There too a conflict
  detector's precision is **two** numbers: detection 0.659
  against the readers' labels and 1.000 against
  the construction labels, against typing 0.073 and   0.000 — the mechanism finds the conflicts and
  reports them as the wrong kind. The per-claim band replicates there as well,
  at chance against an independent reference (κ 0.055 and   0.017). And the measurement's own binding constraint
  turned out to be the annotation: a 2×2 factorial shows the wording of the
  labelling rubric moved the measured precision (+0.366
  and +0.317) while the reader's specialisation moved
  it by +0.049 and +0.000. Part E.11 has the
  whole thing; Part F.4.1 has the novelty position.

## A.5 The dataset, and where it came from

| | |
|---|---|
| **What** | 46 public industrial-engineering articles, 2,383 chunks, six categories |
| **Source** | English Wikipedia, fetched through the MediaWiki `parse` API |
| **Focus domain** | supply chain management — 14 documents, 735 chunks |
| **Benchmark** | 276 silver-standard questions (132 answerable, 144 deliberately unanswerable) |
| **Licence** | CC BY-SA 4.0 for the article text |
| **Shipped with** | `deliverables/dataset/` — the documents, the provenance manifest, the benchmark |
| **Rebuild** | `python3 impl/scripts/build_corpus.py` |

Three corpora are in play here, and they should not be confused.

**The primary corpus** of the original project specification was 634 chunks
across 24 proprietary supply-chain documents. It cannot be redistributed, so
it cannot be shipped with this work or re-run by a reader.

**The public substitute** is what every number in this guide was measured on.
It was assembled to have the properties the framework needs — several
industrial categories, real tables and figures so the modality mechanisms have
something to bite on, and a citable source — and it ships in full with its
provenance. Every document in `deliverables/dataset/manifest.json` carries its
Wikipedia URL, the upstream revision it was read at, the SHA-256 of the exact
bytes used, and its chunk count.

**The second corpus** is the Electronic Code of Federal Regulations:
110 documents, 2,443 chunks, 4 regulatory
regimes, read through the eCFR versioner API, which serves any regulation as
it stood on any past date. It was built to close two objectives the first
corpus cannot support: the contradiction detector needs a corpus that
*contains* conflicts, and the industrial claim needs *authentic* text. Because
regulations are amended, the same provision read at 2021-12-31 and at 2026-06-01 is the same rule at two issues — 948
amended-paragraph pairs, of which 361 (38.1%)
state different numbers, each a conflict whose type is known by construction
and which therefore needs no annotation. Its benchmark has 444
queries (247 answerable, 197 unanswerable)
and was audited for the same shortcut the first benchmark had. It is public
domain, so it ships with the thesis. Part E.11 has the measurements.

**The focus domain** is supply chain management: 14
documents and 735 chunks, with its own 176-question
benchmark (32 answerable, 144
deliberately unanswerable). It is the single industrial domain this thesis is
about — the one the primary corpus covered and the one the practitioner
scenarios are drawn from — and Part E traces real questions from it end to
end. The other five categories are retained for the cross-category transfer
objective, which by definition needs a subset of categories to transfer to
held-out ones.

**What the substitute is not.** These are encyclopedia articles, not the
operating manuals, standard operating procedures and supplier specifications of
a real plant. They are industrial in subject matter, not operationally binding.
The silver-standard labels are derived mechanically from the document, so
absolute recall is optimistic — the comparisons between systems are not
affected, because every system is scored against identical labels. An audit of
the label generator found that 27 of the 132 answerable questions carried a label
attached to the wrong question (20.5%); the gold
chunk was right in every case, so only the answer-side accuracy was affected,
and equally for every arm. The generator was corrected, the benchmark rebuilt
and every experiment re-measured against it; the audit now finds 0 remaining defects out of 32. See
§E.8.

## A.6 The proposal's scope, reconciled

**The proposal promised twelve categories spanning three domains.** The
proposal's own list names them, and the thesis was built on six of the nine
industrial-engineering ones, with a fourth corpus — authentic federal
regulation — standing in for the industrial limb the proposal asked for. The
other six were not built, for reasons that are worth stating before a panel
asks. The full reconciliation, with the proposal's wording and the reason for
every descoping, is in `research/12_scope_reconciliation.md`; this is the part
that belongs in the thesis.

| # | Category, as promised | Built? | Documents | Chunks | Why |
|---|---|---|---|---|---|
| 1 | **Supply Chain Management** ★ focus | **Built** | 14 | 735 | The focus domain, and the domain the practitioner scenarios are drawn from |
| 2 | **Predictive Maintenance** | **Built** | 6 | 316 | Public substitute; encyclopaedic articles about the subject |
| 3 | **Reliability Engineering** | **Built** | 7 | 465 | As above |
| 4 | **Quality Engineering** | **Built** | 7 | 362 | As above |
| 5 | **Production Scheduling** | **Built** | 7 | 244 | As above |
| 6 | **Transportation & Logistics** | Not built | — | — | **Descoped.** The binding artefacts the proposal names — carrier rate cards, routing guides, lane schedules — are proprietary and not redistributable, and the public substitute carries no rate table |
| 7 | **Reverse Logistics** | Not built | — | — | **Descoped**, same reason: RMA procedures, disposal manifests and refurbishment SOPs are proprietary plant documents |
| 8 | **Inventory Management** | Not built | — | — | **Descoped**, same reason: stock policies, cycle counts and ABC/XYZ analyses are proprietary |
| 9 | **Facility Layout & Location** | **Built** | 5 | 261 | Public substitute; the smallest of the six, and the smallest per-category sample in the benchmark |
| 10 | **Demand Forecasting** | Not built | — | — | **Descoped, deliberately.** This is a numerical, tokenised-series problem with its own models and metrics (MASE, forecast-interval coverage), not a document-retrieval problem; a text-RAG pipeline would measure the tokenizer, not the mechanism |
| 11 | **Time-Series Forecasting** | Not built | — | — | **Descoped, deliberately**, as row 10 |
| 12 | **Anomaly Detection** | Not built | — | — | **Descoped, deliberately**, and the sharpest case: Isolation Forest is a *method*, not a document category, and no amount of text retrieval would measure it |

**The fourth corpus is a substitution, not a fulfilment.** The industrial
regulatory corpus — 110 documents, 2,443 chunks, four regimes, read from the
Electronic Code of Federal Regulations at a versioner date — is **not** one of
the twelve categories. It substitutes for the proposal's *authentic industrial
corpus* limb, in the sense of the licence and the provenance discipline; it
does not substitute for the twelve categories, and it does not substitute for
the proposal's binding artefacts. The category table above still has six rows
empty.

**What we claim, and what we do not claim.** This paragraph is the thesis's
scope statement, and it is written to be lifted verbatim:

> **Scope.** This thesis evaluates an evidence-grounded RAG framework on corpora
> it could obtain and redistribute: a public six-category industrial corpus
> (46 documents, 2,383 chunks, 276 questions), its
> supply-chain focus subset (14 documents,
> 735 chunks, 176 questions), and an authentic
> regulatory corpus built from the US Code of Federal Regulations
> (110 documents, 2,443 chunks, 4
> regulatory regimes, 444 questions). **We do not claim** the
> twelve-category, three-domain industrial benchmark the proposal described:
> nine industrial-engineering categories were reduced to six, and the three
> machine-learning categories — demand forecasting, time-series forecasting and
> anomaly detection — were descoped, because they are numerical
> series-reasoning problems rather than document-retrieval problems and a
> text-RAG pipeline cannot measure them. **We do not claim** that retrieval
> configurations transfer across industrial sub-domains in general; what we
> measure is transfer across four regulatory regimes within one corpus and
> across the six categories of one public corpus, where the coverage transfers
> and the fitted threshold does not. **We do not claim** human-expert
> validation of the benchmark labels: the annotations were produced by
> domain-specialised language-model readers with an adjudicator, their
> agreement is reported in full, and consistency between readers is not
> correctness. **We do not claim** that the named analytic methods of the
> proposal — Cp/Cpk, Mann–Kendall, EOQ, Isolation Forest, FMEA RPN, Weibull,
> MASE — are computed by the framework; it retrieves, cites and cross-checks
> the artefacts they produce, and where a contradiction detector names a
> quantity it does so by vocabulary, not by arithmetic. What we do claim is
> measured, with its file named: four of the six research objectives closed
> with a negative result, one with a qualified positive on a single generator,
> and one re-scoped and closed on an authentic industrial corpus.

**Why this is on the record rather than in a footnote.** The descopings are
not all the same kind of decision. Three are engineering facts about what
could be obtained and redistributed; three are a judgement that a category is
a different problem class from the one the thesis measures; and one — the
absence of human-expert validation — is a cost the thesis pays knowingly and
reports in its limitations. The proposal's own house rule is that an honest
negative is worth more than a favourable comparison, and this is the largest
one the project has.


---

# Part B — Every term, defined

## B.1 Language and models

**Token.** The unit a language model actually reads and writes. Models do not see
words or characters; they see *tokens*, which are usually word-pieces. "Economic
order quantity" might be 4 tokens; "reorder" might be 1 token. Because pricing and
context limits are measured in tokens, and because a token can be a fragment, the
same document can cost different amounts for different models. *Why it matters here:*
the evidence trail in this system cites **chunks**, and chunk boundaries are chosen in
words (120 words ≈ 160 tokens). The chunk is the unit a practitioner can actually
go and read in the source document.

**Embedding (vector representation).** A list of 1024 numbers that encodes
the *meaning* of a piece of text, produced by a neural network. Two texts that
mean similar things get vectors that point in similar directions. The number 1024 is simply the width of `BAAI/bge-m3`'s output layer — it has no
deeper meaning.
*Why it matters here:* the embedding is what makes "what is EOQ for A-104" match a
passage that says "the economic order quantity for item A-104" even though the words
differ.

**Large Language Model (LLM).** A model trained on a very large corpus to predict
the next token. It is, fundamentally, a conditional probability distribution over
vocabulary: given the text so far, what is the probability of each next token? An
answer is generated by sampling from that distribution repeatedly. Everything a model
"knows" is stored in its weights — roughly a billion to a trillion parameters,
which is where the "knowledge cutoff" comes from. *Why it matters here:* the model's
internal knowledge is exactly the thing we distrust in an industrial setting, which
is why D1 forces the answer to come from retrieved documents rather than from the
weights.

**Prompt.** The text sent to the model, including instructions and the retrieved
passages.

**Instruction-tuned / chat model.** A base LLM further trained on instruction–response
pairs so it follows directions. `BAAI/bge-m3` and
`cross-encoder/ms-marco-MiniLM-L6-v2` are *not* chat models; they are specialised
encoders.

**Hallucination.** The generation of text that is fluent and plausible but not
grounded in any source. In this thesis it is used in the strict sense of *unfaithful
to the retrieved context* — the model states something the passages do not support.
This is a narrower and more measurable definition than "anything false", and it is
the one the evaluation measures.

**Confabulation.** Farquhar et al. (2024, *Nature* 630:625–630) distinguish this from
hallucination: a *confabulation* is an arbitrary, incorrect generation produced when
the model does not know, whereas a *consistent error* is a confidently-held wrong
belief. Token-level entropy merges these; semantic entropy separates them. **This
distinction is why "confidence" is not the same as "correctness"** — a confidently
wrong claim has high confidence and zero support. The framework therefore always
pairs a confidence tag with a citation.

## B.2 Information retrieval

**Corpus / collection.** The set of documents being searched. Here: 2,383 chunks
from 46 documents.

**Chunk.** A retrievable unit of evidence. Ours are ~101 words, tagged with
modality and category, carrying a page number and a caption.

**Query.** The user's question.

**Ranking.** Ordering documents by relevance to a query. The core of information
retrieval.

**Recall@k.** Of the documents that *should* be retrieved, what fraction appears in
the top k? *Why it matters here:* a missed safety-stock table is a failure regardless
of what else was retrieved. This is the metric the framework is optimised for.

**Precision@k.** Of the documents retrieved, what fraction is relevant? Diagnoses
over-retrieval. Not the metric to optimise, because a generator can ignore
irrelevant context.

**MRR (Mean Reciprocal Rank).** The average of 1/(rank of the first relevant
document). Sensitive to *position*: if the right chunk is first, MRR is 1; if it is
fifth, 0.2. This matters because LLMs attend most strongly to early context — the
"lost in the middle" effect (Liu et al., TACL 2024).

**nDCG@k (Normalised Discounted Cumulative Gain).** A ranked-list metric that
rewards putting *more* relevant documents *higher*, normalised by the ideal ranking
so that queries with different numbers of relevant documents are comparable. The
formula is derived in §C.10.

**BM25.** A lexical ranking function. The "25" is a version number, not a count.
Derived in full in §C.2.

**Term Frequency (TF), Inverse Document Frequency (IDF), TF-IDF.** TF is how often a
term appears in a document; IDF is how *rare* that term is across the corpus.
TF-IDF multiplies them: a term that appears often in this document and rarely in
others is the most informative. BM25 is a more careful descendant of the same idea.

**Bi-encoder / dual encoder.** Two towers that encode the query and the document
*separately*, so every document can be embedded once and stored. Enables
approximate nearest-neighbour search over millions of documents. Cannot represent
"this passage answers *that* question" — only "this passage is about something like
this question".

**Cross-encoder.** One model that reads the query and the document *together*,
concatenated, so every token of the document can attend to every token of the query.
Strictly more accurate, and strictly more expensive: one forward pass per
(query, document) pair, so it can only be applied to a shortlist, never to a whole
corpus. This is why the pipeline is bi-encoder → fusion → cross-encoder.

**HNSW (Hierarchical Navigable Small World).** A graph-based approximate
nearest-neighbour index. Fast, and *approximate*: it can miss true nearest
neighbours. `pgvector` implements it for Postgres.

**pgvector.** The Postgres extension that adds vector types and HNSW/IVFFlat
indexes, so vectors live next to the rest of the data and can be filtered with
ordinary SQL. *Important caveat:* HNSW applies metadata filters **after** the graph
traversal, so a selective filter can silently destroy recall. The fix is
`SET hnsw.iterative_scan = strict_order;` — without it, a category filter may return
almost nothing. This is a production trap worth knowing.

**Reciprocal Rank Fusion (RRF).** Combining several ranked lists into one without
comparing their scores. Derived in §C.4.

## B.3 Confidence, calibration, and statistics

**Posterior probability.** After seeing evidence, the probability that a hypothesis
holds. Here: that a chunk is relevant to the query.

**Likelihood ratio.** The ratio of how likely the evidence is if the hypothesis is
true to how likely it is if the hypothesis is false. The engine of Bayesian
inference. Derived in §C.6.

**Prior / prior odds.** What you believed before seeing the evidence.

**Log-odds.** The logarithm of the odds, i.e. log(p / (1−p)). Addition of
log-odds becomes multiplication of odds, which is why Bayesian updating adds up.

**Calibration.** Whether a predicted probability of 0.8 really corresponds to 80%
accuracy. A model can be *accurate* and *uncalibrated* at the same time: it may get
the right answer 70% of the time while claiming 95% confidence every time.

**Platt scaling.** Fitting a logistic (sigmoid) map from a raw score to a
probability, by maximum likelihood on held-out data.

**Isotonic regression.** Fitting a free-form monotone map from score to probability.
More flexible, more variance.

**Brier score.** Mean squared error between predicted probability and the binary
outcome. Lower is better.

**Expected Calibration Error (ECE).** The sample-weighted mean gap between
confidence and empirical accuracy across probability bins. The number a reviewer
asks for.

**Reliability diagram.** Accuracy versus confidence per bin, with the diagonal as
the perfect-calibration reference.

**Risk–coverage curve.** The operational question: if the system abstains on the
least-confident fraction, how accurate is what remains? "Coverage" is the fraction
answered; "risk" is the error rate among those answered.

**Selective prediction / abstention.** Refusing to answer when confidence is low, so
that the answers you *do* give are more reliable. This is the entire point of D1.

**Abstention precision.** Of the queries the system refused, what fraction were
genuinely unanswerable? A high false-refusal rate and a low abstention precision
together mean the gate is refusing almost everything.

**Cohen's kappa (κ).** Chance-corrected agreement between two human raters.
κ = (observed agreement − chance agreement) / (1 − chance agreement). Raw
agreement is inflated when most items fall in one dominant category; kappa corrects
for that. The September 2026 report measured κ ≥ 0.7 on four categorical fields.

**McNemar's test.** For two systems evaluated on the same items with a binary
outcome. The paired alternative to an unpaired test, and the right test for "is
system A better than system B on the same 276 queries".

**Wilcoxon signed-rank test.** The non-parametric paired test for continuous or
ordinal outcomes. Preferred over the paired t-test when the differences are bounded
and skewed — which per-query faithfulness scores are.

**Effect size.** How big the difference is. Cohen's *d*ₓ = mean(difference) /
sd(difference) for paired samples. Cliff's delta is the non-parametric alternative
in [−1, 1].

**Confidence interval.** A range the true value plausibly lies in. A 95% bootstrap
CI means 95% of resamples produced an interval containing the true value.

**Bootstrap.** Resample with replacement, recompute the statistic, and use the
spread of the results.

**Type I / Type II error.** Type I: rejecting a true null (a false positive — you
claimed an improvement that is not there). Type II: failing to reject a false null
(missed improvement). *Why it matters here:* the September report's modality result
was a null. With a corpus that is 88.8% prose, a null is the **expected** outcome,
not a bug.

**Power.** The probability of detecting a real effect of a given size. A null
result on an underpowered experiment is not evidence of no effect.

**ANOVA.** Comparison of several groups' means. Not used here — the systems are
paired on the same queries, which is a stronger design.

## B.4 Natural Language Inference and claims

**NLI (Natural Language Inference).** A model that reads a *premise* and a
*hypothesis* and labels the relationship as **entailment** (the premise makes the
hypothesis true), **neutral** (neither proves nor disproves), or **contradiction**
(the premise makes the hypothesis false).

**Claim.** An atomic statement that can be true or false on its own.

**Decomposition.** Splitting an answer into its constituent claims so each can be
checked separately.

**Noisy-OR.** Combining independent "witness" events: P(at least one succeeds) =
1 − Π(1 − pᵢ). Derived in §C.9.

**Entropy.** Shannon entropy H(p) = −p log₂ p − (1−p) log₂(1−p), in bits. H(0.5) = 1
(maximum uncertainty), H(0) = H(1) = 0.

**Information gain.** How much observing something reduced your uncertainty.
IG(X; Y) = H(Y) − H(Y|X). Derived in §C.9.

**Faithfulness.** The fraction of an answer's claims entailed by the retrieved
context. RAGAS-style.

**Citation precision / recall.** ALCE-style. *Citation precision*: of the claims
carrying a citation, what fraction have a citation that actually supports them.
*Citation recall*: of the claims that could be cited, what fraction carry one.
Reporting only precision is a trap: a system that cites nothing scores 1.0
precision and 0.0 recall.

**Ground truth / silver labels.** "Ground truth" is human expert annotation.
"Silver" labels are mechanically derived from the document itself. Cheaper and
perfectly reproducible, but slightly optimistic, because the derived gold chunk is
guaranteed to contain the answer somewhere whereas an expert might have judged it
insufficient. Our 276-query benchmark is silver; the 300-query SupplyChainQA v7 is
expert-annotated with κ ≥ 0.7.

---

# Part C — The mathematics, derived

This part derives every formula in the system. Each derivation answers: *what
assumption do I need, and what breaks if it is false?*

## C.1 Cosine similarity — the dense retrieval score

**What we want.** A number in [−1, 1] measuring how alike two embeddings are.

**Definition.** For vectors **q** (query) and **d** (document) in ℝ^d:

```
             q · d
cos(q, d) = ───────────
            ‖q‖ ‖d‖
```

**Derivation of the denominator.** The dot product **q** · **d** = Σ qᵢdᵢ is
the product of the two magnitudes times the cosine of the angle between them:

```
q · d = ‖q‖ ‖d‖ cos θ
```

Rearranging gives the formula. This is not a heuristic — it is an identity.

**Why divide at all?** Because the dot product alone rewards *long* vectors. A
document with large entries in many dimensions gets a large dot product with many
queries, regardless of meaning. Dividing by ‖q‖‖d‖ removes the magnitude and keeps
only the angle: the *direction* of the embedding is the meaning, the length is an
artefact of how the network happened to encode it.

**What breaks if the assumption is false.** The assumption is that direction encodes
meaning and magnitude does not. For normalised sentence embeddings this is
empirically well supported. It is *not* true for, e.g., TF-IDF vectors, where the
magnitude carries term frequency — which is exactly why BM25 needs its own
normalisation (below).

**Implementation note.** Once vectors are L2-normalised, cos(q,d) = **q** · **d**,
because ‖q‖ = ‖d‖ = 1. The code therefore normalises once and uses a plain matrix
product, which is what makes a pgvector HNSW dot-product index viable.

## C.2 BM25 — the lexical score, derived from the probabilistic relevance framework

**Starting point.** Under the PRF, a document is relevant with probability

```
P(R | D, Q) ∝ P(D | R, Q) · P(R | Q)
```

`P(R | Q)` is the same for every document, so it does not affect the *ranking*.
Drop it. What remains is a product over query terms:

```
P(D | R, Q) = Π_{t ∈ Q} P(t | D, R)
```

**Step 1 — term independence.** We assume the presence of one query term in a
document is independent of the presence of others. This is false (terms co-occur
systematically) and is called the "coordination level" assumption. It is what makes
the score computable in linear time, and every production IR system makes it.

**Step 2 — turn the product into a sum, and find the IDF.** Consider the odds that a
term appears in a relevant document versus a non-relevant one. If nₜ of the N
documents contain term t, then

```
P(t | ¬R) ≈ nₜ / N
P(t | R)  ≈ (N − nₜ) / N
```

Their ratio is the information the term carries about relevance:

```
IDF(t) = log [ (N − nₜ) / nₜ ]
```

Because the terms are independent, the log of the product of likelihood ratios is
the *sum* of the log ratios. Taking logs converts products to sums:

```
log P(D | R, Q) = Σ_{t ∈ Q} log [ P(t | R) / P(t | ¬R) ] = Σ_{t ∈ Q} IDF(t)
```

This is where IDF comes from. It is not a heuristic weighting — it is the log
likelihood ratio of the term appearing under relevance versus not.

**Step 3 — the +0.5 smoothing, and why IDF can be negative.** The raw ratio is
undefined when nₜ = N (the term is everywhere) and gives 0 when nₜ = N/2.
Robertson's smoothing

```
IDF(t) = log [ (N − nₜ + 0.5) / (nₜ + 0.5) ]
```

keeps the term finite, and the variant actually used in the code adds +1 inside
the logarithm:

```
IDF(t) = log [ (N − nₜ + 0.5) / (nₜ + 0.5) + 1 ]
```

which keeps IDF **non-negative** even for terms present in more than half the
corpus. Without it, a term like "safety" would *subtract* evidence.

**Step 4 — saturation.** The formula so far assumes relevance depends only on
*whether* a term appears, not how often. That is wrong: the tenth occurrence of
"incoterm" is far less informative than the first. Robertson and Zaragoza (2009)
replace the raw count f(t,D) with

```
f(t,D) · (k₁ + 1)
─────────────────────────────
f(t,D) + k₁ · (1 − b + b · |D|/avgdl)
```

**Why this saturates.** As f → ∞ the fraction tends to (k₁+1), a constant. So the
contribution of a term stops growing. `k₁` controls the speed: k₁ = 0 recovers the
binary present/absent model; k₁ → ∞ recovers linear TF with no saturation at all.
The default **k₁ = 1.2** is the value Robertson et al. tuned and that Lucene has
shipped since 8.x.

**Step 5 — length normalisation.** The denominator contains (1 − b + b·|D|/avgdl).
At b = 0 document length is ignored entirely. At b = 1, a document of exactly
average length gets denominator k₁, one twice as long gets 2k₁, one half as long
gets 0.5k₁. A long document must therefore work harder to earn the same score,
which counteracts the fact that long documents match more terms by accident.
**b = 0.75** is the standard default — nearly full normalisation, but not so
aggressive that short, precise documents are penalised.

**The formula.**

```
              ⎛      f(t,D)(k₁ + 1)        ⎞
BM25(q,D) = Σ  ⎜ IDF(t) · ───────────────── ⎟
   t∈Q      ⎝  f(t,D) + k₁(1 − b + b|D|/avgdl) ⎠
```

**What BM25 does not contain:** term position, proximity, stemming, or any
query-term weighting other than through IDF.

**Worked example.** Corpus of N = 100 documents. Term "incoterm" appears in
nₜ = 5. Then

```
IDF = log[ (100 − 5 + 0.5)/(5 + 0.5) + 1 ] = log[95.5/5.5 + 1] = log[18.36] ≈ 2.91
```

A document of 500 words in a corpus averaging 400 words, containing "incoterm"
3 times:

```
normaliser = 1.2 · (1 − 0.75 + 0.75 · 500/400)
           = 1.2 · (0.25 + 0.9375)
           = 1.2 · 1.1875 = 1.425
contribution = 2.91 · (3 · 2.2)/(3 + 1.425) = 2.91 · 6.6/4.425 = 2.91 · 1.492 = 4.34
```

The same term appearing once in an average-length document contributes
2.91 · (1·2.2)/(1 + 1.2) = 2.91 · 1.0 = 2.91. **Three occurrences score only 1.5×
one occurrence** — that is the saturation, and it is why BM25 does not simply
reward repetition.

**What breaks.** The independence assumption; the assumption that query terms are
equally likely under relevance and non-relevance except through their frequency;
and the stationarity assumption baked into a single global IDF, which is why BM25
degrades on corpora where "relevant" varies by sub-topic — precisely the situation
in a twelve-category industrial corpus.

## C.3 The dense leg, and the encoder that was wrong for it

**What the dense leg is.** A bi-encoder embeds the query and each passage
*independently* and compares the two vectors. That is what makes a document
index possible — but it is also where the difficulty lives: the encoder has to
guess, from each side alone, that a question and a passage are related.

**The first choice was wrong for the job.** The original encoder,
`sentence-transformers/all-MiniLM-L6-v2`, is a *general-purpose sentence encoder* trained with a
symmetric similarity objective: it is trained to place two sentences that mean
the same thing near each other. Retrieval is asymmetric. A passage does not
*resemble* a question; it *answers* it. On this corpus the mismatch was
measurable rather than theoretical: dense-only retrieval reached Recall@10 0.636 against plain BM25's 0.970 (paired Wilcoxon,
p = 9.1e-04), and the fused system's ordering was *worse* than the
lexical leg's — nDCG@10 0.722 against 0.798. The
fusion was paying for the dense leg's slots and getting nothing back. BEIR's
main results table reports the same effect at scale: across its 18 datasets,
zero-shot DPR scores 0.234 against BM25's 0.413, a 43% relative deficit.

**The change, and one detail that is easy to get wrong.** The encoder is now
`BAAI/bge-m3`, a retrieval-trained multilingual model: 1024
dimensions, CLS pooling, a normalisation module, and a long-document training
strategy that handles the query/passages asymmetry in training rather than in
the prompt. **BGE-M3 takes no query instruction.** The smaller
instruction-tuned encoders (E5, GTE, BGE-v1.5) want "Represent this sentence for
searching relevant passages: " in front of the query; BGE-M3's model card says
explicitly that it "no longer requires adding instructions to the queries".
The configuration therefore leaves `query_prefix` empty — and keeps the field
configurable, because the next encoder may well want one.

**What changed.** The gap between the dense leg and the lexical leg closed by more than half; and the fused system now **orders better** than the lexical leg alone, which it did not before. Dense-only retrieval now reaches
Recall@10 0.812 against BM25's 0.969, and the fused system reaches 1.000 with nDCG@10 0.847 against BM25's 0.792.

**The generalisable lesson.** A hybrid retriever is only as good as its worse
leg, and "hybrid" is not a free upgrade: giving a weak leg half the say in the
ranking costs the strong leg's ordering. If the dense leg is not
retrieval-trained, it should not be in the fusion at all — and the way to find
out is to measure the two legs separately, which is what the ablation does.

## C.4 Reciprocal Rank Fusion, derived

**The problem.** We have two ranked lists, R₁ (dense) and R₂ (lexical), and want
one ranking.

**Why adding scores fails.** The two retrievers produce scores on incomparable
scales: BM25 scores are unbounded sums of IDF-weighted counts; cosine similarity
lives in [−1, 1]; cross-encoder logits are unbounded and arbitrarily shifted.
There is no principled way to add them, and any weighting fitted on one corpus
breaks on the next.

**The insight.** Cormack, Clarke and Büttcher (2009) observed that the only
quantity every retriever agrees on is the **rank**, and rank is scale-free. So
ignore scores, use positions.

**Definition.** For a document d, let rᵢ(d) be its 1-based rank in list i. Define

```
RRF(d) = Σ_{i} 1 / (k + rᵢ(d))
```

**Two properties fall out.**

*Parameter-free in the weights.* Every list contributes equally; there is no
per-retriever weight to tune. The constant k is not a weighting — it controls the
*shape* of the rank discount. Cormack et al. report it is insensitive for k > 10;
the de-facto default is **k = 60**.

*Why k damps the top.* The discount 1/(k+r) ≈ 1/k for r ≪ k. At k = 60:

```
rank 1  →  1/61 = 0.01639
rank 10 →  1/70 = 0.01429      (a 13% difference)
rank 20 →  1/80 = 0.01250
```

So the top ten ranks are nearly *equally* discounted. What decides the fused order
is **agreement**: a document ranked 1 by both retrievers accumulates 2 × 0.01639 =
0.03278, roughly double a document ranked 1 by one retriever and absent from the
other. Fusion rewards documents two independent retrievers both like.

**Worked example.** Query: *"what is the economic order quantity for SKU A-104"*.

| Chunk | BM25 rank | Dense rank | BM25 contribution | Dense contribution | RRF total | Fused rank |
|---|---|---|---|---|---|---|
| C1 — "EOQ formula and A-104 policy" | 1 | 3 | 1/61 = 0.01639 | 1/63 = 0.01587 | 0.03226 | **1** |
| C2 — "A-104 reorder point, safety stock" | 4 | 1 | 1/64 = 0.01563 | 1/61 = 0.01639 | 0.03202 | **2** |
| C3 — "SKU catalogue listing" | 2 | 18 | 1/62 = 0.01613 | 1/78 = 0.01282 | 0.02895 | 3 |
| C4 — "Unrelated: dumper haulage cost" | 9 | 6 | 1/69 = 0.01449 | 1/66 = 0.01515 | 0.02964 | 3 |

(C3 and C4 show the point: C4 was ranked 6th by dense, but BM25 gave it nothing, so
it falls below C3 which was strong on both.)

**What RRF gives up.** Score *magnitude*. A reranker wildly confident about its top
hit gets no more credit than one barely sure. This is why the cross-encoder is
applied *after* fusion rather than folded into it.

**The competing alternative.** CombSUM (Fox & Shaw, 1994) sums *normalised scores*
with learned weights. Bruch et al. (2023, *ACM TOIS*, DOI 10.1145/3596512) compared
them across 23 runs and found RRF at least as good and far more robust, because
CombSUM's weights are sensitive to the score distribution. The trade-off: CombSUM
can exploit score *margins* (a top hit at 0.99 versus a rest at 0.2 is
informative; RRF cannot see that). Their results also show tuned RRF does **not**
generalise out-of-domain — which is an argument *for* using untuned k = 60 when the
deployment corpus is unseen, not an argument against it.

## C.5 Cross-encoder reranking

A cross-encoder reads the pair jointly:

```
score(q, d) = wᵀ · Transformer([CLS] q [SEP] d [SEP])[CLS]
```

so every token of the document attends to every token of the query. Strictly more
expressive than a bi-encoder. Strictly more expensive: one forward pass per pair.

**The crucial consequence.** The score is a **logit**, not a probability. Its
distribution shifts with query difficulty and with the number of candidates. A
score of 3.0 might mean "certainly relevant" for one query and "borderline" for
another. **Thresholding it directly is a category error** — which is exactly why
D1 calibrates it before thresholding.

**What our experiment showed.** On the six-category corpus, reranking with a
**top-50 candidate pool** moved recall@10 by +0.000 (p = 1.0 × 10⁰)
— indistinguishable from zero — while its effect on MRR was
+0.111 (p = 9.3 × 10⁻⁴) and on nDCG@10 +0.085
(p = 1.8 × 10⁻³). **The reranker buys ordering, not recall.** That is
exactly what the mechanism predicts: it can only permute the chunks it is
given, so it cannot bring in evidence the first stage discarded, and it cannot
push a relevant chunk that was never in the pool into the top ten.

On the focus domain, with only 32 answerable questions,
even the ordering difference falls below significance: recall@10 went from 1.000 to 0.969 (p = 3.2 × 10⁻¹), MRR from 0.798 to 0.795 and
nDCG@10 from 0.847 to 0.836. **The effect is a property of the
corpus size as much as of the mechanism.** Experiment 5 sweeps the pool size
and shows the shape of the effect.

A caution about reading the recall column on its own. Our benchmark is
silver-standard — a question derived from a chunk contains that chunk's own
words — so the plain lexical retriever already finds the gold chunk most of the
time and Recall@10 is close to its ceiling for every system. The ordering
metrics are where the systems differ, and they are the ones to read.

**Why the pool size decides it.** A cross-encoder can only reorder the candidates
it is given. It has no opinion about the 40 chunks that were never shown to it.
Give it a pool the size of the final context and the best it can do is permute
those ten — it cannot bring in the relevant chunk sitting at fused rank 34, and
it can only lose the relevant one sitting at rank 12. Give it a larger pool and
it has room to promote chunks the first stage ranked below the cut — but the
room is not free: every extra candidate is also a chance to promote a
distractor into the same ten slots. That is why the measured curve peaks
rather than saturates, and why the useful pool is about the size of the
context it feeds rather than an order of magnitude larger.

**The pool size is therefore a first-class parameter, not a tuning detail.** It
is also the most likely explanation of the −5.34 percentage-point reranker
regression reported in the September 2026 project report on a different corpus:
a rerank pool too small relative to the final context. We do not have their
code, so we state this as a **hypothesis with a cheap test** — measure the pool
size against the final context size — rather than as an explanation. Experiment 5
sweeps the pool size directly to show the shape of the effect.

**Why this matters beyond our corpus.** The September 2026 project report records
a **−5.34 percentage-point** reranker regression on `production_scheduling`, on a
different corpus. Our result supplies a candidate mechanism for it: a rerank pool
too small relative to the final context. That is a hypothesis, not a proven
explanation — we do not have their code, and their reranker may also be
domain-mismatched. But it converts an unexplained anomaly into a testable
configuration check, and the check is cheap: measure the rerank pool size against
the final context size.

**The lesson.** A reranker is a *pool-relative* device. Its effect on recall is
governed by how many candidates it sees relative to how many you keep. Its
ordering benefit is real and large (MRR 0.798 → 0.795), and ordering is what
matters for a generative system, because LLMs attend most strongly to early
context. This is also why the gate should sit *after* the reranker, where the
best-evidence ordering is already established.

## C.6 The Bayesian posterior gate, derived

**The question.** Given a retrieval score, what is the probability that the chunk
is relevant to this query?

**Bayes' theorem.**

```
P(R | d) = P(d | R) · P(R) / P(d)
```

Dividing numerator and denominator by P(d | ¬R) gives the odds form, which is the
one to actually use:

```
                P(R)     P(d | R)
P(R | d) = ───────────── · ─────────────
              P(d | ¬R)   P(d | ¬R)
          └──┬──┘   └────┬────┘
        prior odds      likelihood ratio
                      (the Bayes factor)
```

**Interpretation.** The posterior is the prior odds multiplied by how surprising the
evidence is. A likelihood ratio of 1 (the evidence is equally likely either way)
changes nothing.

**The tractable model.** For a single scalar feature x (the reranker score), use a
logistic model on the log-odds scale:

```
log [ P(R|d) / P(¬R|d) ] = β₀ + β₁·x
```

so

```
P(R | d) = σ(β₀ + β₁·x) = 1 / (1 + exp(−(β₀ + β₁·x)))
```

This is Platt scaling's form, and it is exactly what the September 2026 report used
(β₀ = 2.943, β₁ = 1.680 on a 30-query calibration set).

**Reading the coefficients.**
- At x = 0 the prior odds are exp(2.943) ≈ **19 : 1** in favour of relevance.
- One unit of reranker score multiplies the odds by exp(1.680) ≈ **5.4×**.

**Fitting β by maximum likelihood.** The log-loss is

```
L(β) = − [ Σ yᵢ log σ(β₀ + β₁xᵢ) + Σ (1−yᵢ) log(1 − σ(β₀ + β₁xᵢ)) ]
```

which is convex in (β₀, β₁), so Newton's method converges reliably. The gradient is
the score function

```
∂L/∂β₀ = Σ (σ(zᵢ) − yᵢ)
∂L/∂β₁ = Σ (σ(zᵢ) − yᵢ)·xᵢ
```

and the Hessian is

```
∂²L/∂β₀² = Σ pᵢ(1−pᵢ)
∂²L/∂β₀∂β₁ = Σ pᵢ(1−pᵢ)xᵢ
∂²L/∂β₁² = Σ pᵢ(1−pᵢ)xᵢ²       with pᵢ = σ(zᵢ)
```

A small ridge term is added for numerical stability when the score has near-zero
variance, which would otherwise make the design matrix singular.

**Why calibration is not optional.** Thresholding a raw logit at "0" is meaningless:
the logit at which a chunk is relevant depends on the query, on the retriever, and
on the corpus. Platt scaling converts a *ranking signal* into a *probability that
can be thresholded at a stated operating point*.

**Measuring the calibration.**

*Brier score* = mean squared error between predicted probability and the binary
label. It decomposes into calibration error and refinement error — a model can have
a good Brier score while being poorly calibrated, if its predictions are bimodal.

*Expected Calibration Error*:

```
ECE = Σ_b (n_b / N) · |acc_b − conf_b|
```

over equal-width probability bins: the sample-weighted mean gap between confidence
and empirical accuracy. ECE = 0 means that among the predictions assigned 0.8
confidence, 80% were correct.

*Reliability diagram*: accuracy versus confidence per bin, against the diagonal.

*Risk–coverage curve*: sort by confidence, keep the top fraction f, and record the
error rate among them. This is the operational question the gate exists to answer:
**at what coverage is the system 95% correct?**

**What breaks.** The exchangeability assumption behind any finite-sample guarantee.
Geißler et al. (2026, arXiv:2605.05244) apply conformal prediction to exactly this
problem and concede that "the associated statistical guarantees do not hold
generally, since the assumption of sample exchangeability depends on the retriever
setup". A 634-chunk single-category corpus is exactly such a setup. **We therefore
claim empirical calibration on a held-out query set, not a statistical guarantee.**

## C.7 The gate as control flow

The gate is a branch, not an instruction.

```
P_sufficient = calibrate(features of the retrieved set)   # query level

if P_sufficient < τ:
    return NO_EVIDENCE_RESPONSE          # the LLM is never called
else:
    context = accepted chunks
    answer = generate(context)           # and every claim is tagged
```

**A subtlety that matters more than the threshold: the gate is a QUERY-level
decision, not a chunk-level one.** An earlier version of this implementation
calibrated at the chunk level: for every (query, candidate) pair it asked "is
this candidate the gold chunk?" and fitted a logistic map from the reranker
score to that label. That is the wrong question, and it produced a confidently
wrong result — with about fifty candidates per query and one gold chunk, the
base rate of positives is roughly 2%, so a classifier that answers "nothing is
relevant" is right 98% of the time. Maximum-likelihood fitting duly returned a
large **negative** intercept (β₀ = −2.88) and a nearly flat slope (β₁ = 0.27),
the Brier score and ECE looked *excellent* because they were measuring the base
rate, and the resulting operating point refused 46% of the answerable
questions.

The gate does not decide "is this candidate the gold chunk". It decides **"does
this retrieved context contain the answer to the question at all"**. So the
calibration must be at the level of the query:

```
feature vector  →  P(the retrieved context contains the answer)
```

The label is 1 when the context contains a gold chunk — which covers both an
answerable question whose evidence the retriever found *and* an answerable
question whose evidence it missed. In both of those cases the correct behaviour
is to refuse.

**What the gate cannot decide, and the measurement that shows it.** That
sentence needs one correction, and the correction is the most instructive
result in this project. The label is *answer-in-context detectability*. It is
not the same question as "does this context state the answer". When a question
is answerable and the retriever found its evidence, the two agree. When a
question is answerable and the retriever missed it, they agree too — refusing
is the right behaviour. But there is a third case, and it is the case a refusal
benchmark exists to probe: the question is **not answerable from this corpus
at all**, and yet the retriever returns on-topic passages, so every retrieval
feature looks healthy. A detectability gate has nothing to detect there.

Experiment 12 measures how large that gap is. On a benchmark whose unanswerable
class asked about a fabricated identifier, the gate refused 91.7% of that class — but so would any system that
refused on the *shape* of the question, so the number measured the benchmark
rather than the gate. On the repaired class, whose questions the corpus
discusses but for which it states no value, the gate refuses 23.6% (26 of 110) of the hard stratum,
against 76.5% (26 of 34) for questions that
are simply off-topic. Detection survives where the question is off-topic and
largely disappears where it is on-topic but unanswered.

That is the difference between *recognising* an unanswerable question and
*refusing* on absent evidence, and it is the difference between a gate that
looks effective and a gate that is. The features are five signals of the retrieved set, all available
before any generation happens:

| Feature | What it measures |
|---|---|
| `top1_rerank` | the top cross-encoder score |
| `mean_top3_rerank` | the mean of the top three scores |
| `top1_bm25` | the best lexical score |
| `max_rrf` | the best fused score |
| `n_candidates_above_bar` | how many candidates cleared a low relevance bar |

This is the same distinction SQuAD 2.0 makes, and it is the difference between a
gate that works and a gate that looks calibrated because it is measuring the
wrong thing. **It is also the exact trap that the 2026 literature warns about
when it says that query-time filters can measure benchmark construction rather
than filtering** — the label you choose determines what you are measuring.

Three properties that an instruction cannot have:

1. **The model cannot talk its way past it.** There is no prompt text, no
   "ignore previous instructions", no output the model produces that reaches the
   gate. The decision is made on a calibrated number computed before generation.
2. **The refusal is auditable.** "The gate refused because the maximum calibrated
   relevance probability was 0.312 against a threshold of 0.50" is a sentence an
   auditor can check. "The model seemed unsure" is not.
3. **It is portable without retraining.** Self-RAG's reflection tokens (Asai et
   al., ICLR 2024) are *learned* on a training distribution. Moving to a new
   industrial category would require repeating the fine-tuning for each of the
   six categories in the public corpus -- twelve in the original
   project corpus. A threshold on a calibrated score does not. **The
   *calibration* is a separate matter, and it is not portable:** the threshold
   is a fitted parameter, and it is re-fitted per corpus and per retriever
   (L10), which is measured rather than assumed.

**The nearest prior work, and the honest difference.** CRAG (Yan et al., 2024,
arXiv:2401.15884) inserts a retrieval evaluator that returns a confidence degree
and triggers one of four corrective actions — use the documents, web-search,
decompose-and-recompose, or combine. **CRAG still calls the LLM in every branch.**
The difference is one of design philosophy under the same goal:

| | CRAG | This gate |
|---|---|---|
| Low confidence ⇒ | improve the evidence and continue | **decline and return "no evidence"** |
| Placement | inside the generation path | before it; the call can be skipped |
| Inference dependency | web search may be required | none; local computation |
| Auditable reason | a degree | a probability against a stated threshold |

Neither is better in general. Refining-and-continuing is the right choice when the
corpus is incomplete and web search is available; refusing is the right choice when
the corpus is a fixed, closed set of controlled documents and a wrong answer is
more costly than no answer. **That is the situation in industrial decision support,
and saying so precisely is the whole argument.**

## C.8 Modality quota — and where it belongs in the pipeline

**The observation.** In an industrial corpus the binding requirement usually sits in
a table: an economic order quantity, a safety-stock rule, an acceptance tolerance,
an Incoterms matrix. In prose, the same fact is *described* but not *specified*.

**The mechanism.** A floor on the share of the final context occupied by tables and
charts:

```
min_table_share = 0.15   →  at least 2 of 10 chunks are tables
min_chart_share = 0.05   →  at least 1 of 10 chunks is a chart
```

**The algorithm matters more than the threshold.** There are two ways to implement a
floor, and they behave completely differently:

*Rebuild-based.* Walk the ranking, skip anything that would breach a floor, and
backfill. This silently **removes** good high-ranked items and replaces them with
lower-ranked ones. Our first implementation did this, and table recall fell from
**0.906 to 0.469** — the quota made the system actively worse. (Those are
historical figures from the development corpus, recorded in
`research/17_historical_figures.md`; they are not the focus domain's numbers,
where the table recall is already 1.000 without any quota at all.)

*Swap-based (correct).* Take the natural top-10 untouched. While a floor is unmet,
swap the **lowest-ranked** item of the over-represented modality for the
**highest-ranked** available item of the under-represented modality. The context
degrades by the smallest possible amount and the ranking of everything kept is
preserved.

**The pipeline position matters even more.** This was the most surprising finding
of the whole implementation.

*Pre-rerank quota* (the placement the system ships): the quota proposes
a **membership** for the final ten — the cross-encoder then re-scores those ten
and can reorder them, but it cannot change *which* ten they are, so the forced
table chunk survives. **The quota binds.**

*Post-rerank quota* (the placement the system was built with until 16 November
2026, and the one the September 2026 report used): the reranker ranks
first and chooses the final ten itself, and the quota then adjusts that
*final* context by swapping one of them for a table chunk the cross-encoder
already ranked **below** the cut. It tends to import the wrong table chunk and
to displace a good one, and it is working against a veto it cannot appeal.

The two bullets above are the account the measurement supports. The account
that motivated the design was the opposite one — that a quota applied early
merely removes good candidates and a quota applied late binds cheaply — and
it was right about the mechanism and wrong about the conclusion, which is why
both are worth keeping.

**The measured consequence inverts the rule the framework was designed
on.** The quota belongs **before** the cross-encoder, not after it — on the
focus domain and on the six-category corpus. On the focus domain, where table
recall is already 1.000 without any quota at all, the quota's whole effect
falls on overall recall: applied before the reranker it moves it by
+0.031, and applied after the reranker by -0.031.
On the six-category corpus, where the reranker takes table recall from 0.964 to 0.929, the quota applied before the reranker restores
it to 1.000, while the same quota applied after it reaches only 0.929.

**The rule does not hold on every corpus, and no difference is
significant.** On the industrial corpus the ordering reverses: the quota
after the reranker is the better placement there, by a small margin.
None of these differences is statistically significant at the 0.05 level (p = 0.157, 0.480, 0.317 respectively). The correct statement is therefore not "the
quota always belongs before the cross-encoder" but "the quota belongs before
the cross-encoder on the corpora the thesis measures it on, the effect is
small, and its direction is corpus-dependent".

**Which placement the shipped system uses.** The system applies the quota
**before the cross-encoder**, which is the placement the ablation ranks
first on the focus domain — the domain the thesis is about, and the largest
of the three differences the ablation measures. It was built the other way
round — the September 2026 design put the quota after the reranker — and it
stayed that way until 16 November 2026, because changing it invalidates the
gate's calibration, the generator-side comparison and the per-claim results
together, and the defence was three days away. On that date the default was
moved and the measurements that depend on the retrieval were re-taken with it, apart from the per-claim band evaluation against the gold evidence, the per-claim band evaluation against the retrieved evidence and the industrial corpus's per-claim band replication, whose labels come from a panel of reader agents under a written protocol and could not be reproduced. On the focus domain the pre-rerank quota
moves overall recall by
+0.031, against -0.031 for the placement it
replaced, and on the six-category corpus it reaches overall recall 0.939 and table recall 1.000, against 0.924 and 0.929 for the other one.


**Why, which is not obvious.** It is about what each stage can and cannot
undo. A pre-rerank quota proposes a *membership* for the final ten; the
cross-encoder then re-scores those ten and can reorder them, but it cannot
change which ten they are, so a forced table chunk survives. A post-rerank
quota starts from the reranked ten and swaps one of them for a table chunk the
cross-encoder already ranked **below** the cut — so it tends to import the
wrong table chunk and to displace a good one. The quota applied later is
working against a veto it cannot appeal.

**The generalisable rule, corrected:** *a constraint on a downstream artefact
should be enforced where it can still choose the candidates, not where it must
work against another component's judgement.* Enforcing a constraint downstream
of a scorer means importing candidates the scorer has already rejected. This
project arrived at the rule by measuring the opposite of what it expected,
which is the more convincing way to arrive at one.

**A bug this finding exposed.** The first implementation of the swap had its
victim-selection condition inverted: it evicted the modalities that were *at*
their floor and spared the ones with a surplus. The symptom was that the quota
made table recall *worse* — 0.906 collapsing to 0.469 — which looked like a
substantive negative result about modality balancing rather than a one-character
logic error. The regression test that now pins this down lives in
`impl/tests/test_hybrid.py`, and the general lesson is worth stating on its own:
**a result that contradicts the mechanism you believe is a bug report, not a
finding.** The pipeline-position effect was real and survived the fix; the
collapse did not.

**Why the effect is small on a text-heavy corpus.** The September 2026 report's
corpus was 2.3% chart and 7.1% table; our corpus is 5.2% chart and 6.0% table.
With so few tables, a quota of two tables draws on tables deep in the ranking —
tables that are *less* likely to be relevant — and displaces relevant prose to do
it. So the modality benefit is real but bounded, and the cost is what pipeline
position decides. Two remedies for a stronger result: (i) stratify the corpus so
that the modalities are adequately represented, and (ii) report a pre-registered
power analysis. The framework measures and reports the modality composition of
the corpus for exactly this reason — it predicts how large D2 can possibly be.

## C.9 Per-claim confidence: noisy-OR, entropy, information gain

**Decomposition.** An *atomic claim* is a statement that can be true or false on
its own. We use sentence-level decomposition with a split at discourse markers
(semicolon, "however", "but", "whereas"), with a numeric-clause split. Full claim
decomposition (Chen et al., 2024; Fabbri et al., 2022) uses an LLM and is more
precise, but it introduces a second generation step whose errors propagate into
the confidence numbers — and the point of D5 is to give the practitioner a
*reliable* signal.

**Combining the witnesses.** Each retrieved chunk cᵢ is an independent, fallible
witness; the NLI model gives eᵢ = P(cᵢ entails the claim). The standard model for
combining several independent witness events is the **noisy-OR** (Pearl, 1988):
the claim is supported if at least one witness covers it, and each witness
independently fails with probability (1 − eᵢ).

```
P(supported) = 1 − Πᵢ (1 − eᵢ)
```

**Derivation.** Define Sᵢ = "witness i succeeds", i.e. it entails the claim. Then

```
P(no witness succeeds) = P(∩ ¬Sᵢ) = Π P(¬Sᵢ) = Π (1 − eᵢ)
```

by independence, and the complement is the formula. The noisy-OR is a special case
of the Bayesian-network "noisy-OR" gate (Pearl, 1986), in which child nodes can be
activated by any single parent.

**The properties we need.** One highly confident chunk (e = 0.95) supports the
claim regardless of the others. Ten weak chunks accumulate:
1 − 0.9¹⁰ = 0.65. And a single strongly *contradicting* chunk caps the claim,
because we take the **max** of the entailment scores rather than the mean —
averaging would let nine irrelevant chunks dilute one chunk that says the
opposite.

**Information gain.** How much did the retrieved set reduce our uncertainty?

```
I(X; Y) = H(Y) − H(Y | X)
```

Y is the binary event "the claim is supported by the evidence"; X is the retrieved
set. With a Bernoulli posterior q and prior H(Y):

```
H(q) = −q log₂ q − (1−q) log₂(1−q)
IG   = H(prior) − H(q)      bits
```

With an uninformative prior (H = 1 bit), IG = 1 − H(q). Reading: IG = 1 bit means
the evidence left no doubt (q = 1); IG = 0 means it told us nothing (q = 0.5).

**A necessary clarification that the September 2026 report's one-line description
conflates.** IG is *symmetric* about q = 0.5: a claim with q = 0.9 and a claim with
q = 0.1 both give IG = 1 − H(0.9) = 0.531 bits. That is correct behaviour for an
information measure — both are confident states — but it means IG alone cannot
distinguish "well supported" from "well refuted". **So: the confidence band is cut
on q, and IG is reported alongside as the separate "how much did the evidence
reduce uncertainty" figure.** The two answer different questions, and using one for
both is a category error.

**The bands.**

```
q ≥ 0.80   →  grounded     the evidence entails it
q ≥ 0.45   →  inferred     partial support, plausible extension
otherwise  →  uncertain    the evidence does not settle it
```

A claim whose best chunk actively contradicts it is additionally marked
*contradicted*, and its citation points at the contradicting passage, so the
practitioner sees the disagreement rather than a silent low-confidence tag.

## C.10 NLI + topical gate, and the base-rate trap

**Why NLI alone produces false positives.** NLI models are trained on
premise/hypothesis pairs where the two texts are *about the same thing*. Feed them
two passages about different sub-topics — "the safety stock rule for the Kharagpur
plant" versus "the lead time for the Chennai vendor" — and the model must produce
a label anyway. It often produces *contradiction*, because the two texts assert
different things, even though nothing is actually in conflict.

**A measured demonstration.** Here is what our NLI model
(`cross-encoder/nli-deberta-v3-small`) actually outputs on three pairs drawn
from the industrial register of this project:

| Premise | Hypothesis | P(entail) | P(neutral) | P(contra) | Reading |
|---|---|---|---|---|---|
| "The safety stock for plant A is 187 units." | "The safety stock for plant A is 95 units." | 0.000 | 0.001 | **0.999** | A true contradiction. Correct. |
| "The EOQ for SKU A-104 is 250 units." | "The EOQ for SKU A-104 is 250 units." | **0.987** | 0.011 | 0.002 | Entailment. Correct. |
| "Lead time from Chennai vendor is 14 days." | "Safety stock policy uses 2 months of demand." | 0.001 | 0.445 | **0.555** | **Not a contradiction at all** — different sub-topics. And the NLI model says 0.555. |

The third row is the whole design in one line. Two passages that are about
completely different things — a vendor lead time and a stock policy — receive a
0.555 contradiction probability from a model that was never asked to abstain.
Nothing is wrong with these passages; the model simply had to answer a question
it was not equipped to answer. The topical gate exists to catch exactly this,
and it is the *conjunction*, not a tighter threshold, that catches it.

**The conjunction.** Two independent gates must agree:

```
flag(A, B) = contradiction(A, B)  AND  same_subject(A, B)
```

**same_subject** uses two orthogonal signals:

1. *Embedding similarity*: cos(e_A, e_B) ≥ τ_topic (default 0.55). Two passages
   that are semantically close are about the same thing.
2. *Entity/number overlap*: Jaccard overlap of the concrete identifiers — part
   numbers, plant codes, standard references, quantities — must be ≥ 0.10. Two
   passages with high semantic similarity but zero shared entities are almost
   always about different things that happen to be phrased similarly.

```
J(A, B) = |A ∩ B| / |A ∪ B|
```

**Why a conjunction and not a tuned threshold.** Raising the NLI threshold alone
reduces false positives only by also excluding genuine conflicts — both errors fall
together. Adding an *independent, orthogonal* signal lets the two error types be
traded off separately. The entity gate in particular catches the failure mode that
motivates the whole design.

**A third signal: numeric conflict.** Two passages that attach different values to
the same quantity (EOQ = 250 versus EOQ = 400) conflict explicitly, even when the
NLI model is lukewarm, because the contradiction is in the numbers.

**The revision/supersession check.** ContextConflict (EMNLP 2026,
DOI 10.18653/2026.emnlp-main.918) identifies six conflict types — factual,
inferential, temporal, granularity, perspective, ambiguity — of which only two are
genuine contradictions. The most common false positive in industrial documentation
is **temporal supersession**: "Rev 3 sets EOQ at 187 units" and "Rev 4 sets EOQ at
95 units" are *both true*, because Rev 4 replaced Rev 3. Reporting that as a
contradiction is wrong in exactly the way that matters. We therefore check for
explicit revision markers before flagging, and suppress the flag when the two
passages are different revisions of the same document.

**The base-rate trap — the most important methodological point in this section.**
Any false-positive rate must be reported with the prevalence, or it is
uninterpretable. At 1% prevalence, a detector with 50% recall and 99% specificity
still has a 98% false-positive rate — and that number says more about prevalence
than about the detector. This is why §E reports the **always-flag** and **never-flag**
baselines alongside the measured rates. A detector that flags everything has 100%
recall and 0% precision; one that flags nothing has 0% recall and 100% precision. Any
claimed improvement must beat both.

## C.11 The evaluation metrics, derived

**nDCG@k.** Let relᵢ be the graded relevance of the i-th retrieved item (0 if not
relevant; 1 if relevant; 3 if it is a "critical" passage such as the table carrying
a binding requirement).

```
DCG@k  = Σ_{i=1..k} (2^relᵢ − 1) / log₂(i + 1)
IDCG@k = DCG@k computed on the ideal ordering (most relevant first)
nDCG@k = DCG@k / IDCG@k
```

*Why the exponential gain 2^rel − 1?* It makes the jump from relevance 0 to 1 worth
more than the jump from 1 to 2, so that retrieving *something* relevant at all
dominates retrieving a marginally-more-relevant item lower down.

*Why log₂(i+1) in the denominator?* It is a position discount, analogous to BM25's
length normalisation: being at position 1 is worth much more than being at position 10. The log is the standard choice because it is gentle at first and steep later.

*Why normalise?* Queries differ in how many relevant documents exist. Dividing by
the ideal DCG makes the score comparable across queries, and it lies in [0, 1].

**Cohen's kappa.**

```
κ = (P_o − P_e) / (1 − P_e)
```

P_o is observed agreement; P_e is agreement expected by chance from the two
raters' own marginal distributions. *Why not raw agreement?* Raw agreement is
inflated when most items fall in one dominant category: two raters who both always
say "easy" agree 90% of the time while agreeing on nothing that required
judgement. The large-sample standard error is

```
SE(κ) = √[ P_o(1 − P_o) / (N(1 − P_e)) ]
```

and the 95% CI is κ ± 1.96·SE.

**McNemar's test.** Build the 2×2 table of discordant pairs:

```
             B correct   B wrong
  A correct      b           c
  A wrong        d           e
```

Under the null, b and d are exchangeable and b + d ~ Binomial(n_discordant, 0.5).
The exact binomial test is the standard choice; the chi-square approximation
requires n_discordant ≥ 25.

**Wilcoxon signed-rank.** Rank the absolute paired differences, sum the ranks for
positive and negative differences separately, and test the imbalance. Zero
differences are discarded. The effect size is Cohen's d_z = mean(diff)/sd(diff);
the matched-pairs non-parametric counterpart is the Wilcoxon rank-biserial
correlation.

**Which test, when.**

| Situation | Test | Effect size |
|---|---|---|
| Two raters, nominal labels | Cohen's κ with CI | κ |
| Two systems, same queries, binary outcome | McNemar (exact) | difference in proportion |
| Two systems, same queries, continuous outcome | Wilcoxon signed-rank | Cohen's d_z / Cliff's δ |
| A mean with uncertainty | Bootstrap percentile CI | — |

**Why not a t-test on the primary comparison.** Per-query faithfulness scores are
bounded in [0, 1] and their distribution is left-skewed with a spike at 1.0 (most
queries *are* answered faithfully). The normality assumption of the t-test is
violated on the paired *differences*, so the Wilcoxon signed-rank test is the safe
default.

**What N supports.** With N = 276 queries, a paired test can detect a difference of
roughly 0.06 in a per-query proportion at 80% power (McNemar's approximation with
a 25/75 discordance split). With N = 16 user-study participants, a within-subject
sign test can detect a 14/16 split at p ≈ 0.002 — but cannot detect anything
smaller, and cannot support a claim about *generalisation* to a wider population.
Those are different statements, and the report must not blur them.

---

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
# Part F — Where this work stands in the literature

This part is the one to study hardest before the presentation. The single most
important thing it establishes is that **most of what the framework does has
published prior art, and the honest contribution is narrower and more defensible
than the architecture alone would suggest.**

## F.0 The literature, by sub-literature

A map of the literatures this work draws on, what each of them established, what
each of them leaves open, and where this thesis sits inside it. F.1 then puts the
five design moves against the same body of work, and F.2 handles the papers a
committee member is most likely to raise one at a time.

Every paper named below was resolved against a live bibliographic service — the
arXiv Atom API, the ACL Anthology, OpenAlex, Crossref or the DBLP — and its
title, authors, year, venue and identifier were read back from the source record
rather than written from memory. The verification record for each sub-literature
is the corresponding file under `research/`, and anything that could not be
resolved is listed there as UNVERIFIED rather than cited as fact.

### F.0.1 Lexical and dense retrieval

**What the literature established.** BM25 is not a historical artefact: BEIR
(Thakur et al., arXiv:2104.08663) evaluated eighteen datasets and ten retrieval
systems and reported that "BM25 is a robust baseline", with re-ranking and
late-interaction models achieving the best zero-shot performance but at high
computational cost. That is the standard this project's retrieval is measured
against. MTEB (arXiv:2210.07316) established the evaluation protocol the
sentence-embedding field now uses.

**What it leaves open.** Which *encoder* to use. BEIR's statement is about
retrieval families, not about the sentence encoders inside the dense leg.

**Where this work sits.** It measured the encoder rather than the family, and the
result was the project's first substantive finding: with a general-purpose
sentence encoder the dense leg reached Recall@10 0.636 against plain
BM25's 0.970, and the *fused* system's ordering was **worse** than the
lexical leg's — the fusion was paying for the dense leg's slots and getting
nothing back. Swapping in a retrieval-trained encoder (BAAI/bge-m3) moved
the dense leg to 0.812 and the fusion to 1.000 against BM25's 0.969. So
the question "does hybrid retrieval beat BM25?" has a conditional answer: it
depends on which encoder is in the dense leg, and on neither corpus in this
project is the difference statistically significant (p = 3.2e-01 on the focus
corpus, p = 3.2 × 10⁻¹ on the six-category corpus). §C.3 works this through.

### F.0.2 Rank fusion and cross-encoder reranking

**What the literature established.** Reciprocal Rank Fusion is Cormack et al.
(SIGIR 2009): rank-only, parameter-free, and therefore robust when the two
lists' scores are not on the same scale. Bruch et al. (*ACM TOIS* 2023) compared
fusion functions systematically and showed the choice among learned functions is
worth a small, consistent amount over RRF. Single-model alternatives now exist:
M3-Embedding (arXiv:2402.03216) does dense, multi-vector and sparse retrieval
in one model, and is a direct alternative to a BM25 + dense + RRF stack.

**What it leaves open.** How large the reranker's candidate pool should be.
Reranking is usually reported as "we rerank the top-k", with k chosen once.

**Where this work sits.** This project's most actionable finding, and one the
literature does not state: **a reranker's recall is governed by the size of its
candidate pool**, and the curve is not monotone. Recall@10 goes from 0.902 at
a pool of 5 to 0.955 at a pool of 10 — the size of the final context — and
then *back down* to 0.932 at a pool of 100, with the knee at 10
and a gain of +0.053 over the endpoints. A pool larger than the context
cannot improve recall at all, since it can only permute the chunks it was
given; a pool past the knee adds distractors that compete for the same ten
slots. This is also the most likely explanation of the −5.34 pp reranker
regression reported in the September 2026 project report on a different corpus.

### F.0.3 Confidence, calibration and conformal prediction

**What the literature established.** That a retrieval-confidence threshold is a
sound idea and that it needs statistics. CRAG (Yan et al., 2024) makes the
retrieval decision on a confidence score; Yadkori et al. (2024) use conformal
prediction for abstention, which buys a coverage guarantee under an
exchangeability assumption; CalibRAG (NeurIPS 2025) addresses calibration at the
decision level; and Geißler et al. (arXiv:2605.05244) frame the whole thing for
industry with conformal chunk selection plus an attention-based factuality
classifier, reporting up to 6% answer-quality improvement and up to 77%
inconsistency detection — while conceding that "the associated statistical
guarantees do not hold generally, since the assumption of sample exchangeability
depends on the retriever setup."

**What it leaves open.** That the threshold is a *fitted parameter of the
deployment*, not a constant of the architecture. Phillips et al. (arXiv:2603.21172)
show entropy-based uncertainty has a model-dependent failure mode and that a
selective-prediction policy must be evaluated at a stated operating risk level.

**Where this work sits.** It follows both instructions: the gate is a calibrated
probability with a stated operating point τ = 0.05, evaluated as a
risk–coverage curve rather than as a single average rate (Brier 0.1510,
expected calibration error 0.1044), and it is re-fitted per retrieval
configuration. It also follows Geißler et al.'s own caveat as a limitation: the
negative class of this project's gate is dominated by *retrieval failure* rather
than by absence of evidence (0.0%), which
is exactly the regime where a threshold transferred from another retriever is
wrong. §C.6–C.7 derive the posterior; §E.2 measures it.

### F.0.4 Abstention and selective prediction

**What the literature established.** This is the most crowded sub-literature and
the one that most constrains the design. The established findings are:

* **CRAG** (2024) — retrieve, then *evaluate* the retrieved documents for
  relevance before generating, and correct when the evaluation fails.
* **DeclineCraft** (Thakur et al., arXiv:2610.28340) — a 2026 abstention
  benchmark with three findings that bear directly here: adding query rewriting
  and reranking to hybrid dense+sparse retrieval **lowers** the Correct
  Abstention Rate for all twelve models tested; iterative RAG lowers CAR versus
  single-shot in 30 of 40 configurations; and model scale does **not** buy
  abstention ability.
* **TAPS** (Zhang et al., arXiv:2610.16318) — decomposes abstention risk into
  *answering ability* and *distinguishing ability*, and compares at **matched
  coverage**; reports 1.5–9.4 pp lower mean risk than abstention training at
  matched coverage.
* **I-CALM** (Zong et al., arXiv:2604.03904) — a two-stage protocol in which the
  model first chooses to answer or abstain and is then **forced to give a best
  guess** for the abstentions, recovering the counterfactual answer so the
  abstention decision can be scored as a classifier; reports coverage, FAR,
  ECR, CAR and J_abs, and compares at matched coverage including explicit-IDK
  prompting, whose coverage collapses to 0.290 on one model and 0.002 on another.
* **UAEval4RAG** (Peng et al., ACL 2025) — six categories of unanswerable
  request, an Acceptable Ratio and an Unanswered Ratio combined into a Joint
  Score, and prompt restrictiveness as an explicit experimental factor.
* **HALT-RAG** (Goswami & Kurra, arXiv:2509.07475) — a **post-hoc verifier**:
  it operates on the source text and the generated output without performing
  retrieval itself, scores hallucination with an ensemble of two frozen NLI
  models plus lexical signals through a calibrated meta-classifier, and reports
  out-of-fold F1 on HaluEval under a precision-constrained abstention policy.
* **SYNCHECK** (Wu, Gu, Yin & Peng, EMNLP 2024, DOI 10.18653/v1/2024.emnlp-main.527)
  — monitors decoding dynamics to flag unfaithful sentences as they are
  generated; 0.85 AUROC over six long-form RAG tasks, and its FOD decoding
  **outperforms abstention by over 10%**.
* **The Selection Effect** (Tikhomirov & Savchenko, EMNLP 2026) and
  **Recognition–Refusal Misalignment** (Du & Hu, EMNLP 2026) — a gate forwards a
  conditional slice on which the downstream component may be no better than the
  baseline, and *recognising* impossibility and *routing* it to abstention are
  "nearly orthogonal".

**What it leaves open.** Almost everything about the *joint* question this thesis
asks: whether a code-level, non-bypassable gate changes what a generator says,
once the generator's own willingness to decline is controlled for.

**Where this work sits.** Two prompt conditions — a cautious instruction that
permits declining and an answering instruction that does not — run the same
five arms, so that the gate's marginal contribution can be separated from the
generator's. That is a simpler version of I-CALM's protocol, and TAPS's
matched-coverage requirement is the reason the arms are compared at a stated
operating point rather than by refusal count. The result is the framework's own
hypothesis H2.1: **supported under both prompt conditions** The hypothesis was tested under two prompt conditions that differ by a single sentence, with everything else -- the model, the questions, the retrieval, the scorer -- held fixed. Conditional: the hypothesis holds under both prompt conditions. Under the cautious prompt -- the deployed system -- it is supported, at a price: the gate reduced the rate of answering unanswerable questions from 0.535 to 0.417, a fall of 11.8 points, at the cost of answering 30 of 32 answerable questions. Paired question by question, the gate refused 23 of the questions the ungated arm answered and let through 6 of the ones it did not (exact McNemar p = 0.002). Under the answering prompt, which differs from the cautious one by a single sentence, it is supported, at a price: the gate reduced the rate of answering unanswerable questions from 0.938 to 0.528, a fall of 41.0 points, at the cost of answering 30 of 32 answerable questions. Paired question by question, the gate refused 60 of the questions the ungated arm answered and let through 1 of the ones it did not (exact McNemar p = < 0.001). What the framework claims is therefore that the gate reduces the rate of answering unanswerable questions whatever the generator does, and that it is the one component whose behaviour does not depend on the generator's cooperation: the prompt can be wrong, and the gate still holds. A refusal rate and a hallucination rate on generated text remain different quantities, and the two are still not interchangeable in the abstract. The null under
the cautious condition belongs to the Selection Effect and Recognition–Refusal
Misalignment literature: the prompt had already realised the gate's function on
that slice, so the gate's marginal contribution there is legitimately zero, and
the honest reading is "the prompt had done the gate's job", never "gating does
not work". §E.7 has the full comparison.

### F.0.5 Attribution and faithfulness evaluation

**What the literature established.** That the unit of faithfulness measurement
is the *claim*, not the answer. ALCE (Gao et al., EMNLP 2023, arXiv:2305.14627)
introduced **citation precision** and **citation recall** as the backbone
metrics and reported that on ELI5 even the best models lack complete citation
support 50% of the time. FActScore (Min et al., EMNLP 2023, arXiv:2305.14251)
decomposed a generation into atomic facts and scored the share supported by a
reliable source; ChatGPT scores 58%, and its automated estimator has under 2%
error rate across 6,500 generations. TRUE (Honovich et al., NAACL 2022,
arXiv:2204.04991) meta-evaluated factual-consistency metrics and proposed an
*example-level* protocol rather than system-level correlation. ExpertQA
(Malaviya et al., arXiv:2309.07852) collected 484 domain experts across 32
fields to produce 2,177 questions with per-claim attributions. Yue et al.
(EMNLP 2023, arXiv:2305.06311) defined *types* of attribution error.

**What it leaves open.** What to do when the evidence does not support any
part of the answer — which is the per-claim analogue of abstention, and the
subject of Conformal-RAG (arXiv:2506.20978) at the sub-claim level and GRACE
(arXiv:2609.04442), whose three-way Grounded/Refuted/Boundary labelling is
close to this project's *grounded* / *inferred* / *uncertain* banding.

**Where this work sits.** This project uses the atomic-claim decomposition and
reports both sides of the ALCE pair, and it adds the abstention behaviour: a
claim that the retrieved set does not support is labelled *uncertain* rather
than being asserted. The per-claim confidence is a noisy-OR over the
per-chunk entailment probabilities (§C.9), and the information gain reported
alongside it is 1 − H_b(q), so a fully supported claim carries 1 bit and an
unsupported one carries 0. §E.8 audits the answer side rather than trusting it.

### F.0.6 Contradiction and conflict detection

**What the literature established.** That "contradiction" is a category with
sub-types, and that conflating them is the standard error. **ContextConflict**
(EMNLP 2026, DOI 10.18653/2026.emnlp-main.918) identifies six conflict types —
factual, inferential, temporal, granularity, perspective, ambiguity — of which
**only two are genuine contradictions**. **ConflictScore** (EMNLP 2026, DOI
10.18653/2026.emnlp-main.2589) decomposes responses into atomic claims, labels
each against each grounding document, and aggregates into CS-Count/CS-Ratio with
a ConflictBench. Separately, the NLI literature establishes a hard ceiling for
this class of model on technical text: published macro-F1 figures on SciNLI and
MSciNLI are far below general-domain performance, and annotation artefacts and
negation failure compound it.

**What it leaves open.** The *joint* problem this project's D4 addresses — how
to tell a genuine contradiction from two passages that are merely about
different things — and the measurement problem: a conflict detector's precision
cannot be computed against a proxy defined by one of its own branches.

**Where this work sits.** D4 combines a logical-conflict signal (NLI) with an
orthogonal same-subject signal (embedding similarity **or** entity overlap),
because raising the NLI threshold alone suppresses false positives and genuine
conflicts together, whereas adding an independent signal lets the two error
types be traded off separately. The context is reported as a *type* rather than
a binary flag, following ContextConflict, and conflicts are surfaced rather
than resolved, because published evidence indicates that surfacing outperforms
resolving.

**And here the honest result is negative.** Measured against blind reader labels
rather than against a proxy, the gate's precision is 0.0% of 20 alarms; the same readers find 0 contradictions in 80
random unflagged pairs. The corpus holds concept-level prose rather than the
revised procedures the mechanism exists to detect, so **this corpus cannot
evaluate the mechanism at all**, and the deliverables say so rather than quoting
a proxy.

What makes that a finding rather than a shrug is that the measurement was used
to repair the detector. Two rules were defective and both were fixed — the
quantity rule, which keyed a number to the nearest distinctive word, and the
subject check, which let topical similarity through on its own although its own
design says otherwise — and the gate's alarms fell from 81
to 20. A third piece of evidence separates the mechanism
from the corpus: the detector's own positive control, in which the correct
behaviour of every pair is known in advance, is 11 of 11. So the mechanism works, and this corpus cannot test it.

That is also why the shipped system does not cry wolf. Each branch has a
measured precision, fitted into a calibration the pipeline reads, and a branch
below the floor has its findings recorded and withheld rather than shown to a
practitioner — the discipline the answer gate applies to an answer, applied to
the framework's own claims. §C.10 derives the design; §E.3 and §E.11 report the
measurement, and §E.12 gathers what the experiments say together.

### F.0.7 Multimodal and table-aware RAG

**What the literature established.** That a context of prose-only chunks
systematically under-serves industrial documentation, where the binding
requirement usually lives in a table. VisDoMRAG (arXiv:2412.10704), TableRAG
(EMNLP 2025), and VisR-RAG-Fin (2026) all attack retrieval over mixed
document modalities, and TechRAG (arXiv:2606.01613) — *Evidence-Gated
Multimodal Agentic RAG for Technical Literature Reasoning* — is the closest
prior art to the whole thesis and post-dates the proposal.

**What it leaves open.** Where the quota belongs in the pipeline, and whether a
quota helps at all when the corpus has nothing to spare.

**Where this work sits.** The mechanism — a hard, non-bypassable quota on the
*final* context rather than a soft instruction to the model — is not new, and
the thesis does not claim it is. The finding is about *placement and preconditions*:
the quota only pays where the corpus leaves something for it to buy, and **where
it is placed relative to the reranker decides more than the quota's own logic** —
before the reranker it restores the table recall the reranker destroyed
(0.964 → 0.929 → 1.000 on the six-category corpus), after it
it reaches 0.929, and which is cheaper depends on the retriever. §C.8
derives the quota and its placement; §E.1 reports the ablation.

### F.0.8 Industrial RAG and the long-context threat

**What the literature established.** That industrial RAG is a live area with
real deployments and real numbers — and that the strongest threat to any RAG
architecture is that **long context simply wins**. A 2026 study of
document-grounded generation in *manufacturing safety* reports 73.1% for
long-context versus 65.4% for semantic RAG at 26× the token cost, and another
reports 99.3% by placing a ~26k-token knowledge base entirely in the prompt.

**What it leaves open.** What long context costs. Token counts are not a cost
model, and a cost model is what a practitioner needs.

**Where this work sits.** The cost half is measured in dollars, not tokens:
The long-context arm sends 74x more input tokens per query than the pipeline, which at the provider's cached-prefix pricing, with the corpus prefix served as a cache read on 33.0% of the long-context arm's input tokens is a 58.8x input-cost ratio rather than 74x: the token ratio and the cost ratio are different numbers, and only the second one is a cost. The answer-quality half is measured on the focus domain,
where the corpus fits, and the six-category corpus — which exceeds the 128K
window most hosted models offer but fits the 1M-token window of the generator
used here — is reported separately and never pooled with the focus domain.
The answer-quality half of the comparison was measured on the focus domain. With the whole corpus in the prompt the generator answered 31 of 32 answerable questions, the same coverage as the pipeline, and it declined the unanswerable questions at a comparable rate (76 of 144 against 77 of 144), for 74 times the input actually sent per query. On coverage and on cost the result is settled: the whole-corpus prompt declines no more unanswerable questions than the pipeline does and costs 74 times as much to do it. On answer quality the margin is directional but not statistically significant once the answers are scored without the length confound. the comparison is measured, and on this corpus it does not support a superiority claim for long-context prompting in this domain The framing in the proposal's wording
("across diverse industrial sub-domains") is an **intra-domain** transfer study,
and §5.4 says so.

### F.0.9 Benchmark validity and label noise

**What the literature established.** That LLM-generated benchmarks carry label
noise, that LLM-as-judge carries position and leniency biases, and that a
benchmark can be *separable from its input alone* — which makes it a weak test
of the thing it claims to test.

**What it leaves open.** The precedent for a defensible *audit* of one's own
benchmark: not merely reporting that a benchmark may be defective, but
encoding the defect, measuring it, repairing it, and re-measuring everything.

**Where this work sits.** This is where the project made two of its own
findings, and both were negative before they were repaired. The **unanswerable
half of the benchmark was separable from the question text alone**: the
designated hard case asked about a fabricated identifier (`SKU AST-5454`), an
identifier shape no answerable question carried, so a single regular expression
separated the classes perfectly — 76.4% of the class, with no
false positives at all. The half was rebuilt as a **corpus-anchored** class with
the same stems, the same source documents and the same label machinery, and
every measurement was taken again. Separately, an audit of the answer-label
generator found that 27 of the 132 answerable questions carried an answer label
attached to the wrong question (20.5%) —
a table question that names the column its key came from rather than the column its answer came from, and a numeric gold that is a digit prefix of a longer token in the chunk — and the generator was corrected, the benchmark rebuilt, and
everything re-measured against it; the audit now finds 0
remaining defects out of 32. The instrument is kept
alongside the measurement so that the finding stays checkable: the audit is
`impl/experiments/audit_unanswerable_class.py`, the repair is
`impl/scripts/unanswerable_repair.py`, and the benchmark as it stood before the
repair is preserved beside the repaired one.

**The pattern is the same one as the contradiction measurement.** A quantity that
looked like a result — the refusal rate, the precision, the "corroborated"
share — turned out to be an artefact of how the thing was labelled, and the
only way to find out was to audit the instrument rather than trust it.

## F.1 The five design moves against prior art

| Move | Closest prior art | What survives |
|---|---|---|
| **D1** Confidence gate | Geißler et al. 2026 (arXiv:2605.05244), conformal chunk selection; Yan et al. 2024 (CRAG); Yadkori et al. 2024 (conformal abstention) | **Non-bypassability as a control-flow property**, plus industrial-corpus calibration. *Not* "gating on retrieval confidence" as a goal. |
| **D2** Modality balance | VisDoMRAG (arXiv:2412.10704); TableRAG (EMNLP 2025); VisR-RAG-Fin (2026) | **Mechanism** (a hard, non-bypassable quota on the final context) and **domain**, not the goal. |
| **D3** Hybrid + RRF + rerank | Cormack et al. 2009 (RRF); Bruch et al. 2023 (*ACM TOIS*, fusion functions); Thakur et al. 2021 (BEIR); Decian et al. 2026 | Not priority — hybrid beating flat retrieval is a well-established result. The *finding* is that the reranker's effect on recall is **pool-relative**: the measured curve peaks at a pool about the size of the final context, and a larger pool costs as well as gains. |
| **D4** Contradiction surfacing | **No published equivalent.** ConflictScore (EMNLP 2026) is close for D4+D5; ContextConflict (EMNLP 2026) taxonomises conflict types. | **The strongest surviving novelty.** |
| **D5** Per-claim tagging | Conformal-RAG (arXiv:2506.20978) on sub-claims; ConflictScore (EMNLP 2026); GRACE (arXiv:2609.04442) — Grounded/Refuted/Boundary; CalibRAG (NeurIPS 2025) at the decision level | **Calibration *and* presentation in one artefact, for an industrial audience**, with an auditable refusal. |

**The four-claims test.** Before claiming something is new, ask: 1. Does a published paper already do this? (D1, D2, D3, D5: yes.) 2. If so, does it do it *better*? (We do not claim better. We claim different in kind.) 3. If so, is our version *useful for a different reason*? (Auditability, no training, portability across categories.) 4. If no published work covers it, can we defend the claim with our own evidence? (**D4** — and this is where the effort should go.)

## F.2 The papers a committee member is most likely to raise

**1. Decian et al. (2026), "Dynamic RAG with hybrid retrieval: A novel approach to robust LLMs and hallucination prevention," *Neurocomputing* 705, 134911.** Hybrid retrieval with an entropy-based dynamic threshold, reported as a statistically significant gain in correctness. This is the *nearest* prior art to D1 on the mechanism — a retrieval-confidence threshold that changes system behaviour — and the proposal names it as such, so it must be engaged directly. The defensible difference is one of philosophy rather than accuracy: an auditable refusal with a stated reason versus a probabilistic adjustment of the retrieval. **Do not claim to beat it.** A defensible framing is that an entropy-based dynamic threshold adapts continuously to the query, whereas a calibrated posterior with a stated operating point is reproducible and auditable — a different property, and the one that matters in a regulated setting.

**2. Geißler et al. (2026), "Towards Dependable RAG Using Factual Confidence Prediction," arXiv:2605.05244.** Conformal chunk selection plus an attention-based factuality classifier, framed explicitly for industry. Two stages: conformal prediction filters chunks, then an attention-based factuality classifier scores answer–context consistency. Reports up to 6% answer-quality improvement and up to 77% inconsistency detection — and concedes that "the associated statistical guarantees do not hold generally, since the assumption of sample exchangeability depends on the retriever setup." **This is our best citation.** It is *both* the strongest competitor and the source of our own stated limitation.

**3. TechRAG (2026), arXiv:2606.01613** — "Evidence-Gated Multimodal Agentic RAG for Technical Literature Reasoning." Hybrid FAISS+BM25 → cross-encoder rerank, visual retrieval, a 100-point evidence-sufficiency rubric, citation-integrity verification. **This is the closest prior art to the whole thesis and it post-dates the proposal.** It must be cited.

**4. DeclineCraft (Thakur et al., 2026), arXiv:2610.28340.** A 2026 abstention benchmark. Three findings that bear directly on us:
- Adding query rewriting and reranking to hybrid dense+sparse retrieval **lowers** Correct Abstention Rate for all 12 models tested.
- Iterative RAG lowers CAR versus single-shot in 30 of 40 configurations.
- Model scale does **not** buy abstention ability (no significant association).

The first finding is a direct challenge: our D3 *improves* retrieval, and DeclineCraft says better retrieval reduces abstention. **The operational consequence is that the gate's operating point must be calibrated per retrieval configuration.** A single global threshold across arms will manufacture a spurious result. This must be stated as a limitation, not discovered by a reviewer.

**5. Phillips et al. (2026), "Entropy Alone is Insufficient for Safe Selective Prediction in LLMs," arXiv:2603.21172.** Shows entropy-based uncertainty has a *model-dependent* failure mode, and that a selective-prediction policy must be evaluated **at a stated operating risk level**. This is a methodological instruction: evaluate the gate as a selective-prediction policy with a risk–coverage curve, not as a single average hallucination rate. We follow it.

**6. ContextConflict (EMNLP 2026), DOI 10.18653/2026.emnlp-main.918.** Identifies six conflict types — factual, inferential, temporal, granularity, perspective, ambiguity — of which **only two are genuine contradictions**. This is the strongest published justification for a *topical* gate and for reporting a conflict *type* rather than a binary flag.

**7. SYNCHECK (Wu, Gu, Yin & Peng, EMNLP 2024), DOI 10.18653/v1/2024.emnlp-main.527, pp. 9390–9406.** Monitors decoding dynamics — sequence likelihood, uncertainty, context influence, semantic alignment — to flag unfaithful sentences as they are generated; 0.85 AUROC over six long-form RAG tasks, and its FOD decoding **outperforms abstention by over 10%**. **This is the sharpest challenge to D1**, and the answer is set out in Part G.

**8. ConflictScore (EMNLP 2026), DOI 10.18653/2026.emnlp-main.2589.** Decomposes responses into atomic claims, labels each against each grounding document, and aggregates into CS-Count/CS-Ratio, with a ConflictBench. This is close prior art to D4 + D5 combined, and "first-ever conflict detection" would be false.

**9. HALT-RAG (Goswami & Kurra, 2025), arXiv:2509.07475.** The nearest prior art to the confidence gate, and the one a committee will raise first. It is a **post-hoc verifier**: it operates on "the source text and generated output without performing retrieval itself", scores hallucination with an ensemble of two frozen NLI models plus lexical signals through a calibrated meta-classifier, and reports out-of-fold F1 on HaluEval under a precision-constrained abstention policy. So it is prior art for the *detector*, and it is **not** a retrieval-time gate. Its own Future Work says: *"A critical next step for this line of work is to integrate and evaluate detectors like HALT-RAG within a live RAG pipeline to measure its resilience to noisy or irrelevant retrieved context."* **That step is our Experiment 8.** The correct thing to say in the defence is therefore not "our gate is new" — it is not — but "the abstention mechanism is published and we do the measurement the mechanism's own authors name as the next step, and the measurement's answer is conditional in a way detector-level F1 cannot show".

**10. I-CALM (Zong et al., 2026), arXiv:2604.03904.** The paper that most directly answers our experimental-design question. It introduces a **two-stage evaluation protocol**: the model first chooses to answer or abstain, and is then **forced to provide a best guess for the abstained ones**, so the counterfactual answer of every abstention is recovered and the abstention decision can be scored as a classifier of whether that answer would have been wrong. It reports coverage, FAR_answered, ECR, CAR and **J_abs** (Youden's J for the abstention decision), and it compares against baselines **at matched coverage**, including explicit-IDK prompting — which it reports as often impractical, with coverage collapsing to 0.290 on one model and 0.002 on another. Our two prompt conditions are a simpler version of this design; their baseline result is the published precedent for a prompt that refuses on its own.

**11. TAPS (Zhang et al., 2026), arXiv:2610.16318.** Decomposes abstention risk into **answering ability** and **distinguishing ability**, and compares selective answering against abstention training **at matched coverage** on a common evaluation subset, so that neither arm is a straw man. It reports 1.5–9.4 percentage points lower mean risk than abstention training at matched coverage. This is the citation that fixes our comparison protocol: the arms must be compared at matched coverage, or the arm that refuses more wins for the wrong reason.

**12. UAEval4RAG (Peng et al., ACL 2025), 2025.acl-long.415.** Defines six categories of unanswerable request for a given knowledge base, scores systems with an **Acceptable Ratio** and an **Unanswered Ratio**, and combines them in a Joint Score that balances answerable-question correctness against acceptable rejection. It also **sweeps prompt restrictiveness as an explicit experimental factor** and finds that more restrictive prompts reject more unanswerable queries while slightly degrading answerable-question performance, and that "no single configuration consistently delivers optimal performance on both answerable and unanswerable requests". This is the published form of the question our two prompt conditions ask, and its metrics are the ones a refusal count should be reported alongside.

**13. The Selection Effect (Tikhomirov & Savchenko, EMNLP 2026), 2026.emnlp-main.1049,** and **Recognition–Refusal Misalignment (Du & Hu, EMNLP 2026), 2026.emnlp-main.1078.** These two are the reason we report our negative result the way we do. The Selection Effect finds that "encoder gating forwards a conditional slice on which compact LLMs perform no better than the encoder itself, or substantially worse, erasing any standalone LLM advantage" — a gate can destroy the value of what stands behind it, because on the slice the gate forwards, the downstream component is no better than the baseline. Recognition–Refusal Misalignment separates *recognising* impossibility from *routing* it to abstention and finds the two directions "nearly orthogonal", so a model can know the answer is unavailable and answer anyway. **Our cautious-condition null belongs to that literature:** the prompt had already realised the gate's function on that slice, so the gate's marginal contribution there is legitimately zero, and the honest reading is "the prompt had done the gate's job", never "gating does not work". Related caution: ACL 2026 (2026.acl-long.1365) finds that models "systematically overcommit, rarely abstaining", so a single model that abstains is not the general case, and the null we report — reproduced on one generators — is a statement about this setup rather than about gating in general.

## F.3 The threats

**T1 — Long context beats RAG in this exact domain.** A 2026 study of document-grounded generation in *manufacturing safety* reports 73.1% for long-context versus 65.4% for semantic RAG, at 26× the token cost. Another reports 99.3% by placing a ~26k-token knowledge base entirely in the prompt. **On a corpus of this size, long context may simply win** — the focus domain's 735 chunks are 202,529 tokens, which does not fit the 128K window most hosted models offer. This is the most serious threat to the entire thesis. **Parts E.6 and E.7 measure the cost half of it**: The long-context arm sends 74x more input tokens per query than the pipeline, which at the provider's cached-prefix pricing, with the corpus prefix served as a cache read on 33.0% of the long-context arm's input tokens is a 58.8x input-cost ratio rather than 74x: the token ratio and the cost ratio are different numbers, and only the second one is a cost. On the six-category corpus the corpus does not fit the 128K window most hosted models offer at all. The answer-quality half is now measured too: The answer-quality half of the comparison was measured on the focus domain. With the whole corpus in the prompt the generator answered 31 of 32 answerable questions, the same coverage as the pipeline, and it declined the unanswerable questions at a comparable rate (76 of 144 against 77 of 144), for 74 times the input actually sent per query. On coverage and on cost the result is settled: the whole-corpus prompt declines no more unanswerable questions than the pipeline does and costs 74 times as much to do it. On answer quality the margin is directional but not statistically significant once the answers are scored without the length confound. the comparison is measured, and on this corpus it does not support a superiority claim for long-context prompting in this domain.

**Three things bear on how this threat should be answered, and all three are cited rather than asserted.** First, the closest published analogue to our corpus is *favourable* to retrieval: Agri-Query (arXiv:2508.18093) places a 165-page agricultural-machinery operator manual — roughly 59K tokens, chunked at 200 tokens — in the prompt and reports that hybrid RAG consistently beats direct long context, with naive insertion of the whole manual yielding significantly worse results. A machinery manual is what our corpus is a stand-in for. Second, the 2025–2026 consensus is that the question is not *which* to use but *when to route*: LaRA's title is literally *No Silver Bullet for LC or RAG Routing* (arXiv:2502.09977), and the state of the art is a router that escalates only the queries that need it. Our long-context arm is the always-long-context arm of exactly that decision, and we measure it rather than assert a preference for the other arm. Third, a result from November 2026 predicts our own failure mode: *Length Is Cheap, Competition Is Not* (arXiv:2611.04169) reports that the attention mass on evidence explains about 58% of the variance in retrieval loss against at most 8% for log-length, and that a single competing value multiplies the loss by 9–110×. So the expected way a whole-corpus prompt fails on industrial text is *competition among similar values* — several tables stating different numbers for the same quantity — rather than length as such, which is a prediction our corpus can test and our part numbers can show.

**T2 — Query-time filters can measure the benchmark, not the filtering.** A 2026 study of RAG poisoning defences shows AUROC collapsing from 0.953 to 0.758 and miss rate rising from 0.191 to 0.763 after removing a single construction cue from the benchmark, and reports that **12 of 21 published evaluations report no false-positive rate at their operating point.** This is a devastating methodological point: many published RAG filters are detecting a shortcut in the benchmark rather than filtering meaningfully. Our gate must be reported with a false-positive rate at a stated operating point, with length-matched controls and a threshold sweep.

**T3 — LLM-as-judge validity.** Position bias flipped **66 of 80** queries in one measured study; the best judges are still off by up to 5 points and skew lenient; cheap judges achieve AUROC as low as 0.603. If the 500-question benchmark is annotated by LLM agents, the judge must be meta-evaluated against a human-annotated subset.

**T4 — Confident errors.** A claim can be supported by a retrieved passage that is itself stale or wrong. Low uncertainty is not correctness. This is why the framework pairs every confidence tag with a citation, and why D4 (contradiction surfacing) partially covers it — but the literature does not support any claim that contradiction detection catches stale-versus-current conflicts reliably.

**T5 — The corpus is too small for the statistical framing.** 634 chunks, 24 documents, a 30-query calibration set, a 16-participant user study, one focus category. All of these sit below the scale at which conformal machinery, operating-point analysis, or risk–coverage framing are statistically well-founded. Own this early.

**T6 — NLI on technical text is weaker than NLI on general text.** Published ceilings: SciNLI 78.18% Macro-F1, and an LLM-based system on MSciNLI at 51.77%. Annotation artefacts (hypothesis-only at 67%/53%) and negation failure compound this. **The NLI leg must be validated on the industrial corpus, not imported from a general-domain number.**

## F.4 The defensible novelty statement

> Recent work applies conformal prediction to retrieved chunks with finite-sample
> guarantees [Geißler et al., 2026], abstention-policy research shows that a
> threshold must be validated at a stated operating risk level rather than by a
> single average number [Phillips et al., 2026], and empirical studies show that
> better retrieval can *reduce* abstention [Thakur et al., 2026]. We adopt all three
> lessons: we evaluate the gate as a selective-prediction policy with a
> risk–coverage curve, we report a false-positive rate at a stated operating
> point, and we re-fit the calibration for every retrieval configuration we
> compare. We do **not** claim the exchangeability guarantees of conformal
> prediction, because on a single-category industrial corpus those assumptions are
> known not to hold. Our contribution is different in kind: a **code-level,
> non-bypassable** gate that produces an auditable refusal, and, in the
> contradiction-surfacing component, a **type-aware** conflict report in which
> the numeric detector is independent of the NLI verifier and the supersession
> check is explicit. The conjunction itself is not published, but every conjunct
> is — HALT-RAG (arXiv:2509.07475) publishes a calibrated NLI ensemble with
> lexical signals under a precision-constrained abstention policy, which is
> prior art for the *detector*, and Kontrast (arXiv:2607.25959)
> formalises the temporal-change distinction we implement as a supersession
> check. HALT-RAG is, however, a **post-hoc verifier**: it reads the source
> text and the generated output and never retrieves, and its own Future Work
> names "integrate and evaluate detectors like HALT-RAG within a live RAG
> pipeline" as the critical next step — which is the experiment this thesis
> runs. **We do not claim the abstention mechanism is new, and we do not claim
> the contradiction gate is new.** We claim it is a carefully instantiated
> one, we report what it costs rather than only what it catches, and we are
> explicit that the detector's own quality is not the question we answer.
>
> Our headline empirical contribution is not the architecture but the
> **failure-mode characterisation**, and it is mostly negative. We show, on an
> independent corpus, that a modality quota is a **trade and not a gain**, and
> that its pipeline position decides what it costs; that a reranker's effect on
> recall is governed by its **candidate pool** rather than by the reranker; that
> the modality composition of the corpus — not the algorithm — determines
> whether a modality-aware mechanism can have any effect at all; and that the
> confidence gate **cannot separate "there is no evidence here" from "the
> evidence is here and the retriever missed it"**, because the retrieval scores
> it uses cannot. That last one is a negative result about our own mechanism,
> and it is the one we expect a committee to press on, so we state it before
> they do.

**Why this survives an adversarial examiner.** It claims no priority, it states
what it does *not* claim, and it puts the weight on results that are reproducible
from a public corpus with public code.

**Two narrowings forced by work published while this thesis was being written.**
The first concerns the gate itself: a pre-generation gate with escalation is now
published prior art in enterprise (RCL, arXiv:2609.11023, a retrieval-confidence
layer between retrieval and generation that escalates or labels for human review
below a calibrated threshold), in regulated trade finance (HIRA, CIKM 2026,
arXiv:2608.21792), in evidence-grounded QA with runtime accept/refuse/regenerate
(CiteGuard-RAG, arXiv:2609.15830), and in nuclear engineering with provenance
tracking (RADIANT-LLM, arXiv:2604.22755). **We do not claim the gate.** The
second concerns the contribution sentence itself: between July and November 2026
the field produced at least five papers whose explicit object of study is what a
reliability mechanism costs and what it buys — a memory tier that costs +0.368 MiB
and buys nothing (arXiv:2610.07782), a confidence-gated cascade whose *matched
random-escalation control does as well* (arXiv:2610.20634), calibrated
retrieval-budget allocation reporting that gating is not universally faster
(arXiv:2606.29959), conformal factuality control reported jointly with claim
retention (arXiv:2609.38222), and a leakage-controlled, cost-aware evidence-gating
protocol (arXiv:2609.39075). **So "we measure reliability mechanisms" is no longer
a novelty claim; it is the house style of 2026 RAG evaluation, and we do not make
it.** What is not in that list is the joint cost–coverage–reliability frontier for
a confidence gate **on industrial text, at the level of the individual answer
claim, on a corpus regime that is not the procedural one every prior deployment
uses.** That is the claim, and it is narrower than the one this thesis began with.
We would rather defend the narrow claim than lose the wide one.

**The random-escalation control is now part of our own experiment, because the
literature says to run it.** arXiv:2610.20634 is the paper to read: it compares
a cheap non-generative verifier against a frontier LLM on the same 495
human-labelled claims, finds the two *statistically indistinguishable* on the
conventional metric while they disagree on 15.2% of claims and admit very
different rates of unsupported claims (23.2% against 14.1%), and then reports
that "a matched random-escalation control at in-sample thresholds, spending the
same budget by coin flip, does as well, so what buys the saving is the escalation
share and not the probability that picks what to escalate." Its conclusion —
"equal accuracy conceals unequal errors" — is exactly the trap this thesis's
own numbers could fall into. So Experiment 8 now includes a control arm that
refuses the same *number* of questions as the fitted gate and picks them at
random, and the difference between that arm and the fitted gate is what the
confidence score buys over refusing an arbitrary set of the same size.

### F.4.1 The novelty check, and what it changed

A check of the five findings against the published literature — every
identifier resolved against a live registry on 11 November 2026, and written
up in `research/13_novelty_and_positioning.md` — changed what this thesis
leads with. In short:

| Finding | Published? | What may be claimed |
|---|---|---|
| A conflict detector's precision decomposes into **detection** and **typing** | **No** — not published in this pairing | Two metrics instead of one; they are nine-fold apart; a branch with recall 0.000 where conflict provably exists; and a specification — a detector for regulatory text needs version metadata, or must be scoped to detection alone |
| The per-claim band measures **agreement with itself, not correctness** | The filter result is published; the decomposition is not | The band is ordered on the evidence it saw and indistinguishable on an independent reference |
| **Rubric vs reader specialisation** | The principle is published; the factor of nine is not | The specification of the task moved the measured precision of an unchanged detector by a factor of nine |
| **Point-in-time regulatory corpora** as a source of labelled conflicts | The *method* is published (NitiBench+, ICAIL 2026); the *purpose* is not | We applied a published corpus-construction method to conflict detection, and the detector that consumed it finds the conflicts and cannot type them |
| **BM25 beats a dense encoder** on regulatory text | **Already published**, three times, in three jurisdictions | Only the pipeline corollary: the lexical leg carried the pipeline and the fusion and the pre-filter added nothing on top of it |

Two consequences, and the committee will check both. **The BM25 result must
not appear in the abstract** — it is already known, and leading with it is the
one place this thesis would inflate its novelty. And **the spine is the
detection/typing decomposition**, with the failure-mode characterisation as
the second contribution and the rubric factorial as a methodological result
that belongs in an evaluation section rather than in a contribution list. The
full check, with every identifier resolved live, is in
`research/13_novelty_and_positioning.md`.

## F.5 The claims we must NOT make

- ❌ "BM25 beats dense retrieval on regulatory text." Already published, three
  times, in three jurisdictions (arXiv:2506.12895 on CJEU passages,
  arXiv:2412.07462 on statutory articles in Dutch and French, arXiv:2604.01733
  on financial text-and-table documents), with a counter-case at
  arXiv:2608.18752. Our claim is the *corollary* — the lexical leg carried
  this pipeline and the fusion and the pre-filter added nothing measurable on
  top of it — and the dense leg here is a general-purpose encoder that a
  domain-adapted one could overtake (arXiv:2506.12895, arXiv:2604.17778).
- ❌ "We are the first to decompose a conflict detector's precision." The
  taxonomy is published and the difficulty of typing a conflict is known; the
  *pairing* of detection precision and typing precision, reported as two
  numbers, is what is new.
- ❌ "Our gate reduces hallucination better than CRAG / Self-RAG / conformal
  abstention." No such comparison exists in the current evidence base.
- ❌ "We are the first to use a Bayesian posterior for retrieval confidence in
  RAG." Language-modeling IR established the Bayesian relevance model in 1999–2005
  (Song & Croft; Azzopardi et al.; Hiemstra et al.).
- ❌ "We are the first to abstain in RAG." SQuAD 2.0 (2018) defined the task.
- ❌ "Semantic entropy cannot be used at claim level." Confidence-weighted semantic
  entropy (Neurocomputing 2026) and semantic entropy probes (arXiv:2406.15927)
  make this untenable.
- ❌ "No public benchmark exists for industrial-engineering Q&A." **Partly false.**
  TeleEmbedBench (arXiv:2604.17778), a 5,144-pair Kubernetes benchmark, MiRAGE and
  ExpertQA all exist. The defensible version is narrow: *"no public benchmark spans
  multiple industrial-engineering sub-domains with dual expert annotation,
  reported κ, per-claim attribution labels, and an unanswerable class."*
- ❌ "Our hybrid retrieval outperforms flat retrieval." This is a well-established
  result (BEIR: BM25 0.413 → BM25+cross-encoder 0.473, +14.5%) and is **not** a
  contribution. Cite it as prior art and report our number as a replication.
- ❌ "SupplyChainQA is a public benchmark." It is our own unreleased construction;
  the report itself lists the Zenodo release as future work.
- ❌ "Our contradiction gate has no published equivalent." HALT-RAG
  (arXiv:2509.07475) publishes the calibrated abstention mechanism — an NLI
  ensemble with lexical signals under a precision-constrained policy — and
  Kontrast (arXiv:2607.25959) publishes the conflict taxonomy we implement.
  Narrow the claim to the *industrial instantiation with an NLI-independent
  numeric detector*, and to the measurement.
- ❌ "Our gate judges evidence sufficiency." It does not. The label is
  answer-in-context detectability, and the literature reserves "sufficiency"
  for the set-level property (SURE-RAG, arXiv:2605.03534; Certify,
  arXiv:2610.34684). Say "the gate detects whether the answer is in the
  retrieved context".
- ❌ "Our gate catches unanswerable questions." Report the rate at a stated
  operating point against the *never-refuse* and *always-refuse* policies. The
  endpoints of a threshold sweep are not baselines.
- ❌ "Our results transfer to industrial practice." The corpus is
  industrial-engineering *encyclopaedic* text. Beyond the Reranker
  (arXiv:2606.28367) reports that retrieval-enhancement gains come almost
  exclusively from homogeneous corpora, predominantly Wikipedia prose, which
  ours is. State the upper bound rather than the generalisation.
- ❌ "Our contradiction gate recalls 100% of verifiable conflicts." That number
  is true by construction: the verifiable subset is *defined* by numeric
  conflicts and the numeric detector is an OR-branch of the gate. Report what
  the NLI-and-same-subject conjunction catches on its own.

## F.6 The bibliography errors we found and fixed

Every one of the proposal's 18 references resolves to a real paper — there are **no
phantom citations**, which is unusually good. But several carry errors that a
citation checker or an examiner would catch:

| Reference | Error | Correction |
|---|---|---|
| [15] "Microsoft Research (2025), arXiv:2507.21502" | **Wrong author and wrong characterisation.** The authors are **Simchi-Levi, Mellou, Menache & Pathuri**; it is a Springer book chapter, and it is about applying LLMs as a conversational layer over optimisation-based supply-chain tools — not a fine-tuned procurement model. | Simchi-Levi, D., Mellou, K., Menache, I., & Pathuri, J. (2025). *Large Language Models for Supply Chain Decisions.* In *AI in Supply Chains*. Springer. arXiv:2507.21502. |
| [17] "An Application-Oriented Survey" | The title is "A **Capability-Oriented** Survey". | Li, Y., Fu, X., Verma, G., Buitelaar, P., & Liu, M. (2025). arXiv:2510.24476. |
| September report [5] CRAG | **The DOI and page range belong to a different paper.** DOI 10.18653/v1/2024.findings-acl.212, pp. 3563–3578 resolves to **Dhuliawala et al., "Chain-of-Verification Reduces Hallucination in Large Language Models."** CRAG is indexed as arXiv-only. | Cite CRAG as arXiv:2401.15884 and do not attach that DOI. |
| Cross-encoder model ID | `ms-marco-MiniLM-L-6-v2` is not the canonical Hugging Face ID. | `cross-encoder/ms-marco-MiniLM-L6-v2` |
| "MiniMax embed-01 (1024-d)" | No embedding model of that name appears in current MiniMax API documentation. | Use `BAAI/bge-m3` (1024-d). |
| [13] CRUD-RAG | Cited as an arXiv preprint. | Now published: *ACM TOIS*, DOI 10.1145/3701228. |
| [9] InstructRAG | Venue given as 2024. | ICLR 2025 (arXiv:2406.13629). |
| Unverified numbers | The literature table states "77.8% accuracy" (Wan et al.) and "92.4% Top-3 accuracy" (Wu et al.). The papers are real and the DOIs resolve, but **neither figure could be confirmed from the metadata**. | Do not repeat either figure until the full texts are checked. |

---

## F.7 What changed in 2026, and what it forces us to narrow

Three developments between the framework's specification and this writing bear
directly on our claims. This subsection exists so that nobody discovers them in
the room.

**The abstention mechanism has moved past a threshold.** GRAB-RAG
(arXiv:2608.22228) shows that under explicit abstention prompting, models still
answer 41.6% of *misleading* questions, with 63% of those answers echoing the
planted wrong entity; the paper's contribution is not that a threshold exists
but that a threshold is insufficient. SURE-RAG (arXiv:2605.03534) argues that
sufficiency is a *set-level* property that independent passage scoring cannot
detect, and Certify (arXiv:2610.34684) makes it structural, deriving a
Horn-closure certificate from a per-query requirement hypergraph. Sieve and
Sage (arXiv:2609.35794) screens the retrieved set in a lightweight module
*outside* the model before the model is invoked, with a two-state failure
decomposition — unanswerable versus distracted. AGO (arXiv:2610.01218)
quantifies regression risk probabilistically instead of thresholding.

**What this forces on us.** Our gate is a **calibrated answer-in-context
detector with a stated operating point**, not a sufficiency judge, and the
literature reserves "sufficiency" for the set-level property. Part E reports
the contingency table that makes the distinction concrete: how many answerable
questions had their evidence found, how many had it missed, and how many were
unanswerable. On the evaluation corpus the retriever's own recall of the gold
chunk is 100.0%, so retrieval failure accounts for 0.0% of the negative class — the negative
class is mostly genuinely unanswerable, and the gate does well. But the
mechanism is the reason to be careful: the gate's features are retrieval
scores, so its ceiling is set by the retriever, and on a corpus where the
retriever is weaker the same gate would face a negative class dominated by
retrieval failure that it cannot resolve. A reviewer who reads the code will
see that in five minutes.

**The closest single pre-emption of our contradiction mechanism is published.**
HALT-RAG (arXiv:2509.07475) is task-adaptable: an ensemble of NLI models
combined with lexical signals, fed to a calibrated meta-classifier, deployed
under a precision-constrained abstention policy. It is also, and this is the
part that matters for positioning, a **post-hoc verifier**: it operates on the
source text and the generated output "without performing retrieval itself",
so what it reports is the detector's coverage and its detector-level F1, not
a RAG system's behaviour. Its own Future Work says that "a critical next
step for this line of work is to integrate and evaluate detectors like
HALT-RAG within a live RAG pipeline to measure its resilience to noisy or
irrelevant retrieved context". That step is Experiment 8 in this thesis, and
it produces a finding the detector-level literature cannot: put the gate in
front of a live generator and its value depends entirely on whether the
generator declines on its own.
Kontrast (arXiv:2607.25959) separates direct conflicts from
information-granularity differences, temporal changes and incompleteness, which
is our supersession check formalised. WIKICOLLIDE (arXiv:2509.23233) reports
that at least 3.3% of English Wikipedia facts contradict another fact — which is
both a reason our corpus is a reasonable object of study and a benchmark we
should have used.

**What this forces on us.** Our remaining D4 claim is an *industrial
instantiation* in which the numeric detector is independent of the NLI verifier
and the supersession check is explicit, and that can only be defended against
human labels, which we do not have. We say so.

**Retrieval enhancements stop paying once a strong reranker is present.**
Beyond the Reranker (arXiv:2606.28367) evaluates eight enhancement methods on a
heterogeneous corpus with chunker-agnostic relevance labels and
collection-disjoint splits, and finds that only query expansion and one
calibrated method give reliable gains beyond a strong reranker. Its framing
sentence is aimed at work like ours: the reported gains "come almost entirely
from homogeneous corpora, predominantly Wikipedia prose." Ours is exactly such a
corpus. FreshStack (arXiv:2504.13128) independently reports rerankers that fail
to improve first-stage retrieval on two of five technical topics, and T²-RAGBench
(EACL 2026, arXiv:2506.12071) finds hybrid BM25 most effective on text-and-table
data.

**What this forces on us.** Our effect sizes should be read as an **upper
bound** on what the same mechanisms would deliver on mixed-format industrial
documents. It also means the candidate-pool curve (Experiment 5) is the part of
this work that is most likely to be new, and it is the part that was least
discussed until now.

Two further threats belong with these. The Labeling Problem in Hallucination
Detection Benchmarks (NeurIPS 2026 Evaluations and Datasets Track,
arXiv:2610.08026) shows, with 900 human-labelled pairs, that automated labelers
systematically conflate reference faithfulness with factual correctness — a
direct constraint on our silver-standard labels, and the reason the label
standard is stated in the abstract rather than buried. Entropy Alone is
Insufficient for Safe Selective Prediction in LLMs (arXiv:2603.21172) bears on
our information-gain component. And Detecting Is Not Resolving
(arXiv:2605.27157) reports across more than 50,000 turn-level evaluations that
models acknowledge contradictory evidence without constraining their
recommendations — the monitoring-control gap, and the reason we treat
contradiction *surfacing* as a reporting mechanism rather than a resolution
mechanism.

**The benchmark landscape has moved too.** Expert-annotated industrial and
supply-chain benchmarks now exist: the manufacturing-safety benchmark of
arXiv:2511.11847 (24 RAG configurations in a full-factorial design, top two
reviewed by ten industry experts and academics), arXiv:2606.20898 (972
expert-validated answers, comparing RAG against long-context prompting),
arXiv:2603.20534 (669 requirements across four MBN standards plus 49 supplier
qualifications, with expert quality assessment), RealDocBench
(arXiv:2606.07401, which includes supply-chain logistics), and SupChain-Bench
(10.18653/v1/2026.findings-acl.371, peer-reviewed at Findings of ACL 2026). Our
residual claim — that no public benchmark spans multiple industrial-engineering
sub-domains *with dual expert annotation, a reported κ, per-claim attribution
labels, and a deliberate unanswerable class* — has to be stated in exactly those
terms or not at all. Note also that all six of our categories are
industrial-engineering sub-domains, so our transfer experiment is an
**intra-domain** transfer study, and the proposal's wording should be read that
way.

## F.8 The benchmark landscape, and what our benchmark is not

A panel member will ask what our benchmark should have been compared against.
The 2026 landscape has expert-annotated industrial and supply-chain benchmarks,
so the honest answer names them.

| Benchmark | Size | Domain | Annotation | Identifier |
|---|---|---|---|---|
| Manufacturing-safety chatbot benchmark | Expert-validated QA over 3 machines; 24 RAG configurations, full-factorial; top 2 reviewed by 10 industry experts and academics | Machine / occupational safety | Expert validation | arXiv:2511.11847 |
| Token Tax of Epistemic Accuracy | 972 answers, 3 machines, 2 SLMs, 3 grounding architectures | Manufacturing safety | Expert-validated | arXiv:2606.20898 |
| Industrial-scale RAG for requirements engineering | 669 requirements across 4 MBN standards + 49 supplier qualifications | Automotive requirements engineering | Authentic industrial documents; expert quality assessment | arXiv:2603.20534 |
| RealDocBench | 1,356 field-level QA over 581 documents incl. supply-chain logistics | Regulated real-world documents | Typed gold dictionaries; human-verified layout annotation | arXiv:2606.07401 |
| SupChain-Bench | — | Supply chain management | Peer-reviewed benchmark | 10.18653/v1/2026.findings-acl.371 |
| IndusSpec-QA | 3 industrial standard documents | Industrial standards | Ground truth from the standards | 10.18653/2026.emnlp-main.1456 |
| LakeQuest | 9,846 QA pairs, 3 domains | Enterprise/scientific data lakes | Human-validated, with modality-aware evidence pointers | arXiv:2607.12310 |
| T²-RAGBench | 23,088 triples | Real-world text-and-table | Expert-validated at 91.3% context-independence | EACL 2026, arXiv:2506.12071 |
| WIKICOLLIDE / CLAIRE | "the first benchmark of real Wikipedia inconsistencies"; ≥3.3% of English Wikipedia facts contradict another fact | Wikipedia | Human annotation + editor study | arXiv:2509.23233 |
| ExpertQA | 2,177 questions from 484 participants | Long-tail expert domains | Expert-curated questions, expert-evaluated responses, per-claim attributions | 10.18653/v1/2024.naacl-long.167 |

**What our benchmark is not.** Ours is silver-standard: labels derived
mechanically from the document. That is cheap, perfectly reproducible, and
slightly optimistic about absolute recall. It is not expert-annotated, and the
NeurIPS 2026 Evaluations and Datasets Track paper on the labelling problem in
hallucination-detection benchmarks (arXiv:2610.08026) shows, with 900
human-labelled pairs, that automated labelers systematically conflate reference
faithfulness with factual correctness — a direct constraint on what a
silver standard can be used to claim.

**The defensible claim, in full.** *No public benchmark we could find provides
all four of the properties this evaluation needs together: coverage of multiple
industrial-engineering sub-domains, dual expert annotation with a reported κ,
per-claim attribution labels, and a deliberate class of unanswerable questions.
Each property exists in isolation, and several of them — expert annotation,
supply-chain coverage, an unanswerable class — now exist in public benchmarks
that we did not use.* That is the sentence to say. The broader version is
false, and a panel member with the literature in front of them will know it.

**Two corrections to our own earlier notes, found during this check.**
ExpertQA is not arXiv:2402.15049 — that identifier resolves to an astronomy
poster; its canonical identifier is the NAACL 2024 DOI
10.18653/v1/2024.naacl-long.167, and its *published* title is "ExpertQA:
Expert-Curated Questions and Attributed Answers", not the preprint title.
T²-RAGBench's title changed between versions: the arXiv preprint is "T2-RAGBench:
Text-and-Table Benchmark for Evaluating Retrieval-Augmented Generation" and the
EACL 2026 version of record is "T2-RAGBench: Text-and-Table Aware
Retrieval-Augmented Generation".

# Part G — Anticipated viva questions

Each answer is one you can actually defend, with the citation attached.

**Q0. Where did the data come from, and can I run it?**
The primary corpus of the original specification was 634 chunks across 24
proprietary supply-chain documents. It cannot be redistributed, so it cannot be
shipped with this work or re-run by a reader. Every measurement reported here
was taken on a **public substitute**: 46 industrial-engineering
articles from English Wikipedia (2,383 chunks, six
categories), fetched through the MediaWiki API and licensed CC BY-SA 4.0. It was
assembled to have the properties the framework needs — several industrial
categories, genuine tables and figures so the modality mechanisms have
something to act on, and citable provenance.

It ships in full, in `deliverables/dataset/`. For every document the manifest
gives its Wikipedia URL, the upstream revision it was read at, the SHA-256 of
the exact bytes used, and its chunk count. The corpus builder fails loudly
rather than silently dropping a document, and the build checks that no document
is indexed twice or spans two categories.

The thesis focuses on a **single industrial domain, supply chain management**
(14 documents, 735 chunks, 176 questions), because that is what the primary corpus
covered and where the practitioner scenarios come from. The other five
categories exist for the cross-category transfer experiment, which by
definition needs a subset of categories to transfer to held-out ones. Part E
traces real questions from the focus domain end to end.

The honest limitation: these are encyclopedia articles, not operating manuals,
standard operating procedures and supplier specifications. They are industrial
in subject matter, not operationally binding. The labels are silver-standard —
derived mechanically from the document rather than annotated by an expert — so
absolute recall is optimistic. The comparisons between systems are unaffected,
because every system is scored against identical labels.

**Q1. What is the one-sentence contribution?**
An evidence-grounded RAG framework for industrial decision support in which a
code-level, non-bypassable confidence gate, a modality quota, and per-claim
confidence tags are combined; the architectural contribution is modest and
deliberately so, and the substantive contribution is the empirical characterisation
of where each mechanism does and does not help — including three findings that
contradict the design as originally specified.

**Q2. Why is a *code-level* gate better than telling the model to be careful?**
Because an instruction is a request and a branch is a fact. The model cannot
override the gate; there is no output it can produce that reaches the gate. And the
refusal is auditable: "maximum calibrated relevance probability 0.31 against a
threshold 0.50" is checkable, "the model seemed unsure" is not. This is also why
we reject Self-RAG's learned reflection tokens: those are emitted by the model
being gated, and Huang et al. (ICLR 2024) show intrinsic self-correction degrades
without external feedback.

The word "code-level" is doing real work here, so it is worth being concrete
about where the guarantee comes from. The language model is **injected into the
framework**, not called by a harness: `Framework(index, generator=...)`, and the
framework calls it at exactly one line, inside `answer()`, *after* the gate has
accepted. There is no flag, no argument and no early-return path that reaches the
model without passing the gate first, and on a rejection the claim assessment and
contradiction detection are skipped too — a refused query costs no model call at
all. An invariant test asserts this (`impl/tests/test_invariants.py`, "the
generator is reached only through the gate"), and `impl/scripts/verify_gate_path.py`
demonstrates it on the real index by instrumenting the call itself. The only
paths that bypass the gate are the two comparison arms — the ablation arm with
the gate removed, and the whole-corpus long-context baseline — and both are named
for what they remove and reported as separate results.

What the gate does *not* do is judge the *form* of the question. See Q3e.

**Q3. How do you know your confidence probability is a probability?**
We fit a logistic calibration map by maximum likelihood on a held-out *query*
split and report the Brier score, the Expected Calibration Error, a reliability
table, and a risk–coverage curve. A raw cross-encoder score is a logit and is not
a probability; thresholding it directly is a category error.

**Q3a. Why is the calibration query-level rather than chunk-level?**
This is worth knowing because I got it wrong first, and the way I found out is
the point. My first implementation calibrated per *candidate*: "is this candidate
the gold chunk?" With about fifty candidates per query and one gold chunk, the
base rate of positives is about 2%. A classifier that answers "nothing is
relevant" is therefore right 98% of the time, and maximum-likelihood fitting
dutifully returned a large *negative* intercept (β₀ = −2.88) and a nearly flat
slope (β₁ = 0.27). The Brier score was 0.011 and the ECE was 0.004 — which
looked *excellent* — because they were measuring the base rate, not the filter.
The operating point it implied refused 46% of the answerable questions.

The gate does not decide "is this candidate the gold chunk". It decides "does
this context contain enough evidence to answer at all". Calibrating at the query
level removes the degenerate solution, because the base rate there is around a
third rather than 2%.

The general lesson, which is the same one the 2026 literature draws when it
warns that query-time filters can measure benchmark construction rather than
filtering: **the label you choose determines what you are measuring.** A
beautiful calibration number is not evidence that the thing is calibrated.

**Q3b. SYNCHECK beats abstention by over 10%. Why are you abstaining at all?**
This is the sharpest challenge to the work, and I would rather raise it myself.
SYNCHECK (Wu et al., EMNLP 2024) monitors decoding and reports that its FOD
decoding outperforms abstention, reranking and contrastive decoding by over 10%
on faithfulness, at 0.85 AUROC across six long-form RAG tasks.

Three answers. First, the two mechanisms detect different failures: SYNCHECK asks
whether a *generated sentence* is faithful to the context, while the gate asks
whether the context contains enough to answer *at all* — which has to be settled
before generation, because a sentence produced from inadequate evidence cannot
be repaired afterwards. Second, the gate runs before generation, so a refusal
costs one retrieval pass, not a generation plus a monitoring pass. Third, our
claim is not an AUROC against faithfulness detection but per-claim confidence
banding with a cited evidence trail for a practitioner — a different deliverable.

And the concession I make openly: our gate uses a small number of retrieval-side
signals, which is the *simplest* instantiation of the multi-signal design that
both SYNCHECK and Phillips et al. point towards. Combining retrieval confidence,
query–chunk overlap, chunk position and cross-encoder confidence is the natural
next step, and our five-feature calibrator is a first cut at it.

**Q3c. Your gate is calibrated on a label that is really "did the retriever
find the answer". Isn't that a retrieval-success detector, not a sufficiency
judge?**
Yes, and I now say so explicitly rather than defending the old name. The label
is 1 iff the gold chunk is in the reranked candidate pool. The literature
reserves "sufficiency" for a set-level property — that scoring passages
independently cannot detect sufficiency, which is the argument of SURE-RAG
(arXiv:2605.03534) and Certify (arXiv:2610.34684) — so calling my label
"sufficiency" reads as a claim of prior art I do not have. The honest name is
**answer-in-context detectability**.

The consequence is the important part, and it is a limitation rather than a
rhetorical point. The negative class of the label holds two different kinds of
query: answerable questions whose evidence the retriever missed, and questions
that are genuinely unanswerable. Part E reports the three-way decomposition, so
you can see exactly how much of the negative class is retrieval failure — on
the evaluation corpus 0.0%, with the
retriever's own recall of the gold chunk at 100.0%.

The honest statement of the limitation is this. The gate's features are
retrieval scores, so its ability to separate "the answer is in the context"
from "it is not" is bounded by how well those scores carry that information,
and the composition of the negative class moves with the retriever. Here the
retriever is strong enough that the negative class is mostly what the gate is
meant to detect, and it does well. On a corpus where the retriever is weaker,
the same gate would face a negative class dominated by retrieval failure that
it cannot resolve, because the scores it uses are exactly the scores that
failed. That is why the operating point is a fitted, per-corpus parameter, and
why I present the gate as a selective-prediction policy with a risk–coverage
curve rather than as a detector. It is also the field's known result for
model- and prompt-based abstention: GRAB-RAG (arXiv:2608.22228) finds models
still answer 41.6% of misleading questions under explicit abstention
prompting.

**Q3d. What has changed in the literature since you designed this, and does it
change what you are claiming?**
Three things, and yes, they narrowed the claims. First, the abstention
mechanism has moved past a threshold: GRAB-RAG, SURE-RAG, Certify and Sieve and
Sage all argue that a threshold is insufficient, and I have stopped calling my
gate a sufficiency judge for the reason in Q3c. Second, HALT-RAG
(arXiv:2509.07475) publishes the calibrated abstention mechanism — a NLI
ensemble with lexical signals under a precision-constrained abstention policy
— although as a post-hoc verifier it never retrieves, and its own Future Work
names live-pipeline evaluation as the critical next step. So I no longer claim
the contradiction gate is new, and I no longer claim the abstention mechanism
is new either; I claim it is a carefully instantiated one whose numeric
detector is independent of the NLI verifier, and that what the detector is
worth inside a live pipeline had not been measured.
Third, Beyond the Reranker (arXiv:2606.28367) reports that retrieval
enhancements stop paying once a strong reranker is present, and that the
reported gains come almost exclusively from homogeneous corpora, predominantly
Wikipedia prose. Mine is exactly such a corpus, so I report my effect sizes as
an upper bound for mixed-format industrial documents. What survives unchanged is
the measurement work: the candidate-pool curve, the quota's position-versus-cost
trade, and the three-way decomposition of the gate's own label.

**Q3e. What happens if the user types a nonsense question?**
Two different things can be wrong with a question, and the framework now handles
them at two different points.

*Is it a question at all?* A **runtime form check** (`src/query_form.py`) runs
before retrieval. It refuses four things: an empty query; a query with no words
in it; a query whose every word is a function word or a deictic ("what is
this?"); and a query that ends on a word that cannot end a question ("what are
units that?", "what is the cost of?"). Because it runs first, a request it
refuses costs no embedding pass, no cross-encoder pass and no model call at
all.

*Is there evidence for it?* That is the confidence gate's job, and the gate
does it to the extent the evidence allows: it refuses 23.6% of the hard genuinely-unanswerable questions
(26 of 110) — questions the corpus discusses but states no value
for — and 76.5% of the out-of-domain ones
(26 of 34), the two reported separately because they are not
the same test (§E.9). But the gate is an **evidence** gate, and it never asks
whether the query was a question. I measured that too: on the 30 malformed stems the benchmark's own generator produced and
rejected, on the six-category corpus, the gate **accepted 23 of them
(76.7%)**, at a mean posterior of 0.323
against an operating point of 0.05. So the gate is good at "is there
evidence here?" and no use at all at "is this even a question?" — which is
exactly why the two checks are separate components and not one.

The form check is measured, and the two rates are always reported together,
because the second one is the one that matters: a false rejection is a refusal
of a question the corpus could have answered, which is the one failure this
framework is built to avoid.

| population | refused |
|---|---|
| hand-authored malformed queries | 25 of 25 |
| hand-authored well-formed queries | 0 of 35 |
| corpus stems the generator rejected, hand-labelled malformed, on the focus domain | 6 of 16 (37.5%) |
| the same stems, hand-labelled well-formed | 0 of 13 |
| the benchmark's own queries, all well formed | 3 of 176 |

The counterfactual is what decided the design, and it is measured rather than
assumed. The obvious implementation is to reuse the benchmark builder's existing
`_subject_is_usable` filter, which already rejects malformed question subjects
— and it cannot be reused. That filter is a rule about *question generation*,
not about form: it rejects a subject for being one word ("FMEA"), for
containing a hyphen ("root-cause analysis"), or for ending in "-ing" ("pick and
pack warehousing"). Applied to the same well-formed stems it would have
refused **13 of 13**
(100.0%) — "What is reliability engineering?", "What is
logistics?", "What is FMEA?". On the six-category corpus the same counterfactual
refused 37 of 37. So the runtime check was written against the
query as the user typed it, and the tempting shortcut was measured first and
rejected on the numbers.

Two limits, stated because they are real. The check catches 37.5% of the malformed stems, not all of them: the rest are
truncated *clauses*, whose malformation is grammatical rather than lexical, and
catching those needs a parser or a language model — every rule that wide risks
refusing valid questions. And the check has no dictionary and no language model,
so a keyboard mash passes it; the test fixture records two such cases as
expected misses, and the check deliberately fails open on them. The honest
boundary is stated as L15 in Part H.

**Q4. Why not conformal prediction? It has actual guarantees.**
Because those guarantees require exchangeability between the calibration and test
sets, and Geißler et al. (2026) show the assumption depends on the retriever setup.
On a single-category industrial corpus of 634 chunks it does not hold. We adopt
their diagnostics as our limitation and claim only empirical calibration.

**Q5. Your dense retriever was worse than BM25. Why is that not fatal?**
Because it was a finding, not a defect — and because the framework is
instrumented well enough to act on it. `sentence-transformers/all-MiniLM-L6-v2` is a general-purpose
sentence encoder, not a retrieval-trained model, and the retrieval objective is
asymmetric in a way the sentence-similarity objective is not. The BEIR benchmark
reports the same effect — DPR zero-shot at 0.234 versus BM25 at 0.413.

The part worth saying plainly: the first version of this thesis *measured*
that and then kept the weak encoder. The ablation exists to tell you which
leg is carrying the load, so the correct response was to replace it, not to
report around it. The dense leg is now `BAAI/bge-m3`, and §C.3 reports
what that changed: The gap between the dense leg and the lexical leg closed by more than half; and the fused system now **orders better** than the lexical leg alone, which it did not before. The general lesson is the one the
framework teaches: fusion takes the *union* of two shortlists, so a weak leg
does not fail loudly — it just spends the other leg's slots. Measure the legs
separately, and do not assume a hybrid is an upgrade.

**Q6. Your reranker made recall worse. Why keep it?**
With the candidate pool it originally had, that was true — and finding out why
was the most valuable single result of the project. The reranker's effect on
recall is governed by the size of its candidate pool relative to the final
context. With a top-10 pool it cannot bring in a relevant chunk sitting at fused
rank 34, and it can only lose the one sitting at rank 12: recall@20 fell 1.000 → 1.000. With a top-50 pool the same reranker raises recall@10 from 1.000 to 0.969 (p = 3.2 × 10⁻¹) and MRR from 0.798 to 0.795.

That reframes the −5.34 pp reranker regression reported in the September 2026
report: it is not a mystery, it is a pool-size question — and the check is
cheap. I would want to run that measurement on the original code before
claiming it, which is why I present it as a hypothesis with a test rather than
as an explanation.

**Q7. The modality quota made things worse. Is D2 a failure?**
It depends on *where* it is applied, and that is the finding rather than an
excuse. On the focus domain, table recall is already at ceiling — 1.000 at
every rung, because the lexical retriever finds the table chunks on its own — so
the quota has no table gain left to buy there. Applied *before* the cross-encoder
it still moves overall recall by +0.031, because it decides which
ten the cross-encoder ranks instead of displacing one of the ten it has already
ranked; applied *after*, it costs -0.031, because it then has to
import a chunk the cross-encoder already put below the cut. On the six-category
corpus the quota has a table gain to buy — the reranker takes table recall from 0.964 down to 0.929, and the pre-rerank quota puts it back to 1.000.

Two things make that predictable rather than surprising. The corpus modality
composition is measured and reported *before* the result — this corpus is 88.8% prose — and the composition is what predicts whether the
mechanism can have any effect. And the framework's actual contribution here is
the finding that **the quota's position decides what it costs** — and that the
answer is the opposite of what the framework was designed on. Applied *before*
the cross-encoder the quota reaches table recall 1.000 and moves overall
recall by +0.031; applied *after* it, overall recall moves by
-0.031 instead, at a table recall of 1.000. The general rule,
corrected: a constraint on a downstream artefact should be enforced where it can
still choose the candidates, not where it must work against another component's
judgement.

**Q8. How do you know the contradiction detector is not just firing on everything?**
We report the prevalence, the false-positive rate *at a stated operating point*,
precision and recall, and — critically — the always-flag and never-flag baselines.
A detector that flags everything has 100% recall and 0% precision. We also
suppress revision supersession, because "Rev 3 says 187 units" and "Rev 4 says 95
units" are both true.

**Q9. Your confidence tags — how can they be wrong if they are computed, not
predicted?**
Because the tags summarise what the *retrieved context* supports, not what is true
in the world. A claim can be faithfully supported by a passage that is itself
stale. That is why every tag carries a citation, why the contradiction mechanism
partially covers staleness, and why the report lists "confidently wrong" as an
explicit limitation rather than a solved problem.

**Q10. What is the weakest part of the work?**
The empirical scale. 634 chunks, 24 documents, a 30-query calibration set, a
16-participant user study and one focus category are all below the scale at which
the statistical framing we use is well-founded. The claims are therefore framed as
*demonstration and mechanism*, not *generalisation*. And the 2026 literature is
explicit that a better retriever reduces abstention, so our threshold must be
re-fitted per retrieval configuration — which we now do and report.

**Q11. Why not just put the whole corpus in the prompt?**
That is the strongest competing approach and we take it seriously. Our corpus does
fit in a modern context window, and 2026 work reports long-context systems beating
semantic RAG in manufacturing safety at 26× the token cost. **We measured the cost
half of the comparison**: on the focus domain the corpus is 202,529
tokens against the RAG arm's 2,246. The long-context arm sends 74x more input tokens per query than the pipeline, which at the provider's cached-prefix pricing, with the corpus prefix served as a cache read on 33.0% of the long-context arm's input tokens is a 58.8x input-cost ratio rather than 74x: the token ratio and the cost ratio are different numbers, and only the second one is a cost. On the
six-category corpus the corpus exceeds the 128K window most hosted models offer but fits the 1M-token window of the generator used here. A retrieval-side proxy shows the evidence stays at the
top of the whole-corpus ranking (0.969 in the top 10 of 735), so the long-context arm's advantage would have to come
from the reader, not from the retrieval. The answer-quality half of the comparison was measured on the focus domain. With the whole corpus in the prompt the generator answered 31 of 32 answerable questions, the same coverage as the pipeline, and it declined the unanswerable questions at a comparable rate (76 of 144 against 77 of 144), for 74 times the input actually sent per query. On coverage and on cost the result is settled: the whole-corpus prompt declines no more unanswerable questions than the pipeline does and costs 74 times as much to do it. On answer quality the margin is directional but not statistically significant once the answers are scored without the length confound. The evidence
trail, the per-claim auditability and the category routing are properties our
system has.

**Q12. What would you do next, in priority order?**
(1) Repeat the generator-side comparison with a second generator, under both
prompt conditions — the cautious condition found the gate's refusals
redundant with the prompt's, and the answering condition is where it held, so
both findings currently rest on one model. (2) Repeat the long-context arm's
answer-quality comparison on the
six-category corpus, where it has not been made and where it is now feasible:
that corpus fits the 1M-token window of the generator used here. (3) Repeat the encoder swap with a second retrieval-trained
encoder and
re-measure the fusion gain. (4) Replace the LLM-annotated benchmark with
dual-expert annotation plus an LLM meta-evaluation, and report κ with a CI.
(5) Stratify the corpus by modality so D2 can be tested with adequate power, and
pre-register the power analysis. (6) Re-fit the gate threshold for every retrieval
arm, as DeclineCraft requires.

**Q13. Why did you not use a knowledge graph?**
GraphRAG and its descendants are stronger for query-focused summarisation over a
whole corpus, and they are significantly more expensive to build and maintain. For
industrial decision support the retrieval unit is a *specification fragment* — a
table row, a clause — and the thing that must be traceable is a passage, not a
subgraph. A category-level partition is coarser than community detection but is
also auditable and cheap, and it maps to how industrial documentation is actually
filed.

---

# Part H — Limitations, and the honest boundary of the claims

State these before anyone asks. A report that volunteers its limitations is
believed on the claims it does make.

| # | Limitation | Consequence for the claims | What would fix it |
|---|---|---|---|
| **L1** | The evaluation is single-domain by design — supply chain management is the focus — with the other five industrial-engineering categories retained for the cross-category transfer experiment | Generalisation beyond supply chain is **demonstrated mechanistically** and by that transfer experiment, not empirically at production scale | A licensed, multi-domain industrial corpus with the same provenance discipline |
| **L2** | Small corpus (634 chunks, 24 documents) | Results may not transfer to production-scale corpora | A larger, licensed industrial corpus |
| **L2b** | The measurements were taken on a **public substitute** corpus, because the primary corpus is proprietary and cannot be redistributed | The corpus is industrial in subject matter but not operationally binding: encyclopedia articles, not the operating manuals and standard operating procedures of a real plant. The labels are silver-standard, so absolute recall is optimistic | A licensed, expert-annotated industrial corpus with the same provenance discipline; the pipeline is corpus-agnostic and re-runs unchanged |
| **L3** | Modality composition too sparse for the quota to have power (2.3% chart, 7.1% table in the primary corpus; 5.2%/6.0% in ours) | The modality-boost null is **expected**, and is reported as such | Stratified corpus + pre-registered power analysis |
| **L4** | Cross-encoder reranking regresses on some sub-categories (−5.34 pp on `production_scheduling`) | The reranker's benefit is category-dependent | Fine-tuning the reranker on domain-matched data |
| **L5** | Contradiction detection's published ceiling on technical text is low (SciNLI 78.18% Macro-F1) | The false-positive rate is high and the reported 98% → 16% figure needs base-rate accounting | Validate the NLI leg on the industrial corpus; add the revision check |
| **L6** | User study N = 16 | Supports a within-subject sign test (≈14/16 → p ≈ 0.002) but **not** a claim about generalisation | A second industry cohort; ≥ 30 participants |
| **L7** | The benchmark is LLM-annotated (500 questions proposed) | LLM-as-judge bias (position bias flipped 66 of 80 queries in one study) may inflate scores | Dual expert annotation on a subset with κ ≥ 0.7, plus a judge meta-evaluation |
| **L8** | No LLM in the shipped pipeline's answer path | The generation-side metrics (faithfulness, citation precision) are measured against a generator-free extractive baseline | Wire in the production LLM and re-measure |
| **L9** | Long-context baseline measured on cost, and on quality for the focus domain | The long-context arm sends 74x more input tokens per query than the pipeline, which at the provider's cached-prefix pricing, with the corpus prefix served as a cache read on 33.0% of the long-context arm's input tokens is a 58.8x input-cost ratio rather than 74x: the token ratio and the cost ratio are different numbers, and only the second one is a cost. The six-category corpus exceeds the 128K window most hosted models offer but fits the 1M-token window of the generator used here, so the answer-quality half is on the focus domain because that is this thesis's domain and the two corpora are never pooled; the comparison is measured, and on this corpus it does not support a superiority claim for long-context prompting in this domain | Repeat the answer-quality comparison on the six-category corpus, which is now feasible and is the obvious next measurement |
| **L10** | Calibration is fitted per retriever, not universally — and it has to be. Measured rather than asserted: the gate was fitted separately on three retrievers and the thresholds differ — 0.05 on the shipped hybrid, 0.10 on the lexical leg alone, 0.05 on the dense leg alone — and the operating points differ with them. The hybrid's gate answers 0.938 of the answerable questions and refuses 0.361 of the unanswerable ones; the lexical gate 0.906 and 0.611; the dense gate 0.812 and 0.660. The frontier is now reported as a curve — 19 thresholds per retriever, each with its answer rate, refusal rate, abstention precision and coverage, plus the risk–coverage curve — rather than as one chosen point | A threshold fitted on one configuration is too permissive where it is transferred, and it is too permissive in the direction that flatters the configuration it is transferred to: the shipped threshold applied unchanged to the lexical leg answers 0.969 of the answerable questions against 0.906 when it is refitted, and refuses 0.340 of the unanswerable ones against 0.611. On the dense leg the two fitted thresholds coincide and the transfer costs nothing, which is the qualification — it is wrong where the thresholds differ and harmless where they do not, so no single global threshold can be justified. This is the practical form of DeclineCraft's finding that better retrieval changes the right abstention threshold | A calibration that would transfer across retrievers, which would need a retriever-independent feature rather than a calibrated score. The answer for now is the one the framework already gives: the calibration is fitted again for every retrieval stack, and the frontier is reported again with it. See `research/19_gate_per_retriever.md` |
| **L11** | The gate's label is **answer-in-context detectability**, not evidence sufficiency: the positive class is "the gold chunk is in the reranked candidate pool", and the negative class is dominated by *retrieval failure* rather than by absence of evidence | The gate cannot distinguish "there is no evidence here" from "the evidence is here and the retriever missed it", because the retrieval scores it uses are exactly the scores that failed. The literature reserves "sufficiency" for the set-level property (SURE-RAG, Certify) | A label that separates absent evidence from missed evidence — e.g. an answerability annotation on the context, independent of the retrieval scores |
| **L12** | The contradiction gate **cannot be evaluated on this corpus**, and its precision, measured against reader labels rather than against a proxy, is **0.0%** (20 labelled alarms, 95% upper bound 16.1%): two annotators that do not share a model, both blind to the detector's own scores and both 14 of 14 on a control set whose labels are known in advance, agree on the contradiction decision for 101 of the 101 pairs they labelled -- and the same readers find 0 contradictions in 80 random pairs the gate did **not** flag. The detector's own positive control is 11 of 11, so the mechanism works and this corpus does not test it; the fitted calibration therefore leaves **20 findings surfaced and 0 withheld** here |  The annotators are models rather than people, so the number says the alarms are not confirmed by a reader, not that no reader would ever confirm one | A human annotation round over the same sheet -- the instrument is built and shipped: `impl/experiments/label_contradiction_pairs.py` samples the alarms and a simple random sample of the unflagged pairs, writes a labelling sheet with the rubric attached (`impl/experiments/data/contradiction_label_rubric.md`), and scores a filled sheet into a precision and a recall with 95% intervals -- and a corpus that contains contradictions to find, which means revised procedures rather than articles about concepts, on which the conflict calibration can be re-fitted |
| **L13** | The cross-category transfer experiment is an **intra-domain** study: all six categories are industrial-engineering sub-domains, so it tests transfer between sub-domains of one domain, not between domains | The proposal's wording ("across diverse industrial sub-domains") should be read as intra-domain transfer; no claim is made about transfer to a different industry | A corpus spanning genuinely different industries, with the same protocol |
| **L14** | The framework's own hypothesis **H2.1** — that a code-level, non-bypassable gate reduces hallucination — is **supported under both prompt conditions** | The generator-side comparison was run under two prompt conditions, and the hypothesis is supported under both prompt conditions. The claim is established for one generator: the replication on a second generator could not be run, because MiniMax-M3.1-Flash returned no text on 24 of the 66 questions it was asked -- 23 of them on the benchmark's table-lookup family, against 1 of 22 on a control sample of the other families -- and 13 were rescued by a larger output budget. An empty completion is neither an answer nor a refusal, so the harness records the run as not-run instead of quoting a rate it cannot stand behind. And a refusal rate and a hallucination rate computed on generated text are different quantities, so neither is presented as the other. | Repeat the generator-side comparison with a second generator, and on the six-category corpus |
| **L16** | The benchmark's answer labels are silver-standard and mechanically derived, and an audit of the label generator found a defect in it: **27 of the 132** answerable questions carried an answer label attached to the wrong question (20.5%) -- a table question that names the column its key came from rather than the column its answer came from, and a numeric gold that is a digit prefix of a longer token in the chunk. The generator was corrected, the benchmark rebuilt and every experiment re-measured against it; the audit now finds **0** remaining defects out of 32 | The gold *chunk* was correct in every defective case, so the retrieval-side measurements were never affected and the answer-side accuracy was depressed equally for every arm; but the audit encodes two rules rather than checking every label by hand, so a defect class it does not encode would not be found, and the repair changed the answerable set, so only the post-repair numbers are comparable with one another. Separately, the long-context quality margin reaches no test's significance threshold -- not under the whole-answer entailment test, not under a length-controlled re-scoring, and not under a lexical test that ignores length -- so that comparison is directional rather than significant | Hand-check every answerable label against its gold chunk, and report the agreement rate |
| **L17** | The benchmark's **unanswerable class was separable from the question text alone** -- and the defect was found by auditing it and then repaired. A classifier that sees only the question's *shape* -- its stem, its subject size, whether the subject contains a digit, an acronym or a fabricated identifier -- tells the answerable questions from the unanswerable ones with an ROC AUC of 0.608 against a permutation null of 0.468 that the same procedure produces on shuffled labels (p = 0.050), against 0.999 before the unanswerable class was rebuilt; on the better-powered six-category benchmark, whose answerable class is four times larger, the same measurement gives 0.533 against a permutation null of 0.500 (p = 0.267) The defect was in the half's designated hard case, which asked about a fabricated identifier (`SKU AST-5454`): an identifier shape that no answerable question carried, so a single regular expression separated the classes perfectly, catching 76.4% of the class with no false positives at all. The half was rebuilt as a **corpus-anchored** class -- the same question stems, the same source documents, the same label machinery, and each repaired question given a structural twin in the answerable class (106 of 110 have one) -- and every measurement was taken again | Before the repair the headline refusal rate was an **upper bound**, measured on questions identifiable without reading the evidence. After it, the rate is measured on questions whose unanswerability is decidable only from the evidence, and the corpus-anchored stratum -- the case the gate is being tested on -- is reported separately from the trivially-unanswerable out-of-domain stratum. What remains: the repaired class is a **near-miss class**, and that is a property of a mechanically labelled benchmark rather than a defect of the repair. Its questions are ones the corpus discusses without stating the answer in the form the label standard recognises; an independent re-check found 43 of 110 whose subject the corpus comments on without defining it, so a reader could sometimes construct an answer, and 1 of 110 whose certificate does not hold at all. The refusal rate is therefore measured on a class that is partly answerable in a human's sense, which bounds what the absolute number means -- and it does not bound the arm comparison, because every arm is asked the same questions. The residual form-only separability of the repaired class is 0.608 against a permutation null of 0.468 (p = 0.050) on the focus domain, and 0.533 against a permutation null of 0.500 (p = 0.267) on the better-powered six-category benchmark. It is a small residual that the focus-domain run reaches and the better-powered run does not reproduce: small, but not zero. | Hand-check the repaired class's labels against the corpus, and repeat the audit on a second corpus whose construction differs. The audit is `impl/experiments/audit_unanswerable_class.py`, the generator is `impl/scripts/unanswerable_repair.py`, and the benchmark as it stood before the repair is preserved beside the repaired one so that the finding stays checkable |
| **L18** | **The answer-accuracy column is a property of the scoring convention as much as of the system.** The two shipped tests disagree about which arm is best, and the order reverses between the two prompt conditions. Re-scored on the *same* shipped answers under five conventions -- the two shipped ones, plus SQuAD 2.0's normalised exact match and token-level F1 and PopQA's containment rule -- the two shipped tests give opposite verdicts on between 19% and 67% of the answered questions, with Cohen's κ from 0.00 to 0.21, and the four binary conventions span up to 0.90 on one arm's answers | The accuracy column therefore cannot support a claim that the gate makes answers more accurate, and it is reported as a comparison between arms rather than as a level to be quoted. What the measurement settles is that no arm comparison on the answer side reaches significance under more than one convention: the gate-against-no-gate comparison reaches 0 of 5 in the cautious condition and 0 of 5 in the answering one. Everything the gate is actually claimed on -- the coverage, the cost, the refusal of questions it should refuse, the claim-support figures and every retrieval measurement -- is computed from counts and from the evidence rather than from the answer string, and is identical under all five conventions. See §E.8.1 and `research/18_answer_validation_conventions.md` | An LLM judge on semantic equivalence -- BrowseComp's rule, and the fifth convention in the literature -- which was not applied here; and human annotation of the benchmark's own gold answers, which is what would make one convention right rather than merely five conventions measured. No comparable benchmark reports a containment test's false-positive rate either |
| **L15** | The runtime form check is a **second** gate, not a replacement for the first. The confidence gate remains an **evidence** gate — on the 30 malformed stems the benchmark's generator produced, on the six-category corpus, the gate itself accepted 23 (76.7%) at the fitted operating point of 0.05 — while the form check, which runs before retrieval, on the focus domain refused 6 of the 16 hand-labelled malformed stems (37.5%), and refused 0 of the 13 hand-labelled well-formed ones and 3 of the 176 benchmark queries | The remaining malformed stems are truncated *clauses* — their malformation is grammatical rather than lexical — and the check has no dictionary and no language model, so a keyboard mash passes it (two such cases are recorded in the test fixture as expected misses). A request that is a broken clause rather than a broken phrase still reaches retrieval and is answered from whatever the corpus happens to contain about it | A parser or a language model for the form decision, with its own false-rejection rate measured on the same populations. The counterfactual that ruled out reusing the benchmark's own filter is measured too: it would have refused 13 of 13 well-formed stems (100.0%) |
| **L19** | **The proposal promised twelve categories and this thesis builds six of them.** The twelve-category, three-domain industrial benchmark was not built: six of the nine industrial-engineering categories were reduced to six, the three machine-learning categories -- demand forecasting, time-series forecasting and anomaly detection -- were descoped as numerical series-reasoning problems rather than document-retrieval problems, and three industrial categories -- transportation & logistics, reverse logistics and inventory management -- were descoped because the binding artefacts the proposal names are proprietary and not redistributable. The full reconciliation, with the proposal's own wording and the reason for each row, is in §A.6 and `research/12_scope_reconciliation.md` | Every claim in this thesis is about the corpora it was measured on -- a public six-category industrial corpus, its supply-chain focus subset, and an authentic federal regulatory corpus -- and none of them is about the twelve-category benchmark the proposal described. The descopings are of three kinds and are not equally excusable: three are engineering facts about what could be obtained and redistributed, three are a judgement that a category is a different problem class from the one this thesis measures, and one -- the absence of human-expert validation of the benchmark's labels -- is a cost the thesis pays knowingly and reports in this table | The extension into the machine-learning categories is the honest next measurement, and it belongs in the next-steps list rather than in the days before the defence: it needs a series corpus, series-appropriate metrics (MASE, forecast-interval coverage) and a new benchmark, and it would measure a different system from the one this thesis builds. The three proprietary industrial categories cannot exist here at all without a licensed corpus |
| **L20** | **The shipped quota placement was changed on 16 November 2026, and the ablation's ranking of the two placements is not the same on every corpus.** The system now applies the quota *before* the cross-encoder; it shipped the other placement until then, because that was the September 2026 design and moving it invalidates the gate's calibration, the generator-side comparison and the per-claim results together. The ablation's own comparison of the two placements is: on the focus domain the before-the-reranker placement reaches 1.000 Recall@10 against 0.938 after it (p = 0.157); on the six-category corpus the before-the-reranker placement reaches 0.939 Recall@10 against 0.924 after it (p = 0.480); on the industrial corpus the order reverses, the after-the-reranker placement reaching 0.988 Recall@10 against 0.980 before it (p = 0.317). **None of these differences is statistically significant at the 0.05 level (p = 0.157, 0.480, 0.317 respectively).** | The placement's effect is small everywhere and its direction is not uniform, so the shipped default is the focus domain's preference -- the largest of the differences -- rather than a rule the evidence settles. The ablation's own numbers did not move: it measures the two placements as a variable, so re-running it reproduced every rung exactly, on both Wikipedia corpora. What did move is everything that runs through the shipped retrieval -- the gate's calibration above all. 23 of the 26 measurements the deliverables quote that depend on the retrieval were re-measured with the new placement, while the per-claim band evaluation against the gold evidence, the per-claim band evaluation against the retrieved evidence and the industrial corpus's per-claim band replication were taken under the earlier placement and are the measurements this limitation covers. | Re-measure the placement on any corpus it is moved for, in the same pass as everything that depends on it |

**The three sentences that should be in the report verbatim.**

> The contributions of this work are of three kinds, and they differ in strength.
> The architectural contribution — a code-level confidence gate, a modality quota,
> hybrid retrieval with a category pre-filter, contradiction surfacing and per-claim
> tagging — is **incremental**: each component has published prior art, and we
> position ours against it explicitly rather than claiming priority. The empirical
> contribution is a **failure-mode characterisation**: on an independent corpus we
> reproduce the reranker regression, we identify the pipeline position at which a
> modality quota actually binds, and we show that the modality composition of the
> corpus, rather than the retrieval algorithm, determines whether a
> modality-aware mechanism can have any effect. The methodological contribution is
> an **evaluation protocol** — a gate evaluated as a selective-prediction policy
> with a risk–coverage curve and a false-positive rate at a stated operating
> point, with always-flag and never-flag baselines — which recent work shows is
> the minimum needed for a filter result to mean anything.

---

# Part I — The report and the paper, and how they differ

You will be asked about both. They are the same body of research presented for two
different audiences, and confusing them is a bad look.

| | **Department report** (Deliverable 3) | **Polished paper** (Deliverable 2) |
|---|---|---|
| **Audience** | The MTP review panel: Dr. Kumar, the department | A conference or journal reader who does not know you |
| **Length** | ~20–25 pages | ~9 pages IEEE / ~17 pages journal / ~20 pages technical report |
| **Front matter** | IIT Kharagpur title page with logo, certificate, table of contents, page numbers, the house border | Abstract, keywords, IEEE-style or journal-style front matter, no certificate |
| **Structure** | Numbered chapters matching the September 2026 report's table of contents, so the panel can compare directly | IMRaD, compressed, with related work as a separate section |
| **Results** | Full tables, including the null results and the limitations | The headline tables; nulls reported, not hidden |
| **Tone** | Instructional — explains the framework so the panel can assess the work | Argumentative — states a claim and defends it |
| **What it adds** | The full derivation of every formula, the code walkthrough, and the viva Q&A | The novelty statement, the literature positioning, and the reproducibility statement |

**The three formats of Deliverable 2** are the same paper reformatted:

- **Single-column technical report** — the "safe" format. Readable in any
  reviewer, no template risk, and the closest to what a thesis chapter needs.
- **IEEE two-column conference** — the standard for an ISE conference
  submission. Tight: the related work compresses, the derivations move to an
  appendix, and the space goes to the results and the novelty statement.
- **Journal (Elsevier/Scopus) style** — a structured abstract with explicit
  sections, heavier on the contribution statement and the comparison against the
  2025–2026 literature, with a formal reproducibility statement.

**Everything that is asserted in the paper is asserted in the report**, and every
number appears in both. There is one set of results.

---

# Part J — One-page glossary

Revise from this the night before.

| Term | One line |
|---|---|
| **Token** | The unit an LLM reads; usually a word-piece. |
| **Embedding** | A 1024-number vector encoding a text's meaning. |
| **Cosine similarity** | The angle between two embeddings; 1 = same direction. |
| **BM25** | Lexical ranking: IDF × saturated term frequency × length normalisation. |
| **IDF** | Log-likelihood ratio of a term appearing in a relevant vs irrelevant document. |
| **Saturation** | The tenth occurrence of a term counts far less than the first. |
| **Bi-encoder** | Encodes query and document separately; enables ANN search. |
| **Cross-encoder** | Reads query and document together; more accurate, more expensive. |
| **HNSW** | Graph-based approximate nearest-neighbour index. |
| **pgvector** | Postgres extension for vector storage and ANN search. |
| **RRF** | Rank fusion: Σ 1/(k + rank); scale-free, k = 60. |
| **Recall@k** | Fraction of the truly relevant documents found in the top k. |
| **MRR** | Mean of 1/rank of the first relevant document. |
| **nDCG@k** | Rank-and-grade metric normalised by the ideal ranking. |
| **Posterior** | P(relevant) after seeing the retrieval evidence. |
| **Likelihood ratio** | How surprising the evidence is; the engine of Bayes. |
| **Calibration** | Whether a stated probability matches the observed frequency. |
| **Platt scaling** | Fitting a logistic map from score to probability. |
| **Brier score** | Mean squared error between predicted probability and outcome. |
| **ECE** | Mean gap between confidence and accuracy, weighted by bin size. |
| **Risk–coverage** | Error rate among the most confident fraction of answers. |
| **Selective prediction** | Abstaining on low-confidence cases. |
| **Abstention precision** | Of the refusals, the fraction that were genuinely unanswerable. |
| **κ (kappa)** | Chance-corrected agreement between raters. |
| **McNemar** | Paired test for two systems on the same items, binary outcome. |
| **Wilcoxon** | Non-parametric paired test for continuous outcomes. |
| **Effect size** | How big the difference is, not just whether it exists. |
| **Power** | The probability of detecting a real effect. A null on an underpowered test is not evidence of no effect. |
| **NLI** | Entailment / neutral / contradiction between a premise and a hypothesis. |
| **Claim** | An atomic statement that can be true or false. |
| **Noisy-OR** | Combining independent witnesses: 1 − Π(1 − pᵢ). |
| **Entropy** | Uncertainty in bits; H(0.5) = 1. |
| **Information gain** | H(prior) − H(posterior): how much evidence reduced uncertainty. |
| **Faithfulness** | Fraction of claims entailed by the retrieved context. |
| **Citation precision** | Of cited claims, the fraction whose citation actually supports them. |
| **Silver labels** | Labels mechanically derived from the document, not human-annotated. |
| **Supersession** | "Rev 4 replaced Rev 3" — both statements are true; not a contradiction. |
| **Term mismatch** | Two passages share vocabulary but are about different subjects; not a contradiction. |
| **Granularity** | A whole and one of its parts; both can be true at once; not a contradiction. |
| **Measurement term** | A noun that names a measurable quantity — the key a number must be governed by to count as a quantity. |
| **Positive control** | Labelling pairs whose correct answers are known, to check the labeller rather than the detector. |
| **Blind annotation** | Labelling passages without seeing the detector's scores, so the label cannot anchor on them. |
| **Base rate** | The prevalence of the condition; without it a false-positive rate is uninterpretable. |
| **Exchangeability** | The assumption that makes conformal guarantees valid — and that fails on a single-category corpus. |

---

*Compiled 31 October 2026 for the MTP presentation. Every
identifier in this document was resolved against a live bibliographic API; every
measured number was produced by the code in `impl/`.*
