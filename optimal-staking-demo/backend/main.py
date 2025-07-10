"""
FastAPI backend for Optimal Staking → Two-Asset Analytical Solution
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from typing import Union
import os
from pathlib import Path
from models import (
    CalculationRequest, 
    CalculationResponse
)
from calculator_optimized import calculate_tracking_error

app = FastAPI(
    title="Optimal Staking API",
    description="API for two-asset analytical solution for optimal staking",
    version="1.0.0"
)

# Configure CORS for both development and production
# Get frontend URL from environment variable, with fallback for local development
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
allowed_origins = [frontend_url]

# Add localhost for development if not already included
if "localhost" not in frontend_url and "127.0.0.1" not in frontend_url:
    allowed_origins.extend(["http://localhost:5173", "http://127.0.0.1:5173"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "message": "Optimal Staking API",
        "endpoints": {
            "POST /calculate": "Calculate tracking error with given parameters",
            "GET /health": "Health check"
        }
    }


@app.post("/calculate", response_model=CalculationResponse)
def calculate(request: Union[CalculationRequest, dict]):
    """
    Calculate tracking error and net benefit analysis
    Supports both new and legacy request formats
    """
    try:
        return calculate_tracking_error(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/docs/{filename}", response_class=PlainTextResponse)
def get_document(filename: str):
    """
    Serve markdown documentation files
    """
    # Security: ensure filename doesn't contain path traversal
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    # Ensure filename ends with .md
    if not filename.endswith(".md"):
        raise HTTPException(status_code=400, detail="Only markdown files are allowed")
    
    # Path to docs directory (two levels up from backend)
    docs_path = Path(__file__).parent.parent.parent / "docs" / filename
    
    if not docs_path.exists():
        raise HTTPException(status_code=404, detail=f"Document '{filename}' not found")
    
    try:
        with open(docs_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading document: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    # Get port from Railway environment variable, default to 8000 for local development
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)