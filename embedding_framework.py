import numpy as np
from typing import List, Dict, Any, Tuple

class CapabilityEmbeddingEngine:
    """
    Formal Embedding Framework for Capability Composition based on:
    A = (S, C, S_I, G, R, K) and C_i = (T_i, I_i, O_i, P_i, E_i, K_i, R_i, Q_i, Rel_i, A_i, M_i)
    """
    def __init__(self, vocab_vars: List[str], vocab_types: List[str]):
        self.vocab_vars = vocab_vars
        self.vocab_types = vocab_types
        self.var2idx = {v: i for i, v in enumerate(vocab_vars)}
        self.type2idx = {t: i for i, t in enumerate(vocab_types)}
        
        self.d_state = len(vocab_vars)
        self.d_type = len(vocab_types)
        # Vector layout: Type + Inputs + Outputs + Preconditions + Effects + Costs (5) + Rel/Avail (2)
        self.d_cap = self.d_type + (4 * self.d_state) + 5 + 2

    def encode_state(self, state: Dict[str, Any]) -> np.ndarray:
        """Encodes state S = {(x_1, v_1), ..., (x_n, v_n)} into vector space phi_S(S)."""
        vec = np.zeros(self.d_state)
        for var, val in state.items():
            if var in self.var2idx:
                idx = self.var2idx[var]
                if isinstance(val, bool):
                    vec[idx] = 1.0 if val else -1.0
                elif isinstance(val, (int, float)):
                    vec[idx] = float(val)
                elif isinstance(val, str):
                    vec[idx] = 1.0
        return vec

    def encode_goal(self, goal: Dict[str, Any]) -> np.ndarray:
        """Encodes goal specification G = {g_1, ..., g_m} into vector space phi_G(G)."""
        return self.encode_state(goal)

    def encode_capability(self, cap: Dict[str, Any]) -> np.ndarray:
        """
        Encodes C_i = (T_i, I_i, O_i, P_i, E_i, K_i, R_i, Q_i, Rel_i, A_i, M_i) into phi_C(C_i).
        """
        # Type vector T_i
        v_type = np.zeros(self.d_type)
        if cap.get('type') in self.type2idx:
            v_type[self.type2idx[cap['type']]] = 1.0

        # Input vector I_i
        v_in = np.zeros(self.d_state)
        for inp in cap.get('inputs', []):
            if inp in self.var2idx:
                v_in[self.var2idx[inp]] = 1.0

        # Output vector O_i
        v_out = np.zeros(self.d_state)
        for out in cap.get('outputs', []):
            if out in self.var2idx:
                v_out[self.var2idx[out]] = 1.0

        # Precondition P_i and Effect E_i vectors
        v_p = self.encode_state(cap.get('preconditions', {}))
        v_e = self.encode_state(cap.get('effects', {}))

        # Operational costs Q_i = (C_time, C_resource, C_money, C_risk, C_energy)
        q = cap.get('cost', {})
        v_q = np.array([
            q.get('time', 0.0),
            q.get('resource', 0.0),
            q.get('money', 0.0),
            q.get('risk', 0.0),
            q.get('energy', 0.0)
        ])

        # Reliability Rel_i and Availability A_i
        rel = cap.get('reliability', 1.0)
        avail = cap.get('availability', 1.0)
        v_rel_avail = np.array([np.log(max(rel, 1e-5)), float(avail)])

        return np.concatenate([v_type, v_in, v_out, v_p, v_e, v_q, v_rel_avail])

    def evaluate_compatibility(self, cap1_vec: np.ndarray, cap2_vec: np.ndarray) -> float:
        """
        Evaluates compatibility for C1 -> C2 (whether effects/outputs of C1 satisfy preconditions/inputs of C2).
        """
        idx_p_start = self.d_type + 2 * self.d_state
        idx_e_start = idx_p_start + self.d_state
        
        v_e1 = cap1_vec[idx_e_start : idx_e_start + self.d_state]
        v_p2 = cap2_vec[idx_p_start : idx_p_start + self.d_state]

        p2_active = np.abs(v_p2) > 1e-5
        if not np.any(p2_active):
            return 1.0
        
        match = (v_e1[p2_active] == v_p2[p2_active])
        return float(np.mean(match))

    def compose(self, cap1_vec: np.ndarray, cap2_vec: np.ndarray) -> np.ndarray:
        """
        Algebraically composes two capability vectors: C12 = C2 o C1
        """
        composite = cap1_vec.copy()
        
        idx_in = self.d_type
        idx_out = idx_in + self.d_state
        idx_p = idx_out + self.d_state
        idx_e = idx_p + self.d_state
        idx_q = idx_e + self.d_state
        idx_rel = idx_q + 5

        # Merge produced outputs
        composite[idx_out:idx_p] = np.maximum(cap1_vec[idx_out:idx_p], cap2_vec[idx_out:idx_p])
        # Additive effects
        composite[idx_e:idx_q] = cap1_vec[idx_e:idx_q] + cap2_vec[idx_e:idx_q]
        # Additive operational costs
        composite[idx_q:idx_rel] = cap1_vec[idx_q:idx_rel] + cap2_vec[idx_q:idx_rel]
        # Multiplicative reliability (via log-additivity)
        composite[idx_rel] = cap1_vec[idx_rel] + cap2_vec[idx_rel]
        
        return composite

    def similarity(self, v1: np.ndarray, v2: np.ndarray) -> float:
        """Cosine similarity measure across entities."""
        norm1, norm2 = np.linalg.norm(v1), np.linalg.norm(v2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(np.dot(v1, v2) / (norm1 * norm2))

if __name__ == "__main__":
    vocab_vars = [
        "User.authenticated", "User.role", "Cart.exists", "Cart.item_count",
        "Order.exists", "Order.status", "Payment.status", "Inventory.available", "Notification.sent"
    ]
    vocab_types = ["API", "DATABASE", "GUI", "EVENT", "FUNCTION", "FILE", "COMPUTATION", "MESSAGE", "SERVICE"]

    engine = CapabilityEmbeddingEngine(vocab_vars, vocab_types)

    # Required Experiment 1: Capability Compatibility
    C1 = {
        'type': 'API',
        'inputs': ['cart_id'],
        'outputs': ['order_id'],
        'preconditions': {},
        'effects': {'Order.exists': True},
        'cost': {'time': 100, 'money': 0.01},
        'reliability': 0.99
    }

    C2 = {
        'type': 'SERVICE',
        'inputs': ['order_id'],
        'outputs': ['payment_id'],
        'preconditions': {'Order.exists': True},
        'effects': {'Payment.status': True},
        'cost': {'time': 200, 'money': 0.05},
        'reliability': 0.95
    }

    C3 = {
        'type': 'DATABASE',
        'inputs': [],
        'outputs': [],
        'preconditions': {'Order.exists': False},
        'effects': {'Cart.exists': False},
        'cost': {'time': 50, 'money': 0.00},
        'reliability': 0.99
    }

    v_C1 = engine.encode_capability(C1)
    v_C2 = engine.encode_capability(C2)
    v_C3 = engine.encode_capability(C3)

    compat_12 = engine.evaluate_compatibility(v_C1, v_C2)
    compat_13 = engine.evaluate_compatibility(v_C1, v_C3)

    print(f"Compatibility (C1 -> C2): {compat_12:.2f}")
    print(f"Compatibility (C1 -> C3): {compat_13:.2f}")

    # Required Experiment 2: Capability Composition
    v_C12 = engine.compose(v_C1, v_C2)
    print(f"Composite Vector Dimension: {v_C12.shape[0]}")
    print(f"Similarity (C12 vs C2): {engine.similarity(v_C12, v_C2):.4f}")
