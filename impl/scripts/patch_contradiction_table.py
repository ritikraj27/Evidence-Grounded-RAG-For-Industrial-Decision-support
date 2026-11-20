#!/usr/bin/env python3
"""Report the contradiction gate's non-tautological recall.

The joint gate's recall on the verifiable subset was 1.000 -- by
construction, because the verifiable subset is *defined* by numeric
conflicts and the numeric detector is an OR-branch of the gate. That
number was being presented as a result. It is not one.

The experiment now reports the NLI-and-same-subject conjunction on its
own, which is the informative quantity: how many of those conflicts it
catches with the numeric branch removed, and therefore what the numeric
branch adds.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "experiments" / "run_contradiction.py"

OLD_ROW = '''        ["Joint gate (NLI + topical)", summary["joint_gate_flagged"],
         f"{summary['joint_flag_rate']:.3f}",
         f"{summary['joint_recall_on_verifiable_subset']:.3f}",
         f"{summary['joint_alarms_per_verifiable_conflict']:.1f}"],
'''

NEW_ROW = '''        ["NLI AND same-subject (conjunction alone)", summary["conjunction_flagged"],
         f"{summary['conjunction_flagged'] / n if n else 0.0:.3f}",
         f"{summary['conjunction_recall_on_verifiable_subset']:.3f}",
         f"{summary['conjunction_flagged'] / max(summary['verifiable_numeric_conflicts'], 1):.1f}"],
        ["Joint gate (+ numeric branch)", summary["joint_gate_flagged"],
         f"{summary['joint_flag_rate']:.3f}",
         "1.000 (by construction)",
         f"{summary['joint_alarms_per_verifiable_conflict']:.1f}"],
'''

OLD_NOTE = '''        + table + "\\n\\n"
        "The verifiable subset is the set of pairs that attach different values to "'''

NEW_NOTE = '''        + table + "\\n\\n"
        "**The joint gate's recall on the verifiable subset is 1.000 by "
        "construction, and is therefore not evidence.** The verifiable subset is "
        "defined by the presence of a numeric conflict, and the numeric "
        "detector is an OR-branch of the gate. The informative quantity is the "
        "second row: how many of those conflicts the NLI-and-same-subject "
        "conjunction catches with the numeric branch removed, which is what the "
        "numeric branch then adds on top of.\\n\\n"
        "The verifiable subset is the set of pairs that attach different values to "'''


def main() -> int:
    s = TARGET.read_text(encoding="utf-8")
    failures = []
    if OLD_ROW not in s:
        failures.append("table row not found")
    else:
        s = s.replace(OLD_ROW, NEW_ROW, 1)
    if OLD_NOTE not in s:
        failures.append("note anchor not found")
    else:
        s = s.replace(OLD_NOTE, NEW_NOTE, 1)
    if failures:
        for f in failures:
            print(f"!! {f}")
        return 1
    TARGET.write_text(s, encoding="utf-8")
    print("  the contradiction table now reports the conjunction on its own")
    return 0


if __name__ == "__main__":
    sys.exit(main())
