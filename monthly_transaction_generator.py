#!/usr/bin/env python3
"""
MACHO-GPT v3.4-mini: 월별 입고/출고 트랜잭션 생성기 (실제 데이터 기반)
실제 HVDC 데이터 7,573개 케이스를 기반으로 25개월 트랜잭션 생성
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import json
from typing import Dict, List, Tuple

class MachoTransactionGenerator:
    def __init__(self):
        """MACHO v2.8.4 실제 데이터 기반 트랜잭션 생성기"""
        
        # === 실제 데이터 현황 ===
        self.actual_items = {
            'HITACHI': 5346,  # 실제 HITACHI 케이스 수
            'SIMENSE': 2227   # 실제 SIMENSE 케이스 수
        }
        self.total_cases = sum(self.actual_items.values())  # 7,573개
        
        # === 기간 설정 ===
        self.start_date = datetime(2023, 12, 1)
        self.end_date = datetime(2025, 12, 31)
        self.months = []
        current = self.start_date
        while current <= self.end_date:
            self.months.append(current.strftime('%Y-%m'))
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)
        
        print(f"📊 실제 데이터 기반: {self.total_cases:,}개 케이스 × {len(self.months)}개월")
        
        # === INVOICE 매칭 데이터 로드 ===
        self.load_invoice_mapping()
        
        # === 실제 데이터 로드 ===
        self.load_actual_data()
        
        # === 창고 설정 ===
        self.warehouses = {
            'DSV Indoor': {
                'capacity': 2000,
                'utilization': 0.75,
                'storage_types': ['Indoor', 'Climate Control'],
                'distribution': 0.191  # 19.1%
            },
            'DSV Al Markaz': {
                'capacity': 2500,
                'utilization': 0.82,
                'storage_types': ['Outdoor', 'Heavy Equipment'],
                'distribution': 0.302  # 30.2%
            },
            'DSV Outdoor': {
                'capacity': 3000,
                'utilization': 0.88,
                'storage_types': ['Outdoor', 'Large Equipment'],
                'distribution': 0.360  # 36.0%
            },
            'MOSB': {
                'capacity': 1500,
                'utilization': 0.65,
                'storage_types': ['Special', 'Final Assembly'],
                'distribution': 0.147  # 14.7%
            }
        }
        
        # === 계절 요인 (실제 데이터 패턴) ===
        self.seasonal_factors = {
            '2023-12': 1.05, '2024-01': 0.85, '2024-02': 0.90, '2024-03': 1.15,
            '2024-04': 1.25, '2024-05': 1.45, '2024-06': 2.32, '2024-07': 1.95,
            '2024-08': 2.30, '2024-09': 1.80, '2024-10': 1.65, '2024-11': 1.40,
            '2024-12': 1.20, '2025-01': 0.95, '2025-02': 1.05, '2025-03': 2.22,
            '2025-04': 1.75, '2025-05': 1.55, '2025-06': 1.85, '2025-07': 1.60,
            '2025-08': 1.45, '2025-09': 1.30, '2025-10': 1.15, '2025-11': 1.00,
            '2025-12': 0.80
        }
        
        # === 트랜잭션 설정 ===
        self.transaction_types = {
            'IN': {'ratio': 0.40, 'description': '입고'},           # 40%
            'TRANSFER_OUT': {'ratio': 0.35, 'description': '창고이동'},  # 35%
            'FINAL_OUT': {'ratio': 0.25, 'description': '최종출고'}     # 25%
        }
        
        self.global_sequence = 100001  # 케이스 ID 시퀀스
        
    def load_invoice_mapping(self):
        """INVOICE 매칭 데이터 로드 및 비용 분포 분석"""
        try:
            # INVOICE 데이터 로드
            df_invoice = pd.read_excel('hvdc_macho_gpt/WAREHOUSE/data/HVDC WAREHOUSE_INVOICE.xlsx')
            df_hitachi = pd.read_excel('hvdc_macho_gpt/WAREHOUSE/data/HVDC WAREHOUSE_HITACHI(HE).xlsx')
            df_simense = pd.read_excel('hvdc_macho_gpt/WAREHOUSE/data/HVDC WAREHOUSE_SIMENSE(SIM).xlsx')
            
            # INVOICE 모든 HVDC CODE 수집
            invoice_hvdc_cols = ['HVDC CODE', 'HVDC CODE 1', 'HVDC CODE 2', 'HVDC CODE 3', 'HVDC CODE 4']
            invoice_codes = set()
            for col in invoice_hvdc_cols:
                if col in df_invoice.columns:
                    codes = df_invoice[col].dropna().astype(str)
                    invoice_codes.update(codes)
            
            # HITACHI 매칭
            hitachi_hvdc_cols = ['HVDC CODE', 'HVDC CODE 1', 'HVDC CODE 2', 'HVDC CODE 3', 'HVDC CODE 4']
            hitachi_codes = set()
            for col in hitachi_hvdc_cols:
                if col in df_hitachi.columns:
                    codes = df_hitachi[col].dropna().astype(str)
                    hitachi_codes.update(codes)
            hitachi_matched = invoice_codes & hitachi_codes
            
            # SIMENSE 매칭
            simense_hvdc_cols = ['HVDC CODE', 'HVDC CODE 1', 'HVDC CODE 2', 'HVDC CODE 3', 'HVDC CODE 4', 'HVDC CODE 5']
            simense_codes = set()
            for col in simense_hvdc_cols:
                if col in df_simense.columns:
                    codes = df_simense[col].dropna().astype(str)
                    simense_codes.update(codes)
            simense_matched = invoice_codes & simense_codes
            
            # 매칭된 케이스의 실제 비용 분포 분석
            self.invoice_cost_analysis = {
                'hitachi_matched': list(hitachi_matched),
                'simense_matched': list(simense_matched),
                'total_matched': len(hitachi_matched) + len(simense_matched),
                'match_rate': (len(hitachi_matched) + len(simense_matched)) / len(invoice_codes) * 100
            }
            
            # 실제 INVOICE 비용 통계
            total_costs = df_invoice['TOTAL'].dropna()
            self.invoice_cost_stats = {
                'min': total_costs.min(),
                'max': total_costs.max(),
                'mean': total_costs.mean(),
                'median': total_costs.median(),
                'q25': total_costs.quantile(0.25),
                'q75': total_costs.quantile(0.75),
                'std': total_costs.std()
            }
            
            print(f"✅ INVOICE 매칭 완료: HITACHI {len(hitachi_matched)}개, SIMENSE {len(simense_matched)}개")
            print(f"   총 매칭률: {self.invoice_cost_analysis['match_rate']:.1f}%")
            print(f"   실제 비용 범위: ${self.invoice_cost_stats['min']:,.0f} ~ ${self.invoice_cost_stats['max']:,.0f}")
            print(f"   평균/중간값: ${self.invoice_cost_stats['mean']:,.0f} / ${self.invoice_cost_stats['median']:,.0f}")
            
        except Exception as e:
            print(f"⚠️ INVOICE 매칭 로드 실패: {e}")
            # 기본값 설정
            self.invoice_cost_analysis = {'total_matched': 0, 'match_rate': 0}
            self.invoice_cost_stats = {
                'min': 659, 'max': 350439, 'mean': 24816, 'median': 4115,
                'q25': 659, 'q75': 16859, 'std': 45000
            }
    
    def load_actual_data(self):
        """실제 HVDC 데이터 로드"""
        try:
            # HITACHI 데이터
            df_hitachi = pd.read_excel('hvdc_macho_gpt/WAREHOUSE/data/HVDC WAREHOUSE_HITACHI(HE).xlsx')
            # SIMENSE 데이터  
            df_simense = pd.read_excel('hvdc_macho_gpt/WAREHOUSE/data/HVDC WAREHOUSE_SIMENSE(SIM).xlsx')
            
            print(f"✅ 실제 데이터 로드: HITACHI {len(df_hitachi):,}건, SIMENSE {len(df_simense):,}건")
            
            # 실제 케이스 ID 추출
            self.actual_case_ids = []
            
            # HITACHI 케이스 ID
            if 'HVDC CODE' in df_hitachi.columns:
                hitachi_cases = df_hitachi['HVDC CODE'].dropna().astype(str).tolist()
                self.actual_case_ids.extend([f"HIT_{case}" for case in hitachi_cases])
            
            # SIMENSE 케이스 ID
            if 'SERIAL NO.' in df_simense.columns:
                simense_cases = df_simense['SERIAL NO.'].dropna().astype(str).tolist()
                self.actual_case_ids.extend([f"SIM_{case}" for case in simense_cases])
                
            print(f"📋 실제 케이스 ID 추출: {len(self.actual_case_ids):,}개")
            
        except FileNotFoundError:
            print("⚠️ 실제 데이터 파일을 찾을 수 없어 가상 케이스 ID 생성")
            self.generate_virtual_case_ids()
        except Exception as e:
            print(f"⚠️ 데이터 로드 오류: {e}, 가상 케이스 ID 생성")
            self.generate_virtual_case_ids()
    
    def generate_virtual_case_ids(self):
        """가상 케이스 ID 생성 (실제 데이터 미가용시)"""
        self.actual_case_ids = []
        
        # HITACHI 케이스 ID 생성
        for i in range(self.actual_items['HITACHI']):
            self.actual_case_ids.append(f"HIT_{100000 + i:06d}")
            
        # SIMENSE 케이스 ID 생성  
        for i in range(self.actual_items['SIMENSE']):
            self.actual_case_ids.append(f"SIM_{200000 + i:06d}")
    
    def assign_case_to_lifecycle(self, case_id: str) -> Dict:
        """각 케이스의 생명주기 정의"""
        
        # 입고월 결정 (가중 분포)
        inbound_month = np.random.choice(
            self.months, 
            p=[self.seasonal_factors[m]/sum(self.seasonal_factors.values()) for m in self.months]
        )
        
        # 창고 배정
        warehouse = np.random.choice(
            list(self.warehouses.keys()),
            p=[self.warehouses[w]['distribution'] for w in self.warehouses.keys()]
        )
        
        # 생명주기 패턴 결정
        pattern = random.choices(
            ['direct', 'warehouse', 'multi_transfer'],
            weights=[0.3, 0.5, 0.2]  # 30% 직접, 50% 창고경유, 20% 다중이동
        )[0]
        
        lifecycle = {
            'case_id': case_id,
            'pattern': pattern,
            'inbound_month': inbound_month,
            'primary_warehouse': warehouse,
            'transactions': []
        }
        
        # 패턴별 트랜잭션 생성
        if pattern == 'direct':
            # 입고 → 바로 출고
            lifecycle['transactions'] = [
                {'type': 'IN', 'month': inbound_month, 'location': warehouse},
                {'type': 'FINAL_OUT', 'month': self.get_outbound_month(inbound_month), 'location': warehouse}
            ]
        elif pattern == 'warehouse':
            # 입고 → 창고보관 → 출고
            storage_months = random.randint(1, 6)  # 1-6개월 보관
            outbound_month = self.get_outbound_month(inbound_month, storage_months)
            lifecycle['transactions'] = [
                {'type': 'IN', 'month': inbound_month, 'location': warehouse},
                {'type': 'FINAL_OUT', 'month': outbound_month, 'location': warehouse}
            ]
        else:  # multi_transfer
            # 입고 → 창고이동 → 출고
            transfer_count = random.randint(1, 3)
            current_month = inbound_month
            current_warehouse = warehouse
            
            lifecycle['transactions'].append({
                'type': 'IN', 'month': current_month, 'location': current_warehouse
            })
            
            for _ in range(transfer_count):
                next_month = self.get_next_month(current_month, random.randint(1, 3))
                next_warehouse = random.choice([w for w in self.warehouses.keys() if w != current_warehouse])
                
                lifecycle['transactions'].extend([
                    {'type': 'TRANSFER_OUT', 'month': next_month, 'location': current_warehouse},
                    {'type': 'IN', 'month': next_month, 'location': next_warehouse}
                ])
                
                current_month = next_month
                current_warehouse = next_warehouse
            
            # 최종 출고
            final_month = self.get_outbound_month(current_month, random.randint(1, 4))
            lifecycle['transactions'].append({
                'type': 'FINAL_OUT', 'month': final_month, 'location': current_warehouse
            })
        
        return lifecycle
    
    def get_outbound_month(self, inbound_month: str, delay_months: int = None) -> str:
        """출고월 계산"""
        if delay_months is None:
            delay_months = random.randint(1, 8)  # 1-8개월 지연
            
        return self.get_next_month(inbound_month, delay_months)
    
    def get_next_month(self, current_month: str, months_ahead: int) -> str:
        """다음 월 계산"""
        year, month = map(int, current_month.split('-'))
        current_date = datetime(year, month, 1)
        
        for _ in range(months_ahead):
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
                
        return current_date.strftime('%Y-%m')
    
    def generate_transaction_data(self, case_id: str, transaction: Dict) -> Dict:
        """실제 INVOICE 비용 분포 기반 트랜잭션 데이터 생성"""
        
        # 기본 정보
        year, month = map(int, transaction['month'].split('-'))
        day = random.randint(1, 28)
        date = datetime(year, month, day)
        
        # 실제 INVOICE 통계 활용한 금액 계산
        stats = self.invoice_cost_stats
        
        # 90% 확률로 정상 범위 (Q25-Q75), 10% 확률로 극값
        if random.random() < 0.9:
            # 정상 범위: 25-75% 분위수 사이 ($659-$16,859)
            base_amount = random.uniform(stats['q25'], stats['q75'])
        else:
            # 극값: 최소값~Q25 또는 Q75~최대값
            if random.random() < 0.5:
                base_amount = random.uniform(stats['min'], stats['q25'])
            else:
                # 최대값 제한 (평균 + 2*표준편차)
                max_amount = min(stats['max'], stats['mean'] + 2*stats['std'])
                base_amount = random.uniform(stats['q75'], max_amount)
        
        # 재료 타입별 조정
        if 'HIT' in case_id:
            # HITACHI: 기본값 사용
            base_qty = random.randint(5, 50)
            amount_multiplier = 1.0
        else:  # SIMENSE
            # SIMENSE: 약간 낮은 경향
            base_qty = random.randint(3, 30)
            amount_multiplier = random.uniform(0.8, 1.0)
        
        # 트랜잭션 타입별 조정
        if transaction['type'] == 'TRANSFER_OUT':
            # 창고 이동: 핸들링 비용만 발생 (10-30%)
            amount_multiplier *= random.uniform(0.1, 0.3)
        elif transaction['type'] == 'FINAL_OUT':
            # 최종 출고: 전체 가치 반영 (100-120%)
            amount_multiplier *= random.uniform(1.0, 1.2)
        # IN은 기본값 사용 (입고 비용)
        
        # 계절 요인 적용
        seasonal_factor = self.seasonal_factors.get(transaction['month'], 1.0)
        qty = max(1, int(base_qty * seasonal_factor))
        final_amount = base_amount * amount_multiplier * seasonal_factor
        
        # 핸들링 비용 (실제 패턴 반영: 1.5-3.5%)
        handling_rate = random.uniform(0.015, 0.035)
        handling_fee = final_amount * handling_rate
        
        # 매칭 여부 확인
        is_invoice_matched = (
            case_id in getattr(self, 'invoice_cost_analysis', {}).get('hitachi_matched', []) or
            case_id in getattr(self, 'invoice_cost_analysis', {}).get('simense_matched', [])
        )
        
        return {
            'Case_No': case_id,
            'Date': date.strftime('%Y-%m-%d'),
            'Month': transaction['month'],
            'Location': transaction['location'],
            'TxType_Refined': transaction['type'],
            'Qty': qty,
            'Amount': round(final_amount, 2),
            'Handling_Fee': round(handling_fee, 2),
            'Unit_Price': round(final_amount / qty, 2),
            'Vendor': 'HITACHI' if 'HIT' in case_id else 'SIMENSE',
            'Status': 'Completed',
            'Invoice_Matched': is_invoice_matched,  # INVOICE 매칭 여부
            'Base_Amount': round(base_amount, 2),  # 원본 금액
            'Seasonal_Factor': round(seasonal_factor, 3)  # 계절 요인
        }
    
    def generate_monthly_transactions(self) -> pd.DataFrame:
        """월별 트랜잭션 생성 - 실제 케이스 기반"""
        
        print(f"\n🔄 {self.total_cases:,}개 케이스의 생명주기 분석 시작...")
        
        all_transactions = []
        
        # 각 실제 케이스에 대해 생명주기 정의
        for i, case_id in enumerate(self.actual_case_ids):
            if i % 1000 == 0:
                print(f"  진행률: {i:,}/{self.total_cases:,} ({i/self.total_cases*100:.1f}%)")
            
            lifecycle = self.assign_case_to_lifecycle(case_id)
            
            # 생명주기 내 모든 트랜잭션 생성
            for transaction in lifecycle['transactions']:
                tx_data = self.generate_transaction_data(case_id, transaction)
                all_transactions.append(tx_data)
        
        df = pd.DataFrame(all_transactions)
        
        # 날짜순 정렬
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values('Date').reset_index(drop=True)
        df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
        
        print(f"✅ 총 {len(df):,}건의 트랜잭션 생성 완료")
        print(f"   - 기간: {df['Date'].min()} ~ {df['Date'].max()}")
        print(f"   - 케이스 수: {df['Case_No'].nunique():,}개")
        
        return df
    
    def export_to_excel(self, df: pd.DataFrame, filename: str = None) -> str:
        """Excel 파일로 내보내기"""
        
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'HVDC_실제데이터기반_월별트랜잭션_{timestamp}.xlsx'
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            
            # 전체 트랜잭션
            df.to_excel(writer, sheet_name='전체_트랜잭션', index=False)
            
            # 월별 요약
            monthly_summary = df.groupby('Month').agg({
                'Case_No': 'nunique',
                'Qty': 'sum',
                'Amount': 'sum',
                'Handling_Fee': 'sum'
            }).round(2)
            monthly_summary.columns = ['케이스수', '총수량', '총금액', '총핸들링비']
            monthly_summary.to_excel(writer, sheet_name='월별_요약')
            
            # 창고별 요약
            warehouse_summary = df.groupby('Location').agg({
                'Case_No': 'nunique',
                'Qty': 'sum', 
                'Amount': 'sum',
                'Handling_Fee': 'sum'
            }).round(2)
            warehouse_summary.columns = ['케이스수', '총수량', '총금액', '총핸들링비']
            warehouse_summary.to_excel(writer, sheet_name='창고별_요약')
            
            # 트랜잭션 타입별 요약
            txtype_summary = df.groupby('TxType_Refined').agg({
                'Case_No': 'nunique',
                'Qty': 'sum',
                'Amount': 'sum',
                'Handling_Fee': 'sum'
            }).round(2)
            txtype_summary.columns = ['케이스수', '총수량', '총금액', '총핸들링비']
            txtype_summary.to_excel(writer, sheet_name='트랜잭션타입별_요약')
            
            # 통계 정보
            stats = {
                '항목': ['전체 트랜잭션 수', '전체 케이스 수', '총 처리량', '총 금액', '총 비용', '평균 단가'],
                '값': [
                    f"{len(df):,}건",
                    f"{df['Case_No'].nunique():,}개", 
                    f"{df['Qty'].sum():,}개",
                    f"${df['Amount'].sum():,.2f}",
                    f"${df['Handling_Fee'].sum():,.2f}",
                    f"${df['Unit_Price'].mean():.2f}"
                ]
            }
            pd.DataFrame(stats).to_excel(writer, sheet_name='통계', index=False)
        
        try:
            import os
            file_size = os.path.getsize(filename) / 1024  # KB
        except:
            file_size = 0
        
        print(f"📊 Excel 파일 생성: {filename} ({file_size:.0f}KB)")
        return filename

def main():
    """메인 실행 함수"""
    print("🚀 MACHO-GPT v3.4-mini 실제 데이터 기반 월별 트랜잭션 생성기")
    print("=" * 80)
    
    # 생성기 초기화
    generator = MachoTransactionGenerator()
    
    # 트랜잭션 생성
    df_transactions = generator.generate_monthly_transactions()
    
    # Excel 내보내기
    filename = generator.export_to_excel(df_transactions)
    
    # 결과 요약
    print(f"\n📈 **생성 완료 요약**")
    print(f"   - 총 트랜잭션: {len(df_transactions):,}건")
    print(f"   - 실제 케이스: {df_transactions['Case_No'].nunique():,}개")
    print(f"   - 총 처리량: {df_transactions['Qty'].sum():,}개") 
    print(f"   - 총 금액: ${df_transactions['Amount'].sum():,.2f}")
    print(f"   - 평균 월별: {len(df_transactions)/25:.0f}건/월")
    print(f"   - 파일: {filename}")
    
    return df_transactions, filename

if __name__ == "__main__":
    main() 