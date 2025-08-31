"""
ERP Discovery routes - Phase 1 Implementation
Separate file for discovery endpoints with Odoo integration
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

router = APIRouter(tags=["ERP Discovery"], prefix="/erp/discovery")

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
    
    # Parse location from name patterns
    if ' - ' in name:
        parts = name.split(' - ', 1)
        customer_site = parts[0].strip()
        area = parts[1].strip()
        
        # Standardize customer/site naming
        if 'Golden Crust' in customer_site:
            customer = 'Golden Crust Manchester'
            site = 'Manchester Production'
        else:
            customer = customer_site
            site = customer_site
    else:
        customer = "Golden Crust Manchester"  # Default customer
        site = "Manchester Production"
        area = name
    
    return {
        'customer': customer,
        'site': site, 
        'area': area,
        'erp_reference': default_code,
        'placement': 'Internal',
        'configuration': 'Bait/Lured'
    }

def find_matching_microshare_device(devices: List[Dict], erp_reference: str) -> Optional[Dict]:
    """Find Microshare device that matches ERP reference code"""
    
    for device in devices:
        location = device.get('meta', {}).get('location', [])
        if len(location) > 3 and location[3] == erp_reference:
            return device
    
    return None

@router.get("/status")
async def discovery_status():
    """Get ERP discovery system status"""
    try:
        # Test Odoo connection
        odoo = OdooClient(ODOO_CONFIG)
        inspection_points = odoo.get_inspection_points()
        
        return {
            "status": "operational",
            "odoo_connected": True,
            "inspection_points_found": len(inspection_points),
            "discovery_mode": "read_only",
            "default_deveui": "00-00-00-00-00-00-00-00",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "odoo_connected": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/inspection-points")
async def get_erp_inspection_points():
    """Get all inspection points from Odoo ERP"""
    
    odoo = OdooClient(ODOO_CONFIG)
    inspection_points = odoo.get_inspection_points()
    
    # Parse and normalize inspection points
    normalized_points = []
    for point in inspection_points:
        location_data = parse_erp_location(point)
        
        normalized_point = {
            'odoo_id': point['id'],
            'name': point['name'],
            'erp_reference': point['default_code'],
            'current_deveui': point.get('barcode'),
            'location': location_data,
            'active': point.get('active', True),
            'microshare_location_array': [
                location_data['customer'],
                location_data['site'],
                location_data['area'], 
                location_data['erp_reference'],
                location_data['placement'],
                location_data['configuration']
            ]
        }
        
        normalized_points.append(normalized_point)
    
    return {
        "inspection_points": normalized_points,
        "total_count": len(normalized_points),
        "source": "odoo_erp",
        "timestamp": datetime.now().isoformat()
    }

@router.get("/mapping")
async def discover_erp_microshare_mapping(
    client: MicroshareDeviceClient = Depends(get_microshare_client)
):
    """Discover mapping relationships between ERP and Microshare"""
    
    # Get ERP inspection points
    odoo = OdooClient(ODOO_CONFIG) 
    inspection_points = odoo.get_inspection_points()
    
    # Get all Microshare devices
    microshare_data = await client.list_all_clusters_cached(ttl=300)
    all_devices = []
    
    for cluster in microshare_data.get('objs', []):
        devices = cluster.get('data', {}).get('devices', [])
        for device in devices:
            device['cluster_id'] = cluster['_id']
            device['cluster_name'] = cluster.get('name', '')
            device['device_type'] = cluster.get('recType', '')
            all_devices.append(device)
    
    # Create mapping analysis
    mapping_results = []
    
    for point in inspection_points:
        location_data = parse_erp_location(point)
        erp_reference = point['default_code']
        
        # Try to find matching Microshare device
        matching_device = find_matching_microshare_device(all_devices, erp_reference)
        
        mapping_result = {
            'odoo_id': point['id'],
            'erp_reference': erp_reference,
            'erp_name': point['name'],
            'microshare_location': [
                location_data['customer'],
                location_data['site'],
                location_data['area'],
                location_data['erp_reference'],
                location_data['placement'], 
                location_data['configuration']
            ],
            'mapping_status': 'mapped' if matching_device else 'unmapped',
            'microshare_device': matching_device,
            'recommended_action': 'none' if matching_device else 'create_device_with_default_deveui'
        }
        
        mapping_results.append(mapping_result)
    
    # Generate summary statistics
    mapped_count = sum(1 for r in mapping_results if r['mapping_status'] == 'mapped')
    unmapped_count = len(mapping_results) - mapped_count
    
    return {
        "mapping_results": mapping_results,
        "summary": {
            "total_erp_points": len(mapping_results),
            "mapped_devices": mapped_count,
            "unmapped_devices": unmapped_count,
            "mapping_coverage": f"{(mapped_count/len(mapping_results)*100):.1f}%" if mapping_results else "0%"
        },
        "discovery_timestamp": datetime.now().isoformat(),
        "phase": "read_only_discovery"
    }

@router.get("/unmapped")
async def get_unmapped_inspection_points(
    client: MicroshareDeviceClient = Depends(get_microshare_client)
):
    """Get ERP inspection points that have no corresponding Microshare devices"""
    
    # Get full mapping
    mapping_response = await discover_erp_microshare_mapping(client)
    mapping_results = mapping_response['mapping_results']
    
    # Filter unmapped points
    unmapped_points = [r for r in mapping_results if r['mapping_status'] == 'unmapped']
    
    return {
        "unmapped_inspection_points": unmapped_points,
        "count": len(unmapped_points),
        "next_phase_action": "create_microshare_devices_with_default_deveui",
        "default_device_template": {
            "id": "00-00-00-00-00-00-00-00",
            "status": "pending",
            "meta": {
                "location": "derived_from_erp_location_data"
            }
        }
    }
