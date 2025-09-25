"""
HVDC Excel Reporter - Utilities File
"""

import logging
import pandas as pd


def setup_logging():
    """Sets up the logging configuration."""
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    return logging.getLogger(__name__)


def get_pkg(row):
    """Safely extracts the quantity from the 'Pkg' column."""
    pkg_value = row.get("Pkg", 1)
    if pd.isna(pkg_value) or pkg_value == "" or pkg_value == 0:
        return 1
    try:
        return int(pkg_value)
    except (ValueError, TypeError):
        return 1


def get_sqm(row):
    """
    Safely extracts the area from SQM-related columns.
    If no SQM data is found, it estimates it based on the Pkg value.
    """
    sqm_columns = [
        "SQM",
        "sqm",
        "Area",
        "area",
        "AREA",
        "Size_SQM",
        "Item_SQM",
        "Package_SQM",
        "Total_SQM",
        "M2",
        "m2",
        "SQUARE",
        "Square",
        "square",
        "Dimension",
        "Space",
        "Volume_SQM",
    ]

    for col in sqm_columns:
        if col in row.index and pd.notna(row[col]):
            try:
                sqm_value = float(row[col])
                if sqm_value > 0:
                    return sqm_value
            except (ValueError, TypeError):
                continue

    pkg_value = get_pkg(row)
    estimated_sqm = pkg_value * 1.5
    return estimated_sqm


def get_sqm_with_source(row):
    """
    Extracts SQM and identifies its source (actual vs. estimated).
    """
    sqm_columns = [
        "SQM",
        "sqm",
        "Area",
        "area",
        "AREA",
        "Size_SQM",
        "Item_SQM",
        "Package_SQM",
        "Total_SQM",
        "M2",
        "m2",
        "SQUARE",
        "Square",
        "square",
        "Dimension",
        "Space",
        "Volume_SQM",
    ]

    for col in sqm_columns:
        if col in row.index and pd.notna(row[col]):
            try:
                sqm_value = float(row[col])
                if sqm_value > 0:
                    return sqm_value, "ACTUAL", col
            except (ValueError, TypeError):
                continue

    pkg_value = get_pkg(row)
    estimated_sqm = pkg_value * 1.5
    return estimated_sqm, "ESTIMATED", "PKG_BASED"


def check_duplicate_function(func_name: str, namespace):
    """
    Detects duplicate function definitions in a given namespace.
    """
    if func_name in namespace:
        raise RuntimeError(f"Duplicate definition detected: {func_name}")
