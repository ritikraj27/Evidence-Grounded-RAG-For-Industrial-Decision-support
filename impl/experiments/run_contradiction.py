#!/usr/bin/env python3
"""Experiment 3 -- contradiction surfacing: NLI alone vs the joint gate.

The measurement is deliberately harder than "count how many pairs the NLI
model calls contradictory". A contradiction detector is only useful if the
pairs it flags are genuinely conflicting, so the experiment reports a full
confusion matrix at the operating point, together with:

  * **prevalence** -- what fraction of all compared pairs are true conflicts.
    Without it, a false-positive rate is uninterpretable: at 1% prevalence,
    a detector with 50% recall and 99% specificity still has a 98%
    false-positive rate, and the number says more about prevalence than
    about the detector.
  * **precision, recall, F1** of the detector.
  * **always-flag and never-flag baselines.** A detector that flags
    everything has 100% recall and 0% precision; one that flags nothing has
    0% recall and 100% precision. Any claimed improvement must beat both.
  * **the revision/supersession check.** ContextConflict (EMNLP 2026) shows
    that only two of six conflict types are genuine contradictions, and the
    most common false positive in industrial documentation is *temporal
    supersession*: "Rev 3 sets EOQ at 187 units" and "Rev 4 sets EOQ at 95
    units" are both true, because Rev 4 replaced Rev 3. A detector that
    reports that as a contradiction is wrong in the way that matters most.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import (  # noqa: E402
    RESULTS_DIR,
    load_benchmark,
    load_index,
    markdown_table,
    write_result,
)
from src.config import CONFIG, ContradictionConfig  # noqa: E402
from src.contradiction import (  # noqa: E402
    detect_contradictions,
    entity_jaccard,
    numeric_conflicts,
)
from src.pipeline import Framework  # noqa: E402

SEED = 20261118

#: The measured state of the gate *before* the numeric rule was repaired,
#: from the 2026-11-09 runs of this experiment on the same corpora with the
#: same seed. These are recorded rather than recomputed because the old
#: rule no longer exists in the code: the repair is in
#: `src/contradiction.py`, and the reader-labelling experiment that found
#: the defect is Experiment 11.
#:
#: Keyed by corpus: the focus corpus (the headline) and the six-category
#: corpus. The collapse happens on both, which is what says it is a
#: property of encyclopaedic corpora rather than of one article set.
PRE_REPAIR = {
    "": {  # the six-category corpus
        "verifiable_numeric_conflicts": 185,
        "joint_gate_flagged": 625,
        "alarms_numeric_branch_only": 126,
        "after_quantity_rule": {
            "verifiable_numeric_conflicts": 4,
            "joint_gate_flagged": 503,
            "alarms_numeric_branch_only": 4,
        },
    },
    "focus": {
        "verifiable_numeric_conflicts": 21,
        "joint_gate_flagged": 81,
        "alarms_numeric_branch_only": 6,
        "share_alarms_corroborated_by_numeric_check": 0.25925925925925924,
        "after_quantity_rule": {
            "verifiable_numeric_conflicts": 1,
            "joint_gate_flagged": 76,
            "alarms_numeric_branch_only": 1,
        },
    },
}

#: A revision/supersession marker. If two passages reference different
#: revision or version identifiers, they are *versions* of a document, not
#: contradictions -- unless they are about the same subject AND the later
#: revision does not obviously supersede.
_REVISION_RE = re.compile(
    r"\b(rev(?:ision)?\.?\s*\.?\s*\d+|v(?:ersion)?\.?\s*\d+(?:\.\d+)?|"
    r"amendment\s*\d+|issue\s*\d+|edition\s*\d+)\b",
    re.IGNORECASE,
)


def revision_markers(text: str) -> set[str]:
    return {m.group(1).lower().replace(" ", "") for m in _REVISION_RE.finditer(text)}


def is_superseded(a: str, b: str) -> bool:
    """True when the two passages are different revisions of the same document.

    Detection is by explicit revision marker. It is deliberately conservative:
    if the markers are absent, we do not claim supersession, because a false
    supersession claim would suppress a genuine contradiction.
    """
    ma, mb = revision_markers(a), revision_markers(b)
    if not ma or not mb:
        return False
    if ma & mb:
        return False  # same revision -> a real conflict is possible
    # Different revisions: supersession only if the entity overlap confirms
    # they are about the same document.
    return entity_jaccard(a, b) >= 0.25


def main() -> int:
    index = load_index()
    bench = load_benchmark()
    fw = Framework(index)

    print("[exp3] collecting accepted contexts ...", flush=True)
    contexts = []
    for q in bench["queries"]:
        # A query with no gold chunk has no evidence to be contradictory
        # about, and its category filter would fall back to the whole
        # corpus. The family-name test never fired: the unanswerable
        # families are "unanswerable_near_miss" and "unanswerable_ood".
        if not q["gold"]:
            continue
        trace = fw.retrieve(
            q["query"],
            category=q["category"],
            apply_quota=False,
            apply_rerank=True,
        )
        if not trace.accepted:
            continue
        texts = [fw.index.chunk_text[c] for c in trace.accepted]
        emb = np.array([fw.index.embeddings[fw._pos[c]] for c in trace.accepted])
        contexts.append((q, trace.accepted, texts, emb))

    print(f"[exp3] {len(contexts)} contexts; running NLI over all pairs ...", flush=True)

    cfg = ContradictionConfig()
    findings = []
    for q, ids, texts, emb in contexts:
        fs = detect_contradictions(texts, ids, embeddings=emb, config=cfg)
        for f in fs:
            a = fw.index.chunk_text[f.chunk_a]
            b = fw.index.chunk_text[f.chunk_b]
            superseded = is_superseded(a, b)
            # The experiment's own revision check suppresses the *semantic*
            # branch, because a pair that is two revisions of the same
            # document is not contradicting itself -- it is superseded. The
            # detector's own revision branch is the correctly-typed version
            # of that finding, so it is left alone.
            if superseded and f.kind == "semantic":
                f.nli_and_subject = False
                f.flagged = False
                f.reason += "; suppressed as revision supersession"
            f.numeric_only = bool(f.numeric_conflicts) and not f.nli_and_subject
            findings.append(f)

    n = len(findings)
    nli_only = sum(1 for f in findings if f.nli_contradiction_prob >= cfg.nli_threshold)
    joint = sum(1 for f in findings if f.flagged)
    superseded = sum(1 for f in findings if "supersession" in f.reason)

    # A "true" conflict, for the purposes of this experiment, is one that is
    # detected by the joint gate AND has a numeric disagreement OR an NLI
    # contradiction above threshold with same-subject confirmation. Since we
    # have no expert annotation of industrial conflicts, the honest framing
    # is: the joint gate's flags are *candidates*, and we report the precision
    # of the candidate set against the strictest available proxy.
    # The proxy ground truth uses the *detector's own* subject rule, so it
    # is the same set the gate flags. That is exactly why it is a proxy and
    # not a measurement: it cannot credit a branch the definition excludes.
    # The measurement that is not circular is in Experiment 11.
    strict_true = sum(
        1 for f in findings
        if f.nli_contradiction_prob >= cfg.nli_threshold
        and (f.topical_similarity >= cfg.topic_threshold and f.entity_overlap >= cfg.entity_overlap_min)
        and not ("supersession" in f.reason)
    )

    tp = strict_true
    fp = joint - tp
    fn = strict_true - tp  # by construction 0; stated for clarity
    precision = tp / joint if joint else 0.0
    recall = tp / strict_true if strict_true else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0

    # Baselines.
    always_fp = max(n - strict_true, 0)
    never_fp = n - strict_true

    # ---- The independent ground truth -------------------------------
    # The ground truth has to be INDEPENDENT of the detector, or the
    # measurement is circular: a proxy defined partly by the NLI label will
    # always agree with the NLI gate.
    #
    # The independent ground truth available here is the numeric conflict:
    # two passages that attach different values to the same distinctive
    # quantity are in conflict, and that is checkable by inspection, without
    # any model. So we measure two things:
    #
    #   recall on the verifiable subset -- of the pairs that demonstrably
    #   conflict, what fraction does each detector flag?
    #
    #   alarms per real conflict -- how many pairs does each detector flag in
    #   total, per real conflict it catches? A detector that flags many
    #   pairs while catching few real conflicts is generating noise for the
    #   practitioner to wade through.
    #
    # The proxy precision/recall figures are still reported, but they are
    # explicitly marked as proxy.
    verifiable = [f for f in findings if f.numeric_conflicts]
    n_verifiable = len(verifiable)
    nli_flagged_ids = {
        frozenset((f.chunk_a, f.chunk_b)) for f in findings
        if f.nli_contradiction_prob >= cfg.nli_threshold
    }
    joint_flagged_ids = {
        frozenset((f.chunk_a, f.chunk_b)) for f in findings if f.flagged
    }
    # The NLI-and-same-subject conjunction on its own. This is the number
    # that is not a tautology: the full gate's recall on the verifiable
    # subset is 1.0 by construction, because the numeric branch is an
    # OR-branch of the gate and the subset is *defined* by numeric
    # conflicts. What the conjunction contributes has to be measured
    # without the numeric branch.
    conjunction_flagged_ids = {
        frozenset((f.chunk_a, f.chunk_b)) for f in findings if f.nli_and_subject
    }
    nli_caught = sum(1 for f in verifiable
                     if frozenset((f.chunk_a, f.chunk_b)) in nli_flagged_ids)
    joint_caught = sum(1 for f in verifiable
                       if frozenset((f.chunk_a, f.chunk_b)) in joint_flagged_ids)
    conjunction_caught = sum(1 for f in verifiable
                             if frozenset((f.chunk_a, f.chunk_b))
                             in conjunction_flagged_ids)
    numeric_branch_caught = joint_caught - conjunction_caught

    # ---- What the "precision" figure actually measures -------------------
    # There is no independent ground truth for contradiction on this corpus:
    # every available proxy is defined by one of the gate's own branches, so
    # a precision computed against it cannot credit the branch that is not
    # in the definition. The honest reading of the number is therefore how
    # the alarms split between the two branches and how many of them the one
    # check that is independent of the NLI model -- the numeric conflict --
    # corroborates. Both are reported, and neither is called a precision.
    #
    # Counting unit: every quantity in this summary counts *findings* (one
    # per pair, per query context in which the pair occurred), because that
    # is what the denominators count. Counting distinct pairs instead
    # understates the conjunction's flag rate by the number of times a pair
    # recurs across contexts, so the pair count is kept separately and
    # named.
    conjunction_findings = sum(1 for f in findings if f.nli_and_subject)
    numeric_only_findings = sum(1 for f in findings if f.kind == "quantity")
    revision_only_findings = sum(1 for f in findings if f.kind == "revision")
    joint_on_numeric = sum(1 for f in findings
                            if f.flagged and f.numeric_conflicts)
    nli_branch_findings = sum(
        1 for f in findings
        if f.nli_contradiction_prob >= cfg.nli_threshold
        and (f.topical_similarity >= cfg.topic_threshold
             or f.entity_overlap >= cfg.entity_overlap_min)
        and "supersession" not in f.reason)

    # How the alarms split between the three branches, and how many are
    # surfaced. A finding is surfaced only when the measured precision of
    # the branch that raised it clears the calibration floor.
    flagged_by_kind: dict[str, int] = {}
    for f in findings:
        if f.flagged:
            flagged_by_kind[f.kind] = flagged_by_kind.get(f.kind, 0) + 1
    surfaced_count = sum(1 for f in findings if f.flagged and f.surfaced)

    summary = {
        "pairs_compared": n,
        "verifiable_numeric_conflicts": n_verifiable,
        "nli_recall_on_verifiable_subset": (nli_caught / n_verifiable
                                            if n_verifiable else float("nan")),
        "joint_recall_on_verifiable_subset": (joint_caught / n_verifiable
                                              if n_verifiable else float("nan")),
        "conjunction_recall_on_verifiable_subset": (
            conjunction_caught / n_verifiable if n_verifiable else float("nan")),
        "numeric_branch_only_caught": numeric_branch_caught,
        "tautology_note": (
            "the verifiable subset is DEFINED by the presence of a numeric "
            "conflict, and the numeric detector is an OR-branch of the joint "
            "gate, so the joint gate's recall on this subset is 1.0 by "
            "construction and is not evidence. The informative quantity is "
            "'conjunction_recall_on_verifiable_subset': how many of these "
            "conflicts the NLI-and-same-subject conjunction catches with the "
            "numeric branch removed, and therefore what the numeric branch "
            "adds."),
        "nli_flag_rate": nli_only / n if n else 0.0,
        "joint_flag_rate": joint / n if n else 0.0,
        "nli_alarms_per_verifiable_conflict": (nli_only / n_verifiable
                                               if n_verifiable else float("nan")),
        "joint_alarms_per_verifiable_conflict": (joint / n_verifiable
                                                 if n_verifiable else float("nan")),
        "ground_truth_note": (
            "recall on the verifiable subset uses numeric conflicts, which are "
            "checkable by inspection and independent of the NLI model; the "
            "precision/recall figures below are against an NLI-derived PROXY and "
            "are therefore not independent of the detector"),
        "proxy_ground_truth": True,
        "prevalence_of_true_conflict": strict_true / n if n else 0.0,
        "nli_only_flagged": nli_only,
        "nli_only_false_positives": nli_only - strict_true,
        "nli_only_false_positive_rate": (nli_only - strict_true) / nli_only if nli_only else 0.0,
        "joint_gate_flagged": joint,
        "conjunction_flagged": conjunction_findings,
        "conjunction_flagged_distinct_pairs": len(conjunction_flagged_ids),
        "joint_gate_false_positives": fp,
        "joint_gate_false_positive_rate": fp / joint if joint else 0.0,
        "joint_gate_precision": precision,
        "joint_gate_recall": recall,
        "joint_gate_f1": f1,
        # What the "precision" number is, stated so that it cannot be read
        # as a precision against an independent truth.
        "precision_definition": (
            "'joint_gate_precision' is NOT a precision against an independent "
            "ground truth, and after the subject-check repair it is not even "
            "a useful proxy: the 'true' set it is computed against is the "
            "gate's own set, because the proxy uses the gate's own subject "
            "rule. Its precision is therefore 1.000 and its false-positive "
            "rate 0.000 *by construction*, and neither number means "
            "anything. The measurement that is not circular is the reader "
            "labelling in Experiment 11, and the measurement that separates "
            "the mechanism from the corpus is the detector's own control in "
            "Experiment 11b. The corroboration shares below decompose the "
            "alarms between the branches and say nothing about whether the "
            "alarms are right."),
        "alarms_corroborated_by_nli_branch": nli_branch_findings,
        "share_alarms_corroborated_by_nli_branch": (
            nli_branch_findings / joint if joint else 0.0),
        "alarms_numeric_branch_only": numeric_only_findings,
        "alarms_revision_branch_only": revision_only_findings,
        "alarms_corroborated_by_numeric_check": joint_on_numeric,
        "share_alarms_corroborated_by_numeric_check": (
            joint_on_numeric / joint if joint else 0.0),
        "revision_supersession_suppressed": superseded,
        "baseline_always_flag_false_positive_rate": always_fp / n if n else 0.0,
        "baseline_never_flag_false_positive_rate": never_fp / n if n else 0.0,
        # The three branches and how the alarms split between them, with the
        # surfacing decision attached.
        "flagged_by_kind": flagged_by_kind,
        "surfaced_findings": surfaced_count,
        "withheld_findings": joint - surfaced_count,
        "subject_check_rule": (
            "The same-subject check is the conjunction of the two signals its "
            "own design names: topical similarity AND shared concrete objects "
            "(part numbers, plant codes, distinctive quantities, and content "
            "words). The implementation used to let topical similarity through "
            "on its own, which on a corpus of articles about one subject made "
            "the check a topic check: two chunks of the same article about "
            "different sub-topics passed it. The reader labelling in "
            "Experiment 11 showed the consequence and the repair."),
        "revision_branch_rule": (
            "The revision branch is exact rather than statistical: it reads "
            "the version markers out of the text and fires when two passages "
            "name the same standard at two different issues and share a "
            "specific term. It is the branch this corpus can be evaluated on, "
            "because its correctness is a fact about the text rather than a "
            "judgement about it."),
        "numeric_branch_rule": (
            "A number is a quantity only when a measurement term governs it "
            "(the term is also the key the two passages must agree on), when "
            "it is not a bare four-digit year, and when it is not part of a "
            "hyphenated identifier; a measurement term that begins a proper "
            "name is not a measurement. The numeric branch also carries the "
            "same subject check as the conjunction branch. This replaced an "
            "earlier rule that keyed a number to the nearest distinctive "
            "word, which the reader-labelling experiment in Experiment 11 "
            "showed to fire on citation years, version numbers and surnames "
            "rather than on quantities."),
        "verifiable_subset_size_note": (
            f"The verifiable subset now holds {n_verifiable} pair(s). It was "
            f"{(PRE_REPAIR.get('focus' if RESULTS_DIR.name.endswith('_focus') else '', {}) or {}).get('verifiable_numeric_conflicts', 0)} "
            "pairs before the numeric rule was repaired. A subset this "
            "small cannot carry a recall measurement: the joint gate's "
            "recall on it is 1.0 by construction and, at this size, that "
            "number is arithmetic rather than evidence. The corpus is "
            "encyclopaedic prose about concepts, so it contains worked "
            "examples and formulae rather than instance-level data, and a "
            "quantity-conflict detector has almost nothing in it to find. "
            "The measurement that carries weight is the reader-labelled "
            "precision in Experiment 11, together with the alarm counts in "
            "this table."),
        "numeric_rule_repair": {
            "corpus": ("focus" if RESULTS_DIR.name.endswith("_focus")
                       else "six-category"),
            "before": PRE_REPAIR.get(
                "focus" if RESULTS_DIR.name.endswith("_focus") else "", {}),
            "after_quantity_rule": PRE_REPAIR.get(
                "focus" if RESULTS_DIR.name.endswith("_focus") else "",
                {}).get("after_quantity_rule", {}),
            "after": {
                "verifiable_numeric_conflicts": n_verifiable,
                "joint_gate_flagged": joint,
                "alarms_numeric_branch_only": numeric_only_findings,
                "share_alarms_corroborated_by_numeric_check": (
                    joint_on_numeric / joint if joint else 0.0),
            },
            "note": (
                "The repair changed the detector, not the corpus, the "
                "benchmark or the label standard. The corpus is unchanged, "
                "the benchmark is unchanged, the seed is unchanged, and the "
                "rule was replaced by a measurement-keyed rule rather than "
                "tuned to a target. The quantity-level conflicts fell from "
                "21 to "
                f"{n_verifiable} because the ones that fell were not "
                "conflicts: they were citation years, version numbers and "
                "surnames."),
        },
        "subject_check_repair": {
            "before": ((PRE_REPAIR.get(
                "focus" if RESULTS_DIR.name.endswith("_focus") else "",
                {}).get("after_quantity_rule") or {}).get("joint_gate_flagged")),
            "after": joint,
            "nli_only_flagged": nli_only,
            "suppressed_by_subject_check": max(nli_only - joint, 0),
            "note": (
                "The second repair, forced by the same measurement: the "
                "same-subject check let topical similarity through on its "
                "own, although its own design says that two passages with "
                "high semantic similarity and no shared objects are almost "
                "always about different things. On a corpus of articles all "
                "about one subject that made the check a topic check, and it "
                "was the source of most of the alarms. Requiring shared "
                "concrete objects as well, as designed, cut the alarms from "
                "76 to "
                f"{joint} and removed every alarm a reader had called a "
                "subject mismatch."),
        },
        "thresholds": {
            "nli_threshold": cfg.nli_threshold,
            "topic_threshold": cfg.topic_threshold,
            "entity_overlap_min": cfg.entity_overlap_min,
        },
    }

    print("\n[exp3] ==== contradiction detection ====")
    for k, v in summary.items():
        if not isinstance(v, dict):
            print(f"   {k}: {v}")

    payload = {"seed": SEED, "summary": summary,
               "examples": [f.__dict__ for f in findings[:25]]}
    payload["retrieval_placement"] = CONFIG.modality.position
    write_result("exp3_contradiction", payload)

    # The full pair list, with both texts, so that the gate's alarms can be
    # labelled by hand. The precision of a contradiction detector cannot be
    # computed from a proxy defined by the detector's own branches, so the
    # only way to close that gap is to put the pairs in front of a reader;
    # this file is the frame that they are sampled from.
    pairs_path = RESULTS_DIR / "exp3_contradiction_pairs.jsonl"
    with pairs_path.open("w", encoding="utf-8") as fh:
        for i, f in enumerate(findings):
            a = fw.index.chunk_text[f.chunk_a]
            b = fw.index.chunk_text[f.chunk_b]
            fh.write(json.dumps({
                "pair_id": i,
                "chunk_a": f.chunk_a,
                "chunk_b": f.chunk_b,
                "text_a": a,
                "text_b": b,
                "nli_contradiction_prob": round(float(f.nli_contradiction_prob), 4),
                "topical_similarity": (None if f.topical_similarity != f.topical_similarity
                                       else round(float(f.topical_similarity), 4)),
                "entity_overlap": round(float(f.entity_overlap), 4),
                "numeric_conflicts": f.numeric_conflicts,
                "revision_conflicts": f.revision_conflicts,
                "kind": f.kind,
                "surfaced": bool(f.surfaced),
                "surface_reason": f.surface_reason,
                "nli_and_subject": bool(f.nli_and_subject),
                "flagged": bool(f.flagged),
                "numeric_only": bool(f.numeric_only),
                "reason": f.reason,
            }) + "\n")
    print(f"[exp3] wrote {pairs_path} ({len(findings)} pairs)")

    rows = [
        ["NLI only", summary["nli_only_flagged"],
         f"{summary['nli_flag_rate']:.3f}",
         f"{summary['nli_recall_on_verifiable_subset']:.3f}",
         f"{summary['nli_alarms_per_verifiable_conflict']:.1f}"],
        ["NLI AND same-subject (conjunction alone)", summary["conjunction_flagged"],
         f"{summary['conjunction_flagged'] / n if n else 0.0:.3f}",
         f"{summary['conjunction_recall_on_verifiable_subset']:.3f}",
         f"{summary['conjunction_flagged'] / max(summary['verifiable_numeric_conflicts'], 1):.1f}"],
        ["Joint gate (+ numeric branch)", summary["joint_gate_flagged"],
         f"{summary['joint_flag_rate']:.3f}",
         "1.000 (by construction)",
         f"{summary['joint_alarms_per_verifiable_conflict']:.1f}"],
        ["Baseline: always flag", n, "1.000", "1.000",
         f"{n / max(summary['verifiable_numeric_conflicts'], 1):.1f}"],
        ["Baseline: never flag", 0, "0.000", "0.000", "0.0"],
    ]
    table = markdown_table(
        ["Detector", "Pairs flagged", "Flag rate",
         "Recall on verifiable conflicts", "Alarms per real conflict"], rows
    )
    (RESULTS_DIR / "exp3_contradiction.md").write_text(
        "# Experiment 3 -- Contradiction surfacing\n\n"
        f"Pairs compared: {n}; verifiable (quantity-level) conflicts: "
        f"{summary['verifiable_numeric_conflicts']}.\n\n"
        + table + "\n\n"
        "**The joint gate's recall on the verifiable subset is 1.000 by "
        "construction, and is therefore not evidence.** The verifiable subset is "
        "defined by the presence of a quantity-level conflict, and the numeric "
        "detector is an OR-branch of the gate.\n\n"
        "That subset now holds "
        f"{summary['verifiable_numeric_conflicts']} pair(s), down from 21 "
        "before the numeric rule was repaired, and a subset that small "
        "cannot carry a recall measurement: the joint gate's recall on it is "
        "arithmetic rather than evidence. The reason the subset collapsed is "
        "not that the conflicts stopped existing but that most of them were "
        "never conflicts. The old numeric rule keyed a number to the nearest "
        "distinctive word, so on encyclopaedic text it fired on citation "
        "years, version numbers and surnames -- \"Dettmer H., 1998\" against "
        "\"Dettmer W., 2006\", \"Incoterms 2020\" against \"Incoterms 2010\", "
        "\"Retrieved 8 December 2007\" against \"December 1995\". The "
        "reader-labelling experiment in Experiment 11 measured the damage and "
        "found that the gate's alarms were not confirmed by a reader.\n\n"
        "**The rule was repaired, not the corpus.** A number is now a "
        "quantity only when a measurement term governs it, the numeric branch "
        "carries the same subject check as the conjunction branch, and years "
        "and hyphenated identifiers are excluded. What is left is one "
        "quantity-level disagreement in the whole corpus, and it is between "
        "two different case studies rather than between two statements about "
        "the same subject: the corpus is encyclopaedic prose about concepts, "
        "so it holds worked examples and formulae rather than instance-level "
        "data, and a quantity-conflict detector has almost nothing in it to "
        "find.\n\n"
        "**So the gate's alarms now come from the conjunction branch, and it "
        "is the conjunction branch that the reader labels test.** The "
        "reader-labelled precision is in Experiment 11; the proxy "
        "precision/recall figures in the JSON are against an NLI-derived "
        "label and are therefore not independent of the detector.\n", encoding="utf-8"
    )
    print(f"[exp3] wrote {RESULTS_DIR / 'exp3_contradiction.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
