"""
Microshare ERP Integration v3.0.0
ERP Integration API with FastCRUDManager
Version: 3.0.0
Last Updated: 2025-09-14 07:35:00 UTC
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import logging
from datetime import datetime

# Import only essential optimized modules
from api.config.settings import settings
from api.auth.auth import router as auth_router
from api.devices.routes import router as device_router

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Microshare ERP Integration API",
    description="ERP Integration API using FastCRUDManager",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include essential routers FIRST (before static files)
app.include_router(auth_router)
app.include_router(device_router)

# Favicon route (simple fix)
@app.get("/favicon.ico")
async def favicon():
    from fastapi.responses import Response
    # Return empty 1x1 transparent PNG
    return Response(
        content=b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82',
        media_type="image/png"
    )

# Health check endpoints (before static files)
@app.get("/health")
async def health_check():
    """Main health check endpoint"""
    return {
        "status": "healthy",
        "service": "microshare-erp-integration",
        "version": "3.0.0",
        "timestamp": datetime.now().isoformat(),
        "cache_strategy": "Smart cache with surgical updates",
        "features": {
            "crud": True,
            "smart_cache": True,
            "authentication": True,
            "frontend_demo": True
        }
    }

@app.get("/api/v1/status")
async def api_status():
    """Enhanced API status with performance metrics"""
    return {
        "status": "running",
        "version": "3.0.0",
        "performance_tier": "PRODUCTION",
        "endpoints": {
            "devices": "available at /api/v1/devices/",
            "auth": "available at /api/v1/auth/login",
            "frontend": "available at /",
            "performance": "available at /api/v1/devices/performance/benchmark"
        },
        "system_details": {
            "crud_manager": "FastCRUDManager",
            "cache_manager": "SmartCacheManager",
            "discovery_pattern": "Uses cached cluster mapping",
            "cache_updates": "Surgical updates"
        },
        "authentication": {
            "login": "/api/v1/auth/login",
            "working_credentials": "cp_erp_sample@maildrop.cc"
        }
    }

# Serve frontend static files LAST (so it doesn't intercept API routes)
try:
    app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
except Exception as e:
    logger.warning(f"Could not mount frontend static files: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

