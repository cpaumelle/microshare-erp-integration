#!/usr/bin/env python3
"""
Microshare ERP Integration - Deployment Validator (Fixed)
Version: 3.0.1
Created: 2025-09-15 07:30:00 UTC

FIXED: Now follows the same authentication pattern as test_guid_crud_operations.py
- Authenticates with local FastAPI server
- Uses session tokens for protected endpoints
- Matches working patterns exactly

Post-deployment validation for GitHub users:
1. Automatically starts the API server using start_api.py
2. Authenticates using proven login pattern
3. Tests device endpoints with proper authentication
4. Runs GUID-based CRUD operations test
5. Validates full deployment functionality
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
import getpass

class DeploymentValidator:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.results = {'tests_passed': 0, 'tests_failed': 0, 'details': []}
        self.api_process = None
        self.access_token = None

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

    async def authenticate_with_local_server(self):
        """Authenticate with local FastAPI server (same pattern as working test)"""
        print("Authenticating with local FastAPI server...")
        
        try:
            # Get credentials from environment or prompt
            username = os.getenv('MICROSHARE_USERNAME')
            password = os.getenv('MICROSHARE_PASSWORD')
            
            if not username or not password:
                print("   No credentials in environment, using interactive mode...")
                username = input("   Username: ")
                password = getpass.getpass("   Password: ")

            start_time = time.perf_counter()
            
            async with httpx.AsyncClient(timeout=30) as client:
                # Use the exact same authentication pattern as test_guid_crud_operations.py
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
                        'User-Agent': 'Deployment-Validator/3.0.1'
                    }
                )

                duration_ms = (time.perf_counter() - start_time) * 1000

                if response.status_code == 200:
                    auth_response = response.json()
                    
                    # Try different possible token field names (same as working test)
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
                        self.log_test("Authentication", True,
                            f"Successfully authenticated and received session token", duration_ms)
                        return True
                    else:
                        self.log_test("Authentication", False,
                            "No access token found in response", duration_ms)
                        return False
                else:
                    self.log_test("Authentication", False,
                        f"Authentication failed with HTTP {response.status_code}", duration_ms)
                    return False

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000 if 'start_time' in locals() else 0
            self.log_test("Authentication", False,
                f"Authentication error: {str(e)}", duration_ms)
            return False

    def create_headers(self) -> dict:
        """Create headers for authenticated API requests"""
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    async def check_existing_server(self):
        """Check if a server is already running on port 8000"""
        print("Checking for existing API server...")
        
        try:
            async with httpx.AsyncClient(timeout=2) as client:
                response = await client.get(f"{self.base_url}/health")
                if response.status_code == 200:
                    data = response.json()
                    service_name = data.get('service', 'Unknown service')
                    self.log_test("Existing Server Check", True,
                        f"Found running server: {service_name}")
                    return True
        except:
            pass
        
        self.log_test("Existing Server Check", True,
            "No existing server found - will start new one")
        return False

    async def start_api_server(self):
        """Start the API server using start_api.py (only if not already running)"""
        
        # First check if server is already running
        server_exists = await self.check_existing_server()
        if server_exists:
            print("   Using existing API server")
            return True
            
        print("🚀 Starting API server...")

        try:
            # Check if start_api.py exists
            if not os.path.exists('start_api.py'):
                self.log_test("API Server Startup", False,
                    "start_api.py not found in current directory")
                return False

            # Kill any processes that might be blocking port 8000
            try:
                subprocess.run(['pkill', '-f', 'python.*start_api.py'], 
                             capture_output=True, timeout=5)
                subprocess.run(['pkill', '-f', 'python.*main.py'], 
                             capture_output=True, timeout=5)
                await asyncio.sleep(1)  # Wait for cleanup
            except:
                pass  # Ignore errors if no processes to kill

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

            # Verify server actually started
            try:
                async with httpx.AsyncClient(timeout=5) as client:
                    response = await client.get(f"{self.base_url}/health")
                    if response.status_code == 200:
                        self.log_test("Server Verification", True,
                            "API server started and responding")
                        return True
                    else:
                        self.log_test("Server Verification", False,
                            f"Server started but not responding correctly (HTTP {response.status_code})")
                        return False
            except Exception as e:
                self.log_test("Server Verification", False,
                    f"Server started but not accessible: {str(e)}")
                return False

        except Exception as e:
            self.log_test("API Server Startup", False,
                f"Could not start API server: {str(e)}")
            return False

    def stop_api_server(self):
        """Stop the API server process (only if we started it)"""
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
        else:
            # Don't try to stop servers we didn't start
            print("🔄 Leaving existing API server running")
            self.log_test("API Server Management", True,
                "Using existing server - no shutdown needed")

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

    async def test_authenticated_device_discovery(self):
        """Test device discovery with proper authentication (same as working test)"""
        print("Testing authenticated device discovery...")

        if not self.access_token:
            self.log_test("Device Discovery", False,
                "No access token available - authentication required")
            return False

        start_time = time.perf_counter()
        try:
            headers = self.create_headers()
            
            async with httpx.AsyncClient(timeout=30) as client:
                # Use the exact same endpoint pattern as the working test
                response = await client.get(f"{self.base_url}/api/v1/devices/", headers=headers)
                duration_ms = (time.perf_counter() - start_time) * 1000

                if response.status_code == 200:
                    devices_data = response.json()
                    devices = devices_data.get('devices', [])
                    total_count = devices_data.get('total_count', len(devices))

                    if total_count > 0:
                        self.log_test("Device Discovery", True,
                            f"Found {total_count} device(s) with authenticated access", duration_ms)
                        self.log_test("Data Availability", True,
                            f"Your account has accessible device data")
                        
                        # Test device structure (same as working test)
                        if devices and len(devices) > 0:
                            sample_device = devices[0]
                            required_fields = ['id', 'customer', 'site', 'area', 'guid']
                            missing_fields = [field for field in required_fields if field not in sample_device]
                            
                            if not missing_fields:
                                self.log_test("Device Structure", True,
                                    "Device data structure is valid")
                            else:
                                self.log_test("Device Structure", False,
                                    f"Missing fields in device data: {missing_fields}")
                    else:
                        self.log_test("Device Discovery", True,
                            f"Discovery successful but no devices found in your account", duration_ms)
                        self.log_test("Data Availability", False,
                            f"Your account appears to have no devices configured")

                    return True

                elif response.status_code == 401:
                    self.log_test("Device Discovery", False,
                        "Authentication failed - token may be invalid", duration_ms)
                    return False

                elif response.status_code == 403:
                    self.log_test("Device Discovery", False,
                        "Access forbidden - check authentication headers", duration_ms)
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

    async def test_crud_operations_sample(self):
        """Test basic CRUD operations with authentication"""
        print("Testing basic CRUD operations...")

        if not self.access_token:
            self.log_test("CRUD Operations", False,
                "No access token available - authentication required")
            return False

        start_time = time.perf_counter()
        try:
            headers = self.create_headers()
            
            async with httpx.AsyncClient(timeout=30) as client:
                # Test device creation endpoint
                sample_device = {
                    "customer": "ValidationTest",
                    "site": "TestSite", 
                    "area": "TestArea",
                    "erp_reference": f"VAL_TEST_{int(time.time())}",
                    "placement": "Internal",
                    "configuration": "Bait/Lured",
                    "device_type": "rodent_sensor"
                }

                response = await client.post(
                    f"{self.base_url}/api/v1/devices/create",
                    json=sample_device,
                    headers=headers
                )

                duration_ms = (time.perf_counter() - start_time) * 1000

                if response.status_code == 200:
                    create_result = response.json()
                    if create_result.get('success'):
                        self.log_test("CRUD Operations", True,
                            "Device creation endpoint working", duration_ms)
                        
                        # Try to clean up the test device
                        created_device = create_result.get('device', {})
                        device_guid = created_device.get('guid')
                        
                        if device_guid:
                            # Test delete operation
                            delete_response = await client.delete(
                                f"{self.base_url}/api/v1/devices/{device_guid}",
                                headers=headers
                            )
                            
                            if delete_response.status_code == 200:
                                self.log_test("CRUD Cleanup", True,
                                    "Test device successfully cleaned up")
                        
                        return True
                    else:
                        self.log_test("CRUD Operations", False,
                            f"Device creation returned success=false", duration_ms)
                        return False
                else:
                    self.log_test("CRUD Operations", False,
                        f"CRUD endpoint returned HTTP {response.status_code}", duration_ms)
                    return False

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            self.log_test("CRUD Operations", False,
                f"CRUD test error: {str(e)}", duration_ms)
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
        print("Microshare ERP Integration - Deployment Validator v3.0.1 (Fixed)")
        print("Fixed authentication pattern - matches test_guid_crud_operations.py")
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
                self.print_summary()
                return

            # Step 3: Test API health
            print("\nStep 3: API Health Check")
            api_healthy = await self.test_api_health()
            if not api_healthy:
                print("API server started but not responding correctly")

            # Step 4: Authenticate with local server (NEW - matching working test)
            print("\nStep 4: Authentication Test")
            auth_success = await self.authenticate_with_local_server()
            if not auth_success:
                print("Authentication failed - cannot test protected endpoints")
                self.print_summary()
                return

            # Step 5: Test authenticated device discovery (FIXED)
            print("\nStep 5: Authenticated Device Discovery")
            await self.test_authenticated_device_discovery()

            # Step 6: Test basic CRUD operations
            print("\nStep 6: Basic CRUD Operations Test")
            await self.test_crud_operations_sample()

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
