#!/bin/bash
# Microshare ERP Integration v2.0 - Enhanced Installer

set -e

echo "🚀 Installing Microshare ERP Integration v2.0..."

# Install dependencies (including pydantic-settings)
python3 -m pip install -r requirements.txt pydantic-settings --break-system-packages

echo "📝 Configuration Setup"

# Environment selection
echo "Select Microshare environment:"
echo "1) Development (dapp.microshare.io/dapi.microshare.io)"
echo "2) Production (app.microshare.io/api.microshare.io)" 
read -p "Enter choice (1 or 2): " env_choice

if [ "$env_choice" = "1" ]; then
    AUTH_URL="https://dauth.microshare.io"
    API_URL="https://dapi.microshare.io"
    echo "Selected: Development environment"
elif [ "$env_choice" = "2" ]; then
    AUTH_URL="https://auth.microshare.io"
    API_URL="https://api.microshare.io"
    echo "Selected: Production environment"
else
    echo "Invalid choice, defaulting to Development"
    AUTH_URL="https://dauth.microshare.io"
    API_URL="https://dapi.microshare.io"
fi

# Get credentials
echo "Enter your Microshare credentials:"
read -p "Username/Email: " username
read -s -p "Password: " password
echo

# Create .env file
cat > .env << EOF_ENV
MICROSHARE_AUTH_URL=$AUTH_URL
MICROSHARE_API_URL=$API_URL
MICROSHARE_USERNAME=$username
MICROSHARE_PASSWORD=$password
DEVICE_RECORD_TYPE=io.microshare.trap.packed
GATEWAY_RECORD_TYPE=io.microshare.gateway.health.packed
INCIDENT_RECORD_TYPE=io.microshare.demo.sensor.unpacked
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
DEBUG=false
CACHE_TTL=300
API_TIMEOUT=30
EOF_ENV

echo "✅ Installation complete!"
echo ""
echo "🚀 Choose next step:"
echo "1) Start API server (PYTHONPATH=. python3 start_api.py)"
echo "2) Start API server in background and validate deployment"
echo "3) Just validate deployment (server must be running)"
echo ""
read -p "Enter choice (1-3): " next_choice

if [ "$next_choice" = "2" ]; then
    echo "🔄 Starting API server in background..."
    PYTHONPATH=. python3 start_api.py &
    SERVER_PID=$!
    echo "API server started (PID: $SERVER_PID)"
    echo "📖 API docs: http://localhost:8000/docs"
    echo "🔍 Health check: http://localhost:8000/health"
    echo ""
    echo "⏳ Waiting 5 seconds for server to start..."
    sleep 5
    echo ""
    echo "🧪 Running deployment validation..."
    python3 validate_deployment.py
    echo ""
    echo "✅ Validation complete!"
    echo "🛑 To stop the server: kill $SERVER_PID"
elif [ "$next_choice" = "3" ]; then
    echo "🧪 Running deployment validation..."
    echo "Note: Make sure API server is running on port 8000"
    python3 validate_deployment.py
else
    echo "🚀 Start the API with: PYTHONPATH=. python3 start_api.py"
fi

echo "📖 API docs will be available at: http://localhost:8000/docs"
echo "🔍 Health check: http://localhost:8000/health"
