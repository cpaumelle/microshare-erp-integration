"""
Device CRUD operations with caching - COMPLETE IMPLEMENTATION
"""
from fastapi import APIRouter, HTTPException, Depends, Query, Path, Body
from typing import Dict, Any, Optional
import time

from dependencies import get_microshare_client
from src.microshare_client.client import MicroshareDeviceClient
from src.microshare_client.enums import DeviceType
from src.microshare_client.exceptions import MicroshareAPIError
from src.microshare_client.models import DeviceCreateModel, DeviceUpdateModel

router = APIRouter(tags=["Device CRUD - Complete"], prefix="/devices")

# === READ OPERATIONS ===

@router.get("/clusters", summary="List all device clusters (cached)")
async def list_clusters_cached(
    ttl: int = Query(300, description="Cache TTL in seconds", ge=60, le=3600),
    client: MicroshareDeviceClient = Depends(get_microshare_client)
):
    """List all device clusters with caching for improved performance"""
    try:
        start_time = time.time()
        result = await client.list_all_clusters_cached(ttl=ttl)
        execution_time = time.time() - start_time

        if 'meta' not in result:
            result['meta'] = {}
        result['meta']['execution_time'] = round(execution_time, 3)
        result['meta']['cached_response'] = execution_time < 1.0

        return result

    except MicroshareAPIError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list clusters: {str(e)}")

@router.get("/clusters/{cluster_id}", summary="Get specific cluster (cached)")
async def get_cluster_cached(
    cluster_id: str = Path(..., description="Cluster ID"),
    device_type: DeviceType = Query(..., description="Device type (trap or gateway)"),
    ttl: int = Query(300, description="Cache TTL in seconds", ge=60, le=3600),
    client: MicroshareDeviceClient = Depends(get_microshare_client)
):
    """Get specific device cluster with caching"""
    try:
        from src.microshare_client.client import MicroshareDeviceClient

        start_time = time.time()
        result = await client.get_specific_cluster(cluster_id, device_type)
        execution_time = time.time() - start_time

        if 'meta' not in result:
            result['meta'] = {}
        result['meta']['execution_time'] = round(execution_time, 3)

        return result

    except MicroshareAPIError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get cluster: {str(e)}")

@router.get("/", summary="List all devices across clusters (cached)")
async def list_all_devices_cached(
    device_type: Optional[DeviceType] = Query(None, description="Filter by device type"),
    customer: Optional[str] = Query(None, description="Filter by customer name"),
    site: Optional[str] = Query(None, description="Filter by site name"),
    ttl: int = Query(300, description="Cache TTL in seconds"),
    client: MicroshareDeviceClient = Depends(get_microshare_client)
):
    """List all devices across all clusters with optional filtering"""
    try:
        clusters_result = await client.list_all_clusters_cached(ttl=ttl)

        devices = []
        for cluster in clusters_result.get('objs', []):
            cluster_devices = cluster.get('data', {}).get('devices', [])
            cluster_type = DeviceType.from_rec_type(cluster.get('recType', ''))

            if device_type and cluster_type != device_type:
                continue

            for device in cluster_devices:
                location = device.get('meta', {}).get('location', [])

                if customer and (len(location) == 0 or location[0] != customer):
                    continue

                if site and (len(location) < 2 or location[1] != site):
                    continue

                enriched_device = {
                    **device,
                    'cluster_id': cluster['_id'],
                    'cluster_name': cluster.get('name', ''),
                    'device_type': cluster.get('recType', ''),
                    'customer': location[0] if len(location) > 0 else None,
                    'site': location[1] if len(location) > 1 else None,
                    'area': location[2] if len(location) > 2 else None,
                    'erp_reference': location[3] if len(location) > 3 else None,
                    'placement': location[4] if len(location) > 4 else None,
                    'configuration': location[5] if len(location) > 5 else None,
                }

                devices.append(enriched_device)

        return {
            "devices": devices,
            "total_count": len(devices),
            "filters_applied": {
                "device_type": device_type.value if device_type else None,
                "customer": customer,
                "site": site
            },
            "cached_response": True
        }

    except MicroshareAPIError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list devices: {str(e)}")

@router.get("/{device_id}", summary="Find device by ID across clusters")
async def find_device_by_id(
    device_id: str = Path(..., description="Device ID to search for"),
    ttl: int = Query(300, description="Cache TTL in seconds"),
    client: MicroshareDeviceClient = Depends(get_microshare_client)
):
    """Find a specific device by ID across all clusters"""
    try:
        clusters_result = await client.list_all_clusters_cached(ttl=ttl)

        for cluster in clusters_result.get('objs', []):
            cluster_devices = cluster.get('data', {}).get('devices', [])

            for device in cluster_devices:
                if device.get('id') == device_id:
                    location = device.get('meta', {}).get('location', [])

                    return {
                        **device,
                        'cluster_id': cluster['_id'],
                        'cluster_name': cluster.get('name', ''),
                        'device_type': cluster.get('recType', ''),
                        'customer': location[0] if len(location) > 0 else None,
                        'site': location[1] if len(location) > 1 else None,
                        'area': location[2] if len(location) > 2 else None,
                        'erp_reference': location[3] if len(location) > 3 else None,
                        'found_in_cluster': True,
                        'cached_response': True
                    }

        raise HTTPException(status_code=404, detail=f"Device {device_id} not found in any cluster")

    except HTTPException:
        raise
    except MicroshareAPIError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to find device: {str(e)}")

# === CREATE OPERATION ===

@router.post("/clusters/{cluster_id}/devices", summary="Add device to cluster")
async def add_device_to_cluster(
    cluster_id: str = Path(..., description="Cluster ID"),
    device_type: DeviceType = Query(..., description="Device type (trap or gateway)"),
    device: DeviceCreateModel = Body(..., description="Device data"),
    client: MicroshareDeviceClient = Depends(get_microshare_client)
):
    """Add a new device to an existing cluster with cache invalidation"""
    try:
        device_dict = device.dict()
        result = await client.add_device_to_cluster_cached(cluster_id, device_type, device_dict)

        return {
            "message": "Device added successfully",
            "cluster_id": cluster_id,
            "device_type": device_type.value,
            "device_id": device_dict.get('id', 'unknown'),
            "cache_invalidated": True,
            "result": result
        }

    except MicroshareAPIError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add device: {str(e)}")

# === UPDATE OPERATION ===

@router.put("/clusters/{cluster_id}/devices/{device_id}", summary="Update device in cluster")
async def update_device_in_cluster(
    cluster_id: str = Path(..., description="Cluster ID"),
    device_id: str = Path(..., description="Device ID within cluster"),
    device_type: DeviceType = Query(..., description="Device type (trap or gateway)"),
    updates: DeviceUpdateModel = Body(..., description="Device updates"),
    client: MicroshareDeviceClient = Depends(get_microshare_client)
):
    """Update an existing device within a cluster with cache invalidation"""
    try:
        updates_dict = {k: v for k, v in updates.dict().items() if v is not None}
        result = await client.update_device_in_cluster_cached(
            cluster_id, device_type, device_id, updates_dict
        )

        return {
            "message": "Device updated successfully",
            "cluster_id": cluster_id,
            "device_id": device_id,
            "device_type": device_type.value,
            "updates_applied": updates_dict,
            "cache_invalidated": True,
            "result": result
        }

    except MicroshareAPIError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update device: {str(e)}")

# === DELETE OPERATION ===

@router.delete("/clusters/{cluster_id}/devices/{device_id}", summary="Remove device from cluster")
async def remove_device_from_cluster(
    cluster_id: str = Path(..., description="Cluster ID"),
    device_id: str = Path(..., description="Device ID within cluster"),
    device_type: DeviceType = Query(..., description="Device type (trap or gateway)"),
    client: MicroshareDeviceClient = Depends(get_microshare_client)
):
    """Remove a device from a cluster with cache invalidation"""
    try:
        result = await client.remove_device_from_cluster_cached(
            cluster_id, device_type, device_id
        )

        return {
            "message": "Device removed successfully",
            "cluster_id": cluster_id,
            "device_id": device_id,
            "device_type": device_type.value,
            "cache_invalidated": True,
            "result": result
        }

    except MicroshareAPIError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove device: {str(e)}")

# === CACHE MANAGEMENT ===

@router.delete("/cache", summary="Clear device cluster cache")
async def clear_device_cache(
    cluster_id: Optional[str] = Query(None, description="Specific cluster ID to clear"),
    device_type: Optional[DeviceType] = Query(None, description="Device type for specific cluster"),
    client: MicroshareDeviceClient = Depends(get_microshare_client)
):
    """Clear device cluster cache entries"""
    try:
        if cluster_id and device_type:
            client.invalidate_cluster_cache(cluster_id, device_type)
            return {
                "message": f"Cache cleared for cluster {cluster_id} ({device_type.value})",
                "cluster_id": cluster_id,
                "device_type": device_type.value
            }
        else:
            client.invalidate_cluster_cache()
            return {
                "message": "All device cluster cache cleared",
                "cache_cleared": True
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear cache: {str(e)}")
