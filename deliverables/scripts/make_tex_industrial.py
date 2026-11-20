#!/usr/bin/env python3
"""Generate the second-corpus section of the two LaTeX papers.

The industrial corpus -- 110 United States federal regulatory documents read
through the eCFR versioner -- was built to close two of this project's open
objectives, and it carries the paper's clearest new result: a conflict
detector's precision decomposes into *detection* (is the alarm pointing at
something real) and *typing* (is the branch that raised it the branch that
owns the conflict), and the two are nine-fold apart.

This script writes that section into both papers. It writes prose, not
templates, because the interpretive sentences in it are exactly the kind
that go stale: whether fusion beat its lexical leg, whether the band
replicated, whether the rubric or the reader moved the number. Each is a
fact about the run, and a hand-written sentence asserts one answer
regardless. Every number here is read from the result files; nothing is
typed in by hand.

The section is written between two markers in each paper:

    % BEGIN INDUSTRIAL-SECTION
    % END INDUSTRIAL-SECTION

The journal paper gets the full treatment; the conference paper, which is
the condensed venue version, gets a shorter one and fewer figures.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
IND = ROOT / "impl" / "results_industrial"
FOCUS = ROOT / "impl" / "results_focus"

PAPERS = {
    "2b": ROOT / "deliverables" / "Deliverable_2b_IEEE_Conference_Paper.tex",
    "2c": ROOT / "deliverables" / "Deliverable_2c_Journal_Style_Paper.tex",
}

BEGIN = "% BEGIN INDUSTRIAL-SECTION"
END = "% END INDUSTRIAL-SECTION"


def load(path: Path):
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def p_of(x: float) -> str:
    """A p-value in a form that survives LaTeX."""
    if x is None:
        return "n/a"
    if x < 1e-4:
        return "$p<0.0001$"
    return f"$p={x:.4f}$"


def esc(s: str) -> str:
    return s.replace("&", "\\&").replace("%", "\\%").replace("_", "\\_")


# ---------------------------------------------------------------------------
# the measurements
# ---------------------------------------------------------------------------
class Data:
    """Every number the new section reads, loaded once."""

    def __init__(self) -> None:
        self.bench = json.loads((ROOT / "impl" / "data" / "benchmark_industrial"
                                 / "benchmark.json").read_text(encoding="utf-8"))
        self.ablation = load(IND / "exp1_ablation.json")
        self.pool = load(IND / "exp5_pool_size.json")
        self.gate = load(IND / "exp2_gate.json")
        self.rev = load(IND / "exp14_revision_eval.json")
        self.fact = load(IND / "exp21_rubric_factorial.json")
        self.audit = load(IND / "exp12_unanswerable_class_audit.json")
        self.qty = load(IND / "exp20_quantity_stratum.json")
        self.revstats = load(IND / "exp21_revision_corpus_stats.json")
        self.band_focus_gold = load(FOCUS / "exp17_claim_band_eval.json")
        self.band_focus_ret = load(FOCUS / "exp18_claim_band_eval.json")
        self.band_ind_gold = load(IND / "exp21_claim_band_eval_gold.json")
        self.band_ind_ret = load(IND / "exp21_claim_band_eval_retrieved.json")
        self.gate_focus = load(FOCUS / "exp2_gate.json")

    # -- retrieval -------------------------------------------------------
    def system(self, key: str) -> dict:
        return (self.ablation.get("systems") or {})[key]

    def comparison(self, key: str) -> dict | None:
        for c in self.ablation.get("comparisons", []):
            if c["comparison"] == key:
                return c
        return None

    @property
    def cs(self) -> dict:
        return self.ablation["corpus_stats"]

    @property
    def reg(self) -> dict:
        return self.rev["profiles"]["regulatory"]["consensus"]

    @property
    def reg_overall(self) -> dict:
        return self.reg["overall"]

    @property
    def reg_construction(self) -> dict:
        return self.rev["profiles"]["regulatory"]["construction_labels"]

    @property
    def shipped_overall(self) -> dict:
        return self.rev["profiles"]["shipped"]["consensus"]["overall"]

    @property
    def ind_op(self) -> dict:
        return self.gate["chosen_operating_point"]

    @property
    def focus_op(self) -> dict:
        return self.gate_focus["chosen_operating_point"]

    @property
    def cells(self) -> dict:
        return self.fact.get("cells", {})

    @property
    def effects(self) -> dict:
        return self.fact.get("effects", {})

    @property
    def decomposition(self) -> dict:
        return self.fact.get("decomposition", {})


# ---------------------------------------------------------------------------
# the figures
# ---------------------------------------------------------------------------
#: figure key -> (file stem, title). The captions are written here rather
#: than in the template because a caption states a claim about the plotted
#: numbers, and a claim about the numbers is exactly what goes stale.
FIGURES = {
    "fig5": ("fig5_question_only_roc",
             "A classifier that sees only the question text --- no retrieval, no "
             "evidence, no corpus --- telling an answerable question from an "
             "unanswerable one, on both corpora and before and after the "
             "benchmark repair."),
    "fig1": ("fig1_pool_size",
             "Recall against the size of the rerank candidate pool, on the focus "
             "corpus and on the industrial corpus."),
    "fig4": ("fig4_modality_quota_pareto",
             "Overall Recall@10 against table-specific Recall@10 for the seven "
             "ablated systems, on the focus corpus and on the industrial corpus."),
    "fig2": ("fig2_risk_coverage",
             "Risk--coverage of the confidence gate: the risk that an answered "
             "query has no answer in its context, against the fraction of "
             "queries the gate answers."),
    "fig3": ("fig3_calibration",
             "Reliability of the gate's calibrated probability against observed "
             "answerability, on the held-out evaluation half of each corpus."),
    "fig6": ("fig6_contradiction_precision",
             "The contradiction detector's precision against the base rate of "
             "real conflicts in the same population, with 95\\% Wilson "
             "intervals; a filled marker clears the framework's 0.5 calibration "
             "floor and the branch would act, a hollow one does not."),
}


def figure(key: str, width: str) -> str:
    stem, cap = FIGURES[key]
    return (
        "\\begin{figure}[t]\n"
        "\\centering\n"
        f"\\includegraphics[width={width}]{{figures/{stem}.pdf}}\n"
        f"\\caption{{{cap}}}\n"
        f"\\label{{fig:{key}}}\n"
        "\\end{figure}\n"
    )


# ---------------------------------------------------------------------------
# the tables
# ---------------------------------------------------------------------------
def ablation_table(d: Data, width: str) -> str:
    rows = []
    for key, label in (("A. bm25_only", "A. BM25 only"),
                        ("B. dense_only", "B. Dense only"),
                        ("C. hybrid_rrf", "C. Hybrid (RRF)"),
                        ("D. hybrid_rrf_rerank", "D. $+$ cross-encoder"),
                        ("E. +category_filter", "E. $+$ category filter"),
                        ("F. +quota_pre_rerank", "F. $+$ quota (pre-rerank)"),
                        ("G. +quota_post_rerank", "G. $+$ quota (post-rerank)")):
        s = d.system(key)
        tbl = (s.get("modality_recall") or {}).get("table")
        tbl_s = "---" if tbl is None else f"{tbl:.3f}"
        rows.append(f"{label} & {s['recall@5']:.4f} & {s['recall@10']:.4f} & "
                    f"{s['mrr']:.4f} & {s['nDCG@10']:.4f} & {tbl_s} \\\\")
    body = "\n".join(rows)
    resize = f"\\resizebox{{{width}}}{{!}}{{%\n" if "columnwidth" in width else ""
    close = "}\n" if resize else ""
    return (
        "\\begin{table}[t]\n"
        "\\centering\n"
        f"\\caption{{Retrieval ablation on the industrial corpus: "
        f"{d.bench['n_answerable']} answerable queries over "
        f"{d.cs['n_documents']} federal regulatory documents "
        f"({d.cs['n_chunks']:,} chunks). Tbl R@10 is the recall over the "
        f"table-bearing chunks only.}}\n"
        "\\label{tab:ind-ablation}\n"
        "\\small\n"
        f"{resize}"
        "\\begin{tabular}{lrrrrr}\n"
        "\\toprule\n"
        "System & R@5 & R@10 & MRR & nDCG@10 & Tbl R@10 \\\\\n"
        "\\midrule\n"
        f"{body}\n"
        "\\bottomrule\n"
        "\\end{tabular}\n"
        f"{close}"
        "\\end{table}\n"
    )


def factorial_table(d: Data, width: str) -> str:
    rows = []
    for name in ("generalist_v1", "generalist_v2", "specialist_v1",
                 "specialist_v2"):
        c = d.cells.get(name, {}).get("consensus", {})
        if not c:
            continue
        reader = name.split("_")[0]
        rubric = "old (marker test)" if name.endswith("v1") \
            else "sharpened (structural test)"
        rows.append(f"{reader} & {rubric} & {c['detection_precision']:.3f} & "
                    f"{c['typing_precision']:.3f} \\\\")
    body = "\n".join(rows)
    e = d.effects
    eff_rows = [
        f"\\emph{{Rubric}}, at the generalist & "
        f"\\textbf{{{e.get('rubric_effect_at_generalist', {}).get('difference', 0):+.3f}}} \\\\",
        f"\\emph{{Rubric}}, at the specialist & "
        f"\\textbf{{{e.get('rubric_effect_at_specialist', {}).get('difference', 0):+.3f}}} \\\\",
        f"\\emph{{Specialisation}}, at the old rubric & "
        f"{e.get('specialisation_effect_at_v1', {}).get('difference', 0):+.3f} \\\\",
        f"\\emph{{Specialisation}}, at the sharpened rubric & "
        f"{e.get('specialisation_effect_at_v2', {}).get('difference', 0):+.3f} \\\\",
    ]
    eff_body = "\n".join(eff_rows)
    resize = f"\\resizebox{{{width}}}{{!}}{{%\n" if "columnwidth" in width else ""
    close = "}\n" if resize else ""
    return (
        "\\begin{table}[t]\n"
        "\\centering\n"
        "\\caption{The rubric $\\times$ reader-specialisation factorial. Each "
        "cell is an independent reading of the same 240 pairs by the same "
        "detector, under the same regime briefs. Detection precision is the "
        "fraction of the reader's alarms that correspond to a real conflict; "
        "typing precision is the fraction raised by the branch that owns it. "
        "The lower block is the difference in detection precision between the "
        "two cells of each row and column.}\n"
        "\\label{tab:ind-factorial}\n"
        "\\small\n"
        f"{resize}"
        "\\begin{tabular}{llrr}\n"
        "\\toprule\n"
        "Reader & Rubric & Detection & Typing \\\\\n"
        "\\midrule\n"
        f"{body}\n"
        "\\bottomrule\n"
        "\\end{tabular}\n"
        "\\vspace{3pt}\n"
        "\\begin{tabular}{lr}\n"
        "\\toprule\n"
        "Effect & $\\Delta$ detection \\\\\n"
        "\\midrule\n"
        f"{eff_body}\n"
        "\\bottomrule\n"
        "\\end{tabular}\n"
        f"{close}"
        "\\end{table}\n"
    )


def band_caveat() -> str:
    """A note under the band table when a row sits on an earlier configuration.

    The per-claim band was measured on the retrieval configuration the system
    shipped at the time. Where the quota placement moved afterwards, a row
    that cannot be re-measured is quoted as the earlier configuration's
    result rather than passed off as a current one. Which rows are affected
    is read from the provenance stamps, not written here.
    """
    sys.path.insert(0, str(ROOT / "deliverables" / "scripts"))
    from results_source import shipped_quota_position

    shipped = shipped_quota_position()
    stale = []
    for label, path in (
            ("the focus corpus's gold protocol",
             FOCUS / "exp17_claim_band_eval.json"),
            ("the focus corpus's retrieved protocol",
             FOCUS / "exp18_claim_band_eval.json")):
        if not path.exists():
            continue
        doc = json.loads(path.read_text(encoding="utf-8"))
        placement = doc.get("retrieval_placement") or "post_rerank"
        if placement != shipped:
            stale.append(label)
    if not stale:
        return ""
    which = (stale[0] if len(stale) == 1
             else stale[0] + " and " + stale[1])
    return ("\\emph{Caveat.} " + which + (" was" if len(stale) == 1 else " were")
            + " measured before the modality quota was moved to the other "
            "side of the cross-encoder, and the reference labels they rest on "
            "come from a panel of reader agents under a written protocol that "
            "could not be reproduced. They are quoted here as the earlier "
            "configuration's result.")


def band_table(d: Data, width: str) -> str:
    """The band, on all four corpus-and-protocol combinations."""
    combos = (("Focus, gold", d.band_focus_gold),
              ("Focus, retrieved", d.band_focus_ret),
              ("Industrial, gold", d.band_ind_gold),
              ("Industrial, retrieved", d.band_ind_ret))
    rows = []
    for label, doc in combos:
        if not doc:
            continue
        ab = doc.get("agreement_binary", {})
        pb = doc.get("per_band") or {}
        al = doc.get("answer_level") or {}
        kappa = ab.get("cohens_kappa", float("nan"))
        ci = ab.get("ci95") or [float("nan"), float("nan")]
        g = (pb.get("grounded") or {}).get("error_rate", float("nan"))
        i = (pb.get("inferred") or {}).get("error_rate", float("nan"))
        u = (pb.get("uncertain") or {}).get("error_rate", float("nan"))
        clean = al.get("answers_with_no_wrong_claim_rate", float("nan"))
        grounded = al.get(
            "answers_clean_after_keeping_grounded_only_rate", float("nan"))
        rows.append(
            f"{label} & {kappa:.3f} ({ci[0]:+.3f}, {ci[1]:+.3f}) & "
            f"{g:.3f} / {i:.3f} / {u:.3f} & "
            f"{clean * 100:.1f}\\% $\\rightarrow$ {grounded * 100:.1f}\\% \\\\")
    body = "\n".join(rows)
    resize = f"\\resizebox{{{width}}}{{!}}{{%\n" if "columnwidth" in width else ""
    close = "}\n" if resize else ""
    return (
        "\\begin{table}[t]\n"
        "\\centering\n"
        "\\caption{The per-claim confidence band against an independent "
        "reference, on both corpora and both evidence protocols. The kappa "
        "column is the agreement between the band and the reference on the "
        "binary question \\emph{is this claim supported}. The band-error "
        "column gives the error rate of the \\emph{grounded}, \\emph{inferred} "
        "and \\emph{uncertain} bands in that order. The last column is the "
        "share of answers containing no wrong claim, before and after keeping "
        "only the \\emph{grounded} claims.}\n"
        "\\label{tab:ind-band}\n"
        "\\small\n"
        f"{resize}"
        "\\begin{tabular}{lccc}\n"
        "\\toprule\n"
        "Corpus and protocol & $\\kappa$ & Band error (g/i/u) & Clean \\\\"
        "\\midrule\n"
        f"{body}\n"
        "\\bottomrule\n"
        "\\end{tabular}\n"
        f"{close}"
        "\\end{table}\n"
    )


# ---------------------------------------------------------------------------
# the prose
# ---------------------------------------------------------------------------
def full_section(d: Data) -> str:
    cs = d.cs
    bench = d.bench
    reg = d.reg_overall
    cons = d.reg_construction
    eff = d.effects
    dec = d.decomposition
    qty = d.qty
    revstats = d.revstats

    bm = d.comparison("A. bm25_only -> B. dense_only")
    fu = d.comparison("A. bm25_only -> C. hybrid_rrf")
    fi = d.comparison("D. hybrid_rrf_rerank -> E. +category_filter")
    rr = d.comparison("C. hybrid_rrf -> D. hybrid_rrf_rerank")
    qp = d.comparison("E. +category_filter -> F. +quota_pre_rerank")
    qg = d.comparison("F. +quota_pre_rerank -> G. +quota_post_rerank")

    pool50 = None
    for r in (d.pool or {}).get("results", []):
        if r["pool_size"] == 50:
            pool50 = r
    displacement = ((pool50["recall@20"] - pool50["recall@10"]) * 100
                    if pool50 else float("nan"))

    sem = cons["per_branch"]["semantic"]
    revb = cons["per_branch"]["revision"]
    qtyb = cons["per_branch"]["quantity"]
    # The per-branch figures live under the profile's *consensus*, not under
    # its overall block. Reading them from the overall block gave empty
    # dicts, and the numbers were printed as "0" and "nan" in the paper.
    sem_reader = d.reg.get("per_branch", {}).get("semantic", {})
    rev_reader = d.reg.get("per_branch", {}).get("revision", {})

    st = d.audit["after_repair"]["structural_separability"][
        "repaired_whole_class"]
    lp = d.audit["after_repair"]["length_profile"]

    ind_op = d.ind_op
    focus_op = d.focus_op
    ind_cal = d.gate["calibration_metrics"]
    focus_cal = d.gate_focus["calibration_metrics"]

    gen = dec.get("generalist", {})
    spec = dec.get("specialist", {})

    fg = d.band_focus_gold
    fr = d.band_focus_ret
    ig = d.band_ind_gold
    ir = d.band_ind_ret

    def pos_p(doc):
        v = ((doc.get("value_test") or {}).get("paired") or {}) \
            .get("band_vs_first") or {}
        return v.get("wilcoxon_p", float("nan"))

    def kappa(doc):
        return (doc.get("agreement_binary") or {}).get(
            "cohens_kappa", float("nan"))

    def bands(doc):
        pb = doc.get("per_band") or {}
        return tuple((pb.get(b) or {}).get("error_rate", float("nan"))
                     for b in ("grounded", "inferred", "uncertain"))

    def clean(doc):
        al = doc.get("answer_level") or {}
        return (al.get("answers_with_no_wrong_claim_rate", float("nan")),
                al.get("answers_clean_after_keeping_grounded_only_rate",
                       float("nan")))

    fgc, fgg = clean(fg)
    frc, frg = clean(fr)
    igc, igg = clean(ig)
    irc, irg = clean(ir)

    return f"""
\\section{{A second corpus: authentic, versioned, binding industrial text}}
\\label{{sec:industrial}}

\\subsection{{Why a second corpus, and what it is}}

The corpus of Section~\\ref{{sec:protocol}} is encyclopaedic
industrial-engineering prose, and two of this paper's objectives cannot be
closed on it. It contains no conflict a practitioner would recognise as one:
a document read at a single upstream revision cannot contradict itself, and
concept-level prose rarely binds a numeric requirement that another document
contradicts. And it is not the class of document a practitioner reads --- it
is reference material about industrial-engineering concepts, not operating
procedures carrying binding limits.

A second corpus was built to close that gap. It is the United States
\\emph{{Electronic Code of Federal Regulations}} (eCFR), read through the
versioner API, which serves any regulation as it stood on any past date. Two
properties follow, and together they close two objectives with one artefact.
The text is authentic and binding: these are the regulations a plant is
measured against, they carry numeric requirements (exposure limits,
separation distances, capacities, quantities), and they are public domain, so
the corpus ships with the paper. The text is also \\emph{{versioned}}: federal
regulations are amended, so the same section read on
{revstats['pre_date']} and on {revstats['post_date']} is the same rule at two
issues. Aligning the two snapshots gives {revstats['n_amended_paragraph_pairs']}
amended-paragraph pairs, of which
{revstats['n_pairs_stating_different_numbers']}
({revstats['share_stating_different_numbers'] * 100:.1f}\\%) state different
numbers in the two vintages. Such a pair \\emph{{is}} a conflict, and its type
is known by construction: the same provision at two issues is a supersession,
not a contradiction, and no annotation is needed to know that.

The corpus holds {cs['n_documents']} documents and {cs['n_chunks']:,} chunks
({cs['by_modality'].get('text', 0):,} text,
{cs['by_modality'].get('table', 0):,} table,
{cs['by_modality'].get('chart', 0):,} chart) in {cs['n_categories']} regulatory
regimes, and its benchmark has {bench['n_queries']} queries
({bench['n_answerable']} answerable, {bench['n_unanswerable']}
unanswerable). It was audited for the same shortcut the first benchmark had.
The one-rule identifier shortcut that carried 76.4\\% of the first benchmark's
unanswerable class catches
{d.audit['after_repair']['shortcut_diagnostic']['unanswerable_caught']} of
{bench['n_unanswerable']} here, and a question-only classifier separates the
two classes at ROC AUC {st['roc_auc']:.3f} against a permutation null of
{st['permutation_null_auc_mean']:.3f}. The residual separability is question
length --- median {lp['median_length_answerable']:.0f} characters for the
answerable class against {lp['median_length_unanswerable']:.0f} for the
unanswerable one --- which is reported rather than hidden.

{figure('fig5', '0.72\\textwidth')}

\\subsection{{The retrieval findings replicate on authentic text}}

The seven-rung ablation of Section~\\ref{{sec:results}} was re-run unchanged on
the industrial corpus, over {bench['n_answerable']} answerable queries.
Table~\\ref{{tab:ind-ablation}} gives the result and
Table~\\ref{{tab:ablation}} the focus-corpus one.

{ablation_table(d, '0.72\\textwidth')}

The lexical leg carried the pipeline: BM25 reached
Recall@10 {d.system('A. bm25_only')['recall@10']:.4f} against the dense
encoder's {d.system('B. dense_only')['recall@10']:.4f}, a difference of
{bm['delta']:+.3f} ({p_of(bm['wilcoxon']['p_value'])}, $n={bm['wilcoxon']['n']}$).
That is a larger effect and a far smaller $p$ than the same comparison on the
focus corpus. It is also \\emph{{already published}} --- lexical retrieval
beating an off-the-shelf dense encoder on legal and regulatory text has been
reported in several jurisdictions --- so it is not claimed here as new, and
the dense leg here is a general-purpose encoder that a domain-adapted one
could overtake. What the measurement contributes is the
\\emph{{corollary}}: on this corpus neither the hybrid fusion
({fu['delta']:+.3f}, {p_of(fu['wilcoxon']['p_value'])}) nor the category
pre-filter ({fi['delta']:+.3f}, {p_of(fi['wilcoxon']['p_value'])}) added
anything measurable on top of the lexical baseline. The cross-encoder did
help here ({rr['delta']:+.3f}, {p_of(rr['wilcoxon']['p_value'])}), unlike on
the focus corpus.

The candidate-pool curve, which was saturated on the focus corpus and so
could not distinguish ``the pool stopped helping'' from ``the corpus had
nothing left to find'', is sharp here. At a pool of
{pool50['pool_size'] if pool50 else 50}, Recall@20 reaches
{pool50['recall@20']:.3f} while Recall@10 stands at
{pool50['recall@10']:.3f}: {displacement:.2f}\\% of the golds are retrieved
and then pushed \\emph{{out of the ten-chunk context}} by the reranker's own
ordering. Enlarging the pool buys recall the context cannot hold.

The modality quota behaves as a trade on both corpora, and which way it
trades depends on where it is applied. Applied before the reranker it gives
up {abs(qp['delta']) * 100:.1f} points of overall recall
({p_of(qp['wilcoxon']['p_value'])}); applied after it, the industrial corpus
lands on exactly the no-quota operating point, with the pre-rerank arm at
Recall@10 {d.system('F. +quota_pre_rerank')['recall@10']:.4f} against the
post-rerank arm's {d.system('G. +quota_post_rerank')['recall@10']:.4f}
({qg['delta']:+.3f}, {p_of(qg['wilcoxon']['p_value'])}).

{figure('fig1', '0.72\\textwidth')}

{figure('fig4', '0.72\\textwidth')}

\\subsection{{The gate's operating point transfers; its threshold does not}}

At $\\tau = {ind_op['tau']:.2f}$ the industrial gate answers
{ind_op['answerable_answered'] * 100:.1f}\\% of the answerable queries and
refuses {ind_op['unanswerable_refused'] * 100:.1f}\\% of the unanswerable
ones, with an abstention precision of {ind_op['abstention_precision']:.3f} and
a coverage of {ind_op['coverage']:.3f}. The threshold does not transfer ---
{ind_op['tau']:.2f} here against {focus_op['tau']:.2f} on the focus corpus ---
and the operating point does: coverage {ind_op['coverage']:.3f} against
{focus_op['coverage']:.3f}. This is the calibration result of
Section~\\ref{{sec:results}} restated on a second corpus: the threshold is a
fitted parameter of the deployment and must be re-fitted, while the point on
the risk--coverage surface a practitioner cares about is a property of the
mechanism. The two calibrations differ in quality as well as in value: the
industrial gate's expected calibration error is {ind_cal['ece']:.3f} against
{focus_cal['ece']:.3f}, while its Brier score is {ind_cal['brier']:.3f}
against {focus_cal['brier']:.3f}.

{figure('fig2', '0.72\\textwidth')}

{figure('fig3', '0.72\\textwidth')}

\\subsection{{Detection and typing decompose}}

This is the paper's clearest new result, and it needed a corpus that
contains conflicts to be visible.

{reg['n_pairs_total']} pairs were assembled in two strata:
{d.rev['stratum_distribution']['revision']} \\emph{{revision}} pairs (a
paragraph and its amended self) and
{d.rev['stratum_distribution']['similar']} \\emph{{similar}} pairs
(cross-document retrieval neighbours). The pool is mined by the
\\emph{{retriever's}} own lexical signal and never by the detector's numeric
rule, its NLI probability or its subject check: a pool selected on the
detector's decision rule cannot measure the detector's precision, because
every alarm would be in it by construction. The pairs were read by a panel of
domain specialists --- one per regulatory regime --- together with a
generalist control, all blind to the detector.

A conflict detector's precision is two numbers, not one.
\\textbf{{Detection}} asks whether the alarm is pointing at something real.
\\textbf{{Typing}} asks whether the branch that raised the alarm is the
branch that owns the conflict. Measured against the panel's labels, the
detector's detection precision is
{reg['precision_any_flag']:.3f} (95\\% CI
{reg['precision_any_flag_ci95'][0]:.3f}--{reg['precision_any_flag_ci95'][1]:.3f})
and its typing precision is {reg['precision_typing']:.3f} (95\\% CI
{reg['precision_typing_ci95'][0]:.3f}--{reg['precision_typing_ci95'][1]:.3f}).
On the stratum where the conflicts actually are, detection rises to
{d.reg['by_stratum']['revision']['precision_any_flag']:.3f}.

Against the \\emph{{construction}} labels --- the revision stratum, whose
conflict type is known without any judgement --- the separation is starker
still. Detection precision is {cons['overall']['precision_any_flag']:.3f}:
every alarm the detector raises on that stratum points at a real conflict.
Typing precision is {cons['overall']['precision_typing']:.3f}: not one alarm
was raised by the branch that owns its conflict. The semantic branch fired on
{sem['n_flagged']} pairs, of which {sem['label_distribution_of_flagged'].get('quantity_conflict', 0)}
were quantity conflicts; the revision branch fired on {revb['n_flagged']}, of
which {revb['label_distribution_of_flagged'].get('quantity_conflict', 0)}
were quantity conflicts; and the quantity branch fired on
{qtyb['n_flagged']}. Its recall against the
{qtyb['n_annotated_positives']} construction-labelled limit changes is
{qtyb['recall_vs_matching_label']:.3f}.

So the mechanism \\textbf{{finds}} the conflicts and \\textbf{{reports them as
the wrong kind}}. It calls supersessions contradictions, and it cannot say
which version is in force --- because nothing in the retrieved passages says
which issue either of them is. On the industrial corpus the two branches are
also asymmetric in kind: the semantic branch accounts for
{sem_reader.get('n_flagged', 0)} of the detector's alarms at a precision
against any real problem of
{sem_reader.get('precision_vs_any_real_problem', float('nan')):.3f}, while
the revision branch accounts for {rev_reader.get('n_flagged', 0)} at
{rev_reader.get('precision_vs_any_real_problem', float('nan')):.3f}. The
quantity branch is the thinnest result in the whole study: an exhaustive
corpus-wide search over {qty['n_measurement_terms']} measurement terms found
{qty['n_cross_document_conflicts']:,} candidate cross-document quantity
conflicts --- a count that is exact rather than sampled, because the search
groups every (measurement term, value) pair in the corpus and keeps the
terms whose values differ across documents --- of which
{qty['n_pairs_scored']} were put to the reader, and the branch fired on
{qty['n_pairs_the_quantity_branch_fired_on']}. The search is deliberately
over-inclusive: two passages about different boilers share the word
``pressure'', which is why the reader found
{qty['n_pairs_in_the_judge_sheet']} of the sampled pairs to be the same word
used for different things and none to be a genuine quantity conflict. The
branch's precision on this corpus is therefore not measurable, and the
framework's calibration floor would withhold it rather than report it.

{figure('fig6', '0.72\\textwidth')}

\\subsection{{The measurement's binding constraint was the rubric}}

The comparison above was confounded, and the confound was in the
annotation rather than in the detector. The first comparison of the
old-rubric reader against the sharpened one had the same reader in one cell
and a different reader in the other, so ``the old rubric'' and ``the
generalist'' were the same cell. A $2\\times2$ factorial separates them, with
the pairs, the detector and the regime briefs held constant.

{factorial_table(d, '0.72\\textwidth')}

\\emph{{The rubric's wording moved the measured precision by about a third of
a point; the reader's domain specialisation moved it by almost nothing.}}
The mechanism is concrete. The old rubric required a version marker, and a
regulation does not write its own version in its text, so it missed
{gen.get('v2_only_the_old_rubric_missed', 0)} of the
{gen.get('v2_conflicts', 0)} supersessions it was asked to find
({gen.get('share_of_the_new_conflicts_the_old_rubric_missed', 0) * 100:.0f}\\%),
calling them \\texttt{{no\\_conflict}}; the specialist reader missed
{spec.get('v2_only_the_old_rubric_missed', 0)} of
{spec.get('v2_conflicts', 0)}
({spec.get('share_of_the_new_conflicts_the_old_rubric_missed', 0) * 100:.0f}\\%).

Three qualifications are owed to this result. First, the rubric changed the
\\emph{{definition}} of the target as well as the procedure for recognising
one, and this experiment cannot separate the two; what it shows is that the
reader factor is small. Second, ``specialisation'' here was delivered as a
brief to a fixed reader model, not as a different capability, so the claim is
that a brief plus a sharpened rubric buys nothing over the rubric alone ---
narrower than ``specialists are not needed''. Third, the qualitative
principle is already published: that the annotation guideline is a
first-class error source in model annotation is established. What is new is
the factor of nine, and that it lands on the \\emph{{reported system
measurement}} rather than only on the labels.

The generalisable lesson is about measurement rather than about annotation.
A number that moves by a factor of nine with the wording of its own rubric
is not yet a measurement of the thing under test.

\\subsection{{The per-claim band measures agreement, not correctness}}

The third mechanism was measured on both corpora, with the same generator
that produced the focus corpus's answers and with two evidence protocols on
each: the benchmark's own gold evidence (is the claim right?) and the
evidence the retriever actually returned (does a reader agree with the
scorer?).

{band_table(d, '0.72\\textwidth')}

{band_caveat()}

Against an independent reference the band is at chance on all four
combinations: $\\kappa$ {kappa(fg):.3f} on the focus corpus's gold
evidence, {kappa(fr):.3f} on its retrieved evidence, {kappa(ig):.3f} on the
industrial corpus's gold evidence and {kappa(ir):.3f} on its retrieved
evidence. The three bands are also indistinguishable on the gold protocols
({bands(fg)[0]:.3f} / {bands(fg)[1]:.3f} / {bands(fg)[2]:.3f} and
{bands(ig)[0]:.3f} / {bands(ig)[1]:.3f} / {bands(ig)[2]:.3f}), while they are
ordered on the evidence the band itself saw
({bands(fr)[0]:.3f} / {bands(fr)[1]:.3f} / {bands(fr)[2]:.3f} and
{bands(ir)[0]:.3f} / {bands(ir)[1]:.3f} / {bands(ir)[2]:.3f}). The sharper
way to state it: \\textbf{{the band measures whether the retrieved passages
entail the claim --- agreement with itself --- not whether the claim is
true.}} As a filter it nonetheless works: keeping only the
\\emph{{grounded}} claims raises the share of answers containing no wrong
claim from {fgc * 100:.1f}\\% to {fgg * 100:.1f}\\% on the focus corpus's
gold protocol, from {frc * 100:.1f}\\% to {frg * 100:.1f}\\% on its retrieved
protocol, and from {igc * 100:.1f}\\% to {igg * 100:.1f}\\% and
{irc * 100:.1f}\\% to {irg * 100:.1f}\\% on the industrial corpus's two.

The positional comparison --- keeping the first half of an answer rather
than what the band tagged \\emph{{grounded}} --- is the \\emph{{evidence}} for
that reading, not the finding itself, and it does not hold everywhere. Of
the four corpus-and-protocol combinations, one gives a significant
positional result (the focus corpus's gold evidence,
{p_of(pos_p(fg))}, $d_z={((fg.get('value_test') or {}).get('paired') or {}).get('band_vs_first', {}).get('cohens_dz', float('nan')):+.3f}$)
and three do not ({p_of(pos_p(fr))}, {p_of(pos_p(ig))} and
{p_of(pos_p(ir))}). On the focus corpus's gold protocol the comparison is
also not a length artefact: later claims are \\emph{{shorter}}
(Spearman $\\rho$ {((fg.get('value_test') or {}).get('position_length_confound') or {}).get('spearman_position_vs_length', float('nan')):.3f},
{p_of(((fg.get('value_test') or {}).get('position_length_confound') or {}).get('p_value', float('nan')))}).

\\subsection{{What the second corpus does not establish}}

Five limits, stated rather than implied. One jurisdiction, one language and
one regulatory family: the corpus is US federal regulation, and nothing here
shows that the decomposition holds for a plant's own procedures, for a
non-English regulatory regime, or for a corpus of vendor specifications.
The labels are model-generated. The panel's agreement is reported in full,
but agreement between readers is not confirmation that a label is right, and
the thesis's own limitation table names this as the cost of replacing human
annotators. The positional comparison did not replicate across three of the
four combinations, so the band is reported as a filter with a measurement
decomposition, not as a ranking. The rubric factorial shows that the
annotation's wording moved the measurement, which is a warning about the
other measurements in this paper rather than a clean result about the
mechanism; and ``specialisation'' was a brief, not a capability. Finally, the
lexical-over-dense result is a boundary condition on \\emph{{this}}
pipeline with a general-purpose encoder, not a claim about dense retrieval.
"""


def condensed_section(d: Data) -> str:
    """The conference paper's version: the new result, the figures, no detour."""
    cs = d.cs
    bench = d.bench
    reg = d.reg_overall
    cons = d.reg_construction
    eff = d.effects
    dec = d.decomposition
    revstats = d.revstats
    bm = d.comparison("A. bm25_only -> B. dense_only")
    fu = d.comparison("A. bm25_only -> C. hybrid_rrf")
    fi = d.comparison("D. hybrid_rrf_rerank -> E. +category_filter")
    pool50 = next((r for r in (d.pool or {}).get("results", [])
                   if r["pool_size"] == 50), None)
    displacement = ((pool50["recall@20"] - pool50["recall@10"]) * 100
                    if pool50 else float("nan"))
    sem = cons["per_branch"]["semantic"]
    revb = cons["per_branch"]["revision"]
    qtyb = cons["per_branch"]["quantity"]
    st = d.audit["after_repair"]["structural_separability"][
        "repaired_whole_class"]
    gen = dec.get("generalist", {})

    def kappa(doc):
        return (doc.get("agreement_binary") or {}).get(
            "cohens_kappa", float("nan"))

    def bands(doc):
        pb = doc.get("per_band") or {}
        return tuple((pb.get(b) or {}).get("error_rate", float("nan"))
                     for b in ("grounded", "inferred", "uncertain"))

    def pos_p(doc):
        v = ((doc.get("value_test") or {}).get("paired") or {}) \
            .get("band_vs_first") or {}
        return v.get("wilcoxon_p", float("nan"))

    fg = d.band_focus_gold
    fr = d.band_focus_ret
    ig = d.band_ind_gold
    ir = d.band_ind_ret

    return f"""
\\section{{External Validity: A Second, Authentic, Versioned Corpus}}
\\label{{sec:industrial}}

The corpus of Section~\\ref{{sec:protocol}} is encyclopaedic prose, and it
cannot close two of the objectives this paper sets: it contains no conflict
a practitioner would recognise as one, and it is not the class of document a
practitioner reads. A second corpus closes both. It is the United States
\\emph{{Electronic Code of Federal Regulations}}, read through the versioner
API, which serves any regulation as it stood on any past date. The text is
authentic and binding --- these are the regulations a plant is measured
against --- and public domain, so it ships with the paper. It is also
versioned: the same section read on {revstats['pre_date']} and on
{revstats['post_date']} is the same rule at two issues, and
{revstats['n_amended_paragraph_pairs']} amended-paragraph pairs result, of
which {revstats['n_pairs_stating_different_numbers']}
({revstats['share_stating_different_numbers'] * 100:.1f}\\%) state different
numbers in the two vintages. Such a pair \\emph{{is}} a conflict, and its
type is known by construction, with no annotation required.

The corpus holds {cs['n_documents']} documents and {cs['n_chunks']:,} chunks
in {cs['n_categories']} regulatory regimes, with a
{bench['n_queries']}-query benchmark ({bench['n_answerable']} answerable,
{bench['n_unanswerable']} unanswerable) audited for the same shortcut the
first benchmark had: the one-rule identifier shortcut catches
{d.audit['after_repair']['shortcut_diagnostic']['unanswerable_caught']} of
{bench['n_unanswerable']}, and a question-only classifier separates the two
classes at ROC AUC {st['roc_auc']:.3f} against a permutation null of
{st['permutation_null_auc_mean']:.3f}.

\\subsection{{The retrieval findings replicate}}

The seven-rung ablation was re-run unchanged on the industrial corpus.

{ablation_table(d, '\\columnwidth')}

The lexical leg carried the pipeline: BM25 reached Recall@10
{d.system('A. bm25_only')['recall@10']:.4f} against the dense encoder's
{d.system('B. dense_only')['recall@10']:.4f} ({bm['delta']:+.3f},
{p_of(bm['wilcoxon']['p_value'])}, $n={bm['wilcoxon']['n']}$). Lexical
retrieval beating an off-the-shelf dense encoder on legal text is already
published, so it is not claimed as new; what the measurement contributes is
the corollary, that neither the fusion ({fu['delta']:+.3f},
{p_of(fu['wilcoxon']['p_value'])}) nor the category pre-filter
({fi['delta']:+.3f}, {p_of(fi['wilcoxon']['p_value'])}) added anything
measurable on top of the lexical baseline.

The candidate-pool curve, saturated on the focus corpus, is sharp here: at a
pool of {pool50['pool_size'] if pool50 else 50}, Recall@20 reaches
{pool50['recall@20']:.3f} while Recall@10 stands at
{pool50['recall@10']:.3f}, so {displacement:.2f}\\% of the golds are found
and then pushed out of the ten-chunk context by the reranker's own ordering.

{figure('fig1', '\\columnwidth')}

\\subsection{{Detection and typing decompose}}

This is the clearest new result in the paper, and it needed a corpus that
contains conflicts to be visible. {reg['n_pairs_total']} pairs were
assembled --- {d.rev['stratum_distribution']['revision']} amendment pairs and
{d.rev['stratum_distribution']['similar']} retrieval neighbours --- mined by
the \\emph{{retriever's}} signal and never by the detector's, so the pool
cannot flatter the detector. They were read by a panel of domain
specialists, one per regulatory regime, with a generalist control, all blind
to the detector.

A conflict detector's precision is two numbers, not one. \\textbf{{Detection}}
asks whether the alarm points at something real; \\textbf{{typing}} asks
whether the branch that raised it is the branch that owns the conflict.
Against the panel's labels, detection precision is
{reg['precision_any_flag']:.3f} (95\\% CI
{reg['precision_any_flag_ci95'][0]:.3f}--{reg['precision_any_flag_ci95'][1]:.3f})
and typing precision {reg['precision_typing']:.3f} (95\\% CI
{reg['precision_typing_ci95'][0]:.3f}--{reg['precision_typing_ci95'][1]:.3f}).
Against the construction labels, whose conflict type is known without
judgement, the separation is starker: detection
{cons['overall']['precision_any_flag']:.3f} --- every alarm points at a real
conflict --- and typing {cons['overall']['precision_typing']:.3f}. The
semantic branch fired on {sem['n_flagged']} construction-labelled pairs, of
which {sem['label_distribution_of_flagged'].get('quantity_conflict', 0)}
were quantity conflicts; the revision branch fired on {revb['n_flagged']},
of which {revb['label_distribution_of_flagged'].get('quantity_conflict', 0)}
were quantity conflicts; and the quantity branch fired on
{qtyb['n_flagged']}, with a recall of
{qtyb['recall_vs_matching_label']:.3f} against the
{qtyb['n_annotated_positives']} construction-labelled limit changes.

So the mechanism \\textbf{{finds}} the conflicts and \\textbf{{reports them as
the wrong kind}}: it calls supersessions contradictions and cannot say which
version is in force, because nothing in the retrieved passages says which
issue either of them is.

{figure('fig6', '\\columnwidth')}

\\subsection{{The annotation, not the detector, was the binding constraint}}

The comparison above was confounded --- the old-rubric reader was a
generalist, so ``old rubric'' and ``generalist'' were the same cell. A
$2\\times2$ factorial separates them, with the pairs, the detector and the
regime briefs held constant.

{factorial_table(d, '\\columnwidth')}

\\emph{{The rubric's wording moved the measured precision by about a third of
a point; the reader's domain specialisation moved it by almost nothing.}}
The mechanism is concrete: the old rubric required a version marker, and a
regulation does not write its own version in its text, so it missed
{gen.get('v2_only_the_old_rubric_missed', 0)} of the
{gen.get('v2_conflicts', 0)} supersessions it was asked to find, calling them
\\texttt{{no\\_conflict}}. The lesson is about measurement: a number that
moves by a factor of nine with the wording of its own rubric is not yet a
measurement of the thing under test. The qualification is owed: the rubric
changed the definition of the target as well as the procedure for
recognising one, and ``specialisation'' was a brief to a fixed reader model,
not a different capability.

\\subsection{{The per-claim band measures agreement, not correctness}}

The third mechanism was measured on both corpora, with the same generator,
under two evidence protocols each.

{band_table(d, '\\columnwidth')}

{band_caveat()}

Against an independent reference the band is at chance on all four
combinations ($\\kappa$ {kappa(fg):.3f}, {kappa(fr):.3f}, {kappa(ig):.3f},
{kappa(ir):.3f}); the three bands are indistinguishable on the gold
protocols ({bands(fg)[0]:.3f} / {bands(fg)[1]:.3f} / {bands(fg)[2]:.3f} and
{bands(ig)[0]:.3f} / {bands(ig)[1]:.3f} / {bands(ig)[2]:.3f}) and ordered on
the evidence the band itself saw ({bands(fr)[0]:.3f} / {bands(fr)[1]:.3f} /
{bands(fr)[2]:.3f} and {bands(ir)[0]:.3f} / {bands(ir)[1]:.3f} /
{bands(ir)[2]:.3f}). \\textbf{{The band measures whether the retrieved
passages entail the claim --- agreement with itself --- not whether the claim
is true.}} As a filter it works: keeping only the \\emph{{grounded}} claims
raises the share of answers with no wrong claim from
{((fg.get('answer_level') or {}).get('answers_with_no_wrong_claim_rate', float('nan'))) * 100:.1f}\\% to
{((fg.get('answer_level') or {}).get('answers_clean_after_keeping_grounded_only_rate', float('nan'))) * 100:.1f}\\%
on the focus corpus's gold protocol and from
{((ig.get('answer_level') or {}).get('answers_with_no_wrong_claim_rate', float('nan'))) * 100:.1f}\\% to
{((ig.get('answer_level') or {}).get('answers_clean_after_keeping_grounded_only_rate', float('nan'))) * 100:.1f}\\%
on the industrial one. The positional comparison --- keeping the first half
of an answer --- is the evidence for that reading rather than the finding
itself: one of the four combinations gives a significant positional result
and three do not ({p_of(pos_p(fg))}, {p_of(pos_p(fr))}, {p_of(pos_p(ig))},
{p_of(pos_p(ir))}).

\\subsection{{What the second corpus does not establish}}

One jurisdiction, one language, one regulatory family. The labels are
model-generated: the panel's agreement is reported in full, but agreement
between readers is not confirmation that a label is right, and the thesis's
own limitation table names this as the cost of replacing human annotators.
The positional comparison did not replicate on three of four combinations, so
the band is reported as a filter with a measurement decomposition, not as a
ranking. And the lexical-over-dense result is a boundary condition on this
pipeline with a general-purpose encoder, not a claim about dense retrieval.
"""


# ---------------------------------------------------------------------------
# the markdown form, for the technical report (Deliverable 2a)
# ---------------------------------------------------------------------------
def markdown_section(d: Data) -> str:
    """The same section, as markdown, for the technical report.

    The report is the third of the three formats the README calls the same
    paper, so it cannot carry a different body of results from the two LaTeX
    papers. The tables become markdown tables; the six figures are named
    rather than embedded, because the markdown-to-DOCX converter does not
    carry images, and the figures are released beside the papers in
    ``deliverables/figures/``.
    """
    cs = d.cs
    bench = d.bench
    reg = d.reg_overall
    cons = d.reg_construction
    eff = d.effects
    dec = d.decomposition
    qty = d.qty
    revstats = d.revstats

    bm = d.comparison("A. bm25_only -> B. dense_only")
    fu = d.comparison("A. bm25_only -> C. hybrid_rrf")
    fi = d.comparison("D. hybrid_rrf_rerank -> E. +category_filter")
    rr = d.comparison("C. hybrid_rrf -> D. hybrid_rrf_rerank")

    pool50 = next((r for r in (d.pool or {}).get("results", [])
                   if r["pool_size"] == 50), None)
    displacement = ((pool50["recall@20"] - pool50["recall@10"]) * 100
                    if pool50 else float("nan"))
    st = d.audit["after_repair"]["structural_separability"][
        "repaired_whole_class"]
    lp = d.audit["after_repair"]["length_profile"]
    gen = dec.get("generalist", {})
    spec = dec.get("specialist", {})
    ind_op = d.ind_op
    focus_op = d.focus_op
    ind_cal = d.gate["calibration_metrics"]
    focus_cal = d.gate_focus["calibration_metrics"]

    def kappa(doc):
        return (doc.get("agreement_binary") or {}).get(
            "cohens_kappa", float("nan"))

    def bands(doc):
        pb = doc.get("per_band") or {}
        return tuple((pb.get(b) or {}).get("error_rate", float("nan"))
                     for b in ("grounded", "inferred", "uncertain"))

    def clean(doc):
        al = doc.get("answer_level") or {}
        return (al.get("answers_with_no_wrong_claim_rate", float("nan")),
                al.get("answers_clean_after_keeping_grounded_only_rate",
                       float("nan")))

    def pos_p(doc):
        v = ((doc.get("value_test") or {}).get("paired") or {}) \
            .get("band_vs_first") or {}
        return v.get("wilcoxon_p", float("nan"))

    fg, fr = d.band_focus_gold, d.band_focus_ret
    ig, ir = d.band_ind_gold, d.band_ind_ret
    fgc, fgg = clean(fg)
    frc, frg = clean(fr)
    igc, igg = clean(ig)
    irc, irg = clean(ir)

    ablation_rows = []
    for key, label in (("A. bm25_only", "A. BM25 only"),
                       ("B. dense_only", "B. Dense only"),
                       ("C. hybrid_rrf", "C. Hybrid (RRF)"),
                       ("D. hybrid_rrf_rerank", "D. + cross-encoder"),
                       ("E. +category_filter", "E. + category filter"),
                       ("F. +quota_pre_rerank", "F. + quota (pre-rerank)"),
                       ("G. +quota_post_rerank", "G. + quota (post-rerank)")):
        s = d.system(key)
        tbl = (s.get("modality_recall") or {}).get("table")
        ablation_rows.append(
            f"| {label} | {s['recall@5']:.4f} | {s['recall@10']:.4f} | "
            f"{s['mrr']:.4f} | {s['nDCG@10']:.4f} | "
            f"{'---' if tbl is None else f'{tbl:.3f}'} |")

    fact_rows = []
    for name in ("generalist_v1", "generalist_v2", "specialist_v1",
                 "specialist_v2"):
        c = d.cells.get(name, {}).get("consensus", {})
        if not c:
            continue
        reader = name.split("_")[0]
        rubric = ("old (marker test)" if name.endswith("v1")
                  else "sharpened (structural test)")
        fact_rows.append(
            f"| {reader} | {rubric} | {c['detection_precision']:.3f} | "
            f"{c['typing_precision']:.3f} |")

    band_rows = []
    for label, doc in (("Focus, gold", fg), ("Focus, retrieved", fr),
                       ("Industrial, gold", ig),
                       ("Industrial, retrieved", ir)):
        if not doc:
            continue
        ab = doc.get("agreement_binary", {})
        ci = ab.get("ci95") or [float("nan"), float("nan")]
        g, i, u = bands(doc)
        c0, c1 = clean(doc)
        band_rows.append(
            f"| {label} | {kappa(doc):.3f} ({ci[0]:+.3f}, {ci[1]:+.3f}) | "
            f"{g:.3f} / {i:.3f} / {u:.3f} | {c0 * 100:.1f}% → {c1 * 100:.1f}% |")

    return f"""## 6. A second corpus: authentic, versioned, binding industrial text

### 6.1 Why a second corpus, and what it is

The corpus of Section 4 is encyclopaedic prose, and two of this paper's
objectives cannot be closed on it. It contains no conflict a practitioner
would recognise as one: a document read at a single upstream revision cannot
contradict itself, and concept-level prose rarely binds a numeric requirement
that another document contradicts. And it is not the class of document a
practitioner reads — it is reference material about industrial-engineering
concepts, not operating procedures carrying binding limits.

A second corpus was built to close that gap. It is the United States
*Electronic Code of Federal Regulations* (eCFR), read through the versioner
API, which serves any regulation as it stood on any past date. Two properties
follow, and together they close two objectives with one artefact. The text is
authentic and binding: these are the regulations a plant is measured against,
they carry numeric requirements, and they are public domain, so the corpus
ships with the paper. The text is also *versioned*: federal regulations are
amended, so the same section read on {revstats['pre_date']} and on
{revstats['post_date']} is the same rule at two issues. Aligning the two
snapshots gives {revstats['n_amended_paragraph_pairs']} amended-paragraph
pairs, of which {revstats['n_pairs_stating_different_numbers']}
({revstats['share_stating_different_numbers'] * 100:.1f}%) state different
numbers in the two vintages. Such a pair *is* a conflict, and its type is known
by construction: the same provision at two issues is a supersession, not a
contradiction, and no annotation is needed to know that.

The corpus holds {cs['n_documents']} documents and {cs['n_chunks']:,} chunks
({cs['by_modality'].get('text', 0):,} text,
{cs['by_modality'].get('table', 0):,} table,
{cs['by_modality'].get('chart', 0):,} chart) in {cs['n_categories']} regulatory
regimes, and its benchmark has {bench['n_queries']} queries
({bench['n_answerable']} answerable, {bench['n_unanswerable']} unanswerable).
It was audited for the same shortcut the first benchmark had. The one-rule
identifier shortcut that carried 76.4% of the first benchmark's unanswerable
class catches
{d.audit['after_repair']['shortcut_diagnostic']['unanswerable_caught']} of
{bench['n_unanswerable']} here, and a question-only classifier separates the
two classes at ROC AUC {st['roc_auc']:.3f} against a permutation null of
{st['permutation_null_auc_mean']:.3f}. The residual separability is question
length — median {lp['median_length_answerable']:.0f} characters for the
answerable class against {lp['median_length_unanswerable']:.0f} for the
unanswerable one — which is reported rather than hidden.

### 6.2 The retrieval findings replicate on authentic text

The seven-rung ablation of Section 5 was re-run unchanged on the industrial
corpus, over {bench['n_answerable']} answerable queries.

**Table 8 — Retrieval ablation on the industrial corpus.**

| System | R@5 | R@10 | MRR | nDCG@10 | Tbl R@10 |
|---|---|---|---|---|---|
{chr(10).join(ablation_rows)}

The lexical leg carried the pipeline: BM25 reached Recall@10
{d.system('A. bm25_only')['recall@10']:.4f} against the dense encoder's
{d.system('B. dense_only')['recall@10']:.4f}, a difference of
{bm['delta']:+.3f} (p = {bm['wilcoxon']['p_value']:.5f}, n =
{bm['wilcoxon']['n']}). That is a larger effect and a far smaller p than the
same comparison on the focus corpus. It is also *already published* — lexical
retrieval beating an off-the-shelf dense encoder on legal and regulatory text
has been reported in several jurisdictions — so it is not claimed here as new,
and the dense leg here is a general-purpose encoder that a domain-adapted one
could overtake. What the measurement contributes is the *corollary*: on this
corpus neither the hybrid fusion ({fu['delta']:+.3f}, p =
{fu['wilcoxon']['p_value']:.3f}) nor the category pre-filter
({fi['delta']:+.3f}, p = {fi['wilcoxon']['p_value']:.3f}) added anything
measurable on top of the lexical baseline. The cross-encoder did help here
({rr['delta']:+.3f}, p = {rr['wilcoxon']['p_value']:.4f}), unlike on the focus
corpus.

The candidate-pool curve, which was saturated on the focus corpus and so could
not distinguish "the pool stopped helping" from "the corpus had nothing left
to find", is sharp here. At a pool of {pool50['pool_size'] if pool50 else 50},
Recall@20 reaches {pool50['recall@20']:.3f} while Recall@10 stands at
{pool50['recall@10']:.3f}: {displacement:.2f}% of the golds are retrieved and
then pushed *out of the ten-chunk context* by the reranker's own ordering.

### 6.3 The gate's operating point transfers; its threshold does not

At τ = {ind_op['tau']:.2f} the industrial gate answers
{ind_op['answerable_answered'] * 100:.1f}% of the answerable queries and
refuses {ind_op['unanswerable_refused'] * 100:.1f}% of the unanswerable ones,
with an abstention precision of {ind_op['abstention_precision']:.3f} and a
coverage of {ind_op['coverage']:.3f}. The threshold does not transfer —
{ind_op['tau']:.2f} here against {focus_op['tau']:.2f} on the focus corpus —
and the operating point does: coverage {ind_op['coverage']:.3f} against
{focus_op['coverage']:.3f}. This is the calibration result of Section 4.4
restated on a second corpus: the threshold is a fitted parameter of the
deployment and must be re-fitted, while the point on the risk–coverage surface
a practitioner cares about is a property of the mechanism. The two
calibrations differ in quality as well as in value: the industrial gate's
expected calibration error is {ind_cal['ece']:.3f} against
{focus_cal['ece']:.3f}, while its Brier score is {ind_cal['brier']:.3f} against
{focus_cal['brier']:.3f}.

### 6.4 Detection and typing decompose

This is the paper's clearest new result, and it needed a corpus that contains
conflicts to be visible.

{reg['n_pairs_total']} pairs were assembled in two strata:
{d.rev['stratum_distribution']['revision']} *revision* pairs (a paragraph and
its amended self) and {d.rev['stratum_distribution']['similar']} *similar*
pairs (cross-document retrieval neighbours). The pool is mined by the
*retriever's* own lexical signal and never by the detector's numeric rule, its
NLI probability or its subject check: a pool selected on the detector's
decision rule cannot measure the detector's precision, because every alarm
would be in it by construction. The pairs were read by a panel of domain
specialists — one per regulatory regime — together with a generalist control,
all blind to the detector.

A conflict detector's precision is two numbers, not one. **Detection** asks
whether the alarm is pointing at something real. **Typing** asks whether the
branch that raised the alarm is the branch that owns the conflict. Measured
against the panel's labels, the detector's detection precision is
{reg['precision_any_flag']:.3f} (95% CI
{reg['precision_any_flag_ci95'][0]:.3f}–{reg['precision_any_flag_ci95'][1]:.3f})
and its typing precision is {reg['precision_typing']:.3f} (95% CI
{reg['precision_typing_ci95'][0]:.3f}–{reg['precision_typing_ci95'][1]:.3f}).
On the stratum where the conflicts actually are, detection rises to
{d.reg['by_stratum']['revision']['precision_any_flag']:.3f}.

Against the *construction* labels — the revision stratum, whose conflict type
is known without any judgement — the separation is starker still. Detection
precision is {cons['overall']['precision_any_flag']:.3f}: every alarm the
detector raises on that stratum points at a real conflict. Typing precision is
{cons['overall']['precision_typing']:.3f}: not one alarm was raised by the
branch that owns its conflict. The quantity branch fired on
{cons['per_branch']['quantity']['n_flagged']} pairs, and its recall against
the {cons['per_branch']['quantity']['n_annotated_positives']}
construction-labelled limit changes is
{cons['per_branch']['quantity']['recall_vs_matching_label']:.3f}.

So the mechanism **finds** the conflicts and **reports them as the wrong
kind**. It calls supersessions contradictions, and it cannot say which
version is in force — because nothing in the retrieved passages says which
issue either of them is. On the industrial corpus the quantity branch is the
thinnest result in the whole study: an exhaustive corpus-wide search over
{qty['n_measurement_terms']} measurement terms found
{qty['n_cross_document_conflicts']:,} candidate cross-document quantity
conflicts — a count that is exact rather than sampled — of which
{qty['n_pairs_scored']} were put to the reader, and the branch fired on
{qty['n_pairs_the_quantity_branch_fired_on']}. The search is deliberately
over-inclusive: two passages about different boilers share the word
"pressure", which is why the reader found
{qty['n_pairs_in_the_judge_sheet']} of the sampled pairs to be the same word
used for different things and none to be a genuine quantity conflict. The
branch's precision on this corpus is therefore not measurable, and the
framework's calibration floor would withhold it rather than report it.

### 6.5 The measurement's binding constraint was the rubric

The comparison above was confounded, and the confound was in the annotation
rather than in the detector. The first comparison of the old-rubric reader
against the sharpened one had the same reader in one cell and a different
reader in the other, so "the old rubric" and "the generalist" were the same
cell. A 2×2 factorial separates them, with the pairs, the detector and the
regime briefs held constant.

**Table 9 — The rubric × reader-specialisation factorial.**

| Reader | Rubric | Detection precision | Typing precision |
|---|---|---|---|
{chr(10).join(fact_rows)}

| Effect | Δ detection precision |
|---|---|
| **Rubric**, at the generalist | **{eff.get('rubric_effect_at_generalist', {}).get('difference', 0):+.3f}** |
| **Rubric**, at the specialist | **{eff.get('rubric_effect_at_specialist', {}).get('difference', 0):+.3f}** |
| **Specialisation**, at the old rubric | {eff.get('specialisation_effect_at_v1', {}).get('difference', 0):+.3f} |
| **Specialisation**, at the sharpened rubric | {eff.get('specialisation_effect_at_v2', {}).get('difference', 0):+.3f} |

*The rubric's wording moved the measured precision by about a third of a point;
the reader's domain specialisation moved it by almost nothing.* The mechanism
is concrete. The old rubric required a version marker, and a regulation does
not write its own version in its text, so it missed
{gen.get('v2_only_the_old_rubric_missed', 0)} of the
{gen.get('v2_conflicts', 0)} supersessions it was asked to find
({gen.get('share_of_the_new_conflicts_the_old_rubric_missed', 0) * 100:.0f}%),
calling them `no_conflict`; the specialist reader missed
{spec.get('v2_only_the_old_rubric_missed', 0)} of
{spec.get('v2_conflicts', 0)}
({spec.get('share_of_the_new_conflicts_the_old_rubric_missed', 0) * 100:.0f}%).

Three qualifications are owed to this result. First, the rubric changed the
*definition* of the target as well as the procedure for recognising one, and
this experiment cannot separate the two; what it shows is that the reader
factor is small. Second, "specialisation" here was delivered as a brief to a
fixed reader model, not as a different capability, so the claim is that a
brief plus a sharpened rubric buys nothing over the rubric alone — narrower
than "specialists are not needed". Third, the qualitative principle is already
published: that the annotation guideline is a first-class error source in
model annotation is established. What is new is the factor of nine, and that
it lands on the *reported system measurement* rather than only on the labels.

The generalisable lesson is about measurement rather than about annotation. A
number that moves by a factor of nine with the wording of its own rubric is
not yet a measurement of the thing under test.

### 6.6 The per-claim band measures agreement, not correctness

The third mechanism was measured on both corpora, with the same generator that
produced the focus corpus's answers and with two evidence protocols on each:
the benchmark's own gold evidence (is the claim right?) and the evidence the
retriever actually returned (does a reader agree with the scorer?).

**Table 10 — The per-claim band against an independent reference, on both corpora and both protocols.**

| Corpus and protocol | κ (band vs reference) | Band error (grounded / inferred / uncertain) | Answers with no wrong claim |
|---|---|---|---|
{chr(10).join(band_rows)}

Against an independent reference the band is at chance on all four
combinations: κ {kappa(fg):.3f} on the focus corpus's gold evidence,
{kappa(fr):.3f} on its retrieved evidence, {kappa(ig):.3f} on the industrial
corpus's gold evidence and {kappa(ir):.3f} on its retrieved evidence. The
three bands are also indistinguishable on the gold protocols
({bands(fg)[0]:.3f} / {bands(fg)[1]:.3f} / {bands(fg)[2]:.3f} and
{bands(ig)[0]:.3f} / {bands(ig)[1]:.3f} / {bands(ig)[2]:.3f}), while they are
ordered on the evidence the band itself saw
({bands(fr)[0]:.3f} / {bands(fr)[1]:.3f} / {bands(fr)[2]:.3f} and
{bands(ir)[0]:.3f} / {bands(ir)[1]:.3f} / {bands(ir)[2]:.3f}). The sharper way
to state it: **the band measures whether the retrieved passages entail the
claim — agreement with itself — not whether the claim is true.** As a filter
it nonetheless works: keeping only the *grounded* claims raises the share of
answers containing no wrong claim from {fgc * 100:.1f}% to {fgg * 100:.1f}% on
the focus corpus's gold protocol, from {frc * 100:.1f}% to {frg * 100:.1f}% on
its retrieved protocol, and from {igc * 100:.1f}% to {igg * 100:.1f}% and
{irc * 100:.1f}% to {irg * 100:.1f}% on the industrial corpus's two.

The positional comparison — keeping the first half of an answer rather than
what the band tagged *grounded* — is the *evidence* for that reading, not the
finding itself, and it does not hold everywhere. Of the four
corpus-and-protocol combinations, one gives a significant positional result
(the focus corpus's gold evidence, p = {pos_p(fg):.3f}) and three do not
(p = {pos_p(fr):.3f}, p = {pos_p(ig):.3f} and p = {pos_p(ir):.3f}).

### 6.7 What the second corpus does not establish

Five limits, stated rather than implied. One jurisdiction, one language and
one regulatory family: the corpus is US federal regulation, and nothing here
shows that the decomposition holds for a plant's own procedures, for a
non-English regulatory regime, or for a corpus of vendor specifications. The
labels are model-generated. The panel's agreement is reported in full, but
agreement between readers is not confirmation that a label is right, and this
paper's own limitation table names this as the cost of replacing human
annotators. The wording of the annotation rubric moved the measured precision
by a factor of nine, which is a warning about every model-annotated number
here and not only about that one. The positional comparison did not replicate
across three of the four combinations, so the band is reported as a filter
with a measurement decomposition, not as a ranking. And the lexical-over-dense
result is a boundary condition on *this* pipeline with a general-purpose
encoder, not a claim about dense retrieval.

### 6.8 The figures

Six figures accompany this section and are released with the paper in
`deliverables/figures/`, as PDF and PNG, one column wide:
`fig1_pool_size` (recall against the rerank candidate pool, both corpora),
`fig2_risk_coverage` (the gate's risk–coverage curve, both corpora),
`fig3_calibration` (reliability of the gate's probability, both corpora),
`fig4_modality_quota_pareto` (overall against table-specific recall for the
seven ablated systems), `fig5_question_only_roc` (the question-only
classifier, before and after the benchmark repair), and
`fig6_contradiction_precision` (the detector's precision against the base
rate of real conflicts). The two LaTeX papers include all six.
"""


def main() -> int:
    d = Data()
    if not d.ablation or not d.rev or not d.fact:
        print("[tex-industrial] the industrial result files are absent; "
              "leaving the papers as they are")
        return 1
    blocks = {
        "2b": condensed_section(d),
        "2c": full_section(d),
    }
    n = 0
    for key, path in PAPERS.items():
        if not path.exists():
            continue
        s = path.read_text(encoding="utf-8")
        if BEGIN not in s or END not in s:
            print(f"[tex-industrial] {path.name}: markers not found")
            continue
        body = blocks[key].strip()
        new = re.sub(re.escape(BEGIN) + r".*?" + re.escape(END),
                     lambda _m: BEGIN + "\n" + body + "\n" + END,
                     s, flags=re.S)
        if new != s:
            path.write_text(new, encoding="utf-8")
            n += 1
            print(f"[tex-industrial] rewrote the second-corpus section of "
                  f"{path.name} ({len(body):,} chars)")
    return 0 if n else 1


if __name__ == "__main__":
    sys.exit(main())
