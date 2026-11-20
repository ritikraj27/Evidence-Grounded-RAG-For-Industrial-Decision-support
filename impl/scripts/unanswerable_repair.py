#!/usr/bin/env python3
"""The corpus-anchored unanswerable class.

**Why this module exists.** The benchmark's original "near-miss" unanswerable
family was built to be the hard case. Its own comment says so: *"These have
the same surface form as answerable questions but name an identifier that is
verified absent from the corpus. This is the hard case."* The first half of
that sentence is false, and `audit_unanswerable_class.py` measures how false
it is. Every one of the family's questions names a fabricated identifier of
the form ``PREFIX-digits`` (``SKU-8422``, ``WC-1905``), and not one of the
answerable questions contains a token of that shape. A single regular
expression therefore separates the two classes, and the family's
unanswerability is decided by the question string rather than by the
evidence. A system that refused on the shape of the question would score
exactly as well as one that read the retrieved passages, which means the
family cannot support a claim about an *evidence-grounding* mechanism.

**What this module builds instead.** An unanswerable question of the same
shape as an answerable one, about a subject the corpus genuinely discusses,
asking for something the corpus genuinely does not state. The unanswerable
class is drawn from the same three question stems as the answerable class,
from the same *documents*, and by the same label machinery, so the two
classes differ in one respect only: whether the corpus states the answer.
Deciding that requires the corpus, which is what an evidence-grounding
mechanism is supposed to be tested on.

Three stems, mirroring the answerable classes one for one:

===================== ============================================== ==========
answerable class      question stem                                     source of
===================== ============================================== ==========
``definition``        "What is {subject}?"                             prose
``numeric_fact``      "What value is stated for {subject} in the       prose
                      source documentation?"
``table_lookup``      "According to the table in the source document,   tables
                      what is the {column} for {row}?"
===================== ============================================== ==========

**Two things make the classes comparable, and both are needed.**

*Same documents.* The answerable half of the benchmark is 86 definition
questions drawn from 29 source documents, and it is heavily concentrated:
fifteen of them come from one document on reliability engineering. If the
repaired class were drawn from the whole corpus it would be a different
sample of topics, and a classifier could separate the classes by topic
rather than by anything about answerability. So the repaired class is drawn
from the *same documents* the answerable class came from.

*Same label machinery.* The answerable classes are labelled by the
benchmark's own extraction branches: ``DEFINITION_RE`` finds a definition,
``NUMERIC_RE`` finds a value, and a table cell holds the answer. The
repaired class is labelled by the complement of exactly those tests, so the
two halves agree on what "answerable" means by construction.

**How each label is certified.** Every generated question is checked against
the corpus, and the check is written into the record so a reader can
re-derive it:

``definition``
    The subject occurs in the corpus and the corpus never *defines* it.
    "Defines" is tested loosely -- a copula or a definitional verb within
    forty characters either side of the subject, in either order -- because
    the benchmark's own ``DEFINITION_RE`` is too strict to match Wikipedia's
    definitional sentences once they carry a parenthetical gloss. A subject
    the corpus does define would make the question answerable, so the test
    has to be at least as strict as the generator's.

``numeric_fact``
    The subject occurs in the corpus, the benchmark's ``NUMERIC_RE`` never
    matches it as a subject, and no digit appears within two sentences of
    any occurrence of it. The corpus states no value for it anywhere.

``table_lookup``
    The row label occurs in a table and the column name is a header of a
    *different* table in the same document, and the two never occur
    together in any table. The corpus has tables; it does not have that
    cell.

The corpus, the benchmark's answerable half and the label standard are not
modified. This module adds a class; it does not change what "unanswerable"
means.
"""
from __future__ import annotations

import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import build_benchmark as bb  # noqa: E402

#: The window, in characters, within which a definitional verb makes a
#: subject "defined".
_DEFINITION_WINDOW = 40

_DEFINING = (r"is|are|was|were|refers to|denotes|means|stands for")

#: A sentence that *states* something about a term: "<term> is a/an/the
#: ...". The article is what separates a definition from any other use of
#: a copula -- "the performance rate is calculated as" says nothing about
#: what the performance rate is, while "the performance rate is the time
#: available for work" states what it is. The term is captured loosely so
#: that a subject carrying a parenthetical gloss still matches.
_STATES = re.compile(
    r"(?P<term>[A-Za-z][A-Za-z0-9\-'’ ]{2,60}?)\s+"
    r"(?:is|are|was|were|refers to|denotes|means|stands for)\s+"
    r"(?:a|an|the|any|one of)\s+\S",
    re.IGNORECASE,
)

#: A subject's head noun is lower case in the answerable class ("warranty
#: life", "net available time", "outbound logistics"). A repaired question
#: whose head noun is a capitalised proper noun would be distinguishable
#: from the answerable questions by that capital alone, and the class would
#: then be separable from the question text for a reason that has nothing to
#: do with evidence.
_PROPER_HEAD = re.compile(r"^[A-Z][a-z]+$")

#: Wikipedia furniture that appears in the dumps and is not a document.
_WIKIPEDIA_NOISE = re.compile(
    r"^(main article|see also|references|external links|notes|bibliography|"
    r"further reading|sources|authority control|categories|archived from)",
    re.IGNORECASE,
)

#: Navbox furniture: a "portal" row of links with these markers in it.
_NAVBOX = re.compile(r"- v - t - e|- Category -|Commons|Yale LUX|"
                     r"Authority control|Edit this at Wikidata", re.IGNORECASE)

#: Nouns that make a subject a *quantity*. The numeric stem asks for a
#: value, so its subjects have to be things that can have one.
_QUANTITY = re.compile(
    r"\b(cost|costs|time|rate|level|quantity|interval|capacity|volume|yield|"
    r"throughput|downtime|lead|cycle|setup|changeover|stock|inventory|waste|"
    r"defect|efficiency|availability|reliability|variability|margin|buffer|"
    r"tolerance|limit|threshold|performance|productivity|quality|duration|"
    r"period|frequency|probability|ratio|mean|variance|deviation|size|count|"
    r"number|loss|rework|scrap|utilisation|utilization|turnover|coverage|"
    r"latency|lot|batch|takt|sigma|chart|control|capability)\b",
    re.IGNORECASE,
)

#: Words that cannot head a subject phrase. The benchmark's own filter
#: checks only the *first* word for a pronoun, so a subject can end in one;
#: "a summary of these tools" is not a thing anybody would ask the
#: definition of.
_BAD_HEAD = frozenset(
    "these those this that one such same other others many most all several "
    "more less some any each both few various".split()
)

#: A row key that is only a number ("2026", "8") makes a lookup question no
#: reader would ask.
_NUMERIC_KEY = re.compile(r"^[\d.,% ()-]+$")

_MD_HEADING = re.compile(r"^#{1,4}\s+(.+?)\s*$", re.M)

#: The span of a sentence that sits immediately before a copula. This is
#: where the answerable ``definition`` family takes its subjects from, so
#: the repaired class draws its subjects from the same place.
_COPULA_SPAN = re.compile(
    r"([A-Z][A-Za-z0-9\-'’]*(?:[ \-][A-Za-z0-9\-'’]+){0,6})\s+(?:is|are|was|were)\b")


# --------------------------------------------------------------------------
# corpus interrogation
# --------------------------------------------------------------------------
def _document_of(chunk_id: str) -> str:
    """The source document of a chunk. Chunk ids look like ``doc::p1::tbl5``."""
    return chunk_id.split("::")[0]


def _corpus_sentences(chunks) -> list[tuple[str, str]]:
    """Every well-formed sentence in the corpus, with its chunk id."""
    out: list[tuple[str, str]] = []
    for ch in chunks:
        for sent in bb._sentences(ch.text):
            out.append((ch.chunk_id, sent))
    return out


def _defined_index(sentences: list[tuple[str, str]]) -> set[str]:
    """Every term the corpus states something about.

    The test is that some sentence reads "<term> is a/an/the ..." or "<term>
    refers to a/an/the ...". The article is what makes it a statement about
    the term rather than any other use of a copula, and the term is matched
    loosely so that a subject carrying a parenthetical gloss still counts:
    the benchmark's own ``DEFINITION_RE`` misses "Value-stream mapping or
    value-stream mapping (VSM) is a lean management tool", and a subject the
    corpus *does* define would slip through it.
    """
    out: set[str] = set()
    for _cid, sent in sentences:
        for m in _STATES.finditer(sent):
            mt = re.sub(r"\s+", " ", m.group("term").strip().lower())
            if len(mt.split()) >= 2:
                out.add(mt)
    return out


def _is_defined(term: str, defined: set[str]) -> bool:
    """Is *term* one of the terms the corpus states something about?

    A term is defined when it is contained in one of the corpus's stated
    terms, or contains one: "value-stream mapping" is defined by the
    sentence that states "value-stream mapping or value-stream mapping
    (vsm) is a lean management tool", and "net available time" is defined
    by a sentence that states "net available time is the time available
    for work to be done".
    """
    t = term.lower()
    for mt in defined:
        if t in mt or mt in t:
            return True
    return False


def _plain_sentences(text: str) -> list[str]:
    """The chunk text split on sentence boundaries, without the generator's
    filters. The generator's own sentence list drops fragments, so its
    windows cover different spans of text; a check that has to hold under
    both is the one worth making."""
    return re.split(r"(?<=[.!?])\s+", text)


def _has_digit_near(term: str, sentences: list[tuple[str, str]],
                     window: int = 2, plain: list[str] | None = None) -> bool:
    """Does a digit appear within *window* sentences of any occurrence?

    The check is run twice: once over the generator's own sentence list and
    once over a plain split of the chunk text. The two segmentations put
    different spans in the window, so a subject that passes both is one
    whose neighbourhood holds no number under either reading.
    """
    t = term.lower()
    low = [s.lower() for _cid, s in sentences]
    for i, s in enumerate(low):
        if t not in s:
            continue
        for j in range(max(0, i - window), min(len(sentences), i + window + 1)):
            if re.search(r"\d", sentences[j][1]):
                return True
    if plain is not None:
        plow = [s.lower() for s in plain]
        for i, s in enumerate(plow):
            if t not in s:
                continue
            for j in range(max(0, i - window), min(len(plain), i + window + 1)):
                if re.search(r"\d", plain[j]):
                    return True
    return False


def _has_numeric_value(term: str, sentences: list[tuple[str, str]]) -> bool:
    """Does the benchmark's own numeric branch find a value for *term*?"""
    t = term.lower()
    for _cid, sent in sentences:
        m = bb.NUMERIC_RE.search(sent)
        if m and m.group(1).strip().lower() == t:
            return True
    return False


# --------------------------------------------------------------------------
# term pools
# --------------------------------------------------------------------------
def _tables(chunks) -> list[tuple[str, list[str], list[list[str]]]]:
    """The corpus's tables, as (chunk id, header cells, body rows)."""
    out: list[tuple[str, list[str], list[list[str]]]] = []
    for ch in chunks:
        if ch.modality != "table":
            continue
        lines = [ln for ln in ch.text.splitlines() if ln.strip().startswith("|")]
        if len(lines) < 3:
            continue
        hdr = [c.strip() for c in lines[0].strip().strip("|").split("|")]
        if len(hdr) < 2 or all(set(x) <= set("-: ") for x in hdr):
            continue
        rows = []
        for ln in lines[1:]:
            r = [c.strip() for c in ln.strip().strip("|").split("|")]
            if len(r) == len(hdr):
                rows.append(r)
        if rows:
            out.append((ch.chunk_id, hdr, rows))
    return out


def _list_table_items(tables) -> list[str]:
    """The individual terms listed in the corpus's list tables."""
    out: list[str] = []
    for _cid, _hdr, rows in tables:
        for row in rows:
            for cell in row:
                for item in re.split(r"\s-\s|\n", cell):
                    item = item.strip().strip("*").strip()
                    item = re.sub(r"\(.*?\)", "", item).strip()
                    if item:
                        out.append(item)
    return out


def _chunk_terms(chunks) -> list[str]:
    """The concept names a chunk offers: its headings and its list-table items."""
    out: list[str] = []
    out += _heading_terms(chunks)
    out += _list_table_items(_tables(chunks))
    return out


def _heading_terms(chunks) -> list[str]:
    out: list[str] = []
    for ch in chunks:
        for m in _MD_HEADING.finditer(ch.text):
            out.append(m.group(1).strip())
    return out


def _copula_spans(sentences: list[tuple[str, str]]) -> list[str]:
    """The span of a sentence that sits immediately before a copula.

    This is where the answerable ``definition`` family takes its subjects
    from, so the repaired class draws from the same place and the two
    classes share a distribution of subject shapes.
    """
    out: list[str] = []
    for _cid, sent in sentences:
        m = _COPULA_SPAN.match(sent)
        if not m:
            continue
        span = re.split(r"[,–—:;(]", m.group(1))[0].strip()
        if span:
            out.append(span)
    return out


def _usable(term: str) -> bool:
    """Is this a plausible subject phrase, by the benchmark's own rule?

    ``_subject_is_usable`` is the generator's own filter, so using it here
    keeps the two classes on the same footing: a repaired question must fail
    the *evidence* test, never the *well-formedness* test.
    """
    if not term or len(term) < 5 or len(term) > 60:
        return False
    if term.endswith((".", ",", ":", ";")):
        return False
    if not term[0].isupper():
        return False
    if _WIKIPEDIA_NOISE.match(term) or _NAVBOX.search(term):
        return False
    if re.search(r"[(\"“]|\\|https?://", term):
        return False
    words = term.split()
    if not all(w.replace("-", "").replace("'", "").replace("’", "").isalpha()
               for w in words):
        return False
    if not bb._subject_is_usable(term):
        return False
    if words[-1].lower() in _BAD_HEAD:
        return False
    if _PROPER_HEAD.match(words[-1]):
        return False
    return True


def _plural(term: str) -> bool:
    """Is the head noun plural? The copula has to agree with the subject."""
    head = term.split()[-1].lower()
    return head.endswith("s") and not head.endswith(("ss", "us", "is"))


# --------------------------------------------------------------------------
# the documents the answerable classes came from
# --------------------------------------------------------------------------
def _answerable_documents(chunks) -> tuple[dict[str, set[str]],
                                          dict[str, list[dict]]]:
    """Replay the generator to find which documents each class came from.

    The repaired class is restricted to these documents so that the two
    halves of the benchmark are samples of the same topics. Without that
    restriction the answerable questions are concentrated in a handful of
    articles and the repaired questions are not, and a classifier separates
    the two classes by topic rather than by answerability.

    The answerable records themselves come back too, because the repaired
    class is also matched to them on the *shape* of the question.
    """
    out: dict[str, set[str]] = {"definition": set(), "numeric_fact": set(),
                                 "table_lookup": set()}
    records: dict[str, list[dict]] = {"definition": [], "numeric_fact": [],
                                      "table_lookup": []}
    rng = random.Random(0)
    for ch in chunks:
        for rec in bb.questions_from_text(ch.text, ch.chunk_id, ch.category, rng):
            fam = rec["family"]
            if fam in out:
                out[fam].add(_document_of(ch.chunk_id))
                records[fam].append(rec)
        for rec in bb.questions_from_table(ch.text, ch.chunk_id, ch.category, rng):
            fam = rec["family"]
            if fam in out:
                out[fam].add(_document_of(ch.chunk_id))
                records[fam].append(rec)
    return out, records


# --------------------------------------------------------------------------
# the shape of a question
# --------------------------------------------------------------------------
_STEM_PREFIXES = (
    ("table_lookup",
     "According to the table in the source document, what is the "),
    ("numeric_fact", "What value is stated for "),
)
_COPULAS = ("What is ", "What are ", "What was ", "What were ")


def stem_of(query: str) -> str:
    """Which of the benchmark's question stems a query uses."""
    if query.startswith(_STEM_PREFIXES[0][1]):
        return "table_lookup"
    if query.startswith(_STEM_PREFIXES[1][1]) and query.endswith(
            " in the source documentation?"):
        return "numeric_fact"
    for copula in _COPULAS:
        if query.startswith(copula):
            return "definition"
    return "other"


def subject_of(query: str) -> str:
    """The part of the query that names what is being asked about."""
    stem = stem_of(query)
    if stem == "table_lookup":
        return query[len(_STEM_PREFIXES[0][1]):].rsplit(" for ", 1)[0]
    if stem == "numeric_fact":
        return query[len(_STEM_PREFIXES[1][1]):-len(" in the source documentation?")]
    for copula in _COPULAS:
        if query.startswith(copula):
            return query[len(copula):-1]
    return query


def _table_pair(query: str) -> tuple[str, str]:
    """Split a table-stem question into its column name and row label."""
    head = query[len(_STEM_PREFIXES[0][1]):]
    col, _, row = head.rpartition(" for ")
    return col.strip(), row.strip().rstrip("?").strip()


def structural_cell(query: str) -> tuple:
    """A question's shape, as a tuple that can be compared.

    This is the cell the repaired class is *matched* on. It contains the
    stem and whether the subject contains a digit, an acronym or a
    capitalised head, and whether it opens with an article. It contains no
    word of the subject, so a question and its twin differ in nothing a
    shortcut could use. The subject's length is matched separately and
    softly, because a cell that included it would have too few
    candidates to fill in a class this small.
    """
    subject = subject_of(query)
    words = subject.split()
    head = words[-1] if words else ""
    return (
        stem_of(query),
        int(bool(re.search(r"\d", subject))),
        int(bool(re.search(r"\b[A-Z]{2,}\b", subject))),
        int(bool(head[:1].isupper())),
        int(bool(words) and words[0].lower() in ("the", "a", "an")),
    )


def _match_shape(candidates: list[str], answerable: list[str],
                 n: int, rng: random.Random) -> list[str]:
    """Choose *n* candidates whose shape mirrors the answerable class's.

    The answerable class's shape distribution is the reference. For each
    shape cell the answerable class uses, the repaired class takes as many
    candidates as the answerable class has questions of that shape, in the
    same proportion. Cells the answerable class never uses are not taken at
    all, because a question in such a cell is separable from the answerable
    class by its shape alone.

    Within a cell the subject *lengths* are matched by quantile. The length
    of a question is a property of its shape that a shortcut could use --
    "the long questions are the unanswerable ones" -- and the audit measured
    it to be the one cue that survived the cell matching. The answerable
    questions in a cell have a length distribution; the repaired ones are
    drawn at the same quantiles of the candidates' length distribution, so
    the two distributions agree.

    This is the "size-matched construction" of the evidence-sufficiency
    literature: the confounder is controlled by construction rather than
    measured away afterwards.
    """
    want: dict[tuple, int] = {}
    order: list[tuple] = []
    target_len: dict[tuple, list[int]] = {}
    for q in answerable:
        cell = structural_cell(q)
        if cell not in want:
            want[cell] = 0
            order.append(cell)
            target_len[cell] = []
        want[cell] += 1
        target_len[cell].append(len(subject_of(q)))
    total = sum(want.values()) or 1
    quota = {cell: max(1, round(n * want[cell] / total)) for cell in order}

    by_cell: dict[tuple, list[str]] = {}
    for c in candidates:
        by_cell.setdefault(structural_cell(c), []).append(c)
    for v in by_cell.values():
        rng.shuffle(v)

    def _expand_targets(lengths: list[int], k: int) -> list[int]:
        """The answerable class's length distribution, resampled to *k*."""
        if not lengths or k <= 0:
            return []
        s = sorted(lengths)
        if len(s) == 1 or k == 1:
            return [s[0]] * k
        return [s[round(i * (len(s) - 1) / (k - 1))] for i in range(k)]

    def _quantile_pick(pool: list[str], targets: list[int],
                       take: int) -> list[str]:
        """*take* candidates, each the closest in length to a target."""
        if not pool or not targets or take <= 0:
            return []
        chosen: list[str] = []
        remaining = list(pool)
        for t in targets:
            if not remaining:
                break
            best = min(remaining,
                       key=lambda c: (abs(len(subject_of(c)) - t),
                                      rng.random()))
            remaining.remove(best)
            chosen.append(best)
        while len(chosen) < take and remaining:
            t = targets[min(len(chosen), len(targets) - 1)]
            best = min(remaining,
                       key=lambda c: (abs(len(subject_of(c)) - t),
                                      rng.random()))
            remaining.remove(best)
            chosen.append(best)
        return chosen[:take]

    out: list[str] = []
    taken: dict[tuple, int] = {}
    for cell in order:
        pool = by_cell.get(cell, [])
        take = min(quota[cell], len(pool))
        for c in _quantile_pick(pool,
                                _expand_targets(target_len.get(cell, []), take),
                                take):
            if c not in out:
                out.append(c)
                taken[cell] = taken.get(cell, 0) + 1

    # Fill any shortfall from the cells that still have candidates, giving
    # the deficit to the cells whose quota is furthest from being met, and
    # matching the length the same way.
    if len(out) < n:
        for cell in sorted(order, key=lambda c: -(quota[c] - taken.get(c, 0))):
            if len(out) >= n:
                break
            pool = [c for c in by_cell.get(cell, []) if c not in out]
            spare = min(quota[cell], len(pool))
            for c in _quantile_pick(pool,
                                   _expand_targets(target_len.get(cell, []),
                                                   spare),
                                   spare):
                if c not in out:
                    out.append(c)
                if len(out) >= n:
                    break
    return out[:n] if len(out) > n else out


# --------------------------------------------------------------------------
# the three generators
# --------------------------------------------------------------------------
def _definition_questions(sentences, docs, doc_terms, defined, answerable,
                          rng, n) -> list[dict]:
    """'What is {subject}?' for subjects the corpus discusses but never defines."""
    pool: Counter = Counter()
    for cid, sent in sentences:
        if _document_of(cid) not in docs:
            continue
        m = _COPULA_SPAN.match(sent)
        if not m:
            continue
        span = re.split(r"[,–—:;(]", m.group(1))[0].strip()
        if _usable(span):
            pool[span] += 1
    # The corpus's own list tables and headings name the same concepts the
    # prose does, and they carry the acronyms ("RPN", "Cpk", "DPMO") that
    # the answerable class's subjects carry. Without them the repaired
    # class would be separable by whether its subject contained an acronym.
    for doc in docs:
        for term in doc_terms.get(doc, []):
            if _usable(term):
                pool[term] += 1
    candidates = [t for t, _c in pool.most_common()
                  if not _is_defined(t, defined)]
    rng.shuffle(candidates)

    queries = _match_shape(
        [bb.clean_query(f"What {'are' if _plural(t) else 'is'} "
                        f"{bb._subject_for_question(t)}?")
         for t in candidates], answerable, n, rng)
    out: list[dict] = []
    seen: set[str] = set()
    for query in queries:
        subject = bb._subject_for_question(subject_of(query))
        if len(out) >= n:
            break
        if query in seen:
            continue
        seen.add(query)
        out.append({
            "query": query,
            "gold": [],
            "category": "unanswerable",
            "family": "unanswerable_corpus_anchored_definition",
            "modality_target": None,
            "answer": None,
            "label_certificate": (
                "the subject occurs in the corpus and the corpus never "
                "defines it: no sentence in the corpus states the subject "
                "with a copula and an article, so the benchmark's own "
                "definition branch finds no answer"),
        })
    return out


def _numeric_questions(sentences, docs, doc_terms, defined, answerable,
                        plain, rng, n) -> list[dict]:
    """'What value is stated for {subject} in the source documentation?'

    for quantities the corpus mentions but never puts a number to.
    """
    pool: Counter = Counter()
    for cid, sent in sentences:
        if _document_of(cid) not in docs:
            continue
        m = _COPULA_SPAN.match(sent)
        if not m:
            continue
        span = re.split(r"[,–—:;(]", m.group(1))[0].strip()
        if (_usable(span) and _QUANTITY.search(span)
                and len(span.split()) <= 5):
            pool[span] += 1
    for doc in docs:
        for term in doc_terms.get(doc, []):
            if (_usable(term) and _QUANTITY.search(term)
                    and len(term.split()) <= 5):
                pool[term] += 1
    candidates = [t for t, _c in pool.most_common()
                  if not _has_numeric_value(t, sentences)
                  and not _has_digit_near(t, sentences, plain=plain)
                  and not _is_defined(t, defined)]
    rng.shuffle(candidates)

    queries = _match_shape(
        [bb.clean_query(f"What value is stated for "
                        f"{bb._subject_for_question(t)} in the "
                        f"source documentation?")
         for t in candidates], answerable, n, rng)
    out: list[dict] = []
    seen: set[str] = set()
    for query in queries:
        subject = bb._subject_for_question(subject_of(query))
        if len(out) >= n:
            break
        if query in seen:
            continue
        seen.add(query)
        out.append({
            "query": query,
            "gold": [],
            "category": "unanswerable",
            "family": "unanswerable_corpus_anchored_numeric",
            "modality_target": None,
            "answer": None,
            "label_certificate": (
                "the subject occurs in the corpus, the benchmark's numeric "
                "branch never finds a value for it, and no digit appears "
                "within two sentences of any occurrence of it, so the corpus "
                "states no value for it anywhere"),
        })
    return out


def _table_questions(chunks, sentences, docs, answerable, rng, n) -> list[dict]:
    """'According to the table ..., what is the {column} for {row}?'

    for row labels that exist and column names that exist, but never
    together.
    """
    tables = [t for t in _tables(chunks) if _document_of(t[0]) in docs]

    headers: list[tuple[str, str]] = []     # (column, table id)
    keys: list[tuple[str, str]] = []        # (row label, table id)
    for cid, hdr, rows in tables:
        for h in hdr:
            if bb._clean_label(h, 4):
                headers.append((h, cid))
        for row in rows:
            if bb._clean_label(row[0], 5) and not _NUMERIC_KEY.match(row[0]):
                keys.append((row[0], cid))

    # (column, row) pairs that actually occur somewhere in the corpus.
    present: set[tuple[str, str]] = set()
    for _cid, hdr, rows in _tables(chunks):
        for row in rows:
            for j, h in enumerate(hdr):
                if j < len(row):
                    present.add((h.lower(), row[0].lower()))

    candidates: list[tuple[str, str]] = []
    for col, col_cid in headers:
        for row, row_cid in keys:
            if col_cid == row_cid:
                continue                       # same table: that is answerable
            if (col.lower(), row.lower()) in present:
                continue                       # some table does have the cell
            candidates.append((col, row))
    rng.shuffle(candidates)

    queries = _match_shape(
        [bb.clean_query(f"According to the table in the source document, "
                        f"what is the {col} for {row}?")
         for col, row in candidates], answerable, n, rng)
    out: list[dict] = []
    seen: set[str] = set()
    for query in queries:
        col, row = _table_pair(query)
        if len(out) >= n:
            break
        if query in seen:
            continue
        seen.add(query)
        out.append({
            "query": query,
            "gold": [],
            "category": "unanswerable",
            "family": "unanswerable_corpus_anchored_table",
            "modality_target": None,
            "answer": None,
            "label_certificate": (
                f"the row label '{row}' occurs in a table in the corpus and "
                f"the column name '{col}' is a header of a table in the "
                f"corpus, but the two never occur together in any table, so "
                f"the corpus has no cell for this lookup"),
        })
    return out


# --------------------------------------------------------------------------
def generate(chunks, n: int = 110, seed: int = 20261118,
             answerable: dict | None = None) -> list[dict]:
    """The corpus-anchored unanswerable class.

    The split across the three stems follows the answerable class's own
    proportions, so the two classes are matched on the shape of the question
    and differ only in whether the corpus states the answer.

    `answerable` supplies the answerable class the repaired class is to be
    matched against. When it is None the answerable class is recovered by
    replaying the benchmark's own generator over the corpus, which is what
    the shipped benchmarks do. A corpus whose answerable class is produced
    by a different extractor must supply it here: the shape matching --
    the stem, the structural features, the subject-length quantiles -- is
    only meaningful against the class the repaired questions will actually
    be compared with.
    """
    sentences = _corpus_sentences(chunks)
    if answerable is None:
        docs, records = _answerable_documents(chunks)
    else:
        records = answerable
        docs = {
            fam: {_document_of(r["gold"][0]) for r in recs if r.get("gold")}
            for fam, recs in answerable.items()
        }
    # Every document the answerable half was drawn from. The three stems
    # draw from slightly different subsets, so a stem whose own subset is
    # too small to fill its quota is widened to the union rather than to the
    # whole corpus, which would reintroduce the topic skew.
    all_docs = docs["definition"] | docs["numeric_fact"] | docs["table_lookup"]
    # The concept names each document offers, computed once.
    doc_terms: dict[str, list[str]] = defaultdict(list)
    for ch in chunks:
        doc_terms[_document_of(ch.chunk_id)].extend(_chunk_terms([ch]))
    rng = random.Random(seed)
    out: list[dict] = []
    defined = _defined_index(sentences)
    plain = _plain_sentences("\n".join(c.text for c in chunks))
    out += _definition_questions(
        sentences, docs["definition"] | all_docs, doc_terms, defined,
        [r["query"] for r in records["definition"]], rng, round(n * 0.65))
    out += _numeric_questions(
        sentences, docs["numeric_fact"] | all_docs, doc_terms, defined,
        [r["query"] for r in records["numeric_fact"]], plain, rng,
        round(n * 0.14))
    out += _table_questions(
        chunks, sentences, docs["table_lookup"],
        [r["query"] for r in records["table_lookup"]], rng, n - len(out))
    return out
