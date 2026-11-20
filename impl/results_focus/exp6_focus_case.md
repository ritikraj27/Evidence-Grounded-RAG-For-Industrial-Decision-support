# Focus-domain case study — before and after, in full

Focus domain: **supply_chain_management**. 32 answerable questions and 144 deliberately unanswerable ones.

## The aggregate before/after

| | Plain BM25 retriever | The full framework |
|---|---|---|
| Answerable questions answered | 32 | 30 |
| Unanswerable questions answered (wrongly) | **144** | **86** |
| Gate refusal rate on answerable questions | 0.0% | 6.2% |
| Gate refusal rate on unanswerable questions | 0.0% | 40.3% |
| Context contains the gold chunk (answerable questions) | 96.9% | 93.8% |
| Mean chunks in the accepted context | — | 9.4 |

**This is the before/after that matters.** A retriever that never refuses answers every unanswerable question, and every one of those is a wrong answer dressed as a right one. The framework's cost is the answerable questions it declines; its benefit is the unanswerable ones it stops answering. Note that the framework is *not* better at putting the gold chunk in the context -- on silver-standard labels a plain lexical retriever already does that -- and that is the point: the gate is not there to retrieve better, it is there to refuse.

## Per-question before and after

| Question | Family | BM25-only found gold (top-10) | Full framework accepted gold | Gate decision |
|---|---|---|---|---|
| What is freight transportation? | definition | yes | yes | answered |
| According to the table in the source document, what is the Contr… | table_lookup | yes | yes | answered |
| What is inbound logistics? | definition | yes | yes | answered |
| What value is stated for the purpose in the source documentation… | numeric_fact | yes | no | REFUSED |
| What value is stated for SF handled a total in the source docume… | numeric_fact | yes | yes | answered |
| According to the table in the source document, what is the Suffi… | table_lookup | yes | yes | answered |
| What are kanban cards? | definition | yes | yes | answered |
| What is the rope? | definition | yes | yes | answered |
| What is outbound logistics? | definition | yes | yes | answered |
| What is regression analysis? | definition | yes | yes | answered |
| According to the table in the source document, what is the Perce… | table_lookup | yes | yes | answered |
| According to the table in the source document, what is the Suffi… | table_lookup | yes | yes | answered |
| What is the sourcing plan? | definition | yes | yes | answered |
| What is the theory of constraints? | definition | yes | yes | answered |
| What is a sourcing business model? | definition | yes | yes | answered |
| What is six Sigma? | definition | no | yes | answered |
| What is operations research? | definition | yes | yes | answered |
| According to the table in the source document, what is the Compu… | table_lookup | yes | yes | answered |
| What are sourcing Business Models? | definition | yes | yes | answered |
| What is an RFID tag? | definition | yes | yes | answered |
| What is the drum? | definition | yes | yes | answered |
| According to the table in the source document, what is the Contr… | table_lookup | yes | yes | answered |
| What is logistics management? | definition | yes | yes | answered |
| What is since manufacturing in an existing plant? | definition | yes | yes | answered |
| According to the table in the source document, what is the Greel… | table_lookup | yes | yes | answered |
| What value is stated for a rule of thumb in the source documenta… | numeric_fact | yes | no | REFUSED |
| According to the table in the source document, what is the Perce… | table_lookup | yes | yes | answered |
| What is safety stock? | definition | yes | yes | answered |
| What is a prominent example? | definition | yes | yes | answered |
| What is the constraint? | definition | yes | yes | answered |
| What is the average annual variable cost? | definition | yes | yes | answered |
| What is the Chartered Institute? | definition | yes | yes | answered |

## Four questions traced end to end

### A table lookup question

**Question.** According to the table in the source document, what is the Contribution for John Krafcik?

**Before — plain BM25, top 5 of 10:**
      - `just-in-time-manufacturing::p1::tbl36` [table] **<-GOLD**: [TABLE] just-in-time-manufacturing section Key figures | Person | Contribution | | --- | --- | | W. Edwards Deming | Developed statistical quality methods; introduced mod…
      - `kanban::p1::t18` [text]: monitoring of these rules is a never-ending task, thereby ensuring that the kanban does what is required. ### Toyota's six rules Toyota has formulated six rules for the a…
      - `just-in-time-manufacturing::p1::t18` [text]: Oregon, after 40 hours of ZIPS training, workers reduced a week's lead time at a stroke — "things ran smoother" — and ZIPS spread through operations "like an amoeba." At …
      - `theory-of-constraints::p1::tbl49` [table]: [TABLE] theory-of-constraints section Thinking processes | | Sufficient thinking ("If… then") | Necessary thinking ("In order to…we must") | | --- | --- | --- | | What to…
      - `six-sigma::p1::t69` [text]: but there is some way to go to document these empirically and clarify the causal relations.

**After — the full framework:**

  - fused top-10: `just-in-time-manufacturing::p1::t18`, `six-sigma::p1::t69`, `bill-of-materials::p1::tbl3`, `just-in-time-manufacturing::p1::tbl36`, `six-sigma::p1::tbl8` …
  - reranked top-10: `just-in-time-manufacturing::p1::tbl36`, `just-in-time-manufacturing::p1::t18`, `bill-of-materials::p1::tbl3`, `six-sigma::p1::tbl8`, `strategic-sourcing::p1::t24` …
  - gate: accepted
  - top posterior: 0.0788
  - gate signals: [-0.935, -4.614, 16.694, 0.031, 0.0]
  - modality mix of the accepted context: {'text': 4, 'table': 5, 'chart': 1}

  Accepted context, first 5:
      - `just-in-time-manufacturing::p1::tbl36` [table] **<-GOLD**: [TABLE] just-in-time-manufacturing section Key figures | Person | Contribution | | --- | --- | | W. Edwards Deming | Developed statistical quality methods; introduced mod…
      - `just-in-time-manufacturing::p1::t18` [text]: Oregon, after 40 hours of ZIPS training, workers reduced a week's lead time at a stroke — "things ran smoother" — and ZIPS spread through operations "like an amoeba." At …
      - `bill-of-materials::p1::tbl3` [table]: [TABLE] bill-of-materials section body | | | | --- | --- | | icon | This article **needs more citations**. Please help improve this article by adding citations to reliabl…
      - `six-sigma::p1::tbl8` [table]: [TABLE] six-sigma section body | | | | --- | --- | | icon | This article **needs more citations**. Please help improve this article by adding citations to reliable source…
      - `strategic-sourcing::p1::t24` [text]: (identifier)") 978-3-8350-0946-2 - Payne, Joe and Dorn, William, Managing Indirect Spend: Enhancing Profitability Through Strategic Sourcing, John Wiley & Sons, Inc., 201…

### A numeric fact question

**Question.** What value is stated for the purpose in the source documentation?

**Before — plain BM25, top 5 of 10:**
      - `six-sigma::p1::t42` [text] **<-GOLD**: would've seen a drastic decrease of proportions corresponding to a 7.5σ level. In contrast, a true 4.5σ process would have the 4.5σ level on both sides, corresponding to …
      - `logistics::p1::t34` [text]: service(s) related to the disposal of waste produced during a business's operation. - Reverse logistics denotes all operations related to the reuse of products and materi…
      - `just-in-time-manufacturing::p1::t22` [text]: Womack and Jones define Lean as "a way to do more and more with less and less—less human effort, less equipment, less time, and less space—while coming closer and closer …
      - `six-sigma::p1::t58` [text]: A Fortune "Fortune (magazine)") article stated that "of 58 large companies that have announced Six Sigma programs, 91% have trailed the S&P 500 since". The statement was …
      - `kanban::p1::t17` [text]: it is used as a demand signal that immediately travels through the supply chain. This ensures that intermediate stock held in the supply chain are better managed, and are…

**After — the full framework:**

  - fused top-10: `six-sigma::p1::t42`, `six-sigma::p1::t43`, `incoterms::fig2`, `logistics::p1::t34`, `demand-forecasting::p1::t44` …
  - reranked top-10: `six-sigma::p1::t43`, `six-sigma::p1::t42`, `logistics::p1::t34`, `just-in-time-manufacturing::p1::t22`, `six-sigma::p1::t58` …
  - gate: REFUSED — No evidence in the indexed documentation supports an answer to this question. The retrieval-confidence gate rejected the retrieved passages (calibrated sufficiency probability 0.034 < threshold 0.050). No answer has been generated, because generating one would mean inventing it.
  - top posterior: 0.0339
  - gate signals: [-7.262, -7.92, 12.392, 0.032, 0.0]
  - modality mix of the accepted context: {'text': 7, 'chart': 1, 'table': 2}

  Accepted context, first 5:
      - (nothing accepted)

### A definition question

**Question.** What is freight transportation?

**Before — plain BM25, top 5 of 10:**
      - `logistics::p1::t92` [text]: - Automated identification and data capture – Methods of automatically identifying objects by computer systemPages displaying short descriptions of redirect targets - Doc…
      - `logistics::p1::t28` [text]: Loading of a thermal oxidizer in preparation for its transport to a manufacturing plant A forklift truck loads a pallet of humanitarian aid to Pakistan on board a C-17 ai…
      - `third-party-logistics::p1::t20` [text]: quoting, financial settlement, auditing, tracking, customer service and issue resolution. However, they do not employ any truck drivers or warehouse personnel, and they d…
      - `logistics::p1::t29` [text] **<-GOLD**: technologies such as bar code scanning and computers, the availability of stocks can be checked in real time. The purpose of having an inventory is to reduce the overall …
      - `logistics::p1::t66` [text]: semi-trailers. Especially for very long distances, product transportation will likely benefit from using different transportation means: When moving cargo, typical constr…

**After — the full framework:**

  - fused top-10: `logistics::p1::t28`, `logistics::p1::t66`, `third-party-logistics::p1::t37`, `incoterms::p1::t36`, `logistics::p1::t29` …
  - reranked top-10: `logistics::p1::t29`, `incoterms::p1::t13`, `logistics::p1::t28`, `third-party-logistics::p1::t37`, `logistics::p1::t66` …
  - gate: accepted
  - top posterior: 0.2057
  - gate signals: [5.063, 3.254, 8.245, 0.032, 5.0]
  - modality mix of the accepted context: {'text': 7, 'table': 2, 'chart': 1}

  Accepted context, first 5:
      - `logistics::p1::t29` [text] **<-GOLD**: technologies such as bar code scanning and computers, the availability of stocks can be checked in real time. The purpose of having an inventory is to reduce the overall …
      - `incoterms::p1::t13` [text]: to perform or to procure the performance of transport by rail, road, air, sea, inland waterway or by a combination of such modes - Freight forwarder: A firm that makes or…
      - `logistics::p1::t28` [text]: Loading of a thermal oxidizer in preparation for its transport to a manufacturing plant A forklift truck loads a pallet of humanitarian aid to Pakistan on board a C-17 ai…
      - `third-party-logistics::p1::t37` [text]: - Freight - Shipping
      - `logistics::p1::t66` [text]: semi-trailers. Especially for very long distances, product transportation will likely benefit from using different transportation means: When moving cargo, typical constr…

### A question the gate refused

**Question.** What value is stated for the purpose in the source documentation?

**Before — plain BM25, top 5 of 10:**
      - `six-sigma::p1::t42` [text] **<-GOLD**: would've seen a drastic decrease of proportions corresponding to a 7.5σ level. In contrast, a true 4.5σ process would have the 4.5σ level on both sides, corresponding to …
      - `logistics::p1::t34` [text]: service(s) related to the disposal of waste produced during a business's operation. - Reverse logistics denotes all operations related to the reuse of products and materi…
      - `just-in-time-manufacturing::p1::t22` [text]: Womack and Jones define Lean as "a way to do more and more with less and less—less human effort, less equipment, less time, and less space—while coming closer and closer …
      - `six-sigma::p1::t58` [text]: A Fortune "Fortune (magazine)") article stated that "of 58 large companies that have announced Six Sigma programs, 91% have trailed the S&P 500 since". The statement was …
      - `kanban::p1::t17` [text]: it is used as a demand signal that immediately travels through the supply chain. This ensures that intermediate stock held in the supply chain are better managed, and are…

**After — the full framework:**

  - fused top-10: `six-sigma::p1::t42`, `six-sigma::p1::t43`, `incoterms::fig2`, `logistics::p1::t34`, `demand-forecasting::p1::t44` …
  - reranked top-10: `six-sigma::p1::t43`, `six-sigma::p1::t42`, `logistics::p1::t34`, `just-in-time-manufacturing::p1::t22`, `six-sigma::p1::t58` …
  - gate: REFUSED — No evidence in the indexed documentation supports an answer to this question. The retrieval-confidence gate rejected the retrieved passages (calibrated sufficiency probability 0.034 < threshold 0.050). No answer has been generated, because generating one would mean inventing it.
  - top posterior: 0.0339
  - gate signals: [-7.262, -7.92, 12.392, 0.032, 0.0]
  - modality mix of the accepted context: {'text': 7, 'chart': 1, 'table': 2}

  Accepted context, first 5:
      - (nothing accepted)
