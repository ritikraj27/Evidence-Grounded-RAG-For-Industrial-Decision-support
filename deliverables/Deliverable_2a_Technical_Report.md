# An Evidence-Grounded Retrieval-Augmented Generation Framework for Industrial Decision Support: Architecture, Evaluation Protocol, and Failure-Mode Characterisation

**Ritik Raj [25IM60R12]** — Department of Industrial and Systems Engineering, Indian Institute of Technology Kharagpur
**Supervisor:** Dr. Sri Krishna Kumar

*Single-column technical report format. The IEEE two-column and journal-format versions of this paper are Deliverables 2b and 2c.*

---

## Abstract

Industrial practitioners make decisions from paperwork: standard operating procedures, failure-mode and effects analyses, control plans, maintenance logs, calibration records and supplier documents. Generic large language model (LLM) assistants answer such questions fluently but cannot be trusted, because there is no trace from a number back to the page that justifies it, no way to distinguish an inferred claim from a stated one, and no warning when two sources disagree. Retrieval-augmented generation (RAG) grounds the answer in retrieved passages, but existing systems trust the retriever unconditionally, ignore modality diversity, and silently pick one source when documents conflict. In an industrial setting a wrong economic order quantity, wrong incoterm, or wrong safety-stock rule can stop a production line, misplace inventory, or fail an audit. This paper presents a five-mechanism framework for industrial decision support: a code-level, non-bypassable retrieval-confidence gate that returns an explicit "no evidence" response without invoking the language model; per-modality retrieval quotas; hybrid lexical–dense retrieval with a category pre-filter fused by reciprocal rank fusion and reranked by a cross-encoder; contradiction surfacing through a joint natural-language-inference (NLI) and topical gate; and per-claim three-band confidence tagging. We are explicit about what is and is not novel. Every architectural component has published prior art, which we position against rather than claim priority over; our substantive contribution is a failure-mode characterisation, obtained on an independently constructed public industrial corpus of 2,383 chunks across six categories and a 276-query silver-standard benchmark containing deliberately unanswerable questions, with supply chain management as the single industrial domain the work focuses on — the ablation and gate measurements are taken on that domain's 735-chunk subset (176 queries), and the remaining categories carry the cross-category transfer study. We observe, on a corpus independent of the one originally used, the regression of cross-encoder reranking on recall, together with the candidate-pool curve that explains it — a curve that peaks at a pool of about 10 and then declines — and we identify three design properties that the original specification had wrong: a general-purpose sentence encoder costs the fusion its ordering until it is replaced with a retrieval-trained one, a modality quota binds only when applied *before* the reranker rather than after it, and a category pre-filter applied to only one of two retrieval legs is a no-op. We also show that the modality composition of the corpus, rather than the retrieval algorithm, determines whether a modality-aware mechanism can have any effect at all — a null result that is the expected outcome on a text-heavy corpus and is, we argue, under-reported in the literature. We are explicit about what our corpus is: industrial-engineering *encyclopaedic* text drawn from English Wikipedia under CC BY-SA 4.0, shipped in full with per-document provenance, and not the operating manuals, control plans and supplier specifications a practitioner actually uses. Claims that depend on such documents are not made. We repeat every measurement on a second corpus built for the purpose: 110 United States federal regulatory documents (2,443 chunks, 4 regimes) read through the Electronic Code of Federal Regulations at two past dates, so that the same provision at two issues *is* a conflict whose type is known by construction and needs no annotation. The negative findings replicate there — the lexical leg carried the pipeline (-0.081, p = 0.00026) while neither the fusion nor the category pre-filter added anything measurable on top of it — and the candidate-pool curve stops being saturated, so that 1.21% of the retrieved golds are displaced out of the ten-chunk context. There, and this is the paper's clearest new result, a conflict detector's precision splits into two numbers: detection 0.659 against readers' labels and 1.000 against the construction labels, against typing 0.073 and 0.000. The mechanism finds the conflicts and reports them as the wrong kind. A 2×2 factorial over the annotation rubric and the reader's specialisation shows that the rubric's wording, not the specialisation, moved that measured precision (+0.366 and +0.317 against +0.049 and +0.000), which is a warning about the measurement rather than a clean result about the mechanism. We evaluate the confidence gate as a selective-prediction policy with a risk–coverage curve and a false-positive rate at a stated operating point, with always-flag and never-flag baselines, following recent findings that a filter result reported without these quantities does not mean anything. We also report a methodological result we did not expect: auditing our own benchmark showed that its unanswerable class — the half on which a refusal benchmark lives or dies — was separable from the question text alone, because its designated hard case named a fabricated identifier that no answerable question carried. The refusal rate that class produced was an upper bound rather than a measurement. The class was rebuilt so that unanswerability is decidable only from the evidence, every measurement was taken again, and the gate refuses 23.6% of the repaired hard class against the 91.7% the defective class suggested.

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

**Empirical — a failure-mode characterisation, mostly of negative results.** Our substantive contribution is what the measurements show, and several of them contradict the framework's original specification and one contradicts the direction the field has been moving. The dense leg is not merely weaker than the lexical leg: on a corpus whose questions are derived from the documents themselves, fusing it in costs the fusion its ordering until the encoder is replaced with a retrieval-trained one. And the modality quota's pipeline position inverts the rule the framework was designed on: on the focus domain and the six-category corpus it belongs before the cross-encoder rather than after it, while on the industrial corpus the ordering reverses by 0.8 points of Recall@10, and None of these differences is statistically significant at the 0.05 level (p = 0.157, 0.480, 0.317 respectively). The confidence gate cannot separate "there is no evidence here" from "the evidence is here and the retriever missed it", because the retrieval scores it uses cannot; it is therefore an answer-in-context detector, and Section 4.4 reports the contingency table that says so rather than a base rate alone. And a reranker's effect on recall is governed by its candidate pool rather than by the reranker.

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

The form check stands in front of it, and it is a different question. The gate asks whether the retrieved evidence supports an answer; the form check asks whether the request is a question at all. It runs before retrieval, so a request it refuses costs no embedding pass, no cross-encoder pass and no model call. It refuses four things — an empty query, a query with no words, a query whose every word is a function word or a deictic ("what is this?"), and a query that ends on a word that cannot end a question ("what are units that?"). Its rates are measured in §8 rather than asserted: it refused 25 of 25 hand-authored malformed queries and 6 of the 16 hand-labelled malformed stems the benchmark's own generator produced (37.5%), against 0 false rejections among 13 hand-labelled well-formed stems and 3 among the 176 benchmark queries.

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

The query and every chunk are embedded with `BAAI/bge-m3` (1024 dimensions, L2-normalised), and ranked by cosine similarity:

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
portfolio of categories -- six in the public corpus measured here, twelve in the original project corpus: Self-RAG's reflection tokens are learned on a training distribution and would have to be re-learned per category, and Huang et al. (2024) show intrinsic self-correction degrades without external feedback.

**Why refuse rather than refine.** CRAG, the nearest prior art, responds to low confidence by improving the evidence and continuing, and still calls the LLM in every branch. Refuse-and-decline is the better choice under a specific condition: the corpus is a fixed, closed set of controlled documents and the cost of a wrong answer exceeds the cost of no answer. That is the industrial case, and stating the condition precisely is the argument; asserting that CRAG is inferior would not be.

### 3.8 Modality quota

A floor on the share of the final context occupied by tables (0.15) and charts (0.05), implemented as a swap: take the natural top-k untouched, and while a floor is unmet, swap the lowest-ranked item of the over-represented modality for the highest-ranked available item of the under-represented modality. A rebuild-based implementation — walk the ranking, skip what would breach a floor, backfill — silently removes good high-ranked items and measurably degraded table recall in our development.

**The pipeline position is decisive.** Applied *before* the reranker, the quota proposes a **membership** for the final ten; the reranker then re-scores those ten and can reorder them but cannot change *which* ten they are, so the forced table chunk survives and the floor binds. Applied *after* the reranker, the quota adjusts the final context by swapping one of the reranked chunks for a table chunk the reranker already ranked below the cut, so it tends to import the wrong chunk and displace a good one. Section 5 reports the measured difference: on the focus domain and the six-category corpus it belongs before the cross-encoder rather than after it, while on the industrial corpus the ordering reverses by 0.8 points of Recall@10, and None of these differences is statistically significant at the 0.05 level (p = 0.157, 0.480, 0.317 respectively). The rule this framework was designed on is therefore inverted on the corpora the thesis measures it on, and not settled on the third.

**Which placement the shipped system uses.** The system applies the quota *before the cross-encoder*, which is the placement Section 5's measurement ranks first on the focus domain -- the domain the thesis is about, and the largest of the three differences the ablation measures. It was built the other way round -- the September 2026 design put the quota after the reranker -- and it stayed that way until 16 November 2026, because changing it invalidates the gate's calibration, the generator-side comparison and the per-claim results together, and the defence was three days away. On that date the default was moved and the measurements that depend on the retrieval were re-taken with it, apart from the per-claim band evaluation against the gold evidence, the per-claim band evaluation against the retrieved evidence and the industrial corpus's per-claim band replication, whose labels come from a panel of reader agents under a written protocol and could not be reproduced.

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

We evaluate on a **silver-standard** benchmark derived from an independently constructed public industrial corpus, not on the 300-query expert-annotated SupplyChainQA v7 of the earlier project report (which is proprietary and unreleased). Silver labels are mechanically derived from the document itself: a table cell becomes a lookup question with the table chunk as gold; a definitional or numeric sentence becomes a question with its chunk as gold. This is cheap, perfectly reproducible, and slightly optimistic — the derived gold chunk is guaranteed to contain the answer somewhere, whereas an expert annotator might judge it insufficient — so it inflates *absolute* recall. It does not bias the *comparison* between systems, which is what the ablation tests, because every system is scored against the same labels. An audit of those labels is reported in the guide's E.8: 0 of the 32 answerable questions carry an answer label attached to the wrong question, which depresses the *answer-side* accuracy of every arm without changing its direction, and leaves the retrieval-side measurements untouched, because the gold chunk is correct in every case.

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
retriever reaches Recall@10 0.969. That is high, and it is a property of the
*label standard* rather than of the corpus: a question derived from a chunk
contains that chunk's own words, so lexical matching is close to an oracle. Two
consequences follow, and both are visible in Section 5. Recall@10 is near its
ceiling for every system, so the discriminating signal is in the ordering
metrics — MRR and nDCG — where the reranker moves MRR by +0.111 on
the six-category corpus and by -0.3 points on the focus domain,
where the fusion is already at the ceiling — and in the modality trade-off,
which is the one place
where a mechanism changes recall rather than order. It is also why an
expert-annotated benchmark matters, and why the NeurIPS 2026 result on
automatic labelers conflating reference faithfulness with factual correctness
(NeurIPS 2026 Evaluations and Datasets Track, arXiv:2610.08026) bears directly
on what this benchmark can be used to claim.

**The corpus, and where it came from.** Every measurement in this paper was
taken on an independently constructed public corpus of 46
industrial-engineering articles (2,383 chunks, six
categories), assembled from English Wikipedia through the MediaWiki API and
licensed CC BY-SA 4.0. It is a substitute for the primary corpus of the
original specification --- 634 chunks across 24 proprietary supply-chain documents
--- which cannot be redistributed and therefore cannot be shipped with this
paper or re-run by a reader. The substitute ships in full alongside it:
`deliverables/dataset/` holds the documents and a manifest giving, for each
one, its Wikipedia URL, the upstream revision it was read at, the SHA-256 of
the bytes used, and its chunk count.

The thesis focuses on a **single industrial domain, supply chain management**
(14 documents, 735 chunks, 176 questions), because that is the domain the primary corpus
covered and the one the practitioner scenarios are drawn from. The remaining
categories are retained for the cross-category transfer objective, which by
definition needs a subset of categories to transfer to held-out ones. Section
5 traces real questions from the focus domain end to end: what the plain
lexical retriever returned, what the full framework returned instead, what the
gate decided and on which signals, and how every claim in the answer was
banded.

Crucially, the benchmark contains a family of **deliberately unanswerable questions** on topics absent from the corpus. Without them, no confidence-gating experiment is meaningful: a system that answers everything scores 100% recall and 0% hallucination.

**What the gate's label actually is, stated exactly.** The gate is calibrated on a query-level label that is 1 iff the gold chunk is present in the reranked candidate pool. That is an *answer-in-context* label, not an evidence-sufficiency label: the literature reserves "sufficiency" for a set-level property, where scoring passages independently cannot detect it. The gate therefore detects whether the answer is in the retrieved context, and it does not judge whether the context is sufficient.

The negative class contains two different kinds of query, and the sizes of both matter. On the evaluation corpus, of 32 answerable questions whose evidence was found, 0 answerable questions had their evidence missed by the retriever, and 144 questions were unanswerable; the retriever's own recall of the gold chunk is 100.0%, so retrieval failure accounts for 0.0% of the negative class. The limitation is worth stating precisely rather than dramatically: **the gate's features are retrieval scores, so its ability to separate "the answer is in the context" from "it is not" is bounded by how well those scores carry that information, and the composition of the negative class moves with the retriever.** On this corpus the retriever is strong enough that the negative class is mostly genuinely unanswerable, and the gate does well; on a corpus where the retriever is weaker, the same gate would face a negative class dominated by retrieval failure, which it cannot resolve, because the scores it uses are exactly the scores that failed. That is why the operating point is a fitted, per-corpus parameter and not a constant of the architecture, and why every claim about the gate here is stated against this decomposition.

The earlier expert-annotated benchmark is reported separately, with Cohen's κ ≥ 0.7 on four categorical fields, and the two are never pooled.

### 4.2 Metrics

Retrieval is measured by Recall@k, Precision@k, MRR and nDCG@k, with graded relevance (3 for a chunk carrying a binding specification, 1 otherwise), and by **per-modality recall**, which is how the modality claim is tested. Generation is measured by faithfulness (the fraction of claims entailed by the context), citation precision and citation recall.

Queries with no gold set are excluded from recall and nDCG aggregates rather than averaged in as zero — a zero would misrepresent a system as failing to retrieve an answer when there is none to retrieve. Their behaviour is measured by the gate's rejection rate instead.

### 4.3 Statistical treatment

All system comparisons are paired on the same queries. Binary outcomes use McNemar's exact test; continuous per-query outcomes use the Wilcoxon signed-rank test, preferred over the paired t-test because per-query faithfulness is bounded and left-skewed with a mass at 1.0, violating the normality assumption on the paired differences. We report effect sizes (Cohen's d_z, Cliff's δ) alongside every p-value, and bootstrap percentile confidence intervals for the headline figure. A p-value without an effect size answers "is it unlikely" but not "is it large", and the difference is material at n = 132.

### 4.4 The gate as a selective-prediction policy

The gate is evaluated as a policy rather than as a component: we sweep the threshold τ and report, for each, the fraction of answerable questions answered, the fraction of unanswerable questions refused, the abstention precision, and the coverage. The operating point is selected by a stated rule — the highest τ that still answers at least 90% of answerable questions — rather than by inspection of a favourable metric. We also report the risk–coverage curve, so the trade-off is visible in full rather than at one chosen point.

Following the finding that adding reranking to hybrid retrieval lowers the correct abstention rate, **the calibration is fitted separately for each retrieval configuration compared**, so that a change in retrieval strength cannot masquerade as a change in gate quality.

**How retriever-specific is it?** We measured it, on three retrievers that give the gate the same kind of input — a cross-encoder score over a candidate pool — so that only the retriever differs: the shipped hybrid, the lexical leg alone, and the dense leg alone. The fitted thresholds are 0.05, 0.10 and 0.05 respectively, and the operating points move with them: the hybrid's gate answers 0.938 of the answerable questions and refuses 0.361 of the unanswerable ones, the lexical gate 0.906 and 0.611, the dense gate 0.812 and 0.660. Applying the shipped threshold unchanged to the lexical leg is **too permissive, and in the direction that flatters the arm it is transferred to**: it answers 0.969 of the answerable questions against 0.906 when refitted, and refuses 0.340 of the unanswerable ones against 0.611. On the dense leg the two fitted thresholds coincide and the transfer costs nothing, which is the qualification: a transferred threshold is wrong where the fitted thresholds differ and harmless where they do not, so no single global threshold is defensible. Each retriever's full sweep — 19 thresholds, each with its answer rate, refusal rate, abstention precision and coverage — and its risk–coverage curve are reported, so the frontier is a curve and not a chosen point.

### 4.5 Reproducibility

The corpus is fetched from public endpoints and stored locally; the benchmark generator is seeded; the index and embeddings are cached by content hash; the retrieval-side experiment scripts are deterministic given the seeds, while the generator-side comparison is not, because the generator's sampling temperature is provider-determined rather than seed-controlled; its five arms are therefore compared on rates over a fixed question set rather than on paired per-question outcomes. Every result in Section 5 is emitted as JSON alongside the markdown tables used in this paper.

---

## 5. Results


Two corpora are in play, and they have different jobs. The **focus
corpus** is the one every ablation and gate measurement in this section is
taken on: 14 documents and 735 chunks in a
single industrial category — supply chain management — with a modality
composition of 88.8% text, 6.0% table and
5.2% chart, closely matching the 2.3% chart and 7.1% table of
the earlier corpus. Its benchmark contains 176 silver-standard
queries, of which 144 are deliberately unanswerable. The
**six-category corpus** — 46 documents, 2,383 chunks, 276 queries — carries the
cross-category transfer experiment in §5.4, because that experiment is defined
on more than one category. Both were constructed independently of the
proprietary supply-chain corpus of the earlier project report, so the results
are reproducible and are not tied to a single document set.

### 5.1 Retrieval ablation

Seven systems were compared on the same 176 queries. Table 1 gives
the results; paired Wilcoxon signed-rank tests between adjacent rungs appear in
the final two columns.

**Table 1 — Retrieval ablation.** Tbl R@10 is recall restricted to gold chunks
that are tables.

| System | R@5 | R@10 | R@20 | P@10 | MRR | nDCG@10 | Tbl R@10 | ΔR@10 | p |
|---|---|---|---|---|---|---|---|---|---|
| A. BM25 only | 0.969 | 0.969 | 1.000 | 0.097 | 0.736 | 0.792 | 1.000 | — | — |
| B. Dense only | 0.781 | 0.812 | 0.875 | 0.081 | 0.652 | 0.688 | 0.875 | -0.156 | 2.53e-02 |
| C. Hybrid (RRF) | 0.969 | 1.000 | 1.000 | 0.100 | 0.798 | 0.847 | 1.000 | +0.188 | 1.43e-02 |
| D. + cross-encoder rerank | 0.906 | 0.969 | 1.000 | 0.097 | 0.795 | 0.836 | 1.000 | -0.031 | 3.17e-01 |
| E. + category filter | 0.906 | 0.969 | 1.000 | 0.097 | 0.795 | 0.836 | 1.000 | +0.000 | 1.00e+00 |
| F. + quota (pre-rerank) | 0.969 | 1.000 | 1.000 | 0.100 | 0.819 | 0.864 | 1.000 | +0.031 | 3.17e-01 |
| G. + quota (post-rerank) | 0.906 | 0.938 | 0.938 | 0.094 | 0.789 | 0.826 | 1.000 | -0.062 | 1.57e-01 |

**The encoder, not the fusion, was the weak part.** Dense-only retrieval
reaches Recall@10 0.812 and BM25-only 0.969; the
fused system reaches 1.000 (p = 2.5e-02 against the dense
leg), a gain of +0.188 over the dense leg and
+0.031 over the lexical one. Against BM25 the fused system's ordering is better too: nDCG@10 0.847 against 0.792, MRR 0.798 against 0.736.
Reciprocal rank fusion gives the two legs equal say in the ranking, so a weaker
leg spends slots on worse candidates.

That deficit is smaller than it was, and the reason is the encoder rather than
the fusion. The dense leg was originally a general-purpose sentence encoder,
trained with a symmetric similarity objective; retrieval is asymmetric --- a
passage does not resemble a question, it *answers* it --- and the mismatch
appeared as a lexical leg that beat the fusion it was supposed to help. With a
retrieval-trained encoder the dense leg improved substantially and the
fusion's ordering deficit against the lexical leg fell by roughly three
quarters. The generalisable point: a hybrid is only as good as its weaker leg,
and the weaker leg spends the stronger leg's slots.


**Reranking helps, and its benefit depends on the pool it is given.** With a
top-50 candidate pool, reranking moved Recall@10 by
-0.031 (p = 3.17e-01), MRR by -0.003 (p = 1.00e+00)
and nDCG@10 by -0.011 (p = 1.00e+00). A cross-encoder can
only reorder what it was given, so it cannot bring in evidence the first stage
discarded, and on a silver-standard benchmark — where Recall@10 is near its
ceiling for every system, because a question derived from a chunk contains that
chunk's own words — the ordering metrics are where the systems differ and where
the paired tests have anything to measure.
The candidate-pool sweep says the same thing from the other side: Recall@10 rises from 0.902 at a pool of 5 to 0.955 at a pool of 10 and then falls back to 0.932 by a pool of 100, because the extra candidates are distractors competing for the same ten slots. The pool buys recall at depth and spends precision at the cut, so the size that maximises one is not the size that maximises the other. This is the most likely explanation of the −5.34
percentage-point reranker regression reported in the earlier project report on
a different corpus, and it converts that regression from an unexplained anomaly
into a testable configuration hypothesis.

**The category pre-filter changes neither recall nor modality precision.** Recall@10 moved from
0.969 to 0.969 (+0.000, p = 1.000)
and table-specific Recall@10 from 1.000 to
1.000. On the six-category corpus, where
the filter has something to do, it is worth +0.000 of Recall@10 and
+0.000 of table recall; on the focus domain the corpus has one
category, so the filter can only be a no-op, and it is. The general point is
that a filter's measured effect is a property of the corpus as much as of the
filter.

**The quota belongs before the cross-encoder, and this inverts the rule the
framework was designed on.** Applied before the reranker it moves Recall@10 by
+0.031 (0.969 to
1.000, p = 3.17e-01) and reaches table recall
1.000. Applied after the reranker it moves
recall by -0.031 and reaches only
1.000 of table recall — so the
post-rerank placement is -0.062 of Recall@10
worse than the pre-rerank one (p = 1.57e-01).

The mechanism is about what each stage can undo. A pre-rerank quota proposes a
*membership* for the final ten; the cross-encoder re-scores those ten and can
reorder them, but it cannot change which ten they are, so a forced table chunk
survives. A post-rerank quota starts from the reranked ten and swaps one of
them for a table chunk the cross-encoder already ranked below the cut, so it
tends to import the wrong table chunk and displace a good one. The corrected
generalisable lesson is that a constraint on a downstream artefact should be
enforced where it can still choose the candidates, not where it must work
against another component's judgement.

**The corpus composition predicts the outcome.** With
88.8% text, a two-table quota can only draw on tables deep in
the ranking — tables less likely to be relevant — displacing relevant prose. A
null or negative modality effect is therefore the *expected* outcome on such a
corpus, not a defect. This is why the framework measures and reports the corpus
composition: it predicts whether the mechanism can have any effect at all.

![Figure 4. Overall Recall@10 against table-specific Recall@10 for the seven ablated systems, focus corpus (black circles, n = 32 answerable: 24 text, 8 table) and industrial corpus (grey squares, n = 247: 117 text, 130 table). The modality quota does not move both axes: on the industrial corpus the pre-rerank quota buys 0.8 points of table recall and gives up 0.8 points of overall recall, and the post-rerank quota lands on exactly the no-quota operating point; on the focus corpus the post-rerank quota gives up 3.1 points of overall recall while table recall stays at 1.000. The quota is a trade, not a gain, and which way it trades depends on where it is applied.](figures/fig4_modality_quota_pareto.pdf)

![Figure 1. Recall against the size of the rerank candidate pool, on the focus corpus (black circles, 32 answerable of 176 queries) and the industrial corpus (grey squares, 247 of 444). The focus curve saturates at a pool of 10, where Recall@10 = Recall@20 = 1.000, and then falls slightly as the reranker is given more candidates to reorder. The industrial curve does not saturate at 10: there Recall@20 reaches 1.000 at a pool of 50 while Recall@10 stays at 0.988, so 1.21 points of gold are retrieved and then pushed out of the ten-chunk context.](figures/fig1_pool_size.pdf)

### 5.2 The confidence gate

The gate was evaluated as a selective-prediction policy over a threshold sweep,
with the calibration fitted on a query-level 60/40 split.

**Table 2 — Calibration quality on the held-out split.**

| Quantity | Fitted here | Earlier project report |
|---|---|---|
| Univariate β₀ / β₁ on the top rerank score | -1.8473 / 0.2159 | — |
| Multivariate intercept | -2.0607 | — |
| Brier score (held-out half) | 0.1510 | — |
| Expected Calibration Error (held-out half) | 0.1044 | — |

**Table 3 — Threshold sweep.**

| τ | answerable answered | unanswerable refused | abstention precision | coverage |
|---|---|---|---|---|
| 0.05 | 0.938 | 0.361 | 0.963 | 0.693 |
| 0.15 | 0.656 | 0.701 | 0.902 | 0.364 |
| 0.25 | 0.500 | 0.882 | 0.888 | 0.188 |
| 0.35 | 0.469 | 0.931 | 0.887 | 0.142 |
| 0.45 | 0.344 | 0.958 | 0.868 | 0.097 |
| 0.55 | 0.312 | 0.958 | 0.863 | 0.091 |
| 0.65 | 0.188 | 0.979 | 0.844 | 0.051 |
| 0.75 | 0.156 | 0.979 | 0.839 | 0.045 |
| 0.85 | 0.125 | 0.993 | 0.836 | 0.028 |
| 0.95 | 0.062 | 1.000 | 0.828 | 0.011 |

**Table 4 — The selected operating point** (rule: highest tau answering >= 90% of answerable queries).

| Quantity | Value |
|---|---|
| τ | 0.05 |
| Answerable questions answered | 0.938 |
| Unanswerable questions refused | 0.361 |
| Abstention precision | 0.963 |
| Coverage | 0.693 |
| Never-refuse baseline (τ = 0): unanswerable refused | 0.000 |
| Always-refuse baseline (τ = 1): answerable answered | 0.000 |
| Loosest threshold in the sweep (τ = 0.05): unanswerable refused | 0.361 |

The last two rows of that table are **not baselines**: the loosest threshold in
the sweep still refuses some unanswerable queries, and the strictest still
answers some answerable ones. The two degenerate policies are the baselines.

The calibration target is a QUERY-level label that is 1 iff the gold chunk is
present in the reranked candidate pool — that is, **answer-in-context
detectability**, not evidence sufficiency. The literature reserves
"sufficiency" for the set-level property that independent passage scoring
cannot detect, so we do not use the word. The negative class holds two kinds of
query, and their sizes matter: of 32 answerable questions whose
evidence was found, 0 answerable questions had their evidence
missed by the retriever, and 144 questions were unanswerable. The
retriever's own recall of the gold chunk is
1.000, so retrieval failure accounts for
0.0% of the negative class. The gate's features are retrieval scores,
so its ceiling is set by the retriever: on this corpus the negative class is
mostly what the gate is meant to detect, and on a corpus with a weaker
retriever the same gate would face a negative class dominated by retrieval
failure that it cannot resolve.

Two observations matter for interpretation. First, the calibration target is a
QUERY-level label and not a chunk-level one. With one gold chunk among fifty
candidates the chunk-level base rate is about 2%, so a classifier answering
"nothing is relevant" is right 98% of the time and the calibration metrics
look excellent while measuring nothing but the base rate. The fitted
coefficients also differ substantially from the earlier project report's values
(β₀ = 2.943, β₁ = 1.680, fitted on 30 queries of a different corpus), which
is not a contradiction but a demonstration that **the calibration is a fitted
parameter of the deployment, not a constant of the architecture.** Second, the operating point trades coverage
for correctness, and both sides must be reported: the never-refuse baseline
refuses no unanswerable questions, so reporting only the refusal rate would
overstate the gain while reporting only the answerable-answer rate would hide
the cost. The abstention-precision column is what distinguishes a working gate
from an abstaining one.

![Figure 2. Risk-coverage of the confidence gate: the risk that an answered query has no answer in its context, against the fraction of queries the gate answers, on the held-out evaluation half (focus n = 71, industrial n = 178). The degenerate policies bound the curve: always answering carries the base rate of the negative class as its risk at full coverage, and always refusing removes the risk at the cost of all coverage. The industrial gate trades risk for coverage; the focus gate buys almost nothing over answering everything. The fitted operating points (tau = 0.05 focus, tau = 0.40 industrial) answer 0.693 and 0.691 of all queries respectively.](figures/fig2_risk_coverage.pdf)

![Figure 3. Reliability of the gate's calibrated probability against observed answerability, on the held-out evaluation half (focus n = 71, industrial n = 178); the upper panel plots observed answerability against mean predicted probability per bin and the lower panel the number of queries in each bin. The industrial gate tracks the diagonal (ECE 0.075, Brier 0.159); the focus gate does not (ECE 0.1044, Brier 0.1510): it puts most of its queries in the lowest confidence bin, where few of them have an answer in context.](figures/fig3_calibration.pdf)

### 5.3 Contradiction surfacing

The joint gate was compared against the NLI-only gate over every pair of accepted
chunks, with the prevalence of true conflicts and the always-flag and never-flag
baselines reported alongside.

**Table 5 — Contradiction detection.** The proxy precision/recall figures in
the machine-readable results are against an NLI-derived label and are therefore
not independent of the detector.

| Detector | Pairs flagged | Flag rate |
|---|---|---|
| NLI alone | 110 | 0.081 |
| The shipped gate | 20 | 0.015 |
| Baseline: always flag | 1350 | 1.000 |
| Baseline: never flag | 0 | 0.000 |

The gate has three branches, and the alarms split
20 semantic, 0 quantity and
0 revision. The same-subject check is what does the
work: it suppresses 90 of the
bare NLI gate's alarms. The revision-supersession check suppresses a further
0 pairs whose apparent conflict was simply
a later revision of the same policy.

**Two rules were measured, found defective, and repaired.** The quantity rule
used to key a number to the nearest distinctive word, so on encyclopaedic text
it fired on citation years, on version numbers and on surnames; the reader
labels confirmed this, and the pre-repair run is archived beside the results so
the repair is checkable rather than asserted. The rule now keys a number to a
measurement term, excludes bare years and hyphenated identifiers, rejects a
measurement term that begins a proper name, and requires the two passages to
be about the same *instance*. The quantity-level conflicts it reports fell from
21 to 0. The second defect was in the subject
check, whose own design says that two passages with high semantic similarity
and no shared objects are almost always about different things, while the
implementation let high similarity through on its own — a topic check rather
than a subject check. Requiring shared concrete objects as well, as designed,
cut the alarms from 81 to
20 over both repairs together. The corpus, the benchmark
and the label standard were not changed.

The gate's precision has since been measured against reader labels rather than
against a proxy, and the measurement is worse than the corroboration shares
suggest. The contradiction gate's precision, measured against reader labels rather than against a proxy, is 0%: none of the 20 labelled alarms was called a contradiction by either annotator, and the 95% upper bound on the gate's true precision is 16.1%. The two annotators do not share a model, both read the sheet blind to the detector's own scores, and both scored 14 of 14 on a control set whose labels are known in advance, and they agree on the contradiction/no-contradiction decision for 101 of the 101 pairs they labelled. The annotators are models rather than people, so the number says the alarms are not confirmed by a reader, not that no reader would ever confirm one.

The gate has three branches, each measured separately: the semantic branch's 0 of 20 alarms were accepted as genuine contradictions by both annotators. A branch whose measured precision is below the calibration floor has its findings recorded and withheld rather than shown to a practitioner — the same discipline the answer gate applies to an answer, applied to the framework's own claims.



The detector's own positive control -- pairs whose correct behaviour is known in advance, written in the industrial register but not drawn from the corpus -- is 11 of 11, with every contradiction caught and every non-conflict left alone. So the mechanism works; this corpus does not test it.

The absolute false-positive rate is therefore near-total on this corpus, which
is consistent with the published NLI ceilings on technical text and with the
observation that a contradiction detector for industrial documentation is a
triage aid rather than an oracle. Each branch's measured precision is fitted
into a calibration the pipeline reads, and a branch below the floor has its
findings withheld rather than shown: on this corpus that leaves
20 findings surfaced and
0 withheld. This is why the design reports a
conflict *type* and refuses to resolve conflicts automatically: published
evidence indicates that surfacing outperforms resolving.

![Figure 6. The contradiction detector's precision against the base rate of real conflicts in the same population, with 95% Wilson intervals; a filled marker means the point estimate clears the framework's 0.5 calibration floor and the branch would act, a hollow one means it does not and the findings would be withheld. The focus corpus's semantic branch has a precision of 0.0 (0 of 20 alarms confirmed by either annotator) on a base rate of 0.0, so it is withheld; the industrial semantic branch reaches 0.65 (26 of 40) against a base rate of 0.35 and would act.](figures/fig6_contradiction_precision.pdf)

### 5.4 Cross-category transfer

The gate's coefficients and threshold were fitted on one half of the six
industrial categories and applied unchanged to the held-out half, with a
leave-one-category-out variant in which each category is held out in turn.

**Table 6 — Leave-half-out transfer.**

| Quantity | Value |
|---|---|
| Tuning categories | predictive_maintenance, production_scheduling, supply_chain_management |
| Held-out categories | facility_layout, quality_engineering, reliability_engineering |
| Calibrator intercept, tuning half | -1.224 |
| Calibrator top-1 rerank weight, tuning half | 3.139 |
| Calibrator intercept, held-out half | -1.383 |
| Calibrator top-1 rerank weight, held-out half | 0.955 |
| τ (fitted on the tuning half, transferred unchanged) | 0.05 |

| Metric (held-out half) | Transferred | Refitted |
|---|---|---|
| Answerable answered | 1.000 | 0.940 |
| Unanswerable refused | 0.139 | 0.236 |

**Table 7 — Per-category retrieval quality.**

| Category | n | Recall@10 | MRR | nDCG@10 |
|---|---|---|---|---|
| facility_layout | 10 | 1.000 | 0.625 | 0.714 |
| predictive_maintenance | 24 | 0.958 | 0.813 | 0.849 |
| production_scheduling | 11 | 1.000 | 0.718 | 0.787 |
| quality_engineering | 23 | 1.000 | 0.651 | 0.738 |
| reliability_engineering | 34 | 0.853 | 0.590 | 0.652 |
| supply_chain_management | 30 | 1.000 | 0.811 | 0.857 |

The qualitative structure of the result is the important part: the *ranking* of
configurations transfers across industrial sub-domains, but the *threshold* does
not transfer unchanged, and the direction of the error is systematic — a
threshold fitted on one configuration is too permissive where it is
transferred, and too permissive in the direction that flatters the configuration
it is transferred to. At the tuning half's threshold applied unchanged to the
held-out half, the gate answers
1.000 of the
answerable questions against
0.940 when the weights
are refitted there, and refuses
0.139 of the
unanswerable ones against
0.236. This is the
practical form of the decline in abstention reported by Thakur et al. (2026),
and it is why the calibration is re-fitted per arm rather than fitted once and
reused.

![Figure 5. A classifier that sees only the question text, with no retrieval, no evidence and no corpus, telling an answerable question from an unanswerable one. Before the repair the two classes were separable almost perfectly on the focus corpus (ROC AUC 0.999, against a permutation null of 0.455 +/- 0.072), and one regular expression for a fabricated identifier caught 76.4% of the unanswerable questions with no false positive at all. After the repair the shortcut catches nothing, and what is left of the procedure's power is small but not zero: AUC 0.608 on the focus corpus (p = 0.050) and AUC 0.708 on the industrial corpus (p = 0.010). On the better-powered six-category corpus it is indistinguishable from chance: AUC 0.533 (p = 0.267). The benchmark's unanswerable class is decidable from the evidence rather than from a question-shape rule, but on two of the three corpora it is not free of form-only separability.](figures/fig5_question_only_roc.pdf)

### 5.5 The benchmark's unanswerable half: audited, and rebuilt

The unanswerable half of a refusal benchmark is where the benchmark lives or
dies, and it was the half audited last. The audit found a serious defect. A
classifier that saw only the question --- no retrieval, no evidence, no
reasoning about the corpus --- told the answerable questions from the
unanswerable ones at an ROC AUC of **0.999**. The
mechanism was concrete: the half's designated hard case asked about an
identifier verified absent from the corpus (`SKU AST-5454`), and every one of
those questions carried an identifier shape that no answerable question
carried, so a single regular expression separated the two classes perfectly,
catching **76.4%** of the unanswerable class with no
false positives at all. If a system's unanswerability is visible in the
question, then a system refusing on the question's shape scores as well as one
reading the passages, and the benchmark cannot tell them apart.

The half was rebuilt rather than reported around. The repaired class uses the
answerable class's own three question stems, its own source documents and its
own label machinery --- the definition branch finds a definition, the numeric
branch finds a value, a table cell holds the answer --- and the repaired class
is labelled by the complement of exactly those tests. Each repaired question
was further drawn to have a *structural twin* in the answerable class: the same
stem, the same subject size, the same shape markers, and no word in common
(**106 of 110** have one). The
certificates the generator writes into each record were then re-checked
against the corpus by a predicate written independently of the generator:
**1 of
110** failed. The rebuilt class is a
near-miss class: the corpus discusses the subject without stating the answer
in the form the label standard recognises, and
**43 of
110** questions are ones the corpus says
something about without defining it. That bounds what the absolute refusal
rate means; it does not bound the arm comparison, in which every arm is asked
the same questions.

**Table 7 — The unanswerable class before and after the repair.**

| Measurement | Before | After | Reference |
|---|---|---|---|
| Separability from the question's shape (ROC AUC) | 0.999 | 0.608 | permutation null 0.468 |
| Separability from the question's words (ROC AUC) | 0.985 | 0.646 | --- |
| One-rule shortcut, share of the class it carries | 76.4% | 0.0% | 0% is the floor |
| Structural twin exists in the answerable class | --- | 106 of 110 | 1.000 is the ceiling |
| Question-only policy, discrimination (ROC AUC) | 0.675 | 0.564 | 0.5 is no discrimination |

The consequence for the framework's headline number is the substantive result
of this section. On the pre-repair class the gate refused a large majority of
the unanswerable questions; on the repaired class it refuses
**23.6%** of the corpus-anchored ones
(26 of 110) --- questions the
corpus discusses but states no value for --- and 76.5%
of the out-of-domain ones (26 of
34), the latter being unanswerable for any system that
knows what the corpus is about. The pooled figure over the whole unanswerable
class is an upper bound. In other words, the detection problem this framework
addresses is considerably harder than the first version of the benchmark made
it look, and the repair is what shows it.

## 6. A second corpus: authentic, versioned, binding industrial text

### 6.1 Why a second corpus, and what it is

The corpus of Section 4 is encyclopaedic prose, and two of this paper's
objectives cannot be closed on it. It contains no conflict a practitioner
would recognise as one: a document read at a single upstream revision cannot
contradict itself, and concept-level prose rarely binds a numeric requirement
that another document contradicts. And it is not the class of document a
practitioner reads — it is reference material about industrial-engineering
concepts, not operating procedures carrying binding limits.

A second corpus was built to close that gap. It is the United States
*Electronic Code of Federal Regulations* (eCFR), read through the versioner
API, which serves any regulation as it stood on any past date. Two properties
follow, and together they close two objectives with one artefact. The text is
authentic and binding: these are the regulations a plant is measured against,
they carry numeric requirements, and they are public domain, so the corpus
ships with the paper. The text is also *versioned*: federal regulations are
amended, so the same section read on 2021-12-31 and on
2026-06-01 is the same rule at two issues. Aligning the two
snapshots gives 948 amended-paragraph
pairs, of which 361
(38.1%) state different
numbers in the two vintages. Such a pair *is* a conflict, and its type is known
by construction: the same provision at two issues is a supersession, not a
contradiction, and no annotation is needed to know that.

The corpus holds 110 documents and 2,443 chunks
(2,324 text,
119 table,
0 chart) in 4 regulatory
regimes, and its benchmark has 444 queries
(247 answerable, 197 unanswerable).
It was audited for the same shortcut the first benchmark had. The one-rule
identifier shortcut that carried 76.4% of the first benchmark's unanswerable
class catches
0 of
197 here, and a question-only classifier separates the
two classes at ROC AUC 0.708 against a permutation null of
0.505. The residual separability is question
length — median 73 characters for the
answerable class against 50 for the
unanswerable one — which is reported rather than hidden.

### 6.2 The retrieval findings replicate on authentic text

The seven-rung ablation of Section 5 was re-run unchanged on the industrial
corpus, over 247 answerable queries.

**Table 8 — Retrieval ablation on the industrial corpus.**

| System | R@5 | R@10 | MRR | nDCG@10 | Tbl R@10 |
|---|---|---|---|---|---|
| A. BM25 only | 0.8785 | 0.9595 | 0.7554 | 0.8026 | 0.969 |
| B. Dense only | 0.8300 | 0.8785 | 0.6600 | 0.7104 | 0.846 |
| C. Hybrid (RRF) | 0.9312 | 0.9595 | 0.7711 | 0.8160 | 0.946 |
| D. + cross-encoder | 0.9757 | 0.9879 | 0.8269 | 0.8671 | 0.977 |
| E. + category filter | 0.9717 | 0.9879 | 0.8339 | 0.8724 | 0.977 |
| F. + quota (pre-rerank) | 0.9717 | 0.9798 | 0.8378 | 0.8740 | 0.985 |
| G. + quota (post-rerank) | 0.9717 | 0.9879 | 0.8333 | 0.8724 | 0.977 |

The lexical leg carried the pipeline: BM25 reached Recall@10
0.9595 against the dense encoder's
0.8785, a difference of
-0.081 (p = 0.00026, n =
247). That is a larger effect and a far smaller p than the
same comparison on the focus corpus. It is also *already published* — lexical
retrieval beating an off-the-shelf dense encoder on legal and regulatory text
has been reported in several jurisdictions — so it is not claimed here as new,
and the dense leg here is a general-purpose encoder that a domain-adapted one
could overtake. What the measurement contributes is the *corollary*: on this
corpus neither the hybrid fusion (+0.000, p =
1.000) nor the category pre-filter
(+0.000, p = 1.000) added anything
measurable on top of the lexical baseline. The cross-encoder did help here
(+0.028, p = 0.0196), unlike on the focus
corpus.

The candidate-pool curve, which was saturated on the focus corpus and so could
not distinguish "the pool stopped helping" from "the corpus had nothing left
to find", is sharp here. At a pool of 50,
Recall@20 reaches 1.000 while Recall@10 stands at
0.988: 1.21% of the golds are retrieved and
then pushed *out of the ten-chunk context* by the reranker's own ordering.

### 6.3 The gate's operating point transfers; its threshold does not

At τ = 0.40 the industrial gate answers
91.5% of the answerable queries and
refuses 58.9% of the unanswerable ones,
with an abstention precision of 0.847 and a
coverage of 0.691. The threshold does not transfer —
0.40 here against 0.05 on the focus corpus —
and the operating point does: coverage 0.691 against
0.693. This is the calibration result of Section 4.4
restated on a second corpus: the threshold is a fitted parameter of the
deployment and must be re-fitted, while the point on the risk–coverage surface
a practitioner cares about is a property of the mechanism. The two
calibrations differ in quality as well as in value: the industrial gate's
expected calibration error is 0.075 against
0.104, while its Brier score is 0.159 against
0.151.

### 6.4 Detection and typing decompose

This is the paper's clearest new result, and it needed a corpus that contains
conflicts to be visible.

240 pairs were assembled in two strata:
90 *revision* pairs (a paragraph and
its amended self) and 150 *similar*
pairs (cross-document retrieval neighbours). The pool is mined by the
*retriever's* own lexical signal and never by the detector's numeric rule, its
NLI probability or its subject check: a pool selected on the detector's
decision rule cannot measure the detector's precision, because every alarm
would be in it by construction. The pairs were read by a panel of domain
specialists — one per regulatory regime — together with a generalist control,
all blind to the detector.

A conflict detector's precision is two numbers, not one. **Detection** asks
whether the alarm is pointing at something real. **Typing** asks whether the
branch that raised the alarm is the branch that owns the conflict. Measured
against the panel's labels, the detector's detection precision is
0.659 (95% CI
0.505–0.784)
and its typing precision is 0.073 (95% CI
0.025–0.194).
On the stratum where the conflicts actually are, detection rises to
0.897.

Against the *construction* labels — the revision stratum, whose conflict type
is known without any judgement — the separation is starker still. Detection
precision is 1.000: every alarm the
detector raises on that stratum points at a real conflict. Typing precision is
0.000: not one alarm was raised by the
branch that owns its conflict. The quantity branch fired on
0 pairs, and its recall against
the 35
construction-labelled limit changes is
0.000.

So the mechanism **finds** the conflicts and **reports them as the wrong
kind**. It calls supersessions contradictions, and it cannot say which
version is in force — because nothing in the retrieved passages says which
issue either of them is. On the industrial corpus the quantity branch is the
thinnest result in the whole study: an exhaustive corpus-wide search over
64 measurement terms found
1,776 candidate cross-document quantity
conflicts — a count that is exact rather than sampled — of which
119 were put to the reader, and the branch fired on 13. The search is deliberately
over-inclusive: two passages about different boilers share the word
"pressure", which is why the reader found
60 of the sampled pairs to be the same word
used for different things and none to be a genuine quantity conflict. The
branch's precision on this corpus is therefore not measurable, and the
framework's calibration floor would withhold it rather than report it.

### 6.5 The measurement's binding constraint was the rubric

The comparison above was confounded, and the confound was in the annotation
rather than in the detector. The first comparison of the old-rubric reader
against the sharpened one had the same reader in one cell and a different
reader in the other, so "the old rubric" and "the generalist" were the same
cell. A 2×2 factorial separates them, with the pairs, the detector and the
regime briefs held constant.

**Table 9 — The rubric × reader-specialisation factorial.**

| Reader | Rubric | Detection precision | Typing precision |
|---|---|---|---|
| generalist | old (marker test) | 0.293 | 0.073 |
| generalist | sharpened (structural test) | 0.659 | 0.073 |
| specialist | old (marker test) | 0.341 | 0.073 |
| specialist | sharpened (structural test) | 0.659 | 0.073 |

| Effect | Δ detection precision |
|---|---|
| **Rubric**, at the generalist | **+0.366** |
| **Rubric**, at the specialist | **+0.317** |
| **Specialisation**, at the old rubric | +0.049 |
| **Specialisation**, at the sharpened rubric | +0.000 |

*The rubric's wording moved the measured precision by about a third of a point;
the reader's domain specialisation moved it by almost nothing.* The mechanism
is concrete. The old rubric required a version marker, and a regulation does
not write its own version in its text, so it missed
63 of the
82 supersessions it was asked to find
(77%),
calling them `no_conflict`; the specialist reader missed
63 of
90
(70%).

Three qualifications are owed to this result. First, the rubric changed the
*definition* of the target as well as the procedure for recognising one, and
this experiment cannot separate the two; what it shows is that the reader
factor is small. Second, "specialisation" here was delivered as a brief to a
fixed reader model, not as a different capability, so the claim is that a
brief plus a sharpened rubric buys nothing over the rubric alone — narrower
than "specialists are not needed". Third, the qualitative principle is already
published: that the annotation guideline is a first-class error source in
model annotation is established. What is new is the factor of nine, and that
it lands on the *reported system measurement* rather than only on the labels.

The generalisable lesson is about measurement rather than about annotation. A
number that moves by a factor of nine with the wording of its own rubric is
not yet a measurement of the thing under test.

### 6.6 The per-claim band measures agreement, not correctness

The third mechanism was measured on both corpora, with the same generator that
produced the focus corpus's answers and with two evidence protocols on each:
the benchmark's own gold evidence (is the claim right?) and the evidence the
retriever actually returned (does a reader agree with the scorer?).

**Table 10 — The per-claim band against an independent reference, on both corpora and both protocols.**

| Corpus and protocol | κ (band vs reference) | Band error (grounded / inferred / uncertain) | Answers with no wrong claim |
|---|---|---|---|
| Focus, gold | 0.049 (-0.026, +0.124) | 0.542 / 0.513 / 0.610 | 34.4% → 50.0% |
| Focus, retrieved | 0.069 (-0.002, +0.139) | 0.118 / 0.103 / 0.220 | 59.4% → 81.2% |
| Industrial, gold | 0.055 (-0.027, +0.138) | 0.077 / 0.119 / 0.139 | 91.1% → 94.9% |
| Industrial, retrieved | 0.017 (-0.066, +0.101) | 0.006 / 0.017 / 0.026 | 98.3% → 99.6% |

Against an independent reference the band is at chance on all four
combinations: κ 0.049 on the focus corpus's gold evidence,
0.069 on its retrieved evidence, 0.055 on the industrial
corpus's gold evidence and 0.017 on its retrieved evidence. The
three bands are also indistinguishable on the gold protocols
(0.542 / 0.513 / 0.610 and
0.077 / 0.119 / 0.139), while they are
ordered on the evidence the band itself saw
(0.118 / 0.103 / 0.220 and
0.006 / 0.017 / 0.026). The sharper way
to state it: **the band measures whether the retrieved passages entail the
claim — agreement with itself — not whether the claim is true.** As a filter
it nonetheless works: keeping only the *grounded* claims raises the share of
answers containing no wrong claim from 34.4% to 50.0% on
the focus corpus's gold protocol, from 59.4% to 81.2% on
its retrieved protocol, and from 91.1% to 94.9% and
98.3% to 99.6% on the industrial corpus's two.

The positional comparison — keeping the first half of an answer rather than
what the band tagged *grounded* — is the *evidence* for that reading, not the
finding itself, and it does not hold everywhere. Of the four
corpus-and-protocol combinations, one gives a significant positional result
(the focus corpus's gold evidence, p = 0.008) and three do not
(p = 0.417, p = 1.000 and p = 1.000).

### 6.7 What the second corpus does not establish

Five limits, stated rather than implied. One jurisdiction, one language and
one regulatory family: the corpus is US federal regulation, and nothing here
shows that the decomposition holds for a plant's own procedures, for a
non-English regulatory regime, or for a corpus of vendor specifications. The
labels are model-generated. The panel's agreement is reported in full, but
agreement between readers is not confirmation that a label is right, and this
paper's own limitation table names this as the cost of replacing human
annotators. The wording of the annotation rubric moved the measured precision
by a factor of nine, which is a warning about every model-annotated number
here and not only about that one. The positional comparison did not replicate
across three of the four combinations, so the band is reported as a filter
with a measurement decomposition, not as a ranking. And the lexical-over-dense
result is a boundary condition on *this* pipeline with a general-purpose
encoder, not a claim about dense retrieval.

### 6.8 The figures

Six figures accompany this section and are released with the paper in
`deliverables/figures/`, as PDF and PNG, one column wide:
`fig1_pool_size` (recall against the rerank candidate pool, both corpora),
`fig2_risk_coverage` (the gate's risk–coverage curve, both corpora),
`fig3_calibration` (reliability of the gate's probability, both corpora),
`fig4_modality_quota_pareto` (overall against table-specific recall for the
seven ablated systems), `fig5_question_only_roc` (the question-only
classifier, before and after the benchmark repair), and
`fig6_contradiction_precision` (the detector's precision against the base
rate of real conflicts). The two LaTeX papers include all six.

## 7. Discussion

### 7.1 What the framework does well

The framework's strongest property is not any individual mechanism but the fact that each one is *structural*. The gate is a branch rather than an instruction; the quota is enforced on the artefact the generator actually consumes; the conflict report is produced by an orthogonal conjunction rather than by a single classifier's opinion. These properties are auditable, and in an industrial setting auditability is a functional requirement rather than a nicety — a refusal whose reason can be reconstructed from a score and a threshold is usable in a regulatory conversation, and one that cannot is not.

The second strength is the separation of *coverage* from *correctness* as explicit quantities. A framework that reports a single hallucination rate has hidden the trade-off; ours reports the whole risk–coverage surface, which is what lets a deployment choose its own operating point for its own cost function.

### 7.2 What the framework does not do

It does not resolve contradictions; it surfaces them. Given ContextConflict's taxonomy, a binary or type-tagged flag is the instrument available without a trained conflict-type classifier, and the evidence suggests that surfacing beats resolution: CLECK found that models default to the authoritative claim and shift only 34 points when the conflict is made explicit, and ContraDoc found models that outperform humans yet remain unreliable at contradiction detection.

It does not guarantee its own confidence. The calibration is empirical, on a held-out query split, under an exchangeability assumption that a single-category industrial corpus violates. We adopt the diagnostics of the conformal literature as our limitation rather than its guarantees.

It does not beat long context on this corpus, and we measured both halves of that comparison. The most serious threat to this work is that a 2026 study of document-grounded generation in manufacturing safety reports long-context systems ahead of semantic RAG, and another reports near-perfect performance by placing an entire 26k-token knowledge base in the prompt. Our evaluation corpus fits in a modern context window, so the baseline is feasible and we treat it as a threat rather than a formality. Experiment 7 measures the cost half: on the focus domain the corpus is 202,529 tokens and the RAG arm's accepted context averages 2,246 tokens; The long-context arm sends 74x more input tokens per query than the pipeline, which at the provider's cached-prefix pricing, with the corpus prefix served as a cache read on 33.0% of the long-context arm's input tokens is a 58.8x input-cost ratio rather than 74x: the token ratio and the cost ratio are different numbers, and only the second one is a cost. On the six-category corpus the corpus is 680,417 tokens, which does not fit in the 128K window most hosted models offer at all. A retrieval-side proxy shows the evidence stays locatable at the top of the whole-corpus ranking (0.969 in the top 10 of 735). The answer-quality half of the comparison was measured on the focus domain. With the whole corpus in the prompt the generator answered 31 of 32 answerable questions, the same coverage as the pipeline, and it declined the unanswerable questions at a comparable rate (76 of 144 against 77 of 144), for 74 times the input actually sent per query. On coverage and on cost the result is settled: the whole-corpus prompt declines no more unanswerable questions than the pipeline does and costs 74 times as much to do it. On answer quality the margin is directional but not statistically significant once the answers are scored without the length confound.

Three results bear on how this threat should be answered, and all three are cited rather than asserted. The closest published analogue to our corpus is favourable to retrieval: Agri-Query (arXiv:2508.18093) places a 165-page agricultural-machinery operator manual — roughly 59K tokens, chunked at 200 tokens — in the prompt and reports that hybrid RAG consistently beats direct long context, with naive insertion of the whole manual yielding significantly worse results; a machinery manual is what our corpus stands in for. The 2025–2026 consensus is that the question is not *which* to use but *when to route*: LaRA's title is literally *No Silver Bullet for LC or RAG Routing* (arXiv:2502.09977), and the state of the art is a router that escalates only the queries that need it — our long-context arm is the always-long-context arm of exactly that decision, and we measure it rather than assert a preference for the other arm. Finally, *Length Is Cheap, Competition Is Not* (arXiv:2611.04169) reports that the attention mass on evidence explains about 58% of the variance in retrieval loss against at most 8% for log-length, and that a single competing value multiplies the loss by 9–110×, so the expected way a whole-corpus prompt fails on industrial text is *competition among similar values* — several tables stating different numbers for the same quantity — rather than length as such.

The generator-side comparison is the same question asked of the framework's own hypothesis. MiniMax-M3 answered the same 32 answerable and 144 unanswerable questions behind five arms that share the generator, the prompt wording, the question set and the scorer, so a difference between them is attributable to the context and the gate and to nothing else: the same retrieval with the gate removed; the framework at the operating point fitted on this benchmark; a control that refuses as many questions as the fitted gate did, but picks them at random; the framework at the operating point transferred unchanged from the cross-category half; the whole corpus in the prompt. With the generator permitted to decline -- the deployed system -- The rate of answering the unanswerable questions was 0.535 (77 of 144), 0.417 (60 of 144), 0.375 (54 of 144), 0.014 (2 of 144), 0.528 (76 of 144) respectively, and the accuracy on the answerable ones 0.633 (30 of 32), 0.800 (30 of 32), 0.714 (21 of 32), 0.333 (6 of 32), 0.548 (31 of 32) respectively. With the permission to decline removed, and the model, the questions, the retrieval and the scorer all unchanged, The rate of answering the unanswerable questions was 0.938 (135 of 144), 0.528 (76 of 144), 0.604 (87 of 144), 0.021 (3 of 144), 0.931 (134 of 144) respectively, and the accuracy on the answerable ones 0.656 (32 of 32), 0.667 (30 of 32), 0.714 (21 of 32), 0.000 (6 of 32), 0.406 (32 of 32) respectively. Of the claims the arms produced on the unanswerable questions, the fraction supported by nothing in the evidence they were given was 0.554, 0.566, 0.529, 0.333, 0.548 respectively, on 130, 106, 85, 3, 155 claims A refusal that also asserts something -- the documents do not contain the demand for this SKU, so the quantity cannot be computed; in general it is computed as ... -- is counted as an answer and scored on the assertion, which is the reading that gives the gate less credit, and 48 of the unanswerable questions drew one. The claim scorer was audited against the benchmark before the comparison was read: 32 of the 33 answers the benchmark itself considers correct are recognised as supported by the evidence that states them, and 8 of the 9 fabricated values are rejected. The gate's contribution is measured under both prompt conditions, and it holds in both. Under the cautious prompt -- the deployed system -- the hypothesis is supported, at a price: the gate reduced the rate of answering unanswerable questions from 0.535 to 0.417, a fall of 11.8 points, at the cost of answering 30 of 32 answerable questions. Paired question by question, the gate refused 23 of the questions the ungated arm answered and let through 6 of the ones it did not (exact McNemar p = 0.002). Under the answering prompt, which differs from the cautious one by a single sentence and by nothing else, the hypothesis is supported, at a price: the gate reduced the rate of answering unanswerable questions from 0.938 to 0.528, a fall of 41.0 points, at the cost of answering 30 of 32 answerable questions. Paired question by question, the gate refused 60 of the questions the ungated arm answered and let through 1 of the ones it did not (exact McNemar p = < 0.001). What the framework claims is therefore not that the gate reduces hallucination whatever the generator does, but that it is the one component whose behaviour does not depend on the generator's cooperation: the prompt can be wrong, and the gate still holds. An audit of the benchmark's answer labels found that 27 of the 132 answerable questions carried an answer attached to the wrong question: a table question named the column its key came from while taking the answer from the next column, and some numeric golds were digit prefixes of longer tokens. The generator was corrected, the benchmark rebuilt and every experiment in this project re-measured against it, so the numbers reported here are post-repair; the audit now finds 0 defective labels out of 32, and the benchmark as it stood before the repair is kept so that the finding stays checkable. The accuracy margin over the long-context arm reaches no test's significance threshold -- not under the whole-answer entailment test, not under a length-controlled re-scoring of the same answers, and not under a lexical test that ignores length (p = 0.727, 0.508, 0.250), so the long-context comparison is settled on coverage and cost and directional rather than significant on answer quality.

The replication of that comparison on a second generator could not be run, and the reason is measured rather than guessed: MiniMax-M3 returned no text on 0 of the 66 questions it was asked (0 of them on the benchmark's table-lookup family, against 0 of 22 on a control sample of the other families); MiniMax-M3.1-Flash returned no text on 24 of the 66 questions it was asked (23 of them on the benchmark's table-lookup family, against 1 of 22 on a control sample of the other families). The failures are not a shortage of output budget -- of the requests that came back empty, 13 were rescued by retrying at 4096 tokens and 11 were still empty there, the model spending the whole budget on reasoning and returning nothing. An empty completion is neither an answer nor a refusal, so the harness records the run as not-run instead of reporting a rate it cannot stand behind.

### 7.3 A benchmark defect we found, and what it changed

The benchmark's own unanswerable half — the half on which a refusal benchmark
lives or dies — was separable from the question text alone. A classifier that
saw only the question told the answerable questions from the unanswerable ones
at an ROC AUC of 0.999, and one regular expression caught 76.4% of the unanswerable class with no false positives at
all, because the class's designated hard case asked about a fabricated
identifier (`SKU AST-5454`) and every one of those questions carried an
identifier shape that no answerable question carried. If a system's
unanswerability is visible in the question, then a system refusing on the
question's shape scores as well as one reading the passages, and the benchmark
cannot tell them apart.

The half was rebuilt rather than reported around. The repaired class uses the
answerable class's own three question stems, its own source documents and its
own label machinery, and each repaired question was drawn to have a
*structural twin* in the answerable class (106 of 110 of them have
one). Re-measured, the shape-only classifier scores 0.608 against a
permutation null of 0.468, and the one-rule shortcut carries 0.0%.

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
repaired class it refuses 23.6% of the corpus-anchored
ones (26 of 110) — questions the corpus discusses but states no
value for — and 76.5% of the out-of-domain ones
(26 of 34). The detection problem this framework addresses is
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
5. **NLI on technical text, and the contradiction gate's measured precision, which is zero on this corpus.** Published ceilings are materially below general-domain performance, and the gate's precision has since been measured against reader labels rather than against a proxy: The contradiction gate's precision, measured against reader labels rather than against a proxy, is 0%: none of the 20 labelled alarms was called a contradiction by either annotator, and the 95% upper bound on the gate's true precision is 16.1%. The two annotators do not share a model, both read the sheet blind to the detector's own scores, and both scored 14 of 14 on a control set whose labels are known in advance, and they agree on the contradiction/no-contradiction decision for 101 of the 101 pairs they labelled. The annotators are models rather than people, so the number says the alarms are not confirmed by a reader, not that no reader would ever confirm one. The gate has three branches, each measured separately: the semantic branch's 0 of 20 alarms were accepted as genuine contradictions by both annotators. A branch whose measured precision is below the calibration floor has its findings recorded and withheld rather than shown to a practitioner — the same discipline the answer gate applies to an answer, applied to the framework's own claims.  The detector's own positive control -- pairs whose correct behaviour is known in advance, written in the industrial register but not drawn from the corpus -- is 11 of 11, with every contradiction caught and every non-conflict left alone. So the mechanism works; this corpus does not test it. The calibration fitted from that measurement leaves 20 findings surfaced and 0 withheld on this corpus, so the shipped system is silent about conflicts here rather than wrong.
6. **Judge validity.** Any LLM-annotated component carries the measured position and leniency biases; a human-validated subset is required.
7. **Long context compared on cost, and on answer quality for the focus domain.** On the focus domain The long-context arm sends 74x more input tokens per query than the pipeline, which at the provider's cached-prefix pricing, with the corpus prefix served as a cache read on 33.0% of the long-context arm's input tokens is a 58.8x input-cost ratio rather than 74x: the token ratio and the cost ratio are different numbers, and only the second one is a cost. The six-category corpus exceeds the 128K window most hosted models offer (282x the RAG arm's context by the corpus's own token counts) but fits the 1M-token window of the generator used here, so the answer-quality comparison is made on the focus domain because that is the domain this paper is about and because the two corpora are never pooled -- not because the comparison would have been impossible. The answer-quality half of the comparison was measured on the focus domain. With the whole corpus in the prompt the generator answered 31 of 32 answerable questions, the same coverage as the pipeline, and it declined the unanswerable questions at a comparable rate (76 of 144 against 77 of 144), for 74 times the input actually sent per query. On coverage and on cost the result is settled: the whole-corpus prompt declines no more unanswerable questions than the pipeline does and costs 74 times as much to do it. On answer quality the margin is directional but not statistically significant once the answers are scored without the length confound. the comparison is measured, and on this corpus it does not support a superiority claim for long-context prompting in this domain.
8. **Calibration is deployment-specific.** Thresholds must be re-fitted per retrieval configuration and per corpus.
9. **The gate judges evidence, not form, and the form check that stands in front of it is conservative.** The gate decides whether the answer is present in the retrieved context, and never checks whether the query is well-formed: on the 30 malformed query stems the benchmark's own generator produced and rejected, on the six-category corpus, the gate accepted 23 (76.7%) at the fitted operating point of 0.05, against a refusal rate of 23.6% on the hard genuinely-unanswerable questions. The separate runtime form check does refuse malformed requests — on the focus domain, 6 of the 16 hand-labelled malformed stems (37.5%) — but it is a lexical check, not a parser: the malformed stems it misses are truncated *clauses*, whose malformation is grammatical rather than lexical, and it has no dictionary or language model, so a keyboard mash passes it. Its false-rejection rate was measured rather than assumed: 0 of 13 hand-labelled well-formed stems and 3 of the 176 benchmark queries were refused. The generator is injected into the framework and is reached at exactly one line, after the gate accepts, so a refused query costs no model call.
10. **The framework's hypothesis H2.1 — that a code-level, non-bypassable gate reduces hallucination — is supported under both prompt conditions** The hypothesis was tested under two prompt conditions that differ by a single sentence, with everything else -- the model, the questions, the retrieval, the scorer -- held fixed. Conditional: the hypothesis holds under both prompt conditions. Under the cautious prompt -- the deployed system -- it is supported, at a price: the gate reduced the rate of answering unanswerable questions from 0.535 to 0.417, a fall of 11.8 points, at the cost of answering 30 of 32 answerable questions. Paired question by question, the gate refused 23 of the questions the ungated arm answered and let through 6 of the ones it did not (exact McNemar p = 0.002). Under the answering prompt, which differs from the cautious one by a single sentence, it is supported, at a price: the gate reduced the rate of answering unanswerable questions from 0.938 to 0.528, a fall of 41.0 points, at the cost of answering 30 of 32 answerable questions. Paired question by question, the gate refused 60 of the questions the ungated arm answered and let through 1 of the ones it did not (exact McNemar p = < 0.001). What the framework claims is therefore that the gate reduces the rate of answering unanswerable questions whatever the generator does, and that it is the one component whose behaviour does not depend on the generator's cooperation: the prompt can be wrong, and the gate still holds. A refusal rate and a hallucination rate on generated text remain different quantities, and the two are still not interchangeable in the abstract.
11. **The benchmark's unanswerable class was separable from the question text alone — and the defect was found by auditing it and then repaired.** A classifier that sees only the question's *shape* -- its stem, its subject size, whether the subject contains a digit, an acronym or a fabricated identifier -- tells the answerable questions from the unanswerable ones with an ROC AUC of 0.608 against a permutation null of 0.468 that the same procedure produces on shuffled labels (p = 0.050), against 0.999 before the unanswerable class was rebuilt; on the better-powered six-category benchmark, whose answerable class is four times larger, the same measurement gives 0.533 against a permutation null of 0.500 (p = 0.267) The defect was in the half's designated hard case, which asked about a fabricated identifier (`SKU AST-5454`); a single regular expression caught 76.4% of the class with no false positives at all. The half was rebuilt as a corpus-anchored class — the same question stems, the same source documents, the same label machinery, and each repaired question given a structural twin in the answerable class (106 of 110) — and every measurement was taken again. What remains: the repaired class is labelled by the complement of the benchmark's own extraction branches, so a question the corpus answers in a form neither branch recognises would be labelled unanswerable when it is not. The residual form-only separability of the repaired class is 0.608 against a permutation null of 0.468 (p = 0.050) on the focus domain, and 0.533 against a permutation null of 0.500 (p = 0.267) on the better-powered six-category benchmark. It is a small residual that the focus-domain run reaches and the better-powered run does not reproduce: small, but not zero.

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
