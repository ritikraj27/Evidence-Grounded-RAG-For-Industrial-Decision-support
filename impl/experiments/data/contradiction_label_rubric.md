# Rubric for labelling the contradiction gate's pairs

You are given two passages from industrial-engineering documentation. Decide
**one** of five labels for the pair. Exactly one applies.

Work down the tree below and stop at the first question that applies.

## 1. Are the two passages about different subjects, neither being a part of
##    the other?

**Yes → `term_mismatch`**

The passages share vocabulary, a topic word, an entity name or a number, but
they are not about the same thing: two different plants, two different
components, two different topics. A number-matching rule fires on "lead time
is 14 days" and "lead time is 21 days" in two passages that are in fact
about two different plants; that pair is `term_mismatch`, and it is the
failure mode a *subject* check is meant to suppress.

**No → go to question 2.** The two passages are about the same subject, or
one is about a part of what the other is about.

## 2. Is one passage a later revision of the other?

**Yes → `supersession`**

"Raw material lead time is 21 days" and "Raw material lead time is 14 days
(revised, Q3)" are not a contradiction; they are a policy that changed. Look
for revision markers, dates, "updated", "revised", "previously", "now", "as
of", version numbers.

A pair is `supersession` even when the supersession is obvious and the
supersession check did **not** catch it — that is a false negative of the
supersession branch and is exactly what the labelling is looking for.

**No → go to question 3.**

## 3. Is one passage about a whole and the other about one of its parts, and
##    can both be true at the same time?

**Yes → `granularity`**

"The total cycle time for the machining operation is three days" and "the
annealing sub-step of the machining operation takes three days" are about a
whole and one of its parts. The general figure is true of the component in a
different sense, so the two do not contradict each other.

**No → go to question 4.**

## 4. Do the two passages state facts that cannot both be true at the same
##    time?

**Yes → `contradiction`**

Both cannot be true at once, and neither is a later revision of the other.
Two kinds count:

* **Numeric**: the same quantity takes two different values ("the batch
  size is 500 units" against "the batch size is 250 units"), with the
  subject matched — same product, same line, same policy.
* **Qualitative**: the same subject is asserted to have two different
  properties ("the valve is rated for 250 psi" against "the valve is rated
  for 400 psi"; "the material is stainless steel" against "the material is
  aluminium").

**No → go to question 5.**

## 5. Otherwise → `no_conflict`

The two passages are about the same subject and say compatible things. They
make different statements, or the same statement in different words, but
nothing one says is incompatible with anything the other says.

## The labels in one line each

| Label | One-line test | A conflict? |
|---|---|---|
| `term_mismatch` | Different subjects that merely share words. | No |
| `supersession` | Same subject, one is a later revision. | No |
| `granularity` | Same subject, whole versus part, both true at once. | No |
| `no_conflict` | Same subject, compatible statements. | No |
| `contradiction` | Same subject, incompatible statements. | **Yes** |

Only `contradiction` counts as a confirmed alarm. The other four differ in
*why* the pair is not a conflict, and the distinction matters because it is
what separates a detector that is too eager from one that is looking in the
wrong place.

## Notes for the reader

- **`numeric_conflicts` in the detector's own output is a hint, not a label.**
  It says the two passages attach different values to some distinctive
  quantity. It does not say the quantity is the same one, and it does not
  exclude a revision. The sheet shows it so that you can see what the
  detector saw; decide independently.
- **When a passage states a value for a quantity and the other passage states
  a value for a *different* quantity, that is `term_mismatch`,** not a
  contradiction — different measurements are not disagreements.
- **Different granularity is not a contradiction.** This is the category the
  published conflict taxonomy puts between "direct conflict" and
  "information-granularity difference", and it is the one industrial text
  produces most.
- **When you are unsure, say so in `notes` and use the closest label.** A
  labelled sheet with honest uncertainty is more useful than a confident one.
- If a passage is truncated or a table is split across passages, judge the
  pair on what is actually there.
- **Bibliographic text is not evidence.** A citation, an ISBN, a DOI, a
  publication year or a journal title is not a claim about the subject
  domain. Two passages that merely cite different papers are `no_conflict`
  (or `term_mismatch` if they are about different papers).

## After labelling

The sheet is scored by `python experiments/label_contradiction_pairs.py
--score`, which reports the precision of the alarms and an estimate of the
recall over the whole pair population, each with a 95% interval. The labels
are published with the results so that a reader can disagree with any of
them.
