"""
📋 FANR 규정 준수 검증 모듈 (MACHO-GPT TDD v3.5)
Samsung C&T · ADNOC · DSV Partnership

TDD Green Phase: 최소 구현으로 테스트 통과
"""

from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd


def validate_fanr_compliance(invoice_data: Dict) -> Dict:
    """
    FANR 규정 준수 검증 함수
    
    Args:
        invoice_data: 송장 데이터 딕셔너리
        
    Returns:
        dict: {
            'compliance': bool,
            'confidence': float,
            'fanr_approval_valid': bool,
            'regulatory_status': str,
            'validation_flags': list,
            'validation_errors': list,
            'trigger_zero_mode': bool,
            'special_handling_required': bool
        }
    """
    # 기본 결과 구조
    result = {
        'compliance': False,
        'confidence': 0.0,
        'fanr_approval_valid': False,
        'regulatory_status': 'NON_COMPLIANT',
        'validation_flags': [],
        'validation_errors': [],
        'trigger_zero_mode': False,
        'special_handling_required': False
    }
    
    # FANR 승인번호 확인
    fanr_approval_no = invoice_data.get('FANR_Approval_No')
    if not fanr_approval_no:
        result['validation_errors'].append('MISSING_FANR_APPROVAL')
        result['confidence'] = 0.85  # < 0.95
        return result
    
    # FANR 승인 만료일 확인
    fanr_expiry_date = invoice_data.get('FANR_Expiry_Date')
    if fanr_expiry_date:
        try:
            expiry_date = datetime.strptime(fanr_expiry_date, '%Y-%m-%d')
            if expiry_date < datetime.now():
                result['validation_errors'].append('FANR_APPROVAL_EXPIRED')
                result['regulatory_status'] = 'EXPIRED'
                result['confidence'] = 0.80  # < 0.95
                return result
        except ValueError:
            result['validation_errors'].append('INVALID_EXPIRY_DATE')
            result['confidence'] = 0.75  # < 0.95
            return result
    
    # 핵물질 포함 여부 확인
    nuclear_material = invoice_data.get('Nuclear_Material', 'No')
    if nuclear_material.lower() == 'yes':
        result['trigger_zero_mode'] = True
        result['special_handling_required'] = True
        result['regulatory_status'] = 'NUCLEAR_MATERIAL_DETECTED'
        result['validation_flags'].append('NUCLEAR_MATERIAL_HANDLING')
    else:
        result['regulatory_status'] = 'COMPLIANT'
        result['validation_flags'].append('FANR_PASSED')
    
    # 모든 검증 통과 시
    result['compliance'] = True
    result['confidence'] = 0.95  # ≥ 0.95
    result['fanr_approval_valid'] = True
    
    return result


class FANRComplianceValidator:
    """
    FANR 규정 준수 검증기 클래스
    LATTICE 모드 컨테이너 적재 최적화와 연동
    """
    
    def __init__(self, confidence_threshold: float = 0.95):
        """
        초기화
        
        Args:
            confidence_threshold: 신뢰도 임계값 (기본값: 0.95)
        """
        self.confidence_threshold = confidence_threshold
        self.validation_history = []
        
    def validate_batch(self, invoice_list: List[Dict]) -> Dict:
        """
        배치 송장 데이터 FANR 규정 준수 검증
        
        Args:
            invoice_list: 송장 데이터 리스트
            
        Returns:
            dict: 배치 검증 결과
        """
        results = []
        compliant_count = 0
        
        for invoice in invoice_list:
            result = validate_fanr_compliance(invoice)
            results.append(result)
            
            if result['compliance']:
                compliant_count += 1
                
        batch_result = {
            'total_invoices': len(invoice_list),
            'compliant_count': compliant_count,
            'compliance_rate': compliant_count / len(invoice_list) if invoice_list else 0,
            'results': results,
            'batch_confidence': sum(r['confidence'] for r in results) / len(results) if results else 0
        }
        
        return batch_result
    
    def get_validation_summary(self) -> Dict:
        """
        검증 요약 정보 반환
        
        Returns:
            dict: 검증 요약 통계
        """
        if not self.validation_history:
            return {
                'total_validations': 0,
                'average_confidence': 0.0,
                'compliance_rate': 0.0
            }
        
        total_validations = len(self.validation_history)
        compliant_validations = sum(1 for v in self.validation_history if v['compliance'])
        average_confidence = sum(v['confidence'] for v in self.validation_history) / total_validations
        
        return {
            'total_validations': total_validations,
            'average_confidence': average_confidence,
            'compliance_rate': compliant_validations / total_validations
        } 