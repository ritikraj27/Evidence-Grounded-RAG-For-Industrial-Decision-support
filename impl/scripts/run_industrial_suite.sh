#!/bin/bash
# Run the retrieval-side experiments on the authentic industrial corpus (RO6).
#
# The corpus is a third variant alongside the six-category and focus corpora,
# and the `MTP_VARIANT` mechanism points every path at it without a single
# conditional in the code:
#
#   data/corpus_industrial    the eCFR corpus
#   data/benchmark_industrial its benchmark
#   artifacts_industrial      the index, the fitted gate model, the score cache
#   results_industrial        the measurements
#
# The order matters: the ablation establishes that the pipeline runs and
# which systems differ, the gate fit produces the calibrated model the later
# experiments load, and the transfer experiment needs both.
#
set -e
set -o pipefail
cd /Users/ritikraj/Documents/MTP/impl
PY=/Users/ritikraj/Documents/MTP/.venv/bin/python

export MTP_VARIANT=industrial

# The cross-encoder pass is the most expensive step in the suite and torch
# defaults to a conservative thread count. This is a wall-clock setting, not
# a result: the same (query, passage) pairs are scored either way.
export MTP_TORCH_THREADS="${MTP_TORCH_THREADS:-$(sysctl -n hw.ncpu 2>/dev/null || echo 4)}"

# The fitted gate model is cleared, deliberately. It is calibrated on the
# contexts a particular retrieval configuration produces, so a model left
# over from an earlier configuration describes a gate that was fitted
# against different contexts. The gate fit below refits it.
#
# The rerank score cache is kept: the cache key is (query, len(pool),
# pool[0], pool[-1]) over the candidate pool, and the pool the cross-encoder
# scores is the same whatever the quota does afterwards, so the cached
# scores are still the right ones. Clearing it would cost an hour of
# re-scoring and change no number.
rm -f artifacts_industrial/gate_model.json

echo "=== exp1: retrieval ablation ==="
# The unanswerable queries have no gold chunk; every aggregate and every
# paired statistic already excludes them, so dropping them here changes no
# reported number and saves a cross-encoder pass per query.
$PY experiments/run_ablation.py --answerable-only

echo "=== exp2: the confidence gate ==="
$PY experiments/run_gate.py

echo "=== exp5: the candidate-pool sweep ==="
# The unanswerable queries have empty gold sets and contribute nothing to
# recall, MRR or nDCG, but each one still costs a cross-encoder pass over
# its candidate pool. On this corpus the unanswerable class is the larger
# half, so skipping them is a large saving and changes no number.
$PY experiments/run_pool_size.py --answerable-only

echo "=== exp4: cross-category transfer ==="
$PY experiments/run_transfer.py

echo "=== done ==="
ls -la results_industrial/
