"""
Optimized Two-Asset Tracking Error Calculator using Numba
========================================================

Performance optimizations:
1. Pre-computed k-components cached across calculations
2. Vectorized sensitivity analysis
3. Numba JIT compilation for hot paths
4. Minimal object creation overhead
"""

import numpy as np
from numba import jit
from typing import Dict, Tuple, Optional
from dataclasses import dataclass


@jit(
    'Tuple((float64, float64, float64))(float64[:,:], float64, float64)',
    nopython=True,
    cache=True,
    fastmath=True,
)
def compute_k_components_numba(
    cov_matrix: np.ndarray, eth_weight: float, sol_weight: float
) -> Tuple[float, float, float]:
    """JIT-compiled k-component calculation"""
    n_assets = cov_matrix.shape[0]
    inv_cov = np.linalg.inv(cov_matrix)

    # Constraint matrix: sum-to-zero, ETH, SOL
    C = np.zeros((3, n_assets))
    C[0, :] = 1.0  # Sum-to-zero
    C[1, 1] = 1.0  # ETH constraint (index 1)
    C[2, 3] = 1.0  # SOL constraint (index 3)

    # Solve for v_ETH and v_SOL
    # Make C.T contiguous for better performance
    C_T = np.ascontiguousarray(C.T)
    C_inv_cov_C = C @ inv_cov @ C_T
    inv_C_inv_cov_C = np.linalg.inv(C_inv_cov_C)

    # v_ETH
    e_eth = np.array([0.0, 1.0, 0.0])
    lambda_eth = inv_C_inv_cov_C @ e_eth
    v_eth = inv_cov @ C_T @ lambda_eth

    # v_SOL
    e_sol = np.array([0.0, 0.0, 1.0])
    lambda_sol = inv_C_inv_cov_C @ e_sol
    v_sol = inv_cov @ C_T @ lambda_sol

    # Compute variance components (ensure contiguous arrays for optimal performance)
    v_eth_contig = np.ascontiguousarray(v_eth)
    v_sol_contig = np.ascontiguousarray(v_sol)
    cov_matrix_contig = np.ascontiguousarray(cov_matrix)

    v_eth_sigma_v_eth = v_eth_contig @ cov_matrix_contig @ v_eth_contig
    v_sol_sigma_v_sol = v_sol_contig @ cov_matrix_contig @ v_sol_contig
    v_eth_sigma_v_sol = v_eth_contig @ cov_matrix_contig @ v_sol_contig

    # Calculate k values
    k_eth_eth = eth_weight * eth_weight * v_eth_sigma_v_eth
    k_sol_sol = sol_weight * sol_weight * v_sol_sigma_v_sol
    k_eth_sol = eth_weight * sol_weight * v_eth_sigma_v_sol

    return k_eth_eth, k_sol_sol, k_eth_sol


@jit(
    'float64[:](float64[:], float64[:], float64, float64, float64, float64[:], float64[:], float64, int64, int64)',
    nopython=True,
    cache=True,
    fastmath=True,
)
def calculate_tracking_error_vectorized(
    staking_levels_eth: np.ndarray,
    staking_levels_sol: np.ndarray,
    k_eth_eth: float,
    k_sol_sol: float,
    k_eth_sol: float,
    redemption_sizes: np.ndarray,
    redemption_probs: np.ndarray,
    lambda_r: float,
    d_eth: int,
    d_sol: int,
) -> np.ndarray:
    """Vectorized tracking error calculation for multiple staking levels"""
    n_levels = len(staking_levels_eth)
    tracking_errors = np.zeros(n_levels)

    d_short = min(d_eth, d_sol)
    d_long = max(d_eth, d_sol)

    for i in range(n_levels):
        tau_eth = 1.0 - staking_levels_eth[i]
        tau_sol = 1.0 - staking_levels_sol[i]

        # Calculate expected variances
        exp_var_full = 0.0
        exp_var_partial = 0.0

        for j in range(len(redemption_sizes)):
            r = redemption_sizes[j]
            p = redemption_probs[j]

            excess_eth = max(0.0, r - tau_eth)
            excess_sol = max(0.0, r - tau_sol)

            # Full period variance
            var_full = (
                k_eth_eth * excess_eth * excess_eth
                + 2.0 * k_eth_sol * excess_eth * excess_sol
                + k_sol_sol * excess_sol * excess_sol
            )

            # Partial period variance (ETH only)
            var_partial = k_eth_eth * excess_eth * excess_eth

            exp_var_full += p * var_full
            exp_var_partial += p * var_partial

        # Calculate annual variance
        variance_days = d_short * exp_var_full + (d_long - d_short) * exp_var_partial
        annual_variance = lambda_r * variance_days

        tracking_errors[i] = np.sqrt(annual_variance)

    return tracking_errors


@jit(
    'Tuple((float64[:], float64[:], float64[:], float64[:], float64[:], float64[:]))'
    '(float64[:], float64[:], float64[:], float64, float64, float64, float64, float64, float64, '
    'float64[:], float64[:], float64, int64, int64, float64, float64)',
    nopython=True,
    cache=True,
    fastmath=True,
)
def calculate_net_benefits_vectorized(
    tracking_errors: np.ndarray,
    staking_levels_eth: np.ndarray,
    staking_levels_sol: np.ndarray,
    eth_weight: float,
    sol_weight: float,
    eth_yield: float,
    sol_yield: float,
    eth_baseline: float,
    sol_baseline: float,
    redemption_sizes: np.ndarray,
    redemption_probs: np.ndarray,
    lambda_r: float,
    d_eth: int,
    d_sol: int,
    current_td: float,
    cap_td: float,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Vectorized net benefit calculation"""
    n_levels = len(staking_levels_eth)
    yield_benefits = np.zeros(n_levels)
    expected_shortfalls = np.zeros(n_levels)
    tracking_difference_budgets = np.zeros(n_levels)
    td_budget_deficits = np.zeros(n_levels)
    net_benefits = np.zeros(n_levels)
    net_benefits_bps = np.zeros(n_levels)

    # Calculate tracking difference budget once (constant across all staking levels)
    tracking_difference_budget = cap_td - current_td

    for i in range(n_levels):
        # Benefit above baseline
        eth_benefit_baseline = (
            eth_weight * max(0.0, staking_levels_eth[i] - eth_baseline) * eth_yield
        )
        sol_benefit_baseline = (
            sol_weight * max(0.0, staking_levels_sol[i] - sol_baseline) * sol_yield
        )

        # Marginal benefit during episodes
        tau_eth = 1.0 - staking_levels_eth[i]
        tau_sol = 1.0 - staking_levels_sol[i]

        exp_excess_eth = 0.0
        exp_excess_sol = 0.0

        for j in range(len(redemption_sizes)):
            r = redemption_sizes[j]
            p = redemption_probs[j]
            exp_excess_eth += p * max(0.0, r - tau_eth)
            exp_excess_sol += p * max(0.0, r - tau_sol)

        eth_episode_fraction = lambda_r * d_eth / 365.0
        sol_episode_fraction = lambda_r * d_sol / 365.0

        eth_benefit_marginal = (
            eth_weight * eth_yield * eth_episode_fraction * exp_excess_eth
        )
        sol_benefit_marginal = (
            sol_weight * sol_yield * sol_episode_fraction * exp_excess_sol
        )

        total_benefit = (
            eth_benefit_baseline
            + eth_benefit_marginal
            + sol_benefit_baseline
            + sol_benefit_marginal
        )

        # Expected shortfall (negative value)
        expected_shortfall = -tracking_errors[i] * np.sqrt(2.0 / np.pi) * 0.5

        # TD Budget Deficit = MIN[0, (TD Budget - Expected Shortfall)]
        # Note: expected_shortfall is negative, so we use its absolute value
        td_budget_deficit = min(
            0.0, tracking_difference_budget - abs(expected_shortfall)
        )

        # Net benefit = Total Yield + TD Budget Deficit
        # Since td_budget_deficit is non-positive, adding it correctly reduces the net benefit when there's a deficit
        net_benefit = total_benefit + td_budget_deficit

        yield_benefits[i] = total_benefit
        expected_shortfalls[i] = expected_shortfall
        tracking_difference_budgets[i] = tracking_difference_budget
        td_budget_deficits[i] = td_budget_deficit
        net_benefits[i] = net_benefit
        net_benefits_bps[i] = net_benefit * 10000.0

    return (
        yield_benefits,
        expected_shortfalls,
        tracking_difference_budgets,
        td_budget_deficits,
        net_benefits,
        net_benefits_bps,
    )


@dataclass
class OptimizedCalculator:
    """Optimized calculator with cached computations"""

    # Market parameters (constant across calculations)
    cov_matrix: np.ndarray
    eth_weight: float
    sol_weight: float
    redemption_sizes: np.ndarray
    redemption_probs: np.ndarray
    lambda_r: float

    # Yield parameters
    eth_yield: float
    sol_yield: float
    eth_baseline: float
    sol_baseline: float

    # Unbonding periods
    d_eth: int
    d_sol: int

    # Fund details
    nav: float = 500000000.0
    current_td: float = 0.0143
    cap_td: float = 0.015

    # Cached k-components
    _k_components: Optional[Tuple[float, float, float]] = None

    @property
    def k_components(self) -> Tuple[float, float, float]:
        """Lazy computation and caching of k-components"""
        if self._k_components is None:
            self._k_components = compute_k_components_numba(
                self.cov_matrix, self.eth_weight, self.sol_weight
            )
        return self._k_components

    def calculate_tracking_errors(
        self, staking_levels_eth: np.ndarray, staking_levels_sol: np.ndarray
    ) -> np.ndarray:
        """Calculate tracking errors for multiple staking level combinations"""
        k_eth_eth, k_sol_sol, k_eth_sol = self.k_components

        return calculate_tracking_error_vectorized(
            staking_levels_eth,
            staking_levels_sol,
            k_eth_eth,
            k_sol_sol,
            k_eth_sol,
            self.redemption_sizes,
            self.redemption_probs,
            self.lambda_r,
            self.d_eth,
            self.d_sol,
        )

    def calculate_net_benefits(
        self,
        tracking_errors: np.ndarray,
        staking_levels_eth: np.ndarray,
        staking_levels_sol: np.ndarray,
    ) -> Dict[str, np.ndarray]:
        """Calculate net benefits for multiple staking levels"""
        yields, shortfalls, td_budgets, td_deficits, net_ben, net_bps = (
            calculate_net_benefits_vectorized(
                tracking_errors,
                staking_levels_eth,
                staking_levels_sol,
                self.eth_weight,
                self.sol_weight,
                self.eth_yield,
                self.sol_yield,
                self.eth_baseline,
                self.sol_baseline,
                self.redemption_sizes,
                self.redemption_probs,
                self.lambda_r,
                self.d_eth,
                self.d_sol,
                self.current_td,
                self.cap_td,
            )
        )

        return {
            'yield_benefits': yields,
            'expected_shortfalls': shortfalls,
            'tracking_difference_budgets': td_budgets,
            'td_budget_deficits': td_deficits,
            'net_benefits': net_ben,
            'net_benefits_bps': net_bps,
        }

    def perform_2d_sensitivity_analysis(
        self,
        eth_range: Tuple[float, float] = None,
        sol_range: Tuple[float, float] = None,
        n_points: int = 31,
    ) -> Dict[str, np.ndarray]:
        """
        Vectorized 2D sensitivity analysis

        The search space defaults to starting at each asset's baseline staking percentage,
        allowing optimization to recommend levels below the baseline when beneficial.

        Args:
            eth_range: Optional tuple (min, max) for ETH staking levels.
                      Defaults to (eth_baseline, 1.00)
            sol_range: Optional tuple (min, max) for SOL staking levels.
                      Defaults to (sol_baseline, 1.00)
            n_points: Number of points to sample in each dimension
        """
        # Use baseline-derived ranges if not explicitly provided
        if eth_range is None:
            eth_range = (self.eth_baseline, 1.00)
        if sol_range is None:
            sol_range = (self.sol_baseline, 1.00)

        # Create meshgrid of staking levels
        eth_levels = np.linspace(eth_range[0], eth_range[1], n_points)
        sol_levels = np.linspace(sol_range[0], sol_range[1], n_points)

        eth_grid, sol_grid = np.meshgrid(eth_levels, sol_levels)
        eth_flat = eth_grid.flatten()
        sol_flat = sol_grid.flatten()

        # Calculate all tracking errors at once
        tracking_errors = self.calculate_tracking_errors(eth_flat, sol_flat)

        # Calculate all net benefits at once
        results = self.calculate_net_benefits(tracking_errors, eth_flat, sol_flat)

        # Reshape results back to grid
        shape = (n_points, n_points)
        return {
            'eth_levels': eth_grid,
            'sol_levels': sol_grid,
            'tracking_errors': tracking_errors.reshape(shape),
            'yield_benefits': results['yield_benefits'].reshape(shape),
            'expected_shortfalls': results['expected_shortfalls'].reshape(shape),
            'net_benefits_bps': results['net_benefits_bps'].reshape(shape),
        }


# Factory function for creating optimized calculator from existing structures
def create_optimized_calculator(
    benchmark_weights: Dict[str, float],
    market_params: Dict,
    redemption_dist: Dict,
    yield_params: Dict,
    unbonding_days: Dict[str, int],
    fund_details: Optional[Dict[str, float]] = None,
) -> OptimizedCalculator:
    """Create optimized calculator from existing parameter structures"""

    # Build covariance matrix (reuse existing logic)
    assets = ['BTC', 'ETH', 'XRP', 'SOL', 'ADA', 'XLM']
    n = len(assets)

    # Extract volatilities
    vols = np.array([market_params['daily_volatilities'][asset] for asset in assets])

    # Build correlation matrix
    corr_matrix = np.eye(n)
    for pair, corr in market_params['correlations'].items():
        i = assets.index(pair[0])
        j = assets.index(pair[1])
        corr_matrix[i, j] = corr_matrix[j, i] = corr

    # Convert to covariance
    vol_diag = np.diag(vols)
    cov_matrix = vol_diag @ corr_matrix @ vol_diag

    # Convert redemption distribution
    redemption_sizes = np.array(redemption_dist['sizes'])
    redemption_probs = np.array(redemption_dist['probabilities'])

    # Extract fund details or use defaults
    if fund_details:
        nav = fund_details.get('nav', 500000000.0)
        current_td = fund_details.get('current_td', 0.0143)
        cap_td = fund_details.get('cap_td', 0.015)
    else:
        nav = 500000000.0
        current_td = 0.0143
        cap_td = 0.015

    return OptimizedCalculator(
        cov_matrix=cov_matrix,
        eth_weight=benchmark_weights['eth'],
        sol_weight=benchmark_weights['sol'],
        redemption_sizes=redemption_sizes,
        redemption_probs=redemption_probs,
        lambda_r=redemption_dist['lambda'],
        eth_yield=yield_params['eth_yield'],
        sol_yield=yield_params['sol_yield'],
        eth_baseline=yield_params['eth_baseline'],
        sol_baseline=yield_params['sol_baseline'],
        d_eth=unbonding_days['eth'],
        d_sol=unbonding_days['sol'],
        nav=nav,
        current_td=current_td,
        cap_td=cap_td,
    )
