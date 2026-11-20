#!/usr/bin/env python3
"""Add the long-context baseline section to the guide's results.

It goes in as E.7; the focus-domain case study becomes E.8 and the synthesis
E.9.

Note on mechanism: `substitute_tokens.py` runs *before* the generators, so a
generated section cannot use `{{TOKEN}}` placeholders -- they would be emitted
literally. The numbers here are interpolated from the experiment's JSON
directly, and the consistency check compares them against the same JSON, so
they still cannot drift.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "deliverables" / "scripts" / "make_results_md.py"

OLD_FOCUS = "## E.7 The focus domain: supply chain management, before and after"
NEW_FOCUS = "## E.8 The focus domain: supply chain management, before and after"

OLD_SYNTH = "## E.8 What the experiments say, together"
NEW_SYNTH = "## E.9 What the experiments say, together"

BLOCK = '''if exp7:
    _c7 = exp7["summary"]["corpus"]
    _p7 = exp7["summary"]["retrieval_proxy"]
    _g7 = exp7["summary"]["generative"]
    _mc7 = (exp7_mc["summary"]["corpus"] if exp7_mc else _c7)
    _mp7 = (exp7_mc["summary"]["retrieval_proxy"] if exp7_mc else _p7)

    def _fits(c, key):
        return "yes" if c["context_window_fits"].get(key) else "**no**"

    _K1M = "claude-sonnet-4-5 / claude-opus-4-5 (1M)"
    _K256 = "a 256K-window model"
    _K128 = "a 128K-window model (most hosted models)"
    w(f"""
## E.7 The long-context baseline arm (Experiment 7)

The largest threat to this work is that the corpus fits in a modern context
window. If a reader given everything could answer the question directly, the
retrieval machinery would be unnecessary and every result in this part would
be beside the point. This section measures what can be measured.

**The cost half, which needs no generator.** The long-context arm puts the
whole corpus in the prompt; the RAG arm puts the retrieved context in it. On
the focus domain the corpus is **{_c7['corpus_tokens']:,} tokens** across
{_c7['corpus_chunks']:,} chunks, and the RAG arm's accepted context averages
**{_c7['rag_context_tokens_mean']:,.0f} tokens** over
{_c7['rag_context_chunks_mean']:.1f} chunks. **The long-context arm costs
{_c7['token_ratio_long_over_rag']:.0f}x more input per query**, and the RAG arm
reaches the evidence using {_c7['corpus_fraction_retrieved'] * 100:.2f}% of
what the long-context arm reads. On the six-category corpus the corpus is
{_mc7['corpus_tokens']:,} tokens and the ratio is
{_mc7['token_ratio_long_over_rag']:.0f}x.

Whether the long-context arm is *possible* is a separate question, and it
depends on the window:

| Context window | Focus domain | Six-category corpus |
|---|---|---|
| 1M tokens | {_fits(_c7, _K1M)} | {_fits(_mc7, _K1M)} |
| 256K tokens | {_fits(_c7, _K256)} | {_fits(_mc7, _K256)} |
| 128K tokens — most hosted models | {_fits(_c7, _K128)} | {_fits(_mc7, _K128)} |

**The retrieval-side proxy, which also needs no generator.** With the candidate
set widened from the fused shortlist to every chunk in the corpus — the
locating problem a long-context reader faces — does the same scorer still rank
the gold chunk inside the final context? On the focus domain, over
{_p7['n_queries']} answerable queries, the gold chunk lands in the top 10 of
{_p7['candidate_set_size']:,} candidates **{_p7['gold_in_top10']:.3f}** of the
time, at a median rank of **{_p7['median_gold_rank']:.0f}**. The evidence is not
merely present in a large context; it is at the top of it.

**What this establishes, and what it does not.** It establishes the cost half
of the comparison, and the cost half is a property of this corpus and this
pipeline rather than of any particular model: the long-context arm is
{_c7['token_ratio_long_over_rag']:.0f}x more expensive per query, and on the
six-category corpus the corpus does not fit in the 128K window that most
hosted models offer at all.

It does **not** establish the quality half. That half needs a generator, and
no API credential was reachable from the machine this was measured on, so it
was not run and is not estimated: **{"run" if _g7.get("ran") else "not run"}**
is the honest answer. The remaining question is therefore narrower than it was,
but it is still open: *given* the whole corpus in context, does a generative
reader answer better than the pipeline does with {_c7['rag_context_chunks_mean']:.1f}
retrieved chunks, and does the {_c7['token_ratio_long_over_rag']:.0f}x token cost
buy the difference?* The proxy says the evidence is findable; it says nothing
about what a reader does with the context once it has it. The harness is in
`impl/experiments/run_long_context.py` and runs as soon as a credential is
present.

""")

'''

LOAD = '''exp7 = _load("exp7_long_context", ["summary"])'''


def main() -> int:
    s = TARGET.read_text(encoding="utf-8")
    failures = []

    # 1. Load the experiment (focus) and its multi-category counterpart.
    m = [ln for ln in s.split("\n") if ln.startswith("exp5 = ")]
    if not m:
        failures.append("the exp5 load was not found")
    else:
        s = s.replace(m[0], m[0] + '\nexp7 = _load("exp7_long_context", ["summary"])\n'
                      'exp7_mc = load_transfer("exp7_long_context", ["summary"])', 1)

    # 2. Renumber the sections after the new one.
    for old, new in ((OLD_FOCUS, NEW_FOCUS), (OLD_SYNTH, NEW_SYNTH)):
        if s.count(old) != 1:
            failures.append(f"count={s.count(old)} -> {old[:40]!r}")
            continue
        s = s.replace(old, new, 1)

    # 3. Insert the section before the focus case study.
    focus_anchor = 'FOCUS_CASE = ROOT / "impl" / "results_focus" / "exp6_focus_case.md"'
    if focus_anchor not in s:
        failures.append("the focus-case anchor was not found")
    else:
        s = s.replace(focus_anchor, BLOCK + focus_anchor, 1)

    if failures:
        for f in failures:
            print(f"!! {f}")
        return 1
    TARGET.write_text(s, encoding="utf-8")
    print("  added the long-context section to the guide's results")
    return 0


if __name__ == "__main__":
    sys.exit(main())
