#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TDD Test for Status_Location_Date Analysis
SIMENSE & HITACHI raw data av1 컬럼 분석

Following Kent Beck's TDD principles: Red → Green → Refactor
"""

import unittest
import pandas as pd
from pathlib import Path
import numpy as np
from datetime import datetime, timedelta

class TestStatusLocationDateAnalysis(unittest.TestCase):
    """
    TDD Test Class for Status_Location_Date Analysis
    SIMENSE & HITACHI raw data av1 컬럼 분석
    """
    
    def setUp(self):
        """테스트 환경 설정"""
        self.data_dir = Path("hvdc_macho_gpt/WAREHOUSE/data")
        self.simense_file = self.data_dir / "HVDC WAREHOUSE_SIMENSE(SIM).xlsx"
        self.hitachi_file = self.data_dir / "HVDC WAREHOUSE_HITACHI(HE).xlsx"
        
    def test_raw_data_files_exist(self):
        """
        [RED] Phase 1-1: Raw Data Files Existence Test
        
        Given: SIMENSE와 HITACHI raw data 파일들
        When: 파일 존재 여부 확인
        Then: 두 파일 모두 존재해야 함
        """
        self.assertTrue(self.simense_file.exists(), "SIMENSE 파일이 존재하지 않습니다")
        self.assertTrue(self.hitachi_file.exists(), "HITACHI 파일이 존재하지 않습니다")
        
    def test_av1_column_exists_in_raw_data(self):
        """
        [GREEN] Phase 1-2: av1 Column Existence Test
        
        Given: SIMENSE & HITACHI raw data 파일들
        When: av1 컬럼 존재 여부 확인
        Then: 두 파일 모두 av1(Status_Location_Date) 컬럼이 있어야 함
        """
        from status_location_analyzer import load_raw_data_with_av1
        
        simense_data = load_raw_data_with_av1(self.simense_file)
        hitachi_data = load_raw_data_with_av1(self.hitachi_file)
        
        # av1 컬럼 존재 확인
        self.assertIn('av1', simense_data.columns, "SIMENSE 데이터에 av1 컬럼이 없습니다")
        self.assertIn('av1', hitachi_data.columns, "HITACHI 데이터에 av1 컬럼이 없습니다")
            
    def test_status_location_date_format_validation(self):
        """
        [GREEN] Phase 1-3: Status_Location_Date Format Validation Test
        
        Given: av1 컬럼에 Status_Location_Date 데이터
        When: 날짜 형식 검증 실행
        Then: 유효한 날짜 형식이어야 함
        """
        from status_location_analyzer import validate_status_location_dates
        
        validation_result = validate_status_location_dates(
            simense_file=self.simense_file,
            hitachi_file=self.hitachi_file
        )
        
        # 날짜 형식 검증
        self.assertIsInstance(validation_result, dict)
        self.assertIn('simense_valid_dates', validation_result)
        self.assertIn('hitachi_valid_dates', validation_result)
        self.assertIn('date_format_errors', validation_result)
        
        # 90% 이상의 데이터가 유효한 날짜여야 함
        simense_validity = validation_result['simense_valid_dates']
        hitachi_validity = validation_result['hitachi_valid_dates']
        
        self.assertGreaterEqual(simense_validity, 0.90, "SIMENSE 날짜 유효성이 90% 미만입니다")
        self.assertGreaterEqual(hitachi_validity, 0.90, "HITACHI 날짜 유효성이 90% 미만입니다")
    
    def test_final_arrival_date_analysis(self):
        """
        [GREEN] Phase 1-4: Final Arrival Date Analysis Test
        
        Given: Status_Location_Date 데이터
        When: 최종 도착 날짜 분석 실행
        Then: 자재별 최종 도착 위치와 날짜가 분석되어야 함
        """
        from status_location_analyzer import analyze_final_arrival_dates
        
        analysis_result = analyze_final_arrival_dates(
            simense_file=self.simense_file,
            hitachi_file=self.hitachi_file
        )
        
        # 분석 결과 구조 검증
        self.assertIn('simense_analysis', analysis_result)
        self.assertIn('hitachi_analysis', analysis_result)
        self.assertIn('combined_summary', analysis_result)
        
        # 필수 분석 항목 확인
        simense_analysis = analysis_result['simense_analysis']
        self.assertIn('total_materials', simense_analysis)
        self.assertIn('final_locations', simense_analysis)
        self.assertIn('date_range', simense_analysis)
        self.assertIn('arrival_patterns', simense_analysis)
    
    def test_location_timeline_tracking(self):
        """
        [GREEN] Phase 1-5: Location Timeline Tracking Test
        
        Given: 자재별 Status_Location_Date 기록들
        When: 위치 이동 타임라인 추적
        Then: 자재의 이동 경로와 각 위치별 체류 시간이 추적되어야 함
        """
        from status_location_analyzer import track_location_timeline
        
        timeline_result = track_location_timeline(
            simense_file=self.simense_file,
            hitachi_file=self.hitachi_file
        )
        
        # 타임라인 추적 결과 검증
        self.assertIsInstance(timeline_result, dict)
        self.assertIn('material_timelines', timeline_result)
        self.assertIn('location_statistics', timeline_result)
        self.assertIn('flow_patterns', timeline_result)
        
        # 각 자재별 타임라인 검증
        material_timelines = timeline_result['material_timelines']
        self.assertIsInstance(material_timelines, dict)
        
        # 첫 번째 자재의 타임라인 구조 확인
        if material_timelines:
            first_material = list(material_timelines.keys())[0]
            material_data = material_timelines[first_material]
            
            self.assertIn('locations', material_data)
            self.assertIn('dates', material_data)
            self.assertIn('duration_per_location', material_data)
            self.assertIn('total_journey_time', material_data)
    
    def test_status_location_integration_with_flow_code(self):
        """
        [GREEN] Phase 1-6: Status_Location Integration with Flow Code Test
        
        Given: Status_Location_Date와 기존 Flow Code 시스템
        When: 두 시스템 통합 분석 실행
        Then: Flow Code와 실제 도착 날짜가 일치하는지 검증되어야 함
        """
        from status_location_analyzer import integrate_with_flow_code
        
        integration_result = integrate_with_flow_code(
            simense_file=self.simense_file,
            hitachi_file=self.hitachi_file
        )
        
        # 통합 분석 결과 검증
        self.assertIn('flow_code_accuracy', integration_result)
        self.assertIn('date_consistency_check', integration_result)
        self.assertIn('location_mismatch_report', integration_result)
        
        # Flow Code 정확도가 90% 이상이어야 함 (실제 데이터 기반)
        flow_accuracy = integration_result['flow_code_accuracy']
        self.assertGreaterEqual(flow_accuracy, 0.90, "Flow Code 정확도가 90% 미만입니다")
        
        # 날짜 일관성 검증
        date_consistency = integration_result['date_consistency_check']
        self.assertGreaterEqual(date_consistency, 0.90, "날짜 일관성이 90% 미만입니다")

if __name__ == '__main__':
    print("🧪 [TDD] Status_Location_Date Analysis Tests")
    print("📋 Phase 2: Raw Data Analysis Tests (Green Phase)")
    print("=" * 60)
    
    # TDD Green Phase: 모든 테스트가 통과해야 함
    unittest.main(verbosity=2) 