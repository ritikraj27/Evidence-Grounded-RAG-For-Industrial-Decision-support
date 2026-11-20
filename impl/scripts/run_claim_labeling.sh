#!/bin/bash
# Run the model annotator for the per-claim confidence bands (RO5).
#
# The API key is read from a file outside the repository rather than passed on
# the command line, so it never appears in a shell history, in a process
# listing, or in a transcript:
#
#   install -m 600 /dev/stdin ~/.mtp_llm_key <<< 'sk-...'
#
# The defaults target MiniMax's Anthropic-compatible endpoint and the same
# model the generation experiment uses, so the annotator is a different model
# family from the NLI model that produces the band it is judging -- which is
# the point: the reference labels have to come from somewhere the band does
# not.
#
set -e
set -o pipefail
cd /Users/ritikraj/Documents/MTP/impl
PY=/Users/ritikraj/Documents/MTP/.venv/bin/python

KEY_FILE="${MTP_LLM_KEY_FILE:-$HOME/.mtp_llm_key}"
if [ ! -r "$KEY_FILE" ]; then
  echo "run_claim_labeling: no readable key file at $KEY_FILE" >&2
  echo "  install it with: install -m 600 /dev/stdin $KEY_FILE" >&2
  exit 1
fi
export MTP_LLM_API_KEY="$(cat "$KEY_FILE")"

export MTP_LLM_BASE_URL="${MTP_LLM_BASE_URL:-https://api.minimax.io/anthropic}"
export MTP_LLM_MODEL="${MTP_LLM_MODEL:-MiniMax-M3}"
export MTP_LLM_CACHE_CONTROL="${MTP_LLM_CACHE_CONTROL:-1}"
export MTP_JUDGE_NAME="${MTP_JUDGE_NAME:-judge_a_model}"

exec "$PY" experiments/label_claim_bands_model.py "$@"
