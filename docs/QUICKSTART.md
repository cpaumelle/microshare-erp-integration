# Quick Start Guide

Get the Microshare ERP Integration sample running in 5 minutes.

## Prerequisites

- Python 3.11+
- Internet access to Microshare API endpoints
- Docker (optional)

## Installation

```bash
# Clone repository
git clone https://github.com/cpaumelle/microshare-erp-integration.git
cd microshare-erp-integration

# Use demo credentials
cp .env.example .env

# Install dependencies
python3 -m pip install -r requirements.txt

# Start the API
PYTHONPATH=. python3 start_api.py
```

## Verify Installation

```bash
# Check health
curl http://localhost:8000/health

# View API documentation
open http://localhost:8000/docs

# Test device discovery
curl http://localhost:8000/api/v1/devices/
```

## What You Get

- **FastAPI service** running on port 8000
- **Working Microshare integration** with demo credentials
- **Device CRUD operations** ready to use
- **Smart caching** for production-level performance
- **Interactive API docs** at http://localhost:8000/docs

## Next Steps

1. **Explore the API** - Visit http://localhost:8000/docs
2. **Read the docs** - See [DEVELOPER_GUIDE.md](../DEVELOPER_GUIDE.md)
3. **Test deployment** - Run `python3 validate_deployment.py`
4. **Integrate your ERP** - Study the patterns in the code

## Need Your Own Credentials?

See [MICROSHARE_CREDENTIALS.md](MICROSHARE_CREDENTIALS.md) for setting up your own Microshare account.

## Docker Alternative

```bash
docker-compose up --build
```

## Troubleshooting

**Import Errors:**
```bash
# Use Python path
PYTHONPATH=. python3 start_api.py
```

**Missing Dependencies:**
```bash
pip install -r requirements.txt
```

**Authentication Issues:**
```bash
# Check .env file exists and has credentials
cat .env
```