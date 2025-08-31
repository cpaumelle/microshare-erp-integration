"""
FastAPI dependencies for Microshare client management
"""
import os
from functools import lru_cache
from typing import Dict, Any

from src.microshare_client.client import MicroshareDeviceClient
from src.microshare_client.exceptions import AuthenticationError

@lru_cache()
def get_settings() -> Dict[str, Any]:
    """Get application settings from environment"""
    return {
        'microshare_api_host': os.getenv('MICROSHARE_API_HOST', 'https://dapi.microshare.io'),
        'microshare_auth_host': os.getenv('MICROSHARE_AUTH_HOST', 'https://dauth.microshare.io'), 
        'microshare_username': os.getenv('MICROSHARE_USERNAME', 'cp_erp_sample@maildrop.cc'),
        'microshare_password': os.getenv('MICROSHARE_PASSWORD', 'AVH7dbz!brt-rfn0tdk'),
        'microshare_client_id': os.getenv('MICROSHARE_CLIENT_ID', '4DA225C6-94AA-4600-8509-2661CC2A7724')
    }

# Global client instance
_client_instance = None

async def get_microshare_client() -> MicroshareDeviceClient:
    """
    Dependency to get authenticated Microshare client instance.
    Implements singleton pattern for connection reuse.
    """
    global _client_instance
    
    settings = get_settings()
    
    if _client_instance is None:
        _client_instance = MicroshareDeviceClient(
            api_host=settings['microshare_api_host'],
            auth_host=settings['microshare_auth_host']
        )
        
        await _client_instance.__aenter__()
        
        try:
            await _client_instance.authenticate(
                username=settings['microshare_username'],
                password=settings['microshare_password'],
                client_id=settings['microshare_client_id']
            )
            print(f"✅ Authenticated with Microshare API")
            
        except Exception as e:
            print(f"❌ Authentication failed: {e}")
            await _client_instance.__aexit__(None, None, None)
            _client_instance = None
            raise AuthenticationError(f"Failed to authenticate with Microshare: {str(e)}")
    
    return _client_instance

async def cleanup_microshare_client():
    """Cleanup client on application shutdown"""
    global _client_instance
    
    if _client_instance:
        try:
            await _client_instance.__aexit__(None, None, None)
            print("✅ Microshare client cleaned up")
        except Exception as e:
            print(f"⚠️ Error during client cleanup: {e}")
        finally:
            _client_instance = None
