# Microshare ERP Integration - API Reference

**Version**: 3.0.0
**Last Tested**: 2025-09-15
**Status**: Definitive - All endpoints verified against running API

This is the **single source of truth** for all API endpoints and data structures in the Microshare ERP Integration platform.

---

## Authentication

### Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "your-username@company.com",
  "password": "your-password",
  "environment": "dev"
}
```

**Response**:
```json
{
  "success": true,
  "session_token": "jwt-token-string",
  "user_info": {
    "username": "your-username@company.com",
    "environment": "dev",
    "authenticated_at": "2025-09-15T16:50:40.901457"
  },
  "api_base": "https://dapi.microshare.io",
  "expires_at": "2025-09-17T16:50:40"
}
```

### Authentication Status
```http
GET /api/v1/auth/status
Authorization: Bearer {session_token}
```

### Authentication Pattern (curl)
```bash
# Get session token
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user@example.com", "password": "password"}' \
  | jq -r '.session_token')

# Use token in requests
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/devices/
```

---

## Device Management

### List All Devices
```http
GET /api/v1/devices/
Authorization: Bearer {session_token}
```

**Response**: Array of devices across all clusters with performance metrics.

### Create Device
```http
POST /api/v1/devices/create
Authorization: Bearer {session_token}
Content-Type: application/json

{
  "customer": "Customer Name",
  "site": "Site/Facility Name",
  "area": "Area/Zone Name",
  "erp_reference": "ERP_REF_001",
  "placement": "Internal",
  "configuration": "Bait/Lured",
  "device_type": "rodent_sensor"
}
```

**Note**: Use `/create` endpoint, **NOT** `POST /api/v1/devices/`

### Update Device
```http
PUT /api/v1/devices/{device_id}
Authorization: Bearer {session_token}
Content-Type: application/json

{
  "meta": {
    "location": ["Updated", "Location", "Array"]
  }
}
```

### Delete Device
```http
DELETE /api/v1/devices/{device_id}
Authorization: Bearer {session_token}
```

---

## System & Monitoring

### Health Check
```http
GET /health
```

**Response**: Basic service health and version info.

### Detailed Status
```http
GET /api/v1/status
```

**Response**: Complete API status with performance metrics and endpoint information.

### Cache Management
```http
# Get cache status
GET /api/v1/devices/cache/status
Authorization: Bearer {session_token}

# Clear all caches (use sparingly)
POST /api/v1/devices/cache/clear
Authorization: Bearer {session_token}
```

### Performance Monitoring
```http
GET /api/v1/devices/performance/benchmark
```

**Response**: Performance comparison showing 45x improvement metrics.

---

## Device Data Structures

### Critical Architecture Concepts

#### Clusters vs Devices - Essential Distinction
- **CLUSTERS**: Read-only containers that group devices by type and location
- **DEVICES**: The actual IoT devices within clusters that can be CRUD'd
- **NEVER create or modify clusters** - only manage devices within existing clusters

#### Device Types and Location Arrays

### Rodent Sensors (`io.microshare.trap.packed`)

**Standard 6-Layer Location Array**:
```json
{
  "id": "device-eui-string",
  "meta": {
    "location": [
      "Customer Name",         // [0] Customer/Organization
      "Site Name",            // [1] Site/Facility
      "Area Name",            // [2] Area/Zone within site
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

**ERP Reference Field [3]**: This field is **critical for ERP integration** - it serves as the primary link between ERP inspection points and IoT devices.

### Gateways (`io.microshare.gateway.health.packed`)

**Standard 4-Layer Location Array**:
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

### Field Value Options

#### Placement Field [4] - Rodent Sensors
- `"Internal"` - Indoor placement
- `"External"` - Outdoor placement

#### Configuration Field [5] - Rodent Sensors
- `"Bait/Lured"` - Baited trap sensors
- `"Kill/Trap"` - Kill trap mechanisms
- `"Poison"` - Poison station monitoring
- `"Glue"` - Glue trap monitoring
- `"Cavity"` - Cavity/burrow monitoring

**Performance Note**: Extended location arrays beyond standard 6/4 layers may impact query performance.

---

## Direct Microshare API Patterns

For advanced users who need to interact with Microshare API directly:

### Discover All Device Clusters
```bash
# Direct Microshare discovery (expensive operation)
curl -H "Authorization: Bearer $MICROSHARE_TOKEN" \
  "https://dapi.microshare.io/device/*?details=true&page=1&perPage=5000&discover=true"
```

### Get Specific Device Cluster
```bash
# Get cluster details by ID
curl -H "Authorization: Bearer $MICROSHARE_TOKEN" \
  "https://dapi.microshare.io/device/{cluster_id}"
```

**Important**: Direct API calls bypass the FastAPI performance optimizations. Use FastAPI endpoints (`/api/v1/devices/`) for better performance.

---

## Error Handling

### Common HTTP Status Codes
- `200` - Success
- `201` - Created successfully
- `400` - Bad request (invalid data format)
- `401` - Unauthorized (invalid/expired token)
- `404` - Not found (device/cluster doesn't exist)
- `500` - Internal server error

### Authentication Errors
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "username"],
      "msg": "Field required"
    }
  ]
}
```

### Device Creation Errors
```json
{
  "success": false,
  "error": "Device creation failed: Invalid cluster for device type",
  "details": "rodent_sensor devices cannot be added to gateway clusters"
}
```

---

## Performance Characteristics

### Optimization Results
- **Device Listing**: 42x performance improvement (sub-second responses)
- **Device Creation**: 22x faster (~1 second vs 22 seconds)
- **Device Updates**: 24x faster (~1 second vs 23 seconds)
- **Device Deletion**: 23x faster (~1 second vs 22 seconds)

### Cache Strategy
- **Discovery Cache**: 60-second TTL for cluster mapping
- **Device Cache**: 300-second TTL for device data
- **Update Strategy**: Surgical cache updates instead of full clearing

### Best Practices
1. **Use FastAPI endpoints** instead of direct Microshare API for better performance
2. **Cache authentication tokens** - they're valid for ~24 hours
3. **Batch operations** when creating multiple devices
4. **Monitor cache status** via `/api/v1/devices/cache/status`
5. **Use GUID-based operations** for reliable device identification

---

## Integration Notes

### ERP Integration Key Points
- **location[3]** field is the primary sync key between ERP and IoT
- Device creation uses default DevEUI `"00-00-00-00-00-00-00-00"`
- Actual DevEUI assignment happens during physical deployment
- Device status flows: `pending` → `active` → `maintenance` → `inactive`

### Record Types (Microshare)
- Rodent sensors: `"io.microshare.trap.packed"`
- Gateways: `"io.microshare.gateway.health.packed"`

---

## Testing & Validation

All endpoints in this reference have been **tested and verified** against a running API instance.

To validate your deployment:
```bash
# Run the deployment validator
python3 scripts/validate_deployment.py

# Or test endpoints manually
python3 test_endpoints.py
```

---

**This document represents the definitive API contract for the Microshare ERP Integration platform. All other documentation references should defer to these verified endpoints and data structures.**