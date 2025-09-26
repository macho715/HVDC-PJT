#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TDD Test for Final Report Style System
MACHO-GPT v3.4-mini 최종 보고서 스타일 구현

Phase 1: Core Infrastructure Tests (수정된 Green 단계)
Following Kent Beck's TDD principles: Red → Green → Refactor
"""

import unittest
import os
import pandas as pd
from pathlib import Path
import json
from datetime import datetime

class TestFinalReportStyleSystem(unittest.TestCase):
    """
    TDD Test Class for Final Report Generation System
    Based on attached README.md style and Excel structure
    """
    
    def setUp(self):
        """테스트 환경 설정"""
        self.test_data_dir = Path("test_data")
        self.output_dir = Path("output")
        self.test_data_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        
        # 테스트용 샘플 데이터
        self.sample_transaction_data = {
            'vendor': ['HITACHI', 'SIMENSE'] * 50,
            'location': ['DSV Indoor', 'DSV Outdoor', 'DSV Al Markaz'] * 34,
            'flow_code': [1, 2, 3, 0] * 25,
            'wh_handling': [0, 1, 2] * 34,
            'month': ['2024-01', '2024-02', '2024-03'] * 34,
            'quantity': [10, 20, 15] * 34,
            'status': ['Active', 'Complete'] * 50
        }
    
    def test_meta_system_initialization(self):
        """
        [GREEN] Phase 1-1: Meta System Initialization Test
        
        Given: MACHO-GPT 시스템 초기화 요구
        When: 메타 시스템 초기화 실행
        Then: 필수 구성요소들이 올바르게 초기화되어야 함
        """
        from final_report_generator import MachoReportGenerator
        generator = MachoReportGenerator()
        
        # 필수 속성들이 존재해야 함
        self.assertTrue(hasattr(generator, 'containment_modes'))
        self.assertTrue(hasattr(generator, 'command_registry'))
        self.assertTrue(hasattr(generator, 'confidence_threshold'))
        
        # 기본값들이 올바르게 설정되어야 함
        self.assertGreaterEqual(generator.confidence_threshold, 0.95)
        self.assertIn('PRIME', generator.containment_modes)
        self.assertIn('ORACLE', generator.containment_modes)
        self.assertIn('LATTICE', generator.containment_modes)
        self.assertIn('RHYTHM', generator.containment_modes)
        self.assertIn('COST-GUARD', generator.containment_modes)
        self.assertIn('ZERO', generator.containment_modes)
    
    def test_readme_style_documentation_generation(self):
        """
        [GREEN] Phase 1-2: README.md Style Documentation Generation Test
        
        Given: 첨부된 README.md 스타일 요구사항
        When: 문서 생성 함수 실행
        Then: 체계적인 마크다운 문서가 생성되어야 함
        """
        from final_report_generator import generate_readme_style_report
        
        report_config = {
            'project_name': 'HVDC Samsung C&T Logistics',
            'version': 'v3.4-mini',
            'total_transactions': 7573,
            'vendors': ['HITACHI', 'SIMENSE'],
            'warehouses': ['DSV Indoor', 'DSV Outdoor', 'DSV Al Markaz', 'DSV MZP', 'MOSB'],
            'sites': ['AGI', 'DAS', 'MIR', 'SHU']
        }
        
        readme_content = generate_readme_style_report(report_config)
        
        # 필수 섹션들이 포함되어야 함
        self.assertIn('# 🚀 MACHO-GPT', readme_content)
        self.assertIn('## 📋 프로젝트 개요', readme_content)
        self.assertIn('## 🚀 빠른 시작', readme_content)
        self.assertIn('## 📊 최종 결과물', readme_content)
        self.assertIn('## 🔧 시스템 요구사항', readme_content)
        self.assertIn('## 🎯 MACHO-GPT 명령어', readme_content)
        
        # 프로젝트 정보가 올바르게 포함되어야 함
        self.assertIn('HVDC Samsung C&T Logistics', readme_content)
        self.assertIn('v3.4-mini', readme_content)
        self.assertIn('7,573건', readme_content)
    
    def test_excel_warehouse_monthly_structure(self):
        """
        [GREEN] Phase 1-3: Excel Warehouse Monthly Structure Test
        
        Given: 첨부된 Excel 스크린샷의 창고별 월별 구조
        When: Excel 리포트 생성 실행
        Then: 올바른 구조의 창고별 월별 데이터가 생성되어야 함
        """
        from final_report_generator import generate_warehouse_monthly_excel
        
        expected_warehouses = [
            'AA Storage', 'DSV Al Markaz', 'DSV Indoor', 
            'DSV MZP', 'DSV Outdoor', 'Hauler Indoor', 'MOSB'
        ]
        
        excel_data = generate_warehouse_monthly_excel(self.sample_transaction_data)
        
        # Excel 구조 검증
        self.assertIn('창고_월별_입출고', excel_data.keys())
        warehouse_sheet = excel_data['창고_월별_입출고']
        
        # Multi-level 헤더 구조 검증
        self.assertIsInstance(warehouse_sheet.columns, pd.MultiIndex)
        self.assertIn('입고', warehouse_sheet.columns.get_level_values(0))
        self.assertIn('출고', warehouse_sheet.columns.get_level_values(0))
        
        # 창고별 컬럼 존재 확인
        for warehouse in expected_warehouses:
            self.assertIn(warehouse, warehouse_sheet.columns.get_level_values(1))
    
    def test_excel_site_monthly_structure(self):
        """
        [GREEN] Phase 1-4: Excel Site Monthly Structure Test
        
        Given: 첨부된 Excel 스크린샷의 현장별 월별 구조
        When: 현장별 Excel 리포트 생성 실행
        Then: 올바른 구조의 현장별 월별 데이터가 생성되어야 함
        """
        from final_report_generator import generate_site_monthly_excel
        
        expected_sites = ['AGI', 'DAS', 'MIR', 'SHU']
        
        excel_data = generate_site_monthly_excel(self.sample_transaction_data)
        
        # Excel 구조 검증
        self.assertIn('현장_월별_입고재고', excel_data.keys())
        site_sheet = excel_data['현장_월별_입고재고']
        
        # Multi-level 헤더 구조 검증
        self.assertIsInstance(site_sheet.columns, pd.MultiIndex)
        self.assertIn('입고', site_sheet.columns.get_level_values(0))
        self.assertIn('재고', site_sheet.columns.get_level_values(0))
        
        # 현장별 컬럼 존재 확인
        for site in expected_sites:
            self.assertIn(site, site_sheet.columns.get_level_values(1))
    
    def test_batch_script_generation(self):
        """
        [GREEN] Phase 1-5: User-Friendly Batch Script Generation Test
        
        Given: 사용자 친화적 실행 스크립트 요구
        When: 배치 스크립트 생성 실행
        Then: 원클릭 실행 가능한 배치 파일이 생성되어야 함
        """
        from final_report_generator import generate_batch_script
        
        batch_content = generate_batch_script()
        
        # 배치 스크립트 필수 요소 검증
        self.assertIn('@echo off', batch_content)
        self.assertIn('python', batch_content)
        self.assertIn('pause', batch_content)
        self.assertIn('MACHO-GPT', batch_content)
        
        # 메뉴 옵션들 존재 확인
        self.assertIn('1)', batch_content)  # 옵션 1
        self.assertIn('2)', batch_content)  # 옵션 2
        self.assertIn('8)', batch_content)  # 종료 옵션
        
        # UTF-8 인코딩 설정 확인
        self.assertIn('chcp 65001', batch_content)
    
    def test_macho_command_integration(self):
        """
        [GREEN] Phase 1-6: MACHO-GPT Command Integration Test
        
        Given: /cmd 시스템 통합 요구
        When: 명령어 추천 시스템 실행
        Then: 적절한 MACHO-GPT 명령어들이 추천되어야 함
        """
        from final_report_generator import get_recommended_commands
        
        context = {
            'operation_type': 'final_report_generation',
            'data_quality': 0.94,
            'mode': 'PRIME'
        }
        
        commands = get_recommended_commands(context)
        
        # 명령어 형식 검증
        self.assertIsInstance(commands, list)
        self.assertEqual(len(commands), 3)  # 3개 추천 명령어
        
        # 명령어 내용 검증
        for cmd in commands:
            self.assertIn('name', cmd)
            self.assertIn('description', cmd)
            self.assertTrue(cmd['name'].startswith('/'))  # /cmd 형식
            self.assertIsInstance(cmd['description'], str)
            
        # 필수 명령어들 확인
        command_names = [cmd['name'] for cmd in commands]
        self.assertIn('/validate-data', command_names)
        self.assertIn('/generate_insights', command_names)
        self.assertIn('/automate_workflow', command_names)
    
    def tearDown(self):
        """테스트 정리"""
        # 테스트 파일들 정리
        import shutil
        if self.test_data_dir.exists():
            shutil.rmtree(self.test_data_dir)

if __name__ == '__main__':
    print("✅ [TDD] MACHO-GPT Final Report Style System Tests")
    print("📋 Phase 1: Core Infrastructure Tests (Green Phase)")
    print("=" * 60)
    
    # TDD Green Phase: 모든 테스트가 통과해야 함
    unittest.main(verbosity=2) 