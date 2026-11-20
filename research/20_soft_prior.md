# 20 — The soft prior: the repair that was proposed and never tried

**Written:** 12 November 2026, six days before the defence.
**Closes:** gap **G6** from `research/16_open_items_register.md` §C, and with
it threat **T1** from `research/08_direction_check.md` §4.0.
**Artefact:** `impl/experiments/run_soft_prior.py` →
`impl/results/exp22_soft_prior.json`.

---

## 1. What was promised

`research/08_direction_check.md` §4.0, threat T1, is the only place in this
project where a repair for a measured defect was named in advance and then
not run:

> **The category pre-filter costs 7.7 R@10 points** (exp1: 0.730 → 0.653),
> contradicting H2.3's wording. … Re-state H2.3 as a negative-result
> hypothesis: *"a hard metadata category pre-filter is a recall liability on
> a small multi-category corpus."* Test the paired difference on the 240
> answerable queries with a paired bootstrap and a McNemar test on per-query
> hits; report the CI. **Then test the fix: replace the hard filter with a
> soft prior (e.g. a category-boosted RRF term) and report whether it
> recovers the [lost] points while keeping the cross-category benefit. If it
> does not, the negative result stands and should be the claim.**

The hypothesis was re-stated and the cost was measured. The fix was never
tried. This note tries it.

## 2. The design

Five configurations, the same corpus, the same queries, the same scorer. The
only thing that varies is what happens to the category.

| Configuration | What it does |
|---|---|
| `no_category` | no filter, no prior — the control |
| `hard_filter` | **the shipped configuration**: the candidate pool is restricted to the question's category before retrieval |
| `soft_prior_w0.25` | the whole corpus stays in the pool; the in-category chunks are promoted by an extra reciprocal-rank-fusion term of weight 0.25 |
| `soft_prior_w0.5` | the same, weight 0.5 |
| `soft_prior_w1.0` | the same, weight 1.0 — which is exactly one extra RRF list |

The soft prior is implemented as an **optional, default-off** parameter on
`Framework.retrieve` (`impl/src/pipeline.py`, `category_prior`). With the
default of 0 the hard pre-filter is exactly the shipped behaviour, and the
project's unit tests still pass unchanged.

The corpus is the **six-category** one (2,383 chunks, six categories), because
the focus domain has a single category and the filter is therefore inert
there. The 132 answerable queries are used; unanswerable queries have no gold
chunk, so the pre-filter has nothing to act on and every configuration scores
them identically.

## 3. The result

| Configuration | R@10 | R@20 | MRR | nDCG@10 |
|---|---|---|---|---|
| no_category | 0.9318 | 0.9394 | 0.7764 | 0.8143 |
| **hard_filter** (shipped) | 0.9318 | 0.9394 | **0.8025** | **0.8342** |
| soft_prior_w0.25 | 0.9318 | 0.9394 | 0.7764 | 0.8143 |
| soft_prior_w0.5 | 0.9318 | 0.9394 | 0.7764 | 0.8143 |
| soft_prior_w1.0 | 0.9318 | 0.9394 | 0.7764 | 0.8143 |

Paired tests, Wilcoxon signed-rank on the per-query values:

| Comparison | ΔR@10 | p | ΔMRR | p |
|---|---|---|---|---|
| hard_filter → no_category | 0.0000 | 1.000 | **+0.0261** | **0.027** |
| hard_filter → soft_prior (each weight) | 0.0000 | 1.000 | −0.0261 | 0.027 |

**Three findings, and the third is the interesting one.**

### 3.1 There is nothing for the repair to recover

The hard filter's recall cost on this corpus is **exactly zero** — ΔR@10 =
0.0000, p = 1.000 — and the reason is measurable rather than incidental:
**not one of the corpus's gold chunks sits outside its question's category**
(`n_out_of_category_gold` = 0 of 132). The 7.7-point cost that the threat
record describes was measured on the corpus the project had then, a 634-chunk
single-category corpus. On the corpora the thesis actually ships, the filter
costs no recall, so a repair aimed at recovering recall has nothing to
recover.

### 3.2 The filter's benefit is real, and it is in the ordering

Against no category handling at all, the hard filter raises MRR from 0.7764
to 0.8025 and nDCG@10 from 0.8143 to 0.8342, and the paired test on MRR is
significant (**p = 0.027**). So the filter is not a no-op on this corpus. It
is a no-op on *recall*, and it is a measurable gain in *ordering*.

### 3.3 The soft prior does not reproduce the benefit

Every soft prior tested returns the **no-category numbers exactly** — R@10
0.9318, MRR 0.7764, nDCG 0.8143 — and the difference from the hard filter is
significant on MRR (p = 0.027). The repair does not work, and the reason is
mechanical rather than a matter of tuning the weight.

The soft prior and the hard filter act on *different things*. The filter
**removes** the out-of-category chunks from the candidate pool; the prior
**reorders** the pool. Both change which fifty chunks the cross-encoder
scores — measured directly, the prior's pool differs from the control's on
every query — but the chunks it swaps in are deep in the fused ranking and
the reranker scores them below the chunks already in the final context, and
the chunks it swaps out were not in the final context either. On twelve
queries checked by hand, the final reranked top-ten was identical under the
prior and the control on eleven of them.

So the filter's benefit is not a promotion effect. It is that **removing**
the out-of-category chunks removes chunks the reranker *would* have ranked
highly — topically similar material that BM25 surfaced and the cross-encoder
approved — and replaces them with in-category material. A prior that only
reorders cannot do that.

**And this is the mechanism the pipeline's own documentation claims.** The
docstring in `impl/src/pipeline.py` says the filter matters because "the
candidate pool contains only in-category material, so … the reranker's
ranking [is] computed on the correct sub-corpus". That is the right
mechanism, and the measurement supports it. (The same docstring also claims
the filter changes "BM25's IDF statistics … computed on the correct
sub-corpus", which the code does **not** do: BM25 scores the whole corpus and
the filter is applied to the candidate list afterwards. Only the dense leg's
top-k and the reranker's pool are genuinely restricted.)

## 4. What this changes in the thesis

**The negative result stands, and it is now the claim.** T1 said: "If it does
not, the negative result stands and should be the claim." It does not. What
the thesis now says about the category pre-filter is:

* it is **not a recall liability** on the shipped corpora — it costs Δ 0.000
  Recall@10, because no gold chunk is out-of-category in the first place;
* it is **a measurable gain in ordering** on the six-category corpus, MRR
  +0.026 (paired p = 0.027);
* the repair proposed for it **does not work**, and the reason is that a
  prior reorders while a filter removes;
* so the pre-filter stays, and the *claim* about it is the ordering gain, not
  the recall loss that the old corpus showed.

**One sentence in the technical report was wrong and has been corrected.** Its
conclusion said the category pre-filter "is shown to trade overall recall for
modality precision". Neither half is true of the shipped corpora: the recall
is unchanged (Δ 0.000 on the six-category corpus; R@20 *rises* from 0.9960 to
1.0000 on the industrial one), and the per-modality recall is identical with
and without the filter on both. That sentence was a survivor of the corpus
change, and the soft-prior measurement is what exposed it.

## 5. What this does not settle

* **It does not test the soft prior on the industrial corpus.** The same
  experiment would run there with the same script
  (`MTP_VARIANT=industrial`), and the industrial corpus has four regimes
  rather than six categories.
* **It does not test a soft prior that also restricts the pool** — that is,
  the filter with a fallback rather than a hard cut. That is a different
  mechanism and a different experiment.
* **It does not change the shipped default.** The hard pre-filter is what the
  framework ships, the measurement says it should, and the prior remains
  available behind a default-off parameter for anyone who wants it.
* **It does not change the focus domain**, where the filter is inert because
  the corpus has one category.

## 6. How to re-derive any of it

```bash
python impl/experiments/run_soft_prior.py
```

writes `impl/results/exp22_soft_prior.json`, from which
`results_source.soft_prior_summary` reads the headline numbers and the build
substitutes them into the prose.
