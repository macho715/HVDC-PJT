#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Status_Location_Date Excel 보고서 생성기
MACHO-GPT v3.4-mini | 화물이력관리_통합시스템
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import warnings
warnings.filterwarnings('ignore')

def create_status_location_date_excel_report():
    """Status_Location_Date 컬럼과 데이터를 포함한 Excel 보고서 생성"""
    
    print("🚀 Status_Location_Date Excel 보고서 생성 시작...")
    
    try:
        # 1. 기존 MACHO 통합 데이터 로드
        source_file = 'MACHO_Final_Report_Complete_20250703_230904.xlsx'
        
        if not os.path.exists(source_file):
            print(f"❌ 소스 파일을 찾을 수 없습니다: {source_file}")
            return
            
        print(f"📂 소스 파일 로드 중: {source_file}")
        df = pd.read_excel(source_file, sheet_name=0)
        print(f"✅ 데이터 로드 완료: {len(df):,}건, {len(df.columns)}개 컬럼")
        
        # 2. Status_Location_Date 컬럼 정의
        location_columns = {
            'sites': ['AGI', 'DAS', 'MIR', 'SHU'],
            'warehouses': ['DSV Indoor', 'DSV Outdoor', 'DSV Al Markaz', 'MOSB', 'DSV MZP']
        }
        
        # 3. Excel 보고서 생성
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f'Status_Location_Date_보고서_{timestamp}.xlsx'
        
        print(f"📊 Excel 보고서 생성 중: {output_file}")
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            
            # Sheet 1: 화물이력관리_통합데이터 (Status_Location_Date 포함)
            print("📋 Sheet 1: 화물이력관리_통합데이터 생성...")
            
            # 메인 데이터 시트
            main_df = df.copy()
            
            # Status_Location_Date 관련 컬럼 우선 순서로 정렬
            priority_cols = ['Case No.', 'FLOW_CODE', 'Status_Current', 'Status_Location', 'ETA/ATA']
            location_cols = location_columns['sites'] + location_columns['warehouses']
            
            # 컬럼 순서 재정렬
            available_priority_cols = [col for col in priority_cols if col in main_df.columns]
            available_location_cols = [col for col in location_cols if col in main_df.columns]
            other_cols = [col for col in main_df.columns if col not in available_priority_cols + available_location_cols]
            
            final_cols = available_priority_cols + available_location_cols + other_cols
            main_df = main_df[final_cols]
            
            main_df.to_excel(writer, sheet_name='화물이력관리_통합데이터', index=False)
            
            # Sheet 2: Status_Location_Date 컬럼 구조
            print("📋 Sheet 2: Status_Location_Date 컬럼구조 생성...")
            
            structure_data = []
            
            # 현장 위치 컬럼
            for site in location_columns['sites']:
                if site in df.columns:
                    count = df[site].notna().sum()
                    percentage = count / len(df) * 100
                    structure_data.append({
                        '위치_유형': '현장',
                        '컬럼명': site,
                        '건수': count,
                        '비율(%)': round(percentage, 1),
                        '설명': f'{site} 현장 도착일시'
                    })
            
            # 창고 위치 컬럼
            for warehouse in location_columns['warehouses']:
                if warehouse in df.columns:
                    count = df[warehouse].notna().sum()
                    percentage = count / len(df) * 100
                    structure_data.append({
                        '위치_유형': '창고',
                        '컬럼명': warehouse,
                        '건수': count,
                        '비율(%)': round(percentage, 1),
                        '설명': f'{warehouse} 창고 입고일시'
                    })
            
            # 시간 관련 컬럼
            time_cols = [
                {'컬럼명': 'ETA/ATA', '설명': '예상/실제 도착시간'},
                {'컬럼명': 'Status_Current', '설명': '현재 상태 (site/warehouse)'},
                {'컬럼명': 'Status_Location', '설명': '현재 위치 상태'}
            ]
            
            for time_col in time_cols:
                if time_col['컬럼명'] in df.columns:
                    count = df[time_col['컬럼명']].notna().sum()
                    percentage = count / len(df) * 100
                    structure_data.append({
                        '위치_유형': '시간정보',
                        '컬럼명': time_col['컬럼명'],
                        '건수': count,
                        '비율(%)': round(percentage, 1),
                        '설명': time_col['설명']
                    })
            
            structure_df = pd.DataFrame(structure_data)
            structure_df.to_excel(writer, sheet_name='Status_Location_Date_컬럼구조', index=False)
            
            # Sheet 3: Status_Location_Date 실제 데이터 샘플
            print("📋 Sheet 3: Status_Location_Date 실제데이터샘플 생성...")
            
            sample_data = []
            for idx, row in df.head(50).iterrows():
                case_no = row.get('Case No.', f'CASE_{idx}')
                
                # 현재 위치 확인
                current_location = 'Port'
                location_date = 'N/A'
                
                # 현장 우선 확인
                for site in location_columns['sites']:
                    if site in df.columns and pd.notna(row[site]):
                        current_location = site
                        location_date = row[site]
                        break
                
                # 창고 확인 (현장이 없으면)
                if current_location == 'Port':
                    for warehouse in location_columns['warehouses']:
                        if warehouse in df.columns and pd.notna(row[warehouse]):
                            current_location = warehouse
                            location_date = row[warehouse]
                            break
                
                sample_data.append({
                    'Case_No': case_no,
                    'Current_Location': current_location,
                    'Location_Date': location_date,
                    'ETA_ATA': row.get('ETA/ATA', 'N/A'),
                    'Flow_Code': row.get('FLOW_CODE', 'N/A'),
                    'Status_Current': row.get('Status_Current', 'N/A'),
                    'Status_Location': row.get('Status_Location', 'N/A'),
                    'Vendor': row.get('Vendor', 'N/A')
                })
            
            sample_df = pd.DataFrame(sample_data)
            sample_df.to_excel(writer, sheet_name='Status_Location_Date_실제데이터샘플', index=False)
            
            # Sheet 4: 위치별 화물 분포 통계
            print("📋 Sheet 4: 위치별_화물분포_통계 생성...")
            
            distribution_data = []
            
            # 모든 위치 컬럼에 대한 통계
            all_locations = location_columns['sites'] + location_columns['warehouses']
            for location in all_locations:
                if location in df.columns:
                    count = df[location].notna().sum()
                    percentage = count / len(df) * 100
                    
                    location_type = '현장' if location in location_columns['sites'] else '창고'
                    
                    # 특징 설명
                    features = {
                        'SHU': '최대 집중 현장 (용량 관리 필요)',
                        'DSV Outdoor': '외부 창고 (날씨 영향 고려)',
                        'DSV Indoor': '내부 창고 (안전 보관)',
                        'DSV Al Markaz': 'Al Markaz 창고 (중간 경유)',
                        'MIR': '주요 현장 (안정적 운영)',
                        'DAS': '주요 현장 (효율적 운영)',
                        'MOSB': 'MOSB 창고 (전문 보관)',
                        'AGI': 'AGI 현장 (특수 장비)',
                        'DSV MZP': '소규모 창고 (특수 용도)'
                    }
                    
                    distribution_data.append({
                        '위치': location,
                        '건수': count,
                        '비율(%)': round(percentage, 1),
                        '위치_유형': location_type,
                        '특징': features.get(location, '일반 운영')
                    })
            
            # 건수 기준 내림차순 정렬
            distribution_df = pd.DataFrame(distribution_data)
            distribution_df = distribution_df.sort_values('건수', ascending=False)
            distribution_df.to_excel(writer, sheet_name='위치별_화물분포_통계', index=False)
            
            # Sheet 5: Flow Code vs Status_Location_Date 교차 분석
            print("📋 Sheet 5: Flow_Code_vs_Status_Location_교차분석 생성...")
            
            cross_analysis_data = []
            
            # Flow Code별 위치 분포
            for flow_code in sorted(df['FLOW_CODE'].unique()):
                flow_subset = df[df['FLOW_CODE'] == flow_code]
                
                for location in all_locations:
                    if location in df.columns:
                        count = flow_subset[location].notna().sum()
                        if count > 0:
                            percentage = count / len(flow_subset) * 100
                            cross_analysis_data.append({
                                'Flow_Code': flow_code,
                                '위치': location,
                                '건수': count,
                                '비율(%)': round(percentage, 1),
                                '위치_유형': '현장' if location in location_columns['sites'] else '창고'
                            })
            
            cross_df = pd.DataFrame(cross_analysis_data)
            cross_df = cross_df.sort_values(['Flow_Code', '건수'], ascending=[True, False])
            cross_df.to_excel(writer, sheet_name='Flow_Code_vs_Status_Location_교차분석', index=False)
            
            # Sheet 6: 요약 통계
            print("📋 Sheet 6: 요약_통계 생성...")
            
            summary_data = [
                {'구분': '총 화물 건수', '값': f'{len(df):,}건'},
                {'구분': '총 컬럼 수', '값': f'{len(df.columns)}개'},
                {'구분': '현장 위치 수', '값': f'{len(location_columns["sites"])}개'},
                {'구분': '창고 위치 수', '값': f'{len(location_columns["warehouses"])}개'},
                {'구분': '보고서 생성일시', '값': datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
                {'구분': 'Flow Code 범위', '값': f'{df["FLOW_CODE"].min()}-{df["FLOW_CODE"].max()}'},
                {'구분': '주요 벤더', '값': ', '.join(df['Vendor'].value_counts().head(2).index.tolist()) if 'Vendor' in df.columns else 'N/A'},
                {'구분': '데이터 기간', '값': f'{df["ETA/ATA"].min().strftime("%Y-%m-%d")} ~ {df["ETA/ATA"].max().strftime("%Y-%m-%d")}' if 'ETA/ATA' in df.columns else 'N/A'}
            ]
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='요약_통계', index=False)
        
        print(f"✅ Excel 보고서 생성 완료: {output_file}")
        
        # 파일 크기 확인
        file_size = os.path.getsize(output_file) / (1024 * 1024)  # MB
        print(f"📊 파일 크기: {file_size:.1f}MB")
        
        # 시트 구성 요약
        print("\n📋 보고서 구성:")
        print("  1. 화물이력관리_통합데이터 (메인 데이터)")
        print("  2. Status_Location_Date_컬럼구조")
        print("  3. Status_Location_Date_실제데이터샘플")
        print("  4. 위치별_화물분포_통계")
        print("  5. Flow_Code_vs_Status_Location_교차분석")
        print("  6. 요약_통계")
        
        return output_file
        
    except Exception as e:
        print(f"❌ 보고서 생성 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    output_file = create_status_location_date_excel_report()
    if output_file:
        print(f"\n🎉 Status_Location_Date Excel 보고서 생성 완료!")
        print(f"📁 파일 위치: {os.path.abspath(output_file)}")
        print("\n🔧 추천 명령어:")
        print("  /track-material-location realtime [실시간 자재 위치 추적]")
        print("  /analyze-location-distribution status [위치별 분포 현황 분석]")
        print("  /monitor-warehouse-capacity current [창고 용량 현황 모니터링]") 