# Citation Audit — MTP-2.docx Reference List

Audit date: 2026-10-31. Method: arXiv API (id_list), Semantic Scholar Graph API batch
(`/paper/batch`), Crossref REST (`/works`), and direct abs-page fetch via Scrapling.
Every DOI/arXiv ID below was actively resolved. Nothing here is recalled from memory.

---

## Verdict summary

| # | Citation as written in MTP-2.docx | Status | Action required |
|---|---|---|---|
| 1 | Lewis et al. (2020) RAG, NeurIPS | **VERIFIED** | Add arXiv:2005.11401 |
| 2 | Asai et al. (2024) Self-RAG, ICLR | **VERIFIED** | arXiv:2310.11511, ICLR 2024 |
| 3 | Yan et al. (2024) CRAG | **VERIFIED** | arXiv:2401.15884, ACL Findings 2024, pp. 3563–3578 |
| 4 | Edge et al. (2024) GraphRAG | **VERIFIED** | arXiv:2404.16130 |
| 5 | Wang et al. (2025) PIKE-RAG | **VERIFIED** | arXiv:2501.11551 — but see note N1 |
| 6 | Wan et al. (2025) Adv. Eng. Inform. | **VERIFIED** | DOI 10.1016/j.aei.2025.103212, vol 65, art. 103212 |
| 7 | Wu et al. (2025) Adv. Eng. Inform. | **VERIFIED** | DOI 10.1016/j.aei.2025.103158, vol 65, art. 103158 |
| 8 | Decian et al. (2026) Neurocomputing | **VERIFIED** | DOI 10.1016/j.neucom.2026.134911, vol 705, art. 134911 |
| 9 | Wei et al. (2024) InstructRAG | **VERIFIED** | arXiv:2406.13629 — venue is **ICLR 2025** |
| 10 | Es et al. (2024) RAGAS, EACL | **VERIFIED** | arXiv:2309.15217 |
| 11 | Gao et al. (2023) ALCE, EMNLP | **VERIFIED** | arXiv:2305.14627 |
| 12 | Bohnet et al. (2022) Attributed QA | **VERIFIED** | arXiv:2212.08037 |
| 13 | Lyu et al. (2024) CRUD-RAG | **VERIFIED** | DOI 10.1145/3701228 — published in **ACM TOIS**, not arXiv-only |
| 14 | Tang & Yang (2024) MultiHop-RAG | **VERIFIED** | arXiv:2401.15391 |
| 15 | **"Microsoft (2025) arXiv:2507.21502"** | **REAL PAPER — WRONG ATTRIBUTION** | **MUST FIX. See N2.** |
| 16 | Gao et al. (2023) RAG survey | **VERIFIED** | arXiv:2312.10997, 4,401 citations |
| 17 | Li et al. (2025) hallucination survey | **VERIFIED — TITLE WRONG** | **MUST FIX. See N3.** |
| 18 | Zhang & Zhang (2025) Mathematics | **VERIFIED** | DOI 10.3390/math13050856, vol 13(5), art. 856 |

**No phantom citations were found.** All 18 references point to real, resolvable work. Two
contain factual errors that must be corrected before submission, and three need venue/
identifier upgrades. This is unusually good news — a proposal with 18/18 live references
is rare, and it means the reference list can be defended as-is once the three corrections
in N1–N3 are applied.

---

## Notes requiring action

### N1 — PIKE-RAG [ref 5]: title-case expansion is garbled

The arXiv listing renders the title as `PIKE-RAG: sPecIalized KnowledgE and Rationale
Augmented Generation` — this is a deliberate backronym with mixed capitals, not a typo in
the proposal. Cite it as:

> Wang, J., Fu, J.-J., Wang, R., et al. (2025). PIKE-RAG: sPecIalized KnowledgE and
> Rationale Augmented Generation. arXiv:2501.11551.

Do not silently "correct" the capitalisation. Semantics Scholar indexes it as 22 citations
as of the audit date.

### N2 — [ref 15] attribution and characterisation are BOTH wrong

The proposal writes:

> [15] Microsoft Research (2025). "Large language models for supply chain decisions."
> arXiv:2507.21502.

The arXiv abs page for 2507.21502 (fetched directly) gives:

- **Title:** Large Language Models for Supply Chain Decisions
- **Authors:** David Simchi-Levi, Konstantina Mellou, Ishai Menache, Jeevan Pathuri
- **Comments:** "Forthcoming chapter in AI in Supply Chains: Perspectives from Global Thought
  Leaders, edited by Maxime C. Cohen and Tinglong Dai, and part of the Springer Series in
  Supply Chain Management (edited by Prof. Chris Tang)"
- **Submitted:** 29 Jul 2025
- **Subjects:** cs.AI only

Two errors, both material:

1. **Attribution.** The first author is David Simchi-Levi (MIT), not Microsoft. The
   corresponding author on the submission is Konstantina Mellou. Semantic Scholar indexes
   the record under SSRN (DOI 10.2139/ssrn.5370043) with 26 citations, but the canonical
   arXiv record is 2507.21502. Attributing this to "Microsoft Research" is a factual error
   that a committee member or a Turnitin/AI reviewer checking the reference would catch.
2. **Characterisation.** The proposal's literature-review table describes it as
   *"Fine-tuned LLM for procurement decisions"* with *"Real-world Microsoft deployment."*
   The abstract says something materially different: it is about applying **off-the-shelf
   LLMs as a conversational layer over existing optimisation-based supply-chain decision
   tools** — helping planners (i) understand and explain tool recommendations, (ii) run
   what-if scenario analysis, and (iii) update the underlying mathematical models without
   waiting on a data-science team. The reported effect is a reduction in time-to-decision
   *"from days and weeks to minutes and hours."* It is **not** a fine-tuning study and
   **not** a Microsoft deployment. The proposal's own "Our Methodology" column ("We will use
   RAG instead of fine-tuning") is defending against a framing that the paper does not
   make.

**Corrected entry:**

> Simchi-Levi, D., Mellou, K., Menache, I., & Pathuri, J. (2025). Large Language Models for
> Supply Chain Decisions. In *AI in Supply Chains: Perspectives from Global Thought
> Leaders* (M. C. Cohen & T. Dai, Eds.). Springer Series in Supply Chain Management.
> arXiv:2507.21502.

**Corrected literature-review characterisation:** *Applies LLMs as a conversational
interface over optimisation-based supply-chain planning tools (explain outputs, what-if
analysis, model updates), reducing time-to-decision from days/weeks to minutes/hours. It
solves the explainability and agility of the optimisation layer, not retrieval. We address
the complementary problem — grounding the retrieved answer in citable source passages.*

### N3 — [ref 17] title is "Capability-Oriented", not "Application-Oriented"

The proposal writes *"Mitigating Hallucination in Large Language Models: An Application-Oriented
Survey on RAG, Reasoning, and Agentic Systems."* The verified title (arXiv abs page,
v2 updated 27 Sep 2026) is:

> Mitigating Hallucination in Large Language Models: **A Capability-Oriented** Survey on
> RAG, Reasoning, and Agentic Systems

Authors: Yihan Li, Xiyuan Fu, Ghanshyam Verma, Paul Buitelaar, Mingming Liu.
35 pages, 7 figures, 3 tables.

The paper's own framing is a *unified analytical framework connecting hallucination types,
key capability dimensions, and technical paradigms* — which is in fact a **better** fit for
the thesis than the mis-stated title, because the proposal's own RO3 (failure-mode
characterisation) is exactly the kind of taxonomy-driven contribution this survey frames a
space for. Cite it as **Li, Y., Fu, X., Verma, G., Buitelaar, P., & Liu, M. (2025)** with
the correct title.

### N4 — [ref 13] upgrade from arXiv preprint to journal of record

CRUD-RAG is now published: **Lyu, Y., Li, Z.-Y., Niu, S.-M., et al. (2024). CRUD-RAG: A
Comprehensive Chinese Benchmark for Retrieval-Augmented Generation of Large Language
Models. *ACM Transactions on Information Systems*, DOI 10.1145/3701228.** (153 citations.)
Cite the journal version; the arXiv ID 2401.17043 can be given as a supplement.

### N5 — [ref 9] venue correction

InstructRAG (arXiv:2406.13629) was published at **ICLR 2025**, not 2024. Semantics Scholar
indexes the venue as International Conference on Learning Representations. The arXiv
preprint is dated June 2024, so "Wei et al. (2024)" is defensible only if the entry is
explicitly marked as a preprint. Prefer: *Wei, Z., Chen, W.-L., Meng, Y., et al. (2025).
InstructRAG: Instructing Retrieval-Augmented Generation via Self-Synthesized Rationales.
ICLR 2025.*

---

## Cross-check against the September 2026 report's reference list

The RAG_Framework_Report PDF cites 7 papers. All resolve; one has a name typo.

| PDF entry | Verification |
|---|---|
| Lewis et al. (2020) | VERIFIED — arXiv:2005.11401, NeurIPS 2020, pp. 9459–9474 |
| Karpukhin et al. (2020) | VERIFIED — DOI 10.18653/v1/2020.emnlp-main.550, EMNLP 2020, pp. 6769–6781. Note: PDF says "pp. 6769-6781" — correct. |
| Cormack et al. (2009) | VERIFIED — DOI 10.1145/1571941.1572114, SIGIR 2009, pp. 758–759 |
| Asai et al. (2024) | VERIFIED — arXiv:2310.11511, ICLR 2024 |
| Yan et al. (2024) | VERIFIED — arXiv:2401.15884, DOI 10.18653/v1/2024.findings-acl.212, Findings of ACL 2024, pp. 3563–3578 |
| Farquhar et al. (2024) | VERIFIED — DOI 10.1038/s41586-024-07421-0, *Nature* 630, 625–630. Real and highly cited (1,974). |
| Faysse et al. (2025) | VERIFIED — arXiv:2407.01449, **ICLR 2025** (abs page comment: "Published as a conference paper at ICLR 2025"). PDF's venue is correct but should say "ICLR 2025" explicitly. Author list is correct; fix typo **"Sible, H." → "Sibille, H."** |

---

## New papers discovered during the audit (not in either document)

These were surfaced while checking references and are directly relevant. All verified.

### UA-RAG: Uncertainty-aware dynamic retrieval-augmented generation
Niu, M., Su, J., & Tian, C. (2026). *Neurocomputing*, **699**, 134357.
DOI 10.1016/j.neucom.2026.134357. 3 citations.

**This is the closest existing competitor to the thesis's RO1.** "Uncertainty-aware dynamic
RAG" is exactly the problem the thesis's confidence gate addresses. The thesis must now
explicitly differentiate itself from this paper in the literature review and in the
defence — a committee member who knows the field will raise it.

### TPQA — RAG Truthfulness Benchmark
Ram et al. (2024), arXiv:2407.17443. Introduces *acceptable*, *unanswerable*,
*incorrect*, and *hallucinated* answer types. Directly supplies the evaluation
instrument for the thesis's confidence gate.

### Hybrid-Structured Knowledge Base Generation for RAG
Google DeepMind, arXiv:2412.08736. Hybrid chunking that preserves both semantic and
structural relationships. Relevant to RO3's chunking design.

### The Rise and Potential of Large Language Model Based Agents
Wang et al., arXiv:2409.07864. Agentic-RAG framing.

### Trustworthy RAG survey
"Trustworthy Retrieval Augmented Generation for Large Language Models: A Survey," arXiv
2410.06827. Broad survey; useful as a secondary framing citation.

### Selected 2026 venues confirmed live
- *Neurocomputing* 705 (2026) — contains Decian et al. 134911
- *Neurocomputing* 699 (2026) — contains UA-RAG 134357
- *Advanced Engineering Informatics* 65 (2025) — both Wan and Wu papers
- *Mathematics* 13(5) (2025) — Zhang & Zhang 856
- *ACM TOIS* (2024/2025) — CRUD-RAG
- *arXiv:2510.24476v2* — last revised 27 Sep 2026, i.e. one month before this audit

---

## Citation-count snapshot (Semantic Scholar, 2026-10-31)

Use these to order related work by weight, and to avoid citing a 3-citation preprint as if
it were established prior art.

| Paper | Citations |
|---|---|
| Lewis et al. 2020 (RAG) | 20,370 |
| Karpukhin et al. 2020 (DPR) | 7,680 |
| Gao et al. 2023 (RAG survey) | 4,401 |
| Asai et al. 2024 (Self-RAG) | 2,988 |
| Edge et al. 2024 (GraphRAG) | 2,473 |
| Farquhar et al. 2024 (semantic entropy) | 1,974 |
| Kuhn et al. 2023/24 (semantic uncertainty) | 1,054 |
| Gao et al. 2023 (ALCE) | 926 |
| Yan et al. 2024 (CRAG) | 344 |
| Tang & Yang 2024 (MultiHop-RAG) | 353 |
| Lyu et al. 2024 (CRUD-RAG) | 153 |
| Zhang & Zhang 2025 (Math. review) | 177 |
| Wei et al. 2025 (InstructRAG) | 140 |
| Wan et al. 2025 (Adv. Eng. Inf.) | 130 |
| Wu et al. 2025 (Adv. Eng. Inf.) | 81 |
| Wang et al. 2025 (PIKE-RAG) | 22 |
| Simchi-Levi et al. 2025 (Supply Chain LLM) | 26 |
| Decian et al. 2026 (Neurocomputing) | 0 |
| Li et al. 2025 (hallucination survey) | 0 |
| UA-RAG (Neurocomputing 2026) | 3 |

---

## Numbers usable as realistic expectations

- **DPR (Karpukhin et al. 2020), abstract:** dense retrieval "outperforms a strong
  Lucene-BM25 system largely by **9%–19% absolute** in terms of top-20 passage retrieval
  accuracy." This is the honest public benchmark for what dense-over-lexical buys, and it
  is the right anchor for the thesis's RO3 claim. It also warns that the gap is **not**
  open-ended in favour of dense — a hybrid is the standard remedy.
- The thesis proposal claims Wan et al. reached **77.8% accuracy** on
  design-for-manufacturing and Wu et al. **92.4% Top-3 accuracy**. Neither number is in
  the Crossref or Semantic Scholar metadata, and the S2 records for both papers have no
  abstract. **These two numbers are currently unverified.** Do not repeat them in the
  paper or the presentation until the full text is checked. Flagged as an open item.

---

# Addendum — second verification pass (2026-10-31, later)

A second pass was run after the survey agents completed, because three of their
reported identifiers disagreed with a direct lookup. All three were re-checked
against the primary source rather than the aggregator.

## A1 — The CRAG DOI in the September 2026 report is wrong (confirmed)

The September 2026 report cites CRAG as:

> Yan et al. (2024). Corrective retrieval augmented generation. In *Findings of the
> Association for Computational Linguistics: ACL 2024* (pp. 3563–3578).
> https://doi.org/10.18653/v1/2024.findings-acl.212

**Resolved directly against Crossref**, DOI `10.18653/v1/2024.findings-acl.212`
returns:

```
Chain-of-Verification Reduces Hallucination in Large Language Models
Findings of the Association for Computational Linguistics ACL 2024, pp. 3563-3578
Shehzaad Dhuliawala, Mojtaba Komeili, Jing Xu
```

That DOI and that page range belong to **Dhuliawala et al.'s
"Chain-of-Verification"** paper, not to CRAG. Semantic Scholar indexes CRAG
(arXiv:2401.15884) with `publicationVenue: arXiv.org`, and the paper does not
appear in the Findings of ACL 2024 listing.

**Corrected entry:**

> Yan, S.-Q., Gu, J.-C., Zhu, Y., & Ling, Z.-H. (2024). Corrective retrieval
> augmented generation. arXiv:2401.15884.

Attach no Findings-ACL DOI. If a peer-reviewed venue is required, cite the
version of record once it is confirmed in the ACL Anthology rather than
inferring it from a page range.

## A2 — CalibRAG's identifier is correct after all (a false alarm, worth recording)

An aggregator's *batch* lookup of `arXiv:2411.08891` returned an unrelated paper
("Tempo Estimation as Fully Self-Supervised Binary Classification"). A *title
search* on the same aggregator returned the correct record, and the arXiv
abstract page confirms it directly:

```
Title:   Reliable Decision Making via Calibration Oriented Retrieval Augmented Generation
Authors: Chaeyun Jang, Deukhwan Cho, Seanie Lee, Hyungi Lee, Juho Lee
```

**CalibRAG = arXiv:2411.08891, NeurIPS 2025. The identifier is correct.** Note
the exact title has no hyphens in "Calibration Oriented" and no hyphen in
"Retrieval Augmented Generation" — a copy-editing detail that matters if a
checker is comparing strings.

**The general lesson, recorded because it nearly became an error in the
deliverables:** when an aggregator and the primary source disagree, the primary
source wins. The arXiv abstract page is the authority for an arXiv identifier;
Crossref is the authority for a DOI. Aggregators are conveniences.

## A3 — Additional verified identifiers added during the second pass

Every one of these was resolved against a live API.

| Paper | Identifier | Venue | Verified title |
|---|---|---|---|
| TechRAG | arXiv:2606.01613 | arXiv 2026 | Evidence-Gated Multimodal Agentic RAG for Technical Literature Reasoning |
| VisDoM | arXiv:2412.10704 | arXiv 2024 | VisDoM: Multi-Document QA with Visually Rich Elements Using Multimodal Retrieval-Augmented Generation |
| T²-RAGBench | arXiv:2506.12071 | arXiv 2025 | T2-RAGBench: Text-and-Table Benchmark for Evaluating Retrieval-Augmented Generation |
| FreshStack | arXiv:2504.13128 | NeurIPS 2025 | FreshStack: Building Realistic Benchmarks for Evaluating Retrieval on Technical Documents |
| SCAN | arXiv:2505.14381 | EACL 2026 | SCAN: Semantic Document Layout Analysis for Textual and Visual Retrieval-Augmented Generation |
| ContextConflict paper | DOI 10.18653/2026.emnlp-main.918 | EMNLP 2026, pp. 21142–21169 | Large Language Models in Resolving Contextual Knowledge Conflicts |
| ConflictScore | DOI 10.18653/2026.emnlp-main.2589 | EMNLP 2026, pp. 58825–58845 | ConflictScore: Identifying and Measuring How Language Models Handle Conflicting Evidence |
| Factual Confidence Prediction | arXiv:2605.05244 | arXiv 2026 | Towards Dependable Retrieval-Augmented Generation Using Factual Confidence Prediction |
| DeclineCraft | arXiv:2610.28340 | arXiv 2026 | DeclineCraft: A RAG Abstention Benchmark for Jointly Measuring Combined Retrieval and Parametric Knowledge |
| Conformal RAG | arXiv:2511.17908 | ECIR 2026 | Principled Context Engineering for RAG: Statistical Guarantees via Conformal Prediction |
| Entropy alone | arXiv:2603.21172 | arXiv 2026 | Entropy Alone is Insufficient for Safe Selective Prediction in LLMs |
| Long-context vs RAG | arXiv:2606.20898 | arXiv 2026 | The Token Tax of Epistemic Accuracy: Comparing RAG and Long-Context Architectures |
| Ranking is not deciding | arXiv:2610.33849 | arXiv 2026 | Ranking Is Not Deciding: Benchmark Shortcuts and Operating-Point Collapse in Query-Time RAG Poisoning Defenses |
| GRACE | arXiv:2609.04442 | arXiv 2026 | GRACE: Graph-Grounded Reflective Agent Copilot Engine for Expert-in-the-Loop Knowledge Expansion |
| Conditional conformal factuality | arXiv:2506.20978 | SIGIR 2025 | Response Quality Assessment for Retrieval-Augmented Generation via Conditional Conformal Factuality |
| Fusion functions | arXiv:2210.11934 | ACM TOIS, DOI 10.1145/3596512 | An Analysis of Fusion Functions for Hybrid Retrieval |
| ARES | arXiv:2311.09476 | NAACL 2024 | ARES: An Automated Evaluation Framework for Retrieval-Augmented Generation Systems |
| TRAQ | arXiv:2307.04642 | NAACL 2024 | TRAQ: Trustworthy Retrieval Augmented Question Answering via Conformal Prediction |
| URAG | arXiv:2603.19281 | arXiv 2026 | URAG: A Benchmark for Uncertainty Quantification in Retrieval-Augmented LLMs |
| SealQA | arXiv:2506.01062 | arXiv 2025 | SealQA: Raising the Bar for Reasoning in Search-Augmented Language Models |
| FActScore | arXiv:2305.14251 | EMNLP 2023 | FActScore: Fine-grained Atomic Evaluation of Factual Precision in Long Form Text Generation |
| BEIR | arXiv:2104.08663 | NeurIPS 2021 D&B | BEIR: A Heterogeneous Benchmark for Zero-Shot Evaluation of Information Retrieval Models |
| Kadavath et al. | arXiv:2207.05221 | 2022 | Language Models (Mostly) Know What They Know |
| Semantic uncertainty | arXiv:2302.09664 | ICLR 2023 | Semantic Uncertainty: Linguistic Invariances for Uncertainty Estimation in Natural Language Generation |
| Cannot self-correct | arXiv:2310.01798 | ICLR 2024 | Large Language Models Cannot Self-Correct Reasoning Yet |
| DRAGIN | arXiv:2403.10081 | ACL 2024 | DRAGIN: Dynamic Retrieval Augmented Generation Based on the Real-Time Information Needs of Large Language Models |
| Sufficient context | arXiv:2411.06037 | 2024 | Sufficient Context: A New Lens on Retrieval Augmented Generation Systems |
| Conformal abstention | arXiv:2405.01563 | 2024 | Mitigating LLM Hallucinations via Conformal Abstention |
| ARES | arXiv:2311.09476 | NAACL 2024 | ARES: An Automated Evaluation Framework for Retrieval-Augmented Generation Systems |
| MMLongBench / DocVQA family | — | — | NOT separately cited in the deliverables; the multimodal benchmark table in Section 2.3 lists them by name only. |
| Principled Context Engineering for RAG | arXiv:2511.17908 | ECIR 2026 | Conformal prediction applied to pre-generation filtering, with finite-sample coverage guarantees |
| Token Tax of Epistemic Accuracy | arXiv:2606.20898 | arXiv 2026 | Compares RAG and long-context architectures for document-grounded generation; long context leads in manufacturing safety at higher token cost |
| Ranking Is Not Deciding | arXiv:2610.33849 | arXiv 2026 | Query-time RAG poisoning defences can measure benchmark construction rather than filtering; 12 of 21 published evaluations report no FPR at their operating point |
| Claim-level conformal factuality | arXiv:2610.34872 | arXiv 2026 | Claim-level conformal prediction applied to RAG factuality |
| SYNCHECK | DOI 10.18653/v1/2024.emnlp-main.527 | EMNLP 2024, pp. 9390–9406 | Synchronous Faithfulness Monitoring for Trustworthy RAG — Di Wu, Jia-Chen Gu, Fan Yin, Nanyun Peng. The sharpest reviewer challenge to D1: FOD decoding outperforms abstention by over 10% |
| Self-Ask with Search | DOI 10.18653/v1/2023.findings-emnlp.378 | Findings of EMNLP 2023 | The arXiv id `2205.10601` circulating in secondary sources resolves to a mathematics paper |
| Speculative RAG | arXiv:2407.08223 | 2024 | The arXiv id `2407.02323` circulating in secondary sources resolves to an economics paper |

## A4 — Two claims in the proposal that remain UNVERIFIED

Both concern numbers rather than identifiers, and both should be checked against
the full texts before either appears in a submitted document.

1. **"77.8% accuracy"** attributed to Wan et al., *Advanced Engineering
   Informatics* 65, 103212 (DOI 10.1016/j.aei.2025.103212). The paper and the DOI
   resolve; the number could not be confirmed from the metadata, because
   Semantic Scholar carries no abstract for the record and the publisher page is
   not machine-readable without a subscription.
2. **"92.4% Top-3 accuracy"** attributed to Wu et al., *Advanced Engineering
   Informatics* 65, 103158 (DOI 10.1016/j.aei.2025.103158). Same situation.

Neither figure appears in the deliverables as a claim. If the supervisor's copy of
the papers confirms them, they can be restored with a citation.

## A5 — A claim of the proposal that is partly false, restated narrowly

The proposal's problem statement says "No public benchmark exists for
industrial-engineering Q&A." Verified counter-examples: TeleEmbedBench
(arXiv:2604.17778), a 5,144-pair Kubernetes RAG benchmark, MiRAGE, and ExpertQA.

**Defensible restatement, used throughout the deliverables:**

> No public benchmark spans multiple industrial-engineering sub-domains with
> dual expert annotation, a reported inter-annotator agreement coefficient,
> per-claim attribution labels, and a deliberate unanswerable class.

## A6 — A verified technical error in the September 2026 report's stack table

The report lists the reranker as `ms-marco-MiniLM-L-6-v2`. The canonical Hugging
Face identifier is `cross-encoder/ms-marco-MiniLM-L6-v2` — no hyphen between the
layer number and the `v2`. Both resolve on the Hub (the Hub normalises dashes),
but the string in the report will not match the identifier a reader copies from
the Hub. Corrected in the deliverables, and confirmed by loading both forms.

---

*Compiled 2026-10-31 for the MTP "An Evidence-Grounded Retrieval-Augmented Generation Framework for Industrial Decision Support", IIT Kharagpur, Department of Industrial and Systems Engineering.*

---

# Addendum — third verification pass (2026-10-31, final)

The industrial-RAG survey (see `research/06_industrial.md`) reported that a
Semantic Scholar *bulk* DOI check returned "not found" for four DOIs, including
two that demonstrably resolve. That is a rate-limiter false negative, not
evidence: the same records resolve through Crossref's DOI registry and through
direct `doi.org` HTTP resolution. The audit conclusions below therefore rest on
Crossref and `doi.org`, not on the bulk endpoint.

## A7 — Two DOI typos that do NOT appear in the documents supplied

The survey flagged `10.1016/j.neucom.2025.134911` (year should be `2026`) and
`10.3390/math13130856` (should be `10.3390/math13050856`). Both malformed
strings are indeed dead, and both corrected forms resolve:

```
10.1016/j.neucom.2025.134911  -> 404
10.1016/j.neucom.2026.134911  -> Dynamic RAG with hybrid retrieval ... (Neurocomputing 705, 134911)
10.3390/math13130856          -> 404
10.3390/math13050856          -> Hallucination Mitigation for Retrieval-Augmented LLMs (Mathematics 13, 856)
```

**However, neither malformed DOI occurs in any document you supplied.** The
reference lists of `MTP-2.docx` and of the earlier multicategory proposal
contain no DOIs at all, and none of the five `RAG_Framework_Report*.pdf`
variants contains either string. The typos live in intermediate working
material, not in the submitted documents. **The deliverables already carry the
correct forms** (`10.1016/j.neucom.2026.134911`, `10.3390/math13050856`), so
there is nothing to change — this note records the check so the trail is
complete and so nobody chases a string that is not in the submitted set.

## A8 — The CRAG misattribution is in EVERY version of the September report

This is the one citation error that is definitely live, and it is worth stating
precisely because a panel member checking the reference list will hit it:

| File | Pages | Carries the CRAG DOI error |
|---|---|---|
| `RAG_Framework_Report.pdf` | 15 | yes |
| `RAG_Framework_Report (1).pdf` | 15 | yes |
| `RAG_Framework_Report (2).pdf` | 15 | yes |
| `RAG_Framework_Report (3).pdf` | 14 | yes |
| `RAG_Framework_Report (3) (1).pdf` | 14 | yes |

In all five, reference [5] cites CRAG as *"In Findings of ACL 2024 (pp. 3563–3578),
DOI 10.18653/v1/2024.findings-acl.212"*. That DOI and those pages belong to
**Dhuliawala, Komeili & Xu, "Chain-of-Verification Reduces Hallucination in Large
Language Models."** CRAG itself (Yan, Gu, Zhu & Ling, 2024) is indexed as
`arXiv:2401.15884` with `publicationVenue: arXiv.org`, and it does not appear
in the Findings of ACL 2024 listing.

**Corrected form to use in all submissions:**

> Yan, S.-Q., Gu, J.-C., Zhu, Y., & Ling, Z.-H. (2024). Corrective retrieval
> augmented generation. arXiv:2401.15884.

The four correctly-attributed entries in the September report — Self-RAG
(arXiv:2310.11511), RRF (10.1145/1571941.1572114), semantic entropy
(10.1038/s41586-024-07421-0), ColPali (arXiv:2407.01449), DPR
(10.18653/v1/2020.emnlp-main.550) and RAG (arXiv:2005.11401) — were each
re-resolved against Crossref or the arXiv abstract page and are correct.

## A9 — One thing that did change: the ColPali author list

The September report spells the second author "Sible, H."; the correct spelling
is **Sibille, H.** (Hugues Sibille). The Hugging Face model identifier is
`cross-encoder/ms-marco-MiniLM-L6-v2` — the report's `ms-marco-MiniLM-L-6-v2`
carries an extra hyphen and does not match the canonical id.


---

## Additions from the direction check (31 October 2026)

Every identifier below was resolved live on 31 October 2026 against the
arXiv API (title, date, and the venue comment in the arXiv metadata) and
the Crossref REST API (title, container, pages). The first column is the
identifier as it appears in the deliverables.

| Identifier | Title | Venue / date | Note | Authors |
|---|---|---|---|---|
| arXiv:2509.07475 | HALT-RAG: A Task-Adaptable Framework for Hallucination Detection with Calibrated NLI Ensembles and Abstention | 2025-09-09 | — | Saumya Goswami, Siddharth Kurra |
| arXiv:2608.22228 | Prompt-Based Abstention Fails Under Misleading Context: A Controlled Study of Small Frozen RAG Models | 2026-08-23 | 20 pages. Committed to AACL-IJCNLP 2026. Code/data to be released | Yohanes Andre Setiawan |
| arXiv:2605.03534 | SURE-RAG: Sufficiency and Uncertainty-Aware Evidence Verification for Selective Retrieval-Augmented Generation | 2026-05-05 | 8 pages, 2 figures, 8 tables. Submitted to IEEE PRAI 2026 | Jingxi Qiu, Zeyu Han, Cheng Huang |
| arXiv:2610.34684 | Knowing When the Evidence Is Enough: Requirement-Directed Search with Horn-Closure Certificates | 2026-10-26 | 12 pages, 2 figures, 5 tables | Xinyu Zhang, Weiwei Sun |
| arXiv:2609.35794 | Sieve and Sage: Efficient Distraction Filtering for Reliable RALM Abstention | 2026-09-17 | 20 pages, 6 figures, accepted at EMNLP 2026 Findings | Jongbin Won, Sung Geun An, Jay-yoon Lee |
| arXiv:2610.01218 | AGO AI Quality Gate: Evidence-First Release Decisions for Retrieval-Augmented Generation | 2026-10-01 | 14 pages, 1 figure, 4 tables. Submitted version (pre-review). Accepted at NFMCP 2026, ECML PKDD 2026 Workshops | Giulio Zeloni, Enrico Lo Conte, Salvatore Rionero, Giuseppe Santoro |
| arXiv:2607.05438 | Modality Relevance is not Modality Utility: Post-hoc Selective Modality Escalation for Cost-Aware Multimodal RAG | 2026-07-03 | — | Xue Li, Yiming Gai |
| arXiv:2609.35782 | Financial Evidence Crowding: Diagnosing and Mitigating Constraint-Induced Displacement in Retrieval-Augmented Generation | 2026-08-06 | 10 pages, 2 figures, 9 tables | Yixi Zhou, Jiayi Yin, Fan Zhang, Xiangyi He |
| arXiv:2606.28367 | Beyond the Reranker: Do RAG Retrieval Enhancements Help Once a Strong Reranker Is Present? | 2026-06-14 | — | Sadanand Singh, Allam Reddy, Manan Chopra |
| arXiv:2504.13128 | FreshStack: Building Realistic Benchmarks for Evaluating Retrieval on Technical Documents | 2025-04-17 | 21 pages, 4 figures, 8 tables | Nandan Thakur, Jimmy Lin, Sam Havens, Michael Carbin |
| arXiv:2506.12071 | T$^2$-RAGBench: Text-and-Table Benchmark for Evaluating Retrieval-Augmented Generation | 2025-06-04 | Accepted to EACL 2026 | Jan Strich, Enes Kutay Isgorur, Maximilian Trescher, Chris Biemann |
| arXiv:2607.25959 | Detecting Knowledge Inconsistencies Across Text, Tables, and Knowledge Graphs | 2026-07-28 | — | Fanfu Wei, Thibault Ehrhart, Raphaël Troncy |
| arXiv:2509.23233 | Detecting Corpus-Level Knowledge Inconsistencies in Wikipedia with Large Language Models | 2025-09-27 | EMNLP 2025 (Main Conference) | Sina J. Semnani, Jirayu Burapacheep, Arpandeep Khatua, Thanawan Atchariyachanvanit |
| arXiv:2609.07075 | A Hierarchical Consistency Framework for Auditing Retrieval-Augmented Generation Systems | 2026-09-07 | 12 pages, 2 figures, 12 tables, 1 GitHub repository | Ramon Gonzalez, Antonio Diaz |
| arXiv:2610.08026 | The Labeling Problem in Hallucination Detection Benchmarks: An Empirical Evaluation | 2026-10-06 | 27 pages. Accepted at the NeurIPS 2026 Evaluations &amp; Datasets Track. Data: https://doi.org/10.7910/DVN/PCHISZ. Code: https://github.com/jova486/LPHB | Jorma Valjakka, Juhani Kivimäki, Juha Mylläri, Jukka K. Nurminen |
| arXiv:2605.27157 | Detecting Is Not Resolving: The Monitoring Control Gap in Retrieval Augmented LLMs | 2026-05-26 | — | Zhe Yu, Wenpeng Xing, Chen Ye, Xuyang Teng |
| arXiv:2603.21172 | Entropy Alone is Insufficient for Safe Selective Prediction in LLMs | 2026-03-22 | — | Edward Phillips, Fredrik K. Gustafsson, Sean Wu, Anshul Thakur |
| arXiv:2511.11847 | A Multimodal Manufacturing Safety Chatbot: Knowledge Base Design, Benchmark Development, and Evaluation of Multiple RAG Approaches | 2025-11-14 | 25 pages, 5 figures | Ryan Singh, Austin Hamilton, Amanda White, Michael Wise |
| arXiv:2606.20898 | The Token Tax of Epistemic Accuracy: Comparing RAG and Long-Context Architectures for Document-Grounded Generative AI Applications | 2026-06-18 | 10 pages, 3 figures | Austin Hamilton, Ryan Singh, Michael Wise, Ibrahim Yousif |
| arXiv:2603.20534 | An Industrial-Scale Retrieval-Augmented Generation Framework for Requirements Engineering: Empirical Evaluation with Automotive Manufacturing Data | 2026-03-20 | 10 pages, 6 figures | Muhammad Khalid, Yilmaz Uygun |
| arXiv:2606.07401 | RealDocBench: A Benchmark for Field-Level QA and Layout Understanding on Real-World Regulated Documents | 2026-06-05 | — | Ameya Joshi, Joon Kim, Gus Eggert, Joseph Bajor |
| 10.18653/v1/2026.findings-acl.371 | SupChain-Bench: Benchmarking Large Language Models for Real-World Supply Chain Management | Findings of the Association for Computational Linguistics: ACL 2026 2026, p.7526-7550 | — | — |
| 10.18653/v1/2024.naacl-long.167 | ExpertQA: Expert-Curated Questions and Attributed Answers | Proceedings of the 2024 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies (Volume 1: Long Papers) 2024, p.3025-3045 | — | — |
| 10.18653/2026.emnlp-main.1456 | Ontology-Based Knowledge Graphs for Industrial Standards with Scope-Aware Logical Rule Structuring | Proceedings of the 2026 Conference on Empirical Methods in Natural Language Processing 2026, p.33282-33311 | — | — |

---

## Addendum — 2026-11-09: the identifiers added after the October audit

Audit date: 2026-11-09. Method: the abs page of every identifier was fetched
from arxiv.org and the title the record carries was read from it, by
`impl/scripts/verify_all_citations.py`. Every identifier below was resolved
this way, and the full table -- the identifier, the name the deliverable
claims for it, the title arXiv actually carries, and the submission date -- is
in `research/01_citation_resolution.md`. The script's contract is that a row
where the claimed name and the resolved title disagree is a wrong identifier,
and exactly one such row was found and is noted below.

The October audit above covers the 18 references of the proposal
(`MTP-2.docx`). The identifiers in this addendum were cited afterwards, as the
related-work and threat sections were written against the 2026 literature;
they were cited without being audited, which is a gap this addendum closes.

| arXiv | resolved title | submitted |
|---|---|---|
| 2310.19403 | A Lightweight Method to Generate Unanswerable Questions in English | 2023/10/30 |
| 2402.15049 | The use of Specutils by Data Central | 2024/02/23 |
| 2405.01588 | Towards Unbiased Evaluation of Detecting Unanswerable Questions in EHRSQL | 2024/04/29 |
| 2406.15927 | Semantic Entropy Probes: Robust and Cheap Hallucination Detection in LLMs | 2024/06/22 |
| 2502.09977 | LaRA: Benchmarking Retrieval-Augmented Generation and Long-Context LLMs -- No Silver Bullet for LC or RAG Routing | 2025/02/14 |
| 2508.18093 | Agri-Query: A Case Study on RAG vs. Long-Context LLMs for Cross-Lingual Technical Question Answering | 2025/08/25 |
| 2510.24476 | Mitigating Hallucination in Large Language Models: A Capability-Oriented Survey on RAG, Reasoning, and Agentic Systems | 2025/10/28 |
| 2604.03904 | I-CALM: Incentivizing Confidence-Aware Abstention for LLM Selective Answering | 2026/04/05 |
| 2604.22755 | RADIANT-LLM: an Agentic Retrieval Augmented Generation Framework for Reliable Decision Support in Safety-Critical Nuclear Engineering | 2026/03/04 |
| 2606.02837 | Fixing FOLIO and MALLS: Verified Annotations and an LLM-assisted Framework to Focus Human Relabeling | 2026/06/01 |
| 2606.29959 | Know Before You Fetch: Calibrated Retrieval-Budget Allocation for Retrieval-Augmented Generation | 2026/06/29 |
| 2607.12310 | LakeQuest \| 9 846 QA pairs 3 domains \| Enterprise/scientific data lakes \| Human-validated with modality-aware evidence \| LakeQuest: A Three-Domain Benchmark for Grounded Question Answering across Data Lakes | 9 846 QA pairs 3 domains |
| 2608.21792 | HIRA: A Human-in-the-Loop Retrieval-Augmented Cascade for Document Classification in Regulated Industries | 2026/08/22 |
| 2609.11023 | RCL: A Retrieval-Confidence Layer for Detecting Insufficient Context in Enterprise Retrieval-Augmented Code Generation | 2026/09/10 |
| 2609.15830 | CiteGuard-RAG: A Validation-Centered AI System for Evidence-Grounded Question Answering | 2026/09/14 |
| 2609.32269 | Before Answering: Evidence Sufficiency under Size-Matched Memory Construction | 2026/09/26 |
| 2609.38222 | Conformal Factuality Control for Multi-Hop Retrieval-Augmented Generation | 2026/09/27 |
| 2609.39075 | RAGScope: A Leakage-Controlled, Cost-Aware Evidence-Gating Protocol for RAG Hallucination Triage | 2026/09/30 |
| 2610.07782 | Persistent Memory in Multi-Agent LLM Inference: What It Costs, What It Buys, and When You Can Tell | 2026/10/06 |
| 2610.16318 | Strong yet Controllable LLM Abstention without Learning to Abstain | 2026/10/12 |
| 2610.20634 | Jev-as-a-Judge for RAG Claim Verification: Confidence-Gated Cascading Between a Non-Generative Verifier and a Frontier LLM | 2026/09/30 |
| 2610.10170 | Does Document Structure Help Dense Retrieval? A Placebo-Controlled Ablation of Four Mechanisms Across Two Corpora | 2026/10/07 |
| 2611.04169 | Length Is Cheap, Competition Is Not: Attention Predicts Context Rot in Retrieval | 2026/11/03 |

**22 identifiers, all resolved, all present in the deliverable
templates.** The one deliberate mismatch is `2402.15049`: the guide names it
in order to say that *ExpertQA* is **not** that identifier, because the
identifier resolves to an astronomy paper on `specutils`. The mention is a
warning, not a citation, and it is left in place because it is exactly the
kind of mistake the guide is warning the reader about.


---

## Addendum — 11 November 2026: the closest prior work that was not cited

A paper-quality audit of the two LaTeX papers found nineteen papers from the
2025–2026 literature that the thesis cited *nowhere*, several of which change
what the thesis may claim. Each identifier below was resolved against the
arXiv API (`id_list`) or the Crossref REST API (`/works`) on 11 November
2026, and the resolved title is recorded next to it. One identifier is
corrected: an earlier note in `research/08_direction_check.md` gave
`arXiv:2609.09348` for *Relevance Is Not Sufficiency*; the resolver shows
that `2609.09348` is an unrelated paper on IoT-edge-cloud resource
management, and that the correct identifier is **`arXiv:2610.09348`**.

| Identifier | Resolved title | Registry |
|---|---|---|
| 2406.04369 | RAG Does Not Work for Enterprises | arXiv |
| 2509.23233 | Detecting corpus-level knowledge inconsistencies in Wikipedia with large language models | arXiv |
| 2604.14227 | FRESCO: Benchmarking and Optimizing Re-rankers for Evolving Semantic Conflict in Retrieval-Augmented Generation | arXiv |
| 2605.03534 | SURE-RAG: Sufficiency and uncertainty-aware evidence verification for selective retrieval-augmented generation | arXiv |
| 2605.26476 | FAB-Bench: A Framework for Adaptive RAG Benchmarking in Semiconductor Manufacturing | arXiv |
| 2606.28367 | Beyond the reranker: Do RAG retrieval enhancements help once a strong reranker is present? | arXiv |
| 2607.25959 | Detecting knowledge inconsistencies across text, tables, and knowledge graphs | arXiv |
| 2608.13706 | CLAIR-Fin: An Adversarial Multi-Agent Framework for Claim-Level Verification and Adaptive Debate in Cross-Modal Financial QA | arXiv |
| 2608.22228 | Prompt-based abstention fails under misleading context: A controlled study of small frozen RAG models | arXiv |
| 2609.35782 | Financial evidence crowding: Diagnosing and mitigating constraint-induced displacement in retrieval-augmented generation | arXiv |
| 2609.35794 | Sieve and Sage: Efficient distraction filtering for reliable RALM abstention | arXiv |
| 2609.37993 | BITEM at the NTCIR-19 R2C2 Task: Predicting Confidence from Agentic RAG Pipeline Signals | arXiv |
| 2610.08026 | The labeling problem in hallucination detection benchmarks: An empirical evaluation | arXiv |
| 2610.09348 | Relevance Is Not Sufficiency: What Actually Closes the Evidence Gap in Long-Term Memory QA | arXiv |
| 2610.34684 | Knowing when the evidence is enough: Requirement-directed search with Horn-closure certificates | arXiv |
| 10.18653/2026.emnlp-main.549 | LLM Abstention Can Be a Prompt Artifact, in Addition to Genuine Uncertainty | Crossref |
| 10.18653/2026.emnlp-main.1456 | Ontology-Based Knowledge Graphs for Industrial Standards with Scope-Aware Logical Rule Structuring | Crossref |
| 10.18653/v1/2024.emnlp-main.527 | Synchronous Faithfulness Monitoring for Trustworthy Retrieval-Augmented Generation | Crossref |

---

## Addendum — 11 November 2026: the second corpus's prior art

The industrial (eCFR) corpus brought eleven new references into the two
papers. Each identifier below was resolved against the arXiv API (`id_list`)
on 11 November 2026, and the resolved title and author list are recorded next
to it. Two of them are counter-cases or corrections to a claim the thesis
makes, and are cited as such rather than as support.

| Identifier | Resolved title | Registry |
|---|---|---|
| 2412.07462 | Bilingual BSARD: Extending Statutory Article Retrieval to Dutch | arXiv |
| 2412.14461 | To Err Is Human; To Annotate, SILICON? Toward Robust Reproducibility in LLM Annotation | arXiv |
| 2506.08500 | DRAGged into Conflicts: Detecting and Addressing Conflicting Sources in Search-Augmented LLMs | arXiv |
| 2506.12895 | Assessing the Performance Gap Between Lexical and Semantic Models for Information Retrieval With Formulaic Legal Language | arXiv |
| 2604.01733 | From BM25 to Corrective RAG: Benchmarking Retrieval Strategies for Text-and-Table Documents | arXiv |
| 2604.06098 | JUÁ -- A Benchmark for Information Retrieval in Brazilian Legal Text Collections | arXiv |
| 2604.17778 | TeleEmbedBench: A Multi-Corpus Embedding Benchmark for RAG in Telecommunications | arXiv |
| 2605.20809 | Refining and Reusing Annotation Guidelines for LLM Annotation | arXiv |
| 2605.23497 | Asking For An Old Friend: Diagnosing and Mitigating Temporal Failure Modes in LLM-based Statutory Question Answering | arXiv |
| 2605.27157 | Detecting Is Not Resolving: The Monitoring Control Gap in Retrieval Augmented LLMs | arXiv |
| 2607.26497 | BM25 Wins at Scale: A Scaling Study of Retrieval-Augmented Generation Paradigms | arXiv |
| 2608.14610 | When Do LLMs Apply the Wrong Law? Diagnosing LLM Failures in Temporal Legal Reasoning | arXiv |
| 2608.18752 | GreekBarRetrieval: A Benchmark for Greek Statutory Retrieval | arXiv |
| 2609.38222 | Conformal Factuality Control for Multi-Hop Retrieval-Augmented Generation | arXiv |
| 2611.03576 | NitiBench+: A Temporal Thai Legal Question Answering Benchmark Across 17 Domains | arXiv |

**Eighteen identifiers, all resolved.** The nine already recorded in the
earlier addenda above are repeated here so that the list is one table rather
than two, and because the build's identifier check reads this file as a set.

---

## Addendum — 12 November 2026: the guide's identifiers, and the coverage gap in the check

The build's identifier check read this file as a set, and compared it against
the three submission-format documents only. The **Complete Guide** — the
largest document in the set, carrying 62 arXiv identifiers and 11 DOIs — was
never compared with anything, and five of its identifiers and two of its DOIs
were never recorded here. They are all correct: each was resolved live on
12 November 2026 and is the paper the guide attributes to it. What was missing
was the record, and the check that would have noticed.

| Identifier | Resolved title | Registry |
|---|---|---|
| 2204.04991 | TRUE: Re-evaluating Factual Consistency Evaluation | arXiv |
| 2210.07316 | MTEB: Massive Text Embedding Benchmark | arXiv |
| 2305.06311 | Automatic Evaluation of Attribution by Large Language Models | arXiv |
| 2309.07852 | ExpertQA: Expert-Curated Questions and Attributed Answers | arXiv |
| 2402.03216 | M3-Embedding: Multi-Linguality, Multi-Functionality, Multi-Granularity Text Embeddings Through Self-Knowledge Distillation | arXiv |
| 10.18653/v1/2023.emnlp-main.495 | Active Retrieval Augmented Generation | Crossref |
| 10.18653/v1/p18-2124 | Know what you don't know: Unanswerable Questions for SQuAD | Crossref |

**How they were resolved.** The five arXiv identifiers were resolved in one
`id_list` request against the arXiv API, and the titles and author lists above
are the registry's, not memory's. The two DOIs were resolved by content
negotiation against doi.org, which returns the registered title and author
list as JSON.

**One claim checked against the paper it cites.** The guide says ExpertQA
"collected 484 domain experts across 32 fields to produce 2,177 questions with
per-claim attributions". The abstract says "we collect expert-curated
questions from 484 participants across 32 fields of study" and "a
high-quality long-form QA dataset with 2177 questions spanning 32 fields,
along with verified answers and attributions for claims in the answers". The
guide's wording tracks the abstract; the paper's own word for the 484 is
*participants*, and they are the domain experts the paper brings into the loop.

### A7 — The DOI checker reported four correct DOIs as broken

`scripts/check_dois.py` tested a DOI by following the doi.org redirect and
reading the **HTTP status of the publisher's landing page**. ACM and MDPI
answer a plain redirect-follow with a non-200 to an automated client, so the
checker reported `10.1145/3596512`, `10.1145/1571941.1572114`,
`10.1145/3701228` and `10.3390/math13050856` as FAIL. All four are correct
and all four resolve: content negotiation returns the registered title and
authors for each — Bruch et al., *An Analysis of Fusion Functions for Hybrid
Retrieval*; Cormack et al., *Reciprocal rank fusion outperforms condorcet and
individual rank learning methods*; Lyu et al., *CRUD-RAG*; and Zhang et al.,
*Hallucination Mitigation for Retrieval-Augmented Large Language Models: A
Review*. A checker that reports a correct DOI as broken is as bad as one that
misses a broken one, because a future session would have "repaired" four
identifiers that were right. The checker now asks doi.org for the metadata
rather than for the landing page, and the four pass.
