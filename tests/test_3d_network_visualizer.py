#!/usr/bin/env python3
"""
Test-Driven Development for HVDC 3D Network Visualizer
TDD Cycle: Red → Green → Refactor
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from logi_3d_network_visualizer import LogiNetworkVisualizer, NetworkNodeType
import networkx as nx

class TestLogiNetworkVisualizer:
    """HVDC 3D Network Visualizer 테스트 클래스"""
    
    @pytest.fixture
    def visualizer(self):
        """테스트용 시각화 시스템 초기화"""
        return LogiNetworkVisualizer(mode="LATTICE")
    
    @pytest.fixture
    def sample_data(self):
        """테스트용 샘플 데이터"""
        return pd.DataFrame({
            'Item': [f'ITEM_{i:03d}' for i in range(1, 21)],
            'DSV Indoor': [datetime.now() - timedelta(days=np.random.randint(1, 100)) for _ in range(20)],
            'DSV Outdoor': [datetime.now() - timedelta(days=np.random.randint(1, 100)) for _ in range(20)],
            'DSV Al Markaz': [datetime.now() - timedelta(days=np.random.randint(1, 100)) for _ in range(20)],
            'MIR': [datetime.now() - timedelta(days=np.random.randint(1, 100)) for _ in range(20)],
            'SHU': [datetime.now() - timedelta(days=np.random.randint(1, 100)) for _ in range(20)],
            'Category': np.random.choice(['Electrical', 'Mechanical', 'Control'], 20)
        })
    
    def test_visualizer_initialization(self, visualizer):
        """시각화 시스템 초기화 테스트"""
        # Given: LogiNetworkVisualizer 인스턴스
        # When: 초기화 완료
        # Then: 기본 속성들이 올바르게 설정되어야 함
        
        assert visualizer.mode == "LATTICE"
        assert visualizer.confidence_threshold == 0.90
        assert isinstance(visualizer.G, nx.Graph)
        assert len(visualizer.hvdc_warehouses) > 0
        assert len(visualizer.hvdc_sites) > 0
        assert len(visualizer.node_colors) == len(NetworkNodeType)
    
    def test_network_node_type_enum(self):
        """네트워크 노드 타입 Enum 테스트"""
        # Given: NetworkNodeType Enum
        # When: 각 노드 타입 확인
        # Then: 올바른 값들이 정의되어야 함
        
        assert NetworkNodeType.WAREHOUSE.value == "warehouse"
        assert NetworkNodeType.SITE.value == "site"
        assert NetworkNodeType.PORT.value == "port"
        assert NetworkNodeType.SUPPLIER.value == "supplier"
        assert NetworkNodeType.CUSTOMER.value == "customer"
        assert NetworkNodeType.TRANSIT.value == "transit"
    
    def test_data_normalization(self, visualizer, sample_data):
        """데이터 정규화 테스트"""
        # Given: 샘플 데이터
        # When: 정규화 실행
        # Then: 데이터가 올바르게 정규화되어야 함
        
        normalized_data = visualizer._normalize_logistics_data(sample_data)
        
        assert len(normalized_data) == len(sample_data)
        assert not normalized_data.isnull().any().any()  # NaN이 없어야 함
        
        # 문자열 컬럼들이 정규화되었는지 확인
        for col in normalized_data.select_dtypes(include=['object']).columns:
            assert all(isinstance(val, str) for val in normalized_data[col])
    
    def test_network_graph_building(self, visualizer, sample_data):
        """네트워크 그래프 구성 테스트"""
        # Given: 정규화된 데이터
        # When: 네트워크 그래프 구성
        # Then: 노드와 엣지가 올바르게 생성되어야 함
        
        normalized_data = visualizer._normalize_logistics_data(sample_data)
        visualizer._build_network_graph(normalized_data)
        
        # 노드 존재 확인
        assert len(visualizer.G.nodes()) > 0
        
        # HVDC 창고 노드들이 존재하는지 확인
        for warehouse in visualizer.hvdc_warehouses:
            if warehouse in sample_data.columns:
                assert warehouse in visualizer.G.nodes()
        
        # HVDC 현장 노드들이 존재하는지 확인
        for site in visualizer.hvdc_sites:
            if site in sample_data.columns:
                assert site in visualizer.G.nodes()
        
        # 추가 노드들 확인
        additional_nodes = ['Jebel Ali Port', 'Abu Dhabi Port', 'Hitachi Supplier', 'Siemens Supplier', 'Samsung C&T']
        for node in additional_nodes:
            assert node in visualizer.G.nodes()
    
    def test_connection_strength_calculation(self, visualizer, sample_data):
        """연결 강도 계산 테스트"""
        # Given: 두 노드 간의 데이터
        # When: 연결 강도 계산
        # Then: 0.0과 1.0 사이의 값이 반환되어야 함
        
        strength = visualizer._calculate_connection_strength(sample_data, 'DSV Indoor', 'MIR')
        
        assert isinstance(strength, float)
        assert 0.0 <= strength <= 1.0
    
    def test_3d_layout_generation(self, visualizer, sample_data):
        """3D 레이아웃 생성 테스트"""
        # Given: 네트워크 그래프
        # When: 3D 레이아웃 생성
        # Then: 각 노드에 3D 좌표가 할당되어야 함
        
        normalized_data = visualizer._normalize_logistics_data(sample_data)
        visualizer._build_network_graph(normalized_data)
        visualizer._generate_3d_layout()
        
        assert len(visualizer.node_positions) > 0
        
        # 각 노드의 좌표가 3차원인지 확인
        for node, coords in visualizer.node_positions.items():
            assert len(coords) == 3
            assert all(isinstance(coord, (int, float)) for coord in coords)
    
    def test_3d_visualization_creation(self, visualizer, sample_data):
        """3D 시각화 생성 테스트"""
        # Given: 네트워크 그래프와 3D 레이아웃
        # When: 3D 시각화 생성
        # Then: Plotly Figure 객체가 생성되어야 함
        
        normalized_data = visualizer._normalize_logistics_data(sample_data)
        visualizer._build_network_graph(normalized_data)
        visualizer._generate_3d_layout()
        
        fig = visualizer.create_3d_network_visualization()
        
        assert fig is not None
        assert hasattr(fig, 'data')
        assert hasattr(fig, 'layout')
        assert len(fig.data) > 0
    
    def test_logistics_dashboard_creation(self, visualizer, sample_data):
        """물류 대시보드 생성 테스트"""
        # Given: 샘플 데이터
        # When: 대시보드 생성
        # Then: 멀티 패널 대시보드가 생성되어야 함
        
        fig = visualizer.create_logistics_dashboard(sample_data)
        
        assert fig is not None
        assert hasattr(fig, 'data')
        assert hasattr(fig, 'layout')
    
    def test_warehouse_stats_calculation(self, visualizer, sample_data):
        """창고별 통계 계산 테스트"""
        # Given: 샘플 데이터
        # When: 창고별 통계 계산
        # Then: 각 창고별 성과 지표가 계산되어야 함
        
        stats = visualizer._calculate_warehouse_stats(sample_data)
        
        assert isinstance(stats, dict)
        assert len(stats) > 0
        
        # 각 창고의 통계가 숫자인지 확인
        for warehouse, stat in stats.items():
            assert isinstance(stat, (int, float))
            assert stat >= 0
    
    def test_flow_timeline_creation(self, visualizer, sample_data):
        """플로우 타임라인 생성 테스트"""
        # Given: 샘플 데이터
        # When: 타임라인 생성
        # Then: 날짜와 플로우 데이터가 생성되어야 함
        
        timeline = visualizer._create_flow_timeline(sample_data)
        
        assert 'dates' in timeline
        assert 'flows' in timeline
        assert len(timeline['dates']) > 0
        assert len(timeline['flows']) > 0
        assert len(timeline['dates']) == len(timeline['flows'])
    
    def test_node_distribution_calculation(self, visualizer, sample_data):
        """노드 분포 계산 테스트"""
        # Given: 네트워크 그래프
        # When: 노드 분포 계산
        # Then: 노드 타입별 분포가 계산되어야 함
        
        normalized_data = visualizer._normalize_logistics_data(sample_data)
        visualizer._build_network_graph(normalized_data)
        
        distribution = visualizer._calculate_node_distribution()
        
        assert isinstance(distribution, dict)
        assert len(distribution) > 0
        
        # 각 노드 타입의 개수가 양수인지 확인
        for node_type, count in distribution.items():
            assert isinstance(count, int)
            assert count > 0
    
    def test_auto_triggers_check(self, visualizer, sample_data):
        """자동 트리거 확인 테스트"""
        # Given: 샘플 데이터
        # When: 자동 트리거 확인
        # Then: 적절한 트리거 목록이 반환되어야 함
        
        triggers = visualizer._check_auto_triggers(sample_data)
        
        assert isinstance(triggers, list)
        # 트리거가 명령어 형식인지 확인
        for trigger in triggers:
            assert trigger.startswith('/')
    
    def test_data_loading_with_dataframe(self, visualizer, sample_data):
        """DataFrame 데이터 로드 테스트"""
        # Given: DataFrame 형태의 데이터
        # When: 데이터 로드
        # Then: 성공적으로 로드되어야 함
        
        result = visualizer.load_logistics_data(sample_data)
        
        assert result['status'] == 'SUCCESS'
        assert result['confidence'] >= 0.90
        assert result['mode'] == 'LATTICE'
        assert 'nodes_count' in result
        assert 'edges_count' in result
        assert 'triggers' in result
        assert 'next_cmds' in result
    
    def test_data_loading_with_invalid_source(self, visualizer):
        """잘못된 데이터 소스 로드 테스트"""
        # Given: 잘못된 데이터 소스
        # When: 데이터 로드 시도
        # Then: 실패 결과가 반환되어야 함
        
        result = visualizer.load_logistics_data("invalid_file.xyz")
        
        assert result['status'] == 'FAIL'
        assert result['confidence'] == 0.0
        assert 'error' in result
        assert result['mode'] == 'LATTICE'
    
    def test_visualization_export_html(self, visualizer, sample_data, tmp_path):
        """HTML 형식 내보내기 테스트"""
        # Given: 3D 시각화
        # When: HTML 형식으로 내보내기
        # Then: HTML 파일이 생성되어야 함
        
        normalized_data = visualizer._normalize_logistics_data(sample_data)
        visualizer._build_network_graph(normalized_data)
        visualizer._generate_3d_layout()
        fig = visualizer.create_3d_network_visualization()
        
        # 임시 디렉토리에 내보내기
        export_path = tmp_path / "test_export.html"
        result = visualizer.export_visualization(fig, str(export_path), 'html')
        
        assert result['status'] == 'SUCCESS'
        assert result['format'] == 'html'
        assert export_path.exists()
    
    def test_network_graph_properties(self, visualizer, sample_data):
        """네트워크 그래프 속성 테스트"""
        # Given: 네트워크 그래프
        # When: 그래프 속성 확인
        # Then: 노드와 엣지 속성이 올바르게 설정되어야 함
        
        normalized_data = visualizer._normalize_logistics_data(sample_data)
        visualizer._build_network_graph(normalized_data)
        
        # 노드 속성 확인
        for node, attrs in visualizer.G.nodes(data=True):
            assert 'type' in attrs
            assert 'category' in attrs
            assert 'capacity' in attrs
            assert isinstance(attrs['type'], NetworkNodeType)
            assert isinstance(attrs['capacity'], (int, float))
        
        # 엣지 속성 확인
        for edge in visualizer.G.edges(data=True):
            # edge는 (node1, node2, attrs) 튜플
            node1, node2, attrs = edge
            assert 'weight' in attrs
            assert 'type' in attrs
            assert 'distance' in attrs
            assert 0.0 <= attrs['weight'] <= 1.0
            assert attrs['distance'] > 0
    
    def test_node_color_mapping(self, visualizer):
        """노드 색상 매핑 테스트"""
        # Given: 노드 타입별 색상 매핑
        # When: 색상 확인
        # Then: 각 노드 타입에 올바른 색상이 할당되어야 함
        
        colors = visualizer.node_colors
        
        assert NetworkNodeType.WAREHOUSE in colors
        assert NetworkNodeType.SITE in colors
        assert NetworkNodeType.PORT in colors
        assert NetworkNodeType.SUPPLIER in colors
        assert NetworkNodeType.CUSTOMER in colors
        assert NetworkNodeType.TRANSIT in colors
        
        # 색상이 유효한 hex 코드인지 확인
        for color in colors.values():
            assert color.startswith('#')
            assert len(color) == 7  # #RRGGBB 형식
    
    def test_hvdc_specific_configuration(self, visualizer):
        """HVDC 특화 설정 테스트"""
        # Given: HVDC 특화 설정
        # When: 설정 확인
        # Then: HVDC 프로젝트에 맞는 설정이 되어야 함
        
        # 창고 목록 확인
        expected_warehouses = [
            'DSV Indoor', 'DSV Outdoor', 'DSV Al Markaz', 
            'DSV MZP', 'AAA Storage', 'Hauler Indoor', 'MOSB', 'DHL Warehouse'
        ]
        
        for warehouse in expected_warehouses:
            assert warehouse in visualizer.hvdc_warehouses
        
        # 현장 목록 확인
        expected_sites = ['MIR', 'SHU', 'DAS', 'AGI']
        
        for site in expected_sites:
            assert site in visualizer.hvdc_sites

def test_integration_workflow():
    """통합 워크플로우 테스트"""
    """전체 시스템 통합 테스트"""
    # Given: 전체 시각화 시스템
    # When: 전체 워크플로우 실행
    # Then: 모든 단계가 성공적으로 완료되어야 함
    
    # 1. 시스템 초기화
    visualizer = LogiNetworkVisualizer(mode="LATTICE")
    
    # 2. 샘플 데이터 생성
    sample_data = pd.DataFrame({
        'Item': [f'ITEM_{i:03d}' for i in range(1, 11)],
        'DSV Indoor': [datetime.now() - timedelta(days=i) for i in range(1, 11)],
        'MIR': [datetime.now() - timedelta(days=i+5) for i in range(1, 11)],
        'Category': ['Electrical'] * 10
    })
    
    # 3. 데이터 로드
    load_result = visualizer.load_logistics_data(sample_data)
    assert load_result['status'] == 'SUCCESS'
    
    # 4. 3D 시각화 생성
    fig_3d = visualizer.create_3d_network_visualization()
    assert fig_3d is not None
    
    # 5. 대시보드 생성
    fig_dashboard = visualizer.create_logistics_dashboard(sample_data)
    assert fig_dashboard is not None
    
    # 6. 통계 계산
    stats = visualizer._calculate_warehouse_stats(sample_data)
    assert len(stats) > 0
    
    # 7. 타임라인 생성
    timeline = visualizer._create_flow_timeline(sample_data)
    assert len(timeline['dates']) > 0
    
    print("✅ 통합 워크플로우 테스트 통과")

if __name__ == "__main__":
    # 테스트 실행
    pytest.main([__file__, "-v"]) 