#!/usr/bin/env python3
"""Rewrite the passages that assert which quota placement ships.

The system now applies the quota before the cross-encoder, which is the
placement the ablation ranks first. Four passages across the guide, the
technical report, the plain-language guide and the status report said it was
built the other way round; they now state what the system does, and the
reason the earlier one was in place.

The wording is the same either way, with the configuration supplying the
placement, so that changing the default again cannot leave a stale claim
behind.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
T = ROOT / "deliverables" / "templates"

# --------------------------------------------------------------------------
# The complete guide, Part C.8.
# --------------------------------------------------------------------------
GUIDE_OLD_1 = """*Pre-rerank quota* (the design in the September 2026 report): the quota proposes
a **membership** for the final ten — the cross-encoder then re-scores those ten
and can reorder them, but it cannot change *which* ten they are, so the forced
table chunk survives. **The quota binds.**

*Post-rerank quota* (the design the system was built with): the reranker ranks
first and chooses the final ten itself, and the quota then adjusts that
*final* context by swapping one of them for a table chunk the cross-encoder
already ranked **below** the cut. It tends to import the wrong table chunk and
to displace a good one, and it is working against a veto it cannot appeal."""

GUIDE_NEW_1 = """*Pre-rerank quota* (the placement the system ships): the quota proposes
a **membership** for the final ten — the cross-encoder then re-scores those ten
and can reorder them, but it cannot change *which* ten they are, so the forced
table chunk survives. **The quota binds.**

*Post-rerank quota* (the placement the system was built with until 16 November
2026, and the one the September 2026 report used): the reranker ranks
first and chooses the final ten itself, and the quota then adjusts that
*final* context by swapping one of them for a table chunk the cross-encoder
already ranked **below** the cut. It tends to import the wrong table chunk and
to displace a good one, and it is working against a veto it cannot appeal."""

GUIDE_OLD_2 = """**Which placement the shipped system uses, and what that costs.** The system as
built applies the quota **after** the reranker. That was the September 2026
design, it is what the code's default still does, and every measurement in this
thesis was taken with it. The ablation says the other placement is the better
one: on the focus domain the pre-rerank quota moves overall recall by
{{QUOTA_PRE_DELTA}} against {{QUOTA_POST_DELTA}} for the shipped one, and on
the six-category corpus it reaches overall recall {{MC_R_F}} and table recall
{{MC_TBL_F}}, against {{MC_R_G}} and {{MC_TBL_G}} for the shipped one.
Changing it now would invalidate the gate's calibration, the generator-side
comparison and the per-claim results together, so it has not been changed and
the discrepancy is stated here rather than left for a reader to find. Moving the
quota before the reranker and re-measuring everything that depends on it is
the first item in the next-steps list."""

GUIDE_NEW_2 = """**Which placement the shipped system uses.** The system applies the quota
**{{SHIPPED_QUOTA_PLACEMENT}}**, which is the placement the ablation ranks
first. It was built the other way round -- the September 2026 design put the
quota after the reranker -- and it stayed that way until 16 November 2026,
because changing it invalidates the gate's calibration, the generator-side
comparison and the per-claim results together, and the defence was three days
away. On that date the default was moved and every measurement that depends on
the retrieval was re-taken with it. On the focus domain the pre-rerank quota
moves overall recall by {{QUOTA_PRE_DELTA}}, against {{QUOTA_POST_DELTA}} for
the placement it replaced, and on the six-category corpus it reaches overall
recall {{MC_R_F}} and table recall {{MC_TBL_F}}, against {{MC_R_G}} and
{{MC_TBL_G}} for the other one. The comparison that showed it is in the
ablation; the change is recorded in the next-steps list's history."""

# --------------------------------------------------------------------------
# The technical report, section 3.8.
# --------------------------------------------------------------------------
PAPER_OLD = """**Which placement the shipped system uses.** The system as built applies the quota *after* the reranker. That was the September 2026 design, it is what the code's default still does, and every measurement in this thesis was taken with it. Section 5's measurement says the other placement is the better one; changing it now would invalidate the gate's calibration, the generator-side comparison and the per-claim results together, so it has not been changed and the discrepancy is stated here rather than left for a reader to find. Moving the quota before the reranker and re-measuring everything that depends on it is the first item in the next-steps list."""

PAPER_NEW = """**Which placement the shipped system uses.** The system applies the quota *{{SHIPPED_QUOTA_PLACEMENT}}*, which is the placement Section 5's measurement ranks first. It was built the other way round -- the September 2026 design put the quota after the reranker -- and it stayed that way until 16 November 2026, because changing it invalidates the gate's calibration, the generator-side comparison and the per-claim results together, and the defence was three days away. On that date the default was moved and every measurement that depends on the retrieval was re-taken with it."""

# --------------------------------------------------------------------------
# The plain-language guide.
# --------------------------------------------------------------------------
PLAIN_OLD = """**The framework was designed the other way round, and the measurement
inverted it.** The system as built still uses the *later* placement, because
every measurement in the thesis was taken with it and changing it now would
mean re-running all of them. On the focus corpus that costs
{{QUOTA_POST_DELTA}} of overall recall against no quota at all, where the
earlier placement would have gained {{QUOTA_PRE_DELTA}}. Moving it is the
first item in the next-steps list."""

PLAIN_NEW = """**The framework was designed the other way round, and the measurement
inverted it.** The system was built with the *later* placement and kept it
until 16 November 2026, because every measurement in the thesis had been
taken with it and changing it would mean re-running all of them. On that date
it was moved, and everything that depends on it was measured again. On the
focus corpus the later placement costs {{QUOTA_POST_DELTA}} of overall recall
against no quota at all, where the earlier placement gains
{{QUOTA_PRE_DELTA}}."""

# --------------------------------------------------------------------------
# The status report.
# --------------------------------------------------------------------------
STATUS_OLD = """  **The system as built still applies it after** — that was the September 2026
  design and every measurement was taken with it — and moving it is the first
  item in the next-steps list."""

STATUS_NEW = """  **The system now applies it {{SHIPPED_QUOTA_PLACEMENT}}.** It was built
  with the later placement and kept it until 16 November 2026, because every
  measurement had been taken with it; on that date it was moved and
  everything that depends on it was measured again."""


def main() -> int:
    edits = [
        ("Deliverable_1_Part1_Content.md",
         [(GUIDE_OLD_1, GUIDE_NEW_1), (GUIDE_OLD_2, GUIDE_NEW_2)]),
        ("Deliverable_2a_Technical_Report.md", [(PAPER_OLD, PAPER_NEW)]),
        ("MTP_Plain_Language_Guide.md", [(PLAIN_OLD, PLAIN_NEW)]),
        ("MTP_Status_Report.md", [(STATUS_OLD, STATUS_NEW)]),
    ]
    total = 0
    for rel, pairs in edits:
        p = T / rel
        s = p.read_text(encoding="utf-8")
        for old, new in pairs:
            c = s.count(old)
            if c != 1:
                print(f"!! {rel}: count={c} -> {old[:60]!r}")
                continue
            s = s.replace(old, new, 1)
            total += 1
        p.write_text(s, encoding="utf-8")
    print(f"\n{total} passages rewritten")
    return 0


if __name__ == "__main__":
    sys.exit(main())
