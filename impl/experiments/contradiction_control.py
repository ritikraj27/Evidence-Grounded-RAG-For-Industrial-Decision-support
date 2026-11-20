#!/usr/bin/env python3
"""The contradiction detector's own positive control (Experiment 11b).

**Why this exists.** Experiment 11 measured the contradiction gate's
precision against reader labels and found it to be zero: none of its alarms
were confirmed as contradictions. That is a statement about the *corpus* as
much as about the detector -- the same readers found no contradiction in a
random sample of the pairs the gate did not flag either, because the corpus
holds encyclopaedic prose about concepts rather than instance records that
can contradict one another.

A measurement of zero on a corpus with no positives cannot distinguish "the
detector is broken" from "there is nothing to detect". This control does
that: it is a small set of pairs whose correct behaviour is known in
advance, written in the industrial register the corpus is about but not
drawn from it, so a detector that fires on nothing is distinguishable from
a detector that fires on the right things.

**What it measures.** Four classes, each with a known expected outcome:

* ``contradiction`` -- the same subject, incompatible facts. The semantic
  branch must fire.
* ``revision`` -- the same term at two issues of the same standard. The
  revision branch must fire, and the semantic branch need not.
* ``compatible`` -- the same subject, compatible facts. Neither branch may
  fire.
* ``different_subject`` -- different subjects that share vocabulary. Neither
  branch may fire.

The pairs are run through the *shipped* detector, with the real encoder and
the real NLI model, so what is measured is the code that runs in the
pipeline and not a re-implementation of it.

Usage:

    MTP_VARIANT=focus python experiments/contradiction_control.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import ContradictionConfig  # noqa: E402
from src.contradiction import detect_contradictions  # noqa: E402
from src.models import embed_texts  # noqa: E402

#: (expected class, passage A, passage B). The industrial register is
#: deliberate: the corpus is public articles about industrial concepts, and
#: the point is to show the detector works on the *kind* of text the corpus
#: is about without borrowing the corpus's own pairs.
PAIRS: list[tuple[str, str, str]] = [
    # -- contradiction: same subject, incompatible facts ---------------------
    ("contradiction",
     "The economic order quantity for the axial pump assembly is calculated "
     "as 500 units per order, based on a 30-day reorder cycle and the "
     "plant's weekly consumption rate.",
     "The economic order quantity for the axial pump assembly is calculated "
     "as 250 units per order, based on a 60-day reorder cycle and the "
     "plant's weekly consumption rate."),
    ("contradiction",
     "The safety stock level for the Kharagpur warehouse is set at 120 units, "
     "which covers three weeks of average demand.",
     "The safety stock level for the Kharagpur warehouse is set at 45 units, "
     "which covers about one week of average demand."),
    ("contradiction",
     "The conveyor belt is specified to run at a maximum speed of 1.8 metres "
     "per second under normal load.",
     "The conveyor belt is specified to run at a maximum speed of 2.6 metres "
     "per second under normal load."),
    ("contradiction",
     "The plant's overall equipment effectiveness target for the assembly "
     "line is 85 percent, measured monthly.",
     "The plant's overall equipment effectiveness target for the assembly "
     "line is 62 percent, measured monthly."),
    ("contradiction",
     "Inspection of the control plan requires a sample size of 5 units from "
     "every lot before release.",
     "Inspection of the control plan requires a sample size of 2 units from "
     "every lot before release."),
    # -- revision: the same term at two issues of the same standard ---------
    ("revision",
     "Under the CIF Incoterms 2020 rule, the seller must obtain insurance "
     "cover compliant with the Institute Cargo Clauses (A).",
     "Under the CIF Incoterms 2010 rule, the seller must insure the goods for "
     "110 percent of the contract value under Institute Cargo Clauses (A)."),
    ("revision",
     "Revision 4 of the incoming-goods SOP raises the acceptance sample to 5 "
     "units per lot.",
     "Revision 2 of the incoming-goods SOP sets the acceptance sample at 2 "
     "units per lot."),
    # -- compatible: the same subject, compatible facts ----------------------
    ("compatible",
     "The Kharagpur plant operates three shifts per day, with maintenance "
     "scheduled on Sundays.",
     "Maintenance at the Kharagpur plant is carried out on Sundays, when the "
     "line is idle."),
    ("compatible",
     "Safety stock at the Chennai warehouse covers about two weeks of average "
     "demand.",
     "The Chennai warehouse holds enough safety stock to cover roughly a "
     "fortnight of average demand."),
    # -- different subjects that share vocabulary ----------------------------
    ("different_subject",
     "The reorder point at Plant A is 300 units for the same component.",
     "The reorder point at Plant B is 900 units for the same component."),
    ("different_subject",
     "The forklift aisle width in the Kharagpur distribution centre is 3.5 "
     "metres.",
     "Forklift operators at the Kharagpur distribution centre must wear "
     "high-visibility vests at all times."),
]

#: Which branch is expected to fire for each class. A genuine numeric
#: contradiction may be caught by either the semantic branch or the more
#: specific quantity branch -- catching it with the quantity branch is
#: *better* evidence, not a failure, so the expectation is a set.
EXPECTED_BRANCH = {
    "contradiction": {"semantic", "quantity"},
    "revision": {"revision"},
    "compatible": set(),
    "different_subject": set(),
}


def main() -> int:
    from common import RESULTS_DIR, write_result

    cfg = ContradictionConfig()
    rows = []
    for expected, a, b in PAIRS:
        emb = embed_texts([a, b], dim=1024)
        findings = detect_contradictions([a, b], ["a", "b"], embeddings=emb,
                                         config=cfg)
        f = findings[0] if findings else None
        fired = f.kind if (f and f.flagged) else None
        want = EXPECTED_BRANCH[expected]
        ok = (fired in want) if want else (fired is None)
        rows.append({
            "expected_class": expected,
            "expected_branch": sorted(want),
            "fired_branch": fired,
            "ok": ok,
            "nli_contradiction_prob": (f.nli_contradiction_prob if f else None),
            "topical_similarity": (f.topical_similarity if f else None),
            "entity_overlap": (f.entity_overlap if f else None),
            "reason": (f.reason if f else ""),
        })
        print(f"  {'ok  ' if ok else 'MISS'} {expected:<20} "
              f"expected {str(sorted(want)):<22} fired {str(fired)}")

    n = len(rows)
    n_ok = sum(1 for r in rows if r["ok"])
    by_class: dict[str, dict] = {}
    for r in rows:
        b = by_class.setdefault(r["expected_class"], {"n": 0, "correct": 0})
        b["n"] += 1
        b["correct"] += int(r["ok"])

    # The precision that matters: of the pairs the detector flagged, how many
    # were a conflict at all? And of the pairs it correctly left alone, how
    # many did it leave alone?
    flagged = [r for r in rows if r["fired_branch"]]
    n_flagged = len(flagged)
    n_flagged_right = sum(1 for r in flagged
                           if r["fired_branch"] in r["expected_branch"])
    quiet = [r for r in rows if not r["fired_branch"]]
    n_quiet = len(quiet)
    n_quiet_right = sum(1 for r in quiet if not r["expected_branch"])
    by_branch: dict[str, int] = {}
    for r in flagged:
        by_branch[r["fired_branch"]] = by_branch.get(r["fired_branch"], 0) + 1

    summary = {
        "n_pairs": n,
        "n_correct": n_ok,
        "accuracy": n_ok / n if n else None,
        "by_class": by_class,
        "n_flagged": n_flagged,
        "flagged_precision": (n_flagged_right / n_flagged) if n_flagged else None,
        "flagged_by_branch": by_branch,
        "n_correctly_quiet": n_quiet,
        "quiet_specificity": (n_quiet_right / n_quiet) if n_quiet else None,
        "note": (
            "The control measures whether the detector can do its job, not "
            "whether the corpus exercises it. The corpus cannot: the reader "
            "labelling in Experiment 11 found no contradiction among the "
            "alarms or among a random sample of the unflagged pairs. The "
            "corroboration share between this control and that measurement "
            "is the claim that the mechanism works and the corpus does not "
            "test it -- as opposed to the claim that the mechanism does not "
            "work."),
        "pairs": rows,
    }
    write_result("exp11b_contradiction_control", summary)
    print(f"\n[control] {n_ok}/{n} pairs behave as expected "
          f"({summary['accuracy']:.3f})")
    print(f"[control] of {n_flagged} flagged pairs, {n_flagged_right} were "
          f"the right kind of conflict")
    print(f"[control] of {n_quiet} unflagged pairs, {n_quiet_right} were "
          f"correctly left alone")
    print(f"[control] wrote {RESULTS_DIR / 'exp11b_contradiction_control.json'}")
    return 0 if n_ok == n else 1


if __name__ == "__main__":
    sys.exit(main())
