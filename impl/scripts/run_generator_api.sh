#!/bin/bash
# Answer a generator sheet with the provider-hosted generator.
#
# The API key is read from a file outside the repository rather than passed on
# the command line, so it never appears in a shell history, in a process
# listing, or in a transcript:
#
#   install -m 600 /dev/stdin ~/.mtp_llm_key <<< 'sk-...'
#
# The defaults target MiniMax's Anthropic-compatible endpoint and the model
# that produced the focus corpus's answers, so the industrial replication is
# answered by the same generator as the measurement it replicates.
#
set -e
set -o pipefail
cd /Users/ritikraj/Documents/MTP/impl
PY=/Users/ritikraj/Documents/MTP/.venv/bin/python

KEY_FILE="${MTP_LLM_KEY_FILE:-$HOME/.mtp_llm_key}"
if [ ! -r "$KEY_FILE" ]; then
  echo "run_generator_api: no readable key file at $KEY_FILE" >&2
  echo "  install it with: install -m 600 /dev/stdin $KEY_FILE" >&2
  exit 1
fi
export MTP_LLM_API_KEY="$(cat "$KEY_FILE")"

export MTP_LLM_BASE_URL="${MTP_LLM_BASE_URL:-https://api.minimax.io/anthropic}"
export MTP_LLM_MODEL="${MTP_LLM_MODEL:-MiniMax-M3}"
export MTP_LLM_MAX_TOKENS="${MTP_LLM_MAX_TOKENS:-1024}"
export MTP_LLM_CACHE_CONTROL="${MTP_LLM_CACHE_CONTROL:-0}"
export MTP_VARIANT="${MTP_VARIANT:-industrial}"

exec "$PY" scripts/run_generator_api.py "$@"
