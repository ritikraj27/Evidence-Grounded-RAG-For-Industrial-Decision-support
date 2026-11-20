# Reviewer Routing

> **Status: not published upstream.** This file is referenced by 4 installed skills
> (`proof-checker`, `idea-creator`, `rebuttal`, `research-lit`), but the upstream suite
> `github.com/Chanw-research/claude-code-paper-writing` never published it. This
> document was written locally to keep those references resolvable; it does not
> restate upstream policy.

> **中文摘要：** 本文档是本地补写的指针，上游从未发布。默认 `codex` 后端（reasoning effort `xhigh`），`— reviewer: oracle-pro` 可覆盖为 Oracle MCP 上的 GPT-5.4 Pro；后端不可用时的降级模式见 `cross-model-review.md`。

## What this reference governs

All 4 sites attach the same sentence to a `REVIEWER_BACKEND` constant: default `codex`
(Codex MCP, reasoning effort `xhigh`), overridable with `— reviewer: oracle-pro` to reach
GPT-5.4 Pro via Oracle MCP (`proof-checker/SKILL.md:18`, `idea-creator/SKILL.md:23`,
`rebuttal/SKILL.md:44`, `research-lit/SKILL.md:15`). The reference is expected to carry
the full backend-selection policy: which backend serves which kind of review, how a
backend is chosen, and what to do when the chosen backend is unavailable.

**What could not be determined from the referencing skills:** none of the 4 skills
contains a second `REVIEWER_BACKEND` value beyond `codex` and the `oracle-pro` override,
and no skill in this install declares an `mcp__oracle__*` tool. The upstream text may
specify further backends, precedence rules, or a fallback order; that content is not
recoverable from the install, so it is not restated here.

## Where the operative guidance actually lives

- The `Constants` block of each referencing skill — `.claude/skills/proof-checker/SKILL.md`,
  `.claude/skills/idea-creator/SKILL.md`, `.claude/skills/rebuttal/SKILL.md`,
  `.claude/skills/research-lit/SKILL.md` — which carry `REVIEWER_MODEL = gpt-5.4`,
  `REVIEWER_BACKEND = codex`, and the reasoning effort (`xhigh`).
- The reviewer-call blocks in those same skills (e.g. `proof-checker/SKILL.md:183`,
  `idea-creator/SKILL.md:95`) — these show the actual MCP invocation shape for the
  `codex` backend.
- `shared-references/cross-model-review.md` — the **published upstream** document that
  covers the sibling suite's reviewer-availability check and graceful degradation. Its
  pattern (detect → tell the user → offer to configure → fall back to Claude-only with
  an explicit label) is the closest thing in this install to a routing policy, but it
  targets `mcp__llm-review__chat`, not Codex or Oracle.

## How to proceed

1. Default to the `codex` backend with reasoning effort `xhigh`, exactly as the
   referencing skill's own `Constants` block states.
2. Honour `— reviewer: oracle-pro` when the user passes it. Do not invent further
   backend names, and do not silently switch backends.
3. If the selected backend's MCP tools are unavailable, follow the degradation pattern
   in `shared-references/cross-model-review.md`: say so, offer configuration, and if the
   user declines, continue in Claude-only mode with the result explicitly labelled as a
   self-review.
4. Record every reviewer call's trace per `review-tracing.md`.
