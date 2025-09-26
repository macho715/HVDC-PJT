"""
SIMENSE 데이터 Pkg 컬럼 누락 문제 해결 스크립트
"""
import pandas as pd
import logging
from pathlib import Path

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def analyze_simense_pkg_issue():
    """SIMENSE 데이터의 Pkg 컬럼 문제 분석"""
    print("🔍 SIMENSE 데이터 Pkg 컬럼 문제 분석")
    print("=" * 60)
    
    # SIMENSE 데이터 로드
    simense_file = Path("data/HVDC WAREHOUSE_SIMENSE(SIM).xlsx")
    simense_data = pd.read_excel(simense_file, engine='openpyxl')
    
    print(f"📊 SIMENSE 데이터: {len(simense_data):,}건")
    
    # 1. Pkg 컬럼 존재 여부 확인
    if 'Pkg' in simense_data.columns:
        print("✅ Pkg 컬럼이 존재합니다!")
        pkg_sum = simense_data['Pkg'].sum()
        pkg_count = simense_data['Pkg'].count()
        print(f"📦 Pkg 합계: {pkg_sum:,}")
        print(f"📦 유효 데이터: {pkg_count:,}건")
    else:
        print("❌ Pkg 컬럼이 없습니다!")
        
        # 2. 대체 컬럼 찾기
        print("\n🔍 대체 컬럼 찾기:")
        possible_pkg_columns = ['Pkg', 'Package', 'Quantity', 'Qty', 'Packages', 'total handling', 'final handling']
        
        for col in possible_pkg_columns:
            if col in simense_data.columns:
                print(f"   ✅ {col}: {simense_data[col].sum():,}")
            else:
                print(f"   ❌ {col}: 없음")
        
        # 3. total handling 컬럼 확인
        if 'total handling' in simense_data.columns:
            total_handling_sum = simense_data['total handling'].sum()
            print(f"\n📦 total handling 합계: {total_handling_sum:,}")
            
            # 4. final handling 컬럼 확인
            if 'final handling' in simense_data.columns:
                final_handling_sum = simense_data['final handling'].sum()
                print(f"📦 final handling 합계: {final_handling_sum:,}")
        
        # 5. 데이터 샘플 확인
        print(f"\n📋 데이터 샘플 (수량 관련 컬럼):")
        sample_cols = ['total handling', 'final handling', 'minus']
        sample_data = simense_data[sample_cols].head(10)
        print(sample_data)

def fix_simense_pkg_column():
    """SIMENSE 데이터에 Pkg 컬럼 추가"""
    print("\n🔧 SIMENSE 데이터 Pkg 컬럼 수정")
    print("=" * 60)
    
    # SIMENSE 데이터 로드
    simense_file = Path("data/HVDC WAREHOUSE_SIMENSE(SIM).xlsx")
    simense_data = pd.read_excel(simense_file, engine='openpyxl')
    
    # Pkg 컬럼 생성 전략
    print("📋 Pkg 컬럼 생성 전략:")
    
    # 1. total handling을 Pkg로 사용
    if 'total handling' in simense_data.columns:
        simense_data['Pkg'] = simense_data['total handling'].fillna(1).astype(int)
        print(f"✅ total handling을 Pkg로 사용: {simense_data['Pkg'].sum():,}")
    else:
        # 2. final handling을 Pkg로 사용
        if 'final handling' in simense_data.columns:
            simense_data['Pkg'] = simense_data['final handling'].fillna(1).astype(int)
            print(f"✅ final handling을 Pkg로 사용: {simense_data['Pkg'].sum():,}")
        else:
            # 3. 기본값 1로 설정
            simense_data['Pkg'] = 1
            print(f"✅ 기본값 1로 Pkg 설정: {simense_data['Pkg'].sum():,}")
    
    # Vendor 컬럼 추가
    simense_data['Vendor'] = 'SIMENSE'
    simense_data['Source_File'] = 'SIMENSE(SIM)'
    
    # 수정된 데이터 저장
    fixed_file = Path("data/HVDC WAREHOUSE_SIMENSE(SIM)_FIXED.xlsx")
    simense_data.to_excel(fixed_file, index=False, engine='openpyxl')
    
    print(f"✅ 수정된 SIMENSE 데이터 저장: {fixed_file}")
    print(f"📊 총 데이터: {len(simense_data):,}건")
    print(f"📦 Pkg 합계: {simense_data['Pkg'].sum():,}")
    
    return simense_data

def test_combined_data_with_fixed_simense():
    """수정된 SIMENSE 데이터로 통합 테스트"""
    print("\n🧪 수정된 SIMENSE 데이터 통합 테스트")
    print("=" * 60)
    
    try:
        # HITACHI 데이터 로드
        hitachi_file = Path("data/HVDC WAREHOUSE_HITACHI(HE).xlsx")
        hitachi_data = pd.read_excel(hitachi_file, engine='openpyxl')
        hitachi_data['Vendor'] = 'HITACHI'
        hitachi_data['Source_File'] = 'HITACHI(HE)'
        
        # 수정된 SIMENSE 데이터 로드
        fixed_simense_file = Path("data/HVDC WAREHOUSE_SIMENSE(SIM)_FIXED.xlsx")
        if fixed_simense_file.exists():
            simense_data = pd.read_excel(fixed_simense_file, engine='openpyxl')
        else:
            # 수정된 데이터가 없으면 원본에서 수정
            simense_data = fix_simense_pkg_column()
        
        # 데이터 결합
        combined_data = pd.concat([hitachi_data, simense_data], ignore_index=True, sort=False)
        
        print(f"✅ 통합 데이터 생성 완료!")
        print(f"📊 총 데이터: {len(combined_data):,}건")
        
        # Vendor별 분포 확인
        vendor_counts = combined_data['Vendor'].value_counts()
        print(f"\n🏢 Vendor별 분포:")
        for vendor, count in vendor_counts.items():
            print(f"   - {vendor}: {count:,}건")
        
        # Pkg 합계 확인
        if 'Pkg' in combined_data.columns:
            total_pkg = combined_data['Pkg'].sum()
            print(f"\n📦 전체 Pkg 합계: {total_pkg:,}")
            
            # Vendor별 Pkg 합계
            vendor_pkg = combined_data.groupby('Vendor')['Pkg'].sum()
            print(f"\n📦 Vendor별 Pkg 합계:")
            for vendor, pkg_sum in vendor_pkg.items():
                print(f"   - {vendor}: {pkg_sum:,}")
        
        return True
        
    except Exception as e:
        print(f"❌ 통합 테스트 실패: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 SIMENSE 데이터 Pkg 컬럼 문제 해결")
    print("=" * 80)
    
    # 1. 문제 분석
    analyze_simense_pkg_issue()
    
    # 2. Pkg 컬럼 수정
    fixed_simense = fix_simense_pkg_column()
    
    # 3. 통합 테스트
    test_success = test_combined_data_with_fixed_simense()
    
    # 4. 결과 요약
    print("\n" + "=" * 80)
    print("📋 수정 결과 요약:")
    print(f"   - Pkg 컬럼 수정: ✅ 완료")
    print(f"   - 통합 데이터 테스트: {'✅ 성공' if test_success else '❌ 실패'}")
    
    if test_success:
        print("\n🎉 SIMENSE 데이터 Pkg 컬럼 문제가 해결되었습니다!")
        print("📁 수정된 파일: data/HVDC WAREHOUSE_SIMENSE(SIM)_FIXED.xlsx")
    else:
        print("\n⚠️ 추가 확인이 필요합니다.") 