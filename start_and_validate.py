#!/usr/bin/env python3
"""
Start API server in background and run validation
"""
import sys
import os
import time
import subprocess
import signal
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def start_server_and_validate():
    """Start API server in background and run validation"""

    print("🚀 Starting Microshare ERP Integration v3.0...")

    # Start server in background
    server_process = subprocess.Popen([
        sys.executable, "start_api.py"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    print(f"📡 Server starting (PID: {server_process.pid})...")
    print("⏳ Waiting 5 seconds for server to initialize...")
    time.sleep(5)

    # Check if server is still running
    if server_process.poll() is not None:
        stdout, stderr = server_process.communicate()
        print("❌ Server failed to start:")
        print(stdout.decode())
        print(stderr.decode())
        return False

    print("✅ Server started successfully!")
    print("🔍 Running deployment validation...")
    print()

    try:
        # Run validation
        result = subprocess.run([
            sys.executable, "scripts/validate_deployment.py"
        ], capture_output=False, text=True)

        validation_success = result.returncode == 0

        print()
        if validation_success:
            print("✅ Validation completed successfully!")
        else:
            print("⚠️ Validation completed with issues")

    except Exception as e:
        print(f"❌ Validation failed: {e}")
        validation_success = False

    print()
    print("📡 Server Information:")
    print(f"   PID: {server_process.pid}")
    print(f"   URL: http://localhost:8000")
    print(f"   Docs: http://localhost:8000/docs")
    print(f"   Health: http://localhost:8000/health")
    print()
    print("🛑 To stop the server:")
    print(f"   kill {server_process.pid}")
    print("   or press Ctrl+C if running in foreground")

    return validation_success

if __name__ == "__main__":
    try:
        success = start_server_and_validate()
        if success:
            print("\n🎉 Setup complete! Server running in background.")
        else:
            print("\n⚠️ Setup completed with validation issues.")
    except KeyboardInterrupt:
        print("\n\n🛑 Setup interrupted by user")
        sys.exit(1)