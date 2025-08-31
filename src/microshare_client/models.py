"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class DeviceMetaModel(BaseModel):
    """Device metadata model"""
    location: List[str] = Field(..., min_items=4, max_items=6, description="Location hierarchy array")

class DeviceCreateModel(BaseModel):
    """Model for creating new devices"""
    id: str = Field(default="00-00-00-00-00-00-00-00", description="Device ID (use default for auto-assignment)")
    meta: DeviceMetaModel
    status: str = Field(default="pending", description="Device status")
    guid: Optional[str] = Field(None, description="Unique device identifier")

class DeviceUpdateModel(BaseModel):
    """Model for updating existing devices"""
    location: Optional[List[str]] = Field(None, min_items=4, max_items=6, description="Updated location hierarchy")
    status: Optional[str] = Field(None, description="Updated device status")

class CacheStatsModel(BaseModel):
    """Model for cache statistics"""
    cached_items: int
    expired_items_cleaned: int
    cache_keys: List[str]
