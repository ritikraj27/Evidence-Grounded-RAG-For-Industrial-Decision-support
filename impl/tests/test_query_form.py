"""Tests for the runtime query-form check.

The check refuses requests that are not questions, so the failure it can
have is a *false rejection*: refusing a question the corpus could have
answered. The tests therefore pin the hard cases as firmly as the easy ones
-- an acronym subject, a hyphenated subject, a gerund noun, a bare keyword
and a well-formed out-of-domain question must all pass -- and the fixture
files in `tests/fixtures/` carry the population the rates are measured on.

Run with:  .venv/bin/python impl/tests/test_query_form.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.query_form import assess_query_form  # noqa: E402

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def _fixture(name: str) -> dict:
    return json.loads((FIXTURES / f"{name}_queries.json").read_text(encoding="utf-8"))


def test_the_four_rules_fire_where_they_are_meant_to():
    """Each rule rejects its own population, and nothing else."""
    empty = assess_query_form("")
    assert empty.rejected and empty.rule == "empty", empty

    nowords = assess_query_form("42%")
    assert nowords.rejected and nowords.rule == "no_words", nowords

    nocontent = assess_query_form("What is this?")
    assert nocontent.rejected and nocontent.rule == "no_content", nocontent

    incomplete = assess_query_form("What is the cost of?")
    assert incomplete.rejected and incomplete.rule == "incomplete", incomplete

    ok = assess_query_form("What is the economic order quantity?")
    assert ok.valid and ok.rule == "", ok
    print("  ok  the four form rules fire on their own populations")


def test_the_hard_valid_cases_pass():
    """The cases the benchmark's own filter rejects must not be refused.

    `_subject_is_usable` in the benchmark builder rejects "FMEA" for being one
    word, "root-cause analysis" for the hyphen and "pick and pack
    warehousing" for ending in "-ing". A runtime check that reused it would
    refuse "What is reliability engineering?" and "What is logistics?" --
    ordinary questions. These are the cases the check has to get right.
    """
    for q in ("What is FMEA?", "What is MTBF?", "What is IT?",
              "What is root-cause analysis?", "What is flow-shop scheduling?",
              "What is pick and pack warehousing?", "What is performance monitoring?",
              "EOQ", "EOQ?", "safety stock", "material requirements planning",
              "reorder point for SKU A-104", "What is the EOQ for SKU A-104?",
              "Who won the 1998 FIFA World Cup final?"):
        a = assess_query_form(q)
        assert a.valid, f"the form check refused a valid query: {q!r} ({a.rule})"
    print("  ok  acronyms, hyphens, gerunds, terse keywords and out-of-domain "
          "questions all pass")


def test_the_valid_fixture_is_not_falsely_rejected():
    """No well-formed query in the fixture may be refused."""
    fx = _fixture("valid")
    wrong = []
    for entry in fx["queries"]:
        a = assess_query_form(entry["query"])
        if a.rejected:
            wrong.append((entry["query"], a.rule))
    assert not wrong, f"false rejections: {wrong}"
    print(f"  ok  none of the {len(fx['queries'])} well-formed queries is refused")


def test_the_malformed_fixture_is_rejected():
    """Every malformed query in the fixture must be refused, except the ones
    whose miss is deliberate and recorded in the fixture itself."""
    fx = _fixture("malformed")
    wrong = []
    for entry in fx["queries"]:
        expected = entry.get("expect", "reject")
        a = assess_query_form(entry["query"])
        got = "reject" if a.rejected else "accept"
        if got != expected:
            wrong.append((entry["query"], expected, got))
    assert not wrong, f"wrong verdicts: {wrong}"
    n_rejected = sum(1 for e in fx["queries"]
                      if assess_query_form(e["query"]).rejected)
    print(f"  ok  {n_rejected} of {len(fx['queries'])} malformed queries are refused")


def test_the_check_fails_open():
    """A query the check cannot judge must be passed on, not refused.

    The check has no dictionary and no language model, so a keyboard mash is
    invisible to it. Refusing on a guess would be a false rejection, and a
    false rejection is the one failure this framework is about avoiding. The
    fixture records these two cases as expected misses.
    """
    for q in ("asdf", "xyzzy plugh"):
        assert assess_query_form(q).valid, f"the check refused a query it cannot judge: {q!r}"
    print("  ok  the check fails open on input it cannot judge")


def test_a_query_ending_on_a_number_is_not_truncated():
    """A trailing number is the end of the question, not the word before it.

    The regression test for a false rejection the measurement found: three of
    the benchmark's own queries end on a number -- "what was the population of
    Paris in 1850?" -- and a tokeniser that drops bare numbers judges the
    preposition in front of them instead, refusing a well-formed question.
    """
    for q in ("What was the population of Paris in 1850?",
              "According to the table in the source document, what is the DPMO for 691,462?",
              "According to the table in the source document, what is the Percent defective for 0.023%?",
              "What is the EOQ for SKU A?"):
        a = assess_query_form(q)
        assert a.valid, f"the form check refused a valid query: {q!r} ({a.rule})"
    print("  ok  a query ending on a number or a one-character code passes")


def test_a_upper_case_token_counts_as_content():
    """An acronym is content even when it is also a function word.

    "IT" in an industrial corpus is Information Technology, not the pronoun.
    The exemption is deliberately narrow -- two characters, all capitals -- and
    its cost is that all-caps input is judged more leniently, which is the
    safe direction.
    """
    assert assess_query_form("What is IT?").valid
    assert assess_query_form("What is it?").rejected
    print("  ok  an upper-case acronym counts as content")


if __name__ == "__main__":
    print("=== query form tests ===")
    test_the_four_rules_fire_where_they_are_meant_to()
    test_the_hard_valid_cases_pass()
    test_the_valid_fixture_is_not_falsely_rejected()
    test_the_malformed_fixture_is_rejected()
    test_the_check_fails_open()
    test_a_query_ending_on_a_number_is_not_truncated()
    test_a_upper_case_token_counts_as_content()
    print("all query form tests passed")
