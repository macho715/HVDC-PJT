"""
PKG 수량 검증 시스템 테스트
HVDC 프로젝트 TDD 개발 - Phase 1: PKG 수량 집계 테스트
"""

import unittest
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List
import sys
import os

# src 디렉토리를 Python 경로에 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from pkg_validation import PKGValidationSystem

class TestPKGValidation(unittest.TestCase):
    """PKG 수량 검증 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        # PKG 검증 시스템 초기화
        self.pkg_validator = PKGValidationSystem()
        
        # 샘플 송장 데이터
        self.invoice_data = pd.DataFrame({
            'invoice_number': ['INV-001', 'INV-002', 'INV-003'],
            'hs_code': ['HS123456', 'HS789012', 'HS345678'],
            'pkg_count': [100, 150, 200],
            'amount': [15000.0, 22500.0, 30000.0],
            'currency': ['AED', 'AED', 'AED'],
            'supplier': ['Samsung C&T', 'Samsung C&T', 'Samsung C&T'],
            'date': ['2025-01-15', '2025-01-16', '2025-01-17']
        })
        
        # 샘플 창고 입고 데이터
        self.warehouse_data = pd.DataFrame({
            'warehouse_code': ['DSV-OUT', 'DSV-IN', 'DSV-OUT'],
            'invoice_number': ['INV-001', 'INV-002', 'INV-003'],
            'pkg_count': [100, 150, 200],
            'received_date': ['2025-01-15', '2025-01-16', '2025-01-17'],
            'status': ['received', 'received', 'received']
        })
        
        # 샘플 현장 데이터
        self.site_data = pd.DataFrame({
            'site_code': ['HVDC-SITE-1', 'HVDC-SITE-2'],
            'invoice_number': ['INV-001', 'INV-002'],
            'pkg_count': [95, 145],  # 일부 누락/손실
            'delivery_date': ['2025-01-20', '2025-01-21'],
            'status': ['delivered', 'delivered']
        })
        
    def test_pkg_count_should_match_between_invoice_and_warehouse(self):
        """송장과 창고 데이터의 PKG 수량 일치 검증"""
        # Given: 송장 데이터와 창고 입고 데이터
        invoice_pkg_total = self.invoice_data['pkg_count'].sum()
        warehouse_pkg_total = self.warehouse_data['pkg_count'].sum()
        
        # When: PKG 수량 검증 실행
        result = self.pkg_validator.validate_pkg_count_match(
            self.invoice_data, 
            self.warehouse_data
        )
        
        # Then: 두 데이터의 PKG 수량이 일치해야 함
        self.assertTrue(result['is_match'])
        self.assertEqual(result['invoice_total'], invoice_pkg_total)
        self.assertEqual(result['warehouse_total'], warehouse_pkg_total)
        self.assertEqual(result['difference'], 0)
        self.assertGreaterEqual(result['confidence'], 0.95)
        
    def test_pkg_count_discrepancy_should_be_detected(self):
        """PKG 수량 불일치 탐지"""
        # Given: 불일치가 있는 데이터 (현장 데이터 사용)
        invoice_pkg_total = self.invoice_data['pkg_count'].sum()
        site_pkg_total = self.site_data['pkg_count'].sum()
        expected_difference = invoice_pkg_total - site_pkg_total
        
        # When: PKG 수량 검증 실행
        result = self.pkg_validator.validate_pkg_count_match(
            self.invoice_data, 
            self.site_data,
            data1_name='invoice',
            data2_name='site'
        )
        
        # Then: 불일치 탐지
        self.assertFalse(result['is_match'])
        self.assertEqual(result['invoice_total'], invoice_pkg_total)
        self.assertEqual(result['site_total'], site_pkg_total)
        self.assertEqual(result['difference'], expected_difference)
        self.assertGreater(result['difference'], 0)
        self.assertIn('discrepancy_detected', result['alerts'])
        
    def test_pkg_count_validation_should_handle_empty_data(self):
        """빈 데이터 처리"""
        # Given: 빈 데이터프레임
        empty_invoice = pd.DataFrame()
        empty_warehouse = pd.DataFrame()
        
        # When: PKG 수량 검증 실행
        result = self.pkg_validator.validate_pkg_count_match(
            empty_invoice, 
            empty_warehouse
        )
        
        # Then: 적절한 오류 처리
        self.assertFalse(result['is_match'])
        self.assertIn('empty_data', result['errors'])
        self.assertEqual(result['confidence'], 0.0)
        
    def test_pkg_count_validation_should_handle_missing_columns(self):
        """누락된 컬럼 처리"""
        # Given: pkg_count 컬럼이 없는 데이터
        invoice_no_pkg = self.invoice_data.drop(columns=['pkg_count'])
        warehouse_no_pkg = self.warehouse_data.drop(columns=['pkg_count'])
        
        # When: PKG 수량 검증 실행
        result = self.pkg_validator.validate_pkg_count_match(
            invoice_no_pkg, 
            warehouse_no_pkg
        )
        
        # Then: 컬럼 누락 오류 처리
        self.assertFalse(result['is_match'])
        self.assertIn('missing_pkg_count_column', result['errors'])
        self.assertEqual(result['confidence'], 0.0)
        
    def test_pkg_count_validation_should_calculate_confidence_score(self):
        """신뢰도 점수 계산"""
        # Given: 정상 데이터
        # When: PKG 수량 검증 실행
        result = self.pkg_validator.validate_pkg_count_match(
            self.invoice_data, 
            self.warehouse_data
        )
        
        # Then: 신뢰도 점수 계산
        self.assertIn('confidence', result)
        self.assertIsInstance(result['confidence'], float)
        self.assertGreaterEqual(result['confidence'], 0.0)
        self.assertLessEqual(result['confidence'], 1.0)
        
    def test_pkg_count_validation_should_generate_detailed_report(self):
        """상세 리포트 생성"""
        # Given: 정상 데이터
        # When: PKG 수량 검증 실행
        result = self.pkg_validator.validate_pkg_count_match(
            self.invoice_data, 
            self.warehouse_data
        )
        
        # Then: 상세 리포트 생성
        self.assertIn('report', result)
        self.assertIn('timestamp', result['report'])
        self.assertIn('summary', result['report'])
        self.assertIn('details', result['report'])
        self.assertIn('recommendations', result['report'])
        
    def test_pkg_count_validation_should_trigger_alerts_for_critical_discrepancies(self):
        """중요 불일치 시 알림 트리거"""
        # Given: 큰 불일치가 있는 데이터
        large_discrepancy_data = self.warehouse_data.copy()
        large_discrepancy_data.loc[0, 'pkg_count'] = 30  # 큰 차이 (100 -> 30 = 70 차이)
        
        # When: PKG 수량 검증 실행
        result = self.pkg_validator.validate_pkg_count_match(
            self.invoice_data, 
            large_discrepancy_data
        )
        
        # Then: 중요 알림 트리거
        self.assertFalse(result['is_match'])
        self.assertIn('critical_discrepancy', result['alerts'])
        self.assertGreater(result['difference'], 50)  # 임계값 초과
        
    # Helper methods (실제 구현은 나중에)
    def validate_pkg_count_match(self, data1: pd.DataFrame, data2: pd.DataFrame) -> Dict[str, Any]:
        """PKG 수량 일치 검증 (실제 구현 전 임시)"""
        # Red: 실패하는 테스트를 위한 최소 구현
        result = {
            'is_match': False,
            'invoice_total': 0,
            'warehouse_total': 0,
            'site_total': 0,
            'difference': 0,
            'confidence': 0.0,
            'alerts': [],
            'errors': [],
            'report': {
                'timestamp': datetime.now().isoformat(),
                'summary': '',
                'details': {},
                'recommendations': []
            }
        }
        
        # 빈 데이터 체크
        if data1.empty or data2.empty:
            result['errors'].append('empty_data')
            return result
            
        # pkg_count 컬럼 존재 체크
        if 'pkg_count' not in data1.columns or 'pkg_count' not in data2.columns:
            result['errors'].append('missing_pkg_count_column')
            return result
            
        # PKG 수량 집계
        total1 = data1['pkg_count'].sum()
        total2 = data2['pkg_count'].sum()
        
        result['invoice_total'] = total1
        result['warehouse_total'] = total2
        result['site_total'] = total2  # 임시로 동일하게 설정
        
        # 차이 계산
        difference = abs(total1 - total2)
        result['difference'] = difference
        
        # 일치 여부 판단
        result['is_match'] = difference == 0
        
        # 신뢰도 계산 (간단한 로직)
        if result['is_match']:
            result['confidence'] = 0.95
        else:
            result['confidence'] = max(0.0, 0.95 - (difference / total1 * 0.5))
            
        # 알림 생성
        if not result['is_match']:
            result['alerts'].append('discrepancy_detected')
            if difference > 50:  # 임계값
                result['alerts'].append('critical_discrepancy')
                
        # 리포트 생성
        result['report']['summary'] = f"PKG 수량 검증: {'일치' if result['is_match'] else '불일치'}"
        result['report']['details'] = {
            'invoice_total': total1,
            'warehouse_total': total2,
            'difference': difference
        }
        result['report']['recommendations'] = [
            '불일치 발견 시 즉시 조사 필요',
            '정기적인 PKG 수량 검증 권장'
        ]
        
        return result

if __name__ == '__main__':
    unittest.main() 