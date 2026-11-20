<!-- category: facility_layout -->
# Little's law

Theorem in queueing theory

In mathematical [queueing theory](/wiki/Queueing_theory "Queueing theory"), **Little's law** (also **result**, **theorem**, **lemma**, or **formula**[[1]](#cite_note-1)[[2]](#cite_note-allen-2)) is a theorem by [John Little](/wiki/John_Little_(academic) "John Little (academic)") which states that the long-term average number of customers (*L*) in a [stationary](/wiki/Stationary_process "Stationary process") system is equal to the long-term average effective arrival rate (*λ*) multiplied by the average time that a customer spends in the system (*W*). Expressed algebraically the law is

:   L
    =
    λ
    W
    .
    {\displaystyle L=\lambda W.}
    ![{\displaystyle L=\lambda W.}](https://wikimedia.org/api/rest_v1/media/math/render/svg/0dad0c564990973535a7f5f5e7507a1dc727f904)

The relationship is not influenced by the arrival process distribution, the service distribution, the service order, or practically anything else. In most queuing systems, service time is the [bottleneck](/wiki/Bottleneck_(engineering) "Bottleneck (engineering)") that creates the queue.[[3]](#cite_note-3)

The result applies to any system, and particularly, it applies to systems within systems.[[4]](#cite_note-4) For example in a bank branch, the [customer line](/wiki/Queue_area "Queue area") might be one subsystem, and each of the [tellers](/wiki/Bank_teller "Bank teller") another subsystem, and Little's result could be applied to each one, as well as the whole thing. The only requirement is that the system be [ergodic](/wiki/Ergodicity "Ergodicity").[[5]](#cite_note-5)

In some cases it is possible not only to mathematically relate the *average* number in the system to the *average* wait but even to relate the entire *[probability distribution](/wiki/Probability_distribution "Probability distribution")* (and moments) of the number in the system to the wait.[[6]](#cite_note-6)

## History

[[edit](/w/index.php?title=Little%27s_law&veaction=edit&section=1 "Edit section: History") | [edit source](/w/index.php?title=Little%27s_law&action=edit&section=1 "Edit section's source code: History")]

In a 1954 paper, Little's law was assumed true and used without proof.[[7]](#cite_note-little-graves-7)[[8]](#cite_note-8) The form *L* = *λW* was first published by [Philip M. Morse](/wiki/Philip_M._Morse "Philip M. Morse") where he challenged readers to find a situation where the relationship did not hold.[[7]](#cite_note-little-graves-7)[[9]](#cite_note-9) Little published in 1961 his proof of the law, showing that no such situation existed.[[10]](#cite_note-10) Little's proof was followed by a simpler version by Jewell[[11]](#cite_note-11) and another by Eilon.[[12]](#cite_note-12) Shaler Stidham published a different and more intuitive proof in 1972.[[13]](#cite_note-13)[[14]](#cite_note-14)

## Examples

[[edit](/w/index.php?title=Little%27s_law&veaction=edit&section=2 "Edit section: Examples") | [edit source](/w/index.php?title=Little%27s_law&action=edit&section=2 "Edit section's source code: Examples")]

.mw-parser-output .ambox{border:1px solid #a2a9b1;border-left:10px solid #36c;background-color:#fbfbfb;box-sizing:border-box}.mw-parser-output .ambox+.mw-empty-elt+.ambox,.mw-parser-output .ambox+.mw-empty-elt+.mw-empty-elt+.ambox,.mw-parser-output .ambox+.mw-empty-elt+.mw-empty-elt+.mw-empty-elt+.ambox{margin-top:-1px}html body.mediawiki .mw-parser-output .ambox.mbox-small-left{margin:4px 1em 4px 0;overflow:hidden;width:238px;border-collapse:collapse;font-size:88%;line-height:1.25em}.mw-parser-output .ambox-speedy{border-left:10px solid #b32424;background-color:#fee7e6}.mw-parser-output .ambox-delete{border-left:10px solid #b32424}.mw-parser-output .ambox-content{border-left:10px solid #f28500}.mw-parser-output .ambox-style{border-left:10px solid #fc3}.mw-parser-output .ambox-move{border-left:10px solid #9932cc}.mw-parser-output .ambox-protection{border-left:10px solid #a2a9b1}.mw-parser-output .ambox .mbox-text{border:none;padding:0.25em 0.5em;width:100%}.mw-parser-output .ambox .mbox-image{border:none;padding:2px 0 2px 0.5em;text-align:center}.mw-parser-output .ambox .mbox-imageright{border:none;padding:2px 0.5em 2px 0;text-align:center}.mw-parser-output .ambox .mbox-empty-cell{border:none;padding:0;width:1px}.mw-parser-output .ambox .mbox-image-div{width:52px}@media(min-width:720px){.mw-parser-output .ambox{margin:0 10%}}@media print{body.ns-0 .mw-parser-output .ambox{display:none!important}}

|  |  |
| --- | --- |
| [icon](/wiki/File:Question_book-new.svg) | This section **needs [more citations](/wiki/Wikipedia:Verifiability "Wikipedia:Verifiability")**. Please help [improve this section](/wiki/Special:EditPage/Little%27s_law "Special:EditPage/Little's law") by [adding citations to reliable sources](/wiki/Help:Referencing_for_beginners "Help:Referencing for beginners"). Unsourced material may be challenged and [removed](/wiki/Wikipedia:Verifiability#Burden_of_evidence "Wikipedia:Verifiability"). 

### Finding response time

[[edit](/w/index.php?title=Little%27s_law&veaction=edit&section=3 "Edit section: Finding response time") | [edit source](/w/index.php?title=Little%27s_law&action=edit&section=3 "Edit section's source code: Finding response time")]

Imagine an application that had no easy way to measure [response time](/wiki/Response_time_(technology) "Response time (technology)"). If the mean number in the system and the throughput are known, the average response time can be found using Little’s Law:

:   :   mean response time = mean number in system / mean throughput

For example: A queue depth meter shows an average of nine jobs waiting to be serviced. Add one for the job being serviced, so there is an average of ten jobs in the system. Another meter shows a mean throughput of 50 per second. The mean response time is calculated as 0.2 seconds = 10 / 50 per second.

### Customers in the store

[[edit](/w/index.php?title=Little%27s_law&veaction=edit&section=4 "Edit section: Customers in the store") | [edit source](/w/index.php?title=Little%27s_law&action=edit&section=4 "Edit section's source code: Customers in the store")]

Imagine a small store with a single counter and an area for browsing, where only one person can be at the counter at a time, and no one leaves without buying something. So the system is:

:   :   *entrance → browsing → counter → exit*

If the rate at which people enter the store (called the arrival rate) is the rate at which they exit (called the exit rate), the system is stable. By contrast, an arrival rate exceeding an exit rate would represent an unstable system, where the number of waiting customers in the store would gradually increase towards infinity.

Little's Law tells us that the average number of customers in the store *L*, is the effective arrival rate *λ*, times the average time that a customer spends in the store *W*, or simply:

:   L
    =
    λ
    W
    {\displaystyle L=\lambda W}
    ![{\displaystyle L=\lambda W}](https://wikimedia.org/api/rest_v1/media/math/render/svg/c22b7178f025d29c130d89a539e44724438008e5)

Assume customers arrive at the rate of 10 per hour and stay an average of 0.5 hour. This means we should find the average number of customers in the store at any time to be 5.

:   L
    =
    10
    ×
    0.5
    =
    5
    {\displaystyle L=10\times 0.5=5}
    ![{\displaystyle L=10\times 0.5=5}](https://wikimedia.org/api/rest_v1/media/math/render/svg/4950a8ba8fa9c3875479541fe6270b5c52d3a204)

Now suppose the store is considering doing more advertising to raise the arrival rate to 20 per hour. The store must either be prepared to host an average of 10 occupants or must reduce the time each customer spends in the store to 0.25 hour. The store might achieve the latter by ringing up the bill faster or by adding more counters.

We can apply Little's Law to systems within the store. For example, consider the counter and its queue. Assume we notice that there are on average 2 customers in the queue and at the counter. We know the arrival rate is 10 per hour, so customers must be spending 0.2 hours on average checking out.

:   W
    =

    L
    λ
    =

    2
    10
    =
    0.2
    {\displaystyle W={\frac {L}{\lambda }}={\frac {2}{10}}=0.2}
    ![{\displaystyle W={\frac {L}{\lambda }}={\frac {2}{10}}=0.2}](https://wikimedia.org/api/rest_v1/media/math/render/svg/89ce5f596a77a3944a0940a55a70deaedf0f6a87)

We can even apply Little's Law to the counter itself. The average number of people at the counter would be in the range (0, 1) since no more than one person can be at the counter at a time. In that case, the average number of people at the counter is also known as the utilisation of the counter.

However, because a store in reality generally has a limited amount of space, it can eventually become unstable. If the arrival rate is much greater than the exit rate, the store will eventually start to overflow, and thus any new arriving customers will simply be rejected (and forced to go somewhere else or try again later) until there is once again free space available in the store. This is also the difference between the *arrival rate* and the *effective arrival rate*, where the arrival rate roughly corresponds to the rate at which customers arrive at the store, whereas the effective arrival rate corresponds to the rate at which customers *enter* the store. However, in a system with an infinite size and no loss, the two are equal.

## Estimating parameters

[[edit](/w/index.php?title=Little%27s_law&veaction=edit&section=5 "Edit section: Estimating parameters") | [edit source](/w/index.php?title=Little%27s_law&action=edit&section=5 "Edit section's source code: Estimating parameters")]

To use Little's law on data, formulas must be used to estimate the parameters, as the result does not necessarily directly apply over finite time intervals, due to problems like how to log customers already present at the start of the logging interval and those who have not yet departed when logging stops.[[15]](#cite_note-15)

## Applications

[[edit](/w/index.php?title=Little%27s_law&veaction=edit&section=6 "Edit section: Applications") | [edit source](/w/index.php?title=Little%27s_law&action=edit&section=6 "Edit section's source code: Applications")]

Little's law is widely used in manufacturing to predict lead time based on the production rate and the amount of work-in-process.[[16]](#cite_note-16)

Software-performance testers have used Little's law to ensure that the observed performance results are not due to bottlenecks imposed by the testing apparatus.[[17]](#cite_note-17)[[18]](#cite_note-18)

Other applications include staffing emergency departments in hospitals.[[19]](#cite_note-50aniv-19)[[20]](#cite_note-20)

Lastly, an equivalent version of Little's law also applies in the fields of [demography](/wiki/Demography "Demography") and [population biology](/wiki/Population_biology "Population biology"), although not referred to as "Little's Law".[[21]](#cite_note-21)[[22]](#cite_note-22) For example, Cohen (2008)[[23]](#cite_note-23) explains that in a homogeneous stationary population without migration, 

P
=
B
×
e
{\displaystyle P=B\times e}
![{\displaystyle P=B\times e}](https://wikimedia.org/api/rest_v1/media/math/render/svg/cd57392e53aa46d133168fd8b743a739a367d5d3), where 

P
{\displaystyle P}
![{\displaystyle P}](https://wikimedia.org/api/rest_v1/media/math/render/svg/b4dc73bf40314945ff376bd363916a738548d40a) is the total population size, 

B
{\displaystyle B}
![{\displaystyle B}](https://wikimedia.org/api/rest_v1/media/math/render/svg/47136aad860d145f75f3eed3022df827cee94d7a) is the number of births per year, and 

e
{\displaystyle e}
![{\displaystyle e}](https://wikimedia.org/api/rest_v1/media/math/render/svg/cd253103f0876afc68ebead27a5aa9867d927467) is the life expectancy from birth. The formula 

P
=
B
×
e
{\displaystyle P=B\times e}
![{\displaystyle P=B\times e}](https://wikimedia.org/api/rest_v1/media/math/render/svg/cd57392e53aa46d133168fd8b743a739a367d5d3) is thus directly equivalent to Little's law (

L
=
λ
×
W
{\displaystyle L=\lambda \times W}
![{\displaystyle L=\lambda \times W}](https://wikimedia.org/api/rest_v1/media/math/render/svg/7aec6b848a00a1168000c7d421b2366b1ae64725)). However, biological populations tend to be dynamic and therefore more complicated to model accurately.[[24]](#cite_note-24)

## Distributional form

[[edit](/w/index.php?title=Little%27s_law&veaction=edit&section=7 "Edit section: Distributional form") | [edit source](/w/index.php?title=Little%27s_law&action=edit&section=7 "Edit section's source code: Distributional form")]

In some cases, it is possible not only to relate averages but to relate the entire probability distribution of the number in the system to the time in the system under a [first come, first served](/wiki/First_come,_first_served "First come, first served") discipline. A distributional relation for many FIFO/Poisson-class systems was derived by Keilson and Servi (1988)[[25]](#cite_note-KS88-25) and further developed in related work, including links to the Fuhrmann–Cooper decomposition[[26]](#cite_note-KS90-26); later, Bertsimas and Nakazato (1995) provided a new proof and surveyed applications.[[27]](#cite_note-27)

## See also

[[edit](/w/index.php?title=Little%27s_law&veaction=edit&section=8 "Edit section: See also") | [edit source](/w/index.php?title=Little%27s_law&action=edit&section=8 "Edit section's source code: See also")]

- [List of eponymous laws](/wiki/List_of_eponymous_laws "List of eponymous laws") (laws, adages, and other succinct observations or predictions named after persons)
- [Erlang (unit)](/wiki/Erlang_(unit) "Erlang (unit)")

## References

[[edit](/w/index.php?title=Little%27s_law&veaction=edit&section=9 "Edit section: References") | [edit source](/w/index.php?title=Little%27s_law&action=edit&section=9 "Edit section's source code: References")]

.mw-parser-output .reflist-columns-2{column-width:30em}.mw-parser-output .reflist-columns-3{column-width:25em}body.skin-vector-2022 .mw-parser-output .reflist-columns-2{column-width:27em}body.skin-vector-2022 .mw-parser-output .reflist-columns-3{column-width:22.5em}.mw-parser-output .references[data-mw-group=upper-alpha]{list-style-type:upper-alpha}.mw-parser-output .references[data-mw-group=upper-roman]{list-style-type:upper-roman}.mw-parser-output .references[data-mw-group=lower-alpha]{list-style-type:lower-alpha}.mw-parser-output .references[data-mw-group=lower-greek]{list-style-type:lower-greek}.mw-parser-output .references[data-mw-group=lower-roman]{list-style-type:lower-roman}.mw-parser-output div.reflist-liststyle-upper-alpha .references{list-style-type:upper-alpha}.mw-parser-output div.reflist-liststyle-upper-roman .references{list-style-type:upper-roman}.mw-parser-output div.reflist-liststyle-lower-alpha .references{list-style-type:lower-alpha}.mw-parser-output div.reflist-liststyle-lower-greek .references{list-style-type:lower-greek}.mw-parser-output div.reflist-liststyle-lower-roman .references{list-style-type:lower-roman}

1. **[^](#cite_ref-1)** .mw-parser-output cite.citation{font-style:inherit;word-wrap:break-word}.mw-parser-output .citation q{quotes:"\"""\"""'""'"}.mw-parser-output .citation:target{background-color:rgba(0,127,255,0.133)}.mw-parser-output .id-lock-free.id-lock-free a{background:url("//upload.wikimedia.org/wikipedia/commons/6/65/Lock-green.svg")right 0.1em center/9px no-repeat}.mw-parser-output .id-lock-limited.id-lock-limited a,.mw-parser-output .id-lock-registration.id-lock-registration a{background:url("//upload.wikimedia.org/wikipedia/commons/d/d6/Lock-gray-alt-2.svg")right 0.1em center/9px no-repeat}.mw-parser-output .id-lock-subscription.id-lock-subscription a{background:url("//upload.wikimedia.org/wikipedia/commons/a/aa/Lock-red-alt-2.svg")right 0.1em center/9px no-repeat}.mw-parser-output .cs1-ws-icon a{background:url("//upload.wikimedia.org/wikipedia/commons/4/4c/Wikisource-logo.svg")right 0.1em center/12px no-repeat}body:not(.skin-timeless):not(.skin-minerva) .mw-parser-output .id-lock-free a,body:not(.skin-timeless):not(.skin-minerva) .mw-parser-output .id-lock-limited a,body:not(.skin-timeless):not(.skin-minerva) .mw-parser-output .id-lock-registration a,body:not(.skin-timeless):not(.skin-minerva) .mw-parser-output .id-lock-subscription a,body:not(.skin-timeless):not(.skin-minerva) .mw-parser-output .cs1-ws-icon a{background-size:contain;padding:0 1em 0 0}.mw-parser-output .cs1-code{color:inherit;background:inherit;border:none;padding:inherit}.mw-parser-output .cs1-hidden-error{display:none;color:var(--color-error,#bf3c2c)}.mw-parser-output .cs1-visible-error{color:var(--color-error,#bf3c2c)}.mw-parser-output .cs1-maint{display:none;color:#085;margin-left:0.3em}.mw-parser-output .cs1-kern-left{padding-left:0.2em}.mw-parser-output .cs1-kern-right{padding-right:0.2em}.mw-parser-output .citation .mw-selflink{font-weight:inherit}@media screen{.mw-parser-output .cs1-format{font-size:95%}html.skin-theme-clientpref-night .mw-parser-output .cs1-maint{color:#18911f}}@media screen and (prefers-color-scheme:dark){html.skin-theme-clientpref-os .mw-parser-output .cs1-maint{color:#18911f}}Alberto Leon-Garcia (2008). *Probability, statistics, and random processes for electrical engineering* (3rd ed.). Prentice Hall. [ISBN](/wiki/ISBN_(identifier) "ISBN (identifier)") [978-0-13-147122-1](/wiki/Special:BookSources/978-0-13-147122-1 "Special:BookSources/978-0-13-147122-1").
2. **[^](#cite_ref-allen_2-0)** Allen, Arnold A. (1990). [*Probability, Statistics, and Queueing Theory: With Computer Science Applications*](https://archive.org/details/probabilitystati0000alle/page/259). Gulf Professional Publishing. p. [259](https://archive.org/details/probabilitystati0000alle/page/259). [ISBN](/wiki/ISBN_(identifier) "ISBN (identifier)") [0120510510](/wiki/Special:BookSources/0120510510 "Special:BookSources/0120510510").
3. **[^](#cite_ref-3)** Simchi-Levi, D.; [Trick, M. A.](/wiki/Michael_Trick "Michael Trick") (2013). "Introduction to "Little's Law as Viewed on Its 50th Anniversary"". *Operations Research*. **59** (3): 535. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1287/opre.1110.0941](https://doi.org/10.1287%2Fopre.1110.0941).
4. **[^](#cite_ref-4)** Serfozo, R. (1999). "Little Laws". *Introduction to Stochastic Networks*. pp. 135–154. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1007/978-1-4612-1482-3\_5](https://doi.org/10.1007%2F978-1-4612-1482-3_5). [ISBN](/wiki/ISBN_(identifier) "ISBN (identifier)") [978-1-4612-7160-4](/wiki/Special:BookSources/978-1-4612-7160-4 "Special:BookSources/978-1-4612-7160-4").
5. **[^](#cite_ref-5)** Harchol-Balter, Mor. "Chapter 6: Little's Law and Other Operational Laws". *Performance Modeling and Design of Computer Systems: Queueing Theory in Action*. Cambridge University Press. p. 98.
6. **[^](#cite_ref-6)** [Keilson, J.](/wiki/Julian_Keilson "Julian Keilson"); Servi, L. D. (1988). ["A distributional form of Little's Law"](https://dspace.mit.edu/bitstream/1721.1/47244/1/distributionalfo00keil.pdf) (PDF). *Operations Research Letters*. **7** (5): 223. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1016/0167-6377(88)90035-1](https://doi.org/10.1016%2F0167-6377%2888%2990035-1). [hdl](/wiki/Hdl_(identifier) "Hdl (identifier)"):[1721.1/5305](https://hdl.handle.net/1721.1%2F5305).
7. ^ [***a***](#cite_ref-little-graves_7-0) [***b***](#cite_ref-little-graves_7-1) [Little, J. D. C.](/wiki/John_Little_(academic) "John Little (academic)"); Graves, S. C. (2008). ["Little's Law"](http://web.mit.edu/sgraves/www/papers/Little's%20Law-Published.pdf) (PDF). *Building Intuition*. International Series in Operations Research & Management Science. Vol. 115. p. 81. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1007/978-0-387-73699-0\_5](https://doi.org/10.1007%2F978-0-387-73699-0_5). [ISBN](/wiki/ISBN_(identifier) "ISBN (identifier)") [978-0-387-73698-3](/wiki/Special:BookSources/978-0-387-73698-3 "Special:BookSources/978-0-387-73698-3").
8. **[^](#cite_ref-8)** Cobham, Alan (1954). "Priority Assignment in Waiting Line Problems". *Operations Research*. **2** (1): 70–76. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1287/opre.2.1.70](https://doi.org/10.1287%2Fopre.2.1.70). [JSTOR](/wiki/JSTOR_(identifier) "JSTOR (identifier)") [166539](https://www.jstor.org/stable/166539).
9. **[^](#cite_ref-9)** [Morse, Philip M.](/wiki/Philip_M._Morse "Philip M. Morse") (1958). *Queues, inventories, and maintenance: the analysis of operational system with variable demand and supply*. Wiley. "Those readers who would like to experience for themselves the slipperiness of fundamental concepts in this field and the intractability of really general theorems, might try their hand at showing under what circumstances this simple relationship between L and W does not hold."
10. **[^](#cite_ref-10)** [Little, J. D. C.](/wiki/John_Little_(academic) "John Little (academic)") (1961). "A Proof for the Queuing Formula: *L* = *λW*". *[Operations Research](/wiki/Operations_Research_(journal) "Operations Research (journal)")*. **9** (3): 383–387. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1287/opre.9.3.383](https://doi.org/10.1287%2Fopre.9.3.383). [JSTOR](/wiki/JSTOR_(identifier) "JSTOR (identifier)") [167570](https://www.jstor.org/stable/167570).
11. **[^](#cite_ref-11)** Jewell, William S. (1967). "A Simple Proof of: *L* = *λW*". *Operations Research*. **15** (6): 1109–1116. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1287/opre.15.6.1109](https://doi.org/10.1287%2Fopre.15.6.1109). [JSTOR](/wiki/JSTOR_(identifier) "JSTOR (identifier)") [168616](https://www.jstor.org/stable/168616).
12. **[^](#cite_ref-12)** Eilon, Samuel (1969). ["A Simpler Proof of *L* = *λW*"](https://doi.org/10.1287%2Fopre.17.5.915). *Operations Research*. **17** (5): 915–917. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1287/opre.17.5.915](https://doi.org/10.1287%2Fopre.17.5.915). [JSTOR](/wiki/JSTOR_(identifier) "JSTOR (identifier)") [168368](https://www.jstor.org/stable/168368).
13. **[^](#cite_ref-13)** Stidham Jr., Shaler (1974). ["A Last Word on *L* = *λW*"](https://doi.org/10.1287%2Fopre.22.2.417). *Operations Research*. **22** (2): 417–421. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1287/opre.22.2.417](https://doi.org/10.1287%2Fopre.22.2.417). [JSTOR](/wiki/JSTOR_(identifier) "JSTOR (identifier)") [169601](https://www.jstor.org/stable/169601).
14. **[^](#cite_ref-14)** Stidham Jr., Shaler (1972). "*L* = *λW*: A Discounted Analogue and a New Proof". *Operations Research*. **20** (6): 1115–1120. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1287/opre.20.6.1115](https://doi.org/10.1287%2Fopre.20.6.1115). [JSTOR](/wiki/JSTOR_(identifier) "JSTOR (identifier)") [169301](https://www.jstor.org/stable/169301).
15. **[^](#cite_ref-15)** Kim, S. H.; [Whitt, W.](/wiki/Ward_Whitt "Ward Whitt") (2013). ["Statistical Analysis with Little's Law"](http://www.columbia.edu/~ww2040/LL_OR.pdf) (PDF). *Operations Research*. **61** (4): 1030. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1287/opre.2013.1193](https://doi.org/10.1287%2Fopre.2013.1193).
16. **[^](#cite_ref-16)** Correll, Nikolaus (June 13, 2021). ["Manufacturing Lead Time"](https://thesevendeadlywastes.com/lesson/lead-time/). Retrieved June 12, 2021.
17. **[^](#cite_ref-17)** [Software Infrastructure Bottlenecks in J2EE by Deepak Goel](http://www.onjava.com/pub/a/onjava/2005/01/19/j2ee-bottlenecks.html)
18. **[^](#cite_ref-18)** [Benchmarking Blunders and Things That Go Bump in the Night by Neil Gunther](https://arxiv.org/abs/cs/0404043)
19. **[^](#cite_ref-50aniv_19-0)** [Little, J. D. C.](/wiki/John_Little_(academic) "John Little (academic)") (2011). ["Little's Law as Viewed on Its 50th Anniversary"](http://www.informs.org/content/download/255808/2414681/file/little_paper.pdf) (PDF). *Operations Research*. **59** (3): 536–549. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1287/opre.1110.0940](https://doi.org/10.1287%2Fopre.1110.0940). [JSTOR](/wiki/JSTOR_(identifier) "JSTOR (identifier)") [23013126](https://www.jstor.org/stable/23013126).
20. **[^](#cite_ref-20)** Harris, Mark (February 22, 2010). ["Little's Law: The Science Behind Proper Staffing"](https://web.archive.org/web/20120905100132/http://www.epmonthly.com/subspecialties/management/littles-law-the-science-behind-proper-staffing/). Emergency Physicians Monthly. Archived from [the original](https://www.epmonthly.com/subspecialties/management/littles-law-the-science-behind-proper-staffing/) on September 5, 2012. Retrieved September 4, 2012.
21. **[^](#cite_ref-21)** Liang, Haili; Guo, Zhen; Tuljapurkar, Shripad (2023). ["Why life expectancy over-predicts crude death rate"](https://doi.org/10.1186%2Fs41118-023-00188-8). *Genus*. **79** (1): 9. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1186/s41118-023-00188-8](https://doi.org/10.1186%2Fs41118-023-00188-8). [ISSN](/wiki/ISSN_(identifier) "ISSN (identifier)") [2035-5556](https://search.worldcat.org/issn/2035-5556).
22. **[^](#cite_ref-22)** Murray, Bertram G. (2003). ["A new equation relating population size and demographic parameters: some ecological implications"](https://www.jstor.org/stable/23736503). *Annales Zoologici Fennici*. **40** (6): 465–472. [ISSN](/wiki/ISSN_(identifier) "ISSN (identifier)") [0003-455X](https://search.worldcat.org/issn/0003-455X). [JSTOR](/wiki/JSTOR_(identifier) "JSTOR (identifier)") [23736503](https://www.jstor.org/stable/23736503).
23. **[^](#cite_ref-23)** Cohen, Joel E. (2008). ["Constant global population with demographic heterogeneity"](https://www.demographic-research.org/articles/volume/18/14). *Demographic Research*. **18**: 409–436. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.4054/DemRes.2008.18.14](https://doi.org/10.4054%2FDemRes.2008.18.14). [ISSN](/wiki/ISSN_(identifier) "ISSN (identifier)") [1435-9871](https://search.worldcat.org/issn/1435-9871).
24. **[^](#cite_ref-24)** Caswell, Hal (2006). [*Matrix population models: construction, analysis, and interpretation*](https://global.oup.com/academic/product/matrix-population-models-9780878931217) (Second ed.). Sunderland, Massachusetts: Sinauer Associates, Inc. Publishers. [ISBN](/wiki/ISBN_(identifier) "ISBN (identifier)") [978-0-87893-121-7](/wiki/Special:BookSources/978-0-87893-121-7 "Special:BookSources/978-0-87893-121-7").
25. **[^](#cite_ref-KS88_25-0)** Keilson, Julian; Servi, Leslie D. (1988). "A distributional form of Little's law". *Operations Research Letters*. **7** (5): 223–227. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1016/0167-6377(88)90035-1](https://doi.org/10.1016%2F0167-6377%2888%2990035-1). [hdl](/wiki/Hdl_(identifier) "Hdl (identifier)"):[1721.1/47244](https://hdl.handle.net/1721.1%2F47244).
26. **[^](#cite_ref-KS90_26-0)** Keilson, Julian; Servi, Leslie D. (1990). "The distributional form of Little's law and the Fuhrmann-Cooper decomposition". *Operations Research Letters*. **9** (4): 239–247. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1016/0167-6377(90)90068-G](https://doi.org/10.1016%2F0167-6377%2890%2990068-G). [hdl](/wiki/Hdl_(identifier) "Hdl (identifier)"):[1721.1/47195](https://hdl.handle.net/1721.1%2F47195).
27. **[^](#cite_ref-27)** Bertsimas, D.; Nakazato, D. (1995). ["The Distributional Little's Law and Its Applications"](http://web.mit.edu/dbertsim/www/papers/Queuing%20Theory/The%20distributional%20Little's%20law%20and%20its%20applications.pdf) (PDF). *[Operations Research](/wiki/Operations_Research_(journal) "Operations Research (journal)")*. **43** (2): 298. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1287/opre.43.2.298](https://doi.org/10.1287%2Fopre.43.2.298). [JSTOR](/wiki/JSTOR_(identifier) "JSTOR (identifier)") [171838](https://www.jstor.org/stable/171838).

## External links

[[edit](/w/index.php?title=Little%27s_law&veaction=edit&section=10 "Edit section: External links") | [edit source](/w/index.php?title=Little%27s_law&action=edit&section=10 "Edit section's source code: External links")]

- *[A Proof of the Queueing Formula L = λ W](http://www.columbia.edu/~ks20/stochastic-I/stochastic-I-LL.pdf)*, Sigman, K., Columbia University
- *[A Proof of the Queueing Formula L = λ W](http://www.columbia.edu/~ks20/stochastic-I/stochastic-I-LL.pdf)*, Eduardo, Maldonado., Alexby usm

.mw-parser-output .hlist dl,.mw-parser-output .hlist ol,.mw-parser-output .hlist ul{margin:0;padding:0}.mw-parser-output .hlist dd,.mw-parser-output .hlist dt,.mw-parser-output .hlist li{margin:0;display:inline}.mw-parser-output .hlist.inline,.mw-parser-output .hlist.inline dl,.mw-parser-output .hlist.inline ol,.mw-parser-output .hlist.inline ul,.mw-parser-output .hlist dl dl,.mw-parser-output .hlist dl ol,.mw-parser-output .hlist dl ul,.mw-parser-output .hlist ol dl,.mw-parser-output .hlist ol ol,.mw-parser-output .hlist ol ul,.mw-parser-output .hlist ul dl,.mw-parser-output .hlist ul ol,.mw-parser-output .hlist ul ul{display:inline}.mw-parser-output .hlist .mw-empty-li{display:none}.mw-parser-output .hlist dt::after{content:": "}.mw-parser-output .hlist dd::after,.mw-parser-output .hlist li::after{content:"\a0 · ";font-weight:bold}.mw-parser-output .hlist dd:last-child::after,.mw-parser-output .hlist dt:last-child::after,.mw-parser-output .hlist li:last-child::after{content:none}.mw-parser-output .hlist dd dd:first-child::before,.mw-parser-output .hlist dd dt:first-child::before,.mw-parser-output .hlist dd li:first-child::before,.mw-parser-output .hlist dt dd:first-child::before,.mw-parser-output .hlist dt dt:first-child::before,.mw-parser-output .hlist dt li:first-child::before,.mw-parser-output .hlist li dd:first-child::before,.mw-parser-output .hlist li dt:first-child::before,.mw-parser-output .hlist li li:first-child::before{content:" (";font-weight:normal}.mw-parser-output .hlist dd dd:last-child::after,.mw-parser-output .hlist dd dt:last-child::after,.mw-parser-output .hlist dd li:last-child::after,.mw-parser-output .hlist dt dd:last-child::after,.mw-parser-output .hlist dt dt:last-child::after,.mw-parser-output .hlist dt li:last-child::after,.mw-parser-output .hlist li dd:last-child::after,.mw-parser-output .hlist li dt:last-child::after,.mw-parser-output .hlist li li:last-child::after{content:")";font-weight:normal}.mw-parser-output .hlist ol{counter-reset:listitem}.mw-parser-output .hlist ol>li{counter-increment:listitem}.mw-parser-output .hlist ol>li::before{content:" "counter(listitem)"\a0 "}.mw-parser-output .hlist dd ol>li:first-child::before,.mw-parser-output .hlist dt ol>li:first-child::before,.mw-parser-output .hlist li ol>li:first-child::before{content:" ("counter(listitem)"\a0 "}.mw-parser-output .navbox{box-sizing:border-box;border:1px solid #a2a9b1;width:100%;clear:both;font-size:88%;text-align:center;padding:1px;margin:1em auto 0}.mw-parser-output .navbox .navbox{margin-top:0}.mw-parser-output .navbox+.navbox-styles+.navbox,.mw-parser-output .navbox+span.mw-empty-elt+.navbox-styles+.navbox{margin-top:-1px}.mw-parser-output .navbox-inner,.mw-parser-output .navbox-subgroup{width:100%}.mw-parser-output .navbox-group,.mw-parser-output .navbox-title,.mw-parser-output .navbox-abovebelow{padding:0.25em 1em;line-height:1.5em;text-align:center}.mw-parser-output .navbox-group{white-space:nowrap;text-align:right}.mw-parser-output .navbox,.mw-parser-output .navbox-subgroup{background-color:#fdfdfd;color:inherit}.mw-parser-output .navbox-list{line-height:1.5em;border-color:#fdfdfd}.mw-parser-output .navbox-list-with-group{text-align:left;border-left-width:2px;border-left-style:solid}.mw-parser-output tr+tr>.navbox-abovebelow,.mw-parser-output tr+tr>.navbox-group,.mw-parser-output tr+tr>.navbox-image,.mw-parser-output tr+tr>.navbox-list{border-top:2px solid #fdfdfd}.mw-parser-output .navbox-title{background-color:#ccf;color:inherit}.mw-parser-output .navbox-abovebelow,.mw-parser-output .navbox-group,.mw-parser-output .navbox-subgroup .navbox-title{background-color:#ddf;color:inherit}.mw-parser-output .navbox-subgroup .navbox-group,.mw-parser-output .navbox-subgroup .navbox-abovebelow{background-color:#e6e6ff;color:inherit}.mw-parser-output .navbox-even{background-color:#f7f7f7;color:inherit}.mw-parser-output .navbox-odd{background-color:transparent;color:inherit}.mw-parser-output .navbox .hlist td dl,.mw-parser-output .navbox .hlist td ol,.mw-parser-output .navbox .hlist td ul,.mw-parser-output .navbox td.hlist dl,.mw-parser-output .navbox td.hlist ol,.mw-parser-output .navbox td.hlist ul{padding:0.125em 0}.mw-parser-output .navbox .navbar{display:block;font-size:100%}.mw-parser-output .navbox-title .navbar{float:left;text-align:left;margin-right:0.5em}body.skin--responsive .mw-parser-output .navbox-image img{max-width:none!important}@media print{body.ns-0 .mw-parser-output .navbox{display:none!important}}

| .mw-parser-output .navbar{display:inline;font-size:88%;font-weight:normal}.mw-parser-output .navbar-collapse{float:left;text-align:left}.mw-parser-output .navbar-boxtext{word-spacing:0}.mw-parser-output .navbar ul{display:inline-block;white-space:nowrap;line-height:inherit}.mw-parser-output .navbar-brackets::before{margin-right:-0.125em;content:"[ "}.mw-parser-output .navbar-brackets::after{margin-left:-0.125em;content:" ]"}.mw-parser-output .navbar li{word-spacing:-0.125em}.mw-parser-output .navbar a>span,.mw-parser-output .navbar a>abbr{text-decoration:inherit}.mw-parser-output .navbar-mini abbr{font-variant:small-caps;border-bottom:none;text-decoration:none;cursor:inherit}.mw-parser-output .navbar-ct-full{font-size:114%;margin:0 7em}.mw-parser-output .navbar-ct-mini{font-size:114%;margin:0 4em}html.skin-theme-clientpref-night .mw-parser-output .navbar li a abbr{color:var(--color-base)!important}@media(prefers-color-scheme:dark){html.skin-theme-clientpref-os .mw-parser-output .navbar li a abbr{color:var(--color-base)!important}}@media print{.mw-parser-output .navbar{display:none!important}} - [v](/wiki/Template:Queueing_theory "Template:Queueing theory") - [t](/wiki/Template_talk:Queueing_theory "Template talk:Queueing theory") - [e](/wiki/Special:EditPage/Template:Queueing_theory "Special:EditPage/Template:Queueing theory")  [Queueing theory](/wiki/Queueing_theory "Queueing theory") | |
| --- | --- |
| Single queueing nodes | - [D/M/1 queue](/wiki/D/M/1_queue "D/M/1 queue") - [M/D/1 queue](/wiki/M/D/1_queue "M/D/1 queue") - [M/D/c queue](/wiki/M/D/c_queue "M/D/c queue") - [M/M/1 queue](/wiki/M/M/1_queue "M/M/1 queue")   - [Burke's theorem](/wiki/Burke%27s_theorem "Burke's theorem") - [M/M/c queue](/wiki/M/M/c_queue "M/M/c queue") - [M/M/∞ queue](/wiki/M/M/%E2%88%9E_queue "M/M/∞ queue") - [M/G/1 queue](/wiki/M/G/1_queue "M/G/1 queue")   - [Pollaczek–Khinchine formula](/wiki/Pollaczek%E2%80%93Khinchine_formula "Pollaczek–Khinchine formula")   - [Matrix analytic method](/wiki/Matrix_analytic_method "Matrix analytic method") - [M/G/k queue](/wiki/M/G/k_queue "M/G/k queue") - [G/M/1 queue](/wiki/G/M/1_queue "G/M/1 queue") - [G/G/1 queue](/wiki/G/G/1_queue "G/G/1 queue")   - [Kingman's formula](/wiki/Kingman%27s_formula "Kingman's formula")   - [Lindley equation](/wiki/Lindley_equation "Lindley equation") - [Fork–join queue](/wiki/Fork%E2%80%93join_queue "Fork–join queue") - [Bulk queue](/wiki/Bulk_queue "Bulk queue") |
| Arrival processes | - [Poisson point process](/wiki/Poisson_point_process "Poisson point process") - [Markovian arrival process](/wiki/Markovian_arrival_process "Markovian arrival process") - [Rational arrival process](/wiki/Rational_arrival_process "Rational arrival process") |
| Queueing networks | - [Jackson network](/wiki/Jackson_network "Jackson network")   - [Traffic equations](/wiki/Traffic_equations "Traffic equations") - [Gordon–Newell theorem](/wiki/Gordon%E2%80%93Newell_theorem "Gordon–Newell theorem")   - [Mean value analysis](/wiki/Mean_value_analysis "Mean value analysis")   - [Buzen's algorithm](/wiki/Buzen%27s_algorithm "Buzen's algorithm") - [Kelly network](/wiki/Kelly_network "Kelly network") - [G-network](/wiki/G-network "G-network") - [BCMP network](/wiki/BCMP_network "BCMP network") |
| Service policies | - [FIFO](/wiki/FIFO_(computing_and_electronics) "FIFO (computing and electronics)") - [LIFO](/wiki/LIFO_(computing) "LIFO (computing)") - [Processor sharing](/wiki/Processor_sharing "Processor sharing") - [Round-robin](/wiki/Round-robin_scheduling "Round-robin scheduling") - [Shortest job next](/wiki/Shortest_job_next "Shortest job next") - [Shortest remaining time](/wiki/Shortest_remaining_time "Shortest remaining time") |
| Key concepts | - [Continuous-time Markov chain](/wiki/Continuous-time_Markov_chain "Continuous-time Markov chain") - [Kendall's notation](/wiki/Kendall%27s_notation "Kendall's notation") - Little's law - [Product-form solution](/wiki/Product-form_solution "Product-form solution")   - [Balance equation](/wiki/Balance_equation "Balance equation")   - [Quasireversibility](/wiki/Quasireversibility "Quasireversibility")   - [Flow-equivalent server method](/wiki/Flow-equivalent_server_method "Flow-equivalent server method") - [Arrival theorem](/wiki/Arrival_theorem "Arrival theorem") - [Decomposition method](/wiki/Decomposition_method_(queueing_theory) "Decomposition method (queueing theory)") - [Beneš method](/wiki/Bene%C5%A1_method "Beneš method") |
| Limit theorems | - [Fluid limit](/wiki/Fluid_limit "Fluid limit") - [Mean-field theory](/wiki/Mean-field_theory "Mean-field theory") - [Heavy traffic approximation](/wiki/Heavy_traffic_approximation "Heavy traffic approximation")   - [Reflected Brownian motion](/wiki/Reflected_Brownian_motion "Reflected Brownian motion") |
| Extensions | - [Fluid queue](/wiki/Fluid_queue "Fluid queue") - [Layered queueing network](/wiki/Layered_queueing_network "Layered queueing network") - [Polling system](/wiki/Polling_system "Polling system") - [Adversarial queueing network](/wiki/Adversarial_queueing_network "Adversarial queueing network") - [Loss network](/wiki/Loss_network "Loss network") - [Retrial queue](/wiki/Retrial_queue "Retrial queue") |
| [Information systems](/wiki/Information_system "Information system") | - [Data buffer](/wiki/Data_buffer "Data buffer") - [Erlang (unit)](/wiki/Erlang_(unit) "Erlang (unit)") - [Erlang distribution](/wiki/Erlang_distribution "Erlang distribution") - [Flow control (data)](/wiki/Flow_control_(data) "Flow control (data)") - [Message queue](/wiki/Message_queue "Message queue") - [Network congestion](/wiki/Network_congestion "Network congestion") - [Network scheduler](/wiki/Network_scheduler "Network scheduler") - [Pipeline (software)](/wiki/Pipeline_(software) "Pipeline (software)") - [Quality of service](/wiki/Quality_of_service "Quality of service") - [Scheduling (computing)](/wiki/Scheduling_(computing) "Scheduling (computing)") - [Teletraffic engineering](/wiki/Teletraffic_engineering "Teletraffic engineering") |
| [Category](/wiki/Category:Queueing_theory "Category:Queueing theory") | |
