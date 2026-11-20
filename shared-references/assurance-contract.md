# Assurance Contract

> **Status: not published upstream.** This file is referenced by 4 installed skills
> (`citation-audit`, `paper-claim-audit`, `paper-writing`, `proof-checker`), but the upstream suite
> `github.com/Chanw-research/claude-code-paper-writing` never published it. This
> document was written locally to keep those references resolvable; it does not
> restate upstream policy.

> **中文摘要：** 本文档是本地补写的指针，上游从未发布。audit JSON schema 与 verdict 判定表在三个审计技能各自的 `Submission Artifact Emission` 段落；assurance 等级解析在 `paper-writing` Phase 0 与 Phase 6.0。

## What this reference governs

The 4 sites split into two roles. `paper-writing/SKILL.md:116` points here for the
assurance-level contract: `draft` vs `submission`, how the level is derived from
`— effort:` or an explicit `— assurance:` flag, and what each level gates downstream.
The other 3 sites (`proof-checker:567`, `paper-claim-audit:258`, `citation-audit:401`)
point here for the shared JSON schema of the audit artifact — the common field set
(`audit_skill`, `verdict`, `reason_code`, `summary`, `audited_input_hashes`,
`trace_path`, `thread_id`, `reviewer_model`, `reviewer_reasoning`, `generated_at`,
`details`) and the shared verdict vocabulary.

## Where the operative guidance actually lives

- `.claude/skills/paper-writing/SKILL.md` — Phase 0 (Assurance Setup) defines the
  resolution order (explicit `— assurance:` wins, else `lite`/`balanced` → `draft`,
  `max`/`beast` → `submission`, else `draft`) and the per-level behaviour; Phase 6.0
  re-derives the level at the gate so a run cannot silently downgrade.
- The "Submission Artifact Emission" section of each audit skill carries the full JSON
  schema **and** the verdict → `reason_code` decision table verbatim:
  `.claude/skills/proof-checker/SKILL.md:557-690`,
  `.claude/skills/paper-claim-audit/SKILL.md:249-318`,
  `.claude/skills/citation-audit/SKILL.md:393-474`.
- The shared `audited_input_hashes` path convention (paths relative to the paper dir,
  absolute for out-of-paper files) is stated in all three audit skills and is what
  `tools/verify_paper_audits.sh` expects. That script is not present in this install.

## How to proceed

1. Read the schema and the decision table from the audit skill you are running, not from
   a generic template — `details` differs per audit (`per_entry`, `mismatches`,
   `issues`), and only `details` is skill-specific.
2. Always emit the artifact, including when the content detector is negative
   (`NOT_APPLICABLE`). A silent skip is forbidden in every case.
3. Hash the declared input set only — not a repo-wide union, not the reviewer's
   self-reported subset. Use paper-dir-relative keys for in-paper files and absolute
   paths for external result files.
4. Never block on the verdict yourself. The skill emits; `paper-writing` Phase 6 plus
   the verifier decide, based on the assurance level.
