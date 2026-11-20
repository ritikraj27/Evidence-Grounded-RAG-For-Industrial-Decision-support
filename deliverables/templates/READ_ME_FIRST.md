# How to use each deliverable

A short, practical guide. Everything here is a suggestion, not a prescription;
know which parts you can defend cold and which you are going to rehearse.

---

## The order to read them in

| If you have | Read |
|---|---|
| 30 minutes before you walk in | `Deliverable_1_PartJ` — the one-page glossary (Part J of the guide) |
| 2 hours | Part G of the guide (the viva questions and answers), then Part A (the five-minute version) |
| A full evening | Parts A, C, E, F, H of the guide, in that order |
| A week | Everything, plus the paper (Deliverable 2a) and the report (Deliverable 3) |
| Never read any of it | `MTP_Plain_Language_Guide.pdf` — the whole thesis in ordinary words, as one document. Start here if a term is unfamiliar. |

**If you read only one thing, read Part H** — the limitations. A panel trusts a
candidate who volunteers their own weaknesses before being asked. Every claim in
this work is framed so that Part H is the reason it survives scrutiny.

---

## The three sentences to have ready

You will be asked to summarise. These are the answers, and they are the ones the
deliverables are built around:

1. **What is it?** An evidence-grounded RAG framework for industrial decision
   support in which a code-level, non-bypassable confidence gate, a
   modality-balanced retrieval quota, and per-claim confidence tags work
   together with hybrid retrieval and contradiction surfacing.

2. **What did you find?** Three things that contradict the framework's original
   specification: a reranker's recall is governed by its candidate pool
   relative to the final context; a retrieval quota binds only when it is
   enforced *before* the component that could undo it, not after; and the
   modality composition of the corpus, not the retrieval algorithm, determines
   whether a modality-aware mechanism can have any effect at all.

3. **What is new?** Not the architecture — every component has published prior
   art, and the deliverables position each against it. The contribution is a
   failure-mode characterisation and an evaluation protocol that treats the
   confidence gate as a selective-prediction policy.

---

## If you are asked "how do you know your benchmark is valid?"

This is the question to expect, and the answer is that **we audited our own
benchmark and found a serious defect in it, then repaired it and re-measured
everything.** The unanswerable half of the benchmark — the half on which a
refusal benchmark lives or dies — was separable from the question text alone:
a classifier given only the question told answerable from unanswerable at an
ROC AUC of {{UNANS_BEFORE_AUC}}, and one regular expression caught
{{UNANS_SHORTCUT_BEFORE}} of the unanswerable class with no false positives,
because the class's hard case asked about a fabricated identifier
(`SKU AST-5454`) and no answerable question ever named one.

The half was rebuilt as a **corpus-anchored** class: the same question stems,
the same source documents, the same label machinery, and each repaired
question given a *structural twin* in the answerable class
; {{UNANS_MATCH_RATE}} have one. Re-measured, the shape-only
classifier scores {{UNANS_SEP_AUC}} against a permutation null of
{{UNANS_SEP_NULL}}, and the one-rule shortcut carries {{UNANS_SHORTCUT_AFTER}}.
The benchmark as it stood before the repair is kept so the finding stays
checkable.

The honest cost, which you should say plainly: the gate now refuses
{{UNANS_HARD_REFUSED_PCT}} of the corpus-anchored unanswerable questions
({{UNANS_HARD_REFUSED_N}}) rather than the much larger fraction the defective
benchmark produced. The detection problem is harder than the first benchmark
made it look. The repair is what showed it, and a defensible number is worth
more than a flattering one.

---

## Rehearsing the presentation

The deck has **speaker notes on every slide** — read them, they are written as
what you would say, not as reminders.

- **Slide 2** (the 66% figure) — the single most persuasive number you have.
  Memorise the sentence: *"Twenty points lost to confidently answering
  questions that have no answer, in a purely general-domain setting, with no
  industrial content at all."*
- **Slide 12** (the ablation table) — you do not need to memorise the table.
  You need to know that the last two columns are the paired Wilcoxon tests
  between adjacent rungs, and that adjacent rungs isolate one mechanism each.
- **Slide 13** (the three findings) — this is the slide the panel will
  interrogate. Be ready to say "a constraint on a downstream artefact must be
  enforced where it can still choose the candidates, not where it must work
  against another component's judgement" without hesitation. It is the one
  generalisable lesson in the project.
- {{GEN_RMF_SLIDE16}}

**The three questions you will definitely get:**

*"Why not just put the whole corpus in the prompt?"* — {{GEN_RMF_LC_ANSWER}}

*"Did you actually show that you reduced hallucination?"* — Say the precise
thing first: **H2.1 is {{GEN_H2_1_SHORT}}.** {{GEN_H2_1_ANTICIPATED}} A refusal rate and a
hallucination rate on generated text are different quantities, and you are not
going to present one as the other. {{GEN_RMF_PENDING}}

*"Is this better than conformal prediction?"* — No, and you do not claim it is.
Conformal prediction has a finite-sample guarantee and you have an empirical
calibration. Your answer is that the guarantee does not survive the corpus you
have: Geißler et al. (2026) concede exchangeability depends on the retriever
setup, and a single-category industrial corpus is exactly such a setup. You
adopt their diagnostic as your limitation and claim a different property — an
auditable refusal that names the score and the threshold.

---

## If you are asked "what would you do next?"

Say these, in this order, and saying so is a strength.

{{NEXT_STEPS_SHORT_LIST}}

The full text of each is in the guide's next-steps section and it is the same
list the defence deck shows, so nothing here can be a different list from the
one you will be asked about.

---

## Two things to do before you submit anything

**Run the Turnitin originality report on the department report** before you
hand it in. The September 2026 version scored 8% similarity; the present one
is longer and more heavily rewritten, so check it rather than assuming.

**The .tex papers compile, and the build checks it.** `pdflatex` is available on
this machine, so `deliverables/scripts/build_all.py` compiles both papers and
fails if either does not, if the conference paper exceeds its page budget, or
if a line overflows. The current state: the IEEE conference paper is **13
pages** and the journal paper is **31 pages**, both with the industrial
corpus's results and the six figures. The conference paper's budget was
raised from 10 to 13 with the reason recorded in
`deliverables/scripts/check_latex.py`, and it is the supervisor's to reverse.
Read both once in a LaTeX editor anyway, because a compile check does not
catch an awkward paragraph.

---

## Where everything is

```
deliverables/
├── Deliverable_1_Complete_Guide.md / .docx      the teaching guide (10 parts)
├── Deliverable_1_Part1_Content.md               source: Parts A–C
├── Deliverable_1_PartD_Code.md                  source: Part D
├── Deliverable_1_PartE_Results.md               generated from the measurements
├── Deliverable_1_PartF_toJ.md                   source: Parts F–J
├── Deliverable_2a_Technical_Report.md / .docx    paper, single-column
├── Deliverable_2b_IEEE_Conference_Paper.tex      paper, IEEE two-column
├── Deliverable_2c_Journal_Style_Paper.tex       paper, Elsevier/Scopus style
├── Deliverable_3_Department_Report.docx         the department submission
├── Deliverable_4_Presentation_18Nov.pptx        23 slides, notes on every one
├── MTP_Report.md / .docx / .pdf                the project report, written fresh (32 pages, with the title and certificate pages)
├── MTP_Report_Presentation.pptx                the report deck, written fresh (38 slides)
├── MTP_Plain_Language_Guide.md / .docx / .pdf   the whole work in ordinary words
├── dataset/                                     the evaluation corpus, with provenance
│   ├── README.md                                    source, licence, per-document table
│   ├── manifest.json                                URL, revision id, SHA-256, chunk count
│   ├── documents/<category>/*.md                     the documents themselves
│   └── benchmark.json                                the questions that interrogate them
├── templates/                                   pristine tokenised sources
└── scripts/                                     everything that generates the above
```

To regenerate every deliverable after changing anything:

```bash
.venv/bin/python deliverables/scripts/build_all.py
```

The build restores the pristine sources, substitutes the measured values into the
prose, rewrites the results sections from the experiment JSON, rebuilds the
documents, exports the dataset with its provenance, and then runs two checks: a
consistency check (numbers in prose against the measurements, citations against the
audit, corpus integrity, files present) and a slide-layout check (text overflow).
Both fail the build if something is wrong.

---

## The dataset, in one paragraph

Two corpora are in play and they are not the same thing. The **primary corpus**
of the original project specification was 634 chunks across 24 proprietary
supply-chain documents; it cannot be redistributed, so it cannot be shipped with
this work or re-run by a reader. Everything measured here was measured on a
**public substitute**: industrial-engineering articles from English Wikipedia,
fetched through the MediaWiki API, several categories, with real tables and
figures so the modality mechanisms have something to act on.

It ships in full, in `deliverables/dataset/`. For every document the manifest
gives the Wikipedia URL, the upstream revision it was read at, the SHA-256 of
the exact bytes used, and its chunk count. Licence: CC BY-SA 4.0 for the article
text.

The thesis focuses on **supply chain management** — the domain the primary
corpus covered and the one the practitioner scenarios come from. Part E of the
guide traces real questions from that domain end to end: what the plain keyword
retriever returned, what the full framework returned instead, what the gate
decided and on which signals, and how every claim in the answer was banded.

If a panel member asks "where did the data come from?", the answer is on slide
11 of the deck, in §9.0 of the department report, in §A.5 of the guide, and in
`deliverables/dataset/README.md` — all four say the same thing, because all
four are generated from the same manifest.

## The long-context baseline, and what it did and did not settle

This was the biggest threat to the work: the corpus fits in a modern context
window, so a reader given everything might answer the question directly and
the retrieval machinery would be unnecessary. It is now measured on the half
that does not need a generator.

| | Focus domain | Six-category corpus |
|---|---|---|
| The whole corpus, as a prompt | {{LC_CORPUS_TOKENS}} tokens | {{MC_LC_CORPUS_TOKENS}} tokens |
| The RAG arm's accepted context | {{LC_RAG_TOKENS}} tokens ({{LC_RAG_CHUNKS}} chunks) | {{MC_LC_RAG_TOKENS}} tokens |
| **Cost ratio** | **{{LC_RATIO}}×** | **{{MC_LC_RATIO}}×** |
| The RAG arm's share of the corpus | {{LC_CORPUS_FRACTION}}% | — |
| Fits a 128K window | {{LC_FITS_128K}} | {{MC_LC_FITS_128K}} |

And a retrieval-side proxy: with the candidate set widened from the fused
shortlist to *every* chunk in the corpus, the gold chunk still lands in the
scorer's top 10 for {{LC_PROXY_TOP10}} of focus-domain queries (95% interval
{{LC_PROXY_CI}}) at a median rank of {{LC_PROXY_MEDIAN_RANK}}.{{MC_LC_PROXY_CLAUSE}}
The evidence does not get lost in
a big context — but the focus corpus is {{LC_CORPUS_VS_128K}}× the size of a
128K window, and the RAG arm reaches the same evidence using
{{LC_CORPUS_FRACTION}}% of what the long-context arm reads.

**The answer-quality half is now measured.** {{GEN_LC_FINDING}}

**The same gap decides H2.1, and it is settled in the same honest way.** A
second harness (`impl/experiments/run_generation_eval.py`) puts
{{GEN2_GENERATORS_PHRASE}} behind five arms — the same retrieval with the gate removed, the framework at
its fitted operating point, **a random-escalation control that refuses the same
number of questions and picks them at random**, the framework at the operating
point transferred unchanged from the cross-category half, and the whole corpus
in the prompt — under **two prompt instructions that differ by one sentence**
(the generator may decline, or the generator must answer). It scores every
claim each arm produces against the evidence that arm was given.
The scorer is audited before any of it is read: {{GEN_SCORER_TRUTH}}, and
{{GEN_SCORER_FAB}}. The comparison {{GEN_TEST_STATUS}}. The answer to *"did you
show that the gate reduces hallucination?"* is **{{GEN_H2_1_SHORT}}**:
{{GEN_H2_1_DETAIL}}.

The replication on a second generator could not be run, and the reason is
measured rather than guessed: {{GENCOMP_CLAIM}}

---

## One last thing

The work in this repository was produced by measuring things rather than
asserting them, and the results include three null or negative findings that
contradict the original design. That is not a weakness to be managed in the
presentation — it is the most defensible thing about the work, because it is
the evidence that the numbers mean something. A framework whose components all
"work" on the first try has usually been evaluated on something that was
arranged to work.

Be ready to say so, plainly, when the panel asks whether the results were
positive.
