#!/usr/bin/env python3
"""
TDD Phase 1: Core Infrastructure Tests
네 번째 테스트: KPI Trigger Configuration

테스트 목적: MACHO-GPT의 KPI 임계값 기반 자동 트리거 시스템 검증
- 신뢰도 임계값 모니터링 (≥0.95)
- 성능 KPI 추적 (처리시간 <3초)
- 자동 모드 전환 트리거
- 알림 시스템 연동
- 실시간 대시보드 업데이트

KPI Categories:
- Confidence Score (신뢰도 점수)
- Processing Time (처리 시간)
- Success Rate (성공률)
- Error Rate (오류율)
- System Load (시스템 부하)
- Memory Usage (메모리 사용량)
"""

import unittest
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import json
import time

class KPIType(Enum):
    """KPI 유형"""
    CONFIDENCE_SCORE = "confidence_score"
    PROCESSING_TIME = "processing_time"
    SUCCESS_RATE = "success_rate"
    ERROR_RATE = "error_rate"
    SYSTEM_LOAD = "system_load"
    MEMORY_USAGE = "memory_usage"

class TriggerAction(Enum):
    """트리거 액션"""
    SWITCH_TO_ZERO = "switch_to_zero"
    ALERT_NOTIFICATION = "alert_notification"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    ESCALATE_SUPPORT = "escalate_support"
    AUTO_RECOVERY = "auto_recovery"

@dataclass
class KPIThreshold:
    """KPI 임계값 설정"""
    kpi_type: KPIType
    warning_threshold: float
    critical_threshold: float
    target_value: float
    trigger_action: TriggerAction
    monitoring_interval: int  # seconds
    auto_trigger_enabled: bool

@dataclass
class KPIMetric:
    """KPI 메트릭"""
    kpi_type: KPIType
    current_value: float
    timestamp: datetime
    status: str  # "OK", "WARNING", "CRITICAL"
    trend: str   # "STABLE", "IMPROVING", "DEGRADING"

class MACHOKPITriggerSystem:
    """MACHO-GPT KPI 트리거 시스템"""
    
    def __init__(self):
        """KPI 트리거 시스템 초기화"""
        self.thresholds: Dict[KPIType, KPIThreshold] = {}
        self.current_metrics: Dict[KPIType, KPIMetric] = {}
        self.trigger_history: List[Dict] = []
        self.auto_trigger_enabled = True
        self.monitoring_active = False
        
        # KPI 임계값 설정 초기화
        self._initialize_kpi_thresholds()
    
    def _initialize_kpi_thresholds(self):
        """KPI 임계값 초기화"""
        # 신뢰도 점수 임계값
        self.thresholds[KPIType.CONFIDENCE_SCORE] = KPIThreshold(
            kpi_type=KPIType.CONFIDENCE_SCORE,
            warning_threshold=0.90,
            critical_threshold=0.85,
            target_value=0.95,
            trigger_action=TriggerAction.SWITCH_TO_ZERO,
            monitoring_interval=60,
            auto_trigger_enabled=True
        )
        
        # 처리 시간 임계값
        self.thresholds[KPIType.PROCESSING_TIME] = KPIThreshold(
            kpi_type=KPIType.PROCESSING_TIME,
            warning_threshold=3.0,
            critical_threshold=5.0,
            target_value=2.0,
            trigger_action=TriggerAction.PERFORMANCE_OPTIMIZATION,
            monitoring_interval=30,
            auto_trigger_enabled=True
        )
        
        # 성공률 임계값
        self.thresholds[KPIType.SUCCESS_RATE] = KPIThreshold(
            kpi_type=KPIType.SUCCESS_RATE,
            warning_threshold=0.90,
            critical_threshold=0.85,
            target_value=0.95,
            trigger_action=TriggerAction.ALERT_NOTIFICATION,
            monitoring_interval=300,
            auto_trigger_enabled=True
        )
        
        # 오류율 임계값
        self.thresholds[KPIType.ERROR_RATE] = KPIThreshold(
            kpi_type=KPIType.ERROR_RATE,
            warning_threshold=0.05,
            critical_threshold=0.10,
            target_value=0.01,
            trigger_action=TriggerAction.AUTO_RECOVERY,
            monitoring_interval=60,
            auto_trigger_enabled=True
        )
        
        # 시스템 부하 임계값
        self.thresholds[KPIType.SYSTEM_LOAD] = KPIThreshold(
            kpi_type=KPIType.SYSTEM_LOAD,
            warning_threshold=0.70,
            critical_threshold=0.85,
            target_value=0.50,
            trigger_action=TriggerAction.PERFORMANCE_OPTIMIZATION,
            monitoring_interval=30,
            auto_trigger_enabled=True
        )
        
        # 메모리 사용량 임계값
        self.thresholds[KPIType.MEMORY_USAGE] = KPIThreshold(
            kpi_type=KPIType.MEMORY_USAGE,
            warning_threshold=0.80,
            critical_threshold=0.90,
            target_value=0.60,
            trigger_action=TriggerAction.ESCALATE_SUPPORT,
            monitoring_interval=120,
            auto_trigger_enabled=True
        )
    
    def update_metric(self, kpi_type: KPIType, value: float) -> KPIMetric:
        """KPI 메트릭 업데이트"""
        threshold = self.thresholds.get(kpi_type)
        if not threshold:
            return None
        
        # 상태 결정 (높은 값이 좋은 KPI vs 낮은 값이 좋은 KPI)
        if kpi_type in [KPIType.CONFIDENCE_SCORE, KPIType.SUCCESS_RATE]:
            # 높은 값이 좋은 KPI
            if value >= threshold.target_value:
                status = "OK"
            elif value >= threshold.warning_threshold:
                status = "WARNING"
            else:
                status = "CRITICAL"
        else:
            # 낮은 값이 좋은 KPI
            if value <= threshold.target_value:
                status = "OK"
            elif value <= threshold.warning_threshold:
                status = "WARNING"
            else:
                status = "CRITICAL"
        
        # 메트릭 생성
        metric = KPIMetric(
            kpi_type=kpi_type,
            current_value=value,
            timestamp=datetime.now(),
            status=status,
            trend="STABLE"  # 실제 구현에서는 이력 기반 계산
        )
        
        self.current_metrics[kpi_type] = metric
        
        # 자동 트리거 확인
        if self.auto_trigger_enabled and status == "CRITICAL":
            self._trigger_action(kpi_type, threshold.trigger_action, value)
        
        return metric
    
    def _trigger_action(self, kpi_type: KPIType, action: TriggerAction, value: float):
        """트리거 액션 실행"""
        trigger_record = {
            "timestamp": datetime.now(),
            "kpi_type": kpi_type.value,
            "action": action.value,
            "value": value,
            "reason": f"KPI {kpi_type.value} critical threshold exceeded"
        }
        
        self.trigger_history.append(trigger_record)
    
    def get_kpi_status(self, kpi_type: KPIType) -> Optional[KPIMetric]:
        """KPI 상태 조회"""
        return self.current_metrics.get(kpi_type)
    
    def get_critical_metrics(self) -> List[KPIMetric]:
        """임계 상태 메트릭 조회"""
        return [metric for metric in self.current_metrics.values() 
                if metric.status == "CRITICAL"]
    
    def start_monitoring(self):
        """모니터링 시작"""
        self.monitoring_active = True
    
    def stop_monitoring(self):
        """모니터링 중지"""
        self.monitoring_active = False
    
    def get_trigger_history(self) -> List[Dict]:
        """트리거 이력 조회"""
        return self.trigger_history.copy()

class TestKPITriggerConfiguration(unittest.TestCase):
    """KPI 트리거 설정 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.kpi_system = MACHOKPITriggerSystem()
        self.required_confidence = 0.95
        self.max_processing_time = 3.0
        
    def test_kpi_trigger_system_initialization(self):
        """KPI 트리거 시스템 초기화 검증"""
        # 모든 KPI 유형에 대한 임계값 설정 확인
        expected_kpi_types = set(KPIType)
        configured_kpi_types = set(self.kpi_system.thresholds.keys())
        
        self.assertEqual(expected_kpi_types, configured_kpi_types)
        
        # 시스템 기본 상태 확인
        self.assertTrue(self.kpi_system.auto_trigger_enabled)
        self.assertFalse(self.kpi_system.monitoring_active)
    
    def test_confidence_score_threshold_configuration(self):
        """신뢰도 점수 임계값 설정 검증"""
        confidence_threshold = self.kpi_system.thresholds[KPIType.CONFIDENCE_SCORE]
        
        self.assertEqual(confidence_threshold.target_value, 0.95)
        self.assertEqual(confidence_threshold.warning_threshold, 0.90)
        self.assertEqual(confidence_threshold.critical_threshold, 0.85)
        self.assertEqual(confidence_threshold.trigger_action, TriggerAction.SWITCH_TO_ZERO)
        self.assertTrue(confidence_threshold.auto_trigger_enabled)
    
    def test_processing_time_threshold_configuration(self):
        """처리 시간 임계값 설정 검증"""
        time_threshold = self.kpi_system.thresholds[KPIType.PROCESSING_TIME]
        
        self.assertEqual(time_threshold.target_value, 2.0)
        self.assertEqual(time_threshold.warning_threshold, 3.0)
        self.assertEqual(time_threshold.critical_threshold, 5.0)
        self.assertEqual(time_threshold.trigger_action, TriggerAction.PERFORMANCE_OPTIMIZATION)
    
    def test_success_rate_monitoring(self):
        """성공률 모니터링 검증"""
        success_threshold = self.kpi_system.thresholds[KPIType.SUCCESS_RATE]
        
        self.assertEqual(success_threshold.target_value, 0.95)
        self.assertEqual(success_threshold.trigger_action, TriggerAction.ALERT_NOTIFICATION)
        self.assertEqual(success_threshold.monitoring_interval, 300)
    
    def test_kpi_metric_update_and_status(self):
        """KPI 메트릭 업데이트 및 상태 검증"""
        # 정상 신뢰도 점수 업데이트
        metric = self.kpi_system.update_metric(KPIType.CONFIDENCE_SCORE, 0.97)
        
        self.assertEqual(metric.status, "OK")
        self.assertEqual(metric.current_value, 0.97)
        self.assertIsInstance(metric.timestamp, datetime)
        
        # 임계 신뢰도 점수 업데이트
        metric = self.kpi_system.update_metric(KPIType.CONFIDENCE_SCORE, 0.80)
        
        self.assertEqual(metric.status, "CRITICAL")
        self.assertEqual(metric.current_value, 0.80)
    
    def test_auto_trigger_on_critical_threshold(self):
        """임계값 초과 시 자동 트리거 검증"""
        # 임계값 초과 시뮬레이션
        self.kpi_system.update_metric(KPIType.CONFIDENCE_SCORE, 0.80)
        
        # 트리거 이력 확인
        trigger_history = self.kpi_system.get_trigger_history()
        self.assertEqual(len(trigger_history), 1)
        
        trigger_record = trigger_history[0]
        self.assertEqual(trigger_record["kpi_type"], "confidence_score")
        self.assertEqual(trigger_record["action"], "switch_to_zero")
        self.assertEqual(trigger_record["value"], 0.80)
    
    def test_processing_time_performance_trigger(self):
        """처리 시간 성능 트리거 검증"""
        # 처리 시간 초과 시뮬레이션
        self.kpi_system.update_metric(KPIType.PROCESSING_TIME, 6.0)
        
        trigger_history = self.kpi_system.get_trigger_history()
        self.assertEqual(len(trigger_history), 1)
        
        trigger_record = trigger_history[0]
        self.assertEqual(trigger_record["action"], "performance_optimization")
    
    def test_multiple_kpi_monitoring(self):
        """다중 KPI 모니터링 검증"""
        # 여러 KPI 동시 업데이트
        self.kpi_system.update_metric(KPIType.CONFIDENCE_SCORE, 0.97)
        self.kpi_system.update_metric(KPIType.PROCESSING_TIME, 2.5)
        self.kpi_system.update_metric(KPIType.SUCCESS_RATE, 0.92)
        
        # 모든 메트릭 상태 확인
        confidence_status = self.kpi_system.get_kpi_status(KPIType.CONFIDENCE_SCORE)
        time_status = self.kpi_system.get_kpi_status(KPIType.PROCESSING_TIME)
        success_status = self.kpi_system.get_kpi_status(KPIType.SUCCESS_RATE)
        
        self.assertEqual(confidence_status.status, "OK")
        self.assertEqual(time_status.status, "WARNING")
        self.assertEqual(success_status.status, "WARNING")
    
    def test_critical_metrics_identification(self):
        """임계 상태 메트릭 식별 검증"""
        # 일부 KPI를 임계 상태로 설정
        self.kpi_system.update_metric(KPIType.CONFIDENCE_SCORE, 0.80)
        self.kpi_system.update_metric(KPIType.ERROR_RATE, 0.15)
        self.kpi_system.update_metric(KPIType.SUCCESS_RATE, 0.97)
        
        critical_metrics = self.kpi_system.get_critical_metrics()
        self.assertEqual(len(critical_metrics), 2)
        
        critical_types = {metric.kpi_type for metric in critical_metrics}
        expected_critical = {KPIType.CONFIDENCE_SCORE, KPIType.ERROR_RATE}
        self.assertEqual(critical_types, expected_critical)
    
    def test_monitoring_control(self):
        """모니터링 제어 검증"""
        # 모니터링 시작
        self.kpi_system.start_monitoring()
        self.assertTrue(self.kpi_system.monitoring_active)
        
        # 모니터링 중지
        self.kpi_system.stop_monitoring()
        self.assertFalse(self.kpi_system.monitoring_active)
    
    def test_trigger_action_types(self):
        """트리거 액션 유형 검증"""
        expected_actions = {
            "switch_to_zero", "alert_notification", "performance_optimization",
            "escalate_support", "auto_recovery"
        }
        
        actual_actions = {action.value for action in TriggerAction}
        self.assertEqual(actual_actions, expected_actions)
    
    def test_macho_integration_compliance(self):
        """MACHO 통합 시스템 호환성 검증"""
        # 신뢰도 요구사항 준수 확인
        confidence_threshold = self.kpi_system.thresholds[KPIType.CONFIDENCE_SCORE]
        self.assertGreaterEqual(confidence_threshold.target_value, self.required_confidence)
        
        # 처리 시간 요구사항 준수 확인
        time_threshold = self.kpi_system.thresholds[KPIType.PROCESSING_TIME]
        self.assertLessEqual(time_threshold.target_value, self.max_processing_time)
    
    def test_tdd_red_phase_validation(self):
        """TDD RED 단계 검증"""
        # 이 테스트 자체가 TDD RED 단계임을 검증
        test_timestamp = datetime.now()
        
        # 테스트가 실행되고 있음을 확인
        self.assertIsInstance(test_timestamp, datetime)
        
        # TDD 단계 표시
        print(f"\n🔴 TDD RED Phase: KPI Trigger Configuration Test")
        print(f"   테스트 시간: {test_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   검증 대상: {len(KPIType)} KPI 유형 트리거 시스템")
        print(f"   임계값 설정: {len(self.kpi_system.thresholds)} 개")
        print(f"   신뢰도 요구사항: ≥{self.required_confidence}")
        print(f"   처리시간 요구사항: ≤{self.max_processing_time}초")

if __name__ == '__main__':
    print("🧪 MACHO-GPT v3.5 TDD Phase 1: Core Infrastructure Tests")
    print("=" * 70)
    print("📋 Test: KPI Trigger Configuration")
    print("🎯 Purpose: KPI 임계값 기반 자동 트리거 시스템 검증")
    print("-" * 70)
    print("📊 KPI Types: Confidence | Processing Time | Success Rate | Error Rate | System Load | Memory")
    print("🔔 Triggers: Mode Switch | Alerts | Performance Optimization | Escalation | Recovery")
    print("-" * 70)
    
    # TDD RED Phase 실행
    unittest.main(verbosity=2) 