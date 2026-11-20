<!-- category: reliability_engineering -->
# Failure rate

Frequency with which an engineered system or component fails

**Failure rate** is the [frequency](/wiki/Frequency "Frequency") with which any system or component fails, expressed in failures per unit of time. It thus depends on the system conditions, time interval, and total number of systems under study.[[1]](#cite_note-macdiarmid-1)
It can describe electronic, mechanical, or biological systems, in fields such as [systems](/wiki/Systems_engineering "Systems engineering") and [reliability](/wiki/Reliability_engineering "Reliability engineering") engineering, [medicine](/wiki/Medicine "Medicine") and [biology](/wiki/Biology "Biology"), or [insurance](/wiki/Insurance "Insurance") and [finance](/wiki/Finance "Finance"). It is usually denoted by the [Greek letter](/wiki/Greek_alphabet "Greek alphabet") 

λ
{\displaystyle \lambda }
![{\displaystyle \lambda }](https://wikimedia.org/api/rest_v1/media/math/render/svg/b43d0ea3c9c025af1be9128e62a18fa74bedda2a) ([lambda](/wiki/Lambda "Lambda")).

In real-world applications, the failure probability of a system usually differs over time; failures occur more frequently in early-life (["burning in"](/wiki/Burn-in "Burn-in")), or as a system ages (["wearing out"](/wiki/Wear_and_tear "Wear and tear")). This is known as the [bathtub curve](/wiki/Bathtub_curve "Bathtub curve"), where the middle region is called the "useful life period".

## Mean time between failures (MTBF)

[[edit](/w/index.php?title=Failure_rate&veaction=edit&section=1 "Edit section: Mean time between failures (MTBF)") | [edit source](/w/index.php?title=Failure_rate&action=edit&section=1 "Edit section's source code: Mean time between failures (MTBF)")]

The [mean time between failures](/wiki/Mean_time_between_failures "Mean time between failures") (MTBF, 

1

/
λ
{\displaystyle 1/\lambda }
![{\displaystyle 1/\lambda }](https://wikimedia.org/api/rest_v1/media/math/render/svg/1add931eabb9aec89275acb2f50d50428010b0fe)) is often reported instead of the failure rate, as numbers such as "2,000 hours" are more intuitive than numbers such as "0.0005 per hour".

However, this is only valid if the failure rate 

λ
(
t
)
{\displaystyle \lambda (t)}
![{\displaystyle \lambda (t)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/e0e1cc2c2f9e6d8b22c0da0bb5fe8f0f47791e4a) is actually constant over time, such as within the flat region of the bathtub curve. In many cases where MTBF is quoted, it refers only to this region; thus it cannot be used to give an accurate calculation of the average lifetime of a system, as it ignores the "burn-in" and "wear-out" regions.

MTBF appears frequently in [engineering](/wiki/Engineering "Engineering") design requirements, and governs the frequency of required system maintenance and inspections. A similar ratio used in the [transport industries](/wiki/Transport_industry "Transport industry"), especially in [railways](/wiki/Railway "Railway") and trucking, is "mean distance between failures" (MDBF) - allowing maintenance to be scheduled based on distance travelled, rather than at regular time intervals.

## Mathematical definition

[[edit](/w/index.php?title=Failure_rate&veaction=edit&section=2 "Edit section: Mathematical definition") | [edit source](/w/index.php?title=Failure_rate&action=edit&section=2 "Edit section's source code: Mathematical definition")]

The simplest definition of failure rate 

λ
{\displaystyle \lambda }
![{\displaystyle \lambda }](https://wikimedia.org/api/rest_v1/media/math/render/svg/b43d0ea3c9c025af1be9128e62a18fa74bedda2a) is simply the number of failures 

Δ
n
{\displaystyle \Delta n}
![{\displaystyle \Delta n}](https://wikimedia.org/api/rest_v1/media/math/render/svg/31f0672c38daf81ebe64b7828c72883b52d2d261) per time interval 

Δ
t
{\displaystyle \Delta t}
![{\displaystyle \Delta t}](https://wikimedia.org/api/rest_v1/media/math/render/svg/8c28867ecd34e2caed12cf38feadf6a81a7ee542):

λ
=

Δ
n

Δ
t
{\displaystyle \lambda ={\frac {\Delta n}{\Delta t}}}
![{\displaystyle \lambda ={\frac {\Delta n}{\Delta t}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/47d2eb14a60583603d8ab3c4b09f9cbae0382072)

which would depend on the number of systems under study, and the conditions over the time period.

### Failures over time

[[edit](/w/index.php?title=Failure_rate&veaction=edit&section=3 "Edit section: Failures over time") | [edit source](/w/index.php?title=Failure_rate&action=edit&section=3 "Edit section's source code: Failures over time")]

[![](//thumb.wikimedia.org/wikipedia/commons/thumb/8/80/Exponential_distribution_cdf.svg/330px-Exponential_distribution_cdf.svg.png?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail)](/wiki/File:Exponential_distribution_cdf.svg)

Cumulative distribution function for the [exponential distribution](/wiki/Exponential_distribution "Exponential distribution"), often used as the cumulative failure function 

F
(
t
)
{\displaystyle F(t)}
![{\displaystyle F(t)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/5b57ed3bbf501fb3c7f4bc5c4eafa96bb9e32165)

To accurately model failures over time, a **cumulative failure distribution**, 

F
(
t
)
{\displaystyle F(t)}
![{\displaystyle F(t)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/5b57ed3bbf501fb3c7f4bc5c4eafa96bb9e32165) must be defined, which can be any [cumulative distribution function](/wiki/Cumulative_distribution_function "Cumulative distribution function") (CDF) that gradually increases from 

0
{\displaystyle 0}
![{\displaystyle 0}](https://wikimedia.org/api/rest_v1/media/math/render/svg/2aae8864a3c1fec9585261791a809ddec1489950) to 

1
{\displaystyle 1}
![{\displaystyle 1}](https://wikimedia.org/api/rest_v1/media/math/render/svg/92d98b82a3778f043108d4e20960a9193df57cbf). In the case of many identical systems, this may be thought of as the fraction of systems failing over time 

t
{\displaystyle t}
![{\displaystyle t}](https://wikimedia.org/api/rest_v1/media/math/render/svg/65658b7b223af9e1acc877d848888ecdb4466560), after all starting operation at time 

t
=
0
{\displaystyle t=0}
![{\displaystyle t=0}](https://wikimedia.org/api/rest_v1/media/math/render/svg/43469ec032d858feae5aa87029e22eaaf0109e9c); or in the case of a single system, as the [probability](/wiki/Probability "Probability") of the system having its failure time 

T
{\displaystyle T}
![{\displaystyle T}](https://wikimedia.org/api/rest_v1/media/math/render/svg/ec7200acd984a1d3a3d7dc455e262fbe54f7f6e0) before time 

t
{\displaystyle t}
![{\displaystyle t}](https://wikimedia.org/api/rest_v1/media/math/render/svg/65658b7b223af9e1acc877d848888ecdb4466560):

F
(
t
)
=
Pr
(
T
≤
t
)
.
{\displaystyle F(t)=\Pr(T\leq t).}
![{\displaystyle F(t)=\Pr(T\leq t).}](https://wikimedia.org/api/rest_v1/media/math/render/svg/dace67adba69e0ee5a3e0aaa5dafae0d0f6920f4)

As CDFs are defined by integrating a [probability density function](/wiki/Probability_density_function "Probability density function"), the **failure probability density** 

f
(
t
)
{\displaystyle f(t)}
![{\displaystyle f(t)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/5bf044fe2fbfc4bd8d6d7230f4108430263f9fd6) is defined such that:

[![](//thumb.wikimedia.org/wikipedia/commons/thumb/e/ec/Exponential_pdf.svg/330px-Exponential_pdf.svg.png?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail)](/wiki/File:Exponential_pdf.svg)

Exponential probability functions, often used as the failure probability density 

f
(
t
)
{\displaystyle f(t)}
![{\displaystyle f(t)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/5bf044fe2fbfc4bd8d6d7230f4108430263f9fd6)

F
(
t
)
=

∫

0

t
f
(
τ
)

d
τ
{\displaystyle F(t)=\int \_{0}^{t}f(\tau )\,d\tau }
![{\displaystyle F(t)=\int _{0}^{t}f(\tau )\,d\tau }](https://wikimedia.org/api/rest_v1/media/math/render/svg/f5723e65cae633c69f93e4597ff88cc0d3b1a1a1)

where 

τ
{\displaystyle \tau }
![{\displaystyle \tau }](https://wikimedia.org/api/rest_v1/media/math/render/svg/38a7dcde9730ef0853809fefc18d88771f95206c) is a dummy integration variable. Here 

f
(
t
)
{\displaystyle f(t)}
![{\displaystyle f(t)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/5bf044fe2fbfc4bd8d6d7230f4108430263f9fd6) can be thought of as the *instantaneous failure rate*, i.e. the probability of failure in the time interval between 

t
{\displaystyle t}
![{\displaystyle t}](https://wikimedia.org/api/rest_v1/media/math/render/svg/65658b7b223af9e1acc877d848888ecdb4466560) and 

t

+
Δ
t
{\displaystyle t{+}\Delta t}
![{\displaystyle t{+}\Delta t}](https://wikimedia.org/api/rest_v1/media/math/render/svg/68f115ae34a605e8265c0a5d0de5f4a45dcbbf25), as 

Δ
t
{\displaystyle \Delta t}
![{\displaystyle \Delta t}](https://wikimedia.org/api/rest_v1/media/math/render/svg/8c28867ecd34e2caed12cf38feadf6a81a7ee542) tends towards 

0
{\displaystyle 0}
![{\displaystyle 0}](https://wikimedia.org/api/rest_v1/media/math/render/svg/2aae8864a3c1fec9585261791a809ddec1489950):

f
(
t
)
=

lim

Δ
t
→

0

+

Pr
(
t
<
T
≤
t

+
Δ
t
)

Δ
t
.
{\displaystyle f(t)=\lim \_{\Delta t\to 0^{+}}{\frac {\Pr(t<T\leq t{+}\Delta t)}{\Delta t}}.}
![{\displaystyle f(t)=\lim _{\Delta t\to 0^{+}}{\frac {\Pr(t<T\leq t{+}\Delta t)}{\Delta t}}.}](https://wikimedia.org/api/rest_v1/media/math/render/svg/515a1da250ec06820170c5837d2afdaec9652bf6)

### Hazard rate

[[edit](/w/index.php?title=Failure_rate&veaction=edit&section=4 "Edit section: Hazard rate") | [edit source](/w/index.php?title=Failure_rate&action=edit&section=4 "Edit section's source code: Hazard rate")]

A concept closely related but different[[2]](#cite_note-todinov-2) to instantaneous failure rate 

f
(
t
)
{\displaystyle f(t)}
![{\displaystyle f(t)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/5bf044fe2fbfc4bd8d6d7230f4108430263f9fd6) is the **hazard rate** (or **.mw-parser-output .vanchor>:target~.vanchor-text{background-color:#ebf4ff}@media screen{html.skin-theme-clientpref-night .mw-parser-output .vanchor>:target~.vanchor-text{background-color:#0f4dc9}}@media screen and (prefers-color-scheme:dark){html.skin-theme-clientpref-os .mw-parser-output .vanchor>:target~.vanchor-text{background-color:#0f4dc9}}hazard function**), 

h
(
t
)
{\displaystyle h(t)}
![{\displaystyle h(t)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/66abbb8ae1d9f30bb529739b109e1e5bbe83c626). In the many-system case, this is defined as the proportional failure rate of the systems *still functioning* at time 

t
{\displaystyle t}
![{\displaystyle t}](https://wikimedia.org/api/rest_v1/media/math/render/svg/65658b7b223af9e1acc877d848888ecdb4466560) – as opposed to 

f
(
t
)
{\displaystyle f(t)}
![{\displaystyle f(t)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/5bf044fe2fbfc4bd8d6d7230f4108430263f9fd6), which is the expressed as a proportion of the *initial number* of systems.

For convenience we first define the reliability (or [survival function](/wiki/Survival_function "Survival function")) as:

R
(
t
)
=
1
−
F
(
t
)
=
Pr
(
T
>
t
)
{\displaystyle R(t)=1-F(t)=\Pr(T>t)}
![{\displaystyle R(t)=1-F(t)=\Pr(T>t)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/8b1e30fbed33bdcbd0d9e965770bc38b8ef50800)

then the hazard rate is simply the instantaneous failure rate, scaled by the fraction of surviving systems at time 

t
{\displaystyle t}
![{\displaystyle t}](https://wikimedia.org/api/rest_v1/media/math/render/svg/65658b7b223af9e1acc877d848888ecdb4466560):

h
(
t
)
=

f
(
t
)

R
(
t
)
{\displaystyle h(t)={\frac {f(t)}{R(t)}}}
![{\displaystyle h(t)={\frac {f(t)}{R(t)}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/31f7cf383ed61ac90b68822685be05760057f5e3)

In the probabilistic sense for a single system, this can be interpreted as the instantaneous failure rate under the [conditional probability](/wiki/Conditional_probability "Conditional probability") that the system or component has already survived to time 

t
{\displaystyle t}
![{\displaystyle t}](https://wikimedia.org/api/rest_v1/media/math/render/svg/65658b7b223af9e1acc877d848888ecdb4466560):

h
(
t
)
=

lim

Δ
t
→

0

+

Pr
(
t
<
T
≤
t

+
Δ
t
∣
T
>
t
)

Δ
t
.
{\displaystyle h(t)=\lim \_{\Delta t\to 0^{+}}{\frac {\Pr(t<T\leq t{+}\Delta t\mid T>t)}{\Delta t}}.}
![{\displaystyle h(t)=\lim _{\Delta t\to 0^{+}}{\frac {\Pr(t<T\leq t{+}\Delta t\mid T>t)}{\Delta t}}.}](https://wikimedia.org/api/rest_v1/media/math/render/svg/178f7c416aa6d530bd08c5c177f26cafd385b658)

#### Conversion to cumulative failure rate

[[edit](/w/index.php?title=Failure_rate&veaction=edit&section=5 "Edit section: Conversion to cumulative failure rate") | [edit source](/w/index.php?title=Failure_rate&action=edit&section=5 "Edit section's source code: Conversion to cumulative failure rate")]

To convert between 

h
(
t
)
{\displaystyle h(t)}
![{\displaystyle h(t)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/66abbb8ae1d9f30bb529739b109e1e5bbe83c626) and 

F
(
t
)
{\displaystyle F(t)}
![{\displaystyle F(t)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/5b57ed3bbf501fb3c7f4bc5c4eafa96bb9e32165), we can solve the differential equation

h
(
t
)
=

f
(
t
)

R
(
t
)
=
−

R
′
(
t
)

R
(
t
)
{\displaystyle h(t)={\frac {f(t)}{R(t)}}=-{\frac {R'(t)}{R(t)}}}
![{\displaystyle h(t)={\frac {f(t)}{R(t)}}=-{\frac {R'(t)}{R(t)}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/69c9be7cc0a48c56558df94475b4b180712212ec)

with initial condition 

R
(
0
)
=
1
{\displaystyle R(0)=1}
![{\displaystyle R(0)=1}](https://wikimedia.org/api/rest_v1/media/math/render/svg/ca6c78634f05d8ceb7c8eb50c4948033ea6a1f93), which yields[[2]](#cite_note-todinov-2)

F
(
t
)
=
1
−
exp
⁡

(

−

∫

0

t
h
(
τ
)
d
τ
)
.
{\displaystyle F(t)=1-\exp {\left(-\int \_{0}^{t}h(\tau )d\tau \right)}.}
![{\displaystyle F(t)=1-\exp {\left(-\int _{0}^{t}h(\tau )d\tau \right)}.}](https://wikimedia.org/api/rest_v1/media/math/render/svg/d269d32eeb6778d9a53350ab3aca5d9afd424e56)

Thus for a collection of identical systems, only one of hazard rate 

h
(
t
)
{\displaystyle h(t)}
![{\displaystyle h(t)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/66abbb8ae1d9f30bb529739b109e1e5bbe83c626), failure probability density 

f
(
t
)
{\displaystyle f(t)}
![{\displaystyle f(t)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/5bf044fe2fbfc4bd8d6d7230f4108430263f9fd6), or cumulative failure distribution 

F
(
t
)
{\displaystyle F(t)}
![{\displaystyle F(t)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/5b57ed3bbf501fb3c7f4bc5c4eafa96bb9e32165) need be defined.

Confusion can occur as the notation 

λ
(
t
)
{\displaystyle \lambda (t)}
![{\displaystyle \lambda (t)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/e0e1cc2c2f9e6d8b22c0da0bb5fe8f0f47791e4a) for "failure rate" often refers to the function 

h
(
t
)
{\displaystyle h(t)}
![{\displaystyle h(t)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/66abbb8ae1d9f30bb529739b109e1e5bbe83c626) rather than 

f
(
t
)
.
{\displaystyle f(t).}
![{\displaystyle f(t).}](https://wikimedia.org/api/rest_v1/media/math/render/svg/db88c28d6c644c905a4e12de7971c3d1eed37540)[[3]](#cite_note-3)

### Constant hazard rate model

[[edit](/w/index.php?title=Failure_rate&veaction=edit&section=6 "Edit section: Constant hazard rate model") | [edit source](/w/index.php?title=Failure_rate&action=edit&section=6 "Edit section's source code: Constant hazard rate model")]

There are many possible functions that could be chosen to represent failure probability density 

f
(
t
)
{\displaystyle f(t)}
![{\displaystyle f(t)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/5bf044fe2fbfc4bd8d6d7230f4108430263f9fd6) or hazard rate 

h
(
t
)
{\displaystyle h(t)}
![{\displaystyle h(t)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/66abbb8ae1d9f30bb529739b109e1e5bbe83c626), based on empirical or theoretical evidence, but the most common and easily-understandable choice is to set

f
(
t
)
=
λ

e

−
λ
t
,
{\displaystyle f(t)=\lambda e^{-\lambda t},}
![{\displaystyle f(t)=\lambda e^{-\lambda t},}](https://wikimedia.org/api/rest_v1/media/math/render/svg/8aacc89350b3acc5696263065df5bd3a2e5fcd69)

an [exponential function](/wiki/Exponential_function "Exponential function") with scaling constant 

λ
{\displaystyle \lambda }
![{\displaystyle \lambda }](https://wikimedia.org/api/rest_v1/media/math/render/svg/b43d0ea3c9c025af1be9128e62a18fa74bedda2a). As seen in the figures above, this represents a gradually decreasing failure probability density.

The CDF 

F
(
t
)
{\displaystyle F(t)}
![{\displaystyle F(t)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/5b57ed3bbf501fb3c7f4bc5c4eafa96bb9e32165) is then calculated as:

F
(
t
)
=

∫

0

t
λ

e

−
λ
τ

d
τ
=
1
−

e

−
λ
t
,
{\displaystyle F(t)=\int \_{0}^{t}\lambda e^{-\lambda \tau }\,d\tau =1-e^{-\lambda t},}
![{\displaystyle F(t)=\int _{0}^{t}\lambda e^{-\lambda \tau }\,d\tau =1-e^{-\lambda t},}](https://wikimedia.org/api/rest_v1/media/math/render/svg/8b438eb8e060f25f3b57b9318270b0fcc51b0614)

which can be seen to gradually approach 

1
{\displaystyle 1}
![{\displaystyle 1}](https://wikimedia.org/api/rest_v1/media/math/render/svg/92d98b82a3778f043108d4e20960a9193df57cbf) as 

t
→
∞
,
{\displaystyle t\to \infty ,}
![{\displaystyle t\to \infty ,}](https://wikimedia.org/api/rest_v1/media/math/render/svg/561cfbaa874dc49fbb62cbe71cee1ac835ee3c60) representing the fact that eventually all systems under study will fail.

The hazard rate function is then:

h
(
t
)
=

f
(
t
)

R
(
t
)
=

λ

e

−
λ
t

e

−
λ
t
=
λ
.
{\displaystyle h(t)={\frac {f(t)}{R(t)}}={\frac {\lambda e^{-\lambda t}}{e^{-\lambda t}}}=\lambda .}
![{\displaystyle h(t)={\frac {f(t)}{R(t)}}={\frac {\lambda e^{-\lambda t}}{e^{-\lambda t}}}=\lambda .}](https://wikimedia.org/api/rest_v1/media/math/render/svg/db2d994c08c4e4cae7761ab2d04293c6c3c2ecd5)

In other words, in this particular case *only*, the hazard rate is constant over time.

This illustrates the difference in hazard rate and failure probability density - as the number of systems surviving at time 

t
>
0
{\displaystyle t>0}
![{\displaystyle t>0}](https://wikimedia.org/api/rest_v1/media/math/render/svg/29a2960e88369263fe3cfe00ccbfeb83daee212a) gradually reduces, the total failure rate also reduces, but the hazard rate **remains constant**. In other words, the probabilities of each individual system failing do not change over time as the systems age - they are "[memory-less](/wiki/Memorylessness "Memorylessness")".

### Other models

[[edit](/w/index.php?title=Failure_rate&veaction=edit&section=7 "Edit section: Other models") | [edit source](/w/index.php?title=Failure_rate&action=edit&section=7 "Edit section's source code: Other models")]

[![](//thumb.wikimedia.org/wikipedia/commons/thumb/1/1b/Loglogistichaz.svg/330px-Loglogistichaz.svg.png?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail)](/wiki/File:Loglogistichaz.svg)

Hazard function 

h
(
t
)
{\displaystyle h(t)}
![{\displaystyle h(t)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/66abbb8ae1d9f30bb529739b109e1e5bbe83c626) plotted for a selection of [log-logistic distributions](/wiki/Log-logistic_distribution "Log-logistic distribution"), any of which could be used as a hazard rate, depending on the system under study

For many systems, a constant hazard function may not be a realistic approximation; the chance of failure of an individual component may depend on its age. Therefore, other distributions are often used.

For example, the [deterministic distribution](/wiki/Deterministic_distribution "Deterministic distribution") increases hazard rate over time (for systems where wear-out is the most important factor), while the [Pareto distribution](/wiki/Pareto_distribution "Pareto distribution") decreases it (for systems where early-life failures are more common). The commonly used [Weibull distribution](/wiki/Weibull_distribution "Weibull distribution") combines both of these effects, as do the [log-normal](/wiki/Log-normal_distribution "Log-normal distribution") and [hypertabastic](/wiki/Hypertabastic_survival_models "Hypertabastic survival models") distributions.

After modelling a given distribution and parameters for 

h
(
t
)
{\displaystyle h(t)}
![{\displaystyle h(t)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/66abbb8ae1d9f30bb529739b109e1e5bbe83c626), the failure probability density 

f
(
t
)
{\displaystyle f(t)}
![{\displaystyle f(t)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/5bf044fe2fbfc4bd8d6d7230f4108430263f9fd6) and cumulative failure distribution 

F
(
t
)
{\displaystyle F(t)}
![{\displaystyle F(t)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/5b57ed3bbf501fb3c7f4bc5c4eafa96bb9e32165) can be predicted using the given equations.

## Measuring failure rate

[[edit](/w/index.php?title=Failure_rate&veaction=edit&section=8 "Edit section: Measuring failure rate") | [edit source](/w/index.php?title=Failure_rate&action=edit&section=8 "Edit section's source code: Measuring failure rate")]

Failure rate data can be obtained in several ways. The most common means are:

Estimation
:   From field failure rate reports, statistical analysis techniques can be used to estimate failure rates. For accurate failure rates the analyst must have a good understanding of equipment operation, procedures for data collection, the key environmental variables impacting failure rates, how the equipment is used at the system level, and how the failure data will be used by system designers.

Historical data about the device or system under consideration
:   Many organizations maintain internal databases of failure information on the devices or systems that they produce, which can be used to calculate failure rates for those devices or systems. For new devices or systems, the historical data for similar devices or systems can serve as a useful estimate.

Government and commercial failure rate data
:   Handbooks of failure rate data for various components are available from government and commercial sources. MIL-HDBK-217F, *Reliability Prediction of Electronic Equipment*, is a [military standard](/wiki/United_States_Military_Standard "United States Military Standard") that provides failure rate data for many military electronic components. Several failure rate data sources are available commercially that focus on commercial components, including some non-electronic components.

Prediction
:   Time lag is one of the serious drawbacks of all failure rate estimations. Often by the time the failure rate data are available, the devices under study have become obsolete. Due to this drawback, failure-rate prediction methods have been developed. These methods may be used on newly designed devices to predict the device's failure rates and failure modes. Two approaches have become well known, Cycle Testing and FMEDA.

Life Testing
:   The most accurate source of data is to test samples of the actual devices or systems in order to generate failure data. This is often prohibitively expensive or impractical, so that the previous data sources are often used instead.

Cycle Testing
:   Mechanical movement is the predominant failure mechanism causing mechanical and electromechanical devices to wear out. For many devices, the wear-out failure point is measured by the number of cycles performed before the device fails, and can be discovered by cycle testing. In cycle testing, a device is cycled as rapidly as practical until it fails. When a collection of these devices are tested, the test will run until 10% of the units fail dangerously.

FMEDA
:   [Failure modes, effects, and diagnostic analysis](/wiki/Failure_modes,_effects,_and_diagnostic_analysis "Failure modes, effects, and diagnostic analysis") (FMEDA) is a systematic analysis technique to obtain subsystem / product level failure rates, failure modes and design strength. The FMEDA technique considers:

- All components of a design,
- The functionality of each component,
- The failure modes of each component,
- The effect of each component failure mode on the product functionality,
- The ability of any automatic diagnostics to detect the failure,
- The design strength (de-rating, safety factors) and
- The operational profile (environmental stress factors).

Given a component database calibrated with field failure data that is reasonably accurate,[[4]](#cite_note-4) the method can predict product level failure rate and failure mode data for a given application. The predictions have been shown to be more accurate[[5]](#cite_note-5) than field warranty return analysis or even typical field failure analysis given that these methods depend on reports that typically do not have sufficient detail information in failure records.[[6]](#cite_note-6)

## Examples

[[edit](/w/index.php?title=Failure_rate&veaction=edit&section=9 "Edit section: Examples") | [edit source](/w/index.php?title=Failure_rate&action=edit&section=9 "Edit section's source code: Examples")]

### Decreasing failure rates

[[edit](/w/index.php?title=Failure_rate&veaction=edit&section=10 "Edit section: Decreasing failure rates") | [edit source](/w/index.php?title=Failure_rate&action=edit&section=10 "Edit section's source code: Decreasing failure rates")]

A decreasing failure rate describes cases where early-life failures are common[[7]](#cite_note-7) and corresponds to the situation where 

h
(
t
)
{\displaystyle h(t)}
![{\displaystyle h(t)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/66abbb8ae1d9f30bb529739b109e1e5bbe83c626) is a [decreasing function](/wiki/Decreasing_function "Decreasing function").

This can describe, for example, the period of [infant mortality](/wiki/Infant_mortality "Infant mortality") in humans, or the early failure of [transistors](/wiki/Transistor "Transistor") due to manufacturing defects.

Decreasing failure rates have been found in the lifetimes of spacecraft - Baker and Baker commenting that "those spacecraft that last, last on and on."[[8]](#cite_note-8)[[9]](#cite_note-9)

The hazard rate of aircraft air conditioning systems was found to have an exponentially decreasing distribution.[[10]](#cite_note-proschan-10)

### Renewal processes

[[edit](/w/index.php?title=Failure_rate&veaction=edit&section=11 "Edit section: Renewal processes") | [edit source](/w/index.php?title=Failure_rate&action=edit&section=11 "Edit section's source code: Renewal processes")]

In special processes called [renewal processes](/wiki/Renewal_process "Renewal process"), where the time to recover from failure can be neglected, the likelihood of failure remains constant with respect to time.

For a [renewal process](/wiki/Renewal_process "Renewal process") with DFR renewal function, inter-renewal times are concave.[*[clarification needed](/wiki/Wikipedia:Please_clarify "Wikipedia:Please clarify")*][[11]](#cite_note-brown1980-11)[[12]](#cite_note-shanthikumar-12) Brown conjectured the converse, that DFR is also necessary for the inter-renewal times to be concave,[[13]](#cite_note-13) however it has been shown that this conjecture holds neither in the discrete case[[12]](#cite_note-shanthikumar-12) nor in the continuous case.[[14]](#cite_note-14)

### Coefficient of variation

[[edit](/w/index.php?title=Failure_rate&veaction=edit&section=12 "Edit section: Coefficient of variation") | [edit source](/w/index.php?title=Failure_rate&action=edit&section=12 "Edit section's source code: Coefficient of variation")]

When the failure rate is decreasing the [coefficient of variation](/wiki/Coefficient_of_variation "Coefficient of variation") is ⩾ 1, and when the failure rate is increasing the coefficient of variation is ⩽ 1.[*[clarification needed](/wiki/Wikipedia:Please_clarify "Wikipedia:Please clarify")*][[15]](#cite_note-15) Note that this result only holds when the failure rate is defined for all t ⩾ 0[[16]](#cite_note-16) and that the converse result (coefficient of variation determining nature of failure rate) does not hold.

### Units

[[edit](/w/index.php?title=Failure_rate&veaction=edit&section=13 "Edit section: Units") | [edit source](/w/index.php?title=Failure_rate&action=edit&section=13 "Edit section's source code: Units")]

Failure rates can be expressed using any measure of time, but **hours** is the most common unit in practice. Other units, such as miles, revolutions, etc., can also be used in place of "time" units.

Failure rates are often expressed in [engineering notation](/wiki/Engineering_notation "Engineering notation") as **Failures Per Million Hours** (**FPMH**), or 10−6, especially for individual components, since their failure rates are often very low.

The **Failures In Time** (**FIT**) rate of a device is the number of failures that can be expected in one billion (109) device-hours of operation[[17]](#cite_note-17)
(e.g. 1,000 devices for 1,000,000 hours, or 1,000,000 devices for 1,000 hours each, or some other combination). This term is used particularly by the [semiconductor](/wiki/Semiconductor "Semiconductor") industry.

### Combinations of failure types

[[edit](/w/index.php?title=Failure_rate&veaction=edit&section=14 "Edit section: Combinations of failure types") | [edit source](/w/index.php?title=Failure_rate&action=edit&section=14 "Edit section's source code: Combinations of failure types")]

If a complex system consists of many parts, and the failure of any single part means the failure of the entire system, and the chance of failure for each part is [conditionally independent](/wiki/Conditionally_independent "Conditionally independent") of the failure of any other part, then the total failure rate is simply the sum of the individual failure rates of its parts

:   λ

    S
    =

    λ

    P
    1
    +

    λ

    P
    2
    +
    …
    {\displaystyle \lambda \_{S}=\lambda \_{P1}+\lambda \_{P2}+\ldots }
    ![{\displaystyle \lambda _{S}=\lambda _{P1}+\lambda _{P2}+\ldots }](https://wikimedia.org/api/rest_v1/media/math/render/svg/bf373b58479b0026133e3cfdddb26b3188d8df2e)

however, this assumes that the failure rate 

λ
(
t
)
{\displaystyle \lambda (t)}
![{\displaystyle \lambda (t)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/e0e1cc2c2f9e6d8b22c0da0bb5fe8f0f47791e4a) is constant, and that the units are consistent (e.g. failures per million hours), and not expressed as a ratio or as probability densities. This is useful to estimate the failure rate of a system when individual components or subsystems have already been tested.[[18]](#cite_note-18)[[19]](#cite_note-19)

When adding "redundant" components to eliminate a [single point of failure](/wiki/Single_point_of_failure "Single point of failure"), the quantity of interest is not the sum of individual failure rates but rather the "mission failure" rate, or the "mean time between critical failures" (MTBCF).[[20]](#cite_note-20)

Combining failure or hazard rates that are time-dependent is more complicated. For example, mixtures of Decreasing Failure Rate (DFR) variables are also DFR.[[11]](#cite_note-brown1980-11) Mixtures of [exponentially distributed](/wiki/Exponential_distribution "Exponential distribution") failure rates are [hyperexponentially distributed](/wiki/Hyperexponential_distribution "Hyperexponential distribution").

### Simple example

[[edit](/w/index.php?title=Failure_rate&veaction=edit&section=15 "Edit section: Simple example") | [edit source](/w/index.php?title=Failure_rate&action=edit&section=15 "Edit section's source code: Simple example")]

Suppose it is desired to estimate the failure rate of a certain component. Ten identical components are each tested until they either fail or reach 1,000 hours, at which time the test is terminated. A total of 7,502 component-hours of testing is performed, and 6 failures are recorded.

The *estimated* failure rate is:

:   6

     failures

    7502

     hours
    =
    0.0007998

    failures
    hour
    {\displaystyle {\frac {6{\text{ failures}}}{7502{\text{ hours}}}}=0.0007998\,{\frac {\text{failures}}{\text{hour}}}}
    ![{\displaystyle {\frac {6{\text{ failures}}}{7502{\text{ hours}}}}=0.0007998\,{\frac {\text{failures}}{\text{hour}}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/6630363c85f3301f9959a84491ef9795f2048397)

which could also be expressed as a MTBF of 1,250 hours, or approximately 800 failures for every million hours of operation.

## See also

[[edit](/w/index.php?title=Failure_rate&veaction=edit&section=16 "Edit section: See also") | [edit source](/w/index.php?title=Failure_rate&action=edit&section=16 "Edit section's source code: See also")]

.mw-parser-output .portalbox{padding:0;margin:0.5em 0;display:table;box-sizing:border-box;max-width:175px;list-style:none}.mw-parser-output .portalborder{border:1px solid var(--border-color-base,#a2a9b1);padding:0.1em;background:var(--background-color-neutral-subtle,#f8f9fa)}.mw-parser-output .portalbox-entry{display:table-row;font-size:85%;line-height:110%;height:1.9em;font-style:italic;font-weight:bold}.mw-parser-output .portalbox-image{display:table-cell;padding:0.2em;vertical-align:middle;text-align:center}.mw-parser-output .portalbox-link{display:table-cell;padding:0.2em 0.2em 0.2em 0.3em;vertical-align:middle}@media(min-width:640px){.mw-parser-output .portalleft{margin:0.5em 1em 0.5em 0}.mw-parser-output .portalright{clear:right;float:right;margin:0.5em 0 0.5em 1em}}

- [![icon](//thumb.wikimedia.org/wikipedia/commons/thumb/9/9e/Square_root_of_x.svg/40px-Square_root_of_x.svg.png?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail)](/wiki/File:Square_root_of_x.svg)[Mathematics portal](/wiki/Portal:Mathematics "Portal:Mathematics")

.mw-parser-output .div-col{margin-top:0.3em;column-width:30em}.mw-parser-output .div-col-small{font-size:90%}.mw-parser-output .div-col-rules{column-rule:1px solid #aaa}.mw-parser-output .div-col dl,.mw-parser-output .div-col ol,.mw-parser-output .div-col ul{margin-top:0}.mw-parser-output .div-col li,.mw-parser-output .div-col dd{page-break-inside:avoid;break-inside:avoid-column}

- [Annualized failure rate](/wiki/Annualized_failure_rate "Annualized failure rate")
- [Burn-in](/wiki/Burn-in "Burn-in")
- [Failure](/wiki/Failure "Failure")
- [Failure mode](/wiki/Failure_mode "Failure mode")
- [Failure modes, effects, and diagnostic analysis](/wiki/Failure_modes,_effects,_and_diagnostic_analysis "Failure modes, effects, and diagnostic analysis")
- [Force of mortality](/wiki/Force_of_mortality "Force of mortality")
- [Frequency of exceedance](/wiki/Frequency_of_exceedance "Frequency of exceedance")
- [Reliability engineering](/wiki/Reliability_engineering "Reliability engineering")
- [Reliability theory](/wiki/Reliability_theory "Reliability theory")
- [Reliability theory of aging and longevity](/wiki/Reliability_theory_of_aging_and_longevity "Reliability theory of aging and longevity")
- [Survival analysis](/wiki/Survival_analysis "Survival analysis")
- [Weibull distribution](/wiki/Weibull_distribution "Weibull distribution")

## References

[[edit](/w/index.php?title=Failure_rate&veaction=edit&section=17 "Edit section: References") | [edit source](/w/index.php?title=Failure_rate&action=edit&section=17 "Edit section's source code: References")]

.mw-parser-output .reflist-columns-2{column-width:30em}.mw-parser-output .reflist-columns-3{column-width:25em}body.skin-vector-2022 .mw-parser-output .reflist-columns-2{column-width:27em}body.skin-vector-2022 .mw-parser-output .reflist-columns-3{column-width:22.5em}.mw-parser-output .references[data-mw-group=upper-alpha]{list-style-type:upper-alpha}.mw-parser-output .references[data-mw-group=upper-roman]{list-style-type:upper-roman}.mw-parser-output .references[data-mw-group=lower-alpha]{list-style-type:lower-alpha}.mw-parser-output .references[data-mw-group=lower-greek]{list-style-type:lower-greek}.mw-parser-output .references[data-mw-group=lower-roman]{list-style-type:lower-roman}.mw-parser-output div.reflist-liststyle-upper-alpha .references{list-style-type:upper-alpha}.mw-parser-output div.reflist-liststyle-upper-roman .references{list-style-type:upper-roman}.mw-parser-output div.reflist-liststyle-lower-alpha .references{list-style-type:lower-alpha}.mw-parser-output div.reflist-liststyle-lower-greek .references{list-style-type:lower-greek}.mw-parser-output div.reflist-liststyle-lower-roman .references{list-style-type:lower-roman}

1. **[^](#cite_ref-macdiarmid_1-0)** \*
   .mw-parser-output cite.citation{font-style:inherit;word-wrap:break-word}.mw-parser-output .citation q{quotes:"\"""\"""'""'"}.mw-parser-output .citation:target{background-color:rgba(0,127,255,0.133)}.mw-parser-output .id-lock-free.id-lock-free a{background:url("//upload.wikimedia.org/wikipedia/commons/6/65/Lock-green.svg")right 0.1em center/9px no-repeat}.mw-parser-output .id-lock-limited.id-lock-limited a,.mw-parser-output .id-lock-registration.id-lock-registration a{background:url("//upload.wikimedia.org/wikipedia/commons/d/d6/Lock-gray-alt-2.svg")right 0.1em center/9px no-repeat}.mw-parser-output .id-lock-subscription.id-lock-subscription a{background:url("//upload.wikimedia.org/wikipedia/commons/a/aa/Lock-red-alt-2.svg")right 0.1em center/9px no-repeat}.mw-parser-output .cs1-ws-icon a{background:url("//upload.wikimedia.org/wikipedia/commons/4/4c/Wikisource-logo.svg")right 0.1em center/12px no-repeat}body:not(.skin-timeless):not(.skin-minerva) .mw-parser-output .id-lock-free a,body:not(.skin-timeless):not(.skin-minerva) .mw-parser-output .id-lock-limited a,body:not(.skin-timeless):not(.skin-minerva) .mw-parser-output .id-lock-registration a,body:not(.skin-timeless):not(.skin-minerva) .mw-parser-output .id-lock-subscription a,body:not(.skin-timeless):not(.skin-minerva) .mw-parser-output .cs1-ws-icon a{background-size:contain;padding:0 1em 0 0}.mw-parser-output .cs1-code{color:inherit;background:inherit;border:none;padding:inherit}.mw-parser-output .cs1-hidden-error{display:none;color:var(--color-error,#bf3c2c)}.mw-parser-output .cs1-visible-error{color:var(--color-error,#bf3c2c)}.mw-parser-output .cs1-maint{display:none;color:#085;margin-left:0.3em}.mw-parser-output .cs1-kern-left{padding-left:0.2em}.mw-parser-output .cs1-kern-right{padding-right:0.2em}.mw-parser-output .citation .mw-selflink{font-weight:inherit}@media screen{.mw-parser-output .cs1-format{font-size:95%}html.skin-theme-clientpref-night .mw-parser-output .cs1-maint{color:#18911f}}@media screen and (prefers-color-scheme:dark){html.skin-theme-clientpref-os .mw-parser-output .cs1-maint{color:#18911f}}MacDiarmid, Preston; Morris, Seymour; et al. (n.d.). *Reliability Toolkit* (Commercial Practices ed.). Rome, New York: Reliability Analysis Center and Rome Laboratory. pp. 35–39.
2. ^ [***a***](#cite_ref-todinov_2-0) [***b***](#cite_ref-todinov_2-1) Todinov, MT (2007). "Chapter 2.2 HAZARD RATE AND TIME TO FAILURE DISTRIBUTION". *Risk-Based Reliability Analysis and Generic Principles for Risk Reduction*.
3. **[^](#cite_ref-3)** Wang, Shaoping (2016). "Chapter 3.3.1.3: Failure Rate λ(t)". *Comprehensive Reliability Design of Aircraft Hydraulic System*.
4. **[^](#cite_ref-4)** [*Electrical & Mechanical Component Reliability Handbook*](http://www.exida.com). exida. 2006.
5. **[^](#cite_ref-5)** Goble, William M.; Iwan van Beurden (2014). *Combining field failure data with new instrument design margins to predict failure rates for SIS Verification*. Proceedings of the 2014 International Symposium - BEYOND REGULATORY COMPLIANCE, MAKING SAFETY SECOND NATURE, Hilton College Station-Conference Center, College Station, Texas.
6. **[^](#cite_ref-6)** W. M. Goble, "Field Failure Data – the Good, the Bad and the Ugly," exida, Sellersville, PA [[1]](http://www.exida.com/resources/whitepapers.asp)
7. **[^](#cite_ref-7)** Finkelstein, Maxim (2008). "Introduction". *Failure Rate Modelling for Reliability and Risk*. Springer Series in Reliability Engineering. pp. 1–84. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1007/978-1-84800-986-8\_1](https://doi.org/10.1007%2F978-1-84800-986-8_1). [ISBN](/wiki/ISBN_(identifier) "ISBN (identifier)") [978-1-84800-985-1](/wiki/Special:BookSources/978-1-84800-985-1 "Special:BookSources/978-1-84800-985-1").
8. **[^](#cite_ref-8)** Baker, J. C.; Baker, G. A. S. . (1980). "Impact of the space environment on spacecraft lifetimes". *Journal of Spacecraft and Rockets*. **17** (5): 479. [Bibcode](/wiki/Bibcode_(identifier) "Bibcode (identifier)"):[1980JSpRo..17..479B](https://ui.adsabs.harvard.edu/abs/1980JSpRo..17..479B). [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.2514/3.28040](https://doi.org/10.2514%2F3.28040).
9. **[^](#cite_ref-9)** Saleh, Joseph Homer; Castet, Jean-François (2011). "On Time, Reliability, and Spacecraft". *Spacecraft Reliability and Multi-State Failures*. p. 1. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1002/9781119994077.ch1](https://doi.org/10.1002%2F9781119994077.ch1). [ISBN](/wiki/ISBN_(identifier) "ISBN (identifier)") [9781119994077](/wiki/Special:BookSources/9781119994077 "Special:BookSources/9781119994077").
10. **[^](#cite_ref-proschan_10-0)** Proschan, F. (1963). "Theoretical Explanation of Observed Decreasing Failure Rate". *Technometrics*. **5** (3): 375–383. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1080/00401706.1963.10490105](https://doi.org/10.1080%2F00401706.1963.10490105). [JSTOR](/wiki/JSTOR_(identifier) "JSTOR (identifier)") [1266340](https://www.jstor.org/stable/1266340).
11. ^ [***a***](#cite_ref-brown1980_11-0) [***b***](#cite_ref-brown1980_11-1) Brown, M. (1980). ["Bounds, Inequalities, and Monotonicity Properties for Some Specialized Renewal Processes"](https://doi.org/10.1214%2Faop%2F1176994773). *The Annals of Probability*. **8** (2): 227–240. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1214/aop/1176994773](https://doi.org/10.1214%2Faop%2F1176994773). [JSTOR](/wiki/JSTOR_(identifier) "JSTOR (identifier)") [2243267](https://www.jstor.org/stable/2243267).
12. ^ [***a***](#cite_ref-shanthikumar_12-0) [***b***](#cite_ref-shanthikumar_12-1) Shanthikumar, J. G. (1988). ["DFR Property of First-Passage Times and its Preservation Under Geometric Compounding"](https://doi.org/10.1214%2Faop%2F1176991910). *The Annals of Probability*. **16** (1): 397–406. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1214/aop/1176991910](https://doi.org/10.1214%2Faop%2F1176991910). [JSTOR](/wiki/JSTOR_(identifier) "JSTOR (identifier)") [2243910](https://www.jstor.org/stable/2243910).
13. **[^](#cite_ref-13)** Brown, M. (1981). ["Further Monotonicity Properties for Specialized Renewal Processes"](https://doi.org/10.1214%2Faop%2F1176994317). *The Annals of Probability*. **9** (5): 891–895. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1214/aop/1176994317](https://doi.org/10.1214%2Faop%2F1176994317). [JSTOR](/wiki/JSTOR_(identifier) "JSTOR (identifier)") [2243747](https://www.jstor.org/stable/2243747).
14. **[^](#cite_ref-14)** Yu, Y. (2011). "Concave renewal functions do not imply DFR interrenewal times". *Journal of Applied Probability*. **48** (2): 583–588. [arXiv](/wiki/ArXiv_(identifier) "ArXiv (identifier)"):[1009.2463](https://arxiv.org/abs/1009.2463). [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1239/jap/1308662647](https://doi.org/10.1239%2Fjap%2F1308662647). [S2CID](/wiki/S2CID_(identifier) "S2CID (identifier)") [26570923](https://api.semanticscholar.org/CorpusID:26570923).
15. **[^](#cite_ref-15)** [Wierman, A.](/wiki/Adam_Wierman "Adam Wierman"); Bansal, N.; [Harchol-Balter, M.](/wiki/Mor_Harchol-Balter "Mor Harchol-Balter") (2004). ["A note on comparing response times in the M/GI/1/FB and M/GI/1/PS queues"](http://users.cms.caltech.edu/~adamw/papers/fbnote.pdf) (PDF). *Operations Research Letters*. **32**: 73–76. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1016/S0167-6377(03)00061-0](https://doi.org/10.1016%2FS0167-6377%2803%2900061-0).
16. **[^](#cite_ref-16)** Gautam, Natarajan (2012). *Analysis of Queues: Methods and Applications*. CRC Press. p. 703. [ISBN](/wiki/ISBN_(identifier) "ISBN (identifier)") [978-1439806586](/wiki/Special:BookSources/978-1439806586 "Special:BookSources/978-1439806586").
17. **[^](#cite_ref-17)** 
    Xin Li; Michael C. Huang; Kai Shen; Lingkun Chu.
    ["A Realistic Evaluation of Memory Hardware Errors and Software System Susceptibility"](http://www.cs.rochester.edu/~kshen/papers/usenix2010-li.pdf).
    2010.
    p. 6.
18. **[^](#cite_ref-18)** 
    ["Reliability Basics"](http://www.weibull.com/hotwire/issue108/relbasics108.htm).
    2010.
19. **[^](#cite_ref-19)** Vita Faraci.
    ["Calculating Failure Rates of Series/Parallel Networks"](http://src.alionscience.com/pdf/1Q2006.pdf) [Archived](https://web.archive.org/web/20160303224453/http://src.alionscience.com/pdf/1Q2006.pdf) 2016-03-03 at the [Wayback Machine](/wiki/Wayback_Machine "Wayback Machine").
    2006.
20. **[^](#cite_ref-20)** 
    ["Mission Reliability and Logistics Reliability: A Design Paradox"](https://www.quanterion.com/mission-reliability-and-logistics-reliability-a-design-paradox/).

## Further reading

[[edit](/w/index.php?title=Failure_rate&veaction=edit&section=18 "Edit section: Further reading") | [edit source](/w/index.php?title=Failure_rate&action=edit&section=18 "Edit section's source code: Further reading")]

- Goble, William M. (2018), *Safety Instrumented System Design: Techniques and Design Verification*, Research Triangle Park, NC: International Society of Automation
- Blanchard, Benjamin S. (1992). *Logistics Engineering and Management* (Fourth ed.). Englewood Cliffs, New Jersey: Prentice-Hall. pp. 26–32. [ISBN](/wiki/ISBN_(identifier) "ISBN (identifier)") [0135241170](/wiki/Special:BookSources/0135241170 "Special:BookSources/0135241170").
- Ebeling, Charles E. (1997). *An Introduction to Reliability and Maintainability Engineering*. Boston: McGraw-Hill. pp. 23–32. [ISBN](/wiki/ISBN_(identifier) "ISBN (identifier)") [0070188521](/wiki/Special:BookSources/0070188521 "Special:BookSources/0070188521").
- [Federal Standard 1037C](/wiki/Federal_Standard_1037C "Federal Standard 1037C")
- Kapur, K. C.; Lamberson, L. R. (1977). *Reliability in Engineering Design*. New York: John Wiley & Sons. pp. 8–30. [ISBN](/wiki/ISBN_(identifier) "ISBN (identifier)") [0471511919](/wiki/Special:BookSources/0471511919 "Special:BookSources/0471511919").
- Knowles, D. I. (1995). "Should We Move Away From 'Acceptable Failure Rate'?". *Communications in Reliability Maintainability and Supportability*. **2** (1). International RMS Committee, USA: 23.
- [Modarres, M.](/wiki/Mohammad_Modarres "Mohammad Modarres"); Kaminskiy, M.; Krivtsov, V. (2010). *[Reliability Engineering and Risk Analysis: A Practical Guide](/wiki/Reliability_Engineering_and_Risk_Analysis:_A_Practical_Guide "Reliability Engineering and Risk Analysis: A Practical Guide")* (2nd ed.). CRC Press. [ISBN](/wiki/ISBN_(identifier) "ISBN (identifier)") [9780849392474](/wiki/Special:BookSources/9780849392474 "Special:BookSources/9780849392474").
- Mondro, Mitchell J. (June 2002). ["Approximation of Mean Time Between Failure When a System has Periodic Maintenance"](https://web.archive.org/web/20081217175139/http://www.mitre.org/work/best_papers/02/mondro_approx/mondro_approx.pdf) (PDF). *IEEE Transactions on Reliability*. **51** (2): 166–167. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1109/TR.2002.1011521](https://doi.org/10.1109%2FTR.2002.1011521). Archived from [the original](http://www.mitre.org/work/best_papers/02/mondro_approx/mondro_approx.pdf) (PDF) on 2008-12-17. Retrieved 2008-07-14.
- Rausand, M.; Hoyland, A. (2004). *System Reliability Theory; Models, Statistical methods, and Applications*. New York: John Wiley & Sons. [ISBN](/wiki/ISBN_(identifier) "ISBN (identifier)") [047147133X](/wiki/Special:BookSources/047147133X "Special:BookSources/047147133X").
- Turner, T.; Hockley, C.; Burdaky, R. (1997). *The Customer Needs A Maintenance-Free Operating Period*. Leatherhead, Surrey, UK: [ERA Technology Ltd](/wiki/ERA_Technology_Ltd "ERA Technology Ltd"). `{{cite book}}`: `|work=` ignored ([help](/wiki/Help:CS1_errors#periodical_ignored "Help:CS1 errors"))
- U.S. Department of Defense, (1991) *Military Handbook, “Reliability Prediction of Electronic Equipment, MIL-HDBK-217F, 2*

## External links

[[edit](/w/index.php?title=Failure_rate&veaction=edit&section=19 "Edit section: External links") | [edit source](/w/index.php?title=Failure_rate&action=edit&section=19 "Edit section's source code: External links")]

- [*Fault Tolerant Computing in Industrial Automation*](http://lamspeople.epfl.ch/kirrmann/Pubs/FaultTolerance/Fault_Tolerance_Tutorial_HK.pdf) [Archived](https://web.archive.org/web/20140326192930/http://lamspeople.epfl.ch/kirrmann/Pubs/FaultTolerance/Fault_Tolerance_Tutorial_HK.pdf) 2014-03-26 at the [Wayback Machine](/wiki/Wayback_Machine "Wayback Machine") by Hubert Kirrmann, ABB Research Center, Switzerland

.mw-parser-output .hlist dl,.mw-parser-output .hlist ol,.mw-parser-output .hlist ul{margin:0;padding:0}.mw-parser-output .hlist dd,.mw-parser-output .hlist dt,.mw-parser-output .hlist li{margin:0;display:inline}.mw-parser-output .hlist.inline,.mw-parser-output .hlist.inline dl,.mw-parser-output .hlist.inline ol,.mw-parser-output .hlist.inline ul,.mw-parser-output .hlist dl dl,.mw-parser-output .hlist dl ol,.mw-parser-output .hlist dl ul,.mw-parser-output .hlist ol dl,.mw-parser-output .hlist ol ol,.mw-parser-output .hlist ol ul,.mw-parser-output .hlist ul dl,.mw-parser-output .hlist ul ol,.mw-parser-output .hlist ul ul{display:inline}.mw-parser-output .hlist .mw-empty-li{display:none}.mw-parser-output .hlist dt::after{content:": "}.mw-parser-output .hlist dd::after,.mw-parser-output .hlist li::after{content:"\a0 · ";font-weight:bold}.mw-parser-output .hlist dd:last-child::after,.mw-parser-output .hlist dt:last-child::after,.mw-parser-output .hlist li:last-child::after{content:none}.mw-parser-output .hlist dd dd:first-child::before,.mw-parser-output .hlist dd dt:first-child::before,.mw-parser-output .hlist dd li:first-child::before,.mw-parser-output .hlist dt dd:first-child::before,.mw-parser-output .hlist dt dt:first-child::before,.mw-parser-output .hlist dt li:first-child::before,.mw-parser-output .hlist li dd:first-child::before,.mw-parser-output .hlist li dt:first-child::before,.mw-parser-output .hlist li li:first-child::before{content:" (";font-weight:normal}.mw-parser-output .hlist dd dd:last-child::after,.mw-parser-output .hlist dd dt:last-child::after,.mw-parser-output .hlist dd li:last-child::after,.mw-parser-output .hlist dt dd:last-child::after,.mw-parser-output .hlist dt dt:last-child::after,.mw-parser-output .hlist dt li:last-child::after,.mw-parser-output .hlist li dd:last-child::after,.mw-parser-output .hlist li dt:last-child::after,.mw-parser-output .hlist li li:last-child::after{content:")";font-weight:normal}.mw-parser-output .hlist ol{counter-reset:listitem}.mw-parser-output .hlist ol>li{counter-increment:listitem}.mw-parser-output .hlist ol>li::before{content:" "counter(listitem)"\a0 "}.mw-parser-output .hlist dd ol>li:first-child::before,.mw-parser-output .hlist dt ol>li:first-child::before,.mw-parser-output .hlist li ol>li:first-child::before{content:" ("counter(listitem)"\a0 "}.mw-parser-output .navbox{box-sizing:border-box;border:1px solid #a2a9b1;width:100%;clear:both;font-size:88%;text-align:center;padding:1px;margin:1em auto 0}.mw-parser-output .navbox .navbox{margin-top:0}.mw-parser-output .navbox+.navbox-styles+.navbox,.mw-parser-output .navbox+span.mw-empty-elt+.navbox-styles+.navbox{margin-top:-1px}.mw-parser-output .navbox-inner,.mw-parser-output .navbox-subgroup{width:100%}.mw-parser-output .navbox-group,.mw-parser-output .navbox-title,.mw-parser-output .navbox-abovebelow{padding:0.25em 1em;line-height:1.5em;text-align:center}.mw-parser-output .navbox-group{white-space:nowrap;text-align:right}.mw-parser-output .navbox,.mw-parser-output .navbox-subgroup{background-color:#fdfdfd;color:inherit}.mw-parser-output .navbox-list{line-height:1.5em;border-color:#fdfdfd}.mw-parser-output .navbox-list-with-group{text-align:left;border-left-width:2px;border-left-style:solid}.mw-parser-output tr+tr>.navbox-abovebelow,.mw-parser-output tr+tr>.navbox-group,.mw-parser-output tr+tr>.navbox-image,.mw-parser-output tr+tr>.navbox-list{border-top:2px solid #fdfdfd}.mw-parser-output .navbox-title{background-color:#ccf;color:inherit}.mw-parser-output .navbox-abovebelow,.mw-parser-output .navbox-group,.mw-parser-output .navbox-subgroup .navbox-title{background-color:#ddf;color:inherit}.mw-parser-output .navbox-subgroup .navbox-group,.mw-parser-output .navbox-subgroup .navbox-abovebelow{background-color:#e6e6ff;color:inherit}.mw-parser-output .navbox-even{background-color:#f7f7f7;color:inherit}.mw-parser-output .navbox-odd{background-color:transparent;color:inherit}.mw-parser-output .navbox .hlist td dl,.mw-parser-output .navbox .hlist td ol,.mw-parser-output .navbox .hlist td ul,.mw-parser-output .navbox td.hlist dl,.mw-parser-output .navbox td.hlist ol,.mw-parser-output .navbox td.hlist ul{padding:0.125em 0}.mw-parser-output .navbox .navbar{display:block;font-size:100%}.mw-parser-output .navbox-title .navbar{float:left;text-align:left;margin-right:0.5em}body.skin--responsive .mw-parser-output .navbox-image img{max-width:none!important}@media print{body.ns-0 .mw-parser-output .navbox{display:none!important}}

| .mw-parser-output .navbar{display:inline;font-size:88%;font-weight:normal}.mw-parser-output .navbar-collapse{float:left;text-align:left}.mw-parser-output .navbar-boxtext{word-spacing:0}.mw-parser-output .navbar ul{display:inline-block;white-space:nowrap;line-height:inherit}.mw-parser-output .navbar-brackets::before{margin-right:-0.125em;content:"[ "}.mw-parser-output .navbar-brackets::after{margin-left:-0.125em;content:" ]"}.mw-parser-output .navbar li{word-spacing:-0.125em}.mw-parser-output .navbar a>span,.mw-parser-output .navbar a>abbr{text-decoration:inherit}.mw-parser-output .navbar-mini abbr{font-variant:small-caps;border-bottom:none;text-decoration:none;cursor:inherit}.mw-parser-output .navbar-ct-full{font-size:114%;margin:0 7em}.mw-parser-output .navbar-ct-mini{font-size:114%;margin:0 4em}html.skin-theme-clientpref-night .mw-parser-output .navbar li a abbr{color:var(--color-base)!important}@media(prefers-color-scheme:dark){html.skin-theme-clientpref-os .mw-parser-output .navbar li a abbr{color:var(--color-base)!important}}@media print{.mw-parser-output .navbar{display:none!important}} - [v](/wiki/Template:Statistics "Template:Statistics") - [t](/wiki/Template_talk:Statistics "Template talk:Statistics") - [e](/wiki/Special:EditPage/Template:Statistics "Special:EditPage/Template:Statistics")  [Statistics](/wiki/Statistics "Statistics") | |
| --- | --- |
| - [Outline](/wiki/Outline_of_statistics "Outline of statistics") - [Index](/wiki/List_of_statistics_articles "List of statistics articles") | |
| | [Descriptive statistics](/wiki/Descriptive_statistics "Descriptive statistics") | | | --- | --- | | |  |  |  |  |  |  |  |  | | --- | --- | --- | --- | --- | --- | --- | --- | | [Continuous data](/wiki/Continuous_probability_distribution "Continuous probability distribution") | |  |  | | --- | --- | | [Center](/wiki/Central_tendency "Central tendency") | - [Mean](/wiki/Mean "Mean")   - [Arithmetic](/wiki/Arithmetic_mean "Arithmetic mean")   - [Arithmetic-Geometric](/wiki/Arithmetic%E2%80%93geometric_mean "Arithmetic–geometric mean")   - [Contraharmonic](/wiki/Contraharmonic_mean "Contraharmonic mean")   - [Cubic](/wiki/Cubic_mean "Cubic mean")   - [Generalized/power](/wiki/Generalized_mean "Generalized mean")   - [Geometric](/wiki/Geometric_mean "Geometric mean")   - [Harmonic](/wiki/Harmonic_mean "Harmonic mean")   - [Heronian](/wiki/Heronian_mean "Heronian mean")   - [Heinz](/wiki/Heinz_mean "Heinz mean")   - [Lehmer](/wiki/Lehmer_mean "Lehmer mean") - [Median](/wiki/Median "Median") - [Mode](/wiki/Mode_(statistics) "Mode (statistics)") | | [Dispersion](/wiki/Statistical_dispersion "Statistical dispersion") | - [Average absolute deviation](/wiki/Average_absolute_deviation "Average absolute deviation") - [Coefficient of variation](/wiki/Coefficient_of_variation "Coefficient of variation") - [Interquartile range](/wiki/Interquartile_range "Interquartile range") - [Percentile](/wiki/Percentile "Percentile") - [Range](/wiki/Range_(statistics) "Range (statistics)") - [Standard deviation](/wiki/Standard_deviation "Standard deviation") - [Variance](/wiki/Variance#Sample_variance "Variance") | | [Shape](/wiki/Shape_of_the_distribution "Shape of the distribution") | - [Central limit theorem](/wiki/Central_limit_theorem "Central limit theorem") - [Moments](/wiki/Moment_(mathematics) "Moment (mathematics)")   - [Kurtosis](/wiki/Kurtosis "Kurtosis")   - [L-moments](/wiki/L-moment "L-moment")   - [Skewness](/wiki/Skewness "Skewness") | | | [Count data](/wiki/Count_data "Count data") | - [Index of dispersion](/wiki/Index_of_dispersion "Index of dispersion") | | Summary tables | - [Contingency table](/wiki/Contingency_table "Contingency table") - [Frequency distribution](/wiki/Frequency_distribution "Frequency distribution") - [Grouped data](/wiki/Grouped_data "Grouped data") | | [Dependence](/wiki/Correlation_and_dependence "Correlation and dependence") | - [Partial correlation](/wiki/Partial_correlation "Partial correlation") - [Pearson product-moment correlation](/wiki/Pearson_correlation_coefficient "Pearson correlation coefficient") - [Rank correlation](/wiki/Rank_correlation "Rank correlation")   - [Kendall's τ](/wiki/Kendall_rank_correlation_coefficient "Kendall rank correlation coefficient")   - [Spearman's ρ](/wiki/Spearman%27s_rank_correlation_coefficient "Spearman's rank correlation coefficient") - [Scatter plot](/wiki/Scatter_plot "Scatter plot") | | [Graphics](/wiki/Statistical_graphics "Statistical graphics") | - [Bar chart](/wiki/Bar_chart "Bar chart") - [Biplot](/wiki/Biplot "Biplot") - [Box plot](/wiki/Box_plot "Box plot") - [Control chart](/wiki/Control_chart "Control chart") - [Correlogram](/wiki/Correlogram "Correlogram") - [Fan chart](/wiki/Fan_chart_(statistics) "Fan chart (statistics)") - [Forest plot](/wiki/Forest_plot "Forest plot") - [Histogram](/wiki/Histogram "Histogram") - [Pie chart](/wiki/Pie_chart "Pie chart") - [Q–Q plot](/wiki/Q%E2%80%93Q_plot "Q–Q plot") - [Radar chart](/wiki/Radar_chart "Radar chart") - [Run chart](/wiki/Run_chart "Run chart") - [Scatter plot](/wiki/Scatter_plot "Scatter plot") - [Stem-and-leaf display](/wiki/Stem-and-leaf_display "Stem-and-leaf display") - [Violin plot](/wiki/Violin_plot "Violin plot") - [Heatmap](/wiki/Heatmap "Heatmap") - [Scatter Plot Matrix](/wiki/Scatter_plot "Scatter plot") - [ECDF plot](/wiki/Empirical_distribution_function "Empirical distribution function") - [Line chart](/wiki/Line_chart "Line chart") | | | | |
| | [Statistical data processing](/wiki/Data_preprocessing "Data preprocessing") | | | --- | --- | | |  |  | | --- | --- | | [Transformations](/wiki/Data_transformation_(statistics) "Data transformation (statistics)") | - [Data transformation](/wiki/Data_transformation_(statistics) "Data transformation (statistics)") - [Log transformation](/w/index.php?title=Log_transformation&action=edit&redlink=1 "Log transformation (page does not exist)") - [Power transform](/wiki/Power_transform "Power transform")   - [Box–Cox transformation](/wiki/Box%E2%80%93Cox_transformation "Box–Cox transformation")   - [Yeo–Johnson transformation](/wiki/Yeo%E2%80%93Johnson_transformation "Yeo–Johnson transformation") - [Variance-stabilizing transformation](/wiki/Variance-stabilizing_transformation "Variance-stabilizing transformation") - [Anscombe transform](/wiki/Anscombe_transform "Anscombe transform") - [Fisher transformation](/wiki/Fisher_transformation "Fisher transformation") | | [Scaling and normalization](/wiki/Feature_scaling "Feature scaling") | - [Feature scaling](/wiki/Feature_scaling "Feature scaling") - [Normalization](/wiki/Normalization_(statistics) "Normalization (statistics)") - [Standardization (z-score)](/wiki/Standard_score "Standard score") - [Min–max normalization](/w/index.php?title=Min%E2%80%93max_normalization&action=edit&redlink=1 "Min–max normalization (page does not exist)") - [Unit vector normalization](/w/index.php?title=Unit_vector_normalization&action=edit&redlink=1 "Unit vector normalization (page does not exist)") | | Data cleaning | - [Data cleaning](/wiki/Data_cleaning "Data cleaning") - [Outlier](/wiki/Outlier "Outlier") - [Winsorizing](/wiki/Winsorizing "Winsorizing") - [Truncation](/wiki/Truncation_(statistics) "Truncation (statistics)") - [Missing data](/wiki/Missing_data "Missing data") | | Data reduction | - [Dimensionality reduction](/wiki/Dimensionality_reduction "Dimensionality reduction") - [Principal component analysis](/wiki/Principal_component_analysis "Principal component analysis") - [Factor analysis](/wiki/Factor_analysis "Factor analysis") | | Time-series preprocessing | - [Differencing](/wiki/Differencing "Differencing") - [Detrending](/wiki/Detrending "Detrending") - [Seasonal adjustment](/wiki/Seasonal_adjustment "Seasonal adjustment") - [Stationarity transformation](/wiki/Stationary_process "Stationary process") | | | | |
| | [Data collection](/wiki/Data_collection "Data collection") | | | --- | --- | | |  |  | | --- | --- | | [Study design](/wiki/Design_of_experiments "Design of experiments") | - [Effect size](/wiki/Effect_size "Effect size") - [Missing data](/wiki/Missing_data "Missing data") - [Optimal design](/wiki/Optimal_design "Optimal design") - [Population](/wiki/Statistical_population "Statistical population") - [Replication](/wiki/Replication_(statistics) "Replication (statistics)") - [Sample size determination](/wiki/Sample_size_determination "Sample size determination") - [Statistic](/wiki/Statistic "Statistic") - [Statistical power](/wiki/Statistical_power "Statistical power") | | [Survey methodology](/wiki/Survey_methodology "Survey methodology") | - [Sampling](/wiki/Sampling_(statistics) "Sampling (statistics)")   - [Cluster](/wiki/Cluster_sampling "Cluster sampling")   - [Stratified](/wiki/Stratified_sampling "Stratified sampling") - [Opinion poll](/wiki/Opinion_poll "Opinion poll") - [Questionnaire](/wiki/Questionnaire "Questionnaire") - [Standard error](/wiki/Standard_error "Standard error") | | [Controlled experiments](/wiki/Experiment "Experiment") | - [Blocking](/wiki/Blocking_(statistics) "Blocking (statistics)") - [Factorial experiment](/wiki/Factorial_experiment "Factorial experiment") - [Interaction](/wiki/Interaction_(statistics) "Interaction (statistics)") - [Random assignment](/wiki/Random_assignment "Random assignment") - [Randomized controlled trial](/wiki/Randomized_controlled_trial "Randomized controlled trial") - [Randomized experiment](/wiki/Randomized_experiment "Randomized experiment") - [Scientific control](/wiki/Scientific_control "Scientific control") | | Adaptive designs | - [Adaptive clinical trial](/wiki/Adaptive_clinical_trial "Adaptive clinical trial") - [Stochastic approximation](/wiki/Stochastic_approximation "Stochastic approximation") - [Up-and-down designs](/wiki/Up-and-Down_Designs "Up-and-Down Designs") | | [Observational studies](/wiki/Observational_study "Observational study") | - [Cohort study](/wiki/Cohort_study "Cohort study") - [Cross-sectional study](/wiki/Cross-sectional_study "Cross-sectional study") - [Natural experiment](/wiki/Natural_experiment "Natural experiment") - [Quasi-experiment](/wiki/Quasi-experiment "Quasi-experiment") | | | | |
| | [Statistical inference](/wiki/Statistical_inference "Statistical inference") | | | --- | --- | | |  |  | | --- | --- | | [Statistical theory](/wiki/Statistical_theory "Statistical theory") | - [Population](/wiki/Population_(statistics) "Population (statistics)") - [Statistic](/wiki/Statistic "Statistic") - [Probability distribution](/wiki/Probability_distribution "Probability distribution") - [Sampling distribution](/wiki/Sampling_distribution "Sampling distribution")   - [Order statistic](/wiki/Order_statistic "Order statistic") - [Empirical distribution](/wiki/Empirical_distribution_function "Empirical distribution function")   - [Density estimation](/wiki/Density_estimation "Density estimation") - [Statistical model](/wiki/Statistical_model "Statistical model")   - [Model specification](/wiki/Model_specification "Model specification")   - [L*p* space](/wiki/Lp_space "Lp space") - [Parameter](/wiki/Statistical_parameter "Statistical parameter")   - [location](/wiki/Location_parameter "Location parameter")   - [scale](/wiki/Scale_parameter "Scale parameter")   - [shape](/wiki/Shape_parameter "Shape parameter") - [Parametric family](/wiki/Parametric_statistics "Parametric statistics")   - [Likelihood](/wiki/Likelihood_function "Likelihood function") [(monotone)](/wiki/Monotone_likelihood_ratio "Monotone likelihood ratio")   - [Location–scale family](/wiki/Location%E2%80%93scale_family "Location–scale family")   - [Exponential family](/wiki/Exponential_family "Exponential family") - [Completeness](/wiki/Completeness_(statistics) "Completeness (statistics)") - [Sufficiency](/wiki/Sufficient_statistic "Sufficient statistic") - [Statistical functional](/wiki/Plug-in_principle "Plug-in principle")   - [Bootstrap](/wiki/Bootstrapping_(statistics) "Bootstrapping (statistics)")   - [U](/wiki/U-statistic "U-statistic")   - [V](/wiki/V-statistic "V-statistic") - [Optimal decision](/wiki/Optimal_decision "Optimal decision")   - [loss function](/wiki/Loss_function "Loss function") - [Efficiency](/wiki/Efficiency_(statistics) "Efficiency (statistics)") - [Statistical distance](/wiki/Statistical_distance "Statistical distance")   - [divergence](/wiki/Divergence_(statistics) "Divergence (statistics)") - [Asymptotics](/wiki/Asymptotic_theory_(statistics) "Asymptotic theory (statistics)") - [Robustness](/wiki/Robust_statistics "Robust statistics") ([Sensitivity analysis](/wiki/Sensitivity_analysis "Sensitivity analysis")) | | [Frequentist inference](/wiki/Frequentist_inference "Frequentist inference") | |  |  | | --- | --- | | [Point estimation](/wiki/Point_estimation "Point estimation") | - [Estimating equations](/wiki/Estimating_equations "Estimating equations")   - [Maximum likelihood](/wiki/Maximum_likelihood "Maximum likelihood")   - [Method of moments](/wiki/Method_of_moments_(statistics) "Method of moments (statistics)")   - [M-estimator](/wiki/M-estimator "M-estimator")   - [Minimum distance](/wiki/Minimum_distance_estimation "Minimum distance estimation") - [Unbiased estimators](/wiki/Bias_of_an_estimator "Bias of an estimator")   - [Mean-unbiased minimum-variance](/wiki/Minimum-variance_unbiased_estimator "Minimum-variance unbiased estimator")     - [Rao–Blackwellization](/wiki/Rao%E2%80%93Blackwell_theorem "Rao–Blackwell theorem")     - [Lehmann–Scheffé theorem](/wiki/Lehmann%E2%80%93Scheff%C3%A9_theorem "Lehmann–Scheffé theorem")   - [Median unbiased](/wiki/Median-unbiased_estimator "Median-unbiased estimator") - [Plug-in](/wiki/Plug-in_principle "Plug-in principle") | | [Interval estimation](/wiki/Interval_estimation "Interval estimation") | - [Confidence interval](/wiki/Confidence_interval "Confidence interval") - [Pivot](/wiki/Pivotal_quantity "Pivotal quantity") - [Likelihood interval](/wiki/Likelihood_interval "Likelihood interval") - [Prediction interval](/wiki/Prediction_interval "Prediction interval") - [Tolerance interval](/wiki/Tolerance_interval "Tolerance interval") - [Resampling](/wiki/Resampling_(statistics) "Resampling (statistics)")   - [Bootstrap](/wiki/Bootstrapping_(statistics) "Bootstrapping (statistics)")   - [Jackknife](/wiki/Jackknife_resampling "Jackknife resampling") | | [Testing hypotheses](/wiki/Statistical_hypothesis_test "Statistical hypothesis test") | - [1- & 2-tails](/wiki/One-_and_two-tailed_tests "One- and two-tailed tests") - [Power](/wiki/Power_(statistics) "Power (statistics)")   - [Uniformly most powerful test](/wiki/Uniformly_most_powerful_test "Uniformly most powerful test") - [Permutation test](/wiki/Permutation_test "Permutation test")   - [Randomization test](/wiki/Randomization_test "Randomization test") - [Multiple comparisons](/wiki/Multiple_comparisons "Multiple comparisons") | | [Parametric tests](/wiki/Parametric_statistics "Parametric statistics") | - [Likelihood-ratio](/wiki/Likelihood-ratio_test "Likelihood-ratio test")   - [*G*-test](/wiki/G-test "G-test") - [Score/Lagrange multiplier](/wiki/Score_test "Score test") - [Wald](/wiki/Wald_test "Wald test")   - [*Z*-test (normal)](/wiki/Z-test "Z-test") | | | [Specific tests](/wiki/List_of_statistical_tests "List of statistical tests") | |  |  | | --- | --- | | Parametric | - [Student's *t*-test](/wiki/Student%27s_t-test "Student's t-test") - [*F*-test](/wiki/F-test "F-test") | | [Goodness of fit](/wiki/Goodness_of_fit "Goodness of fit") | - [Chi-squared](/wiki/Chi-squared_test "Chi-squared test") - [Kolmogorov–Smirnov](/wiki/Kolmogorov%E2%80%93Smirnov_test "Kolmogorov–Smirnov test") - [Anderson–Darling](/wiki/Anderson%E2%80%93Darling_test "Anderson–Darling test") - [Lilliefors](/wiki/Lilliefors_test "Lilliefors test") - [Jarque–Bera](/wiki/Jarque%E2%80%93Bera_test "Jarque–Bera test") - [Normality (Shapiro–Wilk)](/wiki/Shapiro%E2%80%93Wilk_test "Shapiro–Wilk test") - [Model selection](/wiki/Model_selection "Model selection")   - [Cross validation](/wiki/Cross-validation_(statistics) "Cross-validation (statistics)")   - [AIC](/wiki/Akaike_information_criterion "Akaike information criterion")   - [BIC](/wiki/Bayesian_information_criterion "Bayesian information criterion") | | [Rank statistics](/wiki/Ranking_(statistics) "Ranking (statistics)") | - [Sign](/wiki/Sign_test "Sign test")   - [Sample median](/wiki/Sample_median "Sample median") - [Signed rank (Wilcoxon)](/wiki/Wilcoxon_signed-rank_test "Wilcoxon signed-rank test")   - [Hodges–Lehmann estimator](/wiki/Hodges%E2%80%93Lehmann_estimator "Hodges–Lehmann estimator") - [Rank sum (Mann–Whitney)](/wiki/Mann%E2%80%93Whitney_U_test "Mann–Whitney U test") - [Nonparametric](/wiki/Nonparametric_statistics "Nonparametric statistics") [anova](/wiki/Analysis_of_variance "Analysis of variance")   - [1-way (Kruskal–Wallis)](/wiki/Kruskal%E2%80%93Wallis_test "Kruskal–Wallis test")   - [2-way (Friedman)](/wiki/Friedman_test "Friedman test")   - [Ordered alternative (Jonckheere–Terpstra)](/wiki/Jonckheere%27s_trend_test "Jonckheere's trend test") - [Van der Waerden test](/wiki/Van_der_Waerden_test "Van der Waerden test") | | | [Bayesian inference](/wiki/Bayesian_inference "Bayesian inference") | - [Bayesian probability](/wiki/Bayesian_probability "Bayesian probability")   - [prior](/wiki/Prior_probability "Prior probability")   - [posterior](/wiki/Posterior_probability "Posterior probability") - [Credible interval](/wiki/Credible_interval "Credible interval") - [Bayes factor](/wiki/Bayes_factor "Bayes factor") - [Bayesian estimator](/wiki/Bayes_estimator "Bayes estimator")   - [Maximum posterior estimator](/wiki/Maximum_a_posteriori_estimation "Maximum a posteriori estimation") | | | | |
| | - [Correlation](/wiki/Correlation_and_dependence "Correlation and dependence") - [Regression analysis](/wiki/Regression_analysis "Regression analysis") | | | --- | --- | | |  |  | | --- | --- | | [Correlation](/wiki/Correlation_and_dependence "Correlation and dependence") | - [Pearson product-moment](/wiki/Pearson_product-moment_correlation_coefficient "Pearson product-moment correlation coefficient") - [Partial correlation](/wiki/Partial_correlation "Partial correlation") - [Confounding variable](/wiki/Confounding "Confounding") - [Coefficient of determination](/wiki/Coefficient_of_determination "Coefficient of determination") | | [Regression analysis](/wiki/Regression_analysis "Regression analysis") | - [Errors and residuals](/wiki/Errors_and_residuals "Errors and residuals") - [Regression validation](/wiki/Regression_validation "Regression validation") - [Mixed effects models](/wiki/Mixed_model "Mixed model") - [Simultaneous equations models](/wiki/Simultaneous_equations_model "Simultaneous equations model") - [Multivariate adaptive regression splines (MARS)](/wiki/Multivariate_adaptive_regression_splines "Multivariate adaptive regression splines") - [Template:Least squares and regression analysis](/wiki/Template:Least_squares_and_regression_analysis "Template:Least squares and regression analysis") | | [Linear regression](/wiki/Linear_regression "Linear regression") | - [Simple linear regression](/wiki/Simple_linear_regression "Simple linear regression") - [Ordinary least squares](/wiki/Ordinary_least_squares "Ordinary least squares") - [General linear model](/wiki/General_linear_model "General linear model") - [Bayesian regression](/wiki/Bayesian_linear_regression "Bayesian linear regression") | | Non-standard predictors | - [Nonlinear regression](/wiki/Nonlinear_regression "Nonlinear regression") - [Nonparametric](/wiki/Nonparametric_regression "Nonparametric regression") - [Semiparametric](/wiki/Semiparametric_regression "Semiparametric regression") - [Isotonic](/wiki/Isotonic_regression "Isotonic regression") - [Robust](/wiki/Robust_regression "Robust regression") - [Homoscedasticity and Heteroscedasticity](/wiki/Homoscedasticity_and_heteroscedasticity "Homoscedasticity and heteroscedasticity") | | [Generalized linear model](/wiki/Generalized_linear_model "Generalized linear model") | - [Exponential families](/wiki/Exponential_family "Exponential family") - [Logistic (Bernoulli)](/wiki/Logistic_regression "Logistic regression") / [Binomial](/wiki/Binomial_regression "Binomial regression") / [Poisson regressions](/wiki/Poisson_regression "Poisson regression") | | [Partition of variance](/wiki/Partition_of_sums_of_squares "Partition of sums of squares") | - [Analysis of variance (ANOVA)](/wiki/Analysis_of_variance "Analysis of variance") - [Analysis of variance (ANCOVA)](/wiki/Analysis_of_covariance "Analysis of covariance")] - [MANOVA](/wiki/Multivariate_analysis_of_variance "Multivariate analysis of variance") - [Degrees of freedom](/wiki/Degrees_of_freedom_(statistics) "Degrees of freedom (statistics)") | | | | |
| | [Categorical](/wiki/Categorical_variable "Categorical variable") / [multivariate](/wiki/Multivariate_statistics "Multivariate statistics") / [time-series](/wiki/Time_series "Time series") / [survival analysis](/wiki/Survival_analysis "Survival analysis") | | | --- | --- | | |  |  | | --- | --- | | [Categorical](/wiki/Categorical_variable "Categorical variable") | - [Cohen's kappa](/wiki/Cohen%27s_kappa "Cohen's kappa") - [Contingency table](/wiki/Contingency_table "Contingency table") - [Graphical model](/wiki/Graphical_model "Graphical model") - [Log-linear model](/wiki/Poisson_regression "Poisson regression") - [McNemar's test](/wiki/McNemar%27s_test "McNemar's test") - [Cochran–Mantel–Haenszel statistics](/wiki/Cochran%E2%80%93Mantel%E2%80%93Haenszel_statistics "Cochran–Mantel–Haenszel statistics") | | [Multivariate](/wiki/Multivariate_statistics "Multivariate statistics") | - [Regression](/wiki/General_linear_model "General linear model") - [Manova](/wiki/Multivariate_analysis_of_variance "Multivariate analysis of variance") - [Principal components](/wiki/Principal_component_analysis "Principal component analysis") - [Canonical correlation](/wiki/Canonical_correlation "Canonical correlation") - [Discriminant analysis](/wiki/Linear_discriminant_analysis "Linear discriminant analysis") - [Cluster analysis](/wiki/Cluster_analysis "Cluster analysis") - [Classification](/wiki/Statistical_classification "Statistical classification") - [Structural equation model](/wiki/Structural_equation_modeling "Structural equation modeling")   - [Factor analysis](/wiki/Factor_analysis "Factor analysis") - [Multivariate distributions](/wiki/Multivariate_distribution "Multivariate distribution")   - [Elliptical distributions](/wiki/Elliptical_distribution "Elliptical distribution")     - [Normal](/wiki/Multivariate_normal_distribution "Multivariate normal distribution") | | [Time-series](/wiki/Time_series "Time series") | |  |  | | --- | --- | | General | - [Decomposition](/wiki/Decomposition_of_time_series "Decomposition of time series") - [Trend](/wiki/Trend_estimation "Trend estimation") - [Stationarity](/wiki/Stationary_process "Stationary process") - [Seasonal adjustment](/wiki/Seasonal_adjustment "Seasonal adjustment") - [Exponential smoothing](/wiki/Exponential_smoothing "Exponential smoothing") - [Cointegration](/wiki/Cointegration "Cointegration") - [Structural break](/wiki/Structural_break "Structural break") - [Granger causality](/wiki/Granger_causality "Granger causality") | | Specific tests | - [Dickey–Fuller](/wiki/Dickey%E2%80%93Fuller_test "Dickey–Fuller test") - [Johansen](/wiki/Johansen_test "Johansen test") - [Q-statistic (Ljung–Box)](/wiki/Ljung%E2%80%93Box_test "Ljung–Box test") - [Durbin–Watson](/wiki/Durbin%E2%80%93Watson_statistic "Durbin–Watson statistic") - [Breusch–Godfrey](/wiki/Breusch%E2%80%93Godfrey_test "Breusch–Godfrey test") | | [Time domain](/wiki/Time_domain "Time domain") | - [Autocorrelation (ACF)](/wiki/Autocorrelation "Autocorrelation")   - [partial (PACF)](/wiki/Partial_autocorrelation_function "Partial autocorrelation function") - [Cross-correlation (XCF)](/wiki/Cross-correlation "Cross-correlation") - [ARMA model](/wiki/Autoregressive%E2%80%93moving-average_model "Autoregressive–moving-average model") - [ARIMA model (Box–Jenkins)](/wiki/Box%E2%80%93Jenkins_method "Box–Jenkins method") - [Autoregressive conditional heteroskedasticity (ARCH)](/wiki/Autoregressive_conditional_heteroskedasticity "Autoregressive conditional heteroskedasticity") - [Vector autoregression (VAR)](/wiki/Vector_autoregression "Vector autoregression") ([Autoregressive model (AR)](/wiki/Autoregressive_model "Autoregressive model")) | | [Frequency domain](/wiki/Frequency_domain "Frequency domain") | - [Spectral density estimation](/wiki/Spectral_density_estimation "Spectral density estimation") - [Fourier analysis](/wiki/Fourier_analysis "Fourier analysis") - [Least-squares spectral analysis](/wiki/Least-squares_spectral_analysis "Least-squares spectral analysis") - [Wavelet](/wiki/Wavelet "Wavelet") - [Whittle likelihood](/wiki/Whittle_likelihood "Whittle likelihood") | | | [Survival](/wiki/Survival_analysis "Survival analysis") | |  |  | | --- | --- | | [Survival function](/wiki/Survival_function "Survival function") | - [Kaplan–Meier estimator (product limit)](/wiki/Kaplan%E2%80%93Meier_estimator "Kaplan–Meier estimator") - [Proportional hazards models](/wiki/Proportional_hazards_model "Proportional hazards model") - [Accelerated failure time (AFT) model](/wiki/Accelerated_failure_time_model "Accelerated failure time model") - [First hitting time](/wiki/First-hitting-time_model "First-hitting-time model") | | Hazard function | - [Nelson–Aalen estimator](/wiki/Nelson%E2%80%93Aalen_estimator "Nelson–Aalen estimator") | | Test | - [Log-rank test](/wiki/Log-rank_test "Log-rank test") | | | | | |
| | [Applications](/wiki/List_of_fields_of_application_of_statistics "List of fields of application of statistics") | | | --- | --- | | |  |  | | --- | --- | | [Biostatistics](/wiki/Biostatistics "Biostatistics") | - [Bioinformatics](/wiki/Bioinformatics "Bioinformatics") - [Clinical trials](/wiki/Clinical_trial "Clinical trial") / [studies](/wiki/Clinical_study_design "Clinical study design") - [Epidemiology](/wiki/Epidemiology "Epidemiology") - [Medical statistics](/wiki/Medical_statistics "Medical statistics") | | [Engineering statistics](/wiki/Engineering_statistics "Engineering statistics") | - [Chemometrics](/wiki/Chemometrics "Chemometrics") - [Methods engineering](/wiki/Methods_engineering "Methods engineering") - [Probabilistic design](/wiki/Probabilistic_design "Probabilistic design") - [Process](/wiki/Statistical_process_control "Statistical process control") / [quality control](/wiki/Quality_control "Quality control") - [Reliability](/wiki/Reliability_engineering "Reliability engineering") - [System identification](/wiki/System_identification "System identification") | | [Social statistics](/wiki/Social_statistics "Social statistics") | - [Actuarial science](/wiki/Actuarial_science "Actuarial science") - [Census](/wiki/Census "Census") - [Crime statistics](/wiki/Crime_statistics "Crime statistics") - [Demography](/wiki/Demographic_statistics "Demographic statistics") - [Econometrics](/wiki/Econometrics "Econometrics") - [Jurimetrics](/wiki/Jurimetrics "Jurimetrics") - [National accounts](/wiki/National_accounts "National accounts") - [Official statistics](/wiki/Official_statistics "Official statistics") - [Population statistics](/wiki/Population_statistics "Population statistics") - [Psychometrics](/wiki/Psychometrics "Psychometrics") | | [Spatial statistics](/wiki/Spatial_analysis "Spatial analysis") | - [Cartography](/wiki/Cartography "Cartography") - [Environmental statistics](/wiki/Environmental_statistics "Environmental statistics") - [Geographic information system](/wiki/Geographic_information_system "Geographic information system") - [Geostatistics](/wiki/Geostatistics "Geostatistics") - [Kriging](/wiki/Kriging "Kriging") | | | | |
| - **[Category](/wiki/Category:Statistics "Category:Statistics")** - **[icon](/wiki/File:Square_root_of_x.svg) [Mathematics portal](/wiki/Portal:Mathematics "Portal:Mathematics")** - **[Commons](https://commons.wikimedia.org/wiki/Category:Statistics "commons:Category:Statistics")** - **[WikiProject](/wiki/Wikipedia:WikiProject_Statistics "Wikipedia:WikiProject Statistics")** | |
