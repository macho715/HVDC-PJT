import pytest
import pandas as pd
from datetime import datetime
from pathlib import Path
import sys
import os

# Add the current directory to the path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class TestFinalReporter:
    """
    MACHO-GPT 최종 리포터 생성 테스트
    
    TDD Cycle: Red → Green → Refactor
    물류 도메인 특화 테스트
    """
    
    def test_final_reporter_should_generate_integrated_monthly_report(self):
        """
        최종 리포터가 통합 월별 리포트를 생성해야 함
        
        Given: MACHO 통합 데이터와 설정 파일
        When: 최종 리포터 실행
        Then: 통합 월별 리포트 Excel 파일 생성
        """
        # Given
        test_data = {
            'SQM_STACK': [
                {'date': '2024-01-01', 'sqm': 100, 'stack_height': 2.5},
                {'date': '2024-01-02', 'sqm': 150, 'stack_height': 3.0}
            ],
            'WH_HANDLING': [
                {'date': '2024-01-01', 'wh_handling': 1, 'cost': 1000},
                {'date': '2024-01-02', 'wh_handling': 2, 'cost': 2000}
            ]
        }
        
        # When
        from final_reporter import FinalReporter
        reporter = FinalReporter(confidence_threshold=0.95)
        result = reporter.generate_integrated_monthly_report(test_data)
        
        # Then
        assert result is not None
        assert result['status'] == 'SUCCESS'
        assert result['confidence'] >= 0.95
        assert 'output_file' in result
        assert result['output_file'].endswith('.xlsx')
        
    def test_final_reporter_should_validate_fanr_compliance(self):
        """
        최종 리포터가 FANR 규정 준수를 검증해야 함
        
        Given: 규제 요구사항 데이터
        When: FANR 규정 검증 실행
        Then: 규정 준수 상태 반환
        """
        # Given
        compliance_data = {
            'pressure_limit': 4.0,  # t/m²
            'safety_margin': 0.2,
            'certificate_status': 'VALID'
        }
        
        # When
        from final_reporter import FinalReporter
        reporter = FinalReporter()
        result = reporter.validate_fanr_compliance(compliance_data)
        
        # Then
        assert result is not None
        assert result['compliance_status'] == 'PASSED'
        assert result['confidence'] >= 0.95
        
    def test_final_reporter_should_include_kpi_dashboard(self):
        """
        최종 리포터가 KPI 대시보드를 포함해야 함
        
        Given: 물류 KPI 데이터
        When: KPI 대시보드 생성
        Then: 대시보드 요소들이 포함된 리포트 생성
        """
        # Given
        kpi_data = {
            'success_rate': 0.96,
            'processing_time': 2.5,  # seconds
            'error_rate': 0.04,
            'utilization_rate': 0.87
        }
        
        # When
        from final_reporter import FinalReporter
        reporter = FinalReporter()
        result = reporter.generate_kpi_dashboard(kpi_data)
        
        # Then
        assert result is not None
        assert 'dashboard_elements' in result
        assert len(result['dashboard_elements']) > 0
        assert result['confidence'] >= 0.95
        
    def test_final_reporter_should_handle_containment_mode_switching(self):
        """
        최종 리포터가 containment mode 전환을 처리해야 함
        
        Given: 오류 발생 시나리오
        When: 신뢰도 임계값 미달
        Then: ZERO 모드로 전환
        """
        # Given
        error_scenario = {
            'current_mode': 'LATTICE',
            'confidence': 0.80,  # Below threshold
            'error_type': 'OCR_CONFIDENCE_LOW'
        }
        
        # When
        from final_reporter import FinalReporter
        reporter = FinalReporter()
        result = reporter.handle_error_scenario(error_scenario)
        
        # Then
        assert result is not None
        assert result['mode_switch'] == 'ZERO'
        assert result['fallback_activated'] == True
        
    def test_final_reporter_should_recommend_next_commands(self):
        """
        최종 리포터가 다음 명령어를 추천해야 함
        
        Given: 리포트 생성 완료
        When: 명령어 추천 요청
        Then: 3개 이상의 관련 명령어 추천
        """
        # Given
        report_result = {
            'status': 'SUCCESS',
            'report_type': 'INTEGRATED_MONTHLY',
            'confidence': 0.97
        }
        
        # When
        from final_reporter import FinalReporter
        reporter = FinalReporter()
        result = reporter.recommend_next_commands(report_result)
        
        # Then
        assert result is not None
        assert 'next_cmds' in result
        assert len(result['next_cmds']) >= 3
        assert all(cmd.startswith('/') for cmd in result['next_cmds']) 