<!-- category: supply_chain_management -->
# Demo warehouse policy

A scratch document for trying the pipeline on your own data. It is not part
of any measurement in the thesis: the reported numbers are measured on
`data/corpus_focus` and `data/corpus`, never on this file.

## Reorder policy

Every stocked item carries a reorder point and a reorder quantity. The reorder
point is the stock level at which replenishment is triggered, and the reorder
quantity is the amount that is ordered when it is triggered.

| SKU | Description | Reorder point (units) | Reorder quantity (units) |
| --- | --- | --- | --- |
| A-104 | Hydraulic coupling | 120 | 500 |
| B-220 | Drive belt | 40 | 200 |
| C-311 | Bearing housing | 25 | 100 |
| D-402 | Roller conveyor | 15 | 60 |

The safety stock for each SKU is the difference between the reorder point and
the average daily demand multiplied by the lead time.

## Lead times

| Supplier | Lead time (days) | Incoterm |
| --- | --- | --- |
| Northwind Bearings | 12 | EXW |
| Contoso Drives | 21 | FOB |
| Fabrikam Conveyors | 30 | CIF |

Longer lead times force a larger safety stock, because more demand is
consumed during the replenishment cycle.

## Cycle counting

Cycle counting counts a subset of the stock on a rolling schedule rather than
counting every item once a year. A high-velocity item is counted weekly, a
medium-velocity item monthly, and a slow-moving item quarterly.

| Velocity class | Items | Count interval (days) |
| --- | --- | --- |
| A | 10 | 7 |
| B | 120 | 30 |
| C | 640 | 90 |
