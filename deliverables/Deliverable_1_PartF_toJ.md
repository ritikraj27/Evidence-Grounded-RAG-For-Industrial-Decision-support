# Part F — Where this work stands in the literature

This part is the one to study hardest before the presentation. The single most
important thing it establishes is that **most of what the framework does has
published prior art, and the honest contribution is narrower and more defensible
than the architecture alone would suggest.**

## F.0 The literature, by sub-literature

A map of the literatures this work draws on, what each of them established, what
each of them leaves open, and where this thesis sits inside it. F.1 then puts the
five design moves against the same body of work, and F.2 handles the papers a
committee member is most likely to raise one at a time.

Every paper named below was resolved against a live bibliographic service — the
arXiv Atom API, the ACL Anthology, OpenAlex, Crossref or the DBLP — and its
title, authors, year, venue and identifier were read back from the source record
rather than written from memory. The verification record for each sub-literature
is the corresponding file under `research/`, and anything that could not be
resolved is listed there as UNVERIFIED rather than cited as fact.

### F.0.1 Lexical and dense retrieval

**What the literature established.** BM25 is not a historical artefact: BEIR
(Thakur et al., arXiv:2104.08663) evaluated eighteen datasets and ten retrieval
systems and reported that "BM25 is a robust baseline", with re-ranking and
late-interaction models achieving the best zero-shot performance but at high
computational cost. That is the standard this project's retrieval is measured
against. MTEB (arXiv:2210.07316) established the evaluation protocol the
sentence-embedding field now uses.

**What it leaves open.** Which *encoder* to use. BEIR's statement is about
retrieval families, not about the sentence encoders inside the dense leg.

**Where this work sits.** It measured the encoder rather than the family, and the
result was the project's first substantive finding: with a general-purpose
sentence encoder the dense leg reached Recall@10 0.636 against plain
BM25's 0.970, and the *fused* system's ordering was **worse** than the
lexical leg's — the fusion was paying for the dense leg's slots and getting
nothing back. Swapping in a retrieval-trained encoder (BAAI/bge-m3) moved
the dense leg to 0.812 and the fusion to 1.000 against BM25's 0.969. So
the question "does hybrid retrieval beat BM25?" has a conditional answer: it
depends on which encoder is in the dense leg, and on neither corpus in this
project is the difference statistically significant (p = 3.2e-01 on the focus
corpus, p = 3.2 × 10⁻¹ on the six-category corpus). §C.3 works this through.

### F.0.2 Rank fusion and cross-encoder reranking

**What the literature established.** Reciprocal Rank Fusion is Cormack et al.
(SIGIR 2009): rank-only, parameter-free, and therefore robust when the two
lists' scores are not on the same scale. Bruch et al. (*ACM TOIS* 2023) compared
fusion functions systematically and showed the choice among learned functions is
worth a small, consistent amount over RRF. Single-model alternatives now exist:
M3-Embedding (arXiv:2402.03216) does dense, multi-vector and sparse retrieval
in one model, and is a direct alternative to a BM25 + dense + RRF stack.

**What it leaves open.** How large the reranker's candidate pool should be.
Reranking is usually reported as "we rerank the top-k", with k chosen once.

**Where this work sits.** This project's most actionable finding, and one the
literature does not state: **a reranker's recall is governed by the size of its
candidate pool**, and the curve is not monotone. Recall@10 goes from 0.902 at
a pool of 5 to 0.955 at a pool of 10 — the size of the final context — and
then *back down* to 0.932 at a pool of 100, with the knee at 10
and a gain of +0.053 over the endpoints. A pool larger than the context
cannot improve recall at all, since it can only permute the chunks it was
given; a pool past the knee adds distractors that compete for the same ten
slots. This is also the most likely explanation of the −5.34 pp reranker
regression reported in the September 2026 project report on a different corpus.

### F.0.3 Confidence, calibration and conformal prediction

**What the literature established.** That a retrieval-confidence threshold is a
sound idea and that it needs statistics. CRAG (Yan et al., 2024) makes the
retrieval decision on a confidence score; Yadkori et al. (2024) use conformal
prediction for abstention, which buys a coverage guarantee under an
exchangeability assumption; CalibRAG (NeurIPS 2025) addresses calibration at the
decision level; and Geißler et al. (arXiv:2605.05244) frame the whole thing for
industry with conformal chunk selection plus an attention-based factuality
classifier, reporting up to 6% answer-quality improvement and up to 77%
inconsistency detection — while conceding that "the associated statistical
guarantees do not hold generally, since the assumption of sample exchangeability
depends on the retriever setup."

**What it leaves open.** That the threshold is a *fitted parameter of the
deployment*, not a constant of the architecture. Phillips et al. (arXiv:2603.21172)
show entropy-based uncertainty has a model-dependent failure mode and that a
selective-prediction policy must be evaluated at a stated operating risk level.

**Where this work sits.** It follows both instructions: the gate is a calibrated
probability with a stated operating point τ = 0.05, evaluated as a
risk–coverage curve rather than as a single average rate (Brier 0.1510,
expected calibration error 0.1044), and it is re-fitted per retrieval
configuration. It also follows Geißler et al.'s own caveat as a limitation: the
negative class of this project's gate is dominated by *retrieval failure* rather
than by absence of evidence (0.0%), which
is exactly the regime where a threshold transferred from another retriever is
wrong. §C.6–C.7 derive the posterior; §E.2 measures it.

### F.0.4 Abstention and selective prediction

**What the literature established.** This is the most crowded sub-literature and
the one that most constrains the design. The established findings are:

* **CRAG** (2024) — retrieve, then *evaluate* the retrieved documents for
  relevance before generating, and correct when the evaluation fails.
* **DeclineCraft** (Thakur et al., arXiv:2610.28340) — a 2026 abstention
  benchmark with three findings that bear directly here: adding query rewriting
  and reranking to hybrid dense+sparse retrieval **lowers** the Correct
  Abstention Rate for all twelve models tested; iterative RAG lowers CAR versus
  single-shot in 30 of 40 configurations; and model scale does **not** buy
  abstention ability.
* **TAPS** (Zhang et al., arXiv:2610.16318) — decomposes abstention risk into
  *answering ability* and *distinguishing ability*, and compares at **matched
  coverage**; reports 1.5–9.4 pp lower mean risk than abstention training at
  matched coverage.
* **I-CALM** (Zong et al., arXiv:2604.03904) — a two-stage protocol in which the
  model first chooses to answer or abstain and is then **forced to give a best
  guess** for the abstentions, recovering the counterfactual answer so the
  abstention decision can be scored as a classifier; reports coverage, FAR,
  ECR, CAR and J_abs, and compares at matched coverage including explicit-IDK
  prompting, whose coverage collapses to 0.290 on one model and 0.002 on another.
* **UAEval4RAG** (Peng et al., ACL 2025) — six categories of unanswerable
  request, an Acceptable Ratio and an Unanswered Ratio combined into a Joint
  Score, and prompt restrictiveness as an explicit experimental factor.
* **HALT-RAG** (Goswami & Kurra, arXiv:2509.07475) — a **post-hoc verifier**:
  it operates on the source text and the generated output without performing
  retrieval itself, scores hallucination with an ensemble of two frozen NLI
  models plus lexical signals through a calibrated meta-classifier, and reports
  out-of-fold F1 on HaluEval under a precision-constrained abstention policy.
* **SYNCHECK** (Wu, Gu, Yin & Peng, EMNLP 2024, DOI 10.18653/v1/2024.emnlp-main.527)
  — monitors decoding dynamics to flag unfaithful sentences as they are
  generated; 0.85 AUROC over six long-form RAG tasks, and its FOD decoding
  **outperforms abstention by over 10%**.
* **The Selection Effect** (Tikhomirov & Savchenko, EMNLP 2026) and
  **Recognition–Refusal Misalignment** (Du & Hu, EMNLP 2026) — a gate forwards a
  conditional slice on which the downstream component may be no better than the
  baseline, and *recognising* impossibility and *routing* it to abstention are
  "nearly orthogonal".

**What it leaves open.** Almost everything about the *joint* question this thesis
asks: whether a code-level, non-bypassable gate changes what a generator says,
once the generator's own willingness to decline is controlled for.

**Where this work sits.** Two prompt conditions — a cautious instruction that
permits declining and an answering instruction that does not — run the same
five arms, so that the gate's marginal contribution can be separated from the
generator's. That is a simpler version of I-CALM's protocol, and TAPS's
matched-coverage requirement is the reason the arms are compared at a stated
operating point rather than by refusal count. The result is the framework's own
hypothesis H2.1: **supported under both prompt conditions** The hypothesis was tested under two prompt conditions that differ by a single sentence, with everything else -- the model, the questions, the retrieval, the scorer -- held fixed. Conditional: the hypothesis holds under both prompt conditions. Under the cautious prompt -- the deployed system -- it is supported, at a price: the gate reduced the rate of answering unanswerable questions from 0.535 to 0.417, a fall of 11.8 points, at the cost of answering 30 of 32 answerable questions. Paired question by question, the gate refused 23 of the questions the ungated arm answered and let through 6 of the ones it did not (exact McNemar p = 0.002). Under the answering prompt, which differs from the cautious one by a single sentence, it is supported, at a price: the gate reduced the rate of answering unanswerable questions from 0.938 to 0.528, a fall of 41.0 points, at the cost of answering 30 of 32 answerable questions. Paired question by question, the gate refused 60 of the questions the ungated arm answered and let through 1 of the ones it did not (exact McNemar p = < 0.001). What the framework claims is therefore that the gate reduces the rate of answering unanswerable questions whatever the generator does, and that it is the one component whose behaviour does not depend on the generator's cooperation: the prompt can be wrong, and the gate still holds. A refusal rate and a hallucination rate on generated text remain different quantities, and the two are still not interchangeable in the abstract. The null under
the cautious condition belongs to the Selection Effect and Recognition–Refusal
Misalignment literature: the prompt had already realised the gate's function on
that slice, so the gate's marginal contribution there is legitimately zero, and
the honest reading is "the prompt had done the gate's job", never "gating does
not work". §E.7 has the full comparison.

### F.0.5 Attribution and faithfulness evaluation

**What the literature established.** That the unit of faithfulness measurement
is the *claim*, not the answer. ALCE (Gao et al., EMNLP 2023, arXiv:2305.14627)
introduced **citation precision** and **citation recall** as the backbone
metrics and reported that on ELI5 even the best models lack complete citation
support 50% of the time. FActScore (Min et al., EMNLP 2023, arXiv:2305.14251)
decomposed a generation into atomic facts and scored the share supported by a
reliable source; ChatGPT scores 58%, and its automated estimator has under 2%
error rate across 6,500 generations. TRUE (Honovich et al., NAACL 2022,
arXiv:2204.04991) meta-evaluated factual-consistency metrics and proposed an
*example-level* protocol rather than system-level correlation. ExpertQA
(Malaviya et al., arXiv:2309.07852) collected 484 domain experts across 32
fields to produce 2,177 questions with per-claim attributions. Yue et al.
(EMNLP 2023, arXiv:2305.06311) defined *types* of attribution error.

**What it leaves open.** What to do when the evidence does not support any
part of the answer — which is the per-claim analogue of abstention, and the
subject of Conformal-RAG (arXiv:2506.20978) at the sub-claim level and GRACE
(arXiv:2609.04442), whose three-way Grounded/Refuted/Boundary labelling is
close to this project's *grounded* / *inferred* / *uncertain* banding.

**Where this work sits.** This project uses the atomic-claim decomposition and
reports both sides of the ALCE pair, and it adds the abstention behaviour: a
claim that the retrieved set does not support is labelled *uncertain* rather
than being asserted. The per-claim confidence is a noisy-OR over the
per-chunk entailment probabilities (§C.9), and the information gain reported
alongside it is 1 − H_b(q), so a fully supported claim carries 1 bit and an
unsupported one carries 0. §E.8 audits the answer side rather than trusting it.

### F.0.6 Contradiction and conflict detection

**What the literature established.** That "contradiction" is a category with
sub-types, and that conflating them is the standard error. **ContextConflict**
(EMNLP 2026, DOI 10.18653/2026.emnlp-main.918) identifies six conflict types —
factual, inferential, temporal, granularity, perspective, ambiguity — of which
**only two are genuine contradictions**. **ConflictScore** (EMNLP 2026, DOI
10.18653/2026.emnlp-main.2589) decomposes responses into atomic claims, labels
each against each grounding document, and aggregates into CS-Count/CS-Ratio with
a ConflictBench. Separately, the NLI literature establishes a hard ceiling for
this class of model on technical text: published macro-F1 figures on SciNLI and
MSciNLI are far below general-domain performance, and annotation artefacts and
negation failure compound it.

**What it leaves open.** The *joint* problem this project's D4 addresses — how
to tell a genuine contradiction from two passages that are merely about
different things — and the measurement problem: a conflict detector's precision
cannot be computed against a proxy defined by one of its own branches.

**Where this work sits.** D4 combines a logical-conflict signal (NLI) with an
orthogonal same-subject signal (embedding similarity **or** entity overlap),
because raising the NLI threshold alone suppresses false positives and genuine
conflicts together, whereas adding an independent signal lets the two error
types be traded off separately. The context is reported as a *type* rather than
a binary flag, following ContextConflict, and conflicts are surfaced rather
than resolved, because published evidence indicates that surfacing outperforms
resolving.

**And here the honest result is negative.** Measured against blind reader labels
rather than against a proxy, the gate's precision is 0.0% of 20 alarms; the same readers find 0 contradictions in 80
random unflagged pairs. The corpus holds concept-level prose rather than the
revised procedures the mechanism exists to detect, so **this corpus cannot
evaluate the mechanism at all**, and the deliverables say so rather than quoting
a proxy.

What makes that a finding rather than a shrug is that the measurement was used
to repair the detector. Two rules were defective and both were fixed — the
quantity rule, which keyed a number to the nearest distinctive word, and the
subject check, which let topical similarity through on its own although its own
design says otherwise — and the gate's alarms fell from 81
to 20. A third piece of evidence separates the mechanism
from the corpus: the detector's own positive control, in which the correct
behaviour of every pair is known in advance, is 11 of 11. So the mechanism works, and this corpus cannot test it.

That is also why the shipped system does not cry wolf. Each branch has a
measured precision, fitted into a calibration the pipeline reads, and a branch
below the floor has its findings recorded and withheld rather than shown to a
practitioner — the discipline the answer gate applies to an answer, applied to
the framework's own claims. §C.10 derives the design; §E.3 and §E.11 report the
measurement, and §E.12 gathers what the experiments say together.

### F.0.7 Multimodal and table-aware RAG

**What the literature established.** That a context of prose-only chunks
systematically under-serves industrial documentation, where the binding
requirement usually lives in a table. VisDoMRAG (arXiv:2412.10704), TableRAG
(EMNLP 2025), and VisR-RAG-Fin (2026) all attack retrieval over mixed
document modalities, and TechRAG (arXiv:2606.01613) — *Evidence-Gated
Multimodal Agentic RAG for Technical Literature Reasoning* — is the closest
prior art to the whole thesis and post-dates the proposal.

**What it leaves open.** Where the quota belongs in the pipeline, and whether a
quota helps at all when the corpus has nothing to spare.

**Where this work sits.** The mechanism — a hard, non-bypassable quota on the
*final* context rather than a soft instruction to the model — is not new, and
the thesis does not claim it is. The finding is about *placement and preconditions*:
the quota only pays where the corpus leaves something for it to buy, and **where
it is placed relative to the reranker decides more than the quota's own logic** —
before the reranker it restores the table recall the reranker destroyed
(0.964 → 0.929 → 1.000 on the six-category corpus), after it
it reaches 0.929, and which is cheaper depends on the retriever. §C.8
derives the quota and its placement; §E.1 reports the ablation.

### F.0.8 Industrial RAG and the long-context threat

**What the literature established.** That industrial RAG is a live area with
real deployments and real numbers — and that the strongest threat to any RAG
architecture is that **long context simply wins**. A 2026 study of
document-grounded generation in *manufacturing safety* reports 73.1% for
long-context versus 65.4% for semantic RAG at 26× the token cost, and another
reports 99.3% by placing a ~26k-token knowledge base entirely in the prompt.

**What it leaves open.** What long context costs. Token counts are not a cost
model, and a cost model is what a practitioner needs.

**Where this work sits.** The cost half is measured in dollars, not tokens:
The long-context arm sends 74x more input tokens per query than the pipeline, which at the provider's cached-prefix pricing, with the corpus prefix served as a cache read on 33.0% of the long-context arm's input tokens is a 58.8x input-cost ratio rather than 74x: the token ratio and the cost ratio are different numbers, and only the second one is a cost. The answer-quality half is measured on the focus domain,
where the corpus fits, and the six-category corpus — which exceeds the 128K
window most hosted models offer but fits the 1M-token window of the generator
used here — is reported separately and never pooled with the focus domain.
The answer-quality half of the comparison was measured on the focus domain. With the whole corpus in the prompt the generator answered 31 of 32 answerable questions, the same coverage as the pipeline, and it declined the unanswerable questions at a comparable rate (76 of 144 against 77 of 144), for 74 times the input actually sent per query. On coverage and on cost the result is settled: the whole-corpus prompt declines no more unanswerable questions than the pipeline does and costs 74 times as much to do it. On answer quality the margin is directional but not statistically significant once the answers are scored without the length confound. the comparison is measured, and on this corpus it does not support a superiority claim for long-context prompting in this domain The framing in the proposal's wording
("across diverse industrial sub-domains") is an **intra-domain** transfer study,
and §5.4 says so.

### F.0.9 Benchmark validity and label noise

**What the literature established.** That LLM-generated benchmarks carry label
noise, that LLM-as-judge carries position and leniency biases, and that a
benchmark can be *separable from its input alone* — which makes it a weak test
of the thing it claims to test.

**What it leaves open.** The precedent for a defensible *audit* of one's own
benchmark: not merely reporting that a benchmark may be defective, but
encoding the defect, measuring it, repairing it, and re-measuring everything.

**Where this work sits.** This is where the project made two of its own
findings, and both were negative before they were repaired. The **unanswerable
half of the benchmark was separable from the question text alone**: the
designated hard case asked about a fabricated identifier (`SKU AST-5454`), an
identifier shape no answerable question carried, so a single regular expression
separated the classes perfectly — 76.4% of the class, with no
false positives at all. The half was rebuilt as a **corpus-anchored** class with
the same stems, the same source documents and the same label machinery, and
every measurement was taken again. Separately, an audit of the answer-label
generator found that 27 of the 132 answerable questions carried an answer label
attached to the wrong question (20.5%) —
a table question that names the column its key came from rather than the column its answer came from, and a numeric gold that is a digit prefix of a longer token in the chunk — and the generator was corrected, the benchmark rebuilt, and
everything re-measured against it; the audit now finds 0
remaining defects out of 32. The instrument is kept
alongside the measurement so that the finding stays checkable: the audit is
`impl/experiments/audit_unanswerable_class.py`, the repair is
`impl/scripts/unanswerable_repair.py`, and the benchmark as it stood before the
repair is preserved beside the repaired one.

**The pattern is the same one as the contradiction measurement.** A quantity that
looked like a result — the refusal rate, the precision, the "corroborated"
share — turned out to be an artefact of how the thing was labelled, and the
only way to find out was to audit the instrument rather than trust it.

## F.1 The five design moves against prior art

| Move | Closest prior art | What survives |
|---|---|---|
| **D1** Confidence gate | Geißler et al. 2026 (arXiv:2605.05244), conformal chunk selection; Yan et al. 2024 (CRAG); Yadkori et al. 2024 (conformal abstention) | **Non-bypassability as a control-flow property**, plus industrial-corpus calibration. *Not* "gating on retrieval confidence" as a goal. |
| **D2** Modality balance | VisDoMRAG (arXiv:2412.10704); TableRAG (EMNLP 2025); VisR-RAG-Fin (2026) | **Mechanism** (a hard, non-bypassable quota on the final context) and **domain**, not the goal. |
| **D3** Hybrid + RRF + rerank | Cormack et al. 2009 (RRF); Bruch et al. 2023 (*ACM TOIS*, fusion functions); Thakur et al. 2021 (BEIR); Decian et al. 2026 | Not priority — hybrid beating flat retrieval is a well-established result. The *finding* is that the reranker's effect on recall is **pool-relative**: the measured curve peaks at a pool about the size of the final context, and a larger pool costs as well as gains. |
| **D4** Contradiction surfacing | **No published equivalent.** ConflictScore (EMNLP 2026) is close for D4+D5; ContextConflict (EMNLP 2026) taxonomises conflict types. | **The strongest surviving novelty.** |
| **D5** Per-claim tagging | Conformal-RAG (arXiv:2506.20978) on sub-claims; ConflictScore (EMNLP 2026); GRACE (arXiv:2609.04442) — Grounded/Refuted/Boundary; CalibRAG (NeurIPS 2025) at the decision level | **Calibration *and* presentation in one artefact, for an industrial audience**, with an auditable refusal. |

**The four-claims test.** Before claiming something is new, ask: 1. Does a published paper already do this? (D1, D2, D3, D5: yes.) 2. If so, does it do it *better*? (We do not claim better. We claim different in kind.) 3. If so, is our version *useful for a different reason*? (Auditability, no training, portability across categories.) 4. If no published work covers it, can we defend the claim with our own evidence? (**D4** — and this is where the effort should go.)

## F.2 The papers a committee member is most likely to raise

**1. Decian et al. (2026), "Dynamic RAG with hybrid retrieval: A novel approach to robust LLMs and hallucination prevention," *Neurocomputing* 705, 134911.** Hybrid retrieval with an entropy-based dynamic threshold, reported as a statistically significant gain in correctness. This is the *nearest* prior art to D1 on the mechanism — a retrieval-confidence threshold that changes system behaviour — and the proposal names it as such, so it must be engaged directly. The defensible difference is one of philosophy rather than accuracy: an auditable refusal with a stated reason versus a probabilistic adjustment of the retrieval. **Do not claim to beat it.** A defensible framing is that an entropy-based dynamic threshold adapts continuously to the query, whereas a calibrated posterior with a stated operating point is reproducible and auditable — a different property, and the one that matters in a regulated setting.

**2. Geißler et al. (2026), "Towards Dependable RAG Using Factual Confidence Prediction," arXiv:2605.05244.** Conformal chunk selection plus an attention-based factuality classifier, framed explicitly for industry. Two stages: conformal prediction filters chunks, then an attention-based factuality classifier scores answer–context consistency. Reports up to 6% answer-quality improvement and up to 77% inconsistency detection — and concedes that "the associated statistical guarantees do not hold generally, since the assumption of sample exchangeability depends on the retriever setup." **This is our best citation.** It is *both* the strongest competitor and the source of our own stated limitation.

**3. TechRAG (2026), arXiv:2606.01613** — "Evidence-Gated Multimodal Agentic RAG for Technical Literature Reasoning." Hybrid FAISS+BM25 → cross-encoder rerank, visual retrieval, a 100-point evidence-sufficiency rubric, citation-integrity verification. **This is the closest prior art to the whole thesis and it post-dates the proposal.** It must be cited.

**4. DeclineCraft (Thakur et al., 2026), arXiv:2610.28340.** A 2026 abstention benchmark. Three findings that bear directly on us:
- Adding query rewriting and reranking to hybrid dense+sparse retrieval **lowers** Correct Abstention Rate for all 12 models tested.
- Iterative RAG lowers CAR versus single-shot in 30 of 40 configurations.
- Model scale does **not** buy abstention ability (no significant association).

The first finding is a direct challenge: our D3 *improves* retrieval, and DeclineCraft says better retrieval reduces abstention. **The operational consequence is that the gate's operating point must be calibrated per retrieval configuration.** A single global threshold across arms will manufacture a spurious result. This must be stated as a limitation, not discovered by a reviewer.

**5. Phillips et al. (2026), "Entropy Alone is Insufficient for Safe Selective Prediction in LLMs," arXiv:2603.21172.** Shows entropy-based uncertainty has a *model-dependent* failure mode, and that a selective-prediction policy must be evaluated **at a stated operating risk level**. This is a methodological instruction: evaluate the gate as a selective-prediction policy with a risk–coverage curve, not as a single average hallucination rate. We follow it.

**6. ContextConflict (EMNLP 2026), DOI 10.18653/2026.emnlp-main.918.** Identifies six conflict types — factual, inferential, temporal, granularity, perspective, ambiguity — of which **only two are genuine contradictions**. This is the strongest published justification for a *topical* gate and for reporting a conflict *type* rather than a binary flag.

**7. SYNCHECK (Wu, Gu, Yin & Peng, EMNLP 2024), DOI 10.18653/v1/2024.emnlp-main.527, pp. 9390–9406.** Monitors decoding dynamics — sequence likelihood, uncertainty, context influence, semantic alignment — to flag unfaithful sentences as they are generated; 0.85 AUROC over six long-form RAG tasks, and its FOD decoding **outperforms abstention by over 10%**. **This is the sharpest challenge to D1**, and the answer is set out in Part G.

**8. ConflictScore (EMNLP 2026), DOI 10.18653/2026.emnlp-main.2589.** Decomposes responses into atomic claims, labels each against each grounding document, and aggregates into CS-Count/CS-Ratio, with a ConflictBench. This is close prior art to D4 + D5 combined, and "first-ever conflict detection" would be false.

**9. HALT-RAG (Goswami & Kurra, 2025), arXiv:2509.07475.** The nearest prior art to the confidence gate, and the one a committee will raise first. It is a **post-hoc verifier**: it operates on "the source text and generated output without performing retrieval itself", scores hallucination with an ensemble of two frozen NLI models plus lexical signals through a calibrated meta-classifier, and reports out-of-fold F1 on HaluEval under a precision-constrained abstention policy. So it is prior art for the *detector*, and it is **not** a retrieval-time gate. Its own Future Work says: *"A critical next step for this line of work is to integrate and evaluate detectors like HALT-RAG within a live RAG pipeline to measure its resilience to noisy or irrelevant retrieved context."* **That step is our Experiment 8.** The correct thing to say in the defence is therefore not "our gate is new" — it is not — but "the abstention mechanism is published and we do the measurement the mechanism's own authors name as the next step, and the measurement's answer is conditional in a way detector-level F1 cannot show".

**10. I-CALM (Zong et al., 2026), arXiv:2604.03904.** The paper that most directly answers our experimental-design question. It introduces a **two-stage evaluation protocol**: the model first chooses to answer or abstain, and is then **forced to provide a best guess for the abstained ones**, so the counterfactual answer of every abstention is recovered and the abstention decision can be scored as a classifier of whether that answer would have been wrong. It reports coverage, FAR_answered, ECR, CAR and **J_abs** (Youden's J for the abstention decision), and it compares against baselines **at matched coverage**, including explicit-IDK prompting — which it reports as often impractical, with coverage collapsing to 0.290 on one model and 0.002 on another. Our two prompt conditions are a simpler version of this design; their baseline result is the published precedent for a prompt that refuses on its own.

**11. TAPS (Zhang et al., 2026), arXiv:2610.16318.** Decomposes abstention risk into **answering ability** and **distinguishing ability**, and compares selective answering against abstention training **at matched coverage** on a common evaluation subset, so that neither arm is a straw man. It reports 1.5–9.4 percentage points lower mean risk than abstention training at matched coverage. This is the citation that fixes our comparison protocol: the arms must be compared at matched coverage, or the arm that refuses more wins for the wrong reason.

**12. UAEval4RAG (Peng et al., ACL 2025), 2025.acl-long.415.** Defines six categories of unanswerable request for a given knowledge base, scores systems with an **Acceptable Ratio** and an **Unanswered Ratio**, and combines them in a Joint Score that balances answerable-question correctness against acceptable rejection. It also **sweeps prompt restrictiveness as an explicit experimental factor** and finds that more restrictive prompts reject more unanswerable queries while slightly degrading answerable-question performance, and that "no single configuration consistently delivers optimal performance on both answerable and unanswerable requests". This is the published form of the question our two prompt conditions ask, and its metrics are the ones a refusal count should be reported alongside.

**13. The Selection Effect (Tikhomirov & Savchenko, EMNLP 2026), 2026.emnlp-main.1049,** and **Recognition–Refusal Misalignment (Du & Hu, EMNLP 2026), 2026.emnlp-main.1078.** These two are the reason we report our negative result the way we do. The Selection Effect finds that "encoder gating forwards a conditional slice on which compact LLMs perform no better than the encoder itself, or substantially worse, erasing any standalone LLM advantage" — a gate can destroy the value of what stands behind it, because on the slice the gate forwards, the downstream component is no better than the baseline. Recognition–Refusal Misalignment separates *recognising* impossibility from *routing* it to abstention and finds the two directions "nearly orthogonal", so a model can know the answer is unavailable and answer anyway. **Our cautious-condition null belongs to that literature:** the prompt had already realised the gate's function on that slice, so the gate's marginal contribution there is legitimately zero, and the honest reading is "the prompt had done the gate's job", never "gating does not work". Related caution: ACL 2026 (2026.acl-long.1365) finds that models "systematically overcommit, rarely abstaining", so a single model that abstains is not the general case, and the null we report — reproduced on one generators — is a statement about this setup rather than about gating in general.

## F.3 The threats

**T1 — Long context beats RAG in this exact domain.** A 2026 study of document-grounded generation in *manufacturing safety* reports 73.1% for long-context versus 65.4% for semantic RAG, at 26× the token cost. Another reports 99.3% by placing a ~26k-token knowledge base entirely in the prompt. **On a corpus of this size, long context may simply win** — the focus domain's 735 chunks are 202,529 tokens, which does not fit the 128K window most hosted models offer. This is the most serious threat to the entire thesis. **Parts E.6 and E.7 measure the cost half of it**: The long-context arm sends 74x more input tokens per query than the pipeline, which at the provider's cached-prefix pricing, with the corpus prefix served as a cache read on 33.0% of the long-context arm's input tokens is a 58.8x input-cost ratio rather than 74x: the token ratio and the cost ratio are different numbers, and only the second one is a cost. On the six-category corpus the corpus does not fit the 128K window most hosted models offer at all. The answer-quality half is now measured too: The answer-quality half of the comparison was measured on the focus domain. With the whole corpus in the prompt the generator answered 31 of 32 answerable questions, the same coverage as the pipeline, and it declined the unanswerable questions at a comparable rate (76 of 144 against 77 of 144), for 74 times the input actually sent per query. On coverage and on cost the result is settled: the whole-corpus prompt declines no more unanswerable questions than the pipeline does and costs 74 times as much to do it. On answer quality the margin is directional but not statistically significant once the answers are scored without the length confound. the comparison is measured, and on this corpus it does not support a superiority claim for long-context prompting in this domain.

**Three things bear on how this threat should be answered, and all three are cited rather than asserted.** First, the closest published analogue to our corpus is *favourable* to retrieval: Agri-Query (arXiv:2508.18093) places a 165-page agricultural-machinery operator manual — roughly 59K tokens, chunked at 200 tokens — in the prompt and reports that hybrid RAG consistently beats direct long context, with naive insertion of the whole manual yielding significantly worse results. A machinery manual is what our corpus is a stand-in for. Second, the 2025–2026 consensus is that the question is not *which* to use but *when to route*: LaRA's title is literally *No Silver Bullet for LC or RAG Routing* (arXiv:2502.09977), and the state of the art is a router that escalates only the queries that need it. Our long-context arm is the always-long-context arm of exactly that decision, and we measure it rather than assert a preference for the other arm. Third, a result from November 2026 predicts our own failure mode: *Length Is Cheap, Competition Is Not* (arXiv:2611.04169) reports that the attention mass on evidence explains about 58% of the variance in retrieval loss against at most 8% for log-length, and that a single competing value multiplies the loss by 9–110×. So the expected way a whole-corpus prompt fails on industrial text is *competition among similar values* — several tables stating different numbers for the same quantity — rather than length as such, which is a prediction our corpus can test and our part numbers can show.

**T2 — Query-time filters can measure the benchmark, not the filtering.** A 2026 study of RAG poisoning defences shows AUROC collapsing from 0.953 to 0.758 and miss rate rising from 0.191 to 0.763 after removing a single construction cue from the benchmark, and reports that **12 of 21 published evaluations report no false-positive rate at their operating point.** This is a devastating methodological point: many published RAG filters are detecting a shortcut in the benchmark rather than filtering meaningfully. Our gate must be reported with a false-positive rate at a stated operating point, with length-matched controls and a threshold sweep.

**T3 — LLM-as-judge validity.** Position bias flipped **66 of 80** queries in one measured study; the best judges are still off by up to 5 points and skew lenient; cheap judges achieve AUROC as low as 0.603. If the 500-question benchmark is annotated by LLM agents, the judge must be meta-evaluated against a human-annotated subset.

**T4 — Confident errors.** A claim can be supported by a retrieved passage that is itself stale or wrong. Low uncertainty is not correctness. This is why the framework pairs every confidence tag with a citation, and why D4 (contradiction surfacing) partially covers it — but the literature does not support any claim that contradiction detection catches stale-versus-current conflicts reliably.

**T5 — The corpus is too small for the statistical framing.** 634 chunks, 24 documents, a 30-query calibration set, a 16-participant user study, one focus category. All of these sit below the scale at which conformal machinery, operating-point analysis, or risk–coverage framing are statistically well-founded. Own this early.

**T6 — NLI on technical text is weaker than NLI on general text.** Published ceilings: SciNLI 78.18% Macro-F1, and an LLM-based system on MSciNLI at 51.77%. Annotation artefacts (hypothesis-only at 67%/53%) and negation failure compound this. **The NLI leg must be validated on the industrial corpus, not imported from a general-domain number.**

## F.4 The defensible novelty statement

> Recent work applies conformal prediction to retrieved chunks with finite-sample
> guarantees [Geißler et al., 2026], abstention-policy research shows that a
> threshold must be validated at a stated operating risk level rather than by a
> single average number [Phillips et al., 2026], and empirical studies show that
> better retrieval can *reduce* abstention [Thakur et al., 2026]. We adopt all three
> lessons: we evaluate the gate as a selective-prediction policy with a
> risk–coverage curve, we report a false-positive rate at a stated operating
> point, and we re-fit the calibration for every retrieval configuration we
> compare. We do **not** claim the exchangeability guarantees of conformal
> prediction, because on a single-category industrial corpus those assumptions are
> known not to hold. Our contribution is different in kind: a **code-level,
> non-bypassable** gate that produces an auditable refusal, and, in the
> contradiction-surfacing component, a **type-aware** conflict report in which
> the numeric detector is independent of the NLI verifier and the supersession
> check is explicit. The conjunction itself is not published, but every conjunct
> is — HALT-RAG (arXiv:2509.07475) publishes a calibrated NLI ensemble with
> lexical signals under a precision-constrained abstention policy, which is
> prior art for the *detector*, and Kontrast (arXiv:2607.25959)
> formalises the temporal-change distinction we implement as a supersession
> check. HALT-RAG is, however, a **post-hoc verifier**: it reads the source
> text and the generated output and never retrieves, and its own Future Work
> names "integrate and evaluate detectors like HALT-RAG within a live RAG
> pipeline" as the critical next step — which is the experiment this thesis
> runs. **We do not claim the abstention mechanism is new, and we do not claim
> the contradiction gate is new.** We claim it is a carefully instantiated
> one, we report what it costs rather than only what it catches, and we are
> explicit that the detector's own quality is not the question we answer.
>
> Our headline empirical contribution is not the architecture but the
> **failure-mode characterisation**, and it is mostly negative. We show, on an
> independent corpus, that a modality quota is a **trade and not a gain**, and
> that its pipeline position decides what it costs; that a reranker's effect on
> recall is governed by its **candidate pool** rather than by the reranker; that
> the modality composition of the corpus — not the algorithm — determines
> whether a modality-aware mechanism can have any effect at all; and that the
> confidence gate **cannot separate "there is no evidence here" from "the
> evidence is here and the retriever missed it"**, because the retrieval scores
> it uses cannot. That last one is a negative result about our own mechanism,
> and it is the one we expect a committee to press on, so we state it before
> they do.

**Why this survives an adversarial examiner.** It claims no priority, it states
what it does *not* claim, and it puts the weight on results that are reproducible
from a public corpus with public code.

**Two narrowings forced by work published while this thesis was being written.**
The first concerns the gate itself: a pre-generation gate with escalation is now
published prior art in enterprise (RCL, arXiv:2609.11023, a retrieval-confidence
layer between retrieval and generation that escalates or labels for human review
below a calibrated threshold), in regulated trade finance (HIRA, CIKM 2026,
arXiv:2608.21792), in evidence-grounded QA with runtime accept/refuse/regenerate
(CiteGuard-RAG, arXiv:2609.15830), and in nuclear engineering with provenance
tracking (RADIANT-LLM, arXiv:2604.22755). **We do not claim the gate.** The
second concerns the contribution sentence itself: between July and November 2026
the field produced at least five papers whose explicit object of study is what a
reliability mechanism costs and what it buys — a memory tier that costs +0.368 MiB
and buys nothing (arXiv:2610.07782), a confidence-gated cascade whose *matched
random-escalation control does as well* (arXiv:2610.20634), calibrated
retrieval-budget allocation reporting that gating is not universally faster
(arXiv:2606.29959), conformal factuality control reported jointly with claim
retention (arXiv:2609.38222), and a leakage-controlled, cost-aware evidence-gating
protocol (arXiv:2609.39075). **So "we measure reliability mechanisms" is no longer
a novelty claim; it is the house style of 2026 RAG evaluation, and we do not make
it.** What is not in that list is the joint cost–coverage–reliability frontier for
a confidence gate **on industrial text, at the level of the individual answer
claim, on a corpus regime that is not the procedural one every prior deployment
uses.** That is the claim, and it is narrower than the one this thesis began with.
We would rather defend the narrow claim than lose the wide one.

**The random-escalation control is now part of our own experiment, because the
literature says to run it.** arXiv:2610.20634 is the paper to read: it compares
a cheap non-generative verifier against a frontier LLM on the same 495
human-labelled claims, finds the two *statistically indistinguishable* on the
conventional metric while they disagree on 15.2% of claims and admit very
different rates of unsupported claims (23.2% against 14.1%), and then reports
that "a matched random-escalation control at in-sample thresholds, spending the
same budget by coin flip, does as well, so what buys the saving is the escalation
share and not the probability that picks what to escalate." Its conclusion —
"equal accuracy conceals unequal errors" — is exactly the trap this thesis's
own numbers could fall into. So Experiment 8 now includes a control arm that
refuses the same *number* of questions as the fitted gate and picks them at
random, and the difference between that arm and the fitted gate is what the
confidence score buys over refusing an arbitrary set of the same size.

### F.4.1 The novelty check, and what it changed

A check of the five findings against the published literature — every
identifier resolved against a live registry on 11 November 2026, and written
up in `research/13_novelty_and_positioning.md` — changed what this thesis
leads with. In short:

| Finding | Published? | What may be claimed |
|---|---|---|
| A conflict detector's precision decomposes into **detection** and **typing** | **No** — not published in this pairing | Two metrics instead of one; they are nine-fold apart; a branch with recall 0.000 where conflict provably exists; and a specification — a detector for regulatory text needs version metadata, or must be scoped to detection alone |
| The per-claim band measures **agreement with itself, not correctness** | The filter result is published; the decomposition is not | The band is ordered on the evidence it saw and indistinguishable on an independent reference |
| **Rubric vs reader specialisation** | The principle is published; the factor of nine is not | The specification of the task moved the measured precision of an unchanged detector by a factor of nine |
| **Point-in-time regulatory corpora** as a source of labelled conflicts | The *method* is published (NitiBench+, ICAIL 2026); the *purpose* is not | We applied a published corpus-construction method to conflict detection, and the detector that consumed it finds the conflicts and cannot type them |
| **BM25 beats a dense encoder** on regulatory text | **Already published**, three times, in three jurisdictions | Only the pipeline corollary: the lexical leg carried the pipeline and the fusion and the pre-filter added nothing on top of it |

Two consequences, and the committee will check both. **The BM25 result must
not appear in the abstract** — it is already known, and leading with it is the
one place this thesis would inflate its novelty. And **the spine is the
detection/typing decomposition**, with the failure-mode characterisation as
the second contribution and the rubric factorial as a methodological result
that belongs in an evaluation section rather than in a contribution list. The
full check, with every identifier resolved live, is in
`research/13_novelty_and_positioning.md`.

## F.5 The claims we must NOT make

- ❌ "BM25 beats dense retrieval on regulatory text." Already published, three
  times, in three jurisdictions (arXiv:2506.12895 on CJEU passages,
  arXiv:2412.07462 on statutory articles in Dutch and French, arXiv:2604.01733
  on financial text-and-table documents), with a counter-case at
  arXiv:2608.18752. Our claim is the *corollary* — the lexical leg carried
  this pipeline and the fusion and the pre-filter added nothing measurable on
  top of it — and the dense leg here is a general-purpose encoder that a
  domain-adapted one could overtake (arXiv:2506.12895, arXiv:2604.17778).
- ❌ "We are the first to decompose a conflict detector's precision." The
  taxonomy is published and the difficulty of typing a conflict is known; the
  *pairing* of detection precision and typing precision, reported as two
  numbers, is what is new.
- ❌ "Our gate reduces hallucination better than CRAG / Self-RAG / conformal
  abstention." No such comparison exists in the current evidence base.
- ❌ "We are the first to use a Bayesian posterior for retrieval confidence in
  RAG." Language-modeling IR established the Bayesian relevance model in 1999–2005
  (Song & Croft; Azzopardi et al.; Hiemstra et al.).
- ❌ "We are the first to abstain in RAG." SQuAD 2.0 (2018) defined the task.
- ❌ "Semantic entropy cannot be used at claim level." Confidence-weighted semantic
  entropy (Neurocomputing 2026) and semantic entropy probes (arXiv:2406.15927)
  make this untenable.
- ❌ "No public benchmark exists for industrial-engineering Q&A." **Partly false.**
  TeleEmbedBench (arXiv:2604.17778), a 5,144-pair Kubernetes benchmark, MiRAGE and
  ExpertQA all exist. The defensible version is narrow: *"no public benchmark spans
  multiple industrial-engineering sub-domains with dual expert annotation,
  reported κ, per-claim attribution labels, and an unanswerable class."*
- ❌ "Our hybrid retrieval outperforms flat retrieval." This is a well-established
  result (BEIR: BM25 0.413 → BM25+cross-encoder 0.473, +14.5%) and is **not** a
  contribution. Cite it as prior art and report our number as a replication.
- ❌ "SupplyChainQA is a public benchmark." It is our own unreleased construction;
  the report itself lists the Zenodo release as future work.
- ❌ "Our contradiction gate has no published equivalent." HALT-RAG
  (arXiv:2509.07475) publishes the calibrated abstention mechanism — an NLI
  ensemble with lexical signals under a precision-constrained policy — and
  Kontrast (arXiv:2607.25959) publishes the conflict taxonomy we implement.
  Narrow the claim to the *industrial instantiation with an NLI-independent
  numeric detector*, and to the measurement.
- ❌ "Our gate judges evidence sufficiency." It does not. The label is
  answer-in-context detectability, and the literature reserves "sufficiency"
  for the set-level property (SURE-RAG, arXiv:2605.03534; Certify,
  arXiv:2610.34684). Say "the gate detects whether the answer is in the
  retrieved context".
- ❌ "Our gate catches unanswerable questions." Report the rate at a stated
  operating point against the *never-refuse* and *always-refuse* policies. The
  endpoints of a threshold sweep are not baselines.
- ❌ "Our results transfer to industrial practice." The corpus is
  industrial-engineering *encyclopaedic* text. Beyond the Reranker
  (arXiv:2606.28367) reports that retrieval-enhancement gains come almost
  exclusively from homogeneous corpora, predominantly Wikipedia prose, which
  ours is. State the upper bound rather than the generalisation.
- ❌ "Our contradiction gate recalls 100% of verifiable conflicts." That number
  is true by construction: the verifiable subset is *defined* by numeric
  conflicts and the numeric detector is an OR-branch of the gate. Report what
  the NLI-and-same-subject conjunction catches on its own.

## F.6 The bibliography errors we found and fixed

Every one of the proposal's 18 references resolves to a real paper — there are **no
phantom citations**, which is unusually good. But several carry errors that a
citation checker or an examiner would catch:

| Reference | Error | Correction |
|---|---|---|
| [15] "Microsoft Research (2025), arXiv:2507.21502" | **Wrong author and wrong characterisation.** The authors are **Simchi-Levi, Mellou, Menache & Pathuri**; it is a Springer book chapter, and it is about applying LLMs as a conversational layer over optimisation-based supply-chain tools — not a fine-tuned procurement model. | Simchi-Levi, D., Mellou, K., Menache, I., & Pathuri, J. (2025). *Large Language Models for Supply Chain Decisions.* In *AI in Supply Chains*. Springer. arXiv:2507.21502. |
| [17] "An Application-Oriented Survey" | The title is "A **Capability-Oriented** Survey". | Li, Y., Fu, X., Verma, G., Buitelaar, P., & Liu, M. (2025). arXiv:2510.24476. |
| September report [5] CRAG | **The DOI and page range belong to a different paper.** DOI 10.18653/v1/2024.findings-acl.212, pp. 3563–3578 resolves to **Dhuliawala et al., "Chain-of-Verification Reduces Hallucination in Large Language Models."** CRAG is indexed as arXiv-only. | Cite CRAG as arXiv:2401.15884 and do not attach that DOI. |
| Cross-encoder model ID | `ms-marco-MiniLM-L-6-v2` is not the canonical Hugging Face ID. | `cross-encoder/ms-marco-MiniLM-L6-v2` |
| "MiniMax embed-01 (1024-d)" | No embedding model of that name appears in current MiniMax API documentation. | Use `BAAI/bge-m3` (1024-d). |
| [13] CRUD-RAG | Cited as an arXiv preprint. | Now published: *ACM TOIS*, DOI 10.1145/3701228. |
| [9] InstructRAG | Venue given as 2024. | ICLR 2025 (arXiv:2406.13629). |
| Unverified numbers | The literature table states "77.8% accuracy" (Wan et al.) and "92.4% Top-3 accuracy" (Wu et al.). The papers are real and the DOIs resolve, but **neither figure could be confirmed from the metadata**. | Do not repeat either figure until the full texts are checked. |

---

## F.7 What changed in 2026, and what it forces us to narrow

Three developments between the framework's specification and this writing bear
directly on our claims. This subsection exists so that nobody discovers them in
the room.

**The abstention mechanism has moved past a threshold.** GRAB-RAG
(arXiv:2608.22228) shows that under explicit abstention prompting, models still
answer 41.6% of *misleading* questions, with 63% of those answers echoing the
planted wrong entity; the paper's contribution is not that a threshold exists
but that a threshold is insufficient. SURE-RAG (arXiv:2605.03534) argues that
sufficiency is a *set-level* property that independent passage scoring cannot
detect, and Certify (arXiv:2610.34684) makes it structural, deriving a
Horn-closure certificate from a per-query requirement hypergraph. Sieve and
Sage (arXiv:2609.35794) screens the retrieved set in a lightweight module
*outside* the model before the model is invoked, with a two-state failure
decomposition — unanswerable versus distracted. AGO (arXiv:2610.01218)
quantifies regression risk probabilistically instead of thresholding.

**What this forces on us.** Our gate is a **calibrated answer-in-context
detector with a stated operating point**, not a sufficiency judge, and the
literature reserves "sufficiency" for the set-level property. Part E reports
the contingency table that makes the distinction concrete: how many answerable
questions had their evidence found, how many had it missed, and how many were
unanswerable. On the evaluation corpus the retriever's own recall of the gold
chunk is 100.0%, so retrieval failure accounts for 0.0% of the negative class — the negative
class is mostly genuinely unanswerable, and the gate does well. But the
mechanism is the reason to be careful: the gate's features are retrieval
scores, so its ceiling is set by the retriever, and on a corpus where the
retriever is weaker the same gate would face a negative class dominated by
retrieval failure that it cannot resolve. A reviewer who reads the code will
see that in five minutes.

**The closest single pre-emption of our contradiction mechanism is published.**
HALT-RAG (arXiv:2509.07475) is task-adaptable: an ensemble of NLI models
combined with lexical signals, fed to a calibrated meta-classifier, deployed
under a precision-constrained abstention policy. It is also, and this is the
part that matters for positioning, a **post-hoc verifier**: it operates on the
source text and the generated output "without performing retrieval itself",
so what it reports is the detector's coverage and its detector-level F1, not
a RAG system's behaviour. Its own Future Work says that "a critical next
step for this line of work is to integrate and evaluate detectors like
HALT-RAG within a live RAG pipeline to measure its resilience to noisy or
irrelevant retrieved context". That step is Experiment 8 in this thesis, and
it produces a finding the detector-level literature cannot: put the gate in
front of a live generator and its value depends entirely on whether the
generator declines on its own.
Kontrast (arXiv:2607.25959) separates direct conflicts from
information-granularity differences, temporal changes and incompleteness, which
is our supersession check formalised. WIKICOLLIDE (arXiv:2509.23233) reports
that at least 3.3% of English Wikipedia facts contradict another fact — which is
both a reason our corpus is a reasonable object of study and a benchmark we
should have used.

**What this forces on us.** Our remaining D4 claim is an *industrial
instantiation* in which the numeric detector is independent of the NLI verifier
and the supersession check is explicit, and that can only be defended against
human labels, which we do not have. We say so.

**Retrieval enhancements stop paying once a strong reranker is present.**
Beyond the Reranker (arXiv:2606.28367) evaluates eight enhancement methods on a
heterogeneous corpus with chunker-agnostic relevance labels and
collection-disjoint splits, and finds that only query expansion and one
calibrated method give reliable gains beyond a strong reranker. Its framing
sentence is aimed at work like ours: the reported gains "come almost entirely
from homogeneous corpora, predominantly Wikipedia prose." Ours is exactly such a
corpus. FreshStack (arXiv:2504.13128) independently reports rerankers that fail
to improve first-stage retrieval on two of five technical topics, and T²-RAGBench
(EACL 2026, arXiv:2506.12071) finds hybrid BM25 most effective on text-and-table
data.

**What this forces on us.** Our effect sizes should be read as an **upper
bound** on what the same mechanisms would deliver on mixed-format industrial
documents. It also means the candidate-pool curve (Experiment 5) is the part of
this work that is most likely to be new, and it is the part that was least
discussed until now.

Two further threats belong with these. The Labeling Problem in Hallucination
Detection Benchmarks (NeurIPS 2026 Evaluations and Datasets Track,
arXiv:2610.08026) shows, with 900 human-labelled pairs, that automated labelers
systematically conflate reference faithfulness with factual correctness — a
direct constraint on our silver-standard labels, and the reason the label
standard is stated in the abstract rather than buried. Entropy Alone is
Insufficient for Safe Selective Prediction in LLMs (arXiv:2603.21172) bears on
our information-gain component. And Detecting Is Not Resolving
(arXiv:2605.27157) reports across more than 50,000 turn-level evaluations that
models acknowledge contradictory evidence without constraining their
recommendations — the monitoring-control gap, and the reason we treat
contradiction *surfacing* as a reporting mechanism rather than a resolution
mechanism.

**The benchmark landscape has moved too.** Expert-annotated industrial and
supply-chain benchmarks now exist: the manufacturing-safety benchmark of
arXiv:2511.11847 (24 RAG configurations in a full-factorial design, top two
reviewed by ten industry experts and academics), arXiv:2606.20898 (972
expert-validated answers, comparing RAG against long-context prompting),
arXiv:2603.20534 (669 requirements across four MBN standards plus 49 supplier
qualifications, with expert quality assessment), RealDocBench
(arXiv:2606.07401, which includes supply-chain logistics), and SupChain-Bench
(10.18653/v1/2026.findings-acl.371, peer-reviewed at Findings of ACL 2026). Our
residual claim — that no public benchmark spans multiple industrial-engineering
sub-domains *with dual expert annotation, a reported κ, per-claim attribution
labels, and a deliberate unanswerable class* — has to be stated in exactly those
terms or not at all. Note also that all six of our categories are
industrial-engineering sub-domains, so our transfer experiment is an
**intra-domain** transfer study, and the proposal's wording should be read that
way.

## F.8 The benchmark landscape, and what our benchmark is not

A panel member will ask what our benchmark should have been compared against.
The 2026 landscape has expert-annotated industrial and supply-chain benchmarks,
so the honest answer names them.

| Benchmark | Size | Domain | Annotation | Identifier |
|---|---|---|---|---|
| Manufacturing-safety chatbot benchmark | Expert-validated QA over 3 machines; 24 RAG configurations, full-factorial; top 2 reviewed by 10 industry experts and academics | Machine / occupational safety | Expert validation | arXiv:2511.11847 |
| Token Tax of Epistemic Accuracy | 972 answers, 3 machines, 2 SLMs, 3 grounding architectures | Manufacturing safety | Expert-validated | arXiv:2606.20898 |
| Industrial-scale RAG for requirements engineering | 669 requirements across 4 MBN standards + 49 supplier qualifications | Automotive requirements engineering | Authentic industrial documents; expert quality assessment | arXiv:2603.20534 |
| RealDocBench | 1,356 field-level QA over 581 documents incl. supply-chain logistics | Regulated real-world documents | Typed gold dictionaries; human-verified layout annotation | arXiv:2606.07401 |
| SupChain-Bench | — | Supply chain management | Peer-reviewed benchmark | 10.18653/v1/2026.findings-acl.371 |
| IndusSpec-QA | 3 industrial standard documents | Industrial standards | Ground truth from the standards | 10.18653/2026.emnlp-main.1456 |
| LakeQuest | 9,846 QA pairs, 3 domains | Enterprise/scientific data lakes | Human-validated, with modality-aware evidence pointers | arXiv:2607.12310 |
| T²-RAGBench | 23,088 triples | Real-world text-and-table | Expert-validated at 91.3% context-independence | EACL 2026, arXiv:2506.12071 |
| WIKICOLLIDE / CLAIRE | "the first benchmark of real Wikipedia inconsistencies"; ≥3.3% of English Wikipedia facts contradict another fact | Wikipedia | Human annotation + editor study | arXiv:2509.23233 |
| ExpertQA | 2,177 questions from 484 participants | Long-tail expert domains | Expert-curated questions, expert-evaluated responses, per-claim attributions | 10.18653/v1/2024.naacl-long.167 |

**What our benchmark is not.** Ours is silver-standard: labels derived
mechanically from the document. That is cheap, perfectly reproducible, and
slightly optimistic about absolute recall. It is not expert-annotated, and the
NeurIPS 2026 Evaluations and Datasets Track paper on the labelling problem in
hallucination-detection benchmarks (arXiv:2610.08026) shows, with 900
human-labelled pairs, that automated labelers systematically conflate reference
faithfulness with factual correctness — a direct constraint on what a
silver standard can be used to claim.

**The defensible claim, in full.** *No public benchmark we could find provides
all four of the properties this evaluation needs together: coverage of multiple
industrial-engineering sub-domains, dual expert annotation with a reported κ,
per-claim attribution labels, and a deliberate class of unanswerable questions.
Each property exists in isolation, and several of them — expert annotation,
supply-chain coverage, an unanswerable class — now exist in public benchmarks
that we did not use.* That is the sentence to say. The broader version is
false, and a panel member with the literature in front of them will know it.

**Two corrections to our own earlier notes, found during this check.**
ExpertQA is not arXiv:2402.15049 — that identifier resolves to an astronomy
poster; its canonical identifier is the NAACL 2024 DOI
10.18653/v1/2024.naacl-long.167, and its *published* title is "ExpertQA:
Expert-Curated Questions and Attributed Answers", not the preprint title.
T²-RAGBench's title changed between versions: the arXiv preprint is "T2-RAGBench:
Text-and-Table Benchmark for Evaluating Retrieval-Augmented Generation" and the
EACL 2026 version of record is "T2-RAGBench: Text-and-Table Aware
Retrieval-Augmented Generation".

# Part G — Anticipated viva questions

Each answer is one you can actually defend, with the citation attached.

**Q0. Where did the data come from, and can I run it?**
The primary corpus of the original specification was 634 chunks across 24
proprietary supply-chain documents. It cannot be redistributed, so it cannot be
shipped with this work or re-run by a reader. Every measurement reported here
was taken on a **public substitute**: 46 industrial-engineering
articles from English Wikipedia (2,383 chunks, six
categories), fetched through the MediaWiki API and licensed CC BY-SA 4.0. It was
assembled to have the properties the framework needs — several industrial
categories, genuine tables and figures so the modality mechanisms have
something to act on, and citable provenance.

It ships in full, in `deliverables/dataset/`. For every document the manifest
gives its Wikipedia URL, the upstream revision it was read at, the SHA-256 of
the exact bytes used, and its chunk count. The corpus builder fails loudly
rather than silently dropping a document, and the build checks that no document
is indexed twice or spans two categories.

The thesis focuses on a **single industrial domain, supply chain management**
(14 documents, 735 chunks, 176 questions), because that is what the primary corpus
covered and where the practitioner scenarios come from. The other five
categories exist for the cross-category transfer experiment, which by
definition needs a subset of categories to transfer to held-out ones. Part E
traces real questions from the focus domain end to end.

The honest limitation: these are encyclopedia articles, not operating manuals,
standard operating procedures and supplier specifications. They are industrial
in subject matter, not operationally binding. The labels are silver-standard —
derived mechanically from the document rather than annotated by an expert — so
absolute recall is optimistic. The comparisons between systems are unaffected,
because every system is scored against identical labels.

**Q1. What is the one-sentence contribution?**
An evidence-grounded RAG framework for industrial decision support in which a
code-level, non-bypassable confidence gate, a modality quota, and per-claim
confidence tags are combined; the architectural contribution is modest and
deliberately so, and the substantive contribution is the empirical characterisation
of where each mechanism does and does not help — including three findings that
contradict the design as originally specified.

**Q2. Why is a *code-level* gate better than telling the model to be careful?**
Because an instruction is a request and a branch is a fact. The model cannot
override the gate; there is no output it can produce that reaches the gate. And the
refusal is auditable: "maximum calibrated relevance probability 0.31 against a
threshold 0.50" is checkable, "the model seemed unsure" is not. This is also why
we reject Self-RAG's learned reflection tokens: those are emitted by the model
being gated, and Huang et al. (ICLR 2024) show intrinsic self-correction degrades
without external feedback.

The word "code-level" is doing real work here, so it is worth being concrete
about where the guarantee comes from. The language model is **injected into the
framework**, not called by a harness: `Framework(index, generator=...)`, and the
framework calls it at exactly one line, inside `answer()`, *after* the gate has
accepted. There is no flag, no argument and no early-return path that reaches the
model without passing the gate first, and on a rejection the claim assessment and
contradiction detection are skipped too — a refused query costs no model call at
all. An invariant test asserts this (`impl/tests/test_invariants.py`, "the
generator is reached only through the gate"), and `impl/scripts/verify_gate_path.py`
demonstrates it on the real index by instrumenting the call itself. The only
paths that bypass the gate are the two comparison arms — the ablation arm with
the gate removed, and the whole-corpus long-context baseline — and both are named
for what they remove and reported as separate results.

What the gate does *not* do is judge the *form* of the question. See Q3e.

**Q3. How do you know your confidence probability is a probability?**
We fit a logistic calibration map by maximum likelihood on a held-out *query*
split and report the Brier score, the Expected Calibration Error, a reliability
table, and a risk–coverage curve. A raw cross-encoder score is a logit and is not
a probability; thresholding it directly is a category error.

**Q3a. Why is the calibration query-level rather than chunk-level?**
This is worth knowing because I got it wrong first, and the way I found out is
the point. My first implementation calibrated per *candidate*: "is this candidate
the gold chunk?" With about fifty candidates per query and one gold chunk, the
base rate of positives is about 2%. A classifier that answers "nothing is
relevant" is therefore right 98% of the time, and maximum-likelihood fitting
dutifully returned a large *negative* intercept (β₀ = −2.88) and a nearly flat
slope (β₁ = 0.27). The Brier score was 0.011 and the ECE was 0.004 — which
looked *excellent* — because they were measuring the base rate, not the filter.
The operating point it implied refused 46% of the answerable questions.

The gate does not decide "is this candidate the gold chunk". It decides "does
this context contain enough evidence to answer at all". Calibrating at the query
level removes the degenerate solution, because the base rate there is around a
third rather than 2%.

The general lesson, which is the same one the 2026 literature draws when it
warns that query-time filters can measure benchmark construction rather than
filtering: **the label you choose determines what you are measuring.** A
beautiful calibration number is not evidence that the thing is calibrated.

**Q3b. SYNCHECK beats abstention by over 10%. Why are you abstaining at all?**
This is the sharpest challenge to the work, and I would rather raise it myself.
SYNCHECK (Wu et al., EMNLP 2024) monitors decoding and reports that its FOD
decoding outperforms abstention, reranking and contrastive decoding by over 10%
on faithfulness, at 0.85 AUROC across six long-form RAG tasks.

Three answers. First, the two mechanisms detect different failures: SYNCHECK asks
whether a *generated sentence* is faithful to the context, while the gate asks
whether the context contains enough to answer *at all* — which has to be settled
before generation, because a sentence produced from inadequate evidence cannot
be repaired afterwards. Second, the gate runs before generation, so a refusal
costs one retrieval pass, not a generation plus a monitoring pass. Third, our
claim is not an AUROC against faithfulness detection but per-claim confidence
banding with a cited evidence trail for a practitioner — a different deliverable.

And the concession I make openly: our gate uses a small number of retrieval-side
signals, which is the *simplest* instantiation of the multi-signal design that
both SYNCHECK and Phillips et al. point towards. Combining retrieval confidence,
query–chunk overlap, chunk position and cross-encoder confidence is the natural
next step, and our five-feature calibrator is a first cut at it.

**Q3c. Your gate is calibrated on a label that is really "did the retriever
find the answer". Isn't that a retrieval-success detector, not a sufficiency
judge?**
Yes, and I now say so explicitly rather than defending the old name. The label
is 1 iff the gold chunk is in the reranked candidate pool. The literature
reserves "sufficiency" for a set-level property — that scoring passages
independently cannot detect sufficiency, which is the argument of SURE-RAG
(arXiv:2605.03534) and Certify (arXiv:2610.34684) — so calling my label
"sufficiency" reads as a claim of prior art I do not have. The honest name is
**answer-in-context detectability**.

The consequence is the important part, and it is a limitation rather than a
rhetorical point. The negative class of the label holds two different kinds of
query: answerable questions whose evidence the retriever missed, and questions
that are genuinely unanswerable. Part E reports the three-way decomposition, so
you can see exactly how much of the negative class is retrieval failure — on
the evaluation corpus 0.0%, with the
retriever's own recall of the gold chunk at 100.0%.

The honest statement of the limitation is this. The gate's features are
retrieval scores, so its ability to separate "the answer is in the context"
from "it is not" is bounded by how well those scores carry that information,
and the composition of the negative class moves with the retriever. Here the
retriever is strong enough that the negative class is mostly what the gate is
meant to detect, and it does well. On a corpus where the retriever is weaker,
the same gate would face a negative class dominated by retrieval failure that
it cannot resolve, because the scores it uses are exactly the scores that
failed. That is why the operating point is a fitted, per-corpus parameter, and
why I present the gate as a selective-prediction policy with a risk–coverage
curve rather than as a detector. It is also the field's known result for
model- and prompt-based abstention: GRAB-RAG (arXiv:2608.22228) finds models
still answer 41.6% of misleading questions under explicit abstention
prompting.

**Q3d. What has changed in the literature since you designed this, and does it
change what you are claiming?**
Three things, and yes, they narrowed the claims. First, the abstention
mechanism has moved past a threshold: GRAB-RAG, SURE-RAG, Certify and Sieve and
Sage all argue that a threshold is insufficient, and I have stopped calling my
gate a sufficiency judge for the reason in Q3c. Second, HALT-RAG
(arXiv:2509.07475) publishes the calibrated abstention mechanism — a NLI
ensemble with lexical signals under a precision-constrained abstention policy
— although as a post-hoc verifier it never retrieves, and its own Future Work
names live-pipeline evaluation as the critical next step. So I no longer claim
the contradiction gate is new, and I no longer claim the abstention mechanism
is new either; I claim it is a carefully instantiated one whose numeric
detector is independent of the NLI verifier, and that what the detector is
worth inside a live pipeline had not been measured.
Third, Beyond the Reranker (arXiv:2606.28367) reports that retrieval
enhancements stop paying once a strong reranker is present, and that the
reported gains come almost exclusively from homogeneous corpora, predominantly
Wikipedia prose. Mine is exactly such a corpus, so I report my effect sizes as
an upper bound for mixed-format industrial documents. What survives unchanged is
the measurement work: the candidate-pool curve, the quota's position-versus-cost
trade, and the three-way decomposition of the gate's own label.

**Q3e. What happens if the user types a nonsense question?**
Two different things can be wrong with a question, and the framework now handles
them at two different points.

*Is it a question at all?* A **runtime form check** (`src/query_form.py`) runs
before retrieval. It refuses four things: an empty query; a query with no words
in it; a query whose every word is a function word or a deictic ("what is
this?"); and a query that ends on a word that cannot end a question ("what are
units that?", "what is the cost of?"). Because it runs first, a request it
refuses costs no embedding pass, no cross-encoder pass and no model call at
all.

*Is there evidence for it?* That is the confidence gate's job, and the gate
does it to the extent the evidence allows: it refuses 23.6% of the hard genuinely-unanswerable questions
(26 of 110) — questions the corpus discusses but states no value
for — and 76.5% of the out-of-domain ones
(26 of 34), the two reported separately because they are not
the same test (§E.9). But the gate is an **evidence** gate, and it never asks
whether the query was a question. I measured that too: on the 30 malformed stems the benchmark's own generator produced and
rejected, on the six-category corpus, the gate **accepted 23 of them
(76.7%)**, at a mean posterior of 0.323
against an operating point of 0.05. So the gate is good at "is there
evidence here?" and no use at all at "is this even a question?" — which is
exactly why the two checks are separate components and not one.

The form check is measured, and the two rates are always reported together,
because the second one is the one that matters: a false rejection is a refusal
of a question the corpus could have answered, which is the one failure this
framework is built to avoid.

| population | refused |
|---|---|
| hand-authored malformed queries | 25 of 25 |
| hand-authored well-formed queries | 0 of 35 |
| corpus stems the generator rejected, hand-labelled malformed, on the focus domain | 6 of 16 (37.5%) |
| the same stems, hand-labelled well-formed | 0 of 13 |
| the benchmark's own queries, all well formed | 3 of 176 |

The counterfactual is what decided the design, and it is measured rather than
assumed. The obvious implementation is to reuse the benchmark builder's existing
`_subject_is_usable` filter, which already rejects malformed question subjects
— and it cannot be reused. That filter is a rule about *question generation*,
not about form: it rejects a subject for being one word ("FMEA"), for
containing a hyphen ("root-cause analysis"), or for ending in "-ing" ("pick and
pack warehousing"). Applied to the same well-formed stems it would have
refused **13 of 13**
(100.0%) — "What is reliability engineering?", "What is
logistics?", "What is FMEA?". On the six-category corpus the same counterfactual
refused 37 of 37. So the runtime check was written against the
query as the user typed it, and the tempting shortcut was measured first and
rejected on the numbers.

Two limits, stated because they are real. The check catches 37.5% of the malformed stems, not all of them: the rest are
truncated *clauses*, whose malformation is grammatical rather than lexical, and
catching those needs a parser or a language model — every rule that wide risks
refusing valid questions. And the check has no dictionary and no language model,
so a keyboard mash passes it; the test fixture records two such cases as
expected misses, and the check deliberately fails open on them. The honest
boundary is stated as L15 in Part H.

**Q4. Why not conformal prediction? It has actual guarantees.**
Because those guarantees require exchangeability between the calibration and test
sets, and Geißler et al. (2026) show the assumption depends on the retriever setup.
On a single-category industrial corpus of 634 chunks it does not hold. We adopt
their diagnostics as our limitation and claim only empirical calibration.

**Q5. Your dense retriever was worse than BM25. Why is that not fatal?**
Because it was a finding, not a defect — and because the framework is
instrumented well enough to act on it. `sentence-transformers/all-MiniLM-L6-v2` is a general-purpose
sentence encoder, not a retrieval-trained model, and the retrieval objective is
asymmetric in a way the sentence-similarity objective is not. The BEIR benchmark
reports the same effect — DPR zero-shot at 0.234 versus BM25 at 0.413.

The part worth saying plainly: the first version of this thesis *measured*
that and then kept the weak encoder. The ablation exists to tell you which
leg is carrying the load, so the correct response was to replace it, not to
report around it. The dense leg is now `BAAI/bge-m3`, and §C.3 reports
what that changed: The gap between the dense leg and the lexical leg closed by more than half; and the fused system now **orders better** than the lexical leg alone, which it did not before. The general lesson is the one the
framework teaches: fusion takes the *union* of two shortlists, so a weak leg
does not fail loudly — it just spends the other leg's slots. Measure the legs
separately, and do not assume a hybrid is an upgrade.

**Q6. Your reranker made recall worse. Why keep it?**
With the candidate pool it originally had, that was true — and finding out why
was the most valuable single result of the project. The reranker's effect on
recall is governed by the size of its candidate pool relative to the final
context. With a top-10 pool it cannot bring in a relevant chunk sitting at fused
rank 34, and it can only lose the one sitting at rank 12: recall@20 fell 1.000 → 1.000. With a top-50 pool the same reranker raises recall@10 from 1.000 to 0.969 (p = 3.2 × 10⁻¹) and MRR from 0.798 to 0.795.

That reframes the −5.34 pp reranker regression reported in the September 2026
report: it is not a mystery, it is a pool-size question — and the check is
cheap. I would want to run that measurement on the original code before
claiming it, which is why I present it as a hypothesis with a test rather than
as an explanation.

**Q7. The modality quota made things worse. Is D2 a failure?**
It depends on *where* it is applied, and that is the finding rather than an
excuse. On the focus domain, table recall is already at ceiling — 1.000 at
every rung, because the lexical retriever finds the table chunks on its own — so
the quota has no table gain left to buy there. Applied *before* the cross-encoder
it still moves overall recall by +0.031, because it decides which
ten the cross-encoder ranks instead of displacing one of the ten it has already
ranked; applied *after*, it costs -0.031, because it then has to
import a chunk the cross-encoder already put below the cut. On the six-category
corpus the quota has a table gain to buy — the reranker takes table recall from 0.964 down to 0.929, and the pre-rerank quota puts it back to 1.000.

Two things make that predictable rather than surprising. The corpus modality
composition is measured and reported *before* the result — this corpus is 88.8% prose — and the composition is what predicts whether the
mechanism can have any effect. And the framework's actual contribution here is
the finding that **the quota's position decides what it costs** — and that the
answer is the opposite of what the framework was designed on. Applied *before*
the cross-encoder the quota reaches table recall 1.000 and moves overall
recall by +0.031; applied *after* it, overall recall moves by
-0.031 instead, at a table recall of 1.000. The general rule,
corrected: a constraint on a downstream artefact should be enforced where it can
still choose the candidates, not where it must work against another component's
judgement.

**Q8. How do you know the contradiction detector is not just firing on everything?**
We report the prevalence, the false-positive rate *at a stated operating point*,
precision and recall, and — critically — the always-flag and never-flag baselines.
A detector that flags everything has 100% recall and 0% precision. We also
suppress revision supersession, because "Rev 3 says 187 units" and "Rev 4 says 95
units" are both true.

**Q9. Your confidence tags — how can they be wrong if they are computed, not
predicted?**
Because the tags summarise what the *retrieved context* supports, not what is true
in the world. A claim can be faithfully supported by a passage that is itself
stale. That is why every tag carries a citation, why the contradiction mechanism
partially covers staleness, and why the report lists "confidently wrong" as an
explicit limitation rather than a solved problem.

**Q10. What is the weakest part of the work?**
The empirical scale. 634 chunks, 24 documents, a 30-query calibration set, a
16-participant user study and one focus category are all below the scale at which
the statistical framing we use is well-founded. The claims are therefore framed as
*demonstration and mechanism*, not *generalisation*. And the 2026 literature is
explicit that a better retriever reduces abstention, so our threshold must be
re-fitted per retrieval configuration — which we now do and report.

**Q11. Why not just put the whole corpus in the prompt?**
That is the strongest competing approach and we take it seriously. Our corpus does
fit in a modern context window, and 2026 work reports long-context systems beating
semantic RAG in manufacturing safety at 26× the token cost. **We measured the cost
half of the comparison**: on the focus domain the corpus is 202,529
tokens against the RAG arm's 2,246. The long-context arm sends 74x more input tokens per query than the pipeline, which at the provider's cached-prefix pricing, with the corpus prefix served as a cache read on 33.0% of the long-context arm's input tokens is a 58.8x input-cost ratio rather than 74x: the token ratio and the cost ratio are different numbers, and only the second one is a cost. On the
six-category corpus the corpus exceeds the 128K window most hosted models offer but fits the 1M-token window of the generator used here. A retrieval-side proxy shows the evidence stays at the
top of the whole-corpus ranking (0.969 in the top 10 of 735), so the long-context arm's advantage would have to come
from the reader, not from the retrieval. The answer-quality half of the comparison was measured on the focus domain. With the whole corpus in the prompt the generator answered 31 of 32 answerable questions, the same coverage as the pipeline, and it declined the unanswerable questions at a comparable rate (76 of 144 against 77 of 144), for 74 times the input actually sent per query. On coverage and on cost the result is settled: the whole-corpus prompt declines no more unanswerable questions than the pipeline does and costs 74 times as much to do it. On answer quality the margin is directional but not statistically significant once the answers are scored without the length confound. The evidence
trail, the per-claim auditability and the category routing are properties our
system has.

**Q12. What would you do next, in priority order?**
(1) Repeat the generator-side comparison with a second generator, under both
prompt conditions — the cautious condition found the gate's refusals
redundant with the prompt's, and the answering condition is where it held, so
both findings currently rest on one model. (2) Repeat the long-context arm's
answer-quality comparison on the
six-category corpus, where it has not been made and where it is now feasible:
that corpus fits the 1M-token window of the generator used here. (3) Repeat the encoder swap with a second retrieval-trained
encoder and
re-measure the fusion gain. (4) Replace the LLM-annotated benchmark with
dual-expert annotation plus an LLM meta-evaluation, and report κ with a CI.
(5) Stratify the corpus by modality so D2 can be tested with adequate power, and
pre-register the power analysis. (6) Re-fit the gate threshold for every retrieval
arm, as DeclineCraft requires.

**Q13. Why did you not use a knowledge graph?**
GraphRAG and its descendants are stronger for query-focused summarisation over a
whole corpus, and they are significantly more expensive to build and maintain. For
industrial decision support the retrieval unit is a *specification fragment* — a
table row, a clause — and the thing that must be traceable is a passage, not a
subgraph. A category-level partition is coarser than community detection but is
also auditable and cheap, and it maps to how industrial documentation is actually
filed.

---

# Part H — Limitations, and the honest boundary of the claims

State these before anyone asks. A report that volunteers its limitations is
believed on the claims it does make.

| # | Limitation | Consequence for the claims | What would fix it |
|---|---|---|---|
| **L1** | The evaluation is single-domain by design — supply chain management is the focus — with the other five industrial-engineering categories retained for the cross-category transfer experiment | Generalisation beyond supply chain is **demonstrated mechanistically** and by that transfer experiment, not empirically at production scale | A licensed, multi-domain industrial corpus with the same provenance discipline |
| **L2** | Small corpus (634 chunks, 24 documents) | Results may not transfer to production-scale corpora | A larger, licensed industrial corpus |
| **L2b** | The measurements were taken on a **public substitute** corpus, because the primary corpus is proprietary and cannot be redistributed | The corpus is industrial in subject matter but not operationally binding: encyclopedia articles, not the operating manuals and standard operating procedures of a real plant. The labels are silver-standard, so absolute recall is optimistic | A licensed, expert-annotated industrial corpus with the same provenance discipline; the pipeline is corpus-agnostic and re-runs unchanged |
| **L3** | Modality composition too sparse for the quota to have power (2.3% chart, 7.1% table in the primary corpus; 5.2%/6.0% in ours) | The modality-boost null is **expected**, and is reported as such | Stratified corpus + pre-registered power analysis |
| **L4** | Cross-encoder reranking regresses on some sub-categories (−5.34 pp on `production_scheduling`) | The reranker's benefit is category-dependent | Fine-tuning the reranker on domain-matched data |
| **L5** | Contradiction detection's published ceiling on technical text is low (SciNLI 78.18% Macro-F1) | The false-positive rate is high and the reported 98% → 16% figure needs base-rate accounting | Validate the NLI leg on the industrial corpus; add the revision check |
| **L6** | User study N = 16 | Supports a within-subject sign test (≈14/16 → p ≈ 0.002) but **not** a claim about generalisation | A second industry cohort; ≥ 30 participants |
| **L7** | The benchmark is LLM-annotated (500 questions proposed) | LLM-as-judge bias (position bias flipped 66 of 80 queries in one study) may inflate scores | Dual expert annotation on a subset with κ ≥ 0.7, plus a judge meta-evaluation |
| **L8** | No LLM in the shipped pipeline's answer path | The generation-side metrics (faithfulness, citation precision) are measured against a generator-free extractive baseline | Wire in the production LLM and re-measure |
| **L9** | Long-context baseline measured on cost, and on quality for the focus domain | The long-context arm sends 74x more input tokens per query than the pipeline, which at the provider's cached-prefix pricing, with the corpus prefix served as a cache read on 33.0% of the long-context arm's input tokens is a 58.8x input-cost ratio rather than 74x: the token ratio and the cost ratio are different numbers, and only the second one is a cost. The six-category corpus exceeds the 128K window most hosted models offer but fits the 1M-token window of the generator used here, so the answer-quality half is on the focus domain because that is this thesis's domain and the two corpora are never pooled; the comparison is measured, and on this corpus it does not support a superiority claim for long-context prompting in this domain | Repeat the answer-quality comparison on the six-category corpus, which is now feasible and is the obvious next measurement |
| **L10** | Calibration is fitted per retriever, not universally — and it has to be. Measured rather than asserted: the gate was fitted separately on three retrievers and the thresholds differ — 0.05 on the shipped hybrid, 0.10 on the lexical leg alone, 0.05 on the dense leg alone — and the operating points differ with them. The hybrid's gate answers 0.938 of the answerable questions and refuses 0.361 of the unanswerable ones; the lexical gate 0.906 and 0.611; the dense gate 0.812 and 0.660. The frontier is now reported as a curve — 19 thresholds per retriever, each with its answer rate, refusal rate, abstention precision and coverage, plus the risk–coverage curve — rather than as one chosen point | A threshold fitted on one configuration is too permissive where it is transferred, and it is too permissive in the direction that flatters the configuration it is transferred to: the shipped threshold applied unchanged to the lexical leg answers 0.969 of the answerable questions against 0.906 when it is refitted, and refuses 0.340 of the unanswerable ones against 0.611. On the dense leg the two fitted thresholds coincide and the transfer costs nothing, which is the qualification — it is wrong where the thresholds differ and harmless where they do not, so no single global threshold can be justified. This is the practical form of DeclineCraft's finding that better retrieval changes the right abstention threshold | A calibration that would transfer across retrievers, which would need a retriever-independent feature rather than a calibrated score. The answer for now is the one the framework already gives: the calibration is fitted again for every retrieval stack, and the frontier is reported again with it. See `research/19_gate_per_retriever.md` |
| **L11** | The gate's label is **answer-in-context detectability**, not evidence sufficiency: the positive class is "the gold chunk is in the reranked candidate pool", and the negative class is dominated by *retrieval failure* rather than by absence of evidence | The gate cannot distinguish "there is no evidence here" from "the evidence is here and the retriever missed it", because the retrieval scores it uses are exactly the scores that failed. The literature reserves "sufficiency" for the set-level property (SURE-RAG, Certify) | A label that separates absent evidence from missed evidence — e.g. an answerability annotation on the context, independent of the retrieval scores |
| **L12** | The contradiction gate **cannot be evaluated on this corpus**, and its precision, measured against reader labels rather than against a proxy, is **0.0%** (20 labelled alarms, 95% upper bound 16.1%): two annotators that do not share a model, both blind to the detector's own scores and both 14 of 14 on a control set whose labels are known in advance, agree on the contradiction decision for 101 of the 101 pairs they labelled -- and the same readers find 0 contradictions in 80 random pairs the gate did **not** flag. The detector's own positive control is 11 of 11, so the mechanism works and this corpus does not test it; the fitted calibration therefore leaves **20 findings surfaced and 0 withheld** here |  The annotators are models rather than people, so the number says the alarms are not confirmed by a reader, not that no reader would ever confirm one | A human annotation round over the same sheet -- the instrument is built and shipped: `impl/experiments/label_contradiction_pairs.py` samples the alarms and a simple random sample of the unflagged pairs, writes a labelling sheet with the rubric attached (`impl/experiments/data/contradiction_label_rubric.md`), and scores a filled sheet into a precision and a recall with 95% intervals -- and a corpus that contains contradictions to find, which means revised procedures rather than articles about concepts, on which the conflict calibration can be re-fitted |
| **L13** | The cross-category transfer experiment is an **intra-domain** study: all six categories are industrial-engineering sub-domains, so it tests transfer between sub-domains of one domain, not between domains | The proposal's wording ("across diverse industrial sub-domains") should be read as intra-domain transfer; no claim is made about transfer to a different industry | A corpus spanning genuinely different industries, with the same protocol |
| **L14** | The framework's own hypothesis **H2.1** — that a code-level, non-bypassable gate reduces hallucination — is **supported under both prompt conditions** | The generator-side comparison was run under two prompt conditions, and the hypothesis is supported under both prompt conditions. The claim is established for one generator: the replication on a second generator could not be run, because MiniMax-M3.1-Flash returned no text on 24 of the 66 questions it was asked -- 23 of them on the benchmark's table-lookup family, against 1 of 22 on a control sample of the other families -- and 13 were rescued by a larger output budget. An empty completion is neither an answer nor a refusal, so the harness records the run as not-run instead of quoting a rate it cannot stand behind. And a refusal rate and a hallucination rate computed on generated text are different quantities, so neither is presented as the other. | Repeat the generator-side comparison with a second generator, and on the six-category corpus |
| **L16** | The benchmark's answer labels are silver-standard and mechanically derived, and an audit of the label generator found a defect in it: **27 of the 132** answerable questions carried an answer label attached to the wrong question (20.5%) -- a table question that names the column its key came from rather than the column its answer came from, and a numeric gold that is a digit prefix of a longer token in the chunk. The generator was corrected, the benchmark rebuilt and every experiment re-measured against it; the audit now finds **0** remaining defects out of 32 | The gold *chunk* was correct in every defective case, so the retrieval-side measurements were never affected and the answer-side accuracy was depressed equally for every arm; but the audit encodes two rules rather than checking every label by hand, so a defect class it does not encode would not be found, and the repair changed the answerable set, so only the post-repair numbers are comparable with one another. Separately, the long-context quality margin reaches no test's significance threshold -- not under the whole-answer entailment test, not under a length-controlled re-scoring, and not under a lexical test that ignores length -- so that comparison is directional rather than significant | Hand-check every answerable label against its gold chunk, and report the agreement rate |
| **L17** | The benchmark's **unanswerable class was separable from the question text alone** -- and the defect was found by auditing it and then repaired. A classifier that sees only the question's *shape* -- its stem, its subject size, whether the subject contains a digit, an acronym or a fabricated identifier -- tells the answerable questions from the unanswerable ones with an ROC AUC of 0.608 against a permutation null of 0.468 that the same procedure produces on shuffled labels (p = 0.050), against 0.999 before the unanswerable class was rebuilt; on the better-powered six-category benchmark, whose answerable class is four times larger, the same measurement gives 0.533 against a permutation null of 0.500 (p = 0.267) The defect was in the half's designated hard case, which asked about a fabricated identifier (`SKU AST-5454`): an identifier shape that no answerable question carried, so a single regular expression separated the classes perfectly, catching 76.4% of the class with no false positives at all. The half was rebuilt as a **corpus-anchored** class -- the same question stems, the same source documents, the same label machinery, and each repaired question given a structural twin in the answerable class (106 of 110 have one) -- and every measurement was taken again | Before the repair the headline refusal rate was an **upper bound**, measured on questions identifiable without reading the evidence. After it, the rate is measured on questions whose unanswerability is decidable only from the evidence, and the corpus-anchored stratum -- the case the gate is being tested on -- is reported separately from the trivially-unanswerable out-of-domain stratum. What remains: the repaired class is a **near-miss class**, and that is a property of a mechanically labelled benchmark rather than a defect of the repair. Its questions are ones the corpus discusses without stating the answer in the form the label standard recognises; an independent re-check found 43 of 110 whose subject the corpus comments on without defining it, so a reader could sometimes construct an answer, and 1 of 110 whose certificate does not hold at all. The refusal rate is therefore measured on a class that is partly answerable in a human's sense, which bounds what the absolute number means -- and it does not bound the arm comparison, because every arm is asked the same questions. The residual form-only separability of the repaired class is 0.608 against a permutation null of 0.468 (p = 0.050) on the focus domain, and 0.533 against a permutation null of 0.500 (p = 0.267) on the better-powered six-category benchmark. It is a small residual that the focus-domain run reaches and the better-powered run does not reproduce: small, but not zero. | Hand-check the repaired class's labels against the corpus, and repeat the audit on a second corpus whose construction differs. The audit is `impl/experiments/audit_unanswerable_class.py`, the generator is `impl/scripts/unanswerable_repair.py`, and the benchmark as it stood before the repair is preserved beside the repaired one so that the finding stays checkable |
| **L18** | **The answer-accuracy column is a property of the scoring convention as much as of the system.** The two shipped tests disagree about which arm is best, and the order reverses between the two prompt conditions. Re-scored on the *same* shipped answers under five conventions -- the two shipped ones, plus SQuAD 2.0's normalised exact match and token-level F1 and PopQA's containment rule -- the two shipped tests give opposite verdicts on between 19% and 67% of the answered questions, with Cohen's κ from 0.00 to 0.21, and the four binary conventions span up to 0.90 on one arm's answers | The accuracy column therefore cannot support a claim that the gate makes answers more accurate, and it is reported as a comparison between arms rather than as a level to be quoted. What the measurement settles is that no arm comparison on the answer side reaches significance under more than one convention: the gate-against-no-gate comparison reaches 0 of 5 in the cautious condition and 0 of 5 in the answering one. Everything the gate is actually claimed on -- the coverage, the cost, the refusal of questions it should refuse, the claim-support figures and every retrieval measurement -- is computed from counts and from the evidence rather than from the answer string, and is identical under all five conventions. See §E.8.1 and `research/18_answer_validation_conventions.md` | An LLM judge on semantic equivalence -- BrowseComp's rule, and the fifth convention in the literature -- which was not applied here; and human annotation of the benchmark's own gold answers, which is what would make one convention right rather than merely five conventions measured. No comparable benchmark reports a containment test's false-positive rate either |
| **L15** | The runtime form check is a **second** gate, not a replacement for the first. The confidence gate remains an **evidence** gate — on the 30 malformed stems the benchmark's generator produced, on the six-category corpus, the gate itself accepted 23 (76.7%) at the fitted operating point of 0.05 — while the form check, which runs before retrieval, on the focus domain refused 6 of the 16 hand-labelled malformed stems (37.5%), and refused 0 of the 13 hand-labelled well-formed ones and 3 of the 176 benchmark queries | The remaining malformed stems are truncated *clauses* — their malformation is grammatical rather than lexical — and the check has no dictionary and no language model, so a keyboard mash passes it (two such cases are recorded in the test fixture as expected misses). A request that is a broken clause rather than a broken phrase still reaches retrieval and is answered from whatever the corpus happens to contain about it | A parser or a language model for the form decision, with its own false-rejection rate measured on the same populations. The counterfactual that ruled out reusing the benchmark's own filter is measured too: it would have refused 13 of 13 well-formed stems (100.0%) |
| **L19** | **The proposal promised twelve categories and this thesis builds six of them.** The twelve-category, three-domain industrial benchmark was not built: six of the nine industrial-engineering categories were reduced to six, the three machine-learning categories -- demand forecasting, time-series forecasting and anomaly detection -- were descoped as numerical series-reasoning problems rather than document-retrieval problems, and three industrial categories -- transportation & logistics, reverse logistics and inventory management -- were descoped because the binding artefacts the proposal names are proprietary and not redistributable. The full reconciliation, with the proposal's own wording and the reason for each row, is in §A.6 and `research/12_scope_reconciliation.md` | Every claim in this thesis is about the corpora it was measured on -- a public six-category industrial corpus, its supply-chain focus subset, and an authentic federal regulatory corpus -- and none of them is about the twelve-category benchmark the proposal described. The descopings are of three kinds and are not equally excusable: three are engineering facts about what could be obtained and redistributed, three are a judgement that a category is a different problem class from the one this thesis measures, and one -- the absence of human-expert validation of the benchmark's labels -- is a cost the thesis pays knowingly and reports in this table | The extension into the machine-learning categories is the honest next measurement, and it belongs in the next-steps list rather than in the days before the defence: it needs a series corpus, series-appropriate metrics (MASE, forecast-interval coverage) and a new benchmark, and it would measure a different system from the one this thesis builds. The three proprietary industrial categories cannot exist here at all without a licensed corpus |
| **L20** | **The shipped quota placement was changed on 16 November 2026, and the ablation's ranking of the two placements is not the same on every corpus.** The system now applies the quota *before* the cross-encoder; it shipped the other placement until then, because that was the September 2026 design and moving it invalidates the gate's calibration, the generator-side comparison and the per-claim results together. The ablation's own comparison of the two placements is: on the focus domain the before-the-reranker placement reaches 1.000 Recall@10 against 0.938 after it (p = 0.157); on the six-category corpus the before-the-reranker placement reaches 0.939 Recall@10 against 0.924 after it (p = 0.480); on the industrial corpus the order reverses, the after-the-reranker placement reaching 0.988 Recall@10 against 0.980 before it (p = 0.317). **None of these differences is statistically significant at the 0.05 level (p = 0.157, 0.480, 0.317 respectively).** | The placement's effect is small everywhere and its direction is not uniform, so the shipped default is the focus domain's preference -- the largest of the differences -- rather than a rule the evidence settles. The ablation's own numbers did not move: it measures the two placements as a variable, so re-running it reproduced every rung exactly, on both Wikipedia corpora. What did move is everything that runs through the shipped retrieval -- the gate's calibration above all. 23 of the 26 measurements the deliverables quote that depend on the retrieval were re-measured with the new placement, while the per-claim band evaluation against the gold evidence, the per-claim band evaluation against the retrieved evidence and the industrial corpus's per-claim band replication were taken under the earlier placement and are the measurements this limitation covers. | Re-measure the placement on any corpus it is moved for, in the same pass as everything that depends on it |

**The three sentences that should be in the report verbatim.**

> The contributions of this work are of three kinds, and they differ in strength.
> The architectural contribution — a code-level confidence gate, a modality quota,
> hybrid retrieval with a category pre-filter, contradiction surfacing and per-claim
> tagging — is **incremental**: each component has published prior art, and we
> position ours against it explicitly rather than claiming priority. The empirical
> contribution is a **failure-mode characterisation**: on an independent corpus we
> reproduce the reranker regression, we identify the pipeline position at which a
> modality quota actually binds, and we show that the modality composition of the
> corpus, rather than the retrieval algorithm, determines whether a
> modality-aware mechanism can have any effect. The methodological contribution is
> an **evaluation protocol** — a gate evaluated as a selective-prediction policy
> with a risk–coverage curve and a false-positive rate at a stated operating
> point, with always-flag and never-flag baselines — which recent work shows is
> the minimum needed for a filter result to mean anything.

---

# Part I — The report and the paper, and how they differ

You will be asked about both. They are the same body of research presented for two
different audiences, and confusing them is a bad look.

| | **Department report** (Deliverable 3) | **Polished paper** (Deliverable 2) |
|---|---|---|
| **Audience** | The MTP review panel: Dr. Kumar, the department | A conference or journal reader who does not know you |
| **Length** | ~20–25 pages | ~9 pages IEEE / ~17 pages journal / ~20 pages technical report |
| **Front matter** | IIT Kharagpur title page with logo, certificate, table of contents, page numbers, the house border | Abstract, keywords, IEEE-style or journal-style front matter, no certificate |
| **Structure** | Numbered chapters matching the September 2026 report's table of contents, so the panel can compare directly | IMRaD, compressed, with related work as a separate section |
| **Results** | Full tables, including the null results and the limitations | The headline tables; nulls reported, not hidden |
| **Tone** | Instructional — explains the framework so the panel can assess the work | Argumentative — states a claim and defends it |
| **What it adds** | The full derivation of every formula, the code walkthrough, and the viva Q&A | The novelty statement, the literature positioning, and the reproducibility statement |

**The three formats of Deliverable 2** are the same paper reformatted:

- **Single-column technical report** — the "safe" format. Readable in any
  reviewer, no template risk, and the closest to what a thesis chapter needs.
- **IEEE two-column conference** — the standard for an ISE conference
  submission. Tight: the related work compresses, the derivations move to an
  appendix, and the space goes to the results and the novelty statement.
- **Journal (Elsevier/Scopus) style** — a structured abstract with explicit
  sections, heavier on the contribution statement and the comparison against the
  2025–2026 literature, with a formal reproducibility statement.

**Everything that is asserted in the paper is asserted in the report**, and every
number appears in both. There is one set of results.

---

# Part J — One-page glossary

Revise from this the night before.

| Term | One line |
|---|---|
| **Token** | The unit an LLM reads; usually a word-piece. |
| **Embedding** | A 1024-number vector encoding a text's meaning. |
| **Cosine similarity** | The angle between two embeddings; 1 = same direction. |
| **BM25** | Lexical ranking: IDF × saturated term frequency × length normalisation. |
| **IDF** | Log-likelihood ratio of a term appearing in a relevant vs irrelevant document. |
| **Saturation** | The tenth occurrence of a term counts far less than the first. |
| **Bi-encoder** | Encodes query and document separately; enables ANN search. |
| **Cross-encoder** | Reads query and document together; more accurate, more expensive. |
| **HNSW** | Graph-based approximate nearest-neighbour index. |
| **pgvector** | Postgres extension for vector storage and ANN search. |
| **RRF** | Rank fusion: Σ 1/(k + rank); scale-free, k = 60. |
| **Recall@k** | Fraction of the truly relevant documents found in the top k. |
| **MRR** | Mean of 1/rank of the first relevant document. |
| **nDCG@k** | Rank-and-grade metric normalised by the ideal ranking. |
| **Posterior** | P(relevant) after seeing the retrieval evidence. |
| **Likelihood ratio** | How surprising the evidence is; the engine of Bayes. |
| **Calibration** | Whether a stated probability matches the observed frequency. |
| **Platt scaling** | Fitting a logistic map from score to probability. |
| **Brier score** | Mean squared error between predicted probability and outcome. |
| **ECE** | Mean gap between confidence and accuracy, weighted by bin size. |
| **Risk–coverage** | Error rate among the most confident fraction of answers. |
| **Selective prediction** | Abstaining on low-confidence cases. |
| **Abstention precision** | Of the refusals, the fraction that were genuinely unanswerable. |
| **κ (kappa)** | Chance-corrected agreement between raters. |
| **McNemar** | Paired test for two systems on the same items, binary outcome. |
| **Wilcoxon** | Non-parametric paired test for continuous outcomes. |
| **Effect size** | How big the difference is, not just whether it exists. |
| **Power** | The probability of detecting a real effect. A null on an underpowered test is not evidence of no effect. |
| **NLI** | Entailment / neutral / contradiction between a premise and a hypothesis. |
| **Claim** | An atomic statement that can be true or false. |
| **Noisy-OR** | Combining independent witnesses: 1 − Π(1 − pᵢ). |
| **Entropy** | Uncertainty in bits; H(0.5) = 1. |
| **Information gain** | H(prior) − H(posterior): how much evidence reduced uncertainty. |
| **Faithfulness** | Fraction of claims entailed by the retrieved context. |
| **Citation precision** | Of cited claims, the fraction whose citation actually supports them. |
| **Silver labels** | Labels mechanically derived from the document, not human-annotated. |
| **Supersession** | "Rev 4 replaced Rev 3" — both statements are true; not a contradiction. |
| **Term mismatch** | Two passages share vocabulary but are about different subjects; not a contradiction. |
| **Granularity** | A whole and one of its parts; both can be true at once; not a contradiction. |
| **Measurement term** | A noun that names a measurable quantity — the key a number must be governed by to count as a quantity. |
| **Positive control** | Labelling pairs whose correct answers are known, to check the labeller rather than the detector. |
| **Blind annotation** | Labelling passages without seeing the detector's scores, so the label cannot anchor on them. |
| **Base rate** | The prevalence of the condition; without it a false-positive rate is uninterpretable. |
| **Exchangeability** | The assumption that makes conformal guarantees valid — and that fails on a single-category corpus. |

---

*Compiled 31 October 2026 for the MTP presentation. Every
identifier in this document was resolved against a live bibliographic API; every
measured number was produced by the code in `impl/`.*
