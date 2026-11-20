"""BM25 implemented from first principles.

Why this file exists
--------------------
`scikit-learn`'s ``TfidfVectorizer`` is not BM25, and `rank_bm25` hides the
formula behind a black box. The thesis needs to defend the exact scoring
function, its parameters, and its behaviour at the edges (empty query, term
absent from the corpus, zero-length document). So it is implemented here, in
plain Python + NumPy, with the derivation attached.

The derivation
--------------
Take the Probabilistic Relevance Framework (PRF) as the starting point. Under
PRF a document is relevant to a query with probability

    P(R | D, Q)  ∝  P(D | R, Q) * P(R | Q)

`P(R | Q)` is constant across documents and therefore irrelevant to *ranking*;
we drop it. What remains is a product over query terms:

    P(D | R, Q) = Π_{t in Q} P(t | D, R)

Three modelling decisions turn this product into the BM25 form.

**1. Term independence.** Assume the presence of one query term in a document
is independent of the presence of the others. This is known to be false -- it
is the "coordination level" assumption -- but it is what makes the score
computable in linear time and it is the assumption behind every IR system in
production.

**2. Which documents contain t?** If n_t of the N documents contain t, and we
assume the relevant documents contain the term more often than the
non-relevant ones, then the probability that a random document contains t is

    P(t | ¬R)  ≈  n_t / N
    P(t | R)   ≈  (N - n_t) / N

Under the independence assumption, the *ratio* of these likelihoods is what
carries the information about relevance, and taking logs turns the product
over terms into a sum:

    log P(D | R, Q) = Σ_{t in Q} log [ P(t | R) / P(t | ¬R) ]

This ratio is the **inverse document frequency**, IDF:

    IDF(t) = log [ (N - n_t + 0.5) / (n_t + 0.5) ]

The +0.5 terms are Robertson's smoothing: without them, a term appearing in
every document would give IDF = log(0) = -inf, and a term in exactly half
the documents would give IDF = 0 (neither evidence for nor against). The
+0.5 shifts the ratio so that IDF stays positive for common terms.

**3. Saturation and length normalisation.** The formula above assumes that
relevance depends only on *whether* a term is present, not how many times.
That is wrong: the tenth occurrence of "incoterm" in a document is much less
informative than the first. Robertson and Zaragoza (2009) fix this with two
adjustments.

*Saturation.* Replace the raw count f(t,D) with

    f(t,D) * (k1 + 1) / ( f(t,D) + k1 * (1 - b + b * |D|/avgdl) )

As f -> infinity this ratio tends to (k1+1), a constant. So the contribution
of a term saturates: ten occurrences count more than one, but not ten times
more. `k1` controls how fast saturation happens. k1 = 0 recovers the binary
"present/absent" model; k1 -> infinity recovers linear TF with no saturation
at all. The default k1 = 1.2 is the value Robertson et al. tuned and Lucene
has shipped since 8.x.

*Length normalisation.* The denominator contains (1 - b + b * |D|/avgdl). When
b = 0 the document length is ignored entirely. When b = 1, a document of
exactly average length gets denominator k1, a document twice as long as
average gets k1 * (1 + 1) = 2*k1, and a document half as long gets
k1 * 0.5. A long document therefore has to work harder to earn the same
score, which counteracts the fact that long documents match more terms by
accident. `b` = 0.75 is the standard default: full-ish normalisation, but
not so aggressive that short, precise documents are penalised.

Putting it together:

    BM25(q, D) = Σ_{t in Q} IDF(t) * [ f(t,D) * (k1 + 1) ]
                 / [ f(t,D) + k1 * (1 - b + b * |D| / avgdl) ]

Note what BM25 does *not* contain: no term-position information, no proximity
information, no stemming (that happens in the tokenizer), and no query-term
weighting other than through IDF.
"""
from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass

import numpy as np

#: Word tokens, optionally with internal hyphens/apostrophes so that
#: "safety-stock" and "operator's" survive as single tokens.
_TOKEN_RE = re.compile(r"[a-z0-9]+(?:[-'][a-z0-9]+)*")

#: Very common English function words carry no discriminative power and make
#: BM25's IDF term behave oddly on small corpora. This is a standard, small
#: stop list -- deliberately NOT aggressive, because industrial documents use
#: words like "order" and "stock" in genuinely technical senses.
STOPWORDS = frozenset(
    """
    a an the of and or to in for on at by with from as is are was were be been
    being it its this that these those there here we you they he she i not no
    """.split()
)


def tokenize(text: str, remove_stopwords: bool = True) -> list[str]:
    """Lowercase, split on non-word characters, optionally drop stopwords.

    This is a deliberately simple tokenizer. Production systems use Porter or
    Snowball stemming; for industrial documentation the words that matter
    (EOQ, Incoterms, Incoterm, FMEA, MOQ, SKU) do not have useful stems, and
    aggressive stemming breaks SKU-like tokens.
    """
    toks = _TOKEN_RE.findall(text.lower())
    if remove_stopwords:
        toks = [t for t in toks if t not in STOPWORDS]
    return toks


@dataclass
class BM25Index:
    """An in-memory inverted index that scores documents with BM25.

    Attributes
    ----------
    doc_ids:
        Document identifiers, position-aligned with every array below.
    postings:
        For each term, the list of document indices containing it and the
        term frequency in each.
    doc_len:
        Token count of each document (after tokenisation).
    avgdl:
        Mean document length. The normalisation constant.
    idf:
        Precomputed inverse document frequency per term.
    """

    doc_ids: list[str]
    postings: dict[str, tuple[np.ndarray, np.ndarray]]
    doc_len: np.ndarray
    avgdl: float
    idf: dict[str, float]
    k1: float
    b: float

    @classmethod
    def build(
        cls,
        documents: dict[str, str],
        k1: float = 1.2,
        b: float = 0.75,
        remove_stopwords: bool = True,
    ) -> "BM25Index":
        doc_ids = list(documents.keys())
        postings: dict[str, tuple[list[int], list[int]]] = {}
        doc_len = np.zeros(len(doc_ids), dtype=np.float64)

        for i, did in enumerate(doc_ids):
            toks = tokenize(documents[did], remove_stopwords)
            doc_len[i] = len(toks)
            counts = Counter(toks)
            for term, tf in counts.items():
                postings.setdefault(term, ([], []))[0].append(i)
                postings[term][1].append(tf)

        N = len(doc_ids)
        avgdl = float(doc_len.mean()) if N else 0.0

        idf: dict[str, float] = {}
        for term, (docs, _) in postings.items():
            n_t = len(docs)
            # Robertson +1 smoothing: keeps IDF >= 0 for ubiquitous terms.
            idf[term] = math.log((N - n_t + 0.5) / (n_t + 0.5) + 1.0)

        packed = {
            t: (
                np.asarray(d, dtype=np.int32),
                np.asarray(f, dtype=np.float64),
            )
            for t, (d, f) in postings.items()
        }
        return cls(doc_ids, packed, doc_len, avgdl, idf, k1, b)

    def score(self, query: str) -> np.ndarray:
        """Score every document against `query`.

        Returns a float array aligned with `self.doc_ids`. Documents that
        share no term with the query get exactly 0.0.
        """
        scores = np.zeros(len(self.doc_ids), dtype=np.float64)
        if not self.doc_ids:
            return scores
        toks = tokenize(query)
        # Repeated query terms should not multiply a document's score:
        # treat the query as a set for scoring (classic BM25 behaviour).
        for term in set(toks):
            entry = self.postings.get(term)
            if entry is None:
                continue  # term absent from corpus -> contributes nothing
            doc_idx, tf = entry
            idf_t = self.idf[term]
            norm = self.k1 * (1.0 - self.b + self.b * (self.doc_len[doc_idx] / self.avgdl))
            scores[doc_idx] += idf_t * (tf * (self.k1 + 1.0)) / (tf + norm)
        return scores

    def top_k(self, query: str, k: int) -> list[tuple[str, float]]:
        """Return the `k` highest-scoring (doc_id, score) pairs, best first."""
        scores = self.score(query)
        if k >= len(scores):
            order = np.argsort(-scores)
        else:
            part = np.argpartition(-scores, k)[:k]
            order = part[np.argsort(-scores[part])]
        return [(self.doc_ids[i], float(scores[i])) for i in order if scores[i] > 0.0]

    def explain(self, query: str, doc_id: str) -> list[tuple[str, float, float, int, float]]:
        """Per-term score breakdown for one document.

        Returns (term, idf, tf, doc_len, term_contribution) tuples. This is
        what you show a practitioner who asks "why did this document come
        back?", and it is what the paper's qualitative figure is built from.
        """
        idx = self.doc_ids.index(doc_id)
        rows = []
        for term in set(tokenize(query)):
            entry = self.postings.get(term)
            if entry is None:
                continue
            doc_idx, tf = entry
            where = np.where(doc_idx == idx)[0]
            if len(where) == 0:
                continue
            f = float(tf[where[0]])
            idf_t = self.idf[term]
            norm = self.k1 * (1.0 - self.b + self.b * (self.doc_len[idx] / self.avgdl))
            contribution = idf_t * (f * (self.k1 + 1.0)) / (f + norm)
            rows.append((term, idf_t, f, float(self.doc_len[idx]), contribution))
        return sorted(rows, key=lambda r: -r[4])
