# Output Language Protocol

> **Status: not published upstream.** This file is referenced by 8 installed skills
> (`experiment-plan`, `research-refine`, `research-refine-pipeline`, `idea-creator`,
> `idea-discovery`, `paper-plan`, `paper-writing`, `grant-proposal`), but the upstream suite
> `github.com/Chanw-research/claude-code-paper-writing` never published it. This
> document was written locally to keep those references resolvable; it does not
> restate upstream policy.

> **中文摘要：** 本文档是本地补写的指针，上游从未发布。默认随用户输入语言（见 `.claude/CLAUDE.md`）；`paper-writing` 例外，始终输出英文 LaTeX 以便投稿。

## What this reference governs

The 8 sites share one `## Output Protocols` block; 7 summarise this reference as "respect
the project's language setting", while `paper-writing/SKILL.md:653` overrides it with
"note: paper-writing always outputs English LaTeX for venue submission". The reference
therefore governs the language of every generated output file — prose reports, plans,
proposals, trackers — subject to that one hard exception.

## Where the operative guidance actually lives

- The project-level default: `.claude/CLAUDE.md` ("Key Rules") states that the default
  output language matches the user's input (Traditional Chinese or English).
- `.claude/skills/grant-proposal/SKILL.md` carries a concrete `LANGUAGE = auto` constant
  with its own detection rule (KAKENHI→Japanese, NSF→English, NSFC→Chinese, ERC/DFG/SNSF/
  ARC/NWO→English) and an explicit override form — the clearest worked example of the
  protocol in this suite.
- `.claude/references/bilingual-output.md` defines the paragraph-by-paragraph
  English + Chinese comparison output format, if the user asks for a bilingual artifact.
- `.claude/skills/paper-writing/SKILL.md` — the English-LaTeX exception for venue
  submission.

## How to proceed

1. Default to the user's input language, per `.claude/CLAUDE.md`.
2. Let a skill's own `LANGUAGE` constant win over the default — `grant-proposal` already
   auto-detects per grant type.
3. For `paper-writing`, output English LaTeX regardless of the user's language; venue
   submission is the stated reason.
4. If the user asks for a bilingual artifact, follow `.claude/references/bilingual-output.md`
   for the exact format rather than improvising one.
