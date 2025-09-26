"""
Constants module for HVDC Excel Reporter
Provides default values and configuration constants
"""

from datetime import datetime

# Default date period for data processing
DEFAULT_PERIOD = (
    datetime(2023, 2, 1),  # Start date
    datetime(2025, 6, 1)   # End date
)

# KPI Thresholds
KPI_THRESHOLDS = {
    "pkg_accuracy": 0.99,           # 99% accuracy target
    "site_inventory_days": 30,      # 30-day site inventory limit
    "backlog_tolerance": 0,         # Zero backlog tolerance
    "warehouse_utilization": 0.85   # 85% warehouse utilization limit
}

# Warehouse priority mapping
WAREHOUSE_PRIORITY = {
    "DSV Al Markaz": 1,  # Highest priority
    "DSV Indoor": 2,
    "DSV Outdoor": 3,
    "AAA  Storage": 4,
    "Hauler Indoor": 5,
    "DSV MZP": 6,
    "DSV MZD": 7,
    "MOSB": 8,
    "Unknown": 99
}

# Site locations
SITE_LOCATIONS = ["AGI", "DAS", "MIR", "SHU"]

# Transit locations
TRANSIT_LOCATIONS = ["MOSB", "Shifting"]

# Flow code descriptions
FLOW_CODE_DESCRIPTIONS = {
    0: "Pre-Arrival",
    1: "Port / Transit", 
    2: "Port → WH",
    3: "Port → WH → Site",
    30: "WH Stocked",
    31: "WH → Site Pending",
    32: "WH → Site Completed",
    4: "Site ↔ Site",
    5: "Return to WH",
    6: "Direct Delivery",
    99: "Unknown / Review"
} 