"""
Analytical Tracking Error with Two-Point Distribution
====================================================

Implements the analytical TE formula with a Two-Point redemption distribution
and performs sensitivity analysis on staking percentage and distribution parameters.

The Two-Point Distribution models bimodal redemption patterns:
- Small redemptions (e.g., retail investors)
- Large redemptions (e.g., institutional investors)
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, List
import numpy as np
from math import sqrt
from core.optimal_eth_over_te_dynamic import MarketConfig, CovarianceBuilder


@dataclass(frozen=True)
class TwoPointDistribution:
    """
    Two-Point Distribution for redemption sizes.

    P(R = r1) = p
    P(R = r2) = 1-p
    """

    r1: float  # First redemption size
    r2: float  # Second redemption size
    p: float  # Probability of r1

    def __post_init__(self):
        if not 0 <= self.r1 <= 1:
            raise ValueError(f'r1 must be in [0,1], got {self.r1}')
        if not 0 <= self.r2 <= 1:
            raise ValueError(f'r2 must be in [0,1], got {self.r2}')
        if not 0 <= self.p <= 1:
            raise ValueError(f'p must be in [0,1], got {self.p}')

    @property
    def mean(self) -> float:
        """Expected redemption size"""
        return self.p * self.r1 + (1 - self.p) * self.r2

    @property
    def variance(self) -> float:
        """Variance of redemption size"""
        mean = self.mean
        return self.p * self.r1**2 + (1 - self.p) * self.r2**2 - mean**2

    def expected_squared_excess(self, threshold: float) -> float:
        """E[(R - τ)²₊] for given threshold"""
        excess1 = max(0, self.r1 - threshold)
        excess2 = max(0, self.r2 - threshold)
        return self.p * excess1**2 + (1 - self.p) * excess2**2

    def describe(self) -> str:
        """Human-readable description"""
        return (
            f'{self.r1:.1%} with prob {self.p:.1f}, '
            f'{self.r2:.1%} with prob {1 - self.p:.1f}'
        )


def calculate_base_k(market: MarketConfig) -> float:
    """
    Calculate base_k = eth_weight² × (v' Σ v) from market configuration.
    """
    # Build covariance matrix
    cov_builder = CovarianceBuilder(market)
    cov_matrix = cov_builder.matrix
    inv_cov = np.linalg.inv(cov_matrix)

    # Constraint matrix for Lagrange optimization
    n = len(market.assets)
    C = np.vstack([
        np.ones(n),  # sum-to-zero
        np.eye(n)[1],  # ETH-specific
    ])

    # Unit constraint vector e2 = [0, 1]'
    e2 = np.array([0.0, 1.0])

    # Compute v = Σ⁻¹ C' (C Σ⁻¹ C')⁻¹ e₂
    C_inv_cov_C = C @ inv_cov @ C.T
    lambda_0 = np.linalg.solve(C_inv_cov_C, e2)
    v = inv_cov @ C.T @ lambda_0

    # Compute (v' Σ v)
    v_sigma_v = v @ cov_matrix @ v

    # Calculate base_k
    eth_weight = market.eth_weight
    base_k = eth_weight**2 * v_sigma_v

    return base_k


def analytical_te(
    lambda_redemptions: float,
    episode_days: float,
    base_k: float,
    staking_pct: float,
    distribution: TwoPointDistribution,
) -> float:
    """
    Calculate analytical tracking error.

    TE = √[λ × d × base_k × E[(R - τ)²₊]]
    """
    threshold = 1 - staking_pct
    expected_squared_excess = distribution.expected_squared_excess(threshold)

    variance_days = lambda_redemptions * episode_days * base_k * expected_squared_excess
    return sqrt(variance_days)


def sensitivity_analysis_staking(
    base_k: float,
    lambda_redemptions: float,
    episode_days: float,
    distribution: TwoPointDistribution,
    staking_range: Tuple[float, float],
    n_points: int = 20,
) -> Tuple[List[float], List[float]]:
    """
    Analyze TE sensitivity to staking percentage.
    """
    staking_pcts = np.linspace(staking_range[0], staking_range[1], n_points)
    te_values = []

    for staking_pct in staking_pcts:
        te = analytical_te(
            lambda_redemptions, episode_days, base_k, staking_pct, distribution
        )
        te_values.append(te)

    return staking_pcts.tolist(), te_values


def sensitivity_analysis_distribution(
    base_k: float,
    lambda_redemptions: float,
    episode_days: float,
    staking_pct: float,
    r1_range: Tuple[float, float],
    r2_range: Tuple[float, float],
    p: float = 0.8,
) -> dict:
    """
    Analyze TE sensitivity to distribution parameters.
    """
    n_points = 10
    r1_values = np.linspace(r1_range[0], r1_range[1], n_points)
    r2_values = np.linspace(r2_range[0], r2_range[1], n_points)

    # Create grid
    te_grid = np.zeros((n_points, n_points))

    for i, r1 in enumerate(r1_values):
        for j, r2 in enumerate(r2_values):
            dist = TwoPointDistribution(r1, r2, p)
            te = analytical_te(
                lambda_redemptions, episode_days, base_k, staking_pct, dist
            )
            te_grid[i, j] = te

    return {
        'r1_values': r1_values.tolist(),
        'r2_values': r2_values.tolist(),
        'te_grid': te_grid,
        'p': p,
    }


def main():
    """Demonstrate Two-Point Distribution analysis"""
    # Market configuration
    market = MarketConfig()
    base_k = calculate_base_k(market)

    # Standard parameters
    lambda_redemptions = 18  # Total expected redemptions
    episode_days = 10  # Days per episode

    print('TWO-POINT DISTRIBUTION TRACKING ERROR ANALYSIS')
    print('=' * 70)
    print('\nMarket Parameters:')
    print(f'  ETH weight: {market.eth_weight:.4%}')
    print(f'  base_k: {base_k:.6f}')
    print(f'  λ (redemptions): {lambda_redemptions}')
    print(f'  Episode duration: {episode_days} days')

    # Example distributions
    distributions = [
        TwoPointDistribution(0.05, 0.30, 0.8),  # Mostly small, some large
        TwoPointDistribution(0.10, 0.20, 0.5),  # Equal mix
        TwoPointDistribution(0.02, 0.50, 0.9),  # Mostly tiny, rare huge
    ]

    # 1. Compare distributions at different staking levels
    print('\n' + '-' * 70)
    print('TRACKING ERROR BY DISTRIBUTION AND STAKING LEVEL')
    print('-' * 70)

    staking_levels = [0.0, 0.5, 0.7, 0.8, 0.9, 0.95, 1.0]

    print('Staking', end='')
    for dist in distributions:
        print(f'  |  {dist.describe()}', end='')
    print()
    print('-' * 70)

    for staking in staking_levels:
        print(f'{staking:6.0%}', end='')
        for dist in distributions:
            te = analytical_te(lambda_redemptions, episode_days, base_k, staking, dist)
            print(f'    {te:7.4%}', end='')
        print()

    # 2. Detailed analysis for one distribution
    print('\n' + '-' * 70)
    print('DETAILED ANALYSIS: 5% frequent, 30% rare redemptions')
    print('-' * 70)

    dist = TwoPointDistribution(0.05, 0.30, 0.8)
    print(f'\nDistribution: {dist.describe()}')
    print(f'  Mean redemption: {dist.mean:.3%}')
    print(f'  Std deviation: {sqrt(dist.variance):.3%}')

    print('\nThreshold Effects:')
    for staking in [0.7, 0.8, 0.9, 0.95]:
        threshold = 1 - staking
        e_squared_excess = dist.expected_squared_excess(threshold)

        contributing = []
        if dist.r1 > threshold:
            contributing.append(f'{dist.r1:.0%}')
        if dist.r2 > threshold:
            contributing.append(f'{dist.r2:.0%}')

        print(
            f'  {staking:.0%} staking (τ={threshold:.2f}): '
            f'E[(R-τ)²₊] = {e_squared_excess:.6f}, '
            f'Contributing: {contributing}'
        )

    # 3. Sensitivity to distribution parameters
    print('\n' + '-' * 70)
    print('SENSITIVITY TO SMALL REDEMPTION SIZE (r1)')
    print('-' * 70)

    staking = 0.8
    r2 = 0.30
    p = 0.8

    print(f'\nFixed: r2={r2:.0%}, p={p:.1f}, staking={staking:.0%}')
    print('\nr1      Mean    E[(R-τ)²₊]    TE')
    print('-' * 40)

    for r1 in [0.01, 0.05, 0.10, 0.15, 0.20]:
        dist = TwoPointDistribution(r1, r2, p)
        threshold = 1 - staking
        e_squared = dist.expected_squared_excess(threshold)
        te = analytical_te(lambda_redemptions, episode_days, base_k, staking, dist)

        print(f'{r1:4.0%}    {dist.mean:4.0%}    {e_squared:9.6f}    {te:6.4%}')

    # 4. Optimal staking given distribution
    print('\n' + '-' * 70)
    print('BREAK-EVEN ANALYSIS')
    print('-' * 70)

    # Assuming 5% staking yield
    annual_yield = 0.05
    eth_weight = market.eth_weight

    print(
        f'\nAssuming {annual_yield:.0%} annual staking yield on ETH weight {eth_weight:.2%}'
    )
    print('Distribution: 5% frequent (80%), 30% rare (20%)')

    dist = TwoPointDistribution(0.05, 0.30, 0.8)

    print('\nStaking   TE      Benefit   Net      Decision')
    print('-' * 50)

    for staking in [0.0, 0.5, 0.7, 0.8, 0.85, 0.9, 0.95]:
        te = analytical_te(lambda_redemptions, episode_days, base_k, staking, dist)

        # Staking benefit (simplified - not including overweight benefits)
        benefit = eth_weight * staking * annual_yield

        # Expected shortfall (simplified)
        shortfall = -te * sqrt(2 / np.pi) * 0.5

        net = benefit + shortfall
        decision = '✓' if net > 0 else '✗'

        print(f'{staking:6.0%}  {te:6.4%}  {benefit:7.4%}  {net:+7.4%}  {decision}')

    print('\n' + '=' * 70)
    print('KEY INSIGHTS:')
    print('1. Threshold effects dominate - small frequent redemptions may not matter')
    print('2. Distribution shape critically affects optimal staking level')
    print('3. Rare large redemptions can make high staking levels unviable')


if __name__ == '__main__':
    main()
