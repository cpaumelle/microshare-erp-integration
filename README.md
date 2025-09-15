# Microshare ERP Integration

**Production-ready sample application** demonstrating ERP-IoT integration with Microshare platform.

## What This Is

This sample provides:
- **FastAPI backend** for ERP-Microshare synchronization
- **Real device management** with full CRUD operations
- **Authentication patterns** for Microshare API integration
- **Caching strategies** for production workloads
- **Docker deployment** configuration

## Quick Start

```bash
# Clone and setup (use v3.0-github-ready branch for latest fixes)
git clone -b v3.0-github-ready https://github.com/cpaumelle/microshare-erp-integration.git
cd microshare-erp-integration
cp .env.example .env  # Demo credentials included

# Install dependencies
python3 -m pip install -r requirements.txt --break-system-packages

# Option 1: Start server + run validation automatically
PYTHONPATH=. python3 start_and_validate.py

# Option 2: Start server only (foreground)
PYTHONPATH=. python3 start_api.py
```

**Verify installation:**
```bash
curl http://localhost:8000/health
open http://localhost:8000/docs  # Interactive API documentation
```

## Key Features

- **Web Authentication**: Username/password (no API keys required)
- **Device CRUD**: Complete create/read/update/delete operations
- **Smart Caching**: Sub-second response times
- **Multi-Environment**: Development and production support
- **Docker Ready**: Production deployment configuration
- **Working Demo**: 7 devices across 2 clusters discoverable

## Architecture

```
api/
├── auth/           # Microshare authentication
├── devices/        # Device CRUD and operations
├── config/         # Application configuration
└── main.py         # FastAPI application
```

**Core Technologies:**
- FastAPI + Pydantic v2
- httpx for async HTTP
- Smart caching system
- Docker deployment

## Documentation

- **[Developer Guide](DEVELOPER_GUIDE.md)** - Complete development documentation
- **[API Docs](http://localhost:8000/docs)** - Interactive API documentation (when running)
- **[Device CRUD Guide](microshare_device_crud.md)** - Detailed device operations
- **[Credentials Setup](docs/MICROSHARE_CREDENTIALS.md)** - Getting Microshare access

## Configuration

```bash
# .env file (demo credentials included)
MICROSHARE_AUTH_URL=https://dauth.microshare.io      # Development
MICROSHARE_API_URL=https://dapi.microshare.io        # Development
MICROSHARE_USERNAME=your-username@company.com
MICROSHARE_PASSWORD=your-secure-password
```

## Docker Deployment

```bash
docker-compose up --build
```

## Validation

```bash
# Test your deployment
PYTHONPATH=. python3 start_api.py &
python3 validate_deployment.py
```

## Support

- **GitHub Issues**: Bug reports and feature requests
- **Microshare Support**: support@microshare.io
- **Documentation**: See [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) for complete details

## License

MIT License - see LICENSE file for details.