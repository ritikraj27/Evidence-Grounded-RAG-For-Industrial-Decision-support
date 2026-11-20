#!/usr/bin/env python3
"""Add a guard on the shipped quota placement.

The system shipped the post-rerank quota while its own ablation ranked the
pre-rerank placement better, and nothing in the build noticed: the numbers
were internally consistent and the prose was true as written. That is the
worst kind of defect, because it survives every check.

The guard reads the shipped placement from the configuration and compares it
with the ablation's own measurement. If the system ships the placement the
ablation ranks worse, the build fails -- and the reason it failed is stated
in the limitation, so the reader sees the same thing the panel would.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "deliverables" / "scripts" / "check_consistency.py"

CHECK = '''
def check_shipped_quota_placement() -> None:
    """The shipped quota placement must be the one the ablation ranks first.

    The system applied the quota after the reranker while its own ablation
    measured the before-the-reranker placement to be better. Nothing in the
    build caught it: the numbers were internally consistent and the prose was
    true as written. This guard compares the two, so the configuration cannot
    drift away from the measurement again without stopping the build.
    """
    try:
        from results_source import shipped_quota_position
    except Exception as exc:  # pragma: no cover
        notes.append(f"could not read the shipped quota placement: {exc}")
        return

    pos = shipped_quota_position()
    if pos == "unknown":
        notes.append("the shipped quota placement could not be read")
        return

    # The ablation's own comparison between the two placements.
    exp1 = None
    for d in (FOCUS_RESULTS, RESULTS):
        f = d / "exp1_ablation.json"
        if f.exists():
            exp1 = json.loads(f.read_text(encoding="utf-8"))
            break
    if not exp1:
        notes.append("no ablation result to compare the shipped placement against")
        return

    comp = {c["comparison"].split(" -> ")[0]: c
            for c in exp1.get("comparisons", [])}
    fg = comp.get("F. +quota_pre_rerank")
    if not fg:
        notes.append("the ablation does not compare the two quota placements")
        return

    # The pre-rerank placement's Recall@10, against the post-rerank one.
    pre = exp1["systems"].get("F. +quota_pre_rerank", {}).get("recall@10")
    post = exp1["systems"].get("G. +quota_post_rerank", {}).get("recall@10")
    if pre is None or post is None:
        return

    if pos == "post_rerank" and pre > post:
        problems.append(
            f"the system ships the post-rerank quota ({post:.3f} Recall@10) "
            f"but the ablation ranks the pre-rerank placement higher "
            f"({pre:.3f}). Either move the quota or explain why the shipped "
            f"placement is the one that is kept -- the limitation L20 exists "
            f"for exactly this."
        )
    notes.append(
        f"the shipped quota placement is {pos} "
        f"(pre-rerank {pre:.3f}, post-rerank {post:.3f} Recall@10)")

'''

ANCHOR = "def check_files() -> None:"


def main() -> int:
    s = TARGET.read_text(encoding="utf-8")
    if "def check_shipped_quota_placement" in s:
        print("  the guard is already in place")
        return 0
    assert s.count(ANCHOR) == 1
    s = s.replace(ANCHOR, CHECK.lstrip("\n") + ANCHOR, 1)
    # Wire it into main().
    import re
    m = re.search(r"^(\s*)check_files\(\)$", s, re.M)
    assert m, "check_files() is not called from main()"
    s = s[:m.start()] + f"{m.group(1)}check_shipped_quota_placement()\n" + s[m.start():]
    TARGET.write_text(s, encoding="utf-8")
    print("  the build now fails if the shipped placement is the worse one")
    return 0


if __name__ == "__main__":
    sys.exit(main())
