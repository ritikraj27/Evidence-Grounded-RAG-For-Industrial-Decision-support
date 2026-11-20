#!/bin/bash
# The final sequence: regenerate the answer-side audit, rebuild every
# deliverable, and report what the build's own checks say.
set -e
set -o pipefail
cd /Users/ritikraj/Documents/MTP

echo "=== 1. answer-side audit (focus domain) ==="
cd impl
MTP_VARIANT=focus /Users/ritikraj/Documents/MTP/.venv/bin/python \
  experiments/audit_answer_side.py 2>&1 | grep -Ev "^Loading weights|Warning:|FutureWarning|warnings.warn|^W[0-9]"
cd ..

echo ""
echo "=== 2. rebuild every deliverable ==="
/Users/ritikraj/Documents/MTP/.venv/bin/python deliverables/scripts/build_all.py 2>&1 \
  | grep -E "^===|✗|FAILED|PROBLEM|all checks|no overflow|wrote|ok$|PASS|FAIL"

echo ""
echo "=== 3. the LaTeX papers actually compile ==="
/Users/ritikraj/Documents/MTP/.venv/bin/python deliverables/scripts/check_latex.py 2>&1 | tail -12
