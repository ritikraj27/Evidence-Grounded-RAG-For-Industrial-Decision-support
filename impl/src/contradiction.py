"""Contradiction detection: the joint NLI + topical gate (design move D4).

The problem this solves
-----------------------
When two retrieved passages disagree, a plain RAG system hands both to the
generator and lets it pick one -- usually silently, usually without telling
the user. In an industrial corpus, silent disagreement resolution is
dangerous: two SOP revisions with different safety-stock rules look exactly
like two relevant passages, and the generator will pick whichever one the
prompt ordering favours.

The naive fix -- run an NLI model on every pair of retrieved passages and
report a contradiction when it fires -- fails in a specific and predictable
way. NLI models are trained on premise/hypothesis pairs where the two texts
are *about the same thing*. Feed them two passages about different subtopics
("the safety stock rule for the Kharagpur plant" vs "the lead time for the
Chennai vendor") and the model must produce a label anyway; it often produces
"contradiction" because the two texts assert different things, even though
nothing is actually in conflict. That is a false positive.

The fix: require two independent gates to agree.

**Gate 1 -- logical conflict.** An NLI model checks whether passage A
contradicts passage B: does A make B false?

    contradiction(A, B) = 1 if NLI says A contradicts B else 0

**Gate 2 -- same subject.** Before a disagreement can be a *contradiction*,
the two passages must be talking about the same thing. Otherwise "the policy
changed in 2024" and "the plant runs three shifts" are not in conflict; they
are just different sentences. This gate is implemented with two independent
signals, and *both* are required:

    (a) Embedding similarity. cos(e_A, e_B) >= topic_threshold means the two
        passages are semantically close.

    (b) Shared concrete objects. The two passages must mention some of the
        same concrete objects: part numbers, plant codes, quantities, and
        named things. Jaccard overlap on this set >= entity_overlap_min. Two
        passages with high semantic similarity but zero shared objects are
        almost always about different things that happen to be phrased
        similarly.

The conjunction is what suppresses the false positives:

    flag(A, B) = contradiction(A, B) AND same_subject(A, B)

Why this is the right design rather than a tuned threshold: raising the NLI
threshold alone reduces false positives only by also excluding genuine
conflicts (both errors fall together). Adding an independent, orthogonal
signal -- shared objects -- lets the two error types be traded off
separately.

**The repair that the measurement forced.** The implementation of gate 2 used
to let high semantic similarity through *on its own*, which is not what the
design says. On a corpus of articles all about one subject that made gate 2 a
*topic* check, and two chunks of the same article about different sub-topics
passed it. The reader labelling in Experiment 11 showed the consequence: of the
alarms the readers saw, the ones they called "different subjects" were
suppressed by requiring shared objects, and the ones they called "no
conflict" were not. Requiring both signals, as designed, cut the alarms on
the focus corpus from 75 to 11.

**Additional signal: quantity conflict.** Two passages that attach different
values to the same measured quantity (EOQ = 250 vs EOQ = 400) conflict even
when the NLI model is lukewarm, because the contradiction is explicit. This
module detects it by finding numbers shared between the two passages (same
measurement term) but with different values.

The quantity branch carries the same subject check as the conjunction
branch: a numeric difference between two passages about different things is
not a conflict either.

**Additional signal: revision conflict.** Two passages that describe the same
term at two different issues of the same named standard are not necessarily
contradicting each other -- they may be describing the same rule before and
after it was revised, which is exactly the case a practitioner needs to be
told about, because only one of them is current. This branch is exact rather
than statistical: it reads the version markers out of the text, so it can be
scored by inspection rather than by reader labels.

**Surfacing is gated on measurement.** Each branch has a *measured* precision,
from the reader labelling. A branch whose measured precision is below the
calibration floor has its findings recorded and withheld rather than shown to
a practitioner. This is the discipline the answer gate applies to an answer,
applied to the framework's own claims.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from .config import ARTIFACT_DIR, ContradictionConfig

#: A number, optionally with a unit or a thousands separator.
_NUMBER_RE = re.compile(
    r"(?<![\w.])(\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)\s*"
    r"(%|percent|kg|km|hours?|hrs?|days?|units?|pcs|mtpa|million|billion|eur|inr|usd|\$)?",
    re.IGNORECASE,
)

#: The regulatory unit vocabulary. A regulation states its limits in the
#: units of physics and chemistry -- micrograms per cubic meter, psi,
#: decibels, volts -- and the shipped list has none of them, so a regulatory
#: exposure limit is not recognised as a quantity at all.
_REGULATORY_NUMBER_RE = re.compile(
    r"(?<![\w.])(\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)\s*"
    r"(%|percent|micrograms?|milligrams?|grams?|kilograms?|pounds?|tons?|"
    r"ppm|parts per million|psig|psi|volts?|amperes?|watts?|"
    r"decibels?|db|inches|inch|feet|foot|miles?|"
    r"hours?|hrs?|days?|minutes?|seconds?|months?|years?|"
    r"units?|pcs|mtpa|million|billion|eur|inr|usd|\$|"
    r"cubic meters?|cubic feet|square feet|square inches|gallons?|liters?|"
    r"degrees|percent|micron|mils?)?",
    re.IGNORECASE,
)

_NUMBER_RE_BY_PROFILE = {
    "operations": _NUMBER_RE,
    "regulatory": _REGULATORY_NUMBER_RE,
}

#: Tokens that look like concrete identifiers: part numbers, plant codes,
#: standard references, alphanumeric SKUs.
_ENTITY_RE = re.compile(r"\b(?:[A-Z]{2,}[-_]?\d{2,}[-_]?[A-Z0-9]*|SKU[-_]?\w+|ISO[-_]?\d+|IEC[-_]?\d+|EN[-_]?\d+)\b")


@dataclass
class ContradictionFinding:
    """One detected contradiction (or rejected candidate)."""

    chunk_a: str
    chunk_b: str
    #: P(contradiction) from the NLI model.
    nli_contradiction_prob: float
    #: Cosine similarity of the two chunk embeddings.
    topical_similarity: float
    #: Jaccard overlap of shared entities/numbers.
    entity_overlap: float
    #: True when both gates fired.
    flagged: bool
    #: Human-readable reason, always populated (also for rejected candidates).
    reason: str = ""
    #: Numeric conflicts found, if any. The numeric branch carries the same
    #: subject check as the conjunction branch, so this list is empty for a
    #: pair that fails it.
    numeric_conflicts: list[dict] = field(default_factory=list)
    #: The NLI-and-same-subject conjunction on its own, without the numeric
    #: branch. The full gate is this OR a numeric conflict, so on the subset
    #: of pairs that *have* a numeric conflict the full gate's recall is 1.0
    #: by construction. This field is what makes the conjunction's own
    #: contribution measurable.
    nli_and_subject: bool = False
    #: True when the pair was flagged by the numeric branch alone.
    numeric_only: bool = False
    #: Which branch raised the finding: "semantic" (the NLI-and-subject
    #: conjunction), "quantity" (the measurement-keyed numeric branch) or
    #: "revision" (the exact version-conflict branch).
    kind: str = "semantic"
    #: Revision conflicts found, if any.
    revision_conflicts: list[dict] = field(default_factory=list)
    #: Whether this finding is shown to the practitioner. A finding is
    #: surfaced only when the *measured* precision of the branch that raised
    #: it clears the calibration floor; otherwise it is recorded, with the
    #: reason, and withheld. This is the discipline the answer gate applies
    #: to an answer, applied to the framework's own claims.
    surfaced: bool = True
    #: Why a finding was withheld, when it was.
    surface_reason: str = ""


#: Small bare numbers are not identifiers. "5", "10" and "2" appear in almost
#: every technical passage, so including them makes the Jaccard overlap of
#: two unrelated passages look substantial. Only numbers with three or more
#: digits, or a unit attached, are distinctive enough to count.
_MIN_DISTINCTIVE_NUMBER = 100


def extract_entities(text: str) -> set[str]:
    """Distinctive identifiers and quantities mentioned in a passage.

    Two rules, both learned from a measurement that went wrong the first time:

    1. A *code-like* token (SKU-104, ISO-9001, PN-23) is an identifier.
    2. A bare number is an identifier only if it is large enough to be
       distinctive (three or more digits) or carries a unit. Small bare
       numbers are shared by nearly every technical passage and destroy the
       discriminative power of the overlap measure.
    """
    ents: set[str] = set()
    for m in _ENTITY_RE.finditer(text):
        ents.add(m.group(0).lower())
    for m in _NUMBER_RE.finditer(text):
        raw = m.group(1).replace(",", "")
        unit = (m.group(2) or "").lower()
        try:
            magnitude = float(raw)
        except ValueError:
            magnitude = 0.0
        if magnitude < _MIN_DISTINCTIVE_NUMBER and not unit:
            continue
        ents.add(f"{raw}|{unit}")
    return ents


def entity_jaccard(a: str, b: str) -> float:
    """Jaccard index of the entity sets of two passages.

    J(A,B) = |A ∩ B| / |A ∪ B|

    Returns 0.0 when either passage has no entities, since two passages with
    no concrete identifiers cannot be confirmed to be about the same subject.
    """
    ea, eb = extract_entities(a), extract_entities(b)
    if not ea or not eb:
        return 0.0
    return len(ea & eb) / len(ea | eb)


#: Words that are capitalised for grammatical reasons rather than because
#: they name something: sentence openings, pronouns, and the everyday nouns
#: that a technical article capitalises at the start of a heading.
_PROPER_NOUN_STOP = frozenset("""
the a an and or of in on at to for from with by as is are was were be been this
that these those it its their his her our your they he she we you i not no
also however therefore thus which who whom whose what when where why how all
any each more most less least other another such same than then so if but while
during after before between among within without over under above below up down
out off into onto new old first second third last next previous main major minor
note figure table section chapter article paper book journal volume issue
""".split())

#: A capitalised word or phrase, up to three words long, optionally ending in
#: a short designator: "Incoterms", "CIF", "Plant A".
_PROPER_NOUN_RE = re.compile(
    r"\b[A-Z][A-Za-z'-]{2,}(?:\s+[A-Z][A-Za-z'-]*){0,2}\b")

#: A content word: three letters or more, lower case.
_CONTENT_WORD_RE = re.compile(r"[a-z][a-z'-]{2,}")

#: Words too generic to identify a subject. "the safety stock of plant A"
#: and "the safety stock of plant B" disagree about a quantity; "the number
#: of units" and "the number of days" do not, because "units" and "days"
#: name no particular measurement. This list also carries the ordinary
#: English function words, which are shared by every passage and so say
#: nothing about subject identity.
_CONTENT_STOP = frozenset("""
number amount quantity value rate level count total sum average mean median
maximum minimum max min figure datum data item units unit day days week weeks
month months year years hour hours minute minutes second seconds
percent percentage order production capacity output input cost price time
size length weight height depth speed factor index score scale ratio share
the and for with from that this these those its their there then than when
where while have has had been were will would could should shall must may
can not but you they them he she was were are our your his her him
one two three four five six seven eight nine ten about into over under
after before during between among within without above below up down out off
per via also more most less least such same other another each any all
first second third last next previous new old made make made
""".split())


def content_terms(text: str) -> set[str]:
    """The content words a passage uses, with the generic ones removed.

    Ordinary industrial prose names its subject in lower case -- "the axial
    pump assembly", "the safety stock level", "the control plan" -- so a
    subject check that only reads capitalised tokens cannot see it. This is
    the third kind of "concrete object", and on prose it carries most of the
    signal.
    """
    return {w for w in _CONTENT_WORD_RE.findall(text.lower())
            if w not in _CONTENT_STOP}


def proper_nouns(text: str, instance_identifier: bool = False) -> set[str]:
    """Distinctive named things a passage mentions.

    These are the *instance* identifiers: "Plant A", "Incoterms", "Kharagpur".
    A quantity conflict needs the two passages to be about the same
    instance, not merely the same measurement, and this is what tells the
    two apart -- "Plant A" and "Plant B" share the word "plant" and nothing
    else.

    A capitalised token is a candidate. It is dropped when it is the first
    word of a sentence (that is capitalisation, not a name), and when every
    word in it is in the stop list.
    """
    out: set[str] = set()
    for m in _PROPER_NOUN_RE.finditer(text):
        raw = m.group(0).split()
        if m.start() == 0 or text[m.start() - 1] in ".!?\n":
            # A sentence opening: the capitalisation is grammatical, so the
            # first word is dropped and the rest of the name is kept.
            #
            # The exception is a name whose last word is a single capital
            # letter. "Plant A" and "Plant B" are two instances, and the
            # instance check is the only thing that tells them apart; but
            # "A" is on the stop list as the English article, so dropping
            # the first word of "Plant A" leaves nothing and the instance
            # disappears. A single trailing capital letter is an instance
            # identifier, not an article.
            keep = (instance_identifier and len(raw) > 1
                    and len(raw[-1]) == 1 and raw[-1].isupper())
            if not keep:
                raw = raw[1:]
        # A single capital letter inside a name is an instance identifier and
        # is kept, even though "a" is on the stop list as the English
        # article: "Plant A" and "Plant B" have to come out as two different
        # names, and dropping the letter from both would leave them
        # sharing "Plant".
        words = [w for w in raw
                 if w.lower() not in _PROPER_NOUN_STOP
                 or (instance_identifier and len(w) == 1 and w.isupper())]
        if not words:
            continue
        out.add(" ".join(words))
    return out


def subject_terms(text: str) -> set[str]:
    """Every concrete object a passage names.

    Part numbers and plant codes, distinctive quantities, and content words.
    The three together are what "the same subject" has to mean.
    """
    return extract_entities(text) | content_terms(text)


def subject_jaccard(a: str, b: str) -> float:
    """Jaccard index over the concrete objects two passages name.

    J(A,B) = |A ∩ B| / |A ∪ B|

    Returns 0.0 when either passage names nothing concrete, since two
    passages with no shared object cannot be confirmed to be about the same
    subject.
    """
    ta, tb = subject_terms(a), subject_terms(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def shared_instance(a: str, b: str,
                     instance_identifier: bool = False) -> bool:
    """True when two passages name the same *instance* of a thing.

    Two passages can be about the same measurement at two different sites --
    Plant A's reorder point and Plant B's reorder point -- and that is not a
    conflict. Telling them apart needs an instance identifier: a plant code,
    a product name, a line. This is what an industrial document has and an
    encyclopaedia does not.
    """
    return bool(proper_nouns(a, instance_identifier)
                & proper_nouns(b, instance_identifier))


#: Measurement terms -- nouns that name a measurable quantity. A number
#: becomes a *quantity* only when one of these governs it, and the term is
#: what the two passages must agree on.
#:
#: This list replaces an earlier rule that keyed a number to "the nearest
#: distinctive word" in the 60 characters before it. That rule was measured
#: in Experiment 11 and it was the source of the contradiction gate's
#: alarms: on encyclopaedic text the nearest distinctive word is a surname
#: ("Dettmer H., 1998" against "Dettmer W., 2006"), a month name ("Retrieved
#: 8 December 2007" against "December 1995"), a publisher ("Productivity
#: Press", "Management Science") or a version marker ("Incoterms 2020"
#: against "Incoterms 2010"). Every one of the 21 numeric conflicts that
#: rule produced was a citation artifact; not one was a measurement.
#:
#: The vocabulary is written from the operations and supply-chain domain and
#: is applied uniformly. It is a declared prior, not something fitted to
#: the corpus.
_OPERATIONS_MEASUREMENT_TERMS = frozenset("""
eoq wip oee tat cpk
inventory stock buffer capacity throughput productivity
utilisation utilization yield scrap rework defect downtime uptime turnover
demand batch headcount employees staff weight volume distance speed
temperature pressure cost price revenue margin profit budget
shipment shipments cargo freight labor labour
""".split())

#: The quantities a regulation binds on: exposure limits, physical
#: dimensions, pressures, electrical ratings, and the physical constants a
#: chemical or material standard is written in.
_REGULATORY_MEASUREMENT_TERMS = _OPERATIONS_MEASUREMENT_TERMS | frozenset("""
exposure limit limit clearance depth diameter width height length
thickness concentration dose level rating tolerance leakage emissions
opacity particulate frequency illumination luminance velocity displacement
containment separation elevation fall distance travel distance
net explosive content explosive content flashpoint vapor specific gravity
viscosity acidity toxicity flammability combustibility ignition
penetration resistance hardness gauge coating weight
amount quantity size storage load span rise run gap overlap
""".split())

_MEASUREMENT_TERMS_BY_PROFILE = {
    "operations": _OPERATIONS_MEASUREMENT_TERMS,
    "regulatory": _REGULATORY_MEASUREMENT_TERMS,
}

#: Multi-word measurement terms. Matched before the single-word list, so
#: "reorder point" wins over any single word inside it.
_MEASUREMENT_PHRASES = (
    "economic order quantity",
    "on-time delivery",
    "capacity utilization",
    "machine utilization",
    "reorder point",
    "safety stock",
    "lead time",
    "cycle time",
    "setup time",
    "changeover time",
    "batch size",
    "lot size",
    "delivery time",
    "fill rate",
    "flow rate",
    "production rate",
    "defect rate",
    "scrap rate",
    "service level",
    "work in process",
)

#: The multi-word measurement terms a regulation binds on. "Permissible
#: exposure limit" has to be matched before "exposure limit", which is why
#: the phrase list is scanned longest-first.
_REGULATORY_MEASUREMENT_PHRASES = _MEASUREMENT_PHRASES + (
    "permissible exposure limit",
    "exposure limit",
    "action level",
    "time weighted average",
    "sound pressure level",
    "noise dose",
    "flash point",
    "boiling point",
    "vapor pressure",
    "specific gravity",
    "net explosive content",
    "maximum safe working pressure",
    "maximum allowable pressure",
    "dilation pressure",
    "design pressure",
    "test pressure",
    "degrees fahrenheit",
    "degrees celsius",
    "wire rope",
    "handrail height",
    "guard height",
    "safety factor",
)

_MEASUREMENT_PHRASES_BY_PROFILE = {
    "operations": _MEASUREMENT_PHRASES,
    "regulatory": _REGULATORY_MEASUREMENT_PHRASES,
}

#: A bare four-digit number in this range is a year, not a quantity. The
#: range is deliberately narrow: encyclopaedic prose writes years in four
#: digits and writes quantities in two, three, five or more digits far more
#: often.
_YEAR_LOW, _YEAR_HIGH = 1500, 2100

#: Scale words. "3 billion" is a magnitude, not a unit, so they are folded
#: into the value rather than the key.
_SCALE_WORDS = frozenset({"million", "billion", "trillion"})

#: Words of a measurement term, as they appear in the text.
_TERM_WORD_RE = re.compile(r"[A-Za-z][A-Za-z\-]*")

#: Lower-case words that may sit *inside* a capitalised name without ending
#: it: "International Journal of Operations and Production Management".
_NAME_CONNECTORS = frozenset(
    {"and", "of", "for", "in", "on", "at", "by", "to", "the", "&"})


def _title_runs(text: str) -> tuple[list[tuple[str, int]], set[int]]:
    """Tokenise ``text`` and mark the tokens that sit inside a proper name.

    A proper name is a run of two or more capitalised tokens, possibly
    separated by short connecting words. This is what distinguishes a
    measurement ("inventory was cut by 92%") from the same word used as
    part of a venue or publisher name ("Productivity Press", "Operations &
    Production Management"). A single capitalised word is not a name: it is
    usually just the first word of a sentence.
    """
    raw = [(m.group(0), m.end()) for m in _TERM_WORD_RE.finditer(text)]
    tokens = [(w.lower(), end) for w, end in raw]
    caps = [w[:1].isupper() for w, _ in raw]
    flagged: set[int] = set()
    i = 0
    while i < len(tokens):
        if not caps[i]:
            i += 1
            continue
        k, n_cap = i + 1, 1
        while k < len(tokens):
            if caps[k]:
                n_cap += 1
                k += 1
            elif tokens[k][0] in _NAME_CONNECTORS:
                k += 1
            else:
                break
        if n_cap >= 2:
            flagged.update(range(i, k))
        i = k
    return tokens, flagged


def _measurement_key(
    tokens: list[tuple[str, int]],
    flagged: set[int],
    before: int,
    profile: str = "operations",
    lookback: int = 0,
) -> str:
    """The measurement term governing a number, or "" when there is none.

    ``before`` is the character offset at which the number starts. The term
    chosen is the one whose last word ends closest to the number, so "the
    reorder point was set to 40 units" keys on "reorder point" and not on an
    earlier term in the sentence.

    ``profile`` selects the measurement vocabulary: the shipped
    operations vocabulary, or the regulatory one.
    """
    terms = _MEASUREMENT_TERMS_BY_PROFILE.get(
        profile, _OPERATIONS_MEASUREMENT_TERMS)
    phrases = _MEASUREMENT_PHRASES_BY_PROFILE.get(
        profile, _MEASUREMENT_PHRASES)
    idxs = [i for i, (_w, end) in enumerate(tokens) if end <= before]
    if not idxs:
        return ""
    idxs = [i for i in idxs if tokens[i][1] > before - 60]
    best, best_end = "", -1
    for pos, i in enumerate(idxs):
        # The term may end up to `lookback` tokens before the number. The
        # shipped rule required it to be the token immediately before, which
        # fits "the reorder point was set to 40 units" and does not fit
        # "the permissible exposure limit for cadmium is 5 micrograms per
        # cubic meter", where the noun phrase is separated from the number
        # by the thing being limited and the copula. Because the
        # vocabulary is declared, the look-back is bounded rather than
        # open: it cannot reach a surname or a month name that no
        # vocabulary entry would match.
        for gap in range(0, lookback + 1):
            end = pos - gap
            if end < 0:
                continue
            for span in (3, 2, 1):
                if end - span + 1 < 0:
                    continue
                first = idxs[end - span + 1]
                phrase = " ".join(tokens[j][0]
                                  for j in idxs[end - span + 1: end + 1])
                known = (
                    phrase in phrases
                    or (span == 1 and phrase in terms)
                )
                if not known:
                    continue
                # A single-word term that begins a proper name is part of
                # that name, not a measurement. Multi-word phrases are
                # exempt: a phrase like "lead time" names a quantity rather
                # than a venue, and rejecting phrases would cost recall on
                # the instance-level corpora where real quantity conflicts
                # live.
                if span == 1 and first in flagged:
                    continue
                if tokens[end][1] > best_end:
                    best, best_end = phrase, tokens[end][1]
                break
            if best:
                break
    return best


def numeric_conflicts(
    text_a: str,
    text_b: str,
    subject_gate: bool | None = None,
    instance_gate: bool | None = None,
    profile: str = "operations",
    lookback: int = 0,
) -> list[dict]:
    """Find quantities that both passages name but attach different values to.

    A number is counted only when a **measurement term** governs it. The
    term is what the number is a measurement *of*, and it is the key the two
    passages must agree on. Numbers that no measurement term governs are
    not quantities at all: they are years, page numbers, ISBN and DOI
    fragments, citation counts, or section numbers.

    Three numbers are excluded explicitly, each for a reason that was
    measured rather than assumed:

    * a bare four-digit number in the year range, which is a date;
    * a number that is part of a hyphenated identifier (``915299-14-3``),
      which is a code fragment;
    * a number smaller than three digits with no unit, which is shared by
      nearly every passage.

    A measurement term that begins a proper name is not a measurement
    either: "Productivity Press" and "International Journal of Operations
    & Production Management" are venues, and the pages and ISBN digits
    around them are not quantities.

    The key carries the unit, so "5 days" and "5 hours" are different
    quantities and are not compared with each other.

    Parameters
    ----------
    subject_gate:
        When False, the branch returns nothing. The contradiction gate
        requires the same-subject check for the numeric branch too: two
        passages about different things that happen to state different
        numbers are not in conflict.
    instance_gate:
        When False, the branch returns nothing. A quantity conflict is only
        a conflict if the two passages are about the *same instance* -- Plant
        A's reorder point and Plant B's reorder point are two different
        reorder points, not one reorder point with two values.
    """
    if subject_gate is False or instance_gate is False:
        return []

    def keyed_numbers(text: str) -> dict[str, set[str]]:
        out: dict[str, set[str]] = {}
        tokens, flagged = _title_runs(text)
        number_re = _NUMBER_RE_BY_PROFILE.get(profile, _NUMBER_RE)
        for m in number_re.finditer(text):
            raw = m.group(1).replace(",", "")
            unit = (m.group(2) or "").lower()
            try:
                magnitude = float(raw)
            except ValueError:
                continue
            if unit in _SCALE_WORDS:
                # A magnitude, not a unit: fold it into the value.
                raw = f"{raw}{unit}"
                unit = ""
            if not unit and _YEAR_LOW <= magnitude <= _YEAR_HIGH:
                continue
            if magnitude < _MIN_DISTINCTIVE_NUMBER and not unit:
                continue
            # A number inside a hyphenated identifier is a code fragment.
            if m.start() > 0 and text[m.start() - 1] in "-–":
                continue
            term = _measurement_key(tokens, flagged, m.start(), profile, lookback)
            if not term:
                continue
            key = f"{term}|{unit}"
            out.setdefault(key, set()).add(raw)
        return out

    ka, kb = keyed_numbers(text_a), keyed_numbers(text_b)
    conflicts = []
    for key in set(ka) & set(kb):
        va, vb = ka[key], kb[key]
        # A conflict requires the two passages to attach *different* values to
        # the same quantity name. Sharing a name with overlapping values is
        # agreement, not conflict.
        if va == vb:
            continue
        if va & vb:
            # They agree on at least one value; only the extra values differ.
            if len(va) == 1 or len(vb) == 1:
                continue
        term, _, unit = key.partition("|")
        conflicts.append({"quantity": term, "unit": unit,
                           "values_a": sorted(va), "values_b": sorted(vb)})
    return conflicts


#: A named standard or document followed by a version. The version families
#: that carry the meaning are the standards bodies and the rules themselves;
#: the revision markers are how a document says which issue it is.
_STANDARD_VERSION_RE = re.compile(
    r"\b(incoterms?|iso|iec|astm|ansi|nist|ieee|bs|en|"
    r"rev(?:ision)?|version|edition|issue|amendment)\s*\.?\s*"
    r"(\d{1,4}(?:\.\d+)?)\b",
    re.IGNORECASE,
)

#: A bare "v3" version marker.
_SHORT_VERSION_RE = re.compile(r"\bv\s*\.?\s*(\d{1,3}(?:\.\d+)?)\b",
                               re.IGNORECASE)

#: A standard citation that carries its edition.
#:
#: The shipped vocabulary reads a version marker as a family word followed by
#: a number -- "Incoterms 2020", "ISO 9001" -- and takes the *qualifier*
#: from an acronym near the marker. A regulation cites standards the other
#: way round: the standard has a number and the edition is attached to it
#: ("ASTM A47-68", "ISO 817:2014(E)", "ANSI Z87.1-2010", "IEC 79-10-1995").
#:
#: So the regulatory profile reads the edition out of the citation, and the
#: qualifier is the standard's own number -- which is the thing that has to
#: match for two passages to be about the same standard. The shipped
#: vocabulary's qualifier is a nearby acronym, and an acronym is often a
#: constant ("FR", "ANSI"), which is why it produces false revision
#: conflicts on regulatory text.
_REGULATORY_STANDARD_RE = re.compile(
    r"\b(?P<family>iso|iec|astm|ansi|nist|ieee|bs|ul|sae|api|asme)\s*"
    r"(?P<number>[A-Z]{0,4}\d{1,5}(?:[.\-][A-Za-z0-9]{1,6}){0,3})\s*"
    r"[\-–:]\s*(?P<edition>\d{2,4})\b",
    re.IGNORECASE)

#: An acronym-style term: two to six capitals. These are the identifiers that
#: name a *specific* thing inside a standard -- CIF, CIP, SKU, EOQ.
_ACRONYM_RE = re.compile(r"\b[A-Z]{2,6}\b")

#: A code-like token: SKU-104, ISO-9001, SOP-12.
_CODE_RE = re.compile(r"\b[A-Z]{2,}[-_]?\d{2,}[-_]?[A-Z0-9]*\b")

#: How far back to look for the term a version qualifies.
_QUALIFIER_WINDOW = 40


#: The revision markers and the standards families, normalised. "Rev 4" and
#: "Revision 4" are the same family; a bare "v2" is its own.
_FAMILY_ALIASES = {
    "rev": "revision",
    "revision": "revision",
    "version": "version",
    "edition": "edition",
    "issue": "issue",
    "amendment": "amendment",
    "incoterm": "incoterms",
    "incoterms": "incoterms",
    "iso": "iso",
    "iec": "iec",
    "astm": "astm",
    "ansi": "ansi",
    "nist": "nist",
    "ieee": "ieee",
    "bs": "bs",
    "en": "en",
}


def standard_versions(text: str, profile: str = "commercial"
                     ) -> dict[str, dict[str, set[str]]]:
    """The versions of named standards a passage describes, and what they qualify.

    "CIF Incoterms 2020" gives {"incoterms": {"2020": {"CIF"}}}: the
    version 2020 of the Incoterms family, and the term it qualifies.

    The qualifier is what makes this branch usable. A passage that merely
    *mentions* an older version in passing -- "which is a change from
    Incoterms 2010" -- does not describe that version, and a version that
    qualifies nothing is not the passage's version either. Only a version
    that qualifies a named term can be the version a passage is about.

    The `regulatory` profile reads a different shape of citation: the
    standard's number with its edition attached, where the number is the
    qualifier and the edition is the version.
    """
    if profile == "regulatory":
        out: dict[str, dict[str, set[str]]] = {}
        for m in _REGULATORY_STANDARD_RE.finditer(text):
            family = m.group("family").lower()
            number = m.group("number").upper()
            edition = m.group("edition")
            out.setdefault(family, {}).setdefault(edition, set()).add(number)
        return out

    out = {}
    for m in _STANDARD_VERSION_RE.finditer(text):
        family = _FAMILY_ALIASES.get(m.group(1).lower().rstrip("."), None)
        if family is None:
            continue
        version = m.group(2)
        before = text[max(0, m.start() - _QUALIFIER_WINDOW):m.start()]
        after = text[m.end():m.end() + _QUALIFIER_WINDOW]
        quals = set()
        for window in (before, after):
            for q in (list(_ACRONYM_RE.finditer(window))
                      + list(_CODE_RE.finditer(window))):
                quals.add(q.group(0))
        out.setdefault(family, {}).setdefault(version, set()).update(quals)
    for m in _SHORT_VERSION_RE.finditer(text):
        out.setdefault("v", {}).setdefault(m.group(1), set())
    return out


def acronyms(text: str) -> set[str]:
    """Acronym-style terms: CIF, CIP, SKU, EOQ."""
    return set(m.group(0) for m in _ACRONYM_RE.finditer(text))


def revision_conflicts(text_a: str, text_b: str,
                       profile: str = "commercial") -> list[dict]:
    """Find pairs that describe the same term at two different versions.

    This is a different question from the semantic contradiction branch, and
    it is one the corpus can answer. Two passages that qualify the *same
    term* with *different versions* of the same named standard are
    describing the same rule at two points in its life. The practitioner
    needs to know that, because the two passages can state different
    requirements and only one of them is current.

    Two exclusions keep the branch honest, and both were forced by
    measurement rather than assumed:

    * a version that qualifies no term is not a version the passage is
      about. "the 11 pre-defined terms of Incoterms 2020" mentions a
      version; it does not describe one rule at that version.
    * a version mentioned only in passing is a reference, not the
      passage's version. "which is a change from Incoterms 2010" describes
      the rule as it is *now*.

    The criterion is a fact about the text rather than a judgement about
    it, which is why this branch can be scored by inspection while the
    semantic branch needs reader labels.
    """
    va, vb = standard_versions(text_a, profile), standard_versions(text_b, profile)
    shared = set(va) & set(vb)
    if not shared:
        return []
    conflicts = []
    for family in sorted(shared):
        # The versions each passage actually describes, with the terms they
        # qualify. A version that qualifies nothing is a mention, not a
        # description, and is dropped.
        da = {v: q for v, q in va[family].items() if q}
        db = {v: q for v, q in vb[family].items() if q}
        if not da or not db:
            continue
        if set(da) & set(db):
            # They describe the same version: not two different issues.
            continue
        terms = set()
        for qa in da.values():
            for qb in db.values():
                terms |= qa & qb
        terms = {t for t in terms if t.lower() != family}
        if not terms:
            continue
        conflicts.append({
            "standard": family,
            "versions_a": sorted(da),
            "versions_b": sorted(db),
            "shared_terms": sorted(terms),
        })
    return conflicts


#: The measured precision of each branch, and the floor below which a branch
#: is not shown to anyone. This is the same discipline the answer gate
#: applies to an answer, applied to the framework's own claims: a branch
#: whose measured precision does not clear the floor is computed, recorded,
#: and withheld.
#:
#: The calibration is fitted by Experiment 11 (the reader labelling) and
#: shipped as an artefact, exactly as the gate's Platt coefficients are.
#: A branch with no calibration is surfaced, because nothing has been
#: measured against it; the absence of a measurement is not a measurement.
@dataclass
class ConflictCalibration:
    """Measured precision per branch, and the floor for surfacing one."""
    #: branch name -> measured precision (0.0-1.0)
    precision: dict[str, float] = field(default_factory=dict)
    #: branch name -> how many findings the precision was measured on
    n_measured: dict[str, int] = field(default_factory=dict)
    #: the floor a branch's measured precision must clear to be surfaced
    min_precision: float = 0.5

    def allows(self, kind: str) -> tuple[bool, str]:
        """Whether this branch may surface a finding, and why."""
        if kind not in self.precision:
            return True, ""
        p = self.precision[kind]
        n = self.n_measured.get(kind, 0)
        if p >= self.min_precision:
            return True, ""
        return False, (
            f"the {kind} branch's measured precision is {p:.3f} on {n} "
            f"labelled findings, below the {self.min_precision:.2f} floor, so "
            f"the finding is recorded and withheld")


#: Where the fitted conflict calibration lives, if it has been fitted. It
#: sits with the gate's fitted model, in the variant's artefact directory.
CALIBRATION_PATH = ARTIFACT_DIR / "conflict_calibration.json"


def load_calibration(path: Path | None = None) -> ConflictCalibration:
    """Load the fitted conflict calibration, or an empty one.

    An empty calibration surfaces every branch, because nothing has been
    measured against it. The absence of a measurement is not a measurement.
    """
    p = path or CALIBRATION_PATH
    if not p.exists():
        return ConflictCalibration()
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return ConflictCalibration()
    return ConflictCalibration(
        precision={k: float(v) for k, v in
                   (raw.get("precision") or {}).items()},
        n_measured={k: int(v) for k, v in
                    (raw.get("n_measured") or {}).items()},
        min_precision=float(raw.get("min_precision", 0.5)),
    )


def detect_contradictions(
    chunks: list[str],
    chunk_ids: list[str],
    embeddings: np.ndarray | None = None,
    config: ContradictionConfig | None = None,
    calibration: ConflictCalibration | None = None,
    probs: list[dict[str, float]] | None = None,
) -> list[ContradictionFinding]:
    """Run the joint NLI + subject gate over every pair of context chunks.

    Parameters
    ----------
    chunks:
        The accepted context chunks (post-gate).
    chunk_ids:
        Their identifiers, aligned with `chunks`.
    embeddings:
        (n, d) matrix of chunk embeddings, used for the topical similarity
        gate. If None, the gate falls back to entity overlap only.
    calibration:
        The measured precision of each branch. A finding whose branch has
        been measured below the floor is recorded and withheld rather than
        surfaced.
    probs:
        Pre-computed NLI probabilities for the pairs, in the order this
        function would build them. Passing them lets a caller score many
        pairs in one batched model call instead of one call per pair, which
        is the difference between minutes and hours when the pairs are
        scored a few hundred at a time.
    """
    from .models import nli_probs

    config = config or ContradictionConfig()
    calibration = calibration or load_calibration()
    findings: list[ContradictionFinding] = []
    n = len(chunks)
    if n < 2:
        return findings

    pairs = []
    index_pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            pairs.append((chunks[i], chunks[j]))
            index_pairs.append((i, j))
            if len(pairs) >= config.max_pairs:
                break
        if len(pairs) >= config.max_pairs:
            break

    if probs is None:
        probs = nli_probs(pairs, config.nli_model)

    for (i, j), p in zip(index_pairs, probs):
        a, b = chunks[i], chunks[j]
        nli_c = p["contradiction"]

        if embeddings is not None:
            from .models import cosine_similarity_matrix

            sim = float(
                cosine_similarity_matrix(
                    embeddings[i : i + 1], embeddings[j : j + 1]
                )[0, 0]
            )
        else:
            sim = float("nan")

        ent = subject_jaccard(a, b)
        # The same-subject check is what the design says it is: "two
        # passages with high semantic similarity but zero shared entities
        # are almost always about different things". The implementation used
        # to let high similarity through on its own, which on a corpus of
        # articles about one subject made the check a *topic* check and let
        # through every pair of chunks in the article. It is now the
        # conjunction of the two signals, as designed.
        same_subject = bool(
            (sim == sim and sim >= config.topic_threshold)
            and ent >= config.entity_overlap_min
        )

        num_conf = numeric_conflicts(a, b, subject_gate=same_subject,
                                     instance_gate=shared_instance(
                                         a, b, config.instance_identifier),
                                     profile=config.measurement_profile,
                                     lookback=config.measurement_lookback)
        rev_conf = revision_conflicts(a, b, profile=config.standard_profile)
        nli_fires = nli_c >= config.nli_threshold
        conjunction = bool(nli_fires and same_subject)

        # A more specific branch wins the label. A revision conflict is the
        # actionable version of "these two disagree": it says the rule
        # changed, not that one of the two is wrong, and it says which is
        # current. A quantity conflict is likewise more specific than a bare
        # semantic one, because it names the quantity that disagrees.
        if rev_conf:
            kind = "revision"
            flagged = True
            reason = (
                f"the two passages describe the same term at two different "
                f"issues of the same standard: {rev_conf}"
            )
        elif num_conf:
            kind = "quantity"
            flagged = True
            reason = (
                f"the two passages attach different values to the same "
                f"measured quantity: {num_conf}"
            )
        elif conjunction:
            kind = "semantic"
            flagged = True
            reason = (
                f"NLI contradiction probability {nli_c:.3f} >= "
                f"{config.nli_threshold:.2f} and the same-subject check "
                f"passed (cos={sim:.3f}, shared-object Jaccard={ent:.3f})"
            )
        else:
            kind = "semantic"
            flagged = False
            reasons = []
            if not nli_fires:
                reasons.append(
                    f"NLI contradiction probability {nli_c:.3f} < {config.nli_threshold:.2f}"
                )
            if not same_subject:
                reasons.append(
                    f"the same-subject check failed (cos={sim:.3f}, "
                    f"shared-object Jaccard={ent:.3f})"
                )
            reason = "; ".join(reasons)

        surfaced, surface_reason = calibration.allows(kind)

        findings.append(
            ContradictionFinding(
                chunk_a=chunk_ids[i],
                chunk_b=chunk_ids[j],
                nli_contradiction_prob=float(nli_c),
                topical_similarity=sim,
                entity_overlap=ent,
                flagged=flagged,
                reason=reason,
                numeric_conflicts=num_conf,
                nli_and_subject=conjunction,
                numeric_only=bool(num_conf) and not conjunction,
                kind=kind,
                revision_conflicts=rev_conf,
                surfaced=surfaced,
                surface_reason=surface_reason,
            )
        )
    return findings


def contradiction_summary(findings: list[ContradictionFinding]) -> dict:
    """Summarise detections for the report table.

    ``nli_only_flagged`` counts pairs the bare NLI gate would have flagged
    (nli_prob >= threshold) regardless of the topical gate. The difference
    between that number and ``flagged`` is the false positives the topical
    gate suppresses.

    The summary also reports how the findings split between the three
    branches and how many are *surfaced*: a finding whose branch has a
    measured precision below the calibration floor is recorded and withheld.
    """
    total = len(findings)
    nli_only = sum(1 for f in findings if f.nli_contradiction_prob >= 0.70)
    flagged = sum(1 for f in findings if f.flagged)
    by_kind: dict[str, int] = {}
    for f in findings:
        if f.flagged:
            by_kind[f.kind] = by_kind.get(f.kind, 0) + 1
    return {
        "pairs_compared": total,
        "nli_only_flagged": nli_only,
        "joint_gate_flagged": flagged,
        "suppressed_false_positives": max(nli_only - flagged, 0),
        "false_positive_rate_nli_only": (nli_only - flagged) / nli_only if nli_only else 0.0,
        "false_positive_rate_joint": (nli_only - flagged) / nli_only if nli_only else 0.0,
        "flagged_by_kind": by_kind,
        "surfaced": sum(1 for f in findings if f.flagged and f.surfaced),
        "withheld": sum(1 for f in findings if f.flagged and not f.surfaced),
    }
