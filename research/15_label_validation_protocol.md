# 15 — The answer-validation protocol: what it is, what the literature says about it, and which numbers depend on it

**What this file is.** The MTP benchmark's answer-side scoring is implemented but was never
written down. `_answer_is_correct` in `impl/experiments/run_generation_eval.py:474` runs **two
independent correctness tests** on every answered question, and the results files report both
(`correct_nli` and `correct_keyterm`, one column each). The docstring's one sentence — that the
two tests "fail differently" — is the whole of the current documentation. This note states the
protocol exactly as the code implements it, sets it against what comparable benchmarks do about
answer validation, lists the failure modes the literature actually quantifies, and says plainly
which reported numbers depend on the choice and which do not.

**Written.** 11 November 2026, for the 18 November 2026 defence.

**How it was prepared.** Every identifier below was resolved against a live registry on
**11 November 2026**; §6 records the route for each, and §6.2 lists the identifiers that were
supplied for this note but could **not** be resolved, together with what they actually point to.
Every number attributed to the thesis was read from the repository on the same date, and the
file and line it came from is given. Where the two disagree, the repository wins. Where the
literature quantifies nothing, this file says so rather than supplying a figure.

**A note on the label standard.** The benchmark's `label_standard` field reads `"silver"` in all
three benchmarks (`impl/data/benchmark/benchmark.json`,
`impl/data/benchmark_focus/benchmark.json`, `impl/data/benchmark_industrial/benchmark.json`). The
corpus, the benchmark and the label standard are frozen; nothing in this note proposes changing
any of them. The note proposes only that the protocol be *described*, and that the description
be checked against the code.

---

## 1. The protocol as implemented

### 1.1 The function

`impl/experiments/run_generation_eval.py:474-497`. It takes the generated answer text and the
gold answer string and returns a two-tuple `(by_nli, by_key)`. It is called once per answered
question (`:693`) and the two booleans are written to the record as `correct_nli` and
`correct_keyterm` (`:694-695`). The two tests are summed separately into `accuracy_nli` and
`accuracy_keyterm` (`:828-831`), so no reported number anywhere in the project collapses the two
into one.

The docstring, in full:

> The NLI test asks whether the generated answer entails the gold answer.
> The key-term test asks whether the gold answer's content words appear in
> the generated answer. They fail differently -- the NLI test is strict
> about paraphrase, the key-term test is strict about exact wording -- so
> reporting both keeps a single brittle test from deciding the result.

An empty gold answer returns `(False, False)` immediately (`:483-484`).

### 1.2 Test 1 — the NLI (entailment) test

* **What is computed.** One NLI call, `nli_probs([(answer_text, gold_answer)], ...)` (`:485`),
  with the generated answer as the **premise** and the gold answer as the **hypothesis**. The
  ordering matters: the question asked is "does the generated answer entail the gold answer?",
  not "does the gold answer entail the generated answer".
* **The model.** `CONFIG.claim.nli_model`, read from `impl/src/config.py:202`:
  `cross-encoder/nli-deberta-v3-small`. It is the same model the per-claim citation test uses.
* **The threshold.** `SUPPORT_THRESHOLD = 0.5` (`impl/experiments/run_generation_eval.py:159`).
  The comment above it records why the value is what it is: *"0.5 is the same threshold
  `src/claims.py` uses to decide whether a claim carries a citation."*
* **The verdict.** `by_nli = entail[0]["entailment"] >= 0.5` (`:486`).

Two consequences follow directly from the premise/hypothesis ordering and are visible in the
project's own numbers. First, the test is **asymmetric in length**: a long answer that contains
the gold as a conclusion entails it, while a long answer that contains the gold as one clause
among others may not. Second, it is **paraphrase-tolerant**: "the limit is 20 percent" entails
the gold "20 percent", but "the limit is twenty per cent" may or may not, depending on the
model. This is the "strict about paraphrase" half of the docstring's claim.

### 1.3 Test 2 — the key-term test

* **The token pattern.** `re.findall(r"[a-z0-9][a-z0-9.%/-]*", str(gold_answer).lower())`
  (`:490-491`). A token must start with an ASCII letter or digit and may then contain `.`, `%`,
  `/` and `-`. The gold is lowercased first. Consequences that matter for this corpus: a decimal
  point and a percent sign stay inside the token (`"69%"`, `"0.0000019%"`), a hyphenated word
  stays one token (`"non-destructive"`, `"dark-field"`), and a **sentence-final full stop stays
  inside the token** (`"Drilling."` → `"drilling."`).
* **The stopword filter.** The module-level `_STOPWORDS` set (`:164-171`), 98 English function
  words. Note that it includes `no`, so a gold of `"No"` yields no content terms at all.
* **The length/digit rule.** A token survives if `len(t) > 2 or any(c.isdigit() for c in t)`
  (`:492-493`). This is what keeps short numeric answers alive.
* **The six-token cap.** `[:6]` (`:493`). The cap keeps the **first** six surviving tokens in
  left-to-right order, not a salience-based or random subset. A gold with more than six content
  words is scored on its first six only.
* **The match.** `t in answer_text.lower()` (`:495`) — a plain **substring** test against the
  whole generated answer, with no token-boundary check on either side.
* **The threshold.** `>= max(1, len(terms) // 2)` (`:496`).

The code's own comment on the filter is the justification for keeping bare values, and it is
worth quoting because it explains a design decision that is otherwise invisible:

> ```python
>     # The key terms of the gold answer, filtered the same way the verbatim
>     # test filters them: a bare value like "69%" is a content term and has to
>     # count, or every short numeric answer would score as incorrect.
> ```
> — `impl/experiments/run_generation_eval.py:487-489`

The docstring calls this test "strict about exact wording". That is accurate for the substring
match itself, but the *threshold* is a recall threshold over terms, not an exact match against
the gold string, and §3.1 quantifies how far the two diverge.

### 1.4 Three properties of the implemented filter that the docstring does not state

These were measured directly against the project's own gold answers, by re-running the filter
over all **411 answerable gold answers** in the three benchmarks
(`impl/data/benchmark/`, `impl/data/benchmark_focus/`, `impl/data/benchmark_industrial/`)
using the code's own regular expression, stopword list and thresholds.

**(a) The "at least half" rule is integer division, and for 3- and 5-term golds it is below
half.** `len(terms) // 2` truncates. The threshold is therefore:

| content terms | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| terms required | 1 | 1 | **1** | 2 | **2** | 3 |
| fraction required | 100% | 50% | **33%** | 50% | **40%** | 50% |

**45 of the 411 answerable gold answers (10.9%)** fall into the below-half rows. A gold with
three content words is scored correct on the strength of **one** of them. This is a real
discrepancy between the docstring's word ("at least half") and the code, and it is not
cosmetic: it is the difference between one third and one half of the gold's content.

**(b) 102 of 411 golds (24.8%) reduce to a single substring check, and 15 of 411 (3.6%) cannot
be scored correct by this test at all.** The term-count distribution over the 411 answerable
golds is 0 terms: 15, 1 term: 102, 2: 39, 3: 19, 4: 31, 5: 26, 6 (capped): 179. The 15
zero-term golds are **all the literal string `"No"`**, all in the industrial benchmark's
`table_lookup` family; `"no"` is in `_STOPWORDS`, so `bool(terms)` is `False` and `by_key` is
`False` **whatever the generator answered**. A correct answer of "No", "no." or "The LDEQ for
NNNa is No" scores *incorrect* on the key-term test. That is a hard ceiling of 15/247 = 6.1%
on the industrial corpus's answerable set, and it is a ceiling on the *test*, not on the
generator. The NLI test is unaffected: a generated "No" plainly entails the gold "No".

**(c) The substring match has no token boundaries, so short terms are trivially satisfied.**
**86 of the 411 golds (20.9%)** contain at least one content term of two characters or fewer —
`"1"`, `"3"`, `"7"`, `"45"`, `"152"` — and any of these is a substring of many unrelated strings.
A gold of `"Mar. 1, 1980"` yields the terms `["mar.", "1", "1980"]`, needs one, and the term
`"1"` is satisfied by `"1980"`, `"2020"` or `"1861"`. A gold of `"45,785"` yields
`["45", "785"]` — the comma splits the number — needs one, and is satisfied by an answer
containing only the digits `45`. This is a false-positive path, not a false-negative one, and it
runs in the opposite direction to the `"No"` ceiling above.

Two smaller artefacts, listed for completeness because they will show up if the benchmark is
ever re-scored: **13 golds** carry a content token ending in a full stop (`"drilling."`,
`"control."`, `"2022."`, `"ref."`), and an answer that writes the same word *without* the
sentence-final punctuation fails the substring check on that token; and **11 golds** carry a
percent sign inside the token (`"6.7%"`, `"0.0000019%"`, `"80%"`), so a gold of `"20%"` is
satisfied only by the literal substring `"20%"` — `"20 percent"` does not contain it.

### 1.5 What "silver-standard" means for this protocol

The benchmark's labels are **silver-standard**: they are *derived from* the document rather than
*annotated on* it. The builder copies a value out of the gold chunk when it writes the question
(`impl/scripts/build_industrial_benchmark.py`; the `answer` field is set alongside the `gold`
chunk id at build time). Two things follow.

**It inflates absolute recall.** A question built from a chunk is, by construction, answerable
from that chunk, and the gold answer string is the chunk's own wording. The absolute accuracy
figures this protocol produces are therefore an upper bound on what the same systems would score
against human-written questions with human-written reference answers. This is the same objection
that applies to TriviaQA's distant supervision (its evidence is "independently gathered", but
its answer aliases come from the web, not from annotators) and to PopQA's Wikidata templates.

**It does not bias the comparison between systems.** Every arm is scored against *identical*
labels. A label that is wrong for one arm is wrong for all of them, so the error is a common
shift rather than a differential one. The project's own audit makes this argument explicitly
(`impl/experiments/audit_answer_side.py`, docstring; and `impl/results/exp9_label_audit.json`,
`note`: *"the gold chunk is correct in every defective case; only the answer string is attached
to the wrong question, so the retrieval-side metrics are unaffected"*). The label-defect rate
before the builder was repaired was **30 of 132 answerable questions by the conservative screen
and 27 by the precise rules** (`impl/results/exp9_label_audit.json`, `pre_repair`), i.e.
**20.5%–22.7%** of the answerable set carried an answer string attached to the wrong question;
after the repair it is **0 of 132**. That is a large enough error rate to move absolute
numbers and small enough, because it is common to all arms, to leave the comparison intact. It
is also the reason the label standard is frozen as it is: the defect was in the *builder*, and
fixing the builder rebuilt the benchmark rather than relabelling it.

---

## 2. How comparable benchmarks validate answers

All identifiers in this section were resolved live on 11 November 2026; §6 gives the route for
each. Where a paper's own wording matters, it is quoted.

### 2.1 Open-domain QA: SQuAD 2.0, TriviaQA, PopQA, WebQA, CRAG, BrowseComp

**SQuAD 2.0** (`arXiv:1806.03822`) adds an abstention task to extractive QA: over **50,000
unanswerable questions written adversarially by crowdworkers to look similar to answerable
ones** (abstract). The metric is **exact match and token-level F1**, and the unanswerable
decision is made by a *tuned threshold*: the model abstains when its predicted probability of
being unanswerable exceeds a threshold, and the threshold "is tuned separately for each model on
the development set", with the threshold that maximises F1 carried to the test set (§5.1). The
benchmark's human accuracy is **89.5% F1**, the best model reaches **66.3% F1**, and the
same architecture trained on SQuAD 1.1 reaches **85.8% F1** — a 5.4-point human gap on 1.1
against a 23.2-point gap on 2.0 (abstract; Table 3). The **EM-versus-F1 gap for the same
system** is visible in Table 4: DocQA+ELMo scores EM 79.4 / F1 83.0 on SQuAD 1.1, EM 85.7 /
F1 89.6 on SQuAD 1.1 with rule-based negatives, and EM 65.1 / F1 67.6 on SQuAD 2.0.

The **normalisation** is not described in the paper body; it lives in the official evaluation
script, `evaluate-v2.0.py` in the `rajpurkar/SQuAD-explorer` repository (read live). It is:
lowercase, remove the articles `a|an|the`, remove all `string.punctuation`, collapse
whitespace; `compute_exact` is then normalised-string equality, and F1 is token overlap. Note
what this normalisation does **not** do: it does not convert units, does not rescale, and does
not round. `"69%"` normalises to `"69"`; `"69 percent"` normalises to `"69 percent"`; the two
remain unequal.

**TriviaQA** (`arXiv:1705.03551`) states its alias mechanism explicitly (§6.1):

> We use the same evaluation metrics as SQuAD – exact match (EM) and F1 over
> words in the answer(s). For questions that have Numerical and FreeForm
> answers, we use a single given answer as ground truth. For questions that
> have Wikipedia entities as answers, we use Wikipedia aliases as valid answer
> along with the given answer.

So the alias list is applied *only* to the Wikipedia-entity subset, and the numerical and
free-form subsets are scored against a single string. The EM-to-F1 gap on the same baselines is
in the paper's table: Random 12.74 / 22.35, Classifier 23.42 / 27.68, BiDAF 40.26 / 45.74 (Wiki
dev) — gaps of 9.6, 4.3 and 5.5 points respectively, against a human baseline of roughly 79–80%.

**PopQA** is described in **Mallen, Asai, Zhong, Das, Khashabi and Hajishirzi (2023), "When not
to trust language models"** (`arXiv:2212.10511`, ACL 2023), and the dataset card
`akariasai/PopQA` on the Hugging Face Hub carries that same citation. The **metric is a
containment test**, quoted from the paper (§3.1 of the paper):

> Metrics: accuracy. We mark a prediction as correct if any substring of the
> prediction is an exact match of any of the gold answers.

The **multiplicity** comes from the knowledge graph: *"The set of acceptable answers to the
question is the set of entities E such that (S, R, E) exists in the knowledge graph"* — so
PopQA ships a **set** of acceptable answers, not a string. The **long-tail design** is the
benchmark's purpose: 14k questions built by sampling knowledge triples of 16 relationship types
from Wikidata and verbalising them with a hand-written template per relationship type, with
entity popularity taken from **Wikipedia monthly page views**. CRAG's appendix records the
long-tail subset the community actually uses: **1,399 rare-entity queries whose monthly Wikipedia
page views are less than 100** (`arXiv:2401.15884`, Appendix B.1).

**WebQA** (`arXiv:2109.00590`) unifies the answer schema across modalities in a way that is
directly relevant here (§B.3 of the paper):

> We unify the answer schema to be a complete natural language sentence and use
> an open answer set, so neither span prediction nor classification over a
> fixed vocabulary suffice.

It also states the reason the neighbouring benchmarks made the opposite choice: MultiModalQA
"requires different answer schemas for TextQA, ImageQA and TableQA" (span / yes-no / table cell
or aggregation), and ManyModalQA "restricts all answers to be a single word" — *"to avoid
ambiguity and for easy evaluation"*. WebQA's own scale is 22,423 image-based and 24,343
text-based queries over 600K images and 750K snippets; the answers are full sentences, and the
paper notes that "the full sentence answers are almost entirely unique". The point for this
note is the trade WebQA makes explicitly: **an open answer set and free-form sentences buy
realism and lose an unambiguous single-string scoring rule.**

**CRAG** (`arXiv:2401.15884`) scores correctness with **accuracy** for its three short-form
tasks and **FactScore** for its long-form task (Biography). Appendix B.1 is explicit that on
PopQA "only one entity of factual knowledge is expected to be answered for each single
question", and that the evaluation follows Self-RAG's long-tail subset. So CRAG inherits PopQA's
containment rule rather than defining a new one.

**BrowseComp** (`arXiv:2504.12516`) short-circuits the problem by **restricting the answer
form**, so that grading can be exact. The abstract: "predicted answers are short and easily
verifiable against reference answers". §2.1: trainers created questions "with single,
indisputable, short answers that would not change over time and were supported by evidence".
Grading is by an **LLM judge** checking whether the answer is "semantically equivalent to the
reference answer", using the same grading prompt as Humanity's Last Exam. The design principle —
*short, unambiguous answers are graded with a semantic equivalence check* — is the opposite of
the thesis's problem: the thesis's gold answers are extracted from regulatory text and are
sometimes ambiguous, so it cannot adopt the answer form.

### 2.2 Table QA: answers are lists, tuples, cells and choices

The thesis's corpus contains table cells, and the table-QA literature's answer formats are
worth stating precisely because they are not strings.

**WikiTableQuestions** is introduced by **Pasupat and Liang (2015), "Compositional Semantic
Parsing on Semi-Structured Tables"** (`arXiv:1508.00305`), which created "a new dataset of
22,033 complex questions on Wikipedia tables". The dataset's own record on the Hugging Face Hub,
`stanfordnlp/wikitablequestions` (read live), specifies the shape: each instance has
`answers` as a **sequence of strings**, and a `table` struct of `header`, `rows` and `name`;
the published example is `"answers": ["2004"]` against a table of `header`/`rows`. The table
itself is a nested structure — a header row and a list of rows — so the answer is a cell
selected from a two-dimensional array, and the dataset admits **more than one accepted answer
string per question**.

**TabFact** (`arXiv:1909.02164`) is not a QA benchmark at all: it is **binary fact
verification**, with "16k Wikipedia tables as the evidence for 118k human-annotated natural
language statements, which are labeled as either ENTAILED or REFUTED". Its answer space is
therefore two-valued, which is the cheapest possible validation problem and the furthest
possible contrast with the thesis's free-text regulatory golds.

**TabMWP** is introduced by **Lu, Qiu, Chang, Wu and Zhu (2023), "Dynamic Prompt Learning via
Policy Gradient for Semi-structured Mathematical Reasoning"** (`arXiv:2209.14610`, ICLR 2023),
the paper the dataset's own project page (`promptpg.github.io`) names. It presents "Tabular
Math Word Problems (TabMWP), a new dataset containing 38,431 open-domain grade-level problems
that require mathematical reasoning on both textual and tabular data", and it has "**two types
of questions: free-text and multi-choice**", each "annotated with gold solutions to reveal the
multi-step reasoning process". The project page gives the split: **74.7% free-text, 25.3%
multi-choice**. So TabMWP's answers are either a free-text value (often numeric) or a choice
from an option list, and the *dataset* distinguishes them.

**HybridQA** (`arXiv:2004.07347`) aligns each question with "a Wikipedia table and multiple
free-form corpora linked with the entities in the table"; the answers are free-form, and the
paper reports EM below 20% for the two single-modality baselines against "an EM over 40%" for
the hybrid model.

**The common pattern.** Across WTQ, TabMWP, TabFact and HybridQA the answer is one of: a
**list of accepted strings**, a **cell inside a nested table**, a **choice from an option
list**, a **binary verdict**, or a **free-text string**. Only the last of these is
single-string, and it is the only one a single gold string can represent exactly. The thesis's
corpus produces table cells whose values include bare numbers (`"20"`), numbers with spelled-out
units (`"20 percent"`), numbers with symbols (`"6.7%"`), multi-word cell values
(`"Rubber Tire Manufacturing Industry"`), single words with trailing punctuation
(`"Drilling."`), and boolean-ish cell values (`"No"`).

### 2.3 Retrieval-side metrics, and why they are separate — BEIR

**BEIR** (`arXiv:2104.08663`) is the IR community's reason the thesis reports retrieval
metrics separately from answer correctness. Its §3.3 argues for a single rank-aware metric
across heterogeneous tasks:

> Decision support metrics such as Precision and Recall which are both rank
> unaware are not suitable. Binary rank-aware metrics such as MRR and MAP fail
> to evaluate tasks with graded relevance judgements.

BEIR therefore "compute[s] **nDCG@10** for all datasets" using the official TREC evaluation tool,
with **Recall@100** reported alongside (Table 9). This is the argument that the retrieval leg
and the answer leg are measured by different instruments, on different objects: BEIR's judgements
are about *which documents were retrieved*, and no amount of care in answer matching makes a
retrieval metric sensitive to how the answer is scored.

BEIR also supplies the single most useful quantified demonstration of label-noise propagation in
this note — see §3.5.

### 2.4 Attribution and reference-free faithfulness — ALCE, RAGAS, ARES

**ALCE** (`arXiv:2305.14627`) is the closest published analogue to what the thesis measures on
the attribution side, and it is explicit about its answer-validation conventions (§A of the
paper):

* For **ASQA**: "we calculate the recall of correct short answers by checking whether the short
  answers (provided by the dataset) are **exact substrings of the generation** (exact match
  recall; EM recall)".
* For **QAMPARI**: "we calculate the precision and recall of the model prediction, by checking
  the **exact match to the gold answer list**", plus a "recall-5" relaxation under which recall
  is 100% if the prediction includes at least five correct answers.
* For **ELI5**: "the ELI5 dataset does not provide short entity answers", so ROUGE is used —
  and the paper says so critically: "ROUGE ... does not reflect the correctness well".

Note what this means: **the leading citation-generation benchmark uses a containment test for
short-form answers, an exact-match-to-a-list test for list answers, and ROUGE — with an explicit
warning — where no short answer exists.** The thesis's key-term test is a third thing again: a
containment test with a term-recall threshold rather than a whole-answer containment.

ALCE's attribution metrics are **citation recall** and **citation precision** (§3.3):

> We evaluate citation qualities using two metrics: (1) citation recall, which
> determines if the output is entirely supported by cited passages, and (2)
> citation precision, which identifies any irrelevant citations.

and the checker is an **NLI model**: "We use an NLI model to verify whether a statement is
supported". This is the same family of instrument the thesis uses for its NLI test and for its
per-claim support test, at the same 0.5-style threshold, and it is the published precedent for
reporting a **pair** of attribution numbers rather than one.

**RAGAS** (`arXiv:2309.15217`) and **ARES** (`arXiv:2311.09476`) are the reference-free
faithfulness instruments. RAGAS provides metrics that work "**without having to rely on ground
truth human annotations**", across the dimensions of context relevance/precision, faithfulness
and answer relevancy. ARES trains lightweight LM judges on synthetic data for **context
relevance, answer faithfulness and answer relevance**, and then uses **prediction-powered
inference** over "a small set of human-annotated datapoints" to bound judge error, evaluated
across eight knowledge-intensive tasks in KILT, SuperGLUE and AIS.

Both assume something the thesis's protocol does not: a *reference-free* claim is a claim about
the relationship between an answer and its **context**, not against a gold answer. A
reference-free faithfulness score cannot say whether the answer is the right answer, only
whether it is supported by what the system showed the model. This is why the thesis reports
claim support and answer correctness as separate columns: they answer different questions, and
the project's own deliverable already makes this separation explicitly.

---

## 3. The known failure modes, and what the literature actually quantifies

This section is deliberately conservative. Where the literature gives a number, the number is
given with its source. Where it does not, that is stated.

### 3.1 Containment versus exact match

**The mechanism.** A containment match credits an answer that contains the gold string but adds
material around it; an exact match penalises a correct answer expressed differently. The two
directions of error are different and both are live in the thesis's corpus.

**Published conventions, in order of strictness.**

| Convention | Who uses it | Source |
|---|---|---|
| Containment of the gold in the prediction | PopQA | `arXiv:2212.10511` §3.1, quoted in §2.1 |
| Containment of the gold in the prediction | ALCE, for ASQA | `arXiv:2305.14627` §A, quoted in §2.4 |
| Normalised exact match (string equality) | SQuAD 2.0 | `evaluate-v2.0.py`, `compute_exact` |
| EM **and** token-level F1, reported together | SQuAD 2.0, TriviaQA | `arXiv:1806.03822` Table 4; `arXiv:1705.03551` §6.1 |
| Exact match against a gold *list* | ALCE, for QAMPARI | `arXiv:2305.14627` §A |
| LLM judge on semantic equivalence | BrowseComp | `arXiv:2504.12516` §2.3 |
| Term recall at a threshold | **this thesis** | `impl/experiments/run_generation_eval.py:490-496` |

**Quantified deltas where they exist.**

* **EM → F1, same system, same answers.** SQuAD 2.0, DocQA+ELMo: **EM 65.1 vs F1 67.6** on
  SQuAD 2.0 (gap 2.5); EM 79.4 vs F1 83.0 on SQuAD 1.1 (gap 3.6); EM 85.7 vs F1 89.6 with
  rule-based negatives (gap 3.9). TriviaQA, Wiki dev: Random **12.74 / 22.35** (gap 9.6),
  Classifier **23.42 / 27.68** (gap 4.3), BiDAF **40.26 / 45.74** (gap 5.5).
* **Whole-answer entailment versus the same answers scored two other ways** — this is the
  project's own measurement, and it is the closest available analogue. On the focus corpus, 30
  paired questions, retrieval arm versus long-context arm
  (`impl/results_focus/exp9_label_audit.json`, `significance`): under the whole-answer NLI test
  the discordant pairs are 4 retrieval-only against 3 long-context-only, **p = 1.000**; under a
  length-controlled first-sentence NLI test, 7 against 2, **p = 0.180**; under the lexical
  key-term test, 3 against 0, **p = 0.250**. Median answer lengths: 181 characters (retrieval
  arm) against 254 (long-context arm). **All three tests agree on direction; none reaches
  p < 0.05; and the p-values are ordered the opposite way to the deliverable's prose suggests
  (see §4.3).**
* **Containment's false-positive rate.** The literature does not quantify it. PopQA's paper and
  ALCE's paper both adopt containment without reporting what it costs in false positives.
  This is an explicit gap, not a figure this note can supply from the literature.

**Where the literature gives no number.** There is no published estimate, for any of these
benchmarks, of the score difference between a containment test and a term-recall test on the
same answers. The thesis's own two-column report is, as far as this note can establish, the
unusual thing about it — and §5 says what would make it a measurement rather than a report.

**Measured locally, in the direction the literature does not cover.** On the thesis's own golds,
the key-term test's containment has no token-boundary check: **86 of 411 answerable golds
(20.9%)** carry a content term of two characters or fewer, and a term such as `"1"` or `"45"` is
satisfied by any longer string containing those digits (§1.4c). No comparable benchmark reports a
figure for this, because no comparable benchmark uses this test.

### 3.2 Gold-answer ambiguity, aliasing and multiplicity

**The mechanism.** When more than one surface form is correct, a single-string gold penalises
correct answers. This is not hypothetical for this corpus: the gold strings are copied out of
regulatory text, and the same value is expressible as `"20%"`, `"20 percent"` and `"twenty
per cent"`.

**What the literature does about it.**

* **TriviaQA** ships **Wikipedia aliases** for the entity-answer subset, and the paper says
  precisely where the alias list applies and where it does not (§2.1). *Size of the effect: the
  paper reports no separate number for the alias contribution; the TriviaQA baseline table
  separates Wikipedia from web evaluation but does not isolate the aliasing contribution.*
* **PopQA** derives the acceptable-answer set from the knowledge graph: *"the set of entities E
  such that (S, R, E) exists in the knowledge graph"* (§2.1). The dataset card lists
  `possible_answers` as *"A list of the gold answers"*. *Size of the effect: not reported as a
  separate figure in either source.*
* **WebQA** sidesteps the problem by unifying to "a complete natural language sentence" with
  "an open answer set", and by choosing not to optimise for easy evaluation — while noting that
  ManyModalQA restricted answers to a single word "to avoid ambiguity and for easy evaluation".
  The paper does not quantify what that trade costs.
* **ALCE** handles list answers by exact-matching against a gold list and adds a recall-5
  relaxation; for ASQA it uses substring containment because the dataset supplies the short
  answers.
* **WikiTableQuestions** accepts a **list** of answer strings per question, and the table is a
  nested structure, so a cell value may legitimately have more than one accepted spelling.

**The honest summary.** The literature's consensus is that multiplicity must be handled
*structurally* — by shipping a list of acceptable answers (PopQA, WTQ, ALCE/QAMPARI) or by
aliasing (TriviaQA) — and that a single-string gold is a known source of false negatives. **The
literature does not quantify the size of that penalty.** No cited paper reports "X% of correct
answers were rejected because the gold was a single string". This note does not supply one
either.

**Where this bites the thesis specifically.** Two places, both verified against the benchmark
files: the **15 `"No"` golds** that the key-term test cannot score correct (§1.4b), and the
numeric golds — **127 of 411 golds (30.9%)** contain at least one purely numeric content token
(`"20"`, `"6.7%"`, `"0.0000019%"`) — where a correct answer in a different unit form or at a
different rounding is a false negative. Neither has been measured against a human annotation of
this corpus, because no such annotation exists (§5).

### 3.3 Numeric, unit and rounding conventions

**The mechanism.** A gold of `"69%"` against an answer of `"69 percent"` or `"0.69"`.

**What the conventions are, and where they are documented.**

* **SQuAD 2.0** — normalisation is documented in the evaluation script, not the paper:
  lowercase, remove articles, remove punctuation, collapse whitespace. **No unit conversion, no
  rescaling, no rounding.** `"69%"` → `"69"`; `"69 percent"` → `"69 percent"`; `"0.69"` →
  `"069"`. The latter is worth noting: stripping punctuation leaves the leading zero, so
  `"0.69"` becomes `"069"` and does not match `"69"`.
* **TriviaQA** — EM and F1 over words, with aliases for the entity subset (§2.1). Numerical and
  free-form answers use "a single given answer as ground truth", so no unit tolerance is
  offered.
* **PopQA** — containment of a gold answer, where the gold set is drawn from Wikidata, so the
  acceptable surface forms are those the knowledge graph records for that entity.
* **TabMWP** — distinguishes free-text numeric answers from multiple-choice answers
  (§2.2), which is a *format* distinction, not a numeric-tolerance convention.
* **This thesis** — no numeric convention at all. The gold string is matched as a substring;
  `"20%"` is satisfied by `"20%"` and not by `"20 percent"`; `"20 percent"` yields the terms
  `["20", "percent"]` and needs one of the two, so `"20 percent"` and `"20%"` both pass it,
  while `"20"` alone also passes it (one of two terms). The two tests disagree about
  `"20 percent"` in opposite directions, and neither has been characterised against a
  human-written variant of the same question.

**What the literature does not say.** There is no cited source that specifies a canonical
policy for percentage-versus-decimal scaling or for rounding tolerance in open-domain QA answer
matching, and no cited source quantifies how often such a mismatch occurs. The nearest thing is
SQuAD 2.0's choice of the *same* metrics for numerical and free-form answers, with aliases
confined to the entity subset — that is, the leading benchmark simply does not solve the numeric
problem, and does not claim to.

### 3.4 Partial-credit scoring

**What it is.** SQuAD's token-level F1, as distinct from exact match: the harmonic mean of
precision and recall over the *token multiset overlap* of prediction and gold, after the
normalisation above. TriviaQA inherits it.

**What it buys.** A partially correct answer earns partial credit instead of zero, and the
EM-versus-F1 gap is the price of that choice, measured on the same systems and the same answers:
**2.5 to 3.9 points** on SQuAD 2.0's Table 4, **4.3 to 9.6 points** on TriviaQA's baselines
(§3.1). Partial credit is what lets a benchmark report both an exactness-sensitive and an
overlap-sensitive number from one scoring function.

**What it costs.** F1 is a *set-overlap* measure, and it is not a correctness measure: a
prediction that contains every gold token plus a large amount of unrelated text still scores
well on recall while scoring poorly on precision, and the two are averaged. ALCE's own criticism
of ROUGE on ELI5 — "ROUGE ... does not reflect the correctness well" — is the general form of
this objection: overlap metrics and correctness metrics are different instruments.

**What the thesis does instead.** The thesis reports **two** independent binary tests rather
than one continuous partial-credit metric. That is a defensible choice and it is not the
literature's choice: no cited benchmark reports two independent correctness tests side by side
for the same answers. The cost is that the thesis reports no partial credit at all, so a
partially-correct answer scores zero on both tests; the benefit is that the two columns
diagnose *different* failures rather than averaging them away.

### 3.5 Label-noise propagation

**The question.** How much does one upstream labelling error move a downstream score?

**The general answer, quantified, from BEIR.** BEIR's TREC-COVID Hole@10 analysis is the
cleanest published measurement of this, because it holds the retrieval systems fixed and changes
only the judgements. "Hole@10" counts top-10 hits that the annotators never saw; BEIR then
annotated **980 missing query-document pairs** "following the original annotation guidelines"
and re-computed nDCG@10 (`arXiv:2104.08663`, Table 4 and §"Hole@10 analysis"):

| System | Hole@10 | nDCG@10 original | nDCG@10 annotated | Δ |
|---|---|---|---|---|
| BM25 | 6.4% | 0.656 | 0.668 | +0.012 |
| DeepCT | 19.4% | 0.406 | 0.472 | +0.066 |
| SPARTA | 12.4% | 0.538 | 0.624 | +0.086 |
| docT5query | 2.8% | 0.713 | 0.714 | +0.001 |
| DPR | 30.6% | 0.332 | 0.445 | +0.113 |
| ANCE | 14.4% | 0.654 | 0.735 | +0.081 |
| TAS-B | 31.8% | 0.481 | 0.555 | +0.074 |
| ColBERT | 12.4% | 0.677 | 0.735 | +0.058 |
| BM25+CE | 1.6% | 0.757 | 0.760 | +0.003 |

Three things follow, and all three bear on this thesis.

1. **The size of the movement scales with how much of the top-k the annotators missed**, from
   +0.001 for a system whose hits the annotators saw (docT5query, Hole@10 = 2.8%) to +0.113
   for the system they saw least of (DPR, Hole@10 = 30.6%).
2. **Label noise can reorder systems, not merely move them.** BEIR's own reading: after
   annotation, ANCE "improves from 0.654 (slightly below BM25) to 0.735, which is 6.7 points
   above the BM25 performance". A ranking that is a property of the annotation pool, not of the
   systems, is not a finding.
3. **BEIR notes the annotation pool is itself biased** — it was "biased towards" the systems
   that contributed to it.

**The thesis's own case.** The benchmark's label defect rate before the builder was repaired was
**30 of 132 answerable questions (22.7%)** by the conservative screen and **27 (20.5%)** by the
precise rules (`impl/results/exp9_label_audit.json`, `pre_repair`). The project's audit
(`impl/experiments/audit_answer_side.py`) establishes that the **gold chunk was correct in every
defective case**, so the retrieval-side measurements were never affected, and that the
answer-side accuracy was depressed **for every arm equally** because every arm is scored against
the same labels. That is the BEIR lesson applied and answered: the noise was large (22.7%) but
common-mode, so it moved absolute numbers and not the ordering.

**What the literature does not quantify.** No cited paper reports "an upstream labelling error of
rate *r* moves a downstream answer-correctness score by *x*". BEIR quantifies the analogous
effect for *retrieval* metrics under a retrieval-specific noise model (unseen documents);
SQuAD 2.0 quantifies the effect of adding a new question class (answerable → unanswerable:
66.3% F1 against 85.8% F1 for the same architecture, and the human gap widening from 5.4 to 23.2
points). Neither is the quantity a reader would want for this benchmark, and no source supplies
it.

---

## 4. What this means for the thesis's reported numbers

### 4.1 What does not depend on the answer-validation choice at all

**Every retrieval-side measurement.** BEIR's argument (§2.3) is that retrieval quality is a
property of the retrieved set, judged by rank-aware judgements about documents. Recall@k,
nDCG@k, MRR, and the pool-size and category-quota figures are computed against gold *chunks*,
and gold chunks were never affected by the answer-label defect
(`impl/results/exp9_label_audit.json`, `note`). The answer-validation protocol has no path to
these numbers. The gate's operating point, the coverage cost, the risk-coverage curve, the
calibration diagnostics, and the transfer result are all **invariant** to the choice of answer
metric.

**The unanswerable-class analysis.** The unanswerable questions carry no answer labels at all
(`impl/results_focus/exp12_unanswerable_class_audit.json`), so the H2.1 result — that the gate
refuses questions it should refuse — rests on *whether the system answered*, not on whether the
answer was scored correct.

**The claim-support and claim-hallucination columns.** These are scored by `_claim_support`,
a different function with a different design: per-claim entailment against the evidence the arm
was shown, with an explicit literal-statement test as an alternative for bare values
(`impl/experiments/run_generation_eval.py:408-471`). They are **not** the answer-validation
protocol and are not affected by it.

### 4.2 What does depend on it, and in which direction

The generator-side accuracy column is the only place the choice bites, and it is worth being
precise about the *direction* rather than asserting that the numbers are fragile.

**The key-term test is uniformly more lenient than the NLI test on this corpus.** Across the
focus corpus's five arms in both generator conditions, `accuracy_keyterm` exceeds
`accuracy_nli` in every single case:

| Arm (focus corpus, answerable, "cautious") | answered | NLI | key-term | spread |
|---|---|---|---|---|
| retrieval, gate removed | 31/32 | 0.613 | 0.903 | 0.290 |
| framework, gate fitted on this benchmark | 30/32 | 0.733 | 0.900 | 0.167 |
| control refusing at random | 22/32 | 0.591 | 0.818 | 0.227 |
| framework, threshold transferred unchanged | 11/32 | 0.364 | 0.727 | 0.364 |
| whole corpus in the prompt | 31/32 | 0.548 | 0.774 | 0.226 |

(Source: `impl/results_focus/exp8_generation.json`, `arms.*.answerable`. The same pattern holds
for the "answering" condition, `impl/results_focus/exp8_generation_answering.json`: 0.719/0.875,
0.633/0.900, 0.636/0.818, 0.273/0.818, 0.406/0.750.)

The mechanism is not mysterious: the key-term test is a containment test with a low bar
(§1.4), and the NLI test is a semantic test with a 0.5 threshold on a premise that may be much
longer than its hypothesis.

**And the ordering of the arms is not stable across the two tests.** In the "cautious" condition
the NLI test puts the fitted gate **first** (0.733 against 0.613 for the ungated pipeline, a
margin of 0.120), while the key-term test puts the ungated pipeline **first** by the thinnest
possible margin (0.903 against 0.900, a margin of 0.003). In the "answering" condition the
ordering **reverses**: NLI puts the ungated pipeline first (0.719 against 0.633, a margin of
0.085) and the key-term test puts the fitted gate first (0.900 against 0.875, a margin of
0.025). The same reversal happens between two other arms in the "answering" condition: the
transferred threshold scores 0.818 against the whole-corpus arm's 0.750 on the key-term test,
but 0.273 against 0.406 on the NLI test.

**The direction of the sensitivity, stated concretely.** The answer-validation convention
determines:

* **the absolute level** of every generator-side accuracy figure — by 0.17 to 0.36 in this
  corpus, which is larger than most of the margins the thesis reports;
* **whether the gate looks better or worse than no gate at all** — the sign of that particular
  comparison flips with the test, in both generator conditions, in opposite directions;
* **not** the coverage, cost, claim-support or retrieval numbers, and **not** the *direction* of
  the long-context comparison, which the audit confirms is the same under all three of its
  scoring variants (§3.1).

**The claims that survive the switch and the claims that do not.**

* **Survive.** "The gate refuses the questions it should refuse and refuses many it need not"
  (coverage, cost, claim support, unanswerable analysis). "The whole corpus in the prompt does
  not decline more unanswerable questions than the pipeline does, and costs far more" (coverage
  and cost). "The generator does not reproduce the corpus's values from parameters"
  (closed-book accuracy 0.094 NLI / 0.188 key-term on the focus corpus, 0.061 / 0.220 on the
  main corpus — `impl/results_focus/exp12_unanswerable_class_audit.json` and
  `impl/results/exp12_unanswerable_class_audit.json`; both conventions agree that the closed-book
  answers are wrong the great majority of the time).
* **Survive, at reduced strength.** "The whole-corpus prompt is not better on answer quality than
  the ten-chunk prompt": direction holds under all three tests, but the margin is not
  statistically significant under any of them (p = 1.000, 0.180, 0.250).
* **Do not survive.** Any statement of the form "the gated framework answers more accurately
  than the ungated pipeline" **as a headline accuracy claim**, because the sign of that
  comparison depends on which of the two reported tests is read. The defensible version is the
  one the deliverable already reaches: the gate's benefit is on **coverage and cost**, and its
  answer-side effect is **directional, not significant**.

### 4.3 Two defects in the deliverable's E.8 prose, found while checking this

Both are in the *generated* text, not in the measurement, and neither was fixed here because
other processes are working in `deliverables/`.

1. **The significance sentence states the p-values backwards.**
   `deliverables/scripts/results_source.py:2062-2071` emits "The accuracy margin over the
   long-context arm is significant only under the whole-answer entailment test (p = 1.000) and
   not under a length-controlled re-scoring ... (p = 0.180) or a lexical test ... (p = 0.250)".
   The p-value **1.000** is the *least* significant of the three, and the other two are smaller
   than it; none is significant at α = 0.05. The sentence's **conclusion** — that the
   long-context comparison is "directional rather than significant on answer quality" — is
   correct and is if anything conservative; the **reasoning** attached to it is not. The
   corrected sentence should read that *no* test reaches significance, with the whole-answer
   test the least discriminating of the three.
2. **A Python `None` has been rendered into prose.** The same template reads
   `pre.get('n_defective')` from the focus corpus's label audit
   (`impl/results_focus/exp9_label_audit.json`), whose `pre_repair` block carries no
   `n_defective` field — the focus corpus's pre-repair benchmark is a *different* corpus
   (`same_corpus: false`). The rendered sentence in
   `deliverables/Deliverable_1_PartE_Results.md` therefore reads "**None of the 132
   answerable questions** carrying an answer attached to the wrong question". The true figures
   are **30 of 132 by the conservative screen and 27 by the precise rules** pre-repair, and
   **0 of 132** post-repair — and the focus corpus's own post-repair count is **0 of 32**
   (`impl/results_focus/exp9_label_audit.json`).

Neither defect changes a reported number. The first makes a conservative conclusion look
weakly-supported; the second understates a defect rate that is actually worth stating.

### 4.4 Two generator-side runs that have not been completed

Every generator-side accuracy figure in the thesis therefore comes from **one generator, on one
corpus (the focus corpus), in two prompt conditions**. Two further conditions are recorded as
not run, for two different reasons.

* The **industrial** corpus's generator-side evaluation was never completed:
  `impl/results_industrial/exp8_generation_industrial.json` records `status: "not_run"` with
  the reason *"the generator rejected the requests, so no arm asked any question and no rate from
  it is reported: HTTP 429 -- Token Plan usage limit reached"*.
* The **second-generator replication** on the focus corpus was never completed either:
  `impl/results_focus/exp8_generation_flash.json` records `status: "not_run"` with the reason
  *"the generator rejected the requests, so no arm asked any question and no rate from it is
  reported: rag_nogate: empty completion (stop_reason='max_tokens', content types=['thinking'])"*.

Two consequences, and they point in opposite directions. The **first** is a limit on what the
answer-validation protocol can be said to have measured: it has been measured on one generator's
answers on one corpus, so the two-column report characterises *the instrument*, not the
generator population. The **second** is a limit on the industrial corpus specifically: when the
industrial run is repeated, the **15 `"No"` golds** (§1.4b) will impose a hard 6.1% ceiling on
the key-term column for that corpus, which the NLI column will not share. That ceiling should be
handled before the industrial numbers are read, not after.

---

## 5. What was not done

This note closes a documentation gap. It closes four smaller gaps. It does not close these.

1. **No human double-annotation of a sample of the benchmark's own questions.** Nobody has
   independently written the answer to a sample of the focus or industrial benchmark's questions,
   so the *correctness* of the silver labels is unmeasured on this corpus. The label audit
   (`impl/experiments/audit_answer_side.py`) checks that the gold string is **stated by the gold
   chunk** and **sits in the column the question names** — it checks the label against the
   document, not against a human's reading of the question. Nothing here establishes that the
   generated question is *unambiguous*, which is the assumption the whole protocol rests on.
   This is the single largest open item.
2. **No measurement of the aliasing rate on this corpus's gold answers specifically.** §3.2
   quantifies the *mechanism* — 127 of 411 golds (30.9%) carry a purely numeric content token,
   15 are the string `"No"`, 13 carry a trailing full stop inside a token — but nobody has
   counted how many of the corpus's gold answers have **more than one correct surface form**,
   because that requires the human annotation in item 1.
3. **No re-scoring of the shipped results under a third validation convention.** The thesis
   reports two tests and audits three (whole-answer NLI, first-sentence NLI, lexical
   key-term). A third *convention* in the sense of the literature — SQuAD's normalised exact
   match and token-level F1, or PopQA's whole-answer containment, or an LLM judge on semantic
   equivalence in BrowseComp's style — has not been applied to the shipped answers.
   **This is feasible, and cheap.** `_answer_is_correct` is a single function
   (`impl/experiments/run_generation_eval.py:474`), the generator answers and the gold strings are
   both present in the result files (`records[arm][i].answer_text`, and the benchmark's `answer`
   field), and the audit already demonstrates the pattern for a third scoring variant
   (`_paired_robustness` in `impl/experiments/audit_answer_side.py:244-295`, which re-scores the
   *same* answers under three conventions and reports McNemar tests). A fourth convention would
   be an extension of that function, not a new experiment.
4. **No measurement of how often the two tests disagree, question by question.** The project
   reports both columns and the arm-level spreads (§4.2), but the *paired* disagreement count
   between `correct_nli` and `correct_keyterm` — the questions on which the two conventions give
   opposite verdicts — is not reported, and that count is the direct measure of how much the
   convention matters for a given question. It is derivable from the shipped records without
   re-running anything.

---

## 6. Identifiers: how each was resolved

**The house rule.** Nothing in this file is cited from memory. Every identifier below was
resolved on **11 November 2026** against a live registry, and the title was read from the
registry's record, not from a citation in another paper.

### 6.1 Resolved

| Work | Identifier | Registry and route | What was read |
|---|---|---|---|
| SQuAD 2.0 | `arXiv:1806.03822` | arXiv API (`research/_litquery.py arxiv-ids`) + arXiv abs page + ar5iv full text | title, authors, "ACL 2018", abstract, Tables 3–4 |
| TriviaQA | `arXiv:1705.03551` | arXiv API + ar5iv full text | title, authors, abstract, §6.1 evaluation metrics, baseline table |
| PopQA | `arXiv:2212.10511` | arXiv API + arXiv PDF (v4) + Hugging Face dataset card `akariasai/popqa` + CRAG's bibliography | title, authors, "ACL 2023", §3.1 metrics, dataset construction |
| WebQA | `arXiv:2109.00590` | arXiv API ("CVPR Camera ready") + arXiv PDF (v4) | title, authors, abstract, appendix §B.3 answer schema, §C |
| CRAG | `arXiv:2401.15884` | arXiv API + arXiv PDF (v3) | title, authors, abstract, §5.1, Appendix B.1, bibliography entry for PopQA |
| BrowseComp | `arXiv:2504.12516` | arXiv API + ar5iv full text | title, authors, abstract, §2.1 criteria, §2.3 grading |
| TabFact | `arXiv:1909.02164` | arXiv API ("Accepted to ICLR 2020") | title, authors, abstract |
| WikiTableQuestions | `arXiv:1508.00305` | arXiv API + Hugging Face dataset card `stanfordnlp/wikitablequestions` | title, authors, abstract (22,033 questions), dataset card's field schema and citation |
| TabMWP | `arXiv:2209.14610` | arXiv API ("ICLR 2023") + project page `promptpg.github.io` | title, authors, abstract (38,431 problems, free-text vs multi-choice), the dataset's own citation |
| HybridQA | `arXiv:2004.07347` | arXiv API ("Accepted to Proceedings of EMNLP 2020 (Findings)") | title, authors, abstract |
| BEIR | `arXiv:2104.08663` | arXiv API ("Accepted at NeurIPS 2021 Dataset and Benchmark Track") + ar5iv full text | title, authors, §3.3 metric argument, Table 4 (Hole@10) |
| ALCE | `arXiv:2305.14627` | arXiv API ("Accepted by EMNLP 2023") + ar5iv full text | title, authors, §3.3 citation metrics, appendix §A answer-correctness conventions |
| RAGAS | `arXiv:2309.15217` | arXiv API | title, authors, abstract |
| ARES | `arXiv:2311.09476` | arXiv API ("NAACL 2024") | title, authors, abstract |
| SQuAD 2.0 evaluation script | `rajpurkar/SQuAD-explorer` → `evaluate-v2.0.py` | GitHub raw API | `normalize_answer`, `compute_exact`, `compute_f1` |

**Registries used.** arXiv API (`export.arxiv.org/api/query`), arXiv abstract pages
(`arxiv.org/abs/<id>`), ar5iv (`ar5iv.labs.arxiv.org/html/<id>`), arXiv PDF via `pdftotext`,
the ACL Anthology's per-volume BibTeX (`aclanthology.org/volumes/<volume>.bib`), the Crossref
REST API (prefix filter `10.18653`), OpenAlex (`api.openalex.org`), the Hugging Face Hub API
and dataset cards, the GitHub REST API and `raw.githubusercontent.com`, and the arXiv full-text
search interface (`arxiv.org/search/?searchtype=all`).

**Registries that failed and were worked around.** DBLP's API returned non-JSON on every
attempt from this host. Semantic Scholar's API returned HTTP 429 on most title queries. The
ACL Anthology's JavaScript search page could not be read without a browser, and the Playwright
browser binary is not installed at the path the venv expects; the volume-level `.bib` endpoint
was used instead.

### 6.2 Supplied for this note but not resolvable as given — and what they actually are

Eight of the identifiers in the brief for this note point to **unrelated papers**. Each was
checked twice: once through the arXiv API and once by reading the `citation_title` meta tag on
the arXiv abstract page. Both channels agree in every case.

| Identifier as supplied | Supposed to be | What it actually is |
|---|---|---|
| `arXiv:2110.14739` | PopQA | "Generalized Shape Metrics on Neural Representations" (Williams, Kunz, Kornblith, Linderman; NeurIPS 2021) |
| `arXiv:2107.12621` | WebQA | "Intrusion Detection with Machine Learning Using Open-Sourced Datasets" (Mourouzis, Avgousti) |
| `arXiv:2404.18916` | BrowseComp | "Observation of generalized t-J spin dynamics with tunable dipolar interactions" (Carroll et al.) |
| `arXiv:2005.01438` | TabFact | "Conditional maximum entropy and Superstatistics" (Sergio Davis) |
| `arXiv:2007.00336` | WikiTableQuestions | "On the Minimization of Sobolev Norms of Time-Varying Graph Signals: Estimation of New Coronavirus Disease 2019" (Giraldo, Bouwmans) |
| `arXiv:2201.08785` | TabMWP | "Search setup for long-duration transient gravitational waves from glitching pulsars during LIGO-Virgo third observing run" (Modafferi et al.) |
| `arXiv:2010.05413` | HybridQA | "Dark supernova remnant" (Yoshiaki Sofue) |

The correct identifiers, each resolved live, are in §6.1. **None of the seven is cited in this
note under the identifier supplied.**

Two further points of provenance, since they affect how the PopQA and TabMWP entries should be
read:

* **PopQA has no separate paper titled after the dataset.** The dataset's canonical citation —
  the one on its own Hugging Face card, and the one CRAG's bibliography uses — is **Mallen et
  al. (2023), "When not to trust language models", ACL 2023, pp. 9802–9822** = `arXiv:2212.10511`.
  The dataset name "PopQA" appears inside that paper. The metric quoted in §2.1 is that paper's
  own metric statement.
* **TabMWP's dataset paper is the ICLR 2023 PromptPG paper**, `arXiv:2209.14610`, named as such
  by the dataset's own project page `promptpg.github.io`, which is the link the arXiv record's
  own comment points to.

### 6.3 Resolved but not read in full, and therefore not cited for a claim

`arXiv:2309.15217` (RAGAS) and `arXiv:2311.09476` (ARES) were cited from their abstracts only;
neither full text was read, so no claim in this note rests on their internal detail. The same
applies to `arXiv:1909.02164` (TabFact), `arXiv:2004.07347` (HybridQA) and `arXiv:1508.00305`
(WTQ), for which abstracts, the dataset card and the arXiv comments were read but not the full
texts. `arXiv:2109.00590` (WebQA) was read as a PDF; its ar5iv render is partial and the
appendix was used for the answer-schema statement.

---

## 7. References

Resolved on 11 November 2026 as recorded in §6.1.

1. Rajpurkar, Jia, Percy Liang. **Know What You Don't Know: Unanswerable Questions for SQuAD.**
   arXiv:1806.03822. ACL 2018.
2. Joshi, Mandar, Eunsol Choi, Daniel S. Weld, Luke Zettlemoyer. **TriviaQA: A Large Scale
   Distantly Supervised Challenge Dataset for Reading Comprehension.** arXiv:1705.03551. 2017.
3. Mallen, Alex, Akari Asai, Victor Zhong, Rajarshi Das, Daniel Khashabi, Hannaneh Hajishirzi.
   **When Not to Trust Language Models: Investigating Effectiveness of Parametric and
   Non-Parametric Memories.** arXiv:2212.10511. ACL 2023, pp. 9802–9822. *(The PopQA
   dataset.)*
4. Chang, Yingshan, Mridu Narang, Hisami Suzuki, Guihong Cao, and others. **WebQA: Multihop
   and Multimodal QA.** arXiv:2109.00590. CVPR camera-ready.
5. Yan, Shi-Qi, Jia-Chen Gu, Yun Zhu, Zhen-Hua Ling, and others. **Corrective Retrieval
   Augmented Generation.** arXiv:2401.15884. 2024.
6. Wei, Jason, Zhiqing Sun, Spencer Papay, Scott McKinney, and others. **BrowseComp: A Simple
   Yet Challenging Benchmark for Browsing Agents.** arXiv:2504.12516. 2025.
7. Chen, Wenhu, Hongmin Wang, Jianshu Chen, Yunkai Zhang, and others. **TabFact: A Large-scale
   Dataset for Table-based Fact Verification.** arXiv:1909.02164. ICLR 2020.
8. Pasupat, Panupong, Percy Liang. **Compositional Semantic Parsing on Semi-Structured Tables.**
   arXiv:1508.00305. ACL 2015. *(The WikiTableQuestions dataset.)*
9. Lu, Pan, Liang Qiu, Kai-Wei Chang, Ying Nian Wu, Song-Chun Zhu. **Dynamic Prompt Learning via
   Policy Gradient for Semi-structured Mathematical Reasoning.** arXiv:2209.14610. ICLR 2023.
   *(The TabMWP dataset.)*
10. Chen, Wenhu, Hanwen Zha, Zhiyu Chen, Wenhan Xiong, and others. **HybridQA: A Dataset of
    Multi-Hop Question Answering over Tabular and Textual Data.** arXiv:2004.07347. EMNLP 2020
    (Findings).
11. Thakur, Nandan, Nils Reimers, Andreas Rücklé, Abhishek Srivastava, Iryna Gurevych, and
    others. **BEIR: A Heterogenous Benchmark for Zero-shot Evaluation of Information Retrieval
    Models.** arXiv:2104.08663. NeurIPS 2021 Datasets and Benchmarks.
12. Gao, Tianyu, Howard Yen, Jiatong Yu, Danqi Chen, and others. **Enabling Large Language Models
    to Generate Text with Citations.** arXiv:2305.14627. EMNLP 2023.
13. Es, Shahul, Jithin James, Luis Espinosa-Anke, Steven Schockaert, and others. **Ragas:
    Automated Evaluation of Retrieval Augmented Generation.** arXiv:2309.15217. EACL 2024.
14. Saad-Falcon, Jon, Omar Khattab, Christopher Potts, Matei Zaharia, and others. **ARES: An
    Automated Evaluation Framework for Retrieval-Augmented Generation Systems.** arXiv:2311.09476.
    NAACL 2024.

---

*Prepared for the MTP "An Evidence-Grounded Retrieval-Augmented Generation Framework for
Industrial Decision Support", IIT Kharagpur, Department of Industrial and Systems Engineering.
Every identifier was resolved live on 11 November 2026 and every thesis number was read from the
repository on the same date. Where the deliverable's prose and the repository disagree, the
repository wins and the disagreement is recorded in §4.3 rather than silently reconciled.*
