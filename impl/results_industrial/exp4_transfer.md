# Experiment 4 -- Cross-category transfer

Tuning half: ['hazmat_transport', 'occupational_safety']

Held-out half: ['environmental_control', 'process_safety']

tau (fitted on the tuning half, transferred unchanged) = 0.05

Each arm is evaluated on the queries it is about: the transferred arm carries the tuning half's model AND threshold unchanged onto the held-out half; the refitted arm is the held-out half's own model and threshold, and is the ceiling.

The split is over document categories, and the benchmark's unanswerable questions carry no category, so neither half contains any. This experiment therefore measures coverage on the answerable questions across domains, and says nothing about refusal behaviour across domains.

| Metric (held-out half) | Transferred | Refitted |
|---|---|---|
| Answerable answered | 1.000 | 1.000 |
| Answerable refused | 0.000 | 0.000 |
| Coverage | 0.543 | 0.517 |
| Top-1 accuracy given accepted | 1.000 | 1.000 |

### Per-category retrieval quality

| Category | n | R@10 | MRR | nDCG@10 |
|---|---|---|---|---|
| environmental_control | 79 | 0.962 | 0.693 | 0.758 |
| hazmat_transport | 50 | 1.000 | 0.816 | 0.862 |
| occupational_safety | 92 | 0.978 | 0.821 | 0.859 |
| process_safety | 26 | 1.000 | 0.782 | 0.837 |
