#!/usr/bin/env python3
"""Score the contradiction detector against independently annotated pairs (RO4).

**What this measures.** The contradiction gate's precision on a corpus that
actually contains conflicts. Experiment 11 measured it on the focus corpus
and got 0%, because that corpus contains no contradictions: every alarm was
a false positive and the calibration correctly withheld the findings. A
precision measured where there are no positives is a measurement of the
corpus, not of the mechanism.

Here the pairs come from two strata:

``revision``
    The same regulation, read on two dates either side of a real amendment.
    Where the amendment changed a limit, the two versions state different
    requirements. These are genuine conflicts in real industrial text.

``similar``
    Cross-document pairs the retriever would put together. These carry the
    false-alarm load.

The labels come from an independent annotator that never saw the detector's
output (the rubric and the two passages, and nothing else), so the precision
below is the detector's, not the annotator's opinion of it.

**Two profiles, side by side.** The detector's measurement vocabulary and
its version vocabulary are declared priors written for operations and
supply-chain prose. A regulatory corpus binds on "permissible exposure
limit" and cites "ASTM A47-68". The `operations`/`commercial` profile is
the shipped one; the `regulatory` profile is the extension the industrial
measurement motivates. Both are reported, because the interesting number is
the difference between them.

Usage:
    MTP_VARIANT=industrial python experiments/run_revision_eval.py \
        --pairs  ../results_industrial/exp14_pairs.json \
        --labels ../results_industrial/exp14_judge_labels.json \
        --out    ../results_industrial/exp14_revision_eval.json
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import math
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

# The entailment and embedding passes are the expensive steps and are
# embarrassingly parallel; torch's default thread count leaves most of the
# machine idle.
try:
    import torch

    torch.set_num_threads(int(os.environ.get(
        "MTP_TORCH_THREADS", "0") or 0) or (os.cpu_count() or 4))
except Exception:  # pragma: no cover - torch is always present
    pass

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import CONFIG, ContradictionConfig  # noqa: E402
from src.contradiction import detect_contradictions  # noqa: E402
from src.models import embed_texts  # noqa: E402
from src.models import nli_probs as nli_probs_fn  # noqa: E402

#: The label each branch is responsible for.
BRANCH_FOR_LABEL = {
    "quantity_conflict": "quantity",
    "semantic_conflict": "semantic",
    "supersession": "revision",
}

#: The labels that count as a real problem a practitioner should be told
#: about. `term_mismatch`, `granularity` and `no_conflict` are false alarms.
REAL_LABELS = ("quantity_conflict", "semantic_conflict", "supersession")


def wilson(successes: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (float("nan"), float("nan"))
    p = successes / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, centre - half), min(1.0, centre + half))


_TOKEN_RE = re.compile(r"[a-z0-9]+")


def change_fraction(a: str, b: str) -> float:
    """How much of the text differs between the two passages.

    A token-level measure, and one that knows nothing about the detector:
    it says how much was rewritten, not whether what was rewritten conflicts.
    It is the covariate that separates an *editorial* amendment -- a
    renumbered paragraph, an added cross-reference -- from a *substantive*
    one, and it is what explains why the amended-paragraph stratum holds so
    few real conflicts.
    """
    ta = set(_TOKEN_RE.findall(a.lower()))
    tb = set(_TOKEN_RE.findall(b.lower()))
    if not ta and not tb:
        return 0.0
    return 1.0 - (len(ta & tb) / max(len(ta | tb), 1))


def _profile_config(profile: str) -> ContradictionConfig:
    """The detector configuration for a named profile.

    Three configurations, because the two changes are separable and should
    be reported separately:

    ``shipped``
        the operations vocabulary, the commercial version vocabulary and the
        shipped look-back. This is the framework as shipped.
    ``lookback``
        the same vocabularies with the look-back widened, which changes how
        *far* the rule reaches without changing *what* it looks for.
    ``regulatory``
        the regulatory measurement and version vocabularies with the
        widened look-back -- the configuration the industrial measurement
        motivates.
    """
    if profile == "regulatory":
        return dataclasses.replace(
            CONFIG.contradiction,
            measurement_profile="regulatory",
            standard_profile="regulatory",
            measurement_lookback=3,
            instance_identifier=True,
        )
    if profile == "instance":
        return dataclasses.replace(
            CONFIG.contradiction,
            measurement_lookback=3,
            instance_identifier=True,
        )
    if profile == "lookback":
        return dataclasses.replace(
            CONFIG.contradiction, measurement_lookback=3)
    return CONFIG.contradiction


def _by_change_class(rows: list[dict], findings: dict) -> dict:
    """The detector's behaviour split by how much the two texts changed.

    A regulatory amendment is usually editorial: a renumbered paragraph, an
    added cross-reference, a comma. Splitting the pool by how much was
    rewritten separates "the detector fires on everything the rule touched"
    from "the detector fires on the amendments that changed the requirement".
    """
    out: dict = {}
    for klass in ("editorial", "substantive"):
        sel = [r for r in rows if r["change_class"] == klass]
        flagged = [r for r in sel
                   if findings[r["pair_id"]] is not None
                   and findings[r["pair_id"]].flagged]
        real = sum(1 for r in flagged if r["label"] in REAL_LABELS)
        positives = sum(1 for r in sel if r["label"] in REAL_LABELS)
        lo, hi = wilson(real, len(flagged))
        out[klass] = {
            "n_pairs": len(sel),
            "n_annotated_conflicts": positives,
            "conflict_base_rate": positives / len(sel) if sel else None,
            "n_flagged": len(flagged),
            "n_flagged_with_a_real_problem": real,
            "precision_any_flag": real / len(flagged) if flagged else None,
            "precision_ci95": [lo, hi],
            "label_distribution": dict(Counter(r["label"] for r in sel)),
        }
    return out


def _by_stratum(rows: list[dict], findings: dict) -> dict:
    """The detector's behaviour on each stratum separately.

    The `revision` stratum is constructed: every pair in it is the same
    provision read on two dates, so it is a supersession by construction --
    a fact about the corpus rather than a judgement about the pair. That
    makes the stratum the one place where the *branch* the detector assigns
    can be checked against something that is not an annotation.
    """
    out: dict = {}
    for stratum in ("revision", "similar"):
        sel = [r for r in rows if r["stratum"] == stratum]
        flagged = [r for r in sel
                   if findings[r["pair_id"]] is not None
                   and findings[r["pair_id"]].flagged]
        real = sum(1 for r in flagged if r["label"] in REAL_LABELS)
        lo, hi = wilson(real, len(flagged))
        out[stratum] = {
            "n_pairs": len(sel),
            "n_flagged": len(flagged),
            "flag_rate": len(flagged) / len(sel) if sel else None,
            "n_flagged_with_a_real_problem": real,
            "precision_any_flag": real / len(flagged) if flagged else None,
            "precision_ci95": [lo, hi],
            "branch_distribution_of_the_alarms": dict(
                Counter(findings[r["pair_id"]].kind for r in flagged)),
            "label_distribution": dict(Counter(r["label"] for r in sel)),
            "note": "the revision stratum is two issues of the same "
                    "provision by construction, so its conflict type is "
                    "known independently of any annotation; the branch "
                    "distribution says which branch the detector used",
        }
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pairs", required=True)
    ap.add_argument("--labels", required=True,
                    help="one or more annotation files, comma-separated")
    ap.add_argument("--out", required=True)
    ap.add_argument("--profiles", default="operations,regulatory")
    args = ap.parse_args()

    pairs_doc = json.loads(Path(args.pairs).read_text(encoding="utf-8"))
    label_files = [p.strip() for p in args.labels.split(",") if p.strip()]
    label_sets: dict[str, dict] = {}
    for path in label_files:
        doc = json.loads(Path(path).read_text(encoding="utf-8"))
        name = doc.get("annotator") or Path(path).stem
        label_sets[name] = doc.get("labels", {})

    revision_pairs = pairs_doc["revision_pairs"]
    similar_pairs = pairs_doc["similar_pairs"]

    # Rebuild the pair list in the same order the judge sheet used, so the
    # pair ids line up.
    records: list[dict] = []
    pid = 0
    for p in revision_pairs:
        pid += 1
        records.append({"pair_id": pid, "stratum": "revision",
                        "passage_a": p["passage_a"], "passage_b": p["passage_b"]})
    for p in similar_pairs:
        pid += 1
        records.append({"pair_id": pid, "stratum": "similar",
                        "passage_a": p["passage_a"], "passage_b": p["passage_b"]})

    # The construction labels, where the corpus provides them: a revision
    # stratum pair is the same provision at two issues, so its conflict type
    # is known without any annotation. They are a *separate view*, never a
    # voter: mixing a construction label into the consensus would let the
    # corpus's own construction settle a question the annotators were
    # asked to answer.
    construction: dict[str, str] = {}
    for r in pairs_doc.get("pairs_annotated", []):
        if r.get("construction_label"):
            construction[str(r["pair_id"])] = r["construction_label"]

    rows = []
    for rec in records:
        key = str(rec["pair_id"])
        votes = {name: ls.get(key) for name, ls in label_sets.items()}
        votes = {k: v for k, v in votes.items() if v}
        if not votes:
            continue
        row = {**rec, "votes": votes}
        row["change"] = change_fraction(rec["passage_a"], rec["passage_b"])
        row["change_class"] = ("substantive" if row["change"] >= 0.30
                               else "editorial")
        # The consensus label: the label the majority gives. A pair the
        # annotators split on is *contested*; it is reported as "not a
        # conflict" in the consensus view, because a precision claim that
        # counts a contested pair as a hit can only inflate the number.
        tally = Counter(votes.values())
        best, best_n = tally.most_common(1)[0]
        row["label"] = best if best_n > len(votes) / 2 else "no_conflict"
        row["majority_label"] = best
        row["contested"] = len(set(votes.values())) > 1
        rows.append(row)

    # Every annotator's labels are also scored on their own, because a
    # consensus that depends on a tie-break rule hides how much the number
    # moves with the annotator.
    label_views: dict[str, list[dict]] = {"consensus": rows}
    for name in label_sets:
        label_views[name] = [
            {**r, "label": label_sets[name].get(str(r["pair_id"]),
                                                 "no_conflict")}
            for r in rows if label_sets[name].get(str(r["pair_id"]))]
    if construction:
        label_views["construction_labels"] = [
            {**r, "label": construction[str(r["pair_id"])]}
            for r in rows if str(r["pair_id"]) in construction]

    # The agreement between the annotators, pairwise.
    agreement: dict = {"pairwise": {}, "annotators": sorted(label_sets)}
    names = sorted(label_sets)
    for i, a_name in enumerate(names):
        for b_name in names[i + 1:]:
            common = [str(r["pair_id"]) for r in records
                      if label_sets[a_name].get(str(r["pair_id"]))
                      and label_sets[b_name].get(str(r["pair_id"]))]
            if not common:
                continue
            a = [label_sets[a_name][k] for k in common]
            b = [label_sets[b_name][k] for k in common]
            from src.stats import cohens_kappa
            kappa, lo, hi = cohens_kappa(a, b)
            crosstab: dict[str, int] = defaultdict(int)
            for x, y in zip(a, b):
                crosstab[f"{x} | {y}"] += 1
            agreement["pairwise"][f"{a_name} vs {b_name}"] = {
                "n_labelled_by_both": len(common),
                "cohens_kappa": kappa,
                "ci95": [lo, hi],
                "agreement_rate": sum(1 for x, y in zip(a, b) if x == y)
                / len(common),
                "crosstab": dict(crosstab),
            }
    if agreement["pairwise"]:
        agreement["note"] = (
            "the consensus view takes the majority label and treats a "
            "contested pair as not a conflict, so a contested pair can only "
            "lower the measured precision, never raise it. Every annotator "
            "is also scored alone, so the spread across annotators is "
            "visible rather than hidden by the tie-break.")

    print(f"[ro4] {len(rows)} annotated pairs "
          f"({Counter(r['stratum'] for r in rows)})", flush=True)
    print(f"[ro4] label distribution: {Counter(r['label'] for r in rows)}",
          flush=True)

    for r in rows:
        r["change"] = change_fraction(r["passage_a"], r["passage_b"])
        r["change_class"] = ("substantive" if r["change"] >= 0.30
                             else "editorial")

    # One embedding pass for every passage.
    texts, index_of = [], {}
    for r in rows:
        for side in ("passage_a", "passage_b"):
            t = r[side]
            if t not in index_of:
                index_of[t] = len(texts)
                texts.append(t)
    print(f"[ro4] embedding {len(texts)} passages ...", flush=True)
    emb = embed_texts(texts, model_name=CONFIG.embedding.model,
                      batch_size=CONFIG.embedding.batch_size,
                      normalize=CONFIG.embedding.normalize,
                      dim=CONFIG.embedding.dim)
    emb_lookup = {t: emb[index_of[t]] for t in index_of}

    results: dict = {
        "schema": "mtp.revision-eval/1",
        "n_pairs_annotated": len(rows),
        "label_distribution": dict(Counter(r["label"] for r in rows)),
        "stratum_distribution": dict(Counter(r["stratum"] for r in rows)),
        "annotator_agreement": agreement,
        "profiles": {},
    }

    # The label sources the metrics are computed against: the consensus, and
    # each annotator on its own. The detector's verdict does not depend on
    # the labels, so it is computed once per profile and then scored against
    # each source -- which is what makes the sensitivity of the conclusion
    # to the annotator disagreement visible.
    label_sources = label_views

    for profile in [p.strip() for p in args.profiles.split(",") if p.strip()]:
        cfg = _profile_config(profile)
        # One batched entailment call for every pair, rather than one call
        # per pair: the per-call overhead dominates the actual inference, and
        # scoring a few hundred pairs this way takes minutes rather than
        # hours.
        nli_inputs = [(r["passage_a"], r["passage_b"]) for r in rows]
        nli_probs = nli_probs_fn(nli_inputs, cfg.nli_model) if nli_inputs else []
        findings_by_id = {}
        for r, probs in zip(rows, nli_probs):
            a, b = r["passage_a"], r["passage_b"]
            vectors = np.stack([emb_lookup[a], emb_lookup[b]])
            found = detect_contradictions(
                [a, b], ["a", "b"], embeddings=vectors, config=cfg,
                probs=[probs])
            findings_by_id[r["pair_id"]] = found[0] if found else None

        for source, source_rows in label_sources.items():
            # -- per-branch precision and recall ----------------------------
            per_branch: dict = {}
            for branch in ("semantic", "quantity", "revision"):
                per_branch[branch] = {
                    "n_flagged": 0,
                    "n_label_matching_this_branch": 0,
                    "n_label_a_real_problem": 0,
                    "precision_vs_matching_label": None,
                    "precision_vs_any_real_problem": None,
                    "precision_ci95": [float("nan"), float("nan")],
                    "label_distribution_of_flagged": {},
                    "n_flagged_in_revision_stratum": 0,
                    "n_flagged_in_similar_stratum": 0,
                    "recall_vs_matching_label": None,
                    "recall_ci95": [float("nan"), float("nan")],
                    "n_annotated_positives": 0,
                }
            for branch in ("semantic", "quantity", "revision"):
                flagged = [r for r in source_rows
                           if findings_by_id[r["pair_id"]] is not None
                           and findings_by_id[r["pair_id"]].kind == branch
                           and findings_by_id[r["pair_id"]].flagged]
                n = len(flagged)
                matching = sum(1 for r in flagged
                               if BRANCH_FOR_LABEL.get(r["label"]) == branch)
                real = sum(1 for r in flagged if r["label"] in REAL_LABELS)
                lo, hi = wilson(real, n)
                per_branch[branch] = {
                    "n_flagged": n,
                    "n_label_matching_this_branch": matching,
                    "n_label_a_real_problem": real,
                    "precision_vs_matching_label": (matching / n) if n else None,
                    "precision_vs_any_real_problem": (real / n) if n else None,
                    "precision_ci95": [lo, hi],
                    "label_distribution_of_flagged": dict(
                        Counter(r["label"] for r in flagged)),
                    "n_flagged_in_revision_stratum": sum(
                        1 for r in flagged if r["stratum"] == "revision"),
                    "n_flagged_in_similar_stratum": sum(
                        1 for r in flagged if r["stratum"] == "similar"),
                }

            # -- recall per branch ----------------------------------------
            # BRANCH_FOR_LABEL maps a *label* to the *branch* that owns it,
            # so the unpacking is (label, branch).
            for label, branch in BRANCH_FOR_LABEL.items():
                positives = [r for r in source_rows if r["label"] == label]
                hit = sum(1 for r in positives
                          if findings_by_id[r["pair_id"]] is not None
                          and findings_by_id[r["pair_id"]].kind == branch
                          and findings_by_id[r["pair_id"]].flagged)
                lo, hi = wilson(hit, len(positives))
                per_branch.setdefault(branch, {})["recall_vs_matching_label"] = (
                    hit / len(positives) if positives else None)
                per_branch[branch]["recall_ci95"] = [lo, hi]
                per_branch[branch]["n_annotated_positives"] = len(positives)

            # -- the mechanism as a whole ---------------------------------
            flagged = [r for r in source_rows
                       if findings_by_id[r["pair_id"]] is not None
                       and findings_by_id[r["pair_id"]].flagged]
            real = sum(1 for r in flagged if r["label"] in REAL_LABELS)
            lo, hi = wilson(real, len(flagged))
            n_positive = sum(1 for r in source_rows
                             if r["label"] in REAL_LABELS)
            # Detection and typing are different questions. "Detection" asks
            # whether the alarm points at something real; "typing" asks
            # whether the branch that raised it is the branch that owns the
            # conflict. A detector can be excellent at the first and
            # systematically wrong about the second, and the second is what
            # tells the practitioner what to do about it.
            typed = sum(1 for r in flagged
                        if BRANCH_FOR_LABEL.get(r["label"])
                        == findings_by_id[r["pair_id"]].kind)
            lo2, hi2 = wilson(typed, len(flagged))
            overall = {
                "n_flagged": len(flagged),
                "n_flagged_with_a_real_problem": real,
                "precision_any_flag": real / len(flagged) if flagged else None,
                "precision_any_flag_ci95": [lo, hi],
                "n_flagged_typed_correctly": typed,
                "precision_typing": typed / len(flagged) if flagged else None,
                "precision_typing_ci95": [lo2, hi2],
                "n_pairs_total": len(source_rows),
                "flag_rate": len(flagged) / len(source_rows) if source_rows else None,
                "recall_any_real_problem": (real / n_positive
                                            if n_positive else None),
                "n_annotated_conflicts": n_positive,
                "note": "precision_any_flag is the fraction of the detector's "
                        "alarms that correspond to a real conflict of any "
                        "type -- detection. precision_typing is the fraction "
                        "whose branch is the branch that owns the conflict "
                        "-- typing. recall_any_real_problem is the fraction "
                        "of the annotated conflicts the detector alarms on at "
                        "all",
            }

            # -- the confusion matrix -------------------------------------
            confusion = defaultdict(int)
            for r in source_rows:
                f = findings_by_id[r["pair_id"]]
                kind = f.kind if (f is not None and f.flagged) else "not_flagged"
                confusion[f'{r["label"]} -> {kind}'] += 1

            # -- which branches would survive the framework's own floor ----
            floor = 0.5
            withheld = []
            for branch, block in per_branch.items():
                p = block.get("precision_vs_any_real_problem")
                if p is not None and p < floor:
                    withheld.append({"branch": branch, "precision": p,
                                     "n_flagged": block["n_flagged"]})

            results["profiles"].setdefault(profile, {})[source] = {
                "measurement_profile": cfg.measurement_profile,
                "standard_profile": cfg.standard_profile,
                "per_branch": per_branch,
                "overall": overall,
                "confusion": dict(confusion),
                "branches_below_the_precision_floor": withheld,
                "by_change_class": _by_change_class(source_rows, findings_by_id),
                "by_stratum": _by_stratum(source_rows, findings_by_id),
                "surviving_findings": sum(
                    1 for r in flagged
                    if per_branch.get(findings_by_id[r["pair_id"]].kind, {})
                    .get("precision_vs_any_real_problem", 1.0) >= floor),
            }
            print(f"[ro4] profile={profile} labels={source}: "
                  f"{len(flagged)} alarms, precision "
                  f"{overall['precision_any_flag']}", flush=True)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, indent=2, default=float), encoding="utf-8")
    print(f"[ro4] wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
