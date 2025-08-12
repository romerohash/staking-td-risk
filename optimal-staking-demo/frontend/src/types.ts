export interface AssetStakingParams {
  staking_pct: number;
  unbonding_period_days: number;
  annual_yield: number;
  baseline_staking_pct: number;
}

export interface StakingParams {
  eth: AssetStakingParams;
  sol: AssetStakingParams;
}

export interface RedemptionDistributionItem {
  probability: number;
  size: number;
}

export interface RedemptionParams {
  expected_redemptions_per_year: number;
  distribution: RedemptionDistributionItem[];
}

export interface BenchmarkWeights {
  btc: number;
  eth: number;
  xrp: number;
  sol: number;
  ada: number;
  link: number;
  xlm: number;
  ltc: number;
  uni: number;
}

export interface AssetVolatilities {
  btc: number;
  eth: number;
  xrp: number;
  sol: number;
  ada: number;
  link: number;
  xlm: number;
  ltc: number;
  uni: number;
}

export interface CorrelationParameters {
  btc_eth: number;
  btc_excluded: number;
  eth_excluded: number;
  within_excluded: number;
}

export interface MarketParameters {
  benchmark_weights: BenchmarkWeights;
  volatilities: AssetVolatilities;
  correlations: CorrelationParameters;
  trading_days_per_year?: number;
}

export interface FundDetails {
  nav: number;
  current_td: number;
  cap_td: number;
}

export interface CalculationRequest {
  staking: StakingParams;
  redemption: RedemptionParams;
  market?: MarketParameters;
  fund_details?: FundDetails;
}

export interface DecompositionResults {
  tracking_error: number;
  te_eth_only: number;
  te_sol_only: number;
  independence_approx: number;
  correlation_cost: number;
  correlation_cost_pct: number;
  eth_contribution_pct: number;
  sol_contribution_pct: number;
  cross_contribution_pct: number;
}

export interface NetBenefitResults {
  tracking_error: number;
  eth_benefit_baseline: number;
  eth_benefit_marginal: number;
  eth_benefit_total: number;
  sol_benefit_baseline: number;
  sol_benefit_marginal: number;
  sol_benefit_total: number;
  total_yield_benefit: number;
  expected_shortfall: number;
  tracking_difference_budget: number;
  td_budget_deficit: number;
  net_benefit: number;
  net_benefit_bps: number;
}

export interface SensitivityPoint {
  staking_level: number;
  tracking_error: number;
  yield_benefit: number;
  expected_shortfall: number;
  net_benefit_bps: number;
}

export interface SensitivityPoint2D {
  eth_staking_level: number;
  sol_staking_level: number;
  tracking_error: number;
  yield_benefit: number;
  expected_shortfall: number;
  net_benefit_bps: number;
}

export interface OptimalStakingLevels {
  eth: number;
  sol: number;
}

export interface CalculationResponse {
  decomposition: DecompositionResults;
  net_benefit: NetBenefitResults;
  optimal_staking_level: number;
  optimal_staking_levels: OptimalStakingLevels;
  sensitivity_analysis: SensitivityPoint[];
  sensitivity_analysis_2d?: SensitivityPoint2D[];
  parameters_used: CalculationRequest;
}