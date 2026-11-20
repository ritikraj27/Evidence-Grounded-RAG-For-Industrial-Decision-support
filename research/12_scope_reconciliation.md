# 12 — Scope reconciliation: what the proposal promised, and what was built

**What this file is.** A defence-ready reconciliation of the MTP proposal's recorded
scope against the work that was actually built and measured. It exists so that a
panel can point at one page instead of discovering the discrepancies themselves.

**Written.** 11 November 2026, for the 18 November 2026 defence.

**What it answers.** Question 3 of §7 of `research/11_supervisor_briefing_2026-11-11.md`:
the proposal's scope, and what was descoped.

**A limitation, stated first.** The proposal document itself (`MTP-2.docx`) is **not in
this repository** — I checked; there is no copy of it here, only the record of it in
`research/06_industrial.md`. Everything below is therefore reconciled against the
**recorded** proposal scope: the twelve-category design guide in §4 of that file, its
construction rules 6–8, and §5.2, §5.6, §5.7 and §5.8. Where this file states what the
proposal promised, it is quoting that record and not a document the panel cannot see.
If the panel holds the original, the two items most likely to be checked against it
are §4's twelve-category table and §4 rule 8's annotation protocol; both are quoted
here from the record.

**House rule.** An honest negative is worth more than a favourable comparison. Where
something was descoped, this file says it was descoped and gives the reason. Where a
number in the briefing disagrees with the repository, the repository wins, and §7 says so.

**The corpora.** The repository holds three, not one:

| Corpus | Documents | Chunks | Modality | Benchmark | Licence | Where |
|---|---|---|---|---|---|---|
| Public, six categories (Wikipedia) | 46 | 2,383 | 2,114 text / 140 table / 129 chart | 276 queries (132 answerable, 144 unanswerable) | CC BY-SA 4.0 | `impl/data/corpus/`, `impl/data/benchmark/` |
| Focus subset — supply chain management only | 14 | 735 | 653 text / 44 table / 38 chart | 176 queries (32 answerable, 144 unanswerable) | CC BY-SA 4.0 | `impl/data/corpus_focus/`, `impl/data/benchmark_focus/` |
| **Industrial regulatory (eCFR, 2026-06-01)** | **110** | **2,443** | 2,324 text / 119 table / 0 chart | **444 queries (247 answerable, 197 unanswerable)** | public domain | `impl/data/corpus_industrial/`, `impl/data/benchmark_industrial/` |

A fourth corpus exists in the project but not in the repository: the September 2026
primary corpus, 634 chunks across 24 proprietary supply-chain documents, not
redistributable. It is the corpus every number in the pre-November deliverables was
*not* measured on, and it is the origin of the thesis's own limitation L2b.

---

## 1. Table A — the six research objectives reconciled

The objectives are the proposal's, in the proposal's numbering, as tabulated in
`deliverables/Deliverable_1_Part1_Content.md` §A.1 ("These are the MTP proposal's
objectives, in its numbering"). One objective per design move, D1–D5, plus RO6.

| RO | Objective, as stated | What was actually measured | Result files | Status |
|---|---|---|---|---|
| **RO1** | A code-level, non-bypassable retrieval-confidence gate returning an explicit "no evidence" response below a threshold, instead of calling the LLM (D1) | Gate fitted and swept on two corpora: focus τ = 0.05 (coverage 0.699, abstention precision 0.962, retriever recall of gold 1.000), industrial τ = 0.40 (coverage 0.691, abstention precision 0.847, Brier 0.159, ECE 0.075, base rate 0.556, retriever recall of gold 1.000). Generator-side comparison on one generator under two prompt conditions: rate of answering unanswerable questions 0.549 → 0.451 (cautious) and 0.889 → 0.597 (answering), paired McNemar p = 0.0094 and p = 1.3 × 10⁻⁹, at the cost of answering 30 of 32 answerable questions. **The second-generator replication was not run** — MiniMax-M3.1-Flash returned no text on 24 of 66 questions (23 of 44 on the table-lookup family, 1 of 22 on a control sample); 15 were rescued at a 4,096-token budget, 9 were not. | `impl/results_focus/exp2_gate.json`, `exp8_generation.json`, `exp8_generation_answering.json`, `exp13_generator_completion.json`; `impl/results_industrial/exp2_gate.json` | **Closed with evidence**, and with a qualified positive: supported under both prompt conditions on one generator; replication on a second generator not run |
| **RO2** | Per-modality retrieval quotas enforcing a minimum share of tables, charts and images (D2) | The quota **trades** rather than gains, and where it sits relative to the reranker decides which system it is compared against. Six-category corpus (140 table and 129 chart chunks in 2,383): the shipped system has table recall 0.929 and text 0.933; the quota applied **before** the reranker restores table recall to 1.000 while text falls to 0.923, and against the shipped system it raises MRR by +0.022 (p = 0.026) and nDCG by +0.019 (p = 0.064); applied **after** it, table recall returns to 0.929. Focus corpus: overall recall +0.031 applied before the reranker (p = 0.317), and −0.063 moving from the pre-rerank to the post-rerank placement (p = 0.157). Industrial corpus (119 table chunks, **no charts at all**): the quota before the reranker moves table recall 0.977 → 0.985 and text 1.000 → 0.974, and against the shipped system it gains MRR +0.011 (p = 0.038) and nDCG +0.007 (p = 0.049); moving it after the reranker returns both to the shipped values. There the chart floor is unsatisfiable by construction, and the framework reports the shortfall rather than papering over it. | `impl/results/exp1_ablation.json`, `impl/results_focus/exp1_ablation.json`, `impl/results_industrial/exp1_ablation.json`, `exp5_pool_size.json` (×3) | **Closed with a negative result** — a trade, not a gain; the mechanism's own hypothesis is qualified, not confirmed |
| **RO3** | Hybrid lexical + dense + reranker via RRF, preceded by a category filter, outperforms flat retrieval (D3) | **Not supported.** Six-category corpus: BM25 Recall@10 0.909 against the dense encoder's 0.750 (Δ −0.159, p = 0.00016); the fusion against its own lexical leg Δ +0.023 (p = 0.317), MRR −0.007 (p = 0.762), nDCG +0.001 (p = 0.815) — no win on any metric; the category pre-filter Δ 0.000 on recall (p = 1.000), with MRR +0.026 (p = 0.027). Industrial corpus, 247 answerable queries: BM25 0.960 against dense 0.879 (Δ −0.081, p = 0.00026, d_z = 0.238); the fusion against its lexical leg Δ 0.000 (p = 1.000); the category pre-filter Δ 0.000 on recall (p = 1.000), with MRR +0.007 (p = 0.088) — marginal, and in the same direction. The reranker's *recall* is governed by the candidate pool: on the industrial corpus Recall@20 = 1.000 at pool 50 while Recall@10 stays 0.988 — 1.21% of golds are found and then pushed out of the ten-chunk context. | `impl/results/exp1_ablation.json`, `exp5_pool_size.json`; `impl/results_focus/exp1_ablation.json`, `exp5_pool_size.json`; `impl/results_industrial/exp1_ablation.json`, `exp5_pool_size.json`; `research/09_encoder_swap.md` | **Closed with a negative result** |
| **RO4** | Cross-document contradiction surfacing — a joint NLI and topical gate (D4) | On the focus corpus the mechanism was **not evaluable**: precision 0.0 of 20 alarms against blind reader labels (95% upper bound 0.161), the same readers finding 0 contradictions in 80 random unflagged pairs, and the detector's own positive control 11 of 11. On the industrial corpus, where conflicts exist, it **finds them and types them wrongly**: under the regulatory vocabulary profile, detection precision 0.659 (CI 0.505–0.784) and 0.897 on the revision stratum where the conflicts are, but typing precision 0.073 (CI 0.025–0.194) — it reports supersessions as contradictions and cannot say which issue is in force, because nothing in the retrieved passages says which issue either of them is. Under the shipped profile the typing precision is 0.000 (CI 0.000–0.088) and detection 0.650 (CI 0.495–0.779). The quantity branch never fires where it provably should (recall 0.000 on 35 construction-labelled limit changes) and, on 1,776 cross-document candidates, fired 13 times and a specialist confirmed **0** of them as conflicts. | `impl/results_focus/exp11_contradiction_precision.json`, `exp11b_contradiction_control.json`; `impl/results_industrial/exp14_revision_eval.json`, `exp14_pairs_annotated.json`, `exp20_quantity_stratum.json`, `exp20_quantity_stratum_specialist_labels.json` | **Closed with a negative result** |
| **RO5** | Per-claim confidence tagging: each claim labelled *grounded*, *inferred* or *uncertain*, carrying a citation back to its source chunk (D5) | The band is a usable **filter** and **not** a usable **ranking**. Agreement between the two claim readers κ = 0.902 (gold protocol) and 0.724 (retrieved), over 350 claims each, plus an adjudicator over the contested claims (23 on the gold protocol); 347 carry a reference. Band against an independent reference: κ = 0.049 (CI −0.026–0.124) on the gold evidence, and the three bands are indistinguishable there (error 0.542 / 0.513 / 0.610); on the evidence the band itself saw, the bands *are* ordered (0.118 / 0.103 / 0.220) and the agreement is 0.069 (CI −0.002–0.139). Filter value: answers containing no wrong claim rise 34.4% → 50.0% (gold) and 59.4% → 81.2% (retrieved) at the cost of keeping 41.5% of claims. **Position beats the band**: keeping the first claims of an answer is the better selector (paired Wilcoxon p = 0.008, d_z = 0.465), and it is not a length artefact (Spearman position-vs-length −0.195, p = 0.0003). Industrial replication on a different generator: κ = −0.056 (CI −0.176–0.065), underpowered at 93% claim support. | `impl/results_focus/exp17_claim_band_eval.json`, `exp18_claim_band_eval.json`, `exp16_claim_band_ablation.json`; `impl/results_industrial/exp19_claim_band_eval.json` | **Closed with a negative result** |
| **RO6** | Evaluation on industrial corpora and industrial benchmarks, with cross-category generalisation | The objective the industrial corpus was built for. Now closed: an authentic regulatory corpus (110 documents, 2,443 chunks, four regimes, eCFR 2026-06-01), its benchmark (444 queries) with its own shortcut audit, cross-regime transfer (tuning half answerable answered 0.993 / unanswerable refused 0.299; held-out half **transferred** 1.000 / 0.299 — the same refusal rate as the tuning half and higher than the arm refitted on the held-out regimes, 0.259), and **three of the thesis's negative findings replicated on authentic industrial text**. The *scope* of RO6 was itself narrowed from the proposal's twelve-category benchmark; see Table B. | `impl/results_industrial/exp1_ablation.json`, `exp2_gate.json`, `exp4_transfer.json`, `exp5_pool_size.json`, `exp12_unanswerable_class_audit.json`; `impl/results/exp4_transfer.json` (rebuilt with the shared negative class) | **Re-scoped, then closed with evidence** |

**What the table says in one line.** Four objectives closed with a negative result
(RO2, RO3, RO4, RO5), one closed with a qualified positive (RO1), one re-scoped and
closed (RO6). The negatives are the finding; the project's rule is that an honest
negative is worth more than a favourable comparison, and none of these four was
surprising to the project once measured.

---

## 2. Table B — the corpus scope reconciled, category by category

The twelve categories and their named analytic methods are as recorded in
`research/06_industrial.md` §4's twelve-category design guide.

| # | Category (as promised) | Named analytic methods (as promised) | What was actually built | Why |
|---|---|---|---|---|
| 1 | **Supply Chain Management** ★ focus | Cp/Cpk, EOQ, safety-stock rules | **Built.** 14 documents, 735 chunks — the focus corpus, and the largest slice of the public corpus. | The focus domain of the thesis and the domain the practitioner scenarios come from. The *methods* were not implemented as an analytic surface (see the note under Table B). |
| 2 | **Predictive Maintenance** | Anomaly detection thresholds; degradation curves | **Built.** 6 documents, 316 chunks. | Public substitute; Wikipedia articles about the subject. |
| 3 | **Reliability Engineering** | FMEA RPN; Weibull; MTBF/MTTR | **Built.** 7 documents, 465 chunks. | As above. "Weibull distribution" and FMEA/RPN vocabulary appear in the corpus as *article text*, not as executed analytics. |
| 4 | **Quality Engineering** | Cp/Cpk, SPC control charts, Pareto | **Built.** 7 documents, 362 chunks. | As above. The 140 table and 129 chart chunks in the public corpus are what let the quota bite there at all — a corpus with no charts cannot satisfy a chart floor. |
| 5 | **Production Scheduling** | Scheduling heuristics; OEE; capacity modelling | **Built.** 7 documents, 244 chunks. | As above. |
| 6 | **Transportation & Logistics** | Incoterms; EOQ; network flow | **Not built.** | Descoped. The binding artefacts the proposal names — carrier rate cards, routing guides, lane schedules — are proprietary and not redistributable, and the public substitute is encyclopaedic prose, which carries no rate table. "Incoterms 2020" survives in the code only as an entry in the contradiction detector's *version vocabulary* (`impl/src/contradiction.py`), not as a corpus. |
| 7 | **Reverse Logistics** | Disposition logic; recovery-value scoring | **Not built.** | Descoped, same reason: RMA procedures, disposal manifests and refurbishment SOPs are proprietary plant documents. |
| 8 | **Inventory Management** | EOQ, safety stock, ABC/XYZ | **Not built.** | Descoped, same reason: stock policies, cycle counts and ABC/XYZ analyses are proprietary. |
| 9 | **Facility Layout & Location** | Facility layout; location models (p-median, gravity) | **Built.** 5 documents, 261 chunks. | Public substitute; the smallest of the six, and the smallest per-category sample in the benchmark (10 questions, against 34 for reliability engineering). |
| 10 | **Demand Forecasting** | Forecast methods; MAPE, MASE | **Not built — descoped, deliberately.** | `research/06_industrial.md` §5.7: this category is not a *text* retrieval problem at all. It is a numerical, tokenised-series problem with its own models (Time-LLM, Chronos, Timer-XL) and its own metrics (MASE, forecast-interval coverage). Lumping it into a document-chunking text-RAG pipeline produces weak results and would measure the tokenizer, not the mechanism. §5.7's own option (a): scope the thesis to the nine industrial-engineering categories and treat the ML three as future work. |
| 11 | **Time-Series Forecasting** | Time-LLM, Chronos, Timer-XL | **Not built — descoped, deliberately.** | As row 10. The same reasoning, stated in §5.7: "it is a numerical, tokenized-series problem with its own models and metrics". |
| 12 | **Anomaly Detection** | Isolation Forest; CUSUM/EQQ; anomaly-score thresholds | **Not built — descoped, deliberately.** | As rows 10–11, and it is the sharpest case: Isolation Forest is a *method*, not a document category, and no amount of text retrieval would measure it. |

### The fourth corpus — a substitution, not a fulfilment

The industrial regulatory corpus is **not** one of the twelve categories. It is a
substitution for the *authentic industrial corpus* limb of the proposal, and it is
marked as such.

| | |
|---|---|
| **What it is** | 110 documents, 2,443 chunks (2,324 text, 119 table, 0 chart), four regulatory regimes — OSHA general industry (44 documents, 983 chunks), EPA environmental control including new source performance standards (37, 909), EPA/OSHA process safety (10, 331), DOT hazardous materials (19, 220) — built from the Electronic Code of Federal Regulations at the versioner date 2026-06-01, in public domain, with a 444-query benchmark (247 answerable, 197 unanswerable) and its own shortcut audit. |
| **Why it was built** | RO4 needed a corpus that *contains* conflicts and RO6 needed a corpus that is *authentic*. Federal regulations are both: binding numeric requirements, and they get amended, so the same section read on two dates is the same rule at two issues. The eCFR versioner serves any past date; the corpus pairs 2021-12-31 with 2026-06-01. |
| **What it substitutes for** | The proposal's promise of a *licensed, redistributable* industrial corpus, in the sense of the licence and the provenance discipline. It does not substitute for the twelve categories. |
| **What it does not substitute for** | The proposal's binding artefacts. This is the thesis's own limitation L2b, unchanged: the corpus is industrial in subject matter but not operationally binding — regulation, not the operating manuals, control plans and supplier specifications a practitioner actually uses. The industrial corpus moves from "articles about concepts" to "binding regulatory text", which is a genuine step, and it does not reach "the documents a plant engineer reads". |
| **Marked as** | **Substitution, not fulfilment.** The category table above still has three rows empty. |

### The named analytic methods — a note that belongs to Table B

None of the named analytic methods (Cp/Cpk, Mann–Kendall, EOQ, Isolation Forest, FMEA
RPN, Weibull, MASE) is implemented as an analytic surface the framework invokes or
verifies against. `Mann–Kendall`, `Isolation Forest` and `MASE` appear nowhere in
`impl/src/`, `impl/scripts/` or `impl/experiments/`; `eoq`, `wip`, `oee`, `tat` and
`cpk` appear only inside `_OPERATIONS_MEASUREMENT_TERMS` in
`impl/src/contradiction.py` — a **vocabulary for finding numbers in text**, not an
analytic the framework computes. The proposal's phrase "a named analytic surface that
the generated answer must respect" (§4) was descoped. The honest form of the claim is
that the framework *retrieves and cites* the artefact a method would have produced; it
does not *verify* the answer against the method.

---

## 3. Table C — the annotation protocol reconciled

The proposal's protocol, as recorded in `research/06_industrial.md` §4 rules 6 and 8
and §5.8: *"annotated by LLM agents using a structured protocol, with human-expert
validation on a random subset to be reported"*, dual annotation with κ ≥ 0.7, an
explicit unanswerable class, and a licensed, redistributable corpus.

| Proposal requirement | What was delivered | Status |
|---|---|---|
| **Annotated by LLM agents using a structured protocol** | A panel of domain-specialised **language-model** readers with an adjudicator: for RO4, one specialist per regulatory regime (occupational safety 133 pairs, process safety 44, environmental control 52, hazmat transport 11) plus a generalist control reading all 240 pairs blind; for RO5, a generalist reader and a supply-chain specialist (κ = 0.902) plus an adjudicator over the 23 contested claims. Two specialists verified their calls against the eCFR's point-in-time API rather than reading alone. | **Delivered.** Note this is the proposal's *own* wording: the annotators were to be LLM agents, so this is fulfilment, not shortfall. |
| **Dual annotation with κ ≥ 0.7** | Delivered, and exceeded: RO5 claim readers κ = 0.902 (gold, n = 350) and 0.724 (retrieved, n = 350); each RO4 specialist against the generalist control κ = 0.661, 0.724, 0.686 and 0.651 (raw agreement 0.805–0.932). A factorial control shows the fix was the **rubric's wording**, not the specialisation: the generalist agrees with each specialist at κ 0.65–0.72, while the reader using the old rubric agrees with them at κ 0.07–0.44. | **Delivered.** |
| **Human-expert validation on a random subset** | **Not delivered.** No human round was run, on any sheet. What stands in its place is agreement between independent model readers, with the full agreement statistics reported and a control that separates the rubric's contribution from the specialisation's. What a human round would have added is *independent confirmation that the labels are right rather than merely consistent* — and this mattered most in exactly the place where the two readers disagreed by a factor of nine in the measured precision (0.075 against the old rubric, 0.659 against the sharpened one). The thesis already discloses that its Experiment 11 annotators were models; this work extends that disclosure to the two heaviest measurements in RO4 and RO5. | **Not delivered — the single largest divergence from the proposal.** |
| **An explicit unanswerable class** | Delivered, and then **repaired** — which is a contribution, not a shortfall. The proposal made this the single most important benchmark-design requirement (`research/06_industrial.md` §4 rule 7: a benchmark without an unanswerable class cannot measure RO1's gate). The class exists in all three benchmarks (144 of 276 on the six-category corpus, 144 of 176 on the focus corpus, 197 of 444 on the industrial corpus). Its *first* construction was defective: one regular expression — a fabricated `PREFIX-digits` identifier — carried 76.4% of the class, so the class was separable from the question text alone. It was rebuilt as a **corpus-anchored** class, where that rule now carries **0.0%** (it catches 0 of 197 on the industrial benchmark). The pre-repair benchmark is kept in the repository (`benchmark_pre_unanswerable_repair.json`) so the finding stays checkable. | **Delivered.** |
| **Benchmark of 500 questions** | The benchmarks delivered are 276 (six-category), 176 (focus) and 444 (industrial). None is 500. The count is bounded by the corpus rather than chosen: the industrial benchmark's `numeric_fact` family falls to 7 questions because the documents carrying the exposure-limit tables were thinned with everything else. The unanswerable class is over-sampled in every benchmark, deliberately, because the gate's whole purpose is refusal. | **Descoped in size.** |
| **A licensed, redistributable corpus** | Delivered twice over: the public corpus is CC BY-SA 4.0 (Wikipedia, with per-document URL, upstream revision, SHA-256 of the bytes used and chunk count, shipped in `deliverables/dataset/`); the industrial corpus is **public domain** (US federal regulations), which removes the licence question the proposal's own limitation table names as the remediation. | **Delivered.** |
| **A named analytic surface per category** | Descoped; see the note under Table B. | **Descoped.** |

---

## 4. The numbering conflict

Two documents a panel will read side by side use the same labels for different things.

| | `deliverables/Deliverable_1_Part1_Content.md` (§A.1) | `deliverables/templates/scripts/make_pptx.py` (slide 7, `objs`, line 578) |
|---|---|---|
| Unit | one objective per **design move** | one objective per **research phase** |
| RO1 | the code-level confidence gate (D1) | framework design |
| RO2 | per-modality retrieval quotas (D2) | component-level evaluation — carrying H2.1–H2.4 |
| RO3 | hybrid retrieval via RRF with a category filter (D3) | failure-mode characterisation |
| RO4 | cross-document contradiction surfacing (D4) | cross-category generalisation — carrying H4.1 |
| RO5 | per-claim confidence tagging (D5) | — (no RO5) |
| RO6 | evaluation on industrial corpora, with cross-category generalisation | — (no RO6) |

So the deck's RO1 is the thesis's *framework* and the guide's RO1 is the *gate*; the
deck's RO4 is the guide's RO6; and the deck's RO2 bundles the guide's RO1–RO5 into a
single objective that carries four hypotheses. A panel member who asks "is RO2
answered?" will get two incompatible answers depending on which document they have open.
This is not a typo — it is two different taxonomies sharing one label.

### Recommendation: keep RO1–RO6 (the deliverable's scheme) as canonical, and re-label the deck's four phases

**Reasoning.** The six-objective scheme *is* the proposal's numbering — the guide says so
explicitly ("These are the MTP proposal's objectives, in its numbering") — and it is
one-to-one with the design moves D1–D5 and with the experiment files a reader will open
to check a claim (exp1, exp2, exp3/exp11, exp15/exp17, exp4). Renumbering the thesis
away from the proposal's own objective list is a defence cost; adapting the deck to the
thesis is not. The deck's four phases are a *different taxonomy*, so they cannot be
reconciled by relabelling alone: the deck's RO2 genuinely bundles five of the six
objectives. The fix is therefore to stop using "RO" for the phases.

**What changes, and where.** Edit the **templates**, never the built files —
`deliverables/scripts/build_all.py` restores each template over its working copy and
re-substitutes the measured values, so an edit to the built file is overwritten by the
next build.

1. `deliverables/templates/scripts/make_pptx.py`, the slide titled **"Research
   Objectives & Hypotheses"** (the seventh slide; its footer number is 6) — the `objs`
   list, lines 577–597: replace the four `RO1…RO4` cards with four cards on a
   non-colliding axis — e.g. **Phase A–D** — each naming the objectives it covers:
   Phase A → RO1; Phase B → RO2, RO3, RO4, RO5 (carrying H2.1–H2.4, with H2.4 split
   across RO4 and RO5); Phase C → RO2–RO5 as the characterisation the negative results
   feed; Phase D → RO6 (carrying H4.1). The four-card layout and the column geometry
   (2.98″ wide, `x += 3.08`) do not change; only the labels and the hypothesis lines do.
2. Same file, that slide's speaker notes (lines 612–619): "Four objectives… RO1 and RO3
   do not carry formal hypotheses" becomes a statement about the phases, and the note
   must name the objectives each phase covers, so the deck states the mapping rather than
   leaving the panel to infer it.
3. Same file, line 1419: on the slide **"Results: Contradiction Surfacing &
   Cross-Category Transfer"** (the seventeenth; footer number 16), the header
   `CROSS-CATEGORY TRANSFER (RO4)` becomes `CROSS-CATEGORY TRANSFER (RO6)`, or loses the
   RO label entirely.
4. `deliverables/templates/Deliverable_1_Part1_Content.md`: **no renumbering needed**
   under this recommendation. It needs (a) a pointer to
   `research/12_scope_reconciliation.md` in the RO table of §A.1, and (b) the RO4, RO5
   and RO6 rows updated to record that those objectives are now closed on the industrial
   corpus — the current RO4 row still reads "The mechanism works, and this corpus cannot
   evaluate it", which is true of the focus corpus and superseded by the industrial
   measurement that RO4 actually closed with.
5. Rebuild with `deliverables/scripts/build_all.py`, then run
   `deliverables/scripts/check_consistency.py` and `deliverables/scripts/check_slides.py`;
   both read the deck and the results, so a renumbering that breaks a cross-reference
   will fail there rather than in front of the panel.

**The alternative, and why not.** Making the deck's four-phase scheme canonical would
force RO1–RO6 → RO1–RO4 renumbering in the guide, the paper and every results table
that cites an objective — a much larger blast radius, and it breaks the continuity with
the proposal's own objective list, which is the one thing a panel is most likely to
check the thesis against. Doing nothing — shipping this file as the only reconciliation —
is the third option, and it is the one that leaves the two documents contradicting each
other on the table.

---

## 5. What we claim, and what we do not claim

Written so that it can be lifted verbatim into the thesis.

> **Scope.** This thesis evaluates an evidence-grounded RAG framework on corpora it could
> obtain and redistribute: a public six-category industrial corpus (46 documents, 2,383
> chunks, 276 questions), its supply-chain focus subset (14 documents, 735 chunks, 176
> questions), and an authentic regulatory corpus built from the US Code of Federal
> Regulations (110 documents, 2,443 chunks, four regulatory regimes, 444 questions).
> **We do not claim** the twelve-category, three-domain industrial benchmark the proposal
> described: nine industrial-engineering categories were reduced to six, and the three
> machine-learning categories — demand forecasting, time-series forecasting and anomaly
> detection — were descoped, because they are numerical series-reasoning problems rather
> than document-retrieval problems and a text-RAG pipeline cannot measure them. **We do
> not claim** that retrieval configurations transfer across industrial sub-domains in
> general; what we measure is transfer across four regulatory regimes within one corpus
> and across the six categories of one public corpus, where the coverage transfers and
> the fitted threshold does not. **We do not claim** human-expert validation of the
> benchmark labels: the annotations were produced by domain-specialised language-model
> readers with an adjudicator, their agreement is reported in full (κ = 0.902 on the
> claim labels; 0.65–0.72 between each specialist and a generalist control), and
> consistency between readers is not correctness. **We do not claim** that the named
> analytic methods of the proposal — Cp/Cpk, Mann–Kendall, EOQ, Isolation Forest, FMEA
> RPN, Weibull, MASE — are computed by the framework; it retrieves, cites and
> cross-checks the artefacts they produce, and where a contradiction detector names a
> quantity it does so by vocabulary, not by arithmetic. What we do claim is measured,
> with its file named: four of the six research objectives closed with a negative
> result, one with a qualified positive on a single generator, and one re-scoped and
> closed on an authentic industrial corpus.

---

## 6. The three options put to the supervisor

Restated from §7.3 of `research/11_supervisor_briefing_2026-11-11.md`.

| Option | What it is | Cost, in one line |
|---|---|---|
| **(a)** | A scope-reconciliation table stating plainly what was descoped and why — **this file**. | Written; needs a pointer from the guide's §A.1 and one paragraph in the limitations table; about half a day to fold into the deliverables. |
| **(b)** | An extension into the machine-learning and data-analytics categories, so the twelve-category promise is literally met. | Weeks, not days: it needs a series corpus, a distinct arm with series-appropriate metrics (MASE, forecast-interval coverage), and a new benchmark — and it would measure a different system from the one this thesis builds. |
| **(c)** | A re-reading of the proposal's wording as "industrial sub-domains", the way the thesis already re-reads the cross-category transfer claim as intra-domain. | Cheap, but it is a change of wording in place of a change of scope, and it is the option a panel is most likely to see through: the proposal's own list names demand forecasting and anomaly detection as machine-learning categories, and no re-reading makes them industrial engineering. |

**Recommendation: (a).** It is the only option that costs a day rather than a month, and
it is the only one that puts the discrepancy on the record *before* the panel finds it.
It also keeps the thesis's own method intact: the project's rule is that an honest
negative is worth more than a favourable comparison, and (b) buys a claim by building a
different system, while (c) buys a claim by changing the words. (a) converts a
discrepancy a panel would otherwise discover into a finding the thesis has already
characterised — and the three descopings have reasons that survive scrutiny: the
proprietary nature of the binding artefacts for three industrial categories, the
machine-learning three being a different problem class, and human-expert validation
having been replaced by model readers whose agreement is reported in full.

Option (b) is not rejected outright; it is the honest next measurement, and it belongs
in the next-steps list rather than in the eighteen days before the defence.

---

## 7. Corrections to the project's own records

Found while verifying every number in this file against the repository. The repository
wins in each case. None of them changes a conclusion; all of them are in the project's
own research notes, which a panel may read.

| # | Record | It says | The repository says |
|---|---|---|---|
| 1 | `research/10` §1.3 | the industrial benchmark is "469 queries, 270 answerable and 199 unanswerable", with a `unanswerable_corpus_anchored_numeric` family of 4 | `impl/data/benchmark_industrial/benchmark.json`: **444 queries, 247 answerable, 197 unanswerable**, and **no numeric unanswerable family**. §2.2 of the same file and the briefing use 444 / 247 / 197, which are the repository's figures. §1.3 is stale. |
| 2 | `research/10` §1.4 | the industrial shortcut audit: structural ROC-AUC **0.843**, bag-of-words **0.841**, permutation null mean 0.504 / sd 0.031 / max 0.572, majority-class F1 0.731, median lengths 83 / 55 characters | `impl/results_industrial/exp12_unanswerable_class_audit.json`: **0.708** (structural), **0.793** (bag of words), null mean **0.505** / sd **0.036** / max **0.597**, F1 **0.715**, median lengths **73** / **50**. The p-values (0.0099, 0.032) and the shortcut's 0.0% agree in both. The same file records that the question-only policy and the parametric-leakage probe were **not run** ("no API credential reachable"). |
| 3 | `research/10` §3.2b | the circularity audit's independent reference hallucination rate is **0.656 [0.589, 0.718]** (gold) and **0.118 [0.075, 0.181]** (retrieved) | `impl/results_focus/exp17_claim_band_eval.json` (gold): **0.571 [0.518, 0.622]**; `exp18_claim_band_eval.json` (retrieved): **0.164 [0.129, 0.207]**. The figure 0.118 [0.075, 0.181] is the *grounded band's* error rate on the retrieved protocol, not the reference's rate. The section's qualitative conclusion — that the shipped 0.382 is entailment presented as hallucination, and that two independent estimates bracket it — stands either way. |
| 4 | `research/10` §4.5 | four detector configurations (`shipped`, `lookback`, `instance`, `regulatory`), with the *shipped* one at detection 0.659 (CI 0.505–0.784) and typing 0.073 (CI 0.025–0.194) | `impl/results_industrial/exp14_revision_eval.json` holds two profiles, `shipped` and `regulatory`. The 0.659 / 0.073 pair belongs to **regulatory** (41 alarms); **shipped** scores detection **0.650** (CI 0.495–0.779) and typing **0.000** (CI 0.000–0.088). `lookback` and `instance` have no separate entry. |
| 5 | the briefing and `research/10` §4.1 | **948 amended-paragraph pairs** in the revision corpus | **Updated 12 November 2026.** When this note was written (11 Nov, 13:48) no result file recorded the 948, and the artefact in the repository was the 240-pair sheet the measurement used — 90 revision-stratum and 150 retriever-neighbour pairs, of which 35 change a quantity and 55 are supersessions by construction. `impl/results_industrial/exp21_revision_corpus_stats.json` was written three hours later (16:56) and does record it: `n_amended_paragraph_pairs = 948`, `n_pairs_stating_different_numbers = 361`, `share_stating_different_numbers = 0.381`. `research/10` §4.1 was therefore already right. The briefing's clause was the wrong one — it read the 35 (a count on the 240-pair sheet) as a count against the 948 — and it has been corrected to 361, with the change recorded in the briefing itself. |

---

*Every number in this file was read from the repository on 11 November 2026. Where the
supervisor briefing of the same date and the repository disagree, the repository's
figure is the one printed here and the disagreement is listed in §7.*

**Status, 12 November 2026.** Rows 1–4 have been fixed in `research/10` and its
figures now agree with the repository. Row 5 was a different kind of entry — a
number that had no artefact behind it when the row was written and did have one
three hours later — and it is now closed on both sides: the artefact exists and
the briefing's clause has been corrected.
