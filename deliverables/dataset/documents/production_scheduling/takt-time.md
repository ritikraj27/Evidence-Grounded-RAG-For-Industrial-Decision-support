<!-- category: production_scheduling -->
# Takt time

Manufacturing term

.mw-parser-output .hatnote{font-style:italic}.mw-parser-output div.hatnote{padding-left:1.6em;margin-bottom:0.5em}.mw-parser-output .hatnote i{font-style:normal}.mw-parser-output .hatnote+.mw-empty-elt+.hatnote{margin-top:-0.5em}@media print{body.ns-0 .mw-parser-output .hatnote{display:none!important}}

"Takt" redirects here. For the chamber ensemble in [Arab music](/wiki/Arab_music "Arab music"), see [Takht (music)](/wiki/Takht_(music) "Takht (music)"). For other uses of "takht", see [Takht](/wiki/Takht_(disambiguation) "Takht (disambiguation)").

**Takt time**, or simply **takt**, is a manufacturing term to describe the required product assembly duration that is needed to match the demand. Often confused with [cycle time](/wiki/Cycle_time_(software) "Cycle time (software)"), takt time is a tool used to design work and it measures the average time interval between the start of production of one unit and the start of production of the next unit when items are produced sequentially. For calculations, it is the time to produce parts divided by the number of parts demanded in that time interval.[[1]](#cite_note-1) The takt time is based on customer demand; if a process or a production line are unable to produce at takt time, either demand leveling, additional resources, or process re-engineering is needed to ensure on-time delivery.

For example, if the customer demand is 10 units per week, then, given a 40-hour workweek and steady flow through the production line, the average duration between production starts should be 4 hours, ideally. This interval is further reduced to account for things like machine downtime and scheduled employee breaks.

## Etymology

[[edit](/w/index.php?title=Takt_time&veaction=edit&section=1 "Edit section: Etymology") | [edit source](/w/index.php?title=Takt_time&action=edit&section=1 "Edit section's source code: Etymology")]

Takt time is a borrowing of the [Japanese word](/wiki/Wasei-eigo "Wasei-eigo") *takuto taimu* (タクトタイム), which in turn was borrowed from the German word **Taktzeit**, meaning 'cycle time'. The word was likely introduced to Japan by German engineers in the 1930s.[[2]](#cite_note-2)

The word originates from the Latin word "tactus" meaning "touch, sense of touch, feeling".[[3]](#cite_note-:0-3) Some earlier meanings include: (16th century) "beat triggered by regular contact, clock beat", then in music "beat indicating the rhythm" and (18th century) "regular unit of note values".[[4]](#cite_note-4)

## History

[[edit](/w/index.php?title=Takt_time&veaction=edit&section=2 "Edit section: History") | [edit source](/w/index.php?title=Takt_time&action=edit&section=2 "Edit section's source code: History")]

Takt time has played an important role in production systems even before the [industrial revolution](/wiki/Industrial_Revolution "Industrial Revolution"). From 16th-century [shipbuilding](/wiki/Shipbuilding "Shipbuilding") in [Venice](/wiki/Venice "Venice"), [mass-production](/wiki/Mass_production "Mass production") of [Model T](/wiki/Ford_Model_T "Ford Model T") by [Henry Ford](/wiki/Henry_Ford "Henry Ford"), synchronizing airframe movement in the German aviation industry and many more. Cooperation between the German aviation industry and [Mitsubishi](/wiki/Mitsubishi "Mitsubishi") brought takt to Japan, where [Toyota](/wiki/Toyota "Toyota") incorporated it in the [Toyota Production System](/wiki/Toyota_Production_System "Toyota Production System") (TPS).[[3]](#cite_note-:0-3)

[James P. Womack](/wiki/James_P._Womack "James P. Womack") and [Daniel T. Jones](/wiki/Daniel_T._Jones_(author) "Daniel T. Jones (author)") in *[The Machine That Changed the World](/wiki/The_Machine_That_Changed_the_World_(book) "The Machine That Changed the World (book)")* (1990)[[5]](#cite_note-5) and *[Lean Thinking](/wiki/Lean_thinking "Lean thinking")* (1996)[[6]](#cite_note-6) introduced the world to the concept of "[lean](/wiki/Lean_manufacturing "Lean manufacturing")". Through this, Takt was connected to lean systems. In the Toyota Production System (TPS), takt time is a central element of the [just-in-time](/wiki/Just-in-time_manufacturing "Just-in-time manufacturing") pillar (JIT) of this production system.

## Definition

[[edit](/w/index.php?title=Takt_time&veaction=edit&section=3 "Edit section: Definition") | [edit source](/w/index.php?title=Takt_time&action=edit&section=3 "Edit section's source code: Definition")]

Assuming a product is made one unit at a time at a constant rate during the net available work time, the takt time is the amount of time that must elapse between two consecutive unit completions in order to meet the demand.

Takt time can be first determined with the formula:[[7]](#cite_note-7)

:   T
    =

    T

    a
    D
    {\displaystyle T={\frac {T\_{a}}{D}}}
    ![{\displaystyle T={\frac {T_{a}}{D}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/ce3cc24ced060081908738a281dfd3aa9d1c5783)

Where  
T   = Takt time (or takt), e.g. [work time between two consecutive units]  
Ta = Net time available to work during the period, e.g. [work time per period]  
D = Demand (customer demand) during the period, e.g. [units required per period]

Net available time is the amount of time available for work to be done. This excludes [break times](/wiki/Break_(work) "Break (work)") and any expected stoppage time (for example [scheduled maintenance](/wiki/Scheduled_maintenance "Scheduled maintenance"), team briefings, etc.).

> **Example**:  
> If there are a total of 8 hours (or 480 minutes) in a shift (gross time) less 30 minutes lunch, 30 minutes for breaks (2 × 15 mins), 10 minutes for a team briefing and 10 minutes for basic maintenance checks, then the net *Available Time to Work* = 480 - 30 - 30 - 10 - 10 = 400 minutes.
>
> If customer demand were 400 units a day and one shift was being run, then the line would be required to output at a minimum rate of one part per minute in order to be able to keep up with customer demand.

Takt time may be adjusted according to requirements within a company. For example, if one department delivers parts to several manufacturing lines, it often makes sense to use similar takt times on all lines to smooth outflow from the preceding station. Customer demand can still be met by adjusting daily working time, reducing [down times](/wiki/Down_time "Down time") on machines, and so on.

## Implementation

[[edit](/w/index.php?title=Takt_time&veaction=edit&section=4 "Edit section: Implementation") | [edit source](/w/index.php?title=Takt_time&action=edit&section=4 "Edit section's source code: Implementation")]

Takt time is common in production lines that move a product along a line of stations that each performs a set of predefined tasks.

- Manufacturing: [casting](/wiki/Casting "Casting") of parts, drilling holes, or preparing a workplace for another task
- Control tasks: testing of parts or adjusting machinery
- Administration: answering standard inquiries or [call center](/wiki/Call_center "Call center") operation
- [Construction Management](/wiki/Construction_management "Construction management"): scheduling process steps within a phase of the project

## Takt in construction

[[edit](/w/index.php?title=Takt_time&veaction=edit&section=5 "Edit section: Takt in construction") | [edit source](/w/index.php?title=Takt_time&action=edit&section=5 "Edit section's source code: Takt in construction")]

With the adoption of [lean thinking in the construction industry](/wiki/Lean_construction "Lean construction"), takt time has found its way into the project-based production systems of the industry. Starting with construction methods that have highly repetitive products like bridge construction, tunnel construction, and repetitive buildings like hotels and residential high-rises, implementation of takt is increasing.[[3]](#cite_note-:0-3)

According to Koskela (1992), an ideal production system has continuous flow and creates value for the customer while transforming raw materials into products.[[8]](#cite_note-8) Construction projects use [critical path method](/wiki/Critical_path_method "Critical path method") (CPM) or [program evaluation and review technique](/wiki/Program_evaluation_and_review_technique "Program evaluation and review technique") (PERT) for planning and scheduling. These methods do not generate flow in the production and tend to be vulnerable to variation in the system. Due to common cost and schedule overruns, industry professionals and academia have started to regard CPM and PERT as outdated methods that often fail to anticipate uncertainties and allocate resources accurately and optimally in a dynamic construction environment.[[9]](#cite_note-9) This has led to increasing developments and implementation of takt.

### Space scheduling

[[edit](/w/index.php?title=Takt_time&veaction=edit&section=6 "Edit section: Space scheduling") | [edit source](/w/index.php?title=Takt_time&action=edit&section=6 "Edit section's source code: Space scheduling")]

Takt, as used in takt planning or takt-time planning (TTP) for construction, is considered one of the several ways of planning and scheduling construction projects based on their utilization of space rather than just time, as done traditionally in the critical path method. Also, to visualize and create flow of work on a construction site, utilization of space becomes essential.[[10]](#cite_note-10) Some other space scheduling methods include:

- [Linear scheduling method](/wiki/Linear_scheduling_method "Linear scheduling method") (LSM) and vertical production method (VPM) which are used to schedule horizontal and vertical repetitive projects respectively,
- Line-of-balance (LOB) method used for any type of repetitive projects.[[11]](#cite_note-11)[[12]](#cite_note-12)
- Location-based management system (LBMS) uses flowlines with the production rates of the crews, as they move through locations with an objective of optimizing work continuity.[[13]](#cite_note-13)

### Comparison with manufacturing

[[edit](/w/index.php?title=Takt_time&veaction=edit&section=7 "Edit section: Comparison with manufacturing") | [edit source](/w/index.php?title=Takt_time&action=edit&section=7 "Edit section's source code: Comparison with manufacturing")]

In manufacturing, the product being built keeps moving on the [assembly line](/wiki/Assembly_line "Assembly line"), while the workstations are stationary. On contrary, construction product, i.e. the building or infrastructure facilities being constructed, is stationary and the workers move from one location to another.[[14]](#cite_note-14)

Takt planning needs an accurate definition of work at each workstation, which in construction is done through defining spaces, called "zones". Due to the non-repetitive distribution of work in construction, achieving work completion within the defined takt for each zone, becomes difficult. Capacity buffer is used to deal with this variability in the system.[[15]](#cite_note-15)

The rationale behind defining these zones and setting the takt is not standardized and varies as per the style of the planner. Work density method (WDM) is one of the methods being used to assist in this process. **Work density** is expressed as a unit of time per unit of area. For a certain work area, work density describes how much time a trade will require to do their work in that area (zone), based on:[[16]](#cite_note-16)

1. the product's design, i.e., what is in the construction project drawings and specifications
2. the scope of the trade's work,
3. the specific task in their schedule (depending on work already in place and work that will follow later in the same or another process),
4. the means and methods the trade will use (e.g., when prefabricating off-site, the work density on-site is expected to decrease),
5. while accounting for crew capabilities and size.

## Benefits of takt time

[[edit](/w/index.php?title=Takt_time&veaction=edit&section=8 "Edit section: Benefits of takt time") | [edit source](/w/index.php?title=Takt_time&action=edit&section=8 "Edit section's source code: Benefits of takt time")]

Once a takt system is implemented there are a number of benefits:

- The product moves along a line, so [bottlenecks](/wiki/Bottleneck_(project_management) "Bottleneck (project management)") (stations that need more time than planned) are easily identified when the product does not move on in time.
- Correspondingly, stations that don't operate reliably (suffer a frequent breakdown, etc.) are easily identified.
- The takt leaves only a certain amount of time to perform the actual [value added](/wiki/Value_added "Value added") work. Therefore, there is a strong motivation to get rid of all non-value-adding tasks (like machine set-up, gathering of tools, transporting products, etc.)
- Workers and machines perform sets of similar tasks, so they don't have to adapt to new processes every day, increasing their productivity.
- There is no place in the takt system for removal of a product from the assembly line at any point before completion, so opportunities for [shrink](/wiki/Shrinkage_(accounting) "Shrinkage (accounting)") and damage in transit are minimized.

## Problems of takt time

[[edit](/w/index.php?title=Takt_time&veaction=edit&section=9 "Edit section: Problems of takt time") | [edit source](/w/index.php?title=Takt_time&action=edit&section=9 "Edit section's source code: Problems of takt time")]

Once a takt system is implemented there are a number of problems:

- When customer demand rises so much that takt time has to come down, quite a few tasks have to be either reorganized to take even less time to fit into the shorter takt time, or they have to be split up between two stations (which means another station has to be squeezed into the line and workers have to adapt to the new setup)
- When one station in the line breaks down for whatever reason the whole line comes to a grinding halt, unless there are buffer capacities for preceding stations to get rid of their products and following stations to feed from. A built-in buffer of three to five percent downtime allows needed adjustments or recovery from failures.[[17]](#cite_note-17)
- Short takt time can put considerable stress on the "moving parts" of a production system or subsystem. In automated systems/subsystems, increased [mechanical stress](/wiki/Stress_(mechanics) "Stress (mechanics)") increases the likelihood of a breakdown, and in non-automated systems/subsystems, personnel face both increased physical stress (which increases the risk of [repetitive motion](/wiki/Repetitive_motion_injury "Repetitive motion injury") (also "stress" or "strain") [injury](/wiki/Repetitive_motion_injury "Repetitive motion injury")), intensified emotional stress, and lowered [motivation](/wiki/Motivation "Motivation"), sometimes to the point of increased [absenteeism](/wiki/Absenteeism "Absenteeism").
- Tasks have to be [leveled](/wiki/Production_leveling "Production leveling") to make sure tasks don't bulk in front of certain stations due to peaks in workload. This decreases the flexibility of the system as a whole.
- The concept of takt time doesn't account for human factors such as an operator needing an unexpected bathroom break or a brief rest period between units (especially for processes involving significant physical labor). In practice, this means that the production processes must be realistically capable of operation above peak takt and demand must be leveled in order to avoid wasted line capacity

## See also

[[edit](/w/index.php?title=Takt_time&veaction=edit&section=10 "Edit section: See also") | [edit source](/w/index.php?title=Takt_time&action=edit&section=10 "Edit section's source code: See also")]

- [Turnaround time](/wiki/Turnaround_time "Turnaround time")
- [Lean manufacturing](/wiki/Lean_manufacturing "Lean manufacturing")
- [Toyota Production System](/wiki/Toyota_Production_System "Toyota Production System")
- [Muri](/wiki/Muri_(Japanese_term) "Muri (Japanese term)")
- [Lean construction](/wiki/Lean_construction "Lean construction")
- *[Factory Physics](/wiki/Factory_Physics "Factory Physics")*, a book on manufacturing management
- [Clock-face scheduling](/wiki/Clock-face_scheduling "Clock-face scheduling"), sometimes referred to as *Taktplan*

## References

[[edit](/w/index.php?title=Takt_time&veaction=edit&section=11 "Edit section: References") | [edit source](/w/index.php?title=Takt_time&action=edit&section=11 "Edit section's source code: References")]

.mw-parser-output .reflist-columns-2{column-width:30em}.mw-parser-output .reflist-columns-3{column-width:25em}body.skin-vector-2022 .mw-parser-output .reflist-columns-2{column-width:27em}body.skin-vector-2022 .mw-parser-output .reflist-columns-3{column-width:22.5em}.mw-parser-output .references[data-mw-group=upper-alpha]{list-style-type:upper-alpha}.mw-parser-output .references[data-mw-group=upper-roman]{list-style-type:upper-roman}.mw-parser-output .references[data-mw-group=lower-alpha]{list-style-type:lower-alpha}.mw-parser-output .references[data-mw-group=lower-greek]{list-style-type:lower-greek}.mw-parser-output .references[data-mw-group=lower-roman]{list-style-type:lower-roman}.mw-parser-output div.reflist-liststyle-upper-alpha .references{list-style-type:upper-alpha}.mw-parser-output div.reflist-liststyle-upper-roman .references{list-style-type:upper-roman}.mw-parser-output div.reflist-liststyle-lower-alpha .references{list-style-type:lower-alpha}.mw-parser-output div.reflist-liststyle-lower-greek .references{list-style-type:lower-greek}.mw-parser-output div.reflist-liststyle-lower-roman .references{list-style-type:lower-roman}

1. **[^](#cite_ref-1)** .mw-parser-output cite.citation{font-style:inherit;word-wrap:break-word}.mw-parser-output .citation q{quotes:"\"""\"""'""'"}.mw-parser-output .citation:target{background-color:rgba(0,127,255,0.133)}.mw-parser-output .id-lock-free.id-lock-free a{background:url("//upload.wikimedia.org/wikipedia/commons/6/65/Lock-green.svg")right 0.1em center/9px no-repeat}.mw-parser-output .id-lock-limited.id-lock-limited a,.mw-parser-output .id-lock-registration.id-lock-registration a{background:url("//upload.wikimedia.org/wikipedia/commons/d/d6/Lock-gray-alt-2.svg")right 0.1em center/9px no-repeat}.mw-parser-output .id-lock-subscription.id-lock-subscription a{background:url("//upload.wikimedia.org/wikipedia/commons/a/aa/Lock-red-alt-2.svg")right 0.1em center/9px no-repeat}.mw-parser-output .cs1-ws-icon a{background:url("//upload.wikimedia.org/wikipedia/commons/4/4c/Wikisource-logo.svg")right 0.1em center/12px no-repeat}body:not(.skin-timeless):not(.skin-minerva) .mw-parser-output .id-lock-free a,body:not(.skin-timeless):not(.skin-minerva) .mw-parser-output .id-lock-limited a,body:not(.skin-timeless):not(.skin-minerva) .mw-parser-output .id-lock-registration a,body:not(.skin-timeless):not(.skin-minerva) .mw-parser-output .id-lock-subscription a,body:not(.skin-timeless):not(.skin-minerva) .mw-parser-output .cs1-ws-icon a{background-size:contain;padding:0 1em 0 0}.mw-parser-output .cs1-code{color:inherit;background:inherit;border:none;padding:inherit}.mw-parser-output .cs1-hidden-error{display:none;color:var(--color-error,#bf3c2c)}.mw-parser-output .cs1-visible-error{color:var(--color-error,#bf3c2c)}.mw-parser-output .cs1-maint{display:none;color:#085;margin-left:0.3em}.mw-parser-output .cs1-kern-left{padding-left:0.2em}.mw-parser-output .cs1-kern-right{padding-right:0.2em}.mw-parser-output .citation .mw-selflink{font-weight:inherit}@media screen{.mw-parser-output .cs1-format{font-size:95%}html.skin-theme-clientpref-night .mw-parser-output .cs1-maint{color:#18911f}}@media screen and (prefers-color-scheme:dark){html.skin-theme-clientpref-os .mw-parser-output .cs1-maint{color:#18911f}}Liker, Jeffrey K. (2004). *The Toyota way: 14 management principles from the world's greatest manufacturer*. New York: McGraw-Hill. [ISBN](/wiki/ISBN_(identifier) "ISBN (identifier)") [0-07-139231-9](/wiki/Special:BookSources/0-07-139231-9 "Special:BookSources/0-07-139231-9"). [OCLC](/wiki/OCLC_(identifier) "OCLC (identifier)") [54005437](https://search.worldcat.org/oclc/54005437).
2. **[^](#cite_ref-2)** Graban, Mark; Ducharme, Colin; Ruddick, Todd. ["Takt Time"](https://ocw.mit.edu/courses/engineering-systems-division/esd-60-lean-six-sigma-processes-summer-2004/lecture-notes/8_1assembly_op.pdf) (PDF).
3. ^ [***a***](#cite_ref-:0_3-0) [***b***](#cite_ref-:0_3-1) [***c***](#cite_ref-:0_3-2) Haghsheno, Shervin; Binninger, Marco; Dlouhy, Janosch; Sterlike, Simon (20 July 2016). [*History and Theoretical Foundations of Takt Planning and Takt Control*](https://www.iglc.net/Papers/Details/1297) (PDF). 24th Annual Conference of the International Group for Lean Construction. Boston. pp. 53–62. Retrieved 22 November 2020.
4. **[^](#cite_ref-4)** ["Takt"](https://www.wissen.de/wortherkunft/takt). Retrieved 2020-11-15.
5. **[^](#cite_ref-5)** Womack, James P. (2007). *The machine that changed the world: the story of lean production--Toyota's secret weapon in the global car wars that is revolutionizing world industry*. Jones, Daniel T., Roos, Daniel. (1st trade pbk. ed.). New York: Free Press. [ISBN](/wiki/ISBN_(identifier) "ISBN (identifier)") [978-0-7432-9979-4](/wiki/Special:BookSources/978-0-7432-9979-4 "Special:BookSources/978-0-7432-9979-4"). [OCLC](/wiki/OCLC_(identifier) "OCLC (identifier)") [85814817](https://search.worldcat.org/oclc/85814817).
6. **[^](#cite_ref-6)** Womack, James P. (2003). *Lean thinking: banish waste and create wealth in your corporation*. Jones, Daniel T. (1st Free Press ed., rev. and updated ed.). New York: Free Press. [ISBN](/wiki/ISBN_(identifier) "ISBN (identifier)") [0-7432-4927-5](/wiki/Special:BookSources/0-7432-4927-5 "Special:BookSources/0-7432-4927-5"). [OCLC](/wiki/OCLC_(identifier) "OCLC (identifier)") [51031471](https://search.worldcat.org/oclc/51031471).
7. **[^](#cite_ref-7)** Hopp, Wallace J. (2011). *Factory physics*. Spearman, Mark L. (Third ed.). Long Grove, Illinois. [ISBN](/wiki/ISBN_(identifier) "ISBN (identifier)") [978-1-57766-739-1](/wiki/Special:BookSources/978-1-57766-739-1 "Special:BookSources/978-1-57766-739-1"). [OCLC](/wiki/OCLC_(identifier) "OCLC (identifier)") [718450337](https://search.worldcat.org/oclc/718450337).`{{cite book}}`: CS1 maint: location missing publisher ([link](/wiki/Category:CS1_maint:_location_missing_publisher "Category:CS1 maint: location missing publisher"))
8. **[^](#cite_ref-8)** 
   Koskela, L. (1992). [*Application of the New Production Philosophy to Construction*](https://purl.stanford.edu/kh328xt3298) (Technical report). Stanford University (published September 1992).
9. **[^](#cite_ref-9)** Abbasi, Saman; Taghizade, Katayoon; Noorzai, Esmatullah (2020-12-01). ["BIM-Based Combination of Takt Time and Discrete Event Simulation for Implementing Just in Time in Construction Scheduling under Constraints"](https://ascelibrary.org/doi/abs/10.1061/%28ASCE%29CO.1943-7862.0001940). *Journal of Construction Engineering and Management*. **146** (12): 04020143. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1061/(ASCE)CO.1943-7862.0001940](https://doi.org/10.1061%2F%28ASCE%29CO.1943-7862.0001940). [ISSN](/wiki/ISSN_(identifier) "ISSN (identifier)") [1943-7862](https://search.worldcat.org/issn/1943-7862). [S2CID](/wiki/S2CID_(identifier) "S2CID (identifier)") [225165221](https://api.semanticscholar.org/CorpusID:225165221).
10. **[^](#cite_ref-10)** Sacks, R.; Treckmann, M.; Rozenfeld, O. (2009-12-01). ["Visualization of Work Flow to Support Lean Construction"](https://ascelibrary.org/doi/abs/10.1061/%28ASCE%29CO.1943-7862.0000102). *Journal of Construction Engineering and Management*. **135** (12): 1307–1315. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1061/(ASCE)CO.1943-7862.0000102](https://doi.org/10.1061%2F%28ASCE%29CO.1943-7862.0000102). [ISSN](/wiki/ISSN_(identifier) "ISSN (identifier)") [0733-9364](https://search.worldcat.org/issn/0733-9364).
11. **[^](#cite_ref-11)** Yamín, René A.; Harmelink, David J. (2001-10-01). ["Comparison of Linear Scheduling Model (LSM) and Critical Path Method (CPM)"](https://ascelibrary.org/doi/abs/10.1061/%28ASCE%290733-9364%282001%29127%3A5%28374%29). *Journal of Construction Engineering and Management*. **127** (5): 374–381. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1061/(ASCE)0733-9364(2001)127:5(374)](https://doi.org/10.1061%2F%28ASCE%290733-9364%282001%29127%3A5%28374%29). [ISSN](/wiki/ISSN_(identifier) "ISSN (identifier)") [0733-9364](https://search.worldcat.org/issn/0733-9364).
12. **[^](#cite_ref-12)** Brioso, Xavier; Murguia, Danny; Urbina, Alonso (19 June 2017). *Teaching Takt-Time, Flowline, and Point-to-point Precedence Relations: A Peruvian Case Study*. Creative Construction Conference. *Procedia Engineering*. Creative Construction Conference 2017, CCC 2017, 19-22 June 2017, Primosten, Croatia. Vol. 196. Primosten, Croatia. pp. 666–673. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1016/j.proeng.2017.08.056](https://doi.org/10.1016%2Fj.proeng.2017.08.056).
13. **[^](#cite_ref-13)** Kenley, Russell. (2010). *Location-based management for construction: planning, scheduling and control*. Seppänen, Olli. London: Spon Press. [ISBN](/wiki/ISBN_(identifier) "ISBN (identifier)") [978-0-415-37050-9](/wiki/Special:BookSources/978-0-415-37050-9 "Special:BookSources/978-0-415-37050-9"). [OCLC](/wiki/OCLC_(identifier) "OCLC (identifier)") [317118189](https://search.worldcat.org/oclc/317118189).
14. **[^](#cite_ref-14)** Tommelein, Iris D. (9 July 2017). [*Collaborative Takt Time Planning of Non-Repetitive Work*](https://iglc.net/Papers/Details/1482) (PDF). 25th Annual Conference of the International Group for Lean Construction. Heraklion, Greece. pp. 745–752. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.24928/2017/0271](https://doi.org/10.24928%2F2017%2F0271). Retrieved 22 November 2020.
15. **[^](#cite_ref-15)** Linnik, Meeli; Berghede, Klas (31 August 2013). [*An Experiment in Takt Time Planning Applied to Non-Repetitive Work*](https://iglc.net/Papers/Details/924) (PDF). 21th Annual Conference of the International Group for Lean Construction. Fortaleza, Brazil. pp. 609–618. Retrieved 22 November 2020.
16. **[^](#cite_ref-16)** Jabbari, Arman; Tommelein, Iris D.; Kaminsky, Philip M. (2020-10-01). ["Workload leveling based on workspace zoning for takt planning"](https://doi.org/10.1016%2Fj.autcon.2020.103223). *[Automation in Construction](/wiki/Automation_in_Construction "Automation in Construction")*. **118** 103223. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1016/j.autcon.2020.103223](https://doi.org/10.1016%2Fj.autcon.2020.103223). [ISSN](/wiki/ISSN_(identifier) "ISSN (identifier)") [0926-5805](https://search.worldcat.org/issn/0926-5805). [S2CID](/wiki/S2CID_(identifier) "S2CID (identifier)") [224887268](https://api.semanticscholar.org/CorpusID:224887268).
17. **[^](#cite_ref-17)** Laraia, Anthony C.; Patricia E. Moody; Robert W. Hall (1999). *The Kaizen Blitz: accelerating breakthroughs in productivity and performance*. New York: John Wiley and Sons. [ISBN](/wiki/ISBN_(identifier) "ISBN (identifier)") [978-0-471-24648-0](/wiki/Special:BookSources/978-0-471-24648-0 "Special:BookSources/978-0-471-24648-0").[*[page needed](/wiki/Wikipedia:Citing_sources "Wikipedia:Citing sources")*]

## External links

[[edit](/w/index.php?title=Takt_time&veaction=edit&section=12 "Edit section: External links") | [edit source](/w/index.php?title=Takt_time&action=edit&section=12 "Edit section's source code: External links")]

- [Lean Manufacturing site about Takt time](http://www.strategosinc.com/takt_time.htm)
- [Six Sigma site about Takt time](http://www.isixsigma.com/dictionary/Takt_Time-455.htm)
- [On Line business processes simulator](http://www.bpsimulator.com/)
- [Takt Time - a vision for Lean Manufacturing](http://world-class-manufacturing.com/takt_time/takt_time.html)
- [Understanding Takt Time and Cycle Time](https://leansigmacorporation.com/understanding-takt-time-and-cycle-time/)

## Further reading

[[edit](/w/index.php?title=Takt_time&veaction=edit&section=13 "Edit section: Further reading") | [edit source](/w/index.php?title=Takt_time&action=edit&section=13 "Edit section's source code: Further reading")]

- Monden, Yasuhiro (2011). *Toyota Production System: An Integrated Approach to Just-In-Time*. New York: Productivity Press. p. 566. [ISBN](/wiki/ISBN_(identifier) "ISBN (identifier)") [978-1-4398-2097-1](/wiki/Special:BookSources/978-1-4398-2097-1 "Special:BookSources/978-1-4398-2097-1").
- [Ohno, Taiichi](/wiki/Taiichi_Ohno "Taiichi Ohno"), *Toyota Production System: Beyond Large-Scale Production*, Productivity Press (1988). [ISBN](/wiki/ISBN_(identifier) "ISBN (identifier)") [0-915299-14-3](/wiki/Special:BookSources/0-915299-14-3 "Special:BookSources/0-915299-14-3")
- Baudin, Michel, *Lean Assembly: The Nuts and Bolts of Making Assembly Operations Flow*, Productivity Press (2002). [ISBN](/wiki/ISBN_(identifier) "ISBN (identifier)") [1-56327-263-6](/wiki/Special:BookSources/1-56327-263-6 "Special:BookSources/1-56327-263-6")
- Ortiz, Chris A., *Kaizen Assembly: Designing, Constructing, and Managing a Lean Assembly Line*, CRC Press. [ISBN](/wiki/ISBN_(identifier) "ISBN (identifier)") [978-0-8493-7187-5](/wiki/Special:BookSources/978-0-8493-7187-5 "Special:BookSources/978-0-8493-7187-5")

.mw-parser-output .hlist dl,.mw-parser-output .hlist ol,.mw-parser-output .hlist ul{margin:0;padding:0}.mw-parser-output .hlist dd,.mw-parser-output .hlist dt,.mw-parser-output .hlist li{margin:0;display:inline}.mw-parser-output .hlist.inline,.mw-parser-output .hlist.inline dl,.mw-parser-output .hlist.inline ol,.mw-parser-output .hlist.inline ul,.mw-parser-output .hlist dl dl,.mw-parser-output .hlist dl ol,.mw-parser-output .hlist dl ul,.mw-parser-output .hlist ol dl,.mw-parser-output .hlist ol ol,.mw-parser-output .hlist ol ul,.mw-parser-output .hlist ul dl,.mw-parser-output .hlist ul ol,.mw-parser-output .hlist ul ul{display:inline}.mw-parser-output .hlist .mw-empty-li{display:none}.mw-parser-output .hlist dt::after{content:": "}.mw-parser-output .hlist dd::after,.mw-parser-output .hlist li::after{content:"\a0 · ";font-weight:bold}.mw-parser-output .hlist dd:last-child::after,.mw-parser-output .hlist dt:last-child::after,.mw-parser-output .hlist li:last-child::after{content:none}.mw-parser-output .hlist dd dd:first-child::before,.mw-parser-output .hlist dd dt:first-child::before,.mw-parser-output .hlist dd li:first-child::before,.mw-parser-output .hlist dt dd:first-child::before,.mw-parser-output .hlist dt dt:first-child::before,.mw-parser-output .hlist dt li:first-child::before,.mw-parser-output .hlist li dd:first-child::before,.mw-parser-output .hlist li dt:first-child::before,.mw-parser-output .hlist li li:first-child::before{content:" (";font-weight:normal}.mw-parser-output .hlist dd dd:last-child::after,.mw-parser-output .hlist dd dt:last-child::after,.mw-parser-output .hlist dd li:last-child::after,.mw-parser-output .hlist dt dd:last-child::after,.mw-parser-output .hlist dt dt:last-child::after,.mw-parser-output .hlist dt li:last-child::after,.mw-parser-output .hlist li dd:last-child::after,.mw-parser-output .hlist li dt:last-child::after,.mw-parser-output .hlist li li:last-child::after{content:")";font-weight:normal}.mw-parser-output .hlist ol{counter-reset:listitem}.mw-parser-output .hlist ol>li{counter-increment:listitem}.mw-parser-output .hlist ol>li::before{content:" "counter(listitem)"\a0 "}.mw-parser-output .hlist dd ol>li:first-child::before,.mw-parser-output .hlist dt ol>li:first-child::before,.mw-parser-output .hlist li ol>li:first-child::before{content:" ("counter(listitem)"\a0 "}.mw-parser-output .navbox{box-sizing:border-box;border:1px solid #a2a9b1;width:100%;clear:both;font-size:88%;text-align:center;padding:1px;margin:1em auto 0}.mw-parser-output .navbox .navbox{margin-top:0}.mw-parser-output .navbox+.navbox-styles+.navbox,.mw-parser-output .navbox+span.mw-empty-elt+.navbox-styles+.navbox{margin-top:-1px}.mw-parser-output .navbox-inner,.mw-parser-output .navbox-subgroup{width:100%}.mw-parser-output .navbox-group,.mw-parser-output .navbox-title,.mw-parser-output .navbox-abovebelow{padding:0.25em 1em;line-height:1.5em;text-align:center}.mw-parser-output .navbox-group{white-space:nowrap;text-align:right}.mw-parser-output .navbox,.mw-parser-output .navbox-subgroup{background-color:#fdfdfd;color:inherit}.mw-parser-output .navbox-list{line-height:1.5em;border-color:#fdfdfd}.mw-parser-output .navbox-list-with-group{text-align:left;border-left-width:2px;border-left-style:solid}.mw-parser-output tr+tr>.navbox-abovebelow,.mw-parser-output tr+tr>.navbox-group,.mw-parser-output tr+tr>.navbox-image,.mw-parser-output tr+tr>.navbox-list{border-top:2px solid #fdfdfd}.mw-parser-output .navbox-title{background-color:#ccf;color:inherit}.mw-parser-output .navbox-abovebelow,.mw-parser-output .navbox-group,.mw-parser-output .navbox-subgroup .navbox-title{background-color:#ddf;color:inherit}.mw-parser-output .navbox-subgroup .navbox-group,.mw-parser-output .navbox-subgroup .navbox-abovebelow{background-color:#e6e6ff;color:inherit}.mw-parser-output .navbox-even{background-color:#f7f7f7;color:inherit}.mw-parser-output .navbox-odd{background-color:transparent;color:inherit}.mw-parser-output .navbox .hlist td dl,.mw-parser-output .navbox .hlist td ol,.mw-parser-output .navbox .hlist td ul,.mw-parser-output .navbox td.hlist dl,.mw-parser-output .navbox td.hlist ol,.mw-parser-output .navbox td.hlist ul{padding:0.125em 0}.mw-parser-output .navbox .navbar{display:block;font-size:100%}.mw-parser-output .navbox-title .navbar{float:left;text-align:left;margin-right:0.5em}body.skin--responsive .mw-parser-output .navbox-image img{max-width:none!important}@media print{body.ns-0 .mw-parser-output .navbox{display:none!important}}

| .mw-parser-output .navbar{display:inline;font-size:88%;font-weight:normal}.mw-parser-output .navbar-collapse{float:left;text-align:left}.mw-parser-output .navbar-boxtext{word-spacing:0}.mw-parser-output .navbar ul{display:inline-block;white-space:nowrap;line-height:inherit}.mw-parser-output .navbar-brackets::before{margin-right:-0.125em;content:"[ "}.mw-parser-output .navbar-brackets::after{margin-left:-0.125em;content:" ]"}.mw-parser-output .navbar li{word-spacing:-0.125em}.mw-parser-output .navbar a>span,.mw-parser-output .navbar a>abbr{text-decoration:inherit}.mw-parser-output .navbar-mini abbr{font-variant:small-caps;border-bottom:none;text-decoration:none;cursor:inherit}.mw-parser-output .navbar-ct-full{font-size:114%;margin:0 7em}.mw-parser-output .navbar-ct-mini{font-size:114%;margin:0 4em}html.skin-theme-clientpref-night .mw-parser-output .navbar li a abbr{color:var(--color-base)!important}@media(prefers-color-scheme:dark){html.skin-theme-clientpref-os .mw-parser-output .navbar li a abbr{color:var(--color-base)!important}}@media print{.mw-parser-output .navbar{display:none!important}} - [v](/wiki/Template:Lean_manufacturing_tools "Template:Lean manufacturing tools") - [t](/wiki/Template_talk:Lean_manufacturing_tools "Template talk:Lean manufacturing tools") - [e](/wiki/Special:EditPage/Template:Lean_manufacturing_tools "Special:EditPage/Template:Lean manufacturing tools")  [Lean manufacturing](/wiki/Lean_manufacturing "Lean manufacturing") tools | |
| --- | --- |
| - [Cellular manufacturing](/wiki/Cellular_manufacturing "Cellular manufacturing") - Takt time - [*Muda*: wastefulness](/wiki/Muda_(Japanese_term) "Muda (Japanese term)") - [*Mura*: unevenness](/wiki/Mura_(Japanese_term) "Mura (Japanese term)") - [*Muri*: overburden](/wiki/Muri_(Japanese_term) "Muri (Japanese term)") - [Continuous-flow manufacturing](/wiki/Continuous-flow_manufacturing "Continuous-flow manufacturing") - [Kanban](/wiki/Kanban "Kanban") - [Five whys](/wiki/Five_whys "Five whys") - [Single-minute exchange of die](/wiki/Single-minute_exchange_of_die "Single-minute exchange of die") - [Poka-yoke](/wiki/Poka-yoke "Poka-yoke") - [Production leveling](/wiki/Production_leveling "Production leveling") - [Total productive maintenance](/wiki/Total_productive_maintenance "Total productive maintenance") - [5S (methodology)](/wiki/5S_(methodology) "5S (methodology)") - [Plan–do–check–act](/wiki/PDCA "PDCA") | |

|  |  |
| --- | --- |
| [Authority control databases](/wiki/Help:Authority_control "Help:Authority control") [Edit this at Wikidata](https://www.wikidata.org/wiki/Q1472394#identifiers "Edit this at Wikidata") | - [GND](https://d-nb.info/gnd/4212485-2) |
