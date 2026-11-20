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
