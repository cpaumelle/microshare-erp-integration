# The Definitive Guide to Microshare Device Cluster CRUD Operations

## Overview

This guide documents the **tested and verified** methods for interacting with Microshare device clusters and performing CRUD operations on devices within those clusters.

## Key Architecture Principles

### 1. Clusters vs Devices - Critical Distinction

- **CLUSTERS**: Read-only containers that define location hierarchy and device grouping
- **DEVICES**: The actual IoT devices within clusters that can be CRUD'd
- **NEVER create or modify clusters** - only manage devices within existing clusters

### 2. Authentication Pattern

All API calls require Bearer token authentication using this proven pattern:

```bash
# Get authentication token
TOKEN=$(curl -s -X POST "http://localhost:8000/auth/token" \
  -H "Content-Type: application/json" \
  -d '{}' | jq -r '.access_token')
```

Or direct Microshare authentication:

```bash
curl -s "https://dauth.microshare.io/oauth2/token?username={username}&password={password}&client_id={api_key}&grant_type=password&scope=ALL:ALL"
```

## Working API Patterns

### Pattern 1: List All Device Clusters (READ ONLY)

**Purpose**: Understand existing cluster structure and find target clusters for device operations.

```bash
# Via FastAPI wrapper (working)
curl -s -H "Authorization: Bearer $TOKEN" "http://localhost:8000/cluster/items"

# Direct Microshare API (working)
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://dapi.microshare.io/device/*?details=true&page=1&perPage=5000&discover=true&field=name&search="
```

**Response Structure**:

```json
{
  "objs": [
    {
      "_id": "68b1357b3270e76ce8e4977e",
      "name": "ERP Sample App | Motion", 
      "recType": "io.microshare.trap.packed",
      "data": {
        "devices": [
          {
            "id": "58A0CB000011F85E",
            "meta": {
              "location": ["Paris HQ", "Rue Voltaire", "3eme etage", "Boite 22", "internal", "bait"]
            },
            "status": "pending"
          }
        ]
      }
    }
  ]
}
```

### Pattern 2: Get Specific Cluster (READ ONLY)

**Purpose**: Get detailed information about a specific cluster and its devices.

```bash
# Get specific cluster by ID
CLUSTER_ID="68b1357b3270e76ce8e4977e"
curl -s "https://dapi.microshare.io/device/io.microshare.trap.packed/$CLUSTER_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/json"
```

### Pattern 3: Add Device to Existing Cluster (CREATE)

**Purpose**: Add a new device to an existing cluster - the ONLY way to create devices.

**Step 1**: Get current cluster data

```bash
CLUSTER_ID="68b1357b3270e76ce8e4977e"
curl -s "https://dapi.microshare.io/device/io.microshare.trap.packed/$CLUSTER_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/json" > current_cluster.json
```

**Step 2**: Add new device to devices array

```bash
jq '.objs[0].data.devices += [{
  "guid": "erp-device-001",
  "id": "ERP1122334455667788", 
  "meta": {
    "location": [
      "Golden Crust Manchester",
      "Manchester Production", 
      "Flour Storage Silo A",
      "ERP024_025_01",
      "Internal",
      "Bait/Lured"
    ]
  },
  "status": "pending"
}]' current_cluster.json | jq '.objs[0]' > updated_cluster.json
```

**Step 3**: PUT updated cluster back

```bash
curl -X PUT "https://dapi.microshare.io/device/io.microshare.trap.packed/$CLUSTER_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  --data-binary @updated_cluster.json
```

**Step 4**: Verify device was added

```bash
curl -s "https://dapi.microshare.io/device/io.microshare.trap.packed/$CLUSTER_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/json" | jq '.objs[0].data.devices | length'
```

### Pattern 4: Update Device in Cluster (UPDATE)

**Purpose**: Modify an existing device's properties.

**Step 1**: Get current cluster

```bash
curl -s "https://dapi.microshare.io/device/io.microshare.trap.packed/$CLUSTER_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/json" > current_cluster.json
```

**Step 2**: Update specific device

```bash
# Update device with ID "ERP1122334455667788"
jq '.objs[0].data.devices |= map(
  if .id == "ERP1122334455667788" then 
    .status = "active" |
    .meta.location[4] = "External"
  else . end
)' current_cluster.json | jq '.objs[0]' > updated_cluster.json
```

**Step 3**: PUT updated cluster

```bash
curl -X PUT "https://dapi.microshare.io/device/io.microshare.trap.packed/$CLUSTER_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  --data-binary @updated_cluster.json
```

### Pattern 5: Remove Device from Cluster (DELETE)

**Purpose**: Remove a device from a cluster.

**Step 1**: Get current cluster

```bash
curl -s "https://dapi.microshare.io/device/io.microshare.trap.packed/$CLUSTER_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/json" > current_cluster.json
```

**Step 2**: Remove device from array

```bash
# Remove device with ID "ERP1122334455667788"
jq '.objs[0].data.devices |= map(select(.id != "ERP1122334455667788"))' \
  current_cluster.json | jq '.objs[0]' > updated_cluster.json
```

**Step 3**: PUT updated cluster

```bash
curl -X PUT "https://dapi.microshare.io/device/io.microshare.trap.packed/$CLUSTER_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  --data-binary @updated_cluster.json
```

## Device Types and Data Structures

### Rodent Sensors (recType: io.microshare.trap.packed)

Rodent sensors are the **critical devices for ERP synchronization** as they directly correspond to pest control inspection points in ERP systems. These devices require precise location mapping for compliance and service delivery.

#### Standard 6-Layer Location Array for Rodent Sensors

```json
{
  "id": "00-00-00-00-00-00-00-00",
  "meta": {
    "location": [
      "Customer Name",        // [0] Customer/Organization (required)
      "Site Name",           // [1] Site/Facility (required)
      "Area Name",           // [2] Area/Zone (required)  
      "ERP_Reference",       // [3] ERP internal_reference - CRITICAL for sync
      "Placement",           // [4] Internal | External
      "Configuration"        // [5] Poison | Bait/Lured | Kill/Trap | Glue | Cavity
    ]
  },
  "status": "pending",
  "guid": "sensor-guid"
}
```

**Rodent Sensor Sync Priority**: HIGH - These must sync accurately with ERP pest control inspection points to maintain service compliance and billing accuracy.

### Gateways (recType: io.microshare.gateway.health.packed)

Gateways are networking infrastructure devices that facilitate communication between sensors and the Microshare platform. Gateway synchronization is useful for network management but not critical for ERP compliance.

#### Standard 4-Layer Location Array for Gateways

```json
{
  "id": "00-00-00-00-00-00-00-00", 
  "meta": {
    "location": [
      "Customer Name",        // [0] Customer/Organization (required)
      "Site Name",           // [1] Site/Facility (required)
      "Area Name",           // [2] Area/Zone (required)
      "Gateway_Location"     // [3] Specific gateway location identifier
    ]
  },
  "status": "active",
  "guid": "gateway-guid"
}
```

**Gateway Sync Priority**: LOW - Nice to have for infrastructure tracking but not required for ERP compliance.

### Extended Location Arrays (Advanced Usage)

While the standard arrays are 6 layers for sensors and 4 layers for gateways, the location array can be extended beyond these base requirements if your application needs additional granularity:

```json
{
  "meta": {
    "location": [
      "Customer",           // [0] Standard
      "Site",              // [1] Standard  
      "Area",              // [2] Standard
      "ERP_Reference",     // [3] Standard
      "Placement",         // [4] Standard
      "Configuration",     // [5] Standard
      "Sub_Zone",          // [6] Extended - specific sub-area
      "Equipment_Type",    // [7] Extended - equipment classification
      "Service_Route"      // [8] Extended - service technician route
    ]
  }
}
```

**Performance Consideration**: Extended arrays beyond the standard 6/4 layers may impact query performance and should only be used when the additional metadata is essential for your application requirements.

## Device Data Structure

### Required Device Fields

```json
{
  "id": "string",           // Device identifier - USE "00-00-00-00-00-00-00-00" BY DEFAULT
  "meta": {
    "location": [           // Location hierarchy array (6 elements)
      "Customer",           // [0] Customer/Organization
      "Site",              // [1] Site/Facility  
      "Area",              // [2] Area/Zone
      "ERP_Reference",     // [3] **CRITICAL**: ERP internal_reference - links back to ERP hierarchy
      "Placement",         // [4] Internal | External | Custom
      "Configuration"      // [5] Poison | Bait/Lured | Kill/Trap | Glue | Cavity | Custom
    ]
  },
  "status": "pending|active|inactive",  // Device status
  "guid": "string"         // Optional: Unique GUID for tracking
}
```

### Microshare Field Values (Pre-defined Options)

#### Placement Field [4] - Allowed Values

- `"Internal"` - Device placed inside building/structure
- `"External"` - Device placed outside building/structure
- Custom values allowed but these are the standard options

#### Configuration Field [5] - Allowed Values

- `"Poison"` - Rodenticide-based trap
- `"Bait/Lured"` - Bait station without poison
- `"Kill/Trap"` - Mechanical kill trap
- `"Glue"` - Glue board trap
- `"Cavity"` - Cavity/burrow inspection
- Custom values allowed but these are the standard pest control configurations

#### Status Field - Allowed Values

- `"pending"` - Device created but not yet deployed
- `"active"` - Device deployed and operational
- `"inactive"` - Device not currently operational
- Additional statuses may exist in Microshare system
  

### Optional Device Fields

```json
{
  "state": {              // Runtime state information
    "updateDate": "ISO_DATE",
    "location": {          // GPS coordinates if available
      "coords": {...}
    }
  },
  "meta": {
    "lora": {             // LoRaWAN configuration
      "AppKey": "",
      "NwkKey": ""
    }
  }
}
```

### ERP Integration Patterns

#### Rodent Sensor to ERP Inspection Point Mapping

Rodent sensors require precise mapping to ERP pest control inspection points for compliance and service delivery:

```javascript
function mapERPInspectionPointToSensor(erpInspectionPoint) {
  return {
    "id": "00-00-00-00-00-00-00-00",  // DEFAULT - let deployment handle DevEUI
    "meta": {
      "location": [
        erpInspectionPoint.customer,                    // [0] Customer
        erpInspectionPoint.site,                       // [1] Site
        erpInspectionPoint.area,                       // [2] Area
        erpInspectionPoint.internal_reference,         // [3] CRITICAL: ERP linkage
        erpInspectionPoint.placement || "Internal",    // [4] Placement
        erpInspectionPoint.configuration || "Bait/Lured" // [5] Configuration
      ]
    },
    "status": "pending",
    "guid": `erp-sensor-${erpInspectionPoint.id}-${Date.now()}`
  };
}
```

#### Gateway to ERP Site Mapping (Optional)

Gateways can be optionally synced for infrastructure tracking:

```javascript
function mapERPSiteToGateway(erpSite) {
  return {
    "id": "00-00-00-00-00-00-00-00",  // DEFAULT - let deployment handle DevEUI
    "meta": {
      "location": [
        erpSite.customer,              // [0] Customer
        erpSite.site_name,            // [1] Site
        erpSite.primary_area,         // [2] Area
        `GW-${erpSite.site_code}`     // [3] Gateway identifier
      ]
    },
    "status": "pending",
    "guid": `erp-gateway-${erpSite.id}-${Date.now()}`
  };
}
```

### Complete ERP Sync Example by Device Type

#### Rodent Sensor Sync (Critical Priority)

```bash
# Sync ERP inspection points to Microshare rodent sensors
TRAP_CLUSTER_ID="68b1357b3270e76ce8e4977e"

# Add rodent sensor with full 6-layer location
NEW_SENSOR='{
  "id": "00-00-00-00-00-00-00-00",
  "meta": {
    "location": [
      "Golden Crust Manchester",
      "Manchester Production",
      "Flour Storage Silo A", 
      "ERP024_025_01",
      "Internal",
      "Bait/Lured"
    ]
  },
  "status": "pending",
  "guid": "erp-sync-sensor-001"
}'

# Add to trap cluster
jq --argjson device "$NEW_SENSOR" '.objs[0].data.devices += [$device]' \
  current_trap_cluster.json | jq '.objs[0]' > updated_trap_cluster.json

curl -X PUT "https://dapi.microshare.io/device/io.microshare.trap.packed/$TRAP_CLUSTER_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  --data-binary @updated_trap_cluster.json
```

#### Gateway Sync (Optional)

```bash
# Sync ERP sites to Microshare gateways  
GATEWAY_CLUSTER_ID="68b1357c3270e76ce8e49782"

# Add gateway with 4-layer location
NEW_GATEWAY='{
  "id": "00-00-00-00-00-00-00-00",
  "meta": {
    "location": [
      "Golden Crust Manchester",
      "Manchester Production",
      "Network Infrastructure",
      "GW-MANC-PROD-01"
    ]
  },
  "status": "pending", 
  "guid": "erp-sync-gateway-001"
}'

# Add to gateway cluster
jq --argjson device "$NEW_GATEWAY" '.objs[0].data.devices += [$device]' \
  current_gateway_cluster.json | jq '.objs[0]' > updated_gateway_cluster.json

curl -X PUT "https://dapi.microshare.io/device/io.microshare.gateway.health.packed/$GATEWAY_CLUSTER_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  --data-binary @updated_gateway_cluster.json
```

## CRITICAL: Device ID Management

### Default Device ID Pattern

**IMPORTANT**: Unless you have specific deployment requirements, ALWAYS use the default Device ID pattern:

```json
{
  "id": "00-00-00-00-00-00-00-00"
}
```

**Why Use Default Device ID:**

- Microshare's deployment system handles actual DevEUI assignment
- Real device IDs should be managed through deployment processes, not API creation
- Using `00-00-00-00-00-00-00-00` signals that this device awaits proper deployment
- Prevents conflicts with actual hardware device identifiers

**When to Use Custom Device IDs:**

- Only when you have specific integration requirements
- When mapping to existing hardware with known DevEUIs
- When instructed by Microshare deployment team

### ERP Integration - Internal Reference Mapping

The `location[3]` field serves as the **critical link** between Microshare devices and ERP hierarchy:

```json
{
  "meta": {
    "location": [
      "Customer Name",
      "Site Name", 
      "Area Name",
      "ERP_INTERNAL_REFERENCE",  // <- This ties device back to ERP inspection point
      "Internal",
      "Bait/Lured"
    ]
  }
}
```

**ERP Internal Reference Rules:**

- Must match exactly the `internal_reference` field from your ERP system
- This is the unique identifier that links the Microshare device back to the originating ERP inspection point
- Used for bidirectional sync between ERP and Microshare
- Should be unique across your entire ERP system

### Mapping ERP Inspection Point to Device

```javascript
function mapERPToDevice(erpInspectionPoint) {
  return {
    "id": "00-00-00-00-00-00-00-00",  // DEFAULT - let deployment handle DevEUI
    "meta": {
      "location": [
        erpInspectionPoint.customer,
        erpInspectionPoint.site,
        erpInspectionPoint.area, 
        erpInspectionPoint.internal_reference,  // CRITICAL: ERP linkage field
        erpInspectionPoint.placement || "Internal",
        erpInspectionPoint.configuration || "Bait/Lured"
      ]
    },
    "status": "pending",
    "guid": `erp-${erpInspectionPoint.id}-${Date.now()}`
  };
}
```

### Working with Specific Device Types

#### Rodent Sensors (Critical for ERP Integration)

Target cluster: **Motion clusters** with `recType: io.microshare.trap.packed`

```bash
# Identify trap clusters
curl -s -H "Authorization: Bearer $TOKEN" "http://localhost:8000/cluster/items" \
  | jq '.objs[] | select(.recType == "io.microshare.trap.packed") | {name: .name, id: ._id, device_count: (.data.devices | length)}'
```

#### Gateways (Optional Infrastructure Tracking)

Target cluster: **Gateway clusters** with `recType: io.microshare.gateway.health.packed`

```bash
# Identify gateway clusters  
curl -s -H "Authorization: Bearer $TOKEN" "http://localhost:8000/cluster/items" \
  | jq '.objs[] | select(.recType == "io.microshare.gateway.health.packed") | {name: .name, id: ._id, device_count: (.data.devices | length)}'
```

### Verification Commands by Device Type

#### Verify Rodent Sensor Creation

```bash
TRAP_CLUSTER_ID="68b1357b3270e76ce8e4977e"
curl -s "https://dapi.microshare.io/device/io.microshare.trap.packed/$TRAP_CLUSTER_ID" \
  -H "Authorization: Bearer $TOKEN" | jq '.objs[0].data.devices[] | {id: .id, erp_ref: .meta.location[3], config: .meta.location[5], status: .status}'
```

#### Verify Gateway Creation

```bash
GATEWAY_CLUSTER_ID="68b1357c3270e76ce8e49782"
curl -s "https://dapi.microshare.io/device/io.microshare.gateway.health.packed/$GATEWAY_CLUSTER_ID" \
  -H "Authorization: Bearer $TOKEN" | jq '.objs[0].data.devices[] | {id: .id, location: .meta.location[3], status: .status}'
```

## Common Pitfalls and Solutions

### ❌ Wrong: Trying to create clusters

```bash
# DON'T DO THIS - Creates metadata, not actual devices
curl -X POST "https://dapi.microshare.io/share/io.microshare.trap.packed" \
  -H "Authorization: Bearer $TOKEN" -d '{"device_data": "..."}'
```

### ✅ Right: Adding devices to existing clusters

```bash
# DO THIS - Adds actual devices to clusters
curl -X PUT "https://dapi.microshare.io/device/io.microshare.trap.packed/$CLUSTER_ID" \
  -H "Authorization: Bearer $TOKEN" --data-binary @updated_cluster.json
```

### ❌ Wrong: Using inconsistent endpoints

```bash
# These endpoints return different results:
GET /device/*           # Returns 0 clusters (unreliable)
GET /cluster/items      # Returns 2 clusters (working)
```

### ✅ Right: Use the proven working pattern

```bash
# Always use the specific cluster endpoint pattern:
GET  /device/io.microshare.trap.packed/{cluster_id}  # Get cluster
PUT  /device/io.microshare.trap.packed/{cluster_id}  # Update cluster
```

## FastAPI Implementation

### Working FastAPI Route Structure

```python
@router.put("/device/cluster/{cluster_id}/add-device")
async def add_device_to_cluster(
    cluster_id: str,
    device_data: dict,
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    """Add device to existing cluster using proven UI pattern"""

    token = credentials.credentials
    base_url = os.getenv("MICROSHARE_API_URL", "https://dapi.microshare.io")

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    # Step 1: Get current cluster
    get_url = f"{base_url}/device/io.microshare.trap.packed/{cluster_id}"
    response = httpx.get(get_url, headers=headers, timeout=30)
    response.raise_for_status()
    cluster = response.json()

    # Step 2: Add new device to devices array
    cluster_obj = cluster['objs'][0]
    cluster_obj['data']['devices'].append(device_data)

    # Step 3: PUT updated cluster
    put_url = f"{base_url}/device/io.microshare.trap.packed/{cluster_id}"
    response = httpx.put(put_url, headers={**headers, "Content-Type": "application/json"}, 
                        json=cluster_obj, timeout=60)
    response.raise_for_status()

    return response.json()
```

## Verification Commands

### Check Device Count

```bash
curl -s "https://dapi.microshare.io/device/io.microshare.trap.packed/$CLUSTER_ID" \
  -H "Authorization: Bearer $TOKEN" | jq '.objs[0].data.devices | length'
```

### List All Devices in Cluster

```bash
curl -s "https://dapi.microshare.io/device/io.microshare.trap.packed/$CLUSTER_ID" \
  -H "Authorization: Bearer $TOKEN" | jq '.objs[0].data.devices[] | {id: .id, location: .meta.location[0:4], status: .status}'
```

### Find Device by ID

```bash
DEVICE_ID="ERP1122334455667788"
curl -s "https://dapi.microshare.io/device/io.microshare.trap.packed/$CLUSTER_ID" \
  -H "Authorization: Bearer $TOKEN" | jq ".objs[0].data.devices[] | select(.id == \"$DEVICE_ID\")"
```

## Summary

This guide provides the **definitive, tested patterns** for Microshare device cluster operations. The key insights are:

1. **Clusters are read-only containers** - never create or modify cluster structure
2. **Devices live within clusters** - all CRUD operations are on devices within existing clusters
3. **The UI pattern works**: GET cluster → modify devices array → PUT cluster
4. **Authentication must be properly handled** with Bearer tokens
5. **Location hierarchy is critical** - 6-element array defines device placement

Following these patterns ensures reliable device management within the Microshare ecosystem.
