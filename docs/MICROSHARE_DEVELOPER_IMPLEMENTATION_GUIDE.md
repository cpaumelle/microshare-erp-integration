# Microshare ERP Integration - Developer Implementation Guide

**Version: 3.0.0**  
**Created: 2025-09-15 15:20:00 UTC**  
**Status: Canonical Implementation Guide**

## Overview

This guide provides the standard approach for building high-performance integrations with the Microshare IoT platform using FastAPI. The architecture focuses on efficient cache utilization, direct cluster access patterns, and reliable device identification to achieve sub-second response times.

## Architecture Principles

### Core Design Philosophy

**Cache-First Operations**: All device operations prioritize cached cluster data over real-time discovery to maintain consistent performance.

**Direct Cluster Access**: Use known cluster IDs for targeted operations rather than scanning all clusters.

**GUID-Based Identification**: Leverage Microshare's unique device GUIDs for reliable device tracking across operations.

**Surgical Cache Updates**: Preserve cache performance through precise updates rather than complete invalidation.

## Microshare API Usage Patterns

### Discovery Pattern (Initialization Only)

Discovery operations are expensive (20+ seconds) and should be used sparingly:

```python
async def initialize_cluster_cache():
    """
    One-time cluster discovery for cache initialization
    Use only during application startup or when cache is completely empty
    """
    if not cache.has_cluster_mapping():
        # Expensive operation - document as such
        cluster_map = await wildcard_discovery_once()
        cache.store_cluster_mapping(cluster_map)
        logger.info("Cluster cache initialized - discovery complete")
```

**When to use discovery**:
- Application startup with empty cache
- Cache corruption recovery (rare)
- Adding support for new cluster types

**When NOT to use discovery**:
- Regular CRUD operations
- Data refresh operations
- User-initiated requests

### Direct Access Pattern (Standard Operations)

Standard operations use cached cluster IDs for fast, targeted access:

```python
async def perform_device_operation(device_data):
    """
    Standard pattern for device operations using cached cluster access
    Target response time: < 1 second
    """
    # Step 1: Get cluster ID from cache (< 10ms)
    cluster_info = cache.get_cluster_for_device_type(device_data.device_type)
    
    if not cluster_info:
        raise HTTPException(
            status_code=503, 
            detail="Cluster cache not initialized - restart application"
        )
    
    # Step 2: Direct cluster access (~ 500ms)
    cluster_data = await direct_cluster_get(cluster_info.cluster_id)
    
    # Step 3: Perform operation (~ 500ms)
    result = await modify_cluster_data(cluster_data, device_data)
    
    # Step 4: Surgical cache update (< 10ms)
    cache.update_specific_data(cluster_info.cluster_id, result)
    
    return result
```

## Cache Management Strategy

### Cache Architecture

The system uses a two-tier cache approach:

```python
class ProductionCacheManager:
    """
    Production-ready cache with surgical update capabilities
    Eliminates expensive discovery operations through smart data management
    """
    
    def __init__(self):
        # Cluster discovery cache (long-lived)
        self.cluster_discovery_cache = {
            'data': {},           # cluster_id -> cluster_info mapping
            'timestamp': 0,       # last discovery time
            'ttl': 3600          # 1 hour TTL for cluster topology
        }
        
        # Device data cache (frequently updated)
        self.device_data_cache = {
            'clusters': {},       # cluster_id -> cluster_data
            'timestamps': {},     # cluster_id -> last_update_time
            'ttl': 300           # 5 minutes TTL for device data
        }
```

### Cache Update Patterns

**Surgical Updates (Preferred)**:
```python
# Update specific device without affecting cache performance
cache.update_device_in_cache(cluster_id, device_id, updated_data)
cache.add_device_to_cache(cluster_id, new_device_data)
cache.remove_device_from_cache(cluster_id, device_id)
```

**Cache Invalidation (Avoid)**:
```python
# Avoid these patterns - they force expensive rediscovery
cache.clear_all_cache()           # Forces 20+ second rediscovery
cache.invalidate_cluster(id)      # Forces cluster reload
```

## Device Identification Standards

### GUID-Based Device Management

All devices must have unique GUIDs for reliable identification:

```python
def process_microshare_device(raw_device, cluster_info):
    """
    Standard device processing that ensures unique identification
    Exposes all necessary fields for frontend and ERP integration
    """
    location = raw_device.get('meta', {}).get('location', [])
    
    # Ensure device has unique identifier
    device_guid = raw_device.get('guid')
    if not device_guid:
        device_guid = f"erp-device-{uuid.uuid4()}"
        # Flag for Microshare update to persist GUID
    
    return {
        'id': raw_device.get('id', '00-00-00-00-00-00-00-00'),
        'guid': device_guid,                    # CRITICAL: Unique identifier
        'customer': location[0] if len(location) > 0 else '',
        'site': location[1] if len(location) > 1 else '',
        'area': location[2] if len(location) > 2 else '',
        'erp_reference': location[3] if len(location) > 3 else '',
        'placement': location[4] if len(location) > 4 else 'Internal',
        'configuration': location[5] if len(location) > 5 else 'Bait/Lured',
        'status': raw_device.get('status', 'pending'),
        'device_type': cluster_info.device_type,
        'cluster_id': cluster_info.cluster_id,
        'cluster_name': cluster_info.cluster_name
    }
```

### Frontend Integration Requirements

Frontend applications should use GUIDs as primary keys:

```javascript
// Standard device identification pattern
const deviceKey = device.guid;  // Always use GUID for unique identification
const deviceId = device.id;     // Device ID may be non-unique placeholder

// CRUD operations use GUID-based endpoints
await fetch(`/api/v1/devices/${device.guid}/update`, {...});
await fetch(`/api/v1/devices/${device.guid}/delete`, {...});
```

## CRUD Operation Implementations

### Create Device Operation

```python
@router.post("/api/v1/devices/create")
async def create_device(device_data: DeviceCreateRequest, auth: dict = Depends(get_auth)):
    """
    High-performance device creation using cached cluster access
    Target response time: < 1 second
    """
    try:
        # Get cluster info from cache
        cluster_info = cache.get_cluster_for_device_type(device_data.device_type)
        
        if not cluster_info:
            raise HTTPException(
                status_code=503,
                detail="Cluster cache not available - contact administrator"
            )
        
        # Direct cluster access
        cluster_data = await direct_cluster_get(
            cluster_info.cluster_id, 
            cluster_info.rec_type,
            auth.access_token
        )
        
        # Create device with unique GUID
        new_device = {
            'id': device_data.device_id or '00-00-00-00-00-00-00-00',
            'guid': f"erp-device-{uuid.uuid4()}",
            'meta': {
                'location': build_location_array(device_data)
            },
            'status': device_data.status or 'pending'
        }
        
        # Add to cluster
        cluster_data['data']['devices'].append(new_device)
        
        # Update Microshare
        await direct_cluster_put(
            cluster_info.cluster_id,
            cluster_info.rec_type, 
            cluster_data,
            auth.access_token
        )
        
        # Surgical cache update
        cache.add_device_to_cache(cluster_info.cluster_id, new_device)
        
        return {
            'success': True,
            'device': process_microshare_device(new_device, cluster_info),
            'cluster_id': cluster_info.cluster_id
        }
        
    except Exception as e:
        logger.error(f"Device creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Device creation failed")
```

### Update Device Operation

```python
@router.put("/api/v1/devices/{device_guid}/update")
async def update_device(
    device_guid: str, 
    updates: DeviceUpdateRequest,
    auth: dict = Depends(get_auth)
):
    """
    GUID-based device update with cache efficiency
    Uses cached cluster data to avoid expensive device lookup
    """
    try:
        # Find device using cached cluster data
        device_location = cache.find_device_by_guid(device_guid)
        
        if not device_location:
            # Fallback: search across clusters if not in cache
            device_location = await find_device_by_guid_fallback(device_guid, auth.access_token)
        
        if not device_location:
            raise HTTPException(status_code=404, detail="Device not found")
        
        # Direct cluster access
        cluster_data = await direct_cluster_get(
            device_location.cluster_id,
            device_location.rec_type,
            auth.access_token
        )
        
        # Update device in cluster data
        for device in cluster_data['data']['devices']:
            if device.get('guid') == device_guid:
                update_device_fields(device, updates)
                device['lastModified'] = datetime.utcnow().isoformat() + 'Z'
                break
        
        # Update Microshare
        await direct_cluster_put(
            device_location.cluster_id,
            device_location.rec_type,
            cluster_data,
            auth.access_token
        )
        
        # Surgical cache update
        cache.update_device_in_cache(
            device_location.cluster_id,
            device_guid,
            updates.dict()
        )
        
        return {
            'success': True,
            'device_guid': device_guid,
            'updated_fields': list(updates.dict().keys())
        }
        
    except Exception as e:
        logger.error(f"Device update failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Device update failed")
```

### Read Operations

```python
@router.get("/api/v1/devices/")
async def get_devices(auth: dict = Depends(get_auth)):
    """
    High-performance device listing using cache-first approach
    Returns all devices with complete GUID and metadata
    """
    try:
        all_devices = []
        clusters_info = {}
        
        # Get cluster mapping from cache
        cluster_map = cache.get_cluster_mapping()
        
        if not cluster_map:
            raise HTTPException(
                status_code=503,
                detail="Cluster cache not initialized - restart application"
            )
        
        # Process each cluster using cached data when available
        for cluster_id, cluster_info in cluster_map.items():
            # Try cache first
            cached_data = cache.get_cached_cluster_data(cluster_id)
            
            if cached_data:
                cluster_data = cached_data['data']
            else:
                # Cache miss - direct cluster access
                cluster_data = await direct_cluster_get(
                    cluster_id,
                    cluster_info.rec_type,
                    auth.access_token
                )
                # Cache the result
                cache.cache_cluster_data(cluster_id, cluster_data)
            
            # Process devices
            devices = cluster_data['data']['devices']
            for device in devices:
                processed_device = process_microshare_device(device, cluster_info)
                all_devices.append(processed_device)
            
            clusters_info[cluster_id] = {
                'name': cluster_info.cluster_name,
                'device_count': len(devices),
                'device_type': cluster_info.device_type
            }
        
        return {
            'success': True,
            'devices': all_devices,
            'total_count': len(all_devices),
            'clusters_info': clusters_info
        }
        
    except Exception as e:
        logger.error(f"Device listing failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Device listing failed")
```

## Performance Standards

### Response Time Targets

- **Device listing**: < 500ms (cache hit), < 2s (cache miss)
- **Device creation**: < 1 second
- **Device updates**: < 1 second  
- **Device deletion**: < 1 second
- **Cache operations**: < 10ms

### Cache Efficiency Targets

- **Cache hit rate**: > 95% for normal operations
- **Discovery frequency**: < 1% of requests
- **Cache persistence**: Hours between invalidation events

### Scalability Considerations

```python
# Connection pooling for high concurrency
async def get_http_client():
    return httpx.AsyncClient(
        timeout=30,
        limits=httpx.Limits(max_connections=100, max_keepalive_connections=20)
    )

# Rate limiting awareness
async def microshare_api_call_with_retry(url, headers, data=None, max_retries=3):
    """Handle Microshare rate limiting gracefully"""
    for attempt in range(max_retries):
        try:
            async with get_http_client() as client:
                if data:
                    response = await client.put(url, headers=headers, json=data)
                else:
                    response = await client.get(url, headers=headers)
                
                if response.status_code == 429:  # Rate limited
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    continue
                    
                return response
                
        except httpx.TimeoutException:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(1)
```

## Error Handling Standards

### Cache Management Errors

```python
class CacheError(Exception):
    """Cache-related errors that require specific handling"""
    pass

class ClusterNotFoundError(CacheError):
    """Requested cluster not available in cache"""
    pass

# Standard error handling pattern
try:
    cluster_info = cache.get_cluster_for_device_type(device_type)
except ClusterNotFoundError:
    # Attempt cache refresh
    await refresh_cluster_cache()
    cluster_info = cache.get_cluster_for_device_type(device_type)
    
    if not cluster_info:
        raise HTTPException(
            status_code=503,
            detail="Cluster configuration unavailable"
        )
```

### Microshare API Errors

```python
async def handle_microshare_response(response: httpx.Response):
    """Standard Microshare response handling"""
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 401:
        raise HTTPException(status_code=401, detail="Authentication failed")
    elif response.status_code == 429:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    elif response.status_code == 503:
        raise HTTPException(status_code=503, detail="Microshare service unavailable")
    else:
        logger.error(f"Microshare API error: {response.status_code} - {response.text}")
        raise HTTPException(status_code=502, detail="Upstream service error")
```

## Testing Standards

### Performance Testing

```python
async def test_crud_performance():
    """Validate operation performance meets standards"""
    
    # Test device creation performance
    start_time = time.perf_counter()
    result = await create_device(test_device_data)
    create_time = time.perf_counter() - start_time
    
    assert create_time < 1.0, f"Create operation too slow: {create_time:.2f}s"
    assert result['success'], "Create operation failed"
    
    # Test cache hit performance
    start_time = time.perf_counter()
    devices = await get_devices()
    read_time = time.perf_counter() - start_time
    
    assert read_time < 0.5, f"Read operation too slow: {read_time:.2f}s"
    assert len(devices['devices']) > 0, "No devices returned"
```

### Cache Consistency Testing

```python
async def test_cache_consistency():
    """Ensure cache reflects actual Microshare state"""
    
    # Create device
    device = await create_device(test_device_data)
    
    # Verify in cache
    cached_device = cache.find_device_by_guid(device['device']['guid'])
    assert cached_device is not None, "Device not found in cache"
    
    # Verify in Microshare
    microshare_device = await find_device_in_microshare(device['device']['guid'])
    assert microshare_device is not None, "Device not found in Microshare"
    
    # Verify data consistency
    assert cached_device['customer'] == microshare_device['customer']
```

## Deployment Considerations

### Environment Configuration

```python
# settings.py
class Settings(BaseSettings):
    # Microshare configuration
    microshare_api_url: str = "https://dapi.microshare.io"
    microshare_auth_url: str = "https://dauth.microshare.io"
    
    # Cache configuration
    cache_cluster_ttl: int = 3600      # 1 hour for cluster topology
    cache_device_ttl: int = 300        # 5 minutes for device data
    
    # Performance tuning
    http_timeout: int = 30
    max_connections: int = 100
    cache_max_size: int = 10000
    
    # Rate limiting
    enable_rate_limiting: bool = True
    rate_limit_requests: int = 100
    rate_limit_window: int = 60
```

### Monitoring and Observability

```python
# Metrics collection
from prometheus_client import Counter, Histogram, Gauge

# Performance metrics
crud_operations = Counter('crud_operations_total', 'Total CRUD operations', ['operation', 'status'])
response_time = Histogram('response_time_seconds', 'Response time', ['endpoint'])
cache_hits = Counter('cache_hits_total', 'Cache hits', ['cache_type'])
cache_misses = Counter('cache_misses_total', 'Cache misses', ['cache_type'])

# Health metrics
active_connections = Gauge('active_connections', 'Active HTTP connections')
cache_size = Gauge('cache_size_bytes', 'Cache size in bytes')
```

## Security Considerations

### API Key Management

```python
# Secure credential handling
class SecureCredentials:
    def __init__(self):
        self.access_token = None
        self.refresh_token = None
        self.expires_at = None
    
    async def get_valid_token(self):
        if self.access_token and datetime.now() < self.expires_at:
            return self.access_token
        
        # Refresh token if needed
        await self.refresh_authentication()
        return self.access_token
```

### Data Validation

```python
class DeviceCreateRequest(BaseModel):
    customer: str = Field(..., min_length=1, max_length=100)
    site: str = Field(..., min_length=1, max_length=100)
    area: str = Field(..., min_length=1, max_length=100)
    erp_reference: str = Field(..., min_length=1, max_length=50)
    placement: str = Field(default="Internal", regex="^(Internal|External)$")
    configuration: str = Field(default="Bait/Lured")
    device_type: str = Field(default="rodent_sensor", regex="^(rodent_sensor|gateway)$")
    
    @validator('erp_reference')
    def validate_erp_reference(cls, v):
        # Ensure ERP reference is unique and properly formatted
        if not re.match(r'^[A-Z0-9_]{3,50}$', v):
            raise ValueError('ERP reference must be 3-50 alphanumeric characters')
        return v
```

## Conclusion

This implementation guide provides the standard patterns for building performant, reliable integrations with the Microshare platform. The architecture prioritizes cache efficiency, direct access patterns, and unique device identification to deliver enterprise-grade performance and reliability.

Key principles to remember:
- Cache-first operations for consistent performance
- GUID-based device identification for reliability  
- Direct cluster access over expensive discovery
- Surgical cache updates to preserve performance
- Comprehensive error handling and monitoring

Following these patterns ensures sub-second response times, reliable device management, and scalable architecture suitable for production ERP integrations.
