# Stochastic Redemption Modeling for Tracking Error Analysis

## Executive Summary

This document presents an analytical framework for modeling tracking error in ETF portfolios using a compound Poisson process. This approach provides a mathematically elegant alternative to discrete episode-based calculations, enabling sensitivity analysis, risk budgeting, and uncertainty quantification.

## Mathematical Foundation

### The Challenge

In portfolios with staked ETH, redemptions create tracking error through forced ETH overweighting. The traditional approach lists discrete episodes:

```
episodes = [(redemption_pct₁, duration₁), (redemption_pct₂, duration₂), ...]
```

For each episode, the tracking error contribution is:
```
TE_episode = √(variance × duration_days)
```

where variance is quadratic in the redemption percentage:
```
variance ∝ (redemption_pct)²
```

### Compound Poisson Process Framework

We model redemptions as a compound Poisson process:

- **N ~ Poisson(λ)**: Number of redemptions in the observation period
- **R₁, R₂, ..., Rₙ**: Independent redemption sizes from distribution F_R

The total squared redemptions become:
```
S = Σᵢ₌₁ᴺ Rᵢ²
```

### Key Mathematical Results

For the compound sum S, we have:

**Expected Value:**
```
E[S] = E[N] × E[R²] = λ × (μ_R² + σ_R²)
```

**Variance:**
```
Var[S] = λ × E[R⁴] - λ(λ-1) × (E[R²])²
```

where:
- μ_R = E[R] is the expected redemption size
- σ_R² = Var[R] is the variance of redemption sizes
- E[R⁴] is the fourth moment of the redemption distribution

### Tracking Error Formula

For episodes with constant duration d days, the tracking error must account for the non-linear relationship between variance and redemption size:

```
variance(r) = base_k × max(0, r - (1 - staking_pct))²
```

where:
- `base_k = eth_weight² × (v' Σ v)` from the optimization
- The threshold `(1 - staking_pct)` determines when ETH overweighting begins

**Important**: The variance is NOT proportional to `r²`, but to `(r - threshold)²`. This means the effective k-factor varies with redemption size:

```
k_effective(r) = base_k × [(r - threshold)/r]²
```

For stochastic redemptions:
```
TE_analytical = √(λ × E[variance(R)] × d)
```

where `E[variance(R)]` must be calculated considering the truncated quadratic relationship.

## Implementation Details

### Redemption Size Distributions

The framework supports multiple distributions for modeling redemption sizes:

#### 1. Homogeneous Distribution
All redemptions have the same size r₀:
```
P(R = r₀) = 1
μ_R = r₀, σ_R² = 0
```

#### 2. Two-Point Distribution
Models bimodal redemption patterns:
```
P(R = r₁) = p,  P(R = r₂) = 1-p
μ_R = p×r₁ + (1-p)×r₂
σ_R² = p(1-p)(r₁-r₂)²
```

#### 3. Beta Distribution
Continuous distribution on [0,1] with flexible shape:
```
R ~ Beta(α, β)
μ_R = α/(α+β)
σ_R² = αβ/[(α+β)²(α+β+1)]
```

#### 4. Empirical Distribution
Directly uses observed redemption patterns from historical data.

### Confidence Intervals

Using the Central Limit Theorem for large λ:

```
S ≈ N(λ×E[R²], λ×Var[R²])
```

This provides confidence intervals for tracking error:
```
TE ∈ [√(k×d×CI_lower), √(k×d×CI_upper)]
```

## Practical Applications

### 1. Risk Budgeting

Given a tracking error budget TE_max, solve for acceptable parameters:

```
λ × (μ_R² + σ_R²) ≤ TE_max²/(k×d)
```

This constraint defines feasible combinations of redemption frequency and size.

### 2. Sensitivity Analysis

The analytical formula enables quick computation of tracking error sensitivity:

**Frequency Sensitivity:**
```
∂TE/∂λ = (k×d×(μ_R²+σ_R²))/(2×TE)
```

**Mean Size Sensitivity:**
```
∂TE/∂μ_R = (2×k×d×λ×μ_R)/(2×TE)
```

**Variance Sensitivity:**
```
∂TE/∂σ_R² = (k×d×λ)/(2×TE)
```

### 3. Scenario Comparison

Different redemption scenarios can be quickly evaluated:

- **Low frequency, large size**: λ=5, μ_R=0.2
- **High frequency, small size**: λ=50, μ_R=0.02
- **Mixed pattern**: Two-point distribution modeling institutional vs retail

## Validation Against Discrete Episodes

The analytical model exactly matches discrete episodes when:

1. **Moment Preservation**: The sum of squared redemptions equals the analytical expectation
2. **Independence**: Redemption sizes are independent
3. **Stationarity**: The redemption process is time-homogeneous

### Example Validation

Discrete schedule:
- 12 × 5% redemptions = 12 × 0.0025 = 0.03
- 3 × 10% redemptions = 3 × 0.01 = 0.03
- 2 × 20% redemptions = 2 × 0.04 = 0.08
- 1 × 30% redemption = 1 × 0.09 = 0.09

Total: Σ(rᵢ²) = 0.23

Analytical model with λ=18:
```
E[R²] = 0.23/18 ≈ 0.0128
```

This can be achieved with a properly calibrated distribution.

## Critical Insight: Non-Constant k-Factor

A key discovery in our analysis is that the relationship between variance and redemption size is fundamentally non-linear due to the threshold effect of staking. The variance follows:

```
variance(r) = base_k × (r - (1 - staking_pct))²  for r > (1 - staking_pct)
variance(r) = 0                                    for r ≤ (1 - staking_pct)
```

This creates an effective k-factor that varies with redemption size. The following table shows values for a scenario where 80% of ETH is staked (threshold = 20%):

| Redemption | Effective k/base_k | Implication |
|------------|-------------------|-------------|
| 20%        | 0.000            | No overweight needed |
| 30%        | 0.111            | Minimal variance |
| 50%        | 0.360            | Moderate variance |
| 100%       | 0.640            | Approaches staking_pct² |

### Implications for Risk Management

1. **Small Redemptions**: Have disproportionately low impact due to the threshold
2. **Large Redemptions**: Generate variance approaching `base_k × staking_pct²`
3. **Risk Budgeting**: Must account for the redemption size distribution, not just the mean
4. **Naive Models**: Using constant k can overestimate risk by 100%+ for typical redemption patterns

## Advantages and Limitations

### Advantages

1. **Computational Efficiency**: Instant calculation vs iterative simulation
2. **Analytical Insights**: Closed-form sensitivity analysis
3. **Uncertainty Quantification**: Natural confidence intervals
4. **Parameter Optimization**: Enables constrained optimization
5. **Scalability**: Handles large numbers of redemptions efficiently

### Limitations

1. **Independence Assumption**: Cannot model correlated redemptions
2. **Stationarity Requirement**: Assumes time-homogeneous process
3. **Distribution Selection**: Requires appropriate choice of F_R
4. **Tail Risk**: May underestimate extreme events
5. **Path Dependence**: Cannot capture sequential effects

## Usage Example

```python
from core.stochastic_redemption_model import StochasticRedemptionAnalyzer
from core.stochastic_redemption_model import BetaDistribution

# Configure stochastic model
analyzer = StochasticRedemptionAnalyzer(
    market_config=market,
    staking_config=staking
)

# Define redemption distribution
redemption_dist = BetaDistribution(alpha=2, beta=8)  # Mean=0.2, moderate variance

# Analyze with λ=20 redemptions over 10 days
results = analyzer.analyze_stochastic(
    expected_redemptions=20,
    redemption_dist=redemption_dist,
    duration_days=10
)

print(f"Expected TE: {results.expected_te:.2%}")
print(f"95% CI: [{results.ci_lower:.2%}, {results.ci_upper:.2%}]")
```

## Conclusion

The compound Poisson process framework provides a powerful analytical tool for tracking error analysis. While the discrete episode approach remains valuable for deterministic schedules and scenario analysis, the stochastic model enables:

- Rapid sensitivity analysis
- Risk budgeting with constraints
- Uncertainty quantification
- Parameter optimization

The choice between approaches depends on the specific use case:
- Use **discrete episodes** for: Fixed schedules, scenario analysis, path-dependent effects
- Use **stochastic modeling** for: Risk limits, sensitivity analysis, large-scale simulation

Both approaches are mathematically consistent when properly calibrated, providing complementary tools for portfolio risk management.