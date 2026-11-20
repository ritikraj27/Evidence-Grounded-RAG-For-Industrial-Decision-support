<!-- category: supply_chain_management -->
# Economic order quantity

Production scheduling model

**Economic order quantity** (**EOQ**), also known as **financial purchase quantity** or **economic buying quantity**,[*[citation needed](/wiki/Wikipedia:Citation_needed "Wikipedia:Citation needed")*] is the order quantity that minimizes the total [holding costs](/wiki/Holding_cost "Holding cost") and [ordering costs](/w/index.php?title=Ordering_cost&action=edit&redlink=1 "Ordering cost (page does not exist)") in [inventory management](/wiki/Field_inventory_management "Field inventory management"). It is one of the oldest classical [production scheduling](/wiki/Scheduling_(production_processes) "Scheduling (production processes)") models. The model was developed by [Ford W. Harris](/wiki/Ford_W._Harris "Ford W. Harris") in 1913, but the consultant R. H. Wilson applied it extensively, and he and K. Andler are given credit for their in-depth analysis.[[1]](#cite_note-Hax1984-1)

## Overview

[[edit](/w/index.php?title=Economic_order_quantity&veaction=edit&section=1 "Edit section: Overview") | [edit source](/w/index.php?title=Economic_order_quantity&action=edit&section=1 "Edit section's source code: Overview")]

The EOQ indicates the optimal number of units to order to minimize the total cost associated with the purchase, delivery, and storage of a product.

EOQ applies only when [demand](/wiki/Demand "Demand") for a product is constant over a period of time (such as a year) and each new order is delivered in full when inventory reaches zero. There is a [fixed cost](/wiki/Fixed_cost "Fixed cost") for each order placed, regardless of the quantity of items ordered; an order is assumed to contain only one type of inventory item. There is also a cost for each unit held in storage, commonly known as [holding cost](/wiki/Holding_cost "Holding cost"), sometimes expressed as a percentage of the purchase cost of the item. Although the EOQ formulation is straightforward, factors such as transportation rates and quantity discounts factor into its real-world application.

The required parameters to the solution are the total demand for the year, the purchase cost for each item, the fixed cost to place the order for a single item and the storage cost for each item per year. Note that the number of times an order is placed will also affect the total cost, though this number can be determined from the other parameters.

### Variables

[[edit](/w/index.php?title=Economic_order_quantity&veaction=edit&section=2 "Edit section: Variables") | [edit source](/w/index.php?title=Economic_order_quantity&action=edit&section=2 "Edit section's source code: Variables")]

- T
  {\displaystyle T}
  ![{\displaystyle T}](https://wikimedia.org/api/rest_v1/media/math/render/svg/ec7200acd984a1d3a3d7dc455e262fbe54f7f6e0) = total annual inventory cost
- P
  {\displaystyle P}
  ![{\displaystyle P}](https://wikimedia.org/api/rest_v1/media/math/render/svg/b4dc73bf40314945ff376bd363916a738548d40a) = purchase [unit price](/wiki/Unit_price "Unit price"), unit production cost
- Q
  {\displaystyle Q}
  ![{\displaystyle Q}](https://wikimedia.org/api/rest_v1/media/math/render/svg/8752c7023b4b3286800fe3238271bbca681219ed) = order quantity
- Q

  ∗
  {\displaystyle Q^{\*}}
  ![{\displaystyle Q^{*}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/c1785c0a77ab5a06684e8a7ac4f5e59d59ec0319) = optimal order quantity
- D
  {\displaystyle D}
  ![{\displaystyle D}](https://wikimedia.org/api/rest_v1/media/math/render/svg/f34a0c600395e5d4345287e21fb26efd386990e6) = annual demand quantity
- K
  {\displaystyle K}
  ![{\displaystyle K}](https://wikimedia.org/api/rest_v1/media/math/render/svg/2b76fce82a62ed5461908f0dc8f037de4e3686b0) = fixed cost per order, setup cost (*not* per unit, typically cost of ordering and shipping and handling. This is not the cost of goods)
- h
  {\displaystyle h}
  ![{\displaystyle h}](https://wikimedia.org/api/rest_v1/media/math/render/svg/b26be3e694314bc90c3215047e4a2010c6ee184a) = annual holding cost per unit, also known as carrying cost or storage cost ([capital cost](/wiki/Capital_cost "Capital cost"), warehouse space, [refrigeration](/wiki/Refrigeration "Refrigeration"), [insurance](/wiki/Insurance "Insurance"), [opportunity cost](/wiki/Opportunity_cost "Opportunity cost") (price x interest), etc. usually not related to the unit production cost)

### Total cost function and derivation of EOQ formula

[[edit](/w/index.php?title=Economic_order_quantity&veaction=edit&section=3 "Edit section: Total cost function and derivation of EOQ formula") | [edit source](/w/index.php?title=Economic_order_quantity&action=edit&section=3 "Edit section's source code: Total cost function and derivation of EOQ formula")]

The single-item EOQ formula finds the minimum point of the following cost function:

Total Cost = purchase cost or production cost + ordering cost + holding cost

Where:

- Purchase cost: This is the [variable cost](/wiki/Variable_cost "Variable cost") of goods: purchase unit price × annual demand quantity. This is 

  P
  ×
  D
  {\displaystyle P\times D}
  ![{\displaystyle P\times D}](https://wikimedia.org/api/rest_v1/media/math/render/svg/67dc7fb6890d56d29a21a7cb5be572e6c0da1b96).
- Ordering cost: This is the cost of placing orders: each order has a fixed cost 

  K
  {\displaystyle K}
  ![{\displaystyle K}](https://wikimedia.org/api/rest_v1/media/math/render/svg/2b76fce82a62ed5461908f0dc8f037de4e3686b0), and we need to order 

  D

  /
  Q
  {\displaystyle D/Q}
  ![{\displaystyle D/Q}](https://wikimedia.org/api/rest_v1/media/math/render/svg/c3ed0077fd4b0860f275d2b183e1994c20dadf0d) times per year. This is 

  K
  D

  /
  Q
  {\displaystyle KD/Q}
  ![{\displaystyle KD/Q}](https://wikimedia.org/api/rest_v1/media/math/render/svg/daf04b2745c5bf0871ac220a1227ab3c7da5cbbb)
- Holding cost: the average quantity in stock (between fully replenished and empty) is 

  Q

  /
  2
  {\displaystyle Q/2}
  ![{\displaystyle Q/2}](https://wikimedia.org/api/rest_v1/media/math/render/svg/e13f2a911be9da48d0ae563484bad6ed3d0782fe), so this cost is 

  h
  Q

  /
  2
  {\displaystyle hQ/2}
  ![{\displaystyle hQ/2}](https://wikimedia.org/api/rest_v1/media/math/render/svg/38c56a6a4167d812e1a945f3924de528adadb78b)

:   T
    =
    P
    D
    +
    K

    D
    Q
    +
    h

    Q
    2
    {\displaystyle T=PD+K{\frac {D}{Q}}+h{\frac {Q}{2}}}
    ![{\displaystyle T=PD+K{\frac {D}{Q}}+h{\frac {Q}{2}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/29a3ec480346f66fc61dd434a1eb0b93c86b919c).

To determine the minimum point of the total [cost curve](/wiki/Cost_curve "Cost curve"), calculate the [derivative](/wiki/Derivative "Derivative") of the total cost with respect to Q (assume all other variables are constant) and set it equal to 0:

:   0
    =
    −

    D
    K

    Q

    2
    +

    h
    2
    {\displaystyle {0}=-{\frac {DK}{Q^{2}}}+{\frac {h}{2}}}
    ![{\displaystyle {0}=-{\frac {DK}{Q^{2}}}+{\frac {h}{2}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/96c840baed6e9520d6d6f9cfdb897ffc8ea0e8ff)

Solving for Q gives Q\* (the optimal order quantity):

:   Q

    ∗
    2
    =

    2
    D
    K
    h
    {\displaystyle Q^{\*2}={\frac {2DK}{h}}}
    ![{\displaystyle Q^{*2}={\frac {2DK}{h}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/f81cc64ababc27147b3fbf8db5efa4fb2976e59b)

Therefore:

**Economic Order Quantity**

Q

∗
=

2
D
K
h
{\displaystyle Q^{\*}={\sqrt {\frac {2DK}{h}}}}
![{\displaystyle Q^{*}={\sqrt {\frac {2DK}{h}}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/7d7c52b45e0bc4b8b9bca91916257130abc9326b)

Q\* is independent of P; it is a function of only K, D, h.

The optimal value Q\* may also be found by recognizing that

:   T
    =

    D
    K
    Q
    +

    h
    Q
    2
    +
    P
    D
    =

    h

    2
    Q
    (
    Q
    −

    2
    D
    K

    /
    h

    )

    2
    +

    2
    h
    D
    K
    +
    P
    D
    ,
    {\displaystyle T={\frac {DK}{Q}}+{\frac {hQ}{2}}+PD={\frac {h}{2Q}}(Q-{\sqrt {2DK/h}})^{2}+{\sqrt {2hDK}}+PD,}
    ![{\displaystyle T={\frac {DK}{Q}}+{\frac {hQ}{2}}+PD={\frac {h}{2Q}}(Q-{\sqrt {2DK/h}})^{2}+{\sqrt {2hDK}}+PD,}](https://wikimedia.org/api/rest_v1/media/math/render/svg/f2c85dfb5c5b46403a1c35d5bc35edbe28811cf9)

where the non-negative quadratic term disappears for 

Q
=

2
D
K

/
h
,
{\textstyle Q={\sqrt {2DK/h}},}
![{\textstyle Q={\sqrt {2DK/h}},}](https://wikimedia.org/api/rest_v1/media/math/render/svg/e862e95c6977c7bc676321740ddabc7d79721aaf) which provides the cost minimum 

T

m
i
n
=

2
h
D
K
+
P
D
.
{\displaystyle T\_{min}={\sqrt {2hDK}}+PD.}
![{\displaystyle T_{min}={\sqrt {2hDK}}+PD.}](https://wikimedia.org/api/rest_v1/media/math/render/svg/ab51da2bdea7ff942858c9a759093ec4e02dd047)

### Example

[[edit](/w/index.php?title=Economic_order_quantity&veaction=edit&section=4 "Edit section: Example") | [edit source](/w/index.php?title=Economic_order_quantity&action=edit&section=4 "Edit section's source code: Example")]

- Annual requirement quantity (D) = 10000 units
- Cost per order (K) = 40
- Cost per unit (P) = 50
- Yearly carrying cost per unit = 4
- Market interest = 2%

Economic order quantity = 

2
D
⋅
K
h
{\displaystyle {\sqrt {\frac {2D\cdot K}{h}}}}
![{\displaystyle {\sqrt {\frac {2D\cdot K}{h}}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/c443ae1535cfbbf813f1ce6f6dd9b3de9299e426) 

=

2
⋅
10000
⋅
40

4
+
50
⋅
2
%
=

2
⋅
10000
⋅
40
5
{\displaystyle ={\sqrt {\frac {2\cdot 10000\cdot 40}{4+50\cdot 2\%}}}={\sqrt {\frac {2\cdot 10000\cdot 40}{5}}}}
![{\displaystyle ={\sqrt {\frac {2\cdot 10000\cdot 40}{4+50\cdot 2\%}}}={\sqrt {\frac {2\cdot 10000\cdot 40}{5}}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/668fe2da1d901611cdd2d6cb05eb5ef4d24237cf) = 400 units

Number of orders per year (based on EOQ) 

=

10000
400
=
25
{\displaystyle ={\frac {10000}{400}}=25}
![{\displaystyle ={\frac {10000}{400}}=25}](https://wikimedia.org/api/rest_v1/media/math/render/svg/ffd862119bebcb04a0c1bfed5de2c237d3cffa07)

Total cost 

=
P
⋅
D
+
K
(
D

/
E
O
Q
)
+
h
(
E
O
Q

/
2
)
{\displaystyle =P\cdot D+K(D/EOQ)+h(EOQ/2)}
![{\displaystyle =P\cdot D+K(D/EOQ)+h(EOQ/2)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/445e1918311c91d4a90fad5da1a1bbe036e6acaa)

Total cost 

=
50
⋅
10000
+
40
⋅
(
10000

/
400
)
+
5
⋅
(
400

/
2
)
=
502000
{\displaystyle =50\cdot 10000+40\cdot (10000/400)+5\cdot (400/2)=502000}
![{\displaystyle =50\cdot 10000+40\cdot (10000/400)+5\cdot (400/2)=502000}](https://wikimedia.org/api/rest_v1/media/math/render/svg/2bf0bff0d3836408d25dda53517fe62988a417ba)

If we check the total cost for any order quantity other than 400(=EOQ), we will see that the cost is higher. For instance, supposing 500 units per order, then

Total cost 

=
50
⋅
10000
+
40
⋅
(
10000

/
500
)
+
5
⋅
(
500

/
2
)
=
502050
{\displaystyle =50\cdot 10000+40\cdot (10000/500)+5\cdot (500/2)=502050}
![{\displaystyle =50\cdot 10000+40\cdot (10000/500)+5\cdot (500/2)=502050}](https://wikimedia.org/api/rest_v1/media/math/render/svg/412dd6079f485e5b2baf9bd31640b7f0ca038fdb)

Similarly, if we choose 300 for the order quantity, then

Total cost 

=
50
⋅
10000
+
40
⋅
(
10000

/
300
)
+
5
⋅
(
300

/
2
)
=
502083.33
{\displaystyle =50\cdot 10000+40\cdot (10000/300)+5\cdot (300/2)=502083.33}
![{\displaystyle =50\cdot 10000+40\cdot (10000/300)+5\cdot (300/2)=502083.33}](https://wikimedia.org/api/rest_v1/media/math/render/svg/21c7a4fc71488278c96206bfe09463fc4648e466)

This illustrates that the economic order quantity is always in the best interests of the firm.

## Extensions

[[edit](/w/index.php?title=Economic_order_quantity&veaction=edit&section=5 "Edit section: Extensions") | [edit source](/w/index.php?title=Economic_order_quantity&action=edit&section=5 "Edit section's source code: Extensions")]

### Quantity discounts

[[edit](/w/index.php?title=Economic_order_quantity&veaction=edit&section=6 "Edit section: Quantity discounts") | [edit source](/w/index.php?title=Economic_order_quantity&action=edit&section=6 "Edit section's source code: Quantity discounts")]

An important extension to the EOQ model is to accommodate quantity discounts. There are two main types of quantity discounts: (1) all-units and (2) incremental.[[2]](#cite_note-2)[[3]](#cite_note-3) Here is a numerical example:

- Incremental unit discount: Units 1–100 cost $30 each; Units 101–199 cost $28 each; Units 200 and up cost $26 each. So when 150 units are ordered, the total cost is $30\*100 + $28\*50.
- All units discount: an order of 1–1000 units costs $50 each; an order of 1001–5000 units costs $45 each; an order of more than 5000 units costs $40 each. So when 1500 units are ordered, the total cost is $45\*1500.

In order to find the optimal order quantity under different quantity discount schemes, one should use algorithms; these algorithms are developed under the assumption that the EOQ policy is still optimal with quantity discounts. Perera et al. (2017)[[4]](#cite_note-4) establish this optimality and fully characterize the (s,S) optimality within the EOQ setting under general cost structures.

### Design of optimal quantity discount schedules

[[edit](/w/index.php?title=Economic_order_quantity&veaction=edit&section=7 "Edit section: Design of optimal quantity discount schedules") | [edit source](/w/index.php?title=Economic_order_quantity&action=edit&section=7 "Edit section's source code: Design of optimal quantity discount schedules")]

In presence of a strategic customer, who responds optimally to discount schedules, the design of an optimal quantity discount scheme by the supplier is complex and has to be done carefully. This is particularly so when the demand at the customer is itself uncertain. An interesting effect called the "reverse bullwhip" takes place where an increase in consumer demand uncertainty actually reduces order quantity uncertainty at the supplier.[[5]](#cite_note-5)

### Backordering costs and multiple items

[[edit](/w/index.php?title=Economic_order_quantity&veaction=edit&section=8 "Edit section: Backordering costs and multiple items") | [edit source](/w/index.php?title=Economic_order_quantity&action=edit&section=8 "Edit section's source code: Backordering costs and multiple items")]

Several extensions can be made to the EOQ model, including backordering costs[[6]](#cite_note-6) and multiple items. In the case backorders are permitted, the inventory carrying costs per cycle are:[[7]](#cite_note-7)

:   I
    C

    ∫

    0

    T

    1
    (
    Q
    −
    s
    −
    λ
    t
    )

    d
    t
    =

    I
    C

    2
    λ
    (
    Q
    −
    s

    )

    2
    ,
    {\displaystyle IC\int \limits \_{0}^{T\_{1}}(Q-s-\lambda t)\,dt={\frac {IC}{2\lambda }}(Q-s)^{2},}
    ![{\displaystyle IC\int \limits _{0}^{T_{1}}(Q-s-\lambda t)\,dt={\frac {IC}{2\lambda }}(Q-s)^{2},}](https://wikimedia.org/api/rest_v1/media/math/render/svg/72c3b3a979a6559b5ac266cb9ec24630ae90dd5d)

where s is the number of backorders when order quantity Q is delivered and 

λ
{\displaystyle \lambda }
![{\displaystyle \lambda }](https://wikimedia.org/api/rest_v1/media/math/render/svg/b43d0ea3c9c025af1be9128e62a18fa74bedda2a) is the rate of demand. The backorder cost per cycle is:

:   π
    s
    +

    π
    ^

    ∫

    0

    T

    2
    λ
    t
    d
    t
    =
    π
    s
    +

    1
    2

    π
    ^
    λ

    T

    2

    2
    =
    π
    s
    +

    π
    ^

    s

    2

    2
    λ
    ,
    {\displaystyle \pi s+{\hat {\pi }}\int \limits \_{0}^{T\_{2}}\lambda tdt=\pi s+{\frac {1}{2}}{\hat {\pi }}\lambda T\_{2}^{2}=\pi s+{\frac {{\hat {\pi }}s^{2}}{2\lambda }},}
    ![{\displaystyle \pi s+{\hat {\pi }}\int \limits _{0}^{T_{2}}\lambda tdt=\pi s+{\frac {1}{2}}{\hat {\pi }}\lambda T_{2}^{2}=\pi s+{\frac {{\hat {\pi }}s^{2}}{2\lambda }},}](https://wikimedia.org/api/rest_v1/media/math/render/svg/6a0675a5b04c4195cb64105fc36c33ab02dfbad9)

where 

π
{\displaystyle \pi }
![{\displaystyle \pi }](https://wikimedia.org/api/rest_v1/media/math/render/svg/9be4ba0bb8df3af72e90a0535fabcc17431e540a) and 

π
^
{\displaystyle {\hat {\pi }}}
![{\displaystyle {\hat {\pi }}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/58f394f42d26b28d8b03bc0303150cb477616cbf) are backorder costs, 

T

2
=
T
−

T

1
{\displaystyle T\_{2}=T-T\_{1}}
![{\displaystyle T_{2}=T-T_{1}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/688e156e72cad1f73878093dcbcda11657bce960), T being the cycle length and 

T

1
=
(
Q
−
s
)

/
λ
{\displaystyle T\_{1}=(Q-s)/\lambda }
![{\displaystyle T_{1}=(Q-s)/\lambda }](https://wikimedia.org/api/rest_v1/media/math/render/svg/35d85a0a209cb6253f86dab47c74f45dad23217f). The average annual variable cost is the sum of order costs, holding inventory costs and backorder costs:

:   K
    =

    λ
    Q
    A
    +

    1

    2
    Q
    I
    C
    (
    Q
    −
    s

    )

    2
    +

    1
    Q
    [
    π
    λ
    s
    +

    1
    2

    π
    ^

    s

    2
    ]
    {\displaystyle {\mathcal {K}}={\frac {\lambda }{Q}}A+{\frac {1}{2Q}}IC(Q-s)^{2}+{\frac {1}{Q}}[\pi \lambda s+{\frac {1}{2}}{\hat {\pi }}s^{2}]}
    ![{\displaystyle {\mathcal {K}}={\frac {\lambda }{Q}}A+{\frac {1}{2Q}}IC(Q-s)^{2}+{\frac {1}{Q}}[\pi \lambda s+{\frac {1}{2}}{\hat {\pi }}s^{2}]}](https://wikimedia.org/api/rest_v1/media/math/render/svg/11559846b39de6384880cc4ef33e3dbfb3c1f877)

To minimize 

K
{\displaystyle {\mathcal {K}}}
![{\displaystyle {\mathcal {K}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/3a70fc5d5ef4fa8ce694447bef39c1aa167a68b2) impose the [partial derivatives](/wiki/Partial_derivatives "Partial derivatives") equal to zero:

:   ∂

    K

    ∂
    Q
    =
    −

    1

    Q

    2

    [

    λ
    A
    +

    1
    2
    I
    C
    (
    Q
    −
    s

    )

    2
    +
    π
    λ
    s
    +

    1
    2

    π
    ^

    s

    2
    ]
    +

    I
    C
    Q
    (
    Q
    −
    s
    )
    =
    0
    {\displaystyle {\frac {\partial {\mathcal {K}}}{\partial Q}}=-{\frac {1}{Q^{2}}}\left[{\lambda }A+{\frac {1}{2}}IC(Q-s)^{2}+\pi \lambda s+{\frac {1}{2}}{\hat {\pi }}s^{2}\right]+{\frac {IC}{Q}}(Q-s)=0}
    ![{\displaystyle {\frac {\partial {\mathcal {K}}}{\partial Q}}=-{\frac {1}{Q^{2}}}\left[{\lambda }A+{\frac {1}{2}}IC(Q-s)^{2}+\pi \lambda s+{\frac {1}{2}}{\hat {\pi }}s^{2}\right]+{\frac {IC}{Q}}(Q-s)=0}](https://wikimedia.org/api/rest_v1/media/math/render/svg/aa7466bafb1e62c05d83300693bf480d87a39c86)
:   ∂

    K

    ∂
    s
    =
    −

    I
    C
    Q
    (
    Q
    −
    s
    )
    +

    1
    Q
    π
    λ
    +

    1
    Q

    π
    ^
    s
    =
    0
    {\displaystyle {\frac {\partial {\mathcal {K}}}{\partial s}}=-{\frac {IC}{Q}}(Q-s)+{\frac {1}{Q}}\pi \lambda +{\frac {1}{Q}}{\hat {\pi }}s=0}
    ![{\displaystyle {\frac {\partial {\mathcal {K}}}{\partial s}}=-{\frac {IC}{Q}}(Q-s)+{\frac {1}{Q}}\pi \lambda +{\frac {1}{Q}}{\hat {\pi }}s=0}](https://wikimedia.org/api/rest_v1/media/math/render/svg/7c0795e7d14bf1e6660ad9899a90d5737f104c34)

Substituting the second equation into the first gives the following [quadratic equation](/wiki/Quadratic_equation "Quadratic equation"):

:   [

    π
    ^

    2
    +

    π
    ^
    I
    C
    ]

    s

    2
    +
    2
    π

    π
    ^
    λ
    s
    +
    (
    π
    λ

    )

    2
    −
    2
    λ
    A
    I
    C
    =
    0
    {\displaystyle [{\hat {\pi }}^{2}+{\hat {\pi }}IC]s^{2}+2\pi {\hat {\pi }}\lambda s+(\pi \lambda )^{2}-2\lambda AIC=0}
    ![{\displaystyle [{\hat {\pi }}^{2}+{\hat {\pi }}IC]s^{2}+2\pi {\hat {\pi }}\lambda s+(\pi \lambda )^{2}-2\lambda AIC=0}](https://wikimedia.org/api/rest_v1/media/math/render/svg/dd5845f37fabaad3e004a198c86bb49a6b1eccfa)

If 

π
^
=
0
{\displaystyle {\hat {\pi }}=0}
![{\displaystyle {\hat {\pi }}=0}](https://wikimedia.org/api/rest_v1/media/math/render/svg/e83dba6ef80547fee2b83165d250d0aa4dc8bd9d) either s=0 or 

s
=
∞
{\displaystyle s=\infty }
![{\displaystyle s=\infty }](https://wikimedia.org/api/rest_v1/media/math/render/svg/5a7ce9f031529d64dd362c4d2d070107187edf96) is optimal. In the first case the optimal lot is given by the classic EOQ formula, in the second case an order is never placed and minimum yearly cost is given by 

π
λ
{\displaystyle \pi \lambda }
![{\displaystyle \pi \lambda }](https://wikimedia.org/api/rest_v1/media/math/render/svg/74541626df0c07894092ffc8d9240e0268d9710a). If 

π
>

2
A
I
C
λ
=
δ
{\displaystyle \pi >{\sqrt {\frac {2AIC}{\lambda }}}=\delta }
![{\displaystyle \pi >{\sqrt {\frac {2AIC}{\lambda }}}=\delta }](https://wikimedia.org/api/rest_v1/media/math/render/svg/9af687cc4885ec52ae23ee69c4032058d18235a4) or 

π
λ
>

K

w
{\displaystyle \pi \lambda >K\_{w}}
![{\displaystyle \pi \lambda >K_{w}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/1da10d6d7267224f6ef8d63943b676e167df13b7) 

s

∗
=
0
{\displaystyle s^{\*}=0}
![{\displaystyle s^{*}=0}](https://wikimedia.org/api/rest_v1/media/math/render/svg/40628aa6ccbfb3f096fd003706c37df86fbaacaa) is optimal, if 

π
<
δ
{\displaystyle \pi <\delta }
![{\displaystyle \pi <\delta }](https://wikimedia.org/api/rest_v1/media/math/render/svg/652364f262a69ab047cf66fc50b12ba27c057e89) then there shouldn't be any inventory system. If 

π
^
≠
0
{\displaystyle {\hat {\pi }}\neq 0}
![{\displaystyle {\hat {\pi }}\neq 0}](https://wikimedia.org/api/rest_v1/media/math/render/svg/527ff92cd3dd3a9db6a5e090dfbcada85d657605) solving the preceding quadratic equation yields:

:   s

    ∗
    =
    [

    π
    ^
    +
    I
    C

    ]

    −
    1

    (

    −
    π
    λ
    +

    [

    (
    2
    λ
    A
    I
    C
    )

    (

    1
    +

    I
    C

    π
    ^
    )
    −

    I
    C

    π
    ^
    (
    π
    λ

    )

    2
    ]

    1

    /
    2
    )
    {\displaystyle s^{\*}=[{\hat {\pi }}+IC]^{-1}\left(-\pi \lambda +\left[(2\lambda AIC)\left(1+{\frac {IC}{\hat {\pi }}}\right)-{\frac {IC}{\hat {\pi }}}(\pi \lambda )^{2}\right]^{1/2}\right)}
    ![{\displaystyle s^{*}=[{\hat {\pi }}+IC]^{-1}\left(-\pi \lambda +\left[(2\lambda AIC)\left(1+{\frac {IC}{\hat {\pi }}}\right)-{\frac {IC}{\hat {\pi }}}(\pi \lambda )^{2}\right]^{1/2}\right)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/3f60909cf6953fe251453c3f5ff7d8771832a510)
:   Q

    ∗
    =

    [

    π
    ^
    +
    I
    C

    π
    ^
    ]

    1

    /
    2

    [

    2
    λ
    A

    I
    C
    −

    (
    π
    λ

    )

    2

    I
    C
    (

    π
    ^
    +
    I
    C
    )
    ]

    1

    /
    2
    {\displaystyle Q^{\*}=\left[{\frac {{\hat {\pi }}+IC}{\hat {\pi }}}\right]^{1/2}\left[{\frac {2\lambda A}{IC}}-{\frac {(\pi \lambda )^{2}}{IC({\hat {\pi }}+IC)}}\right]^{1/2}}
    ![{\displaystyle Q^{*}=\left[{\frac {{\hat {\pi }}+IC}{\hat {\pi }}}\right]^{1/2}\left[{\frac {2\lambda A}{IC}}-{\frac {(\pi \lambda )^{2}}{IC({\hat {\pi }}+IC)}}\right]^{1/2}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/2791c925ddd2295f3f3eec75d64b75c34991f45f)

If there are [backorders](/wiki/Backorder "Backorder"), the reorder point is: 

r

h

∗
=
μ
−
m

Q

∗
−

s

∗
{\displaystyle r\_{h}^{\*}=\mu -mQ^{\*}-s^{\*}}
![{\displaystyle r_{h}^{*}=\mu -mQ^{*}-s^{*}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/2b12b86c1a8d3a0768ad33bb993886e26537476b); with m being the largest integer 

m
≤

τ
T
{\displaystyle m\leq {\frac {\tau }{T}}}
![{\displaystyle m\leq {\frac {\tau }{T}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/5ac50a218c1a7d60e19c9d6cca2f5cd62afda677) and μ the [lead time](/wiki/Lead_time "Lead time") demand.

Additionally, the economic order interval[[8]](#cite_note-8) can be determined from the EOQ and the [economic production quantity](/wiki/Economic_production_quantity "Economic production quantity") model (which determines the optimal production quantity) can be determined in a similar fashion.

A version of the model, the [Baumol-Tobin](/wiki/Baumol-Tobin "Baumol-Tobin") model, has also been used to determine the [money demand](/wiki/Money_demand#Inventory_models "Money demand") function, where a person's holdings of money balances can be seen in a way parallel to a firm's holdings of inventory.[[9]](#cite_note-jep-9)

[Malakooti](/wiki/Behnam_Malakooti "Behnam Malakooti") (2013)[[10]](#cite_note-10) has introduced the multi-criteria EOQ models where the criteria could be minimizing the total cost, Order quantity (inventory), and Shortages.

A version taking the time-value of money into account was developed by Trippi and Lewin.[[11]](#cite_note-tri-11)

### Imperfect quality

[[edit](/w/index.php?title=Economic_order_quantity&veaction=edit&section=9 "Edit section: Imperfect quality") | [edit source](/w/index.php?title=Economic_order_quantity&action=edit&section=9 "Edit section's source code: Imperfect quality")]

Another important extension of the EOQ model is to consider items with imperfect quality. Salameh and Jaber (2000) were the first to study the imperfect items in an EOQ model very thoroughly. They consider an inventory problem in which the demand is deterministic and there is a fraction of imperfect items in the lot and are screened by the buyer and sold by them at the end of the circle at discount price.[[12]](#cite_note-12)

## Implementation

[[edit](/w/index.php?title=Economic_order_quantity&veaction=edit&section=10 "Edit section: Implementation") | [edit source](/w/index.php?title=Economic_order_quantity&action=edit&section=10 "Edit section's source code: Implementation")]

Dave Piasecki identifies two ways in which use of an EOQ approach may be implemented:

- a [spreadsheet](/wiki/Spreadsheet "Spreadsheet") method, whereby the EOQ for each stock item is calculated and recorded manually
- entry of the EOQ formula into a new or existing inventory management system.

He suggests that a system-based implementation would be beneficial where the number of [stock-keeping units](/wiki/Stock-keeping_unit "Stock-keeping unit") is over around 2000. Annual updating of data and formulae are recommended. A hybrid system would involve downloading data into a spreadsheet for calculation purposes and then re-applying this data within the inventory system.[[13]](#cite_note-13)

## Limitations

[[edit](/w/index.php?title=Economic_order_quantity&veaction=edit&section=11 "Edit section: Limitations") | [edit source](/w/index.php?title=Economic_order_quantity&action=edit&section=11 "Edit section's source code: Limitations")]

The EOQ model and its sister, the [economic production quantity](/wiki/Economic_production_quantity "Economic production quantity") model (EPQ), have been criticised for "their restrictive set[s] of assumptions.[[14]](#cite_note-14) Guga and Musa make use of the model for an Albanian [business case](/wiki/Business_case "Business case") study and conclude that the model is "perfect theoretically, but not very suitable from the practical perspective of this firm".[[15]](#cite_note-15) However, James Cargal notes that the formula was developed when business calculations were undertaken "by hand", or using [logarithmic tables](/wiki/Logarithmic_table "Logarithmic table") or a [slide rule](/wiki/Slide_rule "Slide rule"). Use of spreadsheets and specialist software allows for more versatility in the use of the formula and adoption of "assumptions which are more realistic" than in the original model.[[16]](#cite_note-16)[*[self-published source](/wiki/Wikipedia:Verifiability#Self-published_sources "Wikipedia:Verifiability")*]

## See also

[[edit](/w/index.php?title=Economic_order_quantity&veaction=edit&section=12 "Edit section: See also") | [edit source](/w/index.php?title=Economic_order_quantity&action=edit&section=12 "Edit section's source code: See also")]

- [Reorder point](/wiki/Reorder_point "Reorder point")
- [Safety stock](/wiki/Safety_stock "Safety stock")
- [Economic production quantity](/wiki/Economic_production_quantity "Economic production quantity")
- [Newsvendor model](/wiki/Newsvendor_model "Newsvendor model")
- [Dynamic lot size model](/wiki/Dynamic_lot_size_model "Dynamic lot size model")
- [Economic lot scheduling problem](/wiki/Economic_lot_scheduling_problem "Economic lot scheduling problem")

## References

[[edit](/w/index.php?title=Economic_order_quantity&veaction=edit&section=13 "Edit section: References") | [edit source](/w/index.php?title=Economic_order_quantity&action=edit&section=13 "Edit section's source code: References")]

.mw-parser-output .reflist-columns-2{column-width:30em}.mw-parser-output .reflist-columns-3{column-width:25em}body.skin-vector-2022 .mw-parser-output .reflist-columns-2{column-width:27em}body.skin-vector-2022 .mw-parser-output .reflist-columns-3{column-width:22.5em}.mw-parser-output .references[data-mw-group=upper-alpha]{list-style-type:upper-alpha}.mw-parser-output .references[data-mw-group=upper-roman]{list-style-type:upper-roman}.mw-parser-output .references[data-mw-group=lower-alpha]{list-style-type:lower-alpha}.mw-parser-output .references[data-mw-group=lower-greek]{list-style-type:lower-greek}.mw-parser-output .references[data-mw-group=lower-roman]{list-style-type:lower-roman}.mw-parser-output div.reflist-liststyle-upper-alpha .references{list-style-type:upper-alpha}.mw-parser-output div.reflist-liststyle-upper-roman .references{list-style-type:upper-roman}.mw-parser-output div.reflist-liststyle-lower-alpha .references{list-style-type:lower-alpha}.mw-parser-output div.reflist-liststyle-lower-greek .references{list-style-type:lower-greek}.mw-parser-output div.reflist-liststyle-lower-roman .references{list-style-type:lower-roman}

1. **[^](#cite_ref-Hax1984_1-0)** .mw-parser-output cite.citation{font-style:inherit;word-wrap:break-word}.mw-parser-output .citation q{quotes:"\"""\"""'""'"}.mw-parser-output .citation:target{background-color:rgba(0,127,255,0.133)}.mw-parser-output .id-lock-free.id-lock-free a{background:url("//upload.wikimedia.org/wikipedia/commons/6/65/Lock-green.svg")right 0.1em center/9px no-repeat}.mw-parser-output .id-lock-limited.id-lock-limited a,.mw-parser-output .id-lock-registration.id-lock-registration a{background:url("//upload.wikimedia.org/wikipedia/commons/d/d6/Lock-gray-alt-2.svg")right 0.1em center/9px no-repeat}.mw-parser-output .id-lock-subscription.id-lock-subscription a{background:url("//upload.wikimedia.org/wikipedia/commons/a/aa/Lock-red-alt-2.svg")right 0.1em center/9px no-repeat}.mw-parser-output .cs1-ws-icon a{background:url("//upload.wikimedia.org/wikipedia/commons/4/4c/Wikisource-logo.svg")right 0.1em center/12px no-repeat}body:not(.skin-timeless):not(.skin-minerva) .mw-parser-output .id-lock-free a,body:not(.skin-timeless):not(.skin-minerva) .mw-parser-output .id-lock-limited a,body:not(.skin-timeless):not(.skin-minerva) .mw-parser-output .id-lock-registration a,body:not(.skin-timeless):not(.skin-minerva) .mw-parser-output .id-lock-subscription a,body:not(.skin-timeless):not(.skin-minerva) .mw-parser-output .cs1-ws-icon a{background-size:contain;padding:0 1em 0 0}.mw-parser-output .cs1-code{color:inherit;background:inherit;border:none;padding:inherit}.mw-parser-output .cs1-hidden-error{display:none;color:var(--color-error,#bf3c2c)}.mw-parser-output .cs1-visible-error{color:var(--color-error,#bf3c2c)}.mw-parser-output .cs1-maint{display:none;color:#085;margin-left:0.3em}.mw-parser-output .cs1-kern-left{padding-left:0.2em}.mw-parser-output .cs1-kern-right{padding-right:0.2em}.mw-parser-output .citation .mw-selflink{font-weight:inherit}@media screen{.mw-parser-output .cs1-format{font-size:95%}html.skin-theme-clientpref-night .mw-parser-output .cs1-maint{color:#18911f}}@media screen and (prefers-color-scheme:dark){html.skin-theme-clientpref-os .mw-parser-output .cs1-maint{color:#18911f}}Hax, AC; Candea, D. (1984), [*Production and Operations Management*](http://catalogue.nla.gov.au/Record/772207), Englewood Cliffs, NJ: Prentice-Hall, p. 135, [ISBN](/wiki/ISBN_(identifier) "ISBN (identifier)") [9780137248803](/wiki/Special:BookSources/9780137248803 "Special:BookSources/9780137248803")
2. **[^](#cite_ref-2)** Nahmias, Steven (2005). *Production and operations analysis*. McGraw Hill Higher Education.[*[page needed](/wiki/Wikipedia:Citing_sources "Wikipedia:Citing sources")*]
3. **[^](#cite_ref-3)** Zipkin, Paul H., *Foundations of Inventory Management*, McGraw Hill 2000[*[page needed](/wiki/Wikipedia:Citing_sources "Wikipedia:Citing sources")*]
4. **[^](#cite_ref-4)** Perera, Sandun; Janakiraman, Ganesh; Niu, Shun-Chen (2017). "Optimality of (s,S) policies in EOQ models with general cost structures". *International Journal of Production Economics*. **187**: 216–228. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1016/j.ijpe.2016.09.017](https://doi.org/10.1016%2Fj.ijpe.2016.09.017).
5. **[^](#cite_ref-5)** Altintas, Nihat; Erhun, Feryal; Tayur, Sridhar (2008). "Quantity Discounts Under Demand Uncertainty". *Management Science*. **54** (4): 777–92. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1287/mnsc.1070.0829](https://doi.org/10.1287%2Fmnsc.1070.0829). [JSTOR](/wiki/JSTOR_(identifier) "JSTOR (identifier)") [20122426](https://www.jstor.org/stable/20122426).
6. **[^](#cite_ref-6)** Perera, Sandun; Janakiraman, Ganesh; Niu, Shun-Chen (2017). "Optimality of (s,S) policies in EOQ models with general cost structures". *International Journal of Production Economics*. **187**: 216–228. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1016/j.ijpe.2016.09.017](https://doi.org/10.1016%2Fj.ijpe.2016.09.017).
7. **[^](#cite_ref-7)** [T. Whitin](/wiki/Thomson_M._Whitin "Thomson M. Whitin"), G. Hadley, Analysis of Inventory Systems, Prentice Hall 1963
8. **[^](#cite_ref-8)** Goyal, S.K. (1987). "A simple heuristic method for determining economic order interval for linear demand". *Engineering Costs and Production Economics*. **11**: 53–57. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1016/0167-188X(87)90025-5](https://doi.org/10.1016%2F0167-188X%2887%2990025-5).
9. **[^](#cite_ref-jep_9-0)** Caplin, Andrew; Leahy, John (2010). ["Economic Theory and the World of Practice: A Celebration of the (s, S) Model"](https://doi.org/10.1257%2Fjep.24.1.183). *The Journal of Economic Perspectives*. **24** (1): 183–201. [CiteSeerX](/wiki/CiteSeerX_(identifier) "CiteSeerX (identifier)") [10.1.1.730.8784](https://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.730.8784). [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1257/jep.24.1.183](https://doi.org/10.1257%2Fjep.24.1.183). [JSTOR](/wiki/JSTOR_(identifier) "JSTOR (identifier)") [25703488](https://www.jstor.org/stable/25703488). `{{cite journal}}`: Cite uses deprecated parameter `|citeseerx=` ([help](/wiki/Help:CS1_errors#deprecated_params "Help:CS1 errors"))
10. **[^](#cite_ref-10)** Malakooti, B (2013). *Operations and Production Systems with Multiple Objectives*. John Wiley & Sons. [ISBN](/wiki/ISBN_(identifier) "ISBN (identifier)") [978-1-118-58537-5](/wiki/Special:BookSources/978-1-118-58537-5 "Special:BookSources/978-1-118-58537-5").[*[page needed](/wiki/Wikipedia:Citing_sources "Wikipedia:Citing sources")*]
11. **[^](#cite_ref-tri_11-0)** Trippi, Robert R.; Lewin, Donald E. (1974). "A Present Value Formulation of the Classical Eoq Problem". *Decision Sciences*. **5** (1): 30–35. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1111/j.1540-5915.1974.tb00592.x](https://doi.org/10.1111%2Fj.1540-5915.1974.tb00592.x).
12. **[^](#cite_ref-12)** Salameh, M.K.; Jaber, M.Y. (March 2000). "Economic production quantity model for items with imperfect quality". *International Journal of Production Economics*. **64** (1–3): 59–64. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1016/s0925-5273(99)00044-4](https://doi.org/10.1016%2Fs0925-5273%2899%2900044-4). [ISSN](/wiki/ISSN_(identifier) "ISSN (identifier)") [0925-5273](https://search.worldcat.org/issn/0925-5273).
13. **[^](#cite_ref-13)** Piasecki, D., [Optimizing Economic Order Quantity (EOQ)](https://www.inventoryops.com/articles/optomizing-eoq.html), published initially in the January 2001 issue of "Solutions", accessed on 22 February 2025
14. **[^](#cite_ref-14)** Tao, Z., A. L. Guiffrida, and M. D. Troutt, "A green cost based economic production/order quantity model", in *Proceedings of the 1st Annual Kent State International Symposium on Green Supply Chains*, Canton, Ohio, US, 29–30 July 2010
15. **[^](#cite_ref-15)** Guga, E. and Musa, O. (2015) in [Inventory Management through EOQ Model](https://ijecm.co.uk/wp-content/uploads/2015/12/31211.pdf), *International Journal of Economics, Commerce & Management*, Vol. III, Issue 12, December 2015, accessed 9 February 2024
16. **[^](#cite_ref-16)** Cargal, J. M. (2003), [The EOQ Formula](http://www.cargalmathbooks.com/The%20EOQ%20Formula.pdf), *Troy University*, accessed 9 February 2024

## Further reading

[[edit](/w/index.php?title=Economic_order_quantity&veaction=edit&section=14 "Edit section: Further reading") | [edit source](/w/index.php?title=Economic_order_quantity&action=edit&section=14 "Edit section's source code: Further reading")]

- Harris, Ford W. *Operations Cost* (Factory Management Series), Chicago: Shaw (1915)
- Harris, Ford W. (1913). "How many parts to make at once". *Factory, the Magazine of Management*. **10**: 135–136, 152.
- Camp, W. E. "Determining the production order quantity", Management Engineering, 1922
- Wilson, R. H. (1934). "A Scientific Routine for Stock Control". *Harvard Business Review*. **13**: 116–28.
- Plossel, George. Orlicky's Material Requirement's Planning. Second Edition. McGraw Hill. 1984. (first edition 1975)
- Erlenkotter, Donald (2014). ["Ford Whitman Harris's economical lot size model"](https://escholarship.org/uc/item/4s8482p2). *International Journal of Production Economics*. **155**: 12–15. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1016/j.ijpe.2013.12.008](https://doi.org/10.1016%2Fj.ijpe.2013.12.008). [S2CID](/wiki/S2CID_(identifier) "S2CID (identifier)") [153794306](https://api.semanticscholar.org/CorpusID:153794306).
- Perera, Sandun; Janakiraman, Ganesh; Niu, Shun-Chen (2017). "Optimality of (s,S) policies in EOQ models with general cost structures". *International Journal of Production Economics*. **187**: 216–228. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1016/j.ijpe.2016.09.017](https://doi.org/10.1016%2Fj.ijpe.2016.09.017).
- Perera, Sandun; Janakiraman, Ganesh; Niu, Shun-Chen (2018). "Optimality of (s, S) Inventory Policies under Renewal Demand and General Cost Structures". *Production and Operations Management*. **27** (2): 368–383. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1111/poms.12795](https://doi.org/10.1111%2Fpoms.12795). [hdl](/wiki/Hdl_(identifier) "Hdl (identifier)"):[2027.42/142450](https://hdl.handle.net/2027.42%2F142450).
- Tsan-Ming Choi (Ed.) Handbook of EOQ Inventory Problems: Stochastic and Deterministic Models and Applications, Springer's International Series in Operations Research and Management Science, 2014. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1007/978-1-4614-7639-9](https://doi.org/10.1007%2F978-1-4614-7639-9).
- Ventura, Robert; Samuel, Stephen (2016). ["Optimization of fuel injection in GDI engine using economic order quantity and Lambert W function"](https://radar.brookes.ac.uk/radar/items/cc17b1a1-d1c6-4b76-a34a-c8689ea0270f/1/). *Applied Thermal Engineering*. **101**: 112–20. [doi](/wiki/Doi_(identifier) "Doi (identifier)"):[10.1016/j.applthermaleng.2016.02.024](https://doi.org/10.1016%2Fj.applthermaleng.2016.02.024).
- Renewal Demand and (s, S) Optimality by Perera, Janakiraman, and Niu [[1]](https://onlinelibrary.wiley.com/doi/full/10.1111/poms.12795)

## External links

[[edit](/w/index.php?title=Economic_order_quantity&veaction=edit&section=15 "Edit section: External links") | [edit source](/w/index.php?title=Economic_order_quantity&action=edit&section=15 "Edit section's source code: External links")]

- [The EOQ Model](http://www.logisitik.com/learning-center/inventory-management/item/466-economic-order-quantity-eoq-model.html)
- Piasecki, D., [Inventory Operations Consulting documents](https://www.inventoryops.com/)

.mw-parser-output .hlist dl,.mw-parser-output .hlist ol,.mw-parser-output .hlist ul{margin:0;padding:0}.mw-parser-output .hlist dd,.mw-parser-output .hlist dt,.mw-parser-output .hlist li{margin:0;display:inline}.mw-parser-output .hlist.inline,.mw-parser-output .hlist.inline dl,.mw-parser-output .hlist.inline ol,.mw-parser-output .hlist.inline ul,.mw-parser-output .hlist dl dl,.mw-parser-output .hlist dl ol,.mw-parser-output .hlist dl ul,.mw-parser-output .hlist ol dl,.mw-parser-output .hlist ol ol,.mw-parser-output .hlist ol ul,.mw-parser-output .hlist ul dl,.mw-parser-output .hlist ul ol,.mw-parser-output .hlist ul ul{display:inline}.mw-parser-output .hlist .mw-empty-li{display:none}.mw-parser-output .hlist dt::after{content:": "}.mw-parser-output .hlist dd::after,.mw-parser-output .hlist li::after{content:"\a0 · ";font-weight:bold}.mw-parser-output .hlist dd:last-child::after,.mw-parser-output .hlist dt:last-child::after,.mw-parser-output .hlist li:last-child::after{content:none}.mw-parser-output .hlist dd dd:first-child::before,.mw-parser-output .hlist dd dt:first-child::before,.mw-parser-output .hlist dd li:first-child::before,.mw-parser-output .hlist dt dd:first-child::before,.mw-parser-output .hlist dt dt:first-child::before,.mw-parser-output .hlist dt li:first-child::before,.mw-parser-output .hlist li dd:first-child::before,.mw-parser-output .hlist li dt:first-child::before,.mw-parser-output .hlist li li:first-child::before{content:" (";font-weight:normal}.mw-parser-output .hlist dd dd:last-child::after,.mw-parser-output .hlist dd dt:last-child::after,.mw-parser-output .hlist dd li:last-child::after,.mw-parser-output .hlist dt dd:last-child::after,.mw-parser-output .hlist dt dt:last-child::after,.mw-parser-output .hlist dt li:last-child::after,.mw-parser-output .hlist li dd:last-child::after,.mw-parser-output .hlist li dt:last-child::after,.mw-parser-output .hlist li li:last-child::after{content:")";font-weight:normal}.mw-parser-output .hlist ol{counter-reset:listitem}.mw-parser-output .hlist ol>li{counter-increment:listitem}.mw-parser-output .hlist ol>li::before{content:" "counter(listitem)"\a0 "}.mw-parser-output .hlist dd ol>li:first-child::before,.mw-parser-output .hlist dt ol>li:first-child::before,.mw-parser-output .hlist li ol>li:first-child::before{content:" ("counter(listitem)"\a0 "}.mw-parser-output .navbox{box-sizing:border-box;border:1px solid #a2a9b1;width:100%;clear:both;font-size:88%;text-align:center;padding:1px;margin:1em auto 0}.mw-parser-output .navbox .navbox{margin-top:0}.mw-parser-output .navbox+.navbox-styles+.navbox,.mw-parser-output .navbox+span.mw-empty-elt+.navbox-styles+.navbox{margin-top:-1px}.mw-parser-output .navbox-inner,.mw-parser-output .navbox-subgroup{width:100%}.mw-parser-output .navbox-group,.mw-parser-output .navbox-title,.mw-parser-output .navbox-abovebelow{padding:0.25em 1em;line-height:1.5em;text-align:center}.mw-parser-output .navbox-group{white-space:nowrap;text-align:right}.mw-parser-output .navbox,.mw-parser-output .navbox-subgroup{background-color:#fdfdfd;color:inherit}.mw-parser-output .navbox-list{line-height:1.5em;border-color:#fdfdfd}.mw-parser-output .navbox-list-with-group{text-align:left;border-left-width:2px;border-left-style:solid}.mw-parser-output tr+tr>.navbox-abovebelow,.mw-parser-output tr+tr>.navbox-group,.mw-parser-output tr+tr>.navbox-image,.mw-parser-output tr+tr>.navbox-list{border-top:2px solid #fdfdfd}.mw-parser-output .navbox-title{background-color:#ccf;color:inherit}.mw-parser-output .navbox-abovebelow,.mw-parser-output .navbox-group,.mw-parser-output .navbox-subgroup .navbox-title{background-color:#ddf;color:inherit}.mw-parser-output .navbox-subgroup .navbox-group,.mw-parser-output .navbox-subgroup .navbox-abovebelow{background-color:#e6e6ff;color:inherit}.mw-parser-output .navbox-even{background-color:#f7f7f7;color:inherit}.mw-parser-output .navbox-odd{background-color:transparent;color:inherit}.mw-parser-output .navbox .hlist td dl,.mw-parser-output .navbox .hlist td ol,.mw-parser-output .navbox .hlist td ul,.mw-parser-output .navbox td.hlist dl,.mw-parser-output .navbox td.hlist ol,.mw-parser-output .navbox td.hlist ul{padding:0.125em 0}.mw-parser-output .navbox .navbar{display:block;font-size:100%}.mw-parser-output .navbox-title .navbar{float:left;text-align:left;margin-right:0.5em}body.skin--responsive .mw-parser-output .navbox-image img{max-width:none!important}@media print{body.ns-0 .mw-parser-output .navbox{display:none!important}}

|  |  |
| --- | --- |
| [Authority control databases](/wiki/Help:Authority_control "Help:Authority control"): National [Edit this at Wikidata](https://www.wikidata.org/wiki/Q451299#identifiers "Edit this at Wikidata") | - [Spain](https://datos.bne.es/resource/XX4667257) |
