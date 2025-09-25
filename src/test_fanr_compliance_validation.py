#!/usr/bin/env python3
"""
FANR 규제 준수 검증 테스트
TDD Phase 2: test_fanr_compliance_validation
"""

import unittest
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# 프로젝트 루트 경로 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fanr_compliance_validator import validate_fanr_compliance, get_fanr_requirements

class TestFANRComplianceValidation(unittest.TestCase):
    """FANR 규제 준수 검증 테스트"""
    
    def setUp(self):
        """테스트 준비"""
        self.test_invoice_data = {
            'invoice_id': 'INV-2024-001',
            'hs_code': '8471.30.00',
            'confidence': 0.95,
            'certification_status': 'PENDING',
            'compliance_score': 0.0
        }
        
        self.fanr_requirements = get_fanr_requirements()
    
    def test_fanr_compliance_should_validate_hs_code_with_95_percent_confidence(self):
        """FANR 규제: HS 코드 신뢰도 ≥95% 검증"""
        # Given: FANR 승인된 송장 데이터
        invoice_data = self.test_invoice_data.copy()
        invoice_data['confidence'] = 0.95
        
        # When: FANR 준수 검증 실행
        result = validate_fanr_compliance(invoice_data)
        
        # Then: 신뢰도 ≥95% 확인
        self.assertEqual(result['status'], 'PASSED')
        self.assertGreaterEqual(result['confidence'], 0.95)
        self.assertGreaterEqual(result['compliance_score'], 0.95)
    
    def test_fanr_compliance_should_reject_low_confidence_invoices(self):
        """FANR 규제: 낮은 신뢰도 송장 거부"""
        # Given: 낮은 신뢰도 송장
        invoice_data = self.test_invoice_data.copy()
        invoice_data['confidence'] = 0.84
        
        # When: FANR 준수 검증 실행
        result = validate_fanr_compliance(invoice_data)
        
        # Then: 거부되어야 함
        self.assertEqual(result['status'], 'FAILED')
        self.assertLess(result['confidence'], 0.95)
        self.assertEqual(result['compliance_score'], 0.0)
        self.assertTrue(len(result['violations']) > 0)
    
    def test_fanr_compliance_should_validate_required_certifications(self):
        """FANR 규제: 필수 인증 검증"""
        # Given: 인증 정보가 포함된 송장
        invoice_data = self.test_invoice_data.copy()
        invoice_data['certifications'] = ['FANR-CERT']
        
        # When: FANR 준수 검증 실행
        result = validate_fanr_compliance(invoice_data)
        
        # Then: 필수 인증 확인
        self.assertTrue(result['certifications_validated'])
    
    def test_fanr_compliance_should_complete_within_3_seconds(self):
        """FANR 규제: 3초 이내 처리 완료"""
        # Given: 표준 송장 데이터
        invoice_data = self.test_invoice_data.copy()
        
        # When: FANR 준수 검증 실행 (시간 측정)
        start_time = datetime.now()
        result = validate_fanr_compliance(invoice_data)
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Then: 3초 이내 완료 확인
        self.assertLess(processing_time, 3.0)
        self.assertLess(result['processing_time'], 3.0)
    
    def test_fanr_compliance_should_handle_prohibited_items(self):
        """FANR 규제: 금지 품목 처리"""
        # Given: 금지 품목 포함 송장
        invoice_data = self.test_invoice_data.copy()
        invoice_data['item_category'] = 'hazardous_materials'
        
        # When: FANR 준수 검증 실행
        result = validate_fanr_compliance(invoice_data)
        
        # Then: 금지 품목 감지 및 거부
        self.assertEqual(result['status'], 'FAILED')
        self.assertEqual(result['compliance_score'], 0.0)
        self.assertTrue(any('hazardous_materials' in violation for violation in result['violations']))

if __name__ == '__main__':
    print("🧪 FANR 규제 준수 검증 테스트 실행")
    print("TDD Phase 2: test_fanr_compliance_validation")
    print("=" * 70)
    
    # Green 단계: 테스트 통과 확인
    unittest.main(verbosity=2) 