"""
FastAPI backend for Optimal Staking → Two-Asset Analytical Solution
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from typing import Union
import os
from pathlib import Path
from dotenv import load_dotenv
from models import CalculationRequest, CalculationResponse
from calculator_optimized import calculate_tracking_error
from warmup import warmup_numba_functions
import time

# Load environment variables from .env file
load_dotenv()

# Warmup Numba functions during startup
print('Starting application initialization...')
startup_time = time.time()
try:
    warmup_numba_functions()
except Exception as e:
    print(f'Warning: Numba warmup failed: {e}')
print(f'Initialization completed in {time.time() - startup_time:.2f}s')

app = FastAPI(
    title='Optimal Staking API',
    description='API for two-asset analytical solution for optimal staking',
    version='1.0.0',
)

# Create API router for all API endpoints
api_router = FastAPI()

# Configure CORS for development only
# In production, frontend and backend are served from same origin
if os.getenv('ENV') == 'development':
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['http://localhost:5173', 'http://127.0.0.1:5173'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )


@api_router.get('/')
def api_root():
    """API root endpoint with API information"""
    return {
        'message': 'Optimal Staking API',
        'endpoints': {
            'POST /api/calculate': 'Calculate tracking error with given parameters',
            'GET /api/health': 'Health check',
        },
    }


@api_router.post('/calculate', response_model=CalculationResponse)
def calculate(request: Union[CalculationRequest, dict]):
    """
    Calculate tracking error and net benefit analysis
    Supports both new and legacy request formats
    """
    try:
        return calculate_tracking_error(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@api_router.get('/health')
def health_check():
    """Health check endpoint"""
    return {'status': 'healthy'}


@api_router.get('/docs/{filename}', response_class=PlainTextResponse)
def get_document(filename: str):
    """
    Serve markdown documentation files
    """
    # Security: ensure filename doesn't contain path traversal
    if '..' in filename or '/' in filename or '\\' in filename:
        raise HTTPException(status_code=400, detail='Invalid filename')

    # Ensure filename ends with .md
    if not filename.endswith('.md'):
        raise HTTPException(status_code=400, detail='Only markdown files are allowed')

    # Path resolution based on environment
    if os.getenv('ENV') == 'development':
        docs_path = (
            Path(__file__).parent.parent / 'docs' / filename
        )  # Development: backend/../docs/
    else:
        docs_path = (
            Path(__file__).parent / 'docs' / filename
        )  # Production: docs at same level

    if not docs_path.exists():
        raise HTTPException(status_code=404, detail=f"Document '{filename}' not found")

    try:
        with open(docs_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Error reading document: {str(e)}')


# Mount API router under /api prefix
app.mount('/api', api_router)

# Serve static files (React build) from 'static' directory
static_path = Path(__file__).parent / 'static'
if static_path.exists():
    app.mount('/', StaticFiles(directory=str(static_path), html=True), name='static')
else:
    # Fallback for development or when static files not built yet
    @app.get('/')
    def read_index():
        return {
            'message': "Frontend not built. Run 'npm run build' in frontend directory."
        }


if __name__ == '__main__':
    import uvicorn

    # Get port from Railway environment variable, default to 8000 for local development
    port = int(os.getenv('PORT', 8000))
    uvicorn.run(app, host='0.0.0.0', port=port)
