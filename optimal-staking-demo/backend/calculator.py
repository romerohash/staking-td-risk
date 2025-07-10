"""
Wrapper around two_asset_discrete_te.py for the API
"""
from typing import List
import sys
sys.path.append('.')  # Add current directory to path for core imports

from core.two_asset_discrete_te import (
    BenchmarkWeights,
    StakingParameters,
    MarketParameters,
    RedemptionDistribution,
    StakingYieldParameters,
    TwoAssetTrackingError,
    FundDetails
)
from models import (
    CalculationRequest,
    LegacyCalculationRequest,
    CalculationResponse,
    DecompositionResults,
    NetBenefitResults,
    SensitivityPoint,
    SensitivityPoint2D,
    RedemptionDistributionItem,
    OptimalStakingLevels
)
from typing import Union


def convert_legacy_request(legacy_req: LegacyCalculationRequest) -> CalculationRequest:
    """
    Convert legacy request format to new format
    """
    from models import StakingParams, AssetStakingParams, RedemptionParams
    
    # Convert redemption counts to probabilities
    total_count = sum(legacy_req.redemption.redemption_counts)
    distribution = [
        RedemptionDistributionItem(
            size=size,
            probability=count / total_count
        )
        for size, count in zip(
            legacy_req.redemption.redemption_sizes,
            legacy_req.redemption.redemption_counts
        )
    ]
    
    return CalculationRequest(
        staking=StakingParams(
            eth=AssetStakingParams(
                staking_pct=legacy_req.staking.eth_staking_pct,
                unbonding_period_days=10,
                annual_yield=legacy_req.yield_params.annual_staking_yield,
                baseline_staking_pct=legacy_req.yield_params.baseline_staking_percentage
            ),
            sol=AssetStakingParams(
                staking_pct=legacy_req.staking.sol_staking_pct,
                unbonding_period_days=2,
                annual_yield=legacy_req.yield_params.annual_staking_yield,
                baseline_staking_pct=legacy_req.yield_params.baseline_staking_percentage
            )
        ),
        redemption=RedemptionParams(
            expected_redemptions_per_year=legacy_req.redemption.expected_redemptions_per_year,
            distribution=distribution
        )
    )


def calculate_tracking_error(request: Union[CalculationRequest, dict]) -> CalculationResponse:
    """
    Calculate tracking error and perform sensitivity analysis
    """
    # Handle legacy request format
    if isinstance(request, dict):
        # Check if it's legacy format
        if 'yield_params' in request:
            legacy_req = LegacyCalculationRequest(**request)
            request = convert_legacy_request(legacy_req)
        else:
            request = CalculationRequest(**request)
    elif hasattr(request, 'yield_params'):
        # It's a legacy request object
        request = convert_legacy_request(request)
    
    # Create parameter objects from request
    # Handle market parameters
    if request.market:
        benchmark = BenchmarkWeights(
            btc_weight=request.market.benchmark_weights.btc,
            eth_weight=request.market.benchmark_weights.eth,
            xrp_weight=request.market.benchmark_weights.xrp,
            sol_weight=request.market.benchmark_weights.sol,
            ada_weight=request.market.benchmark_weights.ada,
            xlm_weight=request.market.benchmark_weights.xlm
        )
        # Build market parameters from custom values
        market = MarketParameters(
            daily_volatilities={
                'BTC': request.market.volatilities.btc,
                'ETH': request.market.volatilities.eth,
                'XRP': request.market.volatilities.xrp,
                'SOL': request.market.volatilities.sol,
                'ADA': request.market.volatilities.ada,
                'XLM': request.market.volatilities.xlm
            },
            correlations={
                ('BTC', 'ETH'): request.market.correlations.btc_eth,
                ('BTC', 'XRP'): request.market.correlations.btc_excluded,
                ('BTC', 'SOL'): request.market.correlations.btc_excluded,
                ('BTC', 'ADA'): request.market.correlations.btc_excluded,
                ('BTC', 'XLM'): request.market.correlations.btc_excluded,
                ('ETH', 'XRP'): request.market.correlations.eth_excluded,
                ('ETH', 'SOL'): request.market.correlations.eth_excluded,
                ('ETH', 'ADA'): request.market.correlations.eth_excluded,
                ('ETH', 'XLM'): request.market.correlations.eth_excluded,
                ('XRP', 'SOL'): request.market.correlations.within_excluded,
                ('XRP', 'ADA'): request.market.correlations.within_excluded,
                ('XRP', 'XLM'): request.market.correlations.within_excluded,
                ('SOL', 'ADA'): request.market.correlations.within_excluded,
                ('SOL', 'XLM'): request.market.correlations.within_excluded,
                ('ADA', 'XLM'): request.market.correlations.within_excluded
            },
            trading_days_per_year=request.market.trading_days_per_year
        )
    else:
        benchmark = BenchmarkWeights()  # Using defaults
        market = MarketParameters()  # Using defaults
    
    staking = StakingParameters(
        eth_staking_pct=request.staking.eth.staking_pct,
        sol_staking_pct=request.staking.sol.staking_pct,
        eth_unbonding_days=request.staking.eth.unbonding_period_days,
        sol_unbonding_days=request.staking.sol.unbonding_period_days
    )
    
    # Convert redemption distribution
    redemption_sizes = [item.size for item in request.redemption.distribution]
    redemption_probs = [item.probability for item in request.redemption.distribution]
    # Convert probabilities to counts that preserve the distribution
    # Scale by 1000 and round to get reasonable integer counts
    redemption_counts = [int(round(prob * 1000)) for prob in redemption_probs]
    
    redemption = RedemptionDistribution(
        redemption_sizes=redemption_sizes,
        redemption_counts=redemption_counts,
        expected_redemptions_per_year=request.redemption.expected_redemptions_per_year
    )
    
    # Use asset-specific yields
    yield_params = StakingYieldParameters(
        eth_annual_yield=request.staking.eth.annual_yield,
        sol_annual_yield=request.staking.sol.annual_yield,
        eth_baseline_staking_pct=request.staking.eth.baseline_staking_pct,
        sol_baseline_staking_pct=request.staking.sol.baseline_staking_pct
    )
    
    # Create fund details if provided
    fund_details = None
    if request.fund_details:
        fund_details = FundDetails(
            nav=request.fund_details.nav,
            current_td=request.fund_details.current_td,
            cap_td=request.fund_details.cap_td
        )
    
    # Create calculator and compute results
    calculator = TwoAssetTrackingError(
        benchmark, staking, market, redemption, yield_params, fund_details
    )
    
    decomposition = calculator.decompose_results()
    net_benefit = calculator.net_benefit_analysis()
    
    # Perform sensitivity analysis
    sensitivity_points = perform_sensitivity_analysis(
        benchmark, market, redemption, yield_params,
        request.staking.eth.unbonding_period_days,
        request.staking.sol.unbonding_period_days,
        fund_details
    )
    
    # Perform 2D sensitivity analysis
    sensitivity_points_2d = perform_sensitivity_analysis_2d(
        benchmark, market, redemption, yield_params,
        request.staking.eth.unbonding_period_days,
        request.staking.sol.unbonding_period_days,
        fund_details
    )
    
    # Find optimal staking level
    optimal_level = find_optimal_staking_level(sensitivity_points)
    
    # Find optimal staking levels from 2D analysis
    optimal_levels = find_optimal_staking_levels_2d(sensitivity_points_2d)
    
    return CalculationResponse(
        decomposition=DecompositionResults(**decomposition),
        net_benefit=NetBenefitResults(**net_benefit),
        optimal_staking_level=optimal_level,
        optimal_staking_levels=optimal_levels,
        sensitivity_analysis=sensitivity_points,
        sensitivity_analysis_2d=sensitivity_points_2d,
        parameters_used=request
    )


def perform_sensitivity_analysis(
    benchmark: BenchmarkWeights,
    market: MarketParameters,
    redemption: RedemptionDistribution,
    yield_params: StakingYieldParameters,
    eth_unbonding_days: int,
    sol_unbonding_days: int,
    fund_details: FundDetails = None
) -> List[SensitivityPoint]:
    """
    Perform sensitivity analysis across different staking levels
    """
    staking_levels = [0.70, 0.75, 0.80, 0.85, 0.88, 0.89, 0.90, 
                     0.91, 0.92, 0.93, 0.94, 0.95, 0.96, 0.97, 0.98]
    results = []
    
    for level in staking_levels:
        test_staking = StakingParameters(
            eth_staking_pct=level,
            sol_staking_pct=level,
            eth_unbonding_days=eth_unbonding_days,
            sol_unbonding_days=sol_unbonding_days
        )
        test_calc = TwoAssetTrackingError(
            benchmark, test_staking, market, redemption, yield_params, fund_details
        )
        test_benefits = test_calc.net_benefit_analysis()
        
        results.append(SensitivityPoint(
            staking_level=level,
            tracking_error=test_benefits['tracking_error'],
            yield_benefit=test_benefits['total_yield_benefit'],
            expected_shortfall=test_benefits['expected_shortfall'],
            net_benefit_bps=test_benefits['net_benefit_bps']
        ))
    
    return results


def find_optimal_staking_level(sensitivity_points: List[SensitivityPoint]) -> float:
    """
    Find the staking level that maximizes net benefit
    """
    if not sensitivity_points:
        return 0.93  # Default optimal
    
    optimal_point = max(sensitivity_points, key=lambda p: p.net_benefit_bps)
    return optimal_point.staking_level


def find_optimal_staking_levels_2d(sensitivity_points_2d: List[SensitivityPoint2D]) -> OptimalStakingLevels:
    """
    Find the combination of ETH and SOL staking levels that maximizes net benefit
    """
    if not sensitivity_points_2d:
        return OptimalStakingLevels(eth=0.93, sol=0.93)  # Default optimal
    
    optimal_point = max(sensitivity_points_2d, key=lambda p: p.net_benefit_bps)
    return OptimalStakingLevels(
        eth=optimal_point.eth_staking_level,
        sol=optimal_point.sol_staking_level
    )


def perform_sensitivity_analysis_2d(
    benchmark: BenchmarkWeights,
    market: MarketParameters,
    redemption: RedemptionDistribution,
    yield_params: StakingYieldParameters,
    eth_unbonding_days: int,
    sol_unbonding_days: int,
    fund_details: FundDetails = None
) -> List[SensitivityPoint2D]:
    """
    Perform 2D sensitivity analysis across different ETH and SOL staking levels
    """
    # Generate 1% increments from 70% to 100% for smoother surfaces
    eth_levels = [i / 100.0 for i in range(70, 101)]  # 70%, 71%, ..., 100%
    sol_levels = [i / 100.0 for i in range(70, 101)]  # 70%, 71%, ..., 100%
    results = []
    
    for eth_level in eth_levels:
        for sol_level in sol_levels:
            test_staking = StakingParameters(
                eth_staking_pct=eth_level,
                sol_staking_pct=sol_level,
                eth_unbonding_days=eth_unbonding_days,
                sol_unbonding_days=sol_unbonding_days
            )
            test_calc = TwoAssetTrackingError(
                benchmark, test_staking, market, redemption, yield_params, fund_details
            )
            test_benefits = test_calc.net_benefit_analysis()
            
            results.append(SensitivityPoint2D(
                eth_staking_level=eth_level,
                sol_staking_level=sol_level,
                tracking_error=test_benefits['tracking_error'],
                yield_benefit=test_benefits['total_yield_benefit'],
                expected_shortfall=test_benefits['expected_shortfall'],
                net_benefit_bps=test_benefits['net_benefit_bps']
            ))
    
    return results