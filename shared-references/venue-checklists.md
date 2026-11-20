# Venue Checklists

> **Status: not published upstream.** This file is referenced by 4 sites across 2 installed skills
> (`paper-plan`, `paper-write`), but the upstream suite
> `github.com/Chanw-research/claude-code-paper-writing` never published it. This
> document was written locally to keep those references resolvable; it does not
> restate upstream policy.

> **中文摘要：** 本文档是本地补写的指针，上游从未发布。各会场真实要求见 `.claude/skills/conference-paper-writing/references/checklists.md`（NeurIPS／ICML／ICLR／ACL）；页数与引用命令规则见 `paper-write` 自身。

## What this reference governs

`paper-plan/SKILL.md:35` loads it "before freezing the outline for a specific venue";
`paper-write/SKILL.md:35` loads it "during the final write-up and submission-readiness
pass"; `paper-write/SKILL.md:538` makes it a checklist item ("Venue-specific required
sections/checklists satisfied"); and `paper-write/SKILL.md:560` states its expected scope
as "ICLR/NeurIPS/ICML/IEEE submission requirements to check before declaring done". The
reference is expected to carry per-venue submission requirements: required sections,
checklists, page limits, anonymity rules, and citation-command conventions.

## Where the operative guidance actually lives

- **`.claude/skills/conference-paper-writing/references/checklists.md`** — the real
  checklist document in this install: NeurIPS (16 required items), ICML, ICLR (including
  the LLM-disclosure policy), ACL, a Universal Pre-Submission Checklist, a Quick
  Reference for page limits, and template locations.
- `.claude/skills/conference-paper-writing/templates/` — `iclr2026/`, `neurips2025/`,
  `colm2025/` (`.tex` + `.sty`), and a `README.md` describing each.
- `.claude/skills/paper-write/templates/` — `iclr2026.tex`, `neurips2025.tex`,
  `IEEEtran.bst`; `paper-write/SKILL.md` "Venue-Specific Setup" shows how to select
  them.
- `.claude/skills/paper-write/SKILL.md` — the venue rules stated inline: page-limit
  counting differs by venue (ML conferences exclude references/appendix; IEEE counts
  references), ML venues use `natbib` (`\citep`/`\citet`) while IEEE venues use the
  `cite` package (`\cite`), and the anonymity rules.
- `.claude/skills/paper-plan/SKILL.md` — the same rules restated in its "Key Rules".

## How to proceed

1. Read the venue's actual checklist from
   `.claude/skills/conference-paper-writing/references/checklists.md` — it is the
   authoritative list for NeurIPS / ICML / ICLR / ACL, and missing a mandatory checklist
   is a desk rejection.
2. Apply the venue-specific rules inline in `paper-write` / `paper-plan` (page limits,
   citation commands, anonymity) exactly as written there; those are stated, not
   inferred.
3. For an IEEE target, use the `cite` package and numeric `\cite{}`; for ICLR / NeurIPS /
   ICML / CVPR / ACL / AAAI, use `natbib`. Never mix them.
4. Do not add a venue the two files above do not cover, and do not invent page limits or
   checklist items. If the target venue is not listed, say so and use the user's
   call for the missing requirements.
