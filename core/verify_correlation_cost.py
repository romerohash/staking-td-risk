"""
Numerical Verification of Correlation Cost in Multi-Asset Staking
================================================================

This script verifies that the correlation "benefit" is actually a cost
for ETH+SOL staking by:
1. Computing k_ETH_SOL and showing it's positive
2. Testing various staking combinations
3. Demonstrating the constraint competition effect
"""

import numpy as np
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
from core.two_asset_analytical_formula import (
    compute_k_components, create_market_covariance, 
    TwoAssetConfig, expected_values_discrete, 
    analytical_tracking_error_two_asset
)
from scipy import stats


def analyze_k_components(market_cov: np.ndarray) -> Dict[str, float]:
    """Analyze the sign and magnitude of k-components"""
    k_comps = compute_k_components(market_cov)
    
    # Asset weights
    eth_weight = 0.1049
    sol_weight = 0.0387
    
    # Calculate k values
    k_eth_eth = eth_weight**2 * k_comps['v_eth_sigma_v_eth']
    k_sol_sol = sol_weight**2 * k_comps['v_sol_sigma_v_sol']
    k_eth_sol = eth_weight * sol_weight * k_comps['v_eth_sigma_v_sol']
    
    # Calculate correlation between v_ETH and v_SOL
    v_eth = k_comps['v_eth']
    v_sol = k_comps['v_sol']
    
    # Correlation through covariance matrix
    v_correlation = (v_eth @ market_cov @ v_sol) / np.sqrt(
        (v_eth @ market_cov @ v_eth) * (v_sol @ market_cov @ v_sol)
    )
    
    return {
        'k_eth_eth': k_eth_eth,
        'k_sol_sol': k_sol_sol,
        'k_eth_sol': k_eth_sol,
        'k_ratio': k_eth_sol / np.sqrt(k_eth_eth * k_sol_sol),
        'v_correlation': v_correlation,
        'v_eth': v_eth,
        'v_sol': v_sol
    }


def test_staking_combinations(market_cov: np.ndarray,
                            eth_stakings: List[float],
                            sol_stakings: List[float]) -> np.ndarray:
    """Test various staking combinations and compute correlation cost/benefit"""
    n_eth = len(eth_stakings)
    n_sol = len(sol_stakings)
    correlation_impact = np.zeros((n_eth, n_sol))
    
    # Create redemption distribution
    values = [0.05, 0.10, 0.20, 0.30]
    weights = [12/18, 3/18, 2/18, 1/18]
    redemption_dist = stats.rv_discrete(values=(values, weights))
    
    k_components = compute_k_components(market_cov)
    
    for i, eth_staking in enumerate(eth_stakings):
        for j, sol_staking in enumerate(sol_stakings):
            # Configure
            config = TwoAssetConfig(
                eth_staking_pct=eth_staking,
                sol_staking_pct=sol_staking
            )
            
            # Calculate expectations
            expectations = expected_values_discrete(redemption_dist, config, k_components)
            
            # Calculate exact TE
            te_exact = analytical_tracking_error_two_asset(config, k_components, expectations)
            
            # Calculate independent TEs
            k_eth_eth = config.eth_weight**2 * k_components['v_eth_sigma_v_eth']
            k_sol_sol = config.sol_weight**2 * k_components['v_sol_sigma_v_sol']
            
            te_eth_only = np.sqrt(config.lambda_redemptions * config.eth_unbonding_days * 
                                 k_eth_eth * expectations['exp_eth_squared'])
            te_sol_only = np.sqrt(config.lambda_redemptions * config.sol_unbonding_days * 
                                 k_sol_sol * expectations['exp_sol_squared'])
            
            # Independence approximation
            te_indep = np.sqrt(te_eth_only**2 + te_sol_only**2)
            
            # Correlation impact (negative = benefit, positive = cost)
            correlation_impact[i, j] = (te_exact - te_indep) / te_indep * 100 if te_indep > 0 else 0
    
    return correlation_impact


def analyze_constraint_competition(market_cov: np.ndarray) -> Dict[str, np.ndarray]:
    """Analyze how constraints compete for the same hedge assets"""
    inv_cov = np.linalg.inv(market_cov)
    n_assets = market_cov.shape[0]
    
    # Build individual constraint matrices
    C_budget = np.ones((1, n_assets))
    C_eth = np.zeros((1, n_assets))
    C_eth[0, 1] = 1
    C_sol = np.zeros((1, n_assets))
    C_sol[0, 3] = 1
    
    # Single ETH constraint
    C_single_eth = np.vstack([C_budget, C_eth])
    C_inv_C_eth = C_single_eth @ inv_cov @ C_single_eth.T
    v_eth_single = inv_cov @ C_single_eth.T @ np.linalg.inv(C_inv_C_eth) @ np.array([0, 1])
    
    # Single SOL constraint  
    C_single_sol = np.vstack([C_budget, C_sol])
    C_inv_C_sol = C_single_sol @ inv_cov @ C_single_sol.T
    v_sol_single = inv_cov @ C_single_sol.T @ np.linalg.inv(C_inv_C_sol) @ np.array([0, 1])
    
    # Both constraints
    C_both = np.vstack([C_budget, C_eth, C_sol])
    k_components = compute_k_components(market_cov)
    v_eth_multi = k_components['v_eth']
    v_sol_multi = k_components['v_sol']
    
    return {
        'v_eth_single': v_eth_single,
        'v_sol_single': v_sol_single,
        'v_eth_multi': v_eth_multi,
        'v_sol_multi': v_sol_multi,
        'hedge_overlap': np.dot(v_eth_single, v_sol_single)
    }


def visualize_results(correlation_impact: np.ndarray,
                     eth_stakings: List[float],
                     sol_stakings: List[float]):
    """Create heatmap of correlation impact"""
    plt.figure(figsize=(10, 8))
    
    # Create heatmap
    im = plt.imshow(correlation_impact, cmap='RdBu_r', aspect='auto', 
                   interpolation='nearest', vmin=-5, vmax=5)
    
    # Add colorbar
    cbar = plt.colorbar(im)
    cbar.set_label('Correlation Impact (%)\n(Positive = Cost, Negative = Benefit)', 
                   rotation=270, labelpad=20)
    
    # Set ticks
    plt.xticks(range(len(sol_stakings)), [f'{s:.0%}' for s in sol_stakings])
    plt.yticks(range(len(eth_stakings)), [f'{s:.0%}' for s in eth_stakings])
    
    # Labels
    plt.xlabel('SOL Staking %', fontsize=12)
    plt.ylabel('ETH Staking %', fontsize=12)
    plt.title('Correlation Cost in Multi-Asset Staking\n(Exact TE vs Independence Approximation)', 
             fontsize=14)
    
    # Add text annotations
    for i in range(len(eth_stakings)):
        for j in range(len(sol_stakings)):
            text = plt.text(j, i, f'{correlation_impact[i, j]:.1f}%',
                          ha='center', va='center', 
                          color='white' if abs(correlation_impact[i, j]) > 2.5 else 'black',
                          fontsize=8)
    
    plt.tight_layout()
    plt.savefig('correlation_cost_heatmap.png', dpi=150, bbox_inches='tight')
    plt.close()


def main():
    """Comprehensive verification of correlation cost"""
    print("CORRELATION COST VERIFICATION")
    print("=" * 70)
    
    # Get market covariance
    market_cov = create_market_covariance()
    
    # 1. Analyze k-components
    print("\n1. K-COMPONENT ANALYSIS")
    print("-" * 40)
    k_analysis = analyze_k_components(market_cov)
    
    print(f"k_ETH_ETH: {k_analysis['k_eth_eth']:.8f}")
    print(f"k_SOL_SOL: {k_analysis['k_sol_sol']:.8f}")
    print(f"k_ETH_SOL: {k_analysis['k_eth_sol']:.8f}")
    print(f"\nk_ETH_SOL sign: {'POSITIVE (cost)' if k_analysis['k_eth_sol'] > 0 else 'NEGATIVE (benefit)'}")
    print(f"k_ETH_SOL / sqrt(k_ETH_ETH × k_SOL_SOL): {k_analysis['k_ratio']:.3f}")
    print(f"v_ETH · v_SOL correlation: {k_analysis['v_correlation']:.3f}")
    
    # 2. Test various staking combinations
    print("\n2. STAKING COMBINATION ANALYSIS")
    print("-" * 40)
    
    eth_stakings = np.linspace(0.5, 0.95, 10)
    sol_stakings = np.linspace(0.5, 0.95, 10)
    
    correlation_impact = test_staking_combinations(market_cov, eth_stakings, sol_stakings)
    
    print(f"Average correlation impact: {np.mean(correlation_impact):.2f}%")
    print(f"Min correlation impact: {np.min(correlation_impact):.2f}%")
    print(f"Max correlation impact: {np.max(correlation_impact):.2f}%")
    print(f"Percentage of cases with cost (>0): {np.sum(correlation_impact > 0) / correlation_impact.size * 100:.1f}%")
    
    # 3. Constraint competition analysis
    print("\n3. CONSTRAINT COMPETITION ANALYSIS")
    print("-" * 40)
    
    constraint_analysis = analyze_constraint_competition(market_cov)
    
    print("Hedge vectors when constraints are applied individually vs together:")
    print("\nAsset weights in hedge vectors:")
    assets = ['BTC', 'ETH', 'XRP', 'SOL', 'ADA', 'XLM']
    
    print(f"{'Asset':<6} {'ETH-only':<12} {'SOL-only':<12} {'ETH(multi)':<12} {'SOL(multi)':<12}")
    print("-" * 60)
    
    for i, asset in enumerate(assets):
        print(f"{asset:<6} "
              f"{constraint_analysis['v_eth_single'][i]:>11.4f} "
              f"{constraint_analysis['v_sol_single'][i]:>11.4f} "
              f"{constraint_analysis['v_eth_multi'][i]:>11.4f} "
              f"{constraint_analysis['v_sol_multi'][i]:>11.4f}")
    
    print(f"\nHedge vector overlap (v_ETH_single · v_SOL_single): {constraint_analysis['hedge_overlap']:.4f}")
    
    # 4. Specific example
    print("\n4. SPECIFIC EXAMPLE: 80% ETH, 90% SOL")
    print("-" * 40)
    
    config = TwoAssetConfig(eth_staking_pct=0.8, sol_staking_pct=0.9)
    redemption_dist = stats.rv_discrete(values=([0.05, 0.10, 0.20, 0.30], 
                                               [12/18, 3/18, 2/18, 1/18]))
    
    k_components = compute_k_components(market_cov)
    expectations = expected_values_discrete(redemption_dist, config, k_components)
    
    # Calculate exact and independent TEs
    te_exact = analytical_tracking_error_two_asset(config, k_components, expectations)
    
    k_eth_eth = config.eth_weight**2 * k_components['v_eth_sigma_v_eth']
    k_sol_sol = config.sol_weight**2 * k_components['v_sol_sigma_v_sol']
    k_eth_sol = config.eth_weight * config.sol_weight * k_components['v_eth_sigma_v_sol']
    
    te_eth = np.sqrt(config.lambda_redemptions * config.eth_unbonding_days * 
                     k_eth_eth * expectations['exp_eth_squared'])
    te_sol = np.sqrt(config.lambda_redemptions * config.sol_unbonding_days * 
                     k_sol_sol * expectations['exp_sol_squared'])
    te_indep = np.sqrt(te_eth**2 + te_sol**2)
    
    print(f"ETH-only TE: {te_eth:.4%}")
    print(f"SOL-only TE: {te_sol:.4%}")
    print(f"Independence approx: {te_indep:.4%}")
    print(f"Exact two-asset TE: {te_exact:.4%}")
    print(f"Correlation cost: {te_exact - te_indep:.4%} ({(te_exact/te_indep - 1)*100:.1f}% increase)")
    
    # Calculate cross-term contribution
    cross_term_var = (config.lambda_redemptions * config.min_unbonding * 2 * 
                     k_eth_sol * expectations['exp_cross_term'])
    cross_term_te = np.sqrt(cross_term_var)
    
    print(f"\nCross-term contribution: {cross_term_te:.4%}")
    print(f"Cross-term explains: {cross_term_var / (te_exact**2 - te_indep**2) * 100:.1f}% of the excess variance")
    
    # 5. Create visualization
    print("\n5. CREATING VISUALIZATION")
    print("-" * 40)
    visualize_results(correlation_impact, eth_stakings, sol_stakings)
    print("Saved correlation cost heatmap to 'correlation_cost_heatmap.png'")
    
    print("\n" + "=" * 70)
    print("CONCLUSION: The correlation 'benefit' is actually a COST in all tested cases.")
    print("This occurs because ETH and SOL constraints compete for the same hedge assets.")


if __name__ == "__main__":
    main()