# Simple Project Structure for Two-Asset Tracking Error Demo SPA

This document outlines a minimal project structure for an internal demonstration tool using `core/two_asset_discrete_te.py` as the backend calculation engine.

## Tech Stack
- **Backend**: Python FastAPI
- **Frontend**: React 18 + TypeScript + Vite + Material-UI

## Simplified Project Structure

```
optimal-staking-demo/
├── backend/
│   ├── main.py                    # FastAPI app with all endpoints
│   ├── models.py                  # Request/response Pydantic models
│   ├── calculator.py              # Wrapper around two_asset_discrete_te.py
│   ├── core/                      # Copy of existing core calculation files
│   │   └── two_asset_discrete_te.py
│   └── requirements.txt           # fastapi, uvicorn, numpy, scipy, pydantic
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx               # Main app component with all UI
│   │   ├── main.tsx              # Entry point with theme provider
│   │   ├── api.ts                # API client functions
│   │   ├── types.ts              # TypeScript interfaces
│   │   ├── theme.ts              # MUI theme with glassmorphism
│   │   ├── components/
│   │   │   ├── ParameterForm.tsx     # All input forms in glassmorphic card
│   │   │   ├── ResultsDisplay.tsx    # Results with glassmorphic charts
│   │   │   ├── PresetButtons.tsx     # Glassmorphic preset buttons
│   │   │   └── GlassCard.tsx         # Reusable glassmorphic card component
│   │   └── styles/
│   │       └── glassmorphism.ts  # Shared glassmorphism styles
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
│
├── README.md                      # Quick start instructions
└── .gitignore
```

## Implementation Details

### Backend (`main.py`)
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import CalculationRequest, CalculationResponse
from calculator import calculate_tracking_error

app = FastAPI(title="Staking TE Demo")

# Simple CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/calculate", response_model=CalculationResponse)
def calculate(request: CalculationRequest):
    return calculate_tracking_error(request)

@app.get("/presets")
def get_presets():
    return {
        "conservative": {"eth_staking_pct": 0.80, "sol_staking_pct": 0.80},
        "optimal": {"eth_staking_pct": 0.93, "sol_staking_pct": 0.93},
        "aggressive": {"eth_staking_pct": 0.95, "sol_staking_pct": 0.95}
    }
```

### Frontend UI Design Specifications

#### Material-UI Setup
```typescript
// package.json dependencies
{
  "dependencies": {
    "@mui/material": "^5.x",
    "@emotion/react": "^11.x",
    "@emotion/styled": "^11.x",
    "@mui/icons-material": "^5.x",
    "recharts": "^2.x"  // For charts with glassmorphism
  }
}
```

#### Glassmorphism Theme (`theme.ts`)
```typescript
import { createTheme } from '@mui/material/styles';

export const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#8B5CF6',
      light: '#A78BFA',
      dark: '#7C3AED',
    },
    background: {
      default: '#0F0F1E',
      paper: 'rgba(255, 255, 255, 0.05)',
    },
  },
  components: {
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
        },
      },
    },
  },
});
```

#### Glassmorphism Styles (`styles/glassmorphism.ts`)
```typescript
export const glassStyles = {
  card: {
    background: 'rgba(255, 255, 255, 0.05)',
    backdropFilter: 'blur(10px)',
    WebkitBackdropFilter: 'blur(10px)',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    borderRadius: '16px',
    boxShadow: '0 8px 32px 0 rgba(31, 38, 135, 0.37)',
    transition: 'all 0.3s ease',
    '&:hover': {
      transform: 'translateY(-2px)',
      boxShadow: '0 12px 40px 0 rgba(31, 38, 135, 0.45)',
      border: '1px solid rgba(255, 255, 255, 0.2)',
    },
  },
  input: {
    '& .MuiOutlinedInput-root': {
      background: 'rgba(255, 255, 255, 0.05)',
      backdropFilter: 'blur(5px)',
      borderRadius: '8px',
      '& fieldset': {
        borderColor: 'rgba(255, 255, 255, 0.1)',
      },
      '&:hover fieldset': {
        borderColor: 'rgba(255, 255, 255, 0.2)',
      },
    },
  },
  button: {
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    backdropFilter: 'blur(10px)',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    transition: 'all 0.3s ease',
    '&:hover': {
      transform: 'translateY(-1px)',
      boxShadow: '0 4px 20px 0 rgba(102, 126, 234, 0.4)',
    },
  },
  gradientText: {
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    backgroundClip: 'text',
    textFillColor: 'transparent',
  },
};
```

#### App Layout (`App.tsx`)
- Grid layout with glassmorphic cards
- Parameter inputs on the left (4 columns)
- Results display on the right (8 columns)
- Dark gradient background with floating glass elements
- Smooth animations on all interactions

#### Component Features
All components implement:
- **Backdrop blur effects**: 10px blur for cards, 5px for inputs
- **Semi-transparent backgrounds**: rgba(255, 255, 255, 0.05)
- **Subtle borders**: 1px solid rgba(255, 255, 255, 0.1)
- **Gradient accents**: Purple to pink gradients for buttons and text
- **Dark mode**: Deep purple/black background (#0F0F1E)
- **Responsive design**: Material-UI Grid system
- **Hover animations**: Elevation and glow effects

### Running the Application

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

### Example Component (`GlassCard.tsx`)
```typescript
import { Paper, PaperProps } from '@mui/material';
import { glassStyles } from '../styles/glassmorphism';

export const GlassCard: React.FC<PaperProps> = ({ children, sx, ...props }) => {
  return (
    <Paper sx={{ ...glassStyles.card, ...sx }} elevation={0} {...props}>
      {children}
    </Paper>
  );
};
```

### Example Results Display with Glassmorphism
```typescript
import { Box, Typography } from '@mui/material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { GlassCard } from './GlassCard';
import { glassStyles } from '../styles/glassmorphism';

export const ResultsDisplay: React.FC<{ data: any }> = ({ data }) => {
  return (
    <GlassCard>
      <Box p={3}>
        <Typography variant="h5" sx={glassStyles.gradientText} gutterBottom>
          Tracking Error Analysis
        </Typography>
        <Typography variant="h3" color="primary.light">
          {(data.tracking_error * 100).toFixed(2)}%
        </Typography>
        
        <Box mt={4} height={300}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data.sensitivity_data}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis dataKey="staking" stroke="rgba(255,255,255,0.5)" />
              <YAxis stroke="rgba(255,255,255,0.5)" />
              <Tooltip 
                contentStyle={{
                  background: 'rgba(0,0,0,0.8)',
                  border: '1px solid rgba(255,255,255,0.2)',
                  borderRadius: '8px',
                  backdropFilter: 'blur(10px)'
                }}
              />
              <Line 
                type="monotone" 
                dataKey="te" 
                stroke="#8B5CF6" 
                strokeWidth={2}
                dot={{ fill: '#A78BFA', r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </Box>
      </Box>
    </GlassCard>
  );
};
```

## Key Features

1. **Single File Backend**: All API logic in `main.py`
2. **Beautiful UI**: Material-UI with custom glassmorphism theme
3. **No Authentication**: Internal tool, runs locally
4. **No Database**: All calculations are stateless
5. **Simple State Management**: React's useState with Material-UI
6. **Glassmorphism Styling**: Modern glass-like effects throughout
7. **Dark Mode**: Built-in dark theme with purple accents
8. **Responsive Design**: Works on desktop and tablet screens

This structure provides a visually appealing demo tool that can be implemented quickly while maintaining a professional, modern appearance.