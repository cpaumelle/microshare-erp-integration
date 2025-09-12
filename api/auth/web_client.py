"""
Microshare Web Authentication v2.0.0
Web app authentication method (no API keys needed)
"""
import httpx
import json
import base64
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from api.config.settings import settings

logger = logging.getLogger(__name__)

class MicroshareWebAuth:
    """Web app authentication client"""
    
    def __init__(self):
        self.auth_url = settings.microshare_auth_url
        self.api_url = settings.microshare_api_url
        
    async def authenticate(self, username: str, password: str) -> Dict[str, Any]:
        """
        Authenticate using web app method
        Returns access token and session info
        """
        try:
            login_url = f"{self.auth_url.replace('dauth', 'dapp')}/login"
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Web app login
                response = await client.post(
                    login_url,
                    data={
                        'csrfToken': 'api-client',
                        'username': username,
                        'password': password
                    },
                    headers={
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'User-Agent': 'Microshare-API-Client/2.0'
                    },
                    follow_redirects=False
                )
                
                if response.status_code != 303:
                    return {'success': False, 'error': 'Invalid credentials'}
                
                jwt_token = response.cookies.get('PLAY_SESSION')
                if not jwt_token:
                    return {'success': False, 'error': 'No session token received'}
            
            # Extract OAuth2 tokens from JWT
            parts = jwt_token.split('.')
            if len(parts) != 3:
                return {'success': False, 'error': 'Invalid JWT format'}
            
            # Decode JWT payload
            payload_b64 = parts[1]
            padding = len(payload_b64) % 4
            if padding:
                payload_b64 += '=' * (4 - padding)
            
            payload = json.loads(base64.urlsafe_b64decode(payload_b64))
            token_data = payload.get('data', {})
            
            access_token = token_data.get('access_token')
            if not access_token:
                return {'success': False, 'error': 'No access token in response'}
            
            return {
                'success': True,
                'access_token': access_token,
                'refresh_token': token_data.get('refresh_token'),
                'expires_at': token_data.get('expires_at'),
                'api_base': self.api_url,
                'jwt_expires': datetime.fromtimestamp(payload.get('exp', 0)).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def create_auth_headers(self, access_token: str) -> Dict[str, str]:
        """Create headers for authenticated requests"""
        return {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
