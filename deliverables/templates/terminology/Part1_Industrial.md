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

**Here.** The federal regulatory corpus is {{IND_N_CHUNKS}} chunks from
{{IND_N_DOCUMENTS}} documents spanning {{IND_N_REGIMES}} regimes, read from
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

**Here.** The regulatory corpus is organised into {{IND_N_REGIMES}} regimes, so
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
