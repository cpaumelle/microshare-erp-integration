"""
Enumerations for Microshare API integration
"""
from enum import Enum
from typing import Optional

class DeviceType(Enum):
    """Device type enumeration based on Microshare recType values"""

    TRAP = "io.microshare.trap.packed"
    GATEWAY = "io.microshare.gateway.health.packed"

    @classmethod
    def from_rec_type(cls, rec_type: str) -> Optional['DeviceType']:
        """Convert Microshare recType to DeviceType enum"""
        for device_type in cls:
            if device_type.value == rec_type:
                return device_type
        return None

    @classmethod
    def from_string(cls, device_string: str) -> Optional['DeviceType']:
        """Convert string to DeviceType (trap/gateway)"""
        device_string = device_string.lower().strip()

        if device_string in ['trap', 'traps', 'motion', 'rodent']:
            return cls.TRAP
        elif device_string in ['gateway', 'gateways', 'gw']:
            return cls.GATEWAY

        return None

    def get_record_type(self) -> str:
        """Get the Microshare recType value"""
        return self.value

    def get_display_name(self) -> str:
        """Get human-readable display name"""
        if self == DeviceType.TRAP:
            return "Trap/Motion Sensor"
        elif self == DeviceType.GATEWAY:
            return "Gateway"
        return "Unknown Device"

class PlacementType(Enum):
    """Standard placement types for devices"""

    INTERNAL = "Internal"
    EXTERNAL = "External"

    @classmethod
    def get_valid_values(cls):
        """Get list of valid placement values"""
        return [pt.value for pt in cls]

class ConfigurationType(Enum):
    """Standard configuration types for trap devices"""

    POISON = "Poison"
    BAIT_LURED = "Bait/Lured"
    KILL_TRAP = "Kill/Trap"
    GLUE = "Glue"
    CAVITY = "Cavity"

    @classmethod
    def get_valid_values(cls):
        """Get list of valid configuration values"""
        return [ct.value for ct in cls]

class DeviceStatus(Enum):
    """Standard device status values"""

    PENDING = "pending"
    ACTIVE = "active"
    INACTIVE = "inactive"
    PROVISIONING = "Provisioning"

    @classmethod
    def get_valid_values(cls):
        """Get list of valid status values"""
        return [ds.value for ds in cls]
