# Comprehensive List of Parameters, Assumptions, and Variables for Two-Asset Tracking Error Formula Model (ETH and SOL)

## I. Market Structure Parameters

### 1. Asset Weights (Benchmark)
- `eth_weight` = 0.1049 (10.49%)
- `sol_weight` = 0.0387 (3.87%)
- `btc_weight` = 0.7869 (78.69%)
- `xrp_weight` = 0.0549 (5.49%)
- `ada_weight` = 0.0119 (1.19%)
- `xlm_weight` = 0.0027 (0.27%)

### 2. Daily Volatilities
- `σ_BTC` = 3.9%
- `σ_ETH` = 4.8%
- `σ_SOL` = 7.1%
- `σ_XRP` = 5.3%
- `σ_ADA` = 5.5%
- `σ_XLM` = 5.1%

### 3. Correlation Matrix
- `ρ(BTC,ETH)` = 0.70
- `ρ(within_excluded)` = 0.60 (between XRP, ADA, XLM)
- `ρ(cross)` = 0.60 (all other pairs)

## II. Staking Parameters

### 1. Staking Percentages
- `eth_staking_pct`: Fraction of ETH staked (e.g., 0.80 or 0.90)
- `sol_staking_pct`: Fraction of SOL staked (e.g., 0.70 or 0.90)

### 2. Unbonding Periods
- `eth_unbonding_days` = 10 days
- `sol_unbonding_days` = 2 days

### 3. Thresholds
- `τ_ETH` = 1 - eth_staking_pct
- `τ_SOL` = 1 - sol_staking_pct

## III. Redemption Distribution Parameters

### 1. Mixture Distribution Components

#### A. Retail Redemptions (Two-Point)
- `r_retail_1` = 0.02 (2% of NAV)
- `r_retail_2` = 0.00 (0% of NAV)
- `p_retail` = 0.50 (probability of 2% redemption)
- Weight in mixture: `w_retail`

#### B. Institutional Redemptions (Discrete)
- `r_inst_1` = 0.05 (5% of NAV), `p_inst_1` = 0.67
- `r_inst_2` = 0.10 (10% of NAV), `p_inst_2` = 0.17
- `r_inst_3` = 0.20 (20% of NAV), `p_inst_3` = 0.11
- `r_inst_4` = 0.30 (30% of NAV), `p_inst_4` = 0.06
- Weight in mixture: `w_inst` = 1 - `w_retail`

### 2. Redemption Frequency
- `λ` = Expected number of redemptions per year (e.g., 18)
- `λ_retail` = λ × w_retail
- `λ_inst` = λ × w_inst

## IV. Variance Components (k-factors)

### 1. Single-Asset k-components
- `k_ETH_ETH` = eth_weight² × (v_ETH' Σ v_ETH)
- `k_SOL_SOL` = sol_weight² × (v_SOL' Σ v_SOL)

### 2. Cross-Asset k-component
- `k_ETH_SOL` = eth_weight × sol_weight × (v_ETH' Σ v_SOL)

### 3. Base k-values (for reference)
- `base_k_ETH` ≈ 0.000011
- Note: k_ETH_SOL > 0 (correlation cost)

## V. Core Variables

### 1. Tracking Error
- `TE`: Annual tracking error (percentage)

### 2. Time Segmentation
- `d_short` = min(eth_unbonding_days, sol_unbonding_days) = 2
- `d_long` = max(eth_unbonding_days, sol_unbonding_days) = 10

### 3. Redemption Variables
- `R`: Random redemption size (0 to 1)
- `r`: Realized redemption value

### 4. Overweight Variables
- `δ_ETH` = eth_weight × max(0, r - τ_ETH)
- `δ_SOL` = sol_weight × max(0, r - τ_SOL)

## VI. Variance Functions

### 1. Full Period Variance (Days 1-2)
```
Var_full(r) = k_ETH_ETH × (r - τ_ETH)²₊ + 
              2 × k_ETH_SOL × (r - τ_ETH)₊ × (r - τ_SOL)₊ + 
              k_SOL_SOL × (r - τ_SOL)²₊
```

### 2. Partial Period Variance (Days 3-10)
```
Var_partial(r) = k_ETH_ETH × (r - τ_ETH)²₊
```

## VII. Expected Values for Mixture Distribution

### 1. Key Expectations
- `E[(R - τ_ETH)²₊]`: Expected squared excess for ETH
- `E[(R - τ_SOL)²₊]`: Expected squared excess for SOL
- `E[(R - τ_ETH)₊ × (R - τ_SOL)₊]`: Expected cross-product

### 2. Mixture Calculations
```
E[f(R)] = w_retail × E_retail[f(R)] + w_inst × E_inst[f(R)]
```

## VIII. Model Assumptions

### 1. Market Assumptions
- Constant correlations and volatilities
- No transaction costs or market impact
- Linear redemption process (NAV-proportional)

### 2. Stochastic Process Assumptions
- Compound Poisson process for redemptions
- Independence between redemption events
- Stationarity (time-homogeneous)

### 3. Threshold Effect Assumptions
- Variance is zero when r ≤ τ
- Quadratic growth above threshold
- Non-constant k-factor

### 4. Mixture Distribution Assumptions
- Retail and institutional redemptions are distinct processes
- Can be modeled as weighted mixture
- Each component follows its own distribution

## IX. Optimization Variables

### 1. Lagrange Multiplier Framework
- `v_ETH`: Optimal hedge vector for ETH constraint
- `v_SOL`: Optimal hedge vector for SOL constraint
- `a*`: Optimal active weights = δ_ETH × v_ETH + δ_SOL × v_SOL

### 2. Constraint Conditions
- Sum-to-zero: Σa* = 0
- ETH-specific: a*[ETH] = δ_ETH
- SOL-specific: a*[SOL] = δ_SOL

## X. Final Tracking Error Formula

```
TE = √[λ × (d_short × E[Var_full] + (d_long - d_short) × E[Var_partial])]
```

Where the expectations are computed over the mixture distribution:
```
E[Var] = w_retail × E_retail[Var] + w_inst × E_inst[Var]
```