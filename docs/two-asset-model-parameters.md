# Two-Asset Tracking Error Model Parameters for ETH and SOL

This document lists all lowest-level parameters, assumptions, and variables used in the Two-Asset Tracking Error Formula model for ETH and SOL staking.

## Benchmark Weights

- **btc_weight**: 0.7869 (78.69%)
- **eth_weight**: 0.1049 (10.49%)
- **xrp_weight**: 0.0549 (5.49%)
- **sol_weight**: 0.0387 (3.87%)
- **ada_weight**: 0.0119 (1.19%)
- **xlm_weight**: 0.0027 (0.27%)

### Portfolio Constraints
- **sum_to_zero_constraint**: True (active weights must sum to zero)
- **fully_invested**: True (portfolio remains fully invested)

## Staking Parameters

### Staking Percentages
- **eth_staking_pct**: Percentage of ETH that is staked (e.g., 0.90 for 90%)
- **sol_staking_pct**: Percentage of SOL that is staked (e.g., 0.90 for 90%)

### Unbonding Periods
- **eth_unbonding_days**: 10 days
- **sol_unbonding_days**: 2 days

### Staking Yields
- **annual_staking_yield**: Annualized staking yield (e.g., 0.04 for 4% or 0.05 for 5%)
- **baseline_staking_percentage**: Reference staking level for benefit calculations (e.g., 0.70 for 70%)

## Market Structure Parameters

### Daily Volatilities
- **σ_BTC**: 0.039 (3.9%)
- **σ_ETH**: 0.048 (4.8%)
- **σ_XRP**: 0.053 (5.3%)
- **σ_SOL**: 0.071 (7.1%)
- **σ_ADA**: 0.055 (5.5%)
- **σ_XLM**: 0.051 (5.1%)

### Correlation Coefficients
- **ρ(BTC,ETH)**: 0.70 (correlation between BTC and ETH)
- **ρ(BTC,[XRP,SOL,ADA,XLM])**: 0.60 (correlations between BTC and XRP, SOL, ADA, XLM)
- **ρ(ETH,[XRP,SOL,ADA,XLM])**: 0.60 (correlations between ETH and XRP, SOL, ADA, XLM)
- **ρ(XRP,SOL,ADA,XLM)**: 0.60 (correlations between XRP, SOL, ADA, XLM)

### Trading Days
- **trading_days_per_year**: 252

### Market Assumptions
- **correlation_stability**: True (correlations remain constant over time)
- **market_impact**: False (transaction costs not considered)

## Redemption Model Parameters

### Expected Number of Institutional Redemptions
- **λ (Expected number of institutional redemptions per year)**: 18

### Institutional Redemptions Expectancy
Discrete probability distribution of redemption sizes:
- **P(R = 0.05)**: 0.667 (12/18)
- **P(R = 0.10)**: 0.167 (3/18)
- **P(R = 0.20)**: 0.111 (2/18)
- **P(R = 0.30)**: 0.056 (1/18)

### Redemption Process Assumptions
- **process_type**: "Compound Poisson"
- **redemption_independence**: True (redemptions are assumed independent)
- **time_homogeneous**: True (redemption process is stationary)
- **threshold_effects**: True (variance only occurs above redemption threshold)
- **variance_function**: Quadratic above threshold