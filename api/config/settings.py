"""
Microshare ERP Integration v2.0 - Configuration
Version: 2.0.0
Last Updated: 2025-09-12 13:00:00 UTC
Clean configuration management with Pydantic settings
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os

class MicroshareSettings(BaseSettings):
    """Microshare API configuration settings"""
    
    # Microshare API URLs
    microshare_auth_url: str = "https://dauth.microshare.io"
    microshare_api_url: str = "https://dapi.microshare.io"
    
    # Authentication
    microshare_username: str
    microshare_password: str
    
    # Record Types
    device_record_type: str = "io.microshare.trap.packed"
    gateway_record_type: str = "io.microshare.gateway.health.packed"
    incident_record_type: str = "io.microshare.demo.sensor.unpacked"
    
    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_level: str = "INFO"
    debug: bool = False
    
    # Performance
    cache_ttl: int = 300
    api_timeout: int = 30
    redis_url: Optional[str] = None
    
    # CSV Processing
    csv_max_file_size: int = 10485760  # 10MB
    csv_batch_size: int = 100
    csv_cache_ttl: int = 300

    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = MicroshareSettings()
