# ERP-IoT Synchronization Architecture

## Microshare x ERP Integration for Pest Control Management

**Document Version**: 3.0  
**Implementation Status**: Phase 3 Optimised CRUD operations with Microshare API  
**Target Audience**: ERP Developers, System Integrators, IoT Architects

---

## Executive Summary

This document outlines a bidirectional synchronization system between Pest ERP business processes and the Microshare IoT connected monitoring for pest control operations. The implementation bridges the gap between business-centric inspection scheduling and real-time sensor monitoring. We've used an Open-source ERP system called Odoo as a demo ERP for our sample but the app can be adapted to work with any ERP with RESTful API endpoints.

## Current Implementation - Phase 1 Discovery and CRUD on Microshare

### Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│. Your Pest ERP  │    │Sample ERP-       │    │   Microshare    │
│                 │◄──►│Microshare sync   │◄──►│   IoT Platform  │
│                 │    │      app         │    │                 │
│ Inspection      │    │ • Discovery API  │    │ Device Clusters │
│ Points as       │    │ • Mapping Logic  │    │ • Trap Sensors  │
│ Products        │    │ • Cache Layer    │    │ • Gateways      │
│ Category ID: 4  │    │ • Error Handling │    │ • Real-time Data│
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Data Flow Architecture

**ERP → Sync Bridge → IoT Platform**

1. **ERP Discovery**: Read pest control inspection points from Pest `product.product` table
2. **Location Parsing**: Extract customer/site/area from ERP naming conventions
3. **Reference Matching**: Map ERP codes to Microshare device location[3] field
4. **Gap Analysis**: Identify unmapped inspection points requiring IoT devices
5. **Device Recommendations**: Generate Microshare device templates with default DevEUI

### Current Capabilities

#### 1. ERP Data Discovery

- **Endpoint**: `GET /api/v1/erp/discovery/inspection-points`
- **Function**: Retrieves all pest control inspection points from Odoo
- **Data Volume**: 11 inspection points across Golden Crust Manchester
- **Performance**: Real-time XML-RPC connection to Odoo

#### 2. Mapping Analysis

- **Endpoint**: `GET /api/v1/erp/discovery/unmapped`
- **Function**: Identifies ERP points without corresponding IoT devices
- **Current Result**: 9 unmapped points requiring device creation
- **Recommendation**: Create devices with DevEUI `00-00-00-00-00-00-00-00`

#### 3. Location Hierarchy Translation

- **ERP Format**: "Golden Crust Manchester - Flour Storage Silo A"
- **IoT Format**: `["Golden Crust Manchester", "Manchester Production", "Flour Storage Silo A", "ERP024_025_01", "Internal", "Bait/Lured"]`
- **Matching Key**: ERP `default_code` ↔ Microshare `location[3]`

### Data Structure Mapping

#### Odoo ERP Side

```jsonc
{
  "model": "product.product",  
  "category_filter": "categ_id = 4",
  "fields": {
    "id": "Unique Odoo record ID (1-11+)",
    "default_code": "ERP reference (ERP024_025_01)",    // This is the unique reference used by the ERP for the inspection point
    "barcode": "DevEUI storage field",                  // This is the Microshare unique device ID which can be synched back to the ERP
    "name": "Location description",                     // This is the location array descibing the customer, building, floor, room, etc
    "active": "Inspection point status"                 // This may be used to record whether an inspection point is equipped with a sensor or not
  }
}
```

#### Microshare IoT Side

```jsonc
{
  "device_structure": {
    "id": "DevEUI or default 00-00-00-00-00-00-00-00",
    "meta": {
      "location": [
        "Customer name",      // [0] Maps to parsed ERP location
        "Site name",         // [1] Standardized site naming  
        "Area name",         // [2] From ERP inspection point
        "ERP reference",     // [3] PRIMARY MATCHING KEY
        "Placement",         // [4] Internal/External
        "Configuration"      // [5] Bait/Lured/etc
      ]
    },
    "status": "pending|active|inactive"
  }
}
```

### Current Limitations

1. **Read-Only Discovery**: No device creation or modification operations
2. **Limited Error Handling**: Mapping endpoint occasionally times out under load
3. **Static Location Parsing**: Customer/site naming hardcoded to Golden Crust Manchester
4. **No Incident Correlation**: Cannot correlate sensor events with ERP service records
5. **Manual DevEUI Assignment**: Default DevEUI requires manual deployment processes

---

## Future Implementation Roadmap

### ### Phase 2: Incident and Event Correlation

#### 3.1 Real-Time Incident Sync

- **Capability**: Push Microshare sensor alerts to ERP as service incidents
- **Implementation**:
  
  ```python
  POST /api/v1/erp/incidents/sync
  # Creates ERP incident records from Microshare sensor events
  # Links incidents to specific inspection points via reference codes
  ```
  
- **Business Value**: Automated incident reporting and compliance documentation

#### 3.2 Service History Integration

- **Capability**: Correlate sensor data with ERP service visits
- **Implementation**: Track technician visits against sensor activity patterns
- **Analytics**: Identify inspection effectiveness and optimization opportunities

####

### Phase 3: PCT 4.0 API integration

####Microshare is joining the Pest Industry's efforts to standardise API data exchanges between ERPs and connected monitoring systems. We will soon be sharing details on how to enable this.

---

## Technical Implementation Details

### Authentication Architecture

```python
# Multi-system authentication chain
Microshare_Token = authenticate(username, password, client_id)
Odoo_Session = xmlrpc_authenticate(database, username, password)

# Secure credential management
MICROSHARE_API_HOST = "https://dapi.microshare.io"
ODOO_HOST = "http://10.44.1.17:8069"
```

### Error Handling Strategy

- **Graceful Degradation**: ERP connectivity issues don't break IoT operations
- **Retry Logic**: Automatic retry for transient network failures
- **Audit Logging**: Complete sync operation history with timestamps
- **Recovery Procedures**: Manual sync triggers for failed operations

### Data Consistency Model

- **ERP as Source of Truth**: Business data (customers, contracts, schedules)
- **IoT as Operational Truth**: Real-time device status and sensor events
- **Sync Bridge as Mediator**: Handles conflicts and data translation

---

## Business Impact Analysis

### Current Value Delivered

1. **Operational Visibility**: 11 inspection points discoverable across systems
2. **Gap Identification**: 9 unmapped points identified for IoT deployment
3. **Data Standardization**: Consistent location hierarchy across platforms
4. **Performance Optimization**: Sub-second data retrieval with caching

### Phase 2 Business Value (Device Lifecycle)

- **Deployment Efficiency**: 80% reduction in manual device provisioning
- **Inventory Accuracy**: Real-time device inventory synchronization
- **Compliance Automation**: Automated device deployment documentation

### Phase 3 Business Value (Incident Correlation)

- **Response Time**: 90% reduction in incident detection to ERP logging
- **Service Quality**: Real-time verification of pest control effectiveness
- **Customer Satisfaction**: Proactive issue resolution with sensor alerts

### Phase 4 Business Value (Business Intelligence)

- **Revenue Optimization**: Data-driven service pricing and deployment strategies
- **Operational Efficiency**: Predictive analytics for maintenance and service optimization
- **Market Differentiation**: IoT-enabled service offerings vs traditional inspection-only competitors

---

## Security and Compliance Considerations

### Data Privacy

- **Segregation**: Customer data isolated between ERP and IoT platforms
- **Encryption**: All inter-system communication encrypted in transit
- **Access Control**: Role-based permissions for sync operations

### Regulatory Compliance

- **Audit Trails**: Complete history of device deployments and status changes
- **Data Retention**: Configurable retention policies for historical sync data
- **Backup/Recovery**: Cross-platform data backup and disaster recovery procedures

### Network Security

- **API Authentication**: OAuth2 for Microshare, session management for Odoo
- **Rate Limiting**: Protection against API abuse and system overload
- **Monitoring**: Real-time monitoring of sync operations and error rates

---

## Implementation Timeline

### Phase 1: Discovery (COMPLETE)

- **Duration**: 2 weeks
- **Status**: Operational
- **Deliverables**: Read-only mapping analysis, gap identification

### Phase 2: Device Lifecycle (NEXT)

- **Duration**: 3-4 weeks
- **Dependencies**: Phase 1 completion
- **Deliverables**: Automated device creation, DevEUI management, deployment tracking

### Phase 3: Incident Correlation

- **Duration**: 4-6 weeks
- **Dependencies**: Phase 2 completion
- **Deliverables**: Real-time incident sync, service history integration

### Phase 4: Business Intelligence

- **Duration**: 6-8 weeks
- **Dependencies**: Phase 3 operational data
- **Deliverables**: Analytics dashboards, predictive models, customer portals

### Phase 5: Enterprise Features

- **Duration**: 8-12 weeks
- **Dependencies**: Phase 4 validation
- **Deliverables**: Multi-ERP support, compliance automation, multi-tenant architecture

---

## Conclusion

The current Phase 1 implementation provides a solid foundation for ERP-IoT synchronization with proven connectivity to both Odoo and Microshare platforms. The discovery system successfully identifies 9 unmapped inspection points requiring IoT device deployment, demonstrating the business value of automated gap analysis.

The roadmap scales from basic discovery to comprehensive business intelligence, addressing the full spectrum of pest control industry digitization needs. Each phase builds incrementally on proven foundations while delivering immediate business value.

The architecture supports the transition from traditional manual inspection processes to IoT-enabled predictive pest management, positioning pest control companies for competitive advantage through data-driven service delivery.
