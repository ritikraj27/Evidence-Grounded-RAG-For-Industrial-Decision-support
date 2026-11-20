# Experiment 4 -- Cross-category transfer

Tuning half: ['predictive_maintenance', 'production_scheduling', 'supply_chain_management']

Held-out half: ['facility_layout', 'quality_engineering', 'reliability_engineering']

tau (fitted on the tuning half, transferred unchanged) = 0.05

Each arm is evaluated on the queries it is about: the transferred arm carries the tuning half's model AND threshold unchanged onto the held-out half; the refitted arm is the held-out half's own model and threshold, and is the ceiling.

The split is over document categories, and the benchmark's unanswerable questions carry no category, so neither half contains any. This experiment therefore measures coverage on the answerable questions across domains, and says nothing about refusal behaviour across domains.

| Metric (held-out half) | Transferred | Refitted |
|---|---|---|
| Answerable answered | 1.000 | 0.940 |
| Answerable refused | 0.000 | 0.060 |
| Coverage | 0.412 | 0.460 |
| Top-1 accuracy given accepted | 0.940 | 0.952 |

### Per-category retrieval quality

| Category | n | R@10 | MRR | nDCG@10 |
|---|---|---|---|---|
| facility_layout | 10 | 1.000 | 0.625 | 0.714 |
| predictive_maintenance | 24 | 0.958 | 0.813 | 0.849 |
| production_scheduling | 11 | 1.000 | 0.718 | 0.787 |
| quality_engineering | 23 | 1.000 | 0.651 | 0.738 |
| reliability_engineering | 34 | 0.853 | 0.590 | 0.652 |
| supply_chain_management | 30 | 1.000 | 0.811 | 0.857 |
