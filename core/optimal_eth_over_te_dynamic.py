"""
Enhanced Episodic ETH-tilt Tracking Error and Risk Calculator
===========================================================

Analyzes ETF portfolio risk when ETH must be overweighted due to staking illiquidity.
Implements tracking error minimization with staking benefit calculations.

Key features:
- Redemption-driven ETH overweight calculations
- Risk-minimizing portfolio adjustments via Lagrange optimization
- Episode-based tracking error aggregation
- Integrated staking yield benefits analysis
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, NamedTuple
from math import sqrt, pi
import numpy as np
from numpy.typing import NDArray


# Type aliases for clarity
Weights = NDArray[np.float64]
CovMatrix = NDArray[np.float64]
RedemptionPattern = Tuple[float, int, int]  # (redemption_pct, count, duration_days)


# ---------- Configuration ------------------------------------------------ #

@dataclass(frozen=True)
class MarketConfig:
    """Immutable market configuration for NCI-US index tracking"""
    # Asset identifiers
    assets: Tuple[str, ...] = ('BTC', 'ETH', 'XRP', 'SOL', 'ADA', 'XLM')
    
    # Benchmark weights (must sum to 1.0)
    benchmark_weights: Weights = field(
        default_factory=lambda: np.array([0.7869, 0.1049, 0.0549, 0.0387, 0.0119, 0.0027])
    )
    
    # Daily volatilities (as decimals, not percentages)
    daily_volatilities: Weights = field(
        default_factory=lambda: np.array([0.039, 0.048, 0.053, 0.071, 0.055, 0.051])
    )
    
    # Correlation parameters
    rho_btc_eth: float = 0.70
    rho_within_other: float = 0.60
    rho_cross: float = 0.60
    
    # Trading days per year
    trading_days: int = 252
    
    @property
    def eth_index(self) -> int:
        """ETH position in arrays"""
        return 1
    
    @property
    def eth_weight(self) -> float:
        """ETH benchmark weight"""
        return float(self.benchmark_weights[self.eth_index])
    
    @property
    def annual_volatilities(self) -> Weights:
        """Convert daily to annual volatilities"""
        return self.daily_volatilities * sqrt(self.trading_days)


@dataclass(frozen=True)
class StakingConfig:
    """Staking strategy configuration"""
    eth_staking_pct: float = 0.8  # Fraction of ETH staked
    annual_yield: float = 0.04     # Annual staking yield
    eth_weight: float = 0.1049     # ETH benchmark weight
    baseline_staking: float = 0.7  # Baseline staking level
    
    def __post_init__(self):
        if not 0 <= self.eth_staking_pct <= 1:
            raise ValueError(f"Staking percentage must be in [0,1], got {self.eth_staking_pct}")
        if self.annual_yield < 0:
            raise ValueError(f"Annual yield must be non-negative, got {self.annual_yield}")
        if not 0 <= self.baseline_staking <= 1:
            raise ValueError(f"Baseline staking must be in [0,1], got {self.baseline_staking}")
    
    @property
    def extra_staking_benefit(self) -> float:
        """Calculate annual benefit from staking above baseline"""
        extra_staking = max(0, self.eth_staking_pct - self.baseline_staking)
        return self.eth_weight * extra_staking * self.annual_yield


# ---------- Domain Models ------------------------------------------------ #

@dataclass(frozen=True)
class Episode:
    """Single redemption episode with calculated ETH overweight"""
    redemption_pct: float    # NAV redemption percentage
    duration_days: int       # Episode duration  
    delta_eth: float        # Required ETH overweight
    staking_pct: float      # ETH staking percentage
    
    @classmethod
    def from_redemption(cls, redemption_pct: float, duration_days: int,
                       eth_weight: float, staking_pct: float) -> Episode:
        """
        Calculate required ETH overweight from redemption parameters.
        
        When ETH is staked, redemptions deplete liquid assets disproportionately.
        To maintain target weights post-redemption, ETH must be overweighted.
        
        Args:
            redemption_pct: Fraction of NAV redeemed
            duration_days: Episode duration in trading days
            eth_weight: ETH's benchmark weight
            staking_pct: Fraction of ETH staked (illiquid)
            
        Returns:
            Episode with calculated delta_eth
        """
        eth_share = redemption_pct * eth_weight
        free_eth = eth_weight * (1 - staking_pct)
        delta_eth = max(0, eth_share - free_eth)
        
        return cls(redemption_pct, duration_days, delta_eth, staking_pct)


class EpisodeMetrics(NamedTuple):
    """Risk and return metrics for a single episode"""
    episode: Episode
    active_weights: Weights
    daily_variance: float
    te_contribution: float  # Contribution to annual TE
    staking_benefit: float  # Staking yield earned
    expected_shortfall: float  # Expected negative tracking


@dataclass
class PortfolioResults:
    """Aggregated portfolio risk-return metrics"""
    episodes: List[Episode]
    metrics: List[EpisodeMetrics]
    total_annual_te: float
    staking_benefits: float  # Overweight benefits
    expected_shortfall: float
    net_benefit: float  # Total net benefit
    extra_staking_benefit: float = 0.0  # Benefits from staking above baseline
    net_overweight: float = 0.0  # Net (Overweight) = overweight benefits + shortfall


# ---------- Core Mathematics --------------------------------------------- #

class CovarianceBuilder:
    """Builds covariance matrices with specified correlation structure"""
    
    def __init__(self, config: MarketConfig):
        self.config = config
        self._cov_matrix: Optional[CovMatrix] = None
    
    @property
    def matrix(self) -> CovMatrix:
        """Lazy-load covariance matrix"""
        if self._cov_matrix is None:
            self._cov_matrix = self._build()
        return self._cov_matrix
    
    def _build(self) -> CovMatrix:
        """Construct 6x6 covariance matrix"""
        n = len(self.config.assets)
        vols = self.config.daily_volatilities
        
        # Start with variance diagonal
        cov = np.diag(vols ** 2)
        
        # BTC-ETH correlation
        cov[0, 1] = cov[1, 0] = (self.config.rho_btc_eth * 
                                 vols[0] * vols[1])
        
        # Within other assets (indices 2-5)
        for i in range(2, n):
            for j in range(i + 1, n):
                cov[i, j] = cov[j, i] = (self.config.rho_within_other * 
                                        vols[i] * vols[j])
        
        # Cross correlations
        for i in (0, 1):
            for j in range(2, n):
                cov[i, j] = cov[j, i] = (self.config.rho_cross * 
                                        vols[i] * vols[j])
        
        return cov


class ActiveWeightOptimizer:
    """Calculates risk-minimizing active weights via Lagrange multipliers"""
    
    def __init__(self, cov_matrix: CovMatrix):
        self.cov = cov_matrix
        self.inv_cov = np.linalg.inv(cov_matrix)
        self.n_assets = len(cov_matrix)
    
    def optimize(self, delta_eth: float) -> Weights:
        """
        Find active weights minimizing tracking variance.
        
        Constraints:
        - Sum of active weights = 0
        - ETH active weight = delta_eth
        
        Args:
            delta_eth: Required ETH overweight
            
        Returns:
            Optimal active weight vector
        """
        # Constraint matrix: [sum-to-zero; ETH-specific]
        C = np.vstack([
            np.ones(self.n_assets),
            np.eye(self.n_assets)[1]  # ETH is index 1
        ])
        c = np.array([0.0, delta_eth])
        
        # Solve: λ = (C Σ^(-1) C')^(-1) c
        lambda_opt = np.linalg.solve(C @ self.inv_cov @ C.T, c)
        
        # Optimal weights: a* = Σ^(-1) C' λ
        return self.inv_cov @ C.T @ lambda_opt


# ---------- Analysis Engine ---------------------------------------------- #

class EpisodicAnalyzer:
    """Analyzes portfolio risk/return for episodic redemption strategies"""
    
    def __init__(self, market: MarketConfig, staking: StakingConfig):
        self.market = market
        self.staking = staking
        self.cov_builder = CovarianceBuilder(market)
        self.optimizer = ActiveWeightOptimizer(self.cov_builder.matrix)
    
    def analyze_schedule(self, patterns: List[RedemptionPattern],
                        staking_override: Optional[float] = None) -> PortfolioResults:
        """
        Full pipeline: redemptions → episodes → metrics → aggregation
        
        Args:
            patterns: List of (redemption_pct, count, duration_days)
            staking_override: Override default staking percentage
            
        Returns:
            Complete risk-return analysis
        """
        staking_pct = staking_override or self.staking.eth_staking_pct
        
        # Generate episodes
        episodes = self._create_episodes(patterns, staking_pct)
        
        # Calculate metrics
        metrics = [self._analyze_episode(ep) for ep in episodes]
        
        # Aggregate results
        return self._aggregate_metrics(episodes, metrics)
    
    def _create_episodes(self, patterns: List[RedemptionPattern],
                        staking_pct: float) -> List[Episode]:
        """Convert redemption patterns to episodes"""
        episodes = []
        for redemption, count, duration in patterns:
            for _ in range(count):
                ep = Episode.from_redemption(
                    redemption, duration, 
                    self.market.eth_weight, staking_pct
                )
                episodes.append(ep)
        return episodes
    
    def _analyze_episode(self, episode: Episode) -> EpisodeMetrics:
        """Calculate risk and return metrics for one episode"""
        # Optimize active weights
        active = self.optimizer.optimize(episode.delta_eth)
        
        # Risk calculations
        daily_var = active @ self.cov_builder.matrix @ active
        te_contrib = sqrt(episode.duration_days * daily_var)
        
        # Expected shortfall (half-normal distribution)
        annual_te = sqrt(daily_var * self.market.trading_days)
        shortfall = -annual_te * sqrt(2/pi) * 0.5
        
        # Return calculation
        time_frac = episode.duration_days / 365
        benefit = episode.delta_eth * self.staking.annual_yield * time_frac
        
        return EpisodeMetrics(
            episode, active, daily_var, 
            te_contrib, benefit, shortfall
        )
    
    def _aggregate_metrics(self, episodes: List[Episode],
                          metrics: List[EpisodeMetrics]) -> PortfolioResults:
        """Aggregate episode-level metrics to portfolio level"""
        # Total tracking error (sum of variance-days)
        total_var_days = sum(m.daily_variance * m.episode.duration_days 
                            for m in metrics)
        total_te = sqrt(total_var_days)
        
        # Aggregate overweight benefits and costs
        total_overweight_benefits = sum(m.staking_benefit for m in metrics)
        total_shortfall = -total_te * sqrt(2/pi) * 0.5
        net_overweight = total_overweight_benefits + total_shortfall
        
        # Get extra staking benefit from StakingConfig
        extra_staking_benefit = self.staking.extra_staking_benefit
        
        # Total net benefit includes both sources
        total_net_benefit = net_overweight + extra_staking_benefit
        
        return PortfolioResults(
            episodes=episodes,
            metrics=metrics,
            total_annual_te=total_te,
            staking_benefits=total_overweight_benefits,
            expected_shortfall=total_shortfall,
            net_benefit=total_net_benefit,
            extra_staking_benefit=extra_staking_benefit,
            net_overweight=net_overweight
        )


# ---------- Reporting ---------------------------------------------------- #

class ReportGenerator:
    """Generates formatted analysis reports"""
    
    def __init__(self, config: MarketConfig):
        self.config = config
    
    def portfolio_summary(self, results: PortfolioResults) -> str:
        """Generate executive summary"""
        lines = [
            "=" * 60,
            "PORTFOLIO RISK-RETURN SUMMARY",
            "=" * 60,
            f"Total Annual TE: {results.total_annual_te:.2%}",
            f"Overweight Benefits: {results.staking_benefits:.4%}",
            f"Extra Staking Benefits: {results.extra_staking_benefit:.4%}",
            f"Expected Shortfall: {results.expected_shortfall:.4%}",
            f"Net (Overweight): {results.net_overweight:+.4%}",
            f"Total Net Benefit: {results.net_benefit:+.4%}",
            "",
            "Decision: " + ("✓ Positive net benefit" if results.net_benefit > 0 
                          else "✗ Negative net benefit")
        ]
        return "\n".join(lines)
    
    def episode_details(self, results: PortfolioResults, 
                       max_episodes: int = 5) -> str:
        """Generate detailed episode breakdown"""
        lines = ["", "EPISODE DETAILS:", "-" * 40]
        
        for i, metric in enumerate(results.metrics[:max_episodes]):
            ep = metric.episode
            lines.append(
                f"Episode {i+1}: {ep.redemption_pct:.1%} redemption, "
                f"{ep.staking_pct:.0%} staked, δETH={ep.delta_eth:.4f}"
            )
            
            # Show active weights for first episode
            if i == 0:
                lines.append("  Active weights:")
                for asset, weight in zip(self.config.assets, metric.active_weights):
                    if abs(weight) > 1e-6:
                        lines.append(f"    {asset}: {weight:+.5f}")
        
        if len(results.metrics) > max_episodes:
            lines.append(f"... plus {len(results.metrics) - max_episodes} more")
        
        return "\n".join(lines)


# ---------- Main Demo ---------------------------------------------------- #

def run_staking_analysis():
    """Demonstrate analysis across different staking scenarios"""
    # Initialize configuration
    market = MarketConfig()
    
    # Standard redemption schedule
    schedule: List[RedemptionPattern] = [
        (0.05, 12, 10),  # 5% redemptions
        (0.10, 3, 10),   # 10% redemptions
        (0.20, 2, 10),   # 20% redemptions
        (0.30, 1, 10),   # 30% redemption
    ]
    
    # Test scenarios
    scenarios = [
        (0.0, "No staking"),
        (0.7, "70% staked"),
        (0.8, "80% staked"),
        (0.9, "90% staked"),
        (1.0, "Full staking")
    ]
    
    print("\nSTAKING SCENARIO ANALYSIS")
    print("=" * 80)
    
    for staking_pct, desc in scenarios:
        staking = StakingConfig(
            eth_staking_pct=staking_pct, 
            annual_yield=0.05,  # 5% yield
            eth_weight=market.eth_weight,
            baseline_staking=0.7
        )
        analyzer = EpisodicAnalyzer(market, staking)
        results = analyzer.analyze_schedule(schedule)
        
        reporter = ReportGenerator(market)
        print(f"\n{desc}:")
        print(reporter.portfolio_summary(results))
        
        if staking_pct == 0.8:  # Show details for one scenario
            print(reporter.episode_details(results))


def main():
    """Entry point with asset overview"""
    config = MarketConfig()
    
    print("\nNCI-US INDEX COMPOSITION")
    print("-" * 60)
    for asset, weight, vol in zip(config.assets, 
                                  config.benchmark_weights,
                                  config.annual_volatilities):
        print(f"{asset:4s}: {weight:6.2%} (annual vol: {vol*100:5.1f}%)")
    
    run_staking_analysis()


if __name__ == "__main__":
    main()