#!/usr/bin/env python3
"""Score the rubric x specialisation factorial for the RO4 measurement.

**The question.** The RO4 write-up claims that "the rubric's wording moved the
number, not the specialisation", because the generalist control agrees with
each specialist at kappa 0.65-0.72 while the old-rubric judge agrees with
them at kappa 0.07-0.44. That comparison is confounded: the old-rubric rater
was a generalist, so "old rubric" and "generalist" were the same cell. The
decisive cell -- specialist readers on the old rubric -- was never measured.

**The design.** Two factors, crossed:

* **rubric**: v1 (the rubric the first measurement used) or v2 (the sharpened
  one);
* **reader**: generalist (no specialism in any regime) or specialist (one
  reader per regulatory regime, with that regime's brief).

The pairs, the detector, the regime assignment and the regime briefs are
identical across cells. Only the rubric and the reader type vary.

Every cell is read by more than one reader, so a cell's number is not one
reader's idiosyncrasy, and the reader-to-reader spread inside a cell is
visible. Two arms exist to remove a *model* confound: the v2 panel was read
in an earlier session by readers whose model this file cannot verify, so the
v1 generalist and the v2 generalist are each read again here, on the same
model, in the same two halves, and the occupational-safety cell is read again
on the v2 rubric by the same reader that read it on v1.

**How the numbers are produced.** By running the *shipped* evaluation
(`run_revision_eval.py`) once per cell and reading its output. No measurement
logic is re-implemented here: the detection precision, the typing precision,
the Wilson intervals and the Cohen's kappa all come from the same code that
produced every number already in the write-up.

Usage:
    python experiments/run_rubric_factorial.py \
        --pairs ../results_industrial/exp14_pairs_annotated.json \
        --factorial-dir ../results_industrial/panels/factorial \
        --industrial ../results_industrial \
        --out ../results_industrial/exp21_rubric_factorial.json
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVAL = ROOT / "experiments" / "run_revision_eval.py"

#: The cells of the factorial. Each is a list of label files; the reader
#: type is the factor, the rubric version is carried in each file.
CELLS: dict[str, dict] = {
    "generalist_v1": {
        "reader_type": "generalist",
        "rubric": "v1",
        "files": [
            "exp14_judge_b_labels.json",        # the first measurement's judge
            "factorial/labels_generalist_v1_a.json",
            "factorial/labels_generalist_v1_b.json",
        ],
    },
    "generalist_v2": {
        "reader_type": "generalist",
        "rubric": "v2",
        "files": [
            "panels/labels_generalist.json",     # the original generalist control
            "factorial/labels_generalist_v2_a.json",
            "factorial/labels_generalist_v2_b.json",
        ],
    },
    "specialist_v1": {
        "reader_type": "specialist",
        "rubric": "v1",
        "files": [
            "factorial/labels_spec_occupational_v1.json",
            "factorial/labels_spec_process_v1.json",
            "factorial/labels_spec_environmental_v1.json",
            "factorial/labels_spec_hazmat_v1.json",
        ],
    },
    "specialist_v2": {
        "reader_type": "specialist",
        "rubric": "v2",
        "files": [
            "panels/labels_occupational_safety.json",
            "panels/labels_process_safety.json",
            "panels/labels_environmental_control.json",
            "panels/labels_hazmat_transport.json",
        ],
    },
    # The model-matched single-cell contrast: the same reader type, the same
    # regime, the same pairs, the same model, on the two rubrics.
    "occupational_matched": {
        "reader_type": "specialist",
        "rubric": "v1+v2",
        "files": [
            "factorial/labels_spec_occupational_v1.json",
            "factorial/labels_spec_occupational_v2_replicate.json",
        ],
    },
    # The first measurement's own cell. Its two readers did **not** use the
    # same rubric: `judge_a_model` read the original rubric (v0, whose
    # supersession branch required a version marker and so found almost no
    # supersessions), `judge_b_reader` read the marker-test rubric (v1).
    # Their consensus is what produced the 0.075 quoted in the first RO4
    # write-up, and it is a cell in its own right.
    "first_measurement": {
        "reader_type": "generalist",
        "rubric": "v0 and v1 (its two readers differed)",
        "files": [
            "exp14_judge_a_labels.json",
            "exp14_judge_b_labels.json",
        ],
    },
    # The same two rubrics, one reader each, so that the first measurement's
    # number can be decomposed into a rubric part and a reader part.
    "v0_generalist": {
        "reader_type": "generalist",
        "rubric": "v0",
        "files": ["exp14_judge_a_labels.json"],
    },
    "v1_generalist_original": {
        "reader_type": "generalist",
        "rubric": "v1",
        "files": ["exp14_judge_b_labels.json"],
    },
}

#: The individual readers, for the full pairwise kappa matrix.
ALL_RATERS: list[str] = [
    "exp14_judge_a_labels.json",
    "exp14_judge_b_labels.json",
    "panels/labels_generalist.json",
    "panels/labels_occupational_safety.json",
    "panels/labels_process_safety.json",
    "panels/labels_environmental_control.json",
    "panels/labels_hazmat_transport.json",
    "factorial/labels_generalist_v1_a.json",
    "factorial/labels_generalist_v1_b.json",
    "factorial/labels_generalist_v2_a.json",
    "factorial/labels_generalist_v2_b.json",
    "factorial/labels_spec_occupational_v1.json",
    "factorial/labels_spec_process_v1.json",
    "factorial/labels_spec_environmental_v1.json",
    "factorial/labels_spec_hazmat_v1.json",
    "factorial/labels_spec_occupational_v2_replicate.json",
]

PROFILE = "regulatory"


def _run_eval(pairs: Path, label_paths: list[Path], out: Path) -> dict:
    """Run the shipped evaluation over one set of label files."""
    cmd = [sys.executable, str(EVAL),
           "--pairs", str(pairs),
           "--labels", ",".join(str(p) for p in label_paths),
           "--out", str(out),
           "--profiles", PROFILE]
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"evaluation failed for {label_paths}:\n"
                           f"{r.stdout}\n{r.stderr}")
    for line in (r.stdout or "").splitlines():
        if line.strip():
            print(f"    {line}", flush=True)
    return json.loads(out.read_text(encoding="utf-8"))


def _metrics(block: dict) -> dict:
    """The two numbers the factorial turns on, with their intervals."""
    o = block["overall"]
    return {
        "n_flagged": o["n_flagged"],
        "detection_precision": o["precision_any_flag"],
        "detection_precision_ci95": o["precision_any_flag_ci95"],
        "typing_precision": o["precision_typing"],
        "typing_precision_ci95": o["precision_typing_ci95"],
        "recall_any_real_problem": o["recall_any_real_problem"],
        "n_annotated_conflicts": o["n_annotated_conflicts"],
        "n_pairs_total": o["n_pairs_total"],
        "label_distribution_of_flagged":
            block["per_branch"]["semantic"]["label_distribution_of_flagged"],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pairs", required=True)
    ap.add_argument("--industrial", required=True,
                    help="the results_industrial directory")
    ap.add_argument("--factorial-dir", required=True,
                    help="the panels/factorial directory")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    ind = Path(args.industrial)
    fact = Path(args.factorial_dir)

    def resolve(rel: str) -> Path:
        if rel.startswith("factorial/"):
            return fact / rel.split("/", 1)[1]
        return ind / rel

    cells: dict = {}
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        for name, spec in CELLS.items():
            paths = [resolve(f) for f in spec["files"]]
            missing = [p for p in paths if not p.exists()]
            if missing:
                print(f"[factorial] SKIP {name}: missing "
                      f"{[str(m) for m in missing]}", flush=True)
                continue
            print(f"[factorial] cell {name} "
                  f"({spec['rubric']} x {spec['reader_type']}, "
                  f"{len(paths)} readers) ...", flush=True)
            doc = _run_eval(Path(args.pairs), paths, tmpdir / f"{name}.json")
            block = doc["profiles"][PROFILE]
            readers = {}
            for source, blk in block.items():
                if source in ("consensus", "construction_labels"):
                    continue
                readers[source] = _metrics(blk)
            cells[name] = {
                "rubric": spec["rubric"],
                "reader_type": spec["reader_type"],
                "n_readers": len(paths),
                "readers": readers,
                "consensus": _metrics(block["consensus"]),
                "pairwise_kappa_within_cell": {
                    k: v for k, v in doc["annotator_agreement"]["pairwise"].items()
                    if any(k.startswith(f"{r} vs {r2}") or k.startswith(f"{r2} vs {r}")
                           for r in readers for r2 in readers)
                },
            }

        # The full pairwise matrix over every reader.
        print("[factorial] all readers, for the kappa matrix ...", flush=True)
        paths = [resolve(f) for f in ALL_RATERS]
        paths = [p for p in paths if p.exists()]
        missing = [f for f in ALL_RATERS if not resolve(f).exists()]
        if missing:
            print(f"[factorial]   (not yet available: {missing})", flush=True)
        all_doc = _run_eval(Path(args.pairs), paths, tmpdir / "all.json")
        all_block = all_doc["profiles"][PROFILE]

    out: dict = {
        "schema": "mtp.rubric-factorial/1",
        "question": "does the rubric's wording or the reader's specialisation "
                    "move the measured precision?",
        "design": {
            "factors": ["rubric (v1 / v2)", "reader type (generalist / specialist)"],
            "held_constant": ["the 240 pairs", "the detector and its "
                              "configuration", "the regime assignment",
                              "the regime briefs", "the reader model"],
            "note": "every cell is read by more than one reader; the consensus "
                    "takes the majority label and treats a contested pair as "
                    "not a conflict, so a contested pair can only lower the "
                    "measured precision.",
        },
        "cells": cells,
        "all_readers": {
            source: _metrics(blk)
            for source, blk in all_block.items()
            if source not in ("consensus", "construction_labels")
        },
        "pairwise_kappa_all_readers":
            all_doc["annotator_agreement"]["pairwise"],
        "construction_labels": _metrics(all_block["construction_labels"]),
    }

    # -- the effects -------------------------------------------------------
    effects: dict = {}

    def _det(cell: str) -> float | None:
        c = cells.get(cell)
        return None if c is None else c["consensus"]["detection_precision"]

    def _typ(cell: str) -> float | None:
        c = cells.get(cell)
        return None if c is None else c["consensus"]["typing_precision"]

    def _diff(a: str, b: str, key: str) -> dict | None:
        va, vb = _det(a), _det(b)
        if va is None or vb is None:
            return None
        out = {"difference": va - vb, "a": a, "b": b}
        if key == "typing":
            ta, tb = _typ(a), _typ(b)
            out["typing_difference"] = None if ta is None or tb is None \
                else ta - tb
        return out

    effects["rubric_effect_at_generalist"] = _diff("generalist_v2",
                                                   "generalist_v1", "detection")
    effects["rubric_effect_at_specialist"] = _diff("specialist_v2",
                                                    "specialist_v1", "detection")
    effects["specialisation_effect_at_v1"] = _diff("specialist_v1",
                                                    "generalist_v1", "detection")
    effects["specialisation_effect_at_v2"] = _diff("specialist_v2",
                                                    "generalist_v2", "detection")

    r_g = effects["rubric_effect_at_generalist"]
    r_s = effects["rubric_effect_at_specialist"]
    if r_g and r_s:
        effects["interaction"] = {
            "difference_of_differences": r_g["difference"] - r_s["difference"],
            "reading": "the rubric's effect at the generalist cell minus its "
                       "effect at the specialist cell; near zero means the "
                       "two factors act independently",
        }

    # The model-matched single-cell contrast, which holds the reader type,
    # the regime, the pairs and the model fixed and varies only the rubric.
    mm = cells.get("occupational_matched")
    if mm:
        effects["model_matched_rubric_contrast"] = {
            "cell": "occupational_matched",
            "readers": list(mm["readers"].keys()),
            "per_reader": mm["readers"],
            "consensus": mm["consensus"],
        }
    out["effects"] = effects

    # -- what each rubric actually found ------------------------------------
    #
    # The rubric did two things, and this separates them. It changed the
    # *definition* of the target -- which pairs count as a conflict at all --
    # and it changed the *procedure* by which a reader recognises one. The
    # first is visible as the size of the conflict set; the second, in the
    # overlap between two rubrics' conflict sets.
    REAL = {"quantity_conflict", "semantic_conflict", "supersession"}

    def _conflicts(cell_name: str) -> set:
        spec = CELLS.get(cell_name)
        if spec is None:
            return set()
        labels: list[dict] = []
        for rel in spec["files"]:
            path = resolve(rel)
            if not path.exists():
                continue
            labels.append(json.loads(path.read_text(encoding="utf-8"))["labels"])
        if not labels:
            return set()
        out_set = set()
        for key in set().union(*[set(l) for l in labels]):
            votes = [l[key] for l in labels if key in l]
            tally = Counter(votes)
            best, best_n = tally.most_common(1)[0]
            label = best if best_n > len(votes) / 2 else "no_conflict"
            if label in REAL:
                out_set.add(key)
        return out_set

    decomposition: dict = {}
    for reader_type, v1_cell, v2_cell in (
            ("generalist", "generalist_v1", "generalist_v2"),
            ("specialist", "specialist_v1", "specialist_v2")):
        c1, c2 = _conflicts(v1_cell), _conflicts(v2_cell)
        if not c1 or not c2:
            continue
        decomposition[reader_type] = {
            "v1_conflicts": len(c1),
            "v2_conflicts": len(c2),
            "in_both": len(c1 & c2),
            "v1_only": len(c1 - c2),
            "v2_only_the_old_rubric_missed": len(c2 - c1),
            "share_of_the_new_conflicts_the_old_rubric_missed":
                round(len(c2 - c1) / len(c2), 3) if c2 else None,
        }
    out["decomposition"] = decomposition

    Path(args.out).write_text(json.dumps(out, indent=2, default=str),
                               encoding="utf-8")
    print(f"[factorial] wrote {args.out}")

    # A console summary, so the result does not have to be read out of JSON.
    print("\n=== the factorial ===")
    for name, cell in cells.items():
        c = cell["consensus"]
        print(f"{name:24s} {cell['rubric']:6s} {cell['reader_type']:11s} "
              f"n_readers={cell['n_readers']}  detection={c['detection_precision']:.3f} "
              f"typing={c['typing_precision']:.3f}")
    print("\n=== the effects ===")
    for key, val in effects.items():
        if key == "model_matched_rubric_contrast":
            for r, m in val["per_reader"].items():
                print(f"  {r:44s} detection={m['detection_precision']:.3f} "
                      f"typing={m['typing_precision']:.3f}")
        elif isinstance(val, dict) and "difference" in val:
            print(f"  {key:36s} {val['difference']:+.3f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
