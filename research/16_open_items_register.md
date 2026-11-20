# 16 — The open-items register: every limitation and every gap, in one list

**Written:** 12 November 2026, six days before the defence.
**Purpose:** one list, so that the limitations and the gaps can be closed one by
one instead of being rediscovered one by one. Every item below already exists
somewhere in this repository; this note gathers them, gives each one an ID, and
says what closing it would take.

**Sources, by section:**

| Section | Comes from |
|---|---|
| A — the limitations | `research/14_full_explanation.md` §10 |
| B — the supervisor's decisions | `research/14_full_explanation.md` §12.1; `research/11_supervisor_briefing_2026-11-11.md` §7; `research/12_scope_reconciliation.md` §6 |
| C — the measurement gaps | `research/14_full_explanation.md` §12.2 (G1–G15) |
| D — the gaps the answer-validation note found | `research/15_label_validation_protocol.md` §5 and §4.4 |
| E — the probes that were never run | `impl/results_industrial/exp12_unanswerable_class_audit.json` |
| F — the partly-closed threats | `research/08_direction_check.md` §4.0 |
| G — the pre-submission checklist | `deliverables/templates/READ_ME_FIRST.md`; `research/11_supervisor_briefing_2026-11-11.md` §8 |
| H — what is closed | `research/14_full_explanation.md` §12.3 |

---

## How to read this list

**A limitation is not a gap, and a gap is not a limitation.** A limitation is a
statement about the boundary of the evidence — it cannot be "fixed", because
fixing it would mean having a different thesis. What can be done to a
limitation is to *bound* it (narrow the claim to what the evidence supports) or
to *record* it (put it on the record before a panel finds it). A gap, on the
other hand, is a measurement that has not been made, and most of them can be
closed.

Each item carries an **owner**:

| | Owner | Meaning |
|---|---|---|
| **S** | Supervisor | A decision that is not the author's to make. |
| **M** | Measurement | Needs code and compute. Closeable in principle without a person. |
| **H** | Human | Needs an annotator, a practitioner or a second jurisdiction. |
| **D** | Document | An editorial action by the author before submission. |
| **L** | Limitation | Cannot be closed. Can only be bounded or recorded. |

**A note on priority.** Section C is ordered the way `research/14` orders it —
by how much closing the item would change the thesis's claims. The order of the
next-steps list that the deliverables ship (`results_source.next_steps`) is a
*different* order: by feasibility. Both are correct for their own purpose, and
the difference between them is itself a finding — the cheapest items to close
are not the ones that matter most.

---

## A. The limitations (13 items) — owner **L**, with the exception of A11

These are the boundaries of the evidence. A11 is the only one with a decision
attached to it.

| ID | Limitation | Where it is stated | What can be done about it |
|---|---|---|---|
| **L1** | The silver labels are optimistic and mechanically tied to the chunking, which could inflate the benefit of a retriever that shares the chunking's biases. | `14` §10 | Bound the claim: the labels are silver-standard throughout and disclosed as such. Cannot be closed without human labels — see G16. |
| **L2** | The rebuilt unanswerable class is a *near-miss class*. 106 of its questions have a structural twin, but an independent re-check found questions whose subject the corpus comments on without defining it, so the refusal rate is measured on a class that is partly answerable in a human's sense. | `14` §10; the near-miss examples are listed in `exp12_unanswerable_class_audit.json` | Bound the claim: this bounds what the *absolute* number means, not the arm comparison, in which every arm is asked the same questions. Partially closeable by G21. |
| **L3** | The original corpus is public reference material rather than proprietary industrial documentation. | `14` §10 | Cannot be closed — the proprietary corpus cannot be redistributed. L4 is the partial remedy. |
| **L4** | The second corpus narrows L3 but is one jurisdiction, one language, one regulatory family, and regulation rather than a plant's own procedures. | `14` §10 | Closeable by H2 and H3 (another jurisdiction; a plant's own documents). |
| **L5** | Retrieval and gating quality are measured, not end-to-end decision quality. That requires a practitioner study, and the 16-participant pilot supports a within-subject sign test but not a claim about generalisation. | `14` §10 | Needs a properly powered practitioner study. Beyond the defence window. |
| **L6** | The conflict mechanism's precision is measured against reader labels rather than against a proxy. | `14` §10 | Closeable by G1 (human labels on the conflict pairs). |
| **L7** | The per-claim band does not certify correctness. | `14` §10 | Already bounded: the band is reported as a filter with a measurement decomposition, not as a certification. Nothing further to do. |
| **L8** | The query-form check does not parse English. It is lexical, so it misses stems whose malformation is grammatical, and it has no dictionary or language model, so a keyboard mash passes it. It refuses 37.5% of the hand-labelled malformed stems (6 of 16, with no false rejections among 13 well-formed stems) and fails open on what it cannot judge — the conservative direction, since a false rejection would refuse a question the corpus could have answered. | `14` §10 | Bounded and stated. A stronger check is a code change, not a gap. |
| **L9** | The labels on the conflict pairs are model-generated, so the panel's agreement is reported in full but agreement between readers is not confirmation that a label is right. Independent confirmation would require human annotators. | `14` §10 | Closeable by G1. |
| **L10** | The wording of the annotation rubric moved the measured precision by a factor of nine — a warning about every model-annotated number in the thesis, not only about that one. | `14` §10 | Closeable only in part, and only by G1: the rubric must be fixed *before* the human round, not after. The factorial that found this is shipped. |
| **L11** | The proposal promised twelve categories spanning industrial engineering, machine learning and data analytics. The thesis has industrial engineering (six sub-domains) and industrial regulation (four regimes). | `14` §10; `research/12_scope_reconciliation.md` | This is **D1** below — a decision, not a limitation, until the decision is taken. |
| **L12** | *The weakest part of the work is the annotation.* The rubric factorial showed that the wording of the labelling instructions moved the headline number by a factor of nine, which means every model-annotated measurement carries that uncertainty. The detection/typing decomposition survives it because it also has a label-free form; the band measurement is the one that depends on the readers most. | `14` §11 | This is the honest answer to "what is the weakest part of the work". It is a limitation that G1 is the only route out of. |
| **L13** | **The shipped system applies the modality quota after the reranker, and the thesis's own ablation says it belongs before.** | The measurement is unambiguous on the focus domain — the pre-rerank quota moves overall Recall@10 by +0.031 against −0.031 for the shipped placement — and the six-category corpus agrees. The system was built with the after placement and every measurement in the project was taken with it, so every retrieval-side result sits on the configuration the ablation ranks second. The cost is stated in the deliverables rather than left to be found: on the focus domain the shipped placement gives up 3.1 points of Recall@10 against no quota at all, where the earlier placement would have gained them. | The defect is that the shipped configuration and the recommended one differ, and moving it is a research-scale change rather than a one-line edit: the gate's calibration, the generator-side comparison and the per-claim results all sit on the retrieval it would change. It is the first item in the next-steps list. |

---

## B. The supervisor's decisions (6 items) — owner **S**

**One has been taken; three are implemented and await only an acknowledgement;
two are still open.** The status is in the last column, so that a supervisor
reading this register can see, in one place, exactly what is outstanding.

| ID | Decision | Options | Recommendation | Cost | **Status, 12 November 2026** |
|---|---|---|---|---|---|
| **D1** | **The proposal's scope.** | (a) a scope-reconciliation table stating plainly what was descoped and why; (b) an extension into the machine-learning and data-analytics categories; (c) a re-reading of the proposal's wording as "industrial sub-domains". | **(a)**, and it is now *in the thesis*, not only in the research note: the twelve-category table with the reason for every row is the Complete Guide's **§A.6**, the scope statement is quoted there verbatim, the limitation is **L19** in the guide's limitations table, and the technical report, both papers, the plain-language guide, the status report and the deck's limitations slide all carry it. | (a) done. (b) is not rejected: it is the honest next measurement and belongs in the next-steps list, where it already is. (c) is a change of wording in place of a change of scope. | **CLOSED — option (a) taken and folded into the deliverables.** |
| **D2** | **The conference paper's page budget.** It is 13 pages against a recorded 10, raised with the reason in `deliverables/scripts/check_latex.py`. | Keep 13, or cut the clearest new result or the positioning paragraphs. | A judgement about what the paper is for. A 13-page IEEE conference paper is not a submittable conference paper. | — | **OPEN — the one decision that is a genuine judgement and is not the author's to make.** What is already done: the budget, the reason for raising it and the page count are recorded in `deliverables/scripts/check_latex.py`, and the build *fails* if the paper goes over 13 pages, so the number cannot drift. If the supervisor decides on a cut, the two named candidates are the clearest new result (the detection/typing decomposition) and the positioning paragraphs, and either can be removed without touching a measurement. |
| **D3** | **Does the industrial corpus become a second corpus (a generalisation section) or the primary one?** This changes the abstract. | Keep the focus corpus primary, add the industrial corpus as the external-validity section; or re-frame the thesis around "what a practitioner actually reads" and re-order the report. | Keep the focus corpus primary — it carries the pre-registered measurements. | Re-ordering the report if the second option is taken. | **IMPLEMENTED, acknowledgement outstanding.** The recommendation *is* the state of the deliverables: the abstract leads with the focus domain and the industrial corpus is the second-corpus section. The change would be a re-ordering of the report, which nothing has done. |
| **D4** | **How should the model annotators be disclosed?** The disclosure applies to the two heaviest measurements. | Keep it in the limitations table with the agreement statistics beside it; or present it as human annotation. | Keep it in the limitations table with the agreement statistics beside it. | — | **IMPLEMENTED, acknowledgement outstanding.** The disclosure is in the guide's limitations table with the agreement statistics beside it — κ = 0.902 on the claim labels and 0.65–0.72 between each specialist and a generalist control — and the guide says explicitly that consistency between readers is not correctness. |
| **D5** | **"Specialisation" was a brief, not a capability.** The factorial shows a brief plus a sharpened rubric buys nothing over the rubric alone — a narrower claim than "specialists are not needed". | Keep the narrowed wording; or run a stronger version with genuinely different reader models. | Keep the narrowed wording for the defence, and put the stronger version in the next-steps list. | The stronger version is M-gated (see G3). | **IMPLEMENTED, acknowledgement outstanding.** The narrowed wording is what the deliverables say, and the stronger version is named in the next-steps list. Note that the stronger version has since been *partly* run: the industrial panel used genuinely different reader models — one specialist per regulatory regime, plus a generalist control — and the result was the same, the rubric's wording being the binding constraint. See §H row 19. |
| **D6** | **Where should the thesis lead?** | Lead with the detection/typing decomposition and the rubric factorial and demote the BM25 replication; or lead with the replication. | The edit has **already been made** — the abstract leads with the framework and the industrial findings, and BM25 is deliberately not in it. This asks for confirmation, not for work. | — | **CONFIRMATION ONLY.** The edit is made and the three abstracts and the deck's opening all carry the framework and the industrial findings, with BM25 in none of them. Nothing is outstanding but the supervisor's word. |

---

## C. The measurement gaps (15 items) — owner **M** unless marked

Ordered as `research/14` §12.2 orders them: by how much closing the item would
change the thesis's claims.

| ID | Gap | What closing it takes | Owner |
|---|---|---|---|
| **G1** | **Human confirmation of the conflict labels.** The readers were models; agreement between readers is not confirmation that a label is right. The rubric factorial made it worse rather than better: the wording of the labelling instructions moved the measured precision by a factor of nine, so the human round has to fix the rubric before it is run, not after. | Human annotators on a stratified sample of the conflict pairs, against a fixed rubric. The pairs and the rubric ship with the thesis for that round. | **H** |
| **G2** | **One jurisdiction, one language, one regulatory family.** Nothing shows the detection/typing decomposition holds for another jurisdiction's regulatory language, for a plant's own procedures, or for vendor specifications. | Another regulator family; a plant's own documents; vendor specifications. | **H** |
| **G3** | **"Specialisation" was a brief, not a capability.** The factorial shows a brief plus a sharpened rubric buys nothing over the rubric alone. | Genuinely different reader models, not a brief to a fixed one. | **M** |
| **G4** | ~~**The positional comparison did not replicate** on three of the four corpus-and-protocol combinations.~~ **CLOSED 12 November 2026 — see §H row 19.** The *direction* replicates in all four; what does not is the *significance*, and the register's wording had conflated the two. | — | **M** |
| **G5** | **A plant's own revised procedures.** The eCFR corpus supplies the conflicts the Wikipedia corpus could not; it does not supply a plant's documents, where the same procedure at two revisions would be the same kind of conflict with no public versioner to align them. | A plant corpus, plus a re-fit of the conflict calibration on it — the calibration is fitted per corpus, exactly as the answer gate's threshold is. | **H** |
| **G6** | ~~**The soft-prior alternative to the hard category pre-filter** was never tried.~~ **CLOSED 12 November 2026** — see §H row 15. | — | **M** |
| **G7** | **A second, stronger reranker** in the pool-size factorial. The pool-size result is measured; the reranker is not shown not to be the confound. | A 2×2 over {two rerankers} × {pool 10, 50, 100}, plus a no-rerank arm. | **M** |
| **G8** | **A token-level faithfulness monitor** in the SYNCHECK style, so the gate is compared to a detector rather than only to a prompt. | Implement one competing policy and report all three on one risk–coverage plot. | **M** |
| **G9** | **The long-context answer-quality half** on the six-category corpus. The cost half is measured on both corpora and the quality half on the focus domain. | One run: the corpus fits the 1M-token window used here. | **M** |
| **G10** | **The generator-side comparison on a second provider family.** One provider behind five arms settles the hypothesis for one family. | A generator from a different provider family, on the same five arms and both prompt conditions. | **M** |
| **G11** | ~~**A third answer-validation convention.**~~ **CLOSED 12 November 2026** — the same gap as **G18** below. See §H row 12. | — | **M** |
| **G12** | **A meta-evaluation of the annotation instrument** against human labels, so that the model readers' agreement reads as a property of the pairs rather than of the models. | Depends on G1. | **H** |
| **G13** | **The corpus stratified by modality**, with a pre-registered power analysis, so the quota objective can be tested with adequate power. | A stratified corpus and a pre-registered analysis. | **M** |
| **G14** | ~~**The gate fitted per retriever**, with the frontier reported as a curve rather than a point.~~ **CLOSED 12 November 2026** — see §H row 16. | — | **M** |
| **G15** | **A hand-check of the repaired unanswerable class** against the corpus. The audit is no longer a single-corpus result — it has been repeated on the industrial corpus — but the part no audit can do is a person reading the class against the corpus. | A person reading the repaired class against the corpus, on both corpora. | **H** |

---

## D. The gaps the answer-validation note found (5 items)

From `research/15_label_validation_protocol.md` §5 and §4.4. These sit alongside
G1–G15 and were not in the fourteen's list.

| ID | Gap | What closing it takes | Owner |
|---|---|---|---|
| **G16** | **No human double-annotation of a sample of the benchmark's own questions.** Nobody has independently written the answer to a sample of the focus or industrial benchmark's questions, so the *correctness* of the silver labels is unmeasured on this corpus. The label audit checks the gold string against the document, not against a human's reading of the question. Nothing establishes that the generated question is *unambiguous*, which is the assumption the whole protocol rests on. | **This is the single largest open item.** Two annotators on a stratified sample; report Cohen's κ; adjudicate disagreements; and hold the annotation set out of the gate's calibration split. | **H** |
| **G17** | **No measurement of the aliasing rate on this corpus's gold answers.** The mechanism is quantified (127 of 411 golds carry a purely numeric content token, 15 are the string `"No"`, 13 carry a trailing full stop inside a token), but nobody has counted how many of this corpus's gold answers have *more than one correct surface form*, because that requires G16. | Follows G16. | **H** |
| **G18** | ~~**No re-scoring of the shipped results under a third validation convention.**~~ **CLOSED 12 November 2026** — see §H row 12. | — | **M** |
| **G19** | ~~**No measurement of how often the two tests disagree, question by question.**~~ **CLOSED 12 November 2026** — see §H row 13. | — | **M** |
| **G20** | **Two generator-side runs have not been completed.** The industrial corpus's generator-side evaluation (`exp8_generation_industrial.json`) was not run — HTTP 429, token plan limit. The second-generator replication on the focus corpus (`exp8_generation_flash.json`, `exp8_generation_answering_flash.json`) was not run — the generator returned empty completions on the table lookups, and raising the output budget fourfold did not fix it. | A generator that can parse a table, or one whose reasoning budget is bounded; and a working quota for the industrial run. | **M** |

---

## E. The probes that were never run (2 items)

From `impl/results_industrial/exp12_unanswerable_class_audit.json`, which
records three sub-probes as `status: not_run`.

| ID | Probe | Why it is not run | Owner |
|---|---|---|---|
| ~~**G21**~~ | ~~**The question-only policy** on the industrial corpus — can the question alone tell an answerable question from an unanswerable one?~~ **CLOSED 12 November 2026** — see §H row 17. | — | **M** |
| ~~**G22**~~ | ~~**The parametric-leakage probe**, including its closed-book scoring sub-probe — does a generator's own knowledge separate the classes?~~ **CLOSED 12 November 2026** — see §H row 17. | — | **M** |

---

## F. The partly-closed threats (6 items)

From `research/08_direction_check.md` §4.0. Each names what is still open; each
residue is already a gap above, so this section is a cross-reference, not new
work. It is kept because a threat list that is edited after the fact is a
threat list nobody can audit.

| # | Status | Still open | Which gap above |
|---|---|---|---|
| **T1** | Partly closed | The soft-prior alternative was never tried. | **G6** |
| **T7** | Partly closed | The 2×2 over a second, stronger reranker was never run. | **G7** |
| **T8** | Closed for the focus domain | The quality half on the six-category corpus. | **G9** |
| **T10** | Closed in the sense that the comparison now exists | Plant-floor procedural text, and other jurisdictions. | **G2**, **G5** |
| **T11** | Partly closed | Human dual annotation. | **G16** |
| **T16** | Partly closed | A token-level faithfulness monitor in the SYNCHECK style. | **G8** |

**Everything marked closed is closed by an artefact in this repository, not by an
argument.**

---

## G. The pre-submission checklist (4 items) — owner **D**

| ID | Item | Note |
|---|---|---|
| **M1** | **Run the Turnitin originality report on the department report.** | The September 2026 version scored 8% similarity; the present one is longer and more heavily rewritten, so check it rather than assuming. |
| **M2** | **Read both `.tex` papers once in a LaTeX editor.** | They compile and the build checks page budgets and line overflow, but a compile check does not catch an awkward paragraph. |
| **M3** | **Rehearse the defence** against the questions this work makes answerable: where did the corpus come from, what did the mechanism actually do, what is new, and what would you do next with more time. | The deck has speaker notes on every slide, written as what you would say. |
| **M4** | **Carry the positioning decision (D6) into the abstract, the deck's opening and the papers.** | The edit has been made; this is a confirmation and a final read, not a rewrite. |

---

## H. What is closed (19 items) — for the avoidance of doubt

These were open at some point and are closed by an artefact.

| # | What was open | Closed by |
|---|---|---|
| 1 | The contradiction detector could not be evaluated, because the first corpus contained no conflicts. | The second corpus does contain them, and the detector's precision is measured. |
| 2 | The conflict calibration was fitted on a corpus with no conflicts in it. | The regulatory profile is fitted and shipped. |
| 3 | The benchmark's unanswerable class was separable from the question text alone. | The class was rebuilt and the audit repeated on a second corpus. |
| 4 | The retrieval findings had never been measured on authentic industrial text. | The negative findings replicate on the second corpus. |
| 5 | The per-claim band had never been replicated. | It replicates on the second corpus with the same generator. |
| 6 | The first comparison of the two rubrics was confounded. | The 2×2 factorial separates them. |
| 7 | The revision corpus's pair count had no artefact behind it. | Closed 12 November 2026: `exp21_revision_corpus_stats.json` records it, and the briefing's clause was corrected. See `research/12_scope_reconciliation.md` §7 row 5. |
| 8 | The deck's length was stated wrong in both shipped documents — "19 slides" and "21 slides" against a deck of 23 — and nothing re-derived it. | Closed 12 November 2026: both numbers corrected, and `check_consistency.py` now compares the number in the prose against the number in the deck. |
| 9 | The citation audit covered only three of the shipped documents, and only arXiv identifiers — the Complete Guide was never compared with anything, and five of its identifiers and two of its DOIs were never recorded. | Closed 12 November 2026: the seven missing identifiers resolved live and were added to `research/00_citation_audit.md`, and `check_consistency.py` now checks every shipped document for both arXiv identifiers and DOIs. |
| 10 | `scripts/check_dois.py` reported four correct DOIs as broken, because it tested the publisher's landing page rather than the registration. | Closed 12 November 2026: the checker now asks doi.org for the metadata, and all thirteen of the technical report's DOIs resolve. |
| 11 | The Complete Guide stated the gate's calibration as "Brier 0.165 and ECE 0.097". The artefact says **0.1443 and 0.1143**, and no result file holds 0.165 or 0.097 for the query-level gate. | Closed 12 November 2026: the two numbers are now bound to `{{GATE_BRIER}}` and `{{GATE_ECE}}`, and `check_consistency.py` now traces every multi-digit number in the prose to a research note. See `research/17_historical_figures.md` §C. |
| 12 | **The answer-accuracy column was a report rather than a measurement** (G11 and G18): the two shipped tests disagree about which arm is best, and no convention from the literature had been applied to the shipped answers. | Closed 12 November 2026: the same shipped answers were re-scored under **five** conventions — the two shipped ones, plus SQuAD 2.0's normalised exact match and token-level F1 and PopQA's containment rule. Artefact: `impl/scripts/answer_validation_conventions.py` → `impl/results_focus/exp8_answer_validation_conventions.json`. Write-up: `research/18_answer_validation_conventions.md`. The measurement settles that no arm comparison on the answer side reaches significance under more than one convention, and that everything the gate is claimed on is computed from counts and from the evidence rather than from the answer string. |
| 13 | **The paired disagreement count between the two shipped tests was never reported** (G19), so the direct measure of how much the convention matters for a given question was missing. | Closed 12 November 2026 by the same measurement: the two shipped tests give opposite verdicts on between **21.9% and 72.7%** of the answered questions, with Cohen's κ from **−0.05 to 0.16** — at or below the agreement Cohen called "slight", and below chance in two of ten cells. They are two different measurements, not one reported two ways. The revision also found that the **ordering reversal between the two prompt conditions is a property of the system, not of the convention**: it survives three further conventions. |
| 14 | The Complete Guide's limitations table had **a row with a missing cell** — L18 carried four columns where the header has five, so its "consequence for the claims" was silently absent from the rendered table. | Closed 12 November 2026 when L18 was rewritten for the convention measurement: the row now has all five cells, and its text is bound to the `AVC_*` tokens rather than typed. |
| 15 | **The soft-prior alternative to the hard category pre-filter** was never tried (G6), although the project's own threat list (T1) had promised the repair by name. | Closed 12 November 2026: `impl/experiments/run_soft_prior.py` → `impl/results/exp22_soft_prior.json`; write-up in `research/20_soft_prior.md`. The repair **does not work**, and the negative result stands as the claim, which is what T1 said would happen if it did not. Every soft prior tested returns the no-category numbers exactly; there was nothing to recover, because not one of the corpus's gold chunks sits outside its question's category; and what the filter does buy is ordering, which a prior that only reorders cannot reproduce. The measurement also exposed **a stale sentence in three shipped conclusions** — that the filter "trades overall recall for modality precision" — which is true of neither the recall nor the modality precision on the shipped corpora, and **a backwards sentence about the modality quota** in both papers' conclusions, which said the quota binds after the reranker when the finding is that it binds before it. |
| 16 | **The gate was reported at one retriever's operating point, with the frontier as a point** (G14), and limitation L10 said so. | Closed 12 November 2026: `impl/experiments/run_gate_per_retriever.py` → `impl/results_focus/exp2b_gate_per_retriever.json`; write-up in `research/19_gate_per_retriever.md`. The shipped retriever's arm reproduces the shipped gate **exactly** (τ = 0.05, answers 0.9375, refuses 0.35417, Brier 0.14432, ECE 0.11429), which validates the re-implementation; the lexical leg fits τ = 0.10 and the dense leg τ = 0.05, and the operating points move with them. A transferred threshold is **too permissive, and too permissive in the direction that flatters the arm it is transferred to** — which corrects the direction of the thesis's earlier wording in both the papers and the deck. Each retriever's full threshold sweep and risk–coverage curve is now reported. |
| 17 | **The industrial corpus's unanswerable half had never been put through the two probes** the focus corpus's was — the question-only policy and the parametric-leakage probe (G21 and G22) — because no credential was reachable when the audit was run. | Closed 12 November 2026: `impl/experiments/audit_unanswerable_class.py` with `MTP_VARIANT=industrial`; write-up in `research/21_industrial_probes.md`. The result is the strongest version of the repair's finding: on the industrial corpus the question-only policy separates the two classes at AUC 0.478 — no discrimination at all — and refuses 70.9% of the answerable class to do it; the closed-book probe finds the generator answering substantively 95.9% of the unanswerable questions against 95.5% of the answerable ones, with the closed-book answers right only 13.8% of the time. The first attempt **failed** — the provider answered 429 after 744 requests, and the probe then crashed instead of returning what it had collected, because `_leakage` carried a copy of the question-only policy's error branch naming four variables it never defines. Both are fixed: the probe now caches its API responses to disk, so an interrupted run resumes rather than re-buying, and a rate limit waits 60 s rather than 8 s. |
| 18 | **The proposal's scope was an open decision (D1)**, with the reconciliation written but not in the thesis. | Closed 12 November 2026: option (a) taken. The twelve-category table with the reason for every row is the Complete Guide's **§A.6**, the scope statement is quoted there verbatim, the limitation is **L19** in the guide's limitations table, and the technical report, both papers, the plain-language guide, the status report and the deck's limitations slide all carry it. The deck had meanwhile said "four of the twelve categories the proposal promised" where the built count is **six**; it is now token-bound to the corpus manifest and the index. |
| 19 | **The positional comparison was listed as not replicating** on three of the four corpus-and-protocol combinations (G4). | Closed 12 November 2026: the *direction* replicates in all four. Keeping the first claims of an answer carries a higher risk than keeping the band's `grounded` claims at matched coverage in **every** measurement — +0.0923 and +0.0231 on the focus corpus, +0.0300 and +0.0315 on the industrial one — and only the largest of the four clears significance (focus gold, p = 0.008). The gap between the sign and the significance is therefore the *magnitude* and the *power*, not a disagreement in direction, and the band is reported as a filter and not as a ranking because position beats it everywhere. The residual — the magnitude, and the sample it would need — is the next-steps list's third item. |

---

## I. What the build already closes, and needs no human time

Stated so the list is not read as saying nothing is enforced. The build fails if
any of these is violated:

- Every number quoted in prose is re-derived from the result files by
  `impl/scripts/verify_reported_numbers.py`, and an unknown token fails the
  build.
- `deliverables/scripts/check_consistency.py` checks 15 required deliverables,
  reads every colour back out of 5 office files, reads every pixel of 6 figures
  and fails on a non-grey, scans 15 deliverables for null leaks, checks the
  figures' captions against the measured values, checks the next-steps list
  agrees across the report, the documentation and the deck, checks for
  duplicated counts, checks every arXiv identifier and DOI in the seven
  shipped documents against the citation audit, compares the deck's length in
  the prose against the deck, and traces every multi-digit number in the prose
  to a research note.
- `deliverables/scripts/check_slides.py` checks 23 slides for text overflow.
- `deliverables/scripts/check_latex.py` compiles both papers and fails on a page
  budget or a line overflow.
- The deck's length, as stated in the prose, is compared against the deck.
- The deliverables are monochrome, and a colour that is not a grey fails the
  build.

**Nothing on this list is in that category.** Every item above needs a
measurement, a person, a decision, or an editorial pass.

---

## A working order

The next-steps list the deliverables ship (`results_source.next_steps`) orders
by feasibility. This register orders by consequence. Here is the honest merge —
what could actually be closed before 18 November, and what could not.

**Closable before the defence (a day or less each, and no supervisor needed):**

| Order | ID | Why it is worth doing |
|---|---|---|
| 1 | ~~**G19**~~ | **Closed 12 November 2026** — see §H row 13. |
| 2 | ~~**G18**~~ | **Closed 12 November 2026** — see §H row 12. |
| 3 | ~~**G21, G22**~~ | **Closed 12 November 2026** — see §H row 17. |
| 4 | ~~**G6**~~ | **Closed 12 November 2026** — see §H row 15. |
| 5 | ~~**G14**~~ | **Closed 12 November 2026** — see §H row 16. |
| 6 | **M1–M4** | The pre-submission checklist. |

**Closable in the defence window but needing the supervisor or a person:**

| Order | ID | Needs |
|---|---|---|
| 7 | ~~**D1**~~ | **Closed 12 November 2026** — option (a) taken and folded into the deliverables. |
| 8 | **G15** | A person reading the repaired unanswerable class against the corpus, on both corpora. |
| 9 | **G16, G17** | Human double annotation of a benchmark sample. This is the largest open item, and it is also the one that would move the thesis's weakest part. |

**Not closable before the defence, and honestly so:**

| ID | Why |
|---|---|
| **G1, G12** | Human annotators, against a rubric that must be fixed first. |
| **G2, G5** | Another jurisdiction; a plant's own documents. |
| **L3, L4, L5** | The proprietary corpus cannot be redistributed; the practitioner study needs power a 16-participant pilot cannot give. |
| **G3, G9, G10, G20** | Each is one run away, but each needs compute or a working generator, and the second-generator obstacle is a property of the generator, not of the harness. |
| **~~G4~~, G7, G8, G13** | **G4 is closed** — see §H row 19; its residual (the magnitude, and the power it needs) is the next-steps list's third item. G7, G8 and G13 are real experiments with real designs, and they are in the next-steps list, which is where the register said they already were. |

**The point of the register.** Nothing above is a loose end, and none of it is
hidden in a deliverable. The thesis's own result is that three of its design
assumptions were wrong and it says so in the abstract; the limitations and gaps
above are written down in the same place, in the same voice, with the same
artefacts behind them. A panel that reads the limitations table and then reads
the next-steps list should find that they are the same list.
