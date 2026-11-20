#!/usr/bin/env python3
"""Correct the claims about the gate's label.

The direction check reported that two thirds of the gate's negative class is
retrieval failure. That was true of the *defective* corpus, where the
duplicated articles deflated the retriever's recall to 0.707. On the clean
corpus the retriever's recall is 0.921, so the negative class is mostly
genuinely unanswerable queries and the claim has to change.

The limitation itself survives and is worth stating precisely: the gate's
features are retrieval scores, so it can only separate "answer found in the
context" from "answer not found" insofar as those scores carry that
information — and the base rate of the negative class moves with the
retriever. That is why the operating point is a fitted, per-corpus parameter.

New tokens carry the counts so the prose cannot drift from them.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
T = ROOT / "deliverables" / "templates"

# --------------------------------------------------------------------------
# 1. Tokens for the decomposition.
# --------------------------------------------------------------------------
TOKENS = ROOT / "deliverables" / "scripts" / "substitute_tokens.py"
s = TOKENS.read_text(encoding="utf-8")
old = '''        v["GOLD_RECALL_PCT"] = f"{exp2['retriever_recall_of_gold']:.1%}"'''
new = '''        v["GOLD_RECALL_PCT"] = f"{exp2['retriever_recall_of_gold']:.1%}"
        dec = exp2.get("label_decomposition", {})
        v["N_ANSWERABLE_FOUND"] = str(dec.get("answerable_and_found", 0))
        v["N_ANSWERABLE_MISSED"] = str(dec.get("answerable_and_missed", 0))
        v["N_LABEL_UNANSWERABLE"] = str(dec.get("unanswerable", 0))
        _neg = (int(dec.get("answerable_and_missed", 0))
                + int(dec.get("unanswerable", 0)))
        v["NEGATIVE_CLASS_SHARE_RETRIEVAL_FAILURE"] = (
            f"{int(dec.get('answerable_and_missed', 0)) / _neg:.1%}"
            if _neg else "—")'''
assert s.count(old) == 1, s.count(old)
s = s.replace(old, new, 1)
TOKENS.write_text(s, encoding="utf-8")
print("  added the decomposition tokens")

# --------------------------------------------------------------------------
# 2. The technical report's Section 4.4.
# --------------------------------------------------------------------------
PAPER_OLD = """**What the gate's label actually is, stated exactly.** The gate is calibrated on a query-level label that is 1 iff the gold chunk is present in the reranked candidate pool. That is an *answer-in-context* label, not an evidence-sufficiency label: the literature reserves "sufficiency" for a set-level property, where scoring passages independently cannot detect it. The consequence is important and we state it rather than hide it. The negative class is dominated by **retrieval failure** — an answerable question whose evidence the retriever missed — and not by absence of evidence. The gate therefore detects whether the answer is in the context, and cannot distinguish "there is no evidence here" from "the evidence is here and the retriever missed it". Section 4.4 reports the full contingency table: the number of answerable questions whose evidence was found, the number whose evidence was missed, and the number of unanswerable questions. Every claim about the gate in this paper should be read against that decomposition."""

PAPER_NEW = """**What the gate's label actually is, stated exactly.** The gate is calibrated on a query-level label that is 1 iff the gold chunk is present in the reranked candidate pool. That is an *answer-in-context* label, not an evidence-sufficiency label: the literature reserves "sufficiency" for a set-level property, where scoring passages independently cannot detect it. The gate therefore detects whether the answer is in the retrieved context, and it does not judge whether the context is sufficient.

The negative class contains two different kinds of query, and the sizes of both matter. On the evaluation corpus, of {{N_ANSWERABLE_FOUND}} answerable questions whose evidence was found, {{N_ANSWERABLE_MISSED}} answerable questions had their evidence missed by the retriever, and {{N_LABEL_UNANSWERABLE}} questions were unanswerable; the retriever's own recall of the gold chunk is {{GOLD_RECALL_PCT}}, so retrieval failure accounts for {{NEGATIVE_CLASS_SHARE_RETRIEVAL_FAILURE}} of the negative class. The limitation is worth stating precisely rather than dramatically: **the gate's features are retrieval scores, so its ability to separate "the answer is in the context" from "it is not" is bounded by how well those scores carry that information, and the composition of the negative class moves with the retriever.** On this corpus the retriever is strong enough that the negative class is mostly genuinely unanswerable, and the gate does well; on a corpus where the retriever is weaker, the same gate would face a negative class dominated by retrieval failure, which it cannot resolve, because the scores it uses are exactly the scores that failed. That is why the operating point is a fitted, per-corpus parameter and not a constant of the architecture, and why every claim about the gate here is stated against this decomposition."""

EDITS = [
    ("Deliverable_2a_Technical_Report.md", [(PAPER_OLD, PAPER_NEW)]),
]

# --------------------------------------------------------------------------
# 3. The guide's F.7.
# --------------------------------------------------------------------------
F7_OLD = """**What this forces on us.** Our gate is a **calibrated answer-in-context
detector with a stated operating point**, not a sufficiency judge, and the
literature reserves "sufficiency" for the set-level property. Part E reports
the contingency table that makes the distinction concrete: how many answerable
questions had their evidence found, how many had it missed, and how many were
unanswerable. The negative class is dominated by *retrieval failure*, and a
reviewer who reads the code will see that in five minutes."""

F7_NEW = """**What this forces on us.** Our gate is a **calibrated answer-in-context
detector with a stated operating point**, not a sufficiency judge, and the
literature reserves "sufficiency" for the set-level property. Part E reports
the contingency table that makes the distinction concrete: how many answerable
questions had their evidence found, how many had it missed, and how many were
unanswerable. On the evaluation corpus the retriever's own recall of the gold
chunk is {{GOLD_RECALL_PCT}}, so retrieval failure accounts for
{{NEGATIVE_CLASS_SHARE_RETRIEVAL_FAILURE}} of the negative class — the negative
class is mostly genuinely unanswerable, and the gate does well. But the
mechanism is the reason to be careful: the gate's features are retrieval
scores, so its ceiling is set by the retriever, and on a corpus where the
retriever is weaker the same gate would face a negative class dominated by
retrieval failure that it cannot resolve. A reviewer who reads the code will
see that in five minutes."""

EDITS.append(("Deliverable_1_PartF_toJ.md", [(F7_OLD, F7_NEW)]))

# --------------------------------------------------------------------------
# 4. The guide's viva Q3c.
# --------------------------------------------------------------------------
Q3C_OLD = """The consequence is the important part, and it is a limitation rather than a
rhetorical point. The negative class is dominated by *retrieval failure*: an
answerable question whose evidence the retriever missed. Part E reports the
three-way decomposition — answerable-and-found, answerable-and-missed, and
unanswerable — so you can see exactly how much of the negative class is
retrieval failure. A gate built on these scores cannot distinguish "there is no
evidence here" from "the evidence is here and the retriever missed it", because
the scores it uses are exactly the scores that failed. That is a limitation of
the approach, it is the field's known result for prompt- and model-based
abstention too (GRAB-RAG, arXiv:2608.22228, finds models still answer 41.6% of
misleading questions), and it is why I present the gate as a selective-prediction
policy with a risk–coverage curve rather than as a detector."""

Q3C_NEW = """The consequence is the important part, and it is a limitation rather than a
rhetorical point. The negative class of the label holds two different kinds of
query: answerable questions whose evidence the retriever missed, and questions
that are genuinely unanswerable. Part E reports the three-way decomposition, so
you can see exactly how much of the negative class is retrieval failure — on
the evaluation corpus {{NEGATIVE_CLASS_SHARE_RETRIEVAL_FAILURE}}, with the
retriever's own recall of the gold chunk at {{GOLD_RECALL_PCT}}.

The honest statement of the limitation is this. The gate's features are
retrieval scores, so its ability to separate "the answer is in the context"
from "it is not" is bounded by how well those scores carry that information,
and the composition of the negative class moves with the retriever. Here the
retriever is strong enough that the negative class is mostly what the gate is
meant to detect, and it does well. On a corpus where the retriever is weaker,
the same gate would face a negative class dominated by retrieval failure that
it cannot resolve, because the scores it uses are exactly the scores that
failed. That is why the operating point is a fitted, per-corpus parameter, and
why I present the gate as a selective-prediction policy with a risk–coverage
curve rather than as a detector. It is also the field's known result for
model- and prompt-based abstention: GRAB-RAG (arXiv:2608.22228) finds models
still answer 41.6% of misleading questions under explicit abstention
prompting."""

EDITS.append(("Deliverable_1_PartF_toJ.md", [(Q3C_OLD, Q3C_NEW)]))

# --------------------------------------------------------------------------
# 5. The root README's honesty notes.
# --------------------------------------------------------------------------
README_OLD = """- **The architectural contribution is incremental.**"""

README_NEW = """- **The gate's label is answer-in-context detectability, not evidence
  sufficiency.** The positive class is "the gold chunk is in the reranked
  candidate pool"; the negative class holds answerable questions whose evidence
  the retriever missed alongside the genuinely unanswerable ones. The gate's
  features are retrieval scores, so its ceiling is set by the retriever rather
  than by its threshold. The contingency table is reported rather than a base
  rate alone, and the operating point is re-fitted per corpus.
- **The architectural contribution is incremental.**"""

EDITS.append(("../README.md", [(README_OLD, README_NEW)]))


def apply(path: Path, edits):
    if not path.exists():
        print(f"!! missing {path}")
        return 0
    s = path.read_text(encoding="utf-8")
    n = 0
    for old, new in edits:
        c = s.count(old)
        if c != 1:
            print(f"!! {path}: count={c} -> {old[:60]!r}")
            continue
        s = s.replace(old, new, 1)
        n += 1
    path.write_text(s, encoding="utf-8")
    return n


def main() -> int:
    total = 0
    for rel, edits in EDITS:
        total += apply(T / rel, edits)
    print(f"\n{total} replacements applied")
    return 0


if __name__ == "__main__":
    sys.exit(main())
