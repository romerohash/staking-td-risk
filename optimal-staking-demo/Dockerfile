# Multi-stage build for serving React frontend and FastAPI backend together

# Stage 1: Build React frontend
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci

# Copy frontend source code
COPY frontend/ ./

# Build the React app
RUN npm run build

# Stage 2: Python backend with built frontend
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application code
COPY backend/ ./

# Copy built frontend from the builder stage to the static directory
COPY --from=frontend-builder /app/frontend/dist ./static

# Copy docs directory to the correct location
COPY docs/ ./docs/

# Create Numba cache directory
RUN mkdir -p /app/numba_cache && chmod 777 /app/numba_cache

# Set Numba environment variables for production
ENV NUMBA_CACHE_DIR=/app/numba_cache
ENV NUMBA_CPU_NAME=generic
ENV NUMBA_DISABLE_PERFORMANCE_WARNINGS=1
ENV NUMBA_THREADING_LAYER=workqueue
ENV NUMBA_OPT=3

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:${PORT:-8000}/api/health')" || exit 1

# Start the application with optimized settings
# Railway will set the PORT environment variable
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1 --loop uvloop --timeout-graceful-shutdown 30"]