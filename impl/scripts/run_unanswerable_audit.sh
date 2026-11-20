#!/bin/bash
# Run Experiment 12 -- the audit of the benchmark's unanswerable half.
#
# The API key is read from a file outside the repository rather than passed
# on the command line, so it never appears in a shell history, in a process
# listing, or in a transcript:
#
#   install -m 600 /dev/stdin ~/.mtp_llm_key <<< 'sk-...'
#
# The defaults target MiniMax's Anthropic-compatible endpoint and the same
# model the generation experiment uses, so the question-only policy is
# measured with the generator that is measured elsewhere.
#
set -e
set -o pipefail
cd /Users/ritikraj/Documents/MTP/impl
PY=/Users/ritikraj/Documents/MTP/.venv/bin/python

KEY_FILE="${MTP_LLM_KEY_FILE:-$HOME/.mtp_llm_key}"
if [ ! -r "$KEY_FILE" ]; then
  echo "run_unanswerable_audit: no readable key file at $KEY_FILE" >&2
  echo "  install it with: install -m 600 /dev/stdin $KEY_FILE" >&2
  exit 1
fi
export MTP_LLM_API_KEY="$(cat "$KEY_FILE")"

# An explicitly empty MTP_VARIANT means "the default corpus", which is
# what the multi-category run needs; only an unset value falls back to
# the focus domain.
export MTP_VARIANT="${MTP_VARIANT-focus}"
export MTP_LLM_BASE_URL="${MTP_LLM_BASE_URL:-https://api.minimax.io/anthropic}"
export MTP_LLM_MODEL="${MTP_LLM_MODEL:-MiniMax-M3}"
export MTP_LLM_CONTEXT_LIMIT="${MTP_LLM_CONTEXT_LIMIT:-1000000}"

exec "$PY" experiments/audit_unanswerable_class.py "$@"
