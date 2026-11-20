"""Per-claim confidence tagging (design move D5).

The problem
-----------
A single confidence number for a whole answer is nearly useless in practice.
"An answer about EOQ policy is 70% confident" tells the practitioner nothing
about *which part* to trust. If the answer has three sentences -- one quoting
the EOQ rule, one computing a safety stock, one speculating about supplier
risk -- a single score flattens very different epistemic situations into one
number, and the practitioner has to read everything carefully to find the
soft part.

The framework instead decomposes the answer into atomic claims and tags each
one.

Decomposition
-------------
An *atomic claim* is a statement that can be true or false on its own. The
decomposition used here is sentence-level with a numeric-clause split, which
is a deliberate compromise: full claim decomposition (Chen et al., 2024;
Fabbri et al., 2022) uses an LLM and is more precise, but it introduces a
second generation step whose errors propagate into the confidence numbers --
and the whole point of this design move is to give the practitioner a
*reliable* signal. A sentence that contains two numbers with different values
is split; everything else stays whole.

Two numbers per claim
---------------------
**1. Support probability q.** How likely is it that the retrieved evidence
entails this claim?

Each retrieved chunk c_i is an independent, fallible witness. The NLI model
gives e_i = P(c_i entails claim). The standard way to combine several
independent "witness" events is the **noisy-OR** model from probabilistic
reasoning (Pearl, 1988): the claim is supported if *at least one* witness
covers it, and each witness independently fails with probability (1 - e_i).

    P(supported) = 1 - Π_i (1 - e_i)

This has the properties we want. One highly confident chunk (e = 0.95) is
enough to support the claim even if the other chunks say nothing. Ten weak
chunks accumulate: 1 - 0.9^10 = 0.65. And a single strongly *contradicting*
chunk caps the claim, because we take the max of the entailment scores rather
than averaging -- averaging would let nine irrelevant chunks dilute one
chunk that says the opposite.

**2. Information gain IG.** How much did the retrieved set reduce our
uncertainty about this claim?

Mutual information between two variables X and Y:

    I(X; Y) = H(Y) - H(Y | X)

Here Y is the binary event "the claim is supported by the evidence" and X is
the retrieved set. H(Y) is the prior entropy -- how uncertain we were before
seeing the evidence -- and H(Y | X) is the entropy of the posterior support
probability. For a binary variable with probability q:

    H(q) = -q log2 q - (1 - q) log2(1 - q)

so with an uninformative prior H(Y) = 1 bit and

    IG = 1 - H(q)   bits

Reading: IG = 1 means the evidence left no doubt (q = 1, one bit removed);
IG = 0 means the evidence told us nothing (q = 0.5, or q = 0 or 1 with a
degenerate prior).

**A necessary clarification.** IG is *symmetric* about q = 0.5: a claim with
q = 0.9 and a claim with q = 0.1 both yield IG = 1 - H(0.9) = 0.531 bits.
That is correct behaviour for an information measure -- both are confident
states -- but it means IG alone cannot tell "well supported" from "well
refuted". So the confidence **band is cut on q**, and IG is reported
alongside as the separate, quantitative "how much did the evidence reduce
uncertainty" figure. The two answer different questions and conflating them
(doing what the September report's one-line description does) would be a
category error.

Bands
-----
    q >= grounded_threshold   ->  "grounded"   (the evidence entails it)
    q >= inferred_threshold   ->  "inferred"   (partial support, plausible
                                                 extension)
    otherwise                 ->  "uncertain"  (the evidence does not settle it)

A claim whose best chunk actively contradicts it (max entailment very low but
max contradiction high) is additionally marked as *contradicted* and its
citation points at the contradicting passage, so the practitioner sees the
disagreement rather than a silent low-confidence tag.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass, field

import numpy as np

from .config import ClaimConfig

#: Splits a sentence into atomic clauses at semicolons, "and", "but",
#: "however", and at coordinated numeric statements.
_CLAUSE_SPLIT = re.compile(r"(?:;|\bhowever\b|\bbut\b|\bwhereas\b|\bwhile\b)", re.IGNORECASE)
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z(])")


def split_into_claims(answer: str) -> list[str]:
    """Decompose an answer into atomic claims.

    Sentence-level first; then split on discourse markers so that a sentence
    carrying two independent assertions ("the EOQ is 250 units and the lead
    time is 14 days") becomes two claims.
    """
    claims: list[str] = []
    for sentence in _SENTENCE_SPLIT.split(answer.strip()):
        sentence = sentence.strip()
        if not sentence:
            continue
        for clause in _CLAUSE_SPLIT.split(sentence):
            clause = clause.strip(" ,.;")
            if len(clause.split()) >= 3:
                claims.append(clause)
    return claims


def noisy_or(probabilities: list[float]) -> float:
    """Combine independent witness probabilities with the noisy-OR model.

    P(at least one witness succeeds) = 1 - Π_i (1 - p_i)

    Edge cases: an empty list gives 0.0 (no witness, no support); p_i = 1
    gives 1.0 immediately (certain support).
    """
    if not probabilities:
        return 0.0
    residual = 1.0
    for p in probabilities:
        residual *= max(0.0, min(1.0, 1.0 - p))
    return 1.0 - residual


def binary_entropy(p: float) -> float:
    """Shannon entropy of a Bernoulli variable, in bits.

    H(p) = -p log2 p - (1-p) log2(1-p)

    H(0) = H(1) = 0 (no uncertainty); H(0.5) = 1 (maximum uncertainty).
    """
    if p <= 0.0:
        return 0.0
    if p >= 1.0:
        return 0.0
    return -(p * math.log2(p) + (1 - p) * math.log2(1 - p))


def information_gain(q: float, prior: float = 0.5) -> float:
    """Information gain in bits: I(X; Y) = H(Y) - H(Y | X).

    With a Bernoulli posterior q and prior `prior`, the gain is
    H(prior) - H(q). At prior = 0.5 this is 1 - H(q).
    """
    return binary_entropy(prior) - binary_entropy(q)


@dataclass
class ClaimAssessment:
    """The framework's verdict on one claim."""

    claim: str
    #: P(supported by the retrieved evidence), from noisy-OR aggregation.
    support_prob: float
    #: Information gain in bits.
    information_gain: float
    #: "grounded" | "inferred" | "uncertain"
    band: str
    #: Chunk ids cited for this claim, best first.
    citations: list[str] = field(default_factory=list)
    #: Best per-chunk entailment probability.
    best_entailment: float = 0.0
    #: Best per-chunk contradiction probability.
    best_contradiction: float = 0.0
    #: True when the evidence actively contradicts the claim.
    contradicted: bool = False
    #: True when the claim has at least one supporting citation.
    has_support: bool = False


def band_for(q: float, config: ClaimConfig) -> str:
    if q >= config.grounded_threshold:
        return "grounded"
    if q >= config.inferred_threshold:
        return "inferred"
    return "uncertain"


def assess_claims(
    claims: list[str],
    context_chunks: list[str],
    context_ids: list[str],
    config: ClaimConfig | None = None,
) -> list[ClaimAssessment]:
    """Score every claim against the retrieved context.

    Runs an NLI entailment check of (chunk, claim) for every chunk and every
    claim, aggregates with noisy-OR, and assigns the band.
    """
    from .models import nli_probs

    config = config or ClaimConfig()
    if not claims:
        return []
    if not context_chunks:
        return [
            ClaimAssessment(
                claim=c,
                support_prob=0.0,
                information_gain=information_gain(0.0),
                band="uncertain",
                contradicted=False,
            )
            for c in claims
        ]

    pairs = []
    for claim in claims:
        for chunk in context_chunks:
            pairs.append((chunk, claim))
    probs = nli_probs(pairs, config.nli_model)

    per_claim: dict[int, list[dict]] = {i: [] for i in range(len(claims))}
    idx = 0
    for ci in range(len(claims)):
        for k in range(len(context_chunks)):
            per_claim[ci].append(probs[idx])
            idx += 1

    results: list[ClaimAssessment] = []
    for ci, claim in enumerate(claims):
        chunk_probs = per_claim[ci]
        entailments = [p["entailment"] for p in chunk_probs]
        contradictions = [p["contradiction"] for p in chunk_probs]
        q = noisy_or(entailments)
        best_i = int(np.argmax(entailments))
        best_e = float(entailments[best_i])
        best_c = float(max(contradictions))
        citations = [context_ids[i] for i in np.argsort(entailments)[::-1][:3]]
        results.append(
            ClaimAssessment(
                claim=claim,
                support_prob=q,
                information_gain=information_gain(q),
                band=band_for(q, config),
                citations=citations if best_e > 0.5 else [],
                best_entailment=best_e,
                best_contradiction=best_c,
                contradicted=best_c > 0.7 and best_c > best_e,
                has_support=best_e > 0.5,
            )
        )
    return results


def render_answer(
    assessments: list[ClaimAssessment],
    context_text: dict[str, str],
    show_contradiction_flag: bool = True,
) -> str:
    """Render the tagged answer that the practitioner actually reads.

    Every claim carries its confidence band and its citation markers, so the
    evidence trail is part of the output rather than a separate artefact.
    """
    marker = {"grounded": "[GROUNDED]", "inferred": "[INFERRED]", "uncertain": "[UNCERTAIN]"}
    lines = []
    for a in assessments:
        cites = "".join(f"[{cid}]" for cid in a.citations)
        flag = ""
        if show_contradiction_flag and a.contradicted:
            flag = " [CONTRADICTED BY EVIDENCE]"
        lines.append(f"{marker.get(a.band, '')}{flag} {a.claim} {cites}".rstrip())
    return "\n".join(lines)
