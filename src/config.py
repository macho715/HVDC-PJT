"""
HVDC Excel Reporter - Configuration File
"""
from pathlib import Path

# --- Version Information ---
PATCH_VERSION = "v2.8.3-hotfix"
PATCH_DATE = "2025-01-09"
VERIFICATION_RATE = 99.97  # Verification accuracy rate (%)

# --- KPI Thresholds ---
KPI_THRESHOLDS = {
    'pkg_accuracy': 0.99,      # 99% or higher
    'site_inventory_days': 30,  # 30 days or less
    'backlog_tolerance': 0,     # 0 cases
    'warehouse_utilization': 0.85  # 85% or less
}

# --- File Paths ---
DATA_PATH = Path("data")
HITACHI_FILE = DATA_PATH / "HVDC WAREHOUSE_HITACHI(HE).xlsx"
SIMENSE_FILE = DATA_PATH / "HVDC WAREHOUSE_SIMENSE(SIM).xlsx"
INVOICE_FILE = DATA_PATH / "HVDC WAREHOUSE_INVOICE.xlsx"

# --- Column Definitions ---
WAREHOUSE_COLUMNS = [
    'AAA Storage',
    'DSV Al Markaz',
    'DSV Indoor',
    'DSV MZP',
    'DSV MZD',
    'DSV Outdoor',
    'Hauler Indoor',
    'MOSB',
    'DHL Warehouse'
]

SITE_COLUMNS = [
    'AGI',
    'DAS',
    'MIR',
    'SHU'
]

# --- Warehouse Logic ---
WAREHOUSE_PRIORITY = [
    'DSV Al Markaz', 'DSV Indoor', 'DSV Outdoor', 'DSV MZP', 'DSV MZD', 
    'AAA Storage', 'Hauler Indoor', 'MOSB'
]

WAREHOUSE_BASE_SQM = {
    'DSV Al Markaz': 12000, 'DSV Indoor': 8500, 'DSV Outdoor': 15000,
    'DSV MZP': 1000, 'DSV MZD': 1000, 'AAA Storage': 1000,
    'Hauler Indoor': 1000, 'MOSB': 10000,
    'DHL Warehouse': 1000
}

WAREHOUSE_SQM_RATES = {
    'DSV Al Markaz': 25.5, 'DSV Indoor': 28.0, 'DSV Outdoor': 18.5,
    'DSV MZP': 22.0, 'DSV MZD': 22.0, 'AAA Storage': 20.0,
    'Hauler Indoor': 24.0, 'MOSB': 15.0,
    'DHL Warehouse': 21.0
}

# Location priority for tie-breaking same-day moves
LOC_PRIORITY = {
    'DSV Al Markaz': 1, 'DSV Indoor': 2, 'DSV Outdoor': 3,
    'AAA Storage': 4, 'Hauler Indoor': 5, 'DSV MZP': 6, 'DSV MZD': 7,
    'MOSB': 8, 'DHL Warehouse': 9,
    'MIR': 10, 'SHU': 11, 'DAS': 12, 'AGI': 13
}

# --- Flow Codes ---
FLOW_CODES = {
    0: 'Pre Arrival',
    1: 'Port → Site',
    2: 'Port → WH → Site',
    3: 'Port → WH → MOSB → Site',
    4: 'Port → WH → WH → MOSB → Site'
}

# --- All Locations ---
ALL_LOCATIONS = WAREHOUSE_COLUMNS + SITE_COLUMNS