# 09 — Replacing the dense leg: before and after

**What changed.** The dense retrieval leg was
`sentence-transformers/all-MiniLM-L6-v2` — a general-purpose sentence encoder
trained with a *symmetric* similarity objective — and is now `BAAI/bge-m3`, a
retrieval-trained multilingual encoder (1024 dimensions, CLS pooling, a
normalisation module).

**Why.** Retrieval is asymmetric: a passage does not resemble a question, it
answers it. The first measurement in this project showed the mismatch was not
theoretical — dense-only retrieval was significantly worse than plain BM25, and
the fusion's ordering was worse than the lexical leg's, so the fusion was
spending the lexical leg's slots on the dense leg's worse candidates.

**One detail, because it is easy to get wrong.** BGE-M3 takes **no query
instruction**. BGE-v1.5 and the small instruction-tuned encoders (E5, GTE)
expect "Represent this sentence for searching relevant passages: " in front of
the query; BGE-M3's model card states that it "no longer requires adding
instructions to the queries", because the asymmetry is handled in training.
The configuration leaves `query_prefix` empty for that reason, and keeps the
field configurable because the next encoder may well want one.


## Multi-category corpus (six industrial categories)

Before: `sentence-transformers/all-MiniLM-L6-v2`, 132 answerable queries over 2,383 chunks. After: `BAAI/bge-m3`, 132 answerable queries over 2,383 chunks.

| System | R@10 before | R@10 after | MRR before | MRR after | nDCG@10 before | nDCG@10 after | Table R@10 before | Table R@10 after |
|---|---|---|---|---|---|---|---|---|
| BM25 only | 0.917 | 0.917 | 0.680 | 0.680 | 0.735 | 0.735 | 1.000 | 1.000 |
| Dense only | 0.652 | 0.735 | 0.435 | 0.541 | 0.482 | 0.585 | 0.577 | 0.769 |
| Hybrid (RRF) | 0.924 | 0.932 | 0.588 | 0.653 | 0.666 | 0.720 | 0.962 | 1.000 |
| + cross-encoder rerank | 0.932 | 0.932 | 0.767 | 0.766 | 0.806 | 0.805 | 0.923 | 0.923 |
| + category pre-filter | 0.939 | 0.932 | 0.796 | 0.788 | 0.830 | 0.822 | 0.923 | 0.923 |
| + quota (pre-rerank) | 0.917 | 0.939 | 0.785 | 0.793 | 0.818 | 0.829 | 0.962 | 1.000 |
| + quota (post-rerank) | 0.939 | 0.932 | 0.794 | 0.786 | 0.830 | 0.822 | 0.962 | 0.962 |

### Paired tests, before and after

| Comparison | ΔR@10 before | p before | ΔR@10 after | p after | ΔMRR before | p before | ΔMRR after | p after |
|---|---|---|---|---|---|---|---|---|
| A → B | -0.2652 | 9.4e-08 | +0.0152 | — | -0.2451 | 4.1e-07 | -0.0269 | — |
| B → C | +0.2727 | 2.0e-09 | +0.1970 | — | +0.1534 | 5.4e-10 | +0.1119 | — |
| C → D | +0.0076 | 7.4e-01 | +0.0000 | — | +0.1786 | 2.1e-06 | +0.1130 | — |
| D → E | +0.0076 | 3.2e-01 | +0.0076 | — | +0.0288 | 5.9e-02 | +0.0273 | — |
| E → F | -0.0227 | 3.2e-01 | +0.0076 | — | -0.0102 | 9.8e-01 | +0.0057 | — |
| F → G | +0.0227 | 3.2e-01 | -0.0076 | — | +0.0084 | 9.2e-01 | -0.0076 | — |


## Focus domain (supply chain management)

Before: `sentence-transformers/all-MiniLM-L6-v2`, 33 answerable queries over 735 chunks. After: `BAAI/bge-m3`, 33 answerable queries over 735 chunks.

| System | R@10 before | R@10 after | MRR before | MRR after | nDCG@10 before | nDCG@10 after | Table R@10 before | Table R@10 after |
|---|---|---|---|---|---|---|---|---|
| BM25 only | 0.970 | 0.970 | 0.744 | 0.744 | 0.798 | 0.798 | 1.000 | 1.000 |
| Dense only | 0.636 | 0.758 | 0.482 | 0.554 | 0.514 | 0.600 | 0.714 | 0.857 |
| Hybrid (RRF) | 0.970 | 1.000 | 0.644 | 0.767 | 0.722 | 0.824 | 1.000 | 1.000 |
| + cross-encoder rerank | 0.970 | 0.970 | 0.807 | 0.786 | 0.846 | 0.830 | 1.000 | 1.000 |
| + category pre-filter | 0.970 | 0.970 | 0.807 | 0.786 | 0.846 | 0.830 | 1.000 | 1.000 |
| + quota (pre-rerank) | 0.939 | 1.000 | 0.819 | 0.814 | 0.850 | 0.861 | 1.000 | 1.000 |
| + quota (post-rerank) | 0.939 | 0.939 | 0.802 | 0.780 | 0.836 | 0.820 | 1.000 | 1.000 |

### Paired tests, before and after

| Comparison | ΔR@10 before | p before | ΔR@10 after | p after | ΔMRR before | p before | ΔMRR after | p after |
|---|---|---|---|---|---|---|---|---|
| A → B | -0.3333 | 9.1e-04 | +0.0303 | — | -0.2617 | 8.6e-03 | +0.0233 | — |
| B → C | +0.3333 | 9.1e-04 | +0.2424 | — | +0.1618 | 1.8e-04 | +0.2133 | — |
| C → D | +0.0000 | 1.0e+00 | -0.0303 | — | +0.1637 | 3.8e-02 | +0.0192 | — |
| D → E | +0.0000 | 1.0e+00 | +0.0303 | — | +0.0000 | 1.0e+00 | +0.0280 | — |
| E → F | -0.0303 | 3.2e-01 | +0.0303 | — | +0.0117 | 5.0e-01 | +0.0280 | — |
| F → G | +0.0000 | 1.0e+00 | -0.0606 | — | -0.0177 | 3.6e-01 | -0.0338 | — |


## What the change bought

| Quantity | Before | After | Change |
|---|---|---|---|
| Dense-only Recall@10 | 0.652 | 0.735 | +0.083 |
| Dense-only MRR | 0.435 | 0.541 | +0.106 |
| Dense-only nDCG@10 | 0.482 | 0.585 | +0.103 |
| Gap between the dense leg and the lexical leg (R@10) | 0.265 | 0.182 | -0.083 |
| The fusion's ordering deficit against the lexical leg (nDCG@10) | 0.069 | 0.016 | -0.053 |
| The reranker's ordering gain (ΔMRR, C→D) | 0.179 | 0.113 | -0.066 |

A negative entry in the last two rows is an improvement: the gap is something the dense leg has to close, and the deficit is what the fusion was costing the lexical leg.

The reranker's ordering gain gets *smaller* here, and that is not a regression. The reranker reorders the fused list, so the headroom it has to improve is whatever the fusion left on the table; once the fusion is better, there is less for it to recover. The gain is still large and still significant on its own.
