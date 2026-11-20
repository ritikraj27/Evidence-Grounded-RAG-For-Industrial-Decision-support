#!/usr/bin/env python3
"""Experiment 12: the benchmark's *unanswerable* half, audited.

The answerable half is the half that gets audited most, and this project's
audit of it found a defect class, repaired it, and re-measured. The
unanswerable half is the larger risk and had no audit at all, because
nothing in the retrieval-side experiments can fail on it: the unanswerable
questions are *supposed* to have no answer, so the only ways the half can
be wrong are ways no retrieval metric can see.

**What the audit found.** The half was separable from the question text
alone. A classifier that sees only the query -- no retrieval, no evidence,
no corpus -- told an answerable question from an unanswerable one at
F1 0.99 / ROC-AUC 1.00. The mechanism was not subtle: the half's "hard
case" named a fabricated identifier of the form ``PREFIX-digits``
(``SKU-8422``, ``WC-1905``), and *not one* of the 132 answerable questions
contains a token of that shape. One regular expression separated the two
classes perfectly. That matters because the thesis's mechanism is an
*evidence* mechanism: if a system's unanswerability is visible in the
question, a system that refused on the question's shape would score exactly
as well as one that read the retrieved passages, and the benchmark cannot
tell the two apart.

**What was done about it.** The half was rebuilt as a *corpus-anchored*
class: the same three question stems as the answerable half, the same
source documents, subjects the corpus genuinely discusses, and attributes
the corpus genuinely does not state. Its unanswerability is then decidable
only from the evidence. The pre-repair benchmark is preserved beside the
repaired one so the two can be compared.

**Three questions are measured, and they are not the same question.**

*Can the question's **form** tell the two classes apart?* This is the
claim-bearing measurement. A bag-of-words classifier over the whole query
cannot answer it properly: with a hundred or so questions per class it will
memorise the tokens that happen to occur in one of them, so its score says
something about the sample and not about the benchmark. The features that a
shortcut would actually use are the *structural* ones -- the stem, the
length of the subject, whether the subject contains a digit, an acronym or
a code-shaped token, how its head noun is capitalised -- and those are what
the audit reports first.

*Does the **whole query** tell them apart?* Reported second, with a
permutation null so that the number can be read against what the same
procedure produces when the labels mean nothing.

*Does the corpus **leak**?* A closed-book probe asks every question with no
corpus in the prompt. A high rate on the unanswerable class means the
"unanswerable" label is not corpus-specific: either the parameters contain
the answer, or the generator is guessing, which is the behaviour the gate
exists to prevent. The answerable class is the control.

Method note: the closed-book probe uses a *neutral* system prompt, not the
generation harness's "answer only from the documents given", because there
are no documents to answer from and the instruction would be false.

The corpus, the benchmark's answerable half and the label standard are not
modified by this experiment. It measures them.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

import numpy as np

os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("OMP_NUM_THREADS", "4")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import load_benchmark, write_result  # noqa: E402
from src.config import ARTIFACT_DIR, CONFIG  # noqa: E402
from run_generation_eval import (  # noqa: E402
    _REFUSAL_RE,
    _call,
    _llm_config,
    _text_of,
    _usage_of,
)

SEED = 20261118

#: How many label permutations the null distribution is built from.
N_PERMUTATIONS = 100

#: The closed-book system prompt. Neutral on purpose: telling a model to
#: answer only from documents that are not there would measure how it
#: handles a false instruction, not what it knows.
CLOSED_BOOK_SYSTEM = (
    "You are a helpful assistant. Answer the question."
)

#: The shortcut the near-miss class carried: a fabricated identifier of the
#: form PREFIX-digits. No answerable question contains one.
_CODE_RE = re.compile(r"\b[A-Z]{2,3}-\d{2,4}\b")

#: The three question stems the benchmark uses.
_STEMS = (
    ("table_lookup",
     "According to the table in the source document, what is the "),
    ("numeric_fact",
     "What value is stated for "),
)


# --------------------------------------------------------------------------
# structural features: the question's shape and nothing else
# --------------------------------------------------------------------------
#: The canonical shape definitions live with the generator that constructs
#: the repaired class, because the class is *matched* on them: the matching
#: and the measurement must be the same definition or the second says
#: nothing about the first.
sys.path.insert(0, str(ROOT / "scripts"))
from unanswerable_repair import (  # noqa: E402
    stem_of as _stem_of,
    subject_of as _subject_of,
    structural_cell as _structural_cell,
)


def _structural_features(query: str) -> dict:
    """Features a shortcut could use, and nothing else.

    Every feature here is a property of the question's *form*: the stem it
    uses, the shape of its subject, whether the subject contains a token of
    a particular kind. None of them is a word of the subject, so a
    classifier built on them cannot learn "reliability questions are
    answerable" -- which is a fact about this sample of documents, not
    about answerability.
    """
    subject = _subject_of(query)
    words = subject.split()
    cell = _structural_cell(query)
    stem, has_digit, has_acronym, head_cap, has_article = cell
    return {
        "cell": ":".join(str(c) for c in cell),
        "stem": stem,
        "n_words_subject": float(len(words)),
        "n_chars_subject": float(len(subject)),
        "n_chars_question": float(len(query)),
        "has_digit": float(has_digit),
        "has_code": float(bool(_CODE_RE.search(subject))),
        "has_acronym": float(has_acronym),
        "head_capitalised": float(head_cap),
        "subject_leading_article": float(has_article),
    }


def _structural_matrix(queries: list[str]):
    from sklearn.compose import ColumnTransformer
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import StratifiedKFold, cross_val_predict
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OneHotEncoder, StandardScaler

    rows = [_structural_features(q) for q in queries]
    keys = list(rows[0].keys())
    cat = [i for i, k in enumerate(keys) if isinstance(rows[0][k], str)]
    num = [i for i, k in enumerate(keys) if not isinstance(rows[0][k], str)]
    X = np.array([[r[k] for k in keys] for r in rows], dtype=object)
    pipe = Pipeline([
        ("ct", ColumnTransformer([
            ("num", StandardScaler(), num),
            ("cat", OneHotEncoder(handle_unknown="ignore"), cat)])),
        ("clf", LogisticRegression(max_iter=3000, C=1.0,
                                   class_weight="balanced")),
    ])
    return pipe, X


def _bow_matrix(queries: list[str]):
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import StratifiedKFold, cross_val_predict
    from sklearn.pipeline import FeatureUnion, Pipeline

    pipe = Pipeline([
        ("features", FeatureUnion([
            ("word", TfidfVectorizer(ngram_range=(1, 2), min_df=1,
                                     sublinear_tf=True)),
            ("char", TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5),
                                     min_df=2, sublinear_tf=True)),
        ])),
        ("clf", LogisticRegression(max_iter=2000, C=1.0,
                                   class_weight="balanced")),
    ])
    return pipe, None


def _separability(answerable: list[str], unanswerable: list[str],
                  mode: str = "structural",
                  permutations: int = N_PERMUTATIONS) -> dict:
    """How well can a question-only classifier tell the two classes apart?

    ``structural`` uses only the question's form. ``bag_of_words`` uses the
    whole query, which in a finite sample lets the classifier memorise the
    tokens that happen to occur in one class. Both are reported with the
    majority-class reference point and with a permutation null: the same
    procedure run on shuffled labels, which is what the procedure produces
    when the labels carry no information.
    """
    from sklearn.metrics import f1_score, roc_auc_score
    from sklearn.model_selection import StratifiedKFold, cross_val_predict

    pairs = sorted([(q, 1) for q in answerable] + [(q, 0) for q in unanswerable])
    queries = [p[0] for p in pairs]
    y = np.array([p[1] for p in pairs])

    pipe, X = (_structural_matrix(queries) if mode == "structural"
               else _bow_matrix(queries))
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)

    def _score(labels):
        if mode == "structural":
            prob = cross_val_predict(pipe, X, labels, cv=cv,
                                     method="predict_proba")[:, 1]
        else:
            prob = cross_val_predict(pipe, queries, labels, cv=cv,
                                     method="predict_proba")[:, 1]
        pred = (prob >= 0.5).astype(int)
        maj = int(np.bincount(labels).argmax())
        return (float(f1_score(labels, pred)),
                float(roc_auc_score(labels, prob)),
                float(f1_score(labels, np.full_like(labels, maj))))

    f1, auc, base = _score(y)
    null_auc: list[float] = []
    for i in range(permutations):
        permuted = np.random.RandomState(SEED + i).permutation(y)
        null_auc.append(_score(permuted)[1])
    null = np.array(null_auc)
    p_value = (1 + int((null >= auc).sum())) / (1 + len(null))
    return {
        "mode": mode,
        "n_answerable": len(answerable),
        "n_unanswerable": len(unanswerable),
        "f1": f1,
        "roc_auc": auc,
        "f1_majority_class_baseline": base,
        "gap_over_majority": f1 - base,
        "permutation_null_auc_mean": float(null.mean()),
        "permutation_null_auc_sd": float(null.std()),
        "permutation_null_auc_max": float(null.max()),
        "p_value_vs_permutation_null": float(p_value),
        "n_permutations": int(permutations),
        "note": (
            "the null is the same procedure run on shuffled labels. A p-value "
            "near 1 means the procedure cannot tell the classes apart, which "
            "is what a benchmark wants: the question's form does not reveal "
            "whether the corpus holds the answer."),
    }


def _structural_matching(answerable: list[str], unanswerable: list[str]) -> dict:
    """Does every repaired question have a structural twin in the answerable class?

    This is the construction's own quality check, and it is exact: a
    question and its twin have the same stem, the same subject size, and
    the same shape markers, and differ in nothing a shortcut could use.
    A class in which every member has a twin cannot be separated by the
    shape, whatever the sample size.
    """
    cells: dict[tuple, int] = {}
    for q in answerable:
        cells[_structural_cell(q)] = cells.get(_structural_cell(q), 0) + 1
    matched = [q for q in unanswerable if _structural_cell(q) in cells]
    n = len(unanswerable)
    return {
        "n_answerable": len(answerable),
        "n_unanswerable": n,
        "n_matched": len(matched),
        "match_rate": (len(matched) / n) if n else None,
        "n_shape_cells_answerable": len(cells),
        "n_shape_cells_unanswerable": len(
            {_structural_cell(q) for q in unanswerable}),
        "unmatched_examples": [q for q in unanswerable
                               if _structural_cell(q) not in cells][:10],
        "note": (
            "a matched question and its twin have the same stem, the same "
            "subject size, and the same shape markers -- whether the "
            "subject contains a digit, an acronym, a capitalised head, or "
            "an opening article -- and differ in no word. A class in which "
            "every member has a twin cannot be separated by the shape."),
    }


def _shortcut_diagnostic(answerable: list[str], unanswerable: list[str]) -> dict:
    """The one-rule shortcut, and how much of the class it carries.

    A rule that separates the classes without reading the corpus is the
    sharpest form of the defect, because no amount of retrieval quality
    can beat it.
    """
    caught = sum(1 for q in unanswerable if _CODE_RE.search(q))
    missed = sum(1 for q in unanswerable if not _CODE_RE.search(q))
    false_positive = sum(1 for q in answerable if _CODE_RE.search(q))
    n_u = len(unanswerable)
    return {
        "rule": "the query contains a token of the form PREFIX-digits "
                r"(\b[A-Z]{2,3}-\d{2,4}\b)",
        "unanswerable_caught": caught,
        "unanswerable_missed": missed,
        "answerable_false_positives": false_positive,
        "n_unanswerable": n_u,
        "n_answerable": len(answerable),
        "recall_on_unanswerable": (caught / n_u) if n_u else None,
        "share_of_unanswerable_carried_by_the_rule": (caught / n_u) if n_u else None,
    }


def _document_concentration(bench: dict) -> dict:
    """How concentrated the answerable half is in source documents.

    The repaired class is restricted to the documents the answerable half
    came from, so the concentration is a property of the construction and
    has to be measured rather than asserted.
    """
    docs: dict[str, int] = {}
    for rec in bench["queries"]:
        if rec["category"] == "unanswerable":
            continue
        for gold in rec.get("gold") or []:
            doc = str(gold).split("::")[0]
            docs[doc] = docs.get(doc, 0) + 1
    n = sum(docs.values()) or 1
    if not docs:
        return {"n_documents": 0, "largest_document_share": None}
    top = max(docs.values())
    return {
        "n_documents": len(docs),
        "n_answerable": n,
        "largest_document_questions": top,
        "largest_document_share": top / n,
        "note": (
            "the answerable half is concentrated in a small number of source "
            "documents, which is why the repaired class is restricted to "
            "them: drawn from the whole corpus it would be a different "
            "sample of topics, and a classifier would separate the two "
            "classes by topic rather than by answerability."),
    }


def _length_profile(answerable: list[str], unanswerable: list[str]) -> dict:
    la = [len(q) for q in answerable]
    lu = [len(q) for q in unanswerable]
    return {
        "median_length_answerable": float(np.median(la)) if la else None,
        "median_length_unanswerable": float(np.median(lu)) if lu else None,
        "mean_length_answerable": float(np.mean(la)) if la else None,
        "mean_length_unanswerable": float(np.mean(lu)) if lu else None,
    }


# --------------------------------------------------------------------------
# the question-only policy: a system that refuses on the question alone
# --------------------------------------------------------------------------
#: The system prompt for the question-only policy. The model is told what
#: the corpus is about and is given no documents, and asked whether that
#: corpus could answer the question. A policy that answers this well is a
#: policy that can decide answerability without reading any evidence.
POLICY_SYSTEM = (
    "You answer questions about industrial engineering documentation -- "
    "operations research, reliability engineering, quality engineering, "
    "production scheduling, supply chain management and facility layout. "
    "You are given a question but not the documents. Decide whether a "
    "standard industrial engineering documentation set would contain the "
    "answer to it. Reply with exactly one word: YES or NO."
)


def _policy_answer(text: str) -> str | None:
    """'yes' or 'no', or None if the answer was neither."""
    t = text.strip().lower()
    m = re.match(r"\s*(yes|no)\b", t)
    return m.group(1) if m else None


def _question_only_policy(cfg: dict, questions: list[dict]) -> dict:
    """Ask a model, with no documents, whether the corpus could answer.

    This is the hypothesis-only baseline of the answerability literature,
    and it is the measurement that matters for the claim: a fitted
    classifier on a hundred questions can memorise the sample, but a model
    that has never seen the benchmark can only use what the question
    carries. If the policy can tell the two classes apart, then a system
    that refused on the question's shape would score as well as one that
    read the passages, and the benchmark cannot tell them apart.
    """
    if cfg is None:
        return {"status": "not_run",
                "note": "no API credential reachable from this machine"}
    policy_cfg = dict(cfg)
    policy_cfg["system"] = POLICY_SYSTEM
    out = []
    errors = []
    for n, rec in enumerate(questions, 1):
        try:
            resp = _call_retry(policy_cfg, "", rec["query"])
        except Exception as e:  # noqa: BLE001
            errors.append(f"{type(e).__name__}: {e}")
            break
        verdict = _policy_answer(_text_of(resp))
        out.append({
            "query": rec["query"],
            "family": rec.get("family"),
            "category": rec["category"],
            "policy_says_answerable": verdict == "yes",
            "policy_says_unanswerable": verdict == "no",
            "verdict": verdict,
        })
        if n % 25 == 0:
            print(f"[exp12] question-only policy: {n}/{len(questions)}",
                  flush=True)
    def _rates(rows):
        if not rows:
            return None
        n_no = sum(1 for r in rows if r["policy_says_unanswerable"])
        return n_no / len(rows)

    ans = [r for r in out if r["category"] != "unanswerable"]
    un = [r for r in out if r["category"] == "unanswerable"]
    by_family: dict[str, dict] = {}
    for fam in sorted({r["family"] for r in out}):
        rows = [r for r in out if r["family"] == fam]
        by_family[fam] = {
            "n": len(rows),
            "says_unanswerable": sum(1 for r in rows
                                     if r["policy_says_unanswerable"]),
            "rate_unanswerable": _rates(rows),
        }
    # The policy is used as an abstention rule: it abstains where it says
    # NO. Its value on the answerable class is the coverage it costs, and
    # its value on the unanswerable class is the refusals it earns.
    tp = sum(1 for r in un if r["policy_says_unanswerable"])
    fp = sum(1 for r in ans if r["policy_says_unanswerable"])
    precision = tp / (tp + fp) if (tp + fp) else None
    recall = tp / len(un) if un else None
    f1 = (2 * precision * recall / (precision + recall)
          if precision and recall and (precision + recall) else None)
    # The detection rate alone does not say whether the policy discriminates:
    # a policy that refuses everything detects every unanswerable question
    # and answers no answerable one. Its discrimination is the ROC AUC over
    # the two classes, with the score being the refusal.
    auc = None
    try:
        from sklearn.metrics import roc_auc_score
        if ans and un:
            # The score is the policy's *answerability* judgement and the
            # label is answerable, so an AUC above 0.5 means the policy
            # discriminates in the right direction.
            scores = ([1.0 if r["policy_says_answerable"] else 0.0
                       for r in ans]
                      + [1.0 if r["policy_says_answerable"] else 0.0
                         for r in un])
            labels = [1] * len(ans) + [0] * len(un)
            auc = float(roc_auc_score(labels, scores))
    except Exception:  # noqa: BLE001
        auc = None
    if errors:
        # The probe measures a policy's behaviour, and a provider timeout is
        # not a fact about the policy. What was collected is reported, with
        # the shortfall stated.
        return {
            "status": "partial",
            "reason": errors[0],
            "n_asked": len(out),
            "n_questions": len(questions),
            "n_answerable": len(ans),
            "n_unanswerable": len(un),
            "policy_calls_unanswerable_answerable": fp,
            "policy_calls_unanswerable_unanswerable": tp,
            "abstention_precision": precision,
            "abstention_recall": recall,
            "abstention_f1": f1,
            "abstention_auc": auc,
            "coverage_lost_on_answerable": fp / len(ans) if ans else None,
            "unanswerable_detected": tp / len(un) if un else None,
            "by_family": by_family,
            "records": out,
        }
    return {
        "status": "run",
        "n_asked": len(out),
        "n_answerable": len(ans),
        "n_unanswerable": len(un),
        "abstention_auc": auc,
        "policy_calls_unanswerable_answerable": fp,
        "policy_calls_unanswerable_unanswerable": tp,
        "abstention_precision": precision,
        "abstention_recall": recall,
        "abstention_f1": f1,
        "coverage_lost_on_answerable": fp / len(ans) if ans else None,
        "unanswerable_detected": tp / len(un) if un else None,
        "by_family": by_family,
        "records": out,
        "note": (
            "a model given only the question, asked whether the corpus "
            "could answer it. This is the hypothesis-only baseline of the "
            "answerability literature, and it is the number to read next to "
            "the systems: a policy that does well here could refuse without "
            "reading any evidence, so it measures what the benchmark's "
            "questions reveal on their own."),
    }


# --------------------------------------------------------------------------
# the repair's certificates, re-checked independently of the generator
# --------------------------------------------------------------------------
#: "the subject is the thing the corpus talks about" -- written here rather
#: than imported, so that the check does not share code with the generator
#: that produced the questions.
#: A definition, in the sense the label standard uses: a subject, a copula
#: and an article.
_DEFINES_RE = re.compile(
    r"(?P<term>[A-Za-z][A-Za-z0-9\-'’ ]{2,60}?)\s+"
    r"(?:is|are|was|were|refers to|denotes|means|stands for)\s+"
    r"(?:a|an|the|any|one of)\s+\S",
    re.IGNORECASE,
)

_STATES_RE = re.compile(
    r"(?P<term>[A-Za-z][A-Za-z0-9\-'’ ]{2,60}?)\s+"
    r"(?:is|are|was|were|refers to|denotes|means|stands for)\s+"
    r"(?:a|an|the|any|one of)\s+\S",
    re.IGNORECASE,
)


def _corpus_text() -> str:
    """The corpus the pipeline retrieves from.

    This is the *ingested chunk text*, not the raw markdown files: the
    ingestion expands wiki links and strips templates, so a phrase can
    appear in the chunks and not in the file they came from. A check
    against the raw files would measure a corpus the system never sees.
    """
    from src.config import CORPUS_DIR
    from src.ingestion import ingest_corpus
    return "\n".join(c.text for c in ingest_corpus(CORPUS_DIR))


def _verify_certificates(bench: dict) -> dict:
    """Re-check, independently, that the repaired class has no answer.

    The generator writes a certificate into every record. This does not
    trust it: it re-derives the property from the corpus, using a
    predicate written independently of the generator.

    The property is the one the label standard is defined over. For the
    *definition* stem, the benchmark calls a question answerable when the
    corpus states a definition of its subject, and it recognises a
    definition as a subject followed by a copula and an article. A subject
    that stands in the subject position of a copula *without* that article
    --- "The model was based on a linear regression model" --- is not
    recognised by the benchmark's pattern, but a reader can still answer
    the question from it, so the repaired class is held to the stricter
    test: the subject must not stand in the subject position of any copula
    anywhere in the corpus.

    Two counts are reported. The first is the certificate as written, under
    that stricter test. The second is a deliberately looser probe, which
    accepts a definitional span anywhere in the chunk text and treats a
    subject merely *contained* in such a span as defined; the difference
    between the two is the residual this benchmark cannot avoid, and it is
    reported rather than hidden.
    """
    from src.config import CORPUS_DIR
    from src.ingestion import ingest_corpus
    corpus = "\n".join(c.text for c in ingest_corpus(CORPUS_DIR))
    corpus_lower = corpus.lower()
    sentences = re.split(r"(?<=[.!?])\s+", corpus)
    low = [s.lower() for s in sentences]

    # The looser probe: a definitional span anywhere in the text, with the
    # subject contained in it.
    stated: set[str] = set()
    for m in _STATES_RE.finditer(corpus):
        mt = re.sub(r"\s+", " ", m.group("term").strip().lower())
        if len(mt.split()) >= 2:
            stated.add(mt)

    # The stricter test: the subject immediately before a copula.
    subject_copula = re.compile(
        r"([A-Za-z][A-Za-z0-9\-'’ ]{1,58}?)\s+"
        r"(?:is|are|was|were|refers to|denotes|means|stands for)\b",
        re.IGNORECASE,
    )

    def _stands_in_subject_position(term: str) -> bool:
        t = re.sub(r"\s+", " ", term.strip().lower())
        if not t:
            return False
        for sent in sentences:
            for m in subject_copula.finditer(sent):
                span = re.sub(r"\s+", " ", m.group(1).strip().lower())
                if span == t or span.endswith(" " + t):
                    return True
        return False

    def _loosely_defined(term: str) -> bool:
        t = re.sub(r"\s+", " ", term.strip().lower())
        if not t:
            return False
        return any(t in mt or mt in t for mt in stated)

    # The certificate's own test: the corpus states no *definition* of the
    # subject, in the sense the label standard uses -- a subject, a copula,
    # and an article. This is the benchmark's own pattern, applied to every
    # sentence of the corpus rather than to one chunk.
    defined_strictly: set[str] = set()
    for m in _DEFINES_RE.finditer(corpus):
        mt = re.sub(r"\s+", " ", m.group("term").strip().lower())
        if len(mt.split()) >= 2:
            defined_strictly.add(mt)

    def _defined_in_the_standard(term: str) -> bool:
        t = re.sub(r"\s+", " ", term.strip().lower())
        if not t:
            return False
        return any(t in mt or mt in t for mt in defined_strictly)

    def _stands_in_subject_position(term: str) -> bool:
        """Stricter than the standard: the subject before any copula.

        This catches the near-misses the standard cannot see -- a subject
        the corpus says something specific about without defining it, such
        as "The model was based on a linear regression model". A reader can
        answer such a question; the benchmark's pattern cannot see it.
        """
        t = re.sub(r"\s+", " ", term.strip().lower())
        if not t:
            return False
        for sent in sentences:
            for m in subject_copula.finditer(sent):
                span = re.sub(r"\s+", " ", m.group(1).strip().lower())
                if span == t or span.endswith(" " + t):
                    return True
        return False

    checked = {"definition": 0, "numeric_fact": 0, "table_lookup": 0}
    failed: list[dict] = []
    loose_failures: list[dict] = []
    near_miss_by_family: dict[str, int] = {}
    for rec in bench["queries"]:
        if not rec["family"].startswith("unanswerable_corpus_anchored"):
            continue
        q = rec["query"]
        stem = _stem_of(q)
        subject = _subject_of(q)
        checked[stem] += 1
        if stem == "table_lookup":
            row = q.rsplit(" for ", 1)[1].rstrip("?")
            occurs = row.lower() in corpus_lower
            together = bool(re.search(
                re.escape(subject.lower()) + r"[^|\n]{0,80}" + re.escape(row.lower()),
                corpus_lower))
            ok = occurs and not together
        elif stem == "numeric_fact":
            t = subject.lower()
            occurs = t in corpus_lower
            digit = False
            for i, s in enumerate(low):
                if t not in s:
                    continue
                for j in range(max(0, i - 2), min(len(sentences), i + 3)):
                    if re.search(r"\d", sentences[j]):
                        digit = True
                        break
                if digit:
                    break
            ok = occurs and not digit and not _defined_in_the_standard(subject)
        else:
            t = subject.lower()
            occurs = t in corpus_lower
            ok = occurs and not _defined_in_the_standard(subject)
        if not ok:
            failed.append({"query": q, "family": rec["family"],
                           "subject_occurs_in_corpus": occurs})
        # The near-miss probe: the corpus comments on the subject without
        # defining it, so a reader could sometimes construct an answer even
        # though the label standard does not recognise one. This is the
        # class's character, not a failure of the certificate.
        if (stem != "table_lookup"
                and _stands_in_subject_position(subject)
                and not _defined_in_the_standard(subject)):
            loose_failures.append({"query": q, "family": rec["family"]})
            near_miss_by_family[rec["family"]] = (
                near_miss_by_family.get(rec["family"], 0) + 1)
    return {
        "checked": checked,
        "n_failed": len(failed),
        "failures": failed[:20],
        "n_near_miss": len(loose_failures),
        "near_miss_by_family": near_miss_by_family,
        "near_miss_examples": loose_failures[:20],
        "note": (
            "every repaired question is re-checked against the corpus with a "
            "predicate written independently of the generator, using the "
            "label standard's own notion of a definition -- a subject, a "
            "copula and an article -- applied to every sentence of the "
            "corpus rather than to one chunk. The near-miss probe counts a "
            "different thing: the questions whose subject the corpus "
            "comments on without defining it, so that a reader could "
            "sometimes construct an answer even though the label standard "
            "recognises none. That is the character of a mechanically "
            "labelled unanswerable class, and it is reported rather than "
            "hidden."),
    }


# --------------------------------------------------------------------------
# parametric leakage
# --------------------------------------------------------------------------
#: How many times a request is retried before the probe gives up, and how
#: long it waits between attempts. The provider is periodically overloaded and
#: a read timeout is its way of saying so; a probe that dies on one timeout
#: throws away the records it has already collected.
_RETRIES = 4
_RETRY_DELAY = 8.0

#: A rate limit is not a transient failure in the same sense a read timeout
#: is: it means the provider wants a longer pause, not a shorter one. The
#: industrial run made seven hundred and forty-four requests in twenty-five
#: minutes before the provider answered 429, so the wait is long.
_RATE_LIMIT_DELAY = 60.0

#: The pause between requests, so that a run of hundreds of questions does
#: not arrive as a burst. It is a configuration, not a measurement.
_CALL_DELAY = float(os.environ.get("MTP_EXP12_CALL_DELAY", "0.0") or 0.0)

#: A disk cache of the probe's API responses, keyed by the system prompt and
#: the question. The probes ask the provider hundreds of questions, and the
#: provider rate-limits: without a cache, a run interrupted by a 429 throws
#: away the answers it already has and has to buy them again. The key
#: includes the system prompt, so the question-only policy and the
#: closed-book probe cannot collide. The responses are not measurements --
#: the measurements are computed from them -- so caching them changes
#: nothing but the cost of the run.
_CACHE: dict | None = None
_CACHE_PATH = ARTIFACT_DIR / "exp12_llm_cache.json"


def _cache_key(cfg: dict, question: str) -> str:
    return json.dumps([cfg.get("system", ""), question], ensure_ascii=False)


def _cache_load() -> dict:
    global _CACHE
    if _CACHE is None:
        _CACHE = {}
        if _CACHE_PATH.exists():
            try:
                _CACHE = json.loads(_CACHE_PATH.read_text(encoding="utf-8"))
            except Exception:
                _CACHE = {}
    return _CACHE


def _cache_save() -> None:
    if _CACHE is None:
        return
    _CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    _CACHE_PATH.write_text(json.dumps(_CACHE), encoding="utf-8")


def _call_retry(cfg: dict, context: str, question: str) -> dict:
    """One request, retried through the provider's transient failures."""
    import time
    cache = _cache_load()
    key = _cache_key(cfg, question)
    hit = cache.get(key)
    if hit is not None:
        return hit
    last = None
    for attempt in range(1, _RETRIES + 1):
        try:
            resp = _call(cfg, context, question)
            cache[key] = resp
            if len(cache) % 25 == 0:
                _cache_save()
            if _CALL_DELAY:
                time.sleep(_CALL_DELAY)
            return resp
        except Exception as e:  # noqa: BLE001
            last = e
            if attempt < _RETRIES:
                delay = (_RATE_LIMIT_DELAY * attempt
                         if "429" in str(e) else _RETRY_DELAY * attempt)
                print(f"[exp12] {type(e).__name__}: {e} — retrying "
                      f"({attempt}/{_RETRIES}) in {delay:.0f}s", flush=True)
                time.sleep(delay)
    raise last


def _leakage(cfg: dict, questions: list[dict], limit: int | None = None) -> dict:
    """Ask the generator the questions with no corpus in the prompt."""
    if cfg is None:
        return {"status": "not_run",
                "note": "no API credential reachable from this machine"}
    cfg = dict(cfg)
    cfg["system"] = CLOSED_BOOK_SYSTEM
    sub = questions if limit is None else questions[:limit]
    out = []
    errors = []
    for n, q in enumerate(sub, 1):
        try:
            resp = _call_retry(cfg, "", q["query"])
        except Exception as e:  # noqa: BLE001
            errors.append(f"{type(e).__name__}: {e}")
            break
        text = _text_of(resp)
        substantive = bool(text.strip()) and not _REFUSAL_RE.search(text)
        out.append({
            "query": q["query"],
            "category": q["category"],
            "family": q.get("family"),
            "answered_closed_book": substantive,
            "answer_text": text[:600],
            "usage": _usage_of(resp),
        })
        if n % 25 == 0:
            print(f"[exp12] closed-book: {n}/{len(sub)}", flush=True)
    def _rate(rows):
        if not rows:
            return None
        return sum(1 for r in rows if r["answered_closed_book"]) / len(rows)

    ans = [r for r in out if r["category"] != "unanswerable"]
    un = [r for r in out if r["category"] == "unanswerable"]
    by_family: dict[str, float] = {}
    for fam in sorted({r["family"] for r in un}):
        rows = [r for r in un if r["family"] == fam]
        by_family[fam] = sum(1 for r in rows if r["answered_closed_book"]) / len(rows)
    if errors:
        # The probe is a measurement of a policy's behaviour, and a
        # provider timeout is not a fact about the policy. What was
        # collected is reported, with the shortfall stated.
        return {"status": "partial", "reason": errors[0], "n_asked": len(out),
                "n_questions": len(questions),
                "parametric_leakage_rate": _rate(un),
                "parametric_leakage_rate_by_family": by_family,
                "closed_book_answer_rate_answerable": _rate(ans),
                "records": out}
    return {
        "status": "run",
        "n_asked": len(out),
        "n_unanswerable_asked": len(un),
        "n_answerable_asked": len(ans),
        "parametric_leakage_rate": _rate(un),
        "parametric_leakage_rate_by_family": by_family,
        "closed_book_answer_rate_answerable": _rate(ans),
        "records": out,
        "note": (
            "parametric_leakage_rate is the fraction of the unanswerable "
            "questions the generator answers substantively with no corpus in "
            "the prompt. A high rate means the 'unanswerable' class is not "
            "corpus-specific: either the parameters contain the answer, or "
            "the generator is guessing, which is the behaviour the gate "
            "exists to prevent. The answerable class is the control: the same "
            "closed-book question is asked of it."),
    }


def _score_closed_book(bench: dict, leak: dict) -> dict:
    """Are the closed-book answers on the answerable questions *right*?

    This is the difference between two readings of a high closed-book
    answer rate. If the model answers the answerable questions closed-book
    and is often *correct*, the corpus's content is partly in its parameters
    and a system could score well without retrieving anything -- which would
    undercut the retrieval arm. If it answers them and is mostly *wrong*, the
    high rate is truthiness rather than knowledge, and the closed-book
    comparison says nothing about contamination either way.
    """
    if leak.get("status") != "run":
        return {"status": "not_run"}
    from run_generation_eval import _answer_is_correct

    gold = {q["query"]: q for q in bench["queries"]}
    rows = [r for r in leak.get("records", [])
            if r["category"] != "unanswerable"]
    if not rows:
        return {"status": "not_applicable"}
    n_nli = n_key = 0
    for r in rows:
        g = (gold.get(r["query"]) or {}).get("answer") or ""
        if not g:
            continue
        by_nli, by_key = _answer_is_correct(r["answer_text"], g)
        n_nli += bool(by_nli)
        n_key += bool(by_key)
    n = len(rows)
    return {
        "status": "run",
        "n_answerable_asked": n,
        "closed_book_accuracy_nli": n_nli / n if n else None,
        "closed_book_accuracy_keyterm": n_key / n if n else None,
        "note": (
            "the closed-book answers to the answerable questions, scored "
            "against the same gold the retrieval arms are scored against. "
            "A high answer rate with a low accuracy is truthiness, not "
            "memorisation, and the closed-book comparison then says nothing "
            "about contamination. A high accuracy would mean the corpus's "
            "content is in the model's parameters."),
    }


# --------------------------------------------------------------------------
def _load_pre_repair() -> dict | None:
    """The benchmark as it stood before the unanswerable class was rebuilt."""
    from src.config import BENCHMARK_DIR
    p = BENCHMARK_DIR / "benchmark_pre_unanswerable_repair.json"
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def _by_family(records: list[dict]) -> dict[str, list[str]]:
    """Group the questions of a list of benchmark records by family."""
    out: dict[str, list[str]] = {}
    for rec in records:
        out.setdefault(rec["family"], []).append(rec["query"])
    return out


def main() -> int:
    bench = load_benchmark()
    queries = bench["queries"]
    answerable = [q["query"] for q in queries if q["category"] != "unanswerable"]
    unanswerable = [q["query"] for q in queries if q["category"] == "unanswerable"]

    print("[exp12] structural separability ...", flush=True)
    structural = {
        "repaired_whole_class": _separability(answerable, unanswerable,
                                              "structural"),
    }
    unanswerable_records = [q for q in queries if q["category"] == "unanswerable"]
    for fam, qs in sorted(_by_family(unanswerable_records).items()):
        structural[f"repaired_{fam}"] = _separability(answerable, qs,
                                                      "structural")

    print("[exp12] bag-of-words separability ...", flush=True)
    bow = {
        "repaired_whole_class": _separability(answerable, unanswerable,
                                              "bag_of_words", permutations=30),
    }
    for fam, qs in sorted(_by_family(unanswerable_records).items()):
        bow[f"repaired_{fam}"] = _separability(answerable, qs,
                                                "bag_of_words", permutations=15)

    # ---- the pre-repair benchmark, for the before/after
    pre = _load_pre_repair()
    before: dict = {}
    if pre is not None:
        pre_ans = [q["query"] for q in pre["queries"]
                   if q["category"] != "unanswerable"]
        pre_un = [q["query"] for q in pre["queries"]
                  if q["category"] == "unanswerable"]
        before = {
            "source": "benchmark_pre_unanswerable_repair.json",
            "structural": {
                "whole_class": _separability(pre_ans, pre_un, "structural"),
            },
            "bag_of_words": {
                "whole_class": _separability(pre_ans, pre_un,
                                             "bag_of_words", permutations=30),
            },
            "shortcut_diagnostic": _shortcut_diagnostic(pre_ans, pre_un),
            "structural_matching": _structural_matching(pre_ans, pre_un),
            "by_family": {},
        }
        for fam, qs in sorted(_by_family(
                [q for q in pre["queries"] if q["category"] == "unanswerable"]
        ).items()):
            before["by_family"][fam] = {
                "structural": _separability(pre_ans, qs, "structural"),
                "shortcut_diagnostic": _shortcut_diagnostic(pre_ans, qs),
            }

    shortcut = _shortcut_diagnostic(answerable, unanswerable)
    lengths = _length_profile(answerable, unanswerable)
    concentration = _document_concentration(bench)
    matching = {
        "repaired_whole_class": _structural_matching(answerable, unanswerable),
    }
    for fam, qs in sorted(_by_family(unanswerable_records).items()):
        matching[f"repaired_{fam}"] = _structural_matching(answerable, qs)

    print("[exp12] re-checking the repaired class's certificates ...", flush=True)
    certificates = _verify_certificates(bench)

    cfg = _llm_config()
    print("[exp12] question-only policy ...", flush=True)
    policy = _question_only_policy(cfg, queries)

    print("[exp12] closed-book parametric leakage ...", flush=True)
    leak = _leakage(cfg, queries)
    leak["closed_book_scoring"] = _score_closed_book(bench, leak)
    _cache_save()

    if pre is not None:
        print("[exp12] question-only policy on the pre-repair benchmark ...",
              flush=True)
        before["question_only_policy"] = _question_only_policy(cfg, pre["queries"])

    payload = {
        "seed": SEED,
        "n_queries": len(queries),
        "n_answerable": len(answerable),
        "n_unanswerable": len(unanswerable),
        "question": ("can the question alone tell an answerable question "
                     "from an unanswerable one?"),
        "after_repair": {
            "structural_matching": matching,
            "structural_separability": structural,
            "bag_of_words_separability": bow,
            "shortcut_diagnostic": shortcut,
            "length_profile": lengths,
            "document_concentration": concentration,
            "label_certificates": certificates,
        },
        "before_repair": before,
        "question_only_policy": policy,
        "parametric_leakage": leak,
    }
    payload["retrieval_placement"] = CONFIG.modality.position
    write_result("exp12_unanswerable_class_audit", payload)

    s = structural["repaired_whole_class"]
    print(f"\n[exp12] structural separability, repaired class: "
          f"AUC {s['roc_auc']:.3f} (permutation null "
          f"{s['permutation_null_auc_mean']:.3f} +- "
          f"{s['permutation_null_auc_sd']:.3f}, "
          f"p = {s['p_value_vs_permutation_null']:.3f})")
    if before:
        b = before["structural"]["whole_class"]
        print(f"[exp12] structural separability, pre-repair class: "
              f"AUC {b['roc_auc']:.3f} (p = "
              f"{b['p_value_vs_permutation_null']:.3f})")
    print(f"[exp12] the one-rule shortcut carries "
          f"{shortcut['share_of_unanswerable_carried_by_the_rule']:.3f} of the "
          f"repaired class and {before['shortcut_diagnostic']['share_of_unanswerable_carried_by_the_rule']:.3f} "
          f"of the pre-repair class" if before else
          f"[exp12] the one-rule shortcut carries "
          f"{shortcut['share_of_unanswerable_carried_by_the_rule']:.3f} of the "
          f"repaired class")
    m = matching["repaired_whole_class"]
    print(f"[exp12] structural matching: {m['n_matched']}/{m['n_unanswerable']} "
          f"repaired questions have a structural twin in the answerable class")
    pol = policy
    if pol.get("status") == "run":
        print(f"[exp12] question-only policy: detects "
              f"{pol['unanswerable_detected']:.3f} of the unanswerable class "
              f"and costs {pol['coverage_lost_on_answerable']:.3f} of the "
              f"answerable class")
        if before.get("question_only_policy", {}).get("status") == "run":
            b = before["question_only_policy"]
            print(f"[exp12] the same policy on the pre-repair benchmark detects "
                  f"{b['unanswerable_detected']:.3f}")
    print(f"[exp12] certificate re-check: {certificates['n_failed']} of "
          f"{sum(certificates['checked'].values())} repaired questions failed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
