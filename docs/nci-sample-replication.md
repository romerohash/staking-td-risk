# The NCI-US Sample Replication Strategy

## Executive Summary

This document presents a formal mathematical validation for implementing a sample replication strategy using only Bitcoin (BTC) and Ethereum (ETH) to track the Nasdaq Crypto US index (NCI-US). Through a model-free approach that establishes absolute bounds on tracking error, we demonstrate that this two-asset strategy can achieve an expected tracking error of approximately 6% per annum—well within acceptable tolerances for a temporary solution.

The analysis reveals that tracking error is mathematically bounded by **|σ_I − σ_E| ≤ TE ≤ σ_I + σ_E** for any positive semi-definite covariance matrix. Using five-year realized volatilities (June 2020 to June 2025), this translates to bounds between 1.6% and 15.5% annually. These bounds are derived from first principles using only the Cauchy-Schwarz inequality and the positive semi-definite property of covariance matrices, making our conclusions robust to model specification.

## 1. Introduction and Context

### 1.1 The Challenge

Current regulatory constraints prevent the immediate inclusion of certain cryptoassets (XRP, SOL, ADA, XLM) in our ETF structure. These assets collectively represent 10.82% of the benchmark index weight, creating a replication challenge.

### 1.2 The Proposed Solution

We propose a sample replication strategy that:
- Allocates exclusively to BTC (88.24%) and ETH (11.76%)
- Proportionally redistributes the weights of excluded assets
- Maintains the relative weight ratio between BTC and ETH

This approach preserves exposure to 89.18% of the index's market capitalization while maintaining operational feasibility.

## 2. Mathematical Framework: Model-Free Tracking Error Bounds

### 2.1 Active Weight Decomposition

The tracking error (TE) of any portfolio relative to its benchmark is given by:

**TE = √(w′ Σ w)**

where **w** is the active weight vector (portfolio weights minus benchmark weights) and **Σ** is the asset covariance matrix.

For our sample replication:

| Asset | Benchmark Weight | ETF Weight | Active Weight (**w**) |
|-------|-----------------|------------|-----------------------|
| BTC   | 78.69%         | 88.24%     | **+9.55%**           |
| ETH   | 10.49%         | 11.76%     | **+1.27%**           |
| XRP   | 5.49%          | 0%         | **−5.49%**           |
| SOL   | 3.87%          | 0%         | **−3.87%**           |
| ADA   | 1.19%          | 0%         | **−1.19%**           |
| XLM   | 0.27%          | 0%         | **−0.27%**           |

### 2.2 The Model-Free Approach

Rather than assuming a specific covariance structure, we derive bounds that must hold for **any** positive semi-definite covariance matrix. This approach yields results that are:
- Robust to estimation error
- Independent of historical sample period
- Valid under any market regime

We partition the active weights into:
- **w_I**: weights for included assets (BTC, ETH) — positive values
- **w_E**: weights for other assets (XRP, SOL, ADA, XLM) — negative values

### 2.3 Fundamental Tracking Error Bounds

The tracking error can be expressed exactly as:

**TE² = σ²_I + σ²_E + 2 ρ_IE σ_I σ_E**

where:
- **σ_I = √(w′_I Σ_II w_I)** is the volatility of the included basket
- **σ_E = √(w′_E Σ_EE w_E)** is the volatility of the other assets basket
- **ρ_IE** is the correlation between the two baskets

### 2.4 The Cauchy-Schwarz Constraint

The Cauchy-Schwarz inequality, combined with the positive semi-definite property of **Σ**, constrains:

**−1 ≤ ρ_IE ≤ +1**

This mathematical constraint establishes absolute bounds on tracking error:

**|σ_I − σ_E| ≤ TE ≤ σ_I + σ_E**

These bounds are **model-free**—they hold regardless of the specific correlation structure or volatility dynamics assumed.

## 3. Quantitative Analysis

### 3.1 Volatility Calculations

Using realized volatilities from the five-year window (6 Jun 2020 → 5 Jun 2025):
- **BTC**: 3.9% daily (74% annualized), **ETH**: 4.8% daily (92% annualized), correlation: **ρ = 0.70**
- **XRP**: 5.3% daily, **SOL**: 7.1% daily, **ADA**: 5.5% daily, **XLM**: 5.1% daily (average correlation: **ρ = 0.60**)
- Correlation between BTC/ETH and other assets: **ρ = 0.60**

The bucket volatilities are:
- **σ_I** ≈ 0.42% daily
- **σ_E** ≈ 0.52% daily

### 3.2 Tracking Error Scenarios

| Scenario | Correlation between Baskets (**ρ_IE**) | Daily TE | Annual TE |
|----------|--------------------------------------|----------|-----------|
| Best Case | +1.0 | 0.10% | 1.6% |
| **Expected** | **−0.72** | **0.39%** | **6.2%** |
| Worst Case | −1.0 | 0.94% | 15.5% |

The expected scenario reflects typical market conditions where positive correlations among cryptoassets (0.60), combined with negative active weights for other assets, produce a negative basket correlation of −0.72.

### 3.3 Key Insights

1. **Tracking Error Bounds**: Based on the five-year realized volatility data, tracking error would range between 1.6% and 15.5% annually. The mathematical guarantee is that **|σ_I − σ_E| ≤ TE ≤ σ_I + σ_E** for any positive semi-definite covariance matrix.

2. **Expected Performance**: Under the observed correlation structure, tracking error centers around 6% annually—well within acceptable ranges for index tracking products.

3. **Asymptotic Behavior**: As other asset volatility approaches zero, tracking error converges to the minimum bound, validating the strategy in calm market conditions.

## 4. Risk Drivers and Mitigation

### 4.1 Primary Risk Factors

The analysis identifies two key drivers of tracking error:

1. **Volatility Differential**: Higher volatility in other assets increases both bounds
2. **Correlation Structure**: Strong positive correlations among all cryptoassets, paradoxically, can increase tracking error due to the negative weights

### 4.2 Natural Mitigation

The sample replication strategy benefits from:
- **Concentration**: BTC and ETH represent the dominant market share
- **Correlation**: Natural co-movement among cryptoassets provides partial hedging
- **Volatility Scaling**: Lower volatility in larger assets dampens tracking error

## 5. Conclusion

The model-free analysis demonstrates that sample replication using BTC and ETH provides a mathematically sound temporary solution for ETF implementation. The approach:

1. **Establishes mathematical bounds** where TE is constrained by **|σ_I − σ_E| ≤ TE ≤ σ_I + σ_E**
2. **Delivers expected performance** around 6% tracking error based on five-year realized volatilities and correlations
3. **Requires no model assumptions** beyond fundamental mathematical constraints
4. **Maintains exposure** to nearly 90% of the index market capitalization

These bounds, derived solely from the Cauchy-Schwarz inequality and positive semi-definiteness of covariance matrices, provide confidence that the sample replication strategy will perform adequately until full replication becomes feasible.

The mathematical framework presented here offers a robust foundation for evaluating and monitoring the strategy's performance against absolute, model-independent benchmarks.

---

*Marcelo Romero*  
*Director of Portfolio Management*  
*Hashdex*