
---

# Part 10. One page of cheat sheet

| If they ask about | the word is | and the number is |
|---|---|---|
| the data | corpus | {{N_FOCUS_CHUNKS}} chunks, {{N_FOCUS_DOCUMENTS}} documents, {{N_FOCUS_QUERIES}} queries |
| the search | BM25, dense retrieval, RRF, a cross-encoder | Recall@10 {{R_A}} for BM25 alone |
| the check | the confidence gate | threshold {{FOCUS_GATE_TAU}}, coverage {{FOCUS_GATE_COVERAGE}}, abstention precision {{FOCUS_GATE_ABST_PRECISION}} |
| the headline | the rate of answering unanswerable questions | {{GEN_A_NOGATE_UNANS_ANSWER_RATE}} down to {{GEN_A_FITTED_UNANS_ANSWER_RATE}}, p {{GEN_PAIRED_FITTED_UNANS_P}} |
| the control | the random-escalation arm | answers {{GEN_A_RANDOM_UNANS_ANSWER_RATE}}, refuses {{GEN_PAIRED_RANDOM_ANS_B}} answerable |
| what the score buys | refusal precision | {{GEN_PAIRED_FITTED_ANS_B}} against {{GEN_PAIRED_RANDOM_ANS_B}}, and {{TRADE_ANSWERING_WRONG_REMOVED}} wrong answers removed for {{TRADE_ANSWERING_CORRECT_COST_NLI}} |
| the benchmark | the audit | {{UNANS_MATCH_RATE}} certificates, ROC AUC {{UNANS_POLICY_AUC}} and {{UNANS_MC_SEP_AUC}} |
| the repair | the shortcut | {{UNANS_BEFORE_REFUSED_PCT}} before, {{UNANS_HARD_REFUSED_PCT}} after |
| the failure | the contradiction gate | {{CONTRA_PRECISION_PCT}} precision, upper bound {{CONTRA_PRECISION_CI_HI}}, {{CONTRA_PRECISION_AGREE_N}} of {{CONTRA_PRECISION_AGREE_N}} annotator agreement |
| the limit | the transfer | {{GEN_A_XFER_ANS_ANSWERED}} answerable answered against {{GEN_A_NOGATE_ANS_ANSWERED}} |
| the gap | one generator | no text on {{GENCOMP_FAILING_EMPTY_N}} of {{GENCOMP_FAILING_EMPTY_TOTAL}} |
| the cost | long context | {{GEN_LC_TOKEN_RATIO}} times the tokens, {{GEN_LC_COST_RATIO}} times the cost |
| the speed | the retrieval path | {{LAT_TOTAL_MEAN_MS}} ms mean, {{LAT_TOTAL_MEDIAN_MS}} median, {{LAT_TOTAL_P95_MS}} at the 95th percentile |
| a refusal | the gate's decision | {{LAT_RETRIEVAL_S}} s, and no model call at all |
| an answer | the generation | {{GEN_S_PER_ANSWER_MIN}} to {{GEN_S_PER_ANSWER_MAX}} s, of which the framework is {{LAT_RETRIEVAL_S}} s |
