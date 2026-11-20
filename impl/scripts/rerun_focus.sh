#!/bin/bash
# Run every experiment against the focus-domain (supply chain) corpus.
#
# The focus corpus is the single industrial domain the thesis is about. It
# lives in data/corpus_focus, and MTP_VARIANT=focus points the framework's
# data paths at it -- same code, no conditionals.
#
# `set -o pipefail` matters: without it a failed experiment exits zero
# through the `tee | grep` pipeline, and the run reports success having
# measured nothing.
set -e
set -o pipefail
cd /Users/ritikraj/Documents/MTP/impl
PY=/Users/ritikraj/Documents/MTP/.venv/bin/python
export MTP_VARIANT=focus

echo "=== clearing stale focus artefacts ==="
rm -rf artifacts_focus results_focus
mkdir -p artifacts_focus results_focus

echo ""
echo "=== rebuilding the focus benchmark ==="
"$PY" scripts/build_benchmark.py 2>&1 | grep -Ev "^\[W[0-9]|Redirects are currently"

# The generator-side arm (run_generation_eval) needs an API credential and
# incurs charges. Without one it records itself as not run, which is what the
# deliverables then say. To run it against a real generator, use
# scripts/run_generation_eval.sh -- it reads the key from ~/.mtp_llm_key.
for exp in run_gate run_ablation run_contradiction run_transfer run_pool_size run_long_context run_generation_eval validate_claim_scorer audit_answer_side audit_unanswerable_class run_focus_case; do
  echo ""
  echo "=== $exp (focus) ==="
  # The generator arm reads its credential from a file outside the
  # repository, so it is invoked through its wrapper rather than directly:
  # calling experiments/run_generation_eval.py would find no key and record
  # the arm as not run.
  if [ "$exp" = "run_generation_eval" ]; then
    bash scripts/run_generation_eval.sh 2>&1 \
      | tee "results_focus/${exp#run_}.log" \
      | grep -Ev "^\[W[0-9]|Redirects are currently|Warning: You are sending|^Loading weights"
  elif [ "$exp" = "audit_unanswerable_class" ]; then
    # The audit of the unanswerable half also needs a credential: it asks
    # the generator the questions with no corpus in the prompt, and it runs
    # the question-only policy.
    bash scripts/run_unanswerable_audit.sh 2>&1 \
      | tee "results_focus/${exp}.log" \
      | grep -Ev "^\[W[0-9]|Redirects are currently|Warning: You are sending|^Loading weights"
  else
    /usr/bin/time -p "$PY" "experiments/$exp.py" 2>&1 \
      | tee "results_focus/${exp#run_}.log" \
      | grep -Ev "^\[W[0-9]|Redirects are currently|Warning: You are sending|^Loading weights"
  fi
done

# The generator-side comparison under its second prompt condition: the
# generator required to answer rather than permitted to decline. Without it
# the gate's own contribution cannot be separated from the generator's
# willingness to decline.
echo ""
echo "=== run_generation_eval (answering condition, focus) ==="
bash scripts/run_generation_eval.sh --condition answering 2>&1 \
  | tee "results_focus/generation_eval_answering.log" \
  | grep -Ev "^\[W[0-9]|Redirects are currently|Warning: You are sending|^Loading weights"

# How long a query takes, stage by stage. It needs no credential: the
# retrieval path is measured on the real index with the real models, and the
# generation stage is derived from the archived arm totals.
echo ""
echo "=== run_latency (focus) ==="
/usr/bin/time -p "$PY" "experiments/run_latency.py" 2>&1 \
  | tee "results_focus/latency.log" \
  | grep -Ev "^\[W[0-9]|Redirects are currently|Warning: You are sending|^Loading weights"

echo ""
echo "=== FOCUS EXPERMENTS DONE ==="
