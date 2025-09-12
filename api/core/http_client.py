"""
Microshare HTTP Client v2.0.0
Clean async HTTP client for Microshare API integration
"""
import httpx
import logging
from typing import Dict, Any, Optional
from api.config.settings import settings

logger = logging.getLogger(__name__)

class MicroshareHTTPClient:
    """Async HTTP client for Microshare API calls"""
    
    def __init__(self):
        self.timeout = httpx.Timeout(settings.api_timeout)
        self.base_url = settings.microshare_api_url
        
    async def request(
        self,
        method: str,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make authenticated request to Microshare API"""
        
        url = f"{self.base_url}{endpoint}"
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                params=params
            )
            
            if response.status_code >= 400:
                logger.error(f"API request failed: {response.status_code} - {response.text}")
                response.raise_for_status()
                
            return response.json()
    
    async def get(self, endpoint: str, headers: Dict[str, str], params: Optional[Dict] = None):
        return await self.request("GET", endpoint, headers, params=params)
    
    async def post(self, endpoint: str, headers: Dict[str, str], data: Dict[str, Any]):
        return await self.request("POST", endpoint, headers, data)
