#!/usr/bin/env python3
"""Audit the answer side: the benchmark's answerable labels, and how much of
Experiment 8's answer-side result survives a stricter reading.

**Part 1 -- defective labels.** The answer-side accuracy reported by
Experiment 8 is measured against a silver-standard label: the answer string
is copied out of the gold chunk mechanically when the benchmark is built. That
label can be wrong in a way that is invisible in the retrieval metrics,
because the *gold chunk* is still the right chunk -- only the answer string
is attached to the wrong question. Two ways this happened in
`scripts/build_benchmark.py`:

  1. Table questions. The generator walked the header cells of a markdown
     table and, for column k, took the key from row[k] and the answer from
     row[k+1] -- but named the question with header[k]. The question therefore
     asked for the column the *key* came from, while the gold answer was the
     next column's value. "What is the DPMO for 691,462?" was answered "69%",
     which is the percent-defective column.

  2. Numeric-prefix golds. A numeric answer was taken as a digit prefix of a
     longer token in the chunk: "3" out of "3PL", "6" out of "6.8".

Both were found by this audit and both were corrected in the builder. The
generator now names the column the *answer* comes from, and a numeric gold
that is only ever a prefix of a longer token is not generated at all. The
benchmark was rebuilt and every experiment re-measured against it, so the
numbers reported throughout this project are post-repair.

The audit still runs, because an instrument that is not re-checked is not an
instrument. What it reports now is the *residual*: how many labels are still
defective. That number is small, and the checks below are precise rather
than conservative -- a hit is a defect only when the gold genuinely is not
stated by the chunk, not merely when some other token in the chunk happens
to begin with the same characters.

**Part 2 -- how much survives.** Experiment 8's accuracy column uses one
entailment test over the whole answer. A whole-corpus prompt produces longer
answers than a ten-chunk prompt, and entailment against a short gold answer
is easier to fail when the hypothesis is embedded in more text. So the
audit re-scores the retrieval arm against the long-context arm three ways:
the whole answer, the first sentence only (length-controlled), and a lexical
key-term test that ignores length. If the gap holds under all three it is a
quality difference; if it only holds under the first, it is partly an
artefact of how the answer was scored.
"""
from __future__ import annotations

import json
import os
import re
import sys
from math import comb
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

from common import load_benchmark, load_index  # noqa: E402
from src.config import RESULTS_DIR  # noqa: E402


def parse_table(chunk: str):
    """(headers, rows) for a markdown table chunk, or None."""
    rows = []
    for line in chunk.split("\n"):
        if line.startswith("|") and line.count("|") >= 2:
            rows.append([c.strip() for c in line.strip().strip("|").split("|")])
    if len(rows) < 3:
        return None
    if not all(set(c) <= set("-: ") for c in rows[1]):
        return None
    return rows[0], rows[2:]


def _stated_as_token(gold: str, chunk: str) -> bool:
    """Does the chunk state this value as a complete token?

    A value is stated when the chunk contains it and what follows it is not
    part of the same token. The test is deliberately ASCII: a Greek sigma
    after a number is a unit ("6 sigma"), whereas an ASCII letter makes a
    different token ("3PL"). "6" out of "6.8" is not the value; "1" out of
    "1 faulty channel" is.
    """
    core = gold.rstrip("%")
    pat = re.compile(r"(?<![A-Za-z0-9.])" + re.escape(core) + r"(?![A-Za-z0-9.])")
    return bool(pat.search(chunk))


def table_defect(query: str, gold: str, chunk: str) -> bool:
    """Is the gold attached to the wrong column of the wrong row?

    The question names the column the answer should come from and gives the
    key that identifies the row. The label is sound when some row of the
    table carries the key in a cell and the gold in the very next cell, under
    the column the question names.

    The earlier, conservative form of this test looked for the row whose
    *named* column held the key, which fires when the same value appears in
    more than one column of the table and picks the wrong row. That was a
    false positive, and the test above does not make it.
    """
    m = re.search(r"what is the (.+?) for (.+?)\??$", query)
    if not m:
        return False
    named, key = m.group(1).strip(), m.group(2).strip()
    t = parse_table(chunk)
    if not t:
        return False
    headers, rows = t
    hl = [h.strip().lower() for h in headers]
    if named.lower() not in hl:
        return False
    ci = hl.index(named.lower())
    n = len(headers)
    for row in rows:
        cells = [c.strip() for c in row]
        if len(cells) != n:
            continue
        for k in range(len(cells)):
            d = (k + 1) % n
            if d != ci:
                continue
            if (cells[k].strip().lower() == key.lower()
                    and cells[d].strip().lower() == gold.lower()):
                return False
    return True


def numeric_prefix_defect(gold: str, chunk: str) -> bool:
    """Is the gold only ever a prefix of a longer token in the chunk?

    The conservative form of this test fires whenever the gold's digits
    begin some other token in the chunk -- "1" inside "1oo1" -- which is not
    the same as the gold being wrong. What makes a gold defective is that the
    chunk never states it as a complete token.
    """
    if not re.fullmatch(r"\d+(\.\d+)?%?", gold):
        return False
    return not _stated_as_token(gold, chunk)


def table_defect_screen(query: str, gold: str, chunk: str) -> bool:
    """The conservative screen the original audit used.

    It asks whether the question names a column the gold does not come
    from, and it finds the row by looking for the key under the *named*
    column. That is the wrong row whenever the same value appears in more
    than one column, so the screen over-reports -- which is the right
    direction for a screen and the wrong direction for a count. It is kept
    because it is the instrument that found the defect, and because the
    pre-repair benchmark is audited with it, so the historical counts stay
    reproducible.
    """
    m = re.search(r"what is the (.+?) for (.+?)\??$", query)
    if not m:
        return False
    named, key = m.group(1).strip(), m.group(2).strip()
    t = parse_table(chunk)
    if not t:
        return False
    headers, rows = t
    hl = [h.lower() for h in headers]
    if named.lower() not in hl:
        return False
    ci = hl.index(named.lower())
    for row in rows:
        if ci >= len(row) or row[ci].strip().lower() != key.lower():
            continue
        for gi, cell in enumerate(row):
            if cell.strip().lower() == gold.lower() and gi != ci:
                return True
        return False
    return False


def numeric_prefix_defect_screen(gold: str, chunk: str) -> bool:
    """The conservative screen the original audit used for numeric golds.

    It fires whenever the gold's digits begin some other token in the chunk,
    including a token that has nothing to do with the quantity asked about.
    Conservative in the safe direction, and the reason it needs a precise
    counterpart.
    """
    if not re.fullmatch(r"\d+(\.\d+)?%?", gold):
        return False
    core = gold.rstrip("%")
    if re.search(r"(?<![A-Za-z0-9.])" + re.escape(core) + r"(?=[A-Za-z.])", chunk):
        return True
    if gold.endswith("%") and re.search(
            r"(?<![A-Za-z0-9.])" + re.escape(core) + r"\.\d", chunk):
        return True
    return False


def _chunk_text_of(corpus_dir) -> dict:
    """The chunk texts of a corpus, without building an index.

    The defect rules need the text of the gold chunk and nothing else, so
    an index -- with its embeddings and its cache -- is more than the job
    needs.
    """
    from src.ingestion import ingest_corpus
    return {c.chunk_id: c.text for c in ingest_corpus(corpus_dir)}


def defective_queries(bench: dict, index, screen: bool = False) -> dict:
    """The defective labels in a benchmark.

    `screen=True` uses the conservative rules the original audit used;
    the default uses the precise rules, which adjudicate each hit instead of
    flagging it.
    """
    table_rule = table_defect_screen if screen else table_defect
    numeric_rule = (numeric_prefix_defect_screen if screen
                    else numeric_prefix_defect)
    out: dict[str, str] = {}
    for q in bench["queries"]:
        if q["category"] == "unanswerable":
            continue
        gold = str(q.get("answer") or "").strip()
        if not gold:
            continue
        for cid in (q.get("gold") or []):
            chunk = index.chunk_text.get(cid, "")
            if not chunk:
                continue
            if table_rule(q["query"], gold, chunk):
                out[q["query"]] = "the gold does not sit in the column the " \
                                  "question names, in the row the key names"
                break
            if numeric_rule(gold, chunk):
                out[q["query"]] = "the chunk never states the gold as a " \
                                  "complete token"
                break
    return out


def _first_sentence(text: str) -> str:
    parts = re.split(r"(?<=[.!?])\s", text.strip())
    return parts[0] if parts else text


def _mcnemar(b: int, c: int) -> float:
    """Exact two-sided McNemar: 2*P(X <= min(b,c)), X ~ Binom(b+c, 0.5)."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    return min(1.0, 2 * sum(comb(n, i) for i in range(k + 1)) * (0.5 ** n))


def _paired_robustness(gen: dict, bench: dict, defects: dict) -> dict:
    """The retrieval arm against the long-context arm, three ways.

    The question is whether the accuracy gap is a quality difference or an
    artefact of scoring a long answer against a short gold. If it survives
    the length-controlled and lexical tests it is real; if it only survives
    the whole-answer test, it is not.
    """
    from src.config import CONFIG
    from src.models import nli_probs

    goldq = {q["query"]: q for q in bench["queries"]}
    clean = [q["query"] for q in bench["queries"]
             if q["category"] != "unanswerable" and q["query"] not in defects]

    def answered(arm):
        return {r["query"]: r for r in (gen.get("records") or {}).get(arm, [])
                if r.get("answerable") and r.get("answered")}

    rag, longc = answered("rag_nogate"), answered("long_context")
    pairs = [q for q in clean if q in rag and q in longc]

    def _nli(text, gold):
        pr = nli_probs([(text, gold)], CONFIG.claim.nli_model)
        return bool(pr and pr[0]["entailment"] >= 0.5)

    out: dict = {"n_pairs": len(pairs), "tests": {}}
    for name, scorer in (
        ("nli_whole_answer",
         lambda r: bool(r.get("correct_nli"))),
        ("nli_first_sentence",
         lambda r: _nli(_first_sentence(r["answer_text"]),
                         goldq[r["query"]].get("answer") or "")),
        ("keyterm_lexical",
         lambda r: bool(r.get("correct_keyterm"))),
    ):
        b = sum(1 for q in pairs if scorer(rag[q]) and not scorer(longc[q]))
        c = sum(1 for q in pairs if scorer(longc[q]) and not scorer(rag[q]))
        out["tests"][name] = {
            "retrieval_only": b,
            "long_context_only": c,
            "p_value": _mcnemar(b, c),
        }
    lens = {a: sorted(len(r["answer_text"]) for r in sel.values())
            for a, sel in (("rag_nogate", rag), ("long_context", longc))}
    out["answer_length_median"] = {
        a: (v[len(v) // 2] if v else 0) for a, v in lens.items()}
    out["note"] = ("the same answers, scored three ways; a gap that survives "
                   "all three is a quality difference, and one that survives "
                   "only the whole-answer test is partly an artefact of "
                   "scoring a long answer against a short gold")
    return out


def main() -> int:
    index = load_index()
    bench = load_benchmark()
    defects = defective_queries(bench, index)
    screened = defective_queries(bench, index, screen=True)
    answerable = [q for q in bench["queries"] if q["category"] != "unanswerable"]
    clean = [q for q in answerable if q["query"] not in defects]

    payload = {
        "status": "run",
        "n_answerable": len(answerable),
        "n_defective": len(defects),
        "n_clean": len(clean),
        "defective": defects,
        "screen": {
            "n_hits": len(screened),
            "hits": screened,
            "note": "the conservative screen the original audit used: it "
                    "fires whenever the gold's digits begin some other token "
                    "in the chunk, and it finds the table row by looking "
                    "under the named column, so it over-reports. The "
                    "precise rules above adjudicate each hit.",
        },
        "note": "the gold chunk is correct in every defective case; only the "
                "answer string is attached to the wrong question, so the "
                "retrieval-side metrics are unaffected",
    }

    # The benchmark as it stood before the repair, kept so that the finding
    # stays reproducible rather than becoming a story about something that
    # can no longer be checked.
    pre_path = Path(__file__).resolve().parent / "data" / "benchmark_pre_repair.json"
    if pre_path.exists():
        pre = json.loads(pre_path.read_text(encoding="utf-8"))
        pre_ans = [q for q in pre["queries"] if q["category"] != "unanswerable"]
        resolvable = sum(
            1 for q in pre_ans
            if any(cid in index.chunk_text for cid in (q.get("gold") or [])))
        same_corpus = resolvable >= 0.5 * len(pre_ans)
        block = {
            "path": str(pre_path),
            "n_answerable": len(pre_ans),
            "same_corpus": same_corpus,
        }
        if same_corpus:
            block["n_defective_precise"] = len(defective_queries(pre, index))
            block["n_defective_screen"] = len(
                defective_queries(pre, index, screen=True))
            block["n_defective"] = block["n_defective_screen"]
        else:
            # The current index does not hold the pre-repair benchmark's gold
            # chunks -- it is a different corpus generation, or the focus
            # domain rather than the six-category corpus the pre-repair
            # benchmark was built on. The counts are still computable,
            # because the corpus the benchmark was built against is on disk;
            # they were simply not being computed, and the number that
            # should have been in the deliverables was None.
            block["index_note"] = (
                "the current index does not hold this benchmark's gold "
                "chunks, so the counts below were computed against the "
                "six-category corpus the benchmark was built on")
            _six = _chunk_text_of(ROOT / "data" / "corpus")
            _res = sum(1 for q in pre_ans
                        if any(cid in _six for cid in (q.get("gold") or [])))
            if _res >= 0.5 * len(pre_ans):
                _shim = type("_Idx", (), {"chunk_text": _six})()
                block["n_resolvable_against_the_six_category_corpus"] = _res
                block["n_defective_precise"] = len(
                    defective_queries(pre, _shim))
                block["n_defective_screen"] = len(
                    defective_queries(pre, _shim, screen=True))
                block["n_defective"] = block["n_defective_screen"]
                block["same_corpus"] = True
        payload["pre_repair"] = block

    # Experiment 8's answer-side accuracy on the questions that survive.
    gen_path = RESULTS_DIR / "exp8_generation.json"
    if gen_path.exists():
        gen = json.loads(gen_path.read_text(encoding="utf-8"))
        if gen.get("status") == "run":
            subset = {}
            for arm, recs in (gen.get("records") or {}).items():
                answered = [r for r in recs
                            if r["answerable"] and r.get("answered")]
                def _score(rows):
                    n = len(rows)
                    if not n:
                        return {"n": 0, "accuracy_nli": 0.0,
                                "accuracy_keyterm": 0.0}
                    return {
                        "n": n,
                        "accuracy_nli": sum(
                            1 for r in rows if r.get("correct_nli")) / n,
                        "accuracy_keyterm": sum(
                            1 for r in rows if r.get("correct_keyterm")) / n,
                    }
                clean_rows = [r for r in answered if r["query"] not in defects]
                subset[arm] = {
                    "all": _score(answered),
                    "clean": _score(clean_rows),
                    "n_answerable_total": len(answerable),
                }
            payload["arms"] = subset

    # -- Part 2: does the retrieval-vs-long-context gap survive a stricter
    #    reading of the same answers?
    if gen_path.exists():
        gen = json.loads(gen_path.read_text(encoding="utf-8"))
        if gen.get("status") == "run":
            payload["significance"] = _paired_robustness(gen, bench, defects)

    (RESULTS_DIR / "exp9_label_audit.json").write_text(
        json.dumps(payload, indent=2, default=float), encoding="utf-8")
    print(f"[audit] {len(defects)} of {len(answerable)} answerable questions "
          f"carry a defective answer label -> {RESULTS_DIR / 'exp9_label_audit.json'}")
    for arm, blk in (payload.get("arms") or {}).items():
        a, c = blk["all"], blk["clean"]
        print(f"[audit]   {arm:18} all: {a['accuracy_nli']:.3f} nli "
              f"({a['n']} answered)  clean: {c['accuracy_nli']:.3f} nli "
              f"({c['n']} answered)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
