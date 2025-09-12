"""
Microshare ERP Integration v2.0.0 - Main Application
Clean, production-ready FastAPI application
Version: 2.0.0
Last Updated: 2025-09-12 13:30:00 UTC
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from datetime import datetime

# Import routers
from api.devices.router import router as device_router
from api.config.settings import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Microshare ERP Integration API",
    description="Clean, production-ready API for Microshare device management",
    version="2.0.0",
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

# Include routers
app.include_router(device_router, prefix="/api/v1")

# Health check endpoints
@app.get("/health")
async def health_check():
    """Main health check endpoint"""
    return {
        "status": "healthy",
        "service": "microshare-erp-integration",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "environment": "development"
    }

@app.get("/api/v1/status")
async def api_status():
    """Detailed API status"""
    return {
        "api": {
            "status": "operational",
            "version": "2.0.0",
            "features": [
                "web_app_authentication",
                "device_cluster_management", 
                "optimized_performance",
                "concurrent_access"
            ]
        },
        "microshare": {
            "auth_url": settings.microshare_auth_url,
            "api_url": settings.microshare_api_url,
            "environment": "development"
        },
        "performance": {
            "cache_ttl": settings.cache_ttl,
            "api_timeout": settings.api_timeout
        }
    }

# Root endpoint
@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "Microshare ERP Integration API v2.0.0",
        "docs": "/docs",
        "health": "/health",
        "status": "/api/v1/status"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
