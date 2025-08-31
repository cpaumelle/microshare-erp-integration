# Field mapping utilities for ERP integration
from typing import Dict, Any, List

class FieldMapper:
    """Utility class for mapping fields between ERP and Microshare"""
    
    def __init__(self):
        self.microshare_fields = [
            'customer',
            'site', 
            'area',
            'location_id',
            'deployment_type',
            'trap_configuration'
        ]
    
    def map_to_six_field_format(self, data: Dict[str, Any]) -> List[str]:
        """Convert data to Microshare 6-field location array"""
        return [
            data.get('customer', ''),
            data.get('site', ''),
            data.get('area', ''),
            data.get('location_id', ''),
            data.get('deployment_type', 'Internal'),
            data.get('trap_configuration', 'Bait/Lured')
        ]

