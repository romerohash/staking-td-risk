#!/usr/bin/env python3
"""
Performance test script to measure API response times
"""

import time
import requests
import sys

def test_calculate_endpoint(base_url="http://localhost:8000"):
    """Test the /api/calculate endpoint with typical payload"""
    
    # Sample request payload
    payload = {
        "staking": {
            "eth": {
                "staking_pct": 0.90,
                "unbonding_period_days": 10,
                "annual_yield": 0.035,
                "baseline_staking_pct": 0.0
            },
            "sol": {
                "staking_pct": 0.90,
                "unbonding_period_days": 2,
                "annual_yield": 0.06,
                "baseline_staking_pct": 0.0
            }
        },
        "redemption": {
            "expected_redemptions_per_year": 6.5,
            "distribution": [
                {"size": 0.05, "probability": 0.67},
                {"size": 0.10, "probability": 0.17},
                {"size": 0.20, "probability": 0.11},
                {"size": 0.30, "probability": 0.05}
            ]
        }
    }
    
    print(f"Testing API at {base_url}/api/calculate")
    print("-" * 50)
    
    # Warm up request (first request includes JIT compilation)
    print("Warm-up request...")
    start = time.time()
    response = requests.post(f"{base_url}/api/calculate", json=payload)
    warmup_time = time.time() - start
    print(f"  Status: {response.status_code}")
    print(f"  Time: {warmup_time*1000:.1f}ms")
    
    if response.status_code != 200:
        print(f"  Error: {response.text}")
        return
    
    print("\nProduction requests (after warm-up):")
    times = []
    
    # Run 10 test requests
    for i in range(10):
        start = time.time()
        response = requests.post(f"{base_url}/api/calculate", json=payload)
        elapsed = time.time() - start
        times.append(elapsed)
        print(f"  Request {i+1}: {elapsed*1000:.1f}ms (status: {response.status_code})")
    
    # Calculate statistics
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    
    print("\nPerformance Summary:")
    print(f"  Average: {avg_time*1000:.1f}ms")
    print(f"  Min: {min_time*1000:.1f}ms")
    print(f"  Max: {max_time*1000:.1f}ms")
    print(f"  Warm-up overhead: {(warmup_time - avg_time)*1000:.1f}ms")
    
    # Check response data size
    response_size = len(response.content)
    print(f"\nResponse size: {response_size:,} bytes")
    
    # Verify response structure
    data = response.json()
    print(f"Sensitivity points (2D): {len(data.get('sensitivity_analysis_2d', []))}")

if __name__ == "__main__":
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    test_calculate_endpoint(base_url)