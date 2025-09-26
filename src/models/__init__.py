"""
Data models for logistics operations
HVDC Project - Samsung C&T Logistics & ADNOC-DSV Partnership
"""

from typing import Dict, List, Optional, Any
from datetime import datetime

# Core data models
__all__ = [
    "Container",
    "Shipment", 
    "Warehouse",
    "WeatherData",
    "KPIMetrics"
]

class Container:
    """Container data model for logistics operations"""
    def __init__(self, container_id: str, **kwargs):
        self.container_id = container_id
        self.data = kwargs

class Shipment:
    """Shipment data model for tracking logistics"""
    def __init__(self, shipment_id: str, **kwargs):
        self.shipment_id = shipment_id
        self.data = kwargs

class Warehouse:
    """Warehouse data model for facility management"""
    def __init__(self, warehouse_id: str, **kwargs):
        self.warehouse_id = warehouse_id
        self.data = kwargs

class WeatherData:
    """Weather data model for logistics planning"""
    def __init__(self, location: str, **kwargs):
        self.location = location
        self.data = kwargs

class KPIMetrics:
    """KPI metrics model for performance tracking"""
    def __init__(self, metric_name: str, **kwargs):
        self.metric_name = metric_name
        self.data = kwargs
