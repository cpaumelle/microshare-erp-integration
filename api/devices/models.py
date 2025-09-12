"""
Device Data Models v2.0.0
Pydantic models for Microshare device integration
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class DeviceType(str, Enum):
    """Device type enumeration"""
    TRAP = "io.microshare.trap.packed"
    GATEWAY = "io.microshare.gateway.health.packed"

class PlacementType(str, Enum):
    """Device placement options"""
    INTERNAL = "Internal"
    EXTERNAL = "External"

class ConfigurationType(str, Enum):
    """Device configuration options"""
    POISON = "Poison"
    BAIT_LURED = "Bait/Lured"
    KILL_TRAP = "Kill/Trap"
    GLUE = "Glue"
    CAVITY = "Cavity"

class DeviceLocation(BaseModel):
    """6-field device location structure"""
    customer: str = Field(..., description="Customer/Organization name")
    site: str = Field(..., description="Site/Facility name")
    area: str = Field(..., description="Area/Zone name")
    sensor: str = Field(..., description="ERP reference/internal ID")
    placement: str = Field(default=PlacementType.INTERNAL, description="Device placement")
    configuration: str = Field(default=ConfigurationType.BAIT_LURED, description="Device configuration")

class Device(BaseModel):
    """Device data model"""
    id: str = Field(default="00-00-00-00-00-00-00-00", description="Device ID/DevEUI")
    location: DeviceLocation
    status: str = Field(default="pending", description="Device status")
    guid: Optional[str] = Field(None, description="Unique device GUID")

class DeviceCluster(BaseModel):
    """Device cluster model"""
    id: str = Field(..., description="Cluster ID")
    name: str = Field(..., description="Cluster name")
    record_type: str = Field(..., description="Record type")
    devices: List[Device] = Field(default_factory=list, description="Devices in cluster")
    
class DeviceResponse(BaseModel):
    """API response model"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    count: Optional[int] = None
