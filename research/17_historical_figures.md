# 17 — The figures with no artefact behind them

**Written:** 12 November 2026, while auditing the deliverables for evidence.

Every number the deliverables quote about **this project's own measurements**
is bound to a result file by a `{{TOKEN}}`, and
`impl/scripts/verify_reported_numbers.py` re-derives it from the artefact.
Every number they quote about **other people's work** is recorded in a
research note where the source was resolved and read.

A small set of numbers is neither, and this note is where they are recorded.

---

## A. Measurements of implementations this project has since replaced

| Figure | What it was | Where it is quoted | Why it is quoted |
|---|---|---|---|
| **β₀ = −2.88, β₁ = 0.27** | The coefficients of the *chunk-level* gate calibration — the first implementation, which asked the wrong question ("is this candidate the gold chunk?" instead of "can this query be answered?") | `Deliverable_1_Part1_Content.md`, `Deliverable_1_PartD_Code.md`, `Deliverable_1_PartF_toJ.md` | They are the evidence for the most useful bug in the project: with a base rate near 2%, maximum likelihood returns a large negative intercept and a nearly flat slope, and that looks like a finding until you notice it is a badly posed question. |
| **Brier 0.011, ECE 0.004** | The same chunk-level model's calibration quality — which was *excellent-looking* for exactly the wrong reason: it measured the base rate, not the decision. | `Deliverable_1_PartD_Code.md`, `README.md` | They are the point of the anecdote: the numbers looked good and meant nothing. |
| **the implied operating point refused 46% of the answerable questions** | The same chunk-level model's operating point. | `Deliverable_1_Part1_Content.md`, `Deliverable_1_PartD_Code.md`, `Deliverable_1_PartF_toJ.md`, `README.md` | The visible cost of the mis-posed question. |
| **table recall 0.906 → 0.469** | The *rebuild-based* modality quota — the first implementation, whose victim-selection condition was inverted, evicting the modalities that were *at* their floor | `Deliverable_1_Part1_Content.md`, `Deliverable_1_PartD_Code.md` | It is the evidence for the rule the thesis generalises: *a result that contradicts the mechanism you believe is a bug report, not a finding.* |
| **table recall 0.865 → 0.649** | The same rebuild-based quota, measured on the September 2026 corpus | `MTP_Technical_Documentation.md` | The same story, told where the algorithm is described. |

**Why they cannot be re-derived.** The implementations they describe have been
replaced. The quota is now swap-based, and the gate is now a query-level
decision, so none of these figures is reachable from the current code or from
any result file. The git history that would have them was not kept.

**What is done about it.** They are recorded here, and the build's number-
provenance check treats this note as a provenance source: a multi-digit number
in the shipped prose must appear in a research note or in this one. These
figures are the only exceptions, and they are the only ones because they are
the only ones with no artefact.

**What a reader should take from them.** They are not measurements the thesis
leans on. They are illustrations of two mistakes the project made and fixed,
and both mistakes are pinned by regression tests that still run
(`impl/tests/test_hybrid.py` for the quota; the gate's query-level unit tests
for the calibration). The measurements the thesis *does* lean on are all
token-bound.

---

## B. A figure quoted from another paper

| Figure | Source | Where it is quoted |
|---|---|---|
| **+0.368 MiB**, the cost of a memory tier | RADIANT-LLM — arXiv:2604.22755, *RADIANT-LLM: an Agentic Retrieval Augmented Generation Framework for Reliable Decision Support in Safety-Critical Nuclear Engineering* | `Deliverable_1_PartF_toJ.md` |

The identifier is on the record in `research/00_citation_audit.md` and
`research/01_citation_resolution.md`, both resolved live. The figure itself was
written into the prose by hand from the paper, and no note recorded it; this
note does now, and the provenance check reads it from here.

---

## C. The number that was wrong, and what it should have been

While building this check, one number was found that was not merely
unbacked but **incorrect**:

> `Deliverable_1_PartD_Code.md` said "Recalibrating at the query level gave
> Brier **0.165** and ECE **0.097**."

The shipped gate's calibration is in `impl/results_focus/exp2_gate.json`:
**Brier 0.1443, ECE 0.1143**. No result file in the repository holds 0.165 or
0.097 for the query-level gate — the pre-repair gate had Brier 0.0642 and ECE
0.0615, and the industrial gate has Brier 0.1587 and ECE 0.0749. The figure
was typed into the prose by hand instead of being bound to a token, and it had
drifted.

It is now bound: the sentence reads `{{GATE_BRIER}}` and `{{GATE_ECE}}`, the
same tokens every other deliverable uses, so it cannot drift again. **This is
the argument for the provenance check in one incident**: every number that is
not bound to a token is a number that can be wrong and stay wrong, and this
one was.
