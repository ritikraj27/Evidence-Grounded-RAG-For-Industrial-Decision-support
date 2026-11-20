# Experiment 3 -- Contradiction surfacing

Pairs compared: 1350; verifiable (numeric) conflicts: 24.

| Detector | Pairs flagged | Flag rate | Recall on verifiable conflicts | Alarms per real conflict |
|---|---|---|---|---|
| NLI only | 91 | 0.067 | 0.833 | 3.8 |
| NLI AND same-subject (conjunction alone) | 35 | 0.026 | 0.625 | 1.5 |
| Joint gate (+ numeric branch) | 51 | 0.038 | 1.000 (by construction) | 2.1 |
| Baseline: always flag | 1350 | 1.000 | 1.000 | 56.2 |
| Baseline: never flag | 0 | 0.000 | 0.000 | 0.0 |

**The joint gate's recall on the verifiable subset is 1.000 by construction, and is therefore not evidence.** The verifiable subset is defined by the presence of a numeric conflict, and the numeric detector is an OR-branch of the gate. The informative quantity is the second row: how many of those conflicts the NLI-and-same-subject conjunction catches with the numeric branch removed, which is what the numeric branch then adds on top of.

The verifiable subset is the set of pairs that attach different values to the same distinctive quantity -- checkable by inspection and independent of the NLI model. The proxy precision/recall figures in the JSON are against an NLI-derived label and are therefore not independent of the detector.
