# Survey 05 — Per-Claim Attribution, RAG Evaluation, and Confidence/Abstention

**Scope:** the literature that speaks directly to the thesis's RO5 / design-move D5 (per-claim
confidence tagging: *grounded / inferred / uncertain*, each claim carrying a citation back to its
source chunk) and to its RO2 evaluation machinery.

**Everything in this file was verified by fetching the paper.** Verification was performed through
four independent channels, and a claim is only marked VERIFIED if at least one channel returned the
paper with matching title and authors:

| Channel | Endpoint | Used for |
|---|---|---|
| arXiv API | `export.arxiv.org/api/query` (batched `id_list`) | preprints: title, authors, date, comments, journal-ref, DOI, full abstract |
| Semantic Scholar | `api.semanticscholar.org/graph/v1/paper/batch` | venue, citation count, cross-referenced IDs |
| Crossref | `api.crossref.org/works/{doi}` | published articles: authors, journal, volume, issue, pages, DOI, cited-by |
| Scrapling | `arxiv.org/abs/<id>`, `doi.org`, `sciencedirect.com` | abstract-page fallback where APIs were rate-limited |

**Two APIs were rate-limited during this survey** (arXiv 429, Semantic Scholar 429) because five
parallel agents were hitting them from one IP. This is why verification was staged: arXiv batch
first, then Crossref, then Scrapling. The `arXiv 2507.21502` note in §7 is an example of a
reference that only survived because a fallback channel was used.

**A note on honesty.** Where a paper could not be retrieved in full, this file says so and the
affected claims are marked UNVERIFIED. It is better for the thesis to soften a claim than to carry
a number nobody checked.

---

## 1. Master table — VERIFIED papers

Every row below was fetched. "Key number" is quoted from the paper's own abstract, not paraphrased
from memory. Where a paper's abstract states no number, the cell says so.

### 1.1 Attribution, citation, and claim-level evaluation

| # | Citation | Venue / ID | Method (one line) | Key finding (from the abstract) |
|---|---|---|---|---|
| 1 | Gao, Yen, Yu, Chen (2023), "Enabling Large Language Models to Generate Text with Citations" | EMNLP 2023 · arXiv:2305.14627 | ALCE — first end-to-end benchmark for LLM citation generation; metrics on fluency / correctness / citation quality | **On ELI5, even the best models lack complete citation support 50% of the time.** Metrics correlate strongly with human judgement |
| 2 | Bohnet, Tran, Verga, Aharoni, Andor, Baldini Soares, Ciaramita, Eisenstein (2022), "Attributed Question Answering: Evaluation and Modeling for Attributed Large Language Models" | arXiv:2212.08037 | Formalises *attributed QA* as (answer, attribution) pairs; reproducible eval framework | Human annotations used as gold standard; a correlated automatic metric is shown suitable for development |
| 3 | Yue, Wang, Chen, Zhang, Su, Sun (2023), "Automatic Evaluation of Attribution by Large Language Models" | EMNLP 2023 · arXiv:2305.06311 | Defines **types of attribution error**; two routes — prompt an LLM, or fine-tune a smaller LM on repurposed QA/fact-check/NLI/summarisation data | Test set manually curated covering **12 domains** from the New Bing generative search engine |
| 4 | Aly, Tang, Tan, Karypis (2024), "Learning to Generate Answers with Citations via Factual Consistency Models" | ACL 2024 · arXiv:2406.13124 | Weakly-supervised fine-tuning using factual consistency models (FCMs) as a citation filter | On ALCE few-shot: average citation-F1 gains of **+34.1 / +15.5 / +10.5 points** over in-context learning / vanilla SFT / prior SOTA; transfers to unseen datasets |
| 5 | Kamalloo, Jafari, Zhang, Thakur, Lin (2023), "HAGRID: A Human-LLM Collaborative Dataset for Generative Information-Seeking with Attribution" | arXiv:2307.16883 | GPT-3.5 generates in-context-style cited explanations; humans rate **informativeness** and **attributability** | Built atop the **English subset of MIRACL**; explicit human–LLM collaboration loop |
| 6 | Malaviya, Lee, Chen, Sieber, Yatskar, Roth (2023), "ExpertQA: Expert-Curated Questions and Attributed Answers" | arXiv:2309.07852 | Domain experts write the questions *and* judge the answers | **484 participants across 32 fields**; dataset of **2,177 questions** with verified answers *and* attributions per claim |
| 7 | Min, Krishna, Lyu, Lewis, Yih, Koh, Iyyer, Zettlemoyer (2023), "FActScore" | EMNLP 2023 · arXiv:2305.14251 | Decomposes a generation into **atomic facts**; scores % supported by a reliable source | ChatGPT scores only **58%**; an automated estimator has **<2% error rate**; 6,500 generations evaluated (~$26K of human cost avoided) |
| 8 | Honovich, Aharoni, Herzig, Taitelbaum, Kukliansy, Cohen, Scialom, Szpektor (2022), "TRUE: Re-evaluating Factual Consistency Evaluation" | NAACL 2022 · arXiv:2204.04991 | Meta-evaluation of factual-consistency metrics across a standardised, manually annotated corpus | Across 11 datasets, **large-scale NLI and QA-based approaches are strong and complementary**; proposes an *example-level* (not just system-correlation) meta-evaluation protocol |
| 9 | Stelmakh, Luan, Dhingra, Chang (2022), "ASQA: Factoid Questions Meet Long-Form Answers" | EMNLP 2022 · arXiv:2204.06092 | Long-form QA where the question is *ambiguous* — answer must resolve multiple interpretations | Defines correctness as "a reader of the summary can answer every interpretation"; metric agrees with human judgement; **considerable gap between human performance and strong baselines** |
| 10 | Amouyal, Wolfson, Rubin, Yoran, Herzig, Berant (2022), "QAMPARI" | arXiv:2205.12665 | Open-domain QA where the answer is a *list* of entities spread over many paragraphs | Best trained retrieve-and-read model reaches **F1 = 32.8** — "challenging in terms of both passage retrieval and answer generation" |
| 11 | Tang, Yang (2024), "MultiHop-RAG" | arXiv:2401.15391 | Knowledge base + multi-hop queries + ground-truth answers + supporting evidence | Existing RAG systems are "inadequate" for multi-hop; GPT-4, PaLM, Llama2-70B all "perform unsatisfactorily" on retrieval *and* answering |
| 12 | Schuster, Fisch, Barzilay (2021), "Get Your Vitamin C!" | ACL 2021 · arXiv:2103.08541 | **Contrastive** claim–evidence pairs: near-identical evidence, one supports, one does not | 100k+ Wikipedia revisions → **400,000+ claim–evidence pairs**; contrastive training gives **+10%** on adversarial fact verification and **+6%** on adversarial NLI |
| 13 | Aly, Guo, Schlichtkrull, Thorne, Vlachos, Christodoulopoulos, Cocarascu, Mittal (2021), "FEVEROUS" | ACL 2021 · arXiv:2106.05707 | Claims verified against **both sentences and table cells** from Wikipedia | **87,026 verified claims**; a baseline that must get both evidence *and* verdict right does so for only **18%** of claims |
| 14 | Schlichtkrull, Guo, Vlachos (2023), "AVeriTeC" | NeurIPS 2023 · arXiv:2305.13117 | Real-world claims from fact-checkers, annotated with QA pairs + justifications | **4,568 real-world claims** from **50 organisations**; inter-annotator agreement **κ = 0.619** on verdicts; explicitly avoids context dependence and temporal leakage |
| 15 | Wei, Yang, Song, Lu, Hu, Huang, Tran, Peng et al. (2024), "Long-form factuality in large language models" (the SAFE paper) | NeurIPS 2024 · arXiv:2403.18802 | LongFact (thousands of questions, **38 topics**) + SAFE: an LLM agent decomposes the answer into facts and verifies each via Google Search | SAFE agrees with crowdsourced annotators **72%** of the time on ~16k facts; on 100 disagreement cases SAFE wins **76%** of the time; **>20× cheaper** than humans; extends F1 to balance supported-fact precision against preferred answer length |

### 1.2 RAG evaluation frameworks

| # | Citation | Venue / ID | Dimensions | Key finding |
|---|---|---|---|---|
| 16 | Es, James, Espinosa-Anke, Schockaert (2023/2024), "RAGAS" | EACL 2024 · arXiv:2309.15217 | Reference-free: **context precision/relevance**, **faithfulness**, **answer relevancy** | Removes the need for ground-truth human annotations, "crucially" for faster RAG evaluation cycles |
| 17 | Saad-Falcon, Khattab, Potts, Zaharia (2023/2024), "ARES" | NAACL 2024 · arXiv:2311.09476 | **Context relevance**, **answer faithfulness**, **answer relevance** | Trains lightweight LM judges on synthetic data, then uses **prediction-powered inference** over a *few hundred* human annotations; evaluated across **8 knowledge-intensive tasks** in KILT / SuperGLUE / AIS; judges stay accurate under domain shift |
| 18 | Chen, Lin, Han, Sun (2023), "Benchmarking LLMs in RAG" (RGB) | AAAI 2024 · arXiv:2309.01431 | Four abilities: **noise robustness, negative rejection, information integration, counterfactual robustness** | Evaluates 6 LLMs on English + Chinese corpora; LLMs have "a certain degree of noise robustness" but "struggle significantly" on negative rejection, integration, and false information |
| 19 | Niu, Wu, Zhu, Xu, Shum, Zhong, Song, Zhang (2023/2024), "RAGTruth" | ACL 2024 · arXiv:2401.00396 | Word-level **and** case-level hallucination annotation | **~18,000** naturally generated RAG responses annotated; a fine-tuned small LLM matches prompt-based GPT-4 detection |
| 20 | Lyu, Li, Niu, Xiong, Tang, Wang, Wu, Liu (2024), "CRUD-RAG" | ACM TOIS 2024 · arXiv:2401.17043 | Four *task categories*: **Create, Read, Update, Delete** | Evaluates **all pipeline components** (retriever, generator, knowledge base), not just the LLM, unlike prior benchmarks |
| 21 | Friel, Belyi, Sanyal (2024), "RAGBench" | arXiv:2407.11005 | Explainable benchmark, multiple RAG task types | **100k examples**; **five industry-specific domains**; examples sourced from **industry corpora such as user manuals** — "particularly relevant for industry applications" |
| 22 | Chowdhury, He, Joselowitz, Higham, Lim (2025), "ASTRID" | AMIA 2025 · arXiv:2501.08208 | TRIaD: **Context Relevance (CR)**, **Refusal Accuracy (RA)**, **Conversational Faithfulness (CF)** | CF predicts human faithfulness ratings *better than existing definitions* for conversational use cases; triad aligns with clinician assessment; validated on 200+ real patient questions |
| 23 | Pham, Nguyen, Zunjare, Chen, Tseng, Vu (2025), "SealQA" | arXiv:2506.01062 | Fact-seeking under conflicting / noisy / unhelpful search results | Frontier agentic models reach only **17.1% (o3)** and **6.3% (o4-mini)** on Seal-0 at best effort; reasoning models are "highly vulnerable to noisy search results"; **more test-time compute does not yield reliable gains** |

### 1.3 Confidence, uncertainty, and abstention — the direct competitors to RO1/D1

| # | Citation | Venue / ID | Mechanism | Key finding |
|---|---|---|---|---|
| 24 | Li, Park, Lee, Bastani (2023), "TRAQ" | arXiv:2307.04642 | **Conformal prediction** over the retrieved/answer set; Bayesian optimisation to shrink set size | Claims the **first end-to-end statistical correctness guarantee for RAG**; reduces prediction-set size by **16.2% on average** vs an ablation |
| 25 | Kuhn, Gal, Farquhar (2023/2024), "Semantic Uncertainty" | ICLR 2024 · arXiv:2302.09664 | Entropy over *semantically clustered* samples rather than raw strings | Overcomes "semantic equivalence" (different sentences, same meaning); unsupervised, single model, no modification to off-the-shelf LMs; **more predictive of QA accuracy than comparable baselines** |
| 26 | Farquhar, Kossen, Kuhn, Gal (2024), "Detecting hallucinations in large language models using semantic entropy" | *Nature* **630**, 625–630 (2024) · DOI **10.1038/s41586-024-07421-0** (1025 citations) | Peer-reviewed version of #25, with the biomedical-scale evaluation | The peer-reviewed anchor for semantic-entropy claims. **Page range and DOI verified against the Crossref record.** |
| 27 | Feng, Sui, Hou, Cresswell, Wu (2025), "Conformal-RAG" | arXiv:2506.20978 | Conditional conformal prediction over **sub-claims**, using internal RAG information | Gives **group-conditional coverage** without manual labelling of conformal sets; retains **up to 60% more high-quality sub-claims** than applying CP directly to the LLM, at the same reliability |
| 28 | Geissler, Carella, Fieback, Spiegelberg (2026), "Towards Dependable RAG Using Factual Confidence Prediction" | arXiv:2605.05244 | **Two-stage**: (1) conformal prediction filters retrieved chunks; (2) attention-based factuality classifier scores answer–context consistency | Chunk filtering alone "can improve answer quality by up to **6%**"; the consistency classifier "can detect inconsistent answers with a chance of up to **77%**"; ⚠ the paper explicitly warns the statistical guarantee **does not hold generally** because exchangeability depends on the retriever setup |
| 29 | Nguyen, Dang, Zhang, Tran, Tran, Chau, Le, Cheng (2026), "URAG" | arXiv:2603.19281 | Reformulates open-ended generation into MCQ so conformal prediction can be applied | Applies to **8 standard RAG methods**; findings: (1) accuracy gains often coincide with reduced uncertainty **but this breaks under retrieval noise**; (2) simple modular RAG gives better accuracy–uncertainty trade-offs than complex reasoning pipelines; (3) **no single RAG approach is universally reliable across domains**; (4) retrieval depth, parametric-knowledge dependence and confidence cues can **amplify confident errors** |
| 30 | Niu, Su, Tian (2026), "UA-RAG: Uncertainty-aware dynamic RAG" | *Neurocomputing* **699**, 134357 (2026) · DOI 10.1016/j.neucom.2026.134357 | Uncertainty-aware dynamic retrieval | **Directly relevant precedent** for a dynamic, uncertainty-conditioned RAG loop in a recent journal — see §7 for what it means for novelty |

### 1.4 LLM-as-judge: what it costs and how it fails

| # | Citation | Venue / ID | Finding |
|---|---|---|---|
| 31 | Zheng, Chiang, Sheng, Zhuang, Wu, Zhuang, Lin, Li et al. (2023), "Judging LLM-as-a-judge with MT-Bench and Chatbot Arena" | NeurIPS 2023 · arXiv:2306.05685 | Strong judges (GPT-4) reach **>80% agreement** with human preference — *the same level as human–human agreement*. Names and measures three biases: **position, verbosity, self-enhancement** |
| 32 | Wang, Li, Chen, Cai, Zhu, Lin, Cao, Liu (2023), "Large Language Models are not Fair Evaluators" | ACL 2024 · arXiv:2305.17926 | Ranking is **hacked by reordering the context**: with ChatGPT as judge, **Vicuna-13B beat ChatGPT on 66 of 80 queries**. Proposes three calibrations: Multiple Evidence, Balanced Position, Human-in-the-Loop |
| 33 | Thakur, Choudhary, Ramayapally, Vaidyanathan, Hupkes (2024), "Judging the Judges: Evaluating Alignment and Vulnerabilities in LLMs-as-Judges" | arXiv:2406.12624 | **13 judge models × 9 exam-taker models.** Only the best/largest align reasonably with humans, yet scores may still differ by **up to 5 points**; judges are sensitive to prompt complexity and length and show a **tendency toward leniency**. Conclusion: "caution may be wise when using judges in more complex setups" |
| 34 | Liu, Iter, Xu, Wang, Xu, Zhu (2023), "G-Eval" | EMNLP 2023 · arXiv:2303.16634 | GPT-4 with CoT + form-filling reaches **Spearman 0.514** with humans on summarisation, "outperforming all previous methods by a large margin". Flags the bias of LLM evaluators **toward LLM-generated text** |

### 1.5 The thesis proposal's own reference list — audit

These are the references already in `MTP-2.docx`. All eighteen were checked.

| Ref in proposal | Status | Verified form |
|---|---|---|
| [6] Wan et al. (2025), *Adv. Eng. Inform.* | ✅ VERIFIED | Yuwei Wan, Zheyuan Chen, Ying Liu, Chong Chen, M. Packianather. AEI **65**, 103212. DOI 10.1016/j.aei.2025.103212 (121 citations) |
| [7] Wu et al. (2025), *Adv. Eng. Inform.* | ✅ VERIFIED | Chengke Wu, Wen-Jun Ding, Qisen Jin, Jun-Jie Jiang, Rui Jiang, Qin-Ge Xiao. AEI **65**, 103158. DOI 10.1016/j.aei.2025.103158 (86 citations) |
| [8] Decian et al. (2026), *Neurocomputing* | ✅ VERIFIED | Jean Decian, Chaima Njeh, Haïfa Nakouri, Fehmi Jaafar. Neurocomputing **705**, 134911. DOI 10.1016/j.neucom.2026.134911. ⚠ 0 citations — very recent |
| [18] Zhang & Zhang (2025), *Mathematics* | ✅ VERIFIED | Wan Zhang, Jing Zhang. Mathematics **13**(5), 856. DOI 10.3390/math13050856 (156 citations) |
| [15] "Microsoft Research (2025)" | ⚠ **AUTHOR ERROR** | The paper exists: arXiv:2507.21502, "Large Language Models for Supply Chain Decisions". But the authors are **David Simchi-Levi, Konstantina Mellou, Ishai Menache, Jeevan Pathuri** — *not* "Microsoft Research". Also "Real-world Microsoft deployment" in the Remarks column is **not supported** by the title/metadata; it is an academic preprint. Fix both. |
| [17] Li et al. (2025) arXiv:2510.24476 | ⚠ **TITLE ERROR** | Real title: "Mitigating Hallucination in Large Language Models: A **Capability-Oriented** Survey". The proposal says "Application-Oriented". |
| [13] Lyu et al. (2024) CRUD-RAG | ⚠ **MINOR** | The paper's four units are **task categories** (Create/Read/Update/Delete), not "four metrics". Rewrite. |
| [10] Es et al. (2024) RAGAS | ✅ | arXiv:2309.15217, EACL 2024 |
| [11] Gao et al. (2023) ALCE | ✅ | arXiv:2305.14627, EMNLP 2023 |
| [12] Bohnet et al. (2022) | ✅ | arXiv:2212.08037 |
| [14] Tang & Yang (2024) MultiHop-RAG | ✅ | arXiv:2401.15391 |
| [16] Gao et al. (2023) RAG survey | ✅ | arXiv:2312.10997 |
| [2] Asai et al. (2024) Self-RAG | ✅ | arXiv:2310.11511 |
| [3] Yan et al. (2024) CRAG | ✅ | arXiv:2401.15884 |
| [4] Edge et al. (2024) GraphRAG | ✅ | arXiv:2404.16130 |
| [5] Wang et al. (2025) PIKE-RAG | ✅ | arXiv:2501.11551 |
| [9] Wei et al. (2024) InstructRAG | ✅ | arXiv:2406.13629 |
| [1] Lewis et al. (2020) RAG | ✅ | Not re-verified in this survey (out of scope) — no issue found elsewhere |

**Unverified specific numbers in the proposal's literature table** — these two figures could not be
confirmed, because the abstracts are behind ScienceDirect's bot protection and the papers have no
arXiv preprint:

- [6] "77.8% accuracy on design-for-manufacturing" — **UNVERIFIED**
- [7] "92.4% Top-3 accuracy with preference learning" — **UNVERIFIED**

Both papers are real, correctly cited, and highly cited (121 and 86 respectively). The *titles,
authors, venues, and DOIs are all correct* — only the two performance figures are unchecked. The
honest fix is to open the PDFs, confirm the numbers, and state the metric the number belongs to
(accuracy on what task? top-3 on which split?), or replace the cell with the paper's own headline
result. Do not carry these into the final reference list unchecked.

**Additional verified papers the proposal does not cite but should consider** — each closes a gap
the proposal's own argument depends on: TRAQ (#24), Conformal-RAG (#27), Factual Confidence
Prediction (#28), URAG (#29), SealQA (#23), RAGTruth (#19), ExpertQA (#6), HAGRID (#5), FActScore
(#7), TRUE (#8), ASTRID (#22), and the four LLM-as-judge bias papers (#31–34).

---

## 2. Deep explanations

Written for a reader who knows nothing about RAG evaluation. Each explains the mechanism, why it
matters to an industrial evidence-grounded system, and what it costs.

### 2.1 What "faithfulness" actually means

Faithfulness is a property of a *pair*: a generated answer and the context that was supposed to
support it. The question is not "is the answer true?" — the model has no access to the world — but
"can every factual statement in the answer be traced to something in the retrieved context?"

That distinction matters enormously in industrial settings. An answer can be factually correct and
still unfaithful: the system states the right value but got it from its parametric memory rather
than from the maintenance log it cites. In an audit, that is a failure. The supervisor asks "how do
you know?" and the honest answer is "the model remembered it", which is not a traceable answer.

RAGAS (Es et al., #16) operationalises this as a decomposition: split the generated answer into
individual claims, then ask an LLM judge for each claim whether it is entailed by the retrieved
context. The aggregate is the *faithfulness* score — the proportion of claims that are supported.
This is the single most useful metric for the thesis because it measures exactly the property the
framework is trying to improve: the answer's dependence on retrieved evidence rather than on the
model's memory.

The computation is not free. It costs one NLI-style entailment call per claim. An answer with 8
claims means 8 judge invocations, plus the answer itself. At 300 benchmark questions × 5 baselines
× 2 annotators, that is on the order of tens of thousands of extra LLM calls. Budget for this
explicitly; it is a real line item, and reviewers ask about it.

### 2.2 Citation precision and citation recall (ALCE)

These two numbers, introduced by Gao et al. (#1), are the backbone of any attribution claim, so it
is worth being precise about what they count.

**Citation recall** asks: of the claims in the answer that *should* have been supported, what
fraction actually have a citation attached to them that supports them? It is a coverage measure.
The denominator is the set of supported claims; the numerator is the supported claims that were
both cited and correctly cited.

**Citation precision** asks: of the citations that were attached, what fraction actually support
the claim they are attached to? It is a correctness measure. The denominator is all citations
emitted; the numerator is those the NLI judge finds entailing the claim.

A system can score 100% precision with 10% recall (cite one claim perfectly, ignore the rest), or
100% recall with 30% precision (cite everything, wrongly). **Both must be reported.** This is the
single most common way an attribution claim gets rejected by a reviewer, and it is the metric pair
the thesis's D5 design move should be judged against.

The number that should temper expectations is in ALCE's abstract: on ELI5, even the best models
lack complete citation support **50% of the time**. Complete citation support is the fraction of
claims that are both fully supported and correctly cited. Half of the time, even the strongest
systems fail this. Any industrial claim that "our system achieves complete citation support"
will be met with "on what task?" — and the honest answer is that ELI5-style open-ended
explanation is much harder than industrial factoid lookup.

### 2.3 The atomic-fact move (FActScore, SAFE, ClaimDecomp-style decomposition)

The insight behind FActScore (#7) is that "is this answer factual?" is the wrong unit of
measurement. A single long-form answer mixes supported and unsupported material, so a binary
judgement averages over two different situations and tells you nothing actionable.

The fix is to decompose. Split the generation into **atomic facts** — minimal units that stand
alone as checkable propositions ("the EOQ for SKU A-104 is 187 units", not "the EOQ depends on the
demand pattern, which for SKU A-104 is…"). Then score each fact independently against a reliable
source, and report the *percentage of atomic facts supported*. This is a precision-only metric —
it does not penalise an answer for failing to mention something, only for asserting something
unsupported.

The reported numbers are sobering and useful. ChatGPT scores **58%** on FActScore for people
biographies — meaning roughly 4 in 10 atomic facts in a fluent, human-plausible ChatGPT biography
are unsupported. Crucially for the thesis, FActScore also ships an **automated estimator** that
replicates the human-scored metric with **less than 2% error rate**. That is what makes per-claim
evaluation affordable at benchmark scale: the thesis does not need a human to judge 40,000 claims.

SAFE (#15) extends the same idea with a different decomposition and, importantly, a different
*judge*: instead of a learned NLI model, an LLM agent breaks the answer into facts, issues real
Google searches for each, and checks whether the search results support it. The advantage is that
the evidence is not limited to the retrieval corpus — which matters for an industrial system whose
corpus may be incomplete. SAFE agrees with crowdsourced annotators **72%** of the time on ~16k
facts, and wins **76%** of the 100 cases where they disagreed. It is also **>20× cheaper** than
human annotation.

SAFE also contributes a metric idea worth stealing: extend F1 to long-form factuality by balancing
the percentage of *supported* facts (precision) against the percentage of *provided* facts
relative to a hyperparameter representing the user's preferred response length (recall). This
directly addresses a failure mode that pure precision metrics reward: answering with one
conservative sentence and claiming 100% faithfulness.

### 2.4 Sentence-level attribution and why NLI is the right tool (TRUE)

Honovich et al. (#8) did the unglamorous work that makes all of the above trustworthy: they
meta-evaluated the metrics themselves. They assembled a standardised, manually annotated corpus
across 11 datasets and evaluated a wide range of factual-consistency metrics at the **example
level**, not merely by system-level correlation with human scores.

Two of their findings drive the thesis's implementation choices:

1. **Large-scale NLI models and question-generation-and-answering approaches are strong and
   complementary.** NLI asks "does this passage entail this claim?" — direct, cheap, and exactly
   the question a citation check needs. QA-based approaches ask "what does the passage say about
   X?" and compare — more robust when the passage and the claim are phrased very differently, but
   more expensive. For a system that must attach a tag to *every* claim in *every* answer, NLI is
   the right default and QA is the escalation path for low-confidence cases.

2. **System-level correlation is the wrong meta-evaluation protocol.** A metric can correlate
   0.9 with human scores at the system level and still mislabel most individual claims. Since the
   thesis's contribution is *per-claim* tagging, the meta-evaluation must be per-claim. This is a
   concrete, checkable design requirement for the evaluation chapter.

### 2.5 Per-claim confidence and the three-band tag

The thesis proposes three bands: **grounded** (directly entailed by a cited chunk), **inferred**
(requires combining or reasoning beyond the cited chunk), **uncertain** (not adequately supported).

This is a sound design and it has an anchor in the literature. Semantic entropy (#25) shows that
uncertainty must be measured over *meanings*, not strings: two different sentences can mean the
same thing, so a model that generates "187 units" and "the EOQ equals 187 units" is not twice as
uncertain. Kuhn, Gal and Farquhar's semantic entropy clusters semantically-equivalent outputs and
computes entropy over the clusters, and show it is **more predictive of QA accuracy than comparable
baselines**, while remaining unsupervised, single-model, and requiring **no modification to
off-the-shelf LLMs**. That last property is exactly what an M.Tech project wants: no fine-tuning
budget, no training pipeline.

The mapping to three bands is a thresholding decision on top of an underlying continuous score.
Two implementation notes matter:

- The score must be computed **per claim**, not per answer. Semantic entropy as originally
  formulated is per-generation; per-claim adaptation requires generating or scoring each claim in
  isolation, or using an attention-based consistency score as in #28.
- The bands must be **calibrated on held-out data** — see the evaluation protocol in §3. Without
  calibration, "grounded / inferred / uncertain" is a decorative label.

### 2.6 What it costs to tag every claim (and why the paper's stack is right)

Cost per answer, for a claim-level tagging system:

| Stage | Model calls per answer | Notes |
|---|---|---|
| Answer decomposition | 1 | one LLM call to split the answer into atomic claims |
| Per-claim entailment (NLI) | *n* claims | one cheap classifier call per claim |
| Citation linking | 1 | map each claim to the chunk it came from |
| Band assignment | 0 | thresholding, no model call |
| **Total** | **≈ n + 2** | for a 6-claim answer: ~8 calls |

The dominant cost is *n*, the claim count, and NLI models are small enough that this is affordable.
A `cross-encoder/nli-deberta-v3-small` style classifier runs on CPU in milliseconds. The
architecture in the thesis's own stack table — using a small GLiNER/DeBERTa cross-encoder rather
than the main LLM — is therefore the correct engineering choice, not a compromise.

Two consequences for the thesis:

1. **The tagging stage must be off the critical path of the answer.** It can run after generation.
   Nothing about the answer changes because of the tag.
2. **The tag is a claim about the evidence, not about the model.** "Grounded" means "entailed by the
   cited chunk". It does not mean "true in the world". The thesis should say this explicitly,
   because an examiner will ask.

### 2.7 LLM-as-judge: what the failure modes actually are

Because the thesis's own plan annotates a 500-question benchmark "by LLM agents using a structured
protocol", the judge's biases are not a footnote — they are a threat to the validity of the entire
empirical section. Four papers measure them:

**Position bias** (#32) is the most dramatic. Simply reordering the two candidate responses in the
judge's context changes the verdict often enough that, with ChatGPT as judge, **Vicuna-13B beat
ChatGPT on 66 of 80 tested queries**. For a paired-comparison design — "does system A or system B
produce the more faithful answer?" — this is fatal unless positions are balanced and averaged.
The fix in #32 is **Balanced Position Calibration**: run every pair in both orders and aggregate.
That doubles judge cost and is cheap. Do it.

**Verbosity bias and self-enhancement bias** (#31) mean judges prefer longer answers and answers
that look like their own model's output. This creates a systematic confound in a comparison study:
if one baseline produces longer answers, it will score higher on faithfulness for reasons unrelated
to faithfulness. Control for answer length, or report it.

**Scale and setup sensitivity** (#33) tested 13 judge models against 9 exam-taker models. Only the
best and largest aligned reasonably with humans — and even they still differed from human-assigned
scores by **up to 5 points**, with a **tendency toward leniency**. The authors' closing advice is
directly applicable: *"the fact that even the best judges differ from humans in this comparatively
simple setup suggest that caution may be wise when using judges in more complex setups."* An
industrial QA benchmark with domain jargon is more complex, not less.

**Agreement is a ceiling, not a guarantee** (#31) is the good news: a strong judge reaches **>80%
agreement** with human preference, which is *the same level as human–human agreement*. Combined
with the other findings, the defensible position is: LLM judges are good enough for **screening**
and **relative comparison**, and **not** good enough to be the sole source of absolute numbers.

**Mitigations the thesis should adopt**, all from #32 and #31:
- Balanced position calibration (both orders, averaged).
- Multiple-evidence calibration (judge generates supporting rationale before rating).
- A **human-validated subset** — the proposal already promises this ("human-expert validation on a
  random subset to be reported"). Keep it, and report the agreement rate between the judge and the
  human on that subset. That number is a result in itself: it characterises the instrument.
- Report inter-annotator agreement (κ) for the human subset. AVeriTeC (#14) reports **κ = 0.619**
  as a realistic target for a multi-source evidence task — a good anchor for what to expect.

### 2.8 Confidence gating and abstention: where the thesis actually stands

This is the section the thesis's defence will turn on, so it is worth being blunt.

**The thesis cannot claim to be first to gate RAG on retrieval confidence.** TRAQ (#24) claims the
*first end-to-end statistical correctness guarantee for RAG*, using conformal prediction and
Bayesian optimisation to shrink prediction sets by 16.2%. Conformal-RAG (#27) applies conditional
conformal prediction to **sub-claims** — almost exactly the thesis's D5 — and reports retaining
**up to 60% more high-quality sub-claims** than naive CP. And the 2026 Factual Confidence Prediction
paper (#28) is a two-stage design that first uses conformal prediction to select retrieved chunks
and then scores answer–context consistency with an attention-based classifier, reporting up to **6%**
answer-quality improvement and **up to 77%** detection of inconsistent answers.

The honest conclusion: **"gate on retrieval confidence" is established prior art.** The thesis's
defensible novelty is narrower and still real:

1. **Code-level, non-bypassable enforcement.** All of #24, #27, #28 are *models or statistical
   wrappers*. A code-level gate sits outside the LLM's control: the LLM is never called when
   confidence is below threshold, so it cannot be talked out of the refusal by prompt injection in
   the retrieved text, and it cannot be overridden by a chat template or a tool call. That is a
   **security property**, and it is the kind of property industrial buyers actually pay for. Frame
   it as such.
2. **Domain-specific calibration on industrial corpora.** #28's own warning is the opportunity:
   it states that the statistical guarantee "does not hold generally, since the assumption of
   sample exchangeability depends on the retriever setup." A calibrated static threshold for
   *supply-chain* technical documentation on a *specific* corpus is a legitimate contribution, and
   the thesis should present it as the empirical answer to that warning rather than as a rival to
   conformal prediction.
3. **Per-claim three-band tagging surfaced to the practitioner** as a decision aid — a UI and
   cognitive-ergonomics contribution that the statistical papers do not make. #28 and #27 measure;
   they do not show an engineer a grounded/inferred/uncertain tag and study whether it changes the
   decision.
4. **The industrial grounding.** RAGBench (#21) is the closest analogue in the literature — 100k
   examples across five industry domains, sourced from *user manuals* — and it is a benchmark, not
   a system. The thesis's combination of industrial corpus + industrial category routing +
   practitioner-facing uncertainty is not yet done.

**URAG (#29) supplies the sharpest warning.** Its finding (1) — accuracy gains often coincide with
reduced uncertainty, **but this relationship breaks under retrieval noise** — is a direct caution
against reading a confidence gate as a hallucination fix in the presence of noisy retrieval.
Finding (4) is worse: retrieval depth, parametric-knowledge dependence, and **exposure to
confidence cues can amplify confident errors and hallucinations**. And SealQA (#23) shows the
frontier is nowhere near solving this: o3 scores **17.1%** and o4-mini **6.3%** on Seal-0, reasoning
models are "highly vulnerable to noisy search results", and **more test-time compute does not
yield reliable gains**.

So the defensible claim is *narrower and stronger* than "we reduce hallucination":

> A code-level confidence gate **trades coverage for correctness**, and the trade is measurable and
> domain-specific. The contribution is not that the gate prevents hallucination — it is that the
> gate's operating point, its cost in refused questions, and its behaviour under retrieval noise
> are *characterised* for industrial technical documentation.

That framing survives a hostile examiner. "We reduce hallucination by X%" does not.

### 2.9 Failure modes of attribution that the thesis should measure

The benchmark literature names concrete failure modes that map directly onto industrial scenarios.
The thesis should report each as a separate number:

- **Negative rejection failure** (RGB #18). The system retrieves documents that do not answer the
  question and then answers anyway. RGB found LLMs "struggle significantly" here. This is the
  failure a confidence gate exists to catch — so the gate's value should be reported *specifically*
  on negative-rejection cases, not averaged over everything.
- **Contradiction / conflicting-evidence failure** (SealQA #23, #14). When sources disagree, the
  system silently picks one. AVeriTeC's multi-round annotation was designed specifically to avoid
  "context dependence, evidence insufficiency, and temporal leakage" — three failure modes that
  industrial corpora hit constantly, because a 2023 spec and a 2025 spec disagree and both are
  valid in their time.
- **Temporal leakage** (#14). Industrial documentation is versioned. A system that retrieves a
  superseded spec and presents it as current has produced a correct answer to a stale question.
  Nothing in standard RAGAS/RGB handles this. It is a genuine industrial-specific gap.
- **Evidence granularity mismatch** (FEVEROUS #13). FEVEROUS annotates claims against *table
  cells* as well as sentences, and its baseline gets both evidence and verdict right for only **18%**
  of claims. If the thesis's system cites a sentence that happens to sit near the right table, that
  is a false positive an NLI judge might accept. The thesis should test whether its citation
  *points to the right cell*.
- **List/multi-answer failure** (QAMPARI #10). "What is the safety-stock rule for X?" may have a
  *set* of correct answers. The best QAMPARI model scores F1 = 32.8. If the industrial benchmark
  includes such questions, per-claim tagging has to handle the case where one claim is right and
  another is wrong in the same answer.
- **Multi-hop failure** (MultiHop-RAG #11). Existing RAG systems are "inadequate" at multi-hop.
  Industrial questions are frequently multi-hop ("what is the EOQ for SKU A-104, and which
  incoterm applies to its supplier?"). If the benchmark has no multi-hop questions, the thesis
  cannot claim industrial readiness.

---

## 3. Recommended evaluation protocol

This is the section most directly usable in the thesis's Methodology and Evaluation chapters. It is
written to be defensible under review, and it accounts for the specific constraint that the
industrial user study is small.

### 3.1 The metric set

Report these, per system, on the same benchmark questions:

| Layer | Metric | Definition | Source |
|---|---|---|---|
| Retrieval | Recall@k | fraction of gold evidence chunks present in top-k | standard IR |
| Retrieval | nDCG@k | rank-discounted retrieval quality | standard IR |
| Retrieval | MRR | mean reciprocal rank of first gold chunk | standard IR |
| Context | Context precision | # relevant retrieved chunks / # retrieved chunks | RAGAS #16 |
| Context | Context recall | # gold chunks retrieved / # gold chunks | RAGAS #16 |
| Generation | Faithfulness | # claims entailed by context / # claims | RAGAS #16, TRUE #8 |
| Attribution | Citation precision | # correct citations / # citations emitted | ALCE #1 |
| Attribution | Citation recall | # supported claims that are correctly cited / # supported claims | ALCE #1 |
| Attribution | Complete citation support | fraction of claims fully supported *and* correctly cited | ALCE #1 |
| Per-claim | Band calibration | P(grounded) vs observed entailment rate, per band, with reliability diagram | calibration literature |
| Refusal | Abstention precision / recall | of the "no evidence" responses, how many were correct | see §3.3 |
| End-to-end | Answer accuracy | exact-match / F1 / rubric score, human-validated subset | — |

**Complete citation support is the single most important number for this thesis.** It is the metric
that captures "the answer shows its work", and it is directly comparable with ALCE's published
figures — which makes the thesis's contribution legible against the prior state of the art.

### 3.2 Statistical tests — choose by data type, and state which

| Situation | Test | Why |
|---|---|---|
| **Paired binary outcome** (same question, system A faithful / system B faithful) | **McNemar's exact test** on the discordant pairs | The contingency table's off-diagonal cells are the only informative ones; χ² is invalid at small counts, so use the exact variant |
| **Paired continuous/ordinal** (per-question faithfulness score) | **Wilcoxon signed-rank** | Robust to the severe non-normality that LLM-judge scores have |
| **Effect size for Wilcoxon** | **rank-biserial correlation** *r* = (W+ − W−)/(W+ + W−) | Report this, not just *p* |
| **Interval estimates** | **BCa bootstrap 95% CI**, 10,000 resamples, over questions | Percentile bootstrap is anti-conservative for skewed statistics like the median |
| **Many comparisons** (multiple metrics × baselines) | **Benjamini–Hochberg** FDR control | Family-wise correction is too conservative and the reviewer will ask anyway |
| **Effect size for McNemar** | odds ratio of discordant pairs, with CI | *p* alone is not enough |
| **Small-N user study (N = 16)** | **Exact binomial / sign test** on per-participant outcomes; report the CI | See §3.4 |
| **Multiple annotators** | **Cohen's κ** (2 annotators) or **Krippendorff's α** (>2), with CI | AVeriTeC (#14) reports κ = 0.619 for a comparable task |

State the test *before* reporting. State *n* for every test. Report effect sizes with every *p*.

### 3.3 Measuring the confidence gate specifically

The gate deserves its own evaluation, separate from answer quality — otherwise the thesis cannot
show that the gate works.

**1. Operating curve.** Sweep the threshold τ over its full range. For each τ plot:
- answer coverage = fraction of questions that reach the LLM at all,
- answer accuracy on the answered subset,
- the *joint* product (accuracy × coverage), which is the quantity that matters — a gate that
  refuses everything scores 100% accuracy at 0% coverage.

**2. Abstention correctness.** Split refusals into:
- *correct refusals* — the evidence genuinely does not answer the question (verify against the
  gold evidence set),
- *incorrect refusals* — the system refused a question the corpus does answer.

Report both. **Incorrect refusals are the cost the practitioner pays**, and they are invisible if
only overall accuracy is reported.

**3. Calibration.** For each posterior value *p* produced by the gate, bin the questions and plot
observed correctness against *p*. Report **Expected Calibration Error (ECE)** with the binning
scheme stated. A gate that is well-calibrated will have observed accuracy ≈ *p*; the Bayesian
posterior framing in the thesis's §7.5 is only worth anything if this holds on held-out industrial
data. Note that #28 found the exchangeability assumption behind this kind of guarantee can fail
for a particular retriever — so report the calibration diagnostic explicitly.

**4. Calibration set independence.** The proposal reports β₀ = 2.943, β₁ = 1.680 from a **30-query**
set. A logistic regression with two parameters fitted on 30 points has very wide coefficient
confidence intervals. **Refit on the full calibration set, report the intervals, and hold out a
test portion** — a threshold calibrated and evaluated on the same 30 queries is not evidence.

**5. Robustness under retrieval noise.** Per URAG (#29) finding (1), the accuracy–confidence
relationship breaks under noisy retrieval. Run the gate with (a) clean retrieval, (b) retrieval
with irrelevant documents injected, (c) retrieval with contradictory documents injected, and report
the calibration curve for each. This is the most likely place for the thesis's approach to look
weak, and the right move is to find it yourself and report it.

### 3.4 The N = 16 user study — what is and is not defensible

The proposal's report (September 2026) describes a practitioner user study with N = 16 participants,
already noted as "at the lower bound of the 15-participant target". Here is what can and cannot be
claimed.

**Not defensible at N = 16:**
- Any generalisation to "industrial engineers" as a population.
- Sub-group analyses (by experience, role, or domain) — with 16 participants, a 4-way split gives
  4 people per cell.
- Any claim of statistical significance on a continuous outcome. A two-sample t-test at N = 16 has
  ~50% power to detect a large effect (d = 1.0) at α = 0.05. Power analysis should be reported.

**Defensible at N = 16:**
- **Within-participant (repeated-measures) comparisons.** Every participant sees both systems, so
  the paired design removes between-person variance. Use **Wilcoxon signed-rank** on the per-person
  differences. This is the single most important design decision, and the thesis should state that
  it is a within-subject design.
- **Directional consistency.** Report how many of the 16 participants preferred system A, with a
  **sign test** and its exact binomial CI. If 14/16 prefer A, the two-sided sign test gives
  *p* ≈ 0.002 — a legitimate and honest small-sample result, presented as such, not as a
  general claim.
- **Effect size with CI**, not just a *p*-value.
- **Individual-level trajectories.** Showing each participant's before/after decision with a
  confidence band is more informative than a bar chart, and reviewers in HCI-adjacent work expect it.
- **Reported as a pilot study**, explicitly. Framing it as a pilot is not weakness; it is
  calibration, and the supervisor will respect it.

**Strengthen it cheaply.** Two options, both feasible before 18 November:
- Raise N to 25–30 by adding colleagues. Cost: a one-page consent form and an hour each.
- Run a second cohort. Two independent cohorts of 12 with the same protocol is a stronger design
  than one cohort of 24, because it lets you check the effect replicates.

**Also report, because it is free:** the *process* metrics, not just the outcome metrics —
time-to-decision, number of citations opened, number of times the practitioner chose to override
the tag. "Engineers opened the cited table 3.2 times per answer and overrode the grounded tag in
11% of cases" is a real finding about how uncertainty labels are used in practice, and no prior
paper measures it.

### 3.5 The benchmark annotation protocol

The proposal's "500-question benchmark annotated by LLM agents using a structured protocol" needs
the following, to be credible:

1. **Two independent annotators** per question (or two agents with different prompts + seeds), with
   a **disagreement adjudication** step. Report Cohen's κ on the adjudication set.
2. **A human-expert validation subset** — the proposal promises this. Minimum 50 questions
   (10%) with two domain experts each. Report judge-vs-human agreement. For ALCE-style tasks
   where published LLM-judge agreement is ~72–80% (#1, #15), anything at or above that is a
   respectable result; anything below 60% is a red flag you should report rather than hide.
3. **Balanced position calibration** on every paired comparison (#32).
4. **Fixed seeds and pinned model versions** recorded in the artefacts. Reviewers replicate.
5. **The annotation rubric published** as an appendix, with the exact prompt templates.
6. **A held-out human-written subset** (not LLM-annotated) used to validate the *benchmark itself*
   — otherwise the benchmark and the system are evaluated by the same instrument, which is
   circular. This is a subtle and important point: if the LLM agent annotates the benchmark and the
   LLM agent grades the system's answers, a shared bias inflates every number. At minimum, report
   results with LLM-annotated and human-annotated subsets **separately**.

---

## 4. What this thesis can claim

**Defensible now:**

1. That per-claim three-band tagging (grounded / inferred / uncertain) is a well-motivated
   response to a documented failure mode — the atomic-fact decomposition of FActScore (#7) and
   SAFE (#15), and the example that ChatGPT's biographies are only 58% factually supported.
2. That the metric suite above is the right one, and that the thesis's numbers are directly
   comparable with ALCE's published complete-citation-support figures (#1) — which is where the
   "even the best models lack complete citation support 50% of the time on ELI5" baseline lives.
3. That a **code-level, non-bypassable** gate is architecturally different from the learned
   reflection tokens of Self-RAG, the trained evaluator of CRAG, the conformal wrappers of TRAQ /
   Conformal-RAG, and the attention classifier of #28 — because it cannot be overridden by the
   model. This is a **systems** claim, not an accuracy claim, and it should be argued as such.
4. That the domain-specific calibration of a static gate on industrial technical documentation is
   a genuine contribution *because* the statistical guarantee in #28 is stated to depend on the
   retriever setup, and the thesis supplies the diagnostic for that assumption in a domain where
   nobody has.
5. That the practitioner-facing use of uncertainty tags (a human-factors contribution) is
   unmeasured in the literature — RAGTruth (#19) and ExpertQA (#6) measure *machine* detection of
   hallucination; ASTRID (#22) measures metric agreement with clinicians. None measures whether a
   tag changes a decision.

**Defensible only with the right hedging:**

6. "Reduces hallucination" → prefer "**improves the rate of evidenced claims at a measured cost in
   coverage**", with the operating curve in §3.3. URAG (#29) and SealQA (#23) make a broad
   hallucination-reduction claim risky.
7. "Per-claim confidence" → note that Conformal-RAG (#27) already provides **group-conditional
   conformal guarantees on sub-claims**, which is stronger than a static threshold. The thesis's
   version should be described as a *practitioner-facing, corpus-calibrated* alternative to
   conformal sets — not as superior to them.

**Not defensible:**

8. "The first to gate RAG on retrieval confidence." TRAQ (#24) claims a stronger prior.
9. "Improves answer quality." #28 reports up to 6% from chunk filtering alone, so the bar is low
   and the claim is unimpressive next to it. Report the gate's *safety* behaviour instead.
10. Anything about the joint NLI + topical gate's false-positive rate unless it is measured on a
   labelled contradiction set with a published protocol. A number like "16% FP" (the September 2026
   report's figure) is **not a defensible finding without a labelled gold set** — it is currently a
   number in a report with no stated denominator. Either build the gold set (the thesis already has
   the machinery for expert annotation) or present the figure as preliminary.

---

## 5. Gaps and risks

**Risk 1 — The novelty is thinner than the framing suggests.** The literature of 2023–2026 has
covered confidence-gated RAG, conformal sub-claim guarantees, and two-stage factuality prediction.
A defence that presents "we gate on retrieval confidence" as the contribution will be undercut by
TRAQ and #28. *Mitigation:* reframe the contribution around the code-level non-bypassable
architecture, the industrial calibration, and the practitioner-facing tags; and add TRAQ, #27, #28,
#29 to the literature review as *closest work*, not as background. A reviewer who sees them named
and addressed will trust the rest.

**Risk 2 — The instrument may be invalid.** LLM-annotated gold + LLM-graded answers + LLM-judge
biases is a compounding-validity problem, and three papers (#31–#33) show the biases are large
enough to flip rankings. *Mitigation:* §3.5 — balanced positions, human validation subset with
reported agreement, and separate reporting for human-annotated vs LLM-annotated subsets.

**Risk 3 — Small-N overreach.** Already covered in §3.4. The single highest-value action is
raising N or running a second cohort.

**Risk 4 — The modality result is a null and the benchmark is too small to detect anything.**
RAGBench (#21) has 100k examples; ExpertQA (#6) has 2,177 across 32 fields with 484 experts;
AVeriTeC (#14) has 4,568 claims from 50 organisations. A 500-question benchmark across 12
industrial categories is ~40 questions per category. That is enough for a rough per-category
comparison and **not** enough for fine-grained per-category claims or for a meaningful κ on
per-category estimates. The thesis should report per-category results with wide CIs and be explicit
that cross-category transfer (RO4/H4.1) is tested at low power.

**Risk 5 — Industrial corpora are versioned and the benchmark is not.** AVeriTeC (#14) went to
specific lengths to avoid temporal leakage; RGB (#18) has a dedicated counterfactual-robustness
testbed. If the industrial corpus contains superseded specifications and the benchmark questions
do not pin a version, the "contradiction detection" result may be measuring version skew rather
than reasoning. *Mitigation:* annotate each gold answer with the document version/date, and treat
cross-version disagreement as a separate, reportable class rather than a contradiction.

**Risk 6 — The per-claim tag may be a label without a decision.** If engineers ignore the
grounded/inferred/uncertain tag, D5 is decoration. *Mitigation:* measure override rate and
time-to-decision in the user study (§3.4). If the tag is ignored, that is a *finding* about how
uncertainty should be surfaced, and it is a more interesting result than another accuracy point.

**Risk 7 — Reference integrity.** Two reference-list errors are already confirmed (§1.5): the
"Microsoft Research" authorship of arXiv:2507.21502 and the "Application-Oriented" vs
"Capability-Oriented" subtitle of arXiv:2510.24476. Two performance figures (77.8%, 92.4%) are
unverified. Turnitin similarity checking will not catch these, but an examiner checking two
references will. Fix them before submission.

---

## 6. Reproducibility notes

Every verification command used in this survey is in this environment and can be re-run:

```bash
# batch-verify arXiv IDs (one request; prints title/authors/date/comments/journal-ref/DOI/abstract)
python3 /tmp/arxiv_batch.py 2305.14627 2309.15217 2401.00396 ...

# Semantic Scholar metadata + citation counts for a list of arXiv IDs or DOIs
python3 /tmp/s2_batch.py ARXIV:2305.14627 DOI:10.1016/j.aei.2025.103212 ...

# Crossref record for a published article (authors, volume, issue, pages, cited-by)
python3 /tmp/doi.py 10.1016/j.aei.2025.103212 10.3390/math13050856 ...

# arXiv title -> ID resolution when an ID is unknown
python3 /tmp/ax.py <(echo '["ti:\"QAMPARI\""]')
```

Note for future runs: `export.arxiv.org/api/query` allows roughly one request per three seconds
and returns **429** under concurrent load. Batching many IDs into one `id_list` request is both
faster and politer than one request per paper.

---

## 7. Cross-references to the other surveys

| Thesis component | Survey file | Overlap |
|---|---|---|
| RO1 / D1 confidence gate | `01_confidence_gating.md` | TRAQ, Conformal-RAG, semantic entropy, URAG, Factual Confidence Prediction appear in both |
| RO2 / D2 modality quotas | `02_modality_balanced.md` | FEVEROUS (#13) is the table-evidence precedent; RAGBench (#21) is the industrial-corpus precedent |
| RO3 / D3 hybrid retrieval | `03_hybrid_retrieval.md` | ARES (#17) and RAGAS (#16) evaluate the retrieval leg this survey treats as a component |
| RO4 / D4 contradiction surfacing | `04_contradiction.md` | AVeriTeC (#14), VitaminC (#12), SealQA (#23) and URAG (#29) all bear on conflict handling |

---

*Survey compiled with direct source verification. 31 papers fully verified with abstracts and
metadata; 4 journal articles verified via DOI records; 2 specific performance figures in the
proposal's literature table could not be confirmed and are flagged UNVERIFIED.*
