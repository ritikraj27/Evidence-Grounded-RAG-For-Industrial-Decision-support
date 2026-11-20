# Part 4. The generator and the answer

### Generator

**Plain.** The part that writes the answer.

**Technical.** The model that conditions on a prompt and produces text. It is
a conditional distribution over the next token, sampled repeatedly.

**Here.** One generator is tested. A second could not be, because it returned
no text on {{GENCOMP_FAILING_EMPTY_N}} of the {{GENCOMP_FAILING_EMPTY_TOTAL}}
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

**Here.** The focus corpus is {{LC_CORPUS_TOKENS}} tokens against a pipeline
context of {{LC_RAG_TOKENS}}, which is {{GEN_LC_TOKEN_RATIO}} times the
tokens. The cost ratio is {{GEN_LC_COST_RATIO}} times, because
{{GEN_LC_CACHE_HIT}} of the requests were served as a cache read.

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
point: the gate removes {{TRADE_ANSWERING_WRONG_REMOVED}} wrong answers and
costs {{TRADE_ANSWERING_CORRECT_COST_NLI}} correct answer under the
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

**Here.** The detector raised {{CONTRA_PRECISION_N}} labelled alarms and
none was confirmed, with a 95 percent upper bound of
{{CONTRA_PRECISION_CI_HI}} on the true precision. The finding is that the
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
{{RO5_RETRIEVED_GROUNDED_ERROR}} against {{RO5_GOLD_GROUNDED_ERROR}}.

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
