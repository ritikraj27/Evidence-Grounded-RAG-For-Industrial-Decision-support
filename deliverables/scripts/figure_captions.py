"""The six measured figures, and the caption each carries.

One source for the captions, because the figures appear in seven
deliverables and a caption that differs between them is a caption that
drifts. The markdown deliverables reference them through the
`FIG<n>_CAPTION` tokens that `substitute_tokens.py` fills from here; the
generators that write markdown call `figure_line` directly.

The figures themselves are written as PDF, so that the pandoc path embeds
them as vectors. The Word path cannot embed a PDF, so the DOCX converter
uses the PNG sibling of the same figure.
"""
from __future__ import annotations

import re

#: key -> caption, in the order the figures appear in the argument.
FIGURES = {
    "fig1_pool_size": (
        "Figure 1. Recall against the size of the rerank candidate pool, on "
        "the focus corpus (black circles, {{N_FOCUS_ANSWERABLE}} answerable "
        "of {{N_FOCUS_QUERIES}} queries) and the industrial corpus (grey "
        "squares, {{IND_N_ANSWERABLE}} of {{IND_N_QUERIES}}). "
        "The focus curve saturates at a "
        "pool of 10, where Recall@10 = Recall@20 = 1.000, and then falls "
        "slightly as the reranker is given more candidates to reorder. The "
        "industrial curve does not saturate at 10: there Recall@20 reaches "
        "1.000 at a pool of 50 while Recall@10 stays at 0.988, so 1.21 points "
        "of gold are retrieved and then pushed out of the ten-chunk context."),
    "fig2_risk_coverage": (
        "Figure 2. Risk-coverage of the confidence gate: the risk that an "
        "answered query has no answer in its context, against the fraction of "
        "queries the gate answers, on the held-out evaluation half (focus "
        "n = 71, industrial n = 178). The degenerate policies bound the curve: "
        "always answering carries the base rate of the negative class as its "
        "risk at full coverage, and always refusing removes the risk at the "
        "cost of all coverage. The industrial gate trades risk for coverage; "
        "the focus gate buys almost nothing over answering everything. The "
        "fitted operating points (tau = 0.05 focus, tau = 0.40 industrial) "
        "answer {{FOCUS_GATE_COVERAGE}} and {{IND_GATE_COVERAGE}} of all "
        "queries respectively."),
    "fig3_calibration": (
        "Figure 3. Reliability of the gate's calibrated probability against "
        "observed answerability, on the held-out evaluation half (focus "
        "n = 71, industrial n = 178); the upper panel plots observed "
        "answerability against mean predicted probability per bin and the "
        "lower panel the number of queries in each bin. The industrial gate "
        "tracks the diagonal (ECE 0.075, Brier 0.159); the focus gate does not "
        "(ECE {{GATE_ECE}}, Brier {{GATE_BRIER}}): it puts most of its queries "
        "in the lowest confidence bin, where few of them have an answer in "
        "context."),
    "fig4_modality_quota_pareto": (
        "Figure 4. Overall Recall@10 against table-specific Recall@10 for "
        "the seven ablated systems, focus corpus (black circles, n = "
        "{{N_FOCUS_ANSWERABLE}} answerable: 24 text, 8 table) and industrial "
        "corpus (grey squares, n = {{IND_N_ANSWERABLE}}: 117 text, 130 "
        "table). The "
        "modality quota does not move both axes: on the industrial corpus the "
        "pre-rerank quota buys 0.8 points of table recall and gives up 0.8 "
        "points of overall recall, and the post-rerank quota lands on exactly "
        "the no-quota operating point; on the focus corpus the post-rerank "
        "quota gives up 3.1 points of overall recall while table recall "
        "stays at 1.000. The quota is a trade, not a gain, and which way it "
        "trades depends on where it is applied."),
    "fig5_question_only_roc": (
        "Figure 5. A classifier that sees only the question text, with no "
        "retrieval, no evidence and no corpus, telling an answerable question "
        "from an unanswerable one. Before the repair the two classes were "
        "separable almost perfectly on the focus corpus (ROC AUC "
        "{{UNANS_BEFORE_AUC}}, against a permutation null of {{UNANS_BEFORE_NULL}} "
        "+/- {{UNANS_BEFORE_NULL_SD}}), "
        "and one regular "
        "expression for a fabricated identifier caught {{UNANS_SHORTCUT_BEFORE}} "
        "of the unanswerable questions with no false positive at all. After "
        "the repair the shortcut catches nothing, and what is left of the "
        "procedure's power is small but not zero: AUC {{UNANS_SEP_AUC}} on the "
        "focus corpus (p = {{UNANS_SEP_P}}) and AUC {{IND_AUD_SEP_AUC}} on the "
        "industrial corpus (p = {{IND_AUD_SEP_P}}). On the better-powered "
        "six-category corpus it is indistinguishable from chance: AUC "
        "{{UNANS_MC_SEP_AUC}} (p = {{UNANS_MC_SEP_P}}). The benchmark's "
        "unanswerable class is decidable from the evidence rather than from a "
        "question-shape rule, but on two of the three corpora it is not free "
        "of form-only separability."),
    "fig6_contradiction_precision": (
        "Figure 6. The contradiction detector's precision against the base "
        "rate of real conflicts in the same population, with 95% Wilson "
        "intervals; a filled marker means the point estimate clears the "
        "framework's 0.5 calibration floor and the branch would act, a hollow "
        "one means it does not and the findings would be withheld. The focus "
        "corpus's semantic branch has a precision of 0.0 (0 of 20 alarms "
        "confirmed by either annotator) on a base rate of 0.0, so it is "
        "withheld; the industrial semantic branch reaches 0.65 (26 of 40) "
        "against a base rate of 0.35 and would act."),
}

#: key -> the token name that carries the caption.
TOKEN_NAMES = {
    "fig1_pool_size": "FIG1_CAPTION",
    "fig2_risk_coverage": "FIG2_CAPTION",
    "fig3_calibration": "FIG3_CAPTION",
    "fig4_modality_quota_pareto": "FIG4_CAPTION",
    "fig5_question_only_roc": "FIG5_CAPTION",
    "fig6_contradiction_precision": "FIG6_CAPTION",
}


_RESOLVED: dict[str, str] = {}


def resolve(text: str, mapping: dict) -> str:
    """Replace the {{TOKEN}} placeholders in a caption with their values."""
    return re.sub(
        r"\{\{([A-Z0-9_]+)\}\}",
        lambda m: mapping.get(m.group(1), m.group(0)),
        text)


def caption(key: str) -> str:
    """The caption for one figure, with its counts resolved from the tokens.

    The counts in the captions are the same counts the tables beside them
    report, so they are read from the token values rather than written by
    hand; a caption whose number has drifted from its table is worse than
    no caption.
    """
    if key not in _RESOLVED:
        from substitute_tokens import values
        _RESOLVED[key] = resolve(FIGURES[key], values())
    return _RESOLVED[key]


def figure_line(key: str) -> str:
    """The markdown image line for one figure, with its caption."""
    return f"![{caption(key)}](figures/{key}.pdf)\n"


def caption_token(key: str) -> str:
    """The markdown image line for one figure, with a token for the caption."""
    return f"![{{{TOKEN_NAMES[key]}}}](figures/{key}.pdf)\n"
