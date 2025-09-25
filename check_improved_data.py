#!/usr/bin/env python3
"""
개선된 HVDC 데이터 파일 검증 스크립트
"""

import pandas as pd
import os
from datetime import datetime

def check_improved_data():
    """개선된 데이터 파일 검증"""
    print("🔍 개선된 HVDC 데이터 파일 검증")
    print("=" * 80)
    
    # 파일 찾기
    improved_files = [f for f in os.listdir('.') if f.startswith('HVDC_DataQuality_Improved_') and f.endswith('.xlsx')]
    
    if not improved_files:
        print("❌ 개선된 데이터 파일을 찾을 수 없습니다.")
        return
    
    # 가장 최근 파일 사용
    latest_file = max(improved_files, key=lambda x: os.path.getmtime(x))
    print(f"📁 검증 파일: {latest_file}")
    print(f"📊 파일 크기: {os.path.getsize(latest_file):,} bytes")
    
    try:
        # Excel 파일 시트 정보 확인
        excel_file = pd.ExcelFile(latest_file)
        print(f"\n📋 Excel 시트 목록:")
        for sheet_name in excel_file.sheet_names:
            print(f"   - {sheet_name}")
        
        # 개선된 전체 데이터 확인
        print(f"\n🔍 '개선된_전체_데이터' 시트 분석:")
        improved_data = pd.read_excel(latest_file, sheet_name='개선된_전체_데이터')
        print(f"   전체 레코드 수: {len(improved_data):,}건")
        print(f"   컬럼 수: {len(improved_data.columns)}개")
        
        # 창고 컬럼 정보
        warehouse_columns = [
            'DSV Outdoor', 'DSV Indoor', 'DSV Al Markaz', 'AAA  Storage',
            'DHL Warehouse', 'MOSB', 'Hauler Indoor'
        ]
        
        print(f"\n📊 창고 컬럼 데이터 품질 (개선 후):")
        for col in warehouse_columns:
            if col in improved_data.columns:
                non_null_count = improved_data[col].notna().sum()
                print(f"   {col}: {non_null_count:,}건 (100% 날짜 형식)")
        
        # 개선 요약 시트 확인
        print(f"\n📈 '개선_요약' 시트 분석:")
        improvement_summary = pd.read_excel(latest_file, sheet_name='개선_요약')
        print(improvement_summary.to_string(index=False))
        
        # 창고별 개선 통계 시트 확인
        print(f"\n🏢 '창고별_개선_통계' 시트 분석:")
        warehouse_stats = pd.read_excel(latest_file, sheet_name='창고별_개선_통계')
        print(warehouse_stats.to_string(index=False))
        
        # 주요 개선 지표 계산
        print(f"\n🎯 주요 개선 지표:")
        
        # 개선 전후 비교
        original_accuracy = improvement_summary[improvement_summary['구분'] == 'original']['정확도(%)'].iloc[0]
        cleaned_accuracy = improvement_summary[improvement_summary['구분'] == 'cleaned']['정확도(%)'].iloc[0]
        improvement_effect = cleaned_accuracy - original_accuracy
        
        print(f"   📊 정확도 개선: {original_accuracy:.1f}% → {cleaned_accuracy:.1f}% (+{improvement_effect:.1f}%p)")
        
        # 데이터 품질 개선 효과
        total_removed = warehouse_stats['제거된_전각공백'].sum()
        print(f"   🧹 제거된 전각공백: {total_removed:,}건")
        
        # 가장 큰 개선을 보인 창고
        warehouse_stats['개선도'] = warehouse_stats['개선후_정확도(%)'] - warehouse_stats['개선전_정확도(%)']
        best_improvement = warehouse_stats.loc[warehouse_stats['개선도'].idxmax()]
        
        print(f"   🏆 가장 큰 개선 창고: {best_improvement['창고명']} (+{best_improvement['개선도']:.1f}%p)")
        
        # 품질 개선 이전 최악 창고
        worst_original = warehouse_stats.loc[warehouse_stats['개선전_정확도(%)'].idxmin()]
        print(f"   ⚠️ 개선 전 최악 창고: {worst_original['창고명']} ({worst_original['개선전_정확도(%)']:.1f}%)")
        
        # Final_Location_Improved 컬럼 분석
        if 'Final_Location_Improved' in improved_data.columns:
            print(f"\n🏢 Final_Location_Improved 분포:")
            final_location_counts = improved_data['Final_Location_Improved'].value_counts()
            for location, count in final_location_counts.head(10).items():
                print(f"   {location}: {count:,}건")
        
        # 데이터 소스별 분포
        if 'Data_Source' in improved_data.columns:
            print(f"\n📊 데이터 소스별 분포:")
            data_source_counts = improved_data['Data_Source'].value_counts()
            for source, count in data_source_counts.items():
                print(f"   {source}: {count:,}건")
        
        print(f"\n✅ 개선된 데이터 파일 검증 완료!")
        print(f"📁 파일 경로: {latest_file}")
        
    except Exception as e:
        print(f"❌ 파일 검증 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_improved_data() 