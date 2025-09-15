# Microshare ERP Integration - Developer Guide

## Overview

This is a **production-ready sample application** demonstrating how to integrate Enterprise Resource Planning (ERP) systems with Microshare IoT platform. The sample provides:

- **FastAPI backend** for ERP-IoT synchronization
- **Real device management** with full CRUD operations
- **Authentication patterns** for Microshare API
- **Caching strategies** for production workloads
- **Docker deployment** configuration

## What This Sample Demonstrates

### Core Integration Patterns
- **ERP Integration Framework** - Abstract patterns ready for concrete ERP implementations
- **Device lifecycle management** from creation to deployment tracking
- **Location hierarchy mapping** using standardized 6-layer arrays
- **Bidirectional sync patterns** - Architectural foundation for ERP ↔ IoT sync

### Technical Architecture
- **FastAPI** modern async Python web framework
- **Pydantic v2** for data validation and configuration
- **httpx** async HTTP client for external API integration
- **Smart caching** for sub-second response times
- **Modular design** supporting any ERP system

## Quick Start

### Prerequisites
- Python 3.11+
- Docker and Docker Compose (optional)
- Access to Microshare platform (demo credentials included)

**Note**: Modern Python environments (Ubuntu 24.04+, Python 3.12+) use `--break-system-packages` flag for global installs, which is included in all our installation commands.

### 5-Minute Setup

```bash
# Clone the repository (use v3.0-github-ready for latest fixes)
git clone -b v3.0-github-ready https://github.com/cpaumelle/microshare-erp-integration.git
cd microshare-erp-integration

# Copy working demo credentials
cp .env.example .env

# Install dependencies
python3 -m pip install -r requirements.txt --break-system-packages

# Start server + validate automatically (recommended for testing)
PYTHONPATH=. python3 start_and_validate.py

# Or start server only
PYTHONPATH=. python3 start_api.py
```

### Verify Installation

```bash
# Check health
curl http://localhost:8000/health

# View interactive API documentation
open http://localhost:8000/docs

# Test device discovery
curl http://localhost:8000/api/v1/devices/
```

## Application Architecture

### Project Structure

```
microshare-erp-integration/
├── api/                          # FastAPI application
│   ├── auth/                     # Authentication modules
│   │   ├── auth.py              # Microshare authentication
│   │   ├── middleware.py        # Auth middleware
│   │   └── web_client.py        # Web authentication client
│   ├── devices/                  # Device management
│   │   ├── crud.py              # CRUD operations
│   │   ├── routes.py            # API endpoints
│   │   ├── operations.py        # Core device operations
│   │   ├── models.py            # Data models
│   │   └── client.py            # Microshare API client
│   ├── config/                   # Configuration
│   │   └── settings.py          # Application settings
│   └── main.py                  # FastAPI application
├── frontend/                     # Web interface (demo)
├── scripts/                      # Utility scripts
├── performance_testing.py        # Performance benchmarking
├── validate_deployment.py        # Deployment validation
└── start_api.py                 # Application entry point
```

### Key Components

#### 1. Authentication System (`api/auth/`)
- **Web-based authentication** using username/password (no API keys required)
- **JWT token management** with automatic refresh
- **Multi-environment support** (development/production)

#### 2. Device Management (`api/devices/`)
- **CRUD operations** for IoT devices within Microshare clusters
- **Location hierarchy mapping** with 6-element location arrays
- **Device type support** for rodent sensors and gateways
- **Smart caching** for sub-second response times

#### 3. ERP Integration Framework
- **Abstract ERP adapter patterns** in `src/erp_adapter/` ready for implementation
- **Standardized mapping logic** between ERP references and IoT device locations (location[3] field)
- **Pluggable architecture** supporting multiple ERP systems
- **Sync pattern templates** for bidirectional data flow

## Core Concepts

### Device Clusters vs Devices

**Critical distinction for developers:**
- **Clusters**: Read-only containers that group devices by type and location
- **Devices**: The actual IoT devices that can be created, updated, and deleted
- **Never modify clusters** - only manage devices within existing clusters

### Core Architecture Principles

#### Clusters vs Devices - Critical Distinction

**Essential concept for all developers:**
- **CLUSTERS**: Read-only containers that define location hierarchy and device grouping
- **DEVICES**: The actual IoT devices within clusters that can be CRUD'd
- **NEVER create or modify clusters** - only manage devices within existing clusters

#### Device Types

#### Rodent Sensors (`io.microshare.trap.packed`)
**Standard 6-Layer Location Array:**
```json
{
  "id": "device-eui-string",
  "meta": {
    "location": [
      "Customer Name",         // [0] Customer/Organization
      "Site Name",            // [1] Site/Facility
      "Area Name",            // [2] Area/Zone
      "ERP_Reference",        // [3] CRITICAL: ERP internal reference
      "Internal",             // [4] Placement: Internal | External
      "Bait/Lured"           // [5] Configuration type
    ]
  },
  "status": "pending | active | inactive",
  "device_type": "rodent_sensor",
  "cluster_id": "cluster-identifier"
}
```

#### Gateway Devices (`io.microshare.gateway.health.packed`)
**Standard 4-Layer Location Array:**
```json
{
  "id": "gateway-eui-string",
  "meta": {
    "location": [
      "Customer Name",        // [0] Customer/Organization
      "Site Name",           // [1] Site/Facility
      "Area Name",           // [2] Coverage area
      "Gateway_Location"     // [3] Gateway identifier
    ]
  },
  "status": "active | inactive",
  "device_type": "gateway",
  "cluster_id": "gateway-cluster-id"
}
```

**Performance Note**: Extended location arrays beyond standard 6/4 layers may impact query performance.

### ERP Integration Mapping

The `location[3]` field serves as the **critical link** between ERP systems and IoT devices:

```python
def map_erp_to_device(erp_inspection_point):
    """Map ERP inspection point to Microshare device"""
    return {
        "id": "00-00-00-00-00-00-00-00",  # Default - deployment handles actual DevEUI
        "meta": {
            "location": [
                erp_inspection_point.customer,
                erp_inspection_point.site,
                erp_inspection_point.area,
                erp_inspection_point.internal_reference,  # CRITICAL: ERP linkage
                erp_inspection_point.placement or "Internal",
                erp_inspection_point.configuration or "Bait/Lured"
            ]
        },
        "status": "pending",
        "guid": f"erp-sync-{erp_inspection_point.id}"
    }
```

## API Reference

**⚠️ IMPORTANT**: For complete API documentation, see **[API_REFERENCE.md](docs/API_REFERENCE.md)** - the definitive source for all endpoints.

### Quick Reference - Verified Endpoints

```python
# Authentication
POST /api/v1/auth/login     # Returns session_token
GET  /api/v1/auth/status    # Auth status

# Device Management
GET    /api/v1/devices/           # List all devices
POST   /api/v1/devices/create     # Create device (NOTE: /create endpoint)
PUT    /api/v1/devices/{device_id} # Update device
DELETE /api/v1/devices/{device_id} # Delete device

# System Monitoring
GET /health                            # Health check
GET /api/v1/status                     # Detailed status
GET /api/v1/devices/cache/status       # Cache monitoring
GET /api/v1/devices/performance/benchmark # Performance metrics
```

**Authentication Pattern**:
```bash
# Get session token
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user@example.com", "password": "password"}' \
  | jq -r '.session_token')

# Use in authenticated requests
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/devices/
```

## Configuration

### Environment Variables

```bash
# Microshare API Configuration
MICROSHARE_AUTH_URL=https://dauth.microshare.io      # Development
MICROSHARE_API_URL=https://dapi.microshare.io        # Development
MICROSHARE_USERNAME=your-username@company.com
MICROSHARE_PASSWORD=your-secure-password

# Production URLs
MICROSHARE_AUTH_URL=https://auth.microshare.io       # Production
MICROSHARE_API_URL=https://api.microshare.io         # Production

# Application Settings
LOG_LEVEL=INFO
CACHE_TTL=300
API_TIMEOUT=30
```

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Check container health
docker-compose ps

# View logs
docker-compose logs -f api
```

## Development Workflow

### Setting Up Development Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest black isort

# Set up pre-commit hooks (optional)
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=api

# Run specific test file
pytest tests/test_devices.py

# Run integration tests
pytest tests/integration/
```

### Code Quality

```bash
# Format code
black .

# Sort imports
isort .

# Type checking
mypy api/

# Linting
flake8 api/
```

## Performance Considerations

### Caching Strategy
- **Smart cache** with surgical updates instead of full cache clearing
- **Cluster mapping cache** eliminates redundant discovery calls
- **TTL-based refresh** for data consistency
- **Memory-efficient** storage of device mappings

### API Patterns
- **Async operations** for concurrent processing
- **Connection pooling** for external API calls
- **Request batching** for bulk operations
- **Error handling** with exponential backoff

### Benchmarks
- **Authentication**: ~900ms average
- **Device discovery**: 7 devices across 2 clusters
- **Cached operations**: <100ms response time
- **CRUD operations**: ~1 second average

## Troubleshooting

### Common Issues

#### Authentication Failures
```bash
# Error: 401 Unauthorized
# Solution: Check credentials in .env file
cp .env.example .env
# Edit with your credentials
```

#### Import Errors
```bash
# Error: ModuleNotFoundError: No module named 'api'
# Solution: Set Python path
PYTHONPATH=. python3 start_api.py
```

#### Dependency Issues
```bash
# Error: "externally-managed-environment" (Ubuntu 24.04+)
# Solution: Use break-system-packages flag
python3 -m pip install -r requirements.txt --break-system-packages

# Error: Missing pydantic_settings
# Solution: Install dependencies with flag
pip install -r requirements.txt --break-system-packages
```

### Debugging

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check API connectivity
curl -v http://localhost:8000/health

# Validate configuration
python3 -c "from api.config.settings import settings; print(settings)"
```

## Integration Examples

### Basic ERP Sync Pattern

**Note**: This demonstrates the pattern for future ERP implementations. Current system has abstract ERP framework ready.

```python
import httpx

async def sync_erp_inspection_points():
    """Example: Sync ERP inspection points to Microshare devices"""
    base_url = "http://localhost:8000"

    # Authenticate with FastAPI
    async with httpx.AsyncClient() as client:
        auth_response = await client.post(f"{base_url}/api/v1/auth/login", json={
            "username": "your-username@company.com",
            "password": "your-password"
        })

        token = auth_response.json()["session_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Get ERP inspection points (your implementation)
        erp_points = get_erp_inspection_points()

        for point in erp_points:
            device_data = {
                "customer": point.customer,
                "site": point.site,
                "area": point.area,
                "erp_reference": point.internal_reference,  # Critical for sync
                "placement": point.placement or "Internal",
                "configuration": point.configuration or "Bait/Lured",
                "device_type": "rodent_sensor"
            }

            # Create device using correct endpoint
            result = await client.post(
                f"{base_url}/api/v1/devices/create",  # Note: /create endpoint
                json=device_data,
                headers=headers
            )

            print(f"Created device for {point.internal_reference}: {result.status_code}")
```

### Custom ERP Adapter

```python
class CustomERPAdapter:
    """Example ERP adapter implementation"""

    def __init__(self, erp_connection):
        self.erp = erp_connection

    def get_inspection_points(self):
        """Get inspection points from your ERP system"""
        # Your ERP-specific logic here
        return self.erp.query("SELECT * FROM inspection_points WHERE active = 1")

    def map_to_microshare_device(self, erp_point):
        """Map ERP point to Microshare device format"""
        return {
            "id": "00-00-00-00-00-00-00-00",
            "meta": {
                "location": [
                    erp_point.customer_name,
                    erp_point.site_name,
                    erp_point.area_name,
                    erp_point.reference_code,  # Your ERP reference
                    erp_point.placement_type,
                    erp_point.device_config
                ]
            },
            "status": "pending",
            "guid": f"custom-erp-{erp_point.id}"
        }

    async def sync_to_microshare(self, microshare_crud):
        """Sync ERP data to Microshare"""
        points = self.get_inspection_points()

        for point in points:
            device = self.map_to_microshare_device(point)
            await microshare_crud.create_device(device)
```

## Production Deployment

### Environment Setup

```bash
# Production environment variables
export MICROSHARE_AUTH_URL=https://auth.microshare.io
export MICROSHARE_API_URL=https://api.microshare.io
export LOG_LEVEL=WARNING
export CACHE_TTL=600

# Security considerations
export SECRET_KEY=your-production-secret
export ALLOWED_HOSTS=your-domain.com
```

### Docker Production

```dockerfile
# Dockerfile.prod
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Health Monitoring

```bash
# Health check endpoint
curl http://localhost:8000/health

# Detailed status
curl http://localhost:8000/api/v1/status

# Performance metrics
curl http://localhost:8000/api/v1/devices/performance/benchmark
```

## Support and Resources

### Documentation
- **API Documentation**: http://localhost:8000/docs (when running)
- **Microshare Platform**: https://docs.microshare.io
- **FastAPI Framework**: https://fastapi.tiangolo.com

### Getting Help
- **GitHub Issues**: For bugs and feature requests
- **Microshare Support**: support@microshare.io
- **Community**: Microshare developer forums

### License
This sample application is provided under the MIT License. See LICENSE file for details.

---

## Next Steps

1. **Explore the API** - Start the server and visit http://localhost:8000/docs
2. **Run the tests** - Execute `pytest` to understand the test patterns
3. **Review the code** - Study the implementation in `api/` directory
4. **Integrate your ERP** - Use the patterns to connect your specific ERP system
5. **Deploy to production** - Follow the deployment guide for your environment

This sample provides a solid foundation for building production ERP-IoT integrations with Microshare.