# Output Manifest Protocol

> **Status: not published upstream.** This file is referenced by 8 installed skills
> (`experiment-plan`, `research-refine`, `research-refine-pipeline`, `idea-creator`,
> `idea-discovery`, `paper-plan`, `paper-writing`, `grant-proposal`), but the upstream suite
> `github.com/Chanw-research/claude-code-paper-writing` never published it. This
> document was written locally to keep those references resolvable; it does not
> restate upstream policy.

> **中文摘要：** 本文档是本地补写的指针，上游从未发布。规则仅一句「把每个输出记录到 MANIFEST.md」；该文件的格式、列与存放位置上游均未定义，故只写简单追加列表。

## What this reference governs

All 8 sites carry the identical one-line summary "log every output to MANIFEST.md" inside
the same `## Output Protocols` block that points at `output-versioning.md` and
`output-language.md` (e.g. `paper-plan/SKILL.md:318`, `experiment-plan/SKILL.md:225`).
The reference is the only mention of `MANIFEST.md` anywhere in the suite: no skill
creates it, reads it, or defines its columns. The upstream text therefore specifies the
file's name and its purpose (an inventory of what the skill produced) but no format.

## Where the operative guidance actually lives

- The one-line rule itself in each referencing skill's `## Output Protocols` block
  (`.claude/skills/<skill>/SKILL.md`).
- Each skill's own `## Output` / `## Output Contract` section lists the files it writes
  and where — that list is the practical source of the manifest entries (e.g.
  `experiment-plan` writes `refine-logs/EXPERIMENT_PLAN.md` and
  `refine-logs/EXPERIMENT_TRACKER.md`; `citation-audit` writes `CITATION_AUDIT.md`,
  `CITATION_AUDIT.json`, and a trace directory).
- `.claude/skills/paper-writing/SKILL.md` records run-level state under `paper/.aris/`
  (`assurance.txt`, `audit-verifier-report.json`), which is the suite's other
  inventory-of-record mechanism.

## How to proceed

1. Append one line per output file to `MANIFEST.md` after writing it: path, what it is,
   and when it was written.
2. Do not invent a column set, a machine-readable schema, or a required file location —
  upstream defines none. A simple append-only list is enough; the goal is that a human
   can see what this run produced.
3. If `MANIFEST.md` does not exist, create it rather than failing — the skills never
   create it themselves, so its absence is normal on a first run.
4. Treat `MANIFEST.md` as a log, not a contract. Do not make other skills parse it.
