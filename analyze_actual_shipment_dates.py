#!/usr/bin/env python3
"""
실제 SIMENSE & HITACHI Excel 파일에서 화물 입고 날짜 분석
MACHO v2.8.4 - 실제 입고 시점부터 마지막 입고 시점까지 파악
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import re

def analyze_actual_shipment_dates():
    """실제 Excel 파일에서 화물 입고 날짜 분석"""
    
    print("📅 실제 화물 입고 날짜 분석 시작")
    print("=" * 80)
    
    # Excel 파일 경로 설정
    data_paths = {
        'SIMENSE': 'hvdc_macho_gpt/WAREHOUSE/data/HVDC WAREHOUSE_SIMENSE(SIM).xlsx',
        'HITACHI': 'hvdc_macho_gpt/WAREHOUSE/data/HVDC WAREHOUSE_HITACHI(HE).xlsx'
    }
    
    all_dates = []
    vendor_date_ranges = {}
    
    for vendor, file_path in data_paths.items():
        print(f"\n🔍 {vendor} 파일 분석 중: {file_path}")
        
        try:
            if not Path(file_path).exists():
                print(f"   ❌ 파일을 찾을 수 없습니다: {file_path}")
                continue
            
            # Excel 파일 읽기
            df = pd.read_excel(file_path)
            print(f"   📊 총 {len(df):,}행 데이터 로드")
            
            # 날짜 관련 컬럼 찾기
            date_columns = []
            for col in df.columns:
                col_str = str(col).lower()
                if any(keyword in col_str for keyword in ['date', '날짜', 'time', '시간', 'arrival', 'departure', 'eta', 'etd']):
                    date_columns.append(col)
            
            print(f"   📅 발견된 날짜 관련 컬럼: {date_columns}")
            
            vendor_dates = []
            
            # 각 날짜 컬럼 분석
            for col in date_columns:
                print(f"\n   🔎 '{col}' 컬럼 분석:")
                
                # 빈 값이 아닌 데이터만 추출
                non_null_data = df[col].dropna()
                
                if len(non_null_data) == 0:
                    print(f"      ⚠️ 유효한 데이터 없음")
                    continue
                
                # 샘플 데이터 출력
                print(f"      📝 샘플 데이터 (처음 5개): {list(non_null_data.head())}")
                
                # 날짜 형식 변환 시도
                converted_dates = []
                
                for value in non_null_data:
                    try:
                        # 문자열인 경우 여러 날짜 형식 시도
                        if isinstance(value, str):
                            # 일반적인 날짜 형식들
                            date_formats = [
                                '%Y-%m-%d', '%Y/%m/%d', '%d/%m/%Y', '%m/%d/%Y',
                                '%Y-%m-%d %H:%M:%S', '%Y/%m/%d %H:%M:%S',
                                '%d-%m-%Y', '%d.%m.%Y', '%Y.%m.%d'
                            ]
                            
                            for fmt in date_formats:
                                try:
                                    parsed_date = datetime.strptime(value, fmt)
                                    converted_dates.append(parsed_date)
                                    break
                                except ValueError:
                                    continue
                            else:
                                # pandas의 자동 날짜 파싱 시도
                                try:
                                    parsed_date = pd.to_datetime(value)
                                    if not pd.isna(parsed_date):
                                        converted_dates.append(parsed_date.to_pydatetime())
                                except:
                                    pass
                        
                        # 이미 datetime 객체인 경우
                        elif isinstance(value, (datetime, pd.Timestamp)):
                            if isinstance(value, pd.Timestamp):
                                converted_dates.append(value.to_pydatetime())
                            else:
                                converted_dates.append(value)
                        
                        # 숫자인 경우 (Excel 날짜 시리얼)
                        elif isinstance(value, (int, float)) and not np.isnan(value):
                            try:
                                # Excel 날짜 시리얼을 datetime으로 변환
                                excel_date = datetime(1900, 1, 1) + timedelta(days=value - 2)
                                if 1990 <= excel_date.year <= 2030:  # 합리적인 연도 범위
                                    converted_dates.append(excel_date)
                            except:
                                pass
                    
                    except Exception as e:
                        continue
                
                if converted_dates:
                    min_date = min(converted_dates)
                    max_date = max(converted_dates)
                    print(f"      ✅ 변환된 날짜 수: {len(converted_dates):,}개")
                    print(f"      📅 날짜 범위: {min_date.strftime('%Y-%m-%d')} ~ {max_date.strftime('%Y-%m-%d')}")
                    
                    vendor_dates.extend(converted_dates)
                    all_dates.extend(converted_dates)
                else:
                    print(f"      ❌ 날짜 변환 실패")
            
            # 벤더별 날짜 범위 저장
            if vendor_dates:
                vendor_date_ranges[vendor] = {
                    'min_date': min(vendor_dates),
                    'max_date': max(vendor_dates),
                    'total_records': len(vendor_dates),
                    'date_range_days': (max(vendor_dates) - min(vendor_dates)).days
                }
                
                print(f"\n   📊 {vendor} 전체 날짜 요약:")
                print(f"      🗓️ 최초 입고: {vendor_date_ranges[vendor]['min_date'].strftime('%Y-%m-%d')}")
                print(f"      🗓️ 최종 입고: {vendor_date_ranges[vendor]['max_date'].strftime('%Y-%m-%d')}")
                print(f"      📈 총 레코드: {vendor_date_ranges[vendor]['total_records']:,}개")
                print(f"      ⏰ 기간: {vendor_date_ranges[vendor]['date_range_days']}일")
            
        except Exception as e:
            print(f"   ❌ {vendor} 파일 분석 중 오류: {e}")
    
    # 전체 날짜 범위 분석
    print("\n" + "=" * 80)
    print("📊 전체 화물 입고 날짜 분석 결과")
    print("=" * 80)
    
    if all_dates:
        overall_min = min(all_dates)
        overall_max = max(all_dates)
        total_days = (overall_max - overall_min).days
        
        print(f"🗓️ **전체 입고 기간:**")
        print(f"   시작일: {overall_min.strftime('%Y-%m-%d')} ({overall_min.strftime('%A')})")
        print(f"   종료일: {overall_max.strftime('%Y-%m-%d')} ({overall_max.strftime('%A')})")
        print(f"   총 기간: {total_days}일 ({total_days//30:.1f}개월)")
        
        # 월별 분포 생성
        monthly_dist = {}
        for date in all_dates:
            month_key = date.strftime('%Y-%m')
            monthly_dist[month_key] = monthly_dist.get(month_key, 0) + 1
        
        print(f"\n📅 **월별 입고 분포:**")
        sorted_months = sorted(monthly_dist.keys())
        for month in sorted_months:
            count = monthly_dist[month]
            percentage = (count / len(all_dates)) * 100
            print(f"   {month}: {count:,}건 ({percentage:.1f}%)")
        
        # 회계용 연속 월 리스트 생성
        start_month = overall_min.replace(day=1)
        end_month = overall_max.replace(day=1)
        
        accounting_months = []
        current = start_month
        while current <= end_month:
            accounting_months.append(current.strftime('%Y-%m'))
            # 다음 달로 이동
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)
        
        print(f"\n📋 **회계용 연속 월 리스트 ({len(accounting_months)}개월):**")
        print(f"   {accounting_months}")
        
        # 벤더별 상세 정보
        print(f"\n🏢 **벤더별 상세 정보:**")
        for vendor, info in vendor_date_ranges.items():
            print(f"   {vendor}:")
            print(f"      📅 기간: {info['min_date'].strftime('%Y-%m-%d')} ~ {info['max_date'].strftime('%Y-%m-%d')}")
            print(f"      📊 레코드: {info['total_records']:,}개")
            print(f"      ⏰ 일수: {info['date_range_days']}일")
        
        return {
            'overall_min': overall_min,
            'overall_max': overall_max,
            'total_days': total_days,
            'monthly_distribution': monthly_dist,
            'accounting_months': accounting_months,
            'vendor_ranges': vendor_date_ranges,
            'total_records': len(all_dates)
        }
    
    else:
        print("❌ 유효한 날짜 데이터를 찾을 수 없습니다.")
        return None

if __name__ == "__main__":
    print("🔍 MACHO v2.8.4 실제 화물 입고 날짜 분석")
    print("📋 화물 처음 입고 시점부터 마지막 입고 시점까지 분석")
    
    result = analyze_actual_shipment_dates()
    
    if result:
        print(f"\n✅ 실제 화물 입고 날짜 분석 완료!")
        print(f"   총 {result['total_records']:,}개 날짜 레코드 분석")
        print(f"   {len(result['accounting_months'])}개월 연속 기간 확인")
    else:
        print(f"\n❌ 날짜 분석 실패!") 