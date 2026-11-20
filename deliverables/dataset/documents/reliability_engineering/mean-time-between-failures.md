<!-- category: reliability_engineering -->
# Mean time between failures

Predicted elapsed time between inherent failures of a system during operation

**Mean time between failures** (**MTBF**) is the predicted elapsed time between inherent [failures](/wiki/Failure "Failure") of a mechanical or electronic system during normal system operation. MTBF can be calculated as the [arithmetic mean](/wiki/Arithmetic_mean "Arithmetic mean") (average) time between failures of a system. The term is used for repairable systems while **mean time to failure** (**MTTF**) denotes the expected time to failure for a non-repairable system.[[1]](#cite_note-lienig-1)

The definition of MTBF depends on the definition of what is considered a failure. For complex, [repairable](/wiki/Repairable "Repairable") systems, failures are considered to be those out of design conditions which place the system out of service and into a state for repair. Failures which occur that can be left or maintained in an unrepaired condition, and do not place the system out of service, are not considered failures under this definition.[[2]](#cite_note-2) In addition, units that are taken down for routine scheduled maintenance or inventory control are not considered within the definition of failure.[[3]](#cite_note-3) The higher the MTBF, the longer a system is likely to work before failing.

## Overview

[[edit](/w/index.php?title=Mean_time_between_failures&veaction=edit&section=1 "Edit section: Overview") | [edit source](/w/index.php?title=Mean_time_between_failures&action=edit&section=1 "Edit section's source code: Overview")]

Mean time between failures (MTBF) describes the expected time between two failures for a repairable system. For example, three identical systems starting to function properly at time 0 are working until all of them fail. The first system fails after 100 hours, the second after 120 hours and the third after 130 hours. The MTBF of the systems is the average of the three failure times, which is 116.667 hours. If the systems were non-repairable, then their [MTTF](#Variations_of_MTBF) would be 116.667 hours.

In general, MTBF is the "up-time" between two failure states of a repairable system during operation as outlined here:

[![](//thumb.wikimedia.org/wikipedia/commons/thumb/9/92/Time_between_failures.svg/960px-Time_between_failures.svg.png?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail)](/wiki/File:Time_between_failures.svg)

For each observation, the "down time" is the instantaneous time it went down, which is after (i.e. greater than) the moment it went up, the "up time". The difference ("down time" minus "up time") is the amount of time it was operating between these two events.

By referring to the figure above, the MTBF of a component is the sum of the lengths of the operational periods divided by the number of observed failures:

:   MTBF
    =

    ∑

    (

    start of downtime
    −

    start of uptime
    )
    number of failures
    .
    {\displaystyle {\text{MTBF}}={\frac {\sum {({\text{start of downtime}}-{\text{start of uptime}})}}{\text{number of failures}}}.}
    ![{\displaystyle {\text{MTBF}}={\frac {\sum {({\text{start of downtime}}-{\text{start of uptime}})}}{\text{number of failures}}}.}](https://wikimedia.org/api/rest_v1/media/math/render/svg/139f9895b72e10b1323da596a51362f0c7548466)

In a similar manner, mean down time (MDT) can be defined as

:   MDT
    =

    ∑

    (

    start of uptime
    −

    start of downtime
    )
    number of failures
    .
    {\displaystyle {\text{MDT}}={\frac {\sum {({\text{start of uptime}}-{\text{start of downtime}})}}{\text{number of failures}}}.}
    ![{\displaystyle {\text{MDT}}={\frac {\sum {({\text{start of uptime}}-{\text{start of downtime}})}}{\text{number of failures}}}.}](https://wikimedia.org/api/rest_v1/media/math/render/svg/b930406132c6461e156c077db9f1c6a67c953a4b)

## Mathematical description

[[edit](/w/index.php?title=Mean_time_between_failures&veaction=edit&section=2 "Edit section: Mathematical description") | [edit source](/w/index.php?title=Mean_time_between_failures&action=edit&section=2 "Edit section's source code: Mathematical description")]

The MTBF is the [expected value](/wiki/Expected_value "Expected value") of the [random variable](/wiki/Random_variable "Random variable") 

T
{\displaystyle T}
![{\displaystyle T}](https://wikimedia.org/api/rest_v1/media/math/render/svg/ec7200acd984a1d3a3d7dc455e262fbe54f7f6e0) indicating the time until failure. Thus, it can be written as[[4]](#cite_note-birolini-4)

:   MTBF
    =

    E
    {
    T
    }
    =

    ∫

    0

    ∞
    t

    f

    T
    (
    t
    )

    d
    t
    {\displaystyle {\text{MTBF}}=\mathbb {E} \{T\}=\int \_{0}^{\infty }tf\_{T}(t)\,dt}
    ![{\displaystyle {\text{MTBF}}=\mathbb {E} \{T\}=\int _{0}^{\infty }tf_{T}(t)\,dt}](https://wikimedia.org/api/rest_v1/media/math/render/svg/db0c1f4c668eec095f22710f5a7d37d46fe4928d)

where 

f

T
(
t
)
{\displaystyle f\_{T}(t)}
![{\displaystyle f_{T}(t)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/29753bf567358f4c066ed5414c5899ed6dcad750) is the [probability density function](/wiki/Probability_density_function "Probability density function") of 

T
{\displaystyle T}
![{\displaystyle T}](https://wikimedia.org/api/rest_v1/media/math/render/svg/ec7200acd984a1d3a3d7dc455e262fbe54f7f6e0). Equivalently, the MTBF can be expressed in terms of the [reliability function](/wiki/Reliability_function "Reliability function") 

R

T
(
t
)
{\displaystyle R\_{T}(t)}
![{\displaystyle R_{T}(t)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/7904990fd1acf2d0ded346d1daecc9a5d679128d) as

:   MTBF
    =

    ∫

    0

    ∞
    R
    (
    t
    )

    d
    t
    {\displaystyle {\text{MTBF}}=\int \_{0}^{\infty }R(t)\,dt}
    ![{\displaystyle {\text{MTBF}}=\int _{0}^{\infty }R(t)\,dt}](https://wikimedia.org/api/rest_v1/media/math/render/svg/4f1fa2136352fd5d9c46562d9a9d9ec182e7fc72).

The MTBF and 

T
{\displaystyle T}
![{\displaystyle T}](https://wikimedia.org/api/rest_v1/media/math/render/svg/ec7200acd984a1d3a3d7dc455e262fbe54f7f6e0) have units of time (e.g., hours).

Any practically-relevant calculation of the MTBF assumes that the system is working within its "useful life period", which is characterized by a relatively constant [failure rate](/wiki/Failure_rate "Failure rate") (the middle part of the "[bathtub curve](/wiki/Bathtub_curve "Bathtub curve")") when only random failures are occurring.[[1]](#cite_note-lienig-1) In other words, it is assumed that the system has survived initial setup stresses and has not yet approached its expected end of life, both of which often increase the failure rate.

Assuming a constant failure rate 

λ
{\displaystyle \lambda }
![{\displaystyle \lambda }](https://wikimedia.org/api/rest_v1/media/math/render/svg/b43d0ea3c9c025af1be9128e62a18fa74bedda2a) implies that 

T
{\displaystyle T}
![{\displaystyle T}](https://wikimedia.org/api/rest_v1/media/math/render/svg/ec7200acd984a1d3a3d7dc455e262fbe54f7f6e0) has an [exponential distribution](/wiki/Exponential_distribution "Exponential distribution") with parameter 

λ
{\displaystyle \lambda }
![{\displaystyle \lambda }](https://wikimedia.org/api/rest_v1/media/math/render/svg/b43d0ea3c9c025af1be9128e62a18fa74bedda2a). Since the MTBF is the expected value of 

T
{\displaystyle T}
![{\displaystyle T}](https://wikimedia.org/api/rest_v1/media/math/render/svg/ec7200acd984a1d3a3d7dc455e262fbe54f7f6e0), it is given by the reciprocal of the failure rate of the system,[[1]](#cite_note-lienig-1)[[4]](#cite_note-birolini-4)

:   MTBF
    =

    1
    λ
    {\displaystyle {\text{MTBF}}={\frac {1}{\lambda }}}
    ![{\displaystyle {\text{MTBF}}={\frac {1}{\lambda }}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/34d9bf9e4529c82313bb6ed985b57f85e569e247).

Once the MTBF of a system is known, and assuming a constant failure rate, the [probability](/wiki/Probability "Probability") that any one particular system will be operational for a given duration can be inferred[[1]](#cite_note-lienig-1) from the [reliability function](/wiki/Reliability_function "Reliability function") of the [exponential distribution](/wiki/Exponential_distribution "Exponential distribution"), 

R

T
(
t
)
=

e

−
λ
t
{\displaystyle R\_{T}(t)=e^{-\lambda t}}
![{\displaystyle R_{T}(t)=e^{-\lambda t}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/b325a6dad87bb0fcd291f8c3a6d72ba589525bbf). In particular, the probability that a particular system will survive to its MTBF is 

1

/
e
{\displaystyle 1/e}
![{\displaystyle 1/e}](https://wikimedia.org/api/rest_v1/media/math/render/svg/f3f5e6342b5d465a51daf323f383ed1c8e51f43f), or about 37% (i.e., it will fail earlier with probability 63%).[[5]](#cite_note-5)

## Application

[[edit](/w/index.php?title=Mean_time_between_failures&veaction=edit&section=3 "Edit section: Application") | [edit source](/w/index.php?title=Mean_time_between_failures&action=edit&section=3 "Edit section's source code: Application")]

The MTBF value can be used as a system reliability parameter or to compare different systems or designs. This value should only be understood conditionally as the “mean lifetime” (an average value), and not as a quantitative identity between working and failed units.[[1]](#cite_note-lienig-1)

Since MTBF can be expressed as “average life (expectancy)”, many engineers assume that 50% of items will have failed by time *t* = MTBF. This inaccuracy can lead to bad design decisions. Furthermore, probabilistic failure prediction based on MTBF implies the total absence of systematic failures (i.e., a constant failure rate with only intrinsic, random failures), which is not easy to verify.[[4]](#cite_note-birolini-4) Assuming no systematic errors, the probability the system survives during a duration, T, is calculated as exp^(-T/MTBF). Hence the probability a system fails during a duration T, is given by 1 - exp^(-T/MTBF).

MTBF value prediction is an important element in the development of products. Reliability engineers and design engineers often use reliability software to calculate a product's MTBF according to various methods and standards (MIL-HDBK-217F, Telcordia SR332, Siemens SN 29500, FIDES, UTE 80-810 (RDF2000), etc.). The Mil-HDBK-217 reliability calculator manual in combination with RelCalc software (or other comparable tool) enables MTBF reliability rates to be predicted based on design.

A concept which is closely related to MTBF, and is important in the computations involving MTBF, is the [mean down time](/wiki/Mean_down_time "Mean down time") (MDT). MDT can be defined as mean time which the system is down after the failure. Usually, MDT is considered different from MTTR ([Mean Time To Repair](/wiki/Mean_time_to_repair "Mean time to repair")); in particular, MDT usually includes organizational and logistical factors (such as business days or waiting for components to arrive) while MTTR is usually understood as more narrow and more technical.

## Application of MTBF in manufacturing

[[edit](/w/index.php?title=Mean_time_between_failures&veaction=edit&section=4 "Edit section: Application of MTBF in manufacturing") | [edit source](/w/index.php?title=Mean_time_between_failures&action=edit&section=4 "Edit section's source code: Application of MTBF in manufacturing")]

MTBF serves as a crucial metric for managing machinery and equipment reliability. Its application is particularly significant in the context of [total productive maintenance](/wiki/Total_productive_maintenance "Total productive maintenance") (TPM), a comprehensive maintenance strategy aimed at maximizing equipment [effectiveness](/wiki/Effectiveness "Effectiveness"). MTBF provides a quantitative measure of the time elapsed between failures of a system during normal operation, offering insights into the reliability and performance of manufacturing equipment.[[6]](#cite_note-6)

By integrating MTBF with TPM principles, manufacturers can achieve a more proactive maintenance approach. This synergy allows for the identification of patterns and potential failures before they occur, enabling preventive maintenance and reducing unplanned downtime. As a result, MTBF becomes a [key performance indicator](/wiki/Performance_indicator "Performance indicator") (KPI) within TPM, guiding decisions on maintenance schedules, spare parts inventory, and ultimately, optimizing the lifespan and efficiency of machinery.[[7]](#cite_note-7) This strategic use of MTBF within TPM frameworks enhances overall production efficiency, reduces costs associated with breakdowns, and contributes to the continuous improvement of manufacturing processes.

## MTBF and MDT for networks of components

[[edit](/w/index.php?title=Mean_time_between_failures&veaction=edit&section=5 "Edit section: MTBF and MDT for networks of components") | [edit source](/w/index.php?title=Mean_time_between_failures&action=edit&section=5 "Edit section's source code: MTBF and MDT for networks of components")]

Two components 

c

1
,

c

2
{\displaystyle c\_{1},c\_{2}}
![{\displaystyle c_{1},c_{2}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/15ae7f7452e416f7b70940ca260b2582f10382cf) (for instance hard drives, servers, etc.) may be arranged in a network, in [*series* or in *parallel*](/wiki/Series_and_parallel_circuits "Series and parallel circuits"). The terminology is here used by close analogy to electrical circuits, but has a slightly different meaning. We say that the two components are in series if the failure of *either* causes the failure of the network, and that they are in parallel if only the failure of *both* causes the network to fail. The MTBF of the resulting two-component network with repairable components can be computed according to the following formulae, assuming that the MTBF of both individual components is known:[[8]](#cite_note-auroraconsultingengineering-8)[[9]](#cite_note-smith-9)

:   mtbf
    (

    c

    1
    ;

    c

    2
    )
    =

    1

    1

    mtbf
    (

    c

    1
    )
    +

    1

    mtbf
    (

    c

    2
    )
    =

    mtbf
    (

    c

    1
    )
    ×

    mtbf
    (

    c

    2
    )

    mtbf
    (

    c

    1
    )
    +

    mtbf
    (

    c

    2
    )

    ,
    {\displaystyle {\text{mtbf}}(c\_{1};c\_{2})={\frac {1}{{\frac {1}{{\text{mtbf}}(c\_{1})}}+{\frac {1}{{\text{mtbf}}(c\_{2})}}}}={\frac {{\text{mtbf}}(c\_{1})\times {\text{mtbf}}(c\_{2})}{{\text{mtbf}}(c\_{1})+{\text{mtbf}}(c\_{2})}}\;,}
    ![{\displaystyle {\text{mtbf}}(c_{1};c_{2})={\frac {1}{{\frac {1}{{\text{mtbf}}(c_{1})}}+{\frac {1}{{\text{mtbf}}(c_{2})}}}}={\frac {{\text{mtbf}}(c_{1})\times {\text{mtbf}}(c_{2})}{{\text{mtbf}}(c_{1})+{\text{mtbf}}(c_{2})}}\;,}](https://wikimedia.org/api/rest_v1/media/math/render/svg/2d8dae8fddff71e04aebf8291c6da487df8ac920)

where 

c

1
;

c

2
{\displaystyle c\_{1};c\_{2}}
![{\displaystyle c_{1};c_{2}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/2a7c07bf47ca5c643df4dcc754e8967c8f7260e7) is the network in which the components are arranged in series.

For the network containing parallel repairable components, to find out the MTBF of the whole system, in addition to component MTBFs, it is also necessary to know their respective MDTs. Then, assuming that MDTs are negligible compared to MTBFs (which usually stands in practice), the MTBF for the parallel system consisting from two parallel repairable components can be written as follows:[[8]](#cite_note-auroraconsultingengineering-8)[[9]](#cite_note-smith-9)

mtbf
(

c

1
∥

c

2
)

=

1

1

mtbf
(

c

1
)
×

PF
(

c

2
,

mdt
(

c

1
)
)
+

1

mtbf
(

c

2
)
×

PF
(

c

1
,

mdt
(

c

2
)
)

=

1

1

mtbf
(

c

1
)
×

mdt
(

c

1
)

mtbf
(

c

2
)
+

1

mtbf
(

c

2
)
×

mdt
(

c

2
)

mtbf
(

c

1
)

=

mtbf
(

c

1
)
×

mtbf
(

c

2
)

mdt
(

c

1
)
+

mdt
(

c

2
)

,
{\displaystyle {\begin{aligned}{\text{mtbf}}(c\_{1}\parallel c\_{2})&={\frac {1}{{\frac {1}{{\text{mtbf}}(c\_{1})}}\times {\text{PF}}(c\_{2},{\text{mdt}}(c\_{1}))+{\frac {1}{{\text{mtbf}}(c\_{2})}}\times {\text{PF}}(c\_{1},{\text{mdt}}(c\_{2}))}}\\[1em]&={\frac {1}{{\frac {1}{{\text{mtbf}}(c\_{1})}}\times {\frac {{\text{mdt}}(c\_{1})}{{\text{mtbf}}(c\_{2})}}+{\frac {1}{{\text{mtbf}}(c\_{2})}}\times {\frac {{\text{mdt}}(c\_{2})}{{\text{mtbf}}(c\_{1})}}}}\\[1em]&={\frac {{\text{mtbf}}(c\_{1})\times {\text{mtbf}}(c\_{2})}{{\text{mdt}}(c\_{1})+{\text{mdt}}(c\_{2})}}\;,\end{aligned}}}
![{\displaystyle {\begin{aligned}{\text{mtbf}}(c_{1}\parallel c_{2})&={\frac {1}{{\frac {1}{{\text{mtbf}}(c_{1})}}\times {\text{PF}}(c_{2},{\text{mdt}}(c_{1}))+{\frac {1}{{\text{mtbf}}(c_{2})}}\times {\text{PF}}(c_{1},{\text{mdt}}(c_{2}))}}\\[1em]&={\frac {1}{{\frac {1}{{\text{mtbf}}(c_{1})}}\times {\frac {{\text{mdt}}(c_{1})}{{\text{mtbf}}(c_{2})}}+{\frac {1}{{\text{mtbf}}(c_{2})}}\times {\frac {{\text{mdt}}(c_{2})}{{\text{mtbf}}(c_{1})}}}}\\[1em]&={\frac {{\text{mtbf}}(c_{1})\times {\text{mtbf}}(c_{2})}{{\text{mdt}}(c_{1})+{\text{mdt}}(c_{2})}}\;,\end{aligned}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/a1d2e5d033b397eff2629bd553865018dff9ca3f)

where 

c

1
∥

c

2
{\displaystyle c\_{1}\parallel c\_{2}}
![{\displaystyle c_{1}\parallel c_{2}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/d0708cf10ec3ef3267c31e7791ba898a3e800f77) is the network in which the components are arranged in parallel, and 

P
F
(
c
,
t
)
{\displaystyle PF(c,t)}
![{\displaystyle PF(c,t)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/206e68425a2322212832ffaba6ad27e13de27b02) is the probability of failure of component 

c
{\displaystyle c}
![{\displaystyle c}](https://wikimedia.org/api/rest_v1/media/math/render/svg/86a67b81c2de995bd608d5b2df50cd8cd7d92455) during "vulnerability window" 

t
{\displaystyle t}
![{\displaystyle t}](https://wikimedia.org/api/rest_v1/media/math/render/svg/65658b7b223af9e1acc877d848888ecdb4466560).

Intuitively, both these formulae can be explained from the point of view of failure probabilities. First of all, let's note that the probability of a system failing within a certain timeframe is the inverse of its MTBF. Then, when considering series of components, failure of any component leads to the failure of the whole system, so (assuming that failure probabilities are small, which is usually the case) probability of the failure of the whole system within a given interval can be approximated as a sum of failure probabilities of the components. With parallel components the situation is a bit more complicated: the whole system will fail [if and only if](/wiki/If_and_only_if "If and only if") after one of the components fails, the other component fails while the first component is being repaired; this is where MDT comes into play: the faster the first component is repaired, the less is the "vulnerability window" for the other component to fail.

Using similar logic, MDT for a system out of two serial components can be calculated as:[[8]](#cite_note-auroraconsultingengineering-8)

:   mdt
    (

    c

    1
    ;

    c

    2
    )
    =

    mtbf
    (

    c

    1
    )
    ×

    mdt
    (

    c

    2
    )
    +

    mtbf
    (

    c

    2
    )
    ×

    mdt
    (

    c

    1
    )

    mtbf
    (

    c

    1
    )
    +

    mtbf
    (

    c

    2
    )

    ,
    {\displaystyle {\text{mdt}}(c\_{1};c\_{2})={\frac {{\text{mtbf}}(c\_{1})\times {\text{mdt}}(c\_{2})+{\text{mtbf}}(c\_{2})\times {\text{mdt}}(c\_{1})}{{\text{mtbf}}(c\_{1})+{\text{mtbf}}(c\_{2})}}\;,}
    ![{\displaystyle {\text{mdt}}(c_{1};c_{2})={\frac {{\text{mtbf}}(c_{1})\times {\text{mdt}}(c_{2})+{\text{mtbf}}(c_{2})\times {\text{mdt}}(c_{1})}{{\text{mtbf}}(c_{1})+{\text{mtbf}}(c_{2})}}\;,}](https://wikimedia.org/api/rest_v1/media/math/render/svg/5e4c6297680a849c12dc1cbe6c2ff1a71b073410)

and for a system out of two parallel components MDT can be calculated as:[[8]](#cite_note-auroraconsultingengineering-8)

:   mdt
    (

    c

    1
    ∥

    c

    2
    )
    =

    mdt
    (

    c

    1
    )
    ×

    mdt
    (

    c

    2
    )

    mdt
    (

    c

    1
    )
    +

    mdt
    (

    c

    2
    )

    .
    {\displaystyle {\text{mdt}}(c\_{1}\parallel c\_{2})={\frac {{\text{mdt}}(c\_{1})\times {\text{mdt}}(c\_{2})}{{\text{mdt}}(c\_{1})+{\text{mdt}}(c\_{2})}}\;.}
    ![{\displaystyle {\text{mdt}}(c_{1}\parallel c_{2})={\frac {{\text{mdt}}(c_{1})\times {\text{mdt}}(c_{2})}{{\text{mdt}}(c_{1})+{\text{mdt}}(c_{2})}}\;.}](https://wikimedia.org/api/rest_v1/media/math/render/svg/5d38fd53f1337aad2fce0dedf1c3c56a77666087)

Through successive application of these four formulae, the MTBF and MDT of any network of repairable components can be computed, provided that the MTBF and MDT is known for each component. In a special but all-important case of several serial components, MTBF calculation can be easily generalised into

:   mtbf
    (

    c

    1
    ;
    …
    ;

    c

    n
    )
    =

    (

    ∑

    k
    =
    1

    n

    1

    mtbf
    (

    c

    k
    )
    )

    −
    1

    ,
    {\displaystyle {\text{mtbf}}(c\_{1};\dots ;c\_{n})=\left(\sum \_{k=1}^{n}{\frac {1}{{\text{mtbf}}(c\_{k})}}\right)^{-1}\;,}
    ![{\displaystyle {\text{mtbf}}(c_{1};\dots ;c_{n})=\left(\sum _{k=1}^{n}{\frac {1}{{\text{mtbf}}(c_{k})}}\right)^{-1}\;,}](https://wikimedia.org/api/rest_v1/media/math/render/svg/ab197a8acb3b8223f8814760fdf543b1fa3e5163)

which can be shown by induction,[[10]](#cite_note-10) and likewise

:   mdt
    (

    c

    1
    ∥
    ⋯
    ∥

    c

    n
    )
    =

    (

    ∑

    k
    =
    1

    n

    1

    mdt
    (

    c

    k
    )
    )

    −
    1

    ,
    {\displaystyle {\text{mdt}}(c\_{1}\parallel \dots \parallel c\_{n})=\left(\sum \_{k=1}^{n}{\frac {1}{{\text{mdt}}(c\_{k})}}\right)^{-1}\;,}
    ![{\displaystyle {\text{mdt}}(c_{1}\parallel \dots \parallel c_{n})=\left(\sum _{k=1}^{n}{\frac {1}{{\text{mdt}}(c_{k})}}\right)^{-1}\;,}](https://wikimedia.org/api/rest_v1/media/math/render/svg/d4ff49afa781ea4c6e829dbe58cd5d25072c1506)

since the formula for the mdt of two components in parallel is identical to that of the mtbf for two components in series.

## Variations of MTBF

[[edit](/w/index.php?title=Mean_time_between_failures&veaction=edit&section=6 "Edit section: Variations of MTBF") | [edit source](/w/index.php?title=Mean_time_between_failures&action=edit&section=6 "Edit section's source code: Variations of MTBF")]

There are many variations of MTBF, such as *mean time between system aborts* (MTBSA), *mean time between critical failures* (MTBCF) or *mean time between unscheduled removal* (MTBUR). Such nomenclature is used when it is desirable to differentiate among types of failures, such as critical and non-critical failures. For example, in an automobile, the failure of the FM radio does not prevent the primary operation of the vehicle.

It is recommended to use *Mean time to failure* (MTTF) instead of MTBF in cases where a system is replaced after a failure ("non-repairable system"), since MTBF denotes time between failures in a system which can be repaired.[[1]](#cite_note-lienig-1)

[MTTFd](/wiki/MTTFd "MTTFd") is an extension of MTTF, and is only concerned about failures which would result in a dangerous condition. It can be calculated as follows:

:   MTTF

    ≈

    B

    10

    0.1

    n

    onm
    ,

    MTTFd

    ≈

    B

    10
    d

    0.1

    n

    op
    ,
    {\displaystyle {\begin{aligned}{\text{MTTF}}&\approx {\frac {B\_{10}}{0.1n\_{\text{onm}}}},\\[8pt]{\text{MTTFd}}&\approx {\frac {B\_{10d}}{0.1n\_{\text{op}}}},\end{aligned}}}
    ![{\displaystyle {\begin{aligned}{\text{MTTF}}&\approx {\frac {B_{10}}{0.1n_{\text{onm}}}},\\[8pt]{\text{MTTFd}}&\approx {\frac {B_{10d}}{0.1n_{\text{op}}}},\end{aligned}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/469cc107083e433e1ee9aa68ed1dbb1416b1576c)

where *B*10 is the number of operations that a device will operate prior to 10% of a sample of those devices would fail and *n*op is number of operations. *B*10d is the same calculation, but where 10% of the sample would fail to danger. *n*op is the number of operations/cycle in one year.[[11]](#cite_note-11)

### MTBF considering censoring

[[edit](/w/index.php?title=Mean_time_between_failures&veaction=edit&section=7 "Edit section: MTBF considering censoring") | [edit source](/w/index.php?title=Mean_time_between_failures&action=edit&section=7 "Edit section's source code: MTBF considering censoring")]

In fact the MTBF counting only failures with at least some systems still operating that have not yet failed underestimates the MTBF by failing to include in the computations the partial lifetimes of the systems that have not yet failed. With such lifetimes, all we know is that the time to failure exceeds the time they've been running. This is called [censoring](/wiki/Censoring_(statistics) "Censoring (statistics)"). In fact with a [parametric model](/wiki/Parametric_model "Parametric model") of the lifetime, the [likelihood for the experience on any given day is as follows](/wiki/Censoring_(statistics)#likelihood "Censoring (statistics)"):

:   L
    =

    ∏

    i
    λ
    (

    u

    i

    )

    δ

    i
    S
    (

    u

    i
    )
    {\displaystyle L=\prod \_{i}\lambda (u\_{i})^{\delta \_{i}}S(u\_{i})}
    ![{\displaystyle L=\prod _{i}\lambda (u_{i})^{\delta _{i}}S(u_{i})}](https://wikimedia.org/api/rest_v1/media/math/render/svg/d9b2720a50439d54e2fd55e699d324806b405441),

where

:   u

    i
    {\displaystyle u\_{i}}
    ![{\displaystyle u_{i}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/14f13cb025ff2e136dcbd2fc81ddf965b728e3d7) is the failure time for failures and the censoring time for units that have not yet failed,
:   δ

    i
    {\displaystyle \delta \_{i}}
    ![{\displaystyle \delta _{i}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/e0c5e905acee9cc0cf8bc01c08a4e876f43d5c1b) = 1 for failures and 0 for censoring times,
:   S
    (

    u

    i
    )
    {\displaystyle S(u\_{i})}
    ![{\displaystyle S(u_{i})}](https://wikimedia.org/api/rest_v1/media/math/render/svg/50c2895a637a2280e6013f2ed7f5bf5c21eb20df) = the probability that the lifetime exceeds 

    u

    i
    {\displaystyle u\_{i}}
    ![{\displaystyle u_{i}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/14f13cb025ff2e136dcbd2fc81ddf965b728e3d7), called the survival function, and
:   λ
    (

    u

    i
    )
    =
    f
    (
    u
    )

    /
    S
    (
    u
    )
    {\displaystyle \lambda (u\_{i})=f(u)/S(u)}
    ![{\displaystyle \lambda (u_{i})=f(u)/S(u)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/9083021e377d685465ddd9f375bcf9a88d7d3991) is called the [hazard function](/wiki/Failure_rate#hazard_function "Failure rate"), the instantaneous [force of mortality](/wiki/Force_of_mortality "Force of mortality") (where 

    f
    (
    u
    )
    {\displaystyle f(u)}
    ![{\displaystyle f(u)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/32b282ccf3cf0f2b0b601e8629d61612d4951098) = the probability density function of the distribution).

For a constant [exponential distribution](/wiki/Exponential_distribution "Exponential distribution"), the hazard, 

λ
{\displaystyle \lambda }
![{\displaystyle \lambda }](https://wikimedia.org/api/rest_v1/media/math/render/svg/b43d0ea3c9c025af1be9128e62a18fa74bedda2a), is constant. In this case, the MBTF is

:   MTBF = 

    1

    /

    λ
    ^
    =
    ∑

    u

    i

    /
    k
    {\displaystyle 1/{\hat {\lambda }}=\sum u\_{i}/k}
    ![{\displaystyle 1/{\hat {\lambda }}=\sum u_{i}/k}](https://wikimedia.org/api/rest_v1/media/math/render/svg/b3ad89f8f3bf3179ea8156976e160fdfbc3ceff9),

where 

λ
^
{\displaystyle {\hat {\lambda }}}
![{\displaystyle {\hat {\lambda }}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/4e7bb058e73bb0c0545eed7bac5a93b7e1145709) is the maximum likelihood estimate of 

λ
{\displaystyle \lambda }
![{\displaystyle \lambda }](https://wikimedia.org/api/rest_v1/media/math/render/svg/b43d0ea3c9c025af1be9128e62a18fa74bedda2a), maximizing the likelihood given above and 

k
=
∑

σ

i
{\displaystyle k=\sum \sigma \_{i}}
![{\displaystyle k=\sum \sigma _{i}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/c3116a670b5a892cb014fe21604e1108c1f8b16d) is the number of uncensored observations.

We see that the difference between the MTBF considering only failures and the MTBF including censored observations is that the censoring times add to the numerator but not the denominator in computing the MTBF.[[12]](#cite_note-12)

## See also

[[edit](/w/index.php?title=Mean_time_between_failures&veaction=edit&section=8 "Edit section: See also") | [edit source](/w/index.php?title=Mean_time_between_failures&action=edit&section=8 "Edit section's source code: See also")]

.mw-parser-output .div-col{margin-top:0.3em;column-width:30em}.mw-parser-output .div-col-small{font-size:90%}.mw-parser-output .div-col-rules{column-rule:1px solid #aaa}.mw-parser-output .div-col dl,.mw-parser-output .div-col ol,.mw-parser-output .div-col ul{margin-top:0}.mw-parser-output .div-col li,.mw-parser-output .div-col dd{page-break-inside:avoid;break-inside:avoid-column}

- [Annualized failure rate](/wiki/Annualized_failure_rate "Annualized failure rate") – Probability that a device or component will fail during a year of use
- [Failure rate](/wiki/Failure_rate "Failure rate") – Frequency with which an engineered system or component fails
- [Frames per stop](/wiki/Frames_per_stop "Frames per stop") – Term of reliability in the bowling industry
- [Mean time to first failure](/wiki/Mean_time_to_first_failure "Mean time to first failure") – Average service life for non-repairable components
- [Mean time to repair](/wiki/Mean_time_to_repair "Mean time to repair") – Measure of the maintainability of repairable items
- [Power-on hours](/wiki/Power-on_hours "Power-on hours") – Length of time that electrical power is applied to a device
- [Reliability engineering](/wiki/Reliability_engineering "Reliability engineering") – Sub-discipline of systems engineering that emphasizes dependability
- [Residence time (statistics)](/wiki/Residence_time_(statistics) "Residence time (statistics)") – Statistical parameter of random process evolution
- [Bathtub curve](/wiki/Bathtub_curve "Bathtub curve") – Curve for failure rates over time

## References

[[edit](/w/index.php?title=Mean_time_between_failures&veaction=edit&section=9 "Edit section: References") | [edit source](/w/index.php?title=Mean_time_between_failures&action=edit&section=9 "Edit section's source code: References")]

.mw-parser-output .reflist-columns-2{column-width:30em}.mw-parser-output .reflist-columns-3{column-width:25em}body.skin-vector-2022 .mw-parser-output .reflist-columns-2{column-width:27em}body.skin-vector-2022 .mw-parser-output .reflist-columns-3{column-width:22.5em}.mw-parser-output .references[data-mw-group=upper-alpha]{list-style-type:upper-alpha}.mw-parser-output .references[data-mw-group=upper-roman]{list-style-type:upper-roman}.mw-parser-output .references[data-mw-group=lower-alpha]{list-style-type:lower-alpha}.mw-parser-output .references[data-mw-group=lower-greek]{list-style-type:lower-greek}.mw-parser-output .references[data-mw-group=lower-roman]{list-style-type:lower-roman}.mw-parser-output div.reflist-liststyle-upper-alpha .references{list-style-type:upper-alpha}.mw-parser-output div.reflist-liststyle-upper-roman .references{list-style-type:upper-roman}.mw-parser-output div.reflist-liststyle-lower-alpha .references{list-style-type:lower-alpha}.mw-parser-output div.reflist-liststyle-lower-greek .references{list-style-type:lower-greek}.mw-parser-output div.reflist-liststyle-lower-roman .references{list-style-type:lower-roman}

1. ^ [***a***](#cite_ref-lienig_1-0) [***b***](#cite_ref-lienig_1-1) [***c***](#cite_ref-lienig_1-2) [***d***](#cite_ref-lienig_1-3) [***e***](#cite_ref-lienig_1-4) [***f***](#cite_ref-lienig_1-5) .mw-parser-output cite.citation{font-style:inherit;word-wrap:break-word}.mw-parser-output .citation q{quotes:"\"""\"""'""'"}.mw-parser-output .citation:target{background-color:rgba(0,127,255,0.133)}.mw-parser-output .id-lock-free.id-lock-free a{background:url("//upload.wikimedia.org/wikipedia/commons/6/65/Lock-green.svg")right 0.1em center/9px no-repeat}.mw-parser-output .id-lock-limited.id-lock-limited a,.mw-parser-output .id-lock-registration.id-lock-registration a{background:url("//upload.wikimedia.org/wikipedia/commons/d/d6/Lock-gray-alt-2.svg")right 0.1em center/9px no-repeat}.mw-parser-output .id-lock-subscription.id-lock-subscription a{background:url("//upload.wikimedia.org/wikipedia/commons/a/aa/Lock-red-alt-2.svg")right 0.1em center/9px no-repeat}.mw-parser-output .cs1-ws-icon a{background:url("//upload.wikimedia.org/wikipedia/commons/4/4c/Wikisource-logo.svg")right 0.1em center/12px no-repeat}body:not(.skin-timeless):not(.skin-minerva) .mw-parser-output .id-lock-free a,body:not(.skin-timeless):not(.skin-minerva) .mw-parser-output .id-lock-limited a,body:not(.skin-timeless):not(.skin-minerva) .mw-parser-output .id-lock-registration a,body:not(.skin-timeless):not(.skin-minerva) .mw-parser-output .id-lock-subscription a,body:not(.skin-timeless):not(.skin-minerva) .mw-parser-output .cs1-ws-icon a{background-size:contain;padding:0 1em 0 0}.mw-parser-output .cs1-code{color:inherit;background:inherit;border:none;padding:inherit}.mw-parser-output .cs1-hidden-error{display:none;color:var(--color-error,#bf3c2c)}.mw-parser-output .cs1-visible-error{color:var(--color-error,#bf3c2c)}.mw-parser-output .cs1-maint{display:none;color:#085;margin-left:0.3em}.mw-parser-output .cs1-kern-left{padding-left:0.2em}.mw-parser-output .cs1-kern-right{padding-right:0.2em}.mw-parser-output .citation .mw-selflink{font-weight:inherit}@media screen{.mw-parser-output .cs1-format{font-size:95%}html.skin-theme-clientpref-night .mw-parser-output .cs1-maint{color:#18911f}}@media screen and (prefers-color-scheme:dark){html.skin-theme-clientpref-os .mw-parser-output .cs1-maint{color:#18911f}}J. Lienig, H. Bruemmer (2017). "Reliability Analysis". *Fundamentals of Electronic Systems Design*. Springer International Publishing. pp. 45–73. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1007/978-3-319-55840-0\_4](https://doi.org/10.1007%2F978-3-319-55840-0_4). [ISBN](/wiki/ISBN_(identifier) "ISBN (identifier)") [978-3-319-55839-4](/wiki/Special:BookSources/978-3-319-55839-4 "Special:BookSources/978-3-319-55839-4").
2. **[^](#cite_ref-2)** Colombo, A.G., and Sáiz de Bustamante, Amalio: *Systems reliability assessment – Proceedings of the Ispra Course held at the Escuela Tecnica Superior de Ingenieros Navales, Madrid, Spain, September 19–23, 1988 in collaboration with Universidad Politecnica de Madrid*, 1988
3. **[^](#cite_ref-3)** ["Defining Failure: What Is MTTR, MTTF, and MTBF?"](http://blog.fosketts.net/2011/07/06/defining-failure-mttr-mttf-mtbf/). *Stephen Foskett, Pack Rat*. 6 July 2011. Retrieved 2016-01-18.
4. ^ [***a***](#cite_ref-birolini_4-0) [***b***](#cite_ref-birolini_4-1) [***c***](#cite_ref-birolini_4-2) Alessandro Birolini: *Reliability Engineering: Theory and Practice*. Springer, Berlin 2013, [ISBN](/wiki/ISBN_(identifier) "ISBN (identifier)") [978-3-642-39534-5](/wiki/Special:BookSources/978-3-642-39534-5 "Special:BookSources/978-3-642-39534-5").
5. **[^](#cite_ref-5)** ["Reliability and MTBF Overview"](http://www.vicorpower.com/documents/quality/Rel_MTBF.pdf) (PDF). Vicor Reliability Engineering. Retrieved 1 June 2017.
6. **[^](#cite_ref-6)** ["MTBF: What it means and how to calculate it"](https://total-manufacturing.com/maintenance/tpm-en/mtbf/). *total-manufacturing.com*. Retrieved 2024-02-07.
7. **[^](#cite_ref-7)** PhD, Bartosz Misiurek (2021-11-22). ["MTBF MTTR MTTF: TPM Indicators"](https://leancommunity.org/mtbf-mttr-and-mttf/). *Lean Community*. Retrieved 2024-02-07.
8. ^ [***a***](#cite_ref-auroraconsultingengineering_8-0) [***b***](#cite_ref-auroraconsultingengineering_8-1) [***c***](#cite_ref-auroraconsultingengineering_8-2) [***d***](#cite_ref-auroraconsultingengineering_8-3) ["Reliability Characteristics for Two Subsystems in Series or Parallel or n Subsystems in m\_out\_of\_n Arrangement (by Don L. Lin)"](https://web.archive.org/web/20190712084308/http://auroraconsultingengineering.com/doc_files/Reliability_series_parallel.doc). *auroraconsultingengineering.com*. Archived from [the original](http://auroraconsultingengineering.com/doc_files/Reliability_series_parallel.doc) on 2019-07-12. Retrieved 2016-12-23.
9. ^ [***a***](#cite_ref-smith_9-0) [***b***](#cite_ref-smith_9-1) Dr. David J. Smith (2011). *Reliability, Maintainability and Risk* (eighth ed.). Butterworth-Heinemann. [ISBN](/wiki/ISBN_(identifier) "ISBN (identifier)") [978-0080969022](/wiki/Special:BookSources/978-0080969022 "Special:BookSources/978-0080969022").
10. **[^](#cite_ref-10)** ["MTBF Allocations Analysis1"](https://web.archive.org/web/20021106143359/http://www.angelfire.com/ca/summers/Business/MTBFAllocAnalysis1.html). *[Angelfire](/wiki/Angelfire "Angelfire")*. Archived from [the original](http://www.angelfire.com/ca/summers/Business/MTBFAllocAnalysis1.html) on November 6, 2002. Retrieved 2016-12-23.
11. **[^](#cite_ref-11)** ["B10d Assessment – Reliability Parameter for Electro-Mechanical Components"](https://web.archive.org/web/20150708023404/http://www.tuv.com/media/hungary/downloads_hu/B10d_EN.pdf) (PDF). TUVRheinland. Archived from [the original](https://www.tuv.com/media/hungary/downloads_hu/B10d_EN.pdf) (PDF) on 8 July 2015. Retrieved 7 July 2015.
12. **[^](#cite_ref-12)** Lu Tian, [*Likelihood Construction, Inference for Parametric Survival Distributions*](https://web.stanford.edu/~lutian/coursepdf/unit2.pdf) (PDF), [Wikidata](/wiki/WDQ_(identifier) "WDQ (identifier)") [Q98961801](https://www.wikidata.org/wiki/Q98961801 "d:Q98961801") `{{Cite Q}}`: Missing first/last names in Wikidata for Lu Tian [![](//thumb.wikimedia.org/wikipedia/commons/thumb/4/4b/Edit_icon_on_Wikisite.svg/20px-Edit_icon_on_Wikisite.svg.png?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail)](https://www.wikidata.org/wiki/Q89726462 "d:Q89726462") ([help](/wiki/Template:Cite_Q#Error_messages "Template:Cite Q")) .

## External links

[[edit](/w/index.php?title=Mean_time_between_failures&veaction=edit&section=10 "Edit section: External links") | [edit source](/w/index.php?title=Mean_time_between_failures&action=edit&section=10 "Edit section's source code: External links")]

- ["Reliability and Availability Basics"](http://www.eventhelix.com/RealtimeMantra/FaultHandling/reliability_availability_basics.htm). EventHelix.
- Speaks, Scott (2005). ["Reliability and MTBF Overview"](http://www.vicorpower.com/documents/quality/Rel_MTBF.pdf) (PDF). Vicor Reliability Engineering.
- ["Failure Rates, MTBF, and All That"](http://www.mathpages.com/home/kmath498/kmath498.htm). MathPages.
- ["Simple Guide to MTBF: What It Is and When To use It"](https://web.archive.org/web/20230505104442/https://roadtoreliability.com/mtbf-mean-time-between-failure/). Road to Reliability. 10 December 2021. Archived from [the original](https://www.roadtoreliability.com/mtbf-mean-time-between-failure/) on 5 May 2023. Retrieved 3 January 2021.
- ["What is Mean Time to Failure and How Do We Calculate?"](https://www.nexgenam.com/blog/what-is-mean-time-to-failure-mttf/). NEXGEN. 21 June 2023.

.mw-parser-output .hlist dl,.mw-parser-output .hlist ol,.mw-parser-output .hlist ul{margin:0;padding:0}.mw-parser-output .hlist dd,.mw-parser-output .hlist dt,.mw-parser-output .hlist li{margin:0;display:inline}.mw-parser-output .hlist.inline,.mw-parser-output .hlist.inline dl,.mw-parser-output .hlist.inline ol,.mw-parser-output .hlist.inline ul,.mw-parser-output .hlist dl dl,.mw-parser-output .hlist dl ol,.mw-parser-output .hlist dl ul,.mw-parser-output .hlist ol dl,.mw-parser-output .hlist ol ol,.mw-parser-output .hlist ol ul,.mw-parser-output .hlist ul dl,.mw-parser-output .hlist ul ol,.mw-parser-output .hlist ul ul{display:inline}.mw-parser-output .hlist .mw-empty-li{display:none}.mw-parser-output .hlist dt::after{content:": "}.mw-parser-output .hlist dd::after,.mw-parser-output .hlist li::after{content:"\a0 · ";font-weight:bold}.mw-parser-output .hlist dd:last-child::after,.mw-parser-output .hlist dt:last-child::after,.mw-parser-output .hlist li:last-child::after{content:none}.mw-parser-output .hlist dd dd:first-child::before,.mw-parser-output .hlist dd dt:first-child::before,.mw-parser-output .hlist dd li:first-child::before,.mw-parser-output .hlist dt dd:first-child::before,.mw-parser-output .hlist dt dt:first-child::before,.mw-parser-output .hlist dt li:first-child::before,.mw-parser-output .hlist li dd:first-child::before,.mw-parser-output .hlist li dt:first-child::before,.mw-parser-output .hlist li li:first-child::before{content:" (";font-weight:normal}.mw-parser-output .hlist dd dd:last-child::after,.mw-parser-output .hlist dd dt:last-child::after,.mw-parser-output .hlist dd li:last-child::after,.mw-parser-output .hlist dt dd:last-child::after,.mw-parser-output .hlist dt dt:last-child::after,.mw-parser-output .hlist dt li:last-child::after,.mw-parser-output .hlist li dd:last-child::after,.mw-parser-output .hlist li dt:last-child::after,.mw-parser-output .hlist li li:last-child::after{content:")";font-weight:normal}.mw-parser-output .hlist ol{counter-reset:listitem}.mw-parser-output .hlist ol>li{counter-increment:listitem}.mw-parser-output .hlist ol>li::before{content:" "counter(listitem)"\a0 "}.mw-parser-output .hlist dd ol>li:first-child::before,.mw-parser-output .hlist dt ol>li:first-child::before,.mw-parser-output .hlist li ol>li:first-child::before{content:" ("counter(listitem)"\a0 "}.mw-parser-output .navbox{box-sizing:border-box;border:1px solid #a2a9b1;width:100%;clear:both;font-size:88%;text-align:center;padding:1px;margin:1em auto 0}.mw-parser-output .navbox .navbox{margin-top:0}.mw-parser-output .navbox+.navbox-styles+.navbox,.mw-parser-output .navbox+span.mw-empty-elt+.navbox-styles+.navbox{margin-top:-1px}.mw-parser-output .navbox-inner,.mw-parser-output .navbox-subgroup{width:100%}.mw-parser-output .navbox-group,.mw-parser-output .navbox-title,.mw-parser-output .navbox-abovebelow{padding:0.25em 1em;line-height:1.5em;text-align:center}.mw-parser-output .navbox-group{white-space:nowrap;text-align:right}.mw-parser-output .navbox,.mw-parser-output .navbox-subgroup{background-color:#fdfdfd;color:inherit}.mw-parser-output .navbox-list{line-height:1.5em;border-color:#fdfdfd}.mw-parser-output .navbox-list-with-group{text-align:left;border-left-width:2px;border-left-style:solid}.mw-parser-output tr+tr>.navbox-abovebelow,.mw-parser-output tr+tr>.navbox-group,.mw-parser-output tr+tr>.navbox-image,.mw-parser-output tr+tr>.navbox-list{border-top:2px solid #fdfdfd}.mw-parser-output .navbox-title{background-color:#ccf;color:inherit}.mw-parser-output .navbox-abovebelow,.mw-parser-output .navbox-group,.mw-parser-output .navbox-subgroup .navbox-title{background-color:#ddf;color:inherit}.mw-parser-output .navbox-subgroup .navbox-group,.mw-parser-output .navbox-subgroup .navbox-abovebelow{background-color:#e6e6ff;color:inherit}.mw-parser-output .navbox-even{background-color:#f7f7f7;color:inherit}.mw-parser-output .navbox-odd{background-color:transparent;color:inherit}.mw-parser-output .navbox .hlist td dl,.mw-parser-output .navbox .hlist td ol,.mw-parser-output .navbox .hlist td ul,.mw-parser-output .navbox td.hlist dl,.mw-parser-output .navbox td.hlist ol,.mw-parser-output .navbox td.hlist ul{padding:0.125em 0}.mw-parser-output .navbox .navbar{display:block;font-size:100%}.mw-parser-output .navbox-title .navbar{float:left;text-align:left;margin-right:0.5em}body.skin--responsive .mw-parser-output .navbox-image img{max-width:none!important}@media print{body.ns-0 .mw-parser-output .navbox{display:none!important}}

| .mw-parser-output .navbar{display:inline;font-size:88%;font-weight:normal}.mw-parser-output .navbar-collapse{float:left;text-align:left}.mw-parser-output .navbar-boxtext{word-spacing:0}.mw-parser-output .navbar ul{display:inline-block;white-space:nowrap;line-height:inherit}.mw-parser-output .navbar-brackets::before{margin-right:-0.125em;content:"[ "}.mw-parser-output .navbar-brackets::after{margin-left:-0.125em;content:" ]"}.mw-parser-output .navbar li{word-spacing:-0.125em}.mw-parser-output .navbar a>span,.mw-parser-output .navbar a>abbr{text-decoration:inherit}.mw-parser-output .navbar-mini abbr{font-variant:small-caps;border-bottom:none;text-decoration:none;cursor:inherit}.mw-parser-output .navbar-ct-full{font-size:114%;margin:0 7em}.mw-parser-output .navbar-ct-mini{font-size:114%;margin:0 4em}html.skin-theme-clientpref-night .mw-parser-output .navbar li a abbr{color:var(--color-base)!important}@media(prefers-color-scheme:dark){html.skin-theme-clientpref-os .mw-parser-output .navbar li a abbr{color:var(--color-base)!important}}@media print{.mw-parser-output .navbar{display:none!important}} - [v](/wiki/Template:Reliability_indices "Template:Reliability indices") - [t](/wiki/Template_talk:Reliability_indices "Template talk:Reliability indices") - [e](/wiki/Special:EditPage/Template:Reliability_indices "Special:EditPage/Template:Reliability indices")  [Reliability indices](/wiki/Reliability_index "Reliability index") | |
| --- | --- |
| Generic | - [MTBF](/wiki/MTBF "MTBF") - [MTTR](/wiki/Mean_time_to_repair "Mean time to repair") - [FOR](/wiki/Forced_outage_rate "Forced outage rate") - [EFOR](/wiki/Forced_outage_rate "Forced outage rate") |
| Electricity distribution | - [ASUI](/wiki/ASUI "ASUI") - [ASAI](/wiki/Average_Service_Availability_Index "Average Service Availability Index") - [CAIDI](/wiki/CAIDI "CAIDI")/[SAIDI](/wiki/SAIDI "SAIDI") - [CAIFI](/wiki/CAIFI "CAIFI")/[SAIFI](/wiki/SAIFI "SAIFI") - [MAIFI](/wiki/MAIFI "MAIFI") - [CTAIDI](/wiki/CTAIDI "CTAIDI") |
| Electricity generation | - [LOLP](/wiki/LOLP "LOLP") - [LOLE](/wiki/LOLE "LOLE") - [LOLEV](/wiki/LOLEV "LOLEV") - [LOLF](/wiki/Loss_of_load_frequency "Loss of load frequency") - [LOLH](/wiki/LOLH "LOLH") |
