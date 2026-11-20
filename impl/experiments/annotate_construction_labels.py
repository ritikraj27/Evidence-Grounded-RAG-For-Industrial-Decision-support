#!/usr/bin/env python3
"""Add the construction labels and the regime map to the candidate pairs.

**Why construction labels exist.** The quantity branch of the contradiction
gate fires when two passages attach different values to the same measured
quantity. On the annotated pair set that branch never fires, and the reason
is a property of the *pool* rather than of the detector: the pairs that
reach it are mostly the same provision at two issues with an editorial
change, and very few of them state a different quantity.

But there is a stratum where the quantity conflicts are known **by
construction** and need no annotation: two versions of the same provision
between which a limit changed. If the two texts state different
unit-bearing quantities, the rule changed the number it binds on, and that
is a quantity conflict whether or not a reader says so.

**The selection criterion is deliberately weaker than the detector's.**
"a unit-bearing number differs" asks nothing about whether the number is
governed by a declared measurement term, and nothing about the subject and
instance checks. The detector requires all three. So a detector that fails
on this stratum has failed on a real ambiguity, not on a tautology.

**A note on the alignment.** The pairs are aligned by token overlap against
the same section in two snapshots. The overlap distribution is reported by
this script so that the alignment's quality is a measured fact rather than
an assumption: a badly aligned pair would make the whole stratum
meaningless, and a reader should be able to check it.

Usage:
    python experiments/annotate_construction_labels.py \
        --pairs ../results_industrial/exp14_pairs.json \
        --out   ../results_industrial/exp14_pairs_annotated.json
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))

from build_annotator_panels import regime_of  # noqa: E402

#: A generic unit vocabulary, used only to tell a *quantity* from a
#: paragraph marker. It is deliberately not the detector's measurement
#: vocabulary: the detector requires the number to be governed by a declared
#: measurement term, and the construction criterion must not require that,
#: or the stratum would be selected on the detector's own criterion.
_UNITS = (
    "percent|per cent|micograms?|milligrams?|grams?|kilograms?|pounds?|tons?|"
    "ppm|parts per million|psig|psi|volts?|amperes?|watts?|decibels?|db|"
    "inches|inch|feet|foot|miles|hours?|days?|minutes?|seconds?|months?|"
    "years?|cubic meters?|cubic feet|square feet|square inches|gallons?|"
    "liters?|litres|degrees|micron|mils|fiber|cc|"
)
_QUANTITY_RE = re.compile(
    r"(?<![\w.])(\d[\d,]*(?:\.\d+)?)\s*(" + _UNITS + r")\b", re.IGNORECASE)


def quantities(text: str) -> set[str]:
    """Every number-with-a-unit in a text, normalised to (value, unit).

    A number without a unit is not a quantity: in a regulation the bare
    numbers are paragraph markers -- "(a)(1)", "(i)", "(C)" -- and counting
    them would say that every renumbered paragraph is a changed limit.
    """
    out: set[str] = set()
    for m in _QUANTITY_RE.finditer(text):
        value = m.group(1).replace(",", "").rstrip(".")
        unit = m.group(2).lower()
        out.add(f"{value}|{unit}")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pairs", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    doc = json.loads(Path(args.pairs).read_text(encoding="utf-8"))
    records: list[dict] = []
    pid = 0
    for p in doc["revision_pairs"]:
        pid += 1
        records.append({"pair_id": pid, "stratum": "revision",
                        "section": p.get("section", ""),
                        "passage_a": p["passage_a"], "passage_b": p["passage_b"],
                        "overlap": p.get("overlap")})
    for p in doc["similar_pairs"]:
        pid += 1
        records.append({"pair_id": pid, "stratum": "similar",
                        "section": "",
                        "passage_a": p["passage_a"], "passage_b": p["passage_b"]})

    overlaps = [r["overlap"] for r in records
                if r["stratum"] == "revision" and r.get("overlap") is not None]
    for r in records:
        r["numbers_changed"] = (quantities(r["passage_a"])
                                != quantities(r["passage_b"]))
        if r["section"]:
            r["regime"] = regime_of(r["section"])
        else:
            r["regime"] = regime_of(_doc_of(r["passage_a"]))
        # The construction label. A revision-stratum pair is the same
        # provision at two issues: a supersession by construction, and a
        # quantity conflict when the two versions state different
        # quantities. The similar stratum carries no construction label --
        # nothing about how the pair was mined implies anything about
        # whether it conflicts.
        if r["stratum"] == "revision":
            r["construction_label"] = ("quantity_conflict"
                                       if r["numbers_changed"]
                                       else "supersession")
        else:
            r["construction_label"] = None

    n_rev = sum(1 for r in records if r["stratum"] == "revision")
    n_num = sum(1 for r in records
                if r["stratum"] == "revision" and r["numbers_changed"])
    out = {
        **doc,
        "pairs_annotated": records,
        "alignment_quality": {
            "n_revision_pairs": n_rev,
            "overlap_min": min(overlaps) if overlaps else None,
            "overlap_p10": sorted(overlaps)[len(overlaps) // 10]
            if overlaps else None,
            "overlap_median": statistics.median(overlaps) if overlaps else None,
            "overlap_p90": sorted(overlaps)[9 * len(overlaps) // 10]
            if overlaps else None,
            "n_at_or_above_0.5": sum(1 for o in overlaps if o >= 0.5),
            "note": "token-set overlap between a paragraph and the paragraph "
                    "it is aligned with across the two snapshots. A low "
                    "overlap means the alignment may have paired the wrong "
                    "paragraphs, which would make the stratum meaningless.",
        },
        "construction_labels": {
            "n_revision_pairs": n_rev,
            "n_with_changed_quantities": n_num,
            "share_with_changed_quantities": n_num / n_rev if n_rev else None,
            "label_distribution": dict(Counter(
                r["construction_label"] for r in records
                if r["construction_label"])),
            "note": "the revision stratum is the same provision at two "
                    "issues by construction, so its conflict type is known "
                    "without any annotation: a supersession, or a quantity "
                    "conflict where the two versions state different "
                    "quantities. The selection criterion asks only whether a "
                    "unit-bearing number differs, which is strictly weaker "
                    "than the detector's own requirement that the number be "
                    "governed by a declared measurement term.",
        },
    }
    Path(args.out).write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"[ro4] {len(records)} pairs; "
          f"{n_num}/{n_rev} revision pairs state different quantities")
    if overlaps:
        print(f"[ro4] alignment overlap: median {statistics.median(overlaps):.3f}, "
              f"p10 {sorted(overlaps)[len(overlaps)//10]:.3f}, "
              f"{sum(1 for o in overlaps if o >= 0.5)}/{len(overlaps)} at or above 0.5")
    print(f"[ro4] wrote {args.out}")
    return 0


def _doc_of(passage: str) -> str:
    """The source document identifier of a passage, from its heading."""
    m = re.search(r"§\s*([0-9]+\.[0-9]+)", passage[:400])
    if m:
        return m.group(1)
    m = re.search(r"\b(1910|1926|60|112|173)\.\d+\b", passage[:400])
    return m.group(0) if m else "1910.1"


if __name__ == "__main__":
    sys.exit(main())
