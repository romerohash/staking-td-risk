# Staking Percentage x Tracking Difference Risk

## Executive Summary

This document presents a mathematical framework for optimizing ETH staking strategies while tracking the Nasdaq Crypto US (NCI-US) index. The central challenge is balancing the yield benefits of staking against the tracking error costs that arise when staked (illiquid) ETH cannot be sold during fund redemptions.

The analysis reveals that staking $80\%-90\%$ of ETH holdings provides optimal risk-adjusted returns, generating positive net benefits while maintaining acceptable tracking error levels. The framework quantifies these trade-offs precisely, enabling data-driven staking decisions.

## Problem Statement

### The Core Challenge

When an index fund stakes ETH to generate yield, it creates a liquidity mismatch. During redemptions, the fund must sell assets proportionally to maintain index weights. However, staked ETH cannot be sold immediately, forcing the fund to:

1. Sell other liquid assets disproportionately
2. Create temporary underweights in these assets
3. Overweight ETH to compensate and minimize tracking error

This dynamic creates a fundamental trade-off between staking yield and tracking accuracy.

### Index Composition

The Nasdaq Crypto US (NCI-US) index consists of six cryptocurrency assets:

| Asset | Weight | Role in Portfolio |
|-------|--------|-------------------|
| BTC | $78.69\%$ | Dominant position, primary liquidity source |
| ETH | $10.49\%$ | Secondary position, staking opportunity |
| XRP | $5.49\%$ | Alternative liquidity |
| SOL | $3.87\%$ | Alternative liquidity, staking opportunity |
| ADA | $1.19\%$ | Minor position, staking opportunity |
| XLM | $0.27\%$ | Minor position |

### Operating Constraints

#### Tracking Difference Budget

The fund operates under strict performance limits:

$$\text{Maximum Annual Tracking Difference} = 1.5\% \text{ (150 basis points)}$$

Current cost structure:
- Operational costs: $\sim 1.46\%$ (146 basis points)
- **Remaining budget: 4 basis points $(0.04\%)$**

This tight constraint means the staking strategy must generate sufficient benefits to offset any tracking costs while staying within the 4 basis point buffer.

#### Redemption Dynamics

Fund redemptions trigger a cascade of portfolio adjustments:

1. **Liquidity Constraint**: Cannot sell staked ETH proportionally
2. **Rebalancing Need**: Must maintain benchmark weights post-redemption
3. **Overweight Solution**: Temporarily overweight ETH to minimize tracking error
4. **Risk Impact**: Deviation from benchmark creates tracking error

## Mathematical Framework

### 1. ETH Overweight Calculation

The required ETH overweight depends on redemption size and staking percentage:

$$\delta_{ETH} = \max(0, r \times w_{ETH} - w_{ETH} \times (1 - s))$$

Where:
- $\delta_{ETH}$ = Required ETH overweight (as % of portfolio)
- $r$ = Redemption percentage of NAV
- $w_{ETH}$ = ETH benchmark weight $(10.49\%)$
- $s$ = Fraction of ETH that is staked

**Intuition**: This formula calculates the gap between ETH's proportional share of the redemption and the amount of unstaked ETH available to sell.

**Example**: With $90\%$ staking and $10\%$ redemption:

$$\delta_{ETH} = \max(0, 0.10 \times 0.1049 - 0.1049 \times (1 - 0.90)) = 0.0005 = 0.05\%$$

### 2. Risk Modeling: Covariance Matrix

Asset return correlations and volatilities determine portfolio risk:

$$\Sigma_{ij} = \rho_{ij} \times \sigma_i \times \sigma_j$$

#### Correlation Structure

The model uses empirically-grounded correlations:
- $\rho(BTC, ETH) = 0.70$ (high correlation between major cryptocurrencies)
- $\rho(\text{within others}) = 0.60$ (moderate correlation among altcoins)
- $\rho(\text{cross group}) = 0.60$ (cross-correlations between groups)

#### Volatility Parameters

| Asset | Daily Volatility | Annual Volatility |
|-------|-----------------|-------------------|
| BTC   | $3.9\%$         | $61.9\%$          |
| ETH   | $4.8\%$         | $76.2\%$          |
| XRP   | $5.3\%$         | $84.1\%$          |
| SOL   | $7.1\%$         | $112.7\%$         |
| ADA   | $5.5\%$         | $87.3\%$          |
| XLM   | $5.1\%$         | $81.0\%$          |

Annual volatilities use the standard conversion: $\sigma_{annual} = \sigma_{daily} \times \sqrt{252}$

### 3. Portfolio Optimization

Given a required ETH overweight, we find the risk-minimizing portfolio using Lagrange multipliers:

**Optimization Problem:**

$$\min_{a} \frac{1}{2} a^T \Sigma a$$

Subject to:
- $\sum_{i} a_i = 0$ (active weights sum to zero)
- $a_{ETH} = \delta_{ETH}$ (ETH overweight constraint)

**Solution:**

$$a^* = \Sigma^{-1} C^T \lambda^*$$

Where $\lambda^* = (C \Sigma^{-1} C^T)^{-1} c$

The constraint matrix $C$ and vector $c$ encode our requirements:
- $C$ = $2 \times 6$ matrix of constraint coefficients
- $c$ = $[0, \delta_{ETH}]^T$ constraint values

### 4. Tracking Error Quantification

#### Episode-Level Tracking Error

Each redemption episode generates tracking error based on its duration and active weights:

$$TE_{episode} = \sqrt{a^T \Sigma a \times \frac{days}{252}}$$

#### Annual Tracking Error

Multiple episodes aggregate to annual tracking error:

$$TE_{annual} = \sqrt{\sum_i \left(a_i^T \Sigma a_i \times \frac{days_i}{252}\right)}$$

Note: In implementation, this is often calculated as:

$$TE_{annual} = \frac{1}{\sqrt{252}} \times \sqrt{\sum_i (variance_i \times days_i)}$$

This formulation aggregates variance-days across episodes and converts to annual terms.

### 5. Expected Performance Impact

Tracking error creates both positive and negative deviations from the benchmark. The expected negative impact follows from half-normal distribution properties:

$$E[\text{Negative Tracking}] = -TE_{annual} \times \sqrt{\frac{2}{\pi}} \times 0.5$$

Where:
- $TE_{annual}$ is the annualized tracking error from aggregated episodes
- $\sqrt{2/\pi} \approx 0.798$ is the mean of a half-normal distribution
- $0.5$ represents the probability of underperformance

This represents the expected underperformance when tracking error works against the fund.

### 6. Comprehensive Cost-Benefit Analysis

The framework evaluates two distinct benefit sources against tracking costs:

#### Benefit Sources

**1. Overweight Benefits** (episodic):

$$\text{Benefit}_{overweight} = \sum_i \left(\delta_{ETH,i} \times \text{yield} \times \frac{\text{days}_i}{365}\right)$$

These benefits accumulate across all redemption episodes where ETH is overweighted. Each episode contributes based on its overweight size and duration.

**2. Extra Staking Benefits** (continuous):

$$\text{Benefit}_{extra} = w_{ETH} \times \max(0, s - 0.70) \times \text{yield}$$

These benefits accrue continuously throughout the year from staking above the $70\%$ baseline level.

#### Cost Component

**Expected Shortfall** (from aggregate tracking error):

$$\text{Cost} = -TE_{\text{annual}} \times \sqrt{\frac{2}{\pi}} \times 0.5$$

This represents the expected underperformance from the total portfolio tracking error across all episodes.

#### Net Results Calculation

$$\text{Net (Overweight)} = \text{Benefit}_{overweight} + \text{Cost}$$

This measures the direct cost-benefit of the overweight strategy itself.

$$\text{Total Net Benefit} = \text{Net (Overweight)} + \text{Benefit}_{extra}$$

This comprehensive measure includes all sources of value from the staking approach.

## Implementation Framework

### Redemption Schedule Modeling

The analysis uses a realistic redemption schedule that captures different market scenarios:

| Redemption Size | Frequency | Episode Duration | Scenario |
|----------------|-----------|------------------|----------|
| $5\%$ | 12 episodes | 10 days each | Normal fund flows |
| $10\%$ | 3 episodes | 10 days each | Moderate outflows |
| $20\%$ | 2 episodes | 10 days each | Stress events |
| $30\%$ | 1 episode | 10 days | Extreme redemption |

This schedule models 250 trading days with varying redemption patterns, from frequent small redemptions to rare large events.

### Implementation Notes

#### Variance Aggregation
When implementing the tracking error calculation:
1. Calculate daily variance for each episode: $variance_i = a_i^T \Sigma a_i$
2. Weight by episode duration: $variance_i \times days_i$
3. Sum across all episodes: $total\_variance\_days = \sum(variance_i \times days_i)$
4. Convert to annual tracking error: $TE_{annual} = \sqrt{total\_variance\_days / 252}$

#### Time Conventions
- **Trading days (252)**: Used for volatility and tracking error calculations
- **Calendar days (365)**: Used for yield accrual calculations
- This distinction reflects that market risk occurs only on trading days, while staking yields accrue continuously

### Portfolio Rebalancing Mechanics

When a redemption occurs with staked ETH:

1. **Initial State**: Portfolio at benchmark weights
2. **Redemption Impact**: Sell liquid assets disproportionately
3. **Resulting Imbalance**: Underweight in liquid assets, overweight in ETH
4. **Optimization**: Calculate minimum-risk active weights
5. **Rebalancing**: Trade to new optimal weights

### Risk Minimization Properties

The optimization typically produces:
- **BTC**: Bears the largest underweight (highest correlation with ETH)
- **Other Assets**: Proportional underweights based on correlation structure
- **ETH**: Maintains required overweight

Example active weights for $5\%$ ETH overweight:
- BTC: $-2.66\%$
- ETH: $+5.00\%$
- XRP: $-0.69\%$
- SOL: $-0.66\%$
- ADA: $-0.59\%$
- XLM: $-0.55\%$

## Key Findings and Analysis

### 1. Staking Percentage Impact on Risk

The relationship between staking percentage and tracking error is non-linear:

| ETH Staked | Annual Tracking Error | Risk Characterization |
|------------|----------------------|----------------------|
| $70\%$ | $0.00\%$ | No overweight needed |
| $80\%$ | $0.10\%$ | Minimal risk |
| $90\%$ | $0.25\%$ | Moderate risk |
| $100\%$ | $0.49\%$ | Significant risk |

The sharp increase above $90\%$ staking reflects the growing liquidity constraints.

### 2. Break-Even Analysis

With $5\%$ staking yield and $70\%$ baseline, the strategy economics are:

| Staking % | Overweight Benefits | Extra Benefits | Expected Shortfall | Net (Overweight) | Total Net Benefit |
|-----------|-------------------|----------------|-------------------|------------------|-------------------|
| $70\%$ | $0.0000\%$ | $0.0000\%$ | $-0.0000\%$ | $+0.0000\%$ | **$+0.0000\%$** |
| $80\%$ | $0.0014\%$ | $0.0524\%$ | $-0.0411\%$ | $-0.0397\%$ | **$+0.0128\%$** |
| $90\%$ | $0.0057\%$ | $0.1049\%$ | $-0.1007\%$ | $-0.0949\%$ | **$+0.0100\%$** |
| $100\%$ | $0.0230\%$ | $0.1573\%$ | $-0.1971\%$ | $-0.1741\%$ | **$-0.0168\%$** |

**Calculation Details**:
- **Overweight Benefits**: Sum of $\delta_{ETH} \times 5\% \text{ yield} \times \frac{episode\_days}{365}$ across all episodes
- **Extra Benefits**: $10.49\% \times (staking\% - 70\%) \times 5\% \text{ yield}$
- **Expected Shortfall**: $-TE_{annual} \times \sqrt{2/\pi} \times 0.5$, where $TE_{annual}$ is from aggregated episodes
- **Net (Overweight)**: Overweight Benefits + Expected Shortfall
- **Total Net Benefit**: Net (Overweight) + Extra Benefits

**Key Finding**: The strategy remains profitable up to $\sim 93\%$ staking, beyond which tracking costs exceed total benefits.

### 3. Portfolio-Level Yield Impact

Due to ETH's $10.49\%$ weight, portfolio yield impacts are modest:

| ETH Staked | Portfolio Yield Gain |
|------------|---------------------|
| $70\%$ | $0.367\%$ |
| $80\%$ | $0.420\%$ |
| $90\%$ | $0.472\%$ |
| $100\%$ | $0.524\%$ |

These yields must be evaluated against the tracking error costs to determine net value.

## Strategic Recommendations

### 1. Optimal Staking Range: $80\%-90\%$

This range provides:
- Positive net benefits ($1-1.3$ basis points)
- Manageable tracking error ($0.10\%-0.25\%$)
- Sufficient liquidity buffer for redemptions
- Attractive risk-adjusted returns

### 2. Risk Management Framework

Implement dynamic staking based on:
- **Market Volatility**: Reduce staking in high volatility periods
- **Redemption Patterns**: Monitor and anticipate fund flows
- **Correlation Changes**: Adjust model parameters as market structure evolves

### 3. Implementation Considerations

- **Gradual Ramp**: Move to target staking levels gradually
- **Monitoring**: Track actual vs. predicted tracking error
- **Flexibility**: Maintain ability to reduce staking quickly if needed

## Limitations and Extensions

### Current Model Limitations

1. **Static Correlations**: Assumes constant correlation structure
2. **No Market Impact**: Ignores transaction costs and slippage
3. **Independent Episodes**: Doesn't model path dependencies
4. **Single Asset Staking**: Only ETH staking considered

### Potential Extensions

1. **Dynamic Correlations**: Incorporate time-varying correlations
2. **Transaction Costs**: Model explicit trading costs
3. **Multi-Asset Staking**: Extend to other stakeable assets
4. **Stress Testing**: Evaluate performance in extreme scenarios

## Conclusion

This framework provides a rigorous approach to the ETH staking optimization problem. By explicitly modeling the trade-offs between staking yields and tracking error, it enables quantitative decision-making about optimal staking levels.

The analysis demonstrates that moderate staking levels $(80\%-90\%)$ can enhance portfolio returns while maintaining acceptable risk levels. The key insight is that while higher staking percentages generate more yield, they also create disproportionate tracking error costs that eventually overwhelm the benefits.

Fund managers can use this framework to:
- Determine optimal staking percentages given their risk tolerance
- Quantify the cost of illiquidity in precise terms
- Make informed decisions about staking strategy adjustments
- Communicate risk-return trade-offs to stakeholders

The mathematical rigor ensures that staking decisions are grounded in quantitative analysis rather than qualitative judgments, leading to better outcomes for fund investors.

---

## Appendix: Detailed Sensitivity Analysis

### Table 1: ETH Overweight Requirements

This table shows required ETH overweight ($\delta_{ETH}$) for various redemption and staking scenarios:

| ETH Staking | Redemption: $5\%$ | $10\%$ | $15\%$ | $20\%$ | $25\%$ | $30\%$ | $35\%$ | $40\%$ | $45\%$ |
|-------------|------------------|--------|--------|--------|--------|--------|--------|--------|--------|
| $70\%$ staked | $0.000\%$ | $0.000\%$ | $0.000\%$ | $0.000\%$ | $0.000\%$ | $0.000\%$ | $0.524\%$ | $1.049\%$ | $1.573\%$ |
| $80\%$ staked | $0.000\%$ | $0.000\%$ | $0.000\%$ | $0.000\%$ | $0.524\%$ | $1.049\%$ | $1.573\%$ | $2.098\%$ | $2.622\%$ |
| $90\%$ staked | $0.000\%$ | $0.000\%$ | $0.524\%$ | $1.049\%$ | $1.573\%$ | $2.098\%$ | $2.622\%$ | $3.147\%$ | $3.671\%$ |
| $100\%$ staked | $0.524\%$ | $1.049\%$ | $1.573\%$ | $2.098\%$ | $2.622\%$ | $3.147\%$ | $3.671\%$ | $4.196\%$ | $4.720\%$ |

**Interpretation**: The diagonal pattern shows how higher staking percentages require overweights at progressively smaller redemption levels.

### Table 2: Comprehensive Risk-Return Metrics

Using the redemption schedule defined in the implementation section:

| % ETH Staked | Total Annual TE | Overweight Benefits | Extra Staking Benefits | Expected Shortfall | Net (Overweight) | Total Net Benefit |
|--------------|-----------------|---------------------|------------------------|-------------------|------------------|-------------------|
| $70\%$ | $0.00\%$ | $0.0000\%$ | $0.0000\%$ | $-0.0000\%$ | $+0.0000\%$ | $+0.0000\%$ |
| $80\%$ | $0.10\%$ | $0.0014\%$ | $0.0524\%$ | $-0.0411\%$ | $-0.0397\%$ | $+0.0128\%$ |
| $90\%$ | $0.25\%$ | $0.0057\%$ | $0.1049\%$ | $-0.1007\%$ | $-0.0949\%$ | $+0.0100\%$ |
| $100\%$ | $0.49\%$ | $0.0230\%$ | $0.1573\%$ | $-0.1971\%$ | $-0.1741\%$ | $-0.0168\%$ |

**Key Metrics Explained**:
- **Total Annual TE**: Annualized tracking error from all redemption episodes
- **Overweight Benefits**: Staking yield earned on ETH overweights during episodes
- **Extra Staking Benefits**: Additional yield from staking above 70% baseline
- **Expected Shortfall**: Expected negative tracking from portfolio deviation
- **Net (Overweight)**: Direct result of the overweight strategy (benefits minus costs)
- **Total Net Benefit**: Comprehensive measure including all value sources

### Table 3: Expected Portfolio Annual Yield from ETH Staking

| % ETH Staked | $3\%$ Yield | $5\%$ Yield | $8\%$ Yield |
|--------------|-------------|-------------|-------------|
| $70\%$ | $0.220\%$ | $0.367\%$ | $0.587\%$ |
| $80\%$ | $0.252\%$ | $0.420\%$ | $0.671\%$ |
| $90\%$ | $0.283\%$ | $0.472\%$ | $0.755\%$ |
| $100\%$ | $0.315\%$ | $0.524\%$ | $0.839\%$ |

**Formula**: Portfolio yield = ETH weight $(10.49\%)$ × % ETH staked × Staking yield