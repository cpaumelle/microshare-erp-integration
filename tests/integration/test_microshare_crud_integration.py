#!/usr/bin/env python3
"""
Comprehensive CRUD Test Suite for Microshare API
Tests all Create, Read, Update, Delete operations with cache validation
"""

import requests
import json
import time
import sys
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

class MicroshareAPITester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        self.session_token = None
        self.authenticated = False

    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log test results"""
        status = "✅ PASS" if passed else "❌ FAIL"
        self.test_results.append((test_name, status, details))
        print(f"{test_name:<30} {status} {details}")

    def test_authentication(self):
        """Test authentication with .env credentials"""
        print("\n🔐 AUTHENTICATION")
        print("-" * 50)

        try:
            # Test auth status endpoint first
            response = self.session.get(f"{self.base_url}/api/v1/auth/status", timeout=5)
            self.log_test("Auth Endpoint", response.status_code in [200, 401], f"{response.status_code}")

            # Login with .env credentials
            login_data = {
                "username": "cp_erp_sample@maildrop.cc",
                "password": "AVH7dbz!brt-rfn0tdk",
                "environment": "dev"
            }

            response = self.session.post(f"{self.base_url}/api/v1/auth/login", json=login_data, timeout=10)

            if response.status_code == 200:
                auth_data = response.json()
                if auth_data.get('success'):
                    self.session_token = auth_data.get('session_token') or auth_data.get('access_token')
                    # Set Authorization header for future requests
                    self.session.headers.update({'Authorization': f'Bearer {self.session_token}'})
                    self.authenticated = True
                    self.log_test("Login Success", True, f"Token: {self.session_token[:16]}...")
                    return True
                else:
                    self.log_test("Login Failed", False, auth_data.get('detail', 'Unknown error'))
            else:
                self.log_test("Login Failed", False, f"HTTP {response.status_code}")

            return False

        except Exception as e:
            self.log_test("Authentication", False, str(e)[:50])
            return False

    def test_read_operations(self):
        """Test all read operations and cache performance"""
        print("\n📖 READ OPERATIONS")
        print("-" * 50)

        try:
            # Test device discovery
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/api/v1/devices/")
            duration = time.time() - start_time

            if response.status_code == 200:
                data = response.json()
                device_count = data.get('total_count', 0)
                self.log_test("Device Discovery", device_count >= 4, f"{device_count} devices, {duration:.3f}s")

                # Store for later use
                self.devices = data.get('devices', [])
                self.trap_devices = [d for d in self.devices if 'trap' in d.get('device_type', '')]

            # Test cache performance
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/api/v1/devices/")
            cached_duration = time.time() - start_time

            improvement = duration / cached_duration if cached_duration > 0 else 1
            self.log_test("Cache Performance", improvement > 10, f"{improvement:.0f}x faster")

            # Test cluster listing
            response = self.session.get(f"{self.base_url}/api/v1/devices/clusters")
            if response.status_code == 200:
                clusters = response.json().get('objs', [])
                self.trap_cluster_id = None
                for cluster in clusters:
                    if cluster.get('recType') == 'io.microshare.trap.packed':
                        self.trap_cluster_id = cluster['_id']
                        break

                self.log_test("Cluster Discovery", len(clusters) >= 2, f"{len(clusters)} clusters")

            # Test device search
            if self.devices:
                test_device_id = self.devices[0]['id']
                response = self.session.get(f"{self.base_url}/api/v1/devices/{test_device_id}")
                self.log_test("Device Search by ID", response.status_code == 200, test_device_id[:8])

            # Test filtering
            response = self.session.get(f"{self.base_url}/api/v1/devices/?customer=Golden%20Crust%20Manchester")
            if response.status_code == 200:
                filtered_devices = response.json().get('devices', [])
                self.log_test("Customer Filtering", len(filtered_devices) > 0, f"{len(filtered_devices)} devices")

        except Exception as e:
            self.log_test("Read Operations", False, str(e)[:50])

    def test_create_operation(self):
        """Test device creation"""
        print("\n➕ CREATE OPERATION")
        print("-" * 50)

        if not hasattr(self, 'trap_cluster_id') or not self.trap_cluster_id:
            self.log_test("Create Device", False, "No trap cluster found")
            return

        try:
            # Create test device
            new_device = {
                "id": "TEST-CRUD-DEVICE-001",
                "meta": {
                    "location": [
                        "CRUD Test Company",
                        "Test Site",
                        "Test Area",
                        "CRUD_TEST_REF_001",
                        "Internal",
                        "Poison"
                    ]
                },
                "status": "pending",
                "guid": f"crud-test-{int(time.time())}"
            }

            response = self.session.post(
                f"{self.base_url}/api/v1/devices/clusters/{self.trap_cluster_id}/devices?device_type=trap",
                json=new_device,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                self.log_test("Create Device", True, f"Device {new_device['id']}")
                self.test_device_id = new_device['id']

                # Verify device was added
                response = self.session.get(f"{self.base_url}/api/v1/devices/{self.test_device_id}")
                found = response.status_code == 200
                self.log_test("Verify Creation", found, "Device discoverable")

            else:
                self.log_test("Create Device", False, f"HTTP {response.status_code}")

        except Exception as e:
            self.log_test("Create Device", False, str(e)[:50])

    def test_update_operation(self):
        """Test device updates"""
        print("\n✏️  UPDATE OPERATION")
        print("-" * 50)

        if not hasattr(self, 'test_device_id') or not hasattr(self, 'trap_cluster_id'):
            self.log_test("Update Device", False, "No test device to update")
            return

        try:
            # Update the test device
            updates = {
                "location": [
                    "CRUD Test Company UPDATED",
                    "Test Site UPDATED",
                    "Test Area UPDATED",
                    "CRUD_TEST_REF_001_UPDATED",
                    "External",
                    "Bait/Lured"
                ],
                "status": "active"
            }

            response = self.session.put(
                f"{self.base_url}/api/v1/devices/clusters/{self.trap_cluster_id}/devices/{self.test_device_id}?device_type=trap",
                json=updates,
                timeout=30
            )

            if response.status_code == 200:
                self.log_test("Update Device", True, f"Status: {updates['status']}")

                # Verify updates took effect
                time.sleep(1)  # Brief wait for cache invalidation
                response = self.session.get(f"{self.base_url}/api/v1/devices/{self.test_device_id}")
                if response.status_code == 200:
                    device = response.json()
                    updated_correctly = (
                        device.get('status') == 'active' and
                        device.get('placement') == 'External' and
                        'UPDATED' in device.get('customer', '')
                    )
                    self.log_test("Verify Update", updated_correctly, f"Changes applied")
                else:
                    self.log_test("Verify Update", False, "Device not found after update")

            else:
                self.log_test("Update Device", False, f"HTTP {response.status_code}")

        except Exception as e:
            self.log_test("Update Device", False, str(e)[:50])

    def test_delete_operation(self):
        """Test device deletion"""
        print("\n🗑️  DELETE OPERATION")
        print("-" * 50)

        if not hasattr(self, 'test_device_id') or not hasattr(self, 'trap_cluster_id'):
            self.log_test("Delete Device", False, "No test device to delete")
            return

        try:
            # Delete the test device
            response = self.session.delete(
                f"{self.base_url}/api/v1/devices/clusters/{self.trap_cluster_id}/devices/{self.test_device_id}?device_type=trap",
                timeout=30
            )

            if response.status_code == 200:
                self.log_test("Delete Device", True, f"Device {self.test_device_id}")

                # Verify device was removed
                time.sleep(1)  # Brief wait for cache invalidation
                response = self.session.get(f"{self.base_url}/api/v1/devices/{self.test_device_id}")
                device_gone = response.status_code == 404
                self.log_test("Verify Deletion", device_gone, "Device no longer discoverable")

            else:
                self.log_test("Delete Device", False, f"HTTP {response.status_code}")

        except Exception as e:
            self.log_test("Delete Device", False, str(e)[:50])

    def test_cache_invalidation(self):
        """Test cache invalidation after CRUD operations"""
        print("\n💾 CACHE INVALIDATION")
        print("-" * 50)

        try:
            # Get initial cache stats
            response = self.session.get(f"{self.base_url}/api/v1/cache/stats")
            if response.status_code == 200:
                initial_stats = response.json()
                self.log_test("Cache Stats Access", True, f"{initial_stats.get('cached_items', 0)} items")

                # Clear cache
                response = self.session.delete(f"{self.base_url}/api/v1/cache")
                cache_cleared = response.status_code == 200
                self.log_test("Cache Clear", cache_cleared, "Manual cache clear")

                # Verify cache was cleared
                response = self.session.get(f"{self.base_url}/api/v1/cache/stats")
                if response.status_code == 200:
                    cleared_stats = response.json()
                    actually_cleared = cleared_stats.get('cached_items', 1) == 0
                    self.log_test("Cache Cleared", actually_cleared, "0 items in cache")

        except Exception as e:
            self.log_test("Cache Operations", False, str(e)[:50])

    def run_comprehensive_test(self):
        """Run all tests in sequence"""
        print("🧪 MICROSHARE API COMPREHENSIVE CRUD TEST SUITE")
        print("=" * 60)

        # Initialize
        self.devices = []
        self.trap_devices = []
        self.trap_cluster_id = None
        self.test_device_id = None

        # Run test sequence
        if not self.test_authentication():
            print("❌ Authentication failed, skipping remaining tests")
            return False

        self.test_read_operations()
        self.test_create_operation()
        self.test_update_operation()
        self.test_delete_operation()
        self.test_cache_invalidation()

        # Print summary
        return self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)

        total_tests = len(self.test_results)
        passed_tests = sum(1 for _, status, _ in self.test_results if "PASS" in status)
        failed_tests = total_tests - passed_tests

        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")

        if failed_tests > 0:
            print("\n❌ Failed Tests:")
            for test_name, status, details in self.test_results:
                if "FAIL" in status:
                    print(f"  • {test_name}: {details}")

        print("\n" + "=" * 60)

        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED! The Microshare API is fully functional.")
        else:
            print("⚠️  Some tests failed. Check the implementation.")

        return passed_tests == total_tests

def main():
    """Main function"""
    print("Starting Microshare API CRUD tests...")

    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        if response.status_code != 200:
            print(f"❌ Server not responding at {BASE_URL}")
            print("Make sure to start the API first: python3 start_api.py")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Cannot connect to server at {BASE_URL}")
        print("Make sure to start the API first: python3 start_api.py")
        sys.exit(1)

    # Run tests
    tester = MicroshareAPITester(BASE_URL)
    success = tester.run_comprehensive_test()

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
