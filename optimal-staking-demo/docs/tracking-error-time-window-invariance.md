# Time Window Invariance of the Analytical Tracking Error Formula

## Executive Summary

A remarkable property of our analytical tracking error formula is its **time window invariance**: the formula remains unchanged whether calculating annual tracking error directly or computing it over shorter periods (e.g., 21 trading days) and then annualizing. This property has significant practical implications for ETF risk management, where tracking error is typically measured using rolling 21-day windows.

## The Formula

The analytical tracking error formula is:

```
TE = √[λ × d × eth_weight² × (v' Σ v) × E[(R - τ)²₊]]
```

Where:
- λ = expected number of redemptions **per year**
- d = duration per episode (days)
- Other parameters as previously defined

## Mathematical Proof of Time Window Invariance

### Setup

Consider calculating tracking error over a T-day window (e.g., T = 21) and then annualizing:

1. **Redemptions in T days**: λ_T = λ × (T/252)
2. **T-day tracking error**: TE_T = √[λ_T × d × eth_weight² × (v' Σ v) × E[(R - τ)²₊]]
3. **Annualized TE**: TE_annual = TE_T × √(252/T)

### Proof

Substituting the expressions:

```
TE_annual = TE_T × √(252/T)
         = √[λ_T × d × eth_weight² × (v' Σ v) × E[(R - τ)²₊]] × √(252/T)
         = √[(λ × T/252) × d × eth_weight² × (v' Σ v) × E[(R - τ)²₊]] × √(252/T)
```

Combining under a single square root:

```
TE_annual = √[(λ × T/252) × d × eth_weight² × (v' Σ v) × E[(R - τ)²₊] × (252/T)]
         = √[λ × d × eth_weight² × (v' Σ v) × E[(R - τ)²₊] × (T/252) × (252/T)]
         = √[λ × d × eth_weight² × (v' Σ v) × E[(R - τ)²₊] × 1]
         = √[λ × d × eth_weight² × (v' Σ v) × E[(R - τ)²₊]]
```

**QED**: The formula is identical to the direct annual calculation.

## Why This Works

The invariance arises from the perfect cancellation of time-scaling factors:

1. **Redemption scaling**: When moving from annual to T-day period, redemptions scale by T/252
2. **Volatility scaling**: When annualizing T-day volatility, we multiply by √(252/T)
3. **Perfect cancellation**: (T/252) × (252/T) = 1

This is a consequence of:
- Redemptions following a linear time scaling (Poisson process property)
- Volatility following square-root-of-time scaling (Brownian motion property)
- The formula correctly capturing both effects

## Practical Implications for ETF Management

### 1. Simplified Risk Measurement

ETF managers can:
- Use the same formula regardless of measurement window
- No need for complex time-adjustment calculations
- Direct comparison between different time horizons

### 2. Rolling Window Analysis

For 21-day rolling windows:
```python
# Same formula works for any window
annual_te = sqrt(lambda_annual * d * eth_weight**2 * v_sigma_v * expected_squared_excess)
```

No adjustment needed when:
- Reporting daily, weekly, or monthly TE figures
- Comparing different time periods
- Backtesting over various horizons

### 3. Regulatory Compliance

Many regulations require:
- 21-day rolling window calculations
- Annualized reporting
- Historical consistency

The formula's invariance ensures compliance without computational overhead.

## Examples with Different Time Windows

### Example 1: Direct Annual Calculation

Parameters:
- λ = 18 redemptions/year
- d = 10 days/episode
- base_k = 0.000011
- staking_pct = 0.80
- E[(R - 0.2)²₊] = 0.00056

Annual TE = √[18 × 10 × 0.000011 × 0.00056] = 0.105%

### Example 2: 21-Day Window + Annualization

Same parameters:
- λ₂₁ = 18 × (21/252) = 1.5 redemptions
- 21-day TE = √[1.5 × 10 × 0.000011 × 0.00056] = 0.0303%
- Annualized = 0.0303% × √(252/21) = 0.0303% × 3.464 = 0.105%

### Example 3: Monthly (21-Day) Reporting

Monthly redemptions = 18 × (21/252) = 1.5
Monthly TE = Annual TE / √(252/21) = 0.105% / 3.464 = 0.0303%

**Result**: All approaches yield consistent results.

## Special Cases and Boundary Conditions

### 1. Daily Tracking Error

For daily TE (T = 1):
- Daily redemptions: λ₁ = λ/252
- Annualization factor: √252
- Formula still holds

### 2. Intraday Periods

For sub-daily periods, the formula extends naturally:
- Use appropriate time fraction
- Scale λ proportionally
- Annualization preserves the form

### 3. Multi-Year Horizons

For T > 252 days:
- λ_T = λ × (T/252)
- De-annualization factor: √(T/252)
- Formula remains valid

## Implementation Considerations

### 1. Parameter Consistency

Ensure λ is always expressed as **annual** frequency:
```python
# Correct: λ is annual
annual_te = analytical_te(lambda_annual, episode_days, base_k, staking_pct, dist)

# For different windows, λ adjusts automatically
# No manual scaling needed
```

### 2. Numerical Precision

The invariance holds exactly in theory and to machine precision in practice:
```python
# Test invariance
te_direct = analytical_te(18, 10, base_k, staking_pct, dist)
te_21day = analytical_te(18 * 21/252, 10, base_k, staking_pct, dist) * sqrt(252/21)
assert abs(te_direct - te_21day) < 1e-15
```

### 3. Reporting Flexibility

The formula enables flexible reporting:
```python
def te_for_window(window_days: int, annual_lambda: float, **params) -> dict:
    """Calculate TE for any time window"""
    annual_te = analytical_te(annual_lambda, **params)
    window_te = annual_te / sqrt(252 / window_days)
    
    return {
        'window_te': window_te,
        'annualized_te': annual_te,
        'window_days': window_days
    }
```

## Comparison with Monte Carlo Simulation

The time window invariance provides a significant advantage over simulation-based approaches:

### Traditional Monte Carlo
- Must simulate each time window separately
- Annualization introduces additional sampling error
- Computational cost scales with precision requirements

### Analytical Formula
- Single calculation for any time window
- Exact results (no sampling error)
- Constant computational cost

## Mathematical Intuition

The invariance reflects a deep connection between:

1. **Poisson Process Scaling**: E[N(t)] = λt
2. **Brownian Motion Scaling**: Var[W(t)] = σ²t
3. **Square-Root Rule**: SD[W(t)] = σ√t

Our formula correctly captures these relationships:
- Redemption count scales linearly with time
- Variance accumulates linearly with redemption count
- Standard deviation (TE) follows square-root scaling

## Conclusion

The time window invariance of our analytical tracking error formula is not merely a mathematical curiosity—it provides substantial practical benefits:

1. **Simplicity**: One formula for all time horizons
2. **Accuracy**: No approximation errors from time adjustments
3. **Efficiency**: No computational overhead for different windows
4. **Consistency**: Seamless comparison across time periods

For ETF managers calculating tracking error over 21-day rolling windows, this property means:
- Use the annual formula directly with λ as annual redemption rate
- The result automatically represents annualized tracking error
- No manual adjustments or scaling factors needed

This elegant property emerges naturally from the mathematical structure of the problem and validates the robustness of our analytical approach.