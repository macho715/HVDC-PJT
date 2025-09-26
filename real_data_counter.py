#!/usr/bin/env python3
"""
HVDC 실제 데이터 카운터
MACHO-GPT v3.4-mini | Samsung C&T Logistics

🎯 실제 Excel 파일에서 데이터 읽기:
- HVDC WAREHOUSE_SIMENSE(SIM).xlsx
- HVDC WAREHOUSE_HITACHI(HE).xlsx
- WH HANDLING 기반 정확한 개수 카운팅
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os
import sys
from pathlib import Path

# MACHO v2.8.4 설정
MACHO_VERSION = "v2.8.4"

class RealDataCounter:
    """실제 Excel 데이터 카운터"""
    
    def __init__(self):
        print(f"🚀 MACHO {MACHO_VERSION} 실제 데이터 카운터")
        print("=" * 80)
        
        # 파일 경로 설정
        self.data_paths = {
            'SIMENSE': 'hvdc_macho_gpt/WAREHOUSE/data/HVDC WAREHOUSE_SIMENSE(SIM).xlsx',
            'HITACHI': 'hvdc_macho_gpt/WAREHOUSE/data/HVDC WAREHOUSE_HITACHI(HE).xlsx'
        }
        
        # WH HANDLING Flow Code 매핑
        self.flow_code_mapping = {
            0: {'description': 'Port → Site (직접)', 'korean': '직접운송'},
            1: {'description': 'Port → WH1 → Site', 'korean': '창고1개경유'},
            2: {'description': 'Port → WH1 → WH2 → Site', 'korean': '창고2개경유'},
            3: {'description': 'Port → WH1 → WH2 → WH3+ → Site', 'korean': '창고3개+경유'}
        }
        
        self.real_data = {}
        
    def read_excel_file(self, file_path, vendor_name):
        """Excel 파일을 읽어서 데이터 분석"""
        print(f"\n📊 {vendor_name} 파일 읽기 중...")
        print(f"   파일 경로: {file_path}")
        
        try:
            if not os.path.exists(file_path):
                print(f"   ❌ 파일이 존재하지 않습니다: {file_path}")
                return None
            
            # Excel 파일의 모든 시트 확인
            excel_file = pd.ExcelFile(file_path)
            sheet_names = excel_file.sheet_names
            print(f"   📋 시트 목록: {', '.join(sheet_names)}")
            
            # 첫 번째 시트 또는 적절한 시트 읽기
            main_sheet = sheet_names[0]  # 기본적으로 첫 번째 시트
            
            df = pd.read_excel(file_path, sheet_name=main_sheet)
            print(f"   📈 총 행 수: {len(df):,}")
            print(f"   📊 총 열 수: {len(df.columns)}")
            print(f"   📋 컬럼 목록: {', '.join(df.columns.tolist()[:10])}...")  # 상위 10개 컬럼만
            
            return df
            
        except Exception as e:
            print(f"   ❌ 파일 읽기 오류: {e}")
            return None
    
    def analyze_wh_handling(self, df, vendor_name):
        """WH HANDLING 기반 분석"""
        print(f"\n🔍 {vendor_name} WH HANDLING 분석 중...")
        
        if df is None or len(df) == 0:
            print(f"   ❌ 분석할 데이터가 없습니다")
            return None
        
        # WH HANDLING 관련 컬럼 찾기
        wh_columns = []
        for col in df.columns:
            col_lower = str(col).lower()
            if any(keyword in col_lower for keyword in ['wh', 'warehouse', 'handling', '창고']):
                wh_columns.append(col)
        
        print(f"   📋 WH 관련 컬럼: {wh_columns}")
        
        # 기존 'wh handling' 컬럼이 있는지 확인
        wh_handling_col = None
        for col in df.columns:
            if 'wh handling' in str(col).lower():
                wh_handling_col = col
                break
        
        if wh_handling_col:
            print(f"   ✅ 'wh handling' 컬럼 발견: {wh_handling_col}")
            return self.count_by_wh_handling(df, wh_handling_col, vendor_name)
        else:
            print(f"   🔄 WH HANDLING 컬럼 자동 계산 시도...")
            return self.calculate_wh_handling(df, wh_columns, vendor_name)
    
    def count_by_wh_handling(self, df, wh_col, vendor_name):
        """기존 WH HANDLING 컬럼으로 카운팅"""
        print(f"   📊 {wh_col} 컬럼 기반 카운팅...")
        
        # WH HANDLING 값 분포 확인
        wh_values = df[wh_col].value_counts().sort_index()
        print(f"   📈 WH HANDLING 분포:")
        
        flow_distribution = {}
        total_count = len(df)
        
        for wh_value, count in wh_values.items():
            # NaN 값 처리
            if pd.isna(wh_value):
                flow_code = 0  # 직접운송으로 간주
            else:
                flow_code = int(wh_value) if isinstance(wh_value, (int, float)) else 0
            
            # Flow Code가 범위를 벗어나면 조정
            if flow_code > 3:
                flow_code = 3
            elif flow_code < 0:
                flow_code = 0
                
            flow_distribution[flow_code] = flow_distribution.get(flow_code, 0) + count
            
            flow_desc = self.flow_code_mapping.get(flow_code, {}).get('korean', f'Code {flow_code}')
            print(f"      Code {flow_code} ({flow_desc}): {count:,}건")
        
        # 결과 저장
        result = {
            'vendor': vendor_name,
            'total': total_count,
            'distribution': flow_distribution,
            'source_column': wh_col
        }
        
        return result
    
    def calculate_wh_handling(self, df, wh_columns, vendor_name):
        """WH 컬럼들을 기반으로 WH HANDLING 계산"""
        print(f"   🔄 WH HANDLING 자동 계산...")
        
        if not wh_columns:
            # WH 컬럼이 없으면 전체를 직접운송으로 간주
            print(f"   ⚠️  WH 관련 컬럼이 없음 - 전체 직접운송으로 간주")
            total_count = len(df)
            return {
                'vendor': vendor_name,
                'total': total_count,
                'distribution': {0: total_count},
                'source_column': 'auto_calculated'
            }
        
        # Excel 피벗 테이블과 동일한 로직 적용 (SUMPRODUCT 방식)
        wh_handling_counts = []
        
        for index, row in df.iterrows():
            count = 0
            for col in wh_columns:
                if pd.notna(row[col]) and str(row[col]).strip() != '':
                    # 숫자인 경우 처리
                    try:
                        value = float(row[col])
                        if not np.isnan(value) and value != 0:
                            count += 1
                    except:
                        # 문자열인 경우 공백이 아니면 카운트
                        if str(row[col]).strip():
                            count += 1
            
            wh_handling_counts.append(count)
        
        # Flow Code 분포 계산
        flow_distribution = {}
        for count in wh_handling_counts:
            flow_code = min(count, 3)  # 최대 3으로 제한
            flow_distribution[flow_code] = flow_distribution.get(flow_code, 0) + 1
        
        # 결과 출력
        total_count = len(df)
        for flow_code, count in sorted(flow_distribution.items()):
            flow_desc = self.flow_code_mapping.get(flow_code, {}).get('korean', f'Code {flow_code}')
            print(f"      Code {flow_code} ({flow_desc}): {count:,}건")
        
        result = {
            'vendor': vendor_name,
            'total': total_count,
            'distribution': flow_distribution,
            'source_column': f'calculated_from_{len(wh_columns)}_columns'
        }
        
        return result
    
    def process_all_files(self):
        """모든 파일 처리"""
        print(f"\n🚀 실제 데이터 파일 처리 시작...")
        
        for vendor_name, file_path in self.data_paths.items():
            print(f"\n" + "="*60)
            print(f"📊 {vendor_name} 데이터 처리")
            print(f"="*60)
            
            # Excel 파일 읽기
            df = self.read_excel_file(file_path, vendor_name)
            
            if df is not None:
                # WH HANDLING 분석
                result = self.analyze_wh_handling(df, vendor_name)
                
                if result:
                    self.real_data[vendor_name] = result
                else:
                    print(f"   ❌ {vendor_name} 분석 실패")
            else:
                print(f"   ❌ {vendor_name} 파일 읽기 실패")
    
    def generate_summary_report(self):
        """요약 리포트 생성"""
        print(f"\n" + "="*80)
        print(f"📊 MACHO {MACHO_VERSION} 실제 데이터 카운팅 결과")
        print(f"="*80)
        
        total_processed = 0
        overall_distribution = {0: 0, 1: 0, 2: 0, 3: 0}
        
        for vendor_name, data in self.real_data.items():
            print(f"\n🏢 **{vendor_name}:**")
            print(f"   📊 총 건수: {data['total']:,}건")
            print(f"   📋 데이터 소스: {data['source_column']}")
            print(f"   📈 Flow Code 분포:")
            
            total_processed += data['total']
            
            for flow_code in sorted(data['distribution'].keys()):
                count = data['distribution'][flow_code]
                flow_desc = self.flow_code_mapping.get(flow_code, {}).get('korean', f'Code {flow_code}')
                percentage = (count / data['total'] * 100) if data['total'] > 0 else 0
                print(f"      Code {flow_code} ({flow_desc}): {count:,}건 ({percentage:.1f}%)")
                
                overall_distribution[flow_code] += count
        
        print(f"\n📊 **전체 통합 결과:**")
        print(f"   📈 총 처리 건수: {total_processed:,}건")
        print(f"   📊 Flow Code 통합 분포:")
        
        for flow_code in sorted(overall_distribution.keys()):
            count = overall_distribution[flow_code]
            flow_desc = self.flow_code_mapping.get(flow_code, {}).get('korean', f'Code {flow_code}')
            percentage = (count / total_processed * 100) if total_processed > 0 else 0
            print(f"      Code {flow_code} ({flow_desc}): {count:,}건 ({percentage:.1f}%)")
        
        print(f"\n✅ **실제 데이터 기반 카운팅 완료!**")
        print(f"="*80)
        
        return {
            'total_processed': total_processed,
            'vendor_data': self.real_data,
            'overall_distribution': overall_distribution
        }

def main():
    """메인 실행 함수"""
    print("🚀 HVDC 실제 데이터 카운터 실행")
    
    try:
        # 카운터 초기화
        counter = RealDataCounter()
        
        # 모든 파일 처리
        counter.process_all_files()
        
        # 요약 리포트 생성
        summary = counter.generate_summary_report()
        
        print(f"\n🎯 **추천 명령어:**")
        print(f"/update_comprehensive_reporter [실제 데이터로 리포터 업데이트]")
        print(f"/generate_excel_with_real_data [실제 데이터 기반 Excel 리포트 생성]")
        print(f"/compare_simulation_vs_real [시뮬레이션 vs 실제 데이터 비교]")
        
        return True
        
    except Exception as e:
        print(f"❌ 실제 데이터 카운팅 실패: {e}")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print(f"\n✅ MACHO {MACHO_VERSION} 실제 데이터 카운팅 완료!")
    else:
        print(f"\n❌ 실제 데이터 카운팅 실패")
        sys.exit(1) 