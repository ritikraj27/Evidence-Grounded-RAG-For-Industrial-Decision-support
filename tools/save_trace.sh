#!/usr/bin/env bash
#
# save_trace.sh - persist one cross-model reviewer call as a review trace.
#
# Contract (from the skills that call it):
#
#   citation-audit/SKILL.md:112   "Save the response to
#                                  .aris/traces/citation-audit/<date>_runNN/<key>.md
#                                  per the review-tracing protocol."
#   citation-audit/SKILL.md:301, paper-claim-audit/SKILL.md:247,
#   figure-spec/SKILL.md:221, idea-creator/SKILL.md:321,
#   novelty-check/SKILL.md:90, rebuttal/SKILL.md:326:
#
#     "Use `tools/save_trace.sh` or write files directly to
#      .aris/traces/<skill>/<date>_run<NN>/.
#      Respect the `--- trace:` parameter (default: `full`)."
#
# The trace directory layout matches the "trace_path" field of the audit
# artifacts (citation-audit/SKILL.md:414, paper-claim-audit/SKILL.md:271,
# proof-checker/SKILL.md:579):
#
#     .aris/traces/<skill>/<date>_run<NN>/<key>.md
#
# The `--- trace:` skill parameter is mapped onto --mode:
#     full  -> prompt + response, verbatim      (default)
#     brief -> metadata + response excerpt (--max-lines lines)
#     off   -> nothing is written
#
set -euo pipefail

SCRIPT_NAME="save_trace.sh"
SCRIPT_VERSION="1.0"

# ---------------------------------------------------------------- usage ----

usage() {
  cat <<'USAGE'
save_trace.sh - save one cross-model reviewer call as a review trace.

Usage:
  bash tools/save_trace.sh --skill <name> --key <key> [options]
  bash tools/save_trace.sh <skill> <key> < response.md

Options:
  -h, --help              Show this help and exit 0.
  -s, --skill <name>      Skill that produced the trace, e.g. citation-audit.
                          Required (may also be given positionally).
  -k, --key <key>         Trace key / file stem, e.g. lu2024aiscientist.
                          Required (may also be given positionally).
  -r, --response <text>   Reviewer response text.
  -R, --response-file <p> File holding the reviewer response ("-" = stdin).
  -p, --prompt <text>     Prompt that was sent to the reviewer.
  -P, --prompt-file <p>   File holding the prompt ("-" = stdin).
  -d, --date <YYYY-MM-DD> Date stamp for the trace directory.
                          Default: today (local time).
  -n, --run <NN>          Run number inside the trace directory.
                          Default: the next free run for that date.
  -m, --mode <mode>       Trace level: full | brief | off.  Default: full.
      --max-lines <n>     In brief mode, how many response lines to keep.
                          Default: 40.
  -o, --root <dir>        Project root that owns .aris/.
                          Default: $ARIS_ROOT, else the current directory when it
                          looks like a project root, else this script's parent dir.
  -b, --base-dir <dir>    Trace base directory.
                          Default: <root>/.aris/traces
      --thread-id <id>    Reviewer thread id, recorded in the trace.
      --reviewer-model <m>   Reviewer model, recorded in the trace.
      --reviewer-reasoning <r> Reviewer reasoning effort, recorded in the trace.
  -q, --quiet             Do not echo the written path.

Output:
  Writes <root>/.aris/traces/<skill>/<date>_run<NN>/<key>.md
  and prints that path on stdout (unless --quiet).

Exit codes:
  0  trace written (or deliberately skipped in --mode off)
  1  usage error / unreadable input / unwritable output
USAGE
}

die() {
  printf '%s: error: %s\n' "$SCRIPT_NAME" "$*" >&2
  exit 1
}

warn() {
  printf '%s: warning: %s\n' "$SCRIPT_NAME" "$*" >&2
}

# ------------------------------------------------------------ arg parse ----

SKILL=""
KEY=""
RESPONSE=""
RESPONSE_FILE=""
PROMPT=""
PROMPT_FILE=""
DATE=""
RUN=""
MODE="full"
MAX_LINES=40
ROOT=""
BASE_DIR=""
THREAD_ID="${ARIS_THREAD_ID:-}"
REVIEWER_MODEL="${ARIS_REVIEWER_MODEL:-}"
REVIEWER_REASONING="${ARIS_REVIEWER_REASONING:-}"
QUIET=0
POSITIONAL=()

while [ $# -gt 0 ]; do
  case "$1" in
    -h|--help) usage; exit 0 ;;
    -s|--skill)   [ $# -ge 2 ] || die "--skill requires a value"; SKILL="$2"; shift 2 ;;
    --skill=*)    SKILL="${1#*=}"; shift ;;
    -k|--key)     [ $# -ge 2 ] || die "--key requires a value"; KEY="$2"; shift 2 ;;
    --key=*)      KEY="${1#*=}"; shift ;;
    -r|--response)   [ $# -ge 2 ] || die "--response requires a value"; RESPONSE="$2"; shift 2 ;;
    --response=*)    RESPONSE="${1#*=}"; shift ;;
    -R|--response-file) [ $# -ge 2 ] || die "--response-file requires a path"; RESPONSE_FILE="$2"; shift 2 ;;
    --response-file=*) RESPONSE_FILE="${1#*=}"; shift ;;
    -p|--prompt)   [ $# -ge 2 ] || die "--prompt requires a value"; PROMPT="$2"; shift 2 ;;
    --prompt=*)    PROMPT="${1#*=}"; shift ;;
    -P|--prompt-file) [ $# -ge 2 ] || die "--prompt-file requires a path"; PROMPT_FILE="$2"; shift 2 ;;
    --prompt-file=*) PROMPT_FILE="${1#*=}"; shift ;;
    -d|--date)   [ $# -ge 2 ] || die "--date requires a value"; DATE="$2"; shift 2 ;;
    --date=*)    DATE="${1#*=}"; shift ;;
    -n|--run)    [ $# -ge 2 ] || die "--run requires a value"; RUN="$2"; shift 2 ;;
    --run=*)     RUN="${1#*=}"; shift ;;
    -m|--mode)   [ $# -ge 2 ] || die "--mode requires a value"; MODE="$2"; shift 2 ;;
    --mode=*)    MODE="${1#*=}"; shift ;;
    --max-lines) [ $# -ge 2 ] || die "--max-lines requires a value"; MAX_LINES="$2"; shift 2 ;;
    --max-lines=*) MAX_LINES="${1#*=}"; shift ;;
    -o|--root)   [ $# -ge 2 ] || die "--root requires a path"; ROOT="$2"; shift 2 ;;
    --root=*)    ROOT="${1#*=}"; shift ;;
    -b|--base-dir) [ $# -ge 2 ] || die "--base-dir requires a path"; BASE_DIR="$2"; shift 2 ;;
    --base-dir=*) BASE_DIR="${1#*=}"; shift ;;
    --thread-id) [ $# -ge 2 ] || die "--thread-id requires a value"; THREAD_ID="$2"; shift 2 ;;
    --thread-id=*) THREAD_ID="${1#*=}"; shift ;;
    --reviewer-model) [ $# -ge 2 ] || die "--reviewer-model requires a value"; REVIEWER_MODEL="$2"; shift 2 ;;
    --reviewer-model=*) REVIEWER_MODEL="${1#*=}"; shift ;;
    --reviewer-reasoning) [ $# -ge 2 ] || die "--reviewer-reasoning requires a value"; REVIEWER_REASONING="$2"; shift 2 ;;
    --reviewer-reasoning=*) REVIEWER_REASONING="${1#*=}"; shift ;;
    -q|--quiet)  QUIET=1; shift ;;
    --) shift; while [ $# -gt 0 ]; do POSITIONAL[${#POSITIONAL[@]}]="$1"; shift; done ;;
    -*) printf '%s: error: unknown option: %s\n' "$SCRIPT_NAME" "$1" >&2; usage >&2; exit 1 ;;
    *)  POSITIONAL[${#POSITIONAL[@]}]="$1"; shift ;;
  esac
done

if [ -z "$SKILL" ] && [ "${#POSITIONAL[@]}" -ge 1 ]; then SKILL="${POSITIONAL[0]}"; fi
if [ -z "$KEY" ] && [ "${#POSITIONAL[@]}" -ge 2 ]; then KEY="${POSITIONAL[1]}"; fi

[ -n "$SKILL" ] || die "--skill is required"
[ -n "$KEY" ] || die "--key is required"

case "$MODE" in
  full|complete) MODE="full" ;;
  brief|summary|short|minimal) MODE="brief" ;;
  off|none|no|false) MODE="off" ;;
  *) die "unknown --mode '$MODE' (expected: full, brief, off)" ;;
esac

# Sanitize the skill and key so they are safe path components.
sanitize() {
  printf '%s' "$1" | sed -e 's/[^A-Za-z0-9._-]/_/g' -e 's/^\.\+$/_/g'
}
SKILL="$(sanitize "$SKILL")"
KEY="$(sanitize "$KEY")"

# ----------------------------------------------------------- resolve root ---

script_dir() {
  local src="$1" dir
  while [ -L "$src" ]; do
    dir="$(cd -P "$(dirname "$src")" && pwd)"
    src="$(readlink "$src")"
    case "$src" in
      /*) ;;
      *) src="$dir/$src" ;;
    esac
  done
  cd -P "$(dirname "$src")" && pwd
}

SELF_DIR="$(script_dir "$0")"

if [ -z "$ROOT" ]; then
  if [ -n "${ARIS_ROOT:-}" ]; then
    ROOT="$ARIS_ROOT"
  elif [ -d "$PWD/.claude" ] || [ -d "$PWD/tools" ] || [ -d "$PWD/.aris" ]; then
    ROOT="$PWD"
  else
    ROOT="$(cd "$SELF_DIR/.." && pwd)"
  fi
fi
[ -d "$ROOT" ] || die "--root '$ROOT' is not a directory"
ROOT="$(cd "$ROOT" && pwd)"

if [ -z "$BASE_DIR" ]; then
  BASE_DIR="${ARIS_TRACES_DIR:-$ROOT/.aris/traces}"
fi

# ------------------------------------------------------------- date/run ----

if [ -z "$DATE" ]; then
  DATE="$(date +%Y-%m-%d)"
fi
case "$DATE" in
  [0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]) ;;
  *) die "--date must be YYYY-MM-DD (got '$DATE')" ;;
esac

SKILL_DIR="$BASE_DIR/$SKILL"

if [ -z "$RUN" ]; then
  max_run=0
  if [ -d "$SKILL_DIR" ]; then
    for d in "$SKILL_DIR"/*_run*; do
      [ -d "$d" ] || continue
      n="$(basename "$d")"
      n="${n#*_run}"
      case "$n" in
        ''|*[!0-9]*) continue ;;
      esac
      if [ "$n" -gt "$max_run" ]; then max_run="$n"; fi
    done
  fi
  RUN=$((max_run + 1))
fi
case "$RUN" in
  ''|*[!0-9]*) die "--run must be a positive integer (got '$RUN')" ;;
esac
printf -v RUN_PAD "%02d" "$RUN"

TRACE_DIR="$SKILL_DIR/${DATE}_run${RUN_PAD}"
TRACE_FILE="$TRACE_DIR/${KEY}.md"

# -------------------------------------------------------------- content ----

read_text() {
  # read_text <inline-value> <file-value>
  # Precedence: file over inline. "-" means stdin.
  local inline="$1" file="$2"
  if [ -n "$file" ]; then
    if [ "$file" = "-" ]; then
      cat
    elif [ -f "$file" ]; then
      cat "$file"
    else
      die "file not found: $file"
    fi
  elif [ -n "$inline" ]; then
    printf '%s\n' "$inline"
  else
    return 1
  fi
}

RESPONSE_BODY=""
if [ -n "$RESPONSE_FILE" ] || [ -n "$RESPONSE" ]; then
  RESPONSE_BODY="$(read_text "$RESPONSE" "$RESPONSE_FILE")" || die "no response supplied"
elif [ ! -t 0 ]; then
  RESPONSE_BODY="$(cat)"
fi

PROMPT_BODY=""
if [ -n "$PROMPT_FILE" ] || [ -n "$PROMPT" ]; then
  PROMPT_BODY="$(read_text "$PROMPT" "$PROMPT_FILE")" || die "no prompt supplied"
fi

if [ "$MODE" = "off" ]; then
  printf '%s: trace mode off; nothing written (skill=%s key=%s)\n' \
    "$SCRIPT_NAME" "$SKILL" "$KEY" >&2
  exit 0
fi

# ---------------------------------------------------------------- write ----

mkdir -p "$TRACE_DIR" || die "cannot create $TRACE_DIR"

GENERATED_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

{
  printf -- '---\n'
  printf 'skill: %s\n' "$SKILL"
  printf 'key: %s\n' "$KEY"
  printf 'date: %s\n' "$DATE"
  printf 'run: %s\n' "$RUN_PAD"
  printf 'mode: %s\n' "$MODE"
  printf 'thread_id: %s\n' "$THREAD_ID"
  printf 'reviewer_model: %s\n' "$REVIEWER_MODEL"
  printf 'reviewer_reasoning: %s\n' "$REVIEWER_REASONING"
  printf 'generated_at: %s\n' "$GENERATED_AT"
  printf -- '---\n'
  printf '\n'
  printf '# Review trace: %s / %s\n\n' "$SKILL" "$KEY"
  printf '| field | value |\n|---|---|\n'
  printf '| skill | %s |\n' "$SKILL"
  printf '| key | %s |\n' "$KEY"
  printf '| run | %s |\n' "$RUN_PAD"
  printf '| date | %s |\n' "$DATE"
  printf '| mode | %s |\n' "$MODE"
  printf '| thread_id | %s |\n' "$THREAD_ID"
  printf '| reviewer_model | %s |\n' "$REVIEWER_MODEL"
  printf '| reviewer_reasoning | %s |\n' "$REVIEWER_REASONING"
  printf '| generated_at | %s |\n' "$GENERATED_AT"
  printf '\n'

  if [ "$MODE" = "full" ]; then
    printf '## Prompt\n\n'
    if [ -n "$PROMPT_BODY" ]; then
      printf '```\n%s\n```\n\n' "$PROMPT_BODY"
    else
      printf '_(not recorded)_\n\n'
    fi
    printf '## Response\n\n'
    if [ -n "$RESPONSE_BODY" ]; then
      printf '%s\n' "$RESPONSE_BODY"
    else
      printf '_(empty)_\n'
    fi
  else
    printf '## Response (excerpt, first %s lines)\n\n' "$MAX_LINES"
    if [ -n "$RESPONSE_BODY" ]; then
      printf '%s\n' "$RESPONSE_BODY" | head -n "$MAX_LINES"
      total="$(printf '%s\n' "$RESPONSE_BODY" | wc -l | tr -d ' ')"
      if [ "$total" -gt "$MAX_LINES" ]; then
        printf '\n_[truncated: %s of %s lines omitted; re-run with --mode full]_\n' \
          "$((total - MAX_LINES))" "$total"
      fi
    else
      printf '_(empty)_\n'
    fi
  fi
} > "$TRACE_FILE" || die "cannot write $TRACE_FILE"

if [ "$QUIET" -eq 0 ]; then
  printf '%s\n' "$TRACE_FILE"
fi

exit 0
