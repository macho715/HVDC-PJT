"""
KPI Monitoring & Auto-Trigger Tests
MACHO-GPT TDD Phase 7: Real-time KPI Monitoring & Auto-Trigger

Tests that KPI threshold breaches (e.g., ETA delay > 24h) automatically trigger the correct system commands.
"""

import pytest
from typing import Dict, List
from datetime import datetime

# KPI 트리거 임계값 상수
KPI_TRIGGERS = {
    'delta_rate_threshold': 10,  # % change
    'eta_delay_threshold': 24,   # hours
    'pressure_threshold': 4,     # t/m²
    'utilization_threshold': 85, # %
    'cert_expiry_days': 30       # days
}

def check_auto_triggers(kpi_data: Dict) -> List[str]:
    triggers = []
    if kpi_data.get('rate_change', 0) > KPI_TRIGGERS['delta_rate_threshold']:
        triggers.append('/web_search market_updates')
    if kpi_data.get('eta_delay', 0) > KPI_TRIGGERS['eta_delay_threshold']:
        triggers.append('/weather_tie check_conditions')
    if kpi_data.get('pressure', 0) > KPI_TRIGGERS['pressure_threshold']:
        triggers.append('/heat_stow safety_verification')
    if kpi_data.get('utilization', 0) > KPI_TRIGGERS['utilization_threshold']:
        triggers.append('/warehouse optimize_capacity')
    if kpi_data.get('cert_expiry', 999) < KPI_TRIGGERS['cert_expiry_days']:
        triggers.append('/cert_chk verify_expiry')
    return triggers

class TestKPIAutoTrigger:
    """실시간 KPI 모니터링 및 자동 트리거 테스트"""

    def test_kpi_monitor_should_trigger_eta_update_when_delay_exceeds_24h(self):
        """ETA 지연이 24시간 초과 시 weather_tie 트리거 발생 검증"""
        # Given: ETA 지연 30시간
        kpi_data = {
            'eta_delay': 30
        }
        # When: 트리거 체크 실행
        triggers = check_auto_triggers(kpi_data)
        # Then: weather_tie 트리거가 포함되어야 함
        assert '/weather_tie check_conditions' in triggers
        assert len(triggers) == 1

    def test_kpi_monitor_should_trigger_heat_stow_when_pressure_exceeds_limit(self):
        """압력이 4t/m² 초과 시 heat_stow 트리거 발생 검증"""
        # Given: 압력 4.5t/m²
        kpi_data = {
            'pressure': 4.5
        }
        # When: 트리거 체크 실행
        triggers = check_auto_triggers(kpi_data)
        # Then: heat_stow 트리거가 포함되어야 함
        assert '/heat_stow safety_verification' in triggers
        assert len(triggers) == 1

    def test_kpi_monitor_should_trigger_cert_check_when_expiry_approaches(self):
        """인증 만료 30일 임박 시 cert_chk 트리거 발생 검증"""
        # Given: 인증 만료까지 25일
        kpi_data = {
            'cert_expiry': 25
        }
        # When: 트리거 체크 실행
        triggers = check_auto_triggers(kpi_data)
        # Then: cert_chk 트리거가 포함되어야 함
        assert '/cert_chk verify_expiry' in triggers
        assert len(triggers) == 1

    def test_kpi_monitor_should_trigger_warehouse_optimization_when_utilization_exceeds_85_percent(self):
        """창고 가동률이 85% 초과 시 warehouse 트리거 발생 검증"""
        # Given: 창고 가동률 90%
        kpi_data = {
            'utilization': 90
        }
        # When: 트리거 체크 실행
        triggers = check_auto_triggers(kpi_data)
        # Then: warehouse 트리거가 포함되어야 함
        assert '/warehouse optimize_capacity' in triggers
        assert len(triggers) == 1

    def test_kpi_monitor_should_trigger_market_update_when_rate_change_exceeds_10_percent(self):
        """환율 변동률이 10% 초과 시 market_updates 트리거 발생 검증"""
        # Given: 환율 변동률 15%
        kpi_data = {
            'rate_change': 15
        }
        # When: 트리거 체크 실행
        triggers = check_auto_triggers(kpi_data)
        # Then: market_updates 트리거가 포함되어야 함
        assert '/web_search market_updates' in triggers
        assert len(triggers) == 1 

    def test_kpi_monitor_should_trigger_multiple_commands_when_multiple_thresholds_exceeded(self):
        """여러 임계값 초과 시 다중 트리거 발생 검증"""
        # Given: 여러 KPI 임계값 초과
        kpi_data = {
            'eta_delay': 30,      # 24시간 초과
            'pressure': 4.5,      # 4t/m² 초과
            'utilization': 90     # 85% 초과
        }
        # When: 트리거 체크 실행
        triggers = check_auto_triggers(kpi_data)
        # Then: 여러 트리거가 포함되어야 함
        assert '/weather_tie check_conditions' in triggers
        assert '/heat_stow safety_verification' in triggers
        assert '/warehouse optimize_capacity' in triggers
        assert len(triggers) == 3 

    def test_kpi_monitor_should_not_trigger_when_all_values_within_thresholds(self):
        """모든 KPI가 임계값 내에 있을 때 트리거 발생하지 않음 검증"""
        # Given: 모든 KPI가 임계값 내
        kpi_data = {
            'eta_delay': 12,      # 24시간 미만
            'pressure': 3.5,      # 4t/m² 미만
            'utilization': 75,    # 85% 미만
            'rate_change': 5,     # 10% 미만
            'cert_expiry': 45     # 30일 초과
        }
        # When: 트리거 체크 실행
        triggers = check_auto_triggers(kpi_data)
        # Then: 트리거가 발생하지 않아야 함
        assert len(triggers) == 0 