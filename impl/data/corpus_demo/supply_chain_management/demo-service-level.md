<!-- category: supply_chain_management -->
# Demo service level and forecasting

A second scratch document for trying the pipeline on your own data. It is not
part of any measurement in the thesis.

## Service level

The service level is the probability of fulfilling a demand from stock on
hand. It is set as a target rather than a consequence: a higher target costs
more in average inventory.

| Service level target | Cycle service level | Required stock (units) |
| --- | --- | --- |
| 90% | 0.90 | 60 |
| 95% | 0.95 | 95 |
| 97.5% | 0.975 | 130 |
| 99% | 0.99 | 175 |

## Forecast error

Forecast error is the difference between the forecast and the demand that
actually occurred. Mean absolute error is the average of those differences in
absolute terms, which makes it interpretable in the units of the forecast
itself.

| Method | Mean absolute error (units) | Bias (units) |
| --- | --- | --- |
| Naive | 41.2 | 3.8 |
| Moving average (7 days) | 33.5 | 1.1 |
| Exponential smoothing | 28.9 | -0.4 |
| Seasonal naive | 25.1 | -0.9 |

A biased forecast is one whose errors all lean the same way. Bias is worth
tracking separately because a biased forecast can be corrected by a shift
while an unbiased one cannot.

## Safety stock formula

Safety stock equals the demand during lead time multiplied by a service
factor:

    safety stock = demand per day x lead time in days x service factor

The service factor for a 95% service level is approximately 1.65, for a 90%
level approximately 1.28, and for a 99% level approximately 2.33.
