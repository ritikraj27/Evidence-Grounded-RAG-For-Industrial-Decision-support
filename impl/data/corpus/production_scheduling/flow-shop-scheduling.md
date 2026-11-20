<!-- category: production_scheduling -->
# Flow shop scheduling

Class of computational problem

[![](//thumb.wikimedia.org/wikipedia/commons/thumb/5/5a/Flow_Shop_Ordonnancement.JPEG/250px-Flow_Shop_Ordonnancement.JPEG?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail)](/wiki/File:Flow_Shop_Ordonnancement.JPEG)

Flow Shop Ordonnancement

**Flow-shop scheduling** is an [optimization problem](/wiki/Optimization_problem "Optimization problem") in [computer science](/wiki/Computer_science "Computer science") and [operations research](/wiki/Operations_Research "Operations Research"). It is a variant of [optimal job scheduling](/wiki/Optimal_job_scheduling "Optimal job scheduling"). In a general job-scheduling problem, we are given *n* jobs *J*1, *J*2, ..., *Jn* of varying processing times, which need to be scheduled on *m* machines with varying processing power, while trying to minimize the [makespan](/wiki/Makespan "Makespan") – the total length of the schedule (that is, when all the jobs have finished processing). In the specific variant known as *flow-shop scheduling*, each job contains exactly *m* operations. The *i*-th operation of the job must be executed on the *i*-th machine. No machine can perform more than one operation simultaneously. For each operation of each job, execution time is specified.

Flow-shop scheduling is a special case of [job-shop scheduling](/wiki/Job-shop_scheduling "Job-shop scheduling") where there is strict order of all operations to be performed on all jobs. Flow-shop scheduling may apply as well to [production](/wiki/Manufacturing "Manufacturing") facilities as to [computing](/wiki/Computing "Computing") designs. A special type of flow-shop scheduling problem is the **permutation flow-shop scheduling** problem in which the [processing](/wiki/Process_(engineering) "Process (engineering)") order of the jobs on the resources is the same for each subsequent step of processing.

In the standard [three-field notation for optimal-job-scheduling problems](/wiki/Optimal_job_scheduling "Optimal job scheduling"), the flow-shop variant is denoted by **F** in the first field. For example, the problem denoted by " **F3|

p

i
j
{\displaystyle p\_{ij}}
![{\displaystyle p_{ij}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/ca46e6d560ac4e615adcd6d053cd476f4aadfcbd)|**

C

max
{\displaystyle C\_{\max }}
![{\displaystyle C_{\max }}](https://wikimedia.org/api/rest_v1/media/math/render/svg/a9a28f3ceb6f7bc46a4cdf492f771e2ad7e7f288)" is a 3-machines flow-shop problem with unit processing times, where the goal is to minimize the maximum completion time.

## Formal definition

[[edit](/w/index.php?title=Flow-shop_scheduling&veaction=edit&section=1 "Edit section: Formal definition") | [edit source](/w/index.php?title=Flow-shop_scheduling&action=edit&section=1 "Edit section's source code: Formal definition")]

There are *m* machines and *n* jobs. Each job contains exactly *m* operations. The *i*-th operation of the job must be executed on the *i*-th machine. No machine can perform more than one operation simultaneously. For each operation of each job, execution time is specified.

Operations within one job must be performed in the specified order. The first operation gets executed on the first machine, then (as the first operation is finished) the second operation on the second machine, and so on until the *m*-th operation. Jobs can be executed in any order, however. The problem is to determine the optimal such arrangement, i.e. the one with the shortest possible total job execution makespan.

## Sequencing performance measurements (γ)

[[edit](/w/index.php?title=Flow-shop_scheduling&veaction=edit&section=2 "Edit section: Sequencing performance measurements (γ)") | [edit source](/w/index.php?title=Flow-shop_scheduling&action=edit&section=2 "Edit section's source code: Sequencing performance measurements (γ)")]

The sequencing problem can be stated as determining a sequence S such that one or several sequencing objectives are optimized.

1. (Average) Flow time, 

   ∑
   (

   w

   i
   )

   F

   i
   {\displaystyle \sum (w\_{i})F\_{i}}
   ![{\displaystyle \sum (w_{i})F_{i}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/15b45ce520aa9e6337c41c4f83806a0f265a9ddc)
2. Makespan, Cmax
3. (Average) Tardiness, 

   ∑
   (

   w

   i
   )

   T

   i
   {\displaystyle \sum (w\_{i})T\_{i}}
   ![{\displaystyle \sum (w_{i})T_{i}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/8158e31e4306d05f45f454c9b1bb59ab1927780d)
4. ....

detailed discussion of performance measurement can be found in [Malakooti](/wiki/Behnam_Malakooti "Behnam Malakooti")(2013).[[1]](#cite_note-Malakooti-1)

## Complexity of flow-shop scheduling

[[edit](/w/index.php?title=Flow-shop_scheduling&veaction=edit&section=3 "Edit section: Complexity of flow-shop scheduling") | [edit source](/w/index.php?title=Flow-shop_scheduling&action=edit&section=3 "Edit section's source code: Complexity of flow-shop scheduling")]

As presented by Garey et al. (1976),[[2]](#cite_note-Garey-2) most of extensions of the flow-shop-scheduling problems are NP-hard and few of them can be solved optimally in O(nlogn); for example, F2|prmu|Cmax can be solved optimally by using [Johnson's Rule](/wiki/Johnson%27s_Rule "Johnson's Rule").[[3]](#cite_note-Johnson-3)

Taillard provides substantial benchmark problems for scheduling flow shops, open shops, and job shops.[[4]](#cite_note-Taillard-4)

## Solution methods

[[edit](/w/index.php?title=Flow-shop_scheduling&veaction=edit&section=4 "Edit section: Solution methods") | [edit source](/w/index.php?title=Flow-shop_scheduling&action=edit&section=4 "Edit section's source code: Solution methods")]

The proposed methods to solve flow-shop-scheduling problems can be classified as [exact algorithm](/wiki/Exact_algorithm "Exact algorithm") such as [branch and bound](/wiki/Branch_and_bound "Branch and bound") and [heuristic algorithm](/wiki/Heuristic_algorithm "Heuristic algorithm") such as [genetic algorithm](/wiki/Genetic_algorithm "Genetic algorithm").

### Minimizing makespan, Cmax

[[edit](/w/index.php?title=Flow-shop_scheduling&veaction=edit&section=5 "Edit section: Minimizing makespan, Cmax") | [edit source](/w/index.php?title=Flow-shop_scheduling&action=edit&section=5 "Edit section's source code: Minimizing makespan, Cmax")]

F2|prmu|Cmax and F3|prmu|Cmax can be solved optimally by using [Johnson's Rule](/wiki/Johnson%27s_Rule "Johnson's Rule")[[3]](#cite_note-Johnson-3) but for general case there is no algorithm that guarantee the optimality of the solution.

The flow shop contains n jobs simultaneously available at time zero and to be processed by two machines arranged in series with unlimited storage in between them. The processing time of all jobs are known with certainty. It is required to schedule n jobs on machines so as to minimize makespan. The Johnson's rule for scheduling jobs in two-machine flow shop is given below.

In an optimal schedule, job i precedes job j if *min{p1i,p2j} < min{p1j,p2i}*. Where as, p1i is the processing time of job i on machine 1 and p2i is the processing time of job i on machine 2. Similarly, p1j and p2j are processing times of job j on machine 1 and machine 2 respectively.

For Johnson's algorithm:

:   Let p1j be the processing time of job j on machine 1
:   and p2j the processing time of job j on machine 2

Johnson's algorithm:

1. Form set1 containing all the jobs with p1j < p2j
2. Form set2 containing all the jobs with p1j > p2j, the jobs with p1j = p2j may be put in either set.
3. Form the sequence as follows:

   :   (i) The job in set1 go first in the sequence and they go in increasing order of p1j (SPT)
   :   (ii) The jobs in set2 follow in decreasing order of p2j (LPT). Ties are broken arbitrarily.

This type schedule is referred as SPT(1)–LPT(2) schedule.

A detailed discussion of the available solution methods are provided by [Malakooti](/wiki/Behnam_Malakooti "Behnam Malakooti") (2013).[[1]](#cite_note-Malakooti-1)

## See also

[[edit](/w/index.php?title=Flow-shop_scheduling&veaction=edit&section=6 "Edit section: See also") | [edit source](/w/index.php?title=Flow-shop_scheduling&action=edit&section=6 "Edit section's source code: See also")]

- [Open-shop scheduling](/wiki/Open-shop_scheduling "Open-shop scheduling")
- [Job-shop scheduling](/wiki/Job-shop_scheduling "Job-shop scheduling")

## References

[[edit](/w/index.php?title=Flow-shop_scheduling&veaction=edit&section=7 "Edit section: References") | [edit source](/w/index.php?title=Flow-shop_scheduling&action=edit&section=7 "Edit section's source code: References")]

.mw-parser-output .reflist-columns-2{column-width:30em}.mw-parser-output .reflist-columns-3{column-width:25em}body.skin-vector-2022 .mw-parser-output .reflist-columns-2{column-width:27em}body.skin-vector-2022 .mw-parser-output .reflist-columns-3{column-width:22.5em}.mw-parser-output .references[data-mw-group=upper-alpha]{list-style-type:upper-alpha}.mw-parser-output .references[data-mw-group=upper-roman]{list-style-type:upper-roman}.mw-parser-output .references[data-mw-group=lower-alpha]{list-style-type:lower-alpha}.mw-parser-output .references[data-mw-group=lower-greek]{list-style-type:lower-greek}.mw-parser-output .references[data-mw-group=lower-roman]{list-style-type:lower-roman}.mw-parser-output div.reflist-liststyle-upper-alpha .references{list-style-type:upper-alpha}.mw-parser-output div.reflist-liststyle-upper-roman .references{list-style-type:upper-roman}.mw-parser-output div.reflist-liststyle-lower-alpha .references{list-style-type:lower-alpha}.mw-parser-output div.reflist-liststyle-lower-greek .references{list-style-type:lower-greek}.mw-parser-output div.reflist-liststyle-lower-roman .references{list-style-type:lower-roman}

1. ^ [***a***](#cite_ref-Malakooti_1-0) [***b***](#cite_ref-Malakooti_1-1) Malakooti, B (2013). Operations and Production Systems with Multiple Objectives. John Wiley & Sons. .mw-parser-output cite.citation{font-style:inherit;word-wrap:break-word}.mw-parser-output .citation q{quotes:"\"""\"""'""'"}.mw-parser-output .citation:target{background-color:rgba(0,127,255,0.133)}.mw-parser-output .id-lock-free.id-lock-free a{background:url("//upload.wikimedia.org/wikipedia/commons/6/65/Lock-green.svg")right 0.1em center/9px no-repeat}.mw-parser-output .id-lock-limited.id-lock-limited a,.mw-parser-output .id-lock-registration.id-lock-registration a{background:url("//upload.wikimedia.org/wikipedia/commons/d/d6/Lock-gray-alt-2.svg")right 0.1em center/9px no-repeat}.mw-parser-output .id-lock-subscription.id-lock-subscription a{background:url("//upload.wikimedia.org/wikipedia/commons/a/aa/Lock-red-alt-2.svg")right 0.1em center/9px no-repeat}.mw-parser-output .cs1-ws-icon a{background:url("//upload.wikimedia.org/wikipedia/commons/4/4c/Wikisource-logo.svg")right 0.1em center/12px no-repeat}body:not(.skin-timeless):not(.skin-minerva) .mw-parser-output .id-lock-free a,body:not(.skin-timeless):not(.skin-minerva) .mw-parser-output .id-lock-limited a,body:not(.skin-timeless):not(.skin-minerva) .mw-parser-output .id-lock-registration a,body:not(.skin-timeless):not(.skin-minerva) .mw-parser-output .id-lock-subscription a,body:not(.skin-timeless):not(.skin-minerva) .mw-parser-output .cs1-ws-icon a{background-size:contain;padding:0 1em 0 0}.mw-parser-output .cs1-code{color:inherit;background:inherit;border:none;padding:inherit}.mw-parser-output .cs1-hidden-error{display:none;color:var(--color-error,#bf3c2c)}.mw-parser-output .cs1-visible-error{color:var(--color-error,#bf3c2c)}.mw-parser-output .cs1-maint{display:none;color:#085;margin-left:0.3em}.mw-parser-output .cs1-kern-left{padding-left:0.2em}.mw-parser-output .cs1-kern-right{padding-right:0.2em}.mw-parser-output .citation .mw-selflink{font-weight:inherit}@media screen{.mw-parser-output .cs1-format{font-size:95%}html.skin-theme-clientpref-night .mw-parser-output .cs1-maint{color:#18911f}}@media screen and (prefers-color-scheme:dark){html.skin-theme-clientpref-os .mw-parser-output .cs1-maint{color:#18911f}}[ISBN](/wiki/ISBN_(identifier) "ISBN (identifier)") [978-1-118-58537-5](/wiki/Special:BookSources/978-1-118-58537-5 "Special:BookSources/978-1-118-58537-5").
2. **[^](#cite_ref-Garey_2-0)** Garey, M. R.; Johnson, D. S.; Sethi, Ravi (1976). "The complexity of flowshop and jobshop scheduling". *[Mathematics of Operations Research](/wiki/Mathematics_of_Operations_Research "Mathematics of Operations Research")*. **1** (2): 117–129. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1287/moor.1.2.117](https://doi.org/10.1287%2Fmoor.1.2.117).
3. ^ [***a***](#cite_ref-Johnson_3-0) [***b***](#cite_ref-Johnson_3-1) Johnson, S. M. (1954). "Optimal two-and three-stage production schedules with setup times included". *Naval Research Logistics Quarterly*. **1** (1): 61–68. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1002/nav.3800010110](https://doi.org/10.1002%2Fnav.3800010110).
4. **[^](#cite_ref-Taillard_4-0)** Taillard, E. (January 1993). ["Benchmarks for basic scheduling problems"](http://ideas.repec.org/a/eee/ejores/v64y1993i2p278-285.html). *European Journal of Operational Research*. **64** (2): 278–285. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1016/0377-2217(93)90182-M](https://doi.org/10.1016%2F0377-2217%2893%2990182-M).

.mw-parser-output .hlist dl,.mw-parser-output .hlist ol,.mw-parser-output .hlist ul{margin:0;padding:0}.mw-parser-output .hlist dd,.mw-parser-output .hlist dt,.mw-parser-output .hlist li{margin:0;display:inline}.mw-parser-output .hlist.inline,.mw-parser-output .hlist.inline dl,.mw-parser-output .hlist.inline ol,.mw-parser-output .hlist.inline ul,.mw-parser-output .hlist dl dl,.mw-parser-output .hlist dl ol,.mw-parser-output .hlist dl ul,.mw-parser-output .hlist ol dl,.mw-parser-output .hlist ol ol,.mw-parser-output .hlist ol ul,.mw-parser-output .hlist ul dl,.mw-parser-output .hlist ul ol,.mw-parser-output .hlist ul ul{display:inline}.mw-parser-output .hlist .mw-empty-li{display:none}.mw-parser-output .hlist dt::after{content:": "}.mw-parser-output .hlist dd::after,.mw-parser-output .hlist li::after{content:"\a0 · ";font-weight:bold}.mw-parser-output .hlist dd:last-child::after,.mw-parser-output .hlist dt:last-child::after,.mw-parser-output .hlist li:last-child::after{content:none}.mw-parser-output .hlist dd dd:first-child::before,.mw-parser-output .hlist dd dt:first-child::before,.mw-parser-output .hlist dd li:first-child::before,.mw-parser-output .hlist dt dd:first-child::before,.mw-parser-output .hlist dt dt:first-child::before,.mw-parser-output .hlist dt li:first-child::before,.mw-parser-output .hlist li dd:first-child::before,.mw-parser-output .hlist li dt:first-child::before,.mw-parser-output .hlist li li:first-child::before{content:" (";font-weight:normal}.mw-parser-output .hlist dd dd:last-child::after,.mw-parser-output .hlist dd dt:last-child::after,.mw-parser-output .hlist dd li:last-child::after,.mw-parser-output .hlist dt dd:last-child::after,.mw-parser-output .hlist dt dt:last-child::after,.mw-parser-output .hlist dt li:last-child::after,.mw-parser-output .hlist li dd:last-child::after,.mw-parser-output .hlist li dt:last-child::after,.mw-parser-output .hlist li li:last-child::after{content:")";font-weight:normal}.mw-parser-output .hlist ol{counter-reset:listitem}.mw-parser-output .hlist ol>li{counter-increment:listitem}.mw-parser-output .hlist ol>li::before{content:" "counter(listitem)"\a0 "}.mw-parser-output .hlist dd ol>li:first-child::before,.mw-parser-output .hlist dt ol>li:first-child::before,.mw-parser-output .hlist li ol>li:first-child::before{content:" ("counter(listitem)"\a0 "}.mw-parser-output .navbox{box-sizing:border-box;border:1px solid #a2a9b1;width:100%;clear:both;font-size:88%;text-align:center;padding:1px;margin:1em auto 0}.mw-parser-output .navbox .navbox{margin-top:0}.mw-parser-output .navbox+.navbox-styles+.navbox,.mw-parser-output .navbox+span.mw-empty-elt+.navbox-styles+.navbox{margin-top:-1px}.mw-parser-output .navbox-inner,.mw-parser-output .navbox-subgroup{width:100%}.mw-parser-output .navbox-group,.mw-parser-output .navbox-title,.mw-parser-output .navbox-abovebelow{padding:0.25em 1em;line-height:1.5em;text-align:center}.mw-parser-output .navbox-group{white-space:nowrap;text-align:right}.mw-parser-output .navbox,.mw-parser-output .navbox-subgroup{background-color:#fdfdfd;color:inherit}.mw-parser-output .navbox-list{line-height:1.5em;border-color:#fdfdfd}.mw-parser-output .navbox-list-with-group{text-align:left;border-left-width:2px;border-left-style:solid}.mw-parser-output tr+tr>.navbox-abovebelow,.mw-parser-output tr+tr>.navbox-group,.mw-parser-output tr+tr>.navbox-image,.mw-parser-output tr+tr>.navbox-list{border-top:2px solid #fdfdfd}.mw-parser-output .navbox-title{background-color:#ccf;color:inherit}.mw-parser-output .navbox-abovebelow,.mw-parser-output .navbox-group,.mw-parser-output .navbox-subgroup .navbox-title{background-color:#ddf;color:inherit}.mw-parser-output .navbox-subgroup .navbox-group,.mw-parser-output .navbox-subgroup .navbox-abovebelow{background-color:#e6e6ff;color:inherit}.mw-parser-output .navbox-even{background-color:#f7f7f7;color:inherit}.mw-parser-output .navbox-odd{background-color:transparent;color:inherit}.mw-parser-output .navbox .hlist td dl,.mw-parser-output .navbox .hlist td ol,.mw-parser-output .navbox .hlist td ul,.mw-parser-output .navbox td.hlist dl,.mw-parser-output .navbox td.hlist ol,.mw-parser-output .navbox td.hlist ul{padding:0.125em 0}.mw-parser-output .navbox .navbar{display:block;font-size:100%}.mw-parser-output .navbox-title .navbar{float:left;text-align:left;margin-right:0.5em}body.skin--responsive .mw-parser-output .navbox-image img{max-width:none!important}@media print{body.ns-0 .mw-parser-output .navbox{display:none!important}}

| .mw-parser-output .navbar{display:inline;font-size:88%;font-weight:normal}.mw-parser-output .navbar-collapse{float:left;text-align:left}.mw-parser-output .navbar-boxtext{word-spacing:0}.mw-parser-output .navbar ul{display:inline-block;white-space:nowrap;line-height:inherit}.mw-parser-output .navbar-brackets::before{margin-right:-0.125em;content:"[ "}.mw-parser-output .navbar-brackets::after{margin-left:-0.125em;content:" ]"}.mw-parser-output .navbar li{word-spacing:-0.125em}.mw-parser-output .navbar a>span,.mw-parser-output .navbar a>abbr{text-decoration:inherit}.mw-parser-output .navbar-mini abbr{font-variant:small-caps;border-bottom:none;text-decoration:none;cursor:inherit}.mw-parser-output .navbar-ct-full{font-size:114%;margin:0 7em}.mw-parser-output .navbar-ct-mini{font-size:114%;margin:0 4em}html.skin-theme-clientpref-night .mw-parser-output .navbar li a abbr{color:var(--color-base)!important}@media(prefers-color-scheme:dark){html.skin-theme-clientpref-os .mw-parser-output .navbar li a abbr{color:var(--color-base)!important}}@media print{.mw-parser-output .navbar{display:none!important}} - [v](/wiki/Template:Scheduling_problems "Template:Scheduling problems") - [t](/wiki/Template_talk:Scheduling_problems "Template talk:Scheduling problems") - [e](/wiki/Special:EditPage/Template:Scheduling_problems "Special:EditPage/Template:Scheduling problems")  [Optimal job scheduling](/wiki/Optimal_job_scheduling "Optimal job scheduling") problems | |
| --- | --- |
| One-stage jobs | - [Single machine](/wiki/Single-machine_scheduling "Single-machine scheduling") - [Identical machines](/wiki/Identical-machines_scheduling "Identical-machines scheduling") - [Uniform machines](/wiki/Uniform-machines_scheduling "Uniform-machines scheduling") - [Unrelated machines](/wiki/Unrelated-machines_scheduling "Unrelated-machines scheduling") |
| Multi-stage jobs | - [Parallel tasks](/wiki/Parallel_task_scheduling "Parallel task scheduling") - [Open shop](/wiki/Open-shop_scheduling "Open-shop scheduling") - Flow shop - [Job shop](/wiki/Job-shop_scheduling "Job-shop scheduling") |
| Optimization objectives | - [Makespan](/wiki/Makespan "Makespan") - [Earliness](/wiki/Earliness_(scheduling) "Earliness (scheduling)") - [Lateness](/wiki/Lateness_(scheduling) "Lateness (scheduling)") - [Tardiness](/wiki/Tardiness_(scheduling) "Tardiness (scheduling)") - [Throughput](/wiki/Network_throughput "Network throughput") |
| Other requirements | - [Interval scheduling](/wiki/Interval_scheduling "Interval scheduling") - [Truthful job scheduling](/wiki/Truthful_job_scheduling "Truthful job scheduling") |
