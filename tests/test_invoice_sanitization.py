"""
Invoice Data Sanitization Tests
Phase 2: Invoice OCR Module Tests - TDD Cycle
"""

import unittest
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List

class TestInvoiceDataSanitization(unittest.TestCase):
    """송장 데이터 정제 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.sample_invoice_data = {
            'invoice_number': 'INV-2025-001',
            'supplier_name': 'Samsung C&T Corporation',
            'amount': 15000.0,
            'currency': 'AED',
            'hs_code': 'HS123456',
            'description': 'HVDC Equipment',
            'email': 'test@example.com',
            'phone': '+971-50-123-4567',
            'address': 'Dubai, UAE',
            'raw_text': 'Sample invoice text with special characters: @#$%^&*()'
        }
        
    def test_invoice_data_should_remove_special_characters_from_text_fields(self):
        """텍스트 필드에서 특수문자 제거"""
        # Given: 특수문자가 포함된 송장 데이터
        invoice_data = self.sample_invoice_data.copy()
        invoice_data['description'] = 'HVDC@Equipment#$%^&*()'
        invoice_data['supplier_name'] = 'Samsung&C&T@Corporation'
        
        # When: 데이터 정제 실행
        result = self.sanitize_invoice_data(invoice_data)
        
        # Then: 특수문자 제거
        self.assertEqual(result['description'], 'HVDC Equipment')
        self.assertEqual(result['supplier_name'], 'Samsung C T Corporation')
        self.assertNotIn('@', result['description'])
        self.assertNotIn('#', result['description'])
        
    def test_invoice_data_should_normalize_phone_numbers(self):
        """전화번호 정규화"""
        # Given: 다양한 형식의 전화번호
        test_cases = [
            '+971-50-123-4567',
            '+971501234567',
            '971-50-123-4567',
            '050-123-4567',
            '50-123-4567'
        ]
        
        for phone in test_cases:
            with self.subTest(phone=phone):
                # Given: 특정 전화번호
                invoice_data = self.sample_invoice_data.copy()
                invoice_data['phone'] = phone
                
                # When: 전화번호 정규화
                result = self.sanitize_invoice_data(invoice_data)
                
                # Then: 정규화된 형식
                self.assertIsNotNone(result['phone'])
                self.assertTrue(result['phone'].startswith('+971'))
                self.assertEqual(len(result['phone'].replace('-', '')), 13)
                
    def test_invoice_data_should_validate_email_format(self):
        """이메일 형식 검증"""
        # Given: 다양한 이메일 형식
        test_cases = [
            {'email': 'valid@example.com', 'expected': True},
            {'email': 'invalid-email', 'expected': False},
            {'email': '@example.com', 'expected': False},
            {'email': 'test@', 'expected': False},
            {'email': '', 'expected': False}
        ]
        
        for case in test_cases:
            with self.subTest(email=case['email']):
                # Given: 특정 이메일
                invoice_data = self.sample_invoice_data.copy()
                invoice_data['email'] = case['email']
                
                # When: 이메일 검증
                result = self.sanitize_invoice_data(invoice_data)
                
                # Then: 검증 결과 확인
                if case['expected']:
                    self.assertEqual(result['email'], case['email'])
                    self.assertTrue(result['email_valid'])
                else:
                    self.assertFalse(result['email_valid'])
                    self.assertIn('email_invalid', result['validation_errors'])
                    
    def test_invoice_data_should_validate_hs_code_format(self):
        """HS 코드 형식 검증"""
        # Given: 다양한 HS 코드 형식
        test_cases = [
            {'hs_code': 'HS123456', 'expected': True},
            {'hs_code': '123456', 'expected': False},
            {'hs_code': 'HS12345', 'expected': False},  # 너무 짧음
            {'hs_code': 'HS1234567', 'expected': False},  # 너무 김
            {'hs_code': '', 'expected': False}
        ]
        
        for case in test_cases:
            with self.subTest(hs_code=case['hs_code']):
                # Given: 특정 HS 코드
                invoice_data = self.sample_invoice_data.copy()
                invoice_data['hs_code'] = case['hs_code']
                
                # When: HS 코드 검증
                result = self.sanitize_invoice_data(invoice_data)
                
                # Then: 검증 결과 확인
                if case['expected']:
                    self.assertEqual(result['hs_code'], case['hs_code'])
                    self.assertTrue(result['hs_code_valid'])
                else:
                    self.assertFalse(result['hs_code_valid'])
                    self.assertIn('hs_code_invalid', result['validation_errors'])
                    
    def test_invoice_data_should_validate_amount_format(self):
        """금액 형식 검증"""
        # Given: 다양한 금액 형식
        test_cases = [
            {'amount': 15000.0, 'expected': True},
            {'amount': '15000', 'expected': True},
            {'amount': '15,000.50', 'expected': True},
            {'amount': -15000.0, 'expected': False},  # 음수
            {'amount': 'invalid', 'expected': False},
            {'amount': '', 'expected': False}
        ]
        
        for case in test_cases:
            with self.subTest(amount=case['amount']):
                # Given: 특정 금액
                invoice_data = self.sample_invoice_data.copy()
                invoice_data['amount'] = case['amount']
                
                # When: 금액 검증
                result = self.sanitize_invoice_data(invoice_data)
                
                # Then: 검증 결과 확인
                if case['expected']:
                    self.assertIsInstance(result['amount'], (int, float))
                    self.assertTrue(result['amount_valid'])
                    self.assertGreater(result['amount'], 0)
                else:
                    self.assertFalse(result['amount_valid'])
                    self.assertIn('amount_invalid', result['validation_errors'])
                    
    def test_invoice_data_should_remove_pii_data(self):
        """PII 데이터 제거"""
        # Given: PII가 포함된 송장 데이터
        invoice_data = self.sample_invoice_data.copy()
        invoice_data['customer_id'] = 'CUST-12345'
        invoice_data['passport_number'] = 'A12345678'
        invoice_data['credit_card'] = '1234-5678-9012-3456'
        invoice_data['ssn'] = '123-45-6789'
        
        # When: PII 제거 실행
        result = self.sanitize_invoice_data(invoice_data)
        
        # Then: PII 필드 제거
        self.assertNotIn('customer_id', result)
        self.assertNotIn('passport_number', result)
        self.assertNotIn('credit_card', result)
        self.assertNotIn('ssn', result)
        self.assertIn('pii_removed', result['sanitization_log']['actions_taken'])
        
    def test_invoice_data_should_log_sanitization_actions(self):
        """정제 작업 로그 기록"""
        # Given: 정제가 필요한 송장 데이터
        invoice_data = self.sample_invoice_data.copy()
        invoice_data['description'] = 'HVDC@Equipment#$%^&*()'
        invoice_data['email'] = 'invalid-email'
        
        # When: 데이터 정제 실행
        result = self.sanitize_invoice_data(invoice_data)
        
        # Then: 정제 로그 확인
        self.assertIn('sanitization_log', result)
        self.assertIn('timestamp', result['sanitization_log'])
        self.assertIn('actions_taken', result['sanitization_log'])
        self.assertIn('special_characters_removed', result['sanitization_log']['actions_taken'])
        
    def test_invoice_data_should_preserve_required_fields(self):
        """필수 필드 보존"""
        # Given: 필수 필드가 포함된 송장 데이터
        invoice_data = self.sample_invoice_data.copy()
        required_fields = ['invoice_number', 'amount', 'currency', 'supplier_name']
        
        # When: 데이터 정제 실행
        result = self.sanitize_invoice_data(invoice_data)
        
        # Then: 필수 필드 보존
        for field in required_fields:
            self.assertIn(field, result)
            self.assertIsNotNone(result[field])
            self.assertNotEqual(result[field], '')
            
    def test_invoice_data_should_handle_missing_fields_gracefully(self):
        """누락된 필드 우아하게 처리"""
        # Given: 일부 필드가 누락된 송장 데이터
        invoice_data = self.sample_invoice_data.copy()
        del invoice_data['email']
        del invoice_data['phone']
        
        # When: 데이터 정제 실행
        result = self.sanitize_invoice_data(invoice_data)
        
        # Then: 누락된 필드 처리
        self.assertIn('email', result)
        self.assertIn('phone', result)
        self.assertIsNone(result['email'])
        self.assertIsNone(result['phone'])
        self.assertIn('missing_fields', result['validation_errors'])
        
    # Helper methods (실제 구현은 나중에)
    def sanitize_invoice_data(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """송장 데이터 정제 (실제 구현 전 임시)"""
        # Red: 실패하는 테스트를 위한 최소 구현
        result = invoice_data.copy()
        
        # 기본 검증 결과
        result['email_valid'] = True
        result['hs_code_valid'] = True
        result['amount_valid'] = True
        result['validation_errors'] = []
        result['sanitization_log'] = {
            'timestamp': datetime.now().isoformat(),
            'actions_taken': []
        }
        
        # 특수문자 제거 (공백 보존)
        if 'description' in result:
            original_desc = result['description']
            # 특수문자만 제거하고 공백은 보존
            cleaned_desc = ''
            for i, c in enumerate(original_desc):
                if c.isalnum() or c.isspace():
                    cleaned_desc += c
                elif i > 0 and cleaned_desc and not cleaned_desc[-1].isspace():
                    cleaned_desc += ' '  # 특수문자 위치에 공백 추가
            result['description'] = cleaned_desc.strip()
            if original_desc != result['description']:
                result['sanitization_log']['actions_taken'].append('special_characters_removed')
                
        if 'supplier_name' in result:
            original_name = result['supplier_name']
            # 특수문자만 제거하고 공백은 보존
            cleaned_name = ''
            for i, c in enumerate(original_name):
                if c.isalnum() or c.isspace():
                    cleaned_name += c
                elif i > 0 and cleaned_name and not cleaned_name[-1].isspace():
                    cleaned_name += ' '  # 특수문자 위치에 공백 추가
            result['supplier_name'] = cleaned_name.strip()
            if original_name != result['supplier_name']:
                result['sanitization_log']['actions_taken'].append('special_characters_removed')
                
        # 전화번호 정규화
        if 'phone' in result and result['phone']:
            phone = result['phone']
            # 간단한 정규화 (실제로는 더 복잡한 로직 필요)
            phone = phone.replace('-', '').replace(' ', '')
            if phone.startswith('971'):
                phone = '+' + phone
            elif phone.startswith('0'):
                phone = '+971' + phone[1:]
            elif len(phone) == 9 and phone.startswith('50'):  # UAE 모바일 번호
                phone = '+971' + phone
            result['phone'] = phone
            
        # 이메일 검증
        if 'email' in result:
            email = result['email']
            if email and '@' in email and '.' in email.split('@')[1] and len(email.split('@')[0]) > 0:
                result['email_valid'] = True
            else:
                result['email_valid'] = False
                result['validation_errors'].append('email_invalid')
                
        # HS 코드 검증
        if 'hs_code' in result:
            hs_code = result['hs_code']
            if hs_code and hs_code.startswith('HS') and len(hs_code) == 8:
                result['hs_code_valid'] = True
            else:
                result['hs_code_valid'] = False
                result['validation_errors'].append('hs_code_invalid')
                
        # 금액 검증
        if 'amount' in result:
            amount = result['amount']
            try:
                if isinstance(amount, str):
                    amount = float(amount.replace(',', ''))
                if isinstance(amount, (int, float)) and amount > 0:
                    result['amount'] = float(amount)
                    result['amount_valid'] = True
                else:
                    result['amount_valid'] = False
                    result['validation_errors'].append('amount_invalid')
            except (ValueError, TypeError):
                result['amount_valid'] = False
                result['validation_errors'].append('amount_invalid')
                
        # PII 제거
        pii_fields = ['customer_id', 'passport_number', 'credit_card', 'ssn']
        pii_found = False
        for field in pii_fields:
            if field in result:
                del result[field]
                pii_found = True
        if pii_found:
            result['sanitization_log']['actions_taken'].append('pii_removed')
            
        # 누락된 필드 처리
        missing_fields = []
        for field in ['email', 'phone']:
            if field not in result:
                result[field] = None
                missing_fields.append(field)
        if missing_fields:
            result['validation_errors'].append('missing_fields')
            
        return result

if __name__ == '__main__':
    unittest.main() 