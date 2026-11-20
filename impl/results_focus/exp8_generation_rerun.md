# Experiment 8 -- generator-side comparison

One generator, five arms, the same questions and the same scorer.

- condition: `cautious`
- model: `MiniMax-M3`
- answerable questions: 32, unanswerable questions: 144

| Arm | Unanswerable answered | Unanswerable claim hallucination | Answerable answered | Answerable accuracy (NLI) | Claim support (all) |
|---|---|---|---|---|---|
| rag_nogate | 0.535 (77/144) | 0.554 | 0.938 | 0.633 | 0.539 |
| rag@fitted | 0.417 (60/144) | 0.566 | 0.938 | 0.800 | 0.564 |
| rag@random | 0.375 (54/144) | 0.529 | 0.656 | 0.714 | 0.558 |
| rag@transferred | 0.014 (2/144) | 0.333 | 0.188 | 0.333 | 0.581 |

**The two unanswerable columns answer different questions.** `answer_rate` is how often the arm answers at all when the answer does not exist -- the opportunity for hallucination. `claim_hallucination_rate` is of the claims it did produce, how many are supported by nothing in the corpus -- fabrication. A system that refuses everything scores zero on the second and is useless, so the first is the headline.

**The gate's effect, paired question by question.** `b` is the number of questions the ungated arm answered and the gated arm refused; `c` is the reverse; `p` is the exact two-sided McNemar test on the discordant pairs.

| Arm | Set | n | b | c | p |
|---|---|---|---|---|---|
| rag@fitted | unanswerable | 144 | 23 | 6 | 0.0023 |
| rag@fitted | answerable | 32 | 2 | 2 | 1.0000 |
| rag@random | unanswerable | 144 | 30 | 7 | 0.0002 |
| rag@random | answerable | 32 | 11 | 2 | 0.0225 |
| rag@transferred | unanswerable | 144 | 75 | 0 | 0.0000 |
| rag@transferred | answerable | 32 | 25 | 1 | 0.0000 |
