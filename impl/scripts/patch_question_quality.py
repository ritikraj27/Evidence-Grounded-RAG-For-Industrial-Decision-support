#!/usr/bin/env python3
"""Reject malformed generated questions.

A quarter of the benchmark's answerable questions were malformed. The
generator matched a subject with a permissive regex, so a match that started
mid-clause or after a truncated word produced a question no one would ask:

    "What is since manufacturing in an existing plant?"
    "What value is stated for a teep in the source documentation?"

Both are artefacts of the source markup, not of the subject matter. They also
inflate the benchmark's apparent difficulty in a way that was never intended,
because the question's answer is not in the chunk in any meaningful sense.

This adds a plausibility check on the extracted subject, and a check on the
extracted answer, so that a question is only emitted when it is a question a
person would ask about a document.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "scripts" / "build_benchmark.py"

HELPERS = '''
#: A generated question is only usable if its subject is a plausible noun
#: phrase. The permissive regexes above can match mid-clause or after a
#: truncated word, and the result is not a question anybody would ask.
_VERB_LIKE = frozenset("""
    is are was were has have had will can could should would does do did
    been being than that which who whom whose when where while if then
""".split())

#: Words that cannot begin or end a subject phrase.
_BAD_EDGE = frozenset("""
    the a an of in on at to for and or but with by from as that this these
    those its his her their our your my not no also than into onto over
    under about after before between during through against within
""".split())

#: A number, optionally with a unit, for the numeric-fact branch.
_VALUE_RE = re.compile(
    r"^\\d[\\d,]*(?:\\.\\d+)?\\s?(?:%|percent|hours?|hrs?|days?|weeks?|"
    r"months?|years?|units?|kg|km|minutes?|m|cm|mm|s|sec|seconds?)?$",
    re.IGNORECASE,
)


def _subject_is_usable(subject: str) -> bool:
    """True when the matched subject reads like a noun phrase."""
    words = subject.split()
    if len(words) < 2 or len(words) > 8:
        return False
    lowered = [w.lower().strip(",;:\\"'()") for w in words]
    if not all(lowered):
        return False
    if lowered[0] in _BAD_EDGE or lowered[-1] in _BAD_EDGE:
        return False
    if any(w in _VERB_LIKE for w in lowered):
        return False
    # A subject must be words, not markup or punctuation.
    if not all(w.isalpha() for w in words):
        return False
    # A truncated word shows up as a very short token among long ones.
    if min(len(w) for w in words) < 3:
        return False
    # A subject made of the same word twice is an artefact.
    if len(set(lowered)) < 2:
        return False
    return True


def _value_is_usable(value: str) -> bool:
    """True when the extracted answer is a number with an optional unit."""
    return bool(_VALUE_RE.match(value.strip()))
'''

OLD_DEF = '''    for m in DEFINITION_RE.finditer(prose):
        subject = m.group(1).strip()
        if len(subject.split()) > 7:
            continue'''
NEW_DEF = '''    for m in DEFINITION_RE.finditer(prose):
        subject = m.group(1).strip()
        if len(subject.split()) > 7:
            continue
        if not _subject_is_usable(subject):
            continue
        answer = m.group(2).strip()
        # The answer has to be a clause, not a fragment of markup.
        if len(answer) < 25 or not answer[0].isupper() and not answer[0].islower():
            continue
        if "[[" in answer or "]]" in answer:
            continue'''

OLD_NUM = '''        for m in NUMERIC_RE.finditer(prose):
            subject = m.group(1).strip()
            value = m.group(2).strip()
            if len(subject.split()) > 6 or not value:
                continue'''
NEW_NUM = '''        for m in NUMERIC_RE.finditer(prose):
            subject = m.group(1).strip()
            value = m.group(2).strip()
            if len(subject.split()) > 6 or not value:
                continue
            if not _subject_is_usable(subject):
                continue
            if not _value_is_usable(value):
                continue'''


def main() -> int:
    s = TARGET.read_text(encoding="utf-8")
    failures = []
    for old, new in ((OLD_DEF, NEW_DEF), (OLD_NUM, NEW_NUM)):
        if s.count(old) != 1:
            failures.append(f"count={s.count(old)} -> {old[:60]!r}")
            continue
        s = s.replace(old, new, 1)
    if HELPERS not in s:
        anchor = "def questions_from_text("
        if s.count(anchor) != 1:
            failures.append("questions_from_text anchor not found")
        else:
            s = s.replace(anchor, HELPERS.strip("\n") + "\n\n\n" + anchor, 1)
    if failures:
        for f in failures:
            print(f"!! {f}")
        return 1
    TARGET.write_text(s, encoding="utf-8")
    print("  the question generator now rejects malformed subjects and answers")
    return 0


if __name__ == "__main__":
    sys.exit(main())
