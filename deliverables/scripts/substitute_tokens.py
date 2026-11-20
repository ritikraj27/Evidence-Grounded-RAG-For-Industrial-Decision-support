#!/usr/bin/env python3
"""Substitute the measured values into the prose of the deliverables.

Some numbers — the benchmark size, the corpus size, the modality shares — are
stated in prose in the abstracts and the narrative. Hard-coding them means a
changed corpus silently leaves a wrong number in a paper. This script replaces
tokens of the form {{N_QUERIES}} with the live values, so the prose is
regenerated rather than remembered.

Tokens
------
    {{N_QUERIES}}       total benchmark queries
    {{N_ANSWERABLE}}    answerable queries
    {{N_UNANSWERABLE}}  deliberately unanswerable queries
    {{N_CHUNKS}}        corpus chunks
    {{N_DOCUMENTS}}     corpus documents
    {{SHARE_TEXT}}      text share of the corpus, as a percentage
    {{SHARE_TABLE}}     table share
    {{SHARE_CHART}}     chart share
    {{N_CATEGORIES}}    number of industrial categories

The LaTeX templates use the `_TEX` variants of the three formatted numbers.
In LaTeX a bare thousands comma is a punctuation mark rather than a digit
separator, and a bare `%` starts a comment that swallows the rest of the
line, so `{{N_CHUNKS}}` and `{{SHARE_TEXT}}` cannot be used verbatim in a
`.tex` file.

    {{N_CHUNKS_TEX}}    corpus chunks, comma grouped as 2{,}871
    {{SHARE_TEXT_TEX}}  text share, with the percent sign escaped
    {{SHARE_TABLE_TEX}} table share, with the percent sign escaped
    {{SHARE_CHART_TEX}} chart share, with the percent sign escaped
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from figure_captions import (FIGURES, TOKEN_NAMES as FIGURE_TOKENS,
                            resolve as resolve_caption)
from results_source import _significance_clause
from results_source import pull_up_leading_numbers
from results_source import PLACEMENT_STAMPED_RESULTS as _PLACEMENT_STAMPED_RESULTS
from results_source import (  # noqa: E402
    _comp_index,
    _p_str,
    answer_validation_conventions_claim,
    answer_validation_conventions_summary,
    conflict_control_claim,
    conflict_control_summary,
    contradiction_branch_claim,
    contradiction_precision_claim,
    contradiction_precision_claim_short,
    contradiction_precision_mechanism,
    contradiction_precision_mechanism_short,
    contradiction_precision_summary,
    gate_overall,
    gen_arm,
    generation_cost,
    generation_cost_claim,
    generation_summary,
    generation_summary_short,
    h21_conditional_verdict,
    h21_verdict,
    load_conflict_control,
    load_generation,
    load_generation_conditions,
    load_generation_replication,
    generation_replication_claim,
    generation_replication_cautious_claim,
    load_generator_completion,
    generator_completion_claim,
    generator_completion_short,
    load_answer_validation_conventions,
    load_gate_per_retriever,
    scope_summary,
    load_soft_prior,
    load_transfer,
    gate_per_retriever_summary,
    soft_prior_summary,
    next_steps,
    load_label_audit,
    load_scorer_validation,
    load_unanswerable_audit,
    unanswerable_audit_summary,
    residual_form_claim,
    unanswerable_refusal_by_family,
    load_pre_repair_gate,
)

ROOT = Path(__file__).resolve().parents[2]
BENCH = ROOT / "impl" / "data" / "benchmark" / "benchmark.json"
MANIFEST = ROOT / "impl" / "data" / "corpus" / "manifest.json"
RESULTS = ROOT / "impl" / "results"
#: The focus-domain run carries the headline numbers; the multi-category
#: run is the fallback and the source of the transfer study.
FOCUS_RESULTS = ROOT / "impl" / "results_focus"
FOCUS_MANIFEST = ROOT / "impl" / "data" / "corpus_focus" / "manifest.json"
FOCUS_INDEX = ROOT / "impl" / "artifacts_focus" / "index.json"
FOCUS_BENCH = ROOT / "impl" / "data" / "benchmark_focus" / "benchmark.json"

TARGETS = [
    "deliverables/Deliverable_1_Part1_Content.md",
    "deliverables/Deliverable_1_PartD_Code.md",
    "deliverables/Deliverable_1_PartF_toJ.md",
    "deliverables/Deliverable_2a_Technical_Report.md",
    "deliverables/Deliverable_2b_IEEE_Conference_Paper.tex",
    "deliverables/Deliverable_2c_Journal_Style_Paper.tex",
    "deliverables/scripts/make_pptx.py",
    "deliverables/scripts/make_docx.py",
    "README.md",
    "deliverables/READ_ME_FIRST.md",
    "deliverables/MTP_Plain_Language_Guide.md",
    "deliverables/MTP_Status_Report.md",
    "deliverables/MTP_Technical_Documentation.md",
]








def _tex_number(s: str) -> str:
    """Group a thousands separator the way LaTeX wants it: 2{,}871."""
    return s.replace(",", "{,}")



def _first(directories, name: str):
    """The first existing <directory>/name, preferring the focus-domain run."""
    for d in (FOCUS_RESULTS, directories):
        p = d / name
        if p.exists():
            return p
    return None


def _add_form_probe_tokens(v: dict[str, str]) -> None:
    """Expose the form probe: what the gate does with malformed queries.

    The gate is an evidence gate, not a form gate. It decides whether the
    retrieved context suffices to answer; it never asks whether the query is
    well-formed. The probe measures how much of that shows up in the numbers:
    the malformed query stems are the ones the benchmark's own generator
    produced and rejected, harvested by re-running its extraction.
    """
    p = _first(RESULTS, "exp9_form_probe.json")
    if p is None:
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    v["FORM_PROBE_N"] = str(d["n_probed"])
    v["FORM_PROBE_ACCEPTED"] = str(d["n_accepted_by_gate"])
    v["FORM_PROBE_RATE"] = f"{d['acceptance_rate']:.1%}"
    v["FORM_PROBE_MEAN_POSTERIOR"] = f"{d['mean_posterior']:.3f}"
    v["FORM_PROBE_HARVESTED"] = str(d["n_candidates_harvested"])
    # Which corpus the probe ran on. The probe and the runtime form check are
    # measured on different corpora, and a deck that quotes both without
    # saying so looks like it is quoting one.
    v["FORM_PROBE_CORPUS"] = (
        "the focus domain"
        if p.parent == FOCUS_RESULTS else "the six-category corpus")


def _add_form_validator_tokens(v: dict[str, str]) -> None:
    """Expose the runtime query-form check: what it catches, and what it costs.

    The gate is an evidence gate and the form check is a form gate; they
    answer different questions and the probe above measures only the first.
    The check's rates are always reported as a pair -- what it refuses on
    malformed input, and what it refuses on well-formed input -- because the
    second number is the one that matters. A false rejection is a refusal of
    a question the corpus could have answered, which is the one failure this
    framework is built to avoid.

    The counterfactual is the important half. The obvious implementation is
    to reuse the benchmark builder's existing subject filter, and it is
    measured here what that would have cost on the same labelled stems.
    """
    p = _first(RESULTS, "exp10_form_validator.json")
    if p is None:
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    v["FORMVAL_CORPUS"] = (
        "the focus domain"
        if p.parent == FOCUS_RESULTS else "the six-category corpus")

    b = d["benchmark"]
    v["FORMVAL_BENCH_N"] = str(b["n"])
    v["FORMVAL_BENCH_REJECTED"] = str(b["n_rejected"])
    v["FORMVAL_BENCH_RATE"] = f"{b['false_rejection_rate']:.1%}"

    st = d["harvested_stems"]
    v["FORMVAL_STEM_MAL_N"] = str(st["n_malformed"])
    v["FORMVAL_STEM_MAL_REJECTED"] = str(st["n_malformed_rejected"])
    v["FORMVAL_STEM_MAL_RATE"] = f"{st['rejection_rate_on_malformed']:.1%}"
    v["FORMVAL_STEM_GOOD_N"] = str(st["n_well_formed"])
    v["FORMVAL_STEM_GOOD_REJECTED"] = str(st["n_well_formed_rejected"])

    fx_m = d["hand_authored_malformed"]
    fx_v = d["hand_authored_well_formed"]
    v["FORMVAL_FIX_MAL_N"] = str(fx_m["n_expected_rejected"])
    v["FORMVAL_FIX_MAL_REJECTED"] = str(fx_m["n_rejected"])
    # The denominator the hand-written set was drawn from. The two keyboard
    # mashes in it are expected misses, so the refusal count and the size of
    # the set are different numbers.
    v["FORMVAL_FIX_MAL_TOTAL"] = str(fx_m["n"])
    v["FORMVAL_FIX_VAL_N"] = str(fx_v["n"])
    v["FORMVAL_FIX_VAL_REJECTED"] = str(fx_v["n_rejected"])

    cf = d["counterfactual_benchmark_rule"]
    v["FORMVAL_COUNTERFACTUAL_N"] = str(cf["n_well_formed"])
    v["FORMVAL_COUNTERFACTUAL_REJECTED"] = str(cf["n_well_formed_rejected"])
    v["FORMVAL_COUNTERFACTUAL_RATE"] = (
        f"{cf['false_rejection_rate_on_well_formed']:.1%}")

    # What the check costs. It runs before retrieval, so this is the whole
    # price of a refused request.
    _cost = d.get("cost") or {}
    if _cost.get("microseconds_per_query") is not None:
        v["FORMVAL_COST_US"] = f"{_cost['microseconds_per_query']:.1f}"

    # The six-category run, for the transfer statement. Read directly rather
    # than through `_first`, which prefers the focus run.
    mp = RESULTS / "exp10_form_validator.json"
    if mp.exists():
        m = json.loads(mp.read_text(encoding="utf-8"))
        v["FORMVAL_MC_BENCH_N"] = str(m["benchmark"]["n"])
        v["FORMVAL_MC_BENCH_REJECTED"] = str(m["benchmark"]["n_rejected"])
        mst = m["harvested_stems"]
        v["FORMVAL_MC_STEM_MAL_N"] = str(mst["n_malformed"])
        v["FORMVAL_MC_STEM_MAL_REJECTED"] = str(mst["n_malformed_rejected"])
        v["FORMVAL_MC_STEM_MAL_RATE"] = (
            f"{mst['rejection_rate_on_malformed']:.1%}")
        v["FORMVAL_MC_STEM_GOOD_N"] = str(mst["n_well_formed"])
        v["FORMVAL_MC_STEM_GOOD_REJECTED"] = str(mst["n_well_formed_rejected"])
        mcf = m["counterfactual_benchmark_rule"]
        v["FORMVAL_MC_COUNTERFACTUAL_N"] = str(mcf["n_well_formed"])
        v["FORMVAL_MC_COUNTERFACTUAL_REJECTED"] = str(
            mcf["n_well_formed_rejected"])


def _add_baseline_tokens(v: dict[str, str]) -> None:
    """Expose the previous encoder's measurements as tokens.

    The dense leg was a general-purpose sentence encoder before it was
    replaced with a retrieval-trained one. The comparison is a finding, so
    both sides of it are bound to measured values rather than to
    recollection: `BASE_MC_*` is the multi-category corpus, `BASE_F_*` the
    focus domain.
    """
    p = ROOT / "research" / "baseline_minilm" / "baseline_summary.json"
    if not p.exists():
        return
    data = json.loads(p.read_text(encoding="utf-8"))
    for prefix, key in (("BASE_MC", "multi_category"), ("BASE_F", "focus")):
        b = data.get(key)
        if not b:
            continue
        sysm = b["systems"]
        comp = b["comparisons"]
        v[f"{prefix}_ENC"] = b["encoder"]
        for letter, name in (("A", "A. bm25_only"), ("B", "B. dense_only"),
                             ("C", "C. hybrid_rrf"), ("D", "D. hybrid_rrf_rerank")):
            v[f"{prefix}_R_{letter}"] = f"{sysm[name]['recall@10']:.3f}"
            v[f"{prefix}_MRR_{letter}"] = f"{sysm[name]['mrr']:.3f}"
            v[f"{prefix}_NDCG_{letter}"] = f"{sysm[name]['nDCG@10']:.3f}"
        v[f"{prefix}_P_AB"] = f"{comp['A. bm25_only']['p_value']:.1e}"
        v[f"{prefix}_P_BC"] = f"{comp['B. dense_only']['p_value']:.1e}"
        v[f"{prefix}_P_CD"] = f"{comp['C. hybrid_rrf']['p_value']:.1e}"
        v[f"{prefix}_PMRR_CD"] = f"{comp['C. hybrid_rrf'].get('p_mrr') or 0:.1e}"
        v[f"{prefix}_DMRR_CD"] = f"{comp['C. hybrid_rrf'].get('delta_mrr') or 0:+.3f}"
        v[f"{prefix}_DNDCG_CD"] = f"{comp['C. hybrid_rrf'].get('delta_ndcg') or 0:+.3f}"
        v[f"{prefix}_N_ANSWERABLE"] = str(b["n_answerable"])

def _encoder_verdict(v: dict[str, str]) -> str:
    """One sentence stating what the encoder change actually did.

    Written from the measurements rather than asserted, because the outcome
    was not known in advance and the thesis's framing is that the
    measurement is the contribution.
    """
    def num(key):
        try:
            return float(v[key])
        except (KeyError, ValueError):
            return float("nan")

    before_gap = num("BASE_F_R_A") - num("BASE_F_R_B")
    after_gap = num("R_A") - num("R_B")
    before_order = num("BASE_F_NDCG_A") - num("BASE_F_NDCG_C")
    after_order = num("NDCG_A") - num("NDCG_C")

    parts = []
    if after_gap == after_gap and before_gap == before_gap:
        if after_gap < 0:
            parts.append("the dense leg now **beats** the lexical leg on "
                         "Recall@10, where it was behind before")
        elif after_gap < before_gap * 0.5:
            parts.append("the gap between the dense leg and the lexical leg "
                         "closed by more than half")
        elif after_gap < before_gap:
            parts.append("the gap between the dense leg and the lexical leg "
                         "narrowed")
        else:
            parts.append("the gap between the dense leg and the lexical leg "
                         "did not narrow")
    if after_order == after_order and before_order == before_order:
        if after_order < 0:
            parts.append("and the fused system now **orders better** than the "
                         "lexical leg alone, which it did not before")
        elif after_order < before_order:
            parts.append("and the fused system's ordering deficit against the "
                         "lexical leg shrank")
        else:
            parts.append("and the fused system's ordering against the lexical "
                         "leg is unchanged")
    if not parts:
        return "The encoder change did not move the measurements."
    return "; ".join(parts).capitalize() + "."

def _add_transfer_tokens(v: dict) -> None:
    """Bind the cross-category transfer experiment to tokens.

    The experiment is defined only on the six-category corpus, so it is read
    from that run and never from the focus-domain one -- the focus corpus has
    one category and the leave-half-out split is meaningless on it.

    Three arms are reported: the model fitted on the tuning half and applied
    to it, the same model and the same threshold transferred unchanged to the
    held-out half, and the model re-fitted on the held-out half. The third is
    the ceiling: it says what the held-out categories could support if the
    threshold had been refitted there, and the difference between the second
    and the third is what transferring a threshold actually costs.
    """
    p = ROOT / "impl" / "results" / "exp4_transfer.json"
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    lh = d.get("leave_half_out") or {}
    v["TRANSFER_TAU"] = f"{lh.get('tau', 0):.2f}"
    v["TRANSFER_TAU_REFIIT"] = f"{lh.get('tau_refitted_on_held_out', 0):.2f}"
    v["TRANSFER_TUNING_CATS"] = ", ".join(lh.get("tuning_categories") or [])
    v["TRANSFER_HELDOUT_CATS"] = ", ".join(lh.get("held_out_categories") or [])
    arms = (("TUNING", "metrics_tuning"),
            ("XFER", "metrics_held_out_transferred"),
            ("REFIIT", "metrics_held_out_refitted"))
    for prefix, key in arms:
        m = lh.get(key) or {}
        if not m:
            continue
        v[f"TRANSFER_{prefix}_ANSWERABLE_ANSWERED"] = \
            f"{m.get('answerable_answered', 0):.3f}"
        v[f"TRANSFER_{prefix}_UNANSWERABLE_REFUSED"] = \
            f"{m.get('unanswerable_refused', 0):.3f}"
        v[f"TRANSFER_{prefix}_COVERAGE"] = f"{m.get('coverage', 0):.3f}"
        v[f"TRANSFER_{prefix}_TOP1_ACC"] = \
            f"{m.get('top1_accuracy_given_accepted', 0):.3f}"


def _add_contradiction_tokens(v: dict) -> None:
    """Bind the contradiction-surfacing experiment to tokens.

    The one number that must never be quoted without its caveat is the joint
    gate's recall on the verifiable subset: it is 1.000 *by construction*,
    because that subset is defined by a numeric conflict and the numeric
    detector is an OR-branch of the gate. The informative number is the
    conjunction's recall with the numeric branch removed, and both are bound
    here so that neither can be quoted without the other.
    """
    p = ROOT / "impl" / "results_focus" / "exp3_contradiction.json"
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8")).get("summary") or {}
    if not d:
        return
    v["CONTRA_PAIRS"] = f"{d.get('pairs_compared', 0):,}"
    v["CONTRA_VERIFIABLE"] = str(d.get("verifiable_numeric_conflicts", 0))
    v["CONTRA_PREVALENCE"] = f"{d.get('prevalence_of_true_conflict', 0):.4f}"
    v["CONTRA_NLI_FLAGGED"] = str(d.get("nli_only_flagged", 0))
    v["CONTRA_NLI_FLAG_RATE"] = f"{d.get('nli_flag_rate', 0):.3f}"
    v["CONTRA_NLI_ALARMS"] = f"{d.get('nli_alarms_per_verifiable_conflict', 0):.1f}"
    v["CONTRA_NLI_RECALL"] = \
        f"{d.get('conjunction_recall_on_verifiable_subset', 0):.3f}"
    v["CONTRA_CONJUNCTION_FLAGGED"] = str(d.get("conjunction_flagged", 0))
    v["CONTRA_JOINT_FLAGGED"] = str(d.get("joint_gate_flagged", 0))
    v["CONTRA_JOINT_FLAG_RATE"] = f"{d.get('joint_flag_rate', 0):.3f}"
    v["CONTRA_JOINT_ALARMS"] = \
        f"{d.get('joint_alarms_per_verifiable_conflict', 0):.1f}"
    v["CONTRA_NUMERIC_BRANCH_ONLY"] = str(d.get("numeric_branch_only_caught", 0))

    # The measured precision. Until this experiment was run the gate's
    # precision was the framework's largest unverified quantity; it is now
    # measured against reader labels, and the number is bound here together
    # with the agreement between the two annotators, so that neither can be
    # quoted without the other.
    _cp_path = ROOT / "impl" / "results_focus" / "exp11_contradiction_precision.json"
    if not _cp_path.exists():
        return
    try:
        _cp = json.loads(_cp_path.read_text(encoding="utf-8"))
    except Exception:
        return
    _cps = contradiction_precision_summary(_cp)
    if not _cps:
        return
    v["CONTRA_PRECISION_PAIRS"] = str(_cps.get("n_compared"))
    v["CONTRA_PRECISION_N"] = str(_cps.get("n_alarms_compared"))
    v["CONTRA_PRECISION"] = f"{(_cps.get('precision_upper') or 0):.3f}"
    v["CONTRA_PRECISION_PCT"] = f"{(_cps.get('precision_upper') or 0) * 100:.1f}%"
    _lo_ci = _cps.get("precision_upper_ci95") or [0, 0]
    v["CONTRA_PRECISION_CI_LO"] = f"{(_lo_ci[0] or 0) * 100:.1f}%"
    v["CONTRA_PRECISION_CI_HI"] = f"{(_lo_ci[1] or 0) * 100:.1f}%"
    v["CONTRA_PRECISION_AGREE"] = \
        f"{(_cps.get('raw_agreement_2way') or 0) * 100:.1f}%"
    v["CONTRA_PRECISION_AGREE_N"] = str(
        (_cps.get("n_compared") or 0) - (_cps.get("n_disagreements_2way") or 0))
    v["CONTRA_PRECISION_DISAGREE_N"] = str(_cps.get("n_disagreements_2way"))
    # Cohen's kappa is undefined when both readers put every pair in the
    # same category, which is what happens here: the positive category is
    # empty. It is reported as undefined rather than as 0.000, because 0.000
    # would say "no better than chance" where the truth is "no positives to
    # agree or disagree about".
    _k2 = _cps.get("cohen_kappa_2way")
    v["CONTRA_PRECISION_KAPPA"] = ("undefined (the positive category is "
                                    "empty)" if _k2 is None
                                    else f"{_k2:.3f}")
    v["CONTRA_VERIFIABLE_N"] = str(_cps.get("verifiable_n_pairs"))
    _vl = _cps.get("verifiable_labelled_contradiction")
    _vh = _cps.get("verifiable_labelled_contradiction_max")
    v["CONTRA_VERIFIABLE_LABELS"] = (f"{_vl}" if _vl == _vh
                                     else f"{_vl} to {_vh}")
    v["CONTRA_PRECISION_CLAIM"] = contradiction_precision_claim(_cp)
    v["CONTRA_PRECISION_MECHANISM"] = contradiction_precision_mechanism(_cp)
    v["CONTRA_PRECISION_CLAIM_SHORT"] = contradiction_precision_claim_short(_cp)
    v["CONTRA_PRECISION_MECHANISM_SHORT"] = contradiction_precision_mechanism_short(_cp)
    v["CONTRA_BRANCH_CLAIM"] = contradiction_branch_claim(_cp)

    # The three branches of the gate, and how the alarms split between them.
    _kinds = d.get("flagged_by_kind") or {}
    v["CONTRA_BRANCH_SEMANTIC"] = str(_kinds.get("semantic", 0))
    v["CONTRA_BRANCH_REVISION"] = str(_kinds.get("revision", 0))
    v["CONTRA_BRANCH_QUANTITY"] = str(_kinds.get("quantity", 0))
    v["CONTRA_SURFACED"] = str(d.get("surfaced_findings", 0))
    v["CONTRA_WITHHELD"] = str(d.get("withheld_findings", 0))

    # The detector's own positive control: pairs whose correct behaviour is
    # known in advance, so that a measurement of zero on a corpus with no
    # positives can be read as "the corpus cannot exercise the mechanism"
    # rather than "the mechanism does not work".
    _ctl = load_conflict_control()
    if _ctl:
        _csum = conflict_control_summary(_ctl)
        v["CONTRA_CONTROL_N"] = str(_csum.get("n_pairs"))
        v["CONTRA_CONTROL_CORRECT"] = str(_csum.get("n_correct"))
        v["CONTRA_CONTROL_CLAIM"] = conflict_control_claim(_ctl)

    # The positive control: both annotators scored it in full, which is what
    # licenses reading the precision number as a statement about the
    # detector rather than about the annotators' habits.
    _ctrl_n = _cps.get("control_n")
    _ctrl_min = _cps.get("control_correct_min")
    _ctrl_max = _cps.get("control_correct_max")
    if _ctrl_n and _ctrl_min is not None:
        v["CONTRA_PRECISION_CONTROL_N"] = str(_ctrl_n)
        v["CONTRA_PRECISION_CONTROL"] = (
            f"{_ctrl_max} of {_ctrl_n}" if _ctrl_min == _ctrl_max
            else f"{_ctrl_min} to {_ctrl_max} of {_ctrl_n}")

    # How the readers labelled the alarms, which is the diagnosis: a reader
    # that says "different subjects" about an alarm is naming a failure of
    # the subject check; a reader that says "no conflict" is naming a
    # failure of the NLI model.
    _per = _cps.get("per_annotator") or {}
    _tm, _nc = [], []
    for _m in _per.values():
        _d = _m.get("label_distribution_alarms") or {}
        _tm.append(_d.get("term_mismatch", 0))
        _nc.append(_d.get("no_conflict", 0))
    if _tm:
        v["CONTRA_ALARM_N"] = str(_cps.get("n_alarms_compared"))
        v["CONTRA_ALARM_TERM_MISMATCH"] = (
            str(min(_tm)) if min(_tm) == max(_tm)
            else f"{min(_tm)} to {max(_tm)}")
        v["CONTRA_ALARM_NO_CONFLICT"] = (
            str(min(_nc)) if min(_nc) == max(_nc)
            else f"{min(_nc)} to {max(_nc)}")

    # The random sample of the pairs the gate did not flag. Zero
    # contradictions there is what says the corpus does not contain the
    # phenomenon the mechanism detects.
    v["CONTRA_UNFLAGGED_SAMPLE"] = str(_cps.get("n_unflagged_sampled"))
    v["CONTRA_UNFLAGGED_CONTRADICTIONS"] = str(
        _cps.get("n_contradictions_in_unflagged_sample"))

    # The repair, before and after. Both sides are measured, and the
    # pre-repair counts are archived in exp3_contradiction.json.
    _repair = (d.get("numeric_rule_repair") or {})
    _before = _repair.get("before") or {}
    _after = _repair.get("after") or {}
    if _before and _after:
        v["CONTRA_REPAIR_CONFLICTS"] = (
            f"{_before.get('verifiable_numeric_conflicts')} to "
            f"{_after.get('verifiable_numeric_conflicts')}")
        v["CONTRA_REPAIR_ALARMS"] = (
            f"{_before.get('joint_gate_flagged')} to "
            f"{_after.get('joint_gate_flagged')}")
    # The second repair, the subject check. The headline is the whole
    # chain -- before any repair to after both -- and the subject repair
    # on its own is kept separately.
    _subj = (d.get("subject_check_repair") or {})
    if _subj:
        v["CONTRA_ALARMS_AFTER"] = str(_subj.get("after"))
        v["CONTRA_SUBJECT_BEFORE"] = str(_subj.get("before"))
        v["CONTRA_SUBJECT_SUPPRESSED"] = str(
            _subj.get("suppressed_by_subject_check"))
        v["CONTRA_ALARMS_BEFORE"] = str(
            (_before or {}).get("joint_gate_flagged"))


def _add_case_study_tokens(v: dict) -> None:
    """Bind the focus-domain before/after case study to tokens.

    This is the aggregate version of the question a practitioner actually
    asks: not "what does the ablation table say" but "what does the whole
    framework do to my questions, compared with a plain retriever that
    never refuses". The two arms are the plain lexical retriever and the
    full framework, on the same 176 questions.
    """
    p = ROOT / "impl" / "results_focus" / "exp6_focus_case.json"
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8")).get("summary") or {}
    if not d:
        return
    v["CASE_N_QUERIES"] = str(d.get("n_queries", 0))
    v["CASE_N_ANSWERABLE"] = str(d.get("n_answerable", 0))
    v["CASE_N_UNANSWERABLE"] = str(d.get("n_unanswerable", 0))
    v["CASE_BM25_UNANS_ANSWERED"] = str(d.get("unanswerable_answered_by_baseline", 0))
    v["CASE_FW_UNANS_ANSWERED"] = str(d.get("unanswerable_answered_by_framework", 0))
    v["CASE_BM25_GOLD_TOP10"] = f"{d.get('baseline_bm25_gold_in_top10', 0):.3f}"
    v["CASE_FW_GOLD_ACCEPTED"] = f"{d.get('full_framework_gold_accepted', 0):.3f}"
    v["CASE_GATE_REF_ANSWERABLE"] = f"{d.get('gate_refused_answerable', 0):.3f}"
    v["CASE_GATE_REF_UNANSWERABLE"] = (
        f"{d.get('gate_refused_unanswerable', 0):.3f}")
    v["CASE_MEAN_CHUNKS"] = f"{d.get('mean_accepted_chunks', 0):.1f}"
    _n_ans = d.get("n_answerable", 0)
    _ref_ans = round(d.get("gate_refused_answerable", 0) * _n_ans)
    v["CASE_BM25_ANS_ANSWERED"] = str(_n_ans)
    v["CASE_FW_ANS_ANSWERED"] = str(_n_ans - _ref_ans)
    v["CASE_FW_ANS_REFUSED"] = str(_ref_ans)


def _add_trade_tokens(v: dict) -> None:
    """Bind the gate's cost-and-benefit trade to tokens.

    "Does the system work better with or without the gate?" is the question
    that follows "is it working?", and it has no single answer: the gate
    trades correct answers for confidently-wrong ones. These numbers are
    counted from the stored per-question records rather than from the
    summary blocks, because the summary reports an accuracy over the
    questions that were answered -- and a gate that declines the hardest
    questions raises that number by selection alone. Counting the two
    correctness tests separately matters too: they disagree about the size
    of the cost.
    """
    for _cond, _fname in (("CAUTIOUS", "exp8_generation.json"),
                          ("ANSWERING", "exp8_generation_answering.json")):
        p = ROOT / "impl" / "results_focus" / _fname
        if not p.exists():
            continue
        payload = json.loads(p.read_text(encoding="utf-8"))
        if payload.get("status") != "run":
            continue
        records = payload.get("records") or {}
        for _arm, _pfx in (("rag_nogate", "NOGATE"),
                           ("rag@fitted", "FITTED"),
                           ("rag@random", "RANDOM"),
                           ("long_context", "LONGCTX")):
            _r = records.get(_arm) or []
            if not _r:
                continue
            v[f"TRADE_{_cond}_{_pfx}_ANSWERED"] = str(
                sum(1 for r in _r if r.get("answered")))
            v[f"TRADE_{_cond}_{_pfx}_CORRECT_NLI"] = str(
                sum(1 for r in _r if r.get("answered") and r.get("correct_nli")))
            v[f"TRADE_{_cond}_{_pfx}_CORRECT_KEYTERM"] = str(
                sum(1 for r in _r if r.get("answered") and r.get("correct_keyterm")))
            v[f"TRADE_{_cond}_{_pfx}_WRONG_ANSWERED"] = str(
                sum(1 for r in _r if r.get("answered") and not r.get("answerable")))
        # The trade itself, as two differences: how many correct answers the
        # gate gives up, and how many confidently-wrong ones it removes.
        _ng = records.get("rag_nogate") or []
        _ft = records.get("rag@fitted") or []
        if _ng and _ft:
            def _c(rs, key):
                return sum(1 for r in rs
                           if r.get("answered") and r.get(key))
            def _w(rs):
                return sum(1 for r in rs
                           if r.get("answered") and not r.get("answerable"))
            v[f"TRADE_{_cond}_CORRECT_COST_NLI"] = str(
                _c(_ng, "correct_nli") - _c(_ft, "correct_nli"))
            v[f"TRADE_{_cond}_CORRECT_COST_KEYTERM"] = str(
                _c(_ng, "correct_keyterm") - _c(_ft, "correct_keyterm"))
            v[f"TRADE_{_cond}_WRONG_REMOVED"] = str(_w(_ng) - _w(_ft))


def _add_project_scale_tokens(v: dict) -> None:
    """Bind the size of the codebase itself to tokens.

    "How much is there?" is a question a status report has to answer, and an
    answer written by hand goes stale the first time a file is added. These
    are counted from the tree at build time.
    """
    impl = ROOT / "impl"
    src = sorted((impl / "src").glob("*.py"))
    experiments = sorted((impl / "experiments").glob("*.py"))
    scripts = sorted((impl / "scripts").glob("*.py"))
    tests = sorted((impl / "tests").glob("test_*.py"))
    v["N_SOURCE_MODULES"] = str(len(src))
    v["N_EXPERIMENTS"] = str(len(experiments))
    v["N_RUNNER_SCRIPTS"] = str(len(scripts))
    v["N_TEST_FILES"] = str(len(tests))
    v["N_SOURCE_LINES"] = f"{sum(len(p.read_text(encoding='utf-8').splitlines()) for p in src):,}"
    n_tests = 0
    for t in tests:
        n_tests += len(re.findall(r"^def (test_\w+)", t.read_text(encoding="utf-8"),
                                  re.M))
    v["N_TESTS"] = str(n_tests)


def _add_config_tokens(v: dict) -> None:
    """Bind the experiment configuration to tokens.

    The seed and the bootstrap count are the two numbers a reader needs in
    order to reproduce a run, and they belong to the configuration rather
    than to any one result file. The thresholds and the pool sizes are
    bound the same way, so the prose can never name a threshold the code
    does not use.
    """
    try:
        sys.path.insert(0, str(ROOT / "impl"))
        from src.config import CONFIG as _cfg  # noqa: PLC0415
        v["SEED"] = str(_cfg.experiment.seed)
        v["N_BOOTSTRAP"] = f"{_cfg.experiment.n_bootstrap:,}"
        v["RERANK_TOP_N"] = str(_cfg.rerank.top_n)
        v["RERANK_TOP_K_FINAL"] = str(_cfg.rerank.top_k_final)
        v["RERANK_TOP_K_LEXICAL"] = str(_cfg.fusion.lexical_top_k)
        v["RERANK_TOP_K_DENSE"] = str(_cfg.fusion.dense_top_k)
        v["RRF_K"] = str(_cfg.fusion.rrf_k)
        v["CLAIM_GROUNDED_THRESHOLD"] = f"{_cfg.claim.grounded_threshold:.2f}"
        v["CLAIM_INFERRED_THRESHOLD"] = f"{_cfg.claim.inferred_threshold:.2f}"
        v["CONTRA_NLI_THRESHOLD"] = f"{_cfg.contradiction.nli_threshold:.2f}"
        v["CONTRA_TOPIC_THRESHOLD"] = f"{_cfg.contradiction.topic_threshold:.2f}"
        v["CONTRA_ENTITY_OVERLAP_MIN"] = \
            f"{_cfg.contradiction.entity_overlap_min:.2f}"
        v["QUOTA_MIN_TABLE_SHARE"] = f"{_cfg.modality.min_table_share:.2f}"
        v["QUOTA_MIN_CHART_SHARE"] = f"{_cfg.modality.min_chart_share:.2f}"
        v["QUOTA_DEPTH"] = str(_cfg.modality.quota_depth)
        v["BM25_K1"] = f"{_cfg.lexical.k1:.1f}"
        v["BM25_B"] = f"{_cfg.lexical.b:.2f}"
    except Exception:
        v.setdefault("SEED", "20261118")
        v.setdefault("N_BOOTSTRAP", "10,000")


def _add_gate_calibration_tokens(v: dict) -> None:
    """Bind the gate's calibration quality to tokens.

    A calibrated probability that is not calibrated is a number without
    meaning, so the Brier score and the expected calibration error belong
    next to the operating point wherever it is quoted.
    """
    for path in (ROOT / "impl" / "results_focus" / "exp2_gate.json",
                 ROOT / "impl" / "results" / "exp2_gate.json"):
        if not path.exists():
            continue
        d = json.loads(path.read_text(encoding="utf-8"))
        cal = d.get("calibration_metrics") or {}
        if not cal:
            continue
        v["GATE_BRIER"] = f"{cal.get('brier', float('nan')):.4f}"
        v["GATE_ECE"] = f"{cal.get('ece', float('nan')):.4f}"
        break


def _lc_add_long_context_tokens(v: dict) -> None:
    """Bind the long-context baseline arm's measurements to tokens.

    The cost half of the comparison (how many tokens the whole corpus costs
    against how many the retrieved context costs) and the retrieval-side
    proxy are always available. The quality half needs a generator, and is
    bound only when one was actually run.
    """
    for prefix, directory in (("LC", FOCUS_RESULTS), ("MC_LC", RESULTS)):
        f = directory / "exp7_long_context.json"
        if not f.exists():
            if prefix == "MC_LC":
                # The multi-category run has not been made yet. Say so
                # rather than substituting the focus numbers under a
                # different corpus's label; the consistency check blocks
                # the build on the placeholder.
                for _k in ("CORPUS_TOKENS", "CORPUS_CHUNKS", "RAG_TOKENS",
                           "RAG_CHUNKS", "RATIO", "CORPUS_FRACTION",
                           "PROXY_TOP10", "PROXY_TOP20",
                           "PROXY_MEDIAN_RANK", "PROXY_N", "PROXY_SET_SIZE",
                           "FITS_128K", "FITS_256K", "FITS_1M",
                           "QUALITY_RAN"):
                    v[f"MC_LC_{_k}"] = "[not measured]"
            continue
        data = json.loads(f.read_text(encoding="utf-8")).get("summary", {})
        c = data.get("corpus", {})
        p = data.get("retrieval_proxy", {})
        g = data.get("generative", {})
        if not c:
            continue
        v[f"{prefix}_CORPUS_TOKENS"] = f"{c['corpus_tokens']:,}"
        v[f"{prefix}_CORPUS_CHUNKS"] = str(c["corpus_chunks"])
        v[f"{prefix}_RAG_TOKENS"] = f"{c['rag_context_tokens_mean']:,.0f}"
        v[f"{prefix}_RAG_CHUNKS"] = f"{c['rag_context_chunks_mean']:.1f}"
        v[f"{prefix}_RATIO"] = f"{c['token_ratio_long_over_rag']:.0f}"
        v[f"{prefix}_CORPUS_FRACTION"] = f"{c['corpus_fraction_retrieved'] * 100:.2f}"
        # How many times over a 128K window the corpus is. Hand-written
        # multiples of this went stale when the corpus changed, so the
        # factor is measured here like every other size.
        v[f"{prefix}_CORPUS_VS_128K"] = f"{c['corpus_tokens'] / 131072:.1f}"
        v[f"{prefix}_FITS_128K"] = ("yes" if c["context_window_fits"].get(
            "a 128K-window model (most hosted models)") else "**no**")
        v[f"{prefix}_FITS_256K"] = ("yes" if c["context_window_fits"].get(
            "a 256K-window model") else "**no**")
        v[f"{prefix}_FITS_1M"] = ("yes" if c["context_window_fits"].get(
            "claude-sonnet-4-5 / claude-opus-4-5 (1M)") else "**no**")
        if "gold_in_top10" in p:
            v[f"{prefix}_PROXY_TOP10"] = f"{p['gold_in_top10']:.3f}"
            v[f"{prefix}_PROXY_TOP20"] = f"{p['gold_in_top20']:.3f}"
            v[f"{prefix}_PROXY_MEDIAN_RANK"] = f"{p['median_gold_rank']:.0f}"
            v[f"{prefix}_PROXY_N"] = str(p["n_queries"])
            v[f"{prefix}_PROXY_SET_SIZE"] = f"{p['candidate_set_size']:,}"
            v[f"{prefix}_PROXY_CI"] = (
                f"{p['top10_wilson_low']:.3f}-{p['top10_wilson_high']:.3f}")
            v[f"{prefix}_PROXY_CLAUSE"] = (
                f" The same proxy on the "
                f"{'six-category' if prefix == 'MC_LC' else 'focus-domain'} "
                f"corpus puts the gold chunk in the top 10 for "
                f"{p['gold_in_top10']:.3f} of the queries "
                f"({v[f'{prefix}_PROXY_CI']}), at a median rank of "
                f"{p['median_gold_rank']:.0f}.")
        else:
            # The proxy is still running; the cost half is complete.
            for _k in ("PROXY_TOP10", "PROXY_TOP20", "PROXY_MEDIAN_RANK",
                        "PROXY_N", "PROXY_SET_SIZE", "PROXY_CI"):
                v[f"{prefix}_{_k}"] = "[not measured]"
            # The clause is written so that it still reads as a sentence
            # when the proxy did not finish, rather than leaving a number
            # that was never measured in the middle of the prose.
            v[f"{prefix}_PROXY_CLAUSE"] = (
                " The same proxy on the "
                f"{'six-category' if prefix == 'MC_LC' else 'focus-domain'} "
                "corpus did not finish, so no figure is quoted for it.")
        v[f"{prefix}_QUALITY_RAN"] = "yes" if g.get("ran") else "no"
        if g.get("ran"):
            v[f"{prefix}_MODEL"] = g.get("model", "")
            v[f"{prefix}_ACCURACY"] = f"{g.get('answer_accuracy', float('nan')):.3f}"
            v[f"{prefix}_REFUSAL_RATE"] = f"{g.get('refusal_rate', float('nan')):.3f}"


def _gen_add_generation_tokens(v: dict) -> None:
    """Bind the generator-side comparison (Experiment 8) to tokens.

    The experiment puts one generator behind five arms and asks how often each
    arm answers a question that has no answer. It needs an API credential, so
    the tokens exist in both states: the summary paragraph states either what
    was measured or, when nothing was measured, exactly what is untested.
    """
    conditions = load_generation_conditions()
    payload = conditions.get("cautious")
    ran = bool(payload) and payload.get("status") == "run"
    answering = conditions.get("answering")
    answered = bool(answering) and answering.get("status") == "run"
    v["GEN_RAN"] = "yes" if ran else "no"
    v["GEN_MODEL"] = payload.get("model", "not run") if ran else "not run"
    v["GEN_SUMMARY"] = generation_summary(payload)
    v["GEN_SUMMARY_SHORT"] = generation_summary_short(payload)
    v["GEN_N_ANSWERABLE"] = str(payload.get("n_answerable", 0)) if ran else "0"
    v["GEN_N_UNANSWERABLE"] = str(payload.get("n_unanswerable", 0)) if ran else "0"
    v["GEN_CONDITIONS_RUN"] = ("two" if answered else "one" if ran else "none")
    v["GEN_GATE_OVERALL"] = gate_overall(conditions)

    # The audit of the benchmark's unanswerable half: the finding, and the
    # repair of it.
    _ua = unanswerable_audit_summary(load_unanswerable_audit())
    v["UNANS_AUDIT_RAN"] = "yes" if _ua else "no"
    # The multi-category audit is the better-powered measurement of the
    # same property: 132 answerable questions against the focus domain's 32,
    # so a form-only classifier estimates the shape cells from twice the
    # data and its score is less inflated by the small sample.
    _ua_mc = unanswerable_audit_summary(load_unanswerable_audit("multi"))
    v["UNANS_MC_SEP_AUC"] = (f"{_ua_mc['sep_auc']:.3f}"
                              if _ua_mc.get("sep_auc") is not None
                              else "not measured")
    v["UNANS_MC_SEP_P"] = (f"{_ua_mc['sep_p_value']:.3f}"
                            if _ua_mc.get("sep_p_value") is not None
                            else "not measured")
    v["UNANS_MC_NULL"] = (f"{_ua_mc['sep_null_mean']:.3f}"
                          if _ua_mc.get("sep_null_mean") is not None
                          else "not measured")
    v["UNANS_MC_MATCH"] = (
        f"{_ua_mc['hard_matched']} of {_ua_mc['hard_n']}"
        if _ua_mc.get("hard_n") else "not measured")
    v["UNANS_MC_NEAR_MISS"] = (
        f"{_ua_mc['n_near_miss']} of {_ua_mc['n_certificates_checked']}"
        if _ua_mc.get("n_certificates_checked") else "not measured")
    v["UNANS_MC_CERT_FAILURES"] = (
        f"{_ua_mc['n_certificates_failed']} of {_ua_mc['n_certificates_checked']}"
        if _ua_mc.get("n_certificates_checked") else "not measured")
    # The six-category run is quoted beside the focus-domain one wherever the
    # residual form effect is described, because the two runs do not agree on
    # its significance and quoting only the weaker one would overstate it.
    _mc_txt = ""
    if (_ua_mc.get("sep_auc") is not None
            and _ua_mc.get("sep_null_mean") is not None
            and _ua_mc.get("sep_p_value") is not None):
        _mc_txt = (f"; on the better-powered six-category benchmark, whose "
                   f"answerable class is four times larger, the same "
                   f"measurement gives {_ua_mc['sep_auc']:.3f} against a "
                   f"permutation null of {_ua_mc['sep_null_mean']:.3f} "
                   f"(p = {_ua_mc['sep_p_value']:.3f})")

    def _f3(key):
        v_ = _ua.get(key)
        return f"{v_:.3f}" if isinstance(v_, (int, float)) else "not measured"

    def _pct(key):
        v_ = _ua.get(key)
        return f"{v_:.1%}" if isinstance(v_, (int, float)) else "not measured"

    v["UNANS_SEP_F1"] = _f3("sep_f1")
    v["UNANS_SEP_AUC"] = _f3("sep_auc")
    v["UNANS_SEP_BASELINE"] = _f3("sep_baseline_f1")
    v["UNANS_SEP_P"] = _f3("sep_p_value")
    v["UNANS_SEP_NULL"] = _f3("sep_null_mean")
    v["UNANS_BEFORE_F1"] = _f3("before_f1")
    v["UNANS_BEFORE_AUC"] = _f3("before_auc")
    v["UNANS_BEFORE_NULL"] = _f3("before_null_mean")
    v["UNANS_BEFORE_NULL_SD"] = _f3("before_null_sd")
    v["UNANS_BOW_AUC"] = _f3("bow_auc")
    v["UNANS_BEFORE_BOW_AUC"] = _f3("before_bow_auc")
    v["UNANS_SEP_LEN"] = (
        f"{_ua['sep_median_len_answerable']:.0f} against "
        f"{_ua['sep_median_len_unanswerable']:.0f} characters"
        if _ua.get("sep_median_len_answerable") is not None
        else "not measured")
    v["UNANS_MATCH_RATE"] = (
        f"{_ua['hard_matched']} of {_ua['hard_n']}"
        if _ua.get("hard_n") else "not measured")
    v["UNANS_HARD_N"] = (str(_ua["hard_n"]) if _ua.get("hard_n")
                         else "not measured")
    v["UNANS_CERT_FAILURES"] = (
        f"{_ua['n_certificates_failed']} of {_ua['n_certificates_checked']}"
        if _ua.get("n_certificates_checked") else "not measured")
    v["UNANS_NEAR_MISS"] = (
        f"{_ua['n_near_miss']} of {_ua['n_certificates_checked']}"
        if _ua.get("n_certificates_checked") else "not measured")
    v["UNANS_CERT_CHECKED"] = (
        str(_ua["n_certificates_checked"])
        if _ua.get("n_certificates_checked") else "not measured")
    v["UNANS_SHORTCUT_BEFORE"] = _pct("shortcut_before")
    v["UNANS_SHORTCUT_AFTER"] = _pct("shortcut_after")
    v["UNANS_POLICY_DETECT"] = _pct("policy_detected")
    v["UNANS_POLICY_COST"] = _pct("policy_cost")
    v["UNANS_POLICY_BEFORE_DETECT"] = _pct("policy_before_detected")
    v["UNANS_POLICY_BEFORE_COST"] = _pct("policy_before_cost")
    v["UNANS_POLICY_AUC"] = _f3("policy_auc")
    v["UNANS_POLICY_BEFORE_AUC"] = _f3("policy_before_auc")
    v["UNANS_LEAKAGE"] = (f"{_ua['leakage_rate']:.3f}"
                           if _ua.get("leakage_rate") is not None
                           else "not measured")
    v["UNANS_LEAKAGE_ANSWERABLE"] = (
        f"{_ua['leakage_answerable_rate']:.3f}"
        if _ua.get("leakage_answerable_rate") is not None else "not measured")
    v["UNANS_CLOSED_BOOK_ACC"] = (
        f"{_ua['closed_book_accuracy_nli']:.3f}"
        if _ua.get("closed_book_accuracy_nli") is not None else "not measured")
    v["UNANS_AUDIT_SENTENCE"] = (
        f"A classifier that sees only the question's *shape* -- its stem, its "
        f"subject size, whether the subject contains a digit, an acronym or a "
        f"fabricated identifier -- tells the answerable questions from the "
        f"unanswerable ones with an ROC AUC of {_ua['sep_auc']:.3f} against a "
        f"permutation null of {_ua['sep_null_mean']:.3f} that the same "
        f"procedure produces on shuffled labels "
        f"(p = {_ua['sep_p_value']:.3f}), against "
        f"{_ua['before_auc']:.3f} before the unanswerable class was rebuilt"
        f"{_mc_txt}"
        if _ua.get("sep_auc") is not None else
        "The unanswerable half has not been audited.")
    v["UNANS_RESIDUAL_CLAIM"] = residual_form_claim(_ua, _ua_mc)

    # The industrial corpus's own audit of its unanswerable half. It was
    # built after the repair, so it has no "before" half; what it has is the
    # two probes the focus corpus's audit ran -- the question-only policy
    # and the parametric-leakage probe -- plus the residual form-only
    # separability of the repaired class.
    _ind_ua = unanswerable_audit_summary(load_unanswerable_audit("industrial"))

    def _ind_f3(key):
        v_ = _ind_ua.get(key)
        return f"{v_:.3f}" if isinstance(v_, (int, float)) else "not measured"

    def _ind_pct(key):
        v_ = _ind_ua.get(key)
        return f"{v_:.1%}" if isinstance(v_, (int, float)) else "not measured"

    if _ind_ua:
        v["IND_AUD_N_ANSWERABLE"] = str(_ind_ua.get("n_answerable") or 0)
        v["IND_AUD_N_UNANSWERABLE"] = str(_ind_ua.get("n_unanswerable") or 0)
        v["IND_AUD_SEP_AUC"] = (_ind_f3("sep_auc") if _ind_ua.get("sep_auc")
                                is not None else "not measured")
        v["IND_AUD_SEP_P"] = (_ind_f3("sep_p_value")
                              if _ind_ua.get("sep_p_value") is not None
                              else "not measured")
        v["IND_AUD_SEP_NULL_MEAN"] = (_ind_f3("sep_null_mean")
                                      if _ind_ua.get("sep_null_mean") is not None
                                      else "not measured")
        v["IND_AUD_BOW_AUC"] = (_ind_f3("bow_auc")
                                if _ind_ua.get("bow_auc") is not None
                                else "not measured")
        v["IND_AUD_BOW_P"] = (_ind_f3("bow_p_value")
                              if _ind_ua.get("bow_p_value") is not None
                              else "not measured")
        v["IND_AUD_MATCH_RATE"] = (_ind_pct("match_rate")
                                    if _ind_ua.get("match_rate") is not None
                                    else "not measured")
        v["IND_AUD_NEAR_MISS"] = str(_ind_ua.get("n_near_miss") or 0)
        v["IND_AUD_CERT_FAILED"] = str(_ind_ua.get("n_certificates_failed") or 0)
        v["IND_AUD_POLICY_AUC"] = (_ind_f3("policy_auc")
                                   if _ind_ua.get("policy_auc") is not None
                                   else "not measured")
        v["IND_AUD_POLICY_DETECT"] = (_ind_pct("policy_detected")
                                      if _ind_ua.get("policy_detected") is not None
                                      else "not measured")
        v["IND_AUD_POLICY_COST"] = (_ind_pct("policy_cost")
                                    if _ind_ua.get("policy_cost") is not None
                                    else "not measured")
        v["IND_AUD_LEAKAGE"] = (_ind_f3("leakage_rate")
                                if _ind_ua.get("leakage_rate") is not None
                                else "not measured")
        v["IND_AUD_LEAKAGE_ANSWERABLE"] = (
            _ind_f3("leakage_answerable_rate")
            if _ind_ua.get("leakage_answerable_rate") is not None
            else "not measured")
        v["IND_AUD_CB_ACC_NLI"] = (_ind_f3("closed_book_accuracy_nli")
                                   if _ind_ua.get("closed_book_accuracy_nli")
                                   is not None else "not measured")
        v["IND_AUD_CB_ACC_KEYTERM"] = (
            _ind_f3("closed_book_accuracy_keyterm")
            if _ind_ua.get("closed_book_accuracy_keyterm") is not None
            else "not measured")
    else:
        for _k in ("IND_AUD_N_ANSWERABLE", "IND_AUD_N_UNANSWERABLE",
                   "IND_AUD_SEP_AUC", "IND_AUD_SEP_P", "IND_AUD_SEP_NULL_MEAN",
                   "IND_AUD_BOW_AUC", "IND_AUD_BOW_P", "IND_AUD_MATCH_RATE",
                   "IND_AUD_NEAR_MISS", "IND_AUD_CERT_FAILED",
                   "IND_AUD_POLICY_AUC", "IND_AUD_POLICY_DETECT",
                   "IND_AUD_POLICY_COST", "IND_AUD_LEAKAGE",
                   "IND_AUD_LEAKAGE_ANSWERABLE", "IND_AUD_CB_ACC_NLI",
                   "IND_AUD_CB_ACC_KEYTERM"):
            v[_k] = "not measured"
    _cost = generation_cost(payload)
    v["GEN_LC_COST_CLAIM"] = generation_cost_claim(payload)
    v["GEN_LC_TOKEN_RATIO"] = (
        f"{_cost['token_ratio_long_over_nogate']:.0f}"
        if _cost.get("token_ratio_long_over_nogate") else "not measured")
    v["GEN_LC_COST_RATIO"] = (
        f"{_cost['cost_ratio_long_over_nogate']:.1f}"
        if _cost.get("cost_ratio_long_over_nogate") else "not measured")
    v["GEN_LC_CACHE_HIT"] = (
        f"{_cost['long_context_cache_hit_rate']:.1%}"
        if _cost.get("long_context_cache_hit_rate") is not None
        else "not measured")
    v["GEN_GATE_CAUTIOUS_VERDICT"] = (
        h21_verdict(payload, "cautious")[1] if ran else "not measured")
    v["GEN_GATE_ANSWERING_VERDICT"] = (
        h21_verdict(answering, "answering")[1] if answered else "not measured")

    if ran:
        v["GEN_FITTED_TAU"] = f"{payload.get('fitted_tau', float('nan')):.2f}"
        v["GEN_TRANSFERRED_TAU"] = f"{payload.get('transferred_tau', float('nan')):.2f}"

    # Per-arm numbers. The short names are used in the token names because
    # the arm names contain characters that do not belong in a token.
    #
    # The arms are reported under BOTH prompt conditions. The cautious
    # condition is the deployed system; the answering condition is the one
    # that measures the gate's own contribution, because a generator that
    # must answer cannot decline on its own and give the gate the credit.
    short = {"rag_nogate": "NOGATE", "rag@fitted": "FITTED",
             "rag@random": "RANDOM", "rag@transferred": "XFER",
             "long_context": "LONGCTX"}

    def _arm_tokens(prefix: str, arm_payload) -> None:
        for arm, name in short.items():
            blk = gen_arm(arm_payload, arm)
            if not blk:
                for _k in ("UNANS_ANSWERED", "UNANS_ANSWER_RATE",
                           "UNANS_HALLUC_RATE", "ANS_ANSWERED",
                           "ANS_ANSWERED_RATE", "ANS_ACCURACY",
                           "ANS_CLAIM_SUPPORT"):
                    v[f"{prefix}{name}_{_k}"] = "not measured"
                continue
            un = blk.get("unanswerable", {})
            an = blk.get("answerable", {})
            v[f"{prefix}{name}_UNANS_ANSWERED"] = (
                f"{un.get('n_answered', 0)} of {un.get('n', 0)}")
            v[f"{prefix}{name}_UNANS_ANSWER_RATE"] = (
                f"{un.get('answer_rate', 0.0):.3f}")
            v[f"{prefix}{name}_UNANS_HALLUC_RATE"] = (
                f"{un.get('claim_hallucination_rate', 0.0):.3f}")
            v[f"{prefix}{name}_ANS_ANSWERED"] = (
                f"{an.get('n_answered', 0)} of {an.get('n', 0)}")
            v[f"{prefix}{name}_ANS_ANSWERED_RATE"] = (
                f"{an.get('n_answered', 0) / an.get('n', 1):.3f}")
            v[f"{prefix}{name}_ANS_ACCURACY"] = (
                f"{an.get('accuracy_nli', 0.0):.3f}")
            v[f"{prefix}{name}_ANS_CLAIM_SUPPORT"] = (
                f"{an.get('claim_support_rate', 0.0):.3f}")

    _arm_tokens("GEN_", payload)
    if answered:
        _arm_tokens("GEN_A_", answering)

    # The verdict on the framework's own hypothesis. It is computed in one
    # place -- results_source.h21_conditional_verdict -- so the guide, the
    # papers, the report and the deck cannot drift apart on the single most
    # consequential sentence in the work.
    v["GEN_H2_1_SHORT"], v["GEN_H2_1_VERDICT"], v["GEN_H2_1_DETAIL"] = (
        h21_conditional_verdict(conditions))
    v["GEN_H2_1_VERDICT_SENTENCE"] = (
        v["GEN_H2_1_VERDICT"][:1].upper() + v["GEN_H2_1_VERDICT"][1:])

    # The paired McNemar cell for every arm of the answering condition, so
    # that a row of a results table carries its own evidence rather than a
    # blank. The counts b and c are the effect size; the p-value is only the
    # evidence against chance.
    if answered:
        _paired = answering.get("paired") or {}
        for _arm, _name in short.items():
            _blocks = _paired.get(_arm) or {}
            for _cls, _cname in (("unanswerable", "UNANS"),
                                 ("answerable", "ANS")):
                _b = _blocks.get(_cls) or {}
                if _b.get("p_value") is None:
                    v[f"GEN_A_{_name}_{_cname}_MCNEMAR"] = "none"
                    continue
                _p = float(_b["p_value"])
                _ps = "< 0.001" if _p < 0.0005 else f"= {_p:.3f}"
                v[f"GEN_A_{_name}_{_cname}_MCNEMAR"] = (
                    f"b = {_b.get('baseline_answered_arm_refused', 0)}, "
                    f"c = {_b.get('baseline_refused_arm_answered', 0)}, "
                    f"p {_ps}")

    # The paired, question-by-question test, for the arms that separate the
    # gate from the random control. On the *answerable* questions it is the
    # decisive comparison: the gate's refusals cost it almost no coverage,
    # while the control's cost it significantly, and that difference is
    # what the confidence score buys.
    if answered:
        for _arm, _pfx in (("rag@fitted", "FITTED"), ("rag@random", "RANDOM")):
            for _set, _sfx in (("unanswerable", "UNANS"), ("answerable", "ANS")):
                _pb = (((answering.get("paired") or {}).get(_arm) or {})
                       .get(_set) or {})
                if _pb.get("p_value") is None:
                    v[f"GEN_PAIRED_{_pfx}_{_sfx}_B"] = "not measured"
                    v[f"GEN_PAIRED_{_pfx}_{_sfx}_C"] = "not measured"
                    v[f"GEN_PAIRED_{_pfx}_{_sfx}_P"] = "not measured"
                    continue
                v[f"GEN_PAIRED_{_pfx}_{_sfx}_B"] = str(
                    _pb.get("baseline_answered_arm_refused", 0))
                v[f"GEN_PAIRED_{_pfx}_{_sfx}_C"] = str(
                    _pb.get("baseline_refused_arm_answered", 0))
                _p = float(_pb["p_value"])
                v[f"GEN_PAIRED_{_pfx}_{_sfx}_P"] = (
                    "< 0.001" if _p < 0.0005 else f"{_p:.3f}")

    # The same paired test under the cautious condition, where the generator
    # is allowed to decline. The verdict is stated under both conditions, and
    # these are the counts behind the second one.
    for _set, _sfx in (("unanswerable", "UNANS"), ("answerable", "ANS")):
        _pb = (((payload.get("paired") or {}).get("rag@fitted") or {})
               .get(_set) or {})
        if _pb.get("p_value") is None:
            continue
        v[f"GEN_PAIRED_CAUTIOUS_{_sfx}_B"] = str(
            _pb.get("baseline_answered_arm_refused", 0))
        v[f"GEN_PAIRED_CAUTIOUS_{_sfx}_C"] = str(
            _pb.get("baseline_refused_arm_answered", 0))
        _p = float(_pb["p_value"])
        v[f"GEN_PAIRED_CAUTIOUS_{_sfx}_P"] = (
            "< 0.001" if _p < 0.0005 else f"{_p:.3f}")

    # The paired, question-by-question effect of the gate under the
    # answering condition. This is the number that shows the gate doing
    # something, because it pairs the same question across the two arms.
    _pr = {}
    if answered:
        _pr = ((answering.get("paired") or {}).get("rag@fitted") or {}).get(
            "unanswerable") or {}
    if _pr.get("p_value") is not None:
        v["GEN_GATE_EFFECT"] = (
            f"the gate refused {_pr.get('baseline_answered_arm_refused', 0)} "
            f"of the questions the ungated arm answered and let through "
            f"{_pr.get('baseline_refused_arm_answered', 0)} of the ones it "
            f"did not (exact McNemar p = {_p_str(_pr['p_value'])}).")
    else:
        v["GEN_GATE_EFFECT"] = "not measured"

    # How much of the answer-accuracy column is the scoring convention
    # rather than the system. The two shipped tests are re-scored on the
    # same shipped answers alongside three conventions from the published
    # benchmarks, so the column's dependence on the choice is measured
    # rather than asserted.
    _avc = load_answer_validation_conventions()
    _avcs = answer_validation_conventions_summary(_avc)
    if not _avcs:
        v["AVC_N_CONVENTIONS"] = "not measured"
        v["AVC_DISAGREEMENT_MIN"] = "not measured"
        v["AVC_DISAGREEMENT_MAX"] = "not measured"
        v["AVC_KAPPA_MIN"] = "not measured"
        v["AVC_KAPPA_MAX"] = "not measured"
        v["AVC_SPREAD_MAX"] = "not measured"
        v["AVC_SPREAD_NOGATE"] = "not measured"
        v["AVC_DEPENDENT_MIN"] = "not measured"
        v["AVC_DEPENDENT_MAX"] = "not measured"
        v["AVC_GATE_SIG"] = "not measured"
        v["AVC_GATE_SIG_OF"] = "not measured"
        v["AVC_GATE_SIG_ANSWERING"] = "not measured"
        v["AVC_LC_SIG_CAUTIOUS"] = "not measured"
        v["AVC_LC_SIG_ANSWERING"] = "not measured"
        v["AVC_CLAIM"] = answer_validation_conventions_claim(_avc)
    else:
        v["AVC_N_CONVENTIONS"] = str(_avcs.get("n_conventions", 5))
        v["AVC_DISAGREEMENT_MIN"] = f"{_avcs.get('disagreement_min', 0) * 100:.0f}%"
        v["AVC_DISAGREEMENT_MAX"] = f"{_avcs.get('disagreement_max', 0) * 100:.0f}%"
        v["AVC_KAPPA_MIN"] = f"{_avcs.get('kappa_min', 0):.2f}"
        v["AVC_KAPPA_MAX"] = f"{_avcs.get('kappa_max', 0):.2f}"
        v["AVC_SPREAD_MAX"] = f"{_avcs.get('spread_max', 0):.2f}"
        _sp_ng = ((_avcs.get("spread_by_arm") or {})
                  .get("cautious/rag_nogate"))
        v["AVC_SPREAD_NOGATE"] = (f"{_sp_ng:.2f}"
                                  if isinstance(_sp_ng, (int, float))
                                  else "not measured")
        v["AVC_DEPENDENT_MIN"] = str(_avcs.get("convention_dependent_min", 0))
        v["AVC_DEPENDENT_MAX"] = str(_avcs.get("convention_dependent_max", 0))
        v["AVC_GATE_SIG"] = str(
            _avcs.get("sig_cautious_rag@fitted_vs_rag_nogate", 0))
        v["AVC_GATE_SIG_OF"] = str(
            _avcs.get("sig_cautious_rag@fitted_vs_rag_nogate_of", 5))
        v["AVC_GATE_SIG_ANSWERING"] = str(
            _avcs.get("sig_answering_rag@fitted_vs_rag_nogate", 0))
        v["AVC_LC_SIG_CAUTIOUS"] = str(
            _avcs.get("sig_cautious_rag_nogate_vs_long_context", 0))
        v["AVC_LC_SIG_ANSWERING"] = str(
            _avcs.get("sig_answering_rag_nogate_vs_long_context", 0))
        v["AVC_CLAIM"] = answer_validation_conventions_claim(_avc)
        # The five levels for one arm, so the prose can show the spread
        # rather than describe it.
        _lv = (_avcs.get("levels") or {}).get("cautious/rag_nogate") or {}
        for _k, _tok in (("nli", "NLI"), ("keyterm", "KEYTERM"),
                         ("squad_nem", "NEM"),
                         ("popqa_containment", "POPQA"),
                         ("squad_f1_mean", "F1")):
            v[f"AVC_CAUTIOUS_NOGATE_{_tok}"] = (
                f"{_lv.get(_k):.3f}" if isinstance(_lv.get(_k), float)
                else "not measured")

    # The gate fitted per retriever, with the frontier as a curve. L10
    # says the calibration is fitted per retriever and asks for the
    # per-retriever threshold; this is that measurement.
    _gpr = gate_per_retriever_summary(load_gate_per_retriever())
    _gpr_per = _gpr.get("per_retriever") or {}

    def _gpr_val(retriever, key, fmt="{:.3f}"):
        v = (_gpr_per.get(retriever) or {}).get(key)
        return fmt.format(v) if isinstance(v, (int, float)) else "not measured"

    def _gpr_xfer(retriever, key, fmt="{:.3f}"):
        v = ((_gpr.get("transfer") or {}).get(retriever) or {}).get(key)
        return fmt.format(v) if isinstance(v, (int, float)) else "not measured"

    for _r, _tok in (("hybrid_rrf_rerank", "HYBRID"),
                     ("bm25_only_rerank", "BM25"),
                     ("dense_only_rerank", "DENSE")):
        v[f"GPR_{_tok}_TAU"] = _gpr_val(_r, "fitted_tau", "{:.2f}")
        v[f"GPR_{_tok}_ANSWERED"] = _gpr_val(_r, "answerable_answered")
        v[f"GPR_{_tok}_REFUSED"] = _gpr_val(_r, "unanswerable_refused")
        v[f"GPR_{_tok}_COVERAGE"] = _gpr_val(_r, "coverage")
        v[f"GPR_{_tok}_BRIER"] = _gpr_val(_r, "brier", "{:.4f}")
        v[f"GPR_{_tok}_ECE"] = _gpr_val(_r, "ece", "{:.4f}")
    # The cross-category transfer, at the tuning half's threshold applied
    # unchanged to the held-out half against the weights refitted there.
    _xfer = load_transfer("exp4_transfer", ["leave_half_out"])
    _lh = ((_xfer or {}).get("leave_half_out") or {})
    _xt = _lh.get("metrics_held_out_transferred") or {}
    _xr = _lh.get("metrics_held_out_refitted") or {}
    for _k, _tok in (("answerable_answered", "ANSWERED"),
                     ("unanswerable_refused", "REFUSED")):
        v[f"XFER_HELD_{_tok}"] = (f"{_xt.get(_k):.3f}"
                                  if isinstance(_xt.get(_k), (int, float))
                                  else "not measured")
        v[f"XFER_HELD_REFIT_{_tok}"] = (f"{_xr.get(_k):.3f}"
                                         if isinstance(_xr.get(_k), (int, float))
                                         else "not measured")
    v["XFER_TAU"] = (f"{_lh.get('tau'):.2f}"
                     if isinstance(_lh.get("tau"), (int, float))
                     else "not measured")
    # The six categories that were built, against the twelve the proposal
    # promised. The counts are the repository's own.
    _scope = scope_summary()
    for _short in ("SCM", "PM", "RE", "QE", "PS", "FL"):
        _blk = _scope.get(_short) or {}
        v[f"SCOPE_{_short}_DOCS"] = str(_blk.get("documents", "not measured"))
        v[f"SCOPE_{_short}_CHUNKS"] = str(_blk.get("chunks", "not measured"))
    # The per-claim band's industrial replication, on answers from a
    # different generator.
    _ind_band = None
    _ib_path = ROOT / "impl" / "results_industrial" / "exp19_claim_band_eval.json"
    if _ib_path.exists():
        try:
            _ind_band = json.loads(_ib_path.read_text(encoding="utf-8"))
        except Exception:
            _ind_band = None
    if _ind_band:
        _ib_bin = _ind_band.get("agreement_binary") or {}
        _ib_k = _ib_bin.get("cohens_kappa")
        _ib_ci = _ib_bin.get("ci95") or []
        v["IND_RO5_KAPPA"] = (f"{_ib_k:.3f}" if isinstance(_ib_k, (int, float))
                              else "not measured")
        v["IND_RO5_KAPPA_CI_LO"] = (f"{_ib_ci[0]:.3f}" if len(_ib_ci) > 0
                                     else "not measured")
        v["IND_RO5_KAPPA_CI_HI"] = (f"{_ib_ci[1]:.3f}" if len(_ib_ci) > 1
                                     else "not measured")
        v["IND_RO5_N_CLAIMS"] = str(_ib_bin.get("n") or "not measured")
    else:
        v["IND_RO5_KAPPA"] = "not measured"
        v["IND_RO5_KAPPA_CI_LO"] = "not measured"
        v["IND_RO5_KAPPA_CI_HI"] = "not measured"
        v["IND_RO5_N_CLAIMS"] = "not measured"
    # The positional comparison's four risk gaps: how much higher the risk
    # is when the first claims of an answer are kept than when the band's
    # `grounded` claims are. Positive means position is the better filter.
    _gaps: list[float] = []
    for _tok, _path, _key in (
        ("RO5_GOLD_BAND_MINUS_FIRST",
         ROOT / "impl" / "results_focus" / "exp17_claim_band_eval.json", "band_minus_first"),
        ("RO5_RETRIEVED_BAND_MINUS_FIRST",
         ROOT / "impl" / "results_focus" / "exp18_claim_band_eval.json", "band_minus_first"),
        ("IND_RO5_GOLD_BAND_MINUS_FIRST",
         ROOT / "impl" / "results_industrial" / "exp21_claim_band_eval_gold.json", "band_minus_first"),
        ("IND_RO5_RETRIEVED_BAND_MINUS_FIRST",
         ROOT / "impl" / "results_industrial" / "exp21_claim_band_eval_retrieved.json", "band_minus_first"),
    ):
        _gap = None
        try:
            _d = json.loads(_path.read_text(encoding="utf-8"))
            _gap = (((_d.get("value_test") or {}).get("comparisons") or {})
                    .get(_key) or {}).get("mean_risk_gap")
        except Exception:
            _gap = None
        v[_tok] = (f"{_gap:+.4f}" if isinstance(_gap, (int, float))
                   else "not measured")
        if isinstance(_gap, (int, float)):
            _gaps.append(float(_gap))

    # Whether the direction of the positional comparison is uniform is a
    # property of the four gaps, not a thing the prose asserts. A
    # re-measurement can turn one of them into a tie, and the sentence has to
    # follow: the claim "the direction replicates in all four" is not true
    # when one of them is zero, however small the other three are.
    _n = len(_gaps)
    _pos = sum(1 for g in _gaps if g > 0)
    _zero = sum(1 for g in _gaps if g == 0)
    _neg = sum(1 for g in _gaps if g < 0)
    _words = {0: "none", 1: "one", 2: "two", 3: "three", 4: "four",
              5: "five", 6: "six"}
    _word = _words.get(_pos, str(_pos))
    _nword = _words.get(_n, str(_n))
    if _n == 0:
        v["RO5_POSITIONAL_DIRECTION_CLAUSE"] = "the direction was not measured"
        v["RO5_POSITIONAL_DIRECTION_PHRASE"] = "no measurement"
        v["RO5_POSITIONAL_DIRECTION_ADVERB"] = "not measured"
        v["RO5_POSITIONAL_DIRECTION_EVIDENCE"] = "the measured direction"
    elif _pos == _n:
        v["RO5_POSITIONAL_DIRECTION_CLAUSE"] = (
            f"the direction replicates in all {_n}")
        v["RO5_POSITIONAL_DIRECTION_PHRASE"] = f"all {_n}"
        v["RO5_POSITIONAL_DIRECTION_ADVERB"] = "uniform"
        v["RO5_POSITIONAL_DIRECTION_EVIDENCE"] = "the uniform direction"
    else:
        _parts = []
        if _zero:
            _parts.append(f"ties in {_zero}" if _zero > 1 else "ties in one")
        if _neg:
            _parts.append(f"reverses in {_neg}" if _neg > 1 else "reverses in one")
        _where = ", ".join(_parts) if _parts else "does not hold everywhere"
        v["RO5_POSITIONAL_DIRECTION_CLAUSE"] = (
            f"the direction replicates in {_word} of the {_nword} and {_where}")
        v["RO5_POSITIONAL_DIRECTION_PHRASE"] = f"{_word} of the {_nword}"
        v["RO5_POSITIONAL_DIRECTION_ADVERB"] = "not uniform"
        v["RO5_POSITIONAL_DIRECTION_EVIDENCE"] = (
            "the direction that replicates")
    v["SCOPE_N_CATEGORIES_PROMISED"] = "12"
    v["SCOPE_N_CATEGORIES_BUILT"] = str(
        _scope.get("n_categories_built", "not measured"))
    v["GPR_TAU_SPREAD"] = (f"{_gpr.get('tau_spread'):.2f}"
                           if isinstance(_gpr.get("tau_spread"), (int, float))
                           else "not measured")
    _sweep_pts = ((_gpr_per.get("hybrid_rrf_rerank") or {}).get("sweep_points"))
    v["GPR_SWEEP_POINTS"] = (str(_sweep_pts) if _sweep_pts
                             else "not measured")
    for _r, _tok in (("bm25_only_rerank", "BM25"),
                     ("dense_only_rerank", "DENSE")):
        v[f"GPR_{_tok}_XFER_ANSWERED"] = _gpr_xfer(
            _r, "transferred_answerable_answered")
        v[f"GPR_{_tok}_XFER_REFUSED"] = _gpr_xfer(
            _r, "transferred_unanswerable_refused")

    # The soft prior against the hard category pre-filter. T1 said the
    # pre-filter's cost was measured but its proposed repair was not.
    _sp = soft_prior_summary(load_soft_prior())
    _sp_per = _sp.get("per_config") or {}
    _sp_soft = _sp.get("best_soft") or {}

    def _sp_val(cfg, key, fmt="{:.4f}"):
        v = (_sp_per.get(cfg) or {}).get(key)
        return fmt.format(v) if isinstance(v, (int, float)) else "not measured"

    for _c, _tok in (("no_category", "NOCAT"), ("hard_filter", "HARD")):
        v[f"SP_{_tok}_R10"] = _sp_val(_c, "recall_at_10")
        v[f"SP_{_tok}_R20"] = _sp_val(_c, "recall_at_20")
        v[f"SP_{_tok}_MRR"] = _sp_val(_c, "mrr")
        v[f"SP_{_tok}_NDCG"] = _sp_val(_c, "ndcg_at_10")
    v["SP_SOFT_NAME"] = _sp.get("best_soft_name") or "not measured"
    v["SP_SOFT_R10"] = (f"{_sp_soft.get('recall_at_10'):.4f}"
                         if isinstance(_sp_soft.get("recall_at_10"), (int, float))
                         else "not measured")
    v["SP_SOFT_R20"] = (f"{_sp_soft.get('recall_at_20'):.4f}"
                         if isinstance(_sp_soft.get("recall_at_20"), (int, float))
                         else "not measured")
    v["SP_SOFT_MRR"] = (f"{_sp_soft.get('mrr'):.4f}"
                         if isinstance(_sp_soft.get("mrr"), (int, float))
                         else "not measured")
    v["SP_SOFT_NDCG"] = (f"{_sp_soft.get('ndcg_at_10'):.4f}"
                         if isinstance(_sp_soft.get("ndcg_at_10"), (int, float))
                         else "not measured")
    v["SP_N_QUERIES"] = str(_sp.get("n_queries") or "not measured")
    v["SP_OUT_OF_CATEGORY_GOLD"] = str(
        _sp.get("n_out_of_category_gold")
        if _sp.get("n_out_of_category_gold") is not None else "not measured")
    _sp_cmp = (_sp.get("comparisons") or {})
    _sp_key = f"hard_filter -> {_sp.get('best_soft_name')}"
    _sp_c = _sp_cmp.get(_sp_key) or {}
    v["SP_SOFT_P"] = (f"{_sp_c.get('p_value'):.4f}"
                      if isinstance(_sp_c.get("p_value"), (int, float))
                      else "not measured")
    v["SP_SOFT_DELTA"] = (f"{_sp_c.get('delta_recall'):+.4f}"
                           if isinstance(_sp_c.get("delta_recall"), (int, float))
                           else "not measured")
    v["SP_SOFT_DELTA_MRR"] = (
        f"{_sp_c.get('delta_mrr'):+.4f}"
        if isinstance(_sp_c.get("delta_mrr"), (int, float))
        else "not measured")
    v["SP_SOFT_MRR_P"] = (
        f"{_sp_c.get('p_value_mrr'):.4f}"
        if isinstance(_sp_c.get("p_value_mrr"), (int, float))
        else "not measured")
    # The hard filter against no category handling at all: what the filter
    # itself is worth on the six-category corpus.
    _sp_nc = _sp_cmp.get("hard_filter -> no_category") or {}
    v["SP_NOCAT_DELTA_MRR"] = (
        f"{_sp_nc.get('delta_mrr'):+.4f}"
        if isinstance(_sp_nc.get("delta_mrr"), (int, float))
        else "not measured")
    v["SP_NOCAT_MRR_P"] = (
        f"{_sp_nc.get('p_value_mrr'):.4f}"
        if isinstance(_sp_nc.get("p_value_mrr"), (int, float))
        else "not measured")
    v["SP_HARD_MINUS_NOCAT_MRR"] = (
        f"{abs(_sp_nc.get('delta_mrr')):.4f}"
        if isinstance(_sp_nc.get("delta_mrr"), (int, float))
        else "not measured")
    v["SP_NOCAT_DELTA_R10"] = (
        f"{_sp_nc.get('delta_recall'):+.4f}"
        if isinstance(_sp_nc.get("delta_recall"), (int, float))
        else "not measured")

    # The replication on a second generator. One generator behind five arms
    # settles the hypothesis for one model, so the same design was run on a
    # different checkpoint: same corpus, same benchmark, same arms, same
    # scorer, same output budget. The claim is computed from the measured
    # sign in results_source, so a replication that came out the other way is
    # reported the other way.
    replication = load_generation_replication()
    _rep_ans = replication.get("answering")
    _rep_cau = replication.get("cautious")
    v["GEN2_RAN"] = "yes" if replication else "no"
    v["GEN2_GENERATORS"] = "two" if replication else "one"
    v["GEN2_GENERATORS_PHRASE"] = ("two generators" if replication
                                   else "one generator")
    v["GEN2_MODEL"] = (((_rep_ans or _rep_cau or {}).get("model")) or "not run")
    v["GEN2_CLAIM"] = generation_replication_claim(replication)
    v["GEN2_CAUTIOUS_CLAIM"] = generation_replication_cautious_claim(replication)
    v["GEN2_SCOPE"] = ("both prompt conditions" if (_rep_ans and _rep_cau)
                       else "the answering condition" if _rep_ans
                       else "the cautious condition" if _rep_cau
                       else "not measured")
    v["GEN2_CLAIM_SHORT"] = (
        f"the same comparison on {v['GEN2_MODEL']} reproduced the gate's "
        f"contribution" if _rep_ans and (
            ((_rep_ans.get("arms") or {}).get("rag@fitted") or {})
            .get("unanswerable", {}).get("answer_rate", 1.0)
            < ((_rep_ans.get("arms") or {}).get("rag_nogate") or {})
            .get("unanswerable", {}).get("answer_rate", 0.0))
        else "the comparison on the second generator is not yet measured")
    if _rep_ans:
        _arm_tokens("GEN2_A_", _rep_ans)
        for _arm, _pfx in (("rag@fitted", "FITTED"), ("rag@random", "RANDOM")):
            for _set, _sfx in (("unanswerable", "UNANS"), ("answerable", "ANS")):
                _pb = (((_rep_ans.get("paired") or {}).get(_arm) or {})
                       .get(_set) or {})
                if _pb.get("p_value") is None:
                    v[f"GEN2_PAIRED_{_pfx}_{_sfx}_B"] = "not measured"
                    v[f"GEN2_PAIRED_{_pfx}_{_sfx}_C"] = "not measured"
                    v[f"GEN2_PAIRED_{_pfx}_{_sfx}_P"] = "not measured"
                    continue
                v[f"GEN2_PAIRED_{_pfx}_{_sfx}_B"] = str(
                    _pb.get("baseline_answered_arm_refused", 0))
                v[f"GEN2_PAIRED_{_pfx}_{_sfx}_C"] = str(
                    _pb.get("baseline_refused_arm_answered", 0))
                _p2 = float(_pb["p_value"])
                v[f"GEN2_PAIRED_{_pfx}_{_sfx}_P"] = (
                    "< 0.001" if _p2 < 0.0005 else f"{_p2:.3f}")
        _pr2 = (((_rep_ans.get("paired") or {}).get("rag@fitted") or {})
                .get("unanswerable") or {})
        if _pr2.get("p_value") is not None:
            v["GEN2_GATE_EFFECT"] = (
                f"the gate refused {_pr2.get('baseline_answered_arm_refused', 0)} "
                f"of the questions the ungated arm answered and let through "
                f"{_pr2.get('baseline_refused_arm_answered', 0)} of the ones it "
                f"did not (exact McNemar p = {_p_str(_pr2['p_value'])}).")
        else:
            v["GEN2_GATE_EFFECT"] = "not measured"
    else:
        for _k in ("UNANS_ANSWERED", "UNANS_ANSWER_RATE",
                   "UNANS_HALLUC_RATE", "ANS_ANSWERED",
                   "ANS_ACCURACY", "ANS_CLAIM_SUPPORT"):
            for _n in ("NOGATE", "FITTED", "RANDOM", "XFER", "LONGCTX"):
                v[f"GEN2_A_{_n}_{_k}"] = "not measured"
        for _pfx in ("FITTED", "RANDOM"):
            for _sfx in ("UNANS", "ANS"):
                v[f"GEN2_PAIRED_{_pfx}_{_sfx}_B"] = "not measured"
                v[f"GEN2_PAIRED_{_pfx}_{_sfx}_C"] = "not measured"
                v[f"GEN2_PAIRED_{_pfx}_{_sfx}_P"] = "not measured"
        v["GEN2_GATE_EFFECT"] = "not measured"

    # Why the replication on a second generator could not be run. The
    # measurement is a result file like any other.
    _gc = load_generator_completion()
    v["GENCOMP_CLAIM"] = generator_completion_claim(_gc)
    v["GENCOMP_SHORT"] = generator_completion_short(_gc)
    v["GENCOMP_BIG_TOKENS"] = str((_gc or {}).get("big_budget_tokens", 4096))
    _gc_sum = (_gc or {}).get("summary") or {}
    # The generator with the most empty completions is the one that blocked
    # the replication; naming it beats saying "a second generator".
    _failing = ""
    _best = -1
    for _m, _s in _gc_sum.items():
        _e = _s.get("n_empty", 0)
        if _e > _best:
            _best, _failing = _e, _m
    v["GENCOMP_FAILING_MODEL"] = _failing or "the second generator"
    _fs = _gc_sum.get(_failing) or {}
    v["GENCOMP_FAILING_EMPTY"] = (
        f"{_fs.get('n_empty', 0)} of {_fs.get('n_questions', 0)}")
    v["GENCOMP_FAILING_EMPTY_N"] = str(_fs.get("n_empty", 0))
    v["GENCOMP_FAILING_EMPTY_TOTAL"] = str(_fs.get("n_questions", 0))
    v["GENCOMP_FAILING_EMPTY_TABLE"] = (
        f"{_fs.get('n_empty_table', 0)} of {_fs.get('n_table', 0)}")
    v["GENCOMP_FAILING_EMPTY_TABLE_N"] = str(_fs.get("n_empty_table", 0))
    v["GENCOMP_FAILING_EMPTY_TABLE_TOTAL"] = str(_fs.get("n_table", 0))
    v["GENCOMP_FAILING_RESCUED"] = str(
        _fs.get("n_rescued_by_bigger_budget", 0))
    v["GENCOMP_FAILING_STILL_EMPTY"] = str(
        _fs.get("n_empty_even_at_big_budget", 0))
    for _i, _m in enumerate(list(_gc_sum.keys()), 1):
        _s = _gc_sum[_m]
        v[f"GENCOMP_MODEL_{_i}"] = _m
        v[f"GENCOMP_{_i}_EMPTY"] = (f"{_s.get('n_empty', 0)} of "
                                    f"{_s.get('n_questions', 0)}")
        v[f"GENCOMP_{_i}_EMPTY_TABLE"] = (f"{_s.get('n_empty_table', 0)} of "
                                          f"{_s.get('n_table', 0)}")
        v[f"GENCOMP_{_i}_EMPTY_CONTROL"] = (f"{_s.get('n_empty_control', 0)} "
                                            f"of {_s.get('n_control', 0)}")
        v[f"GENCOMP_{_i}_STILL_EMPTY"] = str(
            _s.get("n_empty_even_at_big_budget", 0))
        v[f"GENCOMP_{_i}_RESCUED"] = str(
            _s.get("n_rescued_by_bigger_budget", 0))
    for _i in range(1, 5):
        for _k in ("EMPTY", "EMPTY_TABLE", "EMPTY_CONTROL", "STILL_EMPTY",
                   "RESCUED"):
            v.setdefault(f"GENCOMP_{_i}_{_k}", "not measured")
        v.setdefault(f"GENCOMP_MODEL_{_i}", "not measured")

    # Why the generator-side comparison has not produced numbers. The
    # obstacle has changed since this was first written: a credential is now
    # reachable and valid, and what blocks it is the provider's account
    # credit. Saying "no credential" would now be false, and saying nothing
    # would leave a reader guessing.
    _reason = (payload or {}).get("reason") or ""
    v["GEN_BLOCKED_REASON"] = (
        _reason if _reason else
        ("no API credential was reachable from the machine this was measured "
         "on"))
    v["GEN_BLOCKED_SENTENCE"] = (
        (_reason[:1].upper() + _reason[1:].rstrip(".") + ".") if _reason else
        ("No API credential was reachable from the machine this was measured "
         "on."))
    v["GEN_RUNS_WHEN"] = ("the obstacle is removed" if _reason
                          else "a credential is present")

    v["GEN_TEST_STATUS"] = (
        (f"was run with {payload.get('model', 'a generator')} under "
         + ("two prompt conditions" if answered else "one prompt condition"))
        if ran else f"was not run, because {_reason}")
    v["GEN_H2_1_RETRACTION_NOTE"] = (
        "with a generator behind the pipeline that refusal rate turns out to "
        "be largely redundant wherever the generator is permitted to decline, "
        "because the generator declines those questions on its own"
        if ran else
        "which is the only measured evidence bearing on the hypothesis, and "
        "it is a reduction in the opportunity for hallucination rather than a "
        "rate computed on generated text")

    # The three places that state the verdict and then explain what the
    # evidence actually is. In the measured state that explanation is the
    # generator's own refusal behaviour; in the unmeasured state it is the
    # gate's.
    if ran and answered:
        # -- Both prompt conditions ran. The gate's contribution is
        #    conditional on the generator's behaviour, and the deliverable
        #    says so rather than reporting only the half that flatters the
        #    framework or only the half that indicts it.
        v["GEN_LC_OPENING"] = (
            "It does not beat long context on this corpus, and we measured "
            "both halves of that comparison.")
        v["GEN_RMF_LC_ANSWER"] = (
            "You can, and you measured it. On this corpus the whole-corpus "
            "prompt answered the same number of answerable questions as the "
            "pipeline, declined no more of the unanswerable ones, and cost many "
            "times the input. You do not claim long context is worse in "
            "general; you claim that on this corpus it did not win, that the "
            "quality margin is directional rather than statistically "
            "significant once the answers are scored without the length "
            "confound, and that the evidence trail, the per-claim auditability "
            "and the category routing are properties your system has and a "
            "long-context prompt does not.")
        v["GEN_RMF_SLIDE16"] = (
            "**Slide 16** (limitations) — do not rush it. You are conceding "
            "that the gate's contribution depends on the generator behind it, "
            "that the long-context baseline you raised as the biggest threat "
            "to your own work does not beat you on this corpus, and that your "
            "own benchmark carried a label defect you found by auditing it "
            "and repaired. Conceding all three is what makes the rest "
            "credible.")
        v["GEN_RMF_NEXT_1"] = (
            "1. Repeat the generator-side comparison on a generator that "
            "returns text on the table questions, and on the six-category "
            "corpus. One generator behind five arms settles the hypothesis "
            "once; one generator settles it for one model.")
        v["GEN_RMF_PENDING"] = (
            "The comparison was run with MiniMax-M3 under two prompt "
            "conditions, and it is reported in full in the guide's E.7.")
        _h211 = v.get("GEN_H2_1_SHORT", "")
        v["GEN_H2_1_ANTICIPATED"] = (
            ("What the generator-side comparison showed is that the gate's "
             "contribution does not depend on the generator's willingness to "
             "decline -- the hypothesis is " + _h211 + ". What the framework "
             "claims is that the gate is the one component whose behaviour "
             "does not depend on the generator's cooperation: the prompt can "
             "be wrong, and the gate still holds.")
            if _h211.startswith("supported under both") else
            ("What the generator-side comparison showed is that the gate's "
             "contribution depends on the generator behind it -- the "
             "hypothesis is " + _h211 + ". What the framework claims is that "
             "the gate is the one component whose behaviour does not depend "
             "on the generator's cooperation."))
        v["GEN_H2_1_EVIDENCE"] = (
            "The hypothesis was tested under two prompt conditions that differ "
            "by a single sentence, with everything else -- the model, the "
            "questions, the retrieval, the scorer -- held fixed. "
            + v.get("GEN_H2_1_VERDICT", "")
            + " A refusal rate and a hallucination rate on generated text "
            "remain different quantities, and the two are still not "
            "interchangeable in the abstract.")
        v["GEN_H2_1_L14"] = (
            "The generator-side comparison was run under two prompt "
            "conditions, and the hypothesis is "
            + v.get("GEN_H2_1_SHORT", "")
            + ". The claim is established for one generator: "
            + v.get("GENCOMP_SHORT", "")
            + " And a refusal rate and a hallucination rate computed on "
            "generated text are different quantities, so neither is presented "
            "as the other.")
        v["GEN_LC_HEADING"] = (
            "The long-context baseline is measured on cost and on answer "
            "quality; on this corpus it does not win on coverage or cost, and "
            "it does not win significantly on quality either.")
        v["GEN_H2_1_HEADING"] = (
            "The framework's own hypothesis about hallucination was tested "
            "under two prompt conditions, and it is "
            + v.get("GEN_H2_1_SHORT", "") + ".")
        v["GEN_H2_1_BULLET"] = (
            "**The framework's own hypothesis about hallucination was tested "
            "under two prompt conditions, and the answer is "
            + v.get("GEN_H2_1_SHORT", "")
            + ".** H2.1 -- that a code-level, non-bypassable gate reduces "
            "hallucination -- is supported under both, and what the framework "
            "claims is that the gate reduces the rate of answering "
            "unanswerable questions whatever the generator does: it is the one "
            "component whose behaviour does not depend on the generator's "
            "cooperation. What it does not claim is that a refusal rate is a "
            "hallucination rate -- the two are different quantities and "
            "neither is presented as the other. The claim is also "
            "established for one generator: "
            + v.get("GENCOMP_SHORT", ""))
        v["GEN_H2_1_SLIDE7_NOTE"] = (
            "The comparison was run under two prompt conditions, because one "
            "prompt cannot show what the gate does, and the hypothesis is "
            + v.get("GEN_H2_1_SHORT", "")
            + ". Under the cautious prompt the generator is allowed to "
            "decline and the gate is partly redundant with it; under the "
            "answering prompt it has to answer and the gate is what stands "
            "between it and a fabricated answer. I am reporting both, because "
            "the second is the claim and the first is the limit on it.")
        v["GEN_LC_CLAIM_BULLET"] = (
            "Any superiority claim over long-context prompting — we measured "
            "that baseline on answer quality as well as cost, and on this "
            "corpus the whole-corpus prompt did not win on coverage or cost "
            "and did not win significantly on quality.")
    elif ran:
        v["GEN_LC_OPENING"] = (
            "It does not beat long context on this corpus, and we measured "
            "both halves of that comparison.")
        v["GEN_RMF_LC_ANSWER"] = (
            "You can, and you measured it. On this corpus the whole-corpus "
            "prompt answered the same number of answerable questions as the "
            "pipeline, declined no more of the unanswerable ones, and cost many "
            "times the input. You do not claim long context is worse in "
            "general; you claim that on this corpus it did not win, that the "
            "quality margin is directional rather than statistically "
            "significant once the answers are scored without the length "
            "confound, and that the evidence trail, the per-claim auditability "
            "and the category routing are properties your system has and a "
            "long-context prompt does not.")
        v["GEN_RMF_SLIDE16"] = (
            "**Slide 16** (limitations) — do not rush it. You are conceding "
            "that your own hypothesis did not survive its own test, and that "
            "the long-context baseline you raised as the biggest threat to "
            "your own work does not beat you on this corpus. Conceding both is "
            "what makes the rest credible.")
        v["GEN_RMF_NEXT_1"] = (
            "1. Repeat the generator-side comparison with a second generator, "
            "and on the six-category corpus. One generator behind five arms "
            "settles the hypothesis once; one generator settles it for one "
            "model.")
        v["GEN_RMF_PENDING"] = (
            "The comparison was run with MiniMax-M3, and it is reported in "
            "full in the guide's E.7.")
        v["GEN_H2_1_ANTICIPATED"] = (
            "What the generator-side comparison showed is that the gate did "
            "not reduce the rate of answering unanswerable questions: the "
            "generator declines those questions on its own, so the gate's "
            "refusals were largely redundant with the prompt's. What the gate "
            "did change was coverage on the answerable ones, and that is a "
            "cost rather than a benefit.")
        v["GEN_H2_1_EVIDENCE"] = (
            "With a generator behind the pipeline, the refusal rate the "
            "retrieval-side experiments attribute to the gate is largely "
            "redundant: the generator declines those questions on its own. A "
            "refusal rate and a hallucination rate on generated text remain "
            "different quantities, and the two are still not interchangeable "
            "in the abstract.")
        v["GEN_H2_1_L14"] = (
            "The generator-side comparison was run, with one generator behind "
            "five arms, and the hypothesis is not supported: the gate did not "
            "reduce the rate of answering unanswerable questions, because the "
            "generator declines them on its own. A refusal rate and a "
            "hallucination rate computed on generated text are different "
            "quantities, so the claim is to be read as the framework declining "
            "to answer where there is no answer, not as the generated text "
            "being more faithful.")
        v["GEN_LC_HEADING"] = (
            "The long-context baseline is measured on cost and on answer "
            "quality; on this corpus it does not win on coverage or cost, and "
            "it does not win significantly on quality either.")
        v["GEN_H2_1_HEADING"] = (
            "The framework's own hypothesis about hallucination was tested, "
            "with a generator behind the pipeline, and it is not supported.")
        v["GEN_H2_1_BULLET"] = (
            "**The framework's own hypothesis about hallucination was tested "
            "and is not supported.** H2.1 -- that a code-level, "
            "non-bypassable gate reduces hallucination -- does not hold on "
            "this benchmark with this generator: the gate did not reduce the "
            "rate of answering unanswerable questions, because the "
            "generator declines those questions on its own. What the gate did "
            "change was coverage on the answerable ones, and that is a cost "
            "rather than a benefit. The refusal rate the retrieval-side "
            "experiments attribute to the gate is, with a generator behind "
            "the pipeline, mostly the prompt's.")
        v["GEN_H2_1_SLIDE7_NOTE"] = (
            "What the generator-side comparison showed is that the prompt "
            "already produces most of that refusal on its own, so the gate's "
            "marginal contribution is small, and I am reporting that rather "
            "than the larger refusal rate the retrieval-side experiments "
            "attribute to the gate.")
        v["GEN_LC_CLAIM_BULLET"] = (
            "Any superiority claim over long-context prompting — we measured "
            "that baseline on answer quality as well as cost, and on this "
            "corpus the whole-corpus prompt did not win on coverage or cost "
            "and did not win significantly on quality.")
    else:
        v["GEN_LC_OPENING"] = (
            "It does not yet beat long context, and we measure the part of "
            "that we can.")
        v["GEN_RMF_LC_ANSWER"] = (
            "On a 634-chunk corpus you can, and 2026 work reports long-context "
            "beating semantic RAG in manufacturing safety at 26x the token "
            "cost. You do not claim long context is worse. You claim the "
            "evidence trail, the per-claim auditability and the category "
            "routing are properties your system has and a long-context prompt "
            "does not, and that the corresponding baseline has to be run "
            "before any superiority claim.")
        v["GEN_RMF_SLIDE16"] = (
            "**Slide 16** (limitations) — do not rush it. The long-context "
            "baseline being unrun is the strongest thing you can concede, "
            "because you are the one raising it.")
        v["GEN_RMF_NEXT_1"] = (
            "1. Run the generator-side comparison — one generator behind four "
            "arms, scoring every claim against the evidence that arm was "
            "given. The harness is written; it needs an API credential. It "
            "settles H2.1 and the quality half of the long-context comparison "
            "at the same time.")
        v["GEN_RMF_PENDING"] = (
            "The comparison that would settle it is written and waiting on an "
            "API credential.")
        v["GEN_H2_1_ANTICIPATED"] = (
            f"What you measured is the gate's *refusal behaviour* -- at the "
            f"fitted operating point it refuses "
            f"{v.get('UNANSWERABLE_REFUSED_PCT', 'the unanswerable questions')} "
            f"of the unanswerable questions while answering "
            f"{v.get('ANSWERABLE_ANSWERED_PCT', 'the answerable ones')} of the "
            f"answerable ones, where a plain keyword retriever answers every "
            f"unanswerable question. That reduces the **opportunity** for "
            f"hallucination, entirely by declining to answer.")
        v["GEN_H2_1_EVIDENCE"] = (
            "The measured evidence that does exist is the gate's refusal "
            "behaviour, which reduces the *opportunity* for hallucination by "
            "declining to answer; that is not the same quantity as a "
            "hallucination rate measured on generated text, and the two are "
            "not interchangeable in the abstract.")
        v["GEN_H2_1_L14"] = (
            "What is measured is the gate's *refusal behaviour*, which reduces "
            "the **opportunity** for hallucination by declining to answer. A "
            "refusal rate and a hallucination rate computed on generated text "
            "are different quantities and are not interchangeable. The claim "
            "that the framework reduces hallucination should be read as the "
            "framework declining to answer where there is no answer, not as "
            "the generated text being more faithful.")
        v["GEN_LC_HEADING"] = (
            "The long-context baseline is measured on cost, and the cost is "
            "decisive.")
        v["GEN_H2_1_HEADING"] = (
            "The framework's own hypothesis about hallucination is untested, "
            "and the claim it does support is narrower.")
        v["GEN_H2_1_BULLET"] = (
            "**The framework's own hypothesis about hallucination is "
            "untested.** H2.1 -- that a code-level, non-bypassable gate "
            "reduces hallucination -- is not tested. What is measured is the "
            "gate's refusal rate, which is the *opportunity* for "
            "hallucination; a refusal rate and a hallucination rate on "
            "generated text are different quantities, and the work does not "
            "claim the second.")
        v["GEN_H2_1_SLIDE7_NOTE"] = (
            "The measurement I do have is the gate's refusal behaviour — it "
            "declines to answer most of the unanswerable questions — and that "
            "reduces the opportunity for hallucination. It is not the same "
            "quantity as a hallucination rate computed on generated text, and "
            "I am not going to present one as the other.")
        v["GEN_LC_CLAIM_BULLET"] = (
            "Any superiority claim over long-context prompting — we measured "
            "the cost half of that baseline, not the answer quality, so we "
            "claim neither way.")

    # Clauses that depend only on whether a generator was used, not on what
    # it found. The findings themselves are written after the measurement,
    # because a claim must not be written before the number it rests on.
    if ran:
        v["GEN_H2_1_SLIDE_NOTE"] = (
            f"It was tested with {v.get('GEN2_GENERATORS', 'one')} generator"
            f"{'s' if v.get('GEN2_GENERATORS') != 'one' else ''} behind five "
            f"arms, scoring every claim against the evidence that arm was "
            f"shown.")
        v["GEN_LC_QUALITY_STATUS"] = (
            "measured on cost on both corpora and on quality on the focus "
            "domain")
    else:
        v["GEN_H2_1_SLIDE_NOTE"] = (
            "What is measured without a generator is the refusal rate: the "
            "opportunity for hallucination, not a rate on text.")
        v["GEN_LC_QUALITY_STATUS"] = "measured on cost, not on quality"

    # The benchmark's own answer labels. The audit found a defect class in
    # the label generator, the generator was corrected, the benchmark was
    # rebuilt and every experiment was re-measured against it. What the
    # deliverables report now is the residual -- how many labels are still
    # defective -- alongside the pre-repair count, so that the finding
    # stays checkable rather than becoming a story.
    audit_l = load_label_audit()
    if audit_l and audit_l.get("status") == "run":
        _n_def = audit_l.get("n_defective", 0)
        _n_ans = audit_l.get("n_answerable", 0)
        _n_clean = audit_l.get("n_clean", 0)
        _pre = audit_l.get("pre_repair") or {}
        v["AUDIT_DEFECTIVE_N"] = str(_n_def)
        v["AUDIT_ANSWERABLE_N"] = str(_n_ans)
        v["AUDIT_CLEAN_N"] = str(_n_clean)
        v["AUDIT_DEFECTIVE_PCT"] = f"{_n_def / _n_ans:.1%}" if _n_ans else "—"
        v["AUDIT_SCREEN_N"] = str((audit_l.get("screen") or {}).get(
            "n_hits", 0))
        v["AUDIT_CAUSE"] = (
            "a table question that names the column its key came from rather "
            "than the column its answer came from, and a numeric gold that is "
            "a digit prefix of a longer token in the chunk")
        # The precise count is the finding: the conservative screen
        # over-reports, and the precise rules adjudicate each of its hits.
        # The screen's count is the upper bound, and is reported beside it.
        _pre_n = (_pre.get("n_defective_precise")
                  if _pre.get("n_defective_precise") is not None
                  else _pre.get("n_defective"))
        _pre_screen_n = _pre.get("n_defective_screen")
        if _pre_n is not None:
            v["AUDIT_PRE_REPAIR_DEFECTIVE_N"] = str(_pre_n)
            v["AUDIT_PRE_REPAIR_ANSWERABLE_N"] = str(_pre.get("n_answerable", 0))
            v["AUDIT_PRE_REPAIR_DEFECTIVE_PCT"] = (
                f"{_pre_n / _pre['n_answerable']:.1%}"
                if _pre.get("n_answerable") else "—")
            v["AUDIT_PRE_REPAIR_SCREEN_N"] = (
                str(_pre_screen_n) if _pre_screen_n is not None else "—")
            v["AUDIT_REPAIRED"] = "yes"
        else:
            v["AUDIT_PRE_REPAIR_DEFECTIVE_N"] = "—"
            v["AUDIT_PRE_REPAIR_ANSWERABLE_N"] = "—"
            v["AUDIT_PRE_REPAIR_DEFECTIVE_PCT"] = "—"
            v["AUDIT_PRE_REPAIR_SCREEN_N"] = "—"
            v["AUDIT_REPAIRED"] = "no"
        _sig = (audit_l.get("significance") or {}).get("tests") or {}
        if _sig:
            _w = _sig.get("nli_whole_answer") or {}
            _s = _sig.get("nli_first_sentence") or {}
            _k = _sig.get("keyterm_lexical") or {}
            v["AUDIT_P_WHOLE"] = f"{_w.get('p_value', 0):.3f}"
            v["AUDIT_P_FIRST"] = f"{_s.get('p_value', 0):.3f}"
            v["AUDIT_P_KEYTERM"] = f"{_k.get('p_value', 0):.3f}"
            v["AUDIT_SIG_ROBUST"] = (
                "yes" if (_w.get("p_value", 1) <= 0.05
                          and _s.get("p_value", 1) <= 0.05
                          and _k.get("p_value", 1) <= 0.05) else "no")
            # The clause is derived from the p-values rather than written
            # by hand: a hand-written version of this sentence was written
            # backwards once, calling p = 1.000 significant.
            v["AUDIT_SIG_TEXT"] = (
                f"The retrieval arm scored higher than the long-context arm on "
                f"every test, but the margin "
                f"{_significance_clause(_w, _s, _k)}.")
        else:
            v["AUDIT_P_WHOLE"] = v["AUDIT_P_FIRST"] = v["AUDIT_P_KEYTERM"] = "—"
            v["AUDIT_SIG_ROBUST"] = "not tested"
            v["AUDIT_SIG_TEXT"] = ""
    else:
        v["AUDIT_DEFECTIVE_N"] = v["AUDIT_ANSWERABLE_N"] = "—"
        v["AUDIT_CLEAN_N"] = v["AUDIT_DEFECTIVE_PCT"] = "—"
        v["AUDIT_SCREEN_N"] = "—"
        v["AUDIT_CAUSE"] = "not audited"
        v["AUDIT_PRE_REPAIR_DEFECTIVE_N"] = "—"
        v["AUDIT_PRE_REPAIR_ANSWERABLE_N"] = "—"
        v["AUDIT_PRE_REPAIR_DEFECTIVE_PCT"] = "—"
        v["AUDIT_REPAIRED"] = "no"
        v["AUDIT_P_WHOLE"] = v["AUDIT_P_FIRST"] = v["AUDIT_P_KEYTERM"] = "—"
        v["AUDIT_SIG_ROBUST"] = "not tested"
        v["AUDIT_SIG_TEXT"] = ""

    # The audit of the instrument the comparison rests on. Without it the
    # numbers below are unreadable: a hallucination rate means nothing if
    # the scorer cannot tell a supported claim from an unsupported one.
    audit = load_scorer_validation()
    if audit and audit.get("status") == "run":
        v["GEN_SCORER_TRUTH"] = (
            f"{audit.get('n_truth_supported', 0)} of the "
            f"{audit.get('n_truth', 0)} answers the benchmark itself "
            f"considers correct are recognised as supported by the evidence "
            f"that states them")
        v["GEN_SCORER_FAB"] = (
            f"{audit.get('n_fabrication_rejected', 0)} of the "
            f"{audit.get('n_fabrication', 0)} fabricated values are rejected")
        v["GEN_SCORER_FOREIGN"] = (
            f"{audit.get('n_foreign_rejected', 0)} of the "
            f"{audit.get('n_foreign', 0)} values taken from a different "
            f"quantity are rejected")
        v["GEN_SCORER_LIMITS"] = "; ".join(audit.get("known_limits") or [])
    else:
        v["GEN_SCORER_TRUTH"] = "not audited"
        v["GEN_SCORER_FAB"] = "not audited"
        v["GEN_SCORER_FOREIGN"] = "not audited"
        v["GEN_SCORER_LIMITS"] = "not audited"

    # The long-context comparison. Until the generator-side comparison ran,
    # the quality half of it was unmeasured and the thesis carried it as an
    # open threat; with a generator behind the pipeline, it is measured on
    # the focus domain, and the tokens below carry the result in both
    # states. No em-dashes: these values are substituted into the LaTeX
    # papers as well as the Markdown.
    lc = gen_arm(payload, "long_context")
    ng = gen_arm(payload, "rag_nogate")
    if ran and lc and ng:
        lc_an = lc.get("answerable", {})
        ng_an = ng.get("answerable", {})
        lc_un = lc.get("unanswerable", {})
        ng_un = ng.get("unanswerable", {})
        lc_t = (lc.get("tokens") or {}).get("total_input", 0)
        ng_t = (ng.get("tokens") or {}).get("total_input", 0)
        ratio = (lc_t / ng_t) if ng_t else 0.0
        v["GEN_LC_FINDING"] = (
            f"The answer-quality half of the comparison was measured on the "
            f"focus domain. With the whole corpus in the prompt the generator "
            f"answered {lc_an.get('n_answered', 0)} of {lc_an.get('n', 0)} "
            f"answerable questions, the same coverage as the pipeline, and it "
            f"declined the unanswerable questions at a comparable rate "
            f"({lc_un.get('n_answered', 0)} of {lc_un.get('n', 0)} against "
            f"{ng_un.get('n_answered', 0)} of {ng_un.get('n', 0)}), for "
            f"{ratio:.0f} times the input actually sent per query. On coverage "
            f"and on cost the result is settled: the whole-corpus prompt "
            f"declines no more unanswerable questions than the pipeline does "
            f"and costs {ratio:.0f} times as much to do it. On answer quality "
            f"the margin is directional but not statistically significant once "
            f"the answers are scored without the length confound.")
        v["GEN_LC_CLAIM"] = (
            "the comparison is measured, and on this corpus it does not "
            "support a superiority claim for long-context prompting in this "
            "domain")
    else:
        v["GEN_LC_FINDING"] = (
            "The answer-quality half of the comparison was not measured, "
            "because no API credential was reachable from the machine this "
            "was measured on, so no generator could be put behind the "
            "pipeline; we make no claim about long-context answer quality in "
            "either direction.")
        v["GEN_LC_CLAIM"] = ("no superiority claim over long-context prompting "
                              "is made in either direction")

    # The reproducibility claims have to narrow once a generator is in the
    # loop. The harness seeds everything it controls, but the provider's
    # sampling temperature is not seed-controlled, so the generator-side
    # numbers carry sampling noise and a blanket "deterministic given the
    # seeds" would be false.
    if ran:
        v["REPRO_CLAIM"] = (
            "the retrieval-side experiment scripts are deterministic given the "
            "seeds, while the generator-side comparison is not, because the "
            "generator's sampling temperature is provider-determined rather "
            "than seed-controlled; its five arms are therefore compared on "
            "rates over a fixed question set rather than on paired per-question "
            "outcomes")
        v["REPRO_SEEDED_CLAIM"] = (
            "Everything on the retrieval side is seeded; the generator-side "
            "comparison is not, because the provider's sampling temperature is "
            "fixed rather than seed-controlled")
    else:
        v["REPRO_CLAIM"] = ("the experiment scripts are deterministic given "
                            "the seeds")
        v["REPRO_SEEDED_CLAIM"] = "Everything is seeded"


def _add_industrial_tokens(v: dict[str, str]) -> None:
    """The measurements from the industrial (eCFR) corpus.

    The third corpus -- 110 United States federal regulatory documents --
    was built to close RO4, RO5 and RO6. Its numbers are bound to tokens
    here for the same reason the others are: a number written by hand into a
    template is a claim that nobody re-checked, and the one already caught
    that way was a benchmark size that had drifted by 25 queries.

    Every token is optional: a missing artefact leaves the token out rather
    than substituting a zero, so a build that runs before a measurement
    exists fails loudly on the unknown token instead of shipping a lie.
    """
    ind = ROOT / "impl" / "results_industrial"

    bench_path = (ROOT / "impl" / "data" / "benchmark_industrial"
                  / "benchmark.json")
    if bench_path.exists():
        b = json.loads(bench_path.read_text(encoding="utf-8"))
        v["IND_N_QUERIES"] = str(b["n_queries"])
        v["IND_N_ANSWERABLE"] = str(b["n_answerable"])
        v["IND_N_UNANSWERABLE"] = str(b["n_unanswerable"])

    p = ind / "exp1_ablation.json"
    if p.exists():
        cs = json.loads(p.read_text(encoding="utf-8"))["corpus_stats"]
        v["IND_N_CHUNKS"] = f"{cs['n_chunks']:,}"
        v["IND_N_DOCUMENTS"] = str(cs["n_documents"])
        v["IND_N_REGIMES"] = str(cs["n_categories"])

    # The contradiction detector on the industrial corpus. The headline
    # numbers are the *regulatory* profile's: the shipped operations
    # vocabulary matches no measurement a regulation binds on, so the
    # quantity branch cannot fire at all on this corpus.
    p = ind / "exp14_revision_eval.json"
    if p.exists():
        doc = json.loads(p.read_text(encoding="utf-8"))
        prof = doc["profiles"].get("regulatory", {}).get("consensus", {})
        ov = prof.get("overall", {})
        if ov:
            v["IND_RO4_DETECTION"] = f"{ov['precision_any_flag']:.3f}"
            v["IND_RO4_DETECTION_PCT"] = \
                f"{ov['precision_any_flag'] * 100:.1f}%"
            _ci = ov.get("precision_any_flag_ci95") or [0, 0]
            v["IND_RO4_DETECTION_CI_LO"] = f"{_ci[0]:.3f}"
            v["IND_RO4_DETECTION_CI_HI"] = f"{_ci[1]:.3f}"
            v["IND_RO4_TYPING"] = f"{ov['precision_typing']:.3f}"
            _tci = ov.get("precision_typing_ci95") or [0, 0]
            v["IND_RO4_TYPING_CI_LO"] = f"{_tci[0]:.3f}"
            v["IND_RO4_TYPING_CI_HI"] = f"{_tci[1]:.3f}"
            v["IND_RO4_ALARMS"] = str(ov.get("n_flagged"))
        by = prof.get("by_stratum", {})
        if "revision" in by:
            v["IND_RO4_REV_STRATUM"] = \
                f"{by['revision']['precision_any_flag']:.3f}"
        ship = doc["profiles"].get("shipped", {}).get("consensus", {}) \
            .get("overall", {})
        if ship:
            v["IND_RO4_SHIPPED_DETECTION"] = \
                f"{ship['precision_any_flag']:.3f}"
            v["IND_RO4_SHIPPED_TYPING"] = f"{ship['precision_typing']:.3f}"

    # The benchmark's own audit on the industrial corpus.
    p = ind / "exp12_unanswerable_class_audit.json"
    if p.exists():
        a = json.loads(p.read_text(encoding="utf-8"))["after_repair"]
        st = a["structural_separability"]["repaired_whole_class"]
        bw = a["bag_of_words_separability"]["repaired_whole_class"]
        v["IND_AUDIT_STRUCTURAL"] = f"{st['roc_auc']:.3f}"
        v["IND_AUDIT_BOW"] = f"{bw['roc_auc']:.3f}"
        v["IND_AUDIT_NULL_MEAN"] = \
            f"{st['permutation_null_auc_mean']:.3f}"
        v["IND_SHORTCUT_CAUGHT"] = str(
            a["shortcut_diagnostic"]["unanswerable_caught"])
        lp = a["length_profile"]
        v["IND_LEN_ANSWERABLE"] = str(int(lp["median_length_answerable"]))
        v["IND_LEN_UNANSWERABLE"] = str(int(lp["median_length_unanswerable"]))

    # The retrieval ablation on the industrial corpus: the three negative
    # findings that replicated.
    p = ind / "exp1_ablation.json"
    if p.exists():
        comps = json.loads(p.read_text(encoding="utf-8")).get("comparisons", [])
        by_name = {}
        for c in comps:
            by_name.setdefault(c["comparison"], c)
        for token, key in (("BM25_VS_DENSE", "A. bm25_only -> B. dense_only"),
                           ("FUSION_VS_LEXICAL", "A. bm25_only -> C. hybrid_rrf"),
                           ("FILTER_VS_NO_FILTER",
                            "D. hybrid_rrf_rerank -> E. +category_filter"),
                           ("RERANK_VS_NO_RERANK",
                            "C. hybrid_rrf -> D. hybrid_rrf_rerank")):
            c = by_name.get(key)
            if not c:
                continue
            v["IND_" + token + "_DELTA"] = f"{c['delta']:+.3f}"
            v["IND_" + token + "_P"] = f"{c['wilcoxon']['p_value']:.5f}"
            v["IND_" + token + "_N"] = str(c["wilcoxon"]["n"])

    # The candidate-pool sweep on the industrial corpus, which is not
    # saturated: this is where the displacement is measured.
    p = ind / "exp5_pool_size.json"
    if p.exists():
        results = json.loads(p.read_text(encoding="utf-8")).get("results", [])
        by_pool = {r["pool_size"]: r for r in results}
        if 50 in by_pool:
            r = by_pool[50]
            v["IND_POOL_R10_AT_50"] = f"{r['recall@10']:.3f}"
            v["IND_POOL_R20_AT_50"] = f"{r['recall@20']:.3f}"
            v["IND_POOL_DISPLACEMENT"] = f"{r['recall@20'] - r['recall@10']:.4f}"
            v["IND_POOL_DISPLACEMENT_PCT"] = \
                f"{(r['recall@20'] - r['recall@10']) * 100:.2f}%"

    # The rubric x specialisation factorial.
    p = ind / "exp21_rubric_factorial.json"
    if p.exists():
        fact = json.loads(p.read_text(encoding="utf-8"))
        eff = fact.get("effects", {})
        for token, key in (("IND_FACT_RUBRIC_GENERALIST",
                            "rubric_effect_at_generalist"),
                           ("IND_FACT_RUBRIC_SPECIALIST",
                            "rubric_effect_at_specialist"),
                           ("IND_FACT_SPEC_AT_V1", "specialisation_effect_at_v1"),
                           ("IND_FACT_SPEC_AT_V2", "specialisation_effect_at_v2")):
            e = eff.get(key)
            if e:
                v[token] = f"{e['difference']:+.3f}"
        dec = fact.get("decomposition", {})
        for reader in ("generalist", "specialist"):
            d = dec.get(reader)
            if d:
                v[f"IND_FACT_{reader.upper()}_V1_CONFLICTS"] = \
                    str(d["v1_conflicts"])
                v[f"IND_FACT_{reader.upper()}_V2_CONFLICTS"] = \
                    str(d["v2_conflicts"])
                v[f"IND_FACT_{reader.upper()}_MISSED"] = \
                    str(d["v2_only_the_old_rubric_missed"])
                v[f"IND_FACT_{reader.upper()}_MISSED_SHARE"] = \
                    f"{d['share_of_the_new_conflicts_the_old_rubric_missed']:.2f}"

    # The per-claim band on the industrial corpus, on both protocols.
    for prefix, fname in (("GOLD", "exp21_claim_band_eval_gold.json"),
                          ("RETRIEVED", "exp21_claim_band_eval_retrieved.json")):
        p = ind / fname
        if not p.exists():
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        _ag = d.get("agreement_binary", {})
        if "cohens_kappa" in _ag:
            v[f"IND_RO5_{prefix}_KAPPA"] = f"{_ag['cohens_kappa']:.3f}"
            _kci = _ag.get("ci95") or [0, 0]
            v[f"IND_RO5_{prefix}_KAPPA_CI_LO"] = f"{_kci[0]:.3f}"
            v[f"IND_RO5_{prefix}_KAPPA_CI_HI"] = f"{_kci[1]:.3f}"
        for band_name, blk in (d.get("per_band") or {}).items():
            key = band_name.upper()
            v[f"IND_RO5_{prefix}_{key}_ERROR"] = f"{blk['error_rate']:.3f}"
        al = d.get("answer_level") or {}
        if "answers_with_no_wrong_claim_rate" in al:
            v[f"IND_RO5_{prefix}_CLEAN"] = \
                f"{al['answers_with_no_wrong_claim_rate']:.3f}"
            v[f"IND_RO5_{prefix}_CLEAN_PCT"] = \
                f"{al['answers_with_no_wrong_claim_rate'] * 100:.1f}%"
            v[f"IND_RO5_{prefix}_GROUNDED_ONLY"] = \
                f"{al['answers_clean_after_keeping_grounded_only_rate']:.3f}"
            v[f"IND_RO5_{prefix}_GROUNDED_ONLY_PCT"] = \
                f"{al['answers_clean_after_keeping_grounded_only_rate'] * 100:.1f}%"
        if "n_claims_labelled" in d:
            v[f"IND_RO5_{prefix}_N_CLAIMS"] = str(d["n_claims_labelled"])


def _add_ro5_and_gate_tokens(v: dict[str, str]) -> None:
    """The per-claim band on the focus corpus, and both gates' operating points.

    The band is the one mechanism whose *headline* number is a pair rather
    than a single rate, so every number that goes into a sentence about it
    is bound here: the agreement with an independent reference, the error
    rate in each band, the clean-answer rate before and after the filter,
    and the positional comparison that is the evidence for the reading.
    """
    focus = ROOT / "impl" / "results_focus"
    ind = ROOT / "impl" / "results_industrial"

    for prefix, fname in (("GOLD", "exp17_claim_band_eval.json"),
                          ("RETRIEVED", "exp18_claim_band_eval.json")):
        p = focus / fname
        if not p.exists():
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        _ag = d.get("agreement_binary", {})
        if "cohens_kappa" in _ag:
            v[f"RO5_{prefix}_KAPPA"] = f"{_ag['cohens_kappa']:.3f}"
            _kci = _ag.get("ci95") or [0, 0]
            v[f"RO5_{prefix}_KAPPA_CI_LO"] = f"{_kci[0]:.3f}"
            v[f"RO5_{prefix}_KAPPA_CI_HI"] = f"{_kci[1]:.3f}"
        for band_name, blk in (d.get("per_band") or {}).items():
            v[f"RO5_{prefix}_{band_name.upper()}_ERROR"] = \
                f"{blk['error_rate']:.3f}"
            v[f"RO5_{prefix}_{band_name.upper()}_N"] = str(blk.get("n", 0))
        al = d.get("answer_level") or {}
        if "answers_with_no_wrong_claim_rate" in al:
            v[f"RO5_{prefix}_CLEAN_PCT"] = \
                f"{al['answers_with_no_wrong_claim_rate'] * 100:.1f}%"
            v[f"RO5_{prefix}_GROUNDED_ONLY_PCT"] = \
                f"{al['answers_clean_after_keeping_grounded_only_rate'] * 100:.1f}%"
            v[f"RO5_{prefix}_N_ANSWERS"] = str(al.get("n_answers", 0))
        circ = d.get("circularity_audit") or {}
        if "reference_hallucination_rate" in circ:
            v[f"RO5_{prefix}_REFERENCE_HALLUCINATION"] = \
                f"{circ['reference_hallucination_rate']:.3f}"
        # The positional comparison: "keep the first half of the answer" as a
        # baseline for "keep what the band tagged grounded".
        _paired = (d.get("value_test") or {}).get("paired") or {}
        _pos = _paired.get("band_vs_first")
        if _pos:
            v[f"RO5_{prefix}_POSITION_P"] = f"{_pos['wilcoxon_p']:.3f}"
            v[f"RO5_{prefix}_POSITION_DZ"] = f"{_pos['cohens_dz']:+.3f}"
        _conf = (d.get("value_test") or {}).get("position_length_confound") or {}
        if _conf:
            v["RO5_POSITION_LENGTH_RHO"] = \
                f"{_conf['spearman_position_vs_length']:.3f}"
            v["RO5_POSITION_LENGTH_P"] = f"{_conf['p_value']:.4f}"

    # The same four statistics for the industrial replication, so the paper
    # can report all four corpus-and-protocol combinations side by side.
    for prefix, fname in (("GOLD", "exp21_claim_band_eval_gold.json"),
                          ("RETRIEVED", "exp21_claim_band_eval_retrieved.json")):
        p = ind / fname
        if not p.exists():
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        _pos = ((d.get("value_test") or {}).get("paired") or {}).get(
            "band_vs_first")
        if _pos:
            v[f"IND_RO5_{prefix}_POSITION_P"] = f"{_pos['wilcoxon_p']:.3f}"
            v[f"IND_RO5_{prefix}_POSITION_DZ"] = f"{_pos['cohens_dz']:+.3f}"
        al = d.get("answer_level") or {}
        if "n_answers" in al:
            v[f"IND_RO5_{prefix}_N_ANSWERS"] = str(al["n_answers"])

    # Both gates' operating points, so the two corpora can be compared on
    # the same quantities.
    for prefix, path in (("FOCUS", focus / "exp2_gate.json"),
                         ("IND", ind / "exp2_gate.json")):
        if not path.exists():
            continue
        g = json.loads(path.read_text(encoding="utf-8"))
        op = g.get("chosen_operating_point") or {}
        if op:
            v[f"{prefix}_GATE_TAU"] = f"{op['tau']:.2f}"
            v[f"{prefix}_GATE_COVERAGE"] = f"{op['coverage']:.3f}"
            v[f"{prefix}_GATE_ABST_PRECISION"] = \
                f"{op['abstention_precision']:.3f}"
            v[f"{prefix}_GATE_ANSWERABLE_ANSWERED_PCT"] = \
                f"{op['answerable_answered'] * 100:.1f}%"
            v[f"{prefix}_GATE_UNANSWERABLE_REFUSED_PCT"] = \
                f"{op['unanswerable_refused'] * 100:.1f}%"
        cal = g.get("calibration_metrics") or {}
        if "ece" in cal:
            v[f"{prefix}_GATE_ECE"] = f"{cal['ece']:.3f}"
            v[f"{prefix}_GATE_BRIER"] = f"{cal['brier']:.3f}"


def _add_industrial_detail_tokens(v: dict[str, str]) -> None:
    """The remaining industrial numbers the papers quote in prose.

    Split out from `_add_industrial_tokens` because these are the ones the
    journal paper's new section reads: the ablation's absolute recalls, the
    conflict detector's counts, the exhaustive quantity search, and the
    factorial's four cells.
    """
    ind = ROOT / "impl" / "results_industrial"

    p = ind / "exp1_ablation.json"
    if p.exists():
        doc = json.loads(p.read_text(encoding="utf-8"))
        for key, tok in (("A. bm25_only", "IND_BM25_R10"),
                         ("B. dense_only", "IND_DENSE_R10"),
                         ("C. hybrid_rrf", "IND_FUSED_R10"),
                         ("D. hybrid_rrf_rerank", "IND_RERANK_R10"),
                         ("E. +category_filter", "IND_FILTER_R10"),
                         ("F. +quota_pre_rerank", "IND_QUOTA_PRE_R10"),
                         ("G. +quota_post_rerank", "IND_QUOTA_POST_R10")):
            sysd = (doc.get("systems") or {}).get(key)
            if sysd:
                v[tok] = f"{sysd['recall@10']:.4f}"
        cs = doc.get("corpus_stats") or {}
        if "by_modality" in cs:
            v["IND_N_TEXT_CHUNKS"] = f"{cs['by_modality'].get('text', 0):,}"
            v["IND_N_TABLE_CHUNKS"] = f"{cs['by_modality'].get('table', 0):,}"
            v["IND_N_CHART_CHUNKS"] = f"{cs['by_modality'].get('chart', 0):,}"

    p = ind / "exp14_revision_eval.json"
    if p.exists():
        doc = json.loads(p.read_text(encoding="utf-8"))
        v["IND_RO4_PAIRS"] = str(doc.get("n_pairs_annotated", 0))
        ld = doc.get("label_distribution") or {}
        for label, tok in (("supersession", "IND_RO4_N_SUPERSESSION"),
                           ("term_mismatch", "IND_RO4_N_TERM_MISMATCH"),
                           ("no_conflict", "IND_RO4_N_NO_CONFLICT")):
            if label in ld:
                v[tok] = str(ld[label])
        sd = doc.get("stratum_distribution") or {}
        if "revision" in sd:
            v["IND_RO4_REVISION_STRATUM_N"] = str(sd["revision"])
        if "similar" in sd:
            v["IND_RO4_SIMILAR_STRATUM_N"] = str(sd["similar"])
        reg = doc["profiles"].get("regulatory", {}).get("consensus", {})
        ov = reg.get("overall", {})
        if "n_flagged" in ov:
            v["IND_RO4_N_FLAGGED"] = str(ov["n_flagged"])
        if "recall_any_real_problem" in ov:
            v["IND_RO4_RECALL_ANY"] = f"{ov['recall_any_real_problem']:.3f}"
        cons = (doc["profiles"].get("regulatory", {})
                .get("construction_labels", {}).get("overall", {}))
        if "precision_any_flag" in cons:
            v["IND_RO4_CONSTRUCTION_DETECTION"] = \
                f"{cons['precision_any_flag']:.3f}"
            v["IND_RO4_CONSTRUCTION_TYPING"] = \
                f"{cons['precision_typing']:.3f}"

    p = ind / "exp20_quantity_stratum.json"
    if p.exists():
        q = json.loads(p.read_text(encoding="utf-8"))
        for key, tok in (("n_measurement_terms", "IND_QTY_TERMS"),
                         ("n_cross_document_conflicts", "IND_QTY_CANDIDATES"),
                         ("n_pairs_scored", "IND_QTY_SCORED"),
                         ("n_pairs_the_quantity_branch_fired_on",
                          "IND_QTY_FIRED"),
                         ("n_pairs_in_the_judge_sheet", "IND_QTY_JUDGED")):
            if key in q:
                v[tok] = str(q[key])

    p = ind / "exp21_rubric_factorial.json"
    if p.exists():
        cells = json.loads(p.read_text(encoding="utf-8")).get("cells", {})
        for name, tok in (("generalist_v1", "IND_FACT_G_V1"),
                          ("generalist_v2", "IND_FACT_G_V2"),
                          ("specialist_v1", "IND_FACT_S_V1"),
                          ("specialist_v2", "IND_FACT_S_V2")):
            c = cells.get(name, {}).get("consensus", {})
            if c:
                v[tok + "_DET"] = f"{c['detection_precision']:.3f}"
                v[tok + "_TYP"] = f"{c['typing_precision']:.3f}"
                v[tok + "_N_FLAGGED"] = str(c.get("n_flagged", 0))
                v[tok + "_N_PAIRS"] = str(c.get("n_pairs_total", 0))

    # The size of the revision corpus the candidate pairs were mined from.
    p = ind / "exp21_revision_corpus_stats.json"
    if p.exists():
        s = json.loads(p.read_text(encoding="utf-8"))
        v["IND_REV_PAIRS"] = str(s["n_amended_paragraph_pairs"])
        v["IND_REV_NUMERIC"] = str(s["n_pairs_stating_different_numbers"])
        v["IND_REV_NUMERIC_PCT"] = \
            f"{s['share_stating_different_numbers'] * 100:.1f}%"
        v["IND_REV_PRE_DATE"] = str(s["pre_date"])
        v["IND_REV_POST_DATE"] = str(s["post_date"])


def _add_next_steps_tokens(v: dict[str, str]) -> None:
    """The project's open threads, as tokens.

    One list, shared by the status report, the technical documentation, the
    pre-submission guide and the defence deck; the deck's items used to be a
    different list from the report's, and the two had drifted apart.

    This runs *last*. The items quote the industrial measurements, and a
    token formatted before the industrial tokens exist resolves to "not
    measured" -- which is how three of the nine items rendered as
    "not measured" for a build, silently, in three artefacts at once.
    """
    class _Safe(dict):
        def __missing__(self, key):
            return "not measured"

    _steps = next_steps(load_generation_replication())
    for _i, _st in enumerate(_steps, 1):
        v[f"NEXT_STEP_{_i}"] = _st["long"].format_map(_Safe(v))
        # The short forms are formatted too. They carried no placeholders
        # until the positional comparison's direction became a derived
        # quantity, and a short form that is not formatted ships its
        # placeholder literally.
        v[f"NEXT_STEP_SHORT_{_i}"] = _st["short"].format_map(_Safe(v))
    # The list itself, as one token. The number of items is not fixed: the
    # quota's own item is in the list only while the system ships the
    # placement the ablation ranks second, so it leaves the list when the
    # placement is corrected and comes back if it is reverted. A template
    # that held the items positionally would have to be edited every time
    # the list changed, and a template edited for the wrong reason is how a
    # list drifts. The deck already renders the list from the data; these
    # two tokens let the documents do the same.
    v["NEXT_STEPS_LIST"] = "\n".join(
        f"{_i}. {_st['long'].format_map(_Safe(v))}"
        for _i, _st in enumerate(_steps, 1))
    v["NEXT_STEPS_SHORT_LIST"] = "\n".join(
        f"{_i}. {_st['short'].format_map(_Safe(v))}"
        for _i, _st in enumerate(_steps, 1))
    v["NEXT_STEPS_COUNT"] = str(len(_steps))
    v["NEXT_STEPS_COUNT_WORD"] = {
        1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six",
        7: "seven", 8: "eight", 9: "nine", 10: "ten", 11: "eleven",
        12: "twelve", 13: "thirteen",
    }.get(len(_steps), str(len(_steps)))


def _quota_placement_comparison() -> tuple[str, str, str]:
    """The corpus-by-corpus comparison of the two quota placements.

    The ablation measures both placements on every corpus that runs it, and
    the ranking is not the same on all of them, so the limitation has to say
    which corpus prefers which rather than assert one rule everywhere. Every
    number comes from the ablation's own F-versus-G comparison; none of it is
    written by hand.

    Returns the direction (one clause per corpus), the significance, and a
    compact form of the claim for the abstracts and the conclusions.
    """
    corpora = (
        ("the focus domain", FOCUS_RESULTS),
        ("the six-category corpus", RESULTS),
        ("the industrial corpus", ROOT / "impl" / "results_industrial"),
    )
    parts = []
    for label, d in corpora:
        f = d / "exp1_ablation.json"
        if not f.exists():
            continue
        doc = json.loads(f.read_text(encoding="utf-8"))
        systems = doc.get("systems") or {}
        pre = (systems.get("F. +quota_pre_rerank") or {}).get("recall@10")
        post = (systems.get("G. +quota_post_rerank") or {}).get("recall@10")
        if pre is None or post is None:
            continue
        p = None
        for c in doc.get("comparisons", []):
            if c.get("comparison") == "F. +quota_pre_rerank -> G. +quota_post_rerank":
                p = (c.get("wilcoxon") or {}).get("p_value")
                break
        parts.append((label, pre, post, p))

    if not parts:
        return ("", "", "")

    clauses = []
    ps = []
    for label, pre, post, p in parts:
        ptxt = f" (p = {p:.3f})" if p is not None else ""
        if pre > post:
            clause = (f"on {label} the before-the-reranker placement reaches "
                      f"{pre:.3f} Recall@10 against {post:.3f} after it{ptxt}")
        elif post > pre:
            clause = (f"on {label} the order reverses, the "
                      f"after-the-reranker placement reaching {post:.3f} "
                      f"Recall@10 against {pre:.3f} before it{ptxt}")
        else:
            clause = (f"on {label} the two placements tie at {pre:.3f} "
                      f"Recall@10{ptxt}")
        clauses.append(clause)
        if p is not None:
            ps.append(p)

    direction = "; ".join(clauses) + "."
    if ps and all(p >= 0.05 for p in ps):
        significance = ("None of these differences is statistically "
                        "significant at the 0.05 level (p = "
                        + ", ".join(f"{p:.3f}" for p in ps)
                        + " respectively).")
    elif ps:
        significance = ("The paired tests give p = "
                        + ", ".join(f"{p:.3f}" for p in ps) + " respectively.")
    else:
        significance = ""

    # The compact form, for the abstracts and the conclusions: which corpus
    # prefers which placement, and by how much where they disagree.
    pre_labels = [label for label, pre, post, _p in parts if pre > post]
    post_labels = [label for label, pre, post, _p in parts if post > pre]
    # The margin on the corpus that reverses the ordering, not the largest
    # margin overall -- the point of the sentence is how small the reversal
    # is.
    reversal_gap = max(
        (abs(pre - post) * 100 for label, pre, post, _p in parts
         if post > pre), default=0.0)

    def _join(labels: list[str]) -> str:
        if not labels:
            return ""
        if len(labels) == 1:
            return labels[0]
        return ", ".join(labels[:-1]) + " and " + labels[-1]

    if pre_labels and not post_labels:
        claim = ("on every corpus that measures it, it belongs before the "
                 "cross-encoder rather than after it")
    elif post_labels and not pre_labels:
        claim = ("on every corpus that measures it, it belongs after the "
                 "cross-encoder rather than before it")
    else:
        claim = (f"on {_join(pre_labels)} it belongs before the cross-encoder "
                 f"rather than after it, while on {_join(post_labels)} the "
                 f"ordering reverses by {reversal_gap:.1f} points of Recall@10")
    return (direction, significance, claim)


#: The results that sit on the retrieval. The list lives in
#: `results_source`, because the limitation's disclosure and the check
#: that guards it have to read the same one.
PLACEMENT_STAMPED_RESULTS = _PLACEMENT_STAMPED_RESULTS


def _placement_provenance() -> tuple[str, str]:
    """Which results that sit on the retrieval are on the shipped placement.

    The measurement scripts stamp the placement they ran under into the file
    they write, so this reads the stamps rather than being told. It returns
    the clause for the results that are current and the clause for the ones
    that are not, so the limitation can name the gap instead of implying it
    is absent.
    """
    from results_source import shipped_quota_position

    shipped = shipped_quota_position()
    current, stale = [], []
    for entry in PLACEMENT_STAMPED_RESULTS:
        label, path = entry[0], entry[1]
        note = entry[2] if len(entry) > 2 else None
        if not path.exists():
            continue
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        placement = doc.get("retrieval_placement")
        if placement is None:
            # No stamp: the file predates the stamp, so it was measured
            # under the placement the system shipped then.
            placement = "post_rerank"
        if placement == shipped:
            current.append(label)
        else:
            stale.append((label, note))

    stale_labels = [label for label, _ in stale]

    def _join(labels: list[str]) -> str:
        if not labels:
            return ""
        if len(labels) == 1:
            return labels[0]
        return ", ".join(labels[:-1]) + " and " + labels[-1]

    def _agree(labels: list[str], singular: str, plural: str) -> str:
        return singular if len(labels) == 1 else plural

    if not stale:
        if not current:
            return ("no generator-side result was available.",
                    "no generator-side result was available to re-take")
        return (f"All {len(current)} of the measurements the deliverables "
                f"quote that depend on the retrieval were re-measured with "
                f"the new placement.",
                "every measurement that depends on the retrieval was re-taken "
                "with it")

    # The scope clause says why each exception is an exception, because the
    # reasons differ: a reader-panel measurement cannot be reproduced, while
    # a measurement that simply has not been re-taken yet is a gap in the
    # work rather than a property of the instrument.
    reasons = []
    panel = [label for label, note in stale if note]
    other = [label for label, note in stale if not note]
    if other:
        reasons.append(f"{_join(other)}, which "
                       f"{_agree(other, 'has', 'have')} not been re-taken")
    if panel:
        reasons.append(
            f"{_join(panel)}, whose labels come from a panel of reader agents "
            f"under a written protocol and could not be reproduced")
    scope = ("the measurements that depend on the retrieval were re-taken "
             "with it, apart from " + ", and ".join(reasons))

    n_total = len(current) + len(stale)
    if not current:
        return (f"None of the {n_total} measurements the deliverables quote "
                f"that depend on the retrieval was re-measured with the new "
                f"placement: {_join(stale_labels)} "
                f"{_agree(stale_labels, 'was', 'were')} taken under the earlier "
                f"placement and {_agree(stale_labels, 'is', 'are')} the "
                f"measurements this limitation covers.", scope)
    # The exceptions are named; the ones that were re-measured are counted
    # rather than enumerated, because a table cell that lists thirty
    # confirmations says less than one that names the two that are not
    # confirmed -- and the count is what makes the coverage visible.
    return (f"{len(current)} of the {n_total} measurements the deliverables "
            f"quote that depend on the retrieval were re-measured with the "
            f"new placement, while {_join(stale_labels)} "
            f"{_agree(stale_labels, 'was', 'were')} taken under the earlier "
            f"placement and {_agree(stale_labels, 'is', 'are')} the "
            f"measurements this limitation covers.", scope)


def _add_quota_placement_tokens(v: dict[str, str]) -> None:
    """The limitation row about where the quota is applied.

    The ablation ranks the pre-rerank placement better. When the system ships
    the other one, that has to be stated plainly -- and when it ships the
    recommended one, the limitation is gone and what remains is a note about
    comparability. Both variants are read from the configuration, so neither
    can drift from what the code does.
    """
    from results_source import shipped_quota_position

    pos = shipped_quota_position()
    v["SHIPPED_QUOTA_PLACEMENT"] = {
        "pre_rerank": "before the cross-encoder",
        "post_rerank": "after the cross-encoder",
    }.get(pos, "in the pipeline's configured position")
    direction, significance, claim = _quota_placement_comparison()
    v["QUOTA_PLACEMENT_DIRECTION"] = direction
    v["QUOTA_PLACEMENT_SIGNIFICANCE"] = significance
    v["QUOTA_PLACEMENT_CLAIM"] = claim
    current_clause, stale_clause = _placement_provenance()
    v["PLACEMENT_PROVENANCE"] = current_clause
    v["PLACEMENT_SCOPE"] = stale_clause
    if pos == "post_rerank":
        v["QUOTA_PLACEMENT_LIMITATION_ROW"] = (
            "| **L20** | **The shipped system applies the modality quota "
            "*after* the reranker, and the ablation says it belongs before.** "
            "The measurement is unambiguous on the focus domain -- the "
            "pre-rerank quota moves overall Recall@10 by {{QUOTA_PRE_DELTA}} "
            "against {{QUOTA_POST_DELTA}} for the shipped placement -- and the "
            "six-category corpus agrees. The system was built with the after "
            "placement, it is what the code's default still does, and every "
            "measurement in this thesis was taken with it | Every "
            "retrieval-side measurement therefore sits on a configuration the "
            "thesis's own ablation ranks second, and the cost is not uniform: "
            "on the focus domain the shipped placement gives up "
            "{{QUOTA_POST_COST_PP}} points of Recall@10 against no quota at "
            "all, where the earlier placement would have gained them. The "
            "gate's calibration, the generator-side comparison and the "
            "per-claim results would all have to be re-measured together if "
            "it moved, which is why it was not moved five days before the "
            "defence | Moving the quota before the reranker and re-measuring "
            "everything that depends on it. It is the first item in the "
            "next-steps list, and it is the one place where this project knows "
            "its own shipped configuration is not the one it recommends |")
    elif pos == "pre_rerank":
        v["QUOTA_PLACEMENT_LIMITATION_ROW"] = (
            "| **L20** | **The shipped quota placement was changed on 16 "
            "November 2026, and the ablation's ranking of the two placements "
            "is not the same on every corpus.** The system now applies the "
            "quota *before* the cross-encoder; it shipped the other "
            "placement until then, because that was the September 2026 design "
            "and moving it invalidates the gate's calibration, the "
            "generator-side comparison and the per-claim results together. "
            "The ablation's own comparison of the two placements is: "
            "{{QUOTA_PLACEMENT_DIRECTION}} **{{QUOTA_PLACEMENT_SIGNIFICANCE}}** | "
            "The placement's effect is small everywhere and its direction is "
            "not uniform, so the shipped default is the focus domain's "
            "preference -- the largest of the differences -- rather than a "
            "rule the evidence settles. The ablation's own numbers did not "
            "move: it measures the two placements as a variable, so "
            "re-running it reproduced every rung exactly, on both Wikipedia "
            "corpora. What did move is everything that runs through the "
            "shipped retrieval -- the gate's calibration above all. "
            "{{PLACEMENT_PROVENANCE}} | Re-measure the placement on "
            "any corpus it is moved for, in the same pass as everything that "
            "depends on it |")
    else:
        v["QUOTA_PLACEMENT_LIMITATION_ROW"] = ""

def _add_effect_size_tokens(v: dict[str, str]) -> None:
    """The effect sizes behind the headline retrieval comparisons.

    A p-value says a difference is unlikely to be chance; the effect size
    says how large it is. A master's-level account reports both, and the
    numbers come from the same archived comparison as the p-value.
    """
    path = FOCUS_RESULTS / "exp1_ablation.json"
    if not path.exists():
        return
    doc = json.loads(path.read_text(encoding="utf-8"))
    for c in doc.get("comparisons", []):
        name = c.get("comparison")
        if name == "A. bm25_only -> B. dense_only":
            w = c.get("wilcoxon") or {}
            if w.get("effect_size") is not None:
                v["ABL_DZ_AB"] = f"{abs(float(w['effect_size'])):.2f}"
            if c.get("cliffs_delta") is not None:
                v["ABL_CD_AB"] = f"{abs(float(c['cliffs_delta'])):.2f}"
        elif name == "B. dense_only -> C. hybrid_rrf":
            w = c.get("wilcoxon") or {}
            if w.get("effect_size") is not None:
                v["ABL_DZ_BC"] = f"{abs(float(w['effect_size'])):.2f}"
            if c.get("cliffs_delta") is not None:
                v["ABL_CD_BC"] = f"{abs(float(c['cliffs_delta'])):.2f}"


def _add_focus_pool_tokens(v: dict[str, str]) -> None:
    """The candidate-pool sweep on the supply-chain focus corpus.

    The pool curve is reported for three corpora and they disagree about
    where it peaks, so each corpus keeps its own numbers. The plain POOL
    tokens carry the six-category corpus; these carry the focus corpus, and
    the industrial corpus has its own IND_POOL tokens.
    """
    path = FOCUS_RESULTS / "exp5_pool_size.json"
    if not path.exists():
        return
    results = json.loads(path.read_text(encoding="utf-8")).get("results", [])
    for r in results:
        v[f"FOCUS_POOL_R10_AT_{int(r['pool_size'])}"] = f"{r['recall@10']:.3f}"
        v[f"FOCUS_POOL_R20_AT_{int(r['pool_size'])}"] = f"{r['recall@20']:.3f}"
    if results:
        peak = max(results, key=lambda r: r["recall@10"])
        v["FOCUS_POOL_PEAK"] = str(int(peak["pool_size"]))
        v["FOCUS_POOL_PEAK_R10"] = f"{peak['recall@10']:.3f}"



def _add_latency_tokens(v: dict[str, str]) -> None:
    """How long a query takes, stage by stage, and what a refusal costs.

    The retrieval path is measured directly, by `run_latency.py`, on the real
    index with the real models: the query embedding, the dense leg, the
    lexical leg, the rank fusion, the modality quota, the cross-encoder
    rerank, and the gate. The generation stage is not measured there,
    because it calls a language model over the network; it is derived from
    the archived arm totals, which are the retrieval path plus the model
    calls, and the retrieval path is what the latency run measures.

    The derivation is an upper bound on the generation time, because the
    archived arm totals also carry the offline claim-scoring pass, which a
    user never waits for.
    """
    lat_path = FOCUS_RESULTS / "exp23_latency.json"
    if not lat_path.exists():
        return
    lat = json.loads(lat_path.read_text(encoding="utf-8"))
    total = lat["total"]
    stages = lat["stages"]

    v["LAT_TOTAL_MEAN_MS"] = f"{total['mean_ms']:.0f}"
    v["LAT_TOTAL_MEDIAN_MS"] = f"{total['median_ms']:.0f}"
    v["LAT_TOTAL_P95_MS"] = f"{total['p95_ms']:.0f}"
    v["LAT_TOTAL_MAX_MS"] = f"{total['max_ms']:.0f}"
    v["LAT_RERANK_MS"] = f"{stages['rerank']['mean_ms']:.0f}"
    v["LAT_EMBED_MS"] = f"{stages['embed']['mean_ms']:.1f}"
    v["LAT_DENSE_MS"] = f"{stages['dense_top_k']['mean_ms']:.1f}"
    v["LAT_BM25_MS"] = f"{stages['bm25']['mean_ms']:.1f}"
    v["LAT_GATE_REFUSED_N"] = str(lat["gate_refused"]["n_refused"])
    v["LAT_N_QUERIES"] = str(lat["n_queries"])

    # The retrieval path, in seconds, which is what a refusal costs.
    r = total["mean_ms"] / 1000.0
    v["LAT_RETRIEVAL_S"] = f"{r:.2f}"
    v["LAT_REFUSAL_S"] = f"{r:.2f}"
    nq = lat["n_queries"]

    # The generation stage, derived from the archived arm totals.
    gens: list[float] = []
    for name, cond in (("exp8_generation.json", "CAUTIOUS"),
                       ("exp8_generation_answering.json", "ANSWERING")):
        path = FOCUS_RESULTS / name
        if not path.exists():
            continue
        doc = json.loads(path.read_text(encoding="utf-8"))
        for arm, block in (doc.get("arms") or {}).items():
            if arm == "long_context":
                continue
            total_s = block.get("seconds")
            answered = (block.get("answerable", {}).get("n_answered", 0)
                        + block.get("unanswerable", {}).get("n_answered", 0))
            if not total_s or not answered:
                continue
            gen = (total_s - nq * r) / answered
            gens.append(gen)
            key = arm.replace("@", "_").replace(".", "_").upper()
            v[f"GEN_S_PER_ANSWER_{key}_{cond}"] = f"{gen:.1f}"
    if gens:
        v["GEN_S_PER_ANSWER_MIN"] = f"{min(gens):.1f}"
        v["GEN_S_PER_ANSWER_MAX"] = f"{max(gens):.1f}"

    # The long-context arm has no retrieval stage at all.
    for name, key in (("exp8_generation.json", "CAUTIOUS"),
                      ("exp8_generation_answering.json", "ANSWERING")):
        path = FOCUS_RESULTS / name
        if not path.exists():
            continue
        doc = json.loads(path.read_text(encoding="utf-8"))
        block = (doc.get("arms") or {}).get("long_context")
        if block and block.get("seconds"):
            v[f"LAT_LONGCTX_S_PER_Q_{key}"] = f"{block['seconds'] / nq:.1f}"


def _add_quota_table_tokens(v: dict[str, str]) -> None:
    """The quota placement table, measured on all three corpora.

    The table says where the modality quota is applied, and the direction
    reverses between corpora. Each row is read from that corpus's own
    ablation, so the recall figures and the p-value in a row come from the
    same comparison and cannot be mixed up.
    """
    runs = (
        ("focus", FOCUS_RESULTS / "exp1_ablation.json"),
        ("sixcat", RESULTS / "exp1_ablation.json"),
        ("ind", ROOT / "impl" / "results_industrial" / "exp1_ablation.json"),
    )
    for name, path in runs:
        if not path.exists():
            continue
        doc = json.loads(path.read_text(encoding="utf-8"))
        systems = doc.get("systems") or {}
        pre = systems.get("F. +quota_pre_rerank")
        post = systems.get("G. +quota_post_rerank")
        if not (pre and post):
            continue
        v[f"QUOTA_PRE_{name.upper()}_R10"] = f"{pre['recall@10']:.3f}"
        v[f"QUOTA_POST_{name.upper()}_R10"] = f"{post['recall@10']:.3f}"
        for c in doc.get("comparisons", []):
            if c.get("comparison") == ("F. +quota_pre_rerank -> "
                                       "G. +quota_post_rerank"):
                v[f"QUOTA_PLACE_{name.upper()}_P"] = (
                    f"{c['wilcoxon']['p_value']:.3f}")
                break


def values() -> dict[str, str]:
    bench = json.loads(BENCH.read_text(encoding="utf-8"))
    v = {
        "N_QUERIES": str(bench["n_queries"]),
        "N_ANSWERABLE": str(bench["n_answerable"]),
        "N_UNANSWERABLE": str(bench["n_unanswerable"]),
    }
    # The multi-category benchmark, for the generalisation study.
    _mc_bench = ROOT / "impl" / "data" / "benchmark" / "benchmark.json"
    if _mc_bench.exists():
        _mb = json.loads(_mc_bench.read_text(encoding="utf-8"))
        v["MC_N_QUERIES"] = str(_mb["n_queries"])
        v["MC_N_ANSWERABLE"] = str(_mb["n_answerable"])
        v["MC_N_UNANSWERABLE"] = str(_mb["n_unanswerable"])
    # The corpus *identity* -- how many documents and chunks, over how many
    # categories -- describes the corpus as a whole, so it comes from the
    # multi-category run. The *composition* and every result come from the
    # focus-domain run, because that is the study the deliverables report.
    p = RESULTS / "exp1_ablation.json"
    if p is not None:
        exp1 = json.loads(p.read_text(encoding="utf-8"))
        cs = exp1["corpus_stats"]
        chunks = f"{cs['n_chunks']:,}"
        v["N_CHUNKS"] = chunks
        v["N_CHUNKS_TEX"] = _tex_number(chunks)
        v["N_DOCUMENTS"] = str(cs["n_documents"])
        _focus_cs = None
        _fp = _first(RESULTS, "exp1_ablation.json")
        if _fp is not None:
            _focus_cs = json.loads(_fp.read_text(encoding="utf-8"))["corpus_stats"]
        _comp = _focus_cs or cs
        for key, share in (
            ("TEXT", _comp["share_text"]),
            ("TABLE", _comp["share_table"]),
            ("CHART", _comp["share_chart"]),
        ):
            pct = f"{share:.1%}"
            v[f"SHARE_{key}"] = pct
            v[f"SHARE_{key}_TEX"] = pct.replace("%", r"\%")
        v["MEAN_WORDS"] = f"{_comp['mean_words_per_chunk']:.0f}"
        if _comp.get("duplicate_chunk_ids") is not None:
            # A duplicated chunk identifier quietly inflates every recall
            # measurement that counts chunks, so the count is reported.
            v["DUP_CHUNK_IDS"] = str(_comp["duplicate_chunk_ids"])
    # The dense encoder's identity, read from the configuration so the
    # prose can never name a model the code does not use.
    try:
        from src.config import CONFIG as _cfg
        v["EMBED_MODEL"] = _cfg.embedding.model
        v["EMBED_DIM"] = str(_cfg.embedding.dim)
        # The LaTeX papers write the model name inside \texttt{...}. The
        # token braces and the command's braces collide -- writing
        # \texttt{{EMBED_MODEL}} leaves the command without its opening
        # brace once the token is substituted, which is a LaTeX error that
        # no structural check catches. The value carries the markup
        # instead, so the template writes {{EMBED_MODEL_TEX}} and nothing
        # else.
        v["EMBED_MODEL_TEX"] = "\\texttt{" + _cfg.embedding.model + "}"
        v["EMBED_FAMILY"] = ("retrieval-trained multilingual encoder"
                             if "bge-m3" in _cfg.embedding.model
                             else "general-purpose sentence encoder")
    except Exception:
        v.setdefault("EMBED_MODEL", "BAAI/bge-m3")
        v.setdefault("EMBED_DIM", "1024")
        v.setdefault("EMBED_MODEL_TEX", "\\texttt{BAAI/bge-m3}")
        v.setdefault("EMBED_FAMILY", "retrieval-trained multilingual encoder")
    _add_result_tokens(v)
    _add_quota_placement_tokens(v)
    _add_quota_table_tokens(v)
    _add_effect_size_tokens(v)
    _add_focus_pool_tokens(v)
    _add_latency_tokens(v)
    _add_baseline_tokens(v)
    if MANIFEST.exists():
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        cats = sorted({d["category"] for d in manifest})
        v["N_CATEGORIES"] = str(len(cats))
        words = {2: "two", 3: "three", 4: "four", 5: "five", 6: "six",
                 7: "seven", 8: "eight", 9: "nine", 10: "ten"}
        v["N_CATEGORIES_WORD"] = words.get(len(cats), str(len(cats)))
    if "R_B" in v and "BASE_F_R_B" in v:
        v["ENCODER_VERDICT"] = _encoder_verdict(v)

    if FOCUS_MANIFEST.exists():
        fm = json.loads(FOCUS_MANIFEST.read_text(encoding="utf-8"))
        v["N_FOCUS_DOCUMENTS"] = str(len(fm))
        if FOCUS_INDEX.exists():
            fi = json.loads(FOCUS_INDEX.read_text(encoding="utf-8"))
            v["N_FOCUS_CHUNKS"] = f"{fi['stats']['n_chunks']:,}"
            v["N_FOCUS_CHUNKS_TEX"] = _tex_number(v["N_FOCUS_CHUNKS"])
            v["FOCUS_SHARE_TEXT"] = f"{fi['stats']['share_text']:.1%}"
        else:
            v["N_FOCUS_CHUNKS"] = "—"
            v["FOCUS_SHARE_TEXT"] = "—"
    if FOCUS_BENCH.exists():
        fb = json.loads(FOCUS_BENCH.read_text(encoding="utf-8"))
        v["N_FOCUS_QUERIES"] = str(fb["n_queries"])
        v["N_FOCUS_ANSWERABLE"] = str(fb["n_answerable"])
        v["N_FOCUS_UNANSWERABLE"] = str(fb["n_unanswerable"])
    _add_industrial_tokens(v)
    _add_industrial_detail_tokens(v)
    _add_ro5_and_gate_tokens(v)
    # The figure captions, so that the markdown deliverables can carry the
    # same six figures with the same wording the papers use.
    for _key, _tok in FIGURE_TOKENS.items():
        v[_tok] = resolve_caption(FIGURES[_key], v)
    # Last: the open threads quote the measurements set above.
    _add_next_steps_tokens(v)
    return v


#: The seven ablation rungs, in order.
RUNGS = [
    ("A", "A. bm25_only"),
    ("B", "B. dense_only"),
    ("C", "C. hybrid_rrf"),
    ("D", "D. hybrid_rrf_rerank"),
    ("E", "E. +category_filter"),
    ("F", "F. +quota_pre_rerank"),
    ("G", "G. +quota_post_rerank"),
]


def _sci_plain(p: float) -> str:
    """3.48e-08 -> '3.5 × 10⁻⁸'."""
    if not p or p <= 0:
        return "0"
    from math import floor, log10
    e = int(floor(log10(p)))
    m = p / (10 ** e)
    sup = str(e).translate(str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻"))
    return f"{m:.1f} × 10{sup}"


def _sci_tex(p: float) -> str:
    """3.48e-08 -> '3.5\\!\\times\\!10^{-8}'."""
    if not p or p <= 0:
        return "0"
    from math import floor, log10
    e = int(floor(log10(p)))
    m = p / (10 ** e)
    return f"{m:.1f}\\!\\times\\!10^{{{e}}}"


def _add_result_tokens(v: dict[str, str]) -> None:
    """Bind the measured results to tokens, so the prose cannot drift.

    Every number the guide and the papers quote about their own experiments
    is substituted from the experiment JSON at build time. A hand-written
    result in a template is a claim that survives the next corpus change
    without changing, which is how the IEEE paper came to describe a
    table-recall rise that the data does not show.
    """
    exp1_path = None
    for _d in (FOCUS_RESULTS, RESULTS):
        _c = _d / "exp1_ablation.json"
        if _c.exists():
            exp1_path = _c
            break
    if exp1_path is None:
        return
    exp1 = json.loads(exp1_path.read_text(encoding="utf-8"))
    systems = exp1["systems"]
    comp = _comp_index(exp1["comparisons"])

    for short, key in RUNGS:
        s = systems[key]
        v[f"R_{short}"] = f"{s['recall@10']:.3f}"
        v[f"R20_{short}"] = f"{s['recall@20']:.3f}"
        v[f"MRR_{short}"] = f"{s['mrr']:.3f}"
        v[f"NDCG_{short}"] = f"{s['nDCG@10']:.3f}"
        v[f"TBL_{short}"] = f"{s['modality_recall'].get('table', float('nan')):.3f}"

    # Descriptive aliases, so a template can name the rung it means rather
    # than its letter.
    v["R_RERANK"] = v["R_D"]
    v["R20_RERANK"] = v["R20_D"]
    v["MRR_RERANK"] = v["MRR_D"]
    v["NDCG_RERANK"] = v["NDCG_D"]
    v["R_BM25"] = v["R_A"]
    v["R_HYBRID"] = v["R_C"]

    for (a_short, a_key), (b_short, b_key) in zip(RUNGS[:-1], RUNGS[1:]):
        c = comp.get(a_key)
        if not c:
            continue
        p = c["wilcoxon"]["p_value"]
        v[f"P_{a_short}{b_short}"] = _sci_plain(p)
        v[f"P_{a_short}{b_short}_TEX"] = _sci_tex(p)
        v[f"DELTA_{a_short}{b_short}"] = f"{c['delta']:+.3f}"

    # The quota's price, measured in each of its two positions, against the
    # no-quota configuration E.
    e, f_, g = (systems[k] for _, k in RUNGS[4:7])
    v["TBL_D"] = f"{systems['D. hybrid_rrf_rerank']['modality_recall'].get('table', float('nan')):.3f}"
    v["TBL_F"] = f"{systems['F. +quota_pre_rerank']['modality_recall'].get('table', float('nan')):.3f}"
    # The quota's effect on overall recall, in each of its two positions.
    v["QUOTA_PRE_DELTA"] = f"{systems['F. +quota_pre_rerank']['recall@10'] - systems['E. +category_filter']['recall@10']:+.3f}"
    v["QUOTA_POST_DELTA"] = f"{systems['G. +quota_post_rerank']['recall@10'] - systems['E. +category_filter']['recall@10']:+.3f}"
    v["QUOTA_PRE_COST_PP"] = f"{(e['recall@10'] - f_['recall@10']) * 100:.1f}"
    v["QUOTA_POST_COST_PP"] = f"{(e['recall@10'] - g['recall@10']) * 100:.1f}"
    v["QUOTA_POST_GAIN_PP"] = f"{(g['recall@10'] - f_['recall@10']) * 100:.1f}"
    v["NDCG_QUOTA_PRE_COST"] = f"{e['nDCG@10'] - f_['nDCG@10']:.3f}"
    v["NDCG_QUOTA_POST_COST"] = f"{e['nDCG@10'] - g['nDCG@10']:.3f}"
    v["FUSION_GAIN_PP"] = f"{(systems['C. hybrid_rrf']['recall@10'] - systems['A. bm25_only']['recall@10']) * 100:.1f}"
    v["RERANK_MRR_PP"] = f"{(systems['D. hybrid_rrf_rerank']['mrr'] - systems['C. hybrid_rrf']['mrr']) * 100:.1f}"
    _cd = None
    for _c in comp.values():
        if _c.get("comparison") == "C. hybrid_rrf -> D. hybrid_rrf_rerank":
            _cd = _c
    if _cd:
        v["DELTA_CD_MRR"] = f"{_cd.get('delta_mrr', 0.0):+.3f}"
        v["P_CD_MRR"] = _sci_plain(_cd.get("wilcoxon_mrr", {}).get("p_value", float("nan")))
        v["P_CD_MRR_TEX"] = _sci_tex(_cd.get("wilcoxon_mrr", {}).get("p_value", float("nan")))
        v["DELTA_CD_NDCG"] = f"{_cd.get('delta_ndcg', 0.0):+.3f}"
        v["P_CD_NDCG"] = _sci_plain(_cd.get("wilcoxon_ndcg", {}).get("p_value", float("nan")))
        v["P_CD_NDCG_TEX"] = _sci_tex(_cd.get("wilcoxon_ndcg", {}).get("p_value", float("nan")))
    # BM25 against the fused system: the comparison the narrative turns on.
    _ac = None
    for _c in comp.values():
        if _c.get("comparison") == "A. bm25_only -> C. hybrid_rrf":
            _ac = _c
    if _ac:
        v["DELTA_AC"] = f"{_ac['delta']:+.3f}"
        v["P_AC"] = _sci_plain(_ac["wilcoxon"]["p_value"])
        v["P_AC_TEX"] = _sci_tex(_ac["wilcoxon"]["p_value"])
        v["DELTA_AC_MRR"] = f"{_ac.get('delta_mrr', 0.0):+.3f}"
        v["P_AC_MRR"] = _sci_plain(_ac.get("wilcoxon_mrr", {}).get("p_value", float("nan")))
        v["P_AC_MRR_TEX"] = _sci_tex(_ac.get("wilcoxon_mrr", {}).get("p_value", float("nan")))
    v["RERANK_NDCG_PP"] = f"{(systems['D. hybrid_rrf_rerank']['nDCG@10'] - systems['C. hybrid_rrf']['nDCG@10']) * 100:.1f}"

    # The candidate-pool curve is measurable only on the six-category corpus;
    # the focus domain's recall is at ceiling for every pool size.
    # The fusion against the lexical leg: a non-adjacent comparison the
    # ablation now tests explicitly.
    for _c in exp1.get("comparisons", []):
        if _c.get("comparison") == "A. bm25_only -> C. hybrid_rrf":
            v["DELTA_AC"] = f"{_c['delta']:+.3f}"
            v["P_AC"] = f"{_c['wilcoxon']['p_value']:.1e}"
            v["DELTA_MRR_AC"] = f"{_c.get('delta_mrr', 0.0):+.3f}"
            v["P_MRR_AC"] = f"{_c.get('wilcoxon_mrr', {}).get('p_value', 0.0):.1e}"
            v["DELTA_NDCG_AC"] = f"{_c.get('delta_ndcg', 0.0):+.3f}"
            v["P_NDCG_AC"] = f"{_c.get('wilcoxon_ndcg', {}).get('p_value', 0.0):.1e}"

    exp5_path = RESULTS / "exp5_pool_size.json"
    if exp5_path.exists():
        exp5 = json.loads(exp5_path.read_text(encoding="utf-8"))
        for r in exp5["results"]:
            v[f"POOL{int(r['pool_size'])}"] = f"{r['recall@10']:.3f}"
            v[f"POOL{int(r['pool_size'])}_R20"] = f"{r['recall@20']:.3f}"
        _pk = max(exp5["results"], key=lambda r: r["recall@10"])
        v["POOL_PEAK"] = str(_pk["pool_size"])
        v["POOL_PEAK_R10"] = f"{_pk['recall@10']:.3f}"
        _lo5 = min(exp5["results"], key=lambda r: r["pool_size"])
        v["POOL_PEAK_GAIN"] = f"{_pk['recall@10'] - _lo5['recall@10']:+.3f}"
        v["POOL_PEAK_MINUS_LAST"] = (
            f"{_pk['recall@10'] - exp5['results'][-1]['recall@10']:+.3f}")
        # The pool sweep is monotone up to its knee, so the gain is measured
        # from the smallest pool to the knee rather than to the largest.
        _pools = sorted(int(r["pool_size"]) for r in exp5["results"])
        _best = max(r["recall@10"] for r in exp5["results"])
        _knee = next(int(r["pool_size"]) for r in exp5["results"]
                     if r["recall@10"] >= _best - 0.01)
        v["POOL_KNEE"] = str(_knee)
        _p10 = next((r for r in exp5["results"] if r["pool_size"] == 10), None)
        if _p10:
            v["POOL10_R20"] = f"{_p10['recall@20']:.3f}"
        v["POOL_GAIN"] = (f"{float(v.get(f'POOL{_knee}', 0)) - float(v.get(f'POOL{_pools[0]}', 0)):+.3f}")

    # The multi-category run carries its own numbers. The guide's narrative
    # compares the focus domain with the generalisation corpus, so both sets
    # are needed, and confusing them would put the wrong corpus's figures
    # under a sentence that names the other one.
    mc_path = RESULTS / "exp1_ablation.json"
    if mc_path.exists():
        mc = json.loads(mc_path.read_text(encoding="utf-8"))
        ms = mc["systems"]
        v["MC_TBL_D"] = f"{ms['D. hybrid_rrf_rerank']['modality_recall'].get('table', float('nan')):.3f}"
        v["MC_TBL_E"] = f"{ms['E. +category_filter']['modality_recall'].get('table', float('nan')):.3f}"
        v["MC_TBL_G"] = f"{ms['G. +quota_post_rerank']['modality_recall'].get('table', float('nan')):.3f}"
        v["MC_TBL_F"] = f"{ms['F. +quota_pre_rerank']['modality_recall'].get('table', float('nan')):.3f}"
        v["MC_R_A"] = f"{ms['A. bm25_only']['recall@10']:.3f}"
        v["MC_R_B"] = f"{ms['B. dense_only']['recall@10']:.3f}"
        v["MC_R_C"] = f"{ms['C. hybrid_rrf']['recall@10']:.3f}"
        v["MC_R_D"] = f"{ms['D. hybrid_rrf_rerank']['recall@10']:.3f}"
        v["MC_R_E"] = f"{ms['E. +category_filter']['recall@10']:.3f}"
        v["MC_R_F"] = f"{ms['F. +quota_pre_rerank']['recall@10']:.3f}"
        v["MC_R_G"] = f"{ms['G. +quota_post_rerank']['recall@10']:.3f}"
        v["MC_MRR_C"] = f"{ms['C. hybrid_rrf']['mrr']:.3f}"
        v["MC_MRR_A"] = f"{ms['A. bm25_only']['mrr']:.3f}"
        v["MC_NDCG_C"] = f"{ms['C. hybrid_rrf']['nDCG@10']:.3f}"
        v["MC_NDCG_B"] = f"{ms['B. dense_only']['nDCG@10']:.3f}"
        v["MC_NDCG_A"] = f"{ms['A. bm25_only']['nDCG@10']:.3f}"
        v["MC_R_F"] = f"{ms['F. +quota_pre_rerank']['recall@10']:.3f}"
        v["MC_TBL_F"] = f"{ms['F. +quota_pre_rerank']['modality_recall'].get('table', float('nan')):.3f}"
        v["MC_TBL_D"] = f"{ms['D. hybrid_rrf_rerank']['modality_recall'].get('table', float('nan')):.3f}"
        v["MC_TBL_C"] = f"{ms['C. hybrid_rrf']['modality_recall'].get('table', float('nan')):.3f}"
        v["MC_MRR_D"] = f"{ms['D. hybrid_rrf_rerank']['mrr']:.3f}"
        v["MC_MRR_RERANK_PP"] = f"{(ms['D. hybrid_rrf_rerank']['mrr'] - ms['C. hybrid_rrf']['mrr']) * 100:.1f}"
        for _c in mc.get("comparisons", []):
            if _c.get("comparison") == "A. bm25_only -> C. hybrid_rrf":
                v["MC_DELTA_AC"] = f"{_c['delta']:+.3f}"
                v["MC_P_AC"] = f"{_c['wilcoxon']['p_value']:.1e}"
        v["MC_QUOTA_PRE_COST_PP"] = f"{(ms['E. +category_filter']['recall@10'] - ms['F. +quota_pre_rerank']['recall@10']) * 100:.1f}"
        v["MC_QUOTA_POST_COST_PP"] = f"{(ms['E. +category_filter']['recall@10'] - ms['G. +quota_post_rerank']['recall@10']) * 100:.1f}"
        for _c in mc["comparisons"]:
            if _c.get("comparison") == "C. hybrid_rrf -> D. hybrid_rrf_rerank":
                v["MC_DELTA_CD"] = f"{_c['delta']:+.3f}"
                v["MC_P_CD"] = _sci_plain(_c["wilcoxon"]["p_value"])
                v["MC_DELTA_CD_MRR"] = f"{_c.get('delta_mrr', 0.0):+.3f}"
                v["MC_P_CD_MRR"] = _sci_plain(
                    _c.get("wilcoxon_mrr", {}).get("p_value", float("nan")))
                v["MC_DELTA_CD_NDCG"] = f"{_c.get('delta_ndcg', 0.0):+.3f}"
                v["MC_P_CD_NDCG"] = _sci_plain(
                    _c.get("wilcoxon_ndcg", {}).get("p_value", float("nan")))
            if _c.get("comparison") == "A. bm25_only -> C. hybrid_rrf":
                v["MC_DELTA_AC"] = f"{_c['delta']:+.3f}"
                v["MC_P_AC"] = _sci_plain(_c["wilcoxon"]["p_value"])
                v["MC_DELTA_AC_MRR"] = f"{_c.get('delta_mrr', 0.0):+.3f}"
                v["MC_P_AC_MRR"] = _sci_plain(
                    _c.get("wilcoxon_mrr", {}).get("p_value", float("nan")))

    # The long-context baseline arm. The focus-domain run carries the
    # headline numbers; the multi-category run is the generalisation
    # reference.
    _lc_add_long_context_tokens(v)
    _add_transfer_tokens(v)
    _add_contradiction_tokens(v)
    _add_project_scale_tokens(v)
    _add_config_tokens(v)
    _add_gate_calibration_tokens(v)
    _add_case_study_tokens(v)
    _add_trade_tokens(v)

    # The generator-side comparison (Experiment 8): the answer-quality half
    # of the long-context comparison, and the test of the framework's own
    # hypothesis H2.1.
    exp2_path = _first(RESULTS, "exp2_gate.json")
    if exp2_path.exists():
        exp2 = json.loads(exp2_path.read_text(encoding="utf-8"))
        v["GOLD_RECALL_PCT"] = f"{exp2['retriever_recall_of_gold']:.1%}"
        v["GOLD_MISSED_PCT"] = f"{max(0.0, 1.0 - exp2['retriever_recall_of_gold']):.1%}"
        _d = exp2.get("label_decomposition", {})
        _na = (int(_d.get("answerable_and_found", 0))
               + int(_d.get("answerable_and_missed", 0)))
        v["N_ANSWERABLE_MISSED"] = str(int(_d.get("answerable_and_missed", 0)))
        v["MISSED_SHARE_PCT"] = (f"{int(_d.get('answerable_and_missed', 0)) / _na:.1%}"
                                 if _na else "—")
        dec = exp2.get("label_decomposition", {})
        v["N_ANSWERABLE_FOUND"] = str(dec.get("answerable_and_found", 0))
        v["N_ANSWERABLE_MISSED"] = str(dec.get("answerable_and_missed", 0))
        v["N_LABEL_UNANSWERABLE"] = str(dec.get("unanswerable", 0))
        _neg = (int(dec.get("answerable_and_missed", 0))
                + int(dec.get("unanswerable", 0)))
        v["NEGATIVE_CLASS_SHARE_RETRIEVAL_FAILURE"] = (
            f"{int(dec.get('answerable_and_missed', 0)) / _neg:.1%}"
            if _neg else "—")
        ch = exp2.get("chosen_operating_point", {})
        if "tau" in ch:
            v["TAU"] = f"{ch['tau']:.2f}"
            v["ANSWERABLE_ANSWERED_PCT"] = f"{ch['answerable_answered']:.1%}"
            v["UNANSWERABLE_REFUSED_PCT"] = f"{ch['unanswerable_refused']:.1%}"
            v["ABSTENTION_PRECISION"] = f"{ch['abstention_precision']:.3f}"
            # The refusal rate is also reported per stratum, because the
            # unanswerable class is not homogeneous: the out-of-domain
            # family is unanswerable for any system, and the corpus-anchored
            # family is the case the gate is being tested on.
            _rf = unanswerable_refusal_by_family(exp2)
            v["UNANS_STRATUM_TAU"] = (
                f"{_rf['tau']:.2f}" if _rf.get("tau") is not None
                else "not measured")
            v["UNANS_HARD_REFUSED_PCT"] = (
                f"{_rf['hard_refused_rate']:.1%}"
                if _rf.get("hard_refused_rate") is not None
                else "not measured")
            _pre_gate = load_pre_repair_gate()
            _pre_ch = (_pre_gate or {}).get("chosen_operating_point") or {}
            v["UNANS_BEFORE_REFUSED_PCT"] = (
                f"{_pre_ch['unanswerable_refused']:.1%}" if "unanswerable_refused"
                in _pre_ch else "not measured")
            v["UNANS_BEFORE_ANSWERED_PCT"] = (
                f"{_pre_ch['answerable_answered']:.1%}" if "answerable_answered"
                in _pre_ch else "not measured")
            v["UNANS_BEFORE_TAU"] = (
                f"{_pre_ch['tau']:.2f}" if "tau" in _pre_ch else "not measured")
            v["UNANS_HARD_REFUSED_N"] = (
                f"{_rf['hard_refused']} of {_rf['hard_n']}"
                if _rf.get("hard_n") else "not measured")
            v["UNANS_OOD_REFUSED_PCT"] = (
                f"{_rf['ood_refused_rate']:.1%}"
                if _rf.get("ood_refused_rate") is not None
                else "not measured")
            v["UNANS_OOD_REFUSED_N"] = (
                f"{_rf['ood_refused']} of {_rf['ood_n']}"
                if _rf.get("ood_n") else "not measured")
            v["UNANS_OOD_N"] = (
                str(_rf["ood_n"]) if _rf.get("ood_n") else "not measured")
            v["UNANS_HARD_N_ONLY"] = (
                str(_rf["hard_n"]) if _rf.get("hard_n") else "not measured")

    # The form probe: what fraction of *malformed* queries the gate lets
    # through. This is a limitation, so it is measured rather than asserted.
    _add_form_probe_tokens(v)

    # The runtime form check, which runs before the gate: what it refuses on
    # malformed input, and what it refuses on well-formed input.
    _add_form_validator_tokens(v)

    # Last, because the generator tokens quote the operating point set above.
    _gen_add_generation_tokens(v)

    # The project's open threads are added last of all, by
    # _add_next_steps_tokens, because their text quotes the industrial
    # measurements and this function runs before those exist.


#: Token values that already contain LaTeX markup and must be substituted
#: verbatim into the `.tex` papers. The rule is structural rather than a
#: hand-kept list: a token whose name ends in `_TEX` *is* LaTeX, and
#: everything else is prose that has to be escaped. A value like
#: `88.8\%` or `2.5\!\times\!10^{-2}` is already marked up, and escaping it
#: again would print the backslashes.
LATEX_RAW_TOKENS = {"EMBED_MODEL_TEX"}


def _is_latex_raw(key: str) -> bool:
    return key in LATEX_RAW_TOKENS or key.endswith("_TEX")

#: The characters that break a LaTeX text-mode document. Markdown tolerates
#: all of them: an underscore in a file path ends a word in LaTeX with
#: "Missing $ inserted", and a percent sign comments out the rest of the
#: line. The same token values are substituted into both formats, so the
#: escaping has to happen here rather than in the prose.
_LATEX_SPECIAL = "_%&#$"


def _latex_escape(value) -> str:
    """Escape the characters that a LaTeX text-mode document cannot carry."""
    s = str(value)
    out = []
    for ch in s:
        out.append("\\" + ch if ch in _LATEX_SPECIAL else ch)
    return "".join(out)


def main() -> int:
    vals = values()
    unknown: set[str] = set()

    # A token value lands inside whatever string literal the template holds
    # it in, and some templates are Python source. A double quote in a value
    # ends that literal; a newline breaks it. This has happened once already
    # -- a quoted example inside a summary sentence -- and it presented as a
    # syntax error in a generator rather than as a token problem, which is a
    # long way from the cause.
    #
    # The danger is in *where* the value lands, not in what it contains: a
    # value that may hold a newline is fine in a markdown template and not
    # in a Python one. So a double quote is refused everywhere, and a
    # newline is refused only for the values that land in Python source.
    # The next-steps list is the reason the distinction is needed: it is a
    # block, one line per item, and its length is not fixed.
    quoted = sorted(k for k, v in vals.items() if '"' in str(v))
    if quoted:
        print(f"  !! token values containing a double quote: {quoted}")
        return 1

    python_targets = [rel for rel in TARGETS
                      if (ROOT / rel).exists() and (ROOT / rel).suffix == ".py"]
    multiline_in_python = set()
    for rel in python_targets:
        s = (ROOT / rel).read_text(encoding="utf-8")
        for key in set(re.findall(r"\{\{([A-Z0-9_]+)\}\}", s)):
            v = str(vals.get(key, ""))
            if "\n" in v or "\r" in v:
                multiline_in_python.add(key)
    if multiline_in_python:
        print("  !! token values containing a newline, landing in a Python "
              f"template: {sorted(multiline_in_python)}")
        return 1

    for rel in TARGETS:
        p = ROOT / rel
        if not p.exists():
            continue
        s = p.read_text(encoding="utf-8")
        original = s
        is_tex = p.suffix == ".tex"

        def repl(m):
            key = m.group(1)
            if key not in vals:
                unknown.add(key)
                return m.group(0)
            val = vals[key]
            if is_tex and not _is_latex_raw(key):
                val = _latex_escape(val)
            return val

        if not is_tex:
            s = pull_up_leading_numbers(s, vals)
        # A token's value may itself name a token -- the limitation row
        # quotes the corpus-by-corpus comparison, which is built from
        # several measurements. One pass would leave the inner token in the
        # delivered prose, where it reads as a number that was never
        # measured. So the substitution runs until the text stops changing.
        for _pass in range(8):
            before = s
            s = re.sub(r"\{\{([A-Z0-9_]+)\}\}", repl, s)
            if s == before:
                break
        if s != original:
            p.write_text(s, encoding="utf-8")
            print(f"  substituted tokens in {p.name}")
    if unknown:
        print(f"  !! unknown tokens left in place: {sorted(unknown)}")
        return 1
    print(f"  substituted {len(vals)} measured values")
    return 0


if __name__ == "__main__":
    sys.exit(main())
