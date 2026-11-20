#!/usr/bin/env python3
"""Build the thesis figures from the experiment result JSONs.

Every figure is read from a result file under ``impl/results_focus`` or
``impl/results_industrial``; nothing here invents a number. Where a result
file carries an interval (a Wilson interval on a precision, a bootstrap
interval on a recall) it is plotted as an interval, and where it carries
none, none is drawn.

The script writes a vector PDF (for LaTeX) and a 200 dpi PNG (for review)
into ``deliverables/figures`` and prints the caption of each figure so the
text can be lifted into the papers verbatim.

Usage::

    cd /Users/ritikraj/Documents/MTP && .venv/bin/python impl/scripts/make_figures.py
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

# --------------------------------------------------------------------------
# paths
# --------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[2]
RESULTS_FOCUS = ROOT / "impl" / "results_focus"
RESULTS_INDUSTRIAL = ROOT / "impl" / "results_industrial"
BENCH_FOCUS = ROOT / "impl" / "data" / "benchmark_focus"
BENCH_INDUSTRIAL = ROOT / "impl" / "data" / "benchmark_industrial"
OUTDIR = ROOT / "deliverables" / "figures"

# --------------------------------------------------------------------------
# captions -- the text that goes under each figure in the papers
# --------------------------------------------------------------------------
CAPTIONS = {
    "fig1_pool_size": (
        "Recall against the size of the rerank candidate pool, on the focus "
        "corpus (black circles, 32 answerable of 176 queries) and the "
        "industrial corpus (grey squares, 247 of 444). The focus curve "
        "saturates at a pool of 10, where "
        "Recall@10 = Recall@20 = 1.000, and then falls slightly as the "
        "reranker is given more candidates to reorder. The industrial curve "
        "does not saturate at 10: there Recall@20 reaches 1.000 at a pool of "
        "50 while Recall@10 stays at 0.988, so 1.21 points of gold are "
        "retrieved and then pushed out of the ten-chunk context by the "
        "reranker's own ordering. Enlarging the pool buys recall the context "
        "cannot hold."
    ),
    "fig2_risk_coverage": (
        "Risk-coverage of the confidence gate: the risk that an answered query "
        "has no answer in its context, against the fraction of queries the "
        "gate answers, measured on the held-out evaluation half (focus n = "
        "71, industrial n = 178). The degenerate policies bound the curve: "
        "always answering carries the base rate of the negative class as its "
        "risk (0.818 on the focus corpus, 0.444 on the industrial corpus, over "
        "all queries) at full coverage, and always refusing removes the risk "
        "at the cost of all coverage. The industrial gate trades risk for "
        "coverage: its risk falls from 0.46 at full coverage to 0.29 at two "
        "thirds coverage. The focus gate buys almost nothing over answering "
        "everything, 0.82 down to 0.73 over the same range. The fitted "
        "operating points (tau = 0.05 focus, tau = 0.40 industrial) answer "
        "0.693 and 0.691 of all queries respectively."
    ),
    "fig3_calibration": (
        "Reliability of the gate's calibrated probability against observed "
        "answerability, on the held-out evaluation half (focus n = 71, "
        "industrial n = 178); the upper panel plots observed answerability "
        "against mean predicted probability per bin and the lower panel the "
        "number of queries in each bin. The industrial gate tracks the "
        "diagonal (ECE 0.075, Brier 0.159); the focus gate does not (ECE "
        "0.104, Brier 0.151): it puts most of its queries in the lowest "
        "confidence bin, where few of them have an answer in context."
    ),
    "fig4_modality_quota_pareto": (
        "Overall Recall@10 against table-specific Recall@10 for the seven "
        "ablated systems, focus corpus (black circles, n = 32 answerable: 24 "
        "text, 8 table) and industrial corpus (grey squares, n = 247: 117 "
        "text, 130 table). The "
        "modality quota does not move both axes: on the industrial corpus the "
        "pre-rerank quota (F) buys 0.8 points of table recall and gives up 0.8 "
        "points of overall recall, and the post-rerank quota (G) lands on "
        "exactly the no-quota operating point; on the focus corpus the "
        "post-rerank quota gives up 3.1 points of overall recall while table "
        "recall stays at 1.000. The quota is a trade, not a gain, and which "
        "way it trades depends on where it is applied. The bar on the "
        "industrial D point is the 95% bootstrap interval for its Recall@10, "
        "the only bootstrap interval these result files carry."
    ),
    "fig5_question_only_roc": (
        "A classifier that sees only the question text, with no retrieval, no "
        "evidence and no corpus, telling an answerable question from an "
        "unanswerable one. Before the repair the two classes were separable "
        "almost perfectly on the focus corpus (ROC AUC 0.999, against a "
        "permutation null of 0.455 +/- 0.072 with a maximum of 0.628), and one "
        "regular expression for a fabricated identifier caught 76% of the "
        "unanswerable questions with no false positive at all. After the "
        "repair the same procedure is close to chance on both corpora (focus "
        "AUC 0.608, industrial AUC 0.708), and the shortcut catches nothing. "
        "The benchmark's unanswerable class is now decidable only from the "
        "evidence."
    ),
    "fig6_contradiction_precision": (
        "The contradiction detector's precision against the base rate of real "
        "conflicts in the same population, with 95% Wilson intervals; a filled "
        "marker means the point estimate clears the framework's 0.5 "
        "calibration floor and the branch would act, a hollow one means it "
        "does not and the findings would be withheld. The focus corpus's "
        "semantic branch has a precision of 0.0 (0 of 20 alarms confirmed by "
        "either annotator, 95% upper bound 0.161) on a base rate of 0.0, so it "
        "is withheld; the industrial semantic branch reaches 0.65 (26 of 40) "
        "against a base rate of 0.35 and would act. The industrial quantity "
        "stratum is not measurable from these data: a corpus-wide search "
        "found 1,776 candidate quantity conflicts over 64 measurement terms "
        "and the branch fired on 13 of 119 scored pairs, but its precision was "
        "never measured."
    ),
}

# --------------------------------------------------------------------------
# one shade per corpus, used the same way in all six figures
#
# The deliverables are printed, photocopied and projected, and none of those
# is guaranteed to reproduce a hue. The figures carry no colour at all: the
# two corpora are separated by lightness (black against mid grey) and, where
# the drawing allows it, by marker shape, so that the two series stay apart
# on a black-and-white copier. The captions name the shade rather than a
# colour for the same reason.
# --------------------------------------------------------------------------
C_FOCUS = "#000000"        # black
C_INDUSTRIAL = "#8C8C8C"    # mid grey
C_NEUTRAL = "#B3B3B3"      # light grey, for baselines and reference lines
C_INK = "#333333"

DPI = 200

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Times", "Nimbus Roman", "DejaVu Serif"],
    "font.size": 8,
    "axes.labelsize": 8,
    "axes.titlesize": 8,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    "legend.fontsize": 7,
    "axes.linewidth": 0.6,
    "lines.linewidth": 1.1,
    "lines.markersize": 3.6,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "xtick.major.size": 2.5,
    "ytick.major.size": 2.5,
    "xtick.direction": "in",
    "ytick.direction": "in",
    "xtick.top": True,
    "ytick.right": True,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "savefig.dpi": DPI,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.02,
})


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def load(path: Path) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def wilson(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    """Wilson score interval for a binomial proportion."""
    if n <= 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1.0 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = (z / d) * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (max(0.0, centre - half), min(1.0, centre + half))


COLUMN_WIDTH_IN = 3.5   # one IEEE column


def finish(fig, name: str) -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    pdf = OUTDIR / f"{name}.pdf"
    fig.savefig(pdf)
    fig.savefig(OUTDIR / f"{name}.png", dpi=DPI)
    plt.close(fig)
    width = _pdf_width_in(pdf)
    flag = "" if width is None or width <= COLUMN_WIDTH_IN + 0.02 else \
        f"  <-- WIDER THAN ONE COLUMN ({width:.2f} in)"
    print(f"  wrote {pdf} ({width:.2f} in wide) and "
          f"{OUTDIR / (name + '.png')}{flag}")
    if width is not None and width > COLUMN_WIDTH_IN + 0.02:
        # A figure wider than one column does not fit the IEEE template, and
        # the overflow is invisible in the PNG until the PDF is placed. The
        # check has to fail the build rather than print a warning that
        # scrolls past: a check that reports and continues is a check that
        # does not check.
        raise SystemExit(
            f"[figures] {name}.pdf is {width:.2f} in wide; one IEEE column is "
            f"{COLUMN_WIDTH_IN} in. Shorten the labels or the legend.")


def check_all_widths() -> None:
    """Every figure must fit one column."""
    for pdf in sorted(OUTDIR.glob("*.pdf")):
        width = _pdf_width_in(pdf)
        if width is not None and width > COLUMN_WIDTH_IN + 0.02:
            raise SystemExit(
                f"[figures] {pdf.name} is {width:.2f} in wide; one IEEE column "
                f"is {COLUMN_WIDTH_IN} in.")


def _pdf_width_in(path: Path) -> float | None:
    """The page width of a PDF in inches, read from its MediaBox."""
    import re
    m = re.search(rb"/MediaBox\s*\[\s*0\s+0\s+([\d.]+)\s+[\d.]+\s*\]",
                  path.read_bytes())
    return float(m.group(1)) / 72.0 if m else None


def note(ax, text: str, xy=(0.0, 0.0), **kw) -> None:
    """Small annotation inside the axes, placed in axes coordinates."""
    defaults = dict(fontsize=7.0, color=C_INK, va="bottom", ha="left")
    defaults.update(kw)
    ax.text(xy[0], xy[1], text, transform=ax.transAxes, **defaults)


# --------------------------------------------------------------------------
# figure 1 -- recall against candidate-pool size
# --------------------------------------------------------------------------
def fig_pool_size() -> None:
    focus = load(RESULTS_FOCUS / "exp5_pool_size.json")
    ind = load(RESULTS_INDUSTRIAL / "exp5_pool_size.json")

    def curves(d):
        rows = sorted(d["results"], key=lambda r: r["pool_size"])
        return ([r["pool_size"] for r in rows],
                [r["recall@10"] for r in rows],
                [r["recall@20"] for r in rows])

    fp, f10, f20 = curves(focus)
    ip, i10, i20 = curves(ind)

    fig, (ax, ax2) = plt.subplots(
        2, 1, figsize=(3.5, 3.6), sharex=True,
        gridspec_kw=dict(height_ratios=[1.3, 1.0], hspace=0.42))

    # ---- (a) recall against pool size -----------------------------------
    ax.plot(fp, f10, "-o", color=C_FOCUS, label="focus, R@10")
    ax.plot(fp, f20, "--o", color=C_FOCUS, mfc="white",
            label="focus, R@20")
    ax.plot(ip, i10, "-s", color=C_INDUSTRIAL, label="industrial, R@10")
    ax.plot(ip, i20, "--s", color=C_INDUSTRIAL, mfc="white",
            label="industrial, R@20")

    ax.set_xscale("log")
    ax.set_xlim(4.4, 118)
    ax.set_ylim(0.936, 1.022)
    ax.set_xticks([5, 10, 20, 50, 100])
    ax.set_xticklabels(["5", "10", "20", "50", "100"])
    ax.set_ylabel("Recall")
    ax.set_title("(a) recall against pool size", pad=3)

    ax.axvline(10, color=C_FOCUS, lw=0.6, ls=":", zorder=1)
    ax.text(10.6, 1.012, "focus saturates at pool 10", fontsize=7.0,
            color=C_FOCUS, ha="left", va="center")
    # the gap the industrial corpus opens up at a pool of fifty
    ax.annotate("", xy=(50, i20[3]), xytext=(50, i10[3]),
                arrowprops=dict(arrowstyle="<->", lw=0.8, color=C_INDUSTRIAL))
    ax.text(50, 1.003, "1.21 pts", fontsize=7.0, color=C_INDUSTRIAL,
            ha="center", va="bottom")
    note(ax, "recall over the answerable questions:\n"
             "focus n = 32 of 176, industrial n = 247 of 444",
         xy=(0.03, 0.03), va="bottom")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.42), ncol=2,
              frameon=False, handlelength=1.8, columnspacing=1.0,
              borderpad=0.0, labelspacing=0.25)

    # ---- (b) displacement ------------------------------------------------
    fd = [(a - b) * 100 for a, b in zip(f20, f10)]
    id_ = [(a - b) * 100 for a, b in zip(i20, i10)]
    ax2.axhline(0.0, color=C_NEUTRAL, lw=0.6)
    ax2.plot(fp, fd, "-o", color=C_FOCUS)
    ax2.plot(ip, id_, "-s", color=C_INDUSTRIAL)
    ax2.set_xscale("log")
    ax2.set_xlim(4.4, 118)
    ax2.set_ylim(-0.55, 3.95)
    ax2.set_xticks([5, 10, 20, 50, 100])
    ax2.set_xticklabels(["5", "10", "20", "50", "100"])
    ax2.set_xlabel("rerank candidate pool size")
    ax2.set_ylabel("R@20 - R@10 (pts)")
    ax2.set_title("(b) golds found, then displaced from the context", pad=3)
    ax2.text(21.5, 3.30, "focus", fontsize=7.0, color=C_FOCUS,
             ha="left", va="bottom")
    ax2.text(52, 1.42, "industrial", fontsize=7.0, color=C_INDUSTRIAL,
             ha="left", va="bottom")

    finish(fig, "fig1_pool_size")


# --------------------------------------------------------------------------
# figure 2 -- risk-coverage of the confidence gate
# --------------------------------------------------------------------------
def fig_risk_coverage() -> None:
    focus = load(RESULTS_FOCUS / "exp2_gate.json")
    ind = load(RESULTS_INDUSTRIAL / "exp2_gate.json")

    fig, ax = plt.subplots(figsize=(3.5, 2.7))

    for d, colour, marker, name in ((focus, C_FOCUS, "o", "focus"),
                                    (ind, C_INDUSTRIAL, "s", "industrial")):
        rc = sorted(d["risk_coverage"], key=lambda r: r["coverage"])
        ax.plot([r["coverage"] for r in rc], [r["risk"] for r in rc],
                "-", marker=marker, color=colour, ms=2.4, label=name)

    # the two degenerate policies
    for d in (focus, ind):
        base = d["base_rate_answer_in_context"]
        ax.plot([1.0], [1.0 - base], "s", color=C_NEUTRAL, ms=4.2, zorder=6,
                label="always answer" if d is focus else None)
        ax.plot([0.0], [0.0], "^", color=C_NEUTRAL, ms=4.2, zorder=6,
                label="always refuse" if d is focus else None)

    ax.set_xlim(-0.04, 1.05)
    ax.set_ylim(-0.05, 0.95)
    ax.set_xlabel("coverage (fraction of queries answered)")
    ax.set_ylabel("risk (no answer in context)")
    note(ax, "held-out evaluation half:\n"
             "focus n = 71, industrial n = 178\n"
             "fitted tau: 0.05 focus, 0.40 industrial",
         xy=(0.03, 0.97), va="top")

    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=2,
              frameon=False, handlelength=1.6, columnspacing=1.4,
              borderpad=0.0, labelspacing=0.25)
    finish(fig, "fig2_risk_coverage")


# --------------------------------------------------------------------------
# figure 3 -- reliability diagram of the calibrated gate
# --------------------------------------------------------------------------
def fig_calibration() -> None:
    focus = load(RESULTS_FOCUS / "exp2_gate.json")
    ind = load(RESULTS_INDUSTRIAL / "exp2_gate.json")

    fig, (ax, axh) = plt.subplots(
        2, 1, figsize=(3.5, 3.3), sharex=True,
        gridspec_kw=dict(height_ratios=[2.1, 0.9], hspace=0.45))

    ax.plot([0, 1], [0, 1], "--", color=C_NEUTRAL, lw=0.7, zorder=1,
            label="perfect calibration")

    for d, colour, marker, name in ((focus, C_FOCUS, "o", "focus"),
                                    (ind, C_INDUSTRIAL, "s", "industrial")):
        rows = [r for r in d["reliability_table"] if r["count"] > 0]
        m = d["calibration_metrics"]
        ax.plot([r["confidence"] for r in rows], [r["accuracy"] for r in rows],
                "-", marker=marker, color=colour, ms=3.4,
                label=f"{name}: ECE {m['ece']:.3f}, Brier {m['brier']:.3f}",
                zorder=4)

    ax.set_xlim(-0.03, 1.03)
    ax.set_ylim(-0.06, 1.13)
    ax.set_ylabel("observed answerability")
    ax.set_title("(a) reliability", pad=3)
    ax.legend(loc="upper left", bbox_to_anchor=(0.02, 1.0), frameon=False,
              handlelength=1.6, borderpad=0.0, labelspacing=0.2)

    # ---- counts per bin --------------------------------------------------
    bins = [(r["bin_lo"], r["bin_hi"]) for r in focus["reliability_table"]]
    centres = [(lo + hi) / 2 for lo, hi in bins]
    width = (bins[0][1] - bins[0][0]) * 0.38
    fc = [r["count"] for r in focus["reliability_table"]]
    ic = [r["count"] for r in ind["reliability_table"]]
    axh.bar([c - width / 2 for c in centres], fc, width=width, color=C_FOCUS,
            label="focus")
    axh.bar([c + width / 2 for c in centres], ic, width=width,
            color=C_INDUSTRIAL, label="industrial")
    axh.set_xlabel("calibrated probability (bin)")
    axh.set_ylabel("queries")
    axh.set_title("(b) queries per bin", pad=3)
    axh.set_xticks([0.05, 0.25, 0.45, 0.65, 0.85])
    axh.set_ylim(0, 58)
    note(axh, "held-out evaluation half: focus n = 71, industrial n = 178",
         xy=(0.02, 0.99), va="top")

    finish(fig, "fig3_calibration")


# --------------------------------------------------------------------------
# figure 4 -- modality-quota Pareto frontier
# --------------------------------------------------------------------------
SYSTEM_LABELS = {
    "A. bm25_only": "A",
    "B. dense_only": "B",
    "C. hybrid_rrf": "C",
    "D. hybrid_rrf_rerank": "D",
    "E. +category_filter": "E",
    "F. +quota_pre_rerank": "F",
    "G. +quota_post_rerank": "G",
}
QUOTA_SYSTEMS = {"F", "G"}

# where each point's letter goes, so that nothing overlaps
LABEL_OFFSETS = {
    ("focus", "B"): ((4, 1), "left", "bottom"),
    ("focus", "A, D, E"): ((-5, -2), "right", "top"),
    ("focus", "C, F"): ((0, 4), "center", "bottom"),
    ("focus", "G"): ((0, 4), "center", "bottom"),
    ("industrial", "B"): ((4, 1), "left", "bottom"),
    ("industrial", "C"): ((-4, -2), "right", "top"),
    ("industrial", "A"): ((-4, -2), "right", "top"),
    ("industrial", "D, E, G"): ((5, -1), "left", "top"),
    ("industrial", "F"): ((0, 4), "center", "bottom"),
}


def _pareto(points):
    """The non-dominated set of (x, y) points, both maximised."""
    return [(x, y) for x, y in points
            if not any(x2 >= x and y2 >= y and (x2 > x or y2 > y)
                       for x2, y2 in points)]


def fig_modality_pareto() -> None:
    focus = load(RESULTS_FOCUS / "exp1_ablation.json")
    ind = load(RESULTS_INDUSTRIAL / "exp1_ablation.json")

    def points(d):
        return [(SYSTEM_LABELS.get(name, name[:1]),
                 s["recall@10"], s["modality_recall"]["table"])
                for name, s in d["systems"].items()]

    fig, ax = plt.subplots(figsize=(3.5, 3.0))

    for d, colour, marker, name in ((focus, C_FOCUS, "o", "focus"),
                                    (ind, C_INDUSTRIAL, "s", "industrial")):
        pts = points(d)
        front = sorted(_pareto([(x, y) for _, x, y in pts]))
        if len(front) > 1:
            ax.plot([p[0] for p in front], [p[1] for p in front], "--",
                    color=colour, lw=0.9, alpha=0.7, zorder=1)
        groups: dict[tuple[float, float], list[str]] = {}
        for letter, x, y in pts:
            groups.setdefault((round(x, 10), round(y, 10)), []).append(letter)
        for (x, y), letters in groups.items():
            tag = ", ".join(letters)
            ax.plot([x], [y], marker, color=colour, ms=4.0, zorder=4,
                    markeredgecolor="white", markeredgewidth=0.4)
            if set(letters) & QUOTA_SYSTEMS:
                ax.plot([x], [y], marker, color=colour, ms=7.8, mfc="none",
                        mew=0.8, zorder=3)
            offset, ha, va = LABEL_OFFSETS.get((name, tag),
                                               ((4, 2), "left", "bottom"))
            ax.annotate(tag, (x, y), textcoords="offset points",
                        xytext=offset, fontsize=7.0, color=colour,
                        ha=ha, va=va)

    # the trade the quota makes on the focus corpus: E -> G
    fe = focus["systems"]["E. +category_filter"]
    fg = focus["systems"]["G. +quota_post_rerank"]
    ax.annotate("", xy=(fg["recall@10"], fg["modality_recall"]["table"]),
                xytext=(fe["recall@10"], fe["modality_recall"]["table"]),
                arrowprops=dict(arrowstyle="->", lw=0.9, color=C_FOCUS))

    # the trade the quota makes on the industrial corpus: E -> F
    ie = ind["systems"]["E. +category_filter"]
    if_ = ind["systems"]["F. +quota_pre_rerank"]
    ax.annotate("", xy=(if_["recall@10"], if_["modality_recall"]["table"]),
                xytext=(ie["recall@10"], ie["modality_recall"]["table"]),
                arrowprops=dict(arrowstyle="->", lw=0.9, color=C_INDUSTRIAL))
    ax.text(0.798, 0.945, "arrows: the modality quota's effect",
            fontsize=7.0, color=C_NEUTRAL, ha="left", va="top")

    # the one bootstrap interval the result files carry
    bs = ind["bootstrap_recall10"]
    ax.errorbar([bs["point"]], [ind["systems"]["D. hybrid_rrf_rerank"]
                                ["modality_recall"]["table"]],
                xerr=[[bs["point"] - bs["lo"]], [bs["hi"] - bs["point"]]],
                fmt="none", ecolor=C_INDUSTRIAL, elinewidth=0.9, capsize=0,
                zorder=2)

    ax.set_xlim(0.795, 1.045)
    ax.set_ylim(0.795, 1.035)
    ax.set_xlabel("overall Recall@10")
    ax.set_ylabel("table Recall@10")
    note(ax, "focus n = 32 answerable (24 text, 8 table)\n"
             "industrial n = 247 (117 text, 130 table)",
         xy=(0.02, 0.02), va="bottom")
    note(ax, "ringed: F and G\ndashed: Pareto frontier",
         xy=(0.98, 0.13), va="bottom", ha="right", color=C_NEUTRAL)

    finish(fig, "fig4_modality_quota_pareto")


# --------------------------------------------------------------------------
# figure 5 -- the question-only ROC
# --------------------------------------------------------------------------
def _structural_roc(answerable: list[str], unanswerable: list[str]):
    """Re-derive the question-only ROC exactly as the audit computes it.

    ``impl/experiments/audit_unanswerable_class.py`` fits a logistic
    regression on structural features of the question with a fixed
    cross-validation split, so the out-of-fold scores -- and hence the
    curve -- are reproducible. The caller checks the resulting AUC against
    the value recorded in the result file.
    """
    from sklearn.model_selection import StratifiedKFold, cross_val_predict

    sys.path.insert(0, str(ROOT / "impl"))
    sys.path.insert(0, str(ROOT / "impl" / "experiments"))
    sys.path.insert(0, str(ROOT / "impl" / "scripts"))
    from audit_unanswerable_class import _structural_matrix, SEED

    pairs = sorted([(q, 1) for q in answerable] + [(q, 0) for q in unanswerable])
    queries = [p[0] for p in pairs]
    y = np.array([p[1] for p in pairs])
    pipe, X = _structural_matrix(queries)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    prob = cross_val_predict(pipe, X, y, cv=cv, method="predict_proba")[:, 1]
    return y, prob


def _roc_points(y, prob):
    """(fpr, tpr) at every distinct score threshold, plus the endpoints."""
    order = np.argsort(-prob)
    ys = y[order]
    n_pos = int(ys.sum())
    n_neg = int(len(ys) - n_pos)
    tpr = [0.0]
    fpr = [0.0]
    tp = fp = 0
    for i in range(len(ys)):
        if ys[i] == 1:
            tp += 1
        else:
            fp += 1
        tpr.append(tp / n_pos)
        fpr.append(fp / n_neg)
    return np.array(fpr), np.array(tpr)


def _benchmark_questions(path: Path):
    d = load(path)
    ans = [q["query"] for q in d["queries"] if q["category"] != "unanswerable"]
    un = [q["query"] for q in d["queries"] if q["category"] == "unanswerable"]
    return ans, un


def fig_question_only_roc() -> None:
    from sklearn.metrics import roc_auc_score

    fa = load(RESULTS_FOCUS / "exp12_unanswerable_class_audit.json")
    ia = load(RESULTS_INDUSTRIAL / "exp12_unanswerable_class_audit.json")

    panels = [
        ("focus, before repair",
         BENCH_FOCUS / "benchmark_pre_unanswerable_repair.json",
         fa["before_repair"]["structural"]["whole_class"],
         C_FOCUS, "-"),
        ("focus, after repair",
         BENCH_FOCUS / "benchmark.json",
         fa["after_repair"]["structural_separability"]["repaired_whole_class"],
         C_FOCUS, "--"),
        ("industrial, after repair",
         BENCH_INDUSTRIAL / "benchmark.json",
         ia["after_repair"]["structural_separability"]["repaired_whole_class"],
         C_INDUSTRIAL, "-"),
    ]

    fig, ax = plt.subplots(figsize=(3.5, 3.2))
    ax.plot([0, 1], [0, 1], "--", color=C_NEUTRAL, lw=0.7, zorder=1,
            label="chance")

    for label, bench, rec, colour, ls in panels:
        ans, un = _benchmark_questions(bench)
        y, prob = _structural_roc(ans, un)
        auc = float(roc_auc_score(y, prob))
        if abs(auc - rec["roc_auc"]) > 1e-9:
            raise SystemExit(
                f"figure 5: the re-derived AUC for '{label}' is {auc!r} but "
                f"the result file records {rec['roc_auc']!r}; the curve would "
                f"not be the recorded result")
        fpr, tpr = _roc_points(y, prob)
        ax.plot(fpr, tpr, ls, color=colour, lw=1.3, zorder=3,
                label=f"{label} (AUC {auc:.3f})")

    # the one shortcut the audit measured directly: a fabricated identifier
    for audit, colour in ((fa["before_repair"], C_FOCUS),
                          (fa["after_repair"], C_FOCUS)):
        sd = audit["shortcut_diagnostic"]
        tpr = sd["unanswerable_caught"] / sd["n_unanswerable"]
        fpr = sd["answerable_false_positives"] / sd["n_answerable"]
        ax.plot([fpr], [tpr], "*", color=colour, ms=9.0, zorder=6,
                markeredgecolor="white", markeredgewidth=0.4)

    ax.set_xlim(-0.035, 1.03)
    ax.set_ylim(-0.035, 1.03)
    ax.set_xlabel("false positive rate")
    ax.set_ylabel("true positive rate")
    ax.text(0.035, 0.775,
            "PREFIX-digits rule:\n"
            "76.4%, 0 false positives",
            fontsize=7.0, color=C_INK, ha="left", va="top")
    note(ax, "focus n = 32 answerable / 144 unanswerable\n"
             "industrial n = 247 / 197\n"
             "permutation null (focus, before repair):\n"
             "AUC 0.455 +/- 0.072, max 0.628",
         xy=(0.97, 0.13), va="bottom", ha="right")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.20), ncol=2,
              frameon=False, handlelength=1.8, borderpad=0.0,
              labelspacing=0.25, columnspacing=1.2)

    finish(fig, "fig5_question_only_roc")


# --------------------------------------------------------------------------
# figure 6 -- contradiction precision against the base rate
# --------------------------------------------------------------------------
def fig_contradiction_precision() -> None:
    foc = load(RESULTS_FOCUS / "exp11_contradiction_precision.json")
    rev = load(RESULTS_INDUSTRIAL / "exp14_revision_eval.json")
    qty = load(RESULTS_INDUSTRIAL / "exp20_quantity_stratum.json")
    cons = rev["profiles"]["shipped"]["consensus"]

    rows = []

    # -- focus: the semantic branch of the contradiction gate -------------
    a = foc["annotators"]["judge_a_model"]
    n_labelled = a["n_alarms_labelled"] + a["n_unflagged_sampled"]
    n_true = a["n_alarms_true"] + a["n_missed_true_in_sample"]
    population = a["n_alarms_labelled"] + a["unflagged_population"]
    rows.append({
        "label": "focus, semantic",
        "sub": f"n = {a['n_alarms_labelled']} alarms ({population:,} pairs)",
        "precision": a["precision"],
        "ci": a["precision_ci95"],
        "base_rate": n_true / population,
        "base_ci": wilson(n_true, n_labelled),
        "colour": C_FOCUS,
    })

    # -- industrial: the shipped semantic branch, and its strata ----------
    def industrial_row(name, block, n_pairs, n_conflicts, n_flagged):
        ci = block.get("precision_ci95") or block["precision_any_flag_ci95"]
        return {
            "label": name,
            "sub": f"n = {n_flagged} alarms ({n_pairs} pairs)",
            "precision": block["precision_any_flag"],
            "ci": ci,
            "base_rate": n_conflicts / n_pairs,
            "base_ci": wilson(n_conflicts, n_pairs),
            "colour": C_INDUSTRIAL,
        }

    o = cons["overall"]
    rows.append(industrial_row("industrial, all", o, o["n_pairs_total"],
                                o["n_annotated_conflicts"], o["n_flagged"]))
    rs = cons["by_stratum"]["revision"]
    rows.append(industrial_row("industrial, revision", rs,
                                rs["n_pairs"],
                                rs["label_distribution"]["supersession"],
                                rs["n_flagged"]))
    ss = cons["by_stratum"]["similar"]
    rows.append(industrial_row("industrial, similar", ss,
                                ss["n_pairs"],
                                ss["label_distribution"]["supersession"],
                                ss["n_flagged"]))
    ec = cons["by_change_class"]["editorial"]
    rows.append(industrial_row("industrial, editorial", ec, ec["n_pairs"],
                                ec["label_distribution"]["supersession"],
                                ec["n_flagged"]))
    sc = cons["by_change_class"]["substantive"]
    rows.append(industrial_row("industrial, substantive", sc, sc["n_pairs"],
                                sc["label_distribution"]["supersession"],
                                sc["n_flagged"]))

    fig, ax = plt.subplots(figsize=(3.5, 3.4))
    # The y-tick labels are two lines of text; with the default margins they
    # run off the left of the figure, and a tight bounding box then saves a
    # page wider than the column it has to sit in. Reserve the space instead.
    fig.subplots_adjust(left=0.44, right=0.97, top=0.97, bottom=0.30)

    ys = np.arange(len(rows))[::-1]
    for y, r in zip(ys, rows):
        p = r["precision"]
        lo, hi = r["ci"]
        colour = r["colour"]
        acts = p >= 0.5
        ax.vlines(r["base_rate"], y - 0.3, y + 0.3, color=C_NEUTRAL, lw=1.2,
                  zorder=2)
        ax.plot([lo, hi], [y, y], "-", color=colour, lw=1.3, zorder=3)
        ax.plot([lo, hi], [y, y], "_", color=colour, ms=4.0, zorder=3)
        ax.plot([p], [y], "o", color=colour, ms=4.8,
                mfc=colour if acts else "white",
                markeredgecolor=colour, markeredgewidth=1.0, zorder=4)

    ax.axvline(0.5, color=C_NEUTRAL, lw=0.8, ls=":", zorder=2)
    ax.text(0.515, 5.34, "calibration floor (0.5)", fontsize=7.0,
            color=C_NEUTRAL, ha="left", va="bottom")
    ax.set_yticks(ys)
    ax.set_yticklabels([f"{r['label']}\n{r['sub']}" for r in rows], fontsize=7)
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-1.45, 5.75)
    ax.set_xlabel("precision of the detector's alarms")
    ax.plot([], [], "o", color=C_NEUTRAL, ms=4.8, mfc="white",
            markeredgecolor=C_NEUTRAL, label="precision (95% CI)")
    ax.plot([], [], "|", color=C_NEUTRAL, ms=7.0, mew=1.2,
            label="base rate of real conflicts")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.155), ncol=1,
              frameon=False, handlelength=1.3, borderpad=0.0,
              labelspacing=0.2)
    note(ax, "filled: clears the 0.5 floor and acts;\n"
             "hollow: withheld. The industrial quantity\n"
             f"stratum: no measured precision "
             f"({qty['n_pairs_the_quantity_branch_fired_on']} of "
             f"{qty['n_pairs_scored']} fired)",
         xy=(0.02, 0.006), va="bottom")

    finish(fig, "fig6_contradiction_precision")


# --------------------------------------------------------------------------
def main() -> int:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    print("[figures] building the six figures")
    fig_pool_size()
    fig_risk_coverage()
    fig_calibration()
    fig_modality_pareto()
    fig_question_only_roc()
    fig_contradiction_precision()
    check_all_widths()

    print("\n" + "=" * 78)
    print("CAPTIONS")
    print("=" * 78)
    for name, text in CAPTIONS.items():
        print(f"\n{name}:")
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
