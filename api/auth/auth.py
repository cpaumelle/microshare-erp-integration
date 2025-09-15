"""
Enhanced Authentication Router - Canonical Patterns
Version: 3.0.0
Created: 2025-09-13 08:30:00 UTC
Author: Claude Assistant

Integrates canonical web app authentication patterns into existing auth structure.
Works alongside your existing auth middleware and web_client.
"""

import asyncio
import httpx
import json
import base64
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import jwt
import os

# Import your existing config
from api.config.settings import settings

# Create router
router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])
security = HTTPBearer()

# Canonical environment URLs (from optimized tester)
DEV_WEB_LOGIN = "https://dapp.microshare.io/login"
DEV_API_BASE = "https://dapi.microshare.io"
PROD_WEB_LOGIN = "https://app.microshare.io/login"
PROD_API_BASE = "https://api.microshare.io"

# Session configuration
SESSION_SECRET = os.getenv('SESSION_SECRET', 'dev-secret-change-in-production')
SESSION_EXPIRE_HOURS = 24

class LoginRequest(BaseModel):
    username: str
    password: str
    environment: str = 'dev'

class LoginResponse(BaseModel):
    success: bool
    session_token: str
    user_info: Dict[str, Any]
    api_base: str
    expires_at: str

class AuthStatus(BaseModel):
    authenticated: bool
    environment: str
    api_base: str
    user_info: Optional[Dict[str, Any]] = None

async def authenticate_with_web_app(username: str, password: str, environment: str = 'dev') -> Dict[str, Any]:
    """
    Canonical web app authentication pattern from optimized performance tester.
    This is the pattern that actually works with your credentials.
    """

    # Environment configuration (canonical)
    if environment.lower() == 'dev':
        web_login_url = DEV_WEB_LOGIN
        api_base = DEV_API_BASE
    else:
        web_login_url = PROD_WEB_LOGIN
        api_base = PROD_API_BASE

    try:
        async with httpx.AsyncClient(timeout=30, follow_redirects=False) as client:
            response = await client.post(
                web_login_url,
                data={
                    'csrfToken': 'enhanced-fastapi-auth',
                    'username': username,
                    'password': password
                },
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'User-Agent': 'Microshare-ERP-Integration-Enhanced/3.0'
                }
            )

            if response.status_code == 303:  # Canonical success pattern
                jwt_token = response.cookies.get('PLAY_SESSION')
                if jwt_token:
                    # Extract OAuth2 tokens (canonical pattern from optimized tester)
                    parts = jwt_token.split('.')
                    if len(parts) == 3:
                        payload_b64 = parts[1]
                        padding = len(payload_b64) % 4
                        if padding:
                            payload_b64 += '=' * (4 - padding)

                        payload = json.loads(base64.urlsafe_b64decode(payload_b64))
                        token_data = payload.get('data', {})
                        access_token = token_data.get('access_token')

                        if access_token:
                            return {
                                'success': True,
                                'access_token': access_token,
                                'refresh_token': token_data.get('refresh_token'),
                                'api_base': api_base,
                                'environment': environment,
                                'expires_at': datetime.fromtimestamp(payload.get('exp', 0)).isoformat()
                            }

        return {'success': False, 'error': 'Authentication failed'}

    except Exception as e:
        return {'success': False, 'error': f'Authentication error: {str(e)}'}

def create_session_token(auth_result: Dict) -> str:
    """Create session JWT for the frontend"""
    payload = {
        'microshare_access_token': auth_result['access_token'],
        'api_base': auth_result['api_base'],
        'environment': auth_result['environment'],
        'exp': datetime.now() + timedelta(hours=SESSION_EXPIRE_HOURS),
        'iat': datetime.now(),
        'iss': 'microshare-erp-integration'
    }
    return jwt.encode(payload, SESSION_SECRET, algorithm='HS256')

def verify_session_token(token: str) -> Dict[str, Any]:
    """Verify session token and extract Microshare credentials"""
    try:
        payload = jwt.decode(token, SESSION_SECRET, algorithms=['HS256'])
        return {
            'success': True,
            'access_token': payload['microshare_access_token'],
            'api_base': payload['api_base'],
            'environment': payload['environment']
        }
    except jwt.ExpiredSignatureError:
        return {'success': False, 'error': 'Session expired'}
    except (jwt.DecodeError, jwt.InvalidTokenError, ValueError):
        return {'success': False, 'error': 'Invalid session token'}

# Dependency for route authentication
async def get_current_auth(credentials: HTTPAuthorizationCredentials = Security(security)) -> Dict[str, Any]:
    """FastAPI dependency for authentication - integrates with your existing middleware"""
    token_data = verify_session_token(credentials.credentials)

    if not token_data['success']:
        raise HTTPException(status_code=401, detail=token_data['error'])

    return token_data

@router.post("/login", response_model=LoginResponse)
async def enhanced_login(request: LoginRequest):
    """
    Enhanced login using canonical web app authentication pattern.
    This works with your existing credentials: cp_erp_sample@maildrop.cc
    """

    result = await authenticate_with_web_app(
        request.username,
        request.password,
        request.environment
    )

    if result['success']:
        session_token = create_session_token(result)

        return LoginResponse(
            success=True,
            session_token=session_token,
            user_info={
                'username': request.username,
                'environment': result['environment'],
                'authenticated_at': datetime.now().isoformat()
            },
            api_base=result['api_base'],
            expires_at=result['expires_at']
        )
    else:
        raise HTTPException(status_code=401, detail=result.get('error', 'Authentication failed'))

@router.post("/logout")
async def enhanced_logout():
    """
    Logout endpoint - primarily client-side token cleanup.
    Could be enhanced to invalidate server-side sessions if needed.
    """
    return {"success": True, "message": "Logout successful - clear client-side tokens"}

@router.get("/status", response_model=AuthStatus)
async def auth_status(auth_data: Dict = Depends(get_current_auth)):
    """
    Get current authentication status.
    Works with your existing auth middleware for backward compatibility.
    """
    return AuthStatus(
        authenticated=True,
        environment=auth_data['environment'],
        api_base=auth_data['api_base'],
        user_info={
            'environment': auth_data['environment'],
            'api_base': auth_data['api_base'],
            'token_valid': True
        }
    )

@router.get("/validate-token")
async def validate_token(auth_data: Dict = Depends(get_current_auth)):
    """
    Validate current session token.
    Useful for frontend token refresh logic.
    """
    return {
        "valid": True,
        "environment": auth_data['environment'],
        "api_base": auth_data['api_base'],
        "access_token_length": len(auth_data['access_token']),
        "validated_at": datetime.now().isoformat()
    }

# Export the dependency for use in other routers
__all__ = ['router', 'get_current_auth', 'verify_session_token']
