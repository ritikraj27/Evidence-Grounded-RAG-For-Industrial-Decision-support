# Experiment 7 -- The long-context baseline arm

The threat: the corpus may fit in a modern context window, in which case a reader given everything could answer the question directly and the retrieval machinery would be unnecessary.

## The cost half

- Long-context arm, one query: **202,529 tokens** (the whole corpus, 735 chunks across 14 documents) plus the question (12 tokens).
- RAG arm, one answerable query: **2,246 tokens** (9.4 chunks, retrieved and accepted) plus the question.
- **Ratio: 90x.**
- The RAG arm retrieves 0.90% of the corpus.

| Context window | Holds the whole corpus? |
|---|---|
| claude-sonnet-4-5 / claude-opus-4-5 (1M) | yes |
| a 256K-window model | yes |
| a 128K-window model (most hosted models) | **no** |
| a 32K-window open model | **no** |

## The retrieval-side proxy

With the candidate set widened from the fused shortlist to every chunk in the corpus -- the locating problem a long-context reader faces -- does the same scorer still rank the gold chunk inside the final context?

- Gold chunk in the top 10 of 735: **0.969**
- Top 20: 1.000; top 50: 1.000
- Median rank of the gold chunk: 1 (of 735)

## The quality half

**Not run.** no API credential reachable from this machine: ANTHROPIC_API_KEY and MTP_LLM_API_KEY are unset, the Claude Code CLI is not logged in, and no local generative model is installed. The cost half and the retrieval-side proxy are reported; the quality half is not run and is not estimated.

