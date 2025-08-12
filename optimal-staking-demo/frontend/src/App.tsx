import { useState, useCallback, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Button,
  Snackbar,
  Alert,
  AppBar,
  Toolbar,
  IconButton,
  Drawer,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Switch,
  FormControlLabel,
  Tooltip,
} from '@mui/material';
import CalculateIcon from '@mui/icons-material/Calculate';
import GitHubIcon from '@mui/icons-material/GitHub';
import MenuIcon from '@mui/icons-material/Menu';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import DescriptionIcon from '@mui/icons-material/Description';
import ArrowDropDownIcon from '@mui/icons-material/ArrowDropDown';
import { CalculationRequest, CalculationResponse } from './types';
import { calculateTrackingError } from './api';
import { ParameterForm } from './components/ParameterForm';
import { ResultsDisplay } from './components/ResultsDisplay';
import { MarkdownViewer } from './components/MarkdownViewer';
import { glassStyles } from './styles/glassmorphism';
import { useDebouncedCalculation } from './hooks/useDebouncedCalculation';

const DRAWER_WIDTH = 520;

function App() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<CalculationResponse | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [volatilityType, setVolatilityType] = useState<'daily' | 'annual'>('daily');
  const [documentsAnchorEl, setDocumentsAnchorEl] = useState<null | HTMLElement>(null);
  const [markdownViewerOpen, setMarkdownViewerOpen] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState<{ path: string; title: string } | null>(null);
  const [autoCalculate, setAutoCalculate] = useState(true);
  const [isFormValid, setIsFormValid] = useState(true);
  const [autoFitToOptimal, setAutoFitToOptimal] = useState(false);
  const [parameters, setParameters] = useState<CalculationRequest>({
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
      distribution: [
        { probability: 0.667, size: 0.05 },
        { probability: 0.167, size: 0.10 },
        { probability: 0.111, size: 0.20 },
        { probability: 0.055, size: 0.30 },
      ],
    },
    fund_details: {
      nav: 500000000,  // $500 million
      current_td: 0.0143,  // 1.43%
      cap_td: 0.015,  // 1.5%
    },
  });

  const documentItems = [
    { name: 'Analytical Tracking Error Formula', path: 'analytical-tracking-error-formula.md' },
    { name: 'Tracking Error Time Window Invariance', path: 'tracking-error-time-window-invariance.md' },
    { name: 'Two-Asset Tracking Error Formula', path: 'two-asset-tracking-error-formula.md' },
    { name: 'Staking Benefit Formulation', path: 'staking-benefit-formulation.md' },
    { name: 'Two-Asset Model Parameters', path: 'two-asset-model-parameters.md' },
  ];

  const handleDocumentsClick = (event: React.MouseEvent<HTMLElement>) => {
    setDocumentsAnchorEl(event.currentTarget);
  };

  const handleDocumentsClose = () => {
    setDocumentsAnchorEl(null);
  };

  const handleDocumentClick = (path: string, title: string) => {
    setSelectedDocument({ path, title });
    setMarkdownViewerOpen(true);
    handleDocumentsClose();
  };

  const handleParametersChange = useCallback((newParams: CalculationRequest) => {
    setParameters(newParams);
  }, []);

  const handleCalculate = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      // Convert annual volatilities to daily if needed
      let requestParams = parameters;
      if (volatilityType === 'annual' && parameters.market) {
        const sqrtTradingDays = Math.sqrt(parameters.market.trading_days_per_year || 252);
        requestParams = {
          ...parameters,
          market: {
            ...parameters.market,
            volatilities: {
              btc: parameters.market.volatilities.btc / sqrtTradingDays,
              eth: parameters.market.volatilities.eth / sqrtTradingDays,
              xrp: parameters.market.volatilities.xrp / sqrtTradingDays,
              sol: parameters.market.volatilities.sol / sqrtTradingDays,
              ada: parameters.market.volatilities.ada / sqrtTradingDays,
              link: parameters.market.volatilities.link / sqrtTradingDays,
              xlm: parameters.market.volatilities.xlm / sqrtTradingDays,
              ltc: parameters.market.volatilities.ltc / sqrtTradingDays,
              uni: parameters.market.volatilities.uni / sqrtTradingDays,
            },
          },
        };
      }
      const response = await calculateTrackingError(requestParams);
      setResults(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  }, [parameters, volatilityType]);

  // Automatically recalculate when parameters change
  useDebouncedCalculation({
    parameters,
    onCalculate: handleCalculate,
    delay: 250, // Reduced from 500ms for more responsive updates while still preventing API spam
    enabled: results !== null && autoCalculate && isFormValid, // Only auto-calculate after initial manual calculation, if enabled, and if form is valid
  });

  // Apply optimal staking levels when auto-fit is enabled
  useEffect(() => {
    if (autoFitToOptimal && results?.optimal_staking_levels) {
      const currentEth = parameters.staking.eth.staking_pct;
      const currentSol = parameters.staking.sol.staking_pct;
      const optimalEth = results.optimal_staking_levels.eth;
      const optimalSol = results.optimal_staking_levels.sol;
      
      // Only update if values are different (with tolerance for floating point)
      // This prevents infinite loops when auto-calculate is also enabled
      const tolerance = 0.0001;
      if (Math.abs(currentEth - optimalEth) > tolerance || 
          Math.abs(currentSol - optimalSol) > tolerance) {
        setParameters(prev => ({
          ...prev,
          staking: {
            ...prev.staking,
            eth: {
              ...prev.staking.eth,
              staking_pct: optimalEth,
            },
            sol: {
              ...prev.staking.sol,
              staking_pct: optimalSol,
            },
          },
        }));
      }
    }
  }, [autoFitToOptimal, results?.optimal_staking_levels, parameters.staking.eth.staking_pct, parameters.staking.sol.staking_pct]);

  return (
    <>
      {/* Background gradient */}
      <Box sx={glassStyles.backgroundGradient} />
      
      {/* App Bar */}
      <AppBar position="fixed" sx={{ 
        background: 'rgba(255, 255, 255, 0.05)', 
        backdropFilter: 'blur(10px)',
        WebkitBackdropFilter: 'blur(10px)',
        borderBottom: '1px solid rgba(109, 174, 255, 0.15)',
        boxShadow: 'none',
        zIndex: (theme) => theme.zIndex.drawer + 1,
      }}>
        <Toolbar sx={{ minHeight: '56px !important', height: '56px' }}>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            edge="start"
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" sx={{ flexGrow: 1, display: 'flex', alignItems: 'center', ...glassStyles.gradientText }}>
            <Box
              component="img"
              src="/hashdex-logo.svg"
              alt="Hashdex"
              sx={{
                height: 32,
                width: 'auto',
                mr: 2,
                filter: 'brightness(0) saturate(100%) invert(77%) sepia(23%) saturate(1076%) hue-rotate(175deg) brightness(100%) contrast(101%)',
                opacity: 0.9,
                transition: 'all 0.3s ease',
                '&:hover': {
                  opacity: 1,
                  filter: 'brightness(0) saturate(100%) invert(77%) sepia(23%) saturate(1076%) hue-rotate(175deg) brightness(110%) contrast(101%)',
                }
              }}
            />
            <Box component="span" sx={{ fontWeight: 700 }}>
              Optimal Staking →
            </Box>
            {' '}
            <Box component="span" sx={{ fontWeight: 400 }}>
              Two-Asset Analytical Solution
            </Box>
          </Typography>
          <Button
            color="inherit"
            onClick={handleDocumentsClick}
            startIcon={<DescriptionIcon />}
            endIcon={<ArrowDropDownIcon />}
            sx={{
              mr: 2,
              background: 'rgba(109, 174, 255, 0.1)',
              backdropFilter: 'blur(10px)',
              WebkitBackdropFilter: 'blur(10px)',
              border: '1px solid rgba(109, 174, 255, 0.2)',
              borderRadius: '8px',
              '&:hover': {
                background: 'rgba(109, 174, 255, 0.15)',
                border: '1px solid rgba(109, 174, 255, 0.3)',
              },
            }}
          >
            Documents
          </Button>
          <IconButton 
            color="inherit" 
            href="https://github.com/hashdex/staking-td-risk"
            target="_blank"
          >
            <GitHubIcon />
          </IconButton>
        </Toolbar>
      </AppBar>

      {/* Documents Menu */}
      <Menu
        anchorEl={documentsAnchorEl}
        open={Boolean(documentsAnchorEl)}
        onClose={handleDocumentsClose}
        sx={{
          '& .MuiPaper-root': {
            background: 'rgba(29, 41, 57, 0.95)',
            backdropFilter: 'blur(10px)',
            WebkitBackdropFilter: 'blur(10px)',
            border: '1px solid rgba(109, 174, 255, 0.2)',
            borderRadius: '8px',
            boxShadow: '0 8px 32px 0 rgba(29, 41, 57, 0.37)',
            mt: 1,
          },
        }}
      >
        {documentItems.map((doc) => (
          <MenuItem
            key={doc.path}
            onClick={() => handleDocumentClick(doc.path, doc.name)}
            sx={{
              color: 'rgba(255, 255, 255, 0.9)',
              '&:hover': {
                background: 'rgba(109, 174, 255, 0.1)',
              },
            }}
          >
            <ListItemIcon>
              <DescriptionIcon fontSize="small" sx={{ color: '#6DAEFF' }} />
            </ListItemIcon>
            <ListItemText primary={doc.name} />
          </MenuItem>
        ))}
      </Menu>

      {/* Sidebar */}
      <Drawer
        variant="persistent"
        anchor="left"
        open={sidebarOpen}
        sx={{
          width: sidebarOpen ? DRAWER_WIDTH : 0,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: DRAWER_WIDTH,
            boxSizing: 'border-box',
            background: 'rgba(29, 41, 57, 0.85)',
            backdropFilter: 'blur(10px)',
            WebkitBackdropFilter: 'blur(10px)',
            borderRight: '1px solid rgba(109, 174, 255, 0.15)',
            transition: 'transform 0.3s ease-in-out',
            transform: sidebarOpen ? 'translateX(0)' : `translateX(-${DRAWER_WIDTH}px)`,
          },
        }}
      >
        <Box sx={{ 
          display: 'flex', 
          flexDirection: 'column', 
          height: '100vh',
          position: 'relative'
        }}>
          <Box sx={{ p: 3, pt: 11, overflowY: 'auto', flex: 1, pb: 10 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
              <Typography variant="h5" sx={glassStyles.gradientText}>
                Configuration
              </Typography>
              <IconButton onClick={() => setSidebarOpen(false)} size="small">
                <ChevronLeftIcon />
              </IconButton>
            </Box>
            
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Adjust parameters to analyze tracking error / net benefits trade-off
            </Typography>
            
            <ParameterForm
              parameters={parameters}
              onChange={handleParametersChange}
              onVolatilityTypeChange={setVolatilityType}
              onDocumentClick={handleDocumentClick}
              onValidationChange={setIsFormValid}
              autoFitToOptimal={autoFitToOptimal}
              onAutoFitToOptimalChange={setAutoFitToOptimal}
              hasResults={results !== null}
            />
          </Box>
          
          {/* Persistent Calculate Button */}
          <Box sx={{ 
            position: 'absolute',
            bottom: 0,
            left: 0,
            right: 0,
            p: 1.5,
            background: 'linear-gradient(to top, rgba(29, 41, 57, 0.95) 0%, rgba(29, 41, 57, 0.85) 70%, transparent 100%)',
            backdropFilter: 'blur(10px)',
            WebkitBackdropFilter: 'blur(10px)',
            borderTop: '1px solid rgba(109, 174, 255, 0.1)',
          }}>
            <Box sx={{ display: 'flex', flexDirection: 'row', gap: 1.5, alignItems: 'center' }}>
              <Button
                variant="contained"
                size="large"
                onClick={handleCalculate}
                disabled={loading || !isFormValid}
                startIcon={<CalculateIcon />}
                sx={{ 
                  ...glassStyles.button,
                  py: 0.75,
                  px: 3,
                  fontSize: '1rem',
                  boxShadow: '0 4px 20px 0 rgba(109, 174, 255, 0.3)',
                  flex: 1,
                }}
              >
                {loading && !autoCalculate ? 'Calculating...' : 'Calculate'}
              </Button>
              <Tooltip title="Automatically recalculate when parameters change" placement="top">
                <FormControlLabel
                  control={
                    <Switch
                      checked={autoCalculate}
                      onChange={(e) => setAutoCalculate(e.target.checked)}
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
                  label="Auto"
                  labelPlacement="end"
                  sx={{ 
                    color: 'rgba(255, 255, 255, 0.7)',
                    m: 0,
                    flexShrink: 0,
                    '& .MuiFormControlLabel-label': {
                      fontSize: '0.875rem',
                      ml: 0.5,
                    },
                  }}
                />
              </Tooltip>
            </Box>
          </Box>
        </Box>
      </Drawer>

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          marginLeft: sidebarOpen ? `${DRAWER_WIDTH}px` : 0,
          transition: 'margin 0.3s ease-in-out',
          mt: 7,
          willChange: 'margin-left',
          position: 'relative',
          zIndex: 1,
        }}
      >
        <Container maxWidth={false}>
          <ResultsDisplay results={results} loading={loading} autoCalculate={autoCalculate} onDocumentClick={handleDocumentClick} />
        </Container>
      </Box>

      {/* Error Snackbar */}
      <Snackbar
        open={!!error}
        autoHideDuration={6000}
        onClose={() => setError(null)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert
          onClose={() => setError(null)}
          severity="error"
          sx={{ 
            ...glassStyles.card,
            background: 'rgba(239, 68, 68, 0.1)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
          }}
        >
          {error}
        </Alert>
      </Snackbar>

      {/* Markdown Viewer */}
      <MarkdownViewer
        open={markdownViewerOpen}
        onClose={() => setMarkdownViewerOpen(false)}
        documentPath={selectedDocument?.path || null}
        documentTitle={selectedDocument?.title || ''}
      />
    </>
  );
}

export default App;