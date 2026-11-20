#!/bin/bash
# Re-run the gate on the benchmark as it stood BEFORE the unanswerable
# class was rebuilt, so that the before-and-after comparison rests on a
# generated measurement rather than on a number transcribed from a report.
#
# The pre-repair benchmark is preserved beside the current one, so this
# swaps the file, runs the experiment, writes the payload under its own
# name and puts the current benchmark back. Nothing else may be reading
# the benchmark while this runs.
set -e
set -o pipefail
cd /Users/ritikraj/Documents/MTP/impl
PY=/Users/ritikraj/Documents/MTP/.venv/bin/python

VARIANT="${MTP_VARIANT:-focus}"
if [ "$VARIANT" = "focus" ]; then
  BENCH=data/benchmark_focus
  OUTDIR=results_focus
else
  BENCH=data/benchmark
  OUTDIR=results
fi

CURRENT="$BENCH/benchmark.json"
PRE="$BENCH/benchmark_pre_unanswerable_repair.json"

if [ ! -r "$PRE" ]; then
  echo "rerun_pre_repair_gate: no preserved pre-repair benchmark at $PRE" >&2
  exit 1
fi

echo "=== run_gate on the pre-repair benchmark ==="
export MTP_VARIANT="$VARIANT"
# The benchmark file is overridden rather than swapped: the rest of the
# project reads it, and swapping a file another process may open is a race.
export MTP_BENCHMARK_FILE="$PRE"

# The experiment also writes the fitted gate model, which the generation
# experiment reads for its threshold. It is put back afterwards, so that
# running this does not change the repaired run's operating point.
ARTIFACTS="artifacts_focus"
[ "$VARIANT" = "focus" ] || ARTIFACTS="artifacts"
STASH="$(mktemp -t mtp_gate_model).json"
if [ -r "$ARTIFACTS/gate_model.json" ]; then
  cp "$ARTIFACTS/gate_model.json" "$STASH"
  RESTORE_GATE=1
else
  RESTORE_GATE=0
fi
STASH_RESULT="$(mktemp -t mtp_gate_result).json"
if [ -r "$OUTDIR/exp2_gate.json" ]; then
  cp "$OUTDIR/exp2_gate.json" "$STASH_RESULT"
else
  : > "$STASH_RESULT"
fi
# The experiment writes three artefacts: the JSON result, the markdown
# summary and the fitted gate model. All three have to be put back, or the
# project is left describing the pre-repair benchmark in some of them and the
# repaired one in the others -- which is exactly what happened: the JSON was
# restored and the markdown was not, so the two disagreed.
STASH_MD="$(mktemp -t mtp_gate_md).md"
if [ -r "$OUTDIR/exp2_gate.md" ]; then
  cp "$OUTDIR/exp2_gate.md" "$STASH_MD"
  RESTORE_MD=1
else
  : > "$STASH_MD"
  RESTORE_MD=0
fi
restore_gate() {
  if [ "$RESTORE_GATE" = "1" ]; then
    cp "$STASH" "$ARTIFACTS/gate_model.json"
  fi
  if [ "$RESTORE_MD" = "1" ]; then
    cp "$STASH_MD" "$OUTDIR/exp2_gate.md"
  fi
  rm -f "$STASH" "$STASH_RESULT" "$STASH_MD"
}
trap restore_gate EXIT

/usr/bin/time -p "$PY" experiments/run_gate.py 2>&1 \
  | tee "$OUTDIR/gate_pre_repair.log" \
  | grep -Ev "^\[W[0-9]|Redirects are currently|Warning: You are sending|^Loading weights"

cp "$OUTDIR/exp2_gate.json" "$OUTDIR/exp2_gate_pre_unanswerable_repair.json"
# The repaired run's own result is put back: this script measures the other
# benchmark and must not change what the project reports.
if [ -r "$STASH_RESULT" ]; then
  cp "$STASH_RESULT" "$OUTDIR/exp2_gate.json"
fi
echo "=== wrote $OUTDIR/exp2_gate_pre_unanswerable_repair.json ==="
