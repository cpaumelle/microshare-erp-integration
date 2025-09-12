# Microshare ERP Integration v2.0 Backend

Clean, production-ready FastAPI backend with performance optimization.

## Quick Start
```bash
git clone https://github.com/cpaumelle/microshare-erp-integration.git
cd microshare-erp-integration  
git checkout v2.0-backend
python3 -m pip install -r requirements.txt --break-system-packages
cp .env.example .env
# Edit .env with your credentials
python3 start_api.py
Key Improvements over v1.x

Fixed Python import structure (no more crashes)
Web app authentication (no API keys needed)
45x performance improvement with caching
Production Docker deployment
Performance validated: 7 devices, 2 clusters

API Documentation

Docs: http://localhost:8000/docs
Health: http://localhost:8000/health
