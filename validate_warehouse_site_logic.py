#!/usr/bin/env python3
"""
창고_현장_월별 보고서 수정 로직 검증 스크립트
Executive Summary 가이드 기반 4단계 검증 수행
HVDC 물류 마스터 시스템 v3.4-mini
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
import random
warnings.filterwarnings('ignore')

def main():
    """메인 검증 함수"""
    print("🔍 창고_현장_월별 보고서 로직 검증 시작")
    print("=" * 60)
    
    # 데이터 로드
    main_source = "MACHO_통합관리_20250702_205301/MACHO_Final_Report_Complete_20250703_230904.xlsx"
    
    try:
        df = pd.read_excel(main_source, engine='openpyxl')
        print(f"✅ 데이터 로드 성공: {len(df):,}건, {len(df.columns)}개 컬럼")
        
        # 날짜 컬럼 전처리
        warehouse_cols = ['DSV Indoor', 'DSV Al Markaz', 'DSV Outdoor', 'AAA  Storage', 'Hauler Indoor', 'DSV MZP', 'MOSB']
        site_cols = ['MIR', 'SHU', 'DAS', 'AGI']
        date_columns = warehouse_cols + site_cols
        
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # 1) 로직 적합성 평가
        print("\n📋 1) 로직 적합성 평가")
        print("=" * 40)
        
        total_warehouse_entries = 0
        total_site_entries = 0
        
        print("월별 입고 검증:")
        for warehouse in warehouse_cols:
            if warehouse in df.columns:
                entries = df[warehouse].notna().sum()
                total_warehouse_entries += entries
                if entries > 0:
                    print(f"  {warehouse}: {entries:,}건")
        
        for site in site_cols:
            if site in df.columns:
                entries = df[site].notna().sum()
                total_site_entries += entries
                if entries > 0:
                    print(f"  {site}: {entries:,}건")
        
        print(f"\n총계: 창고 {total_warehouse_entries:,}건, 현장 {total_site_entries:,}건")
        
        # 2) 주요 검증 포인트
        print("\n📋 2) 주요 검증 포인트")
        print("=" * 40)
        
        # 총계 일치 검증
        current_warehouse_stock = 0
        current_site_stock = 0
        
        if 'Status_Location' in df.columns:
            for warehouse in warehouse_cols:
                warehouse_clean = warehouse.replace('  ', ' ').strip()
                count = (df['Status_Location'] == warehouse).sum()
                count += (df['Status_Location'] == warehouse_clean).sum()
                current_warehouse_stock += count
            
            for site in site_cols:
                count = (df['Status_Location'] == site).sum()
                current_site_stock += count
        
        print(f"현재 재고 상태:")
        print(f"  창고 재고: {current_warehouse_stock:,}건")
        print(f"  현장 재고: {current_site_stock:,}건")
        
        # 균형 검증
        expected_balance = total_site_entries + current_warehouse_stock
        balance_diff = abs(total_warehouse_entries - expected_balance)
        balance_ratio = balance_diff / max(total_warehouse_entries, 1) * 100
        
        print(f"\n균형 검증:")
        print(f"  창고 총 입고: {total_warehouse_entries:,}건")
        print(f"  예상값 (현장입고 + 창고재고): {expected_balance:,}건")
        print(f"  차이: {balance_diff:,}건 ({balance_ratio:.1f}%)")
        print(f"  상태: {'✅ 정상' if balance_ratio < 5.0 else '⚠️ 불균형'}")
        
        # 타임스탬프 역전 검증
        timestamp_errors = 0
        
        for idx, row in df.iterrows():
            warehouse_dates = []
            site_dates = []
            
            for warehouse in warehouse_cols:
                if warehouse in row and pd.notna(row[warehouse]):
                    warehouse_dates.append(row[warehouse])
            
            for site in site_cols:
                if site in row and pd.notna(row[site]):
                    site_dates.append(row[site])
            
            # 날짜 역전 확인
            for wh_date in warehouse_dates:
                for site_date in site_dates:
                    if wh_date > site_date:
                        timestamp_errors += 1
                        break
        
        print(f"\n타임스탬프 검증:")
        print(f"  날짜 역전 오류: {timestamp_errors:,}건")
        print(f"  상태: {'✅ 정상' if timestamp_errors == 0 else '⚠️ 오류 발견'}")
        
        # 3) 월별 계산 검증
        print("\n📋 3) 월별 계산 검증")
        print("=" * 40)
        
        # 2024-01 샘플 월 계산
        test_period = pd.Timestamp('2024-01-01')
        print(f"샘플 월: {test_period.strftime('%Y-%m')}")
        
        for warehouse in warehouse_cols[:3]:  # 처음 3개만 샘플
            if warehouse in df.columns:
                warehouse_dates = df[warehouse].dropna()
                month_mask = warehouse_dates.dt.to_period('M') == test_period.to_period('M')
                inbound_count = month_mask.sum()
                
                if inbound_count > 0:
                    print(f"  {warehouse}: {inbound_count}건")
        
        # 4) Excel 파일 검증
        print("\n📋 4) Excel 파일 검증")
        print("=" * 40)
        
        excel_files = [
            "창고_현장_월별_보고서_올바른계산_20250704_015523.xlsx",
            "창고_현장_월별_보고서_올바른계산_20250704_014217.xlsx"
        ]
        
        import os
        excel_found = False
        
        for excel_file in excel_files:
            if os.path.exists(excel_file):
                excel_found = True
                print(f"✅ Excel 파일 발견: {excel_file}")
                
                try:
                    # 창고 시트 확인
                    warehouse_sheet = pd.read_excel(excel_file, sheet_name='창고_월별_입출고', engine='openpyxl')
                    print(f"  창고_월별_입출고: {len(warehouse_sheet)}행 × {len(warehouse_sheet.columns)}열")
                    
                    # 합계 확인
                    if 'Total' in warehouse_sheet['Location'].values:
                        total_row = warehouse_sheet[warehouse_sheet['Location'] == 'Total']
                        inbound_cols = [col for col in total_row.columns if '입고' in col]
                        if inbound_cols:
                            total_inbound = total_row[inbound_cols].sum(axis=1).iloc[0]
                            print(f"  보고서 창고 총 입고: {total_inbound:,.0f}건")
                    
                    # 현장 시트 확인  
                    site_sheet = pd.read_excel(excel_file, sheet_name='현장_월별_입고재고', engine='openpyxl')
                    print(f"  현장_월별_입고재고: {len(site_sheet)}행 × {len(site_sheet.columns)}열")
                    
                    if '합계' in site_sheet['Location'].values:
                        total_row = site_sheet[site_sheet['Location'] == '합계']
                        inbound_cols = [col for col in total_row.columns if '입고' in col]
                        if inbound_cols:
                            total_inbound = total_row[inbound_cols].sum(axis=1).iloc[0]
                            print(f"  보고서 현장 총 입고: {total_inbound:,.0f}건")
                    
                except Exception as e:
                    print(f"  ❌ Excel 읽기 실패: {e}")
                
                break
        
        if not excel_found:
            print("❌ Excel 파일을 찾을 수 없습니다")
        
        # 종합 결론
        print("\n📋 종합 검증 결과")
        print("=" * 40)
        
        issues = []
        if balance_ratio >= 5.0:
            issues.append(f"균형 불일치 {balance_ratio:.1f}%")
        if timestamp_errors > 0:
            issues.append(f"날짜 역전 {timestamp_errors}건")
        if not excel_found:
            issues.append("Excel 파일 없음")
        
        if not issues:
            print("✅ 모든 검증 통과 - 로직이 올바르게 구현됨")
        else:
            print(f"⚠️ 검토 필요 사항: {', '.join(issues)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 검증 실패: {e}")
        return False

if __name__ == "__main__":
    main() 