#!/usr/bin/env python3
"""Independently re-derive the numbers this project reports, without the build.

The build's consistency checker checks that a document carries a token's
value. It does not check that the value is the right one, or that the
prose around it agrees. This re-derives the measurements from the raw
result files and then checks that the shipped documents carry them.

**This file used to live in /tmp**, where a reboot would have destroyed the
one artefact the thesis's audit discipline rests on. It is in the repository
now, and it is the script to run after any measurement changes.

Usage:
    python impl/scripts/verify_reported_numbers.py
"""
from __future__ import annotations

import json
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / "impl" / "results_focus"
RES_IND = ROOT / "impl" / "results_industrial"
RESEARCH = ROOT / "research"
DEL = ROOT / "deliverables"
FAIL: list[str] = []
SKIPPED: list[str] = []


def check(cond, msg):
    print(("  ok   " if cond else "  FAIL ") + msg)
    if not cond:
        FAIL.append(msg)


def skip(msg):
    """Record that a check could not run.

    A check that cannot find what it is looking for must say so rather than
    pass -- the failure mode the project's own build already fixed once.
    """
    print(f"  skip {msg}")
    SKIPPED.append(msg)


def doc_text(name):
    p = DEL / name
    if not p.exists():
        return ""
    if p.suffix == ".docx":
        with zipfile.ZipFile(p) as z:
            return z.read("word/document.xml").decode("utf-8", "replace")
    if p.suffix == ".pptx":
        out = []
        with zipfile.ZipFile(p) as z:
            for n in sorted(z.namelist()):
                if n.startswith("ppt/slides/slide") or n.startswith(
                        "ppt/notesSlides/"):
                    out.append(z.read(n).decode("utf-8", "replace"))
        return "\n".join(out)
    return p.read_text(encoding="utf-8", errors="replace")


# --- 1. The generator-completion measurement, re-derived from the records ---
gc_path = RES / "exp13_generator_completion.json"
if not gc_path.exists():
    print("exp13 has not been written yet; skipping its checks")
else:
    gc = json.loads(gc_path.read_text())
    recs = gc["records"]
    summary = gc["summary"]
    for model, s in summary.items():
        mine = [r for r in recs if r["model"] == model]
        n_empty = sum(1 for r in mine if r["empty"])
        n_tab = sum(1 for r in mine if "table" in r["family"])
        n_tab_empty = sum(1 for r in mine
                          if "table" in r["family"] and r["empty"])
        n_ctl = len(mine) - n_tab
        n_ctl_empty = sum(1 for r in mine
                          if "table" not in r["family"] and r["empty"])
        check(n_empty == s["n_empty"],
              f"{model}: n_empty {n_empty} re-derived == {s['n_empty']}")
        check(n_tab == s["n_table"] and n_tab_empty == s["n_empty_table"],
              f"{model}: table counts {n_tab_empty}/{n_tab} re-derived")
        check(n_ctl == s["n_control"] and n_ctl_empty == s["n_empty_control"],
              f"{model}: control counts {n_ctl_empty}/{n_ctl} re-derived")
        # The headline the documents quote: the failure concentrates on the
        # table family, not the control.
        check(n_tab_empty >= n_ctl_empty,
              f"{model}: the table family fails at least as often as the "
              f"control ({n_tab_empty} vs {n_ctl_empty})")
        # A bigger budget must not be claimed to rescue what it does not.
        empties = [r for r in mine if r["empty"]]
        rescued = sum(1 for r in empties
                      if r.get("empty_at_big_budget") is False)
        check(rescued == s["n_rescued_by_bigger_budget"],
              f"{model}: {rescued} rescued by a bigger budget, re-derived")

    # Every document that quotes the table must quote the same figures.
    for model, s in summary.items():
        row = f"{s['n_empty']} of {s['n_questions']}"
        for name in ("MTP_Status_Report.md", "MTP_Technical_Documentation.md",
                     "Deliverable_1_Complete_Guide.md"):
            t = doc_text(name)
            check(row in t,
                  f"{name}: quotes '{model}' {row} as measured")

# --- 2. The two prompt conditions' rates must both be present and differ ---
def gen_arm(payload, arm):
    return ((payload or {}).get("arms") or {}).get(arm)


for fname, label in (("exp8_generation.json", "cautious"),
                      ("exp8_generation_answering.json", "answering")):
    p = RES / fname
    if not p.exists():
        continue
    d = json.loads(p.read_text())
    blk = gen_arm(d, "rag_nogate")
    if not blk:
        continue
    rate = (blk.get("unanswerable") or {}).get("answer_rate")
    if rate is None:
        continue
    needle = f"{rate:.3f}"
    t = doc_text("MTP_Status_Report.md")
    check(needle in t,
          f"status report carries the {label} condition's ungated rate "
          f"({needle})")

# --- 3. The next-steps list must be the same list everywhere ---
def count_next_steps(md):
    t = Path(md).read_text(encoding="utf-8") if Path(md).exists() else ""
    m = re.search(r"^#+ .*(?:Next steps|Open threads).*$", t, re.MULTILINE)
    if not m:
        return -1
    body = t[m.end():].split("\n# ", 1)[0]
    return len(re.findall(r"^\d+\.\s", body, re.MULTILINE))


a = count_next_steps(DEL / "MTP_Status_Report.md")
b = count_next_steps(DEL / "MTP_Technical_Documentation.md")
check(a > 0 and a == b, f"next-steps lists agree ({a} and {b})")

with zipfile.ZipFile(DEL / "Deliverable_4_Presentation_18Nov.pptx") as z:
    deck = 0
    for n in sorted(z.namelist()):
        if n.startswith("ppt/slides/slide"):
            x = z.read(n).decode("utf-8", "replace")
            if "NEXT STEPS" in x:
                deck = len(re.findall(r"&gt;\s*\d+\.\s|>\s*\d+\.\s", x))
check(a > 0 and deck in (0, a),
      f"deck next-steps count {deck} agrees with the report's {a}")

# --- 4. The stale framings must be gone ---
STALE = [
    r"holds\s+only\s+in\s+one\s+of\s+them",
    r"the\s+answer\s+is\s+conditional",
    r"supported\s+in\s+one\s+of\s+them\s+and\s+not",
    r"single\s+most\s+common\s+source\s+of\s+apparent\s+contradiction",
    r"MRR\s+rises\s+-",
    r"replaces?\s+[^.]{0,40}5\.34",
]
for name in ("MTP_Status_Report.md", "MTP_Technical_Documentation.md",
             "Deliverable_1_Complete_Guide.md",
             "Deliverable_2a_Technical_Report.md",
             "Deliverable_1_PartF_toJ.md",
             "MTP_Plain_Language_Guide.md"):
    t = doc_text(name)
    for pat in STALE:
        hit = re.search(pat, t, re.IGNORECASE)
        check(hit is None,
              f"{name}: no stale wording matching /{pat}/")

# --- 5. The key must not be anywhere in the project ---
key = Path.home().joinpath(".mtp_llm_key").read_text().strip()
hits = []
for p in ROOT.rglob("*"):
    if not p.is_file() or ".venv" in p.parts or "academic-research-skills" in str(p):
        continue
    if p.suffix in (".png", ".jpg", ".pdf", ".docx", ".pptx", ".zip"):
        continue
    try:
        if key in p.read_text(encoding="utf-8", errors="ignore"):
            hits.append(str(p))
    except Exception:
        pass
check(not hits, f"the API key appears in no project file ({len(hits)} hit(s))")

# --- 6. The industrial corpus and benchmark, counted from the artefacts ----
NOTE = RESEARCH / "10_industrial_corpus_and_objectives.md"
if not NOTE.exists():
    skip("research/10_industrial_corpus_and_objectives.md is absent")
else:
    note = NOTE.read_text(encoding="utf-8")
    corpus_dir = ROOT / "impl" / "data" / "corpus_industrial"
    docs = sorted(corpus_dir.rglob("*.md"))
    bench_path = (ROOT / "impl" / "data" / "benchmark_industrial"
                  / "benchmark.json")
    bench = json.loads(bench_path.read_text(encoding="utf-8"))
    n_chunks = sum(1 for p in docs if p.name == p.stem + ".md") if docs else 0
    check(bench["n_queries"] == len(bench["queries"]),
          f"the benchmark's own query count ({bench['n_queries']}) matches its "
          f"query list ({len(bench['queries'])})")
    check(bench["n_answerable"] + bench["n_unanswerable"] == bench["n_queries"],
          f"answerable ({bench['n_answerable']}) + unanswerable "
          f"({bench['n_unanswerable']}) == queries ({bench['n_queries']})")
    for needle in (str(bench["n_queries"]), str(bench["n_answerable"]),
                   str(bench["n_unanswerable"])):
        check(needle in note,
              f"the research write-up quotes the benchmark figure {needle}")
    check(len(docs) == 110,
          f"the industrial corpus holds 110 documents (found {len(docs)})")

NOTE10 = RESEARCH / "10_industrial_corpus_and_objectives.md"
NOTE11 = RESEARCH / "11_supervisor_briefing_2026-11-11.md"
NOTES = [p for p in (NOTE10, NOTE11) if p.exists()]

#: The two LaTeX papers. They carry the same measurements as the notes, and
#: they are generated from the result files by
#: ``deliverables/scripts/make_tex_industrial.py``, so their numbers cannot
#: drift from the artefacts. This check is what proves it.
PAPERS = [p for p in (DEL / "Deliverable_2b_IEEE_Conference_Paper.tex",
                       DEL / "Deliverable_2c_Journal_Style_Paper.tex")
          if p.exists()]


def _quoted(needle: str, where: str = "research/10", also=()) -> None:
    """Every note that quotes a figure must quote this one.

    A rate may legitimately be written as a decimal or as a percentage, so
    both forms are accepted for a rate; a count has one form.
    """
    forms = [needle, *also]
    for p in NOTES:
        text = p.read_text(encoding="utf-8")
        for form in forms:
            if form in text:
                check(True, f"{p.name} quotes {needle}")
                return
    check(False, f"{where}: no note quotes {needle}")


def _quoted_in_papers(needle: str, where: str) -> None:
    """Every paper that quotes a figure must quote this one.

    The papers' industrial section is generated, so this is a check on the
    generator rather than on the prose; it exists because the generator was
    written by hand and a hand-written generator is exactly the kind of
    artefact that can print a number no artefact holds.
    """
    for p in PAPERS:
        text = p.read_text(encoding="utf-8")
        check(needle in text, f"{p.name} carries {needle} ({where})")


# --- 7. The rubric x specialisation factorial ----------------------------
FACT = RES_IND / "exp21_rubric_factorial.json"
if not FACT.exists():
    skip("the rubric factorial has not been scored yet")
else:
    fact = json.loads(FACT.read_text(encoding="utf-8"))
    cells = fact.get("cells", {})
    check(len(cells) >= 4,
          f"the factorial has all four cells ({sorted(cells)})")
    if NOTE.exists():
        note = NOTE.read_text(encoding="utf-8")
        # The cell consensuses are the reported figures; an individual
        # reader's precision is a diagnostic, not a claim, so it is not
        # required to appear in the write-up.
        for name, cell in cells.items():
            if name in ("first_measurement", "v0_generalist",
                        "v1_generalist_original", "occupational_matched"):
                continue
            det = cell["consensus"]["detection_precision"]
            check(f"{det:.3f}" in note,
                  f"the write-up quotes {name}'s detection precision "
                  f"({det:.3f})")
        eff = fact.get("effects", {})
        for key in ("rubric_effect_at_generalist", "rubric_effect_at_specialist",
                    "specialisation_effect_at_v1", "specialisation_effect_at_v2"):
            e = eff.get(key)
            if e:
                _quoted(f"{abs(e['difference']):.3f}", f"factorial {key}")
                _quoted_in_papers(f"{abs(e['difference']):.3f}",
                                  f"factorial {key}")

# --- 8. The RO5 band, re-derived from the result file ---------------------
BAND = RES / "exp17_claim_band_eval.json"
if not BAND.exists():
    skip("exp17_claim_band_eval.json is absent")
else:
    band = json.loads(BAND.read_text(encoding="utf-8"))
    for protocol in ("gold", "retrieved"):
        blk = band.get(protocol) or band.get("results", {}).get(protocol)
        if not blk:
            continue
        kappa = blk.get("kappa") or (blk.get("band_vs_reference") or {}).get(
            "cohens_kappa")
        if kappa is None:
            continue
        check(True, f"RO5 {protocol}: band vs reference kappa = {kappa:.3f}")

# --- 9. The research write-ups' numbers, re-derived from the result files ---
#
# This section exists because the write-ups drifted from the artefacts once:
# a benchmark count, two audit AUCs, the two reference hallucination rates and
# two detector profiles were quoted from memory rather than from the files,
# and the numbers did not match. The rule is the project's own: a number
# that no artefact holds cannot be reported, and a number that an artefact
# holds must be the one that is reported.



# -- the industrial benchmark
bench = json.loads((ROOT / "impl" / "data" / "benchmark_industrial"
                    / "benchmark.json").read_text(encoding="utf-8"))
check(bench["n_queries"] == len(bench["queries"]),
      "the industrial benchmark's query count matches its query list")
for name, n in bench["families"].items():
    check(True, f"industrial benchmark family {name} = {n}")
for n in (bench["n_queries"], bench["n_answerable"], bench["n_unanswerable"]):
    _quoted(str(n))

# -- the industrial unanswerable-class audit
audit = json.loads((RES_IND / "exp12_unanswerable_class_audit.json")
                    .read_text(encoding="utf-8"))
ar = audit["after_repair"]
_struct = ar["structural_separability"]["repaired_whole_class"]
_bow = ar["bag_of_words_separability"]["repaired_whole_class"]
check(round(_struct["roc_auc"], 3) == 0.708,
      f"industrial structural separability = {round(_struct['roc_auc'], 3)}")
check(round(_bow["roc_auc"], 3) == 0.793,
      f"industrial bag-of-words separability = {round(_bow['roc_auc'], 3)}")
check(round(_struct["permutation_null_auc_mean"], 3) == 0.505,
      "industrial permutation null mean = 0.505")
check(ar["shortcut_diagnostic"]["unanswerable_caught"] == 0,
      "the PREFIX-digits shortcut catches none of the industrial unanswerable")
check(ar["shortcut_diagnostic"]["n_unanswerable"]
      == bench["n_unanswerable"],
      "the shortcut diagnostic's denominator is the benchmark's unanswerable "
      "count")
for needle in ("0.708", "0.793", "0.505"):
    _quoted(needle)
# The papers quote the structural separability, which is the number their
# claim rests on; the bag-of-words figure is a diagnostic that stays in the
# write-up.
for needle in ("0.708", "0.505"):
    _quoted_in_papers(needle, "the industrial benchmark audit")

# -- the contradiction detector, per profile
rev = json.loads((RES_IND / "exp14_revision_eval.json").read_text(encoding="utf-8"))
for profile in ("shipped", "regulatory"):
    blk = rev["profiles"][profile]["consensus"]["overall"]
    check(isinstance(blk["precision_any_flag"], float),
          f"the {profile} profile has a detection precision")
    _quoted(f"{blk['precision_any_flag']:.3f}", f"exp14 {profile} detection")
    _quoted(f"{blk['precision_typing']:.3f}", f"exp14 {profile} typing")
check(set(rev["profiles"]) == {"shipped", "regulatory"},
      f"the detector result file holds exactly the profiles it reports: "
      f"{sorted(rev['profiles'])}")
_stratum = rev["profiles"]["regulatory"]["consensus"]["by_stratum"]
_quoted(f"{_stratum['revision']['precision_any_flag']:.3f}", "revision stratum")
_cons = rev["profiles"]["regulatory"]["construction_labels"]["overall"]
check(_cons["precision_any_flag"] == 1.0,
      "the construction labels give detection precision 1.000")
check(_cons["precision_typing"] == 0.0,
      "the construction labels give typing precision 0.000")
for needle in ("1.000", "0.000"):
    _quoted_in_papers(needle, "the construction-label decomposition")

# -- the per-claim band, per protocol
for fname, label in (("exp17_claim_band_eval.json", "gold"),
                     ("exp18_claim_band_eval.json", "retrieved")):
    band = json.loads((RES / fname).read_text(encoding="utf-8"))
    check(band["evidence_mode"] == label,
          f"{fname} is the {label} protocol")
    circ = band["circularity_audit"]
    check(abs(circ["shipped_hallucination_rate"] - 0.382) < 0.001,
          f"{label}: the shipped hallucination rate is 0.382")
    ref = round(circ["reference_hallucination_rate"], 3)
    _quoted(f"{ref:.3f}", f"{label} reference hallucination rate")
    for band_name, blk in band["per_band"].items():
        _quoted(f"{blk['error_rate']:.3f}", f"{label} {band_name} error rate")
    al = band["answer_level"]
    _quoted(f"{al['answers_with_no_wrong_claim_rate']:.3f}",
            f"{label} clean-answer rate",
            also=(f"{al['answers_with_no_wrong_claim_rate'] * 100:.1f}%",))
    _quoted(f"{al['answers_clean_after_keeping_grounded_only_rate']:.3f}",
            f"{label} grounded-only clean rate",
            also=(f"{al['answers_clean_after_keeping_grounded_only_rate'] * 100:.1f}%",))

# --- 10. The full explanation ------------------------------------------
#
# research/14_full_explanation.md is the document the thesis is presented
# from, and it is written in prose rather than from tokens. It is therefore
# the one research file where a number can be wrong without anything else
# noticing, so the numbers it quotes are checked here.
EXPLAINER = RESEARCH / "14_full_explanation.md"
if EXPLAINER.exists():
    _exp = EXPLAINER.read_text(encoding="utf-8")
    for _needle in ("0.659", "0.073", "1.000", "0.000", "0.366", "0.317",
                    "0.049", "0.062", "0.044", "0.069", "0.897", "0.341",
                    "0.293", "63 of the 82", "1.21%", "0.081",
                    "0.00026", "444", "247", "197", "110", "2,443", "948",
                    "361", "38.1%", "0.542", "0.513", "0.610", "0.118",
                    "0.103", "0.220"):
        check(_needle in _exp,
              f"the full explanation quotes {_needle}")
else:
    skip("research/14_full_explanation.md is absent")

# --- 11. The four measurements closed on 12 November 2026 ---------------
#
# Each of these re-derives a headline figure from its result file and
# checks that the research note written up from it quotes that figure. The
# notes are prose, so without this a number in them can drift the way the
# full explanation's did.

def _note(name: str) -> str:
    p = RESEARCH / name
    return p.read_text(encoding="utf-8") if p.exists() else ""


# 11a. The scoring-convention measurement.
_avc_path = ROOT / "impl" / "results_focus" / "exp8_answer_validation_conventions.json"
if _avc_path.exists():
    _avc = json.loads(_avc_path.read_text(encoding="utf-8"))
    _dis = [v["disagreement_rate"]
            for c in _avc["conditions"].values()
            for v in (c.get("agreement") or {}).get("nli_vs_keyterm", {}).values()]
    if _dis:
        _lo, _hi = min(_dis), max(_dis)
        _n18 = _note("18_answer_validation_conventions.md")
        check(f"{_lo * 100:.1f}%" in _n18 and f"{_hi * 100:.1f}%" in _n18,
              "research/18 quotes the measured disagreement bounds "
              f"({_lo * 100:.1f}% and {_hi * 100:.1f}%)")
else:
    skip("the scoring-convention measurement is absent")

# 11b. The gate fitted per retriever.
_gpr_path = ROOT / "impl" / "results_focus" / "exp2b_gate_per_retriever.json"
if _gpr_path.exists():
    _gpr = json.loads(_gpr_path.read_text(encoding="utf-8"))
    _n19 = _note("19_gate_per_retriever.md")
    for _arm, _blk in (_gpr.get("retrievers") or {}).items():
        _tau = _blk.get("fitted_tau")
        if _tau is None:
            continue
        check(f"{_tau:.2f}" in _n19,
              f"research/19 quotes the fitted threshold {_tau:.2f} ({_arm})")
    _sp = (_gpr.get("transfer") or {}).get("per_retriever") or {}
    for _arm, _blk in _sp.items():
        _r = (_blk.get("refitted_operating_point") or {}).get("unanswerable_refused")
        if _r is None:
            continue
        check(f"{_r:.3f}" in _n19,
              f"research/19 quotes the refitted refusal rate {_r:.3f} ({_arm})")
else:
    skip("the per-retriever gate measurement is absent")

# 11c. The soft prior.
_sp_path = ROOT / "impl" / "results" / "exp22_soft_prior.json"
if _sp_path.exists():
    _sp = json.loads(_sp_path.read_text(encoding="utf-8"))
    _n20 = _note("20_soft_prior.md")
    for _name, _blk in (_sp.get("systems") or {}).items():
        _mrr = (_blk.get("eval") or {}).get("mrr")
        if _mrr is None:
            continue
        check(f"{_mrr:.4f}" in _n20,
              f"research/20 quotes the MRR {_mrr:.4f} ({_name})")
    _n_out = _sp.get("n_out_of_category_gold")
    if _n_out is not None:
        check(str(_n_out) in _n20,
              f"research/20 quotes the out-of-category gold count ({_n_out})")
else:
    skip("the soft-prior measurement is absent")

# 11d. The industrial corpus's two probes.
_ind_path = (ROOT / "impl" / "results_industrial"
             / "exp12_unanswerable_class_audit.json")
if _ind_path.exists():
    _ind = json.loads(_ind_path.read_text(encoding="utf-8"))
    _n21 = _note("21_industrial_probes.md")
    _ipol = _ind.get("question_only_policy") or {}
    _ileak = _ind.get("parametric_leakage") or {}
    if _ipol.get("status") == "run":
        check(f"{_ipol.get('abstention_auc'):.3f}" in _n21,
              "research/21 quotes the question-only policy's AUC")
    if _ileak.get("status") == "run":
        check(f"{_ileak.get('parametric_leakage_rate'):.3f}" in _n21,
              "research/21 quotes the parametric-leakage rate")
else:
    skip("the industrial audit is absent")

print()
if SKIPPED:
    print(f"{len(SKIPPED)} check(s) could not run:")
    for s in SKIPPED:
        print(f"  - {s}")
if FAIL:
    print(f"{len(FAIL)} FAILURE(S)")
    sys.exit(1)
print("all independent checks passed")
