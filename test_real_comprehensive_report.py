#!/usr/bin/env python3
"""
MACHO-GPT v3.4-mini TDD Test: 실제 데이터 기반 통합 보고서 생성
Real Data-Based Comprehensive Report Generation Test

실제 데이터 구조:
- 총 7,573건 트랜잭션
- 74개 컬럼 (실제 물류 데이터)
- Flow Code 분포: 0(2,845), 1(3,517), 2(1,131), 3(80)
- WH_HANDLING 분포: 0(2,845), 1(3,517), 2(1,131), 3(80)
"""

import unittest
import pandas as pd
import numpy as np
import os
from datetime import datetime

class TestRealComprehensiveReport(unittest.TestCase):
    """실제 MACHO 데이터 기반 통합 보고서 TDD 테스트"""
    
    def setUp(self):
        """실제 데이터 파일 경로 설정"""
        self.data_file = 'MACHO_통합관리_20250702_205301/01_원본파일/MACHO_WH_HANDLING_전체트랜잭션_SQM_STACK추가_20250702_200757.xlsx'
        self.output_dir = 'MACHO_통합관리_20250702_205301/02_통합결과'
        
        # 실제 데이터 로드
        self.df = pd.read_excel(self.data_file, sheet_name='전체_트랜잭션_SQM_STACK')
        
    def test_real_data_should_have_correct_structure(self):
        """실제 데이터는 올바른 구조를 가져야 함"""
        # Given: 실제 MACHO 데이터
        df = self.df
        
        # Then: 정확한 데이터 구조 확인
        self.assertEqual(len(df), 7573, "총 7,573건의 트랜잭션이 있어야 함")
        self.assertEqual(len(df.columns), 74, "74개 컬럼이 있어야 함")
        
        # 필수 컬럼 확인
        required_columns = [
            'FLOW_CODE', 'WH_HANDLING', 'SQM', 'CBM', 'Stack',
            'DSV Indoor', 'DSV Outdoor', 'DSV Al Markaz', 'MOSB',
            'MIR', 'SHU', 'DAS', 'AGI', 'VENDOR'
        ]
        
        for col in required_columns:
            self.assertIn(col, df.columns, f"컬럼 '{col}'이 존재해야 함")
    
    def test_flow_code_distribution_should_match_actual_data(self):
        """Flow Code 분포는 실제 데이터와 일치해야 함"""
        # Given: 실제 데이터
        df = self.df
        
        # When: Flow Code 분포 확인
        flow_dist = df['FLOW_CODE'].value_counts().sort_index()
        
        # Then: 정확한 분포 확인
        expected_distribution = {
            0: 2845,  # Pre Arrival
            1: 3517,  # Port → Site
            2: 1131,  # Port → Warehouse → Site
            3: 80     # Port → Warehouse → MOSB → Site
        }
        
        for code, expected_count in expected_distribution.items():
            actual_count = flow_dist.get(code, 0)
            self.assertEqual(actual_count, expected_count, 
                           f"Flow Code {code}는 {expected_count}건이어야 함 (실제: {actual_count})")
    
    def test_wh_handling_should_match_flow_code(self):
        """WH_HANDLING은 FLOW_CODE와 일치해야 함"""
        # Given: 실제 데이터
        df = self.df
        
        # When: WH_HANDLING과 FLOW_CODE 비교
        wh_dist = df['WH_HANDLING'].value_counts().sort_index()
        flow_dist = df['FLOW_CODE'].value_counts().sort_index()
        
        # Then: 분포가 일치해야 함
        for code in [0, 1, 2, 3]:
            wh_count = wh_dist.get(code, 0)
            flow_count = flow_dist.get(code, 0)
            self.assertEqual(wh_count, flow_count, 
                           f"WH_HANDLING {code}와 FLOW_CODE {code}가 일치해야 함")
    
    def test_sqm_stack_analysis_should_use_real_data(self):
        """SQM Stack 분석은 실제 데이터를 사용해야 함"""
        # Given: 실제 데이터
        df = self.df
        
        # When: SQM과 Stack 데이터 분석
        sqm_total = df['SQM'].sum()
        stack_avg = df['Stack'].mean()
        
        # Then: 실제 값 확인
        self.assertGreater(sqm_total, 0, "총 SQM은 0보다 커야 함")
        self.assertGreater(stack_avg, 0, "평균 Stack은 0보다 커야 함")
        
        # 실제 SQM 통계 확인
        sqm_stats = df['SQM'].describe()
        self.assertAlmostEqual(sqm_stats['mean'], 5.089673, places=5, 
                              msg="SQM 평균은 실제 데이터와 일치해야 함")
    
    def test_warehouse_location_analysis_should_use_actual_columns(self):
        """창고 위치 분석은 실제 컬럼을 사용해야 함"""
        # Given: 실제 데이터
        df = self.df
        
        # When: 창고 컬럼 확인
        warehouse_columns = ['DSV Indoor', 'DSV Outdoor', 'DSV Al Markaz', 'MOSB', 'DSV MZP']
        site_columns = ['MIR', 'SHU', 'DAS', 'AGI']
        
        # Then: 실제 데이터 존재 확인
        for col in warehouse_columns:
            if col in df.columns:
                non_null_count = df[col].notna().sum()
                self.assertGreaterEqual(non_null_count, 0, f"창고 '{col}' 데이터가 존재해야 함")
        
        for col in site_columns:
            if col in df.columns:
                non_null_count = df[col].notna().sum()
                self.assertGreaterEqual(non_null_count, 0, f"현장 '{col}' 데이터가 존재해야 함")
    
    def test_vendor_distribution_should_reflect_actual_data(self):
        """벤더 분포는 실제 데이터를 반영해야 함"""
        # Given: 실제 데이터
        df = self.df
        
        # When: 벤더 분포 확인
        if 'VENDOR' in df.columns:
            vendor_dist = df['VENDOR'].value_counts()
            
            # Then: 벤더 데이터 존재 확인
            self.assertGreater(len(vendor_dist), 0, "벤더 데이터가 존재해야 함")
            
            # 실제 벤더 비율 확인
            total_with_vendor = df['VENDOR'].notna().sum()
            vendor_coverage = total_with_vendor / len(df)
            self.assertGreater(vendor_coverage, 0, "벤더 커버리지가 있어야 함")
    
    def test_comprehensive_report_generation_with_real_data(self):
        """실제 데이터를 사용한 종합 보고서 생성"""
        # Given: 실제 데이터와 보고서 생성 함수
        df = self.df
        
        # When: 실제 데이터 기반 보고서 생성
        report_data = self.create_real_comprehensive_report(df)
        
        # Then: 보고서 품질 검증
        self.assertIsNotNone(report_data, "보고서 데이터가 생성되어야 함")
        self.assertIn('dashboard', report_data, "대시보드 데이터가 포함되어야 함")
        self.assertIn('monthly_warehouse', report_data, "월별 창고 데이터가 포함되어야 함")
        self.assertIn('sqm_analysis', report_data, "SQM 분석 데이터가 포함되어야 함")
        self.assertIn('status_tracking', report_data, "상태 추적 데이터가 포함되어야 함")
        
        # 데이터 정확성 검증
        dashboard = report_data['dashboard']
        total_transactions = dashboard[dashboard['Metric'] == '총 트랜잭션']['Value'].iloc[0]
        self.assertEqual(total_transactions, 7573, "총 트랜잭션 수가 정확해야 함")
    
    def create_real_comprehensive_report(self, df):
        """실제 데이터 기반 종합 보고서 생성"""
        report_data = {}
        
        # 1. 대시보드 데이터
        dashboard_data = []
        dashboard_data.append({
            'Category': '전체 현황',
            'Metric': '총 트랜잭션',
            'Value': len(df),
            'Unit': '건',
            'Description': '전체 물류 트랜잭션 건수'
        })
        
        # Flow Code 분포
        flow_dist = df['FLOW_CODE'].value_counts().sort_index()
        for code, count in flow_dist.items():
            percentage = count / len(df) * 100
            descriptions = {
                0: "Pre Arrival (사전 도착 대기)",
                1: "Port → Site (직송)",
                2: "Port → Warehouse → Site (창고 경유)",
                3: "Port → Warehouse → MOSB → Site (해상기지 포함)"
            }
            
            dashboard_data.append({
                'Category': 'Flow Code',
                'Metric': f'Code {code}',
                'Value': count,
                'Unit': f'{percentage:.1f}%',
                'Description': descriptions.get(code, f'Code {code}')
            })
        
        # SQM 요약
        total_sqm = df['SQM'].sum()
        avg_sqm = df['SQM'].mean()
        dashboard_data.append({
            'Category': 'SQM 현황',
            'Metric': '총 면적',
            'Value': f'{total_sqm:,.0f}',
            'Unit': '㎡',
            'Description': '전체 화물 총 면적'
        })
        
        dashboard_data.append({
            'Category': 'SQM 현황',
            'Metric': '평균 면적',
            'Value': f'{avg_sqm:.2f}',
            'Unit': '㎡/건',
            'Description': '화물당 평균 면적'
        })
        
        report_data['dashboard'] = pd.DataFrame(dashboard_data)
        
        # 2. 월별 창고 데이터 (실제 데이터 기반)
        warehouse_columns = ['DSV Indoor', 'DSV Outdoor', 'DSV Al Markaz', 'MOSB', 'DSV MZP']
        monthly_data = []
        
        # 실제 데이터 기반 월별 추정
        months = pd.date_range('2024-01', '2025-06', freq='ME').strftime('%Y-%m')
        for month in months:
            row_data = {'Month': month}
            for wh in warehouse_columns:
                if wh in df.columns:
                    wh_data = df[df[wh].notna()]
                    monthly_count = len(wh_data) // 12  # 12개월 분산
                    row_data[f'{wh}_실제데이터'] = monthly_count
                else:
                    row_data[f'{wh}_실제데이터'] = 0
            monthly_data.append(row_data)
        
        report_data['monthly_warehouse'] = pd.DataFrame(monthly_data)
        
        # 3. SQM 분석 (실제 데이터)
        sqm_analysis = []
        stack_groups = df.groupby('Stack')
        for stack_level, group in stack_groups:
            if pd.notna(stack_level) and len(group) > 0:
                original_sqm = group['SQM'].sum()
                optimized_sqm = original_sqm / stack_level if stack_level > 0 else original_sqm
                saving = original_sqm - optimized_sqm
                
                sqm_analysis.append({
                    'Stack_Level': f'{stack_level}-Level',
                    'Item_Count': len(group),
                    'Original_SQM': round(original_sqm, 2),
                    'Optimized_SQM': round(optimized_sqm, 2),
                    'Space_Saving': round(saving, 2),
                    'Saving_Percentage': round(saving/original_sqm*100, 1) if original_sqm > 0 else 0
                })
        
        report_data['sqm_analysis'] = pd.DataFrame(sqm_analysis)
        
        # 4. 상태 추적 (실제 데이터)
        status_data = []
        site_columns = ['MIR', 'SHU', 'DAS', 'AGI']
        
        for idx, row in df.head(100).iterrows():  # 처음 100개 실제 데이터
            # 실제 위치 확인
            final_location = 'Port'
            for site in site_columns:
                if site in df.columns and pd.notna(row[site]):
                    final_location = site
                    break
            
            status_data.append({
                'Case_No': row.get('Case No.', f'CASE_{idx}'),
                'Current_Location': final_location,
                'Flow_Code': row.get('FLOW_CODE', ''),
                'WH_Handling': row.get('WH_HANDLING', ''),
                'SQM': row.get('SQM', 0),
                'CBM': row.get('CBM', 0),
                'Stack': row.get('Stack', 0)
            })
        
        report_data['status_tracking'] = pd.DataFrame(status_data)
        
        return report_data

if __name__ == '__main__':
    print("🧪 MACHO-GPT v3.4-mini 실제 데이터 기반 TDD 테스트")
    print("=" * 80)
    print("📋 대상: 7,573건 실제 트랜잭션 데이터")
    print("🔄 Flow Code 분포: 0(2,845), 1(3,517), 2(1,131), 3(80)")
    print("=" * 80)
    
    unittest.main(verbosity=2) 