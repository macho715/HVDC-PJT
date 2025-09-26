"""
MACHO-GPT Integration Tests
Phase 7: MACHO-GPT Integration - TDD Cycle

Tests AI mode management, command interface, and containment modes
for MACHO-GPT logistics system.
"""

import pytest
import pandas as pd
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from unittest.mock import Mock, patch, MagicMock
import asyncio

# Configure logging for MACHO-GPT
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ContainmentMode:
    """Containment Mode 클래스"""
    name: str
    confidence_threshold: float
    auto_triggers: bool
    description: str
    capabilities: List[str]

@dataclass
class CommandRequest:
    """명령어 요청 클래스"""
    command: str
    args: Dict[str, Any]
    user_role: str
    mode: str
    timestamp: datetime

@dataclass
class CommandResponse:
    """명령어 응답 클래스"""
    status: str
    data: Dict[str, Any]
    confidence: float
    mode: str
    triggers: List[str]
    execution_time: float

class MACHOGPTIntegration:
    """MACHO-GPT 통합 시스템"""
    
    def __init__(self):
        self.current_mode = "PRIME"
        self.modes = {
            "PRIME": ContainmentMode("PRIME", 0.90, True, "일반 물류 작업", ["basic_operations", "data_analysis"]),
            "LATTICE": ContainmentMode("LATTICE", 0.95, True, "창고 및 적재 최적화", ["stowage_optimization", "pressure_analysis"]),
            "ORACLE": ContainmentMode("ORACLE", 0.92, True, "데이터 분석 및 예측", ["predictive_analytics", "real_time_validation"]),
            "RHYTHM": ContainmentMode("RHYTHM", 0.91, True, "KPI 모니터링 및 알림", ["kpi_tracking", "alert_system"]),
            "COST-GUARD": ContainmentMode("COST-GUARD", 0.93, True, "비용 관리 및 승인", ["cost_validation", "approval_workflow"]),
            "ZERO": ContainmentMode("ZERO", 0.0, False, "오류 복구 및 안전 모드", ["error_recovery", "manual_intervention"])
        }
        self.command_registry = {}
        self.kpi_triggers = {}
        
    def switch_mode(self, new_mode: str, reason: str = "") -> Dict[str, Any]:
        """
        Containment Mode 전환
        
        Args:
            new_mode: 새로운 모드 이름
            reason: 전환 이유
            
        Returns:
            Dict: 전환 결과
        """
        if new_mode not in self.modes:
            return {
                'status': 'FAIL',
                'error': f'Invalid mode: {new_mode}',
                'confidence': 0.0
            }
        
        previous_mode = self.current_mode
        self.current_mode = new_mode
        
        # 모드 전환 로그
        logger.info(f"Mode switch: {previous_mode} → {new_mode} | Reason: {reason}")
        
        return {
            'status': 'SUCCESS',
            'previous_mode': previous_mode,
            'current_mode': new_mode,
            'confidence': self.modes[new_mode].confidence_threshold,
            'capabilities': self.modes[new_mode].capabilities,
            'timestamp': datetime.now().isoformat()
        }
    
    def register_command(self, command: str, handler: callable, required_mode: str = "PRIME") -> bool:
        """
        명령어 등록
        
        Args:
            command: 명령어 이름
            handler: 처리 함수
            required_mode: 필요한 모드
            
        Returns:
            bool: 등록 성공 여부
        """
        self.command_registry[command] = {
            'handler': handler,
            'required_mode': required_mode,
            'registered_at': datetime.now()
        }
        return True
    
    def execute_command(self, request: CommandRequest) -> CommandResponse:
        """
        명령어 실행
        
        Args:
            request: 명령어 요청
            
        Returns:
            CommandResponse: 실행 결과
        """
        start_time = datetime.now()
        
        if request.command not in self.command_registry:
            return CommandResponse(
                status='FAIL',
                data={'error': f'Unknown command: {request.command}'},
                confidence=0.0,
                mode=self.current_mode,
                triggers=[],
                execution_time=0.0
            )
        
        command_info = self.command_registry[request.command]
        
        # 모드 호환성 검사
        if command_info['required_mode'] != self.current_mode:
            return CommandResponse(
                status='FAIL',
                data={'error': f'Command requires {command_info["required_mode"]} mode, current: {self.current_mode}'},
                confidence=0.0,
                mode=self.current_mode,
                triggers=['mode_incompatibility'],
                execution_time=0.0
            )
        
        try:
            # 명령어 실행
            result = command_info['handler'](request.args)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return CommandResponse(
                status='SUCCESS',
                data=result,
                confidence=self.modes[self.current_mode].confidence_threshold,
                mode=self.current_mode,
                triggers=[],
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # 오류 발생 시 ZERO 모드로 전환
            if self.current_mode != "ZERO":
                self.switch_mode("ZERO", f"Command execution failed: {str(e)}")
            
            return CommandResponse(
                status='FAIL',
                data={'error': str(e)},
                confidence=0.0,
                mode=self.current_mode,
                triggers=['error_recovery'],
                execution_time=execution_time
            )
    
    def get_mode_info(self, mode_name: str) -> Optional[ContainmentMode]:
        """모드 정보 조회"""
        return self.modes.get(mode_name)
    
    def get_available_commands(self) -> List[str]:
        """사용 가능한 명령어 목록 조회"""
        return list(self.command_registry.keys())
    
    def set_kpi_trigger(self, kpi_name: str, threshold: float, action: str) -> bool:
        """KPI 트리거 설정"""
        self.kpi_triggers[kpi_name] = {
            'threshold': threshold,
            'action': action,
            'created_at': datetime.now()
        }
        return True

class TestMACHOGPTIntegration:
    """MACHO-GPT 통합 테스트"""
    
    def setup_method(self):
        """테스트 설정"""
        self.macho_gpt = MACHOGPTIntegration()
        
        # 테스트용 명령어 등록
        def test_handler(args):
            return {'result': 'success', 'data': args.get('test_data', 'default')}
        
        self.macho_gpt.register_command('test_command', test_handler, 'PRIME')
        self.macho_gpt.register_command('lattice_command', test_handler, 'LATTICE')
    
    def test_containment_mode_switching_success(self):
        """Containment Mode 전환 성공 테스트"""
        # Given: PRIME 모드에서 시작
        assert self.macho_gpt.current_mode == "PRIME"
        
        # When: LATTICE 모드로 전환
        result = self.macho_gpt.switch_mode("LATTICE", "창고 최적화 작업 시작")
        
        # Then: 전환이 성공해야 함
        assert result['status'] == 'SUCCESS'
        assert result['previous_mode'] == 'PRIME'
        assert result['current_mode'] == 'LATTICE'
        assert result['confidence'] == 0.95
        assert 'stowage_optimization' in result['capabilities']
        assert self.macho_gpt.current_mode == "LATTICE"
    
    def test_containment_mode_switching_invalid_mode(self):
        """잘못된 모드 전환 테스트"""
        # Given: PRIME 모드에서 시작
        assert self.macho_gpt.current_mode == "PRIME"
        
        # When: 존재하지 않는 모드로 전환 시도
        result = self.macho_gpt.switch_mode("INVALID_MODE", "테스트")
        
        # Then: 전환이 실패해야 함
        assert result['status'] == 'FAIL'
        assert 'Invalid mode' in result['error']
        assert result['confidence'] == 0.0
        assert self.macho_gpt.current_mode == "PRIME"  # 모드가 변경되지 않음
    
    def test_command_registration_and_execution(self):
        """명령어 등록 및 실행 테스트"""
        # Given: 새로운 명령어 등록
        def custom_handler(args):
            return {'custom_result': args.get('input', 'default')}
        
        success = self.macho_gpt.register_command('custom_command', custom_handler, 'PRIME')
        assert success == True
        
        # When: 명령어 실행
        request = CommandRequest(
            command='custom_command',
            args={'input': 'test_data'},
            user_role='admin',
            mode='PRIME',
            timestamp=datetime.now()
        )
        
        response = self.macho_gpt.execute_command(request)
        
        # Then: 명령어가 성공적으로 실행되어야 함
        assert response.status == 'SUCCESS'
        assert response.data['custom_result'] == 'test_data'
        assert response.confidence == 0.90  # PRIME 모드 신뢰도
        assert response.mode == 'PRIME'
        assert response.execution_time >= 0  # 실행 시간은 0 이상이어야 함
    
    def test_command_execution_mode_incompatibility(self):
        """모드 호환성 검사 테스트"""
        # Given: LATTICE 모드 전환
        self.macho_gpt.switch_mode("LATTICE")
        
        # When: PRIME 모드에서만 실행 가능한 명령어 실행 시도
        request = CommandRequest(
            command='test_command',  # PRIME 모드에서만 실행 가능
            args={},
            user_role='admin',
            mode='LATTICE',
            timestamp=datetime.now()
        )
        
        response = self.macho_gpt.execute_command(request)
        
        # Then: 모드 호환성 오류가 발생해야 함
        assert response.status == 'FAIL'
        assert 'requires PRIME mode' in response.data['error']
        assert response.confidence == 0.0
        assert 'mode_incompatibility' in response.triggers
    
    def test_error_recovery_zero_mode_switch(self):
        """오류 복구 및 ZERO 모드 전환 테스트"""
        # Given: 오류를 발생시키는 명령어 등록
        def error_handler(args):
            raise Exception("Simulated error")
        
        self.macho_gpt.register_command('error_command', error_handler, 'PRIME')
        
        # When: 오류가 발생하는 명령어 실행
        request = CommandRequest(
            command='error_command',
            args={},
            user_role='admin',
            mode='PRIME',
            timestamp=datetime.now()
        )
        
        response = self.macho_gpt.execute_command(request)
        
        # Then: ZERO 모드로 전환되어야 함
        assert response.status == 'FAIL'
        assert 'Simulated error' in response.data['error']
        assert response.confidence == 0.0
        assert 'error_recovery' in response.triggers
        assert self.macho_gpt.current_mode == "ZERO"
    
    def test_mode_capabilities_and_thresholds(self):
        """모드별 기능 및 임계값 테스트"""
        # Given: 각 모드의 정보
        modes_to_test = ["PRIME", "LATTICE", "ORACLE", "RHYTHM", "COST-GUARD", "ZERO"]
        
        for mode_name in modes_to_test:
            # When: 모드 정보 조회
            mode_info = self.macho_gpt.get_mode_info(mode_name)
            
            # Then: 모드 정보가 올바르게 반환되어야 함
            assert mode_info is not None
            assert mode_info.name == mode_name
            
            # ZERO 모드는 신뢰도가 0.0이어야 함
            if mode_name == "ZERO":
                assert mode_info.confidence_threshold == 0.0
                assert mode_info.auto_triggers == False
            else:
                assert mode_info.confidence_threshold >= 0.90
                assert mode_info.auto_triggers == True
    
    def test_command_registry_management(self):
        """명령어 레지스트리 관리 테스트"""
        # Given: 여러 명령어 등록
        def handler1(args): return {'handler': '1'}
        def handler2(args): return {'handler': '2'}
        
        self.macho_gpt.register_command('cmd1', handler1, 'PRIME')
        self.macho_gpt.register_command('cmd2', handler2, 'LATTICE')
        
        # When: 사용 가능한 명령어 목록 조회
        available_commands = self.macho_gpt.get_available_commands()
        
        # Then: 등록된 명령어들이 포함되어야 함
        assert 'cmd1' in available_commands
        assert 'cmd2' in available_commands
        assert 'test_command' in available_commands
        assert 'lattice_command' in available_commands
    
    def test_kpi_trigger_configuration(self):
        """KPI 트리거 설정 테스트"""
        # Given: KPI 트리거 설정
        success = self.macho_gpt.set_kpi_trigger(
            'completion_rate',
            threshold=0.85,
            action='switch_to_rhythm_mode'
        )
        
        # Then: 트리거가 성공적으로 설정되어야 함
        assert success == True
        assert 'completion_rate' in self.macho_gpt.kpi_triggers
        assert self.macho_gpt.kpi_triggers['completion_rate']['threshold'] == 0.85
        assert self.macho_gpt.kpi_triggers['completion_rate']['action'] == 'switch_to_rhythm_mode'
    
    def test_integration_with_existing_systems(self):
        """기존 시스템과의 통합 테스트"""
        # Given: 기존 시스템 시뮬레이션
        with patch('pandas.read_excel') as mock_read_excel:
            mock_read_excel.return_value = pd.DataFrame({
                'warehouse': ['DSV Indoor', 'DSV Outdoor'],
                'inbound': [100, 150],
                'outbound': [80, 120]
            })
            
            # When: LATTICE 모드에서 창고 분석 명령어 실행
            self.macho_gpt.switch_mode("LATTICE")
            
            def warehouse_analysis_handler(args):
                df = pd.read_excel(args.get('file_path', 'test.xlsx'))
                return {
                    'total_inbound': df['inbound'].sum(),
                    'total_outbound': df['outbound'].sum(),
                    'utilization_rate': df['outbound'].sum() / df['inbound'].sum()
                }
            
            self.macho_gpt.register_command('warehouse_analysis', warehouse_analysis_handler, 'LATTICE')
            
            request = CommandRequest(
                command='warehouse_analysis',
                args={'file_path': 'warehouse_data.xlsx'},
                user_role='analyst',
                mode='LATTICE',
                timestamp=datetime.now()
            )
            
            response = self.macho_gpt.execute_command(request)
            
            # Then: 분석이 성공적으로 실행되어야 함
            assert response.status == 'SUCCESS'
            assert response.data['total_inbound'] == 250
            assert response.data['total_outbound'] == 200
            assert response.data['utilization_rate'] == 0.8
            assert response.confidence == 0.95  # LATTICE 모드 신뢰도

if __name__ == '__main__':
    pytest.main([__file__]) 