#!/usr/bin/env python3
"""
Microshare ERP Integration - Deployment Validator
Version: 2.0.0
Created: 2025-09-12 16:00:00 UTC

Validates deployment functionality:
- Tests authentication with user credentials
- Verifies API connectivity and endpoints
- Discovers available devices/clusters (results vary by account)
- Confirms the application works with user's specific data
"""

import asyncio
import httpx
import json
import base64
import time
from datetime import datetime
import sys

class DeploymentValidator:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.results = {'tests_passed': 0, 'tests_failed': 0, 'details': []}

    def log_test(self, test_name: str, success: bool, message: str, duration_ms: float = None):
        """Log test results"""
        status = "PASS" if success else "FAIL"
        result = {
            'test': test_name,
            'status': status,
            'message': message,
            'duration_ms': duration_ms
        }
        self.results['details'].append(result)
        
        if success:
            self.results['tests_passed'] += 1
        else:
            self.results['tests_failed'] += 1
            
        duration_str = f" ({duration_ms:.0f}ms)" if duration_ms else ""
        print(f"   [{status}] {test_name}: {message}{duration_str}")

    async def test_api_health(self):
        """Test basic API health and accessibility"""
        print("Testing API health and accessibility...")
        
        start_time = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.base_url}/health")
                duration_ms = (time.perf_counter() - start_time) * 1000
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_test("API Health Check", True, 
                        f"API is running - {data.get('service', 'Unknown service')}", duration_ms)
                    return True
                else:
                    self.log_test("API Health Check", False, 
                        f"API returned HTTP {response.status_code}", duration_ms)
                    return False
                    
        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            self.log_test("API Health Check", False, 
                f"Could not connect to API: {str(e)}", duration_ms)
            return False

    async def test_api_status(self):
        """Test API status endpoint for feature information"""
        print("Testing API status and features...")
        
        start_time = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.base_url}/api/v1/status")
                duration_ms = (time.perf_counter() - start_time) * 1000
                
                if response.status_code == 200:
                    data = response.json()
                    features = data.get('api', {}).get('features', [])
                    microshare_info = data.get('microshare', {})
                    
                    self.log_test("API Status", True, 
                        f"API operational with {len(features)} features configured", duration_ms)
                    
                    if microshare_info:
                        env_name = "production" if "api.microshare.io" in microshare_info.get('api_url', '') else "development"
                        self.log_test("Environment Detection", True, 
                            f"Connected to Microshare {env_name} environment")
                        
                    return True
                else:
                    self.log_test("API Status", False, 
                        f"Status endpoint returned HTTP {response.status_code}", duration_ms)
                    return False
                    
        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            self.log_test("API Status", False, 
                f"Status endpoint error: {str(e)}", duration_ms)
            return False

    async def test_device_discovery(self):
        """Test device cluster discovery - results vary by account"""
        print("Testing device cluster discovery...")
        
        start_time = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(f"{self.base_url}/api/v1/devices/clusters")
                duration_ms = (time.perf_counter() - start_time) * 1000
                
                if response.status_code == 200:
                    clusters = response.json()
                    cluster_count = len(clusters) if isinstance(clusters, list) else 0
                    
                    # Count total devices across all clusters
                    total_devices = 0
                    if isinstance(clusters, list):
                        for cluster in clusters:
                            devices = cluster.get('devices', [])
                            total_devices += len(devices)
                    
                    if cluster_count > 0:
                        self.log_test("Device Discovery", True, 
                            f"Found {cluster_count} cluster(s) with {total_devices} total device(s)", duration_ms)
                        self.log_test("Data Availability", True, 
                            f"Your account has accessible device data")
                    else:
                        self.log_test("Device Discovery", True, 
                            f"Discovery successful but no clusters found in your account", duration_ms)
                        self.log_test("Data Availability", False, 
                            f"Your account appears to have no device clusters configured")
                        
                    return True
                    
                elif response.status_code == 401:
                    self.log_test("Device Discovery", False, 
                        "Authentication failed - check your Microshare credentials", duration_ms)
                    return False
                    
                else:
                    self.log_test("Device Discovery", False, 
                        f"Discovery failed with HTTP {response.status_code}", duration_ms)
                    return False
                    
        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            self.log_test("Device Discovery", False, 
                f"Discovery error: {str(e)}", duration_ms)
            return False

    async def test_authentication_flow(self):
        """Test that authentication configuration is working"""
        print("Testing authentication configuration...")
        
        # Check if .env file exists and has required fields
        try:
            with open('.env', 'r') as f:
                env_content = f.read()
                
            required_vars = ['MICROSHARE_USERNAME', 'MICROSHARE_PASSWORD', 'MICROSHARE_API_URL']
            missing_vars = [var for var in required_vars if var not in env_content]
            
            if missing_vars:
                self.log_test("Environment Configuration", False, 
                    f"Missing required environment variables: {', '.join(missing_vars)}")
                return False
            else:
                self.log_test("Environment Configuration", True, 
                    "All required environment variables are configured")
                
                # Check if credentials are not empty/placeholder
                has_username = 'MICROSHARE_USERNAME=' in env_content and not 'your-username' in env_content
                has_password = 'MICROSHARE_PASSWORD=' in env_content and not 'your-password' in env_content
                
                if has_username and has_password:
                    self.log_test("Credential Configuration", True, 
                        "Credentials appear to be configured (not placeholder values)")
                else:
                    self.log_test("Credential Configuration", False, 
                        "Credentials appear to be placeholder values - update your .env file")
                        
                return True
                
        except FileNotFoundError:
            self.log_test("Environment Configuration", False, 
                ".env file not found - run ./quick_install.sh to configure")
            return False
        except Exception as e:
            self.log_test("Environment Configuration", False, 
                f"Could not read .env file: {str(e)}")
            return False

    def print_summary(self):
        """Print validation summary"""
        total_tests = self.results['tests_passed'] + self.results['tests_failed']
        success_rate = (self.results['tests_passed'] / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n{'='*60}")
        print("DEPLOYMENT VALIDATION SUMMARY")
        print(f"{'='*60}")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {self.results['tests_passed']}")
        print(f"Failed: {self.results['tests_failed']}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if self.results['tests_failed'] == 0:
            print(f"\nStatus: DEPLOYMENT SUCCESSFUL")
            print("Your Microshare ERP Integration is ready to use!")
            print(f"API Documentation: {self.base_url}/docs")
        else:
            print(f"\nStatus: DEPLOYMENT NEEDS ATTENTION")
            print("Please review failed tests above and:")
            print("1. Check your .env configuration")
            print("2. Verify Microshare credentials")
            print("3. Ensure API server is running")
            print("4. Check network connectivity")

    async def run_validation(self):
        """Run all validation tests"""
        print("Microshare ERP Integration - Deployment Validator")
        print("Testing deployment functionality with your account data")
        print(f"{'='*60}")
        
        # Test sequence
        api_healthy = await self.test_api_health()
        if not api_healthy:
            print(f"\nCannot continue - API server is not accessible")
            print("Please start the API server first:")
            print("  PYTHONPATH=. python3 start_api.py")
            self.print_summary()
            return
        
        await self.test_api_status()
        await self.test_authentication_flow()
        await self.test_device_discovery()
        
        self.print_summary()
        
        # Save results
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"validation_results_{timestamp}.json"
            with open(filename, 'w') as f:
                json.dump(self.results, f, indent=2, default=str)
            print(f"\nDetailed results saved to: {filename}")
        except Exception as e:
            print(f"Could not save results file: {e}")

async def main():
    validator = DeploymentValidator()
    await validator.run_validation()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nValidation interrupted by user")
    except Exception as e:
        print(f"Validation failed: {e}")
