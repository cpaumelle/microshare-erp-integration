# Synchronization patterns for ERP integration
from typing import Dict, Any, Optional
import asyncio

class SyncPattern:
    """Common synchronization patterns for ERP integration"""
    
    def __init__(self, microshare_client, erp_adapter):
        self.microshare_client = microshare_client
        self.erp_adapter = erp_adapter
    
    async def sync_to_microshare(self, erp_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sync ERP data to Microshare"""
        microshare_format = self.erp_adapter.map_to_microshare_format(erp_data)
        result = await self.microshare_client.create_device(microshare_format)
        return result
    
    async def sync_from_microshare(self, device_id: str) -> Dict[str, Any]:
        """Sync Microshare data to ERP"""
        microshare_data = await self.microshare_client.get_device(device_id)
        erp_format = self.erp_adapter.map_from_microshare_format(microshare_data)
        return erp_format

