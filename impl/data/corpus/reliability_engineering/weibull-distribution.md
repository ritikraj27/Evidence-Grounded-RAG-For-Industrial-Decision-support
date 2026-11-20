<!-- category: reliability_engineering -->
# Weibull distribution

Continuous probability distribution

.mw-parser-output .ambox{border:1px solid #a2a9b1;border-left:10px solid #36c;background-color:#fbfbfb;box-sizing:border-box}.mw-parser-output .ambox+.mw-empty-elt+.ambox,.mw-parser-output .ambox+.mw-empty-elt+.mw-empty-elt+.ambox,.mw-parser-output .ambox+.mw-empty-elt+.mw-empty-elt+.mw-empty-elt+.ambox{margin-top:-1px}html body.mediawiki .mw-parser-output .ambox.mbox-small-left{margin:4px 1em 4px 0;overflow:hidden;width:238px;border-collapse:collapse;font-size:88%;line-height:1.25em}.mw-parser-output .ambox-speedy{border-left:10px solid #b32424;background-color:#fee7e6}.mw-parser-output .ambox-delete{border-left:10px solid #b32424}.mw-parser-output .ambox-content{border-left:10px solid #f28500}.mw-parser-output .ambox-style{border-left:10px solid #fc3}.mw-parser-output .ambox-move{border-left:10px solid #9932cc}.mw-parser-output .ambox-protection{border-left:10px solid #a2a9b1}.mw-parser-output .ambox .mbox-text{border:none;padding:0.25em 0.5em;width:100%}.mw-parser-output .ambox .mbox-image{border:none;padding:2px 0 2px 0.5em;text-align:center}.mw-parser-output .ambox .mbox-imageright{border:none;padding:2px 0.5em 2px 0;text-align:center}.mw-parser-output .ambox .mbox-empty-cell{border:none;padding:0;width:1px}.mw-parser-output .ambox .mbox-image-div{width:52px}@media(min-width:720px){.mw-parser-output .ambox{margin:0 10%}}@media print{body.ns-0 .mw-parser-output .ambox{display:none!important}}

|  |  |
| --- | --- |
|  | This article's **use of [external links](/wiki/Wikipedia:External_links "Wikipedia:External links") may not follow Wikipedia's policies or guidelines**. Please [improve this article](https://en.wikipedia.org/w/index.php?title=Weibull_distribution&action=edit) by removing [excessive](/wiki/Wikipedia:What_Wikipedia_is_not#Wikipedia_is_not_a_mirror_or_a_repository_of_links,_images,_or_media_files "Wikipedia:What Wikipedia is not") or [inappropriate](/wiki/Wikipedia:External_links "Wikipedia:External links") external links, and converting useful links where appropriate into [footnote references](/wiki/Wikipedia:Citing_sources "Wikipedia:Citing sources"). *(August 2025)* *([Learn how and when to remove this message](/wiki/Help:Maintenance_template_removal "Help:Maintenance template removal"))* |

@media(min-width:640px){.mw-parser-output .infobox{margin-left:1em;float:right;clear:right;width:22em}}.mw-parser-output .infobox-subbox{padding:0;border:none;margin:-3px;width:auto;min-width:100%;font-size:100%;clear:none;float:none;background-color:transparent;color:inherit}.mw-parser-output .infobox-3cols-child{margin:-3px}.mw-parser-output .infobox .navbar{font-size:100%}.mw-parser-output .infobox-hiddenrow,body.skin--responsive.skin--responsive .mw-parser-output .infobox .infobox-hiddenrow{display:none}@media screen{html.skin-theme-clientpref-night .mw-parser-output .infobox-full-data:not(.notheme)>div:not(.notheme)[style]{background:#1f1f23!important;color:#f8f9fa}}@media screen and (prefers-color-scheme:dark){html.skin-theme-clientpref-os .mw-parser-output .infobox-full-data:not(.notheme)>div:not(.notheme)[style]{background:#1f1f23!important;color:#f8f9fa}}@media(min-width:640px){body.skin--responsive .mw-parser-output .infobox-table{display:table!important}body.skin--responsive .mw-parser-output .infobox-table>caption{display:table-caption!important}body.skin--responsive .mw-parser-output .infobox-table>tbody{display:table-row-group}body.skin--responsive .mw-parser-output .infobox-table th,body.skin--responsive .mw-parser-output .infobox-table td{padding-left:inherit;padding-right:inherit}}.mw-parser-output .ib-prob-dist{border-collapse:collapse;width:20em}.mw-parser-output .ib-prob-dist td,.mw-parser-output .ib-prob-dist th{border:1px solid var(--border-color-base,#a2a9b1);padding:0.3em 0.4em!important}.mw-parser-output .ib-prob-dist .infobox-subheader{text-align:left}.mw-parser-output .ib-prob-dist-image{background:var(--background-color-neutral,#eaecf0);font-weight:bold;text-align:center}

| Weibull (2-parameter) | | | |
| --- | --- | --- | --- |
| Probability density function [Probability distribution function](/wiki/File:Weibull_PDF.svg "Probability distribution function") | | | |
| Cumulative distribution function [Cumulative distribution function](/wiki/File:Weibull_CDF.svg "Cumulative distribution function") | | | |
| [Parameters](/wiki/Statistical_parameter "Statistical parameter") | λ ∈ ( 0 , + ∞ )  {\displaystyle \lambda \in (0,+\infty )\,} {\displaystyle \lambda \in (0,+\infty )\,} [scale](/wiki/Scale_parameter "Scale parameter")      k ∈ ( 0 , + ∞ )  {\displaystyle k\in (0,+\infty )\,} {\displaystyle k\in (0,+\infty )\,} [shape](/wiki/Shape_parameter "Shape parameter") | | |
| [Support](/wiki/Support_(mathematics) "Support (mathematics)") | x ∈ [ 0 , + ∞ )  {\displaystyle x\in [0,+\infty )\,} {\displaystyle x\in [0,+\infty )\,} | | |
| [PDF](/wiki/Probability_density_function "Probability density function") | f ( x ) =   {      k λ   (   x λ )  k − 1  e  − ( x  / λ  )  k ,  x ≥ 0 ,   0 ,  x < 0.  {\displaystyle f(x)={\begin{cases}{\frac {k}{\lambda }}\left({\frac {x}{\lambda }}\right)^{k-1}e^{-(x/\lambda )^{k}},&x\geq 0,\\0,&x<0.\end{cases}}} {\displaystyle f(x)={\begin{cases}{\frac {k}{\lambda }}\left({\frac {x}{\lambda }}\right)^{k-1}e^{-(x/\lambda )^{k}},&x\geq 0,\\0,&x<0.\end{cases}}} | | |
| [CDF](/wiki/Cumulative_distribution_function "Cumulative distribution function") | F ( x ) =   {    1 −  e  − ( x  / λ  )  k ,  x ≥ 0 ,   0 ,  x < 0.  {\displaystyle F(x)={\begin{cases}1-e^{-(x/\lambda )^{k}},&x\geq 0,\\0,&x<0.\end{cases}}} {\displaystyle F(x)={\begin{cases}1-e^{-(x/\lambda )^{k}},&x\geq 0,\\0,&x<0.\end{cases}}} | | |
| [Quantile](/wiki/Quantile_function "Quantile function") | Q ( p ) = λ ( − ln ⁡ ( 1 − p )  )   1 k {\displaystyle Q(p)=\lambda (-\ln(1-p))^{\frac {1}{k}}} {\displaystyle Q(p)=\lambda (-\ln(1-p))^{\frac {1}{k}}} | | |
| [Mean](/wiki/Expected_value "Expected value") | λ  Γ ( 1 + 1  / k )  {\displaystyle \lambda \,\Gamma (1+1/k)\,} {\displaystyle \lambda \,\Gamma (1+1/k)\,} | | |
| [Median](/wiki/Median "Median") | λ ( ln ⁡ 2  )  1  / k  {\displaystyle \lambda (\ln 2)^{1/k}\,} {\displaystyle \lambda (\ln 2)^{1/k}\,} | | |
| [Mode](/wiki/Mode_(statistics) "Mode (statistics)") | {    λ   (    k − 1 k )  1  / k  ,  k > 1 ,   0 ,  k ≤ 1.  {\displaystyle {\begin{cases}\lambda \left({\frac {k-1}{k}}\right)^{1/k}\,,&k>1,\\0,&k\leq 1.\end{cases}}} {\displaystyle {\begin{cases}\lambda \left({\frac {k-1}{k}}\right)^{1/k}\,,&k>1,\\0,&k\leq 1.\end{cases}}} | | |
| [Variance](/wiki/Variance "Variance") | λ  2  [  Γ  (  1 +   2 k ) −   (  Γ  (  1 +   1 k ) )  2 ]  {\displaystyle \lambda ^{2}\left[\Gamma \left(1+{\frac {2}{k}}\right)-\left(\Gamma \left(1+{\frac {1}{k}}\right)\right)^{2}\right]\,} {\displaystyle \lambda ^{2}\left[\Gamma \left(1+{\frac {2}{k}}\right)-\left(\Gamma \left(1+{\frac {1}{k}}\right)\right)^{2}\right]\,} | | |
| [Skewness](/wiki/Skewness "Skewness") | Γ ( 1 + 3  / k )  λ  3 − 3 μ  σ  2 −  μ  3  σ  3 {\displaystyle {\frac {\Gamma (1+3/k)\lambda ^{3}-3\mu \sigma ^{2}-\mu ^{3}}{\sigma ^{3}}}} {\displaystyle {\frac {\Gamma (1+3/k)\lambda ^{3}-3\mu \sigma ^{2}-\mu ^{3}}{\sigma ^{3}}}} | | |
| [Excess kurtosis](/wiki/Excess_kurtosis "Excess kurtosis") | (see text) | | |
| [Entropy](/wiki/Information_entropy "Information entropy") | γ ( 1 − 1  / k ) + ln ⁡ ( λ  / k ) + 1  {\displaystyle \gamma (1-1/k)+\ln(\lambda /k)+1\,} {\displaystyle \gamma (1-1/k)+\ln(\lambda /k)+1\,} | | |
| [MGF](/wiki/Moment-generating_function "Moment-generating function") | ∑  n = 0  ∞     t  n  λ  n  n ! Γ ( 1 + n  / k ) ,   k ≥ 1 {\displaystyle \sum \_{n=0}^{\infty }{\frac {t^{n}\lambda ^{n}}{n!}}\Gamma (1+n/k),\ k\geq 1} {\displaystyle \sum _{n=0}^{\infty }{\frac {t^{n}\lambda ^{n}}{n!}}\Gamma (1+n/k),\ k\geq 1} | | |
| [CF](/wiki/Characteristic_function_(probability_theory) "Characteristic function (probability theory)") | ∑  n = 0  ∞    ( i t  )  n  λ  n  n ! Γ ( 1 + n  / k ) {\displaystyle \sum \_{n=0}^{\infty }{\frac {(it)^{n}\lambda ^{n}}{n!}}\Gamma (1+n/k)} {\displaystyle \sum _{n=0}^{\infty }{\frac {(it)^{n}\lambda ^{n}}{n!}}\Gamma (1+n/k)} | | |
| [Kullback–Leibler divergence](/wiki/Kullback%E2%80%93Leibler_divergence "Kullback–Leibler divergence") | see below | | |

In [probability theory](/wiki/Probability_theory "Probability theory") and [statistics](/wiki/Statistics "Statistics"), the **Weibull distribution** [/ˈwaɪbʊl/](/wiki/Help:IPA/English "Help:IPA/English") is a continuous [probability distribution](/wiki/Probability_distribution "Probability distribution"). It models a broad range of random variables, largely in the nature of a time to failure or time between events. Examples are maximum one-day rainfalls and the time a user spends on a web page.

The distribution is named after Swedish mathematician [Waloddi Weibull](/wiki/Waloddi_Weibull "Waloddi Weibull"), who described it in detail in 1939,[[1]](#cite_note-1)[[2]](#cite_note-2) although it was first identified by [René Maurice Fréchet](/wiki/Ren%C3%A9_Maurice_Fr%C3%A9chet "René Maurice Fréchet") and first applied by Rosin & Rammler (1933) to describe a [particle size distribution](/wiki/Particle-size_distribution "Particle-size distribution").[[3]](#cite_note-:2-3)

## Definition

[[edit](/w/index.php?title=Weibull_distribution&veaction=edit&section=1 "Edit section: Definition") | [edit source](/w/index.php?title=Weibull_distribution&action=edit&section=1 "Edit section's source code: Definition")]

### Standard parameterization

[[edit](/w/index.php?title=Weibull_distribution&veaction=edit&section=2 "Edit section: Standard parameterization") | [edit source](/w/index.php?title=Weibull_distribution&action=edit&section=2 "Edit section's source code: Standard parameterization")]

The [probability density function](/wiki/Probability_density_function "Probability density function") of a Weibull [random variable](/wiki/Random_variable "Random variable") is[[4]](#cite_note-4)[[5]](#cite_note-5)

:   f
    (
    x
    ;
    λ
    ,
    k
    )
    =

    {

    k
    λ

    (

    x
    λ
    )

    k
    −
    1

    e

    −
    (
    x

    /
    λ

    )

    k
    ,

    x
    ≥
    0
    ,

    0
    ,

    x
    <
    0
    ,

    {\displaystyle f(x;\lambda ,k)={\begin{cases}{\frac {k}{\lambda }}\left({\frac {x}{\lambda }}\right)^{k-1}e^{-(x/\lambda )^{k}},&x\geq 0,\\0,&x<0,\end{cases}}}
    ![{\displaystyle f(x;\lambda ,k)={\begin{cases}{\frac {k}{\lambda }}\left({\frac {x}{\lambda }}\right)^{k-1}e^{-(x/\lambda )^{k}},&x\geq 0,\\0,&x<0,\end{cases}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/05e3bcdfd2495ee90297718ab601e9b167b96b0f)

where *k* > 0 is the *[shape parameter](/wiki/Shape_parameter "Shape parameter")* and λ > 0 is the *[scale parameter](/wiki/Scale_parameter "Scale parameter")* of the distribution. Its [complementary cumulative distribution function](/wiki/Cumulative_distribution_function#Complementary_cumulative_distribution_function_(tail_distribution) "Cumulative distribution function") is a [stretched exponential function](/wiki/Stretched_exponential_function "Stretched exponential function"). The Weibull distribution is related to a number of other probability distributions; in particular, it [interpolates](/wiki/Interpolation "Interpolation") between the [exponential distribution](/wiki/Exponential_distribution "Exponential distribution") (*k* = 1) and the [Rayleigh distribution](/wiki/Rayleigh_distribution "Rayleigh distribution") (*k* = 2 and 

λ
=

2
σ
{\displaystyle \lambda ={\sqrt {2}}\sigma }
![{\displaystyle \lambda ={\sqrt {2}}\sigma }](https://wikimedia.org/api/rest_v1/media/math/render/svg/9a7a2872f7bce070c0e67b5db632b285301f4cec)).[[6]](#cite_note-6)

If the quantity, *x,* is a "time-to-failure", the Weibull distribution gives a distribution for which the [hazard rate](/wiki/Failure_rate#Hazard_rate "Failure rate") is proportional to a power of time. The *shape* parameter, *k*, is that power plus one, and so this parameter can be interpreted directly as follows:[[7]](#cite_note-7)

- A value of 

  k
  <
  1

  {\displaystyle k<1\,}
  ![{\displaystyle k<1\,}](https://wikimedia.org/api/rest_v1/media/math/render/svg/7a6b9bf087f37f4b26612ebe865b12a8ea668c31) indicates that the hazard rate decreases over time (like in case of the [Lindy effect](/wiki/Lindy_effect "Lindy effect"), which however corresponds to [Pareto distributions](/wiki/Pareto_distribution "Pareto distribution")[[8]](#cite_note-:0-8) rather than Weibull distributions). This happens if there is significant "infant mortality", or defective items failing early and the hazard rate decreasing over time as the defective items are weeded out of the population. In the context of the [diffusion of innovations](/wiki/Bass_diffusion_model "Bass diffusion model"), this means negative word of mouth: the [hazard function](/wiki/Failure_rate#hazard_function "Failure rate") is a monotonically decreasing function of the proportion of adopters;
- A value of 

  k
  =
  1

  {\displaystyle k=1\,}
  ![{\displaystyle k=1\,}](https://wikimedia.org/api/rest_v1/media/math/render/svg/21af42d1129926be7ceb4dd33fd527997ab46f1f) indicates that the hazard rate is constant over time. This might suggest random external events are causing mortality, or failure. The Weibull distribution reduces to an [exponential distribution](/wiki/Exponential_distribution "Exponential distribution");
- A value of 

  k
  >
  1

  {\displaystyle k>1\,}
  ![{\displaystyle k>1\,}](https://wikimedia.org/api/rest_v1/media/math/render/svg/2b5fff5e154b7e2692c7e29f152fcfe4ee19c4c7) indicates that the hazard rate increases with time. This happens if there is an "aging" process, or parts that are more likely to fail as time goes on. In the context of the [diffusion of innovations](/wiki/Bass_diffusion_model "Bass diffusion model"), this means positive word of mouth: the hazard function is a monotonically increasing function of the proportion of adopters. The function is first convex, then concave with an inflection point at 

  (

  e

  1

  /
  k
  −
  1
  )

  /

  e

  1

  /
  k
  ,

  k
  >
  1

  {\displaystyle (e^{1/k}-1)/e^{1/k},\,k>1\,}
  ![{\displaystyle (e^{1/k}-1)/e^{1/k},\,k>1\,}](https://wikimedia.org/api/rest_v1/media/math/render/svg/2ab90f6acb10b2acef25176c8cecbd8c439c2262).

In the field of [materials science](/wiki/Materials_science "Materials science"), the shape parameter *k* of a distribution of strengths is known as the [Weibull modulus](/wiki/Weibull_modulus "Weibull modulus"). In the context of [diffusion of innovations](/wiki/Diffusion_of_innovations "Diffusion of innovations"), the Weibull distribution is a "pure" imitation/rejection model.

### Optional parameterizations

[[edit](/w/index.php?title=Weibull_distribution&veaction=edit&section=3 "Edit section: Optional parameterizations") | [edit source](/w/index.php?title=Weibull_distribution&action=edit&section=3 "Edit section's source code: Optional parameterizations")]

#### First option

[[edit](/w/index.php?title=Weibull_distribution&veaction=edit&section=4 "Edit section: First option") | [edit source](/w/index.php?title=Weibull_distribution&action=edit&section=4 "Edit section's source code: First option")]

Applications in [medical statistics](/wiki/Medical_statistics "Medical statistics") and [econometrics](/wiki/Econometrics "Econometrics") often adopt a different parameterization.[[9]](#cite_note-9)[[10]](#cite_note-10) The shape parameter *k* is the same as above, while the scale parameter is 

b
=

λ

−
k
{\displaystyle b=\lambda ^{-k}}
![{\displaystyle b=\lambda ^{-k}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/75d6015212afc18ff29110d0b61d0ae8f1933ee0). In this case, for *x* ≥ 0, the probability density function is

:   f
    (
    x
    ;
    k
    ,
    b
    )
    =
    b
    k

    x

    k
    −
    1

    e

    −
    b

    x

    k
    ,
    {\displaystyle f(x;k,b)=bkx^{k-1}e^{-bx^{k}},}
    ![{\displaystyle f(x;k,b)=bkx^{k-1}e^{-bx^{k}},}](https://wikimedia.org/api/rest_v1/media/math/render/svg/fca61110b30ff8c4750561792013a78a7924f3ed)

the cumulative distribution function is

:   F
    (
    x
    ;
    k
    ,
    b
    )
    =
    1
    −

    e

    −
    b

    x

    k
    ,
    {\displaystyle F(x;k,b)=1-e^{-bx^{k}},}
    ![{\displaystyle F(x;k,b)=1-e^{-bx^{k}},}](https://wikimedia.org/api/rest_v1/media/math/render/svg/372d388c3351b80f95b047852e7c252fb1512845)

the quantile function is

:   Q
    (
    p
    ;
    k
    ,
    b
    )
    =

    (

    −

    1
    b
    ln
    ⁡
    (
    1
    −
    p
    )
    )

    1
    k
    ,
    {\displaystyle Q(p;k,b)=\left(-{\frac {1}{b}}\ln(1-p)\right)^{\frac {1}{k}},}
    ![{\displaystyle Q(p;k,b)=\left(-{\frac {1}{b}}\ln(1-p)\right)^{\frac {1}{k}},}](https://wikimedia.org/api/rest_v1/media/math/render/svg/7f8ebba3ccfa7f3bc646e92439c24bdcfe52fdd5)

the hazard function is

:   h
    (
    x
    ;
    k
    ,
    b
    )
    =
    b
    k

    x

    k
    −
    1
    ,
    {\displaystyle h(x;k,b)=bkx^{k-1},}
    ![{\displaystyle h(x;k,b)=bkx^{k-1},}](https://wikimedia.org/api/rest_v1/media/math/render/svg/b1719ed3ccb30cb7ef6459d1c9de75a733e10fc9)

and the mean is

:   b

    −
    1

    /
    k
    Γ
    (
    1
    +
    1

    /
    k
    )
    .
    {\displaystyle b^{-1/k}\Gamma (1+1/k).}
    ![{\displaystyle b^{-1/k}\Gamma (1+1/k).}](https://wikimedia.org/api/rest_v1/media/math/render/svg/446595c3a23d347a9f83e5326229422ebe22a262)

#### Second option

[[edit](/w/index.php?title=Weibull_distribution&veaction=edit&section=5 "Edit section: Second option") | [edit source](/w/index.php?title=Weibull_distribution&action=edit&section=5 "Edit section's source code: Second option")]

A second parameterization option can also be found.[[11]](#cite_note-11)[[12]](#cite_note-12) The shape parameter *k* is the same as in the standard case, while the scale parameter *λ* is replaced with a rate parameter *β* = 1/*λ*. Then, for *x* ≥ 0, the probability density function is

:   f
    (
    x
    ;
    k
    ,
    β
    )
    =
    β
    k
    (

    β
    x

    )

    k
    −
    1

    e

    −
    (
    β
    x

    )

    k
    {\displaystyle f(x;k,\beta )=\beta k({\beta x})^{k-1}e^{-(\beta x)^{k}}}
    ![{\displaystyle f(x;k,\beta )=\beta k({\beta x})^{k-1}e^{-(\beta x)^{k}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/2f06c6e5afd3888dd4a4cb37a4913de10f73fe0c)

the cumulative distribution function is

:   F
    (
    x
    ;
    k
    ,
    β
    )
    =
    1
    −

    e

    −
    (
    β
    x

    )

    k
    ,
    {\displaystyle F(x;k,\beta )=1-e^{-(\beta x)^{k}},}
    ![{\displaystyle F(x;k,\beta )=1-e^{-(\beta x)^{k}},}](https://wikimedia.org/api/rest_v1/media/math/render/svg/7af5433c7af7fd46628ab37c732e48fdb24a89d6)

the quantile function is

:   Q
    (
    p
    ;
    k
    ,
    β
    )
    =

    1
    β
    (
    −
    ln
    ⁡
    (
    1
    −
    p
    )

    )

    1
    k
    ,
    {\displaystyle Q(p;k,\beta )={\frac {1}{\beta }}(-\ln(1-p))^{\frac {1}{k}},}
    ![{\displaystyle Q(p;k,\beta )={\frac {1}{\beta }}(-\ln(1-p))^{\frac {1}{k}},}](https://wikimedia.org/api/rest_v1/media/math/render/svg/153c410ec89994edc9666c3cc522af4e0fd9bda3)

and the hazard function is

:   h
    (
    x
    ;
    k
    ,
    β
    )
    =
    β
    k
    (

    β
    x

    )

    k
    −
    1
    .
    {\displaystyle h(x;k,\beta )=\beta k({\beta x})^{k-1}.}
    ![{\displaystyle h(x;k,\beta )=\beta k({\beta x})^{k-1}.}](https://wikimedia.org/api/rest_v1/media/math/render/svg/62e96db2dedeaa9f27c2952d1f5f1368f70bb21a)

In all three parameterizations, the hazard is decreasing for k < 1, increasing for k > 1 and constant for k = 1, in which case the Weibull distribution reduces to an exponential distribution.

## Properties

[[edit](/w/index.php?title=Weibull_distribution&veaction=edit&section=6 "Edit section: Properties") | [edit source](/w/index.php?title=Weibull_distribution&action=edit&section=6 "Edit section's source code: Properties")]

### Density function

[[edit](/w/index.php?title=Weibull_distribution&veaction=edit&section=7 "Edit section: Density function") | [edit source](/w/index.php?title=Weibull_distribution&action=edit&section=7 "Edit section's source code: Density function")]

The form of the density function of the Weibull distribution changes drastically with the value of *k*. For 0 < *k* < 1, the density function tends to ∞ as *x* approaches zero from above and is strictly decreasing. For *k* = 1, the density function tends to 1/*λ* as *x* approaches zero from above and is strictly decreasing. For *k* > 1, the density function tends to zero as *x* approaches zero from above, increases until its mode and decreases after it. The density function has infinite negative slope at *x* = 0 if 0 < *k* < 1, infinite positive slope at *x* = 0 if 1 < *k* < 2 and null slope at *x* = 0 if *k* > 2. For *k* = 1 the density has a finite negative slope at *x* = 0. For *k* = 2 the density has a finite positive slope at *x* = 0. As *k* goes to infinity, the Weibull distribution converges to a [Dirac delta distribution](/wiki/Dirac_delta_distribution "Dirac delta distribution") centered at *x* = λ. Moreover, the skewness and coefficient of variation depend only on the shape parameter. A generalization of the Weibull distribution is the [hyperbolastic distribution of type III](/wiki/Hyperbolastic_functions "Hyperbolastic functions").

### Cumulative distribution function

[[edit](/w/index.php?title=Weibull_distribution&veaction=edit&section=8 "Edit section: Cumulative distribution function") | [edit source](/w/index.php?title=Weibull_distribution&action=edit&section=8 "Edit section's source code: Cumulative distribution function")]

The [cumulative distribution function](/wiki/Cumulative_distribution_function "Cumulative distribution function") for the Weibull distribution is

:   F
    (
    x
    ;
    k
    ,
    λ
    )
    =
    1
    −

    e

    −
    (
    x

    /
    λ

    )

    k

    {\displaystyle F(x;k,\lambda )=1-e^{-(x/\lambda )^{k}}\,}
    ![{\displaystyle F(x;k,\lambda )=1-e^{-(x/\lambda )^{k}}\,}](https://wikimedia.org/api/rest_v1/media/math/render/svg/de232793bfaa7d0e86c987162741864cb1c22a27)

for *x* ≥ 0, and *F*(*x*; *k*; λ) = 0 for *x* < 0.

If *x* = λ then *F*(*x*; *k*; λ) = 1 − *e*−1 ≈ 0.632 for all values of *k*. Vice versa: at *F*(*x*; *k*; *λ*) = 0.632 the value of *x* ≈ *λ*.

The quantile (inverse cumulative distribution) function for the Weibull distribution is

:   Q
    (
    p
    ;
    k
    ,
    λ
    )
    =
    λ
    (
    −
    ln
    ⁡
    (
    1
    −
    p
    )

    )

    1

    /
    k
    {\displaystyle Q(p;k,\lambda )=\lambda (-\ln(1-p))^{1/k}}
    ![{\displaystyle Q(p;k,\lambda )=\lambda (-\ln(1-p))^{1/k}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/bf9f043e9d7b32e4c4b2c70b44b4ba31c5c59eab)

for 0 ≤ *p* < 1.

The [failure rate](/wiki/Failure_rate "Failure rate") *h* (or hazard function) is given by

:   h
    (
    x
    ;
    k
    ,
    λ
    )
    =

    k
    λ

    (

    x
    λ
    )

    k
    −
    1
    .
    {\displaystyle h(x;k,\lambda )={k \over \lambda }\left({x \over \lambda }\right)^{k-1}.}
    ![{\displaystyle h(x;k,\lambda )={k \over \lambda }\left({x \over \lambda }\right)^{k-1}.}](https://wikimedia.org/api/rest_v1/media/math/render/svg/754b73fc796b27e5ff222b3a6fdd73e3a42a9363)

The [Mean time between failures](/wiki/Mean_time_between_failures "Mean time between failures") *MTBF* is

:   MTBF
    (
    k
    ,
    λ
    )
    =
    λ
    Γ
    (
    1
    +
    1

    /
    k
    )
    .
    {\displaystyle {\text{MTBF}}(k,\lambda )=\lambda \Gamma (1+1/k).}
    ![{\displaystyle {\text{MTBF}}(k,\lambda )=\lambda \Gamma (1+1/k).}](https://wikimedia.org/api/rest_v1/media/math/render/svg/d223628a80553de0c1b72684b8a5af031420938f)

### Moments

[[edit](/w/index.php?title=Weibull_distribution&veaction=edit&section=9 "Edit section: Moments") | [edit source](/w/index.php?title=Weibull_distribution&action=edit&section=9 "Edit section's source code: Moments")]

The [moment generating function](/wiki/Moment_generating_function "Moment generating function") of the [logarithm](/wiki/Logarithm "Logarithm") of a Weibull distributed [random variable](/wiki/Random_variable "Random variable") is given by[[13]](#cite_note-JKB-13)

:   E
    ⁡

    [

    e

    t
    log
    ⁡
    X
    ]
    =

    λ

    t
    Γ

    (

    t
    k
    +
    1
    )
    {\displaystyle \operatorname {E} \left[e^{t\log X}\right]=\lambda ^{t}\Gamma \left({\frac {t}{k}}+1\right)}
    ![{\displaystyle \operatorname {E} \left[e^{t\log X}\right]=\lambda ^{t}\Gamma \left({\frac {t}{k}}+1\right)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/992fe36496b44da30c136e71b8d389bbd3cf5c28)

where Γ is the [gamma function](/wiki/Gamma_function "Gamma function"). Similarly, the [characteristic function](/wiki/Characteristic_function_(probability_theory) "Characteristic function (probability theory)") of log *X* is given by

:   E
    ⁡

    [

    e

    i
    t
    log
    ⁡
    X
    ]
    =

    λ

    i
    t
    Γ

    (

    i
    t
    k
    +
    1
    )
    .
    {\displaystyle \operatorname {E} \left[e^{it\log X}\right]=\lambda ^{it}\Gamma \left({\frac {it}{k}}+1\right).}
    ![{\displaystyle \operatorname {E} \left[e^{it\log X}\right]=\lambda ^{it}\Gamma \left({\frac {it}{k}}+1\right).}](https://wikimedia.org/api/rest_v1/media/math/render/svg/cafc0ab087d13e9a81eefaa6164a1165323b3065)

In particular, the *n*th [raw moment](/wiki/Raw_moment "Raw moment") of *X* is given by

:   m

    n
    =

    λ

    n
    Γ

    (

    1
    +

    n
    k
    )
    .
    {\displaystyle m\_{n}=\lambda ^{n}\Gamma \left(1+{\frac {n}{k}}\right).}
    ![{\displaystyle m_{n}=\lambda ^{n}\Gamma \left(1+{\frac {n}{k}}\right).}](https://wikimedia.org/api/rest_v1/media/math/render/svg/4715daa0e33c2f610448711de83e914f859c44bf)

The [mean](/wiki/Mean "Mean") and [variance](/wiki/Variance "Variance") of a Weibull [random variable](/wiki/Random_variable "Random variable") can be expressed as

:   E
    ⁡
    (
    X
    )
    =
    λ
    Γ

    (

    1
    +

    1
    k
    )

    {\displaystyle \operatorname {E} (X)=\lambda \Gamma \left(1+{\frac {1}{k}}\right)\,}
    ![{\displaystyle \operatorname {E} (X)=\lambda \Gamma \left(1+{\frac {1}{k}}\right)\,}](https://wikimedia.org/api/rest_v1/media/math/render/svg/332c402b04906e614e9d0aeb0c79231d854a77d4)

and

:   var
    ⁡
    (
    X
    )
    =

    λ

    2

    [

    Γ

    (

    1
    +

    2
    k
    )
    −

    (

    Γ

    (

    1
    +

    1
    k
    )
    )

    2
    ]

    .
    {\displaystyle \operatorname {var} (X)=\lambda ^{2}\left[\Gamma \left(1+{\frac {2}{k}}\right)-\left(\Gamma \left(1+{\frac {1}{k}}\right)\right)^{2}\right]\,.}
    ![{\displaystyle \operatorname {var} (X)=\lambda ^{2}\left[\Gamma \left(1+{\frac {2}{k}}\right)-\left(\Gamma \left(1+{\frac {1}{k}}\right)\right)^{2}\right]\,.}](https://wikimedia.org/api/rest_v1/media/math/render/svg/c1fbeabd8489533ec121cdd57f2003ba5229d5d8)

The skewness is given by

:   γ

    1
    =

    2

    Γ

    1

    3
    −
    3

    Γ

    1

    Γ

    2
    +

    Γ

    3

    [

    Γ

    2
    −

    Γ

    1

    2

    ]

    3

    /
    2
    {\displaystyle \gamma \_{1}={\frac {2\Gamma \_{1}^{3}-3\Gamma \_{1}\Gamma \_{2}+\Gamma \_{3}}{[\Gamma \_{2}-\Gamma \_{1}^{2}]^{3/2}}}}
    ![{\displaystyle \gamma _{1}={\frac {2\Gamma _{1}^{3}-3\Gamma _{1}\Gamma _{2}+\Gamma _{3}}{[\Gamma _{2}-\Gamma _{1}^{2}]^{3/2}}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/4debe36ebd435e3ab5ec52a91d071e8b89fd75be)

where 

Γ

i
=
Γ
(
1
+
i

/
k
)
{\displaystyle \Gamma \_{i}=\Gamma (1+i/k)}
![{\displaystyle \Gamma _{i}=\Gamma (1+i/k)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/ee10521897c45afdf8668aff5eeb0c2e8603fe94), which may also be written as

:   γ

    1
    =

    Γ

    (

    1
    +

    3
    k
    )

    λ

    3
    −
    3
    μ

    σ

    2
    −

    μ

    3

    σ

    3
    {\displaystyle \gamma \_{1}={\frac {\Gamma \left(1+{\frac {3}{k}}\right)\lambda ^{3}-3\mu \sigma ^{2}-\mu ^{3}}{\sigma ^{3}}}}
    ![{\displaystyle \gamma _{1}={\frac {\Gamma \left(1+{\frac {3}{k}}\right)\lambda ^{3}-3\mu \sigma ^{2}-\mu ^{3}}{\sigma ^{3}}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/27d651ac447722dcf5a02615511cc50ff825387e)

where the mean is denoted by μ and the standard deviation is denoted by σ.

The excess [kurtosis](/wiki/Kurtosis "Kurtosis") is given by

:   γ

    2
    =

    −
    6

    Γ

    1

    4
    +
    12

    Γ

    1

    2

    Γ

    2
    −
    3

    Γ

    2

    2
    −
    4

    Γ

    1

    Γ

    3
    +

    Γ

    4

    [

    Γ

    2
    −

    Γ

    1

    2

    ]

    2
    {\displaystyle \gamma \_{2}={\frac {-6\Gamma \_{1}^{4}+12\Gamma \_{1}^{2}\Gamma \_{2}-3\Gamma \_{2}^{2}-4\Gamma \_{1}\Gamma \_{3}+\Gamma \_{4}}{[\Gamma \_{2}-\Gamma \_{1}^{2}]^{2}}}}
    ![{\displaystyle \gamma _{2}={\frac {-6\Gamma _{1}^{4}+12\Gamma _{1}^{2}\Gamma _{2}-3\Gamma _{2}^{2}-4\Gamma _{1}\Gamma _{3}+\Gamma _{4}}{[\Gamma _{2}-\Gamma _{1}^{2}]^{2}}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/22013ea4a622ab7a9f7764bc198cfb7ee020c5dd)

where 

Γ

i
=
Γ
(
1
+
i

/
k
)
{\displaystyle \Gamma \_{i}=\Gamma (1+i/k)}
![{\displaystyle \Gamma _{i}=\Gamma (1+i/k)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/ee10521897c45afdf8668aff5eeb0c2e8603fe94). The kurtosis excess may also be written as:

:   γ

    2
    =

    λ

    4
    Γ
    (
    1
    +

    4
    k
    )
    −
    4

    γ

    1

    σ

    3
    μ
    −
    6

    μ

    2

    σ

    2
    −

    μ

    4

    σ

    4
    −
    3.
    {\displaystyle \gamma \_{2}={\frac {\lambda ^{4}\Gamma (1+{\frac {4}{k}})-4\gamma \_{1}\sigma ^{3}\mu -6\mu ^{2}\sigma ^{2}-\mu ^{4}}{\sigma ^{4}}}-3.}
    ![{\displaystyle \gamma _{2}={\frac {\lambda ^{4}\Gamma (1+{\frac {4}{k}})-4\gamma _{1}\sigma ^{3}\mu -6\mu ^{2}\sigma ^{2}-\mu ^{4}}{\sigma ^{4}}}-3.}](https://wikimedia.org/api/rest_v1/media/math/render/svg/a34ec765060ace4df2336c504df0f31a5ccb5d31)

### Moment generating function

[[edit](/w/index.php?title=Weibull_distribution&veaction=edit&section=10 "Edit section: Moment generating function") | [edit source](/w/index.php?title=Weibull_distribution&action=edit&section=10 "Edit section's source code: Moment generating function")]

A variety of expressions are available for the moment generating function of *X* itself. As a [power series](/wiki/Power_series "Power series"), since the raw moments are already known, one has

:   E
    ⁡

    [

    e

    t
    X
    ]
    =

    ∑

    n
    =
    0

    ∞

    t

    n

    λ

    n

    n
    !
    Γ

    (

    1
    +

    n
    k
    )
    .
    {\displaystyle \operatorname {E} \left[e^{tX}\right]=\sum \_{n=0}^{\infty }{\frac {t^{n}\lambda ^{n}}{n!}}\Gamma \left(1+{\frac {n}{k}}\right).}
    ![{\displaystyle \operatorname {E} \left[e^{tX}\right]=\sum _{n=0}^{\infty }{\frac {t^{n}\lambda ^{n}}{n!}}\Gamma \left(1+{\frac {n}{k}}\right).}](https://wikimedia.org/api/rest_v1/media/math/render/svg/fb62dff92f0aad620ce5249b5c4463525c568bea)

Alternatively, one can attempt to deal directly with the integral

:   E
    ⁡

    [

    e

    t
    X
    ]
    =

    ∫

    0

    ∞

    e

    t
    x

    k
    λ

    (

    x
    λ
    )

    k
    −
    1

    e

    −
    (
    x

    /
    λ

    )

    k

    d
    x
    .
    {\displaystyle \operatorname {E} \left[e^{tX}\right]=\int \_{0}^{\infty }e^{tx}{\frac {k}{\lambda }}\left({\frac {x}{\lambda }}\right)^{k-1}e^{-(x/\lambda )^{k}}\,dx.}
    ![{\displaystyle \operatorname {E} \left[e^{tX}\right]=\int _{0}^{\infty }e^{tx}{\frac {k}{\lambda }}\left({\frac {x}{\lambda }}\right)^{k-1}e^{-(x/\lambda )^{k}}\,dx.}](https://wikimedia.org/api/rest_v1/media/math/render/svg/60d34e366e5a1f3e487afba88552504547a972f9)

If the parameter *k* is assumed to be a rational number, expressed as *k* = *p*/*q* where *p* and *q* are integers, then this integral can be evaluated analytically.[[a]](#cite_note-16) With *t* replaced by −*t*, one finds

:   E
    ⁡

    [

    e

    −
    t
    X
    ]
    =

    1

    λ

    k

    t

    k

    p

    k

    q

    /
    p

    (

    2
    π

    )

    q
    +
    p
    −
    2

    G

    p
    ,
    q

    q
    ,
    p

    (

    1
    −
    k
    p
    ,

    2
    −
    k
    p
    ,
    …
    ,

    p
    −
    k
    p

    0
    q
    ,

    1
    q
    ,
    …
    ,

    q
    −
    1
    q

    |

    p

    p

    (

    q

    λ

    k

    t

    k
    )

    q
    )
    {\displaystyle \operatorname {E} \left[e^{-tX}\right]={\frac {1}{\lambda ^{k}\,t^{k}}}\,{\frac {p^{k}\,{\sqrt {q/p}}}{({\sqrt {2\pi }})^{q+p-2}}}\,G\_{p,q}^{\,q,p}\!\left(\left.{\begin{matrix}{\frac {1-k}{p}},{\frac {2-k}{p}},\dots ,{\frac {p-k}{p}}\\{\frac {0}{q}},{\frac {1}{q}},\dots ,{\frac {q-1}{q}}\end{matrix}}\;\right|\,{\frac {p^{p}}{\left(q\,\lambda ^{k}\,t^{k}\right)^{q}}}\right)}
    ![{\displaystyle \operatorname {E} \left[e^{-tX}\right]={\frac {1}{\lambda ^{k}\,t^{k}}}\,{\frac {p^{k}\,{\sqrt {q/p}}}{({\sqrt {2\pi }})^{q+p-2}}}\,G_{p,q}^{\,q,p}\!\left(\left.{\begin{matrix}{\frac {1-k}{p}},{\frac {2-k}{p}},\dots ,{\frac {p-k}{p}}\\{\frac {0}{q}},{\frac {1}{q}},\dots ,{\frac {q-1}{q}}\end{matrix}}\;\right|\,{\frac {p^{p}}{\left(q\,\lambda ^{k}\,t^{k}\right)^{q}}}\right)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/992350d0b4b2c014907ad897f1764513c53539ec)

where *G* is the [Meijer G-function](/wiki/Meijer_G-function "Meijer G-function").

The [characteristic function](/wiki/Characteristic_function_(probability_theory) "Characteristic function (probability theory)") has also been obtained by Muraleedharan et al. (2007)[[16]](#cite_note-17)

### Minima

[[edit](/w/index.php?title=Weibull_distribution&veaction=edit&section=11 "Edit section: Minima") | [edit source](/w/index.php?title=Weibull_distribution&action=edit&section=11 "Edit section's source code: Minima")]

Let 

X

1
,

X

2
,
…
,

X

n
{\displaystyle X\_{1},X\_{2},\ldots ,X\_{n}}
![{\displaystyle X_{1},X_{2},\ldots ,X_{n}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/d67872301909a9d739e265252ad0c7339cead069) be independent and identically distributed Weibull random variables with scale parameter 

λ
{\displaystyle \lambda }
![{\displaystyle \lambda }](https://wikimedia.org/api/rest_v1/media/math/render/svg/b43d0ea3c9c025af1be9128e62a18fa74bedda2a) and shape parameter 

k
{\displaystyle k}
![{\displaystyle k}](https://wikimedia.org/api/rest_v1/media/math/render/svg/c3c9a2c7b599b37105512c5d570edc034056dd40). If the minimum of these 

n
{\displaystyle n}
![{\displaystyle n}](https://wikimedia.org/api/rest_v1/media/math/render/svg/a601995d55609f2d9f5e233e36fbe9ea26011b3b) random variables is 

Z
=
min
(

X

1
,

X

2
,
…
,

X

n
)
{\displaystyle Z=\min(X\_{1},X\_{2},\ldots ,X\_{n})}
![{\displaystyle Z=\min(X_{1},X_{2},\ldots ,X_{n})}](https://wikimedia.org/api/rest_v1/media/math/render/svg/8aadef2deb639bd740ded3c52693f49d983f1c22), then the cumulative probability distribution of 

Z
{\displaystyle Z}
![{\displaystyle Z}](https://wikimedia.org/api/rest_v1/media/math/render/svg/1cc6b75e09a8aa3f04d8584b11db534f88fb56bd) is given by

:   F
    (
    z
    )
    =
    1
    −

    e

    −
    n
    (
    z

    /
    λ

    )

    k
    .
    {\displaystyle F(z)=1-e^{-n(z/\lambda )^{k}}.}
    ![{\displaystyle F(z)=1-e^{-n(z/\lambda )^{k}}.}](https://wikimedia.org/api/rest_v1/media/math/render/svg/f4da23330ba9cd30a691956ffb296ff213839baa)

That is, 

Z
{\displaystyle Z}
![{\displaystyle Z}](https://wikimedia.org/api/rest_v1/media/math/render/svg/1cc6b75e09a8aa3f04d8584b11db534f88fb56bd) will also be Weibull distributed with scale parameter 

n

−
1

/
k
λ
{\displaystyle n^{-1/k}\lambda }
![{\displaystyle n^{-1/k}\lambda }](https://wikimedia.org/api/rest_v1/media/math/render/svg/236ed0a1aaa7369e3e518df4ab2b60137e8fc798) and with shape parameter 

k
{\displaystyle k}
![{\displaystyle k}](https://wikimedia.org/api/rest_v1/media/math/render/svg/c3c9a2c7b599b37105512c5d570edc034056dd40).

### Reparametrization tricks

[[edit](/w/index.php?title=Weibull_distribution&veaction=edit&section=12 "Edit section: Reparametrization tricks") | [edit source](/w/index.php?title=Weibull_distribution&action=edit&section=12 "Edit section's source code: Reparametrization tricks")]

Fix some 

α
>
0
{\displaystyle \alpha >0}
![{\displaystyle \alpha >0}](https://wikimedia.org/api/rest_v1/media/math/render/svg/edd4f784b6e8bb68fa774213ceacbab2d97825dc). Let 

(

π

1
,
.
.
.
,

π

n
)
{\displaystyle (\pi \_{1},...,\pi \_{n})}
![{\displaystyle (\pi _{1},...,\pi _{n})}](https://wikimedia.org/api/rest_v1/media/math/render/svg/465f3fd6661bb3c7d4fa04ba67f263ca236b61f2) be nonnegative, and not all zero, and let 

g

1
,
.
.
.
,

g

n
{\displaystyle g\_{1},...,g\_{n}}
![{\displaystyle g_{1},...,g_{n}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/cd9ca63692df6807ff9b9340a6de1a39624eff5a) be independent samples of 

Weibull
(
1
,

α

−
1
)
{\displaystyle {\text{Weibull}}(1,\alpha ^{-1})}
![{\displaystyle {\text{Weibull}}(1,\alpha ^{-1})}](https://wikimedia.org/api/rest_v1/media/math/render/svg/81b9bbef3fe88f4b33c29c04ab1e2a04616349ea), then[[17]](#cite_note-18)

- arg
  ⁡

  min

  i
  (

  g

  i

  π

  i

  −
  α
  )
  ∼

  Categorical

  (

  π

  j

  ∑

  i

  π

  i
  )

  j
  {\displaystyle \arg \min \_{i}(g\_{i}\pi \_{i}^{-\alpha })\sim {\text{Categorical}}\left({\frac {\pi \_{j}}{\sum \_{i}\pi \_{i}}}\right)\_{j}}
  ![{\displaystyle \arg \min _{i}(g_{i}\pi _{i}^{-\alpha })\sim {\text{Categorical}}\left({\frac {\pi _{j}}{\sum _{i}\pi _{i}}}\right)_{j}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/5a08ef8f12baba99b472b1fb39df2b95c62b3cf8)
- min

  i
  (

  g

  i

  π

  i

  −
  α
  )
  ∼

  Weibull

  (

  (

  ∑

  i

  π

  i
  )

  −
  α
  ,

  α

  −
  1
  )
  {\displaystyle \min \_{i}(g\_{i}\pi \_{i}^{-\alpha })\sim {\text{Weibull}}\left(\left(\sum \_{i}\pi \_{i}\right)^{-\alpha },\alpha ^{-1}\right)}
  ![{\displaystyle \min _{i}(g_{i}\pi _{i}^{-\alpha })\sim {\text{Weibull}}\left(\left(\sum _{i}\pi _{i}\right)^{-\alpha },\alpha ^{-1}\right)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/77214d3549bbec3098c522794a0adbdaf767716f).

### Shannon entropy

[[edit](/w/index.php?title=Weibull_distribution&veaction=edit&section=13 "Edit section: Shannon entropy") | [edit source](/w/index.php?title=Weibull_distribution&action=edit&section=13 "Edit section's source code: Shannon entropy")]

The [information entropy](/wiki/Entropy_(information_theory) "Entropy (information theory)") is given by[[18]](#cite_note-19)

:   H
    (
    λ
    ,
    k
    )
    =
    γ

    (

    1
    −

    1
    k
    )
    +
    ln
    ⁡

    (

    λ
    k
    )
    +
    1
    {\displaystyle H(\lambda ,k)=\gamma \left(1-{\frac {1}{k}}\right)+\ln \left({\frac {\lambda }{k}}\right)+1}
    ![{\displaystyle H(\lambda ,k)=\gamma \left(1-{\frac {1}{k}}\right)+\ln \left({\frac {\lambda }{k}}\right)+1}](https://wikimedia.org/api/rest_v1/media/math/render/svg/0e17afcc052f01b7d5cb80e7739895c197524714)

where 

γ
{\displaystyle \gamma }
![{\displaystyle \gamma }](https://wikimedia.org/api/rest_v1/media/math/render/svg/a223c880b0ce3da8f64ee33c4f0010beee400b1a) is the [Euler–Mascheroni constant](/wiki/Euler%E2%80%93Mascheroni_constant "Euler–Mascheroni constant"). The Weibull distribution is the [maximum entropy distribution](/wiki/Maximum_entropy_distribution "Maximum entropy distribution") for a non-negative real random variate with a fixed [expected value](/wiki/Expected_value "Expected value") of *x**k* equal to *λ**k* and a fixed expected value of ln(*x**k*) equal to ln(*λ**k*) − 

γ
{\displaystyle \gamma }
![{\displaystyle \gamma }](https://wikimedia.org/api/rest_v1/media/math/render/svg/a223c880b0ce3da8f64ee33c4f0010beee400b1a).

### Kullback–Leibler divergence

[[edit](/w/index.php?title=Weibull_distribution&veaction=edit&section=14 "Edit section: Kullback–Leibler divergence") | [edit source](/w/index.php?title=Weibull_distribution&action=edit&section=14 "Edit section's source code: Kullback–Leibler divergence")]

The [Kullback–Leibler divergence](/wiki/Kullback%E2%80%93Leibler_divergence "Kullback–Leibler divergence") between two Weibull distributions is given by[[19]](#cite_note-20)

:   D

    KL
    (

    W
    e
    i
    b

    1
    ∥

    W
    e
    i
    b

    2
    )
    =
    log
    ⁡

    k

    1

    λ

    1

    k

    1
    −
    log
    ⁡

    k

    2

    λ

    2

    k

    2
    +
    (

    k

    1
    −

    k

    2
    )

    [

    log
    ⁡

    λ

    1
    −

    γ

    k

    1
    ]
    +

    (

    λ

    1

    λ

    2
    )

    k

    2
    Γ

    (

    k

    2

    k

    1
    +
    1
    )
    −
    1
    {\displaystyle D\_{\text{KL}}(\mathrm {Weib} \_{1}\parallel \mathrm {Weib} \_{2})=\log {\frac {k\_{1}}{\lambda \_{1}^{k\_{1}}}}-\log {\frac {k\_{2}}{\lambda \_{2}^{k\_{2}}}}+(k\_{1}-k\_{2})\left[\log \lambda \_{1}-{\frac {\gamma }{k\_{1}}}\right]+\left({\frac {\lambda \_{1}}{\lambda \_{2}}}\right)^{k\_{2}}\Gamma \left({\frac {k\_{2}}{k\_{1}}}+1\right)-1}
    ![{\displaystyle D_{\text{KL}}(\mathrm {Weib} _{1}\parallel \mathrm {Weib} _{2})=\log {\frac {k_{1}}{\lambda _{1}^{k_{1}}}}-\log {\frac {k_{2}}{\lambda _{2}^{k_{2}}}}+(k_{1}-k_{2})\left[\log \lambda _{1}-{\frac {\gamma }{k_{1}}}\right]+\left({\frac {\lambda _{1}}{\lambda _{2}}}\right)^{k_{2}}\Gamma \left({\frac {k_{2}}{k_{1}}}+1\right)-1}](https://wikimedia.org/api/rest_v1/media/math/render/svg/6b8b701f13ae0a9c80fb4358f74495e09b96fe3f)

## Parameter estimation

[[edit](/w/index.php?title=Weibull_distribution&veaction=edit&section=15 "Edit section: Parameter estimation") | [edit source](/w/index.php?title=Weibull_distribution&action=edit&section=15 "Edit section's source code: Parameter estimation")]

### Ordinary least square using Weibull plot

[[edit](/w/index.php?title=Weibull_distribution&veaction=edit&section=16 "Edit section: Ordinary least square using Weibull plot") | [edit source](/w/index.php?title=Weibull_distribution&action=edit&section=16 "Edit section's source code: Ordinary least square using Weibull plot")]

[![](//thumb.wikimedia.org/wikipedia/commons/thumb/c/ca/Weibull_qq.svg/250px-Weibull_qq.svg.png?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail)](/wiki/File:Weibull_qq.svg)

Weibull plot

The fit of a Weibull distribution to data can be visually assessed using a Weibull plot.[[20]](#cite_note-21) The Weibull plot is a plot of the [empirical cumulative distribution function](/wiki/Empirical_cumulative_distribution_function "Empirical cumulative distribution function") 

F
^
(
x
)
{\displaystyle {\widehat {F}}(x)}
![{\displaystyle {\widehat {F}}(x)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/745a52a9891dfde90409008ef944ecad43102c5a) of data on special axes in a type of [Q–Q plot](/wiki/Q%E2%80%93Q_plot "Q–Q plot"). The axes are 

ln
⁡
(
−
ln
⁡
(
1
−

F
^
(
x
)
)
)
{\displaystyle \ln(-\ln(1-{\widehat {F}}(x)))}
![{\displaystyle \ln(-\ln(1-{\widehat {F}}(x)))}](https://wikimedia.org/api/rest_v1/media/math/render/svg/2063049f0f253d977da8c3200a6345452c9d0594) versus 

ln
⁡
(
x
)
{\displaystyle \ln(x)}
![{\displaystyle \ln(x)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/0df055b8e294310e6785701c1c67105e109191d8). The reason for this change of variables is the cumulative distribution function can be linearized:

:   F
    (
    x
    )

    =
    1
    −

    e

    −
    (
    x

    /
    λ

    )

    k

    −
    ln
    ⁡
    (
    1
    −
    F
    (
    x
    )
    )

    =
    (
    x

    /
    λ

    )

    k

    ln
    ⁡
    (
    −
    ln
    ⁡
    (
    1
    −
    F
    (
    x
    )
    )
    )
    ⏟

    'y'

    =

    k
    ln
    ⁡
    x
    ⏟

    'mx'
    −

    k
    ln
    ⁡
    λ
    ⏟

    'c'
    {\displaystyle {\begin{aligned}F(x)&=1-e^{-(x/\lambda )^{k}}\\[4pt]-\ln(1-F(x))&=(x/\lambda )^{k}\\[4pt]\underbrace {\ln(-\ln(1-F(x)))} \_{\textrm {'y'}}&=\underbrace {k\ln x} \_{\textrm {'mx'}}-\underbrace {k\ln \lambda } \_{\textrm {'c'}}\end{aligned}}}
    ![{\displaystyle {\begin{aligned}F(x)&=1-e^{-(x/\lambda )^{k}}\\[4pt]-\ln(1-F(x))&=(x/\lambda )^{k}\\[4pt]\underbrace {\ln(-\ln(1-F(x)))} _{\textrm {'y'}}&=\underbrace {k\ln x} _{\textrm {'mx'}}-\underbrace {k\ln \lambda } _{\textrm {'c'}}\end{aligned}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/211d2c05e68101789978ade36bb598b66e56c5a0)

which can be seen to be in the standard form of a straight line. Therefore, if the data came from a Weibull distribution then a straight line is expected on a Weibull plot.

There are various approaches to obtaining the empirical distribution function from data. One method is to obtain the vertical coordinate for each point using

:   F
    ^
    =

    i
    −
    0.3

    n
    +
    0.4
    {\displaystyle {\widehat {F}}={\frac {i-0.3}{n+0.4}}}
    ![{\displaystyle {\widehat {F}}={\frac {i-0.3}{n+0.4}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/6f461deb6c15e1b2fb45a34b721e035b96cccec7),

where 

i
{\displaystyle i}
![{\displaystyle i}](https://wikimedia.org/api/rest_v1/media/math/render/svg/add78d8608ad86e54951b8c8bd6c8d8416533d20) is the rank of the data point and 

n
{\displaystyle n}
![{\displaystyle n}](https://wikimedia.org/api/rest_v1/media/math/render/svg/a601995d55609f2d9f5e233e36fbe9ea26011b3b) is the number of data points.[[21]](#cite_note-22)[[22]](#cite_note-23) Another common estimator[[23]](#cite_note-24) is

:   F
    ^
    =

    i
    −
    0.5
    n
    {\displaystyle {\widehat {F}}={\frac {i-0.5}{n}}}
    ![{\displaystyle {\widehat {F}}={\frac {i-0.5}{n}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/7c9c98f60a56bd4155a176798432c84bcc6d0be2).

Linear regression can also be used to numerically assess goodness of fit and estimate the parameters of the Weibull distribution. The gradient informs one directly about the shape parameter 

k
{\displaystyle k}
![{\displaystyle k}](https://wikimedia.org/api/rest_v1/media/math/render/svg/c3c9a2c7b599b37105512c5d570edc034056dd40) and the scale parameter 

λ
{\displaystyle \lambda }
![{\displaystyle \lambda }](https://wikimedia.org/api/rest_v1/media/math/render/svg/b43d0ea3c9c025af1be9128e62a18fa74bedda2a) can also be inferred.

### Method of moments

[[edit](/w/index.php?title=Weibull_distribution&veaction=edit&section=17 "Edit section: Method of moments") | [edit source](/w/index.php?title=Weibull_distribution&action=edit&section=17 "Edit section's source code: Method of moments")]

The [coefficient of variation](/wiki/Coefficient_of_variation "Coefficient of variation") of Weibull distribution depends only on the shape parameter:[[24]](#cite_note-Cohen1965-25)

:   C

    V

    2
    =

    σ

    2

    μ

    2
    =

    Γ

    (

    1
    +

    2
    k
    )
    −

    (

    Γ

    (

    1
    +

    1
    k
    )
    )

    2

    (

    Γ

    (

    1
    +

    1
    k
    )
    )

    2
    .
    {\displaystyle CV^{2}={\frac {\sigma ^{2}}{\mu ^{2}}}={\frac {\Gamma \left(1+{\frac {2}{k}}\right)-\left(\Gamma \left(1+{\frac {1}{k}}\right)\right)^{2}}{\left(\Gamma \left(1+{\frac {1}{k}}\right)\right)^{2}}}.}
    ![{\displaystyle CV^{2}={\frac {\sigma ^{2}}{\mu ^{2}}}={\frac {\Gamma \left(1+{\frac {2}{k}}\right)-\left(\Gamma \left(1+{\frac {1}{k}}\right)\right)^{2}}{\left(\Gamma \left(1+{\frac {1}{k}}\right)\right)^{2}}}.}](https://wikimedia.org/api/rest_v1/media/math/render/svg/cca0a531bcfb1c4fe4defcf52b52d89a2a4329d2)

Equating the sample quantities 

s

2

/

x
¯

2
{\displaystyle s^{2}/{\bar {x}}^{2}}
![{\displaystyle s^{2}/{\bar {x}}^{2}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/959324e5cacc559824b567910a7cb768d97f6dd2) to 

σ

2

/

μ

2
{\displaystyle \sigma ^{2}/\mu ^{2}}
![{\displaystyle \sigma ^{2}/\mu ^{2}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/5d9ac870606c0c2f30203b879aae5cdedf9ac822), the moment estimate of the shape parameter 

k
{\displaystyle k}
![{\displaystyle k}](https://wikimedia.org/api/rest_v1/media/math/render/svg/c3c9a2c7b599b37105512c5d570edc034056dd40) can be read off either from a look up table or a graph of 

C

V

2
{\displaystyle CV^{2}}
![{\displaystyle CV^{2}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/45b715468e0ef9b14642e553d0889b9def02e871) versus 

k
{\displaystyle k}
![{\displaystyle k}](https://wikimedia.org/api/rest_v1/media/math/render/svg/c3c9a2c7b599b37105512c5d570edc034056dd40). A more accurate estimate of 

k
^
{\displaystyle {\hat {k}}}
![{\displaystyle {\hat {k}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/118731403eb43bdbd3656e87603f013d6804a791) can be found using a root finding algorithm to solve

:   Γ

    (

    1
    +

    2
    k
    )
    −

    (

    Γ

    (

    1
    +

    1
    k
    )
    )

    2

    (

    Γ

    (

    1
    +

    1
    k
    )
    )

    2
    =

    s

    2

    x
    ¯

    2
    .
    {\displaystyle {\frac {\Gamma \left(1+{\frac {2}{k}}\right)-\left(\Gamma \left(1+{\frac {1}{k}}\right)\right)^{2}}{\left(\Gamma \left(1+{\frac {1}{k}}\right)\right)^{2}}}={\frac {s^{2}}{{\bar {x}}^{2}}}.}
    ![{\displaystyle {\frac {\Gamma \left(1+{\frac {2}{k}}\right)-\left(\Gamma \left(1+{\frac {1}{k}}\right)\right)^{2}}{\left(\Gamma \left(1+{\frac {1}{k}}\right)\right)^{2}}}={\frac {s^{2}}{{\bar {x}}^{2}}}.}](https://wikimedia.org/api/rest_v1/media/math/render/svg/c69ded93de0e151a7176ee260c822cad9f445b32)

The moment estimate of the scale parameter can then be found using the first moment equation as

:   λ
    ^
    =

    x
    ¯

    Γ

    (

    1
    +

    1

    k
    ^
    )
    .
    {\displaystyle {\hat {\lambda }}={\frac {\bar {x}}{\Gamma \left(1+{\frac {1}{\hat {k}}}\right)}}.}
    ![{\displaystyle {\hat {\lambda }}={\frac {\bar {x}}{\Gamma \left(1+{\frac {1}{\hat {k}}}\right)}}.}](https://wikimedia.org/api/rest_v1/media/math/render/svg/7f7a1f433029a6ff48b0952ac304e7543406512b)

### Maximum likelihood

[[edit](/w/index.php?title=Weibull_distribution&veaction=edit&section=18 "Edit section: Maximum likelihood") | [edit source](/w/index.php?title=Weibull_distribution&action=edit&section=18 "Edit section's source code: Maximum likelihood")]

The [maximum likelihood estimator](/wiki/Maximum_likelihood_estimation "Maximum likelihood estimation") for the 

λ
{\displaystyle \lambda }
![{\displaystyle \lambda }](https://wikimedia.org/api/rest_v1/media/math/render/svg/b43d0ea3c9c025af1be9128e62a18fa74bedda2a) parameter given 

k
{\displaystyle k}
![{\displaystyle k}](https://wikimedia.org/api/rest_v1/media/math/render/svg/c3c9a2c7b599b37105512c5d570edc034056dd40) is[[24]](#cite_note-Cohen1965-25)

:   λ
    ^
    =

    (

    1
    n

    ∑

    i
    =
    1

    n

    x

    i

    k
    )

    1
    k
    {\displaystyle {\widehat {\lambda }}=\left({\frac {1}{n}}\sum \_{i=1}^{n}x\_{i}^{k}\right)^{\frac {1}{k}}}
    ![{\displaystyle {\widehat {\lambda }}=\left({\frac {1}{n}}\sum _{i=1}^{n}x_{i}^{k}\right)^{\frac {1}{k}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/126c9e3330cfe45c05e00af01d1433b0df22b9f2)

The maximum likelihood estimator for 

k
{\displaystyle k}
![{\displaystyle k}](https://wikimedia.org/api/rest_v1/media/math/render/svg/c3c9a2c7b599b37105512c5d570edc034056dd40) is the solution for *k* of the following equation[[25]](#cite_note-Sornette,_D._2004-26)

:   0
    =

    ∑

    i
    =
    1

    n

    x

    i

    k
    ln
    ⁡

    x

    i

    ∑

    i
    =
    1

    n

    x

    i

    k
    −

    1
    k
    −

    1
    n

    ∑

    i
    =
    1

    n
    ln
    ⁡

    x

    i
    {\displaystyle 0={\frac {\sum \_{i=1}^{n}x\_{i}^{k}\ln x\_{i}}{\sum \_{i=1}^{n}x\_{i}^{k}}}-{\frac {1}{k}}-{\frac {1}{n}}\sum \_{i=1}^{n}\ln x\_{i}}
    ![{\displaystyle 0={\frac {\sum _{i=1}^{n}x_{i}^{k}\ln x_{i}}{\sum _{i=1}^{n}x_{i}^{k}}}-{\frac {1}{k}}-{\frac {1}{n}}\sum _{i=1}^{n}\ln x_{i}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/a8fe9686332c4d9aa86cfada5c1ffd78405124a5)

This equation defines 

k
^
{\displaystyle {\widehat {k}}}
![{\displaystyle {\widehat {k}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/54faca2f564d2a41342e1509bd93f0bca18e4ee8) only implicitly, one must generally solve for 

k
{\displaystyle k}
![{\displaystyle k}](https://wikimedia.org/api/rest_v1/media/math/render/svg/c3c9a2c7b599b37105512c5d570edc034056dd40) by numerical means.

When 

x

1
>

x

2
>
⋯
>

x

N
{\displaystyle x\_{1}>x\_{2}>\cdots >x\_{N}}
![{\displaystyle x_{1}>x_{2}>\cdots >x_{N}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/10d64c87c0cc6c0b7713ae9bce2300660b9954fc) are the 

N
{\displaystyle N}
![{\displaystyle N}](https://wikimedia.org/api/rest_v1/media/math/render/svg/f5e3890c981ae85503089652feb48b191b57aae3) largest observed samples from a dataset of more than 

N
{\displaystyle N}
![{\displaystyle N}](https://wikimedia.org/api/rest_v1/media/math/render/svg/f5e3890c981ae85503089652feb48b191b57aae3) samples, then the maximum likelihood estimator for the 

λ
{\displaystyle \lambda }
![{\displaystyle \lambda }](https://wikimedia.org/api/rest_v1/media/math/render/svg/b43d0ea3c9c025af1be9128e62a18fa74bedda2a) parameter given 

k
{\displaystyle k}
![{\displaystyle k}](https://wikimedia.org/api/rest_v1/media/math/render/svg/c3c9a2c7b599b37105512c5d570edc034056dd40) is[[25]](#cite_note-Sornette,_D._2004-26)

:   λ
    ^

    k
    =

    1
    N

    ∑

    i
    =
    1

    N
    (

    x

    i

    k
    −

    x

    N

    k
    )
    {\displaystyle {\widehat {\lambda }}^{k}={\frac {1}{N}}\sum \_{i=1}^{N}(x\_{i}^{k}-x\_{N}^{k})}
    ![{\displaystyle {\widehat {\lambda }}^{k}={\frac {1}{N}}\sum _{i=1}^{N}(x_{i}^{k}-x_{N}^{k})}](https://wikimedia.org/api/rest_v1/media/math/render/svg/5a0e96ae77029d55966e211be5ff344a10f0a0a0)

Also given that condition, the maximum likelihood estimator for 

k
{\displaystyle k}
![{\displaystyle k}](https://wikimedia.org/api/rest_v1/media/math/render/svg/c3c9a2c7b599b37105512c5d570edc034056dd40) is[*[citation needed](/wiki/Wikipedia:Citation_needed "Wikipedia:Citation needed")*]

:   0
    =

    ∑

    i
    =
    1

    N
    (

    x

    i

    k
    ln
    ⁡

    x

    i
    −

    x

    N

    k
    ln
    ⁡

    x

    N
    )

    ∑

    i
    =
    1

    N
    (

    x

    i

    k
    −

    x

    N

    k
    )
    −

    1
    N

    ∑

    i
    =
    1

    N
    ln
    ⁡

    x

    i
    {\displaystyle 0={\frac {\sum \_{i=1}^{N}(x\_{i}^{k}\ln x\_{i}-x\_{N}^{k}\ln x\_{N})}{\sum \_{i=1}^{N}(x\_{i}^{k}-x\_{N}^{k})}}-{\frac {1}{N}}\sum \_{i=1}^{N}\ln x\_{i}}
    ![{\displaystyle 0={\frac {\sum _{i=1}^{N}(x_{i}^{k}\ln x_{i}-x_{N}^{k}\ln x_{N})}{\sum _{i=1}^{N}(x_{i}^{k}-x_{N}^{k})}}-{\frac {1}{N}}\sum _{i=1}^{N}\ln x_{i}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/61ac4ba6bd899ba27eb8dbd8d0ec2abc937d3ec7)

Again, this being an implicit function, one must generally solve for 

k
{\displaystyle k}
![{\displaystyle k}](https://wikimedia.org/api/rest_v1/media/math/render/svg/c3c9a2c7b599b37105512c5d570edc034056dd40) by numerical means.

## Applications

[[edit](/w/index.php?title=Weibull_distribution&veaction=edit&section=19 "Edit section: Applications") | [edit source](/w/index.php?title=Weibull_distribution&action=edit&section=19 "Edit section's source code: Applications")]

The Weibull distribution is used[*[citation needed](/wiki/Wikipedia:Citation_needed "Wikipedia:Citation needed")*]

[![](//thumb.wikimedia.org/wikipedia/commons/thumb/2/29/FitWeibullDistr.tif/lossless-page1-250px-FitWeibullDistr.tif.png?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail)](/wiki/File:FitWeibullDistr.tif)

Fitted cumulative Weibull distribution to maximum one-day rainfalls

[![](//thumb.wikimedia.org/wikipedia/commons/thumb/8/8f/DCA_with_four_RDC.png/250px-DCA_with_four_RDC.png?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail)](/wiki/File:DCA_with_four_RDC.png)

Fitted curves for oil production time series data[[26]](#cite_note-ReferenceA-27)

- In [survival analysis](/wiki/Survival_analysis "Survival analysis")
- In [reliability engineering](/wiki/Reliability_engineering "Reliability engineering") and [failure analysis](/wiki/Failure_analysis "Failure analysis")
- In [electrical engineering](/wiki/Electrical_engineering "Electrical engineering") to represent overvoltage occurring in an electrical system
- In [industrial engineering](/wiki/Industrial_engineering "Industrial engineering") to represent [manufacturing](/wiki/Manufacturing "Manufacturing") and [delivery](/wiki/Delivery_(commerce) "Delivery (commerce)") times
- In [extreme value theory](/wiki/Extreme_value_theory "Extreme value theory")
- In [weather forecasting](/wiki/Weather_forecasting "Weather forecasting") and the [wind power industry](/wiki/Wind_power#Wind_energy_resources "Wind power") to describe [wind speed distributions](/wiki/Wind_power#Distribution_of_wind_speed "Wind power"), as the natural distribution often matches the Weibull shape[[27]](#cite_note-28)
- In communications systems engineering
  - In [radar](/wiki/Radar "Radar") systems to model the dispersion of the received signals level produced by some types of clutters
  - To model [fading channels](/wiki/Fading_channel "Fading channel") in [Wireless](/wiki/Wireless_communication "Wireless communication") communications, as the [Weibull fading](/wiki/Weibull_fading "Weibull fading") model seems to exhibit good fit to experimental fading [channel](/wiki/Channel_(communications) "Channel (communications)") measurements
- In [information retrieval](/wiki/Information_retrieval "Information retrieval") to model dwell times on web pages.[[28]](#cite_note-29)
- In [general insurance](/wiki/General_insurance "General insurance") to model the size of [reinsurance](/wiki/Reinsurance "Reinsurance") claims, and the cumulative development of [asbestosis](/wiki/Asbestosis "Asbestosis") losses
- In forecasting technological change (also known as the Sharif-Islam model)[[29]](#cite_note-30)
- In [hydrology](/wiki/Hydrology "Hydrology") the Weibull distribution is applied to extreme events such as annual maximum one-day rainfalls and river discharges.
- In [decline curve analysis](/wiki/Decline_curve_analysis "Decline curve analysis") to model oil production rate curve of shale oil wells.[[26]](#cite_note-ReferenceA-27)
- In describing the size of [particles](/wiki/Granular_material "Granular material") generated by grinding, [milling](/wiki/Mill_(grinding) "Mill (grinding)") and [crushing](/wiki/Crusher "Crusher") operations, the 2-Parameter Weibull distribution is used, and in these applications it is sometimes known as the Rosin–Rammler distribution.[[30]](#cite_note-31) In this context it predicts fewer fine particles than the [log-normal distribution](/wiki/Log-normal_distribution "Log-normal distribution") and it is generally most accurate for narrow particle size distributions.[[31]](#cite_note-32) The interpretation of the cumulative distribution function is that 

  F
  (
  x
  ;
  k
  ,
  λ
  )
  {\displaystyle F(x;k,\lambda )}
  ![{\displaystyle F(x;k,\lambda )}](https://wikimedia.org/api/rest_v1/media/math/render/svg/75ac825840b9f254c0b58009dddaf629a4e2ebfd) is the [mass fraction](/wiki/Mass_fraction_(chemistry) "Mass fraction (chemistry)") of particles with diameter smaller than 

  x
  {\displaystyle x}
  ![{\displaystyle x}](https://wikimedia.org/api/rest_v1/media/math/render/svg/87f9e315fd7e2ba406057a97300593c4802b53e4), where 

  λ
  {\displaystyle \lambda }
  ![{\displaystyle \lambda }](https://wikimedia.org/api/rest_v1/media/math/render/svg/b43d0ea3c9c025af1be9128e62a18fa74bedda2a) is the mean particle size and 

  k
  {\displaystyle k}
  ![{\displaystyle k}](https://wikimedia.org/api/rest_v1/media/math/render/svg/c3c9a2c7b599b37105512c5d570edc034056dd40) is a measure of the spread of particle sizes.
- In describing random point clouds (such as the positions of particles in an ideal gas): the probability to find the nearest-neighbor particle at a distance 

  x
  {\displaystyle x}
  ![{\displaystyle x}](https://wikimedia.org/api/rest_v1/media/math/render/svg/87f9e315fd7e2ba406057a97300593c4802b53e4) from a given particle is given by a Weibull distribution with 

  k
  =
  3
  {\displaystyle k=3}
  ![{\displaystyle k=3}](https://wikimedia.org/api/rest_v1/media/math/render/svg/662e06a2436f8a44fec791f5c794621f10dc8f30) and 

  ρ
  =
  1

  /

  λ

  3
  {\displaystyle \rho =1/\lambda ^{3}}
  ![{\displaystyle \rho =1/\lambda ^{3}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/a483bc48a9062740736d2c6de3bdff310cb0757a) equal to the density of the particles.[[32]](#cite_note-33)
- In calculating the rate of radiation-induced [single event effects](/wiki/Radiation_hardening#Digital_damage:_SEE "Radiation hardening") onboard spacecraft, a four-parameter Weibull distribution is used to fit experimentally measured device [cross section probability](/wiki/Cross_section_(physics) "Cross section (physics)") data to a particle [linear energy transfer](/wiki/Linear_energy_transfer "Linear energy transfer") spectrum.[[33]](#cite_note-34) The Weibull fit was originally used because of a belief that particle energy levels align to a statistical distribution, but this belief was later proven false[*[citation needed](/wiki/Wikipedia:Citation_needed "Wikipedia:Citation needed")*] and the Weibull fit continues to be used because of its many adjustable parameters, rather than a demonstrated physical basis.[[34]](#cite_note-35)

## Prediction

[[edit](/w/index.php?title=Weibull_distribution&veaction=edit&section=20 "Edit section: Prediction") | [edit source](/w/index.php?title=Weibull_distribution&action=edit&section=20 "Edit section's source code: Prediction")]

- It is often of interest to predict probabilities of out-of-sample data under the assumption that both the training data and the out-of-sample data follow a Weibull distribution.
- Predictions generated by substituting the [method of moments](/wiki/Method_of_moments_(statistics) "Method of moments (statistics)") or [maximum likelihood](/wiki/Maximum_likelihood_estimation "Maximum likelihood estimation") estimates of the Weibull parameters given above into the [cumulative distribution function](/wiki/Cumulative_distribution_function "Cumulative distribution function") ignore parameter uncertainty. As a result, the probabilities are not well [calibrated](/wiki/Calibration_(statistics) "Calibration (statistics)"), do not reflect the frequencies of out-of-sample events, and, in particular, underestimate the probabilities of out-of-sample tail events.[[35]](#cite_note-:1-36)
- Predictions generated using the objective [Bayesian](/wiki/Bayesian_inference "Bayesian inference") approach of calibrating prior prediction completely eliminate this underestimation. The Weibull distribution is one of a number of statistical distributions with [group](/wiki/Group_(mathematics) "Group (mathematics)") structure. As a result of the group structure, the Weibull has associated left and right [Haar measures](/wiki/Haar_measure "Haar measure"). The use of the right Haar measure as the [prior](/wiki/Prior_probability "Prior probability") (known as the right Haar prior) in a Bayesian prediction gives probabilities that are perfectly calibrated, for any underlying true parameter values.[[36]](#cite_note-37)[[35]](#cite_note-:1-36)[[37]](#cite_note-38) Calibrating prior prediction for the Weibull using the appropriate right Haar prior is implemented in the [R](/wiki/R_(programming_language) "R (programming language)") software package fitdistcp.[[1]](https://cran.r-project.org/web/packages/fitdistcp/index.html)

## Related distributions

[[edit](/w/index.php?title=Weibull_distribution&veaction=edit&section=21 "Edit section: Related distributions") | [edit source](/w/index.php?title=Weibull_distribution&action=edit&section=21 "Edit section's source code: Related distributions")]

- If 

  W
  ∼

  W
  e
  i
  b
  u
  l
  l
  (
  λ
  ,
  k
  )
  {\displaystyle W\sim \mathrm {Weibull} (\lambda ,k)}
  ![{\displaystyle W\sim \mathrm {Weibull} (\lambda ,k)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/f21e5bbf1633f0fc463f8b7b0bdc3eb190f80732), then the variable 

  G
  =
  log
  ⁡
  W
  {\displaystyle G=\log W}
  ![{\displaystyle G=\log W}](https://wikimedia.org/api/rest_v1/media/math/render/svg/a8078886a5629fb79671795fe38a5323f318530c) is [Gumbel (minimum) distributed](/wiki/Gumbel_distribution "Gumbel distribution") with location parameter 

  μ
  =
  log
  ⁡
  λ
  {\displaystyle \mu =\log \lambda }
  ![{\displaystyle \mu =\log \lambda }](https://wikimedia.org/api/rest_v1/media/math/render/svg/cd81ae5ce4f0d31c8a76fbdd8c808f7a1a3b2de6) and scale parameter 

  β
  =
  1

  /
  k
  {\displaystyle \beta =1/k}
  ![{\displaystyle \beta =1/k}](https://wikimedia.org/api/rest_v1/media/math/render/svg/80942139fd639597604e74a006aa1b95955a128b). That is, 

  G
  ∼

  G
  u
  m
  b
  e
  l

  min
  (
  log
  ⁡
  λ
  ,
  1

  /
  k
  )
  {\displaystyle G\sim \mathrm {Gumbel} \_{\min }(\log \lambda ,1/k)}
  ![{\displaystyle G\sim \mathrm {Gumbel} _{\min }(\log \lambda ,1/k)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/50f72981c5ac2ee5a56b8e188e96a8af3c7d917a).
- A Weibull distribution is a [generalized gamma distribution](/wiki/Generalized_gamma_distribution "Generalized gamma distribution") with both shape parameters equal to *k*.
- The translated Weibull distribution (or 3-parameter Weibull) contains an additional parameter.[[13]](#cite_note-JKB-13) It has the [probability density function](/wiki/Probability_density_function "Probability density function")
  > f
  > (
  > x
  > ;
  > k
  > ,
  > λ
  > ,
  > θ
  > )
  > =
  >
  >
  > k
  > λ
  >
  >
  > (
  >
  >
  >
  > x
  > −
  > θ
  > λ
  > )
  >
  > k
  > −
  > 1
  >
  > e
  >
  > −
  >
  >
  > (
  >
  >
  >
  > x
  > −
  > θ
  > λ
  > )
  >
  > k
  >
  > {\displaystyle f(x;k,\lambda ,\theta )={k \over \lambda }\left({x-\theta \over \lambda }\right)^{k-1}e^{-\left({x-\theta \over \lambda }\right)^{k}}\,}
  > ![{\displaystyle f(x;k,\lambda ,\theta )={k \over \lambda }\left({x-\theta  \over \lambda }\right)^{k-1}e^{-\left({x-\theta  \over \lambda }\right)^{k}}\,}](https://wikimedia.org/api/rest_v1/media/math/render/svg/87995d93b45d2bf4f0c5e6577b6e6c079e57fa34)

  for 

  x
  ≥
  θ
  {\displaystyle x\geq \theta }
  ![{\displaystyle x\geq \theta }](https://wikimedia.org/api/rest_v1/media/math/render/svg/208936bb288cd111f7a34cbe2dbed85e3dbc57a7) and 

  f
  (
  x
  ;
  k
  ,
  λ
  ,
  θ
  )
  =
  0
  {\displaystyle f(x;k,\lambda ,\theta )=0}
  ![{\displaystyle f(x;k,\lambda ,\theta )=0}](https://wikimedia.org/api/rest_v1/media/math/render/svg/485d0f18565ed624b79abb117a3a20f75a6b8756) for 

  x
  <
  θ
  {\displaystyle x<\theta }
  ![{\displaystyle x<\theta }](https://wikimedia.org/api/rest_v1/media/math/render/svg/c11f890dd25343362bc3dd296ebd3f678a1cb927), where 

  k
  >
  0
  {\displaystyle k>0}
  ![{\displaystyle k>0}](https://wikimedia.org/api/rest_v1/media/math/render/svg/27b3af208b148139eefc03f0f80fa94c38c5af45) is the [shape parameter](/wiki/Shape_parameter "Shape parameter"), 

  λ
  >
  0
  {\displaystyle \lambda >0}
  ![{\displaystyle \lambda >0}](https://wikimedia.org/api/rest_v1/media/math/render/svg/eea25afc0351140f919cf791c49c1964b8b081de) is the [scale parameter](/wiki/Scale_parameter "Scale parameter") and 

  θ
  {\displaystyle \theta }
  ![{\displaystyle \theta }](https://wikimedia.org/api/rest_v1/media/math/render/svg/6e5ab2664b422d53eb0c7df3b87e1360d75ad9af) is the [location parameter](/wiki/Location_parameter "Location parameter") of the distribution. 

  θ
  {\displaystyle \theta }
  ![{\displaystyle \theta }](https://wikimedia.org/api/rest_v1/media/math/render/svg/6e5ab2664b422d53eb0c7df3b87e1360d75ad9af) value sets an initial failure-free time before the regular Weibull process begins. When 

  θ
  =
  0
  {\displaystyle \theta =0}
  ![{\displaystyle \theta =0}](https://wikimedia.org/api/rest_v1/media/math/render/svg/2a7bc6e34b53e0e8a8815159c356b1acccf7ea24), this reduces to the 2-parameter distribution.
- The Weibull distribution can be characterized as the distribution of a random variable 

  W
  {\displaystyle W}
  ![{\displaystyle W}](https://wikimedia.org/api/rest_v1/media/math/render/svg/54a9c4c547f4d6111f81946cad242b18298d70b7) such that the random variable
  > X
  > =
  >
  >
  > (
  >
  >
  > W
  > λ
  > )
  >
  > k
  > {\displaystyle X=\left({\frac {W}{\lambda }}\right)^{k}}
  > ![{\displaystyle X=\left({\frac {W}{\lambda }}\right)^{k}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/f22379b79497ddec3656eab0f19e916690bddf25)

  is the standard [exponential distribution](/wiki/Exponential_distribution "Exponential distribution") with intensity 1.[[13]](#cite_note-JKB-13)
- This implies that the Weibull distribution can also be characterized in terms of a [uniform distribution](/wiki/Uniform_distribution_(continuous) "Uniform distribution (continuous)"): if 

  U
  {\displaystyle U}
  ![{\displaystyle U}](https://wikimedia.org/api/rest_v1/media/math/render/svg/458a728f53b9a0274f059cd695e067c430956025) is uniformly distributed on 

  (
  0
  ,
  1
  )
  {\displaystyle (0,1)}
  ![{\displaystyle (0,1)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/c79c6838e423c1ed3c7ea532a56dc9f9dae8290b), then the random variable 

  W
  =
  λ
  (
  −
  ln
  ⁡
  (
  U
  )

  )

  1

  /
  k

  {\displaystyle W=\lambda (-\ln(U))^{1/k}\,}
  ![{\displaystyle W=\lambda (-\ln(U))^{1/k}\,}](https://wikimedia.org/api/rest_v1/media/math/render/svg/cc0433edef7dfa2b9f2c23b683eab724016602cf) is Weibull distributed with parameters 

  k
  {\displaystyle k}
  ![{\displaystyle k}](https://wikimedia.org/api/rest_v1/media/math/render/svg/c3c9a2c7b599b37105512c5d570edc034056dd40) and 

  λ
  {\displaystyle \lambda }
  ![{\displaystyle \lambda }](https://wikimedia.org/api/rest_v1/media/math/render/svg/b43d0ea3c9c025af1be9128e62a18fa74bedda2a). Note that 

  −
  ln
  ⁡
  (
  U
  )
  {\displaystyle -\ln(U)}
  ![{\displaystyle -\ln(U)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/e58a3be0fdb7f2b7c45faf46d21c40e98b15a0d5) here is equivalent to 

  X
  {\displaystyle X}
  ![{\displaystyle X}](https://wikimedia.org/api/rest_v1/media/math/render/svg/68baa052181f707c662844a465bfeeb135e82bab) just above. This leads to an easily implemented numerical scheme for simulating a Weibull distribution.
- The Weibull distribution interpolates between the exponential distribution with intensity 

  1

  /
  λ
  {\displaystyle 1/\lambda }
  ![{\displaystyle 1/\lambda }](https://wikimedia.org/api/rest_v1/media/math/render/svg/1add931eabb9aec89275acb2f50d50428010b0fe) when 

  k
  =
  1
  {\displaystyle k=1}
  ![{\displaystyle k=1}](https://wikimedia.org/api/rest_v1/media/math/render/svg/6c035ffa69b5bca8bf2d16c3da3aaad79a8bcbfa) and a [Rayleigh distribution](/wiki/Rayleigh_distribution "Rayleigh distribution") of mode 

  σ
  =
  λ

  /

  2
  {\displaystyle \sigma =\lambda /{\sqrt {2}}}
  ![{\displaystyle \sigma =\lambda /{\sqrt {2}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/a786fa80734536356af025d27dce07773c3c218a) when 

  k
  =
  2
  {\displaystyle k=2}
  ![{\displaystyle k=2}](https://wikimedia.org/api/rest_v1/media/math/render/svg/0bd301789e1f25a3da4be297ff637754ebee5f5d).
- The Weibull distribution (usually sufficient in [reliability engineering](/wiki/Reliability_engineering "Reliability engineering")) is a special case of the three parameter [exponentiated Weibull distribution](/wiki/Exponentiated_Weibull_distribution "Exponentiated Weibull distribution") where the additional exponent equals 1. The exponentiated Weibull distribution accommodates [unimodal](/wiki/Unimodal_function "Unimodal function"), [bathtub shaped](/wiki/Bathtub_curve "Bathtub curve")[[38]](#cite_note-39) and [monotone](/wiki/Monotonic_function "Monotonic function") [failure rates](/wiki/Failure_rate "Failure rate").
- The Weibull distribution is a special case of the [generalized extreme value distribution](/wiki/Generalized_extreme_value_distribution "Generalized extreme value distribution"). It was in this connection that the distribution was first identified by [Maurice Fréchet](/wiki/Maurice_Fr%C3%A9chet "Maurice Fréchet") in 1927.[[39]](#cite_note-40) The closely related [Fréchet distribution](/wiki/Fr%C3%A9chet_distribution "Fréchet distribution"), named for this work, has the probability density function
  > f
  >
  >
  > F
  > r
  > e
  > c
  > h
  > e
  > t
  > (
  > x
  > ;
  > k
  > ,
  > λ
  > )
  > =
  >
  >
  > k
  > λ
  >
  >
  > (
  >
  >
  > x
  > λ
  > )
  >
  > −
  > 1
  > −
  > k
  >
  > e
  >
  > −
  > (
  > x
  >
  > /
  > λ
  >
  > )
  >
  > −
  > k
  > =
  >
  > f
  >
  >
  > W
  > e
  > i
  > b
  > u
  > l
  > l
  > (
  > x
  > ;
  > −
  > k
  > ,
  > λ
  > )
  > .
  > {\displaystyle f\_{\rm {Frechet}}(x;k,\lambda )={\frac {k}{\lambda }}\left({\frac {x}{\lambda }}\right)^{-1-k}e^{-(x/\lambda )^{-k}}=f\_{\rm {Weibull}}(x;-k,\lambda ).}
  > ![{\displaystyle f_{\rm {Frechet}}(x;k,\lambda )={\frac {k}{\lambda }}\left({\frac {x}{\lambda }}\right)^{-1-k}e^{-(x/\lambda )^{-k}}=f_{\rm {Weibull}}(x;-k,\lambda ).}](https://wikimedia.org/api/rest_v1/media/math/render/svg/b09dc6ee62c281cb42bdd9c9a976707a5ab104f3)
- The distribution of a random variable that is defined as the minimum of several random variables, each having a different Weibull distribution, is a [poly-Weibull distribution](/wiki/Poly-Weibull_distribution "Poly-Weibull distribution").
- The Weibull distribution was first applied by Rosin & Rammler (1933)[[3]](#cite_note-:2-3) to describe particle size distributions. It is widely used in [mineral processing](/wiki/Mineral_processing "Mineral processing") to describe [particle size distributions](/wiki/Particle_size_distribution "Particle size distribution") in [comminution](/wiki/Comminution "Comminution") processes. In this context the cumulative distribution is given by
  > f
  > (
  > x
  > ;
  >
  > P
  >
  >
  > 80
  > ,
  > m
  > )
  > =
  >
  >
  > {
  >
  >
  >
  > 1
  > −
  >
  > e
  >
  > ln
  > ⁡
  >
  > (
  > 0.2
  > )
  >
  >
  > (
  >
  >
  > x
  >
  > P
  >
  >
  > 80
  > )
  >
  > m
  >
  > x
  > ≥
  > 0
  > ,
  >
  >
  > 0
  >
  > x
  > <
  > 0
  > ,
  >
  > {\displaystyle f(x;P\_{\rm {80}},m)={\begin{cases}1-e^{\ln \left(0.2\right)\left({\frac {x}{P\_{\rm {80}}}}\right)^{m}}&x\geq 0,\\0&x<0,\end{cases}}}
  > ![{\displaystyle f(x;P_{\rm {80}},m)={\begin{cases}1-e^{\ln \left(0.2\right)\left({\frac {x}{P_{\rm {80}}}}\right)^{m}}&x\geq 0,\\0&x<0,\end{cases}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/385c2720a79553b87c3a6fa685c8ede059061e7f)

  where
  - x
    {\displaystyle x}
    ![{\displaystyle x}](https://wikimedia.org/api/rest_v1/media/math/render/svg/87f9e315fd7e2ba406057a97300593c4802b53e4) is the particle size
  - P

    80
    {\displaystyle P\_{\rm {80}}}
    ![{\displaystyle P_{\rm {80}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/9106a153644cd1a780c113685940ef23e1a01964) is the 80th percentile of the particle size distribution
  - m
    {\displaystyle m}
    ![{\displaystyle m}](https://wikimedia.org/api/rest_v1/media/math/render/svg/0a07d98bb302f3856cbabc47b2b9016692e3f7bc) is a parameter describing the spread of the distribution
- Because of its availability in [spreadsheets](/wiki/Spreadsheet "Spreadsheet"), it is also used where the underlying behavior is actually better modeled by an [Erlang distribution](/wiki/Erlang_distribution "Erlang distribution").[[40]](#cite_note-41)
- If 

  X
  ∼

  W
  e
  i
  b
  u
  l
  l
  (
  λ
  ,

  1
  2
  )
  {\displaystyle X\sim \mathrm {Weibull} (\lambda ,{\frac {1}{2}})}
  ![{\displaystyle X\sim \mathrm {Weibull} (\lambda ,{\frac {1}{2}})}](https://wikimedia.org/api/rest_v1/media/math/render/svg/31fcdf2bf838f664e677b641edda4d2446fbf9fb) then 

  X
  ∼

  E
  x
  p
  o
  n
  e
  n
  t
  i
  a
  l
  (

  1

  λ
  )
  {\displaystyle {\sqrt {X}}\sim \mathrm {Exponential} ({\frac {1}{\sqrt {\lambda }}})}
  ![{\displaystyle {\sqrt {X}}\sim \mathrm {Exponential} ({\frac {1}{\sqrt {\lambda }}})}](https://wikimedia.org/api/rest_v1/media/math/render/svg/dfe605393f7c5df97a55ef7169a3f37b72bc38ac) ([Exponential distribution](/wiki/Exponential_distribution "Exponential distribution"))
- For the same values of k, the [Gamma distribution](/wiki/Gamma_distribution "Gamma distribution") takes on similar shapes, but the Weibull distribution is more [platykurtic](/wiki/Kurtosis#Excess_kurtosis "Kurtosis").

## See also

[[edit](/w/index.php?title=Weibull_distribution&veaction=edit&section=22 "Edit section: See also") | [edit source](/w/index.php?title=Weibull_distribution&action=edit&section=22 "Edit section's source code: See also")]

- [Discrete Weibull distribution](/wiki/Discrete_Weibull_distribution "Discrete Weibull distribution")
- [Fisher–Tippett–Gnedenko theorem](/wiki/Fisher%E2%80%93Tippett%E2%80%93Gnedenko_theorem "Fisher–Tippett–Gnedenko theorem")
- [Logistic distribution](/wiki/Logistic_distribution "Logistic distribution")
- [Rosin–Rammler distribution](/wiki/Particle-size_distribution#Rosin–Rammler_distribution "Particle-size distribution") for particle size analysis
- [Rayleigh distribution](/wiki/Rayleigh_distribution "Rayleigh distribution")
- [Unit Weibull distribution](/wiki/Unit_Weibull_distribution "Unit Weibull distribution")

## Notes

[[edit](/w/index.php?title=Weibull_distribution&veaction=edit&section=23 "Edit section: Notes") | [edit source](/w/index.php?title=Weibull_distribution&action=edit&section=23 "Edit section's source code: Notes")]

.mw-parser-output .reflist-columns-2{column-width:30em}.mw-parser-output .reflist-columns-3{column-width:25em}body.skin-vector-2022 .mw-parser-output .reflist-columns-2{column-width:27em}body.skin-vector-2022 .mw-parser-output .reflist-columns-3{column-width:22.5em}.mw-parser-output .references[data-mw-group=upper-alpha]{list-style-type:upper-alpha}.mw-parser-output .references[data-mw-group=upper-roman]{list-style-type:upper-roman}.mw-parser-output .references[data-mw-group=lower-alpha]{list-style-type:lower-alpha}.mw-parser-output .references[data-mw-group=lower-greek]{list-style-type:lower-greek}.mw-parser-output .references[data-mw-group=lower-roman]{list-style-type:lower-roman}.mw-parser-output div.reflist-liststyle-upper-alpha .references{list-style-type:upper-alpha}.mw-parser-output div.reflist-liststyle-upper-roman .references{list-style-type:upper-roman}.mw-parser-output div.reflist-liststyle-lower-alpha .references{list-style-type:lower-alpha}.mw-parser-output div.reflist-liststyle-lower-greek .references{list-style-type:lower-greek}.mw-parser-output div.reflist-liststyle-lower-roman .references{list-style-type:lower-roman}

1. **[^](#cite_ref-16)** See Cheng, Tellambura & Beaulieu (2004)[[14]](#cite_note-14) for the case when *k* is an integer, and Sagias & Karagiannidis (2005)[[15]](#cite_note-15) for the rational case.

## References

[[edit](/w/index.php?title=Weibull_distribution&veaction=edit&section=24 "Edit section: References") | [edit source](/w/index.php?title=Weibull_distribution&action=edit&section=24 "Edit section's source code: References")]

1. **[^](#cite_ref-1)** .mw-parser-output cite.citation{font-style:inherit;word-wrap:break-word}.mw-parser-output .citation q{quotes:"\"""\"""'""'"}.mw-parser-output .citation:target{background-color:rgba(0,127,255,0.133)}.mw-parser-output .id-lock-free.id-lock-free a{background:url("//upload.wikimedia.org/wikipedia/commons/6/65/Lock-green.svg")right 0.1em center/9px no-repeat}.mw-parser-output .id-lock-limited.id-lock-limited a,.mw-parser-output .id-lock-registration.id-lock-registration a{background:url("//upload.wikimedia.org/wikipedia/commons/d/d6/Lock-gray-alt-2.svg")right 0.1em center/9px no-repeat}.mw-parser-output .id-lock-subscription.id-lock-subscription a{background:url("//upload.wikimedia.org/wikipedia/commons/a/aa/Lock-red-alt-2.svg")right 0.1em center/9px no-repeat}.mw-parser-output .cs1-ws-icon a{background:url("//upload.wikimedia.org/wikipedia/commons/4/4c/Wikisource-logo.svg")right 0.1em center/12px no-repeat}body:not(.skin-timeless):not(.skin-minerva) .mw-parser-output .id-lock-free a,body:not(.skin-timeless):not(.skin-minerva) .mw-parser-output .id-lock-limited a,body:not(.skin-timeless):not(.skin-minerva) .mw-parser-output .id-lock-registration a,body:not(.skin-timeless):not(.skin-minerva) .mw-parser-output .id-lock-subscription a,body:not(.skin-timeless):not(.skin-minerva) .mw-parser-output .cs1-ws-icon a{background-size:contain;padding:0 1em 0 0}.mw-parser-output .cs1-code{color:inherit;background:inherit;border:none;padding:inherit}.mw-parser-output .cs1-hidden-error{display:none;color:var(--color-error,#bf3c2c)}.mw-parser-output .cs1-visible-error{color:var(--color-error,#bf3c2c)}.mw-parser-output .cs1-maint{display:none;color:#085;margin-left:0.3em}.mw-parser-output .cs1-kern-left{padding-left:0.2em}.mw-parser-output .cs1-kern-right{padding-right:0.2em}.mw-parser-output .citation .mw-selflink{font-weight:inherit}@media screen{.mw-parser-output .cs1-format{font-size:95%}html.skin-theme-clientpref-night .mw-parser-output .cs1-maint{color:#18911f}}@media screen and (prefers-color-scheme:dark){html.skin-theme-clientpref-os .mw-parser-output .cs1-maint{color:#18911f}}W. Weibull (1939). "The Statistical Theory of the Strength of Materials". *Ingeniors Vetenskaps Academy Handlingar* (151). Stockholm: Generalstabens Litografiska Anstalts Förlag: 1–45.
2. **[^](#cite_ref-2)** Bowers, et al. (1997) Actuarial Mathematics, 2nd ed. Society of Actuaries.
3. ^ [***a***](#cite_ref-:2_3-0) [***b***](#cite_ref-:2_3-1) Rosin, P.; Rammler, E. (1933). "The law governing the fineness of powdered coal". *Journal of the Institute of Fuel*. **7**: 29–36, 109–122.
4. **[^](#cite_ref-4)** Papoulis, Athanasios Papoulis; Pillai, S. Unnikrishna (2002). *Probability, Random Variables, and Stochastic Processes* (4th ed.). Boston: McGraw-Hill. [ISBN](/wiki/ISBN_(identifier) "ISBN (identifier)") [0-07-366011-6](/wiki/Special:BookSources/0-07-366011-6 "Special:BookSources/0-07-366011-6").
5. **[^](#cite_ref-5)** Kizilersu, Ayse; Kreer, Markus; Thomas, Anthony W. (2018). ["The Weibull distribution"](https://doi.org/10.1111%2Fj.1740-9713.2018.01123.x). *Significance*. **15** (2): 10–11. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1111/j.1740-9713.2018.01123.x](https://doi.org/10.1111%2Fj.1740-9713.2018.01123.x).
6. **[^](#cite_ref-6)** ["Rayleigh Distribution – MATLAB & Simulink – MathWorks Australia"](https://web.archive.org/web/20141012083632/http://www.mathworks.com.au/help/stats/rayleigh-distribution.html). *www.mathworks.com.au*. Archived from [the original](http://www.mathworks.com.au/help/stats/rayleigh-distribution.html) on 12 October 2014. Retrieved 7 October 2014.
7. **[^](#cite_ref-7)** Jiang, R.; Murthy, D.N.P. (2011). "A study of Weibull shape parameter: Properties and significance". *Reliability Engineering & System Safety*. **96** (12): 1619–26. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1016/j.ress.2011.09.003](https://doi.org/10.1016%2Fj.ress.2011.09.003).
8. **[^](#cite_ref-:0_8-0)** Eliazar, Iddo (November 2017). "Lindy's Law". *Physica A: Statistical Mechanics and Its Applications*. **486**: 797–805. [Bibcode](/wiki/Bibcode_(identifier) "Bibcode (identifier)"):[2017PhyA..486..797E](https://ui.adsabs.harvard.edu/abs/2017PhyA..486..797E). [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1016/j.physa.2017.05.077](https://doi.org/10.1016%2Fj.physa.2017.05.077). [S2CID](/wiki/S2CID_(identifier) "S2CID (identifier)") [125349686](https://api.semanticscholar.org/CorpusID:125349686).
9. **[^](#cite_ref-9)** Collett, David (2015). *Modelling survival data in medical research* (3rd ed.). Boca Raton: Chapman and Hall / CRC. [ISBN](/wiki/ISBN_(identifier) "ISBN (identifier)") [978-1439856789](/wiki/Special:BookSources/978-1439856789 "Special:BookSources/978-1439856789").
10. **[^](#cite_ref-10)** Cameron, A. C.; Trivedi, P. K. (2005). *Microeconometrics : methods and applications*. Cambridge University Press. p. 584. [ISBN](/wiki/ISBN_(identifier) "ISBN (identifier)") [978-0-521-84805-3](/wiki/Special:BookSources/978-0-521-84805-3 "Special:BookSources/978-0-521-84805-3").
11. **[^](#cite_ref-11)** Kalbfleisch, J. D.; Prentice, R. L. (2002). *The statistical analysis of failure time data* (2nd ed.). Hoboken, N.J.: J. Wiley. [ISBN](/wiki/ISBN_(identifier) "ISBN (identifier)") [978-0-471-36357-6](/wiki/Special:BookSources/978-0-471-36357-6 "Special:BookSources/978-0-471-36357-6"). [OCLC](/wiki/OCLC_(identifier) "OCLC (identifier)") [50124320](https://search.worldcat.org/oclc/50124320).
12. **[^](#cite_ref-12)** Therneau, T. (2020). ["A Package for Survival Analysis in R."](https://CRAN.R-project.org/package=survival) R package version 3.1.
13. ^ [***a***](#cite_ref-JKB_13-0) [***b***](#cite_ref-JKB_13-1) [***c***](#cite_ref-JKB_13-2) [Johnson, Kotz & Balakrishnan 1994](#CITEREFJohnsonKotzBalakrishnan1994) harvnb error: no target: CITEREFJohnsonKotzBalakrishnan1994 ([help](/wiki/Category:Harv_and_Sfn_template_errors "Category:Harv and Sfn template errors"))
14. **[^](#cite_ref-14)** Cheng, J.; Tellambura, C.; Beaulieu, N.C. (August 2004). "Performance of digital linear modulations on Weibull slow-fading channels". *IEEE Transactions on Communications*. **52** (8): 1265–1268. [Bibcode](/wiki/Bibcode_(identifier) "Bibcode (identifier)"):[2004ITCom..52.1265C](https://ui.adsabs.harvard.edu/abs/2004ITCom..52.1265C). [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1109/TCOMM.2004.833015](https://doi.org/10.1109%2FTCOMM.2004.833015).
15. **[^](#cite_ref-15)** Sagias, N.C.; Karagiannidis, G.K. (October 2005). "Gaussian class multivariate Weibull distributions: theory and applications in fading channels". *IEEE Transactions on Information Theory*. **51** (10): 3608–3619. [Bibcode](/wiki/Bibcode_(identifier) "Bibcode (identifier)"):[2005ITIT...51.3608S](https://ui.adsabs.harvard.edu/abs/2005ITIT...51.3608S). [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1109/TIT.2005.855598](https://doi.org/10.1109%2FTIT.2005.855598).
16. **[^](#cite_ref-17)** Muraleedharan, G.; Rao, A. D.; Kurup, P. G.; Nair, N. Unnikrishnan; Sinha, Mourani (1 August 2007). ["Modified Weibull distribution for maximum and significant wave height simulation and prediction"](https://www.sciencedirect.com/science/article/pii/S0378383907000452). *Coastal Engineering*. **54** (8): 630–638. [Bibcode](/wiki/Bibcode_(identifier) "Bibcode (identifier)"):[2007CoasE..54..630M](https://ui.adsabs.harvard.edu/abs/2007CoasE..54..630M). [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1016/j.coastaleng.2007.05.001](https://doi.org/10.1016%2Fj.coastaleng.2007.05.001). [ISSN](/wiki/ISSN_(identifier) "ISSN (identifier)") [0378-3839](https://search.worldcat.org/issn/0378-3839).
17. **[^](#cite_ref-18)** Balog, Matej; Tripuraneni, Nilesh; Ghahramani, Zoubin; Weller, Adrian (17 July 2017). ["Lost Relatives of the Gumbel Trick"](https://proceedings.mlr.press/v70/balog17a.html). *International Conference on Machine Learning*. PMLR: 371–379. [arXiv](/wiki/ArXiv_(identifier) "ArXiv (identifier)"):[1706.04161](https://arxiv.org/abs/1706.04161).
18. **[^](#cite_ref-19)** Cho, Youngseuk; Sun, Hokeun; Lee, Kyeongjun (5 January 2015). ["Estimating the Entropy of a Weibull Distribution under Generalized Progressive Hybrid Censoring"](https://doi.org/10.3390%2Fe17010102). *Entropy*. **17** (1): 102–122. [Bibcode](/wiki/Bibcode_(identifier) "Bibcode (identifier)"):[2015Entrp..17..102C](https://ui.adsabs.harvard.edu/abs/2015Entrp..17..102C). [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.3390/e17010102](https://doi.org/10.3390%2Fe17010102). [ISSN](/wiki/ISSN_(identifier) "ISSN (identifier)") [1099-4300](https://search.worldcat.org/issn/1099-4300).
19. **[^](#cite_ref-20)** Bauckhage, Christian (2013). "Computing the Kullback-Leibler Divergence between two Weibull Distributions". [arXiv](/wiki/ArXiv_(identifier) "ArXiv (identifier)"):[1310.3713](https://arxiv.org/abs/1310.3713) [[cs.IT](https://arxiv.org/archive/cs.IT)].
20. **[^](#cite_ref-21)** ["1.3.3.30. Weibull Plot"](http://www.itl.nist.gov/div898/handbook/eda/section3/weibplot.htm). *www.itl.nist.gov*.
21. **[^](#cite_ref-22)** Wayne Nelson (2004) *Applied Life Data Analysis*. Wiley-Blackwell [ISBN](/wiki/ISBN_(identifier) "ISBN (identifier)") [0-471-64462-5](/wiki/Special:BookSources/0-471-64462-5 "Special:BookSources/0-471-64462-5")
22. **[^](#cite_ref-23)** Barnett, V. (1975). ["Probability Plotting Methods and Order Statistics"](https://www.jstor.org/stable/2346708). *Journal of the Royal Statistical Society. Series C (Applied Statistics)*. **24** (1): 95–108. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.2307/2346708](https://doi.org/10.2307%2F2346708). [ISSN](/wiki/ISSN_(identifier) "ISSN (identifier)") [0035-9254](https://search.worldcat.org/issn/0035-9254). [JSTOR](/wiki/JSTOR_(identifier) "JSTOR (identifier)") [2346708](https://www.jstor.org/stable/2346708).
23. **[^](#cite_ref-24)** [*ISO 20501:2019 – Fine ceramics (advanced ceramics, advanced technical ceramics) – Weibull statistics for strength data*](https://www.iso.org/standard/69875.html). [ISO](/wiki/ISO "ISO").
24. ^ [***a***](#cite_ref-Cohen1965_25-0) [***b***](#cite_ref-Cohen1965_25-1) Cohen, A. Clifford (November 1965). ["Maximum Likelihood Estimation in the Weibull Distribution Based on Complete and on Censored Samples"](https://www.stat.cmu.edu/technometrics/59-69/VOL-07-04/v0704579.pdf) (PDF). *Technometrics*. **7** (4): 579–588. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1080/00401706.1965.10490300](https://doi.org/10.1080%2F00401706.1965.10490300).
25. ^ [***a***](#cite_ref-Sornette,_D._2004_26-0) [***b***](#cite_ref-Sornette,_D._2004_26-1) Sornette, D. (2004). *Critical Phenomena in Natural Science: Chaos, Fractals, Self-organization, and Disorder*..
26. ^ [***a***](#cite_ref-ReferenceA_27-0) [***b***](#cite_ref-ReferenceA_27-1) Lee, Se Yoon; Mallick, Bani (2021). ["Bayesian Hierarchical Modeling: Application Towards Production Results in the Eagle Ford Shale of South Texas"](https://doi.org/10.1007%2Fs13571-020-00245-8). *Sankhya B*. **84**: 1–43. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1007/s13571-020-00245-8](https://doi.org/10.1007%2Fs13571-020-00245-8).
27. **[^](#cite_ref-28)** ["Wind Speed Distribution Weibull – REUK.co.uk"](http://www.reuk.co.uk/Wind-Speed-Distribution-Weibull.htm). *www.reuk.co.uk*.
28. **[^](#cite_ref-29)** Liu, Chao; White, Ryen W.; Dumais, Susan (19 July 2010). *Understanding web browsing behaviors through Weibull analysis of dwell time*. ACM. pp. 379–386. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1145/1835449.1835513](https://doi.org/10.1145%2F1835449.1835513). [ISBN](/wiki/ISBN_(identifier) "ISBN (identifier)") [9781450301534](/wiki/Special:BookSources/9781450301534 "Special:BookSources/9781450301534"). [S2CID](/wiki/S2CID_(identifier) "S2CID (identifier)") [12186028](https://api.semanticscholar.org/CorpusID:12186028).
29. **[^](#cite_ref-30)** Sharif, M.Nawaz; Islam, M.Nazrul (1980). "The Weibull distribution as a general model for forecasting technological change". *Technological Forecasting and Social Change*. **18** (3): 247–56. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1016/0040-1625(80)90026-8](https://doi.org/10.1016%2F0040-1625%2880%2990026-8).
30. **[^](#cite_ref-31)** [Computational Optimization of Internal Combustion Engine](https://books.google.com/books?id=9RFdUPgpysEC&dq=Rosin-Rammler+distribution+2+Parameter+Weibull+distribution&pg=PA49) page 49
31. **[^](#cite_ref-32)** Austin, L. G.; Klimpel, R. R.; Luckie, P. T. (1984). *Process Engineering of Size Reduction*. Hoboken, NJ: Guinn Printing Inc. [ISBN](/wiki/ISBN_(identifier) "ISBN (identifier)") [0-89520-421-5](/wiki/Special:BookSources/0-89520-421-5 "Special:BookSources/0-89520-421-5").
32. **[^](#cite_ref-33)** Chandrashekar, S. (1943). "Stochastic Problems in Physics and Astronomy". *Reviews of Modern Physics*. **15** (1): 86. [Bibcode](/wiki/Bibcode_(identifier) "Bibcode (identifier)"):[1943RvMP...15....1C](https://ui.adsabs.harvard.edu/abs/1943RvMP...15....1C). [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1103/RevModPhys.15.1](https://doi.org/10.1103%2FRevModPhys.15.1).
33. **[^](#cite_ref-34)** [ECSS-E-ST-10-12C – Methods for the calculation of radiation received and its effects, and a policy for design margins](https://ecss.nl/standard/ecss-e-st-10-12c-methods-for-the-calculation-of-radiation-received-and-its-effects-and-a-policy-for-design-margins/) (Report). European Cooperation for Space Standardization. 15 November 2008.
34. **[^](#cite_ref-35)** L. D. Edmonds; C. E. Barnes; L. Z. Scheick (May 2000). "8.3 Curve Fitting". [An Introduction to Space Radiation Effects on Microelectronics](https://parts.jpl.nasa.gov/pdf/JPL00-62.pdf) (PDF) (Report). NASA Jet Propulsion Laboratory, California Institute of Technology. pp. 75–76.
35. ^ [***a***](#cite_ref-:1_36-0) [***b***](#cite_ref-:1_36-1) Jewson, Stephen; Sweeting, Trevor; Jewson, Lynne (20 February 2025). ["Reducing reliability bias in assessments of extreme weather risk using calibrating priors"](https://ascmo.copernicus.org/articles/11/1/2025/). *Advances in Statistical Climatology, Meteorology and Oceanography*. **11** (1): 1–22. [Bibcode](/wiki/Bibcode_(identifier) "Bibcode (identifier)"):[2025ASCMO..11....1J](https://ui.adsabs.harvard.edu/abs/2025ASCMO..11....1J). [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.5194/ascmo-11-1-2025](https://doi.org/10.5194%2Fascmo-11-1-2025). [ISSN](/wiki/ISSN_(identifier) "ISSN (identifier)") [2364-3579](https://search.worldcat.org/issn/2364-3579).
36. **[^](#cite_ref-37)** Severini, Thomas A.; Mukerjee, Rahul; Ghosh, Malay (1 December 2002). ["On an exact probability matching property of right-invariant priors"](https://doi.org/10.1093/biomet/89.4.952). *Biometrika*. **89** (4): 952–957. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1093/biomet/89.4.952](https://doi.org/10.1093%2Fbiomet%2F89.4.952). [ISSN](/wiki/ISSN_(identifier) "ISSN (identifier)") [0006-3444](https://search.worldcat.org/issn/0006-3444).
37. **[^](#cite_ref-38)** Gerrard, R.; Tsanakas, A. (2011). ["Failure Probability Under Parameter Uncertainty"](https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1539-6924.2010.01549.x). *Risk Analysis*. **31** (5): 727–744. [Bibcode](/wiki/Bibcode_(identifier) "Bibcode (identifier)"):[2011RiskA..31..727G](https://ui.adsabs.harvard.edu/abs/2011RiskA..31..727G). [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1111/j.1539-6924.2010.01549.x](https://doi.org/10.1111%2Fj.1539-6924.2010.01549.x). [ISSN](/wiki/ISSN_(identifier) "ISSN (identifier)") [1539-6924](https://search.worldcat.org/issn/1539-6924). [PMID](/wiki/PMID_(identifier) "PMID (identifier)") [21175720](https://pubmed.ncbi.nlm.nih.gov/21175720).
38. **[^](#cite_ref-39)** ["System evolution and reliability of systems"](http://www.sys-ev.com/reliability01.htm). Sysev (Belgium). 1 January 2010.
39. **[^](#cite_ref-40)** Montgomery, Douglas (19 June 2012). *Introduction to statistical quality control*. [S.l.]: John Wiley. p. 95. [ISBN](/wiki/ISBN_(identifier) "ISBN (identifier)") [9781118146811](/wiki/Special:BookSources/9781118146811 "Special:BookSources/9781118146811").
40. **[^](#cite_ref-41)** Chatfield, C.; Goodhardt, G.J. (1973). "A Consumer Purchasing Model with Erlang Interpurchase Times". *Journal of the American Statistical Association*. **68** (344): 828–835. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1080/01621459.1973.10481432](https://doi.org/10.1080%2F01621459.1973.10481432).

## Further reading

[[edit](/w/index.php?title=Weibull_distribution&veaction=edit&section=25 "Edit section: Further reading") | [edit source](/w/index.php?title=Weibull_distribution&action=edit&section=25 "Edit section's source code: Further reading")]

.mw-parser-output .refbegin{margin-bottom:0.5em}.mw-parser-output .refbegin-hanging-indents>ul,.mw-parser-output .refbegin-hanging-indents section>ul{margin-left:0}.mw-parser-output .refbegin-hanging-indents>ul>li,.mw-parser-output .refbegin-hanging-indents section>ul>li{margin-left:0;padding-left:3.2em;text-indent:-3.2em}.mw-parser-output .refbegin-hanging-indents ul,.mw-parser-output .refbegin-hanging-indents ul li{list-style:none}@media(max-width:720px){.mw-parser-output .refbegin-hanging-indents>ul>li,.mw-parser-output .refbegin-hanging-indents section>ul>li{padding-left:1.6em;text-indent:-1.6em}}.mw-parser-output .refbegin-columns{margin-top:0.3em}.mw-parser-output .refbegin-columns ul{margin-top:0}.mw-parser-output .refbegin-columns li{page-break-inside:avoid;break-inside:avoid-column}@media screen{.mw-parser-output .refbegin{font-size:90%}}

- [Fréchet, Maurice](/wiki/Maurice_Fr%C3%A9chet "Maurice Fréchet") (1927), "Sur la loi de probabilité de l'écart maximum", *Annales de la Société Polonaise de Mathématique, Cracovie*, **6**: 93–116.
- [Mann, Nancy R.](/wiki/Nancy_Mann "Nancy Mann"); Schafer, Ray E.; Singpurwalla, Nozer D. (1974), [*Methods for Statistical Analysis of Reliability and Life Data*](https://archive.org/details/methodsforstatis00mann), Wiley Series in Probability and Mathematical Statistics: Applied Probability and Statistics (1st ed.), New York: John Wiley & Sons, [ISBN](/wiki/ISBN_(identifier) "ISBN (identifier)") [978-0-471-56737-0](/wiki/Special:BookSources/978-0-471-56737-0 "Special:BookSources/978-0-471-56737-0")
- [Weibull, W.](/wiki/Waloddi_Weibull "Waloddi Weibull") (1951), ["A statistical distribution function of wide applicability"](http://web.cecs.pdx.edu/~cgshirl/Documents/Weibull-ASME-Paper-1951.pdf) (PDF), *Journal of Applied Mechanics*, **18** (3): 293–297, [Bibcode](/wiki/Bibcode_(identifier) "Bibcode (identifier)"):[1951JAM....18..293W](https://ui.adsabs.harvard.edu/abs/1951JAM....18..293W), [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1115/1.4010337](https://doi.org/10.1115%2F1.4010337).
- Nelson Jr, Ralph (5 February 2008). ["Dispersing Powders in Liquids, Part 1, Chap 6: Particle Volume Distribution"](http://www.erpt.org/014Q/nelsa-06.htm). Retrieved 5 February 2008.

## External links

[[edit](/w/index.php?title=Weibull_distribution&veaction=edit&section=26 "Edit section: External links") | [edit source](/w/index.php?title=Weibull_distribution&action=edit&section=26 "Edit section's source code: External links")]

- ["Weibull distribution"](https://www.encyclopediaofmath.org/index.php?title=Weibull_distribution), *[Encyclopedia of Mathematics](/wiki/Encyclopedia_of_Mathematics "Encyclopedia of Mathematics")*, EMS Press, 2001 [1994]
- [Mathpages – Weibull analysis](http://www.mathpages.com/home/kmath122/kmath122.htm)
- [The Weibull Distribution](http://reliawiki.org/index.php/The_Weibull_Distribution)
- [Reliability Analysis with Weibull](http://www.crgraph.com/Weibull.pdf)
- Interactive graphic: [Univariate Distribution Relationships](http://www.math.wm.edu/~leemis/chart/UDR/UDR.html)
- [Online Weibull Probability Plotting](http://www.reliafy.com/) [Archived](https://web.archive.org/web/20160822215842/http://www.reliafy.com/) 22 August 2016 at the [Wayback Machine](/wiki/Wayback_Machine "Wayback Machine")

.mw-parser-output .hlist dl,.mw-parser-output .hlist ol,.mw-parser-output .hlist ul{margin:0;padding:0}.mw-parser-output .hlist dd,.mw-parser-output .hlist dt,.mw-parser-output .hlist li{margin:0;display:inline}.mw-parser-output .hlist.inline,.mw-parser-output .hlist.inline dl,.mw-parser-output .hlist.inline ol,.mw-parser-output .hlist.inline ul,.mw-parser-output .hlist dl dl,.mw-parser-output .hlist dl ol,.mw-parser-output .hlist dl ul,.mw-parser-output .hlist ol dl,.mw-parser-output .hlist ol ol,.mw-parser-output .hlist ol ul,.mw-parser-output .hlist ul dl,.mw-parser-output .hlist ul ol,.mw-parser-output .hlist ul ul{display:inline}.mw-parser-output .hlist .mw-empty-li{display:none}.mw-parser-output .hlist dt::after{content:": "}.mw-parser-output .hlist dd::after,.mw-parser-output .hlist li::after{content:"\a0 · ";font-weight:bold}.mw-parser-output .hlist dd:last-child::after,.mw-parser-output .hlist dt:last-child::after,.mw-parser-output .hlist li:last-child::after{content:none}.mw-parser-output .hlist dd dd:first-child::before,.mw-parser-output .hlist dd dt:first-child::before,.mw-parser-output .hlist dd li:first-child::before,.mw-parser-output .hlist dt dd:first-child::before,.mw-parser-output .hlist dt dt:first-child::before,.mw-parser-output .hlist dt li:first-child::before,.mw-parser-output .hlist li dd:first-child::before,.mw-parser-output .hlist li dt:first-child::before,.mw-parser-output .hlist li li:first-child::before{content:" (";font-weight:normal}.mw-parser-output .hlist dd dd:last-child::after,.mw-parser-output .hlist dd dt:last-child::after,.mw-parser-output .hlist dd li:last-child::after,.mw-parser-output .hlist dt dd:last-child::after,.mw-parser-output .hlist dt dt:last-child::after,.mw-parser-output .hlist dt li:last-child::after,.mw-parser-output .hlist li dd:last-child::after,.mw-parser-output .hlist li dt:last-child::after,.mw-parser-output .hlist li li:last-child::after{content:")";font-weight:normal}.mw-parser-output .hlist ol{counter-reset:listitem}.mw-parser-output .hlist ol>li{counter-increment:listitem}.mw-parser-output .hlist ol>li::before{content:" "counter(listitem)"\a0 "}.mw-parser-output .hlist dd ol>li:first-child::before,.mw-parser-output .hlist dt ol>li:first-child::before,.mw-parser-output .hlist li ol>li:first-child::before{content:" ("counter(listitem)"\a0 "}.mw-parser-output .navbox{box-sizing:border-box;border:1px solid #a2a9b1;width:100%;clear:both;font-size:88%;text-align:center;padding:1px;margin:1em auto 0}.mw-parser-output .navbox .navbox{margin-top:0}.mw-parser-output .navbox+.navbox-styles+.navbox,.mw-parser-output .navbox+span.mw-empty-elt+.navbox-styles+.navbox{margin-top:-1px}.mw-parser-output .navbox-inner,.mw-parser-output .navbox-subgroup{width:100%}.mw-parser-output .navbox-group,.mw-parser-output .navbox-title,.mw-parser-output .navbox-abovebelow{padding:0.25em 1em;line-height:1.5em;text-align:center}.mw-parser-output .navbox-group{white-space:nowrap;text-align:right}.mw-parser-output .navbox,.mw-parser-output .navbox-subgroup{background-color:#fdfdfd;color:inherit}.mw-parser-output .navbox-list{line-height:1.5em;border-color:#fdfdfd}.mw-parser-output .navbox-list-with-group{text-align:left;border-left-width:2px;border-left-style:solid}.mw-parser-output tr+tr>.navbox-abovebelow,.mw-parser-output tr+tr>.navbox-group,.mw-parser-output tr+tr>.navbox-image,.mw-parser-output tr+tr>.navbox-list{border-top:2px solid #fdfdfd}.mw-parser-output .navbox-title{background-color:#ccf;color:inherit}.mw-parser-output .navbox-abovebelow,.mw-parser-output .navbox-group,.mw-parser-output .navbox-subgroup .navbox-title{background-color:#ddf;color:inherit}.mw-parser-output .navbox-subgroup .navbox-group,.mw-parser-output .navbox-subgroup .navbox-abovebelow{background-color:#e6e6ff;color:inherit}.mw-parser-output .navbox-even{background-color:#f7f7f7;color:inherit}.mw-parser-output .navbox-odd{background-color:transparent;color:inherit}.mw-parser-output .navbox .hlist td dl,.mw-parser-output .navbox .hlist td ol,.mw-parser-output .navbox .hlist td ul,.mw-parser-output .navbox td.hlist dl,.mw-parser-output .navbox td.hlist ol,.mw-parser-output .navbox td.hlist ul{padding:0.125em 0}.mw-parser-output .navbox .navbar{display:block;font-size:100%}.mw-parser-output .navbox-title .navbar{float:left;text-align:left;margin-right:0.5em}body.skin--responsive .mw-parser-output .navbox-image img{max-width:none!important}@media print{body.ns-0 .mw-parser-output .navbox{display:none!important}}.mw-parser-output .nobold{font-weight:normal}

| .mw-parser-output .navbar{display:inline;font-size:88%;font-weight:normal}.mw-parser-output .navbar-collapse{float:left;text-align:left}.mw-parser-output .navbar-boxtext{word-spacing:0}.mw-parser-output .navbar ul{display:inline-block;white-space:nowrap;line-height:inherit}.mw-parser-output .navbar-brackets::before{margin-right:-0.125em;content:"[ "}.mw-parser-output .navbar-brackets::after{margin-left:-0.125em;content:" ]"}.mw-parser-output .navbar li{word-spacing:-0.125em}.mw-parser-output .navbar a>span,.mw-parser-output .navbar a>abbr{text-decoration:inherit}.mw-parser-output .navbar-mini abbr{font-variant:small-caps;border-bottom:none;text-decoration:none;cursor:inherit}.mw-parser-output .navbar-ct-full{font-size:114%;margin:0 7em}.mw-parser-output .navbar-ct-mini{font-size:114%;margin:0 4em}html.skin-theme-clientpref-night .mw-parser-output .navbar li a abbr{color:var(--color-base)!important}@media(prefers-color-scheme:dark){html.skin-theme-clientpref-os .mw-parser-output .navbar li a abbr{color:var(--color-base)!important}}@media print{.mw-parser-output .navbar{display:none!important}} - [v](/wiki/Template:Probability_distributions "Template:Probability distributions") - [t](/wiki/Template_talk:Probability_distributions "Template talk:Probability distributions") - [e](/wiki/Special:EditPage/Template:Probability_distributions "Special:EditPage/Template:Probability distributions")  [Probability distributions](/wiki/Probability_distribution "Probability distribution") ([list](/wiki/List_of_probability_distributions "List of probability distributions")) | |
| --- | --- |
| Discrete  univariate | |  |  | | --- | --- | | with finite  support | - [Benford](/wiki/Benford%27s_law "Benford's law") - [Bernoulli](/wiki/Bernoulli_distribution "Bernoulli distribution") - [Beta-binomial](/wiki/Beta-binomial_distribution "Beta-binomial distribution") - [Binomial](/wiki/Binomial_distribution "Binomial distribution") - [Categorical](/wiki/Categorical_distribution "Categorical distribution") - [Hypergeometric](/wiki/Hypergeometric_distribution "Hypergeometric distribution")   - [Negative](/wiki/Negative_hypergeometric_distribution "Negative hypergeometric distribution") - [Poisson binomial](/wiki/Poisson_binomial_distribution "Poisson binomial distribution") - [Rademacher](/wiki/Rademacher_distribution "Rademacher distribution") - [Soliton](/wiki/Soliton_distribution "Soliton distribution") - [Discrete uniform](/wiki/Discrete_uniform_distribution "Discrete uniform distribution") - [Zipf](/wiki/Zipf%27s_law "Zipf's law") - [Zipf–Mandelbrot](/wiki/Zipf%E2%80%93Mandelbrot_law "Zipf–Mandelbrot law") | | with infinite  support | - [Beta negative binomial](/wiki/Beta_negative_binomial_distribution "Beta negative binomial distribution") - [Borel](/wiki/Borel_distribution "Borel distribution") - [Conway–Maxwell–Poisson](/wiki/Conway%E2%80%93Maxwell%E2%80%93Poisson_distribution "Conway–Maxwell–Poisson distribution") - [Discrete phase-type](/wiki/Discrete_phase-type_distribution "Discrete phase-type distribution") - [Delaporte](/wiki/Delaporte_distribution "Delaporte distribution") - [Extended negative binomial](/wiki/Extended_negative_binomial_distribution "Extended negative binomial distribution") - [Flory–Schulz](/wiki/Flory%E2%80%93Schulz_distribution "Flory–Schulz distribution") - [Gauss–Kuzmin](/wiki/Gauss%E2%80%93Kuzmin_distribution "Gauss–Kuzmin distribution") - [Geometric](/wiki/Geometric_distribution "Geometric distribution") - [Logarithmic](/wiki/Logarithmic_distribution "Logarithmic distribution") - [Mixed Poisson](/wiki/Mixed_Poisson_distribution "Mixed Poisson distribution") - [Negative binomial](/wiki/Negative_binomial_distribution "Negative binomial distribution") - [Panjer](/wiki/(a,b,0)_class_of_distributions "(a,b,0) class of distributions") - [Parabolic fractal](/wiki/Parabolic_fractal_distribution "Parabolic fractal distribution") - [Poisson](/wiki/Poisson_distribution "Poisson distribution") - [Skellam](/wiki/Skellam_distribution "Skellam distribution") - [Yule–Simon](/wiki/Yule%E2%80%93Simon_distribution "Yule–Simon distribution") - [Zeta](/wiki/Zeta_distribution "Zeta distribution") | |
| Continuous  univariate | |  |  | | --- | --- | | supported on a  bounded interval | - [Arcsine](/wiki/Arcsine_distribution "Arcsine distribution") - [ARGUS](/wiki/ARGUS_distribution "ARGUS distribution") - [Balding–Nichols](/wiki/Balding%E2%80%93Nichols_model "Balding–Nichols model") - [Bates](/wiki/Bates_distribution "Bates distribution") - [Beta](/wiki/Beta_distribution "Beta distribution")   - [Generalized](/wiki/Generalized_beta_distribution "Generalized beta distribution") - [Beta rectangular](/wiki/Beta_rectangular_distribution "Beta rectangular distribution") - [Continuous Bernoulli](/wiki/Continuous_Bernoulli_distribution "Continuous Bernoulli distribution") - [Continuous binomial](/wiki/Continuous_binomial_distribution "Continuous binomial distribution") - [Irwin–Hall](/wiki/Irwin%E2%80%93Hall_distribution "Irwin–Hall distribution") - [Kumaraswamy](/wiki/Kumaraswamy_distribution "Kumaraswamy distribution") - [Logit-normal](/wiki/Logit-normal_distribution "Logit-normal distribution") - [Noncentral beta](/wiki/Noncentral_beta_distribution "Noncentral beta distribution") - [PERT](/wiki/PERT_distribution "PERT distribution") - [Power function](/w/index.php?title=Power_function_distribution&action=edit&redlink=1 "Power function distribution (page does not exist)") - [Raised cosine](/wiki/Raised_cosine_distribution "Raised cosine distribution") - [Reciprocal](/wiki/Reciprocal_distribution "Reciprocal distribution") - [Triangular](/wiki/Triangular_distribution "Triangular distribution") - [U-quadratic](/wiki/U-quadratic_distribution "U-quadratic distribution") - [Uniform](/wiki/Continuous_uniform_distribution "Continuous uniform distribution") - [Wigner semicircle](/wiki/Wigner_semicircle_distribution "Wigner semicircle distribution") | | supported on a  semi-infinite  interval | - [Benini](/wiki/Benini_distribution "Benini distribution") - [Benktander 1st kind](/wiki/Benktander_type_I_distribution "Benktander type I distribution") - [Benktander 2nd kind](/wiki/Benktander_type_II_distribution "Benktander type II distribution") - [Beta prime](/wiki/Beta_prime_distribution "Beta prime distribution") - [Burr](/wiki/Burr_distribution "Burr distribution") - [Chi](/wiki/Chi_distribution "Chi distribution") - [Chi-squared](/wiki/Chi-squared_distribution "Chi-squared distribution")   - [Noncentral](/wiki/Noncentral_chi-squared_distribution "Noncentral chi-squared distribution")   - [Inverse](/wiki/Inverse-chi-squared_distribution "Inverse-chi-squared distribution")     - [Scaled](/wiki/Scaled_inverse_chi-squared_distribution "Scaled inverse chi-squared distribution") - [Dagum](/wiki/Dagum_distribution "Dagum distribution") - [Davis](/wiki/Davis_distribution "Davis distribution") - [Erlang](/wiki/Erlang_distribution "Erlang distribution")   - [Hyper](/wiki/Hyper-Erlang_distribution "Hyper-Erlang distribution") - [Exponential](/wiki/Exponential_distribution "Exponential distribution")   - [Hyperexponential](/wiki/Hyperexponential_distribution "Hyperexponential distribution")   - [Hypoexponential](/wiki/Hypoexponential_distribution "Hypoexponential distribution")   - [Logarithmic](/wiki/Exponential-logarithmic_distribution "Exponential-logarithmic distribution") - [*F*](/wiki/F-distribution "F-distribution")   - [Noncentral](/wiki/Noncentral_F-distribution "Noncentral F-distribution") - [Folded normal](/wiki/Folded_normal_distribution "Folded normal distribution") - [Fréchet](/wiki/Fr%C3%A9chet_distribution "Fréchet distribution") - [Gamma](/wiki/Gamma_distribution "Gamma distribution")   - [Generalized](/wiki/Generalized_gamma_distribution "Generalized gamma distribution")   - [Inverse](/wiki/Inverse-gamma_distribution "Inverse-gamma distribution") - [gamma/Gompertz](/wiki/Gamma/Gompertz_distribution "Gamma/Gompertz distribution") - [Gompertz](/wiki/Gompertz_distribution "Gompertz distribution")   - [Shifted](/wiki/Shifted_Gompertz_distribution "Shifted Gompertz distribution") - [Half-logistic](/wiki/Half-logistic_distribution "Half-logistic distribution") - [Half-normal](/wiki/Half-normal_distribution "Half-normal distribution") - [Hotelling's *T*-squared](/wiki/Hotelling%27s_T-squared_distribution "Hotelling's T-squared distribution") - [Hartman–Watson](/wiki/Hartman%E2%80%93Watson_distribution "Hartman–Watson distribution") - [Inverse Gaussian](/wiki/Inverse_Gaussian_distribution "Inverse Gaussian distribution")   - [Generalized](/wiki/Generalized_inverse_Gaussian_distribution "Generalized inverse Gaussian distribution") - [Kolmogorov](/wiki/Kolmogorov%E2%80%93Smirnov_test "Kolmogorov–Smirnov test") - [Lévy](/wiki/L%C3%A9vy_distribution "Lévy distribution") - [Log-Cauchy](/wiki/Log-Cauchy_distribution "Log-Cauchy distribution") - [Log-Laplace](/wiki/Log-Laplace_distribution "Log-Laplace distribution") - [Log-logistic](/wiki/Log-logistic_distribution "Log-logistic distribution") - [Log-normal](/wiki/Log-normal_distribution "Log-normal distribution") - [Log-t](/wiki/Log-t_distribution "Log-t distribution") - [Lomax](/wiki/Lomax_distribution "Lomax distribution") - [Matrix-exponential](/wiki/Matrix-exponential_distribution "Matrix-exponential distribution") - [Maxwell–Boltzmann](/wiki/Maxwell%E2%80%93Boltzmann_distribution "Maxwell–Boltzmann distribution") - [Maxwell–Jüttner](/wiki/Maxwell%E2%80%93J%C3%BCttner_distribution "Maxwell–Jüttner distribution") - [Mittag-Leffler](/wiki/Mittag-Leffler_distribution "Mittag-Leffler distribution") - [Nakagami](/wiki/Nakagami_distribution "Nakagami distribution") - [Pareto](/wiki/Pareto_distribution "Pareto distribution") - [Phase-type](/wiki/Phase-type_distribution "Phase-type distribution") - [Poly-Weibull](/wiki/Poly-Weibull_distribution "Poly-Weibull distribution") - [Rayleigh](/wiki/Rayleigh_distribution "Rayleigh distribution") - [Relativistic Breit–Wigner](/wiki/Relativistic_Breit%E2%80%93Wigner_distribution "Relativistic Breit–Wigner distribution") - [Rice](/wiki/Rice_distribution "Rice distribution") - [Truncated normal](/wiki/Truncated_normal_distribution "Truncated normal distribution") - [type-2 Gumbel](/wiki/Type-2_Gumbel_distribution "Type-2 Gumbel distribution") - Weibull   - [Discrete](/wiki/Discrete_Weibull_distribution "Discrete Weibull distribution") - [Wilks's lambda](/wiki/Wilks%27s_lambda_distribution "Wilks's lambda distribution") | | supported  on the whole  real line | - [Cauchy](/wiki/Cauchy_distribution "Cauchy distribution") - [Exponential power](/wiki/Generalized_normal_distribution#Version_1 "Generalized normal distribution") - [Fisher's *z*](/wiki/Fisher%27s_z-distribution "Fisher's z-distribution") - [Kaniadakis κ-Gaussian](/wiki/Kaniadakis_Gaussian_distribution "Kaniadakis Gaussian distribution") - [Gaussian *q*](/wiki/Gaussian_q-distribution "Gaussian q-distribution") - [Generalized hyperbolic](/wiki/Generalised_hyperbolic_distribution "Generalised hyperbolic distribution") - [Generalized logistic (logistic-beta)](/wiki/Generalized_logistic_distribution "Generalized logistic distribution") - [Generalized normal](/wiki/Generalized_normal_distribution "Generalized normal distribution") - [Geometric stable](/wiki/Geometric_stable_distribution "Geometric stable distribution") - [Gumbel](/wiki/Gumbel_distribution "Gumbel distribution") - [Holtsmark](/wiki/Holtsmark_distribution "Holtsmark distribution") - [Hyperbolic secant](/wiki/Hyperbolic_secant_distribution "Hyperbolic secant distribution") - [Johnson's *SU*](/wiki/Johnson%27s_SU-distribution "Johnson's SU-distribution") - [Landau](/wiki/Landau_distribution "Landau distribution") - [Laplace](/wiki/Laplace_distribution "Laplace distribution")   - [Asymmetric](/wiki/Asymmetric_Laplace_distribution "Asymmetric Laplace distribution") - [Logistic](/wiki/Logistic_distribution "Logistic distribution") - [Noncentral *t*](/wiki/Noncentral_t-distribution "Noncentral t-distribution") - [Normal (Gaussian)](/wiki/Normal_distribution "Normal distribution") - [Normal-inverse Gaussian](/wiki/Normal-inverse_Gaussian_distribution "Normal-inverse Gaussian distribution") - [Skew normal](/wiki/Skew_normal_distribution "Skew normal distribution") - [Slash](/wiki/Slash_distribution "Slash distribution") - [Stable](/wiki/Stable_distribution "Stable distribution") - [Student's *t*](/wiki/Student%27s_t-distribution "Student's t-distribution") - [Tracy–Widom](/wiki/Tracy%E2%80%93Widom_distribution "Tracy–Widom distribution") - [Variance-gamma](/wiki/Variance-gamma_distribution "Variance-gamma distribution") - [Voigt](/wiki/Voigt_profile "Voigt profile") | | with support  whose type varies | - [Generalized chi-squared](/wiki/Generalized_chi-squared_distribution "Generalized chi-squared distribution") - [Generalized extreme value](/wiki/Generalized_extreme_value_distribution "Generalized extreme value distribution") - [Generalized Pareto](/wiki/Generalized_Pareto_distribution "Generalized Pareto distribution") - [Marchenko–Pastur](/wiki/Marchenko%E2%80%93Pastur_distribution "Marchenko–Pastur distribution") - [Kaniadakis *κ*-exponential](/wiki/Kaniadakis_Exponential_distribution "Kaniadakis Exponential distribution") - [Kaniadakis *κ*-Gamma](/wiki/Kaniadakis_Gamma_distribution "Kaniadakis Gamma distribution") - [Kaniadakis *κ*-Weibull](/wiki/Kaniadakis_Weibull_distribution "Kaniadakis Weibull distribution") - [Kaniadakis *κ*-Logistic](/wiki/Kaniadakis_Logistic_distribution "Kaniadakis Logistic distribution") - [Kaniadakis *κ*-Erlang](/wiki/Kaniadakis_Erlang_distribution "Kaniadakis Erlang distribution") - [*q*-exponential](/wiki/Q-exponential_distribution "Q-exponential distribution") - [*q*-Gaussian](/wiki/Q-Gaussian_distribution "Q-Gaussian distribution") - [*q*-Weibull](/wiki/Q-Weibull_distribution "Q-Weibull distribution") - [Shifted log-logistic](/wiki/Shifted_log-logistic_distribution "Shifted log-logistic distribution") - [Tukey lambda](/wiki/Tukey_lambda_distribution "Tukey lambda distribution") | |
| Mixed  univariate | |  |  | | --- | --- | | continuous- discrete | - [Rectified Gaussian](/wiki/Rectified_Gaussian_distribution "Rectified Gaussian distribution") | |
| [Multivariate  (joint)](/wiki/Joint_probability_distribution "Joint probability distribution") | - *Discrete:* - [Ewens](/wiki/Ewens%27s_sampling_formula "Ewens's sampling formula") - [Multinomial](/wiki/Multinomial_distribution "Multinomial distribution")   - [Dirichlet](/wiki/Dirichlet-multinomial_distribution "Dirichlet-multinomial distribution")   - [Negative](/wiki/Negative_multinomial_distribution "Negative multinomial distribution") - *Continuous:* - [Dirichlet](/wiki/Dirichlet_distribution "Dirichlet distribution")   - [Generalized](/wiki/Generalized_Dirichlet_distribution "Generalized Dirichlet distribution") - [Multivariate Laplace](/wiki/Multivariate_Laplace_distribution "Multivariate Laplace distribution") - [Multivariate normal](/wiki/Multivariate_normal_distribution "Multivariate normal distribution") - [Multivariate stable](/wiki/Multivariate_stable_distribution "Multivariate stable distribution") - [Multivariate *t*](/wiki/Multivariate_t-distribution "Multivariate t-distribution") - [Normal-gamma](/wiki/Normal-gamma_distribution "Normal-gamma distribution")   - [Inverse](/wiki/Normal-inverse-gamma_distribution "Normal-inverse-gamma distribution") - *[Matrix-valued:](/wiki/Random_matrix "Random matrix")* - [LKJ](/wiki/Lewandowski-Kurowicka-Joe_distribution "Lewandowski-Kurowicka-Joe distribution") - [Matrix beta](/wiki/Matrix_variate_beta_distribution "Matrix variate beta distribution") - [Matrix *F*](/wiki/Matrix_F-distribution "Matrix F-distribution") - [Matrix normal](/wiki/Matrix_normal_distribution "Matrix normal distribution") - [Matrix *t*](/wiki/Matrix_t-distribution "Matrix t-distribution") - [Matrix gamma](/wiki/Matrix_gamma_distribution "Matrix gamma distribution")   - [Inverse](/wiki/Inverse_matrix_gamma_distribution "Inverse matrix gamma distribution") - [Wishart](/wiki/Wishart_distribution "Wishart distribution")   - [Normal](/wiki/Normal-Wishart_distribution "Normal-Wishart distribution")   - [Inverse](/wiki/Inverse-Wishart_distribution "Inverse-Wishart distribution")   - [Normal-inverse](/wiki/Normal-inverse-Wishart_distribution "Normal-inverse-Wishart distribution")   - [Complex](/wiki/Complex_Wishart_distribution "Complex Wishart distribution") - [Uniform distribution on a Stiefel manifold](/wiki/Uniform_distribution_on_a_Stiefel_manifold "Uniform distribution on a Stiefel manifold") |
| [Directional](/wiki/Directional_statistics "Directional statistics") | *Univariate (circular) [directional](/wiki/Directional_statistics "Directional statistics")*  [Circular uniform](/wiki/Circular_uniform_distribution "Circular uniform distribution")  [Univariate von Mises](/wiki/Von_Mises_distribution "Von Mises distribution")  [Wrapped normal](/wiki/Wrapped_normal_distribution "Wrapped normal distribution")  [Wrapped Cauchy](/wiki/Wrapped_Cauchy_distribution "Wrapped Cauchy distribution")  [Wrapped exponential](/wiki/Wrapped_exponential_distribution "Wrapped exponential distribution")  [Wrapped asymmetric Laplace](/wiki/Wrapped_asymmetric_Laplace_distribution "Wrapped asymmetric Laplace distribution")  [Wrapped Lévy](/wiki/Wrapped_L%C3%A9vy_distribution "Wrapped Lévy distribution")  *Bivariate (spherical)*  [Kent](/wiki/Kent_distribution "Kent distribution")  *Bivariate (toroidal)*  [Bivariate von Mises](/wiki/Bivariate_von_Mises_distribution "Bivariate von Mises distribution")  *Multivariate*  [von Mises–Fisher](/wiki/Von_Mises%E2%80%93Fisher_distribution "Von Mises–Fisher distribution")  [Bingham](/wiki/Bingham_distribution "Bingham distribution") |
| [Degenerate](/wiki/Degenerate_distribution "Degenerate distribution")  and [singular](/wiki/Singular_distribution "Singular distribution") | *Degenerate*  [Dirac delta function](/wiki/Dirac_delta_function "Dirac delta function")  *Singular*  [Cantor](/wiki/Cantor_distribution "Cantor distribution") |
| Families | - [Circular](/wiki/Circular_distribution "Circular distribution") - [Compound Poisson](/wiki/Compound_Poisson_distribution "Compound Poisson distribution") - [Elliptical](/wiki/Elliptical_distribution "Elliptical distribution") - [Exponential](/wiki/Exponential_family "Exponential family") - [Natural exponential](/wiki/Natural_exponential_family "Natural exponential family") - [Location–scale](/wiki/Location%E2%80%93scale_family "Location–scale family") - [Maximum entropy](/wiki/Maximum_entropy_probability_distribution "Maximum entropy probability distribution") - [Mixture](/wiki/Mixture_distribution "Mixture distribution") - [Pearson](/wiki/Pearson_distribution "Pearson distribution") - [Tweedie](/wiki/Tweedie_distribution "Tweedie distribution") - [Wrapped](/wiki/Wrapped_distribution "Wrapped distribution") |
| - [Category](/wiki/Category:Probability_distributions "Category:Probability distributions") - [Commons](https://commons.wikimedia.org/wiki/Category:Probability_distributions "commons:Category:Probability distributions") | |

.mw-parser-output .tooltip-dotted{border-bottom:1px dotted;cursor:help}

| [Authority control databases](/wiki/Help:Authority_control "Help:Authority control") [Edit this at Wikidata](https://www.wikidata.org/wiki/Q732332#identifiers "Edit this at Wikidata") | |
| --- | --- |
| International | - [GND](https://d-nb.info/gnd/4065029-7) |
| National | - [United States](https://id.loc.gov/authorities/sh85145945) - [Latvia](https://kopkatalogs.lv/F?func=direct&local_base=lnc10&doc_number=000351715&P_CON_LNG=ENG) - [Israel](https://www.nli.org.il/en/authorities/987007553502605171) |
| Other | - [Yale LUX](https://lux.collections.yale.edu/view/concept/4a7fdbc3-683c-40ab-a4b2-48c7333c0921) |
