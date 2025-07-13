# Two-Asset Tracking Error Formula: ETH + SOL

## Overview

This document derives the exact analytical formula for tracking error when a portfolio has two stakable assets with different unbonding periods. The formula accounts for:
- Correlated overweights from common redemption events
- Different unbonding periods creating time-segmented variance
- Cross-asset hedging effects captured through Lagrange optimization

## Mathematical Framework

### 1. Problem Setup

Consider a portfolio tracking a benchmark with two stakable assets:
- **ETH**: weight = 10.49%, unbonding = 10 days, staking = 80%
- **SOL**: weight = 3.87%, unbonding = 2 days, staking = 70%

When redemption r occurs:
- ETH threshold: τ_ETH = 1 - 0.80 = 0.20
- SOL threshold: τ_SOL = 1 - 0.70 = 0.30

### 2. Overweight Calculations

For redemption size r:
```
δ_ETH = eth_weight × max(0, r - τ_ETH)
δ_SOL = sol_weight × max(0, r - τ_SOL)
```

Key insight: These overweights are **correlated** because they depend on the same r.

### 3. Multi-Constraint Lagrangian

We minimize portfolio variance subject to three constraints:

**Objective**: min ½ a' Σ a

**Constraints**:
```
Σᵢ aᵢ = 0        (fully invested)
a_ETH = δ_ETH    (ETH overweight)
a_SOL = δ_SOL    (SOL overweight)
```

In matrix form:
```
C = [1  1  1  1  1  1]   (sum-to-zero)
    [0  1  0  0  0  0]   (ETH constraint)
    [0  0  0  1  0  0]   (SOL constraint)

c = [0, δ_ETH, δ_SOL]'
```

### 4. Lagrangian Solution

The solution has the form:
```
a* = Σ⁻¹ C' (C Σ⁻¹ C')⁻¹ c
```

Since c is linear in δ_ETH and δ_SOL:
```
a* = δ_ETH × v_ETH + δ_SOL × v_SOL
```

where v_ETH and v_SOL are the columns of V = Σ⁻¹ C' (C Σ⁻¹ C')⁻¹ corresponding to each constraint.

### 5. Variance Components

The tracking error variance is:
```
Var(TE) = a*' Σ a*
        = (δ_ETH × v_ETH + δ_SOL × v_SOL)' Σ (δ_ETH × v_ETH + δ_SOL × v_SOL)
        = δ_ETH² × (v_ETH' Σ v_ETH) + 2 × δ_ETH × δ_SOL × (v_ETH' Σ v_SOL) + δ_SOL² × (v_SOL' Σ v_SOL)
```

Substituting the overweight formulas:
```
Var(TE) = eth_weight² × (r - τ_ETH)²₊ × (v_ETH' Σ v_ETH) +
          2 × eth_weight × sol_weight × (r - τ_ETH)₊ × (r - τ_SOL)₊ × (v_ETH' Σ v_SOL) +
          sol_weight² × (r - τ_SOL)²₊ × (v_SOL' Σ v_SOL)
```

### 6. Defining k-Components

Let:
```
k_ETH_ETH = eth_weight² × (v_ETH' Σ v_ETH)
k_ETH_SOL = eth_weight × sol_weight × (v_ETH' Σ v_SOL)
k_SOL_SOL = sol_weight² × (v_SOL' Σ v_SOL)
```

Then:
```
Var(TE) = k_ETH_ETH × (r - τ_ETH)²₊ + 
          2 × k_ETH_SOL × (r - τ_ETH)₊ × (r - τ_SOL)₊ + 
          k_SOL_SOL × (r - τ_SOL)²₊
```

## Time-Segmented Variance

### Different Unbonding Periods

The key complication: ETH takes 10 days to unbond while SOL takes only 2 days.

For each redemption:
- **Days 1-2**: Both assets may be overweighted → Full variance formula
- **Days 3-10**: Only ETH overweighted → Partial variance (SOL term = 0)

### Variance Functions

**Full Period Variance** (both assets active):
```
Var_full(r) = k_ETH_ETH × (r - τ_ETH)²₊ + 
              2 × k_ETH_SOL × (r - τ_ETH)₊ × (r - τ_SOL)₊ + 
              k_SOL_SOL × (r - τ_SOL)²₊
```

**Partial Period Variance** (only ETH active):
```
Var_partial(r) = k_ETH_ETH × (r - τ_ETH)²₊
```

### Total Variance-Days

For a single redemption of size r:
```
Variance-Days(r) = 2 × Var_full(r) + 8 × Var_partial(r)
```

## The Two-Asset Tracking Error Formula

### Expected Variance-Days

For stochastic redemptions with distribution F_R:
```
E[Variance-Days] = 2 × E[Var_full(R)] + 8 × E[Var_partial(R)]
```

Where:
```
E[Var_full(R)] = ∫ Var_full(r) dF_R(r)
E[Var_partial(R)] = ∫ Var_partial(r) dF_R(r)
```

### Annual Tracking Error

The annual tracking error with λ expected redemptions per year:

```
TE = √[λ × E[Variance-Days]]
   = √[λ × (2 × E[Var_full(R)] + 8 × E[Var_partial(R)])]
```

## Expanded Form

Substituting all components:

```
TE = √[λ × (2 × E[k_ETH_ETH × (R - τ_ETH)²₊ + 
                  2 × k_ETH_SOL × (R - τ_ETH)₊ × (R - τ_SOL)₊ + 
                  k_SOL_SOL × (R - τ_SOL)²₊] +
            8 × E[k_ETH_ETH × (R - τ_ETH)²₊])]
```

Simplifying:
```
TE = √[λ × (10 × k_ETH_ETH × E[(R - τ_ETH)²₊] +
            2 × k_SOL_SOL × E[(R - τ_SOL)²₊] +
            4 × k_ETH_SOL × E[(R - τ_ETH)₊ × (R - τ_SOL)₊])]
```

## Special Cases

### Case 1: No Cross-Term (k_ETH_SOL = 0)

If ETH and SOL hedging effects are independent:
```
TE = √[λ × (10 × k_ETH_ETH × E[(R - τ_ETH)²₊] + 2 × k_SOL_SOL × E[(R - τ_SOL)²₊])]
```

This simplifies to weighted single-asset formulas with different durations.

### Case 2: Equal Thresholds (τ_ETH = τ_SOL = τ)

If both assets have the same staking percentage:
```
E[(R - τ_ETH)₊ × (R - τ_SOL)₊] = E[(R - τ)²₊]
```

The formula becomes:
```
TE = √[λ × E[(R - τ)²₊] × (10 × k_ETH_ETH + 2 × k_SOL_SOL + 4 × k_ETH_SOL)]
```

### Case 3: SOL Never Overweighted

If all redemptions are below τ_SOL:
```
TE = √[λ × 10 × k_ETH_ETH × E[(R - τ_ETH)²₊]]
```

This reduces to the single-asset ETH formula.

## Implementation Considerations

### 1. Computing k-Components

The k-components require:
1. Build covariance matrix Σ
2. Construct constraint matrix C
3. Compute V = Σ⁻¹ C' (C Σ⁻¹ C')⁻¹
4. Extract v_ETH (column 2) and v_SOL (column 3)
5. Calculate k values using definitions above

### 2. Handling Redemption Distributions

For discrete distributions with P(R = rᵢ) = pᵢ:
```
E[(R - τ_ETH)₊ × (R - τ_SOL)₊] = Σᵢ pᵢ × max(0, rᵢ - τ_ETH) × max(0, rᵢ - τ_SOL)
```

### 3. Numerical Stability

- Check that (C Σ⁻¹ C') is invertible
- Verify k-components are positive (variance must be non-negative)
- Validate against Monte Carlo simulation

## Key Insights

1. **Non-Additive**: The two-asset TE is NOT √(TE_ETH² + TE_SOL²) due to:
   - Cross-term k_ETH_SOL capturing hedging effects
   - Correlated overweights from common redemption

2. **Time Complexity**: Different unbonding periods create a weighted average of full and partial variance regimes

3. **Threshold Interactions**: The formula depends on THREE expectations:
   - E[(R - τ_ETH)²₊]
   - E[(R - τ_SOL)²₊]  
   - E[(R - τ_ETH)₊ × (R - τ_SOL)₊]

4. **Correlation Effects**: Positive k_ETH_SOL (when constraints compete) increases total TE, creating a correlation cost

## Conclusion

The two-asset tracking error formula is:

```
TE = √[λ × (d_short × E[Var_full(R)] + (d_long - d_short) × E[Var_partial(R)])]
```

Where:
- d_short = min(unbonding days) = 2
- d_long = max(unbonding days) = 10
- Var_full includes all k-components and cross-terms
- Var_partial includes only the long-duration asset

This exact formula captures all correlation effects and time-segmentation, providing accurate risk assessment for multi-asset staking strategies.