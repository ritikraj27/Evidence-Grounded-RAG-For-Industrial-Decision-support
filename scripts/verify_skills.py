#!/usr/bin/env python3
"""Verify that the installed skills resolve their own references.

Checks every skill (and every markdown file inside it) for relative references
- `../sibling/file.md`, `./file.md`, `dir/file.md` - and reports the ones whose
target does not exist.

A reference resolves if it exists relative to ANY of the plausible bases:
  - the directory of the file that contains it
  - the skill root (the directory holding SKILL.md)
  - the skills root (.claude/skills/)
  - the project root
  - the real path of the skill directory (skills are symlinks into the clones)

Usage:
  python3 scripts/verify_skills.py             # report every unresolved reference
  python3 scripts/verify_skills.py --quiet     # only print the summary
  python3 scripts/verify_skills.py --skill X   # only report one skill
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from collections import defaultdict
from typing import Dict, List, Optional, Set, Tuple

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS_ROOT = os.path.join(PROJECT_ROOT, ".claude", "skills")

# markdown links, and bare relative paths that look like files
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
BARE_RE = re.compile(r"(?<![\w/])(\.{1,2}/[\w./\-]+\.(?:md|py|sh|yaml|yml|json|txt|pdf|bib|tex|csv))")
DIR_RE = re.compile(r"(?<![\w/])(\.{1,2}/[\w./\-]+/)")

SKIP_PREFIXES = ("http://", "https://", "mailto:", "#", "data:", "$", "{")
# paths an agent is expected to create at runtime, not read from the repo
RUNTIME_MARKERS = ("{slug}", "{date}", "{topic}", "{paper}", "{id}", "PATH/TO/", "<", "[")
# Files and directories the skills CREATE during a run. They are absent from a
# fresh checkout on purpose, so they are reported separately from real breaks.
RUNTIME_ARTIFACTS = (
    "IDEA_REPORT.md", "AUTO_REVIEW.md", "IDEA_CANDIDATES.md",
    "results", "logs", "figures", "nanobanana-output", "paper", "passports",
    "image.jpg",
)


def is_runtime_artifact(target: str) -> bool:
    """True when the reference names something the skill writes, not reads."""
    cleaned = target.rstrip("/")
    name = os.path.basename(cleaned)
    return name in RUNTIME_ARTIFACTS


def is_external(target: str) -> bool:
    target = target.strip()
    if not target:
        return True
    if "..." in target:
        return True          # schema/path illustration, e.g. "scripts/fixtures/.../mnc.json"
    if "/" not in target and "." not in target:
        return True          # bare placeholder inside LaTeX/JSON examples, e.g. "(url)"
    if target.startswith(SKIP_PREFIXES):
        return True
    if target.startswith("/"):
        return True
    if any(marker in target for marker in RUNTIME_MARKERS):
        return True
    if target.startswith("~"):
        return True
    return False


def candidate_bases(path: str) -> List[str]:
    """Directories a relative reference could be resolved against."""
    bases = [os.path.dirname(path)]
    # skill root: walk up until we find the dir containing SKILL.md
    current = os.path.dirname(path)
    for _ in range(6):
        if os.path.exists(os.path.join(current, "SKILL.md")):
            bases.append(current)
            break
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    bases.append(SKILLS_ROOT)
    bases.append(PROJECT_ROOT)
    # real path of the skill dir (skills are symlinks into the clones)
    real = os.path.realpath(path)
    if real != path:
        bases.append(os.path.dirname(real))
        rcurrent = os.path.dirname(real)
        for _ in range(6):
            if os.path.exists(os.path.join(rcurrent, "SKILL.md")):
                bases.append(rcurrent)
                break
            parent = os.path.dirname(rcurrent)
            if parent == rcurrent:
                break
            rcurrent = parent
    seen: Set[str] = set()
    unique = []
    for base in bases:
        if base not in seen:
            seen.add(base)
            unique.append(base)
    return unique


def resolves(target: str, path: str) -> bool:
    target = target.split("#")[0].strip()
    if not target:
        return True
    for base in candidate_bases(path):
        # normpath matters: a skill dir is often a symlink into a clone, and the
        # filesystem resolves ".." against the symlink TARGET. An agent reading
        # .claude/skills/x/SKILL.md normalizes the path as a string, so we do too.
        if os.path.exists(os.path.normpath(os.path.join(base, target))):
            return True
    return False


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--quiet", action="store_true", help="summary only")
    parser.add_argument("--skill", help="limit the report to one skill")
    args = parser.parse_args(argv)

    broken: Dict[str, List[Tuple[str, int, str]]] = defaultdict(list)
    checked = 0
    runtime = 0

    for skill in sorted(os.listdir(SKILLS_ROOT)):
        skill_dir = os.path.join(SKILLS_ROOT, skill)
        if not os.path.isdir(skill_dir):
            continue
        if args.skill and skill != args.skill:
            continue
        if not os.path.exists(os.path.join(skill_dir, "SKILL.md")):
            continue

        for root, _dirs, names in os.walk(skill_dir):
            for name in names:
                if not name.endswith(".md"):
                    continue
                path = os.path.join(root, name)
                try:
                    with open(path, "r", encoding="utf-8", errors="replace") as handle:
                        text = handle.read()
                except OSError:
                    continue
                rel = os.path.relpath(path, SKILLS_ROOT)
                targets: List[str] = []
                targets += [t for t in LINK_RE.findall(text) if not is_external(t)]
                targets += [t for t in BARE_RE.findall(text) if not is_external(t)]
                targets += [t for t in DIR_RE.findall(text) if not is_external(t)]
                for target in targets:
                    checked += 1
                    if not resolves(target, path):
                        if is_runtime_artifact(target):
                            runtime += 1
                            continue
                        line = text[:text.find(target)].count("\n") + 1
                        broken[skill].append((rel, line, target))

    total = sum(len(v) for v in broken.values())
    if not args.quiet:
        for skill in sorted(broken):
            print(f"\n{skill}  ({len(broken[skill])} unresolved)")
            seen_targets: Set[str] = set()
            for rel, line, target in broken[skill]:
                key = (rel, target)
                if key in seen_targets:
                    continue
                seen_targets.add(key)
                print(f"  {rel}:{line}  ->  {target}")
    print()
    print(f"checked {checked} references across skills; {total} unresolved "
          f"in {len(broken)} skills")
    if runtime:
        print(f"({runtime} further references point at files the skills create at "
              f"runtime - not counted as broken)")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
