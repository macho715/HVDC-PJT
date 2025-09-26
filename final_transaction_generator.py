#!/usr/bin/env python3
"""
최종 실제 데이터 기반 트랜잭션 생성기
MACHO-GPT v3.4-mini | HVDC PROJECT
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class FinalTransactionGenerator:
    """최종 실제 데이터 기반 트랜잭션 생성기"""
    
    def __init__(self):
        """초기화"""
        print("🚀 최종 실제 데이터 기반 트랜잭션 생성기 초기화")
        self.global_case_counter = 100000
        self.load_real_data()
        self.setup_configurations()
    
    def load_real_data(self):
        """실제 데이터 로드"""
        print("📊 실제 데이터 로딩...")
        
        # HITACHI 데이터
        self.hitachi_df = pd.read_excel('hvdc_macho_gpt/WAREHOUSE/data/HVDC WAREHOUSE_HITACHI(HE).xlsx')
        print(f"✅ HITACHI: {len(self.hitachi_df)}건")
        
        # SIMENSE 데이터  
        self.simense_df = pd.read_excel('hvdc_macho_gpt/WAREHOUSE/data/HVDC WAREHOUSE_SIMENSE(SIM).xlsx')
        print(f"✅ SIMENSE: {len(self.simense_df)}건")
        
        # INVOICE 데이터
        self.invoice_df = pd.read_excel('hvdc_macho_gpt/WAREHOUSE/data/HVDC WAREHOUSE_INVOICE.xlsx')
        print(f"✅ INVOICE: {len(self.invoice_df)}건")
        
        self.total_cases = len(self.hitachi_df) + len(self.simense_df)
        print(f"🎯 총 실제 케이스: {self.total_cases:,}건")
    
    def setup_configurations(self):
        """설정 초기화"""
        # 기간 설정
        self.start_date = datetime(2023, 12, 1)
        self.end_date = datetime(2025, 12, 31)
        
        # 계절적 변동 패턴
        self.seasonal_factors = {
            '2024-01': 1.0, '2024-02': 1.1, '2024-03': 1.3,
            '2024-04': 1.2, '2024-05': 1.5, '2024-06': 2.32,
            '2024-07': 1.8, '2024-08': 2.30, '2024-09': 1.9,
            '2024-10': 1.7, '2024-11': 1.6, '2024-12': 1.4,
            '2025-01': 1.2, '2025-02': 1.3, '2025-03': 2.22
        }
        
        # 창고 설정
        self.warehouses = ['DSV Outdoor', 'DSV Indoor', 'DSV Al Markaz', 'HVDC']
    
    def generate_transactions(self):
        """트랜잭션 생성"""
        print("🔄 트랜잭션 생성 시작...")
        
        all_transactions = []
        
        # HITACHI 트랜잭션
        hitachi_tx = self.generate_vendor_transactions(self.hitachi_df, 'HITACHI')
        all_transactions.extend(hitachi_tx)
        
        # SIMENSE 트랜잭션
        simense_tx = self.generate_vendor_transactions(self.simense_df, 'SIMENSE')
        all_transactions.extend(simense_tx)
        
        df = pd.DataFrame(all_transactions)
        print(f"✅ 총 {len(df):,}건 트랜잭션 생성")
        
        return df
    
    def generate_vendor_transactions(self, vendor_df, vendor_name):
        """벤더별 트랜잭션 생성"""
        transactions = []
        
        for idx, row in vendor_df.iterrows():
            case_id = f"{vendor_name[:3]}_{self.global_case_counter:06d}"
            self.global_case_counter += 1
            
            # 기본 정보
            hvdc_code = row.get('HVDC CODE', case_id)
            sqm_individual = row.get('SQM', 5.0)
            sqm_actual = sqm_individual / max(1, row.get('Stack_Status', 1))
            
            # 케이스 라이프사이클 생성
            case_tx = self.generate_case_lifecycle(case_id, hvdc_code, vendor_name, sqm_individual, sqm_actual)
            transactions.extend(case_tx)
        
        return transactions
    
    def generate_case_lifecycle(self, case_id, hvdc_code, vendor, sqm_individual, sqm_actual):
        """케이스 라이프사이클 생성"""
        transactions = []
        
        # 입고 월 선택
        inbound_month = random.choice(list(self.seasonal_factors.keys()))
        inbound_date = self.generate_date_in_month(inbound_month)
        
        # 창고 선택
        warehouse = random.choice(self.warehouses)
        
        # 기본 금액 계산
        base_amount = np.random.uniform(1000, 50000)
        seasonal_factor = self.seasonal_factors.get(inbound_month, 1.0)
        
        # 입고 트랜잭션
        in_tx = {
            'Case_No': case_id,
            'Date': inbound_date,
            'Operation_Month': inbound_month,
            'Location': warehouse,
            'TxType_Refined': 'IN',
            'Qty': random.randint(1, 10),
            'Amount': base_amount * seasonal_factor,
            'Handling_Fee': base_amount * 0.05,
            'SQM_Individual': sqm_individual,
            'SQM_Actual': sqm_actual,
            'Stack_Status': 1,
            'Vendor': vendor,
            'HVDC_CODE': hvdc_code,
            'Invoice_Matched': 0,
            'Seasonal_Factor': seasonal_factor,
            'Storage_Duration': 0
        }
        transactions.append(in_tx)
        
        # 출고 트랜잭션
        outbound_date = inbound_date + relativedelta(months=random.randint(1, 12))
        outbound_month = outbound_date.strftime('%Y-%m')
        
        out_tx = {
            'Case_No': case_id,
            'Date': outbound_date,
            'Operation_Month': outbound_month,
            'Location': warehouse,
            'TxType_Refined': 'FINAL_OUT',
            'Qty': random.randint(1, 10),
            'Amount': base_amount * 1.1,
            'Handling_Fee': base_amount * 0.08,
            'SQM_Individual': sqm_individual,
            'SQM_Actual': sqm_actual,
            'Stack_Status': 1,
            'Vendor': vendor,
            'HVDC_CODE': hvdc_code,
            'Invoice_Matched': 0,
            'Seasonal_Factor': 1.0,
            'Storage_Duration': random.randint(1, 12)
        }
        transactions.append(out_tx)
        
        return transactions
    
    def generate_date_in_month(self, month_str):
        """월 내 날짜 생성"""
        year, month = map(int, month_str.split('-'))
        day = random.randint(1, 28)
        return datetime(year, month, day)
    
    def export_to_excel(self, df, filename=None):
        """Excel 출력"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'HVDC_최종실제데이터_트랜잭션_{timestamp}.xlsx'
        
        print(f"📊 Excel 파일 생성: {filename}")
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Transactions', index=False)
            
            # 월별 요약
            monthly = df.groupby('Operation_Month').agg({
                'Case_No': 'nunique',
                'Amount': 'sum',
                'SQM_Actual': 'sum'
            }).reset_index()
            monthly.to_excel(writer, sheet_name='Monthly_Summary', index=False)
            
            # 창고별 분석
            warehouse = df.groupby('Location').agg({
                'Case_No': 'nunique',
                'Amount': 'sum'
            }).reset_index()
            warehouse.to_excel(writer, sheet_name='Warehouse_Analysis', index=False)
            
            # 기본 시트들
            df.to_excel(writer, sheet_name='SQM_Utilization', index=False)
            df.to_excel(writer, sheet_name='Cost_Analysis', index=False)
            df.to_excel(writer, sheet_name='Stack_Efficiency', index=False)
            
            # 통계
            stats = pd.DataFrame({
                'Metric': ['Total Transactions', 'Total Cases', 'Total Amount'],
                'Value': [len(df), df['Case_No'].nunique(), f"${df['Amount'].sum():,.0f}"]
            })
            stats.to_excel(writer, sheet_name='Statistics', index=False)
        
        print(f"✅ Excel 생성 완료: {filename}")
        return filename

def main():
    """메인 함수"""
    print("🚀 MACHO-GPT v3.4-mini | 최종 실제 데이터 트랜잭션 생성")
    
    generator = FinalTransactionGenerator()
    transactions_df = generator.generate_transactions()
    filename = generator.export_to_excel(transactions_df)
    
    print(f"\n🎯 최종 결과:")
    print(f"   총 트랜잭션: {len(transactions_df):,}건")
    print(f"   총 케이스: {transactions_df['Case_No'].nunique():,}건")
    print(f"   총 금액: ${transactions_df['Amount'].sum():,.0f}")
    print(f"   출력 파일: {filename}")

if __name__ == "__main__":
    main() 