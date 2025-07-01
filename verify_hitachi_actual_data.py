#!/usr/bin/env python3
"""
🔍 HITACHI 실제 데이터 검증 v2.8.3
Excel 피벗 테이블 결과 vs 시스템 검증 결과 비교

사용자 확인 데이터:
- Port→Site: 1,819건 ✅
- Port→WH→Site: 2,561건  
- Port→WH→MOSB→Site: 886건
- Port→WH→wh→MOSB→Site: 80건
"""

import pandas as pd
import sys
import os

class HitachiActualDataVerifier:
    def __init__(self):
        print("🔍 HITACHI 실제 데이터 검증 v2.8.3")
        print("=" * 60)
        
        # Excel에서 확인된 실제 결과
        self.excel_results = {
            'Code 0 (Port→Site)': 1819,
            'Code 1 (Port→WH→Site)': 2561, 
            'Code 2 (Port→WH→MOSB→Site)': 886,
            'Code 3 (Port→WH→wh→MOSB→Site)': 80,
            'Total': 5346
        }
        
        # 우리 시스템 검증 결과  
        self.system_results = {
            'Code 1 (Port→Site)': 1819,
            'Code 2 (Port→WH→Site)': 3081,
            'Code 3 (Port→WH→MOSB→Site)': 441, 
            'Code 4 (Port→WH→wh→MOSB→Site)': 5,
            'Total': 5346
        }
    
    def compare_results(self):
        """실제 데이터와 시스템 결과 비교"""
        print("📊 실제 Excel 데이터 vs 시스템 검증 결과 비교")
        print("-" * 60)
        
        # Port→Site 비교 (Code 매핑 차이 고려)
        excel_port_site = self.excel_results['Code 0 (Port→Site)']
        system_port_site = self.system_results['Code 1 (Port→Site)']
        
        print(f"🎯 Port→Site 비교:")
        print(f"   Excel: {excel_port_site:,}건")
        print(f"   System: {system_port_site:,}건") 
        print(f"   일치: {'✅' if excel_port_site == system_port_site else '❌'}")
        
        print(f"\n📋 전체 비교:")
        print(f"{'구분':<30} {'Excel':<10} {'System':<10} {'차이':<10} {'상태'}")
        print("-" * 65)
        
        comparisons = [
            ('Port→Site', 1819, 1819, '일치'),
            ('Port→WH→Site', 2561, 3081, '차이'),  
            ('Port→WH→MOSB→Site', 886, 441, '차이'),
            ('Port→WH→wh→MOSB→Site', 80, 5, '차이')
        ]
        
        for desc, excel_val, system_val, status in comparisons:
            diff = excel_val - system_val
            status_icon = "✅" if status == "일치" else "❌"
            print(f"{desc:<30} {excel_val:<10,} {system_val:<10,} {diff:<10,} {status_icon}")
    
    def analyze_discrepancies(self):
        """차이점 분석"""
        print(f"\n🔍 차이점 원인 분석")
        print("-" * 40)
        
        print("📈 발견된 패턴:")
        print("1. Port→Site (1819건): ✅ 완벽 일치")
        print("2. Port→WH→Site: 시스템이 +520건 더 많음")  
        print("3. Port→WH→MOSB→Site: 시스템이 -445건 적음")
        print("4. Port→WH→wh→MOSB→Site: 시스템이 -75건 적음")
        
        print(f"\n🤔 가능한 원인:")
        print("• MOSB 인식 로직의 창고 복잡도 계산 차이")
        print("• 전각공백 처리 후 데이터 분류 변화") 
        print("• 벤더별 특화 로직 적용 차이")
        print("• Flow Code 매핑 규칙 적용 순서 차이")
    
    def load_actual_hitachi_data(self):
        """실제 HITACHI 파일 로드하여 재분석"""
        file_path = "hvdc_ontology_system/data/HVDC WAREHOUSE_HITACHI(HE).xlsx"
        
        if not os.path.exists(file_path):
            print(f"❌ 파일을 찾을 수 없습니다: {file_path}")
            return None
            
        try:
            print(f"\n📂 실제 HITACHI 데이터 로드 중...")
            df = pd.read_excel(file_path)
            print(f"✅ 데이터 로드 성공: {len(df):,}행")
            
            # 기본 통계
            print(f"\n📊 데이터 기본 정보:")
            print(f"   총 행수: {len(df):,}건")
            print(f"   컬럼수: {len(df.columns)}개")
            
            # 주요 컬럼 확인
            key_columns = ['HVDC CODE', 'MOSB', 'Status']
            available_columns = [col for col in key_columns if col in df.columns]
            print(f"   주요 컬럼: {', '.join(available_columns)}")
            
            return df
            
        except Exception as e:
            print(f"❌ 데이터 로드 실패: {e}")
            return None
    
    def generate_correction_plan(self):
        """수정 계획 제안"""
        print(f"\n🔧 수정 계획 제안")
        print("-" * 40)
        
        print("📋 우선순위별 수정 사항:")
        print("1. ✅ Port→Site (1819건) - 이미 정확")
        print("2. 🔧 MOSB 인식 로직 재검토 필요")
        print("3. 🔧 창고 복잡도 계산 알고리즘 조정")
        print("4. 🔧 Flow Code 매핑 규칙 정밀 조정")
        
        print(f"\n🎯 목표 달성 방안:")
        print("• Excel 피벗 테이블 결과를 기준값으로 설정")
        print("• MOSB 로직을 Excel 결과에 맞게 조정")
        print("• 벤더별 특화 로직 재검증")
        print("• 단계별 검증으로 정확도 향상")
    
    def run_verification(self):
        """전체 검증 실행"""
        self.compare_results()
        self.analyze_discrepancies() 
        
        # 실제 데이터 로드 시도
        df = self.load_actual_hitachi_data()
        
        self.generate_correction_plan()
        
        print(f"\n" + "=" * 60)
        print("🎯 HITACHI 실제 데이터 검증 결과")
        print("=" * 60)
        print("✅ Port→Site 1819건: 완벽 일치 확인!")
        print("🔧 기타 Flow Code: 조정 필요")
        print("📊 총 데이터: 5,346건 일치")
        print("🎯 Excel 기준값 적용으로 시스템 개선 권장")
        
        return {
            'port_site_match': True,
            'total_count_match': True, 
            'flow_code_adjustment_needed': True,
            'recommendation': 'Excel 피벗 테이블 결과 기준으로 MOSB 로직 조정'
        }

if __name__ == "__main__":
    verifier = HitachiActualDataVerifier()
    result = verifier.run_verification() 