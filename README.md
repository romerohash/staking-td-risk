# Staking Percentage x Tracking Difference Risk

## Executive Summary

This document explains the advanced mathematical framework for managing ETH staking risk in portfolios tracking the Nasdaq Crypto US (NCI-US) index. Through rigorous mathematical analysis, we have derived an **analytical closed-form formula** for tracking error that accounts for the non-linear effects of staking-induced illiquidity. The framework has evolved from discrete episode modeling to a unified stochastic approach, enabling rapid risk assessment and optimal staking decisions.

## Problem Statement

### Context
- **Index**: Nasdaq Crypto US (NCI-US) with six assets:
  - BTC: 78.69%
  - ETH: 10.49%
  - XRP: 5.49%
  - SOL: 3.87%
  - ADA: 1.19%
  - XLM: 0.27%
- **Challenge**: ETH staking creates illiquidity - staked ETH cannot be immediately sold to meet redemptions
- **Goal**: Minimize tracking error while capturing staking yields

### Key Constraints

#### Tracking Difference Budget
The fund operates under strict tracking difference limits:
- **Maximum annual tracking difference**: 1.5% (150 basis points)
- **Current operational costs**: ~1.46% (146 basis points)
- **Remaining budget**: 4 basis points (0.04%)

This means the staking strategy can have a Total Net Benefit as low as -4 bps while keeping the fund's overall tracking difference within the 1.5% commitment.

#### Redemption-Driven Constraints
When redemptions occur and ETH is staked:
1. Cannot sell staked ETH proportionally 
2. Must sell other assets disproportionately
3. This creates underweights in liquid assets
4. To rebalance back to benchmark weights, must overweight ETH

## Mathematical Framework

### 1. The Analytical Tracking Error Formula

Through rigorous mathematical derivation, we have discovered the closed-form formula for annual tracking error:

```
TE = √[λ × d × eth_weight² × (v' Σ v) × E[(R - τ)²₊]]
```

Where:
- **λ**: Expected number of redemptions
- **d**: Duration per episode (days)
- **eth_weight²**: ETH's benchmark weight squared (0.1049² = 0.011)
- **(v' Σ v)**: Market structure term from Lagrange optimization (~0.000964)
- **E[(R - τ)²₊]**: Expected squared excess redemption above threshold
- **τ = 1 - staking_pct**: Redemption threshold

**Key Insight**: This formula reveals that tracking error depends on a non-constant k-factor that varies with redemption size due to threshold effects.

### 2. Threshold Effects and Non-Linear Variance

The variance relationship is fundamentally non-linear:

```
Variance(r) = base_k × (r - τ)²₊
```

Where:
- **base_k = eth_weight² × (v' Σ v)** (~0.000011)
- **(r - τ)₊ = max(0, r - τ)**: Only redemptions exceeding the threshold contribute

This creates a "safety buffer" where small redemptions create zero tracking error:
- If redemption_pct ≤ (1 - staking_pct): No ETH overweight needed
- If redemption_pct > (1 - staking_pct): Quadratic growth in tracking error

### 3. Delta ETH Calculation

The required ETH overweight for a given redemption:

```
δ_ETH = eth_weight × max(0, redemption_pct - (1 - staking_pct))
```

This threshold relationship explains why:
- 70% staking rarely requires overweights
- 80% staking only affects large redemptions
- 90%+ staking makes most redemptions problematic

### 4. Optimal Active Weight Vector

Using Lagrange multipliers, we solve for the risk-minimizing active weights:

```
a* = δ_ETH × v
```

Where **v** is the optimal hedge vector satisfying:
- v[ETH] = 1 (constrained)
- Σv = 0 (sum-to-zero)
- v minimizes variance given covariance structure

For our market:
- v[BTC] ≈ -0.532 (bears most offset due to 0.70 correlation with ETH)
- v[others] ≈ -0.08 to -0.14 (proportional adjustments)

### 5. Stochastic Redemption Modeling

We model redemptions as a compound Poisson process:
- **N ~ Poisson(λ)**: Number of redemptions
- **R_i**: Redemption sizes from distribution F_R

This enables analytical calculation of:
```
E[(R - τ)²₊] = ∫₀¹ max(0, r - τ)² dF_R(r)
```

For discrete distributions:
```
E[(R - τ)²₊] = Σᵢ P(R = rᵢ) × max(0, rᵢ - τ)²
```

## Implementation Innovations

### 1. Redemption Size Distributions

The framework supports multiple distribution models:

#### Empirical Distribution (Default)
Based on historical redemption patterns:
- P(R = 5%) = 67% (frequent small redemptions)
- P(R = 10%) = 17% (medium redemptions)
- P(R = 20%) = 11% (large redemptions)
- P(R = 30%) = 6% (rare large redemptions)

#### Two-Point Distribution
Models bimodal patterns (retail vs institutional):
```
P(R = r₁) = p,  P(R = r₂) = 1-p
E[(R - τ)²₊] = p(r₁ - τ)²₊ + (1-p)(r₂ - τ)²₊
```

### 2. Analytical vs Discrete Validation

Our enhanced stochastic model (`core/stochastic_redemption_model.py`) demonstrates:
- **Exact match**: Analytical and discrete approaches yield identical results
- **Numerical precision**: Differences < 10⁻¹⁵
- **Monte Carlo confirmation**: Simulations validate the analytical formula

### 3. Base-k Calculation

The base-k parameter is computed from market structure:
```python
# From Lagrange optimization
base_k = eth_weight² × (v' Σ v)
# For our market: base_k ≈ 0.000011
```

This captures how efficiently the portfolio can hedge ETH overweights.

## Two-Asset Tracking Error Formula

### Extension to Two Stakable Assets

The framework has been extended to handle the specific case of two stakable assets with different unbonding periods. For ETH (10-day unbonding) and SOL (2-day unbonding), the analytical formula becomes:

```
TE = √[λ × (d_short × E[Var_full] + (d_long - d_short) × E[Var_partial])]
```

Where:
- **d_short**: Minimum unbonding period (2 days for SOL)
- **d_long**: Maximum unbonding period (10 days for ETH)
- **E[Var_full]**: Expected variance when both assets are overweighted (days 1-2)
- **E[Var_partial]**: Expected variance when only ETH is overweighted (days 3-10)

### Time-Segmented Variance

The variance calculation accounts for different time periods:

**Days 1-2 (Both assets overweighted):**
```
Var_full(r) = k_ETH_ETH × (r - τ_ETH)²₊ + 
              2 × k_ETH_SOL × (r - τ_ETH)₊ × (r - τ_SOL)₊ + 
              k_SOL_SOL × (r - τ_SOL)²₊
```

**Days 3-10 (Only ETH overweighted):**
```
Var_partial(r) = k_ETH_ETH × (r - τ_ETH)²₊
```

### Cross-Asset k-Components

The k-components capture the interaction between assets:
- **k_ETH_ETH = eth_weight² × (v_ETH' Σ v_ETH)**: ETH's self-contribution
- **k_SOL_SOL = sol_weight² × (v_SOL' Σ v_SOL)**: SOL's self-contribution  
- **k_ETH_SOL = eth_weight × sol_weight × (v_ETH' Σ v_SOL)**: Cross-term

### Correlation Cost Discovery

A counterintuitive finding: **k_ETH_SOL > 0**, meaning the cross-term increases tracking error rather than reducing it. This occurs because:

1. **Constraint Competition**: ETH and SOL constraints compete for the same hedge assets
2. **Reduced Degrees of Freedom**: Each additional constraint limits the optimizer's flexibility
3. **Positive Correlation**: ETH and SOL are positively correlated (ρ ≈ 0.60)

Example with 90% staking for both assets:
- ETH-only TE: 0.2572%
- SOL-only TE: 0.0425%
- Independence approximation: √(0.2572² + 0.0425²) = 0.2607%
- Exact two-asset TE: 0.2632%
- **Correlation cost: 0.0025% (1.0% increase)**

## Key Findings and Insights

### 1. Threshold-Driven Risk Profile

| Staking % | Threshold | Risk Characteristics |
|-----------|-----------|---------------------|
| 70% | 0.30 | Zero TE for redemptions ≤ 30% |
| 80% | 0.20 | Only 30% redemptions create TE |
| 90% | 0.10 | 10%, 20%, 30% redemptions create TE |
| 95% | 0.05 | All but 5% redemptions create TE |

### 2. Non-Linear Tracking Error Growth

With empirical redemption distribution:
- 70% staking: TE = 0.00% (below all thresholds)
- 80% staking: TE = 0.10% (minimal impact)
- 90% staking: TE = 0.25% (moderate impact)
- 95% staking: TE = 0.35% (significant impact)

### 3. Distribution Sensitivity

Different redemption patterns dramatically affect optimal staking:
- **Conservative** (5%/20% mix): Can stake up to 90%
- **Aggressive** (2%/50% mix): Should limit staking to 70%
- **Institutional** (large rare redemptions): High staking becomes risky

### 4. Mathematical Validation

Key validations from our analysis:
- **k-factor varies**: From 0 at threshold to base_k × staking_pct²
- **Naive constant-k models**: Can have 100%+ error
- **Threshold creates discontinuity**: Small changes near threshold have large impacts

## Practical Applications

### 1. Rapid Risk Assessment

The analytical formula enables instant calculation without simulation:
```python
# Example: 80% staking, empirical distribution
E_squared_excess = 0.000556  # Pre-calculated for distribution
TE = sqrt(18 × 10 × 0.000011 × 0.000556) = 0.103%
```

### 2. Optimal Staking Decision

Given tracking error budget, solve for maximum staking:
```
staking_max = 1 - τ_max
where τ_max solves: TE_budget² = λ × d × base_k × E[(R - τ_max)²₊]
```

### 3. Scenario Analysis

Two-point distribution analysis reveals:
- Small frequent + rare large redemptions → Higher staking viable
- Uniform medium redemptions → Lower staking optimal
- Distribution shape matters more than mean

### 4. Break-Even Analysis

Incorporating staking yields:
- **Net Benefit = Staking Yield Benefits - Expected Shortfall**
- 80% staking: +1.28 bps net benefit
- 90% staking: +1.00 bps net benefit
- 95% staking: Approximately break-even
- 100% staking: -1.68 bps net cost

## Advanced Features

### 1. Confidence Intervals

Using Delta method for large λ:
```
TE ∈ [TE_mean - z×σ_TE, TE_mean + z×σ_TE]
```

### 2. Sensitivity Analysis

Elasticities from analytical derivatives:
- ∂TE/∂λ: Elasticity ≈ 0.5 (square root relationship)
- ∂TE/∂staking: Non-linear, highest near threshold
- ∂TE/∂mean_redemption: Depends on distribution shape

### 3. Model Comparison

| Approach | Advantages | Use Case |
|----------|------------|----------|
| Discrete Episodes | Exact for known schedule | Historical analysis |
| Analytical Formula | Instant calculation | Risk budgeting |
| Monte Carlo | Handles complex paths | Stress testing |

## Interactive Web Application

The framework includes a high-performance web application for real-time tracking error calculations and sensitivity analysis.

### Features

- **⚡ Lightning-Fast Performance**: Sub-100ms response times through Numba JIT optimization (30x speedup from ~3s to <100ms)
- **📊 Real-Time Visualizations**: Interactive 2D sensitivity heatmaps, tracking error decomposition, and yield vs risk trade-offs
- **🧮 Two-Asset Analysis**: Simultaneous ETH and SOL staking with time-segmented variance calculations
- **🎨 Modern UI**: Beautiful glassmorphism design with dark theme and intuitive parameter controls
- **📚 Integrated Documentation**: Built-in viewer for mathematical concepts and formulas

### Technical Stack

- **Backend**: FastAPI with Numba JIT compilation for mathematical computations
- **Frontend**: React 18 + TypeScript + Material-UI with Recharts visualizations
- **Deployment**: Docker container optimized for Railway.app deployment
- **Performance**: Pre-compiled Numba functions with persistent cache

### Quick Start

```bash
# Run with Docker (recommended)
cd optimal-staking-demo
docker build -t staking-demo .
docker run -p 8000:8000 staking-demo

# Or run locally
cd optimal-staking-demo/backend && uvicorn main:app --reload  # Backend on :8000
cd optimal-staking-demo/frontend && npm run dev              # Frontend on :5173
```

### Performance Benchmarks

- **API Response Time**: p50=45ms, p95=85ms, p99=95ms
- **Sensitivity Analysis**: 31x31 grid calculated in ~50ms
- **Cold Start**: Eliminated through strategic Numba warmup

See `optimal-staking-demo/README.md` for detailed setup and deployment instructions.

## Implementation Guide

### Core Scripts

1. **`core/stochastic_redemption_model.py`**
   - Enhanced model with non-constant k-factor
   - Validates analytical vs discrete approaches
   - Provides confidence intervals

2. **`core/analytical_variance_model.py`**
   - Implements variance(r) = base_k × (r - τ)²₊
   - Demonstrates k-factor variation

3. **`core/two_point_distribution_analysis.py`**
   - Lightweight analytical TE calculator
   - Sensitivity analysis tools

4. **`core/verify_base_k.py`**
   - Numerical proof of base_k = eth_weight² × (v' Σ v)
   - Validates Lagrange optimization

5. **`core/two_asset_analytical_formula.py`**
   - Two-asset tracking error implementation (ETH + SOL)
   - Time-segmented variance calculation
   - Cross-asset hedging effects

6. **`core/verify_correlation_cost.py`**
   - Numerical verification of correlation cost in two-asset case
   - Tests various ETH/SOL staking combinations
   - Demonstrates constraint competition effect

7. **`core/two_point_sensitivity_plots.py`**
   - Generates sensitivity analysis visualizations
   - Explores parameter space for two-point distributions
   - Creates heatmaps for staking optimization

8. **`optimal-staking-demo/backend/test_performance.py`**
   - Performance benchmarking suite
   - Validates <100ms response time target
   - Tests Numba optimization effectiveness

### Key Documentation

- **`docs/analytical-tracking-error-formula.md`**: Complete mathematical derivation
- **`docs/stochastic-redemption-modeling.md`**: Compound Poisson process approach
- **`docs/base-k-derivation.md`**: Detailed proof of base_k formula
- **`docs/correlation-cost-explanation.md`**: Why two-asset staking creates correlation cost

## Limitations and Assumptions

1. **Correlation Stability**: Assumes constant correlations
2. **No Market Impact**: Doesn't account for transaction costs
3. **Independence**: Redemptions are independent (no herding)
4. **Linear Redemptions**: NAV-proportional redemptions

## Conclusion

This framework represents a significant advancement in ETF risk management:

1. **Analytical Breakthrough**: The closed-form TE formula eliminates simulation needs
2. **Threshold Discovery**: The (1 - staking_pct) threshold creates fundamental non-linearity
3. **Multi-Asset Extension**: Handles complex interactions between multiple stakable assets (ETH + SOL)
4. **Correlation Cost Insight**: Reveals how staking multiple assets creates competing constraints
5. **Production-Ready Implementation**: High-performance web application with sub-100ms calculations

The mathematical rigor combined with practical tools provides portfolio managers with:
- Instant risk calculation through analytical formulas
- Interactive exploration of staking parameter space
- Real-time visualization of tracking error decomposition
- Optimal staking decisions across multiple assets
- Scenario planning with different redemption distributions
- Precise risk budgeting within tracking difference constraints

By understanding that variance is proportional to (redemption - threshold)² rather than redemption², and that multi-asset staking creates correlation costs, managers can better navigate the staking/liquidity trade-off, potentially extending viable staking levels while maintaining acceptable tracking error.

## Appendix: Key Mathematical Results

### Formula Summary

| Component | Formula | Typical Value |
|-----------|---------|---------------|
| Threshold | τ = 1 - staking_pct | 0.2 (80% staking) |
| Delta ETH | δ_ETH = eth_weight × (r - τ)₊ | Variable |
| Base k | base_k = eth_weight² × (v' Σ v) | 0.000011 |
| Variance | var(r) = base_k × (r - τ)²₊ | Quadratic above τ |
| Annual TE | TE = √[λ × d × base_k × E[(R - τ)²₊]] | 0.1-0.5% |

### Redemption Distribution Impact

| Staking | E[(R - τ)²₊] | Annual TE | Contributing Redemptions |
|---------|--------------|-----------|-------------------------|
| 70% | 0.000000 | 0.00% | None |
| 80% | 0.000556 | 0.10% | 30% only |
| 90% | 0.003333 | 0.25% | 10%, 20%, 30% |
| 95% | 0.006389 | 0.35% | 5%, 10%, 20%, 30% |

These results demonstrate the power of the analytical approach in providing precise, actionable insights for portfolio management.