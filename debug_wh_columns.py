#!/usr/bin/env python3
"""
🔍 창고 컬럼 인식 디버깅 스크립트
가이드 정규식이 실제 데이터에서 작동하는지 확인
"""

import pandas as pd
import re
import os

def test_warehouse_column_detection():
    """실제 Excel 파일에서 창고 컬럼 인식 테스트"""
    
    # 🆕 가이드 정규식
    WH_REGEX = re.compile(
        r'^(DSV\s*(Indoor|Outdoor|Al\s*Markaz|MZ[DP])|JDN\s*MZD|Hauler\s*Indoor|AAA\s{2,}Storage)$',
        flags=re.I
    )
    
    files = [
        'data/HVDC WAREHOUSE_HITACHI(HE).xlsx',
        'data/HVDC WAREHOUSE_SIMENSE(SIM).xlsx'
    ]
    
    for file_path in files:
        if not os.path.exists(file_path):
            print(f"❌ 파일 없음: {file_path}")
            continue
            
        print(f"\n📄 {file_path} 분석 중...")
        
        try:
            # Excel 파일 로드
            df = pd.read_excel(file_path)
            print(f"   📋 전체 컬럼 수: {len(df.columns)}개")
            
            # 모든 컬럼명 출력
            print("   🔍 전체 컬럼 목록:")
            for i, col in enumerate(df.columns):
                print(f"      {i+1:2d}. '{col}'")
            
            # 정규식 매칭 테스트
            matched_cols = []
            for col in df.columns:
                if WH_REGEX.match(col.strip()):
                    matched_cols.append(col)
            
            print(f"\n   ✅ 정규식 매칭 컬럼 ({len(matched_cols)}개):")
            for col in matched_cols:
                print(f"      - '{col}'")
            
            # DSV, MZP, AAA 키워드 검색
            print(f"\n   🔍 키워드별 컬럼 검색:")
            keywords = ['DSV', 'MZP', 'MZD', 'AAA', 'Hauler', 'JDN']
            for keyword in keywords:
                keyword_cols = [col for col in df.columns if keyword.upper() in col.upper()]
                print(f"      {keyword}: {keyword_cols}")
                
        except Exception as e:
            print(f"   ❌ 파일 로드 실패: {e}")

def test_regex_patterns():
    """개별 정규식 패턴 테스트"""
    print("\n🧪 정규식 패턴 개별 테스트")
    print("=" * 50)
    
    test_columns = [
        'DSV Indoor',
        'DSV Outdoor', 
        'DSV Al Markaz',
        'DSV MZP',
        'DSV MZD',
        'JDN MZD',
        'Hauler Indoor',
        'AAA  Storage',
        'AAA   Storage',
        'DSV MZP ',  # 뒤에 공백
        ' DSV Indoor',  # 앞에 공백
    ]
    
    WH_REGEX = re.compile(
        r'^(DSV\s*(Indoor|Outdoor|Al\s*Markaz|MZ[DP])|JDN\s*MZD|Hauler\s*Indoor|AAA\s{2,}Storage)$',
        flags=re.I
    )
    
    for col in test_columns:
        match = WH_REGEX.match(col.strip())
        status = "✅" if match else "❌"
        print(f"   {status} '{col}' → {match.group(0) if match else 'No match'}")

if __name__ == "__main__":
    print("🔍 HVDC 창고 컬럼 인식 디버깅")
    print("=" * 60)
    
    test_regex_patterns()
    test_warehouse_column_detection() 