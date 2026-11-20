#!/bin/bash
# Rebuild the index and re-run every experiment on the current corpus.
#
# The cached artefacts are cleared first, deliberately:
#   * index.npy/index.json -- the corpus changed, so the index must be rebuilt.
#   * rerank_scores.json  -- the cache key is (query, len(pool), pool[0],
#     pool[-1]); it samples only the endpoints of the pool, so a changed
#     corpus can collide with a stale entry. Deleting it is the only safe
#     invalidation.
#   * gate_model.json     -- the gate's calibration must be refitted on the
#     new benchmark, not carried over.
#
# `set -o pipefail` matters: without it a failed experiment exits zero
# through the `tee | grep` pipeline, and the run reports success having
# measured nothing.
set -e
set -o pipefail
cd /Users/ritikraj/Documents/MTP/impl
PY=/Users/ritikraj/Documents/MTP/.venv/bin/python

echo "=== clearing stale artefacts ==="
rm -f artifacts/index.npy artifacts/index.json artifacts/rerank_scores.json \
      artifacts/gate_model.json

echo ""
echo "=== rebuilding the benchmark (gold chunk ids depend on the corpus) ==="
"$PY" scripts/build_benchmark.py 2>&1 | grep -Ev "^\[W[0-9]|Redirects are currently"

for exp in run_ablation run_gate run_contradiction run_transfer run_pool_size run_long_context; do
  echo ""
  echo "=== $exp ==="
  /usr/bin/time -p "$PY" "experiments/$exp.py" 2>&1 \
    | tee "results/${exp#run_}.log" \
    | grep -Ev "^\[W[0-9]|Redirects are currently|Warning: You are sending|^Loading weights"
done

# The audit of the benchmark's unanswerable half needs a credential: it
# asks the generator the questions with no corpus in the prompt, and it
# runs the question-only policy.
echo ""
echo "=== audit_unanswerable_class ==="
MTP_VARIANT="" bash scripts/run_unanswerable_audit.sh 2>&1 \
  | tee "results/audit_unanswerable_class.log" \
  | grep -Ev "^\[W[0-9]|Redirects are currently|Warning: You are sending|^Loading weights"

echo ""
echo "=== ALL EXPERIMENTS DONE ==="
