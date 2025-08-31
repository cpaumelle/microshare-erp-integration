"""
Health check and system status routes
"""
import httpx
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
import time

from dependencies import get_microshare_client
from src.microshare_client.client import MicroshareDeviceClient
from src.microshare_client.exceptions import MicroshareAPIError, AuthenticationError

router = APIRouter(tags=["Health & Status"])

@router.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "service": "Microshare ERP Integration API - Cached Version",
        "version": "2.0.0",
        "timestamp": time.time()
    }

@router.get("/health/microshare")
async def microshare_health_check(
    client: MicroshareDeviceClient = Depends(get_microshare_client)
):
    """Check Microshare API connectivity and authentication"""
    try:
        start_time = time.time()
        clusters = await client.list_all_clusters()
        execution_time = time.time() - start_time
        cluster_count = len(clusters.get('objs', []))
        
        return {
            "status": "healthy",
            "microshare_api": "connected",
            "authentication": "valid",
            "cluster_count": cluster_count,
            "response_time_seconds": round(execution_time, 3)
        }
        
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=f"Microshare authentication failed: {e.message}")
    except MicroshareAPIError as e:
        raise HTTPException(status_code=e.status_code, detail=f"Microshare API error: {e.message}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.get("/health/cache")
async def cache_health_check():
    """Check cache system status"""
    try:
        from src.microshare_client.cache import cluster_cache
        
        test_key = f"health_check_{int(time.time())}"
        test_value = {"test": "data", "timestamp": time.time()}
        
        cluster_cache.set(test_key, test_value, ttl=60)
        retrieved = cluster_cache.get(test_key)
        cluster_cache.delete(test_key)
        
        cache_working = retrieved == test_value
        cached_items = len(cluster_cache._cache)
        expired_count = cluster_cache.cleanup_expired()
        
        return {
            "status": "healthy" if cache_working else "degraded",
            "cache_operations": "working" if cache_working else "failed",
            "cached_items": cached_items,
            "expired_items_cleaned": expired_count
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "unhealthy",
                "cache_operations": "failed",
                "error": str(e)
            }
        )

@router.get("/status")
async def system_status(
    client: MicroshareDeviceClient = Depends(get_microshare_client)
):
    """Comprehensive system status check"""
    try:
        from src.microshare_client.cache import cluster_cache
        
        start_time = time.time()
        clusters = await client.list_all_clusters()
        microshare_time = time.time() - start_time
        
        cache_items = len(cluster_cache._cache)
        expired_cleaned = cluster_cache.cleanup_expired()
        
        return {
            "overall_status": "healthy",
            "components": {
                "api_server": "healthy",
                "microshare_connection": "healthy",
                "cache_system": "healthy",
                "authentication": "valid"
            },
            "metrics": {
                "cluster_count": len(clusters.get('objs', [])),
                "microshare_response_time": round(microshare_time, 3),
                "cached_items": cache_items,
                "expired_items_cleaned": expired_cleaned
            },
            "timestamp": time.time()
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "overall_status": "unhealthy",
                "error": str(e),
                "timestamp": time.time()
            }
        )
