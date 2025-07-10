# Two-Component Staking Benefit Formulation

## Overview

This document derives the mathematical formulation for calculating the expected benefit from staking in the context of the Two-Asset Tracking Error framework. The benefit calculation balances the yield earned from staking against the tracking error costs incurred from reduced liquidity during redemption episodes.

## The Two Components of Staking Benefit

The total staking benefit consists of two distinct components:

1. **Benefit above current staking levels**: The yield earned from staking above a baseline level (assumed to be 70%)
2. **Extra benefit from marginal overweight**: The yield earned by the marginal overweight percentage during redemption episodes above the `(1 - staking_pct)` threshold

## Mathematical Derivation

### Component 1: Benefit Above Baseline Staking

For an asset with weight `w`, staking percentage `s`, baseline staking `s₀`, and annual yield `y`:

```
B₁ = w × (s - s₀) × y
```

**Rationale**: This represents the incremental yield from staking beyond the market's baseline level. If everyone stakes at 70% (baseline), staking at 90% provides an additional 20% exposure to staking yields.

**Constraints**:
- If `s < s₀`, then `B₁ = 0` (no benefit below baseline)
- Typically `s₀ = 0.70` (70% baseline staking)

### Component 2: Marginal Overweight Benefit

During redemption episodes, when redemption size `R > τ = (1 - s)`, the fund must overweight the asset by `(R - τ)` to maintain the staking percentage. This marginal overweight also earns staking yield.

#### Step 1: Expected Marginal Overweight

The expected marginal overweight per redemption episode is:

```
E[max(0, R - τ)] = Σᵢ P(R = rᵢ) × max(0, rᵢ - τ)
```

For the discrete redemption distribution:
- P(5%) = 67%, P(10%) = 17%, P(20%) = 11%, P(30%) = 6%
- With τ = 0.10 (90% staking), only 20% and 30% redemptions create overweight

#### Step 2: Time-Weighted Benefit

The marginal overweight earns yield for the duration of the unbonding period:

```
Time fraction = (λ × d) / 365
```

Where:
- λ = expected redemptions per year (18)
- d = unbonding period in days (10 for ETH, 2 for SOL)
- 365 = days per year

#### Step 3: Marginal Benefit Formula

```
B₂ = w × y × (λ × d / 365) × E[max(0, R - τ)]
```

### Combined Formula

The total benefit for each asset is:

```
Benefit = w × y × [(s - s₀) + (λ × d / 365) × E[max(0, R - (1 - s))]]
```

## Two-Asset Extension

For ETH and SOL with different unbonding periods:

### ETH Benefit
```
Benefit_ETH = w_ETH × y × [(s_ETH - s₀) + (λ × d_ETH / 365) × E[max(0, R - (1 - s_ETH))]]
```

### SOL Benefit
```
Benefit_SOL = w_SOL × y × [(s_SOL - s₀) + (λ × d_SOL / 365) × E[max(0, R - (1 - s_SOL))]]
```

### Total Benefit
```
Total Benefit = Benefit_ETH + Benefit_SOL
```

## Numerical Example

Consider the following parameters:
- ETH: weight = 10.49%, staking = 90%, d = 10 days
- SOL: weight = 3.87%, staking = 90%, d = 2 days
- Baseline staking: 70%
- Annual yield: 5%
- λ = 18 redemptions/year

### ETH Calculation

**Component 1**:
```
B₁_ETH = 0.1049 × (0.90 - 0.70) × 0.05 = 0.1049%
```

**Component 2**:
```
E[max(0, R - 0.10)] = 0.111 × 0.10 + 0.056 × 0.20 = 0.0222
B₂_ETH = 0.1049 × 0.05 × (18 × 10 / 365) × 0.0222 = 0.0057%
```

**Total ETH Benefit**: 0.1049% + 0.0057% = 0.1106%

### SOL Calculation

**Component 1**:
```
B₁_SOL = 0.0387 × (0.90 - 0.70) × 0.05 = 0.0387%
```

**Component 2**:
```
B₂_SOL = 0.0387 × 0.05 × (18 × 2 / 365) × 0.0222 = 0.0004%
```

**Total SOL Benefit**: 0.0387% + 0.0004% = 0.0391%

### Combined Total
```
Total Benefit = 0.1106% + 0.0391% = 0.1497% ≈ 15 basis points
```

## Net Benefit Analysis

The net benefit accounts for both the staking yield benefit and the tracking error cost:

```
Net Benefit = Total Staking Benefit - Tracking Error Cost
```

Where the tracking error cost is typically approximated as:
```
TE Cost ≈ TE × √(2/π) × 0.5
```

This represents the expected shortfall from tracking error under normal distribution assumptions. In other words, it is the expected tracking error when the value is negative. We use this as a proxy for the expected tracking difference cost.

## Implementation Considerations

1. **Baseline Sensitivity**: The choice of baseline staking percentage significantly impacts Component 1
2. **Yield Variability**: Staking yields may vary with total staking levels (not modeled here)
3. **Liquidity Costs**: Higher staking may incur additional liquidity costs beyond tracking error
4. **Time Dynamics**: The model assumes constant redemption patterns and yields

## Validation

The implementation has been validated through:
1. Manual calculation verification matching implementation results to 4 decimal places
2. Edge case testing (staking at baseline, 100% staking)
3. Scenario analysis across different staking levels and yields

## Conclusion

The two-component benefit formulation provides a more nuanced view of staking benefits by:
- Separating baseline benefits from marginal overweight benefits
- Accounting for the time value of overweight positions
- Incorporating asset-specific unbonding periods
- Maintaining mathematical consistency with the tracking error framework

This formulation enables optimal staking decisions that balance yield opportunities against liquidity risks in a mathematically rigorous manner.