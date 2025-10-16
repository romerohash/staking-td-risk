"""
Two-Asset Analytical Tracking Error Formula Implementation
=========================================================

This script demonstrates the exact analytical formula for tracking error
with two stakable assets (ETH and SOL) having different unbonding periods.

The implementation follows the mathematical derivation step-by-step,
showing how the formula accounts for:
- Correlated overweights
- Cross-asset hedging effects
- Time-segmented variance from different unbonding periods
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict
from math import sqrt
import numpy as np
from numpy.typing import NDArray
from scipy import stats


@dataclass(frozen=True)
class TwoAssetConfig:
    """Configuration for two-asset staking scenario"""

    # ETH parameters
    eth_weight: float = 0.1049
    eth_staking_pct: float = 0.90
    eth_unbonding_days: int = 10

    # SOL parameters
    sol_weight: float = 0.0387
    sol_staking_pct: float = 0.90  # Changed to 90% to trigger more overweights
    sol_unbonding_days: int = 2

    # Redemption parameters
    lambda_redemptions: float = 18  # Expected redemptions per year

    @property
    def tau_eth(self) -> float:
        """ETH redemption threshold"""
        return 1 - self.eth_staking_pct

    @property
    def tau_sol(self) -> float:
        """SOL redemption threshold"""
        return 1 - self.sol_staking_pct

    @property
    def min_unbonding(self) -> int:
        """Minimum unbonding period (SOL)"""
        return min(self.eth_unbonding_days, self.sol_unbonding_days)

    @property
    def max_unbonding(self) -> int:
        """Maximum unbonding period (ETH)"""
        return max(self.eth_unbonding_days, self.sol_unbonding_days)


def compute_k_components(
    market_cov: NDArray[np.float64], eth_idx: int = 1, sol_idx: int = 3
) -> Dict[str, float]:
    """
    Compute the k-components from Lagrange optimization.

    k_ETH_ETH = eth_weight² × (v_ETH' Σ v_ETH)
    k_ETH_SOL = eth_weight × sol_weight × (v_ETH' Σ v_SOL)
    k_SOL_SOL = sol_weight² × (v_SOL' Σ v_SOL)
    """
    n_assets = market_cov.shape[0]
    inv_cov = np.linalg.inv(market_cov)

    # Build constraint matrix C
    C = np.zeros((3, n_assets))
    C[0, :] = 1  # Sum-to-zero constraint
    C[1, eth_idx] = 1  # ETH constraint
    C[2, sol_idx] = 1  # SOL constraint

    # Compute (C Σ⁻¹ C')⁻¹
    C_inv_cov_C = C @ inv_cov @ C.T
    inv_C_inv_cov_C = np.linalg.inv(C_inv_cov_C)

    # Extract v_ETH and v_SOL
    # v_ETH corresponds to unit vector [0, 1, 0]
    e_eth = np.array([0.0, 1.0, 0.0])
    lambda_eth = inv_C_inv_cov_C @ e_eth
    v_eth = inv_cov @ C.T @ lambda_eth

    # v_SOL corresponds to unit vector [0, 0, 1]
    e_sol = np.array([0.0, 0.0, 1.0])
    lambda_sol = inv_C_inv_cov_C @ e_sol
    v_sol = inv_cov @ C.T @ lambda_sol

    # Compute variance components
    v_eth_sigma_v_eth = v_eth @ market_cov @ v_eth
    v_sol_sigma_v_sol = v_sol @ market_cov @ v_sol
    v_eth_sigma_v_sol = v_eth @ market_cov @ v_sol

    return {
        'v_eth_sigma_v_eth': v_eth_sigma_v_eth,
        'v_sol_sigma_v_sol': v_sol_sigma_v_sol,
        'v_eth_sigma_v_sol': v_eth_sigma_v_sol,
        'v_eth': v_eth,
        'v_sol': v_sol,
    }


def variance_full_period(
    r: float, config: TwoAssetConfig, k_components: Dict[str, float]
) -> float:
    """
    Calculate variance when both assets are overweighted (days 1-2).

    Var_full(r) = k_ETH_ETH × (r - τ_ETH)²₊ +
                  2 × k_ETH_SOL × (r - τ_ETH)₊ × (r - τ_SOL)₊ +
                  k_SOL_SOL × (r - τ_SOL)²₊
    """
    # Calculate individual overweights
    excess_eth = max(0, r - config.tau_eth)
    excess_sol = max(0, r - config.tau_sol)

    # Compute k-components
    k_eth_eth = config.eth_weight**2 * k_components['v_eth_sigma_v_eth']
    k_sol_sol = config.sol_weight**2 * k_components['v_sol_sigma_v_sol']
    k_eth_sol = (
        config.eth_weight * config.sol_weight * k_components['v_eth_sigma_v_sol']
    )

    # Calculate variance
    variance = (
        k_eth_eth * excess_eth**2
        + 2 * k_eth_sol * excess_eth * excess_sol
        + k_sol_sol * excess_sol**2
    )

    return variance


def variance_partial_period(
    r: float, config: TwoAssetConfig, k_components: Dict[str, float]
) -> float:
    """
    Calculate variance when only ETH is overweighted (days 3-10).

    Var_partial(r) = k_ETH_ETH × (r - τ_ETH)²₊
    """
    excess_eth = max(0, r - config.tau_eth)
    k_eth_eth = config.eth_weight**2 * k_components['v_eth_sigma_v_eth']

    return k_eth_eth * excess_eth**2


def expected_values_discrete(
    redemption_dist: stats.rv_discrete,
    config: TwoAssetConfig,
    k_components: Dict[str, float],
) -> Dict[str, float]:
    """
    Calculate expected values for discrete redemption distribution.

    Returns:
    - E[Var_full(R)]
    - E[Var_partial(R)]
    - E[(R - τ_ETH)²₊]
    - E[(R - τ_SOL)²₊]
    - E[(R - τ_ETH)₊ × (R - τ_SOL)₊]
    """
    # Get discrete values and probabilities
    if hasattr(redemption_dist, 'xk') and hasattr(redemption_dist, 'pk'):
        values = redemption_dist.xk
        probs = redemption_dist.pk
    else:
        # Fallback sampling
        samples = redemption_dist.rvs(size=10000)
        unique_vals, counts = np.unique(samples, return_counts=True)
        values = unique_vals
        probs = counts / counts.sum()

    # Calculate expectations
    exp_var_full = 0.0
    exp_var_partial = 0.0
    exp_eth_squared = 0.0
    exp_sol_squared = 0.0
    exp_cross_term = 0.0

    for r, p in zip(values, probs):
        # Variance expectations
        exp_var_full += p * variance_full_period(r, config, k_components)
        exp_var_partial += p * variance_partial_period(r, config, k_components)

        # Component expectations
        excess_eth = max(0, r - config.tau_eth)
        excess_sol = max(0, r - config.tau_sol)

        exp_eth_squared += p * excess_eth**2
        exp_sol_squared += p * excess_sol**2
        exp_cross_term += p * excess_eth * excess_sol

    return {
        'exp_var_full': exp_var_full,
        'exp_var_partial': exp_var_partial,
        'exp_eth_squared': exp_eth_squared,
        'exp_sol_squared': exp_sol_squared,
        'exp_cross_term': exp_cross_term,
    }


def analytical_tracking_error_two_asset(
    config: TwoAssetConfig,
    k_components: Dict[str, float],
    expectations: Dict[str, float],
) -> float:
    """
    Calculate the analytical tracking error using the two-asset formula.

    TE = √[λ × (d_short × E[Var_full] + (d_long - d_short) × E[Var_partial])]
    """
    d_short = config.min_unbonding  # 2 days
    d_long = config.max_unbonding  # 10 days

    variance_days = (
        d_short * expectations['exp_var_full']
        + (d_long - d_short) * expectations['exp_var_partial']
    )

    annual_variance = config.lambda_redemptions * variance_days

    return sqrt(annual_variance)


def decompose_tracking_error(
    config: TwoAssetConfig,
    k_components: Dict[str, float],
    expectations: Dict[str, float],
) -> Dict[str, float]:
    """
    Decompose tracking error into components for analysis.
    """
    # Calculate k values
    k_eth_eth = config.eth_weight**2 * k_components['v_eth_sigma_v_eth']
    k_sol_sol = config.sol_weight**2 * k_components['v_sol_sigma_v_sol']
    k_eth_sol = (
        config.eth_weight * config.sol_weight * k_components['v_eth_sigma_v_sol']
    )

    # Time periods
    d_short = config.min_unbonding
    d_long = config.max_unbonding

    # Component contributions to annual variance
    eth_contribution = (
        config.lambda_redemptions * d_long * k_eth_eth * expectations['exp_eth_squared']
    )
    sol_contribution = (
        config.lambda_redemptions
        * d_short
        * k_sol_sol
        * expectations['exp_sol_squared']
    )
    cross_contribution = (
        config.lambda_redemptions
        * d_short
        * 2
        * k_eth_sol
        * expectations['exp_cross_term']
    )

    total_variance = eth_contribution + sol_contribution + cross_contribution
    total_te = sqrt(total_variance)

    # Individual tracking errors (hypothetical single-asset)
    te_eth_only = sqrt(
        config.lambda_redemptions * d_long * k_eth_eth * expectations['exp_eth_squared']
    )
    te_sol_only = sqrt(
        config.lambda_redemptions
        * d_short
        * k_sol_sol
        * expectations['exp_sol_squared']
    )

    return {
        'total_te': total_te,
        'te_eth_only': te_eth_only,
        'te_sol_only': te_sol_only,
        'eth_contribution_pct': eth_contribution / total_variance * 100
        if total_variance > 0
        else 0,
        'sol_contribution_pct': sol_contribution / total_variance * 100
        if total_variance > 0
        else 0,
        'cross_contribution_pct': cross_contribution / total_variance * 100
        if total_variance > 0
        else 0,
        'k_eth_eth': k_eth_eth,
        'k_sol_sol': k_sol_sol,
        'k_eth_sol': k_eth_sol,
        'correlation_cost': total_te - (te_eth_only**2 + te_sol_only**2) ** 0.5,
    }


def create_market_covariance() -> NDArray[np.float64]:
    """
    Create the market covariance matrix for NCI-US index.

    Assets: BTC, ETH, XRP, SOL, ADA, XLM
    """
    daily_vols = np.array([0.039, 0.048, 0.053, 0.071, 0.055, 0.051])

    # Correlation structure
    n = len(daily_vols)
    corr_matrix = np.eye(n)

    # BTC-ETH correlation
    corr_matrix[0, 1] = corr_matrix[1, 0] = 0.70

    # Within excluded assets (XRP, SOL, ADA, XLM)
    for i in range(2, n):
        for j in range(i + 1, n):
            corr_matrix[i, j] = corr_matrix[j, i] = 0.60

    # Cross correlations
    for i in [0, 1]:  # BTC, ETH
        for j in range(2, n):  # Others
            if (i, j) != (0, 1) and (i, j) != (1, 0):
                corr_matrix[i, j] = corr_matrix[j, i] = 0.60

    # Convert to covariance
    vol_diag = np.diag(daily_vols)
    cov_matrix = vol_diag @ corr_matrix @ vol_diag

    return cov_matrix


def main():
    """Demonstrate the two-asset analytical formula"""
    print('TWO-ASSET ANALYTICAL TRACKING ERROR FORMULA')
    print('=' * 70)

    # Configuration
    config = TwoAssetConfig()

    print('\nConfiguration:')
    print(
        f'  ETH: {config.eth_weight:.2%} weight, {config.eth_staking_pct:.0%} staked, {config.eth_unbonding_days} day unbonding'
    )
    print(
        f'  SOL: {config.sol_weight:.2%} weight, {config.sol_staking_pct:.0%} staked, {config.sol_unbonding_days} day unbonding'
    )
    print(f'  Expected redemptions: {config.lambda_redemptions} per year')

    # Create redemption distribution
    values = [0.05, 0.10, 0.20, 0.30]
    weights = [12 / 18, 3 / 18, 2 / 18, 1 / 18]
    redemption_dist = stats.rv_discrete(values=(values, weights))

    print('\nRedemption Distribution:')
    for v, w in zip(values, weights):
        print(f'  {v:.0%}: {w:.1%} probability')

    # Get market covariance and compute k-components
    market_cov = create_market_covariance()
    k_components = compute_k_components(market_cov)

    print('\nLagrangian Optimization Results:')
    print(f"  v_ETH' Σ v_ETH: {k_components['v_eth_sigma_v_eth']:.6f}")
    print(f"  v_SOL' Σ v_SOL: {k_components['v_sol_sigma_v_sol']:.6f}")
    print(f"  v_ETH' Σ v_SOL: {k_components['v_eth_sigma_v_sol']:.6f}")

    # Calculate expectations
    expectations = expected_values_discrete(redemption_dist, config, k_components)

    print('\nExpected Values:')
    print(f'  E[(R - τ_ETH)²₊]: {expectations["exp_eth_squared"]:.6f}')
    print(f'  E[(R - τ_SOL)²₊]: {expectations["exp_sol_squared"]:.6f}')
    print(f'  E[(R - τ_ETH)₊ × (R - τ_SOL)₊]: {expectations["exp_cross_term"]:.6f}')

    # Calculate tracking error
    te = analytical_tracking_error_two_asset(config, k_components, expectations)

    print('\nTRACKING ERROR RESULTS:')
    print(f'  Annual TE: {te:.4%}')

    # Decompose results
    decomp = decompose_tracking_error(config, k_components, expectations)

    print('\nDecomposition:')
    print(f'  ETH-only TE: {decomp["te_eth_only"]:.4%}')
    print(f'  SOL-only TE: {decomp["te_sol_only"]:.4%}')
    print(
        f'  Independence approx: {(decomp["te_eth_only"] ** 2 + decomp["te_sol_only"] ** 2) ** 0.5:.4%}'
    )
    print(f'  Exact two-asset TE: {decomp["total_te"]:.4%}')
    print(f'  Correlation cost: {decomp["correlation_cost"]:.4%}')

    print('\nVariance Contributions:')
    print(f'  ETH term: {decomp["eth_contribution_pct"]:.1f}%')
    print(f'  SOL term: {decomp["sol_contribution_pct"]:.1f}%')
    print(f'  Cross term: {decomp["cross_contribution_pct"]:.1f}%')

    print('\nk-Components:')
    print(f'  k_ETH_ETH: {decomp["k_eth_eth"]:.8f}')
    print(f'  k_SOL_SOL: {decomp["k_sol_sol"]:.8f}')
    print(f'  k_ETH_SOL: {decomp["k_eth_sol"]:.8f}')

    # Show redemption-specific variances
    print('\nRedemption-Specific Analysis:')
    print(f'{"Redemption":>10} {"Full Var":>12} {"Partial Var":>12} {"Var-Days":>12}')
    print('-' * 50)

    for r in values:
        var_full = variance_full_period(r, config, k_components)
        var_partial = variance_partial_period(r, config, k_components)
        var_days = (
            config.min_unbonding * var_full
            + (config.max_unbonding - config.min_unbonding) * var_partial
        )
        print(f'{r:>10.0%} {var_full:>12.8f} {var_partial:>12.8f} {var_days:>12.8f}')


if __name__ == '__main__':
    main()
