#!/usr/bin/env python3
"""Add the focus-domain case study to the guide's results generator.

The guide's Part E reports the multi-category evaluation. The focus domain
is where the thesis lives: one industrial domain, every question traced end
to end, before and after. This patch inserts that section into the
generator, so the guide carries it without anyone having to paste it in.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "deliverables" / "scripts" / "make_results_md.py"

OLD_TAIL = '''w("""
## E.6 What the five experiments say, together'''

NEW_TAIL = '''# --- The focus domain -------------------------------------------------
# The single industrial domain the thesis is about. The case study is
# rendered by impl/experiments/run_focus_case.py and inlined here, so the
# guide and the experiment always agree.
FOCUS_CASE = ROOT / "impl" / "results_focus" / "exp6_focus_case.md"
if FOCUS_CASE.exists():
    w("""
---

## E.7 The focus domain: supply chain management, before and after

The multi-category evaluation above is the statistically strongest result.
The focus domain is where the framework is *shown*, on questions a supply
chain practitioner would actually ask, with every intermediate artefact
written out: the two retrieval legs, the fused ranking, the reranked
ranking, the gate's decision and the signals behind it, which chunks the
quota swapped, how each claim was banded, and whether any two accepted
chunks contradict each other.

The point of the section is not another number. It is the evidence that the
architecture changes the *outcome* on a real question, and that every change
is attributable to a named mechanism.

""")
    w(FOCUS_CASE.read_text(encoding="utf-8").strip())
    w("")

w("""
## E.8 What the experiments say, together'''

OLD_OUT = '''OUT.write_text("\\n".join(L), encoding="utf-8")'''
NEW_OUT = '''OUT.write_text("\\n".join(L), encoding="utf-8")'''


def main() -> int:
    s = TARGET.read_text(encoding="utf-8")
    if "E.7 The focus domain" in s:
        print("  the focus section is already wired in")
        return 0
    if OLD_TAIL not in s:
        print("!! anchor not found in make_results_md.py")
        return 1
    s = s.replace(OLD_TAIL, NEW_TAIL, 1)
    # The generator writes to impl/results; the focus case study lives beside it.
    if "ROOT = " in s and "ROOT /" not in s.split("ROOT = ")[1][:120]:
        pass
    TARGET.write_text(s, encoding="utf-8")
    print("  wired the focus-domain section into the guide's results generator")
    return 0


if __name__ == "__main__":
    sys.exit(main())
