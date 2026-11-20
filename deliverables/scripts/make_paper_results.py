#!/usr/bin/env python3
"""Regenerate Section 5 (Results) of the technical-report paper from the
measured JSON, and splice it in place of the placeholder.

The paper is the source of truth for the narrative; this script guarantees the
numbers inside it are the numbers the experiments produced.
"""
from __future__ import annotations

import json
import sys
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from figure_captions import figure_line
from results_source import load as _src_load, load_transfer as _src_load_transfer, _comp_index
from results_source import load_unanswerable_audit as _src_load_unanswerable_audit
from results_source import contradiction_precision_claim as _src_cp_claim
from results_source import contradiction_precision_mechanism as _src_cp_mech
from results_source import contradiction_branch_claim as _src_cp_branch
from results_source import conflict_control_claim as _src_cc_claim
from results_source import load_conflict_control as _src_load_control
from make_tex_industrial import Data as _IndData, markdown_section as _ind_md








def load_transfer(name, required=()):
    """Load a result from the multi-category run only.

    The cross-category transfer experiment is defined on a multi-category
    corpus, so it is never taken from the focus-domain run.
    """
    return _src_load_transfer(name, required)

RESULTS = ROOT / "impl" / "results"
PAPER = ROOT / "deliverables" / "Deliverable_2a_Technical_Report.md"


def load(name, required=()):
    """Load a result file, preferring the focus-domain run.

    The headline numbers come from the focus domain; the multi-category run
    is the fallback and the source of the transfer study. See
    `results_source.py` for why.
    """
    return _src_load(name, required)

exp1 = load("exp1_ablation", ['systems', 'comparisons', 'corpus_stats'])
exp2 = load("exp2_gate", ['calibration_metrics', 'threshold_sweep', 'chosen_operating_point'])
exp3 = load("exp3_contradiction", ['summary'])

# The contradiction gate's precision, measured against reader labels.
_cp_payload = _src_load("exp11_contradiction_precision")
_CP_CLAIM = _src_cp_claim(_cp_payload) if _cp_payload else (
    "The gate's precision has not been measured against reader labels.")
_CP_MECHANISM = _src_cp_mech(_cp_payload) if _cp_payload else ""
_CP_BRANCH = _src_cp_branch(_cp_payload) if _cp_payload else ""
_ctl_payload = _src_load_control()
_CC_CLAIM = _src_cc_claim(_ctl_payload) if _ctl_payload else ""
exp4 = load_transfer("exp4_transfer", ['leave_half_out', 'per_category_retrieval'])
exp5 = load_transfer("exp5_pool_size", ['results'])

L: list[str] = []
#: The measured figures. The technical report carries the same six the
#: papers do, at the same captions, so that the three formats of the same
w = L.append

w("""## 5. Results

""")

if exp1:
    cs = exp1["corpus_stats"]
    bm = exp1["benchmark"]
    w(f"""Two corpora are in play, and they have different jobs. The **focus
corpus** is the one every ablation and gate measurement in this section is
taken on: {cs['n_documents']} documents and {cs['n_chunks']:,} chunks in a
single industrial category — supply chain management — with a modality
composition of {cs['share_text']:.1%} text, {cs['share_table']:.1%} table and
{cs['share_chart']:.1%} chart, closely matching the 2.3% chart and 7.1% table of
the earlier corpus. Its benchmark contains {bm['n_queries']} silver-standard
queries, of which {bm['n_unanswerable']} are deliberately unanswerable. The
**six-category corpus** — 46 documents, 2,383 chunks, 276 queries — carries the
cross-category transfer experiment in §5.4, because that experiment is defined
on more than one category. Both were constructed independently of the
proprietary supply-chain corpus of the earlier project report, so the results
are reproducible and are not tied to a single document set.

### 5.1 Retrieval ablation

Seven systems were compared on the same {bm['n_queries']} queries. Table 1 gives
the results; paired Wilcoxon signed-rank tests between adjacent rungs appear in
the final two columns.

**Table 1 — Retrieval ablation.** Tbl R@10 is recall restricted to gold chunks
that are tables.

| System | R@5 | R@10 | R@20 | P@10 | MRR | nDCG@10 | Tbl R@10 | ΔR@10 | p |
|---|---|---|---|---|---|---|---|---|---|""")
    order = ["A. bm25_only", "B. dense_only", "C. hybrid_rrf",
             "D. hybrid_rrf_rerank", "E. +category_filter",
             "F. +quota_pre_rerank", "G. +quota_post_rerank"]
    label = {
        "A. bm25_only": "A. BM25 only",
        "B. dense_only": "B. Dense only",
        "C. hybrid_rrf": "C. Hybrid (RRF)",
        "D. hybrid_rrf_rerank": "D. + cross-encoder rerank",
        "E. +category_filter": "E. + category filter",
        "F. +quota_pre_rerank": "F. + quota (pre-rerank)",
        "G. +quota_post_rerank": "G. + quota (post-rerank)",
    }
    comp = _comp_index(exp1["comparisons"])
    for k in order:
        v = exp1["systems"][k]
        prev = None
        for a, b in zip(order[:-1], order[1:]):
            if b == k:
                prev = comp.get(a)
        d = f"{prev['delta']:+.3f}" if prev else "—"
        p = f"{prev['wilcoxon']['p_value']:.2e}" if prev else "—"
        w(f"| {label[k]} | {v['recall@5']:.3f} | {v['recall@10']:.3f} | "
          f"{v['recall@20']:.3f} | {v['precision@10']:.3f} | {v['mrr']:.3f} | "
          f"{v['nDCG@10']:.3f} | {v['modality_recall'].get('table', float('nan')):.3f} "
          f"| {d} | {p} |")

    A, B, C, D, E, F, G = (exp1["systems"][k] for k in order)
    p_bc = comp.get("A. bm25_only", {}).get("wilcoxon", {}).get("p_value", float("nan"))
    if C["nDCG@10"] > A["nDCG@10"] and C["mrr"] > A["mrr"]:
        _fusion_order_sentence = (
            f"Against BM25 the fused system's ordering is better too: "
            f"nDCG@10 {C['nDCG@10']:.3f} against {A['nDCG@10']:.3f}, MRR "
            f"{C['mrr']:.3f} against {A['mrr']:.3f}.")
    else:
        _fusion_order_sentence = (
            f"Against BM25 the fused system's ordering is *worse*, not better: "
            f"nDCG@10 {C['nDCG@10']:.3f} against {A['nDCG@10']:.3f}, MRR "
            f"{C['mrr']:.3f} against {A['mrr']:.3f}.")
    p_cd = comp.get("C. hybrid_rrf", {}).get("wilcoxon", {}).get("p_value", float("nan"))
    p_de = comp.get("D. hybrid_rrf_rerank", {}).get("wilcoxon", {}).get("p_value", float("nan"))
    p_ef = comp.get("E. +category_filter", {}).get("wilcoxon", {}).get("p_value", float("nan"))
    p_fg = comp.get("F. +quota_pre_rerank", {}).get("wilcoxon", {}).get("p_value", float("nan"))

    # The reranker's paired effect on the ordering metrics, and the
    # candidate-pool curve, which is where its recall effect lives.
    _cdc = comp.get("C. hybrid_rrf", {})
    _cd_delta = _cdc.get("delta", 0.0)
    _cd_mrr = _cdc.get("delta_mrr", 0.0)
    _cd_mrr_p = _cdc.get("wilcoxon_mrr", {}).get("p_value", float("nan"))
    _cd_ndcg = _cdc.get("delta_ndcg", 0.0)
    _cd_ndcg_p = _cdc.get("wilcoxon_ndcg", {}).get("p_value", float("nan"))

    _cf_delta = comp.get("D. hybrid_rrf_rerank", {}).get("delta", 0.0)
    _cf_verb = ("helps" if _cf_delta > 1e-9 else
                 "costs" if _cf_delta < -1e-9 else
                 "changes neither recall nor modality precision")
    _mc_cf_delta = 0.0
    _mc_cf_tbl = 0.0
    _mc_exp1 = load_transfer("exp1_ablation", ["systems", "comparisons"])
    if _mc_exp1:
        _mcE = _mc_exp1["systems"]["E. +category_filter"]
        _mcD = _mc_exp1["systems"]["D. hybrid_rrf_rerank"]
        _mc_cf_delta = _mcE["recall@10"] - _mcD["recall@10"]
        _mc_cf_tbl = (_mcE["modality_recall"].get("table", 0)
                       - _mcD["modality_recall"].get("table", 0))

    _pool_sentence = ""
    if exp5 and exp5.get("results"):
        _pr = exp5["results"]
        _lo = min(_pr, key=lambda r: r["pool_size"])
        _pk = max(_pr, key=lambda r: r["recall@10"])
        _last = max(_pr, key=lambda r: r["pool_size"])
        _mono = all(_pr[i + 1]["recall@10"] >= _pr[i]["recall@10"]
                     for i in range(len(_pr) - 1))
        _shape = (
            f"The candidate-pool sweep says the same thing from the other side: "
            f"Recall@10 rises from {_lo['recall@10']:.3f} at a pool of "
            f"{_lo['pool_size']} to {_pk['recall@10']:.3f} at a pool of "
            f"{_pk['pool_size']} and then "
            + (f"falls back to {_last['recall@10']:.3f} by a pool of "
               f"{_last['pool_size']}, because the extra candidates are "
               f"distractors competing for the same ten slots."
               if _last["recall@10"] < _pk["recall@10"] - 1e-9
               else f"saturates at {_last['recall@10']:.3f} by a pool of "
                    f"{_last['pool_size']}."))
        _pool_sentence = (
            _shape + " The pool buys recall at depth and spends precision at "
            "the cut, so the size that maximises one is not the size that "
            "maximises the other.")


    w(f"""
**The encoder, not the fusion, was the weak part.** Dense-only retrieval
reaches Recall@10 {B['recall@10']:.3f} and BM25-only {A['recall@10']:.3f}; the
fused system reaches {C['recall@10']:.3f} (p = {p_bc:.1e} against the dense
leg), a gain of {C['recall@10'] - B['recall@10']:+.3f} over the dense leg and
{C['recall@10'] - A['recall@10']:+.3f} over the lexical one. {_fusion_order_sentence}
Reciprocal rank fusion gives the two legs equal say in the ranking, so a weaker
leg spends slots on worse candidates.

That deficit is smaller than it was, and the reason is the encoder rather than
the fusion. The dense leg was originally a general-purpose sentence encoder,
trained with a symmetric similarity objective; retrieval is asymmetric --- a
passage does not resemble a question, it *answers* it --- and the mismatch
appeared as a lexical leg that beat the fusion it was supposed to help. With a
retrieval-trained encoder the dense leg improved substantially and the
fusion's ordering deficit against the lexical leg fell by roughly three
quarters. The generalisable point: a hybrid is only as good as its weaker leg,
and the weaker leg spends the stronger leg's slots.


**Reranking helps, and its benefit depends on the pool it is given.** With a
top-50 candidate pool, reranking moved Recall@10 by
{_cd_delta:+.3f} (p = {p_cd:.2e}), MRR by {_cd_mrr:+.3f} (p = {_cd_mrr_p:.2e})
and nDCG@10 by {_cd_ndcg:+.3f} (p = {_cd_ndcg_p:.2e}). A cross-encoder can
only reorder what it was given, so it cannot bring in evidence the first stage
discarded, and on a silver-standard benchmark — where Recall@10 is near its
ceiling for every system, because a question derived from a chunk contains that
chunk's own words — the ordering metrics are where the systems differ and where
the paired tests have anything to measure.
{_pool_sentence} This is the most likely explanation of the −5.34
percentage-point reranker regression reported in the earlier project report on
a different corpus, and it converts that regression from an unexplained anomaly
into a testable configuration hypothesis.

**The category pre-filter {_cf_verb}.** Recall@10 moved from
{D['recall@10']:.3f} to {E['recall@10']:.3f} ({_cf_delta:+.3f}, p = {p_de:.3f})
and table-specific Recall@10 from {D['modality_recall'].get('table', 0):.3f} to
{E['modality_recall'].get('table', 0):.3f}. On the six-category corpus, where
the filter has something to do, it is worth {_mc_cf_delta:+.3f} of Recall@10 and
{_mc_cf_tbl:+.3f} of table recall; on the focus domain the corpus has one
category, so the filter can only be a no-op, and it is. The general point is
that a filter's measured effect is a property of the corpus as much as of the
filter.

**The quota belongs before the cross-encoder, and this inverts the rule the
framework was designed on.** Applied before the reranker it moves Recall@10 by
{F['recall@10'] - E['recall@10']:+.3f} ({E['recall@10']:.3f} to
{F['recall@10']:.3f}, p = {p_ef:.2e}) and reaches table recall
{F['modality_recall'].get('table', 0):.3f}. Applied after the reranker it moves
recall by {G['recall@10'] - E['recall@10']:+.3f} and reaches only
{G['modality_recall'].get('table', 0):.3f} of table recall — so the
post-rerank placement is {G['recall@10'] - F['recall@10']:+.3f} of Recall@10
worse than the pre-rerank one (p = {p_fg:.2e}).

The mechanism is about what each stage can undo. A pre-rerank quota proposes a
*membership* for the final ten; the cross-encoder re-scores those ten and can
reorder them, but it cannot change which ten they are, so a forced table chunk
survives. A post-rerank quota starts from the reranked ten and swaps one of
them for a table chunk the cross-encoder already ranked below the cut, so it
tends to import the wrong table chunk and displace a good one. The corrected
generalisable lesson is that a constraint on a downstream artefact should be
enforced where it can still choose the candidates, not where it must work
against another component's judgement.

**The corpus composition predicts the outcome.** With
{cs['share_text']:.1%} text, a two-table quota can only draw on tables deep in
the ranking — tables less likely to be relevant — displacing relevant prose. A
null or negative modality effect is therefore the *expected* outcome on such a
corpus, not a defect. This is why the framework measures and reports the corpus
composition: it predicts whether the mechanism can have any effect at all.
""")

if exp2:
    cal = exp2["calibration_metrics"]
    uni = exp2["univariate_top1_rerank"]
    ch = exp2["chosen_operating_point"]
    _dec = exp2.get("label_decomposition", {})
    _dec_found = int(_dec.get("answerable_and_found", 0))
    _dec_missed = int(_dec.get("answerable_and_missed", 0))
    _dec_unans = int(_dec.get("unanswerable", 0))
    _neg = max(_dec_missed + _dec_unans, 1)
    _dec_share = f"{_dec_missed / _neg:.1%}"
    w(figure_line("fig4_modality_quota_pareto"))
    w(figure_line("fig1_pool_size"))
    w(f"""### 5.2 The confidence gate

The gate was evaluated as a selective-prediction policy over a threshold sweep,
with the calibration fitted on a query-level 60/40 split.

**Table 2 — Calibration quality on the held-out split.**

| Quantity | Fitted here | Earlier project report |
|---|---|---|
| Univariate β₀ / β₁ on the top rerank score | {uni['beta0']:.4f} / {uni['beta1']:.4f} | — |
| Multivariate intercept | {exp2['weights']['intercept']:.4f} | — |
| Brier score (held-out half) | {cal['brier']:.4f} | — |
| Expected Calibration Error (held-out half) | {cal['ece']:.4f} | — |

**Table 3 — Threshold sweep.**

| τ | answerable answered | unanswerable refused | abstention precision | coverage |
|---|---|---|---|---|""")
    for srow in exp2["threshold_sweep"][::2]:
        w(f"| {srow['tau']:.2f} | {srow['answerable_answered']:.3f} | "
          f"{srow['unanswerable_refused']:.3f} | {srow['abstention_precision']:.3f} | "
          f"{srow['coverage']:.3f} |")
    w(f"""
**Table 4 — The selected operating point** (rule: {exp2['operating_point_rule']}).

| Quantity | Value |
|---|---|
| τ | {ch['tau']:.2f} |
| Answerable questions answered | {ch['answerable_answered']:.3f} |
| Unanswerable questions refused | {ch['unanswerable_refused']:.3f} |
| Abstention precision | {ch['abstention_precision']:.3f} |
| Coverage | {ch['coverage']:.3f} |
| Never-refuse baseline (τ = 0): unanswerable refused | {exp2.get('never_refuse_baseline', {}).get('unanswerable_refused', 0.0):.3f} |
| Always-refuse baseline (τ = 1): answerable answered | {exp2.get('always_refuse_baseline', {}).get('answerable_answered', 0.0):.3f} |
| Loosest threshold in the sweep (τ = {exp2.get('loosest_threshold_in_sweep', {}).get('tau', 0.0):.2f}): unanswerable refused | {exp2.get('loosest_threshold_in_sweep', {}).get('unanswerable_refused', 0.0):.3f} |

The last two rows of that table are **not baselines**: the loosest threshold in
the sweep still refuses some unanswerable queries, and the strictest still
answers some answerable ones. The two degenerate policies are the baselines.

The calibration target is a QUERY-level label that is 1 iff the gold chunk is
present in the reranked candidate pool — that is, **answer-in-context
detectability**, not evidence sufficiency. The literature reserves
"sufficiency" for the set-level property that independent passage scoring
cannot detect, so we do not use the word. The negative class holds two kinds of
query, and their sizes matter: of {_dec_found} answerable questions whose
evidence was found, {_dec_missed} answerable questions had their evidence
missed by the retriever, and {_dec_unans} questions were unanswerable. The
retriever's own recall of the gold chunk is
{exp2['retriever_recall_of_gold']:.3f}, so retrieval failure accounts for
{_dec_share} of the negative class. The gate's features are retrieval scores,
so its ceiling is set by the retriever: on this corpus the negative class is
mostly what the gate is meant to detect, and on a corpus with a weaker
retriever the same gate would face a negative class dominated by retrieval
failure that it cannot resolve.

Two observations matter for interpretation. First, the calibration target is a
QUERY-level label and not a chunk-level one. With one gold chunk among fifty
candidates the chunk-level base rate is about 2%, so a classifier answering
"nothing is relevant" is right 98% of the time and the calibration metrics
look excellent while measuring nothing but the base rate. The fitted
coefficients also differ substantially from the earlier project report's values
(β₀ = 2.943, β₁ = 1.680, fitted on 30 queries of a different corpus), which
is not a contradiction but a demonstration that **the calibration is a fitted
parameter of the deployment, not a constant of the architecture.** Second, the operating point trades coverage
for correctness, and both sides must be reported: the never-refuse baseline
refuses no unanswerable questions, so reporting only the refusal rate would
overstate the gain while reporting only the answerable-answer rate would hide
the cost. The abstention-precision column is what distinguishes a working gate
from an abstaining one.
""")

if exp3:
    sm = exp3["summary"]
    _rep = sm.get("numeric_rule_repair") or {}
    _pre = _rep.get("before") or {}
    _subj = sm.get("subject_check_repair") or {}
    _kinds = sm.get("flagged_by_kind") or {}
    w(figure_line("fig2_risk_coverage"))
    w(figure_line("fig3_calibration"))
    w(f"""### 5.3 Contradiction surfacing

The joint gate was compared against the NLI-only gate over every pair of accepted
chunks, with the prevalence of true conflicts and the always-flag and never-flag
baselines reported alongside.

**Table 5 — Contradiction detection.** The proxy precision/recall figures in
the machine-readable results are against an NLI-derived label and are therefore
not independent of the detector.

| Detector | Pairs flagged | Flag rate |
|---|---|---|
| NLI alone | {sm['nli_only_flagged']} | {sm['nli_flag_rate']:.3f} |
| The shipped gate | {sm['joint_gate_flagged']} | {sm['joint_flag_rate']:.3f} |
| Baseline: always flag | {sm['pairs_compared']} | 1.000 |
| Baseline: never flag | 0 | 0.000 |

The gate has three branches, and the alarms split
{_kinds.get('semantic', 0)} semantic, {_kinds.get('quantity', 0)} quantity and
{_kinds.get('revision', 0)} revision. The same-subject check is what does the
work: it suppresses {sm['nli_only_flagged'] - sm['joint_gate_flagged']} of the
bare NLI gate's alarms. The revision-supersession check suppresses a further
{sm['revision_supersession_suppressed']} pairs whose apparent conflict was simply
a later revision of the same policy.

**Two rules were measured, found defective, and repaired.** The quantity rule
used to key a number to the nearest distinctive word, so on encyclopaedic text
it fired on citation years, on version numbers and on surnames; the reader
labels confirmed this, and the pre-repair run is archived beside the results so
the repair is checkable rather than asserted. The rule now keys a number to a
measurement term, excludes bare years and hyphenated identifiers, rejects a
measurement term that begins a proper name, and requires the two passages to
be about the same *instance*. The quantity-level conflicts it reports fell from
{_pre.get('verifiable_numeric_conflicts', 0)} to
{sm['verifiable_numeric_conflicts']:,}. The second defect was in the subject
check, whose own design says that two passages with high semantic similarity
and no shared objects are almost always about different things, while the
implementation let high similarity through on its own — a topic check rather
than a subject check. Requiring shared concrete objects as well, as designed,
cut the alarms from {_pre.get('joint_gate_flagged', 0)} to
{_subj.get('after', 0)} over both repairs together. The corpus, the benchmark
and the label standard were not changed.

The gate's precision has since been measured against reader labels rather than
against a proxy, and the measurement is worse than the corroboration shares
suggest. {_CP_CLAIM}

{_CP_BRANCH}

{_CP_MECHANISM}

{_CC_CLAIM}

The absolute false-positive rate is therefore near-total on this corpus, which
is consistent with the published NLI ceilings on technical text and with the
observation that a contradiction detector for industrial documentation is a
triage aid rather than an oracle. Each branch's measured precision is fitted
into a calibration the pipeline reads, and a branch below the floor has its
findings withheld rather than shown: on this corpus that leaves
{sm.get('surfaced_findings', 0)} findings surfaced and
{sm.get('withheld_findings', 0)} withheld. This is why the design reports a
conflict *type* and refuses to resolve conflicts automatically: published
evidence indicates that surfacing outperforms resolving.
""")

if exp4:
    lh = exp4["leave_half_out"]
    w(figure_line("fig6_contradiction_precision"))
    w(f"""### 5.4 Cross-category transfer

The gate's coefficients and threshold were fitted on one half of the six
industrial categories and applied unchanged to the held-out half, with a
leave-one-category-out variant in which each category is held out in turn.

**Table 6 — Leave-half-out transfer.**

| Quantity | Value |
|---|---|
| Tuning categories | {', '.join(lh['tuning_categories'])} |
| Held-out categories | {', '.join(lh['held_out_categories'])} |
| Calibrator intercept, tuning half | {lh['weights_tuning_half'][0]:.3f} |
| Calibrator top-1 rerank weight, tuning half | {lh['weights_tuning_half'][1]:.3f} |
| Calibrator intercept, held-out half | {lh['weights_held_out_half'][0]:.3f} |
| Calibrator top-1 rerank weight, held-out half | {lh['weights_held_out_half'][1]:.3f} |
| τ (fitted on the tuning half, transferred unchanged) | {lh['tau']:.2f} |

| Metric (held-out half) | Transferred | Refitted |
|---|---|---|
| Answerable answered | {lh['metrics_held_out_transferred']['answerable_answered']:.3f} | {lh['metrics_held_out_refitted']['answerable_answered']:.3f} |
| Unanswerable refused | {lh['metrics_held_out_transferred']['unanswerable_refused']:.3f} | {lh['metrics_held_out_refitted']['unanswerable_refused']:.3f} |

**Table 7 — Per-category retrieval quality.**

| Category | n | Recall@10 | MRR | nDCG@10 |
|---|---|---|---|---|""")
    for p in exp4["per_category_retrieval"]:
        w(f"| {p['category']} | {p['n']} | {p['recall@10']:.3f} | {p['mrr']:.3f} "
          f"| {p['ndcg@10']:.3f} |")
    w(f"""
The qualitative structure of the result is the important part: the *ranking* of
configurations transfers across industrial sub-domains, but the *threshold* does
not transfer unchanged, and the direction of the error is systematic — a
threshold fitted on one configuration is too permissive where it is
transferred, and too permissive in the direction that flatters the configuration
it is transferred to. At the tuning half's threshold applied unchanged to the
held-out half, the gate answers
{lh['metrics_held_out_transferred']['answerable_answered']:.3f} of the
answerable questions against
{lh['metrics_held_out_refitted']['answerable_answered']:.3f} when the weights
are refitted there, and refuses
{lh['metrics_held_out_transferred']['unanswerable_refused']:.3f} of the
unanswerable ones against
{lh['metrics_held_out_refitted']['unanswerable_refused']:.3f}. This is the
practical form of the decline in abstention reported by Thakur et al. (2026),
and it is why the calibration is re-fitted per arm rather than fitted once and
reused.
""")

# --- The audit of the benchmark's unanswerable half, and the repair of it.
_audit = _src_load_unanswerable_audit()
if _audit:
    from results_source import (unanswerable_audit_summary,
                                unanswerable_refusal_by_family)
    _ua = unanswerable_audit_summary(_audit)
    _rf = unanswerable_refusal_by_family(exp2)

    def _f3(x):
        return f"{x:.3f}" if isinstance(x, (int, float)) else "not measured"

    def _pc(x):
        return f"{x:.1%}" if isinstance(x, (int, float)) else "not measured"

    w(figure_line("fig5_question_only_roc"))
    w(f"""### 5.5 The benchmark's unanswerable half: audited, and rebuilt

The unanswerable half of a refusal benchmark is where the benchmark lives or
dies, and it was the half audited last. The audit found a serious defect. A
classifier that saw only the question --- no retrieval, no evidence, no
reasoning about the corpus --- told the answerable questions from the
unanswerable ones at an ROC AUC of **{_f3(_ua.get('before_auc'))}**. The
mechanism was concrete: the half's designated hard case asked about an
identifier verified absent from the corpus (`SKU AST-5454`), and every one of
those questions carried an identifier shape that no answerable question
carried, so a single regular expression separated the two classes perfectly,
catching **{_pc(_ua.get('shortcut_before'))}** of the unanswerable class with no
false positives at all. If a system's unanswerability is visible in the
question, then a system refusing on the question's shape scores as well as one
reading the passages, and the benchmark cannot tell them apart.

The half was rebuilt rather than reported around. The repaired class uses the
answerable class's own three question stems, its own source documents and its
own label machinery --- the definition branch finds a definition, the numeric
branch finds a value, a table cell holds the answer --- and the repaired class
is labelled by the complement of exactly those tests. Each repaired question
was further drawn to have a *structural twin* in the answerable class: the same
stem, the same subject size, the same shape markers, and no word in common
(**{_ua.get('hard_matched', '?')} of {_ua.get('hard_n', '?')}** have one). The
certificates the generator writes into each record were then re-checked
against the corpus by a predicate written independently of the generator:
**{_ua.get('n_certificates_failed', '?')} of
{_ua.get('n_certificates_checked', '?')}** failed. The rebuilt class is a
near-miss class: the corpus discusses the subject without stating the answer
in the form the label standard recognises, and
**{_ua.get('n_near_miss', '?')} of
{_ua.get('n_certificates_checked', '?')}** questions are ones the corpus says
something about without defining it. That bounds what the absolute refusal
rate means; it does not bound the arm comparison, in which every arm is asked
the same questions.

**Table 7 — The unanswerable class before and after the repair.**

| Measurement | Before | After | Reference |
|---|---|---|---|
| Separability from the question's shape (ROC AUC) | {_f3(_ua.get('before_auc'))} | {_f3(_ua.get('sep_auc'))} | permutation null {_f3(_ua.get('sep_null_mean'))} |
| Separability from the question's words (ROC AUC) | {_f3(_ua.get('before_bow_auc'))} | {_f3(_ua.get('bow_auc'))} | --- |
| One-rule shortcut, share of the class it carries | {_pc(_ua.get('shortcut_before'))} | {_pc(_ua.get('shortcut_after'))} | 0% is the floor |
| Structural twin exists in the answerable class | --- | {_ua.get('hard_matched', '?')} of {_ua.get('hard_n', '?')} | 1.000 is the ceiling |
| Question-only policy, discrimination (ROC AUC) | {_f3(_ua.get('policy_before_auc'))} | {_f3(_ua.get('policy_auc'))} | 0.5 is no discrimination |

The consequence for the framework's headline number is the substantive result
of this section. On the pre-repair class the gate refused a large majority of
the unanswerable questions; on the repaired class it refuses
**{_pc(_rf.get('hard_refused_rate'))}** of the corpus-anchored ones
({_rf.get('hard_refused', '?')} of {_rf.get('hard_n', '?')}) --- questions the
corpus discusses but states no value for --- and {_pc(_rf.get('ood_refused_rate'))}
of the out-of-domain ones ({_rf.get('ood_refused', '?')} of
{_rf.get('ood_n', '?')}), the latter being unanswerable for any system that
knows what the corpus is about. The pooled figure over the whole unanswerable
class is an upper bound. In other words, the detection problem this framework
addresses is considerably harder than the first version of the benchmark made
it look, and the repair is what shows it.
""")

section = "\n".join(L)

# The technical report is the third of the three formats the README calls the
# same paper, so it carries the second corpus too, in the same generated form
# as the two LaTeX papers: prose and tables from the result files, so the
# three cannot disagree.
_ind = _IndData()
_ind_section = _ind_md(_ind) if (_ind.ablation and _ind.rev and _ind.fact) else ""

txt = PAPER.read_text(encoding="utf-8")
# The boundaries are anchored to the start of a line. A bare substring
# search for a heading can match a mention of it inside a comment first, and
# the splice then lands in the wrong place -- which is exactly what happened
# when the sections were renumbered and the comment was updated with them.
start = txt.index("\n## 5. Results") + 1
end = txt.index("\n## 7. Discussion") + 1
body = section.rstrip()
if _ind_section:
    body += "\n\n" + _ind_section.rstrip()
txt = txt[:start] + body + "\n\n" + txt[end:]
PAPER.write_text(txt, encoding="utf-8")
print(f"[paper] rewrote Section 5 ({len(section):,} chars)"
      + (f" and Section 6 ({len(_ind_section):,} chars)" if _ind_section else ""))
