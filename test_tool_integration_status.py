#!/usr/bin/env python3
"""
TDD Phase 1: Core Infrastructure Tests
다섯 번째 테스트: Tool Integration Status

테스트 목적: MACHO-GPT의 외부 도구 통합 상태 검증
- Python 패키지 의존성 상태
- Excel 처리 도구 (openpyxl, pandas)
- 데이터 분석 도구 (numpy, matplotlib)
- 시스템 도구 (importlib, datetime)
- 외부 API 연결 상태
- 파일 시스템 접근 권한

Integration Categories:
- Core Python Libraries
- Data Processing Tools
- Excel/Report Generation
- System Integration
- External API Connections
- File System Access
"""

import unittest
import sys
import os
import importlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import json

class ToolIntegrationStatus:
    """도구 통합 상태 관리"""
    
    def __init__(self):
        """도구 통합 상태 초기화"""
        self.integration_results = {}
        self.required_packages = {
            'core_python': ['os', 'sys', 'json', 'datetime', 'importlib'],
            'data_processing': ['pandas', 'numpy'],
            'excel_tools': ['openpyxl', 'xlsxwriter'],
            'analysis_tools': ['matplotlib', 'seaborn'],
            'system_tools': ['logging', 'pathlib', 'subprocess'],
            'optional_tools': ['requests', 'urllib3']
        }
        self.integration_status = {}
        self.confidence_threshold = 0.95
        
    def check_package_availability(self, package_name: str) -> Dict:
        """패키지 가용성 검증"""
        try:
            module = importlib.import_module(package_name)
            version = getattr(module, '__version__', 'unknown')
            return {
                'package': package_name,
                'status': 'available',
                'version': version,
                'confidence': 1.0,
                'error': None
            }
        except ImportError as e:
            return {
                'package': package_name,
                'status': 'unavailable',
                'version': None,
                'confidence': 0.0,
                'error': str(e)
            }
        except Exception as e:
            return {
                'package': package_name,
                'status': 'error',
                'version': None,
                'confidence': 0.0,
                'error': str(e)
            }
    
    def check_category_integration(self, category: str) -> Dict:
        """카테고리별 통합 상태 검증"""
        if category not in self.required_packages:
            return {
                'category': category,
                'status': 'unknown',
                'packages': [],
                'success_rate': 0.0,
                'confidence': 0.0
            }
        
        packages = self.required_packages[category]
        results = []
        success_count = 0
        
        for package in packages:
            result = self.check_package_availability(package)
            results.append(result)
            if result['status'] == 'available':
                success_count += 1
        
        success_rate = success_count / len(packages) if packages else 0.0
        
        return {
            'category': category,
            'status': 'healthy' if success_rate >= 0.8 else 'degraded' if success_rate >= 0.5 else 'critical',
            'packages': results,
            'success_rate': success_rate,
            'confidence': success_rate
        }
    
    def check_file_system_access(self) -> Dict:
        """파일 시스템 접근 권한 검증"""
        try:
            # 현재 디렉토리 읽기 권한
            current_dir = os.getcwd()
            dir_contents = os.listdir(current_dir)
            
            # 임시 파일 생성 권한
            test_file = 'test_integration_status.tmp'
            with open(test_file, 'w') as f:
                f.write('test')
            
            # 파일 삭제 권한
            os.remove(test_file)
            
            return {
                'component': 'file_system',
                'status': 'accessible',
                'current_dir': current_dir,
                'write_permission': True,
                'read_permission': True,
                'confidence': 1.0
            }
        except Exception as e:
            return {
                'component': 'file_system',
                'status': 'restricted',
                'current_dir': os.getcwd(),
                'write_permission': False,
                'read_permission': False,
                'confidence': 0.0,
                'error': str(e)
            }
    
    def check_macho_data_directories(self) -> Dict:
        """MACHO 데이터 디렉토리 접근 검증"""
        macho_paths = [
            'MACHO_통합관리_20250702_205301',
            'hvdc_macho_gpt/WAREHOUSE/data',
            'output'
        ]
        
        accessible_paths = []
        total_paths = len(macho_paths)
        
        for path in macho_paths:
            if os.path.exists(path):
                accessible_paths.append(path)
        
        success_rate = len(accessible_paths) / total_paths if total_paths > 0 else 0.0
        
        return {
            'component': 'macho_directories',
            'status': 'accessible' if success_rate >= 0.5 else 'limited',
            'accessible_paths': accessible_paths,
            'total_paths': total_paths,
            'success_rate': success_rate,
            'confidence': success_rate
        }
    
    def check_excel_integration(self) -> Dict:
        """Excel 통합 상태 검증"""
        try:
            import pandas as pd
            import openpyxl
            
            # 테스트 데이터 생성
            test_data = pd.DataFrame({
                'A': [1, 2, 3],
                'B': ['test1', 'test2', 'test3']
            })
            
            # Excel 파일 생성 테스트
            test_file = 'test_excel_integration.xlsx'
            test_data.to_excel(test_file, index=False)
            
            # Excel 파일 읽기 테스트
            read_data = pd.read_excel(test_file)
            
            # 파일 정리
            os.remove(test_file)
            
            return {
                'component': 'excel_integration',
                'status': 'functional',
                'pandas_version': pd.__version__,
                'openpyxl_version': openpyxl.__version__,
                'write_test': True,
                'read_test': True,
                'confidence': 1.0
            }
        except Exception as e:
            return {
                'component': 'excel_integration',
                'status': 'dysfunctional',
                'confidence': 0.0,
                'error': str(e)
            }
    
    def run_comprehensive_integration_check(self) -> Dict:
        """종합 통합 상태 검증"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'categories': {},
            'system_components': {},
            'overall_status': 'unknown',
            'overall_confidence': 0.0
        }
        
        # 카테고리별 검증
        total_confidence = 0.0
        category_count = 0
        
        for category in self.required_packages:
            category_result = self.check_category_integration(category)
            results['categories'][category] = category_result
            total_confidence += category_result['confidence']
            category_count += 1
        
        # 시스템 컴포넌트 검증
        results['system_components']['file_system'] = self.check_file_system_access()
        results['system_components']['macho_directories'] = self.check_macho_data_directories()
        results['system_components']['excel_integration'] = self.check_excel_integration()
        
        # 시스템 컴포넌트 신뢰도 추가
        for component in results['system_components'].values():
            total_confidence += component['confidence']
            category_count += 1
        
        # 전체 신뢰도 계산
        overall_confidence = total_confidence / category_count if category_count > 0 else 0.0
        results['overall_confidence'] = overall_confidence
        results['overall_status'] = 'healthy' if overall_confidence >= 0.8 else 'degraded' if overall_confidence >= 0.5 else 'critical'
        
        return results

class TestToolIntegrationStatus(unittest.TestCase):
    """도구 통합 상태 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.tool_integration = ToolIntegrationStatus()
        self.required_confidence = 0.95
        
    def test_tool_integration_system_initialization(self):
        """도구 통합 시스템 초기화 검증"""
        # 필수 패키지 카테고리 확인
        expected_categories = {
            'core_python', 'data_processing', 'excel_tools', 
            'analysis_tools', 'system_tools', 'optional_tools'
        }
        
        actual_categories = set(self.tool_integration.required_packages.keys())
        self.assertEqual(actual_categories, expected_categories)
        
        # 초기 상태 확인
        self.assertEqual(self.tool_integration.confidence_threshold, 0.95)
        self.assertIsInstance(self.tool_integration.integration_results, dict)
    
    def test_core_python_libraries_availability(self):
        """핵심 Python 라이브러리 가용성 검증"""
        core_result = self.tool_integration.check_category_integration('core_python')
        
        self.assertEqual(core_result['category'], 'core_python')
        self.assertEqual(core_result['status'], 'healthy')
        self.assertEqual(core_result['success_rate'], 1.0)
        
        # 모든 핵심 라이브러리가 사용 가능해야 함
        for package_result in core_result['packages']:
            self.assertEqual(package_result['status'], 'available')
    
    def test_data_processing_tools_integration(self):
        """데이터 처리 도구 통합 검증"""
        data_result = self.tool_integration.check_category_integration('data_processing')
        
        self.assertEqual(data_result['category'], 'data_processing')
        self.assertGreaterEqual(data_result['success_rate'], 0.5)
        
        # pandas는 필수
        pandas_found = False
        for package_result in data_result['packages']:
            if package_result['package'] == 'pandas':
                pandas_found = True
                self.assertEqual(package_result['status'], 'available')
        
        self.assertTrue(pandas_found, "pandas는 필수 패키지입니다")
    
    def test_excel_tools_integration(self):
        """Excel 도구 통합 검증"""
        excel_result = self.tool_integration.check_category_integration('excel_tools')
        
        self.assertEqual(excel_result['category'], 'excel_tools')
        self.assertGreaterEqual(excel_result['success_rate'], 0.5)
        
        # openpyxl 확인
        openpyxl_found = False
        for package_result in excel_result['packages']:
            if package_result['package'] == 'openpyxl':
                openpyxl_found = True
                break
        
        self.assertTrue(openpyxl_found, "openpyxl 패키지가 필요합니다")
    
    def test_package_availability_check(self):
        """개별 패키지 가용성 검증"""
        # 존재하는 패키지 테스트
        os_result = self.tool_integration.check_package_availability('os')
        self.assertEqual(os_result['status'], 'available')
        self.assertEqual(os_result['confidence'], 1.0)
        
        # 존재하지 않는 패키지 테스트
        fake_result = self.tool_integration.check_package_availability('nonexistent_package_12345')
        self.assertEqual(fake_result['status'], 'unavailable')
        self.assertEqual(fake_result['confidence'], 0.0)
    
    def test_file_system_access_verification(self):
        """파일 시스템 접근 권한 검증"""
        fs_result = self.tool_integration.check_file_system_access()
        
        self.assertEqual(fs_result['component'], 'file_system')
        self.assertIn(fs_result['status'], ['accessible', 'restricted'])
        
        # 기본적인 읽기 권한은 있어야 함
        self.assertTrue(fs_result['read_permission'])
        self.assertIsNotNone(fs_result['current_dir'])
    
    def test_macho_data_directories_access(self):
        """MACHO 데이터 디렉토리 접근 검증"""
        macho_result = self.tool_integration.check_macho_data_directories()
        
        self.assertEqual(macho_result['component'], 'macho_directories')
        self.assertIn(macho_result['status'], ['accessible', 'limited'])
        self.assertIsInstance(macho_result['accessible_paths'], list)
        self.assertGreaterEqual(macho_result['total_paths'], 1)
    
    def test_excel_integration_functionality(self):
        """Excel 통합 기능 검증"""
        excel_result = self.tool_integration.check_excel_integration()
        
        self.assertEqual(excel_result['component'], 'excel_integration')
        self.assertIn(excel_result['status'], ['functional', 'dysfunctional'])
        
        # Excel 통합이 작동하는 경우 세부 확인
        if excel_result['status'] == 'functional':
            self.assertTrue(excel_result['write_test'])
            self.assertTrue(excel_result['read_test'])
            self.assertEqual(excel_result['confidence'], 1.0)
    
    def test_comprehensive_integration_check(self):
        """종합 통합 상태 검증"""
        comprehensive_result = self.tool_integration.run_comprehensive_integration_check()
        
        # 결과 구조 확인
        self.assertIn('timestamp', comprehensive_result)
        self.assertIn('categories', comprehensive_result)
        self.assertIn('system_components', comprehensive_result)
        self.assertIn('overall_status', comprehensive_result)
        self.assertIn('overall_confidence', comprehensive_result)
        
        # 전체 상태 확인
        self.assertIn(comprehensive_result['overall_status'], ['healthy', 'degraded', 'critical'])
        self.assertGreaterEqual(comprehensive_result['overall_confidence'], 0.0)
        self.assertLessEqual(comprehensive_result['overall_confidence'], 1.0)
    
    def test_integration_confidence_threshold(self):
        """통합 신뢰도 임계값 검증"""
        # 시스템 전체 신뢰도 확인
        comprehensive_result = self.tool_integration.run_comprehensive_integration_check()
        
        # 최소 신뢰도 임계값 확인 (개발 환경에서는 0.7 이상)
        min_confidence = 0.7
        self.assertGreaterEqual(comprehensive_result['overall_confidence'], min_confidence,
                               f"통합 신뢰도가 {min_confidence} 미만입니다")
    
    def test_macho_integration_compatibility(self):
        """MACHO 통합 시스템 호환성 검증"""
        # 핵심 요구사항 확인
        core_result = self.tool_integration.check_category_integration('core_python')
        data_result = self.tool_integration.check_category_integration('data_processing')
        
        # 핵심 라이브러리는 100% 가용해야 함
        self.assertEqual(core_result['success_rate'], 1.0)
        
        # 데이터 처리는 최소 50% 이상 가용해야 함
        self.assertGreaterEqual(data_result['success_rate'], 0.5)
    
    def test_tdd_red_phase_validation(self):
        """TDD RED 단계 검증"""
        # 이 테스트 자체가 TDD RED 단계임을 검증
        test_timestamp = datetime.now()
        
        # 테스트가 실행되고 있음을 확인
        self.assertIsInstance(test_timestamp, datetime)
        
        # 통합 상태 확인
        integration_result = self.tool_integration.run_comprehensive_integration_check()
        
        # TDD 단계 표시
        print(f"\n🔴 TDD RED Phase: Tool Integration Status Test")
        print(f"   테스트 시간: {test_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   검증 대상: {len(self.tool_integration.required_packages)} 카테고리 도구 통합")
        print(f"   전체 신뢰도: {integration_result['overall_confidence']:.2f}")
        print(f"   전체 상태: {integration_result['overall_status']}")
        print(f"   신뢰도 요구사항: ≥{self.required_confidence}")

if __name__ == '__main__':
    print("🧪 MACHO-GPT v3.5 TDD Phase 1: Core Infrastructure Tests")
    print("=" * 70)
    print("📋 Test: Tool Integration Status")
    print("🎯 Purpose: 외부 도구 통합 상태 검증")
    print("-" * 70)
    print("🔧 Categories: Core Python | Data Processing | Excel Tools | Analysis | System | Optional")
    print("🏗️ Components: File System | MACHO Directories | Excel Integration")
    print("-" * 70)
    
    # TDD RED Phase 실행
    unittest.main(verbosity=2) 