"""
ETH Overweight Sensitivity Analysis
===================================

Generates comprehensive sensitivity tables showing portfolio behavior under
various redemption and staking scenarios. Builds upon the v4 framework.

Tables generated:
1. ETH overweight vs redemption/staking levels
2. Optimal active weights for different overweights  
3. Key metrics sensitivity to staking percentage
4. Portfolio yield from ETH staking
"""

from __future__ import annotations
from typing import List, Tuple
import numpy as np
import pandas as pd

# Import shared components from v4
from core.optimal_eth_over_te_dynamic import (
    MarketConfig, StakingConfig, Episode, EpisodicAnalyzer,
    CovarianceBuilder, ActiveWeightOptimizer,
    RedemptionPattern
)


# ---------- Sensitivity Analysis Functions ------------------------------- #

class SensitivityAnalyzer:
    """Generates sensitivity analysis tables"""
    
    def __init__(self, config: MarketConfig):
        self.config = config
        self.cov_builder = CovarianceBuilder(config)
    
    def delta_eth_sensitivity(self, 
                             redemption_range: Tuple[float, float, float],
                             staking_range: Tuple[float, float, float]) -> pd.DataFrame:
        """
        Table 1: ETH overweight needed for various scenarios
        
        Args:
            redemption_range: (start, stop, step) for redemption percentages
            staking_range: (start, stop, step) for staking percentages
            
        Returns:
            DataFrame with staking % as rows, redemption % as columns
        """
        redemptions = np.arange(*redemption_range)
        stakings = np.arange(*staking_range)
        
        # Calculate delta_eth for each combination
        data = []
        for staking in stakings:
            row = []
            for redemption in redemptions:
                episode = Episode.from_redemption(
                    redemption, 10, self.config.eth_weight, staking
                )
                row.append(episode.delta_eth)
            data.append(row)
        
        return pd.DataFrame(
            data,
            index=[f"{s:.0%} staked" for s in stakings],
            columns=[f"{r:.0%}" for r in redemptions]
        )
    
    def active_weights_sensitivity(self,
                                  delta_range: Tuple[float, float, float],
                                  staking_pct: float = 0.8) -> pd.DataFrame:
        """
        Table 2/3: Optimal active weights for various ETH overweights
        
        Args:
            delta_range: (start, stop, step) for delta_eth values
            staking_pct: Assumed staking percentage for redemption mapping
            
        Returns:
            DataFrame with delta_eth levels and corresponding active weights
        """
        optimizer = ActiveWeightOptimizer(self.cov_builder.matrix)
        delta_values = np.arange(*delta_range)
        
        data = []
        for delta_eth in delta_values:
            # Calculate optimal weights
            active = optimizer.optimize(delta_eth)
            
            # Find corresponding redemption
            redemption = self._inverse_redemption(delta_eth, staking_pct)
            
            # Build row
            row = {
                'Delta ETH': f"{delta_eth:.2%}",
                'Redemption %': f"{redemption:.1%}"
            }
            for asset, weight in zip(self.config.assets, active):
                row[asset] = f"{weight:+.4f}"
            
            data.append(row)
        
        return pd.DataFrame(data)
    
    def _inverse_redemption(self, delta_eth: float, staking_pct: float) -> float:
        """Calculate redemption percentage that produces given delta_eth"""
        if delta_eth <= 0:
            return 0.0
        
        free_eth = self.config.eth_weight * (1 - staking_pct)
        return (delta_eth + free_eth) / self.config.eth_weight
    
    def metrics_by_staking(self,
                          schedule: List[RedemptionPattern],
                          staking_range: Tuple[float, float, float],
                          base_yield: float = 0.05,
                          baseline_staking: float = 0.7) -> pd.DataFrame:
        """
        Table 4: Key metrics sensitivity to staking percentage
        
        Args:
            schedule: Redemption patterns to analyze
            staking_range: (start, stop, step) for staking percentages
            base_yield: Annual staking yield
            baseline_staking: Baseline staking level for comparison
            
        Returns:
            DataFrame with metrics for each staking level
        """
        stakings = np.arange(*staking_range)
        data = []
        
        for staking_pct in stakings:
            # Run analysis
            staking_cfg = StakingConfig(
                eth_staking_pct=staking_pct, 
                annual_yield=base_yield,
                eth_weight=self.config.eth_weight,
                baseline_staking=baseline_staking
            )
            analyzer = EpisodicAnalyzer(self.config, staking_cfg)
            results = analyzer.analyze_schedule(schedule)
            
            # Build row using fields from PortfolioResults
            row = {
                '% ETH Staked': f"{staking_pct:.0%}",
                'Total Annual TE': f"{results.total_annual_te:.2%}",
                'Overweight Benefits': f"{results.staking_benefits:.4%}",
                'Extra Staking Benefits': f"{results.extra_staking_benefit:.4%}",
                'Expected Shortfall': f"{results.expected_shortfall:.4%}",
                'Net (Overweight)': f"{results.net_overweight:+.4%}",
                'Total Net Benefit': f"{results.net_benefit:+.4%}"
            }
            data.append(row)
        
        return pd.DataFrame(data)
    
    def portfolio_yield_table(self,
                             staking_range: Tuple[float, float, float],
                             yield_scenarios: List[float]) -> pd.DataFrame:
        """
        Table 5: Portfolio yield from ETH staking
        
        Args:
            staking_range: (start, stop, step) for staking percentages
            yield_scenarios: List of annual yield rates to consider
            
        Returns:
            DataFrame with portfolio yields
        """
        stakings = np.arange(*staking_range)
        data = []
        
        for staking_pct in stakings:
            row = {'% ETH Staked': f"{staking_pct:.0%}"}
            
            for yield_rate in yield_scenarios:
                portfolio_yield = self.config.eth_weight * staking_pct * yield_rate
                row[f'{yield_rate:.0%} Yield'] = f"{portfolio_yield:.3%}"
            
            data.append(row)
        
        return pd.DataFrame(data)


# ---------- Report Generation -------------------------------------------- #

class SensitivityReporter:
    """Formats and displays sensitivity analysis results"""
    
    def __init__(self, config: MarketConfig):
        self.config = config
        self.analyzer = SensitivityAnalyzer(config)
    
    def generate_all_tables(self):
        """Generate and display all sensitivity tables"""
        
        # Table 1: Delta ETH sensitivity
        print("\n" + "="*80)
        print("TABLE 1: ETH Overweight (delta_eth) Sensitivity Analysis")
        print("="*80)
        print(f"ETH Benchmark Weight: {self.config.eth_weight:.2%}")
        print("\nRows: ETH Staking Percentage")
        print("Columns: NAV Redemption Percentage")
        print("-"*80)
        
        df1 = self.analyzer.delta_eth_sensitivity(
            redemption_range=(0.05, 0.50, 0.05),
            staking_range=(0.70, 1.0, 0.10)
        )
        print(df1.map(lambda x: f"{x:.3%}").to_string())
        
        # Table 2: Active weights at 90% staking
        self._print_active_weights(0.90, table_num=2)
        
        # Table 3: Active weights at 100% staking
        self._print_active_weights(1.00, table_num=3)
        
        # Table 4: Metrics sensitivity
        self._print_metrics_sensitivity()
        
        # Table 5: Portfolio yields
        self._print_portfolio_yields()
        
        # Summary insights
        self._print_insights()
    
    def _print_active_weights(self, staking_pct: float, table_num: int):
        """Display active weights table"""
        print("\n" + "="*80)
        print(f"TABLE {table_num}: Optimal Active Weights for Various ETH Overweights")
        print("="*80)
        print(f"Assuming {staking_pct:.0%} ETH staking for redemption mapping")
        print("-"*80)
        
        df = self.analyzer.active_weights_sensitivity(
            delta_range=(0.005, 0.085, 0.005),
            staking_pct=staking_pct
        )
        print(df.to_string(index=False))
        
        # Weight ranges summary
        print("\n" + "-"*80)
        print("ACTIVE WEIGHT RANGES:")
        print("-"*80)
        
        # Calculate ranges for each asset
        optimizer = ActiveWeightOptimizer(self.analyzer.cov_builder.matrix)
        for i, asset in enumerate(self.config.assets):
            weights = []
            for delta in np.arange(0.005, 0.085, 0.005):
                active = optimizer.optimize(delta)
                weights.append(active[i])
            
            weight_range = max(weights) - min(weights)
            if weight_range > 1e-6:
                print(f"{asset}: {min(weights):+.4f} to {max(weights):+.4f}")
    
    def _print_metrics_sensitivity(self):
        """Display metrics sensitivity table"""
        schedule = [
            (0.05, 12, 10),
            (0.10, 3, 10),
            (0.20, 2, 10),
            (0.30, 1, 10),
        ]
        
        print("\n" + "="*80)
        print("TABLE 4: Key Metrics Sensitivity to ETH Staking Percentage")
        print("="*80)
        print("Redemption schedule: 5% (12x), 10% (3x), 20% (2x), 30% (1x)")
        print("Staking Yield: 5% annual, Baseline: 70%")
        print("-"*80)
        
        df = self.analyzer.metrics_by_staking(
            schedule=schedule,
            staking_range=(0.70, 1.0, 0.10),
            base_yield=0.05,
            baseline_staking=0.70
        )
        print(df.to_string(index=False))
        
        print("\n" + "-"*80)
        print("INSIGHTS:")
        print("- Extra staking benefits: from staking above 70% baseline")
        print("- Total net benefit includes all value sources")
        print("- Higher staking → higher tracking error but also higher benefits")
    
    def _print_portfolio_yields(self):
        """Display portfolio yield table"""
        print("\n" + "="*80)
        print("TABLE 5: Expected Portfolio Annual Yield from ETH Staking")
        print("="*80)
        print(f"ETH Benchmark Weight: {self.config.eth_weight:.2%}")
        print("Portfolio yield = ETH weight × % staked × staking yield")
        print("-"*80)
        
        df = self.analyzer.portfolio_yield_table(
            staking_range=(0.70, 1.0, 0.10),
            yield_scenarios=[0.03, 0.05, 0.08]
        )
        print(df.to_string(index=False))
        
        print("\n" + "-"*80)
        print("NOTE: Portfolio yields reflect ETH's 10.49% benchmark weight")
        print("Maximum yield (100% staked, 8% rate): 0.839% portfolio return")
    
    def _print_insights(self):
        """Display summary insights"""
        print("\n" + "="*80)
        print("KEY INSIGHTS:")
        print("="*80)
        print("1. ETH overweight increases linearly with redemptions above free ETH")
        print("2. Risk-minimizing weights primarily underweight BTC")
        print("3. Higher staking enables more yield but increases tracking error")
        print("4. Net benefits can remain positive even with higher tracking risk")
        print("5. Portfolio yields are modest due to ETH's 10.49% weight")


# ---------- Main Entry Point --------------------------------------------- #

def main():
    """Run comprehensive sensitivity analysis"""
    print("\nETH OVERWEIGHT SENSITIVITY ANALYSIS")
    print("Based on NCI-US Index Tracking")
    
    # Initialize with market configuration
    config = MarketConfig()
    reporter = SensitivityReporter(config)
    
    # Generate all tables and insights
    reporter.generate_all_tables()


if __name__ == "__main__":
    main()