"""
Microshare Device Client with complete CRUD operations and caching
"""
import httpx
from typing import Dict, Any, Optional
import time

from .exceptions import MicroshareAPIError, AuthenticationError
from .enums import DeviceType
from .cache import cluster_cache

class MicroshareDeviceClient:
    """Client for interacting with Microshare device cluster APIs with caching"""

    def __init__(self, api_host: str = "https://dapi.microshare.io", auth_host: str = "https://dauth.microshare.io"):
        self.api_host = api_host.rstrip('/')
        self.auth_host = auth_host.rstrip('/')
        self.session: Optional[httpx.AsyncClient] = None
        self._token: Optional[str] = None
        self._token_expires: Optional[float] = None

    async def __aenter__(self):
        self.session = httpx.AsyncClient(timeout=httpx.Timeout(30.0))
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.aclose()

    def _get_cache_key(self, *args, **kwargs) -> str:
        """Generate consistent cache keys"""
        parts = []
        for arg in args:
            if isinstance(arg, DeviceType):
                parts.append(arg.value)
            else:
                parts.append(str(arg))

        for key, value in sorted(kwargs.items()):
            parts.append(f"{key}:{value}")

        return ":".join(parts)

    async def authenticate(self, username: str, password: str, client_id: str) -> str:
        """Authenticate and get access token"""
        if not self.session:
            raise RuntimeError("Client session not initialized. Use async context manager.")

        auth_params = {
            'username': username,
            'password': password,
            'client_id': client_id,
            'grant_type': 'password',
            'scope': 'ALL:ALL'
        }

        try:
            response = await self.session.post(
                f"{self.auth_host}/oauth2/token",
                params=auth_params
            )
            response.raise_for_status()

            auth_data = response.json()
            self._token = auth_data['access_token']
            expires_in = auth_data.get('expires_in', 3600)
            self._token_expires = time.time() + expires_in - 300

            return self._token

        except httpx.HTTPError as e:
            raise AuthenticationError(f"Authentication failed: {str(e)}")

    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authorization headers"""
        if not self._token:
            raise AuthenticationError("No access token available")

        return {
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/json"
        }

    async def _make_request(self, method: str, url: str, **kwargs) -> httpx.Response:
        """Make authenticated request with error handling"""
        if not self.session:
            raise RuntimeError("Client session not initialized")

        headers = kwargs.get('headers', {})
        headers.update(self._get_auth_headers())
        kwargs['headers'] = headers

        try:
            response = await self.session.request(method, url, **kwargs)

            if response.status_code == 401:
                raise AuthenticationError("Access token expired or invalid")
            elif response.status_code >= 400:
                raise MicroshareAPIError(
                    f"API request failed: {response.status_code}",
                    response.status_code
                )

            return response

        except httpx.HTTPError as e:
            raise MicroshareAPIError(f"HTTP request failed: {str(e)}")

    # === CORE OPERATIONS ===

    async def list_all_clusters(self) -> Dict[str, Any]:
        """List all device clusters without caching"""
        url = f"{self.api_host}/device/*"
        params = {
            'details': 'true',
            'page': 1,
            'perPage': 5000,
            'discover': 'true'
        }

        response = await self._make_request('GET', url, params=params)
        return response.json()

    async def get_specific_cluster(self, cluster_id: str, device_type: DeviceType) -> Dict[str, Any]:
        """Get specific cluster by ID and type"""
        url = f"{self.api_host}/device/{device_type.value}/{cluster_id}"
        response = await self._make_request('GET', url)
        return response.json()

    # === CRUD OPERATIONS ===

    async def add_device_to_cluster(self, cluster_id: str, device_type: DeviceType, device: Dict[str, Any]) -> Dict[str, Any]:
        """Add device to existing cluster"""
        # Get current cluster
        current_cluster = await self.get_specific_cluster(cluster_id, device_type)
        cluster_obj = current_cluster['objs'][0]

        # Add device to devices array
        if 'data' not in cluster_obj:
            cluster_obj['data'] = {'devices': []}
        if 'devices' not in cluster_obj['data']:
            cluster_obj['data']['devices'] = []

        cluster_obj['data']['devices'].append(device)

        # PUT updated cluster
        url = f"{self.api_host}/device/{device_type.value}/{cluster_id}"
        response = await self._make_request('PUT', url, json=cluster_obj)
        return response.json()

    async def update_device_in_cluster(self, cluster_id: str, device_type: DeviceType, device_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update device within cluster"""
        # Get current cluster
        current_cluster = await self.get_specific_cluster(cluster_id, device_type)
        cluster_obj = current_cluster['objs'][0]

        # Find and update device
        devices = cluster_obj.get('data', {}).get('devices', [])
        device_updated = False

        for device in devices:
            if device.get('id') == device_id:
                # Update device fields
                for key, value in updates.items():
                    if key == 'location' and 'meta' in device:
                        device['meta']['location'] = value
                    elif key == 'status':
                        device['status'] = value
                    else:
                        device[key] = value
                device_updated = True
                break

        if not device_updated:
            raise MicroshareAPIError(f"Device {device_id} not found in cluster {cluster_id}")

        # PUT updated cluster
        url = f"{self.api_host}/device/{device_type.value}/{cluster_id}"
        response = await self._make_request('PUT', url, json=cluster_obj)
        return response.json()

    async def remove_device_from_cluster(self, cluster_id: str, device_type: DeviceType, device_id: str) -> Dict[str, Any]:
        """Remove device from cluster"""
        # Get current cluster
        current_cluster = await self.get_specific_cluster(cluster_id, device_type)
        cluster_obj = current_cluster['objs'][0]

        # Remove device from devices array
        devices = cluster_obj.get('data', {}).get('devices', [])
        original_length = len(devices)

        cluster_obj['data']['devices'] = [d for d in devices if d.get('id') != device_id]

        if len(cluster_obj['data']['devices']) == original_length:
            raise MicroshareAPIError(f"Device {device_id} not found in cluster {cluster_id}")

        # PUT updated cluster
        url = f"{self.api_host}/device/{device_type.value}/{cluster_id}"
        response = await self._make_request('PUT', url, json=cluster_obj)
        return response.json()

    # === CACHED OPERATIONS ===

    def invalidate_cluster_cache(self, cluster_id: Optional[str] = None, device_type: Optional[DeviceType] = None) -> None:
        """Invalidate cluster cache entries"""
        if cluster_id and device_type:
            cache_key = self._get_cache_key("cluster", cluster_id, device_type.value)
            cluster_cache.delete(cache_key)
            print(f"Cache INVALIDATED: cluster {cluster_id}")
        else:
            cluster_cache.clear()
            print("Cache CLEARED: all cluster data")

        all_clusters_key = self._get_cache_key("clusters", scope="all")
        cluster_cache.delete(all_clusters_key)

    async def list_all_clusters_cached(self, ttl: int = 300) -> Dict[str, Any]:
        """List all device clusters with caching"""
        cache_key = self._get_cache_key("clusters", scope="all")
        cached_result = cluster_cache.get(cache_key)

        if cached_result is not None:
            print(f"Cache HIT: {cache_key}")
            return cached_result

        print(f"Cache MISS: {cache_key}, fetching from API...")
        clusters = await self.list_all_clusters()
        cluster_cache.set(cache_key, clusters, ttl)
        print(f"Cache SET: {cache_key} (TTL: {ttl}s)")

        return clusters

    # === CACHED CRUD OPERATIONS ===

    async def add_device_to_cluster_cached(self, cluster_id: str, device_type: DeviceType, device: Dict[str, Any]) -> Dict[str, Any]:
        """Add device to cluster and invalidate cache"""
        result = await self.add_device_to_cluster(cluster_id, device_type, device)
        self.invalidate_cluster_cache(cluster_id, device_type)
        return result

    async def update_device_in_cluster_cached(self, cluster_id: str, device_type: DeviceType, device_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update device and invalidate cache"""
        result = await self.update_device_in_cluster(cluster_id, device_type, device_id, updates)
        self.invalidate_cluster_cache(cluster_id, device_type)
        return result

    async def remove_device_from_cluster_cached(self, cluster_id: str, device_type: DeviceType, device_id: str) -> Dict[str, Any]:
        """Remove device and invalidate cache"""
        result = await self.remove_device_from_cluster(cluster_id, device_type, device_id)
        self.invalidate_cluster_cache(cluster_id, device_type)
        return result
