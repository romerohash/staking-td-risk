# Staking Tracking Error Demo

A modern web application for analyzing two-asset tracking error with staking parameters. This tool helps visualize the trade-offs between staking yields and tracking error for ETH and SOL assets.

## Features

- **Interactive Parameter Adjustment**: Real-time sliders for staking percentages
- **Beautiful Visualizations**: Glassmorphism UI with interactive charts
- **Comprehensive Analysis**: Tracking error decomposition, yield benefits, and sensitivity analysis
- **Dark Mode**: Modern dark theme with gradient accents

## Tech Stack

- **Backend**: Python FastAPI
- **Frontend**: React 18 + TypeScript + Vite + Material-UI
- **Styling**: Glassmorphism design with custom theme
- **Charts**: Recharts with custom styling

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

## API Endpoints

- `POST /calculate` - Calculate tracking error with given parameters
- `GET /health` - Health check

## Project Structure

```
optimal-staking-demo/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── models.py            # Pydantic models
│   ├── calculator.py        # Wrapper for calculations
│   └── core/                # Core calculation engine
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── styles/          # Glassmorphism styles
│   │   ├── App.tsx          # Main application
│   │   └── api.ts           # API client
│   └── package.json
└── README.md
```

## Development

1. Start the backend server (port 8000)
2. Start the frontend dev server (port 5173)
3. The frontend proxies API requests to the backend

## Key Parameters

- **Staking Percentages**: 0-100% for ETH and SOL
- **Annual Staking Yield**: Expected yield from staking
- **Baseline Staking**: Reference level for benefit calculations
- **Redemption Distribution**: Historical redemption patterns

## Mathematical Model

The application implements the Two-Asset Tracking Error Formula with:
- Non-linear threshold effects from staking-induced illiquidity
- Time-segmented variance for different unbonding periods
- Correlation cost analysis between ETH and SOL constraints

For detailed mathematical documentation, see the parent repository.