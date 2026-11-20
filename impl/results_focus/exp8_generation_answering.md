# Experiment 8 -- generator-side comparison

One generator, five arms, the same questions and the same scorer.

- condition: `answering`
- model: `MiniMax-M3`
- answerable questions: 32, unanswerable questions: 144

| Arm | Unanswerable answered | Unanswerable claim hallucination | Answerable answered | Answerable accuracy (NLI) | Claim support (all) |
|---|---|---|---|---|---|
| rag_nogate | 0.938 (135/144) | 0.569 | 1.000 | 0.656 | 0.481 |
| rag@fitted | 0.528 (76/144) | 0.578 | 0.938 | 0.667 | 0.498 |
| rag@random | 0.604 (87/144) | 0.642 | 0.656 | 0.714 | 0.402 |
| rag@transferred | 0.021 (3/144) | 0.200 | 0.188 | 0.000 | 0.486 |
| long_context | 0.931 (134/144) | 0.620 | 1.000 | 0.406 | 0.430 |

**The two unanswerable columns answer different questions.** `answer_rate` is how often the arm answers at all when the answer does not exist -- the opportunity for hallucination. `claim_hallucination_rate` is of the claims it did produce, how many are supported by nothing in the corpus -- fabrication. A system that refuses everything scores zero on the second and is useless, so the first is the headline.

**The gate's effect, paired question by question.** `b` is the number of questions the ungated arm answered and the gated arm refused; `c` is the reverse; `p` is the exact two-sided McNemar test on the discordant pairs.

| Arm | Set | n | b | c | p |
|---|---|---|---|---|---|
| rag@fitted | unanswerable | 144 | 60 | 1 | 0.0000 |
| rag@fitted | answerable | 32 | 2 | 0 | 0.5000 |
| rag@random | unanswerable | 144 | 50 | 2 | 0.0000 |
| rag@random | answerable | 32 | 11 | 0 | 0.0010 |
| rag@transferred | unanswerable | 144 | 132 | 0 | 0.0000 |
| rag@transferred | answerable | 32 | 26 | 0 | 0.0000 |
| long_context | unanswerable | 143 | 7 | 6 | 1.0000 |
| long_context | answerable | 32 | 0 | 0 | 1.0000 |
