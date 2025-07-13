# Analytical Tracking Error Formula for Staked ETH Portfolios

## The Unique Formula

The annual tracking error for a portfolio with staked ETH subject to redemptions is:

```
TE = √[λ × d × eth_weight² × (v' Σ v) × E[(R - τ)²₊]]
```

Where:
- λ = expected number of redemptions
- d = duration per episode (days)
- eth_weight = ETH's benchmark weight
- v = optimal hedge vector from Lagrange optimization
- Σ = asset covariance matrix
- R = random redemption size
- τ = 1 - staking_pct (redemption threshold)
- (x)₊ = max(0, x)

## Complete Mathematical Derivation

### 1. Problem Setup

We have a portfolio tracking a benchmark index where ETH can be staked. When redemptions occur:
- Staked ETH cannot be used for redemptions
- This forces ETH overweighting in the remaining portfolio
- The overweighting creates tracking error

### 2. ETH Overweight Calculation

When a fraction `r` of NAV is redeemed:
- ETH share of redemption: `r × eth_weight`
- Available liquid ETH: `eth_weight × (1 - staking_pct)`
- Required overweight: `δ_ETH = max(0, r × eth_weight - eth_weight × (1 - staking_pct))`

Simplifying:
```
δ_ETH = eth_weight × max(0, r - (1 - staking_pct))
δ_ETH = eth_weight × (r - τ)₊
```

where τ = 1 - staking_pct is the threshold below which no overweight is needed.

### 3. Active Weight Optimization

To minimize tracking error, we solve for optimal active weights **a** subject to:
1. Portfolio remains fully invested: Σᵢ aᵢ = 0
2. ETH overweight constraint: a_ETH = δ_ETH

Using Lagrange multipliers:

**Minimize**: f(a) = ½ a' Σ a

**Subject to**: C a = c

Where:
```
C = [1  1  ...  1]    (sum-to-zero)
    [0  1  0 ... 0]   (ETH-specific)

c = [0, δ_ETH]'
```

### 4. Lagrange Solution

The Lagrangian: L(a, λ) = ½ a' Σ a - λ' (C a - c)

First-order conditions:
- ∂L/∂a = 0 ⟹ Σ a = C' λ
- ∂L/∂λ = 0 ⟹ C a = c

Solving:
- a = Σ⁻¹ C' λ
- C Σ⁻¹ C' λ = c
- λ = (C Σ⁻¹ C')⁻¹ c

Therefore:
```
a* = Σ⁻¹ C' (C Σ⁻¹ C')⁻¹ c
```

### 5. Linear Structure

Since c = [0, δ_ETH]' = δ_ETH × [0, 1]', we have:
```
a* = δ_ETH × Σ⁻¹ C' (C Σ⁻¹ C')⁻¹ [0, 1]'
a* = δ_ETH × v
```

where v is a fixed vector depending only on the covariance structure.

### 6. Tracking Error Variance

The tracking error variance is:
```
Var(TE) = a' Σ a = (δ_ETH × v)' Σ (δ_ETH × v)
        = δ_ETH² × (v' Σ v)
```

Substituting δ_ETH = eth_weight × (r - τ)₊:
```
Var(TE) = eth_weight² × (r - τ)²₊ × (v' Σ v)
```

### 7. Defining base_k

We define:
```
base_k ≡ eth_weight² × (v' Σ v)
```

This gives us:
```
Var(TE) = base_k × (r - τ)²₊
```

### 8. Stochastic Redemptions

For a stochastic redemption process:
- N ~ Poisson(λ): number of redemptions
- Rᵢ: independent redemption sizes from distribution F_R
- Each episode has duration d days

The total variance-days is:
```
Total Var-Days = Σᵢ₌₁ᴺ Var(TEᵢ) × d
                = d × Σᵢ₌₁ᴺ base_k × (Rᵢ - τ)²₊
                = d × base_k × Σᵢ₌₁ᴺ (Rᵢ - τ)²₊
```

### 9. Expected Tracking Error

Taking expectations:
```
E[Total Var-Days] = d × base_k × E[Σᵢ₌₁ᴺ (Rᵢ - τ)²₊]
                  = d × base_k × E[N] × E[(R - τ)²₊]
                  = λ × d × base_k × E[(R - τ)²₊]
```

The annual tracking error is:
```
TE = √(E[Total Var-Days])
   = √[λ × d × base_k × E[(R - τ)²₊]]
   = √[λ × d × eth_weight² × (v' Σ v) × E[(R - τ)²₊]]
```

## Key Components Explained

### 1. Market Structure: (v' Σ v)
This term captures how efficiently the portfolio can hedge the ETH overweight:
- Depends on correlations between assets
- Smaller when BTC-ETH correlation is high (easier to hedge)
- Represents the "cost" of the constrained optimization

### 2. Threshold Effect: E[(R - τ)²₊]
This term captures the non-linear impact of redemptions:
- Zero for redemptions below τ = 1 - staking_pct
- Quadratic growth above the threshold
- Creates a "safety buffer" for small redemptions

### 3. Scaling Factors
- √λ: TE grows with square root of redemption frequency
- √d: TE grows with square root of episode duration
- eth_weight: Direct proportionality to ETH's importance

## Special Cases

### 1. Deterministic Single Redemption
If R = r₀ (fixed):
```
TE = √[d × eth_weight² × (v' Σ v) × (r₀ - τ)²₊]
```

### 2. No Staking (τ = 1)
No redemptions require overweight since all ETH is liquid:
```
E[(R - 1)²₊] = 0 for all R ∈ [0, 1]
Therefore: TE = 0
```

### 3. Full Staking (τ = 0)
Maximum overweight needed:
```
E[(R - 0)²₊] = E[R²]
```

### 4. Discrete Schedule
For episodes (r₁, n₁), (r₂, n₂), ...:
```
TE = √[d × eth_weight² × (v' Σ v) × Σᵢ nᵢ(rᵢ - τ)²₊]
```

## Practical Implications

1. **Risk Management**: The formula shows TE is minimized by:
   - Reducing staking percentage (increases τ, and TE = 0 when staking_pct = 0)
   - Decreasing redemption frequency (λ)
   - Shortening episode durations (d)

2. **Threshold Planning**: Redemptions below (1 - staking_pct) create no tracking error

3. **Correlation Benefits**: High BTC-ETH correlation reduces (v' Σ v)

4. **Non-Linear Scaling**: TE does not scale linearly with redemption size due to (r - τ)²₊

## Conclusion

The analytical formula:
```
TE = √[λ × d × eth_weight² × (v' Σ v) × E[(R - τ)²₊]]
```

provides a complete characterization of tracking error for staked ETH portfolios. It captures:
- The optimization structure through (v' Σ v)
- The staking constraint through the threshold τ
- The redemption dynamics through the distribution of R
- The time dimension through λ and d

This formula enables rapid risk assessment, sensitivity analysis, and optimal staking decisions without requiring simulation.

## Redemption Size Distributions and E[(R - τ)²₊]

The key stochastic component in the formula is **E[(R - τ)²₊]**, which depends on the distribution of redemption sizes. This section explains how different distributions affect tracking error and which is used in practice.

### Mathematical Definition

For any redemption size distribution F_R:

```
E[(R - τ)²₊] = ∫₀¹ max(0, r - τ)² dF_R(r)
```

For discrete distributions:
```
E[(R - τ)²₊] = Σᵢ P(R = rᵢ) × max(0, rᵢ - τ)²
```

### Common Distributions and Their Impact

#### 1. Homogeneous Distribution
All redemptions have the same size r₀:
```
P(R = r₀) = 1
E[(R - τ)²₊] = (r₀ - τ)²₊
```
- Simplest case: TE calculation is deterministic
- Used when redemption size is predictable

#### 2. Two-Point Distribution
Models bimodal patterns (e.g., retail vs institutional):
```
P(R = r₁) = p,  P(R = r₂) = 1-p
E[(R - τ)²₊] = p(r₁ - τ)²₊ + (1-p)(r₂ - τ)²₊
```
- Captures heterogeneous investor behavior
- Useful for scenario analysis

#### 3. Beta Distribution
Continuous distribution on [0,1]:
```
R ~ Beta(α, β)
E[(R - τ)²₊] = ∫ᵤ¹ (r - τ)² × [r^(α-1)(1-r)^(β-1)]/B(α,β) dr
```
- Flexible shapes from uniform to highly skewed
- Natural choice for modeling percentages

#### 4. Empirical Distribution
Uses historical redemption data:
```
P(R = rᵢ) = nᵢ/N  where nᵢ is frequency of redemption size rᵢ
E[(R - τ)²₊] = Σᵢ (nᵢ/N) × (rᵢ - τ)²₊
```
- Most accurate for backtesting
- Captures actual redemption patterns

### Implementation in core/stochastic_redemption_model.py

The implementation uses an **empirical discrete distribution** constructed from the redemption schedule. For the standard schedule:

```python
schedule = [
    (0.05, 12, 10),  # 5% redemptions, 12 episodes
    (0.10, 3, 10),   # 10% redemptions, 3 episodes
    (0.20, 2, 10),   # 20% redemptions, 2 episodes
    (0.30, 1, 10),   # 30% redemption, 1 episode
]
```

This creates:
```
P(R = 0.05) = 12/18 = 0.667
P(R = 0.10) = 3/18 = 0.167
P(R = 0.20) = 2/18 = 0.111
P(R = 0.30) = 1/18 = 0.056
```

### Calculating E[(R - τ)²₊] for Different Staking Levels

With τ = 1 - staking_pct, for the empirical distribution above:

#### 80% Staking (τ = 0.2):
```
E[(R - τ)²₊] = 0.667×0 + 0.167×0 + 0.111×0 + 0.056×(0.3-0.2)²
              = 0.056 × 0.01 = 0.00056
```
Only 30% redemptions create tracking error.

#### 90% Staking (τ = 0.1):
```
E[(R - τ)²₊] = 0.667×0 + 0.167×0 + 0.111×(0.2-0.1)² + 0.056×(0.3-0.1)²
              = 0.111×0.01 + 0.056×0.04 = 0.00111 + 0.00224 = 0.00335
```
Both 20% and 30% redemptions create tracking error.

#### 95% Staking (τ = 0.05):
```
E[(R - τ)²₊] = 0.667×0 + 0.167×(0.1-0.05)² + 0.111×(0.2-0.05)² + 0.056×(0.3-0.05)²
              = 0.167×0.0025 + 0.111×0.0225 + 0.056×0.0625
              = 0.000417 + 0.002500 + 0.003472 = 0.006389
```
All except 5% redemptions create tracking error.

### Distribution Choice Guidelines

1. **For Risk Assessment**: Use empirical distribution from historical data
2. **For Scenario Analysis**: Use two-point or discrete mixtures
3. **For Theoretical Analysis**: Use Beta distribution for smooth sensitivity
4. **For Conservative Estimates**: Use distribution with higher variance

### Key Insight: Threshold Creates Non-Linearity

The term E[(R - τ)²₊] introduces fundamental non-linearity:
- Below threshold: Zero contribution regardless of frequency
- Above threshold: Quadratic growth in tracking error
- Distribution shape matters only for R > τ

This explains why:
- Small frequent redemptions may cause less TE than rare large ones
- Increasing staking from 70% to 80% may have minimal impact
- Increasing staking from 90% to 95% can dramatically increase TE