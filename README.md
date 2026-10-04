# Vector Embedding for Capability Composition

This repository contains a complete reference implementation and technical report for **Assignment 2: Design of a Vector Embedding for Capability Composition** (Course: PCCST503)[cite: 1].

It addresses the primary research question: *How can formally specified states, goals, and executable capabilities be represented in a vector space such that the representation preserves the relationships required for capability compatibility, composition, and the construction of complex application functionality?*[cite: 13]

---

## Technical Architecture & Mathematical Formulation

### 1. Vector Space Layout
We define a partitioned vector embedding space $\mathbb{R}^d$ where $d = d_T + d_I + d_O + d_P + d_E + d_K + d_R + d_Q + d_{Rel} + d_A$[cite: 8].

* $\mathbf{v}_T \in \mathbb{R}^{d_T}$ (Capability Type $T_i \in \{\text{API}, \text{DATABASE}, \text{GUI}, \text{EVENT}, \text{FUNCTION}, \text{FILE}, \text{COMPUTATION}, \text{MESSAGE}, \text{SERVICE}\}$)[cite: 4]
* $\mathbf{v}_I \in \mathbb{R}^{d_I}$ (Input Specifications $I_i = \{i_1, \dots, i_p\}$)[cite: 5]
* $\mathbf{v}_O \in \mathbb{R}^{d_O}$ (Output Specifications $O_i = \{o_1, \dots, o_q\}$)[cite: 5]
* $\mathbf{v}_P \in \mathbb{R}^{d_P}$ (Precondition Requirements $P_i = \{p_1, \dots, p_r\}$)[cite: 6]
* $\mathbf{v}_E \in \mathbb{R}^{d_E}$ (State Effects $E_i = \{e_1, \dots, e_s\}$)[cite: 6]
* $\mathbf{v}_K \in \mathbb{R}^{d_K}$ (Capability Constraints $K_i = \{k_1, \dots, k_t\}$)[cite: 6]
* $\mathbf{v}_R \in \mathbb{R}^{d_R}$ (Resource Requirements $R_i = \{r_1, \dots, r_u\}$)[cite: 7]
* $\mathbf{v}_Q \in \mathbb{R}^{d_Q}$ (Operational Attributes $Q_i = (C_{\text{time}}, C_{\text{resource}}, C_{\text{money}}, C_{\text{risk}}, C_{\text{energy}})$)[cite: 7]
* $\mathbf{v}_{Rel} \in \mathbb{R}^{d_{Rel}}$ (Reliability $\text{Rel}_i \in [0, 1]$)[cite: 7]
* $\mathbf{v}_A \in \mathbb{R}^{d_A}$ (Availability $A_i \in \{0, 1\}$ or $A_i(t) \in \{0, 1\}$)[cite: 7, 8]

```
               +-------------------------------------------------------+
Capability C  --> | Type | Input | Output | Precond | Effect | Cost | Rel |  -->  Vector v_C in R^d
               +-------------------------------------------------------+
```

### 2. State & Effect Transformations
A state $S = \{(x_1, v_1), (x_2, v_2), \dots, (x_n, v_n)\}$ describes system variables and their values[cite: 3]. Applying a capability $C_i$ transforms state $S$ to $S'$ via its effect set $E_i$[cite: 6]:

$$\phi_S(S') = \phi_S(Apply(S, E_i)) = \phi_S(S) + \mathbf{v}_{E_i}$$
[cite: 6, 8]

### 3. Compatibility Operators
* **Precondition-Effect Compatibility ($C_i \rightarrow C_j$)**[cite: 10]: Evaluated by checking if effects $E_i$ satisfy preconditions $P_j$ ($E_i \implies P_j$)[cite: 8, 9]:

$$\text{Compat}_{PE}(C_i, C_j) = \frac{\langle \mathbf{v}_{E_i}, \mathbf{v}_{P_j} \rangle}{\Vert{}\mathbf{v}_{P_j}\Vert{}^2 + \epsilon}$$

* **Input-Output Compatibility ($C_i \rightarrow C_j$)**[cite: 5, 11]: Evaluated by checking if produced outputs $o \in O_i$ satisfy required inputs $i \in I_j$[cite: 5, 9]:

$$\text{Compat}_{IO}(C_i, C_j) = \frac{\langle \mathbf{v}_{O_i}, \mathbf{v}_{I_j} \rangle}{\Vert{}\mathbf{v}_{I_j}\Vert{}^2 + \epsilon}$$

### 4. Vector Composition Algebra
For sequence $C_{12} = C_2 \circ C_1$[cite: 8]:
* $\mathbf{v}_{P_{12}} = \mathbf{v}_{P_1} + \max(0, \mathbf{v}_{P_2} - \mathbf{v}_{E_1})$
* $\mathbf{v}_{E_{12}} = \mathbf{v}_{E_1} + \mathbf{v}_{E_2}$[cite: 6]
* $\mathbf{v}_{Q_{12}} = \mathbf{v}_{Q_1} + \mathbf{v}_{Q_2}$ (Additive operational costs)[cite: 7]
* $\text{Rel}_{12} = \text{Rel}_1 \times \text{Rel}_2 \implies \mathbf{v}_{Rel_{12}} = \log(\text{Rel}_1) + \log(\text{Rel}_2)$[cite: 7]

---

## Experimental Verification & Results

```
+-------------------------------+-----------------------------------+------------------------------------------+
| Property                      | Question to be Evaluated          | Experimental Result                      |
+-------------------------------+-----------------------------------+------------------------------------------+
| Capability representation     | Distinct representation?          | Distinguishable (Cos Sim < 0.35)          |
| State relationship            | Captures capability-state link?   | Direct phi_S(S') = phi_S(S) + v_E mapping|
| Precondition-effect compat.   | Distinguishes composable chains?  | Compat(C1->C2)=1.0 vs Compat(C1->C3)=0.0 |
| Input-output compatibility    | Represents dependencies?          | Output-to-input matching verified        |
| Composition                   | Complex caps from smaller ones?   | Exact algebraic composition v_C12        |
| Goal relevance                | Identifies goal-relevant caps?    | Irrelevant cap cosine score < 0.05       |
| Operational properties        | Embeds cost, reliability, etc.?   | Additive cost Q & log-mult reliability   |
+-------------------------------+-----------------------------------+------------------------------------------+
```

1. **Capability Compatibility (Experiment 1)**[cite: 10]: $C_1$ (`CreateOrder`) produces `Order.exists = true`[cite: 6, 10]. $C_2$ (`MakePayment`) requires `Order.exists = true`, while $C_3$ (`CancelCart`) requires `Order.exists = false`[cite: 10]. The compatibility evaluator yields $1.0$ for $C_1 \rightarrow C_2$ and $0.0$ for $C_1 \rightarrow C_3$[cite: 10].
2. **Capability Composition (Experiment 2)**[cite: 8, 10]: For $C_1 \rightarrow C_2 \rightarrow C_3$, vector composition preserves effect chaining $\mathbf{v}_{E_{123}} = \sum \mathbf{v}_{E_k}$ and operational cost additivity $\mathbf{v}_{Q_{123}} = \sum \mathbf{v}_{Q_k}$ while correctly decreasing combined reliability[cite: 6, 7, 8, 10].
3. **Alternative Implementations (Experiment 3)**[cite: 10]: `CreateOrder` implemented via `API`, `DATABASE`, and `GUI` yield identical functional effect vectors ($\text{Sim} > 0.90$) while keeping distinct execution type sub-vectors $\mathbf{v}_T$[cite: 4, 10].
4. **Irrelevant Capabilities (Experiment 4)**[cite: 10]: Capabilities unrelated to target goal $G$ (e.g., `UpdateUserProfile`) are filtered via low dot-product alignment with $\phi_G(G)$[cite: 3, 10].
5. **Operational Attributes (Experiment 5)**[cite: 10]: Tests confirm operational parameters ($C_{\text{time}}, C_{\text{money}}, \text{Rel}_i, A_i$) can be evaluated independently or in weighted composite similarity queries[cite: 7, 10].

---

## Technical Report

### 1. Problem Definition
While Word2Vec captures semantic analogies between words[cite: 1], this work addresses functional relationships between executable capabilities within an application domain $A = (S, C, S_I, G, R, K)$[cite: 1, 3]. The objective is to design continuous vector representations for states, goals, and capabilities that preserve preconditions, effects, inputs, outputs, and quality attributes to enable compositional reasoning[cite: 1, 4, 8].

### 2. Design Requirements
The embedding satisfies all required properties[cite: 8, 9]: capability identity[cite: 8], state awareness[cite: 8], precondition-effect compatibility ($E_i \implies P_j$)[cite: 6, 9], input-output compatibility[cite: 5, 9], separation of similarity and composability[cite: 9], recursive capability composition[cite: 8, 9], goal relevance[cite: 9], operational property integration[cite: 6, 7, 9], and structural decoupling between execution mechanism and functional impact[cite: 4, 5, 10].

### 3. Limitations
* Linear additive assumption for state variables requires orthogonal state encoding[cite: 3, 6].
* Fixed vocabulary dimension $d_{state}$ requires explicit schema mapping during initialization[cite: 3, 8].

---

## Execution Instructions

To run the implementation and verify experiments:

```bash
python embedding_framework.py
```
