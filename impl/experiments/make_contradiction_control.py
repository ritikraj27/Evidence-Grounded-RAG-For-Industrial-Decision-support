#!/usr/bin/env python3
"""Build the positive control for the contradiction labelling (Experiment 11).

**Why a control set exists.** A judge that labelled every pair
``no_conflict`` would score a precision of zero, and a judge that labelled
every pair ``contradiction`` would score a precision of one. Neither is a
measurement of the detector; both are measurements of the judge. The only
way to tell them apart is to hand the judge pairs whose correct labels are
known in advance, and see what it says about those.

**What the control is.** Fourteen short synthetic passages, one per label
class, written so that the rubric's answer is not in doubt: two plants
rather than one for ``term_mismatch``, a whole and one of its parts for
``granularity``, an explicit revision marker for ``supersession``. They are
not drawn from the corpus, so they cannot flatter the detector.

**How it is used.** Both annotators label the control blind, exactly as they
label the real sheet. A judge that misses the contradictions here is not a
judge whose silence on the corpus can be read as evidence about the
detector.

Usage:

    MTP_VARIANT=focus python experiments/make_contradiction_control.py \
        --out results_focus/exp11_judge_control.json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUBRIC = ROOT / "experiments" / "data" / "contradiction_label_rubric.md"

INSTRUCTIONS = (
    "For each pair, read both passages and set `label` to exactly one "
    "of: contradiction, granularity, supersession, term_mismatch, "
    "no_conflict. Use the rubric below. `contradiction` means the two "
    "passages state incompatible facts about the same subject -- "
    "nothing else counts as a true contradiction, and everything else "
    "is a false alarm."
)

#: (expected label, passage A, passage B). The order is the rubric's order.
PAIRS: list[tuple[str, str, str]] = [
    # -- contradiction: same subject, incompatible values -------------------
    ("contradiction",
     "The economic order quantity for the axial pump assembly is calculated "
     "as 500 units per order, based on a 30-day reorder cycle and the "
     "plant's weekly consumption rate.",
     "The economic order quantity for the axial pump assembly is calculated "
     "as 250 units per order, based on a 60-day reorder cycle and the "
     "plant's weekly consumption rate."),
    ("contradiction",
     "The safety stock level for the warehouse is set at 120 units, which "
     "covers three weeks of average demand.",
     "The safety stock level for the warehouse is set at 45 units, which "
     "covers about one week of average demand."),
    ("contradiction",
     "Inspection of the control plan requires a sample size of 5 units from "
     "every lot before release.",
     "Inspection of the control plan requires a sample size of 2 units from "
     "every lot before release."),
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
     "All incoming raw material certificates of conformity must be retained "
     "for five years.",
     "All incoming raw material certificates of conformity must be retained "
     "for two years."),
    # -- granularity: whole and one of its parts, both true at once --------
    ("granularity",
     "The total cycle time for the machining operation is three days.",
     "The annealing sub-step of the machining operation takes three days."),
    ("granularity",
     "The plant's annual throughput is 40,000 units.",
     "The paint shop within the plant has an annual throughput of 40,000 "
     "units."),
    # -- supersession: one is a later revision of the other -----------------
    ("supersession",
     "Raw material lead time is 21 days.",
     "Raw material lead time is 14 days, revised as of the third quarter."),
    ("supersession",
     "The inspection frequency for the gearbox is every 500 operating hours.",
     "The inspection frequency for the gearbox is every 200 operating hours "
     "(updated revision, Rev 4)."),
    # -- term_mismatch: different subjects that share words -----------------
    ("term_mismatch",
     "Plant A uses a reorder point of 300 units for the same component.",
     "Plant B uses a reorder point of 900 units for the same component."),
    ("term_mismatch",
     "The forklift aisle width in the distribution centre is 3.5 metres.",
     "Forklift operators must wear high-visibility vests at all times in the "
     "distribution centre."),
    # -- no_conflict: same subject, compatible statements -------------------
    ("no_conflict",
     "The maximum pallet weight in the distribution centre is 1200 kg.",
     "The maximum pallet weight in the distribution centre is 1200 kilograms, "
     "including the pallet itself."),
    ("no_conflict",
     "The distribution centre operates two shifts per day.",
     "The second shift at the distribution centre starts at 14:00."),
]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", required=True, help="where to write the control")
    ap.add_argument("--blind", action="store_true",
                    help="omit the expected labels, for a judge that reads "
                         "the file directly rather than calling the API")
    args = ap.parse_args()

    rubric = RUBRIC.read_text(encoding="utf-8") if RUBRIC.exists() else ""
    payload = {
        "schema": "mtp.contradiction-judge-control/1",
        "instructions": INSTRUCTIONS,
        "rubric": rubric,
        "labels_allowed": ["contradiction", "granularity", "supersession",
                           "term_mismatch", "no_conflict"],
        "pairs": [
            {
                "pair_id": i,
                "stratum": "control",
                "passage_a": a,
                "passage_b": b,
                **({} if args.blind else {"expected": label}),
            }
            for i, (label, a, b) in enumerate(PAIRS)
        ],
    }
    out = Path(args.out)
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    counts: dict[str, int] = {}
    for label, _a, _b in PAIRS:
        counts[label] = counts.get(label, 0) + 1
    print(f"[control] wrote {out}: {len(PAIRS)} pairs {counts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
