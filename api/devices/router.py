"""
Device API Routes v2.0.0
FastAPI routes for device management
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from api.devices.client import OptimizedDeviceClient
from api.devices.models import DeviceCluster, DeviceResponse
from api.auth.middleware import get_current_user
from api.config.settings import settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/devices", tags=["Devices"])

# Global client instance (in production, use dependency injection)
device_client = OptimizedDeviceClient()

@router.get("/clusters", response_model=List[DeviceCluster])
async def list_clusters(
    page_size: int = Query(2000, ge=50, le=2000, description="Page size for discovery"),
    auth: dict = Depends(get_current_user)
):
    """
    Discover and list all device clusters
    Uses optimized discovery pattern for fast retrieval
    """
    try:
        # Authenticate with Microshare
        auth_success = await device_client.authenticate(
            settings.microshare_username,
            settings.microshare_password
        )
        
        if not auth_success:
            raise HTTPException(status_code=401, detail="Failed to authenticate with Microshare")
        
        clusters = await device_client.discover_clusters(page_size)
        return clusters
        
    except Exception as e:
        logger.error(f"Failed to list clusters: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/clusters/{cluster_id}")
async def get_cluster(
    cluster_id: str,
    record_type: str = Query(settings.device_record_type, description="Record type"),
    auth: dict = Depends(get_current_user)
):
    """
    Get specific cluster by ID (optimized direct access)
    """
    try:
        # Ensure authentication
        if not device_client._access_token:
            await device_client.authenticate(
                settings.microshare_username,
                settings.microshare_password
            )
        
        cluster = await device_client.get_cluster_direct(cluster_id, record_type)
        
        if not cluster:
            raise HTTPException(status_code=404, detail="Cluster not found")
            
        return cluster
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get cluster {cluster_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def device_health():
    """Device service health check"""
    return {
        "status": "healthy",
        "service": "device-management",
        "version": "2.0.0"
    }
