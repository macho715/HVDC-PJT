#!/usr/bin/env python3
"""
MACHO-GPT v3.4-mini 검증 리포트 생성 실행 스크립트
/generate-validation-report 명령어 실행

사용법:
python run_validation_report.py [invoice_file] [warehouse_file]

예시:
python run_validation_report.py "../data/HVDC_WAREHOUSE_INVOICE_CLEANED_20250709_201121.xlsx" "../data/HVDC WAREHOUSE_HITACHI(HE).xlsx"
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from src.generate_validation_report import generate_validation_report, ValidationConfig

def main():
    """메인 실행 함수"""
    print("🚀 MACHO-GPT v3.4-mini 검증 리포트 생성 시스템")
    print("HVDC PROJECT | Samsung C&T | ADNOC·DSV Partnership")
    print("=" * 70)
    
    # 명령행 인자 처리
    if len(sys.argv) == 3:
        invoice_file = sys.argv[1]
        warehouse_file = sys.argv[2]
    else:
        # 기본 파일 경로 사용
        invoice_file = "../data/HVDC_WAREHOUSE_INVOICE_CLEANED_20250709_201121.xlsx"
        warehouse_file = "../data/HVDC WAREHOUSE_HITACHI(HE).xlsx"
        
        print("📋 기본 파일 경로 사용:")
        print(f"  청구서: {invoice_file}")
        print(f"  창고: {warehouse_file}")
        print("\n💡 다른 파일을 사용하려면:")
        print("  python run_validation_report.py [invoice_file] [warehouse_file]")
        print()
    
    # 파일 존재 확인
    if not os.path.exists(invoice_file):
        print(f"❌ 청구서 파일을 찾을 수 없습니다: {invoice_file}")
        print("\n📁 사용 가능한 파일:")
        data_dir = Path("../data")
        if data_dir.exists():
            for file in data_dir.glob("*.xlsx"):
                print(f"  - {file}")
        return
    
    if not os.path.exists(warehouse_file):
        print(f"❌ 창고 파일을 찾을 수 없습니다: {warehouse_file}")
        print("\n📁 사용 가능한 파일:")
        data_dir = Path("../data")
        if data_dir.exists():
            for file in data_dir.glob("*.xlsx"):
                print(f"  - {file}")
        return
    
    print(f"✅ 파일 확인 완료")
    print(f"  📄 청구서: {invoice_file}")
    print(f"  🏭 창고: {warehouse_file}")
    print()
    
    # 검증 설정
    config = ValidationConfig(
        confidence_threshold=0.95,
        amount_tolerance=0.01,
        quantity_tolerance=0.05,
        fanr_compliance_required=True,
        moiat_compliance_required=True,
        generate_pdf=True,
        generate_excel=True,
        generate_rdf=True
    )
    
    try:
        print("🔍 검증 리포트 생성 시작...")
        start_time = datetime.now()
        
        # 검증 리포트 생성
        result = generate_validation_report(invoice_file, warehouse_file, config)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # 결과 출력
        print("\n" + "="*80)
        print("📋 MACHO-GPT 검증 리포트 생성 결과")
        print("="*80)
        
        if result.get('status') == 'ERROR':
            print(f"❌ 오류 발생: {result.get('error_message', '알 수 없는 오류')}")
            print("\n🔧 권고사항:")
            for rec in result.get('recommendations', []):
                print(f"  • {rec}")
            return
        
        # 검증 결과 요약
        overall_validation = result['validation_results']['overall_validation']
        print(f"📊 전체 검증 점수: {overall_validation['total_score']:.3f}")
        print(f"🏆 등급: {overall_validation['grade']}")
        print(f"✅ 상태: {overall_validation['status']}")
        print(f"⏱️  처리 시간: {processing_time:.2f}초")
        
        # 컴포넌트별 점수
        print(f"\n📈 컴포넌트별 점수:")
        component_scores = overall_validation['component_scores']
        for component, score in component_scores.items():
            status_icon = "✅" if score >= 0.9 else "⚠️" if score >= 0.8 else "❌"
            print(f"  {status_icon} {component}: {score:.3f}")
        
        # 생성된 파일
        print(f"\n📄 생성된 파일:")
        for file_type, file_path in result['generated_files'].items():
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
            print(f"  📋 {file_type}: {file_path} ({file_size:.2f} MB)")
        
        # 권고사항
        if result.get('recommendations'):
            print(f"\n💡 권고사항:")
            for i, rec in enumerate(result['recommendations'], 1):
                print(f"  {i}. {rec}")
        
        # 다음 액션
        print(f"\n🔧 추천 명령어:")
        for cmd in result.get('next_actions', []):
            print(f"  {cmd}")
        
        print("="*80)
        print("✅ 검증 리포트 생성 완료!")
        
        # MACHO-GPT 표준 응답
        print(f"\n📊 **Status:** {overall_validation['total_score']:.0%} | PRIME | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"\n❌ 검증 리포트 생성 실패: {e}")
        import traceback
        traceback.print_exc()
        
        print(f"\n🔄 오류 복구 시도 중...")
        try:
            # 기본 설정으로 재시도
            basic_config = ValidationConfig(
                confidence_threshold=0.8,  # 임계값 완화
                generate_pdf=False,  # PDF 생성 비활성화
                generate_rdf=False   # RDF 생성 비활성화
            )
            
            result = generate_validation_report(invoice_file, warehouse_file, basic_config)
            print(f"✅ 복구 성공: {result['generated_files'].get('excel_detailed', 'N/A')}")
        except Exception as recovery_error:
            print(f"❌ 복구 실패: {recovery_error}")

if __name__ == "__main__":
    main() 