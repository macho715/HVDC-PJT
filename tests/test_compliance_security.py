"""
Compliance & Security Tests
Phase 5: Compliance & Security Tests - TDD Cycle

Tests FANR/MOIAT compliance, PII protection, audit trail, and security boundaries
for MACHO-GPT logistics system.
"""

import pytest
import pandas as pd
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from unittest.mock import Mock, patch, MagicMock
import hashlib
import re

# Configure logging for MACHO-GPT
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ComplianceData:
    """규정 준수 데이터 클래스"""
    certification_number: str
    expiry_date: str
    compliance_score: float
    regulatory_body: str  # 'FANR' or 'MOIAT'
    audit_trail: List[Dict[str, Any]]

@dataclass
class PIIData:
    """개인정보 데이터 클래스"""
    data_type: str  # 'invoice', 'vessel', 'crew', 'customer'
    sensitive_fields: List[str]
    encryption_status: bool
    access_level: str  # 'public', 'internal', 'restricted', 'confidential'

class ComplianceSecurityValidator:
    """규정 준수 및 보안 검증 클래스"""
    
    # 규정 임계값 상수
    FANR_COMPLIANCE_THRESHOLD = 0.95
    MOIAT_COMPLIANCE_THRESHOLD = 0.90
    PII_ENCRYPTION_REQUIRED = True
    AUDIT_RETENTION_DAYS = 365 * 7  # 7년
    
    def __init__(self, mode: str = "COST-GUARD"):
        """
        규정 준수 및 보안 검증기 초기화
        
        Args:
            mode: 현재 containment mode
        """
        self.mode = mode
        self.confidence_threshold = 0.95
        self.audit_log = []
        
    def validate_fanr_certification(self, compliance_data: ComplianceData) -> Dict[str, Any]:
        """
        FANR 인증 검증
        
        Args:
            compliance_data: 규정 준수 데이터
            
        Returns:
            Dict: FANR 인증 검증 결과
        """
        try:
            # FANR 규정 검증
            if compliance_data.regulatory_body != 'FANR':
                return {
                    'status': 'ERROR',
                    'error': 'Invalid regulatory body for FANR validation',
                    'confidence': 0.0,
                    'mode': self.mode
                }
            
            # 인증번호 형식 검증
            if not re.match(r'^FANR-\d{4}-\d{3}$', compliance_data.certification_number):
                return {
                    'status': 'FAIL',
                    'error': 'Invalid FANR certification number format',
                    'confidence': 0.0,
                    'mode': self.mode
                }
            
            # 만료일 검증
            expiry_date = datetime.strptime(compliance_data.expiry_date, '%Y-%m-%d')
            if expiry_date < datetime.now():
                return {
                    'status': 'FAIL',
                    'error': 'FANR certification has expired',
                    'confidence': 0.0,
                    'mode': self.mode
                }
            
            # 준수 점수 검증
            if compliance_data.compliance_score < self.FANR_COMPLIANCE_THRESHOLD:
                return {
                    'status': 'FAIL',
                    'error': f'FANR compliance score below threshold: {compliance_data.compliance_score}',
                    'confidence': compliance_data.compliance_score,
                    'mode': 'ZERO'  # 준수 실패 시 ZERO 모드
                }
            
            # 감사 로그 생성
            audit_entry = {
                'timestamp': datetime.now().isoformat(),
                'certification_number': compliance_data.certification_number,
                'validation_result': 'PASS',
                'compliance_score': compliance_data.compliance_score,
                'mode': self.mode
            }
            self.audit_log.append(audit_entry)
            
            return {
                'status': 'SUCCESS',
                'certification_number': compliance_data.certification_number,
                'compliance_score': compliance_data.compliance_score,
                'expiry_date': compliance_data.expiry_date,
                'confidence': 0.95,
                'mode': self.mode,
                'audit_trail': audit_entry
            }
            
        except Exception as e:
            logger.error(f"FANR certification validation error: {e}")
            return {
                'status': 'ERROR',
                'error': str(e),
                'confidence': 0.0,
                'mode': self.mode
            }
    
    def validate_moiat_regulatory_compliance(self, compliance_data: ComplianceData) -> Dict[str, Any]:
        """
        MOIAT 규정 준수 검증
        
        Args:
            compliance_data: 규정 준수 데이터
            
        Returns:
            Dict: MOIAT 규정 준수 검증 결과
        """
        try:
            # MOIAT 규정 검증
            if compliance_data.regulatory_body != 'MOIAT':
                return {
                    'status': 'ERROR',
                    'error': 'Invalid regulatory body for MOIAT validation',
                    'confidence': 0.0,
                    'mode': self.mode
                }
            
            # 인증번호 형식 검증 (MOIAT 형식)
            if not re.match(r'^MOIAT-\d{4}-\d{4}$', compliance_data.certification_number):
                return {
                    'status': 'FAIL',
                    'error': 'Invalid MOIAT certification number format',
                    'confidence': 0.0,
                    'mode': self.mode
                }
            
            # 만료일 검증
            expiry_date = datetime.strptime(compliance_data.expiry_date, '%Y-%m-%d')
            if expiry_date < datetime.now():
                return {
                    'status': 'FAIL',
                    'error': 'MOIAT certification has expired',
                    'confidence': 0.0,
                    'mode': self.mode
                }
            
            # 준수 점수 검증 (MOIAT는 FANR보다 낮은 임계값)
            if compliance_data.compliance_score < self.MOIAT_COMPLIANCE_THRESHOLD:
                return {
                    'status': 'FAIL',
                    'error': f'MOIAT compliance score below threshold: {compliance_data.compliance_score}',
                    'confidence': compliance_data.compliance_score,
                    'mode': 'ZERO'
                }
            
            # 감사 로그 생성
            audit_entry = {
                'timestamp': datetime.now().isoformat(),
                'certification_number': compliance_data.certification_number,
                'validation_result': 'PASS',
                'compliance_score': compliance_data.compliance_score,
                'mode': self.mode
            }
            self.audit_log.append(audit_entry)
            
            return {
                'status': 'SUCCESS',
                'certification_number': compliance_data.certification_number,
                'compliance_score': compliance_data.compliance_score,
                'expiry_date': compliance_data.expiry_date,
                'confidence': 0.92,
                'mode': self.mode,
                'audit_trail': audit_entry
            }
            
        except Exception as e:
            logger.error(f"MOIAT compliance validation error: {e}")
            return {
                'status': 'ERROR',
                'error': str(e),
                'confidence': 0.0,
                'mode': self.mode
            }
    
    def validate_pii_data_protection(self, pii_data: PIIData, data_content: Dict[str, Any]) -> Dict[str, Any]:
        """
        PII 데이터 보호 검증
        
        Args:
            pii_data: PII 데이터 정보
            data_content: 실제 데이터 내용
            
        Returns:
            Dict: PII 보호 검증 결과
        """
        try:
            # 암호화 상태 검증
            if not pii_data.encryption_status:
                return {
                    'status': 'FAIL',
                    'error': 'PII data encryption is required',
                    'confidence': 0.0,
                    'mode': 'ZERO'
                }
            
            # 민감 필드 검증
            sensitive_fields_found = []
            for field in pii_data.sensitive_fields:
                if field in data_content:
                    # 민감 정보 패턴 검증
                    if self._contains_sensitive_pattern(data_content[field]):
                        sensitive_fields_found.append(field)
            
            # 접근 레벨 검증
            if pii_data.access_level not in ['public', 'internal', 'restricted', 'confidential']:
                return {
                    'status': 'FAIL',
                    'error': 'Invalid access level for PII data',
                    'confidence': 0.0,
                    'mode': self.mode
                }
            
            # 민감 정보 노출 검증
            if sensitive_fields_found and pii_data.access_level == 'public':
                return {
                    'status': 'FAIL',
                    'error': f'Sensitive fields exposed in public access: {sensitive_fields_found}',
                    'confidence': 0.0,
                    'mode': 'ZERO'
                }
            
            # 감사 로그 생성
            audit_entry = {
                'timestamp': datetime.now().isoformat(),
                'data_type': pii_data.data_type,
                'access_level': pii_data.access_level,
                'sensitive_fields_count': len(sensitive_fields_found),
                'encryption_status': pii_data.encryption_status,
                'validation_result': 'PASS',
                'mode': self.mode
            }
            self.audit_log.append(audit_entry)
            
            return {
                'status': 'SUCCESS',
                'data_type': pii_data.data_type,
                'access_level': pii_data.access_level,
                'encryption_status': pii_data.encryption_status,
                'sensitive_fields_protected': len(sensitive_fields_found) == 0,
                'confidence': 0.95,
                'mode': self.mode,
                'audit_trail': audit_entry
            }
            
        except Exception as e:
            logger.error(f"PII protection validation error: {e}")
            return {
                'status': 'ERROR',
                'error': str(e),
                'confidence': 0.0,
                'mode': self.mode
            }
    
    def generate_audit_trail(self, operation: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        감사 로그 생성
        
        Args:
            operation: 수행된 작업
            data: 관련 데이터
            
        Returns:
            Dict: 감사 로그 정보
        """
        try:
            audit_entry = {
                'timestamp': datetime.now().isoformat(),
                'operation': operation,
                'user_id': data.get('user_id', 'system'),
                'data_hash': self._generate_data_hash(data),
                'mode': self.mode,
                'retention_days': self.AUDIT_RETENTION_DAYS
            }
            
            self.audit_log.append(audit_entry)
            
            return {
                'status': 'SUCCESS',
                'audit_id': len(self.audit_log),
                'audit_entry': audit_entry,
                'confidence': 0.95,
                'mode': self.mode
            }
            
        except Exception as e:
            logger.error(f"Audit trail generation error: {e}")
            return {
                'status': 'ERROR',
                'error': str(e),
                'confidence': 0.0,
                'mode': self.mode
            }
    
    def enforce_security_boundary(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        보안 경계 강제
        
        Args:
            request_data: 요청 데이터
            
        Returns:
            Dict: 보안 검증 결과
        """
        try:
            # 권한 검증
            user_role = request_data.get('user_role', 'guest')
            required_role = request_data.get('required_role', 'user')
            
            if not self._has_permission(user_role, required_role):
                return {
                    'status': 'DENIED',
                    'error': f'Insufficient permissions: {user_role} cannot access {required_role} level',
                    'confidence': 0.0,
                    'mode': 'ZERO'
                }
            
            # 데이터 무결성 검증
            if not self._validate_data_integrity(request_data):
                return {
                    'status': 'FAIL',
                    'error': 'Data integrity validation failed',
                    'confidence': 0.0,
                    'mode': 'ZERO'
                }
            
            # 세션 검증
            session_valid = request_data.get('session_valid', True)
            if not session_valid:
                return {
                    'status': 'DENIED',
                    'error': 'Invalid or expired session',
                    'confidence': 0.0,
                    'mode': 'ZERO'
                }
            
            # 감사 로그 생성
            audit_entry = {
                'timestamp': datetime.now().isoformat(),
                'user_role': user_role,
                'operation': request_data.get('operation', 'unknown'),
                'security_check': 'PASS',
                'mode': self.mode
            }
            self.audit_log.append(audit_entry)
            
            return {
                'status': 'SUCCESS',
                'user_role': user_role,
                'permissions_granted': True,
                'data_integrity': True,
                'session_valid': True,
                'confidence': 0.95,
                'mode': self.mode,
                'audit_trail': audit_entry
            }
            
        except Exception as e:
            logger.error(f"Security boundary enforcement error: {e}")
            return {
                'status': 'ERROR',
                'error': str(e),
                'confidence': 0.0,
                'mode': self.mode
            }
    
    # Helper methods
    def _contains_sensitive_pattern(self, text: str) -> bool:
        """민감 정보 패턴 검증"""
        sensitive_patterns = [
            r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',  # 신용카드
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # 이메일
            r'\b\d{10,11}\b'  # 전화번호
        ]
        
        for pattern in sensitive_patterns:
            if re.search(pattern, str(text)):
                return True
        return False
    
    def _generate_data_hash(self, data: Dict[str, Any]) -> str:
        """데이터 해시 생성"""
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def _has_permission(self, user_role: str, required_role: str) -> bool:
        """권한 검증"""
        role_hierarchy = {
            'guest': 0,
            'user': 1,
            'admin': 2,
            'super_admin': 3
        }
        
        user_level = role_hierarchy.get(user_role, 0)
        required_level = role_hierarchy.get(required_role, 0)
        
        return user_level >= required_level
    
    def _validate_data_integrity(self, data: Dict[str, Any]) -> bool:
        """데이터 무결성 검증"""
        # 기본적인 데이터 무결성 검증
        required_fields = ['user_id', 'operation', 'timestamp']
        return all(field in data for field in required_fields)


class TestComplianceSecurity:
    """규정 준수 및 보안 테스트 클래스"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 설정"""
        self.validator = ComplianceSecurityValidator(mode="COST-GUARD")
        
    def test_fanr_certification_validation_success(self):
        """FANR 인증 검증 성공 테스트"""
        # Given: 유효한 FANR 인증 데이터
        compliance_data = ComplianceData(
            certification_number='FANR-2025-001',
            expiry_date='2025-12-31',
            compliance_score=0.98,
            regulatory_body='FANR',
            audit_trail=[]
        )
        
        # When: FANR 인증 검증 실행
        result = self.validator.validate_fanr_certification(compliance_data)
        
        # Then: 검증이 성공해야 함
        assert result['status'] == 'SUCCESS'
        assert result['certification_number'] == 'FANR-2025-001'
        assert result['compliance_score'] == 0.98
        assert result['confidence'] >= 0.95
        assert 'audit_trail' in result
        
    def test_fanr_certification_validation_failure(self):
        """FANR 인증 검증 실패 테스트"""
        # Given: 만료된 FANR 인증 데이터
        compliance_data = ComplianceData(
            certification_number='FANR-2024-001',
            expiry_date='2024-12-31',
            compliance_score=0.85,
            regulatory_body='FANR',
            audit_trail=[]
        )
        
        # When: FANR 인증 검증 실행
        result = self.validator.validate_fanr_certification(compliance_data)
        
        # Then: 검증이 실패해야 함
        assert result['status'] == 'FAIL'
        assert 'expired' in result['error'].lower()
        assert result['confidence'] == 0.0
        
    def test_moiat_regulatory_compliance_success(self):
        """MOIAT 규정 준수 검증 성공 테스트"""
        # Given: 유효한 MOIAT 인증 데이터
        compliance_data = ComplianceData(
            certification_number='MOIAT-2025-0001',
            expiry_date='2025-12-31',
            compliance_score=0.92,
            regulatory_body='MOIAT',
            audit_trail=[]
        )
        
        # When: MOIAT 규정 준수 검증 실행
        result = self.validator.validate_moiat_regulatory_compliance(compliance_data)
        
        # Then: 검증이 성공해야 함
        assert result['status'] == 'SUCCESS'
        assert result['certification_number'] == 'MOIAT-2025-0001'
        assert result['compliance_score'] == 0.92
        assert result['confidence'] >= 0.90
        assert 'audit_trail' in result
        
    def test_moiat_regulatory_compliance_failure(self):
        """MOIAT 규정 준수 검증 실패 테스트"""
        # Given: 준수하지 않는 MOIAT 데이터
        compliance_data = ComplianceData(
            certification_number='MOIAT-2025-0001',
            expiry_date='2025-12-31',
            compliance_score=0.85,  # 임계값 미달
            regulatory_body='MOIAT',
            audit_trail=[]
        )
        
        # When: MOIAT 규정 준수 검증 실행
        result = self.validator.validate_moiat_regulatory_compliance(compliance_data)
        
        # Then: 검증이 실패해야 함
        assert result['status'] == 'FAIL'
        assert 'threshold' in result['error'].lower()
        assert result['mode'] == 'ZERO'
        
    def test_pii_data_protection_success(self):
        """PII 데이터 보호 검증 성공 테스트"""
        # Given: 보호된 PII 데이터
        pii_data = PIIData(
            data_type='invoice',
            sensitive_fields=['customer_email', 'phone_number'],
            encryption_status=True,
            access_level='restricted'
        )
        data_content = {
            'invoice_number': 'INV-001',
            'amount': 15000.0,
            'customer_email': 'customer@example.com',
            'phone_number': '123-456-7890'
        }
        
        # When: PII 데이터 보호 검증 실행
        result = self.validator.validate_pii_data_protection(pii_data, data_content)
        
        # Then: 검증이 성공해야 함
        assert result['status'] == 'SUCCESS'
        assert result['encryption_status'] == True
        assert result['access_level'] == 'restricted'
        assert result['confidence'] >= 0.95
        assert 'audit_trail' in result
        
    def test_pii_data_protection_failure(self):
        """PII 데이터 보호 검증 실패 테스트"""
        # Given: 암호화되지 않은 PII 데이터
        pii_data = PIIData(
            data_type='invoice',
            sensitive_fields=['customer_email'],
            encryption_status=False,  # 암호화 안됨
            access_level='public'
        )
        data_content = {
            'invoice_number': 'INV-001',
            'customer_email': 'customer@example.com'
        }
        
        # When: PII 데이터 보호 검증 실행
        result = self.validator.validate_pii_data_protection(pii_data, data_content)
        
        # Then: 검증이 실패해야 함
        assert result['status'] == 'FAIL'
        assert 'encryption' in result['error'].lower()
        assert result['mode'] == 'ZERO'
        
    def test_audit_trail_generation_success(self):
        """감사 로그 생성 성공 테스트"""
        # Given: 작업 데이터
        operation = 'invoice_validation'
        data = {
            'user_id': 'user123',
            'invoice_number': 'INV-001',
            'amount': 15000.0
        }
        
        # When: 감사 로그 생성 실행
        result = self.validator.generate_audit_trail(operation, data)
        
        # Then: 감사 로그가 생성되어야 함
        assert result['status'] == 'SUCCESS'
        assert result['audit_entry']['operation'] == operation
        assert result['audit_entry']['user_id'] == 'user123'
        assert 'data_hash' in result['audit_entry']
        assert result['confidence'] >= 0.95
        
    def test_security_boundary_enforcement_success(self):
        """보안 경계 강제 성공 테스트"""
        # Given: 유효한 요청 데이터
        request_data = {
            'user_role': 'admin',
            'required_role': 'user',
            'operation': 'data_access',
            'session_valid': True,
            'user_id': 'admin123',
            'timestamp': datetime.now().isoformat()  # 필수 필드 추가
        }
        
        # When: 보안 경계 강제 실행
        result = self.validator.enforce_security_boundary(request_data)
        
        # Then: 보안 검증이 성공해야 함
        assert result['status'] == 'SUCCESS'
        assert result['permissions_granted'] == True
        assert result['data_integrity'] == True
        assert result['session_valid'] == True
        assert result['confidence'] >= 0.95
        assert 'audit_trail' in result
        
    def test_security_boundary_enforcement_failure(self):
        """보안 경계 강제 실패 테스트"""
        # Given: 권한이 부족한 요청 데이터
        request_data = {
            'user_role': 'guest',
            'required_role': 'admin',
            'operation': 'admin_access',
            'session_valid': True,
            'user_id': 'guest123'
        }
        
        # When: 보안 경계 강제 실행
        result = self.validator.enforce_security_boundary(request_data)
        
        # Then: 보안 검증이 실패해야 함
        assert result['status'] == 'DENIED'
        assert 'permissions' in result['error'].lower()
        assert result['mode'] == 'ZERO'


if __name__ == "__main__":
    # 테스트 실행
    pytest.main([__file__, "-v"]) 