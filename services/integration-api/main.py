"""
FastAPI main application with proper error handling and cached operations
"""
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx

# Import our modules
from src.microshare_client.client import MicroshareDeviceClient
from src.microshare_client.exceptions import MicroshareAPIError, AuthenticationError
from routes import health, device_crud, erp_sync, erp_discovery

# Create FastAPI app
app = FastAPI(
    title="Microshare ERP Integration API - Cached Version",
    description="API-first sample with caching for ERP integration with Microshare EverSmart Rodent",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handlers
@app.exception_handler(MicroshareAPIError)
async def microshare_api_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "Microshare API Error", "detail": exc.message}
    )

@app.exception_handler(AuthenticationError) 
async def auth_exception_handler(request, exc):
    return JSONResponse(
        status_code=401,
        content={"error": "Authentication Error", "detail": exc.message}
    )

@app.exception_handler(httpx.TimeoutException)
async def timeout_exception_handler(request, exc):
    return JSONResponse(
        status_code=408,
        content={"error": "Request Timeout", "detail": "The request to Microshare API timed out"}
    )

# Include routers with proper prefixes
app.include_router(health.router, prefix="/api/v1")
app.include_router(device_crud.router, prefix="/api/v1") 
app.include_router(erp_sync.router, prefix="/api/v1/erp")
app.include_router(erp_discovery.router, prefix="/api/v1")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Microshare ERP Integration API - Cached Version",
        "version": "2.0.0",
        "features": [
            "Device cluster discovery with caching",
            "Device CRUD operations with cache invalidation", 
            "ERP synchronization endpoints",
            "ERP discovery and mapping analysis",
            "Performance optimized with TTL cache"
        ],
        "endpoints": {
            "health": "/api/v1/health",
            "clusters": "/api/v1/devices/clusters", 
            "devices": "/api/v1/devices/",
            "erp_status": "/api/v1/erp/status",
            "erp_discovery": "/api/v1/erp/discovery/mapping",
            "cache_stats": "/api/v1/cache/stats",
            "docs": "/docs"
        }
    }

# Cache management endpoint
@app.get("/api/v1/cache/stats")
async def cache_stats():
    """Get cache statistics"""
    from src.microshare_client.cache import cluster_cache
    cached_items = len(cluster_cache._cache)
    expired_count = cluster_cache.cleanup_expired()
    return {
        "cached_items": cached_items,
        "expired_items_cleaned": expired_count,
        "cache_keys": list(cluster_cache._cache.keys())
    }

@app.delete("/api/v1/cache")
async def clear_cache():
    """Clear all cache entries"""
    from src.microshare_client.cache import cluster_cache
    cluster_cache.clear()
    return {"message": "Cache cleared successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
