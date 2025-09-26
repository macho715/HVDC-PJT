"""
SIMENSE 데이터 로딩 상태 검증 스크립트
"""
import pandas as pd
import logging
from pathlib import Path

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_simense_data():
    """SIMENSE 데이터 로딩 상태 확인"""
    print("🔍 SIMENSE 데이터 로딩 상태 확인")
    print("=" * 50)
    
    # 파일 경로 설정
    data_dir = Path("data")
    simense_file = data_dir / "HVDC WAREHOUSE_SIMENSE(SIM).xlsx"
    
    # 1. 파일 존재 확인
    print(f"📁 SIMENSE 파일 경로: {simense_file}")
    print(f"📁 파일 존재: {simense_file.exists()}")
    
    if not simense_file.exists():
        print("❌ SIMENSE 파일이 존재하지 않습니다!")
        return False
    
    # 2. 파일 크기 확인
    file_size = simense_file.stat().st_size
    print(f"📊 파일 크기: {file_size:,} bytes ({file_size/1024:.1f} KB)")
    
    # 3. 데이터 로드 시도
    try:
        print("\n📊 SIMENSE 데이터 로드 시도...")
        simense_data = pd.read_excel(simense_file, engine='openpyxl')
        
        print(f"✅ SIMENSE 데이터 로드 성공!")
        print(f"📊 총 행 수: {len(simense_data):,}건")
        print(f"📊 총 열 수: {len(simense_data.columns)}개")
        
        # 4. 컬럼 정보 확인
        print(f"\n📋 컬럼 목록:")
        for i, col in enumerate(simense_data.columns, 1):
            print(f"   {i:2d}. {col}")
        
        # 5. 데이터 샘플 확인
        print(f"\n📋 데이터 샘플 (처음 5행):")
        print(simense_data.head())
        
        # 6. Vendor 컬럼 추가 테스트
        simense_data['Vendor'] = 'SIMENSE'
        simense_data['Source_File'] = 'SIMENSE(SIM)'
        print(f"\n✅ Vendor 컬럼 추가 완료")
        
        # 7. Pkg 컬럼 확인
        if 'Pkg' in simense_data.columns:
            pkg_sum = simense_data['Pkg'].sum()
            pkg_count = simense_data['Pkg'].count()
            print(f"📦 Pkg 컬럼 정보:")
            print(f"   - 총 합계: {pkg_sum:,}")
            print(f"   - 유효 데이터: {pkg_count:,}건")
            print(f"   - NA 값: {len(simense_data) - pkg_count:,}건")
        else:
            print("⚠️ Pkg 컬럼이 없습니다!")
        
        # 8. Status_Location 확인
        if 'Status_Location' in simense_data.columns:
            status_counts = simense_data['Status_Location'].value_counts()
            print(f"\n📍 Status_Location 분포:")
            for status, count in status_counts.items():
                print(f"   - {status}: {count:,}건")
        else:
            print("⚠️ Status_Location 컬럼이 없습니다!")
        
        return True
        
    except Exception as e:
        print(f"❌ SIMENSE 데이터 로드 실패: {str(e)}")
        return False

def check_combined_data():
    """통합 데이터에서 SIMENSE 확인"""
    print("\n🔍 통합 데이터에서 SIMENSE 확인")
    print("=" * 50)
    
    try:
        # HITACHI 데이터 로드
        hitachi_file = Path("data/HVDC WAREHOUSE_HITACHI(HE).xlsx")
        hitachi_data = pd.read_excel(hitachi_file, engine='openpyxl')
        hitachi_data['Vendor'] = 'HITACHI'
        hitachi_data['Source_File'] = 'HITACHI(HE)'
        
        # SIMENSE 데이터 로드
        simense_file = Path("data/HVDC WAREHOUSE_SIMENSE(SIM).xlsx")
        simense_data = pd.read_excel(simense_file, engine='openpyxl')
        simense_data['Vendor'] = 'SIMENSE'
        simense_data['Source_File'] = 'SIMENSE(SIM)'
        
        # 데이터 결합
        combined_data = pd.concat([hitachi_data, simense_data], ignore_index=True, sort=False)
        
        print(f"✅ 통합 데이터 생성 완료!")
        print(f"📊 총 데이터: {len(combined_data):,}건")
        
        # Vendor별 분포 확인
        vendor_counts = combined_data['Vendor'].value_counts()
        print(f"\n🏢 Vendor별 분포:")
        for vendor, count in vendor_counts.items():
            print(f"   - {vendor}: {count:,}건")
        
        # Source_File별 분포 확인
        source_counts = combined_data['Source_File'].value_counts()
        print(f"\n📁 Source_File별 분포:")
        for source, count in source_counts.items():
            print(f"   - {source}: {count:,}건")
        
        return True
        
    except Exception as e:
        print(f"❌ 통합 데이터 확인 실패: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔍 SIMENSE 데이터 검증 시작")
    print("=" * 60)
    
    # 1. SIMENSE 데이터 개별 확인
    simense_ok = check_simense_data()
    
    # 2. 통합 데이터 확인
    combined_ok = check_combined_data()
    
    # 3. 결과 요약
    print("\n" + "=" * 60)
    print("📋 검증 결과 요약:")
    print(f"   - SIMENSE 개별 데이터: {'✅ 정상' if simense_ok else '❌ 문제'}")
    print(f"   - 통합 데이터: {'✅ 정상' if combined_ok else '❌ 문제'}")
    
    if simense_ok and combined_ok:
        print("\n🎉 SIMENSE 데이터가 정상적으로 로드되고 있습니다!")
    else:
        print("\n⚠️ SIMENSE 데이터에 문제가 있습니다. 추가 확인이 필요합니다.") 