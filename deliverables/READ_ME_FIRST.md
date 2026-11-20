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
ROC AUC of 0.999, and one regular expression caught 76.4% of the unanswerable class with no false positives,
because the class's hard case asked about a fabricated identifier
(`SKU AST-5454`) and no answerable question ever named one.

The half was rebuilt as a **corpus-anchored** class: the same question stems,
the same source documents, the same label machinery, and each repaired
question given a *structural twin* in the answerable class
; 106 of 110 have one. Re-measured, the shape-only
classifier scores 0.608 against a permutation null of 0.468, and the one-rule shortcut carries 0.0%.
The benchmark as it stood before the repair is kept so the finding stays
checkable.

The honest cost, which you should say plainly: the gate now refuses 23.6% of the corpus-anchored unanswerable questions
(26 of 110) rather than the much larger fraction the defective
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
- **Slide 16** (limitations) — do not rush it. You are conceding that the gate's contribution depends on the generator behind it, that the long-context baseline you raised as the biggest threat to your own work does not beat you on this corpus, and that your own benchmark carried a label defect you found by auditing it and repaired. Conceding all three is what makes the rest credible.

**The three questions you will definitely get:**

*"Why not just put the whole corpus in the prompt?"* — You can, and you measured it. On this corpus the whole-corpus prompt answered the same number of answerable questions as the pipeline, declined no more of the unanswerable ones, and cost many times the input. You do not claim long context is worse in general; you claim that on this corpus it did not win, that the quality margin is directional rather than statistically significant once the answers are scored without the length confound, and that the evidence trail, the per-claim auditability and the category routing are properties your system has and a long-context prompt does not.

*"Did you actually show that you reduced hallucination?"* — Say the precise
thing first: **H2.1 is supported under both prompt conditions.** What the generator-side comparison showed is that the gate's contribution does not depend on the generator's willingness to decline -- the hypothesis is supported under both prompt conditions. What the framework claims is that the gate is the one component whose behaviour does not depend on the generator's cooperation: the prompt can be wrong, and the gate still holds. A refusal rate and a
hallucination rate on generated text are different quantities, and you are not
going to present one as the other. The comparison was run with MiniMax-M3 under two prompt conditions, and it is reported in full in the guide's E.7.

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

1. Repeat the generator-side comparison on a generator that returns text on table questions.
2. Compare the gate against a token-level faithfulness monitor, not only against a prompt.
3. Settle the positional comparison's power: the direction is not uniform, the significance is not.
4. Run the long-context answer-quality half on the six-category corpus.
5. Add a second, stronger reranker to the pool sweep, so the pool result is not confounded.
6. Test specialisation with genuinely different reader models, rather than a brief to a fixed one.
7. Confirm the conflict labels with human annotators, against a fixed rubric.
8. Extend the corpus from federal regulation to a plant's own revised procedures.
9. Re-fit the conflict calibration on a plant's documents.
10. Extend the industrial corpus beyond one jurisdiction and one language.
11. Stratify the corpus by modality so the quota objective can be tested with adequate power.
12. Hand-check the repaired unanswerable class against the corpus, on both corpora.

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
| The whole corpus, as a prompt | 202,529 tokens | 680,417 tokens |
| The RAG arm's accepted context | 2,246 tokens (9.4 chunks) | 2,399 tokens |
| **Cost ratio** | **90×** | **282×** |
| The RAG arm's share of the corpus | 0.90% | — |
| Fits a 128K window | **no** | **no** |

And a retrieval-side proxy: with the candidate set widened from the fused
shortlist to *every* chunk in the corpus, the gold chunk still lands in the
scorer's top 10 for 0.969 of focus-domain queries (95% interval 0.843-0.994) at a median rank of 1. The same proxy on the six-category corpus puts the gold chunk in the top 10 for 0.902 of the queries (0.839-0.942), at a median rank of 1.
The evidence does not get lost in
a big context — but the focus corpus is 1.5× the size of a
128K window, and the RAG arm reaches the same evidence using 0.90% of what the long-context arm reads.

**The answer-quality half is now measured.** The answer-quality half of the comparison was measured on the focus domain. With the whole corpus in the prompt the generator answered 31 of 32 answerable questions, the same coverage as the pipeline, and it declined the unanswerable questions at a comparable rate (76 of 144 against 77 of 144), for 74 times the input actually sent per query. On coverage and on cost the result is settled: the whole-corpus prompt declines no more unanswerable questions than the pipeline does and costs 74 times as much to do it. On answer quality the margin is directional but not statistically significant once the answers are scored without the length confound.

**The same gap decides H2.1, and it is settled in the same honest way.** A
second harness (`impl/experiments/run_generation_eval.py`) puts
one generator behind five arms — the same retrieval with the gate removed, the framework at
its fitted operating point, **a random-escalation control that refuses the same
number of questions and picks them at random**, the framework at the operating
point transferred unchanged from the cross-category half, and the whole corpus
in the prompt — under **two prompt instructions that differ by one sentence**
(the generator may decline, or the generator must answer). It scores every
claim each arm produces against the evidence that arm was given.
The scorer is audited before any of it is read: 32 of the 33 answers the benchmark itself considers correct are recognised as supported by the evidence that states them, and 8 of the 9 fabricated values are rejected. The comparison was run with MiniMax-M3 under two prompt conditions. The answer to *"did you
show that the gate reduces hallucination?"* is **supported under both prompt conditions**:
the hypothesis holds under both prompt conditions. Under the cautious prompt -- the deployed system -- it is supported, at a price: the gate reduced the rate of answering unanswerable questions from 0.535 to 0.417, a fall of 11.8 points, at the cost of answering 30 of 32 answerable questions. Paired question by question, the gate refused 23 of the questions the ungated arm answered and let through 6 of the ones it did not (exact McNemar p = 0.002). Under the answering prompt, which differs from the cautious one by a single sentence, it is supported, at a price: the gate reduced the rate of answering unanswerable questions from 0.938 to 0.528, a fall of 41.0 points, at the cost of answering 30 of 32 answerable questions. Paired question by question, the gate refused 60 of the questions the ungated arm answered and let through 1 of the ones it did not (exact McNemar p = < 0.001). What the framework claims is therefore that the gate reduces the rate of answering unanswerable questions whatever the generator does, and that it is the one component whose behaviour does not depend on the generator's cooperation: the prompt can be wrong, and the gate still holds..

The replication on a second generator could not be run, and the reason is
measured rather than guessed: MiniMax-M3 returned no text on 0 of the 66 questions it was asked (0 of them on the benchmark's table-lookup family, against 0 of 22 on a control sample of the other families); MiniMax-M3.1-Flash returned no text on 24 of the 66 questions it was asked (23 of them on the benchmark's table-lookup family, against 1 of 22 on a control sample of the other families). The failures are not a shortage of output budget -- of the requests that came back empty, 13 were rescued by retrying at 4096 tokens and 11 were still empty there, the model spending the whole budget on reasoning and returning nothing. An empty completion is neither an answer nor a refusal, so the harness records the run as not-run instead of reporting a rate it cannot stand behind.

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
