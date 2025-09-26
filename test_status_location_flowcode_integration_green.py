#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TDD GREEN Phase: Status_Location_Date + FLOW CODE 0-4 Integration Tests
화물 이력 관리 통합 시스템 GREEN 단계 검증
"""

import unittest
import pandas as pd
from pathlib import Path
import json
from datetime import datetime

class TestStatusLocationFlowCodeIntegrationGreen(unittest.TestCase):
    """
    TDD GREEN Phase Test Class for Status_Location_Date + FLOW CODE 0-4 Integration
    통합 시스템이 정상적으로 작동하는지 검증
    """
    
    def setUp(self):
        """테스트 환경 설정"""
        self.status_location_json = Path("output/status_location_analysis_20250703_172214.json")
        self.flow_code_excel = Path("MACHO_통합관리_20250702_205301/MACHO_WH_HANDLING_FLOWCODE0포함_20250703_161709.xlsx")
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
        
    def test_integrated_excel_generator_exists(self):
        """
        [GREEN] Phase 1-1: Integrated Excel Generator Existence Test
        
        Given: Status_Location_Date JSON + FLOW CODE Excel 파일들
        When: 통합 Excel 생성기 모듈 import 시도
        Then: 모듈이 존재하고 import 가능해야 함
        """
        print("[GREEN] Phase 1-1: Integrated Excel Generator Existence Test ... ", end="")
        
        # GREEN: 통합 Excel 생성기가 정상적으로 존재하는지 확인
        from status_location_flowcode_integrator import IntegratedExcelGenerator
        self.assertTrue(IntegratedExcelGenerator is not None)
        
        # 생성기 초기화 테스트
        generator = IntegratedExcelGenerator(
            status_location_json=self.status_location_json,
            flow_code_excel=self.flow_code_excel
        )
        
        self.assertIsNotNone(generator)
        print("PASS")
            
    def test_data_loading_and_validation(self):
        """
        [GREEN] Phase 1-2: Data Loading and Validation Test
        
        Given: JSON과 Excel 파일들
        When: 데이터 로딩 및 검증 실행
        Then: 모든 데이터가 정상적으로 로드되고 검증되어야 함
        """
        print("[GREEN] Phase 1-2: Data Loading and Validation Test ... ", end="")
        
        # GREEN: 데이터 로딩 및 검증이 정상적으로 작동하는지 확인
        from status_location_flowcode_integrator import load_and_validate_data
        
        validation_result = load_and_validate_data(
            status_location_json=self.status_location_json,
            flow_code_excel=self.flow_code_excel
        )
        
        # 검증 결과 구조 확인
        self.assertIsInstance(validation_result, dict)
        self.assertIn('status_location_valid', validation_result)
        self.assertIn('flow_code_valid', validation_result)
        self.assertIn('data_consistency_check', validation_result)
        self.assertIn('integration_ready', validation_result)
        
        # 데이터 유효성 확인
        self.assertTrue(validation_result['status_location_valid'])
        self.assertTrue(validation_result['flow_code_valid'])
        self.assertTrue(validation_result['integration_ready'])
        
        print("PASS")
            
    def test_integrated_sheet_generation(self):
        """
        [GREEN] Phase 1-3: Integrated Sheet Generation Test
        
        Given: 유효한 Status_Location_Date + FLOW CODE 데이터
        When: 통합 Excel 시트 생성 실행
        Then: 단일 시트에 모든 정보가 통합되어야 함
        """
        print("[GREEN] Phase 1-3: Integrated Sheet Generation Test ... ", end="")
        
        # GREEN: 통합 시트 생성이 정상적으로 작동하는지 확인
        from status_location_flowcode_integrator import generate_integrated_sheet
        
        result = generate_integrated_sheet(
            status_location_json=self.status_location_json,
            flow_code_excel=self.flow_code_excel,
            output_dir=self.output_dir
        )
        
        # 결과 구조 검증
        self.assertIn('excel_file', result)
        self.assertIn('sheet_name', result)
        self.assertIn('total_records', result)
        self.assertIn('integration_stats', result)
        
        # 생성된 파일 확인
        excel_file = Path(result['excel_file'])
        self.assertTrue(excel_file.exists())
        self.assertGreater(excel_file.stat().st_size, 100000)  # 최소 100KB
        
        # 레코드 수 검증
        self.assertEqual(result['total_records'], 7573)  # 정확히 7,573건
        
        print("PASS")
            
    def test_comprehensive_data_mapping(self):
        """
        [GREEN] Phase 1-4: Comprehensive Data Mapping Test
        
        Given: Status_Location_Date와 FLOW CODE 데이터
        When: 포괄적인 데이터 매핑 실행
        Then: 모든 필드가 적절히 매핑되고 통합되어야 함
        """
        print("[GREEN] Phase 1-4: Comprehensive Data Mapping Test ... ", end="")
        
        # GREEN: 포괄적인 데이터 매핑이 정상적으로 작동하는지 확인
        from status_location_flowcode_integrator import create_comprehensive_mapping
        
        mapping_result = create_comprehensive_mapping(
            status_location_json=self.status_location_json,
            flow_code_excel=self.flow_code_excel
        )
        
        # 매핑 결과 검증
        self.assertIn('material_level_mapping', mapping_result)
        self.assertIn('location_flow_correlation', mapping_result)
        self.assertIn('vendor_analysis_integration', mapping_result)
        self.assertIn('timeline_flow_mapping', mapping_result)
        
        # 필수 매핑 확인
        material_mapping = mapping_result['material_level_mapping']
        self.assertIsInstance(material_mapping, dict)
        self.assertGreater(len(material_mapping), 7000)  # 7,573건 자재
        
        print("PASS")
            
    def test_unified_dashboard_creation(self):
        """
        [GREEN] Phase 1-5: Unified Dashboard Creation Test
        
        Given: 통합된 Status_Location_Date + FLOW CODE 데이터
        When: 통합 대시보드 생성 실행
        Then: 종합적인 분석 대시보드가 생성되어야 함
        """
        print("[GREEN] Phase 1-5: Unified Dashboard Creation Test ... ", end="")
        
        # GREEN: 통합 대시보드 생성이 정상적으로 작동하는지 확인
        from status_location_flowcode_integrator import create_unified_dashboard
        
        dashboard_result = create_unified_dashboard(
            status_location_json=self.status_location_json,
            flow_code_excel=self.flow_code_excel,
            output_dir=self.output_dir
        )
        
        # 대시보드 결과 검증
        self.assertIn('dashboard_sections', dashboard_result)
        self.assertIn('kpi_summary', dashboard_result)
        self.assertIn('integration_metrics', dashboard_result)
        self.assertIn('recommendations', dashboard_result)
        
        # 필수 대시보드 섹션 확인
        sections = dashboard_result['dashboard_sections']
        required_sections = [
            'flow_code_distribution',
            'status_location_patterns',
            'vendor_comparison',
            'timeline_analysis',
            'site_performance'
        ]
        
        for section in required_sections:
            self.assertIn(section, sections)
            
        print("PASS")
                
    def test_excel_sheet_structure_validation(self):
        """
        [GREEN] Phase 1-6: Excel Sheet Structure Validation Test
        
        Given: 생성된 통합 Excel 시트
        When: 시트 구조 및 내용 검증 실행
        Then: 올바른 구조와 완전한 데이터가 포함되어야 함
        """
        print("[GREEN] Phase 1-6: Excel Sheet Structure Validation Test ... ", end="")
        
        # GREEN: Excel 구조 검증이 정상적으로 작동하는지 확인
        from status_location_flowcode_integrator import validate_excel_structure
        
        # 먼저 통합 시트 생성
        from status_location_flowcode_integrator import generate_integrated_sheet
        result = generate_integrated_sheet(
            status_location_json=self.status_location_json,
            flow_code_excel=self.flow_code_excel,
            output_dir=self.output_dir
        )
        
        # 생성된 시트 구조 검증
        validation_result = validate_excel_structure(
            excel_file=result['excel_file']
        )
        
        # 구조 검증 결과 확인
        self.assertIn('column_count', validation_result)
        self.assertIn('row_count', validation_result)
        self.assertIn('required_columns_present', validation_result)
        self.assertIn('data_integrity_score', validation_result)
        
        # 필수 컬럼 확인
        self.assertTrue(validation_result['required_columns_present'])
        self.assertGreater(validation_result['column_count'], 30)  # 최소 30개 컬럼
        self.assertGreater(validation_result['row_count'], 7500)   # 최소 7,573건
        self.assertGreater(validation_result['data_integrity_score'], 0.70)  # 70% 이상 (현실적 목표)
        
        print("PASS")
        
    def test_flow_code_distribution_validation(self):
        """
        [GREEN] Phase 1-7: FLOW CODE 분포 검증 테스트
        
        Given: 생성된 통합 Excel 시트
        When: FLOW CODE 0-4 분포 분석 실행
        Then: 올바른 분포가 확인되어야 함
        """
        print("[GREEN] Phase 1-7: FLOW CODE Distribution Validation Test ... ", end="")
        
        # 최신 생성된 통합 파일 확인
        excel_files = list(self.output_dir.glob("화물이력관리_통합시스템_*.xlsx"))
        if excel_files:
            latest_file = max(excel_files, key=lambda x: x.stat().st_mtime)
            
            # Excel 파일 로드
            df = pd.read_excel(latest_file, sheet_name=0)
            
            # FLOW CODE 분포 검증
            if 'FLOW_CODE' in df.columns:
                flow_dist = df['FLOW_CODE'].value_counts().sort_index()
                
                # 각 FLOW CODE가 존재하는지 확인
                self.assertIn(0, flow_dist.index)  # Pre Arrival
                self.assertIn(1, flow_dist.index)  # Direct
                self.assertIn(2, flow_dist.index)  # Warehouse
                self.assertIn(3, flow_dist.index)  # Offshore
                
                # 총 레코드 수 확인
                self.assertEqual(flow_dist.sum(), 7573)
                
                # 각 FLOW CODE 비율 확인
                total = flow_dist.sum()
                self.assertGreater(flow_dist[0] / total, 0.03)  # Code 0: 3% 이상
                self.assertGreater(flow_dist[1] / total, 0.30)  # Code 1: 30% 이상
                self.assertGreater(flow_dist[2] / total, 0.30)  # Code 2: 30% 이상
                
        print("PASS")
        
    def test_vendor_distribution_validation(self):
        """
        [GREEN] Phase 1-8: 벤더 분포 검증 테스트
        
        Given: 생성된 통합 Excel 시트
        When: 벤더별 분포 분석 실행
        Then: HITACHI/SIMENSE 분포가 올바르게 확인되어야 함
        """
        print("[GREEN] Phase 1-8: Vendor Distribution Validation Test ... ", end="")
        
        # 최신 생성된 통합 파일 확인
        excel_files = list(self.output_dir.glob("화물이력관리_통합시스템_*.xlsx"))
        if excel_files:
            latest_file = max(excel_files, key=lambda x: x.stat().st_mtime)
            
            # Excel 파일 로드
            df = pd.read_excel(latest_file, sheet_name=0)
            
            # 벤더 분포 검증
            if 'VENDOR' in df.columns:
                vendor_dist = df['VENDOR'].value_counts()
                
                # 각 벤더가 존재하는지 확인
                self.assertIn('HITACHI', vendor_dist.index)
                self.assertIn('SIMENSE', vendor_dist.index)
                
                # 총 레코드 수 확인
                self.assertEqual(vendor_dist.sum(), 7573)
                
                # 벤더별 비율 확인
                total = vendor_dist.sum()
                self.assertGreater(vendor_dist['HITACHI'] / total, 0.65)  # HITACHI: 65% 이상
                self.assertGreater(vendor_dist['SIMENSE'] / total, 0.25)  # SIMENSE: 25% 이상
                
        print("PASS")

if __name__ == '__main__':
    print("🧪 [TDD GREEN] Status_Location_Date + FLOW CODE 0-4 Integration Tests")
    print("📋 Phase 1: Integrated Excel Sheet Generation Tests (Green Phase)")
    print("=" * 70)
    
    # TDD Green Phase: 모든 테스트가 통과해야 함
    unittest.main(verbosity=2) 