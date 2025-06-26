# Staking Percentage x Tracking Difference Risk

## Executive Summary

This document explains the mathematical approach used in the ETH overweight optimization framework for tracking the Nasdaq Crypto US (NCI-US) index. The NCI-US was chosen instead of the full NCI to simplify the analysis by including fewer assets while still capturing the essential dynamics of crypto index tracking. The framework addresses a specific portfolio management challenge: how to maintain benchmark-like exposure when a significant portion of ETH holdings are staked (illiquid) and the fund faces redemptions.

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

This means the staking strategy can have a Total Net Benefit as low as -4 bps while keeping the fund's overall tracking difference within the 1.5% commitment. When the Total Net Benefit is positive, it represents expected profit; when negative, it represents tracking costs that must be covered.

#### Redemption-Driven Constraints
When redemptions occur and ETH is staked:
1. Cannot sell staked ETH proportionally 
2. Must sell other assets disproportionately
3. This creates underweights in liquid assets
4. To rebalance back to benchmark weights, must overweight ETH

## Mathematical Framework

### 1. Delta ETH Calculation

The core relationship determines how much to overweight ETH based on redemptions and staking percentage:

```
δ_ETH = max(0, redemption_pct × w_ETH - w_ETH × (1 - staking_pct))
```

Where:
- `δ_ETH`: Required ETH overweight
- `redemption_pct`: Redemption as percentage of NAV
- `w_ETH`: ETH benchmark weight (10.49%)
- `staking_pct`: Fraction of ETH that is staked

**Intuition**: The overweight equals the gap between ETH's proportional share of redemptions and available unstaked ETH.

### 2. Covariance Matrix Construction

The 6×6 covariance matrix captures asset relationships:

```
Σ_ij = ρ_ij × σ_i × σ_j
```

With correlation structure:
- `ρ(BTC,ETH) = 0.70`: High correlation between major cryptos
- `ρ(within_other) = 0.60`: Moderate correlation among XRP, SOL, ADA, XLM
- `ρ(cross) = 0.60`: Cross-correlations between groups

Asset volatilities:

| Asset | Daily Volatility | Annual Volatility |
|-------|------------------|-------------------|
| BTC   | 3.9%            | 61.9%            |
| ETH   | 4.8%            | 76.2%            |
| XRP   | 5.3%            | 84.1%            |
| SOL   | 7.1%            | 112.7%           |
| ADA   | 5.5%            | 87.3%            |
| XLM   | 5.1%            | 81.0%            |

*Annual volatilities calculated using √252 trading days*

### 3. Optimal Active Weight Optimization

Given a required ETH overweight, find risk-minimizing active weights using Lagrange multipliers:

**Optimization Problem**:
```
minimize: 0.5 × a' × Σ × a
subject to:
    Σ(a_i) = 0         (sum-to-zero constraint)
    a_ETH = δ_ETH      (ETH overweight constraint)
```

**Solution via Lagrange**:
```
a* = Σ^(-1) × C' × λ*
where: λ* = (C × Σ^(-1) × C')^(-1) × c
```

Where:
- `C`: Constraint matrix (2×6)
- `c`: Constraint values [0, δ_ETH]'

### 4. Tracking Error Calculation

#### Episode Tracking Error
For each redemption episode:
```
TE_episode = √(variance × days)
where: variance = a' × Σ × a
```

#### Annual Tracking Error
Aggregating multiple episodes:
```
TE_annual = √(Σ(variance_i × days_i))
```

### 5. Expected Negative Tracking

Using half-normal distribution properties:
```
E[negative_tracking] = -TE × √(2/π) × 0.5
```

This represents the expected underperformance when tracking error works against the fund.

### 6. Net Cost-Benefit Analysis

The framework separates two distinct sources of staking benefits:

#### Benefits
1. **Overweight Benefits**: Staking yield earned on the ETH overweight during redemption episodes
   - Formula: `δ_ETH × yield × time_fraction`
   - Only applies when ETH is actually overweighted due to redemptions

2. **Extra Staking Benefits**: Additional yield from staking above the 70% baseline
   - Formula: `w_ETH × (staking_pct - 0.70) × yield`
   - Applies continuously based on the staking percentage
   - Calculated as a property of `StakingConfig` for better encapsulation

#### Costs
- **Expected Shortfall**: The expected negative tracking from portfolio deviation
  - Formula: `-TE × √(2/π) × 0.5`

#### Net Result Calculation
```
Net (Overweight) = Overweight Benefits + Expected Shortfall
Total Net Benefit = Net (Overweight) + Extra Staking Benefits
```

This separation clarifies that:
- **Net (Overweight)** measures the cost-benefit of the overweight strategy itself
- **Total Net Benefit** includes all sources of value from the staking approach

## Implementation Details

### Configuration-Driven Design

The framework uses a configuration-driven approach with clear separation of concerns:

1. **`MarketConfig`**: Encapsulates market parameters (weights, volatilities, correlations)
2. **`StakingConfig`**: Manages staking strategy parameters and benefit calculations
   - Contains `eth_staking_pct`, `annual_yield`, `eth_weight`, and `baseline_staking`
   - Provides `extra_staking_benefit` as a computed property
   - Ensures all staking-related logic is centralized

### Episode-Based Analysis

The framework uses an episodic approach where:
1. Each redemption creates an "episode" with specific duration
2. Episodes can have different redemption amounts and durations
3. Total risk is the aggregation of episode risks

### Redemption Schedule

The analysis uses a realistic redemption schedule that models varying redemption patterns:

```python
redemption_schedule = [
    (0.05, 12, 10),  # 5% redemption, 12 episodes, 10 days each
    (0.10, 3, 10),   # 10% redemption, 3 episodes, 10 days each
    (0.20, 2, 10),   # 20% redemption, 2 episodes, 10 days each
    (0.30, 1, 10),   # 30% redemption, 1 episode, 10 days
]
```

**Purpose and Design**:
- **Frequency vs Size Trade-off**: Smaller redemptions (5%) occur more frequently (12 episodes) reflecting normal fund flows
- **Large Event Modeling**: Larger redemptions (20-30%) are modeled as single or few episodes, representing institutional exits or market stress events
- **Risk Aggregation**: Each episode contributes to total tracking error based on its duration and active weights
- **Realistic Timeline**: The schedule spans 250 trading days, capturing annual risk metrics

**Why Episodes Matter**:
1. **Path Dependency**: Earlier redemptions affect available liquidity for later ones
2. **Time-Weighted Risk**: Longer episodes contribute more to annual tracking error
3. **Staking Benefit Accrual**: Benefits accumulate based on episode duration and overweight size
4. **Compound Effects**: Multiple small redemptions can create larger cumulative tracking errors than single large redemptions

### Risk Minimization Algorithm

The active weight optimization ensures:
1. Minimum tracking error variance given constraints
2. BTC typically takes the largest underweight (highest correlation with ETH)
3. Other assets adjust to minimize overall portfolio variance

### Code Architecture

The implementation follows clean code principles with modular components:

```python
# Configuration encapsulation
staking_config = StakingConfig(
    eth_staking_pct=0.90,     # 90% of ETH is staked
    annual_yield=0.05,        # 5% staking yield
    eth_weight=0.1049,        # ETH's benchmark weight
    baseline_staking=0.70     # 70% baseline for extra benefits
)

# The extra staking benefit is calculated as a property
extra_benefit = staking_config.extra_staking_benefit  # Returns 0.1049%
```

This design ensures:
- **Single Responsibility**: Each class handles one aspect (market params, staking params, analysis)
- **Encapsulation**: Staking-related calculations are contained within `StakingConfig`
- **Testability**: Components can be tested independently
- **Clarity**: Clear separation between episodic benefits and baseline benefits

## Key Findings from Analysis

### 1. Staking Percentage Impact
- **0-70% staked**: No overweight needed for typical redemptions
- **80% staked**: Small overweights begin, tracking error ~0.10%
- **90% staked**: Moderate overweights, tracking error ~0.25%
- **100% staked**: Any redemption requires overweight, tracking error ~0.49%

### 2. Active Weight Patterns
For a 5% δ_ETH overweight:
- BTC: -2.66% (bears most of the offset)
- ETH: +5.00% (the required overweight)
- Others: -0.55% to -0.69% (proportional adjustments)

### 3. Break-Even Analysis
With 5% staking yield and 70% baseline:
- **80% staking**: Total net benefit +0.0128% (+1.28 bps)
  - Net (Overweight): -0.0397%
  - Extra Staking Benefits: +0.0524%
- **90% staking**: Total net benefit +0.0100% (+1.00 bps)
  - Net (Overweight): -0.0949%
  - Extra Staking Benefits: +0.1049%
- **100% staking**: Total net benefit -0.0168% (-1.68 bps)
  - Net (Overweight): -0.1741%
  - Extra Staking Benefits: +0.1573%

The strategy remains profitable up to ~95% staking. While the overweight strategy itself generates negative returns at higher staking levels, the extra yield from staking above the 70% baseline compensates for these costs up to the break-even point.

### 4. Portfolio Yield Impact
Due to ETH's 10.49% benchmark weight:
- Maximum portfolio yield gain: 0.52% (at 100% staking, 5% yield)
- This modest impact reflects ETH's relatively small index weight

## Practical Implications

### Manager Compensation Structure

The manager receives staking revenue after covering any costs needed to keep the fund's total tracking difference within 1.5%:

- When Total Net Benefit is **positive** (e.g., +1.28 bps at 80% staking): The strategy generates expected profit for the fund, and no subsidy is needed
- When Total Net Benefit is **negative** (e.g., -1.68 bps at 100% staking): Tracking costs must be covered from staking revenue before manager compensation
- The 4 basis point remaining budget means the strategy can tolerate up to -4 bps in Total Net Benefit while maintaining compliance

### Strategic Recommendations

1. **Optimal Staking Range**: 80-90% provides positive net benefits while maintaining manageable tracking error

2. **Redemption Management**: The framework quantifies the cost of illiquidity, enabling informed staking decisions

3. **Risk Budget**: Annual tracking error of 0.10-0.25% (at 80-90% staking) is reasonable for capturing staking yields

4. **Scalability**: The approach scales with redemption size - larger redemptions require proportionally larger overweights

## Limitations and Assumptions

1. **Correlation Stability**: Assumes constant correlations, which may vary in stressed markets
2. **Linear Redemptions**: Assumes NAV-proportional redemptions
3. **No Market Impact**: Doesn't account for transaction costs or market impact
4. **Single Period**: Each episode is independent; doesn't model path dependency

## Conclusion

The framework provides a rigorous mathematical approach to managing the ETH staking/liquidity trade-off. By explicitly modeling the relationship between staking percentage, redemptions, and tracking error, it enables data-driven decisions about optimal staking levels. 

Key insights from the analysis:
1. **Dual Benefit Structure**: The framework separates episodic overweight benefits from continuous baseline staking benefits, providing clarity on value sources
2. **Optimal Range**: 80-90% staking strikes an optimal balance between yield capture and risk management for typical redemption scenarios
3. **Break-Even Understanding**: While the overweight strategy itself may generate negative returns at high staking levels, the extra yield from staking above baseline can compensate, extending viability to ~95% staking
4. **Risk Budget**: The modest tracking errors (0.10-0.25%) at optimal staking levels are reasonable given the total yield benefits

The analysis demonstrates that a well-calibrated staking strategy can enhance portfolio returns while maintaining acceptable tracking error levels, even in the presence of redemption-driven liquidity constraints.

## Appendix: Sensitivity Analysis Results

### Table 1: ETH Overweight (delta_eth) Sensitivity Analysis

This table shows how the required ETH overweight varies with redemption levels and staking percentages:

| ETH Staking | 5% | 10% | 15% | 20% | 25% | 30% | 35% | 40% | 45% |
|-------------|-----|-----|-----|-----|-----|-----|-----|-----|-----|
| 70% staked | 0.000% | 0.000% | 0.000% | 0.000% | 0.000% | 0.000% | 0.524% | 1.049% | 1.573% |
| 80% staked | 0.000% | 0.000% | 0.000% | 0.000% | 0.524% | 1.049% | 1.573% | 2.098% | 2.622% |
| 90% staked | 0.000% | 0.000% | 0.524% | 1.049% | 1.573% | 2.098% | 2.622% | 3.147% | 3.671% |
| 100% staked | 0.524% | 1.049% | 1.573% | 2.098% | 2.622% | 3.147% | 3.671% | 4.196% | 4.720% |

**Key Insight**: The diagonal pattern shows that as staking increases, smaller redemptions trigger the need for ETH overweights. At 100% staking, any redemption requires an overweight.

### Table 2: Key Metrics Sensitivity to ETH Staking Percentage

Using the redemption schedule defined above, this table shows the comprehensive risk-return trade-offs:

| % ETH Staked | Total Annual TE | Overweight Benefits | Extra Staking Benefits | Expected Shortfall | Net (Overweight) | Total Net Benefit |
|--------------|-----------------|---------------------|------------------------|-------------------|------------------|-------------------|
| 70% | 0.00% | 0.0000% | 0.0000% | -0.0000% | +0.0000% | +0.0000% |
| 80% | 0.10% | 0.0014% | 0.0524% | -0.0411% | -0.0397% | +0.0128% |
| 90% | 0.25% | 0.0057% | 0.1049% | -0.1007% | -0.0949% | +0.0100% |
| 100% | 0.49% | 0.0230% | 0.1573% | -0.1971% | -0.1741% | -0.0168% |

**Notes**:
- **Overweight Benefits**: Staking yield earned on ETH overweights during redemption episodes
- **Extra Staking Benefits**: Additional yield from staking above the 70% baseline (calculated as `StakingConfig.extra_staking_benefit`)
- **Net (Overweight)**: Direct cost-benefit of the overweight strategy (overweight benefits + expected shortfall)
- **Total Net Benefit**: Comprehensive measure including all sources of value
- **Tracking Budget**: With operational costs at ~1.46% of the 1.5% limit, the strategy can tolerate Total Net Benefit as low as -4 bps
- **Break-even**: Occurs around 95% staking where total costs equal total benefits

### Table 3: Expected Portfolio Annual Yield from ETH Staking

This table shows the portfolio-level yield impact given ETH's 10.49% benchmark weight:

| % ETH Staked | 3% Yield | 5% Yield | 8% Yield |
|--------------|----------|----------|----------|
| 70% | 0.220% | 0.367% | 0.587% |
| 80% | 0.252% | 0.420% | 0.671% |
| 90% | 0.283% | 0.472% | 0.755% |
| 100% | 0.315% | 0.524% | 0.839% |

**Formula**: Portfolio yield = ETH weight (10.49%) × % ETH staked × Staking yield

**Key Insights**:
1. Portfolio yields are modest due to ETH's relatively small index weight
2. At 90% staking with 5% yield, the portfolio earns 0.472% annually
3. These yields must be weighed against the tracking error costs shown in Table 2
4. The maximum achievable portfolio yield (100% staking, 8% yield) is 0.839%