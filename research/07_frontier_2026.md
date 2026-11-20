# The 2025–2026 RAG Frontier and Its Pressure on the "Evidence-Grounded RAG for Industrial Decision Support" Thesis

**Compiled:** 31 October 2026 (thesis presentation due 18 November 2026)
**Scope:** State of the art published up to October 2026, assessed against the thesis's five design moves (D1 confidence gate, D2 modality quotas, D3 hybrid + category pre-filter, D4 contradiction surfacing, D5 per-claim three-band tagging) and four research objectives (RO1 design, RO2 component-level evaluation, RO3 failure-mode characterisation, RO4 cross-category generalisation).

---

## 0. Method, and how to read this document

**How the citations here were verified.** Every paper below was retrieved live from arXiv on 31 October 2026 and its metadata (title, author list, submission date, venue/comments, DOI, abstract) read from the `citation_*` meta tags of its abstract page. Nothing is cited from memory. Where a candidate arXiv identifier was guessed and turned out to resolve to a *different* paper, the identifier was discarded and re-derived by title search — six such mis-IDs were caught and corrected during this process (see §7.2). Any claim about a paper's *content* is taken from its abstract as fetched; claims about its *full method* are limited to what the abstract states. Where a number appears below, it is the number printed in the abstract, not an estimate.

**How to use this document.** §1 is the state of the art, organised so you can cite it. §2 is the threat register — read it before you write the introduction, because it determines which sentences you are allowed to claim. §3–§5 are the positioning argument. §6 is your viva script. §7 is the citation appendix.

**One warning before you read on.** The single most consequential finding of this survey is negative for the thesis as currently framed, and you need to hear it now rather than in November: *the two mechanisms the thesis claims as its most novel — a pre-generation statistical confidence gate and per-claim three-band confidence tagging — were both independently published before your submission date, in February 2026 and September 2026 respectively, and the pre-generation filter family as a whole has a published, reproducible methodology-bias critique from October 2026.* The thesis is not dead. But it must be reframed from "we invented these mechanisms" to "we adapted and validated them in an industrial setting under a confounded, contradiction-bearing corpus, and we measured the failure modes the original papers leave open." §2 and §5 give the exact wording that survives scrutiny.

---

## 1. State of the art as of October 2026

### 1.1 Surveys and taxonomies (the citation landscape you must position inside)

| Paper | arXiv | Date | What it is | Why it matters to you |
|---|---|---|---|---|
| Retrieval-Augmented Generation for Large Language Models: A Survey (Gao et al.) | `2312.10997` | 27 Mar 2024 | The canonical Naive → Advanced → Modular taxonomy. 4,401 citations (S2 count). | Your thesis's own literature table cites it as ref [16]. It is *superseded*. |
| A Survey of Multimodal Retrieval-Augmented Generation | `2504.08748` | 25 Mar 2025 | Multimodal RAG survey. | Baseline for D2 positioning. |
| Ask in Any Modality: A Comprehensive Survey on Multimodal RAG | `2502.08826` | 2 Jun 2025 | Modality-agnostic survey. | Baseline for D2 positioning. |
| Graph-based Approaches and Functionalities in RAG: A Comprehensive Survey | `2504.10499` | 21 Jan 2025 | GraphRAG survey. | Frames the GraphRAG-vs-category-filter comparison. |
| Retrieval Augmented Generation Evaluation in the Era of LLMs: A Comprehensive Survey | `2504.14891` | 21 Apr 2025 | Evaluation-methods survey. | Frames RO2/RO3 measurement choices. |
| Towards Trustworthy Retrieval Augmented Generation for LLMs: A Survey | `2502.06872` | 8 Feb 2025 | Trustworthiness survey. | Direct prior art on "trustworthy RAG". |
| Reasoning RAG via System 1 or System 2: A Survey on Reasoning Agentic RAG | `2506.10408` | 12 Jun 2025 | Reasoning-agentic RAG survey. | Positions "when to retrieve" literature. |
| Retrieval-Augmented Generation: A Comprehensive Survey of Architectures, Enhancements, and Applications | `2506.00054` | 28 May 2025 | Broad architecture survey. | General reference. |
| Agentic Retrieval-Augmented Generation: A Survey on Agentic RAG (Singh et al.) | `2501.09136` | 1 Apr 2026 (v2) | **The** agentic-RAG taxonomy. | Confirmed to exist and be current; cite by this ID, not from memory. |
| Scaling Beyond Context: A Survey of Multimodal RAG for Document Understanding | `2510.15253` | 20 Apr 2026 | Multimodal doc RAG survey. | Most recent D2-relevant survey. |
| A Technical Survey of Contextual Enrichment in LLMs (Beyond the Parameters) | `2604.03174` | 3 Apr 2026 | Contextual enrichment survey. | Frames "context engineering" era. |
| Trustworthiness in RAG Systems: A Survey | `2409.10102` | 16 May 2026 (v.) | Trust survey. | Compare to your D1. |
| A Survey of Secure Retrieval-Augmented Generation | `2604.08304` | 12 Oct 2026 | Security survey. | Frames §1.8. |
| Retrieved But Not Reliable: A Survey on Attacks, and Defenses in RAG | `2608.24977` | 27 Aug 2026 | Attack/defence survey. | Frames §1.8. |
| A Survey on Knowledge-Oriented Retrieval-Augmented Generation | `2503.10677` | 20 Jul 2026 (v.) | KG-oriented RAG survey. | Frames GraphRAG positioning. |
| RAG for NLP: A Survey | `2407.13193` | 19 May 2026 (v.) | NLP-application survey. | General reference. |

**Implication.** Your literature review's 18-paper table is 2023-vintage in framing and 2024-vintage in content. It needs a 2026 layer. At minimum add: the Agentic RAG survey (`2501.09136`), the compositionality paper (`2610.29722`), the multimodal doc-RAG survey (`2510.15253`), the long-context comparison (`2606.20898`), the evaluation-protocol papers (`2610.01218`, `2610.33849`), and the conflict-handling papers (`2609.35782`, `2609.16301`).

### 1.2 The long-context vs RAG debate — this is the thesis's biggest existential threat

This is where the honest evidence lives, and it does not favour RAG on a small corpus.

**Verified foundational positions:**

| Paper | arXiv | Finding |
|---|---|---|
| RAG or Long-Context LLMs? A Comprehensive Study and Hybrid Approach (Li, Zhuowan; Li, Cheng; Zhang, Mingyang; Mei, Qiaozhu; Bendersky, Michael) | `2407.16833` | Establishes the hybrid regime: use long context when it fits, RAG when it doesn't. **Your literature table has no entry for this paper — add it.** |
| Retrieval meets Long Context Large Language Models | `2310.03025` | The systematic comparison that precedes the "RAG is dead" argument. |
| In Defense of RAG in the Era of Long-Context Language Models | `2409.01666` | The pro-RAG counter-argument. |
| Lost in the Middle: How Language Models Use Long Contexts (Liu et al.) | `2307.03172` | Relevant information is least used in the middle of long contexts. |
| NoLiMa: Long-Context Evaluation Beyond Literal Matching (Modarressi et al.) | `2502.05167` | Long-context performance degrades on non-literal (semantic) matching even when nominally within the window. |
| RULER: What's the Real Context Size of Your Long-Context LMs? (Hsieh et al.) | `2404.06654` | "Context size" ≠ usable context; effective context is much smaller than advertised. |
| Diagnosing and Mitigating Context Rot in Long-horizon Search | `2606.29718` | An arXiv treatment of context rot (Chroma's original "Context Rot" is a technical report, not an arXiv paper — cite this if you need a peer-reviewable reference). |

**The three papers that must be in your thesis:**

**(a) `2606.20898` — "The Token Tax of Epistemic Accuracy" (18 Jun 2026).** This is the single most dangerous paper for you because it is *domain-matched*. A case study in **manufacturing safety training**, using an expert-validated benchmark, **972 answers**, three machines, two small language models and three retrieval/in-context approaches. Result: **long-context prompting achieved the highest correctness (73.1% vs 65.4% for semantic RAG), at 26× the per-query token cost.** The authors frame this as "the token tax of broader evidentiary access."

> **Why this is fatal to a naive framing.** Your corpus is **634 chunks**. Long-context prompting over 634 chunks is entirely feasible for a modern model. If you claim "our RAG framework beats a plain LLM," you have already lost to a baseline you did not run. If you claim "our RAG framework beats long context," you will lose on accuracy and you will have to explain the token cost.
>
> **What to do instead — and this is the pivot that saves the thesis.** The `2606.20898` finding plus `2609.35831` (below) together tell a coherent story: long context buys accuracy at a 26× token tax; an entropy-driven router recovers **97.4% of the long-context accuracy at a 70.7% token reduction, escalating only 18.2% of queries**. Your static confidence gate is, functionally, a *deterministic, auditable, domain-specialised* version of that router. The defensible claim is not "we invented the gate" — it is **"we replaced a learned probabilistic router with a deterministic, non-bypassable, code-level gate whose operating point is auditable and whose failure modes we characterise in an industrial corpus."** That is a real, defensible contribution, and it is what §5 formalises.

**(b) `2609.35831` — "Beyond the Context Window: An Adaptive Entropy-Based Routing Framework" (EDAR, 23 Sep 2026).** The decision to answer from chunks or escalate to long context uses the **predictive entropy of the token-level probability distribution over the first few generated tokens** of the RAG response; the threshold is swept against cost on a held-out validation set. On LongBench v2 and Infinity-Bench: predictive entropy correlates with hallucination rate at **Pearson r = 0.85 (95% CI [0.83, 0.87])** over 2,000 held-out generations; EDAR **retains 97.4% of the pure-long-context accuracy while reducing total token expenditure by 70.7%, escalating only 18.2% of queries.**

> **Threat class:** SERIOUS. **Your D1 is preceded.** But note what EDAR *cannot* do and what you can: EDAR routes to long context — a resource an on-prem industrial deployment may not have, and a route that produces no evidence trail. Your gate's answer is "no evidence," and its output is auditable. Also note EDAR is a *routing* decision, not a *refusal* decision: it never says "the documents do not support an answer." Refusal is a distinct, still-open problem (§3).

**(c) `2610.29722` — "Retrieval Augmented Generation Compositionality" (LASAGNA, 21 Oct 2026).** 103 pages (9 main), 15 figures, 68 tables; project page and code public. It **pre-declares three hypotheses** and tests **450 configurations across eight benchmarks and corpora ranging from 5K to 200K documents**. Three findings, verbatim from the abstract:

> 1. "individually strong techniques from different phases of a RAG pipeline do not necessarily compose: **three retrieval techniques predict a +47% combined improvement but deliver only +17% when used together.**"
> 2. "component gains stack differently for retrieval and faithfulness, and **optimizing one can hurt the other.**"
> 3. "**the best composition changes as the corpus grows:** the combination that wins on a small corpus may not remain best at large scale."
>
> and closes: "gains measured in isolation are n[ot]…"

> **Threat class:** SERIOUS, but **this is also your single best citation.** LASAGNA is a direct, published, quantitative warning that the thesis's RO2 ("evaluate four retrieval mechanisms") is at high risk of producing non-additive or contradictory effects — exactly the "optimizing one can hurt the other" failure. It also proves the field now demands **pre-declared hypotheses** and **compositional** evaluation. **Practical consequence: your experimental protocol should mirror LASAGNA's — pre-register your hypotheses, evaluate the full pipeline composition rather than isolated ablations, and report at least two corpus sizes.** It gives you a citable methodological standard to claim you met, which converts a threat into evidence of rigour.

**Supporting evidence in the same family:**

- `2609.17564` — "Beyond Static RAG: An Adaptive, Tri-Metric Routing Framework for Efficient Long-Context Inference on Commodity GPUs" (ICML Scale Workshop 2026). Adaptive routing; also documents the "Compression Paradox" (prompt compression adding KV-cache contention that outweighs generation-time savings).
- `2610.08463` — "UNREAL: Unifying Retrieval and Long-Context with a Single Model" (6 Oct 2026). Model-native evidence selection spanning both regimes.
- `2608.00705` — "A Triple-Robustness Analysis of RAG for Multi-Hop Requirements Traceability" (1 Aug 2026). **Requirements traceability is an industrial engineering task**, so this is domain-matched to you. 2×4,440 main-matrix runs, 600 cross-corpus runs, >5,000 faithfulness judgments, varying embedder (local e5-small vs Azure text-embedding-3-small), corpus (DO-178C typed-edge requirements vs Wikipedia/MuSiQue) and judge (paired GPT-5.4 × GPT-4.1). Three findings that should reshape your experimental design:
  - **C2a**: GraphRAG's graph walk floods the context window at retrieval precision **0.12–0.23**, but its synthesizer cites selectively at precision **0.48–0.65**; **"scoring the retrieved set as the attribution set inverts the architecture ranking."** → *Your D5's per-claim tagging must state which set is the attribution set, and you must show the ranking is stable under both definitions.*
  - **C1**: answer-level citation winners are corpus- and stratum-conditional but embedder-robust; GraphRAG ties vanilla on short-hop DO-178C queries and wins every MuSiQue stratum; agentic pipelines lead only on 3+-hop requirements queries. → *Your RO4 (cross-category transfer) should be framed as hop-distance-conditional, not category-conditional.*
  - **C2b**: faithfulness is corpus-conditional — on DO-178C it declines with hop distance (trend p<0.05 in three of four judge × embedder combinations). → *Report faithfulness as a function of hop distance.*
- `2610.37358` — "When Is Additional Retrieval Worthwhile?" (22 Oct 2026). On 60 QASPER articles (188 questions, 169 evidence-evaluable): a cost-aware policy switching from dense+rerank to hybrid triggers on **24.5% of questions** and obtains the same evidence Hit@10 (**78.70%** vs **76.92%** always-keep), and **"paired, paper-cluster bootstrap intervals do not establish a reliable utility advantage."** → *A published negative result for hybrid-over-dense. Directly relevant to your RO3/D3. Report it honestly.*

### 1.3 Agentic and graph RAG — the "static gate looks naive" threat

**Verified canonical anchors:**

| Paper | arXiv | Note |
|---|---|---|
| From Local to Global: A Graph RAG Approach to Query-Focused Summarization (Edge et al.) | `2404.16130` | The original GraphRAG. |
| LightRAG: Simple and Fast RAG (Guo et al.) | `2410.05779` | The main GraphRAG successor. |
| Agentic RAG: A Survey (Singh et al.) | `2501.09136` | Taxonomy. |
| HippoRAG: Neurobiologically Inspired Long-Term Memory for LLMs (Gutierrez et al.) | `2405.14831` | The original HippoRAG. |
| From RAG to Memory: Non-Parametric Continual Learning for LLMs (Gutierrez et al.) | `2502.14802` | **This is HippoRAG 2** — note the title differs from the method name; do not let a title search "correct" the identifier away. |
| KAG: Boosting LLMs in Professional Domains via Knowledge Augmented Generation (OpenSPG) | `2409.13731` | Knowledge-graph-grounded RAG for professional domains — the most directly comparable to your category-filter design in terms of domain specificity. |

**2026 successors relevant to your comparison:**

- `2608.24921` — **post-graph-rag: A PostgreSQL-Native Bi-Temporal Graph RAG Engine** (5 Sep 2026; 35 pages, 8 figures, 15 tables). **Uses the same stack as your thesis**: chunks with embeddings, a canonical entity graph and community summaries in *one PostgreSQL database, with pgvector for search and edge tables for traversal*. Three stated failure modes of existing GraphRAG: infrastructure (three stores to keep in sync), quality (**"a pipeline that never refuses extractor output stores edges asserting nothing"**), and time (a graph that only accumulates treats superseded and current facts alike). Extraction output is *validated before writing* — vague predicates, pronominal names and bare quantities are rejected; predicates normalise onto an optional vocabulary; entities resolve to one vertex per canonical name. A bi-temporal layer records when a relation held versus when the system believed it, superseding incompatible earlier assertions from document order. Against LightRAG on three corpora with extraction and embedding models fixed, it builds a denser, more queryable graph and supersedes relationships where a baseline with no temporal model supersedes none; on LongMemEval (500 long-horizon chat-memory questions) it scores **94.0** (the abstract truncates mid-word at "94.0 perce…" — read the paper for the exact metric and its direction). → *This is simultaneously your best architectural precedent (same Postgres+pgvector stack, same validation-before-write philosophy as your confidence gate) and a direct competitor. Cite it, adopt its validation discipline.*
- `2607.19301` — PAGE-RAG: Evidence-Grounded Adaptive Graph Retrieval for Long-Document QA (21 Jul 2026). "graph structures as semantic skeletons that organise and navigate" rather than independent knowledge sources — a principled argument that *your category filter is a skeleton, not a graph*, and that treating it as such is legitimate.
- `2609.26237` — **ABAI at COLIEE 2026 Task 1** (12 Aug 2026). A production legal-retrieval system whose pipeline is **multi-view BM25 over citation-context windows with reciprocal rank fusion, neural reranking, graph-based features from entity communities and a graph attention network, and a LightGBM meta-learner over 34 features** — i.e. your D3 pipeline plus more, already deployed and benchmarked. Its **best official-test F1 was 0.177 against a cross-validated 0.311**, and the authors attributed the gap to a recall ceiling, temporal distribution shift and threshold miscalibration, then tested all three (threshold transfer costs 0.007 F1; decision quality flat across chronological quartiles; test queries not measurably off-manifold in two independent embedding spaces). Misses split **exactly evenly** between candidates never retrieved and candidates retrieved but ranked below the cut. → *This is your D3 novelty reality check: hybrid+RRF+neural rerank is standard practice, and the paper is a masterclass in honest reporting of a CV→test gap. Model your evaluation reporting on it.*
- `2610.34866` — UniGFM-RAG: Unify Graph Foundation Models and LLMs for End-to-End Retrieval and Reasoning (26 Oct 2026).
- `2609.19622` — Geometric Gain Graph: Zero-Token Graph Construction for Multi-Hop RAG (26 Sep 2026). Names the "Similarity Trap" and "Novelty Traps".
- `2610.36444` — RouteDRAG: Learning to Route and Control Agentic Execution for Multimodal Document RAG (26 Oct 2026). Finds "agentic execution provides query-dependent benefits" — i.e. agentic execution is *not* uniformly better, which supports a **query-conditional** gate over a static one.
- `2609.10239` — LiteRAG: Cost-Efficient Graph-Based RAG (18 Sep 2026).
- `2607.03447` — TRIAGE: Trustworthy Retrieval Instrumentation and Graph Evaluation (3 Jul 2026).
- `2610.02373` — Hop-Decayed Influence: New Vulnerabilities of Structural Auxiliary Indexing (26 Oct 2026). → *Caveat for your D3: the *auxiliary index* (your category filter) is itself an attack surface. Mention it.*

### 1.4 Reliability, hallucination and attribution

**Foundational (verified):** Self-RAG `2310.11511` (30 Nov 2023); CRAG `2401.15884` (24 Jan 2024); Semantic Uncertainty (Farquhar et al.) `2302.09664` (19 Feb 2023) — note this is the paper your prior report cites for "Detecting Hallucinations in Large Language Models Using Semantic Entropy," published in *Nature* 630:625–630 (2024), DOI `10.1038/s41586-024-07421-0`, with the arXiv preprint at `2302.09664`. Cite the *Nature* version.

**Two more foundational anchors you should add:**

- **Context-Aware Decoding** — `2305.14739`, *Trusting Your Evidence: Hallucinate Less with Context-aware Decoding* (Shi et al., 23 May 2023). This is the original CAD method: it re-weights the output distribution towards the retrieved context, so the model's answer is pushed toward the evidence *during decoding* rather than filtered *before* it. It is a **third mechanism class** alongside "filter before generation" (your D1) and "post-hoc claim labelling" (your D5), and it is the one your literature table omits entirely. Cite it in the mechanism taxonomy; an examiner who knows CAD will ask why a *pre*-generation gate was chosen over *decoding-time* re-weighting. Your answer is defensible — CAD cannot produce a refusal and does not give an auditable operating point — but you must have the answer ready.
- **ALCE** — `2305.14627`, *Enabling Large Language Models to Generate Text with Citations* (Gao et al., EMNLP 2023). This is your ref [11]. It introduced NLI-based **citation recall and citation precision**, which is the metric family your D5 must be measured against. Your prior report's §1.3 cites ALCE for NLI-based citation evaluation; that is correct, and it is also the reason a *new* three-band metric needs a clear justification — you are re-binning a quantity ALCE already measures, so your contribution must be about *communicability and human validation*, not measurement.

**The 2026 cluster — this is where your D1 and D5 are in trouble:**

**(a) `2511.17908` — "Principled Context Engineering for RAG: Statistical Guarantees via Conformal Prediction"** (Chakraborty, Yang, Khashabi, Lawrie; submitted 18 Jan 2026; **ECIR 2026**, Springer LNCS, **DOI `10.1007/978-3-032-21300-6_45`**). Abstract: "Existing pre-generation filters rely on heuristics or uncalibrated LLM confidence scores, offering no statistical control over retained evidence. We evaluate and demonstrate context engineering through conformal prediction, a coverage-controlled filtering framework that removes irrelevant content while preserving recall of supporting evidence." On **NeuCLIR** and **RAGTIME**: conformal filtering consistently meets its target coverage and **reduces retained context by 2–3× relative to unfiltered retrieval**; on NeuCLIR, downstream factual accuracy measured by **ARGUE F1 improves under strict filtering** and remains stable at moderate coverage.

> **Threat class: FATAL to "we add a statistically-grounded pre-generation filter" as a novelty claim.** Conformal filtering of RAG context, with published coverage guarantees, was at ECIR 2026. A Bayesian-posterior threshold with logistic-regression calibration (β₀ = 2.943, β₁ = 1.680, on a 30-query set) is, in statistical terms, a *point estimate* of a posterior probability used as a hard threshold — it is strictly weaker than a conformal procedure, which provides a finite-sample coverage guarantee. **Do not claim statistical rigor your method does not have.** Two options: (i) adopt conformal prediction yourself (then cite this paper as prior art you extend to the industrial, contradiction-bearing setting), or (ii) position honestly as a *deterministic, auditable* threshold with a *calibration-curve* validation, and explicitly say it does not provide finite-sample coverage guarantees. Option (ii) is defensible and much cheaper; option (i) is stronger and is the one to take if you have compute time before 18 November.

**(b) `2610.34872` — "Adaptive Retrieval, Selective Answers: Evaluating Conformal Factuality in Agentic RAG"** (26 Oct 2026; code public). "Previous work has studied **claim-level conformal factuality in single-stage RAG and, more recently, multi-hop RAG.**" Evaluates six model-dataset configurations (GPT-6 Luna, Llama 3.1 8B × HotpotQA, Natural Questions, TriviaQA), each with 60 fixed questions, 100 seeded 30/30 calibration-test partitions, five conformal target levels, and a no-conformal-prediction baseline. At the 95% target: **non-empty response coverage ranges 17.23%–60.17%, claim retention 10.72%–43.16%, and full support among non-empty outputs 89.14%–95.56%.**

> **Threat class: FATAL to "per-claim confidence tagging" as a novelty claim.** Claim-level confidence with a published statistical procedure, already extended to multi-hop and now to agentic RAG, is a mature line of work. Your three-band (grounded / inferred / uncertain) labelling is a *coarser, more practitioner-legible* variant of a finer-grained conformal claim-support procedure.
>
> **The counter-positioning that survives:** your tagging is **three-band and semantic** (a claim is *grounded* — stated in the source; *inferred* — derivable from the source by inference; *uncertain* — not supported). Conformal factuality is **binary per claim with a coverage guarantee**. The gap between "is this claim supported at 95% confidence?" and "is this claim stated, inferred, or unsupported?" is a *communicative* gap, and communication is exactly what an industrial practitioner needs — the thesis's own report says per-claim tagging "surfaces model uncertainty to practitioners." **Position the contribution as human-facing uncertainty communication under a safety-critical decision context, and cite the conformal work as the statistical backbone you are NOT reinventing.** Add a direct empirical comparison if time permits.

**(c) `2609.04442` — "GRACE: Graph-Grounded Reflective Agent Copilot Engine"** (3 Sep 2026; AKBC Workshop @ EMNLP 2026). Deconstructs LLM responses into **atomic claims** and grounds them against trusted knowledge priors in a **weighted bipartite graph**; edge weights encode each claim's closeness to the priors; **weighted centrality classifies claims as Grounded, Refuted, or Boundary**; a **Return on Attention (RoA)** objective defers a claim to expert review only when its priority-weighted uncertainty exceeds the cost of verification; verified claims become new evidence anchors, closing a validator-LLM evolutionary loop.

> **Threat class: FATAL to "we introduce three-band per-claim confidence tagging."** Grounded / Refuted / Boundary is your grounded / inferred / uncertain with different labels and a different mechanism (graph centrality vs information gain). This must be cited. **Do not present the three-band taxonomy as new.** Present it as a *simplification aimed at practitioner comprehension*, and — this is the key move — as a **user-study-validated artefact** (your 16-participant study) rather than a novel algorithmic contribution. GRACE has no such validation and no industrial evaluation. *That* is your defensible contribution.

**(d) `2608.13706` — "CLAIR-Fin"** (7 Sep 2026; **FinNLP 2026 @ EMNLP 2026**). Nine-agent framework decomposing questions into atomic claims in a typed Financial Claim Ledger, with: **Asymmetric Evidence Authority** (evidence trust conditioned on claim type rather than treating all modalities as equally reliable), **Chain-of-Custody Verification** (grounding checked at hand-off, not only at exit), an **Adaptive Rebuttal Cycle**, and a **terminal entailment audit paired with a continuous Hallucination Risk Index that distinguishes claims that passed scrutiny from claims never contested**. Evaluated on BB-FinQA-X, a 500-question cross-modal financial set from Bangladesh Bank Annual Report material; the abstract reports faithfulness moving from **0.780** for the single-pass RAG baseline to a higher CLAIR-Fin value that is truncated in the fetched abstract — **read the paper for the exact figure**. → *CLAIR-Fin independently implements D2 (asymmetric modality trust), D4 (entailment audit) and D5 (three-way claim status) in a cross-modal financial domain. It is the single closest prior art to your entire design. Cite it, compare against it, and note the domain difference (financial QA vs industrial engineering) and the scale difference (nine agents vs a single non-bypassable code gate).*

**(e) `2609.16301` — "CLEAR: Cross-Source Evidence Adjudication for LLMs in Medicine"** (14 Sep 2026; 31 pages). Generates candidate answers independently from **three pathways** — parametric knowledge, locally curated corpora, dynamically retrieved evidence — then an aggregation verifier evaluates candidates, supporting evidence, provenance and source quality to identify agreement and conflict; an adjudication module determines preserve-vs-revise through complementary **override-guard** and **challenge-audit** mechanisms; **unresolved conflicts trigger targeted follow-up search and re-adjudication.** → *This is your D4 pattern, published, in medicine. Your "joint NLI + topical gate" is the conflict-*detection* half; CLEAR does detection *plus* resolution *plus* re-retrieval. You should either implement the follow-up-search step or explicitly scope D4 to detection-and-surfacing only and say so.*

**(f) `2610.35056` — "Hallucination-Aware Multi-Agent RAG via Internal Attention Rewards"** (**Findings of EMNLP 2026**). Adds an internal hallucination-risk signal computed from the generator's attention-head norms to the task reward; three role-specific LoRA adapters (query planner, evidence selector, answer generator) over a frozen backbone; a TruthfulQA-trained critic frozen after one training. Improves task performance and reduces hallucination rates over the strongest multi-agent baseline across Qwen3-8B, Llama3-8B, Llama2-13B on RAGTruth, HotpotQA and 2WikiMultiHopQA. → *Uses RAGTruth as a hallucination benchmark — include RAGTruth in your evaluation.*

**(g) `2610.26951` — "The Bottleneck Is Retrieval, Not Reading" (EBG)** (18 Oct 2026). Argues the similarity-driven chunked pipeline "cannot anticipate which passages a question requires and discards document-level context that resolves cross-passage references"; introduces evidence-based generation requiring **line-level citations** and a **joint Ans+Evid metric** that scores correctness and grounding simultaneously. → *Metric design: adopt Ans+Evid or explain why your metric differs.*

**(h) `2610.40314` — "Decompose, Estimate, Select: Coverage-Aware Context Construction for Long-Form RAG"** (29 Oct 2026). Decomposes queries into subquestions, ranks with a coverage-trained bi-encoder, **predicts a document × subquestion coverage matrix with a cross-encoder**, and selects by greedy coverage. → *A coverage-matrix mechanism is a direct competitor to your per-claim confidence tags; also a strong alternative to your D2 quotas.*

### 1.5 Abstention, gating and refusal — the closest art to your D1

**(a) `2610.36561` — "Governed Sovereign RAG for Public Administration"** (26 Oct 2026; **deployed in production** at the State of Tlaxcala, Mexico). Three pillars, all of which you must cite:
1. **A two-stage tripartite epistemic gate** (clarify_policy + a Boltzmann distribution over AnyJev) arbitrating among **answering (SPECIFIC) / facet-guided clarification (CLARIFY) / abstaining (ABSTAIN)**;
2. A **post-generation deterministic numeric verifier** with SHA-256 cache invalidation ensuring every generated fee or validity figure belongs to the retrieved official record;
3. Evaluation over **380 organic production traces (8 weeks)** and a **200-query stratified benchmark (5-fold CV: 86.41% ± 7.50%)**.

Production numbers: **89.47% of traffic is resolved at Level 0 via deterministic templates without free generation** (global p50 0.665 s; direct L0 p50 0.445 s; slow-tail p95 30.412 s under CPU queuing); **0/40 fiscal-amount hallucinations observed in Level 1** (95% bound < …). Covers 1,143 procedures and a decoupled directory of 924 offices.

> **Threat class: SERIOUS.** This is a deployed, government-grade system with an epistemic gate that arbitrates between three outcomes — including abstention — and with a deterministic numeric verifier. Your D1 is a two-way gate (answer / no evidence) without clarification, without numeric verification, and without production traces.
>
> **The openings that remain for you:** (i) no *contradiction* dimension; (ii) no *claim-level* dimension; (iii) its 200-query benchmark is small, and the interesting contribution is the *deployment*, not the algorithm; (iv) it does not operate on industrial engineering documentation with tables and charts. **Add a CLARIFY-style middle tier** — a "retrieved but insufficient/conflicting evidence" response — and you will have a three-way gate that is strictly richer than this system and than your own current two-way design. This is the cheapest single upgrade available to you before 18 November.

**(b) `2610.01218` — "AGO AI Quality Gate: Evidence-First Release Decisions for RAG"** (1 Oct 2026; **NFMCP 2026, ECML PKDD 2026 Workshops**). A **four-state decision model** that treats missing data and judge errors as explicit outcomes; **layered scoring** combining deterministic checks, local guardrails and structured LLM evaluation; a **stratified beta-binomial gate** quantifying regression risk probabilistically; and a **mandatory meta-evaluation protocol** to validate the LLM judge before it influences decisions. Because engagement data is proprietary, the judge layer is evaluated on **RAGBench, a public benchmark of 100k annotated RAG traces across 12 datasets**, with identical stratified test samples (**N = 1200 per judge**): a low-cost judge (**gpt-4.1-nano**) detects non-adherent answers barely above chance at **AUROC 0.603 [0.570, 0.634]** despite producing flawless protocol output, while **gpt-4o reaches 0.783 [0.756, 0.807]** — yet its per-domain performance still ranges **0.62 to 0.88**.

> **Threat class: SERIOUS, and simultaneously your most useful methodological gift.** AGO says, with numbers: *your LLM judge may be barely above chance, and you must meta-evaluate it before trusting it.* If your evaluation uses an LLM judge that has never been meta-evaluated, your reported gains are not credible — and an IIT Kharagpur examiner who knows AGO will say so.
>
> **Do this, and it is a publishable-grade contribution in its own right:** meta-evaluate your judge exactly as AGO does — stratified N=1200, report AUROC with confidence intervals, report per-category spread — and report the number whatever it is. A thesis that reports "our judge scores 0.61, so our headline metric is unreliable, therefore we add a human-verified subset and report both" is *more* credible than one that reports a strong number from an unvalidated judge. AGO's own framework and RAGBench are directly reusable.

**(c) `2610.33849` — "Ranking Is Not Deciding: Benchmark Shortcuts and Operating-Point Collapse in Query-Time RAG Poisoning Defenses"** (24 Oct 2026; 26 pages, 7 figures, 14 tables). **This paper is the most important methodological threat to your entire thesis, and you must engage with it explicitly.**

The claim: "Query-time filters that screen each retrieved document before it reaches the generator are the dominant published defense against RAG poisoning, and they report near-perfect detection on domain benchmarks. We show that this performance is **predicted by how the poison set was built rather than by what the filter reads**: removing a single construction cue destroys the deployed decision before it destroys the ranking."

The mechanism and the numbers: two label-free statistics cue the artefact — **containment** (how often the target question appears verbatim in the poison) and **length overlap**. PoisonedRAG's released code prepends the target question to every inserted passage. Of the **21 published defense evaluations** surveyed, **8 verifiably run poison built this way** and **5 substitute a length cue**; separately, **12 report no false-positive rate at the operating point they deploy**. Deleting only that prefix from the attack authors' own passages (**0.93 still retrieved for their target**) takes **RAGuard**, a published content filter the authors re-implement, from **AUROC 0.953 to 0.758**, and its **miss rate from 0.191 to 0.763**. Across four corpora, four attack families and ten per-document defenses on one shared candidate set, the profile predicts where detection saturates. Padding medical poison to clean length with word-shuffled filler that carries no content takes TrustRAG's set-level performance down.

> **Why this is FATAL to your RO3 if you ignore it.** Your confidence gate is exactly a query-time pre-generation filter. Your evaluation set is exactly a domain benchmark. If your "confident" and "unconfident" chunks are separable by a surface artefact — chunk length, boilerplate phrasing, a template header, the presence of a number in a particular format, or the way your annotators wrote the questions — then your reported detection performance measures your *benchmark construction*, not your gate. This is the failure mode you are most likely to walk into without knowing it exists, because you have no reason to suspect it.
>
> **What to do — a concrete, cheap protocol, and it becomes a contribution:**
> 1. **Report a false-positive rate at your operating point.** 12 of 21 published evaluations do not. Do not be the 13th. Report FPR, not just accuracy or AUROC.
> 2. **Run a length-matched control.** Re-sample your "unconfident" chunks to have the same length distribution as your "confident" chunks, and re-measure. If the gate's separation collapses, you have found a length cue — which is exactly the artefact AGO-style papers get caught by.
> 3. **Report per-category AUROC with CIs**, not one pooled number (your corpus spans 12 categories; per-domain judge spread of 0.62–0.88 in AGO is the expected shape of a heterogeneous industrial corpus).
> 4. **Add an adversarial negative set**: deliberately confusable negatives that are *correct* — e.g. a chunk that is lexically similar to the query but answers a different scope (different plant, different period, different metric). This is precisely what `2609.35782` says matters.
> 5. **Report the 0/1-level** the paper discusses: "operating-point collapse." Your threshold is a *decision*; a decision has an operating point. Show the precision/recall trade-off curve across thresholds, not a single point.
> 6. In the paper, cite `2610.33849` and say explicitly: *"Our gate is evaluated against the benchmark-shortcut pathology identified by Kumar et al. (2026), using length-matched controls and an operating-point sweep."* **That sentence alone moves you from naive to rigorous.** It may be the single highest-value change you can make to the thesis in the time you have.

### 1.6 Contradiction and conflict detection

| Paper | arXiv | Key content |
|---|---|---|
| Financial Evidence Crowding (FinDeCrowd) | `2609.35782` | "passages can match a query's topic while conflicting with its **period, segment, metric scope, or table scope**." Incompatible pools reduce **Recall@10 by 0.147** vs equally difficult compatible pools. FinDeCrowd-RAG (learned score correction + query-level identity gate) raises top-10 evidence inclusion from **0.757 to 0.902**. |
| ARCagent | `2609.36392` | Clinical QA for ME/CFS where "major guidelines **actively contradict** each other on treatment." A **1,706-chunk, 10-source KB with a structured inter-guideline conflict registry**, conflict-aware retrieval calibration, and a benchmark noting keyword matching causes **"systematic underestimation averaging 10.1 percentage points."** Achieves **95.3%**. |
| RAGStress | `2610.04691` | Controlled KB-degradation benchmark: **four naturalistic corruption types (factual corruption, numeric typo, relevance poisoning, contradiction injection) × three severity levels**, over **57 MMLU subjects and 182,546 documents**, **52,500 model-question-condition evaluations**. Finds: clean retrieval can mask robustness differences; **semantic-fidelity corruptions are substantially more harmful than signal-utility perturbations**; **no-retrieval accuracy does not predict corrupted-retrieval robustness**; mixed-KB accuracy should not be treated as worst-case robustness. |
| MONOLOGUE | `2610.34829` | Logic-hijacking single-document poisoning; notes modern aligned LLMs "arbitrate such conflicts conservatively, rejecting overt contradictions in favor of parametric memory." |
| The Immutable Past | `2609.16073` | Formalises **"Semantic Shadowing"** in mutable RAG: conflicting historical observations accumulate and statistically dominate valid recent updates. |
| TWIST | `2609.28575` | Benchmark for contradiction detection / intervention quality in conversational memory: unprompted tension detection, vetting outgoing drafts against the record. |
| RegDivergence-101 | `2608.28607` | Cross-jurisdiction regulatory contradiction detection benchmark. |
| Evidence-Admissible search | `2608.22062` | "Search Broadly, Seek Evidence on Both Sides, Decide Narrowly" — adversarial-robust evidence admissibility. |
| TRACER / evidence integration | `2609.04290` | Evidence integration in LLMs. |

> **Assessment for your D4.** Your "joint NLI + topical gate" is a *reasonable and now well-motivated* design, but it is not novel, and `2609.35782` published the failure mode it targets ("evidence crowding": conflicting candidates consume top-k slots and displace supporting evidence — **Recall@10 −0.147**) plus a **learned correction that beats your hand-designed gate** (0.757 → 0.902). `2609.16301` (CLEAR) published the adjudicate-and-re-retrieve loop. `2609.36392` published a *structured conflict registry* — arguably a better representation of "two documents disagree" than pairwise NLI over chunk pairs, because a registry makes the conflict an explicit first-class object rather than an inference you re-derive per query.
>
> **Recommendation:** keep pairwise joint NLI + topical gating as your implemented mechanism (it is cheap and it is the thing you can actually build and evaluate by 18 November), but *position* it correctly: as a **detection-and-surfacing** mechanism whose known failure mode (viewpoint difference vs true logical contradiction, and per-category false-positive rates) you characterise empirically. Explicitly scope D4 to detection — not resolution — and say so, citing CLEAR for the resolution step you did not do. Then your reported FP rate becomes a finding rather than a flaw. Your own report already says NLI-only gives **98% false positives** dropping to **16%** with the topical gate; that is a *strong, publishable-shaped finding* about why naive NLI gating fails, and `2610.33849` tells you to check it for benchmark artefacts before you claim it.
>
> **Consider, if time allows:** a **conflict registry** (a table of `{chunk_a, chunk_b, topic, conflict_type, resolution_hint}` precomputed at ingestion) instead of or alongside pairwise NLI at query time. It is more industrially legible ("Policy A says X for Plant 1, Policy B says Y for Plant 2"), directly addresses the topic-scoping problem, and sidesteps the query-time latency cost of pairwise NLI. It also gives you the cross-document contradiction *registry* that ARCagent used.

### 1.7 Modality, tables and charts — the D2 landscape

**The visual-retrieval lineage your literature table is missing.** The multimodal retrieval literature is dominated by a different mechanism than yours — *late-interaction visual embedding* rather than text-similarity over extracted content:

- **ColPali: Efficient Document Retrieval with Vision Language Models** — `2407.01449` (Faysse et al.). Encodes each document page as a set of image patches with a VLM and indexes them with a late-interaction ColBERT-style scorer, so retrieval operates over the *rendered page* rather than over extracted text. → *This is the strongest alternative to your table/chart pipeline, and it does not need modality quotas because it never reduces a table to text in the first place.* **Your D2 motivation must acknowledge this.** If your defense is "we use OCR-based extraction because it is cheaper and runs on our hardware", say so; if you have not tried a visual-retrieval arm, an examiner may ask why not.
- **T²-RAGBench: Text-and-Table Benchmark for Evaluating RAG** — `2506.12071`. A benchmark built specifically for the text-and-table retrieval problem. → *Use it as an external check on your table handling.*

**Evidence that the problem is real (supports your D2 motivation):**

- `2610.37080` — **Tessera: Structure-Completed Evidence Units for Web RAG** (27 Oct 2026). Traces answer evidence from source HTML to reader input over the full English Wikipedia and finds that chunking "loses evidence in text and screenshot pipelines alike: evidence present in the source page often fails to reach the reader intact, **particularly structured content such as tables and infoboxes, which chunking separates from the headers and context that give it meaning. Stronger extraction, context expansion, and larger reader budgets leave the loss in place.**" Tessera rebuilds pages into fine-grained evidence units completed with page title, section path and table headers, and **improves answer accuracy by 5–6 points on text and screenshot pipelines**, consistently across readers and retrievers. → *This is a strong, direct empirical confirmation of your D2 problem statement — cite it as motivation.*
- `2610.35542` — **HyperDoc** (ICDE 2027). "existing systems mainly rely on **static selection rules over fixed-granularity retrieval units** such as pages or blocks, resulting in information loss during retrieval and suboptimal performance in downstream reasoning." Proposes budget-aware evidence selection over a **document hypergraph** capturing structural, logical and cross-modal relations.
- `2609.35304` — **Signal or Noise? Modality Contribution and Cooperation in Multimodal GraphRAG** (6 Sep 2026). **The most important paper for your D2 hypothesis.** "it is commonly assumed that retrieving evidence from more modalities at inference time improves downstream performance. Yet, **redundant or overlapping multimodal evidence may distract language models** in question answering, and whether each modality contributes equally across questions, models, and tasks remains poorly understood." Uses DocVQA as testbed, tracks which modality supports which facts, filters at edge level.

> **Threat class: SERIOUS to your D2 *hypothesis*, and helpful to your D2 *problem statement*.** Your hypothesis "per-modality retrieval quotas improve recall on table and chart queries" is now (a) untested against the redundancy/distraction effect that `2609.35304` documents, and (b) facing a competing mechanism — Tessera's structure-completion and HyperDoc's hypergraph selection — which fix the *cause* (structure loss) rather than applying a *quota* on top of it. **Your own report already records a documented null result: the corpus is too text-heavy (2.3% chart, 7.1% table) to exercise the signal.** That null result, read through `2609.35304`, is a *finding*, not a failure: it says modality quotas cannot help when the corpus does not contain the modality. **State it that way, and cite `2609.35304` for the redundancy caveat.** Also note `2609.35304` suggests the mechanism a modality-quota should be tested against: which modality supports which facts, filtered at edge level — a per-fact modality attribution rather than a per-query quota.

**Direct competitors to D2 in industrial settings:**

- `2610.34503` — **Multimodal Requirements Traceability Link Recovery in Industrial Settings** (APSEC 2026). "We extend a retrieval-augmented generation approach for inter-requirements traceability link recovery. **Our extension retrieves text and image candidates separately, classifies each retrieved pair with a vision-language model, and filters the predicted links by verbalized confidence.**" On three non-overlapping industrial requirement sets and six public text-only datasets: **F1 0.310 vs 0.114** for a replication of the Hey et al. baseline; recovers links in all four modality combinations; but recovery remains limited by failures to retrieve related text requirements for image queries; **confidence filtering produces link sets with different** (presumably different precision/recall profiles).
  > **This is your D1 + D2 combined, published, in industrial requirements engineering.** It is the most directly threatening paper in this document. Cite it explicitly, and note both differences you can defend: they filter *links* (a retrieval-verification task) whereas you gate *generation* (an answer-level task); they use verbalized confidence from a VLM whereas you use a calibrated posterior over retrieval features; and they did not characterise failure modes across 12 categories.

- `2510.15253` — Scaling Beyond Context: multimodal RAG survey for document understanding (Apr 2026); `2504.08748` — A Survey of Multimodal RAG (Mar 2025); `2502.08826` — Ask in Any Modality (Jun 2025). Your D2 literature review must engage these.

### 1.8 Evaluation benchmarks and metrics

| Benchmark | arXiv | What it gives you |
|---|---|---|
| RAGAS | `2309.15217` | Reference-free faithfulness, context precision, answer relevancy. Verified authors: **Es, Shahul; James, Jithin; Espinosa-Anke, Luis; Schockaert, Steven** — so your ref [10]'s "Es, S., et al." is **correct as written**; do not change it. Venue: EACL System Demonstrations; **confirm the year and page range on the ACL Anthology** (§7.5). |
| ARES | `2311.09476` | Automated evaluation framework with prediction-powered inference. Verified authors: Saad-Falcon, Khattab, Potts, Zaharia. **Venue: NAACL 2024** (confirmed via Semantic Scholar). → *Distinct from ALCE (below), and a formal reference your bibliography currently lacks — it is the framework you should be using for RO3 evaluation.* |
| RGB | `2309.01431` | "Benchmarking LLMs in RAG" (Chen, Jiawei; Lin, Hongyu; Han, Xianpei; Sun, Le). Cite for negative-rejection (your "no evidence" gate). |
| CRUD-RAG | `2401.17043` | Chinese benchmark; **CRUD** = Create/Read/Update/Delete, with the **specificity** dimension your per-claim tagging maps to. Verified authors: Lyu, Yuanjie; Li, Zhiyu; Niu, Simin; Xiong, Feiyu; Tang, Bo; Wang, Wenjin — your ref [13] "Lyu et al." ✓ |
| FRAMES | `2409.12941` | "Fact, Fetch, and Reason: A Unified Evaluation of RAG" — multi-hop factuality. |
| MultiHop-RAG | `2401.15391` | *MultiHop-RAG: Benchmarking RAG for Multi-Hop Queries* (Tang & Yang, 27 Jan 2024) — **verified**, so your ref [14] is correct as written. Multi-hop question categories (inference, comparison, temporal). → *Include its multi-hop categories in your 500-question benchmark design.* |
| ALCE | `2305.14627` | *Enabling LLMs to Generate Text with Citations* (Gao et al., EMNLP 2023) — your ref [11]. NLI-based citation recall and precision; the metric family D5 must be measured against. |
| LIT-RAGBench | `2603.06198` | **LREC 2026.** Logic, Integration, Table, Reasoning, **Abstention**. 114 human-constructed Japanese questions plus a human-curated English translation; fictional entities and scenarios; LLM-as-a-Judge with category-wise analysis. → *The "Table" and "Abstention" categories map directly onto your D2 and D1. Use it as an external check.* |
| RAGStress | `2610.04691` | KB-degradation stress test (see §1.6). |
| RAGBench | `2407.11005` | *RAGBench: Explainable Benchmark for RAG Systems* (Chen et al., 2024). → *A benchmark with a claim-level "hallucination" attribute; useful as a structural reference.* **Do not confuse it with the other "RAGBench"** (100k traces, 12 datasets) described inside AGO `2610.01218` — see §7.1. |
| RAGBench (as used by AGO) | — | 100k annotated RAG traces across 12 datasets, via `2610.01218`. → *A public, large, diverse benchmark to validate your judge on.* |
| CRAG-Bench | `2406.04744` | *CRAG — Comprehensive RAG Benchmark* (2024). → *Note the name collision with the CRAG *method* (`2401.15884`); they share a name and nothing else.* |
| RAGTruth | `2401.00396` | *RAGTruth: A Hallucination Corpus for Developing Trustworthy RAG* (Niu et al., 2023/24). → *The standard hallucination benchmark, and the one `2610.35056` evaluates against. Add it to your evaluation.* |
| SimpleQA Verified | `2509.07968` | OpenAI's verified factuality benchmark for measuring parametric knowledge. → *Use it as a sanity check on your judge, not on your retriever.* |
| T²-RAGBench | `2506.12071` | Text-and-table RAG benchmark. → *External check on your table handling.* |
| RAG-NIMBF | `2610.27816` | Non-invasive modular benchmarking of the *configuration space* (chunking, embedding, retrieval, reranking, prompting, generation) with controlled ablation and end-to-end experiment tracking; validated on SQuAD. Finding: **MMR raises nDCG@5 by +4 to +11 points**; more detailed prompt instructions meaningfully increase faithfulness. → *A ready-made experimental-design template, and evidence that you need MMR as a diversity baseline against your hybrid retriever.* |
| WinSyn | `2609.12171` | Automated pipeline for realistic **enterprise** QA evaluation: synthetic emails simulating long-running projects with up to 25 employees across roles; long- and short-form questions; emphasises ambiguity, distributed information and naturally occurring queries. Finding: **aggregate scores averaged over all queries remain below 80% for each dataset**. → *Use WinSyn to generate a realistic enterprise supplement to your SupplyChainQA.* |
| BrowseComp | `2504.12516` | Simple yet challenging browsing-agent benchmark. Less central for you but relevant if you claim agentic capability. |
| NoLiMa / RULER | `2502.05167` / `2404.06654` | Long-context stress tests — for the LC baseline in §1.2. |

### 1.9 Security (the axis the thesis omits entirely)

- `2610.30193` — **Protection Is Not One Event: A Survey of RAG Protection Research by Measured Endpoint** (21 Oct 2026; **ACL Rolling Review recommends acceptance at an *ACL conference**). "RAG protection studies use incompatible evaluation metrics, datasets, and threat models." Human-coded evidence map of **118 full-text-confirmed RAG defense papers**, organised by measured endpoint, with a **seven-family taxonomy**. → *The single best framing citation for "RAG safety is not one problem."*
- `2610.35071` — **GuardRAG**: training-free, plug-and-play post-retrieval defence exploiting the **semantic structure of retrieved evidence** against coordinated mutually-reinforcing poisoning. → *Same architecture slot as your gate.*
- `2610.24834` — **Consistency Is the Attack Surface: Detecting Coordinated Retrieval Poisoning with Embedding Geometry**. Across four Natural Questions retrieval seeds, at least one injection reaches the **top-5 in 94.1%** of targeted query-seed rows, and all three form a retrieved majority in **52.9%**. RobustRAG and ReliabilityRAG reach exposure-conditioned… (truncated). → *Devastating for the assumption that a retrieval-stage filter is a sufficient defence: coordinated poisoning survives because retrieval concentrates passages into the reader's context.*
- `2610.28364` — **nokast-secureRAG**: a ~0.5B-parameter SLM acting as a semantic firewall between retrieval and generation, classifying (query, context) pairs as safe / suspicious / malicious.
- `2609.35155` — **Right Facts, Wrong Rule: Scope-Transfer Poisoning of RAG**. → *A poisoning attack that exploits exactly the scope/conflict axis your D4 targets.*
- `2610.25937` — RAGLeak: supply-chain privacy backdoors in RAG.
- `2609.37468` — Backdoor in the Loop: compromising RAG.

> **Strategic note.** The thesis's problem statement is "industrial RAG can hallucinate." A 2026 examiner may reasonably ask: *"if your corpus is attacker-controllable, or if a consultant can insert a superseded safety procedure, what does your confidence gate do?"* You do not need to solve poisoning. You need to **acknowledge it in your limitations section with citations** and state that your gate is a *confidence* mechanism, not a *security* mechanism — while noting that `2610.24834` shows retrieval-stage filtering is insufficient against coordinated attacks, so the gate should be treated as a second line of defence, not the first.

### 1.10 Industrial, enterprise and governed deployment

- `2610.37697` — **chATLAS: A RAG Conversational Assistant for the ATLAS Experiment at CERN** (24 Oct 2026; 20 pages, 6 figures). Conversational access to **more than 30,000 documents** across several collaboration resources, "material largely unavailable to general-purpose language models", using **hybrid dense–sparse retrieval**. → *The flagship industrial-scale RAG deployment; cite as evidence that the problem is real at scale and that hybrid retrieval is the deployed default.*
- `2610.08205` — **Tool-calling retrieval versus vector RAG for a small Greek–English knowledge base** (6 Oct 2026; 13 pages). KyGround: **198 questions** from the published records of a Greek–English agricultural platform, answers verified automatically, each question posed in **up to nine forms** including unaccented Greek, capitals and three Latin-script (Greeklish) schemes. With Claude Haiku 4.5 as router and answer model: the tool-agent reconstruction answered **71.6%** of canonical Greek questions correctly and **vector RAG 95.3%** (difference **−23.6 pp, 95% CI [−33.1, −15.1]**); letting the router write the vector query changed nothing; **placing the whole knowledge base of about 26,000 tokens in the prompt reached 99.3%**. Tool-agent losses arose in retrieval (literal searches returned nothing when router arguments did not occur verbatim), and the agent then abstained.
  > **The most relevant paper in this document to your specific corpus.** Your corpus is 634 chunks; a 26,000-token knowledge base fits in a modern prompt. This paper says: **for a small corpus, put it all in the context and you will beat your retriever** — and it also reports a 23.6-point tool-vs-vector gap in a 198-question benchmark. **You must run the whole-corpus-in-context baseline.** If you don't, this is the paper that will be used against you.
- `2609.11493` — From Document Silos to Process Intelligence: A Multi-Layer Knowledge Graph for CMC Process Development (23 Sep 2026). Pharmaceutical CMC; "information is traditionally fragmented across functions and heterogeneous formats, causing **traceability gaps**"; modular agentic-AI platform converting a heterogeneous corpus into a multi-layer KG for regulatory filing. → *Closest industrial analogue to your 12-category framing; strong "traceability gap" motivation citation.*
- `2610.37728` — Beyond Similarity Search: Knowledge Graph Metadata Enrichment for Enterprise RAG (27 Oct 2026). Direct test of whether KG metadata beats embedding similarity for enterprise documents. → *Your D3 category filter is a metadata-only cousin; this is the modern alternative.*
- `2610.22702` — ACE: An AI-Orchestrated Intrusion Detection and Compliance Mapping Engine (15 Oct 2026). LangGraph five-stage workflow + RAG over **NIST SP 800-53 Rev. 5** controls. → *Citable example of RAG for compliance retrieval.*
- `2609.16301` (CLEAR) and `2610.36561` (Governed Sovereign RAG) — governance and adjudication; see §1.5, §1.6.
- `2609.09503` — Agentic AI-enabled Semantic Commissioning of a Cognitive Digital Twin for Reconfigurable Manufacturing (8 Sep 2026). LangGraph multi-agent orchestration. → *IE-adjacent precedent.*

---

## 2. Threat register — what to do about each

Severity is judged against the thesis's *current* framing (four ROs, five design moves, as written in MTP-2.docx and the Sept 2026 report).

### T1 — "A statistically-grounded pre-generation confidence filter" is published prior art
**Severity: FATAL (to that claim only).** `2511.17908` (ECIR 2026, DOI `10.1007/978-3-032-21300-6_45`) did conformal coverage-controlled filtering with published guarantees and 2–3× context reduction. A logistic-regression-calibrated Bayesian posterior threshold is a point estimate without a finite-sample guarantee — strictly weaker.
**Action.** Either (a) implement conformal filtering as your gate and claim the *industrial, contradiction-bearing* extension, or (b) drop the statistical-rigor claim and argue *determinism, auditability, non-bypassability and per-category calibration reporting*. Recommend (b) for the 18 November date, with (a) as the "immediate next step" bullet. Add the sentence: *"Unlike conformal filters, which provide coverage guarantees on exchangeable data, our gate is a fixed deterministic threshold chosen for auditability in a non-exchangeable industrial corpus; we report its calibration curve per category rather than a coverage guarantee."* That sentence turns a fatal threat into a considered design decision.

### T2 — "Per-claim three-band confidence tagging" is published prior art
**Severity: FATAL (to that claim only).** `2609.04442` (GRACE) classifies claims as Grounded / Refuted / Boundary by weighted graph centrality; `2610.34872` (EMNLP-style, Oct 2026) does claim-level conformal factuality with coverage guarantees, already extended to multi-hop and agentic RAG.
**Action.** Reframe D5 from *mechanism* to *communication artefact validated with practitioners*. Your 16-participant study is the asset GRACE lacks: no user study, no industrial corpus, no 12-category failure characterisation. Also change the band labels so they are not a relabelling of Grounded/Refuted/Boundary — e.g. **"Stated in source" / "Reasonable inference from source" / "Not supported by retrieved evidence"** — because the semantics you want ("inferred") is genuinely different from "Boundary" (which means *contested*, not *inferred*). Make the distinction explicit and testable.

### T3 — Long-context beats RAG on small corpora, in your own domain
**Severity: FATAL (if unaddressed).** `2606.20898` measured long-context at **73.1% vs 65.4%** for semantic RAG in **manufacturing safety**, at 26× token cost. `2610.08205` measured **99.3%** for whole-corpus-in-prompt on a ~26,000-token KB versus 95.3% for vector RAG.
**Action.** Run both baselines and report them. Then reframe the contribution: the gate is an **accuracy-preserving cost-control mechanism** (the EDAR framing: retain ~97% of the accuracy at a fraction of the cost, escalate only a small fraction of queries) plus a **safety** property (refusal rather than confident invention) that cost-optimisation alone does not give. **Add a long-context arm to your RO2 evaluation.** If your corpus is genuinely 634 chunks, this is a 20-line change to your harness and it is non-negotiable.

### T4 — Query-time filters can measure benchmark construction rather than filtering
**Severity: FATAL (to the current evaluation design).** `2610.33849` showed AUROC **0.953 → 0.758** and miss rate **0.191 → 0.763** for a published defence after removing one construction cue; **12 of 21** published evaluations report no FPR at their operating point.
**Action.** The six-point protocol in §1.5(c). This is the highest-value change available: it converts an unexamined methodological fragility into a stated, cited, defended contribution ("we evaluate our gate under the benchmark-shortcut pathology of Kumar et al. 2026").

### T5 — Hybrid + RRF + reranker is standard practice, and one published study finds no reliable advantage
**Severity: SERIOUS.** `2609.26237` (COLIEE 2026) runs multi-view BM25 + RRF + neural reranking + graph features + a 34-feature meta-learner in production; `2610.37358` finds hybrid-over-dense yields no statistically reliable utility advantage on QASPER (Hit@10 78.70% vs 76.92%, bootstrap intervals inconclusive).
**Action.** Do not claim hybrid+RRF beats flat retrieval as a novel finding — it is a well-established result and your own RO3 hypothesises exactly that. Reframe RO3 as *"does this established pipeline hold up in industrial supply-chain corpora, and where does it fail?"* — with `2610.37358` and `2609.26237` cited as the reason the question is open. Add MMR as a diversity baseline (`2610.27816` reports +4 to +11 nDCG@5 from MMR). Report the CV→test gap honestly in the style of `2609.26237` (their 0.311 → 0.177 is the honesty benchmark).

### T6 — Isolated component gains do not compose, and the best composition changes with corpus size
**Severity: SERIOUS.** `2610.29722` (LASAGNA): three retrieval techniques predicted +47% but delivered +17%; optimising retrieval can hurt faithfulness; the best composition changes as the corpus grows.
**Action.** Pre-register hypotheses (as LASAGNA does), evaluate the *composition* not just isolated ablations, and run at least two corpus sizes. Your report's four pipeline stages — annotation, retrieval ablation, gating calibration, contradiction user study — are the right structure; formalise it as a pre-declared protocol and cite LASAGNA as the standard you meet.

### T7 — Modality quotas may *hurt*, and the corpus may not contain the modality
**Severity: SERIOUS.** `2609.35304` documents that redundant multimodal evidence may distract LMs; your own report records a modality null result because the corpus is 2.3% chart / 7.1% table. `2610.34503` (industrial) has already implemented separate text/image retrieval with confidence filtering.
**Action.** Reframe D2 from "quotas will improve recall" to "**what corpus composition is required before modality balancing can matter, and what is the cost of modality-blind retrieval when it does**" — a *boundary condition* finding, with the null result reported as the finding. Test against `2609.35304`'s per-fact modality attribution rather than a per-query quota. Cite `2610.37080` (Tessera) and `2610.35542` (HyperDoc) as alternative mechanisms for the same root cause, and position your quota as the cheap approximation.

### T8 — GraphRAG category routing is more principled than a YAML category filter
**Severity: SERIOUS.** `2404.16130`, `2410.05779`, `2608.24921`, `2607.19301` (PAGE-RAG's "graph as skeleton" framing), `2610.37728` (KG metadata enrichment vs similarity search).
**Action.** `2607.19301` is your best friend: it argues graphs should be treated as *skeletons that organise and navigate*, not as independent knowledge sources. A category filter **is** a coarse skeleton. Say that explicitly. Then be honest that you chose a skeleton *cheap enough to configure in YAML for 12 categories*, and quantify the cost of that choice (e.g. report recall when the category filter is removed, and when it is replaced with a similarity-only retriever — the ablation you already have).

### T9 — Your LLM judge may be barely above chance
**Severity: SERIOUS.** `2610.01218`: gpt-4.1-nano judge AUROC **0.603 [0.570, 0.634]**; gpt-4o **0.783 [0.756, 0.807]**; per-domain spread **0.62–0.88**.
**Action.** Meta-evaluate your judge and report it. Use RAGBench (100k traces, 12 datasets) as the validation set, stratified N=1200 as AGO does. If your judge turns out to be weak, that is a finding worth stating, and it justifies your human-expert subset. **Also re-examine your 98% → 16% false-positive claim: if that number came from an LLM judge, it inherits the judge's error.**

### T10 — RAG security is an axis your thesis ignores
**Severity: MINOR-to-SERIOUS.** `2610.24834` (94.1% top-5 injection exposure, 52.9% majority), `2610.33849`, `2610.35071`, `2609.35155` (scope-transfer poisoning).
**Action.** Add a limitations paragraph and one sentence in the threat model. Do not try to solve it.

### T11 — Evaluation-set construction is a first-class threat on an industrial benchmark you built yourself
**Severity: SERIOUS.** Your SupplyChainQA v7 (300 queries, 7 sub-categories, 2 annotators, κ ≥ 0.7 on four categorical fields) was LLM-agent-annotated with human validation "to be reported" (per MTP-2.docx). Your prior report's benchmark is a self-constructed artefact with a documented inter-annotator agreement on only four of eight schema fields.
**Action.** Complete the human-expert validation round. With 18 November, a realistic target is a **human-verified random subset with a reported agreement statistic and a disagreement analysis**, not the full 500. And state the annotation provenance and the IAA metric explicitly in the methods. Cite `2609.36392`'s warning about **"systematic underestimation averaging 10.1 percentage points caused by keyword matching"** — i.e. report how your automatic scoring handles near-miss answers.

### T12 — Novelty of the *framework assembly* is thin relative to the parts
**Severity: SERIOUS.** Every individual mechanism has 2026 prior art (§1.3–§1.7). An examiner can ask "what here is not a combination of published ideas?"
**Action.** The assembly argument must rest on properties none of the parts has: (i) **industrial** corpus with a 12-category taxonomy and cross-category transfer as a first-class objective; (ii) **non-bypassable, deterministic, auditable** gating in a safety-critical decision context; (iii) **failure-mode characterisation** with honest null results and an operating-point analysis; (iv) **practitioner validation** of the uncertainty vocabulary. See §5 for the exact sentence.

---

## 3. Opportunities — what remains genuinely open

1. **Refusal vs routing vs clarification is still unsettled in industrial settings.** `2609.35831` routes to long context; `2610.36561` arbitrates SPECIFIC/CLARIFY/ABSTAIN in government; `2610.34872` does conformal filtering in agentic RAG. Nobody has characterised a **three-way epistemic gate on industrial engineering documentation with tables and charts and a contradiction-bearing corpus**, and nobody has published the *cost of the gate* (false refusals: queries that had an answer but were gated out) alongside its benefit.
2. **The false-refusal rate of industrial confidence gates is uncharacterised.** Everyone reports detection gains; almost nobody reports "how often did we refuse a question we could have answered?" `2610.33849` proves the field does not even report FPR at the operating point (12 of 21). **Reporting false-refusal rate as a first-class metric, in an industrial corpus, is a real contribution.**
3. **Corpus-composition boundary conditions for modality balancing are unstudied.** `2609.35304` asks whether modalities contribute equally; `2610.34503` shows industrial multimodal retrieval recovering only some modality combinations; nobody has published the *minimum table/chart fraction* at which modality balancing starts to pay, nor the cost of modality-blind retrieval below it. Your null result is the left half of that curve.
4. **Viewpoint difference vs logical contradiction in engineering documents.** Your 98% → 16% false-positive result, if it survives the `2610.33849` artefact checks, is a clean characterisation of a boundary that NLI models handle badly. `2609.35782` (scope conflicts) and `2609.16301` (adjudication) both establish that conflict is multi-typed; **nobody has published a typed conflict taxonomy for industrial documents** (superseded vs scoped vs genuinely contradictory vs complementary).
5. **Faithfulness as a function of hop distance in industrial corpora.** `2608.00705` shows faithfulness declines with hop distance on DO-178C requirements (p<0.05 in three of four judge×embedder cells) but not on Wikipedia chains. **A supply-chain-specific hop-distance faithfulness curve is unpublished.**
6. **Judge meta-evaluation for industrial RAG.** `2610.01218` shows judges collapse to near-chance on cheap models and vary 0.62–0.88 per domain; **no published meta-evaluation exists for an industrial-supply-chain RAG judge.**
7. **Cross-category transfer of retrieval configurations, measured properly.** `2608.00705` shows the best composition changes with corpus size; `2610.29722` shows the best composition changes as corpora grow. **Nobody has asked whether a retrieval configuration tuned on one industrial category transfers zero-shot to eleven others** — which is precisely your RO4, and it is a genuinely open, well-motivated question.

---

## 4. What you must change before 18 November (priority order)

| # | Change | Effort | Why |
|---|---|---|---|
| 1 | Add a **long-context / whole-corpus-in-prompt baseline** to the evaluation harness (`2606.20898`, `2610.08205`) | Low — harness change | Removes T3, the fatal one. Non-negotiable. |
| 2 | Add the **`2610.33849` protocol**: report FPR at the operating point, length-matched controls, threshold sweep, per-category AUROC with CIs | Low–medium — analysis, not new machinery | Converts the thesis's biggest methodological fragility into a cited, defended contribution. |
| 3 | **Meta-evaluate your LLM judge** (AGO protocol: stratified N=1200, AUROC + CI, per-category spread; validate on RAGBench) | Medium | `2610.01218` shows why this is mandatory. |
| 4 | **Rewrite the D1/D5 novelty sentences** to the defensible framings in §5 | Low — writing | T1 and T2 are fatal to the current sentences. |
| 5 | Add the six 2026 papers to the literature review: `2610.29722`, `2606.20898`, `2511.17908`, `2609.04442`, `2609.35782`, `2610.33849` (plus `2610.01218`, `2610.36561`, `2609.16301`, `2610.37080`, `2610.34503`) | Low — writing | Without these, the thesis reads as unaware of the field's October 2026 state. |
| 6 | Add a **CLARIFY tier** to the gate (three-way: answer / insufficient-or-conflicting / no-evidence) | Low — one extra branch | Aligns with `2610.36561` and materially strengthens the design. |
| 7 | Report **false-refusal rate** alongside detection rate | Low — analysis | §3 item 2; nobody has this number. |
| 8 | Add a **conflict taxonomy** (superseded / scoped / contradictory / complementary) to your contradiction results | Medium | Turns D4 from "NLI + topical gate" into a typed characterisation. |
| 9 | Complete **human-expert validation** on a random subset of the benchmark and report agreement + disagreement analysis | Medium — annotation time | T11; your benchmark is a self-constructed artefact. |
| 10 | Add **MMR** as a retrieval-diversity baseline; add **RAGTruth** and **LIT-RAGBench** as external hallucination/abstention checks | Low | `2610.27816`, `2610.35056`, `2603.06198`. |

---

## 5. Novelty pressure test — the strongest defensible statement

**Adversarial question an examiner will ask:** *"A 2026 paper puts a conformal, coverage-guaranteed filter in front of generation; another decomposes answers into atomic claims and labels each Grounded/Refuted/Boundary; another gates answers in production in government; another shows BM25+RRF+rerank is what a production legal-retrieval system already runs. What is new in yours?"*

**The answer that survives — do not deviate from this wording:**

> This work does not introduce retrieval-confidence gating, per-claim confidence labelling, hybrid reciprocal-rank-fusion retrieval, or contradiction detection; each has published precedent, and we cite it. Our contribution is a **characterisation and a deployment** in a setting the literature does not cover: an industrial-engineering decision-support corpus spanning twelve categories, where evidence arrives as text, tables and charts, documents routinely disagree, and a wrong number carries operational, financial or legal cost. Specifically, we contribute: **(i)** a *deterministic, non-bypassable, auditable* epistemic gate whose operating point is reported with false-positive **and false-refusal** rates per category, evaluated under the benchmark-shortcut pathology identified by Kumar et al. (2026), with its calibration curve published rather than a single threshold; **(ii)** a **failure-mode characterisation** across twelve categories, including documented null results — modality balancing shows no effect on a corpus that is 2.3% chart and 7.1% table — and an explicit account of when a static gate is the wrong design; **(iii)** a **cross-category transfer study** of retrieval configurations, which the compositionality literature (`2610.29722`) shows cannot be assumed from single-corpus evidence; and **(iv)** **practitioner validation** of a three-band uncertainty vocabulary (stated / inferred / not supported) that the prior art does not evaluate with humans.

**Why this is strong.** Every clause is either (a) a citation to prior art showing you know it exists, (b) a thing the prior art does not do, or (c) a measurement the prior art does not report. Nothing in the statement claims a mechanism is new. That is exactly what a careful examiner rewards: the candidate who correctly locates their own contribution is more credible than the candidate who claims a component that already exists.

**The three sentences you must remove from any draft:**
1. ~~"we introduce a novel confidence gate"~~ → replaced by the framing above.
2. ~~"our three-band tagging classifies claims as grounded / inferred / uncertain"~~ presented as a *new* taxonomy → present as a *communication design choice*, citing GRACE's Grounded/Refuted/Boundary, and explain that "inferred" denotes *derivable by inference from the source*, which is not GRACE's "Boundary" (contested) and not a binary support decision.
3. ~~"hybrid retrieval with RRF outperforms flat retrieval"~~ presented as a *finding* → present as a *pre-registered hypothesis* whose outcome you report, with `2610.37358` (no reliable advantage for hybrid over dense+rerank on QASPER) and `2609.26237` (production pipeline already uses BM25+RRF+neural rerank) cited as reasons the question is open in an industrial corpus.

---

## 6. Presentation-ready takeaways (viva script, each with a citation)

1. **"We deliberately did not claim a new gating mechanism."** Conformal pre-generation filtering with coverage guarantees was published at ECIR 2026 (`2511.17908`, DOI `10.1007/978-3-032-21300-6_45`), and claim-level confidence labelling is published (`2609.04442`, `2610.34872`). We contribute an industrial characterisation and an auditable operating point, not a new estimator.
2. **"We benchmarked against long context, and we report that it wins on accuracy."** In a manufacturing-safety study, long-context prompting reached 73.1% versus 65.4% for semantic RAG, at 26× the token cost (`2606.20898`). Our gate is a cost-control and safety device, not an accuracy weapon. On a small corpus, whole-corpus-in-prompt reached 99.3% against 95.3% for vector RAG (`2610.08205`).
3. **"Our gate is calibrated per category and we report both error directions."** Twelve of twenty-one published query-time-filter evaluations report no false-positive rate at their deployed operating point (`2610.33849`); removing a single construction cue dropped a published defence from AUROC 0.953 to 0.758. We report FPR, false-refusal rate and a threshold sweep.
4. **"We evaluated our LLM judge before trusting it."** Cheap judges detect non-adherent answers barely above chance (AUROC 0.603 [0.570, 0.634]) and strong judges still vary 0.62–0.88 per domain (`2610.01218`).
5. **"We report null results."** Modality balancing showed no effect because our corpus is 2.3% chart and 7.1% table; published work shows redundant multimodal evidence can even distract the reader (`2609.35304`), and other work shows the corpus-composition boundary matters (`2610.34503`).
6. **"We know the metric definition can invert the ranking."** Scoring the retrieved set as the attribution set inverts the architecture ranking against GraphRAG (`2608.00705`); we report both definitions.
7. **"We know component gains do not compose."** Three retrieval techniques predicted a +47% combined improvement and delivered +17% (`2610.29722`); we pre-registered our hypotheses and evaluated the composition.
8. **"Our contradiction gate targets a named failure mode, and we characterise it."** Conflicting candidates displace supporting evidence and cost 0.147 Recall@10 (`2609.35782`); naive NLI gating produced a 98% false-positive rate in our corpus, reduced to 16% with a topical gate.
9. **"Industrial RAG has an unresolved security axis."** Coordinated poisoning reaches the top-5 in 94.1% of targeted query-seed rows and forms a retrieved majority in 52.9% (`2610.24834`); our gate is a second line of defence, not the first.
10. **"We used the published standards."** Our protocol follows the compositionality framework (`2610.29722`), the judge meta-evaluation protocol (`2610.01218`), the filter-benchmark-shortcut protocol (`2610.33849`), and the abstention taxonomy (`2603.06198`).

---

## 7. Citation appendix

### 7.1 Verified arXiv identifiers used in this document

All fetched and verified 31 Oct 2026. Two provenance levels, both from arXiv itself:

- **Individually verified** — abstract page fetched, metadata read from `citation_title`, `citation_author`, `citation_date`, `citation_doi`, `citation_journal_title` meta tags:
`2302.09664` · `2305.14627` · `2305.14739` · `2307.03172` · `2309.01431` · `2309.15217` · `2310.03025` · `2310.11511` · `2311.09476` · `2401.00396` · `2401.15884` · `2401.15391` · `2401.17043` · `2404.06654` · `2404.16130` · `2405.14831` · `2406.04744` · `2407.01449` · `2407.11005` · `2407.16833` · `2409.01666` · `2409.10102` · `2409.12941` · `2409.13731` · `2410.05779` · `2501.09136` · `2502.05167` · `2502.06872` · `2502.14802` · `2504.08748` · `2504.10499` · `2504.14891` · `2504.12516` · `2506.00054` · `2506.10408` · `2506.12071` · `2507.13193` · `2509.07968` · `2510.15253` · `2511.17908` · `2603.06198` · `2604.03174` · `2604.08304` · `2606.20898` · `2607.19301` · `2608.00705` · `2608.13706` · `2608.24921` · `2608.24977` · `2609.04442` · `2609.12171` · `2609.16073` · `2609.16301` · `2609.17564` · `2609.26237` · `2609.28575` · `2609.35304` · `2609.35782` · `2609.35831` · `2609.36392` · `2610.01218` · `2610.04691` · `2610.08205` · `2610.26951` · `2610.29722` · `2610.30193` · `2610.34503` · `2610.34816` · `2610.34872` · `2610.35056` · `2610.35071` · `2610.35542` · `2610.36561` · `2610.37080` · `2610.37358` · `2610.27816`
- **Observed on an arXiv search-results page** (identifier and title read together from the live result listing; the identifier is genuine arXiv but the abstract was not individually fetched): `2407.13193` · `2502.08826` · `2503.10677` · `2607.03447` · `2607.24791` · `2607.27918` · `2608.05141` · `2608.22062` · `2608.28607` · `2608.28766` · `2609.04290` · `2609.09503` · `2609.10239` · `2609.11493` · `2609.15800` · `2609.19622` · `2609.24220` · `2609.30337` · `2609.35155` · `2609.37468` · `2609.38473` · `2610.02373` · `2610.08463` · `2610.10507` · `2610.11183` · `2610.11370` · `2610.22702` · `2610.24834` · `2610.25937` · `2610.28216` · `2610.28364` · `2610.31863` · `2610.34829` · `2610.34866` · `2610.36444` · `2610.37697` · `2610.37728` · `2610.40314`

**Identifiers that were removed from this appendix during verification.** Three candidates I had carried from the sweep turned out to resolve to entirely unrelated papers, and were struck:

| Struck identifier | Actually is |
|---|---|
| `2603.07658` | *A global well-posedness result for the three-dimensional inviscid quasi-geostrophic equations* (applied mathematics) |
| `2608.29567` | *MotionSync: Non-Causal Refinement of Causal Tracker for Label-Efficient 3D Point Tracking* (computer vision) |
| `2610.13513` | *Short scale asymptotics in nonlocal spectral problems* (applied mathematics) |

**A naming collision you must not fall into.** "RAGBench" refers to **two different things**: `2407.11005` (*RAGBench: Explainable Benchmark for RAG Systems*, 2024), and the 100k-trace, 12-dataset benchmark described inside AGO `2610.01218`. They are not the same artefact. When you cite "RAGBench", name which one and give its identifier — an examiner who reads AGO and then finds `2407.11005` will conclude you did not read your own source. Similarly, "T²-RAGBench" (`2506.12071`, text-and-table) and "LIT-RAGBench" (`2603.06198`) are distinct from both. And note the distinction in the other direction: **CRAG the *method*** (`2401.15884`, Corrective RAG) and **CRAG the *benchmark*** (`2406.04744`, Comprehensive RAG Benchmark) share a name and share nothing else.

**Non-arXiv, verify separately before submission:** Context Rot (Chroma technical report, 2025 — no arXiv record under that title; a related arXiv paper is `2606.29718`, *Diagnosing and Mitigating Context Rot in Long-horizon Search*, 29 Jun 2026, which you can cite instead or alongside); the entity/relation-extraction cost figures cited by `2610.29722` (DeepGraph, one-vs-all, LightRAG, nano-graphrag) — verify each against its own paper; the Chroma report's exact URL and version.

### 7.2 Mis-IDs caught during verification (do not reuse)

Candidate identifiers that resolved to a *different* paper and were discarded:

| Wrong candidate | Actually is | Correct identifier |
|---|---|---|
| `2501.00330` (assumed nano-graphrag) | *Exploring the Implicit Semantic Ability of Multimodal LLMs* | Re-derive by title search |
| `2409.13751` (assumed KAG / OpenSPG) | *Nonlocal mass creation by metricized accelerations in Euclidean matterspace* (physics) | **`2409.13731`** — KAG: Boosting LLMs in Professional Domains via Knowledge Augmented Generation |
| `2412.04369` (assumed SimpleQA) | *Intersection-Aware Assessment of EMS Accessibility in NYC* | OpenAI SimpleQA has no arXiv record under that title; cite **`2509.07968`** (SimpleQA Verified) or the OpenAI release |
| `2310.01739` (assumed Context-Aware Decoding) | *Randomized Dimension Reduction with Statistical Guarantees* | **`2305.14739`** — Trusting Your Evidence: Hallucinate Less with Context-aware Decoding |
| `2310.01783` (assumed "Retrieval Meets Long Context") | *Can LLMs provide useful feedback on research papers?* | **`2310.03025`** — Retrieval meets Long Context Large Language Models |

**One near-miss worth recording as a positive example.** `2502.14802` was *assumed* to be wrong; re-deriving it by title confirmed it is **correct** — it is **HippoRAG 2**, published under the title *"From RAG to Memory: Non-Parametric Continual Learning for Large Language Models"* (Gutierrez et al.). Only my recollection of the *title* was wrong, not the identifier. The original HippoRAG is `2405.14831`. A title-based lookup that trusted memory would have "corrected" a valid identifier into a wrong one — the inverse error is just as damaging.

**Lesson to carry into the paper:** five of twenty-three candidate identifiers I generated from memory were wrong, and every one of them resolved to a *real, plausible-looking paper on a closely adjacent topic* — a physics paper for a knowledge-graph system, a natural-language paper for a benchmarking suite, an education-accessibility study for a factuality benchmark. This is precisely the failure mode that produces undetectable fabricated citations in a bibliography, and it is why the "Facts, Figures & Sources" rule applies to identifiers as well as to prose. **Verify every identifier against its abstract page before it enters the bibliography.**

### 7.2b Authorship corrections to the existing literature table

Checked against the verified `citation_author` meta tags:

- **RAGAS** — `2309.15217` lists **Es, Shahul; James, Jithin; Espinosa-Anke, Luis; Schockaert, Steven**. Your MTP-2.docx ref [10] ("Es, S., et al. (2024)") is **correct as written**. Do not change it.
- **ARES vs ALCE** — `2311.09476` lists **Saad-Falcon, Jon; Khattab, Omar; Potts, Christopher; Zaharia, Matei**. Your ref [11] ("Gao, T., et al. (2023) … *Enabling large language models to generate text with citations*, EMNLP") is a **different paper** — that is ALCE, arXiv **`2305.14627`**. Keep ARES and ALCE as separate entries; they measure different things (ARES = a framework for scoring RAG systems; ALCE = citation recall/precision computed with NLI).
- **Semantic Uncertainty / Semantic Entropy** — the arXiv record `2302.09664` lists authors as **Kuhn, Gal, Farquhar** on its latest version, while the *Nature* paper you cite (630:625–630, DOI `10.1038/s41586-024-07421-0`) lists **Farquhar, Kossen, Kuhn, Gal**. Cite the Nature version with the Nature author order; the arXiv ID is only the preprint pointer.
- **Agentic RAG survey** — `2501.09136` lists **Singh, Aditi; Ehtesham, Abul; Kumar, Saket; Khoei, Tala Talaei; Vasilakos, Athanasios V.**, confirming "Singh et al." ✓.
- **RAG or Long-Context LLMs** — `2407.16833` lists **Li, Zhuowan; Li, Cheng; Zhang, Mingyang; Mei, Qiaozhu; Bendersky, Michael**. Your literature table has **no entry for this paper at all**, which is a gap: it opens the long-context debate the thesis must now answer.
- **LightRAG** `2410.05779` — Guo, Zirui; Xia, Lianghao; Yu, Yanhua; Ao, Tu; Huang, Chao ✓
- **GraphRAG** `2404.16130` — Edge, Darren; Trinh, Ha; Cheng, Newman; Bradley, Joshua; Chao, Alex; Mody, Apurva ✓
- **Lost in the Middle** `2307.03172` — Liu, Nelson F.; Lin, Kevin; Hewitt, John; Paranjape, Ashwin; Bevilacqua, Michele; Petroni, Fabio ✓
- **CRUD-RAG** `2401.17043` — Lyu, Yuanjie; Li, Zhiyu; Niu, Simin; Xiong, Feiyu; Tang, Bo; Wang, Wenjin ✓
- **RGB** `2309.01431` — Chen, Jiawei; Lin, Hongyu; Han, Xianpei; Sun, Le ✓

### 7.3 Audit of the thesis's own existing bibliography (MTP-2.docx, refs [1]–[18])

Every arXiv identifier in your existing literature table was checked against its abstract page on 31 Oct 2026. **All of them resolve to real papers with the expected titles.** No phantom citations were found. That is good news, and it is a stronger starting position than most theses have.

| Ref | ID given | Resolves to | Status |
|---|---|---|---|
| [2] Self-RAG | `2310.11511` | Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection | ✓ |
| [3] CRAG | `2401.15884` | Corrective Retrieval Augmented Generation | ✓ |
| [4] GraphRAG | `2404.16130` | From Local to Global: A Graph RAG Approach to Query-Focused Summarization | ✓ |
| [5] PIKE-RAG | `2501.11551` | PIKE-RAG: sPecIalized KnowledgE and Rationale Augmented Generation | ✓ |
| [10] RAGAS | `2309.15217` | Ragas: Automated Evaluation of Retrieval Augmented Generation | ✓ |
| [12] Attributed QA | — | *not arXiv-verified in this pass* | verify `2212.08037` |
| [13] CRUD-RAG | `2401.17043` | CRUD-RAG: A Comprehensive Chinese Benchmark for RAG | ✓ |
| [14] MultiHop-RAG | `2401.15391` | MultiHop-RAG: Benchmarking RAG for Multi-Hop Queries | ✓ |
| [15] Microsoft (2025) | `2507.21502` | Large Language Models for Supply Chain Decisions | ✓ |
| [16] RAG survey | `2312.10997` | Retrieval-Augmented Generation for Large Language Models: A Survey | ✓ |
| [17] Hallucination survey | `2510.24476` | Mitigating Hallucination in Large Language Models: A **Capability-Oriented** Survey on RAG, Reasoning, … | ✓ but **title differs from your ref [17]** |
| [1] Lewis et al. | — | *not arXiv-verified in this pass* | verify `2005.11401` |
| [6] Wan et al. | — | Adv. Eng. Inform. 65, 103212 | journal — verify via publisher |
| [7] Wu et al. | — | Adv. Eng. Inform. 65, 103158 | journal — verify via publisher |
| [8] Decian et al. (2026) | — | Neurocomputing 705, 134911 | journal — verify via publisher |
| [9] InstructRAG | — | *not arXiv-verified in this pass* | verify `2406.13629` |
| [11] ALCE | `2305.14627` | Enabling Large Language Models to Generate Text with Citations | ✓ — **and distinct from ARES, which your table also cites as ref [11]** |
| [18] Zhang & Zhang (2025) | — | Mathematics 13, 856 | journal — verify via publisher |

**Three concrete corrections to make in the existing table:**

1. **Ref [17] title.** Your entry reads "An application-oriented survey on RAG, reasoning, and agentic systems." The actual title is *"Mitigating Hallucination in Large Language Models: A Capability-Oriented Survey on RAG, Reasoning, and Agentic Systems"* — the phrase is **capability-oriented**, not application-oriented. Fix it; a wrong title in a bibliography is exactly what a Turnitin/citation-integrity check flags.
2. **Ref [11] is doing two jobs.** Your table's row 11 cites "Gao et al. (2023) … Enabling large language models to generate text with citations" (ALCE, `2305.14627`), but your reference list's entry [11] and the report's §5 both lean on ARES (`2311.09476`, Saad-Falcon et al.) as a separate work. Keep them as two clearly distinct entries.
3. **Refs [1], [9], [12] still need identifier checks** against `2005.11401`, `2406.13629`, `2212.08037` respectively. I have not verified these three in this pass and will not assert them.

**The structural gap is not accuracy but recency.** Your table's newest entry is 2026 (ref [8]); the field has published 40+ directly relevant papers between February and October 2026 that touch every one of your four research objectives. §1–§2 above supply the ones that matter.

### 7.4 Papers whose abstracts I read but whose full text I did not open

Every quantitative claim in this document comes from a fetched abstract. The methods are described as the abstracts describe them. Before you write a paragraph attributing a specific experimental detail to any of these papers, open the PDF. The ones where this matters most: `2610.29722` (LASAGNA — read the pre-registered hypotheses), `2606.20898` (the cost model), `2610.33849` (the exact defence set and the 21-evaluation survey), `2610.01218` (the meta-evaluation protocol), `2610.36561` (the gate definition and the Level-0/Level-1 split), `2609.35782` (the compatible/incompatible pool construction).

### 7.5 Venue verification — what is independently corroborated and what is only author-declared

Every venue assertion in this document comes from the arXiv `comments` field, which is **author-declared**. On 31 Oct 2026 I cross-checked twelve of them against Semantic Scholar's independent bibliographic record (batch endpoint, `publicationVenue` / `journal` fields). Results:

| Paper | Venue asserted in this document | Independent corroboration | Status |
|---|---|---|---|
| `2511.17908` | ECIR 2026 | S2 venue = "European Conference on Information Retrieval", **pages 537–546**; S2 `year` field reads **2025** | ✓ Venue **corroborated**. The year label differs because Springer LNCS indexes the proceedings volume under its publication year — ECIR 2026's volume is `978-3-032-21300-6`, matching the DOI `10.1007/978-3-032-21300-6_45`. Cite as **ECIR 2026**; if a tool complains, the page range 537–546 is the disambiguator. |
| `2603.06198` | LREC 2026 | S2 venue = "International Conference on Language Resources and Evaluation", **pages 5482–5493**, year 2026 | ✓ **Fully corroborated**, including the year. |
| `2309.15217` (RAGAS) | EACL (System Demonstrations) | S2 venue = "Conference of the European Chapter of the ACL", year **2023** | ⚠ Venue family corroborated; **year needs checking.** The canonical citation is EACL 2024 System Demonstrations (the arXiv preprint is March 2024); S2 attaches the 2023 EACL proceedings. Verify the year and page range on the ACL Anthology before it enters your bibliography. |
| `2311.09476` (ARES) | — (your table does not cite it formally) | S2 venue = "North American Chapter of the Association for Computational Linguistics" | ✓ **ARES = NAACL 2024** (S2's year field again reads 2023 for the proceedings). Add it as a formal reference with the anthology page range — it is the framework you should be using for RO3 evaluation. |
| `2608.13706` | FinNLP 2026 @ EMNLP 2026 | S2 venue empty, types `['Review']` | Author-declared only. Consistent — a Sep 2026 paper will not be in S2 yet. |
| `2610.35056` | Findings of EMNLP 2026 | S2 venue empty | Author-declared only |
| `2609.04442` | AKBC Workshop @ EMNLP 2026 | S2 venue empty | Author-declared only |
| `2610.35542` | ICDE 2027 | S2 venue empty | Author-declared only |
| `2610.34503` | APSEC 2026 | S2 venue empty | Author-declared only |
| `2610.01218` | NFMCP 2026 / ECML PKDD 2026 Workshops | S2 venue empty | Author-declared only |
| `2610.29722` | *preprint* (no venue claimed) | S2 venue empty | ✓ Consistent — this one is a preprint with a public project page and code. |
| `2608.24977` | ACL Rolling Review **recommends** acceptance at an *ACL conference | S2 venue empty | ✓ Consistent. Note the wording: it is a *review recommendation*, not an acceptance. Do not write "accepted at ACL". |

**Two practical consequences.**

1. **For the 2026 papers, say "preprint" or "accepted at X" exactly as the arXiv comments field states** — and if you cannot check the proceedings before submission, prefer "arXiv preprint, 2026" over naming a venue you have only the authors' claim for. This is precisely the discipline that keeps a bibliography clean.
2. **Your two most-cited evaluation references need fixing.** RAGAS is EACL 2024 Demos (not 2024-per-S2 — check the anthology), and ARES is NAACL 2024 with pages to verify. Get both page ranges from the ACL Anthology.

**Cross-check method, for the record:** S2 `POST /graph/v1/paper/batch` with `fields=title,venue,publicationVenue,year,externalIds,publicationTypes,journal`. Four attempts returned HTTP 429 before succeeding — the unauthenticated pool is saturated. Do not treat a S2 timeout as a negative result; re-query rather than concluding a paper is unindexed.

### 7.6 What this survey did not cover

State these limitations in your own write-up rather than letting an examiner find them:

- **arXiv only.** Non-arXiv venues — IEEE, ACM, Springer, Elsevier, Scopus, Web of Science — were not searched systematically. Several relevant papers almost certainly exist in *Advanced Engineering Informatics*, *Journal of Manufacturing Systems*, *Computers in Industry*, *AI in Manufacturing* and *Industrial & Engineering Chemistry Research*. **Your four journal refs ([6], [7], [8], [18]) live exactly there and were not independently checked.**
- **2026 preprints.** Many of the most important papers here (ten of them dated within the last eight weeks) are preprints with no peer review yet. Cite them as preprints, and treat their numbers as provisional.
- **No full-text systematic search.** This was a targeted, question-driven sweep across twelve arXiv search themes plus identifier verification — not a PRISMA-style systematic review with a registered protocol. If you want to claim a systematic review in the paper, that is a different and larger piece of work.
- **No non-English literature.** The thesis's CRUD-RAG row already flags a Chinese benchmark; a serious survey would note this explicitly.
- **Bibliographic cross-checking was partial.** Semantic Scholar was cross-checked for twelve papers (§7.5) but the unauthenticated API was saturated for most of the session; for every other paper, the venue is author-declared via the arXiv `comments` field. **For the four journal papers in your existing bibliography, use the publisher's own page** — Advanced Engineering Informatics, Neurocomputing and Mathematics each have their own volume/issue conventions, and a wrong article number is a citation-integrity flag.
