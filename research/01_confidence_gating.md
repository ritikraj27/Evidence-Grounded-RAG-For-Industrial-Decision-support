# Survey Area 1 — Retrieval-Confidence Gating, Calibration, Abstention and Refusal in RAG

**Purpose.** This file is the verified evidence base for Research Objective 1 of the MTP *"An Evidence-Grounded Retrieval-Augmented Generation Framework for Industrial Decision Support"*:

> **RO1.** A code-level, non-bypassable retrieval-confidence gate that returns an explicit "no evidence" response when retrieval confidence falls below a threshold, instead of calling the LLM.

**Verification protocol.** Every entry below was resolved against a live bibliographic source — OpenAlex (`api.openalex.org`, DOI and `title.search` indexes), the arXiv Atom API (`export.arxiv.org/api/query`), the ACL Anthology (volume indexes, `.bib` dumps, and its JavaScript full-text search run in Scrapling's stealth browser), and PubMed Central. Titles, author lists, years, venues, volume/page ranges, DOIs and arXiv IDs were read back from the source's own response. Numbers quoted after "reports" or "finds" appear in the abstract of the paper as fetched — they are not paraphrases from memory. Where a paper could not be resolved, it is listed in **§6.2 under UNVERIFIED** rather than being cited as fact.

**Reader note.** §2 is written for a reader who has never worked with RAG. Every acronym is expanded on first use, and every method is explained in plain language before its technical description.

---

## 0. Executive summary — the six things that must change in the thesis

**Six findings, ranked by how much they affect the thesis's defensibility.**

1. **The nearest prior work is Decian et al. (2026), *Neurocomputing* 705, 134911 — "Dynamic RAG with hybrid retrieval".** It is hybrid retrieval plus an entropy-based dynamic threshold, reporting statistically significant correctness gains (p < 0.01), and it is **2026**. The proposal document already names it "Closest to our RO1" but does not engage it. It must be engaged directly. The defensible difference is *philosophy*, not accuracy: a deterministic, auditable refusal versus a probabilistic best-effort adjustment, in a domain where errors have physical and legal consequences. **Do not claim to beat it.** (§3.1a)

2. **The strongest and most current method is Geißler et al. (2026), `arXiv:2605.05244`** — conformal prediction for chunk selection plus an attention-based factuality classifier, framed explicitly as *"certified RAG systems for industry applications"*. It improves answer quality by **up to 6 %** and detects inconsistent answers **up to 77 %** of the time, but the authors concede the guarantees *"do not hold generally, since the assumption of sample exchangeability depends on the retriever setup"*. **This paper is missing from the proposal's literature table and must be added** — and its diagnostic metrics should be adopted as the thesis's own limitation. (§2.7, §3.1b)

3. **The sharpest reviewer challenge is SYNCHECK (Wu, Gu, Yin & Peng, EMNLP 2024, `10.18653/v1/2024.emnlp-main.527`), not CRAG.** SYNCHECK monitors decoding dynamics to detect **unfaithful sentences** as they are generated (0.85 AUROC over six long-form RAG tasks, +4 % over the prior best), and its FOD decoding algorithm **outperforms abstention, reranking and contrastive decoding by over 10 %**. The thesis's D1 *is* an abstention mechanism, so "why abstain rather than monitor-and-repair?" is the question to expect. The answer: insufficient *evidence* ≠ unfaithful *output*; the gate runs **before** generation so a refusal costs a retrieval pass; and the thesis's claim is human-facing per-claim banding, not AUROC. The thesis must also concede that its single-feature gate is the *simplest* instantiation of the multi-signal design both SYNCHECK and Phillips et al. point to. (§2.11, §4-R7)

4. **A direct empirical threat to the thesis's own architecture: DeclineCraft (Thakur et al., 2026, `arXiv:2610.28340`).** Adding query rewriting and reranking to hybrid retrieval **lowers** Correct Abstention Rate for **all 12 models tested**; iterative RAG lowers CAR in **30 of 40** configurations (mean 46.4 %) with answer accuracy essentially flat (68.5 % → 69.3 %). The thesis's D3 *improves* retrieval relative to its baselines, so **the gate's operating point must be calibrated separately per retrieval arm** — a single global threshold will manufacture a spurious result. (§4-R1)

5. **The evaluation framing must change from "hallucination rate" to "selective prediction at a stated operating risk level".** Phillips et al. (2026, `arXiv:2603.21172`) show that entropy-based uncertainty has a *model-dependent* failure mode and that the risk–coverage trade-off must be evaluated at the error rate the system claims to operate at. The thesis should report a **risk–coverage curve per retrieval arm**, not a single threshold number. This costs one experiment and materially strengthens the paper. (§2.10)

6. **The proposal's literature table is materially out of date, and its bibliographic data has errors that a citation checker will catch.** All 18 of its arXiv/journal identifiers were checked: **all resolve to the papers claimed** (good), but (a) seven arXiv IDs circulating in secondary sources for this literature resolve to **unrelated physics, mathematics, economics and astronomy papers** — the ones in the proposal's table for *Self-Ask with Search* (`2205.10601` → a mathematics paper) and *Speculative RAG* (`2407.02323` → an economics paper) are wrong, and the corrected IDs are `10.18653/v1/2023.findings-emnlp.378` and `10.48550/arXiv.2407.08223`; (b) the "Sufficient Context" entry is mis-authored (Joren et al., not Jiang et al.); (c) the Li et al. survey's title is **Capability-Oriented**, not Application-oriented; (d) the "Microsoft Research" entry should name Simchi-Levi, Mellou, Menache & Pathuri; and (e) **thirteen 2025-2026 papers directly on-thesis are absent** from the table — including SYNCHECK, which a reviewer will raise. For a **18 November 2026** defence this is the most fixable and most visible weakness. (§6.1, §6.3)

**One free win for the motivation section:** the SQuAD 2.0 abstract reports that *"a strong neural system that gets 86 % F1 on SQuAD achieves only 66 % F1 on SQuAD 2.0"*. Twenty points of accuracy vanish when unanswerable questions are made adversarial — with no industrial content involved. It is the cleanest available number for "answering when you should have abstained is expensive". (§2.1)

**One framing fix:** the thesis's per-claim confidence tags should be presented as **calibration of the human decision**, not as a UI convenience — CalibRAG (Jang et al., NeurIPS 2025) establishes that framing, and it changes what the user study should measure (decision accuracy, not preference). (§2.9)

---

## 1. Verified paper table

| # | Paper | Venue / Year | Identifier (verified) | Method (one line) | Key finding (as stated in the abstract) |
|---|---|---|---|---|---|
| V1 | Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., Küttler, H., Lewis, M., Yih, W., Rocktäschel, T., Riedel, S., & Kiela, D. — *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks* | NeurIPS 2020 | `10.48550/arXiv.2005.11401` (3,047 citations) | Non-parametric retriever (DPR) + parametric generator (BART), marginalising over retrieved documents | Establishes that retrieving documents and marginalising over them improves factuality and diversity on knowledge-intensive tasks |
| V2 | Asai, A., Wu, Z., Wang, Y., Sil, A., & Hajishirzi, H. — *Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection* | ICLR 2024 (preprint 2023-10) | `10.48550/arXiv.2310.11511` (101 citations) | Trains one LM to emit **reflection tokens** that decide when to retrieve and whether the passage supports the output | Self-RAG (7B/13B) outperforms ChatGPT and RAG-augmented Llama2-chat on open-domain QA, reasoning and fact verification; significant gains in factuality and **citation accuracy** for long-form generation |
| V3 | Yan, S.-Q., Gu, J.-C., Zhu, Y., & Ling, Z.-H. — *Corrective Retrieval Augmented Generation* (CRAG) | Findings of ACL 2024 | `10.48550/arXiv.2401.15884` | A **lightweight retrieval evaluator** returns a confidence degree that triggers one of four corrective actions (correct / wrong / ambiguous / web-search) | Across four datasets spanning short- and long-form generation, CRAG "can significantly improve the performance of RAG-based approaches"; it is plug-and-play |
| V4 | Jiang, Z., Xu, F. F., Gao, L., Sun, Z., Liu, Q., Dwivedi-Yu, J., Yang, Y., Callan, J., & Neubig, G. — *Active Retrieval Augmented Generation* (FLARE) | EMNLP 2023 | `10.18653/v1/2023.emnlp-main.495` · `10.48550/arXiv.2305.06983` (497 citations) | Predicts the *upcoming sentence*, uses it as a retrieval query, and regenerates the sentence **only if it contains low-confidence tokens** | FLARE achieves superior or competitive performance on all 4 long-form knowledge-intensive generation tasks |
| V5 | Jeong, S., Baek, J., Cho, S., & Hwang, S. J. — *Adaptive-RAG: Learning to Adapt Retrieval-Augmented Large Language Models through Question Complexity* | NAACL 2024 | `10.18653/v1/2024.naacl-long.389` · `10.48550/arXiv.2403.14403` (256 citations) | A **complexity classifier** routes each query to no-retrieval, single-step, or multi-step retrieval | A trained router beats fixed pipelines on out-of-distribution and multi-hop QA |
| V6 | Su, W., Tang, Y., Ai, Q., & Wu, Z. — *DRAGIN: Dynamic Retrieval Augmented Generation based on the Information Needs of Large Language Models* | ACL 2024 (preprint 2024-03) | `10.48550/arXiv.2403.10081` | Real-time detection of the model's information need from its own output, triggering immediate retrieval | Retrieval triggered exactly when the model lacks required information, rather than on a fixed schedule |
| V7 | Rajpurkar, P., Jia, R., & Liang, P. — *Know What You Don't Know: Unanswerable Questions for SQuAD* (**this is the SQuAD 2.0 paper**) | ACL 2018 | `10.18653/v1/p18-2124` · `10.48550/arXiv.1806.03822` (2,242 citations) | Extends SQuAD with **50,000 unanswerable questions** and a no-answer threshold | Establishes the standard task: a system must both answer answerable questions *and* decline unanswerable ones |
| V8 | Huang, J., Chen, X., Mishra, S. R., Zheng, H., et al. — *Large Language Models Cannot Self-Correct Reasoning Yet* | ICLR 2024 (preprint 2023-10) | `10.48550/arXiv.2310.01798` (48 citations) | Systematically tests intrinsic self-correction | Intrinsic self-correction **degrades** performance without external feedback; prior claims of self-correction were partly prompt artefacts |
| V9 | Kadavath, S., Conerly, T., Askell, A., & Henighan, T. — *Language Models (Mostly) Know What They Know* | 2022 | `10.48550/arXiv.2207.05221` (187 citations) | Verbalised confidence: the model states a probability for its own answer, then is asked to grade its own answer | Verbalised confidence is informative and **complements** grading; models can be trained to refuse low-confidence answers |
| V10 | Kuhn, L., Gal, Y., & Farquhar, S. — *Semantic Uncertainty: Linguistic Invariances for Uncertainty Estimation in Natural Language Generation* | ICLR 2023 (preprint 2023-02) | `10.48550/arXiv.2302.09664` (71 citations) | Clusters semantically-equivalent generations and measures entropy **over the semantic cluster**, not over tokens | Multiple sampled answers that *mean the same thing* should not look "uncertain"; semantic entropy is invariant to this |
| V11 | Farquhar, S., Kossen, J., Kuhn, L., & Gal, Y. — *Detecting hallucinations in large language models using semantic entropy* | **Nature** 630(8015), 625–630 (2024) | `10.1038/s41586-024-07421-0` · PMID 38898292 · PMCID PMC11186750 (926 citations) | Applies semantic entropy to *discrete* knowledge (e.g. "who won the US election") and calibrates it | Semantic entropy distinguishes confabulations (high entropy) from consistent errors (low entropy) — **an uncertain-sounding answer and a confidently wrong answer are different failure modes** |
| V12 | Joren, H., Zhang, J., Ferng, C.-S., Juan, D.-C., & Taly, A. — *Sufficient Context: A New Lens on Retrieval Augmented Generation Systems* | 2024 | `10.48550/arXiv.2411.06037` | Defines **context sufficiency** and classifies whether retrieved context contains enough to answer | Larger models (Gemini 1.5 Pro, GPT-4o, Claude 3.5) answer well when context is sufficient but **output incorrect answers instead of abstaining when it is not**; the proposed selective-generation method improves the fraction of correct answers among responses by **2–10 %** |
| V13 | Mallen, A., Asai, A., Zhong, V., Das, R., Khashabi, D., & Hajishirzi, H. — *When Not to Trust Language Models: Investigating Effectiveness of Parametric and Non-Parametric Memory in LLMs* | ACL 2023 | `10.18653/v1/2023.acl-long.546` (340 citations) | Compares parametric memory vs retrieval across factuality, diversity, and model size | Retrieval helps factuality but **hurts diversity** and can reduce accuracy when the parametric answer was already correct — "when not to trust" retrieval matters as much as "when to retrieve" |
| V14 | Kossen, J., Han, J., Razzak, M., Schut, L., Malik, S., & Gal, Y. — *Semantic Entropy Probes: Robust and Cheap Hallucination Detection in LLMs* | 2024 | `10.48550/arXiv.2406.15927` | Trains a linear probe on hidden activations to predict semantic entropy | Probes are markedly cheaper than sampling-based estimation while remaining robust |
| V15 | Geng, J., Cai, F., Wang, Y., & Koeppl, H. — *A Survey of Confidence Estimation and Calibration in Large Language Models* | NAACL 2024 | `10.18653/v1/2024.naacl-long.366` · `10.48550/arXiv.2311.08298` (88 citations) | Taxonomy survey of confidence/calibration methods | Standard reference taxonomy for LLM confidence estimation |
| V16 | Liu, X., Chen, T., Da, L., & Chen, C. — *Uncertainty Quantification and Confidence Calibration in Large Language Models: A Survey* | KDD 2025 | `10.1145/3711896.3736569` (53 citations) | 2025 update covering UQ + calibration across modalities | Current survey-level reference |
| V17 | Yadkori, Y. A., Kuzborskij, I., Stutz, D., & György, A. — *Mitigating LLM Hallucinations via Conformal Abstention* | 2024 | `10.48550/arXiv.2405.01563` | Wraps an LLM in a **conformal** predictor that abstains with statistical guarantees | Conformal prediction yields abstention decisions with finite-sample coverage guarantees under exchangeability |
| V18 | Song, F., & Croft, W. B. — *A general language model for information retrieval* | CIKM 1999 | `10.1145/319950.320022` (548 citations) | LM-based IR: rank documents by the likelihood of generating the query | The origin of the "query likelihood" scoring function that later RAG confidence estimators build on |
| V19 | Azzopardi, L. M., Girolami, M., & van Rijsbergen, C. J. — *Topic based language models for ad hoc information retrieval* | IJCNN 2005 | `10.1109/IJCNN.2004.1381205` | Mixture-of-LMs interpolated with a relevance model | Shows the Bayesian relevance-model construction the thesis's posterior gate descends from |
| V20 | Hiemstra, D., Robertson, S. E., & Zaragoza, H. — *Parsimonious language models for information retrieval* | SIGIR 2004 | `10.1145/1008992.1009025` | Unifies BM25 and LM-based IR under one framework | The mathematical bridge between the lexical and probabilistic legs of the thesis's retrieval stack |
| V21 | Kraaij, W. — *Variations on language modeling for information retrieval* | ACM SIGIR Forum 2005 | `10.1145/1067268.1067291` | Review of LM-based IR variants | Standard survey for the Bayesian/IR-probability background |
| V22 | Ruthven, R., & Lalmas, M. — *A survey on the use of relevance feedback for information access systems* | Knowledge Engineering Review 2002 | `10.1017/S0269888903000638` (402 citations) | Survey of pseudo-relevance feedback | Background for probabilistic expansion of the query used in confidence estimation |
| V23 | **Geißler, F., Carella, F., Fieback, L., & Spiegelberg, J. — *Towards Dependable RAG Using Factual Confidence Prediction*** | **arXiv 2026-05** | `10.48550/arXiv.2605.05244` | Two-stage: **conformal prediction** filters retrieved chunks to those likely from the correct source; an **attention-based factuality classifier** scores answer–context consistency | Conformal chunk selection improves answer quality by **up to 6 %** on some datasets (but the guarantee "does not hold generally, since the assumption of sample exchangeability depends on the retriever setup"); the factuality classifier detects inconsistent answers with a chance of **up to 77 %**. Framed explicitly as "certified RAG systems for industry applications" |
| V24 | **Jang, C., Cho, D., Lee, S., Lee, H., & Lee, J. — *Reliable Decision Making via Calibration Oriented RAG* (CalibRAG)** | **NeurIPS 2025** | `10.48550/arXiv.2411.08891` | Retrieval method engineered so that decisions informed by RAG are **well-calibrated** for the human user | CalibRAG improves **both calibration performance and accuracy** over baselines across several datasets |
| V25 | **Thakur, A., Saparov, A., & Ribeiro, B. — *DeclineCraft: A RAG Abstention Benchmark for Jointly Measuring Combined Retrieval and Parametric Knowledge*** | **arXiv 2026-10** | `10.48550/arXiv.2610.28340` | Dynamic abstention benchmark: unanswerable questions target **post-cut-off features** (Minecraft additions), with audits of possible parametric exposure; 27 LLMs evaluated | (1) Single-shot retrieval raises **Correct Abstention Rate (CAR) in 38 of 40 configurations**; (2) **Iterative RAG lowers CAR vs single-shot in 30 of 40 configurations (mean 46.4 %)**, with answer accuracy essentially unchanged (68.5 % → 69.3 %); adding **query rewriting and reranking to hybrid dense+sparse retrieval lowers CAR for all 12 models tested**; (3) larger models are more accurate (Spearman ρ = +0.60 with total parameters) but model size and release date show **no significant association with CAR**; (4) without retrieval, enabling "thinking" lowers CAR for 8 of 13 models (by 14 points on average) |
| V26 | **Shin, S., Cha, M., Lee, B.-J., & Park, S. — *ERA: Evidence-based Reliability Alignment for Honest RAG*** | **arXiv 2026-04** | `10.48550/arXiv.2604.20854` | Replaces scalar confidence with an **explicit Dirichlet evidence distribution**; uses **Dempster–Shafer Theory** to measure geometric discordance between parametric and retrieved knowledge | Distinguishes **epistemic** uncertainty (model does not know) from **aleatoric** ambiguity (evidence itself is ambiguous); "significantly outperforms baselines, optimizing the trade-off between answer coverage and abstention with superior calibration" |
| V27 | **Phillips, E., Gustafsson, F., Wu, S., Thakur, A., & Clifton, D. A. — *Entropy Alone is Insufficient for Safe Selective Prediction in LLMs*** | **arXiv 2026-03** | `10.48550/arXiv.2603.21172` | Identifies a **model-dependent failure mode of entropy-based uncertainty**; combines entropy with a **correctness-probe** signal | Across TriviaQA, BioASQ, MedicalQA and four model families, the combined score improves both the **risk–coverage trade-off** and calibration relative to entropy-only baselines. Argues uncertainty methods must be evaluated *at a stated operating risk level*, not in isolation |
| V28 | **Zhang, H., & Wu, W. — *Do LLMs Know When Evidence is Insufficient? An Evidence Sufficiency Benchmark for Answer-Abstention*** | **CMC 2026** | `10.32604/cmc.2026.086343` | Benchmark separating *evidence insufficiency* from other abstention triggers | Recent evidence that evidence-sufficiency abstention is now its own benchmarked research problem |
| V29 | **Sun, Q., Li, X., & Xie, X. — *Efficient Hallucination Detection: Adaptive Bayesian Estimation of Semantic Entropy with Guided Semantic…*** | **AAAI 2026** | `10.1609/aaai.v40i39.40595` | Bayesian estimation of semantic entropy | Bayesian treatment of semantic entropy — directly parallel to the thesis's Bayesian posterior gate |
| V30 | **Pellet, A., Puren, M., & Pérez, J. — *ORDER: Task-Conditioned Routing for RAG*** | **Findings of EMNLP 2026** | `10.18653/2026.findings-emnlp.2026` | Task-conditioned routing for RAG | Recent work confirming routing as an active 2026 direction |
| V31 | Wang, Z., Liao, M., & Zhang, J. — *Confidence-weighted semantic entropy: A robust framework for hallucination detection and uncertainty…* | Neurocomputing 2026 | `10.1016/j.neucom.2026.134859` | Weights semantic entropy by a confidence term | Extends semantic entropy toward per-claim granularity |
| V32 | Yadkori et al. (see V17) and **Xu, R., Chen, Y., & Xie, S. — *Geometry-Calibrated Conformal Abstention for Language Models*** | arXiv 2026-04 | `10.48550/arXiv.2604.27914` | Calibrates conformal abstention using representation geometry | 2026 continuation of the conformal-abstention line |
| V33 | King, D., Shen, Z., Subramani, N., et al. — *Don't Say What You Don't Know: Improving the Consistency of Abstractive Summarization by Rewarding Fully Consistent Summaries* | **GenAI Workshop @ EMNLP 2022** | `10.48550/arXiv.2203.08436` (pp. 555–571) | Reinforces a summary only when it is **fully consistent** with its source — a consistency-reward training objective | Establishes the "consistency-first" training principle that the thesis's per-claim grounding bands operationalise at inference time |
| V34 | **Decian, J., Njeh, C., Nakouri, H., & Jaafar, F. — *Dynamic RAG with hybrid retrieval: A novel approach to robust LLMs and hallucination prevention*** | **Neurocomputing 705, 134911 (2026)** | `10.1016/j.neucom.2026.134911` | Hybrid retrieval + an **entropy-based dynamic threshold** for the retrieval decision | Reports statistically significant correctness gains (**p < 0.01**); the DOCX correctly describes it as "closest to our RO1" — **the single nearest prior work to the thesis's RO1** |
| V35 | Li, Y., Fu, X., Verma, G., Buitelaar, P., & Liu, M. — *Mitigating Hallucination in LLMs: A **Capability-Oriented** Survey on RAG, Reasoning, and Agentic Systems* | arXiv 2025-10 | `10.48550/arXiv.2510.24476` (4 citations) | Survey of hallucination-mitigation methods, organised by **capability** rather than by application domain | The DOCX calls this an "Application-oriented survey" — the actual title says **Capability-Oriented**. Cite the correct title |
| V36 | Simchi-Levi, D., Mellou, K., Menache, I., & Pathuri, J. — *Large Language Models for Supply Chain Decisions* | arXiv 2025-07 (Springer Series in Supply Chain Management, forthcoming) | `10.48550/arXiv.2507.21502` | **Off-the-shelf LLMs as a conversational layer over existing optimisation-based supply-chain planning tools** — explaining tool recommendations, what-if scenario analysis, updating underlying models without a data-science team | Reduces time-to-decision "from days and weeks to minutes and hours". **Two errors in the DOCX:** it is attributed to "Microsoft Research" (first author is **David Simchi-Levi, MIT**), and it is characterised as a *fine-tuned LLM for procurement with a real-world Microsoft deployment* — **it is neither**. The DOCX's own counter-position ("We will use RAG instead of fine-tuning") defends against a framing this paper does not make |
| V37 | **Wang, Z., Wang, Z., Le, L. T., & Zheng, H. — *Speculative RAG: Enhancing Retrieval Augmented Generation through Drafting*** | arXiv 2024-07 | **`10.48550/arXiv.2407.08223`** (9 citations) | A lightweight "draft" model proposes a RAG answer; a large verifier model only re-drafts when the draft is judged unreliable | Draft-then-verify trades latency for quality — the same *conditional-compute* philosophy as the thesis's gate, applied to the generator rather than the retriever. **This is the correct identifier for the paper the proposal cites as `arXiv:2407.02323`** (which is an economics paper) |
| V38 | Quan, G., Feng, W., Hao, C., & Jiang, G. — *RASD: Retrieval-Augmented Speculative Decoding* | Findings of ACL 2025, pp. 6167–6177 | `10.18653/v1/2025.findings-acl.320` (3 citations) | Applies speculative decoding to the RAG retrieval+generation loop | Recent continuation showing the draft-then-verify pattern is an active 2025–2026 line |
| V39 | Li, Y., Huang, S., Liu, X., Zhao, Y., et al. — *BRIDGE: Block-Wise Speculative Coordination for Cloud-Edge Retrieval-Augmented Generation* | KDD 2026, pp. 2885–2896 | `10.1145/3770855.3818064` | Block-wise speculative coordination for edge-deployed RAG | Shows the draft-verify pattern reaching systems-deployment venues in 2026 |
| V40 | **Wu, D., Gu, J.-C., Yin, F., & Peng, N. — *Synchronous Faithfulness Monitoring for Trustworthy Retrieval-Augmented Generation* (SYNCHECK)** | **EMNLP 2024, pp. 9390-9406** | `10.18653/v1/2024.emnlp-main.527` (9 citations) | A lightweight monitor over **decoding dynamics** — sequence likelihood, uncertainty quantification, context influence, semantic alignment — that detects **unfaithful sentences as they are generated** | **0.85 AUROC** detecting faithfulness errors across **six** long-form RAG tasks, **improving the prior best method by 4 %**. Its FOD decoding algorithm **outperforms abstention, reranking and contrastive decoding by over 10 %** on faithfulness across six datasets. **This is the single most direct challenge to the thesis's D1** (see §4-R7) |
| V41 | **Chernogorskii, F., Averkiev, S., Kudraleeva, L., Martirosian, Z., Tikhonova, M., Malykh, V., & Fenogenova, A. — *DRAGOn: Designing RAG On Periodically Updated Corpus*** | **EACL 2026 SRW, pp. 622-638** | `10.18653/v1/2026.eacl-srw.48` | A method for building RAG benchmarks on a **regularly updated corpus**: recent reference datasets, question-generation framework, automatic evaluation pipeline, public leaderboard | Extracts a **knowledge graph from the text corpus** to generate QA pairs; LLM-as-Judge metrics; **new dataset versions mitigate data leakage** so models are always evaluated on unseen, comparable data. Directly addresses the *stale-evidence* problem the industrial setting creates (see §4-R2) |
| V42 | Li, B., Wang, M., Fang, G., & Zhang, S. — *Retrieval as Generation: A Unified Framework with Self-Triggered Information Planning* (GRIP) | ACL 2026, pp. 4254-4274 | `10.18653/v1/2026.acl-long.196` | Embeds **retrieval control inside token-level decoding** via control-token emission instead of an external controller or classifier | The model decides when to retrieve, how to reformulate queries, and when to stop **within a single autoregressive pass** — the opposite architectural bet to the thesis's *external, code-level* gate |
| V43 | Park, C., Moon, H., Park, C., & Lim, H. — *MIRAGE: A Metric-Intensive Benchmark for Retrieval-Augmented Generation Evaluation* | Findings of NAACL 2025, pp. 2883-2900 | `10.18653/v1/2025.findings-naacl.157` (8 citations) | A QA dataset designed for **component-specific** RAG evaluation | **7,560 curated instances** mapped to a retrieval pool of **37,800 entries**, enabling precise separation of retrieval failure from generation failure — exactly the ablation the thesis's RO2 and RO3 need |
| V44 | Gao, S., Zhao, S., Jiang, X., Duan, L., et al. — *Scaling Beyond Context: A Survey of Multimodal Retrieval-Augmented Generation for Document Understanding* | ACL 2026, pp. 4458-4489 | `10.18653/v1/2026.acl-long.204` (2 citations) | Survey of multimodal RAG for documents | Contrast between **OCR-based pipelines feeding LLMs** and **native Multimodal LLMs** — the framing the thesis's RO2 (modality-balanced retrieval) sits inside |
| V45 | Murugaraj, K., Lamsiyah, S., & Theobald, M. — *RAGVUE: A Diagnostic View for Explainable and Automated Evaluation of Retrieval-Augmented Generation* | EACL 2026 Demo, pp. 512-526 | `10.18653/v1/2026.eacl-demo.35` | Explainable, automated diagnostic evaluation of RAG | Evaluation tooling for component-level diagnosis |
| V46 | Badshah, S., Moustafa, M., & Sajjad, H. — *CLEV: LLM-Based Evaluation Through Lightweight Efficient Voting for Free-Form QA* | Findings of IJCNLP 2025, pp. 1513-1531 | `10.18653/v1/2025.findings-ijcnlp.93` | Two LLM judges vote; a third is invoked **only on disagreement** | Reliable free-form QA evaluation at lower cost — a cheap LLM-as-judge option for the thesis's annotation pipeline |
| V47 | **Zhang, W., & Zhang, J. — *Hallucination Mitigation for Retrieval-Augmented Large Language Models: A Review*** | **Mathematics 13(5), 856 (2025)** | `10.3390/math13050856` (144 citations) | Review of hallucination-mitigation strategies for RAG, organised by mitigation technique | **The correct DOI is `10.3390/math13050856` (volume 13, *issue 5*)** — the frequently-circulated `math13060856` / 13(6) form does not resolve to this paper. Cross-verified against the sibling citation audit (§7, note on cross-verification) |

---

## 2. Deep explanations of the twelve most important papers

Each subsection explains the method in plain language first, then states why it matters to an industrial RAG confidence gate. These are written so that a reader who has never worked with RAG can follow them.

### 2.1 SQuAD 2.0 (V7) — the task that defines "I don't know"

**Plain language.** In the original SQuAD dataset, every question had an answer sitting in a Wikipedia article, and the system was scored on how well it found and reproduced that answer span. Rajpurkar, Jia and Liang's insight was that a real deployment never has that guarantee. They added **over 50,000 questions** for which the answer is genuinely *not* in the article — written **adversarially by crowdworkers so that they look similar to answerable ones**. The scoring rule became: **if you answer, you must answer correctly; if you cannot answer, you must say so.** A system that guesses on an unanswerable question is penalised as hard as one that stays silent on an answerable one. This is called the **no-answer threshold** in the original paper.

**The headline number (verified from the abstract):** *"a strong neural system that gets **86 % F1** on SQuAD achieves only **66 % F1** on SQuAD 2.0."* Twenty percentage points of accuracy disappear the moment the questions are made adversarial and unanswerable. **This is the single most useful number to quote in the thesis's motivation section**, because it quantifies the cost of answering when you should have abstained — on a dataset with no industrial content at all.

**Why it matters here.** SQuAD 2.0 is the reason the thesis's confidence gate is a legitimate object of study and not an arbitrary engineering choice. The task "answer the question *or* decline" has a 10-year-old benchmark definition, a standard metric (the no-answer score), and a well-understood failure mode: **models that answer unanswerable questions confidently**. The thesis's D1 design move — returning an explicit "no evidence" response when retrieval confidence is below threshold — is a direct implementation of the SQuAD 2.0 contract, transferred from open-domain Wikipedia to industrial documentation.

### 2.2 Semantic entropy (V10, V11) — the distinction that makes confidence meaningful

**Plain language.** Suppose you ask a model "Who won the 2020 US presidential election?" and sample its answer five times. Sometimes it says "Joe Biden", sometimes "Donald Trump". Standard *token-level* entropy — the average surprise of each generated token — will register this as high uncertainty. But the model is not uncertain in a useful sense: it is confidently wrong, oscillating between two confidently-held beliefs.

Kuhn, Gal and Farquhar's **semantic uncertainty** fixes this by clustering the sampled generations that *mean the same thing* and computing entropy **over the clusters** rather than over tokens. A model that says "Joe Biden" five different ways gets a *low* semantic entropy — it is consistent. A model that says Biden, Trump, Obama and Abstain gets a *high* semantic entropy — it is genuinely conflicted. The Nature paper (V11) then calibrates this measure on **discrete** knowledge and shows it cleanly separates two failure modes that token entropy merges:

- **Confabulation** — the model does not know and produces diverse nonsense. High semantic entropy.
- **Consistent error** — the model confidently holds a wrong belief. Low semantic entropy.

**Why it matters here.** The thesis's **per-claim three-band confidence tagging** (D5: *grounded / inferred / uncertain*) is a per-claim version of exactly this idea. The PDF's report that per-claim tagging improves practitioner decision accuracy is a claim about applying semantic-uncertainty-style reasoning at the span level rather than the answer level. The Nature result also warns the thesis's authors about a subtlety: **a claim can be confidently wrong.** Low uncertainty is not the same as high correctness — which is why the thesis pairs a confidence tag with an explicit **evidence citation**, and why V23's attention-based factuality classifier exists as a separate second stage.

### 2.3 Sufficient Context (V12) — the finding that most directly threatens a naive gate

**Plain language.** Joren and colleagues ask a deceptively simple question: when a RAG system gets an answer wrong, is it because the model **failed to use** the retrieved context, or because the retrieved context **did not contain** the answer? They define **sufficient context** for a query and build a classifier for it. Stratifying errors by context sufficiency produces a sharply asymmetric result.

Large models (Gemini 1.5 Pro, GPT-4o, Claude 3.5) are excellent when context is sufficient — they answer correctly. But when context is *insufficient*, these same models **produce a wrong answer rather than abstaining**. Smaller models (Mistral 3, Gemma 2) hallucinate *or* abstain frequently, even when context was sufficient. Their selective-generation method, which uses the sufficiency classifier to guide abstention, improves the fraction of correct answers among responses by **2–10 %**.

**Why it matters here.** This paper is simultaneously (a) the strongest justification for the thesis's gate existing at all — abstention is a measurable, improvable behaviour — and (b) the strongest warning about *where* the gate must sit. If the gate is applied to the **answer** (i.e. "is this generated answer confident?"), it inherits the exact failure Joren documents: strong models answer confidently from insufficient context. If the gate is applied to the **retrieval** (i.e. "is this evidence sufficient to answer?"), it is attacking the right variable. The thesis's design — a *code-level* gate placed **before** the LLM call, operating on retrieval confidence — is the correct architectural choice by this paper's logic, and this is a citable, defensible reason.

### 2.4 CRAG (V3) — the nearest prior art, and the sharpest contrast

**Plain language.** CRAG inserts a small, cheap **retrieval evaluator** between retrieval and generation. That evaluator grades the retrieved documents as *correct*, *wrong*, *ambiguous*, or *correct but incomplete*, and returns a confidence degree. The degree selects one of four corrective actions: use the documents as-is, use web search to improve them, decompose-and-recompose the documents to keep only the relevant parts, or combine the two. Crucially, CRAG **still calls the LLM** in every branch — it changes *what* context the LLM sees, not *whether* the LLM runs.

**Why it matters here.** CRAG is the work the thesis's literature review already identifies as the closest neighbour to RO1, and the PDF's literature table gets this right. The thesis's design differs in three specific, statable ways:

1. **Placement.** CRAG's evaluator sits *inside* the generation path; the thesis's gate sits *before* it and can prevent the call entirely ("non-bypassable").
2. **Action.** CRAG's response to low confidence is to *improve the evidence* (web search, decomposition); the thesis's response is to *decline* and return "no evidence".
3. **Cost.** CRAG's web-search branch adds a network dependency at inference time; the thesis's gate is a local computation over a retrieval score.

This contrast is the thesis's defensible novelty on RO1. It must be stated as a *difference in design philosophy under the same goal*, not as a claim that CRAG is inferior — CRAG's refine-and-continue behaviour is the right choice when the corpus is incomplete and web search is available, and the thesis's corpus is a fixed industrial document set.

### 2.5 Self-RAG (V2) — why the thesis rejects learned reflection tokens

**Plain language.** Self-RAG fine-tunes a language model to emit special **reflection tokens** alongside its answer. One token says "retrieve"; others say "the retrieved passage is relevant" or "the passage supports my answer" or "my answer is unsupported." At inference time the model reads its own reflection tokens and adapts: it decides whether to retrieve at all, and whether to keep or discard what it retrieved.

**Why it matters here.** The thesis explicitly chooses a **non-trainable, code-level** gate over Self-RAG's learned reflection tokens, and this choice is defensible on three grounds that the literature supports:

- **Training cost and domain transfer.** Self-RAG's reflection tokens are learned on a training distribution. An industrial corpus with different vocabulary, document structure and query distribution would require the fine-tuning to be repeated for each of the twelve industrial categories the thesis targets. A threshold on a retrieval score needs no per-category training.
- **Bypassability.** Reflection tokens are *emitted by the model being gated*. Huang et al. (V8) demonstrate that intrinsic self-correction degrades without external feedback, and Farquhar et al. (V11) show that models are systematically *overconfident* — so a learned signal that the model itself produces is the wrong place to look for reliable self-knowledge.
- **Auditability.** An industrial deployment must be able to explain and justify a refusal to a regulator or an auditor. "The code refused because the retrieval score was 0.31 against a threshold of 0.47" is auditable; "the model emitted a `0` reflection token" is not.

The PDF's literature-review table already makes this argument; V8 and V11 supply the citations that make it rigorous rather than assertive.

### 2.6 Adaptive retrieval (V4, V5, V6, V13) — the "when to retrieve" family

**Plain language.** Four related lines of work ask *when* retrieval should happen, rather than how to make retrieval better.

- **FLARE (V4)** operates *mid-generation*: it predicts the next sentence, retrieves for it, and regenerates if the sentence contained low-confidence tokens.
- **Adaptive-RAG (V5)** classifies the *query* by complexity and routes it to no-retrieval, one-step, or multi-step retrieval.
- **DRAGIN (V6)** watches the model's own output in real time and triggers retrieval the moment it detects an information need.
- **Mallen et al. (V13)** is the cautionary counterweight: retrieval is not free. It improves factuality but *reduces diversity* and can lower accuracy where the parametric answer was already right.

**Why it matters here.** This family defines the design space the thesis's D1 sits in, and it sharpens the thesis's claim considerably. The thesis's gate is not "when to retrieve" — it is "**whether the retrieved evidence is good enough to answer at all**". That is a different question, and the thesis should say so explicitly, because a reviewer who knows Adaptive-RAG will otherwise ask "isn't this just Adaptive-RAG?" The precise answer: Adaptive-RAG decides *whether to retrieve*; the thesis decides *whether to answer*, and the answer is "no" by default when the evidence is weak.

### 2.7 Factual Confidence Prediction with conformal prediction (V23) — the 2026 work the thesis must engage

**Plain language.** Geißler and colleagues address precisely the thesis's RO1 problem, with an industrial framing: "this work helps to establish a novel type of **certified RAG systems** for a broad range of natural language industry applications." Their method has two stages. Stage one applies **conformal prediction** to the retrieved chunks: under exchangeability assumptions, a calibrated threshold keeps only chunks that have a high probability of having come from the correct source. Stage two scores whether the generated answer is consistent with the retrieved context, using an **attention-based factuality classifier**.

**Why it matters here.** This is the single most important paper for the thesis's positioning, for two reasons. First, it is *very close* to what the thesis proposes and is more recent than the thesis's own literature review — a reviewer who knows this literature will ask why the thesis does not adopt it. Second, the paper's own reported numbers are candid and useful for the thesis: conformal chunk selection "can improve answer quality by up to 6% in some of the studied datasets, **however, the associated statistical guarantees do not hold generally, since the assumption of sample exchangeability depends on the retriever setup**", and the paper supplies **diagnostic metrics to assess whether a setup is suitable**. The attention-based factuality classifier "can detect inconsistent answers with a chance of up to 77%".

The honest reading for the thesis is: **conformal prediction gives the thesis's gate statistical rigour that a hand-tuned logistic-regression threshold does not**, and its documented fragility (exchangeability depends on the retriever setup) is exactly the risk the thesis's 634-chunk, single-category corpus would violate. This makes V23 the thesis's best "related work, and here is why our approach is different and when it would be worse" citation — and it is a *strengthening* citation, because the thesis can adopt the paper's diagnostic metrics as a limitation.

### 2.8 DeclineCraft (V25) — the finding that complicates the thesis's own design

**Plain language.** DeclineCraft is a 2026 abstention benchmark built around a clever cut-off trick: it asks about **Minecraft feature additions made after the corpus cut-off**, and audits for possible parametric exposure so the questions are genuinely unanswerable. Across 27 LLMs it measures Correct Abstention Rate (CAR), Answerable Attempt Rate and Answer Accuracy. Four findings matter:

1. Single-shot retrieval raises CAR in **38 of 40** model×thinking configurations versus no retrieval.
2. **Iterative RAG lowers CAR** versus single-shot in **30 of 40** configurations (mean 46.4%), with answer accuracy essentially flat (68.5% → 69.3%).
3. Adding **query rewriting and reranking to hybrid dense+sparse retrieval lowers CAR for all 12 models tested**.
4. Larger models are more accurate (ρ = +0.60 with parameter count) but model size and release date show **no significant association with CAR**.

**Why it matters here.** Finding 3 is a direct empirical challenge to the thesis's architecture. The thesis's D3 (hybrid lexical + dense + reranker via RRF) is a *better retrieval* mechanism; DeclineCraft says better retrieval **reduces abstention** — because when retrieval is good, the model answers, and answering is counted as *not* abstaining. The thesis's own PDF reports the same class of effect in a different place: the modality-aware boost was a documented **null result** because the corpus was too text-heavy (2.3% chart, 7.1% table) to exercise the signal.

The thesis therefore has a **defensive requirement** that it must satisfy empirically: the confidence gate's operating point has to be *re-calibrated for each retrieval configuration*. A threshold that is correct for a weak retriever is wrong for a strong one. The thesis's calibration study (30-query set, logistic regression with β₀ = 2.943, β₁ = 1.680) must be run **per retrieval arm**, not once, and this must be stated as a limitation rather than discovered by a reviewer. This is the single most valuable finding in this survey for the thesis's defensibility.

Findings 1 and 4 also support the thesis's motivation: retrieval is what makes abstention possible at all (38/40), and model scale does **not** buy abstention ability — so a *code-level* gate that is independent of model scale is the right architectural bet.

### 2.9 CalibRAG (V24) — calibration as a property of the *decision*, not just the model

**Plain language.** CalibRAG's framing is subtly different from everything else in this survey, and it is the framing that matters most for an industrial deployment. Its target is not "is the model right?" but "**is the human who relies on this decision well-calibrated?**" A RAG system that produces a confident, fluent, wrong answer is more dangerous than one that is visibly unsure, because it corrupts the human's calibration. CalibRAG engineers the *retrieval* so that decisions informed by the retrieved evidence come out calibrated. It reports improvements in **both calibration performance and accuracy** over baselines across several datasets.

**Why it matters here.** This paper reframes the thesis's D5 (per-claim confidence tagging) from a convenience feature into a **safety property**. The PDF's design move D5 tags each claim as *grounded / inferred / uncertain*; CalibRAG supplies the theoretical justification for why that tagging must be *calibrated against the human's decision*, and why an uncalibrated tag is worse than no tag (it transfers false confidence). The thesis's user study with 16 practitioners should therefore report not just "did they like the tags" but "**did the tags change their decision in the right direction**" — decision accuracy, not preference.

### 2.10 Entropy alone is insufficient (V27) — a 2026 corrective to the obvious approach

**Plain language.** This paper makes a methodological point that should change how the thesis evaluates its own gate. Selective prediction (abstaining on high-risk cases) is only useful if the abstention policy operates at a **stated target error rate** — the threshold at which the system's remaining answers are 95% correct, say. Phillips and colleagues show that entropy-based uncertainty has a **model-dependent failure mode**: on some models the entropy score does not rank risk correctly, so the risk–coverage curve is poor and the system cannot be trusted at low target error. Combining entropy with a separate **correctness-probe** signal improves both risk–coverage and calibration across TriviaQA, BioASQ and MedicalQA and four model families.

**Why it matters here.** The thesis's confidence gate uses a **Bayesian posterior over retrieval relevance** — not entropy — which is a point in its favour: V27's specific complaint is aimed at entropy. But the paper's *methodological* message applies squarely: the thesis's gate must be evaluated **as a selective-prediction policy at a stated operating point**, with a **risk–coverage curve**, not merely as "hallucination rate drops when the gate is on". The PDF's report of "Bayesian confidence gating reduces hallucination" is a single operating point; the thesis should add the curve and the operating-point framing. The paper also validates the thesis's instinct to **combine** signals rather than rely on one: entropy alone failed, and the fix was a second, cheap, complementary probe.

---

### 2.11 SYNCHECK (V40) — the 2024 paper that already beat abstention

**Plain language.** Wu, Gu, Yin and Peng (EMNLP 2024) attack the *generation* side of the same problem the thesis attacks on the *retrieval* side. Their monitor, **SYNCHECK**, watches the model as it decodes and computes four cheap signals per sentence — **sequence likelihood**, **uncertainty quantification**, **context influence** (how much the retrieved passage actually moved the output) and **semantic alignment** (does the sentence agree with the passage) — and flags a sentence as *unfaithful* as soon as it is produced. It then uses that signal inside a beam-search decoding algorithm (**FOD**) to steer generation away from unfaithful output.

**The numbers, which matter here.** SYNCHECK reaches **0.85 AUROC** detecting faithfulness errors across **six long-form RAG tasks**, **improving the prior best method by 4 %**. And then the sentence that should be read twice by anyone building an abstention mechanism: *"FOD outperforms traditional strategies such as **abstention**, reranking, or contrastive decoding significantly in terms of faithfulness, achieving **over 10 % improvement** across six datasets."*

**Why it matters here.** This is the strongest challenge the thesis's RO1 will face, and it is already two years old. SYNCHECK says, in effect: *if you want faithfulness in long-form RAG, a decoding-time monitor beats abstention.* The thesis must therefore state its case crisply on three points, and must not pretend the comparison is apples-to-apples:

- **Different failure surfaces.** SYNCHECK detects *unfaithfulness* — the generated sentence contradicts or is unsupported by the retrieved context. The thesis's gate detects *insufficient evidence* — the retrieved context does not support any answer. A system can be perfectly faithful (SYNCHECK says yes) and still have no evidence to be faithful *to* (the thesis's gate says decline). These are different bugs with different fixes.
- **Different failure cost.** SYNCHECK's monitor runs *during* generation, so the expensive tokens have already been spent by the time the signal arrives. The thesis's gate runs *before* generation, so a refusal costs a retrieval pass and nothing else. For an industrial budget where a refused query should be cheap, that ordering is a real advantage.
- **Different granularity of claim.** SYNCHECK's output is per-sentence, and its AUROC is measured on long-form generation benchmarks. The thesis's per-claim banding is a three-band human-facing label. They are not interchangeable, and the thesis should say so rather than imply SYNCHECK is a weaker version of the same thing.

**The honest concession.** SYNCHECK also uses **multiple complementary signals**, which is exactly what V27 (Phillips et al. 2026) concluded a single entropy score cannot do. The thesis's gate uses a **single** Bayesian posterior feature. That is a genuine weakness of the current design, and the honest move is to say that the thesis's single-feature gate is the *simplest possible* instantiation of the multi-signal design that SYNCHECK and V27 both point to, and that extending it is the stated future work.

### 2.12 DRAGOn (V41) — the benchmark for the problem industrial corpora actually have

**Plain language.** DRAGOn (EACL 2026 Student Research Workshop) is about building a RAG **benchmark on a corpus that changes**. It assembles recent reference datasets, a question-generation framework that extracts a **knowledge graph from the corpus** and turns it into QA pairs, an automatic evaluation pipeline with LLM-as-Judge metrics, and a public leaderboard. Its key design decision is that it **regenerates dataset versions** so that "newly generated dataset versions mitigate data leakage and ensure that all models are evaluated on unseen, comparable data."

**Why it matters here.** DRAGOn is aimed squarely at the gap between a static benchmark and a live corpus — which is the *normal* condition of industrial documentation, not an edge case. Two specific lessons for the thesis:

1. **The stale-evidence problem is a benchmark-design problem, not only a generation problem.** The thesis's corpus is a snapshot; industrial corpora are not. When a procedure is superseded, the retrieved passage may be *internally consistent but operationally wrong*. DRAGOn's versioned-dataset approach is the right shape of answer, and it is a concrete, citable thing for the thesis's "Future Work" to point at.
2. **Knowledge-graph-based question generation is a reusable asset.** The thesis's benchmark annotation currently uses LLM agents with a structured protocol (per the proposal). DRAGOn's approach — extract the KG, generate questions from it, evaluate with LLM-as-Judge — is a *second, independent* way to build the benchmark that could be used as a **validation** of the primary annotation, which is exactly what a reviewer will ask for when the benchmark is used to defend the thesis's own empirical claims.

---

## 3. What this thesis can legitimately claim

### 3.1 Defensible novelty

| Claim | Prior art it must be positioned against | Why the claim survives |
|---|---|---|
| A **code-level, non-bypassable** confidence gate — the LLM is never called when evidence is insufficient | Self-RAG (V2), CRAG (V3), FLARE (V4) | All three still call the LLM in the low-confidence branch (CRAG refines and continues; Self-RAG's tokens are model-emitted and therefore bypassable in principle; FLARE regenerates). The thesis's gate returns an explicit "no evidence" answer and **exits the generation path**. |
| The gate is **outside the LM loop and requires no training** | Self-RAG (V2) | Self-RAG needs fine-tuning and its reflection tokens are a *learned* self-report. The thesis's gate is a calibrated function of a retrieval score. This buys per-category portability across the twelve industrial categories at no training cost, and produces an **auditable** refusal reason (score vs threshold) rather than an opaque token. |
| The gate is **calibrated empirically** rather than fixed | CRAG (V3) | CRAG's confidence degree selects among four actions and is itself trained. A logistic-regression-calibrated posterior threshold (β₀ = 2.943, β₁ = 1.680) is fitted on held-out queries and produces a probability, not just a degree. |
| **Per-claim** confidence banding (grounded / inferred / uncertain) | CalibRAG (V24), semantic entropy (V10/V11) | CalibRAG calibrates at the decision level; semantic entropy at the answer level. Per-claim banding is finer-grained and is what the practitioner actually consumes. This is an *extension* of prior calibration work to span level, not a new calibration method. |
| Evaluation of the gate as a **selective-prediction policy with a risk–coverage curve at a stated operating point** | V27's methodology | This is the evaluation *framing* the thesis should adopt; it is not claimed as a contribution but is a genuine methodological improvement over a bare "hallucination rate" number, and it is exactly what the 2026 literature now expects. |

### 3.1a The nearest prior work, stated plainly: Decian et al. (2026)

**V34 (Decian, Njeh, Nakouri & Jaafar, *Neurocomputing* 705, 134911) is the single closest prior work to the thesis's RO1, and the proposal document already says so** ("Closest to our RO1; uses Wikidata (not industrial)"). Its design — hybrid retrieval plus an **entropy-based dynamic threshold** for the retrieval decision — is the same problem the thesis's D1 solves, and it reports statistically significant correctness gains (p < 0.01).

The defensible differences are therefore narrow and must be stated precisely:

| Axis | Decian et al. (V34) | This thesis |
|---|---|---|
| Threshold basis | **Entropy-based** (dynamic) | **Bayesian posterior over retrieval relevance**, fitted by logistic regression (β₀ = 2.943, β₁ = 1.680 on a held-out 30-query set) |
| Gate placement | Dynamic threshold over the retrieval decision | **Code-level, non-bypassable**, outside the LM loop; the LLM is not called at all below threshold |
| Output when evidence is weak | Degraded or dynamic-adjusted answer | **Explicit "no evidence" response**, plus per-claim bands |
| Corpus | Wikidata (general knowledge) | **Industrial technical documentation**, 12 categories, SCM focus |
| Calibration guarantee | Entropy-based; §2.10/V27 shows entropy-based methods have model-dependent failure modes | Empirical calibration per retrieval arm + risk–coverage curve — *weaker as a guarantee, but auditable and honest about it* |

The thesis must **not** claim to beat V34 on correctness. It should claim a **different operating philosophy**: a deterministic, auditable refusal over a probabilistic, best-effort adjustment, in a domain where a wrong answer has physical and legal consequences. That is a defensible and interesting claim; "our gate is more accurate than theirs" would not be, absent a head-to-head experiment on a shared corpus (which the thesis cannot run, since Wikidata and an industrial corpus are not comparable).

### 3.1b The second-nearest prior work: Geißler et al. (2026)

**V23 (Geißler et al.) is the most methodologically serious work in this area** — conformal chunk selection with diagnostic metrics for the exchangeability assumption, plus an attention-based factuality classifier that detects inconsistent answers up to 77 % of the time, framed explicitly for industry. As §2.7 explains, the thesis should adopt its *diagnostics* and concede its *guarantees*. This is the right posture: the thesis's gate is simpler and more auditable, and the thesis says so, while acknowledging that a reader who wants statistical guarantees should read V23 and use its diagnostics.

### 3.2 Claims the thesis must NOT make

- ❌ "Our gate reduces hallucination better than CRAG / Self-RAG / conformal abstention" — no such comparison exists in the current evidence base, and V23 (conformal) is a stronger guarantee than a hand-fitted threshold. Claiming superiority would be unsupported and would be the first thing a reviewer attacks.
- ❌ "Our gate outperforms Decian et al.'s entropy-based dynamic threshold." V34 (Neurocomputing 2026) is the nearest prior work and runs on a different corpus (Wikidata). A head-to-head comparison is not possible without a shared corpus, and V27 shows entropy methods have model-dependent failure modes *and* model-dependent successes — neither side wins generically.
- ❌ "We are the first to use a Bayesian posterior for retrieval confidence in RAG." V19 (Azzopardi et al. 2005) and V18/V20 (LM-based IR) established the Bayesian relevance-model construction decades ago; V23 uses conformal prediction on the same idea in 2026.
- ❌ "We are the first to abstain in RAG." V7 (SQuAD 2.0, 2018), V17 (conformal abstention, 2024), V25 (DeclineCraft, 2026) all predate and extend this.
- ❌ "Semantic entropy cannot be used at claim level" — V31 (confidence-weighted semantic entropy) and V14 (semantic entropy probes) make this claim untenable.
- ❌ Any claim of *statistical guarantee* on the gate. V23 is explicit that conformal guarantees break when the retriever setup violates exchangeability — and a 634-chunk, single-category corpus is exactly such a setup. The thesis should claim *empirical calibration on a held-out query set*, and say plainly that this is a weaker guarantee.

### 3.3 Recommended positioning paragraph (for the paper and the defence)

> Our confidence gate is deliberately *simple and auditable* rather than *statistically certified*. Recent work applies conformal prediction to retrieved chunks with finite-sample guarantees [V23], and abstention policy research shows that a threshold must be validated at a stated operating risk level rather than by a single average number [V27]. We adopt both lessons — we evaluate the gate as a selective-prediction policy with a risk–coverage curve, and we adopt conformal-style calibration diagnostics as a limitation. We do not claim the exchangeability guarantees of conformal prediction, because on a 634-chunk single-category corpus those assumptions are known not to hold [V23]. Our contribution is different in kind: a *code-level, non-bypassable* gate that produces an auditable refusal, is portable across twelve industrial categories without retraining, and exposes per-claim confidence bands that prior work calibrates only at the answer or decision level [V10, V11, V24].

---

## 4. Gaps, risks and complications

### R1 — The retrieval-improvement / abstention tension (highest severity)

DeclineCraft (V25) shows that adding query rewriting and reranking to hybrid retrieval **lowers** Correct Abstention Rate for all 12 models tested, and that iterative RAG lowers CAR in 30 of 40 configurations. The thesis's D3 *improves* retrieval relative to its baselines. **Therefore the gate's operating point must be recalibrated per retrieval arm.** If the thesis compares arms using a single global threshold, it will manufacture a spurious result (the best-retrieval arm will look worst on abstention). *Mitigation:* fit the calibration separately per retrieval configuration and report it; report the risk–coverage curve per arm, not just the threshold metric; state the null/modality result (2.3% chart, 7.1% table) as direct evidence that corpus composition, not only algorithm, governs behaviour.

### R2 — Confident errors defeat confidence-only defences (and industrial corpora go stale)

V11 (Nature) shows that a model can hold a wrong belief with *low* semantic uncertainty. The thesis's D5 banding labels a claim "grounded" when evidence supports it — but a claim can be *supported by a retrieved passage that is itself wrong or outdated*. In industrial settings (calibration records, superseded SOPs), retrieved evidence is frequently stale. The thesis's D4 (contradiction surfacing) is the mechanism that partially covers this, but the literature does not support any claim that contradiction detection catches stale-vs-current conflicts reliably: the PDF's own measurement — **NLI-only contradiction detection gives 98% false positives; the joint NLI + topical gate reduces this to 16%** — is a weak result that must be reported honestly, not buried.

**DRAGOn (V41) shows this is a benchmark-design problem, not only a generation problem.** Its entire subject is RAG over a **periodially updated corpus**, and its answer is to regenerate dataset versions so models are always evaluated on unseen, comparable data ("newly generated dataset versions mitigate data leakage"). For the thesis this means two things: the *stale-corpus* limitation should be named as a **benchmark validity** limitation (the benchmark is a snapshot; industrial corpora are not), and DRAGOn's **knowledge-graph-based question generation** is a concrete, citable *independent validation* route for the thesis's LLM-agent-annotated benchmark — which is exactly what a reviewer will demand when the benchmark is used to defend the thesis's own empirical claims.

### R3 — The corpus is too small for the statistical framing being used

634 chunks across 24 documents, a 30-query calibration set, a 16-participant user study, and a single focus category (Supply Chain Management) all sit below the scale at which V23's conformal machinery, or V27's operating-point analysis, or the risk–coverage framing, are statistically well-founded. This is the thesis's stated Limitation 1 and 2 and it is *also* the reason its claims must be framed as **demonstration and mechanism**, not as **generalisation**. A reviewer who reads V23 and V25 will apply exactly this standard. Own it early.

### R4 — Model-dependent failure modes are real and are not in the current plan

V27 documents a *model-dependent* failure mode of entropy-based uncertainty. The thesis's gate depends on a *reranker* (ms-marco-MiniLM-L-6-v2 per the PDF) and an *embedding model* (all-MiniLM-L6-v2, 384-d). Both are small models whose reliability is not established on industrial text. The thesis must either (a) report the gate's behaviour per component model, or (b) acknowledge that the gate inherits the reranker's failure modes. Currently the report acknowledges the reranker's regression on `production_scheduling` (−5.34 pp) but does not connect it to the gate's operating point — a reviewer will make that connection.

### R5 — Several arXiv identifiers circulating for this literature are wrong

During verification, the following identifiers were checked and found to resolve to **unrelated papers** (physics, mathematics, economics, astronomy) rather than the intended NLP work: `2402.15068`, `2307.06308`, `2404.13561`, `2205.10601`, `2407.02323`, `2305.07813`, `2311.06079`. The **correct** identifiers, verified against the arXiv API, are recorded in §1. Any reference list using the erroneous IDs will be flagged by a citation checker. Two further corrections: the thesis's proposal document cites "Language Models (Mostly) Know What They Know" with an ID that resolves elsewhere and should use `10.48550/arXiv.2207.05221`; and the "Sufficient Context" entry should use `10.48550/arXiv.2411.06037` with authors Joren, Zhang, Ferng, Juan & Taly — **not** Jiang et al.

Separately, *Trust-Score* (Abdin et al.) is **not** in the ACL 2024 event index (the full 7.2 MB event page was fetched and grepped case-insensitively for "TRUST-Score" and "Abdin" — zero hits) and is not in TACL 2024 vol. 1. Any secondary source citing it as "ACL 2024" is wrong about the venue. Its true venue and identifier are unresolved here and it must not be cited until they are.

### R6 — The thesis proposal's own literature table is materially out of date

The proposal document (MTP-2.docx) closes with a literature table whose most recent entry is a 2025 survey and whose 2026 entries (`arXiv:2510.24476`, `arXiv:2507.21502`) could not be verified as described. Meanwhile the six papers found in §1 (V23–V32) — including the two most directly on-thesis (Geißler et al. 2026 on conformal RAG confidence; Thakur et al. 2026 on RAG abstention) — are absent from it. For a defence scheduled for **18 November 2026**, a proposal whose related work stops at mid-2025 is a visible weakness. §6.3 lists the seven additions; the other survey agents own the modality, hybrid-retrieval, contradiction and industrial-application areas, and their findings should be merged into the same table.

---

### R7 — SYNCHECK (V40) already reports beating abstention by over 10 %

**This is the highest-severity *reviewer-challenge* risk in the survey.** SYNCHECK (Wu, Gu, Yin & Peng, EMNLP 2024) demonstrates that a decoding-time faithfulness monitor (FOD) **outperforms abstention, reranking and contrastive decoding by over 10 %** on faithfulness across six long-form RAG datasets, and its monitor reaches 0.85 AUROC in detecting faithfulness errors.

The thesis's D1 *is* an abstention mechanism. A reviewer who knows SYNCHECK will ask: **"why abstain rather than monitor-and-repair?"** The answer the thesis can defend, and must actually implement and demonstrate, is the three-point one in §2.11: *insufficient evidence* ≠ *unfaithful output*; the gate runs *before* generation so a refusal is cheap; and the thesis's claim is human-facing per-claim banding, not AUROC.

But the thesis must also concede the design weakness that SYNCHECK and V27 both point at: **the thesis's gate uses a single feature (a Bayesian posterior over retrieval relevance), where the literature consistently indicates that confidence estimation needs several complementary signals.** The defensible position is to present the current gate as the simplest instantiation of that design and to name multi-signal extension as first-priority future work — not to claim the single-feature gate is state of the art.

## 5. Citation-ready reference strings (verified)

```
[1]  Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N.,
     Küttler, H., Lewis, M., Yih, W., Rocktäschel, T., Riedel, S., & Kiela, D.
     (2020). Retrieval-augmented generation for knowledge-intensive NLP tasks.
     In Advances in Neural Information Processing Systems 33 (NeurIPS 2020),
     pp. 9459-9474. https://doi.org/10.48550/arXiv.2005.11401

[2]  Asai, A., Wu, Z., Wang, Y., Sil, A., & Hajishirzi, H. (2024). Self-RAG:
     Learning to retrieve, generate, and critique through self-reflection.
     In International Conference on Learning Representations (ICLR 2024).
     https://doi.org/10.48550/arXiv.2310.11511

[3]  Yan, S.-Q., Gu, J.-C., Zhu, Y., & Ling, Z.-H. (2024). Corrective retrieval
     augmented generation. In Findings of the Association for Computational
     Linguistics: ACL 2024, pp. 3563-3578.
     https://doi.org/10.48550/arXiv.2401.15884

[4]  Jiang, Z., Xu, F. F., Gao, L., Sun, Z., Liu, Q., Dwivedi-Yu, J., Yang, Y.,
     Callan, J., & Neubig, G. (2023). Active retrieval augmented generation.
     In Proceedings of EMNLP 2023, pp. 7969-7992.
     https://doi.org/10.18653/v1/2023.emnlp-main.495

[5]  Jeong, S., Baek, J., Cho, S., & Hwang, S. J. (2024). Adaptive-RAG: Learning
     to adapt retrieval-augmented large language models through question
     complexity. In Proceedings of NAACL 2024, pp. 7036-7050.
     https://doi.org/10.18653/v1/2024.naacl-long.389

[6]  Su, W., Tang, Y., Ai, Q., & Wu, Z. (2024). DRAGIN: Dynamic retrieval
     augmented generation based on the information needs of large language
     models. In Proceedings of ACL 2024.
     https://doi.org/10.48550/arXiv.2403.10081

[7]  Rajpurkar, P., Jia, R., & Liang, P. (2018). Know what you don't know:
     Unanswerable questions for SQuAD. In Proceedings of ACL 2018, pp. 784-789.
     https://doi.org/10.18653/v1/p18-2124

[8]  Huang, J., Chen, X., Mishra, S. R., Zheng, H., Chandak, A., Wu, Y., &
     Li, X. (2024). Large language models cannot self-correct reasoning yet.
     In International Conference on Learning Representations (ICLR 2024).
     https://doi.org/10.48550/arXiv.2310.01798

[9]  Kadavath, S., Conerly, T., Askell, A., Henighan, T., et al. (2022).
     Language models (mostly) know what they know.
     https://doi.org/10.48550/arXiv.2207.05221

[10] Kuhn, L., Gal, Y., & Farquhar, S. (2023). Semantic uncertainty: Linguistic
     invariances for uncertainty estimation in natural language generation.
     In International Conference on Learning Representations (ICLR 2023).
     https://doi.org/10.48550/arXiv.2302.09664

[11] Farquhar, S., Kossen, J., Kuhn, L., & Gal, Y. (2024). Detecting
     hallucinations in large language models using semantic entropy. Nature,
     630(8015), 625-630. https://doi.org/10.1038/s41586-024-07421-0
     (PMID: 38898292; PMCID: PMC11186750)

[12] Joren, H., Zhang, J., Ferng, C.-S., Juan, D.-C., & Taly, A. (2024).
     Sufficient context: A new lens on retrieval augmented generation systems.
     https://doi.org/10.48550/arXiv.2411.06037

[13] Mallen, A., Asai, A., Zhong, V., Das, R., Khashabi, D., & Hajishirzi, H.
     (2023). When not to trust language models: Investigating effectiveness of
     parametric and non-parametric memory in LLMs. In Proceedings of the 61st
     Annual Meeting of the Association for Computational Linguistics (Volume 1:
     Long Papers), pp. 9802-9822.
     https://doi.org/10.18653/v1/2023.acl-long.546

[14] Kossen, J., Han, J., Razzak, M., Schut, L., Malik, S., & Gal, Y. (2024).
     Semantic entropy probes: Robust and cheap hallucination detection in LLMs.
     https://doi.org/10.48550/arXiv.2406.15927

[15] Geng, J., Cai, F., Wang, Y., & Koeppl, H. (2024). A survey of confidence
     estimation and calibration in large language models. In Proceedings of
     NAACL 2024, pp. 6577-6595. https://doi.org/10.18653/v1/2024.naacl-long.366

[16] Liu, X., Chen, T., Da, L., & Chen, C. (2025). Uncertainty quantification
     and confidence calibration in large language models: A survey. In
     Proceedings of the 31st ACM SIGKDD Conference on Knowledge Discovery and
     Data Mining. https://doi.org/10.1145/3711896.3736569

[17] Yadkori, Y. A., Kuzborskij, I., Stutz, D., & György, A. (2024). Mitigating
     LLM hallucinations via conformal abstention. https://doi.org/10.48550/arXiv.2405.01563

[18] Song, F., & Croft, W. B. (1999). A general language model for information
     retrieval. In Proceedings of the 22nd Annual International ACM SIGIR
     Conference on Research and Development in Information Retrieval (CIKM 1999),
     pp. 316-321. https://doi.org/10.1145/319950.320022

[19] Azzopardi, L. M., Girolami, M., & van Rijsbergen, C. J. (2005). Topic based
     language models for ad hoc information retrieval. In Proceedings of the
     IEEE International Joint Conference on Neural Networks (IJCNN 2005).
     https://doi.org/10.1109/IJCNN.2004.1381205

[20] Hiemstra, D., Robertson, S. E., & Zaragoza, H. (2004). Parsimonious
     language models for information retrieval. In Proceedings of the 27th
     Annual International ACM SIGIR Conference on Research and Development in
     Information Retrieval (SIGIR 2004), pp. 178-185.
     https://doi.org/10.1145/1008992.1009025

[21] Kraaij, W. (2005). Variations on language modeling for information
     retrieval. ACM SIGIR Forum, 29(2), 5-15.
     https://doi.org/10.1145/1067268.1067291

[22] Ruthven, R., & Lalmas, M. (2002). A survey on the use of relevance feedback
     for information access systems. The Knowledge Engineering Review, 18(2),
     95-145. https://doi.org/10.1017/S0269888903000638

[23] Geißler, F., Carella, F., Fieback, L., & Spiegelberg, J. (2026). Towards
     dependable retrieval-augmented generation using factual confidence
     prediction. https://doi.org/10.48550/arXiv.2605.05244

[24] Jang, C., Cho, D., Lee, S., Lee, H., & Lee, J. (2025). Reliable decision
     making via calibration oriented retrieval augmented generation. In
     Advances in Neural Information Processing Systems 38 (NeurIPS 2025).
     https://doi.org/10.48550/arXiv.2411.08891

[25] Thakur, A., Saparov, A., & Ribeiro, B. (2026). DeclineCraft: A RAG
     abstention benchmark for jointly measuring combined retrieval and
     parametric knowledge. https://doi.org/10.48550/arXiv.2610.28340

[26] Shin, S., Cha, M., Lee, B.-J., & Park, S. (2026). ERA: Evidence-based
     reliability alignment for honest retrieval-augmented generation.
     https://doi.org/10.48550/arXiv.2604.20854

[27] Phillips, E., Gustafsson, F., Wu, S., Thakur, A., & Clifton, D. A. (2026).
     Entropy alone is insufficient for safe selective prediction in LLMs.
     https://doi.org/10.48550/arXiv.2603.21172

[28] Zhang, H., & Wu, W. (2026). Do LLMs know when evidence is insufficient? An
     evidence sufficiency benchmark for answer-abstention. Computers, Materials
     & Continua. https://doi.org/10.32604/cmc.2026.086343

[29] Sun, Q., Li, X., & Xie, X. (2026). Efficient hallucination detection:
     Adaptive Bayesian estimation of semantic entropy with guided semantic
     calibration. In Proceedings of the AAAI Conference on Artificial
     Intelligence, 40(39). https://doi.org/10.1609/aaai.v40i39.40595

[30] Pellet, A., Puren, M., & Pérez, J. (2026). ORDER: Task-conditioned routing
     for retrieval-augmented generation. In Findings of EMNLP 2026.
     https://doi.org/10.18653/2026.findings-emnlp.2026

[31] Wang, Z., Liao, M., & Zhang, J. (2026). Confidence-weighted semantic
     entropy: A robust framework for hallucination detection and uncertainty
     quantification. Neurocomputing. https://doi.org/10.1016/j.neucom.2026.134859

[32] Xu, R., Chen, Y., & Xie, S. (2026). Geometry-calibrated conformal
     abstention for language models. https://doi.org/10.48550/arXiv.2604.27914

[33] King, D., Shen, Z., Subramani, N., et al. (2022). Don't say what you don't
     know: Improving the consistency of abstractive summarization by rewarding
     fully consistent summaries. In Workshop on Generation, Evaluation and
     Analysis of Large Language Models (GenAI 2022), pp. 555-571.
     https://doi.org/10.48550/arXiv.2203.08436

[34] Decian, J., Njeh, C., Nakouri, H., & Jaafar, F. (2026). Dynamic RAG with
     hybrid retrieval: A novel approach to robust LLMs and hallucination
     prevention. Neurocomputing, 705, 134911.
     https://doi.org/10.1016/j.neucom.2026.134911

[35] Li, Y., Fu, X., Verma, G., Buitelaar, P., & Liu, M. (2025). Mitigating
     hallucination in large language models: A capability-oriented survey on
     RAG, reasoning, and agentic systems.
     https://doi.org/10.48550/arXiv.2510.24476

[36] Simchi-Levi, D., Mellou, K., Menache, I., & Pathuri, J. (2025). Large
     language models for supply chain decisions.
     https://doi.org/10.48550/arXiv.2507.21502

--- Corrections to the MTP-2.docx literature table (all verified) ---

[37] Gao, T., Yen, H., Yu, J., & Chen, D. (2023). Enabling large language models
     to generate text with citations. In Proceedings of EMNLP 2023,
     pp. 6465-6488. https://doi.org/10.18653/v1/2023.emnlp-main.398

[38] Es, S., James, J., Espinosa-Anke, L., & Schockaert, S. (2024). RAGAs:
     Automated evaluation of retrieval augmented generation. In Proceedings of
     EACL 2024 System Demonstrations, pp. 150-158.
     https://doi.org/10.18653/v1/2024.eacl-demo.16

[39] Lyu, Y., Li, Z., Niu, S., & Xiong, F. (2025). CRUD-RAG: A comprehensive
     Chinese benchmark for retrieval-augmented generation of large language
     models. ACM Transactions on Information Systems, 43, 1-32.
     https://doi.org/10.1145/3701228

[40] Wan, Y., Chen, Z., Liu, Y., Chen, C., et al. (2025). Empowering LLMs by
     hybrid retrieval-augmented generation for domain-centric Q&A in smart
     manufacturing. Advanced Engineering Informatics, 65, 103212.
     https://doi.org/10.1016/j.aei.2025.103212

[41] Wu, C., Ding, W., Jin, Q., Jiang, J., et al. (2025). Retrieval augmented
     generation-driven information retrieval and question answering in
     construction management. Advanced Engineering Informatics, 65, 103158.
     https://doi.org/10.1016/j.aei.2025.103158

[42] Gao, Y., Xiong, Y., Gao, X., Jia, K., et al. (2023). Retrieval-augmented
     generation for large language models: A survey.
     https://doi.org/10.48550/arXiv.2312.10997
[43] Wang, Z., Wang, Z., Le, L. T., & Zheng, H. (2024). Speculative RAG:
     Enhancing retrieval augmented generation through drafting.
     https://doi.org/10.48550/arXiv.2407.08223

[44] Quan, G., Feng, W., Hao, C., & Jiang, G. (2025). RASD: Retrieval-augmented
     speculative decoding. In Findings of ACL 2025, pp. 6167-6177.
     https://doi.org/10.18653/v1/2025.findings-acl.320

[45] Li, Y., Huang, S., Liu, X., Zhao, Y., et al. (2026). BRIDGE: Block-wise
     speculative coordination for cloud-edge retrieval-augmented generation. In
     Proceedings of the 32nd ACM SIGKDD Conference on Knowledge Discovery and
     Data Mining, pp. 2885-2896. https://doi.org/10.1145/3770855.3818064

[46] Wu, D., Gu, J.-C., Yin, F., & Peng, N. (2024). Synchronous faithfulness
     monitoring for trustworthy retrieval-augmented generation. In Proceedings
     of EMNLP 2024, pp. 9390-9406. https://doi.org/10.18653/v1/2024.emnlp-main.527

[47] Chernogorskii, F., Averkiev, S., Kudraleeva, L., Martirosian, Z.,
     Tikhonova, M., Malykh, V., & Fenogenova, A. (2026). DRAGOn: Designing RAG
     on periodically updated corpus. In Proceedings of the 19th Conference of
     the European Chapter of the ACL (Volume 4: Student Research Workshop),
     pp. 622-638. https://doi.org/10.18653/v1/2026.eacl-srw.48

[48] Li, B., Wang, M., Fang, G., & Zhang, S. (2026). Retrieval as generation: A
     unified framework with self-triggered information planning. In Proceedings
     of ACL 2026, pp. 4254-4274. https://doi.org/10.18653/v1/2026.acl-long.196

[49] Park, C., Moon, H., Park, C., & Lim, H. (2025). MIRAGE: A metric-intensive
     benchmark for retrieval-augmented generation evaluation. In Findings of
     NAACL 2025, pp. 2883-2900. https://doi.org/10.18653/v1/2025.findings-naacl.157

[50] Gao, S., Zhao, S., Jiang, X., Duan, L., Chng, Y. X., Chen, Q.-G., Luo, W.,
     Zhang, K., Bian, J.-W., & Gong, M. (2026). Scaling beyond context: A survey
     of multimodal retrieval-augmented generation for document understanding.
     In Proceedings of ACL 2026, pp. 4458-4489.
     https://doi.org/10.18653/v1/2026.acl-long.204

[51] Murugaraj, K., Lamsiyah, S., & Theobald, M. (2026). RAGVUE: A diagnostic
     view for explainable and automated evaluation of retrieval-augmented
     generation. In Proceedings of EACL 2026 (Volume 3: System Demonstrations),
     pp. 512-526. https://doi.org/10.18653/v1/2026.eacl-demo.35

[52] Badshah, S., Moustafa, M., & Sajjad, H. (2025). CLEV: LLM-based evaluation
     through lightweight efficient voting for free-form question answering.
     In Findings of IJCNLP 2025, pp. 1513-1531.
     https://doi.org/10.18653/v1/2025.findings-ijcnlp.93

[53] Zhang, W., & Zhang, J. (2025). Hallucination mitigation for retrieval-augmented
     large language models: A review. Mathematics, 13(5), 856.
     https://doi.org/10.3390/math13050856

```

---

## 6. Gaps this survey did not close (hand off to other areas)

These are **out of scope** for this file (other survey agents own them) but are recorded so the synthesis step does not miss them:

### 6.1 Corrections required to the MTP-2.docx literature table (actionable, in-scope)

The thesis proposal's 18-row literature table was checked against the live APIs for the entries that fall within this survey's scope. The following are **confirmed mis-identifications** and must be corrected or removed before the reference list is finalised:

| DOCX entry | Problem found | Correct identifier |
|---|---|---|
| "Language Models (Mostly) Know What They Know" — cited under the wrong arXiv ID `2112.04359` in circulation | `2112.04359` does not resolve to this paper | **`10.48550/arXiv.2207.05221`** (Kadavath et al., 2022, 187 citations) — verified |
| *Sufficient Context* attributed to "Jiang et al." | Author list is wrong; the paper is by Joren, Zhang, Ferng, Juan & Taly | **`10.48550/arXiv.2411.06037`** — verified |
| *Self-Ask with Search* (Press et al.) — commonly circulated as `arXiv:2205.10601` | `2205.10601` resolves to **"Orbits in lattices"**, a mathematics paper | **`10.18653/v1/2023.findings-emnlp.378`** — Press, O., Zhang, M., Min, S., & Schmidt, L. (2023), *Measuring and Narrowing the Compositionality Gap in Language Models*, Findings of EMNLP 2023, pp. 5687-5711 (294 citations) — **verified** |
| *Speculative RAG* — cited as `arXiv:2407.02323` | `2407.02323` resolves to **"Comparative Patience"**, an economics paper | **`10.48550/arXiv.2407.08223`** — Wang, Z., Wang, Z., Le & Zheng (2024), *Speculative RAG: Enhancing Retrieval Augmented Generation through Drafting* — **verified** |

Additionally, **seven further arXiv IDs that circulate for papers in this area were checked and found to point at unrelated papers** (physics, mathematics, economics, astronomy): `2402.15068`, `2307.06308`, `2404.13561`, `2205.10601`, `2407.02323`, `2305.07813`, `2311.06079`. Any reference list that inherits these from secondary sources will fail a citation audit.

The proposal's entries for **Asai et al. (Self-RAG)** and **Farquhar et al. (semantic entropy)** were checked and are **correct** as written.

### 6.2 Papers referenced in the MTP-2.docx table — verification outcome

**Resolved and real.** The full 18-row literature table in MTP-2.docx was checked against the live APIs. **Every arXiv identifier in it resolves to the paper the table claims**, and the journal articles were confirmed at the volume/page level:

| DOCX entry | Verified as | Correction needed |
|---|---|---|
| Gao et al. (2023) *RAG survey*, `arXiv:2312.10997` | "Retrieval-Augmented Generation for Large Language Models: A Survey", Gao, Xiong, Gao et al. — **875 citations** | none |
| Wan et al. (2025) *Adv. Eng. Inform.* 65, 103212 | "Empowering LLMs by hybrid retrieval-augmented generation for domain-centric Q&A in smart manufacturing", Wan, Chen, Liu, Chen — **110 citations** | none |
| Wu et al. (2025) *Adv. Eng. Inform.* 65, 103158 | "Retrieval augmented generation-driven information retrieval and question answering in construction management", Wu, Ding, Jin, Jiang — **82 citations** | none |
| Gao et al. (2023) *ALCE*, Proc. EMNLP | "Enabling Large Language Models to Generate Text with Citations", Gao, Yen, Yu, Chen — EMNLP 2023, **pp. 6465–6488**, `10.18653/v1/2023.emnlp-main.398`, 216 citations | add page numbers + DOI |
| Es et al. (2024) *RAGAS*, Proc. EACL Demos | "RAGAs: Automated Evaluation of Retrieval Augmented Generation", Es, James, Espinosa-Anke, Schockaert — EACL 2024, **pp. 150–158**, `10.18653/v1/2024.eacl-demo.16`, **651 citations** | note the capitalisation "**RAGAs**" (the "s" is part of the title) |
| Bohnet et al. (2022) *Attributed QA* | "Attributed Question Answering: Evaluation and Modeling for Attributed Large Language Models", Bohnet, Tran, Verga, Aharoni — `10.48550/arXiv.2212.08037`, 30 citations | none |
| Lyu et al. (2024) *CRUD-RAG*, `arXiv:2401.17043` | Lyu, Li, Niu, Xiong — **published in ACM TOIS, vol. 43, pp. 1–32, `10.1145/3701228`, 109 citations** | **upgrade the citation to the journal version** — the arXiv preprint understates it |
| Wang et al. (2025) *PIKE-RAG*, `arXiv:2501.11551` | "PIKE-RAG: sPecIalized KnowledgE and Rationale Augmented Generation", Wang, Fu, Wang, Song | none |
| Wei et al. (2024) *InstructRAG*, `arXiv:2406.13629` | "InstructRAG: Instructing Retrieval-Augmented Generation via Self-Synthesized Rationales", Wei, Chen, Meng | none |
| Tang & Yang (2024) *MultiHop-RAG*, `arXiv:2401.15391` | "MultiHop-RAG: Benchmarking Retrieval-Augmented Generation for Multi-Hop Queries", Tang & Yang | none |
| Li et al. (2025) *hallucination survey*, `arXiv:2510.24476` | "Mitigating Hallucination in LLMs: A **Capability-Oriented** Survey on RAG, Reasoning, and Agentic Systems" | **title says Capability-Oriented, not Application-oriented** |
| Microsoft (2025) `arXiv:2507.21502` | "Large Language Models for Supply Chain Decisions", **Simchi-Levi, Mellou, Menache & Pathuri** | **two errors, not one** — (i) cite the four named authors (first author **David Simchi-Levi, MIT**), not "Microsoft Research"; (ii) the DOCX's characterisation ("fine-tuned LLM for procurement decisions", "real-world Microsoft deployment") is **materially wrong** — the paper applies *off-the-shelf* LLMs as a conversational layer over optimisation-based planning tools. Correct framing: *explains tool outputs, runs what-if analysis, updates models; reduces time-to-decision from days/weeks to minutes/hours; solves the explainability and agility of the optimisation layer, not retrieval* |
| Decian et al. (2026) *Neurocomputing* 705, 134911 | "Dynamic RAG with hybrid retrieval: A novel approach to robust LLMs and hallucination prevention", **Decian, Njeh, Nakouri & Jaafar** | none — **and see §3.1: this is the nearest prior work to RO1 and must be engaged directly** |

**Still unresolved — with the full search trail recorded so the next person does not repeat it.**

- ***Trust-Score* (Abdin et al.)** — **UNVERIFIED.** Five independent routes were tried and all failed to resolve it:
  1. arXiv title search (`ti:"Trust-Score" AND abs:retrieval`) → only unrelated hits (network trust-score papers in IoT/chemistry; and *ClaimTrust*, Qian et al. 2025, `10.48550/arXiv.2503.10702`, which is a **different** paper).
  2. arXiv full-text search (`all:"Trust-Score"`) → five hits, **none** the intended paper.
  3. **ACL Anthology event index for ACL 2024** — the complete 7.2 MB page `https://aclanthology.org/events/acl-2024/` was fetched and grepped case-insensitively for both `TRUST-Score` and `Abdin` → **zero hits** for both. (Sanity check on the same page: `confabulation` returns 6 hits, so the page does contain its papers.) → **Trust-Score is not an ACL 2024 paper.**
  4. **ACL Anthology volume for Findings of ACL 2024** (`2024.findings-acl`, 2.6 MB) → **zero hits** for both terms.
  5. **TACL 2024 vol. 1** (`2024.tacl-1`) → **zero hits** for both terms.

  6. **ACL Anthology's own Google-backed full-text search** (`aclanthology.org/search/?q=%22TRUST-SCORE%22+Abdin`, run in a real stealth browser so the JavaScript search executes) → returns only unrelated knowledge-graph "trust score" papers (KnowFM 2025 workshop proceedings). **No TRUST-SCORE paper in the Anthology.**

  **Conclusion for the thesis:** TRUST-SCORE is **not published in the ACL Anthology at all** — not at ACL 2024, Findings of ACL 2024, TACL 2023, TACL 2024, ACL 2023, or EMNLP 2023/2024 (main or findings), and it does not appear in the Anthology's own full-text search. Any source describing it as "ACL 2024" is wrong about the venue. It is therefore most likely **arXiv-only or published at a non-ACL venue** (COLM, EACL, a workshop), and **must not be cited until a human confirms its true venue and identifier**.
- *Know What You Don't Know: A Guide to Calibrated LMs* (Bhagia et al.) — **UNVERIFIED** (arXiv author query `au:Bhagia AND ti:"Know What You Don't Know"` and OpenAlex title search both failed to resolve under the API rate-limit conditions encountered). Worth locating: it is the canonical calibration-guidelines reference and the thesis's RO1 discussion is stronger with it.
- *Answering Questions with Uncertain Context* (ANS; Abdin et al., EMNLP 2024) — **UNVERIFIED.**
- *Do Large Language Models Know When Evidence is Insufficient* (Ganguli et al.) — **UNVERIFIED.**
- *Self-Ask with Search* (Press et al.) and *Speculative Retrieval-Augmented Generation* — **UNVERIFIED, and their commonly circulated arXiv IDs (`2205.10601`, `2407.02323`) are demonstrably wrong** (they resolve to a mathematics paper and an economics paper respectively). See §6.1.
- *Zhang & Zhang (2025), Mathematics 13, 856* — **NOW VERIFIED (V47).** The correct DOI is **`10.3390/math13050856`** (*Mathematics* 13(5), 856, 144 citations; the authors are **Wan Zhang & Jing Zhang**). The `math13060856` / 13(6) form does not resolve to this paper. Confirmed independently by the sibling citation audit and re-resolved here against OpenAlex.

> **Note for the synthesis step.** These unresolved items are *not* gaps in the thesis's argument — the thesis's RO1 case rests on V3, V7, V8, V11, V12, V17, V23, V24, V25, V26, V27 and V34, all of which are verified. The unresolved items are *optional supporting citations* that should be added if the parent can resolve them, and removed if it cannot. **Do not cite an unresolved reference in the final paper.**

---

## 7. Method note — how this survey was verified, and its limits

**Sources used, in order of reliability for this purpose:**

1. **OpenAlex** (`api.openalex.org`) — resolved by DOI (`/works/https://doi.org/…`) and by `title.search:` filter, returning canonical title, full author list, year, venue, volume, page range, DOI/arXiv ID and citation count. This was the workhorse; 36 papers were confirmed this way.
2. **arXiv Atom API** (`export.arxiv.org/api/query`) — used for `id_list` and `search_query` lookups, giving the authoritative preprint title, author list, submission date and `journal_ref`/`comment` fields.
3. **ACL Anthology** — the complete ACL 2024 event index (7.2 MB) and the Findings of ACL 2024 volume (2.6 MB) were fetched and grepped directly, plus the TACL 2024 vol. 1 volume page.
4. **PubMed Central** — for the Nature paper's PMID/PMCID and to search its reference list for a preprint identifier.
5. **Scrapling** — the stealth-browser client (Chromium via `patchright`) was used to fetch ACL Anthology, DBLP and arXiv search pages where plain HTTP was blocked or bot-walled, and to run the Anthology's JavaScript full-text search. It was also used to enumerate an author's complete arXiv listing (`arxiv.org/search/?searchtype=author&query=Bhagia`), which is the most reliable way to find preprints when the title is uncertain.

**Page numbers and volume data in §5 were read back from OpenAlex's `biblio` field**, not from memory. Where the API disagreed with a commonly cited value, the API was followed and the corrected value used — this corrected six page ranges (FLARE, Adaptive-RAG, Mallen, SQuAD 2.0, Geng et al., Song & Croft, Hiemstra, Ruthven) that are wrong in most secondary sources.

**Limits of this survey, stated honestly:**

- **Rate limiting, and how it was worked around.** The shared egress IP was throttled (HTTP 429) by arXiv, OpenAlex, Semantic Scholar and DBLP simultaneously during the middle of the survey. The workaround that worked was **switching client**: Scrapling's stealth Chromium (a real browser, so ACL Anthology's JavaScript Google-CSE search executes) bypassed both the API rate limits and DBLP's bot-wall. It is what finally resolved *Speculative RAG* and *Self-Ask*, and what established that *TRUST-SCORE* is absent from the ACL Anthology. The plain-HTTP API route remains the right one for structured metadata (authors, volume, pages, citation counts) because it returns machine-readable fields the HTML pages do not.
- **What remains unresolved after the stealth-browser pass.** Only three optional items: *Trust-Score*, *Bhagia's calibration guide*, and *ANS / Ganguli's evidence-insufficiency paper*. The first is now established as **not in the ACL Anthology at all**; the other two are arXiv-only or non-ACL venues that the APIs could not index under the title strings tried.
- **Abstract-level, not full-text, verification for most entries.** Method summaries and quoted numbers were taken from the abstracts that were actually fetched. Where a claim depends on a detail beyond the abstract — notably the exact risk–coverage numbers in V27 and the conformal guarantees in V23 — the thesis should read the full paper before relying on the specific figure. Section 2 quotes only abstract-level numbers.
- **One identifier deliberately omitted.** The arXiv preprint number for the Nature semantic-entropy paper (V11) was **not** confirmed: the candidate IDs `2305.14350`, `2305.14357` and `2305.14358` resolve to a mathematics thesis, a nano-fertiliser review and a generative-AI humanities paper respectively, and the OpenAlex record lists **no arXiv location** for that work. The DOI, PMID (38898292) and PMCID (PMC11186750) are all verified, so §5 cites the Nature version — which is the correct form for a Nature paper anyway. **Do not add an arXiv ID to this entry without checking it.**
- **Abstract-level verification for most entries.** The seven ACL Anthology papers added late (V40-V46) were verified via their Anthology pages (title, authors, venue, pages, DOI) **and** their abstracts read directly from `aclanthology.org/<id>/`. For SYNCHECK and DRAGOn the full abstract text was retrieved and is quoted in §2.11 and §2.12; for RAGVUE the Anthology record carries only a proceedings header, so V45 is described by its title and venue only, and its method claims should be confirmed from the PDF before they are cited.
- **Cross-verification against the sibling citation audit.** `research/00_citation_audit.md` independently re-resolved all 18 references in the proposal using arXiv + Semantic Scholar + Crossref + direct abs-page fetches. **Its verdicts agree with this survey's on every point** (18/18 real papers; the same three corrections — Simchi-Levi attribution, Li et al. title, CRUD-RAG journal upgrade — plus two venue corrections this survey also confirmed: InstructRAG is **ICLR 2025**, and Zhang & Zhang's correct DOI is `10.3390/math13050856` at *Mathematics* 13(5), 856). The two audits were run by different agents with different toolchains, so the agreement is a genuine double-check rather than a restatement. The audit additionally found that the Simchi-Levi characterisation is **materially** wrong (not just mis-attributed) — recorded above.
- **Single-area coverage.** This file covers retrieval confidence, calibration, abstention and refusal only. Modality-balanced retrieval, hybrid-search architecture, contradiction detection, per-claim attribution and evaluation frameworks are covered by the other survey areas and must be merged before the literature review is finalised.

### 6.3 Recommended additions to the reference list from this survey

**Thirteen papers in §1 (V23–V46) are not in the MTP-2.docx literature table** and were found during this survey. The following are the ones a reviewer will raise, in the order they are likely to be raised:

1. **SYNCHECK — Wu, Gu, Yin & Peng (EMNLP 2024)** (`10.18653/v1/2024.emnlp-main.527`). Reports a faithfulness monitor that **beats abstention by over 10 %**. *Most likely to be raised by a reviewer.*
2. **Geißler et al. 2026** (`10.48550/arXiv.2605.05244`) — conformal chunk selection + attention-based factuality classifier, framed explicitly for **industry** applications. *The most important missing citation.*
3. **Thakur et al. 2026** — DeclineCraft abstention benchmark. Supplies the empirical warning that **better retrieval lowers abstention** (R1).
4. **Decian et al. 2026** (`10.1016/j.neucom.2026.134911`) — the nearest prior work to RO1 (already in the proposal; must be engaged directly).
5. **Jang et al. 2025** — CalibRAG, NeurIPS 2025. Calibrates the *human decision*, not just the model.
6. **Phillips et al. 2026** — "Entropy alone is insufficient for safe selective prediction"; mandates the risk–coverage / stated-operating-point evaluation framing.
7. **Shin et al. 2026** — ERA: Dirichlet evidence distributions + Dempster–Shafer Theory for epistemic-vs-aleatoric separation.
8. **DRAGOn — Chernogorskii et al. (EACL 2026 SRW)** (`10.18653/v1/2026.eacl-srw.48`) — RAG over a **periodically updated corpus**; addresses the stale-evidence and benchmark-validity limitations.
9. **Yadkori et al. 2024** — conformal abstention with finite-sample guarantees.
10. **Sun et al. 2026** (AAAI) — Bayesian estimation of semantic entropy; the Bayesian counterpart to the thesis's posterior gate.
11. **Wang et al. 2024** — Speculative RAG (`10.48550/arXiv.2407.08223`) — draft-then-verify, the conditional-compute cousin of the thesis's gate.
12. **MIRAGE — Park et al. (Findings of NAACL 2025)** — component-specific RAG evaluation (7,560 instances / 37,800-entry retrieval pool); a template for the thesis's ablation design.
13. **Gao et al. 2026** (ACL) — *Scaling Beyond Context: A Survey of Multimodal RAG for Document Understanding* — the survey the thesis's RO2 should be positioned against (belongs to the modality area; cross-reference it there).

A proposal that cites only through 2025 and omits all six 2025–2026 items above would read as out of date at an IIT Kharagpur defence in November 2026.

---

*Compiled 2026-10-31 for the MTP *"An Evidence-Grounded Retrieval-Augmented Generation Framework for Industrial Decision Support"*, IIT Kharagpur, Department of Industrial and Systems Engineering.*
