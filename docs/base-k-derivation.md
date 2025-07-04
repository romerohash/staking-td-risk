# Comprehensive Derivation of base_k = eth_weight² × (v' Σ v)

## Overview

This document provides a detailed mathematical derivation showing how the `base_k` coefficient emerges from the Lagrange multiplier optimization for risk-minimizing active weights. We'll show step-by-step how the tracking error variance can be expressed in terms of redemption percentage, leading to the identification of `base_k`.

## 1. Problem Setup

### 1.1 Active Weight Constraints

We need to find active weights **a** that minimize tracking error variance subject to:
1. Sum-to-zero constraint: Σᵢ aᵢ = 0 (portfolio remains fully invested)
2. ETH-specific constraint: a_ETH = δ_ETH (required ETH overweight)

### 1.2 Redemption-Driven ETH Overweight

From the redemption mechanics:
```
δ_ETH = max(0, eth_weight × (redemption_pct - (1 - staking_pct)))
```

When redemption_pct > (1 - staking_pct):
```
δ_ETH = eth_weight × (redemption_pct - (1 - staking_pct))
```

## 2. Lagrange Multiplier Solution

### 2.1 Optimization Problem

Minimize: **f(a) = ½ a' Σ a** (tracking error variance)

Subject to:
- **C a = c**

where:
```
C = [1  1  1  1  1  1]  (sum-to-zero)
    [0  1  0  0  0  0]  (ETH-specific)

c = [0]
    [δ_ETH]
```

### 2.2 Lagrangian Formulation

The Lagrangian is:
```
L(a, λ) = ½ a' Σ a - λ' (C a - c)
```

Taking derivatives:
- ∂L/∂a = Σ a - C' λ = 0
- ∂L/∂λ = C a - c = 0

From the first equation: **a = Σ⁻¹ C' λ**

### 2.3 Solving for Lagrange Multipliers

Substituting into the constraint:
```
C a = C Σ⁻¹ C' λ = c
```

Therefore:
```
λ = (C Σ⁻¹ C')⁻¹ c
```

### 2.4 Optimal Active Weights

The optimal active weights are:
```
a* = Σ⁻¹ C' λ = Σ⁻¹ C' (C Σ⁻¹ C')⁻¹ c
```

## 3. Linear Structure in δ_ETH

### 3.1 Key Observation

Since **c = [0, δ_ETH]'**, we can write:
```
c = δ_ETH × [0, 1]' = δ_ETH × e₂
```

where e₂ is the unit vector for the ETH constraint.

### 3.2 Linearity of Solution

This means:
```
λ = (C Σ⁻¹ C')⁻¹ c = δ_ETH × (C Σ⁻¹ C')⁻¹ e₂ = δ_ETH × λ₀
```

And therefore:
```
a* = Σ⁻¹ C' λ = δ_ETH × Σ⁻¹ C' λ₀ = δ_ETH × v
```

where **v = Σ⁻¹ C' λ₀** is a fixed vector that depends only on the covariance structure.

## 4. Tracking Error Variance

### 4.1 Variance Calculation

The tracking error variance is:
```
Var(TE) = a' Σ a = (δ_ETH × v)' Σ (δ_ETH × v)
        = δ_ETH² × (v' Σ v)
```

### 4.2 Substituting δ_ETH

When redemption_pct > (1 - staking_pct):
```
δ_ETH = eth_weight × (redemption_pct - (1 - staking_pct))
```

Therefore:
```
Var(TE) = [eth_weight × (redemption_pct - (1 - staking_pct))]² × (v' Σ v)
        = eth_weight² × (redemption_pct - (1 - staking_pct))² × (v' Σ v)
```

## 5. Identifying base_k

### 5.1 Definition

From the variance expression, we can identify:
```
base_k = eth_weight² × (v' Σ v)
```

This gives us:
```
Var(TE) = base_k × (redemption_pct - (1 - staking_pct))²
```

### 5.2 Properties of base_k

1. **Covariance Dependence**: (v' Σ v) depends on:
   - The inverse covariance matrix Σ⁻¹
   - The constraint structure C
   - The specific optimization problem

2. **ETH Weight Scaling**: The eth_weight² factor captures:
   - The direct impact of ETH's benchmark weight
   - The quadratic nature of the variance calculation

3. **Constant for Given Market**: For a fixed covariance structure and ETH weight, base_k is constant

## 6. Why k_factor Cannot Be Constant

If we define k_factor as variance/redemption_pct², then:
```
k_factor = base_k × [(redemption_pct - (1 - staking_pct))/redemption_pct]²
```

This shows k_factor varies with redemption_pct, approaching:
- 0 as redemption_pct → (1 - staking_pct)
- base_k × staking_pct² as redemption_pct → 1

## 7. Implementation Verification

From the code in `ActiveWeightOptimizer.optimize()`:
```python
# Constraint matrix
C = np.vstack([
    np.ones(self.n_assets),      # sum-to-zero
    np.eye(self.n_assets)[1]     # ETH-specific
])
c = np.array([0.0, delta_eth])

# Lagrange multipliers
lambda_opt = np.linalg.solve(C @ self.inv_cov @ C.T, c)

# Optimal weights
active = self.inv_cov @ C.T @ lambda_opt
```

This implements exactly the mathematical solution derived above, confirming:
- Active weights are linear in delta_eth
- The coefficient vector v = Σ⁻¹ C' λ₀
- Variance is quadratic: δ_ETH² × (v' Σ v)

## 8. Conclusion

The derivation shows that:

1. **base_k = eth_weight² × (v' Σ v)** emerges naturally from the Lagrange multiplier optimization
2. The term (v' Σ v) represents the "efficiency" of the optimal active weight vector
3. The eth_weight² scaling comes from the linear relationship between δ_ETH and redemption_pct
4. This structure explains why variance is quadratic in (redemption_pct - threshold) rather than redemption_pct itself

This mathematical framework provides the foundation for accurate tracking error calculation in stochastic redemption models.