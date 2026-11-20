<!-- category: facility_layout -->
# Queueing theory

Mathematical study of waiting lines, or queues

[![](//thumb.wikimedia.org/wikipedia/commons/thumb/2/2b/ServidorParalelo.jpg/250px-ServidorParalelo.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail)](/wiki/File:ServidorParalelo.jpg)

[Queue networks](#Queueing_networks) are systems in which single queues are connected by a routing network. In this image, servers are represented by circles, queues by a series of rectangles and the routing network by arrows. In the study of queue networks one typically tries to obtain the [equilibrium distribution](/wiki/Equilibrium_distribution "Equilibrium distribution") of the network, although in many applications the study of the [transient state](/wiki/Transient_state "Transient state") is fundamental.

**Queueing theory** is the mathematical study of [queues, or waiting lines](/wiki/Queue_area "Queue area").[[1]](#cite_note-sun-1) A queueing model is constructed so that queue lengths and waiting time can be predicted.[[1]](#cite_note-sun-1) Queueing theory is generally considered a branch of [operations research](/wiki/Operations_research "Operations research") because the results are often used when making business decisions about the resources needed to provide a service.

Queueing theory has its origins in research by [Agner Krarup Erlang](/wiki/Agner_Krarup_Erlang "Agner Krarup Erlang"), who created models to describe the system of incoming calls at the Copenhagen Telephone Exchange Company.[[1]](#cite_note-sun-1) These ideas were seminal to the field of [teletraffic engineering](/wiki/Teletraffic_engineering "Teletraffic engineering") and have since seen applications in [telecommunications](/wiki/Telecommunications "Telecommunications"), [traffic engineering](/wiki/Traffic_engineering_(transportation) "Traffic engineering (transportation)"), [computing](/wiki/Computing "Computing"),[[2]](#cite_note-2) [project management](/wiki/Project_management "Project management"), and particularly [industrial engineering](/wiki/Industrial_engineering "Industrial engineering"), where they are applied in the design of factories, shops, offices, and hospitals.[[3]](#cite_note-3)[[4]](#cite_note-4)

## Description

[[edit](/w/index.php?title=Queueing_theory&veaction=edit&section=1 "Edit section: Description") | [edit source](/w/index.php?title=Queueing_theory&action=edit&section=1 "Edit section's source code: Description")]

Queueing theory is one of the major areas of study in the discipline of [management science](/wiki/Management_science "Management science"). Through management science, businesses are able to solve a variety of problems using different scientific and mathematical approaches. Queueing analysis is the probabilistic analysis of waiting lines, and thus the results, also referred to as the operating characteristics, are probabilistic rather than deterministic.[[5]](#cite_note-taylor_2019-5) The probability that n customers are in the queueing system, the average number of customers in the queueing system, the average number of customers in the waiting line, the average time spent by a customer in the total queuing system, the average time spent by a customer in the waiting line, and finally the probability that the server is busy or idle are all of the different operating characteristics that these queueing models compute.[[5]](#cite_note-taylor_2019-5) The overall goal of queueing analysis is to compute these characteristics for the current system and then test several alternatives that could lead to improvement. Computing the operating characteristics for the current system and comparing the values to the characteristics of the alternative systems allows managers to see the pros and cons of each potential option. These systems help in the final decision making process by showing ways to increase savings, reduce waiting time, improve efficiency, etc. The main queueing models that can be used are the single-server waiting line system and the multiple-server waiting line system, which are discussed further below. These models can be further differentiated depending on whether service times are constant or undefined, the queue length is finite, the calling population is finite, etc.[[5]](#cite_note-taylor_2019-5)

## Single queueing nodes

[[edit](/w/index.php?title=Queueing_theory&veaction=edit&section=2 "Edit section: Single queueing nodes") | [edit source](/w/index.php?title=Queueing_theory&action=edit&section=2 "Edit section's source code: Single queueing nodes")]

A *queue* or *queueing node* can be thought of as nearly a [black box](/wiki/Black_box "Black box"). *Jobs* (also called *customers* or *requests*, depending on the field) arrive to the queue, possibly wait some time, take some time being processed, and then depart from the queue.

[![](//upload.wikimedia.org/wikipedia/commons/a/a8/Black_box_queue_diagram.png?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail_unscaled)](/wiki/File:Black_box_queue_diagram.png)

A black box. Jobs arrive to, and depart from, the queue.

However, the queueing node is not quite a pure black box since some information is needed about the inside of the queueing node. The queue has one or more *servers* which can each be paired with an arriving job. When the job is completed and departs, that server will again be free to be paired with another arriving job.

[![](//upload.wikimedia.org/wikipedia/commons/0/06/Queueing_node_service_digram.png?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail_unscaled)](/wiki/File:Queueing_node_service_digram.png)

A queueing node with 3 servers. Server **a** is idle, and thus an arrival is given to it to process. Server **b** is currently busy and will take some time before it can complete service of its job. Server **c** has just completed service of a job and thus will be next to receive an arriving job.

An analogy often used is that of the cashier at a supermarket. Customers arrive, are processed by the cashier, and depart. Each cashier processes one customer at a time, and hence this is a queueing node with only one server. A setting where a customer will leave immediately if the cashier is busy when the customer arrives, is referred to as a queue with no *buffer* (or no *waiting area*). A setting with a waiting zone for up to *n* customers is called a queue with a buffer of size *n*.

### Birth-death process

[[edit](/w/index.php?title=Queueing_theory&veaction=edit&section=3 "Edit section: Birth-death process") | [edit source](/w/index.php?title=Queueing_theory&action=edit&section=3 "Edit section's source code: Birth-death process")]

.mw-parser-output .hatnote{font-style:italic}.mw-parser-output div.hatnote{padding-left:1.6em;margin-bottom:0.5em}.mw-parser-output .hatnote i{font-style:normal}.mw-parser-output .hatnote+.mw-empty-elt+.hatnote{margin-top:-0.5em}@media print{body.ns-0 .mw-parser-output .hatnote{display:none!important}}

See also: [Survival analysis](/wiki/Survival_analysis "Survival analysis")

The behaviour of a single queue (also called a *queueing node*) can be described by a [birth–death process](/wiki/Birth%E2%80%93death_process "Birth–death process"), which describes the arrivals and departures from the queue, along with the number of jobs currently in the system. If *k* denotes the number of jobs in the system (either being serviced or waiting if the queue has a buffer of waiting jobs), then an arrival increases *k* by 1 and a departure decreases *k* by 1.

The system transitions between values of *k* by *births* and *deaths*, which occur at the arrival rates 

λ

i
{\displaystyle \lambda \_{i}}
![{\displaystyle \lambda _{i}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/72fde940918edf84caf3d406cc7d31949166820f) and the departure rates 

μ

i
{\displaystyle \mu \_{i}}
![{\displaystyle \mu _{i}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/dea0a0293841cce9eef98b55e53a92b82ae59ee4) for each job 

i
{\displaystyle i}
![{\displaystyle i}](https://wikimedia.org/api/rest_v1/media/math/render/svg/add78d8608ad86e54951b8c8bd6c8d8416533d20). For a queue, these rates are generally considered not to vary with the number of jobs in the queue, so a single [average](/wiki/Average "Average") rate of arrivals/departures per unit time is assumed. Under this assumption, this process has an arrival rate of 

λ
=

avg
(

λ

1
,

λ

2
,
…
,

λ

k
)
{\displaystyle \lambda ={\text{avg}}(\lambda \_{1},\lambda \_{2},\dots ,\lambda \_{k})}
![{\displaystyle \lambda ={\text{avg}}(\lambda _{1},\lambda _{2},\dots ,\lambda _{k})}](https://wikimedia.org/api/rest_v1/media/math/render/svg/51d649c6a53479477273095ca7d04d5fe906bfce) and a departure rate of 

μ
=

avg
(

μ

1
,

μ

2
,
…
,

μ

k
)
{\displaystyle \mu ={\text{avg}}(\mu \_{1},\mu \_{2},\dots ,\mu \_{k})}
![{\displaystyle \mu ={\text{avg}}(\mu _{1},\mu _{2},\dots ,\mu _{k})}](https://wikimedia.org/api/rest_v1/media/math/render/svg/fd14f9b6b1c5a8ca77e65b070ba29f05b971d6f5).

[![](//upload.wikimedia.org/wikipedia/commons/2/28/BD-proces.png?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail_unscaled)](/wiki/File:BD-proces.png)

A birth–death process. The values in the circles represent the state of the system, which evolves based on arrival rates *λi* and departure rates *μi*.

[![](//thumb.wikimedia.org/wikipedia/commons/thumb/6/65/Mm1_queue.svg/250px-Mm1_queue.svg.png?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail)](/wiki/File:Mm1_queue.svg)

A queue with 1 server, arrival rate *λ* and departure rate *μ*

#### Balance equations

[[edit](/w/index.php?title=Queueing_theory&veaction=edit&section=4 "Edit section: Balance equations") | [edit source](/w/index.php?title=Queueing_theory&action=edit&section=4 "Edit section's source code: Balance equations")]

The [steady state](/wiki/Steady_state "Steady state") equations for the birth-and-death process, known as the [balance equations](/wiki/Balance_equation "Balance equation"), are as follows. Here 

P

n
{\displaystyle P\_{n}}
![{\displaystyle P_{n}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/5949c8b1de44005a1af3a11188361f2a830842d1) denotes the steady state probability to be in state *n*.

μ

1

P

1
=

λ

0

P

0
{\displaystyle \mu \_{1}P\_{1}=\lambda \_{0}P\_{0}}
![{\displaystyle \mu _{1}P_{1}=\lambda _{0}P_{0}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/a7a4e5285814b8eea220253084ab8f82def8fba4)

λ

0

P

0
+

μ

2

P

2
=
(

λ

1
+

μ

1
)

P

1
{\displaystyle \lambda \_{0}P\_{0}+\mu \_{2}P\_{2}=(\lambda \_{1}+\mu \_{1})P\_{1}}
![{\displaystyle \lambda _{0}P_{0}+\mu _{2}P_{2}=(\lambda _{1}+\mu _{1})P_{1}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/a51aff4e76af68ff0f33d4e8df7880aadfae1a7e)

λ

n
−
1

P

n
−
1
+

μ

n
+
1

P

n
+
1
=
(

λ

n
+

μ

n
)

P

n
{\displaystyle \lambda \_{n-1}P\_{n-1}+\mu \_{n+1}P\_{n+1}=(\lambda \_{n}+\mu \_{n})P\_{n}}
![{\displaystyle \lambda _{n-1}P_{n-1}+\mu _{n+1}P_{n+1}=(\lambda _{n}+\mu _{n})P_{n}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/cd1372440063dca352ad00370fdd7720bb8fd791)
The first two equations imply

P

1
=

λ

0

μ

1

P

0
{\displaystyle P\_{1}={\frac {\lambda \_{0}}{\mu \_{1}}}P\_{0}}
![{\displaystyle P_{1}={\frac {\lambda _{0}}{\mu _{1}}}P_{0}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/cf82d5d7d9b0fa14ba1e64073b6b5a7f432980a2)
and

P

2
=

λ

1

μ

2

P

1
+

1

μ

2
(

μ

1

P

1
−

λ

0

P

0
)
=

λ

1

μ

2

P

1
=

λ

1

λ

0

μ

2

μ

1

P

0
{\displaystyle P\_{2}={\frac {\lambda \_{1}}{\mu \_{2}}}P\_{1}+{\frac {1}{\mu \_{2}}}(\mu \_{1}P\_{1}-\lambda \_{0}P\_{0})={\frac {\lambda \_{1}}{\mu \_{2}}}P\_{1}={\frac {\lambda \_{1}\lambda \_{0}}{\mu \_{2}\mu \_{1}}}P\_{0}}
![{\displaystyle P_{2}={\frac {\lambda _{1}}{\mu _{2}}}P_{1}+{\frac {1}{\mu _{2}}}(\mu _{1}P_{1}-\lambda _{0}P_{0})={\frac {\lambda _{1}}{\mu _{2}}}P_{1}={\frac {\lambda _{1}\lambda _{0}}{\mu _{2}\mu _{1}}}P_{0}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/97f411f6bc8dbeb0d88db374f3efb34e9ef4ed5f)
By mathematical induction,

P

n
=

λ

n
−
1

λ

n
−
2
⋯

λ

0

μ

n

μ

n
−
1
⋯

μ

1

P

0
=

P

0

∏

i
=
0

n
−
1

λ

i

μ

i
+
1
{\displaystyle P\_{n}={\frac {\lambda \_{n-1}\lambda \_{n-2}\cdots \lambda \_{0}}{\mu \_{n}\mu \_{n-1}\cdots \mu \_{1}}}P\_{0}=P\_{0}\prod \_{i=0}^{n-1}{\frac {\lambda \_{i}}{\mu \_{i+1}}}}
![{\displaystyle P_{n}={\frac {\lambda _{n-1}\lambda _{n-2}\cdots \lambda _{0}}{\mu _{n}\mu _{n-1}\cdots \mu _{1}}}P_{0}=P_{0}\prod _{i=0}^{n-1}{\frac {\lambda _{i}}{\mu _{i+1}}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/55649d575f6f927af2f10ec5bc4c33c61b44ba14)
The condition 

∑

n
=
0

∞

P

n
=

P

0
+

P

0

∑

n
=
1

∞

∏

i
=
0

n
−
1

λ

i

μ

i
+
1
=
1
{\displaystyle \sum \_{n=0}^{\infty }P\_{n}=P\_{0}+P\_{0}\sum \_{n=1}^{\infty }\prod \_{i=0}^{n-1}{\frac {\lambda \_{i}}{\mu \_{i+1}}}=1}
![{\displaystyle \sum _{n=0}^{\infty }P_{n}=P_{0}+P_{0}\sum _{n=1}^{\infty }\prod _{i=0}^{n-1}{\frac {\lambda _{i}}{\mu _{i+1}}}=1}](https://wikimedia.org/api/rest_v1/media/math/render/svg/a63e8bb72ee3619d1be086ac4fc83a86ab1e2ac1) leads to

P

0
=

1

1
+

∑

n
=
1

∞

∏

i
=
0

n
−
1

λ

i

μ

i
+
1
{\displaystyle P\_{0}={\frac {1}{1+\sum \_{n=1}^{\infty }\prod \_{i=0}^{n-1}{\frac {\lambda \_{i}}{\mu \_{i+1}}}}}}
![{\displaystyle P_{0}={\frac {1}{1+\sum _{n=1}^{\infty }\prod _{i=0}^{n-1}{\frac {\lambda _{i}}{\mu _{i+1}}}}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/8f069108a04b258551e4e7cc8da2e06c16ee6bf2)

which, together with the equation for 

P

n
{\displaystyle P\_{n}}
![{\displaystyle P_{n}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/5949c8b1de44005a1af3a11188361f2a830842d1) 

(
n
≥
1
)
{\displaystyle (n\geq 1)}
![{\displaystyle (n\geq 1)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/9ba2ba4672a730074e09f736217cd4dc797688c4), fully describes the required steady state probabilities.

### Kendall's notation

[[edit](/w/index.php?title=Queueing_theory&veaction=edit&section=5 "Edit section: Kendall's notation") | [edit source](/w/index.php?title=Queueing_theory&action=edit&section=5 "Edit section's source code: Kendall's notation")]

Main article: [Kendall's notation](/wiki/Kendall%27s_notation "Kendall's notation")

Single queueing nodes are usually described using Kendall's notation in the form A/S/*c* where *A* describes the distribution of durations between each arrival to the queue, *S* the distribution of service times for jobs, and *c* the number of servers at the node.[[6]](#cite_note-tijms-6)[[7]](#cite_note-7) For an example of the notation, the [M/M/1 queue](/wiki/M/M/1_queue "M/M/1 queue") is a simple model where a single server serves jobs that arrive according to a [Poisson process](/wiki/Poisson_process "Poisson process") (where inter-arrival durations are [exponentially distributed](/wiki/Exponentially_distributed "Exponentially distributed")) and have exponentially distributed service times (the M denotes a [Markov process](/wiki/Markov_process "Markov process")). In an [M/G/1 queue](/wiki/M/G/1_queue "M/G/1 queue"), the G stands for *general* and indicates an arbitrary [probability distribution](/wiki/Probability_distribution "Probability distribution") for service times.

### Example analysis of an M/M/1 queue

[[edit](/w/index.php?title=Queueing_theory&veaction=edit&section=6 "Edit section: Example analysis of an M/M/1 queue") | [edit source](/w/index.php?title=Queueing_theory&action=edit&section=6 "Edit section's source code: Example analysis of an M/M/1 queue")]

Consider a queue with one server and the following characteristics:

- *λ
  {\displaystyle \lambda }
  ![{\displaystyle \lambda }](https://wikimedia.org/api/rest_v1/media/math/render/svg/b43d0ea3c9c025af1be9128e62a18fa74bedda2a)*: the arrival rate (the reciprocal of the expected time between each customer arriving, e.g. 10 customers per second)
- *μ
  {\displaystyle \mu }
  ![{\displaystyle \mu }](https://wikimedia.org/api/rest_v1/media/math/render/svg/9fd47b2a39f7a7856952afec1f1db72c67af6161)*: the reciprocal of the mean service time (the expected number of consecutive service completions per the same unit time, e.g. per 30 seconds)
- *n*: the parameter characterizing the number of customers in the system
- P

  n
  {\displaystyle P\_{n}}
  ![{\displaystyle P_{n}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/5949c8b1de44005a1af3a11188361f2a830842d1): the probability of there being *n* customers in the system in steady state

Further, let 

E

n
{\displaystyle E\_{n}}
![{\displaystyle E_{n}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/ad6b82f2a00af6c9efd4c16d4e99329605645c0c) represent the number of times the system enters state *n*, and 

L

n
{\displaystyle L\_{n}}
![{\displaystyle L_{n}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/ebec334cb04f246db1139e2ca6be0b957d2ef520) represent the number of times the system leaves state *n*. Then 

|

E

n
−

L

n
|
∈
{
0
,
1
}
{\displaystyle \left\vert E\_{n}-L\_{n}\right\vert \in \{0,1\}}
![{\displaystyle \left\vert E_{n}-L_{n}\right\vert \in \{0,1\}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/dfaafc34f6462bc71ab4a5194a0bb972f8fb7332) for all *n*. That is, the number of times the system leaves a state differs by at most 1 from the number of times it enters that state, since it will either return into that state at some time in the future (

E

n
=

L

n
{\displaystyle E\_{n}=L\_{n}}
![{\displaystyle E_{n}=L_{n}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/89b7c47a5be1ac22f494b768c0f1b56e09544dc5)) or not (

|

E

n
−

L

n
|
=
1
{\displaystyle \left\vert E\_{n}-L\_{n}\right\vert =1}
![{\displaystyle \left\vert E_{n}-L_{n}\right\vert =1}](https://wikimedia.org/api/rest_v1/media/math/render/svg/d65367f17e71d4151a16ec5b659c183aeb415c2e)).

When the system arrives at a steady state, the arrival rate should be equal to the departure rate.

Thus the balanced equations

μ

P

1
=
λ

P

0
{\displaystyle \mu P\_{1}=\lambda P\_{0}}
![{\displaystyle \mu P_{1}=\lambda P_{0}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/0cef41c1fd4cd03b9c4e2716b34e78137e79bc59)

λ

P

0
+
μ

P

2
=
(
λ
+
μ
)

P

1
{\displaystyle \lambda P\_{0}+\mu P\_{2}=(\lambda +\mu )P\_{1}}
![{\displaystyle \lambda P_{0}+\mu P_{2}=(\lambda +\mu )P_{1}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/e61a6b6f06fd2c96aa97cc3918aea6005781772f)

λ

P

n
−
1
+
μ

P

n
+
1
=
(
λ
+
μ
)

P

n
{\displaystyle \lambda P\_{n-1}+\mu P\_{n+1}=(\lambda +\mu )P\_{n}}
![{\displaystyle \lambda P_{n-1}+\mu P_{n+1}=(\lambda +\mu )P_{n}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/d5b89b81570c52e1dc2e05762817f5fdc73b03f2)
imply

P

n
=

λ
μ

P

n
−
1
,
 
n
=
1
,
2
,
…
{\displaystyle P\_{n}={\frac {\lambda }{\mu }}P\_{n-1},\ n=1,2,\ldots }
![{\displaystyle P_{n}={\frac {\lambda }{\mu }}P_{n-1},\ n=1,2,\ldots }](https://wikimedia.org/api/rest_v1/media/math/render/svg/40b487bcc4eb2e715c4bc6c0cdd2d4a738c39709)
The fact that 

P

0
+

P

1
+
⋯
=
1
{\displaystyle P\_{0}+P\_{1}+\cdots =1}
![{\displaystyle P_{0}+P_{1}+\cdots =1}](https://wikimedia.org/api/rest_v1/media/math/render/svg/2c547fd67b3ec848ee87d9b1173aef5deacff28d) leads to the [geometric distribution](/wiki/Geometric_distribution "Geometric distribution") formula

P

n
=
(
1
−
ρ
)

ρ

n
{\displaystyle P\_{n}=(1-\rho )\rho ^{n}}
![{\displaystyle P_{n}=(1-\rho )\rho ^{n}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/008d712dff3854a99eb83857de02434f0ce48b4c)
where 

ρ
=

λ
μ
<
1
{\displaystyle \rho ={\frac {\lambda }{\mu }}<1}
![{\displaystyle \rho ={\frac {\lambda }{\mu }}<1}](https://wikimedia.org/api/rest_v1/media/math/render/svg/dd6b4bc487c1cb0f02f86e51abae727c5c4a5ee5).

### Simple two-equation queue

[[edit](/w/index.php?title=Queueing_theory&veaction=edit&section=7 "Edit section: Simple two-equation queue") | [edit source](/w/index.php?title=Queueing_theory&action=edit&section=7 "Edit section's source code: Simple two-equation queue")]

A common basic queueing system is attributed to [Erlang](/wiki/Agner_Krarup_Erlang "Agner Krarup Erlang") and is a modification of [Little's Law](/wiki/Little%27s_Law "Little's Law"). Given an arrival rate *λ*, a dropout rate *σ*, and a departure rate *μ*, length of the queue *L* is defined as:

L
=

λ
−
σ
μ
{\displaystyle L={\frac {\lambda -\sigma }{\mu }}}
![{\displaystyle L={\frac {\lambda -\sigma }{\mu }}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/2e05024fcce4a8c1c414acc00b1ca517bea6c8e7)

Assuming an exponential distribution for the rates, the waiting time *W* can be defined as the proportion of arrivals that are served. This is equal to the exponential survival rate of those who do not drop out over the waiting period, giving:

μ
λ
=

e

−
W

μ
{\displaystyle {\frac {\mu }{\lambda }}=e^{-W{\mu }}}
![{\displaystyle {\frac {\mu }{\lambda }}=e^{-W{\mu }}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/504b727b98da9f16e4bdbedcaecb12e4de4dc522)

The second equation is commonly rewritten as:

W
=

1
μ

l
n

λ
μ
{\displaystyle W={\frac {1}{\mu }}\mathrm {ln} {\frac {\lambda }{\mu }}}
![{\displaystyle W={\frac {1}{\mu }}\mathrm {ln} {\frac {\lambda }{\mu }}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/89cbeab3b567b6bf4b0be6a4f4e44222c885ec9b)

The two-stage one-box model is common in [epidemiology](/wiki/Epidemiology "Epidemiology").[[8]](#cite_note-8)

## History

[[edit](/w/index.php?title=Queueing_theory&veaction=edit&section=8 "Edit section: History") | [edit source](/w/index.php?title=Queueing_theory&action=edit&section=8 "Edit section's source code: History")]

In 1909, [Agner Krarup Erlang](/wiki/Agner_Krarup_Erlang "Agner Krarup Erlang"), a Danish engineer who worked for the Copenhagen Telephone Exchange, published the first paper on what would now be called queueing theory.[[9]](#cite_note-9)[[10]](#cite_note-10)[[11]](#cite_note-11) He modeled the number of telephone calls arriving at an exchange by a [Poisson process](/wiki/Poisson_process "Poisson process") and solved the [M/D/1 queue](/wiki/M/D/1_queue "M/D/1 queue") in 1917 and [M/D/*k* queueing](/wiki/M/D/k_queue "M/D/k queue") model in 1920.[[12]](#cite_note-century-12) In Kendall's notation:

- M stands for *Markov* or *memoryless*, and means arrivals occur according to a Poisson process
- D stands for *deterministic*, and means jobs arriving at the queue require a fixed amount of service
- *k* describes the number of servers at the queueing node (*k* = 1, 2, 3, ...)

If the node has more jobs than servers, then jobs will queue and wait for service.

The [M/G/1 queue](/wiki/M/G/1_queue "M/G/1 queue") was solved by [Felix Pollaczek](/wiki/Felix_Pollaczek "Felix Pollaczek") in 1930,[[13]](#cite_note-13) a solution later recast in probabilistic terms by [Aleksandr Khinchin](/wiki/Aleksandr_Khinchin "Aleksandr Khinchin") and now known as the [Pollaczek–Khinchine formula](/wiki/Pollaczek%E2%80%93Khinchine_formula "Pollaczek–Khinchine formula").[[12]](#cite_note-century-12)[[14]](#cite_note-century1-14)

After the 1940s, queueing theory became an area of research interest to mathematicians.[[14]](#cite_note-century1-14) In 1953, [David George Kendall](/wiki/David_George_Kendall "David George Kendall") solved the GI/M/*k* queue[[15]](#cite_note-15) and introduced the modern notation for queues, now known as [Kendall's notation](/wiki/Kendall%27s_notation "Kendall's notation"). In 1957, Pollaczek studied the GI/G/1 using an [integral equation](/wiki/Integral_equation "Integral equation").[[16]](#cite_note-16) [John Kingman](/wiki/John_Kingman "John Kingman") gave a formula for the [mean waiting time](/wiki/Mean_sojourn_time "Mean sojourn time") in a [G/G/1 queue](/wiki/G/G/1_queue "G/G/1 queue"), now known as [Kingman's formula](/wiki/Kingman%27s_formula "Kingman's formula").[[17]](#cite_note-17)

[Leonard Kleinrock](/wiki/Leonard_Kleinrock "Leonard Kleinrock") worked on the application of queueing theory to [message switching](/wiki/Message_switching "Message switching") in the early 1960s and [packet switching](/wiki/Packet_switching "Packet switching") in the early 1970s. His initial contribution to this field was his doctoral thesis at the [Massachusetts Institute of Technology](/wiki/Massachusetts_Institute_of_Technology "Massachusetts Institute of Technology") in 1962, published in book form in 1964. His theoretical work published in the early 1970s underpinned the use of packet switching in the [ARPANET](/wiki/ARPANET "ARPANET"), a forerunner to the Internet.

The [matrix geometric method](/wiki/Matrix_geometric_method "Matrix geometric method") and [matrix analytic methods](/wiki/Matrix_analytic_method "Matrix analytic method") have allowed queues with [phase-type distributed](/wiki/Phase-type_distribution "Phase-type distribution") inter-arrival and service time distributions to be considered.[[18]](#cite_note-18)

Systems with coupled orbits are an important part in queueing theory in the application to wireless networks and signal processing.[[19]](#cite_note-19)

Modern day application of queueing theory concerns among other things [product development](/wiki/Product_development "Product development") where (material) products have a spatiotemporal existence, in the sense that products have a certain volume and a certain duration.[[20]](#cite_note-20)

Problems such as performance metrics for the [M/G/*k* queue](/wiki/M/G/k_queue "M/G/k queue") remain an open problem.[[12]](#cite_note-century-12)[[14]](#cite_note-century1-14)

## Service disciplines

[[edit](/w/index.php?title=Queueing_theory&veaction=edit&section=9 "Edit section: Service disciplines") | [edit source](/w/index.php?title=Queueing_theory&action=edit&section=9 "Edit section's source code: Service disciplines")]

"First come, first served" redirects here. For the Kool Keith album, see [First Come, First Served](/wiki/First_Come,_First_Served "First Come, First Served").

Various scheduling policies can be used at queueing nodes:

[First in, first out](/wiki/FIFO_(computing_and_electronics) "FIFO (computing and electronics)")
:   [![](//thumb.wikimedia.org/wikipedia/commons/thumb/d/d3/Fifo_queue.png/250px-Fifo_queue.png?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail)](/wiki/File:Fifo_queue.png)

    First in first out (FIFO) queue example

     Also called *first-come, first-served* (FCFS),[[21]](#cite_note-Manuel-21) this principle states that customers are served one at a time and that the customer that has been waiting the longest is served first.[[22]](#cite_note-penttinen-22)

[Last in, first out](/wiki/LIFO_(computing) "LIFO (computing)")
:   This principle also serves customers one at a time, but the customer with the shortest [waiting time](/wiki/Mean_sojourn_time "Mean sojourn time") will be served first.[[22]](#cite_note-penttinen-22) Also known as a [stack](/wiki/Stack_(data_structure) "Stack (data structure)").

[Processor sharing](/wiki/Processor_sharing "Processor sharing")
:   Service capacity is shared equally between customers.[[22]](#cite_note-penttinen-22)

Service in random order (SIRO)
:   Also called *random order of service* (ROS), this discipline states that the next job served is selected at random from the jobs waiting in the queue.

Priority
:   Customers with high priority are served first.[[22]](#cite_note-penttinen-22) Priority queues can be of two types: *non-preemptive* (where a job in service cannot be interrupted) and *preemptive* (where a job in service can be interrupted by a higher-priority job). No work is lost in either model.[[23]](#cite_note-23)

[Shortest job first](/wiki/Shortest_job_first "Shortest job first")
:   The next job to be served is the one with the smallest size.[[24]](#cite_note-24)

Preemptive shortest job first
:   The next job to be served is the one with the smallest original size.[[25]](#cite_note-25)

[Shortest remaining processing time](/wiki/Shortest_remaining_processing_time "Shortest remaining processing time")
:   The next job to serve is the one with the smallest remaining processing requirement.[[26]](#cite_note-26)

Service facility
:   - Single server: customers line up and there is only one server
    - Several parallel servers (single queue): customers line up and there are several servers
    - Several parallel servers (several queues): there are many counters and customers can decide for which to queue

Unreliable server
:   Server failures occur according to a stochastic (random) process (usually Poisson) and are followed by setup periods during which the server is unavailable. The interrupted customer remains in the service area until server is fixed.[[27]](#cite_note-27)

Customer waiting behavior
:   - Balking: customers decide not to join the queue if it is too long
    - Jockeying: customers switch between queues if they think they will get served faster by doing so
    - Reneging: customers leave the queue if they have waited too long for service

    Arriving customers not served (either due to the queue having no buffer, or due to balking or reneging by the customer) are also known as *dropouts*. The average rate of dropouts is a significant parameter describing a queue.

## Queueing networks

[[edit](/w/index.php?title=Queueing_theory&veaction=edit&section=10 "Edit section: Queueing networks") | [edit source](/w/index.php?title=Queueing_theory&action=edit&section=10 "Edit section's source code: Queueing networks")]

Queue networks are systems in which multiple queues are connected by *customer routing*. When a customer is serviced at one node, it can join another node and queue for service, or leave the network.

For networks of *m* nodes, the state of the system can be described by an *m*–dimensional vector (*x*1, *x*2, ..., *x**m*) where *x**i* represents the number of customers at each node.

The simplest non-trivial networks of queues are called [tandem queues](/wiki/Jackson_network "Jackson network").[[28]](#cite_note-28) The first significant results in this area were [Jackson networks](/wiki/Jackson_network "Jackson network"),[[29]](#cite_note-29)[[30]](#cite_note-jackson-30) for which an efficient [product-form stationary distribution](/wiki/Product-form_stationary_distribution "Product-form stationary distribution") exists and the [mean value analysis](/wiki/Mean_value_analysis "Mean value analysis")[[31]](#cite_note-31) (which allows average metrics such as throughput and sojourn times) can be computed.[[32]](#cite_note-32) If the total number of customers in the network remains constant, the network is called a *closed network* and has been shown to also have a product–form stationary distribution by the [Gordon–Newell theorem](/wiki/Gordon%E2%80%93Newell_theorem "Gordon–Newell theorem").[[33]](#cite_note-33) This result was extended to the [BCMP network](/wiki/BCMP_network "BCMP network"),[[34]](#cite_note-34) where a network with very general service time, regimes, and customer routing is shown to also exhibit a product–form stationary distribution. The [normalizing constant](/wiki/Normalizing_constant "Normalizing constant") can be calculated with the [Buzen's algorithm](/wiki/Buzen%27s_algorithm "Buzen's algorithm"), proposed in 1973.[[35]](#cite_note-buzen-1973-35)

Networks of customers have also been investigated, such as [Kelly networks](/wiki/Kelly_network "Kelly network"), where customers of different classes experience different priority levels at different service nodes.[[36]](#cite_note-36) Another type of network are [G-networks](/wiki/G-networks "G-networks"), first proposed by [Erol Gelenbe](/wiki/Erol_Gelenbe "Erol Gelenbe") in 1993:[[37]](#cite_note-37) these networks do not assume exponential time distributions like the classic Jackson network.

### Routing algorithms

[[edit](/w/index.php?title=Queueing_theory&veaction=edit&section=11 "Edit section: Routing algorithms") | [edit source](/w/index.php?title=Queueing_theory&action=edit&section=11 "Edit section's source code: Routing algorithms")]

See also: [Stochastic scheduling](/wiki/Stochastic_scheduling "Stochastic scheduling")

In discrete-time networks where there is a constraint on which service nodes can be active at any time, the max-weight scheduling algorithm chooses a service policy to give optimal throughput in the case that each job visits only a single-person service node.[[21]](#cite_note-Manuel-21) In the more general case where jobs can visit more than one node, [backpressure routing](/wiki/Backpressure_routing "Backpressure routing") gives optimal throughput. A [network scheduler](/wiki/Network_scheduler "Network scheduler") must choose a [queueing algorithm](/wiki/Queueing_algorithm "Queueing algorithm"), which affects the characteristics of the larger network.[[38]](#cite_note-38)

### Mean-field limits

[[edit](/w/index.php?title=Queueing_theory&veaction=edit&section=12 "Edit section: Mean-field limits") | [edit source](/w/index.php?title=Queueing_theory&action=edit&section=12 "Edit section's source code: Mean-field limits")]

[Mean-field models](/wiki/Mean-field_model "Mean-field model") consider the limiting behaviour of the [empirical measure](/wiki/Empirical_measure "Empirical measure") (proportion of queues in different states) as the number of queues *m* approaches infinity. The impact of other queues on any given queue in the network is approximated by a differential equation. The deterministic model converges to the same stationary distribution as the original model.[[39]](#cite_note-39)

### Heavy traffic/diffusion approximations

[[edit](/w/index.php?title=Queueing_theory&veaction=edit&section=13 "Edit section: Heavy traffic/diffusion approximations") | [edit source](/w/index.php?title=Queueing_theory&action=edit&section=13 "Edit section's source code: Heavy traffic/diffusion approximations")]

Main article: [Heavy traffic approximation](/wiki/Heavy_traffic_approximation "Heavy traffic approximation")

In a system with high occupancy rates (utilisation near 1), a heavy traffic approximation can be used to approximate the queueing length process by a [reflected Brownian motion](/wiki/Reflected_Brownian_motion "Reflected Brownian motion"),[[40]](#cite_note-40) [Ornstein–Uhlenbeck process](/wiki/Ornstein%E2%80%93Uhlenbeck_process "Ornstein–Uhlenbeck process"), or more general [diffusion process](/wiki/Diffusion_process "Diffusion process").[[41]](#cite_note-41) The number of dimensions of the Brownian process is equal to the number of queueing nodes, with the diffusion restricted to the non-negative [orthant](/wiki/Orthant "Orthant").

### Fluid limits

[[edit](/w/index.php?title=Queueing_theory&veaction=edit&section=14 "Edit section: Fluid limits") | [edit source](/w/index.php?title=Queueing_theory&action=edit&section=14 "Edit section's source code: Fluid limits")]

Main article: [Fluid limit](/wiki/Fluid_limit "Fluid limit")

Fluid models are continuous deterministic analogs of queueing networks obtained by taking the limit when the process is scaled in time and space, allowing heterogeneous objects. This scaled trajectory converges to a deterministic equation which allows the stability of the system to be proven. It is known that a queueing network can be stable but have an unstable fluid limit.[[42]](#cite_note-42)

### Queueing applications

[[edit](/w/index.php?title=Queueing_theory&veaction=edit&section=15 "Edit section: Queueing applications") | [edit source](/w/index.php?title=Queueing_theory&action=edit&section=15 "Edit section's source code: Queueing applications")]

Queueing theory finds widespread application in computer science and information technology. In networking, for instance, queues are integral to routers and switches, where packets queue up for transmission. By applying queueing theory principles, designers can optimize these systems, ensuring responsive performance and efficient resource utilization.

Beyond the technological realm, queueing theory is relevant to everyday experiences. Whether waiting in line at a supermarket or for public transportation, understanding the principles of queueing theory provides valuable insights into optimizing these systems for enhanced user satisfaction. At some point, everyone will be involved in an aspect of queuing. What some may view to be an inconvenience could possibly be the most effective method.
Queueing theory, a discipline rooted in applied mathematics and computer science, is a field dedicated to the study and analysis of queues, or waiting lines, and their implications across a diverse range of applications. This theoretical framework has proven instrumental in understanding and optimizing the efficiency of systems characterized by the presence of queues. The study of queues is essential in contexts such as traffic systems, computer networks, telecommunications, and service operations.

Queueing theory delves into various foundational concepts, with the arrival process and service process being central. The arrival process describes the manner in which entities join the queue over time, often modeled using stochastic processes like Poisson processes. The efficiency of queueing systems is gauged through key performance metrics. These include the average queue length, average wait time, and system throughput. These metrics provide insights into the system's functionality, guiding decisions aimed at enhancing performance and reducing wait times.[[43]](#cite_note-43)[[44]](#cite_note-44)[[45]](#cite_note-45)

## See also

[[edit](/w/index.php?title=Queueing_theory&veaction=edit&section=16 "Edit section: See also") | [edit source](/w/index.php?title=Queueing_theory&action=edit&section=16 "Edit section's source code: See also")]

.mw-parser-output .div-col{margin-top:0.3em;column-width:30em}.mw-parser-output .div-col-small{font-size:90%}.mw-parser-output .div-col-rules{column-rule:1px solid #aaa}.mw-parser-output .div-col dl,.mw-parser-output .div-col ol,.mw-parser-output .div-col ul{margin-top:0}.mw-parser-output .div-col li,.mw-parser-output .div-col dd{page-break-inside:avoid;break-inside:avoid-column}

- [Ehrenfest model](/wiki/Ehrenfest_model "Ehrenfest model")
- [Erlang unit](/wiki/Erlang_unit "Erlang unit")
- [Line management](/wiki/Line_management "Line management")
- [Network simulation](/wiki/Network_simulation "Network simulation")
- [Project production management](/wiki/Project_production_management "Project production management")
- [Queue area](/wiki/Queue_area "Queue area")
- [Queueing delay](/wiki/Queueing_delay "Queueing delay")
- [Queue management system](/wiki/Queue_management_system "Queue management system")
- [Queuing Rule of Thumb](/wiki/Queuing_Rule_of_Thumb "Queuing Rule of Thumb")
- [Random early detection](/wiki/Random_early_detection "Random early detection")
- [Renewal theory](/wiki/Renewal_theory "Renewal theory")
- [Throughput](/wiki/Throughput "Throughput")
- [Scheduling (computing)](/wiki/Scheduling_(computing) "Scheduling (computing)")
- [Traffic jam](/wiki/Traffic_jam "Traffic jam")
- [Traffic generation model](/wiki/Traffic_generation_model "Traffic generation model")
- [Flow network](/wiki/Flow_network "Flow network")

## References

[[edit](/w/index.php?title=Queueing_theory&veaction=edit&section=17 "Edit section: References") | [edit source](/w/index.php?title=Queueing_theory&action=edit&section=17 "Edit section's source code: References")]

.mw-parser-output .reflist-columns-2{column-width:30em}.mw-parser-output .reflist-columns-3{column-width:25em}body.skin-vector-2022 .mw-parser-output .reflist-columns-2{column-width:27em}body.skin-vector-2022 .mw-parser-output .reflist-columns-3{column-width:22.5em}.mw-parser-output .references[data-mw-group=upper-alpha]{list-style-type:upper-alpha}.mw-parser-output .references[data-mw-group=upper-roman]{list-style-type:upper-roman}.mw-parser-output .references[data-mw-group=lower-alpha]{list-style-type:lower-alpha}.mw-parser-output .references[data-mw-group=lower-greek]{list-style-type:lower-greek}.mw-parser-output .references[data-mw-group=lower-roman]{list-style-type:lower-roman}.mw-parser-output div.reflist-liststyle-upper-alpha .references{list-style-type:upper-alpha}.mw-parser-output div.reflist-liststyle-upper-roman .references{list-style-type:upper-roman}.mw-parser-output div.reflist-liststyle-lower-alpha .references{list-style-type:lower-alpha}.mw-parser-output div.reflist-liststyle-lower-greek .references{list-style-type:lower-greek}.mw-parser-output div.reflist-liststyle-lower-roman .references{list-style-type:lower-roman}

1. ^ [***a***](#cite_ref-sun_1-0) [***b***](#cite_ref-sun_1-1) [***c***](#cite_ref-sun_1-2) .mw-parser-output cite.citation{font-style:inherit;word-wrap:break-word}.mw-parser-output .citation q{quotes:"\"""\"""'""'"}.mw-parser-output .citation:target{background-color:rgba(0,127,255,0.133)}.mw-parser-output .id-lock-free.id-lock-free a{background:url("//upload.wikimedia.org/wikipedia/commons/6/65/Lock-green.svg")right 0.1em center/9px no-repeat}.mw-parser-output .id-lock-limited.id-lock-limited a,.mw-parser-output .id-lock-registration.id-lock-registration a{background:url("//upload.wikimedia.org/wikipedia/commons/d/d6/Lock-gray-alt-2.svg")right 0.1em center/9px no-repeat}.mw-parser-output .id-lock-subscription.id-lock-subscription a{background:url("//upload.wikimedia.org/wikipedia/commons/a/aa/Lock-red-alt-2.svg")right 0.1em center/9px no-repeat}.mw-parser-output .cs1-ws-icon a{background:url("//upload.wikimedia.org/wikipedia/commons/4/4c/Wikisource-logo.svg")right 0.1em center/12px no-repeat}body:not(.skin-timeless):not(.skin-minerva) .mw-parser-output .id-lock-free a,body:not(.skin-timeless):not(.skin-minerva) .mw-parser-output .id-lock-limited a,body:not(.skin-timeless):not(.skin-minerva) .mw-parser-output .id-lock-registration a,body:not(.skin-timeless):not(.skin-minerva) .mw-parser-output .id-lock-subscription a,body:not(.skin-timeless):not(.skin-minerva) .mw-parser-output .cs1-ws-icon a{background-size:contain;padding:0 1em 0 0}.mw-parser-output .cs1-code{color:inherit;background:inherit;border:none;padding:inherit}.mw-parser-output .cs1-hidden-error{display:none;color:var(--color-error,#bf3c2c)}.mw-parser-output .cs1-visible-error{color:var(--color-error,#bf3c2c)}.mw-parser-output .cs1-maint{display:none;color:#085;margin-left:0.3em}.mw-parser-output .cs1-kern-left{padding-left:0.2em}.mw-parser-output .cs1-kern-right{padding-right:0.2em}.mw-parser-output .citation .mw-selflink{font-weight:inherit}@media screen{.mw-parser-output .cs1-format{font-size:95%}html.skin-theme-clientpref-night .mw-parser-output .cs1-maint{color:#18911f}}@media screen and (prefers-color-scheme:dark){html.skin-theme-clientpref-os .mw-parser-output .cs1-maint{color:#18911f}}Sundarapandian, V. (2009). "7. Queueing Theory". *Probability, Statistics and Queueing Theory*. PHI Learning. [ISBN](/wiki/ISBN_(identifier) "ISBN (identifier)") [978-81-203-3844-9](/wiki/Special:BookSources/978-81-203-3844-9 "Special:BookSources/978-81-203-3844-9").
2. **[^](#cite_ref-2)** Lawrence W. Dowdy, Virgilio A.F. Almeida, Daniel A. Menasce. ["Performance by Design: Computer Capacity Planning by Example"](http://www.cs.gmu.edu/~menasce/perfbyd/). [Archived](https://web.archive.org/web/20160506025515/http://cs.gmu.edu/~menasce/perfbyd/) from the original on 2016-05-06. Retrieved 2009-07-08.
3. **[^](#cite_ref-3)** Schlechter, Kira (March 2, 2009). ["Hershey Medical Center to open redesigned emergency room"](http://www.pennlive.com/midstate/index.ssf/2009/03/hershey_med_to_open_redesigned.html). *The Patriot-News*. [Archived](https://web.archive.org/web/20160629151917/http://www.pennlive.com/midstate/index.ssf/2009/03/hershey_med_to_open_redesigned.html) from the original on June 29, 2016. Retrieved March 12, 2009.
4. **[^](#cite_ref-4)** Mayhew, Les; Smith, David (December 2006). [*Using queuing theory to analyse completion times in accident and emergency departments in the light of the Government 4-hour target*](https://web.archive.org/web/20210907100556/https://openaccess.city.ac.uk/id/eprint/2309/). [Cass Business School](/wiki/Cass_Business_School "Cass Business School"). [ISBN](/wiki/ISBN_(identifier) "ISBN (identifier)") [978-1-905752-06-5](/wiki/Special:BookSources/978-1-905752-06-5 "Special:BookSources/978-1-905752-06-5"). Archived from [the original](https://openaccess.city.ac.uk/id/eprint/2309/) on September 7, 2021. Retrieved 2008-05-20.
5. ^ [***a***](#cite_ref-taylor_2019_5-0) [***b***](#cite_ref-taylor_2019_5-1) [***c***](#cite_ref-taylor_2019_5-2) Taylor, Bernard W. (2019). *Introduction to management science* (13th ed.). New York: Pearson. [ISBN](/wiki/ISBN_(identifier) "ISBN (identifier)") [978-0-13-473066-0](/wiki/Special:BookSources/978-0-13-473066-0 "Special:BookSources/978-0-13-473066-0").
6. **[^](#cite_ref-tijms_6-0)** Tijms, H.C, *Algorithmic Analysis of Queues*, Chapter 9 in A First Course in Stochastic Models, Wiley, Chichester, 2003
7. **[^](#cite_ref-7)** [Kendall, D. G.](/wiki/David_George_Kendall "David George Kendall") (1953). ["Stochastic Processes Occurring in the Theory of Queues and their Analysis by the Method of the Imbedded Markov Chain"](https://doi.org/10.1214%2Faoms%2F1177728975). *The Annals of Mathematical Statistics*. **24** (3): 338–354. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1214/aoms/1177728975](https://doi.org/10.1214%2Faoms%2F1177728975). [JSTOR](/wiki/JSTOR_(identifier) "JSTOR (identifier)") [2236285](https://www.jstor.org/stable/2236285).
8. **[^](#cite_ref-8)** Hernández-Suarez, Carlos (2010). ["An application of queuing theory to SIS and SEIS epidemic models"](https://doi.org/10.3934%2Fmbe.2010.7.809). *Math. Biosci*. **7** (4): 809–823. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.3934/mbe.2010.7.809](https://doi.org/10.3934%2Fmbe.2010.7.809). [PMID](/wiki/PMID_(identifier) "PMID (identifier)") [21077709](https://pubmed.ncbi.nlm.nih.gov/21077709).
9. **[^](#cite_ref-9)** ["Agner Krarup Erlang (1878-1929) | plus.maths.org"](http://pass.maths.org.uk/issue2/erlang/index.html). Pass.maths.org.uk. 1997-04-30. [Archived](https://web.archive.org/web/20081007225944/http://pass.maths.org.uk/issue2/erlang/index.html) from the original on 2008-10-07. Retrieved 2013-04-22.
10. **[^](#cite_ref-10)** Asmussen, S. R.; [Boxma, O. J.](/wiki/Onno_Boxma "Onno Boxma") (2009). "Editorial introduction". *[Queueing Systems](/wiki/Queueing_Systems "Queueing Systems")*. **63** (1–4): 1–2. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1007/s11134-009-9151-8](https://doi.org/10.1007%2Fs11134-009-9151-8). [S2CID](/wiki/S2CID_(identifier) "S2CID (identifier)") [45664707](https://api.semanticscholar.org/CorpusID:45664707).
11. **[^](#cite_ref-11)** [Erlang, Agner Krarup](/wiki/Agner_Krarup_Erlang "Agner Krarup Erlang") (1909). ["The theory of probabilities and telephone conversations"](https://web.archive.org/web/20111001212934/http://oldwww.com.dtu.dk/teletraffic/erlangbook/pps131-137.pdf) (PDF). *Nyt Tidsskrift for Matematik B*. **20**: 33–39. Archived from [the original](http://oldwww.com.dtu.dk/teletraffic/erlangbook/pps131-137.pdf) (PDF) on 2011-10-01.
12. ^ [***a***](#cite_ref-century_12-0) [***b***](#cite_ref-century_12-1) [***c***](#cite_ref-century_12-2) [Kingman, J. F. C.](/wiki/John_Kingman "John Kingman") (2009). "The first Erlang century—and the next". *[Queueing Systems](/wiki/Queueing_Systems "Queueing Systems")*. **63** (1–4): 3–4. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1007/s11134-009-9147-4](https://doi.org/10.1007%2Fs11134-009-9147-4). [S2CID](/wiki/S2CID_(identifier) "S2CID (identifier)") [38588726](https://api.semanticscholar.org/CorpusID:38588726).
13. **[^](#cite_ref-13)** Pollaczek, F., Ueber eine Aufgabe der Wahrscheinlichkeitstheorie, Math. Z. 1930
14. ^ [***a***](#cite_ref-century1_14-0) [***b***](#cite_ref-century1_14-1) [***c***](#cite_ref-century1_14-2) [Whittle, P.](/wiki/Peter_Whittle_(mathematician) "Peter Whittle (mathematician)") (2002). ["Applied Probability in Great Britain"](https://doi.org/10.1287%2Fopre.50.1.227.17792). *[Operations Research](/wiki/Operations_Research_(journal) "Operations Research (journal)")*. **50** (1): 227–239. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1287/opre.50.1.227.17792](https://doi.org/10.1287%2Fopre.50.1.227.17792). [JSTOR](/wiki/JSTOR_(identifier) "JSTOR (identifier)") [3088474](https://www.jstor.org/stable/3088474).
15. **[^](#cite_ref-15)** Kendall, D.G.:Stochastic processes occurring in the theory of queues and their analysis by the method of the imbedded Markov chain, Ann. Math. Stat. 1953
16. **[^](#cite_ref-16)** Pollaczek, F., Problèmes Stochastiques posés par le phénomène de formation d'une queue
17. **[^](#cite_ref-17)** [Kingman, J. F. C.](/wiki/John_Kingman "John Kingman"); Atiyah (October 1961). "The single server queue in heavy traffic". *[Mathematical Proceedings of the Cambridge Philosophical Society](/wiki/Mathematical_Proceedings_of_the_Cambridge_Philosophical_Society "Mathematical Proceedings of the Cambridge Philosophical Society")*. **57** (4): 902. [Bibcode](/wiki/Bibcode_(identifier) "Bibcode (identifier)"):[1961PCPS...57..902K](https://ui.adsabs.harvard.edu/abs/1961PCPS...57..902K). [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1017/S0305004100036094](https://doi.org/10.1017%2FS0305004100036094). [JSTOR](/wiki/JSTOR_(identifier) "JSTOR (identifier)") [2984229](https://www.jstor.org/stable/2984229). [S2CID](/wiki/S2CID_(identifier) "S2CID (identifier)") [62590290](https://api.semanticscholar.org/CorpusID:62590290).
18. **[^](#cite_ref-18)** Ramaswami, V. (1988). "A stable recursion for the steady state vector in markov chains of m/g/1 type". *Communications in Statistics. Stochastic Models*. **4**: 183–188. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1080/15326348808807077](https://doi.org/10.1080%2F15326348808807077).
19. **[^](#cite_ref-19)** Morozov, E. (2017). "Stability analysis of a multiclass retrial system withcoupled orbit queues". *Proceedings of 14th European Workshop*. Lecture Notes in Computer Science. Vol. 17. pp. 85–98. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1007/978-3-319-66583-2\_6](https://doi.org/10.1007%2F978-3-319-66583-2_6). [ISBN](/wiki/ISBN_(identifier) "ISBN (identifier)") [978-3-319-66582-5](/wiki/Special:BookSources/978-3-319-66582-5 "Special:BookSources/978-3-319-66582-5").
20. **[^](#cite_ref-20)** Carlson, E.C.; Felder, R.M. (1992). ["Simulation and queueing network modeling of single-product production campaigns"](https://www.sciencedirect.com/science/article/abs/pii/0098135492800185). *Computers & Chemical Engineering*. **16** (7): 707–718. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1016/0098-1354(92)80018-5](https://doi.org/10.1016%2F0098-1354%2892%2980018-5).
21. ^ [***a***](#cite_ref-Manuel_21-0) [***b***](#cite_ref-Manuel_21-1) Manuel, Laguna (2011). [*Business Process Modeling, Simulation and Design*](https://books.google.com/books?id=d-V8c8YRJikC&q=%22First-come%2C+first-served%22+business&pg=PA178). Pearson Education India. p. 178. [ISBN](/wiki/ISBN_(identifier) "ISBN (identifier)") [978-81-317-6135-9](/wiki/Special:BookSources/978-81-317-6135-9 "Special:BookSources/978-81-317-6135-9"). Retrieved 6 October 2017.
22. ^ [***a***](#cite_ref-penttinen_22-0) [***b***](#cite_ref-penttinen_22-1) [***c***](#cite_ref-penttinen_22-2) [***d***](#cite_ref-penttinen_22-3) Penttinen A., *Chapter 8 – Queueing Systems*, Lecture Notes: S-38.145 - Introduction to Teletraffic Theory.
23. **[^](#cite_ref-23)** [Harchol-Balter, M.](/wiki/Mor_Harchol-Balter "Mor Harchol-Balter") (2012). "Scheduling: Non-Preemptive, Size-Based Policies". *Performance Modeling and Design of Computer Systems*. pp. 499–507. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1017/CBO9781139226424.039](https://doi.org/10.1017%2FCBO9781139226424.039). [ISBN](/wiki/ISBN_(identifier) "ISBN (identifier)") [978-1-139-22642-4](/wiki/Special:BookSources/978-1-139-22642-4 "Special:BookSources/978-1-139-22642-4").
24. **[^](#cite_ref-24)** Andrew S. Tanenbaum; Herbert Bos (2015). [*Modern Operating Systems*](https://books.google.com/books?id=9gqnngEACAAJ). Pearson. [ISBN](/wiki/ISBN_(identifier) "ISBN (identifier)") [978-0-13-359162-0](/wiki/Special:BookSources/978-0-13-359162-0 "Special:BookSources/978-0-13-359162-0").
25. **[^](#cite_ref-25)** [Harchol-Balter, M.](/wiki/Mor_Harchol-Balter "Mor Harchol-Balter") (2012). "Scheduling: Preemptive, Size-Based Policies". *Performance Modeling and Design of Computer Systems*. pp. 508–517. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1017/CBO9781139226424.040](https://doi.org/10.1017%2FCBO9781139226424.040). [ISBN](/wiki/ISBN_(identifier) "ISBN (identifier)") [978-1-139-22642-4](/wiki/Special:BookSources/978-1-139-22642-4 "Special:BookSources/978-1-139-22642-4").
26. **[^](#cite_ref-26)** [Harchol-Balter, M.](/wiki/Mor_Harchol-Balter "Mor Harchol-Balter") (2012). "Scheduling: SRPT and Fairness". *Performance Modeling and Design of Computer Systems*. pp. 518–530. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1017/CBO9781139226424.041](https://doi.org/10.1017%2FCBO9781139226424.041). [ISBN](/wiki/ISBN_(identifier) "ISBN (identifier)") [978-1-139-22642-4](/wiki/Special:BookSources/978-1-139-22642-4 "Special:BookSources/978-1-139-22642-4").
27. **[^](#cite_ref-27)** Dimitriou, I. (2019). "A Multiclass Retrial System With Coupled Orbits And Service Interruptions: Verification of Stability Conditions". *Proceedings of FRUCT 24*. **7**: 75–82.
28. **[^](#cite_ref-28)** ["Lecture 13: M/M/1 queues and queueing networks"](http://www.stats.ox.ac.uk/~winkel/bs3a07l13-14.pdf#page=4) (PDF). [Archived](https://web.archive.org/web/20170329085928/http://www.stats.ox.ac.uk/~winkel/bs3a07l13-14.pdf#page=4) (PDF) from the original on 2017-03-29. Retrieved 2018-08-02.
29. **[^](#cite_ref-29)** [Jackson, J. R.](/wiki/James_R._Jackson "James R. Jackson") (1957). "Networks of Waiting Lines". *Operations Research*. **5** (4): 518–521. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1287/opre.5.4.518](https://doi.org/10.1287%2Fopre.5.4.518). [JSTOR](/wiki/JSTOR_(identifier) "JSTOR (identifier)") [167249](https://www.jstor.org/stable/167249).
30. **[^](#cite_ref-jackson_30-0)** Jackson, James R. (Oct 1963). "Jobshop-like Queueing Systems". *[Management Science](/wiki/Management_Science:_A_Journal_of_the_Institute_for_Operations_Research_and_the_Management_Sciences "Management Science: A Journal of the Institute for Operations Research and the Management Sciences")*. **10** (1): 131–142. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1287/mnsc.1040.0268](https://doi.org/10.1287%2Fmnsc.1040.0268). [JSTOR](/wiki/JSTOR_(identifier) "JSTOR (identifier)") [2627213](https://www.jstor.org/stable/2627213).
31. **[^](#cite_ref-31)** Reiser, M.; Lavenberg, S. S. (1980). ["Mean-Value Analysis of Closed Multichain Queuing Networks"](https://doi.org/10.1145%2F322186.322195). *[Journal of the ACM](/wiki/Journal_of_the_ACM "Journal of the ACM")*. **27** (2): 313. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1145/322186.322195](https://doi.org/10.1145%2F322186.322195). [S2CID](/wiki/S2CID_(identifier) "S2CID (identifier)") [8694947](https://api.semanticscholar.org/CorpusID:8694947).
32. **[^](#cite_ref-32)** Van Dijk, N. M. (1993). ["On the arrival theorem for communication networks"](https://research.vu.nl/ws/files/73611045/Scanjob%20199100081). *Computer Networks and ISDN Systems*. **25** (10): 1135–2013. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1016/0169-7552(93)90073-D](https://doi.org/10.1016%2F0169-7552%2893%2990073-D). [S2CID](/wiki/S2CID_(identifier) "S2CID (identifier)") [45218280](https://api.semanticscholar.org/CorpusID:45218280). [Archived](https://web.archive.org/web/20190924062816/https://research.vu.nl/ws/files/73611045/Scanjob%2520199100081) from the original on 2019-09-24. Retrieved 2019-09-24.
33. **[^](#cite_ref-33)** Gordon, W. J.; [Newell, G. F.](/wiki/Gordon_F._Newell "Gordon F. Newell") (1967). "Closed Queuing Systems with Exponential Servers". *[Operations Research](/wiki/Operations_Research_(journal) "Operations Research (journal)")*. **15** (2): 254. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1287/opre.15.2.254](https://doi.org/10.1287%2Fopre.15.2.254). [JSTOR](/wiki/JSTOR_(identifier) "JSTOR (identifier)") [168557](https://www.jstor.org/stable/168557).
34. **[^](#cite_ref-34)** Baskett, F.; [Chandy, K. Mani](/wiki/K._Mani_Chandy "K. Mani Chandy"); Muntz, R.R.; Palacios, F.G. (1975). ["Open, closed and mixed networks of queues with different classes of customers"](https://doi.org/10.1145%2F321879.321887). *Journal of the ACM*. **22** (2): 248–260. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1145/321879.321887](https://doi.org/10.1145%2F321879.321887). [S2CID](/wiki/S2CID_(identifier) "S2CID (identifier)") [15204199](https://api.semanticscholar.org/CorpusID:15204199).
35. **[^](#cite_ref-buzen-1973_35-0)** [Buzen, J. P.](/wiki/Jeffrey_P._Buzen "Jeffrey P. Buzen") (1973). ["Computational algorithms for closed queueing networks with exponential servers"](http://www-unix.ecs.umass.edu/~krishna/ece673/buzen.pdf) (PDF). *Communications of the ACM*. **16** (9): 527–531. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1145/362342.362345](https://doi.org/10.1145%2F362342.362345). [S2CID](/wiki/S2CID_(identifier) "S2CID (identifier)") [10702](https://api.semanticscholar.org/CorpusID:10702). [Archived](https://web.archive.org/web/20160513192804/http://www-unix.ecs.umass.edu/~krishna/ece673/buzen.pdf) (PDF) from the original on 2016-05-13. Retrieved 2015-09-01.
36. **[^](#cite_ref-36)** [Kelly, F. P.](/wiki/Frank_Kelly_(mathematician) "Frank Kelly (mathematician)") (1975). "Networks of Queues with Customers of Different Types". *Journal of Applied Probability*. **12** (3): 542–554. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.2307/3212869](https://doi.org/10.2307%2F3212869). [JSTOR](/wiki/JSTOR_(identifier) "JSTOR (identifier)") [3212869](https://www.jstor.org/stable/3212869). [S2CID](/wiki/S2CID_(identifier) "S2CID (identifier)") [51917794](https://api.semanticscholar.org/CorpusID:51917794).
37. **[^](#cite_ref-37)** [Gelenbe, Erol](/wiki/Erol_Gelenbe "Erol Gelenbe") (Sep 1993). "G-Networks with Triggered Customer Movement". *Journal of Applied Probability*. **30** (3): 742–748. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.2307/3214781](https://doi.org/10.2307%2F3214781). [JSTOR](/wiki/JSTOR_(identifier) "JSTOR (identifier)") [3214781](https://www.jstor.org/stable/3214781). [S2CID](/wiki/S2CID_(identifier) "S2CID (identifier)") [121673725](https://api.semanticscholar.org/CorpusID:121673725).
38. **[^](#cite_ref-38)** Newell, G. F. (1982). [*Applications of Queueing Theory*](https://doi.org/10.1007/978-94-009-5970-5). [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1007/978-94-009-5970-5](https://doi.org/10.1007%2F978-94-009-5970-5). [ISBN](/wiki/ISBN_(identifier) "ISBN (identifier)") [978-94-009-5972-9](/wiki/Special:BookSources/978-94-009-5972-9 "Special:BookSources/978-94-009-5972-9").
39. **[^](#cite_ref-39)** Bobbio, A.; Gribaudo, M.; Telek, M. S. (2008). "Analysis of Large Scale Interacting Systems by Mean Field Method". *2008 Fifth International Conference on Quantitative Evaluation of Systems*. p. 215. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1109/QEST.2008.47](https://doi.org/10.1109%2FQEST.2008.47). [ISBN](/wiki/ISBN_(identifier) "ISBN (identifier)") [978-0-7695-3360-5](/wiki/Special:BookSources/978-0-7695-3360-5 "Special:BookSources/978-0-7695-3360-5"). [S2CID](/wiki/S2CID_(identifier) "S2CID (identifier)") [2714909](https://api.semanticscholar.org/CorpusID:2714909).
40. **[^](#cite_ref-40)** Chen, H.; [Whitt, W.](/wiki/Ward_Whitt "Ward Whitt") (1993). "Diffusion approximations for open queueing networks with service interruptions". *[Queueing Systems](/wiki/Queueing_Systems "Queueing Systems")*. **13** (4): 335. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1007/BF01149260](https://doi.org/10.1007%2FBF01149260). [S2CID](/wiki/S2CID_(identifier) "S2CID (identifier)") [1180930](https://api.semanticscholar.org/CorpusID:1180930).
41. **[^](#cite_ref-41)** Yamada, K. (1995). ["Diffusion Approximation for Open State-Dependent Queueing Networks in the Heavy Traffic Situation"](https://doi.org/10.1214%2Faoap%2F1177004602). *The Annals of Applied Probability*. **5** (4): 958–982. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1214/aoap/1177004602](https://doi.org/10.1214%2Faoap%2F1177004602). [JSTOR](/wiki/JSTOR_(identifier) "JSTOR (identifier)") [2245101](https://www.jstor.org/stable/2245101).
42. **[^](#cite_ref-42)** Bramson, M. (1999). ["A stable queueing network with unstable fluid model"](https://doi.org/10.1214%2Faoap%2F1029962815). *The Annals of Applied Probability*. **9** (3): 818–853. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1214/aoap/1029962815](https://doi.org/10.1214%2Faoap%2F1029962815). [JSTOR](/wiki/JSTOR_(identifier) "JSTOR (identifier)") [2667284](https://www.jstor.org/stable/2667284).
43. **[^](#cite_ref-43)** Gross, D., & Harris, C. M. (1998). *Fundamentals of Queueing Theory*. John Wiley & Sons.
44. **[^](#cite_ref-44)** Kleinrock, L. (1976). *Queueing Systems: Volume I - Theory*. Wiley.
45. **[^](#cite_ref-45)** Cooper, B. F., & Mitrani, I. (1985). *Queueing Networks: A Fundamental Approach*. John Wiley & Sons.

## Further reading

[[edit](/w/index.php?title=Queueing_theory&veaction=edit&section=18 "Edit section: Further reading") | [edit source](/w/index.php?title=Queueing_theory&action=edit&section=18 "Edit section's source code: Further reading")]

- Gross, Donald; Carl M. Harris (1998). *Fundamentals of Queueing Theory*. Wiley. [ISBN](/wiki/ISBN_(identifier) "ISBN (identifier)") [978-0-471-32812-4](/wiki/Special:BookSources/978-0-471-32812-4 "Special:BookSources/978-0-471-32812-4"). [Online](https://books.google.com/books?id=K3lQGeCtAJgC)
- Zukerman, Moshe (2013). [*Introduction to Queueing Theory and Stochastic Teletraffic Models*](http://www.ee.cityu.edu.hk/~zukerman/classnotes.pdf) (PDF). [arXiv](/wiki/ArXiv_(identifier) "ArXiv (identifier)"):[1307.2968](https://arxiv.org/abs/1307.2968).
- Deitel, Harvey M. (1984) [1982]. [*An introduction to operating systems*](https://archive.org/details/introductiontoopdeit00deit/page/673) (revisited first ed.). Addison-Wesley. p. [673](https://archive.org/details/introductiontoopdeit00deit/page/673). [ISBN](/wiki/ISBN_(identifier) "ISBN (identifier)") [978-0-201-14502-1](/wiki/Special:BookSources/978-0-201-14502-1 "Special:BookSources/978-0-201-14502-1"). chap.15, pp. 380–412
- Gelenbe, Erol; Isi Mitrani (2010). [*Analysis and Synthesis of Computer Systems*](https://www.researchgate.net/publication/345903225). World Scientific 2nd Edition. [ISBN](/wiki/ISBN_(identifier) "ISBN (identifier)") [978-1-908978-42-4](/wiki/Special:BookSources/978-1-908978-42-4 "Special:BookSources/978-1-908978-42-4").
- Newell, Gordron F. (1 June 1971). *Applications of Queueing Theory*. Chapman and Hall.
- Leonard Kleinrock, [Information Flow in Large Communication Nets](http://www.lk.cs.ucla.edu/bibliography-public_reports.html), (MIT, Cambridge, May 31, 1961) Proposal for a Ph.D. Thesis
- Leonard Kleinrock. *Information Flow in Large Communication Nets* (RLE Quarterly Progress Report, July 1961)
- Leonard Kleinrock. *Communication Nets: Stochastic Message Flow and Delay* (McGraw-Hill, New York, 1964)
- [Kleinrock, Leonard](/wiki/Leonard_Kleinrock "Leonard Kleinrock") (2 January 1975). [*Queueing Systems: Volume I – Theory*](https://archive.org/details/queueingsystems02klei). New York: Wiley Interscience. pp. [417](https://archive.org/details/queueingsystems02klei/page/417). [ISBN](/wiki/ISBN_(identifier) "ISBN (identifier)") [978-0-471-49110-1](/wiki/Special:BookSources/978-0-471-49110-1 "Special:BookSources/978-0-471-49110-1").
- [Kleinrock, Leonard](/wiki/Leonard_Kleinrock "Leonard Kleinrock") (22 April 1976). [*Queueing Systems: Volume II – Computer Applications*](https://archive.org/details/queueingsystems00klei/page/576). New York: Wiley Interscience. pp. [576](https://archive.org/details/queueingsystems00klei/page/576). [ISBN](/wiki/ISBN_(identifier) "ISBN (identifier)") [978-0-471-49111-8](/wiki/Special:BookSources/978-0-471-49111-8 "Special:BookSources/978-0-471-49111-8").
- Lazowska, Edward D.; John Zahorjan; G. Scott Graham; Kenneth C. Sevcik (1984). [*Quantitative System Performance: Computer System Analysis Using Queueing Network Models*](https://archive.org/details/quantitativesyst00lazo). Prentice-Hall, Inc. [ISBN](/wiki/ISBN_(identifier) "ISBN (identifier)") [978-0-13-746975-8](/wiki/Special:BookSources/978-0-13-746975-8 "Special:BookSources/978-0-13-746975-8").
- Jon Kleinberg; Éva Tardos (30 June 2013). [*Algorithm Design*](https://books.google.com/books?id=ROiUngEACAAJ). Pearson. [ISBN](/wiki/ISBN_(identifier) "ISBN (identifier)") [978-1-292-02394-6](/wiki/Special:BookSources/978-1-292-02394-6 "Special:BookSources/978-1-292-02394-6").

## External links

[[edit](/w/index.php?title=Queueing_theory&veaction=edit&section=19 "Edit section: External links") | [edit source](/w/index.php?title=Queueing_theory&action=edit&section=19 "Edit section's source code: External links")]

.mw-parser-output .side-box{margin:4px 0;box-sizing:border-box;border:1px solid var(--border-color-base,#a2a9b1);font-size:88%;line-height:1.25em;background-color:var(--background-color-interactive-subtle,#f8f9fa);color:inherit;display:flow-root}.mw-parser-output .infobox .side-box{font-size:100%}.mw-parser-output .side-box-abovebelow,.mw-parser-output .side-box-text{padding:0.25em 0.9em}.mw-parser-output .side-box-image{padding:2px 0 2px 0.9em;text-align:center}.mw-parser-output .side-box-imageright{padding:2px 0.9em 2px 0;text-align:center}@media(min-width:500px){.mw-parser-output .side-box-flex{display:flex;align-items:center}.mw-parser-output .side-box-text{flex:1;min-width:0}}@media(min-width:640px){.mw-parser-output .side-box{width:238px}.mw-parser-output .side-box-right{clear:right;float:right;margin-left:1em}.mw-parser-output .side-box-left{margin-right:1em}}@media print{body.ns-0 .mw-parser-output .sistersitebox{display:none!important}}@media screen{html.skin-theme-clientpref-night .mw-parser-output .sistersitebox img[src\*="Wiktionary-logo-en-v2.svg"]{filter:invert(1)brightness(55%)contrast(250%)hue-rotate(180deg)}}@media screen and (prefers-color-scheme:dark){html.skin-theme-clientpref-os .mw-parser-output .sistersitebox img[src\*="Wiktionary-logo-en-v2.svg"]{filter:invert(1)brightness(55%)contrast(250%)hue-rotate(180deg)}}

.mw-parser-output .plainlist ol,.mw-parser-output .plainlist ul{line-height:inherit;list-style:none;margin:0;padding:0}.mw-parser-output .plainlist ol li,.mw-parser-output .plainlist ul li{margin-bottom:0}

[![Wiktionary logo](//thumb.wikimedia.org/wikipedia/commons/thumb/9/99/Wiktionary-logo-en-v2.svg/40px-Wiktionary-logo-en-v2.svg.png?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail)](/wiki/File:Wiktionary-logo-en-v2.svg)

Look up ***[queueing](https://en.wiktionary.org/wiki/queueing "wiktionary:queueing")*** or ***[queuing](https://en.wiktionary.org/wiki/queuing "wiktionary:queuing")*** in Wiktionary, the free dictionary.

- [Teknomo's Queueing theory tutorial and calculators](http://people.revoledu.com/kardi/tutorial/Queuing/index.html)
- [Virtamo's Queueing Theory Course](http://www.netlab.tkk.fi/opetus/s383143/kalvot/english.shtml)
- [Myron Hlynka's Queueing Theory Page](http://web2.uwindsor.ca/math/hlynka/queue.html)
- [LINE: a general-purpose engine to solve queueing models](http://line-solver.sf.net)

.mw-parser-output .hlist dl,.mw-parser-output .hlist ol,.mw-parser-output .hlist ul{margin:0;padding:0}.mw-parser-output .hlist dd,.mw-parser-output .hlist dt,.mw-parser-output .hlist li{margin:0;display:inline}.mw-parser-output .hlist.inline,.mw-parser-output .hlist.inline dl,.mw-parser-output .hlist.inline ol,.mw-parser-output .hlist.inline ul,.mw-parser-output .hlist dl dl,.mw-parser-output .hlist dl ol,.mw-parser-output .hlist dl ul,.mw-parser-output .hlist ol dl,.mw-parser-output .hlist ol ol,.mw-parser-output .hlist ol ul,.mw-parser-output .hlist ul dl,.mw-parser-output .hlist ul ol,.mw-parser-output .hlist ul ul{display:inline}.mw-parser-output .hlist .mw-empty-li{display:none}.mw-parser-output .hlist dt::after{content:": "}.mw-parser-output .hlist dd::after,.mw-parser-output .hlist li::after{content:"\a0 · ";font-weight:bold}.mw-parser-output .hlist dd:last-child::after,.mw-parser-output .hlist dt:last-child::after,.mw-parser-output .hlist li:last-child::after{content:none}.mw-parser-output .hlist dd dd:first-child::before,.mw-parser-output .hlist dd dt:first-child::before,.mw-parser-output .hlist dd li:first-child::before,.mw-parser-output .hlist dt dd:first-child::before,.mw-parser-output .hlist dt dt:first-child::before,.mw-parser-output .hlist dt li:first-child::before,.mw-parser-output .hlist li dd:first-child::before,.mw-parser-output .hlist li dt:first-child::before,.mw-parser-output .hlist li li:first-child::before{content:" (";font-weight:normal}.mw-parser-output .hlist dd dd:last-child::after,.mw-parser-output .hlist dd dt:last-child::after,.mw-parser-output .hlist dd li:last-child::after,.mw-parser-output .hlist dt dd:last-child::after,.mw-parser-output .hlist dt dt:last-child::after,.mw-parser-output .hlist dt li:last-child::after,.mw-parser-output .hlist li dd:last-child::after,.mw-parser-output .hlist li dt:last-child::after,.mw-parser-output .hlist li li:last-child::after{content:")";font-weight:normal}.mw-parser-output .hlist ol{counter-reset:listitem}.mw-parser-output .hlist ol>li{counter-increment:listitem}.mw-parser-output .hlist ol>li::before{content:" "counter(listitem)"\a0 "}.mw-parser-output .hlist dd ol>li:first-child::before,.mw-parser-output .hlist dt ol>li:first-child::before,.mw-parser-output .hlist li ol>li:first-child::before{content:" ("counter(listitem)"\a0 "}.mw-parser-output .navbox{box-sizing:border-box;border:1px solid #a2a9b1;width:100%;clear:both;font-size:88%;text-align:center;padding:1px;margin:1em auto 0}.mw-parser-output .navbox .navbox{margin-top:0}.mw-parser-output .navbox+.navbox-styles+.navbox,.mw-parser-output .navbox+span.mw-empty-elt+.navbox-styles+.navbox{margin-top:-1px}.mw-parser-output .navbox-inner,.mw-parser-output .navbox-subgroup{width:100%}.mw-parser-output .navbox-group,.mw-parser-output .navbox-title,.mw-parser-output .navbox-abovebelow{padding:0.25em 1em;line-height:1.5em;text-align:center}.mw-parser-output .navbox-group{white-space:nowrap;text-align:right}.mw-parser-output .navbox,.mw-parser-output .navbox-subgroup{background-color:#fdfdfd;color:inherit}.mw-parser-output .navbox-list{line-height:1.5em;border-color:#fdfdfd}.mw-parser-output .navbox-list-with-group{text-align:left;border-left-width:2px;border-left-style:solid}.mw-parser-output tr+tr>.navbox-abovebelow,.mw-parser-output tr+tr>.navbox-group,.mw-parser-output tr+tr>.navbox-image,.mw-parser-output tr+tr>.navbox-list{border-top:2px solid #fdfdfd}.mw-parser-output .navbox-title{background-color:#ccf;color:inherit}.mw-parser-output .navbox-abovebelow,.mw-parser-output .navbox-group,.mw-parser-output .navbox-subgroup .navbox-title{background-color:#ddf;color:inherit}.mw-parser-output .navbox-subgroup .navbox-group,.mw-parser-output .navbox-subgroup .navbox-abovebelow{background-color:#e6e6ff;color:inherit}.mw-parser-output .navbox-even{background-color:#f7f7f7;color:inherit}.mw-parser-output .navbox-odd{background-color:transparent;color:inherit}.mw-parser-output .navbox .hlist td dl,.mw-parser-output .navbox .hlist td ol,.mw-parser-output .navbox .hlist td ul,.mw-parser-output .navbox td.hlist dl,.mw-parser-output .navbox td.hlist ol,.mw-parser-output .navbox td.hlist ul{padding:0.125em 0}.mw-parser-output .navbox .navbar{display:block;font-size:100%}.mw-parser-output .navbox-title .navbar{float:left;text-align:left;margin-right:0.5em}body.skin--responsive .mw-parser-output .navbox-image img{max-width:none!important}@media print{body.ns-0 .mw-parser-output .navbox{display:none!important}}

| .mw-parser-output .navbar{display:inline;font-size:88%;font-weight:normal}.mw-parser-output .navbar-collapse{float:left;text-align:left}.mw-parser-output .navbar-boxtext{word-spacing:0}.mw-parser-output .navbar ul{display:inline-block;white-space:nowrap;line-height:inherit}.mw-parser-output .navbar-brackets::before{margin-right:-0.125em;content:"[ "}.mw-parser-output .navbar-brackets::after{margin-left:-0.125em;content:" ]"}.mw-parser-output .navbar li{word-spacing:-0.125em}.mw-parser-output .navbar a>span,.mw-parser-output .navbar a>abbr{text-decoration:inherit}.mw-parser-output .navbar-mini abbr{font-variant:small-caps;border-bottom:none;text-decoration:none;cursor:inherit}.mw-parser-output .navbar-ct-full{font-size:114%;margin:0 7em}.mw-parser-output .navbar-ct-mini{font-size:114%;margin:0 4em}html.skin-theme-clientpref-night .mw-parser-output .navbar li a abbr{color:var(--color-base)!important}@media(prefers-color-scheme:dark){html.skin-theme-clientpref-os .mw-parser-output .navbar li a abbr{color:var(--color-base)!important}}@media print{.mw-parser-output .navbar{display:none!important}} - [v](/wiki/Template:Queueing_theory "Template:Queueing theory") - [t](/wiki/Template_talk:Queueing_theory "Template talk:Queueing theory") - [e](/wiki/Special:EditPage/Template:Queueing_theory "Special:EditPage/Template:Queueing theory")  Queueing theory | |
| --- | --- |
| Single queueing nodes | - [D/M/1 queue](/wiki/D/M/1_queue "D/M/1 queue") - [M/D/1 queue](/wiki/M/D/1_queue "M/D/1 queue") - [M/D/c queue](/wiki/M/D/c_queue "M/D/c queue") - [M/M/1 queue](/wiki/M/M/1_queue "M/M/1 queue")   - [Burke's theorem](/wiki/Burke%27s_theorem "Burke's theorem") - [M/M/c queue](/wiki/M/M/c_queue "M/M/c queue") - [M/M/∞ queue](/wiki/M/M/%E2%88%9E_queue "M/M/∞ queue") - [M/G/1 queue](/wiki/M/G/1_queue "M/G/1 queue")   - [Pollaczek–Khinchine formula](/wiki/Pollaczek%E2%80%93Khinchine_formula "Pollaczek–Khinchine formula")   - [Matrix analytic method](/wiki/Matrix_analytic_method "Matrix analytic method") - [M/G/k queue](/wiki/M/G/k_queue "M/G/k queue") - [G/M/1 queue](/wiki/G/M/1_queue "G/M/1 queue") - [G/G/1 queue](/wiki/G/G/1_queue "G/G/1 queue")   - [Kingman's formula](/wiki/Kingman%27s_formula "Kingman's formula")   - [Lindley equation](/wiki/Lindley_equation "Lindley equation") - [Fork–join queue](/wiki/Fork%E2%80%93join_queue "Fork–join queue") - [Bulk queue](/wiki/Bulk_queue "Bulk queue") |
| Arrival processes | - [Poisson point process](/wiki/Poisson_point_process "Poisson point process") - [Markovian arrival process](/wiki/Markovian_arrival_process "Markovian arrival process") - [Rational arrival process](/wiki/Rational_arrival_process "Rational arrival process") |
| Queueing networks | - [Jackson network](/wiki/Jackson_network "Jackson network")   - [Traffic equations](/wiki/Traffic_equations "Traffic equations") - [Gordon–Newell theorem](/wiki/Gordon%E2%80%93Newell_theorem "Gordon–Newell theorem")   - [Mean value analysis](/wiki/Mean_value_analysis "Mean value analysis")   - [Buzen's algorithm](/wiki/Buzen%27s_algorithm "Buzen's algorithm") - [Kelly network](/wiki/Kelly_network "Kelly network") - [G-network](/wiki/G-network "G-network") - [BCMP network](/wiki/BCMP_network "BCMP network") |
| Service policies | - [FIFO](/wiki/FIFO_(computing_and_electronics) "FIFO (computing and electronics)") - [LIFO](/wiki/LIFO_(computing) "LIFO (computing)") - [Processor sharing](/wiki/Processor_sharing "Processor sharing") - [Round-robin](/wiki/Round-robin_scheduling "Round-robin scheduling") - [Shortest job next](/wiki/Shortest_job_next "Shortest job next") - [Shortest remaining time](/wiki/Shortest_remaining_time "Shortest remaining time") |
| Key concepts | - [Continuous-time Markov chain](/wiki/Continuous-time_Markov_chain "Continuous-time Markov chain") - [Kendall's notation](/wiki/Kendall%27s_notation "Kendall's notation") - [Little's law](/wiki/Little%27s_law "Little's law") - [Product-form solution](/wiki/Product-form_solution "Product-form solution")   - [Balance equation](/wiki/Balance_equation "Balance equation")   - [Quasireversibility](/wiki/Quasireversibility "Quasireversibility")   - [Flow-equivalent server method](/wiki/Flow-equivalent_server_method "Flow-equivalent server method") - [Arrival theorem](/wiki/Arrival_theorem "Arrival theorem") - [Decomposition method](/wiki/Decomposition_method_(queueing_theory) "Decomposition method (queueing theory)") - [Beneš method](/wiki/Bene%C5%A1_method "Beneš method") |
| Limit theorems | - [Fluid limit](/wiki/Fluid_limit "Fluid limit") - [Mean-field theory](/wiki/Mean-field_theory "Mean-field theory") - [Heavy traffic approximation](/wiki/Heavy_traffic_approximation "Heavy traffic approximation")   - [Reflected Brownian motion](/wiki/Reflected_Brownian_motion "Reflected Brownian motion") |
| Extensions | - [Fluid queue](/wiki/Fluid_queue "Fluid queue") - [Layered queueing network](/wiki/Layered_queueing_network "Layered queueing network") - [Polling system](/wiki/Polling_system "Polling system") - [Adversarial queueing network](/wiki/Adversarial_queueing_network "Adversarial queueing network") - [Loss network](/wiki/Loss_network "Loss network") - [Retrial queue](/wiki/Retrial_queue "Retrial queue") |
| [Information systems](/wiki/Information_system "Information system") | - [Data buffer](/wiki/Data_buffer "Data buffer") - [Erlang (unit)](/wiki/Erlang_(unit) "Erlang (unit)") - [Erlang distribution](/wiki/Erlang_distribution "Erlang distribution") - [Flow control (data)](/wiki/Flow_control_(data) "Flow control (data)") - [Message queue](/wiki/Message_queue "Message queue") - [Network congestion](/wiki/Network_congestion "Network congestion") - [Network scheduler](/wiki/Network_scheduler "Network scheduler") - [Pipeline (software)](/wiki/Pipeline_(software) "Pipeline (software)") - [Quality of service](/wiki/Quality_of_service "Quality of service") - [Scheduling (computing)](/wiki/Scheduling_(computing) "Scheduling (computing)") - [Teletraffic engineering](/wiki/Teletraffic_engineering "Teletraffic engineering") |
| [Category](/wiki/Category:Queueing_theory "Category:Queueing theory") | |

.mw-parser-output .tooltip-dotted{border-bottom:1px dotted;cursor:help}

| [Authority control databases](/wiki/Help:Authority_control "Help:Authority control") [Edit this at Wikidata](https://www.wikidata.org/wiki/Q847526#identifiers "Edit this at Wikidata") | |
| --- | --- |
| International | - [GND](https://d-nb.info/gnd/4255044-0) - [FAST](https://id.worldcat.org/fast/1085713) |
| National | - [United States](https://id.loc.gov/authorities/sh85109832) - [France](https://catalogue.bnf.fr/ark:/12148/cb12647707b) - [BnF data](https://data.bnf.fr/ark:/12148/cb12647707b) - [Japan](https://id.ndl.go.jp/auth/ndlna/00567524) - [Czech Republic](https://aleph.nkp.cz/F/?func=find-c&local_base=aut&ccl_term=ica=ph276803&CON_LNG=ENG) - [Israel](https://www.nli.org.il/en/authorities/987007553435905171) |
| Other | - [Yale LUX](https://lux.collections.yale.edu/view/concept/9814a1d3-512e-4f2e-961c-e9089be0adda) |
