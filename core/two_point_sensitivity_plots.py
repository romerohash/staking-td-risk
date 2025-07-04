"""
Generate sensitivity analysis plots for Two-Point Distribution
"""

import numpy as np
import matplotlib.pyplot as plt
from core.two_point_distribution_analysis import (
    TwoPointDistribution, calculate_base_k, analytical_te,
    sensitivity_analysis_staking, sensitivity_analysis_distribution
)
from core.optimal_eth_over_te_dynamic import MarketConfig


def plot_staking_sensitivity():
    """Plot TE vs staking percentage for different distributions"""
    # Setup
    market = MarketConfig()
    base_k = calculate_base_k(market)
    lambda_redemptions = 18
    episode_days = 10
    
    # Different distribution scenarios
    scenarios = [
        ("Conservative: 5% (80%), 20% (20%)", TwoPointDistribution(0.05, 0.20, 0.8)),
        ("Moderate: 5% (80%), 30% (20%)", TwoPointDistribution(0.05, 0.30, 0.8)),
        ("Aggressive: 2% (90%), 50% (10%)", TwoPointDistribution(0.02, 0.50, 0.9)),
        ("Balanced: 10% (50%), 20% (50%)", TwoPointDistribution(0.10, 0.20, 0.5)),
    ]
    
    plt.figure(figsize=(10, 6))
    
    for label, dist in scenarios:
        staking_pcts, te_values = sensitivity_analysis_staking(
            base_k, lambda_redemptions, episode_days, dist, (0, 1), 50
        )
        te_pcts = [te * 100 for te in te_values]  # Convert to percentage
        plt.plot(staking_pcts, te_pcts, label=label, linewidth=2)
    
    # Add threshold markers
    for s in [0.7, 0.8, 0.9]:
        plt.axvline(s, color='gray', linestyle='--', alpha=0.3)
        plt.text(s, plt.ylim()[1]*0.95, f'{s:.0%}', ha='center', va='top', fontsize=8)
    
    plt.xlabel('ETH Staking Percentage', fontsize=12)
    plt.ylabel('Annual Tracking Error (%)', fontsize=12)
    plt.title('Tracking Error Sensitivity to Staking Level\n(Two-Point Redemption Distributions)', fontsize=14)
    plt.legend(loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.xlim(0, 1)
    plt.ylim(bottom=0)
    
    plt.tight_layout()
    plt.savefig('images/staking_sensitivity_two_point.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    print("Created: staking_sensitivity_two_point.png")


def plot_distribution_heatmap():
    """Plot TE heatmap for different r1, r2 combinations"""
    # Setup
    market = MarketConfig()
    base_k = calculate_base_k(market)
    lambda_redemptions = 18
    episode_days = 10
    staking_pct = 0.8  # 80% staking
    
    # Create figure with subplots for different p values
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    p_values = [0.9, 0.8, 0.5]  # High frequency of r1, moderate, equal
    
    for idx, (ax, p) in enumerate(zip(axes, p_values)):
        result = sensitivity_analysis_distribution(
            base_k, lambda_redemptions, episode_days, staking_pct,
            r1_range=(0, 0.3), r2_range=(0, 0.5), p=p
        )
        
        # Convert to percentage
        te_grid_pct = result['te_grid'] * 100
        
        # Create heatmap
        im = ax.imshow(te_grid_pct, origin='lower', aspect='auto', 
                      cmap='YlOrRd', interpolation='bilinear')
        
        # Set labels
        ax.set_xlabel('r2 (Large Redemption)', fontsize=10)
        ax.set_ylabel('r1 (Small Redemption)', fontsize=10)
        ax.set_title(f'p = {p:.1f}\n(P(r1) = {p:.0%})', fontsize=12)
        
        # Set tick labels
        n_ticks = 6
        r1_ticks = np.linspace(0, len(result['r1_values'])-1, n_ticks).astype(int)
        r2_ticks = np.linspace(0, len(result['r2_values'])-1, n_ticks).astype(int)
        
        ax.set_xticks(r2_ticks)
        ax.set_xticklabels([f'{result["r2_values"][i]:.0%}' for i in r2_ticks])
        ax.set_yticks(r1_ticks)
        ax.set_yticklabels([f'{result["r1_values"][i]:.0%}' for i in r1_ticks])
        
        # Add contour lines
        contour = ax.contour(te_grid_pct, levels=[0.1, 0.2, 0.3, 0.4, 0.5], 
                           colors='black', alpha=0.4, linewidths=1)
        ax.clabel(contour, inline=True, fontsize=8, fmt='%.1f%%')
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Annual TE (%)', fontsize=9)
    
    fig.suptitle(f'Tracking Error Heatmaps for Two-Point Distributions\n'
                 f'(80% ETH Staked, λ={lambda_redemptions}, d={episode_days} days)', 
                 fontsize=14)
    
    plt.tight_layout()
    plt.savefig('images/distribution_heatmap_two_point.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    print("Created: distribution_heatmap_two_point.png")


def plot_threshold_effects():
    """Visualize how threshold affects contribution to TE"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Distribution parameters
    r1, r2, p = 0.05, 0.30, 0.8
    dist = TwoPointDistribution(r1, r2, p)
    
    # Range of thresholds
    thresholds = np.linspace(0, 0.5, 100)
    contributions = []
    
    for tau in thresholds:
        e_squared = dist.expected_squared_excess(tau)
        contributions.append(e_squared)
    
    # Convert threshold to staking percentage
    staking_pcts = 1 - thresholds
    
    # Plot 1: E[(R-τ)²₊] vs threshold
    ax1.plot(thresholds, contributions, 'b-', linewidth=2)
    ax1.axvline(r1, color='green', linestyle='--', alpha=0.7, label=f'r1={r1:.0%}')
    ax1.axvline(r2, color='red', linestyle='--', alpha=0.7, label=f'r2={r2:.0%}')
    ax1.fill_between(thresholds, 0, contributions, alpha=0.3)
    
    ax1.set_xlabel('Threshold τ = 1 - staking_pct', fontsize=12)
    ax1.set_ylabel('E[(R - τ)²₊]', fontsize=12)
    ax1.set_title('Expected Squared Excess vs Threshold', fontsize=14)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Component contributions
    staking_levels = [0.5, 0.7, 0.8, 0.9, 0.95]
    contributions_r1 = []
    contributions_r2 = []
    
    for s in staking_levels:
        tau = 1 - s
        c1 = p * max(0, r1 - tau)**2
        c2 = (1-p) * max(0, r2 - tau)**2
        contributions_r1.append(c1)
        contributions_r2.append(c2)
    
    x = np.arange(len(staking_levels))
    width = 0.35
    
    bars1 = ax2.bar(x - width/2, contributions_r1, width, label=f'r1={r1:.0%} (p={p:.1f})')
    bars2 = ax2.bar(x + width/2, contributions_r2, width, label=f'r2={r2:.0%} (p={1-p:.1f})')
    
    ax2.set_xlabel('Staking Percentage', fontsize=12)
    ax2.set_ylabel('Contribution to E[(R - τ)²₊]', fontsize=12)
    ax2.set_title('Individual Redemption Contributions', fontsize=14)
    ax2.set_xticks(x)
    ax2.set_xticklabels([f'{s:.0%}' for s in staking_levels])
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            if height > 0.0001:
                ax2.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.4f}', ha='center', va='bottom', fontsize=8)
    
    plt.suptitle(f'Threshold Effects for Two-Point Distribution\n'
                 f'({r1:.0%} with p={p}, {r2:.0%} with p={1-p})', fontsize=14)
    
    plt.tight_layout()
    plt.savefig('images/threshold_effects_two_point.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    print("Created: threshold_effects_two_point.png")


def main():
    """Generate all sensitivity analysis plots"""
    print("Generating Two-Point Distribution sensitivity analysis plots...")
    
    plot_staking_sensitivity()
    plot_distribution_heatmap()
    plot_threshold_effects()
    
    print("\nAll plots generated successfully!")
    print("\nKey insights from the analysis:")
    print("1. TE increases non-linearly with staking percentage")
    print("2. Distribution shape dramatically affects TE at high staking levels")
    print("3. Threshold effects create 'safe zones' where small redemptions don't impact TE")
    print("4. The probability weight (p) affects overall TE magnitude")


if __name__ == "__main__":
    main()