# Base ERP adapter for Microshare integration
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseERPAdapter(ABC):
    """Abstract base class for ERP system adapters"""
    
    @abstractmethod
    def map_to_microshare_format(self, erp_data: Dict[str, Any]) -> Dict[str, Any]:
        """Map ERP data to Microshare 6-field format"""
        pass
    
    @abstractmethod
    def map_from_microshare_format(self, microshare_data: Dict[str, Any]) -> Dict[str, Any]:
        """Map Microshare data to ERP format"""
        pass

