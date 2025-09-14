#!/usr/bin/env python3
"""
Microshare ERP Integration - Deployment Validator
Version: 3.0.0
Created: 2025-09-14 15:40:00 UTC

Post-deployment validation for GitHub users:
1. Automatically starts the API server using start_api.py
2. Runs GUID-based CRUD operations test to validate full deployment
3. Tests authentication with user credentials
4. Verifies API connectivity and endpoints
5. Discovers available devices/clusters (results vary by account)
"""

import asyncio
import httpx
import json
import base64
import time
from datetime import datetime
import sys
import subprocess
import os
import signal

class DeploymentValidator:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.results = {'tests_passed': 0, 'tests_failed': 0, 'details': []}
        self.api_process = None

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

    async def start_api_server(self):
        """Start the API server using start_api.py"""
        print("🚀 Starting API server...")

        try:
            # Check if start_api.py exists
            if not os.path.exists('start_api.py'):
                self.log_test("API Server Startup", False,
                    "start_api.py not found in current directory")
                return False

            # Start the API server process
            self.api_process = subprocess.Popen(
                ['python3', 'start_api.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            self.log_test("API Server Process", True,
                f"API server started with PID {self.api_process.pid}")

            # Wait a moment for server to start up
            print("   Waiting for server to initialize...")
            await asyncio.sleep(3)

            return True

        except Exception as e:
            self.log_test("API Server Startup", False,
                f"Could not start API server: {str(e)}")
            return False

    def stop_api_server(self):
        """Stop the API server process"""
        if self.api_process:
            try:
                print("🛑 Stopping API server...")
                self.api_process.terminate()
                self.api_process.wait(timeout=5)
                self.log_test("API Server Shutdown", True,
                    "API server stopped successfully")
            except subprocess.TimeoutExpired:
                # Force kill if it doesn't stop gracefully
                self.api_process.kill()
                self.log_test("API Server Shutdown", True,
                    "API server force stopped")
            except Exception as e:
                self.log_test("API Server Shutdown", False,
                    f"Error stopping API server: {str(e)}")

    async def run_guid_crud_test(self):
        """Run the GUID-based CRUD operations test"""
        print("Running GUID-based CRUD operations test...")

        start_time = time.perf_counter()
        try:
            # Run the CRUD test script
            result = subprocess.run(
                ['python3', 'test_guid_crud_operations.py'],
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout
            )

            duration_ms = (time.perf_counter() - start_time) * 1000

            if result.returncode == 0:
                self.log_test("GUID CRUD Operations", True,
                    "All CRUD operations completed successfully", duration_ms)

                # Check for specific success indicators in output
                if "GUID-BASED CRUD OPERATIONS SUCCESSFUL" in result.stdout:
                    self.log_test("CRUD Functionality Validation", True,
                        "Full CRUD functionality confirmed")
                else:
                    self.log_test("CRUD Functionality Validation", True,
                        "CRUD test completed without errors")

                return True
            else:
                self.log_test("GUID CRUD Operations", False,
                    f"CRUD test failed with exit code {result.returncode}", duration_ms)

                # Print stderr for debugging
                if result.stderr:
                    print(f"   Error details: {result.stderr[:200]}...")

                return False

        except subprocess.TimeoutExpired:
            duration_ms = (time.perf_counter() - start_time) * 1000
            self.log_test("GUID CRUD Operations", False,
                "CRUD test timed out after 2 minutes", duration_ms)
            return False
        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            self.log_test("GUID CRUD Operations", False,
                f"CRUD test error: {str(e)}", duration_ms)
            return False

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
        print("Microshare ERP Integration - Deployment Validator v3.0.0")
        print("Automatic post-deployment validation for GitHub users")
        print(f"{'='*60}")

        try:
            # Step 1: Check environment configuration first
            print("Step 1: Environment Configuration")
            await self.test_authentication_flow()

            # Step 2: Start API server automatically
            print("\nStep 2: API Server Startup")
            server_started = await self.start_api_server()
            if not server_started:
                print("\nCannot continue - API server startup failed")
                print("Please check:")
                print("  1. start_api.py exists in current directory")
                print("  2. All dependencies are installed")
                print("  3. .env file is properly configured")
                self.print_summary()
                return

            # Step 3: Test API health
            print("\nStep 3: API Health Check")
            api_healthy = await self.test_api_health()
            if not api_healthy:
                print("API server started but not responding correctly")

            # Step 4: Test API status
            print("\nStep 4: API Status and Features")
            await self.test_api_status()

            # Step 5: Test device discovery
            print("\nStep 5: Device Discovery")
            await self.test_device_discovery()

            # Step 6: Run comprehensive CRUD test
            print("\nStep 6: GUID-based CRUD Operations Test")
            await self.run_guid_crud_test()

            self.print_summary()

            # Save results
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"deployment_validation_{timestamp}.json"
                with open(filename, 'w') as f:
                    json.dump(self.results, f, indent=2, default=str)
                print(f"\nDetailed results saved to: {filename}")
            except Exception as e:
                print(f"Could not save results file: {e}")

        finally:
            # Always try to stop the server when done
            self.stop_api_server()

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
