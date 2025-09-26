#!/usr/bin/env python3
"""
TDD Phase 1: Core Infrastructure Tests
두 번째 테스트: Containment Mode Switching

테스트 목적: MACHO-GPT의 6개 Containment Mode 간 전환 기능 검증
- PRIME: 기본 모드 (최고 성능)
- ORACLE: 데이터 검증 모드 (엄격한 유효성 검사)
- ZERO: 안전 모드 (실패 시 자동 전환)
- LATTICE: OCR 모드 (Invoice 및 Container OCR)
- RHYTHM: KPI 모니터링 모드 (실시간 추적)
- COST-GUARD: 비용 관리 모드 (승인 필수)
"""

import unittest
import sys
import os
from datetime import datetime
from enum import Enum
from typing import Dict, Optional

class ContainmentMode(Enum):
    """MACHO-GPT Containment Modes"""
    PRIME = "PRIME"
    ORACLE = "ORACLE"
    ZERO = "ZERO"
    LATTICE = "LATTICE"
    RHYTHM = "RHYTHM"
    COST_GUARD = "COST_GUARD"

class MACHOModeManager:
    """MACHO-GPT 모드 관리자 (TDD용 최소 구현)"""
    
    def __init__(self, initial_mode: ContainmentMode = ContainmentMode.PRIME):
        """모드 관리자 초기화"""
        self.current_mode = initial_mode
        self.confidence_threshold = 0.95
        self.mode_history = [initial_mode]
        self.failsafe_enabled = True
        self.auto_switch_triggers = {}
        
        # 모드별 설정
        self.mode_configs = {
            ContainmentMode.PRIME: {
                'confidence_min': 0.95,
                'auto_triggers': True,
                'description': '기본 모드 - 최고 성능'
            },
            ContainmentMode.ORACLE: {
                'data_validation': 'strict',
                'real_time_sync': True,
                'description': '데이터 검증 모드 - 엄격한 유효성 검사'
            },
            ContainmentMode.LATTICE: {
                'ocr_threshold': 0.85,
                'stowage_optimization': 'advanced',
                'description': 'OCR 모드 - Invoice 및 Container OCR'
            },
            ContainmentMode.RHYTHM: {
                'kpi_refresh_interval': 3600,
                'alert_threshold': 0.10,
                'description': 'KPI 모니터링 모드 - 실시간 추적'
            },
            ContainmentMode.COST_GUARD: {
                'cost_validation': 'mandatory',
                'approval_required': True,
                'description': '비용 관리 모드 - 승인 필수'
            },
            ContainmentMode.ZERO: {
                'fallback_mode': True,
                'manual_override': 'required',
                'description': '안전 모드 - 실패 시 자동 전환'
            }
        }
    
    def switch_mode(self, target_mode: ContainmentMode, reason: str = "Manual") -> bool:
        """모드 전환"""
        if not isinstance(target_mode, ContainmentMode):
            return False
        
        previous_mode = self.current_mode
        self.current_mode = target_mode
        self.mode_history.append(target_mode)
        
        return True
    
    def get_current_mode(self) -> ContainmentMode:
        """현재 모드 조회"""
        return self.current_mode
    
    def get_mode_config(self, mode: Optional[ContainmentMode] = None) -> Dict:
        """모드 설정 조회"""
        target_mode = mode or self.current_mode
        return self.mode_configs.get(target_mode, {})
    
    def auto_switch_to_zero(self, trigger_reason: str) -> bool:
        """자동 ZERO 모드 전환 (failsafe)"""
        if not self.failsafe_enabled:
            return False
        
        if self.current_mode != ContainmentMode.ZERO:
            return self.switch_mode(ContainmentMode.ZERO, f"Failsafe: {trigger_reason}")
        
        return True
    
    def validate_mode_transition(self, from_mode: ContainmentMode, to_mode: ContainmentMode) -> bool:
        """모드 전환 유효성 검증"""
        # COST_GUARD에서 다른 모드로 전환 시 승인 필요
        if from_mode == ContainmentMode.COST_GUARD and to_mode != ContainmentMode.ZERO:
            return False  # 승인 로직은 실제 구현에서 처리
        
        # ZERO 모드에서는 수동 승인 후에만 전환 가능
        if from_mode == ContainmentMode.ZERO:
            return False  # 수동 승인 로직은 실제 구현에서 처리
        
        return True

class TestContainmentModeSwitching(unittest.TestCase):
    """Containment Mode 전환 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.mode_manager = MACHOModeManager()
        self.required_confidence = 0.95
        
    def test_initial_mode_is_prime(self):
        """초기 모드가 PRIME인지 검증"""
        current_mode = self.mode_manager.get_current_mode()
        self.assertEqual(current_mode, ContainmentMode.PRIME)
    
    def test_all_containment_modes_exist(self):
        """모든 6개 Containment Mode가 정의되어 있는지 검증"""
        expected_modes = {
            'PRIME', 'ORACLE', 'ZERO', 'LATTICE', 'RHYTHM', 'COST_GUARD'
        }
        
        actual_modes = {mode.value for mode in ContainmentMode}
        self.assertEqual(actual_modes, expected_modes)
    
    def test_mode_switching_functionality(self):
        """기본 모드 전환 기능 검증"""
        # PRIME → LATTICE 전환
        success = self.mode_manager.switch_mode(ContainmentMode.LATTICE)
        self.assertTrue(success)
        self.assertEqual(self.mode_manager.get_current_mode(), ContainmentMode.LATTICE)
        
        # LATTICE → RHYTHM 전환
        success = self.mode_manager.switch_mode(ContainmentMode.RHYTHM)
        self.assertTrue(success)
        self.assertEqual(self.mode_manager.get_current_mode(), ContainmentMode.RHYTHM)
    
    def test_mode_configurations_exist(self):
        """모든 모드의 설정이 존재하는지 검증"""
        for mode in ContainmentMode:
            config = self.mode_manager.get_mode_config(mode)
            self.assertIsInstance(config, dict)
            self.assertIn('description', config)
    
    def test_lattice_mode_ocr_configuration(self):
        """LATTICE 모드의 OCR 설정 검증"""
        self.mode_manager.switch_mode(ContainmentMode.LATTICE)
        config = self.mode_manager.get_mode_config()
        
        self.assertIn('ocr_threshold', config)
        self.assertEqual(config['ocr_threshold'], 0.85)
        self.assertIn('stowage_optimization', config)
        self.assertEqual(config['stowage_optimization'], 'advanced')
    
    def test_rhythm_mode_kpi_configuration(self):
        """RHYTHM 모드의 KPI 설정 검증"""
        self.mode_manager.switch_mode(ContainmentMode.RHYTHM)
        config = self.mode_manager.get_mode_config()
        
        self.assertIn('kpi_refresh_interval', config)
        self.assertEqual(config['kpi_refresh_interval'], 3600)
        self.assertIn('alert_threshold', config)
        self.assertEqual(config['alert_threshold'], 0.10)
    
    def test_cost_guard_mode_validation(self):
        """COST_GUARD 모드의 승인 설정 검증"""
        self.mode_manager.switch_mode(ContainmentMode.COST_GUARD)
        config = self.mode_manager.get_mode_config()
        
        self.assertIn('cost_validation', config)
        self.assertEqual(config['cost_validation'], 'mandatory')
        self.assertIn('approval_required', config)
        self.assertTrue(config['approval_required'])
    
    def test_auto_failsafe_to_zero_mode(self):
        """자동 ZERO 모드 전환 (failsafe) 기능 검증"""
        # 임의의 모드에서 시작
        self.mode_manager.switch_mode(ContainmentMode.ORACLE)
        
        # 실패 상황 시뮬레이션
        success = self.mode_manager.auto_switch_to_zero("OCR 신뢰도 < 0.85")
        
        self.assertTrue(success)
        self.assertEqual(self.mode_manager.get_current_mode(), ContainmentMode.ZERO)
    
    def test_mode_history_tracking(self):
        """모드 전환 이력 추적 검증"""
        # 여러 모드 전환
        self.mode_manager.switch_mode(ContainmentMode.LATTICE)
        self.mode_manager.switch_mode(ContainmentMode.RHYTHM)
        self.mode_manager.switch_mode(ContainmentMode.ORACLE)
        
        history = self.mode_manager.mode_history
        expected_history = [
            ContainmentMode.PRIME,    # 초기
            ContainmentMode.LATTICE,
            ContainmentMode.RHYTHM,
            ContainmentMode.ORACLE
        ]
        
        self.assertEqual(history, expected_history)
    
    def test_oracle_mode_strict_validation(self):
        """ORACLE 모드의 엄격한 검증 설정 확인"""
        self.mode_manager.switch_mode(ContainmentMode.ORACLE)
        config = self.mode_manager.get_mode_config()
        
        self.assertIn('data_validation', config)
        self.assertEqual(config['data_validation'], 'strict')
        self.assertIn('real_time_sync', config)
        self.assertTrue(config['real_time_sync'])
    
    def test_zero_mode_manual_override_required(self):
        """ZERO 모드의 수동 승인 요구사항 검증"""
        self.mode_manager.switch_mode(ContainmentMode.ZERO)
        config = self.mode_manager.get_mode_config()
        
        self.assertIn('fallback_mode', config)
        self.assertTrue(config['fallback_mode'])
        self.assertIn('manual_override', config)
        self.assertEqual(config['manual_override'], 'required')
    
    def test_integration_with_confidence_threshold(self):
        """신뢰도 임계값과 모드 전환 통합 검증"""
        # 신뢰도 임계값 확인
        self.assertGreaterEqual(self.mode_manager.confidence_threshold, self.required_confidence)
        
        # PRIME 모드에서 신뢰도 설정 확인
        config = self.mode_manager.get_mode_config(ContainmentMode.PRIME)
        self.assertIn('confidence_min', config)
        self.assertEqual(config['confidence_min'], 0.95)
    
    def test_macho_gpt_integration_ready(self):
        """MACHO-GPT 통합 준비 상태 검증"""
        # 모든 모드가 /cmd 시스템과 호환되는지 확인
        for mode in ContainmentMode:
            config = self.mode_manager.get_mode_config(mode)
            self.assertIsInstance(config, dict)
            self.assertTrue(len(config) > 0)
        
        # 통합 시스템 import 가능 확인
        try:
            from macho_integrated_system import MACHOIntegratedSystem
            integrated_system = MACHOIntegratedSystem()
            
            # 통합 시스템이 모드 관리자와 호환되는지 확인
            self.assertIsNotNone(integrated_system)
            
        except ImportError:
            self.fail("MACHO 통합 시스템과의 연동 실패")
    
    def test_tdd_red_phase_validation(self):
        """TDD RED 단계 검증"""
        test_timestamp = datetime.now()
        
        print(f"\n🔴 TDD RED Phase: Containment Mode Switching Test")
        print(f"   테스트 시간: {test_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   검증 대상: 6개 Containment Mode 전환 시스템")
        print(f"   모드 목록: {[mode.value for mode in ContainmentMode]}")
        print(f"   현재 모드: {self.mode_manager.get_current_mode().value}")
        print(f"   신뢰도 요구사항: ≥{self.required_confidence}")

if __name__ == '__main__':
    print("🧪 MACHO-GPT v3.4-mini TDD Phase 1: Core Infrastructure Tests")
    print("=" * 70)
    print("📋 Test: Containment Mode Switching")
    print("🎯 Purpose: 6개 Containment Mode 간 전환 기능 검증")
    print("-" * 70)
    print("🔧 Modes: PRIME | ORACLE | ZERO | LATTICE | RHYTHM | COST-GUARD")
    print("-" * 70)
    
    # TDD RED Phase 실행
    unittest.main(verbosity=2) 