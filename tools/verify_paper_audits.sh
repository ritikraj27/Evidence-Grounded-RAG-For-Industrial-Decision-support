#!/usr/bin/env bash
#
# verify_paper_audits.sh - external gate over the paper submission audit
# artifacts. Exit code is the source of truth for "paper-writing" Phase 6.
#
# Contract (from the skills that call it):
#
#   paper-writing/SKILL.md:522 and :556
#
#     bash <ARIS_REPO>/tools/verify_paper_audits.sh paper/ --assurance submission
#
#   paper-writing/SKILL.md:559-568
#
#     Exit 0 - all mandatory audits present, JSON schema-valid, hashes fresh,
#              no blocking verdicts.
#     Exit 1 - surface paper/.aris/audit-verifier-report.json and refuse the
#              Final Report. Row statuses:
#                MISSING           -> rerun that audit
#                STALE             -> paper files edited after the audit ran
#                BLOCKING_VERDICT  -> FAIL / BLOCKED / ERROR
#                SCHEMA_INVALID    -> audit artifact malformed
#
#   paper-writing/SKILL.md:619
#
#     "| 6.0 Assurance Verifier | [OK|STALE|BLOCKING_VERDICT|HAS_ISSUES|
#      SCHEMA_INVALID|MISSING] per audit; exit [0|1] overall (N/A if draft) |
#      .aris/audit-verifier-report.json |"
#
# The three mandatory artifacts, all written at the paper directory root:
#   proof-checker      -> PROOF_AUDIT.json       (proof-checker/SKILL.md:565)
#   paper-claim-audit  -> PAPER_CLAIM_AUDIT.json (paper-claim-audit/SKILL.md:251)
#   citation-audit     -> CITATION_AUDIT.json    (citation-audit/SKILL.md:395)
#
# "audited_input_hashes" keys are resolved relative to the paper directory
# (no "paper/" prefix) and absolute for files outside it - see
# citation-audit/SKILL.md:457-461 and paper-claim-audit/SKILL.md:293-299.
#
set -euo pipefail

SCRIPT_NAME="verify_paper_audits.sh"
SCRIPT_VERSION="1.0"
PYTHON_BIN="${PYTHON:-python3}"
SEP=$'\x1f'   # unit separator: safe inside flattened text

# ---------------------------------------------------------------- usage ----

usage() {
  cat <<'USAGE'
verify_paper_audits.sh - gate a paper directory on its submission audits.

Usage:
  bash tools/verify_paper_audits.sh <paper-dir> [--assurance draft|submission]

Options:
  -h, --help                Show this help and exit 0.
  -a, --assurance <level>   draft | submission.
                            Default: the value of <paper-dir>/.aris/assurance.txt
                            when that file exists, else "draft".
      --report <path>       Where to write the JSON report.
                            Default: <paper-dir>/.aris/audit-verifier-report.json
      --json                Also print the report JSON on stdout.
  -q, --quiet               Suppress the human-readable summary on stdout.

Audit rows and statuses:
  OK                 artifact present, schema-valid, hashes fresh, PASS /
                     NOT_APPLICABLE verdict.
  HAS_ISSUES         verdict WARN. Reported, never blocking.
  MISSING            artifact file not found. Blocking at assurance=submission.
  SCHEMA_INVALID     artifact malformed or missing a required field.
                     Blocking at assurance=submission.
  STALE              an audited input file changed (or vanished) since the
                     audit ran. Blocking at assurance=submission.
  BLOCKING_VERDICT   verdict FAIL / BLOCKED / ERROR. Always blocking.

Exit codes:
  0  no blocking row
  1  at least one blocking row (or the paper directory is unusable)
USAGE
}

die() {
  printf '%s: error: %s\n' "$SCRIPT_NAME" "$*" >&2
  exit 1
}

say() {
  [ "$QUIET" -eq 1 ] || printf '%s\n' "$*"
}

# ------------------------------------------------------------ arg parse ----

PAPER_DIR=""
ASSURANCE=""
REPORT_PATH=""
PRINT_JSON=0
QUIET=0

while [ $# -gt 0 ]; do
  case "$1" in
    -h|--help) usage; exit 0 ;;
    -a|--assurance) [ $# -ge 2 ] || die "--assurance requires a value"; ASSURANCE="$2"; shift 2 ;;
    --assurance=*) ASSURANCE="${1#*=}"; shift ;;
    --report) [ $# -ge 2 ] || die "--report requires a path"; REPORT_PATH="$2"; shift 2 ;;
    --report=*) REPORT_PATH="${1#*=}"; shift ;;
    --json) PRINT_JSON=1; shift ;;
    -q|--quiet) QUIET=1; shift ;;
    --) shift; if [ $# -gt 0 ]; then PAPER_DIR="$1"; fi; break ;;
    -*) printf '%s: error: unknown option: %s\n' "$SCRIPT_NAME" "$1" >&2; usage >&2; exit 1 ;;
    *)  if [ -z "$PAPER_DIR" ]; then PAPER_DIR="$1"
        else printf '%s: error: unexpected argument: %s\n' "$SCRIPT_NAME" "$1" >&2; usage >&2; exit 1
        fi
        shift ;;
  esac
done

[ -n "$PAPER_DIR" ] || { printf '%s: error: a paper directory is required\n' "$SCRIPT_NAME" >&2; usage >&2; exit 1; }
[ -d "$PAPER_DIR" ] || die "paper directory '$PAPER_DIR' does not exist"
PAPER_DIR="$(cd "$PAPER_DIR" && pwd)"

if [ -z "$ASSURANCE" ] && [ -f "$PAPER_DIR/.aris/assurance.txt" ]; then
  ASSURANCE="$(tr -d '[:space:]' < "$PAPER_DIR/.aris/assurance.txt" 2>/dev/null || true)"
fi
[ -n "$ASSURANCE" ] || ASSURANCE="draft"
case "$ASSURANCE" in
  draft|submission) ;;
  *) die "unknown assurance level '$ASSURANCE' (expected: draft, submission)" ;;
esac

[ -z "$REPORT_PATH" ] && REPORT_PATH="$PAPER_DIR/.aris/audit-verifier-report.json"

command -v "$PYTHON_BIN" >/dev/null 2>&1 || die "'$PYTHON_BIN' not found; it is required to parse the audit JSON"

TMPDIR_LOCAL="$(mktemp -d "${TMPDIR:-/tmp}/verify_paper_audits.XXXXXX")"
cleanup() { rm -rf "$TMPDIR_LOCAL"; }
trap cleanup EXIT

ROWS_FILE="$TMPDIR_LOCAL/rows.tsv"
PY_EXTRACT="$TMPDIR_LOCAL/extract.py"
PY_REPORT="$TMPDIR_LOCAL/report.py"
: > "$ROWS_FILE"

# ------------------------------------------------------------- helpers ----

compute_sha256() {
  local f="$1" out=""
  [ -f "$f" ] || return 1
  if command -v shasum >/dev/null 2>&1; then
    out="$(shasum -a 256 "$f" 2>/dev/null | awk '{print $1}')"
  elif command -v sha256sum >/dev/null 2>&1; then
    out="$(sha256sum "$f" 2>/dev/null | awk '{print $1}')"
  else
    return 2
  fi
  [ -n "$out" ] || return 1
  printf '%s' "$out"
}

normalize_hash() {
  printf '%s' "$1" | sed -e 's/^[Ss][Hh][Aa]256://' -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' \
    | tr 'A-F' 'a-f'
}

resolve_audited_path() {
  # Relative keys resolve against the paper directory; absolute keys are used
  # as-is (citation-audit/SKILL.md:457-461).
  case "$1" in
    /*) printf '%s' "$1" ;;
    *)  printf '%s/%s' "$PAPER_DIR" "$1" ;;
  esac
}

cat > "$PY_EXTRACT" <<'PYEOF'
import json
import sys

ALLOWED = {"PASS", "WARN", "FAIL", "NOT_APPLICABLE", "BLOCKED", "ERROR"}
REQUIRED = (
    "audit_skill",
    "verdict",
    "reason_code",
    "summary",
    "audited_input_hashes",
    "generated_at",
)
SEP = "\x1f"


def flat(value):
    if not isinstance(value, str):
        try:
            value = json.dumps(value, sort_keys=True)
        except (TypeError, ValueError):
            value = repr(value)
    return " ".join(value.replace("\t", " ").replace("\r", " ").split())


def emit(*fields):
    print(SEP.join(flat(f) for f in fields))


path = sys.argv[1]
try:
    with open(path, "r", encoding="utf-8") as handle:
        doc = json.load(handle)
except Exception as exc:  # any parse problem counts as schema-invalid
    emit("STATUS", "SCHEMA_INVALID", "unreadable or malformed JSON: %s" % exc)
    sys.exit(0)

if not isinstance(doc, dict):
    emit("STATUS", "SCHEMA_INVALID", "top-level JSON value is not an object")
    sys.exit(0)

missing = [key for key in REQUIRED if key not in doc]
if missing:
    emit("STATUS", "SCHEMA_INVALID", "missing required field(s): %s" % ", ".join(missing))
    sys.exit(0)

verdict = doc.get("verdict")
if not isinstance(verdict, str) or verdict not in ALLOWED:
    emit("STATUS", "SCHEMA_INVALID", "unknown verdict: %s" % verdict)
    sys.exit(0)

hashes = doc.get("audited_input_hashes")
if not isinstance(hashes, dict):
    emit("STATUS", "SCHEMA_INVALID", "audited_input_hashes is not an object")
    sys.exit(0)

emit("STATUS", "OK", "")
emit("AUDIT_SKILL", doc.get("audit_skill"))
emit("VERDICT", verdict)
emit("REASON", doc.get("reason_code"))
emit("SUMMARY", doc.get("summary"))
for key in sorted(hashes):
    emit("HASH", key, hashes[key])
PYEOF

cat > "$PY_REPORT" <<'PYEOF'
import datetime
import json
import sys

rows_path, paper_dir, assurance, overall, exit_code, version = sys.argv[1:7]

rows = []
with open(rows_path, "r", encoding="utf-8") as handle:
    for line in handle:
        line = line.rstrip("\n")
        if not line.strip():
            continue
        parts = line.split("\x1f")
        parts += [""] * (6 - len(parts))
        audit, artifact, status, verdict, reason, detail = parts[:6]
        rows.append(
            {
                "audit": audit,
                "artifact": artifact,
                "status": status,
                "verdict": verdict,
                "reason_code": reason,
                "detail": detail,
            }
        )

non_ok = sum(1 for row in rows if row["status"] != "OK")
report = {
    "verifier": "verify_paper_audits.sh",
    "verifier_version": version,
    "paper_dir": paper_dir,
    "assurance": assurance,
    "generated_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "overall_status": overall,
    "exit_code": int(exit_code),
    "audits": rows,
    "summary": "%s - %d audit(s) checked, %d non-OK row(s)" % (overall, len(rows), non_ok),
}
print(json.dumps(report, indent=2))
PYEOF

# ------------------------------------------------------------ main loop ----

BLOCKING=0
NON_OK=0

add_row() {
  printf '%s%s%s%s%s%s%s%s%s%s%s\n' "$1" "$SEP" "$2" "$SEP" "$3" "$SEP" "$4" "$SEP" "$5" "$SEP" "$6" >> "$ROWS_FILE"
}

is_blocking() {
  case "$1" in
    BLOCKING_VERDICT) return 0 ;;
    MISSING|SCHEMA_INVALID|STALE)
      [ "$ASSURANCE" = "submission" ] && return 0
      return 1
      ;;
    *) return 1 ;;
  esac
}

check_one_audit() {
  local audit="$1" artifact="$2" expected_skill="$3"
  local path="$PAPER_DIR/$artifact"

  if [ ! -f "$path" ]; then
    add_row "$audit" "$artifact" "MISSING" "" "" "artifact not found at $path"
    NON_OK=$((NON_OK + 1))
    if is_blocking "MISSING"; then BLOCKING=$((BLOCKING + 1)); fi
    return 0
  fi

  local extracted
  extracted="$("$PYTHON_BIN" "$PY_EXTRACT" "$path")"

  local status="" detail="" audit_skill="" verdict="" reason="" summary=""
  local hash_key="" hash_value=""

  while IFS="$SEP" read -r field v1 v2; do
    case "$field" in
      STATUS)      status="$v1"; detail="$v2" ;;
      AUDIT_SKILL) audit_skill="$v1" ;;
      VERDICT)     verdict="$v1" ;;
      REASON)      reason="$v1" ;;
      SUMMARY)     summary="$v1" ;;
      HASH)        hash_key="$v1"; hash_value="$v2" ;;
    esac
  done <<EOF
$extracted
EOF

  if [ "$status" != "OK" ]; then
    add_row "$audit" "$artifact" "SCHEMA_INVALID" "" "" "$detail"
    NON_OK=$((NON_OK + 1))
    if is_blocking "SCHEMA_INVALID"; then BLOCKING=$((BLOCKING + 1)); fi
    return 0
  fi

  if [ "$audit_skill" != "$expected_skill" ]; then
    add_row "$audit" "$artifact" "SCHEMA_INVALID" "$verdict" "$reason" \
      "audit_skill is '$audit_skill', expected '$expected_skill'"
    NON_OK=$((NON_OK + 1))
    if is_blocking "SCHEMA_INVALID"; then BLOCKING=$((BLOCKING + 1)); fi
    return 0
  fi

  # Freshness: rehash every declared audited input.
  local stale_detail=""
  while IFS="$SEP" read -r field v1 v2; do
    [ "$field" = "HASH" ] || continue
    hash_key="$v1"; hash_value="$v2"
    local target actual stored
    target="$(resolve_audited_path "$hash_key")"
    stored="$(normalize_hash "$hash_value")"
    if ! actual="$(compute_sha256 "$target")"; then
      stale_detail="audited input '$hash_key' is missing or unreadable ($target)"
      break
    fi
    actual="$(normalize_hash "$actual")"
    if [ "$actual" != "$stored" ]; then
      stale_detail="audited input '$hash_key' changed since the audit ran (expected $stored, found $actual)"
      break
    fi
  done <<EOF
$extracted
EOF

  if [ -n "$stale_detail" ]; then
    add_row "$audit" "$artifact" "STALE" "$verdict" "$reason" "$stale_detail"
    NON_OK=$((NON_OK + 1))
    if is_blocking "STALE"; then BLOCKING=$((BLOCKING + 1)); fi
    return 0
  fi

  case "$verdict" in
    FAIL|BLOCKED|ERROR)
      add_row "$audit" "$artifact" "BLOCKING_VERDICT" "$verdict" "$reason" "$summary"
      NON_OK=$((NON_OK + 1))
      BLOCKING=$((BLOCKING + 1))
      ;;
    WARN)
      add_row "$audit" "$artifact" "HAS_ISSUES" "$verdict" "$reason" "$summary"
      NON_OK=$((NON_OK + 1))
      ;;
    *)
      add_row "$audit" "$artifact" "OK" "$verdict" "$reason" "$summary"
      ;;
  esac
}

check_one_audit "proof-checker"     "PROOF_AUDIT.json"       "proof-checker"
check_one_audit "paper-claim-audit" "PAPER_CLAIM_AUDIT.json" "paper-claim-audit"
check_one_audit "citation-audit"    "CITATION_AUDIT.json"    "citation-audit"

# --------------------------------------------------------------- report ----

EXIT_CODE=0
[ "$BLOCKING" -gt 0 ] && EXIT_CODE=1

if [ "$NON_OK" -eq 0 ]; then
  OVERALL="OK"
elif [ "$BLOCKING" -gt 0 ]; then
  OVERALL="BLOCKED"
else
  OVERALL="HAS_ISSUES"
fi

REPORT_JSON="$("$PYTHON_BIN" "$PY_REPORT" "$ROWS_FILE" "$PAPER_DIR" "$ASSURANCE" "$OVERALL" "$EXIT_CODE" "$SCRIPT_VERSION")"
[ -n "$REPORT_JSON" ] || die "failed to build the verifier report"

mkdir -p "$(dirname "$REPORT_PATH")"
printf '%s\n' "$REPORT_JSON" > "$REPORT_PATH" || die "cannot write $REPORT_PATH"

if [ "$PRINT_JSON" -eq 1 ]; then
  printf '%s\n' "$REPORT_JSON"
fi

# -------------------------------------------------------------- summary ----

if [ "$QUIET" -eq 0 ] && [ "$PRINT_JSON" -eq 0 ]; then
  say "Audit verification ($ASSURANCE) - $PAPER_DIR"
  while IFS="$SEP" read -r audit artifact status verdict reason detail; do
    [ -n "$audit" ] || continue
    printf '  %-16s %-24s %s' "$status" "$artifact" "$audit"
    [ -n "$verdict" ] && printf ' (verdict=%s)' "$verdict"
    [ -n "$reason" ] && printf ' (reason=%s)' "$reason"
    [ -n "$detail" ] && printf ' - %s' "$detail"
    printf '\n'
  done < "$ROWS_FILE"
  say ""
  say "Overall: $OVERALL   exit=$EXIT_CODE   report: $REPORT_PATH"
fi

exit "$EXIT_CODE"
