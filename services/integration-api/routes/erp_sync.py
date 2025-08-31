"""
ERP Synchronization endpoints - Phase 1 Discovery Implementation
Real implementation with Odoo integration and Microshare device mapping
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Any, Optional
import xmlrpc.client
import os
from datetime import datetime

from ..dependencies import get_microshare_client
from core.client import MicroshareDeviceClient
from core.enums import DeviceType
from core.exceptions import MicroshareAPIError

router = APIRouter(tags=["ERP Synchronization"])

# Odoo connection configuration
ODOO_CONFIG = {
    'host': os.getenv('ODOO_HOST', 'http://10.44.1.17:8069'),
    'database': os.getenv('ODOO_DATABASE', 'pest_demo'),
    'username': os.getenv('ODOO_USERNAME', 'cpaumelle@microshare.io'),
    'password': os.getenv('ODOO_PASSWORD', 'pfw*XQP8bfj8ztx7mvd'),
    'pest_category_id': int(os.getenv('ODOO_PEST_CATEGORY_ID', '4'))
}

class OdooClient:
    """Simple Odoo XML-RPC client for ERP data access"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.common = None
        self.models = None
        self.uid = None
        self._connect()
    
    def _connect(self):
        """Establish connection to Odoo"""
        try:
            self.common = xmlrpc.client.ServerProxy(f"{self.config['host']}/xmlrpc/2/common")
            self.models = xmlrpc.client.ServerProxy(f"{self.config['host']}/xmlrpc/2/object")
            
            # Authenticate
            self.uid = self.common.authenticate(
                self.config['database'],
                self.config['username'], 
                self.config['password'],
                {}
            )
            
            if not self.uid:
                raise Exception("Odoo authentication failed")
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Odoo connection failed: {str(e)}")
    
    def get_inspection_points(self) -> List[Dict[str, Any]]:
        """Get all pest control inspection points from Odoo"""
        try:
            inspection_points = self.models.execute_kw(
                self.config['database'], 
                self.uid, 
                self.config['password'],
                'product.product',
                'search_read',
                [[('categ_id', '=', self.config['pest_category_id'])]],
                {'fields': ['id', 'name', 'default_code', 'barcode', 'description', 'active']}
            )
            
            return inspection_points
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch inspection points: {str(e)}")

def parse_erp_location(inspection_point: Dict[str, Any]) -> Dict[str, str]:
    """Extract location components from ERP inspection point data"""
    
    name = inspection_point.get('name', '')
    default_code = inspection_point.get('default_code', '')
    description = inspection_point.get('description', '')
    
    # Parse location from name pattern: "Golden Crust Manchester - Flour Storage Silo A"
    if ' - ' in name:
        parts = name.split(' - ', 1)
        customer_site = parts[0].strip()
        area = parts[1].strip()
        
        # Try to split customer and site
        if 'Golden Crust' in customer_site:
            customer = 'Golden Crust Manchester'  # Normalized
            site = 'Manchester Production'
        else:
            customer = customer_site
            site = customer_site
    else:
        # Handle inspection point format: "Inspection Point 01 - Kitchen Food Prep Area"
        customer = "Golden Crust Manchester"  # Default customer
        site = "Manchester Production"
        area = name
    
    return {
        'customer': customer,
        'site': site, 
        'area': area,
        'erp_reference': default_code,
        'placement': 'Internal',  # Default
        'configuration': 'Bait/Lured'  # Default
    }

def find_matching_microshare_device(devices: List[Dict], erp_reference: str) -> Optional[Dict]:
    """Find Microshare device that matches ERP reference code"""
    
    for device in devices:
        location = device.get('meta', {}).get('location', [])
        if len(location) > 3 and location[3] == erp_reference:
            return device
    
    return None

# Legacy endpoints for compatibility
@router.get("/status")
async def erp_sync_status():
    """Get ERP synchronization status - Enhanced with real Odoo connection"""
    try:
        # Test Odoo connection
        odoo = OdooClient(ODOO_CONFIG)
        inspection_points = odoo.get_inspection_points()
        
        return {
            "status": "ERP sync operational",
            "version": "2.0.0 - Phase 1 Discovery",
            "features": ["Odoo integration", "Device discovery", "Read-only mapping", "Inspection point analysis"],
            "implementation_status": "Phase 1 - Discovery operational",
            "odoo_connection": "connected",
            "inspection_points": len(inspection_points),
            "discovery_endpoints": [
                "/erp/discovery/status",
                "/erp/discovery/inspection-points", 
                "/erp/discovery/mapping",
                "/erp/discovery/unmapped"
            ]
        }
        
    except Exception as e:
        return {
            "status": "ERP sync degraded",
            "version": "2.0.0 - Phase 1 Discovery",
            "odoo_connection": "failed",
            "error": str(e),
            "implementation_status": "Discovery endpoints available, Odoo connection issues"
        }

@router.post("/sync")
async def trigger_erp_sync():
    """Trigger ERP synchronization - Phase 1 Discovery Mode"""
    return {
        "message": "ERP sync Phase 1 - Discovery mode active",
        "phase": "read_only_discovery", 
        "actions_available": [
            "GET /erp/discovery/mapping - Analyze ERP to Microshare mapping",
            "GET /erp/discovery/unmapped - Find unmapped inspection points",
            "Phase 2 coming: Create Microshare devices for unmapped ERP points"
        ],
        "discovery_mode": True,
        "write_operations": False
    }

@router.get("/mapping")
async def get_erp_mapping():
    """Get ERP to Microshare field mappings - Enhanced with real data"""
    
    # Get sample data to show real mapping
    try:
        odoo = OdooClient(ODOO_CONFIG)
        inspection_points = odoo.get_inspection_points()
        sample_point = inspection_points[0] if inspection_points else None
        
        if sample_point:
            location_data = parse_erp_location(sample_point)
            microshare_location = [
                location_data['customer'],
                location_data['site'],
                location_data['area'],
                location_data['erp_reference'],
                location_data['placement'],
                location_data['configuration']
            ]
        else:
            microshare_location = ["Customer", "Site", "Area", "ERP_REF", "Internal", "Bait/Lured"]
            
    except:
        microshare_location = ["Customer", "Site", "Area", "ERP_REF", "Internal", "Bait/Lured"]
    
    return {
        "mapping_strategy": "reference_code_matching",
        "odoo_erp_structure": {
            "model": "product.product",
            "category_filter": f"categ_id = {ODOO_CONFIG['pest_category_id']}",
            "key_fields": {
                "id": "Unique Odoo record ID", 
                "default_code": "ERP internal reference (primary matching key)",
                "barcode": "DevEUI storage field",
                "name": "Human readable location description"
            }
        },
        "microshare_structure": {
            "location_array_mapping": {
                "location[0]": "Customer name",
                "location[1]": "Site name", 
                "location[2]": "Area name",
                "location[3]": "ERP reference (matches Odoo default_code)",
                "location[4]": "Placement (Internal/External)",
                "location[5]": "Configuration (Bait/Lured/etc)"
            }
        },
        "matching_logic": {
            "primary_key": "Odoo.default_code ↔ Microshare.location[3]",
            "device_creation": "Unmapped ERP points get DevEUI = '00-00-00-00-00-00-00-00'"
        },
        "example_mapping": {
            "odoo_record": {
                "id": sample_point['id'] if sample_point else 99,
                "default_code": sample_point['default_code'] if sample_point else "ERP024_025_01",
                "name": sample_point['name'] if sample_point else "Golden Crust Manchester - Flour Storage Silo A"
            },
            "microshare_device": {
                "id": "00-00-00-00-00-00-00-00",
                "meta": {"location": microshare_location},
                "status": "pending"
            }
        }
    }

