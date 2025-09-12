"""
Optimized Device Client v2.0.0  
High-performance Microshare device management
"""
import asyncio
import logging
from typing import List, Dict, Any, Optional
from api.core.http_client import MicroshareHTTPClient
from api.auth.web_client import MicroshareWebAuth
from api.devices.models import DeviceCluster, Device, DeviceType
from api.config.settings import settings

logger = logging.getLogger(__name__)

class OptimizedDeviceClient:
    """High-performance device client with caching"""
    
    def __init__(self):
        self.http_client = MicroshareHTTPClient()
        self.auth_client = MicroshareWebAuth()
        self._access_token: Optional[str] = None
        self._cluster_cache: Dict[str, DeviceCluster] = {}
        
    async def authenticate(self, username: str, password: str) -> bool:
        """Authenticate and store access token"""
        auth_result = await self.auth_client.authenticate(username, password)
        
        if auth_result['success']:
            self._access_token = auth_result['access_token']
            logger.info("Authentication successful")
            return True
        else:
            logger.error(f"Authentication failed: {auth_result.get('error')}")
            return False
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers"""
        if not self._access_token:
            raise ValueError("Not authenticated - call authenticate() first")
        return self.auth_client.create_auth_headers(self._access_token)
    
    async def discover_clusters(self, page_size: int = 2000) -> List[DeviceCluster]:
        """
        Discover all device clusters (optimized pattern)
        Uses wildcard discovery for initial cluster identification
        """
        headers = self._get_auth_headers()
        
        params = {
            'details': 'true',
            'page': 1,
            'perPage': page_size,
            'discover': 'true'
        }
        
        logger.info("Starting cluster discovery...")
        response = await self.http_client.get("/device/*", headers, params)
        
        clusters = []
        for cluster_data in response.get('objs', []):
            cluster = DeviceCluster(
                id=cluster_data['_id'],
                name=cluster_data.get('name', 'Unknown'),
                record_type=cluster_data.get('recType', 'unknown'),
                devices=self._parse_devices(cluster_data.get('data', {}))
            )
            clusters.append(cluster)
            self._cluster_cache[cluster.id] = cluster
            
        logger.info(f"Discovered {len(clusters)} clusters with {sum(len(c.devices) for c in clusters)} total devices")
        return clusters
    
    async def get_cluster_direct(self, cluster_id: str, record_type: str) -> Optional[DeviceCluster]:
        """
        Get cluster directly (optimized ~500ms response)
        """
        headers = self._get_auth_headers()
        endpoint = f"/device/{record_type}/{cluster_id}"
        
        try:
            response = await self.http_client.get(endpoint, headers)
            cluster_data = response.get('objs', [{}])[0]
            
            return DeviceCluster(
                id=cluster_data['_id'],
                name=cluster_data.get('name', 'Unknown'),
                record_type=cluster_data.get('recType', record_type),
                devices=self._parse_devices(cluster_data.get('data', {}))
            )
        except Exception as e:
            logger.error(f"Failed to get cluster {cluster_id}: {str(e)}")
            return None
    
    async def get_all_clusters_concurrent(self) -> List[DeviceCluster]:
        """
        Get all clusters concurrently for maximum performance
        """
        if not self._cluster_cache:
            await self.discover_clusters()
        
        tasks = []
        for cluster_id, cluster in self._cluster_cache.items():
            task = self.get_cluster_direct(cluster_id, cluster.record_type)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        clusters = []
        for result in results:
            if isinstance(result, DeviceCluster):
                clusters.append(result)
        
        return clusters
    
    def _parse_devices(self, cluster_data: Dict[str, Any]) -> List[Device]:
        """Parse devices from cluster data"""
        devices = []
        
        for device_data in cluster_data.get('devices', []):
            # Parse location array (6-field structure)
            location_array = device_data.get('meta', {}).get('location', [])
            
            if len(location_array) >= 6:
                from api.devices.models import DeviceLocation
                location = DeviceLocation(
                    customer=location_array[0],
                    site=location_array[1], 
                    area=location_array[2],
                    sensor=location_array[3],
                    placement=location_array[4],
                    configuration=location_array[5]
                )
                
                device = Device(
                    id=device_data.get('id', '00-00-00-00-00-00-00-00'),
                    location=location,
                    status=device_data.get('status', 'pending'),
                    guid=device_data.get('guid')
                )
                devices.append(device)
        
        return devices
