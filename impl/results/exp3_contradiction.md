# Experiment 3 -- Contradiction surfacing

Pairs compared: 5535; verifiable (quantity-level) conflicts: 0.

| Detector | Pairs flagged | Flag rate | Recall on verifiable conflicts | Alarms per real conflict |
|---|---|---|---|---|
| NLI only | 645 | 0.117 | nan | nan |
| NLI AND same-subject (conjunction alone) | 162 | 0.029 | nan | 162.0 |
| Joint gate (+ numeric branch) | 162 | 0.029 | 1.000 (by construction) | nan |
| Baseline: always flag | 5535 | 1.000 | 1.000 | 5535.0 |
| Baseline: never flag | 0 | 0.000 | 0.000 | 0.0 |

**The joint gate's recall on the verifiable subset is 1.000 by construction, and is therefore not evidence.** The verifiable subset is defined by the presence of a quantity-level conflict, and the numeric detector is an OR-branch of the gate.

That subset now holds 0 pair(s), down from 21 before the numeric rule was repaired, and a subset that small cannot carry a recall measurement: the joint gate's recall on it is arithmetic rather than evidence. The reason the subset collapsed is not that the conflicts stopped existing but that most of them were never conflicts. The old numeric rule keyed a number to the nearest distinctive word, so on encyclopaedic text it fired on citation years, version numbers and surnames -- "Dettmer H., 1998" against "Dettmer W., 2006", "Incoterms 2020" against "Incoterms 2010", "Retrieved 8 December 2007" against "December 1995". The reader-labelling experiment in Experiment 11 measured the damage and found that the gate's alarms were not confirmed by a reader.

**The rule was repaired, not the corpus.** A number is now a quantity only when a measurement term governs it, the numeric branch carries the same subject check as the conjunction branch, and years and hyphenated identifiers are excluded. What is left is one quantity-level disagreement in the whole corpus, and it is between two different case studies rather than between two statements about the same subject: the corpus is encyclopaedic prose about concepts, so it holds worked examples and formulae rather than instance-level data, and a quantity-conflict detector has almost nothing in it to find.

**So the gate's alarms now come from the conjunction branch, and it is the conjunction branch that the reader labels test.** The reader-labelled precision is in Experiment 11; the proxy precision/recall figures in the JSON are against an NLI-derived label and are therefore not independent of the detector.
