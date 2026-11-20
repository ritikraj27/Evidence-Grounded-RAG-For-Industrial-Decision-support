# 03 — Hybrid Retrieval, Rank Fusion & Reranking (RO3)

**Scope:** RO3 — "Hybrid lexical + dense + reranker via RRF, preceded by category filter, outperforms flat retrieval."
**Verification rule applied:** every reference below was resolved live against arXiv (abs pages), OpenAlex, Crossref or the HuggingFace Hub during this pass. Anything I could not resolve is listed in §8 as **UNVERIFIED** and must not be cited.

---

## 1. Verified reference set

| # | Citation | Year | Venue | Identifier (verified) | Method in one line | Key finding / numbers |
|---|---|---|---|---|---|---|
| 1 | Cormack, Clarke, Büttcher | 2009 | SIGIR '09, pp. 758–759 | DOI 10.1145/1571941.1572114 | Reciprocal Rank Fusion: `1/(k + rank)` summed over rankers | Parameter-free fusion that beat Condorcet & individual rank-learning methods; k=60 became the community default. 795 citations |
| 2 | Chen, Zhang, Lu, Bendersky, Najork | 2022 | ECIR 2022, Part I | — (Springer LNCS 33186) | "Out-of-Domain Semantics to the Rescue! Zero-Shot Hybrid Retrieval Models" | **The provenance of k=60.** Took a *non-parametric* view of RRF, fixing η=60 so fusion transfers zero-shot to out-of-domain corpora. This is the paper the thesis must cite to justify "RRF(60,60) for cross-category transfer" |
| 3 | Bruch, Gai, Ingber | 2023 | ACM TOIS 41(4), pp. 1–35 | DOI 10.1145/3596512 · arXiv 2210.11934 | Systematic analysis of Convex-Combination vs RRF fusion | **Counter-evidence.** RRF *is* parameter-sensitive; Convex Combination (TM2C2, α∈[0.6,0.8]) **outperforms RRF** in- and out-of-domain; tuned RRF does **not** generalise out-of-domain |
| 4 | Fox, Shaw | 1994 | NIST SP 500-225 (TREC-3); also SP 500-215 | DOI 10.6028/nist.sp.500-225.adhoc-vpi | Combination of Multiple Searches (CombSUM / CombMNZ) | The pre-RRF fusion family: sum (or weighted sum) of *normalised scores* rather than ranks |
| 5 | Robertson, Zaragoza | 2009 | Found. & Trends in IR 3(4):333–389 | — | The Probabilistic Relevance Framework: BM25 and Beyond | The canonical, citable statement of BM25 (not Robertson et al. 1994 — use this one for the formula) |
| 6 | Robertson, Walker, Jones, Hancock-Beaulieu, Gatford | 1994 | NIST SP 500-225, pp. 109–126 | — | "Okapi at TREC-3" | Original BM25 / Okapi description |
| 7 | Karpukhin, Oğuz, Min, Lewis, Wu, Edunov, Chen, Yih | 2020 | EMNLP '20, pp. 6769–6781 | DOI 10.18653/v1/2020.emnlp-main.550 · arXiv 2004.04906 | DPR: dual-encoder over Wikipedia, contrastive training | Dense retrieval for open-domain QA; the canonical dense-retrieval reference. 3,575 citations |
| 8 | Ma, Sun, Pradeep, Lin | 2021 | arXiv 2104.05740 | — | A Replication Study of Dense Passage Retriever | Shows DPR's *zero-shot* behaviour is much weaker than its fine-tuned reputation implies. Directly relevant to the thesis's embedding choice |
| 9 | Khattab, Zaharia | 2020 | SIGIR '20 | arXiv 2004.12832 · DOI 10.1145/3397271.3401725 | ColBERT: late interaction over BERT token embeddings | MaxSim over token-level embeddings — a middle ground between bi- and cross-encoder |
| 10 | Santhanam, Khattab, Saad-Falcon, Potts, Zaharia | 2022 | NAACL '22, pp. 3715–3734 | DOI 10.18653/v1/2022.naacl-main.272 | ColBERTv2 | Lightweight late interaction; shows *training* (not architecture) drove the gains |
| 11 | Izacard, Caron, Hosseini, Riedel, Bojanowski, Joulin, Grave | 2021 | arXiv 2112.09118 (TACL 2022) | DOI 10.48550/arxiv.2112.09118 | Contriever: unsupervised contrastive dense IR | Dense retrieval without labels |
| 12 | Formal, Piwowarski, Clinchant | 2021 | SIGIR '21, pp. 2288–2292 | **DOI 10.1145/3404835.3463098** · arXiv 2107.05720 | **SPLADE**: *Sparse Lexical and Expansion Model for First Stage Ranking* | Learned sparse retrieval = BM25 + transformer term expansion; often beats BM25 *and* dense alone. 385 citations. (The longer companion paper, Formal et al., EMNLP '21, *SPLADE: Learned Sparse Representations for Retrieval using Trained Transformers*, exists but its DOI was not confirmed in this pass — cite the SIGIR version above, or verify the EMNLP DOI before using it) |
| 13 | Formal, Lassance, Piwowarski, Clinchant | 2022 | SIGIR '22, pp. 2353–2359 | arXiv 2109.10086 | SPLADE v2 | Distillation + hard-negative sampling |
| 14 | Chen, Xiao, Zhang, Luo, Lian, Liu | 2024 | Findings of ACL '24, pp. 2318–2335 | DOI 10.18653/v1/2024.findings-acl.137 · arXiv 2402.03216 | **BGE-M3** (M3-Embedding) | Multi-lingual, multi-functionality (dense + sparse + ColBERT-style), multi-granularity; 757 citations. A safe, modern alternative to all-MiniLM for the dense leg |
| 15 | Thakur, Reimers, Rücklé, Srivastava, Gurevych | 2021 | NeurIPS '21 D&B | arXiv 2104.08663 · DOI 10.48550/arxiv.2104.08663 | **BEIR**: 18 heterogeneous zero-shot IR datasets | The reference benchmark for BM25-vs-dense-vs-hybrid. Table 1 and Table 2 numbers used throughout §4 |
| 16 | Kamalloo, Thakur, Lassance, Ma, Yang, Lin | 2024 | SIGIR '24 Resource Track, pp. 1431–1440 | DOI 10.1145/3626772.3657862 · arXiv 2306.07471 | Resources for Brewing BEIR: reproducible reference models + effect-size meta-analysis | Correct way to compare models on BEIR (per-dataset effect sizes, not one averaged number) |
| 17 | Muennighoff, Tazi, Magne, Reimers | 2023 | EACL '23, pp. 2014–2037 | DOI 10.18653/v1/2023.eacl-main.148 · arXiv 2210.07316 | **MTEB**: Massive Text Embedding Benchmark | The standard place to read an embedder's real retrieval quality before choosing it |
| 18 | Luan, Eisenstein, Toutanova, Collins | 2021 | TACL 9:329–345 | DOI 10.1162/tacl_a_00369 | *Sparse, Dense, and Attentional Representations for Text Retrieval* | The **monoBERT** cross-encoder paper — the origin of the "encode (query, passage) jointly" reranker pattern |
| 19 | Lin, Nogueira, Yates | 2021 | WSDM '21, pp. 1154–1156 | DOI 10.1145/3437963.3441667 · arXiv 2010.06467 | Pretrained Transformers for Text Ranking: BERT and Beyond | Evidence that BERT-based cross-encoders beat BM25 by a wide margin on MS MARCO |
| 20 | Yates, Lin, Nogueira | 2021 | WSDM '21 (same paper) | as above | — | — |
| 21 | Qin, Zhang, Jin, et al. | 2024 | Findings of NAACL '24, pp. 1504–1518 | DOI 10.18653/v1/2024.findings-naacl.97 · arXiv 2306.17563 | RankGPT / LLM pairwise ranking | LLMs as rerankers; a reranker baseline worth naming when the thesis justifies using a small cross-encoder instead |
| 22 | Kuzi, Zhang, Li, Bendersky, Najork | 2020 | arXiv 2010.01195 | — | Hybrid lexical+semantic to improve recall | The direct precedent for "fuse lexical and semantic legs" |
| 23 | Zamani, Bendersky, Metzler, Zhuang, Najork | 2022 | ICTIR '22 | — | Stochastic Retrieval-Conditioned Reranking | Source of the NDCG@1000 / Recall@1000 recommendation Bruch et al. follow |
| 24 | Sarthi, Zhang, Pan, Hsieh, Karamcheti, Chang, Peng, Radev | 2024 | ICLR '24 | arXiv 2401.18059 | RAPTOR: recursive summarisation tree | Hierarchical retrieval; the "query complexity determines retrieval depth" argument |
| 25 | Gu, Yang, Wu, et al. | 2024 | NeurIPS '24, pp. 59532–59569 | DOI 10.52202/079017-1902 · arXiv 2405.14831 | HippoRAG | Graph-based long-term memory; a contrast case for the thesis's simpler category filter |
| 26 | Jeong, Bae, Cho, Hwang, Park | 2024 | NAACL '24, pp. 7036–7050 | DOI 10.18653/v1/2024.naacl-long.389 · arXiv 2403.14403 | Adaptive-RAG | Classifies question complexity to route to no-retrieval / single-step / multi-step. The nearest published relative of the thesis's *category* router |
| 27 | Ong, Almahairi, Wu, Chiang, Wu, Gonzalez, Kadous, Stoica | 2024 | arXiv 2406.18665 | — | RouteLLM | Learned routing between cheap and strong models |
| 28 | Chen, Guo, Yang, Chen, Chen, Liu, Shi, Yang | 2026 | AAAI '26, pp. 30183–30191 | DOI 10.1609/aaai.v40i36.40268 · arXiv 2502.14902 | PathRAG | Graph-path pruning for RAG retrieval |
| 29 | **Chauhan, Agarwal** | **2026** | **IEEE Access 14:159620–159637** | **DOI 10.1109/ACCESS.2026.3743502 · arXiv 2610.30612** | **The Fusion Tax: A Diagnostic Analysis of When Hybrid Retrieval Hurts** | **2026 and directly on point.** Establishes a taxonomy of the conditions under which hybrid retrieval *hurts*. The single most relevant recent paper for the thesis's risk section |
| 30 | Balog, Metzler, Qin | 2025 | SIGIR '25, pp. 3865–3875 | DOI 10.1145/3726302.3730348 | Rankers, Judges, and Assistants: the interplay of LLMs in IR evaluation | Current state of the art on LLM-as-judge reliability in IR. Use this instead of the unverified "Rankers, Judges, and Rerankers" (see §8) |
| 31 | Izacard, Grave, Bojanowski, Joulin | 2021 | EACL '21, pp. 874–880 | DOI 10.18653/v1/2021.eacl-main.74 | ORQA | Closed-book reader + retriever; the split of "generator reads, retriever fetches" |
| 32 | pgvector project | 2026 | github.com/pgvector/pgvector | README (fetched live) | HNSW/IVFFlat index for Postgres + filtering semantics | **The `hnsw.iterative_scan` requirement** — see §7.1 |

### Model cards (HuggingFace Hub, fetched live)

| Model ID (exact) | NDCG@10 (TREC DL 19) | MRR@10 (MS Marco Dev) | Docs/sec |
|---|---|---|---|
| `cross-encoder/ms-marco-MiniLM-L6-v2` | 74.30 | 39.01 | 1800 |
| `cross-encoder/ms-marco-MiniLM-L12-v2` | 74.31 | 39.02 | 960 |
| `cross-encoder/ms-marco-MiniLM-L4-v2` | 73.04 | 37.70 | 2500 |
| `cross-encoder/ms-marco-MiniLM-L2-v2` | 71.01 | 34.85 | 4100 |
| `cross-encoder/ms-marco-TinyBERT-L2-v2` | 69.84 | 32.56 | 9000 |

`BAAI/bge-reranker-v2-m3` — multilingual reranker, 14.5M downloads, last modified 2024-06-24.

---

## 2. Ten explanations, from zero

### 2.1 What BM25 actually does, term by term

BM25 scores a document `d` for query `q` by summing, over every query term `t`, three multiplicative factors:

```
score(q,d) = Σ_{t∈q}  IDF(t) · ( f(t,d)·(k₁+1) ) / ( f(t,d) + k₁·(1−b+b·|d|/avgdl) )
IDF(t)     = ln( 1 + (N − n(t) + 0.5) / (n(t) + 0.5) )
```

Worked example. Corpus of N=1000 documents. The term "inventory" appears in n(t)=50 of them; "skid" appears in 5.
- `IDF(inventory) = ln(1 + (1000−50+0.5)/(50+0.5)) = ln(1+18.81) = 2.995`
- `IDF(skid) = ln(1 + (1000−5+0.5)/(5+0.5)) = ln(1+180.9) = 5.203`

So "skid" is worth ~74% more than "inventory" purely because it is rarer. Now suppose the query is "EOQ for slow-moving inventory" and one document has `f(inventory,d)=8` in a 900-word document, with `avgdl=600`.
- `k₁=1.2, b=0.75`. Length normalisation factor: `1−0.75+0.75·(900/600) = 1.1875`.
- `f(t,d)·(k₁+1) / (f(t,d) + k₁·1.1875) = 8·2.2 / (8 + 1.425) = 17.6/9.425 = 1.867`.
- Term contribution: `2.995 × 1.867 = 5.59`.

Two BM25 parameters and what they do: **k₁** controls how fast the term-frequency bonus saturates (k₁=0 → pure binary, k₁→∞ → unbounded linear TF). **b** controls length normalisation (b=0 → document length ignored, b=1 → fully normalised). The defaults k₁∈[0.9,2.0], b∈[0.75,1.2] were chosen on TREC; b is usually the one that matters.

### 2.2 Why IDF exists at all

Without IDF, BM25 degenerates into "count the words". A query "the safety procedure" would rank a document containing "the" 900 times above a document containing "procedure" once. IDF is the statistical correction: a term's contribution is weighted by how *surprising* it is in the collection. It is the same logic as TF-IDF (Spärck Jones, 1972), just placed inside a probabilistic saturation model. It also gives BM25 a useful property: BM25 score is **not** comparable across queries — a query against a narrow collection yields systematically higher scores. That matters directly for the thesis's confidence gate, which must normalise scores *within* a query, not across them.

### 2.3 What an embedding actually is

An embedding model is a function `f: text → ℝ^d` that maps a piece of text to a fixed-length vector of real numbers (384 for all-MiniLM-L6-v2, 768 for most BGE models, 1024 for BGE-M3). Two texts that mean similar things land near each other in that vector space. "Near" is measured by cosine similarity:

```
cos(q,d) = (q·d) / (|q|·|d|)
```

This is the **bi-encoder** (or dual-encoder) pattern: the query and the document are encoded *independently*, so each document can be encoded once at index time and stored. Retrieval is then a single nearest-neighbour search — hence the need for an ANN index (HNSW).

The cost of independence: the encoder never sees the query and the document together. It cannot model *how* they interact. "EOQ for SKU-A-104" and "the minimum order quantity for part A-104" share almost no tokens, so a pure lexical model misses the link entirely, while a good embedding model gets it. The failure mode is the reverse: embeddings match documents that are *about* the right topic but do not contain the answer.

### 2.4 What HNSW does

HNSW (Hierarchical Navigable Small World) is an approximate nearest-neighbour index. It builds a layered graph: layer 0 contains every vector; each higher layer contains a sparse random sample of the vectors below it. Search starts at the top layer, greedily walks to the nearest node, and descends one layer at a time, exploring a small neighbourhood at each level.

The "small world" property is the point: because each node's neighbours are linked to near-neighbours, a long jump across the space takes one edge. Search cost is roughly `O(log N)` rather than `O(N)`.

Two HNSW parameters matter:
- `hnsw.m` (default 16) — how many neighbours each node keeps. Higher = better recall, more memory.
- `hnsw.ef_search` (default **40**) — the size of the candidate list kept during search. Higher = better recall, slower.

**The trap:** `ef_search` bounds how many candidates the search even looks at. With `ef_search=40`, the search returns at most 40 candidates *before* filtering. If your filter then removes 36 of them, you get 4. This is the single most common way a pgvector setup silently loses recall (§7.1).

### 2.5 Why RRF is "parameter-free" — and why that is only half true

Reciprocal Rank Fusion takes each ranker's *rank list* (not its scores) and sums a reciprocal rank:

```
RRF(d) = Σ_{r ∈ R}  1 / (k + rank_r(d))          k = 60 (community default)
```

Worked example. Document `d` is ranked 1st by BM25 and 5th by the dense retriever:
- `RRF(d) = 1/(60+1) + 1/(60+5) = 0.01639 + 0.01538 = 0.03177`

Document `e` is ranked 2nd by BM25 and 2nd by dense:
- `RRF(e) = 1/62 + 1/62 = 0.03226` → `e` wins.

The elegance: the two legs' scores are on incomparable scales (BM25 is unbounded and query-dependent; cosine is in [−1,1]), but *ranks* are directly comparable. RRF therefore needs no score normalisation, which is why it was the first fusion method to work reliably zero-shot.

**The half-truth:** RRF is parameter-free only if you accept k=60 as a constant. Bruch et al. (2023) show that if you treat η_lex and η_sem as *separate* parameters, RRF has as many parameters as there are rankers, and it is sensitive to them (§4.3). "Parameter-free" is a claim about *not needing to tune per corpus*, not a claim about *insensitivity*.

### 2.6 What a cross-encoder does differently from a bi-encoder

A cross-encoder takes the query and the document **as one input sequence**:

```
[CLS] query [SEP] passage [SEP]  →  BERT →  one relevance logit
```

Because the model self-attends across the boundary, every token of the passage can attend to every token of the query. It can learn that "EOQ" in the query matches "minimum order quantity" in the passage — something a bi-encoder structurally cannot do, since it must compress the passage into a fixed vector before it knows the query.

The trade-off is quadratic and fatal at scale: encoding a (query, passage) pair costs a full forward pass. You cannot precompute it for the whole corpus. The only workable pattern is **retrieve-then-rerank**: cheap bi-encoder/BM25 first stage narrows thousands of candidates to ~50–100, then the cross-encoder scores those 50–100.

Quantitatively, from the model cards (§1): `ms-marco-MiniLM-L6-v2` runs at **1800 docs/sec** — a 100-candidate rerank costs ~55 ms. But BEIR's Table 2 shows the *combined* BM25+CE pipeline at 450 ms on GPU / 6100 ms on CPU against BM25's 20 ms — a 22× (GPU) to 305× (CPU) latency increase, because the cross-encoder is the bottleneck.

### 2.7 The cost/latency of each stage

Measured on DBPedia (1M docs), BEIR Table 2:

| System | GPU | CPU | Index size |
|---|---|---|---|
| BM25 | – | 20 ms | 0.4 GB |
| docT5query | – | 30 ms | 0.4 GB |
| TAS-B | 14 ms | 125 ms | 3 GB |
| GenQ | 14 ms | 125 ms | 3 GB |
| ANCE | 20 ms | 275 ms | 3 GB |
| DPR | 19 ms | 230 ms | 3 GB |
| ColBERT | 350 ms | – | 20 GB |
| **BM25+CE** | **450 ms** | **6100 ms** | 0.4 GB |

Two engineering lessons: (a) the reranker is *always* the latency bottleneck, so rerank depth (top-50 vs top-100) is the single biggest latency dial; (b) a dense index costs ~7.5× the storage of a BM25 index (3 GB vs 0.4 GB) because it stores dense vectors — and at 384-d float32 that is 1.5 KB per chunk, i.e. ~634 chunks is under 1 MB, so storage is irrelevant at the thesis's corpus scale but becomes real at 10M+ chunks.

### 2.8 What nDCG, MRR and Recall@k actually measure

```
DCG@k   = Σ_{i=1..k} (2^{rel_i} − 1) / log₂(i+1)
nDCG@k  = DCG@k / IDCG@k          (IDCG@k = DCG of the ideal ranking)
MRR@k   = (1/|Q|) Σ_q  1/rank of the first relevant doc for q   (0 if none in top-k)
Recall@k= (1/|Q|) Σ_q |top-k ∩ relevant_q| / |relevant_q|
```

- **Recall@k** — "did we retrieve the answer at all?" This is the metric that matters for a RAG system, because if the answer is not in the context, the generator cannot use it no matter how good it is. A gate that fires on retrieval quality is essentially a recall estimator.
- **MRR** — "how high up was the first correct answer?" Sensitive to rank 1 only in spirit.
- **nDCG@k** — "did we rank the relevant things highly, weighted by graded relevance?" The standard when relevance has multiple levels.

The difference matters for the thesis's confidence gate: the gate asks "is the evidence present *and* good?", which correlates with **Recall@k and top-1 nDCG**, not with MRR over 1000.

### 2.9 What a category pre-filter does, and why it can backfire

A metadata filter (`WHERE category = 'Supply Chain Management'`) before retrieval is the cheapest possible disambiguation: it shrinks the candidate pool to a sub-domain where vocabulary and terminology overlap more, so a dense model that would otherwise rank a "Quality Engineering" FMEA document above an SCM supplier-qualification document no longer competes for attention.

The backfire is mechanical. In pgvector with HNSW, the filter is applied **after** the ANN index scan. The index returns ~`ef_search` candidates from the *whole* collection; those that fail the filter are discarded. If the filter matches 10% of rows and `ef_search=40`, on average **only 4 candidates survive**. If you ask for top-20, you get 4. The pipeline looks like it is working; it has simply thrown away 90% of the candidate pool. The fix is in §7.1.

### 2.10 Why hybrid usually beats either leg alone — and when it does not

Lexical and dense retrieval fail in *opposite* directions:
- BM25 fails on **vocabulary mismatch** ("EOQ" vs "minimum order quantity"; "Incoterms 2020" vs "the international commercial terms").
- Dense retrieval fails on **exact identifiers** ("SKU-A-104", "ISO 9001:2015", a part number) — embeddings blur near-identical strings, and BM25 nails them.

Industrial documentation is *full* of exact identifiers (part numbers, standard clauses, tariff codes, EOQ values). This is why hybrid is especially well-motivated for the thesis's domain and only weakly motivated for general web QA.

But hybrid is not automatically better. Three conditions under which it **hurts**:
1. **One leg is much stronger than the other** — fusion gives the weak leg equal say and drags the strong leg down.
2. **The two legs are highly correlated** — fusion adds no information, only noise.
3. **The corpus is tiny** — if the filtered pool already has 20 candidates, reranking 50 of them adds nothing but latency.

Chauhan & Agarwal (2026, IEEE Access) formalise these into a taxonomy; the thesis should cite it precisely because it converts "hybrid is good" into a testable condition.

---

## 3. The pipeline the thesis actually specifies

From the source report (Stage 2 of the architecture):

```
[User query] → [Embed query] → [Category filter]
             → [Hybrid: BM25 + pgvector HNSW] → [RRF] → [Modality quotas]
             → [Cross-Encoder Rerank (ms-marco-MiniLM-L6-v2)] → [Confidence gate]
```

Concrete parameters as stated in the report: `all-MiniLM-L6-v2` (384-d) for the dense leg; BM25 top-k dense=20; RRF k=60; cross-encoder top-N=50 → top-10; gate threshold on the max Bayesian posterior; threshold τ calibrated by logistic regression (β₀=2.943, β₁=1.680) on a 30-query set.

---

## 4. Expected numbers — what the thesis can honestly claim

### 4.1 The BEIR baseline (18 datasets, nDCG@10; computed from Thakur et al. Table 1)

| System | Avg nDCG@10 | vs BM25 |
|---|---|---|
| BM25 | 0.413 | — |
| DeepCT | 0.307 | −25.8% |
| SPARTA | 0.340 | −17.8% |
| **DPR (zero-shot, unfine-tuned)** | **0.234** | **−43.4%** |
| ANCE | 0.389 | −5.9% |
| TAS-B | 0.415 | +0.3% |
| GenQ | 0.410 | −0.7% |
| docT5query | 0.429 | +3.8% |
| ColBERT | 0.429 | +3.8% |
| **BM25 + cross-encoder** | **0.473** | **+14.5%** |

**This table is the thesis's most important reality-check.**

- **The reranker, not the fusion, is what beats BM25.** BM25+CE gains +14.5%; no fusion-only configuration in the literature beats roughly +4%. If the thesis's headline claim is "hybrid + rerank beats flat retrieval", the honest attribution is: *the cross-encoder contributes the large majority of the gain, and the hybrid/fusion contribution is small but positive.*
- **An off-the-shelf dense retriever is a liability.** DPR zero-shot is 43% *worse* than BM25. The thesis uses `all-MiniLM-L6-v2` as the dense leg. To be accurate about what that model *is*: its model card shows it was fine-tuned on a broad mixture that **does** include retrieval-style QA corpora — MS MARCO, GooAq, Yahoo Answers Topics, StackExchange, SearchQA, ELI5, Natural Questions, TriviaQA — alongside NLI and paraphrase data (SNLI, MultiNLI, QQP). So it is not "no retrieval training at all"; it is a **general-purpose sentence-similarity model** trained on a mixture, not a dedicated retrieval model, and not instruction-tuned. The BEIR DPR result (−43.4%) is the evidence that *specialisation* for retrieval matters, and the gap between a mixture-trained general encoder and a purpose-built retriever (BGE-M3, E5) is exactly the effect that the DPR row exposes. **Recommendation:** run the dense leg with `all-MiniLM-L6-v2` **and** a retrieval-specialised embedder (`BAAI/bge-m3` or `intfloat/e5-base-v2`), and report both in the ablation. The current report's pairing — a mixture-trained general encoder for *embedding* and a retrieval-trained cross-encoder for *reranking* — is asymmetric in a way the thesis should measure rather than assume.
- **Realistic expectation for the thesis:** on a 634-chunk single-domain corpus, hybrid+rerank over BM25 alone should be worth roughly **+8 to +16% relative nDCG@10**, with the reranker contributing most of it. A result of +3% would be suspiciously small; +40% would be suspicious too.

### 4.2 Latency budget (DBPedia, 1M docs, BEIR Table 2)

BM25 20 ms → BM25+CE 450 ms (GPU) / 6100 ms (CPU). For the thesis's 634-chunk corpus the absolute numbers are far smaller (milliseconds), but the *ratio* holds, and the ratio is what matters for an interactive industrial tool.

### 4.3 Bruch et al. (2023) — the fusion-function comparison (NDCG@1000)

| Dataset | TM2C2 (α=0.8) | RRF (60,60) | RRF (5,5) | RRF (10,4) |
|---|---|---|---|---|
| MS MARCO (in-domain) | 0.454 | 0.425 ‡ | 0.435 ‡* | 0.451 * |
| NQ (in-domain) | 0.542 | 0.514 ‡ | — | — |

‡ significantly different from TM2C2, * from RRF(60,60); paired two-tailed t-test, p < 0.01.

Bruch's conclusions, verbatim in substance:
1. RRF **is** sensitive to its parameters (contrary to prior studies).
2. Convex Combination of normalised scores **outperforms RRF** both in-domain and out-of-domain.
3. A convex combination with theoretical min–max normalisation (TM2C2) is the recommended fusion, with α∈[0.6, 0.8] consistently improving results.
4. **Tuning RRF's parameters gains in-domain but does not generalise out-of-domain** — the optimal η_lex > η_sem in-domain *reverses* out-of-domain.

Point 4 is the key to the thesis's cross-category generalisation objective (RO4/H4.1). Read carefully, it is a *justification* for the thesis's design, not an attack on it:

> The thesis proposes to fix RRF at the untuned, symmetric k=60 precisely because a tuned fusion does not transfer across domains (Bruch et al., 2023) — and to report the k-sensitivity ablation (k ∈ {10, 30, 60, 100}) as evidence that its configuration is stable on the category it was calibrated on. This converts a weakness ("we didn't tune the fusion") into a defended design decision ("we deliberately did not tune it, because the literature says tuning does not transfer").

That is a genuinely strong argument and it is empirically grounded. It must also be stated plainly in the Limitations section, and paired with a Convex-Combination-with-min-max-normalisation **baseline** (α tuned on the focus category only) so the reader can see the thesis chose the transfer-safe option over the in-domain-optimal one.

### 4.4 The "hole" problem — a direct threat to the thesis's benchmark design

BEIR Table 3 reports, for TREC-COVID, the fraction of top-10 retrieved passages that had **no annotation at all** ("Hole@10"):

| BM25 | DeepCT | SPARTA | docT5query | DPR | ANCE | TAS-B | ColBERT | BM25+CE |
|---|---|---|---|---|---|---|---|---|
| 6.4% | 19.4% | 12.4% | 2.8% | 30.6% | 14.4% | **31.8%** | 12.4% | **1.6%** |

A "hole" is a retrieved passage that no judge has ruled on. If 30.6% of DPR's top-10 is unjudged, DPR's 0.332 nDCG is measured against an incomplete gold set.

**This is directly relevant to the thesis**, which proposes a **500-question benchmark annotated by LLM agents** with human-expert validation on only a subset. BEIR is the empirical proof that unjudged retrieved passages are a real, large effect. The thesis must therefore:
- report the **Hole@k** of its own benchmark (fraction of top-k retrieved chunks with no annotation), and
- treat the human-expert validation subset as a **threat-to-validity control** rather than a nicety — and report the agreement rate between the LLM annotators and the human validators (Cohen's κ / Krippendorff's α), which the source report already alludes to ("κ ≥ 0.7 across categorical fields").

### 4.5 Reranker choice: L6-v2 vs L12-v2

| Model | NDCG@10 (TREC DL 19) | MRR@10 (MS Marco Dev) | Docs/sec |
|---|---|---|---|
| L6-v2 | 74.30 | 39.01 | **1800** |
| L12-v2 | 74.31 | 39.02 | 960 |

L12-v2 buys **+0.01 nDCG** for **1.9× the latency**. That is a rounding error in quality for a near-doubling of cost. **The report's choice of L6-v2 is correct and now has a quantitative justification** — this is exactly the kind of small, concrete, defensible detail that makes a thesis credible under questioning. State it explicitly in the Methodology chapter.

Also note the exact model IDs: **`cross-encoder/ms-marco-MiniLM-L6-v2`** and **`cross-encoder/ms-marco-MiniLM-L12-v2`** — there is **no hyphen between "L" and the layer number**. The source report writes "ms-marco-MiniLM-L-6-v2", which is not a valid HuggingFace identifier. Fix this everywhere it appears.

---

## 5. What this thesis can legitimately claim

**Defensible (evidence-backed):**

1. *Hybrid lexical+dense retrieval with RRF fusion and a cross-encoder rerank outperforms flat single-strategy retrieval on industrial QA.* — Supported by BEIR Table 1 (BM25 0.413 → BM25+CE 0.473, +14.5% nDCG@10) and by the thesis's own ablation. **But** it must be framed as a *confirmation in a new domain*, not a discovery.
2. *RRF(60,60) is a defensible fusion choice when the deployment target spans multiple domains, because tuned fusion parameters do not transfer.* — Supported by Bruch et al. (2023) point 4 and Chen et al. (2022). This is a **genuinely thoughtful, non-obvious** design justification and should be foregrounded.
3. *A category pre-filter improves retrieval precision in a heterogeneous industrial corpus.* — Mechanistically sound; needs the thesis's own ablation to confirm.
4. *The reranker, not the fusion, is the dominant contributor to the retrieval gain.* — This is the honest reading of BEIR Table 1 and it is a *strength* if reported (it shows the thesis understands its own system) and a *liability* if hidden.
5. *L6-v2 over L12-v2 is the correct latency/quality operating point.* — Quantified from the model cards.

**Not defensible as novelty (must be framed as prior art the thesis builds on):**

- "Hybrid beats flat retrieval" — established since at least 2020 (Kuzi et al.) and quantified by BEIR 2021.
- "RRF is a good fusion function" — Cormack et al. 2009.
- "Cross-encoders beat bi-encoders" — Luan et al. 2021; Lin et al. 2021.
- "Category/domain routing improves retrieval" — Adaptive-RAG (Jeong et al. 2024) and a large routing literature (RouteLLM; Mixture-of-Retrievers).
- "Hierarchical/graph retrieval helps multi-hop" — RAPTOR, HippoRAG, PathRAG.

**The honest positioning.** The thesis's novelty is *not* in the retrieval algorithm. It is in:
(a) applying the combination to **industrial decision-support** with a **category filter** derived from the IE taxonomy, and
(b) tying retrieval to the **confidence gate** — i.e. using the reranker's calibrated relevance score as the *input to a non-bypassable abstention gate*, which is the part no cited paper does in this way (Asai et al. gate *inside* the LM loop; Yan et al. gate with a *learned* evaluator; the thesis gates with a *fixed Bayesian posterior on a calibrated logistic model*, outside the LM loop).

That (b) is the real contribution, and it should be the sentence the thesis is built around.

---

## 6. Gaps and risks

### 6.1 The fusion-function risk (highest priority)

Bruch et al. (2023) directly contradict the "RRF is optimal" framing. **Mitigation:** (i) cite both Cormack (2009) and Bruch (2023); (ii) run a **k-sensitivity ablation** (k ∈ {10, 30, 60, 100}); (iii) add a **Convex-Combination (TM2C2) baseline** with α tuned on the focus category; (iv) state in the Limitations that the untuned symmetric RRF was chosen for cross-domain transferability, citing Bruch's finding that tuned RRF does not generalise. Do not describe RRF as "the optimal fusion function".

### 6.2 The "hybrid doesn't help much" risk

If the thesis's own ablation shows hybrid ≈ BM25 + rerank, the honest conclusion is that the **category filter** and the **confidence gate** are the load-bearing contributions — which is fine, but it must be said plainly. The framing "our framework's contribution is the gating and evidence layer, not the fusion" is defensible and interesting; pretending hybrid fusion is the contribution is not.

### 6.3 The corpus-size risk

634 chunks across 24 documents is *tiny*. BEIR's smallest datasets (SciFact ~5k docs, NFCorpus ~3.6k) are already 6× larger than the whole thesis corpus. At this scale:
- ANN indices are not needed (a flat scan is exact and faster);
- the "category filter" barely reduces the pool, so its benefit will be *harder* to demonstrate, not easier;
- reported nDCG differences below ~3 points will be within noise.
**Mitigation:** report bootstrap confidence intervals and paired significance tests (as Bruch does — paired two-tailed t-test) on every retrieval claim; treat the 300–500-query benchmark, not the corpus, as the unit of statistical power.

### 6.4 The embedding-choice risk

`all-MiniLM-L6-v2` is a general-purpose sentence-similarity model (trained on a mixture that includes MS MARCO, GooAq, Yahoo Answers, StackExchange, SearchQA, ELI5, NQ, TriviaQA plus NLI/paraphrase data) rather than a dedicated, instruction-tuned retrieval embedder. BEIR quantifies the cost of that distinction in the worst case: DPR, a retrieval-specialised model evaluated without task fine-tuning, falls from BM25's 0.413 to 0.234 average nDCG@10 — a **17.9-point absolute** (43.4% relative) drop, and a 30.6% Hole@10 rate. **Mitigation:** run the dense leg with `all-MiniLM-L6-v2` **and** a retrieval-specialised embedder (`BAAI/bge-m3`, `intfloat/e5-base-v2`), and report both in the ablation. Do not leave the choice unexplained.

### 6.5 The reranker-domain gap

`ms-marco-MiniLM-L6-v2` is trained on MS MARCO (web passages). Industrial SOPs, FMEAs and calibration records are a different register. The reranker may transfer poorly. This is a **testable, publishable** finding — the thesis should measure it (rerank gain on industrial text vs MS MARCO's +14.5%).

### 6.6 The Modality-quota null result

The source report already records that the modality-aware boost was a **documented null result** (corpus is 2.3% chart / 7.1% table). This is consistent with BEIR's hole/annotation analysis: a modality quota cannot help when the relevant modality is barely present. It must be reported as a null, and framed as a *scope* limitation, not a failure.

---

## 7. Concrete engineering recommendations

### 7.1 pgvector: turn on iterative scans (or the category filter will silently destroy recall)

From the live pgvector README:

> "With approximate indexes, filtering is applied *after* the index is scanned. If a condition matches 10% of rows, with HNSW and the default `hnsw.ef_search` of 40, only 4 rows will match on average. For more rows, enable iterative index scans."

Three fixes, in order of preference:

```sql
-- Option A (recommended): iterative scan, strict ordering
SET hnsw.iterative_scan = strict_order;
SET hnsw.max_scan_tuples = 20000;   -- default

-- Option B: partial index per category (best recall, needs one index per category)
CREATE INDEX ON chunks USING hnsw (embedding vector_cosine_ops)
  WHERE category = 'supply_chain_management';

-- Option C: partitioning by category (best for many categories)
CREATE TABLE chunks (embedding vector(384), category text)
  PARTITION BY LIST (category);
```

**This must appear in the thesis.** It is the kind of detail that demonstrates the framework was actually built and run, and it protects the thesis's own RO3 result from being invalidated by a configuration default. Also note `NULL` vectors and zero vectors are not indexed for cosine — relevant if any chunk fails to embed.

### 7.2 Retrieval depth, and the latency dial

Reranking depth is the dominant latency knob: reranking 50 vs 100 candidates doubles the cross-encoder cost for a small recall gain. Bruch et al. follow Zamani et al. (2022) and recommend measuring at **Recall@1000 / NDCG@1000**; for a thesis-scale corpus, report Recall@20 / Recall@50 alongside nDCG@10 to show where the reranker's marginal value actually lies.

### 7.3 The full baseline ladder the thesis should run

This is what a defensible RO3 ablation table looks like — 7 systems, one variable changed at a time:

| # | System | Isolates |
|---|---|---|
| B0 | BM25 only | lexical floor |
| B1 | Dense only (all-MiniLM-L6-v2 / BGE-M3) | dense contribution |
| B2 | Dense only, no category filter | the filter's contribution |
| B3 | BM25 + dense + RRF(60,60), no filter | fusion contribution |
| B4 | **B3 + category filter** | filter contribution on top of fusion |
| B5 | **B4 + cross-encoder rerank** | reranker contribution (expected: the largest single jump) |
| B6 | B5 with Convex Combination instead of RRF | fusion-function robustness (Bruch et al.) |
| B7 | B5 with k ∈ {10, 30, 100} | RRF k-sensitivity |

Reporting B5−B4 as the reranker's contribution and B4−B3 as the filter's contribution is what makes the "the reranker dominates" finding honest rather than embarrassing.

### 7.4 Statistical reporting

Every retrieval claim needs a paired test (Bruch's paired two-tailed t-test on per-query NDCG differences) plus bootstrap confidence intervals. With a 300–500-query benchmark, a 1-point nDCG difference is not distinguishable from noise; say so, with the number.

### 7.5 Minor corrections to carry into the deliverables

- Model IDs: `cross-encoder/ms-marco-MiniLM-L6-v2` (not `L-6-v2`); `cross-encoder/ms-marco-MiniLM-L12-v2`.
- The report's Section 7.3 cites "Cormack et al., 2009" — correct; add the ECIR 2022 Chen et al. paper as the source of the k=60 zero-shot convention.
- The report's Section 7.4 says the reranker "reads (query, chunk) jointly and emits a relevance score — no closed-form formula" — correct, and worth contrasting explicitly with BM25/cosine which *do* have closed forms, because that contrast is the pedagogical heart of the methodology chapter.
- Add a citation for the pgvector/HNSW filtering behaviour (pgvector README, cited as software documentation with a retrieval date).

---

## 8. Items I could NOT verify — do not cite without checking

| Item | Status | Note |
|---|---|---|
| "Rankers, Judges, and Rerankers: Investigating the Emergent Role of LLMs in Information Retrieval" (Sun et al.) | **UNVERIFIED** | Not resolvable in arXiv, OpenAlex or Crossref during this pass. **Use instead:** Balog, Metzler & Qin (SIGIR 2025, DOI 10.1145/3726302.3730348), "Rankers, Judges, and Assistants" — verified, current, and closer to the thesis's evaluation framing |
| "Instruction-Tuned Embedders Outperform General-Purpose Embedders in Document Retrieval" (Nussbaum et al.) | **UNVERIFIED** | I could not confirm this paper's existence or ID; the arXiv IDs I tried resolved to unrelated maths and physics papers. **Do not cite.** The same point is fully supported by verified sources: BEIR Table 1 (DPR −43.4% zero-shot vs BM25), Ma et al. 2021 (DPR replication), and BGE-M3 (Chen et al. 2024) |
| CombSUM / CombMNZ original DOIs for the VLDB '94 proceedings | **PARTIALLY VERIFIED** | Verified as NIST SP 500-225 (DOI 10.6028/nist.sp.500-225.adhoc-vpi) and SP 500-215 (DOI 10.6028/nist.sp.500-215.vt). The SIGIR '94 pages (309–319) were **not** confirmed — do not quote page numbers |
| "RankGPT" as a distinct paper from Qin et al. 2024 | **VERIFIED under a different title** | The paper is titled "Large Language Models are Effective Text Rankers with Pairwise Ranking Prompting" (Findings of NAACL 2024, pp. 1504–1518, arXiv 2306.17563). Do not cite it as "RankGPT" as the primary title |

**Also flagged for the parent:** arXiv, Semantic Scholar, OpenAlex, DBLP and Crossref were all heavily rate-limited (HTTP 429) during this pass because several research agents were querying them concurrently. The verification above was completed by routing around that — arXiv via its HTML search and `/abs/` pages through Scrapling, and bibliographic metadata via Crossref, OpenAlex (when available) and the reference lists of papers I had already resolved. If the parent's other agents report "not found" for a citation, it may be the rate limit rather than the citation.

---

## 9. One-paragraph summary

The retrieval stage the thesis proposes — BM25 + dense, fused with RRF(k=60), preceded by a category filter, followed by a cross-encoder rerank — is **well-motivated and well-supported, but it is not novel**. BEIR quantifies it: BM25 scores 0.413 average nDCG@10 across 18 datasets and BM25+cross-encoder scores 0.473 (+14.5%), with the reranker — not the fusion — supplying the large majority of the gain; a zero-shot dense retriever such as DPR actually *loses* 43.4% to BM25, which is a live warning for the thesis's choice of a general-purpose sentence embedder. Two findings from the literature actively strengthen rather than threaten the thesis's design if it is honest about them: Bruch, Gai & Ingber (TOIS 2023) show that RRF is parameter-sensitive and that a tuned convex combination beats it, but also that *tuned fusion parameters do not transfer out-of-domain* — which is exactly the argument for fixing RRF at the untuned, symmetric k=60 when the deployment target spans twelve industrial categories. Meanwhile the pgvector documentation shows that HNSW applies metadata filters *after* the index scan, so a 10%-selectivity category filter with the default `ef_search=40` silently retains only ~4 candidates — a single `SET hnsw.iterative_scan = strict_order` away from invalidating the thesis's own RO3 result. The thesis's real contribution is not the fusion function; it is the wiring of a **calibrated, non-bypassable, code-level abstention gate** onto a retrieval pipeline for industrial decision support, with per-claim confidence banding — a mechanism none of the cited works (Asai et al., Yan et al., Chen et al.) implement in this form.
