"""
Request and Response models for the Staking TE Demo API
"""

from typing import List, Optional
from pydantic import BaseModel, Field, validator


class BenchmarkWeights(BaseModel):
    """Benchmark weights for NCI-US index assets"""

    btc: float = Field(0.7869, ge=0, le=1, description='BTC weight')
    eth: float = Field(0.1049, ge=0, le=1, description='ETH weight')
    xrp: float = Field(0.0549, ge=0, le=1, description='XRP weight')
    sol: float = Field(0.0387, ge=0, le=1, description='SOL weight')
    ada: float = Field(0.0119, ge=0, le=1, description='ADA weight')
    xlm: float = Field(0.0027, ge=0, le=1, description='XLM weight')

    @validator('*')
    def validate_sum(cls, v, values):
        # Only validate when all values are present
        if len(values) == 5:  # All other fields have been set
            total = sum(values.values()) + v
            if abs(total - 1.0) > 0.0001:
                raise ValueError(f'Weights must sum to 1.0, got {total}')
        return v


class AssetVolatility(BaseModel):
    """Daily volatilities for each asset"""

    btc: float = Field(0.039, ge=0, le=1, description='BTC daily volatility')
    eth: float = Field(0.048, ge=0, le=1, description='ETH daily volatility')
    xrp: float = Field(0.053, ge=0, le=1, description='XRP daily volatility')
    sol: float = Field(0.071, ge=0, le=1, description='SOL daily volatility')
    ada: float = Field(0.055, ge=0, le=1, description='ADA daily volatility')
    xlm: float = Field(0.051, ge=0, le=1, description='XLM daily volatility')


class CorrelationParameters(BaseModel):
    """Correlation parameters for the market"""

    btc_eth: float = Field(0.70, ge=-1, le=1, description='BTC-ETH correlation')
    btc_excluded: float = Field(
        0.60, ge=-1, le=1, description='BTC vs excluded assets correlation'
    )
    within_excluded: float = Field(
        0.60, ge=-1, le=1, description='Within excluded assets correlation'
    )
    eth_excluded: float = Field(
        0.60, ge=-1, le=1, description='ETH vs excluded assets correlation'
    )


class MarketParameters(BaseModel):
    """Market structure parameters"""

    benchmark_weights: BenchmarkWeights = Field(default_factory=BenchmarkWeights)
    volatilities: AssetVolatility = Field(default_factory=AssetVolatility)
    correlations: CorrelationParameters = Field(default_factory=CorrelationParameters)
    trading_days_per_year: int = Field(252, ge=1, description='Trading days per year')


class FundDetails(BaseModel):
    """Fund details for tracking difference calculation"""

    nav: float = Field(500000000, gt=0, description='Net Asset Value in dollars')
    current_td: float = Field(
        0.0143, ge=0, le=1, description='Current expected tracking difference'
    )
    cap_td: float = Field(
        0.015, ge=0, le=1, description='Tracking difference cap set by committee'
    )


class AssetStakingParams(BaseModel):
    """Staking parameters for a single asset"""

    staking_pct: float = Field(0.90, ge=0, le=1, description='Staking percentage')
    unbonding_period_days: int = Field(10, ge=0, description='Unbonding period in days')
    annual_yield: float = Field(0.05, ge=0, le=0.20, description='Annual staking yield')
    baseline_staking_pct: float = Field(
        0.70, ge=0, le=1, description='Baseline staking percentage'
    )


class StakingParams(BaseModel):
    """Staking parameters for ETH and SOL"""

    eth: AssetStakingParams = Field(
        default_factory=lambda: AssetStakingParams(
            staking_pct=0.90,
            unbonding_period_days=10,
            annual_yield=0.03,
            baseline_staking_pct=0.70,
        )
    )
    sol: AssetStakingParams = Field(
        default_factory=lambda: AssetStakingParams(
            staking_pct=0.90,
            unbonding_period_days=2,
            annual_yield=0.073,
            baseline_staking_pct=0.70,
        )
    )


class RedemptionDistributionItem(BaseModel):
    """Single item in redemption distribution"""

    probability: float = Field(
        ge=0, le=1, description='Probability of this redemption size'
    )
    size: float = Field(
        ge=0, le=1, description='Redemption size as fraction of portfolio'
    )


class RedemptionParams(BaseModel):
    """Redemption distribution parameters"""

    expected_redemptions_per_year: float = Field(
        default=18, ge=0, description='Expected number of redemptions per year'
    )
    distribution: List[RedemptionDistributionItem] = Field(
        default=[
            RedemptionDistributionItem(probability=0.667, size=0.05),
            RedemptionDistributionItem(probability=0.167, size=0.10),
            RedemptionDistributionItem(probability=0.111, size=0.20),
            RedemptionDistributionItem(probability=0.055, size=0.30),
        ],
        description='Redemption size distribution',
    )

    @validator('distribution')
    def validate_probabilities(cls, v):
        total_prob = sum(item.probability for item in v)
        if (
            abs(total_prob - 1.0) > 0.01
        ):  # Allow 1% tolerance for floating point precision
            raise ValueError(f'Probabilities must sum to 1.0, got {total_prob}')
        return v


# Legacy models for backward compatibility
class LegacyStakingParams(BaseModel):
    """Legacy staking parameters (for backward compatibility)"""

    eth_staking_pct: float = Field(
        0.90, ge=0, le=1, description='ETH staking percentage'
    )
    sol_staking_pct: float = Field(
        0.90, ge=0, le=1, description='SOL staking percentage'
    )


class LegacyRedemptionParams(BaseModel):
    """Legacy redemption distribution parameters"""

    redemption_sizes: List[float] = Field(
        default=[0.05, 0.10, 0.20, 0.30], description='Redemption sizes'
    )
    redemption_counts: List[int] = Field(
        default=[12, 3, 2, 1], description='Count of redemptions for each size'
    )
    expected_redemptions_per_year: float = Field(
        default=18, description='Expected number of redemptions per year'
    )


class YieldParams(BaseModel):
    """Staking yield parameters"""

    annual_staking_yield: float = Field(
        0.05, ge=0, le=0.20, description='Annual staking yield'
    )
    baseline_staking_percentage: float = Field(
        0.70, ge=0, le=1, description='Baseline staking level'
    )


class CalculationRequest(BaseModel):
    """Request model for tracking error calculation"""

    staking: StakingParams = Field(default_factory=StakingParams)
    redemption: RedemptionParams = Field(default_factory=RedemptionParams)
    market: Optional[MarketParameters] = Field(
        default=None, description='Optional market parameters'
    )
    fund_details: Optional[FundDetails] = Field(
        default=None, description='Optional fund details'
    )

    class Config:
        # Allow extra fields for backward compatibility
        extra = 'allow'


# Legacy calculation request for backward compatibility
class LegacyCalculationRequest(BaseModel):
    """Legacy request model for backward compatibility"""

    staking: LegacyStakingParams = Field(default_factory=LegacyStakingParams)
    redemption: LegacyRedemptionParams = Field(default_factory=LegacyRedemptionParams)
    yield_params: YieldParams = Field(default_factory=YieldParams)


class DecompositionResults(BaseModel):
    """Decomposition of tracking error results"""

    tracking_error: float
    te_eth_only: float
    te_sol_only: float
    independence_approx: float
    correlation_cost: float
    correlation_cost_pct: float
    eth_contribution_pct: float
    sol_contribution_pct: float
    cross_contribution_pct: float


class NetBenefitResults(BaseModel):
    """Net benefit analysis results"""

    tracking_error: float
    eth_benefit_baseline: float
    eth_benefit_marginal: float
    eth_benefit_total: float
    sol_benefit_baseline: float
    sol_benefit_marginal: float
    sol_benefit_total: float
    total_yield_benefit: float
    expected_shortfall: float
    tracking_difference_budget: float
    td_budget_deficit: float
    net_benefit: float
    net_benefit_bps: float


class SensitivityPoint(BaseModel):
    """Single point in sensitivity analysis"""

    staking_level: float
    tracking_error: float
    yield_benefit: float
    expected_shortfall: float
    net_benefit_bps: float


class SensitivityPoint2D(BaseModel):
    """Single point in 2D sensitivity analysis"""

    eth_staking_level: float
    sol_staking_level: float
    tracking_error: float
    yield_benefit: float
    expected_shortfall: float
    net_benefit_bps: float


class OptimalStakingLevels(BaseModel):
    """Optimal staking levels for each asset"""

    eth: float = Field(description='Optimal ETH staking percentage')
    sol: float = Field(description='Optimal SOL staking percentage')


class CalculationResponse(BaseModel):
    """Response model for tracking error calculation"""

    decomposition: DecompositionResults
    net_benefit: NetBenefitResults
    optimal_staking_level: float  # Kept for backward compatibility
    optimal_staking_levels: OptimalStakingLevels  # New field for individual levels
    sensitivity_analysis: List[SensitivityPoint]
    sensitivity_analysis_2d: Optional[List[SensitivityPoint2D]] = None
    parameters_used: CalculationRequest
