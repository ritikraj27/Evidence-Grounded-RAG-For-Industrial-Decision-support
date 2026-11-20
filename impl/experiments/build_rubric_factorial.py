#!/usr/bin/env python3
"""Build the v1-rubric annotation sheets for the rubric x specialisation factorial.

**Why this file exists.** The RO4 write-up claims that "the rubric's wording
moved the number, not the specialisation", because the generalist control
agrees with each specialist at kappa 0.65-0.72 while the old-rubric judge
agrees with them at kappa 0.07-0.44. That comparison is **confounded**: the
old-rubric rater was a generalist, so "old rubric" and "generalist" are the
same cell. The decisive cell -- *specialist readers on the old rubric* -- was
never measured.

This file builds the sheets for that cell (and for a second old-rubric
generalist, so the old-rubric cell has two independent readers and the
detector's measured precision can be checked for reader-to-reader spread).

The treatment is **the rubric**, and only the rubric: the regime assignment,
the regime brief, the reader note and the pairs are identical to the v2
panels. The rubric text and the instructions are taken verbatim from the
first measurement's judge sheet (`exp14_judge_input.json`), so the v1 arm is
the rubric as it actually was, not a reconstruction.

Usage:
    python experiments/build_rubric_factorial.py \
        --judge-input ../results_industrial/exp14_judge_input.json \
        --panels ../results_industrial/panels \
        --outdir ../results_industrial/panels/factorial
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_annotator_panels import REGIMES  # noqa: E402

#: The labels both rubric versions allow. The v1 sheet's own list is used
#: when present; this is the fallback.
LABELS_ALLOWED = ["quantity_conflict", "semantic_conflict", "supersession",
                   "granularity", "term_mismatch", "no_conflict"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--judge-input", required=True,
                    help="the v1 judge sheet, for its rubric and instructions")
    ap.add_argument("--panels", required=True,
                    help="the v2 panels directory, for the regime briefs")
    ap.add_argument("--outdir", required=True)
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    judge = json.loads(Path(args.judge_input).read_text(encoding="utf-8"))
    rubric_v1 = judge["rubric"]
    instructions_v1 = judge["instructions"]
    labels_allowed = judge.get("labels_allowed", LABELS_ALLOWED)

    # The pairs, in the order the v2 panels used, so a pair id means the same
    # pair in every cell of the factorial.
    general = json.loads(
        (Path(args.panels) / "panel_generalist.json").read_text(encoding="utf-8"))
    pairs = general["pairs"]
    print(f"[factorial] {len(pairs)} pairs from the generalist panel")

    # Which regime each pair belongs to, taken from the v2 regime map.
    regime_map = json.loads(
        (Path(args.panels).parent / "exp14_pairs_with_regime.json")
        .read_text(encoding="utf-8"))
    by_id = {str(r["pair_id"]): r["regime"]
             for r in regime_map["pairs_with_regime"]}

    for regime, meta in REGIMES.items():
        sel = [p for p in pairs if by_id.get(str(p["pair_id"])) == regime]
        if not sel:
            continue
        sheet = {
            "schema": "mtp.revision-judge-input/2",
            "regime": regime,
            "regime_title": meta["title"],
            "regime_governs": meta["governs"],
            "reader_note": meta["reader_note"],
            "parts": meta["parts"],
            "instructions": instructions_v1,
            "rubric": rubric_v1,
            "labels_allowed": labels_allowed,
            "pairs": [{"pair_id": p["pair_id"], "passage_a": p["passage_a"],
                       "passage_b": p["passage_b"]} for p in sel],
        }
        path = outdir / f"panel_{regime}_v1.json"
        path.write_text(json.dumps(sheet, indent=2), encoding="utf-8")
        print(f"[factorial] {regime:22s} {len(sel):3d} pairs -> {path.name}")

    # The old-rubric generalist: a second independent reader for the v1
    # generalist cell, so the old-rubric cell is not a single reader's
    # idiosyncrasy.
    general_sheet = {
        "schema": "mtp.revision-judge-input/2",
        "regime": "general",
        "regime_title": "All four regimes, read without a specialism",
        "regime_governs": "occupational safety, process safety, environmental "
                          "control and hazardous-materials transport.",
        "reader_note": "You are reading pairs from four different regulatory "
                       "regimes without a specialism in any of them. Apply the "
                       "rubric as written.",
        "instructions": instructions_v1,
        "rubric": rubric_v1,
        "labels_allowed": labels_allowed,
        "pairs": [{"pair_id": p["pair_id"], "passage_a": p["passage_a"],
                   "passage_b": p["passage_b"]} for p in pairs],
    }
    path = outdir / "panel_generalist_v1.json"
    path.write_text(json.dumps(general_sheet, indent=2), encoding="utf-8")
    print(f"[factorial] {'generalist':22s} {len(pairs):3d} pairs -> {path.name}")

    counts = Counter(by_id.get(str(p["pair_id"])) for p in pairs)
    print(f"[factorial] regime distribution: {dict(counts)}")

    # -- the matched-model replicates -------------------------------------
    #
    # The v2 panel's readers were produced in an earlier session, by a model
    # this file cannot verify. A rubric effect measured between the v1
    # readers and the v2 panel would therefore be confounded with a model
    # effect. Two replicate arms remove that confound: the same readers, on
    # the same model, on the other rubric.
    #
    # The generalist arm is split in two halves for both rubrics, so the two
    # generalist cells have the same number of readers, the same model and
    # the same chunking -- and the split gives a reader-to-reader spread
    # inside each cell rather than one reader standing for a cell.

    def _slice(items, start, end):
        return items[start:end]

    half = len(pairs) // 2
    general_sheet["pairs"] = _slice(pairs, 0, half)
    path = outdir / "panel_generalist_v1_a.json"
    path.write_text(json.dumps(general_sheet, indent=2), encoding="utf-8")
    print(f"[factorial] {'generalist_v1_a':22s} {half:3d} pairs -> {path.name}")

    general_sheet["pairs"] = _slice(pairs, half, len(pairs))
    path = outdir / "panel_generalist_v1_b.json"
    path.write_text(json.dumps(general_sheet, indent=2), encoding="utf-8")
    print(f"[factorial] {'generalist_v1_b':22s} {len(pairs) - half:3d} pairs "
          f"-> {path.name}")

    # The v2 generalist, split the same way, on the v2 rubric and instructions.
    v2 = json.loads(
        (Path(args.panels) / "panel_generalist.json").read_text(encoding="utf-8"))
    v2_general = {
        "schema": "mtp.revision-judge-input/2",
        "regime": "general",
        "regime_title": "All four regimes, read without a specialism",
        "regime_governs": "occupational safety, process safety, environmental "
                          "control and hazardous-materials transport.",
        "reader_note": "You are reading pairs from four different regulatory "
                       "regimes without a specialism in any of them. Apply the "
                       "rubric as written.",
        "instructions": v2["instructions"],
        "rubric": v2["rubric"],
        "labels_allowed": v2["labels_allowed"],
    }
    v2_half = len(v2["pairs"]) // 2
    for tag, chunk in (("a", v2["pairs"][:v2_half]),
                       ("b", v2["pairs"][v2_half:])):
        sheet = dict(v2_general, pairs=[{"pair_id": p["pair_id"],
                                         "passage_a": p["passage_a"],
                                         "passage_b": p["passage_b"]}
                                        for p in chunk])
        path = outdir / f"panel_generalist_v2_{tag}.json"
        path.write_text(json.dumps(sheet, indent=2), encoding="utf-8")
        print(f"[factorial] {'generalist_v2_' + tag:22s} {len(chunk):3d} pairs "
              f"-> {path.name}")

    # The v2 occupational sheet, read again by the same model that reads the
    # v1 occupational sheet.
    v2_occ = json.loads(
        (Path(args.panels) / "panel_occupational_safety.json")
        .read_text(encoding="utf-8"))
    path = outdir / "panel_occupational_safety_v2_replicate.json"
    path.write_text(json.dumps(v2_occ, indent=2), encoding="utf-8")
    print(f"[factorial] {'occupational_v2_repl':22s} "
          f"{len(v2_occ['pairs']):3d} pairs -> {path.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
