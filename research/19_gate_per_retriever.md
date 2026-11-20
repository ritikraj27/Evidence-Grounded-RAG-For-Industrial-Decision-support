# 19 — The gate fitted per retriever, and the frontier as a curve

**Written:** 12 November 2026, six days before the defence.
**Closes:** gap **G14** from `research/16_open_items_register.md` §C.
**Artefact:** `impl/experiments/run_gate_per_retriever.py` →
`impl/results_focus/exp2b_gate_per_retriever.json`.

---

## 1. What the limitation said, and what closing it takes

Limitation **L10** in the Complete Guide's table:

> Calibration is fitted per retriever, not universally. A threshold
> transferred to a new retriever is wrong — and DeclineCraft shows it is
> wrong in the direction that flatters the weaker system. **Re-fit per arm,
> and report the per-arm threshold.**

The technical report already *asserted* the first half of that — §4.4 says
"the calibration is fitted separately for each retrieval configuration
compared, so that a change in retrieval strength cannot masquerade as a
change in gate quality" — but the thesis reported **one** operating point, for
**one** retriever, and the per-retriever thresholds had never been measured.

This note measures them, and adds the second half of what L10 asks for: the
**frontier as a curve** rather than as a point.

## 2. The design

Three retrievers, each producing the *same kind* of input to the gate — a
cross-encoder score over a candidate pool — so the calibrator has the same
shape in all three and what differs is the retriever that produced the
scores:

| Retriever | What it retrieves |
|---|---|
| `hybrid_rrf_rerank` | dense + BM25 fused by RRF, then reranked — **the shipped configuration** |
| `bm25_only_rerank` | the lexical leg alone, then reranked |
| `dense_only_rerank` | the dense leg alone, then reranked |

For each retriever the gate is fitted on its own features, on its own 60/40
query split, with the same seed and the same procedure as the shipped gate,
and the operating point is chosen by the shipped rule: *the highest τ that
still answers at least 90% of the answerable questions*.

**The re-implementation is validated by reproducing the shipped gate exactly.**
The `hybrid_rrf_rerank` arm returns τ = 0.05, 0.9375 of the answerable
questions answered, 0.35417 of the unanswerable ones refused, Brier 0.14432
and ECE 0.11429 — identical to `impl/results_focus/exp2_gate.json`'s
`chosen_operating_point` and `calibration_metrics` to every digit printed.
The shipped gate is therefore not a separate thing that happens to agree;
it is the same computation.

## 3. The result

### 3.1 The fitted threshold is retriever-specific

| Retriever | gold found | fitted τ | answerable answered | unanswerable refused | Brier | ECE |
|---|---|---|---|---|---|---|
| hybrid (shipped) | 32/176 (0.182) | **0.05** | 0.938 | 0.354 | 0.1443 | 0.1143 |
| lexical leg alone | 32/176 (0.182) | **0.10** | 0.906 | 0.611 | 0.1303 | 0.1616 |
| dense leg alone | 28/176 (0.159) | **0.05** | 0.812 | 0.674 | 0.1406 | 0.1697 |

Three things move together when the retriever changes, and none of them is a
constant of the architecture:

* **the threshold** — 0.05 on the hybrid, 0.10 on the lexical leg;
* **the operating point** — the lexical leg's gate refuses 61.1% of the
  unanswerable questions against the hybrid's 35.4%, and answers 90.6% of
  the answerable ones against 93.8%;
* **the evidence the retriever finds** — the dense leg finds the gold chunk
  for 28 of the 176 queries where the other two find 32, and its gate
  therefore answers only 81.2% of the answerable questions.

A gate that is "the same gate" on a different retriever is a different
system. That is the claim L10 makes, and it is now a measurement.

### 3.2 What a transferred threshold costs

The shipped retriever's τ, applied unchanged to another retriever's
calibrated posterior, against the threshold fitted on that retriever:

| Transfer | answerable answered | unanswerable refused | coverage |
|---|---|---|---|
| hybrid τ = 0.05 → lexical leg | **0.938** (against 0.906 refitted) | **0.347** (against 0.611) | 0.705 (against 0.483) |
| hybrid τ = 0.05 → dense leg | 0.812 (against 0.812) | 0.674 (against 0.674) | 0.415 (against 0.415) |

**The transfer is too permissive, and it is too permissive in the direction
that flatters the arm it is transferred to.** On the lexical leg the hybrid's
threshold answers 93.8% of the answerable questions — three points *more*
than the refitted threshold — while refusing 34.7% of the unanswerable ones,
which is **26.4 points fewer**. The lexical arm would look better on the
refusal metric than it is, which is exactly the failure L10 names.

And the honest qualification: **the transfer is not always wrong.** On the
dense leg both retrievers happen to fit τ = 0.05, so the transferred threshold
and the refitted one give identical operating points and the cost is exactly
zero. The transfer is wrong where the fitted thresholds differ and harmless
where they coincide — which is why a single global threshold cannot be
justified, and why the frontier has to be a curve.

### 3.3 The frontier as a curve

Each retriever's result now carries the **whole** sweep — all 19 thresholds
on the 0.05 grid, each with its answer rate, refusal rate, abstention
precision and coverage — and the **risk–coverage curve** on the held-out
half, 176 points long. The shipped report already described this in prose
("we sweep the threshold τ and report, for each, the fraction of answerable
questions answered, the fraction of unanswerable questions refused, the
abstention precision, and the coverage"); what was missing was that the sweep
was only ever run on one retriever.

### 3.4 The direction, stated precisely

The cross-category experiment already measured the same phenomenon along the
*category* axis (`impl/results/exp4_transfer.json`):

* the tuning half's τ = 0.05 applied to the held-out half answers **95.5%**
  of the answerable questions against **89.6%** for the refitted threshold,
  and refuses **21.5%** of the unanswerable ones against **30.6%**;
* leave-one-category-out is starker: for `facility_layout` the transferred
  τ = 0.05 answers **all ten** of the answerable questions and refuses
  **none** of the 144 unanswerable ones, where its own fit needs τ = 0.50
  and refuses everything.

Both experiments therefore show the same thing: **a threshold fitted on one
configuration is too permissive where it is transferred, and that flatters
the configuration it is transferred to.** The thesis's earlier wording — "a
threshold fitted on a weaker retrieval configuration is too permissive when
applied to a stronger one, which would flatter the weaker arm" — has the
logic of its last clause inconsistent with its first, and has been rewritten
in the deliverables to the sentence above, which is what the numbers support.

## 4. What this does not settle

* **It does not make a threshold portable.** A calibration that transferred
  across retrievers would need a retriever-independent feature rather than a
  calibrated score. Nothing here suggests one.
* **It does not cover the long-context arm.** That arm has no retrieval score
  at all, so it has no posterior to threshold; its threshold is a separate
  question, and it is reported as such in the generator-side experiment.
* **It is the focus domain only.** The focus corpus has one category, so the
  category pre-filter is inert here and the comparison is purely over
  retrievers. The six-category corpus is where the category axis is
  measurable, and that is where the cross-category numbers above come from.
* **It does not change the gate's behaviour in the shipped system.** The
  shipped retriever's numbers are unchanged — the re-implementation
  reproduced them exactly — so nothing in the deliverables' headline figures
  moves.

## 5. How to re-derive any of it

```bash
python impl/experiments/run_gate_per_retriever.py
```

writes `impl/results_focus/exp2b_gate_per_retriever.json`, from which
`results_source.gate_per_retriever_summary` reads the headline numbers and
the build substitutes them into the prose.
