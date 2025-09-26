"""
FANR Compliance Validation Tests
Phase 2: Invoice OCR Module Tests - TDD Cycle
"""

import unittest
import pandas as pd
from datetime import datetime
from typing import Dict, Any

class TestFANRComplianceValidation(unittest.TestCase):
    """FANR 규정 준수 검증 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.sample_invoice_data = {
            'invoice_number': 'INV-2025-001',
            'hs_code': 'HS123456',
            'amount': 15000.0,
            'currency': 'AED',
            'supplier': 'Samsung C&T',
            'certification_number': 'FANR-2025-001',
            'expiry_date': '2025-12-31',
            'compliance_score': 0.98
        }
        
    def test_fanr_certification_should_be_valid_when_certification_number_exists(self):
        """FANR 인증번호가 존재할 때 유효성 검증"""
        # Given: FANR 인증번호가 있는 송장 데이터
        invoice_data = self.sample_invoice_data.copy()
        
        # When: FANR 인증 검증 실행
        result = self.validate_fanr_certification(invoice_data)
        
        # Then: 인증이 유효해야 함
        self.assertTrue(result['is_valid'])
        self.assertEqual(result['certification_number'], 'FANR-2025-001')
        self.assertGreaterEqual(result['confidence'], 0.95)
        
    def test_fanr_certification_should_fail_when_certification_number_missing(self):
        """FANR 인증번호가 없을 때 검증 실패"""
        # Given: FANR 인증번호가 없는 송장 데이터
        invoice_data = self.sample_invoice_data.copy()
        invoice_data['certification_number'] = None
        
        # When: FANR 인증 검증 실행
        result = self.validate_fanr_certification(invoice_data)
        
        # Then: 인증이 실패해야 함
        self.assertFalse(result['is_valid'])
        self.assertEqual(result['error'], 'FANR certification number is required')
        self.assertEqual(result['confidence'], 0.0)
        
    def test_fanr_certification_should_fail_when_expiry_date_passed(self):
        """FANR 인증 만료일이 지났을 때 검증 실패"""
        # Given: 만료된 FANR 인증
        invoice_data = self.sample_invoice_data.copy()
        invoice_data['expiry_date'] = '2024-12-31'  # 만료된 날짜
        
        # When: FANR 인증 검증 실행
        result = self.validate_fanr_certification(invoice_data)
        
        # Then: 인증이 실패해야 함
        self.assertFalse(result['is_valid'])
        self.assertIn('expired', result['error'].lower())
        self.assertEqual(result['confidence'], 0.0)
        
    def test_fanr_compliance_score_should_be_above_threshold(self):
        """FANR 준수 점수가 임계값 이상이어야 함"""
        # Given: 다양한 준수 점수
        test_cases = [
            {'score': 0.98, 'expected': True},
            {'score': 0.95, 'expected': True},
            {'score': 0.94, 'expected': False},
            {'score': 0.90, 'expected': False}
        ]
        
        for case in test_cases:
            with self.subTest(score=case['score']):
                # Given: 특정 준수 점수
                invoice_data = self.sample_invoice_data.copy()
                invoice_data['compliance_score'] = case['score']
                
                # When: FANR 준수 검증 실행
                result = self.validate_fanr_compliance(invoice_data)
                
                # Then: 임계값에 따른 결과 확인
                self.assertEqual(result['is_compliant'], case['expected'])
                
    def test_fanr_validation_should_trigger_zero_mode_when_compliance_fails(self):
        """FANR 준수 실패 시 ZERO 모드 전환"""
        # Given: 준수하지 않는 송장 데이터
        invoice_data = self.sample_invoice_data.copy()
        invoice_data['compliance_score'] = 0.85  # 임계값 미달
        
        # When: FANR 검증 실행
        result = self.validate_fanr_compliance(invoice_data)
        
        # Then: ZERO 모드 전환 및 알림
        self.assertFalse(result['is_compliant'])
        self.assertEqual(result['mode'], 'ZERO')
        self.assertIn('compliance_failed', result['triggers'])
        
    def test_fanr_validation_should_log_audit_trail(self):
        """FANR 검증 시 감사 로그 생성"""
        # Given: 송장 데이터
        invoice_data = self.sample_invoice_data.copy()
        
        # When: FANR 검증 실행
        result = self.validate_fanr_compliance(invoice_data)
        
        # Then: 감사 로그 생성
        self.assertIn('audit_trail', result)
        self.assertIn('timestamp', result['audit_trail'])
        self.assertIn('invoice_number', result['audit_trail'])
        self.assertIn('validation_result', result['audit_trail'])
        
    # Helper methods (실제 구현은 나중에)
    def validate_fanr_certification(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """FANR 인증 검증 (실제 구현 전 임시)"""
        # Red: 실패하는 테스트를 위한 최소 구현
        if not invoice_data.get('certification_number'):
            return {
                'is_valid': False,
                'error': 'FANR certification number is required',
                'confidence': 0.0
            }
        
        # 만료일 검증
        expiry_date = invoice_data.get('expiry_date')
        if expiry_date:
            try:
                expiry = datetime.strptime(expiry_date, '%Y-%m-%d')
                if expiry < datetime.now():
                    return {
                        'is_valid': False,
                        'error': 'FANR certification has expired',
                        'confidence': 0.0
                    }
            except ValueError:
                return {
                    'is_valid': False,
                    'error': 'Invalid expiry date format',
                    'confidence': 0.0
                }
        
        return {
            'is_valid': True,
            'certification_number': invoice_data['certification_number'],
            'confidence': 0.95
        }
        
    def validate_fanr_compliance(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """FANR 준수 검증 (실제 구현 전 임시)"""
        # Red: 실패하는 테스트를 위한 최소 구현
        compliance_score = invoice_data.get('compliance_score', 0.0)
        threshold = 0.95
        
        is_compliant = compliance_score >= threshold
        mode = 'ZERO' if not is_compliant else 'PRIME'
        
        triggers = []
        if not is_compliant:
            triggers.append('compliance_failed')
            
        audit_trail = {
            'timestamp': datetime.now().isoformat(),
            'invoice_number': invoice_data.get('invoice_number'),
            'validation_result': 'PASS' if is_compliant else 'FAIL',
            'compliance_score': compliance_score,
            'threshold': threshold
        }
        
        return {
            'is_compliant': is_compliant,
            'compliance_score': compliance_score,
            'mode': mode,
            'triggers': triggers,
            'audit_trail': audit_trail,
            'confidence': compliance_score if is_compliant else 0.0
        }

if __name__ == '__main__':
    unittest.main() 