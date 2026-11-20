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

**Here.** The focus corpus has {{N_FOCUS_DOCUMENTS}} documents; the
six-category corpus has {{N_DOCUMENTS}}; the industrial corpus has
{{IND_N_DOCUMENTS}}; the regulatory corpus has {{IND_N_DOCUMENTS}}.

### Chunk

**Plain.** A piece of a document, cut up so that the system can retrieve one
piece rather than a whole file.

**Technical.** A retrievable unit of evidence: a contiguous span of a
document, of bounded length, carrying metadata identifying its parent
document, its modality, its category and its position.

**Here.** Chunks average {{MEAN_WORDS}} words. The chunk is deliberately the
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

**Here.** The long-context comparison is a token comparison: {{LC_CORPUS_TOKENS}}
tokens for the whole corpus against {{LC_RAG_TOKENS}} for the accepted context.

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
six-category corpus has {{N_CATEGORIES_WORD}} categories. The category
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
fitting and the generation experiment: {{N_FOCUS_CHUNKS}} chunks from
{{N_FOCUS_DOCUMENTS}} documents, with {{N_FOCUS_QUERIES}} queries of which
{{N_FOCUS_ANSWERABLE}} are answerable.

**Here.** When a number in this talk is quoted without a corpus, this is the
corpus it came from.

### Six-category corpus

**Plain.** The corpus built to check whether the findings survive on material
from outside the one category.

**Technical.** The generalisation corpus, {{N_CHUNKS}} chunks from
{{N_DOCUMENTS}} documents spanning {{N_CATEGORIES_WORD}} categories, with
{{N_QUERIES}} queries.

**Here.** It carries the cross-category transfer study and the half of the
long-context comparison that could not be run on the focus corpus.

### Industrial corpus

**Plain.** The corpus built for the purpose, out of real regulatory
documents.

**Technical.** The InduSight industrial regulatory corpus: {{IND_N_CHUNKS}}
chunks from {{IND_N_DOCUMENTS}} United States federal regulatory documents
read through the Electronic Code of Federal Regulations, with
{{IND_N_QUERIES}} queries and {{IND_N_REGIMES}} regimes.

**Here.** It carries the candidate-pool curve, the quota trade, and the
contradiction detector's phenomenon.

### Federal regulatory corpus

**Plain.** The regulatory material the contradiction detector was pointed at.

**Technical.** The {{IND_N_REGIMES}} United States federal regimes that make
up the industrial regulatory corpus, read at two past dates so that the same
provision at two issues is a conflict whose type is known by construction.

**Here.** The contradiction detector's precision against reader labels is
{{CONTRA_PRECISION_PCT}}, on {{CONTRA_PRECISION_N}} labelled alarms, and the
finding is that the corpus does not hold the phenomenon the detector detects.
