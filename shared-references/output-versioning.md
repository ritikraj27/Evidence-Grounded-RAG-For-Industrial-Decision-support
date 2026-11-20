# Output Versioning Protocol

> **Status: not published upstream.** This file is referenced by 8 installed skills
> (`experiment-plan`, `research-refine`, `research-refine-pipeline`, `idea-creator`,
> `idea-discovery`, `paper-plan`, `paper-writing`, `grant-proposal`), but the upstream suite
> `github.com/Chanw-research/claude-code-paper-writing` never published it. This
> document was written locally to keep those references resolvable; it does not
> restate upstream policy.

> **中文摘要：** 本文档是本地补写的指针，上游从未发布。各技能在 `## Output Protocols` 区块引用它，规则仅一句「先写带时间戳的文件，再复制为固定文件名」；时间戳格式与保留策略上游未定义，请查各技能自身的 `## Output` 章节。

## What this reference governs

All 8 sites carry the identical one-line summary "write timestamped file first, then copy
to fixed name" inside an `## Output Protocols` block (e.g. `paper-plan/SKILL.md:317`,
`grant-proposal/SKILL.md:653`). The block is appended at the end of each skill, so it
applies to every output file that skill writes — plan, tracker, summary, proposal, and
report files alike. The upstream text does not specify the timestamp format, where the
timestamped copy lives, or when the fixed-name copy is refreshed.

## Where the operative guidance actually lives

- The one-line rule itself, repeated in each referencing skill's `## Output Protocols`
  block (`.claude/skills/<skill>/SKILL.md`).
- `paper-write` and `paper-writing` carry the concrete backup rule that this protocol
  sits on top of: "Backup before overwrite — never destroy existing `paper/` directory
  without backing up" (`.claude/skills/paper-write/SKILL.md`).
- `paper-writing` / `paper-plan` name the exact output paths each skill writes
  (e.g. `PAPER_PLAN.md`, `NARRATIVE_REPORT.md`, `refine-logs/EXPERIMENT_PLAN.md`) in their
  own `## Output` sections — read those for the fixed names.

## How to proceed

1. Treat the one-line summary as the whole rule: write the real file under a
   timestamped name first, then copy it to the fixed name the skill's own
   `## Output` section names.
2. Do not invent a timestamp format, a directory layout, or a retention policy — none is
   specified upstream. If a timestamp format matters, ask the user.
3. Never let the versioning step destroy the previous artifact. Take the backup the
   skill names before overwriting.
4. `paper-writing` (`.claude/skills/paper-writing/SKILL.md`) is an exception worth
   reading first: it always emits English LaTeX for venue submission, so version the
   LaTeX tree as a unit rather than file-by-file.
