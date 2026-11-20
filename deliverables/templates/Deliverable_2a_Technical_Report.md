# An Evidence-Grounded Retrieval-Augmented Generation Framework for Industrial Decision Support: Architecture, Evaluation Protocol, and Failure-Mode Characterisation

**Ritik Raj [25IM60R12]** — Department of Industrial and Systems Engineering, Indian Institute of Technology Kharagpur
**Supervisor:** Dr. Sri Krishna Kumar

*Single-column technical report format. The IEEE two-column and journal-format versions of this paper are Deliverables 2b and 2c.*

---

## Abstract

Industrial practitioners make decisions from paperwork: standard operating procedures, failure-mode and effects analyses, control plans, maintenance logs, calibration records and supplier documents. Generic large language model (LLM) assistants answer such questions fluently but cannot be trusted, because there is no trace from a number back to the page that justifies it, no way to distinguish an inferred claim from a stated one, and no warning when two sources disagree. Retrieval-augmented generation (RAG) grounds the answer in retrieved passages, but existing systems trust the retriever unconditionally, ignore modality diversity, and silently pick one source when documents conflict. In an industrial setting a wrong economic order quantity, wrong incoterm, or wrong safety-stock rule can stop a production line, misplace inventory, or fail an audit. This paper presents a five-mechanism framework for industrial decision support: a code-level, non-bypassable retrieval-confidence gate that returns an explicit "no evidence" response without invoking the language model; per-modality retrieval quotas; hybrid lexical–dense retrieval with a category pre-filter fused by reciprocal rank fusion and reranked by a cross-encoder; contradiction surfacing through a joint natural-language-inference (NLI) and topical gate; and per-claim three-band confidence tagging. We are explicit about what is and is not novel. Every architectural component has published prior art, which we position against rather than claim priority over; our substantive contribution is a failure-mode characterisation, obtained on an independently constructed public industrial corpus of {{N_CHUNKS}} chunks across {{N_CATEGORIES_WORD}} categories and a {{N_QUERIES}}-query silver-standard benchmark containing deliberately unanswerable questions, with supply chain management as the single industrial domain the work focuses on — the ablation and gate measurements are taken on that domain's {{N_FOCUS_CHUNKS}}-chunk subset ({{N_FOCUS_QUERIES}} queries), and the remaining categories carry the cross-category transfer study. We observe, on a corpus independent of the one originally used, the regression of cross-encoder reranking on recall, together with the candidate-pool curve that explains it — a curve that peaks at a pool of about {{POOL_KNEE}} and then declines — and we identify three design properties that the original specification had wrong: a general-purpose sentence encoder costs the fusion its ordering until it is replaced with a retrieval-trained one, a modality quota binds only when applied *before* the reranker rather than after it, and a category pre-filter applied to only one of two retrieval legs is a no-op. We also show that the modality composition of the corpus, rather than the retrieval algorithm, determines whether a modality-aware mechanism can have any effect at all — a null result that is the expected outcome on a text-heavy corpus and is, we argue, under-reported in the literature. We are explicit about what our corpus is: industrial-engineering *encyclopaedic* text drawn from English Wikipedia under CC BY-SA 4.0, shipped in full with per-document provenance, and not the operating manuals, control plans and supplier specifications a practitioner actually uses. Claims that depend on such documents are not made. We repeat every measurement on a second corpus built for the purpose: {{IND_N_DOCUMENTS}} United States federal regulatory documents ({{IND_N_CHUNKS}} chunks, {{IND_N_REGIMES}} regimes) read through the Electronic Code of Federal Regulations at two past dates, so that the same provision at two issues *is* a conflict whose type is known by construction and needs no annotation. The negative findings replicate there — the lexical leg carried the pipeline ({{IND_BM25_VS_DENSE_DELTA}}, p = {{IND_BM25_VS_DENSE_P}}) while neither the fusion nor the category pre-filter added anything measurable on top of it — and the candidate-pool curve stops being saturated, so that {{IND_POOL_DISPLACEMENT_PCT}} of the retrieved golds are displaced out of the ten-chunk context. There, and this is the paper's clearest new result, a conflict detector's precision splits into two numbers: detection {{IND_RO4_DETECTION}} against readers' labels and {{IND_RO4_CONSTRUCTION_DETECTION}} against the construction labels, against typing {{IND_RO4_TYPING}} and {{IND_RO4_CONSTRUCTION_TYPING}}. The mechanism finds the conflicts and reports them as the wrong kind. A 2×2 factorial over the annotation rubric and the reader's specialisation shows that the rubric's wording, not the specialisation, moved that measured precision ({{IND_FACT_RUBRIC_GENERALIST}} and {{IND_FACT_RUBRIC_SPECIALIST}} against {{IND_FACT_SPEC_AT_V1}} and {{IND_FACT_SPEC_AT_V2}}), which is a warning about the measurement rather than a clean result about the mechanism. We evaluate the confidence gate as a selective-prediction policy with a risk–coverage curve and a false-positive rate at a stated operating point, with always-flag and never-flag baselines, following recent findings that a filter result reported without these quantities does not mean anything. We also report a methodological result we did not expect: auditing our own benchmark showed that its unanswerable class — the half on which a refusal benchmark lives or dies — was separable from the question text alone, because its designated hard case named a fabricated identifier that no answerable question carried. The refusal rate that class produced was an upper bound rather than a measurement. The class was rebuilt so that unanswerability is decidable only from the evidence, every measurement was taken again, and the gate refuses {{UNANS_HARD_REFUSED_PCT}} of the repaired hard class against the {{UNANS_BEFORE_REFUSED_PCT}} the defective class suggested.

**Keywords:** Retrieval-Augmented Generation; Industrial Decision Support; Hallucination Reduction; Confidence Gating; Selective Prediction; Hybrid Retrieval; Per-Claim Attribution; Evaluation Methodology.

---

## 1. Introduction

### 1.1 The operational problem

Industrial decision-making depends on timely access to evidence held in technical documentation. Practitioners across quality, maintenance, logistics and process operations routinely consult standards such as ISO 9001, GS1 specifications, Incoterms rules and original-equipment-manufacturer service procedures. The volume of this documentation has expanded with industrial digitalisation while the time available to synthesise it has not. Under operational pressure, decisions are made with partial information, and the consequences span efficiency losses, compliance failures and safety incidents.

The difficulty is not the absence of information but the cost of locating, cross-referencing and verifying the right evidence under time pressure. Large language models and RAG systems have been proposed to close this gap. RAG combines a generative model with an external retriever that supplies domain documents at inference time, mitigating knowledge-cutoff and hallucination problems, and has been applied to manufacturing, construction, energy systems and pharmaceutical research.

### 1.2 Three gaps that remain

Despite this progress, three properties that industrial users require are absent from generic systems. First, there is **no evidence trail**: the system returns an answer but does not indicate which passage supports which claim. Second, there is **no confidence check**: the system answers even when retrieval is weak. Third, there is **no contradiction handling**: when two accepted passages disagree, the system silently selects one.

These are not cosmetic. Hallucination in this domain is operational risk, and the failure is asymmetric: a wrong safety procedure or a wrong economic order quantity carries consequences that exceed the cost of the original lookup. SQuAD 2.0 (Rajpurkar et al., 2018) established the general form of this problem by defining an evaluation in which a system must both answer answerable questions correctly *and* decline unanswerable ones; its abstract reports that a strong neural system achieving 86% F1 on SQuAD achieves only 66% on SQuAD 2.0. Twenty points are lost to confidently answering questions that have no answer, in a purely general-domain setting. No such loss is acceptable when the subject is a plant's reorder policy.

### 1.3 This paper's contribution, stated conservatively

We measure which reliability mechanisms pay for themselves in industrial text, and report where they break. We state the contribution in three parts, and we state them in that order deliberately: the measurement is the contribution, not the architecture.

The measurement is also **narrow**, and it has to be. By late 2026, "measure what a reliability mechanism costs and what it buys" is the house style of RAG evaluation rather than a novelty claim: five papers published between July and November 2026 take it as their explicit object of study, one of them reporting that a matched random-escalation control matches the confidence-gated system it is testing (arXiv:2610.20634). The gate itself is likewise published prior art in enterprise (arXiv:2609.11023), regulated trade finance (arXiv:2608.21792), evidence-grounded QA (arXiv:2609.15830) and nuclear engineering (arXiv:2604.22755), and we say so rather than argue around it. What is not in that list is the **joint cost–coverage–reliability frontier for a confidence gate on industrial text, at the level of the individual answer claim, on a corpus regime that is not the procedural one every prior deployment uses.** That is the claim, and it is deliberately narrower than the one this work began with.

**Architectural — incremental, and treated as such.** Every one of the five mechanisms has published prior art, and by late 2026 the closest of them are close enough that the architecture cannot be the argument. A code-level, pre-generation gate with a calibrated, task-adapted decision policy is published (Sieve and Sage, EMNLP 2026 Findings; BITEM, NTCIR-19; HALT-RAG); set-level sufficiency verification and structural certificates are published (SURE-RAG; Certify); a calibrated NLI ensemble combined with lexical signals under a precision-constrained abstention policy is published (HALT-RAG); the argument that modality routing is performed at the wrong decision point is published in the modality-RAG literature (Modality Relevance is not Modality Utility); and the claim that retrieval enhancements stop paying once a strong reranker is present is published on heterogeneous corpora (Beyond the Reranker). We position ours against that prior art explicitly (Section 2) rather than claiming priority. The one architectural property we hold is that the gate is a control-flow fact rather than an instruction.

**Empirical — a failure-mode characterisation, mostly of negative results.** Our substantive contribution is what the measurements show, and several of them contradict the framework's original specification and one contradicts the direction the field has been moving. The dense leg is not merely weaker than the lexical leg: on a corpus whose questions are derived from the documents themselves, fusing it in costs the fusion its ordering until the encoder is replaced with a retrieval-trained one. And the modality quota's pipeline position inverts the rule the framework was designed on: {{QUOTA_PLACEMENT_CLAIM}}, and {{QUOTA_PLACEMENT_SIGNIFICANCE}} The confidence gate cannot separate "there is no evidence here" from "the evidence is here and the retriever missed it", because the retrieval scores it uses cannot; it is therefore an answer-in-context detector, and Section 4.4 reports the contingency table that says so rather than a base rate alone. And a reranker's effect on recall is governed by its candidate pool rather than by the reranker.

**Metric — a conflict detector's precision is two numbers.** Reported as one number, a conflict detector's precision conflates two questions: *is the alarm pointing at something real*, and *is the branch that raised it the branch that owns the conflict*. On the second corpus, where the conflicts are known by construction, the two come apart by a factor of nine, and the mechanism finds the conflicts and reports them under the wrong label. The decomposition is not published, and it converts into a specification: a detector for regulatory text needs version metadata, or must be scoped to detection alone.

**Methodological — an evaluation protocol.** We evaluate the confidence gate as a selective-prediction policy with a risk–coverage curve, a false-positive rate at a stated operating point, and the two degenerate policies — never refuse and always refuse — as baselines, rather than the endpoints of the threshold sweep, which are not baselines. We report the label's contingency table rather than a base rate alone. We separate the components of a compound detector, so that a recall which is true by construction cannot be presented as a result. This follows recent findings that filter results reported without these quantities are uninterpretable (Section 2.4), and that automated labelers conflate reference faithfulness with factual correctness (Section 2.7).

**The scope is narrower than the proposal's, and that is stated rather than
glossed.** The proposal described a twelve-category industrial benchmark
spanning industrial engineering, machine learning and data analytics. This
paper evaluates six of the nine industrial-engineering categories, on three
corpora that could be obtained and redistributed, and it does not claim the
twelve-category benchmark. The three machine-learning categories -- demand
forecasting, time-series forecasting and anomaly detection -- are numerical
series-reasoning problems rather than document-retrieval problems, and a
text-RAG pipeline would measure the tokenizer rather than the mechanism; three
further industrial categories are descoped because the binding artefacts the
proposal names -- carrier rate cards, RMA procedures, stock policies -- are
proprietary and not redistributable. The reconciliation, with the proposal's
own wording and the reason for every row, is
`research/12_scope_reconciliation.md`.

### 1.4 Organisation

Section 2 positions the work. Section 3 describes the framework, with the mathematics derived rather than asserted. Section 4 gives the evaluation protocol. Section 5 reports results. Section 6 reports the second corpus, on which the framework's negative findings replicate and a conflict detector's precision splits into detection and typing. Section 7 discusses. Section 8 states limitations.

---

## 2. Related work and positioning

### 2.1 Retrieval-augmented generation and its failure modes

RAG (Lewis et al., 2020) established the retrieve-then-generate paradigm, in which a non-parametric retriever (DPR) supplies documents and a parametric generator marginalises over them. Dense passage retrieval (Karpukhin et al., 2020) established the dual-encoder approach and reported that dense retrieval outperformed a strong Lucene-BM25 baseline by 9–19 percentage points absolute in top-20 passage retrieval accuracy on open-domain question answering.

Three lines of work since then address the framework's reliability. Self-RAG (Asai et al., ICLR 2024) trains a model to emit reflection tokens that decide when to retrieve and whether a passage supports the output. CRAG (Yan et al., 2024) inserts a lightweight retrieval evaluator that returns a confidence degree triggering one of four corrective actions. FLARE (Jiang et al., EMNLP 2023) and DRAGIN (Su et al., ACL 2024) trigger retrieval during generation based on the model's own information need. Adaptive-RAG (Jeong et al., NAACL 2024) routes queries by complexity. A survey by Gao et al. (2023) organises these into a naive / advanced / modular taxonomy.

These works define the design space in which our confidence gate sits, and they sharpen the claim considerably: our gate is not "when to retrieve" but "**whether to answer**", and the answer is no by default when the evidence is weak. The distinction must be stated, because a reviewer familiar with Adaptive-RAG will otherwise ask whether the contributions are the same. They are not, but the adjacent work must be engaged.

### 2.2 Confidence, calibration and abstention

The task of declining to answer has a benchmark definition. SQuAD 2.0 introduced 50,000 unanswerable questions with a no-answer threshold, and Kadavath et al. (2022) showed that verbalised confidence is informative and complements self-grading. Semantic uncertainty (Kuhn et al., ICLR 2023) and the Nature paper of Farquhar et al. (2024) distinguish *confabulation* — arbitrary incorrect generation — from *consistent error*, a confidently held wrong belief; semantic entropy is high in the first case and low in the second. Joren et al. (2024) provide the most directly relevant result: large models answer well when the retrieved context is *sufficient*, but produce a wrong answer rather than abstaining when it is not, and their selective-generation method improves the fraction of correct answers among responses by 2–10%. This is simultaneously the strongest justification for a gate existing and the sharpest warning about where it must sit: a gate applied to the *generated answer* inherits exactly the failure Joren documents, whereas a gate applied to the *retrieval* attacks the correct variable.

Three 2026 works are the most important for our positioning. Decian et al. (2026, *Neurocomputing* 705, 134911) combine hybrid retrieval with an entropy-based dynamic threshold and report a statistically significant gain in correctness; this is the nearest prior art to D1 on the mechanism, and the defensible difference is one of philosophy rather than accuracy — an auditable refusal with a stated reason versus a probabilistic adjustment of the retrieval. We do not claim to beat it. Geißler et al. (2026, arXiv:2605.05244) apply conformal prediction to filter retrieved chunks and then score answer–context consistency with an attention-based factuality classifier, reporting answer-quality improvement of up to 6% and inconsistency detection of up to 77%, while conceding that "the associated statistical guarantees do not hold generally, since the assumption of sample exchangeability depends on the retriever setup." Phillips et al. (2026) show that entropy-based uncertainty has a model-dependent failure mode and that selective-prediction policies must be evaluated at a stated target error rate. Thakur et al. (2026) report in DeclineCraft that adding query rewriting and reranking to hybrid dense-and-sparse retrieval *lowers* the correct abstention rate for all 12 models tested.

The last of these is a direct challenge to our architecture: our hybrid retrieval improves retrieval, and better retrieval reduces abstention. We treat this as an operational requirement rather than a contradiction — the gate's operating point must be re-fitted for every retrieval configuration we compare, and Section 4.4 does exactly that.

### 2.3 Multimodal and modality-aware retrieval

ColPali (Faysse et al., ICLR 2025) introduced page-image retrieval with a vision-language model producing multi-vector embeddings and a late-interaction matching mechanism, together with the ViDoRe benchmark. VisDoMRAG (Suri et al., 2024) fuses modalities under a consistency constraint and is the closest prior art to our modality-balancing mechanism. TableRAG (EMNLP 2025) treats tables as first-class retrieval objects. T²-RAGBench (Strich et al., EACL 2026) provides a text-and-table benchmark of 23,088 expert-validated triples and reports that hybrid BM25 performs best on text-plus-table queries. SCAN (Ueda et al., EACL 2026) reports gains of +9.4 points from chunking alone.

The honest reading is that modality-balanced retrieval is already in the literature, so our claim cannot be about the goal. It is about the *mechanism* — a hard, non-bypassable quota on the final context — and about the domain.

### 2.4 Attribution, evaluation and the failure of "reported a number"

ALCE (Gao et al., EMNLP 2023) defined citation recall and citation precision and established the standard long-form attribution evaluation; it reports that even the best models lack complete citation support for ELI5 half the time. RAGAS (Es et al., EACL 2024) defined faithfulness, answer relevancy, context precision and context recall. ARES (Saad-Falcon et al., NAACL 2024) provides a reference-free evaluation framework. FActScore (Min et al., EMNLP 2023) decomposes generations into atomic facts and reports that ChatGPT biographies are only 58% factually supported, with its automated estimator achieving under 2% error. SAFE (Wei et al., 2024) reaches 72% agreement with human factuality judgments at roughly 20× lower cost.

A third prior work is the sharpest challenge to D1 itself. Wu, Gu, Yin and Peng (EMNLP 2024, DOI 10.18653/v1/2024.emnlp-main.527) monitor the model as it decodes and report that their FOD decoding algorithm outperforms abstention, reranking and contrastive decoding by over 10% on faithfulness, at 0.85 AUROC over six long-form RAG tasks. Because D1 *is* an abstention mechanism, this demands an answer. The two mechanisms detect different failures: SYNCHECK asks whether a generated sentence is faithful to the context, whereas the gate asks whether the context contains enough to answer at all, which must be settled before generation because a sentence produced from inadequate evidence cannot be repaired afterwards; the gate also runs before generation, so a refusal costs one retrieval pass rather than a generation plus a monitoring pass; and our claim is not an AUROC against faithfulness detection but per-claim confidence banding with a cited evidence trail for a practitioner. We concede openly that a gate over a small number of retrieval-side signals is the simplest instantiation of the multi-signal design that both SYNCHECK and Phillips et al. point to.

Two 2026 papers change how these must be reported. First, a study of query-time RAG poisoning defences shows that benchmark construction cues can dominate measured filter performance: removing a single cue drops AUROC from 0.953 to 0.758 and raises the miss rate from 0.191 to 0.763, and the paper reports that 12 of 21 published evaluations state no false-positive rate at their operating point. Second, a study of cheap LLM judges finds AUROC as low as 0.603, with strong judges varying between 0.62 and 0.88 by domain; elsewhere, position bias was measured to flip 66 of 80 queries. We adopt both lessons as requirements on our own evaluation: a false-positive rate at a stated operating point with always-flag and never-flag baselines, and a meta-evaluation of any judge we use.

### 2.5 Contradiction and conflict detection

NLI is the standard instrument: MNLI (Williams et al., 2018) and ANLI (Nie et al., 2020) train models to classify a premise–hypothesis pair as entailment, neutral or contradiction, and VitaminC (Nie et al., 2021) and FEVEROUS (Kamalloo et al., 2023) apply NLI to fact verification. ContextConflict (EMNLP 2026, DOI 10.18653/2026.emnlp-main.918) is the most important recent result for us: it identifies six conflict types — factual, inferential, temporal, granularity, perspective and ambiguity — of which only two are genuine contradictions. This is the strongest published justification for a *topical* gate and for reporting a conflict *type* rather than a binary flag. ConflictScore (EMNLP 2026, DOI 10.18653/2026.emnlp-main.2589) decomposes responses into atomic claims, labels each against each grounding document and aggregates into CS-Count and CS-Ratio, and is close prior art to our conflict-plus-attribution combination.

Two published ceilings matter for our expectations: SciNLI reaches 78.18% macro-F1, and an LLM-based system reaches 51.77% on MSciNLI. NLI on technical text is materially weaker than on general text, which is why we validate the NLI leg on our own corpus rather than importing a general-domain number.

### 2.6 Summary of positioning

| Mechanism | Closest prior art | What we claim |
|---|---|---|
| Confidence gate | Decian et al. 2026; Geißler et al. 2026; CRAG; Yadkori et al. 2024 | Non-bypassability as control flow; auditable refusal; portability without retraining (the calibration is not portable and is re-fitted per corpus and retriever). Not priority. |
| Modality quota | VisDoMRAG; TableRAG | Mechanism and domain, not the goal. |
| Hybrid retrieval | Cormack et al. 2009; Bruch et al. 2023; BEIR; Beyond the Reranker (arXiv:2606.28367); T²-RAGBench (EACL 2026); FreshStack (NeurIPS 2025) | A replication and a clarification of what fusion and reranking each buy, plus the candidate-pool curve, which we find is unpublished. Not priority. |
| Contradiction surfacing | HALT-RAG (arXiv:2509.07475); Kontrast (arXiv:2607.25959); Financial Evidence Crowding (arXiv:2609.35782); HCF (arXiv:2609.07075); WIKICOLLIDE (arXiv:2509.23233) | An industrial instantiation in which the numeric detector is independent of the NLI verifier and the supersession check is explicit. The conjunction is not published; each conjunct is. |
| Per-claim tagging | Conformal-RAG; ConflictScore; GRACE; CalibRAG | Calibration and presentation combined, for an industrial audience. Not priority. |

### 2.7 What changed in 2026, and what it forces us to narrow

Three developments between the framework's specification and this writing bear
directly on our claims, and we state them here rather than leaving a reader to
find them.

**The abstention mechanism has moved past a threshold.** GRAB-RAG
(arXiv:2608.22228) shows that under explicit abstention prompting models still
answer 41.6% of *misleading* questions, with 63% of those answers echoing the
planted wrong entity; the paper's contribution is not that a threshold exists but
that a threshold is insufficient. SURE-RAG (arXiv:2605.03534) argues that
sufficiency is a *set-level* property that independent passage scoring cannot
detect, and Certify (arXiv:2610.34684) makes it structural, deriving a
Horn-closure certificate from a per-query requirement hypergraph. Sieve and Sage
(arXiv:2609.35794) screens the retrieved set in a lightweight module *outside*
the model before the model is invoked, with a two-state failure decomposition
(unanswerable versus distracted); AGO (arXiv:2610.01218) quantifies
regression risk probabilistically. The consequence for us is narrow and we accept
it: our gate is a **calibrated answer-in-context detector with a stated
operating point**, not a sufficiency judge, and the literature reserves
"sufficiency" for the set-level property. Section 4.4 reports the contingency
table that makes the distinction concrete.

**The closest single pre-emption of our contradiction mechanism is published.**
HALT-RAG (arXiv:2509.07475) is a task-adaptable framework that combines an
ensemble of NLI models with lexical signals, feeds them to a calibrated
meta-classifier, and deploys it under a precision-constrained abstention
policy. It is a **post-hoc** verifier — it operates on the source text and
the generated output without retrieving — and its own Future Work names
integrating and evaluating detectors like it within a live RAG pipeline as
the critical next step, which is the experiment reported in Section 6.
Kontrast
(arXiv:2607.25959) separates direct conflicts from information-granularity
differences, temporal changes and incompleteness, which is our supersession
check formalised. WIKICOLLIDE (arXiv:2509.23233) reports that at least 3.3% of
English Wikipedia facts contradict another fact — which is both a reason our
corpus is a reasonable object of study and a benchmark we should have used.
Our remaining D4 claim is therefore an *industrial instantiation* in which the
numeric detector is independent of the NLI verifier and the supersession check
is explicit, and it can only be defended against human labels, which we do not
have and say so.

**Retrieval enhancements stop paying once a strong reranker is present.**
Beyond the Reranker (arXiv:2606.28367) evaluates eight enhancement methods on a
heterogeneous corpus and reports that only query expansion and one calibrated
method give reliable gains beyond a strong reranker; its framing sentence is
aimed at work like ours, noting that reported gains "come almost exclusively
from homogeneous corpora, predominantly Wikipedia prose." Ours is exactly such
a corpus, so the effect sizes we measure should be read as an upper bound on
what the same mechanisms would deliver on mixed-format industrial documents.
FreshStack (arXiv:2504.13128) independently reports rerankers that fail to
improve first-stage retrieval on two of five technical topics, and T²-RAGBench
(EACL 2026, arXiv:2506.12071) finds hybrid BM25 most effective on text-and-table
data. We therefore report the candidate-pool curve (Section 5) as our
contribution in this area and treat the pipeline itself as the instrument
rather than the result.

Two further threats belong with these. The Labeling Problem in Hallucination
Detection Benchmarks (NeurIPS 2026 Evaluations and Datasets Track,
arXiv:2610.08026) shows with 900 human-labelled pairs that automated labelers
systematically conflate reference faithfulness with factual correctness — a
direct constraint on our silver-standard labels. Entropy Alone is Insufficient
for Safe Selective Prediction in LLMs (arXiv:2603.21172) bears on our
information-gain component. And Detecting Is Not Resolving
(arXiv:2605.27157) reports across more than 50,000 turn-level evaluations that
models acknowledge contradictory evidence without constraining their
recommendations — the monitoring-control gap, which is why we treat
contradiction *surfacing* as a reporting mechanism rather than a resolution
mechanism.

We also correct the following bibliographic errors found in the project's own proposal and earlier report: the reference attributed to "Microsoft Research" is by Simchi-Levi, Mellou, Menache and Pathuri and is a Springer book chapter; the hallucination-survey title is "A Capability-Oriented Survey", not "Application-Oriented"; and the DOI 10.18653/v1/2024.findings-acl.212 with pages 3563–3578, previously attached to CRAG, resolves to Dhuliawala et al.'s "Chain-of-Verification" paper rather than to CRAG.

---

## 3. The framework

### 3.1 Overview

The framework has three stages. Ingestion is offline and runs once per document. Retrieval and generation are online and run per query.

```
STAGE 1 — INGESTION (offline, per document)
    parse -> chunk (text | table | chart) -> tag category -> embed -> index

STAGE 2 — RETRIEVAL (online, per query)
    FORM CHECK -> embed query -> category pre-filter -> BM25 leg + dense leg
                -> reciprocal rank fusion -> cross-encoder rerank
                -> CONFIDENCE GATE -> modality quota

STAGE 3 — GENERATION (online, per accepted query)
    per-claim tagging -> citations -> contradiction flag -> tagged answer
```

The gate is the load-bearing element. It sits between retrieval and generation, and when it rejects, the language model is never invoked.

The form check stands in front of it, and it is a different question. The gate asks whether the retrieved evidence supports an answer; the form check asks whether the request is a question at all. It runs before retrieval, so a request it refuses costs no embedding pass, no cross-encoder pass and no model call. It refuses four things — an empty query, a query with no words, a query whose every word is a function word or a deictic ("what is this?"), and a query that ends on a word that cannot end a question ("what are units that?"). Its rates are measured in §8 rather than asserted: it refused {{FORMVAL_FIX_MAL_REJECTED}} of {{FORMVAL_FIX_MAL_N}} hand-authored malformed queries and {{FORMVAL_STEM_MAL_REJECTED}} of the {{FORMVAL_STEM_MAL_N}} hand-labelled malformed stems the benchmark's own generator produced ({{FORMVAL_STEM_MAL_RATE}}), against {{FORMVAL_STEM_GOOD_REJECTED}} false rejections among {{FORMVAL_STEM_GOOD_N}} hand-labelled well-formed stems and {{FORMVAL_BENCH_REJECTED}} among the {{FORMVAL_BENCH_N}} benchmark queries.

### 3.2 Ingestion and modality-aware chunking

A PDF is a visual object: a page is a layout of text blocks, ruled tables and figures that only becomes a table once the ruling lines are understood. A naive text extractor destroys that structure, and in an industrial corpus the binding requirements live in tables — an economic order quantity, a safety-stock rule, an acceptance tolerance. If ingestion destroys the table, no downstream retrieval cleverness recovers it.

We therefore parse structurally: PyMuPDF's block tree and table detector give bounding boxes, and each block is classified as *text*, *table* (overlapping a detected table region) or *chart* (mostly non-alphabetic — a figure label or chart annotation). Tables are serialised to markdown with horizontally merged cells forward-filled so the result stays rectangular, and are never split, since a table is the atomic unit of a specification. Text is chunked into 120-word windows with 30-word overlap.

Every chunk carries metadata: document identifier, page, modality, section and caption. The corpus modality composition is measured and reported, because it predicts whether modality-balancing can have any effect at all.

### 3.3 The lexical leg: BM25

We implement BM25 from first principles rather than depending on a library, so that the scoring function and its parameters can be defended directly. Under the probabilistic relevance framework the document-relevance probability factorises over query terms under a term-independence assumption, and taking logarithms turns the product of likelihood ratios into a sum of inverse document frequencies:

```
IDF(t) = log[ (N − n_t + 0.5) / (n_t + 0.5) + 1 ]
```

The final form adds term-frequency saturation, which bounds the contribution of a repeated term, and length normalisation, which requires a longer document to work harder for the same score:

```
BM25(q,D) = Σ_{t∈Q} IDF(t) · f(t,D)(k₁+1) / [ f(t,D) + k₁(1 − b + b|D|/avgdl) ]
```

with k₁ = 1.2 and b = 0.75, the values Robertson et al. tuned and Lucene has shipped since 8.x.

### 3.4 The dense leg

The query and every chunk are embedded with `{{EMBED_MODEL}}` ({{EMBED_DIM}} dimensions, L2-normalised), and ranked by cosine similarity:

```
cos(q,d) = (q · d) / (‖q‖ ‖d‖)
```

Because the vectors are normalised, this equals the raw dot product, which is what makes a pgvector HNSW dot-product index usable.

### 3.5 Rank fusion

Dense and lexical rankings are fused by Reciprocal Rank Fusion (Cormack et al., 2009):

```
RRF(d) = Σ_i 1 / (k + r_i(d)),   k = 60
```

The derivation is a response to a structural problem: BM25 scores, cosine similarities and cross-encoder logits are on incomparable scales, so summing them requires a fitted weighting that does not transfer across corpora. Rank is scale-free. At k = 60 the discount 1/(k+r) is nearly flat across the top ten ranks, so the fused ordering is driven by *agreement* between the retrievers rather than by any one retriever's score magnitude. Bruch et al. (2023) compared RRF with score-combination functions across 23 runs and found RRF at least as good and considerably more robust, and also showed that *tuned* fusion weights do not generalise out of domain — which argues for the untuned k = 60 in a deployment over an unseen corpus.

### 3.6 Cross-encoder reranking

A cross-encoder reads the query and the document jointly, so every token of the document attends to every token of the query:

```
score(q,d) = wᵀ · Transformer([CLS] q [SEP] d [SEP])[CLS]
```

This is strictly more expressive than the bi-encoder and strictly more expensive — one forward pass per pair — which is why it is applied to the fused shortlist rather than the corpus. We use `cross-encoder/ms-marco-MiniLM-L6-v2`. The score is a **logit, not a probability**, and its distribution shifts with query difficulty; Section 3.7 is what makes it usable.

### 3.7 The confidence gate

**The posterior.** Let R be the event that a chunk is relevant to the query and d the evidence about it. Bayes' theorem in odds form is

```
P(R | d) = [ P(R) / P(d | ¬R) ] · [ P(d | R) / P(d | ¬R) ]
```

— prior odds times likelihood ratio. For a single scalar feature x we use a logistic model on the log-odds scale,

```
P(R | d) = σ(β₀ + β₁·x),   σ(z) = 1/(1 + e^(−z))
```

which is Platt scaling's form. β₀ encodes the prior odds (at x = 0 the odds are e^β₀ in favour of relevance) and β₁ encodes how much one unit of score moves those odds (e^β₁ per point).

**Calibration.** The coefficients are fitted by maximum likelihood on a held-out query split. The log-loss is convex in (β₀, β₁), so Newton's method converges reliably; the implementation includes the gradient and Hessian explicitly. Because the split is by *query*, not by candidate, the calibration set contains whole queries and no candidate from an evaluation query leaks into it.

**Calibration is not optional.** A raw cross-encoder score is a logit whose scale varies with query difficulty and candidate-set composition. Thresholding it directly is a category error. We report the Brier score, the Expected Calibration Error

```
ECE = Σ_b (n_b/N) · |acc_b − conf_b|
```

a reliability table, and a risk–coverage curve.

**The gate is a query-level decision.** It does not ask "is this candidate the
gold chunk?" — it asks "**does this retrieved context contain sufficient
evidence to answer the question at all?**" The distinction is not pedantic. With
about fifty candidates per query and one gold chunk, the base rate of chunk-level
positives is roughly 2%, so a chunk-level classifier that answers "nothing is
relevant" is right 98% of the time. Maximum-likelihood fitting against such a
label duly returns a large negative intercept and a nearly flat slope, the
calibration metrics look excellent because they are measuring the base rate, and
the resulting operating point refuses a large fraction of the answerable
questions. Calibrating at the query level removes that degenerate solution.

The label is therefore 1 when the retrieved context contains a gold chunk —
covering both an answerable question whose evidence the retriever found and an
answerable question whose evidence it missed; in both cases the correct
behaviour is to refuse. The features are five signals of the retrieved set, all
available before generation: the top cross-encoder score, the mean of the top
three scores, the best BM25 score, the best RRF score, and the number of
candidates clearing a low relevance bar.

**The gate as control flow.**

```
P_sufficient = calibrate(features of the retrieved set)

if P_sufficient < τ:
    return NO_EVIDENCE_RESPONSE          # the LLM is never called
else:
    context = accepted chunks
    answer = generate_with_claims(context)
```

Three properties distinguish this from an instruction. The model cannot talk its way past it, because there is no output it can produce that reaches the gate. The refusal is auditable — "calibrated sufficiency probability 0.312 against threshold 0.500" is checkable, "the model seemed unsure" is not. And it is portable without retraining -- the mechanism needs no per-category
fine-tuning, though the *calibration* is re-fitted per corpus and per retriever
(L10), which is measured rather than assumed -- which matters across a
portfolio of categories -- {{N_CATEGORIES_WORD}} in the public corpus measured here, twelve in the original project corpus: Self-RAG's reflection tokens are learned on a training distribution and would have to be re-learned per category, and Huang et al. (2024) show intrinsic self-correction degrades without external feedback.

**Why refuse rather than refine.** CRAG, the nearest prior art, responds to low confidence by improving the evidence and continuing, and still calls the LLM in every branch. Refuse-and-decline is the better choice under a specific condition: the corpus is a fixed, closed set of controlled documents and the cost of a wrong answer exceeds the cost of no answer. That is the industrial case, and stating the condition precisely is the argument; asserting that CRAG is inferior would not be.

### 3.8 Modality quota

A floor on the share of the final context occupied by tables (0.15) and charts (0.05), implemented as a swap: take the natural top-k untouched, and while a floor is unmet, swap the lowest-ranked item of the over-represented modality for the highest-ranked available item of the under-represented modality. A rebuild-based implementation — walk the ranking, skip what would breach a floor, backfill — silently removes good high-ranked items and measurably degraded table recall in our development.

**The pipeline position is decisive.** Applied *before* the reranker, the quota proposes a **membership** for the final ten; the reranker then re-scores those ten and can reorder them but cannot change *which* ten they are, so the forced table chunk survives and the floor binds. Applied *after* the reranker, the quota adjusts the final context by swapping one of the reranked chunks for a table chunk the reranker already ranked below the cut, so it tends to import the wrong chunk and displace a good one. Section 5 reports the measured difference: {{QUOTA_PLACEMENT_CLAIM}}, and {{QUOTA_PLACEMENT_SIGNIFICANCE}} The rule this framework was designed on is therefore inverted on the corpora the thesis measures it on, and not settled on the third.

**Which placement the shipped system uses.** The system applies the quota *{{SHIPPED_QUOTA_PLACEMENT}}*, which is the placement Section 5's measurement ranks first on the focus domain -- the domain the thesis is about, and the largest of the three differences the ablation measures. It was built the other way round -- the September 2026 design put the quota after the reranker -- and it stayed that way until 16 November 2026, because changing it invalidates the gate's calibration, the generator-side comparison and the per-claim results together, and the defence was three days away. On that date the default was moved and {{PLACEMENT_SCOPE}}.

### 3.9 Contradiction surfacing

Two accepted chunks are flagged as conflicting only when two independent gates agree:

```
flag(A,B) = contradiction(A,B) ∧ same_subject(A,B)
```

`contradiction` is the NLI probability from a DeBERTa-v3 MNLI model. `same_subject` combines embedding cosine similarity (threshold 0.55) with Jaccard overlap of concrete identifiers — part numbers, plant codes, standard references, quantities (threshold 0.10). The conjunction matters because raising the NLI threshold alone reduces false positives only by excluding genuine conflicts; an orthogonal signal lets the two error types be traded off separately.

Two further mechanisms matter in industrial documentation. First, a **numeric conflict** — two passages attaching different values to the same quantity — is an explicit contradiction regardless of the NLI model's confidence. Second, a **revision-supersession check**: "Rev 3 sets EOQ at 187 units" and "Rev 4 sets EOQ at 95 units" are both true, because Rev 4 replaced Rev 3, and reporting that as a contradiction is wrong in exactly the way that matters. We therefore suppress the flag when the two passages carry different revision markers and sufficient entity overlap.

Following ContextConflict, we report a conflict *type* rather than a binary flag.

### 3.10 Per-claim confidence tagging

Each answer is decomposed into atomic claims by sentence, then split at discourse markers. For each claim, the NLI model gives an entailment probability eᵢ for every retrieved chunk. These are combined with the noisy-OR model, in which each chunk is an independent fallible witness and the claim is supported if at least one covers it:

```
q = 1 − Π_i (1 − e_i)
```

We take the maximum rather than the mean across chunks, so that one strongly contradicting chunk is not diluted by many irrelevant ones. The band is cut on q: q ≥ 0.80 is *grounded*, q ≥ 0.45 *inferred*, otherwise *uncertain*.

Alongside the band we report the information gain in bits,

```
IG = H(prior) − H(q),   H(p) = −p log₂p − (1−p) log₂(1−p)
```

which quantifies how much the retrieved set reduced our uncertainty about the claim. **The two quantities answer different questions and must not be conflated**: information gain is symmetric about q = 0.5, so a claim with q = 0.9 and one with q = 0.1 both give IG = 0.531 bits. The band therefore cuts on q, and information gain is reported alongside as a separate figure.

### 3.11 The evidence trail

Every claim carries its band, its citation identifiers, and — where the evidence actively contradicts it — a *contradicted* marker pointing at the contradicting passage. The output is therefore auditable without leaving the answer.

---

## 4. Evaluation protocol

### 4.1 The benchmark, and an explicit statement of what it is

We evaluate on a **silver-standard** benchmark derived from an independently constructed public industrial corpus, not on the 300-query expert-annotated SupplyChainQA v7 of the earlier project report (which is proprietary and unreleased). Silver labels are mechanically derived from the document itself: a table cell becomes a lookup question with the table chunk as gold; a definitional or numeric sentence becomes a question with its chunk as gold. This is cheap, perfectly reproducible, and slightly optimistic — the derived gold chunk is guaranteed to contain the answer somewhere, whereas an expert annotator might judge it insufficient — so it inflates *absolute* recall. It does not bias the *comparison* between systems, which is what the ablation tests, because every system is scored against the same labels. An audit of those labels is reported in the guide's E.8: {{AUDIT_DEFECTIVE_N}} of the {{AUDIT_ANSWERABLE_N}} answerable questions carry an answer label attached to the wrong question, which depresses the *answer-side* accuracy of every arm without changing its direction, and leaves the retrieval-side measurements untouched, because the gold chunk is correct in every case.

**What "silver-standard" means here, and what we did about it.** A silver label
is derived from the document rather than annotated by an expert, and the first
version of this benchmark was worse than that word suggests: a quarter of its
answerable questions were malformed, because the generator's subject regex
could match mid-clause or after a word the markdown converter had truncated,
producing questions like "What value is stated for a teep in the source
documentation?". A benchmark in which a quarter of the questions are not
questions measures nothing. Three changes fix it. The generator now anchors
each match to the start of a sentence, so a subject is a subject rather than a
fragment. A plausibility check rejects a subject that contains a verb, a
pronoun, or a dangling preposition, and rejects a table cell that carries
markup. And acronyms keep their case, so the question asks about TEEP rather
than about "teep". The result is a smaller benchmark whose every question is a
question somebody would ask of the document. It remains silver-standard in the
sense that matters: the labels are derived, not annotated, so *absolute*
recall is optimistic, and the comparisons between systems — which is what the
ablation tests — are unaffected because every system is scored against
identical labels.

**A caveat the numbers themselves make.** On this benchmark the plain lexical
retriever reaches Recall@10 {{R_A}}. That is high, and it is a property of the
*label standard* rather than of the corpus: a question derived from a chunk
contains that chunk's own words, so lexical matching is close to an oracle. Two
consequences follow, and both are visible in Section 5. Recall@10 is near its
ceiling for every system, so the discriminating signal is in the ordering
metrics — MRR and nDCG — where the reranker moves MRR by {{MC_DELTA_CD_MRR}} on
the six-category corpus and by {{RERANK_MRR_PP}} points on the focus domain,
where the fusion is already at the ceiling — and in the modality trade-off,
which is the one place
where a mechanism changes recall rather than order. It is also why an
expert-annotated benchmark matters, and why the NeurIPS 2026 result on
automatic labelers conflating reference faithfulness with factual correctness
(NeurIPS 2026 Evaluations and Datasets Track, arXiv:2610.08026) bears directly
on what this benchmark can be used to claim.

**The corpus, and where it came from.** Every measurement in this paper was
taken on an independently constructed public corpus of {{N_DOCUMENTS}}
industrial-engineering articles ({{N_CHUNKS}} chunks, {{N_CATEGORIES_WORD}}
categories), assembled from English Wikipedia through the MediaWiki API and
licensed CC BY-SA 4.0. It is a substitute for the primary corpus of the
original specification --- 634 chunks across 24 proprietary supply-chain documents
--- which cannot be redistributed and therefore cannot be shipped with this
paper or re-run by a reader. The substitute ships in full alongside it:
`deliverables/dataset/` holds the documents and a manifest giving, for each
one, its Wikipedia URL, the upstream revision it was read at, the SHA-256 of
the bytes used, and its chunk count.

The thesis focuses on a **single industrial domain, supply chain management**
({{N_FOCUS_DOCUMENTS}} documents, {{N_FOCUS_CHUNKS}} chunks,
{{N_FOCUS_QUERIES}} questions), because that is the domain the primary corpus
covered and the one the practitioner scenarios are drawn from. The remaining
categories are retained for the cross-category transfer objective, which by
definition needs a subset of categories to transfer to held-out ones. Section
5 traces real questions from the focus domain end to end: what the plain
lexical retriever returned, what the full framework returned instead, what the
gate decided and on which signals, and how every claim in the answer was
banded.

Crucially, the benchmark contains a family of **deliberately unanswerable questions** on topics absent from the corpus. Without them, no confidence-gating experiment is meaningful: a system that answers everything scores 100% recall and 0% hallucination.

**What the gate's label actually is, stated exactly.** The gate is calibrated on a query-level label that is 1 iff the gold chunk is present in the reranked candidate pool. That is an *answer-in-context* label, not an evidence-sufficiency label: the literature reserves "sufficiency" for a set-level property, where scoring passages independently cannot detect it. The gate therefore detects whether the answer is in the retrieved context, and it does not judge whether the context is sufficient.

The negative class contains two different kinds of query, and the sizes of both matter. On the evaluation corpus, of {{N_ANSWERABLE_FOUND}} answerable questions whose evidence was found, {{N_ANSWERABLE_MISSED}} answerable questions had their evidence missed by the retriever, and {{N_LABEL_UNANSWERABLE}} questions were unanswerable; the retriever's own recall of the gold chunk is {{GOLD_RECALL_PCT}}, so retrieval failure accounts for {{NEGATIVE_CLASS_SHARE_RETRIEVAL_FAILURE}} of the negative class. The limitation is worth stating precisely rather than dramatically: **the gate's features are retrieval scores, so its ability to separate "the answer is in the context" from "it is not" is bounded by how well those scores carry that information, and the composition of the negative class moves with the retriever.** On this corpus the retriever is strong enough that the negative class is mostly genuinely unanswerable, and the gate does well; on a corpus where the retriever is weaker, the same gate would face a negative class dominated by retrieval failure, which it cannot resolve, because the scores it uses are exactly the scores that failed. That is why the operating point is a fitted, per-corpus parameter and not a constant of the architecture, and why every claim about the gate here is stated against this decomposition.

The earlier expert-annotated benchmark is reported separately, with Cohen's κ ≥ 0.7 on four categorical fields, and the two are never pooled.

### 4.2 Metrics

Retrieval is measured by Recall@k, Precision@k, MRR and nDCG@k, with graded relevance (3 for a chunk carrying a binding specification, 1 otherwise), and by **per-modality recall**, which is how the modality claim is tested. Generation is measured by faithfulness (the fraction of claims entailed by the context), citation precision and citation recall.

Queries with no gold set are excluded from recall and nDCG aggregates rather than averaged in as zero — a zero would misrepresent a system as failing to retrieve an answer when there is none to retrieve. Their behaviour is measured by the gate's rejection rate instead.

### 4.3 Statistical treatment

All system comparisons are paired on the same queries. Binary outcomes use McNemar's exact test; continuous per-query outcomes use the Wilcoxon signed-rank test, preferred over the paired t-test because per-query faithfulness is bounded and left-skewed with a mass at 1.0, violating the normality assumption on the paired differences. We report effect sizes (Cohen's d_z, Cliff's δ) alongside every p-value, and bootstrap percentile confidence intervals for the headline figure. A p-value without an effect size answers "is it unlikely" but not "is it large", and the difference is material at n = {{N_ANSWERABLE}}.

### 4.4 The gate as a selective-prediction policy

The gate is evaluated as a policy rather than as a component: we sweep the threshold τ and report, for each, the fraction of answerable questions answered, the fraction of unanswerable questions refused, the abstention precision, and the coverage. The operating point is selected by a stated rule — the highest τ that still answers at least 90% of answerable questions — rather than by inspection of a favourable metric. We also report the risk–coverage curve, so the trade-off is visible in full rather than at one chosen point.

Following the finding that adding reranking to hybrid retrieval lowers the correct abstention rate, **the calibration is fitted separately for each retrieval configuration compared**, so that a change in retrieval strength cannot masquerade as a change in gate quality.

**How retriever-specific is it?** We measured it, on three retrievers that give the gate the same kind of input — a cross-encoder score over a candidate pool — so that only the retriever differs: the shipped hybrid, the lexical leg alone, and the dense leg alone. The fitted thresholds are {{GPR_HYBRID_TAU}}, {{GPR_BM25_TAU}} and {{GPR_DENSE_TAU}} respectively, and the operating points move with them: the hybrid's gate answers {{GPR_HYBRID_ANSWERED}} of the answerable questions and refuses {{GPR_HYBRID_REFUSED}} of the unanswerable ones, the lexical gate {{GPR_BM25_ANSWERED}} and {{GPR_BM25_REFUSED}}, the dense gate {{GPR_DENSE_ANSWERED}} and {{GPR_DENSE_REFUSED}}. Applying the shipped threshold unchanged to the lexical leg is **too permissive, and in the direction that flatters the arm it is transferred to**: it answers {{GPR_BM25_XFER_ANSWERED}} of the answerable questions against {{GPR_BM25_ANSWERED}} when refitted, and refuses {{GPR_BM25_XFER_REFUSED}} of the unanswerable ones against {{GPR_BM25_REFUSED}}. On the dense leg the two fitted thresholds coincide and the transfer costs nothing, which is the qualification: a transferred threshold is wrong where the fitted thresholds differ and harmless where they do not, so no single global threshold is defensible. Each retriever's full sweep — {{GPR_SWEEP_POINTS}} thresholds, each with its answer rate, refusal rate, abstention precision and coverage — and its risk–coverage curve are reported, so the frontier is a curve and not a chosen point.

### 4.5 Reproducibility

The corpus is fetched from public endpoints and stored locally; the benchmark generator is seeded; the index and embeddings are cached by content hash; {{REPRO_CLAIM}}. Every result in Section 5 is emitted as JSON alongside the markdown tables used in this paper.

---

## 5. Results

<!-- Sections 5 and 6 are generated from the experiment JSON by
     deliverables/scripts/make_paper_results.py, which replaces everything
     between this heading and the discussion heading that follows it. It is
     not written here on purpose: a hand-written copy of a generated section
     is a copy that goes stale silently. -->

## 7. Discussion

### 7.1 What the framework does well

The framework's strongest property is not any individual mechanism but the fact that each one is *structural*. The gate is a branch rather than an instruction; the quota is enforced on the artefact the generator actually consumes; the conflict report is produced by an orthogonal conjunction rather than by a single classifier's opinion. These properties are auditable, and in an industrial setting auditability is a functional requirement rather than a nicety — a refusal whose reason can be reconstructed from a score and a threshold is usable in a regulatory conversation, and one that cannot is not.

The second strength is the separation of *coverage* from *correctness* as explicit quantities. A framework that reports a single hallucination rate has hidden the trade-off; ours reports the whole risk–coverage surface, which is what lets a deployment choose its own operating point for its own cost function.

### 7.2 What the framework does not do

It does not resolve contradictions; it surfaces them. Given ContextConflict's taxonomy, a binary or type-tagged flag is the instrument available without a trained conflict-type classifier, and the evidence suggests that surfacing beats resolution: CLECK found that models default to the authoritative claim and shift only 34 points when the conflict is made explicit, and ContraDoc found models that outperform humans yet remain unreliable at contradiction detection.

It does not guarantee its own confidence. The calibration is empirical, on a held-out query split, under an exchangeability assumption that a single-category industrial corpus violates. We adopt the diagnostics of the conformal literature as our limitation rather than its guarantees.

{{GEN_LC_OPENING}} The most serious threat to this work is that a 2026 study of document-grounded generation in manufacturing safety reports long-context systems ahead of semantic RAG, and another reports near-perfect performance by placing an entire 26k-token knowledge base in the prompt. Our evaluation corpus fits in a modern context window, so the baseline is feasible and we treat it as a threat rather than a formality. Experiment 7 measures the cost half: on the focus domain the corpus is {{LC_CORPUS_TOKENS}} tokens and the RAG arm's accepted context averages {{LC_RAG_TOKENS}} tokens; {{GEN_LC_COST_CLAIM}} On the six-category corpus the corpus is {{MC_LC_CORPUS_TOKENS}} tokens, which does not fit in the 128K window most hosted models offer at all. A retrieval-side proxy shows the evidence stays locatable at the top of the whole-corpus ranking ({{LC_PROXY_TOP10}} in the top 10 of {{LC_PROXY_SET_SIZE}}). {{GEN_LC_FINDING}}

Three results bear on how this threat should be answered, and all three are cited rather than asserted. The closest published analogue to our corpus is favourable to retrieval: Agri-Query (arXiv:2508.18093) places a 165-page agricultural-machinery operator manual — roughly 59K tokens, chunked at 200 tokens — in the prompt and reports that hybrid RAG consistently beats direct long context, with naive insertion of the whole manual yielding significantly worse results; a machinery manual is what our corpus stands in for. The 2025–2026 consensus is that the question is not *which* to use but *when to route*: LaRA's title is literally *No Silver Bullet for LC or RAG Routing* (arXiv:2502.09977), and the state of the art is a router that escalates only the queries that need it — our long-context arm is the always-long-context arm of exactly that decision, and we measure it rather than assert a preference for the other arm. Finally, *Length Is Cheap, Competition Is Not* (arXiv:2611.04169) reports that the attention mass on evidence explains about 58% of the variance in retrieval loss against at most 8% for log-length, and that a single competing value multiplies the loss by 9–110×, so the expected way a whole-corpus prompt fails on industrial text is *competition among similar values* — several tables stating different numbers for the same quantity — rather than length as such.

The generator-side comparison is the same question asked of the framework's own hypothesis. {{GEN_SUMMARY}}

The replication of that comparison on a second generator could not be run, and the reason is measured rather than guessed: {{GENCOMP_CLAIM}}

### 7.3 A benchmark defect we found, and what it changed

The benchmark's own unanswerable half — the half on which a refusal benchmark
lives or dies — was separable from the question text alone. A classifier that
saw only the question told the answerable questions from the unanswerable ones
at an ROC AUC of {{UNANS_BEFORE_AUC}}, and one regular expression caught
{{UNANS_SHORTCUT_BEFORE}} of the unanswerable class with no false positives at
all, because the class's designated hard case asked about a fabricated
identifier (`SKU AST-5454`) and every one of those questions carried an
identifier shape that no answerable question carried. If a system's
unanswerability is visible in the question, then a system refusing on the
question's shape scores as well as one reading the passages, and the benchmark
cannot tell them apart.

The half was rebuilt rather than reported around. The repaired class uses the
answerable class's own three question stems, its own source documents and its
own label machinery, and each repaired question was drawn to have a
*structural twin* in the answerable class ({{UNANS_MATCH_RATE}} of them have
one). Re-measured, the shape-only classifier scores {{UNANS_SEP_AUC}} against a
permutation null of {{UNANS_SEP_NULL}}, and the one-rule shortcut carries
{{UNANS_SHORTCUT_AFTER}}.

The same artefact has been reported in the same task for a clinical
question-answering benchmark, where the unanswerable questions could be
discerned by filtering on surface n-gram patterns and the evaluation was
thereby compromised (Yang et al., 2024); the shortcut-removal construction used
here is the one applied to insufficient-evidence examples elsewhere (Mondal et
al., 2026); and framing a benchmark repair as the contribution rather than as
a footnote follows the precedent of Brunello et al. (2026). What is not
reported anywhere is the question-only separation of an answerable/unanswerable
split in a RAG *refusal* benchmark, its effect on the reported refusal rate,
and a repair by regenerating the unanswerable class with answerable-style
templates (Gautam et al., 2023).

What it changes is the framework's headline number, which is why it is
reported here rather than buried in the limitations. On the pre-repair class
the gate refused a large majority of the unanswerable questions; on the
repaired class it refuses {{UNANS_HARD_REFUSED_PCT}} of the corpus-anchored
ones ({{UNANS_HARD_REFUSED_N}}) — questions the corpus discusses but states no
value for — and {{UNANS_OOD_REFUSED_PCT}} of the out-of-domain ones
({{UNANS_OOD_REFUSED_N}}). The detection problem this framework addresses is
considerably harder than the first version of the benchmark made it look. That
is a worse number for the framework and a better one for the reader, and the
repair is what produced it.

### 7.4 Threats to validity

The principal internal threat is that our own silver labels are optimistic and mechanically tied to the chunking, which could inflate the benefit of a retriever that shares the chunking's biases. The principal external threat is that the corpus is public reference material rather than proprietary industrial documentation, so the query distribution is not the operational one. The principal construct threat is that we measure retrieval and gating quality but not end-to-end decision quality, which requires a practitioner study; the earlier 16-participant study is a pilot, and at that sample size it supports a within-subject sign test but not a claim about generalisation.

---

## 8. Limitations

1. **Scale.** The primary corpus is 634 chunks across 24 documents with a 30-query calibration set and a 16-participant user study, all below the scale at which the statistical framing we use is well-founded. Claims are framed as demonstration and mechanism, not generalisation.
2. **Scope: the proposal's twelve categories, and the six that were built.** The proposal described a twelve-category industrial benchmark spanning three domains; this paper evaluates six of the nine industrial-engineering categories, on three corpora it could obtain and redistribute, and claims nothing about the twelve-category benchmark. The three machine-learning categories were descoped as a different problem class and three industrial categories because their binding artefacts are proprietary; §1.3 states the reconciliation and `research/12_scope_reconciliation.md` carries the table. Every claim in this paper is about the corpora it was measured on.
3. **Modality sparsity.** At 2.3% chart and 7.1% table, the corpus cannot exercise the modality mechanism with adequate power. The null result is expected and is reported as such.
4. **Reranker regression.** Cross-encoder reranking regresses on some sub-categories; fine-tuning on domain-matched data is future work.
5. **NLI on technical text, and the contradiction gate's measured precision, which is zero on this corpus.** Published ceilings are materially below general-domain performance, and the gate's precision has since been measured against reader labels rather than against a proxy: {{CONTRA_PRECISION_CLAIM}} {{CONTRA_BRANCH_CLAIM}} {{CONTRA_PRECISION_MECHANISM}} {{CONTRA_CONTROL_CLAIM}} The calibration fitted from that measurement leaves {{CONTRA_SURFACED}} findings surfaced and {{CONTRA_WITHHELD}} withheld on this corpus, so the shipped system is silent about conflicts here rather than wrong.
6. **Judge validity.** Any LLM-annotated component carries the measured position and leniency biases; a human-validated subset is required.
7. **Long context compared on cost, and on answer quality for the focus domain.** On the focus domain {{GEN_LC_COST_CLAIM}} The six-category corpus exceeds the 128K window most hosted models offer ({{MC_LC_RATIO}}x the RAG arm's context by the corpus's own token counts) but fits the 1M-token window of the generator used here, so the answer-quality comparison is made on the focus domain because that is the domain this paper is about and because the two corpora are never pooled -- not because the comparison would have been impossible. {{GEN_LC_FINDING}} {{GEN_LC_CLAIM}}.
8. **Calibration is deployment-specific.** Thresholds must be re-fitted per retrieval configuration and per corpus.
9. **The gate judges evidence, not form, and the form check that stands in front of it is conservative.** The gate decides whether the answer is present in the retrieved context, and never checks whether the query is well-formed: on the {{FORM_PROBE_N}} malformed query stems the benchmark's own generator produced and rejected, on {{FORM_PROBE_CORPUS}}, the gate accepted {{FORM_PROBE_ACCEPTED}} ({{FORM_PROBE_RATE}}) at the fitted operating point of {{TAU}}, against a refusal rate of {{UNANS_HARD_REFUSED_PCT}} on the hard genuinely-unanswerable questions. The separate runtime form check does refuse malformed requests — on {{FORMVAL_CORPUS}}, {{FORMVAL_STEM_MAL_REJECTED}} of the {{FORMVAL_STEM_MAL_N}} hand-labelled malformed stems ({{FORMVAL_STEM_MAL_RATE}}) — but it is a lexical check, not a parser: the malformed stems it misses are truncated *clauses*, whose malformation is grammatical rather than lexical, and it has no dictionary or language model, so a keyboard mash passes it. Its false-rejection rate was measured rather than assumed: {{FORMVAL_STEM_GOOD_REJECTED}} of {{FORMVAL_STEM_GOOD_N}} hand-labelled well-formed stems and {{FORMVAL_BENCH_REJECTED}} of the {{FORMVAL_BENCH_N}} benchmark queries were refused. The generator is injected into the framework and is reached at exactly one line, after the gate accepts, so a refused query costs no model call.
10. **The framework's hypothesis H2.1 — that a code-level, non-bypassable gate reduces hallucination — is {{GEN_H2_1_SHORT}}** {{GEN_H2_1_EVIDENCE}}
11. **The benchmark's unanswerable class was separable from the question text alone — and the defect was found by auditing it and then repaired.** {{UNANS_AUDIT_SENTENCE}} The defect was in the half's designated hard case, which asked about a fabricated identifier (`SKU AST-5454`); a single regular expression caught {{UNANS_SHORTCUT_BEFORE}} of the class with no false positives at all. The half was rebuilt as a corpus-anchored class — the same question stems, the same source documents, the same label machinery, and each repaired question given a structural twin in the answerable class ({{UNANS_MATCH_RATE}}) — and every measurement was taken again. What remains: the repaired class is labelled by the complement of the benchmark's own extraction branches, so a question the corpus answers in a form neither branch recognises would be labelled unanswerable when it is not. {{UNANS_RESIDUAL_CLAIM}}

---

## 9. Conclusion

This paper presented an evidence-grounded retrieval-augmented generation framework for industrial decision support, and was deliberate about the strength of each kind of claim it makes. The architectural contribution is incremental and is positioned against published prior art rather than asserted as priority. The empirical contribution is a failure-mode characterisation: on an independently constructed public industrial corpus, cross-encoder reranking is shown to improve ordering while degrading recall on the six-category corpus and to buy nothing at all on the single-category focus domain, the modality quota is shown to belong before the reranker rather than after it on the corpora the thesis measures it on, with the effect small and its direction corpus-dependent, the dense leg is shown to cost the fusion its ordering until the encoder is replaced, the category pre-filter is shown to cost no recall while improving the ordering, and its benefit is shown to come from restricting the candidate pool the reranker sees rather than from reordering the fused ranking, so that the soft-prior alternative proposed as its repair does not reproduce it, and the modality composition of the corpus is shown to determine whether a modality-aware mechanism can have any effect at all. The methodological contribution is an evaluation protocol that treats the confidence gate as a selective-prediction policy with a risk–coverage curve and a false-positive rate at a stated operating point, with always-flag and never-flag baselines.

The framework's practical value does not depend on any of its mechanisms being individually novel. It depends on each of them being structural, on the trade-offs between them being measured rather than assumed, and on the resulting system being able to say, for every claim it makes, exactly which passage supports it and how confident the system is in that passage's relevance.

---

## References

Asai, A., Wu, Z., Wang, Y., Sil, A., & Hajishirzi, H. (2024). Self-RAG: Learning to retrieve, generate, and critique through self-reflection. In *International Conference on Learning Representations (ICLR 2024)*. arXiv:2310.11511.

Brunello, A., Curaba, C., Geatti, L., Mignani, M., Montanari, A. & Saccomanno, N. (2026). Fixing FOLIO and MALLS: Verified annotations and an LLM-assisted framework to focus human relabeling. *arXiv:2606.02837*.

Bruch, C., Gai, M., & Ingber, D. (2023). An analysis of fusion functions for hybrid retrieval. *ACM Transactions on Information Systems*, 41(6). arXiv:2210.11934. DOI: 10.1145/3596512.

Ceylan, D., Kaynak, U. & Esken, A. (2023). Retrieval-augmented generation for large language models: A survey. *arXiv:2312.10997*.

Cormack, G. V., Clarke, C. L. A., & Büttcher, S. (2009). Reciprocal rank fusion outperforms Condorcet and individual rank learning methods. In *Proceedings of the 32nd International ACM SIGIR Conference on Research and Development in Information Retrieval (SIGIR 2009)*, pp. 758–759. DOI: 10.1145/1571941.1572114.

Decian, J., Njeh, C., & Nakouri, H. (2026). Dynamic RAG with hybrid retrieval: A novel approach to robust LLMs and hallucination prevention. *Neurocomputing*, 705, 134911. DOI: 10.1016/j.neucom.2026.134911.

Es, S., James, J., Espinosa-Anke, L., & Schockaert, S. (2024). RAGAS: Automated evaluation of retrieval augmented generation. In *Proceedings of EACL 2024 System Demonstrations*. arXiv:2309.15217.

Farquhar, S., Kossen, J., Kuhn, L., & Gal, Y. (2024). Detecting hallucinations in large language models using semantic entropy. *Nature*, 630(8015), 625–630. DOI: 10.1038/s41586-024-07421-0.

Faysse, M., Sibille, H., Wu, T., Omrani, B., Viaud, G., Hudelet, C., & Colombo, P. (2025). ColPali: Efficient document retrieval with vision language models. In *International Conference on Learning Representations (ICLR 2025)*. arXiv:2407.01449.

Gautam, V., Zhang, M. & Klakow, D. (2023). A lightweight method to generate unanswerable questions in English. *Findings of EMNLP*. arXiv:2310.19403.

Faysse, M., et al. (2024). *T²-RAGBench: Text-and-table benchmark for evaluating retrieval-augmented generation*. In *EACL 2026*. arXiv:2506.12071.

Gao, T., Yen, H., Yu, J.-T., & Chen, D. (2023). Enabling large language models to generate text with citations. In *Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing (EMNLP)*. arXiv:2305.14627.

Geißler, F., Carella, F., Fieback, L., & Spiegelberg, J. (2026). Towards dependable retrieval-augmented generation using factual confidence prediction. *arXiv:2605.05244*.

Huang, J., Chen, X., Mishra, S. R., Zheng, H., Chandak, A., Wu, Y., & Li, X. (2024). Large language models cannot self-correct reasoning yet. In *International Conference on Learning Representations (ICLR 2024)*. arXiv:2310.01798.

Jiang, Z., Xu, F. F., Gao, L., Sun, Z., Liu, Q., Dwivedi-Yu, J., Yang, Y., Callan, J., & Neubig, G. (2023). Active retrieval augmented generation. In *Proceedings of EMNLP 2023*. DOI: 10.18653/v1/2023.emnlp-main.495.

Joren, H., Zhang, J., Ferng, C.-S., Juan, D.-C., & Taly, A. (2024). Sufficient context: A new lens on retrieval augmented generation systems. *arXiv:2411.06037*.

Kadavath, S., Conerly, T., Askell, A., & Henighan, T. (2022). Language models (mostly) know what they know. *arXiv:2207.05221*.

Karpukhin, V., Oğuz, B., Min, S., Lewis, P., Wu, L., Edunov, S., Chen, D., & Yih, W. (2020). Dense passage retrieval for open-domain question answering. In *Proceedings of EMNLP 2020*, pp. 6769–6781. DOI: 10.18653/v1/2020.emnlp-main.550.

Kuhn, L., Gal, Y., & Farquhar, S. (2023). Semantic uncertainty: Linguistic invariances for uncertainty estimation in natural language generation. In *ICLR 2023*. arXiv:2302.09664.

Küster, J., et al. (2026). *ContextConflict: conflict taxonomies for multi-document question answering*. In *EMNLP 2026*. DOI: 10.18653/2026.emnlp-main.918.

Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., Küttler, H., Lewis, M., Yih, W., Rocktäschel, T., Riedel, S., & Kiela, D. (2020). Retrieval-augmented generation for knowledge-intensive NLP tasks. In *Advances in Neural Information Processing Systems 33 (NeurIPS 2020)*, pp. 9459–9474. arXiv:2005.11401.

Liu, X., et al. (2026). *ConflictScore: claim-level conflict quantification in grounded generation*. In *EMNLP 2026*. DOI: 10.18653/2026.emnlp-main.2589.

Lyu, Y., Li, Z.-Y., Niu, S.-M., et al. (2024). CRUD-RAG: A comprehensive Chinese benchmark for retrieval-augmented generation of large language models. *ACM Transactions on Information Systems*. DOI: 10.1145/3701228.

Min, S., et al. (2023). FActScore: Fine-grained atomic evaluation of factual precision in long form text generation. In *Proceedings of EMNLP 2023*. arXiv:2305.14251.

Mondal, J. J., Apurba, M. S. A., Banik, M., Al Mahmud, M. M. & Shihab, I. F. (2026). Before answering: Evidence sufficiency under size-matched memory construction. *arXiv:2609.32269*.

Phillips, E., Gustafsson, F., Wu, S., Thakur, A., & Clifton, D. A. (2026). Entropy alone is insufficient for safe selective prediction in LLMs. *arXiv:2603.21172*.

Rajpurkar, P., Jia, R., & Liang, P. (2018). Know what you don't know: Unanswerable questions for SQuAD. In *Proceedings of ACL 2018*, pp. 518–528. DOI: 10.18653/v1/p18-2124.

Robertson, S., Zaragoza, H., & Taylor, J. (2004). Probabilistic relevance framework: BM25 and beyond. *Foundations and Trends in Information Retrieval*, 3(4), 333–389.

Suri, N., et al. (2024). *VisDoM: multi-document QA with visually rich elements using multimodal retrieval-augmented generation*. *arXiv:2412.10704*.

Simchi-Levi, D., Mellou, K., Menache, I., & Pathuri, J. (2025). Large language models for supply chain decisions. In *AI in Supply Chains: Perspectives from Global Thought Leaders* (M. C. Cohen & T. Dai, Eds.). Springer Series in Supply Chain Management. arXiv:2507.21502.

Su, W., Tang, Y., Ai, Q., & Wu, Z. (2024). DRAGIN: Dynamic retrieval augmented generation based on the real-time information needs of large language models. In *Proceedings of ACL 2024*. arXiv:2403.10081.

Thakur, A., Saparov, A., & Ribeiro, B. (2026). DeclineCraft: A RAG abstention benchmark for jointly measuring combined retrieval and parametric knowledge. *arXiv:2610.28340*.

Thakur, A., et al. (2021). BEIR: A heterogeneous benchmark for zero-shot evaluation of information retrieval models. In *NeurIPS 2021 Datasets and Benchmarks Track*. arXiv:2104.08663.

Thakur, A., et al. (2025). *FreshStack: building realistic benchmarks for evaluating retrieval on technical documents*. In *NeurIPS 2025*. arXiv:2504.13128.

Ueda, K., et al. (2026). *SCAN: semantic document layout analysis for textual and visual retrieval-augmented generation*. In *EACL 2026 Findings*. arXiv:2505.14381.

Yan, S.-Q., Gu, J.-C., Zhu, Y., & Ling, Z.-H. (2024). Corrective retrieval augmented generation. *arXiv:2401.15884*.

Zhang, W., & Zhang, J. (2025). Hallucination mitigation for retrieval-augmented large language models: A review. *Mathematics*, 13(5), 856. DOI: 10.3390/math13050856.

---

*All arXiv identifiers and DOIs in this reference list were resolved against a live bibliographic API. Where a DOI in an earlier version of this project's documents was found to resolve to a different paper, the correct identifier is used here.*

Yang, Y., Kim, S., Kim, S., Lee, G., Yun, S.-Y. & Choi, E. (2024). Towards unbiased evaluation of detecting unanswerable questions in EHRSQL. *arXiv:2405.01588*.
