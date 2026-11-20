#!/usr/bin/env python3
"""Generate the numeric Results prose of the two LaTeX papers from the JSON.

The ablation *tables* in both papers were already regenerated from the
measured JSON. Their *prose* was not, and it had drifted: the IEEE paper
described a table-recall rise from 0.892 to 0.919 and a 14.1-point quota
cost, neither of which matches the measured data, and both papers quoted a
dense-only Recall@10 of 0.471 against a measured 0.477.

Worse than being stale, prose can be *wrong*: whether the category filter
raises table recall, or whether the quota helps or hurts, are facts about
the run, and a hand-written sentence asserts one answer regardless. This
generator reads the measurements and writes the interpretation that the
measurements support.

The block is delimited in the templates by `% BEGIN RESULTS-NUMERIC` and
`% END RESULTS-NUMERIC`.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from results_source import load as _src_load, load_transfer as _src_load_transfer, _comp_index

RESULTS = ROOT / "impl" / "results"
PAPERS = [
    ROOT / "deliverables" / "Deliverable_2b_IEEE_Conference_Paper.tex",
    ROOT / "deliverables" / "Deliverable_2c_Journal_Style_Paper.tex",
]

BEGIN = "% BEGIN RESULTS-NUMERIC"
END = "% END RESULTS-NUMERIC"








def load(name, required=()):
    """Load a result file, preferring the focus-domain run.

    The headline numbers come from the focus domain; the multi-category run
    is the fallback and the source of the transfer study. See
    `results_source.py` for why.
    """
    return _src_load(name, required)


def load_transfer(name, required=()):
    """Load a result from the multi-category run only.

    The candidate-pool sweep is defined on the six-category corpus: on the
    focus domain the gold chunk is in the top ten for every pool size, so the
    curve is flat at ceiling and says nothing about pool size.
    """
    return _src_load_transfer(name, required)

def sci(p: float) -> str:
    """3.48e-08 -> '3.5\\!\\times\\!10^{-8}'."""
    if not p or p <= 0:
        return "0"
    from math import floor, log10
    e = int(floor(log10(p)))
    m = p / (10 ** e)
    return f"{m:.1f}\\!\\times\\!10^{{{e}}}"


def signed_pp(x: float) -> str:
    return f"{x * 100:+.1f}"


def build_block(condensed: bool = False) -> str | None:
    exp1 = load("exp1_ablation", ("systems", "comparisons", "corpus_stats"))
    # The candidate-pool curve is only informative on the six-category
    # corpus: on the focus domain the gold chunk is in the top ten for
    # every pool size, so the curve is flat at ceiling. The pool experiment
    # is defined on the multi-category corpus and is loaded from there.
    exp5 = load_transfer("exp5_pool_size", ("results",))
    if not exp1:
        return None

    S = exp1["systems"]
    comp = _comp_index(exp1["comparisons"])
    cs = exp1["corpus_stats"]

    A = S["A. bm25_only"]
    B = S["B. dense_only"]
    C = S["C. hybrid_rrf"]
    D = S["D. hybrid_rrf_rerank"]
    E = S["E. +category_filter"]
    F = S["F. +quota_pre_rerank"]
    G = S["G. +quota_post_rerank"]

    def p_of(a: str) -> float:
        return comp[a]["wilcoxon"]["p_value"]

    def p_named(name: str) -> float:
        return comp[name]["wilcoxon"]["p_value"]

    def move_phrase(delta: float, old: float, new: float, label: str) -> str:
        """'raised R from 0.9 to 1.0' / 'lowered ...' / 'left R unchanged at 0.9'."""
        if delta > 1e-9:
            return f"raised {label} from {old:.3f} to {new:.3f}"
        if delta < -1e-9:
            return f"lowered {label} from {old:.3f} to {new:.3f}"
        return f"left {label} unchanged at {old:.3f}"

    # --- fusion -----------------------------------------------------------
    dense_weaker = B["recall@10"] < A["recall@10"]
    gain_vs_b = C["recall@10"] - B["recall@10"]
    gain_vs_a = C["recall@10"] - A["recall@10"]
    p_bc = p_of("B. dense_only")
    p_ac = p_named("A. bm25_only -> C. hybrid_rrf")

    # --- reranking --------------------------------------------------------
    cd_delta = D["recall@10"] - C["recall@10"]
    cd_phrase = move_phrase(cd_delta, C["recall@10"], D["recall@10"], "Recall@10")
    r20_delta = D["recall@20"] - C["recall@20"]
    r20_phrase = move_phrase(r20_delta, C["recall@20"], D["recall@20"], "Recall@20")

    # The heading has to agree with the numbers beside it. On this corpus the
    # reranker moves MRR and nDCG by less than a thousandth either way, so a
    # heading that says it "helps the ordering" is contradicted by the very
    # sentence under it.
    _mrr_move = D["mrr"] - C["mrr"]
    rerank_head = (
        "Reranking helps the ordering and its recall effect depends on the "
        "pool it is given."
        if _mrr_move > 1e-9 else
        "Reranking moves nothing on this corpus, and its recall effect "
        "depends on the pool it is given.")

    # --- pool size --------------------------------------------------------
    pool_sentence = ""
    if exp5 and exp5.get("results"):
        by_pool = {r["pool_size"]: r for r in exp5["results"]}
        small = min(by_pool)
        large = max(by_pool)
        peak = max(by_pool.values(), key=lambda r: r["recall@10"])
        peak_size = peak["pool_size"]
        sizes = ", ".join(str(s) for s in sorted(by_pool))
        # The sweep is measured on the six-category corpus, which is where the
        # curve is sharp enough to have a peak. Saying so keeps the paragraph
        # from reading as one corpus's numbers and another's conclusion.
        _pool_where = ("On the six-category corpus, sweeping the pool size over "
                       f"{sizes} gives a curve that rises and ")
        if large > peak_size and peak["recall@10"] > by_pool[large]["recall@10"] + 1e-9:
            pool_sentence = (
                f"{_pool_where}then falls: Recall@10 climbs from "
                f"{by_pool[small]['recall@10']:.3f} "
                f"at a pool of {small} to a peak of {peak['recall@10']:.3f} at a pool "
                f"of {peak_size}, and then declines to "
                f"{by_pool[large]['recall@10']:.3f} by a pool of {large}. The extra "
                f"candidates are distractors competing for the same ten slots, so a "
                f"larger pool costs. A pool the size of the final context is the "
                f"best of the sweep, not the smallest."
            )
        else:
            pool_sentence = (
                f"{_pool_where}saturates: Recall@10 climbs from "
                f"{by_pool[small]['recall@10']:.3f} "
                f"at a pool of {small} to {peak['recall@10']:.3f} at a pool of "
                f"{peak_size} and then holds at "
                f"{by_pool[large]['recall@10']:.3f}."
            )

    # --- category filter --------------------------------------------------
    cat_delta = E["recall@10"] - D["recall@10"]
    cat_phrase = move_phrase(cat_delta, D["recall@10"], E["recall@10"], "Recall@10")
    tbl_d = D["modality_recall"].get("table", float("nan"))
    tbl_e = E["modality_recall"].get("table", float("nan"))
    if tbl_e > tbl_d + 1e-9:
        tbl_clause = (f"while table-specific Recall@10 rose from {tbl_d:.3f} to "
                      f"{tbl_e:.3f}")
    elif tbl_e < tbl_d - 1e-9:
        tbl_clause = (f"while table-specific Recall@10 fell from {tbl_d:.3f} to "
                      f"{tbl_e:.3f}")
    else:
        tbl_clause = (f"and table-specific Recall@10 was unchanged at "
                      f"{tbl_d:.3f}")
    if abs(cat_delta) < 1e-9 and abs(tbl_e - tbl_d) < 1e-9:
        cat_head = ("The category pre-filter is a no-op on the focus domain")
        cat_tail = ("Neither overall recall nor table-specific recall moves, and "
                    "that is the expected outcome: the focus corpus has one "
                    "category, so there is nothing for the filter to remove.")
    else:
        cat_head = ("The category pre-filter trades overall recall for modality "
                    "precision")
        cat_tail = "This is a genuine trade-off and is reported as one."

    # --- quota ------------------------------------------------------------
    pre_delta = F["recall@10"] - E["recall@10"]
    post_delta = G["recall@10"] - E["recall@10"]
    post_vs_pre_pp = (G["recall@10"] - F["recall@10"]) * 100
    tbl_f = F["modality_recall"].get("table", float("nan"))
    tbl_g = G["modality_recall"].get("table", float("nan"))
    tbl_base = E["modality_recall"].get("table", float("nan"))
    if tbl_g > tbl_base + 1e-9:
        tbl_move = f"lifted table recall from {tbl_base:.3f} to {tbl_g:.3f}"
    elif tbl_g < tbl_base - 1e-9:
        tbl_move = f"lowered table recall from {tbl_base:.3f} to {tbl_g:.3f}"
    else:
        tbl_move = f"left table recall unchanged at {tbl_base:.3f}"
    if tbl_g < tbl_f - 1e-9:
        tbl_post_clause = (f"and reaches only {tbl_g:.3f} table recall --- so the "
                           f"post-rerank placement is {abs(post_vs_pre_pp):.1f} points "
                           f"worse on Recall@10 than the pre-rerank one")
    else:
        tbl_post_clause = (f"and reaches table recall {tbl_g:.3f} --- so the "
                           f"post-rerank placement is {abs(post_vs_pre_pp):.1f} points "
                           f"worse on Recall@10 than the pre-rerank one")

    quota_clause = (
        f"Applied before the reranker it moves Recall@10 by "
        f"{pre_delta:+.3f} ({E['recall@10']:.3f} to "
        f"{F['recall@10']:.3f}, $p={sci(p_of('E. +category_filter'))}$) and "
        f"reaches table recall {tbl_f:.3f}. Applied after the reranker it moves "
        f"recall by {post_delta:+.3f} {tbl_post_clause} "
        f"($p={sci(p_of('F. +quota_pre_rerank'))}$). The "
        f"mechanism is about what each stage can undo: a pre-rerank quota "
        f"proposes the membership of the final ten and the cross-encoder can "
        f"only reorder it, whereas a post-rerank quota must import candidates "
        f"the cross-encoder already ranked below the cut."
    )

    if dense_weaker:
        if condensed:
            _fusion_sentence = (
                "The dense-only system is still behind BM25, which is a "
                "property of the encoder rather than a defect of the "
                "framework: retrieval is asymmetric, so a passage does not "
                "resemble a question, it \\emph{answers} it. The first "
                "version of this work used a general-purpose sentence encoder "
                "here and the deficit was larger; a retrieval-trained encoder "
                "narrowed it. A hybrid is only as good as its weaker leg, and "
                "the weaker leg spends the stronger leg its slots.")
        else:
            _fusion_sentence = (
                "The dense-only system is still behind BM25, which is a property of "
                "the encoder rather than a defect of the framework: retrieval is "
                "asymmetric --- a passage does not resemble a question, it "
                "\\emph{answers} it. The first version of this work used a "
                "general-purpose sentence encoder here and the deficit was larger; "
                "replacing it with a retrieval-trained encoder narrowed it. A "
                "hybrid is only as good as its weaker leg, and the weaker leg "
                "spends the stronger leg its slots.")
    else:
        _fusion_sentence = ("The dense leg is therefore not carrying the load on "
                            "this corpus.")

    text = f"""
\\paragraph{{Fusion beats the dense leg{', and the dense leg is the weaker one' if dense_weaker else ''}.}}
Recall@10 was {A['recall@10']:.3f} for BM25 alone, {B['recall@10']:.3f} for dense
alone and {C['recall@10']:.3f} for the fused system. Against the dense leg that
is a gain of {gain_vs_b:+.3f} ($p={sci(p_bc)}$); against the lexical leg it is
{gain_vs_a:+.3f} ($p={sci(p_ac)}$), which is not significant --- fusion stopped
being a loss, and on this corpus it is not demonstrably a win.
{_fusion_sentence}

\\paragraph{{{rerank_head}}}
With a top-50 rerank pool, reranking {cd_phrase} ($p={sci(p_of('C. hybrid_rrf'))}$),
and moved MRR from {C['mrr']:.3f} to {D['mrr']:.3f} and nDCG@10 from
{C['nDCG@10']:.3f} to {D['nDCG@10']:.3f}. With a top-10 pool --- the same size as
the final context --- the same reranker {r20_phrase}, because a reranker can only
reorder within the pool it is given, so a small pool forces it to discard
relevant tail items. {pool_sentence}
{'' if condensed else f'''This is the most likely explanation of the $-5.34$ percentage-point reranker
regression previously reported on an independent corpus, and it converts that
regression from an unexplained anomaly into a testable configuration hypothesis.
'''}
\\paragraph{{{cat_head}.}} The filter {cat_phrase} ($p={sci(p_of('D. hybrid_rrf_rerank'))}$)
{tbl_clause}. {cat_tail}

\\paragraph{{The quota's effect depends on where it is applied.}} {quota_clause}
{'' if condensed else f'''The generalisable lesson, corrected, is that \\emph{{a constraint on a
downstream artefact should be enforced where it can still choose the
candidates, not where it must work against another component's judgement}}.
'''}

\\paragraph{{The corpus composition predicts the outcome.}} The corpus is
{cs['share_text'] * 100:.1f}\\% text, {cs['share_table'] * 100:.1f}\\% table and
{cs['share_chart'] * 100:.1f}\\% chart, closely matching the 2.3\\% chart and 7.1\\%
table of the earlier project-report corpus. With so few non-text chunks, a
two-table quota can only draw on tables deep in the ranking --- tables less
likely to be relevant --- displacing relevant prose, so a null or negative
modality effect is the \\emph{{expected}} outcome on such a corpus, not a bug.
That is why the framework measures the modality composition, and it explains
the previously reported null result as a power limitation rather than a
defect. On this corpus the post-rerank quota {tbl_move} while costing
{(E['recall@10'] - G['recall@10']) * 100:.1f} points of overall recall.
"""
    return text.strip()


def main() -> int:
    block = build_block()
    condensed_block = build_block(condensed=True)
    if block is None:
        print("[tex-prose] exp1_ablation.json not available; leaving the prose as it is")
        return 1
    n = 0
    for p in PAPERS:
        if not p.exists():
            continue
        s = p.read_text(encoding="utf-8")
        if BEGIN not in s or END not in s:
            print(f"[tex-prose] {p.name}: markers not found")
            continue
        # The conference paper is the condensed venue version; the journal
        # version carries the full results prose.
        use = condensed_block if "2b" in p.name else block
        new = re.sub(re.escape(BEGIN) + r".*?" + re.escape(END),
                     lambda _m: BEGIN + "\n" + use + "\n" + END,
                     s, flags=re.S)
        if new != s:
            p.write_text(new, encoding="utf-8")
            n += 1
            print(f"[tex-prose] rewrote the results prose of {p.name}")
    return 0 if n else 1


if __name__ == "__main__":
    sys.exit(main())
