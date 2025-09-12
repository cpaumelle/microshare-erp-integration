#!/bin/bash
# Microshare ERP Integration v2.0 - Secure Installer

set -e

echo "🚀 Installing Microshare ERP Integration v2.0..."

# Install dependencies
python3 -m pip install -r requirements.txt --break-system-packages

# Create .env with user-provided credentials
echo "📝 Configuration Setup"
echo "Enter your Microshare credentials:"
read -p "Username/Email: " username
read -s -p "Password: " password
echo

# Create .env file
cat > .env << EOF_ENV
MICROSHARE_AUTH_URL=https://dauth.microshare.io
MICROSHARE_API_URL=https://dapi.microshare.io
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
