<!-- category: production_scheduling -->
# Job shop scheduling

Optimization problem

**Job-shop scheduling**, **the job-shop problem** (**JSP**) or **job-shop scheduling problem** (**JSSP**) is an [optimization problem](/wiki/Optimization_problem "Optimization problem") in [computer science](/wiki/Computer_science "Computer science") and [operations research](/wiki/Operations_Research "Operations Research"). It is a variant of [optimal job scheduling](/wiki/Optimal_job_scheduling "Optimal job scheduling"). In a general job scheduling problem, we are given *n* jobs *J*1, *J*2, ..., *Jn* of varying processing times, which need to be scheduled on *m* machines with varying processing power, while trying to minimize the [makespan](/wiki/Makespan "Makespan") – the total length of the schedule (that is, when all the jobs have finished processing). In the specific variant known as *job-shop scheduling*, each job consists of a set of *operations* *O*1, *O*2, ..., *On* which need to be processed in a specific order (known as *precedence constraints*). Each operation has a *specific machine* that it needs to be processed on and only one operation in a job can be processed at a given time. A common relaxation is the **flexible** job shop, where each operation can be processed on any machine of a given *set* (the machines in each set are identical).

The name originally came from the scheduling of jobs in a [job shop](/wiki/Job_shop "Job shop"), but the theme has wide applications beyond that type of instance. It is a well-known [combinatorial optimization](/wiki/Combinatorial_optimization "Combinatorial optimization") problem and was the first to undergo [competitive analysis](/wiki/Competitive_analysis_(online_algorithm) "Competitive analysis (online algorithm)"), introduced by Graham in 1966.[[1]](#cite_note-graham1966-1) The best problem instances for a basic model with a makespan objective are due to Taillard.[[2]](#cite_note-TaillardIns-2)

In the standard [three-field notation for optimal job scheduling problems](/wiki/Optimal_job_scheduling "Optimal job scheduling"), the job-shop variant is denoted by *J* in the first field. For example, the problem denoted by "

J

3

|

p

i
j

|

C

max
{\displaystyle J\_{3}|p\_{ij}|C\_{\max }}
![{\displaystyle J_{3}|p_{ij}|C_{\max }}](https://wikimedia.org/api/rest_v1/media/math/render/svg/824c21706f76fda5838feeb159d55f4e82d2a384)" is a 3-machines job-shop problem with unit processing times, where the goal is to minimize the maximum completion time.

## Problem variations

[[edit](/w/index.php?title=Job-shop_scheduling&veaction=edit&section=1 "Edit section: Problem variations") | [edit source](/w/index.php?title=Job-shop_scheduling&action=edit&section=1 "Edit section's source code: Problem variations")]

Many variations of the problem exist, including the following:

- Machines can have duplicates (flexible job shop with duplicate machines) or belong to groups of identical machines (flexible job shop).[[3]](#cite_note-3)
- Machines can require a certain gap between jobs or no idle-time.
- Machines can have sequence-dependent setups.
- [Objective function](/wiki/Objective_function "Objective function") can be to minimize the makespan, the [*Lp*](/wiki/Lp_space "Lp space") norm, tardiness, maximum lateness etc. It can also be multi-objective optimization problem.
- Certain jobs must be completed before others can start (see [workflow](/wiki/Workflow "Workflow")), and objectives may involve multiple-criteria.[[4]](#cite_note-4)
- Set of jobs can relate to different set of machines.
- Deterministic (fixed) processing times or probabilistic processing times.

## NP-hardness

[[edit](/w/index.php?title=Job-shop_scheduling&veaction=edit&section=2 "Edit section: NP-hardness") | [edit source](/w/index.php?title=Job-shop_scheduling&action=edit&section=2 "Edit section's source code: NP-hardness")]

Since the [traveling salesman problem](/wiki/Traveling_salesman_problem "Traveling salesman problem") is [NP-hard](/wiki/NP-hard "NP-hard"), the job-shop problem with [sequence-dependent setup](/w/index.php?title=Sequence-dependent_setup&action=edit&redlink=1 "Sequence-dependent setup (page does not exist)") is also NP-hard since the TSP is a special case of the JSP with a single job (the salesman in TSP) and the machines (the cities in TSP).[[5]](#cite_note-5)

## Problem representation

[[edit](/w/index.php?title=Job-shop_scheduling&veaction=edit&section=3 "Edit section: Problem representation") | [edit source](/w/index.php?title=Job-shop_scheduling&action=edit&section=3 "Edit section's source code: Problem representation")]

The [disjunctive graph](/wiki/Disjunctive_graph "Disjunctive graph")[[6]](#cite_note-6) is one of the popular models used for describing the job-shop scheduling problem instances.[[7]](#cite_note-7)

A mathematical statement of the problem can be made as follows:

Let 

M
=
{

M

1
,

M

2
,
…
,

M

m
}
{\displaystyle M=\{M\_{1},M\_{2},\dots ,M\_{m}\}}
![{\displaystyle M=\{M_{1},M_{2},\dots ,M_{m}\}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/adf5dd0349b4c0de053c0d2014180c9b1505635c) and 

J
=
{

J

1
,

J

2
,
…
,

J

n
}
{\displaystyle J=\{J\_{1},J\_{2},\dots ,J\_{n}\}}
![{\displaystyle J=\{J_{1},J_{2},\dots ,J_{n}\}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/b0451a8e5ea43c915e120a4be7f1c93f1a47dfd3) be two [finite](/wiki/Finite_set "Finite set") [sets](/wiki/Set_(mathematics) "Set (mathematics)"). On account of the industrial origins of the problem, the 

M

i
{\displaystyle \displaystyle M\_{i}}
![{\displaystyle \displaystyle M_{i}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/0618e61f02dda21572392fe5bb3aef1688939bc3) are called **machines** and the 

J

j
{\displaystyle \displaystyle J\_{j}}
![{\displaystyle \displaystyle J_{j}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/be0fa976f1b2ef06ceb67202feb1cba1d04fadfa) are called **jobs**.

Let 

 

X
{\displaystyle \displaystyle \ {\mathcal {X}}}
![{\displaystyle \displaystyle \ {\mathcal {X}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/5c1721ed7ced9d150621aad985c0c96820b9513f) denote the set of all sequential assignments of jobs to machines, such that every job is done by every machine exactly once; elements 

x
∈

X
{\displaystyle x\in {\mathcal {X}}}
![{\displaystyle x\in {\mathcal {X}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/0b3cd596d560b9f3bc71615911c2438cbbf49c15) may be written as 

n
×
m
{\displaystyle n\times m}
![{\displaystyle n\times m}](https://wikimedia.org/api/rest_v1/media/math/render/svg/d82325a2a02ad79bc7c347ba9702ad46eb0de824) matrices, in which column 

i
{\displaystyle \displaystyle i}
![{\displaystyle \displaystyle i}](https://wikimedia.org/api/rest_v1/media/math/render/svg/aef5149af5f66188f9eff0977e500b44ce509c0c) lists the jobs that machine 

M

i
{\displaystyle \displaystyle M\_{i}}
![{\displaystyle \displaystyle M_{i}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/0618e61f02dda21572392fe5bb3aef1688939bc3) will do, in order. For example, the matrix

:   x
    =

    (

    1

    2

    2

    3

    3

    1
    )
    {\displaystyle x={\begin{pmatrix}1&2\\2&3\\3&1\end{pmatrix}}}
    ![{\displaystyle x={\begin{pmatrix}1&2\\2&3\\3&1\end{pmatrix}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/409eb3d72c50472a67cf12b22e459736e6621426)

means that machine 

M

1
{\displaystyle \displaystyle M\_{1}}
![{\displaystyle \displaystyle M_{1}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/9cfc49197068ee86210dbcff9cad025014ccd487) will do the three jobs 

J

1
,

J

2
,

J

3
{\displaystyle \displaystyle J\_{1},J\_{2},J\_{3}}
![{\displaystyle \displaystyle J_{1},J_{2},J_{3}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/ddf109d6016bf2e9035aa8a7624e015a3d2142f0) in the order 

J

1
,

J

2
,

J

3
{\displaystyle \displaystyle J\_{1},J\_{2},J\_{3}}
![{\displaystyle \displaystyle J_{1},J_{2},J_{3}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/ddf109d6016bf2e9035aa8a7624e015a3d2142f0), while machine 

M

2
{\displaystyle \displaystyle M\_{2}}
![{\displaystyle \displaystyle M_{2}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/5ea61fd4629d5986fe6afe6670f6a554567d0f50) will do the jobs in the order 

J

2
,

J

3
,

J

1
{\displaystyle \displaystyle J\_{2},J\_{3},J\_{1}}
![{\displaystyle \displaystyle J_{2},J_{3},J_{1}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/440105d383cfb4054b4595799ad7985bd36f09cc).

Suppose also that there is some **cost function** 

C
:

X
→
[
0
,
+
∞
]
{\displaystyle C:{\mathcal {X}}\to [0,+\infty ]}
![{\displaystyle C:{\mathcal {X}}\to [0,+\infty ]}](https://wikimedia.org/api/rest_v1/media/math/render/svg/7b12140e27b2f84b275db6cda5a988176f88e391). The cost function may be interpreted as a "total processing time", and may have some expression in terms of times 

C

i
j
:
M
×
J
→
[
0
,
+
∞
]
{\displaystyle C\_{ij}:M\times J\to [0,+\infty ]}
![{\displaystyle C_{ij}:M\times J\to [0,+\infty ]}](https://wikimedia.org/api/rest_v1/media/math/render/svg/40bf2488b7f615e906a50d5beb545594110c2d19), the cost/time for machine 

M

i
{\displaystyle \displaystyle M\_{i}}
![{\displaystyle \displaystyle M_{i}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/0618e61f02dda21572392fe5bb3aef1688939bc3) to do job 

J

j
{\displaystyle \displaystyle J\_{j}}
![{\displaystyle \displaystyle J_{j}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/be0fa976f1b2ef06ceb67202feb1cba1d04fadfa).

The **job-shop problem** is to find an assignment of jobs 

x
∈

X
{\displaystyle x\in {\mathcal {X}}}
![{\displaystyle x\in {\mathcal {X}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/0b3cd596d560b9f3bc71615911c2438cbbf49c15) such that 

C
(
x
)
{\displaystyle \displaystyle C(x)}
![{\displaystyle \displaystyle C(x)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/fec91857bc9b763d321b39dab8c711fa3054b188) is a minimum, that is, there is no 

y
∈

X
{\displaystyle y\in {\mathcal {X}}}
![{\displaystyle y\in {\mathcal {X}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/3454688293d32142aa5a436e436f81e23d146d4b) such that 

C
(
x
)
>
C
(
y
)
{\displaystyle \displaystyle C(x)>C(y)}
![{\displaystyle \displaystyle C(x)>C(y)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/8a997b981b45d4729f605dd8800aa238460b6466).

## Scheduling efficiency

[[edit](/w/index.php?title=Job-shop_scheduling&veaction=edit&section=4 "Edit section: Scheduling efficiency") | [edit source](/w/index.php?title=Job-shop_scheduling&action=edit&section=4 "Edit section's source code: Scheduling efficiency")]

Scheduling efficiency can be defined for a schedule through the ratio of total machine idle time to the total processing time as below:

C
′
=
1
+

∑

i

l

i

∑

j
,
k

p

j
k
=

C
.
m

∑

j
,
k

p

j
k
{\displaystyle C'=1+{\sum \_{i}l\_{i} \over \sum \_{j,k}p\_{jk}}={C.m \over \sum \_{j,k}p\_{jk}}}
![{\displaystyle C'=1+{\sum _{i}l_{i} \over \sum _{j,k}p_{jk}}={C.m \over \sum _{j,k}p_{jk}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/7d2702982ff3f579a6299ff27d1132d36bc96a1a)

Where 

l

i
{\displaystyle l\_{i}}
![{\displaystyle l_{i}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/48ba35055d00bcaa522bca9247c8857730998759) represents the idle time of machine i, C is the makespan, and m is the number of machines. This formulation normalizes the makespan by the number of machines and total processing time, allowing for the comparison of resource utilization across job-shop scheduling (JSP) instances of varying sizes.[[8]](#cite_note-:0-8)

## The problem of infinite cost

[[edit](/w/index.php?title=Job-shop_scheduling&veaction=edit&section=5 "Edit section: The problem of infinite cost") | [edit source](/w/index.php?title=Job-shop_scheduling&action=edit&section=5 "Edit section's source code: The problem of infinite cost")]

One of the first problems that must be dealt with in the JSP is that many proposed solutions have infinite cost: i.e., there exists 

x

∞
∈

X
{\displaystyle x\_{\infty }\in {\mathcal {X}}}
![{\displaystyle x_{\infty }\in {\mathcal {X}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/d0652deb7b5b78aecb8c7ae608c883146557a61d) such that 

C
(

x

∞
)
=
+
∞
{\displaystyle C(x\_{\infty })=+\infty }
![{\displaystyle C(x_{\infty })=+\infty }](https://wikimedia.org/api/rest_v1/media/math/render/svg/a6aeb96df6e169d58a43122ca90ded826c2ae889). In fact, it is quite simple to concoct examples of such 

x

∞
{\displaystyle x\_{\infty }}
![{\displaystyle x_{\infty }}](https://wikimedia.org/api/rest_v1/media/math/render/svg/d0941cb6e94cc76978032ede275b912849590ab6) by ensuring that two machines will [deadlock](/wiki/Deadlock_(computer_science) "Deadlock (computer science)"), so that each waits for the output of the other's next step.

## Major results

[[edit](/w/index.php?title=Job-shop_scheduling&veaction=edit&section=6 "Edit section: Major results") | [edit source](/w/index.php?title=Job-shop_scheduling&action=edit&section=6 "Edit section's source code: Major results")]

Graham introduced the List scheduling algorithm in 1966, which is (2 − 1/m)-competitive, where *m* is the number of machines.[[1]](#cite_note-graham1966-1) It was later proven to be the optimal online algorithm for two and three machines. The [Coffman–Graham algorithm](/wiki/Coffman%E2%80%93Graham_algorithm "Coffman–Graham algorithm") (1972) for uniform-length jobs is also optimal for two machines and (2 − 2/m)-competitive.[[9]](#cite_note-9)[[10]](#cite_note-10)

In 1992, Bartal, Fiat, Karloff, and Vohra presented a 1.986-competitive algorithm,[[11]](#cite_note-11) followed by a 1.945-competitive algorithm by Karger, Philips, and Torng in 1994.[[12]](#cite_note-12) That same year, Albers introduced a different 1.923-competitive algorithm.[[13]](#cite_note-13) The best known result is by Fleischer and Wahl, achieving a 1.9201 competitive ratio.[[14]](#cite_note-14)

Albers also established a lower bound of 1.852.[[15]](#cite_note-15) Taillard instances play a key role in developing job-shop scheduling with a makespan objective.

In 1976, Garey proved that this problem is [NP-complete](/wiki/NP-complete "NP-complete") for *m* > 2, meaning no optimal solution can be computed in polynomial time unless [P=NP](/wiki/P%3DNP "P=NP").[[16]](#cite_note-garey1976-16)

In 2011, Xin Chen et al. provided optimal algorithms for online scheduling on two related machines, improving previous results.[[17]](#cite_note-17)[[18]](#cite_note-18)

## Offline makespan minimization

[[edit](/w/index.php?title=Job-shop_scheduling&veaction=edit&section=7 "Edit section: Offline makespan minimization") | [edit source](/w/index.php?title=Job-shop_scheduling&action=edit&section=7 "Edit section's source code: Offline makespan minimization")]

### Atomic jobs

[[edit](/w/index.php?title=Job-shop_scheduling&veaction=edit&section=8 "Edit section: Atomic jobs") | [edit source](/w/index.php?title=Job-shop_scheduling&action=edit&section=8 "Edit section's source code: Atomic jobs")]

.mw-parser-output .hatnote{font-style:italic}.mw-parser-output div.hatnote{padding-left:1.6em;margin-bottom:0.5em}.mw-parser-output .hatnote i{font-style:normal}.mw-parser-output .hatnote+.mw-empty-elt+.hatnote{margin-top:-0.5em}@media print{body.ns-0 .mw-parser-output .hatnote{display:none!important}}

See also: [Multiprocessor scheduling](/wiki/Multiprocessor_scheduling "Multiprocessor scheduling")

The simplest form of the offline makespan minimisation problem deals with atomic jobs, that is, jobs that are not subdivided into multiple operations. It is equivalent to packing a number of items of various different sizes into a fixed number of bins, such that the maximum bin size needed is as small as possible. (If instead the number of bins is to be minimised, and the bin size is fixed, the problem becomes a different problem, known as the [bin packing problem](/wiki/Bin_packing_problem "Bin packing problem").)

[Dorit S. Hochbaum](/wiki/Dorit_S._Hochbaum "Dorit S. Hochbaum") and [David Shmoys](/wiki/David_Shmoys "David Shmoys") presented a [polynomial-time approximation scheme](/wiki/Polynomial-time_approximation_scheme "Polynomial-time approximation scheme") in 1987 that finds an approximate solution to the offline makespan minimisation problem with atomic jobs to any desired degree of accuracy.[[19]](#cite_note-hs-19)

### Jobs consisting of multiple operations

[[edit](/w/index.php?title=Job-shop_scheduling&veaction=edit&section=9 "Edit section: Jobs consisting of multiple operations") | [edit source](/w/index.php?title=Job-shop_scheduling&action=edit&section=9 "Edit section's source code: Jobs consisting of multiple operations")]

The basic form of the problem of scheduling jobs with multiple (M) operations, over M machines, such that all of the first operations must be done on the first machine, all of the second operations on the second, etc., and a single job cannot be performed in parallel, is known as the [flow-shop scheduling](/wiki/Flow-shop_scheduling "Flow-shop scheduling") problem. Various algorithms exist, including [genetic algorithms](/wiki/Genetic_algorithm "Genetic algorithm").[[20]](#cite_note-ossp-ga-20)

#### Johnson's algorithm

[[edit](/w/index.php?title=Job-shop_scheduling&veaction=edit&section=10 "Edit section: Johnson's algorithm") | [edit source](/w/index.php?title=Job-shop_scheduling&action=edit&section=10 "Edit section's source code: Johnson's algorithm")]

See also: [Johnson's rule](/wiki/Johnson%27s_rule "Johnson's rule")

A heuristic algorithm by S. M. Johnson can be used to solve the case of a 2 machine N job problem when all jobs are to be processed in the same order.[[21]](#cite_note-21) The steps of algorithm are as follows:

Job Pi has two operations, of duration Pi1, Pi2, to be done on Machine M1, M2 in that sequence.

- *Step 1.* List A = { 1, 2, …, N }, List L1 = {}, List L2 = {}.
- *Step 2.* From all available operation durations, pick the minimum.

If the minimum belongs to Pk1,

Remove K from list A; Add K to end of List L1.

If minimum belongs to Pk2,

Remove K from list A; Add K to beginning of List L2.

- *Step 3.* Repeat Step 2 until List A is empty.
- *Step 4.* Join List L1, List L2. This is the optimum sequence.

Johnson's method only works optimally for two machines. However, since it is optimal, and easy to compute, some researchers have tried to adopt it for M machines, (*M* > 2.)

The idea is as follows: Imagine that each job requires m operations in sequence, on M1, M2 … Mm. We combine the first *m*/2 machines into an (imaginary) Machining center, MC1, and the remaining Machines into a Machining Center MC2. Then the total processing time for a Job P on MC1 = sum (operation times on first *m*/2 machines), and processing time for Job P on MC2 = sum(operation times on last *m*/2 machines).

By doing so, we have reduced the m-Machine problem into a Two Machining center scheduling problem. We can solve this using Johnson's method.

## Makespan prediction

[[edit](/w/index.php?title=Job-shop_scheduling&veaction=edit&section=11 "Edit section: Makespan prediction") | [edit source](/w/index.php?title=Job-shop_scheduling&action=edit&section=11 "Edit section's source code: Makespan prediction")]

Machine learning has been recently used to *predict* the optimal makespan of a JSP instance without actually producing the optimal schedule.[[8]](#cite_note-:0-8) Preliminary results show around 80% accuracy in classifying small randomly generated JSP instances by optimal scheduling efficiency using supervised learning.

## Example

[[edit](/w/index.php?title=Job-shop_scheduling&veaction=edit&section=12 "Edit section: Example") | [edit source](/w/index.php?title=Job-shop_scheduling&action=edit&section=12 "Edit section's source code: Example")]

Here is an example of a job-shop scheduling problem formulated in [AMPL](/wiki/AMPL "AMPL") as a [mixed-integer programming](/wiki/Linear_programming#Integer_unknowns "Linear programming") problem with indicator constraints:

```
param N_JOBS;
param N_MACHINES;

set JOBS ordered = 1..N_JOBS;
set MACHINES ordered = 1..N_MACHINES;

param ProcessingTime{JOBS, MACHINES} > 0;

param CumulativeTime{i in JOBS, j in MACHINES} =
   sum {jj in MACHINES: ord(jj) <= ord(j)} ProcessingTime[i,jj];

param TimeOffset{i1 in JOBS, i2 in JOBS: i1 <> i2} =
   max {j in MACHINES}
     (CumulativeTime[i1,j] - CumulativeTime[i2,j] + ProcessingTime[i2,j]);

var end >= 0;
var start{JOBS} >= 0;
var precedes{i1 in JOBS, i2 in JOBS: ord(i1) < ord(i2)} binary;

minimize makespan: end;

subj to makespan_def{i in JOBS}:
   end >= start[i] + sum{j in MACHINES} ProcessingTime[i,j];

subj to no12_conflict{i1 in JOBS, i2 in JOBS: ord(i1) < ord(i2)}:
   precedes[i1,i2] ==> start[i2] >= start[i1] + TimeOffset[i1,i2];

subj to no21_conflict{i1 in JOBS, i2 in JOBS: ord(i1) < ord(i2)}:
   !precedes[i1,i2] ==> start[i1] >= start[i2] + TimeOffset[i2,i1];

data;

param N_JOBS := 4;
param N_MACHINES := 4;

param ProcessingTime:
   1 2 3 4 :=
1  5 4 2 1
2  8 3 6 2
3  9 7 2 3
4  3 1 5 8;
```

## Related problems

[[edit](/w/index.php?title=Job-shop_scheduling&veaction=edit&section=13 "Edit section: Related problems") | [edit source](/w/index.php?title=Job-shop_scheduling&action=edit&section=13 "Edit section's source code: Related problems")]

- [Flow-shop scheduling](/wiki/Flow-shop_scheduling "Flow-shop scheduling") is a similar problem but without the constraint that each operation must be done on a specific machine (only the order constraint is kept).
- [Open-shop scheduling](/wiki/Open-shop_scheduling "Open-shop scheduling") is a similar problem but also without the order constraint.

## See also

[[edit](/w/index.php?title=Job-shop_scheduling&veaction=edit&section=14 "Edit section: See also") | [edit source](/w/index.php?title=Job-shop_scheduling&action=edit&section=14 "Edit section's source code: See also")]

.mw-parser-output .div-col{margin-top:0.3em;column-width:30em}.mw-parser-output .div-col-small{font-size:90%}.mw-parser-output .div-col-rules{column-rule:1px solid #aaa}.mw-parser-output .div-col dl,.mw-parser-output .div-col ol,.mw-parser-output .div-col ul{margin-top:0}.mw-parser-output .div-col li,.mw-parser-output .div-col dd{page-break-inside:avoid;break-inside:avoid-column}

- [Disjunctive graph](/wiki/Disjunctive_graph "Disjunctive graph")
- [Dynamic programming](/wiki/Dynamic_programming "Dynamic programming")
- [Genetic algorithm scheduling](/wiki/Genetic_algorithm_scheduling "Genetic algorithm scheduling")
- [List of NP-complete problems](/wiki/List_of_NP-complete_problems "List of NP-complete problems")
- [Optimal control](/wiki/Optimal_control "Optimal control")
- [Scheduling (production processes)](/wiki/Scheduling_(production_processes) "Scheduling (production processes)")

## References

[[edit](/w/index.php?title=Job-shop_scheduling&veaction=edit&section=15 "Edit section: References") | [edit source](/w/index.php?title=Job-shop_scheduling&action=edit&section=15 "Edit section's source code: References")]

.mw-parser-output .reflist-columns-2{column-width:30em}.mw-parser-output .reflist-columns-3{column-width:25em}body.skin-vector-2022 .mw-parser-output .reflist-columns-2{column-width:27em}body.skin-vector-2022 .mw-parser-output .reflist-columns-3{column-width:22.5em}.mw-parser-output .references[data-mw-group=upper-alpha]{list-style-type:upper-alpha}.mw-parser-output .references[data-mw-group=upper-roman]{list-style-type:upper-roman}.mw-parser-output .references[data-mw-group=lower-alpha]{list-style-type:lower-alpha}.mw-parser-output .references[data-mw-group=lower-greek]{list-style-type:lower-greek}.mw-parser-output .references[data-mw-group=lower-roman]{list-style-type:lower-roman}.mw-parser-output div.reflist-liststyle-upper-alpha .references{list-style-type:upper-alpha}.mw-parser-output div.reflist-liststyle-upper-roman .references{list-style-type:upper-roman}.mw-parser-output div.reflist-liststyle-lower-alpha .references{list-style-type:lower-alpha}.mw-parser-output div.reflist-liststyle-lower-greek .references{list-style-type:lower-greek}.mw-parser-output div.reflist-liststyle-lower-roman .references{list-style-type:lower-roman}

1. ^ [***a***](#cite_ref-graham1966_1-0) [***b***](#cite_ref-graham1966_1-1) .mw-parser-output cite.citation{font-style:inherit;word-wrap:break-word}.mw-parser-output .citation q{quotes:"\"""\"""'""'"}.mw-parser-output .citation:target{background-color:rgba(0,127,255,0.133)}.mw-parser-output .id-lock-free.id-lock-free a{background:url("//upload.wikimedia.org/wikipedia/commons/6/65/Lock-green.svg")right 0.1em center/9px no-repeat}.mw-parser-output .id-lock-limited.id-lock-limited a,.mw-parser-output .id-lock-registration.id-lock-registration a{background:url("//upload.wikimedia.org/wikipedia/commons/d/d6/Lock-gray-alt-2.svg")right 0.1em center/9px no-repeat}.mw-parser-output .id-lock-subscription.id-lock-subscription a{background:url("//upload.wikimedia.org/wikipedia/commons/a/aa/Lock-red-alt-2.svg")right 0.1em center/9px no-repeat}.mw-parser-output .cs1-ws-icon a{background:url("//upload.wikimedia.org/wikipedia/commons/4/4c/Wikisource-logo.svg")right 0.1em center/12px no-repeat}body:not(.skin-timeless):not(.skin-minerva) .mw-parser-output .id-lock-free a,body:not(.skin-timeless):not(.skin-minerva) .mw-parser-output .id-lock-limited a,body:not(.skin-timeless):not(.skin-minerva) .mw-parser-output .id-lock-registration a,body:not(.skin-timeless):not(.skin-minerva) .mw-parser-output .id-lock-subscription a,body:not(.skin-timeless):not(.skin-minerva) .mw-parser-output .cs1-ws-icon a{background-size:contain;padding:0 1em 0 0}.mw-parser-output .cs1-code{color:inherit;background:inherit;border:none;padding:inherit}.mw-parser-output .cs1-hidden-error{display:none;color:var(--color-error,#bf3c2c)}.mw-parser-output .cs1-visible-error{color:var(--color-error,#bf3c2c)}.mw-parser-output .cs1-maint{display:none;color:#085;margin-left:0.3em}.mw-parser-output .cs1-kern-left{padding-left:0.2em}.mw-parser-output .cs1-kern-right{padding-right:0.2em}.mw-parser-output .citation .mw-selflink{font-weight:inherit}@media screen{.mw-parser-output .cs1-format{font-size:95%}html.skin-theme-clientpref-night .mw-parser-output .cs1-maint{color:#18911f}}@media screen and (prefers-color-scheme:dark){html.skin-theme-clientpref-os .mw-parser-output .cs1-maint{color:#18911f}}Graham, R. (1966). ["Bounds for certain multiprocessing anomalies"](http://www.math.ucsd.edu/~ronspubs/66_04_multiprocessing.pdf) (PDF). *Bell System Technical Journal*. **45** (9): 1563–1581. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1002/j.1538-7305.1966.tb01709.x](https://doi.org/10.1002%2Fj.1538-7305.1966.tb01709.x).
2. **[^](#cite_ref-TaillardIns_2-0)** ["Taillard Instances"](http://mistic.heig-vd.ch/taillard/problemes.dir/ordonnancement.dir/ordonnancement.html). *mistic.heig-vd.ch*. Retrieved 2025-03-17.
3. **[^](#cite_ref-3)** Maccarthy (1993). "Addressing the gap in scheduling research: a review of optimization and heuristic methods in production scheduling".
4. **[^](#cite_ref-4)** Malakooti, B (2013). *Operations and Production Systems with Multiple Objectives*. John Wiley & Sons. [ISBN](/wiki/ISBN_(identifier) "ISBN (identifier)") [978-1-118-58537-5](/wiki/Special:BookSources/978-1-118-58537-5 "Special:BookSources/978-1-118-58537-5").
5. **[^](#cite_ref-5)** Sharma, P. (March 2016). "A review on job shop scheduling with setup times". *Proceedings of the Institution of Mechanical Engineers, Part B: Journal of Engineering Manufacture*. **230** (3): 517–533. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1177/0954405414560617](https://doi.org/10.1177%2F0954405414560617). [ISSN](/wiki/ISSN_(identifier) "ISSN (identifier)") [0954-4054](https://search.worldcat.org/issn/0954-4054).
6. **[^](#cite_ref-6)** B. Roy, B. Sussmann, Les problèmes d'ordonnancement avec constraintes disjonctives, SEMA, Note D.S., No. 9, Paris, 1964.
7. **[^](#cite_ref-7)** Błażewicz, Jacek (December 2000). "The disjunctive graph machine representation of the job shop scheduling problem". *European Journal of Operational Research*. **127** (2): 317–331. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1016/S0377-2217(99)00486-5](https://doi.org/10.1016%2FS0377-2217%2899%2900486-5). [ISSN](/wiki/ISSN_(identifier) "ISSN (identifier)") [0377-2217](https://search.worldcat.org/issn/0377-2217).
8. ^ [***a***](#cite_ref-:0_8-0) [***b***](#cite_ref-:0_8-1) Mirshekarian, Sadegh; Šormaz, Dušan N. (9 June 2016). ["Correlation of job-shop scheduling problem features with scheduling efficiency"](https://web.archive.org/web/20180417034243/http://mirshekarian.me/files/corrJSSP.pdf) (PDF). *[Expert Systems with Applications](/wiki/Expert_Systems_with_Applications "Expert Systems with Applications")*. **62**: 131–147. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1016/j.eswa.2016.06.014](https://doi.org/10.1016%2Fj.eswa.2016.06.014). Archived from [the original](https://mirshekarian.me/files/corrJSSP.pdf) (PDF) on 2018-04-17.
9. **[^](#cite_ref-9)** [Coffman, E. G. Jr.](/wiki/Edward_G._Coffman_Jr. "Edward G. Coffman Jr."); [Graham, R. L.](/wiki/Ronald_Graham "Ronald Graham") (1972), ["Optimal scheduling for two-processor systems"](http://www.math.ucsd.edu/~ronspubs/72_04_two_processors.pdf) (PDF), *Acta Informatica*, **1** (3): 200–213, [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1007/bf00288685](https://doi.org/10.1007%2Fbf00288685), [MR](/wiki/MR_(identifier) "MR (identifier)") [0334913](https://mathscinet.ams.org/mathscinet-getitem?mr=0334913), [S2CID](/wiki/S2CID_(identifier) "S2CID (identifier)") [40603807](https://api.semanticscholar.org/CorpusID:40603807).
10. **[^](#cite_ref-10)** Lam, Shui; [Sethi, Ravi](/wiki/Ravi_Sethi "Ravi Sethi") (1977), "Worst case analysis of two scheduling algorithms", *[SIAM Journal on Computing](/wiki/SIAM_Journal_on_Computing "SIAM Journal on Computing")*, **6** (3): 518–536, [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1137/0206037](https://doi.org/10.1137%2F0206037), [MR](/wiki/MR_(identifier) "MR (identifier)") [0496614](https://mathscinet.ams.org/mathscinet-getitem?mr=0496614).
11. **[^](#cite_ref-11)** Bartal, Y.; A. Fiat; H. Karloff; R. Vohra (1992). "New Algorithms for an Ancient Scheduling Problem". *Proc. 24th ACM Symp*. Theory of Computing. pp. 51–58. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1145/129712.129718](https://doi.org/10.1145%2F129712.129718).
12. **[^](#cite_ref-12)** [Karger, D.](/wiki/David_Karger "David Karger"); S. Phillips; E. Torng (1994). ["A Better Algorithm for an Ancient Scheduling Problem"](http://portal.acm.org/citation.cfm?doid=314464.314487). *Proc. Fifth ACM Symp*. Discrete Algorithms.
13. **[^](#cite_ref-13)** [Albers, Susanne](/wiki/Susanne_Albers "Susanne Albers"); Torben Hagerup (1992). ["Improved parallel integer sorting without concurrent writing"](http://portal.acm.org/citation.cfm?id=139404.139491). *Proceedings of the third annual ACM-SIAM symposium on Discrete algorithms*. Symposium on Discrete Algorithms archive. pp. 463–472.
14. **[^](#cite_ref-14)** Fleischer, Rudolf (2000). *Algorithms – ESA 2000*. Berlin / Heidelberg: Springer. pp. 202–210. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1007/3-540-45253-2\_19](https://doi.org/10.1007%2F3-540-45253-2_19). [ISBN](/wiki/ISBN_(identifier) "ISBN (identifier)") [978-3-540-41004-1](/wiki/Special:BookSources/978-3-540-41004-1 "Special:BookSources/978-3-540-41004-1").
15. **[^](#cite_ref-15)** [Albers, Susanne](/wiki/Susanne_Albers "Susanne Albers") (1999). "Better bounds for online scheduling". *[SIAM Journal on Computing](/wiki/SIAM_Journal_on_Computing "SIAM Journal on Computing")*. **29** (2): 459–473. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1137/S0097539797324874](https://doi.org/10.1137%2FS0097539797324874). [hdl](/wiki/Hdl_(identifier) "Hdl (identifier)"):[11858/00-001M-0000-0014-9E1F-1](https://hdl.handle.net/11858%2F00-001M-0000-0014-9E1F-1).
16. **[^](#cite_ref-garey1976_16-0)** Garey, M. R.; Johnson, D. S.; Sethi, Ravi (1976). "The Complexity of Flowshop and Jobshop Scheduling". *[Mathematics of Operations Research](/wiki/Mathematics_of_Operations_Research "Mathematics of Operations Research")*. **1** (2): 117–129. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1287/moor.1.2.117](https://doi.org/10.1287%2Fmoor.1.2.117). [JSTOR](/wiki/JSTOR_(identifier) "JSTOR (identifier)") [3689278](https://www.jstor.org/stable/3689278).
17. **[^](#cite_ref-17)** Chen, Xin; Lan, Yan; Benkő, Attila; Dósa, György; Han, Xin (2011). ["*Optimal algorithms for online scheduling with bounded rearrangement at the end*"](https://doi.org/10.1016%2Fj.tcs.2011.07.014). *Theoretical Computer Science*. **412** (45): 6269–6278. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1016/j.tcs.2011.07.014](https://doi.org/10.1016%2Fj.tcs.2011.07.014).
18. **[^](#cite_ref-18)** Liu, M.; Xu, Y.; Chu, C.; Zheng, F. (2009). ["Online scheduling on two uniform machines to minimize the makespan"](https://doi.org/10.1016%2Fj.tcs.2009.01.007). *Theoret. Comput. Sci*. **410** (21–23): 2099–2109. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1016/j.tcs.2009.01.007](https://doi.org/10.1016%2Fj.tcs.2009.01.007).
19. **[^](#cite_ref-hs_19-0)** [Hochbaum, Dorit](/wiki/Dorit_S._Hochbaum "Dorit S. Hochbaum"); [Shmoys, David](/wiki/David_Shmoys "David Shmoys") (1987). ["Using dual approximation algorithms for scheduling problems: theoretical and practical results"](http://www.columbia.edu/~cs2035/courses/ieor6400.F07/hs.pdf) (PDF). *[Journal of the ACM](/wiki/Journal_of_the_ACM "Journal of the ACM")*. **34** (1): 144–162. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1145/7531.7535](https://doi.org/10.1145%2F7531.7535). [S2CID](/wiki/S2CID_(identifier) "S2CID (identifier)") [9739129](https://api.semanticscholar.org/CorpusID:9739129).
20. **[^](#cite_ref-ossp-ga_20-0)** Khuri, Sami; Miryala, Sowmya Rao (1999). "Genetic Algorithms for Solving Open Shop Scheduling Problems". *Proceedings of the 9th Portuguese Conference on Artificial Intelligence: Progress in Artificial Intelligence*. London: [Springer Verlag](/wiki/Springer_Verlag "Springer Verlag"). [CiteSeerX](/wiki/CiteSeerX_(identifier) "CiteSeerX (identifier)") [10.1.1.29.4699](https://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.29.4699). `{{cite conference}}`: Cite uses deprecated parameter `|citeseerx=` ([help](/wiki/Help:CS1_errors#deprecated_params "Help:CS1 errors"))
21. **[^](#cite_ref-21)** S.M. Johnson, Optimal two- and three-stage production schedules with setup times included, Naval Res. Log. Quart. I(1954)61-68.

## External links

[[edit](/w/index.php?title=Job-shop_scheduling&veaction=edit&section=16 "Edit section: External links") | [edit source](/w/index.php?title=Job-shop_scheduling&action=edit&section=16 "Edit section's source code: External links")]

- [University of Vienna](https://www.mat.univie.ac.at/~neum/glopt/software_g.html) Directory of methodologies, systems and software for dynamic optimization.
- [Taillard instances](http://mistic.heig-vd.ch/taillard/problemes.dir/ordonnancement.dir/jobshop.dir/best_lb_up.txt)
- *Brucker P.* [Scheduling Algorithms](https://link.springer.com/content/pdf/bfm%3A978-3-540-24804-0%2F1.pdf). Heidelberg, Springer. Fifth ed. [ISBN](/wiki/ISBN_(identifier) "ISBN (identifier)") [978-3-540-24804-0](/wiki/Special:BookSources/978-3-540-24804-0 "Special:BookSources/978-3-540-24804-0")

.mw-parser-output .hlist dl,.mw-parser-output .hlist ol,.mw-parser-output .hlist ul{margin:0;padding:0}.mw-parser-output .hlist dd,.mw-parser-output .hlist dt,.mw-parser-output .hlist li{margin:0;display:inline}.mw-parser-output .hlist.inline,.mw-parser-output .hlist.inline dl,.mw-parser-output .hlist.inline ol,.mw-parser-output .hlist.inline ul,.mw-parser-output .hlist dl dl,.mw-parser-output .hlist dl ol,.mw-parser-output .hlist dl ul,.mw-parser-output .hlist ol dl,.mw-parser-output .hlist ol ol,.mw-parser-output .hlist ol ul,.mw-parser-output .hlist ul dl,.mw-parser-output .hlist ul ol,.mw-parser-output .hlist ul ul{display:inline}.mw-parser-output .hlist .mw-empty-li{display:none}.mw-parser-output .hlist dt::after{content:": "}.mw-parser-output .hlist dd::after,.mw-parser-output .hlist li::after{content:"\a0 · ";font-weight:bold}.mw-parser-output .hlist dd:last-child::after,.mw-parser-output .hlist dt:last-child::after,.mw-parser-output .hlist li:last-child::after{content:none}.mw-parser-output .hlist dd dd:first-child::before,.mw-parser-output .hlist dd dt:first-child::before,.mw-parser-output .hlist dd li:first-child::before,.mw-parser-output .hlist dt dd:first-child::before,.mw-parser-output .hlist dt dt:first-child::before,.mw-parser-output .hlist dt li:first-child::before,.mw-parser-output .hlist li dd:first-child::before,.mw-parser-output .hlist li dt:first-child::before,.mw-parser-output .hlist li li:first-child::before{content:" (";font-weight:normal}.mw-parser-output .hlist dd dd:last-child::after,.mw-parser-output .hlist dd dt:last-child::after,.mw-parser-output .hlist dd li:last-child::after,.mw-parser-output .hlist dt dd:last-child::after,.mw-parser-output .hlist dt dt:last-child::after,.mw-parser-output .hlist dt li:last-child::after,.mw-parser-output .hlist li dd:last-child::after,.mw-parser-output .hlist li dt:last-child::after,.mw-parser-output .hlist li li:last-child::after{content:")";font-weight:normal}.mw-parser-output .hlist ol{counter-reset:listitem}.mw-parser-output .hlist ol>li{counter-increment:listitem}.mw-parser-output .hlist ol>li::before{content:" "counter(listitem)"\a0 "}.mw-parser-output .hlist dd ol>li:first-child::before,.mw-parser-output .hlist dt ol>li:first-child::before,.mw-parser-output .hlist li ol>li:first-child::before{content:" ("counter(listitem)"\a0 "}.mw-parser-output .navbox{box-sizing:border-box;border:1px solid #a2a9b1;width:100%;clear:both;font-size:88%;text-align:center;padding:1px;margin:1em auto 0}.mw-parser-output .navbox .navbox{margin-top:0}.mw-parser-output .navbox+.navbox-styles+.navbox,.mw-parser-output .navbox+span.mw-empty-elt+.navbox-styles+.navbox{margin-top:-1px}.mw-parser-output .navbox-inner,.mw-parser-output .navbox-subgroup{width:100%}.mw-parser-output .navbox-group,.mw-parser-output .navbox-title,.mw-parser-output .navbox-abovebelow{padding:0.25em 1em;line-height:1.5em;text-align:center}.mw-parser-output .navbox-group{white-space:nowrap;text-align:right}.mw-parser-output .navbox,.mw-parser-output .navbox-subgroup{background-color:#fdfdfd;color:inherit}.mw-parser-output .navbox-list{line-height:1.5em;border-color:#fdfdfd}.mw-parser-output .navbox-list-with-group{text-align:left;border-left-width:2px;border-left-style:solid}.mw-parser-output tr+tr>.navbox-abovebelow,.mw-parser-output tr+tr>.navbox-group,.mw-parser-output tr+tr>.navbox-image,.mw-parser-output tr+tr>.navbox-list{border-top:2px solid #fdfdfd}.mw-parser-output .navbox-title{background-color:#ccf;color:inherit}.mw-parser-output .navbox-abovebelow,.mw-parser-output .navbox-group,.mw-parser-output .navbox-subgroup .navbox-title{background-color:#ddf;color:inherit}.mw-parser-output .navbox-subgroup .navbox-group,.mw-parser-output .navbox-subgroup .navbox-abovebelow{background-color:#e6e6ff;color:inherit}.mw-parser-output .navbox-even{background-color:#f7f7f7;color:inherit}.mw-parser-output .navbox-odd{background-color:transparent;color:inherit}.mw-parser-output .navbox .hlist td dl,.mw-parser-output .navbox .hlist td ol,.mw-parser-output .navbox .hlist td ul,.mw-parser-output .navbox td.hlist dl,.mw-parser-output .navbox td.hlist ol,.mw-parser-output .navbox td.hlist ul{padding:0.125em 0}.mw-parser-output .navbox .navbar{display:block;font-size:100%}.mw-parser-output .navbox-title .navbar{float:left;text-align:left;margin-right:0.5em}body.skin--responsive .mw-parser-output .navbox-image img{max-width:none!important}@media print{body.ns-0 .mw-parser-output .navbox{display:none!important}}

| .mw-parser-output .navbar{display:inline;font-size:88%;font-weight:normal}.mw-parser-output .navbar-collapse{float:left;text-align:left}.mw-parser-output .navbar-boxtext{word-spacing:0}.mw-parser-output .navbar ul{display:inline-block;white-space:nowrap;line-height:inherit}.mw-parser-output .navbar-brackets::before{margin-right:-0.125em;content:"[ "}.mw-parser-output .navbar-brackets::after{margin-left:-0.125em;content:" ]"}.mw-parser-output .navbar li{word-spacing:-0.125em}.mw-parser-output .navbar a>span,.mw-parser-output .navbar a>abbr{text-decoration:inherit}.mw-parser-output .navbar-mini abbr{font-variant:small-caps;border-bottom:none;text-decoration:none;cursor:inherit}.mw-parser-output .navbar-ct-full{font-size:114%;margin:0 7em}.mw-parser-output .navbar-ct-mini{font-size:114%;margin:0 4em}html.skin-theme-clientpref-night .mw-parser-output .navbar li a abbr{color:var(--color-base)!important}@media(prefers-color-scheme:dark){html.skin-theme-clientpref-os .mw-parser-output .navbar li a abbr{color:var(--color-base)!important}}@media print{.mw-parser-output .navbar{display:none!important}} - [v](/wiki/Template:Scheduling_problems "Template:Scheduling problems") - [t](/wiki/Template_talk:Scheduling_problems "Template talk:Scheduling problems") - [e](/wiki/Special:EditPage/Template:Scheduling_problems "Special:EditPage/Template:Scheduling problems")  [Optimal job scheduling](/wiki/Optimal_job_scheduling "Optimal job scheduling") problems | |
| --- | --- |
| One-stage jobs | - [Single machine](/wiki/Single-machine_scheduling "Single-machine scheduling") - [Identical machines](/wiki/Identical-machines_scheduling "Identical-machines scheduling") - [Uniform machines](/wiki/Uniform-machines_scheduling "Uniform-machines scheduling") - [Unrelated machines](/wiki/Unrelated-machines_scheduling "Unrelated-machines scheduling") |
| Multi-stage jobs | - [Parallel tasks](/wiki/Parallel_task_scheduling "Parallel task scheduling") - [Open shop](/wiki/Open-shop_scheduling "Open-shop scheduling") - [Flow shop](/wiki/Flow-shop_scheduling "Flow-shop scheduling") - Job shop |
| Optimization objectives | - [Makespan](/wiki/Makespan "Makespan") - [Earliness](/wiki/Earliness_(scheduling) "Earliness (scheduling)") - [Lateness](/wiki/Lateness_(scheduling) "Lateness (scheduling)") - [Tardiness](/wiki/Tardiness_(scheduling) "Tardiness (scheduling)") - [Throughput](/wiki/Network_throughput "Network throughput") |
| Other requirements | - [Interval scheduling](/wiki/Interval_scheduling "Interval scheduling") - [Truthful job scheduling](/wiki/Truthful_job_scheduling "Truthful job scheduling") |
