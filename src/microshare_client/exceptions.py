"""
Custom exceptions for Microshare API integration
"""

class MicroshareAPIError(Exception):
    """Base exception for Microshare API errors"""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class AuthenticationError(MicroshareAPIError):
    """Authentication related errors"""

    def __init__(self, message: str):
        super().__init__(message, status_code=401)

class DeviceNotFoundError(MicroshareAPIError):
    """Device not found in cluster"""

    def __init__(self, device_id: str, cluster_id: str):
        message = f"Device {device_id} not found in cluster {cluster_id}"
        super().__init__(message, status_code=404)

class ClusterNotFoundError(MicroshareAPIError):
    """Cluster not found"""

    def __init__(self, cluster_id: str):
        message = f"Cluster {cluster_id} not found"
        super().__init__(message, status_code=404)

class InvalidDeviceDataError(MicroshareAPIError):
    """Invalid device data provided"""

    def __init__(self, message: str):
        super().__init__(f"Invalid device data: {message}", status_code=400)

class CacheError(Exception):
    """Cache operation errors"""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
