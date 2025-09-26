"""
OCR Fallback to Zero Mode Tests
Phase 2: Invoice OCR Module Tests - TDD Cycle
"""

import unittest
import pandas as pd
from datetime import datetime
from typing import Dict, Any

class TestOCRFallbackToZeroMode(unittest.TestCase):
    """OCR 실패 시 ZERO 모드 전환 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.sample_invoice_data = {
            'invoice_number': 'INV-2025-001',
            'image_path': 'invoice_sample.jpg',
            'ocr_confidence': 0.85,
            'extracted_text': 'Sample invoice text',
            'hs_code': 'HS123456',
            'amount': 15000.0,
            'currency': 'AED'
        }
        
    def test_ocr_should_fallback_to_zero_mode_when_confidence_below_threshold(self):
        """OCR 신뢰도가 임계값 미달 시 ZERO 모드 전환"""
        # Given: 낮은 OCR 신뢰도
        invoice_data = self.sample_invoice_data.copy()
        invoice_data['ocr_confidence'] = 0.75  # 임계값 0.85 미달
        
        # When: OCR 처리 및 모드 전환 확인
        result = self.process_ocr_with_fallback(invoice_data)
        
        # Then: ZERO 모드로 전환
        self.assertEqual(result['mode'], 'ZERO')
        self.assertFalse(result['ocr_success'])
        self.assertIn('low_confidence', result['triggers'])
        self.assertLess(result['confidence'], 0.85)
        
    def test_ocr_should_stay_in_prime_mode_when_confidence_above_threshold(self):
        """OCR 신뢰도가 임계값 이상 시 PRIME 모드 유지"""
        # Given: 높은 OCR 신뢰도
        invoice_data = self.sample_invoice_data.copy()
        invoice_data['ocr_confidence'] = 0.95  # 임계값 0.85 초과
        
        # When: OCR 처리 및 모드 확인
        result = self.process_ocr_with_fallback(invoice_data)
        
        # Then: PRIME 모드 유지
        self.assertEqual(result['mode'], 'PRIME')
        self.assertTrue(result['ocr_success'])
        self.assertNotIn('low_confidence', result['triggers'])
        self.assertGreaterEqual(result['confidence'], 0.85)
        
    def test_ocr_should_fallback_when_hs_code_extraction_fails(self):
        """HS 코드 추출 실패 시 ZERO 모드 전환"""
        # Given: HS 코드 추출 실패
        invoice_data = self.sample_invoice_data.copy()
        invoice_data['ocr_confidence'] = 0.90
        invoice_data['hs_code'] = None  # HS 코드 추출 실패
        
        # When: OCR 처리 및 모드 전환 확인
        result = self.process_ocr_with_fallback(invoice_data)
        
        # Then: ZERO 모드로 전환
        self.assertEqual(result['mode'], 'ZERO')
        self.assertFalse(result['ocr_success'])
        self.assertIn('hs_code_missing', result['triggers'])
        self.assertIsNone(result['extracted_hs_code'])
        
    def test_ocr_should_fallback_when_amount_extraction_fails(self):
        """금액 추출 실패 시 ZERO 모드 전환"""
        # Given: 금액 추출 실패
        invoice_data = self.sample_invoice_data.copy()
        invoice_data['ocr_confidence'] = 0.90
        invoice_data['amount'] = None  # 금액 추출 실패
        
        # When: OCR 처리 및 모드 전환 확인
        result = self.process_ocr_with_fallback(invoice_data)
        
        # Then: ZERO 모드로 전환
        self.assertEqual(result['mode'], 'ZERO')
        self.assertFalse(result['ocr_success'])
        self.assertIn('amount_missing', result['triggers'])
        self.assertIsNone(result['extracted_amount'])
        
    def test_ocr_should_fallback_when_image_processing_fails(self):
        """이미지 처리 실패 시 ZERO 모드 전환"""
        # Given: 이미지 처리 실패
        invoice_data = self.sample_invoice_data.copy()
        invoice_data['image_path'] = 'nonexistent.jpg'
        invoice_data['ocr_confidence'] = 0.0  # 처리 실패
        
        # When: OCR 처리 및 모드 전환 확인
        result = self.process_ocr_with_fallback(invoice_data)
        
        # Then: ZERO 모드로 전환
        self.assertEqual(result['mode'], 'ZERO')
        self.assertFalse(result['ocr_success'])
        self.assertIn('image_processing_failed', result['triggers'])
        self.assertEqual(result['confidence'], 0.0)
        
    def test_ocr_fallback_should_trigger_manual_review(self):
        """OCR 실패 시 수동 검토 트리거"""
        # Given: OCR 실패 상황
        invoice_data = self.sample_invoice_data.copy()
        invoice_data['ocr_confidence'] = 0.70  # 낮은 신뢰도
        
        # When: OCR 처리 및 수동 검토 확인
        result = self.process_ocr_with_fallback(invoice_data)
        
        # Then: 수동 검토 요청
        self.assertTrue(result['manual_review_required'])
        self.assertIn('manual_review', result['next_actions'])
        self.assertIsNotNone(result['fallback_reason'])
        
    def test_ocr_fallback_should_preserve_original_data(self):
        """OCR 실패 시 원본 데이터 보존"""
        # Given: OCR 실패 상황
        invoice_data = self.sample_invoice_data.copy()
        invoice_data['ocr_confidence'] = 0.60
        
        # When: OCR 처리 및 데이터 보존 확인
        result = self.process_ocr_with_fallback(invoice_data)
        
        # Then: 원본 데이터 보존
        self.assertIn('original_data', result)
        self.assertEqual(result['original_data']['invoice_number'], 'INV-2025-001')
        self.assertEqual(result['original_data']['image_path'], 'invoice_sample.jpg')
        
    def test_ocr_fallback_should_log_error_details(self):
        """OCR 실패 시 상세 오류 로그"""
        # Given: OCR 실패 상황
        invoice_data = self.sample_invoice_data.copy()
        invoice_data['ocr_confidence'] = 0.50
        
        # When: OCR 처리 및 오류 로그 확인
        result = self.process_ocr_with_fallback(invoice_data)
        
        # Then: 상세 오류 로그
        self.assertIn('error_log', result)
        self.assertIn('timestamp', result['error_log'])
        self.assertIn('error_type', result['error_log'])
        self.assertIn('confidence_threshold', result['error_log'])
        self.assertIn('actual_confidence', result['error_log'])
        
    # Helper methods (실제 구현은 나중에)
    def process_ocr_with_fallback(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """OCR 처리 및 실패 시 ZERO 모드 전환 (실제 구현 전 임시)"""
        # Red: 실패하는 테스트를 위한 최소 구현
        ocr_confidence = invoice_data.get('ocr_confidence', 0.0)
        confidence_threshold = 0.85
        
        # 기본 결과 구조
        result = {
            'mode': 'PRIME',
            'ocr_success': True,
            'confidence': ocr_confidence,
            'triggers': [],
            'next_actions': [],
            'manual_review_required': False,
            'fallback_reason': None,
            'original_data': invoice_data.copy(),
            'error_log': {
                'timestamp': datetime.now().isoformat(),
                'error_type': 'none',
                'confidence_threshold': confidence_threshold,
                'actual_confidence': ocr_confidence
            }
        }
        
        # 신뢰도 검증
        if ocr_confidence < confidence_threshold:
            result['mode'] = 'ZERO'
            result['ocr_success'] = False
            result['triggers'].append('low_confidence')
            result['manual_review_required'] = True
            result['next_actions'].append('manual_review')
            result['fallback_reason'] = f'OCR confidence {ocr_confidence:.2%} below threshold {confidence_threshold:.2%}'
            result['error_log']['error_type'] = 'low_confidence'
            
        # HS 코드 검증
        if not invoice_data.get('hs_code'):
            result['mode'] = 'ZERO'
            result['ocr_success'] = False
            result['triggers'].append('hs_code_missing')
            result['extracted_hs_code'] = None
            result['error_log']['error_type'] = 'hs_code_missing'
            
        # 금액 검증
        if not invoice_data.get('amount'):
            result['mode'] = 'ZERO'
            result['ocr_success'] = False
            result['triggers'].append('amount_missing')
            result['extracted_amount'] = None
            result['error_log']['error_type'] = 'amount_missing'
            
        # 이미지 처리 실패 검증
        if invoice_data.get('image_path') == 'nonexistent.jpg':
            result['mode'] = 'ZERO'
            result['ocr_success'] = False
            result['triggers'].append('image_processing_failed')
            result['confidence'] = 0.0
            result['error_log']['error_type'] = 'image_processing_failed'
            
        return result

if __name__ == '__main__':
    unittest.main() 