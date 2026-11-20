#!/usr/bin/env python3
"""Scan the report and the deck for AI-writing tells and stray dashes.

The user asked for prose that does not read as machine-written. That is not
a thing a checker can settle on its own, but the loudest tells can be
counted, and a checker that fails the build on them is worth more than a
checker's opinion.

What it looks for:

  * the long dashes -- an em dash, an en dash, a minus sign, a figure dash.
    The brief was plain hyphens only, and a dash that survived in a heading
    is the kind of thing a reader notices without being able to say why.
  * the stock phrases of the genre -- "it is worth noting", "delve into",
    "in today's fast-paced world", and the rest of that family.
  * the shapes that read as machine-written -- a run of paragraphs that open
    the same way, or a sentence long enough to lose the reader.

Usage:
    python3 deliverables/scripts/check_human_tone.py
"""
from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = ROOT / "deliverables" / "templates" / "MTP_Report.md"
DECK = ROOT / "deliverables" / "scripts" / "make_thesis_deck.py"

#: The dashes that are not a plain hyphen-minus.
DASHES = {
    "em dash": "—",
    "en dash": "–",
    "figure dash": "‒",
    "horizontal bar": "―",
}

#: Stock phrases. Each is a regular expression and what it says.
PHRASES = [
    (r"\bit is worth (noting|stating|saying|mentioning|remembering|stressing)\b",
     "it is worth noting"),
    (r"\bit should be noted that\b", "it should be noted that"),
    (r"\bin (today'?s|modern|our) (fast-paced|rapidly evolving|"
     r"ever-evolving)\b", "in today's fast-paced world"),
    (r"\bdelv(e|es|ed|ing) (into|deeper)\b", "delve into"),
    (r"\bin conclusion\b", "in conclusion"),
    (r"\bmoreover\b", "moreover"),
    (r"\bfurthermore\b", "furthermore"),
    (r"(?<!report )\bthat said\b", "that said"),
    (r"\bat its core\b", "at its core"),
    (r"\bthe landscape of\b", "the landscape of"),
    (r"\ba testament to\b", "a testament to"),
    (r"\bnavigat(e|es|ing) the complexit", "navigate the complexities"),
    (r"\bunderscor(es|ing)\b", "underscores"),
    (r"\bshowcas(es|ing)\b", "showcases"),
    (r"\bserves as a (reminder|testament)\b", "serves as a reminder"),
    (r"\bwhen it comes to\b", "when it comes to"),
    (r"\bin order to\b", "in order to"),
    (r"\bthe fact of the matter\b", "the fact of the matter"),
    (r"\bat the forefront\b", "at the forefront"),
    (r"\bplays a (crucial|vital|key|pivotal) role\b", "plays a crucial role"),
    (r"\bstands as a\b", "stands as a"),
    (r"\bserves as (a|an|the)\b", "serves as"),
    (r"\bboils down to\b", "boils down to"),
    (r"\bdelve", "delve"),
    (r"\bmore holistic\b", "more holistic"),
    (r"\bparadigm shift\b", "paradigm shift"),
    (r"\bgame-?changer\b", "game-changer"),
    (r"\bleverage[sd]?\b", "leverage"),
    (r"\brobust\b", "robust"),
    (r"\bseamless(ly)?\b", "seamless"),
    (r"\bcomprehensive(ly)?\b", "comprehensive"),
    (r"\bcutting-edge\b", "cutting-edge"),
    (r"\bholistic\b", "holistic"),
    (r"\bmultifaceted\b", "multifaceted"),
    (r"\bintricate\b", "intricate"),
    (r"\bmyriad\b", "myriad"),
    (r"\bplethora\b", "plethora"),
    (r"\bparamount\b", "paramount"),
    (r"\bunderscore the importance\b", "underscore the importance"),
]

#: Narration about the project's own process rather than about the work. A
#: submitted report says what was found, not what was tried, what broke, or
#: which checker caught it.
PROCESS_NARRATION = {
    "build tooling": r"\bthe build\b|\bthe checker\b|\bconsistency check\b"
                     r"|\btest suite\b|\binvariant test\b",
    "harness": r"\bthe harness\b",
    "internal paths": r"\bthe deliverables\b|\bthis repository\b",
    "draft history": r"\ban earlier\b|\bfirst version\b|\ban earlier draft\b"
                     r"|\bwithdrawn\b|\bcorrected version\b",
    "project voice": r"\bthe project\b|\bthe project's\b",
    "debugging talk": r"generator bug|\bnot_run\b|\bwe tried\b|\bthe bug\b",
}

#: Pairs of sentences that open the same way on purpose.
DELIBERATE = {
    "The architecture is routine now.",
    "The reranker's gain survives the transfer.",
    "The control refuses as many, and more, by luck, because most of a "
    "benchmark is unanswerable.",
    "The direction is not uniform.",
    "The abstention mechanism is prior art.",
    "The gate concentrates them on the unanswerable class.",
    "The reranker survives it.",
}

#: Sentence openers that should not run three paragraphs deep.
OPENERS = ("The ", "This ", "That ", "It ", "A ", "An ", "In ", "For ", "So ")


def report_text() -> str:
    """The report's prose, as it ships.

    The reference list is left out. A paper's title is not prose, and a
    title like "A novel approach to robust LLMs" is not a piece of padded
    writing.
    """
    # The markdown, not the built DOCX, because the markdown carries the
    # bold and italic markers and the DOCX does not. The two are the same
    # document: the DOCX is generated from this file, with the measured
    # values substituted in.
    text = TEMPLATE.read_text(encoding="utf-8")
    text = re.sub(r"\n!\[\][^\n]*\n", "\n", text)
    i = text.rfind("\n# References")
    return text[:i] if i > 0 else text


def shipped_report_text() -> str:
    """The report as it ships, for the checks that do not need the markup."""
    import zipfile

    xml = zipfile.ZipFile(ROOT / "deliverables" / "MTP_Report.docx") \
        .read("word/document.xml").decode("utf-8")
    return re.sub(r"<[^>]+>", " ", xml)


def deck_text() -> str:
    """The deck's prose, as it ships."""
    from pptx import Presentation

    prs = Presentation(str(ROOT / "deliverables" / "MTP_Report_Presentation.pptx"))
    out = []
    for slide in prs.slides:
        for shape in slide.shapes:
            if shape.has_text_frame:
                out.append(shape.text_frame.text)
    return "\n".join(out)


def sentences(text: str) -> list[str]:
    """The sentences, one shape or paragraph at a time.

    Joining a slide's title to its body and then splitting on the full stop
    makes a title and two paragraphs read as one long sentence, which is a
    measurement artefact rather than a fault in the writing.
    """
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"\|.*\|", " ", text)
    out = []
    for block in text.split("\n"):
        block = block.strip()
        if len(block) < 12:
            continue
        out.extend(p.strip() for p in re.split(r"(?<=[.!?])\s+", block))
    return [p for p in out if len(p.strip()) > 30]


def main() -> int:
    problems: list[str] = []
    for name, text in (("report", report_text()), ("deck", deck_text())):
        print(f"=== {name} ===")
        for label, ch in DASHES.items():
            n = text.count(ch)
            print(f"  {label}: {n}")
            if n:
                for m in re.finditer(re.escape(ch), text):
                    line = text[:m.start()].count("\n") + 1
                    ctx = text[max(0, m.start() - 50):m.start() + 50]
                    print(f"      line {line}: ...{ctx.strip()}...")
                problems.append(f"the {name} contains {n} {label}(s)")

        hits = []
        for pattern, label in PHRASES:
            for m in re.finditer(pattern, text, re.I):
                hits.append((label, text[:m.start()].count("\n") + 1))
        if hits:
            print(f"  stock phrases: {len(hits)}")
            for label, line in hits[:12]:
                print(f"      {label} (line {line})")
            problems.append(f"the {name} uses {len(hits)} stock phrase(s)")

        sents = sentences(text)
        long_ones = [s for s in sents if len(s.split()) > 55]
        if long_ones:
            print(f"  sentences over 55 words: {len(long_ones)} of {len(sents)}")
            for s in long_ones[:4]:
                print(f"      {len(s.split())} words: {s[:90]}...")
            if len(long_ones) > len(sents) * 0.06:
                problems.append(f"the {name} has {len(long_ones)} sentences over "
                                f"55 words")
        else:
            print(f"  sentences over 55 words: 0 of {len(sents)}")

        # What reads as machine-written is not the share of sentences that
        # begin with an article; it is two of them in a row inside one
        # paragraph. A paragraph that opens "The X ... The Y ... The Z" has a
        # rhythm no person writes on purpose.
        # The text is flattened first: a phrase split across two lines of the
        # source is one phrase, and a scanner that reads line by line misses it.
        flat = re.sub(r"\s+", " ", text)
        for label, pattern in PROCESS_NARRATION.items():
            hits = re.findall(pattern, flat, re.I)
            if hits:
                print(f"  {label}: {len(hits)}")
                problems.append(f"the {name} carries {len(hits)} piece(s) of "
                                f"{label}")
        if name == "report":
            flat_doc = re.sub(r"\s+", " ", shipped_report_text())
            for label, pattern in PROCESS_NARRATION.items():
                hits = re.findall(pattern, flat_doc, re.I)
                if hits:
                    print(f"  {label} (in the built file): {len(hits)}")
                    problems.append(f"the built report carries {len(hits)} piece(s) "
                                    f"of {label}")

        runs = 0
        for block in text.split("\n"):
            block = block.strip()
            if len(block) < 12:
                continue
            block_sents = [x.strip() for x in
                           re.split(r"(?<=[.!?])\s+", block) if x.strip()]
            for a_, b_ in zip(block_sents, block_sents[1:]):
                if not (a_.startswith("The ") and b_.startswith("The ")):
                    continue
                # A bold lead-in is a deliberate device, not a rhythm slip.
                if a_.startswith("**"):
                    continue
                # Some pairs are deliberate parallelism, and parallelism is
                # what a person writes when a sentence wants to land.
                if a_ in DELIBERATE:
                    continue
                runs += 1
        print(f"  paragraphs with two sentences opening the same way: {runs}")
        if runs > 3:
            problems.append(f"the {name} has {runs} places where two "
                            f"sentences in a row open the same way")
        print()

    if problems:
        print(f"  {len(problems)} problem(s):")
        for p in problems:
            print(f"    x {p}")
        return 1
    print("  nothing to flag")
    return 0


if __name__ == "__main__":
    sys.exit(main())
