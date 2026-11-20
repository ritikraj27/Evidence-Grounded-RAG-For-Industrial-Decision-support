<!-- category: reliability_engineering -->
# Fault tree analysis

Failure analysis system used in safety engineering and reliability engineering

[![](//thumb.wikimedia.org/wikipedia/commons/thumb/d/db/Fault_tree.svg/250px-Fault_tree.svg.png?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail)](/wiki/File:Fault_tree.svg)

A fault tree diagram

**Fault tree analysis** (**FTA**) is a type of [failure analysis](/wiki/Failure_analysis "Failure analysis") in which an undesired state of a system is examined. This analysis method is mainly used in [safety engineering](/wiki/Safety_engineering "Safety engineering") and [reliability engineering](/wiki/Reliability_engineering "Reliability engineering") to understand how systems can fail, to identify the best ways to reduce risk and to determine (or get a feeling for) event rates of a safety accident or a particular system level (functional) failure. FTA is used in the [aerospace](/wiki/Aerospace "Aerospace"),[[1]](#cite_note-NASA_SE_Toolbox-1) [nuclear power](/wiki/Nuclear_power "Nuclear power"), [chemical and process](/wiki/Process_manufacturing "Process manufacturing"),[[2]](#cite_note-2)[[3]](#cite_note-3)[[4]](#cite_note-4) [pharmaceutical](/wiki/Pharmaceutical_drug "Pharmaceutical drug"),[[5]](#cite_note-5) [petrochemical](/wiki/Petrochemical "Petrochemical") and other high-hazard industries; but is also used in fields as diverse as risk factor identification relating to [social service](/wiki/Social_services "Social services") system failure.[[6]](#cite_note-6) FTA is also used in software engineering for debugging purposes and is closely related to cause-elimination technique used to detect bugs.

In aerospace, the more general term "system failure condition" is used for the "undesired state" / top event of the fault tree. These conditions are classified by the severity of their effects. The most severe conditions require the most extensive fault tree analysis. These system failure conditions and their classification are often previously determined in the functional [hazard analysis](/wiki/Hazard_analysis "Hazard analysis").

## Usage

[[edit](/w/index.php?title=Fault_tree_analysis&veaction=edit&section=1 "Edit section: Usage") | [edit source](/w/index.php?title=Fault_tree_analysis&action=edit&section=1 "Edit section's source code: Usage")]

Fault tree analysis can be used to:[[7]](#cite_note-7)[[8]](#cite_note-8)

- understand the logic leading to the top event / undesired state.
- show compliance with the (input) system safety / reliability requirements.
- prioritize the contributors leading to the top event- creating the critical equipment/parts/events lists for different importance measures
- monitor and control the safety performance of the [complex system](/wiki/Complex_system "Complex system") (e.g., is a particular aircraft safe to fly when fuel valve *x* malfunctions? For how long is it allowed to fly with the valve malfunction?).
- minimize and optimize resources.
- assist in designing a system. The FTA can be used as a design tool that helps to create (output / lower level) requirements.
- function as a diagnostic tool to identify and correct causes of the top event. It can help with the creation of diagnostic manuals / processes.

## History

[[edit](/w/index.php?title=Fault_tree_analysis&veaction=edit&section=2 "Edit section: History") | [edit source](/w/index.php?title=Fault_tree_analysis&action=edit&section=2 "Edit section's source code: History")]

.mw-parser-output .ambox{border:1px solid #a2a9b1;border-left:10px solid #36c;background-color:#fbfbfb;box-sizing:border-box}.mw-parser-output .ambox+.mw-empty-elt+.ambox,.mw-parser-output .ambox+.mw-empty-elt+.mw-empty-elt+.ambox,.mw-parser-output .ambox+.mw-empty-elt+.mw-empty-elt+.mw-empty-elt+.ambox{margin-top:-1px}html body.mediawiki .mw-parser-output .ambox.mbox-small-left{margin:4px 1em 4px 0;overflow:hidden;width:238px;border-collapse:collapse;font-size:88%;line-height:1.25em}.mw-parser-output .ambox-speedy{border-left:10px solid #b32424;background-color:#fee7e6}.mw-parser-output .ambox-delete{border-left:10px solid #b32424}.mw-parser-output .ambox-content{border-left:10px solid #f28500}.mw-parser-output .ambox-style{border-left:10px solid #fc3}.mw-parser-output .ambox-move{border-left:10px solid #9932cc}.mw-parser-output .ambox-protection{border-left:10px solid #a2a9b1}.mw-parser-output .ambox .mbox-text{border:none;padding:0.25em 0.5em;width:100%}.mw-parser-output .ambox .mbox-image{border:none;padding:2px 0 2px 0.5em;text-align:center}.mw-parser-output .ambox .mbox-imageright{border:none;padding:2px 0.5em 2px 0;text-align:center}.mw-parser-output .ambox .mbox-empty-cell{border:none;padding:0;width:1px}.mw-parser-output .ambox .mbox-image-div{width:52px}@media(min-width:720px){.mw-parser-output .ambox{margin:0 10%}}@media print{body.ns-0 .mw-parser-output .ambox{display:none!important}}

|  |  |
| --- | --- |
| Globe icon. | The examples and perspectives in this section **may not represent a [worldwide view](/wiki/Wikipedia:WikiProject_Countering_systemic_bias "Wikipedia:WikiProject Countering systemic bias") of the subject**. You may [improve this section](/wiki/Special:EditPage/Fault_tree_analysis "Special:EditPage/Fault tree analysis"), discuss the issue on the [talk page](/wiki/Talk:Fault_tree_analysis "Talk:Fault tree analysis"), or create a new section, as appropriate. *(May 2022)* *([Learn how and when to remove this message](/wiki/Help:Maintenance_template_removal "Help:Maintenance template removal"))* |

Fault tree analysis (FTA) was originally developed in 1962 at [Bell Laboratories](/wiki/Bell_Labs "Bell Labs") by H.A. Watson, under a [U.S. Air Force](/wiki/United_States_Air_Force "United States Air Force") [Ballistics Systems Division](/wiki/526th_ICBM_Systems_Group "526th ICBM Systems Group") contract to evaluate the [Minuteman I](/wiki/LGM-30_Minuteman "LGM-30 Minuteman") [Intercontinental Ballistic Missile](/wiki/Intercontinental_Ballistic_Missile "Intercontinental Ballistic Missile") (ICBM) Launch Control System.[[9]](#cite_note-9)[[10]](#cite_note-10)[[11]](#cite_note-11)[[12]](#cite_note-12) The use of fault trees has since gained widespread support and is often used as a failure analysis tool by reliability experts.[[13]](#cite_note-13) Following the first published use of FTA in the 1962 Minuteman I Launch Control Safety Study, [Boeing](/wiki/Boeing "Boeing") and [AVCO](/wiki/Avco "Avco") expanded use of FTA to the entire Minuteman II system in 1963–1964. FTA received extensive coverage at a 1965 [System Safety](/wiki/System_Safety "System Safety") Symposium in [Seattle](/wiki/Seattle "Seattle") sponsored by Boeing and the [University of Washington](/wiki/University_of_Washington "University of Washington").[[14]](#cite_note-14) Boeing began using FTA for [civil aircraft](/wiki/Civil_aviation "Civil aviation") design around 1966.[[15]](#cite_note-15)[[16]](#cite_note-16)

Subsequently, within the U.S. military, application of FTA for use with fuses was explored by [Picatinny Arsenal](/wiki/Picatinny_Arsenal "Picatinny Arsenal") in the 1960s and 1970s.[[17]](#cite_note-17) In 1976 the [U.S. Army Materiel Command](/wiki/United_States_Army_Materiel_Command "United States Army Materiel Command") incorporated FTA into an Engineering Design Handbook on Design for Reliability.[[18]](#cite_note-18) The Reliability Analysis Center at [Rome Laboratory](/wiki/Rome_Laboratory "Rome Laboratory") and its successor organizations now with the [Defense Technical Information Center](/wiki/Defense_Technical_Information_Center "Defense Technical Information Center") (Reliability Information Analysis Center, and now Defense Systems Information Analysis Center[[19]](#cite_note-19)) has published documents on FTA and reliability block diagrams since the 1960s.[[20]](#cite_note-20)[[21]](#cite_note-21)[[22]](#cite_note-22) MIL-HDBK-338B provides a more recent reference.[[23]](#cite_note-23)

[![](//thumb.wikimedia.org/wikipedia/commons/thumb/c/ce/MIT_16.885J_-_ESD.35J_Aircraft_Systems_Engineering%2C_Fall_2004_-_Fault_Tree_and_Event_Tree_Examples.jpg/250px-MIT_16.885J_-_ESD.35J_Aircraft_Systems_Engineering%2C_Fall_2004_-_Fault_Tree_and_Event_Tree_Examples.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail)](/wiki/File:MIT_16.885J_-_ESD.35J_Aircraft_Systems_Engineering,_Fall_2004_-_Fault_Tree_and_Event_Tree_Examples.jpg)

Fault tree and event tree examples from the field of aircraft systems engineering.

In 1970, the [U.S. Federal Aviation Administration](/wiki/FAA "FAA") (FAA) published a change to 14 [CFR](/wiki/Code_of_Federal_Regulations "Code of Federal Regulations") 25.1309 [airworthiness](/wiki/Airworthiness "Airworthiness") regulations for [transport category](/wiki/Transport_category "Transport category") [aircraft](/wiki/Aircraft "Aircraft") in the [Federal Register](/wiki/Federal_Register "Federal Register") at 35 FR 5665 (1970-04-08). This change adopted failure probability criteria for [aircraft systems](/wiki/Aircraft_systems "Aircraft systems") and equipment and led to widespread use of FTA in civil aviation. In 1998, the FAA published Order 8040.4,[[24]](#cite_note-24) establishing risk management policy including hazard analysis in a range of critical activities beyond aircraft certification, including [air traffic control](/wiki/Air_traffic_control "Air traffic control") and modernization of the U.S. [National Airspace System](/wiki/National_Airspace_System "National Airspace System"). This led to the publication of the FAA System Safety Handbook, which describes the use of FTA in various types of formal hazard analysis.[[25]](#cite_note-25)

Early in the [Apollo program](/wiki/Apollo_project "Apollo project") the question was asked about the probability of successfully sending astronauts to the moon and returning them safely to Earth. A risk, or reliability, calculation of some sort was performed and the result was a mission success probability that was unacceptably low. This result discouraged NASA from further quantitative risk or reliability analysis until after the *Challenger* accident in 1986. Instead, NASA decided to rely on the use of [failure modes and effects analysis (FMEA)](/wiki/Failure_mode_and_effects_analysis "Failure mode and effects analysis") and other qualitative methods for system safety assessments. After the *Challenger* accident, the importance of [probabilistic risk assessment](/wiki/Probabilistic_risk_assessment "Probabilistic risk assessment") (PRA) and FTA in systems risk and reliability analysis was realized and its use at NASA has begun to grow and now FTA is considered as one of the most important system reliability and safety analysis techniques.[[26]](#cite_note-fthbaa-26)

Within the nuclear power industry, the [U.S. Nuclear Regulatory Commission](/wiki/Nuclear_Regulatory_Commission "Nuclear Regulatory Commission") began using PRA methods including FTA in 1975, and significantly expanded PRA research following the 1979 incident at [Three Mile Island](/wiki/Three_Mile_Island_accident "Three Mile Island accident").[[27]](#cite_note-27) This eventually led to the 1981 publication of the NRC Fault Tree Handbook NUREG–0492,[[28]](#cite_note-28) and mandatory use of PRA under the NRC's regulatory authority.

Following process industry disasters such as the 1984 [Bhopal disaster](/wiki/Bhopal_disaster "Bhopal disaster") and 1988 [Piper Alpha](/wiki/Piper_Alpha "Piper Alpha") explosion, in 1992 the [United States Department of Labor](/wiki/United_States_Department_of_Labor "United States Department of Labor") [Occupational Safety and Health Administration](/wiki/Occupational_Safety_and_Health_Administration "Occupational Safety and Health Administration") (OSHA) published in the Federal Register at 57 FR 6356 (1992-02-24) its [Process Safety Management](/wiki/Process_Safety_Management "Process Safety Management") (PSM) standard in 19 CFR 1910.119.[[29]](#cite_note-29) OSHA PSM recognizes FTA as an acceptable method for [process hazard analysis](/wiki/Process_hazard_analysis "Process hazard analysis") (PHA).

Today FTA is widely used in [system safety](/wiki/System_safety "System safety") and [reliability engineering](/wiki/Reliability_engineering "Reliability engineering"), and in all major fields of engineering.

## Methodology

[[edit](/w/index.php?title=Fault_tree_analysis&veaction=edit&section=3 "Edit section: Methodology") | [edit source](/w/index.php?title=Fault_tree_analysis&action=edit&section=3 "Edit section's source code: Methodology")]

FTA [methodology](/wiki/Methodology "Methodology") is described in several industry and government standards, including NRC NUREG–0492 for the nuclear power industry, an aerospace-oriented revision to NUREG–0492 for use by [NASA](/wiki/NASA "NASA"),[[26]](#cite_note-fthbaa-26) [SAE](/wiki/Society_of_Automotive_Engineers "Society of Automotive Engineers") [ARP4761](/wiki/ARP4761 "ARP4761") for civil aerospace, MIL–HDBK–338 for military systems, [IEC](/wiki/International_Electrotechnical_Commission "International Electrotechnical Commission") standard IEC 61025[[30]](#cite_note-30) is intended for cross-industry use and has been adopted as European Norm EN 61025.

Any sufficiently complex system is subject to failure as a result of one or more subsystems failing. The likelihood of failure, however, can often be reduced through improved system design. Fault tree analysis maps the relationship between faults, subsystems, and redundant safety design elements by creating a logic diagram of the overall system.

The undesired outcome is taken as the root ('top event') of a tree of logic. For instance, the undesired outcome of a metal stamping press operation being considered might be a human appendage being stamped. Working backward from this top event it might be determined that there are two ways this could happen: during normal operation or during maintenance operation. This condition is a logical OR. Considering the branch of the hazard occurring during normal operation, perhaps it is determined that there are two ways this could happen: the press cycles and harms the operator, or the press cycles and harms another person. This is another logical OR. A design improvement can be made by requiring the operator to press two separate buttons to cycle the machine—this is a safety feature in the form of a logical AND. The button may have an intrinsic failure rate—this becomes a fault stimulus that can be analyzed.

When fault trees are labeled with actual numbers for failure probabilities, [computer programs](/wiki/Computer_programs "Computer programs") can calculate failure probabilities from fault trees. When a specific event is found to have more than one effect event, i.e. it has impact on several subsystems, it is called a common cause or common mode. Graphically speaking, it means this event will appear at several locations in the tree. Common causes introduce dependency relations between events. The probability computations of a tree which contains some common causes are much more complicated than regular trees where all events are considered as independent. Not all software tools available on the market provide such capability.

The tree is usually written out using conventional [logic gate](/wiki/Logic_gate "Logic gate") symbols. A cut set is a combination of events, typically component failures, causing the top event. If no event can be removed from a cut set without failing to cause the top event, then it is called a minimal cut set.

Some industries use both fault trees and [event trees](/wiki/Event_tree "Event tree") (see [Probabilistic Risk Assessment](/wiki/Probabilistic_Risk_Assessment "Probabilistic Risk Assessment")). An event tree starts from an undesired initiator (loss of critical supply, component failure etc.) and follows possible further system events through to a series of final consequences. As each new event is considered, a new node on the tree is added with a split of probabilities of taking either branch. The probabilities of a range of 'top events' arising from the initial event can then be seen.

Classic programs include the [Electric Power Research Institute](/wiki/Electric_Power_Research_Institute "Electric Power Research Institute")'s (EPRI) CAFTA software, which is used by many of the US nuclear power plants and by a majority of US and international aerospace manufacturers, and the [Idaho National Laboratory](/wiki/Idaho_National_Laboratory "Idaho National Laboratory")'s [SAPHIRE](/wiki/SAPHIRE "SAPHIRE"), which is used by the U.S. Government to evaluate the safety and [reliability](/wiki/Reliability_engineering "Reliability engineering") of [nuclear reactors](/wiki/Nuclear_reactor "Nuclear reactor"), the [Space Shuttle](/wiki/Space_Shuttle "Space Shuttle"), and the [International Space Station](/wiki/International_Space_Station "International Space Station"). Outside the US, the software [RiskSpectrum](http://www.RiskSpectrum.com) is a popular tool for fault tree and event tree analysis, and is licensed for use at more than 60% of the world's nuclear power plants for probabilistic safety assessment. Professional-grade [free software](/wiki/Free_software "Free software") is also widely available; SCRAM[[31]](#cite_note-31) is an open-source tool that implements the Open-PSA Model Exchange Format[[32]](#cite_note-32) open standard for probabilistic safety assessment applications.

## Graphic symbols

[[edit](/w/index.php?title=Fault_tree_analysis&veaction=edit&section=4 "Edit section: Graphic symbols") | [edit source](/w/index.php?title=Fault_tree_analysis&action=edit&section=4 "Edit section's source code: Graphic symbols")]

The basic symbols used in FTA are grouped as events, gates, and transfer symbols. Minor variations may be used in FTA software.

### Event symbols

[[edit](/w/index.php?title=Fault_tree_analysis&veaction=edit&section=5 "Edit section: Event symbols") | [edit source](/w/index.php?title=Fault_tree_analysis&action=edit&section=5 "Edit section's source code: Event symbols")]

Event symbols are used for *primary events* and *intermediate events*. Primary events are not further developed on the fault tree. Intermediate events are found at the output of a gate. The event symbols are shown below:

- [![Basic event](//upload.wikimedia.org/wikipedia/commons/4/43/FTA_basic_event.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail_unscaled)](/wiki/File:FTA_basic_event.jpg "Basic event")

  Basic event
- [![External event](//upload.wikimedia.org/wikipedia/commons/8/8d/FTA_initiating_event.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail_unscaled)](/wiki/File:FTA_initiating_event.jpg "External event")

  External event
- [![Undeveloped event](//thumb.wikimedia.org/wikipedia/commons/thumb/b/b1/FTA_undeveloped_event.jpg/120px-FTA_undeveloped_event.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail)](/wiki/File:FTA_undeveloped_event.jpg "Undeveloped event")

  Undeveloped event
- [![Conditioning event](//thumb.wikimedia.org/wikipedia/commons/thumb/5/52/FTA_conditioning_event.jpg/120px-FTA_conditioning_event.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail)](/wiki/File:FTA_conditioning_event.jpg "Conditioning event")

  Conditioning event
- [![Intermediate event](//thumb.wikimedia.org/wikipedia/commons/thumb/1/1b/FTA_intermediate_event.jpg/120px-FTA_intermediate_event.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail)](/wiki/File:FTA_intermediate_event.jpg "Intermediate event")

  Intermediate event

The primary event symbols are typically used as follows:

- **Basic event** – failure or error in a system component or element (example: switch stuck in open position)
- **External event** – normally expected to occur (not of itself a fault)
- **Undeveloped event** – an event about which insufficient information is available, or which is of no consequence
- **Conditioning event** – conditions that restrict or affect logic gates (example: mode of operation in effect)

An intermediate event gate can be used immediately above a primary event to provide more room to type the event description.

FTA is a top-to-bottom approach.

### Gate symbols

[[edit](/w/index.php?title=Fault_tree_analysis&veaction=edit&section=6 "Edit section: Gate symbols") | [edit source](/w/index.php?title=Fault_tree_analysis&action=edit&section=6 "Edit section's source code: Gate symbols")]

Gate symbols describe the relationship between input and output events. The symbols are derived from Boolean logic symbols:

- [![OR gate](//upload.wikimedia.org/wikipedia/commons/e/e9/FTA_OR_gate.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail_unscaled)](/wiki/File:FTA_OR_gate.jpg "OR gate")

  OR gate
- [![AND gate](//upload.wikimedia.org/wikipedia/commons/c/cf/FTA_AND_gate.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail_unscaled)](/wiki/File:FTA_AND_gate.jpg "AND gate")

  AND gate
- [![Exclusive OR gate](//thumb.wikimedia.org/wikipedia/commons/thumb/c/c3/FTA_XOR_gate.jpg/120px-FTA_XOR_gate.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail)](/wiki/File:FTA_XOR_gate.jpg "Exclusive OR gate")

  Exclusive OR gate
- [![Priority AND gate](//thumb.wikimedia.org/wikipedia/commons/thumb/f/f7/FTA_priority_AND_gate.jpg/120px-FTA_priority_AND_gate.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail)](/wiki/File:FTA_priority_AND_gate.jpg "Priority AND gate")

  Priority AND gate
- [![Inhibit gate](//thumb.wikimedia.org/wikipedia/commons/thumb/2/2a/FTA_inhibit_gate.jpg/120px-FTA_inhibit_gate.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail)](/wiki/File:FTA_inhibit_gate.jpg "Inhibit gate")

  Inhibit gate

The gates work as follows:

- **OR gate** – the output occurs if any input occurs.
- **AND gate** – the output occurs only if all inputs occur (inputs are independent from the source).
- **Exclusive OR gate** – the output occurs if exactly one input occurs.
- **Priority AND gate** – the output occurs if the inputs occur in a specific sequence specified by a conditioning event.
- **Inhibit gate** – the output occurs if the input occurs under an enabling condition specified by a conditioning event.

### Transfer symbols

[[edit](/w/index.php?title=Fault_tree_analysis&veaction=edit&section=7 "Edit section: Transfer symbols") | [edit source](/w/index.php?title=Fault_tree_analysis&action=edit&section=7 "Edit section's source code: Transfer symbols")]

Transfer symbols are used to connect the inputs and outputs of related fault trees, such as the fault tree of a subsystem to its system. NASA prepared a complete document about FTA through practical incidents.[[26]](#cite_note-fthbaa-26)

- [![Transfer in](//thumb.wikimedia.org/wikipedia/commons/thumb/2/2c/FTA_transfer_in.jpg/120px-FTA_transfer_in.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail)](/wiki/File:FTA_transfer_in.jpg "Transfer in")

  Transfer in
- [![Transfer out](//thumb.wikimedia.org/wikipedia/commons/thumb/1/13/FTA_transfer_out.jpg/120px-FTA_transfer_out.jpg?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail)](/wiki/File:FTA_transfer_out.jpg "Transfer out")

  Transfer out

## Basic mathematical foundation

[[edit](/w/index.php?title=Fault_tree_analysis&veaction=edit&section=8 "Edit section: Basic mathematical foundation") | [edit source](/w/index.php?title=Fault_tree_analysis&action=edit&section=8 "Edit section's source code: Basic mathematical foundation")]

Events in a fault tree are associated with [statistical](/wiki/Statistics "Statistics") [probabilities](/wiki/Probability_theory "Probability theory") or Poisson-Exponentially distributed constant rates. For example, component failures may typically occur at some constant [failure rate](/wiki/Failure_rate "Failure rate") λ (a constant hazard function). In this simplest case, failure probability depends on the rate λ and the exposure time t:

P
=
1
−

e

−
λ
t
{\displaystyle P=1-e^{-\lambda t}}
![{\displaystyle P=1-e^{-\lambda t}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/470bc52985fa5beda6af021a6aa5e7efc3614a45)

where:

P
≈
λ
t
{\displaystyle P\approx \lambda t}
![{\displaystyle P\approx \lambda t}](https://wikimedia.org/api/rest_v1/media/math/render/svg/878b7ad2eadfbd13f9ddd2a99860987402e88a88) if 

λ
t
<
0.001
{\displaystyle \lambda t<0.001}
![{\displaystyle \lambda t<0.001}](https://wikimedia.org/api/rest_v1/media/math/render/svg/cabfc853617b74c18191fb724ff2c2eedef2389e)

A fault tree is often normalized to a given time interval, such as a flight hour or an average mission time. Event probabilities depend on the relationship of the event hazard function to this interval.

Unlike conventional [logic gate](/wiki/Logic_gate "Logic gate") diagrams in which inputs and outputs hold the [binary](/wiki/Binary_numeral_system "Binary numeral system") values of TRUE (1) or FALSE (0), the gates in a fault tree output probabilities related to the [set operations](/wiki/Algebra_of_sets "Algebra of sets") of [Boolean logic](/wiki/Boolean_logic "Boolean logic"). The probability of a gate's output event depends on the input event probabilities.

An AND gate represents a combination of [independent](/wiki/Independence_(probability_theory) "Independence (probability theory)") events. That is, the probability of any input event to an AND gate is unaffected by any other input event to the same gate. In [set theoretic](/wiki/Set_theory "Set theory") terms, this is equivalent to the intersection of the input event sets, and the probability of the AND gate output is given by:

:   P (A and B) = P (A ∩ B) = P(A) P(B)

An OR gate, on the other hand, corresponds to set union:

:   P (A or B) = P (A ∪ B) = P(A) + P(B) - P (A ∩ B)

Since failure probabilities on fault trees tend to be small (less than .01), P (A ∩ B) usually becomes a very small error term, and the output of an OR gate may be conservatively approximated by using an assumption that the inputs are [mutually exclusive events](/wiki/Mutually_exclusive_events "Mutually exclusive events"):

:   P (A or B) ≈ P(A) + P(B), P (A ∩ B) ≈ 0

An exclusive OR gate with two inputs represents the probability that one or the other input, but not both, occurs:

:   P (A xor B) = P(A) + P(B) - 2P (A ∩ B)

Again, since P (A ∩ B) usually becomes a very small error term, the exclusive OR gate has limited value in a fault tree.

Quite often, Poisson-Exponentially distributed rates[[33]](#cite_note-33) are used to quantify a fault tree instead of probabilities. Rates are often modeled as constant in time while probability is a function of time. Poisson-Exponential events are modelled as infinitely short so no two events can overlap. An OR gate is the superposition (addition of rates) of the two input failure frequencies or failure rates which are modeled as [Poisson point processes](/wiki/Poisson_point_process "Poisson point process"). The output of an AND gate is calculated using the unavailability (Q1) of one event thinning the Poisson point process of the other event (λ2). The unavailability (Q2) of the other event then thins the Poisson point process of the first event (λ1). The two resulting Poisson point processes are superimposed according to the following equations.

The output of an AND gate is the combination of independent input events 1 and 2 to the AND gate:

:   Failure Frequency = λ1Q2 + λ2Q1 where Q = 1 - e-λt ≈ λt if λt < 0.001
:   Failure Frequency ≈ λ1λ2t2 + λ2λ1t1 if λ1t1 < 0.001 and λ2t2 < 0.001

In a fault tree, unavailability (Q) may be defined as the unavailability of safe operation and may not refer to the unavailability of the system operation depending on how the fault tree was structured. The input terms to the fault tree must be carefully defined.

## Analysis

[[edit](/w/index.php?title=Fault_tree_analysis&veaction=edit&section=9 "Edit section: Analysis") | [edit source](/w/index.php?title=Fault_tree_analysis&action=edit&section=9 "Edit section's source code: Analysis")]

Many different approaches can be used to model a FTA, but the most common and popular way can be summarized in a few steps. A single fault tree is used to analyze one and only one undesired event, which may be subsequently fed into another fault tree as a basic event. Though the nature of the undesired event may vary dramatically, a FTA follows the same procedure for any undesired event; be it a delay of 0.25 ms for the generation of electrical power, an undetected cargo bay fire, or the random, unintended launch of an [ICBM](/wiki/ICBM "ICBM").

FTA analysis involves five steps:

1. Define the undesired event to study.
   - Definition of the undesired event can be very hard to uncover, although some of the events are very easy and obvious to observe. An engineer with a wide knowledge of the design of the system is the best person to help define and number the undesired events. Undesired events are used then to make FTAs. Each FTA is limited to one undesired event.
2. Obtain an understanding of the system.
   - Once the undesired event is selected, all causes with probabilities of affecting the undesired event of 0 or more are studied and analyzed. Getting exact numbers for the probabilities leading to the event is usually impossible for the reason that it may be very costly and time-consuming to do so. Computer software is used to study probabilities; this may lead to less costly system analysis.  
      System analysts can help with understanding the overall system. System designers have full knowledge of the system and this knowledge is very important for not missing any cause affecting the undesired event. For the selected event all causes are then numbered and sequenced in the order of occurrence and then are used for the next step which is drawing or constructing the fault tree.
3. Construct the fault tree.
   - After selecting the undesired event and having analyzed the system so that we know all the causing effects (and if possible their probabilities) we can now construct the fault tree. Fault tree is based on AND and OR gates which define the major characteristics of the fault tree.
4. Evaluate the fault tree.
   - After the fault tree has been assembled for a specific undesired event, it is evaluated and analyzed for any possible improvement or in other words study the risk management and find ways for system improvement. A wide range of qualitative and quantitative analysis methods can be applied.[[34]](#cite_note-34) This step is as an introduction for the final step which will be to control the hazards identified. In short, in this step we identify all possible hazards affecting the system in a direct or indirect way.
5. Control the hazards identified.
   - This step is very specific and differs largely from one system to another, but the main point will always be that after identifying the hazards all possible methods are pursued to decrease the probability of occurrence.

## Comparison with other analytical methods

[[edit](/w/index.php?title=Fault_tree_analysis&veaction=edit&section=10 "Edit section: Comparison with other analytical methods") | [edit source](/w/index.php?title=Fault_tree_analysis&action=edit&section=10 "Edit section's source code: Comparison with other analytical methods")]

FTA is a [deductive](/wiki/Deductive_reasoning "Deductive reasoning"), top-down method aimed at analyzing the effects of initiating faults and events on a complex system. This contrasts with [failure mode and effects analysis](/wiki/Failure_mode_and_effects_analysis "Failure mode and effects analysis") (FMEA), which is an [inductive](/wiki/Inductive_reasoning "Inductive reasoning"), bottom-up analysis method aimed at analyzing the effects of single component or function failures on equipment or subsystems. FTA is very good at showing how resistant a system is to single or multiple initiating faults. It is not good at finding all possible initiating faults. FMEA is good at exhaustively cataloging initiating faults, and identifying their local effects. It is not good at examining multiple failures or their effects at a system level. FTA considers external events, FMEA does not.[[35]](#cite_note-35) In civil aerospace the usual practice is to perform both FTA and FMEA, with a [failure mode effects summary](/wiki/Failure_mode_and_effects_analysis "Failure mode and effects analysis") (FMES) as the interface between FMEA and FTA.

Alternatives to FTA include [dependence diagram](/wiki/Reliability_block_diagram "Reliability block diagram") (DD), also known as [reliability block diagram](/wiki/Reliability_block_diagram "Reliability block diagram") (RBD) and [Markov analysis](/wiki/Markov_analysis "Markov analysis"). A dependence diagram is equivalent to a success tree analysis (STA), the logical inverse of an FTA, and depicts the system using paths instead of gates. DD and STA produce probability of success (i.e., avoiding a top event) rather than probability of a top event.

## See also

[[edit](/w/index.php?title=Fault_tree_analysis&veaction=edit&section=11 "Edit section: See also") | [edit source](/w/index.php?title=Fault_tree_analysis&action=edit&section=11 "Edit section's source code: See also")]

.mw-parser-output .side-box{margin:4px 0;box-sizing:border-box;border:1px solid var(--border-color-base,#a2a9b1);font-size:88%;line-height:1.25em;background-color:var(--background-color-interactive-subtle,#f8f9fa);color:inherit;display:flow-root}.mw-parser-output .infobox .side-box{font-size:100%}.mw-parser-output .side-box-abovebelow,.mw-parser-output .side-box-text{padding:0.25em 0.9em}.mw-parser-output .side-box-image{padding:2px 0 2px 0.9em;text-align:center}.mw-parser-output .side-box-imageright{padding:2px 0.9em 2px 0;text-align:center}@media(min-width:500px){.mw-parser-output .side-box-flex{display:flex;align-items:center}.mw-parser-output .side-box-text{flex:1;min-width:0}}@media(min-width:640px){.mw-parser-output .side-box{width:238px}.mw-parser-output .side-box-right{clear:right;float:right;margin-left:1em}.mw-parser-output .side-box-left{margin-right:1em}}@media print{body.ns-0 .mw-parser-output .sistersitebox{display:none!important}}@media screen{html.skin-theme-clientpref-night .mw-parser-output .sistersitebox img[src\*="Wiktionary-logo-en-v2.svg"]{filter:invert(1)brightness(55%)contrast(250%)hue-rotate(180deg)}}@media screen and (prefers-color-scheme:dark){html.skin-theme-clientpref-os .mw-parser-output .sistersitebox img[src\*="Wiktionary-logo-en-v2.svg"]{filter:invert(1)brightness(55%)contrast(250%)hue-rotate(180deg)}}

.mw-parser-output .plainlist ol,.mw-parser-output .plainlist ul{line-height:inherit;list-style:none;margin:0;padding:0}.mw-parser-output .plainlist ol li,.mw-parser-output .plainlist ul li{margin-bottom:0}

[![Wikimedia Commons logo](//thumb.wikimedia.org/wikipedia/en/thumb/4/4a/Commons-logo.svg/40px-Commons-logo.svg.png?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail)](/wiki/File:Commons-logo.svg)

Wikimedia Commons has media related to [Fault tree diagrams](https://commons.wikimedia.org/wiki/Category:Fault_tree_diagrams "commons:Category:Fault tree diagrams").

- [Event tree analysis](/wiki/Event_tree_analysis "Event tree analysis")
- [Failure mode and effects analysis](/wiki/Failure_mode_and_effects_analysis "Failure mode and effects analysis")
- [Ishikawa diagram](/wiki/Ishikawa_diagram "Ishikawa diagram")
- [Reliability engineering](/wiki/Reliability_engineering "Reliability engineering")
- [Root cause analysis](/wiki/Root_cause_analysis "Root cause analysis")
- [Safety engineering](/wiki/Safety_engineering "Safety engineering")
- [System safety](/wiki/System_safety "System safety")
- [Why-because analysis](/wiki/Why-because_analysis "Why-because analysis")

## External links

[[edit](/w/index.php?title=Fault_tree_analysis&veaction=edit&section=12 "Edit section: External links") | [edit source](/w/index.php?title=Fault_tree_analysis&action=edit&section=12 "Edit section's source code: External links")]

- [KUREAS](https://github.com/curtlsmith/KUREAS) - Open source software for event and fault tree analysis
- [Visual-XSel](https://crgraph.de/en/Fault-Tree-Analysis) - Commercial tool for fault tree Analysis
- [Arbre Analyste](https://www.arbre-analyste.fr/en.html) - Free software for fault tree Analysis
- [ITEM TOOLkit](http://www.itemsoft.com/fault_tree.html) - Commercial tool for fault tree Analysis

## References

[[edit](/w/index.php?title=Fault_tree_analysis&veaction=edit&section=13 "Edit section: References") | [edit source](/w/index.php?title=Fault_tree_analysis&action=edit&section=13 "Edit section's source code: References")]

.mw-parser-output .reflist-columns-2{column-width:30em}.mw-parser-output .reflist-columns-3{column-width:25em}body.skin-vector-2022 .mw-parser-output .reflist-columns-2{column-width:27em}body.skin-vector-2022 .mw-parser-output .reflist-columns-3{column-width:22.5em}.mw-parser-output .references[data-mw-group=upper-alpha]{list-style-type:upper-alpha}.mw-parser-output .references[data-mw-group=upper-roman]{list-style-type:upper-roman}.mw-parser-output .references[data-mw-group=lower-alpha]{list-style-type:lower-alpha}.mw-parser-output .references[data-mw-group=lower-greek]{list-style-type:lower-greek}.mw-parser-output .references[data-mw-group=lower-roman]{list-style-type:lower-roman}.mw-parser-output div.reflist-liststyle-upper-alpha .references{list-style-type:upper-alpha}.mw-parser-output div.reflist-liststyle-upper-roman .references{list-style-type:upper-roman}.mw-parser-output div.reflist-liststyle-lower-alpha .references{list-style-type:lower-alpha}.mw-parser-output div.reflist-liststyle-lower-greek .references{list-style-type:lower-greek}.mw-parser-output div.reflist-liststyle-lower-roman .references{list-style-type:lower-roman}

1. **[^](#cite_ref-NASA_SE_Toolbox_1-0)** .mw-parser-output cite.citation{font-style:inherit;word-wrap:break-word}.mw-parser-output .citation q{quotes:"\"""\"""'""'"}.mw-parser-output .citation:target{background-color:rgba(0,127,255,0.133)}.mw-parser-output .id-lock-free.id-lock-free a{background:url("//upload.wikimedia.org/wikipedia/commons/6/65/Lock-green.svg")right 0.1em center/9px no-repeat}.mw-parser-output .id-lock-limited.id-lock-limited a,.mw-parser-output .id-lock-registration.id-lock-registration a{background:url("//upload.wikimedia.org/wikipedia/commons/d/d6/Lock-gray-alt-2.svg")right 0.1em center/9px no-repeat}.mw-parser-output .id-lock-subscription.id-lock-subscription a{background:url("//upload.wikimedia.org/wikipedia/commons/a/aa/Lock-red-alt-2.svg")right 0.1em center/9px no-repeat}.mw-parser-output .cs1-ws-icon a{background:url("//upload.wikimedia.org/wikipedia/commons/4/4c/Wikisource-logo.svg")right 0.1em center/12px no-repeat}body:not(.skin-timeless):not(.skin-minerva) .mw-parser-output .id-lock-free a,body:not(.skin-timeless):not(.skin-minerva) .mw-parser-output .id-lock-limited a,body:not(.skin-timeless):not(.skin-minerva) .mw-parser-output .id-lock-registration a,body:not(.skin-timeless):not(.skin-minerva) .mw-parser-output .id-lock-subscription a,body:not(.skin-timeless):not(.skin-minerva) .mw-parser-output .cs1-ws-icon a{background-size:contain;padding:0 1em 0 0}.mw-parser-output .cs1-code{color:inherit;background:inherit;border:none;padding:inherit}.mw-parser-output .cs1-hidden-error{display:none;color:var(--color-error,#bf3c2c)}.mw-parser-output .cs1-visible-error{color:var(--color-error,#bf3c2c)}.mw-parser-output .cs1-maint{display:none;color:#085;margin-left:0.3em}.mw-parser-output .cs1-kern-left{padding-left:0.2em}.mw-parser-output .cs1-kern-right{padding-right:0.2em}.mw-parser-output .citation .mw-selflink{font-weight:inherit}@media screen{.mw-parser-output .cs1-format{font-size:95%}html.skin-theme-clientpref-night .mw-parser-output .cs1-maint{color:#18911f}}@media screen and (prefers-color-scheme:dark){html.skin-theme-clientpref-os .mw-parser-output .cs1-maint{color:#18911f}}Goldberg, B. E.; Everhart, K.; Stevens, R.; Babbitt, N.; Clemens, P.; Stout, L. (1994). ["3"](https://ntrs.nasa.gov/search.jsp?R=19950012517). *System engineering toolbox for design-oriented engineers*. Marshall Space Flight Center. pp. 3–35 to 3–48.`{{cite book}}`: CS1 maint: location missing publisher ([link](/wiki/Category:CS1_maint:_location_missing_publisher "Category:CS1 maint: location missing publisher"))
2. **[^](#cite_ref-2)** Center for Chemical Process Safety (April 2008). [*Guidelines for Hazard Evaluation Procedures*](http://www.aiche.org/ccps/publications/books/guidelines-hazard-evaluation-procedures-3rd-edition) (3rd ed.). Wiley. [ISBN](/wiki/ISBN_(identifier) "ISBN (identifier)") [978-0-471-97815-2](/wiki/Special:BookSources/978-0-471-97815-2 "Special:BookSources/978-0-471-97815-2").
3. **[^](#cite_ref-3)** Center for Chemical Process Safety (October 1999). [*Guidelines for Chemical Process Quantitative Risk Analysis*](http://www.aiche.org/ccps/publications/books/guidelines-chemical-process-quantitative-risk-analysis-2nd-edition) (2nd ed.). American Institute of Chemical Engineers. [ISBN](/wiki/ISBN_(identifier) "ISBN (identifier)") [978-0-8169-0720-5](/wiki/Special:BookSources/978-0-8169-0720-5 "Special:BookSources/978-0-8169-0720-5").
4. **[^](#cite_ref-4)** U.S. Department of Labor Occupational Safety and Health Administration (1994). [*Process Safety Management Guidelines for Compliance*](https://www.osha.gov/Publications/osha3133.pdf) (PDF). U.S. Government Printing Office. OSHA 3133.
5. **[^](#cite_ref-5)** ICH Harmonised Tripartite Guidelines. Quality Guidelines (January 2006). [*Q9 Quality Risk Management*](http://www.ich.org/fileadmin/Public_Web_Site/ICH_Products/Guidelines/Quality/Q9/Step4/Q9_Guideline.pdf).
6. **[^](#cite_ref-6)** Lacey, Peter (2011). "An Application of Fault Tree Analysis to the Identification and Management of Risks in Government Funded Human Service Delivery". *Proceedings of the 2nd International Conference on Public Policy and Social Sciences*. [SSRN](/wiki/SSRN_(identifier) "SSRN (identifier)") [2171117](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2171117).
7. **[^](#cite_ref-7)** ["Fault Tree Explanation"](https://ftvisualisations.wixsite.com/ftvisualisations/fault-tree-information). *ftvisualisations*. Retrieved 2024-05-31.
8. **[^](#cite_ref-8)** ["Projects"](https://ftvisualisations.wixsite.com/ftvisualisations/projects-1). *ftvisualisations*. Retrieved 2024-05-31.
9. **[^](#cite_ref-9)** Ericson, Clifton (1999). ["Fault Tree Analysis - A History"](https://web.archive.org/web/20110723124816/http://www.fault-tree.net/papers/ericson-fta-history.pdf) (PDF). *Proceedings of the 17th International Systems Safety Conference*. Archived from [the original](http://www.fault-tree.net/papers/ericson-fta-history.pdf) (PDF) on 2011-07-23. Retrieved 2010-01-17.
10. **[^](#cite_ref-10)** Rechard, Robert P. (1999). ["Historical Relationship Between Performance Assessment for Radioactive Waste Disposal and Other Types of Risk Assessment in the United States"](https://www.osti.gov/bridge/servlets/purl/759847-JsFRIG/webviewable/) (pdf). *Risk Analysis*. **19** (5): 763–807. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1023/A:1007058325258](https://doi.org/10.1023%2FA%3A1007058325258). [PMID](/wiki/PMID_(identifier) "PMID (identifier)") [10765434](https://pubmed.ncbi.nlm.nih.gov/10765434). [S2CID](/wiki/S2CID_(identifier) "S2CID (identifier)") [704496](https://api.semanticscholar.org/CorpusID:704496). SAND99-1147J. Retrieved 2010-01-22.
11. **[^](#cite_ref-11)** Winter, Mathias (1995). ["Software Fault Tree Analysis of an Automated Control System Device Written in ADA"](https://web.archive.org/web/20120515221443/http://handle.dtic.mil/100.2/ADA303377). *Master's Thesis*. ADA303377. Archived from [the original](http://handle.dtic.mil/100.2/ADA303377) (pdf) on May 15, 2012. Retrieved 2010-01-17.
12. **[^](#cite_ref-12)** Benner, Ludwig (1975). ["Accident Theory and Accident Investigation"](https://web.archive.org/web/20010306205651/http://www.iprr.org/Papers/75iasiatheory.html). *Proceedings of the Society of Air Safety Investigators Annual Seminar*. Archived from the original on March 6, 2001. Retrieved 2010-01-17.
13. **[^](#cite_ref-13)** Martensen, Anna L.; Butler, Ricky W. (January 1987). ["The Fault-Tree Compiler"](https://ntrs.nasa.gov/search.jsp?R=19870011332). *Langely Research Center*. NTRS. Retrieved June 17, 2011.
14. **[^](#cite_ref-14)** DeLong, Thomas (1970). ["A Fault Tree Manual"](https://web.archive.org/web/20160304031008/http://www.dtic.mil/get-tr-doc/pdf?AD=AD0739001). *Master's Thesis*. AD739001. Archived from [the original](http://www.dtic.mil/get-tr-doc/pdf?AD=AD0739001) (pdf) on March 4, 2016. Retrieved 2014-05-18.
15. **[^](#cite_ref-15)** Eckberg, C. R. (1964). [*WS-133B Fault Tree Analysis Program Plan*](https://web.archive.org/web/20160303225811/http://www.dtic.mil/get-tr-doc/pdf?AD=AD0299561). Seattle, WA: The Boeing Company. D2-30207-1. Archived from [the original](http://www.dtic.mil/get-tr-doc/pdf?AD=AD0299561) on March 3, 2016. Retrieved 2014-05-18.
16. **[^](#cite_ref-16)** Hixenbaugh, A. F. (1968). [*Fault Tree for Safety*](https://web.archive.org/web/20160303224602/http://www.dtic.mil/get-tr-doc/pdf?AD=AD0847015). Seattle, WA: The Boeing Company. D6-53604. Archived from [the original](http://www.dtic.mil/get-tr-doc/pdf?AD=AD0847015) on March 3, 2016. Retrieved 2014-05-18.
17. **[^](#cite_ref-17)** Larsen, Waldemar (January 1974). [*Fault Tree Analysis*](https://web.archive.org/web/20140518022301/http://www.dtic.mil/get-tr-doc/pdf?AD=AD0774843). Picatinny Arsenal. Technical Report 4556. Archived from [the original](http://www.dtic.mil/get-tr-doc/pdf?AD=AD0774843) on May 18, 2014. Retrieved 2014-05-17.
18. **[^](#cite_ref-18)** Evans, Ralph A. (January 5, 1976). [*Engineering Design Handbook Design for Reliability*](http://apps.dtic.mil/dtic/tr/fulltext/u2/a027370.pdf) (PDF). US Army Materiel Command. AMCP-706-196. [Archived](https://web.archive.org/web/20140518022549/http://www.dtic.mil/dtic/tr/fulltext/u2/a027370.pdf) (PDF) from the original on May 18, 2014. Retrieved 2014-05-17.
19. **[^](#cite_ref-19)** ["DSIAC – Defense Systems Information Analysis Center"](https://dsiac.org/). Retrieved 2023-03-25.
20. **[^](#cite_ref-20)** Begley, T. F.; Cummings (1968). *Fault Tree for Safety*. RAC. ADD874448.
21. **[^](#cite_ref-21)** Anderson, R. T. (March 1976). [*Reliability Design Handbook*](https://apps.dtic.mil/sti/pdfs/ADA024601.pdf) (PDF). Reliability Analysis Center. RDH 376. [Archived](https://web.archive.org/web/20140518020425/http://www.dtic.mil/get-tr-doc/pdf?AD=ADA024601) from the original on May 18, 2014. Retrieved 2014-05-17.
22. **[^](#cite_ref-22)** Mahar, David J.; James W. Wilbur (1990). *Fault Tree Analysis Application Guide*. Reliability Analysis Center.
23. **[^](#cite_ref-23)** "7.9 Fault Tree Analysis". [*Electronic Reliability Design Handbook*](http://www.everyspec.com/MIL-HDBK/MIL-HDBK-0300-0499/MIL-HDBK-338B_15041/) (pdf). B. [U.S. Department of Defense](/wiki/United_States_Department_of_Defense "United States Department of Defense"). 1998. MIL–HDBK–338B. Retrieved 2010-01-17.
24. **[^](#cite_ref-24)** ASY-300 (June 26, 1998). [*Safety Risk Management*](http://www.faa.gov/documentLibrary/media/directives/ND/ND8040-4.pdf) (PDF). Federal Aviation Administration. 8040.4.`{{cite book}}`: CS1 maint: numeric names: authors list ([link](/wiki/Category:CS1_maint:_numeric_names:_authors_list "Category:CS1 maint: numeric names: authors list"))
25. **[^](#cite_ref-25)** FAA (December 30, 2000). [*System Safety Handbook*](http://www.faa.gov/regulations_policies/handbooks_manuals/aviation/risk_management/ss_handbook/). Federal Aviation Administration.
26. ^ [***a***](#cite_ref-fthbaa_26-0) [***b***](#cite_ref-fthbaa_26-1) [***c***](#cite_ref-fthbaa_26-2) Vesely, William; et al. (2002). [*Fault Tree Handbook with Aerospace Applications*](https://web.archive.org/web/20161228133244/https://elibrary.gsfc.nasa.gov/_assets/doclibBidder/tech_docs/25.%20NASA_Fault_Tree_Handbook_with_Aerospace_Applications%20-%20Copy.pdf) (PDF). [National Aeronautics and Space Administration](/wiki/NASA "NASA"). Archived from [the original](https://elibrary.gsfc.nasa.gov/_assets/doclibBidder/tech_docs/25.%20NASA_Fault_Tree_Handbook_with_Aerospace_Applications%20-%20Copy.pdf) (PDF) on 2016-12-28. Retrieved 2018-07-16. ![Public Domain](//thumb.wikimedia.org/wikipedia/en/thumb/6/62/PD-icon.svg/20px-PD-icon.svg.png?utm_source=en.wikipedia.org&utm_campaign=parser&utm_content=thumbnail) This article incorporates text from this source, which is in the [public domain](/wiki/Public_domain "Public domain").
27. **[^](#cite_ref-27)** Acharya, Sarbes; et al. (1990). [*Severe Accident Risks: An Assessment for Five U.S. Nuclear Power Plants*](https://www.nrc.gov/reading-rm/doc-collections/nuregs/staff/sr1150/v1/sr1150v1-intro-and-part-1.pdf) (PDF). Wasthington, DC: U.S. [Nuclear Regulatory Commission](/wiki/Nuclear_Regulatory_Commission "Nuclear Regulatory Commission"). NUREG–1150. Retrieved 2010-01-17.
28. **[^](#cite_ref-28)** Vesely, W. E.; et al. (1981). [*Fault Tree Handbook*](https://www.nrc.gov/reading-rm/doc-collections/nuregs/staff/sr0492/sr0492.pdf) (PDF). [Nuclear Regulatory Commission](/wiki/Nuclear_Regulatory_Commission "Nuclear Regulatory Commission"). NUREG–0492. Retrieved 2010-01-17.
29. **[^](#cite_ref-29)** Elke, Holly C., [*Global Application of the Process Safety Management Standard*](http://www.asse.org/assets/1/7/Holly_Elke_Article.pdf) (PDF)
30. **[^](#cite_ref-30)** *Fault Tree Analysis*. Edition 2.0. [International Electrotechnical Commission](/wiki/International_Electrotechnical_Commission "International Electrotechnical Commission"). 2006. [ISBN](/wiki/ISBN_(identifier) "ISBN (identifier)") [978-2-8318-8918-4](/wiki/Special:BookSources/978-2-8318-8918-4 "Special:BookSources/978-2-8318-8918-4"). IEC 61025.
31. **[^](#cite_ref-31)** ["SCRAM 0.11.4 — SCRAM 0.11.4 documentation"](https://web.archive.org/web/20161123011255/https://scram-pra.org/). *scram-pra.org*. Archived from [the original](https://scram-pra.org/) on 23 November 2016. Retrieved 13 January 2022.
32. **[^](#cite_ref-32)** ["The Open-PSA Model Exchange Format — The Open-PSA Model Exchange Format 2.0"](https://open-psa.github.io/mef/). *open-psa.github.io*.
33. **[^](#cite_ref-33)** Olofsson and Andersson, Probability, Statistics and Stochastic Processes, John Wiley and Sons, 2011.
34. **[^](#cite_ref-34)** Ruijters, Enno; Stoelinga, Mariëlle I. A. (February–May 2015). ["Fault tree analysis: A survey of the state-of-the-art in modeling, analysis and tools"](https://research.utwente.nl/en/publications/fault-tree-analysis-a-survey-of-the-stateoftheart-in-modeling-analysis-and-tools(88c7ba34-fe51-4f9d-b2f3-cb04aeffaa6e).html). *Computer Science Review*. 15–16: 29–62. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1016/j.cosrev.2015.03.001](https://doi.org/10.1016%2Fj.cosrev.2015.03.001).
35. **[^](#cite_ref-35)** Long, Allen, [*Beauty & the Beast – Use and Abuse of Fault Tree as a Tool*](https://web.archive.org/web/20090419200036/http://www.fault-tree.net/papers/long-beauty-and-beast.pdf) (PDF), fault-tree.net, archived from [the original](http://www.fault-tree.net/papers/long-beauty-and-beast.pdf) (PDF) on 19 April 2009, retrieved 16 January 2010
