"""
Heat-Stow Optimization Algorithm Tests
MACHO-GPT TDD Phase 3: Heat-Stow Analysis Module

Tests stowage optimization algorithm for container placement
and thermal distribution calculations.
"""

import pytest
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json
import logging
from dataclasses import dataclass

# Configure logging for MACHO-GPT
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Container:
    """컨테이너 데이터 클래스"""
    container_id: str
    weight: float  # ton
    length: float  # m
    width: float   # m
    height: float  # m
    temperature: float  # °C
    heat_sensitive: bool = False
    priority: int = 1  # 1=높음, 2=보통, 3=낮음

@dataclass(frozen=True)
class StowagePosition:
    """적재 위치 데이터 클래스"""
    x: int  # 열 위치
    y: int  # 행 위치
    z: int  # 층 위치
    available: bool = True
    max_weight: float = 4.0  # t/m²

class HeatStowOptimizer:
    """Heat-Stow 적재 최적화 알고리즘 클래스"""
    
    # 최적화 상수
    MAX_PRESSURE = 4.0  # t/m²
    TEMPERATURE_VARIANCE_THRESHOLD = 5.0  # °C
    HEAT_SENSITIVE_PRIORITY_BONUS = 2
    OPTIMIZATION_ITERATIONS = 100
    
    def __init__(self, warehouse_dimensions: Tuple[int, int, int] = (10, 10, 3)):
        """
        Heat-Stow 최적화기 초기화
        
        Args:
            warehouse_dimensions: 창고 크기 (가로, 세로, 높이)
        """
        self.width, self.length, self.height = warehouse_dimensions
        self.mode = "LATTICE"
        self.confidence_threshold = 0.95
        
        # 적재 위치 초기화
        self.positions = self._initialize_positions()
        
    def _initialize_positions(self) -> Dict[Tuple[int, int, int], StowagePosition]:
        """적재 위치 초기화"""
        positions = {}
        for x in range(self.width):
            for y in range(self.length):
                for z in range(self.height):
                    positions[(x, y, z)] = StowagePosition(x, y, z)
        return positions
    
    def calculate_container_area(self, container: Container) -> float:
        """컨테이너 면적 계산"""
        return container.length * container.width
    
    def calculate_pressure(self, container: Container, position: StowagePosition) -> float:
        """특정 위치에서의 압력 계산"""
        area = self.calculate_container_area(container)
        return container.weight / area if area > 0 else 0
    
    def is_position_valid(self, container: Container, position: StowagePosition) -> bool:
        """위치 유효성 검증"""
        if not position.available:
            return False
            
        pressure = self.calculate_pressure(container, position)
        return pressure <= self.MAX_PRESSURE
    
    def calculate_thermal_distribution(self, containers: List[Container], 
                                     positions: Dict[str, StowagePosition]) -> Dict:
        """열 분포 계산"""
        try:
            if not containers:
                return {
                    'status': 'SUCCESS',
                    'thermal_variance': 0.0,
                    'max_temperature': 0.0,
                    'min_temperature': 0.0,
                    'average_temperature': 0.0,
                    'confidence': 0.95,
                    'mode': self.mode
                }
            
            temperatures = [container.temperature for container in containers]
            max_temp = max(temperatures)
            min_temp = min(temperatures)
            avg_temp = sum(temperatures) / len(temperatures)
            
            # 온도 분산 계산
            variance = sum((t - avg_temp) ** 2 for t in temperatures) / len(temperatures)
            thermal_variance = variance ** 0.5  # 표준편차
            
            # 열 분포 품질 평가
            is_optimal = thermal_variance <= self.TEMPERATURE_VARIANCE_THRESHOLD
            confidence = 0.95 if is_optimal else 0.85
            
            return {
                'status': 'SUCCESS' if is_optimal else 'WARNING',
                'thermal_variance': round(thermal_variance, 2),
                'max_temperature': round(max_temp, 1),
                'min_temperature': round(min_temp, 1),
                'average_temperature': round(avg_temp, 1),
                'is_optimal': is_optimal,
                'confidence': confidence,
                'mode': self.mode,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Thermal distribution calculation error: {e}")
            return {
                'status': 'ERROR',
                'confidence': 0.0,
                'error': str(e),
                'mode': self.mode
            }
    
    def optimize_stowage(self, containers: List[Container]) -> Dict:
        """적재 최적화 알고리즘 실행"""
        try:
            if not containers:
                return {
                    'status': 'SUCCESS',
                    'optimized_containers': 0,
                    'total_containers': 0,
                    'utilization_rate': 0.0,
                    'confidence': 0.95,
                    'mode': self.mode
                }
            
            # 컨테이너를 우선순위와 열 민감도에 따라 정렬
            sorted_containers = self._sort_containers_by_priority(containers)
            
            # 적재 계획 생성
            stowage_plan = {}
            optimized_count = 0
            
            for container in sorted_containers:
                best_position = self._find_best_position(container)
                if best_position:
                    stowage_plan[container.container_id] = best_position
                    # 위치를 사용 불가로 표시
                    pos_key = (best_position.x, best_position.y, best_position.z)
                    if pos_key in self.positions:
                        # frozen dataclass이므로 새로운 인스턴스 생성
                        old_pos = self.positions[pos_key]
                        self.positions[pos_key] = StowagePosition(
                            old_pos.x, old_pos.y, old_pos.z, 
                            available=False, max_weight=old_pos.max_weight
                        )
                    optimized_count += 1
            
            # 최적화 결과 평가
            utilization_rate = optimized_count / len(containers)
            is_successful = utilization_rate >= 0.90
            confidence = 0.95 if is_successful else 0.85
            
            return {
                'status': 'SUCCESS' if is_successful else 'WARNING',
                'optimized_containers': optimized_count,
                'total_containers': len(containers),
                'utilization_rate': round(utilization_rate, 3),
                'stowage_plan': stowage_plan,
                'confidence': confidence,
                'mode': self.mode,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Stowage optimization error: {e}")
            return {
                'status': 'ERROR',
                'confidence': 0.0,
                'error': str(e),
                'mode': self.mode
            }
    
    def _sort_containers_by_priority(self, containers: List[Container]) -> List[Container]:
        """컨테이너를 우선순위에 따라 정렬"""
        def priority_key(container):
            # 열 민감도가 높은 컨테이너에 보너스 점수
            priority_score = container.priority
            if container.heat_sensitive:
                priority_score -= self.HEAT_SENSITIVE_PRIORITY_BONUS
            return priority_score
        
        return sorted(containers, key=priority_key)
    
    def _find_best_position(self, container: Container) -> Optional[StowagePosition]:
        """최적 위치 찾기"""
        valid_positions = []
        
        for pos_key, pos in self.positions.items():
            if self.is_position_valid(container, pos):
                # 위치 품질 점수 계산 (중앙에 가까울수록 높은 점수)
                center_x, center_y = self.width // 2, self.length // 2
                distance_from_center = ((pos.x - center_x) ** 2 + (pos.y - center_y) ** 2) ** 0.5
                quality_score = 1.0 / (1.0 + distance_from_center)
                
                valid_positions.append((pos_key, pos, quality_score))
        
        if not valid_positions:
            return None
        
        # 가장 높은 품질 점수의 위치 반환
        best_key, best_position, _ = max(valid_positions, key=lambda x: x[2])
        return best_position


class TestHeatStowOptimization:
    """Heat-Stow 적재 최적화 테스트 클래스"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 설정"""
        self.optimizer = HeatStowOptimizer(warehouse_dimensions=(5, 5, 2))
        
    def test_stowage_optimization_algorithm_basic_placement(self):
        """기본 적재 최적화 테스트"""
        # Given: 기본 컨테이너들
        containers = [
            Container('CONT001', weight=2.0, length=6.0, width=2.4, height=2.6, temperature=25.0),
            Container('CONT002', weight=3.0, length=6.0, width=2.4, height=2.6, temperature=30.0),
            Container('CONT003', weight=1.5, length=6.0, width=2.4, height=2.6, temperature=20.0),
        ]
        
        # When: 적재 최적화 실행
        result = self.optimizer.optimize_stowage(containers)
        
        # Then: 성공적으로 최적화되어야 함
        assert result['status'] == 'SUCCESS'
        assert result['optimized_containers'] == 3
        assert result['total_containers'] == 3
        assert result['utilization_rate'] == 1.0
        assert result['confidence'] >= 0.95
        assert len(result['stowage_plan']) == 3
        
    def test_stowage_optimization_algorithm_priority_sorting(self):
        """우선순위 기반 정렬 테스트"""
        # Given: 다양한 우선순위의 컨테이너들
        containers = [
            Container('CONT001', weight=2.0, length=6.0, width=2.4, height=2.6, 
                     temperature=25.0, priority=3),  # 낮은 우선순위
            Container('CONT002', weight=3.0, length=6.0, width=2.4, height=2.6, 
                     temperature=30.0, priority=1, heat_sensitive=True),  # 높은 우선순위 + 열 민감
            Container('CONT003', weight=1.5, length=6.0, width=2.4, height=2.6, 
                     temperature=20.0, priority=2),  # 보통 우선순위
        ]
        
        # When: 우선순위 정렬 실행
        sorted_containers = self.optimizer._sort_containers_by_priority(containers)
        
        # Then: 열 민감도가 높은 컨테이너가 먼저 와야 함
        assert sorted_containers[0].container_id == 'CONT002'  # 열 민감도 높음
        assert sorted_containers[0].heat_sensitive == True
        
    def test_stowage_optimization_algorithm_position_validation(self):
        """위치 유효성 검증 테스트"""
        # Given: 다양한 컨테이너와 위치
        # 무게 60 ton, 면적 6.0 × 2.4 = 14.4 m² → 압력 = 60/14.4 ≈ 4.17 t/m² (한계 초과)
        heavy_container = Container('CONT001', weight=60.0, length=6.0, width=2.4, height=2.6, temperature=25.0)
        position = StowagePosition(0, 0, 0, available=True, max_weight=4.0)
        
        # When: 위치 유효성 검증
        is_valid = self.optimizer.is_position_valid(heavy_container, position)
        
        # Then: 압력 한계를 초과하므로 유효하지 않아야 함
        assert is_valid == False
        
        # 압력 한계 내의 컨테이너 테스트
        light_container = Container('CONT002', weight=2.0, length=6.0, width=2.4, height=2.6, temperature=25.0)
        is_valid_light = self.optimizer.is_position_valid(light_container, position)
        assert is_valid_light == True
        
    def test_stowage_optimization_algorithm_thermal_distribution(self):
        """열 분포 계산 테스트"""
        # Given: 다양한 온도의 컨테이너들
        containers = [
            Container('CONT001', weight=2.0, length=6.0, width=2.4, height=2.6, temperature=20.0),
            Container('CONT002', weight=3.0, length=6.0, width=2.4, height=2.6, temperature=25.0),
            Container('CONT003', weight=1.5, length=6.0, width=2.4, height=2.6, temperature=30.0),
        ]
        positions = {'CONT001': StowagePosition(0, 0, 0), 'CONT002': StowagePosition(1, 1, 0)}
        
        # When: 열 분포 계산
        result = self.optimizer.calculate_thermal_distribution(containers, positions)
        
        # Then: 열 분포 정보가 정확히 계산되어야 함
        assert result['status'] == 'SUCCESS'
        assert result['max_temperature'] == 30.0
        assert result['min_temperature'] == 20.0
        assert result['average_temperature'] == 25.0
        assert result['thermal_variance'] > 0
        assert result['confidence'] >= 0.95
        
    def test_stowage_optimization_algorithm_thermal_variance_threshold(self):
        """열 분산 임계값 테스트"""
        # Given: 높은 온도 분산을 가진 컨테이너들
        containers = [
            Container('CONT001', weight=2.0, length=6.0, width=2.4, height=2.6, temperature=15.0),
            Container('CONT002', weight=3.0, length=6.0, width=2.4, height=2.6, temperature=35.0),  # 큰 온도 차이
        ]
        positions = {'CONT001': StowagePosition(0, 0, 0), 'CONT002': StowagePosition(1, 1, 0)}
        
        # When: 열 분포 계산
        result = self.optimizer.calculate_thermal_distribution(containers, positions)
        
        # Then: 높은 온도 분산으로 인해 경고 상태가 되어야 함
        assert result['status'] == 'WARNING'
        assert result['thermal_variance'] > self.optimizer.TEMPERATURE_VARIANCE_THRESHOLD
        assert result['confidence'] < 0.95
        
    def test_stowage_optimization_algorithm_empty_containers(self):
        """빈 컨테이너 목록 처리 테스트"""
        # Given: 빈 컨테이너 목록
        containers = []
        
        # When: 적재 최적화 실행
        result = self.optimizer.optimize_stowage(containers)
        
        # Then: 적절한 처리
        assert result['status'] == 'SUCCESS'
        assert result['optimized_containers'] == 0
        assert result['total_containers'] == 0
        assert result['utilization_rate'] == 0.0
        assert result['confidence'] >= 0.95
        
    def test_stowage_optimization_algorithm_warehouse_capacity(self):
        """창고 용량 한계 테스트"""
        # Given: 창고 용량을 초과하는 많은 컨테이너들
        containers = []
        for i in range(100):  # 창고 용량(5x5x2=50)을 초과
            containers.append(Container(
                f'CONT{i:03d}', 
                weight=2.0, 
                length=6.0, 
                width=2.4, 
                height=2.6, 
                temperature=25.0
            ))
        
        # When: 적재 최적화 실행
        result = self.optimizer.optimize_stowage(containers)
        
        # Then: 일부만 최적화되고 경고 상태가 되어야 함
        assert result['status'] == 'WARNING'
        assert result['optimized_containers'] < len(containers)
        assert result['utilization_rate'] < 1.0
        assert result['confidence'] < 0.95
        
    def test_stowage_optimization_algorithm_position_quality_scoring(self):
        """위치 품질 점수 계산 테스트"""
        # Given: 컨테이너와 다양한 위치
        container = Container('CONT001', weight=2.0, length=6.0, width=2.4, height=2.6, temperature=25.0)
        
        # When: 최적 위치 찾기
        best_position = self.optimizer._find_best_position(container)
        
        # Then: 중앙에 가까운 위치가 선택되어야 함
        assert best_position is not None
        center_x, center_y = self.optimizer.width // 2, self.optimizer.length // 2
        distance_from_center = ((best_position.x - center_x) ** 2 + (best_position.y - center_y) ** 2) ** 0.5
        assert distance_from_center <= 2  # 중앙에서 2칸 이내


if __name__ == "__main__":
    # 테스트 실행
    pytest.main([__file__, "-v"]) 