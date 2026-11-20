# Writing Principles

> **Status: not published upstream.** This file is referenced by 5 sites across 2 installed skills
> (`paper-plan`, `paper-write`), but the upstream suite
> `github.com/Chanw-research/claude-code-paper-writing` never published it. This
> document was written locally to keep those references resolvable; it does not
> restate upstream policy.

> **中文摘要：** 本文档是本地补写的指针，上游从未发布。摘要用五段式：做了什么／为何难／怎么做／证据／最强结果；叙事原则见 `paper-plan/SKILL.md:95`，完整写法见 `conference-paper-writing/references/writing-guide.md`。

## What this reference governs

`paper-write/SKILL.md:34` loads it "before drafting the Abstract, Introduction, Related
Work, or when prose feels generic"; `paper-plan/SKILL.md:34` loads it "when framing the
one-sentence contribution, Abstract, Introduction, Related Work, or hero figure"; and
`paper-write/SKILL.md:182` names the concrete artefact it must supply — the **5-part
abstract flow: what, why hard, how, evidence, strongest result**. `paper-plan/SKILL.md:95`
adds the narrative principle the outline must satisfy by the end of the Introduction:
the paper tells one coherent technical story, makes What / Why / So What explicit, and
front-loads title, abstract, introduction, and hero figure. `paper-write/SKILL.md:559`
summarises the expected scope as "story framing, abstract/introduction patterns,
sentence-level clarity, reviewer reading order".

## Where the operative guidance actually lives

- **`shared-references/academic-writing.md`** — the **published upstream** document that
  covers most of this ground for the sibling EmpiricalWiki suite: hourglass narrative
  shape, per-section rules (Introduction / Related Work / Method / Experiments /
  Conclusion), sentence- and paragraph-level clarity rules, notation consistency,
  figure and table design, and the de-AI polish pass. Read it for the substance; note
  that its section vocabulary is written for LaTeX papers and does not mention the
  5-part abstract flow by that name.
- **`.claude/skills/conference-paper-writing/references/writing-guide.md`** — the closest
  match for the 5-part abstract flow in this install: "Sebastian Farquhar's 5-Sentence
  Formula" (what you achieved / why it is hard / how / what evidence / your most
  remarkable result), plus the narrative principle, reviewer reading patterns, Gopen &
  Swan clarity principles, and figure design.
- `.claude/skills/paper-write/SKILL.md` — the section-specific guidelines (§0 Abstract,
  §1 Introduction, …) and the reverse-outline test and anti-inflation polish, which the
  skill says to keep using.

## How to proceed

1. Draft the Abstract with the 5-part flow from `paper-write/SKILL.md:182`; the worked
   example is in `conference-paper-writing/references/writing-guide.md`.
2. Apply the narrative principle from `paper-plan/SKILL.md:95` when freezing the
   outline, and again when writing the Introduction.
3. Use `shared-references/academic-writing.md` for sentence-level clarity, section
   structure, and the de-AI polish pass.
4. These references are support material, not an extra workflow phase
   (`paper-write/SKILL.md:38`). Do not paste their contents into the draft and do not
   turn them into a checklist the user has to approve.
