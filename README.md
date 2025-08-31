# Microshare ERP Integration

Production-ready FastAPI service for ERP integration with Microshare EverSmart Rodent platform.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](docker-compose.yml)

## Quick Start (5 Minutes)

```bash
# 1. Clone and setup
git clone https://github.com/cpaumelle/microshare-erp-integration.git
cd microshare-erp-integration

# 2. Use working development credentials (already configured!)
cp .env.example .env

# 3. Launch with Docker
docker compose up -d

# 4. Validate deployment (RECOMMENDED)
./scripts/validate_deployment.sh
```

## Post-Deployment Validation

**Run the validation script to confirm everything works correctly:**

```bash
./scripts/validate_deployment.sh
```

**Expected Output:**
```
Phase 1: Basic Health Checks
  Health Check... PASS (0.01s)

Phase 2: Cache Performance Demo  
  Device Listing... PASS (19.57s)
    Second call (cached)... PASS (0.01s) [1779x faster]
  Cluster Info... PASS (0.01s)

Phase 3: System Metrics
  Device count: 7
```

**Performance Insights:**
- Initial API calls: 30-60 seconds (Microshare API fetch)
- Cached responses: <1 second (100-2000x speedup)
- Cache TTL: 300 seconds (5 minutes)

**If validation fails, this indicates a real issue - not a timeout problem.**

## Working API Endpoints

After validation passes, these endpoints are ready for use:

- **Health Check**: `GET /api/v1/health` - Service status and version
- **All Devices**: `GET /api/v1/devices/` - Returns all devices with location data (use 60s timeout)
- **Device Clusters**: `GET /api/v1/devices/clusters` - Returns cluster information with cache metadata
- **Specific Device**: `GET /api/v1/devices/{device_id}` - Get individual device details
- **API Documentation**: `http://localhost:8000/docs` - Interactive Swagger UI

## Developer Quick Commands

```bash
# Get device count (always use proper timeout)
curl -s --max-time 60 http://localhost:8000/api/v1/devices/ | jq '.devices | length'

# Monitor cache performance
curl -s http://localhost:8000/api/v1/cache/stats | jq .

# Clear cache for testing
curl -s -X DELETE http://localhost:8000/api/v1/cache

# Interactive documentation
open http://localhost:8000/docs
```

## Production Features

- **Enterprise Performance**: 0.011s cached response times (1000x improvement)
- **Complete Data Access**: 7 devices from 2 Microshare clusters
- **Professional Field Mapping**: customer, site, area, erp_reference, placement, configuration
- **Working Credentials**: Generic development access included in `.env.example`
- **Docker Ready**: One-command deployment with health checks
- **TTL Caching**: 300-second cache with automatic invalidation
- **Error Handling**: Comprehensive exception handling and logging

## Performance Metrics

Based on production testing with working Microshare credentials:

- **Device Count**: 7 devices (6 traps + 1 gateway)
- **Response Time**: 0.011s (cached), ~30s (initial load)
- **Cache Hit Rate**: Near 100% for repeated requests
- **Data Quality**: Complete 6-element location arrays with GPS coordinates
- **Uptime**: Docker health checks with automatic restart

## Data Structure

Each device includes:

```json
{
  "id": "58A0CB000011F85E",
  "customer": "Paris HQ",
  "site": "Rue Voltaire", 
  "area": "3eme etage",
  "erp_reference": "Boite 22",
  "placement": "internal",
  "configuration": "bait",
  "status": "pending",
  "cluster_id": "68b1357b3270e76ce8e4977e",
  "cluster_name": "ERP Sample App | Motion",
  "device_type": "io.microshare.trap.packed",
  "meta": {
    "location": ["Paris HQ", "Rue Voltaire", "3eme etage", "Boite 22", "internal", "bait"]
  },
  "state": {
    "updateDate": "2025-08-29T07:18:42.231Z",
    "location": {
      "coords": {
        "latitude": 47.45269293241441,
        "longitude": 8.558177665156517
      }
    }
  }
}
```

## Architecture

```
Your ERP System ←→ FastAPI Service ←→ Microshare Platform
                          ↓
                   TTL Cache + Processing
```

**Universal ERP Compatibility:**
- SAP, Salesforce, Microsoft Dynamics, Oracle ERP
- Custom ERP systems and databases
- Any system with REST API capabilities

## Configuration

### Environment Variables

Key settings in `.env`:

```env
# Microshare API Configuration  
MICROSHARE_AUTH_URL=https://dauth.microshare.io
MICROSHARE_API_URL=https://dapi.microshare.io
MICROSHARE_USERNAME=cp_erp_sample@maildrop.cc
MICROSHARE_PASSWORD=AVH7dbz!brt-rfn0tdk
MICROSHARE_API_KEY=4DA225C6-94AA-4600-8509-2661CC2A7724

# Performance Settings
API_TIMEOUT=60
CACHE_TTL=300
DEBUG=true
```

### Docker Deployment

The service includes:
- Multi-stage Dockerfile with production and development targets
- Health checks with curl and jq
- Automatic restart policies
- Volume mounts for logs and data
- Configurable timeout settings

## Troubleshooting

### Performance Expectations

**This is normal behavior:**
- First API call: 30-60 seconds (fetching from Microshare)
- Cached calls: <1 second
- Empty responses initially (until cache builds)

**This indicates a problem:**
- Validation script fails
- Health check returns errors
- Consistent timeouts >60 seconds

### Common Issues

**Container fails to start:**
```bash
docker compose logs microshare-api
# Check for import errors or missing environment variables
```

**API timeouts:**
```bash
# Always use proper timeouts for device endpoints
curl --max-time 60 http://localhost:8000/api/v1/devices/
```

**Authentication errors:**
```bash
# Test direct Microshare API access
TOKEN=$(curl -s "https://dauth.microshare.io/oauth2/token?username=cp_erp_sample@maildrop.cc&password=AVH7dbz!brt-rfn0tdk&client_id=4DA225C6-94AA-4600-8509-2661CC2A7724&grant_type=password&scope=ALL:ALL" | jq -r '.access_token')
echo "Token: $TOKEN"
```

## Documentation

- [Microshare Device CRUD Guide](docs/microshare_device_crud_guide.md) - Complete API documentation
- [Development Credentials](docs/MICROSHARE_CREDENTIALS.md) - Platform access guide
- [Docker Deployment](docker-compose.yml) - Production configuration

## Development

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run directly (development mode)
cd services/integration-api
python main.py

# Access at http://localhost:8000
```

### Docker Development

```bash
# Development mode with hot reload
docker compose -f docker-compose.dev.yml up -d
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Ready to integrate your ERP with Microshare?** Start with the 5-minute setup above, then run `./scripts/validate_deployment.sh` to confirm everything works.

For production deployment guidance, see [DEPLOYMENT.md](docs/DEPLOYMENT.md)
