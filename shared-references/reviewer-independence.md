# Reviewer Independence

> **Status: not published upstream.** This file is referenced by 8 sites across 6 installed skills
> (`proof-checker`, `citation-audit`, `paper-claim-audit`, `paper-plan`, `paper-write`, `paper-writing`), but the upstream suite
> `github.com/Chanw-research/claude-code-paper-writing` never published it. This
> document was written locally to keep those references resolvable; it does not
> restate upstream policy.

> **中文摘要：** 本文档是本地补写的指针，上游从未发布。每次评审／审计用全新线程，不喂入既往审计结果、作者风格上下文或执行方解释；同一次调用内的追问轮次除外。

## What this reference governs

Every reference site uses this file to justify the same two rules: (a) each audit or
review runs in a **fresh reviewer thread**, never `codex-reply` across separate
invocations, and prior audit outputs are never fed back in as input
(`proof-checker/SKILL.md:695`, `citation-audit/SKILL.md:481`, `paper-claim-audit/SKILL.md:318`);
(b) reviewer and auditor sub-skills see only the artifact plus the user's prompt — never
the author's stylistic context (`paper-write/SKILL.md:66`,
`paper-writing/SKILL.md:78`, `paper-plan/SKILL.md:64`). `paper-claim-audit` goes
further and calls its own variant "zero-context evidence audit", stricter than this
baseline.

## Where the operative guidance actually lives

- `proof-checker/SKILL.md` — the most precise statement, including the deliberate
  exception: within one invocation `codex-reply` is correct for Phase 3 follow-up
  rounds, while the Phase 3.5 blind second review must spawn a fresh thread.
- `citation-audit/SKILL.md` and `paper-claim-audit/SKILL.md` — each skill's "Thread
  independence" section.
- `paper-writing/SKILL.md` — Phase 4.5/4.7/5.5/5.8 must run on the artifact alone.
- `shared-references/cross-model-review.md` — the **published upstream** document that
  states the same principle for the sibling EmpiricalWiki suite (reviewers must not
  receive the primary model's score, assessment, or recommendation). Read it for the
  reasoning about anchoring bias; note that it targets `mcp__llm-review__chat`, while
  this suite's reviewers run through Codex MCP.

## How to proceed

1. Start a fresh `mcp__codex__codex` thread per top-level audit or review invocation; do
   not reuse a saved `threadId` across invocations.
2. Pass only the artifact and the user's prompt to a reviewer. Withhold `— style-ref`
   and its cache, prior audit JSON, executor summaries, and conversation history.
3. Do not pass `PROOF_AUDIT`, `PAPER_CLAIM_AUDIT`, `CITATION_AUDIT`, `EXPERIMENT_LOG`,
   `AUTO_REVIEW`, or `NARRATIVE_REPORT` into another audit.
4. Within a single invocation, use `codex-reply` only where the skill explicitly allows
   it, and honour any deliberate blind re-review step it names.
