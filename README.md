# Microshare ERP Integration v2.0

Clean, production-ready FastAPI backend for Microshare device management and ERP integration.

## Quick Installation (Recommended)
```bash
git clone https://github.com/cpaumelle/microshare-erp-integration.git
cd microshare-erp-integration
./quick_install.sh
PYTHONPATH=. python3 start_api.py
The installer will:

Install all dependencies automatically
Ask for your Microshare environment (dev/prod)
Prompt for your credentials securely
Configure the application properly

Manual Installation
If you prefer manual setup:
bashgit clone https://github.com/cpaumelle/microshare-erp-integration.git
cd microshare-erp-integration
python3 -m pip install -r requirements.txt --break-system-packages

# Create .env file with your settings
cp .env.example .env
# Edit .env with your Microshare credentials and environment

# Start the API
PYTHONPATH=. python3 start_api.py
Configuration
The application requires Microshare credentials in .env file:
bashMICROSHARE_AUTH_URL=https://dauth.microshare.io  # or https://auth.microshare.io for prod
MICROSHARE_API_URL=https://dapi.microshare.io    # or https://api.microshare.io for prod
MICROSHARE_USERNAME=your-username@company.com
MICROSHARE_PASSWORD=your-secure-password
Key Features

Web App Authentication: No API keys needed - just username/password
Performance Optimized: 45x faster device retrieval with caching
Clean Architecture: Fixed Python imports, no container crashes
Multi-Environment: Supports both development and production Microshare
Production Ready: Docker deployment with health checks
Validated Performance: 7 devices across 2 clusters discovery

API Documentation
After starting the server:

API Documentation: http://localhost:8000/docs
Health Check: http://localhost:8000/health
API Status: http://localhost:8000/api/v1/status

Docker Deployment
bashdocker-compose up --build
Troubleshooting
"Field required" error for username/password

Cause: Missing or incomplete .env file
Solution: Run ./quick_install.sh or manually create .env with credentials

"ModuleNotFoundError: No module named 'api'"

Cause: Python path issue
Solution: Use PYTHONPATH=. python3 start_api.py

"ModuleNotFoundError: No module named 'pydantic_settings'"

Cause: Missing dependency
Solution: Run ./quick_install.sh or pip install pydantic-settings --break-system-packages

Migration from v1.x
This v2.0 release represents a complete architectural rewrite:

Fixed all Python import structure issues
Eliminated container crashes and startup failures
Implemented web-based authentication system
Added performance optimization with 45x improvement
Production-ready deployment with comprehensive health checks

Support

GitHub Issues: Report bugs or request features
API Documentation: Complete endpoint documentation at /docs
Health Monitoring: Status endpoint at /health

Architecture

FastAPI 0.104+: Modern async Python web framework
Pydantic v2: Data validation and settings management
httpx: Async HTTP client for Microshare integration
Docker: Containerized deployment with health checks

Performance Benchmarks

Authentication: ~900ms
Device Discovery: 7 devices, 2 clusters
Direct Cluster Access: ~500ms per cluster
Concurrent Operations: Optimized parallel processing
