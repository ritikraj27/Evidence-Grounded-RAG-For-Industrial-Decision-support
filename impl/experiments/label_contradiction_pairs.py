#!/usr/bin/env python3
"""Sample and score the contradiction gate's pairs for hand labelling.

**Why this exists.** The contradiction gate's recall on the *verifiable*
subset is 1.000 by construction, because that subset is defined by the
presence of a numeric conflict and the numeric detector is an OR-branch of
the gate. The gate's *precision* cannot be computed from a proxy either: every
proxy available on this corpus is defined by one of the gate's own branches,
so it cannot credit an alarm that only the other branch raised. The
experiment therefore reports how the alarms split between the branches and
calls the rest a precision gap (limitation L12).

The only way to close that gap is to put the pairs in front of a reader. This
script is the instrument for that: it samples the pairs, writes a sheet with
the rubric attached, and scores a filled sheet into a precision and a recall
with confidence intervals.

**The sampling design.** Two populations, sampled separately, because they
answer different questions:

* the **alarms** -- every pair the gate flagged. Precision is the fraction
  of these a reader calls a genuine contradiction. The numeric-only stratum
  (raised by the numeric branch alone) is the contested one and is taken in
  full; the conjunction stratum is sampled.
* the **unflagged** pairs -- a simple random sample of the whole unflagged
  population. Recall needs an estimate of how many true contradictions the
  gate *missed*, and a simple random sample is what makes that estimate
  unbiased; the sample is then scaled by the population size. A separate
  *near-miss* stratum is drawn for diagnosis but is **not** pooled into the
  recall estimate, because it is enriched by construction and pooling an
  enriched stratum into a population estimate would bias it.

**The rubric** is in `impl/experiments/data/contradiction_label_rubric.md`
and is copied into every sheet, so a reader cannot label against a definition
they have not seen.

Usage:

    # 1. build the sheet
    python experiments/label_contradiction_pairs.py --sample

    # 2. a human (or an author, with the caveat the sheet records) fills in
    #    the `label` field of each pair

    # 3. score it
    python experiments/label_contradiction_pairs.py --score
"""
from __future__ import annotations

import argparse
import json
import math
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.config import RESULTS_DIR  # noqa: E402

PAIRS_NAME = "exp3_contradiction_pairs.jsonl"
SHEET_NAME = "exp11_contradiction_labels.json"
RUBRIC = Path(__file__).resolve().parent / "data" / "contradiction_label_rubric.md"

#: The label a reader can assign to a pair.
LABELS = ("contradiction", "granularity", "supersession", "term_mismatch",
          "no_conflict")

#: A pair is a true contradiction only under this label.
TRUE_LABEL = "contradiction"

#: How many pairs to take from each stratum of the flagged population.
ALARM_SAMPLE = {"numeric_only": 40, "conjunction": 60, "revision": 40}

#: How many unflagged pairs to draw. The recall estimate is this sample
#: scaled up by the size of the unflagged population, so its width is set
#: here and by the number of true contradictions it happens to contain.
UNFLAGGED_SAMPLE = 80

#: How many near-miss pairs to draw for diagnosis only.
NEAR_MISS_SAMPLE = 30

#: A pair is a near miss if the NLI probability was within this distance of
#: the threshold and the subject check would have passed.
NEAR_MISS_MARGIN = 0.2


def load_pairs() -> list[dict]:
    p = RESULTS_DIR / PAIRS_NAME
    if not p.exists():
        raise SystemExit(
            f"{p} does not exist. Run experiments/run_contradiction.py first: "
            "it writes the pairs this script samples from.")
    out = []
    for line in p.read_text(encoding="utf-8").splitlines():
        if line.strip():
            out.append(json.loads(line))
    return out


def _same_subject(pair: dict) -> bool:
    """The subject check, recomputed from the stored scores.

    The detector's own `nli_and_subject` flag is recomputed here rather than
    reused, because the near-miss stratum needs the subject check *without*
    the NLI threshold -- a pair whose subject check passed but whose NLI
    probability fell short is exactly the kind of pair that could be a missed
    contradiction.

    The rule matches the detector's: topical similarity *and* shared
    concrete objects, both required.
    """
    sim = pair.get("topical_similarity")
    ent = pair.get("entity_overlap") or 0.0
    topic_ok = sim is not None and sim >= 0.55
    return bool(topic_ok and ent >= 0.1)


def _near_miss(pair: dict) -> bool:
    p = pair.get("nli_contradiction_prob")
    if p is None:
        return False
    return 0.7 - NEAR_MISS_MARGIN <= p < 0.7 and _same_subject(pair)


def sample(pairs: list[dict], seed: int) -> dict:
    """Draw the stratified sheet."""
    rng = random.Random(seed)
    flagged = [p for p in pairs if p.get("flagged")]
    unflagged = [p for p in pairs if not p.get("flagged")]

    # The gate has three branches and each is a separate stratum, because
    # each has a different evidence base: the semantic branch is judged by
    # reader labels, the quantity branch by whether the two passages are
    # about the same instance, and the revision branch by whether the two
    # passages really are two issues of the same standard. The two small
    # strata are taken in full; the semantic one is sampled.
    numeric_only = [p for p in flagged if p.get("kind") == "quantity"]
    revision = [p for p in flagged if p.get("kind") == "revision"]
    conjunction = [p for p in flagged
                   if p.get("kind") not in ("quantity", "revision")]

    def _take(pool, k):
        pool = list(pool)
        rng.shuffle(pool)
        return pool[:k]

    selected: list[tuple[str, dict]] = []
    for p in _take(numeric_only, ALARM_SAMPLE["numeric_only"]):
        selected.append(("numeric_only_alarm", p))
    for p in _take(revision, ALARM_SAMPLE["revision"]):
        selected.append(("revision_alarm", p))
    for p in _take(conjunction, ALARM_SAMPLE["conjunction"]):
        selected.append(("conjunction_alarm", p))

    # The unflagged sample is a simple random sample of the whole unflagged
    # population: that is what makes the recall estimate unbiased.
    unflagged_sample = _take(unflagged, UNFLAGGED_SAMPLE)
    for p in unflagged_sample:
        selected.append(("unflagged_random", p))

    # Diagnostic only -- enriched by construction, so never pooled into the
    # population estimate.
    near_miss_pool = [p for p in unflagged
                      if p["pair_id"] not in {q["pair_id"] for q in unflagged_sample}
                      and _near_miss(p)]
    for p in _take(near_miss_pool, NEAR_MISS_SAMPLE):
        selected.append(("near_miss_diagnostic", p))

    rubric = RUBRIC.read_text(encoding="utf-8") if RUBRIC.exists() else ""
    sheet = {
        "schema": "mtp.contradiction-labels/1",
        "seed": seed,
        "instructions": (
            "For each pair, read both passages and set `label` to exactly one "
            "of: contradiction, granularity, supersession, term_mismatch, "
            "no_conflict. Use the rubric below. `contradiction` means the two "
            "passages state incompatible facts about the same subject -- "
            "nothing else counts as a true contradiction, and everything else "
            "is a false alarm."),
        "rubric": rubric,
        "labels_allowed": list(LABELS),
        "true_label": TRUE_LABEL,
        "populations": {
            "n_pairs": len(pairs),
            "n_flagged": len(flagged),
            "n_unflagged": len(unflagged),
            "n_numeric_only_alarms": len(numeric_only),
            "n_conjunction_alarms": len(conjunction),
            "n_revision_alarms": len(revision),
        },
        "sampling": {
            "n_alarm_numeric_only": min(len(numeric_only), ALARM_SAMPLE["numeric_only"]),
            "n_alarm_revision": min(len(revision), ALARM_SAMPLE["revision"]),
            "n_alarm_conjunction": min(len(conjunction), ALARM_SAMPLE["conjunction"]),
            "n_unflagged_random": len(unflagged_sample),
            "n_near_miss_diagnostic": min(len(near_miss_pool), NEAR_MISS_SAMPLE),
        },
        "pairs": [],
    }
    for stratum, p in selected:
        sheet["pairs"].append({
            "pair_id": p["pair_id"],
            "stratum": stratum,
            "chunk_a": p["chunk_a"],
            "chunk_b": p["chunk_b"],
            "text_a": p["text_a"],
            "text_b": p["text_b"],
            "detector": {
                "nli_contradiction_prob": p["nli_contradiction_prob"],
                "topical_similarity": p["topical_similarity"],
                "entity_overlap": p["entity_overlap"],
                "numeric_conflicts": p["numeric_conflicts"],
                "revision_conflicts": p.get("revision_conflicts", []),
                "kind": p.get("kind", "semantic"),
                "nli_and_subject": p["nli_and_subject"],
                "flagged": p["flagged"],
            },
            "label": "",
            "notes": "",
        })
    return sheet


def judge_input(sheet: dict, keep_stratum: bool = True) -> dict:
    """The blind sheet a judge reads: the rubric and the two passages only.

    The detector's own output -- its NLI probability, its topical
    similarity, its numeric-conflict list, whether the pair was flagged --
    is *not* here. The stratum is kept because the annotator records it for
    the scorer; it is not sent to the judge. Pass ``keep_stratum=False`` for
    a judge that reads the file directly rather than through the API, so
    that its blindness is structural rather than a promise.
    """
    pairs = []
    for p in sheet["pairs"]:
        pair = {
            "pair_id": p["pair_id"],
            "passage_a": p["text_a"],
            "passage_b": p["text_b"],
        }
        if keep_stratum:
            pair["stratum"] = p["stratum"]
        pairs.append(pair)
    return {
        "schema": "mtp.contradiction-judge-input/1",
        "instructions": sheet["instructions"],
        "rubric": sheet["rubric"],
        "labels_allowed": sheet["labels_allowed"],
        "pairs": pairs,
    }


def _wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """A Wilson score interval for a binomial proportion."""
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = (z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))) / d
    return (max(0.0, centre - half), min(1.0, centre + half))


def load_annotator(path: Path) -> dict:
    """Read one annotator's labels.

    The file is the JSON a labelling run writes: an `annotator` name, the
    `model` that produced the labels if it was a model, and a `labels` map
    from pair id to label.
    """
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    labels = {str(k): v for k, v in (data.get("labels") or {}).items()}
    return {
        "name": data.get("annotator") or Path(path).stem,
        "model": data.get("model"),
        "kind": "model" if data.get("model") else "human",
        "labels": labels,
    }


def cohen_kappa(a: list[str], b: list[str]) -> float | None:
    """Cohen's kappa for two raters over the same items.

    Chance agreement is corrected for, because with five categories and
    skewed marginals the raw agreement rate is inflated: most pairs are
    ``no_conflict`` for both annotators for the uninteresting reason that
    most pairs really are.
    """
    n = len(a)
    if n == 0:
        return None
    observed = sum(1 for x, y in zip(a, b) if x == y) / n
    ca, cb = {}, {}
    for x in a:
        ca[x] = ca.get(x, 0) + 1
    for y in b:
        cb[y] = cb.get(y, 0) + 1
    expected = sum((ca.get(lbl, 0) / n) * (cb.get(lbl, 0) / n)
                   for lbl in set(ca) | set(cb))
    if expected >= 1.0:
        return None
    return (observed - expected) / (1 - expected)


def _counts(labels) -> dict[str, int]:
    """Label counts, for the label itself rather than for a pair id."""
    out: dict[str, int] = {}
    for lab in labels:
        out[lab] = out.get(lab, 0) + 1
    return out


def _annotator_metrics(sheet: dict, labels: dict[str, str]) -> dict:
    """One annotator's precision, recall estimate and stratum breakdown."""
    pairs = sheet.get("pairs") or []
    strata = {str(p["pair_id"]): p["stratum"] for p in pairs}
    alarms = [(pid, lab) for pid, lab in labels.items()
              if strata.get(pid, "").endswith("_alarm")]
    unflagged = [(pid, lab) for pid, lab in labels.items()
                  if strata.get(pid) == "unflagged_random"]

    tp = sum(1 for _pid, lab in alarms if lab == TRUE_LABEL)
    n_alarms = len(alarms)
    prec = tp / n_alarms if n_alarms else None
    ci = _wilson(tp, n_alarms) if n_alarms else None

    missed = sum(1 for _pid, lab in unflagged if lab == TRUE_LABEL)
    n_unflagged_pop = (sheet.get("populations") or {}).get("n_unflagged", 0)
    n_sample = len(unflagged)
    if n_sample and n_unflagged_pop:
        est_missed = missed * (n_unflagged_pop / n_sample)
    else:
        est_missed = None

    if est_missed is None or not tp:
        recall = recall_ci = est_total = None
    else:
        est_total = tp + est_missed
        recall = tp / est_total if est_total else None
        lo_p, hi_p = _wilson(missed, n_sample) if n_sample else (0.0, 1.0)
        lo_total = tp + lo_p * n_unflagged_pop
        hi_total = tp + hi_p * n_unflagged_pop
        recall_ci = (tp / hi_total if hi_total else None,
                     tp / lo_total if lo_total else None)

    by_stratum: dict[str, dict] = {}
    distribution: dict[str, int] = {}
    for pid, lab in labels.items():
        st = strata.get(pid, "unknown")
        b = by_stratum.setdefault(st, {"n": 0, "n_true": 0})
        b["n"] += 1
        if lab == TRUE_LABEL:
            b["n_true"] += 1
        distribution[lab] = distribution.get(lab, 0) + 1

    return {
        "n_labelled": len(labels),
        "n_alarms_labelled": n_alarms,
        "n_alarms_true": tp,
        "precision": prec,
        "precision_ci95": list(ci) if ci else None,
        "recall_estimate": recall,
        "recall_ci95": list(recall_ci) if recall_ci else None,
        "n_unflagged_sampled": n_sample,
        "n_missed_true_in_sample": missed,
        "unflagged_population": n_unflagged_pop,
        "sampling_scale": (n_unflagged_pop / n_sample) if n_sample and n_unflagged_pop else None,
        "estimated_total_true_contradictions": est_total,
        "by_stratum": by_stratum,
        "label_distribution": distribution,
        # The labels *within the alarms*, which is the diagnosis: a reader
        # that says "different subjects" about an alarm is naming a failure
        # of the subject check, and a reader that says "no conflict" about an
        # alarm is naming a failure of the NLI model. Both are actionable;
        # "not a contradiction" on its own is not.
        "label_distribution_alarms": _counts(lab for _pid, lab in alarms),
        "label_distribution_unflagged": _counts(lab for _pid, lab in unflagged),
    }


#: The label each branch's alarms *should* carry if the branch is right.
#: The semantic branch claims a contradiction; the revision branch claims a
#: supersession -- one passage describing a later revision of the other --
#: which the rubric has as its own label; the quantity branch claims a
#: contradiction about one measured quantity.
BRANCH_EXPECTED_LABELS = {
    "semantic": {TRUE_LABEL},
    "quantity": {TRUE_LABEL},
    "revision": {"supersession", TRUE_LABEL},
}


def branch_metrics(sheet: dict, labels: dict[str, str]) -> dict:
    """One annotator's accuracy, per branch of the gate.

    The gate has three branches and each is judged against the label that
    branch is claiming. A semantic alarm is right when the reader calls it a
    contradiction; a revision alarm is right when the reader calls it a
    supersession -- one passage describing a later revision of the other --
    because that is what the branch claims and it is a conflict of the right
    kind for a practitioner to be told about.
    """
    kinds = {str(p["pair_id"]): ((p.get("detector") or {}).get("kind")
                                 or "semantic")
             for p in (sheet.get("pairs") or [])}
    flagged = {str(p["pair_id"]): bool((p.get("detector") or {}).get("flagged"))
               for p in (sheet.get("pairs") or [])}
    out: dict[str, dict] = {}
    for pid, lab in labels.items():
        # Only the branch's *alarms* are counted. A pair the gate did not
        # flag is not evidence about a branch, whatever the branch would
        # have said about it.
        if not flagged.get(pid):
            continue
        kind = kinds.get(pid, "semantic")
        b = out.setdefault(kind, {"n": 0, "n_acceptable": 0,
                                  "n_true_contradiction": 0})
        b["n"] += 1
        if lab in BRANCH_EXPECTED_LABELS.get(kind, {TRUE_LABEL}):
            b["n_acceptable"] += 1
        if lab == TRUE_LABEL:
            b["n_true_contradiction"] += 1
    for b in out.values():
        b["acceptable_rate"] = (b["n_acceptable"] / b["n"]) if b["n"] else None
        b["true_contradiction_rate"] = (
            (b["n_true_contradiction"] / b["n"]) if b["n"] else None)
    return out


def write_calibration(sheet: dict, annotators: list[dict], path: Path,
                      min_precision: float = 0.5) -> dict:
    """Fit the conflict calibration that governs what is surfaced.

    Each branch's measured precision is the share of its alarms the readers
    accept as the kind of conflict that branch claims. A branch whose
    measured precision is below the floor has its findings recorded and
    withheld; a branch that was never measured is surfaced, because the
    absence of a measurement is not a measurement.

    The file is written beside the gate's fitted model, in the variant's
    artefact directory, and is read by the pipeline at inference time.
    """
    per_branch: dict[str, dict] = {}
    for a in annotators:
        for kind, b in branch_metrics(sheet, a["labels"]).items():
            acc = per_branch.setdefault(
                kind, {"n": 0, "n_acceptable": 0, "annotators": []})
            acc["n"] += b["n"]
            acc["n_acceptable"] += b["n_acceptable"]
            acc["annotators"].append({"name": a["name"],
                                      "n": b["n"],
                                      "n_acceptable": b["n_acceptable"]})
    precision, n_measured = {}, {}
    for kind, acc in per_branch.items():
        if not acc["n"]:
            continue
        precision[kind] = acc["n_acceptable"] / acc["n"]
        n_measured[kind] = acc["n"]
    payload = {
        "schema": "mtp.conflict-calibration/1",
        "min_precision": min_precision,
        "precision": precision,
        "n_measured": n_measured,
        "by_annotator": {
            a["name"]: branch_metrics(sheet, a["labels"]) for a in annotators
        },
        "note": (
            "The measured precision of each branch of the contradiction gate, "
            "from the reader labelling (Experiment 11). The pipeline reads "
            "this file and withholds the findings of any branch whose "
            "measured precision is below 'min_precision'. A branch that "
            "does not appear in 'precision' has not been measured and is "
            "surfaced: the absence of a measurement is not a measurement."),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def score_multi(sheet: dict, annotators: list[dict],
                control_sheet: dict | None = None,
                control_labels: list[dict] | None = None) -> dict:
    """Score a sheet labelled by two or more independent annotators.

    Each annotator gets its own precision and recall estimate. The
    agreement between them is reported separately, because a precision
    measured by one annotator is a statement about that annotator as much as
    about the detector, and the agreement is what says whether the labels
    are a property of the pairs.

    The headline precision is a **band**, not a point. A pair counts as a
    true contradiction only if the annotators agree it is one; a pair they
    disagree about is counted as a false alarm at the lower end of the band
    and as a true contradiction at the upper end. The band is the honest
    summary when there is no third adjudicator, and it collapses when the
    annotators agree about which pairs are contradictions.
    """
    out: dict = {
        "status": "run",
        "n_annotators": len(annotators),
        "annotators": {},
    }
    for a in annotators:
        m = _annotator_metrics(sheet, a["labels"])
        m["kind"] = a["kind"]
        m["model"] = a["model"]
        m["by_branch"] = branch_metrics(sheet, a["labels"])
        out["annotators"][a["name"]] = m

    names = [a["name"] for a in annotators]
    pairs = sheet.get("pairs") or []
    strata = {str(p["pair_id"]): p["stratum"] for p in pairs}

    # The per-branch aggregate: each branch of the gate, with the share of
    # its alarms the readers accept as the kind of conflict that branch
    # claims. This is what the pipeline's surfacing decision is fitted on.
    agg: dict[str, dict] = {}
    for a in annotators:
        for kind, b in branch_metrics(sheet, a["labels"]).items():
            e = agg.setdefault(kind, {"n": 0, "n_acceptable": 0,
                                      "n_true_contradiction": 0})
            e["n"] += b["n"]
            e["n_acceptable"] += b["n_acceptable"]
            e["n_true_contradiction"] += b["n_true_contradiction"]
    for e in agg.values():
        e["acceptable_rate"] = (e["n_acceptable"] / e["n"]) if e["n"] else None
        e["true_contradiction_rate"] = (
            (e["n_true_contradiction"] / e["n"]) if e["n"] else None)
    out["by_branch"] = agg

    # The agreement block, over every pair both annotators labelled.
    if len(annotators) >= 2:
        a, b = annotators[0], annotators[1]
        common = sorted(set(a["labels"]) & set(b["labels"]))
        la = [a["labels"][p] for p in common]
        lb = [b["labels"][p] for p in common]
        two_a = [TRUE_LABEL if x == TRUE_LABEL else "other" for x in la]
        two_b = [TRUE_LABEL if y == TRUE_LABEL else "other" for y in lb]
        alarms_common = [p for p in common
                         if strata.get(p, "").endswith("_alarm")]
        agree_true = sum(1 for p in alarms_common
                         if a["labels"][p] == TRUE_LABEL
                         and b["labels"][p] == TRUE_LABEL)
        n_alarms_common = len(alarms_common)
        lower = agree_true / n_alarms_common if n_alarms_common else None
        upper = ((sum(1 for p in alarms_common
                      if TRUE_LABEL in (a["labels"][p], b["labels"][p])))
                 / n_alarms_common) if n_alarms_common else None
        out["agreement"] = {
            "n_compared": len(common),
            "raw_agreement_5way": (sum(1 for x, y in zip(la, lb) if x == y)
                                    / len(common)) if common else None,
            "cohen_kappa_5way": cohen_kappa(la, lb),
            "raw_agreement_2way": (sum(1 for x, y in zip(two_a, two_b)
                                        if x == y) / len(common))
                                   if common else None,
            "cohen_kappa_2way": cohen_kappa(two_a, two_b),
            "n_disagreements_2way": sum(1 for x, y in zip(two_a, two_b) if x != y),
            "disagreeing_pair_ids": [p for p, x, y in zip(common, two_a, two_b)
                                     if x != y],
            "n_alarms_compared": n_alarms_common,
            "precision_band_lower": lower,
            "precision_band_upper": upper,
            "precision_band_lower_ci95": (list(_wilson(agree_true, n_alarms_common))
                                          if n_alarms_common else None),
            "precision_band_upper_ci95": (
                list(_wilson(sum(1 for p in alarms_common
                                  if TRUE_LABEL in (a["labels"][p],
                                                     b["labels"][p])),
                             n_alarms_common)) if n_alarms_common else None),
        }

    # The positive control: the pairs the numeric branch called verifiable.
    # If the annotators do not call those contradictions, the annotators and
    # the detector disagree about what a verifiable conflict is, and the
    # precision number has to be read with that in mind.
    nc_ids = []
    for p in pairs:
        det = p.get("detector") or {}
        if det.get("numeric_conflicts"):
            nc_ids.append(str(p["pair_id"]))
    if nc_ids:
        control = {}
        for a in annotators:
            lab = [a["labels"][p] for p in nc_ids if p in a["labels"]]
            control[a["name"]] = {
                "n": len(lab),
                "n_labelled_contradiction": sum(1 for x in lab if x == TRUE_LABEL),
                "distribution": {k: lab.count(k) for k in set(lab)},
            }
        out["verifiable_subset_control"] = {
            "n_numeric_conflict_pairs_in_sheet": len(nc_ids),
            "pair_ids": nc_ids,
            "by_annotator": control,
        }

    # The positive control: a set of pairs whose correct labels are known
    # in advance, with no corpus origin, so a judge that labelled everything
    # `no_conflict` would be caught. Its score is what licenses reading the
    # precision number as a statement about the detector rather than about
    # the annotators' habits.
    if control_sheet:
        expected = {str(p["pair_id"]): p.get("expected")
                    for p in (control_sheet.get("pairs") or [])}
        by_annotator = {}
        for a, c_labels in zip(annotators, control_labels):
            scored = [(pid, lab, expected.get(pid))
                      for pid, lab in c_labels.items() if pid in expected]
            correct = [(pid, lab, exp) for pid, lab, exp in scored if lab == exp]
            by_annotator[a["name"]] = {
                "n": len(scored),
                "n_correct": len(correct),
                "n_correct_contradiction": sum(
                    1 for _p, _l, exp in scored
                    if exp == TRUE_LABEL and _l == TRUE_LABEL),
                "n_expected_contradiction": sum(
                    1 for _p, _l, exp in scored if exp == TRUE_LABEL),
                "misses": [{"pair_id": pid, "expected": exp, "got": lab}
                           for pid, lab, exp in scored if lab != exp],
            }
        out["positive_control"] = {
            "n_pairs": len(expected),
            "by_annotator": by_annotator,
            "note": (
                "The control pairs are synthetic and have known labels, so "
                "their score measures the annotator rather than the "
                "detector. A judge that scores badly here cannot support any "
                "claim about the corpus."),
        }

    out["note"] = (
        "Precision is computed on the labelled alarms; recall is an estimate "
        "from a simple random sample of the unflagged pairs scaled to the "
        "unflagged population, with the enriched near-miss stratum excluded. "
        "Where two annotators are recorded, each is scored separately, their "
        "agreement is reported, and the headline precision is a band whose "
        "lower end counts a disagreement between annotators as a false alarm "
        "and whose upper end counts it as a true contradiction."
    )
    return out


def score(sheet: dict) -> dict:
    """Turn a filled sheet into a precision and a recall, with intervals."""
    pairs = sheet.get("pairs") or []
    labelled = [p for p in pairs if p.get("label")]
    unlabelled = [p for p in pairs if not p.get("label")]
    bad = sorted({p["label"] for p in labelled} - set(LABELS))

    alarms = [p for p in labelled if p["stratum"].endswith("_alarm")]
    unflagged = [p for p in labelled if p["stratum"] == "unflagged_random"]

    tp = sum(1 for p in alarms if p["label"] == TRUE_LABEL)
    n_alarms = len(alarms)
    prec = tp / n_alarms if n_alarms else None
    prec_ci = _wilson(tp, n_alarms) if n_alarms else None

    # The recall estimate: scale the true contradictions found among the
    # unflagged sample up to the size of the unflagged population, and add
    # the ones the gate did catch. The near-miss stratum is excluded on
    # purpose -- it is enriched by construction.
    missed_in_sample = sum(1 for p in unflagged if p["label"] == TRUE_LABEL)
    n_unflagged = (sheet.get("populations") or {}).get("n_unflagged", 0)
    n_sample = len(unflagged)
    if n_sample and n_unflagged:
        scale = n_unflagged / n_sample
        est_missed = missed_in_sample * scale
    else:
        scale = None
        est_missed = None

    if est_missed is None or not tp:
        recall = None
        recall_ci = None
        est_total = None
    else:
        est_total = tp + est_missed
        recall = tp / est_total if est_total else None
        # A conservative interval: the sample's own proportion at both ends.
        lo_p, hi_p = _wilson(missed_in_sample, n_sample) if n_sample else (0.0, 1.0)
        lo_total = tp + lo_p * n_unflagged
        hi_total = tp + hi_p * n_unflagged
        recall_ci = (tp / hi_total if hi_total else None,
                     tp / lo_total if lo_total else None)

    by_stratum: dict[str, dict] = {}
    for p in labelled:
        b = by_stratum.setdefault(p["stratum"], {"n": 0, "n_true": 0})
        b["n"] += 1
        if p["label"] == TRUE_LABEL:
            b["n_true"] += 1

    return {
        "status": "run",
        "n_labelled": len(labelled),
        "n_unlabelled": len(unlabelled),
        "unrecognised_labels": bad,
        "precision": prec,
        "precision_ci95": list(prec_ci) if prec_ci else None,
        "n_alarms_labelled": n_alarms,
        "n_alarms_true": tp,
        "recall_estimate": recall,
        "recall_ci95": list(recall_ci) if recall_ci else None,
        "n_unflagged_sampled": n_sample,
        "n_missed_true_in_sample": missed_in_sample,
        "unflagged_population": n_unflagged,
        "sampling_scale": scale,
        "estimated_total_true_contradictions": est_total,
        "by_stratum": by_stratum,
        "note": (
            "Precision is computed on the labelled alarms. Recall is an "
            "estimate: the true contradictions found among a simple random "
            "sample of the unflagged pairs are scaled up by the size of the "
            "unflagged population, and the near-miss stratum is excluded from "
            "the scale because it is enriched by construction. The labels are "
            "author labels unless a second annotator is recorded in the "
            "sheet, and are therefore not independent annotation."),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sample", action="store_true",
                    help="write the labelling sheet")
    ap.add_argument("--score", action="store_true",
                    help="score a filled sheet")
    ap.add_argument("--seed", type=int, default=20261118)
    ap.add_argument("--sheet", default=str(RESULTS_DIR / SHEET_NAME))
    ap.add_argument("--judge", action="append", default=[],
                    metavar="FILE",
                    help="an annotator's label file; repeat for each "
                         "annotator. With two or more, the scorer reports "
                         "each annotator separately plus their agreement.")
    ap.add_argument("--judge-input", metavar="FILE",
                    help="write a blind judge sheet (rubric and the two "
                         "passages only) for the model annotator")
    ap.add_argument("--no-stratum", action="store_true",
                    help="omit the stratum from the judge sheet, for a judge "
                         "that reads the file rather than calling the API")
    ap.add_argument("--control", metavar="FILE",
                    help="the positive-control sheet, whose pairs have known "
                         "labels, so the annotators can be scored on it")
    ap.add_argument("--control-labels", action="append", default=[],
                    metavar="FILE",
                    help="an annotator's labels for the control set; repeat "
                         "once per annotator, in the same order as --judge")
    ap.add_argument("--calibration", metavar="FILE",
                    help="write the fitted conflict calibration here. It "
                         "records each branch's measured precision, and the "
                         "pipeline withholds the findings of any branch below "
                         "the floor.")
    ap.add_argument("--min-precision", type=float, default=0.5,
                    help="the precision a branch must reach to be surfaced "
                         "(default: 0.5)")
    args = ap.parse_args()

    sheet_path = Path(args.sheet)
    if args.sample:
        pairs = load_pairs()
        sheet = sample(pairs, args.seed)
        sheet_path.write_text(json.dumps(sheet, indent=2, default=str),
                              encoding="utf-8")
        print(f"[labels] wrote {sheet_path} with {len(sheet['pairs'])} pairs "
              f"to label")
        print(f"[labels] populations: {sheet['populations']}")
        print(f"[labels] sampled: {sheet['sampling']}")
        return 0

    if args.judge_input:
        if not sheet_path.exists():
            print(f"[labels] no sheet at {sheet_path}; run --sample first")
            return 2
        sheet = json.loads(sheet_path.read_text(encoding="utf-8"))
        out = Path(args.judge_input)
        out.write_text(
            json.dumps(judge_input(sheet, keep_stratum=not args.no_stratum),
                       indent=2),
            encoding="utf-8")
        print(f"[labels] wrote blind judge sheet {out} "
              f"({len(sheet['pairs'])} pairs)")
        return 0

    if args.score:
        if not sheet_path.exists():
            print(f"[labels] no sheet at {sheet_path}; run --sample first")
            return 2
        sheet = json.loads(sheet_path.read_text(encoding="utf-8"))
        if args.judge:
            annotators = [load_annotator(Path(p)) for p in args.judge]
            control_sheet = None
            control_labels = None
            if args.control:
                control_sheet = json.loads(
                    Path(args.control).read_text(encoding="utf-8"))
                control_labels = []
                for p in args.control_labels:
                    control_labels.append(
                        load_annotator(Path(p))["labels"])
                if len(control_labels) != len(annotators):
                    print("[labels] --control-labels must be given once per "
                          "--judge, in the same order")
                    return 2
            result = score_multi(sheet, annotators, control_sheet,
                                 control_labels)
        else:
            result = score(sheet)
        out = RESULTS_DIR / "exp11_contradiction_precision.json"
        out.write_text(json.dumps(result, indent=2, default=str),
                       encoding="utf-8")
        print(f"[labels] wrote {out}")
        if args.judge:
            for name, m in result["annotators"].items():
                print(f"   [{name}] precision {m['precision']} "
                      f"(CI {m['precision_ci95']}), "
                      f"{m['n_alarms_true']}/{m['n_alarms_labelled']} alarms "
                      f"true, recall estimate {m['recall_estimate']}")
            ag = result.get("agreement") or {}
            print(f"   agreement: raw 2-way {ag.get('raw_agreement_2way')}, "
                  f"kappa 2-way {ag.get('cohen_kappa_2way')}, "
                  f"kappa 5-way {ag.get('cohen_kappa_5way')}, "
                  f"{ag.get('n_disagreements_2way')} disagreement(s)")
            print(f"   precision band: [{ag.get('precision_band_lower')}, "
                  f"{ag.get('precision_band_upper')}]")
            ctrl = result.get("verifiable_subset_control") or {}
            for name, c in (ctrl.get("by_annotator") or {}).items():
                print(f"   verifiable-subset control [{name}]: "
                      f"{c['n_labelled_contradiction']}/{c['n']} of the "
                      f"numeric-conflict pairs called contradictions")
            pc = result.get("positive_control") or {}
            for name, c in (pc.get("by_annotator") or {}).items():
                print(f"   positive control [{name}]: "
                      f"{c['n_correct']}/{c['n']} correct")
            if args.calibration:
                cal = write_calibration(sheet, annotators,
                                        Path(args.calibration),
                                        min_precision=args.min_precision)
                print(f"   calibration: {cal['precision']} "
                      f"(n measured: {cal['n_measured']}) -> "
                      f"{args.calibration}")
                for name, m in result["annotators"].items():
                    for kind, b in (m.get("by_branch") or {}).items():
                        print(f"     [{name}] {kind}: {b['n_acceptable']}/{b['n']} "
                              f"alarms accepted as the kind that branch claims")
            return 0
        for k in ("n_labelled", "n_unlabelled", "n_alarms_labelled",
                  "n_alarms_true", "precision", "precision_ci95",
                  "recall_estimate", "recall_ci95"):
            print(f"   {k}: {result.get(k)}")
        if result["unrecognised_labels"]:
            print(f"   !! unrecognised labels: {result['unrecognised_labels']}")
        return 0

    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
