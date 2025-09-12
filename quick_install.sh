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
# Microshare Configuration
MICROSHARE_AUTH_URL=$AUTH_URL
MICROSHARE_API_URL=$API_URL
MICROSHARE_USERNAME=$username
MICROSHARE_PASSWORD=$password

# Record Types
DEVICE_RECORD_TYPE=io.microshare.trap.packed
GATEWAY_RECORD_TYPE=io.microshare.gateway.health.packed
INCIDENT_RECORD_TYPE=io.microshare.demo.sensor.unpacked

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
DEBUG=false

# Performance & Caching
CACHE_TTL=300
API_TIMEOUT=30
EOF_ENV

echo "✅ Installation complete!"
echo "🚀 Start the API with: PYTHONPATH=. python3 start_api.py"
echo "📖 API docs will be available at: http://localhost:8000/docs"
echo "🔍 Health check: http://localhost:8000/health"
