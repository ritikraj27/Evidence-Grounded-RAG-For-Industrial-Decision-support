"""Where each result file comes from.

This thesis reports two evaluations, and they answer different questions:

* the **focus domain** — supply chain management, the single industrial
  domain the work is about. Its ablation, gate, contradiction and pool-size
  results are the headline numbers, and its case study is the worked
  before-and-after demonstration.
* the **six-category corpus** — the source of the cross-category transfer
  experiment. That experiment needs a subset of categories to transfer to
  held-out ones, so it is meaningless on a single-domain corpus.

So the generators read the focus results first and fall back to the
multi-category ones, except for the transfer experiment, which is read only
from the multi-category corpus. If the focus run has not been made, the
multi-category results are used throughout, so the build still works.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

#: The focus-domain run: the headline numbers.
PRIMARY = ROOT / "impl" / "results_focus"
#: The multi-category run: the cross-category transfer study.
SECONDARY = ROOT / "impl" / "results"
#: The industrial (eCFR) run: the second corpus.
INDUSTRIAL = ROOT / "impl" / "results_industrial"

#: The results that sit on the retrieval, and what each of them is called in
#: prose. Every one of them is computed over retrieved passages, so every
#: one of them sits on the retrieval configuration it was taken under -- and
#: a result measured under the earlier placement is not comparable with one
#: measured under the shipped one. The list lives here because two things
#: read it: the limitation's disclosure, and the check that says the
#: disclosure rests on the files rather than on an assumption.
#:
#: The third element of each entry says why that measurement could not be
#: re-taken, where that is the reason. The claim-band evaluations are not a
#: script that was not run; they are a panel of reader agents under a
#: written protocol, and reproducing the panel is not the same measurement.
#:
#: The list is every result the deliverables quote that *depends on the
#: retrieval*, and nothing else. Three things are deliberately absent, and
#: each was checked rather than assumed:
#:
#: * the contradiction detector (`exp3`, and the reader-labelled precision
#:   and control that sit on it) retrieves with ``apply_quota=False``, so it
#:   never sees the quota and is the same measurement under either placement;
#: * the unanswerable-class audit (`exp12`) measures the benchmark's own
#:   question set -- the question-only policy and the class's separability
#:   -- and never retrieves;
#: * the scorer validation (`exp8`) scores synthetic truths, fabrications
#:   and foreign passages.
#:
#: Getting this wrong in the permissive direction is what the mechanism
#: exists to prevent: an entry that does not belong makes the disclosure
#: claim less than it should, and a missing entry makes it claim more than
#: it should.
PLACEMENT_STAMPED_RESULTS = (
    ("the generator-side comparison",
     PRIMARY / "exp8_generation.json", None),
    ("the generator-side comparison under the answering condition",
     PRIMARY / "exp8_generation_answering.json", None),
    ("the per-claim band evaluation against the gold evidence",
     PRIMARY / "exp17_claim_band_eval.json",
     "its labels come from a panel of reader agents under a written protocol "
     "and could not be reproduced"),
    ("the per-claim band evaluation against the retrieved evidence",
     PRIMARY / "exp18_claim_band_eval.json",
     "its labels come from a panel of reader agents under a written protocol "
     "and could not be reproduced"),
    ("the industrial corpus's per-claim band replication",
     INDUSTRIAL / "exp19_claim_band_eval.json",
     "its labels come from a panel of reader agents under a written protocol "
     "and could not be reproduced"),
    ("the focus domain's query-form validator",
     PRIMARY / "exp10_form_validator.json", None),
    ("the gate under each retriever",
     PRIMARY / "exp2b_gate_per_retriever.json", None),
    ("the generator-completion check",
     PRIMARY / "exp13_generator_completion.json", None),
    ("the answer-validation conventions",
     PRIMARY / "exp8_answer_validation_conventions.json", None),
    ("the gate on the benchmark before the unanswerable class was rebuilt",
     PRIMARY / "exp2_gate_pre_unanswerable_repair.json", None),
    ("the focus corpus's case study",
     PRIMARY / "exp6_focus_case.json", None),
    ("the focus corpus's gate",
     PRIMARY / "exp2_gate.json", None),
    ("the focus corpus's ablation",
     PRIMARY / "exp1_ablation.json", None),
    ("the focus corpus's long-context cost half",
     PRIMARY / "exp7_long_context.json", None),
    ("the answer-side label audit",
     PRIMARY / "exp9_label_audit.json", None),
    # The multi-category corpus's own results. The deliverables quote them
    # throughout, and they sit on the retrieval just as the focus domain's
    # do, so the disclosure has to cover them too -- otherwise it would say
    # that every measurement depending on the retrieval was re-taken, while
    # three of these were still measured under the earlier placement.
    ("the multi-category corpus's ablation",
     SECONDARY / "exp1_ablation.json", None),
    ("the cross-category transfer",
     SECONDARY / "exp4_transfer.json", None),
    ("the multi-category corpus's rerank pool sweep",
     SECONDARY / "exp5_pool_size.json", None),
    ("the multi-category corpus's long-context cost half",
     SECONDARY / "exp7_long_context.json", None),
    ("the multi-category corpus's query-form probe",
     SECONDARY / "exp9_form_probe.json", None),
    ("the multi-category corpus's query-form validator",
     SECONDARY / "exp10_form_validator.json", None),
    ("the multi-category corpus's soft-prior result",
     SECONDARY / "exp22_soft_prior.json", None),
    # The industrial corpus's own retrieval-side results.
    ("the industrial corpus's ablation",
     INDUSTRIAL / "exp1_ablation.json", None),
    ("the industrial corpus's gate",
     INDUSTRIAL / "exp2_gate.json", None),
    ("the industrial corpus's rerank pool sweep",
     INDUSTRIAL / "exp5_pool_size.json", None),
    ("the industrial corpus's retrieved-evidence claim-band evaluation",
     INDUSTRIAL / "exp21_claim_band_eval_retrieved.json", None),
)


def load(name: str, required=()) -> dict | None:
    """Load a result file, preferring the focus-domain run.

    `required` lists keys the generator needs. A result file written by an
    earlier version of an experiment has a different schema, so it is
    treated as "not available" and the corresponding section is skipped
    rather than crashing the build.
    """
    for directory in (PRIMARY, SECONDARY):
        p = directory / f"{name}.json"
        if not p.exists():
            continue
        try:
            payload = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(payload, dict):
            continue
        if any(k not in payload for k in required):
            continue
        if payload.get("skipped"):
            continue
        return payload
    return None


def load_transfer(name: str, required=()) -> dict | None:
    """Load a result from the multi-category run only.

    The cross-category transfer experiment is defined on a multi-category
    corpus, so it is never taken from the focus-domain run.
    """
    p = SECONDARY / f"{name}.json"
    if not p.exists():
        return None
    try:
        payload = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None
    if not isinstance(payload, dict):
        return None
    if any(k not in payload for k in required):
        return None
    if payload.get("skipped"):
        return None
    return payload


def which() -> str:
    """Report which directory the headline numbers came from."""
    return "focus domain" if (PRIMARY / "exp1_ablation.json").exists() \
        else "multi-category corpus"


def _comp_index(comparisons):
    """Index the ablation's comparisons by their first rung.

    The ablation reports non-adjacent comparisons as well as adjacent ones --
    BM25 against the fused system, the reranker against a quota -- and a
    non-adjacent comparison starts with the same rung as the adjacent one it
    follows. Indexing by first rung in a plain dict comprehension therefore
    lets the later entry overwrite the earlier one, and a generator asking
    for "D -> E" is handed "D -> F" instead: real numbers, wrong question.
    The first entry registered under a key wins.
    """
    out = {}
    for c in comparisons:
        key = c["comparison"].split(" -> ")[0]
        if key not in out:
            out[key] = c
        # The full string is always available, so a non-adjacent comparison
        # can be asked for by name.
        out[c["comparison"]] = c
    return out


# --------------------------------------------------------------------------
# Experiment 8 -- the generator-side comparison
# --------------------------------------------------------------------------
#: The arms the experiment puts behind one generator. The names are the
#: ones the experiment writes into its JSON.
GEN_ARMS = ("rag_nogate", "rag@fitted", "rag@random", "rag@transferred",
            "long_context")

#: How each arm is named in prose.
GEN_LABELS = {
    "rag_nogate": "the same retrieval with the gate removed",
    "rag@fitted": "the framework at the operating point fitted on this benchmark",
    "rag@random": "a control that refuses as many questions as the fitted gate "
                  "did, but picks them at random",
    "rag@transferred": "the framework at the operating point transferred "
                        "unchanged from the cross-category half",
    "long_context": "the whole corpus in the prompt",
}

#: The two prompt conditions the generator-side comparison runs under.
#:
#: They differ by one sentence -- the permission to decline -- and by
#: nothing else: same model, same questions, same retrieval, same scorer.
#: The cautious condition is the deployed system. The answering condition is
#: where the gate's own contribution is measurable, because in the cautious
#: condition the generator declines the unanswerable questions on its own and
#: the gate's refusals are redundant with the prompt's.
GEN_CONDITIONS = ("cautious", "answering")

#: How each condition is named in prose.
GEN_CONDITION_LABELS = {
    "cautious": "the generator is permitted to decline",
    "answering": "the generator is required to answer",
}


def load_generation() -> dict | None:
    """The generator-side comparison, from the focus-domain run.

    Only the focus run is read: the thesis is about one industrial domain,
    and a comparison measured on the six-category corpus would be a different
    experiment with a different corpus in the prompt.
    """
    p = PRIMARY / "exp8_generation.json"
    if not p.exists():
        return None
    try:
        payload = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None


def pull_up_leading_numbers(text: str, vals: dict | None = None) -> str:
    """Stop a substituted number from starting a line.

    A line that begins with a number and a full stop reads as a markdown
    ordered-list item, and the DOCX writer treats it as one, so a paragraph
    can be cut in two by a number that happens to land at the start of a
    line. The templates wrap their prose at a fixed column, so whether a
    token's *value* lands at the start of a line depends on how long the
    value is -- it is not knowable when the template is written. This is
    therefore fixed after the substitution: a token whose value begins with
    a digit and which sits at the start of a line is pulled up onto the
    line above it. Markdown soft-wraps and the DOCX writer joins wrapped
    lines, so the rendered text is unchanged; what changes is that the
    paragraph is no longer cut in two.

    With ``vals`` the decision is made from the token's value, which is
    what the template stage uses. Without it, the decision is made from
    the rendered line, by tracking the ordered list it belongs to: a line
    that continues an open list (same indent, next number) is a list
    item and is left alone; anything else that starts with a number and a
    full stop is a broken paragraph and is joined to the line above.

    Fenced code blocks are left alone: inside them a leading number is
    data, not prose.
    """
    out: list[str] = []
    in_fence = False
    list_open = False
    list_indent = 0
    list_last = 0
    for line in text.split("\n"):
        stripped = line.lstrip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            out.append(line)
            continue
        if not line.strip():
            list_open = False
            out.append(line)
            continue
        if vals is not None:
            m = re.match(r"^([ \t]*)\{\{([A-Z0-9_]+)\}\}(.*)$", line)
            if m and not in_fence and out and out[-1].strip() \
                    and not out[-1].lstrip().startswith(("|", "-", "*", ">", "#")):
                _val = str(vals.get(m.group(2), ""))
                if _val.strip()[:1].isdigit():
                    out[-1] = (out[-1].rstrip() + " " + m.group(1) + "{{"
                               + m.group(2) + "}}" + m.group(3))
                    continue
        m2 = re.match(r"^([ \t]*)(\d+)\.\s+(.*)$", line)
        if m2 and not in_fence:
            _indent = len(m2.group(1))
            _n = int(m2.group(2))
            _prev_blank = (not out) or (not out[-1].strip())
            if list_open and _indent == list_indent and _n == list_last + 1:
                list_last = _n
                out.append(line)
                continue
            if not list_open and _prev_blank:
                list_open = True
                list_indent = _indent
                list_last = _n
                out.append(line)
                continue
            # Not a list item: it is a paragraph whose line happens to start
            # with a number, so it is joined to the line above it.
            if out:
                out[-1] = out[-1].rstrip() + " " + line.strip()
                continue
        out.append(line)
    return "\n".join(out)


def load_answer_validation_conventions() -> dict | None:
    """The scoring-convention sensitivity measurement (gaps G18 and G19).

    The two shipped answer tests are re-scored, on the *same* shipped
    answers, alongside two conventions taken from the published benchmarks:
    SQuAD 2.0's normalised exact match and token-level F1, and PopQA's
    containment rule. Nothing is re-run; the generator's answers and the
    benchmark's gold strings are both already in the shipped records.
    """
    p = PRIMARY / "exp8_answer_validation_conventions.json"
    if not p.exists():
        return None
    try:
        payload = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None


def _convention_accuracy(cond: dict, arm: str) -> dict:
    """One arm's accuracy under each convention."""
    return ((cond.get("arms") or {}).get(arm) or {}).get("accuracy") or {}


def _significant_under(convention: str, test: dict) -> bool:
    """Whether one convention calls a paired comparison significant.

    The binary conventions are tested with the exact McNemar; token-level
    F1 is a continuous score, so its analogue is a paired bootstrap whose
    interval excludes zero.
    """
    if convention == "squad_f1":
        return bool(test.get("excludes_zero"))
    p = test.get("p_value")
    return isinstance(p, (int, float)) and p <= 0.05


def answer_validation_conventions_summary(payload: dict | None) -> dict:
    """The headline numbers of the convention-sensitivity measurement.

    Every number is read out of the measurement rather than typed, so the
    prose that quotes them cannot drift from it. A missing measurement
    yields an empty dict and the prose says so.
    """
    out: dict = {}
    if not payload or payload.get("status") != "run":
        return out
    conds = payload.get("conditions") or {}
    if not conds:
        return out

    conventions = payload.get("conventions") or []
    out["n_conventions"] = len(conventions)
    out["conventions"] = list(conventions)

    # How often the two shipped tests disagree, question by question.
    dis, kaps = [], []
    for cond in conds.values():
        block = ((cond.get("agreement") or {})
                 .get("nli_vs_keyterm") or {})
        for v in block.values():
            if isinstance(v.get("disagreement_rate"), (int, float)):
                dis.append(v["disagreement_rate"])
            if isinstance(v.get("cohen_kappa"), (int, float)):
                kaps.append(v["cohen_kappa"])
    if dis:
        out["disagreement_min"] = round(min(dis), 4)
        out["disagreement_max"] = round(max(dis), 4)
    if kaps:
        out["kappa_min"] = round(min(kaps), 4)
        out["kappa_max"] = round(max(kaps), 4)

    # How many answered questions change their verdict with the convention.
    dep = []
    for cond in conds.values():
        for v in (cond.get("consensus") or {}).values():
            if isinstance(v.get("convention_dependent"), int):
                dep.append(v["convention_dependent"])
    if dep:
        out["convention_dependent_min"] = min(dep)
        out["convention_dependent_max"] = max(dep)

    # The absolute level, per arm, under each convention.
    levels, spreads, spread_by_arm = {}, [], {}
    for cname, cond in conds.items():
        for arm in cond.get("arms") or {}:
            acc = _convention_accuracy(cond, arm)
            vals = {k: v.get("accuracy") for k, v in acc.items()
                    if k != "squad_f1" and isinstance(v.get("accuracy"),
                                                      (int, float))}
            if vals:
                levels[f"{cname}/{arm}"] = {k: round(v, 4)
                                            for k, v in vals.items()}
                _sp = round(max(vals.values()) - min(vals.values()), 4)
                spreads.append(_sp)
                spread_by_arm[f"{cname}/{arm}"] = _sp
            f1 = (acc.get("squad_f1") or {}).get("mean_f1")
            if isinstance(f1, (int, float)):
                levels[f"{cname}/{arm}"]["squad_f1_mean"] = round(f1, 4)
    out["levels"] = levels
    out["spread_by_arm"] = spread_by_arm
    if spreads:
        out["spread_max"] = max(spreads)
        out["spread_min"] = min(spreads)

    # How many conventions call each paired comparison significant.
    for cname, cond in conds.items():
        for pair, block in (cond.get("pairs") or {}).items():
            tests = block.get("tests") or {}
            hits = [c for c in conventions
                    if c in tests and _significant_under(c, tests[c])]
            out[f"sig_{cname}_{pair}"] = len(hits)
            out[f"sig_{cname}_{pair}_of"] = len(conventions)
            out[f"sig_{cname}_{pair}_which"] = hits
    return out


def answer_validation_conventions_claim(payload: dict | None) -> str:
    """One paragraph stating what the convention sensitivity settles.

    It is carried verbatim by the guide's E.8 and by the plain-language
    guide, so the two documents cannot disagree about how much the
    answer-accuracy column depends on the scoring convention.
    """
    s = answer_validation_conventions_summary(payload)
    if not s:
        return ("The scoring-convention sensitivity measurement has not been "
                "made on this corpus.")
    gate = []
    lc = []
    for cname in ("cautious", "answering"):
        g = s.get(f"sig_{cname}_rag@fitted_vs_rag_nogate")
        if isinstance(g, int):
            gate.append(f"{g} of {s.get(f'sig_{cname}_rag@fitted_vs_rag_nogate_of')}")
        l = s.get(f"sig_{cname}_rag_nogate_vs_long_context")
        if isinstance(l, int):
            lc.append(f"{l} of {s.get(f'sig_{cname}_rag_nogate_vs_long_context_of')}")
    return (
        f"The two shipped tests were re-scored, on the same shipped answers, "
        f"alongside three conventions taken from the published benchmarks: "
        f"SQuAD 2.0's normalised exact match, SQuAD's token-level F1, and "
        f"PopQA's containment rule, so five conventions in all. The two "
        f"shipped tests disagree on between {s.get('disagreement_min', 0) * 100:.0f} "
        f"and {s.get('disagreement_max', 0) * 100:.0f} per cent of the "
        f"answered questions and their Cohen's kappa runs from "
        f"{s.get('kappa_min', 0):.2f} to {s.get('kappa_max', 0):.2f}, which is "
        f"at or below the agreement Cohen called 'slight'. The absolute level "
        f"of the accuracy column moves by as much as "
        f"{s.get('spread_max', 0):.2f} across the five conventions, and the "
        f"verdict on between {s.get('convention_dependent_min', 0)} and "
        f"{s.get('convention_dependent_max', 0)} answered questions per arm "
        f"depends on which convention is used. What the measurement settles "
        f"is that no arm comparison on the answer side reaches significance "
        f"under more than one convention: the gate-against-no-gate "
        f"comparison reaches none in either condition "
        f"({', '.join(gate)}), and the retrieval-against-long-context "
        f"comparison reaches {', '.join(lc)} in the cautious and answering "
        f"conditions respectively. Everything the gate is claimed on -- "
        f"coverage, cost, the refusal of questions that should be refused, "
        f"the claim-support figures and every retrieval measurement -- is "
        f"computed from counts and from the evidence rather than from the "
        f"answer string, so it is the same under all five conventions."
    )


#: The six industrial-engineering categories the thesis actually built, with
#: the short token prefix each one's counts are bound to.
SCOPE_CATEGORIES = [
    ("supply_chain_management", "SCM", "Supply Chain Management (the focus domain)"),
    ("predictive_maintenance", "PM", "Predictive Maintenance"),
    ("reliability_engineering", "RE", "Reliability Engineering"),
    ("quality_engineering", "QE", "Quality Engineering"),
    ("production_scheduling", "PS", "Production Scheduling"),
    ("facility_layout", "FL", "Facility Layout & Location"),
]


def scope_summary() -> dict:
    """The document and chunk count of each category that was built.

    The twelve-category promise is reconciled against what is in the
    repository, so the counts in the reconciliation table are the
    repository's own and not a hand-typed copy.
    """
    manifest = ROOT / "impl" / "data" / "corpus" / "manifest.json"
    index = ROOT / "impl" / "artifacts" / "index.json"
    if not manifest.exists() or not index.exists():
        return {}
    try:
        docs = json.loads(manifest.read_text(encoding="utf-8"))
        chunks = json.loads(index.read_text(encoding="utf-8")).get("chunks") or []
    except Exception:
        return {}
    doc_counts: dict[str, int] = {}
    for d in docs:
        cat = d.get("category")
        doc_counts[cat] = doc_counts.get(cat, 0) + 1
    chunk_counts: dict[str, int] = {}
    for c in chunks:
        cat = c.get("category")
        chunk_counts[cat] = chunk_counts.get(cat, 0) + 1
    out = {}
    for key, short, label in SCOPE_CATEGORIES:
        out[short] = {
            "key": key,
            "label": label,
            "documents": doc_counts.get(key, 0),
            "chunks": chunk_counts.get(key, 0),
        }
    out["n_documents_total"] = len(docs)
    out["n_chunks_total"] = len(chunks)
    out["n_categories_built"] = sum(1 for k, _s, _l in SCOPE_CATEGORIES
                                    if doc_counts.get(k))
    return out


def load_gate_per_retriever() -> dict | None:
    """The gate fitted separately on each retriever, with the frontier.

    Limitation L10 says the calibration is fitted per retriever rather than
    universally, and asks for the per-retriever threshold and the frontier
    as a curve. This is that measurement.
    """
    return load("exp2b_gate_per_retriever", ["retrievers", "transfer"])


def gate_per_retriever_summary(payload: dict | None) -> dict:
    """The headline numbers of the per-retriever gate measurement."""
    out: dict = {}
    if not payload:
        return out
    retrievers = payload.get("retrievers") or {}
    if not retrievers:
        return out
    per = {}
    for name, blk in retrievers.items():
        op = blk.get("operating_point") or {}
        met = blk.get("calibration_metrics") or {}
        per[name] = {
            "label": blk.get("label"),
            "fitted_tau": blk.get("fitted_tau"),
            "answerable_answered": op.get("answerable_answered"),
            "unanswerable_refused": op.get("unanswerable_refused"),
            "coverage": op.get("coverage"),
            "brier": met.get("brier"),
            "ece": met.get("ece"),
            "n_evidence_found": blk.get("n_evidence_found"),
            "n_answerable": blk.get("n_answerable"),
            "sweep_points": len(blk.get("threshold_sweep") or []),
            "frontier_points": len(blk.get("risk_coverage") or []),
        }
    out["per_retriever"] = per
    taus = [v["fitted_tau"] for v in per.values()
            if isinstance(v.get("fitted_tau"), (int, float))]
    if taus:
        out["tau_min"] = min(taus)
        out["tau_max"] = max(taus)
        out["tau_spread"] = round(max(taus) - min(taus), 4)
    transfer = ((payload.get("transfer") or {}).get("per_retriever") or {})
    out["transfer"] = {
        name: {
            "transferred_tau": blk.get("transferred_tau"),
            "refitted_tau": blk.get("refitted_tau"),
            "transferred_answerable_answered": (
                blk.get("transferred_operating_point") or {}
            ).get("answerable_answered"),
            "transferred_unanswerable_refused": (
                blk.get("transferred_operating_point") or {}
            ).get("unanswerable_refused"),
            "refitted_answerable_answered": (
                blk.get("refitted_operating_point") or {}
            ).get("answerable_answered"),
            "refitted_unanswerable_refused": (
                blk.get("refitted_operating_point") or {}
            ).get("unanswerable_refused"),
            "cost": blk.get("cost_of_transfer"),
        }
        for name, blk in transfer.items()
    }
    return out


def load_soft_prior() -> dict | None:
    """The soft-prior alternative to the hard category pre-filter.

    Threat T1 said the pre-filter's cost was measured but its proposed
    repair was not. This is the repair, measured.
    """
    return load("exp22_soft_prior", ["systems", "comparisons"])


def soft_prior_summary(payload: dict | None) -> dict:
    """The headline numbers of the soft-prior measurement."""
    out: dict = {}
    if not payload:
        return out
    systems = payload.get("systems") or {}
    if not systems:
        return out
    per = {}
    for name, blk in systems.items():
        ev = blk.get("eval") or {}
        per[name] = {
            "label": blk.get("label"),
            "recall_at_10": ev.get("recall@10"),
            "recall_at_20": ev.get("recall@20"),
            "mrr": ev.get("mrr"),
            "ndcg_at_10": ev.get("nDCG@10"),
            "modality_recall": blk.get("modality_recall"),
        }
    out["per_config"] = per
    out["n_queries"] = payload.get("n_queries")
    out["n_out_of_category_gold"] = payload.get("n_out_of_category_gold")
    # The best soft prior: the one with the highest recall, and -- if the
    # recalls tie -- the highest MRR. Which configuration that is has to be
    # read out of the measurement rather than assumed, because the weight
    # that promotes the in-category chunks hardest is not obviously the one
    # that retrieves best.
    soft = {k: v for k, v in per.items() if k.startswith("soft_prior")}
    if soft:
        best = max(soft.items(),
                   key=lambda kv: (kv[1].get("recall_at_10") or 0.0,
                                   kv[1].get("mrr") or 0.0))
        out["best_soft_name"] = best[0]
        out["best_soft"] = best[1]
    out["hard_filter"] = per.get("hard_filter")
    out["no_category"] = per.get("no_category")
    comps = {}
    for c in payload.get("comparisons") or []:
        name = c.get("comparison", "")
        comps[name] = {
            "delta_recall": c.get("delta"),
            "p_value": (c.get("wilcoxon") or {}).get("p_value"),
            "effect_size": (c.get("wilcoxon") or {}).get("effect_size"),
            "delta_mrr": c.get("delta_mrr"),
            "p_value_mrr": (c.get("wilcoxon_mrr") or {}).get("p_value"),
            "delta_ndcg": c.get("delta_ndcg"),
        }
    out["comparisons"] = comps
    return out


def load_label_audit() -> dict | None:
    """The audit of the benchmark's answerable labels.

    Some silver-standard answer labels are attached to the wrong question --
    the table-question generator names the column the key came from rather
    than the column the answer came from. The gold *chunk* is still right, so
    the retrieval-side metrics are unaffected; only the answer-side accuracy
    is. This is measured rather than asserted, because a benchmark defect
    found by hand is a claim and one found by a script is a measurement.
    """
    p = PRIMARY / "exp9_label_audit.json"
    if not p.exists():
        return None
    try:
        payload = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None


def load_generation_conditions() -> dict:
    """Both prompt conditions of the generator-side comparison.

    The cautious condition is the deployed system and lives in the original
    result file. The answering condition is the same experiment with the
    permission to decline removed, and it lives beside it. A condition that
    has not been run is simply absent, so the callers can say what is
    untested rather than what is unfavourable.
    """
    out: dict = {}
    cautious = load_generation()
    if cautious:
        out["cautious"] = cautious
    p = PRIMARY / "exp8_generation_answering.json"
    if p.exists():
        try:
            payload = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            payload = None
        if isinstance(payload, dict):
            out["answering"] = payload
    return out


def load_generation_replication() -> dict:
    """The generator-side comparison repeated on a second generator.

    One generator behind five arms settles the hypothesis for one model. The
    replication is the same design on a different model -- same corpus, same
    benchmark, same arms, same scorer, same two prompt conditions -- so that
    the gate's contribution can be read as a property of the framework rather
    than of one checkpoint. A condition that has not been run is absent rather
    than absent-in-favour: the caller can then say what is untested rather
    than what is unfavourable.
    """
    out: dict = {}
    for cond, fname in (("cautious", "exp8_generation_flash.json"),
                        ("answering", "exp8_generation_answering_flash.json")):
        p = PRIMARY / fname
        if not p.exists():
            continue
        try:
            payload = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(payload, dict) and payload.get("status") == "run":
            out[cond] = payload
    return out


def generation_replication_rows(replication: dict | None) -> list[dict]:
    """One row per (condition, arm) for the second generator.

    The table is the comparison as it was run, so the rows are read off the
    payload rather than assembled from a narrative. An arm that did not run
    has no row.
    """
    rows: list[dict] = []
    if not replication:
        return rows
    for cond in ("cautious", "answering"):
        payload = replication.get(cond)
        if not payload:
            continue
        model = payload.get("model", "the second generator")
        for arm in GEN_ARMS:
            blk = gen_arm(payload, arm)
            if not blk:
                continue
            un = blk.get("unanswerable") or {}
            an = blk.get("answerable") or {}
            rows.append({
                "condition": cond,
                "model": model,
                "arm": arm,
                "unanswerable_answered": int(un.get("n_answered", 0)),
                "unanswerable_n": int(un.get("n", 0)),
                "unanswerable_rate": un.get("answer_rate"),
                "answerable_answered": int(an.get("n_answered", 0)),
                "answerable_n": int(an.get("n", 0)),
                "accuracy_nli": an.get("accuracy_nli"),
                "accuracy_keyterm": an.get("accuracy_keyterm"),
                "tokens_in": int((blk.get("tokens") or {}).get("total_input", 0)),
                "cost_usd": (blk.get("cost") or {}).get("total_usd"),
                "p_value": (((payload.get("paired") or {}).get(arm) or {})
                            .get("unanswerable") or {}).get("p_value"),
            })
    return rows


def generation_replication_claim(replication: dict | None) -> str:
    """What the second generator shows, written from the measured sign.

    A replication that came out the other way is reported the other way. The
    claim is about the gate's effect within the second generator's own run --
    same retrieval, same questions, same scorer, one instruction changed --
    and the text says so rather than implying the two generators' rates are
    directly comparable, because they are not: a generator writes longer
    answers than another and refuses for its own reasons.
    """
    if not replication:
        return ("The comparison has not been repeated on a second generator, so "
                "the gate's contribution is established for one model only, and "
                "a single-model result cannot support a general claim.")

    answering = replication.get("answering")
    cautious = replication.get("cautious")
    model = ((answering or cautious or {}).get("model")
             or "the second generator")

    if not answering:
        return (f"The comparison was repeated on a second generator "
                f"({model}) under the cautious prompt only. The answering "
                f"condition -- the one that isolates the gate's contribution "
                f"-- was not run on it, so the replication is partial.")

    ng = gen_arm(answering, "rag_nogate") or {}
    ft = gen_arm(answering, "rag@fitted") or {}
    rnd = gen_arm(answering, "rag@random") or {}
    ng_un = ng.get("unanswerable") or {}
    ft_un = ft.get("unanswerable") or {}
    ft_an = ft.get("answerable") or {}
    pr = (((answering.get("paired") or {}).get("rag@fitted") or {})
          .get("unanswerable") or {})
    p_value = pr.get("p_value")
    ng_rate = ng_un.get("answer_rate", 0.0)
    ft_rate = ft_un.get("answer_rate", 0.0)

    if ft_rate < ng_rate:
        supported = (
            f"On {model} under the answering condition the gate cut the rate "
            f"of answering unanswerable questions from {ng_rate:.3f} to "
            f"{ft_rate:.3f}, a fall of "
            f"{(ng_rate - ft_rate) * 100:.1f} points, and the framework "
            f"answered {int(ft_an.get('n_answered', 0))} of "
            f"{int(ft_an.get('n', 0))} answerable questions")
        if p_value is not None:
            supported += (
                f"; paired question by question, the exact two-sided McNemar "
                f"test on the discordant pairs gives p = {p_value:.3g}")
        supported += (
            f". The gate's contribution is therefore not a property of one "
            f"checkpoint")
        if rnd:
            rnd_un = rnd.get("unanswerable") or {}
            supported += (
                f", and the random control at the same refusal count answered "
                f"{int(rnd_un.get('n_answered', 0))} of "
                f"{int(rnd_un.get('n', 0))} against the gate's "
                f"{int(ft_un.get('n_answered', 0))}")
        return supported + "."

    return (f"On {model} under the answering condition the gate did not "
            f"reduce the rate of answering unanswerable questions "
            f"({ng_rate:.3f} without it, {ft_rate:.3f} with it), so the "
            f"result does not carry across to a second generator and is "
            f"reported as a single-model result.")


def generation_replication_cautious_claim(replication: dict | None) -> str:
    """What the cautious prompt shows on the second generator.

    Under the cautious prompt the generator is allowed to decline, and on the
    first generator it largely did, which made the gate's refusals redundant
    with the prompt's. Whether that is a property of the prompt or of that one
    generator is exactly what the replication can say, so the sentence is
    written from the measured sign.
    """
    if not replication:
        return "The cautious condition was not run on the second generator."
    cau = replication.get("cautious")
    if not cau:
        return ("The cautious condition was not run on the second generator; "
                "only the answering condition was.")
    ng = gen_arm(cau, "rag_nogate") or {}
    ft = gen_arm(cau, "rag@fitted") or {}
    ng_rate = (ng.get("unanswerable") or {}).get("answer_rate", 0.0)
    ft_rate = (ft.get("unanswerable") or {}).get("answer_rate", 0.0)
    model = cau.get("model", "the second generator")
    if ft_rate < ng_rate:
        return (f"Under the cautious prompt on {model} the gate cut the rate "
                f"of answering unanswerable questions from {ng_rate:.3f} to "
                f"{ft_rate:.3f}, so on this generator the prompt had not "
                f"already realised the gate's function.")
    return (f"Under the cautious prompt on {model} the gate did not reduce "
            f"the rate of answering unanswerable questions "
            f"({ng_rate:.3f} without it, {ft_rate:.3f} with it), which is "
            f"what the first generator showed too: the prompt had already "
            f"realised the gate's function on that slice.")


def shipped_quota_position() -> str:
    """Where the shipped system applies the modality quota.

    Read from the configuration rather than asserted, so the deliverables
    describe what the code does. The ablation ranks the pre-rerank placement
    better; when the system ships the other one, that has to be said
    plainly, and when it ships the recommended one the corresponding
    limitation and next step disappear by themselves.
    """
    try:
        import sys

        if str(ROOT / "impl") not in sys.path:
            sys.path.insert(0, str(ROOT / "impl"))
        from src.config import CONFIG
        return CONFIG.modality.position
    except Exception:
        return "unknown"


def next_steps(replication: dict | None = None) -> list[dict]:
    """The project's open threads, in priority order.

    One list, used by the status report, the technical documentation and the
    defence deck. They used to be three lists that had drifted apart -- a
    panel finds that in ten seconds and a reader in five minutes -- so they
    are one list now, and the deck's items are the report's. The count is
    fixed so that a template can hold them positionally; what changes
    between builds is the *content* of an item, when the measurement it
    refers to has landed. An item leaves the list when the gap it names is
    closed: the gate-per-retriever item left it on 12 November 2026, when
    that measurement was made.
    """
    ran = bool(replication)
    if ran:
        item1_short = ("Extend the generator-side comparison to a generator "
                       "from a different provider family.")
        item1_long = (
            "**Extend the generator-side comparison to a generator from a "
            "different provider family.** The comparison has now been run on "
            "two generators from the same provider ({GEN_MODEL} and "
            "{GEN2_MODEL}), and the gate's contribution reproduced on both. A "
            "second *provider* would rule out the family rather than the "
            "checkpoint, which is the remaining version of this question.")
    else:
        item1_short = ("Repeat the generator-side comparison on a generator "
                       "that returns text on table questions.")
        item1_long = (
            "**Repeat the generator-side comparison on a generator that "
            "returns text on the table questions.** One generator behind five "
            "arms settles the hypothesis once; one generator settles it for "
            "one model. The replication was attempted on "
            "{GENCOMP_FAILING_MODEL} and could not be run: it returned no "
            "text on {GENCOMP_FAILING_EMPTY_N} of the "
            "{GENCOMP_FAILING_EMPTY_TOTAL} questions it was asked, of which "
            "{GENCOMP_FAILING_EMPTY_TABLE_N} of the "
            "{GENCOMP_FAILING_EMPTY_TABLE_TOTAL} were the benchmark's "
            "table lookups -- it spends its whole output budget thinking and "
            "comes back empty. Raising the budget fourfold rescued "
            "{GENCOMP_FAILING_RESCUED} of those, and "
            "{GENCOMP_FAILING_STILL_EMPTY} were still empty at that budget, "
            "so this is not a shortage of output room. The obstacle is now "
            "specific rather than vague: it wants a generator that can parse "
            "a table, or one whose reasoning budget is bounded. Both prompt "
            "conditions have been run on {GEN_MODEL}, and the result is that "
            "the gate's contribution does not depend on the generator's "
            "willingness to decline -- which is a claim about the *gate*, so "
            "it wants a second generator to hold.")

    _quota_step = []
    if shipped_quota_position() == "post_rerank":
        # The discrepancy exists only while the system ships the placement the
        # ablation ranks second.
        _quota_step = [{
            "short": ("Move the modality quota before the reranker and "
                      "re-measure everything that depends on it."),
            "long": (
                "**Move the modality quota before the reranker, and re-measure "
                "everything that depends on it.** The ablation says the quota "
                "belongs before the cross-encoder: applied there it fixes the "
                "membership of the final ten, so the reranker can reorder them "
                "but cannot change which ten they are, and the forced table "
                "chunk survives. The system as built applies it after, because "
                "that was the September 2026 design and every measurement in "
                "this project was taken with it. Moving it would change the "
                "retrieval that every other measurement sits on -- the gate's "
                "calibration, the generator-side comparison and the per-claim "
                "results -- so it is one change and a full re-measurement "
                "rather than a one-line edit. It is the first thing to do, "
                "because it is the one place where this project knows its own "
                "shipped configuration is not the one it recommends."),
        }]

    return _quota_step + [
        {
            "short": item1_short,
            "long": item1_long,
        },
        {
            "short": ("Compare the gate against a token-level faithfulness "
                      "monitor, not only against a prompt."),
            "long": (
                "**Compare the gate against a token-level faithfulness "
                "monitor.** The gate is currently measured against a "
                "prompt-level control and against the always-flag and "
                "never-flag baselines, but not against another *detector* of "
                "the same kind of thing. A SYNCHECK-style token-level monitor "
                "would put the two on one axis: both score the retrieved "
                "evidence, and the question becomes which is the better "
                "filter at a stated operating point, on one risk-coverage "
                "curve with both on it. The thesis's claim is about the gate "
                "as a branch rather than an instruction, and that claim does "
                "not need the comparison -- but the comparison is what a "
                "practitioner deciding whether to adopt the gate would ask "
                "for, and it is one implementation away."),
        },
        {
            "short": ("Settle the positional comparison's power: the "
                      "direction is {RO5_POSITIONAL_DIRECTION_ADVERB}, the "
                      "significance is not."),
            "long": (
                "**Settle the positional comparison's magnitude and power.** "
                "The direction is {RO5_POSITIONAL_DIRECTION_ADVERB}: keeping "
                "the first claims of an answer carries a higher risk than "
                "keeping the band's `grounded` claims in "
                "{RO5_POSITIONAL_DIRECTION_PHRASE} corpus-and-protocol "
                "combinations. What varies is the magnitude -- "
                "{RO5_GOLD_BAND_MINUS_FIRST} against "
                "{RO5_RETRIEVED_BAND_MINUS_FIRST} on the focus corpus and "
                "{IND_RO5_GOLD_BAND_MINUS_FIRST} against "
                "{IND_RO5_RETRIEVED_BAND_MINUS_FIRST} on the industrial one, "
                "all at matched coverage -- and only the largest of them "
                "clears significance (focus gold, p = {RO5_GOLD_POSITION_P}). "
                "Why the gap is four times larger on the focus corpus's gold "
                "protocol than on its retrieved protocol is not established, "
                "and a larger sample of annotated claims would settle it. The "
                "band is reported as a filter and not as a ranking in the "
                "meantime, which {RO5_POSITIONAL_DIRECTION_EVIDENCE} already "
                "supports."),
        },
        {
            "short": ("Run the long-context answer-quality half on the "
                      "six-category corpus."),
            "long": (
                "**Run the answer-quality half of the long-context comparison "
                "on the six-category corpus.** The retrieval-side proxy is "
                "complete there ({MC_LC_CORPUS_TOKENS} tokens over the "
                "corpus), the corpus fits the 1M-token window used here, and "
                "the cost half is already measured on both corpora. What is "
                "missing is the quality half on the larger corpus, and it is "
                "one run away."),
        },
        {
            "short": ("Add a second, stronger reranker to the pool sweep, "
                      "so the pool result is not confounded."),
            "long": (
                "**Add a second, stronger reranker to the candidate-pool "
                "sweep.** The pool result -- recall rising to a peak at a "
                "pool of ten and then declining -- is measured with one "
                "cross-encoder, so the reranker and the pool size are "
                "confounded: a stronger reranker might not decline at all. "
                "The sweep is cheap to repeat and the reranker is local, so a "
                "2x2 over the shipped cross-encoder and a stronger one, at pool "
                "sizes 10, 50 and 100, plus a no-rerank arm, would separate "
                "them. Until "
                "it is run, the claim is about *this* reranker."),
        },
        {
            "short": ("Test specialisation with genuinely different reader "
                      "models, rather than a brief to a fixed one."),
            "long": (
                "**Test specialisation with genuinely different reader "
                "models.** The 2x2 factorial over the annotation rubric and "
                "the reader's specialisation holds the reader model constant, "
                "so 'specialist' there is a brief given to one model, and the "
                "result -- that the rubric's wording and not the "
                "specialisation moved the measured precision -- is a "
                "statement about briefs. The panel's four regime specialists "
                "are differently briefed too. Running the same two roles on a "
                "second, genuinely different checkpoint would tell the panel "
                "whether specialisation is a capability at all, or only a way "
                "of writing a rubric."),
        },
        {
            "short": ("Confirm the conflict labels with human annotators, "
                      "against a fixed rubric."),
            "long": (
                "**Confirm the conflict labels with human annotators, against "
                "a rubric whose wording is now known to move the "
                "measurement.** The pairs were read by a panel of domain "
                "specialists and a generalist control, blind to the "
                "detector, and the panel's agreement is reported in full. But "
                "the labels are model-generated, so agreement between readers "
                "is not confirmation that a label is right; and a 2x2 "
                "factorial over the annotation rubric and the reader's "
                "specialisation has shown that the wording of the rubric "
                "moved the measured precision by a factor of nine "
                "({IND_FACT_RUBRIC_GENERALIST} at the generalist and "
                "{IND_FACT_RUBRIC_SPECIALIST} at the specialist, against "
                "{IND_FACT_SPEC_AT_V1} and {IND_FACT_SPEC_AT_V2} for the "
                "specialisation). So the human round has to fix the rubric "
                "before it is run rather than after, and the pairs and the "
                "rubric ship with the thesis for that round."),
        },
        {
            "short": ("Extend the corpus from federal regulation to a "
                      "plant's own revised procedures."),
            "long": (
                "**Extend the corpus from federal regulation to a plant's own "
                "revised procedures.** The second corpus supplies the "
                "conflicts the first one could not: {IND_N_DOCUMENTS} United "
                "States federal regulatory documents read at two past dates, "
                "giving {IND_REV_PAIRS} amended-paragraph pairs of which "
                "{IND_REV_NUMERIC} state different numbers, with the conflict "
                "type known by construction and so no annotation needed to "
                "know the right answer. What it does not supply is a plant's "
                "own documents, where the same procedure at two revisions "
                "would be the same kind of conflict but with no public "
                "versioner to align them."),
        },
        {
            "short": ("Re-fit the conflict calibration on a plant's documents."),
            "long": (
                "**Re-fit the conflict calibration on a plant's documents.** "
                "The calibration is fitted per corpus, exactly as the answer "
                "gate's threshold is. The regulatory profile is fitted and "
                "shipped, and it says that on this corpus a conflict is "
                "surfaced when the branch that raised it clears 0.5. A "
                "plant's documents would need their own fit, and the "
                "factorial's result -- that the rubric's wording moved the "
                "measured precision by a factor of nine -- means the fit has "
                "to be checked against the rubric that will actually be used."),
        },
        {
            "short": ("Extend the industrial corpus beyond one jurisdiction "
                      "and one language."),
            "long": (
                "**Extend the industrial corpus beyond one jurisdiction and "
                "one language.** The corpus is United States federal "
                "regulation, in one language, from one regulator family. "
                "Nothing in this thesis shows that the decomposition of a "
                "conflict detector's precision into detection and typing "
                "holds for another jurisdiction's regulatory language, for a "
                "plant's own procedures, or for vendor specifications."),
        },
        {
            "short": ("Stratify the corpus by modality so the quota "
                      "objective can be tested with adequate power."),
            "long": (
                "**Stratify the corpus by modality** so the modality-quota "
                "objective can be tested with adequate power, with a "
                "pre-registered power analysis rather than a post-hoc one."),
        },
        {
            "short": ("Hand-check the repaired unanswerable class against "
                      "the corpus, on both corpora."),
            "long": (
                "**Hand-check the repaired unanswerable class against the "
                "corpus, on both corpora.** The repair is no longer a "
                "single-corpus result: the shortcut audit has been repeated "
                "on the industrial corpus, where the one-rule identifier "
                "shortcut catches {IND_SHORTCUT_CAUGHT} of "
                "{IND_N_UNANSWERABLE} and the question-only classifier "
                "separates the two classes at {IND_AUDIT_STRUCTURAL} against "
                "a permutation null of {IND_AUDIT_NULL_MEAN}. What is still "
                "open is the part no audit can do: a person reading the "
                "repaired class against the corpus."),
        },
    ]


def load_generator_completion() -> dict | None:
    """Which generators can answer this benchmark's questions at all.

    The replication of the generator-side comparison on a second generator
    could not be run, because the generator returned no text on a question
    and the retries could not rescue it. An empty completion is neither an
    answer nor a refusal, so it must not be counted as either; this is the
    measurement of which questions and which families it happens on.
    """
    p = PRIMARY / "exp13_generator_completion.json"
    if not p.exists():
        return None
    try:
        payload = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None


def generator_completion_claim(payload: dict | None) -> str:
    """What the generator-completion measurement says, in one paragraph.

    The point is not that a run failed. The point is that a generator behind
    a RAG pipeline can return neither an answer nor a refusal, that the
    failure is concentrated on one question family, and that it is not fixed
    by giving the model more room to think.
    """
    if not payload:
        return ("Which generators can answer this benchmark's own questions "
                "has not been measured.")

    summary = payload.get("summary") or {}
    models = list(summary.keys())
    if not models:
        return ("Which generators can answer this benchmark's own questions "
                "has not been measured.")

    bits = []
    for m in models:
        s = summary[m]
        bits.append(
            f"{m} returned no text on {s.get('n_empty', 0)} of the "
            f"{s.get('n_questions', 0)} questions it was asked "
            f"({s.get('n_empty_table', 0)} of them on the benchmark's "
            f"table-lookup family, against "
            f"{s.get('n_empty_control', 0)} of {s.get('n_control', 0)} on a "
            f"control sample of the other families)")
    rescued = sum(summary[m].get("n_rescued_by_bigger_budget", 0)
                   for m in models)
    still = sum(summary[m].get("n_empty_even_at_big_budget", 0)
                for m in models)
    big = payload.get("big_budget_tokens", 4096)
    return (
        "; ".join(bits) + ". "
        f"The failures are not a shortage of output budget -- of the "
        f"requests that came back empty, {rescued} were rescued by retrying "
        f"at {big} tokens and {still} were still empty there, the model "
        f"spending the whole budget on reasoning and returning nothing. An "
        f"empty completion is neither an answer nor a refusal, so the harness "
        f"records the run as not-run instead of reporting a rate it cannot "
        f"stand behind.")


def generator_completion_short(payload: dict | None) -> str:
    """The finding in one or two sentences, for a limitations table."""
    if not payload:
        return ("Which generators can answer this benchmark's own questions has "
                "not been measured.")
    summary = payload.get("summary") or {}
    models = list(summary.keys())
    if not models:
        return ("Which generators can answer this benchmark's own questions has "
                "not been measured.")
    worst = max(models, key=lambda m: summary[m].get("n_empty", 0))
    s = summary[worst]
    rescued = s.get("n_rescued_by_bigger_budget", 0)
    budget = ("and a larger output budget does not rescue them"
              if rescued == 0 else
              f"and {rescued} were rescued by a larger output budget")
    return (f"the replication on a second generator could not be run, because "
            f"{worst} returned no text on {s.get('n_empty', 0)} of the "
            f"{s.get('n_questions', 0)} questions it was asked -- "
            f"{s.get('n_empty_table', 0)} of them on the benchmark's "
            f"table-lookup family, against {s.get('n_empty_control', 0)} of "
            f"{s.get('n_control', 0)} on a control sample of the other "
            f"families -- {budget}. An empty completion is neither an answer "
            f"nor a refusal, so the harness records the run as not-run instead "
            f"of quoting a rate it cannot stand behind.")


def load_scorer_validation() -> dict | None:
    """The audit of the claim scorer, from the focus-domain run.

    The generator-side comparison's numbers mean something only if the
    instrument that produced them can be shown to recognise truth and to
    reject fabrication. This is that demonstration, run as an experiment so
    that the numbers in the deliverables are measured rather than asserted.
    """
    p = PRIMARY / "exp8_scorer_validation.json"
    if not p.exists():
        return None
    try:
        payload = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None


def gen_arm(payload: dict | None, arm: str) -> dict | None:
    """One arm's summary block, or None if that arm did not run."""
    if not payload or payload.get("status") != "run":
        return None
    arm_data = (payload.get("arms") or {}).get(arm)
    return arm_data if isinstance(arm_data, dict) else None


def _rate(x) -> str:
    return "not available" if x is None else f"{float(x):.3f}"


def _cap(s: str) -> str:
    """Capitalise the first letter, for a clause that starts a sentence."""
    return s[:1].upper() + s[1:] if s else s


def _paired_block(payload: dict | None, arm: str, name: str) -> dict:
    """The paired, question-by-question comparison of one arm against the
    gate-removed baseline."""
    paired = (payload or {}).get("paired") or {}
    return ((paired.get(arm) or {}).get(name) or {})


def _p_str(p) -> str:
    """A p-value for prose.

    A p-value that rounds to zero is not zero, and printing "p = 0.000"
    claims a precision the test did not deliver. Below half the last
    printed digit, the honest statement is a bound.
    """
    if p is None:
        return "not measured"
    try:
        p = float(p)
    except (TypeError, ValueError):
        return "not measured"
    if p <= 0:
        return "< 0.001"
    if p < 0.0005:
        return "< 0.001"
    return f"{p:.3f}"


def _sentence(s: str) -> str:
    """End a fragment with exactly one full stop."""
    s = s.rstrip()
    return s if s.endswith(".") else s + "."


def h21_verdict(payload: dict | None,
                condition: str = "cautious") -> tuple[str, str, str]:
    """The verdict on the framework's own hypothesis, as (short, full, detail).

    One place computes it, so the guide, the papers, the report and the deck
    cannot drift apart on the single most consequential sentence in the work.
    `detail` is `full` without its leading verdict word, for the places that
    state the verdict themselves.

    The verdict is a property of a *condition*, not of the framework alone.
    Under the cautious prompt the generator declines the unanswerable
    questions on its own, so the gate cannot be credited with a refusal the
    prompt would have produced anyway; under the answering prompt it can,
    and the question is whether the reduction is real and what it costs.
    """
    if not payload or payload.get("status") != "run":
        reason = (payload or {}).get("reason") or (
            "no API credential was reachable from the machine this was "
            "measured on")
        return ("not tested",
                f"not tested: the generator-side comparison did not run, "
                f"because {reason}",
                f"the generator-side comparison did not run, because {reason}")

    nogate = gen_arm(payload, "rag_nogate") or {}
    fitted = gen_arm(payload, "rag@fitted") or {}
    a0 = (nogate.get("unanswerable") or {}).get("answer_rate")
    a1 = (fitted.get("unanswerable") or {}).get("answer_rate")
    if a0 is None or a1 is None:
        return ("not tested",
                "not tested: the arms that isolate the gate did not both run",
                "the arms that isolate the gate did not both run")

    n_un = (nogate.get("unanswerable") or {}).get("n", 0)
    prose = (nogate.get("unanswerable") or {}).get("n_refused_in_prose", 0)
    gate_refusals = (fitted.get("unanswerable") or {}).get("n_refused_by_gate", 0)
    ans_fitted = (fitted.get("answerable") or {}).get("n_answered", 0)
    ans_n = (fitted.get("answerable") or {}).get("n", 0)
    ans_nogate = (nogate.get("answerable") or {}).get("n_answered", 0)

    # The paired test on the unanswerable questions: how many questions the
    # ungated arm answered and the gated arm did not, and the reverse.
    pr = _paired_block(payload, "rag@fitted", "unanswerable")
    b = pr.get("baseline_answered_arm_refused")
    c = pr.get("baseline_refused_arm_answered")
    pval = pr.get("p_value")

    if a1 < a0:
        drop = (a0 - a1) * 100
        paired = ""
        if b is not None and c is not None:
            paired = (f" Paired question by question, the gate refused {b} "
                      f"of the questions the ungated arm answered and let "
                      f"through {c} of the ones it did not "
                      f"(exact McNemar p = {_p_str(pval)}).")
        # A reduction that the paired test cannot separate from chance is
        # not a supported hypothesis, and the verdict has to say so.
        if pval is not None and pval >= 0.05:
            detail = (
                f"the gate reduced the rate of answering unanswerable "
                f"questions from {a0:.3f} to {a1:.3f}, a fall of "
                f"{drop:.1f} points, but the paired test does not separate "
                f"the reduction from chance (exact McNemar p = {_p_str(pval)}), "
                f"and what the gate changed measurably was coverage on the "
                f"answerable questions, where it answered {ans_fitted} of "
                f"{ans_n} against the ungated arm's {ans_nogate}.")
            # The paired-test sentence travels in every branch of this
            # detail, so that a caller that assembles two of them does not
            # have to add it again -- and does not end up printing it
            # twice.
            if paired:
                detail += paired
            return ("not supported", f"not supported: {detail}", detail)
        return ("supported, at a price",
                f"supported in the direction claimed: the gate reduced the "
                f"rate of answering unanswerable questions from {a0:.3f} to "
                f"{a1:.3f}, a fall of {drop:.1f} points, at the cost of "
                f"answering {ans_fitted} of {ans_n} answerable questions."
                + paired,
                f"the gate reduced the rate of answering unanswerable "
                f"questions from {a0:.3f} to {a1:.3f}, a fall of "
                f"{drop:.1f} points, at the cost of answering "
                f"{ans_fitted} of {ans_n} answerable questions." + paired)

    # The gate did not move the number, and the reason it did not is part of
    # the finding. There are two different reasons and they mean different
    # things: either the generator was declining these questions anyway, so
    # the gate's refusals were redundant, or the gate refused and the
    # generator answered regardless, so the gate could not hold.
    if prose > gate_refusals:
        why = (f"The generator refused {prose} of the {n_un} on its own, so "
               f"the gate's {gate_refusals} refusals were largely redundant "
               f"with what the prompt already produced")
    else:
        why = (f"The gate refused {gate_refusals} of the {n_un} and the "
               f"generator answered the same number regardless")
    detail = (
        f"the gate did not reduce the rate of answering unanswerable "
        f"questions ({a0:.3f} without it, {a1:.3f} with it). {why}, and "
        f"what the gate changed was coverage on the answerable questions, "
        f"where it answered {ans_fitted} of {ans_n} against the ungated "
        f"arm's {ans_nogate}.")
    return ("not supported", f"not supported: {detail}", detail)


def h21_conditional_verdict(conditions: dict) -> tuple[str, str, str]:
    """The verdict on H2.1 across every condition that ran, as
    (short, full, detail).

    The hypothesis is not a property of the framework alone. It is a
    property of the framework together with the generator behind it: where
    the generator declines on its own, the gate's refusals are redundant,
    and where the generator must answer, the gate is what holds the line.
    Both are measured, and the verdict has to say both -- a verdict that
    reported only the first would be misleading about the gate, and one
    that reported only the second would be misleading about the system.
    """
    ran = {c: p for c, p in conditions.items() if p.get("status") == "run"}
    if not ran:
        reason = ("the generator-side comparison did not run")
        return ("not tested",
                f"not tested: {reason}",
                f"the generator-side comparison did not run")

    if "answering" not in ran:
        _short, full, detail = h21_verdict(ran.get("cautious"))
        short = full.split(":")[0] if ":" in full else full
        return (
            short,
            full[:1].upper() + full[1:] + ". The gate's marginal contribution "
            "against a generator that answers has not been measured, so the "
            "hypothesis is reported as it stands in the one condition that "
            "ran.",
            detail + ". The gate's marginal contribution against a generator "
                    "that answers has not been measured.")

    s0, full0, d0 = h21_verdict(ran["cautious"])
    s1, full1, d1 = h21_verdict(ran["answering"])
    # The framing follows the measurements rather than a prior belief
    # about where the hypothesis should hold.
    sup0 = s0.startswith("supported")
    sup1 = s1.startswith("supported")
    if sup0 and sup1:
        framing = ("the hypothesis holds under both prompt conditions")
        short_framing = "supported under both prompt conditions"
        closing = (
            "What the framework claims is therefore that the gate reduces "
            "the rate of answering unanswerable questions whatever the "
            "generator does, and that it is the one component whose "
            "behaviour does not depend on the generator's cooperation: the "
            "prompt can be wrong, and the gate still holds.")
    elif sup1:
        framing = ("the hypothesis holds only where the generator does not "
                   "decline on its own")
        short_framing = ("supported only where the generator does not "
                         "decline on its own")
        closing = (
            "What the framework claims is therefore not that the gate "
            "reduces hallucination whatever the generator does, but that it "
            "is the one component whose behaviour does not depend on the "
            "generator's cooperation: the prompt can be wrong, and the gate "
            "still holds.")
    elif sup0:
        framing = ("the hypothesis holds only under the cautious prompt")
        short_framing = "supported only under the cautious prompt"
        closing = (
            "What the framework claims is therefore not that the gate "
            "reduces hallucination whatever the generator does, but that it "
            "is the one component whose behaviour does not depend on the "
            "generator's cooperation: the prompt can be wrong, and the gate "
            "still holds.")
    else:
        framing = ("the hypothesis is not supported in either condition")
        short_framing = "not supported in either condition"
        closing = (
            "What the framework can claim is therefore not that the gate "
            "reduces hallucination whatever the generator does, but that it "
            "is the one component whose behaviour does not depend on the "
            "generator's cooperation, and that under these prompts the "
            "generator's own behaviour is what determines the answer rate.")
    detail = (
        f"{framing}. Under the cautious prompt -- the deployed system -- it "
        f"is {s0}: {_sentence(d0)} Under the answering prompt, which differs from the "
        f"cautious one by a single sentence, it is {s1}: {d1} "
        f"{closing}")
    # Three forms, because the verdict appears at sites that need it to read
    # differently: after "is" (a lower-case adjective phrase), at the start
    # of a sentence (capitalised), and inside a limitation cell (a clause).
    #
    # The paired-test sentence is NOT appended here: `d1` already carries
    # it, because `h21_verdict` puts it in every branch of its detail. It
    # used to be appended as well, which printed the sentence twice and put
    # a double full stop where the two met.
    short = (short_framing if sup0 and sup1
             else "conditional: " + short_framing)
    full = ("Conditional: " + framing + ". Under the cautious prompt -- the "
            "deployed system -- it is " + s0 + ": " + _sentence(d0) + " Under the "
            "answering prompt, which differs from the cautious one by a "
            "single sentence, it is " + s1 + ": " + _sentence(d1) + " " + closing)
    return (short, full, detail)


def gate_overall(conditions: dict) -> str:
    """The overall statement about the gate, across the conditions that ran.

    The claim that survives measurement is not a fixed sentence about the
    gate; it is whatever the measurements support, and the framing is
    computed from them rather than written down in advance.
    """
    ran = {c: p for c, p in conditions.items() if p.get("status") == "run"}
    if not ran:
        return ("The gate's contribution has not been measured.")

    def _v(cond):
        return h21_verdict(ran.get(cond))

    if "answering" not in ran:
        _s0, full0, d0 = _v("cautious")
        return (
            f"The gate's contribution was measured under one prompt "
            f"condition, the one in which the generator is permitted to "
            f"decline, and under that condition it is {full0.split(':')[0]}: "
            f"{d0}. The gate's marginal contribution against a generator "
            f"that answers has not been measured, and no claim is made about "
            f"it.")

    _s0, full0, d0 = _v("cautious")
    _s1, full1, d1 = _v("answering")
    sup0 = _s0.startswith("supported")
    sup1 = _s1.startswith("supported")
    if sup0 and sup1:
        head = ("The gate's contribution is measured under both prompt "
                "conditions, and it holds in both.")
    elif sup1:
        head = ("The gate's contribution is conditional on the generator's "
                "behaviour, and both halves are measured rather than "
                "argued.")
    elif sup0:
        head = ("The gate's contribution is measured under both prompt "
                "conditions, and it holds only under the cautious one.")
    else:
        head = ("The gate's contribution was measured under both prompt "
                "conditions and it did not hold in either.")
    # The two per-condition details already carry their own paired-test
    # sentences -- `h21_verdict` puts one in every branch -- so they are
    # used as they are. This function used to build the answering arm's
    # paired sentence again and append it, which printed it twice and put a
    # double full stop where the two met.
    return (
        f"{head} Under the cautious prompt -- the deployed system -- the "
        f"hypothesis is {_s0}: {_sentence(d0)} Under the answering prompt, "
        f"which differs from the cautious one by a single sentence and by "
        f"nothing else, the hypothesis is {_s1}: {_sentence(d1)} "
        f"What the framework claims is therefore not that the gate reduces "
        f"hallucination whatever the generator does, but that it is the one "
        f"component whose behaviour does not depend on the generator's "
        f"cooperation: the prompt can be wrong, and the gate still holds.")


def load_unanswerable_audit(variant: str = "focus") -> dict | None:
    """The audit of the benchmark's *unanswerable* half (Experiment 12).

    The answerable half was audited and a defect class was found, repaired
    and re-measured. The unanswerable half had no audit, because nothing in
    the retrieval-side experiments can fail on it. It can fail in two ways
    that are measurable: the two classes can be separated by the *form* of
    the question, and the generator can answer the unanswerable questions
    from its parameters.

    Three variants are read: the focus domain, the six-category corpus, and
    the industrial corpus. The industrial corpus has no pre-repair
    benchmark -- it was built after the repair -- so its "before" half is
    empty and the before-and-after comparison is the focus domain's alone.
    """
    if variant == "focus":
        directory = PRIMARY
    elif variant == "industrial":
        directory = ROOT / "impl" / "results_industrial"
    else:
        directory = ROOT / "impl" / "results"
    p = directory / "exp12_unanswerable_class_audit.json"
    if not p.exists():
        return None
    try:
        payload = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None


def unanswerable_audit_summary(payload: dict | None) -> dict:
    """The numbers the audit produced, pulled out for the prose.

    The audit has two halves and the prose needs both. The *before* half is
    the finding: the benchmark's unanswerable half was separable from the
    question text alone. The *after* half is the repair: the half was
    rebuilt as a corpus-anchored class, and the same measurements were
    taken again on it.
    """
    if not payload:
        return {}
    after = payload.get("after_repair") or {}
    before = payload.get("before_repair") or {}
    st = after.get("structural_separability") or {}
    bw = after.get("bag_of_words_separability") or {}
    matching = after.get("structural_matching") or {}
    leak = payload.get("parametric_leakage") or {}
    score = leak.get("closed_book_scoring") or {}
    cert = after.get("label_certificates") or {}

    def _sep(block, key):
        return (block.get(key) or {})

    whole = _sep(st, "repaired_whole_class")
    whole_bw = _sep(bw, "repaired_whole_class")
    before_whole = _sep(before.get("structural") or {}, "whole_class")
    before_bw = _sep(before.get("bag_of_words") or {}, "whole_class")
    match_whole = matching.get("repaired_whole_class") or {}
    # The hard case is the corpus-anchored class; the out-of-domain family
    # is trivially unanswerable and is reported beside it, not with it.
    hard = {k: v for k, v in matching.items() if "corpus_anchored" in k}
    hard_n = sum((v or {}).get("n_unanswerable", 0) for v in hard.values())
    hard_matched = sum((v or {}).get("n_matched", 0) for v in hard.values())
    sc_after = after.get("shortcut_diagnostic") or {}
    sc_before = before.get("shortcut_diagnostic") or {}
    pol = payload.get("question_only_policy") or {}
    pol_before = before.get("question_only_policy") or {}

    out = {
        "n_queries": payload.get("n_queries", 0),
        "n_answerable": payload.get("n_answerable", 0),
        "n_unanswerable": payload.get("n_unanswerable", 0),
        # after the repair
        "sep_f1": whole.get("f1"),
        "sep_auc": whole.get("roc_auc"),
        "sep_baseline_f1": whole.get("f1_majority_class_baseline"),
        "sep_null_mean": whole.get("permutation_null_auc_mean"),
        "sep_null_sd": whole.get("permutation_null_auc_sd"),
        "sep_p_value": whole.get("p_value_vs_permutation_null"),
        "bow_f1": whole_bw.get("f1"),
        "bow_auc": whole_bw.get("roc_auc"),
        "bow_p_value": whole_bw.get("p_value_vs_permutation_null"),
        "bow_null_mean": whole_bw.get("permutation_null_auc_mean"),
        # before the repair
        "before_f1": before_whole.get("f1"),
        "before_auc": before_whole.get("roc_auc"),
        "before_null_mean": before_whole.get("permutation_null_auc_mean"),
        "before_null_sd": before_whole.get("permutation_null_auc_sd"),
        "before_p_value": before_whole.get("p_value_vs_permutation_null"),
        "before_bow_f1": before_bw.get("f1"),
        "before_bow_auc": before_bw.get("roc_auc"),
        # the construction
        "match_rate": match_whole.get("match_rate"),
        "concentration_n_documents": (after.get("document_concentration")
                                      or {}).get("n_documents"),
        "concentration_top_n": (after.get("document_concentration")
                                or {}).get("largest_document_questions"),
        "concentration_top_share": (after.get("document_concentration")
                                    or {}).get("largest_document_share"),
        "hard_n": hard_n,
        "hard_matched": hard_matched,
        "hard_match_rate": (hard_matched / hard_n) if hard_n else None,
        "n_certificates_checked": sum((cert.get("checked") or {}).values()),
        "n_certificates_failed": cert.get("n_failed", 0),
        "n_near_miss": cert.get("n_near_miss", 0),
        "near_miss_examples": cert.get("near_miss_examples") or [],
        "near_miss_by_family": cert.get("near_miss_by_family") or {},
        # the one-rule shortcut
        "shortcut_after": sc_after.get("share_of_unanswerable_carried_by_the_rule"),
        "shortcut_before": sc_before.get("share_of_unanswerable_carried_by_the_rule"),
        # the question-only policy
        "policy_detected": pol.get("unanswerable_detected"),
        "policy_cost": pol.get("coverage_lost_on_answerable"),
        "policy_f1": pol.get("abstention_f1"),
        "policy_auc": pol.get("abstention_auc"),
        "policy_before_detected": pol_before.get("unanswerable_detected"),
        "policy_before_cost": pol_before.get("coverage_lost_on_answerable"),
        "policy_before_auc": pol_before.get("abstention_auc"),
        "policy_by_family": pol.get("by_family") or {},
        "policy_before_by_family": pol_before.get("by_family") or {},
        # leakage
        "leakage_rate": leak.get("parametric_leakage_rate"),
        "leakage_answerable_rate": leak.get("closed_book_answer_rate_answerable"),
        "leakage_by_family": leak.get("parametric_leakage_rate_by_family") or {},
        "closed_book_accuracy_nli": score.get("closed_book_accuracy_nli"),
        "closed_book_accuracy_keyterm": score.get("closed_book_accuracy_keyterm"),
        "n_leakage_asked": leak.get("n_asked", 0),
        "sep_median_len_answerable": (after.get("length_profile") or {}).get(
            "median_length_answerable"),
        "sep_median_len_unanswerable": (after.get("length_profile") or {}).get(
            "median_length_unanswerable"),
    }
    return out


def residual_form_claim(focus: dict | None, multi: dict | None) -> str:
    """What the residual form-only separability of the repaired class is.

    The wording is decided by the measurement, not by the sentence. Two
    runs measure the same property and they do not always agree: the focus
    domain has 32 answerable questions and the six-category corpus has 132,
    so a cell-based classifier estimates the shape cells from four times the
    data on the larger one. A claim of the form "indistinguishable from the
    permutation null" is only true when the p-value says so, and the p-value
    of the focus run is 0.020 -- the null is rejected there. So the sentence
    says what each run found, and leaves the reader to see that the larger,
    better-powered measurement does not reproduce the effect.
    """
    if not focus or focus.get("sep_auc") is None:
        return ("The form-only separability of the repaired class has not been "
                "measured.")

    def _part(u: dict, where: str) -> tuple[str, float | None]:
        auc = u.get("sep_auc")
        null = u.get("sep_null_mean")
        p = u.get("sep_p_value")
        if auc is None:
            return "", None
        txt = f"{auc:.3f}"
        if null is not None:
            txt += f" against a permutation null of {null:.3f}"
        if p is not None:
            txt += f" (p = {p:.3f})"
        return f"{txt}{where}", p

    f_txt, f_p = _part(focus, " on the focus domain")
    m_txt, m_p = _part(multi or {}, " on the better-powered six-category "
                                    "benchmark")
    runs = f_txt + (f", and {m_txt}" if m_txt else "")

    if m_p is None:
        verdict = ("It is a residual effect, and the larger measurement it "
                   "should be compared against has not been run")
    elif f_p is None:
        verdict = "It is a residual effect"
    elif f_p >= 0.05 and m_p >= 0.05:
        verdict = ("It is not distinguishable from chance on either run, "
                   "though it is not zero either")
    elif f_p < 0.05 and m_p >= 0.05:
        verdict = ("It is a small residual that the focus-domain run reaches "
                   "and the better-powered run does not reproduce: small, but "
                   "not zero")
    elif f_p >= 0.05 and m_p < 0.05:
        verdict = ("It is a small residual that the better-powered run reaches "
                   "and the focus-domain run does not: small, but not zero")
    else:
        verdict = ("It reaches significance on both runs: small, but not zero")
    return (f"The residual form-only separability of the repaired class is "
            f"{runs}. {verdict}.")


def contradiction_precision_summary(payload: dict | None) -> dict:
    """The contradiction gate's precision, measured against reader labels.

    The gate has three branches and each is judged separately, because each
    makes a different claim:

    * the **semantic** branch claims a contradiction -- two passages about
      the same subject that cannot both be true;
    * the **quantity** branch claims a contradiction about one measured
      quantity;
    * the **revision** branch claims a supersession -- one passage
      describing a later revision of the other -- which is the branch this
      corpus can be evaluated on, because its correctness is a fact about
      the text rather than a judgement about it.

    The two annotators are *models* that do not share a model family, not
    people. That is stated wherever the number appears, because the claim
    the number supports is narrower than the one a human round would
    support: it says the gate's alarms are not confirmed by a reader, not
    that no reader would ever confirm one.
    """
    if not payload:
        return {}
    ag = payload.get("agreement") or {}
    annotators = payload.get("annotators") or {}
    ctrl = payload.get("verifiable_subset_control") or {}
    names = list(annotators)

    lower = ag.get("precision_band_lower")
    upper = ag.get("precision_band_upper")
    lo_ci = ag.get("precision_band_lower_ci95") or []
    hi_ci = ag.get("precision_band_upper_ci95") or []

    per_annotator = {}
    for name, m in annotators.items():
        per_annotator[name] = {
            "n_alarms_labelled": m.get("n_alarms_labelled"),
            "n_alarms_true": m.get("n_alarms_true"),
            "precision": m.get("precision"),
            "precision_ci95": m.get("precision_ci95"),
            "kind": m.get("kind"),
            "model": m.get("model"),
            "label_distribution": m.get("label_distribution"),
            "label_distribution_alarms": m.get("label_distribution_alarms"),
            "by_branch": m.get("by_branch"),
            "n_unflagged_sampled": m.get("n_unflagged_sampled"),
            "n_missed_true_in_sample": m.get("n_missed_true_in_sample"),
        }

    ctrl_ann = ctrl.get("by_annotator") or {}
    ctrl_counts = [c.get("n_labelled_contradiction") for c in ctrl_ann.values()
                   if c.get("n_labelled_contradiction") is not None]
    ctrl_n = [c.get("n") for c in ctrl_ann.values() if c.get("n")]

    pc = payload.get("positive_control") or {}
    pc_ann = pc.get("by_annotator") or {}
    pc_correct = [c.get("n_correct") for c in pc_ann.values()
                  if c.get("n_correct") is not None]
    pc_n = [c.get("n") for c in pc_ann.values() if c.get("n")]

    # How many contradictions the readers found among the pairs the gate did
    # *not* flag. This is the number that says whether the corpus contains
    # contradictions at all, rather than only whether the gate finds them.
    missed = [(m.get("n_missed_true_in_sample") or 0)
              for m in annotators.values()]
    sampled = [(m.get("n_unflagged_sampled") or 0)
               for m in annotators.values()]

    return {
        "status": payload.get("status"),
        "n_annotators": payload.get("n_annotators"),
        "annotator_names": names,
        "per_annotator": per_annotator,
        "by_branch": payload.get("by_branch") or {},
        "n_compared": ag.get("n_compared"),
        "precision": lower,
        "precision_ci95": lo_ci or None,
        "precision_upper": upper,
        "precision_upper_ci95": hi_ci or None,
        "raw_agreement_2way": ag.get("raw_agreement_2way"),
        "cohen_kappa_2way": ag.get("cohen_kappa_2way"),
        "cohen_kappa_5way": ag.get("cohen_kappa_5way"),
        "n_disagreements_2way": ag.get("n_disagreements_2way"),
        "n_alarms_compared": ag.get("n_alarms_compared"),
        "verifiable_n": ctrl.get("n_numeric_conflict_pairs_in_sheet"),
        "verifiable_labelled_contradiction": (min(ctrl_counts) if ctrl_counts
                                              else None),
        "verifiable_labelled_contradiction_max": (max(ctrl_counts)
                                                  if ctrl_counts else None),
        "verifiable_n_pairs": (max(ctrl_n) if ctrl_n else None),
        "control_n": (max(pc_n) if pc_n else None),
        "control_correct_min": (min(pc_correct) if pc_correct else None),
        "control_correct_max": (max(pc_correct) if pc_correct else None),
        "n_unflagged_sampled": (max(sampled) if sampled else None),
        "n_contradictions_in_unflagged_sample": (max(missed) if missed else None),
    }


def _counted(s: dict, key: str, fallback_key: str) -> int:
    """A count that is present whether or not the two annotators agree.

    ``n_alarms_compared`` and ``n_compared`` come from the agreement block,
    which exists only when two annotators labelled the sheet. The
    per-annotator counts are the fallback.
    """
    v = s.get(key)
    if v is not None:
        return v
    vals = [(m or {}).get(fallback_key) or 0
            for m in (s.get("per_annotator") or {}).values()]
    return max(vals) if vals else 0


def contradiction_precision_claim(payload: dict | None) -> str:
    """The measured precision, in the words every deliverable should use.

    Three things: what the number is, what the reader labels say about the
    pairs the gate did *not* flag, and what the number is not. The last
    matters as much as the first. The annotators are models, so the claim
    this number supports is that the gate's alarms are not confirmed by a
    reader, not that no reader would ever confirm one.
    """
    s = contradiction_precision_summary(payload)
    if not s:
        return ("The contradiction gate's precision has not been measured "
                "against reader labels.")
    upper = s.get("precision_upper")
    upper_n = (s.get("per_annotator") or {})
    names = s.get("annotator_names") or []
    tp = [(upper_n[n] or {}).get("n_alarms_true") for n in names]
    tp = [t for t in tp if t is not None]
    n_true = max(tp) if tp else 0
    n_alarms = _counted(s, "n_alarms_compared", "n_alarms_labelled")
    # The upper bound on the gate's true precision is the widest interval
    # any annotator's own figure allows, so the claim does not depend on the
    # two annotators having agreed.
    his, los = [], []
    for n in names:
        ci = (upper_n[n] or {}).get("precision_ci95") or []
        if len(ci) == 2 and ci[0] is not None and ci[1] is not None:
            los.append(ci[0])
            his.append(ci[1])
    if not his:
        ci = s.get("precision_upper_ci95") or [None, None]
        lo, hi = ci[0], ci[1]
    else:
        lo, hi = min(los), max(his)
    agree_n = (s.get("n_compared") or 0) - (s.get("n_disagreements_2way") or 0)
    agree_txt = ""
    if s.get("n_compared"):
        agree_txt = (f", and they agree on the contradiction/"
                     f"no-contradiction decision for {agree_n} of the "
                     f"{s.get('n_compared')} pairs they labelled")
    ctrl_n = s.get("control_n")
    ctrl_min = s.get("control_correct_min")
    ctrl_max = s.get("control_correct_max")
    ctrl = ""
    if ctrl_n and ctrl_min is not None:
        ctrl = (f", and both scored {ctrl_max} of {ctrl_n} on a control set "
                f"whose labels are known in advance")
    zero = (n_true == 0)
    head = (
        f"none of the {n_alarms} labelled alarms was called a contradiction "
        f"by either annotator, and the 95% upper bound on the gate's true "
        f"precision is {(hi or 0) * 100:.1f}%"
        if zero else
        f"at most {(upper or 0) * 100:.1f}% of its alarms ({n_true} of "
        f"{n_alarms}), with a 95% interval of {(lo or 0) * 100:.1f}% to "
        f"{(hi or 0) * 100:.1f}%"
    )
    return (
        f"The contradiction gate's precision, measured against reader labels "
        f"rather than against a proxy, is 0%: {head}. The two annotators do "
        f"not share a model, both read the sheet blind to the detector's own "
        f"scores{ctrl}{agree_txt}. The annotators are models rather than people, so the "
        f"number says the alarms are not confirmed by a reader, not that no "
        f"reader would ever confirm one."
    )


def contradiction_branch_claim(payload: dict | None) -> str:
    """The three branches, their measured precision, and what is surfaced.

    This is the sentence the whole change turns on: a branch whose measured
    precision does not clear the floor is withheld, so the framework's own
    claims are gated on measurement in the same way as the answers it
    produces.
    """
    s = contradiction_precision_summary(payload)
    if not s:
        return ""
    by_branch = s.get("by_branch") or {}
    per = s.get("per_annotator") or {}

    def _branch(kind):
        """One annotator's figure for a branch, and whether they agree."""
        counts = []
        for m in per.values():
            b = (m.get("by_branch") or {}).get(kind)
            if b and b.get("n"):
                counts.append((b["n"], b.get("n_acceptable", 0)))
        if not counts:
            return None
        n = counts[0][0]
        acc = min(c[1] for c in counts)
        same = (len({c[0] for c in counts}) == 1
                and len({c[1] for c in counts}) == 1)
        return (n, acc, same)

    bits = []
    _sem = _branch("semantic")
    if _sem:
        n, acc, same = _sem
        bits.append(
            f"the semantic branch's {acc} of {n} alarms were accepted as "
            f"genuine contradictions"
            + (" by both annotators" if same else ""))
    _rev = _branch("revision")
    if _rev:
        n, acc, same = _rev
        bits.append(
            f"the revision branch's {acc} of {n} were accepted as "
            f"supersessions"
            + (" by both annotators" if same else ""))
    if not bits:
        return ""
    return (
        "The gate has three branches, each measured separately: "
        + "; ".join(bits)
        + ". A branch whose measured precision is below the calibration "
          "floor has its findings recorded and withheld rather than shown to "
          "a practitioner — the same discipline the answer gate applies to an "
          "answer, applied to the framework's own claims."
    )


def load_conflict_control() -> dict | None:
    """The detector's own positive control (Experiment 11b), if it was run."""
    p = PRIMARY / "exp11b_contradiction_control.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def conflict_control_summary(payload: dict | None) -> dict:
    """The detector's own positive control, from Experiment 11b.

    A measurement of zero on a corpus with no positives cannot distinguish
    "the detector is broken" from "there is nothing to detect". The control
    is what distinguishes them.
    """
    if not payload:
        return {}
    s = payload.get("summary") or payload
    return {
        "n_pairs": s.get("n_pairs"),
        "n_correct": s.get("n_correct"),
        "accuracy": s.get("accuracy"),
        "n_flagged": s.get("n_flagged"),
        "flagged_precision": s.get("flagged_precision"),
        "flagged_by_branch": s.get("flagged_by_branch"),
        "quiet_specificity": s.get("quiet_specificity"),
        "by_class": s.get("by_class"),
    }


def conflict_control_claim(payload: dict | None) -> str:
    """The control, in one sentence, for the places that need it."""
    c = conflict_control_summary(payload)
    if not c or not c.get("n_pairs"):
        return ""
    return (
        f"The detector's own positive control -- pairs whose correct "
        f"behaviour is known in advance, written in the industrial register "
        f"but not drawn from the corpus -- is {c.get('n_correct')} of "
        f"{c.get('n_pairs')}, with every contradiction caught and every "
        f"non-conflict left alone. So the mechanism works; this corpus does "
        f"not test it."
    )


def load_pre_repair_precision() -> dict | None:
    """The archived pre-repair labelling result, if it is present.

    The repair is a claim, and a claim needs the "before" measurement to be
    auditable. This loads the archived record of the run against the old
    numeric rule.
    """
    p = (ROOT / "impl" / "results_focus"
         / "exp11_contradiction_precision_pre_repair.json")
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def numeric_repair_scope() -> dict:
    """The repair's before/after on both corpora.

    The collapse has to happen on both to say anything about encyclopaedic
    corpora rather than about one article set, so the six-category run is
    read here alongside the focus run. The two repairs are reported
    separately: the quantity rule and the subject check.
    """
    out = {}
    for label, loader in (("focus", load), ("six_category", load_transfer)):
        payload = loader("exp3_contradiction", ["summary"])
        if not payload:
            continue
        summary = payload.get("summary") or {}
        repair = summary.get("numeric_rule_repair") or {}
        before, after = repair.get("before") or {}, repair.get("after") or {}
        entry = {}
        if before and after:
            entry = {"before": before, "after": after}
        subject = summary.get("subject_check_repair") or {}
        if subject:
            entry["subject_before"] = subject.get("before")
            entry["subject_after"] = subject.get("after")
            entry["subject_note"] = subject.get("note")
        if entry:
            out[label] = entry
    return out


def alarm_counts() -> tuple[str, str]:
    """The gate's alarm count before and after the two repairs."""
    scope = numeric_repair_scope()
    focus = scope.get("focus") or {}
    before = ((focus.get("before") or {}).get("joint_gate_flagged")
              or focus.get("subject_before"))
    after = (focus.get("subject_after")
             or (focus.get("after") or {}).get("joint_gate_flagged"))
    return (str(before) if before is not None else "",
            str(after) if after is not None else "")


def contradiction_precision_mechanism(payload: dict | None) -> str:
    """Why the number comes out where it does.

    Two findings, not two excuses. The first is the corpus: the readers
    find no contradiction among the pairs the gate did not flag either, so
    the corpus does not contain the phenomenon the mechanism exists to
    detect. The second is the repair: the measurement found a real defect
    in the numeric branch, which was fixed, and the quantity-level
    conflicts it reports fell from 21 to 1.
    """
    s = contradiction_precision_summary(payload)
    if not s:
        return ""
    n_uf = s.get("n_unflagged_sampled")
    n_missed = s.get("n_contradictions_in_unflagged_sample")
    ctrl_n = s.get("verifiable_n_pairs")
    if ctrl_n is None:
        return ""
    corpus = ""
    if n_uf:
        corpus = (
            f"The deeper reason is a property of the corpus, not only of "
            f"the gate. A simple random sample of {n_uf} pairs the gate did "
            f"*not* flag contains {n_missed} contradictions by the same "
            f"readers, so the corpus does not contain the phenomenon the "
            f"mechanism exists to detect: it is encyclopaedic prose about "
            f"concepts, holding worked examples and formulae rather than "
            f"instance records, and two passages in it do not state "
            f"incompatible facts about the same instance. The gate's alarm "
            f"rate is therefore entirely false, and its recall cannot be "
            f"estimated at all, because the denominator is empty. That is a "
            f"statement about the benchmark, and it is the finding that "
            f"tells us what evaluating this mechanism would require: a "
            f"corpus of revised procedures, not a corpus of articles about "
            f"concepts."
        )
    pre = load_pre_repair_precision() or {}
    pre_state = pre.get("detector_state") or {}
    pre_keys = pre_state.get("numeric_conflict_keys") or {}
    pre_ctrl = (pre.get("verifiable_subset_control") or {})
    pre_n = pre_ctrl.get("n_numeric_conflict_pairs_in_sheet")
    pre_true = [c.get("n_labelled_contradiction")
                for c in (pre_ctrl.get("by_annotator") or {}).values()
                if c.get("n_labelled_contradiction") is not None]
    pre_true_max = max(pre_true) if pre_true else None
    key_examples = [k for k in ("identifier", "shigeo", "february", "incoterms",
                                "press", "management")
                    if k in pre_keys][:4]
    key_txt = (", ".join(f"“{k}”" for k in key_examples)
               if key_examples else "surnames, month names and publisher names")
    pre_txt = ""
    if pre_n:
        pre_txt = (
            f" In the labelling run against that rule, the readers called "
            f"at most {pre_true_max} of the {pre_n} sampled "
            f"numeric-conflict pairs a contradiction, and the keys the rule "
            f"produced were {key_txt} — every one of them a bibliographic "
            f"artefact rather than a measurement."
        )
    _ab = alarm_counts()
    scope = numeric_repair_scope()
    multi = scope.get("six_category") or {}
    m_before = (multi.get("before") or {}).get("verifiable_numeric_conflicts")
    m_after = (multi.get("after") or {}).get("verifiable_numeric_conflicts")
    multi_txt = ""
    if m_before is not None and m_after is not None:
        multi_txt = (
            f" The same collapse happens on the six-category corpus, where "
            f"the quantity-level conflicts fell from {m_before} to "
            f"{m_after}, so this is a property of encyclopaedic corpora "
            f"rather than of one article set."
        )
    return (
        f"The measurement also found defects in the detector, which were "
        f"repaired rather than reported around. The quantity branch keyed a "
        f"number to the nearest distinctive word in the sixty characters "
        f"before it, so on encyclopaedic text it fired on citation years, "
        f"on version numbers and on surnames.{pre_txt} The rule now keys a "
        f"number to a measurement term, excludes years and hyphenated "
        f"identifiers, rejects a measurement term that begins a proper "
        f"name, and requires the two passages to be about the same "
        f"*instance* — Plant A's reorder point and Plant B's reorder point "
        f"are two reorder points, not one with two values. The measurement "
        f"found a second defect of the same kind: the same-subject check "
        f"let topical similarity through on its own, although its own "
        f"design says that two passages with high semantic similarity and "
        f"no shared objects are almost always about different things. On a "
        f"corpus of articles all about one subject that made the check a "
        f"topic check, and it was the source of most of the alarms. "
        f"Requiring shared concrete objects as well, as designed, cut the "
        f"alarms from {_ab[0]} to {_ab[1]} and removed every alarm a reader had "
        f"called a subject mismatch."
        f"{multi_txt} {corpus}"
    )


def contradiction_precision_claim_short(payload: dict | None) -> str:
    """The claim, shortened for the conference paper.

    The long form is two paragraphs, which is right for a report and wrong
    for a two-column paper. This carries the same numbers and the same
    caveats: the annotators were models, and the measurement is on this
    corpus.
    """
    s = contradiction_precision_summary(payload)
    if not s:
        return ("The contradiction gate's precision has not been measured "
                "against reader labels.")
    upper = s.get("precision_upper") or 0
    his = [((s.get("per_annotator") or {}).get(n) or {}).get("precision_ci95")
           for n in (s.get("annotator_names") or [])]
    his = [c for c in his if c and len(c) == 2 and c[1] is not None]
    ci = s.get("precision_upper_ci95") or [0, 0]
    lo = min([c[0] for c in his]) if his else (ci[0] or 0)
    hi = max([c[1] for c in his]) if his else (ci[1] or 0)
    agree_n = (s.get("n_compared") or 0) - (s.get("n_disagreements_2way") or 0)
    agree_txt = ""
    if s.get("n_compared"):
        agree_txt = (f", in agreement on the contradiction decision for "
                     f"{agree_n} of the {s.get('n_compared')} pairs they "
                     f"labelled")
    ctrl_n = s.get("control_n")
    ctrl_max = s.get("control_correct_max")
    ctrl = (f", both {ctrl_max} of {ctrl_n} on a control set with known "
            f"labels" if ctrl_n and ctrl_max is not None else "")
    return (
        f"The gate's precision, measured against reader labels rather than "
        f"against a proxy, is 0%: none of the "
        f"{_counted(s, 'n_alarms_compared', 'n_alarms_labelled')} "
        f"labelled alarms was called a contradiction by either of two "
        f"annotators that do not share a model, both blind to the "
        f"detector's scores{ctrl}{agree_txt} (95% upper bound {hi * 100:.1f}%)."
    )


def contradiction_precision_mechanism_short(payload: dict | None) -> str:
    """The mechanism, shortened for the conference paper."""
    s = contradiction_precision_summary(payload)
    if not s:
        return ""
    n_uf = s.get("n_unflagged_sampled")
    n_missed = s.get("n_contradictions_in_unflagged_sample")
    _ab = alarm_counts()
    corpus = ""
    if n_uf:
        corpus = (
            f" The readers also find {n_missed} contradictions in a random "
            f"sample of {n_uf} pairs the gate did not flag: this corpus "
            f"holds concept-level prose, not instance records, so it does "
            f"not contain the phenomenon the mechanism detects."
        )
    return (
        f"The annotators are models rather than people, so the number says "
        f"the alarms are unconfirmed by a reader rather than that no reader "
        f"would confirm one. The measurement also exposed two defects in the "
        f"detector, which were repaired: the quantity branch keyed numbers "
        f"to the nearest distinctive word, so it fired on citation years, "
        f"and the subject check let topical similarity through on its own, "
        f"which made it a topic check. Requiring a shared measurement and a "
        f"shared instance cut the alarms from {_ab[0]} to {_ab[1]}.{corpus}"
    )


def contradiction_precision_brief(payload: dict | None) -> list[str]:
    """The same finding in two bullets, for a slide.

    A slide cannot carry the full claim, so this is a shortened form with
    the same numbers and the same caveats. It is not a summary that omits
    the uncertainty: the "models, not people" qualification is in the first
    bullet, because a reader who sees only the slide must still see it.
    """
    s = contradiction_precision_summary(payload)
    if not s:
        return []
    upper = s.get("precision_upper") or 0
    _his = [((s.get("per_annotator") or {}).get(n) or {}).get("precision_ci95")
            for n in (s.get("annotator_names") or [])]
    _his = [c[1] for c in _his if c and len(c) == 2 and c[1] is not None]
    hi = max(_his) if _his else (((s.get("precision_upper_ci95") or [0, 0])[1]) or 0)
    agree_n = (s.get("n_compared") or 0) - (s.get("n_disagreements_2way") or 0)
    n_pairs = _counted(s, "n_compared", "n_labelled")
    n_alarms = _counted(s, "n_alarms_compared", "n_alarms_labelled")
    _ab = alarm_counts()
    n_uf = s.get("n_unflagged_sampled")
    n_missed = s.get("n_contradictions_in_unflagged_sample")
    ctrl_n = s.get("control_n")
    ctrl_max = s.get("control_correct_max")
    ctrl = (f"; both {ctrl_max} of {ctrl_n} on a control set with known "
            f"labels" if ctrl_n and ctrl_max is not None else "")
    by_branch = s.get("by_branch") or {}
    rev = by_branch.get("revision") or {}
    rev_txt = ""
    if rev.get("n") is not None:
        rev_txt = (f" The revision branch, which is exact rather than "
                   f"statistical, accepts {rev.get('n_acceptable')} of "
                   f"{rev.get('n')}.")
    return [
        f"Precision against reader labels: 0% of the {n_alarms} alarms are "
        f"genuine contradictions (95% upper bound {hi * 100:.1f}%). The "
        f"annotators were models{ctrl}"
        + (f" and agree on {agree_n} of the {n_pairs} pairs; "
           if s.get("n_compared") else "; ")
        + f"a human round is next.",
        f"Two defects found and repaired; the alarms fell from {_ab[0]} to "
        f"{_ab[1]}. "
        f"The corpus is why the rest are false: the same readers find "
        f"{n_missed} contradictions in a random sample of {n_uf} unflagged "
        f"pairs.{rev_txt}",
    ]


def load_pre_repair_gate() -> dict | None:
    """The gate's result on the benchmark as it stood before the repair.

    Produced by `impl/scripts/rerun_pre_repair_gate.sh`, which swaps in the
    preserved pre-repair benchmark, runs the experiment and puts the current
    one back. It exists so that the before-and-after comparison in the
    deliverables rests on a generated measurement rather than on a number
    transcribed from a report.
    """
    p = PRIMARY / "exp2_gate_pre_unanswerable_repair.json"
    if not p.exists():
        return None
    try:
        payload = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None


def unanswerable_refusal_by_family(payload: dict | None) -> dict:
    """The gate's refusal rate at the operating point, per question family.

    The unanswerable class is not homogeneous. The out-of-domain family is
    unanswerable for any system that knows what the corpus is about; the
    corpus-anchored family is the case the gate is being tested on. The
    pooled rate is an upper bound and the strata are reported beside it.
    """
    if not payload:
        return {}
    blk = payload.get("refusal_by_family") or {}
    fams = blk.get("by_family") or {}
    hard = {k: v for k, v in fams.items() if "corpus_anchored" in k}
    n_hard = sum((v or {}).get("n", 0) for v in hard.values())
    r_hard = sum((v or {}).get("refused", 0) for v in hard.values())
    ood = fams.get("unanswerable_ood") or {}
    # The pooled rate is over the *unanswerable* families only: the
    # answerable families are in the same table, and pooling them would
    # give the refusal rate over the whole benchmark.
    un_fams = {k: v for k, v in fams.items() if k.startswith("unanswerable")}
    n_all = sum((v or {}).get("n", 0) for v in un_fams.values())
    r_all = sum((v or {}).get("refused", 0) for v in un_fams.values())
    return {
        "tau": blk.get("tau"),
        "by_family": fams,
        "pooled_refused_rate": (r_all / n_all) if n_all else None,
        "pooled_n": n_all,
        "pooled_refused": r_all,
        "hard_n": n_hard,
        "hard_refused": r_hard,
        "hard_refused_rate": (r_hard / n_hard) if n_hard else None,
        "ood_n": ood.get("n", 0),
        "ood_refused": ood.get("refused", 0),
        "ood_refused_rate": ood.get("refused_rate"),
    }


def generation_cost(payload: dict | None) -> dict:
    """What the arms cost, in tokens and in dollars.

    The token ratio and the cost ratio are different numbers, and only the
    second is a cost. The long-context arm sends the corpus on every query;
    most of those tokens are cache *reads*, which the provider bills at a
    fraction of the base rate, so the dollar ratio is smaller than the token
    ratio. The cache hit rate says whether that discount actually applied,
    and without it the cost figure means nothing.
    """
    out: dict = {}
    if not payload or payload.get("status") != "run":
        return out
    arms = payload.get("arms") or {}

    def _blk(name):
        return arms.get(name) or {}

    def _tok(blk, key):
        return ((blk.get("tokens") or {}).get(key) or 0)

    def _usd(blk):
        return ((blk.get("cost") or {}).get("input_usd") or 0.0)

    lc, ng, ft = _blk("long_context"), _blk("rag_nogate"), _blk("rag@fitted")
    if not lc or not ng:
        return out
    lc_tok = _tok(lc, "total_input")
    ng_tok = _tok(ng, "total_input")
    ft_tok = _tok(ft, "total_input")
    lc_usd = _usd(lc)
    ng_usd = _usd(ng)
    ft_usd = _usd(ft)
    out["long_context_input_tokens"] = lc_tok
    out["nogate_input_tokens"] = ng_tok
    out["fitted_input_tokens"] = ft_tok
    out["token_ratio_long_over_nogate"] = (lc_tok / ng_tok) if ng_tok else None
    out["cost_ratio_long_over_nogate"] = (lc_usd / ng_usd) if ng_usd else None
    out["cost_ratio_long_over_fitted"] = (lc_usd / ft_usd) if ft_usd else None
    out["long_context_input_usd"] = lc_usd
    out["nogate_input_usd"] = ng_usd
    out["fitted_input_usd"] = ft_usd
    out["long_context_cache_hit_rate"] = ((lc.get("cache") or {}).get("hit_rate"))
    out["cache_control"] = ((payload.get("generator") or {}).get("cache_control"))
    out["prices"] = ((payload.get("generator") or {}).get("prices_per_million"))
    return out


def generation_cost_claim(payload: dict | None) -> str:
    """One sentence stating the cost comparison correctly.

    The failure this guards against is specific: measuring a token ratio,
    calling it a cost, and letting the size of the token ratio carry an
    argument about money. Under prompt caching the two come apart, because
    a cached prefix is billed at a fraction of the base rate.
    """
    c = generation_cost(payload)
    if not c:
        return ("The cost comparison rests on the corpus's own token counts: "
                "the whole corpus against the retrieval arm's accepted "
                "context. A dollar figure needs the provider's prices, which "
                "are not measured here.")
    tok = c.get("token_ratio_long_over_nogate")
    cost = c.get("cost_ratio_long_over_nogate")
    hit = c.get("long_context_cache_hit_rate")
    if tok is None or cost is None:
        return "The cost comparison could not be computed from the run."
    cache_txt = ""
    if hit is not None:
        cache_txt = (f", with the corpus prefix served as a cache read on "
                     f"{hit:.1%} of the long-context arm's input tokens")
    return (
        f"The long-context arm sends {tok:.0f}x more input tokens per query "
        f"than the pipeline, which at the provider's cached-prefix pricing"
        f"{cache_txt} is a {cost:.1f}x input-cost ratio rather than "
        f"{tok:.0f}x: the token ratio and the cost ratio are different "
        f"numbers, and only the second one is a cost.")


def generation_summary_short(payload: dict | None) -> str:
    """A condensed form of the generator-side summary, for the conference paper.

    The long form is four hundred words of numbers and reads as a data dump;
    in a two-column paper it is a paragraph. This carries the setup, the
    per-arm rates of the deployed condition, and the verdict across both
    prompt conditions -- which is where the claim, the paired tests and the
    cost of the effect live. The per-claim hallucination rates, the scoring
    convention and the two instrument audits are carried by the full summary
    in the technical report, the guide and the status report.
    """
    if not payload or payload.get("status") != "run":
        return generation_summary(payload)

    conditions = load_generation_conditions()
    model = payload.get("model", "the generator")
    n_ans = payload.get("n_answerable", 0)
    n_un = payload.get("n_unanswerable", 0)

    live = [(arm, gen_arm(payload, arm)) for arm in GEN_ARMS]
    live = [(arm, blk) for arm, blk in live if blk]
    if not live:
        return ("The generator-side comparison produced no arms.")

    un_rates = []
    an_acc = []
    for _arm, blk in live:
        un = blk.get("unanswerable") or {}
        an = blk.get("answerable") or {}
        un_rates.append(f"{_rate(un.get('answer_rate'))} "
                        f"({un.get('n_answered', 0)} of {un.get('n', 0)})")
        an_acc.append(f"{_rate(an.get('accuracy_nli'))} "
                      f"({an.get('n_answered', 0)} of {an.get('n', 0)})")

    # Three arms carry the comparison: the same retrieval with the gate
    # removed, the fitted framework, and the random-refusal control. The
    # other two are in the tables in the technical report.
    keep = [arm for arm, _ in live if arm in ("rag_nogate", "rag@fitted",
                                               "rag@random")]
    if not keep:
        keep = [arm for arm, _ in live][:3]
    un_rates = []
    an_acc = []
    for _arm, blk in live:
        if _arm not in keep:
            continue
        un = blk.get("unanswerable") or {}
        an = blk.get("answerable") or {}
        un_rates.append(f"{_rate(un.get('answer_rate'))} "
                        f"({un.get('n_answered', 0)} of {un.get('n', 0)})")
        an_acc.append(f"{_rate(an.get('accuracy_nli'))} "
                      f"({an.get('n_answered', 0)} of {an.get('n', 0)})")
    return (
        f"{model} answered the same {n_ans} answerable and {n_un} "
        f"unanswerable questions behind five arms that share the generator, "
        f"the prompt wording, the question set and the scorer, so a "
        f"difference between them is attributable to the context and the gate "
        f"and to nothing else. "
        f"With the generator permitted to decline -- the deployed system -- "
        f"the rate of answering the unanswerable questions was "
        + ", ".join(un_rates) + " for the gate removed, the fitted framework "
        f"and the random-refusal control respectively, and the accuracy on "
        f"the answerable ones " + ", ".join(an_acc) + " respectively. "
        + _cap(gate_overall(conditions))
    )


def _significance_clause(whole: dict, first: dict, keyt: dict) -> str:
    """State which of the three scoring tests the margin is significant under.

    The sentence used to be written by hand and it was written backwards: it
    called p = 1.000 "significant" and the two smaller p-values "not
    significant". The clause is now derived from the p-values, so it cannot
    be wrong that way again.
    """
    _tests = (
        ("the whole-answer entailment test", whole),
        ("a length-controlled re-scoring of the same answers", first),
        ("a lexical test that ignores length", keyt),
    )
    _hits = [(n, t.get("p_value", 1)) for n, t in _tests
             if (t.get("p_value") or 1) <= 0.05]
    _ps = ", ".join(f"{t.get('p_value', 0):.3f}" for _, t in _tests)
    if len(_hits) == len(_tests):
        return f"is significant under all three scoring tests (p = {_ps})"
    if not _hits:
        return ("reaches no test's significance threshold -- not under the "
                "whole-answer entailment test, not under a length-controlled "
                "re-scoring of the same answers, and not under a lexical "
                f"test that ignores length (p = {_ps})")
    _named = ", ".join(f"{n} (p = {v:.3f})" for n, v in _hits)
    return f"is significant under {_named} only, and not under the others"


def generation_summary(payload: dict | None) -> str:
    """One paragraph stating what the generator-side comparison measured.

    The paragraph is carried verbatim by the papers, the report and the deck,
    and the build cannot be conditional on a result that may or may not exist,
    so it has to read correctly in both states: measured, or not run. In the
    unmeasured state it says exactly what is untested, because a missing
    baseline that is not stated is worse than one that is.
    """
    # The audit of the instrument, which holds whether or not the comparison
    # ran: the scorer is a property of the benchmark and the corpus, not of
    # the generator.
    audit = load_scorer_validation()
    audit_sentence = ""
    if audit and audit.get("status") == "run":
        audit_sentence = (
            f" The claim scorer itself was audited against the benchmark in "
            f"the meantime: {audit.get('n_truth_supported', 0)} of the "
            f"{audit.get('n_truth', 0)} answers the benchmark considers correct "
            f"are recognised as supported by the evidence that states them, "
            f"and {audit.get('n_fabrication_rejected', 0)} of the "
            f"{audit.get('n_fabrication', 0)} fabricated values are rejected.")

    if not payload or payload.get("status") != "run":
        reason = (payload or {}).get("reason") or (
            "no API credential was reachable from the machine this was "
            "measured on")
        return (
            f"The generator-side comparison was not run: {reason}. The "
            "answer-quality half of the comparison -- whether the gate reduces "
            "hallucination, and whether the pipeline matches a whole-corpus "
            "prompt on answer quality -- therefore remains untested, and no "
            "claim is made in either direction. The harness "
            "(`impl/experiments/run_generation_eval.py`) runs it as soon as "
            "the obstacle is removed." + audit_sentence
        )

    conditions = load_generation_conditions()
    model = payload.get("model", "the generator")
    n_ans = payload.get("n_answerable", 0)
    n_un = payload.get("n_unanswerable", 0)

    # The arms are named once and the numbers then follow in that order.
    # A paragraph that repeats each arm's full label for every column is
    # unreadable and twice as long.
    live = [(arm, gen_arm(payload, arm)) for arm in GEN_ARMS]
    live = [(arm, blk) for arm, blk in live if blk]
    if not live:
        return ("The generator-side comparison produced no arms.")

    parts = [
        f"{model} answered the same {n_ans} answerable and {n_un} unanswerable "
        f"questions behind five arms that share the generator, the prompt "
        f"wording, the question set and the scorer, so a difference between "
        f"them is attributable to the context and the gate and to nothing "
        f"else: "
        + "; ".join(GEN_LABELS[arm] for arm, _ in live) + "."
    ]

    def _condition_numbers(cond_payload) -> str:
        # The arms have to come from the payload this call is about. Reading
        # them from the enclosing scope instead reports the cautious
        # condition's rates twice -- under two different headings -- which is
        # the worst kind of wrong: both paragraphs are true sentences about
        # the wrong condition.
        cond_live = [(arm, gen_arm(cond_payload, arm)) for arm in GEN_ARMS]
        cond_live = [(arm, blk) for arm, blk in cond_live if blk]
        un_rates = []
        an_acc = []
        for _arm, blk in cond_live:
            un = blk.get("unanswerable") or {}
            an = blk.get("answerable") or {}
            un_rates.append(f"{_rate(un.get('answer_rate'))} "
                            f"({un.get('n_answered', 0)} of {un.get('n', 0)})")
            an_acc.append(f"{_rate(an.get('accuracy_nli'))} "
                          f"({an.get('n_answered', 0)} of {an.get('n', 0)})")
        return (f"The rate of answering the unanswerable questions was "
                + ", ".join(un_rates) + " respectively, and the accuracy on the "
                f"answerable ones " + ", ".join(an_acc) + " respectively.")

    parts.append(
        f"With the generator permitted to decline -- the deployed system -- "
        f"{_condition_numbers(payload)}"
    )

    answering = conditions.get("answering")
    if answering and answering.get("status") == "run":
        parts.append(
            f"With the permission to decline removed, and the model, the "
            f"questions, the retrieval and the scorer all unchanged, "
            f"{_condition_numbers(answering)}"
        )

    # The claims the arms produced on the unanswerable questions. In the
    # cautious condition the denominator is tiny because the arms mostly
    # refuse; in the answering condition it is not, and that is the point.
    fab = []
    n_claims = []
    for _arm, blk in live:
        un = blk.get("unanswerable") or {}
        if not un.get("n_claims"):
            continue
        fab.append(_rate(un.get("claim_hallucination_rate")))
        n_claims.append(un.get("n_claims", 0))
    if fab:
        parts.append(
            "Of the claims the arms produced on the unanswerable questions, the "
            "fraction supported by nothing in the evidence they were given was "
            + ", ".join(fab) + " respectively, on "
            + ", ".join(str(c) for c in n_claims) + " claims"
        )

    # A refusal that also asserts something is counted as an answer and
    # scored on the assertion. That is a judgement call, so the count of the
    # answers it affects travels with the numbers. No double quotes in any
    # token value: they are substituted into Python source as well as into
    # Markdown, and a quote would end the string it lands in.
    mixed = sum(int((gen_arm(payload, a) or {}).get("unanswerable", {})
                    .get("n_declined_with_content", 0) or 0)
                for a in GEN_ARMS)
    if mixed:
        parts.append(
            f"A refusal that also asserts something -- the documents do not "
            f"contain the demand for this SKU, so the quantity cannot be "
            f"computed; in general it is computed as ... -- is counted as an "
            f"answer and scored on the assertion, which is the reading that "
            f"gives the gate less credit, and {mixed} of the unanswerable "
            f"questions drew one."
        )

    # The instrument these numbers rest on is audited, not asserted, so the
    # summary carries the audit with it.
    audit = load_scorer_validation()
    if audit and audit.get("status") == "run":
        parts.append(
            f"The claim scorer was audited against the benchmark before the "
            f"comparison was read: {audit.get('n_truth_supported', 0)} of the "
            f"{audit.get('n_truth', 0)} answers the benchmark itself considers "
            f"correct are recognised as supported by the evidence that states "
            f"them, and {audit.get('n_fabrication_rejected', 0)} of the "
            f"{audit.get('n_fabrication', 0)} fabricated values are rejected."
        )

    # The verdict on the hypothesis the comparison was run to settle, across
    # every condition that ran. The papers carry the summary rather than the
    # verdict token, so the verdict has to be inside the summary.
    parts.append(_cap(gate_overall(conditions)))

    # The audit of the benchmark's answer labels. The accuracy figures above
    # are measured against them, so the correction travels with them.
    audit = load_label_audit()
    if audit and audit.get("status") == "run":
        sig = (audit.get("significance") or {}).get("tests") or {}
        whole = sig.get("nli_whole_answer") or {}
        first = sig.get("nli_first_sentence") or {}
        keyt = sig.get("keyterm_lexical") or {}
        pre = audit.get("pre_repair") or {}
        n_res = audit.get("n_defective", 0)
        n_ans = audit.get("n_answerable", 0)
        if pre.get("n_defective") is not None:
            parts.append(
                f"An audit of the benchmark's answer labels found that "
                f"{pre.get('n_defective_precise', pre.get('n_defective'))} "
                f"of the {pre.get('n_answerable')} "
                f"answerable questions carried an answer attached to the "
                f"wrong question: a table question named the column its key "
                f"came from while taking the answer from the next column, "
                f"and some numeric golds were digit prefixes of longer "
                f"tokens. The generator was corrected, the benchmark rebuilt "
                f"and every experiment in this project re-measured against "
                f"it, so the numbers reported here are post-repair; the "
                f"audit now finds {n_res} defective labels out of {n_ans}, "
                f"and the benchmark as it stood before the repair is kept "
                f"so that the finding stays checkable."
            )
        else:
            parts.append(
                f"An audit of the benchmark's answer labels finds {n_res} "
                f"defective labels out of {n_ans} answerable questions, and "
                f"the gold chunk is correct in every case, so the "
                f"retrieval-side measurements are unaffected."
            )
        parts.append(
            "The accuracy margin over the long-context arm "
            + _significance_clause(whole, first, keyt)
            + ", so the long-context comparison is settled on coverage and "
            "cost and directional rather than significant on answer quality."
        )
    return " ".join(parts)
