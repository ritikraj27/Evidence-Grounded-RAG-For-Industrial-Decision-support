#!/usr/bin/env python3
"""Fix three things the direction check found in the gate experiment.

1. **The baselines were not baselines.** `sweep[0]` is the loosest threshold
   *in the sweep* (tau = 0.05), not a never-refuse policy, and `sweep[-1]`
   is the strictest threshold in the sweep, not an always-refuse policy.
   The report called the first an "always-answer baseline"; it refuses
   ~5% of unanswerable queries, so it is a degenerate artefact rather
   than a baseline. True tau = 0 and tau = 1 policies are now computed
   and reported.

2. **The label is a retrieval-success label.** The positive class is
   "the gold chunk is in the reranked candidate pool". The negative
   class is therefore mostly *retrieval failure*, not absence of
   evidence. The payload now says so, reports the 2x2 decomposition
   the claim depends on, and renames the key accordingly.

3. **The function names said "sufficiency".** The literature reserves
   "sufficiency" for a set-level property (arXiv:2605.03534,
   arXiv:2610.09348), so the name reads as a claim of prior art. The
   internal helpers are renamed to "detectability".
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
IMPL = ROOT / "impl"

# --------------------------------------------------------------------------
# 1. Rename the internal helpers.
# --------------------------------------------------------------------------
RENAMES = [
    ("sufficiency_features", "detectability_features"),
    ("sufficiency_posterior", "detectability_posterior"),
]
renamed = 0
for rel in ["src/confidence.py", "src/pipeline.py",
            "experiments/common.py", "experiments/run_gate.py",
            "experiments/run_transfer.py"]:
    p = IMPL / rel
    if not p.exists():
        continue
    s = p.read_text(encoding="utf-8")
    orig = s
    for old, new in RENAMES:
        s = re.sub(rf"\b{old}\b", new, s)
    if s != orig:
        p.write_text(s, encoding="utf-8")
        renamed += 1
print(f"  renamed the detectability helpers in {renamed} files")

# --------------------------------------------------------------------------
# 2. The gate experiment: true baselines, label definition, decomposition.
# --------------------------------------------------------------------------
p = IMPL / "experiments" / "run_gate.py"
s = p.read_text(encoding="utf-8")

OLD_BASELINES = '''    always = sweep[0]
    strictest = sweep[-1]
    print(f"[exp2] always-answer baseline (lowest tau) refuses "
          f"{always['unanswerable_refused']:.3f} of unanswerable; the strictest "
          f"threshold (tau={strictest['tau']:.2f}) answers only "
          f"{strictest['answerable_answered']:.3f} of answerable", flush=True)
'''

NEW_BASELINES = '''    # The endpoints of the sweep are NOT baselines: the loosest threshold in
    # the sweep still refuses some unanswerable queries, and the strictest
    # still answers some answerable ones. The true baselines are the two
    # degenerate policies, tau = 0 (never refuse) and tau = 1 (always
    # refuse), and they have to be computed rather than read off the
    # sweep.
    ans_mask = np.array([c["has_gold"] for c in cases])
    n_ans, n_un = int(ans_mask.sum()), int((~ans_mask).sum())
    never_refuse = {
        "tau": 0.0,
        "answerable_answered": 1.0,
        "answerable_refused": 0.0,
        "unanswerable_refused": 0.0,
        "unanswerable_answered": 1.0,
        # Undefined, not zero: no abstentions are made, so there is no
        # precision to report.
        "abstention_precision": None,
        "coverage": 1.0,
    }
    always_refuse = {
        "tau": 1.0,
        "answerable_answered": 0.0,
        "answerable_refused": 1.0,
        "unanswerable_refused": 1.0,
        "unanswerable_answered": 0.0,
        "abstention_precision": (n_un / (n_un + n_ans)) if (n_un + n_ans) else None,
        "coverage": 0.0,
    }
    loosest = sweep[0]
    strictest = sweep[-1]
    print(f"[exp2] never-refuse baseline (tau=0) refuses 0.000 of unanswerable; "
          f"always-refuse (tau=1) answers 0.000 of answerable. The loosest "
          f"threshold in the sweep (tau={loosest['tau']:.2f}) still refuses "
          f"{loosest['unanswerable_refused']:.3f} of unanswerable, which is why "
          f"it is a sweep endpoint and not a baseline.", flush=True)
'''

if OLD_BASELINES not in s:
    print("!! the baselines block was not found")
    sys.exit(1)
s = s.replace(OLD_BASELINES, NEW_BASELINES, 1)

OLD_PAYLOAD = '''        "always_answer_baseline": always,
        "strictest_threshold_baseline": strictest,
    }'''
NEW_PAYLOAD = '''        "never_refuse_baseline": never_refuse,
        "always_refuse_baseline": always_refuse,
        "loosest_threshold_in_sweep": loosest,
        "strictest_threshold_in_sweep": strictest,
        "baseline_note": (
            "The sweep endpoints are not baselines: the loosest threshold in "
            "the sweep still refuses some unanswerable queries. The true "
            "baselines are the degenerate policies tau=0 (never refuse) and "
            "tau=1 (always refuse)."),
    }'''
if OLD_PAYLOAD not in s:
    print("!! the payload block was not found")
    sys.exit(1)
s = s.replace(OLD_PAYLOAD, NEW_PAYLOAD, 1)

OLD_KEYS = '''        "n_contexts_with_evidence": int(n_pos),
        "base_rate_sufficient_evidence": float(y_all.mean()),'''
NEW_KEYS = '''        "n_contexts_with_answer_in_context": int(n_pos),
        "base_rate_answer_in_context": float(y_all.mean()),
        "label_definition": (
            "The positive class is 1 iff the gold chunk is present in the "
            "reranked candidate pool. The negative class is therefore "
            "dominated by RETRIEVAL FAILURE -- an answerable query whose "
            "evidence the retriever missed -- not by absence of evidence. "
            "The gate detects answer-in-context detectability; it does not "
            "detect evidence sufficiency."),
        "label_decomposition": {
            "answerable_and_found": int(sum(
                1 for c in cases if c["has_gold"] and c["gold_found"])),
            "answerable_and_missed": int(sum(
                1 for c in cases if c["has_gold"] and not c["gold_found"])),
            "unanswerable": int(sum(1 for c in cases if not c["has_gold"])),
            "note": (
                "The negative class is (answerable_and_missed + unanswerable). "
                "Report the share of it that is retrieval failure: that "
                "fraction is the limit on what the gate can be said to "
                "detect."),
        },'''
if OLD_KEYS not in s:
    print("!! the key block was not found")
    sys.exit(1)
s = s.replace(OLD_KEYS, NEW_KEYS, 1)
s = s.replace(
    '"design": "query-level sufficiency calibration (not candidate-level)"',
    '"design": "query-level answer-in-context calibration (not candidate-level)"', 1)
p.write_text(s, encoding="utf-8")
print("  run_gate.py: true baselines, label definition and decomposition")

# --------------------------------------------------------------------------
# 3. The two consumers of the renamed key.
# --------------------------------------------------------------------------
for rel in ["deliverables/scripts/make_results_md.py",
            "deliverables/scripts/make_docx.py"]:
    p = ROOT / rel
    s = p.read_text(encoding="utf-8")
    if "base_rate_sufficient_evidence" in s:
        s = s.replace("base_rate_sufficient_evidence", "base_rate_answer_in_context")
        p.write_text(s, encoding="utf-8")
        print(f"  {rel}: updated the renamed key")

print("\ndone")
