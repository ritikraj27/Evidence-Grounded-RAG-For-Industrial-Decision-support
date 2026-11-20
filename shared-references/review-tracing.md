# Review Tracing

> **Status: not published upstream.** This file is referenced by 6 installed skills
> (`citation-audit`, `figure-spec`, `idea-creator`, `novelty-check`, `paper-claim-audit`, `rebuttal`), but the upstream suite
> `github.com/Chanw-research/claude-code-paper-writing` never published it. This
> document was written locally to keep those references resolvable; it does not
> restate upstream policy.

> **中文摘要：** 本文档是本地补写的指针，上游从未发布。每次评审调用后把原始 prompt 与原始回复写入 `.aris/traces/<skill>/<date>_run<NN>/`；本安装没有 `tools/save_trace.sh`，须直接写文件。

## What this reference governs

All 6 sites carry a near-identical `## Review Tracing` paragraph: after each
`mcp__codex__codex` or `mcp__codex__codex-reply` call, save the trace via
`tools/save_trace.sh` or write it to `.aris/traces/<skill>/<date>_run<NN>/`, respecting
the `--- trace:` parameter (default `full`). The reference is the canonical statement of
the trace format, directory layout, and the `--- trace:` parameter's allowed values.

**What could not be determined from the referencing skills:** the referencing skills give
the directory template and the parameter default, but never enumerate what `--- trace:`
accepts besides `full`, nor the on-disk filename convention for a trace beyond
`citation-audit`'s per-entry `<key>.md` form (`citation-audit/SKILL.md:112`). Note also
that `tools/save_trace.sh` does not exist in this install, so the reference must be
followed by writing the trace files directly.

## Where the operative guidance actually lives

- The `## Review Tracing` section in each of the 6 referencing skills —
  `.claude/skills/citation-audit/SKILL.md:301`,
  `.claude/skills/figure-spec/SKILL.md:221`,
  `.claude/skills/idea-creator/SKILL.md:321`,
  `.claude/skills/novelty-check/SKILL.md:90`,
  `.claude/skills/paper-claim-audit/SKILL.md:247`,
  `.claude/skills/rebuttal/SKILL.md:326`.
- The `trace_path` field in each audit skill's JSON artifact schema — e.g.
  `.claude/skills/citation-audit/SKILL.md:414` writes
  `.aris/traces/citation-audit/<date>_run<NN>/` — which is what makes the trace
  discoverable after the run.
- `.claude/skills/paper-writing/SKILL.md:536` — the instruction to record each
  sub-audit's trace when the three audits are invoked from the pipeline.

## How to proceed

1. After every reviewer call, write the raw prompt and the raw response to
   `.aris/traces/<skill>/<date>_run<NN>/`, creating the directory if needed. Use
   `<skill>` as the skill's own name (e.g. `citation-audit`, `paper-claim-audit`).
2. Save the response verbatim — the trace is the evidence that the reviewer actually saw
   only what it was given. Do not summarise it into the trace.
3. Default to the full trace. If a skill accepts a reduced `--- trace:` mode, honour
   it; do not invent additional modes.
4. Point the audit artifact's `trace_path` at the directory you wrote, so the verifier
   can find it.
