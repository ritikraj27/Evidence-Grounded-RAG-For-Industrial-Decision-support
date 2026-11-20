# 08 — Research-Direction Check

**Scope.** Sceptical review of the MTP direction "An Evidence-Grounded Retrieval-Augmented
Generation Framework for Industrial Decision Support" (Ritik Raj, 25IM60R12, Dept. of
Industrial & Systems Engineering, IIT Kharagpur; supervisor Dr. Sri Krishna Kumar;
defence 18 November 2026).

**Check date.** 31 October 2026.

**Inputs reviewed.**

| Input | Path |
|---|---|
| M.Tech proposal | `/Users/ritikraj/Downloads/InduSight_MTP_Proposal.docx` |
| Department report (Nov 2026) | `/Users/ritikraj/Documents/MTP/deliverables/Deliverable_3_Department_Report.docx` |
| Sept 2026 framework report | `/Users/ritikraj/Downloads/RAG_Framework_Report (3) (1).pdf` |
| Implementation | `/Users/ritikraj/Documents/MTP/impl/` (`src/`, `experiments/`, `data/`, `results/`) |
| Prior literature passes in this repo | `research/00_citation_audit.md` … `research/07_frontier_2026.md` |

**Method.** Every identifier below was resolved against a live primary source on
31 October 2026: the arXiv REST API (`scripts/arxiv_search.py`), the ACL Anthology
volume indexes and `.bib` records (`scripts/acl_find.py`), and the Crossref REST API
(`scripts/crossref_resolve.py`). Nothing is cited from memory.

**Tooling limits, stated honestly.** Semantic Scholar returned HTTP 429 for this IP on
every attempt (single-record and batch), and the OpenAlex daily budget for this IP is
exhausted. **No citation counts are reported for the newly found papers.** Where
"weight" matters below, the proxy used is the venue-acceptance string in the arXiv
`comment` field, read live from the arXiv abstract page — that is a peer-review signal,
not an impact signal. ArXiv's HTML search endpoint was used for discovery (its
`searchtype=all` behaves as a strict AND, so queries were kept to two or three terms).

**Knowledge-cutoff caveat.** My own training data ends in January 2025. Essentially
everything from 2025 and 2026 in this report is therefore *new to me* and was verified
online today; I have no prior belief about these papers, and where I describe what a
paper "shows" I am reporting its abstract as retrieved, not a result I have
independently reproduced.

---

## 0. Verdict on direction

**The direction is live, but the thesis as currently framed is aimed at the weakest
version of itself.** The 2025-2026 literature has not closed on industrial RAG — if
anything it has widened, and there are now at least eight 2026 papers that do what this
thesis proposes to do at higher quality (single-domain industrial corpora, expert
annotation, and full-factorial mechanism ablations, e.g. `arXiv:2511.11847`,
`arXiv:2603.20534`, `arXiv:2605.26476`, `arXiv:2606.20898`). But the specific
*abstain* mechanism the thesis advances as D1 — a calibrated threshold on a query-level
sufficiency label — has been overtaken: the field's 2026 contribution is not "we gate on
a threshold" but "a threshold is insufficient", via set-level sufficiency verification
(`arXiv:2605.03534`), structural certificates (`arXiv:2610.34684`), graded failure modes
(`arXiv:2608.22228`), and probabilistic risk-quantified gates (`arXiv:2610.01218`). The
thesis's own numbers already reproduce the field's headline negative finding — at the
stated operating point the gate catches only **26.4%** of unanswerable queries — and the
thesis presents that as a success rather than as the finding it actually is. The
defensible thesis is not "we built a reliable gate"; it is **"we measured the reliability
mechanisms in industrial text and found which ones pay for themselves, at what price, and
exactly where they break"** — and that reframing turns the weakest parts of the current
results (weak gate, negative category filter, negative overall recall under modality
quotas, tautological contradiction recall) into the substance of the contribution.
Two things must be fixed before this is defensible: the results directory mixes
experiments computed on two different benchmark generations (§4, T0), and the
"sufficiency" label is in fact a *retrieval-success* label (§1.4), which changes what
the thesis is allowed to claim.

---

## 1. Direction check

### 1.1 What supports the direction

**a) The reliability/abstention line is expanding, not contracting.** Verified 2026 work
on the *same problem* as D1, none of which is in the repo's existing passes:

- `arXiv:2605.03534` — **SURE-RAG**: "evidence sufficiency verification for selective
  RAG"; treats sufficiency as a **set-level** property ("missing hops and unresolved
  conflicts cannot be detected by scoring passages independently"), aggregates
  per-(claim, passage) NLI relation distributions into four answer-level feature
  blocks, and emits a three-way decision with an auditable selective score.
- `arXiv:2610.34684` — **Certify**: makes sufficiency **structural** rather than
  learned — a per-query requirement hypergraph plus Horn closure yields a *certificate*
  (the minimal sufficient passages and their derivation) or an abstention naming the
  open requirements. Reports deciding "significantly more accurately than search
  agents, graph retrieval and sufficiency judges in default configurations".
- `arXiv:2604.23783` — **S2G-RAG** (ACL 2026 Main): an explicit controller that predicts
  whether the current evidence memory supports answering and, if not, emits structured
  gap items for the next retrieval turn.
- `arXiv:2609.35794` — **Sieve and Sage** (EMNLP 2026 Findings): a **lightweight module
  outside the LLM** screens the retrieved document set for distracting evidence *before*
  invoking the costly LLM — architecturally the same move as the thesis's "non-bypassable,
  code-level" gate, with a two-state failure decomposition (unanswerable vs. distracted).
- `arXiv:2609.37993` — **BITEM @ NTCIR-19 R2C2**: the confidence score is "computed by
  the orchestrator from what the run leaves behind and is never asked of the model",
  and an answer is released only once checked evidence stands behind it.
- `arXiv:2608.22228` — **GRAB-RAG** (AACL-IJCNLP 2026): graded abstention across four
  context conditions (supportive / degraded / missing / misleading).
- `arXiv:2610.01218` — **AGO AI Quality Gate**: a **stratified beta-binomial gate that
  quantifies regression risk probabilistically**, plus a mandatory meta-evaluation
  protocol for the LLM judge.
- `arXiv:2608.10406` — **Post-Calibration Reliability Reranking** (CIKM 2026): label-wise
  monotone projection of calibrated confidence onto residual risk.
- `arXiv:2604.07985` — **Predicting the Benefit of Retrieval Augmentation** (CIKM 2026):
  predicting, per query, whether retrieval will help.

**b) Industrial-domain RAG is a live, well-funded subfield with public benchmarks.**

- `arXiv:2511.11847` — multimodal **manufacturing safety** chatbot: expert-validated
  QA over three machines, **24 RAG configurations in a full-factorial design**, top-2
  evaluated by **ten industry experts and academic researchers**.
- `arXiv:2606.20898` — **Token Tax of Epistemic Accuracy**: the same group, on an
  **expert-validated benchmark of 972 answers across three machines**, comparing RAG
  against long-context prompting.
- `arXiv:2603.20534` — **industrial-scale RAG for requirements engineering** on authentic
  automotive documentation: 669 requirements across four MBN standards, 49 supplier
  qualifications, hybrid semantic-lexical MRR 0.847, expert quality assessment.
- `arXiv:2601.15434` — **ManuRAG**: multimodal manufacturing QA, 1,515 QA pairs.
- `arXiv:2605.26476` — **FAB-Bench**: semiconductor-manufacturing RAG benchmarking with
  six diagnostic metrics across four LLMs and four RAG frameworks, context windows
  4K–32K.
- `arXiv:2603.24556` — chunking strategies for RAG on **oil-and-gas enterprise
  documents** (including P&IDs), and a finding that text-only RAG is limited on
  visually/spatially encoded documents.
- `arXiv:2604.17778` — **TeleEmbedBench**: multi-corpus industrial retrieval benchmark
  (O-RAN specs, 3GPP, srsRAN code).
- `arXiv:2610.34503` — multimodal requirements traceability in **industrial** settings:
  text and image candidates retrieved **separately**, links filtered by verbalised
  confidence, evaluated on three industrial requirement sets.
- `10.18653/2026.emnlp-main.1456` — ontology-based KG construction over **industrial
  standard documents**, with the **IndusSpec-QA** dataset over three such documents.
- `10.18653/v1/2026.findings-acl.371` — **SupChain-Bench**, a peer-reviewed
  supply-chain benchmark (Findings of ACL 2026).

**c) Contradiction/conflict handling is a live area with a 2026 ACL presence.**
EMNLP 2026 alone contains `2026.emnlp-main.829` (CoVer), `.1033` (TRIAD), `.1772`
(FIDES), `.2589` (ConflictScore), `.918` (LLMs in Resolving Contextual Knowledge
Conflicts), `.539` (CoRECT), `.2293` (Twin Worlds: Equivariance-Based Abstention for
Evidence-Grounded Reasoning). `arXiv:2507.21544` (MAGIC, EMNLP 2025 Findings) is a
purpose-built inter-context-conflict benchmark; `arXiv:2509.23233` (EMNLP 2025 Main)
contributes **WIKICOLLIDE**, the first benchmark of *real* Wikipedia inconsistencies,
and reports that **at least 3.3% of English Wikipedia facts contradict another fact** —
directly relevant to a Wikipedia-derived corpus.

**d) Cross-encoder candidate-pool effects are a known but under-measured phenomenon.**
`arXiv:2504.13128` (FreshStack, NeurIPS 2025) reports "cases where rerankers do not
improve first-stage retrieval accuracy (two out of five topics)". `arXiv:2606.28367`
("Beyond the Reranker") reports that "a strong cross-encoder reranker accounts for most
of the pipeline's quality". Neither publishes the *recall-versus-pool-size curve* the
thesis's Experiment 5 produces, so that measurement remains available.

### 1.2 What undercuts the direction

**a) The strongest 2026 evaluation of RAG retrieval-enhancement attacks exactly the
thesis's D2 and D3.** `arXiv:2606.28367` ("Beyond the Reranker") evaluates eight
enhancement methods (query expansion, hierarchical/cross-document summarization,
graph expansion, per-query routing, rank fusion, corrective re-retrieval) on a
heterogeneous benchmark with **chunker-agnostic span-overlap relevance labels and
collection-disjoint splits**, and finds only query expansion and one calibrated
per-source method yield reliable gains beyond a strong reranker. Its framing sentence
is aimed straight at this thesis: the benefits reported for RAG enhancements "come
almost exclusively from homogeneous corpora, predominantly Wikipedia prose." The
thesis's corpus *is* homogeneous Wikipedia prose, so the thesis's D3 gain sits in
exactly the regime where published gains are known to be inflated, and D2's quota sits
exactly where the published evidence says enhancements stop paying.

**b) The thesis's own data already contradicts H2.3.** From
`impl/results/exp1_ablation.md`: hybrid+RRF+rerank R@10 = **0.730**; adding the
category pre-filter drops it to **0.653**. The category pre-filter costs 7.7 points.
H2.3 as currently worded ("hybrid … preceded by category filter … outperforms flat
retrieval") is not supported by the thesis's own ablation. This is a finding, not a
bug — but it must be stated as the finding.

**c) Reranking has been shown to *degrade* abstention.** `arXiv:2610.28340`
(DeclineCraft, 27 LLMs): "Adding query rewriting and reranking to hybrid (dense &
sparse) retrieval lowers CAR for all 12 models tested." The thesis's D1 gate sits
*downstream* of a cross-encoder, so the operating point is arm-dependent. The thesis's
own transfer experiment shows exactly this: tau fitted on the tuning half is **0.05**
while the full-set operating point is **0.10** — a factor-of-two shift from changing
the retrieval arm.

**d) Detection is not resolution.** `arXiv:2605.27157` ("Detecting Is Not Resolving:
The Monitoring Control Gap in Retrieval Augmented LLMs", 50,000+ turn-level evaluations
across four model families): models "readily acknowledge contradictory evidence, yet
this awareness fails to constrain their final recommendations", and
"contradiction acknowledgement is uncorrelated with safe resolution". H2.4 ("surfacing
contradictions … improves practitioner decision accuracy") is directly threatened.

**e) Long-context is a live alternative architecture.** `arXiv:2606.20898` reports
long-context prompting ahead of RAG on some manufacturing-safety axes at a token cost.
The thesis's corpus is 46 documents / 2,592 chunks, and the focus corpus is 14
documents — both plausibly fit in a modern context window. A reviewer will ask whether
RAG is the right architecture for the corpus at all.

**f) The benchmark's labelling standard is contested in the literature.** `arXiv:2610.08026`
("The Labeling Problem in Hallucination Detection Benchmarks", **NeurIPS 2026
Evaluations & Datasets Track**, DOI `10.7910/DVN/PCHISZ`) uses 900 human-labelled
QA pairs to show that automated labelers "may apply [reference faithfulness] even when
the intended target is [factual correctness]". The thesis's benchmark is
`label_standard: "silver"`. `arXiv:2610.33849` adds a second attack: query-time RAG
poisoning defences "can measure benchmark construction rather than filtering", and
"12 of 21 published evaluations report no FPR at their operating point".

**g) Entropy-only confidence tagging is explicitly contested.** `arXiv:2603.21172`
("Entropy Alone is Insufficient for Safe Selective Prediction in LLMs") bears directly
on the thesis's D5 entropy component.

### 1.3 The four specific sub-questions, answered

**(i) Has the "abstain / no-evidence" literature advanced past a simple threshold gate?**
**Yes — decisively, and in three named directions.**

1. *Set-level sufficiency instead of per-passage relevance.* `arXiv:2605.03534`
   (SURE-RAG) and `arXiv:2610.09348` ("Relevance Is Not Sufficiency") both argue that
   scoring passages independently cannot detect sufficiency; S2G-RAG
   (`arXiv:2604.23783`) and Certify (`arXiv:2610.34684`) build sufficiency into the
   retrieval loop.
2. *Structural certificates instead of learned thresholds.* Certify
   (`arXiv:2610.34684`) derives a Horn-closure certificate from a requirement
   hypergraph; "Given correct retrieval, requirements and links, the decision is sound,
   and complete up to the entity check." A thesis that offers Platt scaling will be
   asked why it does not offer a certificate.
3. *Graded failure modes instead of one binary.* GRAB-RAG (`arXiv:2608.22228`)
   separates *missing* from *misleading* evidence and reports that models "abstain when
   context is absent, not when it is misleading" — under explicit abstention prompting
   they still answer **41.6%** of misleading questions, with **63%** of those answers
   echoing the planted wrong entity verbatim; a generator-side conflict check cuts that
   to 13.3% but discards many correct answers, "while an NLI verifier recovers that
   coverage but fails when [the evidence is missing]".

The thesis's benchmark already contains the corresponding taxonomy — 110 of its 384
queries are `unanswerable_near_miss` and 34 are `unanswerable_ood`. The thesis's own
gate result (26.4% of unanswerables refused at tau = 0.10) is a *reproduction of
GRAB-RAG's headline finding in a new domain*. That is a publishable result. It is not a
success result, and the report currently presents it as the latter.

**(ii) Has anyone published the JOINT NLI-plus-same-subject contradiction gate?**
**Not in the packaged form the thesis uses.** I searched arXiv (11 query formulations,
2-3 terms each, over the contradiction / conflict / knowledge-conflict / NLI-contradiction
space) and the ACL Anthology 2025-2026 volumes (needles: `contradiction`, `conflict`,
`abstention`, `selective prediction`, `refusal`, `industrial`, `manufacturing`,
`supply chain`). No paper was found that publishes *NLI-contradiction AND
(cosine similarity OR entity/number overlap), at chunk-pair level, with an independent
numeric-conflict detector and a revision-supersession check, in an industrial RAG
system*. But every conjunct is published separately, and one paper packages most of
the mechanism:

- `arXiv:2509.07475` — **HALT-RAG**: a feature set derived from **an ensemble of two
  frozen NLI models *and* lightweight lexical signals**, fed to a **calibrated,
  task-adapted meta-classifier**, deployed under a **precision-constrained decision
  policy** that yields an abstention. That is, functionally, *NLI ∧ lexical-same-subject,
  calibrated, with abstention* — the union of the thesis's D1 and D4.
- `arXiv:2609.35782` — **Financial Evidence Crowding**: a learned score correction
  combining **fixed relevance score + typed compatibility + local lexical competition**,
  with a **query-level identity gate** applying the correction. This is the
  thesis's "same-subject confirmation + non-bypassable gate" in a financial QA setting.
- `arXiv:2607.25959` — **Kontrast**: a taxonomy of cross-modal knowledge inconsistencies
  that explicitly separates *direct conflicts* from *information-granularity differences*,
  *temporal changes*, and *KG incompleteness* — i.e. the thesis's supersession check
  and its "granularity difference is not contradiction" concern, already formalised, on
  Wikipedia/Wikidata.
- `arXiv:2609.07075` — **Hierarchical Consistency Framework**: a post-hoc, model-agnostic
  audit at three levels (corpus, retrieved context, answer), representing corpus
  conflicts as **source-linked atomic facts** and returning an **Answer Consistency
  Score** with supporting and contradictory statements.
- `arXiv:2609.16301` (CLEAR), `arXiv:2605.17301` (ConflictRAG),
  `2026.emnlp-main.829` (CoVer), `2026.emnlp-main.2589` (ConflictScore),
  `2026.emnlp-main.918` — the rest of the conflict-resolution and conflict-typing field.

**Conclusion for D4:** the *conjunction* is unpublished, but the conjunction is a
composition of published mechanisms, and the two closest packages (HALT-RAG, Financial
Evidence Crowding) already cover "calibrated NLI+lexical gate" and "typed-compatibility
+ lexical-competition + query-level gate" respectively. The thesis's remaining D4 claim
should be narrowed to: *an industrial instantiation in which the numeric-conflict
detector is independent of the NLI verifier and the supersession check is explicit* —
which then **must** be evaluated against human labels, because the current evaluation
cannot distinguish its own detector from its own ground truth (§4, T2).

**(iii) Has anyone published the finding that a modality quota only binds when applied
downstream of a component that could undo it?** **Not with that framing, but the
substantive claim is published, in the modality-RAG context, by name.**

- `arXiv:2607.05438` — **"Modality Relevance is not Modality Utility: Post-hoc
  Selective Modality Escalation for Cost-Aware Multimodal RAG"**: "We show that this is
  the wrong decision point." Pre-retrieval modality routing over-escalates relative to
  an oracle; the fix is a **post-hoc** intervention inside a fixed pool. This is the
  thesis's D2 ordering claim, in the modality-RAG literature, 2026.
- `arXiv:2609.35782` — **Financial Evidence Crowding**: the *displacement mechanism*
  the thesis's numbers exhibit: "conflicting candidates consume limited context slots and
  displace answer-supporting evidence", with **Recall@10 reduced by 0.147** relative to
  equally difficult compatible pools.
- `arXiv:2606.29328` — **GeoRAG**: "single-point, query-proximity scorers cannot cover
  multi-modal demands, exposing a structural limit of ranking-based selection" — the
  theoretical case for coverage-based (quota) selection over top-k.
- `arXiv:2610.03421` — **CLIMB** (EMNLP 2026 Findings): builds a complementary evidence
  pool with an MMR-style objective *and* performs confidence-controlled refinement
  *within that fixed pool* — again, the "decide after the pool is fixed" architecture.

So: the thesis's measured trade (post-rerank quota buys +6.3 points of table recall for
−8.1 points of overall R@10; pre-rerank quota buys the same table recall for −16.2) is
a *new measurement in a new setting* of a *published mechanism*. It is worth publishing
as a measurement, but it cannot be presented as a novel architectural insight.

**(iv) Has anyone published that cross-encoder rerank recall is governed by candidate-pool
size, and that a pool the size of the final context cannot improve recall?** **No — I
found no paper that publishes this as a headline finding.** The nearest published results
are *corroborating* rather than *pre-empting*: FreshStack (`arXiv:2504.13128`) reports
rerankers that fail to improve first-stage retrieval on 2 of 5 topics; "Beyond the
Reranker" (`arXiv:2606.28367`) reports that a strong reranker accounts for most of
pipeline quality; T²-RAGBench (`arXiv:2506.12071`) finds Hybrid BM25 (dense+sparse
fusion) most effective for text-and-table data. **Experiment 5 is the most genuinely
publishable, least pre-empted measurement in the thesis**, and it is currently the
least discussed (§4, T5/T7).

### 1.4 A naming problem in D1 that a reviewer with the code will catch first

The "query-level sufficiency label" is defined in `impl/experiments/run_gate.py` as:

```python
label = 1 if gold and (gold & set(cid for cid, _ in scored)) else 0
```

where `scored` is the **reranked candidate pool**. Therefore the label is exactly:

> *1 iff the gold chunk is present in the retrieved context (and a gold chunk exists).*

That is a **retrieval-success label**, not an evidence-sufficiency label. Unanswerable
queries (empty gold) are label 0 by construction; answerable queries whose gold was
missed are *also* label 0 and are indistinguishable from unanswerable ones by the
features. The gate is therefore doing what `arXiv:2604.07985` and `arXiv:2608.26379`
do — predicting whether the answer is in the context — and not what the thesis calls it.
Two consequences:

1. **The claim must be renamed.** "Evidence sufficiency" → "answer-in-context
   detectability" / "retrieval-success detection". The literature explicitly reserves
   "sufficiency" for the set-level property (`arXiv:2610.09348`, `arXiv:2605.03534`),
   so the current name reads as an incorrect claim of prior art.
2. **The reported base rate is mis-stated in the report.** `impl/results/exp2_gate.json`
   records `base_rate_sufficient_evidence = 0.429` and `retriever_recall_of_gold =
   0.707`. The correct decomposition, given `n_queries = 366` (222 answerable + 144
   unanswerable): **157 of 222 answerable queries (70.7%) have their gold chunk in the
   retrieved pool; 65 answerable queries (29.3%) do not.** The gate is therefore being
   asked to separate {157 answerable-found} from {65 answerable-missed ∪ 144
   unanswerable} = 209. **Two thirds of the negative class is retrieval failure, not
   absence of evidence.** Every statement in the thesis about "the corpus contains no
   evidence" must be re-checked against this.

---

## 2. Prior art per mechanism D1–D4

| Mechanism | Prior art? | Citation | What it pre-empts | Verdict |
|---|---|---|---|---|
| **D1** — code-level, non-bypassable retrieval-confidence gate; calibration on a query-level sufficiency label; risk–coverage curve; always-flag/never-flag baselines; stated operating point | **Yes — the architecture and the framing are published; the specific label is not** | `arXiv:2609.35794` (EMNLP 2026 Findings) | A lightweight module screens the retrieved set *before* the LLM is invoked and the LLM abstains — the same non-bypassable, code-level, pre-LLM placement. | **Pre-empted as architecture.** |
| | | `arXiv:2609.37993` (NTCIR-19 R2C2) | Confidence computed by the orchestrator, "never asked of the model"; answer released only when checked evidence stands behind it. | **Pre-empted as architecture.** |
| | | `arXiv:2610.34684` | Sufficiency made *structural* via Horn-closure certificates; beats sufficiency judges in default configurations. | **Pre-empts the learning-based alternative.** |
| | | `arXiv:2605.03534` | Set-level sufficiency verification; 3-way decision; auditable selective score. | **Pre-empts per-passage sufficiency claims.** |
| | | `arXiv:2610.09348` | "Relevance Is Not Sufficiency"; blinded judgement over the retrieved set; Gold Hit / Turn Hit as coverage proxies ≈ the thesis's sufficiency label. | **Pre-empts the label.** |
| | | `arXiv:2604.07985` (CIKM 2026) | Predicting per query whether retrieval will help; selective retrieval. | **Pre-empts the decision problem.** |
| | | `arXiv:2608.10406` (CIKM 2026) | Post-hoc calibration of relevance decisions + residual-risk reranking. | **Pre-empts the calibration methodology.** |
| | | `arXiv:2610.01218` | Stratified beta-binomial gate with probabilistic regression-risk quantification + mandatory judge meta-evaluation. | **Pre-empts the risk-quantified gate.** |
| | | `arXiv:2604.20854` | Dirichlet belief masses over internal vs. external knowledge; Dempster-Shafer conflict measure for abstention. | **Pre-empts the "two-source confidence" variant.** |
| | | `arXiv:2609.37993`, `arXiv:2609.35794` (above) + `arXiv:2610.28340` | DeclineCraft measures CAR across 27 LLMs; shows reranking *lowers* CAR for all 12 models tested. | **Pre-empts the benchmark** and constrains the operating point. |
| | | `10.18653/v1/2024.emnlp-main.527` (SYNCHECK, EMNLP 2024) | Token-level faithfulness monitoring; FOD decoding beats abstention by >10%. | **Already known; still the sharpest challenge.** |
| | | `arXiv:2509.07475` (HALT-RAG) | Calibrated NLI ensemble + lexical signals + precision-constrained abstention. | **Pre-empts D1+D4 jointly.** |
| | | `arXiv:2610.34684` + `arXiv:2608.22228` | Certificates and graded failure modes. | **Pre-empts the "threshold is enough" framing.** |
| | | **Net for D1** | — | What remains genuinely unpublished: (a) a *query-level* detectability label (rather than passage-level) calibrated on a **held-out** split and reported as a risk–coverage curve *with* always-answer/always-refuse baselines **in an industrial corpus**; (b) the explicit **falsification** of the gate by the near-miss unanswerable family, reproducing GRAB-RAG's finding in a new domain; (c) the demonstration that the operating point is **arm- and corpus-specific** (tau 0.05 vs 0.10 across arms, 0.05 vs 0.10 on tuning vs. full set). | **Narrow but real. Reframe D1 as "answer-in-context detectability + a published negative result", not "evidence sufficiency".** |
| **D2** — per-modality retrieval quotas over text/table/chart chunks, applied BEFORE or AFTER the cross-encoder reranker | **The mechanism is published; the ordering comparison is not** | `arXiv:2607.05438` | "We show that this is the wrong decision point" (pre-retrieval modality routing); proposes **post-hoc** intervention within a fixed pool. | **Directly pre-empts the ordering claim in the modality-RAG setting.** |
| | | `arXiv:2609.35782` | Constraint-induced displacement: conflicting/incompatible candidates consume top-k slots and displace answer-supporting evidence; **Recall@10 −0.147**. | **Pre-empts the trade-off mechanism.** |
| | | `arXiv:2606.29328` | Top-k ranking structurally cannot cover multi-modal demands (facility-location / submodular objective with a 1−1/e guarantee). | **Pre-empts the theoretical justification for quotas.** |
| | | `arXiv:2610.03421` (CLIMB, EMNLP 2026 Findings) | Complementary-evidence pool + confidence-controlled refinement *inside* the fixed pool. | **Pre-empts the "intervene after the pool" architecture.** |
| | | `arXiv:2606.28367` | Retrieval enhancements stop paying once a strong reranker is present. | **Pre-empts the "quota adds on top of the reranker" expectation.** |
| | | `arXiv:2607.25959` (Kontrast) | Taxonomy separating cross-modal conflict from granularity difference and temporal change. | **Pre-empts the D4/diagnostic side.** |
| | | `arXiv:2601.15434` (ManuRAG), `arXiv:2412.10704` (VisDoM), `arXiv:2506.12071` (T²-RAGBench) | Multimodal / text-and-table industrial QA with modality-specific evaluation. | **Already known.** |
| | | **Net for D2** | — | Unpublished: a *controlled, same-budget* comparison of the same quota applied pre- vs. post-reranker on an industrial corpus, reporting the full Pareto trade (overall R@10 vs. table R@10) rather than a single number. The thesis's data show the trade is *strictly dominated* in one direction — but the thesis currently reports it as a win. | **Keep, but reframe as a measured trade-off, not a gain.** |
| **D3** — hybrid BM25 (hand-implemented) + dense all-MiniLM-L6-v2, fused by RRF, category pre-filter, then a cross-encoder reranker | **Yes — standard practice, thoroughly benchmarked** | `arXiv:2606.28367` | Eight enhancements on a shared backbone with a strong reranker: only query expansion and one calibrated method give reliable gains beyond it; gains reported on Wikipedia prose do not transfer to mixed-format corpora. | **Pre-empts the whole assembly.** |
| | | `arXiv:2604.01733` | Ten retrieval strategies incl. cross-encoder reranking on 23,088 text-and-table queries; hybrid+rerank best (R@5 0.816); **BM25 beats dense on financial documents**. | **Pre-empts the pipeline and the hybrid claim.** |
| | | `arXiv:2506.12071` (T²-RAGBench, EACL 2026) | 23,088 triples; **Hybrid BM25 (dense+sparse) most effective for text-and-table**; expert-validated 91.3% context-independent. | **Pre-empts the fusion choice.** |
| | | `arXiv:2504.13128` (FreshStack, NeurIPS 2025) | Rerankers do not improve first-stage retrieval on 2 of 5 technical topics. | **Corroborates the thesis's own reranker regression.** |
| | | `arXiv:2604.17778` (TeleEmbedBench) | LLM-based embedders significantly beat sentence-transformers; domain instructions help code but *hurt* natural-language specs. | **Threatens the all-MiniLM-L6-v2 choice.** |
| | | `arXiv:2601.15457`; `arXiv:2210.11934` (TOIS, DOI `10.1145/3596512`) | Chunking/retrieval/re-ranking policy-document QA; systematic fusion-function comparison. | **Already known.** |
| | | **Net for D3** | — | D3 is not a contribution. Worse, the thesis's own ablation shows the category pre-filter **costs 7.7 R@10 points**, which is a finding in line with `arXiv:2606.28367`'s message but in the opposite direction from H2.3's wording. The *one* publishable D3 element is the pool-size curve (§1.3-iv). | **Demote D3 to "the pipeline in which the other mechanisms are measured". Report the category-filter regression as a finding.** |
| **D4** — joint gate: NLI contradiction AND same-subject confirmation (cosine OR entity/number overlap), plus an independent numeric-conflict detector and a revision-supersession check | **Components: yes. The conjunction as packaged: no** | `arXiv:2509.07475` (HALT-RAG) | NLI ensemble ∧ lexical signals → calibrated meta-classifier → precision-constrained abstention. | **The closest single pre-emption of the whole mechanism.** |
| | | `arXiv:2609.35782` | Typed compatibility + local lexical competition + query-level identity gate. | **Pre-empts "same-subject confirmation + non-bypassable gate".** |
| | | `arXiv:2607.25959` (Kontrast) | Cross-modal inconsistency taxonomy: direct conflict vs. granularity difference vs. temporal change vs. incompleteness. | **Pre-empts the supersession/granularity distinction.** |
| | | `arXiv:2509.23233` (EMNLP 2025 Main) | CLAIRE + **WIKICOLLIDE**: corpus-level inconsistency detection on Wikipedia with editor-in-the-loop; ≥3.3% of English Wikipedia facts contradict another fact. | **Pre-empts the Wikipedia-corpus inconsistency framing and supplies a benchmark.** |
| | | `arXiv:2609.07075` (HCF) | Three-level (corpus / context / answer) consistency audit with source-linked atomic facts and an Answer Consistency Score. | **Pre-empts the multi-level audit.** |
| | | `arXiv:2604.14227` (FRESCO) | Rerankers show "a strong bias toward older, semantically rich documents, even when they are factually obsolete", using **Wikipedia revisions** — i.e. the supersession problem, on the same corpus family. | **Pre-empts the supersession check's ground.** |
| | | `arXiv:2605.03534` | "unresolved conflicts" as a set-level property that independent passage scoring cannot detect. | **Pre-empts the pairwise-only design.** |
| | | `arXiv:2604.25313` (Faithfulness-QA) | 99,094 counterfactual entity-substitution samples creating controlled knowledge conflicts between context and parametric memory. | **Pre-empts the conflict-synthesis methodology.** |
| | | `arXiv:2605.17301`; `2026.emnlp-main.829`; `2026.emnlp-main.1033`; `2026.emnlp-main.1772`; `2026.emnlp-main.2589`; `2026.emnlp-main.918`; `arXiv:2609.16301` | Conflict detection/typing/resolution and conflict-scoring across a dense 2026 field. | **The field is crowded; the thesis must cite it explicitly.** |
| | | **Net for D4** | — | The conjunction is not published, but (a) HALT-RAG already publishes NLI+lexical+calibration+abstention; (b) Kontrast already publishes the temporal/granularity taxonomy; (c) FRESCO already publishes the Wikipedia-revision recency problem. The thesis's D4 novelty reduces to *an industrial instantiation with an NLI-independent numeric detector*, and that can only be defended with human-labelled precision/recall, which the current experiment cannot provide (§4, T2). | **Narrow. Must be re-evaluated against human labels.** |

---

## 3. Single-domain focus — recommendation

### 3.1 Does the literature support a single-domain industrial RAG evaluation?

**Yes, strongly — and single-domain deep evaluations are the dominant form in the
2025-2026 industrial RAG literature.** Verified single-domain precedents:

| Paper | Scope | Depth of the evaluation |
|---|---|---|
| `arXiv:2511.11847` | Machine safety (3 machines) | 24 RAG configurations, full-factorial; 10 industry experts + academics on the top 2 |
| `arXiv:2606.20898` | Machine safety (same corpus) | 972 expert-validated answers, 2 SLMs × 3 grounding architectures |
| `arXiv:2603.20534` | Automotive requirements engineering | 669 requirements / 4 MBN standards / 49 supplier qualifications; expert quality assessment |
| `arXiv:2601.15434` | Manufacturing principles & practice | 3 datasets, 1,515 QA pairs |
| `arXiv:2605.26476` | Semiconductor manufacturing | 200 QA pairs, 6 diagnostic metrics, 4 LLMs × 4 RAG frameworks, 4K–32K contexts |
| `arXiv:2603.24556` | Oil & gas enterprise documents | 4 chunking strategies on a proprietary corpus incl. P&IDs |
| `arXiv:2610.34503` | Industrial requirements traceability | 3 non-overlapping industrial requirement sets |
| `10.18653/2026.emnlp-main.1456` | Industrial standards | IndusSpec-QA over 3 industrial standard documents |
| `10.18653/v1/2026.findings-acl.371` | Supply chain | Peer-reviewed (ACL Findings 2026) |

**Conversely, multi-domain evaluation is also a live norm** (`arXiv:2607.12310`
LakeQuest, three domains, 9,846 human-validated QA pairs, COLM 2026;
`arXiv:2604.22239` MuDABench, Findings of ACL 2026; `arXiv:2506.12071`;
`arXiv:2607.03028`). **The literature therefore does not say multi-domain is now
required.** It says the two designs are both acceptable, and that the *depth* of the
mechanism evaluation is what distinguishes them.

### 3.2 The reviewer objection is not "you need six categories"

It is three narrower, sharper objections:

1. **A generalisation claim cannot be supported by one domain.** The thesis's RO4/H4.1
   *is* the generalisation claim. A single-domain thesis cannot make it, and H4.1 as
   written ("configurations tuned on a subset of industrial categories transfer zero-shot
   to held-out categories") is *literally unimplementable* under a single-domain scope.
   Note also that all six of the thesis's categories — `predictive_maintenance`,
   `production_scheduling`, `supply_chain_management`, `quality_engineering`,
   `reliability_engineering`, `facility_layout` — are **industrial-engineering
   sub-domains**. So H4.1 is an **intra-domain** transfer claim. It should be renamed
   accordingly; a reviewer who notices this will trust the rest of the framing more,
   not less.
2. **The corpus is the real problem, not the domain count.** The 2026 single-domain
   papers all use *authentic* regulatory, manual, or standard documents
   (`arXiv:2511.11847`, `arXiv:2603.20534`, `arXiv:2603.24556`, `arXiv:2606.07401`).
   The thesis's corpus is **46 (focus: 14) Wikipedia articles**. No 2026 paper claims
   "industrial decision support" from a Wikipedia-derived corpus. The reviewer objection
   is: *"your corpus is encyclopaedic prose about industrial engineering; it contains no
   procedures, no control plans, no maintenance logs, no supplier documents — the things
   the word 'industrial decision support' refers to."* This objection applies equally
   at six categories. Narrowing the domain does not fix it.
3. **A single-domain "before/after" is only meaningful if the corpus is authentic.**
   With a Wikipedia corpus, the before/after demonstrates that the pipeline works on
   Wikipedia-derived QA. That is a fine paper; it is not industrial decision support.

### 3.3 The focus benchmark as currently built cannot carry the headline

From `/Users/ritikraj/Documents/MTP/impl/data/benchmark_focus/benchmark.json`:

| Property | Focus (supply chain) | Full (6 categories) |
|---|---|---|
| Queries | 213 | 384 |
| Answerable | **69** | 240 |
| Unanswerable | **144** (67.6%) | 144 (37.5%) |
| `table_lookup` queries | **9** | 32 |
| `definition` | 43 | 146 |
| `numeric_fact` | 17 | 62 |

Three problems: (a) **n = 69 answerable queries** cannot support a modality-quota claim
(9 table-lookup queries) or a calibration claim; (b) **all 144 unanswerable queries are
inherited** from the multi-category set (`unanswerable_near_miss` 110 + `unanswerable_ood`
34) rather than being supply-chain-specific, so the focus set's gate statistics are
dominated by a class that is not about supply chain at all; (c) the focus gate artefact
`impl/artifacts_focus/gate_model.json` has `tau = 0.05` and `base_rate = 0.277` — a
**different** operating point from the full set's 0.10 — with `fitted_on.n_queries = 213`,
i.e. the reported focus operating point was selected on the same queries it is evaluated
on, and a reviewer will note that the artefact's own metadata reports all 213 queries
as the fitting set.

### 3.4 Recommendation

**Do not drop RO4. Re-scope, don't subtract.**

1. **Keep the six-category corpus exactly as it is, as the *generalisation* study.** It
   is built, it is cheap, and it is the only evidence for H4.1. Rename H4.1 to
   "intra-domain (industrial-engineering sub-domain) transfer" and state explicitly that
   all six categories lie inside one domain.
2. **Make the single-domain supply-chain corpus the *depth* study** — a full-factorial
   mechanism ablation (the same 24-configuration-style design as `arXiv:2511.11847`) on
   one domain, with the before/after demonstration. This is the study that a committee
   will find convincing, and it is the design the 2026 literature has validated.
3. **Rebuild the focus benchmark to be supply-chain-native:**
   - raise answerable supply-chain queries to **≥ 150** (target ≥ 2× current), and
     raise `table_lookup` to **≥ 32** to match the multi-category set, so the modality
     claim has the same power as the generalisation claim;
   - generate **supply-chain-specific** unanswerable queries (wrong company, wrong part
     family, wrong Incoterm, out-of-date policy) rather than inheriting near-miss
     queries from other categories, and keep the inherited ones as a *second* class so
     the near-miss effect remains measurable;
   - **re-fit the gate per corpus** and report the operating point on the held-out half
     only (§4, T3/T4). Per DeclineCraft (`arXiv:2610.28340`) the operating point is
     arm- and corpus-dependent; a single global tau will manufacture a spurious result.
4. **Swap in authentic supply-chain documents for at least part of the corpus.** This is
   the single highest-value change available and it is cheap: public regulatory and
   standard documents (OSHA, EPA, FAR, Incoterms, ISO/EN standards summaries, MBN
   9666) are freely usable, and `arXiv:2610.34503`, `10.18653/2026.emnlp-main.1456`
   and `arXiv:2606.07401` show exactly how to annotate them. Even 10-15 authentic
   documents would let the thesis claim an authentic-domain result while retaining the
   Wikipedia set as the scale corpus.
5. **If the time budget allows only one choice, choose the single domain — but only with
   an authentic corpus and a rebuilt benchmark.** A six-category thesis on a Wikipedia
   corpus is the weakest available option: it has the widest claim, the thinnest
   evidence per category (n = 24 for `facility_layout`), and the least credible corpus.

**If authentic documents cannot be obtained in time:** keep the Wikipedia corpus, retitle
the thesis's domain claim to *"industrial engineering encyclopaedic text"* (or *"long-tail
industrial topics"*), remove every "decision support" claim that depends on documents a
practitioner would actually use, and state the corpus limitation in the abstract. This
is a smaller thesis, but it is a defensible one.

---

## 4. Threats to the thesis

### 4.0 Status, 11 November 2026

**This list was written on 31 October 2026 and its `Already answered?` column is a
snapshot of that date.** It is left as written, because a threat list that is
edited after the fact is a threat list nobody can audit. This is the record of
what has happened to each of them since.

| # | Status now | Closed by |
|---|---|---|
| T0 | **Closed** | The results are split by corpus (`impl/results_focus/`, `impl/results_industrial/`), the focus run was re-run on the current benchmark, and `impl/scripts/verify_reported_numbers.py` now re-derives every quoted number from the artefacts and fails the build on a mismatch. |
| T1 | **Partly closed** | The hypothesis was re-stated as a negative result, and the pre-filter is a no-op on the focus corpus and Δ 0.000 (p = 1.000) on the industrial one. **Still open:** the soft-prior alternative was never tried. |
| T2 | **Closed** | The branch composition is reported — semantic, revision and quantity, each with its own precision and recall — and the gate is scored against reader labels rather than against the proxy that made the 1.000 a tautology. |
| T3 | **Closed** | The full risk–coverage curve is reported against true never-refuse and always-refuse baselines, and the operating-point rule is stated rather than chosen by inspection. |
| T4 | **Closed** | Transfer is reported at matched coverage rather than at a matched threshold, and the threshold's failure to transfer is now a finding: a threshold fitted on a weaker configuration is too permissive on a stronger one. |
| T5 | **Closed** | R@20 is measured on the pre-truncation list. The industrial sweep reports R@20 = 1.000 against R@10 = 0.988 at pool 50 — a difference the dead metric could not have shown. |
| T6 | **Closed** | The label is *answer-in-context detectability* throughout, and the papers say why the word *sufficiency* is not used. |
| T7 | **Partly closed** | The pool-size dependence is measured, and the reranker does help on the industrial corpus (Δ +0.028, p = 0.020). **Still open:** the 2×2 over a second, stronger reranker was never run. |
| T8 | **Closed for the focus domain** | The long-context arm is measured on cost and on answer quality. **Still open:** the quality half on the six-category corpus — next-steps item 2. |
| T9 | **Closed** | The encoder was replaced with a retrieval-trained multilingual encoder (`research/09_encoder_swap.md`), and the operating point's non-portability across corpora became a finding rather than a defect. |
| T10 | **Closed in the sense that the comparison now exists** | The second corpus is authentic and binding (the eCFR), and the encyclopaedic-versus-authentic comparison is reported: the negative findings replicate on it. **Still open:** plant-floor procedural text, and other jurisdictions. |
| T11 | **Partly closed** | The unsupported claim was removed — the labels are described as silver-standard throughout, and the annotation is disclosed as model-generated with its agreement statistics beside it. **Still open:** human dual annotation — next-steps item 3. |
| T12 | **Closed** | Per-category intervals, the matched-coverage framing and the minimum-detectable-effect caveat are reported; the industrial corpus adds 247 answerable queries. |
| T13 | **Closed** | H2.4 was re-labelled a formative study and the hypothesis wording removed. |
| T14 | **Closed** | The Pareto frontier is figure 4, and the operating point that maximises table recall subject to a stated overall-recall loss is reported. |
| T15 | **Closed** | The per-branch counts and precisions are in the results files and in the papers. |
| T16 | **Partly closed** | The generator-side comparison measures a prompt-conditioned decline arm, always- and never-refuse baselines and a matched random-escalation control. **Still open:** a token-level faithfulness monitor in the SYNCHECK style. |

**Four threats are partly closed and each names what is still open.** Everything
marked *closed* is closed by an artefact in this repository, not by an argument.


| # | Threat | Already answered? | Experiment needed |
|---|---|---|---|
| **T0** | **The results directory mixes two benchmark generations.** `impl/results/exp1_ablation.json` records `n_queries = 384`; `exp2_gate.json` records **366**; `exp5_pool_size.json` records **366**. File mtimes: corpus files 14:06, benchmark 14:11, index 14:12; exp1 re-run 14:54; exp2 07:25, exp4 07:47, exp5 08:37, exp3 09:09. **The gate, transfer and pool-size results were computed on a different corpus and benchmark from the ablation they are compared against in the report.** | **No — this is the highest-severity issue and it is a reproducibility defect, not a hypothesis.** | Re-run **all five** experiments on the current corpus/benchmark via `impl/scripts/rerun_all.sh`, and regenerate every table in the report from those artefacts. Then diff against the numbers currently in `deliverables/`. Cross-table statements such as "the quota raises table R@10 from 0.906 to 0.969 [exp1] while the pool-50 configuration gives R@10 0.653 [exp5]" are currently not comparisons on the same data and must be re-checked. |
| **T1** | **The category pre-filter costs 7.7 R@10 points** (exp1: 0.730 → 0.653), contradicting H2.3's wording. | **No.** The hypothesis as written is contradicted by the thesis's own data. | Re-state H2.3 as a negative-result hypothesis: *"a hard metadata category pre-filter is a recall liability on a small multi-category corpus."* Test the paired difference on the 240 answerable queries with a paired bootstrap and a McNemar test on per-query hits; report the CI. Then test the fix: replace the hard filter with a soft prior (e.g. a category-boosted RRF term) and report whether it recovers the 7.7 points while keeping the cross-category benefit. If it does not, the negative result stands and should be the claim. |
| **T2** | **The D4 headline "joint gate recall on verifiable conflicts = 1.000" is a tautology.** In `impl/experiments/run_contradiction.py`, the verifiable subset is `f.numeric_conflicts` non-empty, while `f.flagged = (f.flagged and not superseded) or bool(f.numeric_conflicts)` — the numeric detector is an OR-branch of the gate, so the gate flags every verifiable conflict by construction. | **No.** The report's own note says the proxy precision/recall "are against an NLI-derived label and are therefore not independent of the detector" — but the headline table still presents 1.000 as a result. | Hand-label a stratified random sample: **150 flagged pairs + 150 unflagged pairs** drawn from the 14,535 compared, against a written rubric that separates *contradiction* from *granularity difference*, *temporal supersession*, *term mismatch*, and *different scope*. Report precision/recall/F1 with CIs on those labels, plus the decomposition: NLI∧topical alone, numeric alone, and their union. Target: **precision ≥ 0.80 at recall ≥ 0.80** for the joint gate; report the base rate (342 / 14,535 = **2.35%**) alongside, since precision at a 2.35% base rate is the number that decides usability. |
| **T3** | **The gate catches only 26.4% of unanswerable queries at the stated operating point** (tau = 0.10, coverage 0.883, abstention precision 0.884). 73.6% of out-of-corpus queries still receive an answer. | **No.** | Report the full risk–coverage curve against a **true** never-refuse baseline (tau = 0) and a true always-refuse baseline (tau = 1). The current table's "always_answer_baseline" is tau = 0.05 (it refuses 4.9% of unanswerables — 7 queries — and reports abstention precision 1.000 on that basis, which is a degenerate artefact, not a baseline). Decide the operating point against an explicit utility criterion (e.g. cost of a false answer vs. cost of a refusal) rather than "highest tau answering ≥ 90% of answerable queries", and state the criterion. If no operating point achieves ≥ 0.70 refusal at ≥ 0.80 coverage, publish the negative result and cite `arXiv:2608.22228` as the independent corroboration it is. |
| **T4** | **The cross-category transfer "succeeded" because the fitted threshold degenerated.** tau fitted on the tuning half = **0.05**, the loosest threshold in the sweep, which refuses only 4.9% of unanswerable queries. Transferring a near-never-abstain gate is not transfer. | **No.** | Report the operating-point sweep **separately** for the tuning and held-out halves, and report transfer at a **matched coverage** rather than a matched threshold: for each target coverage c ∈ {0.80, 0.85, 0.90}, report the held-out unanswerable-refusal rate at the threshold that achieves c on the tuning half, with a CI. Also report the retrieval-metric transfer (exp4's R@10 per category) separately from the gate transfer — those are different claims. Note the per-category n: `facility_layout` n = **11** in the held-out half; at n = 11 no significance statement about transfer is possible. Either add queries to the small categories or state the minimum detectable effect at each n. |
| **T5** | **`R@20` is a dead metric.** `impl/src/pipeline.py:319` truncates `reranked_ids` to `top_k_final = 10` before evaluation, so `recall_at_k(run, rel, 20)` is identical to `recall_at_k(run, rel, 10)` for every row — visible as `R@20 == R@10` in every table in `impl/results/`. | **No.** | Either evaluate on the pre-truncation list (pool sizes 50/100) or delete the R@20 column. A 5-minute change; a checker reading the code will find it immediately and it undercuts every table it appears in. |
| **T6** | **The "sufficiency" label is a retrieval-success label** (§1.4), and the negative class is 2/3 retrieval failure rather than absent evidence. | **No.** | Rename the label and re-derive every base rate from the 2×2 contingency: answerable/unanswerable × found/not-found. Then re-state what the gate detects: *answer-in-context detectability*, not evidence sufficiency. The key number to publish is the gate's ability to separate *{answerable, found}* from *{answerable, missed}* alone — that is the honest version of "the retriever knows when it missed", and it is a measurable, publishable quantity. |
| **T7** | **The reranker contributes almost nothing and sometimes subtracts.** FreshStack (`arXiv:2504.13128`) independently reports rerankers that fail to improve first-stage retrieval on 2 of 5 technical topics; the thesis's own note records a 5.34-point regression on `production_scheduling`. | **Partly — the effect is documented but not bounded.** | Run a **2 × 2 reranker ablation**: {`cross-encoder/ms-marco-MiniLM-L6-v2`, one larger/stronger reranker} × {pool 10, pool 50, pool 100}, plus a no-rerank arm, on the current benchmark. Report the pool curve per reranker. The claim to defend is the *pool-size* result, not the reranker — but the reranker must be shown not to be the confound. |
| **T8** | **Long-context is a credible alternative architecture** (`arXiv:2606.20898` on a comparable manufacturing corpus). | **No.** | Add a **long-context arm**: feed the entire corpus (focus: 14 documents; full: 46) to the same generator and measure the same three axes (answer correctness, hallucination rate, decision quality). The gate's value is then the *marginal* gain over long-context at equal cost. Without this arm, the reviewer can reasonably argue that the whole pipeline is unnecessary. |
| **T9** | **The embedder is a 2022 model and the reranker a 6-layer MiniLM.** TeleEmbedBench (`arXiv:2604.17778`) finds LLM-based embedders significantly beat sentence-transformers, and that domain instructions help code but *hurt* natural-language specification retrieval — which is exactly the thesis's corpus. | **No.** | Re-run the ablation with one modern embedder (e.g. Qwen3-Embedding or BGE-M3) as a sensitivity check, and re-fit the gate's features on the new scores. Expect the gate's coefficients (currently `top1_rerank` +4.69, `mean_top3_rerank` −3.53 — a non-monotone fit on ~94 positive calibration cases) to change materially. If they do, the operating point must be re-derived, which is itself a reportable result: *the calibrated operating point is not portable across embedders.* |
| **T10** | **The corpus is encyclopaedic, not industrial.** The 2026 industrial literature uses authentic regulatory, manual, standard, and maintenance documents. | **No.** | Either (a) add 10–15 authentic supply-chain documents (public regulatory/standard sources) with the same query-generation and annotation protocol, and report the mechanism ablation separately on encyclopaedic vs. authentic sub-corpora — **this comparison alone would be a strong paper**, because it directly tests whether the thesis's findings are corpus artefacts; or (b) retitle the domain claim and drop "decision support" from the abstract. |
| **T11** | **The benchmark labels are silver-standard** (`label_standard: "silver"`), and `arXiv:2610.08026` (NeurIPS 2026 Evaluations & Datasets Track) shows automated labelers systematically conflate reference faithfulness with factual correctness, using 900 human-labelled pairs. | **No — the report claims dual expert annotation with κ, and none of it is visible in the artefacts.** | Dual-annotate a stratified random sample of **120 queries** (60 answerable / 60 unanswerable, stratified across the 5 families) by two annotators with industrial-engineering competence; report Cohen's κ; adjudicate disagreements; and — critically — **hold the annotation set out of the gate's calibration split** so the reported calibration metrics are not computed on annotated-and-fitted data. |
| **T12** | **Small-N statistics throughout.** 384 queries; per-category n as low as 24 (`facility_layout`) and 11 in exp4's held-out half. | **No.** | Report per-category CIs, choose the test by data type (McNemar for paired binary hits, bootstrap for recall differences, Wilcoxon signed-rank for per-query metric shifts), and state the **minimum detectable effect** at each n so the reader can see what "no significant degradation" does and does not license. |
| **T13** | **The N = 16 user study behind H2.4.** | **No.** | Pre-register the effect size and the primary outcome before running, or re-label H2.4 as a **formative** qualitative study and remove the hypothesis wording. A committee will ask for a power analysis; there is no honest way to power 16 participants for a decision-accuracy difference. |
| **T14** | **The modality quota's cost is not stated.** exp1 shows the quota raises table R@10 from 0.906 to 0.969 (+6.3) but lowers overall R@10 from 0.730 to 0.649 (−8.1) post-rerank and to 0.568 (−16.2) pre-rerank. | **No.** | Sweep the quota and report the **Pareto frontier** (overall R@10 vs. table R@10, one point per quota setting). State the operating point that maximises table R@10 subject to overall R@10 loss ≤ 2 points. If that point does not exist, say so: *"at this corpus size a modality quota does not pay for itself."* That is a legitimate and quotable result, and it aligns with `arXiv:2609.35782`'s displacement mechanism and `arXiv:2607.05438`'s decision-point argument. |
| **T15** | **The D4 gate's composition is unknown.** The joint gate flagged 674 of 14,535 pairs; NLI-only flagged 1,224. Because the numeric detector is OR-ed in, an unknown share of the 674 is numeric-detector hits rather than NLI∧topical hits — so "the joint gate" may be mostly the numeric detector. | **No.** | Report the 2×2 decomposition (NLI∧topical ∧ numeric, each separately and the union) with counts, so the contribution of each conjunct is visible. This is a table, not an experiment, and it must exist. |
| **T16** | **The contrast with SYNCHECK and prompt-based abstention is asserted, not measured.** SYNCHECK (EMNLP 2024) reports FOD decoding beating abstention by over 10%; `arXiv:2608.22228` reports prompt-based abstention answering 41.6% of misleading questions. | **No.** | Implement at least one competing policy on the same benchmark and the same contexts: (a) an LLM-prompted "say I don't know" instruction, and (b) a token-level faithfulness monitor in the SYNCHECK style if time allows. Report the three policies on one risk–coverage plot. This is the single experiment that converts D1 from "we built a gate" into "we compared a gate to the alternatives". |

---

## 5. Benchmark landscape

Sizes and annotation types are taken from abstracts and publisher records retrieved live
on 31 October 2026, except where explicitly marked. "Not stated in abstract" means the
figure is not in the abstract and I did not open the full text — treat those as
unverified, not as zero.

| Benchmark | Size | Domain | Annotation | Identifier | Link |
|---|---|---|---|---|---|
| **T²-RAGBench** | 23,088 question–context–answer triples | Real-world text-and-table (financial/business documents) | Transformed from SOTA datasets into context-independent form; **expert-validated at 91.3%** context-independence | arXiv:2506.12071; EACL 2026, DOI `10.18653/v1/2026.eacl-long.8`, pp. 165–191 | https://aclanthology.org/2026.eacl-long.8/ |
| **FreshStack** | 5 datasets (fresh/niche technical topics) | Code + technical documentation | Automatic: corpus collection → nugget generation from community Q&A → nugget-level support via hybrid retrieval | arXiv:2504.13128; NeurIPS 2025, DOI `10.52202/085713-5255`, pp. 174653–174681 | https://arxiv.org/abs/2504.13128 |
| **TeleEmbedBench** | 9,000 question–chunk pairs over 3 corpora (O-RAN specs, 3GPP, srsRAN code) — *size from this repo's earlier verified pass, not re-verified today* | Telecommunications | Automated two-stage LLM pipeline (generate → validate), **no expert annotation** | arXiv:2604.17778 | https://arxiv.org/abs/2604.17778 |
| **Manufacturing safety chatbot benchmark** | Expert-validated QA over 3 machines; 24 RAG configurations tested; top-2 reviewed by 10 industry experts + academics | Machine / occupational safety | **Expert validation**; industry-expert evaluation | arXiv:2511.11847 | https://arxiv.org/abs/2511.11847 |
| **Token Tax of Epistemic Accuracy** benchmark | **972 answers**, 3 machines, 2 SLMs, 3 grounding architectures | Manufacturing safety | **Expert-validated** | arXiv:2606.20898 | https://arxiv.org/abs/2606.20898 |
| **Industrial-scale RAG for requirements engineering** | 669 requirements across 4 MBN standards (2015–2023) + 49 supplier qualifications | Automotive requirements engineering | Authentic industrial documents; **expert quality assessment** | arXiv:2603.20534 | https://arxiv.org/abs/2603.20534 |
| **ManuRAG** | 3 datasets, **1,515 QA pairs** (mathematical, MCQ, review-based) | Manufacturing principles and practice | Dataset-native QA construction | arXiv:2601.15434 | https://arxiv.org/abs/2601.15434 |
| **FAB-Bench** | **200 QA pairs** curated from >1,300 generated candidates; 3 synthesis strategies | Semiconductor manufacturing | Curated + diagnostics (6 metrics) across 4 LLMs × 4 RAG frameworks, 4K–32K contexts | arXiv:2605.26476 | https://arxiv.org/abs/2605.26476 |
| **RealDocBench** | **1,356 field-level QA** over 581 documents (4 domains incl. supply-chain logistics) + **1,500 human-verified page images** with COCO-style boxes | Regulated real-world documents (mortgage, financial reporting, supply-chain logistics, clinical) | Typed gold dictionaries; **human-verified layout annotation** | arXiv:2606.07401 | https://arxiv.org/abs/2606.07401 |
| **SupChain-Bench** | Not stated in the record I retrieved | Supply chain management | Peer-reviewed benchmark (not re-checked for annotation method) | Findings of ACL 2026, DOI `10.18653/v1/2026.findings-acl.371`, pp. 7526–7550 | https://aclanthology.org/2026.findings-acl.371/ |
| **LakeQuest** | **9,846 QA pairs**, 3 domains (AI/ML metadata, retail banking, multimodal biomedical drug info) | Enterprise/scientific data lakes | **Human-validated**, with **modality-aware evidence pointers** | arXiv:2607.12310; COLM 2026 | https://arxiv.org/abs/2607.12310 |
| **ChartWalker-Bench** | Not stated in abstract | Cross-chart analytical QA (scientific, business, political) | Generated from a hierarchical knowledge graph with structure-aware sampling | arXiv:2606.23997 | https://arxiv.org/abs/2606.23997 |
| **MuDABench** | **80,000+ pages, 332 analytical QA instances** | Financial / large semi-structured document collections | Distant supervision from document metadata + annotated financial databases | arXiv:2604.22239; Findings of ACL 2026 | https://arxiv.org/abs/2604.22239 |
| **HETERQA** | Not stated in abstract | Record retrieval over multiple heterogeneous sources | Not checked | arXiv:2607.03028 | https://arxiv.org/abs/2607.03028 |
| **MAGIC** | Not stated in abstract | Inter-context knowledge conflicts | KG-generated conflicts with explicit relational structure | arXiv:2507.21544; EMNLP 2025 Findings | https://arxiv.org/abs/2507.21544 |
| **WIKICOLLIDE** (with CLAIRE) | "The first benchmark of real Wikipedia inconsistencies"; **≥ 3.3% of English Wikipedia facts contradict another fact** | Wikipedia | CLAIRE-assisted analysis + **human annotation**; editor user study | arXiv:2509.23233; EMNLP 2025 Main | https://arxiv.org/abs/2509.23233 |
| **SpecRead v2.1** | **385 questions** over 10 OpenTitan IP blocks + 82 controls (41 distractor, 41 consistent-RTL) | Hardware specification documents | Type-4 items built from **real RTL mutations verified by Icarus Verilog simulation**; with-spec/without-spec ablation | arXiv:2609.33699 | https://arxiv.org/abs/2609.33699 |
| **HetDocQA** (inside "Beyond the Reranker") | Not stated in abstract | Heterogeneous mixed-format corpora (code, markdown, tables, scientific PDFs, prose) | **Chunker-agnostic span-overlap relevance labels; collection-disjoint splits** | arXiv:2606.28367 | https://arxiv.org/abs/2606.28367 |
| **Faithfulness-QA** | **99,094 samples**; entity bank of 76,953 entities, 8 types | SQuAD + TriviaQA, counterfactual entity substitution | 100% pass on four automated checks; 200-sample audits | arXiv:2604.25313 | https://arxiv.org/abs/2604.25313 |
| **DeclineCraft** | 27 LLMs × 40 model×thinking configurations; unanswerable questions target Minecraft feature additions after a corpus cut-off | General (gaming/parametric-knowledge probe) | Deliberate cut-off design + **audits of possible parametric exposure** | arXiv:2610.28340 | https://arxiv.org/abs/2610.28340 |
| **GRAB-RAG** | Paired benchmark, NQ + HotpotQA, **4 context conditions** (supportive, degraded, missing, misleading); 5 abstention policies × 3 models (3.8B–8B) | General QA | Controlled construction: gold passages edited to support a wrong answer | arXiv:2608.22228; AACL-IJCNLP 2026 | https://arxiv.org/abs/2608.22228 |
| **ExpertQA** | **2,177 questions from 484 participants across 32 fields** | Long-tail expert domains (general, incl. professional fields) | **Expert-curated questions; expert-evaluated responses; verified answers and per-claim attributions** | NAACL 2024, DOI `10.18653/v1/2024.naacl-long.167`, pp. 3025–3045 | https://aclanthology.org/2024.naacl-long.167/ |
| **IndusSpec-QA** (inside the industrial-standards ontology paper) | 3 industrial standard documents (QA size not stated in abstract) | Industrial standards | Ground truth from the standards | EMNLP 2026, DOI `10.18653/2026.emnlp-main.1456` | https://aclanthology.org/2026.emnlp-main.1456/ |
| **SParK-Eval** | Size not stated in abstract | Industrial records for domain-adaptive pretraining | QA pairs annotated by **input structure** (sentence / table / list) | Findings of ACL 2026, DOI `10.18653/v1/2026.findings-acl.1221` | https://aclanthology.org/2026.findings-acl.1221/ |

**Expert-annotated industrial / supply-chain benchmarks specifically** — the ones a
reviewer will name, in order of how directly they undercut the thesis's benchmark claim:
`arXiv:2511.11847` and `arXiv:2606.20898` (972 expert-validated answers on machine
safety — the closest comparator), `arXiv:2603.20534` (automotive RE with expert
assessment), `arXiv:2605.26476` (semiconductor), `10.18653/v1/2026.findings-acl.371`
(SupChain-Bench, peer-reviewed), `10.18653/2026.emnlp-main.1456` (IndusSpec-QA),
`arXiv:2606.07401` (RealDocBench, incl. supply-chain logistics), `arXiv:2607.12310`
(LakeQuest, human-validated). **Three of these are expert-annotated in an industrial or
supply-chain domain**, so the proposal's residual claim ("no public benchmark spans
multiple industrial-engineering sub-domains with dual expert annotation, a reported κ,
per-claim attribution labels, and a deliberate unanswerable class") must be re-checked
against this table and narrowed to exactly what survives.

### 5.1 Identifier corrections found during this check

Three identifiers circulating in secondary sources or in this repository's own notes are
wrong or stale, and should be fixed before submission:

1. **ExpertQA is not `arXiv:2402.15049`.** That arXiv ID resolves to *"The use of
   Specutils by Data Central"* (an astronomy poster). ExpertQA's canonical identifier is
   the NAACL 2024 DOI `10.18653/v1/2024.naacl-long.167`, and its **published** title is
   *"ExpertQA: Expert-Curated Questions and Attributed Answers"* — not "A Benchmark of
   Informative and Trustworthy Answers from Long-Tailed Expert Domains", which is the
   preprint title.
2. **T²-RAGBench's published title changed.** The arXiv preprint is *"T2-RAGBench:
   Text-and-Table Benchmark for Evaluating Retrieval-Augmented Generation"*; the EACL
   2026 version of record is *"T2-RAGBench: Text-and-Table Aware Retrieval-Augmented
   Generation"*. `research/02_modality_balanced.md` currently pairs the arXiv title with
   the EACL DOI — a mismatch a copy-editor will catch.
3. **SupChain-Bench, not "SupplyChain-Bench."** The ACL Anthology title (and the
   Crossref record) read *"{S}up{C}hain-Bench: Benchmarking Large Language Models for
   Real-World Supply Chain Management"*. Note the ACL Anthology's 2026 EMNLP DOI scheme
   has **no `/v1/` segment** (`10.18653/2026.emnlp-main.<n>`), unlike every other volume.

---

## 6. Recommended positioning statement

*For the viva. Six sentences; every claim in it is supported by a number you already
have or can produce.*

> My thesis measures which reliability mechanisms actually pay for themselves in
> industrial text, rather than proposing a new mechanism — and its central result is a
> negative one that the 2026 literature has only begun to name. I built a query-level
> gate that refuses to answer when the retrieved context does not contain the answer,
> calibrated on a held-out split and reported as a risk–coverage curve against
> always-answer and always-refuse baselines; at the operating point that preserves 97.7%
> of answerable queries it catches only 26.4% of unanswerable ones, because the
> retrieval scores it uses cannot separate "no evidence exists" from "evidence exists
> but the retriever missed it" — the same failure that GRAB-RAG and DeclineCraft report
> for model- and prompt-based abstention, reproduced here in an industrial corpus. My
> second result localises where a modality quota binds: applied before the cross-encoder
> it is dominated by the same reranker that later reorders it, and applied after it buys
> 6.3 points of table recall at a cost of 8.1 points of overall recall, so the quota is
> a trade and not a gain — the displacement mechanism is published
> (Financial Evidence Crowding), but the controlled pre-versus-post measurement in this
> setting is not. Third, I show that cross-encoder recall is governed by the candidate
> pool rather than by the reranker: with a pool equal to the final context size the
> reranker is net-harmful, and recall saturates only beyond the pool this corpus
> supports — this is the one measurement in the thesis that I do not believe has been
> published. Fourth, I characterise what these mechanisms cannot do: contradictions are
> detected far more reliably than they are resolved, which agrees with the
> monitoring-control gap reported in "Detecting Is Not Resolving", and a hard category
> pre-filter costs 7.7 recall points, which I believe is the most transferable negative
> result in the work. Finally, I release the benchmark, its labelling protocol, the
> per-query failure taxonomy, and the full ablation, so the negative results are
> reproducible — because my contribution is a measurement contribution, and its value is
> that it says which reliability mechanisms pay for themselves in industrial text, at
> what price, and exactly where they break.

---

## 7. Sources

Every identifier below was resolved on 31 October 2026. The verification route is
noted per entry.

### arXiv (resolved via arXiv API / abs page, this session)

- arXiv:2504.13128 — FreshStack: Building Realistic Benchmarks for Evaluating Retrieval on Technical Documents — NeurIPS 2025
- arXiv:2506.12071 — T2-RAGBench: Text-and-Table Benchmark for Evaluating Retrieval-Augmented Generation (preprint title; published title differs)
- arXiv:2507.21544 — MAGIC: A Multi-Hop and Graph-Based Benchmark for Inter-Context Conflicts in Retrieval-Augmented Generation — EMNLP 2025 Findings
- arXiv:2509.07475 — HALT-RAG: A Task-Adaptable Framework for Hallucination Detection with Calibrated NLI Ensembles and Abstention
- arXiv:2509.23233 — Detecting Corpus-Level Knowledge Inconsistencies in Wikipedia with Large Language Models — EMNLP 2025 Main
- arXiv:2511.11847 — A Multimodal Manufacturing Safety Chatbot: Knowledge Base Design, Benchmark Development, and Evaluation of Multiple RAG Approaches
- arXiv:2601.15434 — ManuRAG: Multi-modal Retrieval Augmented Generation for Manufacturing Question Answering
- arXiv:2603.20534 — An Industrial-Scale Retrieval-Augmented Generation Framework for Requirements Engineering: Empirical Evaluation with Automotive Manufacturing Data
- arXiv:2603.21172 — Entropy Alone is Insufficient for Safe Selective Prediction in LLMs
- arXiv:2603.24556 — Evaluating Chunking Strategies For Retrieval-Augmented Generation in Oil and Gas Enterprise Documents — CCSEIT 2026
- arXiv:2604.01733 — From BM25 to Corrective RAG: Benchmarking Retrieval Strategies for Text-and-Table Documents
- arXiv:2604.07985 — Predicting the Benefit of Retrieval Augmentation in Open-Domain Question Answering — CIKM 2026
- arXiv:2604.14227 — FRESCO: Benchmarking and Optimizing Re-rankers for Evolving Semantic Conflict in Retrieval-Augmented Generation
- arXiv:2604.20854 — ERA: Evidence-based Reliability Alignment for Honest Retrieval-Augmented Generation
- arXiv:2604.22239 — Navigating Large-Scale Document Collections: MuDABench for Multi-Document Analytical QA — Findings of ACL 2026
- arXiv:2604.23783 — S2G-RAG: Structured Sufficiency and Gap Judging for Iterative Retrieval-Augmented QA — ACL 2026 Main
- arXiv:2604.25313 — Faithfulness-QA: A Counterfactual Entity Substitution Dataset for Training Context-Faithful RAG Models
- arXiv:2605.03534 — SURE-RAG: Sufficiency and Uncertainty-Aware Evidence Verification for Selective Retrieval-Augmented Generation
- arXiv:2605.05244 — Towards Dependable Retrieval-Augmented Generation Using Factual Confidence Prediction
- arXiv:2605.17301 — ConflictRAG: Detecting and Resolving Knowledge Conflicts in Retrieval Augmented Generation
- arXiv:2605.26476 — FAB-Bench: A Framework for Adaptive RAG Benchmarking in Semiconductor Manufacturing
- arXiv:2605.27105 — Lost in the Evidence? Reproducing Document Position and Context Size Effects in RAG — SIGIR 2026
- arXiv:2605.27157 — Detecting Is Not Resolving: The Monitoring Control Gap in Retrieval Augmented LLMs
- arXiv:2606.01613 — TechRAG: Evidence-Gated Multimodal Agentic RAG for Technical Literature Reasoning
- arXiv:2606.07401 — RealDocBench: A Benchmark for Field-Level QA and Layout Understanding on Real-World Regulated Documents
- arXiv:2606.20898 — The Token Tax of Epistemic Accuracy: Comparing RAG and Long-Context Architectures for Document-Grounded Generative AI Applications
- arXiv:2606.28367 — Beyond the Reranker: Do RAG Retrieval Enhancements Help Once a Strong Reranker Is Present?
- arXiv:2606.29328 — Covering the Unseen: Information Demand Coverage Optimization for Retrieval-Augmented Generation
- arXiv:2606.34503 — Multimodal Requirements Traceability Link Recovery in Industrial Settings — APSEC 2026
- arXiv:2607.03028 — HETERQA: Benchmarking Record Retrieval over Multiple Heterogeneous Sources
- arXiv:2607.05438 — Modality Relevance is not Modality Utility: Post-hoc Selective Modality Escalation for Cost-Aware Multimodal RAG
- arXiv:2607.12310 — LakeQuest: A Three-Domain Benchmark for Grounded Question Answering across Data Lakes — COLM 2026
- arXiv:2607.25959 — Detecting Knowledge Inconsistencies Across Text, Tables, and Knowledge Graphs (Kontrast)
- arXiv:2608.10406 — Post-Calibration Reliability Reranking of Relevance Decisions via Label-wise Monotone Projection — CIKM 2026
- arXiv:2608.22228 — Prompt-Based Abstention Fails Under Misleading Context: A Controlled Study of Small Frozen RAG Models — AACL-IJCNLP 2026
- arXiv:2608.29175 — An Explainable Coherence Score for Detecting Temporal Inconsistencies in Political News
- arXiv:2609.04442 — GRACE: Graph-Grounded Reflective Agent Copilot Engine for Expert-in-the-Loop Knowledge Expansion — AKBC @ EMNLP 2026
- arXiv:2609.07075 — A Hierarchical Consistency Framework for Auditing Retrieval-Augmented Generation Systems
- arXiv:2609.09348 — Relevance Is Not Sufficiency: What Actually Closes the Evidence Gap in Long-Term Memory QA
- arXiv:2609.16073 — The Immutable Past: Formalizing State Mutability and Conflict Resolution in Mutable RAG
- arXiv:2609.16301 — CLEAR: Cross-Source Evidence Adjudication for Large Language Models in Medicine
- arXiv:2609.33699 — SpecRead: A Benchmark for Measuring Whether Language Models Understand Hardware Specifications
- arXiv:2609.35782 — Financial Evidence Crowding: Diagnosing and Mitigating Constraint-Induced Displacement in Retrieval-Augmented Generation
- arXiv:2609.35794 — Sieve and Sage: Efficient Distraction Filtering for Reliable RALM Abstention — EMNLP 2026 Findings
- arXiv:2609.37993 — BITEM at the NTCIR-19 R2C2 Task: Predicting Confidence from Agentic RAG Pipeline Signals
- arXiv:2610.01218 — AGO AI Quality Gate: Evidence-First Release Decisions for Retrieval-Augmented Generation — NFMCP 2026
- arXiv:2610.03421 — CLIMB: Confidence-Guided Complementary Evidence for Multimodal Retrieval-Augmented Generation — EMNLP 2026 Findings
- arXiv:2610.08026 — The Labeling Problem in Hallucination Detection Benchmarks: An Empirical Evaluation — NeurIPS 2026 Evaluations & Datasets Track
- arXiv:2610.28340 — DeclineCraft: A RAG Abstention Benchmark for Jointly Measuring Combined Retrieval and Parametric Knowledge
- arXiv:2610.33849 — Ranking Is Not Deciding: Benchmark Shortcuts and Operating-Point Collapse in Query-Time RAG Poisoning Defenses
- arXiv:2610.34684 — Knowing When the Evidence Is Enough: Requirement-Directed Search with Horn-Closure Certificates
- arXiv:2610.36915 — Do We Need an LLM to Know Why Sources Conflict? Decision Models for Knowledge-Conflict Typing in RAG

### DOIs — ACL Anthology and Crossref (resolved this session)

- 10.18653/v1/2024.naacl-long.167 — ExpertQA: Expert-Curated Questions and Attributed Answers — NAACL 2024, pp. 3025–3045
- 10.18653/v1/2024.emnlp-main.527 — Synchronous Faithfulness Monitoring for Trustworthy Retrieval-Augmented Generation (SYNCHECK) — EMNLP 2024, pp. 9390–9406
- 10.18653/v1/2025.emnlp-main.67 — Think Wider, Detect Sharper: Reinforced Reference Coverage for Document-Level Self-Contradiction Detection — EMNLP 2025
- 10.18653/v1/2026.eacl-long.8 — T2-RAGBench: Text-and-Table Aware Retrieval-Augmented Generation — EACL 2026, pp. 165–191
- 10.18653/v1/2026.findings-acl.1221 — SParK-Eval: Evaluating Structure-Aware Knowledge Acquisition in LLMs for Domain Adaptation to Industrial Records — Findings of ACL 2026
- 10.18653/v1/2026.findings-acl.371 — SupChain-Bench: Benchmarking Large Language Models for Real-World Supply Chain Management — Findings of ACL 2026, pp. 7526–7550
- 10.18653/2026.emnlp-main.161 — To Answer or to Abstain: Mitigating Search-Agent Hallucinations via Abstention-Aware Reinforcement Learning — EMNLP 2026, pp. 3696–3718
- 10.18653/2026.emnlp-main.539 — CoRECT: Context-Aware Logit Contrast for Hidden State Rectification to Resolve Knowledge Conflicts — EMNLP 2026
- 10.18653/2026.emnlp-main.549 — LLM Abstention Can Be a Prompt Artifact, in Addition to Genuine Uncertainty — EMNLP 2026, pp. 12612–12633
- 10.18653/2026.emnlp-main.829 — CoVer: Conflict-aware Claim Verification — EMNLP 2026
- 10.18653/2026.emnlp-main.918 — Large Language Models in Resolving Contextual Knowledge Conflicts — EMNLP 2026, pp. 21142–21169
- 10.18653/2026.emnlp-main.1033 — TRIAD: A Three-Axis Framework for Knowledge Conflict Resolution in RAG — EMNLP 2026
- 10.18653/2026.emnlp-main.1456 — Ontology-Based Knowledge Graphs for Industrial Standards with Scope-Aware Logical Rule Structuring (introduces IndusSpec-QA) — EMNLP 2026
- 10.18653/2026.emnlp-main.1772 — FIDES: Faithful Inference via Deep Evidence Signals for Retrieval-Memory Conflict in RAG — EMNLP 2026
- 10.18653/2026.emnlp-main.2293 — Twin Worlds: Equivariance-Based Abstention for Evidence-Grounded Reasoning — EMNLP 2026, pp. 52170–52188
- 10.18653/2026.emnlp-main.2589 — ConflictScore: Identifying and Measuring How Language Models Handle Conflicting Evidence — EMNLP 2026, pp. 58825–58845
- 10.52202/085713-5255 — FreshStack: Building Realistic Benchmarks for Evaluating Retrieval on Technical Documents — NeurIPS 2025, pp. 174653–174681
- 10.1016/j.neucom.2026.134357 — UA-RAG: Uncertainty-aware dynamic retrieval-augmented generation — Neurocomputing 699:134357
- 10.1016/j.neucom.2026.134911 — Dynamic RAG with hybrid retrieval: A novel approach to robust LLMs and hallucination prevention — Neurocomputing 705:134911
- 10.1016/j.aei.2025.103212 — Empowering LLMs by hybrid retrieval-augmented generation for domain-centric Q&A in smart manufacturing — Adv. Eng. Informatics 65:103212
- 10.1016/j.aei.2025.103158 — Retrieval augmented generation-driven information retrieval and question answering in construction management — Adv. Eng. Informatics 65:103158
- 10.7910/DVN/PCHISZ — Harvard Dataverse dataset for arXiv:2610.08026 (The Labeling Problem in Hallucination Detection Benchmarks); resolves via doi.org to dataverse.harvard.edu (202)

### Identifiers cited above that were resolved in this repository's earlier audit
(`research/00_citation_audit.md`), **not** re-resolved on 31 October 2026

- arXiv:2005.11401 — Lewis et al., RAG — NeurIPS 2020
- arXiv:2104.08663 — BEIR — NeurIPS 2021 D&B
- arXiv:2205.10601 — *not* the Self-Ask-with-Search paper; do not cite
- arXiv:2210.11934 / 10.1145/3596512 — An Analysis of Fusion Functions for Hybrid Retrieval — ACM TOIS
- arXiv:2307.04642 — TRAQ — NAACL 2024
- arXiv:2310.11511 — Self-RAG — ICLR 2024
- arXiv:2401.15884 — CRAG (arXiv; *not* the ACL Findings paper)
- arXiv:2404.16130 — GraphRAG
- arXiv:2407.01449 — ColPali — ICLR 2025
- arXiv:2411.06037 — Sufficient Context
- arXiv:2411.08891 — CalibRAG — NeurIPS 2025
- arXiv:2405.01563 — Mitigating LLM Hallucinations via Conformal Abstention
- arXiv:2412.10704 — VisDoM — NAACL 2025
- arXiv:2501.11551 — PIKE-RAG
- arXiv:2511.17908 — Principled Context Engineering for RAG: Statistical Guarantees via Conformal Prediction — ECIR 2026
- arXiv:2603.19281 — URAG: A Benchmark for Uncertainty Quantification in Retrieval-Augmented LLMs
- arXiv:2601.15457 — Chunking, Retrieval and Re-ranking for policy-document QA
- 10.18653/v1/2020.emnlp-main.550 — Karpukhin et al., DPR — EMNLP 2020
- 10.1145/1571941.1572114 — Cormack, Clarke & Buettcher, RRF — SIGIR 2009
- 10.1145/3701228 — CRUD-RAG — ACM TOIS

### Explicitly NOT verified, and therefore not asserted anywhere above

- The figures **77.8%** (Wan et al., `10.1016/j.aei.2025.103212`) and **92.4% Top-3** (Wu
  et al., `10.1016/j.aei.2025.103158`) remain unverified from metadata; the DOIs resolve
  and the titles are confirmed, but the numbers are not in the publisher metadata and
  could not be confirmed without the full text. Do not repeat them until checked against
  the paper.
- Citation counts for any paper in this report — Semantic Scholar returned HTTP 429 for
  every request from this IP, and OpenAlex's daily budget for this IP is exhausted.
- Benchmark sizes marked "Not stated in abstract" (SupChain-Bench, ChartWalker-Bench,
  MAGIC, HETERQA, HetDocQA, IndusSpec-QA, SParK-Eval) and the annotation-method details
  for SupChain-Bench, which I did not retrieve.
- Whether the joint NLI-plus-same-subject contradiction gate has been published under a
  formulation my search did not surface. My search covered arXiv (11 query formulations
  over the contradiction / conflict / knowledge-conflict / NLI space) and the ACL
  Anthology 2025-2026 volumes with the needles listed in §1.3(ii). Absence of evidence
  from these searches is weaker than evidence of absence, and an exhaustive systematic
  review is the right instrument for the final prior-art claim in the thesis.

---

*Compiled 31 October 2026 for the MTP "An Evidence-Grounded Retrieval-Augmented Generation
Framework for Industrial Decision Support", IIT Kharagpur, Department of Industrial and
Systems Engineering. Companion to `research/00_citation_audit.md` … `research/07_frontier_2026.md`;
this document supersedes none of them and should be read alongside `research/06_industrial.md`
and `research/07_frontier_2026.md`.*
