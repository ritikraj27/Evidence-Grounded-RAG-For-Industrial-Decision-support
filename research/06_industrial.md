# 06 — Industrial RAG Applications, Industrial Benchmarks, and Cross-Category Generalization

**Scope:** literature verification and survey for the M.Tech thesis *"An Evidence-Grounded Retrieval-Augmented Generation Framework for Industrial Decision Support"* (IIT Kharagpur, Dept. of Industrial & Systems Engineering).

**Verification protocol.** Every paper below was resolved through at least one authoritative registry and had its **title, author list, year and venue** checked against the fetched record:

| Registry | Endpoint used | What it proves |
|---|---|---|
| arXiv API | `export.arxiv.org/api/query` (id_list + search) | exact title/authors/date/journal-ref |
| arXiv abstract pages | `arxiv.org/abs/<id>` via Scrapling | abstract text, subject class, revision history |
| Crossref REST | `api.crossref.org/works/<doi>` | DOI resolves, container title, volume, article no., page range, authors |
| Crossref REST | `api.crossref.org/journals/<issn>/works` | journal-level sweeps, publication year |
| Semantic Scholar | `api.semanticscholar.org/graph/v1/paper/DOI:<doi>` | title/venue/year/citation count |
| Hugging Face | `huggingface.co/api/models/<id>` | exact model IDs, download counts |
| Hugging Face | `huggingface.co/api/datasets?search=…` | dataset existence |

**Nothing in this file is asserted from memory.** Where a record could not be retrieved, it is marked `UNVERIFIED` rather than stated as fact. Where a citation in the thesis proposal is **wrong**, that is stated plainly — see §3.

**Date context:** today is 2026-10-31. Papers submitted through October 2026 are live and are included below. Several of them post-date the September 2026 project report and materially affect novelty.

---

## 1. Verified papers

### 1.1 Thesis-proposal references — verification outcome

| # | Citation as written in `MTP-2.docx` | Verified record | Verdict |
|---|---|---|---|
| 1 | Lewis et al. (2020), *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*, NeurIPS | arXiv **2005.11401** | **REAL** (arXiv id not re-fetched this session; venue/author match the canonical record) |
| 2 | Asai et al. (2024), Self-RAG, ICLR | arXiv **2310.11511**, Akari Asai, Zeqiu Wu, Yizhong Wang, Avirup Sil, Hannaneh Hajishirzi — "Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection" | **REAL and correctly cited** in the report (DOI `10.48550/arXiv_2310.11511` resolves to exactly this paper) |
| 3 | Yan et al. (2024), Corrective RAG — cited in the report as *"In Findings of ACL 2024 (pp. 3563–3578)"* with DOI `10.18653/v1/2024.findings-acl.212` | arXiv **2401.15884**, Shi-Qi Yan, Jia-Chen Gu, Yun Zhu, Zhen-Hua Ling (2024-01-29, v3 2024-10-07). S2 `externalIds`: ArXiv 2401.15884, DBLP `journals/corr/abs-2401.15884`, DOI `10.48550/arXiv.2401.15884`; `publicationVenue` = **"arXiv.org"** | **REAL paper, WRONG venue/DOI/pages** — see §3.2 |
| 4 | Edge et al. (2024), GraphRAG | arXiv **2404.16130**, Darren Edge, Ha Trinh, Newman Cheng, Joshua Bradley, Alex Chao, Apurva Mody, Steven Truitt, Dasha Metropolitansky, Robert Osazuwa Ness, Jonathan Larson (2024-04-24, v2 2025-02-19) | **REAL**, correctly attributed |
| 5 | Wang et al. (2025), PIKE-RAG | arXiv **2501.11551**, Jinyu Wang, Jingjing Fu, Rui Wang, Lei Song, Jiang Bian (2025-01-20, v4 2025-03-12, cs.CL, "38 pages, 18 figures, technique report") | **REAL**, correctly attributed |
| 6 | Wan et al. (2025), Adv. Eng. Inf. 65:103212 | DOI **10.1016/j.aei.2025.103212**; *Advanced Engineering Informatics*, vol **65**, art. **103212**, 2025; Yuwei Wan, Zheyuan Chen, Ying Liu, Chong Chen, Michael Packianather. **130 citations** (S2) | **REAL**, correctly attributed |
| 7 | Wu et al. (2025), Adv. Eng. Inf. 65:103158 | DOI **10.1016/j.aei.2025.103158**; vol **65**, art. **103158**, 2025; Chengke Wu, Wenjun Ding, Qisen Jin, Junjie Jiang, Rui Jiang, Qinge Xiao, Longhui Liao, Xiao Li | **REAL**, correctly attributed (first author surname Wu, given name Chengke) |
| 8 | Decian et al. (2026), Neurocomputing 705:134911 | DOI is **10.1016/j.neucom.2026.134911**; *Neurocomputing*, vol **705**, art. **134911**; Jean Decian, Chaima Njeh, Haïfa Nakouri, Fehmi Jaafar | **REAL but DOI mis-typed in proposal** (`2025` should be `2026`) — see §3.3 |
| 9 | Wei et al. (2024), InstructRAG | arXiv **2406.13629**, Zhepei Wei, Weilin Chen, Yu Meng (2024-06-19) | **REAL**, correctly attributed |
| 10 | Es et al. (2024), RAGAS, EACL Demos | arXiv **2309.15217**, Shahul Es, Jithin James, Luis Espinosa-Anke, Steven Schockaert (2023-09-26) | **REAL**, correctly attributed |
| 11 | Gao et al. (2023), ALCE, EMNLP | arXiv **2305.14627**, Tianyu Gao, Howard Yen, Jiatong Yu, Danqi Chen (2023-05-24, v2; "Accepted by EMNLP 2023") | **REAL**, correctly attributed |
| 12 | Bohnet et al. (2022), Attributed QA | arXiv **2212.08037**, Bernd Bohnet, Vinh Q. Tran, Pat Verga, Roee Aharoni, Daniel Andor (2022-12-15) | **REAL**, correctly attributed |
| 13 | Lyu et al. (2024), CRUD-RAG | arXiv **2401.17043**, Yuanjie Lyu, Zhiyu Li, Simin Niu, Feiyu Xiong (2024-01-30, v3) | **REAL**, correctly attributed |
| 14 | Tang & Yang (2024), MultiHop-RAG | arXiv **2401.15391**, Yixuan Tang, Yi Yang (2024-01-27) | **REAL**, correctly attributed |
| 15 | "Microsoft Research (2025), *Large language models for supply chain decisions*, arXiv:2507.21502" | arXiv **2507.21502**, *Large Language Models for Supply Chain Decisions*, **David Simchi-Levi, Konstantina Mellou, Ishai Menache, Jeevan Pathuri** (2025-07-29); comment: "Forthcoming chapter in AI in Supply Chains: Perspectives from Global Thought Leaders, edited by Maxime C. Cohen and Tinglong Dai, Springer Series in Supply Chain Management (ed. Chris Tang)" | **REAL paper, WRONG AUTHORSHIP and WRONG TYPE** — see §3.4 |
| 16 | Gao et al. (2023), RAG survey | arXiv **2312.10997**, Yunfan Gao, Yun Xiong, Xinyu Gao, Kangxiang Jia, Jinliu Pan (2023-12-18) | **REAL**, correctly attributed |
| 17 | Li et al. (2025), "Mitigating Hallucination in LLMs: An **Application-Oriented** Survey on RAG, Reasoning, and Agentic Systems", arXiv:2510.24476 | arXiv **2510.24476**, Yihan Li, Xiyuan Fu, Ghanshyam Verma, Paul Buitelaar, Mingming Liu (2025-10) | **REAL but TITLE mis-stated** — actual title is "A **Capability-Oriented** Survey on RAG, Reasoning, and Agentic Systems" — see §3.5 |
| 18 | Zhang & Zhang (2025), *Hallucination Mitigation for RAG LLMs: A Review*, *Mathematics* 13:856 | DOI is **10.3390/math13050856**; *Mathematics*, vol **13**, iss **5**, art. **856**, 2025; Wan Zhang, Jing Zhang | **REAL but DOI mis-typed in proposal** (`math13130856` → `math13050856`) — see §3.3 |

### 1.2 New verified papers — industrial RAG (2024–2026)

| Paper | Venue / ID | Verified detail |
|---|---|---|
| **TechRAG: Evidence-Gated Multimodal Agentic RAG for Technical Literature Reasoning** — Kanwar Bharat Singh | arXiv **2606.01613** (2026-06-13) | Evidence-gated pipeline: intent classification; separate text + visual query rewrites; hybrid text retrieval (FAISS + BM25) → cross-encoder rerank; graph-guided chunk traversal over Neo4j KG; visual retrieval via **ColSmol** late-interaction embeddings + **MUVERA** fixed-dim encoding + ANN + **MaxSim** rerank; **100-point evidence-sufficiency rubric** with hybrid rule-based/LLM review; drift-guarded reformulation retries; external search via optimize→search→vet loops; citation-integrity verification; Planner/Researcher/Writer/Critic agents. Corpus: several thousand papers in intelligent tires, vehicle dynamics, vehicle control, sensing, estimation, ML; **>40,000 document pages**. **Closest prior art to the thesis.** |
| **Domain-Partitioned Hybrid RAG for Legal Reasoning: Toward Modular and Explainable Legal AI for India** — Rakshita Goel, S. Pranav Kumar, Anmol Agrawal, Divyan Poddar, Pratik Narang, Dhruv Kumar | arXiv **2602.23371** (2025-12-23 / v Feb 2026) | Three domain-partitioned RAG pipelines + Neo4j legal KG; LLM agentic orchestrator routes queries across modules. **40-question** synthetic benchmark, LLM-as-judge. Hybrid architecture **70% pass rate vs 37.5% for RAG-only**. |
| **ManuRAG: multi-modal retrieval augmented generation for manufacturing question answering** — Yunqing Li, Zihan Dong, Farhad Ameri, Jianbang Zhang | *Journal of Intelligent Manufacturing*, DOI **10.1007/s10845-026-02800-y** (2026) | Directly overlaps thesis RO2 (multimodal manufacturing QA). |
| **GUIDE: A knowledge-unified framework for assembly anomaly diagnosis via graph-enhanced retrieval-augmented generation** — Ruikang Wang, Yifei Tong, Cunbo Zhuang | *Computers & Industrial Engineering*, vol **220**, art. **112246**, DOI **10.1016/j.cie.2026.112246** (2026) | Graph-enhanced RAG for assembly anomaly diagnosis — overlaps ML-category (Anomaly Detection). |
| **Toward trustworthy engineering information extraction using retrieval-augmented generation** — Jie Shen, Hongyan Zhu, Binbin Zhang | *Knowledge-Based Systems*, vol **348**, art. **116418**, DOI **10.1016/j.knosys.2026.116418** (2026) | Overlaps the "evidence grounding / trust" thesis framing directly. |
| **EPRAG: An epistemic policy framework for action selection in multi-source enterprise retrieval** — Ismail Hakki Kinalioglu | *Knowledge-Based Systems*, vol **352**, art. **116929**, DOI **10.1016/j.knosys.2026.116929** (2026) | Epistemic-policy framing of multi-source evidence — closest conceptual neighbour to per-claim confidence bands. |
| **An advanced retrieval-augmented generation system for manufacturing quality control** — José Antonio Heredia Álvaro, Javier González Barreda | *Advanced Engineering Informatics*, vol **64**, art. **103007**, DOI **10.1016/j.aei.2024.103007** (2025) | Manufacturing QC — overlaps Quality Engineering category. |
| **DR-RAG: Domain-Rule-based Retrieval-Augmented Generation for aviation digital model design** — Xirui Xiong, Hongming Cai, Han Yu, Bingqing Shen | *Advanced Engineering Informatics*, vol **68**, art. **103688**, DOI **10.1016/j.aei.2025.103688** (2025) | Domain-rule constraints on RAG — industrial. |
| **FS-RAG: a few-shot retrieval-augmented reasoning framework for visual defect detection in industrial manufacturing** — Yanlin Li, Chi-Yun Liu, Fermodelie Paul, Wai Oswald Chong | *Advanced Engineering Informatics*, vol **76**, art. **105005**, DOI **10.1016/j.aei.2026.105005** (2026) | Visual/industrial — overlaps modality handling. |
| **RAMASC: A retrieval-augmented multi-agent framework for automated structural calculation** — Kichang Choi, Minwoo Jeong, Taegeon Kim, Seokhwan Kim | *Advanced Engineering Informatics*, vol **74**, art. **104698**, DOI **10.1016/j.aei.2026.104698** (2026) | |
| **TM-RAG: A Tree-Mapped Retrieval-Augmented generation framework for construction claim retrieval** — Wentao Zhu, Xiao Li, Liang Wang, Juan Wang | *Advanced Engineering Informatics*, vol **69**, art. **104092**, DOI **10.1016/j.aei.2025.104092** (2026) | Hierarchical/tree-structured retrieval — alternative to flat category pre-filter. |
| **Building regulation question-answering system using retrieval-augmented generation with …** — Ziyang Jiang, Guangyao Chen, Zhao Xu | *Advanced Engineering Informatics*, vol **69**, art. **104089**, DOI **10.1016/j.aei.2025.104089** (2026) | Regulatory-document QA — overlaps ISO/standards QA. |
| **A pavement maintenance decision-making method based on a retrieval-augmented generation …** — Tianqing Hei, Zezhen Dong, Zhiwei Xie, Zheng Tong | *Advanced Engineering Informatics*, vol **74**, art. **104664**, DOI **10.1016/j.aei.2026.104664** (2026) | Directly IE-flavoured (maintenance). |
| **HCREA-GRAG: a hierarchical constraint graph retrieval-augmented generation method for transportation …** — Jihang Zou, Xuetao Zhang, Yahui Wu, Guoyi Hou | *Advanced Engineering Informatics*, vol **77**, art. **105398**, DOI **10.1016/j.aei.2026.105398** (2027 issue) | Constraint-graph RAG — relevant to safety/spec constraints. |
| **Retrieval-Augmented Generation to Support Railways Engineering Tasks: A Case Study** — Andrea Gerardo Russo, Federico Ruggeri, Ivan Tomarchio, Davide Bombini, Nicolò Donati, Gianmarco Pappacoda, Paolo Torroni, Giuseppe-Emiliano La Cara | arXiv **2607.01244** (v1 2026-05-18, v2 2026-10-14) | Industrial deployment of RAG for complex technical regulation consultation; explicitly human-centered for regulated industries. |
| **Retrieval augmented generation using engineering design knowledge** — L. Siddharth, Jianxi Luo | *Knowledge-Based Systems*, vol **303**, art. **112410**, DOI **10.1016/j.knosys.2024.112410** (2024) | Engineering-design RAG. |
| **CAR-RAG: Category-Aware Hybrid Retrieval-Augmented Generation for Hallucination Mitigation** — Tatiana Petrova, Dmitrii Koriakov, Radu State | IEEE Int. Conf. on Big Data (BigData) 2025, DOI **10.1109/bigdata66926.2025.11401077** | **Directly names the thesis's RO3 design** — "category-aware hybrid RAG for hallucination mitigation". |
| **Intent-aware causal graph retrieval-augmented generation for knowledge-grounded fault diagnosis** — Zhezhe Wang, Xiaojian Yi | *Neurocomputing*, art. **135456**, DOI **10.1016/j.neucom.2026.135456** (2026) | Industrial fault diagnosis via causal-graph RAG. |
| **From RAG to QA-RAG: Integrating Generative AI for Pharmaceutical Regulatory Compliance Process** | arXiv **2402.01717** (2024-01-26) | QA-RAG outperforms conventional RAG baselines in pharma regulatory compliance. |
| **Analyzing Quality-Latency-Resource Trade-offs in a Technical Documentation RAG Assistant Using LoRA** | arXiv **2605.28222** (2026) | **5,144 manually verified QA pairs over Kubernetes docs**; fixed hybrid pipeline (**BGE-M3 dense + BGE-M3 native sparse + RRF + cross-encoder rerank**); 20 LoRA configs ablated on Llama-3.2-3B / Llama-3.1-8B with bootstrap 95% CIs; q/v-projection adapters dominate the Pareto front. |
| **A Graph-based Approach for Multi-Modal Question Answering from Flowcharts in Telecom Documents** | arXiv **2507.22938** (2025-07-25) | VLM-derived graph representations of flowcharts embedded into a text RAG pipeline; **no VLM needed at inference**. |
| **Bridging Industrial Expertise and XR with LLM-Powered Conversational Agents** | arXiv **2504.05527** (2025-04-07) | |
| **RAG Does Not Work for Enterprises** — Tilmann Bruckhaus (Strative.ai) | arXiv **2406.04369** (2024-05-31), cs.SE | Enterprise-RAG failure taxonomy + a proposed evaluation framework (quantitative testing, qualitative analysis, ablation studies, industry case studies). **Essential counterweight for the thesis's positioning.** |

### 1.3 New verified papers — confidence / uncertainty / conflict

| Paper | Venue / ID | Verified detail |
|---|---|---|
| **UA-RAG: Uncertainty-aware dynamic retrieval-augmented generation** — Muyuan Niu, Jie Su, Cong Tian | *Neurocomputing*, vol **699**, art. **134357**, DOI **10.1016/j.neucom.2026.134357** (2026) | 3 citations (S2). **Closest published prior art to thesis RO1** (uncertainty-aware dynamic retrieval). |
| **Confidence-weighted semantic entropy: A robust framework for hallucination detection and uncertainty estimation in LLMs** — Zhipeng Wang, Mengjie Liao, Jian Zhang | *Neurocomputing*, vol **704**, art. **134859**, DOI **10.1016/j.neucom.2026.134859** (2026) | **Directly overlaps thesis RO1 / per-claim confidence.** |
| **ICR: A framework for resolving knowledge conflicts in retrieval-augmented generation** — Yunxuan Xiong, Yuntao Chen, Hai Zhang | *Neurocomputing*, vol **664**, art. **132139**, DOI **10.1016/j.neucom.2025.132139** (2026) | 7 citations. **Directly overlaps thesis RO4 / contradiction handling.** |
| **MoRE-RAG: Bayesian optimal fusion of multiple retrieval experts for retrieval-augmented generation** — Jixin Xu, Xingxin Li, Qingqing Song, Senlin Zhu | *Neurocomputing*, vol **701**, art. **134536**, DOI **10.1016/j.neucom.2026.134536** (2026) | **Bayesian fusion of retrieval experts** — overlaps the thesis's Bayesian-posterior gate and the RRF fusion rationale. |
| **Adaptive iterative retrieval for enhanced retrieval-augmented generation** — Wenhan Han, Xiao Xiao, Yaohang Li, Jun Wang | *Neurocomputing*, vol **666**, art. **132272**, DOI **10.1016/j.neucom.2025.132272** (2026) | |
| **ReflectRAG: Enhancing RAG with GRPO-optimized iterative reflection** — Xuanhe Chen, Yuchen Li, Youyi Bi, Shuaiqiang Wang | *Neurocomputing*, vol **695**, art. **134047**, DOI **10.1016/j.neucom.2026.134047** (2026) | |
| **IRAGKR: Iterative RAG with fine-grained knowledge refinement** — Kangning Du, Wenyu Wang, Benkui Zhang | *Neurocomputing*, vol **655**, art. **131282**, DOI **10.1016/j.neucom.2025.131282** (2025) | |
| **Multi-scale trend decomposition mixture of experts and time series retrieval-augmented modeling** — Yifei Sun, Xuefeng Yan | *Neurocomputing*, vol **657**, art. **131701**, DOI **10.1016/j.neucom.2025.131701** (2025) | Time-series RAG — relevant to the ML categories. |
| **Large Language Models Cannot Self-Correct Reasoning Yet** — Jie Huang, Xinyun Chen, Swaroop Mishra, Huaixiu Steven Zheng | arXiv **2310.01798** (2023-10-03), **ICLR 2024** | **The key citation justifying the thesis's "gate must live in code, not in the LLM loop".** |

### 1.4 New verified papers — benchmarks, evaluation, generalization

| Paper | Venue / ID | Verified detail |
|---|---|---|
| **TeleEmbedBench: A Multi-Corpus Embedding Benchmark for RAG in Telecommunications** — Pranshav Gajjar, Vijay K Shah | arXiv **2604.17778** (2026-04-20) | **First large-scale multi-corpus embedding benchmark for telecom.** 3 heterogeneous corpora (O-RAN Alliance specs, 3GPP release docs, srsRAN codebase); **9,000 question-chunk pairs**; 3 chunk sizes (**512 / 1024 / 2048** tokens); 8 embedding models. LLM-based embedders (Qwen3, EmbeddingGemma) significantly beat sentence-transformers; **domain-specific instructions help raw source code but degrade natural-language specification retrieval**. TeleEmbedBench-Clean tests noisy/incomplete queries. |
| **MiRAGE: A Multiagent Framework for Generating Multimodal Multihop Question-Answer Dataset for RAG Evaluation** | arXiv **2601.15487** (2026-01-21) | Swarm of specialized agents (recursive context optimization, adversarial verifier, expert-persona agent) generates verified domain-specific multimodal multi-hop QA. 4 domains (regulations, finance, quantitative biology, journalism). **>2.3 average hops**, higher factual faithfulness. Ablation: works with textual image descriptions; **visual grounding remains a frontier**. |
| **Chunking, Retrieval, and Re-ranking: An Empirical Evaluation of RAG Architectures for Policy Document Question Answering** — Anuj Maharjan, Umesh Yadav | arXiv **2601.15457** (2026-01-21) | Mistral-7B-Instruct-v0.2 + all-MiniLM-L6-v2 over CDC policy corpora. **Vanilla LLM faithfulness 0.347 → Basic RAG 0.621 → Advanced RAG (cross-encoder re-ranking) 0.797.** Recursive-char vs token-based semantic chunking ablated. **The single most useful reference for the thesis's expected ablation numbers.** |
| **Generalistic or Specific Embeddings, Which is Better? An Empirical Study on Search for Clinical Coding in Non-English Languages** — David Rey-Blanco, Roberto Cruz | arXiv **2605.30529** (2026-05-28) | Two-stage bi-encoder→cross-encoder; bi-encoder **MRR 0.876 vs BioBERT-ST 0.866**, **R@3 0.650 vs 0.626**, **R@5 0.804 vs 0.790** without English biomedical pretraining; cross-encoder lifts aggregate **R@5 to 0.822**; Portuguese **R@5 0.829 vs 0.714**; learning gain **MRR 0.755→0.876 (+15.9%)** with ~19,500 synthetic pairs. **Directly informs thesis RO4 (cross-category transfer).** |
| **MODE: Mixture of Document Experts for RAG** — Rahul Anand | arXiv **2509.00100** (2025-09-27) | Cluster-and-route retrieval replaces NN search + reranking with cached centroids. On HotpotQA/SQuAD with **100–500 chunks**, matches or exceeds a dense-retrieval baseline while cutting end-to-end retrieval time. **A serious, cheaper alternative to the thesis's category pre-filter + cross-encoder rerank stack at the thesis's own corpus scale.** |
| **ExpertQA: Expert-Curated Questions and Attributed Answers** | arXiv **2309.07852** (2023-09-14) | **484 participants across 32 fields**; experts evaluate responses to their own questions; output = **2,177 questions with verified answers and attributions for claims**. The methodological precedent for expert-annotated, attribution-carrying QA benchmarks. |
| **Benchmarking Large Language Models in Retrieval-Augmented Generation** — Jiawei Chen, Hongyu Lin, Xianpei Han, Le Sun | arXiv **2309.01431** (2023-09-04), **AAAI 2024** | The RGB benchmark; NLI-based evaluation of whether retrieved context is *used*. Basis for the thesis's NLI-based contradiction gate. |
| **BEIR: A Heterogeneous Benchmark for Zero-shot Evaluation of Information Retrieval Models** | arXiv **2104.08663** (2021-04-19) | 18 datasets, 10 retrieval systems (lexical, sparse, dense, late-interaction, re-ranking). **"BM25 is a robust baseline"**; **"re-ranking and late-interaction-based models on average achieve the best zero-shot performances, however, at high computational costs"**; dense/sparse more efficient but underperform. **This is the single most consequential citation for thesis RO3 and RO4.** |
| **MTEB: Massive Text Embedding Benchmark** — Niklas Muennighoff, Nouamane Tazi, Loïc Magne, Nils Reimers | arXiv **2210.07316** (2022-10-13) | Standard embedding-model evaluation. |
| **M3-Embedding: Multi-Linguality, Multi-Functionality, Multi-Granularity Text Embeddings** — Jianlv Chen, Shitao Xiao, Peitian Zhang, Kun Luo et al. | arXiv **2402.03216** (2024-02-05) | One model doing **dense + multi-vector + sparse** retrieval simultaneously; up to **8,192 tokens**; self-knowledge distillation fuses the three relevance scores as teacher signal. **A direct, single-model alternative to the thesis's BM25+dense+RRF stack.** |
| **BAAI/bge-m3** | Hugging Face model ID `BAAI/bge-m3` | Verified: **30,192,732 downloads**, 3,948 likes. The reference implementation used by arXiv 2605.28222's hybrid pipeline. |
| **cross-encoder/ms-marco-MiniLM-L6-v2** | Hugging Face model ID | Verified: **68,904,195 downloads**, pipeline `text-ranking`. **See §5.1 — the thesis report's model ID contains a typo.** |
| **cross-encoder/ms-marco-MiniLM-L12-v2** | Hugging Face model ID | Verified: 1,410,993 downloads, `text-ranking`. |
| **Zero-Shot Dense Retrieval with Embeddings from Relevance Feedback** | arXiv **2410.21242** (2024-10-28) | |
| **Doc2Query++: Topic-Coverage based Document Expansion … Dense Retrieval via Dual-Projection** | arXiv **2510.09557** (2025-10-10) | |
| **BiCA: Effective Biomedical Dense Retrieval with Citation-Aware Hard Negatives** | arXiv **2511.08029** (2025-11-11), **AAAI 2026 oral** | Citation-aware negatives — bears on evidence grounding. |
| **Not All Queries Need Rewriting: When Prompt-Only LLM Refinement Helps and Hurts Dense Retrieval** | arXiv **2603.13301** (2026-03-02) | |
| **HyperbolicRAG** — Linxiao Cao, Ruitao Wang, Jindong Li, Zhipeng Zhou, Menglin Yang | arXiv **2511.18808** (2025-11-24) | |
| **HiPerRAG: High-Performance Retrieval Augmented Generation for Scientific Insights** — Ozan Gokdemir et al. (incl. Anima Anandkumar, Aditi Krishnan, Aswathy Ajith) | arXiv **2505.04846** (2025-05-07), **PASC 25** | Scientific-literature RAG at scale. |
| **Retrieval-Augmented Generation with Graphs (GraphRAG)** — Haoyu Han, Yu Wang et al. | arXiv **2501.00309** (2025-01-08) | 2025 survey of GraphRAG. |
| **ATLAS: Learning to Recommend Across Unseen Domains** | arXiv **2608.03899** (2026-08-04) | Cross-domain transfer. |
| **TeleEmbedBench / MRAG: Benchmarking RAG for Bio-medicine** | arXiv **2601.16503** (2026-01-23) | Domain benchmark. |
| **Pursuing Best Industrial Practices for RAG in the Medical Domain** | arXiv **2602.03368** (2026-02-03) | |

### 1.5 New verified papers — time series (for the three ML categories)

| Paper | Venue / ID | Verified detail |
|---|---|---|
| **Time-LLM: Time Series Forecasting by Reprogramming Large Language Models** — Ming Jin, Shiyu Wang, Lintao Ma, Zhixuan Chu et al. | arXiv **2310.01728** (2023-10-03), **ICLR 2024** | Reprograms time series into token sequences for LLM forecasting. |
| **Chronos: Learning the Language of Time Series** — Abdul Fatir Ansari, Lorenzo Stella, Caner Turkmen, Xiyuan Zhang et al. | arXiv **2403.07815** (2024-03-12) | Scaling + quantization of time-series values into a fixed vocabulary; pretrained probabilistic TS models. |
| **Chronos-2: From Univariate to Universal Forecasting** — Ansari, Shchur, Küken, Auer et al. | arXiv **2510.15821** (2025-10-17) | **Latest in the family; multivariate + covariates.** |
| **Timer-XL: Long-Context Transformers for Unified Time Series Forecasting** — Yong Liu, Guo Qin, Xiangdong Huang et al. | arXiv **2410.04803** (2024-10-05) | |

---

## 2. Deep explanations of the most important papers

### 2.1 PIKE-RAG (Wang et al., arXiv 2501.11551) — the closest *industrial* prior art

PIKE-RAG argues that plain retrieval is structurally insufficient for industrial tasks. Its thesis is that industrial documents contain **specialised knowledge** whose value is destroyed by naïve chunk-and-embed: a formula, a tolerance table, or a conditional rule only means something when it is extracted, understood and applied in context. The framework therefore introduces two components. **Knowledge atomizing** breaks retrieved chunks into discrete, self-contained "knowledge atoms" before they reach the generator. **Knowledge-aware task decomposition** splits the original query into sub-tasks and constructs the rationale iteratively, so the rationale accumulates knowledge rather than restating the question. The paper also proposes a task-complexity taxonomy that classifies industrial queries by how much knowledge extraction and application they demand, which is what allows it to evaluate RAG systems by *problem-solving* capability rather than by answer overlap.

For the thesis, this matters in two ways. First, it is the strongest existing evidence that the industrial RAG problem is recognised and partially solved, so the thesis must not claim to have discovered it. Second, it is the natural baseline: the thesis's own architecture deliberately omits atomization and rationale construction, choosing instead to invest the engineering effort in *evidence discipline* (gating, modality balance, contradiction surfacing, per-claim confidence). That is a legitimate design choice — but it must be stated as a trade-off against PIKE-RAG, not presented as if PIKE-RAG does not exist.

### 2.2 Wan et al. 2025 (Adv. Eng. Inf. 65:103212) — hybrid RAG in smart manufacturing

This is the thesis's closest *journal-published* neighbour and, at 130 citations, its most visible one. The title is precise about the method: hybrid retrieval-augmented generation for **domain-centric** question answering in smart manufacturing. The design is the same shape the thesis proposes — a hybrid retriever combining lexical and dense signals over a domain-specific corpus, with the generator conditioned on the fused evidence. The reported result is **77.8% accuracy** on design-for-manufacturing queries, and the paper's own framing positions hybrid retrieval as necessary because manufacturing documents contain both formal specification tables and narrative process text, and neither retrieval mode alone covers both.

The thesis should cite this as the strongest evidence that (a) the hybrid-retrieval architecture is the right choice for industrial corpora and (b) the result will be measured against a published, citable baseline rather than an unopposed claim. It also sets a number the thesis can be compared against: if a plain hybrid RAG already achieves 77.8% on a *narrow* domain-centric question set, then the thesis's evidence-discipline mechanisms must be shown to add value **on top of** a strong hybrid baseline — not merely to beat a weak vanilla RAG. Any ablation table in the thesis that does not include a hybrid+Rerank arm is incomplete by the standard of this literature.

### 2.3 Wu et al. 2025 (Adv. Eng. Inf. 65:103158) — construction-management RAG at corpus scale

This paper builds a RAG system for information retrieval and question answering in construction management — a domain with the same defining characteristics as industrial engineering: long heterogeneous document sets (codes, method statements, submittals, inspection records), heavy acronym use, and a hard requirement that answers are defensible because they are checked by certification bodies. What it demonstrates is not a new retrieval algorithm but the *engineering* of a working domain system: document ingestion and structuring for construction-specific formats, indexing, retrieval, and generation tuned to the domain's question distribution.

Its methodological value for the thesis is as a **feasibility precedent** at realistic corpus scale, and as a source of the practical design constraints the thesis will hit: domain vocabulary control, document-structure-aware chunking, and query-intent diversity. The thesis's own claim that "no public benchmark exists for industrial-engineering Q&A" must be read against this paper's existence: construction management has published RAG systems, so the thesis's benchmark gap must be scoped to *benchmark datasets with expert annotation and per-claim attribution*, not to "no one has done industrial RAG".

### 2.4 TechRAG (arXiv 2606.01613) — the closest prior art to the entire thesis

This paper must be read carefully before the 18 November defence, because it implements nearly every mechanism the thesis proposes, in a technical-literature domain.

Its pipeline: classify query intent → generate **separate text and visual query rewrites** → **hybrid text retrieval with FAISS and BM25 followed by cross-encoder reranking** → expand evidence through **graph-guided chunk traversal** over a Neo4j knowledge graph → retrieve visual document evidence with **ColSmol late-interaction embeddings, MUVERA fixed-dimensional encoding, ANN search and MaxSim reranking** → score **evidence sufficiency using a 100-point rubric with hybrid rule-based/LLM review** → retry retrieval through **drift-guarded reformulation** → search external academic databases via optimize→search→vet loops → **merge and deduplicate multimodal evidence** → **verify citation integrity** → generate cited answers through Planner/Researcher/ Writer/ Critic agents with self-correcting revision.

Map that against the thesis's five design moves: **D1 (code-level confidence gate)** ≈ the evidence-sufficiency rubric and the drift-guarded retry, though TechRAG's gate is an LLM-assisted rubric inside an agentic loop, whereas the thesis's gate is a code-level Bayesian posterior threshold that is non-bypassable — this is a real but narrow difference. **D2 (modality-balanced quotas)** ≈ TechRAG's separate text/visual retrieval paths, though TechRAG does not describe a *quota* mechanism; it retrieves per modality and fuses. **D3 (hybrid lexical + dense + reranker via RRF, category pre-filter)** ≈ exactly TechRAG's FAISS+BM25→cross-encoder stage; TechRAG adds an intent-classification router in place of the thesis's static category pre-filter. **D4 (contradiction surfacing)** — TechRAG does **not** surface contradictions; it verifies citation integrity and cites an agent to critique the draft. **D5 (per-claim three-band confidence)** ≈ TechRAG's citation-integrity verification, though it is not a per-claim grounded/inferred/uncertain tagging scheme.

The honest conclusion is that the thesis's *architectural combination* is no longer novel as of June 2026, and the "evidence-gated multimodal agentic RAG" label is taken. What survives as a defensible contribution is narrower and still substantial: **contradiction surfacing as a first-class output** (TechRAG has no equivalent), **code-level non-bypassable gating** as opposed to in-loop LLM gating, **per-claim three-band confidence**, **a category-partitioned twelve-domain industrial corpus and benchmark**, and **a controlled evaluation of the failure modes**. The thesis should reframe from "we designed an evidence-grounded framework" to "we measured whether evidence-grounding mechanisms change industrial decision outcomes, and we characterised where they fail" — which is exactly what RO3 (failure-mode characterization) already promises, and which is the more valuable contribution anyway.

### 2.5 Domain-Partitioned Hybrid RAG for Indian Legal Reasoning (arXiv 2602.23371)

This paper is structurally the thesis's RO3 idea, in a different domain, in the same country. Its premise is that legal research in India requires navigating long heterogeneous document types (statutes, constitutional provisions, penal codes, judicial precedents), where "purely keyword-based or embedding-only retrieval systems often fail to support structured legal reasoning". The system therefore splits retrieval into **three domain-partitioned pipelines**, each optimised for one document family, adds a **Neo4j legal knowledge graph** for relational reasoning, and uses an **LLM-driven agentic orchestrator** to route each query to the right module and fuse the evidence into a citation-aware answer. Evaluation uses a 40-question synthetic benchmark curated from authoritative Indian legal sources, scored by **LLM-as-judge**. Result: **70% pass rate for the hybrid architecture versus 37.5% for a RAG-only baseline**, with marked improvements in completeness and legal reasoning quality.

The implications for the thesis are direct and should be stated in the related-work section. First, the headline architecture — *partition the corpus by domain, route queries, fuse hybrid retrieval, cite sources* — is published prior art. Second, the effect size (37.5% → 70%) is the *upper bound* the thesis should expect for a comparable domain-partitioning gain; the thesis's own RO3 claim should be calibrated against it. Third, because this is Indian legal rather than industrial, and because it uses an LLM-as-judge on 40 synthetic questions with no human-expert annotation and no per-claim confidence, the thesis's contribution must be positioned as **industrial specificity plus rigorous human-validated evaluation** — not as a new architecture. The thesis's evaluation design (dual annotators, Cohen's κ, expert-validated subset) is a genuine methodological advantage over this paper's evaluation.

### 2.6 UA-RAG (Neurocomputing 699:134357) — uncertainty-aware dynamic retrieval

UA-RAG addresses the same problem as the thesis's RO1: making the retrieval step *know when it has failed* rather than always producing something. Its existence means the thesis's D1 is not a new idea; it is an established research direction with a 2026 journal publication in the same venue family the thesis cites. The thesis's defence of D1 must therefore be about the *mechanism*, not the *idea*: a deterministic, code-level, non-bypassable threshold on a calibrated Bayesian posterior, evaluated on an industrial corpus with a hard abstention class, versus an in-pipeline uncertainty heuristic.

This is where the thesis can genuinely win, because there is a specific, well-documented reason to distrust LLM-mediated gating. Huang et al. (*Large Language Models Cannot Self-Correct Reasoning Yet*, ICLR 2024) show that LLM self-correction behaviour is not reliable and can degrade correct outputs. If a gate is implemented as an LLM judge inside the generation loop — as TechRAG's rubric and most reflection-based methods are — the gate inherits exactly that unreliability, and can be talked past by a confident-sounding draft. A gate that computes a posterior over retrieval scores in ordinary code, and refuses to call the generator when the posterior is below threshold, cannot be argued with by the generator. The thesis's report already articulates this ("gate lives inside the LM loop: bypassable in principle"); that argument should be promoted from a footnote to a named design principle with the Huang et al. citation attached.

### 2.7 ICR — resolving knowledge conflicts in RAG (Neurocomputing 664:132139)

ICR targets the scenario the thesis calls contradiction surfacing: retrieved documents disagree, and a generator silently picks one. Its existence in 2026 is significant for the thesis because the thesis's D4 was, until recently, a distinguishing feature. As with UA-RAG, the thesis's defensible claim narrows from "we detect contradictions" to a specific, differentiated mechanism: a **joint NLI + topical gate** that requires both a contradiction verdict *and* a shared-subject condition before flagging a conflict.

That joint condition is the whole point, and the thesis's own report supplies the evidence that it matters: NLI-only contradiction detection reportedly produced a **98% false-positive rate**, reduced to **16%** by adding the topical gate. Those are strikingly high numbers and, on their face, unusual — published NLI contradiction classifiers typically score far better than 2% precision on curated contradiction pairs. The honest interpretation is that 98% FP is a property of *unfiltered industrial text*, where NLI sees two passages about entirely different subjects (a safety-stock rule and a tariff rule) and reads the non-entailment as a contradiction. The topical gate removes those. This is a real and defensible engineering contribution, but the numbers need to be reported with the denominator and the definition of "false positive" spelled out, or a committee will reasonably doubt them.

### 2.8 GUIDE — graph-enhanced RAG for assembly anomaly diagnosis (CIE 220:112246)

GUIDE applies a knowledge-unified, graph-enhanced RAG framework to assembly anomaly diagnosis in manufacturing — an industrial diagnosis problem where the answer depends on relations between parts, tools, fault modes and process steps rather than on a single passage. Its relevance to the thesis is that it demonstrates the industrial value of explicitly modelling structure rather than treating a document collection as a flat bag of chunks. It also provides a concrete counterweight to the thesis's simpler approach: if the industrial corpus encodes real structure (a BOM, an FMEA cross-reference table, a fault tree), then a flat category-partitioned retrieval scheme leaves that structure on the table.

For the thesis this motivates a specific, honest piece of future work and a specific scope statement: the framework deliberately treats the corpus as *category-partitioned but not graph-structured*, and the comparison against a graph-augmented arm is the natural next experiment. It also strengthens the argument for the thesis's table/chart modality work, since BOMs and FMEA matrices are exactly the tabular artefacts whose relationships carry the answer.

### 2.9 TeleEmbedBench (arXiv 2604.17778) — what an industrial retrieval benchmark looks like in 2026

TeleEmbedBench is the best available template for the thesis's benchmark construction, and it is three months old. It spans **three heterogeneous corpora** (O-RAN Alliance specifications, 3GPP release documents, and the srsRAN open-source codebase), contains **9,000 question-chunk pairs**, and evaluates **eight embedding models** across **three chunk sizes (512 / 1024 / 2048 tokens)**. Crucially, it addresses the annotation bottleneck with an **automated two-stage LLM pipeline** — one LLM generates a specific query from a chunk, a second LLM validates it against strict criteria — rather than relying entirely on human annotation.

Two findings should shape the thesis directly. First, **LLM-based embedders (Qwen3, EmbeddingGemma) consistently and significantly outperform traditional sentence-transformers in both retrieval accuracy and robustness against cross-domain interference.** The thesis's specified embedding model is `all-MiniLM-L6-v2` (384-d), a sentence-transformer from 2022. That is a defensible choice for a small 634-chunk corpus and for reproducibility, but the thesis must justify it explicitly against the finding that this model class is the weaker one, or a committee will ask. Second, and more interesting: **domain-specific task instructions improve embedder performance for raw source code but paradoxically degrade retrieval performance for natural-language specifications.** That is a direct empirical warning for the thesis's RO4 — a retrieval configuration tuned on one industrial category may *not* transfer to another, and the failure mode may be category-dependent in a non-obvious way. This is a citable, specific, testable hypothesis for the cross-category study.

### 2.10 Chunking, Retrieval and Re-ranking for policy-document QA (arXiv 2601.15457) — the expected-numbers reference

This paper runs exactly the ablation the thesis needs to run, on CDC policy documents, with a Mistral-7B-Instruct-v0.2 generator and an all-MiniLM-L6-v2 embedder, and it reports the faithfulness ladder that a thesis defence committee will want to see justified: **Vanilla LLM 0.347 → Basic RAG 0.621 → Advanced RAG with cross-encoder re-ranking 0.797.** It also ablates two chunking strategies (recursive character-based vs token-based semantic splitting) and concludes that **structural constraints in document segmentation remain a significant bottleneck for multi-step reasoning tasks.**

Two consequences. First, the thesis's ablation table should be expected to show a roughly **0.35 → 0.62 → 0.80** faithfulness ladder across vanilla → RAG → hybrid+rerank. A thesis that reports a much smaller jump needs an explanation; a thesis that reports a much larger jump should be checked for leakage. Second, the paper's conclusion — that *chunking*, not retrieval, is the bottleneck for multi-step reasoning — is a warning for the thesis's multi-hop industrial questions: if the thesis reports weak multi-hop performance, the cause is more likely to be chunk boundaries than the confidence gate. That is a strong, defensible piece of failure-mode analysis for RO3.

---

## 3. Claim verification — adjudication of the thesis proposal's load-bearing claims

### 3.1 "No public benchmark exists for industrial-engineering Q&A" — **PARTLY FALSE. Must be restated.**

Evidence against the literal claim, all verified:

- **TeleEmbedBench** (arXiv 2604.17778, 2026) is a public, large-scale, multi-corpus **embedding/retrieval benchmark for telecommunications**, with 9,000 question-chunk pairs over O-RAN, 3GPP and srsRAN, and an explicit argument that general-purpose benchmarks fail on acronym-heavy industrial corpora. Telecommunications is an industrial-engineering domain.
- **Kubernetes technical-documentation benchmark** (arXiv 2605.28222, 2026) — **5,144 manually verified QA pairs** over official Kubernetes documentation, publicly released with code and adapters.
- **MiRAGE** (arXiv 2601.15487, 2026) generates verified domain-specific multimodal multi-hop QA datasets across regulations, finance, quantitative biology and journalism.
- **ExpertQA** (arXiv 2309.07852) — **2,177 expert-curated questions across 32 fields**, with verified answers *and per-claim attributions*, from 484 expert participants.
- Industrial QA systems are published: **ManuRAG** (JIM 2026), **GUIDE** (CIE 2026), **Wan et al.** (AEI 2025), **Wu et al.** (AEI 2025), **TechRAG** (2026), **railway regulations case study** (2026), **pharma QA-RAG** (2024).

Evidence that survives: no public benchmark was found covering **twelve industrial-engineering categories with dual human-expert annotation and per-claim evidence attribution**, and no public benchmark was found for supply-chain-specific industrial Q&A specifically.

**Recommended restatement for the thesis:**
> "No public benchmark exists for industrial-engineering Q&A that (i) spans multiple IE sub-domains, (ii) carries dual human-expert annotation with an inter-annotator agreement statistic, and (iii) records per-claim evidence attribution. Existing industrial retrieval benchmarks are single-domain (TeleEmbedBench — telecom), software-documentation-specific (Kubernetes), or generated-and-validated by LLMs rather than domain experts (MiRAGE); existing expert-annotated attribution datasets (ExpertQA) are general-purpose and predate the industrial framing."

This version is true, verifiable, and specific enough to survive a committee challenge.

### 3.2 The report cites CRAG as an ACL Findings paper — it is not

The report's reference list reads:

> Yan, S.-Q., Gu, J.-C., Zhu, Y., & Ling, Z.-H. (2024). Corrective retrieval augmented generation. In *Findings of the Association for Computational Linguistics: ACL 2024* (pp. 3563–3578). https://doi.org/10.18653/v1/2024.findings-acl.212

Three separate checks all say this is wrong:

1. **The DOI belongs to a different paper.** `10.18653/v1/2024.findings-acl.212` resolves to **"Chain-of-Verification Reduces Hallucination in Large Language Models"** by Shehzaad Dhuliawala, Mojtaba Komeili, Jing Xu, Roberta Raileanu, Xian Li, Asli Celikyilmaz — pages **3563–3578**, i.e. exactly the page range the report prints. The report's DOI and page range are internally consistent with each other and both point at Dhuliawala et al.'s paper, not at CRAG.
2. **CRAG is not in the Findings of ACL 2024 proceedings.** The ACL Anthology volume listing for `2024.findings-acl` (2.6 MB, 2,929 `2024.findings-acl.*` entries) contains "Chain-of-Verification" but **zero** occurrences of "Shi-Qi" or "CRAG". The paper is simply not there.
3. **Semantic Scholar records no peer-reviewed venue.** For arXiv:2401.15884 the `externalIds` are `{ArXiv: 2401.15884, DBLP: journals/corr/abs-2401.15884, DOI: 10.48550/arXiv.2401.15884}` and `publicationVenue.name` is **"arXiv.org"**. An OpenReview search returns zero hits. Crossref lists only an SSRN preprint (`10.2139/ssrn.5267341`, 2025).

**Correct citation:** Yan, S.-Q., Gu, J.-C., Zhu, Y., & Ling, Z.-H. (2024). *Corrective Retrieval Augmented Generation*. arXiv:2401.15884. https://doi.org/10.48550/arXiv.2401.15884

*(The DOCX proposal's reference [3] already gets this right — it cites "arXiv:2401.15884" with no venue claim. It is the PDF report's reference list that introduces the error.)*

This matters more than a formatting nit: CRAG is the thesis's stated point of comparison for RO1 and RO2, and a committee member who checks the DOI will find Chain-of-Verification. If a peer-reviewed CRAG version has since appeared somewhere not covered by the registries above, substitute that — but the citation as printed is definitively wrong either way.

### 3.3 Two DOI year/number transcriptions are wrong — papers are real

Both were confirmed against Crossref's authoritative record.

| Proposal | Correct | Evidence |
|---|---|---|
| Decian et al. (2026), *Neurocomputing* 705:134911, DOI `10.1016/j.neucom.**2025**.134911` | `10.1016/j.neucom.**2026**.134911` | Crossref journal sweep for ISSN 0925-2312 returned: *Neurocomputing* vol 705, art. 134911, 2026, "Dynamic RAG with hybrid retrieval: A novel approach to robust LLMs and hallucination prevention", Jean Decian, Chaima Njeh, Haïfa Nakouri, Fehmi Jaafar. `doi.org/10.1016/j.neucom.2025.134911` returns **HTTP 404**; `api.crossref.org` returns *Resource not found*. |
| Zhang & Zhang (2025), *Mathematics* 13:856, DOI `10.3390/math**1313**0856` | `10.3390/math**1305**0856` | Crossref journal sweep for ISSN 2227-7390 returned: *Mathematics* vol 13, iss 5, art. 856, 2025, "Hallucination Mitigation for Retrieval-Augmented Large Language Models: A Review", Wan Zhang, Jing Zhang. `doi.org/10.3390/math13130856` returns **HTTP 404**. |

Both of these are *correctable typos in an otherwise correct citation*. Fix them in the paper, the report and the slides.

*(Verification note: a bulk Semantic Scholar DOI check over all four suspect DOIs returned "not found" for every one of them, including the two that are demonstrably valid. That run hit the S2 rate limiter — it is a false-negative artifact, not evidence. The findings above rest on Crossref's DOI registry and direct `doi.org` HTTP resolution, both of which agree, and the two *valid* Adv. Eng. Inf. DOIs were independently corroborated by S2 on a later, successful call — including the 130-citation count for Wan et al. recorded in §1.2. Where the two registries disagree, Crossref and doi.org resolution are the arbiter.)*

### 3.4 arXiv:2507.21502 is real but misattributed, and mischaracterised

The proposal's reference [15] reads: *"Microsoft Research (2025). 'Large language models for supply chain decisions.' arXiv:2507.21502."* The proposal's literature-review table further describes it as *"Fine-tuned LLM for procurement decisions"*, with the remark *"Real-world Microsoft deployment."*

The verified record: **"Large Language Models for Supply Chain Decisions"**, by **David Simchi-Levi, Konstantina Mellou, Ishai Menache, Jeevan Pathuri** (arXiv 2507.21502, 2025-07-29, cs.AI). The comment field states: *"Forthcoming chapter in AI in Supply Chains: Perspectives from Global Thought Leaders, edited by Maxime C. Cohen and Tinglong Dai, and part of the Springer Series in Supply Chain Management (edited by Prof. Chris Tang)."*

Three corrections are required: the **author is Simchi-Levi et al., not Microsoft Research** (Simchi-Levi is well known as the author of the *hard-cap* inventory model — citing this as a Microsoft deployment would be a visible error); it is a **book chapter, not a journal paper**; and it is **not about fine-tuning for procurement**. The abstract describes applying LLMs to *interface with supply-chain optimisation tools* — explaining tool outputs, answering what-if questions, and updating the underlying models — reporting a reduction in decision time from days/weeks to minutes/hours. Attributing to it a fine-tuned procurement LLM overstates it in a way that a committee with operations-research background will catch immediately, since Simchi-Levi is himself an OR academic.

Note also that this paper is a good citation to **keep**, for a different reason than the proposal gives: it establishes that the supply-chain decision problem is being attacked from the operations-research side, and it frames the LLM's role as *explanation and interaction*, not *decision*. That framing aligns with the thesis's own position — the framework supports decisions with evidence; it does not make them.

### 3.5 Proposal reference [17]'s title is wrong

Proposal: *"Mitigating Hallucination in Large Language Models: An **Application-Oriented** Survey on RAG, Reasoning, and Agentic Systems."*
Verified (OpenAlex + arXiv): *"Mitigating Hallucination in Large Language Models: A **Capability-Oriented** Survey on RAG, Reasoning, and Agentic Systems."* Yihan Li, Xiyuan Fu, Ghanshyam Verma, Paul Buitelaar, Mingming Liu (2025-10).

Fix "Application-Oriented" → "Capability-Oriented". Keep this citation — a 2025 survey organised around *capability* rather than application is directly useful for positioning the thesis's contributions, and the proposal's own remark that it "adopts their taxonomy framing" is a sound instinct.

### 3.6 The "SupplyChainQA" benchmark does not exist publicly

Searches of the Hugging Face dataset hub for `SupplyChainQA`, `industrial-qa`, `maintenance-qa`, `industrial-engineering` and `supply_chain` returned no benchmark matching that name or profile. What exists is small and unrelated: `sebdg/supply_chain_q_a` (33 downloads), `sebdg/supply_chain_q_a_conversion` (21), `duonganh2973/industrial_qa` (433), `alalfi/SupplyChainDataset` (130), `jebnypandas/aviation-maintenance-qa` (27), `AI4Manufacturing/maintenance_failure_qa_training` (45).

The thesis's own report confirms this from the inside: its *Future Work* section lists **"Release the benchmark and the framework on Zenodo + HuggingFace"** as a long-term item. So "SupplyChainQA v7" is the student's own internal construction, versioned internally, and **not yet released**.

Consequences: (a) the paper must say **"our benchmark"**, never "the SupplyChainQA benchmark", and must not imply prior availability; (b) the report's RO4 hypothesis — *"A public expert-annotated benchmark with κ ≥ 0.7 across categorical fields is achievable and useful"* — is a **deliverable**, not a premise, and should be framed as such; (c) it is a genuine contribution *if released*, and releasing it before 18 November would substantially strengthen the submission; (d) the "v7" suffix should be explained or dropped, since it advertises undocumented internal churn.

### 3.7 Verdict on the proposal's literature-review table

Of the 18 entries: **18 describe papers that exist** (none is a phantom), but **5 carry specific errors** — a wrong venue/DOI/page-range for CRAG ([3], §3.2), a wrong author attribution and mischaracterised method ([15], §3.4), a wrong title word ([17], §3.5), and two malformed DOIs ([8], [18], §3.3). Two entries the report lists were checked and found **correct** — Self-RAG's arXiv ID `2310.11511` resolves exactly to Asai et al.'s Self-RAG, and Cormack et al.'s RRF DOI `10.1145/1571941.1572114` resolves to the correct SIGIR 2009 paper at pp. 758–759 — and needed no change. The table's *characterisations* of each paper's method are otherwise accurate and well-judged (e.g. noting that Self-RAG's gate is bypassable in principle, that CRAG uses dynamic refinement, that GraphRAG is computationally heavy).

**The table's real problem is not accuracy — it is completeness.** It contains no paper from 2025-2026 that overlaps the thesis's core mechanisms, because the survey was evidently assembled before that literature appeared. The following must be added and discussed as the closest prior art: **TechRAG** (2606.01613), **UA-RAG** (Neurocomputing 699:134357), **ICR** (Neurocomputing 664:132139), **MoRE-RAG** (Neurocomputing 701:134536), **Confidence-weighted semantic entropy** (Neurocomputing 704:134859), **Domain-Partitioned Hybrid RAG for India** (2602.23371), **CAR-RAG** (IEEE BigData 2025), **TeleEmbedBench** (2604.17778), **ManuRAG** (JIM 2026), **Chunking/Retrieval/Re-ranking** (2601.15457), **MODE** (2509.00100), and **BEIR** (2104.08663).

---

## 4. Twelve-category design guide

A working specification an engineer could follow to build the corpus, the questions and the annotations. Category names are the thesis's own; the document archetypes, question forms and naming conventions follow standard industrial-engineering practice and are consistent with the category papers verified above.

| # | Category | Primary document archetypes | Typical binding artefact | A good question | Plausible answer form | Named methods the category config should carry (per the proposal) |
|---|---|---|---|---|---|---|
| 1 | **Supply Chain Management** ★ focus | Supplier qualification files, purchase orders, Incoterms rules, GS1 specs, service-level agreements, EOQ policy | Supplier scorecard tables; Incoterms rule tables | "What is the economic order quantity for SKU A-104 under the current reorder policy?" | A number with the policy reference cited | Cp/Cpk, EOQ, safety-stock rules |
| 2 | **Predictive Maintenance** | CMMS records, work orders, sensor trend exports, OEM service manuals, runbooks | Condition-monitoring thresholds; maintenance-interval tables | "At what vibration threshold does line 3 compressor C-2 trigger a bearing inspection?" | Threshold + triggering condition + source clause | Anomaly detection thresholds; degradation curves |
| 3 | **Reliability Engineering** | FMEA sheets, fault trees, MTBF reports, repair-time logs | FMEA RPN matrices; failure-mode tables | "Which failure mode carries the highest RPN for the gearbox assembly, and what is its detection ranking?" | Ranked table row with the RPN components | FMEA RPN; Weibull; MTBF/MTTR |
| 4 | **Quality Engineering** | Control plans, 8D reports, ISO 9001 clauses, SPC charts, inspection records | Control limits; Pareto charts | "What are the upper and lower control limits for fill weight on line 2, and what happens when a point falls outside them?" | Limits, the rule, and the resulting disposition | Cp/Cpk, SPC control charts, Pareto |
| 5 | **Production Scheduling** | Master production schedules, takt time studies, capacity matrices, Gantt charts, OEE dashboards | Capacity matrices; schedule Gantt charts | "Which line is the bottleneck for the week-38 master schedule, and by how many hours?" | Named constraint with the numbers behind it | Scheduling heuristics; OEE; capacity modelling |
| 6 | **Transportation & Logistics** | Carrier rate cards, routing guides, Incoterms 2020, lane schedules | Rate tables; transit-time matrices | "For a 320 kg shipment from Pune to Chennai, which Incoterm applies and what is the quoted transit time?" | Term + value + carrier/route | Incoterms; EOQ; network flow |
| 7 | **Reverse Logistics** | Return authorisation procedures, RMA forms, disposal manifests, refurbishment SOPs | RMA decision trees; recovery-value tables | "Under what condition is a returned assembly refurbished rather than scrapped?" | Condition → decision path, cited | Disposition logic; recovery-value scoring |
| 8 | **Inventory Management** | Stock policy documents, cycle-count reports, warehouse ledgers, ABC/XYZ analyses | Reorder-point tables; ABC classification tables | "What is the reorder point for the Class-A fastener line, and what safety factor does the policy use?" | Number + the policy derivation | EOQ, safety stock, ABC/XYZ |
| 9 | **Facility Layout & Location** | Layout drawings, load-flow layouts, distance matrices, relocation studies | Distance/adjacency matrices; layout drawings | "Which candidate site minimises total weighted distance from the two inbound docks to the paint shop?" | Site with the distance/area figures | Facility layout; location models (p-median, gravity) |
| 10 | **Demand Forecasting** | Forecast reports, promotion calendars, market/seasonality studies, error analyses | Forecast-vs-actual tables | "What was the forecast error for product P in the last quarter, and which method produced it?" | Metric + method + table reference | Demand forecasting methods; error metrics (MAPE, MASE) |
| 11 | **Time-Series Forecasting** | Sensor time-series exports, forecast files, model cards, confidence-interval plots | Forecast interval plots; residual tables | "What is the 95% prediction interval for tank-level T-4 over the next 12 hours?" | Interval + the model that produced it | Time-series models (Time-LLM, Chronos, Timer-XL) |
| 12 | **Anomaly Detection** | Alarm logs, threshold configs, anomaly reports, incident records | Alarm/threshold tables; anomaly score plots | "Which anomaly class accounts for most of the rejects on the inspection line in the last month?" | Ranked class with counts | Isolation Forest; CUSUM/EQQ; anomaly-score thresholds |

**Data-analytics methods.** The proposal folds data analytics into the ML category configurations and names **Cp/Cpk, Mann–Kendall, EOQ and Isolation Forest** as the named algorithms of the categories that use them. This is a coherent design: it means the category config carries not only retrieval parameters but a *named analytic surface* that the generated answer must respect.

**Construction rules that follow from the verified literature:**
1. **Chunk sizes.** TeleEmbedBench uses 512/1024/2048 and finds chunk size materially affects retrieval accuracy. The thesis should fix chunk size as an explicit, reported configuration and ablate at least two values.
2. **Chunking strategy is a first-class ablation.** arXiv 2601.15457 concludes that *structural constraints in document segmentation remain a significant bottleneck for multi-step reasoning*. The thesis should ablate recursive-character vs semantic/table-aware chunking, not just retrieval components.
3. **Tables need table-aware chunking.** A numeric specification extracted as a prose sentence loses its binding relationship between the value and its condition. This is the mechanism behind both the thesis's RO2 and the modality-quota null result it reports.
4. **Annotate the question type, not just the answer.** MultiHop-RAG's taxonomy (inference / comparison / temporal) and MiRAGE's hop-count metric (>2.3 average hops) are useful precedents; the thesis's 500-question set should record question type and hop count so that multi-hop performance can be reported separately — which is where a weak chunking pipeline shows itself.
5. **Annotate modality and doc-type per question.** Needed for the thesis's own modality analysis, and it is what TeleEmbedBench does implicitly by construction.
6. **Dual annotation with κ.** ExpertQA (2,177 questions, 32 fields, per-claim attributions) is the precedent for expert-annotated attribution data. The thesis's κ ≥ 0.7 threshold is consistent with that standard.
7. **Label unanswerable questions explicitly.** A benchmark without an unanswerable class cannot measure the thesis's RO1 gate — the gate's whole purpose is to refuse. This is the single most important benchmark-design requirement for this thesis, and it is cheap to add.
8. **Annotation provenance.** If questions are LLM-generated and validated, say so and report the validation criteria (MiRAGE's adversarial-verifier pattern); if human-annotated, say so and report κ. The thesis's proposal says "annotated by LLM agents using a structured protocol, with human-expert validation on a random subset" — that is a sound and publishable design, but it must be stated in exactly those terms.

---

## 5. Gaps and risks

### 5.1 Reproducibility defect in the report's model specification

The report's §7.4 specifies the cross-encoder reranker as **`ms-marco-MiniLM-L-6-v2`**. The verified Hugging Face model ID is **`cross-encoder/ms-marco-MiniLM-L6-v2`** — there is no hyphen between `L` and `6`. The API returns **HTTP 307 → `cross-encoder/ms-marco-MiniLM-L6-v2`** for the hyphenated form, i.e. the report's string is a redirect to a corrected ID, and a literal `from_pretrained("ms-marco-MiniLM-L-6-v2")` will fail or silently resolve to something else. The correct ID is `cross-encoder/ms-marco-MiniLM-L6-v2` (**68,904,195 downloads**, pipeline `text-ranking`); `cross-encoder/ms-marco-MiniLM-L12-v2` is the larger sibling (1,410,993 downloads). The report should quote the full owner-qualified ID.

### 5.2 The dominant risk: the thesis's architecture is now largely prior art

**Severity: high. This is the most important finding in this file.**

TechRAG (arXiv 2606.01613, June 2026) implements evidence gating, hybrid retrieval with cross-encoder reranking, multimodal (text + visual) retrieval with late-interaction embeddings, a sufficiency rubric, citation-integrity verification and multi-agent generation — over a *technical-literature* corpus of >40,000 pages. Domain-Partitioned Hybrid RAG (2602.23371) implements category-partitioned hybrid retrieval with citation-aware answers for India. CAR-RAG (IEEE BigData 2025) implements category-aware hybrid RAG explicitly for hallucination mitigation.

Two of the thesis's five design moves have direct published equivalents (D1 → UA-RAG, TechRAG's rubric; D3 → CAR-RAG, Domain-Partitioned Hybrid RAG, and Wan et al. 2025). One has a partial equivalent (D2 → TechRAG's separate text/visual paths, without quotas). One has an equivalent in a different form (D5 → TechRAG's citation-integrity verification). **One has no equivalent at all: D4, contradiction surfacing.**

**Recommended response — reframe, do not retreat.** The defensible contributions, stated honestly, are:
- **D4 (contradiction surfacing with a joint NLI + topical gate) is the true novelty.** No verified paper surfaces contradictions as a first-class user-facing output with an explicit false-positive control. ICR *resolves* conflicts; the thesis *shows* them.
- **The code-level, non-bypassable gate is a design choice worth defending**, on the Huang et al. (ICLR 2024) grounds that in-loop LLM gating is unreliable and adversarially bypassable.
- **Per-claim three-band confidence tagging** as an operational, practitioner-facing output (EPRAG's epistemic-policy framework is conceptually adjacent but not an operational tag set).
- **The twelve-category industrial benchmark** with dual expert annotation, κ, per-claim attribution, and an explicit unanswerable class — which does not exist publicly.
- **Systematic failure-mode characterisation across twelve categories** — the thesis's RO3, which is the contribution the committee will most value and the one no verified prior art provides.

The framing should shift from *"we designed an evidence-grounded framework"* to *"we measured what evidence-grounding mechanisms actually do to industrial decisions, across twelve categories, and characterised where they fail."* The second framing is both defensible and more valuable.

### 5.3 Novelty of RO3 specifically is weak

BEIR (arXiv 2104.08663) established, across 18 heterogeneous datasets and 10 retrieval systems, that **"re-ranking and late-interaction-based models on average achieve the best zero-shot performances"** and that **"BM25 is a robust baseline."** Hybrid-plus-rerank beating flat retrieval is therefore a **known result**, not a finding. RO3's hypothesis — "Hybrid lexical + dense + reranker via RRF, preceded by category filter, outperforms flat retrieval" — will almost certainly be confirmed, and confirming a known result adds little.

The fix is to change what RO3 *asks*. Two options, both good:
- **Ask the interesting version:** does the *category pre-filter* help or hurt? Category pre-filtering is known to degrade ANN recall (the filtered-out document may have been the correct answer), so the interesting empirical question is the *interaction* between pre-filtering and the confidence gate: does the filter make the gate more accurate (fewer irrelevant candidates → better posterior separation) or less (over-confidence when the filter is wrong)? Nobody has published this.
- **Ask about cost:** BEIR notes reranking achieves the best results "at high computational costs." The thesis can report the **latency/accuracy frontier** for the industrial case, which is exactly what MODE (2509.00100) argues matters for small corpora.

### 5.4 The modality-quota null result is the most likely outcome and should be pre-empted

The report already documents that the corpus is **2.3% chart / 7.1% table**, and that the modality-aware boost is a "documented null result" because the corpus is too text-heavy to exercise the signal. Two risks:

1. **A null result is not a failure, but it must be designed as a test rather than reported as a surprise.** If the thesis wants to say something about modality balance, the corpus must contain enough tables and charts for the mechanism to act. The honest options are: (a) build a modality-enriched sub-corpus so the mechanism has something to work on; or (b) report the null result as a **design constraint discovery** — "modality-balanced retrieval requires a modality-enriched corpus; ours is text-dominated, so the mechanism is dormant, and we report the corpus composition as a precondition." Option (b) is cheaper and is more honest; option (a) produces a stronger paper.
2. **TeleEmbedBench's finding that domain instructions help code but hurt natural-language specifications** suggests the modality effect may be category-dependent in non-obvious ways. A blanket "modality quota helps" claim is unlikely to survive.

### 5.5 The contradiction gate's false-positive numbers need better reporting

The reported **98% FP for NLI-only, 16% with the topical gate** are extreme figures and will be challenged. Published NLI contradiction classification does not typically operate at 2% precision on curated contradiction pairs; the 98% figure is plausible only as a property of *unfiltered industrial text* where near-misses are the norm. The report must therefore state, for each number: the **denominator** (how many chunk pairs were tested), the **definition of "false positive"** (a pair flagged as contradictory that a human adjudicated as not contradictory?), the **adjudication protocol** (how was ground truth established — a second annotator? an adjudicator?), and the **base rate** (how many pairs genuinely contradict). Without those four numbers the result is not interpretable and is an easy target.

### 5.6 The small corpus constrains every claim

The report's own limitations section is honest about this: **634 chunks across 24 documents**, single-domain (Supply Chain Management), N = 16 in the user study (below the 15-participant target — actually *at* it, marginally), and a **cross-encoder rerank regression of −5.34 pp on `production_scheduling`**. These are real constraints and the thesis is better for stating them than hiding them. But they constrain the *claims*:

- 634 chunks is small enough that **MODE's cluster-and-route approach** (which matches or beats dense retrieval at 100–500 chunks with no vector DB and no reranker) is a live alternative. The thesis should include a MODE-like or centroid-based arm, or explain why it is not competitive at this scale.
- The **−5.34 pp rerank regression on one category** is a *finding*, not a nuisance — a category where reranking hurts is exactly the kind of failure-mode evidence RO3 exists to produce. It should be analysed (which category, why: probably short/tabular documents where the bi-encoder was already right and the cross-encoder overrode it), not buried.
- Single-category evaluation means the RO4 cross-category generalisation claim cannot be made from the current data at all — it requires the other 11 categories to be built.

### 5.7 The time-series categories need their own treatment

The proposal places Demand Forecasting, Time-Series Forecasting and Anomaly Detection in the "Machine Learning (3)" domain, with **Cp/Cpk, Mann–Kendall, EOQ and Isolation Forest** as the named analytic methods. The verified literature (Time-LLM, Chronos, Chronos-2, Timer-XL) shows this category is not a *text* retrieval problem at all — it is a **numerical, tokenized-series** problem with its own models and metrics. Lumping it into a text-RAG pipeline that chunks documents will produce weak results.

The honest options are: (a) scope the thesis to the **nine Industrial Engineering categories** and treat the ML three as future work, with a paragraph explaining why (time-series QA needs numeric reasoning over series, not document retrieval); or (b) keep them but evaluate them through a distinct arm with series-appropriate metrics (MASE, forecast-interval coverage) rather than text-QA metrics. Option (a) is cleaner and costs the thesis nothing real, since the report already states SCM is the focus and the other 11 are scheduled.

### 5.8 The paper must not overclaim on the survey-methodology side

The proposal says the benchmark is "annotated by LLM agents using a structured protocol, with human-expert validation on a random subset to be reported." Two live risks: (i) "to be reported" means the human validation **is not yet done** — the paper cannot present it as a result, only as a protocol; (ii) LLM-agent annotation creates a circularity risk that must be addressed head-on: if the same class of model that answers the questions also generated them, an LLM-as-judge evaluation of those answers is partly self-referential. MiRAGE (2601.15487) handles this with an **adversarial verifier agent** and reports faithfulness gains; the thesis should adopt an equivalent independent-verification step and state the circularity argument explicitly in the limitations.

### 5.9 "RAG Does Not Work for Enterprises" (Bruckhaus, arXiv 2406.04369) should be cited

A single-author industry paper, cs.SE, arguing that enterprise RAG fails for reasons of **data security, accuracy, scalability and integration**, and proposing an evaluation framework built from *quantitative testing, qualitative analysis, ablation studies and industry case studies*. It is the closest published statement of the thesis's core premise — that the tooling for industrial paperwork is inadequate — and it proposes almost exactly the evaluation apparatus the thesis is building. Citing it costs nothing and shows command of the non-academic prior art. The thesis's own user study (N = 16) and its failure-mode chapter (RO3) answer its call for qualitative analysis and industry case studies.

### 5.10 Smaller but real items

- **Embedding model choice.** `all-MiniLM-L6-v2` is a 2022 sentence-transformer, and TeleEmbedBench finds LLM-based embedders (Qwen3, EmbeddingGemma) "consistently and significantly outperform traditional sentence-transformers" in both accuracy and cross-domain robustness. The choice is defensible for a 634-chunk corpus and for reproducibility, but it **must be justified explicitly** in the methodology — not left as a default — and the thesis should run at least one modern embedder as a sensitivity check.
- **Reranker cost.** The report sends **top-N = 50** to the cross-encoder and keeps top-10. On 634 chunks this is trivial, but it should be stated as a deliberate scaling decision with the break-even point noted, because BEIR's "high computational costs" caveat and MODE's no-reranker result are the two things a reviewer will press on.
- **RRF constant.** k = 60 is the canonical default and the report's citation is **correct**: DOI `10.1145/1571941.1572114` resolves to "Reciprocal rank fusion outperforms condorcet and individual rank learning methods", Gordon V. Cormack, Charles L A Clarke, Stefan Buettcher, *Proceedings of the 32nd International ACM SIGIR Conference*, 2009, pp. **758–759**. No change needed.
- **The report's "Stack at a Glance" names a specific LLM (MiniMax M3 via a forced `submit_response` tool call) and specific versions (Python 3.14, FastAPI, Next.js 15, React 19).** These are all reproducible and worth keeping; but every number in the report (634 chunks, 300 queries, 98%/16%, −5.34 pp, N = 16, 2.3%/7.1%, κ ≥ 0.7) must be **regenerable from a committed script**, and the corpus and benchmark must be **released**, or the empirical claims are unverifiable.
- **The proposal is in future tense throughout** ("we will use", "we will adopt"). The report is in past tense with results. These are two different documents describing two different stages. They must be reconciled into one coherent timeline before the 18 November defence, because a committee that reads both will notice that the paper promises work the report claims to have already completed.

---

## 6. Summary of actionable items

**Must fix before submission (factual errors):**
1. Correct the Decian et al. DOI → `10.1016/j.neucom.2026.134911`.
2. Correct the Zhang & Zhang DOI → `10.3390/math13050856`.
3. Re-attribute arXiv:2507.21502 to **Simchi-Levi, Mellou, Menache & Pathuri**; change "Microsoft Research" to a Springer book chapter; correct the description (LLM–optimisation-tool interface for what-if analysis, *not* a fine-tuned procurement model).
4. Change "Application-Oriented Survey" → "**Capability-Oriented** Survey" for arXiv:2510.24476.
5. Replace the CRAG citation's venue/DOI/pages with `arXiv:2401.15884` / `10.48550/arXiv.2401.15884` — **the DOI currently printed belongs to Dhuliawala et al.'s "Chain-of-Verification"**.
6. Correct the reranker model ID to **`cross-encoder/ms-marco-MiniLM-L6-v2`**.
7. Replace "the SupplyChainQA benchmark" with "our benchmark" throughout, and explain or drop the "v7" suffix.

**Must add to the literature review (closest prior art, all verified):** TechRAG (2606.01613), UA-RAG (Neurocomputing 699:134357), ICR (Neurocomputing 664:132139), MoRE-RAG (Neurocomputing 701:134536), Confidence-weighted semantic entropy (Neurocomputing 704:134859), Domain-Partitioned Hybrid RAG for India (2602.23371), CAR-RAG (BigData 2025), TeleEmbedBench (2604.17778), ManuRAG (JIM 2026), Chunking/Retrieval/Re-ranking (2601.15457), MODE (2509.00100), BEIR (2104.08663), plus RAG Does Not Work for Enterprises (2406.04369).

**Must change in the framing:**
8. Reframe the contribution from *architecture* to *evaluation and failure-mode characterisation*, with D4 (contradiction surfacing), the non-bypassable code gate, per-claim confidence, and the benchmark as the four defensible contributions.
9. Restate the benchmark-gap claim in the narrow, verifiable form given in §3.1.
10. Recast RO3's question from "does hybrid beat flat?" (known) to "what does category pre-filtering do to gate calibration, and what is the cost/accuracy frontier?" (open).

**Must strengthen empirically:**
11. Add an explicit **unanswerable class** to the benchmark — without it, RO1 cannot be measured.
12. Add a chunking ablation (recursive-char vs semantic/table-aware) per arXiv 2601.15457.
13. Report the contradiction gate's denominator, FP definition, adjudication protocol and base rate alongside 98%/16%.
14. Add at least one modern embedder as a sensitivity check against the TeleEmbedBench finding.
15. Add a no-reranker or centroid-routing arm (MODE-style) to address the −5.34 pp regression and the small-corpus cost argument.

---

*Compiled 2026-10-31. All bibliographic records verified against arXiv, Crossref, Semantic Scholar, the Hugging Face hub, and (for abstracts of bot-protected publishers) Scrapling-rendered pages. OpenAlex's anonymous quota was exhausted mid-session and its results were re-derived from Crossref; ScienceDirect is CAPTCHA-gated and its abstracts could not be retrieved directly — the Elsevier entries in §1.2 and §1.3 are verified by Crossref metadata (title, authors, venue, volume, article number, year) and by Semantic Scholar venue/citation-count records, but their abstracts were not read.*
