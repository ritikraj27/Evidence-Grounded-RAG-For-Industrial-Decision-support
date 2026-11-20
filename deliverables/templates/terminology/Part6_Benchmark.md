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

**Here.** The focus corpus carries {{CASE_N_ANSWERABLE}} answerable questions,
and the six-category corpus {{MC_N_ANSWERABLE}}.

### Unanswerable question

**Plain.** A question that looks answerable but that the documents do not
answer.

**Technical.** A query for which the corpus contains no answering unit, but
which is constructed to be indistinguishable in form from an answerable one,
so that the difference between the two classes is a difference in evidence
rather than in phrasing.

**Here.** The focus corpus carries {{CASE_N_UNANSWERABLE}} unanswerable
questions and the six-category corpus {{MC_N_UNANSWERABLE}}.

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

**Here.** {{UNANS_MATCH_RATE}} structural certificates pass on the focus
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
refusal rate of {{UNANS_BEFORE_REFUSED_PCT}} is reported as the upper bound
it was, and the repaired class gives {{UNANS_HARD_REFUSED_PCT}}.

### Question-only policy

**Plain.** A rule for telling the two halves of the benchmark apart using
nothing but the wording of the question.

**Technical.** A classifier operating on the question text alone, with no
retrieval, no evidence and no access to the corpus, used as an audit of
whether the benchmark's labels are separable from its input form.

**Here.** Its ROC AUC is {{UNANS_POLICY_AUC}} on the focus corpus and
{{UNANS_MC_SEP_AUC}} on the six-category one, which is what a class with no
shortcut should look like.

### Separability

**Plain.** How easily you can tell the two halves apart.

**Technical.** The degree to which a labelling is predictable from features
other than the intended task, quantified here by the discrimination of the
question-only classifier.

**Here.** It is measured again at the level of the gate's own refusals, where
the ROC AUC is {{UNANS_SEP_AUC}}, which is a little above chance and is
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

**Here.** {{UNANS_POLICY_AUC}} and {{UNANS_MC_SEP_AUC}} for the question-only
audit, and {{UNANS_SEP_AUC}} for the gate's own refusals.

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

**Here.** The gate refuses {{UNANS_HARD_REFUSED_PCT}} of it, of
{{UNANS_HARD_N}} questions, and the gap between that and the
out-of-domain stratum is the finding on slide 16.

### Out-of-domain stratum

**Plain.** The part of the unanswerable class where the question is about
something the corpus does not cover at all.

**Technical.** The subset of the unanswerable class in which the question's
subject is outside the corpus's domain entirely, so the question is
answerable-looking but recognisably foreign.

**Here.** The gate refuses {{UNANS_OOD_REFUSED_N}} of them, which is a much
higher rate than on the hard stratum. The gate is good at recognising
foreign questions and weak at recognising the ones that are nearly in scope.

### Closed-book

**Plain.** Asking the model without giving it any documents.

**Technical.** Evaluation of a generator with the retrieved context removed,
so that the answer comes from the model's parameters alone. Its purpose is
diagnostic: it reveals whether a task can be solved without the evidence.

**Here.** The closed-book unanswerable rate is {{UNANS_CLOSED_BOOK_ACC}}, and
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
{{CONTRA_PRECISION_AGREE_N}} decisions, but they are not human readers.

### Defect and repair

**Plain.** Something was wrong with the instrument, and it was fixed and
re-measured.

**Technical.** A documented error in a measurement or labelling procedure,
the change made to correct it, and the complete re-measurement afterwards
rather than an adjustment of the original numbers.

**Here.** The benchmark's unanswerable class was rebuilt and every
measurement was taken again. The headline moved from
{{UNANS_BEFORE_REFUSED_PCT}} to {{UNANS_HARD_REFUSED_PCT}}.

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
