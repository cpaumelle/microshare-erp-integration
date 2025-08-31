#!/usr/bin/env python3
"""
Performance benchmark script for Microshare ERP Integration API
Tests API response times and caching performance
"""

import time
import asyncio
import httpx
import statistics
from datetime import datetime

class PerformanceBenchmark:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.results = {}
    
    async def benchmark_endpoint(self, endpoint: str, num_requests: int = 10):
        """Benchmark a specific endpoint"""
        print(f"📊 Benchmarking {endpoint} ({num_requests} requests)...")
        
        times = []
        async with httpx.AsyncClient() as client:
            for i in range(num_requests):
                start_time = time.time()
                try:
                    response = await client.get(f"{self.base_url}{endpoint}")
                    end_time = time.time()
                    response_time = end_time - start_time
                    times.append(response_time)
                    print(f"  Request {i+1}: {response_time:.3f}s (Status: {response.status_code})")
                except Exception as e:
                    print(f"  Request {i+1}: ERROR - {e}")
                    continue
        
        if times:
            avg_time = statistics.mean(times)
            min_time = min(times)
            max_time = max(times)
            
            self.results[endpoint] = {
                'average': avg_time,
                'minimum': min_time, 
                'maximum': max_time,
                'requests': len(times)
            }
            
            print(f"  ⚡ Average: {avg_time:.3f}s, Min: {min_time:.3f}s, Max: {max_time:.3f}s")
        else:
            print(f"  ❌ No successful requests for {endpoint}")
    
    async def run_benchmarks(self):
        """Run all performance benchmarks"""
        print(f"🚀 Starting performance benchmarks at {datetime.now()}")
        print("=" * 60)
        
        endpoints = [
            "/health",
            "/devices/locations",
            "/incidents"
        ]
        
        for endpoint in endpoints:
            await self.benchmark_endpoint(endpoint)
            print()
        
        print("📈 Performance Summary:")
        print("=" * 60)
        for endpoint, results in self.results.items():
            print(f"{endpoint}:")
            print(f"  Average: {results['average']:.3f}s")
            print(f"  Best: {results['minimum']:.3f}s") 
            print(f"  Worst: {results['maximum']:.3f}s")
            print()

if __name__ == "__main__":
    benchmark = PerformanceBenchmark()
    asyncio.run(benchmark.run_benchmarks())

