# Evaluation dataset — provenance and reproduction

This directory is the dataset every number in the thesis was measured on.
It is self-contained: the documents, their provenance, and the benchmark
that interrogates them.

## What it is

| | |
|---|---|
| **Source** | English Wikipedia, fetched through the MediaWiki `parse` API |
| **Documents** | 46 industrial-engineering articles |
| **Chunks** | 2,383 chunks after modality-aware chunking |
| **Focus domain** | supply chain management — 14 documents, 735 chunks |
| **Benchmark** | `benchmark.json` — silver-standard questions with a deliberate unanswerable class |
| **Pre-repair benchmark** | `benchmark_pre_unanswerable_repair.json` — the benchmark before its unanswerable class was rebuilt, shipped so the audit's finding stays checkable |
| **Licence** | CC BY-SA 4.0 (text of the source articles) |
| **Exported** | 2026-11-18 |

The corpus is a **public substitute** for the primary corpus of the original
project specification (634 chunks, 24 proprietary supply-chain documents),
which cannot be redistributed. It was assembled to have the properties the
framework needs: several industrial categories, real tables and figures to
exercise the modality mechanisms, and citable provenance.

## The focus domain

The thesis focuses on a single industrial domain, **supply chain management**, because the
original specification's corpus and its practitioner scenarios were
supply-chain, and because a deep before/after demonstration in one domain is
more informative than a shallow one across six. The remaining categories are
retained for the cross-category transfer objective (RO4), which by definition
needs a subset of categories to transfer to held-out ones.

| Document | Chunks | SHA-256 |
|---|---|---|
| Economic order quantity | 45 | `937f23ecebbc…` |
| Incoterms | 74 | `e91dc51d56a5…` |
| Safety stock | 36 | `6335da97ee17…` |
| Just-in-time manufacturing | 57 | `39f9bfb541b0…` |
| Material requirements planning | 10 | `18963766647b…` |
| Bill of materials | 28 | `7abe39a54ea1…` |
| Kanban | 49 | `50f85339b838…` |
| Theory of constraints | 82 | `060d7435e761…` |
| Inventory management | 5 | `1a75bd03678f…` |
| Strategic sourcing | 28 | `454100cb160c…` |
| Third-party logistics | 46 | `1dcc73b12b7e…` |
| Logistics | 117 | `7a1fb0afa64e…` |
| Demand forecasting | 55 | `7d6b1428355d…` |
| Six Sigma | 103 | `4bb61fa4acba…` |

## Every document

`revision_id` is the upstream Wikipedia revision the article was read at.
The SHA-256 is of the exact bytes in `documents/`, which is the stronger
guarantee: an upstream article can be edited, the local copy cannot.

| Article | Category | Chunks | SHA-256 | Revision |
|---|---|---|---|---|
| Economic order quantity **(focus)** | supply_chain_management | 45 | `937f23ecebbc…` | [1371190686](https://en.wikipedia.org/wiki/Economic_order_quantity) |
| Incoterms **(focus)** | supply_chain_management | 74 | `e91dc51d56a5…` | [1383756740](https://en.wikipedia.org/wiki/Incoterms) |
| Safety stock **(focus)** | supply_chain_management | 36 | `6335da97ee17…` | [1363765886](https://en.wikipedia.org/wiki/Safety_stock) |
| Just-in-time manufacturing **(focus)** | supply_chain_management | 57 | `39f9bfb541b0…` | [1386359900](https://en.wikipedia.org/wiki/Lean_manufacturing) |
| Material requirements planning **(focus)** | supply_chain_management | 10 | `18963766647b…` | [1370351255](https://en.wikipedia.org/wiki/Material_requirements_planning) |
| Bill of materials **(focus)** | supply_chain_management | 28 | `7abe39a54ea1…` | [1370351239](https://en.wikipedia.org/wiki/Bill_of_materials) |
| Kanban **(focus)** | supply_chain_management | 49 | `50f85339b838…` | [1372576004](https://en.wikipedia.org/wiki/Kanban) |
| Theory of constraints **(focus)** | supply_chain_management | 82 | `060d7435e761…` | [1380318896](https://en.wikipedia.org/wiki/Theory_of_constraints) |
| Inventory management **(focus)** | supply_chain_management | 5 | `1a75bd03678f…` | [1380812647](https://en.wikipedia.org/wiki/Inventory_management) |
| Strategic sourcing **(focus)** | supply_chain_management | 28 | `454100cb160c…` | [1379779385](https://en.wikipedia.org/wiki/Strategic_sourcing) |
| Third-party logistics **(focus)** | supply_chain_management | 46 | `1dcc73b12b7e…` | [1384887739](https://en.wikipedia.org/wiki/Third-party_logistics) |
| Logistics **(focus)** | supply_chain_management | 117 | `7a1fb0afa64e…` | [1385819727](https://en.wikipedia.org/wiki/Logistics) |
| Demand forecasting **(focus)** | supply_chain_management | 55 | `7d6b1428355d…` | [1375725813](https://en.wikipedia.org/wiki/Demand_forecasting) |
| Six Sigma **(focus)** | supply_chain_management | 103 | `4bb61fa4acba…` | [1383079006](https://en.wikipedia.org/wiki/Six_Sigma) |
| Predictive maintenance | predictive_maintenance | 32 | `b36dcd1b94b4…` | [1384736435](https://en.wikipedia.org/wiki/Predictive_maintenance) |
| Total productive maintenance | predictive_maintenance | 23 | `42290cb669af…` | [1360890044](https://en.wikipedia.org/wiki/Total_productive_maintenance) |
| Overall equipment effectiveness | predictive_maintenance | 60 | `d5d4a5a8b888…` | [1372274508](https://en.wikipedia.org/wiki/Overall_equipment_effectiveness) |
| Root cause analysis | predictive_maintenance | 55 | `380909a2094f…` | [1384160474](https://en.wikipedia.org/wiki/Root-cause_analysis) |
| Condition monitoring | predictive_maintenance | 47 | `cc93c8857c41…` | [1361846752](https://en.wikipedia.org/wiki/Condition_monitoring) |
| Failure mode and effects analysis | predictive_maintenance | 99 | `7b1a3879101c…` | [1384956540](https://en.wikipedia.org/wiki/Failure_mode_and_effects_analysis) |
| Job shop scheduling | production_scheduling | 43 | `861aa7169395…` | [1386367621](https://en.wikipedia.org/wiki/Job-shop_scheduling) |
| Flow shop scheduling | production_scheduling | 19 | `ed8df2d2d7d5…` | [1386017446](https://en.wikipedia.org/wiki/Flow-shop_scheduling) |
| Production planning | production_scheduling | 18 | `5fab4a054aa3…` | [1374895438](https://en.wikipedia.org/wiki/Production_planning) |
| Gantt chart | production_scheduling | 37 | `011f63cba3da…` | [1379039146](https://en.wikipedia.org/wiki/Gantt_chart) |
| Lean manufacturing | production_scheduling | 57 | `8c7c4d897993…` | [1386359900](https://en.wikipedia.org/wiki/Lean_manufacturing) |
| Takt time | production_scheduling | 39 | `11634eca9131…` | [1375744934](https://en.wikipedia.org/wiki/Takt_time) |
| Line balancing | production_scheduling | 31 | `47b9d8ce27a3…` | [1354994410](https://en.wikipedia.org/wiki/Production_leveling) |
| Statistical process control | quality_engineering | 55 | `c2d4461b7abb…` | [1379841838](https://en.wikipedia.org/wiki/Statistical_process_control) |
| Control chart | quality_engineering | 60 | `ac215b4b103c…` | [1374768971](https://en.wikipedia.org/wiki/Control_chart) |
| Eight disciplines problem solving | quality_engineering | 27 | `7fb397f1733c…` | [1356602541](https://en.wikipedia.org/wiki/Eight_disciplines_problem_solving) |
| Quality control | quality_engineering | 27 | `166e9b67735f…` | [1328028707](https://en.wikipedia.org/wiki/Quality_control) |
| ISO 9001 | quality_engineering | 114 | `58a1fc3e2103…` | [1382090669](https://en.wikipedia.org/wiki/ISO_9000_family) |
| Design for manufacturability | quality_engineering | 38 | `1b27837b029a…` | [1374322160](https://en.wikipedia.org/wiki/Design_for_manufacturability) |
| Taguchi methods | quality_engineering | 41 | `73a6d423a912…` | [1375383209](https://en.wikipedia.org/wiki/Taguchi_methods) |
| Material handling | facility_layout | 41 | `3aa0e6cc1a2e…` | [1334883214](https://en.wikipedia.org/wiki/Material_handling) |
| Warehouse | facility_layout | 91 | `2f5b6de30cd5…` | [1380952537](https://en.wikipedia.org/wiki/Warehouse) |
| Plant layout | facility_layout | 16 | `410810ad0767…` | [1331886224](https://en.wikipedia.org/wiki/Plant_layout_study) |
| Queueing theory | facility_layout | 82 | `e0136ff3669c…` | [1383596220](https://en.wikipedia.org/wiki/Queueing_theory) |
| Little's law | facility_layout | 31 | `22859897a8e5…` | [1370351232](https://en.wikipedia.org/wiki/Little%27s_law) |
| Reliability engineering | reliability_engineering | 175 | `0c549e5ed770…` | [1381130775](https://en.wikipedia.org/wiki/Reliability_engineering) |
| Mean time between failures | reliability_engineering | 44 | `6c88cf3ce3b8…` | [1365344539](https://en.wikipedia.org/wiki/Mean_time_between_failures) |
| Mean time to repair | reliability_engineering | 10 | `11c8e5672909…` | [1334587485](https://en.wikipedia.org/wiki/Mean_time_to_repair) |
| Failure rate | reliability_engineering | 52 | `4f3b73838603…` | [1369999026](https://en.wikipedia.org/wiki/Failure_rate) |
| Maintainability | reliability_engineering | 19 | `56369fb6f017…` | [1369990359](https://en.wikipedia.org/wiki/Maintainability) |
| Weibull distribution | reliability_engineering | 95 | `403a1063275f…` | [1378377736](https://en.wikipedia.org/wiki/Weibull_distribution) |
| Fault tree analysis | reliability_engineering | 70 | `faf00d10aef2…` | [1376909957](https://en.wikipedia.org/wiki/Fault_tree_analysis) |

## Reproducing it

```bash
python3 impl/scripts/build_corpus.py        # re-fetch the documents
python3 impl/scripts/build_benchmark.py      # regenerate the questions
python3 impl/scripts/build_index.py          # build the retrieval index
```

`impl/scripts/build_corpus.py` is deterministic in its output given the
upstream revisions recorded above, and it fails loudly if a title cannot be
fetched rather than silently dropping a document.

## Attribution

The article texts are from Wikipedia and are licensed under
**CC BY-SA 4.0**. Wikipedia content is contributed by its users under that
licence, and the per-document attribution belongs to those contributors; the
revision identifiers above identify exactly which revision was used, which is
the attribution the licence asks for.

## Known limitations

- These are encyclopedia articles, not the operating manuals, standard
  operating procedures and supplier specifications of a real plant. They are
  *industrial in subject matter*, not *operationally binding*.
- Silver-standard labels are derived mechanically from the document, so
  absolute recall is optimistic. The comparisons between systems are not
  affected, because every system is scored against identical labels.
- The corpus is small relative to production corpora, which is why the
  results are framed as mechanism characterisation rather than generalisation.
