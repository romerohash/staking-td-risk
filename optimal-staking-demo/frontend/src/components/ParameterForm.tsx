import React, { useState, useCallback, useEffect } from 'react';
import {
  Box,
  TextField,
  Typography,
  Slider,
  Stack,
  Divider,
  InputAdornment,
  Grid,
  Button,
  Switch,
  FormControlLabel,
  Tooltip,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import { CalculationRequest, AssetStakingParams, BenchmarkWeights, MarketParameters, AssetVolatilities, RedemptionDistributionItem, FundDetails } from '../types';
import { glassStyles } from '../styles/glassmorphism';
import { CollapsibleSection } from './CollapsibleSection';
import { RedemptionDistributionBuilder } from './RedemptionDistributionBuilder';
import { InfoTooltip } from './InfoTooltip';
import { useDebouncedNumericInput } from '../hooks/useDebouncedNumericInput';

interface ParameterFormProps {
  parameters: CalculationRequest;
  onChange: (params: CalculationRequest) => void;
  onVolatilityTypeChange?: (type: 'daily' | 'annual') => void;
  onDocumentClick?: (path: string, title: string) => void;
  onValidationChange?: (isValid: boolean) => void;
  autoFitToOptimal?: boolean;
  onAutoFitToOptimalChange?: (value: boolean) => void;
  hasResults?: boolean;
}

interface AssetStakingSectionProps {
  asset: 'eth' | 'sol';
  color: string;
  parameters: CalculationRequest;
  handleAssetStakingChange: (
    asset: 'eth' | 'sol',
    field: keyof AssetStakingParams,
    value: number,
    isPercentage?: boolean
  ) => void;
  onDocumentClick?: (path: string, title: string) => void;
  disabled?: boolean;
}

const AssetStakingSection: React.FC<AssetStakingSectionProps> = ({ 
  asset, 
  color, 
  parameters, 
  handleAssetStakingChange, 
  onDocumentClick,
  disabled = false
}) => {
  // Debounced inputs for smooth typing experience
  const unbondingInput = useDebouncedNumericInput({
    value: parameters.staking[asset].unbonding_period_days,
    onChange: (value) => handleAssetStakingChange(asset, 'unbonding_period_days', value),
    min: 0,
    decimalPlaces: 0,
  });

  const stakingYieldInput = useDebouncedNumericInput({
    value: parameters.staking[asset].annual_yield * 100,
    onChange: (value) => handleAssetStakingChange(asset, 'annual_yield', value, true),
    min: 0,
    max: 20,
    decimalPlaces: 1,
  });

  const baselineStakingInput = useDebouncedNumericInput({
    value: parameters.staking[asset].baseline_staking_pct * 100,
    onChange: (value) => handleAssetStakingChange(asset, 'baseline_staking_pct', value, true),
    min: 0,
    max: 100,
    decimalPlaces: 0,
  });

  return (
  <Box sx={{ mb: 3 }}>
    <Typography variant="subtitle2" sx={{ mb: 2, textTransform: 'uppercase' }}>
      {asset} Configuration
    </Typography>
    
    <Stack spacing={2}>
      <Box>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
          <Typography variant="body2" color="text.secondary">
            Staking Percentage: {(parameters.staking[asset].staking_pct * 100).toFixed(0)}%
          </Typography>
          <InfoTooltip
            title="Percentage of the asset that is staked and subject to unbonding delays"
            documentLink={{
              path: 'two-asset-model-parameters.md',
              title: 'Model Parameters',
              section: 'staking-parameters'
            }}
            onDocumentClick={onDocumentClick}
          />
        </Box>
        <Slider
          value={parameters.staking[asset].staking_pct * 100}
          onChange={(_, value) => handleAssetStakingChange(asset, 'staking_pct', value as number, true)}
          min={0}
          max={100}
          step={1}
          disabled={disabled}
          sx={{
            color: color,
            opacity: disabled ? 0.5 : 1,
            '& .MuiSlider-thumb': {
              background: `linear-gradient(135deg, ${color} 0%, ${color}CC 100%)`,
            },
          }}
        />
      </Box>

      <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
        <TextField
          label="Unbonding Period"
          type="number"
          value={unbondingInput.value}
          onChange={(e) => unbondingInput.onChange(e.target.value)}
          inputProps={{ min: 0, step: 1 }}
          InputProps={{
            endAdornment: (
              <InputAdornment position="end">
                days
                <InfoTooltip
                  title="Time required to unlock staked assets and make them liquid"
                  documentLink={{
                    path: 'two-asset-tracking-error-formula.md',
                    title: 'Two-Asset Formula',
                    section: 'different-unbonding-periods'
                  }}
                  onDocumentClick={onDocumentClick}
                />
              </InputAdornment>
            ),
          }}
          sx={{ ...glassStyles.input, flex: '1 1 30%', minWidth: '200px' }}
          size="small"
        />
        
        <TextField
          label="Staking Yield"
          type="number"
          value={stakingYieldInput.value}
          onChange={(e) => stakingYieldInput.onChange(e.target.value)}
          inputProps={{ min: 0, max: 20, step: 0.1 }}
          InputProps={{
            endAdornment: (
              <InputAdornment position="end">
                %
                <InfoTooltip
                  title="Annual percentage return from staking"
                  documentLink={{
                    path: 'staking-benefit-formulation.md',
                    title: 'Staking Benefits'
                  }}
                  onDocumentClick={onDocumentClick}
                />
              </InputAdornment>
            ),
          }}
          sx={{ ...glassStyles.input, flex: '1 1 30%', minWidth: '200px' }}
          size="small"
        />
        
        <TextField
          label="Baseline Staking"
          type="number"
          value={baselineStakingInput.value}
          onChange={(e) => baselineStakingInput.onChange(e.target.value)}
          inputProps={{ min: 0, max: 100, step: 1 }}
          InputProps={{
            endAdornment: (
              <InputAdornment position="end">
                %
                <InfoTooltip
                  title="Reference staking level for calculating incremental benefits"
                  description="Benefits are calculated only for staking above this baseline level, higher baselines reduce the incentive (baseline benefit) to stake, leading to lower optimal staking levels"
                  documentLink={{
                    path: 'staking-benefit-formulation.md',
                    title: 'Benefit Formulation',
                    section: 'component-1-benefit-above-baseline-staking'
                  }}
                  onDocumentClick={onDocumentClick}
                />
              </InputAdornment>
            ),
          }}
          sx={{ ...glassStyles.input, flex: '1 1 30%', minWidth: '200px' }}
          size="small"
        />
      </Box>
    </Stack>
  </Box>
  );
};

export const ParameterForm: React.FC<ParameterFormProps> = ({
  parameters,
  onChange,
  onVolatilityTypeChange,
  onDocumentClick,
  onValidationChange,
  autoFitToOptimal = false,
  onAutoFitToOptimalChange,
  hasResults = false,
}) => {
  const [volatilityType, setVolatilityType] = useState<'daily' | 'annual'>('daily');
  const [fundDetailsError, setFundDetailsError] = useState<string | null>(null);
  
  // State for collapsible sections
  const [expandedSections, setExpandedSections] = useState({
    fundDetails: false,
    benchmarkWeights: false,
    marketParameters: false,
    stakingParameters: false,
    redemptionParameters: false,
  });
  
  // Toggle individual section
  const toggleSection = useCallback((section: keyof typeof expandedSections) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section],
    }));
  }, []);
  
  // Check if at least one section is expanded
  const hasExpandedSection = Object.values(expandedSections).some(expanded => expanded);
  
  // Toggle all sections
  const toggleAllSections = useCallback(() => {
    const shouldCollapse = hasExpandedSection;
    setExpandedSections({
      fundDetails: !shouldCollapse,
      benchmarkWeights: !shouldCollapse,
      marketParameters: !shouldCollapse,
      stakingParameters: !shouldCollapse,
      redemptionParameters: !shouldCollapse,
    });
  }, [hasExpandedSection]);
  
  // Default market parameters
  const defaultBenchmarkWeights: BenchmarkWeights = {
    btc: 0.7869,
    eth: 0.1049,
    xrp: 0.0549,
    sol: 0.0387,
    ada: 0.0119,
    xlm: 0.0027,
  };

  const defaultMarketParams: MarketParameters = {
    benchmark_weights: defaultBenchmarkWeights,
    volatilities: {
      btc: 0.039,
      eth: 0.048,
      xrp: 0.053,
      sol: 0.071,
      ada: 0.055,
      xlm: 0.051,
    },
    correlations: {
      btc_eth: 0.70,
      btc_excluded: 0.60,
      eth_excluded: 0.60,
      within_excluded: 0.60,
    },
    trading_days_per_year: 252,
  };

  // Initialize market params if not present
  const marketParams = parameters.market || defaultMarketParams;
  
  // Default fund details
  const defaultFundDetails: FundDetails = {
    nav: 500000000,
    current_td: 0.0143,
    cap_td: 0.015,
  };
  
  // Initialize fund details if not present
  const fundDetails = parameters.fund_details || defaultFundDetails;
  
  // Debounced inputs for Fund Details
  const navInput = useDebouncedNumericInput({
    value: fundDetails.nav,
    onChange: (value) => handleFundDetailsChange('nav', value),
    min: 0,
    decimalPlaces: 0,
  });
  
  const currentTdInput = useDebouncedNumericInput({
    value: fundDetails.current_td * 100,
    onChange: (value) => handleFundDetailsChange('current_td', value / 100),
    min: 0,
    max: 100,
    decimalPlaces: 2,
  });
  
  const capTdInput = useDebouncedNumericInput({
    value: fundDetails.cap_td * 100,
    onChange: (value) => handleFundDetailsChange('cap_td', value / 100),
    min: 0,
    max: 100,
    decimalPlaces: 2,
  });
  
  // Precise normalization function for benchmark weights
  const normalizeBenchmarkWeights = useCallback((weights: BenchmarkWeights): BenchmarkWeights => {
    const total = Object.values(weights).reduce((sum, weight) => sum + weight, 0);
    if (total === 0) return weights;
    
    // First pass: normalize all weights
    const normalized: any = {};
    const assetKeys = Object.keys(weights) as (keyof BenchmarkWeights)[];
    
    assetKeys.forEach(key => {
      normalized[key] = weights[key] / total;
    });
    
    // Second pass: adjust last weight to ensure exact sum of 1.0
    const allButLast = assetKeys.slice(0, -1);
    const lastKey = assetKeys[assetKeys.length - 1];
    const sumExceptLast = allButLast.reduce((sum, key) => sum + normalized[key], 0);
    normalized[lastKey] = 1.0 - sumExceptLast;
    
    // Ensure last weight is not negative
    if (normalized[lastKey] < 0) {
      normalized[lastKey] = 0;
    }
    
    return normalized as BenchmarkWeights;
  }, []);
  
  // Normalize redemption distribution to ensure probabilities sum to 1.0
  const normalizeRedemptionDistribution = useCallback((items: RedemptionDistributionItem[]): RedemptionDistributionItem[] => {
    if (items.length === 0) return items;
    
    const total = items.reduce((sum, item) => sum + item.probability, 0);
    if (total === 0) return items;
    
    // First pass: normalize all probabilities
    const normalized = items.map(item => ({
      ...item,
      probability: item.probability / total
    }));
    
    // Second pass: adjust last item to ensure exact sum of 1.0
    const sumExceptLast = normalized.slice(0, -1).reduce((sum, item) => sum + item.probability, 0);
    normalized[normalized.length - 1].probability = 1.0 - sumExceptLast;
    
    // Ensure last probability is not negative
    if (normalized[normalized.length - 1].probability < 0) {
      normalized[normalized.length - 1].probability = 0;
    }
    
    return normalized;
  }, []);
  
  const handleAssetStakingChange = (
    asset: 'eth' | 'sol',
    field: keyof AssetStakingParams,
    value: number,
    isPercentage = false
  ) => {
    onChange({
      ...parameters,
      staking: {
        ...parameters.staking,
        [asset]: {
          ...parameters.staking[asset],
          [field]: isPercentage ? value / 100 : value,
        },
      },
    });
  };

  const handleRedemptionChange = (field: string, value: number) => {
    onChange({
      ...parameters,
      redemption: {
        ...parameters.redemption,
        [field]: value,
      },
    });
  };

  const handleFundDetailsChange = (field: keyof FundDetails, value: number) => {
    const newFundDetails = {
      ...fundDetails,
      [field]: value,
    };
    
    // Validate Current TD vs Cap TD
    if (newFundDetails.current_td > newFundDetails.cap_td) {
      setFundDetailsError('Current TD cannot exceed Cap TD');
      onValidationChange?.(false);
    } else {
      setFundDetailsError(null);
      onValidationChange?.(true);
    }
    
    onChange({
      ...parameters,
      fund_details: newFundDetails,
    });
  };
  
  // Check validation on mount and when fund details change
  useEffect(() => {
    if (fundDetails.current_td > fundDetails.cap_td) {
      setFundDetailsError('Current TD cannot exceed Cap TD');
      onValidationChange?.(false);
    } else {
      setFundDetailsError(null);
      onValidationChange?.(true);
    }
  }, [fundDetails.current_td, fundDetails.cap_td, onValidationChange]);

  // These functions are no longer needed as the RedemptionDistributionBuilder handles them internally

  return (
    <Stack spacing={3}>
      {/* Apply All Defaults Button */}
      <Box>
        <Button
          variant="outlined"
          size="small"
          onClick={() => {
            // Apply default market parameters with volatility conversion if needed
            const volatilitiesToApply = volatilityType === 'annual' 
              ? Object.entries(defaultMarketParams.volatilities).reduce(
                  (acc, [asset, vol]) => ({
                    ...acc,
                    [asset]: (vol ?? 0) * Math.sqrt(defaultMarketParams.trading_days_per_year ?? 252),
                  }),
                  {} as AssetVolatilities
                )
              : defaultMarketParams.volatilities;

            // Apply default redemption distribution (normalized)
            const defaultDistribution = [
              { probability: 0.667, size: 0.05 },
              { probability: 0.167, size: 0.10 },
              { probability: 0.111, size: 0.20 },
              { probability: 0.055, size: 0.30 },
            ];
            const normalizedDistribution = normalizeRedemptionDistribution(defaultDistribution);

            // Apply all defaults at once
            onChange({
              ...parameters,
              staking: {
                eth: {
                  staking_pct: 0.90,
                  unbonding_period_days: 10,
                  annual_yield: 0.03,
                  baseline_staking_pct: 0.70,
                },
                sol: {
                  staking_pct: 0.90,
                  unbonding_period_days: 2,
                  annual_yield: 0.073,
                  baseline_staking_pct: 0.70,
                },
              },
              redemption: {
                expected_redemptions_per_year: 18,
                distribution: normalizedDistribution,
              },
              market: {
                benchmark_weights: defaultBenchmarkWeights,
                volatilities: volatilitiesToApply,
                correlations: defaultMarketParams.correlations,
                trading_days_per_year: defaultMarketParams.trading_days_per_year,
              },
              fund_details: defaultFundDetails,
            });
          }}
          sx={glassStyles.buttonSubtle}
          fullWidth
        >
          Apply Default Configuration
        </Button>
      </Box>
      
      {/* Expand/Collapse All Button */}
      <Box sx={{ mb: 2 }}>
        <Button
          variant="outlined"
          size="small"
          onClick={toggleAllSections}
          startIcon={hasExpandedSection ? <ExpandLessIcon /> : <ExpandMoreIcon />}
          sx={glassStyles.buttonSubtle}
          fullWidth
        >
          {hasExpandedSection ? 'Collapse All' : 'Expand All'}
        </Button>
      </Box>

      {/* Fund Details */}
      <CollapsibleSection 
        title="Fund Details" 
        expanded={expandedSections.fundDetails}
        onToggle={() => toggleSection('fundDetails')}
      >
        <Box sx={{ mb: 2 }}>
          <Button
            variant="outlined"
            size="small"
            onClick={() => {
              onChange({
                ...parameters,
                fund_details: defaultFundDetails,
              });
            }}
            sx={glassStyles.buttonSubtle}
            fullWidth
          >
            Apply Default Fund Details
          </Button>
        </Box>
        
        <Stack spacing={2}>
          {/* NAV */}
          <TextField
            label="NAV"
            value={navInput.value}
            onChange={(e) => navInput.onChange(e.target.value)}
            type="number"
            InputProps={{
              startAdornment: <InputAdornment position="start">$</InputAdornment>,
              endAdornment: (
                <InputAdornment position="end">
                  <InfoTooltip
                    title="Fund's net asset value"
                    onDocumentClick={onDocumentClick}
                  />
                </InputAdornment>
              ),
            }}
            sx={glassStyles.input}
            size="small"
            fullWidth
          />

          {/* Current TD and Cap TD side by side */}
          <Box sx={{ display: 'flex', gap: 2 }}>
            <TextField
              label="Current TD"
              value={currentTdInput.value}
              onChange={(e) => currentTdInput.onChange(e.target.value)}
              type="number"
              error={!!fundDetailsError}
              helperText={fundDetailsError && 'Current TD > Cap TD'}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    %
                    <InfoTooltip
                      title="Current expected tracking difference"
                      onDocumentClick={onDocumentClick}
                    />
                  </InputAdornment>
                ),
              }}
              sx={{ ...glassStyles.input, flex: 1 }}
              size="small"
            />

            <TextField
              label="Cap TD"
              value={capTdInput.value}
              onChange={(e) => capTdInput.onChange(e.target.value)}
              type="number"
              error={!!fundDetailsError}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    %
                    <InfoTooltip
                      title="Tracking difference cap set by committee"
                      onDocumentClick={onDocumentClick}
                    />
                  </InputAdornment>
                ),
              }}
              sx={{ ...glassStyles.input, flex: 1 }}
              size="small"
            />
          </Box>
        </Stack>
      </CollapsibleSection>

      {/* Benchmark Weights */}
      <CollapsibleSection 
        title="Benchmark Weights" 
        expanded={expandedSections.benchmarkWeights}
        onToggle={() => toggleSection('benchmarkWeights')}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Typography variant="body2" color="text.secondary">
            Index benchmark allocations
          </Typography>
          <InfoTooltip
            title="Asset weights in the NCI-US index benchmark"
            description="These weights determine the portfolio's target allocations"
            documentLink={{
              path: 'two-asset-model-parameters.md',
              title: 'Model Parameters',
              section: 'benchmark-weights'
            }}
            onDocumentClick={onDocumentClick}
          />
        </Box>
        <Box sx={{ mb: 2 }}>
          <Button
            variant="outlined"
            size="small"
            onClick={() => {
              onChange({
                ...parameters,
                market: {
                  ...marketParams,
                  benchmark_weights: defaultBenchmarkWeights,
                },
              });
            }}
            sx={glassStyles.buttonSubtle}
            fullWidth
          >
            Apply NCI-US Default Weights
          </Button>
        </Box>
        
        <Stack spacing={2}>
          {Object.entries(marketParams.benchmark_weights).map(([asset, weight]) => {
            const assetColors: Record<string, string> = {
              btc: '#F7931A',
              eth: '#627EEA',
              xrp: '#00AAE4',
              sol: '#14F195',
              ada: '#0033AD',
              xlm: '#000000',
            };
            
            return (
              <Box key={asset}>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                  {asset.toUpperCase()}: {(weight * 100).toFixed(2)}%
                </Typography>
                <Slider
                  value={weight}
                  onChange={(_, value) => {
                    const newWeights = {
                      ...marketParams.benchmark_weights,
                      [asset]: value as number,
                    };
                    const normalizedWeights = normalizeBenchmarkWeights(newWeights);
                    onChange({
                      ...parameters,
                      market: {
                        ...marketParams,
                        benchmark_weights: normalizedWeights,
                      },
                    });
                  }}
                  min={0}
                  max={1}
                  step={0.0001}
                  sx={{ color: assetColors[asset] || '#6DAEFF' }}
                />
              </Box>
            );
          })}
          
          <Divider sx={{ my: 1, borderColor: 'rgba(109, 174, 255, 0.1)' }} />
          
          <Typography variant="body2" color="text.secondary">
            Total: {(
              Object.values(marketParams.benchmark_weights).reduce((sum, weight) => sum + weight, 0) * 100
            ).toFixed(1)}% (auto-normalized)
          </Typography>
        </Stack>
      </CollapsibleSection>

      {/* Market Parameters */}
      <CollapsibleSection 
        title="Market Parameters" 
        expanded={expandedSections.marketParameters}
        onToggle={() => toggleSection('marketParameters')}
      >
        <Stack spacing={3}>
            {/* Apply Default Button */}
          <Box sx={{ mb: 2 }}>
            <Button
              variant="outlined"
              size="small"
              onClick={() => {
                // Apply conversion if volatility type is annual
                const volatilitiesToApply = volatilityType === 'annual' 
                  ? Object.entries(defaultMarketParams.volatilities).reduce(
                      (acc, [asset, vol]) => ({
                        ...acc,
                        [asset]: (vol ?? 0) * Math.sqrt(defaultMarketParams.trading_days_per_year ?? 252),
                      }),
                      {} as AssetVolatilities
                    )
                  : defaultMarketParams.volatilities;

                onChange({
                  ...parameters,
                  market: {
                    ...marketParams,
                    volatilities: volatilitiesToApply,
                    correlations: defaultMarketParams.correlations,
                    trading_days_per_year: defaultMarketParams.trading_days_per_year,
                    benchmark_weights: marketParams.benchmark_weights, // Keep current benchmark weights
                  },
                });
              }}
              sx={glassStyles.buttonSubtle}
              fullWidth
            >
              Apply Default Market Parameters
            </Button>
          </Box>

          {/* Volatility Section */}
          <Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="subtitle2" color="text.secondary">
                Volatilities
              </Typography>
              <FormControlLabel
                control={
                  <Switch
                    checked={volatilityType === 'annual'}
                    onChange={(e) => {
                      const newType = e.target.checked ? 'annual' : 'daily';
                      const conversionFactor = newType === 'annual' ? Math.sqrt(252) : 1 / Math.sqrt(252);
                      
                      const newVolatilities = Object.entries(marketParams.volatilities).reduce(
                        (acc, [asset, vol]) => ({
                          ...acc,
                          [asset]: vol * conversionFactor,
                        }),
                        {} as AssetVolatilities
                      );

                      onChange({
                        ...parameters,
                        market: {
                          ...marketParams,
                          volatilities: newVolatilities,
                        },
                      });
                      setVolatilityType(newType);
                      onVolatilityTypeChange?.(newType);
                    }}
                    sx={{
                      '& .MuiSwitch-switchBase.Mui-checked': {
                        color: '#6DAEFF',
                      },
                      '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                        backgroundColor: '#6DAEFF',
                      },
                    }}
                  />
                }
                label={volatilityType === 'annual' ? 'Annual' : 'Daily'}
              />
            </Box>
            
            <Grid container spacing={2}>
              {Object.entries(marketParams.volatilities).map(([asset, vol]) => {
                // eslint-disable-next-line react-hooks/rules-of-hooks
                const volInput = useDebouncedNumericInput({
                  value: vol * 100,
                  onChange: (value) => {
                    onChange({
                      ...parameters,
                      market: {
                        ...marketParams,
                        volatilities: {
                          ...marketParams.volatilities,
                          [asset]: value / 100,
                        },
                      },
                    });
                  },
                  min: 0,
                  max: 100,
                  decimalPlaces: 1,
                });
                
                return (
                  <Grid item xs={6} key={asset}>
                    <TextField
                      label={asset.toUpperCase()}
                      type="number"
                      value={volInput.value}
                      onChange={(e) => volInput.onChange(e.target.value)}
                      InputProps={{
                        endAdornment: <InputAdornment position="end">%</InputAdornment>,
                      }}
                      sx={glassStyles.input}
                      fullWidth
                      size="small"
                    />
                  </Grid>
                );
              })}
            </Grid>
          </Box>
          
          <Divider sx={{ borderColor: 'rgba(109, 174, 255, 0.1)' }} />
          
          {/* Correlation Section */}
          <Box>
            <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 2 }}>
              Correlations
            </Typography>
            
            <Stack spacing={2}>
              {(() => {
                const btcEthInput = useDebouncedNumericInput({
                  value: marketParams.correlations.btc_eth,
                  onChange: (value) => {
                    onChange({
                      ...parameters,
                      market: {
                        ...marketParams,
                        correlations: {
                          ...marketParams.correlations,
                          btc_eth: value,
                        },
                      },
                    });
                  },
                  min: -1,
                  max: 1,
                  decimalPlaces: 2,
                });
                
                return (
                  <TextField
                    label="ρ(BTC, ETH)"
                    type="number"
                    value={btcEthInput.value}
                    onChange={(e) => btcEthInput.onChange(e.target.value)}
                    inputProps={{ min: -1, max: 1, step: 0.01 }}
                    sx={glassStyles.input}
                    fullWidth
                    size="small"
                  />
                );
              })()}
              
              {(() => {
                const btcExcludedInput = useDebouncedNumericInput({
                  value: marketParams.correlations.btc_excluded,
                  onChange: (value) => {
                    onChange({
                      ...parameters,
                      market: {
                        ...marketParams,
                        correlations: {
                          ...marketParams.correlations,
                          btc_excluded: value,
                        },
                      },
                    });
                  },
                  min: -1,
                  max: 1,
                  decimalPlaces: 2,
                });
                
                return (
                  <TextField
                    label="ρ(BTC, [XRP, SOL, ADA, XLM])"
                    type="number"
                    value={btcExcludedInput.value}
                    onChange={(e) => btcExcludedInput.onChange(e.target.value)}
                    inputProps={{ min: -1, max: 1, step: 0.01 }}
                    sx={glassStyles.input}
                    fullWidth
                    size="small"
                  />
                );
              })()}
              
              {(() => {
                const ethExcludedInput = useDebouncedNumericInput({
                  value: marketParams.correlations.eth_excluded,
                  onChange: (value) => {
                    onChange({
                      ...parameters,
                      market: {
                        ...marketParams,
                        correlations: {
                          ...marketParams.correlations,
                          eth_excluded: value,
                        },
                      },
                    });
                  },
                  min: -1,
                  max: 1,
                  decimalPlaces: 2,
                });
                
                return (
                  <TextField
                    label="ρ(ETH, [XRP, SOL, ADA, XLM])"
                    type="number"
                    value={ethExcludedInput.value}
                    onChange={(e) => ethExcludedInput.onChange(e.target.value)}
                    inputProps={{ min: -1, max: 1, step: 0.01 }}
                    sx={glassStyles.input}
                    fullWidth
                    size="small"
                  />
                );
              })()}
              
              {(() => {
                const withinExcludedInput = useDebouncedNumericInput({
                  value: marketParams.correlations.within_excluded,
                  onChange: (value) => {
                    onChange({
                      ...parameters,
                      market: {
                        ...marketParams,
                        correlations: {
                          ...marketParams.correlations,
                          within_excluded: value,
                        },
                      },
                    });
                  },
                  min: -1,
                  max: 1,
                  decimalPlaces: 2,
                });
                
                return (
                  <TextField
                    label="ρ(XRP, SOL, ADA, XLM)"
                    type="number"
                    value={withinExcludedInput.value}
                    onChange={(e) => withinExcludedInput.onChange(e.target.value)}
                    inputProps={{ min: -1, max: 1, step: 0.01 }}
                    sx={glassStyles.input}
                    fullWidth
                    size="small"
                  />
                );
              })()}
            </Stack>
          </Box>
        </Stack>
      </CollapsibleSection>

      {/* Staking Parameters */}
      <CollapsibleSection 
        title="Staking Parameters"
        expanded={expandedSections.stakingParameters}
        onToggle={() => toggleSection('stakingParameters')}
        headerContent={
          <Tooltip title="Automatically apply optimal staking percentages">
            <FormControlLabel
              control={
                <Switch
                  checked={autoFitToOptimal}
                  onChange={(e) => onAutoFitToOptimalChange?.(e.target.checked)}
                  disabled={!hasResults}
                  size="small"
                  sx={{
                    '& .MuiSwitch-switchBase.Mui-checked': {
                      color: '#6DAEFF',
                    },
                    '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                      backgroundColor: '#6DAEFF',
                    },
                  }}
                />
              }
              label="Auto-fit to optimal"
              labelPlacement="start"
              sx={{
                m: 0,
                '& .MuiFormControlLabel-label': {
                  fontSize: '0.875rem',
                  color: autoFitToOptimal ? '#6DAEFF' : 'rgba(255, 255, 255, 0.7)',
                  mr: 1,
                },
              }}
              onClick={(e) => e.stopPropagation()}
            />
          </Tooltip>
        }
      >
        {/* Apply Default Button */}
        <Box sx={{ mb: 2 }}>
          <Button
            variant="outlined"
            size="small"
            onClick={() => {
              onChange({
                ...parameters,
                staking: {
                  eth: {
                    staking_pct: 0.90,
                    unbonding_period_days: 10,
                    annual_yield: 0.03,
                    baseline_staking_pct: 0.70,
                  },
                  sol: {
                    staking_pct: 0.90,
                    unbonding_period_days: 2,
                    annual_yield: 0.073,
                    baseline_staking_pct: 0.70,
                  },
                },
              });
            }}
            sx={glassStyles.buttonSubtle}
            fullWidth
          >
            Apply Default Staking Parameters
          </Button>
        </Box>
        <AssetStakingSection 
          asset="eth" 
          color="#6DAEFF" 
          parameters={parameters}
          handleAssetStakingChange={handleAssetStakingChange}
          onDocumentClick={onDocumentClick}
          disabled={autoFitToOptimal}
        />
        <Divider sx={{ my: 3, borderColor: 'rgba(109, 174, 255, 0.1)' }} />
        <AssetStakingSection 
          asset="sol" 
          color="#D7E6FF" 
          parameters={parameters}
          handleAssetStakingChange={handleAssetStakingChange}
          onDocumentClick={onDocumentClick}
          disabled={autoFitToOptimal}
        />
      </CollapsibleSection>

      {/* Redemption Parameters */}
      <CollapsibleSection 
        title="Redemption Parameters" 
        expanded={expandedSections.redemptionParameters}
        onToggle={() => toggleSection('redemptionParameters')}
      >
        <Stack spacing={3}>
          {/* Apply Default Button */}
          <Box sx={{ mb: 2 }}>
            <Button
              variant="outlined"
              size="small"
              onClick={() => {
                const defaultDistribution = [
                  { probability: 0.667, size: 0.05 },
                  { probability: 0.167, size: 0.10 },
                  { probability: 0.111, size: 0.20 },
                  { probability: 0.055, size: 0.30 },
                ];
                const normalizedDistribution = normalizeRedemptionDistribution(defaultDistribution);
                onChange({
                  ...parameters,
                  redemption: {
                    expected_redemptions_per_year: 18,
                    distribution: normalizedDistribution,
                  },
                });
              }}
              sx={glassStyles.buttonSubtle}
              fullWidth
            >
              Apply Default Redemption Distribution
            </Button>
          </Box>

          {/* Expected Redemptions per Year */}
          <Box>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Typography variant="body2" color="text.secondary">
                Expected (Institutional) Redemptions per Year: {parameters.redemption.expected_redemptions_per_year.toFixed(1)}
              </Typography>
              <InfoTooltip
                title="Lambda (λ) - average number of institutional redemptions per year"
                description="Used in the Poisson process model for redemption frequency"
                documentLink={{
                  path: 'two-asset-model-parameters.md',
                  title: 'Model Parameters',
                  section: 'expected-number-of-institutional-redemptions'
                }}
                onDocumentClick={onDocumentClick}
              />
            </Box>
            <Slider
              value={parameters.redemption.expected_redemptions_per_year}
              onChange={(_, value) => handleRedemptionChange('expected_redemptions_per_year', value as number)}
              min={0}
              max={40}
              step={0.1}
              marks={[
                { value: 0, label: '0' },
                { value: 10, label: '10' },
                { value: 20, label: '20' },
                { value: 30, label: '30' },
                { value: 40, label: '40' },
              ]}
              sx={{
                color: '#6DAEFF',
                '& .MuiSlider-thumb': {
                  background: 'linear-gradient(135deg, #6DAEFF 0%, #4A94E6 100%)',
                },
              }}
            />
          </Box>
          
          <Divider sx={{ borderColor: 'rgba(109, 174, 255, 0.1)' }} />
          
          {/* Visual Distribution Builder */}
          <RedemptionDistributionBuilder
            distribution={parameters.redemption.distribution}
            expectedRedemptionsPerYear={parameters.redemption.expected_redemptions_per_year}
            onChange={(newDistribution) => {
              onChange({
                ...parameters,
                redemption: {
                  ...parameters.redemption,
                  distribution: newDistribution,
                },
              });
            }}
            onDocumentClick={onDocumentClick}
          />
        </Stack>
      </CollapsibleSection>
    </Stack>
  );
};