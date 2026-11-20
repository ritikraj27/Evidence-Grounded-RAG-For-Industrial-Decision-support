# D4 — Contradiction Surfacing: Literature Survey and Verification

**Scope:** the thesis design move *D4 — Cross-document contradiction surfacing (joint NLI + topical gate)*, plus
the evidence base it depends on (NLI datasets, truth discovery, fact checking, conflict-aware RAG,
per-claim attribution).

**Verification protocol.** Every citation below was resolved against a live source — ACL Anthology
volume index pages (authoritative BibTeX), the arXiv `abs` pages, or the Crossref REST API — and the
title/authors/year/DOI were read off the source record. Metadata was **not** taken from memory.
Where a paper could not be resolved, it is listed under §7 as **UNVERIFIED** rather than asserted.
Two APIs were unusable for parts of this survey (see §8): Semantic Scholar is IP-rate-limited from
this host and OpenAlex's free daily budget for the IP is exhausted.

---

## 1. Verified bibliography

### 1.1 NLI foundations and datasets

| # | Paper | Venue / year | Verified ID | Method in one line | Key finding with numbers |
|---|---|---|---|---|---|
| N1 | Bowman, Angeli, Potts, Manning — *A Large Annotated Corpus for Learning Natural Language Inference* (SNLI) | EMNLP 2015 | arXiv `1508.05326` | Crowd workers write entail/contradict/neutral hypotheses against a caption (premise) | **570K** sentence pairs — two orders of magnitude larger than prior resources; lexicalised classifiers become competitive |
| N2 | Williams, Nangia, Bowman — *A Broad-Coverage Challenge Corpus for Sentence Understanding through Inference* (MultiNLI) | NAACL-HLT 2018 | DOI `10.18653/v1/N18-1101` | 433K+ premise–hypothesis pairs across 11 genres | Multi-genre coverage; Crossref reports **971 citations**. Became the default transfer benchmark |
| N3 | Nie, Bowman, et al. — *Adversarial NLI: A New Benchmark for Natural Language Understanding* (ANLI) | ACL 2020 | DOI `10.18653/v1/2020.acl-main.441` | Three progressively harder rounds collected adversarially against the model in the previous round | Hardest NLI benchmark; Crossref reports **204 citations**. Round 1→3 accuracy collapses for every system tested |
| N4 | Liu et al. — *WANLI: Worker and AI Collaboration for Natural Language Inference Dataset Creation* | Findings of EMNLP 2022 | DOI `10.18653/v1/2022.findings-emnlp.508` | Native-speaker workers assist a trained annotator model on tricky examples | **29 citations**; adversarial-collection procedure shown to also work with LLM assistance |
| N5 | Gururangan et al. — *Annotation Artifacts in Natural Language Inference Data* | NAACL 2018 | arXiv `1803.02324` | Train a classifier on the **hypothesis alone**, ignoring the premise | A hypothesis-only model reaches **67% on SNLI** and **53% on MultiNLI** — the label is partly guessable from the hypothesis alone. *"the success of NLI models to date has been overestimated"* |
| N6 | McCoy, Pavlick, Lin et al. — *Avoiding the Hypothesis-Only Bias in NLI via Ensemble Adversarial Training* | EMNLP 2020 | DOI `10.18653/v1/2020.emnlp-main.665` | Ensemble of adversaries penalises hypothesis-only artefacts | Reduces artefact exploitation *in the sentence representations*, which single-adversarial training (Belinkov et al. 2019) does not fix |
| N7 | Hossain, Kovatchev, Dutta, Kao, Wei & Blanco — *An Analysis of Natural Language Inference Benchmarks through the Lens of Negation* | EMNLP 2020 | DOI `10.18653/v1/2020.emnlp-main.732` | New benchmark where negation is decisive | Negation is **underrepresented** in existing NLI benchmarks; one can ignore the few negations and still score well; **state-of-the-art transformers struggle** on the negation-critical pairs |
| N8 | Koreeda & Manning — *ContractNLI: A Dataset for Document-level Natural Language Inference for Contracts* | Findings of EMNLP 2021 | DOI `10.18653/v1/2021.findings-emnlp.164` | Clause pairs from contracts, with an entailment-only label set and a "not-inferred" class | Document-level NLI for long, structured professional text; the closest published analogue to engineering-manual inference |
| N9 | Yin, Radev & Xiong — *DocNLI: A Large-scale Dataset for Document-level Natural Language Inference* | Findings of ACL 2021 | DOI `10.18653/v1/2021.findings-acl.435` | Sentence pairs from Wikipedia documents, annotated at the **document** level (sentence pair + which document it came from) | Establishes that a sentence pair can be neutral *in one document* and contradicting *in another* — the document context changes the label |
| N10 | Mathur, Kunapuli, Bhat, Shrivastava, Manocha & Singh — *DocInfer: Document-level Natural Language Inference using Optimal Evidence Selection* | EMNLP 2022 | DOI `10.18653/v1/2022.emnlp-main.51` | Jointly selects the minimal evidence sentences needed to label a pair | Evidence selection is necessary — not every sentence in the document is evidence; the selection step is learned |
| N11 | Wang, Cao, Li, Huang, Wang & Shao — *R²F: A General Retrieval, Reading and Fusion Framework for Document-level NLI* | EMNLP 2022 | DOI `10.18653/v1/2022.emnlp-main.204` | Retrieve → read → fuse for doc-level NLI | Retrieval is a necessary stage of document-level inference, not an optional one |
| N12 | Sadat & Caragea — *SciNLI: A Corpus for Natural Language Inference on Scientific Text* | ACL 2022 | DOI `10.18653/v1/2022.acl-long.511` | **107,412** sentence pairs from scholarly papers | Best model (XLNet) reaches **Macro F1 78.18% / accuracy 78.23%** — *"substantial room for improvement"* |
| N13 | Sadat & Caragea — *MSciNLI: A Diverse Benchmark for Scientific Natural Language Inference* | NAACL 2024 | DOI `10.18653/v1/2024.naacl-long.90` | **132,320** pairs across five new scientific domains | Best PLM **Macro F1 77.21%**; best **LLM Macro F1 only 51.77%**; domain shift *degrades* scientific-NLI performance |
| N14 | Bruno & Roth — *LawngNLI: A Long-Premise Benchmark for In-Domain Generalization…* | Findings of EMNLP 2022 | DOI `10.18653/v1/2022.findings-emnlp.369` | Long, multigranular premises from US legal opinions with auto labels validated by humans | Long-premise NLI is a distinct problem: near-top performance on long premises can be reached by fine-tuning on short ones — the long-premise skill is learned, not assumed |
| N15 | — *A Multilingual Perspective Towards the Evaluation of Attribution Methods in Natural Language Inference* | EMNLP 2022 | DOI `10.18653/v1/2022.emnlp-main.101` | Evaluate attribution/evidence methods across languages | Attribution quality is language-dependent — relevant to claiming an English-only industrial benchmark generalises |

### 1.2 Fact checking, claim verification, truth discovery

| # | Paper | Venue / year | Verified ID | Method | Key finding / numbers |
|---|---|---|---|---|---|
| F1 | Aly et al. — *The Fact Extraction and VERification Over Unstructured and Structured information* (FEVEROUS) | FEVER Workshop, ACL 2021 | DOI `10.18653/v1/2021.fever-1.1` | Full-document + table evidence fact verification | **84 citations**; establishes evidence provenance as a first-class output of the verifier |
| F2 | Schuster, Fisch, Barzilay — *Get Your Vitamin C! Robust Fact Verification with Contrastive Evidence* (VitaminC) | NAACL 2021 | arXiv `2103.08541` | **100,000+** Wikipedia revisions; **400,000+** claim–evidence pairs whose evidence pairs are near-identical except that one supports the claim and one does not | Training on the contrastive design improves accuracy by **10% on adversarial fact verification** and **6% on adversarial NLI** |
| F3 | Kamoi, Goyal, Rodriguez, Durrett et al. — *WiCE: Real-World Entailment for Claims in Wikipedia* | EMNLP 2023 | DOI `10.18653/v1/2023.emnlp-main.470` | Fine-grained claim–evidence entailment with **sub-sentence** claim units and a **minimal** supporting-evidence set | Textual-entailment models **underperform under domain shift**; per-subclaim evidence is required for faithful attribution |
| F4 | — *Verifiable Generation with Subsentence-Level Fine-Grained Citations* (SCiFi) | Findings of ACL 2024 | DOI `10.18653/v1/2024.findings-acl.920` | **10K** Wikipedia paragraphs with **subsentence-level** citations | Sentence-level citations are too coarse to say *which part* of the sentence is supported |
| F5 | Chiang & Lee — *Merging Facts, Crafting Fallacies: Evaluating the Contradictory Nature of Aggregated Factual Claims…* | Findings of ACL 2024 | DOI `10.18653/v1/2024.findings-acl.160` | Tests the assumption that factually-correct claims aggregate to a factually-correct paragraph | **FActScore and citation metrics both fail** when correct facts are combined into a false paragraph because of **entity ambiguity** — a direct warning for the thesis's per-claim aggregation step |
| F6 | — *CREPE: Open-Domain Question Answering with False Presuppositions* | ACL 2023 | DOI `10.18653/v1/2023.acl-long.583` | QA dataset built from a natural distribution of presupposition failures | **25%** of real user questions contain false presuppositions; adaptations of open-domain QA models find them only moderately well and struggle to say whether the presupposition is false |
| F7 | Kargupta, Tian & Han — *Beyond True or False: Retrieval-Augmented Hierarchical Analysis of Nuanced Claims* (ClaimSpect) | ACL 2025 | DOI `10.18653/v1/2025.acl-long.1434` | Decomposes a nuanced claim into aspects/sub-aspects and validates each | Many industrial claims cannot be labelled true/false; a hierarchical aspect decomposition is the alternative to a binary verdict |
| F8 | — *Understanding Fact Verification and Evidence Extraction Benchmark* (FEVER) / *Fact or Fiction: Verifying Scientific Claims* | EMNLP 2020 | DOI `10.18653/v1/2020.emnlp-main.609` | Scientific-claim verification | A dedicated scientific-claim benchmark exists — the industrial analogue is a gap the thesis may claim |
| F9 | — *Truth Discovery on Categorical Multi-Valued Attributes with Source Relations* | IEEE COMCOMM 2018 | DOI `10.1109/compcomm.2018.8780660` | Truth discovery when sources have **relations** (one source copies another) | Copying/derivation between sources must be modelled — a copy of a wrong source is not independent corroboration |
| F10 | — *Truth Discovery of Multi-Source Text Data* | IEICE Trans. Inf. Syst. 2019 | DOI `10.1587/TRANSINF.2018EDL8267` | Truth discovery for **text** data specifically | Text truth discovery needs textual (not numeric) source-reliability modelling |
| F11 | — *An Unsupervised Approach of Truth Discovery From Multi-Sourced Text Data* | IEEE Access 2019 | DOI `10.1109/ACCESS.2019.2934469` | Unsupervised source-reliability estimation for text | Source reliability can be *estimated*, not assumed — the basis for a non-parametric contradiction gate |
| F12 | — *Scaling up truth discovery* | IEEE ICDE 2016 | DOI `10.1109/ICDE.2016.7498359` | Scalable truth-discovery algorithm | Classic scalability reference for the truth-discovery lineage |
| F13 | — *Truth Discovery from Multiple Dependent Sources* | IEEE Trans. Comput. Soc. Syst. 2026 | DOI `10.1109/TCSS.2026.3657429` | Truth discovery where sources are **dependent** | Current-year statement of the dependency problem in F9 |

### 1.3 Knowledge conflict in LLMs and RAG

| # | Paper | Venue / year | Verified ID | Contribution |
|---|---|---|---|---|
| K1 | Xu et al. — *Knowledge Conflicts for LLMs: A Survey* | EMNLP 2024 | DOI `10.18653/v1/2024.emnlp-main.486` | Canonical taxonomy: **context–memory**, **inter-context**, **intra-memory** conflict. The thesis's D4 (two retrieved chunks disagreeing) is *inter-context* |
| K2 | Longpre, Perisetla, Chen, Ramesh, DuBois & Singh — *Entity-Based Knowledge Conflicts in Question Answering* | EMNLP 2021 | DOI `10.18653/v1/2021.emnlp-main.565` | Formalises context–memory conflict; measures over-reliance on memorised information; mitigation improves **out-of-distribution generalisation by 4–7%**. *"practitioners [should] evaluate model tendency to hallucinate rather than read"* |
| K3 | Chen, Zhang & Choi — *Rich Knowledge Sources Bring Complex Knowledge Conflicts: Recalibrating Models to Reflect Conflicting Evidence* | EMNLP 2022 | DOI `10.18653/v1/2022.emnlp-main.146` | Simulates conflicts with up to **100** retrieved passages plus parametric knowledge; retrieval performance drives which source the model relies on |
| K4 | Tan, Sun, Yang, Wang, Cao & Cheng — *Blinded by Generated Contexts: How Language Models Merge Generated and Retrieved Contexts When Knowledge Conflicts?* | ACL 2024 | DOI `10.18653/v1/2024.acl-long.337` | Paired generated-vs-retrieved contexts with one correct answer; **GPT-4, GPT-3.5 and Llama-2 all bias toward the generated context even when it is wrong** |
| K5 | Pham, Ngo, Luu & Nguyen — *Who's Who: Large Language Models Meet Knowledge Conflicts in Practice* | Findings of EMNLP 2024 | DOI `10.18653/v1/2024.findings-emnlp.593` | Real-world rather than synthetic conflict instances |
| K6 | Marjanovic, Yu, Atanasova, Maistro, Lioma & Augenstein — *DYNAMICQA: Tracing Internal Knowledge Conflicts in Language Models* | Findings of EMNLP 2024 | DOI `10.18653/v1/2024.findings-emnlp.838` | Two conflict measures; facts with **temporal dynamics** (facts that change over time) and **disputable dynamic facts** (facts that differ by viewpoint) |
| K7 | Jin, Cao, Yuan, Chen, Xu, Li, Jiang, Liu & Zhao — *Cutting Off the Head Ends the Conflict: A Mechanism for Interpreting and Mitigating Knowledge Conflicts in Language Models* | Findings of ACL 2024 | DOI `10.18653/v1/2024.findings-acl.70` | Mechanistic (activation-level) account of conflict handling |
| K8 | Yuan, Yang, Wang, Liu, Zhao & Liu — *Discerning and Resolving Knowledge Conflicts through Adaptive Decoding with Contextual Information-Entropy Constraint* (COIECD) | Findings of ACL 2024 | DOI `10.18653/v1/2024.findings-acl.234` | **Detects whether a conflict actually occurs** before changing decoding — an explicit precedent for "gate first, then act" |
| K9 | Tighidet, Mogini, Ben younes, Mei, Gallinari & Piwowarski — *Context Copying Modulation: The Role of Entropy Neurons in Managing Parametric and Contextual Knowledge Conflicts* | Findings of EMNLP 2025 | DOI `10.18653/v1/2025.findings-emnlp.1116` | Identifies *entropy neurons* that switch the model between parametric and contextual modes |
| K10 | Huo, Li, Qin, Qu, Li, Li, Ma & Cheng — *Micro-Act: Mitigate Knowledge Conflict in Question Answering via Actionable Self-Reasoning* | ACL 2025 | DOI `10.18653/v1/2025.acl-long.909` | Self-reasoning as the mitigation action |
| K11 | Li, Guo, Gao, Chen, Zhao, Zhang, Liu, Wu, Yao & Wei — *LLMs Trust Humans More, That's a Problem! Unveiling and Mitigating the Authority Bias in RAG* | ACL 2025 | DOI `10.18653/v1/2025.acl-long.1400` | LLMs favour **user-supplied** knowledge over the database even when the user is wrong — a new bias that any industrial deployment must handle |
| K12 | Tong, Zhang, Liu, Fu, Song, Zhang, Zhang, Zhu, Yang, Zhang & Li — *Ask, Condition or Abstain: Reinforcement Learning for Missing-Premise Reasoning* | EMNLP 2026 | URL `aclanthology.org/2026.emnlp-main.1440/` (no DOI registered yet) | The three-way decision — answer / condition / abstain — trained by RL |

### 1.4 Conflict-aware RAG — the direct comparators (2025–2026)

| # | Paper | Venue / year | Verified ID | What it does | Numbers |
|---|---|---|---|---|---|
| R1 | Zhang, Xiang, Xiao, Wang, Li, Wang & Su — *FaithfulRAG: Fact-Level Conflict Modeling for Context-Faithful Retrieval-Augmented Generation* | ACL 2025 | DOI `10.18653/v1/2025.acl-long.1062` | Models discrepancies between **modes** of parametric and contextual knowledge at fact level; argues existing faithful-RAG methods achieve faithfulness by *suppressing* parametric knowledge, which damages context interpretation | — |
| R2 | Wang, Wan, Sun, Chen & Arik — *Astute RAG: Overcoming Imperfect Retrieval Augmentation and Knowledge Conflicts for LLMs* | ACL 2025 | DOI `10.18653/v1/2025.acl-long.1476` | Finds imperfect retrieval is *"inevitable, common, and harmful"*; identifies LLM-internal vs external knowledge conflict as the post-retrieval bottleneck; adaptively elicits essential information | — |
| R3 | Choi, Park, Lee & Lee — *Conflict-Aware Soft Prompting for Retrieval-Augmented Generation* (introduces **CARE**, Conflict-Aware REtrieval-Augmented Generation) | EMNLP 2025 | DOI `10.18653/v1/2025.emnlp-main.1371` | A **context assessor** encoding external context into memory embeddings, trained with grounded/adversarial soft prompting to discern unreliable context | **Average +5.0%** on QA and fact-checking benchmarks |
| R4 | *(merged into R3 — the CARE paper's canonical title is "Conflict-Aware Soft Prompting for Retrieval-Augented Generation"; the framework name CARE appears in its abstract. Cite once.)* | EMNLP 2025 | — | — | — |
| R5 | Yang, Liu, Li & Lei — *Large Language Models in Resolving Contextual Knowledge Conflicts* | EMNLP 2026 | DOI `10.18653/2026.emnlp-main.918` | **Taxonomy of six contextual-conflict types: factual, inferential, temporal, granularity, perspective, ambiguity**; dataset **ContextConflict** with **5,781** samples covering reasoning and summarisation, with explicit contradictions *and* implicit multi-step conflicts | *"current models still fall short"* across **nine** LLMs |
| R6 | Liu, Halfaker, Roth & Xia — *ConflictScore: Identifying and Measuring How Language Models Handle Conflicting Evidence* | EMNLP 2026 | DOI `10.18653/2026.emnlp-main.2589` | **Decomposes responses into atomic claims, labels each claim against each grounding document**, aggregates into **ConflictScore-Count** (proportion of conflicting claims) and **ConflictScore-Ratio** (balance of supporting vs contradicting evidence); introduces **ConflictBench** covering ambiguity, contradiction and divergent opinions | Metric detects overconfident claims across domains |
| R7 | Jin, Li, Song, Yang, Yang, Tian, Ma, Li & Zhang — *TRIAD: A Three-Axis Framework for Knowledge Conflict Resolution in RAG* | EMNLP 2026 | DOI `10.18653/2026.emnlp-main.1033` | Identifies three coupled failure axes: **question complexity**, **long misleading evidence**, **off-target parametric recall**; shows their *interaction* is harder than any single axis | Training-free; decomposes a question into sub-questions and calibrates evidence at sub-question level |
| R8 | Zhang, Shi, Chu, Wang, Chuai, Wang, Chen, Li, Yi & Li — *CoVer: Conflict-aware Claim Verification* | EMNLP 2026 | DOI `10.18653/2026.emnlp-main.829` | Three-stage pipeline — evidence schema normalisation, factual consensus, support verification; prioritises definitive evidence over noise | **88.4% accuracy on CONFACT-HumC**; dataset ContraNote: **33,686** posts (evidence-level) and **54,474** instances (aggregation-level) |
| R9 | Hacker & Bar — *Saying vs. Seeing: Evaluating LLM Conflict Awareness and Resolution Preference under Latent Claim-Evidence Disagreement* (CLECK) | EMNLP 2026 | DOI `10.18653/2026.emnlp-main.1727` | Counterfactual benchmark of **5,922** instances (balanced **2,669**-instance subset) probing *latent* conflicts that only emerge after multi-step derivation | Among instruction-tuned models, recovering both competing answers does **not** translate into recognising the conflict; when the conflict does surface, preference shifts by **34 percentage points** toward the derived evidence |
| R10 | Zhang, Lu, Chen, Zheng, Jiang, Zhu & Fan — *Sampling Less, Knowing More: Contradiction-aware Adaptive Spectral and Entropic UQ for LLMs* (CASE) | EMNLP 2026 | DOI `10.18653/2026.emnlp-main.1093` | Builds a **contradiction graph** over sampled responses; quantifies semantic disagreement by normalised spectral norms; token-level predictive entropy as a complementary signal | Adaptive sampling budget per query |
| R11 | — *Disentangling Reasoning Logic to Resolve Explicit Knowledge Conflicts* | ACL 2026 | DOI `10.18653/v1/2026.acl-long.1451` | Separates the reasoning-logic component of an explicit conflict |
| R12 | — *Debate-of-Thoughts: Resolving Knowledge Conflicts in LLMs Through Internal Deliberation* | ACL 2026 | DOI `10.18653/v1/2026.acl-long.1651` | Internal debate to resolve conflicts |
| R13 | — *CoRect: Context-Aware Logit Contrast for Hidden State Rectification to Resolve Knowledge Conflicts* | EMNLP 2026 | DOI `10.18653/2026.emnlp-main.539` | Hidden-state rectification via logit contrast |
| R14 | Schuster, Gautam & Markert — *Whose Facts Win? LLM Source Preferences under Knowledge Conflicts* | ACL 2026 | DOI `10.18653/v1/2026.acl-long.1357` | Controlled study of source credibility preferences using synthetic sources, across **13 open-weight LLMs** | Source *identity*, not just content, drives which side the model takes |
| R15 | — *Key Path Identification for Resolving Knowledge Conflicts via SAE-based Steering* | EMNLP 2026 | DOI `10.18653/2026.emnlp-main.857` | Sparse-autoencoder steering to locate conflict-resolution circuits |
| R16 | — *CODE: A Contradiction-Based Overthinking Attack Framework for Prolonging RAG* | EMNLP 2026 | DOI `10.18653/2026.emnlp-main.917` | Adversarial: injecting contradictions to make RAG loop — an **adversarial threat model** the thesis should acknowledge |
| R17 | Zheng, Zhou, Zheng, Peng, Guo, Wu, Niu, Wu & Huang — *CDConv: A Benchmark for Contradiction Detection in Chinese Conversations* | EMNLP 2022 | DOI `10.18653/v1/2022.emnlp-main.2` | Benchmark showing contradiction detection is domain- and language-specific |
| R18 | Makhervaks, Gillis & Radinsky — *Clinical Contradiction Detection* | EMNLP 2023 | DOI `10.18653/v1/2023.emnlp-main.80` | Contradiction detection in a high-stakes domain — the closest existing precedent for "industrial" contradiction detection |
| R19 | Li, Raheja & Kumar — *ContraDoc: Understanding Self-Contradictions in Documents with Large Language Models* | NAACL 2024 | DOI `10.18653/v1/2024.naacl-long.362` | First human-annotated dataset for **self-contradictions in long documents**, varying document length, contradiction type and appearance scope | GPT-3.5, GPT-4, PaLM2, LLaMA-v2 evaluated: **GPT-4 is best and can outperform humans, yet remains unreliable** on self-contradictions needing nuance and context |
| R20 | Chen, Lyu, Liu, Zhang, Lv & Xu — *Think Wider, Detect Sharper: Reinforced Reference Coverage for Document-Level Self-Contradiction Detection* (DSCD) | EMNLP 2025 | DOI `10.18653/v1/2025.emnlp-main.67` | Shows CoT prompting gives only marginal gains on DSCD and is **inconsistent across repeated responses** because reasoning chains miss contradictory sentences; fixes this with SFT + RL and a reference-coverage reward | — |

### 1.5 Confidence, gating and abstention (the RO1 dependency of D4)

| # | Paper | Venue / year | Verified ID | Contribution |
|---|---|---|---|---|
| C1 | Xin, Tang, Yu & Lin — *The Art of Abstention: Selective Prediction and Error Regularization for NLP* | ACL 2021 | DOI `10.18653/v1/2021.acl-long.84` | Selective prediction for NLP: abstain on low-confidence inputs; compares confidence estimators; proposes an error-regularisation trick that improves confidence estimation at low compute cost |
| C2 | Gu & Hopkins — *On the Evaluation of Neural Selective Prediction Methods for NLP* | ACL 2023 | DOI `10.18653/v1/2023.acl-long.437` | Survey + empirical comparison of neural selective classification; introduces **refinement**, a *calibrated* metric for evaluating confidence functions |
| C3 | Chen, Yuan, Cui, Liu & Ji — *A Close Look into the Calibration of Pre-trained Language Models* | ACL 2023 | DOI `10.18653/v1/2023.acl-long.75` | Six controlled variables (dataset difficulty, training samples, steps, tunable parameters, model scale, pretraining) change PLM calibration during training; existing calibration methods are only partly effective |
| C4 | Tian, Mitchell, Zhou, Sharma, Rafailov, Yao, Finn & Manning — *Just Ask for Calibration: Strategies for Eliciting Calibrated Confidence Scores from LLMs Fine-Tuned with Human Feedback* | EMNLP 2023 | DOI `10.18653/v1/2023.emnlp-main.330` | Prompting for calibrated confidence from RLHF models |
| C5 | Zhang, Qiu, Guo, Deng, Zhang, Zhang, Zhou, Wang & Fu — *Enhancing Uncertainty-Based Hallucination Detection with Stronger Focus* | EMNLP 2023 | DOI `10.18653/v1/2023.emnlp-main.58` | Reference-free, uncertainty-based hallucination detection that concentrates on informative keywords |
| C6 | Shi, Zhang, Wang, Xie, Choi, Zhang, et al. — *Trusting Your Evidence: Hallucinate Less with Context-aware Decoding* (CAD) | ICLR 2023 | arXiv `2305.14739` | Amplitudes the contribution of the context versus the parametric prior — a *principled* way to weight retrieved evidence |
| C7 | Yan, Gu, Zhu & Ling — *Corrective Retrieval Augmented Generation* (CRAG) | 2024 | arXiv `2401.15884` | A retrieval **evaluator** with a confidence degree triggers refine/web-search/decompose corrective actions; shows behaviour when retrieval goes wrong |
| C8 | Manakul, Liusie & Gales — *SelfCheckGPT: Zero-Resource Black-Box Hallucination Detection for Generative Large Language Models* | EMNLP 2023 | DOI `10.18653/v1/2023.emnlp-main.557` | Sampling-based consistency check for hallucination — the practical alternative to a trained detector |
| C9 | Li, Cheng, Zhao, Nie & Wen — *HaluEval: A Large-Scale Hallucination Evaluation Benchmark for Large Language Models* | EMNLP 2023 | DOI `10.18653/v1/2023.emnlp-main.397` | Standard hallucination benchmark with tasks for QA, dialogue, summarisation |
| C10 | Liu, Zhang, Brockett, Mao, Sui, Chen & Dolan — *A Token-level Reference-free Hallucination Detection Benchmark for Free-form Text Generation* (introduces the **FActScore** method) | ACL 2022 | DOI `10.18653/v1/2022.acl-long.464` | Decomposes a long answer into atomic facts and verifies each against Wikipedia — the canonical per-claim decomposition method |
| C10b | Min, Krishna, Lyu, Lewis, Yih, Koh, Iyyer, Zettlemoyer & Hajishirzi — *FActScore: Fine-grained Atomic Evaluation of Factual Precision in Long Form Text Generation* | EMNLP 2023 | DOI `10.18653/v1/2023.emnlp-main.741` | The full FActScore system (atomic decomposition + NLI verifier + aggregation) — **cite alongside C10**; the two papers are distinct and often conflated |
| C11 | Niu, Wu, Zhu, Xu, Shum, Zhong, Song & Zhang — *RAGTruth: A Hallucination Corpus for Developing Trustworthy Retrieval-Augmented Language Models* | ACL 2024 | DOI `10.18653/v1/2024.acl-long.585` (arXiv `2401.00396`) | **~18,000** RAG responses, manually annotated at case *and word* level with hallucination intensity; benchmarks several hallucination-detection methods |
| C12 | Saad-Falcon, Khattab, Potts & Zaharia — *ARES: An Automated Evaluation Framework for Retrieval-Augmented Generation Systems* | NAACL 2024 | arXiv `2311.09476` | Lightweight LM judges for context relevance, answer faithfulness, answer relevance, using prediction-powered inference with a few hundred human annotations; judges survive domain shift |
| C13 | Chen, Lin, Han & Sun — *Benchmarking Large Language Models in Retrieval-Augmented Generation* (RGB) | AAAI 2024 | arXiv `2309.01431` | Standard RGB benchmark: noise robustness, negative rejection, information integration, counterfactual robustness |
| C14 | Gao, Yen, Yu & Chen — *Enabling Large Language Models to Generate Text with Citations* (ALCE) | EMNLP 2023 | DOI `10.18653/v1/2023.emnlp-main.398` | NLI-based citation recall/precision — the standard citation-quality metric family |
| C15 | Edge, Trinh, Cheng, Bradley, Chao, Mody, Truitt, Metropolitansky, Ness, Larson et al. — *From Local to Global: A Graph RAG Approach to Query-Focused Summarization* | 2024 | arXiv `2404.16130` | GraphRAG: community summaries for corpus-level questions — the alternative the thesis positions against |
| C16 | Wei, Chen & Meng — *InstructRAG: Instructing Retrieval-Augmented Generation via Self-Synthesized Rationales* | ICLR 2025 | arXiv `2406.13629` | Rationale-based denoising of noisy retrieved context — a *prompt-level* alternative to a code-level gate |
| C17 | Li, Cao, Pan, Ma & Sun — *Towards Verifiable Generation: A Benchmark for Knowledge-aware Language Model Attribution* | Findings of ACL 2024 | DOI `10.18653/v1/2024.findings-acl.28` | Attribution benchmark for verifiable generation |
| C18 | Magomere, La Malfa, Tonneau, Kazemi & Hale — *When Claims Evolve: Evaluating and Enhancing the Robustness of Embedding Models Against Misinformation Edits* | Findings of ACL 2025 | DOI `10.18653/v1/2025.findings-acl.1150` | Embedding models degrade as claims are edited — a retrieval-side instability the thesis's versioning story must handle |
| C19 | Cao & Wang — *Verifiable Generation with Subsentence-Level Fine-Grained Citations* (SCiFi) | Findings of ACL 2024 | DOI `10.18653/v1/2024.findings-acl.920` | **10K** Wikipedia paragraphs with **subsentence-level** citations — the closest published analogue to the thesis's per-claim confidence tag |
| C20 | Jiang, Zhang, Weir, Ebner, Wanner, Sanders, Khashabi, Liu & Van Durme — *Core: Robust Factual Precision with Informative Sub-Claim Identification* | Findings of ACL 2025 | DOI `10.18653/v1/2025.findings-acl.1018` | Selects *informative* sub-claims for verification rather than all atomic facts — a direct methodological precedent for the thesis's per-claim tagging granularity decision |
| C21 | Kargupta, Tian & Han — *Beyond True or False: Retrieval-Augmented Hierarchical Analysis of Nuanced Claims* (ClaimSpect) | ACL 2025 | DOI `10.18653/v1/2025.acl-long.1434` | Decomposes a nuanced claim into aspects/sub-aspects and validates each — the precedent for a *non-binary* claim label set in industrial text |
| C22 | Kamoi, Goyal, Rodriguez, Durrett et al. — *WiCE: Real-World Entailment for Claims in Wikipedia* | EMNLP 2023 | DOI `10.18653/v1/2023.emnlp-main.470` | Sub-sentence claim entailment with a minimal supporting-evidence set; shows entailment models underperform under domain shift |
| C23 | Chiang & Lee — *Merging Facts, Crafting Fallacies: Evaluating the Contradictory Nature of Aggregated Factual Claims in Long-Form Generations* | Findings of ACL 2024 | DOI `10.18653/v1/2024.findings-acl.160` | Correct claims can aggregate into a false claim through **entity ambiguity**; FActScore and citation metrics both fail on such cases |

---

## 2. Teaching notes — NLI and contradiction detection for a reader who knows none of this

### 2.1 What an NLI model actually does

Natural Language Inference reframes "do these two passages agree?" as a **three-way classification of a
sentence pair**. The input is a *premise* (the longer, trusted text) and a *hypothesis* (the shorter
proposition being tested). The output is one of three labels:

| Label | Plain meaning | Example (premise → hypothesis) |
|---|---|---|
| **Entailment** | If the premise is true, the hypothesis must be true | "Safety stock for SKU A is 187 units." → "SKU A's safety stock is 187 units." |
| **Contradiction** | The two cannot both be true | "Safety stock for SKU A is 187 units." → "SKU A's safety stock is 95 units." |
| **Neutral** | Both could be true, but the premise does not settle it | "Safety stock for SKU A is 187 units." → "SKU A's safety stock is reviewed quarterly." |

The crucial point for a practitioner: **"neutral" is the most common class in industrial text.** Two
passages that are both perfectly sensible and both true will usually be *neutral* with respect to each
other, because they talk about different things. A contradiction classifier that is asked to fire on
"these two chunks disagree" will be handed thousands of *neutral* pairs, and every false alarm costs
the same as a real detection.

A modern NLI model is a fine-tuned transformer (DeBERTa, RoBERTa, or an instruction-tuned LLM) that
outputs a three-way distribution. Two engineering facts follow:

1. **The label is a probability, not a fact.** A model that outputs `contradiction: 0.51` is not
   "confident"; on the hard subsets the model's own probabilities are poorly calibrated (C3).
2. **The model was trained on a specific distribution.** Models trained on SNLI/MultiNLI see
   everyday English; SciNLI (N12) and MSciNLI (N13) exist precisely because scientific and technical
   text breaks them — an XLNet trained on general NLI reaches **78% Macro F1 on SciNLI**, and a
   prompt-tuned LLM reaches only **51.77% on MSciNLI**. An industrial corpus — ISO standards,
   OEM manuals, calibration certificates — is *harder still*.

### 2.2 Why a naive NLI contradiction detector produces false positives

There are four independent failure modes, and the thesis's "joint NLI + topical gate" is a response to
the first three.

**(a) The topical failure — the two passages are about different things.** A supply-chain corpus will
contain a safety-stock rule for Plant 1, a safety-stock rule for Plant 2, and a safety-stock rule for
a different SKU family. A contradiction classifier sees "187 units" vs "95 units" and fires. But the
two sentences are about *different subjects*, so they are **neutral**, not contradictory. The subject
is the discriminator, and an NLI model has to *infer* it. This is exactly the failure the topical
gate removes.

**(b) The granularity failure — the two passages are true at different levels of detail.** A policy
document says "reorder point is 187 units"; a plant memo says "reorder point for the Jiangsu line is
95 units". Neither contradicts the other; the memo is *more specific*. The published literature
confirms this is a real, named category: the six-type contextual-conflict taxonomy of R5
(EMNLP 2026) lists **granularity** and **perspective** alongside factual, inferential, temporal and
ambiguity conflicts, and reports that current models *"still fall short"* on all of them. Two of those
six types are *not* logical contradictions at all.

**(c) The perspective failure — the two passages record different viewpoints.** DYNAMICQA (K6)
documents "disputable dynamic facts, which can change depending on the viewpoint". The 2025 paper on
nuanced claims (F7) makes the same case for industrial-scale claims: many cannot be labelled
true/false at all, only decomposed into aspects.

**(d) The artefact failure — the model is not reading the premise.** N5 showed that a classifier
trained on the hypothesis *alone* reaches **67% on SNLI** and **53% on MultiNLI**. Models learn
dataset regularities ("negation in the hypothesis ⇒ contradiction") rather than the semantic relation
between premise and hypothesis. N7 adds that negation specifically is under-represented and that
SOTA transformers fail when negation becomes decisive — and industrial text is full of
"except where...", "not exceeding...", "unless superseded by...". N6 shows how to train the bias out
(ensemble adversarial training), but the takeaway for the thesis is that **the NLI leg of the gate must
be validated on industrial text, not assumed from general-domain NLI results.**

### 2.3 What a topical gate is and why it works

A *topical gate* is a second, cheap classifier that asks a **different question** from the NLI model.
Instead of "do these two passages contradict each other?", it asks **"are these two passages about the
same thing?"**

In practice it is a similarity or entity-overlap test over the two chunks:

- **Entity overlap.** Extract equipment IDs, SKU codes, plant names, line IDs, standard numbers
  (`ISO 9001`, `GS1-128`, `Incoterms 2020`) and require that the conflicting pair shares the
  *subject* entity. "187 units for SKU A-104" and "95 units for SKU A-207" fail the gate; "187
  units for SKU A-104" (Rev 3) and "95 units for SKU A-104" (Rev 4) pass it.
- **Embedding or lexical similarity.** A cosine similarity above a threshold on the two chunk
  embeddings, with the threshold *calibrated on the industrial corpus*, not copied from a generic
  dataset.
- **Category routing.** Because the thesis already routes each query to one of twelve industrial
  categories (Industrial Engineering 9, Machine Learning 3), the topical gate can be restricted
  within-category — a strong, cheap prior that general-purpose RAG does not have.

The two gates compose as a **conjunction**: *contradiction* **AND** *same subject* ⇒ flag. Because
the two errors are largely independent (a topically-irrelevant pair is usually neutral to the NLI
model; a same-subject non-conflict is usually neutral too), the conjunction has a much better
precision than either leg alone. This is the same logical structure as R8's three-stage pipeline
(evidence schema normalisation → consensus → support verification) and R6's two-dimensional
ConflictScore (count of conflicting claims × ratio of supporting to contradicting evidence).

### 2.4 Why this is not the same as "context-memory conflict"

A great deal of the conflict literature is about a **different** conflict, and mixing them up is the
most common error in write-ups of this area.

| | **Context–memory conflict** | **Inter-context conflict (the thesis's D4)** |
|---|---|---|
| Where the clash is | Retrieved passage vs the model's own trained weights | Retrieved passage vs *another retrieved passage* |
| Who resolves it | The decoding strategy (CAD, COIECD, CARE, Astute RAG) | The *retrieval/verification layer* (the thesis's gate) |
| Typical fix | Re-weight context vs prior at decoding time | Detect, then **surface** both to the practitioner |
| Canonical refs | K1, K2, K6, R1, R2, R3 | K3, R5, R9, R19, R20, R6 |

The thesis's D4 is squarely the right-hand column. This matters for the literature review: it means
Self-RAG (reflection tokens), CRAG (retrieval evaluator), and CAD are *adjacent* baselines, not
the same mechanism, and the report's claim that "the gate lives outside the LM loop, non-bypassable"
is a genuine architectural distinction rather than a novelty claim in name only.

### 2.5 What the practitioner actually sees — and why "surfacing" beats "resolving"

Every conflict-aware RAG paper in §1.4 *resolves* the conflict: the model picks a side. The thesis's
D4 *surfaces* it. That is a deliberate and defensible design choice, and the literature supports it:

- R19 (ContraDoc) found that even **GPT-4 — which can outperform humans on the task — remains
  unreliable** on self-contradictions that require nuance and context. If the strongest available
  resolver is unreliable, an automatic resolver is the wrong thing to put in front of a safety-stock
  decision.
- R9 (CLECK, 2026) found that instruction-tuned models *"default to the authoritative claim"* and that
  recognising a latent conflict at all is a distinct capability from answering it. Automatic
  resolution also destroys the information the practitioner needs.
- F9 (truth discovery with source relations) shows that a source may simply be *copying* another
  source. When two retrieved chunks agree, they may be one document, not two confirmations. When
  they disagree, the practitioner needs to know *which document is newer* — an information a
  resolving model would silently discard.
- K11 (Authority Bias) shows LLMs prefer the *user's* claim over the database even when the user is
  wrong. Any automatic tie-break inherits this bias.

So: an automatic resolver throws away the choice, and the practitioner is exactly the person who
should make it. Surfacing is the correct design for the industrial setting, and the literature is
what justifies it.

### 2.6 The confound: temporal supersession is not contradiction

This is the single most likely cause of an unforced error in an industrial corpus, and it is worth
stating explicitly in the paper. Industrial documentation is **versioned**: OEM manual Rev 3 says
187 units, Rev 4 says 95 units. Both are true *of their revision*. A contradiction detector that
ignores revision metadata will flag every superseded specification in the corpus.

Mitigations, in order of preference:
1. **Ingestion-time metadata.** Store the document revision, effective date and supersession chain
   with each chunk, and compare revisions before comparing content.
2. **D4 check order.** Test "is this the same subject *at the same revision*?" before testing
   "do the statements differ?" — i.e. fold the revision check into the topical gate.
3. **Report the revision alongside the flag.** If the conflict is a supersession, say so.

K6 (DYNAMICQA) formalises the temporal axis of exactly this problem.

### 2.7 How the per-claim confidence tags (D5) interact with D4

D4 decides *whether to flag*; D5 decides *how to label each claim in the answer*. The two share a
mechanism, which is an efficiency argument: if a claim is already decomposed and already scored
against each source chunk (as in F10's FActScore and R6's ConflictScore), then the contradiction
check on that claim is nearly free.

The literature also warns about a specific failure of this aggregation, which F5 demonstrates
empirically: **factually correct claims can aggregate into a false claim.** F5 shows that Llama-chat
generates paragraphs containing verifiable facts that combine into a non-factual paragraph *because
of entity ambiguity*, and that **both FActScore and citation-based metrics fail on such cases**. The
thesis's D5 three-band tagging (grounded / inferred / uncertain) should therefore be defined so that
*entity ambiguity* forces a downgrade, and the paper should report F5's failure mode as a known
limitation rather than discovering it during defence.

---

## 3. Threshold reality-check: are the 98% → 16% false-positive numbers defensible?

The thesis's own report claims:

- NLI-only contradiction detection produces a **98% false-positive rate**
- the joint NLI + topical gate reduces this to **16%**

**These numbers need careful, explicit base-rate accounting before they go in a paper.** The problem
is that "false-positive rate" is ambiguous, and the two candidate definitions differ by orders of
magnitude. Here is the arithmetic under the published NLI accuracy figures.

### 3.1 The two definitions

- **FPR (false-positive rate)** = P(flag | no real contradiction). This is a property of the
  *detector* and is independent of the corpus mix. A detector with 78% specificity has FPR = 22%.
- **1 − Precision** = P(flag | flagged) is **not** a real contradiction. This is a property of the
  detector *and the corpus*, and it is what "98% of flags are wrong" actually means.

If the report means "98% of the time we raise a flag, it is wrong", that is a **precision** claim.
If it means "98% of genuinely consistent pairs are wrongly flagged", that is an **FPR** claim of 98%,
which would require a detector far worse than any published NLI model (98% FPR ⇒ 2% specificity).

### 3.2 Precision under published accuracy, given a base rate

Take the published scientific-text NLI performance as the best available proxy for an industrial
corpus: **Macro F1 ≈ 78%** (N12, SciNLI) and **LLM Macro F1 ≈ 51.77%** (N13, MSciNLI). Suppose the
gate's two legs behave roughly as: sensitivity to true contradictions ≈ 0.80, specificity ≈ 0.78.
Precision = TP / (TP + FP) with TP = 0.80·π and FP = 0.22·(1−π) for base rate π:

| Base rate π of true contradictions among compared pairs | TP | FP | **1 − Precision** | FPR |
|---|---|---|---|---|
| 30% (contradiction-heavy benchmark) | 0.240 | 0.154 | **39%** | 22% |
| 10% (realistic mixed set) | 0.080 | 0.198 | **71%** | 22% |
| 5% (typical top-k chunk set) | 0.040 | 0.209 | **84%** | 22% |
| 1% (sparse real conflicts) | 0.008 | 0.218 | **96.5%** | 22% |

**Conclusion: a 98% false-positive *share* is entirely plausible and in fact conservative** for an
NLI-only gate on an industrial corpus — it is what you get automatically whenever the base rate of
true contradictions is low and the detector is roughly at published accuracy. It is not an
extraordinary claim, but it *is* a base-rate claim, and it must be reported with the base rate stated.

### 3.3 Does the topical gate get you to 16%?

If the topical gate removes fraction **φ** of the false positives while retaining fraction **ρ** of the
true positives, then:

- FP' = 0.22·(1−π)·(1−φ)
- TP' = 0.80·π·ρ
- 1 − Precision' = FP' / (FP' + TP')

For π = 5% and ρ = 0.9:

| φ (share of FPs removed) | 1 − Precision' |
|---|---|
| 0.50 | 73% |
| 0.80 | 53% |
| 0.90 | 39% |
| **0.99** | **16%** |

**A 16% false-positive share requires the topical gate to remove ~99% of false positives while
keeping 90% of true positives.** That is a strong claim and it must be *earned by measurement*, not
assumed. Two possibilities:

1. **The gate really is that effective** — plausible if the industrial corpus is well-entity-indexed
   (SKU codes, plant IDs, standard numbers) so that a subject-mismatch filter is nearly perfect at
   rejecting cross-subject pairs. This is exactly the case where an entity-overlap gate beats an
   embedding-similarity gate, and it is a *defensible, domain-specific argument*.
2. **The reported number is FPR, not 1 − Precision** — i.e. the gate reduces the *false-positive rate*
   from 98% to 16% (specificity 2% → 84%). Under this reading the claim is about the detector, not
   the corpus mix, and the arithmetic above does not apply.

### 3.4 What to do about this before submission

1. **Report both numbers, with the base rate.** Precision, recall, F1, and **the prevalence of true
   contradictions in the evaluation set**. A contradiction-detection result without prevalence is not
   interpretable, and any reviewer in this area will ask for it.
2. **State the definition explicitly** ("98% of raised flags were false positives" vs "the detector
   mis-flagged 98% of consistent pairs").
3. **Add the trivial-but-necessary baseline: always-not-flag.** If the prevalence is 5%, a gate that
   never fires has 95% precision and 100% recall-of-nothing. Report the always-flag and
   random-flag baselines; they are what makes a 16% FP share impressive or not.
4. **Report the gate's own operating point.** Sensitivity/specificity of the topical gate at the
   chosen threshold, swept, not a single point.
5. **Prefer the "annotated error taxonomy" presentation.** A table of the *types* of false positive
   (granularity, perspective, temporal supersession, cross-subject, entity ambiguity) with counts
   is far more convincing than a single percentage — and it directly uses R5's six-type taxonomy, so
   it positions the thesis against published work rather than inventing a taxonomy.

---

## 4. What this thesis can claim (defensibility)

**Defensible as stated:**

1. *Industrial decision support is a distinct deployment context for evidence-grounded RAG.* The
   published conflict literature covers dialogue (R17), clinical text (R18), social-media claims
   (R8), scientific claims (F8) and long documents (R19) — but **not** industrial engineering
   documentation (SOPs, FMEA, calibration records, OEM manuals). The thesis's twelve-category
   industrial taxonomy is a genuine gap. Note R18 (Clinical Contradiction Detection) is the closest
   precedent and should be cited as such — it shows high-stakes-domain contradiction detection is
   feasible, and the thesis can say "clinical text showed X; we show industrial text shows Y".
2. *Per-claim, per-source conflict labelling with an explicit aggregation metric.* R6 (ConflictScore,
   EMNLP 2026) is the closest work and **must be cited**. The thesis's defensible delta is:
   (a) the domain, (b) the **joint NLI + topical gate** operating on *retrieved chunks* rather than
   on answer-claims × documents, (c) the topical gate as a named, ablated component, (d) the
   code-level non-bypassable confidence gate that *refuses to answer* rather than only labelling,
   and (e) the practitioner-facing surfacing decision (surfacing vs resolving — see §2.5, supported
   by R19's unreliability finding and R9's default-to-authoritative finding).
3. *That surfacing beats resolving in the industrial setting.* This is a **design argument backed by
   published unreliability**, and it is stronger than a novelty claim. R19: GPT-4 beats humans but is
   unreliable. R9: models default to the authoritative claim and shift 34 points only when the
   conflict is noticed. K11: authority bias. F9: source dependence. Together these justify
   "hand the conflict to the practitioner" far better than they justify a new automatic resolver.
4. *That the false-positive problem is real and quantified.* R19 (unreliable on nuanced
   self-contradictions), R5 (six conflict types, models fall short), N12/N13 (78% and 51.77% Macro F1
   on scientific text), N5 (67%/53% hypothesis-only accuracy), N7 (negation failure), R20 (CoT
   inconsistent across repeated responses on document-level self-contradiction) — this is a
   well-evidenced problem, and the thesis is on solid ground asserting it.
5. *That the six-type conflict taxonomy is the right frame.* R5 (EMNLP 2026) supplies
   factual / inferential / temporal / granularity / perspective / ambiguity. The thesis can adopt
   this taxonomy, show which types the industrial corpus exhibits, and demonstrate that a
   binary contradiction/not gate is the wrong instrument because two of the six types are not
   contradictions at all.

**Claims to soften or drop:**

1. *"The gate reduces false positives from 98% to 16%"* — restate per §3, with prevalence and both
   metrics.
2. *"No existing work does contradiction surfacing"* — **false**. R6, R8, R19, R20 all do
   conflict detection; R5 does contextual conflict resolution. The thesis must claim *industrial
   evidence-grounded surfacing with a non-bypassable gate and per-claim confidence*, not first-ever
   conflict detection.
3. *"The three-band per-claim confidence tag is new"* — F10 (FActScore) decomposes into atomic facts;
   F3 (WiCE) does sub-sentence entailment; F4 (SCiFi) does subsentence-level citations; R6 does
   per-claim × per-document labels. The *three-band* label set as applied to industrial claims is
   plausibly new; atomic-claim decomposition is not.

---

## 5. Gaps, risks and required actions

| Risk | Severity | Action |
|---|---|---|
| **R6 (ConflictScore, EMNLP 2026) is a close prior-art collision** — atomic claims × documents × labels, aggregated into two metrics | **High** | Cite explicitly in the literature review, state the delta (§4.2), and add a comparison row in the framework-comparison table. If the thesis's D5 is only "label each claim and aggregate", it is *not* novel |
| **"98% → 16% FP" is not interpretable without prevalence** | **High** | Restate as in §3.4: report precision/recall/F1 **plus prevalence**, plus always-flag and never-flag baselines |
| **Temporal supersession will dominate the error profile** in a versioned industrial corpus | **High** | Store revision/effective-date metadata at ingestion; test D4 *after* the revision check; report the supersession share of all flags |
| **NLI models underperform on technical text** (51.77% LLM Macro F1 on MSciNLI) | **High** | Either fine-tune/validate the NLI leg on the industrial corpus and report that validation, or state the NLI leg's measured accuracy on the corpus as a first-class result — do not import a general-domain number |
| **Granularity and perspective conflicts are not contradictions** | Medium | Adopt R5's six-type taxonomy; report flag counts per type; consider a non-binary "divergence" band alongside "contradiction" |
| **Adversarial contradiction injection** (R16) can degrade the system | Medium | Acknowledge as a threat model in Limitations; a code-level gate is *more* exposed to this than a decoding-level fix, since the gate can be fed contradictory chunks deliberately |
| **No published industrial contradiction-detection benchmark** | Medium | This is an opportunity, not just a gap: the thesis's own benchmark (RO4/benchmark objective) can be positioned as the first industrial one — but then the benchmark, not the gate, must be the contribution |
| **Unverified citations** (§7) | Low | Resolve before submission |

---

## 6. Recommended citation set for the D4 section of the thesis

If only ~12 references are needed, use these — all verified:

1. K1 — Xu et al., Knowledge Conflicts for LLMs: A Survey (EMNLP 2024) — the taxonomy and vocabulary.
2. R5 — Large Language Models in Resolving Contextual Knowledge Conflicts (EMNLP 2026) — the six-type
   taxonomy and ContextConflict; **the single most important citation for justifying the topical gate**.
3. R6 — ConflictScore (EMNLP 2026) — per-claim × per-document conflict labelling; **the closest prior
   art; must be positioned against**.
4. R19 — ContraDoc (NAACL 2024) — long-document self-contradiction; humans vs GPT-4 unreliability.
5. R20 — DSCD (EMNLP 2025) — CoT inconsistency on document-level contradiction detection.
6. R9 — CLECK (EMNLP 2026) — models default to the authoritative claim; 34-point preference shift.
7. K11 — Authority Bias (ACL 2025) — LLMs favour user knowledge over the database.
8. N12 — SciNLI (ACL 2022) — 78.18% Macro F1 ceiling on scientific text.
9. N13 — MSciNLI (NAACL 2024) — 51.77% LLM Macro F1; domain shift hurts.
10. N5 — Annotation Artifacts (NAACL 2018) — 67%/53% hypothesis-only accuracy.
11. N9 — DocNLI (Findings of ACL 2021) — document context changes the entailment label.
12. F5 — Merging Facts, Crafting Fallacies (Findings of ACL 2024) — correct facts can aggregate into a
    false claim; FActScore and citation metrics fail on entity ambiguity.

Supporting: K2, K3, K6, K8, K9, K10, R1, R2, R3, R7, R8, R10, R11, R14, R17, R18, F2, F3, F4, F7, F9,
F10, F11, N1–N4, N6–N8, N10–N14, C1–C18, and for the per-claim layer specifically C19 (subsentence
citations), C20 (Core — informative sub-claim selection) and C23 (correct facts aggregating into a
false claim).

---

## 7. UNVERIFIED — flagged, not asserted

These are on the scope list and are almost certainly real, but **their metadata could not be confirmed
from any source reachable in this environment**. Resolve before the citation goes into the paper.

| Paper | Status | Notes |
|---|---|---|
| **ConTRoL: A Natural Language Inference Dataset for Reasoning about Contradictions** (Liang et al.) | **UNVERIFIED** | Not present in the ACL Anthology at EMNLP 2018–2023, NAACL 2018–2023, or ACL 2018–2024 (verified by scanning those event index pages for the exact token `ConTRoL`). arXiv search was HTTP 429 throughout; Semantic Scholar is IP-rate-limited; OpenAlex daily quota exhausted; DBLP behind an Anubis proof-of-work wall and flaky when reachable. **Do not cite without checking the arXiv listing directly.** |
| **CREPE: A Contrastive Framework for Fact Verification and Reasoning over Claims** (Gao et al.) | **UNVERIFIED** | Same checks: absent from ACL Anthology event pages. Note there is a *verified* different paper with the same acronym — CREPE (false presuppositions), ACL 2023, DOI `10.18653/v1/2023.acl-long.583` — and a third (chest X-ray, EMNLP 2025, `10.18653/v1/2025.emnlp-main.1102`). **Disambiguate carefully** |
| **TruthFinder: A Multi-Source Truth Discovery Framework** (Yin, Lagaraine, Wang, Li; ICDE 2017) | **UNVERIFIED** | The DOI `10.1109/ICDE.2017.8009757` was tried and returned **404** — do not use it. The truth-discovery lineage *is* well covered by verified substitutes: F9 (`10.1109/compcomm.2018.8780660`), F10 (`10.1587/TRANSINF.2018EDL8267`), F11 (`10.1109/ACCESS.2019.2934469`), F12 (`10.1109/ICDE.2016.7498359`), F13 (`10.1109/TCSS.2026.3657429`) |
| **ConTRoL / CREPE / TruthFinder exact venues, years and author lists** | UNVERIFIED | — |
| **MNLI dataset size** (433K premise–hypothesis pairs across 11 genres) | **PARTIALLY VERIFIED** | The paper (Williams, Nangia, Bowman; NAACL 2018; DOI `10.18653/v1/N18-1101`; pp. 1112–1122) and its record are verified; the "433K / 11 genres" figures come from memory of the paper and should be re-checked against the PDF before quoting |
| **ConTRoL and CREPE reported accuracy figures** | UNVERIFIED | Do not quote numbers from these two until the PDFs are read |

---

## 8. Tooling built during this survey (reusable by the other research streams)

All scripts live in `scripts/` and are safe to reuse:

| Script | What it does | Why it exists |
|---|---|---|
| `scripts/verify_arxiv_ids.py` | Resolves **many** arXiv IDs in one API call via `id_list`, printing RESOLVED / NOT-FOUND per ID | The arXiv REST API is rate-limited to ~1 req/3 s; `id_list` collapses 20 lookups into 1 |
| `scripts/arxiv_search.py` | arXiv **HTML** search + `abs` page resolver (title, authors, abstract, comment, jref, DOI) | The JSON API returns 429; the HTML search page does not (though it is also throttled under load). `--ids` resolves known IDs reliably |
| `scripts/arxiv_batch.py` | Runs many arXiv queries into one JSON index | Bulk discovery |
| `scripts/acl_find.py` | Title-fragment search across ACL Anthology volume indexes; returns exact BibTeX records | **The workhorse.** ACL volume pages are static, unlimited, and give canonical DOIs. `--volumes` accepts a comma list |
| `scripts/acl_grep.py` | Fast title grep across every cached ACL volume | Sweeps for a topic in seconds |
| `scripts/acl_extract.py` | Full records (title, authors, **abstract**, venue) from cached volume pages | Abstracts are embedded in the volume HTML — no per-paper request needed |
| `scripts/crossref_resolve.py` | Title → Crossref metadata | For non-ACL venues (IEEE, Elsevier, Springer) |
| `scripts/resolve_titles.py` | Title → OpenAlex metadata | Unused for this stream: the IP's free daily OpenAlex budget is exhausted (resets 00:00 UTC) |
| `scripts/dblp_resolve.py` | Title → DBLP metadata | Unreliable here: DBLP is behind an Anubis proof-of-work wall; the Scrapling stealth browser *can* solve it, but `fetch()` inside `browser_evaluate` returns truncated JSON intermittently |

**Two API limits worth knowing before the next research stream:**
Semantic Scholar (`api.semanticscholar.org`) returns **429** for this IP on both plain HTTP and
through the Scrapling stealth client — it needs an API key. OpenAlex returns 429 with
*"Insufficient budget … resets at midnight UTC"*. **ACL Anthology and Crossref are the reliable
sources**; arXiv HTML works but is throttled.

**Volume indexes already cached** in `/tmp/acl_cache/` (28 volumes, 2020–2026, incl. the full
`2025.acl-long`, `2025.emnlp-main`, `2026.acl-long` and `2026.emnlp-main` proceedings) — re-running
`acl_grep.py` against them is instantaneous and free.
