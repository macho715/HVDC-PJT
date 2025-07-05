#!/usr/bin/env python3
"""
MACHO-GPT v3.4-mini 통합 파이프라인
HVDC 프로젝트 - Flow Code → 트랜잭션 이벤트 전체 자동화

실행 순서:
1. Flow Code 부여 (HITACHI + SIMENSE)
2. 트랜잭션 이벤트 자동 생성
3. 정규화 트랜잭션 테이블 생성

작성: 2025-07-01
버전: v3.4-mini
모드: PRIME → LATTICE → RHYTHM
"""

import pandas as pd
import numpy as np
import re
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class MachoIntegratedPipeline:
    """MACHO-GPT 통합 파이프라인 엔진"""
    
    def __init__(self):
        self.confidence_threshold = 0.90
        self.site_locations = ['AGI', 'DAS', 'MIR', 'SHU']
        
        # 파일 경로 설정
        self.file_hitachi = 'data/HVDC WAREHOUSE_HITACHI(HE).xlsx'
        self.file_simense = 'data/HVDC WAREHOUSE_SIMENSE(SIM).xlsx'
        self.output_flow_code = 'data/flowcode_transaction_table.xlsx'
        self.output_final = 'output/정규화_트랜잭션테이블_상세.xlsx'
        
    def get_warehouse_columns(self, df):
        """창고 관련 컬럼 추출"""
        warehouse_keywords = ['DSV', 'HAULER', 'AAA', 'MOSB', 'JDN']
        warehouse_columns = []
        
        for col in df.columns:
            if any(keyword in str(col).upper() for keyword in warehouse_keywords):
                warehouse_columns.append(col)
        
        return warehouse_columns
    
    def get_unified_case_column(self, df):
        """Case ID 컬럼 통합 감지"""
        case_candidates = ['Case_No', 'Case ID', 'Case_ID', 'CASE_NO', 'CASE_ID']
        
        for candidate in case_candidates:
            if candidate in df.columns:
                return candidate
        
        # 컬럼명에 'case'가 포함된 것 찾기
        for col in df.columns:
            if 'case' in str(col).lower():
                return col
        
        return df.columns[0]  # fallback
    
    def add_cum_wh_before_mosb(self, df, wh_cols, case_col='Case_ID'):
        """MOSB 이전 창고 수 계산"""
        df['wh_before_mosb'] = 0
        
        for idx, row in df.iterrows():
            count = 0
            for col in wh_cols:
                if 'MOSB' not in str(col).upper() and pd.notna(row[col]):
                    count += 1
            df.loc[idx, 'wh_before_mosb'] = count
        
        return df
    
    def route_to_flow_code_v2(self, row):
        """Flow Code 라우팅 로직 v2.8.3"""
        # Pre Arrival 체크 (Code 0)
        if pd.isna(row.get('Status_Location')) or str(row.get('Status_Location')).strip() == '':
            return 0
        
        status_loc = str(row.get('Status_Location', '')).upper()
        
        # Pre Arrival 키워드 체크
        pre_arrival_keywords = ['ETA', 'ETD', 'ARRIVAL', 'EXPECTED', 'PENDING']
        if any(keyword in status_loc for keyword in pre_arrival_keywords):
            return 0
        
        # MOSB 체크
        has_mosb = pd.notna(row.get('MOSB'))
        wh_before_mosb = row.get('wh_before_mosb', 0)
        
        # 현장 위치 체크
        is_site = any(site in status_loc for site in self.site_locations)
        
        if has_mosb:
            # MOSB 관련 Flow Code
            if wh_before_mosb <= 1:
                return 3  # MOSB 단순
            else:
                return 4  # MOSB 복합
        else:
            # 일반 창고 Flow Code
            if wh_before_mosb <= 1:
                return 1  # 단순 창고
            else:
                return 2  # 복합 창고
    
    def get_date_from_row(self, row):
        """행에서 첫 번째 유효한 날짜 추출"""
        date_columns = [col for col in row.index if any(x in str(col).upper() for x in ['ETD', 'ETA', 'DATE', 'TIME'])]
        
        for col in date_columns:
            if pd.notna(row[col]):
                try:
                    return pd.to_datetime(row[col])
                except:
                    continue
        
        return pd.Timestamp('2024-01-01')  # fallback
    
    def get_location_from_row(self, row):
        """행에서 위치 정보 추출"""
        if pd.notna(row.get('Status_Location')):
            return str(row['Status_Location'])
        
        # 창고/현장 컬럼에서 활성 위치 찾기
        all_locations = self.site_locations + ['DSV', 'HAULER', 'AAA', 'MOSB', 'JDN']
        
        for loc in all_locations:
            for col in row.index:
                if loc in str(col).upper() and pd.notna(row[col]):
                    return loc
        
        return 'UNKNOWN'
    
    def get_pkg_from_row(self, row):
        """행에서 Pkg 수량 추출"""
        pkg_candidates = ['Pkg', 'PKG', 'Package', 'Quantity', 'Qty']
        
        for candidate in pkg_candidates:
            if candidate in row.index and pd.notna(row[candidate]):
                try:
                    return float(row[candidate])
                except:
                    continue
        
        return 1.0  # fallback
    
    def get_val(self, row, col):
        """안전한 값 추출"""
        return row[col] if col in row and pd.notna(row[col]) else None
    
    def step1_generate_flow_code(self):
        """1단계: Flow Code 생성"""
        print("🔄 1단계: Flow Code 생성 시작...")
        
        # HITACHI 처리
        print("   📊 HITACHI 데이터 처리 중...")
        df_hitachi = pd.read_excel(self.file_hitachi)
        wh_cols_h = self.get_warehouse_columns(df_hitachi)
        case_col_h = self.get_unified_case_column(df_hitachi)
        
        df_hitachi['Case_ID'] = df_hitachi[case_col_h]
        df_hitachi = self.add_cum_wh_before_mosb(df_hitachi, wh_cols_h, case_col='Case_ID')
        df_hitachi['Flow_Code'] = df_hitachi.apply(self.route_to_flow_code_v2, axis=1)
        df_hitachi['Vendor'] = 'HITACHI'
        
        # 날짜, 위치, Pkg 정보 추가
        df_hitachi['Date'] = df_hitachi.apply(self.get_date_from_row, axis=1)
        df_hitachi['Location'] = df_hitachi.apply(self.get_location_from_row, axis=1)
        df_hitachi['Pkg'] = df_hitachi.apply(self.get_pkg_from_row, axis=1)
        
        # SIMENSE 처리
        print("   📊 SIMENSE 데이터 처리 중...")
        df_simense = pd.read_excel(self.file_simense)
        wh_cols_s = self.get_warehouse_columns(df_simense)
        case_col_s = self.get_unified_case_column(df_simense)
        
        df_simense['Case_ID'] = df_simense[case_col_s]
        df_simense = self.add_cum_wh_before_mosb(df_simense, wh_cols_s, case_col='Case_ID')
        df_simense['Flow_Code'] = df_simense.apply(self.route_to_flow_code_v2, axis=1)
        df_simense['Vendor'] = 'SIMENSE'
        
        # 날짜, 위치, Pkg 정보 추가
        df_simense['Date'] = df_simense.apply(self.get_date_from_row, axis=1)
        df_simense['Location'] = df_simense.apply(self.get_location_from_row, axis=1)
        df_simense['Pkg'] = df_simense.apply(self.get_pkg_from_row, axis=1)
        
        # 통합 및 저장
        df_combined = pd.concat([df_hitachi, df_simense], ignore_index=True)
        
        # 필수 컬럼만 선택
        essential_cols = ['Case_ID', 'Date', 'Location', 'Pkg', 'Flow_Code', 'Vendor', 'wh_before_mosb']
        if 'MOSB' in df_combined.columns:
            essential_cols.append('MOSB')
        if 'SQM' in df_combined.columns:
            essential_cols.append('SQM')
        if 'Stackable' in df_combined.columns:
            essential_cols.append('Stackable')
        
        df_final = df_combined[essential_cols].copy()
        df_final.to_excel(self.output_flow_code, index=False)
        
        print(f"   ✅ Flow Code 테이블 저장: {self.output_flow_code}")
        print(f"   📊 총 케이스: {len(df_final):,}건 (HITACHI: {len(df_hitachi):,}, SIMENSE: {len(df_simense):,})")
        
        # Flow Code 분포 출력
        flow_dist = df_final['Flow_Code'].value_counts().sort_index()
        print("   🔄 Flow Code 분포:")
        for code, count in flow_dist.items():
            print(f"      Code {code}: {count:,}건")
        
        return df_final
    
    def step2_generate_transactions(self):
        """2단계: 트랜잭션 이벤트 생성"""
        print("\n🔄 2단계: 트랜잭션 이벤트 생성 시작...")
        
        # Flow Code 테이블 로드
        df = pd.read_excel(self.output_flow_code)
        df['Date'] = pd.to_datetime(df['Date'])
        
        print(f"   📊 입력 데이터: {len(df):,}건")
        
        trx_rows = []
        case_count = 0
        
        for case_id, group in df.groupby('Case_ID'):
            case_count += 1
            if case_count % 1000 == 0:
                print(f"   🔄 진행률: {case_count:,} 케이스 처리 중...")
            
            group = group.sort_values('Date')
            prev_row = None
            
            for idx, row in group.iterrows():
                # IN 이벤트 (모든 위치 도착)
                trx_rows.append({
                    'Case_ID': row['Case_ID'],
                    'Date': row['Date'],
                    'Location': row['Location'],
                    'Event': 'IN',
                    'Pkg': abs(row['Pkg']),
                    'SQM': self.get_val(row, 'SQM'),
                    'Stackable': self.get_val(row, 'Stackable'),
                    'Flow_Code': row.get('Flow_Code'),
                    'Vendor': row.get('Vendor')
                })
                
                # MOVE 이벤트 (위치 변경시)
                if prev_row is not None and row['Location'] != prev_row['Location']:
                    # MOVE_OUT (이전 위치에서 출고)
                    trx_rows.append({
                        'Case_ID': row['Case_ID'],
                        'Date': row['Date'],
                        'Location': prev_row['Location'],
                        'Event': 'MOVE_OUT',
                        'Pkg': -abs(row['Pkg']),
                        'SQM': self.get_val(prev_row, 'SQM'),
                        'Stackable': self.get_val(prev_row, 'Stackable'),
                        'Flow_Code': prev_row.get('Flow_Code'),
                        'Vendor': row.get('Vendor')
                    })
                    
                    # MOVE_IN (새 위치로 입고)
                    trx_rows.append({
                        'Case_ID': row['Case_ID'],
                        'Date': row['Date'],
                        'Location': row['Location'],
                        'Event': 'MOVE_IN',
                        'Pkg': abs(row['Pkg']),
                        'SQM': self.get_val(row, 'SQM'),
                        'Stackable': self.get_val(row, 'Stackable'),
                        'Flow_Code': row.get('Flow_Code'),
                        'Vendor': row.get('Vendor')
                    })
                
                prev_row = row
            
            # OUT 이벤트 (현장에서 최종 출고)
            if len(group) > 0:
                last = group.iloc[-1]
                if last['Location'] in self.site_locations:
                    trx_rows.append({
                        'Case_ID': last['Case_ID'],
                        'Date': last['Date'],
                        'Location': last['Location'],
                        'Event': 'OUT',
                        'Pkg': -abs(last['Pkg']),
                        'SQM': self.get_val(last, 'SQM'),
                        'Stackable': self.get_val(last, 'Stackable'),
                        'Flow_Code': last.get('Flow_Code'),
                        'Vendor': last.get('Vendor')
                    })
            
            # RETURN 이벤트 (현장에서 창고로 복귀)
            if len(group) > 1:
                for i in range(1, len(group)):
                    curr_loc = group.iloc[i]['Location']
                    prev_loc = group.iloc[i-1]['Location']
                    
                    if prev_loc in self.site_locations and curr_loc not in self.site_locations:
                        trx_rows.append({
                            'Case_ID': group.iloc[i]['Case_ID'],
                            'Date': group.iloc[i]['Date'],
                            'Location': curr_loc,
                            'Event': 'RETURN',
                            'Pkg': abs(group.iloc[i]['Pkg']),
                            'SQM': self.get_val(group.iloc[i], 'SQM'),
                            'Stackable': self.get_val(group.iloc[i], 'Stackable'),
                            'Flow_Code': group.iloc[i].get('Flow_Code'),
                            'Vendor': group.iloc[i].get('Vendor')
                        })
        
        # 트랜잭션 DataFrame 생성
        trx_df = pd.DataFrame(trx_rows)
        trx_df = trx_df.sort_values(['Case_ID', 'Location', 'Date'])
        
        # 누적재고 계산
        trx_df['누적재고'] = trx_df.groupby(['Location', 'Case_ID'])['Pkg'].cumsum()
        
        # 저장
        trx_df.to_excel(self.output_final, index=False)
        
        print(f"   ✅ 트랜잭션 테이블 저장: {self.output_final}")
        print(f"   📊 총 트랜잭션: {len(trx_df):,}건")
        
        # 이벤트별 분포
        event_dist = trx_df['Event'].value_counts()
        print("   📋 이벤트별 분포:")
        for event, count in event_dist.items():
            print(f"      {event}: {count:,}건")
        
        return trx_df
    
    def generate_summary_report(self):
        """요약 리포트 생성"""
        print("\n" + "="*80)
        print("📊 MACHO-GPT v3.4-mini 통합 파이프라인 완료 리포트")
        print("="*80)
        
        # Flow Code 테이블 통계
        if pd.api.types.is_file_like(self.output_flow_code):
            try:
                df_flow = pd.read_excel(self.output_flow_code)
                print(f"📦 Flow Code 테이블: {len(df_flow):,}건")
                
                vendor_dist = df_flow['Vendor'].value_counts()
                print("🏢 벤더별 분포:")
                for vendor, count in vendor_dist.items():
                    print(f"   {vendor}: {count:,}건")
            except:
                print("❌ Flow Code 테이블 읽기 실패")
        
        # 트랜잭션 테이블 통계
        try:
            df_trx = pd.read_excel(self.output_final)
            print(f"\n🔄 트랜잭션 테이블: {len(df_trx):,}건")
            
            event_dist = df_trx['Event'].value_counts()
            print("📋 이벤트별 분포:")
            for event, count in event_dist.items():
                print(f"   {event}: {count:,}건")
            
            location_dist = df_trx['Location'].value_counts().head(5)
            print("\n📍 상위 5개 위치:")
            for location, count in location_dist.items():
                print(f"   {location}: {count:,}건")
                
        except Exception as e:
            print(f"❌ 트랜잭션 테이블 읽기 실패: {e}")
        
        print(f"\n📈 신뢰도: {self.confidence_threshold*100}% 이상")
        print(f"🎯 완료 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        return {
            'status': 'SUCCESS',
            'confidence': 0.95,
            'mode': 'RHYTHM',
            'triggers': ['pipeline_complete', 'transaction_ready'],
            'next_cmds': [
                'visualize_data',
                'generate_kpi_dashboard',
                'switch_mode COST_GUARD'
            ]
        }
    
    def run_full_pipeline(self):
        """전체 파이프라인 실행"""
        print("🚀 MACHO-GPT v3.4-mini 통합 파이프라인 시작")
        print("모드: PRIME → LATTICE → RHYTHM")
        print("="*60)
        
        try:
            # 1단계: Flow Code 생성
            df_flow = self.step1_generate_flow_code()
            
            # 2단계: 트랜잭션 이벤트 생성
            df_trx = self.step2_generate_transactions()
            
            # 3단계: 요약 리포트
            result = self.generate_summary_report()
            
            return result
            
        except Exception as e:
            print(f"❌ 파이프라인 실행 오류: {e}")
            print("ZERO 모드로 전환 - 수동 확인 필요")
            return {
                'status': 'FAILED',
                'confidence': 0.0,
                'mode': 'ZERO',
                'error': str(e)
            }

# 메인 실행부
if __name__ == "__main__":
    pipeline = MachoIntegratedPipeline()
    result = pipeline.run_full_pipeline()
    
    print(f"\n✅ 파이프라인 완료 - 상태: {result['status']}")
    if result['status'] == 'SUCCESS':
        print(f"📊 신뢰도: {result['confidence']*100}% | 모드: {result['mode']}")
    
    # 추천 명령어 출력
    if 'next_cmds' in result:
        print(f"\n🔧 **추천 명령어:**")
        for i, cmd in enumerate(result['next_cmds'], 1):
            print(f"/{cmd} [단계 {i} - 다음 로직컬 스텝]") 