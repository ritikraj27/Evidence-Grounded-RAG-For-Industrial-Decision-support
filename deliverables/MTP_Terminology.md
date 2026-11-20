---
title: "The Words of This Work"
subtitle: "Every keyword, in plain language and in technical language, with the number that belongs to it"
author: "Ritik Raj (25IM60R12), Department of Industrial and Systems Engineering, IIT Kharagpur"
date: ""
shorttitle: "The terminology guide"
---
# How to read this

This is the vocabulary of the work. Every term a panel might use, and every
term the deck uses, is here twice: once in ordinary words, for the moment when
you need to follow a question rather than lead one, and once in the technical
words, for the moment when you need to answer precisely.

**Why two.** An examiner who asks about "sufficiency" or "abstention precision"
is testing whether you know the technical sense. A practitioner who asks what
"the corpus" is, or what a "tolerance" is, is testing whether you know the
subject. Being able to move between the two registers, without either losing
the thread, is most of what defending this work asks.

**How each entry is written.** Three paragraphs, always in the same order.

- **Plain.** What the word means in ordinary language.
- **Technical.** What the word means in the precise sense used by the field
  and by this work.
- **Here.** What the word means in *this* work, with the measured number
  where a number belongs.

**Where the numbers come from.** Every figure in the third paragraph is
substituted from the archived result files when this document is built, so it
cannot drift away from the deck or the report. Where a number does not appear,
the sentence says what the term is for rather than what it came out at.

**What this document does not do.** It does not replace the report, which
carries the derivations, and it does not replace the technical companion,
which carries every formula with its symbols named and its origin stated. It
is the layer in between: the words, in both registers, with the work's own
numbers attached.

# Part 1. The industrial setting

These are the words from the domain the framework is built for. They are the
ones an examiner in industrial engineering is most likely to use, and the ones
a computer-science examiner is most likely to find unfamiliar.

### Procedure

**Plain.** The written instruction that says how to do a particular job, in
the order it has to be done.

**Technical.** A controlled document specifying a sequence of operations on
specified equipment or material, with stated preconditions. In a quality
system a procedure is a controlled artefact with an owner, a revision number
and an approval record.

**Here.** The industrial corpora contain procedures of this kind: setup and
calibration instructions, inspection routines, and test procedures.

### Specification

**Plain.** The document that says what a thing has to be: how big, how strong,
how accurate, how it must be made.

**Technical.** A set of requirements, usually quantified, that a product,
material, process or service must satisfy. A specification is normative
rather than descriptive: it states what shall be, and conformance is decided
against it.

**Here.** The questions the benchmark asks are specification questions. "What
is the stated tolerance on the shaft?" and "What does the procedure require
before the run?" are both answerable only from a retrieved specification.

### Tolerance

**Plain.** How far a measurement is allowed to be from the number on the
drawing. A shaft specified at 25.00 millimetres with a tolerance of 0.05 is
acceptable anywhere between 24.95 and 25.05.

**Technical.** The permitted deviation of a measured quantity from its
nominal or specified value, usually written as a limit pair, an interval, or
a plus-or-minus value. It is a property of the requirement, not of the part:
the tolerance is set by function, cost and risk, and it is the same for every
part in a batch.

**Here.** The opening example of the whole talk is a tolerance that the model
quotes without support. A wrongly fabricated tolerance is not a wrong answer
in the way a wrong summary is a wrong answer; it is a number that a
manufacturing engineer would act on.

### Calibration record

**Plain.** The sheet that says when an instrument was last checked against a
known standard, what it read at the time, and whether it passed.

**Technical.** A record of the comparison of a measuring instrument or
standard against a traceable reference, giving the result, the date and the
traceability chain. A calibration record is evidence about an instrument's
state at a point in time, not about the thing the instrument later measured.

**Here.** Calibration records are one of the four document types the industrial
corpus is built from, and they are the clearest case of a document whose
answer depends on a date.

### Control plan

**Plain.** The document that says, for each step of a process, what has to be
checked, how often, to what limit, and what to do when it is out.

**Technical.** A structured set of instructions describing the controls to be
applied at each process step, including the characteristic to be controlled,
the specification limits, the measurement method, the sample size and the
reaction plan on non-conformity.

**Here.** Control plans are among the corpus's modalities. They are also the
reason the retrieval system needs a modality quota: a question about a
control limit is usually answered from a table, and a text-only ranking
system tends to starve it.

### Failure mode and effects analysis

**Plain.** A study that lists every way a thing can go wrong, how bad each
one is, how likely it is, and what to do about it.

**Technical.** A structured, qualitative risk-analysis method that
decomposes a system into functions, identifies potential failure modes for
each, and assesses each by severity, occurrence and detectability, with
mitigation actions assigned.

**Here.** FMEA documents are in the corpus because they are where the
industrial domain already writes down what can go wrong. They are a natural
source of unanswerable questions: the corpus describes failure modes for a
particular process, and a question about a mode the document never mentions is
genuinely unanswerable from it.

### Bill of materials

**Plain.** The list of everything that goes into a product: the parts, how
many of each, and what each one is called.

**Technical.** A structured inventory of the components and sub-assemblies
that make up a product, with quantities, part numbers, revision levels and
the parent-child relationships between them.

**Here.** The bill of materials is the clearest case of a document where a
question has a right answer only at a particular revision. The corpus
carries the revision, and a question asked at the wrong revision is
unanswerable rather than ambiguous.

### Economic order quantity

**Plain.** How many units to order at one time, so that the cost of holding
stock and the cost of running out balance out.

**Technical.** The order quantity minimising the sum of ordering cost and
holding cost under a standard demand model, computed from the periodic
demand rate, the ordering cost per order, and the per-unit-per-period holding
cost.

**Here.** It is one of the worked examples in the plain-language guide,
because it is the kind of question a procurement engineer asks and because
the answer sits in a formula inside a document rather than in the model's
weights.

### Safety stock

**Plain.** Extra stock kept on the shelf so that a surprise does not stop the
line.

**Technical.** Inventory held above the expected replenishment requirement to
buffer against variability in demand or supply, sized from a service-level or
safety-factor argument rather than from the average requirement.

**Here.** It appears as a term the model must retrieve rather than recall,
and it is a good test of whether the retrieval is reaching the right
document: a generic definition of safety stock is available in the model's
weights, and a definition tied to this plant's policy is not.

### Incoterm

**Plain.** The rulebook that says who is responsible for the goods, and who
pays for what, at each stage of an international shipment.

**Technical.** A standardised set of rules published by the International
Chamber of Commerce defining the responsibilities of buyers and sellers in
the delivery of goods across borders, in particular the point at which risk
and cost pass from one party to the other.

**Here.** Incoterms appear in the industrial corpus as a classification a
question can be asked against, which makes them a good source of both
answerable and unanswerable questions.

### Regulatory text

**Plain.** The binding rules themselves, published by a regulator, with legal
force.

**Technical.** The normative text of a statute or regulation, as distinct
from guidance, explanatory material and commentary. In the United States
federal context the Code of Federal Regulations is the codified form of
executive-branch regulations.

**Here.** The federal regulatory corpus is 2,443 chunks from
110 documents spanning 4 regimes, read from
the Electronic Code of Federal Regulations. It is the corpus where the
contradiction phenomenon was looked for, because a provision that has been
amended is a conflict whose type is known by construction.

### Jurisdiction

**Plain.** The legal territory a rule applies in. A requirement written for
one country is not automatically a requirement in another.

**Technical.** The geographic and legal scope within which a law, regulation
or standard has force. In this work it is both a corpus property and a limit
on the claim: a finding measured on one jurisdiction's text is not
established for another.

**Here.** Limitation L8 of the deck is the jurisdiction limitation, and it is
listed as one of the eight things the work does not claim.

### Regime

**Plain.** A whole area of regulation, treated as one family: all the rules
about a particular subject.

**Technical.** A coherent body of regulatory material, such as occupational
safety or environmental protection, drawn from a defined set of instruments
and administered as a unit.

**Here.** The regulatory corpus is organised into 4 regimes, so
that a question can be asked within a regime and a conflict can be located
across regimes.

### Work instruction

**Plain.** The document that tells one person, at one station, what to do at
each step.

**Technical.** A detailed, task-level instruction for a specific operation or
station, usually a controlled document derived from a procedure and containing
the sequence, the tools, the acceptance criteria and the records to be
completed.

**Here.** Work instructions are short, procedural, and dense in numbers, which
is the combination that makes them hard for a lexical ranker and useful for
the modality quota.

### Maintenance log

**Plain.** The running record of what was done to a machine, when, and what
was found.

**Technical.** A chronological record of maintenance activities, carrying the
asset identifier, the date, the activity type, the parts replaced, the
readings taken and the outcome, retained as evidence of the asset's
condition.

**Here.** Maintenance logs are the corpus's record type where the answer
depends on the most recent entry rather than on any single one, which makes
them a good test of whether the system cites the right passage.

### Non-conformance

**Plain.** A documented instance of something not meeting its requirement.

**Technical.** A recorded departure from a specified requirement, with the
requirement, the observed condition, the disposition (rework, use-as-is,
repair, reject, scrap) and the approvals. The record is the evidence that a
departure was detected and dispositioned.

**Here.** A non-conformance record is a rare kind of document in a public
corpus, and its absence is exactly the sort of thing a question can turn on:
a question about what happened to a specific non-conformance is unanswerable
from a corpus that never mentions it.

### Revision

**Plain.** The version number that says which issue of a document this is, and
what changed.

**Technical.** The controlled identifier of an issue of a document, tied to a
date and to an approval. A requirement's meaning is a function of its
revision, so a corpus that mixes revisions without recording them cannot
answer revision-dependent questions reliably.

**Here.** The corpus records the revision of every document it ships, and the
bill-of-materials questions are the ones where a wrong revision would produce
a plausible and wrong answer.

### Traceability

**Plain.** Being able to follow a number back to where it came from and prove
it along the way.

**Technical.** The property of a record or a product that its origin, and the
steps it has passed through, can be established and demonstrated. In
metrology it additionally denotes the unbroken chain of calibrations linking
an instrument to a national or international standard.

**Here.** Traceability is the property the whole framework is designed to
restore. The claim scorer attaches a citation to every claim, and the corpus
ships a SHA-256 of every document, so a reader can go from an answer back to
the exact bytes it came from.

# Part 2. The corpus and how it was prepared

### Corpus

**Plain.** The pile of documents the system reads. Everything the system can
answer from has to be in there, and nothing outside it counts.

**Technical.** A collection: the set of documents being searched, segmented
into retrievable chunks. Retrieval is defined relative to a collection, and
every retrieval metric in this work is a function of the corpus it was
measured on.

**Here.** Four corpora, each with one job. The focus corpus carries the
ablation, the gate and the generation experiment.

### Document

**Plain.** One original file, in its entirety, with its own identity and its
own provenance.

**Technical.** A retrievable unit at the level of authorship or publication:
a single PDF, a single regulation, a single manual. Documents are the unit
of provenance and licensing; chunks are the unit of retrieval.

**Here.** The focus corpus has 14 documents; the
six-category corpus has 46; the industrial corpus has
110; the regulatory corpus has 110.

### Chunk

**Plain.** A piece of a document, cut up so that the system can retrieve one
piece rather than a whole file.

**Technical.** A retrievable unit of evidence: a contiguous span of a
document, of bounded length, carrying metadata identifying its parent
document, its modality, its category and its position.

**Here.** Chunks average 101 words. The chunk is deliberately the
unit a practitioner can go and read in the source document.

### Chunking

**Plain.** Deciding where to cut the documents up.

**Technical.** The segmentation of a document into retrievable units,
together with the decision of which metadata to attach to each unit and how
to handle headings, tables and figures that straddle a boundary.

**Here.** Chunking is a design decision, not a preprocessing detail, because
a table cut down the middle is not retrievable as a table. That is one of
the reasons the modality is recorded on every chunk.

### Token

**Plain.** The unit the language model actually reads and writes. Models do
not see words; they see pieces of words.

**Technical.** A sub-word unit produced by a tokenizer, mapping text to a
sequence of integer identifiers. Token counts, and therefore context limits
and prices, are measured in tokens rather than in words or characters.

**Here.** The long-context comparison is a token comparison: 202,529
tokens for the whole corpus against 2,246 for the accepted context.

### Tokenisation

**Plain.** Turning text into tokens, and back.

**Technical.** The reversible mapping between text and token identifiers, with
a vocabulary fixed at the time the model was trained.

**Here.** It matters because a token is a fraction of a word, so the same
document costs different amounts with different models, and because the
chunk boundary is chosen in words while the context limit is counted in
tokens.

### Modality

**Plain.** What kind of thing a piece of the document is: written prose, a
table, a chart, or a figure.

**Technical.** The representational format of a retrieved unit, distinguished
here by the kind of query it can answer: prose carries narrative and
procedural content, tables carry parameter values and limits, and charts and
figures carry trends and shapes.

**Here.** Every chunk carries its modality. The modality quota exists to stop
a text-heavy pool from starving a modality that holds the answer.

### Category

**Plain.** What subject the document is about.

**Technical.** A subject label attached to a document or a chunk, drawn from a
controlled vocabulary of categories used to partition the corpus.

**Here.** The focus corpus is single-category by construction; the
six-category corpus has six categories. The category
pre-filter on slide 12 is a no-op on both, and finding F13 explains why.

### Provenance

**Plain.** Where a document came from, and what was done to it.

**Technical.** The recorded chain of custody for a dataset element: its
origin, its identifier at the origin, the transformations applied to it, and
the licence under which it is redistributed.

**Here.** The corpus ships with its provenance attached, and the plain-language
guide makes a point of it: a corpus that cannot be traced is the reason the
substitute ships with a trace.

### SHA-256

**Plain.** A fingerprint of a file. Change one character anywhere and the
fingerprint changes completely.

**Technical.** A cryptographic hash function producing a 256-bit digest of a
message. It is preimage resistant and collision resistant, so a digest is
evidence that two files are the same bytes, not a signature of who produced
them.

**Here.** Every document in the corpus carries the SHA-256 of its content, so
a reader can confirm that the chunk they were shown came from the file the
manifest says it came from.

### Licence

**Plain.** The permission that says what may be done with the document and
what must be credited.

**Technical.** The legal grant under which a document is redistributed,
carrying obligations that the redistributing dataset must satisfy: attribution,
share-alike, and sometimes non-commercial restriction.

**Here.** The corpus is English Wikipedia industrial-engineering text under
CC BY-SA 4.0, and the licence travels with each document.

### Manifest

**Plain.** The index of everything in the package: what is in it, how much,
and what each piece is.

**Technical.** A machine-readable inventory file listing the elements of a
dataset with their identifiers, counts and checksums, sufficient to verify
that a copy of the data is complete and unaltered.

**Here.** The manifest is what makes the corpus checkable rather than
merely downloadable.

### Public substitute

**Plain.** A stand-in for the real thing, which anyone can look at.

**Technical.** A dataset constructed to stand in for a proprietary one that
cannot be redistributed, matching its properties as closely as possible and
carrying its own provenance so that the claims made on it can be audited.

**Here.** The primary corpus was proprietary supply-chain text that cannot be
redistributed, so every measurement runs on a public substitute. The claims
are narrowed to match, and slide 2 says so.

### De-duplication

**Plain.** Making sure the same text does not appear twice, because a
duplicate makes a benchmark look easier than it is.

**Technical.** The removal of near-identical records from a dataset, by exact
hash or by similarity, so that train and evaluation splits do not share
content and so that a frequency count is not inflated.

**Here.** The chunk identifiers are unique across the corpus, and the
benchmark's answerable and unanswerable classes are built to share no word,
which is a stronger condition than de-duplication alone.

### Focus corpus

**Plain.** The one corpus that carries the main results.

**Technical.** The supply-chain corpus used for the ablation, the gate
fitting and the generation experiment: 735 chunks from
14 documents, with 176 queries of which
32 are answerable.

**Here.** When a number in this talk is quoted without a corpus, this is the
corpus it came from.

### Six-category corpus

**Plain.** The corpus built to check whether the findings survive on material
from outside the one category.

**Technical.** The generalisation corpus, 2,383 chunks from
46 documents spanning six categories, with
276 queries.

**Here.** It carries the cross-category transfer study and the half of the
long-context comparison that could not be run on the focus corpus.

### Industrial corpus

**Plain.** The corpus built for the purpose, out of real regulatory
documents.

**Technical.** The InduSight industrial regulatory corpus: 2,443
chunks from 110 United States federal regulatory documents
read through the Electronic Code of Federal Regulations, with
444 queries and 4 regimes.

**Here.** It carries the candidate-pool curve, the quota trade, and the
contradiction detector's phenomenon.

### Federal regulatory corpus

**Plain.** The regulatory material the contradiction detector was pointed at.

**Technical.** The 4 United States federal regimes that make
up the industrial regulatory corpus, read at two past dates so that the same
provision at two issues is a conflict whose type is known by construction.

**Here.** The contradiction detector's precision against reader labels is
0.0%, on 20 labelled alarms, and the
finding is that the corpus does not hold the phenomenon the detector detects.

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
1.2 and b to 0.75. It is the lexical leg, and on the focus corpus it
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

**Here.** k1 is 1.2 and b is 0.75, and both are standard values rather
than tuned ones, which is worth saying if asked.

### Lexical leg

**Plain.** One of the two searches, the one that looks for the words.

**Technical.** A retrieval branch that scores candidate units by term overlap
between the query and the unit, without a learned representation. Here it is
Okapi BM25.

**Here.** The lexical leg is the stronger one on the focus corpus: Recall@10
0.969 against the dense leg's 0.812.

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

**Here.** The embeddings are 1024 numbers wide, produced by
BAAI/bge-m3. The width is simply the size of the output layer and has no
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
the corpus: it moves MRR by -0.3 points on the focus corpus and
11.1 points on the six-category one.

### Fusion

**Plain.** Combining the two search rankings into one.

**Technical.** The combination of the rankings or scores produced by two or
more retrievers into a single ranking. Fusion is necessary when the legs
have complementary failure modes.

**Here.** Fusion is what took Recall@10 from the dense leg's 0.812 back up
to 1.000, without becoming a significant win over BM25 on its own.

### Reciprocal rank fusion

**Plain.** Combining rankings by adding up a score that depends only on where
each list put a passage, not on its score.

**Technical.** A rank-based fusion function that sums, over the contributing
rankings, the reciprocal of the rank plus a smoothing constant k, so that a
document's fused score depends on its positions rather than on the
incommensurable scores of the systems that produced them.

**Here.** Reciprocal rank fusion is the function from Cormack et al. (2009),
used with k set to 60. It is prior art, and the deck says so.

### Candidate pool

**Plain.** The shortlist the reranker gets to look at.

**Technical.** The set of units passed from the first-stage retriever to the
reranker, of size k. The pool is a hard ceiling on what the reranker can
return, because it can only reorder what it is given.

**Here.** The pool curve peaks at ten on the focus corpus and falls back to
0.969 at twenty, fifty and a hundred. The finding is that more
candidates is not better: the gold chunk is found and then pushed out.

### Top-k

**Plain.** The k best passages, and no more.

**Technical.** The first k units of a ranking. Used both as a retrieval cut-off
and, here, as the size of the final context the generator is given.

**Here.** The final context is 10 chunks. A pool the same
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
disagree: -0.3 points on focus, 11.1 on the
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

# Part 4. The generator and the answer

### Generator

**Plain.** The part that writes the answer.

**Technical.** The model that conditions on a prompt and produces text. It is
a conditional distribution over the next token, sampled repeatedly.

**Here.** One generator is tested. A second could not be, because it returned
no text on 24 of the 66
questions, which is limitation L1 and the first item on the future-work list.

### Reader

**Plain.** The part that reads the passages and writes the answer from them.

**Technical.** The generation component of a retrieval-augmented system: the
module that takes the retrieved context and the query and produces the
grounded answer, as opposed to the retriever that found the context.

**Here.** The reader and the retriever are separate, and the gate sits
between them, so that a refusal costs no model call at all.

### Prompt

**Plain.** Everything you send the model: the instructions, the question, and
the passages.

**Technical.** The full input to the model, comprising a system instruction,
the retrieved context and the user query. The prompt is the only channel
through which the retrieved evidence reaches the generator.

**Here.** The prompt is the lever the experiment turns on: the two conditions
differ only in whether the instruction requires an answer or permits a
decline.

### System instruction

**Plain.** The standing instruction that tells the model how to behave.

**Technical.** The part of the prompt that sets the model's role and its
constraints, as opposed to the task content.

**Here.** It is where "you must answer" and "you may decline" are written,
which is what makes the two prompt conditions differ by one clause and
nothing else.

### Context window

**Plain.** How much the model can hold in its head at once.

**Technical.** The maximum number of tokens the model can attend to in one
forward pass, fixed at training and deployment time.

**Here.** The cross-category corpus does not fit a 128K-token window, which
is why the whole-corpus arm of the long-context comparison could not be run
there.

### Long context

**Plain.** Putting a lot of material into the prompt at once instead of
searching for the right bit.

**Technical.** The use of a long context window to carry a large corpus
directly, removing the retrieval step, and the comparison of that regime with
a retrieve-then-read regime on coverage, accuracy and cost.

**Here.** The focus corpus is 202,529 tokens against a pipeline
context of 2,246, which is 74 times the
tokens. The cost ratio is 58.8 times, because
33.0% of the requests were served as a cache read.

### Hallucination

**Plain.** The model stating something that is not in the source material,
fluently and confidently.

**Technical.** The generation of text that is not grounded in the retrieved
context. In this work the term is used in the strict sense of unfaithful to
the context, which is narrower and more measurable than "anything false".

**Here.** The measurement in this work is on the rate of answering
unanswerable questions, not on the hallucination rate in generated text.
Those are different quantities with different instruments, and limitation L6
says so.

### Claim

**Plain.** One assertion in the answer, small enough to be checked on its own.

**Technical.** A single proposition extracted from the generated text, to be
labelled with a support status and a confidence.

**Here.** Claims are the unit of the per-claim annotation, and the reason the
frontier in this work is reported at the level of the individual answer claim
rather than at the level of the answer.

### Entailment

**Plain.** The passage says the claim follows.

**Technical.** The relation in which a premise makes a hypothesis necessarily
true, so that the hypothesis cannot be false if the premise is true.

**Here.** Entailment is the instrument behind the trade at the operating
point: the gate removes 59 wrong answers and
costs 1 correct answer under the
entailment test.

### Natural language inference

**Plain.** A task where the model is given two statements and has to say
whether the first one follows from the second.

**Technical.** A classification task over pairs of premises and hypotheses,
with the labels entailment, neutral and contradiction, in which a model
learns the semantic relation between them.

**Here.** It is one of the two branches of the contradiction gate, and it is
what supplies the "against reader labels" half of that gate's measurement.

### Contradiction

**Plain.** Two sources in the corpus that say opposite things.

**Technical.** A pair of passages whose content is mutually inconsistent, in
the sense that they cannot both be true of the world at the same time.

**Here.** The detector raised 20 labelled alarms and
none was confirmed, with a 95 percent upper bound of
16.1% on the true precision. The finding is that the
corpus does not hold the phenomenon, not that the detector is broken.

### Conflict

**Plain.** The same as a contradiction, but where the type of the disagreement
is known: a changed limit, a superseded requirement, a different scope.

**Technical.** A knowledge conflict in which the relation between the
conflicting statements is classified, for example as temporal, numeric,
scope or editorial.

**Here.** The industrial corpus is read at two past dates so that the same
provision at two issues *is* a conflict whose type is known by construction,
which is why the measurement there needed no annotation.

### Topical similarity

**Plain.** Two passages are about the same subject.

**Technical.** The degree to which two passages concern the same subject
matter, usually computed from shared vocabulary or from embedding proximity.

**Here.** It is the other branch of the contradiction gate, and it is the
branch that is too weak to carry the decision on its own: a topical check
finds passages that are about the same thing, which is not the same as
finding passages that disagree.

### Groundedness

**Plain.** How much of the answer actually comes from the passages.

**Technical.** The degree to which the claims of a generated answer are
supported by the retrieved context, measured by an entailment model or by
human judgement.

**Here.** Groundedness is what the claim scorer estimates, claim by claim,
and what the per-claim band reports.

### Per-claim band

**Plain.** A traffic light on every sentence of the answer: supported,
partly supported, or not supported.

**Technical.** A three-band categorical confidence label assigned to each
extracted claim, derived from the scores of the entailment and topical
checks together with a confidence measure.

**Here.** It is the fifth mechanism, and finding F13 is about it: most
unattributed error comes from the evidence given rather than the logic,
0.118 against 0.542.

### Three-band confidence

**Plain.** Three levels rather than a number, because a number implies a
precision the model does not have.

**Technical.** A categorical confidence scheme mapping a continuous score
onto a small number of ordered levels, chosen so that the levels correspond
to decisions a reader can act on.

**Here.** The bands are the deliverable a practitioner reads: the point of
the banding is that the reader is told what to do, not merely what the
system believes.

### Evidence trail

**Plain.** The path from the answer back to the page it came from.

**Technical.** The chain of citations linking each claim of a generated answer
to the retrieved units that support it, so that a reader can verify the claim
without trusting the generator.

**Here.** It is the property the whole framework exists to restore. It is
what distinguishes a grounded answer from a fluent one, and it is why every
claim carries a citation.

# Part 5. The gate, and the statistics of deciding

### Confidence

**Plain.** How sure the system is that it can answer.

**Technical.** A score attached to a prediction, intended to be comparable
with a probability. Confidence is only meaningful relative to a calibration
procedure; an uncalibrated confidence score is a number.

**Here.** The gate's confidence is a calibrated probability of the answer
being present in the retrieved context, not a measure of how fluent the
answer would be.

### Calibration

**Plain.** Making sure that when the system says it is 80 percent sure, it is
right about eight times out of ten.

**Technical.** The property of a predictor that its output probabilities
match the observed frequencies of the outcomes, measured by a calibration
error such as the expected calibration error or the Brier score.

**Here.** The gate's calibration error is 0.1044, and it is reported
rather than improved by refitting, because a calibration error that is not
reported cannot be checked.

### Platt scaling

**Plain.** Turning a set of numbers into a probability, by fitting a simple
sigmoid to them.

**Technical.** A method for converting the scores of a classifier into
probabilities, by fitting a logistic regression on the scores, optionally with
a scaling factor, and regularising its slope so that it behaves sensibly on
an unbalanced problem.

**Here.** The gate is Platt scaling on a five-dimensional feature vector,
fitted by maximum likelihood on 60 percent of the queries. It is one
parameter family on purpose: it can be calibrated and audited.

### Feature vector

**Plain.** The list of numbers the gate looks at.

**Technical.** The vector of query-level statistics handed to the classifier.
Its dimensionality and its individual content determine what the model can
and cannot detect.

**Here.** Five statistics of the candidate pool: the top reranker score, the
mean reranker score, the top BM25 score, the best fused score, and the number
of chunks above the reranker's own relevance bar.

### Query-level gate

**Plain.** A gate that judges the whole search at once, rather than judging
each passage.

**Technical.** A gate whose decision is a function of aggregate statistics of
the retrieved set rather than of any individual retrieved unit. It cannot
localise the answer, but it is not gameable by the presence of one
confidently wrong passage.

**Here.** Every feature describes the pool rather than a chunk, and that is
what removes the degenerate chunk-level solution, where the score is high
whenever the question looks familiar whether or not the answer is there.

### Threshold

**Plain.** The line the score has to cross before the system answers.

**Technical.** The decision boundary of a binary classifier, expressed on the
score scale. Its value is a choice, and saying where it came from is part of
the result.

**Here.** The threshold is 0.05, chosen by a rule stated in
advance: the highest that still answers at least 90 percent of the answerable
questions.

### Operating point

**Plain.** The particular threshold the system ships with, together with what
it costs and what it buys.

**Technical.** A specific choice on the risk-coverage curve, fixing the
trade-off between the risk of answering without evidence and the loss of
coverage from refusing.

**Here.** At the fitted point the coverage is 0.693 and the
abstention precision is 0.963.

### Coverage

**Plain.** The share of questions the system answers rather than refusing.

**Technical.** The proportion of the query set on which the selective
predictor emits a prediction, as opposed to abstaining. Coverage and risk
together determine the shape of the risk-coverage curve.

**Here.** The fitted point covers 0.693 of the queries.

### Abstention

**Plain.** Saying "I do not have the evidence" instead of answering.

**Technical.** The withholding of a prediction by a selective predictor,
where the decision is governed by a calibrated confidence threshold. In the
conformal literature abstention carries a guarantee: with the threshold set
at a stated level, the probability that an emitted prediction is wrong is
bounded.

**Here.** The gate abstains without a model call, so a refusal costs a
fraction of an answer.

### Abstention precision

**Plain.** Of the times the system refused, how often it was right to refuse.

**Technical.** The proportion of abstentions that are correct, that is, the
cases in which the withheld answer would indeed have been wrong.

**Here.** It is 0.963 at the fitted operating point, and
it is the precision claim that the whole slide 18 rests on.

### Selective prediction

**Plain.** The system decides when to answer and when to keep quiet, and the
decision is measured rather than assumed.

**Technical.** A framework in which a model abstains on the inputs it cannot
answer, and the quality of that decision is measured on the risk-coverage
curve, with always-answer and never-answer baselines.

**Here.** The gate is evaluated as a selective-prediction policy with
risk-coverage, with the always-answer and never-answer baselines, and with
the random-escalation control as the third.

### Conformal prediction

**Plain.** A way of setting the decision line so that the promise about being
right has a stated guarantee attached to it.

**Technical.** A framework for distribution-free uncertainty quantification
that produces prediction sets or abstentions whose coverage guarantee holds
under exchangeability, without assumptions about the data distribution.

**Here.** The shape of the mechanism is taken from the conformal literature,
and the deck says so on slide 4. What is measured here is whether the
mechanism works on this corpus, which the literature does not answer.

### Risk-coverage curve

**Plain.** The picture of what you trade when you answer less: as the system
refuses more, the risk of being wrong goes down, and the curve shows the
price of each setting.

**Technical.** The curve of risk against coverage for a selective predictor,
where risk is the conditional error rate of the emitted predictions and
coverage is the fraction of inputs on which a prediction is emitted. A
steeper curve dominates a flatter one.

**Here.** Figure 3 on slide 15 is the whole curve, and the slide shows it
because a single threshold hides the shape behind it.

### Expected calibration error

**Plain.** On average, how far the system's stated confidence is from how
often it is actually right.

**Technical.** A weighted average, over confidence bins, of the absolute
difference between the mean confidence in a bin and the empirical frequency
of correct outcomes in that bin.

**Here.** The gate's expected calibration error is 0.1044.

### Brier score

**Plain.** A single number for how bad the probabilities are, counting both
over-confidence and over-caution.

**Technical.** The mean squared difference between a predicted probability
and the observed outcome, which decomposes into calibration and refinement
components.

**Here.** Not on the slides; it is in the report's derivation of the
calibration measurement, and it is the instrument to quote if the expected
calibration error is questioned as bin-dependent.

### Posterior

**Plain.** The probability after you have taken the evidence into account.

**Technical.** The probability distribution over an unknown quantity updated
by the likelihood of the observed data, as opposed to the prior distribution
before the data.

**Here.** The gate's output is a posterior over one event: that the answer is
present in the retrieved context.

### Fitted threshold and transferred threshold

**Plain.** The threshold the system was tuned with, and the same threshold
applied somewhere else.

**Technical.** A threshold selected on the data the model was fitted on, and
the same value applied to a different corpus or a different distribution. A
transferred threshold is only valid if the score distributions are
comparable.

**Here.** The transferred threshold does not transfer: the transferred arm
answered 6 of 32 answerable questions against
32 of 32 for the ungated arm. That is finding F12, and it
is why the threshold is a configuration value rather than a property of the
method.

# Part 6. The benchmark, and the audit that checks it

### Benchmark

**Plain.** The set of questions the system is tested on, with the right
answers known.

**Technical.** A dataset of queries paired with reference answers or
reference sets, used to evaluate a system against a stated protocol.

**Here.** The benchmark in this work has two halves: questions the corpus can
answer and questions it cannot, and the whole contribution on the benchmark
side is that the second half was found to be broken and was rebuilt.

### Answerable question

**Plain.** A question the documents really do answer.

**Technical.** A query for which the corpus contains a unit that answers it,
identified by construction: the question was generated from a chunk that
states its answer.

**Here.** The focus corpus carries 32 answerable questions,
and the six-category corpus 132.

### Unanswerable question

**Plain.** A question that looks answerable but that the documents do not
answer.

**Technical.** A query for which the corpus contains no answering unit, but
which is constructed to be indistinguishable in form from an answerable one,
so that the difference between the two classes is a difference in evidence
rather than in phrasing.

**Here.** The focus corpus carries 144 unanswerable
questions and the six-category corpus 144.

### Gold answer

**Plain.** The correct answer, written down, so that the system's answer can
be marked.

**Technical.** The reference answer for a question, used as the criterion for
correctness. Here it is an assertion that the entailment model can test.

**Here.** The answer labels were the half of the benchmark that was defective
and had to be repaired.

### Structural twin

**Plain.** The answerable question that looks exactly like the unanswerable
one in every way except that the corpus can answer it.

**Technical.** A paired construction in which each unanswerable question is
matched to an answerable one on the stem, the subject size, the shape markers
and the absence of shared vocabulary, so that any classifier operating on
question form alone should score at chance.

**Here.** It is what makes the audit meaningful: the twins are the reason a
question-only classifier cannot tell the two halves apart.

### Structural certificate

**Plain.** A document that shows a question really was built the way it was
supposed to be built.

**Technical.** A machine-checkable record of the structural properties
asserted for a question, checked against the generated artefact.

**Here.** 106 of 110 structural certificates pass on the focus
corpus.

### Stem

**Plain.** The fixed frame of the question, with the subject dropped in.

**Technical.** The template part of a generated question, shared across
questions so that the variable content is the subject rather than the
phrasing.

**Here.** Both classes use the same three stems, which is the first reason a
difference between them is a difference in the evidence.

### Question family

**Plain.** The kind of question it is: asking for a definition, asking for a
number, or asking for a lookup in a table.

**Technical.** The category of a question according to the information need it
expresses, recorded on the question so that rates can be reported per family
rather than only in aggregate.

**Here.** Every question carries its family, and slide 10 says so.

### Subject size

**Plain.** How big the thing the question is about is.

**Technical.** The magnitude or extent of the entity a question concerns,
matched between the two classes so that neither is systematically about larger
or smaller entities.

**Here.** Matching subject size is one of the four properties that make a
structural twin a twin.

### Shape markers

**Plain.** The little signals in the wording that give the shape of a
question away.

**Technical.** Surface features of a question, such as interrogative type,
length and syntactic form, which a classifier operating on form alone could
exploit.

**Here.** They are matched across the two classes, and the audit's job is to
show that no classifier can still use them.

### Shortcut

**Plain.** A way of solving the test without doing the work the test is
supposed to measure.

**Technical.** A spurious correlation between a task's input features and its
label, allowing a model to score well without performing the intended
capability.

**Here.** The defect in this benchmark was an identifier shortcut in the hard
stratum, which was found, reported and repaired. The defective class's
refusal rate of 91.7% is reported as the upper bound
it was, and the repaired class gives 23.6%.

### Question-only policy

**Plain.** A rule for telling the two halves of the benchmark apart using
nothing but the wording of the question.

**Technical.** A classifier operating on the question text alone, with no
retrieval, no evidence and no access to the corpus, used as an audit of
whether the benchmark's labels are separable from its input form.

**Here.** Its ROC AUC is 0.564 on the focus corpus and
0.533 on the six-category one, which is what a class with no
shortcut should look like.

### Separability

**Plain.** How easily you can tell the two halves apart.

**Technical.** The degree to which a labelling is predictable from features
other than the intended task, quantified here by the discrimination of the
question-only classifier.

**Here.** It is measured again at the level of the gate's own refusals, where
the ROC AUC is 0.608, which is a little above chance and is
reported as the finding rather than hidden.

### ROC curve

**Plain.** A picture of how well a detector sorts cases, from every possible
setting of its decision line.

**Technical.** The curve of true positive rate against false positive rate as
the decision threshold is swept over all values, with the area under it
summarising the discrimination.

**Here.** Figure 4 on slide 16 is the question-only ROC curve, and the dashed
line is chance.

### ROC AUC

**Plain.** The single number for that picture: 0.5 is a coin toss, 1.0 is
perfect.

**Technical.** The area under the receiver operating characteristic curve, a
ranking measure of a binary classifier's discrimination that is independent
of the threshold chosen.

**Here.** 0.564 and 0.533 for the question-only
audit, and 0.608 for the gate's own refusals.

### Permutation null

**Plain.** The score you would get by chance, worked out by shuffling the
labels and seeing what the classifier would score on the shuffled data.

**Technical.** A null distribution obtained by permuting the labels, which
gives the distribution of the statistic under the hypothesis that the labels
carry no information.

**Here.** The question-only classifier's score is compared against this
rather than against a fixed number, which is the correct comparison for a
small, structured benchmark.

### Hard stratum

**Plain.** The part of the unanswerable class where the question is on-topic
but the answer is not there.

**Technical.** The subset of the unanswerable class in which the question's
subject is within the corpus's domain, so that only the absence of the
specific answer distinguishes it from an answerable question. It is the
hardest stratum and the one the benchmark lives or dies on.

**Here.** The gate refuses 23.6% of it, of
110 questions, and the gap between that and the
out-of-domain stratum is the finding on slide 16.

### Out-of-domain stratum

**Plain.** The part of the unanswerable class where the question is about
something the corpus does not cover at all.

**Technical.** The subset of the unanswerable class in which the question's
subject is outside the corpus's domain entirely, so the question is
answerable-looking but recognisably foreign.

**Here.** The gate refuses 26 of 34 of them, which is a much
higher rate than on the hard stratum. The gate is good at recognising
foreign questions and weak at recognising the ones that are nearly in scope.

### Closed-book

**Plain.** Asking the model without giving it any documents.

**Technical.** Evaluation of a generator with the retrieved context removed,
so that the answer comes from the model's parameters alone. Its purpose is
diagnostic: it reveals whether a task can be solved without the evidence.

**Here.** The closed-book unanswerable rate is 0.094, and
it is in the audit because a class a model can recognise without retrieval is
measuring something other than what the benchmark claims.

### Silver standard

**Plain.** Labels that are not signed off by a person, but are good enough to
work with.

**Technical.** Annotations produced by a model or by a procedure rather than
by an expert, used where expert annotation is unavailable, and carrying a
measured agreement rate against the expert reference.

**Here.** The contradiction annotation is model-based, and it is limitation
L4: the annotators do not share a model, they are blind to the detector's
scores, they are correct on a control set, and they agreed on all
101 decisions, but they are not human readers.

### Defect and repair

**Plain.** Something was wrong with the instrument, and it was fixed and
re-measured.

**Technical.** A documented error in a measurement or labelling procedure,
the change made to correct it, and the complete re-measurement afterwards
rather than an adjustment of the original numbers.

**Here.** The benchmark's unanswerable class was rebuilt and every
measurement was taken again. The headline moved from
91.7% to 23.6%.

### Audit

**Plain.** A check of the measuring equipment, done before you trust a single
reading from it.

**Technical.** A systematic examination of a measurement procedure for
validity, including checks that the labels are not recoverable from features
other than the intended ones, and checks that the instrument behaves
correctly on a control set.

**Here.** The audit is on slide 10, and the readings it produces are the
certificate count, the shortcut detection, the two question-only ROC AUCs,
the closed-book rate and the hard-stratum refusal rate.

### Shortcut audit

**Plain.** The record of the shortcut that was found in the benchmark, and of
what was done about it.

**Technical.** A published artefact accompanying a dataset, documenting the
spurious feature that was detected in the labels, the detection procedure, the
repair, and the re-measurement.

**Here.** It ships with the benchmark. Publishing it alongside the dataset is
the point: a reader has to be able to check the claim that the class is now
clean, and that is only possible if the instrument that found the defect is
still there.

### Leakage

**Plain.** Information from the test set leaking into the training, so that
the score is flattering and wrong.

**Technical.** The contamination of a held-out set with information
available during fitting, whether through shared records, shared documents or
shared statistics.

**Here.** Two forms are guarded against: the answerable and unanswerable
classes share no word, and the gate is fitted on 60 percent of the queries
with the threshold swept on the held-out 40 percent.

# Part 7. The statistics

### Paired test

**Plain.** A test that compares two systems on the same questions, rather
than on two separate piles of questions.

**Technical.** A significance test in which the observations are differences
within units rather than measurements of two independent groups, which
removes between-unit variance from the comparison.

**Here.** Every comparison in this work is paired, because the arms answer
exactly the same questions. An unpaired test would treat the arms as
independent and throw the pairing away.

### Exact test

**Plain.** A test that works out the answer by counting every possible
arrangement, rather than by approximating.

**Technical.** A test in which the p value is computed by enumerating the
permutations of the data that are at least as extreme as the observed one,
under the null hypothesis. It makes no distributional approximation, which
matters when the counts are small.

**Here.** The McNemar test used for the generation experiment is exact, and
the counts are small enough for that to be a real difference rather than a
formality.

### McNemar's test

**Plain.** The test for two systems that answer the same questions, which
looks only at the questions where the two systems disagreed.

**Technical.** A test for the difference between two paired proportions in
which the discordant pairs alone carry information. The statistic is the
number of discordant pairs in one direction minus those in the other, and
the exact version conditions on their total.

**Here.** It is the generation-side test, and the table on slide 17 gives
the discordant counts directly: for the fitted gate against the ungated arm
on the unanswerable class, b = 60 and c = 1.

### Discordant pair

**Plain.** A question that one system answered and the other refused, or
that one refused and the other answered.

**Technical.** An observation in which two paired measurements differ in
outcome. The two cells in which both measurements agree carry no information
about the direction of the difference.

**Here.** The table reports b and c for every arm pair, so that the effect
is visible and not only the test result.

### The counts b and c

**Plain.** b is the number of questions the first system answered and the
second refused; c is the number the first refused and the second answered.

**Technical.** The two discordant cells of a two-by-two table, conventionally
ordered so that b counts the cells favouring the second condition and c
those favouring the first.

**Here.** For the fitted gate against the ungated arm, b = 60 and c = 1 on
the unanswerable class, at p < 0.001.

### Wilcoxon signed-rank test

**Plain.** A test that compares two systems on the same questions and takes
into account how big the differences are as well as how often they go each
way.

**Technical.** A non-parametric test for the difference between two paired
samples, in which the differences are ranked by absolute magnitude and the
test is on the signed rank sum. It assumes symmetry of the difference
distribution and does not assume normality of the values.

**Here.** It is the retrieval-side test, applied to every comparison of the
seven configurations, and the p values for the two headline comparisons are
0.025 and 0.014.

### Effect size

**Plain.** How big the difference is, as opposed to whether it is unlikely to
be chance.

**Technical.** A quantity expressing the magnitude of an effect in the units
of the measurement, as opposed to the evidence against the null hypothesis.
A p value answers "is it probably zero?"; an effect size answers "how big
is it?"

**Here.** Both are reported. Slide 12 gives Cohen's d and Cliff's delta
beside the p value, because a paired difference of 0.156 on 32 queries needs
both.

### Cohen's d_z

**Plain.** The difference between the two systems, expressed in units of the
spread of the differences themselves.

**Technical.** The standardised mean difference for paired samples, the mean
of the differences divided by their standard deviation. d_z = 1 means the
average difference is one standard deviation of the differences.

**Here.** It is 0.42 for BM25 against the dense leg and
0.47 for fusion against the dense leg.

### Cliff's delta

**Plain.** How often one system beats the other, head to head, on every
pair of questions.

**Technical.** A non-parametric effect size equal to the proportion of
discordant pairs in one direction minus the proportion in the other, taking
all pairwise comparisons. It is bounded between minus one and one, and
absolute values below about 0.147 are conventionally called small.

**Here.** It is 0.16 for BM25 against the dense leg, which is a small
effect, and that is why the sentence about the dense leg says "significantly
worse" rather than "much worse".

### Null result

**Plain.** The comparison found nothing, and that is a finding rather than a
failure.

**Technical.** a failure to reject the null hypothesis. It is evidence that
the effect, if any, is smaller than the design could detect, and it is not
evidence that the effect is exactly zero.

**Here.** Four results are nulls: the quota placement on three corpora, the
fusion-over-BM25 comparison, the reranker on the focus corpus, and the
contradiction gate. Each is reported as no difference established here.

### No difference established here

**Plain.** The wording used instead of "no difference".

**Technical.** The standard reading of a null result at a given sample size:
the confidence interval for the effect includes zero, and the study was not
powered to exclude effects smaller than its resolution. It is a statement
about what this study could show, not about the world.

**Here.** It is how limitation L5 is worded on slide 23, and it is the phrase
to use if a panel presses on any of the four nulls.

### p value

**Plain.** How surprising the result would be if there were nothing going on.

**Technical.** The probability, under the null hypothesis, of observing a
statistic at least as extreme as the one obtained. It is not the probability
that the null is true and it is not the probability that the result is
correct.

**Here.** The headline p values are < 0.001 under the
answering prompt and 0.002 under the cautious one.

### Significance

**Plain.** Unlikely enough to be worth believing.

**Technical.** A result is conventionally called significant when its p value
falls below a pre-set threshold, usually 0.05. The threshold is a convention
about evidence, not about truth.

**Here.** The comparisons that carry the claims are the ones the protocol
named in advance: one per class per arm pair.

### Power

**Plain.** How likely the study is to find a difference if there is one.

**Technical.** The probability of rejecting the null hypothesis when a
specified alternative is true, which depends on the sample size, the effect
size and the threshold.

**Here.** It is the reason the nulls are read as nulls. The quota-placement
and fusion-over-BM25 comparisons are nulls at this sample size, and item 5 of
the future-work list is a pre-registered power analysis for exactly this
reason.

### Multiple comparisons

**Plain.** Looking at a lot of things and finding that one of them looks
significant by chance.

**Technical.** The inflation of the family-wise error rate when several
hypotheses are tested against the same data, and the corrections or
pre-specified primary endpoints used to control it.

**Here.** The exploratory comparisons are reported as configuration findings
and nulls rather than as claims, so no correction is applied to them either.

### Wilson interval

**Plain.** A sensible range for a proportion, which behaves properly when the
proportion is near zero or one.

**Technical.** A score interval for a binomial proportion computed from the
Wilson score statistic, which stays inside the unit interval and is well
behaved at extreme proportions where the normal approximation is not.

**Here.** Proportions in this work carry Wilson intervals, and it is the
Wilson interval that gives the contradiction gate's 95 percent upper bound of
16.1% on a precision of 0.0%.

### Bootstrap

**Plain.** Working out the uncertainty by resampling the data with
replacement, many times.

**Technical.** A resampling method that approximates the sampling
distribution of a statistic by drawing many resamples with replacement and
recomputing the statistic on each, with the spread of the results giving the
uncertainty.

**Here.** The bootstrap widths are reported next to the point estimates, as
the protocol note on slide 11 says.

### Proportion and rate

**Plain.** The share of something, and the same thing expressed per unit.

**Technical.** A proportion is a count divided by a denominator; a rate is a
count divided by an exposure. The two are not interchangeable, and a rate
without its denominator is not a measurement.

**Here.** Both are used and both are labelled: the rate of answering
unanswerable questions is a proportion over the class, and the abstention
precision is a proportion over the refusals.

### Refusal precision

**Plain.** Of the times the system refused, how often the answer really was
not there.

**Technical.** The proportion of abstentions that are correct, which is the
precision of the abstaining decision and the quantity that the risk-coverage
curve reports at each coverage.

**Here.** 0.963 at the fitted operating point. It is
the number that the random-escalation control exists to isolate, and slide 18
is built on the difference between it and the control's.

# Part 8. The machinery and the experiment

### Pipeline

**Plain.** The fixed order in which the work is done.

**Technical.** A sequence of processing stages in which each stage consumes
the output of the previous one. A pipeline is a control-flow decision: the
only way to reach a later stage is through the earlier ones.

**Here.** Five stages, and stage 3 is the gate. It is a pipeline in the
strong sense, not a set of components that can be rearranged.

### Stage

**Plain.** One step of the pipeline.

**Technical.** A unit of processing in a pipeline with a defined input, a
defined output and a defined place in the control flow.

**Here.** Stage 0 validates the query form and stage 3 is the confidence
gate. Those two are the stages that may refuse, and the table on slide 6
marks them.

### Arm

**Plain.** One version of the system being compared against the others.

**Technical.** A configuration of the system under test, differing from the
others in one controlled respect, and evaluated on the same questions.

**Here.** Five arms on slide 17: the ungated arm, the fitted gate, the random
control, the transferred threshold and the long-context arm.

### Ablation

**Plain.** Taking the system apart a piece at a time to see what each piece
was doing.

**Technical.** A controlled comparison in which one component is added or
removed at a time while everything else is held fixed, so that the effect of
that component is isolated.

**Here.** The seven retrieval configurations on slide 12 are an ablation, in
the order the components were added.

### Baseline

**Plain.** The thing you are compared against.

**Technical.** A reference configuration providing the reference point for a
comparison, either the simplest working configuration or the state of the
art against which a method is claimed to improve.

**Here.** The baseline is BM25 alone: Recall@10 0.969, the strongest of the
seven configurations on the focus corpus, and the reason the retrieval claim
is narrow.

### Control

**Plain.** A comparison built to make sure the effect you found came from the
thing you changed and not from something else.

**Technical.** A configuration that differs from the treatment in a way known
not to carry the mechanism under test, so that a difference between them
isolates the mechanism.

**Here.** The random-escalation control refuses at random with the same
frequency. It answers unanswerable questions at 0.604
against the fitted gate's 0.528, and it refuses
11 answerable questions against the gate's
2. That comparison is the whole result.

### Evaluation arm

**Plain.** The version of the system whose numbers you report.

**Technical.** The configuration whose performance is the measurement of
interest, as opposed to configurations used as comparators.

**Here.** The fitted arm, at the threshold the stated rule selects.

### Non-bypassable

**Plain.** The system cannot answer without going through the check.

**Technical.** A property of the control flow in which the guarded component
is on every path to the output, so that no configuration of the inputs can
reach the output without passing the guard.

**Here.** The generator is called at exactly one line, after the gate has
accepted, so a refused query costs no model call at all. The only two paths
that skip the gate are the comparison arms, and both are reported as
separate results.

### Held-out half

**Plain.** The half of the questions kept back and not looked at while the
system was being built.

**Technical.** The evaluation partition, excluded from model fitting and from
threshold selection, used once at the end.

**Here.** The gate is fitted on 60 percent of the queries, and the threshold
sweep reported on slide 15 is on the remaining 40 percent.

### Calibration split

**Plain.** The part of the data used to turn the system's score into an
honest probability.

**Technical.** The partition on which the calibration mapping is estimated,
kept separate from the evaluation partition so that the calibration error
reported is out of sample.

**Here.** The calibration split's mean and deviation standardise the feature
vector, which is why the table on slide 7 names them.

### Seed

**Plain.** The number that makes a run repeatable.

**Technical.** The initial value of the random number generator, fixing the
random draws so that a run can be reproduced exactly.

**Here.** Every archived result file records the seed it was run with, which
is one of the things that makes the results checkable rather than merely
reported.

### Archived result file

**Plain.** The saved output of a run, kept so that anyone can check the
numbers later.

**Technical.** The persisted JSON of an experiment, holding the configuration,
the seed, the per-query records and the computed statistics, sufficient to
recompute every number reported without re-running the experiment.

**Here.** Every figure in the deck comes from one of these. That is the
sentence to say if a panel asks whether the numbers can be checked.

### Reproducibility

**Plain.** Being able to get the same numbers again.

**Technical.** The property that a result can be regenerated from a stated
configuration, code and seed, and that the regenerated result agrees with the
archived one.

**Here.** The build regenerates every deliverable from the archived result
files, and the checkers read the numbers back off the built artefacts, so a
drift between a report and a slide stops the build rather than reaching a
PDF.

### Instrument

**Plain.** The thing that does the measuring. It can be wrong.

**Technical.** Any device, procedure or model whose output is treated as a
measurement. The methodological point is that an instrument has to be audited
before its readings are trusted, exactly as a gauge has to be calibrated
before it is read.

**Here.** The two instruments that failed were the benchmark's own labelling
procedure and the contradiction annotation, and finding that out is what
changed the headline from 91.7% to
23.6%.

### Claim annotation

**Plain.** Marking every sentence of the answer with what supports it.

**Technical.** The process of extracting the claims of a generated answer and
assigning each a support status, a confidence band and a citation.

**Here.** The per-claim band and the claim scorer's error profile are the
fifth mechanism and finding F13, which says that most unattributed error
comes from the evidence given rather than from the logic:
0.118 against 0.542.

### Empty completion

**Plain.** The model returned nothing at all.

**Technical.** A generation that terminates without producing any text,
which is distinct from a refusal: a refusal is a decision, and an empty
completion is the absence of one.

**Here.** The second generator returned an empty completion on
24 of the 66 questions,
which is why the replication could not be run. It is finding F14, and it is
the reason an empty completion is counted as a third outcome rather than
folded into refusal.

# Part 9. How long it takes

The words a panel member uses when the question is about the system running
rather than the system being right.

### Latency

**Plain.** How long you wait.

**Technical.** The elapsed time between a request being made and the
corresponding response being complete. It is a distribution, not a number,
and a latency claim without a distribution is not a measurement.

**Here.** The retrieval path is 124 milliseconds on average
over the 176 focus-corpus queries, 158 at the
median and 166 at the 95th percentile.

### Response time

**Plain.** The whole time from asking a question to getting the answer.

**Technical.** The end-to-end elapsed time for one query, from the request
arriving to the response being returned, which includes every stage the
request passes through and, if the request is answered, the generation.

**Here.** A refused query returns in 0.12 seconds, and an
answered one in the sum of that and the generation, which is between
4.2 and 13.6 seconds.

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

**Here.** The retrieval path's median is 158 milliseconds,
against a mean of 124.

### A percentile

**Plain.** The value below which a given share of the measurements fall.

**Technical.** The value under which a stated proportion of the observations
lie, usually taken as the nearest-rank value of the ordered sample. The 95th
percentile is the one quoted in a service commitment.

**Here.** The 95th percentile of the retrieval path is
166 milliseconds, and the slowest query in the run took
190.

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

**Here.** The cross-encoder rerank is 122 of the
124 milliseconds of the retrieval path. The query embedding
is 0.8, the dense leg 0.7 and the lexical leg
0.1, and the rank fusion, the modality quota and the gate
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
refused query costs the same 0.12 seconds of retrieval and
then stops. What a refusal saves is the generation, because the model is
never called. On the focus benchmark the gate refused
60 of the 176 queries.

### An upper bound

**Plain.** A number that is definitely too big, so the true value is smaller.

**Technical.** A quantity known to be at least as large as the quantity of
interest, derived by including work that the user does not actually wait for.

**Here.** The generation figure, between 4.2 and
13.6 seconds per answered query, is an upper bound,
because the archived arm totals also carry the offline claim-scoring pass
that a user never waits for.

---

# Part 10. One page of cheat sheet

| If they ask about | the word is | and the number is |
|---|---|---|
| the data | corpus | 735 chunks, 14 documents, 176 queries |
| the search | BM25, dense retrieval, RRF, a cross-encoder | Recall@10 0.969 for BM25 alone |
| the check | the confidence gate | threshold 0.05, coverage 0.693, abstention precision 0.963 |
| the headline | the rate of answering unanswerable questions | 0.938 down to 0.528, p < 0.001 |
| the control | the random-escalation arm | answers 0.604, refuses 11 answerable |
| what the score buys | refusal precision | 2 against 11, and 59 wrong answers removed for 1 |
| the benchmark | the audit | 106 of 110 certificates, ROC AUC 0.564 and 0.533 |
| the repair | the shortcut | 91.7% before, 23.6% after |
| the failure | the contradiction gate | 0.0% precision, upper bound 16.1%, 101 of 101 annotator agreement |
| the limit | the transfer | 6 of 32 answerable answered against 32 of 32 |
| the gap | one generator | no text on 24 of 66 |
| the cost | long context | 74 times the tokens, 58.8 times the cost |
| the speed | the retrieval path | 124 ms mean, 158 median, 166 at the 95th percentile |
| a refusal | the gate's decision | 0.12 s, and no model call at all |
| an answer | the generation | 4.2 to 13.6 s, of which the framework is 0.12 s |
