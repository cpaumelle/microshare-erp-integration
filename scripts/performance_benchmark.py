#!/usr/bin/env python3
"""
Microshare ERP Integration - Performance Benchmark Script (Updated)
Version: 2.0.0
Created: 2025-09-15 14:30:00 UTC

UPDATED: Now follows the same authentication pattern as validate_deployment.py
- Authenticates with local FastAPI server
- Uses session tokens for protected endpoints
- Tests both authenticated and unauthenticated endpoints
- Provides comprehensive performance metrics

Performance benchmark script for Microshare ERP Integration API
Tests API response times, caching performance, and authentication overhead
"""

import asyncio
import httpx
import json
import time
import statistics
import os
import getpass
from datetime import datetime
from typing import Dict, List, Optional


class PerformanceBenchmark:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.results = {}
        self.access_token = None
        self.auth_overhead = 0
        
    async def authenticate_with_local_server(self) -> bool:
        """Authenticate with local FastAPI server (same pattern as validate_deployment.py)"""
        print("🔐 Authenticating with local FastAPI server...")

        try:
            # Get credentials from environment or prompt
            username = os.getenv('MICROSHARE_USERNAME')
            password = os.getenv('MICROSHARE_PASSWORD')

            if not username or not password:
                print("   No credentials in environment, using interactive mode...")
                username = input("   Username: ")
                password = getpass.getpass("   Password: ")

            auth_start_time = time.perf_counter()

            async with httpx.AsyncClient(timeout=30) as client:
                # Use the exact same authentication pattern as validate_deployment.py
                login_data = {
                    "username": username,
                    "password": password,
                    "environment": "dev"  # Default to dev environment
                }

                response = await client.post(
                    f"{self.base_url}/api/v1/auth/login",
                    json=login_data,
                    headers={
                        'Content-Type': 'application/json',
                        'User-Agent': 'Performance-Benchmark/2.0.0'
                    }
                )

                auth_end_time = time.perf_counter()
                self.auth_overhead = (auth_end_time - auth_start_time) * 1000

                if response.status_code == 200:
                    auth_response = response.json()

                    # Try different possible token field names (same as validate_deployment.py)
                    possible_token_fields = [
                        'access_token', 'session_token', 'token',
                        'auth_token', 'jwt', 'bearer_token'
                    ]

                    self.access_token = None
                    for field in possible_token_fields:
                        if field in auth_response:
                            self.access_token = auth_response[field]
                            break

                    if self.access_token:
                        print(f"   ✅ Authentication successful ({self.auth_overhead:.1f}ms)")
                        return True
                    else:
                        print("   ❌ No access token found in response")
                        return False
                else:
                    print(f"   ❌ Authentication failed with HTTP {response.status_code}")
                    return False

        except Exception as e:
            print(f"   ❌ Authentication error: {str(e)}")
            return False

    def create_headers(self) -> dict:
        """Create headers for authenticated API requests"""
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    async def benchmark_endpoint(self, endpoint: str, num_requests: int = 10, 
                                authenticated: bool = False, method: str = 'GET', 
                                payload: dict = None) -> Dict:
        """Benchmark a specific endpoint with optional authentication"""
        endpoint_type = "🔒 Authenticated" if authenticated else "🌐 Public"
        print(f"📊 Benchmarking {endpoint_type} {method} {endpoint} ({num_requests} requests)...")
        
        times = []
        status_codes = []
        errors = 0
        
        # Prepare headers
        headers = {}
        if authenticated and self.access_token:
            headers = self.create_headers()
        elif authenticated and not self.access_token:
            print(f"   ⚠️  Skipping authenticated endpoint - no access token")
            return {'error': 'No authentication token available'}

        async with httpx.AsyncClient(timeout=30) as client:
            for i in range(num_requests):
                start_time = time.perf_counter()
                try:
                    if method.upper() == 'GET':
                        response = await client.get(f"{self.base_url}{endpoint}", headers=headers)
                    elif method.upper() == 'POST':
                        response = await client.post(f"{self.base_url}{endpoint}", 
                                                   json=payload, headers=headers)
                    elif method.upper() == 'PUT':
                        response = await client.put(f"{self.base_url}{endpoint}", 
                                                  json=payload, headers=headers)
                    elif method.upper() == 'DELETE':
                        response = await client.delete(f"{self.base_url}{endpoint}", headers=headers)
                    else:
                        raise ValueError(f"Unsupported method: {method}")
                    
                    end_time = time.perf_counter()
                    response_time = (end_time - start_time) * 1000  # Convert to milliseconds
                    
                    times.append(response_time)
                    status_codes.append(response.status_code)
                    
                    status_icon = "✅" if 200 <= response.status_code < 300 else "⚠️"
                    print(f"  Request {i+1:2d}: {response_time:6.1f}ms {status_icon} (HTTP {response.status_code})")
                    
                except Exception as e:
                    end_time = time.perf_counter()
                    response_time = (end_time - start_time) * 1000
                    errors += 1
                    print(f"  Request {i+1:2d}: {response_time:6.1f}ms ❌ ERROR - {str(e)[:50]}")
                    continue

        # Calculate statistics
        if times:
            result = {
                'endpoint': endpoint,
                'method': method,
                'authenticated': authenticated,
                'requests_sent': num_requests,
                'successful_requests': len(times),
                'failed_requests': errors,
                'average_ms': statistics.mean(times),
                'median_ms': statistics.median(times),
                'minimum_ms': min(times),
                'maximum_ms': max(times),
                'std_dev_ms': statistics.stdev(times) if len(times) > 1 else 0,
                'status_codes': list(set(status_codes)),
                'success_rate': (len(times) / num_requests) * 100 if num_requests > 0 else 0
            }
            
            # Calculate percentiles
            if len(times) >= 2:
                sorted_times = sorted(times)
                result['p95_ms'] = sorted_times[int(0.95 * len(sorted_times))]
                result['p99_ms'] = sorted_times[int(0.99 * len(sorted_times))]
            
            print(f"  📈 Avg: {result['average_ms']:.1f}ms, "
                  f"Min: {result['minimum_ms']:.1f}ms, "
                  f"Max: {result['maximum_ms']:.1f}ms, "
                  f"Success: {result['success_rate']:.1f}%")
        else:
            result = {
                'endpoint': endpoint,
                'method': method,
                'authenticated': authenticated,
                'error': 'No successful requests',
                'requests_sent': num_requests,
                'successful_requests': 0,
                'failed_requests': errors,
                'success_rate': 0
            }
            print(f"  ❌ No successful requests for {endpoint}")

        return result

    async def test_authentication_performance(self) -> Dict:
        """Test authentication endpoint performance specifically"""
        print("🔐 Testing authentication endpoint performance...")
        
        # Get credentials
        username = os.getenv('MICROSHARE_USERNAME', 'test-user')
        password = os.getenv('MICROSHARE_PASSWORD', 'test-pass')
        
        login_payload = {
            "username": username,
            "password": password,
            "environment": "dev"
        }
        
        return await self.benchmark_endpoint(
            "/api/v1/auth/login", 
            num_requests=5,  # Fewer requests for auth to avoid rate limiting
            authenticated=False,
            method="POST",
            payload=login_payload
        )

    async def run_benchmarks(self):
        """Run all performance benchmarks"""
        print(f"🚀 Starting Performance Benchmarks - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Target API: {self.base_url}")
        print("=" * 80)

        # Step 1: Test basic connectivity
        print("\n🌐 Step 1: Basic Connectivity Tests")
        basic_endpoints = [
            ("/health", False, "GET"),
            ("/", False, "GET"),
            ("/docs", False, "GET"),
        ]
        
        for endpoint, auth_required, method in basic_endpoints:
            result = await self.benchmark_endpoint(endpoint, num_requests=5, 
                                                 authenticated=auth_required, method=method)
            self.results[f"basic_{endpoint.replace('/', '_')}"] = result

        # Step 2: Authentication performance
        print("\n🔐 Step 2: Authentication Performance")
        auth_result = await self.test_authentication_performance()
        self.results['authentication'] = auth_result

        # Step 3: Authenticate for protected endpoints
        print("\n🔑 Step 3: Authentication Setup")
        auth_success = await self.authenticate_with_local_server()
        
        if auth_success:
            print("\n🔒 Step 4: Authenticated Endpoint Tests")
            
            # Test authenticated endpoints
            authenticated_endpoints = [
                ("/api/v1/devices/", True, "GET"),
                ("/api/v1/devices/clusters", True, "GET"),
                ("/api/v1/auth/me", True, "GET"),
                ("/api/v1/auth/status", True, "GET"),
            ]
            
            for endpoint, auth_required, method in authenticated_endpoints:
                result = await self.benchmark_endpoint(endpoint, num_requests=10, 
                                                     authenticated=auth_required, method=method)
                self.results[f"auth_{endpoint.replace('/', '_').replace('api_v1_', '')}"] = result

            # Step 5: CRUD Operation Performance
            print("\n⚡ Step 5: CRUD Operations Performance")
            await self.test_crud_performance()

        else:
            print("\n⚠️  Skipping authenticated endpoint tests - authentication failed")

        # Step 6: Generate performance report
        print("\n📊 Step 6: Performance Analysis")
        self.generate_performance_report()

    async def test_crud_performance(self):
        """Test CRUD operations performance"""
        print("🔧 Testing CRUD operations performance...")
        
        if not self.access_token:
            print("   ⚠️  Skipping CRUD tests - no authentication token")
            return

        # Test device creation
        test_device = {
            "customer": "PerfTest",
            "site": "BenchmarkSite",
            "area": "TestArea",
            "erp_reference": f"PERF_TEST_{int(time.time())}",
            "placement": "Internal",
            "configuration": "Bait/Lured",
            "device_type": "rodent_sensor"
        }

        # Create operation
        create_result = await self.benchmark_endpoint(
            "/api/v1/devices/create",
            num_requests=3,  # Fewer to avoid creating too many test devices
            authenticated=True,
            method="POST",
            payload=test_device
        )
        self.results['crud_create'] = create_result

        # Read operations (already tested above)
        # Update and Delete would require more complex test data management

    def generate_performance_report(self):
        """Generate a comprehensive performance report"""
        print("\n" + "=" * 80)
        print("📈 PERFORMANCE BENCHMARK REPORT")
        print("=" * 80)

        # Authentication overhead
        if self.auth_overhead > 0:
            print(f"🔐 Authentication Overhead: {self.auth_overhead:.1f}ms")

        # Summary statistics
        successful_tests = [r for r in self.results.values() if isinstance(r, dict) and 'average_ms' in r]
        
        if successful_tests:
            all_response_times = [r['average_ms'] for r in successful_tests]
            fastest_endpoint = min(successful_tests, key=lambda x: x['average_ms'])
            slowest_endpoint = max(successful_tests, key=lambda x: x['average_ms'])
            
            print(f"\n📊 Overall Statistics:")
            print(f"   Total Tests: {len(self.results)}")
            print(f"   Successful Tests: {len(successful_tests)}")
            print(f"   Average Response Time: {statistics.mean(all_response_times):.1f}ms")
            print(f"   Fastest Endpoint: {fastest_endpoint['endpoint']} ({fastest_endpoint['average_ms']:.1f}ms)")
            print(f"   Slowest Endpoint: {slowest_endpoint['endpoint']} ({slowest_endpoint['average_ms']:.1f}ms)")

        # Detailed results
        print(f"\n🔍 Detailed Results:")
        print("-" * 80)
        
        for test_name, result in self.results.items():
            if isinstance(result, dict) and 'average_ms' in result:
                auth_status = "🔒" if result.get('authenticated') else "🌐"
                success_rate = result.get('success_rate', 0)
                success_indicator = "✅" if success_rate >= 95 else "⚠️" if success_rate >= 80 else "❌"
                
                print(f"{auth_status} {result['method']} {result['endpoint']}")
                print(f"   {success_indicator} Success Rate: {success_rate:.1f}% "
                      f"({result.get('successful_requests', 0)}/{result.get('requests_sent', 0)})")
                print(f"   ⚡ Avg: {result['average_ms']:.1f}ms, "
                      f"Min: {result['minimum_ms']:.1f}ms, "
                      f"Max: {result['maximum_ms']:.1f}ms")
                
                if 'p95_ms' in result:
                    print(f"   📈 P95: {result['p95_ms']:.1f}ms, P99: {result.get('p99_ms', 0):.1f}ms")
                
                print()
            elif isinstance(result, dict) and 'error' in result:
                print(f"❌ {test_name}: {result['error']}")
                print()

        # Performance recommendations
        print("💡 Performance Recommendations:")
        print("-" * 80)
        
        if successful_tests:
            slow_endpoints = [r for r in successful_tests if r['average_ms'] > 1000]
            if slow_endpoints:
                print("⚠️  Slow endpoints detected (>1000ms):")
                for endpoint in slow_endpoints:
                    print(f"   - {endpoint['endpoint']}: {endpoint['average_ms']:.1f}ms")
                print("   Consider implementing caching or optimization")
            else:
                print("✅ All endpoints performing well (<1000ms average)")

            # Check success rates
            failing_endpoints = [r for r in successful_tests if r.get('success_rate', 0) < 95]
            if failing_endpoints:
                print("\n⚠️  Endpoints with low success rates (<95%):")
                for endpoint in failing_endpoints:
                    print(f"   - {endpoint['endpoint']}: {endpoint.get('success_rate', 0):.1f}%")
            else:
                print("✅ All endpoints have good reliability (≥95% success rate)")

        # Save results to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"performance_benchmark_{timestamp}.json"
        
        try:
            # Add metadata to results
            report_data = {
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'target_url': self.base_url,
                    'auth_overhead_ms': self.auth_overhead,
                    'total_tests': len(self.results),
                    'successful_tests': len(successful_tests)
                },
                'results': self.results
            }
            
            with open(filename, 'w') as f:
                json.dump(report_data, f, indent=2, default=str)
            print(f"\n💾 Detailed results saved to: {filename}")
        except Exception as e:
            print(f"\n❌ Could not save results file: {e}")

        print(f"\n🏁 Performance benchmark completed - {datetime.now().strftime('%H:%M:%S')}")


async def main():
    """Main function to run performance benchmarks"""
    benchmark = PerformanceBenchmark()
    await benchmark.run_benchmarks()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Benchmark interrupted by user")
    except Exception as e:
        print(f"❌ Benchmark failed: {e}")
        import traceback
        traceback.print_exc()
