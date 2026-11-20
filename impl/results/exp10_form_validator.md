# Experiment 10 -- Runtime query-form validation

The check refuses a request before retrieval if it is not a well-formed
question. A refusal is only acceptable if it is rare on well-formed
input, so both rates are reported together.

| Population | n | refused | rate |
|---|---|---|---|
| benchmark queries (all well formed) | 276 | 1 | 0.004 |
| hand-authored well formed | 35 | 0 | 0.000 |
| hand-authored malformed | 25 | 25 | 1.000 |
| harvested stems, hand-labelled malformed | 53 | 12 | 0.226 |
| harvested stems, hand-labelled well formed | 37 | 0 | 0.000 |
| counterfactual: the benchmark's own rule, on well-formed stems | 37 | 37 | 1.000 |

Cost: 3.9 microseconds per query.
