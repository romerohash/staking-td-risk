# Performance Improvements for Optimal Staking Demo

## Problem
The `/api/calculate` endpoint was experiencing 300-400ms response times on Railway.app, significantly slower than local development.

## Root Cause Analysis
1. **Numba JIT Cold Starts**: The primary bottleneck was Numba JIT compilation happening on each cold container start
2. **Railway Scale-to-Zero**: Containers were frequently cold due to automatic shutdown after inactivity
3. **Large Computation Grid**: 2D sensitivity analysis was computing 961 points (31x31 grid)

## Implemented Optimizations

### 1. Numba JIT Warmup (warmup.py)
- Created warmup script that pre-compiles all Numba functions during container startup
- Triggers compilation with representative data matching production workloads
- Integrated into main.py startup sequence

### 2. Eager Compilation with Type Signatures
- Added explicit type signatures to all Numba functions
- Enables immediate compilation instead of lazy JIT
- Examples:
  ```python
  @jit("float64[:](float64[:], float64[:], ...)", nopython=True, cache=True, fastmath=True)
  ```

### 3. Docker Configuration
- Created persistent Numba cache directory: `/app/numba_cache`
- Set environment variables for optimal Numba performance:
  - `NUMBA_CPU_NAME=generic` for cloud portability
  - `NUMBA_OPT=3` for maximum optimization
  - `NUMBA_CACHE_DIR=/app/numba_cache` for persistent caching

### 4. Computation Grid
- Maintained full 31x31 grid (961 points) for 2D sensitivity analysis
- Vectorized calculations ensure fast computation despite large grid
- Numba JIT optimization handles the computational load efficiently

### 5. Railway Configuration (railway.json)
- Disabled scale-to-zero with `"sleepApplication": false`
- Ensures containers stay warm in production
- Configured health checks and restart policies

### 6. Uvicorn Optimization
- Added `--loop uvloop` for faster async event loop
- Single worker process to maximize Numba cache hits
- Graceful shutdown timeout for clean container restarts

## Expected Results
- **First request (cold start)**: ~100-150ms (down from 300-400ms)
- **Subsequent requests**: <50ms
- **Memory usage**: Slightly higher due to Numba cache
- **CPU usage**: Lower after initial compilation

## Testing
Use the included `test_performance.py` script:
```bash
python test_performance.py https://your-app.railway.app
```

## Deployment Steps
1. Commit all changes
2. Push to repository
3. Railway will automatically rebuild with new Dockerfile (includes all Numba env vars)
4. Monitor initial startup logs for warmup completion
5. Test with the performance script

## Additional Recommendations
1. Consider using Railway's "Always On" tier for production to completely eliminate cold starts
2. Monitor container memory usage - Numba cache may require slight memory increase
3. For extreme performance needs, consider pre-building a Docker image with AOT-compiled Numba functions