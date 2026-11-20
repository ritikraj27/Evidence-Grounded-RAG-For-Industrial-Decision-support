#!/bin/bash
# Run Experiment 8 -- the generator-side comparison -- against a real
# generator.
#
# The API key is read from a file outside the repository rather than passed on
# the command line, so it never appears in a shell history, in a process
# listing, or in a transcript:
#
#   install -m 600 /dev/stdin ~/.mtp_llm_key <<< 'sk-...'
#
# The defaults target MiniMax's Anthropic-compatible endpoint, whose two live
# models (MiniMax-M3 and MiniMax-M3.1-Flash) both have a 1M-token context
# window -- the focus corpus is about 203k tokens, so the long-context arm
# fits comfortably. Override with the MTP_LLM_* variables below.
#
# This run costs money. A smoke test that exercises the same code path for a
# fraction of the cost:
#
#   MTP_GEN_UNANSWERABLE=2 ./scripts/run_generation_eval.sh
#
# The prompt condition is an axis. The default, `cautious`, is the deployed
# system; `answering` removes the permission to decline so that the gate's
# own contribution is measurable against a generator that answers:
#
#   ./scripts/run_generation_eval.sh --condition answering
#
set -e
set -o pipefail
cd /Users/ritikraj/Documents/MTP/impl
PY=/Users/ritikraj/Documents/MTP/.venv/bin/python

KEY_FILE="${MTP_LLM_KEY_FILE:-$HOME/.mtp_llm_key}"
if [ ! -r "$KEY_FILE" ]; then
  echo "run_generation_eval: no readable key file at $KEY_FILE" >&2
  echo "  install it with: install -m 600 /dev/stdin $KEY_FILE" >&2
  exit 1
fi
export MTP_LLM_API_KEY="$(cat "$KEY_FILE")"

export MTP_VARIANT="${MTP_VARIANT:-focus}"
export MTP_LLM_BASE_URL="${MTP_LLM_BASE_URL:-https://api.minimax.io/anthropic}"
export MTP_LLM_MODEL="${MTP_LLM_MODEL:-MiniMax-M3}"
export MTP_LLM_CONTEXT_LIMIT="${MTP_LLM_CONTEXT_LIMIT:-1000000}"
# The long-context arm sends the identical corpus prefix on every query, so
# it is sent as a cached prefix. MiniMax's Anthropic-compatible route honours
# `cache_control` and serves the repeat reads at the discounted rate, which
# is what such a system would actually pay.
export MTP_LLM_CACHE_CONTROL="${MTP_LLM_CACHE_CONTROL:-1}"
export MTP_GEN_UNANSWERABLE="${MTP_GEN_UNANSWERABLE:-0}"
# The budget counts cached reads too, so the long-context arm's 177 requests
# of a 202k-token corpus come to roughly 36M tokens. The default cap of 20M
# would stop the run partway through the last arm.
export MTP_LLM_MAX_INPUT_TOKENS="${MTP_LLM_MAX_INPUT_TOKENS:-200000000}"

exec "$PY" experiments/run_generation_eval.py "$@"
