# Supervisor briefing — 11 November 2026

**For:** Dr. Sri Krishna Kumar
**From:** Ritik Raj (25IM60R12)
**Re:** Closing RO4, RO5 and RO6 — an authentic industrial corpus, and what it says about the framework
**Defence:** 18 November 2026 (7 days)

---

## 1. Where the thesis stands

Six research objectives. Four were closed with measured evidence before this
work. **All three that were open are now closed**, and the closures come
with two uncomfortable results and one that strengthens the thesis.

The uncomfortable ones: **two of the five mechanisms do not do what the
thesis says they do.** The contradiction gate detects *supersession* and
reports it as contradiction; the per-claim confidence band is a usable
*filter* and not a usable *ranking*. Both were measurable before; both are
now measured properly.

---

## 2. What I did this week

**The idea that unlocked two objectives at once.** RO4 needed a corpus that
*contains* conflicts. RO6 needed a corpus that is *authentic*. Federal
regulations are both: they are real industrial documents with binding
numeric requirements, and they get amended — so the same section read on
two dates is the same rule at two issues. One artefact supplied both.

**What was built:**

| | |
|---|---|
| **Corpus** | 110 documents, 2,443 chunks, four regulatory regimes, from the eCFR (public domain) |
| **Benchmark** | 444 queries — 247 answerable, 197 unanswerable — with its own shortcut audit |
| **Revision corpus** | the same regulations read at 2021-12-31 and 2026-06-01; **948 amended-paragraph pairs**, of which 361 state different numbers |
| **Annotation** | **a panel of domain specialists** — one per regulatory regime, plus a generalist control and an adjudicator — all blind to the framework's own scoring code |

**On the annotation.** You said no human annotators; the panel replaces them.
Four specialists (OSHA general industry, process safety, environmental
control, DOT hazmat), a generalist control, and an adjudicator for the pairs
the readers disputed. Two of the specialists verified their calls against the
eCFR's point-in-time API rather than reading alone. **The agreement is
reported in full, and it turned out to matter more than the specialisation.**

---

## 3. "Where did you take the dataset from?"

**The Electronic Code of Federal Regulations (eCFR)** — the official US
federal regulations, at `ecfr.gov`.

* **Which parts.** 29 CFR 1910 (OSHA general industry), 40 CFR 60 (EPA
  new source performance standards), 40 CFR 112 (EPA risk management
  programmes), 49 CFR 173 (DOT hazardous materials).
* **Which date.** The versioner serves any regulation *as it stood on any
  past date*. The corpus is the 2026-06-01 snapshot; the revision corpus
  pairs 2021-12-31 with 2026-06-01.
* **Licence.** Public domain — US federal regulations are works of the US
  government. The corpus ships with the thesis with no licence question,
  which matters because the thesis's own limitation table names "a licensed,
  multi-domain industrial corpus" as the remediation it needed.
* **Reproducibility.** `impl/scripts/fetch_ecfr.py` is the only thing
  between the URL and the corpus; the raw XML is cached and the build is
  deterministic.

**Why this and not a plant dataset.** Real manufacturing corpora are
proprietary and non-redistributable. The eCFR is authentic *regulatory*
text — the class of document the thesis said it lacked ("not the operating
manuals, control plans and supplier specifications a practitioner actually
uses") — it is redistributable, and it carries version history, which is
what RO4 needed.

---

## 4. The results

### 4.1 RO6 — the thesis's negative findings replicate on authentic text

247 answerable queries, paired Wilcoxon tests, bootstrap CI [0.972, 1.000]
for Recall@10.

| Finding | Δ Recall@10 | p |
|---|---|---|
| **BM25 beats the dense encoder** | −0.081 | **0.00026** |
| Fusion **does not** beat its lexical leg | 0.000 | 1.000 |
| The **category pre-filter is a no-op** | 0.000 | 1.000 |
| The reranker **helps here** (it hurt on Wikipedia) | +0.028 | 0.020 |
| The **quota belongs after** the reranker | — | 0.038 (MRR) |

The BM25 result is the important one *for this pipeline*: on the focus corpus
it rested on 32 answerable queries at p = 0.025; on authentic regulatory
documents with 247 queries it is three times the effect size and twenty-five
times the significance, so **it was not an artefact of a small encyclopaedic
sample**. Two things about it, stated plainly because a literature check
found them. First, that lexical retrieval beats a general-purpose dense
encoder on legal and financial text is **already published** — three times,
in three jurisdictions — so it must not be claimed as new, and it is not in
this thesis's abstract. What is new is the *corollary*: on this corpus the
lexical leg carried the pipeline and **neither the fusion nor the category
pre-filter added anything measurable on top of it** (Δ 0.000, p = 1.000 each).
Second, the dense leg here is a 2022 general-purpose sentence encoder and a
domain-adapted encoder can overtake BM25, so this is a statement about this
pipeline, not about dense retrieval.

**The lead claim got sharper.** The candidate-pool sweep on the focus corpus
was saturated (Recall@10 = 1.000 at pool 10), so its "peaks then declines"
shape could not distinguish "the pool stopped helping" from "the corpus had
nothing left to find". The industrial corpus is not saturated:

| Pool | R@10 | R@20 | Displaced (R@20 − R@10) |
|---|---|---|---|
| 10 | 0.980 | 0.980 | 0.0000 |
| 20 | 0.988 | 0.992 | 0.0040 |
| 50 | 0.988 | **1.000** | **0.0121** |

At pool 50 the gold chunk is in the reranked top-20 for *every* query, and
1.21% of them are then pushed **out of the ten-chunk context** by
distractors. The displacement is now measured directly rather than inferred.

**The gate.** At τ = 0.40: 91.5% of answerable answered, 58.9% of
unanswerable refused, abstention precision 0.847, coverage 0.691, with both
degenerate baselines reported. The threshold does **not** transfer across
corpora (0.40 here against 0.05 on the focus corpus) but the **operating
point** does (coverage 0.691 against 0.699).

### 4.2 RO4 — it finds the conflicts and reports them as the wrong kind

240 pairs, two independent readings of the rubric plus the panel.

| | Value |
|---|---|
| **Detection precision** (is there something there) | **0.659** (CI 0.505–0.784) |
| …on the stratum where the conflicts actually are | **0.897** |
| **Typing precision** (is it typed correctly) | **0.073** (CI 0.025–0.194) |
| Quantity branch, recall on 35 limit changes | **0.000** |
| Quantity branch, on 1,776 cross-document candidates | **0 confirmed** of 13 alarms |
| Revision branch, recall on 55 supersessions | **0.000** |

So the mechanism **finds** the conflicts and **reports them as
contradictions** when they are supersessions — and it cannot say which
version is in force, because nothing in the retrieved passages says which
issue either of them is. That is the one thing a practitioner needs from a
contradiction detector on a regulatory corpus, and it is exactly what the
mechanism does not deliver.

The quantity branch has nothing to fire on: OSHA harmonised its
construction and general-industry limits for asbestos, cadmium, lead and
silica, so the same substance carries the same limit in both, and 58 of 60
cross-document pairs a specialist reviewed turned out to be the same word
used for different things.

**And the annotation was the binding constraint — and now it is measured
rather than asserted.** The first comparison was confounded: the old-rubric
reader was a generalist, so "old rubric" and "generalist" were the same cell.
A 2×2 factorial separates them, with the pairs, the detector and the regime
briefs held constant:

| Cell | rubric | detection precision | typing precision |
|---|---|---|---|
| generalist | old (marker test) | 0.293 | 0.073 |
| generalist | sharpened (structural test) | **0.659** | 0.073 |
| specialist | old (marker test) | 0.341 | 0.073 |
| specialist | sharpened (structural test) | **0.659** | 0.073 |

**The rubric's wording moved the measured precision by 0.32–0.37. The
reader's domain specialisation moved it by at most 0.049, and by 0.000 on the
rubric this thesis reports.** The mechanism is concrete: the old rubric
required a version marker, and a regulation does not write its own version in
its text, so it missed **63 of the 82 supersessions** it was asked to find,
calling them `no_conflict` rather than something else.

Two things I want to be careful about. The rubric changed the *definition* of
the target as well as the *procedure* for recognising one, and this
experiment cannot separate those two — both are rubric-level, and what it
shows is that the reader factor is small. And "specialisation" here was
delivered as a brief to a fixed reader model, not as a different capability;
the qualitative form of this finding is already published, so what is new is
that **the specification of the task moved the measured precision of an
unchanged detector by a factor of nine**.

### 4.3 RO5 — a filter, not a ranking

350 claims, two readers (κ = 0.902) plus an adjudicator; 347 carry a
reference.

| | Gold evidence ("is the claim right?") | Retrieved evidence ("does a reader agree with the scorer?") |
|---|---|---|
| Band vs reference (κ) | **0.049** (CI −0.026, 0.124) | 0.069 (CI −0.002, 0.139) |
| `grounded` / `inferred` / `uncertain` error | 0.542 / 0.513 / 0.610 | **0.118 / 0.103 / 0.220** |
| Answers with no wrong claim → keeping only `grounded` | 34.4% → **50.0%** | 59.4% → **81.2%** |

**Against the benchmark's own gold evidence the band does not track
correctness at all** (κ = 0.049, CI −0.026 to 0.124; the three bands are
0.542 / 0.513 / 0.610 and are indistinguishable), while against the evidence
it saw, the bands are ordered (0.118 / 0.103 / 0.220).

The sharper way to put the finding is: **the band measures whether the
retrieved passages entail the claim — that is, agreement with itself — not
whether the claim is true.** The positional comparison is the evidence for
that, not the finding itself: "read the first half" beats "read what the
framework tagged grounded" on the gold protocol (p = 0.008, and not a length
artefact — later claims are *shorter*, Spearman −0.195, p = 0.0003), but it
**did not replicate**: of the two corpora and two protocols, only the focus
corpus's gold evidence gives a significant positional result (the other three:
p = 0.417, p = 0.083 and p = 0.317). So I report it as evidence rather than
as the claim.

**What does replicate is the finding itself.** On the industrial corpus, with
the *same generator* that produced the focus corpus's answers, the band is
again at chance against an independent reference (κ 0.062 and 0.044 on the two
protocols, both intervals including zero) and again ordered on the evidence
it saw (a `grounded` claim wrong 6.9% of the time, an `uncertain` one 15.6%).
Two corpora, two protocols, one generator, the same answer.

Three readers independently found the same generator defect: claims of the
form `Preferred Provider | 4` carry the number the passage assigns to the
*next* item — an off-by-one in reading ordered lists.

### 4.4 What is new, and what is not

I ran a novelty check against the 2026 literature before writing this, and it
changed some of what I would have said. Reporting it here rather than
letting you find it:

| Finding | Status | What I can claim |
|---|---|---|
| A conflict detector's precision **decomposes into detection and typing** | **Not published** | Two metrics instead of one; they are nine-fold apart; a branch with recall 0.000 where conflict provably exists |
| The per-claim band **measures agreement with itself, not correctness** | The filter result is published; the informative-vs-agreement decomposition is not | The band is ordered on the evidence it saw and indistinguishable on an independent reference |
| **Rubric design vs reader specialisation** | The qualitative principle is published; the factor-of-nine is not | The specification of the task moved the measured precision of an unchanged detector by a factor of nine |
| **Point-in-time regulatory corpora** as a source of labelled conflicts | The *method* is published (NitiBench+, ICAIL 2026); the *purpose* is not | I applied a published corpus-construction method to conflict detection, and the detector that consumed it finds the conflicts and cannot type them |
| **BM25 beats the dense encoder** on regulatory text | **Already published**, three times over | Only the pipeline corollary: the lexical leg carried the pipeline and the fusion and pre-filter added nothing on top of it |

Two consequences. The BM25 result must not appear in the abstract, and I
have not put it there. And **the spine of the thesis is the detection/typing
decomposition** — the clearest new thing in it — with the rubric factorial as
a methodological result that belongs in an evaluation section rather than in a
contribution list. The full check, with every identifier resolved against a
live registry, is in `research/13_novelty_and_positioning.md`.

---

## 5. Two defects I found in my own earlier experiments

Worth reporting because the thesis's audit discipline is the strongest thing
about it, and because one of them changes a number already in the
deliverables.

1. **The cross-category transfer experiment had no negative class.** The
   unanswerable queries carry no category, so splitting *by category* dropped
   them out of both halves. The shipped six-category result has
   `n_unanswerable: 0` and `unanswerable_refused: NaN` in every split — the
   experiment was measuring only how many true answers get refused. Fixed:
   the shared negative class now goes into both halves. **The deliverables
   have been rebuilt** and the consistency checker passes; Table 6 now
   carries 0.174 and 0.215 where it had `NaN`.
2. **The per-claim band and the reported claim-support rate are different
   functions of the same evidence** — a noisy-OR (what the answer ships)
   against a maximum (what the papers report). They disagree on 23 of 350
   claims, and the reported "claim hallucination rate" of 0.382 is a measure
   of *entailment* presented as a measure of *hallucination*: two
   independent estimates bracket it at 0.164 and 0.571.

**Nothing already in the deliverables is contradicted by the new work.** The
thesis's own limitation table said the contradiction gate "cannot be
evaluated on this corpus" and named the remediation: "a corpus that contains
contradictions to find, which means revised procedures rather than articles
about concepts". That is exactly what I built. The thesis's calibration
already withheld every finding at 0% precision; on the new corpus the
calibration would surface them — correctly, because they *are* real
conflicts.

---

## 6. What I changed in the framework

Ten changes, all default-off or behaviour-preserving, so the shipped numbers
are unchanged **by construction** — and confirmed unchanged **by
measurement**: the focus corpus's `exp3_contradiction.json` reproduces
bit-identically and all 32 tests pass. The substance: a configurable
measurement-key look-back, selectable regulatory measurement and version
vocabularies, an instance-identifier rule, a shared negative class in the
transfer split, batched entailment, and three statistical corrections (a
cluster bootstrap over answers, a majority rather than unanimity consensus,
and a per-branch recall that was silently computing nothing).

---

## 7. What I need from you

1. **Does the industrial corpus become a second corpus (a generalisation
   section) or the primary one?** This is the biggest structural question
   and it changes the abstract. My recommendation: keep the focus corpus as
   primary (it carries the pre-registered measurements) and add the
   industrial corpus as the external-validity section — but if you want the
   thesis framed around "what a practitioner actually reads", the framing
   changes and I would need to re-order the report.
2. **How should the model annotators be disclosed?** The thesis already
   discloses that the Experiment 11 annotators were models, and the panel
   makes that disclosure apply to the two heaviest measurements. My
   recommendation: keep it in the limitations table with the agreement
   statistics beside it, rather than presenting it as human annotation.
3. **The proposal's scope.** It promised twelve categories spanning
   industrial engineering, machine learning and data analytics; I have 110
   documents in four *regulatory* regimes. Do you want (a) a scope-
   reconciliation table stating plainly what was descoped and why, (b) an
   extension into the machine-learning and data-analytics categories, or
   (c) a re-reading of the proposal's wording as "industrial sub-domains",
   the way the thesis already re-reads the cross-category transfer claim as
   intra-domain? **(a) is written and ready** —
   `research/12_scope_reconciliation.md`.
4. **Where the thesis should lead.** The novelty check says the
   detection/typing decomposition is the only clearly new *result*, and that
   the BM25 result is already published and must not lead. Do you want the
   abstract and the defence to lead with the decomposition and the rubric
   factorial, with the BM25 replication demoted to the ablation table? I have
   made that edit already; I am asking because it changes what the panel
   hears first, and because it is your thesis.
5. **The one remaining methodological worry.** "Specialisation" in the RO4
   factorial was delivered as a *brief* to a fixed reader model, not as a
   different capability — so the factorial shows that a brief plus a sharpened
   rubric buys nothing over the rubric alone, which is a narrower claim than
   "specialists are not needed". Do you want that narrowed wording kept, or
   should I run a stronger version with genuinely different reader models?

---

## 8. What I will do next, in order

1. ~~Write the scope-reconciliation table~~ — done:
   `research/12_scope_reconciliation.md`.
2. ~~Re-run the deliverable checks end-to-end and re-verify every quoted
   number against the result files~~ — done, and it found five wrong numbers
   in my own write-up, which are now fixed. The verification script now lives
   in the repository at `impl/scripts/verify_reported_numbers.py` rather than
   in `/tmp`, where a reboot would have destroyed it.
3. **Rehearse the defence** against the questions this work makes answerable:
   where did the corpus come from, what did the mechanism actually do, what
   is new, and what would you do next with more time.
4. **Decide the positioning** (question 4 above) and carry it into the
   abstract, the deck's opening and the papers.

**Everything in §4 is written up in full, with every number, in
`research/10_industrial_corpus_and_objectives.md`.**

---

## Correction, 12 November 2026

One number in the table in §2 changed after this briefing was written. It read
"**948 amended-paragraph pairs, of which 35 change a limit**". The 35 was
counted on the 240-pair sheet the RO4 evaluation scored — 90 revision-stratum
pairs and 150 retriever-neighbour pairs, of which 35 change a quantity and 55
are supersessions by construction — and was read as a count against the 948.
The correct count against the 948 is **361, or 38.1%**, and it is what the
deliverables already print: `impl/results_industrial/exp21_revision_corpus_stats.json`
records `n_amended_paragraph_pairs = 948` and
`n_pairs_stating_different_numbers = 361`. The row now reads 361.
