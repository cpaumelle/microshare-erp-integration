#!/usr/bin/env python3
"""
Frontend and API Server Launcher
Serves both the FastAPI backend and static frontend files
"""

import os
import sys
import time
import signal
import threading
import subprocess
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse

# Add project root to Python path
project_root = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(project_root))

class FrontendHandler(SimpleHTTPRequestHandler):
    """Custom handler for serving frontend files with proper routing"""

    def __init__(self, *args, **kwargs):
        # Set the directory to serve from
        self.frontend_dir = project_root / 'frontend'
        super().__init__(*args, directory=str(self.frontend_dir), **kwargs)

    def do_GET(self):
        """Handle GET requests with SPA routing"""

        # Parse the URL
        parsed = urlparse(self.path)
        path = parsed.path

        # Handle root requests
        if path == '/':
            path = '/index.html'

        # Handle SPA routing - serve index.html for unknown routes
        file_path = self.frontend_dir / path.lstrip('/')

        if not file_path.exists() and not path.startswith('/api/'):
            # For non-API routes that don't exist, serve index.html (SPA routing)
            if not any(path.endswith(ext) for ext in ['.css', '.js', '.html', '.png', '.jpg', '.ico']):
                self.path = '/index.html'

        # Add CORS headers for development
        self.send_cors_headers()

        # Call the parent handler
        super().do_GET()

    def send_cors_headers(self):
        """Add CORS headers for development"""
        # This is already handled by do_GET, but we ensure CORS headers are set
        pass

    def end_headers(self):
        """Add CORS headers and cache control before ending headers"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')

        # Add cache-busting headers for development
        if self.path.endswith(('.js', '.css', '.html')):
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')

        super().end_headers()

def start_api_server():
    """Start the FastAPI backend server"""

    print("🚀 Starting FastAPI backend server...")

    try:
        # Import and start the API
        from api.main import app
        import uvicorn

        # Run uvicorn in a separate thread
        def run_api():
            uvicorn.run(
                app,
                host="0.0.0.0",
                port=8000,
                log_level="info",
                access_log=True
            )

        api_thread = threading.Thread(target=run_api, daemon=True)
        api_thread.start()

        # Wait a moment for the server to start
        time.sleep(2)
        print("✅ FastAPI backend started on http://localhost:8000")

        return api_thread

    except Exception as e:
        print(f"❌ Failed to start API server: {e}")
        sys.exit(1)

def start_frontend_server(port=3000):
    """Start the frontend static file server"""

    print(f"🌐 Starting frontend server on port {port}...")

    try:
        # Create server (listen on all interfaces for VM access)
        server = HTTPServer(('0.0.0.0', port), FrontendHandler)

        print(f"✅ Frontend server started on http://localhost:{port}")
        print(f"📁 Serving files from: {project_root / 'frontend'}")

        return server

    except Exception as e:
        print(f"❌ Failed to start frontend server: {e}")
        sys.exit(1)

def check_dependencies():
    """Check if required dependencies are available"""

    print("🔍 Checking dependencies...")

    try:
        import uvicorn
        import fastapi
        print("✅ FastAPI and Uvicorn available")
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("📦 Install with: pip install -r requirements.txt")
        sys.exit(1)

    # Check if frontend directory exists
    frontend_dir = project_root / 'frontend'
    if not frontend_dir.exists():
        print(f"❌ Frontend directory not found: {frontend_dir}")
        sys.exit(1)

    print("✅ All dependencies satisfied")

def show_startup_info():
    """Show startup information and URLs"""

    print("\n" + "="*60)
    print("🔗 MICROSHARE ERP INTEGRATION - FULL STACK SERVER")
    print("="*60)
    print()
    print("📊 BACKEND (API):")
    print("   • URL: http://localhost:8000")
    print("   • API Docs: http://localhost:8000/docs")
    print("   • Health: http://localhost:8000/health")
    print()
    print("🌐 FRONTEND (Web UI):")
    print("   • URL: http://localhost:3000")
    print("   • Login: http://localhost:3000/")
    print("   • Dashboard: http://localhost:3000/dashboard-new.html")
    print()
    print("🔧 DEVELOPMENT:")
    print("   • All files served from ./frontend/")
    print("   • CORS enabled for cross-origin requests")
    print("   • Auto-reload: Restart script to update backend")
    print()
    print("⚡ READY TO USE:")
    print("   1. Open http://localhost:3000 in your browser")
    print("   2. Login with demo credentials (pre-filled)")
    print("   3. Explore device management features")
    print()
    print("Press Ctrl+C to stop all servers")
    print("="*60)

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print("\n🛑 Shutting down servers...")
    sys.exit(0)

def main():
    """Main function to start both servers"""

    # Set up signal handling
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print("🚀 Microshare ERP Integration - Full Stack Launcher")
    print(f"📂 Project root: {project_root}")

    # Check dependencies
    check_dependencies()

    # Start API server
    api_thread = start_api_server()

    # Start frontend server
    frontend_server = start_frontend_server(port=3000)

    # Show information
    show_startup_info()

    try:
        # Run the frontend server (this blocks)
        frontend_server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Received shutdown signal")
    finally:
        print("🧹 Cleaning up...")
        frontend_server.shutdown()
        frontend_server.server_close()
        print("✅ Servers stopped")

if __name__ == "__main__":
    main()