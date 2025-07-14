# Staking Tracking Error Demo

A high-performance web application for analyzing two-asset tracking error with staking parameters. This tool provides real-time calculations and interactive visualizations to explore the trade-offs between staking yields and tracking error for ETH and SOL assets in portfolios tracking the Nasdaq Crypto US (NCI-US) index.

## Features

- **⚡ Lightning-Fast Performance**: Sub-100ms response times through Numba JIT optimization (30x speedup)
- **🎨 Beautiful UI**: Modern glassmorphism design with dark theme and gradient accents
- **📊 Interactive Visualizations**: 
  - Real-time 2D sensitivity heatmaps (31x31 grid)
  - Tracking error decomposition charts
  - Yield vs tracking error trade-off analysis
  - Redemption distribution builder
- **🧮 Advanced Mathematics**: Implements closed-form analytical tracking error formula with threshold effects
- **📱 Responsive Design**: Collapsible sidebar with intuitive parameter controls
- **📚 Built-in Documentation**: Integrated markdown viewer for mathematical concepts

## Tech Stack

- **Backend**: Python FastAPI with Numba JIT compilation
- **Frontend**: React 18 + TypeScript + Vite + Material-UI
- **Performance**: Numba @jit optimization with pre-compilation warmup
- **Deployment**: Docker + Railway.app ready
- **Styling**: Glassmorphism design with custom Material-UI theme
- **Charts**: Recharts with custom styling for financial visualizations

## Quick Start

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

The API will be available at http://localhost:8000

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The application will be available at http://localhost:5173

## Docker Deployment (Recommended)

Build and run the unified container that serves both frontend and backend:

```bash
cd optimal-staking-demo
docker build -t staking-demo .
docker run -p 8000:8000 staking-demo
```

The application will be available at http://localhost:8000

## API Endpoints

- `POST /api/calculate` - Calculate tracking error with given parameters
  - Handles two-asset staking calculations
  - Returns tracking error decomposition and net benefits
  - Response time: <100ms (optimized with Numba)
- `GET /api/health` - Health check endpoint
- `GET /api/docs/{filename}` - Serve mathematical documentation

## Project Structure

```
optimal-staking-demo/
├── backend/
│   ├── main.py                    # FastAPI application with docs serving
│   ├── models.py                  # Pydantic models for type validation
│   ├── calculator.py              # Basic calculation wrapper
│   ├── calculator_optimized.py    # Numba-optimized calculations
│   ├── warmup.py                  # JIT pre-compilation script
│   ├── test_performance.py        # Performance benchmarking suite
│   ├── core/
│   │   ├── two_asset_discrete_te.py    # Core TE calculations
│   │   └── optimized_calculator.py     # Numba-decorated functions
│   └── docs/                      # Mathematical documentation
├── frontend/
│   ├── src/
│   │   ├── components/            # React components
│   │   │   ├── ParameterForm.tsx
│   │   │   ├── ResultsDisplay.tsx
│   │   │   ├── RedemptionDistributionBuilder.tsx
│   │   │   └── GlassCard.tsx
│   │   ├── hooks/                 # Custom React hooks
│   │   ├── styles/                # Glassmorphism styles
│   │   ├── App.tsx                # Main application
│   │   └── api.ts                 # Backend API client
│   └── public/
│       └── hashdex-logo.svg       # Brand assets
├── Dockerfile                     # Multi-stage build configuration
├── railway.json                   # Railway deployment config
├── DEPLOYMENT.md                  # Deployment guide
└── PERFORMANCE_IMPROVEMENTS.md    # Optimization documentation
```

## Development

1. Start the backend server (port 8000)
2. Start the frontend dev server (port 5173)
3. The frontend proxies API requests to the backend

## Performance Optimization

The application achieves **30x performance improvement** (from ~3s to <100ms) through:

### Numba JIT Compilation
- Pre-compilation of all mathematical functions on startup
- Explicit type signatures for optimal machine code generation
- Persistent cache directory for compiled functions
- Contiguous array operations for covariance matrices

### Optimization Strategies
```python
# Example of Numba optimization
@jit(nopython=True, cache=True)
def calculate_variance_optimized(redemption: float, tau: float, base_k: float) -> float:
    """Variance with threshold effects - optimized for Numba."""
    if redemption <= tau:
        return 0.0
    return base_k * (redemption - tau) ** 2
```

### Performance Benchmarks
- Cold start elimination: First request completes in <100ms
- Sensitivity analysis: 31x31 grid calculated in ~50ms
- API response time: p50=45ms, p95=85ms, p99=95ms

Run performance tests:
```bash
cd backend
python test_performance.py
```

## Mathematical Model

The application implements the **Two-Asset Analytical Tracking Error Formula**:

```
TE = √[λ × (d_short × E[Var_full] + (d_long - d_short) × E[Var_partial])]
```

### Key Mathematical Concepts

1. **Non-Linear Threshold Effects**
   - Variance = base_k × max(0, redemption - threshold)²
   - Creates "safety buffer" where small redemptions have zero impact
   - Threshold = 1 - staking_percentage

2. **Time-Segmented Variance**
   - Days 1-2: Both ETH and SOL overweighted (Var_full)
   - Days 3-10: Only ETH overweighted (Var_partial)
   - Accounts for different unbonding periods (ETH: 10 days, SOL: 2 days)

3. **Correlation Cost**
   - Staking multiple assets creates competing constraints
   - k_ETH_SOL > 0 means the cross-term increases tracking error
   - Each constraint reduces degrees of freedom for optimization

4. **Market Parameters**
   - Benchmark: NCI-US index weights and correlations
   - Base k-factor ≈ 0.000011 (derived from Lagrange optimization)
   - Stochastic redemption model with compound Poisson process

For complete mathematical derivations, see:
- `docs/two-asset-tracking-error-formula.md`
- `docs/correlation-cost-explanation.md`
- Parent repository documentation

## Production Deployment

### Railway.app Deployment

The application is configured for one-click deployment to Railway:

1. Fork the repository
2. Connect to Railway
3. Deploy using the provided `railway.json` configuration

Features:
- Automatic builds from Git pushes
- Health checks and auto-restart
- Persistent Numba cache across deployments
- Environment-based configuration

See `DEPLOYMENT.md` for detailed Railway deployment instructions.

### Environment Variables

- `PORT`: Server port (default: 8000)
- `NUMBA_CACHE_DIR`: Persistent cache location
- `PYTHONUNBUFFERED`: Enable real-time logging

## Key Parameters

- **Staking Percentages**: 0-100% for ETH and SOL
- **Annual Staking Yields**: ETH: 3%, SOL: 7.3% (configurable)
- **Unbonding Periods**: ETH: 10 days, SOL: 2 days
- **Redemption Distribution**: Empirical distribution from historical data
  - 5% redemptions: 67% probability
  - 10% redemptions: 17% probability
  - 20% redemptions: 11% probability
  - 30% redemptions: 6% probability
- **Market Structure**: Based on NCI-US index composition