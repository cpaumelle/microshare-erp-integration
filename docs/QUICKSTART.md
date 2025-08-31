# Quick Start Guide - Microshare ERP Integration

Get up and running with the Microshare ERP Integration API in 5 minutes.

## Prerequisites

- Docker and Docker Compose installed
- Python 3.11+ (if running without Docker)
- Internet access to Microshare API endpoints

## 5-Minute Setup

### Step 1: Clone Repository
```bash
git clone https://github.com/microshare/microshare-erp-integration.git
cd microshare-erp-integration
```

### Step 2: Use Working Credentials
```bash
# Generic development credentials are already configured!
cp .env.example .env
```

### Step 3: Launch with Docker
```bash
docker-compose up -d
```

### Step 4: Verify Installation
```bash
# Check health
curl http://localhost:8000/health

# View API documentation
open http://localhost:8000/docs

# Test device discovery
curl http://localhost:8000/devices/locations
```

## What You Get

- **FastAPI service** running on port 8000
- **Working Microshare integration** with generic dev credentials
- **Complete CRUD operations** for device management
- **High-performance caching** with automatic refresh
- **Interactive API docs** at http://localhost:8000/docs

## Next Steps

1. **Explore the API** - Visit http://localhost:8000/docs
2. **Run tests** - `pytest` to validate functionality
3. **Check performance** - `python scripts/performance_benchmark.py`
4. **Integrate your ERP** - See examples/ directory for patterns

## Need Your Own Credentials?

See [MICROSHARE_CREDENTIALS.md](MICROSHARE_CREDENTIALS.md) for getting your own Microshare account.
