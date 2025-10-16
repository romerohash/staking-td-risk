"""
Warmup script to pre-compile Numba functions during container startup
===================================================================

This script triggers JIT compilation of all Numba functions with representative
data to eliminate cold start latency in production.
"""

import numpy as np
import time
from core.optimized_calculator import (
    compute_k_components_numba,
    calculate_tracking_error_vectorized,
    calculate_net_benefits_vectorized,
)


def warmup_numba_functions():
    """Pre-compile all Numba functions with representative data"""
    print('Starting Numba warmup...')
    start_time = time.time()

    # Create representative data matching production shapes
    n_assets = 6
    cov_matrix = np.eye(n_assets, dtype=np.float64) * 0.01

    # Warmup compute_k_components_numba
    print('  Warming up k-components calculation...')
    k_eth_eth, k_sol_sol, k_eth_sol = compute_k_components_numba(
        cov_matrix, eth_weight=0.1049, sol_weight=0.0387
    )

    # Warmup tracking error calculation with various sizes
    print('  Warming up tracking error calculation...')

    # Small batch (single calculation)
    staking_levels_eth = np.array([0.90], dtype=np.float64)
    staking_levels_sol = np.array([0.90], dtype=np.float64)
    redemption_sizes = np.array([0.05, 0.10, 0.20, 0.30], dtype=np.float64)
    redemption_probs = np.array([0.67, 0.17, 0.11, 0.05], dtype=np.float64)

    calculate_tracking_error_vectorized(
        staking_levels_eth,
        staking_levels_sol,
        k_eth_eth,
        k_sol_sol,
        k_eth_sol,
        redemption_sizes,
        redemption_probs,
        lambda_r=6.5,
        d_eth=10,
        d_sol=2,
    )

    # Large batch (sensitivity analysis size)
    staking_levels_large = np.linspace(0.70, 1.0, 31, dtype=np.float64)
    calculate_tracking_error_vectorized(
        staking_levels_large,
        staking_levels_large,
        k_eth_eth,
        k_sol_sol,
        k_eth_sol,
        redemption_sizes,
        redemption_probs,
        lambda_r=6.5,
        d_eth=10,
        d_sol=2,
    )

    # Warmup net benefits calculation
    print('  Warming up net benefits calculation...')
    tracking_errors = np.array([0.01, 0.02, 0.03], dtype=np.float64)
    staking_levels = np.array([0.80, 0.90, 0.95], dtype=np.float64)

    calculate_net_benefits_vectorized(
        tracking_errors,
        staking_levels,
        staking_levels,
        eth_weight=0.1049,
        sol_weight=0.0387,
        eth_yield=0.035,
        sol_yield=0.06,
        eth_baseline=0.0,
        sol_baseline=0.0,
        redemption_sizes=redemption_sizes,
        redemption_probs=redemption_probs,
        lambda_r=6.5,
        d_eth=10,
        d_sol=2,
        current_td=0.002,
        cap_td=0.007,
    )

    elapsed = time.time() - start_time
    print(f'✅ Numba warmup completed in {elapsed:.2f}s')

    return True


if __name__ == '__main__':
    warmup_numba_functions()
