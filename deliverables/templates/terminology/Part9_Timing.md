# Part 9. How long it takes

The words a panel member uses when the question is about the system running
rather than the system being right.

### Latency

**Plain.** How long you wait.

**Technical.** The elapsed time between a request being made and the
corresponding response being complete. It is a distribution, not a number,
and a latency claim without a distribution is not a measurement.

**Here.** The retrieval path is {{LAT_TOTAL_MEAN_MS}} milliseconds on average
over the {{LAT_N_QUERIES}} focus-corpus queries, {{LAT_TOTAL_MEDIAN_MS}} at the
median and {{LAT_TOTAL_P95_MS}} at the 95th percentile.

### Response time

**Plain.** The whole time from asking a question to getting the answer.

**Technical.** The end-to-end elapsed time for one query, from the request
arriving to the response being returned, which includes every stage the
request passes through and, if the request is answered, the generation.

**Here.** A refused query returns in {{LAT_RETRIEVAL_S}} seconds, and an
answered one in the sum of that and the generation, which is between
{{GEN_S_PER_ANSWER_MIN}} and {{GEN_S_PER_ANSWER_MAX}} seconds.

### Time to first token

**Plain.** How long before anything appears on the screen.

**Technical.** The interval between the request being sent and the first
token of the response being received. It is the latency a user perceives as
responsiveness, and it is much shorter than the full response time.

**Here.** Not separately measured here, and worth saying so. The system
generates an answer in one block rather than streaming, so the user waits for
the whole answer.

### Throughput

**Plain.** How many you can do at once.

**Technical.** The number of requests completed per unit time, which is the
reciprocal of the service time only when the system is saturated.

**Here.** Not the constraint in this work. The cost is in the model call, and
the framework's own work is small enough that throughput is not the thing a
panel should worry about.

### The median

**Plain.** The middle value: half the queries are faster and half are slower.

**Technical.** The fiftieth percentile of a distribution. It is the
robust summary of a latency distribution, because it is not moved by a single
slow outlier, and it is what should be quoted alongside the mean.

**Here.** The retrieval path's median is {{LAT_TOTAL_MEDIAN_MS}} milliseconds,
against a mean of {{LAT_TOTAL_MEAN_MS}}.

### A percentile

**Plain.** The value below which a given share of the measurements fall.

**Technical.** The value under which a stated proportion of the observations
lie, usually taken as the nearest-rank value of the ordered sample. The 95th
percentile is the one quoted in a service commitment.

**Here.** The 95th percentile of the retrieval path is
{{LAT_TOTAL_P95_MS}} milliseconds, and the slowest query in the run took
{{LAT_TOTAL_MAX_MS}}.

### Wall clock

**Plain.** The clock on the wall.

**Technical.** Elapsed real time, as opposed to a count of processor time.
It includes everything the process waited for, including the network.

**Here.** Every timing in this work is wall clock, because the question a user
asks is about waiting, not about how much processor was used.

### The dominant term

**Plain.** The one part that takes almost all the time.

**Technical.** The summand that accounts for nearly all of a total, and
therefore the one worth optimising.

**Here.** The cross-encoder rerank is {{LAT_RERANK_MS}} of the
{{LAT_TOTAL_MEAN_MS}} milliseconds of the retrieval path. The query embedding
is {{LAT_EMBED_MS}}, the dense leg {{LAT_DENSE_MS}} and the lexical leg
{{LAT_BM25_MS}}, and the rank fusion, the modality quota and the gate
together come to under a millisecond.

### A batch total

**Plain.** The time for the whole run, not for one query.

**Technical.** The summed elapsed time of a run over many queries. It gives
the average only when the number of queries is known and every query did the
same work, which is not true of an arm that refuses some questions.

**Here.** The archived generation runs record a batch total per arm, and
those totals are what the generation stage is derived from, because the
retrieval path is measured directly and the difference between the two is the
model call.

### Warm-up

**Plain.** The first run, which is slower because everything has to be
loaded.

**Technical.** The first execution of a model or an index, which pays for
loading weights and building caches. It is discarded before any measurement
is taken, because it is a startup cost and not a per-query cost.

**Here.** The latency run warms up on a query that is not in the benchmark,
so that no benchmark query is served from the in-memory rerank cache and
every one of them pays a live rerank.

### A cache

**Plain.** A note that says "I have already done this, here is the answer".

**Technical.** A stored result of a previous computation, returned when the
same inputs recur. A cache makes a repeated measurement fast, and it makes
that measurement a measurement of the cache rather than of the computation.

**Here.** The reranker scores are cached in memory within a run. The latency
run is careful about this, and the warm-up query is chosen so that the
cached path cannot make a benchmark query look fast.

### A refusal is not a faster answer

**Plain.** Saying no takes just as long as the work that came before it; it
just skips the part after.

**Technical.** The property of a decision placed late in a pipeline, where
the work upstream of the decision is done whether or not the decision
succeeds. Only the work downstream of it is saved.

**Here.** The gate's decision is taken at the end of the retrieval path, so a
refused query costs the same {{LAT_RETRIEVAL_S}} seconds of retrieval and
then stops. What a refusal saves is the generation, because the model is
never called. On the focus benchmark the gate refused
{{LAT_GATE_REFUSED_N}} of the {{LAT_N_QUERIES}} queries.

### An upper bound

**Plain.** A number that is definitely too big, so the true value is smaller.

**Technical.** A quantity known to be at least as large as the quantity of
interest, derived by including work that the user does not actually wait for.

**Here.** The generation figure, between {{GEN_S_PER_ANSWER_MIN}} and
{{GEN_S_PER_ANSWER_MAX}} seconds per answered query, is an upper bound,
because the archived arm totals also carry the offline claim-scoring pass
that a user never waits for.
