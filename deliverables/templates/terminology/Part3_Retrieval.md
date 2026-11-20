# Part 3. Retrieval: finding the right passage

### Query

**Plain.** What the user typed, in their own words.

**Technical.** The text submitted to the retrieval system to be matched
against the indexed collection. A query may be natural-language, a keyword
list, or a structured filter.

**Here.** The same query string is used by the form validator, the two
retrieval legs, the reranker and the gate, so that the evidence the gate
judges is the evidence the reader will see.

### Retrieval

**Plain.** Going and finding the passages that might answer the question.

**Technical.** The process of selecting, from a corpus, the units most likely
to be relevant to a query, by scoring every unit and ranking them.

**Here.** Two legs run and their rankings are fused, because a lexical leg and
a dense leg fail in different ways.

### Ranking

**Plain.** Putting the passages in order, best first.

**Technical.** The ordering of retrieved units by estimated relevance to the
query. Ranking is the output of retrieval, and every metric in this work
measures the quality of the ranking rather than the quality of the set.

**Here.** The retrieval slide reports Recall@10, MRR and nDCG@10, which are
three different things you can do with a ranking.

### Relevance

**Plain.** How well a passage answers the question that was asked.

**Technical.** The relation between a retrieved unit and the information need
expressed by the query, judged against a relevance assessment. Here relevance
is operationalised as whether the unit contains the gold chunk.

**Here.** It matters that relevance is defined at the chunk level, so that
the gold chunk is the unit of correctness for every retrieval metric here.

### BM25

**Plain.** The classic way of scoring a passage by how many rare words it
contains, with two knobs that stop long passages from winning by sheer size.

**Technical.** A probabilistic ranking function derived from the Robertson and
Sparck-Jones framework, scoring the term-frequency saturation and inverse
document frequency of query terms in a document, with a length-normalisation
parameter.

**Here.** Okapi BM25 with the Robertson-Sparck-Jones IDF, with k1 set to
{{BM25_K1}} and b to 0.75. It is the lexical leg, and on the focus corpus it
is the stronger one.

### Inverse document frequency

**Plain.** A word's rarity across the collection. A word in every document
counts for nothing; a word in three documents counts for a lot.

**Technical.** The logarithmic ratio of the total document count to the number
of documents containing the term, which is the probabilistic statement that
a term carrying information is a term that occurs in a small fraction of the
collection.

**Here.** The IDF is what makes BM25 prefer the specification that mentions a
rare part number over the manual that mentions a common verb.

### Term frequency

**Plain.** How often the word appears in the passage.

**Technical.** The count of term occurrences in a document, which BM25
saturates: the tenth occurrence of a term in a passage adds far less to the
score than the second.

**Here.** The saturation is the reason a long passage does not simply win by
repeating the query terms.

### The saturation parameter and the length parameter

**Plain.** Two knobs on BM25. The first says how quickly repeating a word
stops helping; the second says how much a long passage is penalised for
being long.

**Technical.** k1 controls the point at which term-frequency saturation
begins, and b controls the degree of length normalisation, with b = 0
meaning no length normalisation and b = 1 full normalisation.

**Here.** k1 is {{BM25_K1}} and b is 0.75, and both are standard values rather
than tuned ones, which is worth saying if asked.

### Lexical leg

**Plain.** One of the two searches, the one that looks for the words.

**Technical.** A retrieval branch that scores candidate units by term overlap
between the query and the unit, without a learned representation. Here it is
Okapi BM25.

**Here.** The lexical leg is the stronger one on the focus corpus: Recall@10
{{R_A}} against the dense leg's {{R_B}}.

### Dense leg

**Plain.** The other search, the one that looks for meaning rather than
words.

**Technical.** A retrieval branch that embeds the query and every candidate
unit into a shared vector space and scores by similarity. It matches on
meaning, so it fails where lexical overlap is absent and succeeds where the
wording differs entirely.

**Here.** The dense leg is significantly worse on the focus corpus, and that
is why the general-purpose sentence encoder was replaced with a
retrieval-trained one.

### Embedding

**Plain.** A list of numbers that stands for the meaning of a piece of text.

**Technical.** A dense vector representation of a piece of text produced by a
neural network, trained so that texts with similar meanings have nearby
vectors. Similarity is then computed in that space.

**Here.** The embeddings are {{EMBED_DIM}} numbers wide, produced by
{{EMBED_MODEL}}. The width is simply the size of the output layer and has no
deeper meaning.

### Bi-encoder

**Plain.** A model that reads the question and the passage separately and
then compares their number-lists.

**Technical.** A dual-encoder architecture in which the query and the
document are embedded independently by two towers with shared parameters, and
scored by a similarity function over the two vectors. Because the document
tower does not depend on the query, its outputs can be precomputed and
indexed.

**Here.** A bi-encoder is what makes retrieval fast at corpus scale, and
also what makes it weaker: the query and the passage never see each other
while the scores are computed.

### Cross-encoder

**Plain.** A model that reads the question and the passage together, and
therefore can notice that the passage really does answer the question.

**Technical.** A single-encoder architecture in which the query and the
document are concatenated and passed through one network, so that the score
is a function of their interaction rather than of two independent scores. It
is accurate and too slow to run over a whole corpus.

**Here.** The cross-encoder is the reranker: it scores a shortlist that the
two legs have already produced, which is the only way its cost is affordable.

### Reranking

**Plain.** Taking the shortlist the search gave you and going through it
properly, one candidate at a time, with a more careful model.

**Technical.** The second-stage scoring of a candidate set produced by a
first-stage retriever, using a more expensive and more accurate model.

**Here.** The reranker is the component whose value turned out to depend on
the corpus: it moves MRR by {{RERANK_MRR_PP}} points on the focus corpus and
{{MC_MRR_RERANK_PP}} points on the six-category one.

### Fusion

**Plain.** Combining the two search rankings into one.

**Technical.** The combination of the rankings or scores produced by two or
more retrievers into a single ranking. Fusion is necessary when the legs
have complementary failure modes.

**Here.** Fusion is what took Recall@10 from the dense leg's {{R_B}} back up
to {{R_C}}, without becoming a significant win over BM25 on its own.

### Reciprocal rank fusion

**Plain.** Combining rankings by adding up a score that depends only on where
each list put a passage, not on its score.

**Technical.** A rank-based fusion function that sums, over the contributing
rankings, the reciprocal of the rank plus a smoothing constant k, so that a
document's fused score depends on its positions rather than on the
incommensurable scores of the systems that produced them.

**Here.** Reciprocal rank fusion is the function from Cormack et al. (2009),
used with k set to {{RRF_K}}. It is prior art, and the deck says so.

### Candidate pool

**Plain.** The shortlist the reranker gets to look at.

**Technical.** The set of units passed from the first-stage retriever to the
reranker, of size k. The pool is a hard ceiling on what the reranker can
return, because it can only reorder what it is given.

**Here.** The pool curve peaks at ten on the focus corpus and falls back to
{{FOCUS_POOL_R10_AT_20}} at twenty, fifty and a hundred. The finding is that more
candidates is not better: the gold chunk is found and then pushed out.

### Top-k

**Plain.** The k best passages, and no more.

**Technical.** The first k units of a ranking. Used both as a retrieval cut-off
and, here, as the size of the final context the generator is given.

**Here.** The final context is {{RERANK_TOP_K_FINAL}} chunks. A pool the same
size as the context cannot improve recall at all, because the reranker can
only permute what it was shown.

### Gold chunk

**Plain.** The one passage that contains the answer, known because the
benchmark was built from it.

**Technical.** The retrieved unit designated by the benchmark as containing
the information need, against which retrieval is scored. It is a labelling
artefact, not a model output.

**Here.** The gold chunk was always correct throughout, so the repair to the
answer labels never touched the retrieval-side measurements.

### Recall at k

**Plain.** Of the passages that contain the answer, how many of them did the
system bring back in its first k.

**Technical.** The proportion of the relevant units that appear in the top k
of a ranking.

**Here.** Recall@10 is the headline retrieval number, and it is what the
seven configurations on slide 12 are compared on.

### Mean reciprocal rank

**Plain.** How far down the list the answer usually is, counting from one,
and averaged over the questions.

**Technical.** The mean over queries of the reciprocal of the rank of the
first relevant unit, so that a relevant unit at rank one contributes 1 and one
at rank ten contributes 0.1.

**Here.** MRR is what the reranker moves, and it is where the two corpora
disagree: {{RERANK_MRR_PP}} points on focus, {{MC_MRR_RERANK_PP}} on the
six-category corpus.

### Normalised discounted cumulative gain

**Plain.** A ranking score that rewards putting the answer near the top, and
is normalised so that two rankings can be compared.

**Technical.** A position-weighted gain accumulated down the ranking and
divided by the gain of the ideal ranking for the same query, so that the
score lies between zero and one.

**Here.** nDCG@10 is the third retrieval column on slide 12, and it is
reported next to Recall@10 because recall alone cannot tell a good ordering
from a lucky one.

### Discounted cumulative gain

**Plain.** Adds up how good each position in the list is, with the
contribution of later positions reduced.

**Technical.** The sum over the ranking of the gain of each retrieved unit
weighted by the logarithm of its inverse rank, so that a relevant unit at
rank one counts more than the same unit at rank ten.

**Here.** It is the numerator of nDCG, and it is what makes the metric
position-sensitive.

### Ideal discounted cumulative gain

**Plain.** What the score would be if the ranking were perfect.

**Technical.** The discounted cumulative gain of the ideal ranking for a
query, which places all the relevant units at the top. It is the denominator
of nDCG and the reason nDCG is comparable across queries.

**Here.** Nothing on the slides; it is in the report's derivation of the
metric.

### Precision at k

**Plain.** Of the k passages you brought back, how many were actually
relevant.

**Technical.** The proportion of the top k of a ranking that is relevant.

**Here.** Not used as a headline, because a system that retrieves one passage
out of a thousand relevant ones scores well on precision and badly on
recall, and the questions this work answers are about not missing the answer.

### Category pre-filter

**Plain.** Narrowing the search to the documents in the question's category
before searching, instead of searching everything and filtering afterwards.

**Technical.** A hard constraint applied to the candidate set before
scoring, in which only units whose category matches a predicted or stated
category are eligible for retrieval.

**Here.** It is a no-op on both corpora, and finding F13 gives the reason: the
filter's recall cost is exactly zero because not one gold chunk sits outside
its question's category. What it does buy is ordering.

### Modality quota

**Plain.** A rule that makes sure the answer's passage is not starved out by
the amount of prose in the pool.

**Technical.** A floor on the number of final-context units drawn from each
modality, applied to the candidate set after retrieval so that the
composition of the context reflects the composition of the question rather
than the composition of the corpus.

**Here.** It is a floor and not a ceiling, and where it is applied turned out
not to matter: the three corpora disagree, and none of the three differences
is significant.

### Displacement

**Plain.** The answer being found and then pushed out of the final list by
something else.

**Technical.** The phenomenon in which a unit present in the candidate pool
is retrieved but excluded from the final context by the reranker's ordering,
so that recall at the context size is lower than recall at the pool size.

**Here.** It is measured on the industrial corpus, where 1.21 percent of the
gold is retrieved and then pushed out of the ten-chunk context, and it is the
mechanism behind the candidate-pool curve.
