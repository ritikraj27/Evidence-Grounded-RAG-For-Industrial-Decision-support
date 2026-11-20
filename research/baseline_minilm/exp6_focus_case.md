# Focus-domain case study — before and after, in full

Focus domain: **supply_chain_management**. 33 answerable questions and 144 deliberately unanswerable ones.

## The aggregate before/after

| | Plain BM25 retriever | The full framework |
|---|---|---|
| Answerable questions answered | 33 | 30 |
| Unanswerable questions answered (wrongly) | **144** | **24** |
| Gate refusal rate on answerable questions | 0.0% | 9.1% |
| Gate refusal rate on unanswerable questions | 0.0% | 83.3% |
| Context contains the gold chunk (answerable questions) | 97.0% | 84.8% |
| Mean chunks in the accepted context | — | 9.1 |

**This is the before/after that matters.** A retriever that never refuses answers every unanswerable question, and every one of those is a wrong answer dressed as a right one. The framework's cost is the answerable questions it declines; its benefit is the unanswerable ones it stops answering. Note that the framework is *not* better at putting the gold chunk in the context -- on silver-standard labels a plain lexical retriever already does that -- and that is the point: the gate is not there to retrieve better, it is there to refuse.

## Per-question before and after

| Question | Family | BM25-only found gold (top-10) | Full framework accepted gold | Gate decision |
|---|---|---|---|---|
| According to the table in the source document, what is the Perso… | table_lookup | yes | yes | answered |
| What is an RFID tag? | definition | yes | yes | answered |
| What is the constraint? | definition | yes | yes | answered |
| What is inbound logistics? | definition | yes | yes | answered |
| What are kanban cards? | definition | yes | no | answered |
| According to the table in the source document, what is the DPMO … | table_lookup | yes | yes | answered |
| What value is stated for describe four categories in the source … | numeric_fact | yes | no | REFUSED |
| What is the drum? | definition | yes | yes | answered |
| What is a prominent example? | definition | yes | yes | answered |
| What is freight transportation? | definition | yes | yes | answered |
| What is the rope? | definition | yes | yes | answered |
| What value is stated for the purpose in the source documentation… | numeric_fact | yes | yes | answered |
| According to the table in the source document, what is the Greel… | table_lookup | yes | yes | answered |
| What is operations research? | definition | yes | yes | answered |
| According to the table in the source document, what is the Suffi… | table_lookup | yes | yes | answered |
| What value is stated for like a survey in the source documentati… | numeric_fact | yes | no | REFUSED |
| What is the Chartered Institute? | definition | yes | yes | answered |
| What are sourcing Business Models? | definition | yes | yes | answered |
| What is outbound logistics? | definition | yes | yes | answered |
| What is the average annual variable cost? | definition | yes | yes | answered |
| What is logistics management? | definition | yes | no | answered |
| What is regression analysis? | definition | yes | yes | answered |
| What is since manufacturing in an existing plant? | definition | yes | yes | answered |
| What is safety stock? | definition | yes | yes | answered |
| According to the table in the source document, what is the Perce… | table_lookup | yes | yes | answered |
| What is the sourcing plan? | definition | yes | yes | answered |
| What value is stated for a rule of thumb in the source documenta… | numeric_fact | yes | yes | answered |
| According to the table in the source document, what is the Fort … | table_lookup | yes | yes | answered |
| What is the theory of constraints? | definition | yes | yes | answered |
| According to the table in the source document, what is the Perso… | table_lookup | yes | no | REFUSED |
| What is six Sigma? | definition | no | yes | answered |
| What value is stated for SF handled a total in the source docume… | numeric_fact | yes | yes | answered |
| What is a sourcing business model? | definition | yes | yes | answered |

## Four questions traced end to end

### A table lookup question

**Question.** According to the table in the source document, what is the Person for Taiichi Ohno?

**Before — plain BM25, top 5 of 10:**
      - `just-in-time-manufacturing::p1::tbl36` [table] **<-GOLD**: [TABLE] just-in-time-manufacturing section Key figures | Person | Contribution | | --- | --- | | W. Edwards Deming | Developed statistical quality methods; introduced mod…
      - `kanban::p1::tbl8` [table]: [TABLE] kanban section body | | | | --- | --- | | Kanban maintains inventory levels; a signal is sent to produce and deliver a new shipment as material is consumed. These…
      - `kanban::p1::t17` [text]: it is used as a demand signal that immediately travels through the supply chain. This ensures that intermediate stock held in the supply chain are better managed, and are…
      - `just-in-time-manufacturing::p1::t13` [text]: was quickly turned around so that additional materials were purchased." Toyota's Shigeo Shingo and Taiichi Ohno, building on Deming's teachings, redesigned Toyota's manuf…
      - `kanban::p1::t34` [text]: of Computer-Integrated Manufacturing. London: John Wiley. pp. 128–132. ISBN "ISBN (identifier)") 0-471-93450-X. 2. **^** "Kanban". Random House Dictionary. Dictionary.com…

**After — the full framework:**

  - fused top-10: `just-in-time-manufacturing::p1::t16`, `kanban::p1::t10`, `kanban::p1::tbl8`, `kanban::p1::t12`, `just-in-time-manufacturing::p1::tbl36` …
  - reranked top-10: `kanban::p1::t10`, `just-in-time-manufacturing::p1::tbl36`, `just-in-time-manufacturing::p1::t51`, `kanban::p1::tbl8`, `just-in-time-manufacturing::p1::t16` …
  - gate: accepted
  - top posterior: 0.1771
  - gate signals: [-0.807, -2.403, 16.316, 0.031, 0.0]
  - modality mix of the accepted context: {'text': 7, 'table': 2, 'chart': 1}

  Accepted context, first 5:
      - `kanban::p1::t10` [text]: abbreviated JIT). Taiichi Ohno, an industrial engineer at Toyota, developed kanban to improve manufacturing efficiency. The system takes its name from the cards that trac…
      - `just-in-time-manufacturing::p1::tbl36` [table] **<-GOLD**: [TABLE] just-in-time-manufacturing section Key figures | Person | Contribution | | --- | --- | | W. Edwards Deming | Developed statistical quality methods; introduced mod…
      - `just-in-time-manufacturing::p1::t51` [text]: - Ohno, Taiichi (1988). Toyota Production System: Beyond Large-Scale Production. CRC Press. ISBN "ISBN (identifier)") 978-0-915299-14-0. - Shingo, Shigeo. 1985. A Revolut…
      - `kanban::p1::tbl8` [table]: [TABLE] kanban section body | | | | --- | --- | | Kanban maintains inventory levels; a signal is sent to produce and deliver a new shipment as material is consumed. These…
      - `just-in-time-manufacturing::p1::t16` [text]: of home markets, and, above all, to broaden our opportunities in foreign markets where we must compete with the products of other industrial nations, we should welcome an…

  Contradictions surfaced:
      - `kanban::p1::t10` vs `just-in-time-manufacturing::p1::tbl36`: NLI contradiction probability 0.003 < 0.70; same-subject check failed (cos=0.337, entity Jaccard=0.000)
      - `kanban::p1::t10` vs `just-in-time-manufacturing::p1::t51`: NLI contradiction probability 0.003 < 0.70; same-subject check failed (cos=0.300, entity Jaccard=0.000)
      - `kanban::p1::t10` vs `kanban::p1::tbl8`: NLI contradiction probability 0.001 < 0.70
      - `kanban::p1::t10` vs `just-in-time-manufacturing::p1::t16`: NLI contradiction probability 0.002 < 0.70; same-subject check failed (cos=0.407, entity Jaccard=0.000)

### A numeric fact question

**Question.** What value is stated for describe four categories in the source documentation?

**Before — plain BM25, top 5 of 10:**
      - `third-party-logistics::p1::t9` [text] **<-GOLD**: Third-party logistics providers include freight forwarders, courier companies, and other companies integrating and offering subcontracted logistics and transportation ser…
      - `demand-forecasting::p1::t37` [text]: lost gross margin). - C o v e r {\displaystyle C\_{over}} !{\displaystyle C_{over}} is the cost per unit of over-forecasting (e.g., inventory holding cost). By optimizing…
      - `theory-of-constraints::p1::t19` [text]: the need of the constraint in a holistic manner. This can also be done daily in a central operations room that is accessible to everybody. ### Plant types There are four …
      - `incoterms::p1::t8` [text]: Cargo Clauses(A). Under the CIF Incoterms rule, which is reserved for use in maritime trade and is often used in commodity trading, the Institute Cargo Clauses (C) remain…
      - `incoterms::p1::t9` [text]: Incoterms 2020 are subdivided into two categories based only on method of delivery. The larger group of seven rules may be used regardless of the method of transport, wit…

**After — the full framework:**

  - fused top-10: `incoterms::p1::t8`, `just-in-time-manufacturing::p1::t24`, `logistics::p1::t47`, `third-party-logistics::p1::t9`, `six-sigma::p1::t36` …
  - reranked top-10: `third-party-logistics::p1::t9`, `just-in-time-manufacturing::p1::t24`, `incoterms::p1::t9`, `theory-of-constraints::p1::t20`, `theory-of-constraints::p1::t19` …
  - gate: REFUSED — No evidence in the indexed documentation supports an answer to this question. The retrieval-confidence gate rejected the retrieved passages (calibrated sufficiency probability 0.021 < threshold 0.150). No answer has been generated, because generating one would mean inventing it.
  - top posterior: 0.0207
  - gate signals: [-6.197, -7.191, 13.593, 0.031, 0.0]
  - modality mix of the accepted context: {'text': 7, 'table': 2, 'chart': 1}

  Accepted context, first 5:
      - (nothing accepted)

### A definition question

**Question.** What is an RFID tag?

**Before — plain BM25, top 5 of 10:**
      - `logistics::p1::t85` [text] **<-GOLD**: as a sequence of black and white bars varying in width, which when read by laser is translated into a digital sequence, which according to fixed rules can be converted in…
      - `third-party-logistics::p1::t33` [text]: businesses. For example, if you are a company with unique or complex supply chain requirements, aligning a 3PL's offerings with your specific needs will be challenging. R…
      - `logistics::p1::t84` [text]: Main article: Logistics automation An automated storage and retrieval system used by both the U.S. military at March Air Reserve Base in Riverside County, California, in …
      - `theory-of-constraints::p1::t25` [text]: Drum-buffer-rope is a manufacturing execution methodology based on the fact the output of a system can only be the same as the output at the constraint of the system. Any…
      - `theory-of-constraints::p1::tbl49` [table]: [TABLE] theory-of-constraints section Thinking processes | | Sufficient thinking ("If… then") | Necessary thinking ("In order to…we must") | | --- | --- | --- | | What to…

**After — the full framework:**

  - fused top-10: `logistics::p1::t85`, `logistics::p1::t84`, `third-party-logistics::p1::t33`, `kanban::fig2`, `kanban::p1::t27` …
  - reranked top-10: `logistics::p1::t85`, `logistics::p1::t84`, `incoterms::p1::t10`, `third-party-logistics::p1::t33`, `logistics::p1::t22` …
  - gate: accepted
  - top posterior: 0.9962
  - gate signals: [9.487, -1.779, 16.359, 0.033, 1.0]
  - modality mix of the accepted context: {'text': 7, 'table': 2, 'chart': 1}

  Accepted context, first 5:
      - `logistics::p1::t85` [text] **<-GOLD**: as a sequence of black and white bars varying in width, which when read by laser is translated into a digital sequence, which according to fixed rules can be converted in…
      - `logistics::p1::t84` [text]: Main article: Logistics automation An automated storage and retrieval system used by both the U.S. military at March Air Reserve Base in Riverside County, California, in …
      - `incoterms::p1::t10` [text]: Previously, the term had been defined informally but it is now defined as the point in the transaction where "the risk of loss or damage [to the goods] passes from the se…
      - `third-party-logistics::p1::t33` [text]: businesses. For example, if you are a company with unique or complex supply chain requirements, aligning a 3PL's offerings with your specific needs will be challenging. R…
      - `logistics::p1::t22` [text]: defines logistics as "the detailed coordination of a complex operation involving many people, facilities, or supplies", and the Oxford Dictionary on-line defines it as "t…

  Contradictions surfaced:
      - `logistics::p1::t85` vs `logistics::p1::t84`: NLI contradiction probability 0.004 < 0.70; same-subject check failed (cos=0.423, entity Jaccard=0.000)
      - `logistics::p1::t85` vs `incoterms::p1::t10`: NLI contradiction probability 0.002 < 0.70; same-subject check failed (cos=0.134, entity Jaccard=0.000)
      - `logistics::p1::t85` vs `third-party-logistics::p1::t33`: NLI contradiction probability 0.000 < 0.70; same-subject check failed (cos=0.159, entity Jaccard=0.000)
      - `logistics::p1::t85` vs `logistics::p1::t22`: NLI contradiction probability 0.001 < 0.70; same-subject check failed (cos=0.189, entity Jaccard=0.000)

### A question the gate refused

**Question.** What value is stated for describe four categories in the source documentation?

**Before — plain BM25, top 5 of 10:**
      - `third-party-logistics::p1::t9` [text] **<-GOLD**: Third-party logistics providers include freight forwarders, courier companies, and other companies integrating and offering subcontracted logistics and transportation ser…
      - `demand-forecasting::p1::t37` [text]: lost gross margin). - C o v e r {\displaystyle C\_{over}} !{\displaystyle C_{over}} is the cost per unit of over-forecasting (e.g., inventory holding cost). By optimizing…
      - `theory-of-constraints::p1::t19` [text]: the need of the constraint in a holistic manner. This can also be done daily in a central operations room that is accessible to everybody. ### Plant types There are four …
      - `incoterms::p1::t8` [text]: Cargo Clauses(A). Under the CIF Incoterms rule, which is reserved for use in maritime trade and is often used in commodity trading, the Institute Cargo Clauses (C) remain…
      - `incoterms::p1::t9` [text]: Incoterms 2020 are subdivided into two categories based only on method of delivery. The larger group of seven rules may be used regardless of the method of transport, wit…

**After — the full framework:**

  - fused top-10: `incoterms::p1::t8`, `just-in-time-manufacturing::p1::t24`, `logistics::p1::t47`, `third-party-logistics::p1::t9`, `six-sigma::p1::t36` …
  - reranked top-10: `third-party-logistics::p1::t9`, `just-in-time-manufacturing::p1::t24`, `incoterms::p1::t9`, `theory-of-constraints::p1::t20`, `theory-of-constraints::p1::t19` …
  - gate: REFUSED — No evidence in the indexed documentation supports an answer to this question. The retrieval-confidence gate rejected the retrieved passages (calibrated sufficiency probability 0.021 < threshold 0.150). No answer has been generated, because generating one would mean inventing it.
  - top posterior: 0.0207
  - gate signals: [-6.197, -7.191, 13.593, 0.031, 0.0]
  - modality mix of the accepted context: {'text': 7, 'table': 2, 'chart': 1}

  Accepted context, first 5:
      - (nothing accepted)
