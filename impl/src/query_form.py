"""Runtime validation of the *form* of a query.

The confidence gate decides whether the retrieved context can support an
answer. It never asks whether the query is a well-formed question, because
that is a different property and it is decided before retrieval rather than
after it. This module holds that check.

Why it is not the benchmark builder's rule
------------------------------------------
`scripts/build_benchmark.py` has a filter called `_subject_is_usable`, and it
looks like it does this job. It does not, and reusing it would be a serious
mistake: it is a *question-generation* filter. It asks "does this extracted
noun phrase make a good question?", and it answers "no" for reasons that have
nothing to do with whether a question is well formed. It rejects "FMEA"
because the subject is one word, "root-cause analysis" because of the hyphen,
and "pick and pack warehousing" because the subject ends in "-ing". Those are
perfectly good questions, and a runtime check that refused them would refuse
valid user input. Its job is to keep bad questions *out of the benchmark*; this
module's job is to keep bad *requests* out of the generator.

What it rejects
---------------
Only what cannot be a query at all:

  R1 ``empty``       the query is empty or whitespace
  R2 ``no_words``    the query contains no alphabetic character
  R3 ``no_content``  every word is a function word or a deictic, so there is
                     nothing to look up ("what is this?")
  R4 ``incomplete``  the query ends on a word that cannot end an English
                     question ("what are units that?", "what is the cost of?")

What it deliberately does not reject
------------------------------------
A terse keyword query ("safety stock", "EOQ?"), a hyphenated or acronym
subject ("what is root-cause analysis?", "what is FMEA?"), a query with no
question mark ("material requirements planning"), or a question that is well
formed but out of the corpus's domain ("who won the 1998 FIFA World Cup?").
The last of those is the *gate's* job and not this one's: refusing it here
would claim evidence reasoning that a form check cannot do, and it would make
the form check's refusal rate meaningless as a measurement of form.

Every rule here is a **false-rejection** risk, and in this framework a false
rejection is a refusal of a question the corpus can answer -- the one failure
mode the whole design is about avoiding. The rates are measured, not asserted:
`experiments/run_form_validator.py` reports the rejection rate on malformed
input and the false-rejection rate on well-formed input, and the deliverables
quote them.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

#: Words that carry no retrieval content: articles, prepositions, coordinators,
#: auxiliaries, pronouns, deictics, quantifiers and the wh-words. A query
#: built only from these has no subject to look up.
NON_CONTENT_WORDS = frozenset("""
a an the
of in on at to for from by with about against between among through during
before after above below under over into onto upon within without across
behind beyond per via
and or but nor so yet
is are was were be been being am do does did done has have had having
can could will would shall should may might must
i me my mine myself we us our ours ourselves you your yours yourself
he him his she her hers it its they them their theirs themselves
this that these those there here
one ones all any some none no not nothing anything something everything
many much most more less few fewer least several such both each either
neither other others another same
what which who whom whose when where why how whether whatever whichever
following preceding previous latter former
""".split())

#: Words that cannot end a well-formed English question. A query that ends on
#: one of these is a truncated fragment. This list is deliberately narrower
#: than `NON_CONTENT_WORDS`: quantifiers and negations are excluded, because
#: "is the answer none?" and "is the answer no?" are well formed, and a rule
#: that refused them would be refusing valid questions.
CANNOT_END_WORDS = frozenset("""
of in on at to for from by with about against between among through during
before after above below under over into onto upon within without across
behind beyond per via
and or but nor so yet
a an the
is are was were be been being am do does did has have had having
can could will would shall should may might must
that which who whom whose what when where why how whether
than as if then
i me my we us our you your he him his she her it its they them their
""".split())

#: A token is treated as an acronym or a unit code -- and therefore as
#: content -- when it is at least two characters long and written entirely in
#: upper case. "IT" in an industrial corpus is Information Technology, not the
#: pronoun; "EOQ" is a term. The cost of this exemption is a missed rejection
#: on all-caps input, which is the safe direction: the check fails open
#: towards retrieval rather than towards a refusal.
_ACRONYM_MIN_LENGTH = 2

#: Words are the runs of letters, with any internal digits and hyphens kept,
#: so that "A-104", "H2O" and "SKU-A-2" survive as single tokens. A token
#: must start with a letter, so a bare number is not a word.
_WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9\-]*")

#: The last word of a query, for the truncation rule. This is a run of
#: letters and digits, so a query ending in a number -- "what was the
#: population of Paris in 1850?" -- ends on "1850" and not on the "in" before
#: it. Tokenising for the content rule cannot be used for this: it drops
#: bare numbers, and a query ending in one would then be judged on the word
#: before it, which is a preposition in exactly the queries that are fine.
_LAST_RUN_RE = re.compile(r"[A-Za-z0-9]+")

#: The refusal shown to a user whose query cannot be answered because it is
#: not a question. It is deliberately distinct from the evidence gate's
#: refusal: the two say different things and the user needs to know which one
#: happened.
FORM_REFUSAL_MESSAGE = (
    "This request cannot be answered because it is not a well-formed question "
    "({detail}). Rephrase it as a question about the indexed documentation "
    "-- for example, name the quantity, the method or the term you are asking "
    "about. No answer has been generated."
)


@dataclass(frozen=True)
class FormAssessment:
    """The verdict of the form check on one query.

    `rule` names the rule that fired, and is empty when the query is valid.
    `detail` is the human-readable reason, used in the refusal message.
    """

    valid: bool
    rule: str = ""
    detail: str = ""

    @property
    def rejected(self) -> bool:
        return not self.valid


def _tokens(query: str) -> list[str]:
    """The alphabetic tokens of the query, in order."""
    return [t.rstrip("-") for t in _WORD_RE.findall(query)]


def _last_word(query: str) -> str:
    """The last run of letters and digits in the query, or "" if there is none."""
    runs = _LAST_RUN_RE.findall(query)
    return runs[-1] if runs else ""


def _is_content(token: str) -> bool:
    """Whether a token carries something to look up.

    An upper-case token of two or more characters is an acronym or a unit
    code and counts as content; everything else counts as content only if it
    is not a function word.
    """
    if len(token) >= _ACRONYM_MIN_LENGTH and token.isupper():
        return True
    return token.lower() not in NON_CONTENT_WORDS


def assess_query_form(query: str) -> FormAssessment:
    """Decide whether `query` is a well-formed enough request to retrieve for.

    The check is conservative by design: it refuses only what cannot be a
    query, because a refusal here is a refusal of something the corpus may
    well be able to answer.
    """
    if query is None or not query.strip():
        return FormAssessment(False, "empty", "the query is empty")

    tokens = _tokens(query)
    if not tokens:
        return FormAssessment(False, "no_words",
                              "the query contains no words, only punctuation "
                              "or numbers")

    if not any(_is_content(t) for t in tokens):
        return FormAssessment(
            False, "no_content",
            "the query contains no subject to look up, only words like "
            "'what', 'is' or 'this'")

    last = _last_word(query)
    # A one-character final word is more likely an identifier than an
    # English word -- "SKU A" is a stock code, not the article -- and a
    # two-or-more character upper-case word is an acronym.
    if (len(last) >= _ACRONYM_MIN_LENGTH
            and not (last.isupper() and any(c.isalpha() for c in last))
            and last.lower() in CANNOT_END_WORDS):
        return FormAssessment(
            False, "incomplete",
            f"the query ends on '{last}', which cannot end a question -- it "
            f"looks truncated")

    return FormAssessment(True)
