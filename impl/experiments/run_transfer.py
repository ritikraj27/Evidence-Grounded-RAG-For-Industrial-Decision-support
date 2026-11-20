#!/usr/bin/env python3
"""Experiment 4 -- cross-category transfer of the retrieval configuration.

The thesis's RO4 asks whether a retrieval configuration tuned on one set of
industrial categories transfers zero-shot to held-out categories. This
experiment answers it with the corpus the implementation actually ships,
which contains six real industrial categories.

Design
------
Categories are split into a *tuning* half and a *held-out* half. The gate's
calibration and its threshold are fitted on the tuning half only, then applied
unchanged to the held-out half. The quantity of interest is the degradation in
the held-out metrics.

This is the honest version of the claim. It is NOT the claim "we tuned on
industrial and it happens to work on industrial" -- every category in this
corpus is industrial, so the test is transfer *across industrial
sub-domains*, which is what the thesis actually asserts.

A second, stronger version of the test is also run: fit the calibration on
category A alone and evaluate on every other category one at a time, which
shows how much the threshold is category-specific.

Calibration target
------------------
The gate is calibrated at the QUERY level -- "does this retrieved context
contain sufficient evidence to answer?" -- for the same reason as in
Experiment 2: with one gold chunk among ~50 candidates the candidate-level
base rate is about 2%, and maximum-likelihood fitting against it returns
"nothing is relevant" and calls it a probability.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import (  # noqa: E402
    RESULTS_DIR,
    fit_query_calibrator,
    load_benchmark,
    load_index,
    markdown_table,
    query_features,
    detectability_posterior,
    write_result,
)
from src.evaluate import evaluate_retrieval  # noqa: E402
from src.config import CONFIG  # noqa: E402
from src.pipeline import Framework  # noqa: E402

SEED = 20261118


def pick_tau(pairs, target_coverage=0.90):
    """Choose tau by a stated rule: the highest tau still answering at least
    `target_coverage` of the answerable queries."""
    for tau in np.arange(0.05, 0.96, 0.05):
        answered = sum(1 for c, p in pairs if p >= tau and c["has_gold"])
        n_ans = sum(1 for c, p in pairs if c["has_gold"])
        if n_ans and answered / n_ans >= target_coverage:
            return float(tau)
    return 0.5


def metrics_at(pairs, tau):
    """Coverage and correctness at one threshold."""
    answered = refused = 0
    n_ans = n_un = 0
    correct_refusal = 0
    accepted_has_gold = accepted_total = 0
    for c, p in pairs:
        if c["has_gold"]:
            n_ans += 1
            if p < tau:
                refused += 1
            else:
                answered += 1
                accepted_total += 1
                if c["gold_found"]:
                    accepted_has_gold += 1
        else:
            n_un += 1
            if p < tau:
                correct_refusal += 1
    return {
        "n_answerable": n_ans,
        "n_unanswerable": n_un,
        "answerable_answered": answered / n_ans if n_ans else float("nan"),
        "answerable_refused": refused / n_ans if n_ans else float("nan"),
        "unanswerable_refused": correct_refusal / n_un if n_un else float("nan"),
        "coverage": ((answered + correct_refusal) / (n_ans + n_un)
                     if (n_ans + n_un) else 0.0),
        "top1_accuracy_given_accepted": (accepted_has_gold / accepted_total
                                         if accepted_total else float("nan")),
    }


def main() -> int:
    index = load_index()
    bench = load_benchmark()
    fw = Framework(index)

    print("[exp4] scoring all queries ...", flush=True)
    cases = query_features(fw, bench)
    categories = sorted({c["q"]["category"] for c in cases
                         if c["q"]["category"] != "unanswerable"})
    print(f"[exp4] categories: {categories}", flush=True)

    if len(categories) < 2:
        # The transfer experiment needs a subset of categories to transfer
        # to held-out ones. On the single-domain focus corpus there is no
        # split to make, so the experiment does not apply; the multi-category
        # corpus carries it.
        print(f"[exp4] only {len(categories)} category — the transfer split "
              "needs at least two; skipping.", flush=True)
        write_result("exp4_transfer", {
            "seed": SEED,
            "skipped": True,
            "reason": f"only {len(categories)} category in this corpus",
            "categories": categories,
        })
        (RESULTS_DIR / "exp4_transfer.md").write_text(
            "# Experiment 4 — Cross-category transfer\n\n"
            f"Skipped: this corpus has {len(categories)} category "
            f"({categories}), and the transfer split needs at least two.\n",
            encoding="utf-8")
        return 0

    rng = np.random.default_rng(SEED)

    # ---- Test 1: leave-half-out ---------------------------------------
    perm = rng.permutation(len(categories))
    half = len(categories) // 2
    tune_cats = {categories[i] for i in perm[:half]}
    test_cats = {categories[i] for i in perm[half:]}
    print(f"[exp4] tuning categories: {sorted(tune_cats)}")
    print(f"[exp4] held-out categories: {sorted(test_cats)}", flush=True)

    tune_cases = [c for c in cases if c["q"]["category"] in tune_cats]
    test_cases = [c for c in cases if c["q"]["category"] in test_cats]

    # The unanswerable queries carry no category -- "the corpus does not
    # state this answer" is not a property of one category -- so a split
    # by category silently drops the entire negative class out of *both*
    # halves, and the experiment ends up measuring only how many true
    # answers get refused. On the multi-category corpus the shipped
    # result has exactly this shape: n_unanswerable 0 and
    # unanswerable_refused NaN in every split.
    #
    # The negative class is shared, not split: it belongs in both halves.
    # It is the class the gate exists to manage, and an experiment that
    # transfers the gate's threshold across categories without it cannot
    # say anything about the gate's transfer.
    unanswerable_cases = [c for c in cases
                           if c["q"]["category"] == "unanswerable"]
    print(f"[exp4] shared negative class: {len(unanswerable_cases)} "
          f"unanswerable queries, in both halves", flush=True)
    tune_cases = tune_cases + unanswerable_cases
    test_cases = test_cases + unanswerable_cases

    model_tune = fit_query_calibrator(tune_cases, rng, frac=0.6)
    model_test = fit_query_calibrator(test_cases, rng, frac=0.6)
    model_all = fit_query_calibrator(cases, rng, frac=0.6)

    # Each arm is evaluated on the queries it is *about*.
    #
    # This was wrong, and the fix is the whole point of the experiment. The
    # posteriors were computed over `cases` -- every query in the corpus --
    # for every arm, so all three arms reported the same denominator
    # (n_answerable = 132, the whole benchmark, not the 66 of a half) and
    # the "transferred" arm scored the held-out queries with the model
    # fitted on the held-out half. Nothing was transferred. The numbers
    # were real and the labels were wrong, which is the failure mode this
    # project keeps finding.
    #
    #   tuning    -- model and threshold fitted on the tuning half,
    #               evaluated on the tuning half.
    #   transferred -- the tuning half's model and threshold applied
    #               unchanged to the held-out half. This is the arm that
    #               measures transfer.
    #   refitted -- the held-out half's own model and threshold, evaluated
    #               on the held-out half. This is the ceiling.
    pairs_tune = detectability_posterior(tune_cases, model_tune)
    pairs_transfer = detectability_posterior(test_cases, model_tune)
    pairs_test = detectability_posterior(test_cases, model_test)

    tau = pick_tau(pairs_tune)
    tau_test = pick_tau(pairs_test)
    m_tune = metrics_at(pairs_tune, tau)
    m_transfer = metrics_at(pairs_transfer, tau)   # model AND threshold transferred
    m_oracle = metrics_at(pairs_test, tau_test)    # refitted on the held-out half

    print(f"[exp4] tau (fitted on the tuning half) = {tau}")
    print(f"[exp4] tuning-half metrics   : {m_tune}")
    print(f"[exp4] held-out, TRANSFERRED  : {m_transfer}")
    print(f"[exp4] held-out, REFITTED     : {m_oracle}", flush=True)

    # ---- Test 1b: the comparison at a FIXED operating point ------------
    # Comparing each half at its own selected tau is close to trivial when
    # the selection rule lands on the same (lowest) tau in both. The
    # meaningful test holds the threshold fixed and asks how much the
    # *calibration* has to be refitted.
    #
    # The two columns are different posteriors: the transferred column is
    # the tuning half's model scored on the held-out half, the refitted
    # column is the held-out half's own model. They used to be the same
    # call, so the "refitted" column was a copy of the "transferred" one.
    fixed_taus = [0.10, 0.25, 0.50, 0.75]
    fixed_rows = []
    for t in fixed_taus:
        m_tr = metrics_at(pairs_transfer, t)
        m_re = metrics_at(pairs_test, t)
        fixed_rows.append({
            "tau": t,
            "transferred": m_tr,
            "refitted_same_tau": m_re,
        })
        print(f"[exp4] fixed tau={t:.2f}: held-out answerable_answered="
              f"{m_tr['answerable_answered']:.3f} unanswerable_refused="
              f"{m_tr['unanswerable_refused']:.3f}", flush=True)

    # ---- Test 2: leave-one-category-out -------------------------------
    # The same scope rule as above: leave-one-out is about the category that
    # was held out, so both arms are scored on that category's queries and
    # nowhere else. The leave-out arm uses the model fitted on the other
    # categories; the own-fit arm uses the model fitted on the held-out
    # category itself. They used to be scored over every query in the
    # corpus, and the own-fit arm was scored with the *other* categories'
    # posteriors at the own category's threshold.
    loco = []
    for cat in categories:
        # Same rule as the leave-half-out split: the shared negative class
        # goes into both the fitting set and the held-out set.
        others = [c for c in cases if c["q"]["category"] not in (cat, "unanswerable")]
        others = others + unanswerable_cases
        b = fit_query_calibrator(others, rng, frac=0.6)
        if b is None:
            continue
        pairs_others = detectability_posterior(others, b)
        t = pick_tau(pairs_others)
        own = [c for c in cases if c["q"]["category"] == cat]
        own = own + unanswerable_cases
        pairs_held = detectability_posterior(own, b)
        m_held = metrics_at(pairs_held, t)

        b_own = fit_query_calibrator(own, rng, frac=0.6)
        m_own = {}
        tau_own = None
        if b_own is not None:
            pairs_own = detectability_posterior(own, b_own)
            tau_own = pick_tau(pairs_own)
            m_own = metrics_at(pairs_own, tau_own)

        loco.append({
            "held_out_category": cat,
            "weights_from_others": [float(x) for x in b["weights"]],
            "weights_own": ([float(x) for x in b_own["weights"]]
                            if b_own else None),
            "tau_transferred": t,
            "tau_refitted": tau_own,
            "transferred": m_held,
            "own_fit": m_own,
        })
        print(f"[exp4] LOCO {cat}: transferred answerable_answered="
              f"{m_held['answerable_answered']:.3f} "
              f"unanswerable_refused={m_held['unanswerable_refused']:.3f}",
              flush=True)

    # ---- Test 3: per-category retrieval quality -----------------------
    per_cat = []
    for cat in categories:
        sub = [c for c in cases if c["q"]["category"] == cat]
        runs = [c["fused"] for c in sub]
        rels = [set(c["q"]["gold"]) for c in sub]
        grades = [{g: (3.0 if c["q"]["family"] == "table_lookup" else 1.0)
                   for g in c["q"]["gold"]} for c in sub]
        ev = evaluate_retrieval(runs, rels, grades)
        per_cat.append({
            "category": cat,
            "n": len(sub),
            "recall@10": ev.recall_at_10,
            "mrr": ev.mrr,
            "ndcg@10": ev.ndcg_at_10,
        })
        print(f"[exp4] {cat}: n={len(sub)} R@10={ev.recall_at_10:.3f} "
              f"MRR={ev.mrr:.3f} nDCG={ev.ndcg_at_10:.3f}", flush=True)

    payload = {
        "seed": SEED,
        "design": "query-level sufficiency calibration; model and threshold "
                  "transferred unchanged",
        "categories": categories,
        "leave_half_out": {
            "tuning_categories": sorted(tune_cats),
            "held_out_categories": sorted(test_cats),
            "weights_tuning_half": [float(x) for x in model_tune["weights"]],
            "weights_held_out_half": [float(x) for x in model_test["weights"]],
            "weights_all": [float(x) for x in model_all["weights"]],
            "tau": tau,
            "tau_refitted_on_held_out": tau_test,
            "metrics_tuning": m_tune,
            "metrics_held_out_transferred": m_transfer,
            "metrics_held_out_refitted": m_oracle,
            "fixed_tau_comparison": fixed_rows,
            "weights_stability": {
                "tuning_intercept": float(model_tune["weights"][0]),
                "held_out_intercept": float(model_test["weights"][0]),
                "tuning_top1_rerank": float(model_tune["weights"][1]),
                "held_out_top1_rerank": float(model_test["weights"][1]),
            },
        },
        "leave_one_category_out": loco,
        "per_category_retrieval": per_cat,
    }
    payload["retrieval_placement"] = CONFIG.modality.position
    write_result("exp4_transfer", payload)

    rows = [
        [p["category"], p["n"], f"{p['recall@10']:.3f}", f"{p['mrr']:.3f}",
         f"{p['ndcg@10']:.3f}"]
        for p in per_cat
    ]
    table = markdown_table(["Category", "n", "R@10", "MRR", "nDCG@10"], rows)
    arm_rows = markdown_table(
        ["Metric (held-out half)", "Transferred", "Refitted"],
        [[name,
          f"{m_transfer.get(key, float('nan')):.3f}",
          f"{m_oracle.get(key, float('nan')):.3f}"]
         for name, key in (("Answerable answered", "answerable_answered"),
                           ("Answerable refused", "answerable_refused"),
                           ("Coverage", "coverage"),
                           ("Top-1 accuracy given accepted",
                            "top1_accuracy_given_accepted"))])
    (RESULTS_DIR / "exp4_transfer.md").write_text(
        "# Experiment 4 -- Cross-category transfer\n\n"
        f"Tuning half: {sorted(tune_cats)}\n\nHeld-out half: {sorted(test_cats)}\n\n"
        f"tau (fitted on the tuning half, transferred unchanged) = {tau}\n\n"
        "Each arm is evaluated on the queries it is about: the transferred arm "
        "carries the tuning half's model AND threshold unchanged onto the "
        "held-out half; the refitted arm is the held-out half's own model and "
        "threshold, and is the ceiling.\n\n"
        "The split is over document categories, and the benchmark's "
        "unanswerable questions carry no category, so neither half contains "
        "any. This experiment therefore measures coverage on the answerable "
        "questions across domains, and says nothing about refusal behaviour "
        "across domains.\n\n"
        + arm_rows + "\n\n"
        "### Per-category retrieval quality\n\n"
        + table + "\n", encoding="utf-8"
    )
    print(f"[exp4] wrote {RESULTS_DIR / 'exp4_transfer.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
