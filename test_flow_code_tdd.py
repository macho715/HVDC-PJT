#!/usr/bin/env python3
"""
HVDC Flow Code TDD Tests
Following Kent Beck's TDD methodology: Red → Green → Refactor
"""

import pytest


def test_should_return_flow_code_0_for_pre_arrival_status():
    """Test: Should return flow code 0 for Pre_Arrival status"""
    # Arrange
    record = {"Status": "PRE ARRIVAL"}
    
    # Act
    result = calculate_flow_code(record)
    
    # Assert
    assert result == 0, f"Expected flow code 0 for Pre_Arrival status, got {result}"


def test_should_return_flow_code_1_for_direct_port_to_site_shipment():
    """Test: Should return flow code 1 for direct Port→Site shipment"""
    # Arrange
    record = {"Status": "Active"}  # Active status with no warehouse = direct shipment
    
    # Act
    result = calculate_flow_code(record)
    
    # Assert
    assert result == 1, f"Expected flow code 1 for direct Port→Site shipment, got {result}"


def calculate_flow_code(record):
    """Calculate logistics flow code based on record data"""
    # Minimum implementation to make the test pass (Green phase)
    if record.get("Status") == "PRE ARRIVAL":
        return 0 