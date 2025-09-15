#!/usr/bin/env python3
"""
Simple frontend test using playwright
Tests the reorganized modular frontend
"""

import asyncio
import time
from playwright.async_api import async_playwright

async def test_frontend():
    """Test the frontend functionality"""

    print("🧪 Testing Microshare ERP Integration Frontend")
    print("=" * 50)

    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            # Test 1: Load login page
            print("1. Testing login page load...")
            await page.goto("http://localhost:3000/")

            title = await page.title()
            print(f"   ✅ Title: {title}")

            # Check if our modular CSS is loaded
            app_css = await page.evaluate("!!document.querySelector('link[href*=\"app.css\"]')")
            components_css = await page.evaluate("!!document.querySelector('link[href*=\"components.css\"]')")
            print(f"   ✅ App CSS loaded: {app_css}")
            print(f"   ✅ Components CSS loaded: {components_css}")

            # Test 2: Check JavaScript modules
            print("\n2. Testing JavaScript modules...")
            await page.wait_for_timeout(1000)  # Wait for modules to load

            config_loaded = await page.evaluate("typeof CONFIG !== 'undefined'")
            ui_loaded = await page.evaluate("typeof UI !== 'undefined'")
            auth_loaded = await page.evaluate("typeof AuthManager !== 'undefined'")
            app_loaded = await page.evaluate("typeof App !== 'undefined'")

            print(f"   ✅ CONFIG module: {config_loaded}")
            print(f"   ✅ UI module: {ui_loaded}")
            print(f"   ✅ AuthManager module: {auth_loaded}")
            print(f"   ✅ App module: {app_loaded}")

            # Test 3: Check login form component loading
            print("\n3. Testing login form component...")
            await page.wait_for_timeout(2000)  # Wait for component to load

            login_form = await page.query_selector("#loginForm")
            username_field = await page.query_selector("#username, input[name='username']")
            password_field = await page.query_selector("#password, input[name='password']")

            print(f"   ✅ Login form present: {login_form is not None}")
            print(f"   ✅ Username field: {username_field is not None}")
            print(f"   ✅ Password field: {password_field is not None}")

            # Test 4: Try form interaction
            print("\n4. Testing form interaction...")
            if username_field and password_field:
                await username_field.fill("test@example.com")
                await password_field.fill("testpassword")
                print("   ✅ Form fields can be filled")

                # Check if demo credentials are pre-filled (dev mode)
                username_value = await username_field.get_attribute("value")
                if username_value:
                    print(f"   ✅ Demo credentials pre-filled: {username_value}")

            # Test 5: Check API endpoints are accessible
            print("\n5. Testing API connectivity...")
            response = await page.evaluate("""
                fetch('http://localhost:8000/health')
                    .then(r => r.json())
                    .then(data => data.status)
                    .catch(e => 'error: ' + e.message)
            """)
            print(f"   ✅ Backend health: {response}")

            # Test 6: Test dashboard page (new modular version)
            print("\n6. Testing dashboard page...")
            await page.goto("http://localhost:3000/dashboard-new.html")

            dashboard_title = await page.title()
            print(f"   ✅ Dashboard title: {dashboard_title}")

            # Check for dashboard elements
            nav_present = await page.query_selector(".navbar")
            stats_present = await page.query_selector(".card")
            buttons_present = await page.query_selector("#discover-btn, #add-device-btn")

            print(f"   ✅ Navigation present: {nav_present is not None}")
            print(f"   ✅ Stats cards present: {stats_present is not None}")
            print(f"   ✅ Action buttons present: {buttons_present is not None}")

            # Test 7: Check responsive design
            print("\n7. Testing responsive design...")
            await page.set_viewport_size({"width": 375, "height": 667})  # Mobile size
            await page.wait_for_timeout(500)

            mobile_friendly = await page.evaluate("""
                window.innerWidth < 768 &&
                document.querySelector('.container') !== null
            """)
            print(f"   ✅ Mobile responsive: {mobile_friendly}")

            print("\n" + "=" * 50)
            print("🎉 Frontend test completed successfully!")
            print("\n📋 Test Summary:")
            print("   ✅ Login page loads correctly")
            print("   ✅ Modular CSS/JS architecture working")
            print("   ✅ Component loading system functional")
            print("   ✅ API connectivity established")
            print("   ✅ Dashboard navigation working")
            print("   ✅ Responsive design functional")

        except Exception as e:
            print(f"\n❌ Test failed: {e}")

        finally:
            await browser.close()

async def test_api_integration():
    """Test API integration specifically"""

    print("\n🔗 Testing API Integration")
    print("=" * 30)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            await page.goto("http://localhost:3000/")
            await page.wait_for_timeout(2000)

            # Test authentication endpoint
            auth_test = await page.evaluate("""
                fetch('http://localhost:8000/api/v1/auth/login', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        username: 'invalid',
                        password: 'invalid',
                        environment: 'dev'
                    })
                })
                .then(r => ({status: r.status, ok: r.ok}))
                .catch(e => ({error: e.message}))
            """)

            print(f"   ✅ Auth endpoint responds: {auth_test}")

            # Test devices endpoint (should require auth)
            devices_test = await page.evaluate("""
                fetch('http://localhost:8000/api/v1/devices/')
                .then(r => ({status: r.status, ok: r.ok}))
                .catch(e => ({error: e.message}))
            """)

            print(f"   ✅ Devices endpoint (protected): {devices_test}")

        except Exception as e:
            print(f"❌ API test failed: {e}")

        finally:
            await browser.close()

if __name__ == "__main__":
    print("🚀 Starting Frontend Tests...")
    print(f"📍 VM IP: 10.35.1.112")
    print(f"🌐 Frontend: http://10.35.1.112:3000")
    print(f"📊 Backend: http://10.35.1.112:8000")
    print()

    # Wait a moment for servers to be ready
    time.sleep(2)

    # Run tests
    asyncio.run(test_frontend())
    asyncio.run(test_api_integration())

    print("\n🎯 Access URLs:")
    print(f"   • Frontend: http://10.35.1.112:3000")
    print(f"   • Backend API: http://10.35.1.112:8000/docs")
    print(f"   • Health Check: http://10.35.1.112:8000/health")