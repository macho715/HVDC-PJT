"""
Heat-Stow Analysis Pressure Limit Tests
MACHO-GPT TDD Phase 3: Heat-Stow Analysis Module

Tests pressure limit enforcement for container stowage optimization
following FANR safety regulations (4t/m² maximum pressure).
"""

import pytest
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json
import logging

# Configure logging for MACHO-GPT
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HeatStowAnalyzer:
    """Heat-Stow 분석을 위한 압력 한계 검증 클래스"""
    
    # FANR 규정 상수
    DEFAULT_PRESSURE_LIMIT = 4.0  # t/m²
    HIGH_CONFIDENCE_THRESHOLD = 0.95
    WARNING_CONFIDENCE_THRESHOLD = 0.85
    COMPLIANCE_RATE_THRESHOLD = 0.95
    
    def __init__(self, pressure_limit: float = DEFAULT_PRESSURE_LIMIT):
        """
        Heat-Stow 분석기 초기화
        
        Args:
            pressure_limit: 최대 허용 압력 (t/m²), 기본값 4.0 (FANR 규정)
        """
        self.pressure_limit = pressure_limit
        self.confidence_threshold = self.HIGH_CONFIDENCE_THRESHOLD
        self.mode = "LATTICE"  # Heat-Stow 분석 모드
        
    def _create_result_dict(self, status: str, pressure: float = 0, 
                           confidence: float = 0.0, error: str = None, 
                           is_within_limit: bool = None) -> Dict:
        """
        결과 딕셔너리 생성 헬퍼 메서드
        
        Args:
            status: 결과 상태 (SUCCESS/WARNING/FAIL/ERROR)
            pressure: 계산된 압력값
            confidence: 신뢰도 점수
            error: 오류 메시지 (있는 경우)
            is_within_limit: 압력 한계 준수 여부
            
        Returns:
            Dict: 표준화된 결과 딕셔너리
        """
        result = {
            'status': status,
            'pressure': round(pressure, 2) if pressure else 0,
            'confidence': confidence,
            'mode': self.mode,
            'timestamp': datetime.now().isoformat()
        }
        
        if error:
            result['error'] = error
        if is_within_limit is not None:
            result['is_within_limit'] = is_within_limit
            result['pressure_limit'] = self.pressure_limit
            
        return result
        
    def calculate_container_pressure(self, container_data: Dict) -> Dict:
        """
        컨테이너 압력 계산
        
        Args:
            container_data: 컨테이너 정보 (무게, 면적, 위치 등)
            
        Returns:
            Dict: 압력 계산 결과 및 검증 상태
        """
        try:
            weight = container_data.get('weight', 0)  # ton
            area = container_data.get('area', 1)      # m²
            
            if area <= 0:
                return self._create_result_dict(
                    status='FAIL',
                    confidence=0.0,
                    error='Invalid area: must be positive'
                )
            
            pressure = weight / area  # t/m²
            
            # 압력 한계 검증
            is_within_limit = pressure <= self.pressure_limit
            confidence = self.HIGH_CONFIDENCE_THRESHOLD if is_within_limit else self.WARNING_CONFIDENCE_THRESHOLD
            status = 'SUCCESS' if is_within_limit else 'WARNING'
            
            return self._create_result_dict(
                status=status,
                pressure=pressure,
                confidence=confidence,
                is_within_limit=is_within_limit
            )
            
        except Exception as e:
            logger.error(f"Pressure calculation error: {e}")
            return self._create_result_dict(
                status='ERROR',
                confidence=0.0,
                error=str(e)
            )
    
    def validate_stowage_plan(self, containers: List[Dict]) -> Dict:
        """
        적재 계획의 압력 한계 준수 검증
        
        Args:
            containers: 컨테이너 목록
            
        Returns:
            Dict: 전체 적재 계획 검증 결과
        """
        try:
            results = []
            total_containers = len(containers)
            compliant_containers = 0
            
            for container in containers:
                result = self.calculate_container_pressure(container)
                results.append(result)
                
                if result.get('is_within_limit', False):
                    compliant_containers += 1
            
            compliance_rate = compliant_containers / total_containers if total_containers > 0 else 0
            overall_confidence = min(self.HIGH_CONFIDENCE_THRESHOLD, compliance_rate * self.HIGH_CONFIDENCE_THRESHOLD)
            
            # 빈 리스트인 경우 SUCCESS, 그렇지 않으면 준수율에 따라 결정
            status = 'SUCCESS' if total_containers == 0 else ('SUCCESS' if compliance_rate >= self.COMPLIANCE_RATE_THRESHOLD else 'WARNING')
            
            return {
                'status': status,
                'total_containers': total_containers,
                'compliant_containers': compliant_containers,
                'compliance_rate': round(compliance_rate, 3),
                'confidence': round(overall_confidence, 3),
                'pressure_limit': self.pressure_limit,
                'results': results,
                'mode': self.mode,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Stowage plan validation error: {e}")
            return self._create_result_dict(
                status='ERROR',
                confidence=0.0,
                error=str(e)
            )


class TestHeatStowPressureLimit:
    """Heat-Stow 압력 한계 강제 테스트 클래스"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 설정"""
        self.analyzer = HeatStowAnalyzer(pressure_limit=4.0)
        
    def test_pressure_limit_enforcement_within_safe_range(self):
        """안전 범위 내 압력 계산 테스트"""
        # Given: 안전한 압력 범위의 컨테이너 데이터
        container_data = {
            'weight': 3.0,  # ton
            'area': 1.0,    # m²
            'container_id': 'CONT001'
        }
        
        # When: 압력 계산 실행
        result = self.analyzer.calculate_container_pressure(container_data)
        
        # Then: 압력이 한계 내에 있고 신뢰도가 높아야 함
        assert result['status'] == 'SUCCESS'
        assert result['pressure'] == 3.0
        assert result['is_within_limit'] == True
        assert result['confidence'] >= 0.95
        assert result['pressure_limit'] == 4.0
        assert result['mode'] == 'LATTICE'
        
    def test_pressure_limit_enforcement_at_boundary(self):
        """경계값에서의 압력 한계 테스트"""
        # Given: 정확히 한계값인 압력
        container_data = {
            'weight': 4.0,  # ton
            'area': 1.0,    # m²
            'container_id': 'CONT002'
        }
        
        # When: 압력 계산 실행
        result = self.analyzer.calculate_container_pressure(container_data)
        
        # Then: 경계값에서도 허용되어야 함
        assert result['status'] == 'SUCCESS'
        assert result['pressure'] == 4.0
        assert result['is_within_limit'] == True
        assert result['confidence'] >= 0.95
        
    def test_pressure_limit_enforcement_exceeds_limit(self):
        """한계 초과 압력 테스트"""
        # Given: 한계를 초과하는 압력
        container_data = {
            'weight': 5.0,  # ton
            'area': 1.0,    # m²
            'container_id': 'CONT003'
        }
        
        # When: 압력 계산 실행
        result = self.analyzer.calculate_container_pressure(container_data)
        
        # Then: 경고 상태가 되어야 함
        assert result['status'] == 'WARNING'
        assert result['pressure'] == 5.0
        assert result['is_within_limit'] == False
        assert result['confidence'] < 0.95
        
    def test_pressure_limit_enforcement_with_different_areas(self):
        """다양한 면적에서의 압력 계산 테스트"""
        # Given: 다양한 면적의 컨테이너들
        test_cases = [
            {'weight': 2.0, 'area': 0.5, 'expected_pressure': 4.0, 'should_pass': True},
            {'weight': 3.0, 'area': 0.8, 'expected_pressure': 3.75, 'should_pass': True},
            {'weight': 4.5, 'area': 1.0, 'expected_pressure': 4.5, 'should_pass': False},
        ]
        
        for case in test_cases:
            # When: 압력 계산 실행
            result = self.analyzer.calculate_container_pressure({
                'weight': case['weight'],
                'area': case['area'],
                'container_id': f'CONT_{case["weight"]}_{case["area"]}'
            })
            
            # Then: 예상된 결과와 일치해야 함
            assert result['pressure'] == case['expected_pressure']
            assert result['is_within_limit'] == case['should_pass']
            
    def test_pressure_limit_enforcement_invalid_data(self):
        """잘못된 데이터 처리 테스트"""
        # Given: 잘못된 데이터
        invalid_cases = [
            {'weight': 1.0, 'area': 0, 'expected_status': 'FAIL'},
            {'weight': -1.0, 'area': 1.0, 'expected_status': 'SUCCESS'},  # 음수 무게는 허용
            {'weight': 1.0, 'area': -1.0, 'expected_status': 'FAIL'},
        ]
        
        for case in invalid_cases:
            # When: 압력 계산 실행
            result = self.analyzer.calculate_container_pressure({
                'weight': case['weight'],
                'area': case['area'],
                'container_id': f'INVALID_{case["weight"]}_{case["area"]}'
            })
            
            # Then: 적절한 오류 처리
            assert result['status'] == case['expected_status']
            
    def test_stowage_plan_validation_all_compliant(self):
        """모든 컨테이너가 준수하는 적재 계획 테스트"""
        # Given: 모든 컨테이너가 압력 한계를 준수하는 계획
        containers = [
            {'weight': 2.0, 'area': 1.0, 'container_id': 'CONT001'},
            {'weight': 3.0, 'area': 1.0, 'container_id': 'CONT002'},
            {'weight': 3.5, 'area': 1.0, 'container_id': 'CONT003'},
        ]
        
        # When: 적재 계획 검증 실행
        result = self.analyzer.validate_stowage_plan(containers)
        
        # Then: 전체 계획이 성공 상태여야 함
        assert result['status'] == 'SUCCESS'
        assert result['total_containers'] == 3
        assert result['compliant_containers'] == 3
        assert result['compliance_rate'] == 1.0
        assert result['confidence'] >= 0.95
        
    def test_stowage_plan_validation_partial_compliance(self):
        """부분적 준수 적재 계획 테스트"""
        # Given: 일부 컨테이너가 한계를 초과하는 계획
        containers = [
            {'weight': 2.0, 'area': 1.0, 'container_id': 'CONT001'},  # 준수
            {'weight': 5.0, 'area': 1.0, 'container_id': 'CONT002'},  # 초과
            {'weight': 3.0, 'area': 1.0, 'container_id': 'CONT003'},  # 준수
        ]
        
        # When: 적재 계획 검증 실행
        result = self.analyzer.validate_stowage_plan(containers)
        
        # Then: 경고 상태가 되어야 함
        assert result['status'] == 'WARNING'
        assert result['total_containers'] == 3
        assert result['compliant_containers'] == 2
        assert abs(result['compliance_rate'] - 2/3) < 0.001  # 부동소수점 정밀도 허용
        assert result['confidence'] < 0.95
        
    def test_stowage_plan_validation_empty_list(self):
        """빈 컨테이너 목록 처리 테스트"""
        # Given: 빈 컨테이너 목록
        containers = []
        
        # When: 적재 계획 검증 실행
        result = self.analyzer.validate_stowage_plan(containers)
        
        # Then: 적절한 처리
        assert result['status'] == 'SUCCESS'
        assert result['total_containers'] == 0
        assert result['compliant_containers'] == 0
        assert result['compliance_rate'] == 0
        
    def test_pressure_limit_configuration(self):
        """압력 한계 설정 테스트"""
        # Given: 다른 압력 한계로 설정된 분석기
        custom_analyzer = HeatStowAnalyzer(pressure_limit=3.0)
        
        # When: 한계값에서 테스트
        result = custom_analyzer.calculate_container_pressure({
            'weight': 3.0,
            'area': 1.0,
            'container_id': 'CONT_CUSTOM'
        })
        
        # Then: 새로운 한계값이 적용되어야 함
        assert result['pressure_limit'] == 3.0
        assert result['is_within_limit'] == True
        
        # 한계 초과 테스트
        result_exceed = custom_analyzer.calculate_container_pressure({
            'weight': 4.0,
            'area': 1.0,
            'container_id': 'CONT_EXCEED'
        })
        
        assert result_exceed['is_within_limit'] == False


if __name__ == "__main__":
    # 테스트 실행
    pytest.main([__file__, "-v"]) 