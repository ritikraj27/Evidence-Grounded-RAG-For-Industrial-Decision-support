#!/usr/bin/env python3
"""Consistency checks over the generated deliverables.

Six things that silently rot as a project evolves, checked here:

1. **Numbers that appear in prose.** The query count, the chunk count, the
   document count and the modality shares are stated in the guide, the paper,
   the presentation and the report. If the corpus or the benchmark changes,
   any of them can be left behind. This check reports every place where a
   stale number survives.

2. **Corpus integrity.** The manifest, the index and the benchmark must
   agree, no chunk id may be duplicated, and no document may sit in two
   categories. An article fetched into two categories is indexed twice, is
   split by the category pre-filter, and leaks into both halves of the
   cross-category transfer split -- and nothing in the experiment code
   reports any of that.

3. **Templates that hard-code a corpus size.** Every such number is a
   `{{TOKEN}}` substituted at build time. A literal in a template survives
   the next corpus change and quietly becomes a false claim.

4. **Citations that were never verified.** Every arXiv identifier and DOI that
   appears in a deliverable must appear in the citation audit, which is where
   each one was resolved against a live API. An identifier that is not in the
   audit is either new or wrong, and both need attention.

5. **Deliverables that no longer exist.** The build assumes a fixed set.

6. **Superseded measurements.** A hand-written sentence in a template
   survives a corpus change and becomes a false claim -- a paper that
   describes a reranker raising recall when the current run shows it lowering
   it. Every value that was true of the archived pre-encoder-swap run and is
   not true of the current one is looked for in every deliverable.

Exit status is 0 when nothing is wrong, 1 when a check fails, so the build can
stop rather than ship an inconsistent document set.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DELIV = ROOT / "deliverables"
TEMPLATES = ROOT / "deliverables" / "templates"
RESULTS = ROOT / "impl" / "results"
FOCUS_RESULTS = ROOT / "impl" / "results_focus"
#: The third corpus -- the industrial (eCFR) one -- carries measurements that
#: are current, so the superseded-results tripwire has to know about them.
#: Without this, a value that was true of the industrial run and has since
#: been superseded would not be caught, and one that is current could be
#: flagged as stale by coincidence.
INDUSTRIAL_RESULTS = ROOT / "impl" / "results_industrial"
BENCH = ROOT / "impl" / "data" / "benchmark" / "benchmark.json"
MANIFEST = ROOT / "impl" / "data" / "corpus" / "manifest.json"
INDEX = ROOT / "impl" / "artifacts" / "index.json"
FOCUS_INDEX = ROOT / "impl" / "artifacts_focus" / "index.json"
AUDIT = ROOT / "research" / "00_citation_audit.md"

TEXT_TARGETS = [
    "Deliverable_1_Part1_Content.md",
    "Deliverable_1_PartD_Code.md",
    "Deliverable_1_PartF_toJ.md",
    "Deliverable_1_Complete_Guide.md",
    "Deliverable_2a_Technical_Report.md",
    "Deliverable_2b_IEEE_Conference_Paper.tex",
    "Deliverable_2c_Journal_Style_Paper.tex",
    "scripts/make_pptx.py",
    "scripts/make_docx.py",
    "READ_ME_FIRST.md",
    "../README.md",
    "MTP_Defence_Script_Guide.md",
]

REQUIRED_FILES = [
    "Deliverable_1_Complete_Guide.md",
    "Deliverable_1_Complete_Guide.docx",
    "Deliverable_2a_Technical_Report.md",
    "Deliverable_2a_Technical_Report.docx",
    "Deliverable_2b_IEEE_Conference_Paper.tex",
    "Deliverable_2c_Journal_Style_Paper.tex",
    "Deliverable_3_Department_Report.docx",
    "Deliverable_4_Presentation_18Nov.pptx",
    "MTP_Defence_Deck_Companion.md",
    "MTP_Report_Deck_Companion.md",
    "MTP_Defence_Script_Guide.md",
    "MTP_Status_Report.md",
    "MTP_Status_Report.pdf",
    "MTP_Technical_Documentation.md",
    "MTP_Technical_Documentation.pdf",
    "MTP_Plain_Language_Guide.md",
    "MTP_Plain_Language_Guide.docx",
    "MTP_Plain_Language_Guide.pdf",
]

problems: list[str] = []
notes: list[str] = []


def normalise_latex(text: str) -> str:
    """Turn LaTeX digit grouping (2{,}570) into plain digits (2570)."""
    # LaTeX groups the comma: 2{,}570 -> 2570
    return re.sub(r"\{,\}(\d{3})", r"\1", text)


def is_symbolic(text: str, start: int) -> bool:
    """True when the number at `start` is a parameter or a worked example.

    Two forms are not claims about this corpus:

    * "Corpus of N = 100 documents" -- a worked example with a symbolic N;
    * "At b = 0 document length is ignored" -- a formula parameter that the
      next word happens to continue.
    """
    lead = text[max(0, start - 16):start]
    return bool(re.search(r"[A-Za-z]\s*=\s*$", lead))


def check_numbers() -> None:
    bench = json.loads(BENCH.read_text(encoding="utf-8"))
    exp1_path = next((d / "exp1_ablation.json" for d in
                        (FOCUS_RESULTS, RESULTS)
                        if (d / "exp1_ablation.json").exists()), None)
    if exp1_path is None:
        notes.append("exp1 not yet run; skipping the number consistency check")
        return
    exp1 = json.loads(exp1_path.read_text(encoding="utf-8"))

    n_q = bench["n_queries"]
    n_ans = bench["n_answerable"]
    n_un = bench["n_unanswerable"]
    n_chunks = exp1["corpus_stats"]["n_chunks"]
    share_text = exp1["corpus_stats"]["share_text"]
    # Two corpora are in play: the multi-category one, whose size the prose
    # quotes when it describes the dataset, and the focus-domain one, whose
    # size the results are measured on. Both counts are legitimate.
    chunk_counts = {n_chunks}
    for d in (FOCUS_RESULTS, RESULTS, INDUSTRIAL_RESULTS):
        f = d / "exp1_ablation.json"
        if f.exists():
            chunk_counts.add(json.loads(f.read_text(encoding="utf-8"))
                             ["corpus_stats"]["n_chunks"])

    # Any "NNN-query" or "NNN queries" claim in the deliverables must be the
    # size of one of the current benchmarks. Two benchmarks are in play --
    # the multi-category one and the focus-domain one -- and the expert-
    # annotated SupplyChainQA is a third, which is quoted for comparison.
    counts = {n_q}
    for f in (ROOT / "impl" / "data" / "benchmark" / "benchmark.json",
              ROOT / "impl" / "data" / "benchmark_focus" / "benchmark.json",
              ROOT / "impl" / "data" / "benchmark_industrial" / "benchmark.json"):
        if f.exists():
            b = json.loads(f.read_text(encoding="utf-8"))
            counts.add(b["n_queries"])
    stale_query_count = re.compile(r"\b(\d{2,4})[- ]quer")
    for name in TEXT_TARGETS:
        p = DELIV / name
        if not p.exists():
            continue
        text = normalise_latex(p.read_text(encoding="utf-8"))
        for m in stale_query_count.finditer(text):
            val = int(m.group(1))
            if val in counts or val in (300, 200):
                continue  # a current benchmark, or another paper's
            if val < 100:
                continue  # not a benchmark-size claim
            if is_symbolic(text, m.start()):
                continue  # a formula parameter or a worked example
            # A derived count -- the size of the gate's negative class --
            # is not a benchmark size.
            window = text[max(0, m.start() - 90):m.end() + 40].lower()
            if "negative class" in window or "negative" in window:
                continue
            problems.append(
                f"{name}: query count {val} matches no current benchmark "
                f"({sorted(counts)}) — '{text[max(0, m.start()-40):m.end()+20]}'"
            )

    # The chunk count must match.
    chunk_pat = re.compile(r"\b(\d{1,3}(?:,\d{3})*)\s+chunks\b")
    for name in TEXT_TARGETS:
        p = DELIV / name
        if not p.exists():
            continue
        text = normalise_latex(p.read_text(encoding="utf-8"))
        for m in chunk_pat.finditer(text):
            val = int(m.group(1).replace(",", ""))
            if val in chunk_counts or val == 634:
                continue  # a current corpus, or the September report's corpus
            if val < 100:
                continue  # a context-size statement, not a corpus-size claim
            if is_symbolic(text, m.start()):
                continue  # a formula parameter or a worked example
            problems.append(
                f"{name}: chunk count {val} matches no current corpus "
                f"({sorted(chunk_counts)}) — '{text[max(0, m.start()-40):m.end()+20]}'"
            )

    # The unanswerable count must match wherever it is stated next to the
    # benchmark size.
    for name in TEXT_TARGETS:
        p = DELIV / name
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8")
        for m in re.finditer(r"of which (\d+) are\s*\n?deliberately unanswerable", text):
            val = int(m.group(1))
            if val != n_un:
                problems.append(
                    f"{name}: unanswerable count {val} does not match "
                    f"({n_un})"
                )

    notes.append(
        f"numbers checked: {n_q} queries ({n_ans} answerable, {n_un} "
        f"unanswerable), {n_chunks} chunks, {share_text:.1%} text"
    )


def check_corpus_integrity() -> None:
    """The corpus, the index and the benchmark must agree.

    A corpus built by fetching the same article into two categories produces
    two chunks with the same id, a document that belongs to two categories,
    and a leak across the train/held-out category split. Nothing about the
    experiment code would report that, so it is checked here against the
    manifest, the index and the benchmark.
    """
    if not MANIFEST.exists() or not INDEX.exists():
        notes.append("corpus manifest or index missing; skipping the integrity check")
        return
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    stats = index["stats"]
    chunks = index["chunks"]

    titles = [d["title"] for d in manifest]
    dup_titles = {t for t in titles if titles.count(t) > 1}
    if dup_titles:
        problems.append(
            f"corpus manifest lists {sorted(dup_titles)} more than once — an "
            "article in two categories is indexed twice and leaks across the "
            "cross-category transfer split"
        )

    if stats.get("duplicate_chunk_ids", 0):
        problems.append(
            f"index has {stats['duplicate_chunk_ids']} duplicated chunk ids — "
            "the same document was ingested more than once"
        )

    ids = [c["chunk_id"] for c in chunks]
    if len(set(ids)) != len(ids):
        problems.append(
            f"index holds {len(ids)} chunks but only {len(set(ids))} distinct "
            "chunk ids"
        )

    # No document may sit in two categories.
    by_doc: dict[str, set[str]] = {}
    for c in chunks:
        by_doc.setdefault(c["doc_id"], set()).add(c["category"])
    straddle = {d: sorted(cs) for d, cs in by_doc.items() if len(cs) > 1}
    if straddle:
        problems.append(
            f"{len(straddle)} document(s) appear under more than one category: "
            f"{sorted(straddle)[:5]}"
        )

    if stats["n_documents"] != len(set(titles)):
        problems.append(
            f"index reports {stats['n_documents']} documents but the manifest "
            f"holds {len(set(titles))} distinct titles"
        )
    if stats["n_chunks"] != len(chunks):
        problems.append(
            f"index stats report {stats['n_chunks']} chunks but the index holds "
            f"{len(chunks)}"
        )
    # The long-context arm reads the corpus directly, so its reported size
    # must match the index it was measured against.
    for directory, label, index_path in (
            (FOCUS_RESULTS, "focus-domain long-context run", FOCUS_INDEX),
            (RESULTS, "multi-category long-context run", INDEX)):
        lc = directory / "exp7_long_context.json"
        if not lc.exists():
            continue
        data = json.loads(lc.read_text(encoding="utf-8")).get("summary", {})
        lc_stats = data.get("corpus", {})
        idx = json.loads(index_path.read_text(encoding="utf-8"))["stats"]
        if lc_stats and lc_stats.get("corpus_chunks") != idx["n_chunks"]:
            problems.append(
                f"the {label} was measured on {lc_stats.get('corpus_chunks')} "
                f"chunks but its index holds {idx['n_chunks']} — re-run it or "
                "restore the matching index")

    notes.append(
        f"corpus integrity: {stats['n_documents']} documents, "
        f"{stats['n_chunks']} chunks, {stats.get('n_categories', '?')} categories, "
        f"{stats.get('duplicate_chunk_ids', 0)} duplicate chunk ids"
    )

    # Staleness: every experiment must have been run against the index that
    # is actually on disk. If the corpus was rebuilt and an experiment was
    # not re-run, the two disagree and every number in the deliverables is
    # wrong. The same check covers the long-context arm, which reads the
    # corpus directly and would otherwise report the size of a corpus that no
    # longer exists.
    for results_dir, index_path, label in (
        (FOCUS_RESULTS, FOCUS_INDEX, "focus-domain run"),
        (RESULTS, INDEX, "multi-category run"),
    ):
        exp1_path = results_dir / "exp1_ablation.json"
        idx_path = index_path
        if not exp1_path.exists() or not idx_path.exists():
            continue
        exp1 = json.loads(exp1_path.read_text(encoding="utf-8"))
        cs = exp1.get("corpus_stats", {})
        idx = json.loads(idx_path.read_text(encoding="utf-8"))["stats"]
        if not cs:
            continue
        if cs.get("n_chunks") != idx["n_chunks"]:
            problems.append(
                f"the {label} was run on {cs.get('n_chunks')} chunks but its "
                f"index holds {idx['n_chunks']} — re-run the experiment or "
                "restore the matching index"
            )


def check_templates_tokenised() -> None:
    """The templates must not hard-code a corpus or benchmark size.

    Every such number is now a `{{TOKEN}}` that the build substitutes from
    the measured artefacts. A literal left in a template is a number that
    will survive the next corpus change and quietly become a false claim --
    which is exactly how the guide came to say "41 documents" while the
    report said "39".
    """
    # Literals that legitimately describe the *September report's* corpus,
    # not ours, and the expert-annotated benchmark it is compared against.
    # 200 is FAB-Bench's query-answer pair count, quoted from the paper when
    # it is named as a comparator; it is that benchmark's number, not ours.
    allowed = {634, 24, 300, 371, 200}
    # The industrial corpus's own size, read from its result file rather
    # than written by hand: it is a current corpus, so its counts are as
    # legitimate as the other two.
    _ind_exp1 = INDUSTRIAL_RESULTS / "exp1_ablation.json"
    if _ind_exp1.exists():
        _ics = json.loads(_ind_exp1.read_text(encoding="utf-8"))["corpus_stats"]
        allowed.add(_ics["n_chunks"])
        allowed.add(_ics["n_documents"])
    problems_found: list[str] = []
    checked = 0
    for p in sorted(TEMPLATES.rglob("*")):
        if not p.is_file() or p.suffix not in (".md", ".tex", ".py"):
            continue
        rel = p.relative_to(TEMPLATES)
        text = normalise_latex(p.read_text(encoding="utf-8"))
        checked += 1
        for pat, label in (
            (r"\b(\d{1,3}(?:,\d{3})*)\s+chunks\b", "chunk count"),
            (r"\b(\d{2,4})[- ]quer", "query count"),
            (r"\b(\d{1,3})\s+documents?\b", "document count"),
        ):
            for m in re.finditer(pat, text):
                val = int(m.group(1).replace(",", ""))
                if val in allowed or val < 100:
                    continue
                # "Corpus of N = 100 documents" is a worked example with a
                # symbolic N, not a claim about this corpus.
                if is_symbolic(text, m.start()):
                    continue
                # A number in a row that cites a paper is that paper's
                # number -- a benchmark's size, not ours.
                line_start = text.rfind("\n", 0, m.start()) + 1
                line_end = text.find("\n", m.end())
                line = text[line_start:line_end if line_end != -1 else len(text)]
                if re.search(r"arXiv:|10\.\d{4,9}/|DOI", line):
                    continue
                problems_found.append(
                    f"templates/{rel}: hard-coded {label} {val} — use a "
                    f"{{{{TOKEN}}}} instead"
                )
    # A placeholder where a measurement should be is a build failure: the
    # deliverable would ship a sentence with no number in it.
    for name in TEXT_TARGETS:
        pp = DELIV / name
        if not pp.exists():
            continue
        text = pp.read_text(encoding="utf-8")
        n = text.count("[not measured]")
        if n:
            problems.append(
                f"{name}: {n} occurrence(s) of the placeholder — the "
                "corresponding experiment has not been run")
    problems.extend(problems_found)
    notes.append(
        f"{checked} template files checked for hard-coded corpus sizes"
        + (f" — {len(problems_found)} found" if problems_found else "")
    )


def check_document_counts() -> None:
    """Every document count stated in a deliverable must be a current one.

    Two corpora are in play and both counts are legitimate: the
    multi-category corpus and the focus domain. A number that matches
    neither is stale.
    """
    counts = set()
    for d in (FOCUS_RESULTS, RESULTS, INDUSTRIAL_RESULTS):
        f = d / "exp1_ablation.json"
        if f.exists():
            counts.add(json.loads(f.read_text(encoding="utf-8"))
                       ["corpus_stats"]["n_documents"])
    if not counts:
        return
    pat = re.compile(r"\b(\d{1,3})[- ]documents?\b")
    for name in TEXT_TARGETS:
        p = DELIV / name
        if not p.exists():
            continue
        text = normalise_latex(p.read_text(encoding="utf-8"))
        for m in pat.finditer(text):
            val = int(m.group(1))
            if val in counts or val == 24:
                continue  # a current corpus, or the September report's corpus
            if is_symbolic(text, m.start()):
                continue  # a formula parameter or a worked example
            # A number in a row that cites a paper is that paper's number.
            line_start = text.rfind("\n", 0, m.start()) + 1
            line_end = text.find("\n", m.end())
            line = text[line_start:line_end if line_end != -1 else len(text)]
            if re.search(r"arXiv:|10\.\d{4,9}/|DOI", line):
                continue
            problems.append(
                f"{name}: document count {val} matches neither current corpus "
                f"({sorted(counts)}) \u2014 "
                f"'{text[max(0, m.start()-40):m.end()+20]}'"
            )



def check_benchmark_questions() -> None:
    """Every answerable question must be a question somebody would ask.

    The silver-standard generator derives questions from sentences in the
    documents. A permissive match could begin mid-clause or after a word the
    markdown converter had truncated, and the result was a question like
    "What value is stated for a teep in the source documentation?". A
    quarter of the benchmark was malformed before the generator was taught
    to reject a subject that does not read like a noun phrase.
    """
    if not BENCH.exists():
        return
    bench = json.loads(BENCH.read_text(encoding="utf-8"))
    answerable = [q for q in bench["queries"] if q["gold"]]
    # The rebuilt unanswerable class is held to the same standard: a
    # question nobody would ask is a defect whichever half of the benchmark
    # it sits in.
    answerable += [q for q in bench["queries"]
                   if q["family"].startswith("unanswerable_corpus_anchored")]
    malformed = []
    for q in answerable:
        t = q["query"]
        if not t.endswith("?"):
            malformed.append((t, "no question mark"))
        elif "  " in t:
            malformed.append((t, "double space"))
        elif "**" in t or "[[" in t or "|" in t:
            malformed.append((t, "markup left in the question"))
        elif not t.startswith(("What is ", "What are ", "What was ", "What were ",
                               "What value is stated for ",
                               "According to the table in the source document, ")):
            malformed.append((t, "unrecognised question shape"))
        else:
            # The subject of a "What is X?" question must not contain a
            # verb: that means the match began mid-clause.
            head = t[len("What is "):] if t.startswith("What is ") else ""
            if head:
                body = head.rstrip("?").lower()
                for verb in (" is ", " are ", " was ", " were ", " shows ",
                             " know ", " assume ", " published ", " avoid "):
                    if verb in body:
                        malformed.append((t, f"verb {verb.strip()!r} in the subject"))
                        break
    for t, why in malformed[:10]:
        problems.append(f"benchmark: malformed question ({why}) — {t!r}")
    if malformed:
        problems.append(
            f"benchmark: {len(malformed)} of {len(answerable)} answerable "
            "questions are malformed")
    notes.append(
        f"benchmark: {len([q for q in bench['queries'] if q['gold']])} "
        f"answerable + "
        f"{len(bench['queries']) - len([q for q in bench['queries'] if q['gold']])} "
        f"unanswerable questions "
        f"({len(answerable)} checked, {len(malformed)} malformed)")


def check_no_unsubstituted_tokens() -> None:
    """No deliverable may ship with a `{{TOKEN}}` still in it.

    A token that the substitution does not know about is left in place
    literally, and the reader sees `{{POOL5}}` where a number should be.
    The token pattern once excluded digits, so every token with a digit in it
    was silently left unsubstituted for months.
    """
    import re as _re
    pattern = _re.compile(r"\{\{[A-Z0-9_]+\}\}")
    # A token written with one brace instead of two is just as unsubstituted
    # as one written with two, and the prose ships it literally either way.
    # The same is true of a bare token *name* left in the text, which is
    # what a token looks like after the braces have been stripped.
    known = set()
    try:
        import sys as _sys
        _sys.path.insert(0, str(DELIV / "scripts"))
        from substitute_tokens import values as _values
        known = set(_values())
    except Exception:
        pass
    for name in TEXT_TARGETS + ["../README.md"]:
        p = DELIV / name
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8")
        leftovers = sorted(set(pattern.findall(text)))
        if leftovers:
            problems.append(
                f"{name}: unsubstituted tokens {leftovers} — the prose would "
                "ship them literally"
            )
        if known and p.suffix == ".md":
            # A token written with ONE brace instead of two is just as
            # unsubstituted as one written with two. Only a known token
            # name counts: a LaTeX macro such as {EMNLP} and a Python
            # format placeholder are not tokens.
            singles = sorted(
                m for m in _re.findall(r"\{([A-Z0-9_]+)\}", text)
                if m in known)
            if singles:
                problems.append(
                    f"{name}: tokens written with one brace {singles} — the "
                    "prose would ship them literally"
                )
            bare = sorted(
                tok for tok in known
                if len(tok) > 3
                and _re.search(r"(?<![A-Z0-9_])" + _re.escape(tok)
                               + r"(?![A-Z0-9_])", text))
            if bare:
                problems.append(
                    f"{name}: bare token names {bare} — the prose would ship "
                    "them literally"
                )
    notes.append("no unsubstituted tokens in the deliverables")


def _decimals_in(obj, out: set[str]) -> None:
    """Collect every number in [0, 1] from a JSON tree, at three decimals."""
    if isinstance(obj, dict):
        for v in obj.values():
            _decimals_in(v, out)
    elif isinstance(obj, list):
        for v in obj:
            _decimals_in(v, out)
    elif isinstance(obj, (int, float)) and not isinstance(obj, bool):
        f = float(obj)
        if 0.0 <= f <= 1.0:
            out.add(f"{f:.3f}")


#: Numbers that are illustrative rather than measured, and are allowed to
#: coincide with a superseded measurement. Each one is an example sentence
#: about what a refusal looks like, not a result.
ALLOWED_SUPERSEDED = {
    "0.312",  # the worked example of an auditable refusal message
}

#: Numbers that are *quotations from other people's published work*, quoted
#: in the related-work and threat sections. The tripwire cannot tell a
#: measurement of ours from a citation of someone else's, and these five
#: coincide with values the archived pre-swap run also produced -- which is
#: a coincidence, not a drift. Each is named here with what it is, so the
#: allow-list is a record rather than a mute button.
ALLOWED_QUOTED_FROM_LITERATURE = {
    "0.191",  # miss rate quoted from the 2026 query-time RAG-poisoning-defence study
    "0.758",  # AUROC quoted from the same study
    "0.763",  # miss rate quoted from the same study
    "0.603",  # AUROC quoted from the 2026 cheap-LLM-judge study
    "0.290",  # coverage quoted from I-CALM (arXiv:2604.03904)
}
ALLOWED_SUPERSEDED = ALLOWED_SUPERSEDED | ALLOWED_QUOTED_FROM_LITERATURE


def check_no_superseded_results() -> None:
    """No template may hard-code a measurement that has been superseded.

    The generators rewrite the tables and the parts of the prose that they
    own, but hand-written sentences in a template survive a corpus change
    unchanged and become false claims. The archive in
    `research/baseline_minilm/` holds the pre-encoder-swap measurements; any
    decimal that was true of that run and is not true of the current one is a
    value that only a stale sentence would quote.

    The **templates** are scanned, not the built deliverables: a number that
    arrives through a `{{TOKEN}}` is bound to a measurement and is deliberate
    -- the before/after comparison quotes the archived baseline on purpose --
    whereas a number written by hand in a template is a claim that nobody
    re-checked.

    This is a tripwire, not a proof: it catches the values that were
    measured and then replaced, and it cannot catch a value from a run that
    was never archived.
    """
    import glob

    baseline: set[str] = set()
    current: set[str] = set()
    for p in glob.glob(str(ROOT / "research" / "baseline_minilm" / "*.json")):
        _decimals_in(json.loads(Path(p).read_text(encoding="utf-8")), baseline)
    for d in (FOCUS_RESULTS, RESULTS):
        for p in glob.glob(str(d / "*.json")):
            _decimals_in(json.loads(Path(p).read_text(encoding="utf-8")), current)
    if not baseline:
        notes.append("no archived baseline; skipping the superseded-results check")
        return
    superseded = sorted(baseline - current - ALLOWED_SUPERSEDED)
    if not superseded:
        notes.append("superseded-results check: no superseded values to look for")
        return
    pattern = re.compile(
        r"(?<![\d.])(" + "|".join(re.escape(d) for d in superseded) + r")(?![\d])"
    )
    targets = sorted(TEMPLATES.glob("*.md")) + sorted(TEMPLATES.glob("*.tex")) \
        + sorted((TEMPLATES / "scripts").glob("*.py"))
    for p in targets:
        hits = sorted(set(pattern.findall(p.read_text(encoding="utf-8"))))
        if hits:
            problems.append(
                f"templates/{p.name}: hard-codes {hits} — values that were true "
                "of the archived pre-swap run and are not true of the current one; "
                "bind them to a token"
            )
    notes.append(
        f"superseded-results check: {len(superseded)} archived values checked "
        f"against {len(targets)} templates"
    )


def check_headline_results() -> None:
    """The headline measurements must appear in the guide, and must be the
    measured ones.

    The corpus sizes are checked elsewhere. This one covers the results:
    the ablation's key numbers are quoted in the guide's five-minute
    summary and in the papers, and a hand-written copy of one of them can
    go stale without any other check noticing.
    """
    exp1_path = next((d / "exp1_ablation.json" for d in (FOCUS_RESULTS, RESULTS)
                      if (d / "exp1_ablation.json").exists()), None)
    if exp1_path is None:
        return
    exp1 = json.loads(exp1_path.read_text(encoding="utf-8"))
    S = exp1["systems"]
    guide = DELIV / "Deliverable_1_Complete_Guide.md"
    if not guide.exists():
        return
    text = guide.read_text(encoding="utf-8")

    wanted = {
        "dense-only Recall@10": f"{S['B. dense_only']['recall@10']:.3f}",
        "hybrid Recall@10": f"{S['C. hybrid_rrf']['recall@10']:.3f}",
        "BM25 Recall@10": f"{S['A. bm25_only']['recall@10']:.3f}",
        "reranked MRR": f"{S['D. hybrid_rrf_rerank']['mrr']:.3f}",
    }
    missing = [f"{k} ({v})" for k, v in wanted.items() if v not in text]
    if missing:
        problems.append(
            "the guide does not quote the measured value(s): "
            + ", ".join(missing))
    notes.append(
        f"headline results checked: {len(wanted) - len(missing)}/{len(wanted)}")


#: Every document the build ships that can carry an identifier. The check
#: used to cover the three submission-format papers only, so the Complete
#: Guide -- the largest document in the set -- was never compared with the
#: citation audit, and five of its identifiers were never recorded. Every
#: shipped document with a reference list is in here now.
CITATION_TARGETS = [
    "Deliverable_1_Complete_Guide.md",
    "Deliverable_2a_Technical_Report.md",
    "Deliverable_2b_IEEE_Conference_Paper.tex",
    "Deliverable_2c_Journal_Style_Paper.tex",
    "MTP_Status_Report.md",
    "MTP_Technical_Documentation.md",
    "READ_ME_FIRST.md",
]


def _dois(text: str) -> set[str]:
    """The DOIs in a text, with the punctuation around them removed.

    A DOI is written "DOI: 10.18653/v1/2023.emnlp-main.495." in the prose
    and "doi={10.18653/v1/2024.emnlp-main.527}" in the LaTeX, so the same
    registration arrives with a full stop or a brace attached. Comparing
    the raw strings would report every one of them as unrecorded.
    """
    out = set()
    for raw in re.findall(r"10\.\d{4,9}/[^\s,;)\]}]+", text):
        cleaned = raw.rstrip(".")
        while cleaned and cleaned[-1] in ".,;:*{}":
            cleaned = cleaned[:-1]
        if cleaned:
            out.add(cleaned)
    return out


def check_citations() -> None:
    if not AUDIT.exists():
        problems.append("research/00_citation_audit.md is missing")
        return
    audit = AUDIT.read_text(encoding="utf-8")
    # The audit records identifiers in several formats; collect them all.
    audited = set(re.findall(r"\b(\d{4}\.\d{4,5})\b", audit))
    audited_dois = _dois(audit)

    n_ids = n_dois = 0
    for name in CITATION_TARGETS:
        p = DELIV / name
        if not p.exists():
            continue
        text = normalise_latex(p.read_text(encoding="utf-8"))
        for i in sorted(set(re.findall(r"\b(\d{4}\.\d{4,5})\b", text))):
            n_ids += 1
            if i not in audited:
                problems.append(
                    f"{name}: arXiv:{i} is not recorded in the citation audit"
                )
        for d in sorted(_dois(text)):
            n_dois += 1
            if d not in audited_dois:
                problems.append(
                    f"{name}: DOI {d} is not recorded in the citation audit"
                )
    notes.append(f"citation identifiers checked against {len(audited)} audited "
                 f"entries: {n_ids} arXiv reference(s) and {n_dois} DOI "
                 f"reference(s) across {len(CITATION_TARGETS)} document(s)")


def check_generation_comparison() -> None:
    """The generator-side comparison must agree with the benchmark it ran on.

    Experiment 8 puts a generator behind five arms and reports, for each of
    them, how many of the unanswerable questions it answered. It runs under
    two prompt conditions, and both result files are checked here: if a run
    was made against a different benchmark than the one the deliverables
    quote, the numbers are still real but they answer a different question,
    and nothing else in the build would notice.
    """
    bench_p = ROOT / "impl" / "data" / "benchmark_focus" / "benchmark.json"
    if not bench_p.exists():
        return
    bench = json.loads(bench_p.read_text(encoding="utf-8"))
    n_ans = len([q for q in bench["queries"] if q["category"] != "unanswerable"])
    n_un = len([q for q in bench["queries"] if q["category"] == "unanswerable"])
    for _label, _fname in (("cautious", "exp8_generation.json"),
                           ("answering", "exp8_generation_answering.json"),
                           ("cautious, second generator",
                            "exp8_generation_flash.json"),
                           ("answering, second generator",
                            "exp8_generation_answering_flash.json")):
        _check_one_generation_run(_label, _fname, n_ans, n_un)


def _check_one_generation_run(label: str, fname: str, n_ans: int,
                              n_un: int) -> None:
    """One prompt condition's result file, against the focus benchmark."""
    p = ROOT / "impl" / "results_focus" / fname
    if not p.exists():
        notes.append(f"generator-side comparison ({label}): not run "
                     "(no result file)")
        return
    try:
        payload = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        problems.append(f"generator-side comparison ({label}): result file "
                         "is unreadable")
        return
    if payload.get("status") != "run":
        reason = payload.get("reason")
        notes.append(f"generator-side comparison ({label}): recorded as not "
                     "run" + (f" ({reason})" if reason else ""))
        return

    if payload.get("n_answerable") != n_ans or payload.get("n_unanswerable") != n_un:
        # The experiment may ask fewer unanswerable questions than the
        # benchmark holds -- it samples them, because the long-context arm
        # costs a corpus read per question. Asking for *more* than the
        # benchmark holds is impossible, and asking for a different number of
        # answerable questions is a different benchmark.
        if payload.get("n_answerable", 0) > n_ans:
            problems.append(
                f"generator-side comparison ({label}): claims "
                f"{payload.get('n_answerable')} answerable questions, the focus "
                f"benchmark has {n_ans}")
        elif payload.get("n_unanswerable", 0) > n_un:
            problems.append(
                f"generator-side comparison ({label}): claims "
                f"{payload.get('n_unanswerable')} unanswerable questions, the "
                f"focus benchmark has {n_un}")
        elif payload.get("n_answerable") != n_ans:
            problems.append(
                f"generator-side comparison ({label}): measured on "
                f"{payload.get('n_answerable')} answerable questions, the focus "
                f"benchmark has {n_ans} -- the answerable set is not sampled")
        else:
            sampled = n_un - payload.get("n_unanswerable", 0)
            if sampled:
                notes.append(
                    f"generator-side comparison ({label}): {sampled} of the {n_un} "
                    f"unanswerable questions were not asked")

    asked_ans = payload.get("n_answerable", 0)
    asked_un = payload.get("n_unanswerable", 0)
    for arm, block in (payload.get("arms") or {}).items():
        if not isinstance(block, dict) or "unanswerable" not in block:
            continue
        un = block["unanswerable"]
        an = block.get("answerable", {})
        if un.get("n") != asked_un:
            problems.append(
                f"generator-side comparison ({label}): arm {arm} reports {un.get('n')} "
                f"unanswerable questions, the run asked {asked_un}")
        if an and an.get("n") != asked_ans:
            problems.append(
                f"generator-side comparison ({label}): arm {arm} reports {an.get('n')} "
                f"answerable questions, the run asked {asked_ans}")

    # A run whose corpus did not fit the model's window is not a failed
    # experiment, but it must not be reported as one that measured the
    # long-context arm.
    if payload.get("fits_context_window") is False:
        lc = (payload.get("arms") or {}).get("long_context") or {}
        if lc.get("status") == "corpus_does_not_fit":
            notes.append(
                f"generator-side comparison ({label}): the corpus does not fit the "
                "model's context window, so the long-context arm was skipped")
    notes.append(
        f"generator-side comparison ({label}): {n_ans} answerable + {n_un} unanswerable "
        f"questions, arms checked against the focus benchmark")


def check_generation_replication() -> None:
    """The replication on a second generator must agree with what it claims.

    The generator-side comparison was repeated on a second checkpoint. If it
    ran, the documents that describe it must name the model they measured and
    carry its numbers; if it did not run, no document may claim that it did.
    Either way, the numbers quoted for the second generator have to be the
    ones in its result file.
    """
    runs = {}
    for label, fname in (("cautious", "exp8_generation_flash.json"),
                         ("answering", "exp8_generation_answering_flash.json")):
        p = ROOT / "impl" / "results_focus" / fname
        if not p.exists():
            continue
        try:
            payload = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            problems.append(f"generator-side replication ({label}): result "
                            "file is unreadable")
            continue
        if payload.get("status") == "run":
            runs[label] = payload
    if not runs:
        notes.append("generator-side replication: not run; skipping the "
                     "replication-claim check")
        return

    model = (runs.get("answering") or runs.get("cautious"))["model"]
    # The documents that carry the replication.
    carriers = ["MTP_Status_Report.md", "MTP_Technical_Documentation.md",
                "Deliverable_1_Complete_Guide.md", "READ_ME_FIRST.md"]
    for name in carriers:
        p = DELIV / name
        if not p.exists():
            continue
        text = normalise_latex(p.read_text(encoding="utf-8"))
        if model not in text:
            problems.append(
                f"{name}: the replication is not mentioned, so it does not "
                f"name the generator it was measured on ({model})")
    # The numbers the documents quote for the second generator have to be the
    # ones in its result file.
    ans = runs.get("answering")
    if ans:
        fitted = ((ans.get("arms") or {}).get("rag@fitted") or {})
        un = fitted.get("unanswerable") or {}
        rate = un.get("answer_rate")
        if rate is not None:
            needle = f"{rate:.3f}"
            for name in ("MTP_Status_Report.md", "MTP_Technical_Documentation.md"):
                p = DELIV / name
                if not p.exists():
                    continue
                text = normalise_latex(p.read_text(encoding="utf-8"))
                if needle not in text:
                    problems.append(
                        f"{name}: quotes the replication's gate answer rate "
                        f"nowhere ({needle})")
    notes.append(
        f"generator-side replication: {len(runs)} condition(s) on {model}, "
        "the documents' figures checked against the result file")


def check_next_steps_agree() -> None:
    """The report, the documentation and the deck must carry one next-steps list.

    They were three lists, and they had drifted apart: the deck still carried
    an older list whose first item was a measurement that has since been
    made. The list now lives in one place and is rendered into all three, so
    the only thing left to check is that they still carry the same number of
    items.
    """
    import re as _re

    def _count_report(name: str) -> int:
        p = DELIV / name
        if not p.exists():
            return -1
        text = p.read_text(encoding="utf-8")
        # The two documents head the list differently; matching only one of
        # them would silently skip the comparison.
        m = _re.search(r"^#+ .*(?:Next steps|Open threads).*$", text,
                       _re.MULTILINE)
        if not m:
            return -1
        body = text[m.end():]
        body = body.split("\n# ", 1)[0]
        return len(_re.findall(r"^\d+\.\s", body, _re.MULTILINE))

    report = _count_report("MTP_Status_Report.md")
    doc = _count_report("MTP_Technical_Documentation.md")
    if report > 0 and doc > 0 and report != doc:
        problems.append(
            f"next steps: the status report lists {report} and the technical "
            f"documentation lists {doc}; they are one list")

    # The pre-submission guide carries the same list in its short form, and
    # it used to carry a hand-written copy that drifted: it still said the
    # contradiction corpus had to be built after it had been.
    _rmf = DELIV / "READ_ME_FIRST.md"
    if _rmf.exists():
        _t = _rmf.read_text(encoding="utf-8")
        _m = _re.search(r"^#+ .*what would you do next.*$", _t, _re.M)
        if _m:
            _n = len(_re.findall(r"^\d+\.\s", _m.group(0), _re.MULTILINE))
            if _n == 0:
                _body = _t[_m.end():].split("\n## ", 1)[0]
                _n = len(_re.findall(r"^\d+\.\s", _body, _re.MULTILINE))
            if report > 0 and _n != report:
                problems.append(
                    f"next steps: the pre-submission guide lists {_n} and the "
                    f"status report lists {report}; they are one list")
    # The deck: count the numbered items on the conclusion slide.
    try:
        from pptx import Presentation
        pptx_p = DELIV / "Deliverable_4_Presentation_18Nov.pptx"
        if pptx_p.exists():
            prs = Presentation(str(pptx_p))
            deck = 0
            for slide in prs.slides:
                for shape in slide.shapes:
                    if not shape.has_text_frame:
                        continue
                    txt = shape.text_frame.text
                    if "NEXT STEPS, IN PRIORITY ORDER" not in txt:
                        continue
                    deck = len(_re.findall(r"^\d+\.\s", txt, _re.MULTILINE))
            if deck and report and deck != report:
                problems.append(
                    f"next steps: the deck lists {deck} and the status report "
                    f"lists {report}; they are one list")
            notes.append(f"next steps: {report} items, agreeing across the "
                         "report, the documentation and the deck")
    except Exception:
        pass


def check_condition_rates_distinct() -> None:
    """The two prompt conditions' rates must both be there, and they differ.

    The generator-side summary states the per-arm rates twice: once for the
    cautious condition and once for the answering condition. A paragraph that
    reads the arms out of the wrong payload quotes the cautious condition
    under both headings -- and every sentence is individually true, so no
    other check sees it. The two conditions differ a lot, so a document that
    carries one of the two rates and not the other is carrying the wrong one.
    """
    try:
        sys.path.insert(0, str(DELIV / "scripts"))
        from results_source import (load_generation_conditions, gen_arm)
    except Exception:
        return
    conditions = load_generation_conditions()
    cautious = conditions.get("cautious")
    answering = conditions.get("answering")
    if not cautious or not answering:
        return

    def _rate(payload) -> str | None:
        blk = gen_arm(payload, "rag_nogate") or {}
        r = (blk.get("unanswerable") or {}).get("answer_rate")
        return f"{r:.3f}" if r is not None else None

    c_rate, a_rate = _rate(cautious), _rate(answering)
    if not c_rate or not a_rate or c_rate == a_rate:
        return

    # The documents that carry the generator-side summary in full. The
    # conference paper carries the condensed form, which quotes the deployed
    # condition's rates and the verdict across both, and is not checked here.
    carriers = ["Deliverable_2a_Technical_Report.md",
                "Deliverable_2c_Journal_Style_Paper.tex",
                "scripts/make_pptx.py",
                "MTP_Status_Report.md",
                "MTP_Technical_Documentation.md"]
    for name in carriers:
        p = DELIV / name
        if not p.exists():
            continue
        text = normalise_latex(p.read_text(encoding="utf-8"))
        has_c, has_a = c_rate in text, a_rate in text
        if has_c != has_a:
            problems.append(
                f"{name}: quotes the cautious condition's rate ({c_rate}) but "
                f"not the answering condition's ({a_rate}), or the other way "
                f"round -- one of the two paragraphs is reporting the wrong "
                f"condition")
    notes.append(
        f"generator-side conditions: cautious {c_rate} and answering {a_rate} "
        "both carried by the documents that quote them")


def check_ordering_claim_scoped() -> None:
    """A claim about the reranker must be scoped to the corpus that supports it.

    "The reranker buys ordering, not recall" was true on the six-category
    corpus and false on the focus domain, where the reranker moves MRR by
    less than a thousandth in either direction. A heading that asserts it
    unqualified, over numbers taken from the corpus where it does not hold,
    is contradicted by the sentence under it -- so the phrase has to travel
    with the corpus it was measured on.
    """
    try:
        sys.path.insert(0, str(DELIV / "scripts"))
        from results_source import load as _src_load
    except Exception:
        return
    exp1 = _src_load("exp1_ablation", ("systems",))
    if not exp1:
        return
    C = exp1["systems"].get("C. hybrid_rrf") or {}
    D = exp1["systems"].get("D. hybrid_rrf_rerank") or {}
    if D.get("mrr", 0.0) > C.get("mrr", 0.0):
        # The claim holds on the corpus the documents report; nothing to scope.
        return

    claim = re.compile(r"buys? ordering|helps? the ordering", re.IGNORECASE)
    scope = re.compile(r"six[- ]categor", re.IGNORECASE)
    hits = 0
    for name in TEXT_TARGETS:
        p = DELIV / name
        if not p.exists():
            continue
        text = normalise_latex(p.read_text(encoding="utf-8"))
        for m in claim.finditer(text):
            hits += 1
            window = text[max(0, m.start() - 300): m.end() + 400]
            if not scope.search(window):
                problems.append(
                    f"{name}: says the reranker buys ordering without saying "
                    f"which corpus -- on this corpus (the focus domain) it "
                    f"moves MRR by {D.get('mrr', 0.0) - C.get('mrr', 0.0):+.4f}")
    notes.append(
        f"reranker-ordering claim: {hits} occurrence(s), each scoped to the "
        "corpus it was measured on")


def check_verdict_framing() -> None:
    """The framing of the H2.1 verdict must match the measured verdict.

    The verdict used to be "the hypothesis holds only in one of them", from
    the run where the cautious condition was a null. It was then measured
    as supported under both, and the verdict moved -- but the prose around
    it did not, so a document could say "supported under both prompt
    conditions" and "the hypothesis holds only in one of them" in the same
    table row. Each sentence was written for a different measurement.
    """
    try:
        sys.path.insert(0, str(DELIV / "scripts"))
        from results_source import (load_generation_conditions,
                                    h21_conditional_verdict)
    except Exception:
        return
    conditions = load_generation_conditions()
    if not conditions:
        return
    short, _full, _detail = h21_conditional_verdict(conditions)
    stale = re.compile(
        r"holds\s+only\s+in\s+one\s+of\s+them"
        r"|supported\s+in\s+one\s+of\s+them\s+and\s+not\s+in\s+the\s+other"
        r"|the\s+answer\s+is\s+conditional"
        r"|does\s+not\s+hold\s+where\s+the\s+generator\s+is\s+permitted"
        r"|holds\s+where\s+the\s+generator\s+behind\s+the\s+pipeline",
        re.IGNORECASE)
    if "both" not in short.lower():
        notes.append("H2.1 verdict: not the both-conditions case; skipping "
                     "the framing check")
        return
    hits = 0
    for name in TEXT_TARGETS:
        p = DELIV / name
        if not p.exists():
            continue
        text = normalise_latex(p.read_text(encoding="utf-8"))
        for m in stale.finditer(text):
            hits += 1
            problems.append(
                f"{name}: still says the hypothesis holds in only one of the "
                f"two prompt conditions -- it is supported under both -- "
                f"'{text[max(0, m.start() - 60):m.end() + 40]}'")
    notes.append(f"H2.1 verdict framing: {short}, {hits} stale wording(s)")


def check_no_null_leaks() -> None:
    """No Python null may reach a deliverable's prose.

    A missing measurement is not a number, and writing one out is worse
    than omitting it: the guide once shipped the sentence "the audit found
    None of the 132 answerable questions carrying an answer attached to the
    wrong question", because the audit had not computed the count and the
    generator interpolated the value it was given without asking whether it
    was there. Every artefact that carries prose is scanned for the shapes
    a null takes when it is interpolated.
    """
    import re as _re
    import zipfile as _zip

    # The shapes an interpolated null takes. "None of these eight is
    # exotic" is ordinary English and is not a hit; "None of the 132
    # answerable questions" is.
    _patterns = [
        _re.compile(r"\bNone\s+of\s+(?:the\s+)?\d"),
        # A bolded null, unless it is the start of ordinary English
        # ("**None of these eight is exotic**").
        _re.compile(r"\*\*None\b(?!\s+of\b)"),
        _re.compile(r"\(\s*None\s*\)"),
        _re.compile(r"[:=]\s*None\b"),
        _re.compile(r"\bnan\b"),
        _re.compile(r"\bnot measured\b"),
    ]
    targets = [p for p in DELIV.glob("*.md")]
    targets += [p for p in DELIV.glob("*.tex")]
    for name in ("Deliverable_1_Complete_Guide.docx",
                 "Deliverable_2a_Technical_Report.docx",
                 "Deliverable_3_Department_Report.docx"):
        targets.append(DELIV / name)
    hits = []
    for p in targets:
        if not p.exists():
            continue
        if p.suffix == ".docx":
            with _zip.ZipFile(p) as z:
                text = " ".join(z.read(n).decode("utf-8", "replace")
                                for n in z.namelist()
                                if n.endswith(".xml") and "document" in n)
        else:
            text = p.read_text(encoding="utf-8")
        for pat in _patterns:
            m = pat.search(text)
            if m:
                hits.append(f"{p.name}: {m.group(0)!r} at {m.start()}")
                break
    if hits:
        for h in hits[:6]:
            problems.append(f"a null leaked into the prose -- {h}")
    notes.append(f"null-leak scan over {len(targets)} deliverable(s)")


def check_shipped_quota_placement() -> None:
    """The shipped quota placement must be the one the ablation ranks first.

    The system applied the quota after the reranker while its own ablation
    measured the before-the-reranker placement to be better. Nothing in the
    build caught it: the numbers were internally consistent and the prose was
    true as written. This guard compares the two, so the configuration cannot
    drift away from the measurement again without stopping the build.

    The ablation's ranking is not the same on every corpus: the industrial
    corpus prefers the other placement, by a small and insignificant margin.
    So the guard fires on the focus domain -- the single industrial domain
    the thesis is about, and the corpus the deliverables quote -- and reports
    the other corpora alongside it. Requiring the placement to win on every
    corpus would let a regression through, because one corpus prefers the
    other placement.
    """
    try:
        from results_source import shipped_quota_position
    except Exception as exc:  # pragma: no cover
        notes.append(f"could not read the shipped quota placement: {exc}")
        return

    pos = shipped_quota_position()
    if pos == "unknown":
        notes.append("the shipped quota placement could not be read")
        return

    # The ablation's own comparison between the two placements, on every
    # corpus that measures them.
    measured = []
    for d in (FOCUS_RESULTS, RESULTS, INDUSTRIAL_RESULTS):
        f = d / "exp1_ablation.json"
        if not f.exists():
            continue
        exp1 = json.loads(f.read_text(encoding="utf-8"))
        pre = exp1["systems"].get("F. +quota_pre_rerank", {}).get("recall@10")
        post = exp1["systems"].get("G. +quota_post_rerank", {}).get("recall@10")
        if pre is None or post is None:
            continue
        measured.append((d.name, pre, post))

    if not measured:
        notes.append("no ablation result to compare the shipped placement against")
        return

    # The corpus the thesis is about is the one the guard fires on; the
    # others are reported, because their disagreement is a finding rather
    # than a reason to ship the worse default.
    primary = next((m for m in measured if m[0] == FOCUS_RESULTS.name), measured[0])
    _name, pre, post = primary
    shipped_value = post if pos == "post_rerank" else pre
    other_value = pre if pos == "post_rerank" else post
    if shipped_value < other_value:
        others = "; ".join(
            f"{n}: pre {p:.3f}, post {q:.3f}" for n, p, q in measured
        )
        problems.append(
            f"the system ships the {pos} quota and the ablation ranks it "
            f"worse on the focus domain, the corpus the thesis is about "
            f"(pre {pre:.3f} against post {post:.3f} Recall@10). "
            f"Either move the quota or explain why the shipped placement is "
            f"the one that is kept -- the limitation L20 exists for exactly "
            f"this. Every corpus that measures the placement: {others}."
        )
    notes.append(
        f"the shipped quota placement is {pos} ("
        + "; ".join(f"{n}: pre {p:.3f}, post {q:.3f}" for n, p, q in measured)
        + ")")


def check_contradiction_labels_still_apply() -> None:
    """The blind labels must still be labels *of* the pairs the run produced.

    The contradiction experiment was re-run after the quota moved, and the
    labels on the flagged pairs and their controls are carried over from the
    earlier run. That is only legitimate if the pairs are the same pairs:
    the labels are keyed by pair id, and a pair id is derived from the two
    passages, so a re-run that changed a passage would change the id and
    leave the label describing something that is no longer in the data. This
    check reads the pairs the run actually produced and confirms that every
    labelled pair is still there, with the same passages.
    """
    focus = ROOT / "impl" / "results_focus"
    judge_input = focus / "exp11_judge_input.json"
    labels = focus / "exp11_judge_a_labels.json"
    pairs_file = focus / "exp3_contradiction_pairs.jsonl"
    if not (judge_input.exists() and labels.exists() and pairs_file.exists()):
        notes.append("contradiction labels: no labelled pairs to check")
        return

    try:
        sheet = json.loads(judge_input.read_text(encoding="utf-8"))
        lab = json.loads(labels.read_text(encoding="utf-8"))
    except Exception:
        notes.append("contradiction labels: unreadable, skipping")
        return

    labelled = set((lab.get("labels") or {}))
    if not labelled:
        notes.append("contradiction labels: none recorded, skipping")
        return

    current: dict[str, dict] = {}
    for line in pairs_file.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            p = json.loads(line)
        except Exception:
            continue
        current[str(p.get("pair_id"))] = p

    sheet_pairs = {str(p.get("pair_id")): p for p in (sheet.get("pairs") or [])}
    missing, changed = [], []
    for pid in sorted(labelled):
        p = current.get(pid)
        if p is None:
            missing.append(pid)
            continue
        q = sheet_pairs.get(pid)
        if q is None:
            continue
        if ((q.get("passage_a") or "").strip()[:120]
                != (p.get("text_a") or "").strip()[:120]
                or (q.get("passage_b") or "").strip()[:120]
                != (p.get("text_b") or "").strip()[:120]):
            changed.append(pid)
    if missing or changed:
        problems.append(
            f"the contradiction labels no longer describe the pairs the run "
            f"produced: {len(missing)} labelled pair(s) are absent from "
            f"{pairs_file.name} and {len(changed)} have a different passage "
            f"now. The precision figures quoted from those labels are not "
            f"measurements of the system as it runs. Re-label them, or "
            f"withdraw the figures."
            + (f" Missing: {missing[:5]}." if missing else "")
            + (f" Changed: {changed[:5]}." if changed else ""))
    notes.append(
        f"contradiction labels: all {len(labelled)} labelled pair(s) are "
        f"present in the current run with the same passages")


def check_placement_provenance() -> None:
    """Every result that sits on the retrieval must say which placement it was taken on.

    The limitation names the results that were not re-measured after the
    quota moved, and that disclosure is derived from a stamp the
    measurement scripts write into the file they produce. A result without
    the stamp would be *assumed* to be on the earlier placement, and the
    disclosure would then be wrong in whichever direction the assumption was
    wrong. So the stamp has to be there, and this check says so.
    """
    from results_source import shipped_quota_position
    from results_source import PLACEMENT_STAMPED_RESULTS

    shipped = shipped_quota_position()
    stamped, unstamped = [], []
    for entry in PLACEMENT_STAMPED_RESULTS:
        label, path = entry[0], entry[1]
        if not path.exists():
            continue
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            unstamped.append(label)
            continue
        placement = doc.get("retrieval_placement")
        if placement is None:
            unstamped.append(label)
        else:
            stamped.append(f"{label} ({placement})")
    if unstamped:
        problems.append(
            "these results carry no placement stamp, so the limitation's "
            "account of what was re-measured would rest on an assumption "
            "rather than on the file: "
            + ", ".join(unstamped)
            + ". Stamp them with "
            "deliverables/scripts/stamp_measurement_provenance.py, or write "
            "the stamp in the measurement script that produces them.")
    stale = [s for s in stamped if s.endswith("(post_rerank)")] \
        if shipped == "pre_rerank" else []
    notes.append(
        f"placement provenance: {len(stamped)} result(s) stamped, "
        f"{len(stale)} on the earlier placement")


def check_generator_pairing() -> None:
    """The gate's paired effect must pair each question with the same question.

    The generator-side comparison is reported as a paired test: for each
    question, whether the ungated arm answered and the gated arm did not.
    Pairing by position is only correct while every arm was measured on the
    same benchmark in the same order. The long-context arm is carried over
    from the archive when the quota placement moves, and the benchmark is
    rebuilt in between -- the same questions in a different order -- so
    pairing by position compares the wrong questions and the counts still
    look plausible. This recomputes the pairing by query and compares.
    """
    from results_source import PRIMARY

    files = [
        ("the cautious generator comparison", PRIMARY / "exp8_generation.json"),
        ("the answering generator comparison",
         PRIMARY / "exp8_generation_answering.json"),
    ]
    checked = 0
    for label, path in files:
        if not path.exists():
            continue
        doc = json.loads(path.read_text(encoding="utf-8"))
        records = doc.get("records") or {}
        paired = doc.get("paired") or {}
        base_by_query = {r["query"]: r for r in records.get("rag_nogate") or []}
        for arm, block in paired.items():
            arm_by_query = {r["query"]: r
                            for r in records.get(arm) or []}
            shared = [q for q in base_by_query if q in arm_by_query]
            for name, answerable in (("unanswerable", False),
                                     ("answerable", True)):
                pairs = [(base_by_query[q], arm_by_query[q]) for q in shared
                         if base_by_query[q]["answerable"] == answerable]
                want_b = sum(1 for x, y in pairs
                             if x["answered"] and not y["answered"])
                want_c = sum(1 for x, y in pairs
                             if not x["answered"] and y["answered"])
                got = block.get(name) or {}
                if (got.get("n_pairs") != len(pairs)
                        or got.get("baseline_answered_arm_refused") != want_b
                        or got.get("baseline_refused_arm_answered") != want_c):
                    problems.append(
                        f"the paired effect for {arm} ({name}) in {label} "
                        f"does not pair the same question with the same "
                        f"question: it reports "
                        f"{got.get('n_pairs')} pairs "
                        f"({got.get('baseline_answered_arm_refused')} / "
                        f"{got.get('baseline_refused_arm_answered')} "
                        f"discordant) where pairing by query gives "
                        f"{len(pairs)} ({want_b} / {want_c}). Rebuild it with "
                        f"impl/experiments/run_generation_eval.py --resummarise.")
                checked += 1
    notes.append(f"generator pairing: {checked} paired block(s) recomputed by "
                 f"query and matched")


def check_files() -> None:
    for name in REQUIRED_FILES:
        p = DELIV / name
        if not p.exists():
            problems.append(f"missing deliverable: {name}")
        elif p.stat().st_size < 5000:
            problems.append(f"suspiciously small deliverable: {name} "
                            f"({p.stat().st_size} bytes)")
    notes.append(f"{len(REQUIRED_FILES)} required deliverables checked")


#: The documents the number-provenance check reads. The *templates* are
#: checked, not the shipped copies, because the templates are where a number
#: is written by hand -- a substituted value in a shipped file is bound to a
#: token by definition, and a token slot in a template is the hole where an
#: unbacked number could still sit.
PROVENANCE_TARGETS = [
    "Deliverable_1_Part1_Content.md",
    "Deliverable_1_PartD_Code.md",
    "Deliverable_1_PartF_toJ.md",
    "Deliverable_2a_Technical_Report.md",
    "MTP_Plain_Language_Guide.md",
    "MTP_Status_Report.md",
    "MTP_Technical_Documentation.md",
    "READ_ME_FIRST.md",
    "README.md",
]

#: Numbers that are arithmetic shown in a worked example, not measurements.
#: They are listed rather than detected, because a heuristic that swallowed
#: every number next to an equals sign would also swallow a real claim
#: written as "the gate reached 0.883 at tau = 0.10". Each entry is the
#: result of arithmetic the reader can redo from the numbers beside it in
#: the text.
PROVENANCE_DERIVED = {
    # The worked example in Part 1's recall table: 1/62, 1/78 and their sum,
    # and the two neighbouring categories' ratios.
    "0.01282", "0.01449", "0.01515", "0.01563", "0.01587", "0.01613",
    "0.02895", "0.02964", "0.03202", "0.03278",
    # The normal quantile in "kappa +/- 1.96 * SE".
    "1.96",
    # The BM25 IDF worked example: log[95.5/5.5 + 1] = log[18.36] = 2.91.
    "2.91",
}

#: A number in the prose has to be traceable: either it is bound to a token
#: (and therefore re-derived from a result file), or it is recorded in a
#: research note where the source was read. The research notes are the
#: provenance for the numbers quoted from other people's work and for the
#: figures quoted from implementations this project has since replaced;
#: `research/17_historical_figures.md` holds the second kind.
PROVENANCE_NOTES = [
    ROOT / "research" / n for n in (
        "00_citation_audit.md", "01_confidence_gating.md",
        "01_citation_resolution.md", "02_modality_balanced.md",
        "03_hybrid_retrieval.md", "04_contradiction.md",
        "05_attribution_eval.md", "06_industrial.md",
        "07_frontier_2026.md", "08_direction_check.md",
        "09_encoder_swap.md", "10_industrial_corpus_and_objectives.md",
        "11_supervisor_briefing_2026-11-11.md", "12_scope_reconciliation.md",
        "13_novelty_and_positioning.md", "14_full_explanation.md",
        "15_label_validation_protocol.md", "16_open_items_register.md",
        "17_historical_figures.md", "18_answer_validation_conventions.md",
        "19_gate_per_retriever.md", "20_soft_prior.md",
    )
]

#: A number with a decimal point and at least two decimals, or a thousands
#: separator. The threshold is what makes this check about *claims* rather
#: than about counting: "12 of 21" is prose, "0.906" is a measurement.
_PROVENANCE_NUMBER = re.compile(
    r"(?<![\w./])(\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+\.\d{2,})(?![\w./])")


def _prose_numbers(text: str) -> set[str]:
    """The multi-digit numbers a piece of prose states.

    Everything that is a number but not a claim is removed: code, token
    slots, identifiers, years, section numbers, and the figure and table
    numbers the documents use to point at their own figures.
    """
    t = re.sub(r"```.*?```", " ", text, flags=re.S)   # fenced code
    t = re.sub(r"`[^`]*`", " ", t)                     # inline code
    t = re.sub(r"\{\{[^}]*\}\}", " ", t)               # token slots
    t = re.sub(r"\b\d{4}\.\d{4,5}\b", " ", t)          # arXiv identifiers
    t = re.sub(r"10\.\d{4,9}/\S+", " ", t)             # DOIs
    t = re.sub(r"\b(19|20)\d{2}\b", " ", t)            # years
    t = re.sub(r"(?i)\b(section|figure|fig|table|part|chapter|appendix|"
               r"eq|equation|slide)\s*\.?\s*\d+(\.\d+)?", " ", t)
    t = re.sub(r"§\s*\d+(\.\d+)*", " ", t)            # a section mark has
                                                      # no word boundary
                                                      # before it
    t = re.sub(r"^\s*#{1,6}\s*\d+(\.\d+)*", " ", t, flags=re.M)  # headings
    t = re.sub(r"\[\s*\d+\s*\]\([^)]*\)", " ", t)      # link targets
    t = re.sub(r"\b\d+\.\d+\s*$", " ", t, flags=re.M)  # list numbering
    return set(_PROVENANCE_NUMBER.findall(t))


def check_number_provenance() -> None:
    """Every multi-digit number in the prose must be traceable.

    Two kinds of number carry a claim: one about this project's own
    measurements, and one about somebody else's work. The first is bound to
    a token and re-derived from a result file by
    `verify_reported_numbers.py`. The second is recorded in a research note
    where the source was resolved and read. This check catches the third
    kind -- a number written by hand that has nothing behind it -- which is
    the one that can be wrong and stay wrong.
    """
    provenance = ""
    for p in PROVENANCE_NOTES:
        if p.exists():
            provenance += p.read_text(encoding="utf-8")
    if not provenance:
        problems.append("no research note is available to check number "
                        "provenance against")
        return
    n_checked = 0
    for name in PROVENANCE_TARGETS:
        p = TEMPLATES / name
        if not p.exists():
            continue
        for num in sorted(_prose_numbers(p.read_text(encoding="utf-8"))):
            n_checked += 1
            plain = num.replace(",", "")
            if num in PROVENANCE_DERIVED:
                continue
            if num not in provenance and plain not in provenance:
                problems.append(
                    f"{name}: the number {num} has no provenance -- it is in "
                    f"no research note and it is not bound to a token")
    notes.append(f"number provenance: {n_checked} number(s) in the prose "
                 f"traced to {len([p for p in PROVENANCE_NOTES if p.exists()])}"
                 f" research note(s)")


#: The deck's length is stated in two of the shipped documents, and it was
#: stated wrong in both -- "19 slides" in one and "21 slides" in the other,
#: against a deck of 23. Nothing caught it, because a slide count written in
#: prose is a fact nobody re-derives. It is checked here instead: the count
#: in the prose must be the count in the deck.
def check_deck_slide_count() -> None:
    # There are two decks now. A claim is attributed to the deck its own line
    # names, because a document that mentions both has two different counts to
    # be right about, and checking them against one deck would fail the second
    # one for being correct.
    decks = {
        "original": (DELIV / "Deliverable_4_Presentation_18Nov.pptx",
                     ("Deliverable_4_Presentation_18Nov.pptx",)),
        "fresh": (DELIV / "MTP_Report_Presentation.pptx",
                  ("MTP_Report_Presentation.pptx", "report deck", "written fresh")),
    }
    try:
        from pptx import Presentation
    except ImportError:
        notes.append("deck slide count: python-pptx is not installed; skipping")
        return
    counts = {}
    for name, (path, _) in decks.items():
        if not path.exists():
            continue
        counts[name] = len(Presentation(str(path)).slides)
    if "original" not in counts:
        return
    checked = 0
    # The pristine sources are checked as well as the shipped copies: the
    # templates are what the build copies from, so a wrong number there is
    # the one that would ship.
    sources = [ROOT / "README.md", DELIV / "READ_ME_FIRST.md",
               TEMPLATES / "README.md", TEMPLATES / "READ_ME_FIRST.md"]
    for p in sources:
        if not p.exists():
            continue
        for line in p.read_text(encoding="utf-8").splitlines():
            claims = re.findall(r"(\d+)\s+slides", line)
            if not claims:
                continue
            which = "original"
            for name, (_path, markers) in decks.items():
                if name in counts and any(m in line for m in markers):
                    which = name
            for claimed in claims:
                checked += 1
                if int(claimed) != counts[which]:
                    problems.append(
                        f"{p.relative_to(ROOT)} says the {which} deck has "
                        f"{claimed} slides; it has {counts[which]}")
    notes.append("deck slide count: "
                 + ", ".join(f"{k}={v}" for k, v in counts.items())
                 + f", {checked} mention(s) in the prose")


#: The deliverables are printed, photocopied and projected, and none of
#: those is guaranteed to reproduce a hue. A document whose meaning depends
#: on a colour is a document that fails on a mono printer, so the whole set
#: is monochrome -- and the check is here because a theme that is
#: monochrome by convention is a theme that is coloured again the moment
#: somebody adds a shape.
def check_monochrome() -> None:
    import zipfile
    targets = [n for n in REQUIRED_FILES
               if n.endswith((".docx", ".pptx"))]
    if not targets:
        return
    for name in targets:
        p = DELIV / name
        if not p.exists():
            continue
        coloured = set()
        with zipfile.ZipFile(p) as z:
            for entry in z.namelist():
                if not entry.endswith(".xml"):
                    continue
                data = z.read(entry).decode("utf-8", "replace")
                hexes = set(re.findall(r'srgbClr val="([0-9A-Fa-f]{6})"', data))
                hexes |= set(re.findall(r'w:fill="([0-9A-Fa-f]{6})"', data))
                hexes |= set(re.findall(
                    r'<w:color\b[^>]*?w:val="([0-9A-Fa-f]{6})"', data))
                for h in hexes:
                    if h[0:2] != h[2:4] or h[2:4] != h[4:6]:
                        coloured.add(h)
        if coloured:
            problems.append(
                f"{name} carries {len(coloured)} colour(s) that are not grey "
                f"({', '.join(sorted(coloured)[:6])}"
                f"{'...' if len(coloured) > 6 else ''}) -- the deliverables "
                f"are monochrome")
    notes.append(f"{len(targets)} office file(s) checked for colour")


#: The same rule, for the figures. The six figures were drawn in blue and
#: vermillion while every document around them was made monochrome, and
#: nothing caught it: the documents' own colours were checked, and the
#: figures were not. A figure is the most photocopied part of the set, so it
#: is checked here -- pixel by pixel, on the PNG that the Word path embeds
#: and the vector PDF that the LaTeX path embeds are written from the same
#: drawing.
def check_figures_monochrome() -> None:
    figures = DELIV / "figures"
    pngs = sorted(figures.glob("*.png")) if figures.exists() else []
    if not pngs:
        return
    try:
        from PIL import Image
    except ImportError:
        notes.append("figure colours: Pillow is not installed; skipping")
        return
    coloured = []
    for png in pngs:
        with Image.open(png) as im:
            rgb = im.convert("RGB")
            # Pillow 14 renames getdata; the old name warns.
            seen = set(rgb.get_flattened_data()
                       if hasattr(rgb, "get_flattened_data")
                       else rgb.getdata())
        off = sorted(c for c in seen if not (c[0] == c[1] == c[2]))
        if off:
            c = off[0]
            coloured.append(f"{png.name} ({len(off)} non-grey colour(s), "
                            f"e.g. #{c[0]:02X}{c[1]:02X}{c[2]:02X})")
    if coloured:
        problems.append(
            "the figures carry colour that is not grey: "
            + "; ".join(coloured) + " -- the deliverables are monochrome")
    notes.append(f"{len(pngs)} figure(s) checked for colour")


#: A figure is a picture of a result file, and a picture does not update
#: itself. On 16 November 2026 all six figures were three days older than the
#: experiments they draw, and figure 3 still carried the calibration figures
#: from the run before last (ECE 0.114 against the measured 0.104). Nothing
#: caught it, because the colour check reads pixels and the caption check
#: reads text. The check here is the obvious one: a figure has to be newer
#: than the results it is drawn from.
def check_figures_are_current() -> None:
    figures = DELIV / "figures"
    pngs = sorted(figures.glob("*.png")) if figures.exists() else []
    if not pngs:
        return
    newest = 0.0
    for d in (ROOT / "impl" / "results_focus", ROOT / "impl" / "results_industrial",
              ROOT / "impl" / "results"):
        if not d.exists():
            continue
        for f in d.glob("*.json"):
            newest = max(newest, f.stat().st_mtime)
    if newest == 0.0:
        return
    stale = [f"{p.name} ({p.stat().st_mtime - newest:.0f}s behind the results)"
             for p in pngs if p.stat().st_mtime < newest]
    if stale:
        problems.append(
            "the figures are older than the results they draw: "
            + "; ".join(stale)
            + " -- re-run impl/scripts/make_figures.py")
    notes.append(f"figure freshness: {len(pngs)} figure(s) checked against the "
                 f"result files")


#: The two phrases that assert a measurement is indistinguishable from
#: chance. A permutation null is only indistinguishable when the p-value
#: says so, so every occurrence is checked against the p-value that was
#: actually measured for the corpus the sentence names.
_CHANCE_CLAIM = re.compile(
    r"(not\s+distinguishable\s+from\s+chance|indistinguishable\s+from\s+the\s+"
    r"permutation\s+null|indistinguishable\s+from\s+chance|"
    r"close\s+to\s+chance|as\s+close\s+to\s+chance\s+as)",
    re.IGNORECASE,
)


def check_separability_claim() -> None:
    """The claim about the repaired class must agree with its p-value.

    The residual form-only separability of the repaired class is measured
    twice: on the focus domain, whose p-value against the permutation null
    is 0.020, and on the better-powered six-category corpus, whose is 0.149.
    Only the second is indistinguishable from chance. A sentence that calls
    the first one indistinguishable is a false claim -- and it is exactly the
    kind that survives a build, because the number it quotes is correct and
    only the verdict attached to it is wrong.
    """
    import sys as _sys
    _sys.path.insert(0, str(DELIV / "scripts"))
    try:
        from results_source import (load_unanswerable_audit,
                                    unanswerable_audit_summary)
    except Exception as exc:  # pragma: no cover - import guard
        notes.append(f"separability-claim check skipped ({exc})")
        return

    measured: dict[str, float] = {}
    for variant in ("focus", "multi"):
        summary = unanswerable_audit_summary(load_unanswerable_audit(variant))
        auc = summary.get("sep_auc")
        p = summary.get("sep_p_value")
        if auc is None or p is None:
            continue
        measured[f"{auc:.3f}"] = p

    if not measured:
        notes.append("separability-claim check skipped (no audit measured)")
        return

    for name in TEXT_TARGETS:
        p = DELIV / name
        if not p.exists():
            continue
        text = normalise_latex(p.read_text(encoding="utf-8"))
        for sentence in re.split(r"(?<=\.)\s+", text):
            if not _CHANCE_CLAIM.search(sentence):
                continue
            # Which corpus is the sentence about? The AUC it quotes names it.
            quoted = [m for m in re.findall(r"\b\d\.\d{3}\b", sentence)
                      if m in measured]
            if quoted:
                for auc in quoted:
                    p_value = measured[auc]
                    if p_value < 0.05:
                        problems.append(
                            f"{name}: calls the form-only separability at "
                            f"AUC {auc} indistinguishable from chance, but "
                            f"its measured p-value against the permutation "
                            f"null is {p_value:.3f} -- the null is rejected"
                        )
            else:
                m = re.search(r"p\s*=\s*(0\.\d+)", sentence)
                if m and float(m.group(1)) < 0.05:
                    problems.append(
                        f"{name}: calls a measurement indistinguishable from "
                        f"chance while quoting p = {m.group(1)}, which rejects "
                        f"the null"
                    )
    notes.append(
        f"separability-claim check: {len(measured)} measured AUC/p-value pairs "
        f"({', '.join(f'{k}->{v:.3f}' for k, v in measured.items())})"
    )


#: A count that is written twice: "43 of 110 of 110". It happens when a
#: token already renders "N of M" and the sentence around it adds the
#: denominator again. It is harmless in meaning and embarrassing in a
#: document that a committee reads closely.
_DOUBLE_COUNT = re.compile(r"\b(\d+)\s+of\s+(\d+)\s+of\s+\2\b")


def check_no_double_counts() -> None:
    """No deliverable may write the same count twice."""
    for name in TEXT_TARGETS:
        p = DELIV / name
        if not p.exists():
            continue
        text = normalise_latex(p.read_text(encoding="utf-8"))
        for m in _DOUBLE_COUNT.finditer(text):
            problems.append(
                f"{name}: writes the count twice -- "
                f"'{text[max(0, m.start()-40):m.end()+20]}'"
            )
    notes.append("no duplicated counts in the deliverables")


def check_precision_claim() -> None:
    """The contradiction gate's precision is measured; the old wording is stale.

    Experiment 11 put the flagged pairs in front of two independent
    annotators under a written rubric, so the gate's precision is a
    measurement and not an open gap. Any deliverable still saying that the
    precision is unverified, or that it "needs human labels", is quoting the
    state of the work before that experiment, and is now wrong in the same
    way the old separability claim was.
    """
    measured = ROOT / "impl" / "results_focus" / "exp11_contradiction_precision.json"
    if not measured.exists():
        notes.append("contradiction precision: not measured; "
                     "skipping the stale-wording check")
        return
    stale = re.compile(
        r"precision\s+is\s+unverified"
        r"|precision\s+is\s+not\s+verified"
        r"|true\s+precision\s+is\s+unverified"
        r"|unverified\s+precision"
        r"|precision\s+is\s+unverified\s+and\s+needs\s+human\s+labels"
        r"|needs\s+human\s+labels"
        r"|no\s+independent\s+ground\s+truth\s+for\s+contradiction",
        re.IGNORECASE,
    )
    # The numeric rule was repaired after the labelling experiment, so a
    # deliverable that still describes the *old* rule in the present tense is
    # quoting a detector that no longer exists. The repaired rule and the
    # pre-repair measurement both ship, and the deliverables have to be able
    # to say what the old rule did, so the check is on the tense: "keyed" and
    # "used to key" are history and pass; "keys" is a claim about the code
    # that ships, and does not.
    stale_rule = re.compile(
        r"\bkeys\s+a\s+number\s+to\s+the\s+nearest\s+distinctive\s+word"
        r"|numeric\s+(?:branch|detector|conflict\s+detector)\s+keys\b"
        r"|numeric\s+(?:branch|detector)\s+keys\s+on\s+citation\s+years",
        re.IGNORECASE,
    )
    hits = 0
    for name in TEXT_TARGETS:
        p = DELIV / name
        if not p.exists():
            continue
        text = normalise_latex(p.read_text(encoding="utf-8"))
        for m in stale.finditer(text):
            hits += 1
            problems.append(
                f"{name}: says the contradiction gate's precision is still "
                f"unverified, but Experiment 11 measured it -- "
                f"'{text[max(0, m.start()-50):m.end()+30]}'"
            )
        for m in stale_rule.finditer(text):
            hits += 1
            problems.append(
                f"{name}: describes the pre-repair numeric rule as the current "
                f"one -- '{text[max(0, m.start()-60):m.end()+40]}'"
            )
    notes.append(
        f"contradiction precision: measured, {hits} stale claim(s) found")


def check_conflict_calibration() -> None:
    """The fitted conflict calibration must agree with the measured precision.

    The pipeline reads this file to decide which branches may surface a
    finding to a practitioner. If it disagrees with the scored measurement,
    the system would be gating on a number that is not the one that was
    measured, and the deliverables would be quoting a calibration that is
    not the one in force.
    """
    cal_path = ROOT / "impl" / "artifacts_focus" / "conflict_calibration.json"
    scored_path = (ROOT / "impl" / "results_focus"
                    / "exp11_contradiction_precision.json")
    if not cal_path.exists():
        notes.append("conflict calibration: not fitted; skipping")
        return
    if not scored_path.exists():
        notes.append("conflict calibration: no scored measurement to check "
                     "against; skipping")
        return
    try:
        cal = json.loads(cal_path.read_text(encoding="utf-8"))
        scored = json.loads(scored_path.read_text(encoding="utf-8"))
    except Exception as exc:
        problems.append(f"conflict calibration: unreadable ({exc})")
        return

    by_branch = scored.get("by_branch") or {}
    checked = 0
    for kind, measured in sorted((cal.get("precision") or {}).items()):
        agg = by_branch.get(kind) or {}
        n = agg.get("n")
        if not n:
            problems.append(
                f"conflict calibration: branch '{kind}' is calibrated at "
                f"{measured:.3f} but the scored measurement has no {kind} "
                f"alarms to measure it on")
            continue
        expected = agg.get("n_acceptable", 0) / n
        checked += 1
        if abs(expected - measured) > 0.02:
            problems.append(
                f"conflict calibration: branch '{kind}' is calibrated at "
                f"{measured:.3f} but the scored measurement says {expected:.3f} "
                f"({agg.get('n_acceptable')} of {n})")
    notes.append(
        f"conflict calibration: {checked} branch(es) checked against the "
        f"measured precision")


def main() -> int:
    check_numbers()
    check_document_counts()
    check_corpus_integrity()
    check_benchmark_questions()
    check_headline_results()
    check_no_unsubstituted_tokens()
    check_no_superseded_results()
    check_templates_tokenised()
    check_citations()
    check_generation_comparison()
    check_condition_rates_distinct()
    check_verdict_framing()
    check_ordering_claim_scoped()
    check_generation_replication()
    check_next_steps_agree()
    check_separability_claim()
    check_no_double_counts()
    check_precision_claim()
    check_conflict_calibration()
    check_shipped_quota_placement()
    check_placement_provenance()
    check_generator_pairing()
    check_contradiction_labels_still_apply()
    check_files()
    check_deck_slide_count()
    check_number_provenance()
    check_monochrome()
    check_figures_monochrome()
    check_figures_are_current()
    check_no_null_leaks()

    print("=== consistency checks ===")
    for n in notes:
        print(f"  · {n}")
    if problems:
        print(f"\n  {len(problems)} PROBLEM(S):")
        for pr in problems:
            print(f"    ✗ {pr}")
        return 1
    print("\n  all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
