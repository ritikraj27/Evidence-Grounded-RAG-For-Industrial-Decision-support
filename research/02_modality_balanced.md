# RO2 — Modality-Balanced Retrieval: Literature Verification and Analysis

**Scope.** Verification and analysis of the prior art behind the thesis's second research
objective: *per-modality retrieval quotas* that enforce a minimum share of tables, charts and
images in the retrieved context, so that text chunks do not crowd out tabular evidence in
industrial corpora.

**Verification protocol.** Every paper below was retrieved from the arXiv Atom API, Crossref
REST API or DBLP during this review, and the arXiv identifier, DOI, author list and venue
below were checked against what those services actually returned. Titles, author lists and
abstract text are quoted or paraphrased from retrieved abstracts. Where a venue could not be
confirmed through Crossref or the arXiv `comment`/`journal_ref` fields, the paper is listed as
an **arXiv preprint** and no venue is asserted. **No citation in this file is inferred from
memory.**

> Note on one thesis-proposal citation: the proposal's literature-review table lists
> "Faysse et al. (2025) — ColPali: Efficient Document Retrieval with Vision Language Models".
> This paper is real and the attribution is correct, but it is **not a 2025 arXiv preprint** —
> arXiv 2407.01449 was first submitted **27 June 2024**, and its arXiv comment reads
> *"Published as a conference paper at ICLR 2025"*. The correct citation is
> **Faysse et al. (2024/2025), arXiv:2407.01449, ICLR 2025**. The same row also lists the DOI
> as `10.48550/arXiv.2407.01449`; that DOI is the arXiv-issued DataCite DOI, which is correct
> only if the thesis does not also want the ICLR proceedings DOI. Use the ICLR venue.

---

## 1. Verified paper table

| # | Paper | Authors (first + et al.) | Year | Venue (verified) | arXiv / DOI | Method (one line) | Key finding with numbers |
|---|---|---|---|---|---|---|---|
| 1 | **ColPali: Efficient Document Retrieval with Vision Language Models** | Faysse, Sibille, Wu, Omrani, Viaud, Hudelot, Colombo | 2024 (ICLR 2025) | ICLR 2025 (arXiv comment) | arXiv:2407.01449 | Embeds **page images** with a VLM into many multi-vector patch embeddings; scores with late interaction (MaxSim). | Introduces the **ViDoRe** benchmark (page-level visual document retrieval, multiple domains/languages). Reports ColPali "largely outperforms modern document retrieval pipelines" while being simpler/faster and end-to-end trainable. No single headline number in the abstract. |
| 2 | **Reproducibility, Replicability, and Insights into Visual Document Retrieval with Late Interaction** | Qiao, Ju, Ma, Kanoulas, Yates | 2025 | arXiv preprint | arXiv:2505.07730 | Re-evaluates ColPali-style VDR across several pre-trained VLMs, with and without late interaction. | Confirms late interaction "yields considerable improvements in retrieval effectiveness" but "introduces computational inefficiencies during inference"; finds query tokens **cannot explicitly match image patches** the way text queries match text, so the text-retrieval intuition does not transfer. |
| 3 | **ColMate: Contrastive Late Interaction and Masked Text for Multimodal Document Retrieval** | Masry, Thakkar, Bechard, Madhusudhan, Awal, Mishra, … | 2025 | EMNLP 2025 Industry Track, DOI 10.18653/v1/2025.emnlp-industry.145 | arXiv:2511.00903 | New OCR-based pretraining objective + self-supervised masked contrastive learning + a late-interaction score tailored to multimodal document structure. | **+3.61 %** over existing retrieval models on **ViDoRe V2**, with stronger generalisation to out-of-domain benchmarks. |
| 4 | **ModernVBERT: Towards Smaller Visual Document Retrievers** | Teiletche, Macé, Conti, Loison, Viaud, Colombo, … | 2025 | arXiv preprint | arXiv:2510.01149 | Systematic study of the visual-document-retrieval training recipe (attention masking, image resolution, modality-alignment data, late-interaction contrastive objectives). | A **250 M-parameter** VLM encoder that **outperforms models up to 10× larger** when fine-tuned for document retrieval; runs on cheap CPU hardware, cutting latency and cost. |
| 5 | **VisRAG: Vision-based Retrieval-augmented Generation on Multi-modality Documents** | Yu, Tang, Xu, Cui, Ran, Yan, … | 2024 | arXiv preprint | arXiv:2410.10594 | Embeds the **document image itself** with a VLM (no text extraction) and feeds retrieved page images to a VLM generator. | **20–40 % end-to-end performance gain** over a traditional text-based RAG pipeline, by eliminating the information loss introduced during parsing. |
| 6 | **VisDoM: Multi-Document QA with Visually Rich Elements Using Multimodal RAG** | Suri, Mathur, Dernoncourt, Goswami, Rossi, Manocha | 2025 | NAACL 2025, DOI 10.18653/v1/2025.naacl-long.310 | arXiv:2412.10704 | **VisDoMBench** (first multi-document QA benchmark with tables, charts, slides); VisDoMRAG runs textual and visual retrieval **concurrently** with a *consistency-constrained modality fusion* mechanism that aligns reasoning across modalities. | Improves accuracy "in scenarios where critical information is distributed across modalities" and improves **answer verifiability through implicit context attribution**; beats unimodal and long-context LLM baselines end-to-end. |
| 7 | **SCAN: Semantic Document Layout Analysis for Textual and Visual RAG** | Ueda, Dong, Boros, Ito, Sera, Oyamada | 2026 | EACL 2026 Findings, DOI 10.18653/v1/2026.findings-eacl.82 | arXiv:2505.14381 | Detects document regions at *semantic* granularity (contiguous coherent components) by fine-tuning object detectors; feeds both a text RAG and a visual RAG pipeline. | **+9.4 points** end-to-end on textual RAG and **+10.4 points** on visual RAG, outperforming conventional approaches *and commercial document-processing solutions*, on English and Japanese datasets. |
| 8 | **T²-RAGBench: Text-and-Table Benchmark for Evaluating RAG** | Strich, Kutay Isgorur, Trescher, Biemann, Semmann | 2026 | EACL 2026, DOI 10.18653/v1/2026.eacl-long.8 | arXiv:2506.12071 | **23 088** question–context–answer triples over real-world text-and-table data; deliberately *not* Oracle-context, so the model must retrieve first. | **91.3 %** of questions validated by experts as context-independent. Their sweep finds **Hybrid BM25** (dense + sparse fused) the most effective approach for text-and-table data. The benchmark "remains challenging even for SOTA LLMs". |
| 9 | **FreshStack: Building Realistic Benchmarks for Evaluating Retrieval on Technical Documents** | Thakur, Lin, Havens, Carbin, Khattab, Drozdov | 2025 | NeurIPS 2025, DOI 10.52202/085713-5255 | arXiv:2504.13128 | Automatic IR-benchmark construction from code + technical documentation: corpus collection → nugget generation from community Q&A → nugget-level support via hybrid retrieval. | On five fresh/niche topics, out-of-the-box retrieval models "significantly underperform oracle approaches" on **all five**. Crucially: they identify **cases where rerankers do not improve first-stage retrieval accuracy (2 of 5 topics)** — a direct external corroboration of the thesis's own reranker regression result. |
| 10 | **VisR-RAG-Fin: Benchmarking Multimodal RAG over Visually Rich Financial Documents** | El Bachyr, Bernardy, Ezzini, Klein, Bissyandé, Mont'e, … | 2026 (Oct) | arXiv preprint | arXiv:2610.24822 | Open-source benchmark for page-level QA over visually rich financial documents, built by a general pipeline that **preserves original layout and visual content**. | Systematic analysis of retrieval and generation behaviour under **text-only, multimodal and hybrid** configurations — i.e. it is the closest published template for the thesis's own modality ablation. |
| 11 | **TableRAG: A RAG Framework for Heterogeneous Document Reasoning** | Yu, Jian, Chen | 2025 | EMNLP 2025, DOI 10.18653/v1/2025.emnlp-main.710 | arXiv:2506.10380 | Semantic-aware chunking over heterogeneous documents (text, tables, layout), with a module that reasons over the retrieved structure. | One of the few papers that treats **table and text as heterogeneous first-class items** rather than flattening tables to text before retrieval. Cited 18× (Crossref, at time of check). |
| 12 | **TableRAG: Million-Token Table Understanding with Language Models** | Chen, Miculicich, Eisenschlos, Wang | 2024 | arXiv preprint | arXiv:2410.04739 | Table-specific pretraining and a table-aware prompting scheme for million-token table inputs. | Establishes that tables require **dedicated representation and reasoning**, not merely text serialisation — the direct precedent for treating a table as a distinct retrieval modality. |
| 13 | **Late Chunking: Contextual Chunk Embeddings Using Long-Context Embedding Models** | Günther, Mohr, Williams, Wang | 2024 | EMNLP 2024 *(venue not Crossref-confirmed; cite by arXiv id)* | arXiv:2409.04701 | Encode the *whole document* with a long-context embedding model first, then mean-pool **per token** to produce each chunk's embedding — the chunk inherits the document's context. | Establishes that chunk embeddings need not be computed independently: contextualising chunks after document-level encoding improves retrieval. Directly relevant if the thesis wants table captions to carry their page context. |
| 14 | **RAPTOR: Recursive Abstractive Processing for Tree-Organized Retrieval** | Sarthi, Abdullah, Tuli, Khanna, Goldie, Manning | 2024 | ICLR 2024 *(venue not Crossref-confirmed; cite by arXiv id)* | arXiv:2401.18059 | Recursively embeds, clusters and summarises chunks bottom-up into a tree of levels of abstraction; at inference retrieves from the **whole tree**, integrating information across documents at different levels of abstraction. | "Retrieval with recursive summaries offers significant improvements over traditional retrieval-augmented LMs"; coupled with GPT-4 it improves the best QuALITY benchmark performance by **20 % in absolute accuracy**, with state-of-the-art results on multi-step reasoning tasks. |
| 15 | **OmniDocBench: Benchmarking Diverse PDF Document Parsing with Comprehensive Annotations** | Ouyang, Qu, Zhou, Zhu, Zhang, Lin, … | 2025 | CVPR 2025, DOI 10.1109/cvpr52734.2025.02313 | arXiv:2412.07626 | Annotations across **9 document sources** (papers, textbooks, handwritten notes, dense newspapers), **19 layout categories**, **15 attribute labels**; end-to-end and attribute-level evaluation. | The standard yardstick for parsing quality; shows both pipeline-based and end-to-end VLM parsers have document-type-specific weaknesses. Cited 40×. |
| 16 | **Document Parsing Unveiled: Techniques, Challenges, and Prospects** | Zhang, Wang, Huang, Zhang, Wang, Liang, … | 2024 | arXiv preprint | arXiv:2410.21169 | Survey separating **modular pipeline systems** (layout analysis + per-type recognition) from **unified VLM models**. | Names the open challenges that bound any modality-aware thesis claim: robustness to complex layouts, reliability of VLM-based parsing, inference efficiency. |
| 17 | **RAGBench: Explainable Benchmark for RAG Systems** | Friel, Belyi, Sanyal | 2024 | arXiv preprint | arXiv:2407.11005 | **100 k** examples across **five industry-specific domains** and several RAG task types, sourced from industry corpora such as user manuals; the **TRACe** explainable metric framework. | The largest industrial-domain RAG benchmark located in this review, and its "explainable, actionable" metric design is the pattern the thesis's per-claim diagnostics should follow. |
| 18 | **HiChunk: Evaluating and Enhancing RAG with Hierarchical Chunking** | Lu, Chen, Qiao, Sun | 2026 | ACL 2026, DOI 10.18653/v1/2026.acl-long.1372 | arXiv:2509.11552 | Shows existing RAG benchmarks cannot measure chunking quality because of **evidence sparsity**; introduces **HiCBench** (manually annotated multi-level chunking points) + a fine-tuned multi-level structuring framework with an Auto-Merge retrieval algorithm. | Directly relevant: if the thesis wants to defend chunk-level modality quotas, it needs a chunking-aware benchmark, because the effect cannot be separated from chunking effects otherwise. |
| 19 | **MRAG-Suite: A Diagnostic Evaluation Platform for Visual RAG** | Ji, Lan, Ng | 2025 | arXiv preprint | arXiv:2509.24253 | Integrates WebQA, Chart-RAG, Visual-RAG and MRAG-Bench; adds **difficulty-based and ambiguity-aware filtering** and **MM-RAGChecker**, a claim-level diagnostic tool. | Finds "substantial accuracy reductions under difficult and ambiguous queries, highlighting prevalent hallucinations" — i.e. claim-level diagnostics are only trustworthy on ambiguity-filtered subsets. |
| 20 | **A Survey of Multimodal RAG** | Mei, Mo, Yang, Chen | 2025 | arXiv preprint | arXiv:2504.08748 | Survey of MRAG components, datasets, evaluation and limitations. | States MRAG "outperforms traditional RAG, especially in scenarios requiring both visual and textual understanding" — the premise the thesis's modality claim rests on. |
| 21 | **Ask in Any Modality: A Comprehensive Survey on Multimodal RAG** | Abootorabi, Zobeiri, Dehghani, Mohammadkhani, Mohammadi, Ghahroodi, … | 2025 | arXiv preprint | arXiv:2502.08826 | Full survey: datasets, benchmarks, metrics, evaluation, retrieval, **fusion**, augmentation, generation, training strategies, agentic approaches. | Identifies **cross-modal alignment and reasoning** as the challenges unique to MRAG beyond unimodal RAG — the formal statement of why "just retrieve more modalities" is not sufficient. |
| 22 | **Scaling Beyond Context: A Survey of Multimodal RAG for Document Understanding** | Gao, Zhao, Jiang, Duan, Chng, Chen, … | 2025 | arXiv preprint | arXiv:2510.15253 | Taxonomy by domain, retrieval modality and granularity; covers graph structures and agentic frameworks, datasets, benchmarks, industry deployment. | Argues OCR-based pipelines "lose structural detail" while native MLLMs "struggle with context modelling" — the exact tension a modality-aware retrieval layer mediates. |
| 23 | **DocVQA: A Dataset for VQA on Document Images** | Mathew, Karatzas, Jawahar | 2021 | WACV 2021, DOI 10.1109/wacv48630.2021.00225 | arXiv:2007.00398 | **50 000 questions** defined on **12 000+ document images**; detailed comparison against other VQA and reading-comprehension datasets; several VQA/reading-comprehension baselines. | Existing models perform reasonably on some question types but leave a large gap to **human performance of 94.36 %**; the gap is concentrated on questions "where understanding structure of the document is crucial". Cited 546×. |
| 24 | **InfographicVQA** | Mathew, Bagal, Pérez Tito, Karatzas, Valveny, Jawahar | 2022 | WACV 2022, DOI 10.1109/wacv51458.2022.00264 | arXiv:2104.12756 | A diverse collection of infographics with natural-language question/answer annotations; questions "require methods to jointly reason over the document layout, textual content, graphical elements, and data visualizations", curated to require elementary reasoning and basic arithmetic. | Establishes baseline performance with two strong multi-modal VQA baselines. Cited 212×; the reference point for "charts and diagrams are not a solved problem". *(The abstract does not state the image/question counts — do not quote dataset sizes from memory; read them from the paper's dataset section.)* |
| 25 | **ChartQA: A Benchmark for QA about Charts with Visual and Logical Reasoning** | Masry, Long, Tan, Joty, Hoque | 2022 | Findings of ACL 2022, DOI 10.18653/v1/2022.findings-acl.177 | arXiv:2203.10244 | **9.6 K human-written** questions plus **23.1 K generated from human-written chart summaries**; two transformer models that **combine visual features and the data table of the chart in a unified way**. | State-of-the-art on previous datasets and on the benchmark, but the evaluation "reveals several challenges in answering complex reasoning questions". Cited 452×. |
| 26 | **SlideVQA: A Dataset for Document VQA on Slides** | Li, … | 2023 | AAAI 2023, DOI 10.1609/aaai.v37i11.26598 | — | Multi-slide document VQA over slide decks with complex layouts and embedded figures. | Cited 70×; shows slide-level layout is a distinct retrieval problem from page-level text. |
| 27 | **MMLongBench-Doc: Benchmarking Long-context Document Understanding** | Li, Liu, Feng, … | 2024 | NeurIPS 2024, DOI 10.52202/079017-3041 | — | Long-document understanding with text, tables, charts and images; reports accuracy, retrieval quality and long-context model performance. | Cited 36×; provides the retrieval-vs-long-context comparison the thesis needs to show that retrieval still beats stuffing context. |
| 28 | **Hierarchical Patch Compression for ColPali (HPC-ColPali)** | Bach | 2025 | arXiv preprint | arXiv:2506.21601 | K-Means quantisation of patch embeddings to 1-byte centroid indices, attention-guided dynamic pruning, optional binary encoding for Hamming search. | Up to **32× storage reduction**; **60 % less late-interaction computation** with < 2 % nDCG@10 loss; in a legal-summarisation RAG pipeline it **reduced hallucination rate by 30 %** and halved end-to-end latency. |
| 29 | **VisRAG2.0 / EVisRAG: Mitigating Visual Hallucinations via Evidence-Guided Multi-Image Reasoning** | Sun, Peng, Yan, Yu, Liu, Mei, … | 2025 | arXiv preprint | arXiv:2510.09733 | Observes each retrieved image first, **records question-relevant visual evidence per image**, then reasons over the aggregated evidence; RS-GRPO aligns rewards with token spans per stage. | Outperforms the backbone VLM by **~19 % on average** across multiple VQA benchmarks while "substantially reducing visual hallucinations" — the evidence-collection-then-reason pattern the thesis mirrors at claim level. |
| 30 | **When Image and Text Disagree: Cross-Modal Evidence Conflict…** | — | 2026 | 2nd Workshop on Multimodal Augmented Generation, DOI 10.18653/v1/2026.magmar-main.3 | — | Detects and characterises **cross-modal conflict** (image text vs. surrounding text disagreeing). | Bridges the thesis's D4 (contradiction surfacing) and RO2 (modality balance): disagreement is not only between documents but between modalities of the same document. |

**Venue note.** Where a DOI is shown it was returned by Crossref for that exact title, or read
from the paper's own arXiv abstract page. Rows listed as "arXiv preprint" (13, 14, 17, 20, 21,
22, 28) had no Crossref-confirmed venue at the time of this review — cite them by arXiv
identifier rather than asserting a venue.

---

## 2. Deep explanations of the ten most important papers

### 2.1 ColPali (arXiv:2407.01449, ICLR 2025) — the reference visual retriever

ColPali attacks a specific weakness of conventional RAG pipelines. When you build a vector
index, you must first turn the document into text, and that step is lossy: a table becomes a
run of tokens that no longer says "this is a row, this is a header, this number is the value of
that column"; a chart's shape, colour and axis labels are simply gone; the spatial relation
between a caption and the figure it describes is destroyed. ColPali's answer is to skip text
extraction entirely. It feeds the **rendered page image** into a vision-language model and
asks the model to emit one embedding vector *per image patch* — so a single page becomes
hundreds of small vectors rather than one long string of tokens. At query time it does the same
for the question, then scores the page with a **late-interaction** (MaxSim) operation: for each
query token vector, take the maximum similarity against all page-patch vectors, then sum. A
query token does not have to align with a page token; it only has to align with *somewhere* on
the page. This is what lets a natural-language question match a chart's visual structure. The
paper also introduced **ViDoRe**, a benchmark of page-level visual document retrieval tasks
spanning several domains and languages, precisely because the community had no way to measure
this. The trade-off is storage and compute: a page with 1 030 patches at 128 dimensions is
roughly 130 k floats, orders of magnitude more than a text chunk. The follow-up work in §1
(rows 2, 3, 4, 28) is largely about keeping late interaction while reducing that bill.

### 2.2 VisRAG (arXiv:2410.10594) — the same idea pushed through the whole pipeline

VisRAG makes the OCR-free argument at *pipeline* level rather than retriever level. Its claim is
that parsing loss is not a retriever problem but a pipeline problem: even a perfect retriever
cannot recover information that was destroyed before indexing. So VisRAG embeds document images
with a VLM, retrieves page images, and hands those *images* to a VLM generator — the generator
reads the same pixels the retriever saw. The reported result is a **20–40 % end-to-end
performance gain** over a traditional text-based RAG pipeline, which is large enough to change
the engineering decision: if your corpus is visually rich, do not build a text index at all.
The counter-evidence matters equally for an industrial thesis: the gain comes from *keeping the
visual channel*, not from *balancing* it. Nothing in VisRAG forces a table to be retrieved when
the query is a table question — it improves what you can see, not what you choose to look at.

### 2.3 VisDoM / VisDoMRAG (arXiv:2412.10704, NAACL 2025) — the closest prior art to the thesis's RO2

VisDoM is the single most important paper for this thesis's novelty position, and it should be
read in full before the defence. It introduces **VisDoMBench**, described by its authors as the
first comprehensive benchmark for QA over *multiple* documents containing visually rich
elements — tables, charts and presentation slides — which is exactly the regime the thesis
claims to address. Its VisDoMRAG system runs a textual retrieval pipeline and a visual
retrieval pipeline **concurrently**, then fuses them with what the authors call a
**consistency-constrained modality fusion** mechanism: the reasoning traces from the two
modalities are constrained to agree before a final answer is produced. Two consequences
follow. First, the thesis's "modality-balanced retrieval" is not the first attempt to make
multi-modal retrieval work; it is a re-framing of an existing problem, and the paper must say
so. Second — and this is the opening — VisDoMRAG fuses *after* retrieval and constrains
*consistency*, whereas the thesis proposes to constrain the *composition of the retrieved set*
by quota, before generation. That is a genuine architectural difference, but it is a difference
of mechanism, not of goal, and the thesis must argue it as such rather than claiming the goal.

### 2.4 T²-RAGBench (arXiv:2506.12071, EACL 2026) — the benchmark the thesis should build on

T²-RAGBench is built around one design decision that should be copied. Most text-and-table QA
datasets are *context-dependent*: the same question has different correct answers depending on
which context you were given. That makes them useless for evaluating a RAG system, because the
system is judged on retrieval and the gold answer silently depends on it. T²-RAGBench's
authors transform state-of-the-art datasets into a **context-independent** format, and validate
that transformation with experts — **91.3 %** of questions confirmed context-independent. The
benchmark contains **23 088** question–context–answer triples and, unlike the usual Oracle-context
setting, forces the model to retrieve the correct context *before* numerical reasoning. Two
results matter for this thesis: the benchmark remains "challenging even for SOTA LLMs", and the
authors' retrieval sweep identifies **Hybrid BM25** — dense and sparse fused — as the most
effective approach on text-and-table data. That is independent, third-party support for the
thesis's RO3 hybrid-retrieval design, and it comes from a benchmark specifically built around
mixed text-and-table evidence.

### 2.5 FreshStack (arXiv:2504.13128, NeurIPS 2025) — why rerankers sometimes hurt

FreshStack matters for a result the thesis's own report records but cannot yet explain: the
cross-encoder reranker *regressed* retrieval quality by 5.34 points on the `production_scheduling`
category. FreshStack's authors looked for the same phenomenon across five fresh technical topics
and report that they "identify cases where rerankers do not improve first-stage retrieval
accuracy (two out of five topics)". Their explanation of the gap is that existing retrieval
models, applied out of the box, significantly underperform oracle approaches on all five
topics — i.e. the first-stage recall is the bottleneck, and a reranker cannot recover a document
the first stage never returned. A reranker that reorders a bad candidate list faithfully
preserves the badness. This gives the thesis a defensible, citable framing for its reranker
regression: it is not an implementation bug but a known property of reranking on heterogeneous
corpora, and it is a *finding*, not a failure.

### 2.6 SCAN (arXiv:2505.14381, EACL 2026 Findings) — semantic granularity beats fixed chunking

SCAN's premise is that "a single page contains large amounts of information" and that naive
fixed-size chunking therefore destroys document structure before retrieval ever starts. It
proposes identifying document components at **coarse-grained semantic** granularity — "coherent
regions covering contiguous components" — by fine-tuning an object-detection model on an
annotated dataset. The numbers are the point: applying SCAN improves end-to-end textual RAG by
**up to 9.4 points** and visual RAG by **up to 10.4 points**, and it does so while
"outperforming … even commercial document processing solutions". For the thesis this is a
two-edged result. It supports the design move of making chunking *structure-aware* rather than
fixed-length, which is what makes a "table chunk" a meaningful unit to quota against. It also
warns that any measured "modality quota" effect is confounded with chunking quality unless the
corpus and chunker are held fixed across arms — which is exactly what the thesis's ablation
must do.

### 2.7 Late Chunking (arXiv:2409.04701) and RAPTOR (arXiv:2401.18059) — two ways to give a chunk more context

These two papers solve related problems with opposite philosophies, and both bear on the
thesis's design.

*Late Chunking* keeps the chunker simple (fixed windows) but changes how embeddings are
computed. Instead of encoding each chunk in isolation, you encode the **whole document** with a
long-context embedding model and then mean-pool the token vectors belonging to each chunk. The
chunk's embedding therefore inherits the document's context — a chunk that is the third row of
a specifications table now carries the table's heading in its vector space. For the thesis this
is directly useful: a modality quota is only meaningful if chunks are comparable across
modalities, and contextualised embeddings make "the safety-stock row" and "the safety-stock
paragraph" land near each other.

*RAPTOR* keeps the embedding function ordinary and instead builds a **recursive tree of
summaries** over the corpus, retrieving over both leaf chunks and internal summary nodes. It
excels on thematic and recursive questions ("what are the main themes?"). For the thesis it
suggests a design that is currently unused: the category pre-filter (D3) is a *hard, flat*
routing rule; a summary node per category would make it *soft* — the router retrieves a
category summary plus that category's chunks, so a cross-category question can still be
answered. It also raises the honest question of whether a flat category filter should be
compared against a hierarchical index rather than only against flat retrieval.

### 2.8 ChartQA (arXiv:2203.10244, Findings of ACL 2022) — why the chart's table matters

ChartQA's premise is that chart questions are hard for two separate reasons: they involve
"several logical and arithmetic operations", and they "commonly refer to visual features of a
chart". Existing datasets missed this because their questions were template-based with
fixed-vocabulary answers. The benchmark therefore pairs **9.6 K human-written questions** with
**23.1 K questions generated from human-written chart summaries**, and — the detail that
matters for this thesis — the two models they present "combine visual features and the data
table of the chart in a unified way to answer questions". That is, the winning configuration
uses **both representations of the same chart simultaneously**.

The lesson for the thesis is precise: in industrial documents, the same information usually
exists twice — as a rendered chart *and* as the table it was drawn from. A retrieval system
that treats only the table as retrievable may be able to answer chart questions correctly, and
one that treats only the rendered chart as retrievable may be able to answer them correctly
*when the renderer preserved the labels*. The interesting industrial question is not "can you
read charts" but "**which representation of the same fact should the retriever prefer, and
does your corpus contain both?**" That is a better framing for the thesis's RO2 than a raw
modality quota, and it is directly testable.

### 2.9 OmniDocBench (arXiv:2412.07626, CVPR 2025) — the ceiling on any modality claim

Any claim about modality-balanced retrieval is really a claim about *what the parser preserved*.
OmniDocBench measures exactly that: it annotates **nine document sources** — academic papers,
textbooks, handwritten notes, densely typeset newspapers — with **19 layout categories** and
**15 attribute labels**, and evaluates parsing both end-to-end and attribute-by-attribute. Its
finding that matters here is that both pipeline-based methods and end-to-end VLM parsers have
document-type-specific weaknesses; no parser is uniformly best.

Two implications. First, the thesis's corpus composition (industrial manuals, standards
documents, spreadsheets) determines which parser to use, and the choice must be defended
against OmniDocBench's per-type breakdown rather than asserted. Second, if the parser flattens
a table into prose, then a modality quota has nothing to allocate — there are no table chunks.
**Parsing fidelity is a precondition for the modality experiment**, and the thesis should say
so explicitly rather than presenting the quota as a self-contained improvement.

### 2.10 MRAG-Suite (arXiv:2509.24253) — how to diagnose a modality effect honestly

MRAG-Suite's contribution is methodological and it directly addresses a weakness in how
modality claims are usually evaluated. It integrates four multimodal benchmarks (WebQA,
Chart-RAG, Visual-RAG, MRAG-Bench) and then applies **difficulty-based and ambiguity-aware
filtering** before scoring. The result of that filtering is the important finding:
accuracy drops "substantially under difficult and ambiguous queries, highlighting prevalent
hallucinations". MRAG-Suite also ships **MM-RAGChecker**, a claim-level diagnostic tool.

The implication for the thesis's RO2 evaluation is concrete. If a modality quota changes which
chunks are in context, it will help most on queries whose evidence lives in the
previously-underrepresented modality, and it will *hurt* on queries whose evidence lives in
text, because the quota displaces text chunks. Reporting a single aggregate recall number
hides exactly the structure the thesis needs to show. MRAG-Suite's difficulty/ambiguity
stratification is the tool for showing it.

---

## 3. Practical recipe: a working industrial multimodal ingestion + retrieval pipeline

All library versions below were verified against the live PyPI JSON API on 2026-10-31.

### Stage A — Ingestion (offline, per document)

1. **Parse with layout awareness, not text extraction.**
   - `docling` **v2.145.0** — "SDK and CLI for parsing PDF, DOCX, HTML, and more, to a unified
     document representation". IBM's parser is layout-aware and emits a structured document
     tree (headings, paragraphs, tables as *tables*, pictures) with positions.
   - `marker-pdf` **v2.1.0** — "Convert documents to markdown with high speed and accuracy";
     the fastest path to high-fidelity markdown for RAG.
   - `unstructured` **v0.27.36** — "A library that prepares raw documents for downstream ML tasks";
     broad format coverage with per-element metadata (element type, page number).
   - `pymupdf` **v2.0** — "A high performance Python library for data extraction, analysis,
     conversion & manipulation"; use for page rasterisation when a *visual* index is wanted.
   - Evaluate your choice against **OmniDocBench (CVPR 2025)**, per document type, not in the
     abstract. For an industrial corpus, hand-check 50 tables and 20 charts and measure what
     fraction of cell values survive parsing. **Do not proceed to the modality experiment until
     this number is acceptable** — a quota over unparsed tables is a quota over nothing.

2. **Keep two channels per document.**
   - *Text channel*: text chunks, each tagged with `modality ∈ {text}`.
   - *Visual/table channel*: for each page, (a) a rendered image for a VLM-embedding index and
     (b) a structured table object serialised to markdown/CSV, tagged `modality ∈ {table}`;
     chart captions, legends and axis labels tagged `modality ∈ {chart}`.
   - **Record the page and section provenance on every chunk** (`source_doc`, `page`,
     `bbox`, `modality`, `header_path`). Without provenance you cannot cite, cannot
     deduplicate across channels, and cannot measure a quota's effect.

3. **Chunk with structure awareness.**
   - Fixed-size windows are the baseline; *Late Chunking* (arXiv:2409.04701) is the
     low-cost upgrade (document-level encoding, per-chunk pooling).
   - *SCAN* (arXiv:2505.14381) is the stronger option when layout is complex.
   - Keep the chunker **identical across all ablation arms**. Any modality effect measured
     with a chunker that differs between arms is uninterpretable — this is exactly the
     confound *HiChunk* (arXiv:2509.11552) exists to expose.

### Stage B — Indexing

4. **Dense index.** `sentence-transformers` **v6.2.0** ("Embeddings, Retrieval, and
   Reranking") with `sentence-transformers/all-MiniLM-L6-v2` (384-d, verified live on
   HuggingFace: ~186 M downloads) is the cheap default; `BAAI/bge-reranker-base` and
   `jinaai/jina-embeddings-v2-base-en` are verified alternatives. Store vectors in
   **PostgreSQL + `pgvector` v0.5.1** with an HNSW index, exactly as the thesis's architecture
   already specifies — pgvector's HNSW is a graph index that gives sub-linear search over
   hundreds of thousands of vectors with no separate vector database to operate.

5. **Sparse index.** `rank-bm25` **v0.2.2** ("Various BM25 algorithms for document ranking") for
   the lexical leg. For a stronger hybrid, `FlagEmbedding` **v1.4.2** provides BGE-M3's
   sparse/dense/multi-vector representations and its own reranker. Note T²-RAGBench's finding
   that **Hybrid BM25** was the strongest retriever on text-and-table data — the thesis's
   hybrid design has independent support.

6. **Visual index (optional, high effort).** `colpali-engine` **v0.3.18** ("The code used to
   train and run inference with the ColPali architecture") gives late-interaction page
   embeddings. Budget for the storage cost: **HPC-ColPali** (arXiv:2506.21601) achieves up to
   **32× storage reduction** and **60 % less late-interaction computation** with < 2 % nDCG@10
   loss — without such compression, a 24-document corpus is fine but a production corpus is
   not. For a thesis-scale corpus, plain ColPali is acceptable; say so explicitly and quantify
   the storage.

### Stage C — Retrieval (online, per query)

7. **Filter, then retrieve, then fuse, then rerank, then quota.**
   - Category pre-filter (D3) narrows the candidate pool first — it is a *routing* decision,
     and it makes the subsequent ranking cheaper.
   - Run dense and lexical legs; fuse with **Reciprocal Rank Fusion** (Cormack et al. 2009,
     k = 60).
   - Rerank the fused top-N with a cross-encoder. Verified model id:
     **`cross-encoder/ms-marco-MiniLM-L6-v2`** (≈68.9 M downloads).
     ⚠️ **Correction needed in the thesis report:** the report currently writes
     `ms-marco-MiniLM-L-6-v2`. The correct HuggingFace identifier has **no hyphen between
     "L" and "6"** — `ms-marco-MiniLM-L6-v2`. As written it will fail to resolve.
   - **Apply the modality quota last, on the reranked list.** The quota must be the final
     composition step; applying it before reranking lets the reranker undo it.

8. **Measure the quota's effect per stratum, not in aggregate.** Use MRAG-Suite's
   difficulty/ambiguity stratification and report recall on table-evidenced queries and
   text-evidenced queries separately. Report the *displacement* cost as well as the gain.

### Stage D — Evaluation

9. `ragas` **v0.4.3** ("Evaluation framework for RAG and LLM applications") for faithfulness,
   context precision and answer relevancy; the thesis already names RAGAS.
   For citation quality, use NLI-based precision/recall of citations in the style of ALCE
   (Gao et al. 2023). For a text-and-table-specific sweep, **T²-RAGBench** (23 088 triples,
   91.3 % expert-validated context-independence) is the right instrument. For realistic
   industrial-document retrieval, **FreshStack** and **RAGBench** (100 k examples, five
   industry domains) are the right external references.

---

## 4. What this thesis can claim

### 4.1 The claim that survives

**"Modality-aware *composition* of the retrieved set — enforced as a hard quota at the last
stage, in a code path that cannot be bypassed — improves evidence-grounded answers in
industrial Q&A."**

This claim is defensible because:

- The underlying premise is established: MRAG beats text-only RAG where queries need visual
  evidence (arXiv:2504.08748; VisRAG's 20–40 % end-to-end gain, arXiv:2410.10594).
- The mechanism is distinct from the closest prior art in a way that can be argued: VisDoMRAG
  (NAACL 2025) constrains *consistency across modalities after retrieval*; the thesis
  constrains *which modalities are present in the retrieved set before generation*.
- The tooling to build it is standard and reproducible (Docling/ColPali/pgvector/BM25 +
  RRF + a cross-encoder), so the claim is falsifiable.

### 4.2 The claim that is at risk

**"Modality-balanced retrieval is a new contribution."** It is not, and the thesis must not say
it is. The prior art is:

| Prior work | What it already does | Date |
|---|---|---|
| VisDoMRAG (arXiv:2412.10704, NAACL 2025) | Concurrent textual + visual retrieval with consistency-constrained **modality fusion** | Dec 2024 / NAACL 2025 |
| TableRAG (arXiv:2506.10380, EMNLP 2025) | Treats text and tables as **heterogeneous** first-class retrieval objects | Jun 2025 |
| VisR-RAG-Fin (arXiv:2610.24822) | Benchmarks **text-only vs multimodal vs hybrid** configurations on visually rich documents | Oct 2026 |
| Ask in Any Modality (arXiv:2502.08826) | Surveys **fusion** as a first-class MRAG research dimension | Feb 2025 |
| ChartQA (arXiv:2203.10244) | Publishes the **underlying table** for every chart — making table-vs-image retrieval an explicit choice | Mar 2022 |

The defensible novelty is **narrower and better**: the *mechanism* (a hard, non-bypassable
per-modality quota applied after reranking), the *domain* (industrial decision support), the
*evidence trail* (per-claim confidence that says which modality supported which claim), and
the *empirical honesty* about when it does not help.

### 4.3 The claim the thesis should make instead

The strongest version of this contribution is not "we retrieve more tables". It is:

> In industrial corpora the same fact frequently appears in **two representations** — a rendered
> chart and the table it was drawn from (ChartQA), or a prose paragraph and the specification
> table it summarises. A retriever that treats representations as interchangeable (or that
> lets text crowd out tables by volume) will systematically miss binding constraints. We show
> that an explicit, enforced per-modality composition of the retrieved set — with the
> modality-supporting each claim recorded — changes which evidence the generator sees, and we
> quantify both the gain and the displacement cost.

That framing is novel, is supported by the prior art, and is exactly what the thesis's own
null result can then be interpreted against.

---

## 5. Gaps and risks

### 5.1 The null result is the honest outcome, and it is the most likely one

The thesis's own report records that the modality-aware boost was **a documented null result**:
the corpus is too text-heavy (**2.3 % chart, 7.1 % table**) for the quota to exercise the
signal. This is not a failure of implementation; it is a **power problem**. If a corpus contains
7.1 % tables and a quota reserves 20 % of the context for tables, the quota either has nothing
to select from (so the rule is inert) or it must promote a table chunk that is *not* relevant to
the query (so it displaces a relevant text chunk). Either way the effect is noise.

What the literature says about this, and what to do:

- **Fix the corpus, not the algorithm.** The benchmark corpus must contain enough table- and
  chart-evidenced queries for the effect to be estimable. A quota experiment needs queries
  *stratified* by the modality of their gold evidence, with a minimum stratum size chosen before
  the run. Power analysis first; effect size second.
- **Report the null as a result.** *FreshStack* (arXiv:2504.13128) exists precisely because
  clean, uncontaminated, realistic benchmarks are rare; a careful null with a stated power
  analysis is publishable and is more defensible than a positive result on a corpus too small
  to detect it.
- **The published literature supports the null on its own terms.** VisRAG's gains come from
  *eliminating parsing loss*, not from balancing; T²-RAGBench's Hybrid-BM25 result is about
  *fusion* of dense and sparse over a corpus that is already mixed. If the thesis's corpus is
  not mixed, the theory predicts no effect — and the thesis should say that prediction was made
  in advance.

### 5.2 Confound: parsing fidelity

Any modality result is really a parsing result. OmniDocBench (CVPR 2025) shows no parser is
uniformly best, and Document Parsing Unveiled (arXiv:2410.21169) names robustness to complex
layouts and reliability of VLM parsing as open problems. **Mitigation:** report the parser and
its per-type accuracy on the thesis corpus, hold it fixed across arms, and — if a table's
values are not preserved, say that the modality channel is empty for that document.

### 5.3 Confound: chunking

HiChunk (arXiv:2509.11552) shows existing RAG benchmarks cannot isolate chunking quality
because of **evidence sparsity**, and SCAN (arXiv:2505.14381) shows chunking alone can move
textual RAG by ~9.4 points and visual RAG by ~10.4 points. A modality-quota effect smaller
than the chunking effect is uninterpretable. **Mitigation:** fixed chunker across arms;
report chunk-count and chunk-length distributions *per modality* so a reader can see that the
quota is not simply selecting shorter or longer chunks.

### 5.4 Confound: reranking

The thesis's own reranker regression (−5.34 pp on `production_scheduling`) has an independent
explanation in FreshStack: rerankers failed to improve first-stage retrieval on **two of five**
topics, and out-of-the-box retrieval significantly underperforms oracle on all five. **This is
a citable mechanism, not an excuse** — but it also means the reranker's contribution must be
measured per category, and the category on which it fails should be reported rather than
dropped.

### 5.5 Risk: the metric

MRAG-Suite (arXiv:2509.24253) found substantial accuracy reductions under difficult and
ambiguous queries and provides **MM-RAGChecker** for claim-level diagnosis. A single recall
number over a modality-stratified benchmark will not support a modality claim. **Mitigation:**
report recall@k on table-evidenced queries, chart-evidenced queries and text-evidenced
queries separately, plus the displacement cost on the text stratum.

### 5.6 Risk: the library stack in the thesis report

Two corrections to the report's "Stack at a Glance" table are needed, both verified live:

| Report says | Verified | Action |
|---|---|---|
| `ms-marco-MiniLM-L-6-v2` | `cross-encoder/ms-marco-MiniLM-L6-v2` (no hyphen between L and 6) | Fix — as written it will not resolve |
| `MiniMax embed-01 (1024-d, opt-in)` | No embedding model is exposed in the current MiniMax API documentation index (`platform.minimax.io/docs/llms.txt`, checked 2026-10-31); the public model lineup is `MiniMaxAI/MiniMax-M3`, `MiniMax-M3.1-Flash`, `MiniMax-M2/M2.1/M2.5/M2.7` and the H/Music/VL series | Replace with a verified embedding path: `all-MiniLM-L6-v2` (384-d, default) or `BAAI/bge-m3` (1024-d) via `sentence-transformers`/`FlagEmbedding` |

`MiniMaxAI/MiniMax-M3` itself **is** a real model (verified on HuggingFace, ≈1 599 likes), so the
report's choice of generator is sound; only the embedding row needs replacing.

---

## 6. Bibliography for this section (verified)

Format: Authors (Year). *Title*. Venue. arXiv/DOI.

1. Faysse, M., Sibille, H., Wu, T., Omrani, B., Viaud, G., Hudelot, C., & Colombo, P. (2024/2025). ColPali: Efficient Document Retrieval with Vision Language Models. *ICLR 2025*. arXiv:2407.01449.
2. Qiao, J., Ju, J.-H., Ma, X., Kanoulas, E., & Yates, A. (2025). Reproducibility, Replicability, and Insights into Visual Document Retrieval with Late Interaction. arXiv:2505.07730.
3. Masry, A., Thakkar, M., Bechard, P., Madhusudhan, S. T., Awal, R., & Mishra, S., et al. (2025). ColMate: Contrastive Late Interaction and Masked Text for Multimodal Document Retrieval. *EMNLP 2025 Industry Track*. DOI 10.18653/v1/2025.emnlp-industry.145. arXiv:2511.00903.
4. Teiletche, P., Macé, Q., Conti, M., Loison, A., Viaud, G., Colombo, P., et al. (2025). ModernVBERT: Towards Smaller Visual Document Retrievers. arXiv:2510.01149.
5. Yu, S., Tang, C., Xu, B., Cui, J., Ran, J., Yan, Y., et al. (2024). VisRAG: Vision-based Retrieval-augmented Generation on Multi-modality Documents. arXiv:2410.10594.
6. Suri, M., Mathur, P., Dernoncourt, F., Goswami, K., Rossi, R. A., & Manocha, D. (2025). VisDoM: Multi-Document QA with Visually Rich Elements Using Multimodal Retrieval-Augmented Generation. *NAACL 2025*. DOI 10.18653/v1/2025.naacl-long.310. arXiv:2412.10704.
7. Ueda, N., Dong, Y., Boros, K., Ito, D., Sera, T., & Oyamada, M. (2026). SCAN: Semantic Document Layout Analysis for Textual and Visual Retrieval-Augmented Generation. *Findings of EACL 2026*. DOI 10.18653/v1/2026.findings-eacl.82. arXiv:2505.14381.
8. Strich, J., Kutay Isgorur, E., Trescher, M., Biemann, C., & Semmann, M. (2026). T²-RAGBench: Text-and-Table Benchmark for Evaluating Retrieval-Augmented Generation. *EACL 2026*. DOI 10.18653/v1/2026.eacl-long.8. arXiv:2506.12071.
9. Thakur, N., Lin, J., Havens, S., Carbin, M., Khattab, O., & Drozdov, A. (2025). FreshStack: Building Realistic Benchmarks for Evaluating Retrieval on Technical Documents. *NeurIPS 2025*. DOI 10.52202/085713-5255. arXiv:2504.13128.
10. El Bachyr, O., Bernardy, L. M., Ezzini, S., Klein, J., Bissyandé, T. F., Mont'e, C., et al. (2026). VisR-RAG-Fin: Benchmarking Multimodal RAG over Visually Rich Financial Documents. arXiv:2610.24822.
11. Yu, X., Jian, P., & Chen, C. (2025). TableRAG: A Retrieval Augmented Generation Framework for Heterogeneous Document Reasoning. *EMNLP 2025*. DOI 10.18653/v1/2025.emnlp-main.710. arXiv:2506.10380.
12. Chen, S.-A., Miculicich, L., Eisenschlos, J. M., & Wang, Z. (2024). TableRAG: Million-Token Table Understanding with Language Models. arXiv:2410.04739.
13. Günther, M., Mohr, I., Williams, D. J., & Wang, B. (2024). Late Chunking: Contextual Chunk Embeddings Using Long-Context Embedding Models. arXiv:2409.04701.
14. Sarthi, P., Abdullah, S., Tuli, A., Khanna, S., Goldie, A., & Manning, C. D. (2024). RAPTOR: Recursive Abstractive Processing for Tree-Organized Retrieval. arXiv:2401.18059.
15. Ouyang, L., Qu, Y., Zhou, H., Zhu, J., Zhang, R., Lin, Q., et al. (2025). OmniDocBench: Benchmarking Diverse PDF Document Parsing with Comprehensive Annotations. *CVPR 2025*. DOI 10.1109/cvpr52734.2025.02313. arXiv:2412.07626.
16. Zhang, Q., Wang, B., Huang, V. S.-J., Zhang, J., Wang, Z., Liang, H., et al. (2024). Document Parsing Unveiled: Techniques, Challenges, and Prospects for Structured Information Extraction. arXiv:2410.21169.
17. Friel, R., Belyi, M., & Sanyal, A. (2024). RAGBench: Explainable Benchmark for Retrieval-Augmented Generation Systems. arXiv:2407.11005.
18. Lu, W., Chen, K., Qiao, R., & Sun, X. (2026). HiChunk: Evaluating and Enhancing Retrieval-Augmented Generation with Hierarchical Chunking. *ACL 2026*. DOI 10.18653/v1/2026.acl-long.1372. arXiv:2509.11552.
19. Ji, Y., Lan, W., & Ng, P. (2025). MRAG-Suite: A Diagnostic Evaluation Platform for Visual Retrieval-Augmented Generation. arXiv:2509.24253.
20. Mei, L., Mo, S., Yang, Z., & Chen, C. (2025). A Survey of Multimodal Retrieval-Augmented Generation. arXiv:2504.08748.
21. Abootorabi, M. M., Zobeiri, A., Dehghani, M., Mohammadkhani, M. A., Mohammadi, B., Ghahroodi, O., et al. (2025). Ask in Any Modality: A Comprehensive Survey on Multimodal Retrieval-Augmented Generation. arXiv:2502.08826.
22. Gao, S., Zhao, S., Jiang, X., Duan, L., Chng, Y. X., Chen, Q.-G., et al. (2025). Scaling Beyond Context: A Survey of Multimodal Retrieval-Augmented Generation for Document Understanding. arXiv:2510.15253.
23. Mathew, M., Karatzas, D., & Jawahar, C. V. (2021). DocVQA: A Dataset for VQA on Document Images. *WACV 2021*. DOI 10.1109/wacv48630.2021.00225. arXiv:2007.00398.
24. Mathew, M., Bagal, V., Pérez Tito, R., Karatzas, D., Valveny, E., & Jawahar, C. V. (2022). InfographicVQA. *WACV 2022*. DOI 10.1109/wacv51458.2022.00264. arXiv:2104.12756.
25. Masry, A., Long, D. X., Tan, J. Q., Joty, S., & Hoque, E. (2022). ChartQA: A Benchmark for Question Answering about Charts with Visual and Logical Reasoning. *Findings of ACL 2022*. DOI 10.18653/v1/2022.findings-acl.177. arXiv:2203.10244.
26. MMLongBench-Doc: Benchmarking Long-context Document Understanding (2024). *NeurIPS 2024*. DOI 10.52202/079017-3041.
27. Bach, D. (2025). Hierarchical Patch Compression for ColPali: Efficient Multi-Vector Document Retrieval with Dynamic Pruning and Quantization. arXiv:2506.21601.
28. Sun, Y., Peng, C., Yan, Y., Yu, S., Liu, Z., Mei, S., et al. (2025). VisRAG2.0: Mitigating Visual Hallucinations via Evidence-Guided Multi-Image Reasoning in Visual Retrieval-Augmented Generation. arXiv:2510.09733.
29. When Image and Text Disagree: Cross-Modal Evidence Conflict… (2026). *2nd Workshop on Multimodal Augmented Generation*. DOI 10.18653/v1/2026.magmar-main.3.

**Verified third-party toolchain** (PyPI JSON API, 2026-10-31): `docling` 2.145.0,
`colpali-engine` 0.3.18, `pgvector` 0.5.1, `rank-bm25` 0.2.2, `sentence-transformers` 6.2.0,
`marker-pdf` 2.1.0, `unstructured` 0.27.36, `FlagEmbedding` 1.4.2, `pymupdf` 2.0,
`ragas` 0.4.3.
**Verified model identifiers** (HuggingFace API, 2026-10-31): `sentence-transformers/all-MiniLM-L6-v2`
(384-d, ≈186 M downloads), `cross-encoder/ms-marco-MiniLM-L6-v2` (≈68.9 M downloads),
`BAAI/bge-reranker-base`, `jinaai/jina-embeddings-v2-base-en`, `MiniMaxAI/MiniMax-M3`.

---

## 7. Items explicitly NOT verified

- **RAPTOR (2401.18059)** and **InfographicVQA (2104.12756)** were flagged after the arXiv API
  began throttling; both have since been **re-fetched individually and confirmed** (RAPTOR:
  Sarthi, Abdullah, Tuli, Khanna, Goldie, Manning, submitted 31 Jan 2024; InfographicVQA:
  Mathew, Bagal, Pérez Tito, Karatzas, Valveny, Jawahar, submitted 26 Apr 2021). Both arXiv
  ids in this file are now verified against the paper's own abstract page.
- **TAT-DQA** (Smock et al.) is a real ACL 2024 paper, but it did not surface in Crossref or
  arXiv title search under any query used here, and its arXiv id is therefore **not asserted**.
  Re-verify before citing.
- **MMLongBench-Doc** (row 26) has no author list in this file; Crossref returned the venue and
  DOI. **Add the author list from the NeurIPS 2024 proceedings page before typesetting.**
- **SlideVQA** (row 26 in the table) — DOI verified via Crossref; the arXiv id is not asserted.
- **InfographicVQA dataset size** — deliberately not stated in this file. The retrieved
  abstract does not give image/question counts; read them from the paper's dataset section
  before quoting them.
- The "**ChartQA-X**", "**MSG-Chart**" and "**Hierarchical multimodal transformers for
  Multi-Page DocVQA**" papers appeared in searches and exist, but were **not** developed into
  this section because they do not bear directly on the modality-quota claim. They are
  available if the defence asks about chart reasoning depth.

## 8. Channels that failed during this review (recorded so it is not repeated)

- **OpenAlex** — shared free daily budget exhausted for this network's IP address
  ("Insufficient budget… $0.0008 remaining; resets at midnight UTC"). Needs a personal API key.
- **Semantic Scholar Graph API** — anonymous pool returns 429 for this network; needs
  `SEMANTIC_SCHOLER_API_KEY`.
- **arXiv Atom API** — works but throttles hard under bursts (429 after 2–3 rapid queries);
  reliable at ~6 s spacing with exponential backoff.
- **arXiv HTML search** — 429 from a plain HTTP client; reachable only through the Scrapling
  stealth browser.
- **DBLP API** — 429 after a handful of requests.
- **`WebSearch` tool** — unavailable in this environment (model configuration error:
  *"MiniMax-M3.1-Flash requires adaptive thinking"*).

The channels that *did* work throughout: **arXiv Atom API** (paced), **Crossref REST API**
(polite-pool, no key needed), **arXiv via Scrapling**, **ACL Anthology** (direct pages),
**HuggingFace API**, **PyPI JSON API**.
