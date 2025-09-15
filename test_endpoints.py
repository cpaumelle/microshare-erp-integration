#!/usr/bin/env python3
"""
Quick endpoint tester following validate_deployment.py pattern
"""
import asyncio
import httpx
import json
import os

async def test_endpoints():
    base_url = "http://localhost:8000"
    access_token = None

    print("🔍 Testing API Endpoints")
    print("=" * 50)

    async with httpx.AsyncClient(timeout=30) as client:
        # 1. Test health endpoint
        print("\n1. Health Check:")
        try:
            response = await client.get(f"{base_url}/health")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ GET /health - {data.get('service')} v{data.get('version')}")
            else:
                print(f"   ❌ GET /health - HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ GET /health - Error: {e}")

        # 2. Test authentication
        print("\n2. Authentication:")
        try:
            # Get credentials from environment
            username = os.getenv('MICROSHARE_USERNAME', 'cp_erp_sample@maildrop.cc')
            password = os.getenv('MICROSHARE_PASSWORD', 'AVH7dbz!brt-rfn0tdk')

            login_data = {
                "username": username,
                "password": password,
                "environment": "dev"
            }

            response = await client.post(f"{base_url}/api/v1/auth/login", json=login_data)
            if response.status_code == 200:
                auth_response = response.json()

                # Look for token field (following validator pattern)
                possible_token_fields = ['access_token', 'session_token', 'token', 'auth_token']
                for field in possible_token_fields:
                    if field in auth_response:
                        access_token = auth_response[field]
                        print(f"   ✅ POST /api/v1/auth/login - Got {field}")
                        break

                if not access_token:
                    print(f"   ⚠️  POST /api/v1/auth/login - Success but no token found")
            else:
                print(f"   ❌ POST /api/v1/auth/login - HTTP {response.status_code}")
                print(f"       Response: {response.text}")
        except Exception as e:
            print(f"   ❌ POST /api/v1/auth/login - Error: {e}")

        if not access_token:
            print("\n❌ Cannot test authenticated endpoints without token")
            return

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        # 3. Test device endpoints
        print("\n3. Device Endpoints:")

        # Test device list
        try:
            response = await client.get(f"{base_url}/api/v1/devices/", headers=headers)
            if response.status_code == 200:
                data = response.json()
                count = data.get('total_count', 0) if isinstance(data, dict) else len(data)
                print(f"   ✅ GET /api/v1/devices/ - Found {count} devices")
            else:
                print(f"   ❌ GET /api/v1/devices/ - HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ GET /api/v1/devices/ - Error: {e}")

        # Test device creation endpoint
        try:
            test_device = {
                "customer": "Test Customer",
                "site": "Test Site",
                "area": "Test Area",
                "erp_reference": "TEST_001",
                "placement": "Internal",
                "configuration": "Bait/Lured",
                "device_type": "rodent_sensor"
            }

            response = await client.post(f"{base_url}/api/v1/devices/create", json=test_device, headers=headers)
            if response.status_code in [200, 201]:
                print(f"   ✅ POST /api/v1/devices/create - Device creation endpoint working")
            else:
                print(f"   ❌ POST /api/v1/devices/create - HTTP {response.status_code}")
                print(f"       Response: {response.text[:200]}...")
        except Exception as e:
            print(f"   ❌ POST /api/v1/devices/create - Error: {e}")

        # 4. Test other endpoints mentioned in docs
        print("\n4. Other Documented Endpoints:")

        endpoints_to_test = [
            ("/api/v1/auth/status", "GET"),
            ("/api/v1/devices/cache/status", "GET"),
            ("/api/v1/devices/performance/benchmark", "GET"),
            ("/api/v1/devices/test", "GET"),
            ("/api/v1/status", "GET"),  # From main.py
        ]

        for endpoint, method in endpoints_to_test:
            try:
                if method == "GET":
                    response = await client.get(f"{base_url}{endpoint}", headers=headers)
                    if response.status_code == 200:
                        print(f"   ✅ {method} {endpoint} - Working")
                    else:
                        print(f"   ❌ {method} {endpoint} - HTTP {response.status_code}")

            except Exception as e:
                print(f"   ❌ {method} {endpoint} - Error: {e}")

        # 5. Test endpoints that docs claim exist but might not
        print("\n5. Questionable Endpoints from Docs:")

        questionable_endpoints = [
            ("/api/v1/devices/discovery", "GET"),  # From DEVELOPER_GUIDE
            ("/api/v1/devices/clusters", "GET"),   # From DEVELOPER_GUIDE
            ("/cluster/items", "GET"),             # From microshare_device_crud.md
            ("/auth/token", "POST"),               # From microshare_device_crud.md
        ]

        for endpoint, method in questionable_endpoints:
            try:
                if method == "GET":
                    response = await client.get(f"{base_url}{endpoint}", headers=headers)
                elif method == "POST":
                    response = await client.post(f"{base_url}{endpoint}", json={}, headers=headers)

                if response.status_code == 200:
                    print(f"   ✅ {method} {endpoint} - EXISTS!")
                else:
                    print(f"   ❌ {method} {endpoint} - HTTP {response.status_code} (likely doesn't exist)")

            except Exception as e:
                print(f"   ❌ {method} {endpoint} - Error: {e} (likely doesn't exist)")

    print("\n" + "=" * 50)
    print("🏁 Endpoint Testing Complete")

if __name__ == "__main__":
    asyncio.run(test_endpoints())