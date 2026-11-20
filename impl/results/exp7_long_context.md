# Experiment 7 -- The long-context baseline arm

The threat: the corpus may fit in a modern context window, in which case a reader given everything could answer the question directly and the retrieval machinery would be unnecessary.

## The cost half

- Long-context arm, one query: **680,417 tokens** (the whole corpus, 2,383 chunks across 46 documents) plus the question (11 tokens).
- RAG arm, one answerable query: **2,399 tokens** (9.6 chunks, retrieved and accepted) plus the question.
- **Ratio: 282x.**
- The RAG arm retrieves 0.34% of the corpus.

| Context window | Holds the whole corpus? |
|---|---|
| claude-sonnet-4-5 / claude-opus-4-5 (1M) | yes |
| a 256K-window model | **no** |
| a 128K-window model (most hosted models) | **no** |
| a 32K-window open model | **no** |

## The retrieval-side proxy

With the candidate set widened from the fused shortlist to every chunk in the corpus -- the locating problem a long-context reader faces -- does the same scorer still rank the gold chunk inside the final context?

- Gold chunk in the top 10 of 2,383: **0.902**
- Top 20: 0.932; top 50: 0.970
- Median rank of the gold chunk: 1 (of 2,383)

## The quality half

**Not run.** no API credential reachable from this machine: ANTHROPIC_API_KEY and MTP_LLM_API_KEY are unset, the Claude Code CLI is not logged in, and no local generative model is installed. The cost half and the retrieval-side proxy are reported; the quality half is not run and is not estimated.

