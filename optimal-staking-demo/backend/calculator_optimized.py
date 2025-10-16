"""
Optimized wrapper for the API using the high-performance calculator
==================================================================

Drop-in replacement for calculator.py with 10-100x performance improvement
for sensitivity analysis while maintaining exact same API interface.
"""

import numpy as np
from typing import List, Union
from core.optimized_calculator import OptimizedCalculator, create_optimized_calculator
from models import (
    CalculationRequest,
    LegacyCalculationRequest,
    CalculationResponse,
    DecompositionResults,
    NetBenefitResults,
    SensitivityPoint,
    SensitivityPoint2D,
    OptimalStakingLevels,
)

# Import original calculator for legacy compatibility and decomposition
from calculator import convert_legacy_request, TwoAssetTrackingError
from core.two_asset_discrete_te import (
    BenchmarkWeights,
    StakingParameters,
    MarketParameters,
    RedemptionDistribution,
    StakingYieldParameters,
    FundDetails,
)


def calculate_tracking_error(
    request: Union[CalculationRequest, dict],
) -> CalculationResponse:
    """
    Optimized tracking error calculation with vectorized sensitivity analysis
    """
    # Handle legacy request format (same as original)
    if isinstance(request, dict):
        if 'yield_params' in request:
            legacy_req = LegacyCalculationRequest(**request)
            request = convert_legacy_request(legacy_req)
        else:
            request = CalculationRequest(**request)
    elif hasattr(request, 'yield_params'):
        request = convert_legacy_request(request)

    # Parse market parameters
    if request.market:
        benchmark_weights = {
            'btc': request.market.benchmark_weights.btc,
            'eth': request.market.benchmark_weights.eth,
            'sol': request.market.benchmark_weights.sol,
        }
        market_params = {
            'daily_volatilities': {
                'BTC': request.market.volatilities.btc,
                'ETH': request.market.volatilities.eth,
                'XRP': request.market.volatilities.xrp,
                'SOL': request.market.volatilities.sol,
                'ADA': request.market.volatilities.ada,
                'XLM': request.market.volatilities.xlm,
            },
            'correlations': {
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
                ('ADA', 'XLM'): request.market.correlations.within_excluded,
            },
        }
    else:
        # Use defaults
        benchmark_weights = {'btc': 0.7869, 'eth': 0.1049, 'sol': 0.0387}
        market_params = {
            'daily_volatilities': {
                'BTC': 0.039,
                'ETH': 0.048,
                'XRP': 0.053,
                'SOL': 0.071,
                'ADA': 0.055,
                'XLM': 0.051,
            },
            'correlations': {
                ('BTC', 'ETH'): 0.70,
                ('BTC', 'XRP'): 0.60,
                ('BTC', 'SOL'): 0.60,
                ('BTC', 'ADA'): 0.60,
                ('BTC', 'XLM'): 0.60,
                ('ETH', 'XRP'): 0.60,
                ('ETH', 'SOL'): 0.60,
                ('ETH', 'ADA'): 0.60,
                ('ETH', 'XLM'): 0.60,
                ('XRP', 'SOL'): 0.60,
                ('XRP', 'ADA'): 0.60,
                ('XRP', 'XLM'): 0.60,
                ('SOL', 'ADA'): 0.60,
                ('SOL', 'XLM'): 0.60,
                ('ADA', 'XLM'): 0.60,
            },
        }

    # Parse redemption distribution
    redemption_dist = {
        'sizes': [item.size for item in request.redemption.distribution],
        'probabilities': [item.probability for item in request.redemption.distribution],
        'lambda': request.redemption.expected_redemptions_per_year,
    }

    # Parse yield parameters
    yield_params = {
        'eth_yield': request.staking.eth.annual_yield,
        'sol_yield': request.staking.sol.annual_yield,
        'eth_baseline': request.staking.eth.baseline_staking_pct,
        'sol_baseline': request.staking.sol.baseline_staking_pct,
    }

    # Unbonding days
    unbonding_days = {
        'eth': request.staking.eth.unbonding_period_days,
        'sol': request.staking.sol.unbonding_period_days,
    }

    # Parse fund details
    fund_details = None
    if request.fund_details:
        fund_details = {
            'nav': request.fund_details.nav,
            'current_td': request.fund_details.current_td,
            'cap_td': request.fund_details.cap_td,
        }

    # Create optimized calculator
    opt_calc = create_optimized_calculator(
        benchmark_weights,
        market_params,
        redemption_dist,
        yield_params,
        unbonding_days,
        fund_details,
    )

    # For decomposition and single-point calculation, use original calculator
    # (ensures exact compatibility and provides detailed decomposition)
    benchmark = (
        BenchmarkWeights()
        if not request.market
        else BenchmarkWeights(
            btc_weight=request.market.benchmark_weights.btc,
            eth_weight=request.market.benchmark_weights.eth,
            xrp_weight=request.market.benchmark_weights.xrp,
            sol_weight=request.market.benchmark_weights.sol,
            ada_weight=request.market.benchmark_weights.ada,
            xlm_weight=request.market.benchmark_weights.xlm,
        )
    )

    staking = StakingParameters(
        eth_staking_pct=request.staking.eth.staking_pct,
        sol_staking_pct=request.staking.sol.staking_pct,
        eth_unbonding_days=request.staking.eth.unbonding_period_days,
        sol_unbonding_days=request.staking.sol.unbonding_period_days,
    )

    market = (
        MarketParameters()
        if not request.market
        else MarketParameters(
            daily_volatilities=market_params['daily_volatilities'],
            correlations=market_params['correlations'],
            trading_days_per_year=request.market.trading_days_per_year,
        )
    )

    redemption_sizes = [item.size for item in request.redemption.distribution]
    redemption_probs = [item.probability for item in request.redemption.distribution]
    # Convert probabilities to counts that preserve the distribution
    # Scale by 1000 and round to get reasonable integer counts
    redemption_counts = [int(round(prob * 1000)) for prob in redemption_probs]

    redemption = RedemptionDistribution(
        redemption_sizes=redemption_sizes,
        redemption_counts=redemption_counts,
        expected_redemptions_per_year=request.redemption.expected_redemptions_per_year,
    )

    yield_params_obj = StakingYieldParameters(
        eth_annual_yield=request.staking.eth.annual_yield,
        sol_annual_yield=request.staking.sol.annual_yield,
        eth_baseline_staking_pct=request.staking.eth.baseline_staking_pct,
        sol_baseline_staking_pct=request.staking.sol.baseline_staking_pct,
    )

    # Create fund details if provided
    fund_details_obj = None
    if request.fund_details:
        fund_details_obj = FundDetails(
            nav=request.fund_details.nav,
            current_td=request.fund_details.current_td,
            cap_td=request.fund_details.cap_td,
        )

    # Calculate decomposition using original calculator
    calculator = TwoAssetTrackingError(
        benchmark, staking, market, redemption, yield_params_obj, fund_details_obj
    )
    decomposition = calculator.decompose_results()
    net_benefit = calculator.net_benefit_analysis()

    # Perform OPTIMIZED 1D sensitivity analysis
    sensitivity_points = perform_sensitivity_analysis_optimized(opt_calc)

    # Perform OPTIMIZED 2D sensitivity analysis
    sensitivity_points_2d = perform_sensitivity_analysis_2d_optimized(opt_calc)

    # Find optimal levels
    optimal_level = find_optimal_staking_level(sensitivity_points)
    optimal_levels = find_optimal_staking_levels_2d(sensitivity_points_2d)

    return CalculationResponse(
        decomposition=DecompositionResults(**decomposition),
        net_benefit=NetBenefitResults(**net_benefit),
        optimal_staking_level=optimal_level,
        optimal_staking_levels=optimal_levels,
        sensitivity_analysis=sensitivity_points,
        sensitivity_analysis_2d=sensitivity_points_2d,
        parameters_used=request,
    )


def perform_sensitivity_analysis_optimized(
    opt_calc: OptimizedCalculator,
) -> List[SensitivityPoint]:
    """
    Optimized 1D sensitivity analysis using vectorized calculations

    The search space starts at the minimum of the baseline staking percentages,
    allowing optimization to recommend levels below the baseline when beneficial.
    """
    # Use the minimum baseline as the starting point for the search
    min_baseline = min(opt_calc.eth_baseline, opt_calc.sol_baseline)

    # Generate staking levels starting from the minimum baseline
    # Use same granular increments around high-probability areas (0.88-0.98)
    if min_baseline <= 0.85:
        levels_list = [
            min_baseline + i * 0.05
            for i in range(int((0.85 - min_baseline) / 0.05) + 1)
        ]
        levels_list.extend([
            0.88,
            0.89,
            0.90,
            0.91,
            0.92,
            0.93,
            0.94,
            0.95,
            0.96,
            0.97,
            0.98,
        ])
    else:
        # If baseline is already high, just use granular increments from baseline to 0.98
        levels_list = [
            min_baseline + i * 0.01
            for i in range(int((0.98 - min_baseline) / 0.01) + 1)
        ]

    staking_levels = np.array(levels_list)

    # Calculate all tracking errors at once
    tracking_errors = opt_calc.calculate_tracking_errors(staking_levels, staking_levels)

    # Calculate all net benefits at once
    results = opt_calc.calculate_net_benefits(
        tracking_errors, staking_levels, staking_levels
    )

    # Convert to SensitivityPoint objects
    sensitivity_points = []
    for i, level in enumerate(staking_levels):
        sensitivity_points.append(
            SensitivityPoint(
                staking_level=level,
                tracking_error=tracking_errors[i],
                yield_benefit=results['yield_benefits'][i],
                expected_shortfall=results['expected_shortfalls'][i],
                net_benefit_bps=results['net_benefits_bps'][i],
            )
        )

    return sensitivity_points


def perform_sensitivity_analysis_2d_optimized(
    opt_calc: OptimizedCalculator,
) -> List[SensitivityPoint2D]:
    """Optimized 2D sensitivity analysis using vectorized calculations"""
    # Full 31x31 grid for complete coverage (961 points)
    results_2d = opt_calc.perform_2d_sensitivity_analysis(n_points=31)

    # Convert to list of SensitivityPoint2D objects
    sensitivity_points_2d = []
    n_points = results_2d['eth_levels'].shape[0]

    for i in range(n_points):
        for j in range(n_points):
            sensitivity_points_2d.append(
                SensitivityPoint2D(
                    eth_staking_level=results_2d['eth_levels'][i, j],
                    sol_staking_level=results_2d['sol_levels'][i, j],
                    tracking_error=results_2d['tracking_errors'][i, j],
                    yield_benefit=results_2d['yield_benefits'][i, j],
                    expected_shortfall=results_2d['expected_shortfalls'][i, j],
                    net_benefit_bps=results_2d['net_benefits_bps'][i, j],
                )
            )

    return sensitivity_points_2d


def find_optimal_staking_level(sensitivity_points: List[SensitivityPoint]) -> float:
    """Find the staking level that maximizes net benefit"""
    if not sensitivity_points:
        return 0.93

    optimal_point = max(sensitivity_points, key=lambda p: p.net_benefit_bps)
    return optimal_point.staking_level


def find_optimal_staking_levels_2d(
    sensitivity_points_2d: List[SensitivityPoint2D],
) -> OptimalStakingLevels:
    """Find the combination of ETH and SOL staking levels that maximizes net benefit"""
    if not sensitivity_points_2d:
        return OptimalStakingLevels(eth=0.93, sol=0.93)

    optimal_point = max(sensitivity_points_2d, key=lambda p: p.net_benefit_bps)
    return OptimalStakingLevels(
        eth=optimal_point.eth_staking_level, sol=optimal_point.sol_staking_level
    )
