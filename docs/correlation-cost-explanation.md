# Why Two-Asset Staking Creates a Correlation Cost, Not Benefit

## The Counterintuitive Result

In traditional portfolio theory, diversification typically reduces risk. However, in our two-asset staking case with ETH and SOL, we observe the opposite: the exact two-asset tracking error is **higher** than the independence approximation √(TE²_ETH + TE²_SOL).

This document explains the mathematical intuition behind this phenomenon.

## Mathematical Framework

### The Cross-Term Sign

In the two-asset variance formula:
```
Var = k_ETH_ETH × (r - τ_ETH)²₊ + 2 × k_ETH_SOL × (r - τ_ETH)₊ × (r - τ_SOL)₊ + k_SOL_SOL × (r - τ_SOL)²₊
```

The sign of k_ETH_SOL determines whether we have a benefit or cost:
- k_ETH_SOL < 0: Correlation benefit (reduces TE)
- k_ETH_SOL > 0: Correlation cost (increases TE)

Where:
```
k_ETH_SOL = eth_weight × sol_weight × (v_ETH' Σ v_SOL)
```

## Why k_ETH_SOL > 0 in Our Case

### 1. Constraint Competition

The key insight: ETH and SOL constraints **compete** rather than complement each other.

When solving the Lagrangian:
```
min ½ a' Σ a
s.t. Σᵢ aᵢ = 0
     a_ETH = δ_ETH
     a_SOL = δ_SOL
```

We're forcing the optimizer to satisfy multiple overweight constraints simultaneously. The vectors v_ETH and v_SOL represent the optimal portfolio adjustments for unit overweights.

### 2. Limited Hedging Options

Consider what happens when we need to overweight both ETH and SOL:

**Single Asset (ETH only)**:
- Overweight ETH by δ_ETH
- Underweight other assets optimally to minimize variance
- SOL can be used as part of the hedge

**Two Assets (ETH + SOL)**:
- Overweight ETH by δ_ETH
- Overweight SOL by δ_SOL
- Must underweight remaining assets (BTC, XRP, ADA, XLM) more aggressively
- Lost SOL as a hedging instrument for ETH (and vice versa)

### 3. Mathematical Intuition

The positive v_ETH' Σ v_SOL arises because:

1. **Common Direction**: Both v_ETH and v_SOL must create overweights, pushing the portfolio in similar directions relative to the benchmark.

2. **Shared Hedge Assets**: Both constraints must be hedged using the same limited set of non-staked assets (primarily BTC).

3. **Correlation Structure**: ETH and SOL are positively correlated (ρ ≈ 0.60), meaning their risk profiles are similar rather than offsetting.

## The Constraint Multiplication Effect

### Degrees of Freedom Analysis

**Unconstrained portfolio**: 6 degrees of freedom (6 assets - 1 budget constraint)

**Single stakable asset**: 4 degrees of freedom (6 assets - 1 budget - 1 overweight constraint)

**Two stakable assets**: 3 degrees of freedom (6 assets - 1 budget - 2 overweight constraints)

Each additional constraint reduces the optimizer's ability to minimize risk.

### Geometric Interpretation

Think of the optimization as finding the closest point to the origin (minimum variance) on a constrained surface:

1. **Single constraint**: We're restricted to a hyperplane, but have flexibility within it
2. **Two constraints**: We're restricted to the intersection of two hyperplanes (a lower-dimensional space)
3. **The intersection point is farther from the origin than either hyperplane's closest point**

## Empirical Verification

From our implementation:
- k_ETH_ETH = 0.00001078
- k_SOL_SOL = 0.00000380
- k_ETH_SOL = 0.00000080 > 0 ✓

The positive k_ETH_SOL confirms that v_ETH and v_SOL are positively correlated through the covariance matrix.

## When Would We See Benefits?

Correlation benefits (k_ETH_SOL < 0) would occur if:

1. **Negative Correlation**: If ETH and SOL were negatively correlated, their overweights might partially offset each other's risk.

2. **Different Risk Profiles**: If one asset was defensive while the other was aggressive relative to the benchmark.

3. **Complementary Constraints**: If the constraints pushed the portfolio in opposite directions that happened to reduce overall variance.

## The Time-Segmentation Amplifier

The different unbonding periods create an additional cost:

**Days 1-2**: Both constraints active → Full correlation cost
**Days 3-10**: Only ETH constraint → No cross-term

If both assets had the same unbonding period, at least the time-segmentation complexity would disappear. The different periods mean we experience the worst of both worlds: correlation costs when both are active, then continued single-asset risk afterward.

## Practical Implications

### 1. Staking Strategy

The correlation cost suggests:
- Staking two assets simultaneously is riskier than the sum of individual risks
- Consider staggering staking positions rather than staking all at once
- The most correlated assets create the highest costs when staked together

### 2. Risk Budgeting

When allocating risk budget:
- Don't assume two-asset staking provides diversification benefits
- Account for the correlation cost in tracking error calculations
- The exact two-asset formula is essential; independence approximations underestimate risk

### 3. Asset Selection

When considering two stakable assets, prefer:
- Assets with low or negative correlations
- Assets with similar unbonding periods (reduces time complexity)
- Assets that serve different roles in the portfolio

## Conclusion

The correlation "benefit" becoming a cost reflects a fundamental principle: **constraints reduce optimization flexibility**. When we force two overweights simultaneously, we're not diversifying risk—we're compounding constraints.

This is analogous to the difference between:
- **Voluntary diversification**: Choosing multiple assets to reduce risk
- **Forced diversification**: Being required to hold specific assets regardless of risk

In two-asset staking, we have forced overweights, not voluntary diversification. The mathematical framework correctly captures this through positive cross-terms that increase, rather than decrease, tracking error.